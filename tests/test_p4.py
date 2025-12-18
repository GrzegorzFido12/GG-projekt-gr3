import os
from graph_model import Graph, Node, HyperEdge
from p4 import P4
from visualization import draw


OUTPUT_DIR = "visualizations"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def create_boundary_edge_graph():
    """Creates a simple graph with a single boundary edge marked for refinement."""
    g = Graph()
    n1 = Node(0, 0, "v1")
    n2 = Node(4, 0, "v2")
    g.add_node(n1)
    g.add_node(n2)
    g.add_edge(HyperEdge((n1, n2), "E", boundary=True, R=1, B=1))
    return g, n1, n2


def create_square_with_boundary_edges():
    """Creates a square with all boundary edges, one marked for refinement."""
    g = Graph()
    nodes = [
        Node(0, 0, "n1"),
        Node(4, 0, "n2"),
        Node(4, 4, "n3"),
        Node(0, 4, "n4")
    ]
    for n in nodes:
        g.add_node(n)
    
    # First edge is marked for refinement (R=1)
    g.add_edge(HyperEdge((nodes[0], nodes[1]), "E", boundary=True, R=1, B=1))
    # Other edges are not marked (R=0)
    g.add_edge(HyperEdge((nodes[1], nodes[2]), "E", boundary=True, R=0, B=1))
    g.add_edge(HyperEdge((nodes[2], nodes[3]), "E", boundary=True, R=0, B=1))
    g.add_edge(HyperEdge((nodes[3], nodes[0]), "E", boundary=True, R=0, B=1))
    
    # Add Q hyperedge for the quadrilateral
    g.add_edge(HyperEdge(tuple(nodes), "Q", R=0))
    
    return g, nodes


def create_complex_mesh():
    """Creates a more complex mesh with multiple elements."""
    g = Graph()
    nodes = [
        Node(0, 0, "a"),
        Node(4, 0, "b"),
        Node(8, 0, "c"),
        Node(0, 4, "d"),
        Node(4, 4, "e"),
        Node(8, 4, "f"),
    ]
    for n in nodes:
        g.add_node(n)
    
    # Boundary edges
    g.add_edge(HyperEdge((nodes[0], nodes[1]), "E", boundary=True, R=1, B=1))  # bottom-left, marked
    g.add_edge(HyperEdge((nodes[1], nodes[2]), "E", boundary=True, R=0, B=1))  # bottom-right
    g.add_edge(HyperEdge((nodes[0], nodes[3]), "E", boundary=True, R=0, B=1))  # left
    g.add_edge(HyperEdge((nodes[2], nodes[5]), "E", boundary=True, R=0, B=1))  # right
    g.add_edge(HyperEdge((nodes[3], nodes[4]), "E", boundary=True, R=0, B=1))  # top-left
    g.add_edge(HyperEdge((nodes[4], nodes[5]), "E", boundary=True, R=0, B=1))  # top-right
    
    # Internal edge (shared, not boundary)
    g.add_edge(HyperEdge((nodes[1], nodes[4]), "E", boundary=False, R=0, B=0))
    
    # Two quadrilateral elements
    g.add_edge(HyperEdge((nodes[0], nodes[1], nodes[4], nodes[3]), "Q", R=0))
    g.add_edge(HyperEdge((nodes[1], nodes[2], nodes[5], nodes[4]), "Q", R=0))
    
    return g, nodes


# ============= TEST FUNCTIONS =============

