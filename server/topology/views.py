from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse

# Create your views here.


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


@api_view(["POST"])
def topologyCreate(request):
    toponame = request.data.get("name")

    return HttpResponse("Received POST data")


def topologyRemove(request):
    if request.method == "POST":
        # request.body 是一个字节字符串 (bytes)
        raw_body = request.body

        print(raw_body)

        return HttpResponse("Received POST data")

    return HttpResponse("Please send a POST request")


def topologyLinkAdd(request):
    if request.method == "POST":
        # request.body 是一个字节字符串 (bytes)
        raw_body = request.body

        print(raw_body)

        return HttpResponse("Received POST data")

    return HttpResponse("Please send a POST request")


def topologyLinkDel(request):
    if request.method == "POST":
        # request.body 是一个字节字符串 (bytes)
        raw_body = request.body

        print(raw_body)

        return HttpResponse("Received POST data")

    return HttpResponse("Please send a POST request")
