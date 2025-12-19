from production_base import Production
from graph_model import Graph, Node, HyperEdge
from typing import Optional, List

@Production.register
class P7(Production):
    """
    Production P7 - Marks edges of a pentagonal element for refinement.
    
    This production finds a pentagonal element (P) marked for refinement (R=1)
    and sets the R attribute of all its five boundary edges (E) to 1.
    """
    
    def get_left_side(self) -> Graph:
        g = Graph()
        # Create 5 vertices for the pentagon
        nodes = [Node(0, 0, f"v{i}") for i in range(1, 6)]
        for n in nodes: g.add_node(n)
        
        # Central pentagonal hyperedge marked for refinement
        g.add_edge(HyperEdge(tuple(nodes), "P", R=1))
        
        # 5 surrounding edges (initially R=0 or any)
        for i in range(5):
            g.add_edge(HyperEdge((nodes[i], nodes[(i+1)%5]), "E", R=0))
        return g

    def find_match(self, graph: Graph) -> Optional[HyperEdge]:
        # The trigger is the central pentagonal edge P with R=1
        for edge in graph.hyperedges:
            if edge.hypertag == "P" and edge.R == 1 and len(edge.nodes) == 5:
                return edge
        return None

    def get_right_side(self, matched: Graph, level: int) -> Graph:
        result = Graph()
        # Find the central P edge in the matched subgraph
        p_edge = next(e for e in matched.hyperedges if e.hypertag == "P")
        p_nodes = p_edge.nodes
        
        # Add all nodes to result
        for node in matched.nodes:
            result.add_node(node)
            
        # Keep the central P edge
        result.add_edge(HyperEdge(p_nodes, "P", R=p_edge.R, B=p_edge.B))
        
        # For every edge E in the matched subgraph, set R=1
        for edge in matched.hyperedges:
            if edge.hypertag == "E":
                result.add_edge(HyperEdge(edge.nodes, "E", boundary=edge.boundary, R=1, B=edge.B))
            elif edge != p_edge:
                result.add_edge(HyperEdge(edge.nodes, edge.hypertag, edge.boundary, edge.R, edge.B))
                
        return result

    def can_apply(self, graph: Graph) -> bool:
        return self.find_match(graph) is not None