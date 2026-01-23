from graph_model import Graph, Node, HyperEdge
from visualization import draw


def make_graph() -> Graph:
    g = Graph()
    n1 = Node(3, 13, "v1")
    n2 = Node(50, 13, "v2")
    n3 = Node(70, 7, "v3")
    n4 = Node(50, 1, "v4")
    n5 = Node(3, 1, "v5")
    n6 = Node(1, 5, "v6")
    n7 = Node(1, 9, "v7")
    n8 = Node(5, 9, "v8")
    n9 = Node(17, 9, "v9")
    n10 = Node(17, 5, "v10")
    n11 = Node(5, 5, "v11")

    for n in [n1, n2, n3, n4, n5, n6, n7, n8, n9, n10, n11]:
        g.add_node(n)

    g.add_edge(HyperEdge((n1, n7), "E", R=0, B=1))
    g.add_edge(HyperEdge((n7, n6), "E", R=0, B=1))
    g.add_edge(HyperEdge((n6, n5), "E", R=0, B=1))
    g.add_edge(HyperEdge((n5, n11), "E", R=0, B=0))
    g.add_edge(HyperEdge((n11, n8), "E", R=0, B=0))
    g.add_edge(HyperEdge((n8, n1), "E", R=0, B=0))
    g.add_edge(HyperEdge((n1, n2), "E", R=0, B=1))
    g.add_edge(HyperEdge((n8, n9), "E", R=0, B=0))
    g.add_edge(HyperEdge((n11, n10), "E", R=0, B=0))
    g.add_edge(HyperEdge((n5, n4), "E", R=0, B=1))
    g.add_edge(HyperEdge((n4, n10), "E", R=0, B=0))
    g.add_edge(HyperEdge((n10, n9), "E", R=0, B=0))
    g.add_edge(HyperEdge((n9, n2), "E", R=0, B=0))
    g.add_edge(HyperEdge((n2, n3), "E", R=0, B=1))
    g.add_edge(HyperEdge((n3, n4), "E", R=0, B=1))

    g.add_edge(HyperEdge((n9, n2, n3, n4, n10), "P", R=0))
    g.add_edge(HyperEdge((n11, n10, n4, n5), "Q", R=0))
    return g