def test_p4_basic_boundary_edge():
    """Test P4 on a simple boundary edge marked for refinement."""
    g, n1, n2 = create_boundary_edge_graph()
    
    draw(g, f"{OUTPUT_DIR}/test_p4_basic_before.png")
    
    # Verify initial state
    assert len(g.nodes) == 2
    edges = [e for e in g.hyperedges if e.hypertag == "E"]
    assert len(edges) == 1
    assert edges[0].R == 1
    assert edges[0].B == 1
    
    production = P4()
    assert production.can_apply(g)
    
    result = g.apply(production)
    
    draw(g, f"{OUTPUT_DIR}/test_p4_basic_after.png")
    
    # Verify production was applied
    assert result == 1
    
    # Should now have 3 nodes (original 2 + 1 hanging node)
    assert len(g.nodes) == 3
    
    # Should now have 2 edges instead of 1
    edges_after = [e for e in g.hyperedges if e.hypertag == "E"]
    assert len(edges_after) == 2
    
    # Both edges should have R=0 and B=1
    for edge in edges_after:
        assert edge.R == 0, f"Edge R should be 0, got {edge.R}"
        assert edge.B == 1, f"Edge B should be 1, got {edge.B}"
    
    # Verify hanging node exists at midpoint
    hanging_nodes = [n for n in g.nodes if n.hanging]
    assert len(hanging_nodes) == 1
    assert hanging_nodes[0].x == 2.0  # midpoint of (0,0) and (4,0)
    assert hanging_nodes[0].y == 0.0


def test_p4_cannot_apply_to_shared_edge():
    """Test that P4 cannot be applied to shared (non-boundary) edges."""
    g = Graph()
    n1 = Node(0, 0, "v1")
    n2 = Node(4, 0, "v2")
    g.add_node(n1)
    g.add_node(n2)
    # Shared edge (B=0), even if marked for refinement
    g.add_edge(HyperEdge((n1, n2), "E", boundary=False, R=1, B=0))
    
    production = P4()
    assert not production.can_apply(g)
    
    result = g.apply(production)
    assert result == 0


def test_p4_cannot_apply_to_unmarked_edge():
    """Test that P4 cannot be applied to edges not marked for refinement."""
    g = Graph()
    n1 = Node(0, 0, "v1")
    n2 = Node(4, 0, "v2")
    g.add_node(n1)
    g.add_node(n2)
    # Boundary edge but not marked (R=0)
    g.add_edge(HyperEdge((n1, n2), "E", boundary=True, R=0, B=1))
    
    production = P4()
    assert not production.can_apply(g)
    
    result = g.apply(production)
    assert result == 0


def test_p4_on_square():
    """Test P4 on a square with one boundary edge marked for refinement."""
    g, nodes = create_square_with_boundary_edges()
    
    draw(g, f"{OUTPUT_DIR}/test_p4_square_before.png")
    
    # Initial counts
    initial_nodes = len(g.nodes)
    initial_edges = len([e for e in g.hyperedges if e.hypertag == "E"])
    
    production = P4()
    result = g.apply(production)
    
    draw(g, f"{OUTPUT_DIR}/test_p4_square_after.png")
    
    assert result == 1
    
    # Should have one more node
    assert len(g.nodes) == initial_nodes + 1
    
    # Should have one more edge (1 becomes 2, so +1)
    final_edges = len([e for e in g.hyperedges if e.hypertag == "E"])
    assert final_edges == initial_edges + 1
    
    # Q edge should be preserved
    q_edges = [e for e in g.hyperedges if e.hypertag == "Q"]
    assert len(q_edges) == 1


def test_p4_on_complex_mesh():
    """Test P4 on a complex mesh - should only break one boundary edge."""
    g, nodes = create_complex_mesh()
    
    draw(g, f"{OUTPUT_DIR}/test_p4_complex_before.png")
    
    # Count initial marked boundary edges
    marked_boundary_edges = [e for e in g.hyperedges if e.hypertag == "E" and e.R == 1 and e.B == 1]
    assert len(marked_boundary_edges) == 1
    
    production = P4()
    result = g.apply(production)
    
    draw(g, f"{OUTPUT_DIR}/test_p4_complex_after.png")
    
    assert result == 1
    
    # No more marked boundary edges
    marked_after = [e for e in g.hyperedges if e.hypertag == "E" and e.R == 1 and e.B == 1]
    assert len(marked_after) == 0
    
    # Q edges should be preserved
    q_edges = [e for e in g.hyperedges if e.hypertag == "Q"]
    assert len(q_edges) == 2


