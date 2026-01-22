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


if __name__ == "__main__":
    unittest.main()
