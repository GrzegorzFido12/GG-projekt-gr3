import math
import os
import unittest
from productions.p10 import P10
from graph_model import Graph, Node, HyperEdge
from visualization import draw

VIS_DIR = "visualizations/p10_visualizations"
os.makedirs(VIS_DIR, exist_ok=True)


def create_hexagon_with_edges(shift_x=0, shift_y=0, radius=10, label_prefix="", s_R=1, e_R=0):
    """
    Tworzy heksagon wraz z krawędziami brzegowymi.

    Args:
        s_R: atrybut R dla środka (S). Dla P10 musi być 1.
        e_R: atrybut R dla krawędzi (E). Dla P10 musi być 0.
    """
    g = Graph()
    nodes = []

    # Wierzchołki
    for i in range(6):
        angle = 2 * math.pi * i / 6
        x = shift_x + radius * math.cos(angle)
        y = shift_y + radius * math.sin(angle)
        nodes.append(Node(x, y, f"{label_prefix}v{i}"))

    for n in nodes:
        g.add_node(n)

    # Wnętrze (S)
    g.add_edge(HyperEdge(tuple(nodes), "S", R=s_R))

    # Krawędzie (E)
    for i in range(6):
        u = nodes[i]
        v = nodes[(i + 1) % 6]
        g.add_edge(HyperEdge((u, v), "E", boundary=True, R=e_R, B=1))

    return g


