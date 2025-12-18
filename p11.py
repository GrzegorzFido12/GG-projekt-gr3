from production_base import Production
from graph_model import Graph, Node, HyperEdge
from typing import Optional


@Production.register
class P11(Production):
    """
    Production P11 - Breaks hexagonal elements marked for refinement.

    This production finds a hexagonal element (Q) marked for refinement (R=1) with all edges broken (R=0).
    It splits the hexagon into smaller elements, setting R=0 for all new hyperedges with label Q.

    Left side: A hexagonal element Q with R=1 and all edges broken (R=0).
    Right side: Smaller elements Q with R=0.
    """

    def get_left_side(self) -> Graph:
        """
        Returns a graph representing the left side of production P11.
        The left side is a hexagonal element (Q) marked for refinement (R=1) with all edges broken (R=0).
        """
        g = Graph()
        nodes = [
            Node(0, 0, "v1"),
            Node(1, 0, "v2"),
            Node(1.5, 0.866, "v3"),
            Node(1, 1.732, "v4"),
            Node(0, 1.732, "v5"),
            Node(-0.5, 0.866, "v6"),
        ]
        for n in nodes:
            g.add_node(n)

        edges = [
            HyperEdge((nodes[i], nodes[(i + 1) % len(nodes)]), "E", boundary=True, R=0, B=1)
            for i in range(len(nodes))
        ]
        for e in edges:
            g.add_edge(e)

        g.add_edge(HyperEdge(tuple(nodes), "Q", R=1))

        return g

    def get_right_side(self, matched: Graph, level: int) -> Graph:
        """
        Returns the right side of the production after applying it to the matched subgraph.
        Splits the hexagon into smaller elements, setting R=0 for all new hyperedges with label Q.
        """
        result = Graph()

        # Debugging: Print matched subgraph
        print("Matched subgraph:")
        print(f"Nodes: {len(matched.nodes)}")
        print(f"Edges: {len(matched.hyperedges)}")
        for edge in matched.hyperedges:
            print(edge)

        # Get the hexagon edge (Q with R=1)
        hexagon_edge = next((e for e in matched.hyperedges if e.hypertag == "Q" and e.R == 1), None)
        if not hexagon_edge:
            return result
        
        hexagon_nodes = list(hexagon_edge.nodes)

        # Add original nodes to the result graph
        for node in hexagon_nodes:
            result.add_node(node)

        # Create new elements (triangles) from the hexagon
        center_x = sum(node.x for node in hexagon_nodes) / len(hexagon_nodes)
        center_y = sum(node.y for node in hexagon_nodes) / len(hexagon_nodes)
        center_node = Node(center_x, center_y, "center")
        result.add_node(center_node)

        # Create triangular Q elements
        for i in range(len(hexagon_nodes)):
            edge_nodes = (hexagon_nodes[i], hexagon_nodes[(i + 1) % len(hexagon_nodes)], center_node)
            result.add_edge(HyperEdge(edge_nodes, "Q", R=0))

        # Preserve boundary edges (E edges with R=0)
        for edge in matched.hyperedges:
            if edge.hypertag == "E" and edge.R == 0:
                result.add_edge(edge)

        # Debugging: Print resulting graph
        print("Resulting graph:")
        print(f"Nodes: {len(result.nodes)}")
        print(f"Edges: {len(result.hyperedges)}")
        for edge in result.hyperedges:
            print(edge)

        return result

    def can_apply(self, graph: Graph) -> bool:
        """
        Checks if the production can be applied to the given graph.
        Returns True if there exists a hexagonal element (Q) marked for refinement (R=1) with all edges broken (R=0).
        """
        for edge in graph.hyperedges:
            if edge.hypertag == "Q" and edge.R == 1:
                hexagon_nodes = edge.nodes
                if all(
                    any(e.nodes == (hexagon_nodes[i], hexagon_nodes[(i + 1) % len(hexagon_nodes)]) and e.R == 0
                        for e in graph.hyperedges)
                    for i in range(len(hexagon_nodes))
                ):
                    return True
        return False

    def find_match(self, graph: Graph) -> Optional[HyperEdge]:
        """
        Finds a matching hexagonal element in the graph for the left side of the production.
        Returns the first hexagonal element (Q) marked for refinement (R=1) with all edges broken (R=0).
        """
        for edge in graph.hyperedges:
            if edge.hypertag == "Q" and edge.R == 1:
                hexagon_nodes = edge.nodes
                if all(
                    any(e.nodes == (hexagon_nodes[i], hexagon_nodes[(i + 1) % len(hexagon_nodes)]) and e.R == 0
                        for e in graph.hyperedges)
                    for i in range(len(hexagon_nodes))
                ):
                    return edge
        return None

    def is_isomorphic_to_left_side(self, subgraph: Graph) -> bool:
        """
        Checks if the given subgraph is isomorphic to the left side of the production.
        The left side consists of:
        - Exactly 6 nodes
        - Exactly 6 edges E with R=0
        - Exactly 1 edge Q with R=1
        """
        nodes = subgraph.nodes
        edges = subgraph.hyperedges

        if len(nodes) != 6 or len(edges) != 7:
            return False

        edge_counts = {
            "E": sum(1 for e in edges if e.hypertag == "E" and e.R == 0),
            "Q": sum(1 for e in edges if e.hypertag == "Q" and e.R == 1),
        }

        return edge_counts["E"] == 6 and edge_counts["Q"] == 1

    def find_all_matches(self, graph: Graph) -> list:
        """
        Finds all matching hexagonal elements in the graph for the left side of the production.
        Returns a list of hexagonal elements (Q) marked for refinement (R=1) with all edges broken (R=0).
        """
        matches = []
        for edge in graph.hyperedges:
            if edge.hypertag == "Q" and edge.R == 1:
                hexagon_nodes = edge.nodes
                if all(
                    any(e.nodes == (hexagon_nodes[i], hexagon_nodes[(i + 1) % len(hexagon_nodes)]) and e.R == 0
                        for e in graph.hyperedges)
                    for i in range(len(hexagon_nodes))
                ):
                    matches.append(edge)
        return matches