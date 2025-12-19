from production_base import Production
from graph_model import Graph, Node, HyperEdge
from typing import Optional

@Production.register
class P3(Production):
    """
    Production P3 - Breaks shared edges marked for refinement.
    
    This production finds a shared edge (B=0) that is marked for refinement (R=1)
    and splits it by:
    1. Creating a new hanging node at the midpoint of the edge.
    2. Replacing the original edge with two new edges connecting to the new node.
    3. Setting R=0 for the new edges.
    
    Left side: An edge E with B=0 (shared) and R=1 (marked for refinement).
    Right side: Two edges E with B=0 and R=0, connected through a new hanging node.
    """
    
    def get_left_side(self) -> Graph:
        g = Graph()
        n1 = Node(0, 0, "v1")
        n2 = Node(1, 0, "v2")
        g.add_node(n1)
        g.add_node(n2)
        g.add_edge(HyperEdge((n1, n2), "E", boundary=False, R=1, B=0))
        return g
    
    def get_right_side(self, matched: Graph, level: int) -> Graph:
        result = Graph()
        
        # Find the matched shared edge marked for refinement
        matched_edge = None
        for edge in matched.hyperedges:
            if edge.hypertag == "E" and edge.R == 1 and edge.B == 0:
                matched_edge = edge
                break
        
        if matched_edge is None:
            return matched
        
        n1, n2 = matched_edge.nodes[0], matched_edge.nodes[1]
        result.add_node(n1)
        result.add_node(n2)
        
        # Create a new hanging node at the midpoint
        mid_x, mid_y = (n1.x + n2.x) / 2, (n1.y + n2.y) / 2
        new_node_label = f"h_{n1.label}_{n2.label}"
        hanging_node = Node(mid_x, mid_y, new_node_label, hanging=True)
        result.add_node(hanging_node)
        
        # Create two new edges, shared (B=0) and not marked for refinement (R=0)
        result.add_edge(HyperEdge((n1, hanging_node), "E", boundary=False, R=0, B=0))
        result.add_edge(HyperEdge((hanging_node, n2), "E", boundary=False, R=0, B=0))
        
        return result

    def can_apply(self, graph: Graph) -> bool:
        return any(e.hypertag == "E" and e.R == 1 and e.B == 0 for e in graph.hyperedges)

    def find_match(self, graph: Graph) -> Optional[HyperEdge]:
        for edge in graph.hyperedges:
            if edge.hypertag == "E" and edge.R == 1 and edge.B == 0:
                return edge
        return None