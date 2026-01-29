import os
from graph_model import Graph
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


def pipeline(g: Graph, label: str, level: int):
    step = 1
    marking = [P9, P0]
    productions = [P1, P4, P3, P5, P10, P4, P2, P3, P11]
    for _ in range(level):

        for prod in marking:
            while g.apply(prod(), specified_label=label):
                draw(g, os.path.join(DIR, f"{step}.png"))
                step += 1

        for prod in productions:
            while g.apply(prod()):
                draw(g, os.path.join(DIR, f"{step}.png"))
                step += 1


def main():
    os.makedirs(DIR, exist_ok=True)

    g = make_graph()
    draw(g, os.path.join(DIR, f"0.png"))
    pipeline(g, "G", 2)


if __name__ == "__main__":
    main()
