from production_base import Production
from graph_model import Graph, Node, HyperEdge
from typing import Optional


@Production.register
class P4(Production):
    """
    Production P4 - Breaks boundary edges marked for refinement.
    
    This production finds a boundary edge (B=1) that is marked for refinement (R=1)
    and splits it by:
    1. Creating a new hanging node at the midpoint of the edge
    2. Replacing the original edge with two new edges connecting to the new node
    3. Setting R=0 for the new edges (they are no longer marked for refinement)
    
    Left side: An edge E with B=1 (boundary) and R=1 (marked for refinement)
    Right side: Two edges E with B=1 and R=0, connected through a new hanging node
    """
    
    def get_left_side(self) -> Graph:
        """
        Returns a graph representing the left side of production P4.
        The left side is a boundary edge (B=1) marked for refinement (R=1).
        """
        g = Graph()
        n1 = Node(0, 0, "v1")
        n2 = Node(1, 0, "v2")
        g.add_node(n1)
        g.add_node(n2)
        g.add_edge(HyperEdge((n1, n2), "E", boundary=True, R=1, B=1))
        return g
    
    def get_right_side(self, matched: Graph, level: int) -> Graph:
        """
        Returns the right side of the production after applying it to the matched subgraph.
        Creates a new hanging node at the midpoint and splits the edge into two.
        """
        result = Graph()
        
        # Find the matched edge that is a boundary edge marked for refinement
        matched_edge = None
        for edge in matched.hyperedges:
            if edge.hypertag == "E" and edge.R == 1 and edge.B == 1:
                matched_edge = edge
                break
        
        if matched_edge is None:
            # If no matching edge found, return the original graph
            for node in matched.nodes:
                result.add_node(node)
            for edge in matched.hyperedges:
                result.add_edge(edge)
            return result
        
        # Get the two nodes of the edge
        n1, n2 = matched_edge.nodes[0], matched_edge.nodes[1]
        
        # Add original nodes
        result.add_node(n1)
        result.add_node(n2)
        
        # Create a new hanging node at the midpoint
        mid_x = (n1.x + n2.x) / 2
        mid_y = (n1.y + n2.y) / 2
        new_node_label = f"h_{n1.label}_{n2.label}"
        hanging_node = Node(mid_x, mid_y, new_node_label, hanging=True)
        result.add_node(hanging_node)
        
        # Create two new edges, both boundary (B=1) but not marked for refinement (R=0)
        edge1 = HyperEdge((n1, hanging_node), "E", boundary=True, R=0, B=1)
        edge2 = HyperEdge((hanging_node, n2), "E", boundary=True, R=0, B=1)
        result.add_edge(edge1)
        result.add_edge(edge2)
        
        # Copy other edges that are not the matched edge
        for edge in matched.hyperedges:
            if edge != matched_edge:
                result.add_edge(HyperEdge(edge.nodes, edge.hypertag, edge.boundary, edge.R, edge.B))
        
        return result
    
    def can_apply(self, graph: Graph) -> bool:
        """
        Checks if the production can be applied to the given graph.
        Returns True if there exists a boundary edge (B=1) marked for refinement (R=1).
        """
        for edge in graph.hyperedges:
            if edge.hypertag == "E" and edge.R == 1 and edge.B == 1:
                return True
        return False
    
    def find_match(self, graph: Graph) -> Optional[HyperEdge]:
        """
        Finds a matching edge in the graph for the left side of the production.
        Returns the first boundary edge (B=1) marked for refinement (R=1).
        """
        for edge in graph.hyperedges:
            if edge.hypertag == "E" and edge.R == 1 and edge.B == 1:
                return edge
        return None
    
    def is_isomorphic_to_left_side(self, subgraph: Graph) -> bool:
        """
        Checks if the given subgraph is isomorphic to the left side of the production.
        The left side consists of:
        - Exactly 2 nodes
        - Exactly 1 edge E with B=1 and R=1
        """
        nodes = subgraph.nodes
        edges = subgraph.hyperedges
        
        # Must have exactly 2 nodes
        if len(nodes) != 2:
            return False
        
        # Must have exactly 1 edge
        if len(edges) != 1:
            return False
        
        edge = edges[0]
        
        # Edge must be labeled 'E', be a boundary edge (B=1), and marked for refinement (R=1)
        if edge.hypertag != "E":
            return False
        if edge.B != 1:
            return False
        if edge.R != 1:
            return False
        
        # Edge must connect the two nodes
        if set(edge.nodes) != set(nodes):
            return False
        
        return True
    
    def find_all_matches(self, graph: Graph) -> list:
        """
        Finds all subgraphs in the given graph that are isomorphic to the left side.
        Returns a list of matching edges.
        """
        matches = []
        for edge in graph.hyperedges:
            if edge.hypertag == "E" and edge.R == 1 and edge.B == 1:
                matches.append(edge)
        return matches

