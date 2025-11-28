import threading
from time import sleep
from controller_handler import ControllerHandler

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

    def controller_service_server_start(self, sdn_controller):
        print("Starting RPC server on {}:{}".format(self.host, self.port))

        transport = TSocket.TServerSocket(host=self.host, port=self.port)

        tfactory = TTransport.TBufferedTransportFactory()
        pfactory = TBinaryProtocol.TBinaryProtocolFactory()
        processor = TMultiplexedProcessor()

        processor.registerProcessor("ControllerService", ControllerService.Processor(ControllerHandler(sdn_controller)))

        server = TServer.TThreadedServer(processor, transport, tfactory, pfactory)

        server_thread = threading.Thread(target=server.serve, name='rpc_server')
        server_thread.daemon = True
        server_thread.start()

