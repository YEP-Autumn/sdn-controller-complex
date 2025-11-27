from django.http import HttpResponse
from rest_framework.decorators import api_view

# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the stream_backend index.")

@api_view(["POST"])
def stream_backend_packet_send(request):
    print("Received packet send request with data:", request.data)
    return HttpResponse("Stream backend packet send endpoint.")