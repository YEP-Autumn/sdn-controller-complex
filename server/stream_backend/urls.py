from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("packet/send", views.stream_backend_packet_send, name="stream_backend_packet_send"),
]
