from graph_model import Graph, Node, HyperEdge


def make_graph() -> Graph:
    graph = Graph()

    v_A = Node(0, 5, "A")
    v_B = Node(0, 10, "B")
    v_C = Node(5, 15, "C")
    v_D = Node(40, 15, "D")
    v_E = Node(50, 10, "E")
    v_F = Node(50, 5, "F")
    v_G = Node(40, 0, "G")
    v_H = Node(5, 0, "H")
    v_I = Node(10, 5, "I")
    v_J = Node(10, 10, "J")
    v_K = Node(30, 10, "K")
    v_L = Node(30, 5, "L")

    for v in [v_A, v_B, v_C, v_D, v_E, v_F, v_G, v_H, v_I, v_J, v_K, v_L]:
        graph.add_node(v)

    # Outline A -> H
    graph.add_edge(HyperEdge((v_A, v_B), "E", R=0, B=1))
    graph.add_edge(HyperEdge((v_B, v_C), "E", R=0, B=1))
    graph.add_edge(HyperEdge((v_C, v_D), "E", R=0, B=1))
    graph.add_edge(HyperEdge((v_D, v_E), "E", R=0, B=1))
    graph.add_edge(HyperEdge((v_E, v_F), "E", R=0, B=1))
    graph.add_edge(HyperEdge((v_F, v_G), "E", R=0, B=1))
    graph.add_edge(HyperEdge((v_G, v_H), "E", R=0, B=1))
    graph.add_edge(HyperEdge((v_H, v_A), "E", R=0, B=1))

    # Central Quad I - > L
    graph.add_edge(HyperEdge((v_I, v_J), "E", R=0, B=0))
    graph.add_edge(HyperEdge((v_J, v_K), "E", R=0, B=0))
    graph.add_edge(HyperEdge((v_K, v_L), "E", R=0, B=0))
    graph.add_edge(HyperEdge((v_L, v_I), "E", R=0, B=0))

    # Connectors: Outline -> Central Quad
    graph.add_edge(HyperEdge((v_C, v_J), "E", R=0, B=0))
    graph.add_edge(HyperEdge((v_D, v_K), "E", R=0, B=0))
    graph.add_edge(HyperEdge((v_G, v_L), "E", R=0, B=0))
    graph.add_edge(HyperEdge((v_H, v_I), "E", R=0, B=0))

    # Figures
    graph.add_edge(HyperEdge((v_H, v_G, v_I, v_L), "Q", R=0))
    graph.add_edge(HyperEdge((v_D, v_E, v_F, v_G, v_L, v_K), "S", R=0))

    return graph
