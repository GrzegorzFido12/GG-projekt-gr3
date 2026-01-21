from graph_model import Node, HyperEdge, Graph


def add_hanging_nodes_on_external_edges(
    graph: Graph,
    element_edge_tag: str = "P",
    edge_tag: str = "E"
) -> Graph:
    """
    For each external edge E of a polygonal element,
    inserts a hanging node that splits the edge into two.

    Returns a NEW graph.
    """

    new_graph = Graph()

    # 1. Skopiuj wszystkie węzły
    for node in graph.nodes:
        new_graph.add_node(node)

    # 2. Zidentyfikuj element (Q / P)
    elements = [e for e in graph.hyperedges if e.hypertag == element_edge_tag]
    if len(elements) != 1:
        raise ValueError("Expected exactly one polygonal element")

    element = elements[0]
    element_nodes = list(element.nodes)

    # pomocniczo: pary wierzchołków elementu
    polygon_edges_labels = {
        frozenset((element_nodes[i].label, element_nodes[(i + 1) % len(element_nodes)].label))
        for i in range(len(element_nodes))
    }

    # 3. Przetwarzaj krawędzie
    for edge in graph.hyperedges:
        if edge.hypertag != edge_tag:
            # inne hiperkrawędzie kopiujemy bez zmian
            new_graph.add_edge(edge)
            continue

        u, v = edge.nodes
        is_external = frozenset((u.label, v.label)) in polygon_edges_labels


        if not is_external:
            # wewnętrzne E – kopiujemy
            new_graph.add_edge(edge)
            continue

        # 4. Dodaj węzeł wiszący (środek krawędzi)
        hx = 0.5 * (u.x + v.x)
        hy = 0.5 * (u.y + v.y)
        h = Node(hx, hy, f"h_{u.label}_{v.label}")
        h.hyperref = edge   # oznaczenie: węzeł wiszący

        h.hanging = True
        new_graph.add_node(h)

        # 5. Zastąp E(u, v) przez E(u, h) i E(h, v)
        new_graph.add_edge(
            HyperEdge((u, h), edge_tag, R=edge.R, B=edge.B)
        )
        new_graph.add_edge(
            HyperEdge((h, v), edge_tag, R=edge.R, B=edge.B)
        )

    return new_graph
