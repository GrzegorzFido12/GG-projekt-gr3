from graph_model import Graph, Node, HyperEdge
from production_base import Production


@Production.register
class P5(Production):
    """Production P5 - breaks quadrilateral into 4 smaller quadrilaterals."""

    def get_left_side(self) -> Graph:
        """Creates the left side pattern."""
        g = Graph()

        # Corner nodes
        n1 = Node(0, 0, "n1")
        n2 = Node(2, 0, "n2")
        n3 = Node(2, 2, "n3")
        n4 = Node(0, 2, "n4")

        # Midpoint nodes
        n5 = Node(1, 0, "n5")
        n6 = Node(2, 1, "n6")
        n7 = Node(1, 2, "n7")
        n8 = Node(0, 1, "n8")

        for node in [n1, n2, n3, n4, n5, n6, n7, n8]:
            g.add_node(node)

        # E hyperedges (all R=0)
        g.add_edge(HyperEdge((n1, n5), "E", r=0))
        g.add_edge(HyperEdge((n5, n2), "E", r=0))
        g.add_edge(HyperEdge((n2, n6), "E", r=0))
        g.add_edge(HyperEdge((n6, n3), "E", r=0))
        g.add_edge(HyperEdge((n3, n7), "E", r=0))
        g.add_edge(HyperEdge((n7, n4), "E", r=0))
        g.add_edge(HyperEdge((n4, n8), "E", r=0))
        g.add_edge(HyperEdge((n8, n1), "E", r=0))

        # Q hyperedge (R=1)
        g.add_edge(HyperEdge((n1, n2, n3, n4), "Q", r=1))

        return g

    def get_right_side(self, matched: Graph, level: int) -> Graph:
        """Creates the right side transformation (conforms to Production interface)."""
        g = Graph()

        # Retrieve nodes by their pattern labels
        n1 = matched.get_node("n1")
        n2 = matched.get_node("n2")
        n3 = matched.get_node("n3")
        n4 = matched.get_node("n4")
        n5 = matched.get_node("n5")
        n6 = matched.get_node("n6")
        n7 = matched.get_node("n7")
        n8 = matched.get_node("n8")

        # Calculate central vertex (centroid of corners)
        corners = [n1, n2, n3, n4]
        corner_labels = "_".join(sorted(n.label for n in corners))
        v_x = sum(n.x for n in corners) / 4
        v_y = sum(n.y for n in corners) / 4
        v = Node(v_x, v_y, f"V_{corner_labels}_L{level}")

        # Add all nodes
        for node in [n1, n2, n3, n4, n5, n6, n7, n8, v]:
            g.add_node(node)

        # Preserve existing E hyperedges (including boundary flag B)
        for edge in matched.hyperedges:
            if edge.hypertag == "E":
                g.add_edge(
                    HyperEdge(edge.nodes, "E", R=edge.R, B=edge.B)
                )

        # New internal E hyperedges: midpoint -> center
        for mp in [n5, n6, n7, n8]:
            g.add_edge(
                HyperEdge((mp, v), "E", R=0, B=0)
            )

        # New Q hyperedges (always internal)
        g.add_edge(HyperEdge((n1, n5, v, n8), "Q", R=0, B=0))
        g.add_edge(HyperEdge((n5, n2, n6, v), "Q", R=0, B=0))
        g.add_edge(HyperEdge((v, n6, n3, n7), "Q", R=0, B=0))
        g.add_edge(HyperEdge((n8, v, n7, n4), "Q", R=0, B=0))

        return g

    def can_apply(self, matched_graph: Graph) -> bool:
        """
        Checks whether the production P5 can be applied to the matched subgraph.
        Logical equivalent of the former filter_match method.
        """

        # Exactly one Q hyperedge marked for refinement
        q_edges = [e for e in matched_graph.hyperedges if e.hypertag == "Q"]
        if len(q_edges) != 1:
            return False
        if q_edges[0].r != 1:
            return False

        # All E hyperedges must be already broken (R = 0)
        e_edges = [e for e in matched_graph.hyperedges if e.hypertag == "E"]
        if not e_edges or not all(e.r == 0 for e in e_edges):
            return False

        # Exactly 8 regular nodes (4 corners + 4 midpoints)
        regular_nodes = [n for n in matched_graph.nodes if n.hyperref is None]
        if len(regular_nodes) != 8:
            return False

        return True

    def find_match(self, graph: Graph) -> list[Graph]:
        """
        Finds all subgraphs of `graph` to which this production can be applied.
        """

        matches = []

        # Step 1: structural matching using left side pattern
        pattern = self.get_left_side()
        candidate_subgraphs = graph.find_subgraphs_isomorphic_to(pattern)

        # Step 2: semantic filtering (R, B, counts, etc.)
        for subgraph in candidate_subgraphs:
            if self.can_apply(subgraph):
                matches.append(subgraph)

        return matches[0]
