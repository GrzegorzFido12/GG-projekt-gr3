import os

from graph_model import Graph, Node, HyperEdge
from productions.p0 import P0
from productions.p1 import P1
from productions.p10 import P10
from productions.p11 import P11
from productions.p2 import P2
from productions.p3 import P3
from productions.p4 import P4
from productions.p5 import P5
from productions.p9 import P9
from visualization import draw

OUTPUT_DIR = "../../visualizations/wywod3"
os.makedirs(OUTPUT_DIR, exist_ok=True)
step = 0
chosen_point = Node(7, 0.75, "X")


def create_starting_graph():
    global chosen_point
    g = Graph()
    v1 = Node(0, 0.75, "v1")
    v2 = Node(0, 2.25, "v2")
    v3 = Node(1, 3, "v3")
    v4 = Node(1.5, 2.25, "v4")
    v5 = Node(1.5, 0.75, "v5")
    v6 = Node(1, 0, "v6")
    # v7 = Node(12, 2, "v7")
    v8 = Node(7, 2.25, "v8")
    v9 = Node(8.5, 3, "v9")
    v10 = Node(10, 2.25, "v10")
    v11 = Node(10, 0.75, "v11")
    v12 = Node(8.5, 0, "v12")
    nodes = [v1, v2, v3, v4, v5, v6, chosen_point, v8, v9, v10, v11, v12]
    for node in nodes:
        g.add_node(node)

    g.add_edge(HyperEdge((v1, v2), "E", boundary=True))
    g.add_edge(HyperEdge((v1, v6), "E", boundary=True))
    g.add_edge(HyperEdge((v2, v3), "E", boundary=True))
    g.add_edge(HyperEdge((v6, v5), "E"))
    g.add_edge(HyperEdge((v3, v4), "E"))
    g.add_edge(HyperEdge((v5, v4), "E"))
    g.add_edge(HyperEdge((v5, chosen_point), "E"))
    g.add_edge(HyperEdge((v4, v8), "E"))
    g.add_edge(HyperEdge((chosen_point, v8), "E"))
    g.add_edge(HyperEdge((v6, v12), "E", boundary=True, B=1))
    g.add_edge(HyperEdge((v3, v9), "E", boundary=True))
    g.add_edge(HyperEdge((chosen_point, v12), "E"))
    g.add_edge(HyperEdge((v8, v9), "E"))
    g.add_edge(HyperEdge((v12, v11), "E", boundary=True, B=1))
    g.add_edge(HyperEdge((v9, v10), "E", boundary=True, B=1))
    g.add_edge(HyperEdge((v10, v11), "E", boundary=True, B=1))
    g.add_edge(HyperEdge((v4, v5, chosen_point, v8), "Q"))
    g.add_edge(HyperEdge((v5, v6, chosen_point, v12), "Q"))
    g.add_edge(HyperEdge((v3, v4, v8, v9), "Q"))
    g.add_edge(HyperEdge((v1, v2, v3, v4, v5, v6), "S"))
    g.add_edge(HyperEdge((chosen_point, v8, v9, v10, v11, v12), "S"))
    print("<Starting_graph>")
    draw(g, f"{OUTPUT_DIR}/starting_graph.png")
    print("-------------------")
    return g


def apply_and_draw_production(graph, production):
    global step
    graph.apply(production)
    print(production)
    draw(g, f"{OUTPUT_DIR}/graph_after_{step}_step.png")
    print("-------------------")
    step += 1


def has_node(graph):
    global chosen_point
    nodes = graph.nodes
    for node in nodes:
        if node == chosen_point or (node.x == chosen_point.x and node.y == chosen_point.y):
            return True
    return False


def choose_with_point(graph, production):
    global step
    graph.apply_with_point(production, chosen_point)
    print(production)
    draw(g, f"{OUTPUT_DIR}/graph_after_{step}_step.png")
    print("-------------------")
    step += 1


def choose_rectangle_with_point(graph, production):
    global step
    graph.apply_rectangle_with_point(production, chosen_point)
    print(production)
    draw(g, f"{OUTPUT_DIR}/graph_after_{step}_step.png")
    print("-------------------")
    step += 1


def make_disquisition(g):
    choose_with_point(g, P0())
    choose_with_point(g, P9())
    apply_and_draw_production(g, P1())
    apply_and_draw_production(g, P4())
    apply_and_draw_production(g, P3())
    apply_and_draw_production(g, P3())
    apply_and_draw_production(g, P3())
    apply_and_draw_production(g, P5())
    apply_and_draw_production(g, P10())
    apply_and_draw_production(g, P4())
    apply_and_draw_production(g, P4())
    apply_and_draw_production(g, P4())
    apply_and_draw_production(g, P2())
    apply_and_draw_production(g, P3())
    apply_and_draw_production(g, P3())
    apply_and_draw_production(g, P11())
    choose_rectangle_with_point(g, P0())
    apply_and_draw_production(g, P1())
    apply_and_draw_production(g, P2())
    apply_and_draw_production(g, P2())
    apply_and_draw_production(g, P3())
    apply_and_draw_production(g, P3())
    apply_and_draw_production(g, P5())
    choose_rectangle_with_point(g, P0())
    apply_and_draw_production(g, P1())
    apply_and_draw_production(g, P3())
    apply_and_draw_production(g, P3())
    apply_and_draw_production(g, P3())
    apply_and_draw_production(g, P3())
    apply_and_draw_production(g, P5())


if __name__ == "__main__":
    g = create_starting_graph()
    make_disquisition(g)
