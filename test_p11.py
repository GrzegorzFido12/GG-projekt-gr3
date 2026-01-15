import math
import os
from graph_model import Graph, Node, HyperEdge
from p11 import P11
from visualization import draw

# --- Konfiguracja katalogu wyjściowego ---
OUTPUT_DIR = "visualizations"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Funkcja pomocnicza do tworzenia poprawnego grafu wejściowego ---
def create_valid_input_graph(r_val=1):
    """Tworzy sześciokąt z wiszącymi węzłami (odpowiednik lewej strony P11)."""
    g = Graph()
    corners = [
        Node(0, 0, "v1"), Node(10, 0, "v2"), Node(15, 8.66, "v3"),
        Node(10, 17.32, "v4"), Node(0, 17.32, "v5"), Node(-5, 8.66, "v6"),
    ]
    for n in corners: g.add_node(n)

    # Tworzenie wiszących węzłów i krawędzi brzegowych
    num_corners = len(corners)
    for i in range(num_corners):
        c_curr = corners[i]
        c_next = corners[(i + 1) % num_corners]
        mid_x = (c_curr.x + c_next.x) / 2
        mid_y = (c_curr.y + c_next.y) / 2
        h_node = Node(mid_x, mid_y, f"h_{i}", hanging=True)
        g.add_node(h_node)
        g.add_edge(HyperEdge((c_curr, h_node), "E", boundary=True, R=0, B=1))
        g.add_edge(HyperEdge((h_node, c_next), "E", boundary=True, R=0, B=1))

    # Krawędź główna S
    g.add_edge(HyperEdge(tuple(corners), "S", R=r_val))
    return g

# --- 1. Test sprawdzania izomorfizmu (LHS vs Graf) ---
def test_isomorphism_check():
    """
    Sprawdza, czy metoda is_isomorphic poprawnie identyfikuje graf pasujący do lewej strony produkcji.
    """
    print("  > Generowanie wizualizacji dla testu izomorfizmu...")
    p11 = P11()

    # Przypadek Pozytywny: Graf idealnie pasujący
    valid_graph = create_valid_input_graph(r_val=1)
    draw(valid_graph, f"{OUTPUT_DIR}/test_p11_isomorphism_check__before.png")
    assert p11.is_isomorphic(valid_graph) is True, \
        "Graf powinien być izomorficzny z lewą stroną produkcji."

    # Przypadek Negatywny 1: Brak węzła wiszącego (inna topologia)
    broken_graph = create_valid_input_graph(r_val=1)
    h_node = next(n for n in broken_graph.nodes if n.hanging)

    # FIX: Najpierw usuwamy krawędzie powiązane z węzłem, potem węzeł
    edges_to_remove = [e for e in broken_graph.hyperedges if h_node in e.nodes]
    for e in edges_to_remove:
        broken_graph.remove_edge(e)

    broken_graph.remove_node(h_node)

    draw(broken_graph, f"{OUTPUT_DIR}/test_p11_isomorphism_check__broken_topology.png")
    assert p11.is_isomorphic(broken_graph) is False, \
        "Graf z usuniętym węzłem wiszącym NIE powinien być izomorficzny."

    # Przypadek Negatywny 2: Zła etykieta krawędzi (S -> X)
    wrong_label_graph = create_valid_input_graph(r_val=1)
    s_edge = next(e for e in wrong_label_graph.hyperedges if e.hypertag == 'S')
    s_edge.hypertag = "X"

    draw(wrong_label_graph, f"{OUTPUT_DIR}/test_p11_isomorphism_check__wrong_label.png")
    assert p11.is_isomorphic(wrong_label_graph) is False, \
        "Graf z inną etykietą krawędzi głównej NIE powinien być izomorficzny."

# --- 2. Test decydowania o miejscu zastosowania (R=1 vs R=0) ---
def test_location_decision_based_on_R():
    """
    Sprawdza, na jakiej podstawie decydujemy, gdzie stosować produkcję.
    """
    print("  > Generowanie wizualizacji dla testu flagi R...")
    p11 = P11()

    # Graf z R=0 (nie powinien pasować)
    graph_r0 = create_valid_input_graph(r_val=0)
    draw(graph_r0, f"{OUTPUT_DIR}/test_p11_location_decision_based_on_R__R0_ignored.png")
    assert p11.find_match(graph_r0) is None, \
        "Produkcja nie powinna zostać zastosowana w miejscu, gdzie R=0."

    # Graf z R=1 (powinien pasować)
    graph_r1 = create_valid_input_graph(r_val=1)
    draw(graph_r1, f"{OUTPUT_DIR}/test_p11_location_decision_based_on_R__R1_matched.png")
    match = p11.find_match(graph_r1)
    assert match is not None, \
        "Produkcja powinna znaleźć dopasowanie tam, gdzie R=1."
    assert match.hypertag == "S" and match.R == 1

