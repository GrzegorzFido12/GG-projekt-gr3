from production_base import Production
from graph_model import Graph, HyperEdge


@Production.register
class P0(Production):
    def get_left_side(self) -> Graph:
        return Graph()

    def get_right_side(self, matched: Graph, level: int) -> Graph:
        result = Graph()
        
        for node in matched.nodes:
            result.add_node(node)
        
        for edge in matched.hyperedges:
            if edge.hypertag == "Q":
                result.add_edge(HyperEdge(edge.nodes, edge.hypertag, edge.boundary, R=1, B=edge.B))
            else:
                result.add_edge(HyperEdge(edge.nodes, edge.hypertag, edge.boundary, edge.R, edge.B))
        
        return result

    def can_apply(self, graph: Graph) -> bool:
        for edge in graph.hyperedges:
            if edge.hypertag == "Q" and edge.R == 0:
                return True
        return False

    def find_match(self, graph: Graph):
        for edge in graph.hyperedges:
            if edge.hypertag == "Q" and edge.R == 0:
                return edge
        return None