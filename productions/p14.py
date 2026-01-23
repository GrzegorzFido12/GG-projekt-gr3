import math
from typing import List, Optional, Tuple, Dict
from graph_model import Graph, HyperEdge, Node
from production_base import Production

@Production.register
class P14(Production):

    def get_left_side(self) -> Graph:
        g = Graph()
        corners = [
            Node(10 * math.cos(2*math.pi*i/7), 10 * math.sin(2*math.pi*i/7), f"v{i}") 
            for i in range(7)
        ]
        for v in corners:
            g.add_node(v)

        g.add_edge(HyperEdge(tuple(corners), "T", R=1))

        for i in range(7):
            c1 = corners[i]
            c2 = corners[(i + 1) % 7]
            h = Node((c1.x + c2.x) / 2, (c1.y + c2.y) / 2, f"m{i}", hanging=True)
            g.add_node(h)
            g.add_edge(HyperEdge((c1, h), "E", B=1, R=1))
            g.add_edge(HyperEdge((h, c2), "E", B=1, R=1))

        return g

    def get_right_side(self, matched: Graph, level: int) -> Graph:
        new_graph = Graph()

        t_edge = next(e for e in matched.hyperedges if e.hypertag == "T")
        corners = list(t_edge.nodes)

        cx = sum(n.x for n in corners) / len(corners)
        cy = sum(n.y for n in corners) / len(corners)
        center = Node(cx, cy, "v_center")
        new_graph.add_node(center)

        corners = self._sort_angularly(corners, cx, cy)

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
                
                segment_attributes[(c1.label, h.label)] = self._get_edge_attrs(matched, c1, h)
                segment_attributes[(h.label, c2.label)] = self._get_edge_attrs(matched, h, c2)

        for n in matched.nodes:
            new_graph.add_node(n)

        for i in range(len(corners)):
            c = corners[i]
            c_prev = corners[i - 1]
            c_next = corners[(i + 1) % len(corners)]

            h_prev = pair_to_mid.get(tuple(sorted((c_prev.label, c.label))))
            h_next = pair_to_mid.get(tuple(sorted((c.label, c_next.label))))

            if not h_prev or not h_next:
                continue

            new_graph.add_edge(HyperEdge((center, h_prev, c, h_next), "Q", R=0))

            for h_node in [h_prev, h_next]:
                key = (h_node.label, c.label)
                if key in segment_attributes:
                    attrs = segment_attributes[key]
                    new_graph.add_edge(HyperEdge((h_node, c), "E", R=attrs['R'], B=attrs['B']))
                else:
                    key_rev = (c.label, h_node.label)
                    if key_rev in segment_attributes:
                        attrs = segment_attributes[key_rev]
                        new_graph.add_edge(HyperEdge((c, h_node), "E", R=attrs['R'], B=attrs['B']))

            new_graph.add_edge(HyperEdge((center, h_next), "E", R=0, B=0))

        return new_graph

    def find_match(self, graph: Graph) -> Optional[HyperEdge]:
        for e in graph.hyperedges:
            if e.hypertag == "T" and e.R == 1 and len(e.nodes) == 7:
                corners = list(e.nodes)
                mids = [
                    n for n in graph.nodes
                    if n not in corners and self._is_midpoint(graph, n, corners)
                ]
                if len(mids) == 7:
                    return HyperEdge(tuple(corners + mids), "T", R=1)
        return None

    def can_apply(self, graph: Graph) -> bool:
        return self.find_match(graph) is not None

    def _is_midpoint(self, graph: Graph, node: Node, corners: List[Node]) -> bool:
        neighbors = []
        for e in graph.hyperedges:
            if e.hypertag == "E" and node in e.nodes:
                for n in e.nodes:
                    if n in corners:
                        neighbors.append(n)
        
        if len(neighbors) != 2:
            return False
            
        c1, c2 = neighbors
        d1 = math.hypot(node.x - c1.x, node.y - c1.y)
        d2 = math.hypot(node.x - c2.x, node.y - c2.y)
        d_total = math.hypot(c1.x - c2.x, c1.y - c2.y)
        
        return abs((d1 + d2) - d_total) < 1e-4

    def _sort_angularly(self, nodes: List[Node], cx: float, cy: float) -> List[Node]:
        return sorted(nodes, key=lambda n: math.atan2(n.y - cy, n.x - cx))

    def _find_mid_node(self, graph: Graph, a: Node, b: Node) -> Optional[Node]:
        for n in graph.nodes:
            if n is a or n is b:
                continue
            has_a = any(e.hypertag == "E" and a in e.nodes and n in e.nodes for e in graph.hyperedges)
            has_b = any(e.hypertag == "E" and b in e.nodes and n in e.nodes for e in graph.hyperedges)
            if has_a and has_b:
                d1 = math.hypot(a.x - n.x, a.y - n.y)
                d2 = math.hypot(n.x - b.x, n.y - b.y)
                d = math.hypot(a.x - b.x, a.y - b.y)
                if abs((d1 + d2) - d) < 1e-4:
                    return n
        return None

    def _get_edge_attrs(self, graph: Graph, n1: Node, n2: Node) -> Dict:
        for e in graph.hyperedges:
            if e.hypertag == "E" and n1 in e.nodes and n2 in e.nodes:
                return {'R': e.R, 'B': e.B}
        return {'R': 0, 'B': 1}
