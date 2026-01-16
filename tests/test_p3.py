import os
import uuid
from graph_model import Graph, Node, HyperEdge
from productions.p3 import P3

# Assuming a visualization utility exists
# from visualization import draw
from visualization import draw

OUTPUT_DIR = "visualizations/p3"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def create_shared_edge_graph():
    """Creates a simple graph with a single shared edge marked for refinement (R=1, B=0)."""
    g = Graph()
    n1 = Node(1, 4, "v1")
    n2 = Node(1, 2, "v2")
    g.add_node(n1)
    g.add_node(n2)
    # R=1 (marked), B=0 (shared/internal)
    g.add_edge(HyperEdge((n1, n2), "E", boundary=False, R=1, B=0))
    return g, n1, n2


def create_two_quads_with_shared_edge():
    """Creates two adjacent squares with a shared internal edge, marked for P3 refinement."""
    g = Graph()
    nodes = [
        Node(0, 0, "n1"),  # bottom-left
        Node(4, 0, "n2"),  # bottom-mid
        Node(9, 0, "n3"),  # bottom-right
        Node(0, 4, "n4"),  # top-left
        Node(4, 4, "n5"),  # top-mid (node on shared edge)
        Node(9, 4, "n6"),  # top-right
    ]
    for n in nodes:
        g.add_node(n)

    # Boundary edges (R=0, B=1)
    g.add_edge(HyperEdge((nodes[0], nodes[1]), "E", boundary=True, R=0, B=1))
    g.add_edge(HyperEdge((nodes[1], nodes[2]), "E", boundary=True, R=0, B=1))
    g.add_edge(HyperEdge((nodes[3], nodes[4]), "E", boundary=True, R=0, B=1))
    g.add_edge(HyperEdge((nodes[4], nodes[5]), "E", boundary=True, R=0, B=1))
    g.add_edge(HyperEdge((nodes[0], nodes[3]), "E", boundary=True, R=0, B=1))
    g.add_edge(HyperEdge((nodes[2], nodes[5]), "E", boundary=False, R=1, B=0))

    # Shared internal edge, MARKED for P3 (R=1, B=0)
    g.add_edge(HyperEdge((nodes[1], nodes[4]), "E", boundary=False, R=1, B=0))

    # Two quadrilateral elements (Q)
    g.add_edge(HyperEdge((nodes[0], nodes[1], nodes[4], nodes[3]), "Q", R=0))
    g.add_edge(HyperEdge((nodes[1], nodes[2], nodes[5], nodes[4]), "Q", R=0))

    return g, nodes


# ============= TEST FUNCTIONS =============


def test_p3_basic_shared_edge():
    """Test P3 on a simple shared edge marked for refinement (R=1, B=0)."""
    g, n1, n2 = create_shared_edge_graph()

    # draw(g, f"{OUTPUT_DIR}/test_p3_basic_before.png")
    draw(g, f"{OUTPUT_DIR}/test_p3_basic_shared_edge_before.png")
    # Verify initial state
    assert len(g.nodes) == 2
    edges = [e for e in g.hyperedges if e.hypertag == "E"]
    assert len(edges) == 1
    assert edges[0].R == 1
    assert edges[0].B == 0

    production = P3()
    assert production.can_apply(g)

    result = g.apply(production)
    draw(g, f"{OUTPUT_DIR}/test_p3_basic_shared_edge_after.png")
    # draw(g, f"{OUTPUT_DIR}/test_p3_basic_after.png")

    # Verify production was applied
    assert result == 1

    # Should now have 3 nodes (original 2 + 1 new node)
    assert len(g.nodes) == 3

    # Should now have 2 edges instead of 1
    edges_after = [e for e in g.hyperedges if e.hypertag == "E"]
    assert len(edges_after) == 3

    # Both new edges should have R=0 and B=0
    for edge in edges_after:
        assert edge.R == 0, f"New edge R should be 0, got {edge.R}"
        assert edge.B == 0, f"New edge B should be 0, got {edge.B}"
        assert len(edge.nodes) == 2, "New edges must be 2-node segments"

    # Verify new node exists at midpoint
    new_nodes = [n for n in g.nodes if n.label.startswith("v_new")]
    assert len(new_nodes) == 1


