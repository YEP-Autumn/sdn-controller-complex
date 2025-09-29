from pprint import pprint
import uuid
from dijkstar import Graph, find_path

from __test_data import TestData

class Port:
    def __init__(self, port_no):
        self.port_no = port_no

    def __hash__(self):
        return hash(self.port_no)

    def __eq__(self, other):
        return self.port_no == other.port_no

class InterconnectionPort(Port):
    def __init__(self, port_no):
        super().__init__(port_no)


class PathVector:
    def __init__(self, start, end, weight):
        self.start = start
        self.end = end
        self.weight = weight

    def __hash__(self):
        return hash((self.start, self.end))

    def __eq__(self, other):
        return self.start == other.start and self.end == other.end

class SlaveDevice:

    uuid = None

    hostname = None

    port_list = set()

    interconnection_link_list = set()

    def __init__(self):
        pass

    def add_port(self, port_no, port_type = None, mac = None, ip = None):
        self.port_list.add(Port(port_no, port_type, mac, ip))

    def remove_port(self, port_no):
        self.port_list.discard(Port(port_no))

    def add_interconnection_link(self, port_no):
        self.interconnection_link_list.add(InterconnectionPort(port_no))

    def remove_interconnection_link(self, port_no):
        self.interconnection_link_list.discard(InterconnectionPort(port_no))

class PathCalculateUnit:

    path_vector = set()

    def __init__(self):
        pass

    def calculate_path(self, start, end):
        graph = Graph()
        for path in self.path_vector:
            graph.add_edge(path.start, path.end, path.weight)
            # graph.add_edge(path.end, path.start, path.weight)

        try:
            path_info = find_path(graph, start, end)
            return path_info.nodes
        except:
            return None

    def add_path(self, start, end, weight):
        path = self.__path_search(start, end)

        if not path:
            self.path_vector.add(PathVector(start, end, weight))
        else:
            path.weight = weight

    def remove_path(self, start, end):
        self.path_vector.discard(PathVector(start, end, 0))

    def __path_search(self, start, end):
        for path in self.path_vector:
            if path.start == start and path.end == end:
                return path
        return None



class SDNController:

    slave_devices = {}

    path_calculate_unit = None

    stream_table = {}

    def __init__(self):
        self.path_calculate_unit = PathCalculateUnit()



if __name__ == "__main__":
    path_calculate_unit = PathCalculateUnit()

    for link in TestData.device_1['interconnection_links']:
        path_calculate_unit.add_path(link['src']['id'], link['dst']['id'], 0)

    for link in TestData.device_2['interconnection_links']:
        path_calculate_unit.add_path(link['src']['id'], link['dst']['id'], 0)

    for link in TestData.device_3['interconnection_links']:
        path_calculate_unit.add_path(link['src']['id'], link['dst']['id'], 0)   
    
    for link in TestData.device_4['interconnection_links']:
        path_calculate_unit.add_path(link['src']['id'], link['dst']['id'], 0)

    pprint(path_calculate_unit.path_vector)
    path = path_calculate_unit.calculate_path('device_1', 'device_4')
    pprint(path)