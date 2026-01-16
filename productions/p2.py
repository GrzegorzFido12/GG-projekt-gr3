import math
from typing import Optional
from graph_model import Graph, Node, HyperEdge
from production_base import Production

@Production.register
class P2(Production):
    def get_left_side(self) -> Graph:
        g = Graph()
        v1 = Node(0, 0, "v1")
        v2 = Node(0, 2, "v2")
        v3 = Node(0, 1, "v3")

        g.add_node(v1)
        g.add_node(v2)
        g.add_node(v3)

        g.add_edge(HyperEdge((v1, v2), "E", R=1, B=0))
        g.add_edge(HyperEdge((v1, v3), "E", R=3, B=3))
        g.add_edge(HyperEdge((v3, v2), "E", R=2, B=2))
        return g

    def find_match(self, graph: Graph) -> Optional[HyperEdge]:
        for e1 in graph.hyperedges:
            if e1.hypertag == "E" and e1.R == 1 and e1.B == 0 and len(e1.nodes) == 2:
                u, v = e1.nodes[0], e1.nodes[1]

                target_x = (u.x + v.x) / 2
                target_y = (u.y + v.y) / 2

                w = next((n for n in graph.nodes if math.isclose(n.x, target_x)
                          and math.isclose(n.y, target_y) and n not in (u, v)), None)

                if w:
                    has_u_w = any(set(e.nodes) == {u, w} for e in graph.hyperedges)
                    has_v_w = any(set(e.nodes) == {v, w} for e in graph.hyperedges)

                    if has_u_w and has_v_w:
                        return HyperEdge((u, v, w), "E", R=1, B=0)
        return None

    def get_right_side(self, matched: Graph, level: int) -> Graph:
        main_edge = next(e for e in matched.hyperedges if e.R == 1)
        u, v = main_edge.nodes[0], main_edge.nodes[1]

        w = next(n for n in matched.nodes if n not in (u, v))

        result = Graph()

        for n in [u, v, w]:
            result.add_node(n)

        result.add_edge(HyperEdge((u, w), "E", R=0, B=main_edge.B))
        result.add_edge(HyperEdge((w, v), "E", R=0, B=main_edge.B))

        return result

    def can_apply(self, graph: Graph) -> bool:
        return self.find_match(graph) is not None
