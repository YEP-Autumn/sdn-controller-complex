from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
import os
import sys
import json
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.protocol import TCompactProtocol
import traceback


# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the stream_backend index.")


@require_http_methods(["POST"])
def stream_backend_packet_send(request):
    try:
        # Support multipart/form-data with a `file` field and optional extra fields.
        # Fall back to raw request.body for existing clients that POST the binary directly.
        binary_data = None
        received_filename = None
        parsed_fields = {}

        content_type = request.META.get("CONTENT_TYPE", request.content_type or "")
        if content_type and content_type.startswith("multipart/"):
            # Django populates request.FILES and request.POST for multipart requests
            if "file" not in request.FILES:
                return JsonResponse({"error": "No file field in multipart request"}, status=400)
            uploaded = request.FILES["file"]
            try:
                binary_data = uploaded.read()
            except Exception:
                # UploadedFile should support read(); if not, try .file
                try:
                    binary_data = uploaded.file.read()
                except Exception as e:
                    return JsonResponse({"error": f"Unable to read uploaded file: {e}"}, status=400)
            received_filename = getattr(uploaded, "name", None)

            # Parse additional form fields (attempt JSON decode when possible)
            for k in request.POST:
                v = request.POST.get(k)
                if v is None:
                    parsed_fields[k] = None
                    continue
                try:
                    parsed_fields[k] = json.loads(v)
                except Exception:
                    parsed_fields[k] = v
        else:
            # Fallback: treat entire body as raw binary
            binary_data = request.body

        if binary_data is None:
            return JsonResponse({"error": "No binary data in request"}, status=400)

        print(f"Received binary packet of {len(binary_data)} bytes")
        print('Hex dump:', binary_data.hex())

        # Ensure generated Thrift Python package is importable (thrift/gen-py)
        # Compute project root (three levels up from this file: server/stream_backend/views.py -> project root)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        gen_py_path = os.path.join(project_root, "thrift", "gen-py")
        if gen_py_path not in sys.path:
            sys.path.insert(0, gen_py_path)

        # Import generated thrift types for Packet
        try:
            from packet import ttypes as packet_ttypes
        except Exception as e:
            return JsonResponse({"error": f"Failed importing generated thrift packet types: {e}"}, status=500)

        # Try several deserialization strategies to be robust against framing/protocol differences
        errors = []

        def _try_with_protocol(data, prot_cls):
            try:
                trans = TTransport.TMemoryBuffer(data)
                iprot = prot_cls(trans)
                pkt = packet_ttypes.Packet()
                pkt.read(iprot)
                return pkt
            except Exception as e:
                return e

        pkt = None

        # 1) TBinaryProtocol as-is
        res = _try_with_protocol(binary_data, TBinaryProtocol.TBinaryProtocol)
        if isinstance(res, packet_ttypes.Packet):
            pkt = res
        else:
            errors.append(f"binary-as-is: {repr(res)}")

        # 2) If failed, try removing a 4-byte big-endian frame length prefix (common with framed transports)
        if pkt is None and len(binary_data) > 4:
            try:
                frame_len = int.from_bytes(binary_data[:4], byteorder="big")
                if frame_len == len(binary_data) - 4 or frame_len <= len(binary_data) - 4:
                    stripped = binary_data[4:4 + frame_len] if frame_len <= len(binary_data) - 4 else binary_data[4:]
                    res = _try_with_protocol(stripped, TBinaryProtocol.TBinaryProtocol)
                    if isinstance(res, packet_ttypes.Packet):
                        pkt = res
                    else:
                        errors.append(f"binary-strip-be-4byte(len={frame_len}): {repr(res)}")
            except Exception as e:
                errors.append(f"binary-strip-be-4byte-exc: {repr(e)}")

        # 3) Try little-endian 4-byte length prefix
        if pkt is None and len(binary_data) > 4:
            try:
                frame_len = int.from_bytes(binary_data[:4], byteorder="little")
                if frame_len == len(binary_data) - 4 or frame_len <= len(binary_data) - 4:
                    stripped = binary_data[4:4 + frame_len] if frame_len <= len(binary_data) - 4 else binary_data[4:]
                    res = _try_with_protocol(stripped, TBinaryProtocol.TBinaryProtocol)
                    if isinstance(res, packet_ttypes.Packet):
                        pkt = res
                    else:
                        errors.append(f"binary-strip-le-4byte(len={frame_len}): {repr(res)}")
            except Exception as e:
                errors.append(f"binary-strip-le-4byte-exc: {repr(e)}")

        # 4) Try CompactProtocol as-is
        if pkt is None:
            res = _try_with_protocol(binary_data, TCompactProtocol.TCompactProtocol)
            if isinstance(res, packet_ttypes.Packet):
                pkt = res
            else:
                errors.append(f"compact-as-is: {repr(res)}")

        # 5) Try CompactProtocol with 4-byte BE/LE stripping
        if pkt is None and len(binary_data) > 4:
            try:
                for byteorder in ("big", "little"):
                    try:
                        frame_len = int.from_bytes(binary_data[:4], byteorder=byteorder)
                    except Exception:
                        errors.append(f"compact-strip-{byteorder}-4byte-exc")
                        continue
                    if frame_len == len(binary_data) - 4 or frame_len <= len(binary_data) - 4:
                        stripped = binary_data[4:4 + frame_len] if frame_len <= len(binary_data) - 4 else binary_data[4:]
                        res = _try_with_protocol(stripped, TCompactProtocol.TCompactProtocol)
                        if isinstance(res, packet_ttypes.Packet):
                            pkt = res
                            break
                        else:
                            errors.append(f"compact-strip-{byteorder}(len={frame_len}): {repr(res)}")
            except Exception as e:
                errors.append(f"compact-strip-exc: {repr(e)}")

        if pkt is None:
            tb = traceback.format_exc()
            errors.append(f"final-exc: {tb}")
            response_obj = {
                "error": "Thrift deserialization failed",
                "attempts": errors,
                "hex": binary_data.hex(),
            }
            try:
                print("Thrift deserialization failed response:\n", json.dumps(response_obj, ensure_ascii=False, indent=2))
            except Exception:
                print("Thrift deserialization failed response (raw):", response_obj)
            return JsonResponse(response_obj, status=400)

        # Build a JSON-serializable summary of the Packet
        def field_to_dict(fm: packet_ttypes.FieldMeta):
            field = fm.field
            d = {"type": fm.type}
            if field is None:
                return d
            if getattr(field, "ether", None) is not None:
                eth = field.ether
                d["ether"] = {"dst": eth.dst, "src": eth.src, "type": eth.type}
            if getattr(field, "vlan", None) is not None:
                vlan = field.vlan
                d["vlan"] = {"vlan": vlan.vlan, "type": vlan.type}
            if getattr(field, "ipv4", None) is not None:
                ip4 = field.ipv4
                d["ipv4"] = {"src_ip": ip4.src_ip, "dst_ip": ip4.dst_ip}
            return d

        field_list = []
        if pkt.field_list:
            for fm in pkt.field_list:
                try:
                    field_list.append(field_to_dict(fm))
                except Exception:
                    field_list.append({"error": "unable to convert field"})

        response_obj = {
            "message": "Stream backend packet send endpoint.",
            "bytes_received": len(binary_data),
            "packet": {"field_list": field_list},
            "received_filename": received_filename,
            "fields": parsed_fields,
        }
        try:
            print("Thrift deserialization success response:\n", json.dumps(response_obj, ensure_ascii=False, indent=2))
        except Exception:
            print("Thrift deserialization success response (raw):", response_obj)
        return JsonResponse(response_obj, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
