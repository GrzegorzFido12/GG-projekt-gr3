from productions.p0 import P0
from productions.p1 import P1
from productions.p4 import P4
from productions.p5 import P5
from productions.p6 import P6
from productions.p7 import P7
from productions.p8 import P8
from visualization import draw
from wywody.gr7.breaking_edges import add_hanging_nodes_on_external_edges
from wywody.gr7.first_graph import make_graph


def main_func():
    g = make_graph()
    draw(g, "1.png")

    p6 = P6()
    g.apply(p6)
    draw(g, "2.png")

    p7 = P7()
    g.apply(p7)
    draw(g, "3.png")

    #add hanging vertices
    g= add_hanging_nodes_on_external_edges(g)
    draw(g, "test.png")

    p8 = P8()
    g.apply(p8)
    draw(g, "4.png")

    p0 = P0() #nie działa dla złamanych krawędzi więc nwm co z tym zrobić..
    g.apply(p0)
    draw(g, "5.png")

    p1 = P1() #tego nikt nie wstawił na gita xD
    g.apply(p1)
    draw(g, "6.png")

    p4 = P4()
    g.apply(p4)
    draw(g, "7.png")

    p5 = P5() #tego też nie..
    g.apply(p5)
    draw(g, "8.png")

main_func()