# --- 3. Test wyszukiwania podgrafu w dużym grafie ---
def test_finding_subgraph_in_large_graph():
    """
    Sprawdza wyszukiwanie izomorficznego podgrafu w większej strukturze.
    """
    print("  > Generowanie wizualizacji dla testu dużego grafu...")
    large_graph = Graph()

    # Dodajemy "szum"
    noise_node1 = Node(25, 25, "noise1")
    noise_node2 = Node(30, 30, "noise2")
    large_graph.add_node(noise_node1)
    large_graph.add_node(noise_node2)
    large_graph.add_edge(HyperEdge((noise_node1, noise_node2), "E", B=1))

    # Dodajemy poprawny sześciokąt
    valid_subgraph = create_valid_input_graph(r_val=1)
    for node in valid_subgraph.nodes:
        large_graph.add_node(node)
    for edge in valid_subgraph.hyperedges:
        large_graph.add_edge(edge)

    draw(large_graph, f"{OUTPUT_DIR}/test_p11_finding_subgraph_in_large_graph__before.png")

    p11 = P11()
    match = p11.find_match(large_graph)

    assert match is not None, "Powinno znaleźć podgraf w dużym grafie."
    assert len(match.nodes) >= 6
    matched_labels = [n.label for n in match.nodes]
    assert "noise1" not in matched_labels

# --- 4. Test poprawności wyniku (Post-conditions) ---
def test_result_correctness():
    """
    Sprawdza poprawność transformacji (przed -> po).
    """
    print("  > Generowanie wizualizacji dla testu poprawności wyniku...")
    graph = create_valid_input_graph(r_val=1)
    p11 = P11()

    # Wizualizacja PRZED
    draw(graph, f"{OUTPUT_DIR}/test_p11_result_correctness__before.png")

    # Aplikacja produkcji
    graph.apply(p11)

    # Wizualizacja PO
    draw(graph, f"{OUTPUT_DIR}/test_p11_result_correctness__after.png")

    # Weryfikacje
    centers = [n for n in graph.nodes if n.label == "v_center"]
    assert len(centers) == 1, "Musi powstać dokładnie jeden węzeł centralny."

    hanging_now = [n for n in graph.nodes if getattr(n, 'hanging', False)]
    assert len(hanging_now) == 0, "Po produkcji P11 nie powinno być wiszących węzłów."

    q_edges = [e for e in graph.hyperedges if e.hypertag == "Q"]
    assert len(q_edges) == 6, "Graf wynikowy musi składać się z 6 elementów czworokątnych (Q)."

    assert all(q.R == 0 for q in q_edges), "Nowe elementy Q powinny mieć R=0."

def test_p11_irregular_geometry():
    """Tests if P11 handles a topologically valid but geometrically distorted hexagon."""
    print("Running test_p11_irregular_geometry...")
    g = Graph()
    
    # Define a "Squashed" Hexagon
    corners = [
        Node(0, 0, "v1"), 
        Node(12, 2, "v2"),   # Slightly up
        Node(14, 8, "v3"),   # Narrower
        Node(10, 20, "v4"),  # Stretched up
        Node(0, 15, "v5"), 
        Node(-2, 6, "v6"),   # Bulging left
    ]
    for n in corners: g.add_node(n)

    # Automatically generate midpoints to ensure they are mathematically correct for the test
    for i in range(6):
        c1 = corners[i]
        c2 = corners[(i + 1) % 6]
        h = Node((c1.x+c2.x)/2, (c1.y+c2.y)/2, f"h{i}", hanging=True)
        g.add_node(h)
        g.add_edge(HyperEdge((c1, h), "E", B=1))
        g.add_edge(HyperEdge((h, c2), "E", B=1))

    g.add_edge(HyperEdge(tuple(corners), "S", R=1))

    # Visualization BEFORE
    draw(g, f"{OUTPUT_DIR}/test_p11_irregular_geometry_before.png")

    p11 = P11()
    assert p11.can_apply(g), "P11 should apply to irregular polygons if topology is correct."
    
    g.apply(p11)

    # Visualization AFTER
    draw(g, f"{OUTPUT_DIR}/test_p11_irregular_geometry_after.png")
    
    # Verify we still get 6 Q elements
    assert len([e for e in g.hyperedges if e.hypertag == "Q"]) == 6

