from enum import Enum
import threading
import time
import uuid
from dijkstar import Graph, find_path
from opf import OPF


class ForwardEntryType(Enum):
    ENCAP = 0
    DECAP = 1
    FORWARD = 2
    LOCAL = 3


class Port:
    def __init__(self, device_hostname, port_no):
        self.device_hostname = device_hostname
        self.port_no = port_no
        self.last_update_time = time.time()

    def __str__(self):
        return "Port(device_hostname={}, port_no={})".format(self.device_hostname, self.port_no)

    def __repr__(self):
        return self.__str__()

class InterconnectionPort():

    def __init__(self, device_hostname, port_no, peer_device_hostname, peer_port):
        self.device_hostname = device_hostname
        self.port_no = port_no
        self.peer_device_hostname = peer_device_hostname
        self.peer_port = peer_port
        self.last_update_time = time.time()

    def __str__(self):
        return "InterconnectionPort(device_hostname={}, port_no={}, peer_device_hostname={}, peer_port={})".\
            format(self.device_hostname, self.port_no, self.peer_device_hostname, self.peer_port)

    def __repr__(self):
        return self.__str__()

class PathVector:
    def __init__(self, start, end, weight):
        self.start = start
        self.end = end
        self.weight = weight
        self.mark = 0

    def __str__(self):
        return "PathVector(start={}, end={}, weight={})".format(self.start, self.end, self.weight)

    def __repr__(self):
        return self.__str__()

class SlaveDevice:

    def __init__(self, hostname):
        self.uuid = uuid.uuid4()
        self.hostname = hostname
        self.port_list = []
        self.interconnection_link_list = []
        self.stream_table = []
        self.stream_table_add_queue = []
        self.stream_table_del_queue = []
        threading.Thread(target=self.__port_aging_timer, name='port_aging_timer').start()

    def add_port(self, port_no):
        port = self.__search_port(port_no)
        if port:
            port.last_update_time = time.time()
        else:
            self.port_list.append(Port(self.hostname, port_no))
 
    def remove_port(self, port_no):
        port = self.__search_port(port_no)
        if port:
            self.port_list.remove(port)

    def add_interconnection_link(self, port_no, peer_device_hostname, peer_port):
        link  = self.__search_interconnection_link(port_no, peer_device_hostname, peer_port)
        if link:
            link.last_update_time = time.time()
        else:
            self.interconnection_link_list.append(
                InterconnectionPort(
                    self.hostname, port_no, 
                    peer_device_hostname, 
                    peer_port))

    def remove_interconnection_link(self, port_no, peer_device_hostname, peer_port):
        link  = self.__search_interconnection_link(port_no, peer_device_hostname, peer_port)
        if link:
            self.interconnection_link_list.remove(link)

    def __search_port(self, port_no):
        for port in self.port_list:
            if port.port_no == port_no:
                return port
        return None
    
    def __search_interconnection_link(self, port_no, peer_device_hostname, peer_port):
        for link in self.interconnection_link_list:
            if link.port_no == port_no and link.peer_device_hostname == peer_device_hostname and link.peer_port == peer_port:
                return link
        return None
    
    def lookup_peer_device_interconnection_port(self, peer_device_hostname):
        for link in self.interconnection_link_list:
            if link.peer_device_hostname == peer_device_hostname:
                return link.peer_port
        return None

    def check_if_same_stream_table(self,stream_table_1, stream_table_2):
        if (stream_table_1.stream_id != stream_table_2.stream_id or \
            stream_table_1.forward_type != stream_table_2.forward_type or \
            stream_table_1.in_port != stream_table_2.in_port or \
            stream_table_1.out_port != stream_table_2.out_port):
            return False

        return True

    def add_stream_table_add_queue(self, stream_table_add):

        # 如果stream table中存在该stream_table, 什么也不做
        for _ in self.stream_table:
            if self.check_if_same_stream_table(_, stream_table_add):
                return

        # 如果add queue中存在该stream_table, 什么也不做
        for _ in self.stream_table_add_queue:
            if self.check_if_same_stream_table(_, stream_table_add):
                return

        # 如果del queue中存在该stream_table, 什么也不做
        for _ in self.stream_table_del_queue:
            if self.check_if_same_stream_table(_, stream_table_add):
                return

        self.stream_table_add_queue.append(stream_table_add)

    
    def add_stream_table_del_queue(self, stream_table_del):
        # 如果add queue中存在该stream_table, 说明该条目还未下发到设备, 将其从add queue中删除后返回
        for _ in self.stream_table_add_queue:
            if self.check_if_same_stream_table(_, stream_table_del):
                self.stream_table_add_queue.remove(_)
                return

        # 如果del queue中存在该stream_table, 什么也不做
        for _ in self.stream_table_del_queue:
            if self.check_if_same_stream_table(_, stream_table_del):
                return

        # 如果stream table存在该stream_table, 则添加到删除队列
        for stream_table in self.stream_table:
            if self.check_if_same_stream_table(_, stream_table_del):
                self.stream_table_del_queue.append(stream_table)
                return

    def stream_table_install_finish(self):
        self.stream_table.extend(self.stream_table_add_queue)
        for stream_table in self.stream_table_del_queue:
            self.stream_table.remove(stream_table)

        self.stream_table_add_queue = []
        self.stream_table_del_queue = []

    def __port_aging_timer(self):
        for port in self.port_list:
            if time.time() - port.last_update_time > 30:
                self.port_list.remove(port)
        
        for link in self.interconnection_link_list:
            if time.time() - link.last_update_time > 30:
                self.interconnection_link_list.remove(link)

    def __str__(self):
        return "SlaveDevice(hostname={}, uuid={})".format(self.hostname, self.uuid)

    def __repr__(self):
        return self.__str__()