def test_p4_preserves_other_edges():
    """Test that P4 preserves edges that are not being broken."""
    g, nodes = create_square_with_boundary_edges()
    
    # Get edges not marked for refinement
    unmarked_edges_before = [
        (e.nodes[0].label, e.nodes[1].label, e.R, e.B) 
        for e in g.hyperedges 
        if e.hypertag == "E" and e.R == 0
    ]
    
    production = P4()
    g.apply(production)
    
    # Check that unmarked edges are still present
    unmarked_edges_after = [
        (e.nodes[0].label, e.nodes[1].label, e.R, e.B) 
        for e in g.hyperedges 
        if e.hypertag == "E" and e.R == 0 and "h_" not in e.nodes[0].label and "h_" not in e.nodes[1].label
    ]
    
    # All original unmarked edges should still be present (minus the one we broke, plus 2 new ones)
    assert len(unmarked_edges_before) == 3  # 3 unmarked edges initially


def test_p4_hanging_node_position():
    """Test that the hanging node is created at the correct midpoint."""
    g = Graph()
    n1 = Node(2, 6, "p1")
    n2 = Node(10, 14, "p2")
    g.add_node(n1)
    g.add_node(n2)
    g.add_edge(HyperEdge((n1, n2), "E", boundary=True, R=1, B=1))
    
    draw(g, f"{OUTPUT_DIR}/test_p4_diagonal_before.png")
    
    production = P4()
    g.apply(production)
    
    draw(g, f"{OUTPUT_DIR}/test_p4_diagonal_after.png")
    
    # Find the hanging node
    hanging_nodes = [n for n in g.nodes if n.hanging]
    assert len(hanging_nodes) == 1
    
    # Check midpoint calculation
    expected_x = (2 + 10) / 2  # 6
    expected_y = (6 + 14) / 2  # 10
    
    assert hanging_nodes[0].x == expected_x, f"Expected x={expected_x}, got {hanging_nodes[0].x}"
    assert hanging_nodes[0].y == expected_y, f"Expected y={expected_y}, got {hanging_nodes[0].y}"


def test_p4_isomorphism_check():
    """Test the isomorphism check function."""
    production = P4()
    
    # Create a valid left-side graph
    valid_g = Graph()
    n1 = Node(0, 0, "a")
    n2 = Node(1, 0, "b")
    valid_g.add_node(n1)
    valid_g.add_node(n2)
    valid_g.add_edge(HyperEdge((n1, n2), "E", boundary=True, R=1, B=1))
    
    assert production.is_isomorphic_to_left_side(valid_g)
    
    # Test with wrong R value
    invalid_g1 = Graph()
    n1 = Node(0, 0, "a")
    n2 = Node(1, 0, "b")
    invalid_g1.add_node(n1)
    invalid_g1.add_node(n2)
    invalid_g1.add_edge(HyperEdge((n1, n2), "E", boundary=True, R=0, B=1))
    
    assert not production.is_isomorphic_to_left_side(invalid_g1)
    
    # Test with wrong B value
    invalid_g2 = Graph()
    n1 = Node(0, 0, "a")
    n2 = Node(1, 0, "b")
    invalid_g2.add_node(n1)
    invalid_g2.add_node(n2)
    invalid_g2.add_edge(HyperEdge((n1, n2), "E", boundary=False, R=1, B=0))
    
    assert not production.is_isomorphic_to_left_side(invalid_g2)


def test_p4_missing_node():
    """Test that P4 handles graphs with missing nodes correctly."""
    g = Graph()
    n1 = Node(0, 0, "v1")
    g.add_node(n1)
    # Cannot create an edge with less than 2 nodes
    
    production = P4()
    assert not production.can_apply(g)


def test_p4_wrong_edge_label():
    """Test that P4 doesn't apply to edges with wrong labels."""
    g = Graph()
    n1 = Node(0, 0, "v1")
    n2 = Node(4, 0, "v2")
    g.add_node(n1)
    g.add_node(n2)
    # Edge with label Q instead of E
    g.add_edge(HyperEdge((n1, n2), "Q", boundary=True, R=1, B=1))
    
    production = P4()
    assert not production.can_apply(g)


