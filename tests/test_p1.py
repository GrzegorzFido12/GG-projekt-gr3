import unittest
import os
from productions.p1 import P1
from graph_model import Graph, Node, HyperEdge
from visualization import draw

OUTPUT_DIR = "visualizations/p1_visualisations"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def create_basic_quad_for_p1(R=1):
    """
    Tworzy graf zawierający czworokąt.

    Args:
        R: atrybut R dla elementu Q
    """
    g = Graph()

    v1 = Node(0, 0, "v1")
    v2 = Node(4, 0, "v2")
    v3 = Node(4, 4, "v3")
    v4 = Node(0, 4, "v4")

    for v in (v1, v2, v3, v4):
        g.add_node(v)

    g.add_edge(HyperEdge((v1, v2), "E", boundary=True, R=0, B=1))
    g.add_edge(HyperEdge((v2, v3), "E", boundary=True, R=0, B=1))
    g.add_edge(HyperEdge((v3, v4), "E", boundary=True, R=0, B=1))
    g.add_edge(HyperEdge((v4, v1), "E", boundary=True, R=0, B=1))

    g.add_edge(HyperEdge((v1, v2, v3, v4), "Q", boundary=False, R=R, B=0))

    return g


class TestP1(unittest.TestCase):

    def draw(self, graph, step_name):
        """Pomocnicza funkcja do wizualizacji kroków testu"""
        test_method_name = self._testMethodName
        filename = f"{OUTPUT_DIR}/{test_method_name}_{step_name}.png"
        draw(graph, filename)

    def test_apply_isomorphic(self):
        """Test czy produkcja aplikuje się do idealnego grafu wejściowego."""
        g = create_basic_quad_for_p1()
        self.draw(g, "before")

        prod = P1()
        self.assertTrue(prod.can_apply(g))

        result = g.apply(prod)
        self.draw(g, "after")

        self.assertEqual(result, 1)

        # All 4 E edges should now have R=1
        e_edges = [e for e in g.hyperedges if e.hypertag == "E"]
        self.assertEqual(len(e_edges), 4)
        for e in e_edges:
            self.assertEqual(e.R, 1)

        # Q should still be there with R=1
        q_edges = [e for e in g.hyperedges if e.hypertag == "Q"]
        self.assertEqual(len(q_edges), 1)
        self.assertEqual(q_edges[0].R, 1)

    def test_apply_R0(self):
        """Test czy produkcja NIE aplikuje się, gdy Q ma R=0."""
        g = create_basic_quad_for_p1(R=0)
        self.draw(g, "before")

        prod = P1()
        self.assertFalse(prod.can_apply(g))

        result = g.apply(prod)
        self.draw(g, "after")
        self.assertEqual(result, 0)

        # Edges should remain R=0
        e_edges = [e for e in g.hyperedges if e.hypertag == "E"]
        for e in e_edges:
            self.assertEqual(e.R, 0)

    def test_apply_already_refined(self):
        """Test czy produkcja NIE aplikuje się, gdy krawędzie są już zaznaczone (R=1)."""
        g = create_basic_quad_for_p1()
        # Set all E edges to R=1 manually
        for e in g.hyperedges:
            if e.hypertag == "E":
                e.R = 1

        self.draw(g, "before")

        prod = P1()
        # Should simulate 'None' match because looking for E with R=0
        self.assertFalse(prod.can_apply(g))

        result = g.apply(prod)
        self.draw(g, "after")
        self.assertEqual(result, 0)

    def test_wrong_hypertag(self):
        """Test negatywny: Zła etykieta (P zamiast Q)."""
        g = create_basic_quad_for_p1()
        q_edge = [e for e in g.hyperedges if e.hypertag == "Q"][0]
        # remove Q, add P
        g.remove_edge(q_edge)
        g.add_edge(HyperEdge(q_edge.nodes, "P", boundary=False, R=1, B=0))

        self.draw(g, "before")
        prod = P1()
        self.assertFalse(prod.can_apply(g))
        g.apply(prod)
        self.draw(g, "after")

    def test_embedded_in_larger_graph_preserves_context(self):
        """
        Test funkcjonalny: P1 powinno oznaczyć R=1 tylko dla krawędzi E wewnątrz Q,
        a dodatkowy kontekst (węzły/krawędzie spoza Q) musi pozostać nienaruszony.
        """
        g = create_basic_quad_for_p1(R=1)

        ext1 = Node(10, 0, "ext1")
        ext2 = Node(10, 4, "ext2")
        g.add_node(ext1)
        g.add_node(ext2)

        v2 = g.get_node("v2")
        g.add_edge(HyperEdge((v2, ext1), "E", boundary=True, R=0, B=1))
        g.add_edge(HyperEdge((ext1, ext2), "E", boundary=True, R=0, B=1))

        self.draw(g, "before")

        prod = P1()
        self.assertTrue(prod.can_apply(g))

        result = g.apply(prod)

        self.draw(g, "after")
        self.assertEqual(result, 1)

        # Context retained
        self.assertIsNotNone(g.get_node("ext1"))
        self.assertIsNotNone(g.get_node("ext2"))

        # Other edges cant change R
        ext_edges = [
            e
            for e in g.hyperedges
            if e.hypertag == "E" and ("ext1" in e.label or "ext2" in e.label)
        ]
        self.assertEqual(len(ext_edges), 2)
        for e in ext_edges:
            self.assertEqual(e.R, 0)

    def test_missing_boundary_edges_breaks_match(self):
        """
        Test negatywny: jeśli usuniemy jedną krawędź E (zostawiając 3/4),
        P1 nie ma czego oznaczać.
        """
        g = create_basic_quad_for_p1(R=1)

        v1 = g.get_node("v1")
        v2 = g.get_node("v2")

        edges_to_remove = [
            e
            for e in g.hyperedges
            if e.hypertag == "E" and v1 in e.nodes and v2 in e.nodes
        ]
        # Only one edge removed
        self.assertTrue(len(edges_to_remove) > 0)
        g.remove_edge(edges_to_remove[0])

        self.draw(g, "before")

        prod = P1()
        self.assertFalse(prod.can_apply(g))

        result = g.apply(prod)
        self.draw(g, "after")
        self.assertEqual(result, 0)

    def test_larger_graph_wont_apply(self):
        """
        Test negatywny: Graf jest pięciokątem (5 węzłów, 5 krawędzi, Q łączy 5 węzłów).
        P1 wymaga Q 4-węzłowego.
        """
        g = Graph()
        nodes = [
            Node(0, 0, "v0"),
            Node(4, 0, "v1"),
            Node(6, 3, "v2"),
            Node(3, 6, "v3"),
            Node(-2, 3, "v4"),
        ]
        for n in nodes:
            g.add_node(n)

        # 5 egdes
        for i in range(5):
            u = nodes[i]
            v = nodes[(i + 1) % 5]
            g.add_edge(HyperEdge((u, v), "E", boundary=True, R=0, B=1))

        # Q connects 5 edges
        g.add_edge(HyperEdge(tuple(nodes), "Q", boundary=False, R=1, B=0))

        self.draw(g, "before")

        prod = P1()
        self.assertFalse(prod.can_apply(g))

        result = g.apply(prod)
        self.draw(g, "after")
        self.assertEqual(result, 0)


if __name__ == "__main__":
    unittest.main()
