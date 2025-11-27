from django.http import HttpResponse
from .models import Topology
from django.views.decorators.http import require_http_methods

# Create your views here.


def index(request):
    return HttpResponse("Hello, world. You're at the topology index.")


@require_http_methods(["POST"])
def topologyCreate(request):

    # print("Creating topology:", toponame)

    # all = Topology.objects.filter(name__icontains="").first()
    # print("all:", all)

    # return HttpResponse("Received POST data")

    # topology = Topology.objects.create(name=toponame)

    # link1 = TopologyLink.objects.create(
    #     src_port_index=1,
    #     src_device=1,
    #     dst_port_index=2,
    #     dst_device=2,
    #     is_two_way=True,
    #     topology=topology,
    # )

    # link2 = TopologyLink.objects.create(
    #     src_port_index=2,
    #     src_device=1,
    #     dst_port_index=2,
    #     dst_device=2,
    #     is_two_way=True,
    #     topology=topology,
    # )

    # link3 = TopologyLink.objects.create(
    #     src_port_index=3,
    #     src_device=1,
    #     dst_port_index=2,
    #     dst_device=2,
    #     is_two_way=True,
    #     topology=topology,
    # )

    all = Topology.objects.all()
    for t in all:
        print(t)
        for link in t.links.all():
            print("  ", link)

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
