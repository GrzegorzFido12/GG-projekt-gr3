import os
from productions.p0 import P0
from graph_model import Graph, Node, HyperEdge
from visualization import draw


OUTPUT_DIR = "visualizations/p0_visualisations"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def create_square_graph(x, y, size, prefix):
    """
    Creates a square graph with 4 nodes and 4 boundary edges.
    Node layout:
    4 ---- 3
    |      |
    |      |
    1 ---- 2
    """
    g = Graph()

    nodes = [
        Node(x, y, f"{prefix}1"),
        Node(x + size, y, f"{prefix}2"),
        Node(x + size, y + size, f"{prefix}3"),
        Node(x, y + size, f"{prefix}4"),
    ]

    for n in nodes:
        g.add_node(n)

    for i in range(4):
        next_i = (i + 1) % 4
        g.add_edge(HyperEdge((nodes[i], nodes[next_i]), "E", R=0, B=0))

    return g, nodes


def create_bad_square_graph(x, y, size, prefix):
    """
    Creates a square graph with 4 nodes and 4 boundary edges.
    Node layout:
    4 ---- 3
    |      |
    |      |
    1 ---- 2
    """
    g = Graph()

    nodes = [
        Node(x, y, f"{prefix}1"),
        Node(x + size, y, f"{prefix}2"),
        Node(x + size, y + size, f"{prefix}3"),
        Node(x, y + size, f"{prefix}4"),
    ]

    for n in nodes:
        g.add_node(n)

    for i in range(4):
        next_i = (i + 1) % 4
        if i == 2:
            g.add_edge(HyperEdge((nodes[i], nodes[next_i]), "F", R=0, B=0))
        else:
            g.add_edge(HyperEdge((nodes[i], nodes[next_i]), "E", R=0, B=0))

    return g, nodes


def create_joined_squares_graph(x, y, size):
    """
    Creates two squares joined together, sharing a central edge.
    Node layout:
    4 -- 5 -- 6
    |    |    |
    1 -- 2 -- 3
    """
    g = Graph()

    n1 = Node(x, y, "n1")
    n2 = Node(x + size, y, "n2")
    n3 = Node(x + 2 * size, y, "n3")
    n4 = Node(x, y + size, "n4")
    n5 = Node(x + size, y + size, "n5")
    n6 = Node(x + 2 * size, y + size, "n6")

    nodes = [n1, n2, n3, n4, n5, n6]
    for n in nodes:
        g.add_node(n)

    g.add_edge(HyperEdge((n1, n2), "E", boundary=True))
    g.add_edge(HyperEdge((n2, n3), "E", boundary=True))
    g.add_edge(HyperEdge((n4, n5), "E", boundary=True))
    g.add_edge(HyperEdge((n5, n6), "E", boundary=True))

    g.add_edge(HyperEdge((n1, n4), "E", boundary=True))
    g.add_edge(HyperEdge((n2, n5), "E", boundary=False))
    g.add_edge(HyperEdge((n3, n6), "E", boundary=True))

    left_square_nodes = [n1, n2, n5, n4]
    right_square_nodes = [n2, n3, n6, n5]

    return g, left_square_nodes, right_square_nodes


def test_marking_unmarked_element():
    """
    Test: Graph with a square and a Q edge with R=0.
    Expected: Production should apply and mark Q with R=1.
    """
    g, nodes = create_square_graph(1, 1, 3, "x")
    g.add_edge(HyperEdge(tuple(nodes), "Q", R=0))

    draw(g, f"{OUTPUT_DIR}/test_p0_square_before.png")

    q_edge_before = [e for e in g.hyperedges if e.hypertag == "Q"][0]
    assert q_edge_before.R == 0

    production = P0()
    result = g.apply(production)

    draw(g, f"{OUTPUT_DIR}/test_p0_square_after.png")

    assert result == 1

    q_edge_after = [e for e in g.hyperedges if e.hypertag == "Q"][0]
    assert q_edge_after.R == 1


