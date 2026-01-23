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


def main_func():
    g = make_graph()
    draw(g, "img/1.png")

    p6 = P6()
    g.apply(p6)
    draw(g, "img/2.png")

    p7 = P7()
    g.apply(p7)
    draw(g, "img/3.png")

    #add hanging vertices
    #g= add_hanging_nodes_on_external_edges(g)
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

    p0 = P0()
    g.apply(p0)
    draw(g, "img/6.png")

    p1 = P1() #tego nikt nie wstawił na gita xD
    g.apply(p1)
    draw(g, "img/7.png")

    p4 = P4()
    g.apply(p4)
    draw(g, "img/8.png")

    p5 = P5() #tego też nie..
    g.apply(p5)
    draw(g, "img/9.png")

main_func()