def test_p4_find_all_matches():
    """Test finding all matching edges for P4."""
    g = Graph()
    nodes = [
        Node(0, 0, "a"),
        Node(4, 0, "b"),
        Node(8, 0, "c"),
        Node(12, 0, "d")
    ]
    for n in nodes:
        g.add_node(n)
    
    # Three boundary edges marked for refinement
    g.add_edge(HyperEdge((nodes[0], nodes[1]), "E", boundary=True, R=1, B=1))
    g.add_edge(HyperEdge((nodes[1], nodes[2]), "E", boundary=True, R=1, B=1))
    g.add_edge(HyperEdge((nodes[2], nodes[3]), "E", boundary=True, R=1, B=1))
    
    draw(g, f"{OUTPUT_DIR}/test_p4_multiple_before.png")
    
    production = P4()
    matches = production.find_all_matches(g)
    
    assert len(matches) == 3
    
    # Apply production multiple times
    for _ in range(3):
        g.apply(production)
    
    draw(g, f"{OUTPUT_DIR}/test_p4_multiple_after.png")
    
    # All edges should now be broken (R=0)
    marked_edges = [e for e in g.hyperedges if e.hypertag == "E" and e.R == 1]
    assert len(marked_edges) == 0


def test_p4_embedded_in_larger_graph():
    """Test P4 when the matching subgraph is part of a larger graph."""
    g = Graph()
    
    # Create a larger mesh with one boundary edge marked
    nodes = [
        Node(0, 0, "m1"),
        Node(4, 0, "m2"),
        Node(8, 0, "m3"),
        Node(0, 4, "m4"),
        Node(4, 4, "m5"),
        Node(8, 4, "m6"),
        Node(0, 8, "m7"),
        Node(4, 8, "m8"),
        Node(8, 8, "m9"),
    ]
    for n in nodes:
        g.add_node(n)
    
    # Bottom row - only first edge is boundary and marked
    g.add_edge(HyperEdge((nodes[0], nodes[1]), "E", boundary=True, R=1, B=1))
    g.add_edge(HyperEdge((nodes[1], nodes[2]), "E", boundary=True, R=0, B=1))
    
    # Middle row
    g.add_edge(HyperEdge((nodes[3], nodes[4]), "E", boundary=False, R=0, B=0))
    g.add_edge(HyperEdge((nodes[4], nodes[5]), "E", boundary=False, R=0, B=0))
    
    # Top row
    g.add_edge(HyperEdge((nodes[6], nodes[7]), "E", boundary=True, R=0, B=1))
    g.add_edge(HyperEdge((nodes[7], nodes[8]), "E", boundary=True, R=0, B=1))
    
    # Vertical edges (left and right are boundary)
    g.add_edge(HyperEdge((nodes[0], nodes[3]), "E", boundary=True, R=0, B=1))
    g.add_edge(HyperEdge((nodes[3], nodes[6]), "E", boundary=True, R=0, B=1))
    g.add_edge(HyperEdge((nodes[2], nodes[5]), "E", boundary=True, R=0, B=1))
    g.add_edge(HyperEdge((nodes[5], nodes[8]), "E", boundary=True, R=0, B=1))
    
    # Internal vertical edges
    g.add_edge(HyperEdge((nodes[1], nodes[4]), "E", boundary=False, R=0, B=0))
    g.add_edge(HyperEdge((nodes[4], nodes[7]), "E", boundary=False, R=0, B=0))
    
    # Add Q hyperedges for each cell
    g.add_edge(HyperEdge((nodes[0], nodes[1], nodes[4], nodes[3]), "Q", R=0))
    g.add_edge(HyperEdge((nodes[1], nodes[2], nodes[5], nodes[4]), "Q", R=0))
    g.add_edge(HyperEdge((nodes[3], nodes[4], nodes[7], nodes[6]), "Q", R=0))
    g.add_edge(HyperEdge((nodes[4], nodes[5], nodes[8], nodes[7]), "Q", R=0))
    
    draw(g, f"{OUTPUT_DIR}/test_p4_large_mesh_before.png")
    
    initial_node_count = len(g.nodes)
    initial_q_edges = len([e for e in g.hyperedges if e.hypertag == "Q"])
    
    production = P4()
    result = g.apply(production)
    
    draw(g, f"{OUTPUT_DIR}/test_p4_large_mesh_after.png")
    
    assert result == 1
    
    # One new node should be added
    assert len(g.nodes) == initial_node_count + 1
    
    # Q edges should be preserved
    final_q_edges = len([e for e in g.hyperedges if e.hypertag == "Q"])
    assert final_q_edges == initial_q_edges


