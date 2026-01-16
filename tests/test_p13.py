import unittest
import os
from graph_model import Graph, Node, HyperEdge
from productions.p13 import P13
from visualization import draw

class TestP13(unittest.TestCase):
    def setUp(self):
        self.production = P13()
        self.viz_dir = "visualizations/p13_visualizations"
        os.makedirs(self.viz_dir, exist_ok=True)

    def create_heptagon_with_edges(self, t_r=1, e_r=0):
        g = Graph()
        nodes = [Node(x, y, f"v{i}") for i, (x, y) in enumerate([
            (0, 2), (1, 3), (2, 3), (3, 2), (3, 1), (2, 0), (1, 0)
        ])]
        for n in nodes:
            g.add_node(n)
        
        g.add_edge(HyperEdge(tuple(nodes), "T", R=t_r))
        
        for i in range(7):
            g.add_edge(HyperEdge((nodes[i], nodes[(i + 1) % 7]), "E", R=e_r))
        return g

    def test_p13_find_match_success(self):
        g = self.create_heptagon_with_edges(t_r=1, e_r=0)
        match = self.production.find_match(g)
        self.assertIsNotNone(match)
        self.assertEqual(match.hypertag, "T")
        self.assertEqual(len(match.nodes), 7)

    def test_p13_find_match_already_marked(self):
        g = self.create_heptagon_with_edges(t_r=1, e_r=1)
        match = self.production.find_match(g)
        self.assertIsNone(match)

    def test_p13_apply(self):
        g = self.create_heptagon_with_edges(t_r=1, e_r=0)
        draw(g, os.path.join(self.viz_dir, "test_p13_before.png"))
        result = g.apply(self.production)
        self.assertEqual(result, 1)
        draw(g, os.path.join(self.viz_dir, "test_p13_after.png"))
        
        e_edges = [e for e in g.hyperedges if e.hypertag == "E"]
        self.assertEqual(len(e_edges), 7)
        for e in e_edges:
            self.assertEqual(e.R, 1)
            
        t_edges = [e for e in g.hyperedges if e.hypertag == "T"]
        self.assertEqual(len(t_edges), 1)
        self.assertEqual(t_edges[0].R, 1)

    def test_p13_cannot_apply_t_r0(self):
        g = self.create_heptagon_with_edges(t_r=0, e_r=0)
        result = g.apply(self.production)
        self.assertEqual(result, 0)

    def test_p13_multiple_heptagons(self):
        g = self.create_heptagon_with_edges(t_r=1, e_r=0)
        
        nodes2 = [Node(x + 5, y, f"u{i}") for i, (x, y) in enumerate([
            (0, 2), (1, 3), (2, 3), (3, 2), (3, 1), (2, 0), (1, 0)
        ])]
        for n in nodes2:
            g.add_node(n)
        g.add_edge(HyperEdge(tuple(nodes2), "T", R=1))
        for i in range(7):
            g.add_edge(HyperEdge((nodes2[i], nodes2[(i + 1) % 7]), "E", R=0))
            
        draw(g, os.path.join(self.viz_dir, "test_p13_multiple_before.png"))
        
        result1 = g.apply(self.production)
        self.assertEqual(result1, 1)
        draw(g, os.path.join(self.viz_dir, "test_p13_multiple_after1.png"))
        
        result2 = g.apply(self.production)
        self.assertEqual(result2, 1)
        draw(g, os.path.join(self.viz_dir, "test_p13_multiple_after2.png"))
        
        result3 = g.apply(self.production)
        self.assertEqual(result3, 0)

    def test_p13_partial_marking(self):
        g = self.create_heptagon_with_edges(t_r=1, e_r=0)
        
        e_edges = [e for e in g.hyperedges if e.hypertag == "E"]
        g.remove_edge(e_edges[0])
        g.add_edge(HyperEdge(e_edges[0].nodes, "E", R=1))
        
        draw(g, os.path.join(self.viz_dir, "test_p13_partial_before.png"))
        result = g.apply(self.production)
        self.assertEqual(result, 1)
        draw(g, os.path.join(self.viz_dir, "test_p13_partial_after.png"))
        
        for e in [e for e in g.hyperedges if e.hypertag == "E"]:
            self.assertEqual(e.R, 1)

if __name__ == '__main__':
    unittest.main()
