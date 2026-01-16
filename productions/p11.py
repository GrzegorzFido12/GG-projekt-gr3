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
            Node(0, 0, "v1"),
            Node(10, 0, "v2"),
            Node(15, 8, "v3"),
            Node(10, 16, "v4"),
            Node(0, 16, "v5"),
            Node(-5, 8, "v6"),
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

        # --- extract corners from S-edge ---
        s_edge = next(e for e in matched.hyperedges if e.hypertag == "S")
        corners = list(s_edge.nodes)

        # --- compute center ---
        cx = sum(n.x for n in corners) / len(corners)
        cy = sum(n.y for n in corners) / len(corners)

        center = Node(cx, cy, "v_center")
        new_graph.add_node(center)

        # --- angular sort ---
        corners = self._sort_angularly(corners, cx, cy)

        # --- helper for directed edge keys ---
        def directed_edge_key(a: Node, b: Node):
            return (a.label, b.label)

        # --- detect mid-edge nodes and collect edge info for each directed segment ---
        pair_to_mid = {}
        segment_attributes: Dict[Tuple[str, str], Dict] = {}  # directed (from, to) -> {R, B}

        for i in range(len(corners)):
            c1 = corners[i]
            c2 = corners[(i + 1) % len(corners)]

            h = self._find_mid_node(matched, c1, c2)
            if h:
                key = tuple(sorted((c1.label, c2.label)))
                pair_to_mid[key] = h
                new_graph.add_node(h)
                
                # Get attributes for EACH directed segment separately
                attrs_c1_h = self._get_directed_edge_attributes(matched, c1, h)
                attrs_h_c2 = self._get_directed_edge_attributes(matched, h, c2)
                
                segment_attributes[directed_edge_key(c1, h)] = attrs_c1_h
                segment_attributes[directed_edge_key(h, c2)] = attrs_h_c2

        # --- add corner nodes ---
        for c in corners:
            new_graph.add_node(c)

        # --- build new structure ---
        for i in range(len(corners)):
            c = corners[i]
            c_prev = corners[i - 1]
            c_next = corners[(i + 1) % len(corners)]

            undirected_prev = tuple(sorted((c_prev.label, c.label)))
            undirected_next = tuple(sorted((c.label, c_next.label)))
            
            h_prev = pair_to_mid.get(undirected_prev)
            h_next = pair_to_mid.get(undirected_next)

            # Guard: skip incomplete configurations
            if not h_prev or not h_next:
                continue

            # Q face with R=0
            new_graph.add_edge(
                HyperEdge((center, h_prev, c, h_next), "Q", R=0)
            )

            # Get attributes for each outgoing edge from corner c
            # Edge from h_prev to c
            attrs_h_prev_c = segment_attributes.get(directed_edge_key(h_prev, c), {'R': 0, 'B': 1})
            # Edge from c to h_next
            attrs_c_h_next = segment_attributes.get(directed_edge_key(c, h_next), {'R': 0, 'B': 1})
            
            # Create boundary edges with their specific attributes
            new_graph.add_edge(HyperEdge((c, h_next), "E", 
                                        R=attrs_c_h_next['R'], 
                                        B=attrs_c_h_next['B']))
            new_graph.add_edge(HyperEdge((h_prev, c), "E", 
                                        R=attrs_h_prev_c['R'], 
                                        B=attrs_h_prev_c['B']))

            # Internal spoke - always B=0, R=0
            new_graph.add_edge(HyperEdge((center, h_next), "E", R=0, B=0))

        return new_graph

    def is_isomorphic(self, subgraph: Graph) -> bool:
        lhs = self.get_left_side()

        if len(subgraph.nodes) != 12:
            return False

        s1 = next(e for e in lhs.hyperedges if e.hypertag == "S")
        s2 = next((e for e in subgraph.hyperedges if e.hypertag == "S"), None)
        if not s2 or s2.R != s1.R or len(s2.nodes) != 6:
            return False

        corners1 = list(s1.nodes)
        corners2 = list(s2.nodes)

        mids1 = [n for n in lhs.nodes if n not in corners1]
        mids2 = [n for n in subgraph.nodes if n not in corners2]

        if len(mids1) != 6 or len(mids2) != 6:
            return False

        for perm in permutations(corners2):
            cmap = dict(zip(corners1, perm))
            used = set()
            ok = True

            for m1 in mids1:
                n1, n2 = self._corner_neighbors(lhs, m1, corners1)
                mapped = {cmap[n1], cmap[n2]}

                found = False
                for m2 in mids2:
                    if m2 in used:
                        continue
                    if set(self._corner_neighbors(subgraph, m2, corners2)) == mapped:
                        used.add(m2)
                        found = True
                        break
                if not found:
                    ok = False
                    break

            if ok:
                return True

        return False
    
    def can_apply(self, graph: Graph) -> bool:
        return self.find_match(graph) is not None

    def find_match(self, graph: Graph) -> Optional[HyperEdge]:
        for e in graph.hyperedges:
            if e.hypertag == "S" and e.R == 1 and len(e.nodes) == 6:
                corners = list(e.nodes)
                mids = [
                    n for n in graph.nodes
                    if n not in corners and self.is_midpoint(graph, n, corners)
                ]
                if len(mids) == 6:
                    return HyperEdge(tuple(corners + mids), "S", R=1)
        return None

    def is_midpoint(self, graph: Graph, node: Node, corners: List[Node]) -> bool:
        neighbors = self._corner_neighbors(graph, node, corners)
        if len(neighbors) != 2:
            return False

        c1, c2 = neighbors
        d1 = math.hypot(node.x - c1.x, node.y - c1.y)
        d2 = math.hypot(node.x - c2.x, node.y - c2.y)
        d_full = math.hypot(c1.x - c2.x, c1.y - c2.y)

        return abs((d1 + d2) - d_full) < 1e-4

    def _corner_neighbors(self, graph: Graph, node: Node, corners: List[Node]) -> List[Node]:
        result = []
        for e in graph.hyperedges:
            if e.hypertag == "E" and node in e.nodes:
                for n in e.nodes:
                    if n in corners:
                        result.append(n)
        return result

    def _sort_angularly(self, nodes: List[Node], cx: float, cy: float) -> List[Node]:
        return sorted(nodes, key=lambda n: math.atan2(n.y - cy, n.x - cx))
    
    def _find_mid_node(self, graph: Graph, a: Node, b: Node) -> Optional[Node]:
        """
        Finds a node lying between a and b that:
        - is connected to both a and b by E-edges
        - lies geometrically on segment a--b
        """
        for n in graph.nodes:
            if n is a or n is b:
                continue

            if self._connected_by_E(graph, a, n) and self._connected_by_E(graph, n, b):
                if self._collinear_between(a, n, b):
                    return n
        return None

    def _connected_by_E(self, graph: Graph, a: Node, b: Node) -> bool:
        for e in graph.hyperedges:
            if e.hypertag == "E" and a in e.nodes and b in e.nodes:
                return True
        return False

    def _collinear_between(self, a: Node, m: Node, b: Node, eps: float = 1e-4) -> bool:
        d1 = math.hypot(a.x - m.x, a.y - m.y)
        d2 = math.hypot(m.x - b.x, m.y - b.y)
        d = math.hypot(a.x - b.x, a.y - b.y)
        return abs((d1 + d2) - d) < eps

    def _get_directed_edge_attributes(self, graph: Graph, node_from: Node, node_to: Node) -> Dict:
        """
        Extracts R and B attributes from a directed edge segment in the original graph.
        Returns a dict with 'R' and 'B' values for the specific edge from node_from to node_to.
        """
        r_flag = 0  # default
        b_flag = 1  # default boundary
        
        # Find the specific directed edge
        for e in graph.hyperedges:
            if e.hypertag == "E" and node_from in e.nodes and node_to in e.nodes:
                if hasattr(e, 'R'):
                    r_flag = e.R
                if hasattr(e, 'B'):
                    b_flag = e.B
                break  # Found the edge, use its attributes
        
        return {'R': r_flag, 'B': b_flag}