def test_p11_missing_hanging_flag():
    """Tests that P11 rejects a graph if a midpoint node is not marked 'hanging'."""
    print("Running test_p11_missing_hanging_flag...")
    g = create_valid_input_graph(r_val=1)
    
    # Find a hanging node and remove the hanging flag
    h_node = next(n for n in g.nodes if n.hanging)
    h_node.hanging = False # Simulating a fixed node
    
    # Visualization BEFORE (Should look normal, but internally different)
    draw(g, f"{OUTPUT_DIR}/test_p11_missing_hanging_flag_before.png")
    
    p11 = P11()
    assert not p11.can_apply(g), "P11 should NOT apply if a boundary midpoint is not a hanging node."
    
    # Visualization AFTER (Should be identical to before)
    draw(g, f"{OUTPUT_DIR}/test_p11_missing_hanging_flag_after.png")

def test_p11_disconnected_hanging_node():
    """Tests that P11 rejects a graph if the hanging node is geometrically correct but not connected."""
    print("Running test_p11_disconnected_hanging_node...")
    g = create_valid_input_graph(r_val=1)
    
    # Get a hanging node
    h_node = next(n for n in g.nodes if n.label == "h_0")
    
    # Remove the edges connecting to this hanging node
    edges_to_remove = [e for e in g.hyperedges if h_node in e.nodes]
    for e in edges_to_remove:
        g.remove_edge(e)
        
    # Add a direct edge between corners (skipping the hanging node)
    # This creates a topology mismatch even though h_node exists at the correct coordinates
    c1 = next(n for n in g.nodes if n.label == "v1")
    c2 = next(n for n in g.nodes if n.label == "v2")
    g.add_edge(HyperEdge((c1, c2), "E", B=1))
    
    draw(g, f"{OUTPUT_DIR}/test_p11_disconnected_hanging_node_before.png")
    
    p11 = P11()
    assert not p11.can_apply(g), "P11 should NOT apply if the hanging node is not part of the boundary edge."
    
    draw(g, f"{OUTPUT_DIR}/test_p11_disconnected_hanging_node_after.png")

def test_p11_double_application():
    """Tests that P11 cannot be applied twice to the same element immediately."""
    print("Running test_p11_double_application...")
    g = create_valid_input_graph(r_val=1)
    p11 = P11()
    
    draw(g, f"{OUTPUT_DIR}/test_p11_double_application_before.png")
    
    # First application
    assert p11.can_apply(g)
    g.apply(p11)
    
    draw(g, f"{OUTPUT_DIR}/test_p11_double_application_step1.png")
    
    # Second application check
    # P11 looks for "S" with R=1. The result of P11 produces "Q" with R=0.
    # Therefore, it should not find a match.
    assert not p11.can_apply(g), "P11 should not be applicable to its own result (Q elements)."
    
    draw(g, f"{OUTPUT_DIR}/test_p11_double_application_after.png")

if __name__ == "__main__":
    try:
        test_isomorphism_check()
        print("Test 1 (Izomorfizm): PASSED")
        
        test_location_decision_based_on_R()
        print("Test 2 (Lokalizacja): PASSED")
        
        test_finding_subgraph_in_large_graph()
        print("Test 3 (Wyszukiwanie): PASSED")
        
        test_result_correctness()
        print("Test 4 (Poprawność wyniku): PASSED")
        
        test_p11_disconnected_hanging_node()
        print("Test 5 (Rozłączny węzeł wiszący): PASSED")

        test_p11_missing_hanging_flag()
        print("Test 6 (Brak flagi wiszącej): PASSED")

        test_p11_irregular_geometry()
        print("Test 7 (Nieregularna geometria): PASSED")

        test_p11_double_application()
        print("Test 8 (Podwójne zastosowanie): PASSED")
        
    except AssertionError as e:
        print(f"FAILED: {e}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"CRITICAL ERROR: {e}")