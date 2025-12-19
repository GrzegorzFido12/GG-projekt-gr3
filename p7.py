from production_base import Production
from graph_model import Graph, Node, HyperEdge
from typing import Optional

@Production.register
class P7(Production):
    """
    Production P7 - Marks edges of pentagonal element for refinement.
    
    This production finds a pentagonal element (hyperedge with label P) that is marked 
    for refinement (R=1) and marks all its edges (labeled E) for refinement by setting R=1.
    
    Left side: A pentagonal element P with R=1, connected to 5 nodes via 5 edges E
    Right side: Same structure, but all edges E now have R=1
    """
    
    def get_left_side(self) -> Graph:
        """
        Returns a graph representing the left side of production P7.
        A pentagonal element (P) with R=1, surrounded by 5 edges (E) with R=0.
        """
        g = Graph()
        
        # Create 5 vertices for the pentagon
        n1 = Node(0, 0, "v1")
        n2 = Node(1, 0, "v2")
        n3 = Node(1.5, 0.5, "v3")
        n4 = Node(0.5, 1, "v4")
        n5 = Node(-0.5, 0.5, "v5")
        
        g.add_node(n1)
        g.add_node(n2)
        g.add_node(n3)
        g.add_node(n4)
        g.add_node(n5)
        
        # Add the pentagonal element (P) connecting all 5 nodes
        g.add_edge(HyperEdge((n1, n2, n3, n4, n5), "P", boundary=False, R=1, B=0))
        
        # Add 5 edges (E) connecting consecutive vertices
        g.add_edge(HyperEdge((n1, n2), "E", boundary=False, R=0, B=0))
        g.add_edge(HyperEdge((n2, n3), "E", boundary=False, R=0, B=0))
        g.add_edge(HyperEdge((n3, n4), "E", boundary=False, R=0, B=0))
        g.add_edge(HyperEdge((n4, n5), "E", boundary=False, R=0, B=0))
        g.add_edge(HyperEdge((n5, n1), "E", boundary=False, R=0, B=0))
        
        return g
    
    def get_right_side(self, matched: Graph, level: int) -> Graph:
        """
        Returns the right side of the production.
        Marks all edges (E) connected to the pentagonal element (P) with R=1.
        """
        result = Graph()
        
        # Find the pentagonal element marked for refinement
        pentagon = None
        for edge in matched.hyperedges:
            if edge.hypertag == "P" and edge.R == 1:
                pentagon = edge
                break
        
        if pentagon is None:
            # If no matching pentagon found, return the original graph
            for node in matched.nodes:
                result.add_node(node)
            for edge in matched.hyperedges:
                result.add_edge(edge)
            return result
        
        # Get the 5 nodes of the pentagon
        pentagon_nodes = set(pentagon.nodes)
        
        # Add all nodes
        for node in matched.nodes:
            result.add_node(node)
        
        # Process all edges
        for edge in matched.hyperedges:
            if edge.hypertag == "E":
                # Check if this edge belongs to the pentagon
                # An edge belongs to the pentagon if both its nodes are in the pentagon
                edge_nodes = set(edge.nodes)
                if edge_nodes.issubset(pentagon_nodes) and len(edge.nodes) == 2:
                    # Mark this edge for refinement (set R=1)
                    result.add_edge(HyperEdge(edge.nodes, edge.hypertag, edge.boundary, R=1, B=edge.B))
                else:
                    # Keep the edge as is
                    result.add_edge(HyperEdge(edge.nodes, edge.hypertag, edge.boundary, edge.R, edge.B))
            else:
                # Copy non-edge hyperedges as is (like the pentagon itself)
                result.add_edge(HyperEdge(edge.nodes, edge.hypertag, edge.boundary, edge.R, edge.B))
        
        return result
    
    def can_apply(self, graph: Graph) -> bool:
        """
        Checks if the production can be applied to the given graph.
        Returns True if there exists a pentagonal element (P) marked for refinement (R=1).
        """
        for edge in graph.hyperedges:
            if edge.hypertag == "P" and edge.R == 1:
                return True
        return False
    
    def find_match(self, graph: Graph) -> Optional[HyperEdge]:
        """
        Finds a matching pentagonal element in the graph.
        Returns the first pentagonal element (P) marked for refinement (R=1).
        """
        for edge in graph.hyperedges:
            if edge.hypertag == "P" and edge.R == 1:
                return edge
        return None
    
    def is_isomorphic_to_left_side(self, subgraph: Graph) -> bool:
        """
        Checks if the given subgraph is isomorphic to the left side of the production.
        The left side consists of:
        - Exactly 5 nodes
        - 1 pentagonal element P with R=1
        - 5 edges E (with R=0) connecting consecutive vertices of the pentagon
        """
        nodes = subgraph.nodes
        edges = subgraph.hyperedges
        
        # Must have exactly 5 nodes
        if len(nodes) != 5:
            return False
        
        # Must have exactly 6 hyperedges (1 pentagon + 5 edges)
        if len(edges) != 6:
            return False
        
        # Find the pentagonal element
        pentagon = None
        edge_list = []
        for edge in edges:
            if edge.hypertag == "P" and edge.R == 1 and len(edge.nodes) == 5:
                pentagon = edge
            elif edge.hypertag == "E" and edge.R == 0 and len(edge.nodes) == 2:
                edge_list.append(edge)
            else:
                return False
        
        # Must have 1 pentagon and 5 edges
        if pentagon is None or len(edge_list) != 5:
            return False
        
        # Verify that pentagon connects all 5 nodes
        if set(pentagon.nodes) != set(nodes):
            return False
        
        # Verify that all edges connect nodes in the pentagon
        for edge in edge_list:
            if not set(edge.nodes).issubset(set(pentagon.nodes)):
                return False
        
        return True
    
    def find_all_matches(self, graph: Graph) -> list:
        """
        Finds all pentagonal elements in the graph that are marked for refinement.
        Returns a list of matching pentagonal hyperedges.
        """
        matches = []
        for edge in graph.hyperedges:
            if edge.hypertag == "P" and edge.R == 1:
                matches.append(edge)
        return matches