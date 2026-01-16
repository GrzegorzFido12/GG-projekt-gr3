from typing import Optional
from graph_model import Graph, Node, HyperEdge
from production_base import Production

@Production.register
class P6(Production):
    def get_left_side(self) -> Graph:
        g = Graph()
        n1 = Node(0, 0, "v1")
        n2 = Node(1, 0, "v2")
        n3 = Node(1, 2, "v3")
        n4 = Node(0, 2, "v4")
        n5 = Node(2, 1, "v5")
        for n in [n1, n2, n3, n4, n5]: g.add_node(n)

        g.add_edge(HyperEdge((n1, n2), "E", R=1, B=1))
        g.add_edge(HyperEdge((n2, n5), "E", R=2, B=2))
        g.add_edge(HyperEdge((n5, n3), "E", R=3, B=3))
        g.add_edge(HyperEdge((n3, n4), "E", R=6, B=4))
        g.add_edge(HyperEdge((n4, n1), "E", R=5, B=5))
        g.add_edge(HyperEdge((n1, n2, n3, n4, n5), "P", R=0))
        return g

    def get_right_side(self, matched: Graph, level: int) -> Graph:
        old_p_edge = next(e for e in matched.hyperedges if e.hypertag == "P")

        result = Graph()
        for node in matched.nodes:
            result.add_node(node)

        for edge in matched.hyperedges:
            if edge.hypertag == "E":
                result.add_edge(edge)

        result.add_edge(HyperEdge(old_p_edge.nodes, "P", R=1))

        return result

    def find_match(self, graph: Graph) -> Optional[HyperEdge]:
        for p_edge in graph.hyperedges:
            if p_edge.hypertag == "P" and len(p_edge.nodes) == 5 and p_edge.R == 0:
                return p_edge
        return None

    def can_apply(self, graph: Graph) -> bool:
        return self.find_match(graph) is not None
