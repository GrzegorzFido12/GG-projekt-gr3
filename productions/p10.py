from production_base import Production
from graph_model import Graph, Node, HyperEdge
from typing import Optional


@Production.register
class P10(Production):
    """
    Produkcja P10 - Oznacza krawędzie elementu heksagonalnego do podziału.

    Wersja Ścisła (Strict):
    - Wymaga kompletnego heksagonu (dokładnie 6 krawędzi wewnątrz).
    - Jeśli brakuje krawędzi, produkcja się nie stosuje (zgodność z prezentacją).
    """

    def get_left_side(self) -> Graph:
        g = Graph()
        nodes = [Node(0, 0, f"v{i}") for i in range(1, 7)]
        for n in nodes:
            g.add_node(n)
        g.add_edge(HyperEdge(tuple(nodes), "S", R=1))
        return g

    def get_right_side(self, matched: Graph, level: int) -> Graph:
        result = Graph()

        # Kopiujemy węzły
        for node in matched.nodes:
            result.add_node(node)

        # Przepisujemy krawędzie ze zmianami
        for edge in matched.hyperedges:
            if edge.hypertag == "S":
                # S pozostaje bez zmian (R=1)
                result.add_edge(HyperEdge(edge.nodes, "S", R=1))
            elif edge.hypertag == "E":
                # Krawędzie E oznaczamy do podziału (R=1)
                # Zachowujemy atrybut B (Boundary) bez zmian
                result.add_edge(
                    HyperEdge(edge.nodes, "E", edge.boundary, R=1, B=edge.B)
                )

        return result

    def can_apply(self, graph: Graph) -> bool:
        # Szukamy kandydata: S z R=1
        s_edges = [e for e in graph.hyperedges if e.hypertag == "S" and e.R == 1]

        for s_edge in s_edges:
            s_nodes_set = set(s_edge.nodes)

            # KROK 1 (STRICT): Znajdź WSZYSTKIE krawędzie E należące do tego heksagonu
            enclosed_edges = [
                e
                for e in graph.hyperedges
                if e.hypertag == "E" and set(e.nodes).issubset(s_nodes_set)
            ]

            # Ścisłe sprawdzanie topologii: Heksagon musi mieć dokładnie 6 krawędzi.
            # Jeśli ma 5 (brakująca) lub inną liczbę, odrzucamy go (zwracamy False dla tego kandydata).
            if len(enclosed_edges) != 6:
                continue

                # KROK 2: Sprawdź czy jest sens aplikować (czy jest co zmieniać, tzn. R=0)
            for edge in enclosed_edges:
                if edge.R == 0:
                    return True
        return False

    def find_match(self, graph: Graph) -> Optional[HyperEdge]:
        s_edges = [e for e in graph.hyperedges if e.hypertag == "S" and e.R == 1]

        for s_edge in s_edges:
            s_nodes_set = set(s_edge.nodes)

            enclosed_edges = [
                e
                for e in graph.hyperedges
                if e.hypertag == "E" and set(e.nodes).issubset(s_nodes_set)
            ]

            # Tutaj również musimy być ściśli.
            # Jeśli znajdziemy S, ale jest uszkodzony (nie ma 6 krawędzi), nie zwracamy go.
            if len(enclosed_edges) != 6:
                continue

            for edge in enclosed_edges:
                if edge.R == 0:
                    # Zwracamy S - silnik graph_model.apply automatycznie
                    # pobierze wszystkie krawędzie zawarte w węzłach S.
                    return s_edge
        return None
