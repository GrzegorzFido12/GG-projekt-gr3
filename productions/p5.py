from production_base import Production
from graph_model import Graph, Node, HyperEdge


@Production.register
class P5(Production):
    """
    P5: Splits Q (R=1) into 4 smaller quads if ALL its 4 sides are already broken
        into two E-edges with R=0 via a midpoint node.

    IMPORTANT: Graph.apply() passes to get_right_side() only a subgraph built from Q corners,
               so we MUST compute and store midpoints context while we still have the full graph.
    """

    def __init__(self):
        self._ctx = None

    def get_left_side(self) -> Graph:
        return Graph()

    @staticmethod
    def _find_midpoint_node(full_graph: Graph, a: Node, b: Node):
        """
        Find node m such that:
          E(a,m) exists with R=0
          E(m,b) exists with R=0
        """
        for e1 in full_graph.hyperedges:
            if e1.hypertag != "E" or e1.R != 0 or len(e1.nodes) != 2:
                continue
            if a not in e1.nodes:
                continue

            m = e1.nodes[0] if e1.nodes[1] == a else e1.nodes[1]
            if m == b:
                continue

            for e2 in full_graph.hyperedges:
                if e2.hypertag != "E" or e2.R != 0 or len(e2.nodes) != 2:
                    continue
                if m in e2.nodes and b in e2.nodes:
                    return m

        return None

    def _compute_ctx(self, full_graph: Graph):
        self._ctx = None

        for q in full_graph.hyperedges:
            if q.hypertag != "Q" or q.R != 1 or len(q.nodes) != 4:
                continue

            corners = list(q.nodes)
            mids = []

            ok = True
            for i in range(4):
                a = corners[i]
                b = corners[(i + 1) % 4]
                m = self._find_midpoint_node(full_graph, a, b)
                if m is None:
                    ok = False
                    break
                mids.append(m)

            if ok:
                self._ctx = {"q": q, "corners": corners, "mid": mids}
                return q

        return None

    def can_apply(self, graph: Graph) -> bool:
        return self._compute_ctx(graph) is not None

    def find_match(self, graph: Graph):
        return self._compute_ctx(graph)

    def get_right_side(self, matched: Graph, level: int) -> Graph:
        """
        matched contains ONLY corners of Q (and any edges strictly among those corners).
        We use self._ctx (computed on full graph) to build refinement result.
        """
        result = Graph()

        for node in matched.nodes:
            result.add_node(node)

        old_q = None
        for he in matched.hyperedges:
            if he.hypertag == "Q" and he.R == 1 and len(he.nodes) == 4:
                old_q = he
                break

        for he in matched.hyperedges:
            if he == old_q:
                continue
            result.add_edge(HyperEdge(he.nodes, he.hypertag, he.boundary, he.R, he.B))

        if not self._ctx:
            return result

        v1, v2, v3, v4 = self._ctx["corners"]
        m12, m23, m34, m41 = self._ctx["mid"]

        cx = (v1.x + v2.x + v3.x + v4.x) / 4.0
        cy = (v1.y + v2.y + v3.y + v4.y) / 4.0
        c = Node(cx, cy, f"c_{v1.label}_{v2.label}_{v3.label}_{v4.label}")
        result.add_node(c)

        for m in (m12, m23, m34, m41):
            result.add_edge(HyperEdge((c, m), "E", boundary=False, R=0, B=0))

        result.add_edge(HyperEdge((v1, m12, c, m41), "Q", boundary=False, R=0, B=0))
        result.add_edge(HyperEdge((v2, m23, c, m12), "Q", boundary=False, R=0, B=0))
        result.add_edge(HyperEdge((v3, m34, c, m23), "Q", boundary=False, R=0, B=0))
        result.add_edge(HyperEdge((v4, m41, c, m34), "Q", boundary=False, R=0, B=0))

        return result
