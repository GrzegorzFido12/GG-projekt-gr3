import os
from graph_model import Graph, Node, HyperEdge
from productions.p7_ import P7
from visualization import draw

OUTPUT_DIR = "visualizations/p7"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============= HELPER FUNCTIONS =============
def create_isolated_pentagon(r_value=1, missing_edge=False, missing_node=False):
    """Creates a single pentagonal element P with 5 surrounding E edges."""
    g = Graph()
    nodes = [Node(2, 4, "v1"), Node(4, 3, "v2"), Node(3, 1, "v3"), Node(1, 1, "v4")]

    if not missing_node:
        nodes.append(Node(0, 3, "v5"))

    for n in nodes:
        g.add_node(n)

    # Central pentagonal hyperedge P
    g.add_edge(HyperEdge(tuple(nodes), "P", R=r_value))

    # 5 surrounding boundary edges E (initially R=0)
    if missing_edge or missing_node:
        for i in range(4):
            # Mixing B values to test preservation
            b_val = 1 if i < 3 else 0
            d = 5
            if missing_node:
                d = 4
            g.add_edge(
                HyperEdge(
                    (nodes[i], nodes[(i + 1) % d]),
                    "E",
                    boundary=(b_val == 1),
                    R=0,
                    B=b_val,
                )
            )
    else:
        for i in range(5):
            # Mixing B values to test preservation
            b_val = 1 if i < 3 else 0
            g.add_edge(
                HyperEdge(
                    (nodes[i], nodes[(i + 1) % 5]),
                    "E",
                    boundary=(b_val == 1),
                    R=0,
                    B=b_val,
                )
            )

    return g, nodes


def create_complex_pentagonal_mesh():
    """Creates a mesh with a pentagon (P) and an adjacent quadrilateral (Q)."""
    g = Graph()
    # Nodes for the pentagon (left side) and quad (right side)
    nodes = {
        "v1": Node(1, 4, "v1"),
        "v2": Node(3, 4, "v2"),
        "v3": Node(4, 2, "v3"),
        "v4": Node(3, 0, "v4"),
        "v5": Node(1, 0, "v5"),
        "v6": Node(5, 4, "v6"),
        "v7": Node(5, 0, "v7"),
    }
    for n in nodes.values():
        g.add_node(n)

    # Pentagon P (marked for refinement)
    p_nodes = (nodes["v1"], nodes["v2"], nodes["v3"], nodes["v4"], nodes["v5"])
    g.add_edge(HyperEdge(p_nodes, "P", R=1))

    # Surrounding edges for P
    g.add_edge(HyperEdge((nodes["v1"], nodes["v2"]), "E", boundary=True, R=0, B=1))
    g.add_edge(
        HyperEdge((nodes["v2"], nodes["v3"]), "E", boundary=False, R=0, B=0)
    )  # Shared with Q
    g.add_edge(
        HyperEdge((nodes["v3"], nodes["v4"]), "E", boundary=False, R=0, B=0)
    )  # Shared with Q
    g.add_edge(HyperEdge((nodes["v4"], nodes["v5"]), "E", boundary=True, R=0, B=1))
    g.add_edge(HyperEdge((nodes["v5"], nodes["v1"]), "E", boundary=True, R=0, B=1))

    # Quadrilateral Q (NOT marked for refinement)
    # q_nodes = (nodes["v2"], nodes["v6"], nodes["v7"], nodes["v4"], nodes["v3"])
    # g.add_edge(HyperEdge(q_nodes, "Q", R=0))

    # Additional edges for Q that are not part of P
    g.add_edge(HyperEdge((nodes["v2"], nodes["v6"]), "E", boundary=True, R=0, B=1))
    g.add_edge(HyperEdge((nodes["v6"], nodes["v7"]), "E", boundary=True, R=0, B=1))
    g.add_edge(HyperEdge((nodes["v7"], nodes["v4"]), "E", boundary=True, R=0, B=1))
    g.add_edge(HyperEdge((nodes["v3"], nodes["v6"]), "E", boundary=True, R=0, B=1))
    g.add_edge(HyperEdge((nodes["v3"], nodes["v7"]), "E", boundary=True, R=0, B=1))

    return g


