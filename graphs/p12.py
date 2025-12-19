import math
import os
import copy
from visualization import draw
from production_base import Production
from productions.p12 import P12
from graph_model import Graph, Node, HyperEdge

def make_septagon():
    prod = P12()
    return prod.get_left_side()

def create_lhs_septagon():
    """
    Poprawny graf izomorficzny z LHS produkcji P12 (septagon z 7 węzłami i krawędziami E).
    Wierzchołki ustawione w okręgu.
    """
    g = Graph()
    n_nodes = 7
    radius = 1.0
    nodes = []

    for i in range(n_nodes):
        angle = 2 * math.pi * i / n_nodes
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        node = Node(x=x, y=y, label=f"v{i}")
        nodes.append(node)
        g.add_node(node)

    # Hiperkrawędź Q
    q = HyperEdge(tuple(nodes), hypertag="Q", R=0, B=0)
    g.add_edge(q)

    # Hiperkrawędzie E (cycle)
    for i in range(n_nodes):
        e = HyperEdge((nodes[i], nodes[(i + 1) % n_nodes]), hypertag="E", B=1)
        g.add_edge(e)

    return g


def create_containing_graph():
    """
    Większy graf zawierający septagon LHS jako podgraf.
    Dodatkowe węzły są połączone z septagonem, aby graf był spójny.
    """
    g = create_lhs_septagon()
    septagon_nodes = g.nodes[:7]  # pierwsze 7 węzłów to septagon

    # Dodajemy dodatkowe węzły
    extra_nodes = [Node(x=2.0, y=0, label="extra1"),
                   Node(x=2.0, y=2.0, label="extra2")]
    for n in extra_nodes:
        g.add_node(n)

    # Tworzymy spójne połączenia między nowymi węzłami a septagonem
    g.add_edge(HyperEdge((extra_nodes[0], septagon_nodes[0]), hypertag="E", B=0))
    g.add_edge(HyperEdge((extra_nodes[1], septagon_nodes[3]), hypertag="E", B=0))

    # Połączenie między nowymi węzłami
    g.add_edge(HyperEdge((extra_nodes[0], extra_nodes[1]), hypertag="E", B=0))

    return g


def create_missing_vertex_graph():
    """
    Graf izomorficzny z LHS, ale bez jednego wierzchołka.
    """
    g = create_lhs_septagon()
    if g.nodes:
        g.remove_node(g.nodes[0])
    return g

def create_missing_edge_graph():
    """
    Graf izomorficzny z LHS, ale bez jednej krawędzi E.
    """
    g = create_lhs_septagon()
    e_edges = [e for e in g.hyperedges if e.hypertag == "E"]
    if e_edges:
        g.remove_edge(e_edges[0])
    return g

def create_wrong_label_graph():
    """
    Graf izomorficzny z LHS, ale zmienia etykietę jednego węzła.
    """
    g = create_lhs_septagon()
    if g.nodes:
        g.nodes[0].label = "wrong_label"
    return g

def create_wrong_coordinates_graph():
    """
    Graf izomorficzny z LHS, ale zmienia współrzędne jednego węzła.
    """
    g = create_lhs_septagon()
    g.nodes[0].x += 0.5
    g.nodes[0].y += 0.5

    return g

def create_all_test_graphs():
    """
    Zwraca listę wszystkich sześciu grafów testowych:
    1. Poprawny LHS
    2. LHS jako podgraf większego grafu
    3. LHS bez wierzchołka
    4. LHS bez krawędzi
    5. LHS z niepoprawną etykietą
    6. LHS z niepoprawnymi współrzędnymi
    """
    return [
        create_lhs_septagon(),
        create_containing_graph(),
        create_missing_vertex_graph(),
        create_missing_edge_graph(),
        create_wrong_label_graph(),
        create_wrong_coordinates_graph()
    ]

def draw_graph_before_after(graph: Graph, production: Production, output_dir: str, prefix: str = "p12"):
    """
    Rysuje graf przed i po zastosowaniu produkcji.
    Zapisuje dwa obrazy do output_dir:
      prefix_before.png
      prefix_after.png
    """

    os.makedirs(output_dir, exist_ok=True)

    # Rysuj graf przed zastosowaniem produkcji
    before_path = os.path.join(output_dir, f"{prefix}_before.png")
    draw(graph, before_path)
    print(f"Saved before-application graph: {before_path}")

    # Zastosuj produkcję na kopii grafu
    graph_after = copy.deepcopy(graph)
    graph_after.apply(production)

    # Rysuj graf po zastosowaniu produkcji
    after_path = os.path.join(output_dir, f"{prefix}_after.png")
    draw(graph_after, after_path)
    print(f"Saved after-application graph: {after_path}")

if __name__ == "__main__":

    out_dir = "../productions/visualizations/p12_visualizations"
    graphs = create_all_test_graphs()
    prod = P12()

    for i, g in enumerate(graphs):
        print(f"Graph {i}: {len(g.nodes)} nodes, {len(g.hyperedges)} hyperedges")
        draw_graph_before_after(g, prod, out_dir, prefix=f"test_{i}")