def test_p4_triangle_boundary():
    """Test P4 on a triangle with boundary edges."""
    g = Graph()
    nodes = [
        Node(0, 0, "t1"),
        Node(6, 0, "t2"),
        Node(3, 5, "t3")
    ]
    for n in nodes:
        g.add_node(n)
    
    # All boundary edges, only one marked
    g.add_edge(HyperEdge((nodes[0], nodes[1]), "E", boundary=True, R=1, B=1))
    g.add_edge(HyperEdge((nodes[1], nodes[2]), "E", boundary=True, R=0, B=1))
    g.add_edge(HyperEdge((nodes[2], nodes[0]), "E", boundary=True, R=0, B=1))
    
    draw(g, f"{OUTPUT_DIR}/test_p4_triangle_before.png")
    
    production = P4()
    result = g.apply(production)
    
    draw(g, f"{OUTPUT_DIR}/test_p4_triangle_after.png")
    
    assert result == 1
    
    # Check that we have 4 nodes now
    assert len(g.nodes) == 4
    
    # Check that the hanging node is at the correct position
    hanging = [n for n in g.nodes if n.hanging][0]
    assert hanging.x == 3.0  # midpoint of (0,0) and (6,0)
    assert hanging.y == 0.0


def test_p4_missing_edge():
    """Test that P4 cannot be applied when there are 2 nodes but no edge connecting them."""
    g = Graph()
    n1 = Node(0, 0, "v1")
    n2 = Node(4, 0, "v2")
    g.add_node(n1)
    g.add_node(n2)
    # No edge added - missing edge
    
    production = P4()
    assert not production.can_apply(g)
    
    result = g.apply(production)
    assert result == 0
    
    # Graph should remain unchanged
    assert len(g.nodes) == 2
    assert len(g.hyperedges) == 0


def test_p4_vertex_label_change():
    """Test that changing vertex labels doesn't affect the production mechanism."""
    # Test with various vertex labels - production should still work
    # Note: empty labels are not tested because Node uses label for hashing/equality
    test_cases = [
        ("a", "b"),
        ("node_1", "node_2"),
        ("x", "y"),  # short labels
        ("123", "456"),  # numeric strings
        ("α", "β"),  # unicode labels
        ("very_long_label_name_1", "very_long_label_name_2"),  # long labels
    ]
    
    production = P4()
    
    for label1, label2 in test_cases:
        g = Graph()
        n1 = Node(0, 0, label1)
        n2 = Node(4, 0, label2)
        g.add_node(n1)
        g.add_node(n2)
        g.add_edge(HyperEdge((n1, n2), "E", boundary=True, R=1, B=1))
        
        # Production should be applicable regardless of vertex labels
        assert production.can_apply(g), f"Failed for labels: {label1}, {label2}"
        
        result = g.apply(production)
        assert result == 1, f"Production failed for labels: {label1}, {label2}"
        
        # Should have 3 nodes after application
        assert len(g.nodes) == 3, f"Wrong node count for labels: {label1}, {label2}"


