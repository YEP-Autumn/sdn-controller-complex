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


def _parse_request_data(request):
    """
    Parse request data from either multipart/form-data or raw binary.
    
    Returns:
        tuple: (binary_data, received_filename, parsed_fields) or JsonResponse on error
    """
    binary_data = None
    received_filename = None
    parsed_fields = {}

    content_type = request.META.get("CONTENT_TYPE", request.content_type or "")
    
    if content_type and content_type.startswith("multipart/"):
        if "file" not in request.FILES:
            return None, None, None, JsonResponse({"error": "No file field in multipart request"}, status=400)
        
        uploaded = request.FILES["file"]
        try:
            binary_data = uploaded.read()
        except Exception:
            try:
                binary_data = uploaded.file.read()
            except Exception as e:
                return None, None, None, JsonResponse({"error": f"Unable to read uploaded file: {e}"}, status=400)
        
        received_filename = getattr(uploaded, "name", None)
        
        # Parse additional form fields
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
        binary_data = request.body

    if binary_data is None:
        return None, None, None, JsonResponse({"error": "No binary data in request"}, status=400)

    return binary_data, received_filename, parsed_fields, None


def _setup_thrift_path():
    """Setup sys.path to include generated Thrift Python package."""
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    gen_py_path = os.path.join(project_root, "thrift", "gen-py")
    if gen_py_path not in sys.path:
        sys.path.insert(0, gen_py_path)


def _try_deserialize_with_protocol(data, prot_cls, packet_ttypes):
    """
    Attempt to deserialize Thrift packet with given protocol.
    
    Returns:
        packet_ttypes.Packet or Exception
    """
    try:
        trans = TTransport.TMemoryBuffer(data)
        iprot = prot_cls(trans)
        pkt = packet_ttypes.Packet()
        pkt.read(iprot)
        return pkt
    except Exception as e:
        return e


def _try_strip_frame_and_deserialize(data, frame_prefix_len, byteorder, prot_cls, packet_ttypes, errors, strategy_name):
    """
    Try stripping frame length prefix and deserializing.
    
    Returns:
        packet_ttypes.Packet or None
    """
    if len(data) <= frame_prefix_len:
        return None
    
    try:
        frame_len = int.from_bytes(data[:frame_prefix_len], byteorder=byteorder)
        if frame_len == len(data) - frame_prefix_len or frame_len <= len(data) - frame_prefix_len:
            stripped = data[frame_prefix_len:frame_prefix_len + frame_len] if frame_len <= len(data) - frame_prefix_len else data[frame_prefix_len:]
            res = _try_deserialize_with_protocol(stripped, prot_cls, packet_ttypes)
            if isinstance(res, packet_ttypes.Packet):
                return res
            else:
                errors.append(f"{strategy_name}(len={frame_len}): {repr(res)}")
    except Exception as e:
        errors.append(f"{strategy_name}-exc: {repr(e)}")
    
    return None


def _deserialize_packet(binary_data, packet_ttypes):
    """
    Try multiple deserialization strategies to handle different protocols and framing.
    
    Returns:
        tuple: (packet, errors_list)
    """
    errors = []
    pkt = None

    # Strategy 1: TBinaryProtocol as-is
    res = _try_deserialize_with_protocol(binary_data, TBinaryProtocol.TBinaryProtocol, packet_ttypes)
    if isinstance(res, packet_ttypes.Packet):
        return res, errors
    else:
        errors.append(f"binary-as-is: {repr(res)}")

    # Strategy 2: TBinaryProtocol with big-endian 4-byte frame length
    pkt = _try_strip_frame_and_deserialize(
        binary_data, 4, "big", TBinaryProtocol.TBinaryProtocol, packet_ttypes, errors, "binary-strip-be-4byte"
    )
    if pkt is not None:
        return pkt, errors

    # Strategy 3: TBinaryProtocol with little-endian 4-byte frame length
    pkt = _try_strip_frame_and_deserialize(
        binary_data, 4, "little", TBinaryProtocol.TBinaryProtocol, packet_ttypes, errors, "binary-strip-le-4byte"
    )
    if pkt is not None:
        return pkt, errors

    # Strategy 4: TCompactProtocol as-is
    res = _try_deserialize_with_protocol(binary_data, TCompactProtocol.TCompactProtocol, packet_ttypes)
    if isinstance(res, packet_ttypes.Packet):
        return res, errors
    else:
        errors.append(f"compact-as-is: {repr(res)}")

    # Strategy 5: TCompactProtocol with frame length stripping
    for byteorder in ("big", "little"):
        pkt = _try_strip_frame_and_deserialize(
            binary_data, 4, byteorder, TCompactProtocol.TCompactProtocol, packet_ttypes, errors, f"compact-strip-{byteorder}-4byte"
        )
        if pkt is not None:
            return pkt, errors

    return None, errors


def _field_meta_to_dict(fm):
    """Convert FieldMeta object to JSON-serializable dictionary."""
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


def _build_field_list(packet):
    """Build JSON-serializable field list from Packet object."""
    field_list = []
    if packet.field_list:
        for fm in packet.field_list:
            try:
                field_list.append(_field_meta_to_dict(fm))
            except Exception:
                field_list.append({"error": "unable to convert field"})
    return field_list


def _log_json_response(message, response_obj):
    """Safely log response object as JSON."""
    try:
        print(f"{message}\n{json.dumps(response_obj, ensure_ascii=False, indent=2)}")
    except Exception:
        print(f"{message} (raw): {response_obj}")


@require_http_methods(["POST"])
def stream_backend_packet_send(request):
    """
    Handle incoming binary packets over HTTP.
    
    Supports:
    - Multipart form data with 'file' field
    - Raw binary body
    - Multiple Thrift serialization protocols and framing formats
    """
    try:
        # Parse request data
        binary_data, received_filename, parsed_fields, error_response = _parse_request_data(request)
        if error_response is not None:
            return error_response

        print(f"Received binary packet of {len(binary_data)} bytes")
        print('Hex dump:', binary_data.hex())

        # Setup Thrift import path
        _setup_thrift_path()

        # Import generated thrift types
        try:
            from packet import ttypes as packet_ttypes
        except Exception as e:
            return JsonResponse({"error": f"Failed importing generated thrift packet types: {e}"}, status=500)

        # Attempt deserialization
        pkt, errors = _deserialize_packet(binary_data, packet_ttypes)

        if pkt is None:
            tb = traceback.format_exc()
            errors.append(f"final-exc: {tb}")
            response_obj = {
                "error": "Thrift deserialization failed",
                "attempts": errors,
                "hex": binary_data.hex(),
            }
            _log_json_response("Thrift deserialization failed response:", response_obj)
            return JsonResponse(response_obj, status=400)

        # Build success response
        field_list = _build_field_list(pkt)
        response_obj = {
            "message": "Stream backend packet send endpoint.",
            "bytes_received": len(binary_data),
            "packet": {"field_list": field_list},
            "received_filename": received_filename,
            "fields": parsed_fields,
        }
        _log_json_response("Thrift deserialization success response:", response_obj)
        return JsonResponse(response_obj, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
