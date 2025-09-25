from dijkstar import Graph, find_path

graph = Graph()
graph.add_edge(1, 2, 10)
graph.add_edge(1, 3, 5)
graph.add_edge(2, 3, 2)
graph.add_edge(2, 4, 1)
graph.add_edge(3, 4, 3)
graph.add_edge(1,4, 100)

path = find_path(graph, 1, 4)
print(path.nodes)
print(path.total_cost)