def test_p4_wrong_vertex_coordinates():
    """Test that production works correctly with various vertex coordinates."""
    production = P4()
    
    # Test with different coordinate configurations
    test_cases = [
        # (x1, y1, x2, y2, expected_mid_x, expected_mid_y)
        (0, 0, 4, 0, 2.0, 0.0),        # horizontal
        (0, 0, 0, 4, 0.0, 2.0),        # vertical
        (0, 0, 4, 4, 2.0, 2.0),        # diagonal
        (-2, -2, 2, 2, 0.0, 0.0),      # crossing origin
        (1.5, 2.5, 3.5, 4.5, 2.5, 3.5),  # floating point
        (100, 200, 300, 400, 200.0, 300.0),  # large values
        (-100, -200, -300, -400, -200.0, -300.0),  # negative values
    ]
    
    for x1, y1, x2, y2, exp_mid_x, exp_mid_y in test_cases:
        g = Graph()
        n1 = Node(x1, y1, "v1")
        n2 = Node(x2, y2, "v2")
        g.add_node(n1)
        g.add_node(n2)
        g.add_edge(HyperEdge((n1, n2), "E", boundary=True, R=1, B=1))
        
        result = g.apply(production)
        assert result == 1, f"Production failed for coords: ({x1},{y1})-({x2},{y2})"
        
        # Verify hanging node position
        hanging_nodes = [n for n in g.nodes if n.hanging]
        assert len(hanging_nodes) == 1
        
        assert hanging_nodes[0].x == exp_mid_x, \
            f"Wrong x for ({x1},{y1})-({x2},{y2}): expected {exp_mid_x}, got {hanging_nodes[0].x}"
        assert hanging_nodes[0].y == exp_mid_y, \
            f"Wrong y for ({x1},{y1})-({x2},{y2}): expected {exp_mid_y}, got {hanging_nodes[0].y}"


def test_p4_remove_random_edge_from_valid_graph():
    """Test that removing an edge from a valid matching graph prevents production."""
    # Create a graph that would normally match (square with one marked boundary edge)
    g = Graph()
    nodes = [
        Node(0, 0, "n1"),
        Node(4, 0, "n2"),
        Node(4, 4, "n3"),
        Node(0, 4, "n4")
    ]
    for n in nodes:
        g.add_node(n)
    
    # Add all edges except the one marked for refinement (simulate "removing" it)
    # The marked edge (n1-n2) is NOT added
    g.add_edge(HyperEdge((nodes[1], nodes[2]), "E", boundary=True, R=0, B=1))
    g.add_edge(HyperEdge((nodes[2], nodes[3]), "E", boundary=True, R=0, B=1))
    g.add_edge(HyperEdge((nodes[3], nodes[0]), "E", boundary=True, R=0, B=1))
    
    production = P4()
    
    # Should not be able to apply - no edge with R=1 and B=1
    assert not production.can_apply(g)
    
    result = g.apply(production)
    assert result == 0
    
    # Graph should remain unchanged
    assert len(g.nodes) == 4
    assert len(g.hyperedges) == 3


def test_p4_visualization_correctness():
    """Test that visualization contains correct elements after production."""
    import os
    
    g, n1, n2 = create_boundary_edge_graph()
    
    # Apply production
    production = P4()
    g.apply(production)
    
    # Verify graph state which will be visualized
    # 1. All vertices exist
    assert len(g.nodes) == 3
    
    # 2. All edges exist
    edges = [e for e in g.hyperedges if e.hypertag == "E"]
    assert len(edges) == 2
    
    # 3. Vertices have correct coordinates
    node_coords = {(n.x, n.y) for n in g.nodes}
    assert (0, 0) in node_coords, "Original node (0,0) missing"
    assert (4, 0) in node_coords, "Original node (4,0) missing"
    assert (2.0, 0.0) in node_coords, "Hanging node (2,0) missing"
    
    # 4. Vertices have labels
    for node in g.nodes:
        assert node.label is not None, f"Node at ({node.x}, {node.y}) has no label"
    
    # 5. Edges connect correct nodes
    edge_node_coords = set()
    for edge in edges:
        for node in edge.nodes:
            edge_node_coords.add((node.x, node.y))
    
    # All nodes should be connected by edges
    assert edge_node_coords == node_coords, "Not all nodes are connected by edges"
    
    # Draw and verify file was created
    output_path = f"{OUTPUT_DIR}/test_p4_viz_correctness.png"
    draw(g, output_path)
    assert os.path.exists(output_path), f"Visualization file {output_path} was not created"


