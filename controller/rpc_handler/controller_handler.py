import sys
sys.path.append("../thrift/gen-py")

from pprint import pprint

from controller.ttypes import Config

class ControllerHandler:

    def __init__(self):
        pass

    def keep_alive(self, device_update):
        pprint(device_update)
        return Config()

    def link_full_request(self, device):
        pprint(device)
        return Config()