class PathCalculateUnit:

    def __init__(self):
        self.path_vector_list = []
        self.path_vector_map = {}

    def calculate_path(self, start, end):
        graph = Graph()
        for path in self.path_vector_list:
            graph.add_edge(path.start, path.end, path.weight)

        try:
            path_info = find_path(graph, start, end)
            return path_info.nodes
        except:
            return []

    def add_path(self, start, end, weight):
        path_vector = self.path_search(start, end)

        if not path_vector:
            path_vector = PathVector(start, end, weight)
            self.path_vector_list.append(path_vector)
            self.path_vector_map[(start, end)] = path_vector
        else:
            path_vector.weight = weight
        
        return path_vector

    def remove_path(self, start, end):
        path = self.path_search(start, end)

        if path:
            self.path_vector_list.remove(path)
            self.path_vector_map.pop((start, end))

    def path_search(self, start, end):
        return self.path_vector_map.get((start, end))

    def clear_outdated_path(self):
        for path_vector in self.path_vector_list[:]:
            if path_vector.mark == 0:
                self.remove_path(path_vector.start, path_vector.end)
            else:
                path_vector.mark = 0

class StreamTable:

    def __init__(self, device, stream_id):
        self.device = device
        self.stream_id = stream_id

    def add_encap_stream_table(self, in_port, next_device):
        self.forward_type = ForwardEntryType.ENCAP
        self.in_port = in_port
        self.out_port = next_device.lookup_peer_device_interconnection_port(self.device.hostname)
        self.device.add_stream_table_add_queue(self)

    def add_decap_stream_table(self, from_device, out_port):
        self.forward_type = ForwardEntryType.DECAP
        self.in_port = self.device.lookup_peer_device_interconnection_port(from_device.hostname)
        self.out_port = out_port
        self.device.add_stream_table_add_queue(self)

    def add_forward_stream_table(self, from_device, next_device):
        self.forward_type = ForwardEntryType.FORWARD
        self.in_port = self.device.lookup_peer_device_interconnection_port(from_device.hostname)
        self.out_port = next_device.lookup_peer_device_interconnection_port(self.device.hostname)
        self.device.add_stream_table_add_queue(self)

    def add_local_stream_table(self, in_port, out_port):
        self.forward_type = ForwardEntryType.LOCAL
        self.in_port = in_port
        self.out_port = out_port
        self.device.add_stream_table_add_queue(self)

    def remove_stream_tabel(self):
        self.device.add_stream_table_del_queue(self)

    def __str__(self):
        return "StreamTable(stream_id={}, device={}, forward_type={}, in_port={}, out_port={})".\
            format(self.stream_id, self.device, self.forward_type, self.in_port, self.out_port)

    def __repr__(self):
        return self.__str__()

class Stream:

    def __init__(self, stream_id, src_port, dst_port):
        self.stream_id = stream_id
        self.src_port = src_port
        self.dst_port = dst_port
        self.stream_table = []
        self.path = []

    def add_path(self, path):

        assert(0 == len(self.path))

        if len(path) == 0 : return

        assert(path[0].hostname == self.src_port.device_hostname and \
               path[-1].hostname == self.dst_port.device_hostname)

        self.path = path

        if(len(self.path) == 1):
            stream_table = StreamTable(path[0], self.stream_id)
            stream_table.add_local_stream_table(self.src_port.port_no, self.dst_port.port_no)

            self.stream_table.append(stream_table)

        elif (len(self.path) == 1):
            stream_table = StreamTable(path[0], self.stream_id)
            stream_table.add_encap_stream_table(self.src_port.port_no, path[1])

            self.stream_table.append(stream_table)

            stream_table = StreamTable(path[1], self.stream_id)
            stream_table.add_decap_stream_table(path[0], self.dst_port.port_no)

            self.stream_table.append(stream_table)

        else:
            stream_table = StreamTable(path[0], self.stream_id)
            stream_table.add_encap_stream_table(self.src_port.port_no, path[1])

            self.stream_table.append(stream_table)

            for i in range(1, len(self.path) - 1):
                stream_table = StreamTable(path[i], self.stream_id)
                stream_table.add_forward_stream_table(path[i - 1], path[i + 1])
                self.stream_table.append(stream_table)

            stream_table = StreamTable(path[-1], self.stream_id)
            stream_table.add_decap_stream_table(path[-2], self.dst_port.port_no)
            self.stream_table.append(stream_table)

    def remove_path(self):
        for stream_table in self.stream_table:
            stream_table.remove_stream_tabel()

        self.stream_table = []
        self.path = []

    def __str__(self):
        return "Stream(stream_id: {}, src_port: {}, dst_port: {}, path: {}".\
            format(self.stream_id, self.src_port, self.dst_port, self.path)
    
    def __repr__(self):
        return self.__str__()

