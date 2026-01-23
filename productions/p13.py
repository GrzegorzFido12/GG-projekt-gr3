from production_base import Production
from graph_model import Graph, Node, HyperEdge
from typing import Optional


@Production.register
class P13(Production):
    def get_left_side(self) -> Graph:
        g = Graph()
        nodes = [Node(0, 0, f"v{i}") for i in range(1, 8)]
        for n in nodes:
            g.add_node(n)
        
        g.add_edge(HyperEdge(tuple(nodes), "T", R=1))

        for i in range(7):
            g.add_edge(HyperEdge((nodes[i], nodes[(i + 1) % 7]), "E", R=0))
        return g

    def find_match(self, graph: Graph) -> Optional[HyperEdge]:
        t_edges = [e for e in graph.hyperedges if e.hypertag == "T" and e.R == 1 and len(e.nodes) == 7]

        for t_edge in t_edges:
            t_nodes_set = set(t_edge.nodes)

            enclosed_edges = [
                e
                for e in graph.hyperedges
                if e.hypertag == "E" and set(e.nodes).issubset(t_nodes_set)
            ]

            if len(enclosed_edges) != 7:
                continue

            if any(edge.R == 0 for edge in enclosed_edges):
                return t_edge
                
        return None

    def get_right_side(self, matched: Graph, level: int) -> Graph:
        result = Graph()

        for node in matched.nodes:
            result.add_node(node)

        for edge in matched.hyperedges:
            if edge.hypertag == "T":
                result.add_edge(HyperEdge(edge.nodes, "T", R=1, B=edge.B, boundary=edge.boundary))
            elif edge.hypertag == "E":
                result.add_edge(
                    HyperEdge(edge.nodes, "E", R=1, B=edge.B, boundary=edge.boundary)
                )
            else:
                result.add_edge(
                    HyperEdge(edge.nodes, edge.hypertag, R=edge.R, B=edge.B, boundary=edge.boundary)
                )

        return result

    def can_apply(self, graph: Graph) -> bool:
        return self.find_match(graph) is not None