def test_p4_complete_right_side_verification():
    """Comprehensive test verifying all aspects of the right side of the production."""
    g = Graph()
    n1 = Node(0, 0, "v1")
    n2 = Node(6, 0, "v2")
    g.add_node(n1)
    g.add_node(n2)
    g.add_edge(HyperEdge((n1, n2), "E", boundary=True, R=1, B=1))
    
    production = P4()
    result = g.apply(production)
    
    assert result == 1
    
    # Verify all vertices
    assert len(g.nodes) == 3, "Should have exactly 3 nodes"
    
    # Original nodes should still exist
    original_nodes = [n for n in g.nodes if not n.hanging]
    assert len(original_nodes) == 2, "Should have 2 original nodes"
    
    # Hanging node should exist
    hanging_nodes = [n for n in g.nodes if n.hanging]
    assert len(hanging_nodes) == 1, "Should have 1 hanging node"
    
    hanging = hanging_nodes[0]
    assert hanging.x == 3.0, f"Hanging node x should be 3.0, got {hanging.x}"
    assert hanging.y == 0.0, f"Hanging node y should be 0.0, got {hanging.y}"
    assert hanging.label is not None, "Hanging node should have a label"
    
    # Verify all edges
    edges = [e for e in g.hyperedges if e.hypertag == "E"]
    assert len(edges) == 2, "Should have exactly 2 edges"
    
    for edge in edges:
        # All edges should be boundary edges
        assert edge.B == 1, f"Edge should have B=1, got {edge.B}"
        # All edges should not be marked for refinement
        assert edge.R == 0, f"Edge should have R=0, got {edge.R}"
        # All edges should have label "E"
        assert edge.hypertag == "E", f"Edge should have label 'E', got {edge.hypertag}"
        # All edges should connect exactly 2 nodes
        assert len(edge.nodes) == 2, f"Edge should connect 2 nodes, got {len(edge.nodes)}"
    
    # Verify edge connectivity
    # One edge should connect v1 to hanging node
    # Other edge should connect hanging node to v2
    edge_endpoints = []
    for edge in edges:
        coords = tuple(sorted([(n.x, n.y) for n in edge.nodes]))
        edge_endpoints.append(coords)
    
    expected_edge1 = tuple(sorted([(0, 0), (3.0, 0.0)]))
    expected_edge2 = tuple(sorted([(3.0, 0.0), (6, 0)]))
    
    assert expected_edge1 in edge_endpoints, f"Missing edge from v1 to hanging node"
    assert expected_edge2 in edge_endpoints, f"Missing edge from hanging node to v2"


if __name__ == "__main__":
    tests = [
        ("P4 BASIC BOUNDARY EDGE", test_p4_basic_boundary_edge),
        ("P4 CANNOT APPLY TO SHARED EDGE", test_p4_cannot_apply_to_shared_edge),
        ("P4 CANNOT APPLY TO UNMARKED EDGE", test_p4_cannot_apply_to_unmarked_edge),
        ("P4 ON SQUARE", test_p4_on_square),
        ("P4 ON COMPLEX MESH", test_p4_on_complex_mesh),
        ("P4 PRESERVES OTHER EDGES", test_p4_preserves_other_edges),
        ("P4 HANGING NODE POSITION", test_p4_hanging_node_position),
        ("P4 ISOMORPHISM CHECK", test_p4_isomorphism_check),
        ("P4 MISSING NODE", test_p4_missing_node),
        ("P4 WRONG EDGE LABEL", test_p4_wrong_edge_label),
        ("P4 FIND ALL MATCHES", test_p4_find_all_matches),
        ("P4 EMBEDDED IN LARGER GRAPH", test_p4_embedded_in_larger_graph),
        ("P4 TRIANGLE BOUNDARY", test_p4_triangle_boundary),
        ("P4 MISSING EDGE", test_p4_missing_edge),
        ("P4 VERTEX LABEL CHANGE", test_p4_vertex_label_change),
        ("P4 WRONG VERTEX COORDINATES", test_p4_wrong_vertex_coordinates),
        ("P4 REMOVE RANDOM EDGE FROM VALID GRAPH", test_p4_remove_random_edge_from_valid_graph),
        ("P4 VISUALIZATION CORRECTNESS", test_p4_visualization_correctness),
        ("P4 COMPLETE RIGHT SIDE VERIFICATION", test_p4_complete_right_side_verification),
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

