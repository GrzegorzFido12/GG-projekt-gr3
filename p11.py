import math
from itertools import permutations
from typing import List, Optional, Tuple
from graph_model import Graph, HyperEdge, Node
from production_base import Production

@Production.register
class P11(Production):
    def get_left_side(self) -> Graph:
        g = Graph()
        
        # Create corners
        v1 = Node(0, 0, "v1")
        v2 = Node(10, 0, "v2")
        v3 = Node(15, 8, "v3")
        v4 = Node(10, 16, "v4")
        v5 = Node(0, 16, "v5")
        v6 = Node(-5, 8, "v6")
        
        corners = [v1, v2, v3, v4, v5, v6]
        for v in corners:
            g.add_node(v)
            
        g.add_edge(HyperEdge(tuple(corners), "S", R=1))
        
        pairs = [(v1, v2), (v2, v3), (v3, v4), (v4, v5), (v5, v6), (v6, v1)]
        for idx, (start, end) in enumerate(pairs):
            mid_x = (start.x + end.x) / 2
            mid_y = (start.y + end.y) / 2
            h = Node(mid_x, mid_y, f"h{idx}", hanging=True)
            g.add_node(h)
            g.add_edge(HyperEdge((start, h), "E", B=1))
            g.add_edge(HyperEdge((h, end), "E", B=1))
            
        return g

    def get_right_side(self, matched: Graph, level: int) -> Graph:
        new_graph = Graph()
        
        all_nodes = matched.nodes
        s_edge = next(e for e in matched.hyperedges if e.hypertag == 'S')
        corners = list(s_edge.nodes)
        
        hanging_nodes = [n for n in all_nodes if n not in corners]
        
        # Calculate center
        center_x = sum(n.x for n in corners) / len(corners)
        center_y = sum(n.y for n in corners) / len(corners)
        new_center = Node(center_x, center_y, "v_center", hanging=False)
        new_graph.add_node(new_center)
        
        corners = self._sort_angularly(corners, center_x, center_y)
        
        # Map corners to their specific hanging node
        corner_pair_to_hanging = {}
        n_corners = len(corners)
        
        # Add corners and found hanging nodes to new graph
        for i in range(n_corners):
            c1 = corners[i]
            c2 = corners[(i + 1) % n_corners]
            
            found_h = None
            for h in hanging_nodes:
                d1 = math.hypot(h.x - c1.x, h.y - c1.y)
                d2 = math.hypot(h.x - c2.x, h.y - c2.y)
                d_full = math.hypot(c1.x - c2.x, c1.y - c2.y)
                
                if abs((d1 + d2) - d_full) < 1e-4:
                    found_h = h
                    break
            
            if found_h:
                corner_pair_to_hanging[(c1.label, c2.label)] = found_h
                found_h.hanging = False
                new_graph.add_node(found_h)
        
        for c in corners:
            new_graph.add_node(c)

        # Create new elements
        for i in range(n_corners):
            c_curr = corners[i]
            c_next = corners[(i + 1) % n_corners]
            c_prev = corners[(i - 1 + n_corners) % n_corners]
            
            h_next = corner_pair_to_hanging.get((c_curr.label, c_next.label))
            h_prev = corner_pair_to_hanging.get((c_prev.label, c_curr.label))
            
            if h_next and h_prev:
                # 1. Create Q hyperedge
                q_nodes = (new_center, h_prev, c_curr, h_next)
                new_graph.add_edge(HyperEdge(q_nodes, "Q", R=0))
                
                # 2. Re-create Boundary Edges (B=1)
                new_graph.add_edge(HyperEdge((c_curr, h_next), "E", B=1))
                new_graph.add_edge(HyperEdge((h_prev, c_curr), "E", B=1))
                
                # 3. Create Internal "Spoke" Edges (B=0)
                # This ensures the visual line from Center -> Midpoint exists
                # We use B=0 to distinguish it from the boundary if needed
                new_graph.add_edge(HyperEdge((new_center, h_next), "E", B=0))

        return new_graph
    
    def is_isomorphic(self, subgraph: Graph) -> bool:
        lhs = self.get_left_side()

        # 1. Basic Counts
        if len(subgraph.nodes) != len(lhs.nodes): return False
        if len(subgraph.hyperedges) != len(lhs.hyperedges): return False

        # 2. Filter nodes by 'hanging' property
        corners1 = [n for n in lhs.nodes if not getattr(n, 'hanging', False)]
        hanging1 = [n for n in lhs.nodes if getattr(n, 'hanging', False)]
        corners2 = [n for n in subgraph.nodes if not getattr(n, 'hanging', False)]
        hanging2 = [n for n in subgraph.nodes if getattr(n, 'hanging', False)]

        if len(corners1) != len(corners2): return False
        if len(hanging1) != len(hanging2): return False

        # 3. Helper to get neighbors of a hanging node
        def get_corner_neighbors(g, h_node, all_corners):
            neighbors = set()
            for e in g.hyperedges:
                if h_node in e.nodes and e.hypertag == 'E':
                    for n in e.nodes:
                        if n in all_corners:
                            neighbors.add(n)
            return neighbors

        for p_corners in permutations(corners2):
            corner_map = dict(zip(corners1, p_corners))
            hanging_matched = set()
            valid_permutation = True
            
            for h1 in hanging1:
                neighbors1 = get_corner_neighbors(lhs, h1, corners1)
                if len(neighbors1) != 2: 
                    valid_permutation = False; break
                
                mapped_neighbors = {corner_map[n] for n in neighbors1}
                
                found_h2 = None
                for h2 in hanging2:
                    if h2 in hanging_matched: continue
                    neighbors2 = get_corner_neighbors(subgraph, h2, corners2)
                    if neighbors2 == mapped_neighbors:
                        found_h2 = h2
                        break
                
                if found_h2:
                    hanging_matched.add(found_h2)
                else:
                    valid_permutation = False
                    break
            
            if valid_permutation:
                s_edges1 = [e for e in lhs.hyperedges if e.hypertag == 'S']
                s_edges2 = [e for e in subgraph.hyperedges if e.hypertag == 'S']
                if len(s_edges1) != len(s_edges2): continue
                if s_edges1 and s_edges2:
                    if s_edges1[0].R != s_edges2[0].R: continue
                return True
        return False

    def can_apply(self, graph: Graph) -> bool:
        return self.find_match(graph) is not None

    def find_match(self, graph: Graph) -> Optional[HyperEdge]:
        for edge in graph.hyperedges:
            if edge.hypertag == 'S' and edge.R == 1 and len(edge.nodes) == 6:
                if self._check_all_edges_broken(graph, edge):
                    corners = list(edge.nodes)
                    hanging_nodes = self._get_hanging_nodes(graph, corners)
                    all_involved_nodes = tuple(corners + hanging_nodes)
                    return HyperEdge(all_involved_nodes, "S", R=1)
        return None

    def _check_all_edges_broken(self, graph: Graph, s_edge: HyperEdge) -> bool:
        corners = list(s_edge.nodes)
        if len(corners) != 6: return False
        
        center_x = sum(n.x for n in corners) / 6
        center_y = sum(n.y for n in corners) / 6
        sorted_corners = self._sort_angularly(corners, center_x, center_y)
        
        for i in range(6):
            c1 = sorted_corners[i]
            c2 = sorted_corners[(i + 1) % 6]
            if not self._has_hanging_node(graph, c1, c2):
                return False
        return True

    def _get_hanging_nodes(self, graph: Graph, corners: List[Node]) -> List[Node]:
        hanging = []
        center_x = sum(n.x for n in corners) / len(corners)
        center_y = sum(n.y for n in corners) / len(corners)
        sorted_corners = self._sort_angularly(corners, center_x, center_y)
        
        for i in range(len(corners)):
            c1 = sorted_corners[i]
            c2 = sorted_corners[(i + 1) % len(corners)]
            h = self._find_hanging_node(graph, c1, c2)
            if h:
                hanging.append(h)
        return hanging

    def _has_hanging_node(self, graph: Graph, n1: Node, n2: Node) -> bool:
        return self._find_hanging_node(graph, n1, n2) is not None

    def _find_hanging_node(self, graph: Graph, n1: Node, n2: Node) -> Optional[Node]:
        """
        Finds a node that is:
        1. Marked as hanging.
        2. Geometrically between n1 and n2.
        3. Topologically connected to n1 and n2 via 'E' edges.
        """
        for node in graph.nodes:
            if node.hanging:
                # 1. Geometric Check
                d1 = math.hypot(node.x - n1.x, node.y - n1.y)
                d2 = math.hypot(node.x - n2.x, node.y - n2.y)
                d_full = math.hypot(n1.x - n2.x, n1.y - n2.y)
                
                if abs((d1 + d2) - d_full) < 1e-4:
                    # 2. Topological Check (MUST exist edges: n1-node and node-n2)
                    connected_to_n1 = False
                    connected_to_n2 = False
                    
                    for edge in graph.hyperedges:
                        # Assuming boundary edges are tagged "E" or just standard edges
                        if n1 in edge.nodes and node in edge.nodes:
                            connected_to_n1 = True
                        if n2 in edge.nodes and node in edge.nodes:
                            connected_to_n2 = True
                    
                    if connected_to_n1 and connected_to_n2:
                        return node
        return None

    def _sort_angularly(self, nodes: List[Node], cx: float, cy: float) -> List[Node]:
        return sorted(nodes, key=lambda n: math.atan2(n.y - cy, n.x - cx))