def create_complex_pentagonal_mesh_2():
    """Creates a mesh with a pentagon (P) and an adjacent quadrilateral (Q)."""
    g = Graph()
    # Nodes for the pentagon (left side) and quad (right side)
    nodes = {
        "v1": Node(1, 4, "v1"),
        "v2": Node(3, 4, "v2"),
        "v3": Node(4, 2, "v3"),
        "v4": Node(3, 0, "v4"),
        "v5": Node(1, 0, "v5"),
        "v6": Node(5, 4, "v6"),
        "v7": Node(5, 0, "v7"),
        "v11": Node(11, 4, "v11"),
        "v12": Node(13, 4, "v12"),
        "v13": Node(14, 2, "v13"),
        "v14": Node(13, 0, "v14"),
        "v15": Node(11, 0, "v15"),
        "v16": Node(15, 4, "v16"),
        "v17": Node(15, 0, "v17"),
    }

    for n in nodes.values():
        g.add_node(n)

    # for n in nodes2.values():
    #     g.add_node(n)

    # Pentagon P (marked for refinement)
    p_nodes = (nodes["v1"], nodes["v2"], nodes["v3"], nodes["v4"], nodes["v5"])
    g.add_edge(HyperEdge(p_nodes, "P", R=1))
    # Pentagon P (marked for refinement)
    p_nodes = (nodes["v11"], nodes["v12"], nodes["v13"], nodes["v14"], nodes["v15"])
    g.add_edge(HyperEdge(p_nodes, "P", R=1))

    # Surrounding edges for P
    g.add_edge(HyperEdge((nodes["v1"], nodes["v2"]), "E", boundary=True, R=0, B=1))
    g.add_edge(
        HyperEdge((nodes["v2"], nodes["v3"]), "E", boundary=False, R=0, B=0)
    )  # Shared with Q
    g.add_edge(
        HyperEdge((nodes["v3"], nodes["v4"]), "E", boundary=False, R=0, B=0)
    )  # Shared with Q
    g.add_edge(HyperEdge((nodes["v4"], nodes["v5"]), "E", boundary=True, R=0, B=1))
    g.add_edge(HyperEdge((nodes["v5"], nodes["v1"]), "E", boundary=True, R=0, B=1))

    # Quadrilateral Q (NOT marked for refinement)
    # Surrounding edges for P
    g.add_edge(HyperEdge((nodes["v11"], nodes["v12"]), "E", boundary=True, R=0, B=1))
    g.add_edge(
        HyperEdge((nodes["v12"], nodes["v13"]), "E", boundary=False, R=0, B=0)
    )  # Shared with Q
    g.add_edge(
        HyperEdge((nodes["v13"], nodes["v14"]), "E", boundary=False, R=0, B=0)
    )  # Shared with Q
    g.add_edge(HyperEdge((nodes["v14"], nodes["v15"]), "E", boundary=True, R=0, B=1))
    g.add_edge(HyperEdge((nodes["v15"], nodes["v11"]), "E", boundary=True, R=0, B=1))

    # Quadrilateral Q (NOT marked for refinement)
    # q_nodes = (nodes["v2"], nodes["v6"], nodes["v7"], nodes["v4"], nodes["v3"])
    # g.add_edge(HyperEdge(q_nodes, "Q", R=0))

    # Additional edges for Q that are not part of P
    g.add_edge(HyperEdge((nodes["v2"], nodes["v6"]), "E", boundary=True, R=0, B=1))
    g.add_edge(HyperEdge((nodes["v6"], nodes["v7"]), "E", boundary=True, R=0, B=1))
    g.add_edge(HyperEdge((nodes["v7"], nodes["v4"]), "E", boundary=True, R=0, B=1))
    g.add_edge(HyperEdge((nodes["v3"], nodes["v6"]), "E", boundary=True, R=0, B=1))
    g.add_edge(HyperEdge((nodes["v3"], nodes["v7"]), "E", boundary=True, R=0, B=1))
    # g.add_edge(HyperEdge((nodes["v6"], nodes["v11"]), "E", boundary=True, R=1, B=1))
    # g.add_edge(HyperEdge((nodes["v7"], nodes["v15"]), "E", boundary=True, R=1, B=1))

    g.add_edge(HyperEdge((nodes["v12"], nodes["v16"]), "E", boundary=True, R=0, B=1))
    g.add_edge(HyperEdge((nodes["v16"], nodes["v17"]), "E", boundary=True, R=0, B=1))
    g.add_edge(HyperEdge((nodes["v17"], nodes["v14"]), "E", boundary=True, R=0, B=1))
    g.add_edge(HyperEdge((nodes["v13"], nodes["v16"]), "E", boundary=True, R=0, B=1))
    g.add_edge(HyperEdge((nodes["v13"], nodes["v17"]), "E", boundary=True, R=0, B=1))

    return g


