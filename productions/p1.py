from production_base import Production
from graph_model import Graph, HyperEdge


@Production.register
class P1(Production):
    """
    P1: If there exists a quadrilateral element Q with R=1,
        then mark its boundary edges E (belonging to this Q) by setting R=1.
    """

    def get_left_side(self) -> Graph:
        return Graph()

    def can_apply(self, graph: Graph) -> bool:
        for q in graph.hyperedges:
            if q.hypertag != "Q" or q.R != 1 or len(q.nodes) != 4:
                continue

            for e in graph.hyperedges:
                if (
                    e.hypertag == "E"
                    and e.R == 0
                    and all(n in q.nodes for n in e.nodes)
                ):
                    return True

        return False

    def find_match(self, graph: Graph):
        for q in graph.hyperedges:
            if q.hypertag != "Q" or q.R != 1 or len(q.nodes) != 4:
                continue

            for e in graph.hyperedges:
                if (
                    e.hypertag == "E"
                    and e.R == 0
                    and all(n in q.nodes for n in e.nodes)
                ):
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
