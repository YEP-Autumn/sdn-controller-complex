from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods


# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the stream_backend index.")


@require_http_methods(["POST"])
def stream_backend_packet_send(request):
    try:
        # 获取原始二进制数据
        binary_data = request.body
        print(f"Received binary packet of {len(binary_data)} bytes")
        print('Hex dump:', binary_data.hex())

        

        # 处理二进制数据...
        # (在这里添加你的业务逻辑)

        return JsonResponse(
            {
                "message": "Stream backend packet send endpoint.",
                "bytes_received": len(binary_data),
            },
            status=200,
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
