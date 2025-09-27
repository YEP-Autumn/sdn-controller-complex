from dijkstar import Graph, find_path
from __test_data import TestData


graph = Graph()
for link in TestData.device_1:
    src = link['src']['id']
    dst = link['dst']['id']
    graph.add_edge(src, dst, 1)

for link in TestData.device_2:
    src = link['src']['id']
    dst = link['dst']['id']
    graph.add_edge(src, dst, 1)

for link in TestData.device_3:
    src = link['src']['id']
    dst = link['dst']['id']
    graph.add_edge(src, dst, 1)

for link in TestData.device_4:
    src = link['src']['id']
    dst = link['dst']['id']
    graph.add_edge(src, dst, 1)

path = find_path(graph, 'device_1', 'device_4')
print(path.nodes)
print(path.total_cost)
