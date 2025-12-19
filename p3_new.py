from production_base import Production
from graph_model import Graph, Node, HyperEdge
from typing import Optional, List
import uuid

@Production.register
class P3_alt(Production):
    """
    Production P3_alt - Refines a shared edge marked for refinement.
    
    This production finds a hyperedge E with R=1 and B=0 (unbroken, marked for refinement)
    connecting two nodes (V1, V2) and replaces it with two new E edges and a new node V_new 
    at the midpoint, plus another E edge forming a triangle (as per the image).
    It sets R=0 for the new E hyperedges.
    
    LHS: A hyperedge E connecting two nodes, R=1, B=0.
    RHS: The E is replaced by three new E edges and a new node V_new. R is set to 0.
    """
    
    def get_left_side(self) -> Graph:
        g = Graph()
        # Create 2 vertices
        v1 = Node(x=1, y=0, label="v1")
        v2 = Node(x=1, y=2, label="v2")
        g.add_node(v1)
        g.add_node(v2)
        
        # Hyperedge E marked for refinement (R=1) and B=0
        # The coordinates are placeholders; matching relies on hypertag and R/B.
        g.add_edge(HyperEdge((v1, v2), "E", R=1, B=0)) 
        return g

    def find_match(self, graph: Graph) -> Optional[HyperEdge]:
        # Find a hyperedge 'E' connecting exactly two nodes, with R=1 and B=0.
        for edge in graph.hyperedges:
            # Check for the hypertag, number of nodes, R=1, and B=0
            if edge.hypertag == "E" and len(edge.nodes) == 2 and edge.R == 1 and edge.B == 0:
                return edge
        return None

    def get_right_side(self, matched: Graph, level: int) -> Graph:
        result = Graph()
        
        # Find the matched edge that is a boundary edge marked for refinement
        matched_edge = None
        for edge in matched.hyperedges:
            if edge.hypertag == "E" and edge.R == 1 and edge.B == 0:
                matched_edge = edge
                break
        
        if matched_edge is None:
            # If no matching edge found, return the original graph
            for node in matched.nodes:
                result.add_node(node)
            for edge in matched.hyperedges:
                result.add_edge(edge)
            return result

        # The matched hyperedge is the one to be refined

        v1, v2 = matched_edge.nodes
        
        # --- 1. Create the new vertex V_new ---
        
        # Calculate midpoint coordinates for the new vertex
        # Note: In a real system, the coordinates might be managed differently, 
        # but for this example, we take the average as shown in the image.
        new_x = (v1.x + v2.x) 
        new_y = (v1.y + v2.y) / 2
        # Assuming a z-coordinate for the third dimension, but since it's not in Node,
        # we'll use a placeholder or assume 2D if the original nodes only have x/y.
        # For simplicity, we only use x and y from the Node definition.
        
        # Create a unique label for the new node
        new_node_label = f"v_new" 
        v_new = Node(x=new_x, y=new_y, label=new_node_label)
        result.add_node(v_new)
        
        # --- 2. Add original nodes to the result ---
        result.add_node(v1)
        result.add_node(v2)
        
        # E_new_1: (V2, V_new)
        result.add_edge(HyperEdge((v2, v_new), "E", R=0, B=matched_edge.B)) 
        
        # E_new_2: (V_new, V1)
        result.add_edge(HyperEdge((v_new, v1), "E", R=0, B=matched_edge.B))

        result.add_edge(HyperEdge((v2, v1), "E", R=0, B=matched_edge.B))
        
        # Copy other edges that are not the matched edge
        for edge in matched.hyperedges:
            if edge != matched_edge:
                result.add_edge(HyperEdge(edge.nodes, edge.hypertag, edge.boundary, edge.R, edge.B))
        
        return result

    def can_apply(self, graph: Graph) -> bool:
        return self.find_match(graph) is not None