from production_base import Production
from graph_model import Graph, Node, HyperEdge


@Production.register
class P1(Production):
    """
    Production P1 - set boundary edges r=1.
    """

    def get_left_side(self) -> Graph:
        """
        Creates the left side of the production.

        Returns:
            Graph with 4 nodes in a square, connected by E edges,
            with Q hyperedge in the middle.
        """
        g = Graph()

        n1 = Node(0, 0, "n1")
        n2 = Node(1, 0, "n2")
        n3 = Node(1, 1, "n3")
        n4 = Node(0, 1, "n4")

        g.add_node(n1)
        g.add_node(n2)
        g.add_node(n3)
        g.add_node(n4)

        g.add_edge(HyperEdge((n1, n2), "E"))
        g.add_edge(HyperEdge((n2, n3), "E"))
        g.add_edge(HyperEdge((n3, n4), "E"))
        g.add_edge(HyperEdge((n4, n1), "E"))

        g.add_edge(HyperEdge((n1, n2, n3, n4), "Q"))

        return g

    def get_right_side(self, matched: Graph, level: int) -> Graph:
        """
        Creates the right side of the production.

        All E hyperedges get r=1.
        Q hyperedge is preserved.
        """
        g = Graph()

        # Add all nodes unchanged
        for node in matched.nodes:
            g.add_node(node)

        # Rewrite hyperedges
        for edge in matched.hyperedges:
            if edge.hypertag == "E":
                g.add_edge(
                    HyperEdge(edge.nodes, "E", r=1, b=edge.b),
                    check_nodes=False
                )
            elif edge.hypertag == "Q":
                g.add_edge(
                    HyperEdge(edge.nodes, "Q", r=edge.r, b=edge.b),
                    check_nodes=False
                )

        return g

    def can_apply(self, matched_graph: Graph) -> bool:
        """
        Production P1 can be applied if at least one E hyperedge
        is not yet marked with r = 1.
        """
        for edge in matched_graph.hyperedges:
            if edge.hypertag == "E" and edge.R != 1:
                return True
        return False

    def find_match(self, graph: Graph) -> list[Graph]:
        """
        Finds all subgraphs to which production P1 can be applied.
        """

        matches = []

        pattern = self.get_left_side()
        candidate_subgraphs = graph.find_subgraphs_isomorphic_to(pattern)

        for subgraph in candidate_subgraphs:
            if self.can_apply(subgraph):
                matches.append(subgraph)

        return matches[0]