def test_p3_cannot_apply_to_boundary_edge():
    """Test that P3 cannot be applied to boundary (B=1) edges."""
    g = Graph()
    n1 = Node(0, 0, "v1")
    n2 = Node(4, 0, "v2")
    g.add_node(n1)
    g.add_node(n2)
    # Boundary edge (B=1), even if marked for refinement
    g.add_edge(HyperEdge((n1, n2), "E", boundary=True, R=1, B=1))

    draw(g, f"{OUTPUT_DIR}/test_p3_cannot_apply_to_boundary_edge.png")

    production = P3()
    assert not production.can_apply(g)

    result = g.apply(production)
    assert result == 0


def test_p3_cannot_apply_to_unmarked_edge():
    """Test that P3 cannot be applied to edges not marked for refinement (R=0)."""
    g = Graph()
    n1 = Node(0, 0, "v1")
    n2 = Node(4, 0, "v2")
    g.add_node(n1)
    g.add_node(n2)
    # Shared edge (B=0) but not marked (R=0)
    g.add_edge(HyperEdge((n1, n2), "E", boundary=False, R=0, B=0))

    draw(g, f"{OUTPUT_DIR}/test_p3_cannot_apply_to_unmarked_edge.png")

    production = P3()
    assert not production.can_apply(g)

    result = g.apply(production)
    assert result == 0


def test_p3_on_two_quads_shared_edge():
    """Test P3 on a complex mesh where one shared edge is marked."""
    g, nodes = create_two_quads_with_shared_edge()

    draw(g, f"{OUTPUT_DIR}/test_p3_on_two_quads_shared_edge_before.png")
    # draw(g, f"{OUTPUT_DIR}/test_p3_two_quads_before.png")

    # Initial counts
    initial_nodes = len(g.nodes)
    initial_e_edges = len([e for e in g.hyperedges if e.hypertag == "E"])

    production = P3()
    cnt = 0
    while production.can_apply(g):
        result = g.apply(production)

        cnt += 1
        draw(g, f"{OUTPUT_DIR}/test_p3_on_two_quads_shared_edge_after_{cnt}.png")

    # draw(g, f"{OUTPUT_DIR}/test_p3_on_two_quads_shared_edge_after.png")

    # draw(g, f"{OUTPUT_DIR}/test_p3_two_quads_after.png")

    assert result == 1
    # print(result)
    # Should have one more node
    # print(len(g.nodes) , initial_nodes , cnt)

    assert len(g.nodes) == initial_nodes + cnt

    # Should have one more E edge (1 marked E becomes 2 new E's, so +1)
    final_e_edges = len([e for e in g.hyperedges if e.hypertag == "E"])
    # print(final_e_edges , initial_e_edges + 2*cnt)

    assert final_e_edges == initial_e_edges + 2 * cnt

    # Q edges should be preserved
    q_edges = [e for e in g.hyperedges if e.hypertag == "Q"]
    assert len(q_edges) == 2
    # print(len(q_edges))


