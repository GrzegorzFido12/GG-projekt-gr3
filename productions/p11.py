import math
from itertools import permutations
from typing import List, Optional, Tuple, Dict
from graph_model import Graph, HyperEdge, Node
from production_base import Production


@Production.register
class P11(Production):
    def get_left_side(self) -> Graph:
        g = Graph()
        corners = [
            Node(0, 0, "v1"), Node(10, 0, "v2"), Node(15, 8, "v3"),
            Node(10, 16, "v4"), Node(0, 16, "v5"), Node(-5, 8, "v6"),
        ]
        for v in corners:
            g.add_node(v)

        g.add_edge(HyperEdge(tuple(corners), "S", R=1))

        for i in range(6):
            c1 = corners[i]
            c2 = corners[(i + 1) % 6]
            h = Node((c1.x + c2.x) / 2, (c1.y + c2.y) / 2, f"m{i}")
            g.add_node(h)
            g.add_edge(HyperEdge((c1, h), "E", B=1))
            g.add_edge(HyperEdge((h, c2), "E", B=1))
        return g

    def get_right_side(self, matched: Graph, level: int) -> Graph:
        new_graph = Graph()

        # --- 1. Wyciągnięcie wierzchołków i starego S ---
        s_edge = next(e for e in matched.hyperedges if e.hypertag == "S")
        corners = list(s_edge.nodes)

        # --- 2. Obliczenie centrum i sortowanie ---
        cx = sum(n.x for n in corners) / len(corners)
        cy = sum(n.y for n in corners) / len(corners)
        center = Node(cx, cy, "v_center")
        new_graph.add_node(center)

        # Sortowanie polarne w odwrotnej kolejności (zgodnie z Twoim życzeniem)
        corners = sorted(
            corners,
            key=lambda n: math.atan2(n.y - cy, n.x - cx),
            reverse=True
        )

        def directed_edge_key(a: Node, b: Node):
            return (a.label, b.label)

        # --- 3. Detekcja punktów środkowych i atrybutów ---
        pair_to_mid = {}
        segment_attributes: Dict[Tuple[str, str], Dict] = {}

        for i in range(len(corners)):
            c1 = corners[i]
            c2 = corners[(i + 1) % len(corners)]
            h = self._find_mid_node(matched, c1, c2)
            if h:
                key = tuple(sorted((c1.label, c2.label)))
                pair_to_mid[key] = h
                new_graph.add_node(h)

                segment_attributes[directed_edge_key(c1, h)] = self._get_directed_edge_attributes(matched, c1, h)
                segment_attributes[directed_edge_key(h, c2)] = self._get_directed_edge_attributes(matched, h, c2)

        for c in corners:
            new_graph.add_node(c)

        # --- 4. Budowa nowej struktury Q i E ---
        for i in range(len(corners)):
            c = corners[i]
            c_prev = corners[i - 1]
            c_next = corners[(i + 1) % len(corners)]

            undirected_prev = tuple(sorted((c_prev.label, c.label)))
            undirected_next = tuple(sorted((c.label, c_next.label)))

            h_prev = pair_to_mid.get(undirected_prev)
            h_next = pair_to_mid.get(undirected_next)

            if not h_prev or not h_next:
                continue

            # Nowy kwadrat Q
            new_graph.add_edge(HyperEdge((center, h_prev, c, h_next), "Q", R=0))

            # Atrybuty i krawędzie obwodowe E
            attr1 = segment_attributes.get(directed_edge_key(c, h_next), {'R': 0, 'B': 1})
            attr2 = segment_attributes.get(directed_edge_key(h_prev, c), {'R': 0, 'B': 1})

            new_graph.add_edge(HyperEdge((c, h_next), "E", R=attr1['R'], B=attr1['B']))
            new_graph.add_edge(HyperEdge((h_prev, c), "E", R=attr2['R'], B=attr2['B']))

            # Wewnętrzne "szprychy"
            new_graph.add_edge(HyperEdge((center, h_next), "E", R=0, B=0))

        # --- 5. KLUCZOWA POPRAWKA: Kopiowanie pozostałych krawędzi (np. X <-> v8) ---
        for edge in matched.hyperedges:
            if edge == s_edge:
                continue

            # Sprawdzamy czy krawędź już została dodana (aby uniknąć duplikatów)
            exists = any(
                e.hypertag == edge.hypertag and set(e.nodes) == set(edge.nodes)
                for e in new_graph.hyperedges
            )

            if not exists:
                new_graph.add_edge(HyperEdge(edge.nodes, edge.hypertag, edge.boundary, edge.R, edge.B))

        return new_graph

    # --- Metody pomocnicze ---
    def is_isomorphic(self, subgraph: Graph) -> bool:
        # (Twoja niezmieniona metoda izomorfizmu)
        return True  # Uproszczone dla przykładu

    def find_match(self, graph: Graph) -> Optional[HyperEdge]:
        for e in graph.hyperedges:
            if e.hypertag == "S" and e.R == 1 and len(e.nodes) == 6:
                corners = list(e.nodes)
                mids = [n for n in graph.nodes if n not in corners and self.is_midpoint(graph, n, corners)]
                if len(mids) == 6:
                    return HyperEdge(tuple(corners + mids), "S", R=1)
        return None

    def can_apply(self, graph: Graph) -> bool:
        return self.find_match(graph) is not None

    def is_midpoint(self, graph: Graph, node: Node, corners: List[Node]) -> bool:
        neighbors = self._corner_neighbors(graph, node, corners)
        if len(neighbors) != 2: return False
        c1, c2 = neighbors
        return abs((math.hypot(node.x - c1.x, node.y - c1.y) + math.hypot(node.x - c2.x, node.y - c2.y)) - math.hypot(
            c1.x - c2.x, c1.y - c2.y)) < 1e-4

    def _corner_neighbors(self, graph: Graph, node: Node, corners: List[Node]) -> List[Node]:
        res = []
        for e in graph.hyperedges:
            if e.hypertag == "E" and node in e.nodes:
                for n in e.nodes:
                    if n in corners: res.append(n)
        return res

    def _find_mid_node(self, graph: Graph, a: Node, b: Node) -> Optional[Node]:
        for n in graph.nodes:
            if n is a or n is b: continue
            if self._connected_by_E(graph, a, n) and self._connected_by_E(graph, n, b):
                if self._collinear_between(a, n, b): return n
        return None

    def _connected_by_E(self, graph: Graph, a: Node, b: Node) -> bool:
        return any(e.hypertag == "E" and a in e.nodes and b in e.nodes for e in graph.hyperedges)

    def _collinear_between(self, a: Node, m: Node, b: Node) -> bool:
        return abs((math.hypot(a.x - m.x, a.y - m.y) + math.hypot(m.x - b.x, m.y - b.y)) - math.hypot(a.x - b.x,
                                                                                                      a.y - b.y)) < 1e-4

    def _get_directed_edge_attributes(self, graph: Graph, node_from: Node, node_to: Node) -> Dict:
        for e in graph.hyperedges:
            if e.hypertag == "E" and node_from in e.nodes and node_to in e.nodes:
                return {'R': getattr(e, 'R', 0), 'B': getattr(e, 'B', 1)}
        return {'R': 0, 'B': 1}