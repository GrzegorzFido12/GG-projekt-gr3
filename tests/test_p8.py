import math
import os
import unittest
import inspect
from productions.p8 import P8
from graph_model import Graph, Node, HyperEdge
from visualization import draw

# Konfiguracja katalogu na zrzuty
VIS_DIR = "visualizations/p8"
os.makedirs(VIS_DIR, exist_ok=True)


def create_broken_pentagon(shift_x=0, shift_y=0, radius=10, label_prefix="", R=1, broken=True):
    """
    Tworzy graf zawierający pięciokąt.

    Args:
        shift_x, shift_y: przesunięcie środka pentagonu
        radius: promień okręgu opisanego
        label_prefix: prefix do etykiet węzłów (np. "A_")
        R: atrybut R dla elementu P
        broken: czy krawędzie mają być podzielone (z węzłami wiszącymi)
    """
    g = Graph()
    corners = []
    hanging = []

    # Tworzenie 5 wierzchołków narożnych
    for i in range(5):
        angle = 2 * math.pi * i / 5
        x = shift_x + radius * math.cos(angle)
        y = shift_y + radius * math.sin(angle)
        corners.append(Node(x, y, f"{label_prefix}v{i}"))

    # Dodanie węzłów
    for n in corners:
        g.add_node(n)

    # Hiperkrawędź P (wnętrze)
    g.add_edge(HyperEdge(tuple(corners), "P", R=R))

    # Tworzenie krawędzi brzegowych
    for i in range(5):
        u = corners[i]
        v = corners[(i + 1) % 5]

        if broken:
            # Wersja z węzłem wiszącym (połamana)
            mx = (u.x + v.x) / 2
            my = (u.y + v.y) / 2
            h = Node(mx, my, f"{label_prefix}h{i}", hanging=True)
            g.add_node(h)
            hanging.append(h)

            g.add_edge(HyperEdge((u, h), "E", boundary=True, R=0, B=1))
            g.add_edge(HyperEdge((h, v), "E", boundary=True, R=0, B=1))
        else:
            # Wersja zwykła (niepołamana)
            g.add_edge(HyperEdge((u, v), "E", boundary=True, R=1, B=1))

    return g


