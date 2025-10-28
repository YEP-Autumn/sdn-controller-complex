from pprint import pprint
import sys
import time

from test.__test_data import TestData


sys.path.append('thrift/gen-py')

from controller import ControllerService

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.protocol.TMultiplexedProtocol import TMultiplexedProtocol

from controller.ttypes import Device, InterconnectionLink, Port

if __name__ == "__main__":
    transport = TSocket.TSocket('localhost', 9090)

    transport = TTransport.TBufferedTransport(transport)

    protocol = TBinaryProtocol.TBinaryProtocol(transport)

    client = ControllerService.Client(TMultiplexedProtocol(protocol, "ControllerService"))

    transport.open()

    device_list = []

    port_list = []
    link_list = []

    # for port in TestData.device_1['ports']:
    #     port_list.append(Port(port['port_no']))

    # for link in TestData.device_1['interconnection_links']:
    #     link_list.append(
    #         InterconnectionLink(
    #             local_if_index=link['to']['port'], 
    #             peer_device_name=link['from']['hostname'], 
    #             peer_if_index=link['from']['port']))

    # device_list.append(Device(TestData.device_1['hostname'], port_list, link_list))

    port_list = []
    link_list = []

    for port in TestData.device_2['ports']:
        port_list.append(Port(port['port_no']))

    for link in TestData.device_2['interconnection_links']:
        link_list.append(
            InterconnectionLink(
                local_if_index=link['to']['port'], 
                peer_device_name=link['from']['hostname'], 
                peer_if_index=link['from']['port']))


    device_list.append(Device(TestData.device_2['hostname'], port_list, link_list))

    port_list = []
    link_list = []

    for port in TestData.device_3['ports']:
        port_list.append(Port(port['port_no']))

    for link in TestData.device_3['interconnection_links']:
        link_list.append(
            InterconnectionLink(
                local_if_index=link['to']['port'], 
                peer_device_name=link['from']['hostname'], 
                peer_if_index=link['from']['port']))

    device_list.append(Device(TestData.device_3['hostname'], port_list, link_list))

    port_list = []
    link_list = []

    for port in TestData.device_4['ports']:
        port_list.append(Port(port['port_no']))

    for link in TestData.device_4['interconnection_links']:
        link_list.append(
            InterconnectionLink(
                local_if_index=link['to']['port'], 
                peer_device_name=link['from']['hostname'], 
                peer_if_index=link['from']['port']))

    device_list.append(Device(TestData.device_4['hostname'], port_list, link_list))

    while True:
        for device in device_list:
            ret = client.link_full_request(device)
            pprint("----- Device{} Link Full Request Result -----".format(device.name))
            pprint(ret)
        time.sleep(5)

    pprint(ret)

    transport.close()