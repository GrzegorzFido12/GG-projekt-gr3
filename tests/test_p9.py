import math
import os
import unittest
from productions.p9 import P9
from graph_model import Graph, Node, HyperEdge
from visualization import draw

# Konfiguracja katalogu na zrzuty
VIS_DIR = "visualizations/p9_visualisations"
os.makedirs(VIS_DIR, exist_ok=True)


def create_hexagon(shift_x=0, shift_y=0, radius=10, label_prefix="", R=0):
    """
    Tworzy graf zawierający heksagon:
    1. 6 wierzchołków
    2. Centralną hiperkrawędź S
    3. 6 krawędzi obwodowych E (niezbędnych do poprawnego dopasowania produkcji P9)

    Args:
        shift_x, shift_y: przesunięcie środka
        radius: promień
        label_prefix: prefix etykiet
        R: atrybut R dla elementu S
    """
    g = Graph()
    nodes = []

    # Tworzenie 6 wierzchołków
    for i in range(6):
        angle = 2 * math.pi * i / 6
        x = shift_x + radius * math.cos(angle)
        y = shift_y + radius * math.sin(angle)
        nodes.append(Node(x, y, f"{label_prefix}v{i}"))

    for n in nodes:
        g.add_node(n)

    # Hiperkrawędź S (wnętrze heksagonu)
    g.add_edge(HyperEdge(tuple(nodes), "S", R=R))

    # Krawędzie obwodowe E (niezbędne dla topologii heksagonu w P9)
    for i in range(6):
        u = nodes[i]
        v = nodes[(i + 1) % 6]  # Połączenie cykliczne
        # Atrybuty R i B dla krawędzi E są dowolne z punktu widzenia LHS P9,
        # ale ustawiamy standardowe wartości.
        g.add_edge(HyperEdge((u, v), "E", boundary=True, R=0, B=1))

    return g


class TestP9(unittest.TestCase):

    def viz(self, graph, step_name):
        """Pomocnicza funkcja do wizualizacji"""
        test_method_name = self._testMethodName
        filename = f"{VIS_DIR}/{test_method_name}_{step_name}.png"
        draw(graph, filename)

    def test_apply_isomorphic(self):
        """Test czy produkcja aplikuje się do pełnego heksagonu (S + krawędzie E) z R=0."""
        g = create_hexagon(R=0)
        self.viz(g, "before")

        prod = P9()
        # Teraz can_apply sprawdza również obecność krawędzi E
        self.assertTrue(prod.can_apply(g), "Produkcja powinna zaakceptować kompletny heksagon")

        result = g.apply(prod)
        self.viz(g, "after")

        self.assertEqual(result, 1)

        # Sprawdzenie czy R dla S zmieniło się na 1
        s_edge = next(e for e in g.hyperedges if e.hypertag == "S")
        self.assertEqual(s_edge.R, 1)

    def test_apply_missing_boundary_edges(self):
        """
        Sprawdza, czy produkcja ODRZUCA graf, który ma S, ale brakuje mu krawędzi E.
        """
        g = create_hexagon(R=0)

        # Usuwamy wszystkie krawędzie E
        edges_to_remove = [e for e in g.hyperedges if e.hypertag == "E"]
        for e in edges_to_remove:
            g.remove_edge(e)

        self.viz(g, "before")

        prod = P9()
        self.assertFalse(prod.can_apply(g), "Produkcja nie powinna aplikować się bez krawędzi obwodowych E")

        result = g.apply(prod)
        self.viz(g, "after")
        self.assertEqual(result, 0)

    def test_apply_R1(self):
        """Test czy produkcja NIE aplikuje się, gdy S ma już R=1."""
        g = create_hexagon(R=1)
        self.viz(g, "before")

        prod = P9()
        self.assertFalse(prod.can_apply(g))

        result = g.apply(prod)
        self.viz(g, "after")
        self.assertEqual(result, 0)

    def test_wrong_hypertag(self):
        """Test negatywny: Zła etykieta (P zamiast S)."""
        g = create_hexagon(R=0)

        # Podmieniamy S na P
        s_edge = [e for e in g.hyperedges if e.hypertag == "S"][0]
        g.remove_edge(s_edge)
        g.add_edge(HyperEdge(s_edge.nodes, "P", R=0))

        self.viz(g, "before")
        prod = P9()
        self.assertFalse(prod.can_apply(g))
        g.apply(prod)
        self.viz(g, "after")

    def test_two_hexagons_one_ready(self):
        """
        Dwa heksagony: jeden z R=0 (gotowy), drugi z R=1 (już oznaczony).
        Produkcja powinna zmienić tylko ten pierwszy.
        """
        # Lewy - gotowy (R=0)
        g = create_hexagon(shift_x=-15, label_prefix="L_", R=0)

        # Prawy - zajęty (R=1)
        g_right = create_hexagon(shift_x=15, label_prefix="R_", R=1)

        # Scalanie grafów
        for n in g_right.nodes: g.add_node(n)
        for e in g_right.hyperedges: g.add_edge(e)

        self.viz(g, "before")

        prod = P9()
        self.assertTrue(prod.can_apply(g))

        g.apply(prod)
        self.viz(g, "after")

        # Weryfikacja
        # POPRAWKA: Dodano warunek 'e.hypertag == "S"', aby nie pobrało krawędzi "E" (która ma R=0)
        left_s = next(e for e in g.hyperedges if e.hypertag == "S" and "L_v0" in [n.label for n in e.nodes])
        right_s = next(e for e in g.hyperedges if e.hypertag == "S" and "R_v0" in [n.label for n in e.nodes])

        self.assertEqual(left_s.R, 1, "Lewy powinien zostać oznaczony (zmieniony na 1)")
        self.assertEqual(right_s.R, 1, "Prawy powinien pozostać 1")

    def test_apply_on_complex_graph_preserves_context(self):
        """Test osadzenia w większym grafie."""
        g = create_hexagon(R=0)

        # Dodajemy dodatkowy węzeł i krawędź
        extra = Node(20, 20, "extra")
        g.add_node(extra)
        v0 = g.get_node("v0")
        g.add_edge(HyperEdge((v0, extra), "CONN", R=0))

        self.viz(g, "before")
        prod = P9()
        g.apply(prod)
        self.viz(g, "after")

        self.assertIsNotNone(g.get_node("extra"))
        s_edge = next(e for e in g.hyperedges if e.hypertag == "S")
        self.assertEqual(s_edge.R, 1)


if __name__ == "__main__":
    unittest.main()