class Topology:

    def __init__(self):
        self.path_calculate_unit = PathCalculateUnit()
        self.slave_devices = []
        self.device_name_to_uuid = {}
        threading.Thread(target=self.__update_device_topology_timer, name='update_device_topology_timer').start()

    def add_slave_device(self, device):
        self.slave_devices.append(device)
        self.device_name_to_uuid[device.hostname] = device.uuid
        for port in device.interconnection_link_list:
            self.path_calculate_unit.add_path(port.peer_device_hostname, device.hostname, 1)

    def remove_slave_device(self, device):
        for port in device.interconnection_link_list:
            self.path_calculate_unit.remove_path(port.peer_device_hostname, device.hostname)
        self.slave_devices.remove(device)
        self.device_name_to_uuid.pop(device.hostname)

    def search_slave_device(self, hostname):
        for device in self.slave_devices:
            if device.hostname == hostname:
                return device
        return None

    def search_slave_device_by_uuid(self, uuid):
        for device in self.slave_devices:
            if device.uuid == uuid:
                return device
        return None

    def calculate_path(self, start, end):
        return self.path_calculate_unit.calculate_path(start, end)

    def __update_device_topology_timer(self):
        while True:
            for device in self.slave_devices:
                for link in device.interconnection_link_list:
                    path_vector = self.path_calculate_unit.path_search(link.peer_device_hostname, device.hostname)
                    if not path_vector:
                        path_vector = self.path_calculate_unit.add_path(link.peer_device_hostname, device.hostname, 1)
                    path_vector.mark = 1

            self.path_calculate_unit.clear_outdated_path()
            time.sleep(5)

class SDNController:

    def __init__(self):
        self.stream_table = []
        self.topo = Topology()
        self.opf_stream_id = OPF(1, 4094)
        threading.Thread(target=self.__stream_table_update_timer, name='stream_table_update_timer').start()

    def add_unidirectional_stream(self, src_port, dst_port):
        stream = self.__search_stream(src_port, dst_port)
        if stream:
            return
        stream = Stream(self.opf_stream_id.alloc_offset(), src_port, dst_port)
        self.stream_table.append(stream)

        path_hostname = self.topo.calculate_path(src_port.device_hostname, dst_port.device_hostname)
        if path_hostname:
            path_device = []
            for hostname in path_hostname:
                device = self.topo.search_slave_device(hostname)
                if None == device:
                    return
                path_device.append(device)
            stream.add_path(path_device)

    def remove_unidirectional_stream(self, src_port, dst_port):
        stream = self.__search_stream(src_port, dst_port)
        if stream:
            stream.remove_path()
            self.opf_stream_id.free_offset(stream.stream_id)
            self.stream_table.remove(stream)

    def __search_stream(self, src_port, dst_port):
        for stream in self.stream_table:
            if stream.src_port == src_port and stream.dst_port == dst_port:
                return stream
        return None

    def add_bidirectional_stream(self, port1, port2):
        self.add_unidirectional_stream(port1, port2)
        self.add_unidirectional_stream(port2, port1)

    def remove_bidirectional_stream(self, port1, port2):
        self.remove_unidirectional_stream(port1, port2)
        self.remove_unidirectional_stream(port2, port1)

    def update_stream_table(self, stream):
        path_hostname = self.topo.calculate_path(stream.src_port.device_hostname, stream.dst_port.device_hostname)
        path_device = []
        for hostname in path_hostname:
            device = self.topo.search_slave_device(hostname)
            if None == device: 
                path_device = []
                break
            path_device.append(device)

        if path_device == stream.path:
            return

        stream.remove_path()

        if len(path_device) > 0:
            stream.add_path(path_device)

    def __stream_table_update_timer(self):
        while True:
            for stream in self.stream_table:
                self.update_stream_table(stream)
            time.sleep(3)

    def topology_add_slave_device(self, device):
        self.topo.add_slave_device(device)

    def topology_remove_slave_device(self, device):
        self.topo.remove_slave_device(device)