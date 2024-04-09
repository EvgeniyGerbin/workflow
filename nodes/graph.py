import networkx as nx


def build_workflow_graph(nodes, edge):
    graph = nx.DiGraph()
    for node in nodes:
        graph.add_node(id=node.id, type=node.type, name=node.name, status=node.status)

    for edge in edge:
        graph.add_edge(u_of_edge=edge.from_node_id, v_of_edge=edge.to_node_id)

    return graph
