from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
import os
import sys
import json
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.protocol import TCompactProtocol
import traceback
import logging


# Module logger
logger = logging.getLogger(__name__)
try:
    logger.addHandler(logging.NullHandler())
except Exception:
    pass


# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the stream_backend index.")


def _parse_request_data(request):
    """
    Parse request data from either multipart/form-data or raw binary.
    
    Returns:
        tuple: (binary_data, received_filename, parsed_fields) or JsonResponse on error
    """
    received_filename = None
    parsed_fields = {}
    
    # Use Django's request.FILES for multipart data handling
    if request.FILES:
        if "file" not in request.FILES:
            logger.warning("Multipart request missing 'file' field")
            return None, None, None, JsonResponse({"error": "No file field in multipart request"}, status=400)
        
        uploaded = request.FILES["file"]
        try:
            binary_data = uploaded.read()
        except Exception as e:
            logger.exception("Unable to read uploaded file")
            return None, None, None, JsonResponse({"error": f"Unable to read uploaded file: {e}"}, status=400)
        
        received_filename = uploaded.name
        
        # Use request.POST to parse form fields directly
        for key, value in request.POST.items():
            try:
                parsed_fields[key] = json.loads(value)
            except json.JSONDecodeError:
                parsed_fields[key] = value
    else:
        # Django automatically parses request.body for non-multipart requests
        binary_data = request.body

    if not binary_data:
        logger.warning("Request contained no binary data")
        return None, None, None, JsonResponse({"error": "No binary data in request"}, status=400)

    return binary_data, received_filename, parsed_fields, None

def _try_deserialize_with_protocol(data, prot_cls, packet_ttypes):
    """
    Attempt to deserialize Thrift packet with given protocol.
    
    Returns:
        packet_ttypes.Packet or Exception
    """
    logger.debug("Attempting deserialize: protocol=%s, data_len=%d", getattr(prot_cls, '__name__', str(prot_cls)), len(data))
    try:
        trans = TTransport.TMemoryBuffer(data)
        iprot = prot_cls(trans)
        pkt = packet_ttypes.Packet()
        pkt.read(iprot)
        logger.debug("Deserialization attempt successful for protocol=%s", getattr(prot_cls, '__name__', str(prot_cls)))
        return pkt
    except Exception as e:
        logger.debug("Deserialization attempt failed for protocol=%s: %s", getattr(prot_cls, '__name__', str(prot_cls)), repr(e), exc_info=True)
        return e


def _try_strip_frame_and_deserialize(data, frame_prefix_len, byteorder, prot_cls, packet_ttypes, errors, strategy_name):
    """
    Try stripping frame length prefix and deserializing.
    
    Returns:
        packet_ttypes.Packet or None
    """
    if len(data) <= frame_prefix_len:
        logger.debug("Data too short to contain frame prefix: data_len=%d, prefix_len=%d", len(data), frame_prefix_len)
        return None
    
    try:
        frame_len = int.from_bytes(data[:frame_prefix_len], byteorder=byteorder)
        logger.debug("Parsed frame length=%d from prefix_len=%d (byteorder=%s) for strategy=%s", frame_len, frame_prefix_len, byteorder, strategy_name)
        if frame_len == len(data) - frame_prefix_len or frame_len <= len(data) - frame_prefix_len:
            stripped = data[frame_prefix_len:frame_prefix_len + frame_len] if frame_len <= len(data) - frame_prefix_len else data[frame_prefix_len:]
            res = _try_deserialize_with_protocol(stripped, prot_cls, packet_ttypes)
            if isinstance(res, packet_ttypes.Packet):
                try:
                    logger.info(
                        "Deserialization succeeded using strategy '%s' (frame_prefix_len=%d, byteorder=%s, protocol=%s)",
                        strategy_name,
                        frame_prefix_len,
                        byteorder,
                        getattr(prot_cls, "__name__", str(prot_cls)),
                    )
                except Exception:
                    # Best-effort logging; don't break deserialization on logging error
                    pass
                return res
            else:
                err = f"{strategy_name}(len={frame_len}): {repr(res)}"
                errors.append(err)
                logger.debug("%s", err)
    except Exception as e:
        err = f"{strategy_name}-exc: {repr(e)}"
        errors.append(err)
        logger.debug("%s", err, exc_info=True)
    
    return None