def test_already_marked_element():
    """
    Test: Graph with a square and a Q edge with R=1.
    Expected: Production should NOT apply as Q is already marked.
    """
    g, nodes = create_square_graph(1, 1, 3, "a")
    g.add_edge(HyperEdge(tuple(nodes), "Q", R=1))

    draw(g, f"{OUTPUT_DIR}/test_p0_already_marked_before.png")

    production = P0()

    result = g.apply(production)

    draw(g, f"{OUTPUT_DIR}/test_p0_already_marked_after.png")

    assert result == 0


def test_wrong_edge():
    """
    Test: Graph with a square and a Q edge with R=0 and one wrong edge.
    Expected: Production should NOT apply and mark Q as one edge is wrong.
    """
    g, nodes = create_bad_square_graph(1, 1, 3, "x")
    g.add_edge(HyperEdge(tuple(nodes), "Q", R=0))

    draw(g, f"{OUTPUT_DIR}/test_p0_wrong_square_before.png")

    q_edge_before = [e for e in g.hyperedges if e.hypertag == "Q"][0]
    assert q_edge_before.R == 0

    production = P0()
    result = g.apply(production)

    draw(g, f"{OUTPUT_DIR}/test_p0_wrong_square_after.png")

    assert result == 0

    q_edge_after = [e for e in g.hyperedges if e.hypertag == "Q"][0]
    assert q_edge_after.R == 0


def test_triangle():
    """
    Test: Graph with three nodes forming a triangle and a Q edge with R=0.
    Expected: Production should NOT apply as there are not enough boundary edges.
    """
    g = Graph()

    nodes = [Node(0, 0, "x1"), Node(2, 0, "x2"), Node(2, 2, "x3")]

    for n in nodes:
        g.add_node(n)

    for i in range(3):
        next_i = (i + 1) % 3
        g.add_edge(HyperEdge((nodes[i], nodes[next_i]), "E", R=0, B=1))

    g.add_edge(HyperEdge(tuple(nodes), "Q", R=0))

    draw(g, f"{OUTPUT_DIR}/test_p0_triangle_before.png")

    production = P0()

    result = g.apply(production)

    draw(g, f"{OUTPUT_DIR}/test_p0_triangle_after.png")

    assert result == 0

    q_edge = [e for e in g.hyperedges if e.hypertag == "Q"][0]
    assert q_edge.R == 0


def test_pentagon():
    """
    Test: Graph with 5 nodes (Pentagon).
    Expected: Should NOT apply (requires exactly 4 nodes).
    """
    g = Graph()
    nodes = [
        Node(0, 0, "x1"),
        Node(1, 0, "x2"),
        Node(2, 1, "x3"),
        Node(1, 2, "x4"),
        Node(0, 1, "x5"),
    ]
    for i in range(5):
        next_i = (i + 1) % 5
        g.add_edge(HyperEdge((nodes[i], nodes[next_i]), "E", R=0, B=1))

    g.add_edge(HyperEdge(tuple(nodes), "Q", R=0))

    draw(g, f"{OUTPUT_DIR}/test_p0_pentagon_before.png")

    production = P0()

    result = g.apply(production)

    draw(g, f"{OUTPUT_DIR}/test_p0_pentagon_after.png")

    assert result == 0

    q_edge = [e for e in g.hyperedges if e.hypertag == "Q"][0]
    assert q_edge.R == 0


def test_two_nodes_with_Q():
    """
    Test: Graph with two nodes connected by a Q edge with R=0.
    Expected: Production should NOT apply as there are not enough boundary edges.
    """
    g = Graph()

    n1 = Node(0, 0, "v1")
    n2 = Node(4, 0, "v2")

    g.add_node(n1)
    g.add_node(n2)

    g.add_edge(HyperEdge((n1, n2), "Q", R=0))

    draw(g, f"{OUTPUT_DIR}/test_p0_two_nodes_before.png")

    q_edge_before = [e for e in g.hyperedges if e.hypertag == "Q"][0]
    assert q_edge_before.R == 0

    production = P0()
    result = g.apply(production)

    draw(g, f"{OUTPUT_DIR}/test_p0_two_nodes_after.png")

    assert result == 0

    q_edge_after = [e for e in g.hyperedges if e.hypertag == "Q"][0]
    assert q_edge_after.R == 0


