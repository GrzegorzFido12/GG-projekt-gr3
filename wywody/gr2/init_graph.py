from graph_model import Graph, Node, HyperEdge


def make_graph() -> Graph:
    g = Graph()

    # Left
    w0 = Node(0.0, 1.0, "B")
    w1 = Node(0.5, 2.0, "C")
    w2 = Node(1.0, 1.0, "J")
    w3 = Node(1.0, -1.0, "I")
    w4 = Node(0.5, -2.0, "H")
    w5 = Node(0.0, -1.0, "A")

    nodes = [w0, w1, w2, w3, w4, w5]
    for n in nodes:
        g.add_node(n)
    for u, v in ((w0, w1), (w0, w5), (w4, w5)):
        g.add_edge(HyperEdge((u, v), "E", boundary=True, R=0, B=1))
    for u, v in ((w1, w2), (w2, w3), (w3, w4)):
        g.add_edge(HyperEdge((u, v), "E", boundary=False, R=0, B=1))

    # Right
    w8 = Node(4.0, -2.0, "G")
    w9 = Node(5.0, -1.0, "F")
    w10 = Node(5.0, 1.0, "E")
    w11 = Node(4.0, 2.0, "D")
    nodes = [w8, w9, w10, w11]
    for n in nodes:
        g.add_node(n)
    for u, v in ((w8, w9), (w9, w10), (w10, w11), (w1, w11), (w4, w8)):
        g.add_edge(HyperEdge((u, v), "E", boundary=True, R=0, B=1))

    # Connector
    w6 = Node(3.0, 1.0, "K")
    w7 = Node(3.0, -1.0, "L")
    nodes = [w6, w7]
    for n in nodes:
        g.add_node(n)
    for u, v in ((w2, w6), (w3, w7), (w6, w7)):
        g.add_edge(HyperEdge((u, v), "E", boundary=False, R=0, B=1))

    for u, v in ((w7, w8), (w6, w11)):
        g.add_edge(HyperEdge((u, v), "E", boundary=False, R=0, B=1))

    # Hyperedges
    g.add_edge(HyperEdge(tuple((w1, w2, w6, w11)), "Q", R=0))
    g.add_edge(HyperEdge(tuple((w2, w6, w7, w3)), "Q", R=0))
    g.add_edge(HyperEdge(tuple((w3, w7, w8, w4)), "Q", R=0))
    g.add_edge(HyperEdge(tuple((w6, w7, w8, w9, w10, w11)), "S", R=0))
    g.add_edge(HyperEdge(tuple((w0, w1, w2, w3, w4, w5)), "S", R=0))

    return g
