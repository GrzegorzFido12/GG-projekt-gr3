import os
from graph_model import Graph, Node, HyperEdge
from p0 import P0
from visualization import draw


OUTPUT_DIR = "visualizations"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def create_square_graph(x, y, size, prefix):
    g = Graph()
    
    nodes = [
        Node(x, y, f"{prefix}1"),
        Node(x + size, y, f"{prefix}2"),
        Node(x + size, y + size, f"{prefix}3"),
        Node(x, y + size, f"{prefix}4")
    ]
    
    for n in nodes:
        g.add_node(n)
    
    for i in range(4):
        next_i = (i + 1) % 4
        g.add_edge(HyperEdge((nodes[i], nodes[next_i]), "E", R=0, B=1))
    
    return g, nodes


def test_marking_unmarked_element():
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
    g, nodes = create_square_graph(1, 1, 3, "a")
    g.add_edge(HyperEdge(tuple(nodes), "Q", R=1))
    production = P0()
    
    result = g.apply(production)
    
    assert result == 0


def test_triangle():
    g = Graph()
    
    nodes = [
        Node(0, 0, "x1"),
        Node(2, 0, "x2"),
        Node(2, 2, "x3")
    ]
    
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
    
    assert result == 1
    
    q_edge = [e for e in g.hyperedges if e.hypertag == "Q"][0]
    assert q_edge.R == 1


def test_two_nodes_with_Q():
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
    
    assert result == 1
    
    q_edge_after = [e for e in g.hyperedges if e.hypertag == "Q"][0]
    assert q_edge_after.R == 1


def test_edge_attributes_preserved():
    g, nodes = create_square_graph(0, 0, 2, "n")
    
    e_edges_before = [
        (e.nodes, e.hypertag, e.R, e.B) 
        for e in g.hyperedges if e.hypertag == "E"
    ]
    
    g.add_edge(HyperEdge(tuple(nodes), "Q", R=0))
    
    production = P0()
    g.apply(production)
    
    e_edges_after = [
        (e.nodes, e.hypertag, e.R, e.B) 
        for e in g.hyperedges if e.hypertag == "E"
    ]
    
    assert len(e_edges_before) == len(e_edges_after)
    assert set(e_edges_before) == set(e_edges_after)


if __name__ == "__main__":
    
    tests = [
        ("MARKING UNMARKED ELEMENTS", test_marking_unmarked_element),
        ("MARKING ALREADY MARKED ELEMENTS", test_already_marked_element),
        ("TRIANGLE TEST", test_triangle),
        ("TWO NODES TEST", test_two_nodes_with_Q),
        ("ATTRIBUTES PRESERVED TEST", test_edge_attributes_preserved),
    ]
    
    passed = 0
    failed = 0
    
    for i, (name, test_func) in enumerate(tests, 1):
        print(f"\n{name}")
        try:
            test_func()
            print(f"PASSED")
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