def test_edge_attributes_preserved():
    """
    Test: Square with Q(R=0) and edges with specific attributes.
    Expected: After applying production, edges should retain their attributes.
    """
    g, nodes = create_square_graph(0, 0, 2, "n")

    e_edges_before = [
        (e.nodes, e.hypertag, e.R, e.B) for e in g.hyperedges if e.hypertag == "E"
    ]

    g.add_edge(HyperEdge(tuple(nodes), "Q", R=0))

    production = P0()
    g.apply(production)

    e_edges_after = [
        (e.nodes, e.hypertag, e.R, e.B) for e in g.hyperedges if e.hypertag == "E"
    ]

    assert len(e_edges_before) == len(e_edges_after)
    assert set(e_edges_before) == set(e_edges_after)


def test_two_adjacent_squares_both_unmarked():
    """
    Test: Two adjacent squares, both R=0.
    Expected: Production should apply twice (once for left, once for right).
    """
    g, left_nodes, right_nodes = create_joined_squares_graph(0, 0, 10)

    g.add_edge(HyperEdge(tuple(left_nodes), "Q", R=0))
    g.add_edge(HyperEdge(tuple(right_nodes), "Q", R=0))

    draw(g, f"{OUTPUT_DIR}/test_adj_both_0_before.png")

    production = P0()

    assert g.apply(production) == 1, "Should apply to first square"

    assert g.apply(production) == 1, "Should apply to second square"

    assert g.apply(production) == 0, "Should not apply anymore"

    q_edges = [e for e in g.hyperedges if e.hypertag == "Q"]
    assert len(q_edges) == 2
    assert all(e.R == 1 for e in q_edges), "Both squares should be marked (R=1)"

    draw(g, f"{OUTPUT_DIR}/test_adj_both_0_after.png")


def test_two_adjacent_squares_mixed_state():
    """
    Test: Two adjacent squares, one with R=0, one with R=1.
    Expected: Production should apply only to the one with R=0.
    """
    g, left_nodes, right_nodes = create_joined_squares_graph(0, 0, 10)

    g.add_edge(HyperEdge(tuple(left_nodes), "Q", R=0))
    g.add_edge(HyperEdge(tuple(right_nodes), "Q", R=1))

    draw(g, f"{OUTPUT_DIR}/test_adj_mixed_before.png")

    production = P0()

    assert g.apply(production) == 1, "Should apply to the R=0 square"

    assert g.apply(production) == 0, "Should not apply again (right is already R=1)"

    left_q = [
        e for e in g.hyperedges if e.hypertag == "Q" and set(e.nodes) == set(left_nodes)
    ][0]
    right_q = [
        e
        for e in g.hyperedges
        if e.hypertag == "Q" and set(e.nodes) == set(right_nodes)
    ][0]

    assert left_q.R == 1, "Left square should adhere to production"
    assert right_q.R == 1, "Right square should remain R=1"

    draw(g, f"{OUTPUT_DIR}/test_adj_mixed_after.png")


