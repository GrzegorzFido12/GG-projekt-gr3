from graph_model import Graph, Node, HyperEdge
from productions.p12 import P12
import unittest


def make_septagon():
        g = Graph()

        nodes = [Node(0.0, 0.0, f"v{i}") for i in range(7)]
        for n in nodes:
            g.add_node(n)

        # Q element
        q = HyperEdge(
            nodes=tuple(nodes),
            hypertag="Q",
            R=0,
            B=0
        )
        g.add_edge(q)

        # E boundary cycle
        for i in range(7):
            e = HyperEdge(
                nodes=(nodes[i], nodes[(i + 1) % 7]),
                hypertag="E",
                R=0,
                B=1
            )
            g.add_edge(e)

        return g
class TestP12Isomorphism(unittest.TestCase):

    def setUp(self):
        self.prod = P12()
    

    def test_can_apply_to_isomorphic_graph(self):
        """
        czy da się wykonac produkcję do grafu izomorficznego z grafem lewej strony produkcji
        """
        g = make_septagon()
        self.assertTrue(self.prod.can_apply(g))

    def test_missing_vertex_breaks_isomorphism(self):
        """
        czy zmiana grafu do którego stosujemy produkcję poprzez
usunięcie losowego wierzchołka nie psuje tego mechanizmu
        """
        g = make_septagon()

        node = g.nodes[0]
        g.remove_node(node)

        self.assertFalse(self.prod.can_apply(g))
        
    def test_missing_edge_breaks_isomorphism(self):
        """
        czy zmiana grafu do którego stosujemy produkcję poprzez usunięcie losowej krawędzi nie psuje tego mechanizmu
        """
        g = make_septagon()

        e_edges = [e for e in g.hyperedges if e.hypertag == "E"]
        g.remove_edge(e_edges[0])

        self.assertFalse(self.prod.can_apply(g))

    def test_relabeling_vertex_breaks_isomorphism(self):
        """
        czy zmiana grafu do którego stosujemy produkcję poprzez
zmianę etykiety losowego wierzchołka nie psuje tego
mechanizmu
        """
        g = make_septagon()

        node = g.nodes[0]
        node.label = "X"

        self.assertTrue(self.prod.can_apply(g))

    def test_septagon_as_subgraph_of_larger_graph(self):
        """
        czy umieszczenie grafu izomorficznego z grafem lewej strony
jako podgrafu większego grafu nie psuje tego mechanizmu
        """
        g = make_septagon()

        # add extra unrelated structure
        extra_nodes = [Node(1.0, 1.0, f"x{i}") for i in range(3)]
        for n in extra_nodes:
            g.add_node(n)

        e = HyperEdge(
                nodes=(extra_nodes[0], extra_nodes[1]),
                hypertag="E",
                R=0,
                B=0
            )
        g.add_edge(e)

        self.assertTrue(self.prod.can_apply(g))


if __name__ == "__main__":
    unittest.main()



