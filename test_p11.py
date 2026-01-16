import math
import os
from graph_model import Graph, Node, HyperEdge
from p11v2 import P11
from visualization import draw

# --- Konfiguracja katalogu wyjściowego ---
OUTPUT_DIR = "visualizations"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_valid_hexagon(r_val=1, prefix="v"):
    """
    Creates a valid P11-compatible hexagon:
    - 6 corner nodes
    - 6 midpoint nodes
    - symmetric E edges
    - one S edge
    """
    g = Graph()

    corners = [
        Node(0, 0, f"{prefix}1"),
        Node(10, 0, f"{prefix}2"),
        Node(15, 8.66, f"{prefix}3"),
        Node(10, 17.32, f"{prefix}4"),
        Node(0, 17.32, f"{prefix}5"),
        Node(-5, 8.66, f"{prefix}6"),
    ]

    for n in corners:
        g.add_node(n)

    for i in range(6):
        c1 = corners[i]
        c2 = corners[(i + 1) % 6]
        m = Node((c1.x + c2.x) / 2, (c1.y + c2.y) / 2, f"m{i}_{prefix}")
        g.add_node(m)
        g.add_edge(HyperEdge((c1, m), "E", B=0))
        g.add_edge(HyperEdge((m, c2), "E", B=1))

    g.add_edge(HyperEdge(tuple(corners), "S", R=r_val))
    return g

def test_isomorphism():
    p11 = P11()

    g_ok = create_valid_hexagon(r_val=1)
    draw(g_ok, f"{OUTPUT_DIR}/t1_iso_ok.png")
    assert p11.is_isomorphic(g_ok)

    g_bad = create_valid_hexagon(r_val=1)
    g_bad.hyperedges[-1].hypertag = "X"
    draw(g_bad, f"{OUTPUT_DIR}/t1_iso_bad.png")
    assert not p11.is_isomorphic(g_bad)


# --- 2. Test decydowania o miejscu zastosowania (R=1 vs R=0) ---
def test_r_flag():
    p11 = P11()

    g0 = create_valid_hexagon(r_val=0)
    assert not p11.can_apply(g0)

    g1 = create_valid_hexagon(r_val=1)
    assert p11.can_apply(g1)


def test_subgraph_in_large_graph():
    g = Graph()

    noise1 = Node(50, 50, "noise1")
    noise2 = Node(60, 50, "noise2")
    g.add_node(noise1)
    g.add_node(noise2)
    g.add_edge(HyperEdge((noise1, noise2), "E", B=1))

    hexagon = create_valid_hexagon(r_val=1)
    for n in hexagon.nodes:
        g.add_node(n)
    for e in hexagon.hyperedges:
        g.add_edge(e)

    draw(g, f"{OUTPUT_DIR}/t3_large_before.png")

    p11 = P11()
    assert p11.can_apply(g)
    g.apply(p11)

    draw(g, f"{OUTPUT_DIR}/t3_large_after.png")

    assert len([e for e in g.hyperedges if e.hypertag == "Q"]) == 6


def test_result_correctness():
    g = create_valid_hexagon(r_val=1)
    p11 = P11()

    draw(g, f"{OUTPUT_DIR}/t4_before.png")
    g.apply(p11)
    draw(g, f"{OUTPUT_DIR}/t4_after.png")

    centers = [n for n in g.nodes if n.label == "v_center"]
    assert len(centers) == 1

    q_edges = [e for e in g.hyperedges if e.hypertag == "Q"]
    assert len(q_edges) == 6
    assert all(e.R == 0 for e in q_edges)


def test_irregular_geometry():
    g = Graph()

    corners = [
        Node(0, 0, "v1"),
        Node(12, 2, "v2"),
        Node(14, 8, "v3"),
        Node(10, 20, "v4"),
        Node(0, 15, "v5"),
        Node(-2, 6, "v6"),
    ]
    for n in corners:
        g.add_node(n)

    for i in range(6):
        c1 = corners[i]
        c2 = corners[(i + 1) % 6]
        m = Node((c1.x + c2.x) / 2, (c1.y + c2.y) / 2, f"m{i}")
        g.add_node(m)
        g.add_edge(HyperEdge((c1, m), "E", B=1))
        g.add_edge(HyperEdge((m, c2), "E", B=1))

    g.add_edge(HyperEdge(tuple(corners), "S", R=1))

    draw(g, f"{OUTPUT_DIR}/t5_irregular_before.png")
    g.apply(P11())
    draw(g, f"{OUTPUT_DIR}/t5_irregular_after.png")

    assert len([e for e in g.hyperedges if e.hypertag == "Q"]) == 6




def test_double_application():
    g = create_valid_hexagon(r_val=1)
    p11 = P11()

    assert p11.can_apply(g)
    g.apply(p11)

    assert not p11.can_apply(g)

def test_embedded_hexagon():
    g = create_valid_hexagon(r_val=1, prefix="c")

    # external connections
    for c in [n for n in g.nodes if n.label.startswith("c")]:
        ext = Node(c.x + 5, c.y + 5, f"ext_{c.label}")
        g.add_node(ext)
        g.add_edge(HyperEdge((c, ext), "E", B=1))

    draw(g, f"{OUTPUT_DIR}/t7_embedded_before.png")
    g.apply(P11())
    draw(g, f"{OUTPUT_DIR}/t7_embedded_after.png")

    assert len([e for e in g.hyperedges if e.hypertag == "Q"]) == 6



if __name__ == "__main__":
    test_isomorphism()
    test_r_flag()
    test_subgraph_in_large_graph()
    test_result_correctness()
    test_irregular_geometry()
    test_double_application()
    test_embedded_hexagon()
    print("ALL TESTS PASSED ✅")