def test_p3_hanging_node_position_diagonal():
    """Test that the new node is created at the correct midpoint for a diagonal edge."""
    g = Graph()
    n1 = Node(2, 6, "p1")
    n2 = Node(10, 14, "p2")
    g.add_node(n1)
    g.add_node(n2)
    g.add_edge(HyperEdge((n1, n2), "E", boundary=False, R=1, B=0))

    draw(g, f"{OUTPUT_DIR}/test_p3_hanging_node_position_diagonal_before.png")
    # draw(g, f"{OUTPUT_DIR}/test_p3_diagonal_before.png")

    production = P3()
    g.apply(production)

    draw(g, f"{OUTPUT_DIR}/test_p3_hanging_node_position_diagonal_after.png")
    # draw(g, f"{OUTPUT_DIR}/test_p3_diagonal_after.png")

    # Find the new node
    new_nodes = [n for n in g.nodes if n.label.startswith("v_new")]
    assert len(new_nodes) == 1

    # Check midpoint calculation
    expected_x = 2 + 10  # 6.0
    expected_y = (6 + 14) / 2  # 10.0

    assert new_nodes[0].x == expected_x, (
        f"Expected x={expected_x}, got {new_nodes[0].x}"
    )
    assert new_nodes[0].y == expected_y, (
        f"Expected y={expected_y}, got {new_nodes[0].y}"
    )


def test_p3_complete_right_side_verification():
    """Comprehensive test verifying all aspects of the right side of the production."""
    g = Graph()
    n1 = Node(0, 0, "v1")
    n2 = Node(6, 0, "v2")
    g.add_node(n1)
    g.add_node(n2)
    # The matching edge (R=1, B=0)
    g.add_edge(HyperEdge((n1, n2), "E", boundary=False, R=1, B=0))

    production = P3()
    result = g.apply(production)

    assert result == 1

    # Verify all vertices
    assert len(g.nodes) == 3, "Should have exactly 3 nodes"

    # Original nodes should still exist
    original_node_labels = {n1.label, n2.label}
    assert all(
        n.label in original_node_labels
        for n in g.nodes
        if not n.label.startswith("v_new")
    )

    # New node should exist
    new_nodes = [n for n in g.nodes if n.label.startswith("v_new")]
    assert len(new_nodes) == 1, "Should have 1 new node"

    new_node = new_nodes[0]
    assert new_node.x == 3.0, "New node x should be 3.0"
    assert new_node.y == 0.0, "New node y should be 0.0"

    # Verify all edges
    edges = [e for e in g.hyperedges if e.hypertag == "E"]
    assert len(edges) == 2, "Should have exactly 2 new E edges"

    for edge in edges:
        # All new edges should be shared/internal
        assert edge.B == 0, f"New edge should have B=0, got {edge.B}"
        # All new edges should not be marked for refinement
        assert edge.R == 0, f"New edge should have R=0, got {edge.R}"
        assert edge.hypertag == "E"
        assert len(edge.nodes) == 2

    # Verify edge connectivity
    # One edge should connect v1 to new node
    # Other edge should connect new node to v2
    edge_endpoints = []
    for edge in edges:
        coords = tuple(sorted([(n.x, n.y) for n in edge.nodes]))
        edge_endpoints.append(coords)

    expected_edge1 = tuple(sorted([(0, 0), (3.0, 0.0)]))
    expected_edge2 = tuple(sorted([(3.0, 0.0), (6, 0)]))

    assert expected_edge1 in edge_endpoints, "Missing new edge from v1 to new node"
    assert expected_edge2 in edge_endpoints, "Missing new edge from new node to v2"


if __name__ == "__main__":
    tests = [
        ("P3 BASIC SHARED EDGE", test_p3_basic_shared_edge),
        ("P3 CANNOT APPLY TO BOUNDARY EDGE", test_p3_cannot_apply_to_boundary_edge),
        ("P3 CANNOT APPLY TO UNMARKED EDGE", test_p3_cannot_apply_to_unmarked_edge),
        ("P3 ON TWO QUADS (SHARED EDGE)", test_p3_on_two_quads_shared_edge),
        ("P3 HANGING NODE POSITION (DIAGONAL)", test_p3_hanging_node_position_diagonal),
        # ("P3 COMPLETE RIGHT SIDE VERIFICATION", test_p3_complete_right_side_verification),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
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
            import traceback

            traceback.print_exc()
            failed += 1

    print(f"\n{'=' * 50}")
    print(f"RESULTS: {passed}/{len(tests)} tests passed")

    if failed > 0:
        exit(1)
