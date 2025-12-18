"""
Test Suite for P11 Production

Tests included:
1. P11 BASIC HEXAGON: Verifies that a single hexagon marked for refinement is correctly transformed.
2. P11 CANNOT APPLY TO UNMARKED HEXAGON: Ensures P11 does not apply to unmarked hexagons.
3. P11 PRESERVES OTHER EDGES: Confirms that edges unrelated to the hexagon are preserved.
4. P11 HANGING NODE POSITION: Validates the correct placement of the central node.
5. P11 MULTIPLE HEXAGONS: Tests that P11 refines only the marked hexagon when multiple hexagons are present.
"""

import os
from graph_model import Graph, Node, HyperEdge
from p11 import P11
from visualization import draw

OUTPUT_DIR = "visualizations"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_hexagon_with_broken_edges():
    """Creates a hexagonal element with all edges broken and marked for refinement."""
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

def test_p11_basic_hexagon():
    """Test P11 on a hexagonal element with all edges broken."""
    g = create_hexagon_with_broken_edges()

    draw(g, f"{OUTPUT_DIR}/test_p11_basic_before.png")

    # Debugging: Print initial state
    print("Initial state:")
    print(f"Nodes: {len(g.nodes)}")
    print(f"Edges: {len(g.hyperedges)}")
    for edge in g.hyperedges:
        print(edge)

    # Verify initial state
    assert len(g.nodes) == 6
    edges = [e for e in g.hyperedges if e.hypertag == "E"]
    assert len(edges) == 6
    assert all(e.R == 0 for e in edges)

    hexagon = next(e for e in g.hyperedges if e.hypertag == "Q")
    assert hexagon.R == 1

    # Apply production P11
    p11 = P11()
    assert p11.can_apply(g)
    g.apply(p11)

    draw(g, f"{OUTPUT_DIR}/test_p11_basic_after.png")

    # Debugging: Print resulting state
    print("Resulting state:")
    print(f"Nodes: {len(g.nodes)}")
    print(f"Edges: {len(g.hyperedges)}")
    for edge in g.hyperedges:
        print(edge)

    # Verify resulting state
    assert len(g.nodes) == 7  # One new central node

    # Verify new elements
    new_elements = [e for e in g.hyperedges if e.hypertag == "Q"]
    assert len(new_elements) == 6
    assert all(e.R == 0 for e in new_elements)

def test_p11_cannot_apply_to_unmarked_hexagon():
    """Test that P11 cannot be applied to hexagons not marked for refinement."""
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

    g.add_edge(HyperEdge(tuple(nodes), "Q", R=0))

    draw(g, f"{OUTPUT_DIR}/test_p11_cannot_apply_to_unmarked_hexagon.png")

    p11 = P11()
    assert not p11.can_apply(g)

def test_p11_preserves_other_edges():
    """Test that P11 preserves edges that are not part of the hexagon being refined."""
    g = create_hexagon_with_broken_edges()

    # Add an extra edge not part of the hexagon
    extra_node = Node(2, 2, "extra")
    g.add_node(extra_node)
    g.add_edge(HyperEdge((g.nodes[0], extra_node), "E", boundary=True, R=0, B=1))

    draw(g, f"{OUTPUT_DIR}/test_p11_preserves_other_edges_before.png")

    p11 = P11()
    g.apply(p11)

    draw(g, f"{OUTPUT_DIR}/test_p11_preserves_other_edges_after.png")

    # Verify the extra edge is still present
    extra_edges = [e for e in g.hyperedges if "extra" in [n.label for n in e.nodes]]
    assert len(extra_edges) == 1

def test_p11_hanging_node_position():
    """Test that the central node is created at the correct position."""
    g = create_hexagon_with_broken_edges()

    draw(g, f"{OUTPUT_DIR}/test_p11_hanging_node_position_before.png")

    p11 = P11()
    g.apply(p11)

    draw(g, f"{OUTPUT_DIR}/test_p11_hanging_node_position_after.png")

    # Find the central node
    central_node = [n for n in g.nodes if n.label == "center"]
    assert len(central_node) == 1

    # Check position
    expected_x = sum(n.x for n in g.nodes if n.label.startswith("v")) / 6
    expected_y = sum(n.y for n in g.nodes if n.label.startswith("v")) / 6

    assert central_node[0].x == expected_x
    assert central_node[0].y == expected_y

def test_p11_embedded_in_larger_graph():
    """Test P11 when the hexagon is part of a larger graph."""
    pass  # Placeholder for future test implementation

def test_p11_multiple_hexagons():
    """Test P11 on a graph with multiple hexagons, only one marked for refinement."""
    g = Graph()

    # Create two hexagons
    nodes1 = [
        Node(0, 0, "v1"),
        Node(1, 0, "v2"),
        Node(1.5, 0.866, "v3"),
        Node(1, 1.732, "v4"),
        Node(0, 1.732, "v5"),
        Node(-0.5, 0.866, "v6"),
    ]
    nodes2 = [
        Node(3, 0, "u1"),
        Node(4, 0, "u2"),
        Node(4.5, 0.866, "u3"),
        Node(4, 1.732, "u4"),
        Node(3, 1.732, "u5"),
        Node(2.5, 0.866, "u6"),
    ]

    for n in nodes1 + nodes2:
        g.add_node(n)

    edges1 = [
        HyperEdge((nodes1[i], nodes1[(i + 1) % 6]), "E", boundary=True, R=0, B=1)
        for i in range(6)
    ]
    edges2 = [
        HyperEdge((nodes2[i], nodes2[(i + 1) % 6]), "E", boundary=True, R=0, B=1)
        for i in range(6)
    ]

    for e in edges1 + edges2:
        g.add_edge(e)

    g.add_edge(HyperEdge(tuple(nodes1), "Q", R=1))  # Mark the first hexagon for refinement
    g.add_edge(HyperEdge(tuple(nodes2), "Q", R=0))  # Second hexagon not marked

    draw(g, f"{OUTPUT_DIR}/test_p11_multiple_hexagons_before.png")

    # Apply P11
    p11 = P11()
    g.apply(p11)

    draw(g, f"{OUTPUT_DIR}/test_p11_multiple_hexagons_after.png")

    # Verify the first hexagon is refined
    q_edges = [e for e in g.hyperedges if e.hypertag == "Q"]
    assert len(q_edges) == 6 + 1  # 6 new Q edges + 1 unrefined hexagon
    assert all(e.R == 0 for e in q_edges if e != edges2[-1])

    # Verify the second hexagon remains unchanged
    unrefined_hexagon = next(e for e in g.hyperedges if e.nodes == tuple(nodes2))
    assert unrefined_hexagon.R == 0

if __name__ == "__main__":
    tests = [
        ("P11 BASIC HEXAGON", test_p11_basic_hexagon),
        ("P11 CANNOT APPLY TO UNMARKED HEXAGON", test_p11_cannot_apply_to_unmarked_hexagon),
        ("P11 PRESERVES OTHER EDGES", test_p11_preserves_other_edges),
        ("P11 HANGING NODE POSITION", test_p11_hanging_node_position),
        ("P11 EMBEDDED IN LARGER GRAPH", test_p11_embedded_in_larger_graph),
        ("P11 MULTIPLE HEXAGONS", test_p11_multiple_hexagons),
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

    print(f"\n{'='*50}")
    print(f"RESULTS: {passed}/{len(tests)} tests passed")

    if failed > 0:
        exit(1)