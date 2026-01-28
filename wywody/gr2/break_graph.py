import os
from wywody.gr2.init_graph import make_graph
from visualization import draw
from productions.p0 import P0
from productions.p1 import P1
from productions.p2 import P2
from productions.p3 import P3
from productions.p4 import P4
from productions.p5 import P5
from productions.p9 import P9
from productions.p10 import P10
from productions.p11 import P11

DIR = "wywody/gr2/img"


def main():
    os.makedirs(DIR, exist_ok=True)

    # Around vertex G
    graph = make_graph()
    draw(graph, f"{DIR}/0.png")

    # 1. Mark Quad
    graph.apply(P0())
    print("P0")
    draw(graph, f"{DIR}/1.png")

    # 2. Mark Hex
    graph.apply(P9())
    print("P9")
    draw(graph, f"{DIR}/2.png")

    # 3. Marking Quad Edges
    graph.apply(P1())
    print("P1")
    draw(graph, f"{DIR}/3.png")

    # 4. Break Boundary
    while P4().can_apply(graph=graph):
        graph.apply(P4())
        print("P4")
    draw(graph, f"{DIR}/4.png")

    # 5. Break Joint Edges
    while P3().can_apply(graph=graph):
        graph.apply(P3())
        print("P3")
    draw(graph, f"{DIR}/5.png")

    # 6. Break Quad
    while P5().can_apply(graph=graph):
        graph.apply(P5())
        print("P5")
    draw(graph, f"{DIR}/6.png")

    # 7. Marking Hex Edges
    graph.apply(P10())
    print("P10")
    draw(graph, f"{DIR}/7.png")

    # 8. Break Boundary
    while P4().can_apply(graph=graph):
        graph.apply(P4())
        print("P4")
    draw(graph, f"{DIR}/8.png")

    # 9. Break Joint Already Broken
    while P2().can_apply(graph=graph):
        graph.apply(P2())
        print("P2")
    draw(graph, f"{DIR}/9.png")

    # 10. Break Joint Edges
    while P3().can_apply(graph=graph):
        graph.apply(P3())
        print("P3")
    draw(graph, f"{DIR}/10.png")

    # 11. Break Hex
    while P11().can_apply(graph=graph):
        graph.apply(P11())
        print("P5")
    draw(graph, f"{DIR}/11.png")


if __name__ == "__main__":
    main()