def test_missing_boundary_edge():
    """
    Test: Square with Q(R=0) but one boundary edge is missing, creating a "hanging" node.
    Expected: Production should NOT apply due to incomplete boundary."""
    g = Graph()
    nodes = [Node(0, 0, "n1"), Node(1, 0, "n2"), Node(1, 1, "n3"), Node(0, 1, "n4")]
    for n in nodes:
        g.add_node(n)

    g.add_edge(HyperEdge((nodes[0], nodes[1]), "E", boundary=True))
    g.add_edge(HyperEdge((nodes[1], nodes[2]), "E", boundary=True))
    g.add_edge(HyperEdge((nodes[2], nodes[3]), "E", boundary=True))

    g.add_edge(HyperEdge(tuple(nodes), "Q", R=0))

    draw(g, f"{OUTPUT_DIR}/test_missing_boundary.png")

    production = P0()
    result = g.apply(production)

    assert result == 0, "Should NOT apply because boundary is not complete"

    q_edge = [e for e in g.hyperedges if e.hypertag == "Q"][0]
    assert q_edge.R == 0, "R should remain 0"


def test_double_edge_compensating_missing_edge():
    """
    Test: Square with 4 nodes, but one side has DOUBLE edges and one side has NONE.
    Expected: Production should NOT apply (needs 1 edge on each of the 4 sides).
    """
    g = Graph()
    nodes = [Node(0, 0, "n1"), Node(1, 0, "n2"), Node(1, 1, "n3"), Node(0, 1, "n4")]
    for n in nodes:
        g.add_node(n)

    g.add_edge(HyperEdge((nodes[0], nodes[1]), "E", boundary=True))
    g.add_edge(HyperEdge((nodes[0], nodes[1]), "E", boundary=True))

    g.add_edge(HyperEdge((nodes[1], nodes[2]), "E", boundary=True))

    g.add_edge(HyperEdge((nodes[2], nodes[3]), "E", boundary=True))

    g.add_edge(HyperEdge(tuple(nodes), "Q", R=0))

    draw(g, f"{OUTPUT_DIR}/test_p0_double_edge_compensating_missing_before.png")

    production = P0()
    result = g.apply(production)

    draw(g, f"{OUTPUT_DIR}/test_p0_double_edge_compensating_missing_after.png")

    assert result == 0, (
        "Production applied to an open loop because duplicate edges fooled the counter!"
    )


def test_q_attributes_preserved():
    """
    Test: Q edge has custom B=1.
    Expected: After production, new Q edge should still have B=1.
    """
    g, nodes = create_square_graph(0, 0, 1, "p")

    g.add_edge(HyperEdge(tuple(nodes), "Q", R=0, B=5))

    production = P0()
    g.apply(production)

    new_q = [e for e in g.hyperedges if e.hypertag == "Q"][0]
    assert new_q.R == 1
    assert new_q.B == 5, f"Expected B=5, got B={new_q.B}. Attribute B was lost!"


if __name__ == "__main__":
    tests = [
        ("MARKING UNMARKED ELEMENTS", test_marking_unmarked_element),
        ("MARKING ALREADY MARKED ELEMENTS", test_already_marked_element),
        ("WRONG EDGE TEST", test_wrong_edge),
        ("TRIANGLE TEST", test_triangle),
        ("PENTAGON TEST", test_pentagon),
        ("TWO NODES TEST", test_two_nodes_with_Q),
        ("ATTRIBUTES PRESERVED TEST", test_edge_attributes_preserved),
        ("TWO ADJACENT SQUARES BOTH UNMARKED", test_two_adjacent_squares_both_unmarked),
        ("TWO ADJACENT SQUARES MIXED STATE", test_two_adjacent_squares_mixed_state),
        ("MISSING BOUNDARY EDGE TEST", test_missing_boundary_edge),
        (
            "DOUBLE EDGE COMPENSATING MISSING EDGE TEST",
            test_double_edge_compensating_missing_edge,
        ),
        ("Q ATTRIBUTES PRESERVED TEST", test_q_attributes_preserved),
    ]

    passed = 0
    failed = 0

    for i, (name, test_func) in enumerate(tests, 1):
        print(f"\n{name}")
        try:
            test_func()
            print("PASSED")
            passed += 1
        except AssertionError as e:
            print(f"FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"ERROR: {e}")
            failed += 1

    print(f" {passed}/{len(tests)} tests passed")

    if failed > 0:
        exit(1)
