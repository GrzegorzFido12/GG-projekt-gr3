from production_base import Production
from graph_model import Graph, Node, HyperEdge
from typing import Optional


@Production.register
class P8(Production):
    """
    Produkcja P8 - Dzieli element pięciokątny oznaczony do podziału (R=1),
    jeśli wszystkie jego krawędzie brzegowe są już podzielone (posiadają węzły wiszące).

    Lewa strona:
    - Element pięciokątny P z atrybutem R=1.
    - 5 wierzchołków narożnych.
    - 5 węzłów wiszących na krawędziach (oznacza to, że krawędzie są 'broken').

    Prawa strona:
    - Podział pięciokąta na 5 mniejszych czworokątów (Q).
    - Dodanie węzła centralnego.
    - Połączenie węzła centralnego z węzłami wiszącymi.
    - Nowe elementy Q mają R=0.
    """

    def get_left_side(self) -> Graph:
        """
        Zwraca przykładowy graf lewej strony produkcji.
        """
        g = Graph()
        # Tworzymy 5 wierzchołków narożnych i 5 wiszących
        corners = [Node(0, 0, f"v{i}") for i in range(5)]
        hanging = [Node(0, 0, f"h{i}") for i in range(5)]

        for n in corners + hanging:
            g.add_node(n)

        # Hiperkrawędź P reprezentująca wnętrze pięciokąta
        g.add_edge(HyperEdge(tuple(corners), "P", R=1))

        # Krawędzie brzegowe (podzielone)
        for i in range(5):
            u = corners[i]
            v = corners[(i + 1) % 5]
            h = hanging[i]
            # Krawędzie E łączące narożniki z wiszącymi
            g.add_edge(HyperEdge((u, h), "E", boundary=True))
            g.add_edge(HyperEdge((h, v), "E", boundary=True))

        return g

    def find_match(self, graph: Graph) -> Optional[Graph]:
        for p_edge in graph.hyperedges:
            if p_edge.hypertag != "P" or p_edge.R != 1 or len(p_edge.nodes) != 5:
                continue

            corners = list(p_edge.nodes)
            hanging_nodes = []
            matched_edges = [p_edge]

            for i in range(5):
                u = corners[i]
                v = corners[(i + 1) % 5]
                h = None

                for e1 in graph.hyperedges:
                    if e1.hypertag == "E" and u in e1.nodes:
                        h_cand = e1.nodes[0] if e1.nodes[1] == u else e1.nodes[1]
                        if h_cand in corners:
                            continue

                        for e2 in graph.hyperedges:
                            if e2.hypertag == "E" and set(e2.nodes) == {h_cand, v}:
                                h = h_cand
                                matched_edges.extend([e1, e2])
                                break
                    if h:
                        break

                if h is None:
                    break

                hanging_nodes.append(h)

            if len(hanging_nodes) != 5:
                continue

            matched = Graph()
            for n in corners + hanging_nodes:
                matched.add_node(n)
            for e in matched_edges:
                matched.add_edge(e)

            return matched

        return None

    def can_apply(self, graph: Graph) -> bool:
        return self.find_match(graph) is not None

    def get_right_side(self, matched: Graph, level: int) -> Graph:
        result = Graph()

        # 1. PRZEPISZ CAŁY GRAF
        for n in matched.nodes:
            result.add_node(n)
        for e in matched.hyperedges:
            if e.hypertag == "P":
                continue
            result.add_edge(e)

        # 2. znajdź P
        p_edge = next(e for e in matched.hyperedges if e.hypertag == "P")

        corners = list(p_edge.nodes)

        # 3. oznacz jako przetworzone
        p_edge.R = 0

        hanging_nodes = []
        for i in range(5):
            u = corners[i]
            v = corners[(i + 1) % 5]

            found_h = None
            for n in matched.nodes:
                if n in corners: continue

                connected_u = False
                connected_v = False
                for e in matched.hyperedges:
                    if e.hypertag == "E" and n in e.nodes:
                        if u in e.nodes: connected_u = True
                        if v in e.nodes: connected_v = True

                if connected_u and connected_v:
                    found_h = n
                    break
            hanging_nodes.append(found_h)

        # Dodaj węzły
        for n in corners + hanging_nodes:
            result.add_node(n)

        # 2. Oblicz środek
        avg_x = sum(n.x for n in corners) / 5
        avg_y = sum(n.y for n in corners) / 5
        center = Node(avg_x, avg_y, f"center_p8_{corners[0].label}")
        result.add_node(center)

        for i in range(5):
            h = hanging_nodes[i]
            h_prev = hanging_nodes[(i - 1) % 5]

            result.add_edge(HyperEdge((center, h), "E", R=0, B=0))
            result.add_edge(HyperEdge((corners[i], h, center, h_prev), "Q", R=0))

        return result