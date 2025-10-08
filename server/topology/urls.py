from django.urls import path

from . import views

urlpatterns = [
    path("", views.topology_link_add, name="index"),
]