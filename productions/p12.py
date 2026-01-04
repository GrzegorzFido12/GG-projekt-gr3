from production_base import Production
from graph_model import Graph, HyperEdge, Node


@Production.register
class P12(Production):
    """
    Production P12:
    Marks a septagonal element (Q with 7 nodes) for refinement
    by setting its R attribute to 1.
    """

    def can_apply(self, graph: Graph) -> bool:
        return self.find_match(graph) is not None

    def find_match(self, graph: Graph):
        #sprawdzamy wszystkie hiperkrawędzie
        for q in graph.hyperedges:
            # podstawowe własności
            if q.hypertag != "T" or q.R != 0 or len(q.nodes) != 7:
                continue

            nodes = set(q.nodes)

            # Sprawdzenie, że wszystkie węzły istnieją w grafie
            if not all(n in graph.nodes for n in nodes):
                continue

            e_edges = [
                e for e in graph.hyperedges
                if (
                    e.hypertag == "E"
                    and len(e.nodes) == 2
                    and set(e.nodes).issubset(nodes)
                )
            ]

            # 3. musi mieć 7 krawędzi E
            if len(e_edges) != 7:
                continue

            # każdy wierzchołek o stopniu 2
            degree = {n: 0 for n in nodes}
            for e in e_edges:
                a, b = e.nodes
                degree[a] += 1
                degree[b] += 1

            if any(d != 2 for d in degree.values()):
                continue

            # jeden cykl
            visited = set()
            stack = [next(iter(nodes))]

            adjacency = {n: set() for n in nodes}
            for e in e_edges:
                a, b = e.nodes
                adjacency[a].add(b)
                adjacency[b].add(a)

            while stack:
                v = stack.pop()
                if v in visited:
                    continue
                visited.add(v)
                stack.extend(adjacency[v] - visited)

            if visited != nodes:
                continue

            return q

        return None

    def get_left_side(self) -> Graph:
        g = Graph()

        nodes = [Node(0.0, 0.0, f"v{i}") for i in range(7)]
        for n in nodes:
            g.add_node(n)

        # hiperkrawedz Q
        q = HyperEdge(
            nodes=tuple(nodes),
            hypertag="T",
            R=0,
            B=0
        )
        g.add_edge(q)

        # hiperkrawędzie E (tworzy siedmiokąt)
        for i in range(7):
            e = HyperEdge(
                nodes=(nodes[i], nodes[(i + 1) % 7]),
                hypertag="E",
                R=0,
                B=1   # boundary edge
            )
            g.add_edge(e)

        return g

    def get_right_side(self, matched: Graph, level: int) -> Graph:
        """
        Right side reproduces the same hyperedge,
        but with R = 1.
        """
        g = Graph()

        for node in matched.nodes:
            g.add_node(node)
        
        # R=1 dla Q + kopiowanie hiperkrawedzi
        for edge in matched.hyperedges:
            if edge.hypertag == "T" and len(edge.nodes) == 7:
                g.add_edge(
                    HyperEdge(
                        nodes=edge.nodes,
                        hypertag="T",
                        boundary=edge.boundary,
                        R=1,
                        B=edge.B,
                    )
                )
            else: g.add_edge(edge)

        return g

