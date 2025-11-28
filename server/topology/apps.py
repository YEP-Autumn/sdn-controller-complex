from django.apps import AppConfig
from rpc_server import RpcServer
from lib.controller.controller import SDNController
import os

global SDN_CONTROLLER
global THRIFT_RPC_SERVER


class TopologyConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "topology"

    def ready(self):
        print("Topology app is ready {}.".format(os.environ.get("RUN_MAIN", None)))
        if os.environ.get("RUN_MAIN", None) != "true":
            print("Initializing SDN Controller and RPC Server...")
            SDN_CONTROLLER = SDNController()
            THRIFT_RPC_SERVER = RpcServer(
                "127.0.0.1", 9090
            ).controller_service_server_start(SDN_CONTROLLER)
