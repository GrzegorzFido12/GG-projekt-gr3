from productions.p0 import P0
from productions.p1 import P1
from productions.p3 import P3
from productions.p4 import P4
from productions.p5 import P5
from productions.p6 import P6
from productions.p7 import P7
from productions.p8 import P8
from visualization import draw
from wywody.gr7.first_graph import make_graph

def main_func(q_iter = 3):
    g = make_graph()
    draw(g, "img/1.png")

    p6 = P6()
    g.apply(p6)
    draw(g, "img/2.png")

    p7 = P7()
    g.apply(p7)
    draw(g, "img/3.png")

    p3 = P3()
    while p3.can_apply(g):
        g.apply(p3)
    draw(g, "img/4.png")

    p4 = P4()
    while p4.can_apply(g):
        g.apply(p4)

    draw(g, "img/5.png")

    p8 = P8()
    g.apply(p8)
    draw(g, "img/6.png")

    for i in range(q_iter):
        p0 = P0()
        g.apply(p0)
        draw(g, f"img/{i}_1.png")

        p1 = P1()
        g.apply(p1)
        draw(g, f"img/{i}_2.png")

        p3 = P3()
        while p3.can_apply(g):
            g.apply(p3)
        draw(g, f"img/{i}_3.png")

        p4 = P4()
        while p4.can_apply(g):
            g.apply(p4)
        draw(g, f"img/{i}_4.png")

        p5 = P5()
        #draw(p5.find_match(g), f"test.png")
        g.apply(p5)
        draw(g, f"img/{i}_5.png")

main_func()