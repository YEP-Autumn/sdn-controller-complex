import pprint

from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

def index(request):
    pprint.pprint(request.__dict__)
    return HttpResponse("Hello, world. You're at the polls index.")