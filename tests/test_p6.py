import os
import unittest

from graph_model import Graph, Node, HyperEdge
from productions.p6 import P6
from visualization import draw

OUTPUT_DIR = "visualizations/p6_visualisations"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def make_graph():
    prod = P6()
    return prod.get_left_side()


class TestP6Production(unittest.TestCase):
    def setUp(self):
        self.prod = P6()

    def test_transformation_success(self):
        """Sprawdza poprawną aplikację P6 przy spełnionym RFC"""
        g = make_graph()

        # Upewniamy się, że warunek RFC jest spełniony (przynajmniej jedna krawędź E ma R=1)
        # W Twoim make_graph() / get_left_side() pierwsza krawędź ma już R=1, więc to zadziała.

        draw(g, f"{OUTPUT_DIR}/test_before.png")
        result = g.apply(self.prod)
        draw(g, f"{OUTPUT_DIR}/test_after.png")

        self.assertEqual(result, 1, "Produkcja P6 powinna zostać zaaplikowana, bo RFC jest spełnione")
        p_edge = [e for e in g.hyperedges if e.hypertag == "P"][0]
        self.assertEqual(p_edge.R, 1, "Atrybut R krawędzi P powinien zmienić się na 1")

    def test_already_marked_fails(self):
        """Produkcja nie powinna się zaaplikować, jeśli R jest już równe 1"""
        g = make_graph()
        p_edge = [e for e in g.hyperedges if e.hypertag == "P"][0]
        g.remove_edge(p_edge)
        g.add_edge(HyperEdge(p_edge.nodes, "P", R=1))
        draw(g, f"{OUTPUT_DIR}/test_already_marked.png")
        result = g.apply(self.prod)
        self.assertEqual(result, 0, "Produkcja nie powinna działać dla R=1")

    def test_wrong_topology_fails(self):
        """Produkcja nie powinna działać, jeśli krawędź P ma inną liczbę węzłów niż 5 (np. 4)"""
        g = Graph()
        n1 = Node(0, 0, "x1")
        n2 = Node(1, 0, "x2")
        n3 = Node(1, 1, "x3")
        n4 = Node(0, 1, "x4")
        nodes = [n1, n2, n3, n4]
        for n in nodes:
            g.add_node(n)

        g.add_edge(HyperEdge((n1, n2), "E", R=1, B=1))
        g.add_edge(HyperEdge((n2, n3), "E", R=0, B=1))
        g.add_edge(HyperEdge((n3, n4), "E", R=0, B=1))
        g.add_edge(HyperEdge((n4, n1), "E", R=0, B=1))

        g.add_edge(HyperEdge(tuple(nodes), "P", R=0))

        draw(g, f"{OUTPUT_DIR}/test_wrong_topology.png")

        self.assertFalse(self.prod.can_apply(g), "P6 powinna zostać odrzucona dla 4 węzłów, nawet przy spełnionym RFC")

    def test_vertex_coordinates_preserved(self):
        """Sprawdza, czy współrzędne węzłów pozostają niezmienione"""
        g = make_graph()
        original_coords = [(n.x, n.y) for n in g.nodes]

        g.apply(self.prod)

        new_coords = [(n.x, n.y) for n in g.nodes]
        self.assertEqual(original_coords, new_coords, "Współrzędne węzłów nie mogą się zmienić")

    def test_embedded_in_larger_graph(self):
        """Testuje, czy P6 zadziała, gdy pentagon dzieli krawędź z innym wielokątem (np. kwadratem)"""
        g = make_graph()

        v4 = g.get_node("v4")
        v5 = g.get_node("v5")
        extra_v1 = Node(3.0, 2.0, "extra1")
        extra_v2 = Node(3.0, 0.0, "extra2")

        g.add_node(extra_v1)
        g.add_node(extra_v2)

        g.add_edge(HyperEdge((v4, extra_v1), "E", R=0, B=1))
        g.add_edge(HyperEdge((extra_v1, extra_v2), "E", R=0, B=1))
        g.add_edge(HyperEdge((extra_v2, v5), "E", R=0, B=1))

        draw(g, f"{OUTPUT_DIR}/test_embedded_before.png")

        result = g.apply(self.prod)

        draw(g, f"{OUTPUT_DIR}/test_embedded_after.png")

        self.assertEqual(result, 1)
        p_edge = [e for e in g.hyperedges if e.hypertag == "P"][0]
        self.assertEqual(p_edge.R, 1)
        self.assertIsNotNone(g.get_node("extra1"))

    def test_multiple_candidates(self):
        """Sprawdza, czy przy dwóch pentagonach produkcja aplikuje się tylko do jednego na raz"""
        g = make_graph()

        nodes2 = [
            Node(5.0, 0.0, "sec1"), Node(5.0, 2.0, "sec2"),
            Node(6.0, 3.0, "sec3"), Node(7.0, 2.0, "sec4"), Node(7.0, 0.0, "sec5")
        ]
        for n in nodes2:
            g.add_node(n)

        for i in range(5):
            g.add_edge(HyperEdge((nodes2[i], nodes2[(i + 1) % 5]), "E"))
        g.add_edge(HyperEdge(tuple(nodes2), "P", R=0))

        draw(g, f"{OUTPUT_DIR}/test_multiple_before.png")

        p_r0_before = [e for e in g.hyperedges if e.hypertag == "P" and e.R == 0]
        self.assertEqual(len(p_r0_before), 2)

        g.apply(self.prod)

        p_r0_after = [e for e in g.hyperedges if e.hypertag == "P" and e.R == 0]
        p_r1_after = [e for e in g.hyperedges if e.hypertag == "P" and e.R == 1]

        self.assertEqual(len(p_r0_after), 1)
        self.assertEqual(len(p_r1_after), 1)
        draw(g, f"{OUTPUT_DIR}/test_multiple_after.png")

    def test_no_match_with_similar_label(self):
        """Sprawdza, czy produkcja ignoruje krawędzie o innym labelu (np. 'Q') mimo 5 węzłów"""
        g = make_graph()
        p_edge = [e for e in g.hyperedges if e.hypertag == "P"][0]
        g.remove_edge(p_edge)
        g.add_edge(HyperEdge(p_edge.nodes, "Q", R=0))
        draw(g, f"{OUTPUT_DIR}/test_no_match_with_similar_label.png")

        self.assertFalse(self.prod.can_apply(g))

    def test_preserves_boundary_conditions(self):
        """Sprawdza, czy produkcja zmienia R, ale zachowuje wartości B na krawędziach"""
        g = make_graph()
        original_b_values = {e: e.B for e in g.hyperedges if e.hypertag == "E"}

        g.apply(self.prod)

        for e in g.hyperedges:
            if e.hypertag == "E":
                self.assertEqual(e.B, original_b_values[e], "Wartości B nie powinny ulec zmianie")

    def test_number_of_vertices(self):
        """Sprawdza ilość wierzchołków po aplikacji P6"""
        g = make_graph()
        vertices_before = len(g.nodes)
        g.apply(self.prod)
        vertices_after = len(g.nodes)

        self.assertEqual(vertices_after, vertices_before,
                         "Ilość wierzchołków po produkcji powinna być taka, jak przed produkcją")


if __name__ == '__main__':
    unittest.main()