def _deserialize_packet(binary_data, packet_ttypes):
    """
    Try multiple deserialization strategies to handle different protocols and framing.

    Returns:
        tuple: (packet or None, errors_list, used_strategy or None)
    """
    errors = []
    pkt = None

    # Strategy 1: TFramedTransport (4-byte big-endian frame length) + TCompactProtocol
    # Most commonly used by modern Thrift clients (better compression)
    strategy = "compact-framed-be-4byte"
    pkt = _try_strip_frame_and_deserialize(
        binary_data, 4, "big", TCompactProtocol.TCompactProtocol, packet_ttypes, errors, strategy
    )
    if pkt is not None:
        return pkt, errors, strategy

    # Strategy 2: TFramedTransport (4-byte little-endian frame length) + TCompactProtocol
    strategy = "compact-framed-le-4byte"
    pkt = _try_strip_frame_and_deserialize(
        binary_data, 4, "little", TCompactProtocol.TCompactProtocol, packet_ttypes, errors, strategy
    )
    if pkt is not None:
        return pkt, errors, strategy

    # Strategy 3: TFramedTransport (4-byte big-endian frame length) + TBinaryProtocol
    strategy = "binary-framed-be-4byte"
    pkt = _try_strip_frame_and_deserialize(
        binary_data, 4, "big", TBinaryProtocol.TBinaryProtocol, packet_ttypes, errors, strategy
    )
    if pkt is not None:
        return pkt, errors, strategy

    # Strategy 4: TFramedTransport (4-byte little-endian frame length) + TBinaryProtocol
    strategy = "binary-framed-le-4byte"
    pkt = _try_strip_frame_and_deserialize(
        binary_data, 4, "little", TBinaryProtocol.TBinaryProtocol, packet_ttypes, errors, strategy
    )
    if pkt is not None:
        return pkt, errors, strategy

    # Strategy 5: TCompactProtocol without framing
    logger.debug("Trying strategy: compact-as-is")
    res = _try_deserialize_with_protocol(binary_data, TCompactProtocol.TCompactProtocol, packet_ttypes)
    if isinstance(res, packet_ttypes.Packet):
        logger.info("Deserialization succeeded using strategy 'compact-as-is' (protocol=%s)", getattr(TCompactProtocol.TCompactProtocol, '__name__', str(TCompactProtocol.TCompactProtocol)))
        return res, errors, "compact-as-is"
    else:
        errors.append(f"compact-as-is: {repr(res)}")
        logger.debug("compact-as-is failed: %s", repr(res))

    # Strategy 6: TBinaryProtocol without framing
    logger.debug("Trying strategy: binary-as-is")
    res = _try_deserialize_with_protocol(binary_data, TBinaryProtocol.TBinaryProtocol, packet_ttypes)
    if isinstance(res, packet_ttypes.Packet):
        logger.info("Deserialization succeeded using strategy 'binary-as-is' (protocol=%s)", getattr(TBinaryProtocol.TBinaryProtocol, '__name__', str(TBinaryProtocol.TBinaryProtocol)))
        return res, errors, "binary-as-is"
    else:
        errors.append(f"binary-as-is: {repr(res)}")
        logger.debug("binary-as-is failed: %s", repr(res))

    return None, errors, None


def _field_meta_to_dict(fm):
    """Convert FieldMeta object to JSON-serializable dictionary."""
    field = fm.field
    d = {"type": fm.type}
    
    if field is None:
        return d
    
    if getattr(field, "ether", None) is not None:
        eth = field.ether
        # Display type as hex
        ether_type_hex = hex(eth.type if eth.type >= 0 else (eth.type + 65536))
        d["ether"] = {"dst": eth.dst, "src": eth.src, "type": ether_type_hex}
    
    if getattr(field, "vlan", None) is not None:
        vlan = field.vlan
        # Display type as hex
        vlan_type_hex = hex(vlan.type if vlan.type >= 0 else (vlan.type + 65536))
        d["vlan"] = {"vlan": vlan.vlan, "type": vlan_type_hex}
    
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
        logger.info("%s\n%s", message, json.dumps(response_obj, ensure_ascii=False, indent=2))
    except Exception:
        logger.info("%s (raw): %s", message, response_obj)


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

        try:
            logger.info("Received binary packet of %d bytes", len(binary_data))
            logger.debug("Hex dump: %s", binary_data.hex())
        except Exception:
            # Best-effort logging; don't interfere with request handling
            pass

        # Import generated thrift types
        try:
            from packet import ttypes as packet_ttypes
        except Exception as e:
            return JsonResponse({"error": f"Failed importing generated thrift packet types: {e}"}, status=500)

        # Attempt deserialization
        pkt, errors, used_strategy = _deserialize_packet(binary_data, packet_ttypes)

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
            "used_strategy": used_strategy,
            "received_filename": received_filename,
            "fields": parsed_fields,
        }
        _log_json_response("Thrift deserialization success response:", response_obj)
        return JsonResponse(response_obj, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
