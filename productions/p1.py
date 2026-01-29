from production_base import Production
from typing import Optional
from graph_model import Graph, HyperEdge


@Production.register
class P1(Production):
    """
    P1: If there exists a quadrilateral element Q with R=1,
        then mark its boundary edges E (belonging to this Q) by setting R=1.
    """

    def get_left_side(self) -> Graph:
        return Graph()

    @staticmethod
    def _check_isomorphism(graph: Graph, q: HyperEdge) -> bool:
        """
        Check if there are exactly 4 boundary edges (E, R=0) connecting the nodes of Q.
        (This assumes the standard square topology v1-v2-v3-v4-v1)
        """
        q_nodes = set(q.nodes)
        count = 0
        for e in graph.hyperedges:
            if (
                e.hypertag == "E"
                and e.R == 0
                and len(e.nodes) == 2
                and e.nodes[0] in q_nodes
                and e.nodes[1] in q_nodes
            ):
                count += 1

        # We expect exactly 4 edges for a quadrilateral
        return count == 4

    def can_apply(self, graph: Graph) -> bool:
        for q in graph.hyperedges:
            if q.hypertag != "Q" or q.R != 1 or len(q.nodes) != 4:
                continue

            if self._check_isomorphism(graph, q):
                return True

        return False

    def find_match(
        self, graph: Graph, node_label: Optional[str] = None
    ) -> Optional[HyperEdge]:
        for q in graph.hyperedges:
            if q.hypertag != "Q" or q.R != 1 or len(q.nodes) != 4:
                continue

            if self._check_isomorphism(graph, q):
                if node_label and not any(n.label == node_label for n in q.nodes):
                    continue
                return q

        return None

    def get_right_side(self, matched: Graph, level: int) -> Graph:
        """
        Marks only those E-edges whose both endpoints are among the nodes of the matched Q (R=1).
        Everything else is preserved.
        """
        result = Graph()

        for node in matched.nodes:
            result.add_node(node)

        q = None
        for he in matched.hyperedges:
            if he.hypertag == "Q" and he.R == 1 and len(he.nodes) == 4:
                q = he
                break

        if q is None:
            for he in matched.hyperedges:
                result.add_edge(
                    HyperEdge(he.nodes, he.hypertag, he.boundary, he.R, he.B)
                )
            return result

        q_nodes = set(q.nodes)

        for he in matched.hyperedges:
            if he.hypertag == "E" and all(n in q_nodes for n in he.nodes):
                result.add_edge(HyperEdge(he.nodes, "E", he.boundary, R=1, B=he.B))
            else:
                result.add_edge(
                    HyperEdge(he.nodes, he.hypertag, he.boundary, he.R, he.B)
                )

        return result
