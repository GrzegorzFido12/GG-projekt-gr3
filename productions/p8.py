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
        hanging = [Node(0, 0, f"h{i}", hanging=True) for i in range(5)]

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

    def find_match(self, graph: Graph) -> Optional[HyperEdge]:
        """
        Znajduje element P oznaczony do podziału, którego wszystkie krawędzie są podzielone.
        """
        for p_edge in graph.hyperedges:
            # Szukamy hiperkrawędzi P, R=1, 5 wierzchołków
            if p_edge.hypertag == "P" and p_edge.R == 1 and len(p_edge.nodes) == 5:
                corners = list(p_edge.nodes)
                hanging_nodes = []
                found_all_hanging = True

                # Sprawdzamy każdy bok pięciokąta
                for i in range(5):
                    u = corners[i]
                    v = corners[(i + 1) % 5]

                    # Szukamy węzła wiszącego h pomiędzy u i v
                    h_found = None

                    # Znajdź sąsiadów u połączonych krawędzią E
                    neighbors_u = set()
                    for edge in graph.hyperedges:
                        if edge.hypertag == "E" and u in edge.nodes:
                            other = (
                                edge.nodes[1] if edge.nodes[0] == u else edge.nodes[0]
                            )
                            neighbors_u.add(other)

                    # Sprawdź czy któryś z sąsiadów jest odpowiednim węzłem wiszącym
                    for h_cand in neighbors_u:
                        # POPRAWKA: Węzeł wiszący nie może być wierzchołkiem narożnym
                        if h_cand == u or h_cand == v:
                            continue

                        # POPRAWKA: Wymagamy, aby węzeł miał flagę hanging (zgodnie z modelem)
                        if not h_cand.hanging:
                            continue

                        is_connected_to_v = False
                        for edge in graph.hyperedges:
                            if (
                                edge.hypertag == "E"
                                and h_cand in edge.nodes
                                and v in edge.nodes
                            ):
                                is_connected_to_v = True
                                break

                        if is_connected_to_v:
                            h_found = h_cand
                            break

                    if h_found:
                        hanging_nodes.append(h_found)
                    else:
                        found_all_hanging = False
                        break

                if found_all_hanging:
                    all_nodes = corners + hanging_nodes
                    return HyperEdge(tuple(all_nodes), "MATCH_CONTAINER", R=1)

        return None

    def can_apply(self, graph: Graph) -> bool:
        return self.find_match(graph) is not None

    def get_right_side(self, matched: Graph, level: int) -> Graph:
        result = Graph()

        # 1. Odzyskaj strukturę z podgrafu matched
        p_edge = None
        for e in matched.hyperedges:
            if e.hypertag == "P":
                p_edge = e
                break

        if not p_edge:
            return matched

        corners = list(p_edge.nodes)

        # Odzyskaj węzły wiszące w odpowiedniej kolejności
        hanging_nodes = []
        for i in range(5):
            u = corners[i]
            v = corners[(i + 1) % 5]

            found_h = None
            for n in matched.nodes:
                if n in corners:
                    continue

                connected_u = False
                connected_v = False
                for e in matched.hyperedges:
                    if e.hypertag == "E" and n in e.nodes:
                        if u in e.nodes:
                            connected_u = True
                        if v in e.nodes:
                            connected_v = True

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

        # 3. Odtwórz krawędzie i dodaj wnętrze
        for i in range(5):
            u = corners[i]
            v = corners[(i + 1) % 5]
            h = hanging_nodes[i]

            # Pobierz atrybut B z oryginalnych krawędzi
            b_val_uh = 0
            for e in matched.hyperedges:
                if set(e.nodes) == {u, h}:
                    b_val_uh = e.B
                    break

            b_val_hv = 0
            for e in matched.hyperedges:
                if set(e.nodes) == {h, v}:
                    b_val_hv = e.B
                    break

            result.add_edge(
                HyperEdge((u, h), "E", boundary=(b_val_uh == 1), R=0, B=b_val_uh)
            )
            result.add_edge(
                HyperEdge((h, v), "E", boundary=(b_val_hv == 1), R=0, B=b_val_hv)
            )

            result.add_edge(HyperEdge((center, h), "E", boundary=False, R=0, B=0))

            h_prev = hanging_nodes[(i - 1) % 5]
            result.add_edge(HyperEdge((u, h, center, h_prev), "Q", R=0))

        return result
