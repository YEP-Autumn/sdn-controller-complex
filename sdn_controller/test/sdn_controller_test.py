import time
from __test_data import TestData
from sdn_controller import PathCalculateUnit, Port, SDNController, SlaveDevice
from pprint import pprint

def sdn_controller_test():

    controller = SDNController()

    # slave device 1
    slave_device_1 = SlaveDevice(TestData.device_1['hostname'])
    for i in range(len(TestData.device_1['ports'])):
        slave_device_1.add_port(TestData.device_1['ports'][i]['port_no'])

    for i in range(len(TestData.device_1['interconnection_links'])):
        slave_device_1.add_interconnection_link(\
            TestData.device_1['interconnection_links'][i]['to']['port'], \
            TestData.device_1['interconnection_links'][i]['from']['hostname'], \
            TestData.device_1['interconnection_links'][i]['from']['port'])

    # slave device 2
    slave_device_2 = SlaveDevice(TestData.device_2['hostname'])
    for i in range(len(TestData.device_2['ports'])):
        slave_device_2.add_port(TestData.device_2['ports'][i]['port_no'])

    for i in range(len(TestData.device_2['interconnection_links'])):
        slave_device_2.add_interconnection_link(\
            TestData.device_2['interconnection_links'][i]['to']['port'], \
            TestData.device_2['interconnection_links'][i]['from']['hostname'], \
            TestData.device_2['interconnection_links'][i]['from']['port'])

    # slave device 3
    slave_device_3 = SlaveDevice(TestData.device_3['hostname'])
    for i in range(len(TestData.device_3['ports'])):
        slave_device_3.add_port(TestData.device_3['ports'][i]['port_no'])

    for i in range(len(TestData.device_3['interconnection_links'])):
        slave_device_3.add_interconnection_link(\
            TestData.device_3['interconnection_links'][i]['to']['port'], \
            TestData.device_3['interconnection_links'][i]['from']['hostname'], \
            TestData.device_3['interconnection_links'][i]['from']['port'])

    # slave device 4
    slave_device_4 = SlaveDevice(TestData.device_4['hostname'])
    for i in range(len(TestData.device_4['ports'])):
        slave_device_4.add_port(TestData.device_4['ports'][i]['port_no'])

    for i in range(len(TestData.device_4['interconnection_links'])):
        slave_device_4.add_interconnection_link(\
            TestData.device_4['interconnection_links'][i]['to']['port'], \
            TestData.device_4['interconnection_links'][i]['from']['hostname'], \
            TestData.device_4['interconnection_links'][i]['from']['port'])

    controller.topology_add_slave_device(slave_device_1)
    controller.topology_add_slave_device(slave_device_2)
    controller.topology_add_slave_device(slave_device_3)
    controller.topology_add_slave_device(slave_device_4)

    pprint(controller.topo.path_calculate_unit.path_vector_list)

    controller.add_bidirectional_stream(Port('device_1', 1), Port('device_4', 3))

    for stream in controller.stream_table:
        pprint(stream)
        pprint(stream.stream_table)


    # while True:
        # for device in controller.topo.slave_devices:
        #     pprint(device.stream_table_add_queue)

    # while True:
    #     time.sleep(10)
    #     pprint(controller.topo.path_calculate_unit.path_vector_list)
    #     for stream in controller.stream_table:
    #         pprint(stream)
    #         pprint(stream.stream_table)

if __name__ == "__main__":
    sdn_controller_test()
    pass