
import sys
import threading
from time import sleep
sys.path.append("thrift/gen-py")
from handler.controller_handler import ControllerHandler
from pprint import pprint

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
from thrift.TMultiplexedProcessor import TMultiplexedProcessor

from controller import ControllerService

class RpcServer:

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def controller_service_server_start(self):
        self.transport = TSocket.TServerSocket(host=self.host, port=self.port)

        self.tfactory = TTransport.TBufferedTransportFactory()
        self.pfactory = TBinaryProtocol.TBinaryProtocolFactory()
        self.processor = TMultiplexedProcessor().registerProcessor("ControllerService", ControllerService.Processor(ControllerHandler()))

        self.processor

        self.server = TServer.TThreadedServer(self.processor, self.transport, self.tfactory, self.pfactory)

        self.server_thread = threading.Thread(target=self.server.serve, name='rpc_server')
        self.server_thread.daemon = True
        self.server_thread.start()


if __name__ == "__main__":

    RpcServer("127.0.0.1", 9090).controller_service_server_start()
    pprint("Starting the server...")
    
    sleep(10000)


    
    