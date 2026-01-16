import unittest
import math
import os
from graph_model import Graph, Node, HyperEdge
from productions.p14 import P14
from visualization import draw

class TestP14(unittest.TestCase):
    def setUp(self):
        self.production = P14()
        self.viz_dir = "visualizations/p14_visualizations"
        os.makedirs(self.viz_dir, exist_ok=True)

    def create_broken_heptagon(self, t_r=1):
        g = Graph()
        corners = [Node(math.cos(2*math.pi*i/7), math.sin(2*math.pi*i/7), f"v{i}") for i in range(7)]
        for n in corners:
            g.add_node(n)
        
        mids = []
        for i in range(7):
            c1 = corners[i]
            c2 = corners[(i + 1) % 7]
            m = Node((c1.x + c2.x)/2, (c1.y + c2.y)/2, f"m{i}", hanging=True)
            mids.append(m)
            g.add_node(m)
            g.add_edge(HyperEdge((c1, m), "E", B=1, R=1))
            g.add_edge(HyperEdge((m, c2), "E", B=1, R=1))
            
        g.add_edge(HyperEdge(tuple(corners), "T", R=t_r))
        return g, corners, mids

    def test_p14_find_match_success(self):
        g, _, _ = self.create_broken_heptagon(t_r=1)
        match = self.production.find_match(g)
        self.assertIsNotNone(match)
        self.assertEqual(len(match.nodes), 14)

    def test_p14_apply(self):
        g, _, _ = self.create_broken_heptagon(t_r=1)
        draw(g, os.path.join(self.viz_dir, "test_p14_before.png"))
        result = g.apply(self.production)
        self.assertEqual(result, 1)
        draw(g, os.path.join(self.viz_dir, "test_p14_after.png"))
        
        q_edges = [e for e in g.hyperedges if e.hypertag == "Q"]
        self.assertEqual(len(q_edges), 7)
        for q in q_edges:
            self.assertEqual(len(q.nodes), 4)
            self.assertEqual(q.R, 0)

        center_nodes = [n for n in g.nodes if n.label == "v_center"]
        self.assertEqual(len(center_nodes), 1)

    def test_p14_cannot_apply_without_all_mids(self):
        g, corners, mids = self.create_broken_heptagon(t_r=1)
        m_node = mids[0]
        edges_to_remove = [e for e in g.hyperedges if m_node in e.nodes]
        for e in edges_to_remove:
            g.remove_edge(e)
        g.remove_node(m_node)
        
        result = g.apply(self.production)
        self.assertEqual(result, 0)

    def test_p14_distorted_geometry(self):
        g, corners, mids = self.create_broken_heptagon(t_r=1)
        
        c = corners[0]
        c.x += 2.0
        c.y += 2.0
        
        m0 = mids[0]
        c1 = corners[1]
        m0.x = (c.x + c1.x) / 2
        m0.y = (c.y + c1.y) / 2
        
        m6 = mids[6]
        c6 = corners[6]
        m6.x = (c.x + c6.x) / 2
        m6.y = (c.y + c6.y) / 2
        
        draw(g, os.path.join(self.viz_dir, "test_p14_distorted_before.png"))
        result = g.apply(self.production)
        self.assertEqual(result, 1)
        draw(g, os.path.join(self.viz_dir, "test_p14_distorted_after.png"))

    def test_p14_preserves_boundary_flags(self):
        g, corners, mids = self.create_broken_heptagon(t_r=1)
        
        e_edges = sorted([e for e in g.hyperedges if e.hypertag == "E"], key=lambda x: str(x.nodes))
        g.remove_edge(e_edges[0])
        g.add_edge(HyperEdge(e_edges[0].nodes, "E", B=0, R=1))
        
        draw(g, os.path.join(self.viz_dir, "test_p14_attributes_before.png"))
        result = g.apply(self.production)
        self.assertEqual(result, 1)
        draw(g, os.path.join(self.viz_dir, "test_p14_attributes_after.png"))
        
        found_b0 = False
        for e in [e for e in g.hyperedges if e.hypertag == "E"]:
            if set(e.nodes) == set(e_edges[0].nodes):
                self.assertEqual(e.B, 0)
                found_b0 = True
        self.assertTrue(found_b0)

if __name__ == '__main__':
    unittest.main()
