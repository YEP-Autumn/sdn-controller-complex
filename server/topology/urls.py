from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("add", views.topologyCreate, name="topologyCreate"),
    path("del", views.topologyRemove, name="topologyRemove"),
    path("link/add", views.topologyLinkAdd, name="topologyLinkAdd"),
    path("link/del", views.topologyLinkDel, name="topologyLinkDel"),
]
