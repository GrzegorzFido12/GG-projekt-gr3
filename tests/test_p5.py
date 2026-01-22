import unittest
import os
from productions.p5 import P5
from graph_model import Graph, Node, HyperEdge
from visualization import draw

OUTPUT_DIR = "visualizations/p5_visualisations"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def create_basic_quad_for_p5(R=1):
    """
    Tworzy graf gotowy do produkcji P5 (lub nie, w zależności od argumentów).
    Domyślnie:
    Q marked for refinement (R=1).
    All 4 sides are already broken via midpoints:
      v1 - m12 - v2
      v2 - m23 - v3
      v3 - m34 - v4
      v4 - m41 - v1
    """
    g = Graph()

    v1 = Node(0, 0, "v1")
    v2 = Node(4, 0, "v2")
    v3 = Node(4, 4, "v3")
    v4 = Node(0, 4, "v4")

    for v in (v1, v2, v3, v4):
        g.add_node(v)

    m12 = Node(2, 0, "m12", hanging=True)
    m23 = Node(4, 2, "m23", hanging=True)
    m34 = Node(2, 4, "m34", hanging=True)
    m41 = Node(0, 2, "m41", hanging=True)

    for m in (m12, m23, m34, m41):
        g.add_node(m)

    g.add_edge(HyperEdge((v1, m12), "E", boundary=True, R=0, B=1))
    g.add_edge(HyperEdge((m12, v2), "E", boundary=True, R=0, B=1))

    g.add_edge(HyperEdge((v2, m23), "E", boundary=True, R=0, B=1))
    g.add_edge(HyperEdge((m23, v3), "E", boundary=True, R=0, B=1))

    g.add_edge(HyperEdge((v3, m34), "E", boundary=True, R=0, B=1))
    g.add_edge(HyperEdge((m34, v4), "E", boundary=True, R=0, B=1))

    g.add_edge(HyperEdge((v4, m41), "E", boundary=True, R=0, B=1))
    g.add_edge(HyperEdge((m41, v1), "E", boundary=True, R=0, B=1))

    g.add_edge(HyperEdge((v1, v2, v3, v4), "Q", boundary=False, R=R, B=0))

    return g


class TestP5(unittest.TestCase):

    def draw(self, graph, step_name):
        """Pomocnicza funkcja do wizualizacji kroków testu"""
        test_method_name = self._testMethodName
        filename = f"{OUTPUT_DIR}/{test_method_name}_{step_name}.png"
        draw(graph, filename)

    def test_apply_isomorphic(self):
        """Test czy produkcja aplikuje się do idealnego grafu wejściowego."""
        g = create_basic_quad_for_p5()
        self.draw(g, "before")

        prod = P5()
        self.assertTrue(prod.can_apply(g))

        result = g.apply(prod)
        self.draw(g, "after")

        self.assertEqual(result, 1)

        centroids = [n for n in g.nodes if n.label.startswith("c_")]
        self.assertEqual(
            len(centroids), 1, "Expected exactly one centroid node after P5"
        )

        q_edges = [e for e in g.hyperedges if e.hypertag == "Q"]
        self.assertEqual(len(q_edges), 4, "Expected 4 Q edges after P5")
        self.assertTrue(
            all(e.R == 0 for e in q_edges), "All new Q edges should have R=0"
        )

    def test_missing_midpoint(self):
        """Test negatywny: Jeden bok nie jest podzielony węzłem wiszącym."""
        g = create_basic_quad_for_p5()

        # Usuwamy podział na boku v1-v2 (usuwamy m12 i krawędzie do niego)
        m12 = g.get_node("m12")
        edges_to_remove = [e for e in g.hyperedges if m12 in e.nodes]
        for e in edges_to_remove:
            g.remove_edge(e)
        g.remove_node(m12)

        # Dodajemy z powrotem bezpośrednią krawędź v1-v2
        v1 = g.get_node("v1")
        v2 = g.get_node("v2")
        g.add_edge(HyperEdge((v1, v2), "E", boundary=True, R=0, B=1))

        self.draw(g, "before")

        prod = P5()
        self.assertFalse(prod.can_apply(g))

        result = g.apply(prod)
        self.draw(g, "after")
        self.assertEqual(result, 0)

    def test_apply_R0(self):
        """Test negatywny: Q ma R=0."""
        g = create_basic_quad_for_p5(R=0)
        self.draw(g, "before")

        prod = P5()
        self.assertFalse(prod.can_apply(g))

        result = g.apply(prod)
        self.draw(g, "after")
        self.assertEqual(result, 0)

    def test_wrong_hypertag(self):
        """Test negatywny: Zła etykieta (P zamiast Q)."""
        g = create_basic_quad_for_p5()
        q_edge = [e for e in g.hyperedges if e.hypertag == "Q"][0]
        # remove Q, add P
        g.remove_edge(q_edge)
        g.add_edge(HyperEdge(q_edge.nodes, "P", boundary=False, R=1, B=0))

        self.draw(g, "before")

        prod = P5()
        self.assertFalse(prod.can_apply(g))

        result = g.apply(prod)
        self.draw(g, "after")
        self.assertEqual(result, 0)


if __name__ == "__main__":
    unittest.main()
