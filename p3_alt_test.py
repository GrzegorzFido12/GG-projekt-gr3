import os
from graph_model import Graph, Node, HyperEdge
from p3 import P3
from visualization import draw

OUTPUT_DIR = "visualizations"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_shared_edge_graph():
    """Creates a simple graph with a single shared edge marked for refinement."""
    g = Graph()
    n1 = Node(0, 0, "v1")
    n2 = Node(4, 0, "v2")
    g.add_node(n1)
    g.add_node(n2)
    # Shared edge (B=0) marked for refinement (R=1)
    g.add_edge(HyperEdge((n1, n2), "E", boundary=False, R=1, B=0))
    return g

def create_two_elements_shared_edge():
    """Creates two elements sharing a marked internal edge."""
    g = Graph()
    nodes = [
        Node(0, 4, "n1"), Node(4, 4, "n2"), Node(8, 4, "n3"),
        Node(0, 0, "n4"), Node(4, 0, "n5"), Node(8, 0, "n6")
    ]
    for n in nodes: g.add_node(n)
    
    # Shared interior edge between two quads
    g.add_edge(HyperEdge((nodes[1], nodes[4]), "E", boundary=False, R=1, B=0))
    
    # Boundary edges (unmarked)
    g.add_edge(HyperEdge((nodes[0], nodes[1]), "E", boundary=True, R=0, B=1))
    g.add_edge(HyperEdge((nodes[1], nodes[2]), "E", boundary=True, R=0, B=1))
    
    return g

# ============= TEST FUNCTIONS =============

def test_p3_basic_shared_edge():
    """Test P3 on a simple internal edge marked for refinement."""
    g = create_shared_edge_graph()
    draw(g, f"{OUTPUT_DIR}/test_p3_basic_before.png")
    
    production = P3()
    assert production.can_apply(g)
    result = g.apply(production)
    draw(g, f"{OUTPUT_DIR}/test_p3_basic_after.png")
    
    assert result == 1
    assert len(g.nodes) == 3 # 2 original + 1 hanging
    edges = [e for e in g.hyperedges if e.hypertag == "E"]
    assert len(edges) == 2
    for e in edges:
        assert e.R == 0
        assert e.B == 0

def test_p3_cannot_apply_to_boundary_edge():
    """Test that P3 cannot be applied to boundary (B=1) edges."""
    g = Graph()
    n1, n2 = Node(0,0,"v1"), Node(4,0,"v2")
    g.add_node(n1); g.add_node(n2)
    # Boundary edge (B=1) - P3 should ignore this
    g.add_edge(HyperEdge((n1, n2), "E", boundary=True, R=1, B=1))
    
    production = P3()
    assert not production.can_apply(g)

if __name__ == "__main__":
    test_p3_basic_shared_edge()
    test_p3_cannot_apply_to_boundary_edge()
    print("P3 Tests Passed")