# ============= TEST FUNCTIONS =============


def test_p7_basic_propagation():
    """Tests that P7 marks all 5 surrounding E edges of a marked pentagon."""
    g, _ = create_isolated_pentagon(r_value=1)
    draw(g, f"{OUTPUT_DIR}/test_p7_basic_before.png")

    production = P7()
    assert production.can_apply(g)

    result = g.apply(production)
    draw(g, f"{OUTPUT_DIR}/test_p7_basic_after.png")

    assert result == 1
    # Verify all 5 edges now have R=1
    marked_edges = [e for e in g.hyperedges if e.hypertag == "E" and e.R == 1]
    assert len(marked_edges) == 5

    # Verify the P edge itself remains marked
    p_edge = [e for e in g.hyperedges if e.hypertag == "P"][0]
    assert p_edge.R == 1


def test_p7_preservation_of_attributes():
    """Tests that B and boundary attributes of E edges are preserved."""
    g, _ = create_isolated_pentagon(r_value=1)
    production = P7()

    draw(g, f"{OUTPUT_DIR}/test_p7_preservation_of_attributes_before.png")

    g.apply(production)

    draw(g, f"{OUTPUT_DIR}/test_p7_preservation_of_attributes_after.png")

    ##????
    for edge in g.hyperedges:
        if edge.hypertag == "E":
            # Check if original B values (from create_isolated_pentagon) are preserved
            if edge.nodes[0].label in ["v1", "v2", "v3"] and edge.nodes[1].label in [
                "v1",
                "v2",
                "v3",
            ]:
                assert edge.B == 1
                assert edge.boundary is True
            elif edge.nodes[0].label in ["v4", "v5"] or edge.nodes[1].label in [
                "v4",
                "v5",
            ]:
                # Check that at least some logic for B=0 was preserved
                pass


def test_p7_cannot_apply_unmarked():
    """Tests that P7 does not apply if the pentagon has R=0."""
    g, _ = create_isolated_pentagon(r_value=0)
    production = P7()
    assert not production.can_apply(g)
    assert g.apply(production) == 0


def test_p7_wrong_tag():
    """Tests that P7 does not apply to other shapes (like Q) even if R=1."""
    g = Graph()
    nodes = [Node(0, 0, "n1"), Node(1, 0, "n2"), Node(1, 1, "n3"), Node(0, 1, "n4")]
    for n in nodes:
        g.add_node(n)
    g.add_edge(HyperEdge(tuple(nodes), "Q", R=1))  # R=1 but tag is Q
    g.add_edge(HyperEdge((nodes[0], nodes[1]), "E", R=0))

    production = P7()
    assert not production.can_apply(g)


