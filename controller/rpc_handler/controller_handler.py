import sdn_controller
from sdn_controller import SDNController, SlaveDevice

from pprint import pprint
import controller.ttypes
from controller.ttypes import Config, ConfigUpdate, ForwardEntry, Operation, Stream


def forward_type_translate_to_rpc(forward_type):
    if forward_type == sdn_controller.ForwardEntryType.ENCAP:
        return controller.ttypes.ForwardEntryType.ENCAP
    elif forward_type == sdn_controller.ForwardEntryType.DECAP:
        return controller.ttypes.ForwardEntryType.DECAP
    elif forward_type == sdn_controller.ForwardEntryType.FORWARD:
        return controller.ttypes.ForwardEntryType.FORWARD
    elif forward_type == sdn_controller.ForwardEntryType.LOCAL:
        return controller.ttypes.ForwardEntryType.LOCAL

class ControllerHandler:

    def __init__(self):
        self.sdn_controller = SDNController()

    def keep_alive(self, device_update):
        pprint(device_update)

        streams_add = []
        streams_del = []
        streams_update = []

        slave_device: SlaveDevice = self.sdn_controller.topo.search_slave_device(device_update.name)
        if None == slave_device:
            slave_device = SlaveDevice(device_update.name)
            self.sdn_controller.topology_add_slave_device(slave_device)

        for port_update in device_update.port_update_list:
            if port_update.op == Operation.ADD:
                slave_device.add_port(port_update.if_index)
            elif port_update.op == Operation.DEL:
                slave_device.remove_port(port_update.if_index)
            elif port_update.op == Operation.UPDATE:
                pass

        for link_update in device_update.link_update_list:
            if link_update.op == Operation.ADD:
                slave_device.add_interconnection_link(
                    link_update.if_index, 
                    link_update.peer_device_name, 
                    link_update.peer_if_index)

            elif link_update.op == Operation.DEL:
                slave_device.remove_interconnection_link(
                    link_update.if_index, 
                    link_update.peer_device_name, 
                    link_update.peer_if_index)
            elif link_update.op == Operation.UPDATE:
                pass
        
        for add_queue in slave_device.stream_table_add_queue:
            forward_entry = ForwardEntry(
                    add_queue.stream_id, 
                    add_queue.in_port,
                    add_queue.out_port,
                    forward_type_translate_to_rpc(add_queue.forward_type))
            streams_add.append(Stream(add_queue.stream_id, forward_entry))
        
        for del_queue in slave_device.stream_table_del_queue:
            streams_del.append(Stream(del_queue.stream_id))

        slave_device.stream_table_install_finish()

        return ConfigUpdate(streams_add, streams_del, streams_update)

    def link_full_request(self, device):
        pprint(device)

        streams_list = []

        slave_device: SlaveDevice = self.sdn_controller.topo.search_slave_device(device.name)
        if None == slave_device:
            slave_device = SlaveDevice(device.name)
            self.sdn_controller.topology_add_slave_device(slave_device)

        for port in device.port_list:
            slave_device.add_port(port.if_index)

        for link in device.link_list:
            slave_device.add_interconnection_link(
                link.local_if_index, 
                link.peer_device_name, 
                link.peer_if_index)

        for stream in slave_device.stream_table:
            forward_entry = ForwardEntry(
                    stream.stream_id, 
                    stream.src_port.if_index,
                    stream.dst_port.if_index,
                    forward_type_translate_to_rpc(stream.forward_type))
            streams_list.append(Stream(stream.stream_id, forward_entry))
        
        return Config(streams_list)