class TestP10(unittest.TestCase):

    def viz(self, graph, step_name):
        test_method_name = self._testMethodName
        filename = f"{VIS_DIR}/{test_method_name}_{step_name}.png"
        draw(graph, filename)

    def test_apply_isomorphic(self):
        """Test standardowy: S(R=1) + E(R=0) -> E(R=1)."""
        g = create_hexagon_with_edges(s_R=1, e_R=0)
        self.viz(g, "before")

        prod = P10()
        self.assertTrue(prod.can_apply(g))

        result = g.apply(prod)
        self.viz(g, "after")

        self.assertEqual(result, 1)

        # Sprawdzenie czy wszystkie krawędzie E mają R=1
        edges = [e for e in g.hyperedges if e.hypertag == "E"]
        self.assertEqual(len(edges), 6)
        for e in edges:
            self.assertEqual(e.R, 1)

        # S powinno zostać bez zmian (R=1)
        s_edge = next(e for e in g.hyperedges if e.hypertag == "S")
        self.assertEqual(s_edge.R, 1)

    def test_apply_unmarked_S(self):
        """Test negatywny: Jeśli S ma R=0, nie oznaczamy krawędzi."""
        g = create_hexagon_with_edges(s_R=0, e_R=0)
        self.viz(g, "before")

        prod = P10()
        self.assertFalse(prod.can_apply(g))

        result = g.apply(prod)
        self.viz(g, "after")
        self.assertEqual(result, 0)

        # Krawędzie powinny pozostać R=0
        edges = [e for e in g.hyperedges if e.hypertag == "E"]
        for e in edges:
            self.assertEqual(e.R, 0)

    def test_apply_edges_already_marked(self):
        """Test negatywny: Jeśli krawędzie już mają R=1, nic nie robimy."""
        g = create_hexagon_with_edges(s_R=1, e_R=1)
        self.viz(g, "before")

        prod = P10()
        # W zależności od implementacji can_apply:
        # Jeśli sprawdza "czy istnieje choć jedna krawędź R=0", to tutaj zwróci False.
        self.assertFalse(prod.can_apply(g))

        g.apply(prod)
        self.viz(g, "after")

    def test_partial_marking(self):
        """
        Test sytuacji mieszanej: S(R=1), ale część krawędzi już oznaczona (R=1), część nie (R=0).
        Produkcja powinna oznaczyć te brakujące.
        """
        g = create_hexagon_with_edges(s_R=1, e_R=0)

        # Ręcznie zmieniamy R na 1 dla 3 krawędzi
        edges = [e for e in g.hyperedges if e.hypertag == "E"]
        for i in range(3):
            g.remove_edge(edges[i])
            g.add_edge(HyperEdge(edges[i].nodes, "E", boundary=True, R=1, B=1))

        self.viz(g, "before")

        prod = P10()
        self.assertTrue(prod.can_apply(g))
        g.apply(prod)
        self.viz(g, "after")

        # Teraz wszystkie powinny być 1
        all_edges = [e for e in g.hyperedges if e.hypertag == "E"]
        for e in all_edges:
            self.assertEqual(e.R, 1)

    def test_two_hexagons_context(self):
        """
        Dwa heksagony:
        A: S=1, E=0 (gotowy do P10)
        B: S=0, E=0 (niegotowy)
        """
        g = create_hexagon_with_edges(shift_x=-15, label_prefix="A_", s_R=1, e_R=0)
        g_right = create_hexagon_with_edges(shift_x=15, label_prefix="B_", s_R=0, e_R=0)

        for n in g_right.nodes: g.add_node(n)
        for e in g_right.hyperedges: g.add_edge(e)

        self.viz(g, "before")

        prod = P10()
        self.assertTrue(prod.can_apply(g))
        g.apply(prod)
        self.viz(g, "after")

        # Krawędzie A powinny zmienić się na 1
        edges_A = [e for e in g.hyperedges if e.hypertag == "E" and "A_" in e.nodes[0].label]
        for e in edges_A:
            self.assertEqual(e.R, 1, "Krawędzie heksagonu A powinny zostać oznaczone")

        # Krawędzie B powinny pozostać 0
        edges_B = [e for e in g.hyperedges if e.hypertag == "E" and "B_" in e.nodes[0].label]
        for e in edges_B:
            self.assertEqual(e.R, 0, "Krawędzie heksagonu B nie powinny być ruszane")

    def test_wrong_label_S(self):
        """
        Test negatywny: Sprawdza kryterium 'graf z niepoprawną etykietą'.
        Jeśli centralny element ma etykietę inną niż 'S' (np. 'Q'), produkcja nie powinna ruszyć.
        """
        # Tworzymy heksagon, ale zmieniamy etykietę środka na 'Q'
        g = create_hexagon_with_edges(s_R=1, e_R=0)

        # Ręczna podmiana etykiety S -> Q
        s_edge = next(e for e in g.hyperedges if e.hypertag == "S")
        g.remove_edge(s_edge)
        g.add_edge(HyperEdge(s_edge.nodes, "Q", R=1))

        self.viz(g, "before")

        prod = P10()
        # Produkcja nie powinna znaleźć pasującego 'S'
        self.assertFalse(prod.can_apply(g))

        g.apply(prod)
        self.viz(g, "after")

        # Upewniamy się, że krawędzie E nadal mają R=0
        edges = [e for e in g.hyperedges if e.hypertag == "E"]
        for e in edges:
            self.assertEqual(e.R, 0)

    def test_missing_boundary_edge(self):
        """
        Test ścisły (zgodny z prezentacją): Graf niepoprawny (brak jednej krawędzi).
        Produkcja NIE powinna się wykonać, ponieważ graf nie jest izomorficzny z lewą stroną (brak krawędzi).
        """
        g = create_hexagon_with_edges(s_R=1, e_R=0)

        # Usuwamy jedną krawędź brzegową (E)
        e_to_remove = next(e for e in g.hyperedges if e.hypertag == "E")
        g.remove_edge(e_to_remove)

        self.viz(g, "before")

        prod = P10()

        # Oczekujemy False - produkcja odrzuca niekompletny graf
        # Wcześniej było assertTrue, teraz zmieniamy na assertFalse
        self.assertFalse(prod.can_apply(g))

        # Próba aplikacji powinna nie wprowadzić zmian (lub zwrócić błąd/0)
        res = g.apply(prod)
        self.viz(g, "after")

        # Sprawdzamy, czy graf pozostał nienaruszony (krawędzie nadal mają R=0)
        remaining_edges = [e for e in g.hyperedges if e.hypertag == "E"]
        for e in remaining_edges:
            self.assertEqual(e.R, 0, "Produkcja nie powinna zmieniać uszkodzonego grafu")

    def test_disjoint_edge_topology(self):
        """
        Test topologii: Sprawdza, czy produkcja nie oznacza krawędzi, która fizycznie
        jest blisko, ma etykietę E i R=0, ale nie należy do węzłów heksagonu S.
        """
        g = create_hexagon_with_edges(s_R=1, e_R=0)

        # Dodajemy "obcą" krawędź E, która używa zupełnie nowych węzłów
        # (symulacja błędu w siatce lub sąsiedniego elementu)
        n1 = Node(100, 100, "x1")
        n2 = Node(101, 101, "x2")
        g.add_node(n1)
        g.add_node(n2)
        # Obca krawędź E, R=0
        foreign_edge = HyperEdge((n1, n2), "E", boundary=True, R=0, B=1)
        g.add_edge(foreign_edge)

        self.viz(g, "before")

        prod = P10()
        self.assertTrue(prod.can_apply(g))  # Aplikuje się do heksagonu
        g.apply(prod)
        self.viz(g, "after")

        # Sprawdzamy: krawędzie heksagonu mają R=1
        hex_edges = [e for e in g.hyperedges if e.hypertag == "E" and e.nodes[0] != n1]
        for e in hex_edges:
            self.assertEqual(e.R, 1)

        # Sprawdzamy: obca krawędź nadal ma R=0 (bo nie zawiera się w węzłach S)
        # Implementacja p10.py używa `issubset`, więc to powinno zadziałać poprawnie.
        checked_foreign_edge = next(e for e in g.hyperedges if e.nodes[0] == n1)
        self.assertEqual(checked_foreign_edge.R, 0)

    def test_preserves_B_attribute(self):
        """
        Test braku skutków ubocznych:
        Sprawdza, czy produkcja zmieniając R=1, nie psuje atrybutu B (Boundary).
        Symulujemy heksagon, gdzie 3 krawędzie są na brzegu (B=1), a 3 wewnątrz (B=0).
        """
        g = create_hexagon_with_edges(s_R=1, e_R=0)

        # Modyfikujemy B dla połowy krawędzi
        edges = [e for e in g.hyperedges if e.hypertag == "E"]
        for i, edge in enumerate(edges):
            if i % 2 == 0:
                # Podmieniamy na krawędź z B=0
                g.remove_edge(edge)
                g.add_edge(HyperEdge(edge.nodes, "E", boundary=False, R=0, B=0))
            # Pozostałe (nieparzyste) mają domyślne B=1 z create_hexagon_with_edges

        self.viz(g, "before")

        prod = P10()
        g.apply(prod)
        self.viz(g, "after")

        # Sprawdzamy wyniki
        for i, edge in enumerate(g.hyperedges):
            if edge.hypertag == "E":
                self.assertEqual(edge.R, 1, "R powinno być zmienione na 1")
                # Sprawdzamy czy B zostało zachowane
                expected_B = 0 if (i % 2 == 0) else 1
                # Uwaga: kolejność w hyperedges może być inna niż przy tworzeniu,
                # więc lepiej sprawdzać konkretne instancje lub logikę opartą na węzłach.
                # W tym prostym przypadku (jedna operacja) kolejność zazwyczaj się zachowuje,
                # ale bezpieczniej byłoby to zrobić tak:

        # Weryfikacja bardziej odporna na kolejność:
        cnt_b0 = sum(1 for e in g.hyperedges if e.hypertag == "E" and e.B == 0 and e.R == 1)
        cnt_b1 = sum(1 for e in g.hyperedges if e.hypertag == "E" and e.B == 1 and e.R == 1)

        self.assertEqual(cnt_b0, 3, "Powinny być 3 krawędzie z B=0")
        self.assertEqual(cnt_b1, 3, "Powinny być 3 krawędzie z B=1")

    def test_invalid_node_count_for_S(self):
        """
        Test ścisły: Element oznaczony jako 'S' (heksagon), ale będący geometrycznie pięciokątem.
        Wizualnie wierzchołki ułożone są na okręgu.
        Produkcja powinna odrzucić ten graf (zwrócić False), ponieważ S musi mieć 6 krawędzi.
        """
        g = Graph()
        nodes = []
        import math

        # Tworzymy 5 wierzchołków ułożonych na okręgu (prawdziwy pięciokąt)
        radius = 10
        for i in range(5):
            angle = 2 * math.pi * i / 5
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            nodes.append(Node(x, y, f"v{i}"))

        for n in nodes:
            g.add_node(n)

        # Oznaczamy go błędnie jako "S" (heksagon) mimo że to pięciokąt
        g.add_edge(HyperEdge(tuple(nodes), "S", R=1))

        # Dodajemy 5 krawędzi brzegowych
        for i in range(5):
            u, v = nodes[i], nodes[(i + 1) % 5]
            g.add_edge(HyperEdge((u, v), "E", boundary=True, R=0, B=1))

        self.viz(g, "before")

        prod = P10()

        # Oczekujemy False - produkcja widzi, że "S" ma tylko 5 krawędzi w środku
        self.assertFalse(prod.can_apply(g))

        # Aplikacja nie powinna wprowadzić zmian
        g.apply(prod)
        self.viz(g, "after")

        # Sprawdzamy czy krawędzie pozostały nienaruszone (R=0)
        for e in g.hyperedges:
            if e.hypertag == "E":
                self.assertEqual(e.R, 0)

    def test_empty_graph(self):
        """Test brzegowy: Pusty graf."""
        g = Graph()
        prod = P10()
        self.assertFalse(prod.can_apply(g))
        # Upewniamy się, że wywołanie apply na pustym grafie jest bezpieczne
        # (w zależności od implementacji base, może rzucić wyjątek lub zwrócić False)
        try:
            res = g.apply(prod)
            self.assertEqual(res, 0)
        except Exception as e:
            self.fail(f"Aplikacja na pustym grafie rzuciła wyjątek: {e}")

if __name__ == "__main__":
    unittest.main()