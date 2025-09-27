from pprint import pprint
import sys


sys.path.append('thrift/gen-py')

from controller import ControllerService

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.protocol.TMultiplexedProtocol import TMultiplexedProtocol

from controller.ttypes import Device

if __name__ == "__main__":
    transport = TSocket.TSocket('localhost', 9090)

    transport = TTransport.TBufferedTransport(transport)

    protocol = TBinaryProtocol.TBinaryProtocol(transport)

    client = ControllerService.Client(TMultiplexedProtocol(protocol, "ControllerService"))

    transport.open()
    
    device = Device("device_1",[], [])

    ret = client.link_full_request(device)
    pprint(ret)

    transport.close()