from typing import Optional
import math

from graph_model import Graph, Node, HyperEdge
from production_base import Production


@Production.register
class P9(Production):
    """
    Produkcja P9 - Oznacza element heksagonalny do podziału (refinement).

    Lewa strona:
    - Element heksagonalny reprezentowany przez hiperkrawędź S (z R=0).
    - Musi być otoczony przez 6 krawędzi E (tworzących obwód heksagonu).

    Prawa strona:
    - Ten sam element, ale hiperkrawędź S ma ustawiony atrybut R=1.
    """

    def get_left_side(self) -> Graph:
        g = Graph()
        # Tworzymy 6 wierzchołków
        nodes = [Node(0, 0, f"v{i}") for i in range(6)]
        for n in nodes:
            g.add_node(n)

        # Centralna hiperkrawędź S
        g.add_edge(HyperEdge(tuple(nodes), "S", R=0))

        # Krawędzie obwodowe E (niezbędne dla kontekstu lewej strony)
        # Zakładamy kolejność wierzchołków po obwodzie
        for i in range(6):
            u = nodes[i]
            v = nodes[(i + 1) % 6]
            g.add_edge(HyperEdge((u, v), "E", boundary=True))  # R i B są dowolne w LHS

        return g

    def get_right_side(self, matched: Graph, level: int) -> Graph:
        result = Graph()

        # Przepisujemy wszystkie węzły
        for node in matched.nodes:
            result.add_node(node)

        # Przetwarzamy krawędzie
        for edge in matched.hyperedges:
            if edge.hypertag == "S" and edge.R == 0:
                # To jest nasza krawędź S, którą zmieniamy -> R=1
                result.add_edge(
                    HyperEdge(edge.nodes, "S", edge.boundary, R=1, B=edge.B)
                )
            else:
                # Krawędzie E (i ewentualne inne) przepisujemy bez zmian
                result.add_edge(
                    HyperEdge(edge.nodes, edge.hypertag, edge.boundary, edge.R, edge.B)
                )

        return result

    def _check_topology(self, graph: Graph, s_edge: HyperEdge) -> bool:
        """
        Pomocnicza metoda sprawdzająca, czy krawędź S jest poprawnym heksagonem
        otoczonym przez krawędzie E.
        """
        # 1. Sprawdzenie atrybutów S
        if s_edge.hypertag != "S" or s_edge.R != 0:
            return False

        # 2. Sprawdzenie liczby wierzchołków
        if len(s_edge.nodes) != 6:
            return False

        # 3. Sortowanie wierzchołków zgodnie z obwodem (polarne)
        raw_nodes = list(s_edge.nodes)

        # Obliczamy środek geometryczny heksagonu
        avg_x = sum(n.x for n in raw_nodes) / 6.0
        avg_y = sum(n.y for n in raw_nodes) / 6.0

        # Sortujemy wierzchołki według kąta (tutaj reverse=True dla zgodności z Twoją prośbą)
        nodes = sorted(
            raw_nodes,
            key=lambda n: math.atan2(n.y - avg_y, n.x - avg_x),
            reverse=True
        )

        for i in range(6):
            u = nodes[i]
            v = nodes[(i + 1) % 6]

            edge_found = False
            for edge in graph.hyperedges:
                if edge.hypertag == "E" and set(edge.nodes) == {u, v}:
                    edge_found = True
                    break
            if not edge_found:
                return False  # Brak krawędzi E między wierzchołkami heksagonu

        return True

    def can_apply(self, graph: Graph) -> bool:
        # Przeszukujemy graf w poszukiwaniu pasującego S wraz z otoczeniem
        for edge in graph.hyperedges:
            if self._check_topology(graph, edge):
                return True
        return False

    def find_match(self, graph: Graph) -> Optional[HyperEdge]:
        # Zwracamy hiperkrawędź S, która spełnia wszystkie wymogi topologiczne
        for edge in graph.hyperedges:
            if self._check_topology(graph, edge):
                return edge
        return None

    def has_point(self, point, nodes):
        for node in nodes:
            if node.x == point.x and node.y == point.y:
                return True
        return False

    def find_match_with_point(self, graph: Graph, point):
        for edge in graph.hyperedges:
            if self._check_topology(graph, edge) and self.has_point(point, edge.nodes):
                return edge
        return None