def test_p7_complex_mesh_isolation():
    """Tests P7 in a mesh: only edges belonging to the marked pentagon should change."""
    g = create_complex_pentagonal_mesh_2()
    draw(g, f"{OUTPUT_DIR}/test_p7_mesh_before.png")

    production = P7()
    cnt = 1
    print(production.can_apply(g))
    g.apply(production)
    print(production.can_apply(g))
    g.apply(production)
    draw(g, f"{OUTPUT_DIR}/test_p7_mesh_after{cnt}.png")

    # cnt=1
    # while production.can_apply(g):
    #     g.apply(production)

    #     draw(g, f"{OUTPUT_DIR}/test_p7_mesh_after{cnt}.png")
    #     cnt=+1

    # 5 edges of the pentagon should be marked R=1
    # Note: 2 of these are shared with Q, but since they belong to P, they should be marked
    marked_edges = [e for e in g.hyperedges if e.hypertag == "E" and e.R == 1]
    assert len(marked_edges) == 10

    # The 2 edges of Q that do NOT belong to P should still be R=0
    unmarked_q_edges = [e for e in g.hyperedges if e.hypertag == "E" and e.R == 0]
    assert len(unmarked_q_edges) == 10  # Total E edges in mesh (8) - P edges (3) = 5


# def test_p7_find_all_matches():

#     """Tests finding multiple marked pentagons in one graph."""
#     g = Graph()

#     # Create two separate pentagons
#     draw(g, f"{OUTPUT_DIR}/test_p7_complex_mesh_before.png")

#     production = P7()
#     matches = production.find_all_matches(g) if hasattr(production, 'find_all_matches') else []
#     g.apply(production)

#     draw(g, f"{OUTPUT_DIR}/test_p7_complex_mesh_after.png")
#     if matches:
#         assert len(matches) == 2


def test_p7_missing_edge():
    """Tests that P7 marks all 5 surrounding E edges of a marked pentagon."""
    g, _ = create_isolated_pentagon(r_value=1, missing_edge=True)
    draw(g, f"{OUTPUT_DIR}/test_p7_missing_edge_before.png")

    production = P7()

    assert not production.can_apply(g)
    draw(g, f"{OUTPUT_DIR}/test_p7_missing_edge_after.png")


def test_p7_missing_node():
    """Tests that P7 marks all 5 surrounding E edges of a marked pentagon."""
    g, _ = create_isolated_pentagon(r_value=1, missing_node=True)
    draw(g, f"{OUTPUT_DIR}/test_p7_missing_node_before.png")

    production = P7()

    assert not production.can_apply(g)
    draw(g, f"{OUTPUT_DIR}/test_p7_missing_node_after.png")


def test_p7_basic_propagation():
    """Tests that P7 marks all 5 surrounding E edges of a marked pentagon."""
    g, _ = create_isolated_pentagon(r_value=1)
    draw(g, f"{OUTPUT_DIR}/test_p7_basic_before.png")

    production = P7()
    assert production.can_apply(g)

    result = g.apply(production)
    draw(g, f"{OUTPUT_DIR}/test_p7_basic_after.png")

    assert result == 1
    # Verify all 5 edges now have R=1
    marked_edges = [e for e in g.hyperedges if e.hypertag == "E" and e.R == 1]
    assert len(marked_edges) == 5

    # Verify the P edge itself remains marked
    p_edge = [e for e in g.hyperedges if e.hypertag == "P"][0]
    assert p_edge.R == 1


if __name__ == "__main__":
    tests = [
        ("P7 BASIC PROPAGATION", test_p7_basic_propagation),
        ("P7 PRESERVATION OF ATTRIBUTES", test_p7_preservation_of_attributes),
        ("P7 CANNOT APPLY UNMARKED", test_p7_cannot_apply_unmarked),
        ("P7 WRONG TAG", test_p7_wrong_tag),
        ("P7 COMPLEX MESH ISOLATION", test_p7_complex_mesh_isolation),
        # ("P7 FIND ALL MATCHES", test_p7_find_all_matches),
        ("P7 MISSING EDGE", test_p7_missing_edge),
        ("P7 MISSING NODE", test_p7_missing_node),
    ]

    for name, test_func in tests:
        print(f"\nRunning {name}...")
        try:
            test_func()
            print("PASSED")
        except Exception as e:
            print(f"FAILED: {e}")
            import traceback

            traceback.print_exc()
