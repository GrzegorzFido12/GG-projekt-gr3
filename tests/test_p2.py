import os
import unittest

from graph_model import Graph, Node, HyperEdge
from productions.p2 import P2
from visualization import draw

OUTPUT_DIR = "visualizations/p2_visualisations"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def make_graph():
    prod = P2()
    return prod.get_left_side()


class TestP2Isomorphism(unittest.TestCase):

    def setUp(self):
        self.prod = P2()

    def test_can_apply_positive(self):
        """Sprawdza, czy produkcja wykrywa poprawny graf izomorficzny"""
        g = make_graph()
        draw(g, f"{OUTPUT_DIR}/test_positive_before.png")
        self.assertTrue(self.prod.can_apply(g))

    def test_missing_vertex_fails(self):
        """Usunięcie wierzchołka środkowego powinno uniemożliwić produkcję"""
        g = make_graph()
        v3 = g.get_node("v3")
        g.remove_node(v3)
        draw(g, f"{OUTPUT_DIR}/test_missing_vertex_fails.png")
        self.assertFalse(self.prod.can_apply(g))

    def test_wrong_geometry_fails(self):
        """Jeśli v3 nie jest w połowie drogi między v1 i v2, produkcja nie powinna ruszyć"""
        g = Graph()
        v1 = Node(0, 0, "v1")
        v2 = Node(0, 2, "v2")
        v3 = Node(1, 1.5, "v3")  # Nie w środku!
        g.add_node(v1)
        g.add_node(v2)
        g.add_node(v3)
        g.add_edge(HyperEdge((v1, v2), "E", R=1, B=0))
        g.add_edge(HyperEdge((v1, v3), "E", R=3, B=3))
        g.add_edge(HyperEdge((v3, v2), "E", R=2, B=2))

        draw(g, f"{OUTPUT_DIR}/test_wrong_geometry.png")

        self.assertFalse(self.prod.can_apply(g))

    def test_missing_edge_breaks_isomorphism(self):
        """
        czy zmiana grafu do którego stosujemy produkcję poprzez usunięcie losowej krawędzi nie psuje tego mechanizmu
        """
        g = make_graph()

        e_edges = [e for e in g.hyperedges if e.hypertag == "E"]
        g.remove_edge(e_edges[0])

        draw(g, f"{OUTPUT_DIR}/test_missing_edge.png")

        self.assertFalse(self.prod.can_apply(g))

    def test_wrong_attributes_fails(self):
        """Jeśli główna krawędź ma R=0 zamiast R=1, produkcja nie powinna ruszyć"""
        g = make_graph()
        old_edge = next(e for e in g.hyperedges if e.R == 1)
        g.remove_edge(old_edge)
        g.add_edge(HyperEdge(old_edge.nodes, "E", R=0, B=0))

        draw(g, f"{OUTPUT_DIR}/test_wrong_attributes.png")

        self.assertFalse(self.prod.can_apply(g))

    def test_transformation_correctness(self):
        """Sprawdza czy po apply() graf ma poprawną strukturę RHS"""
        g = make_graph()

        draw(g, f"{OUTPUT_DIR}/test_transformation_before.png")

        result = g.apply(self.prod)

        draw(g, f"{OUTPUT_DIR}/test_transformation_after.png")

        self.assertEqual(result, 1, "Produkcja powinna zostać zaaplikowana")

        e_edges = [e for e in g.hyperedges if e.hypertag == "E"]
        self.assertEqual(len(e_edges), 2)

        for e in e_edges:
            self.assertEqual(e.R, 0, "Nowe krawędzie muszą mieć R=0")
            self.assertEqual(e.B, 0, "Nowe krawędzie muszą zachować B=0")

        self.assertIsNotNone(g.get_node("v1"))
        self.assertIsNotNone(g.get_node("v2"))
        self.assertIsNotNone(g.get_node("v3"))

    def test_vertex_coordinates_preserved(self):
        """Sprawdza, czy produkcja nie przesuwa istniejących wierzchołków"""
        g = make_graph()
        v1_coords = (g.get_node("v1").x, g.get_node("v1").y)
        v2_coords = (g.get_node("v2").x, g.get_node("v2").y)
        v3_coords = (g.get_node("v3").x, g.get_node("v3").y)

        g.apply(self.prod)

        v1_after = g.get_node("v1")
        v2_after = g.get_node("v2")
        v3_after = g.get_node("v3")
        self.assertEqual((v1_after.x, v1_after.y), v1_coords)
        self.assertEqual((v2_after.x, v2_after.y), v2_coords)
        self.assertEqual((v3_after.x, v3_after.y), v3_coords)

    def test_missing_adjacent_edges_fails(self):
        """Produkcja nie powinna zadziałać, jeśli długa krawędź (R=1) nie ma towarzyszących krawędzi bocznych"""
        g = Graph()
        v1 = Node(0, 0, "v1")
        v2 = Node(0, 2, "v2")
        v3 = Node(0, 1, "v3")
        g.add_node(v1)
        g.add_node(v2)
        g.add_node(v3)

        g.add_edge(HyperEdge((v1, v2), "E", R=1, B=0))
        g.add_edge(HyperEdge((v1, v3), "E", R=1, B=0))

        draw(g, f"{OUTPUT_DIR}/test_missing_adj_fails.png")
        self.assertFalse(self.prod.can_apply(g))

    def test_embedded_in_larger_graph(self):
        """Sprawdza, czy produkcja P2 działa poprawnie, gdy pasujący podgraf jest częścią większej struktury"""
        g = make_graph()

        v_ext1 = Node(2, 0, "ext1")
        v_ext2 = Node(2, 2, "ext2")
        g.add_node(v_ext1)
        g.add_node(v_ext2)

        v2 = g.get_node("v2")
        g.add_edge(HyperEdge((v2, v_ext1), "E", R=0, B=1))
        g.add_edge(HyperEdge((v_ext1, v_ext2), "E", R=0, B=1))
        g.add_edge(HyperEdge((v_ext2, v2), "E", R=0, B=1))

        draw(g, f"{OUTPUT_DIR}/test_embedded_before.png")

        result = g.apply(self.prod)

        draw(g, f"{OUTPUT_DIR}/test_embedded_after.png")

        self.assertEqual(result, 1)
        self.assertIsNotNone(g.get_node("ext1"))
        self.assertEqual(len([e for e in g.hyperedges if "ext1" in e.label]), 2)

    def test_multiple_candidates_only_one_applied(self):
        """Sprawdza, czy przy dwóch możliwych miejscach aplikacji, produkcja zmienia tylko jedno na raz"""
        g = make_graph()

        v4 = Node(5, 0, "v4")
        v5 = Node(5, 2, "v5")
        v6 = Node(5, 1, "v6")
        g.add_node(v4)
        g.add_node(v5)
        g.add_node(v6)
        g.add_edge(HyperEdge((v4, v5), "E", R=1, B=0))
        g.add_edge(HyperEdge((v4, v6), "E", R=3, B=3))
        g.add_edge(HyperEdge((v6, v5), "E", R=2, B=2))

        draw(g, f"{OUTPUT_DIR}/test_multiple_before.png")

        r1_before = [e for e in g.hyperedges if e.R == 1]
        self.assertEqual(len(r1_before), 2)

        result = g.apply(self.prod)

        draw(g, f"{OUTPUT_DIR}/test_multiple_after.png")

        r1_after = [e for e in g.hyperedges if e.R == 1]
        self.assertEqual(result, 1)
        self.assertEqual(len(r1_after), 1)

    def test_no_match_with_different_label(self):
        """Sprawdza, czy produkcja ignoruje krawędzie o innym tagu niż 'E', nawet jeśli geometria się zgadza"""
        g = Graph()
        v1 = Node(0, 0, "v1")
        v2 = Node(0, 2, "v2")
        v3 = Node(0, 1, "v3")
        g.add_node(v1)
        g.add_node(v2)
        g.add_node(v3)

        g.add_edge(HyperEdge((v1, v2), "Q", R=1, B=0))
        g.add_edge(HyperEdge((v1, v3), "Q", R=3, B=3))
        g.add_edge(HyperEdge((v3, v2), "Q", R=2, B=2))

        draw(g, f"{OUTPUT_DIR}/test_different_label.png")

        self.assertFalse(self.prod.can_apply(g))


if __name__ == '__main__':
    unittest.main()
