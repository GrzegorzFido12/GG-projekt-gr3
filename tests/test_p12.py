from graph_model import Node
from productions.p12 import P12
import unittest

def make_septagon():
    prod = P12()
    return prod.get_left_side()

def make_big_graph_with_septagon_subgraph():
    g = make_septagon()
    # add extra unrelated structure
    extra_nodes = [Node(1.0, 1.0, f"x{i}") for i in range(3)]
    for n in extra_nodes:
        g.add_node(n)
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
        g = make_big_graph_with_septagon_subgraph()

        self.assertTrue(self.prod.can_apply(g))

    def test_apply_does_not_damage_supergraph(self):
        """
        czy jeśli graf izomorficzny z grafem lewej strony jest
umieszczony jako podgraf większego grafu, to czy produkcja nie
„uszkadza” większego grafu
        """
        g = make_big_graph_with_septagon_subgraph()

        nodes_before = set(g.nodes)
        edges_before = set(g.hyperedges)

        production = P12()
        g.apply(production)

        # elementy spoza Q
        outside_nodes = {n for n in nodes_before if n.label.startswith("OUT")}
        outside_edges = {e for e in edges_before if e.hypertag == "OUT"}

        self.assertTrue(outside_nodes.issubset(set(g.nodes)))
        self.assertTrue(outside_edges.issubset(set(g.hyperedges)))

    def test_embedding_transformation(self):
        """
        czy jeśli graf izomorficzny z grafem lewej strony jest
umieszczony w jako podgraf większego grafu, to czy produkcja
dobrze transformuje osadzenie
        """
        g = make_septagon()

        q_before = [e for e in g.hyperedges if e.hypertag == "Q"][0]
        nodes_before = set(q_before.nodes)

        production = P12()
        g.apply(production)

        q_after = [e for e in g.hyperedges if e.hypertag == "Q"][0]

        self.assertEqual(q_after.R, 1)
        self.assertEqual(set(q_after.nodes), nodes_before)

    def test_rhs_graph_structure(self):
        """
        czy graf izomorficzny z grafem prawej strony jest poprawny (czy
ma wszystkie wierzchołki, krawędzie i poprawne etykiety)
        """
        g = make_septagon()

        production = P12()
        g.apply(production)

        q_edges = [e for e in g.hyperedges if e.hypertag == "Q"]
        e_edges = [e for e in g.hyperedges if e.hypertag == "E"]

        self.assertEqual(len(q_edges), 1)
        self.assertEqual(q_edges[0].R, 1)
        self.assertEqual(len(q_edges[0].nodes), 7)

        self.assertEqual(len(e_edges), 7)
        for e in e_edges:
            self.assertEqual(len(e.nodes), 2)
        
    def test_vertex_coordinates_preserved(self):
        """czy współrzędne nowych wierzchołków w tym grafie są
poprawne"""
        g = make_septagon()

        coords_before = {
            n.label: (n.x, n.y) for n in g.nodes
        }

        production = P12()
        g.apply(production)

        for n in g.nodes:
            self.assertEqual(coords_before[n.label], (n.x, n.y))