class TestP8(unittest.TestCase):

    def viz(self, graph, step_name):
        """Pomocnicza funkcja do wizualizacji kroków testu"""
        test_method_name = self._testMethodName
        filename = f"{VIS_DIR}/{test_method_name}_{step_name}.png"
        draw(graph, filename)

    def test_apply_isomorphic(self):
        """Test czy produkcja aplikuje się do idealnego grafu wejściowego."""
        g = create_broken_pentagon()
        self.viz(g, "before")

        prod = P8()
        self.assertTrue(prod.can_apply(g))

        result = g.apply(prod)
        self.viz(g, "after")

        self.assertEqual(result, 1)
        self.assertEqual(len(g.nodes), 11)  # 5 narożnych + 5 wiszących + 1 środek

        # Powinno być 5 nowych elementów Q
        q_edges = [e for e in g.hyperedges if e.hypertag == "Q"]
        self.assertEqual(len(q_edges), 5)
        for q in q_edges:
            self.assertEqual(q.R, 0)

    def test_apply_missing_break(self):
        """Test czy produkcja NIE aplikuje się, gdy jedna krawędź nie jest podzielona."""
        g = create_broken_pentagon()

        # Usuwamy 'złamanie' na jednym boku (h0)
        edges_to_remove = [e for e in g.hyperedges if any(n.label == "h0" for n in e.nodes)]
        for e in edges_to_remove:
            g.remove_edge(e)

        h0 = g.get_node("h0")
        g.remove_node(h0)

        # Dodajemy bezpośrednią krawędź v0-v1
        v0 = g.get_node("v0")
        v1 = g.get_node("v1")
        g.add_edge(HyperEdge((v0, v1), "E", R=0, B=1))

        self.viz(g, "before")

        prod = P8()
        self.assertFalse(prod.can_apply(g))

        # Upewniamy się, że graf się nie zmienił
        result = g.apply(prod)
        self.viz(g, "after")  # Should look same as before
        self.assertEqual(result, 0)

    def test_apply_R0(self):
        """Test czy produkcja NIE aplikuje się, gdy P ma R=0."""
        g = create_broken_pentagon(R=0)
        self.viz(g, "before")

        prod = P8()
        self.assertFalse(prod.can_apply(g))
        g.apply(prod)
        self.viz(g, "after")

    def test_center_coordinates(self):
        """Sprawdza czy nowy węzeł centralny jest w (0,0)."""
        g = create_broken_pentagon()
        prod = P8()
        g.apply(prod)
        self.viz(g, "after")

        center = [n for n in g.nodes if "center" in n.label][0]
        self.assertAlmostEqual(center.x, 0.0, places=5)
        self.assertAlmostEqual(center.y, 0.0, places=5)

    def test_apply_on_complex_graph_preserves_context(self):
        """Test osadzenia w większym grafie z szumem."""
        g = create_broken_pentagon()

        # Dodajemy "szum"
        noise_node = Node(15, 15, "noise_1")
        g.add_node(noise_node)
        v0 = g.get_node("v0")
        g.add_edge(HyperEdge((v0, noise_node), "EXT", R=0, B=0))

        self.viz(g, "before")

        prod = P8()
        result = g.apply(prod)
        self.viz(g, "after")

        self.assertEqual(result, 1)
        self.assertIsNotNone(g.get_node("noise_1"))

    def test_wrong_hypertag(self):
        """Test negatywny: Zła etykieta (Q zamiast P)."""
        g = create_broken_pentagon()
        p_edge = [e for e in g.hyperedges if e.hypertag == "P"][0]
        g.remove_edge(p_edge)
        g.add_edge(HyperEdge(p_edge.nodes, "Q", R=1))

        self.viz(g, "before")
        prod = P8()
        self.assertFalse(prod.can_apply(g))
        g.apply(prod)
        self.viz(g, "after")

    def test_missing_corner_node(self):
        """Test negatywny: Uszkodzony graf (brak wierzchołka)."""
        g = create_broken_pentagon()
        v0 = g.get_node("v0")
        edges_to_remove = [e for e in g.hyperedges if v0 in e.nodes]
        for e in edges_to_remove:
            g.remove_edge(e)
        g.remove_node(v0)

        self.viz(g, "before")
        prod = P8()
        self.assertFalse(prod.can_apply(g))
        g.apply(prod)
        self.viz(g, "after")

    def test_apply_distorted_pentagon(self):
        """
        NOWY TEST: Sprawdza działanie na nieregularnym (wykrzywionym) pięciokącie.
        Ważne dla weryfikacji, czy algorytm nie polega na idealnych współrzędnych.
        """
        g = Graph()
        # Definiujemy ręcznie "krzywe" wierzchołki
        coords = [
            (0, 10), (8, 5), (5, -8), (-5, -8), (-8, 5)
        ]
        corners = [Node(x, y, f"v{i}") for i, (x, y) in enumerate(coords)]
        for n in corners: g.add_node(n)

        hanging = []
        for i in range(5):
            u = corners[i]
            v = corners[(i + 1) % 5]
            # Węzeł wiszący nie musi być idealnie na środku geometrycznym dla topologii,
            # ale dla wizualizacji ładniej jak jest w okolicy środka
            mx = (u.x + v.x) / 2 + (1 if i % 2 == 0 else -1)  # lekkie przesunięcie
            my = (u.y + v.y) / 2
            h = Node(mx, my, f"h{i}", hanging=True)
            g.add_node(h)
            hanging.append(h)

            g.add_edge(HyperEdge((u, h), "E", boundary=True, R=0, B=1))
            g.add_edge(HyperEdge((h, v), "E", boundary=True, R=0, B=1))

        g.add_edge(HyperEdge(tuple(corners), "P", R=1))

        self.viz(g, "before")

        prod = P8()
        self.assertTrue(prod.can_apply(g))
        g.apply(prod)

        self.viz(g, "after")

        # Sprawdzamy czy powstało 5 elementów Q
        self.assertEqual(len([e for e in g.hyperedges if e.hypertag == "Q"]), 5)

    def test_two_pentagons_one_ready(self):
        """
        NOWY TEST: Dwa pięciokąty obok siebie.
        Lewy (A) - gotowy do podziału (R=1, wszystkie boki połamane).
        Prawy (B) - niegotowy (R=1, ale jeden bok ciągły).
        Wynik: Tylko lewy powinien się podzielić.
        """
        # Tworzymy lewy pentagon (gotowy)
        g_left = create_broken_pentagon(shift_x=-15, label_prefix="L_", R=1, broken=True)

        # Tworzymy prawy pentagon (niegotowy - broken=False tworzy ciągłe krawędzie)
        # Uwaga: create_broken_pentagon z broken=False tworzy pentagon bez węzłów wiszących.
        # Żeby test był ciekawszy, dodajmy mu 4 węzły wiszące ręcznie, a jeden zostawmy ciągły.
        # Ale najprościej użyć broken=True i "naprawić" jeden bok.
        g_right = create_broken_pentagon(shift_x=15, label_prefix="R_", R=1, broken=True)

        # Łączymy grafy
        for n in g_left.nodes: g_right.add_node(n)
        for e in g_left.hyperedges: g_right.add_edge(e)
        g = g_right  # teraz g zawiera oba

        # Psujemy jeden bok w prawym pentagonie (R_)
        # Usuwamy h0 i zastępujemy krawędzią v0-v1
        edges_to_remove = [e for e in g.hyperedges if any(n.label == "R_h0" for n in e.nodes)]
        for e in edges_to_remove: g.remove_edge(e)
        g.remove_node(g.get_node("R_h0"))

        r_v0 = g.get_node("R_v0")
        r_v1 = g.get_node("R_v1")
        g.add_edge(HyperEdge((r_v0, r_v1), "E", boundary=True, R=0, B=1))

        self.viz(g, "before")

        prod = P8()

        # Powinien znaleźć dopasowanie (dla lewego)
        self.assertTrue(prod.can_apply(g))

        # Aplikujemy raz
        changes = g.apply(prod)
        self.assertEqual(changes, 1)

        self.viz(g, "after")

        # Weryfikacja:
        # Lewy pentagon (L_P) powinien zniknąć (zastąpiony przez Q)
        left_p = [e for e in g.hyperedges if e.hypertag == "P" and any("L_" in n.label for n in e.nodes)]
        self.assertEqual(len(left_p), 0)

        # Prawy pentagon (R_P) powinien zostać nienaruszony
        right_p = [e for e in g.hyperedges if e.hypertag == "P" and any("R_" in n.label for n in e.nodes)]
        self.assertEqual(len(right_p), 1)


if __name__ == "__main__":
    unittest.main()