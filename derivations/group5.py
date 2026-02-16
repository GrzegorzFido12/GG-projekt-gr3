import os

from graph_model import Graph, Node, HyperEdge
from productions.p7_ import P7
from productions.p8 import P8
from productions.p1 import P1
from productions.p5 import P5
from productions.p2 import P2
from productions.p3 import P3
from productions.p4 import P4
from visualization import draw

VIS_DIR = "visualizations/group5"
os.makedirs(VIS_DIR, exist_ok=True)


def create_initial_graph():
    """
    Creates an initial graph with 3 trapezoidal elements around a central rectangular void.
    Top, Left, and Bottom Trapezoids.
    """
    g = Graph()
    nodes = []

    # Center and size for Inner Rectangle
    width, height = 20, 15
    center_x, center_y = 15, 15

    # Margin for Outer Nodes (to form trapezoids)
    margin = 10

    # Inner Corners (v0-v3)
    inner_corners = [
        (center_x - width / 2, center_y + height / 2),  # v0: TL
        (center_x + width / 2, center_y + height / 2),  # v1: TR
        (center_x + width / 2, center_y - height / 2),  # v2: BR
        (center_x - width / 2, center_y - height / 2),  # v3: BL
    ]

    # Outer Corners (v4-v7) (expanded)
    outer_corners = [
        (center_x - width / 2 - margin, center_y + height / 2 + margin),  # v4: Outer TL
        (center_x + width / 2 + margin, center_y + height / 2 + margin),  # v5: Outer TR
        (center_x + width / 2 + margin, center_y - height / 2 - margin),  # v6: Outer BR
        (center_x - width / 2 - margin, center_y - height / 2 - margin),  # v7: Outer BL
    ]

    coords = inner_corners + outer_corners
    for i, (x, y) in enumerate(coords):
        n = Node(x, y, f"v{i}")
        nodes.append(n)
        g.add_node(n)

    # Alias for clarity
    v0, v1, v2, v3 = nodes[0], nodes[1], nodes[2], nodes[3]
    v4, v5, v6, v7 = nodes[4], nodes[5], nodes[6], nodes[7]

    # Define Elements (HyperEdges)
    # Order: Top-Left, Top-Right, Bottom-Right, Bottom-Left of the QUAD

    # Central HyperNode S (R=0 initially)
    g.add_edge(HyperEdge((v0, v1, v2, v3), "Q", R=0))

    # Top Trapezoid: Left side is v4-v0, Top is v4-v5, Right is v5-v1, Bottom is v0-v1
    # Nodes: v4, v5, v1, v0
    trap_top = HyperEdge((v4, v5, v1, v0), "Q", R=0)

    # Left Trapezoid: Left side is v7-v4, Top is v4-v0, Right is v0-v3, Bottom is v7-v3
    # Nodes: v7, v4, v0, v3
    trap_left = HyperEdge((v7, v4, v0, v3), "Q", R=0)

    # Bottom Trapezoid: Left side is v3-v7, Top is v3-v2, Right is v2-v6, Bottom is v7-v6
    # Nodes: v3, v2, v6, v7
    trap_bottom = HyperEdge((v3, v2, v6, v7), "Q", R=0)

    g.add_edge(trap_top)
    g.add_edge(trap_left)
    g.add_edge(trap_bottom)

    # Define Edges with Boundary Flags
    # Helper to add edge
    def add_boundary_edge(n1, n2, is_boundary):
        g.add_edge(
            HyperEdge((n1, n2), "E", boundary=is_boundary, B=(1 if is_boundary else 0))
        )

    # --- Top Trapezoid Edges ---
    add_boundary_edge(v4, v5, True)  # Top Outer
    add_boundary_edge(v5, v1, False)  # Right Arm (Boundary)
    add_boundary_edge(v0, v1, False)  # Bottom Inner (Boundary of hole)
    add_boundary_edge(v4, v0, False)  # Left Arm (Shared with Left Trap)

    # --- Left Trapezoid Edges ---
    add_boundary_edge(v7, v4, True)  # Left Outer
    add_boundary_edge(v7, v3, False)  # Bottom Arm (Shared with Bottom Trap)
    add_boundary_edge(v3, v0, False)  # Right Inner (Boundary of hole)

    # --- Bottom Trapezoid Edges ---
    add_boundary_edge(v6, v7, True)  # Bottom Outer
    add_boundary_edge(v6, v2, False)  # Right Arm (Boundary)
    add_boundary_edge(v2, v3, False)  # Top Inner (Boundary of hole)

    # --- Close the hole on the right ---
    add_boundary_edge(v1, v2, False)  # Right Inner (Boundary of hole)

    # --- Close the Outer Right Edge with 2 segments ---
    v8_x = (v5.x + v6.x) / 2 + 20
    v8_y = (v5.y + v6.y) / 2
    v8 = Node(v8_x, v8_y, "v8")
    g.add_node(v8)

    add_boundary_edge(v5, v8, True)  # Top-Right Outer Segment
    add_boundary_edge(v8, v6, True)  # Bottom-Right Outer Segment

    # Right Pentagon
    # Initially R=0. We will mark it for refinement in run_derivation.
    pentagon_right = HyperEdge((v1, v2, v6, v8, v5), "P", R=0)
    g.add_edge(pentagon_right)

    return g


def run_derivation():
    print("Running Group 5 Derivation...")

    # 0. Initial State
    graph = create_initial_graph()
    draw(graph, os.path.join(VIS_DIR, "0_initial.png"))
    print("Step 0: Initial graph created.")

    # 1. Mark Pentagon for Refinement (Manual Step or P0 equivalent)
    # Find the central pentagon (Tag="P", R=0) and mark it (R=1)
    # This prepares it for P7.
    candidates = [e for e in graph.hyperedges if e.hypertag == "P" and e.R == 0]
    if candidates:
        # Assuming only one for this derivation
        cand = candidates[0]
        graph.remove_edge(cand)
        graph.add_edge(HyperEdge(cand.nodes, "P", R=1, B=cand.B))
        draw(graph, os.path.join(VIS_DIR, "1_marked.png"))
        print("Step 1: Pentagon marked for refinement (R=1).")
    else:
        print("Warning: No pentagon found to mark.")

    # 2. Apply P7 (Marks edges of the pentagon)
    p7 = P7()
    if p7.can_apply(graph):
        graph.apply(p7)
        draw(graph, os.path.join(VIS_DIR, "2_p7_applied.png"))
        print("Step 2: P7 applied.")
    else:
        print("Step 2 Failed: P7 condition not met.")
        return

    # 3. Break Edges (Apply P2/P4 Loop)
    # P7 marks edges with R=1. We need to split them.
    # P4 handles boundary edges (B=1, R=1) -> splits them.
    # P2 handles internal edges (B=0, R=1) -> splits them.
    # We loop until no more edges can be broken.
    print("Step 3: Breaking edges...")
    p2 = P2()
    p3 = P3()
    p4 = P4()

    iteration = 0
    while True:
        broken_something = False

        # Try P4 (Boundary)
        if p4.can_apply(graph):
            graph.apply(p4)
            broken_something = True
            # print("  Applied P4 (Boundary Edge Break)")

        # Try P2 (Internal hanging match)
        elif p2.can_apply(graph):
            graph.apply(p2)
            broken_something = True
            # print("  Applied P2 (Internal hanging match)")

        # Try P3 (Internal Refinement)
        elif p3.can_apply(graph):
            graph.apply(p3)
            broken_something = True
            # print("  Applied P3 (Internal Edge Break)")

        if not broken_something:
            break

        iteration += 1

    draw(graph, os.path.join(VIS_DIR, "3_edges_broken.png"))
    print(f"Step 3: Edges broken in {iteration} iterations.")

    # 4. Apply P8 (Splits the pentagon now that edges are broken)
    p8 = P8()
    if p8.can_apply(graph):
        graph.apply(p8)
        draw(graph, os.path.join(VIS_DIR, "4_p8_applied.png"))
        print("Step 4: P8 applied.")
    else:
        print("Step 4 Failed: P8 condition not met.")

    #  --- NEW STEPS FOR TOP TRAPEZOID ---

    # 5. Mark Top Trapezoid for Refinement
    # Find the Q element with nodes v4, v5 (Top Outer corners).
    print("Step 5: Marking Top Trapezoid...")
    top_trap = None
    for q in graph.hyperedges:
        if q.hypertag == "Q" and q.R == 0:
            # Check if this Q contains v4 and v5
            # We need to find nodes by label since objects might differ if re-created (though here they persist)
            n_labels = [n.label for n in q.nodes]
            if "v4" in n_labels and "v5" in n_labels:
                top_trap = q
                break

    if top_trap:
        graph.remove_edge(top_trap)
        graph.add_edge(HyperEdge(top_trap.nodes, "Q", R=1, B=top_trap.B))
        draw(graph, os.path.join(VIS_DIR, "5_top_trap_marked.png"))
        print("Step 5: Top Trapezoid marked (R=1).")
    else:
        print("Step 5 Failed: Top Trapezoid not found.")
        return

    # 6. Apply P1 (Marks edges of the Q)
    p1 = P1()
    if p1.can_apply(graph):
        graph.apply(p1)
        draw(graph, os.path.join(VIS_DIR, "6_p1_applied.png"))
        print("Step 6: P1 applied (Edges marked).")
    else:
        print("Step 6 Failed: P1 condition not met.")
        # We might continue if maybe edges are already marked or broken, but P1 is expected.

    # 7. Break Edges (Apply P2/P4 Loop again)
    print("Step 7: Breaking edges for Top Trapezoid...")
    iteration = 0
    while True:
        broken_something = False

        # Try P4 (Boundary)
        if p4.can_apply(graph):
            graph.apply(p4)
            broken_something = True

        # Try P2 (Internal hanging match)
        elif p2.can_apply(graph):
            graph.apply(p2)
            broken_something = True

        # Try P3 (Internal Refinement)
        elif p3.can_apply(graph):
            graph.apply(p3)
            broken_something = True

        if not broken_something:
            break

        iteration += 1

    draw(graph, os.path.join(VIS_DIR, "7_edges_broken_top.png"))
    print(f"Step 7: Edges broken in {iteration} iterations.")

    # 8. Apply P5 (Splits the Top Trapezoid)
    p5 = P5()
    if p5.can_apply(graph):
        graph.apply(p5)
        draw(graph, os.path.join(VIS_DIR, "8_p5_applied.png"))
        print("Step 8: P5 applied (Top Trapezoid split).")
    else:
        # Debugging info
        print("Step 8 Failed: P5 condition not met.")
        # Check why
        # Q marked?
        candidates = [q for q in graph.hyperedges if q.hypertag == "Q" and q.R == 1]
        print(f"  Candidates Q(R=1): {len(candidates)}")
        # Check ctx
        ctx = p5._compute_ctx(graph)
        print(f"  P5 Context found: {ctx is not None}")


    import math
    import re

    # --- HELPER FUNCTIONS ---

    def get_adjacent_nodes(node, graph):
        """Returns list of nodes directly connected to 'node' via E edges."""
        adjacent = []
        for edge in graph.hyperedges:
            if edge.hypertag == "E" and len(edge.nodes) == 2:
                if node in edge.nodes:
                    other = edge.nodes[1] if edge.nodes[0] == node else edge.nodes[0]
                    adjacent.append(other)
        return adjacent

    def find_edge(n1, n2, graph):
        """Returns the E edge connecting n1 and n2, or None."""
        for edge in graph.hyperedges:
            if edge.hypertag == "E" and set(edge.nodes) == {n1, n2}:
                return edge
        return None

    def find_node_by_label(label, graph):
        """Returns the node with the given label, or None."""
        for node in graph.nodes:
            if node.label == label:
                return node
        return None

    def node_distance(n1, n2):
        """Returns Euclidean distance between two nodes."""
        return math.sqrt((n1.x - n2.x) ** 2 + (n1.y - n2.y) ** 2)

    def find_q_closest_to_target(graph, center_node_label, target_node_label):
        """
        Finds the Q element containing 'center_node_label' that is spatially closest
        to 'target_node_label'.
        Returns: (best_q, adjacent_nodes_in_q)
        """
        center_node = find_node_by_label(center_node_label, graph)
        target_node = find_node_by_label(target_node_label, graph)

        if not center_node or not target_node:
            return None, None

        candidates = []
        for q in graph.hyperedges:
            if q.hypertag == "Q" and q.R == 0 and len(q.nodes) == 4:
                if center_node in q.nodes:
                    # Metric: sum of distances of all nodes in Q to target
                    # (Or min distance, but sum is robust)
                    metric = sum(node_distance(n, target_node) for n in q.nodes)
                    candidates.append((q, metric))
        
        if not candidates:
            return None, None
        
        # Sort by metric (ascending)
        candidates.sort(key=lambda x: x[1])
        best_q = candidates[0][0]

        # Find nodes in this Q that are directly connected to center_node via E edges
        # These are the "adjacent" nodes defining the sector
        q_neighbors = []
        for n in best_q.nodes:
            if n == center_node:
                continue
            if find_edge(center_node, n, graph):
                q_neighbors.append(n)
        
        # If expected structure holds, there should be 2 such neighbors
        # If not (e.g. diagonal connection?), we take what we find
        return best_q, q_neighbors

    def split_trapezoid(
        graph, q_element, target_vertex, adjacent_nodes, p4, p5, step_num, vis_prefix
    ):
        """
        Generic function to split a trapezoid:
        1. Mark edges (between target/adjacent, and adjacent/center)
        2. Apply P4 to split edges
        3. Mark Q for refinement
        4. Apply P5 to split the Q
        5. If P5 fails, try P2 (to resolve hanging nodes created by previous splits)
        """
        print(f"Step {step_num}: Processing trapezoid with nodes: {[n.label for n in q_element.nodes]}...")

        # Identify center node: The node in Q that is the "structural center" (from previous split)
        # It typically starts with 'c_' or 'center'.
        center_node = None
        for n in q_element.nodes:
            if n.label.startswith("c_") or n.label.startswith("center"):
                center_node = n
                break
        
        if not center_node:
             # Fallback to max distance if no explicit center node found
            center_node = max(q_element.nodes, key=lambda n: node_distance(target_vertex, n))
        
        print(f"  Identified center node: {center_node.label}")

        # Helper to detect if a node is already "Level 2" refined (e.g. h_v5_h_v5_v1)
        def is_refined_node(node):
            return node.label.count("h_") > 1

        # Edges to mark
        edges_to_mark = []
        
        # 1. Edges from target to neighbor (Boundary)
        # We rely on 'adjacent_nodes' (closest to v5) for the boundaries.
        for neighbor in adjacent_nodes:
            if is_refined_node(neighbor):
                print(f"  Skipping boundary edge to {neighbor.label} (already refined).")
                continue
                
            edge = find_edge(target_vertex, neighbor, graph)
            if edge:
                edges_to_mark.append((target_vertex, neighbor, edge))
        
        # 2. Edges from Q-Corners to Center (Internal Spokes)
        # We look at ALL nodes in Q (except target and center) to find spokes.
        # This catches nodes like h_v5_v1 which might not be adjacent to v5 anymore (green circle case).
        q_corners = [n for n in q_element.nodes if n != target_vertex and n != center_node]
        for corner in q_corners:
            edge = find_edge(corner, center_node, graph)
            if edge:
                 edges_to_mark.append((corner, center_node, edge))

        if edges_to_mark:
            print(f"  Marking {len(edges_to_mark)} edges.")
            for n1, n2, target_edge in edges_to_mark:
                graph.remove_edge(target_edge)
                graph.add_edge(HyperEdge((n1, n2), "E", boundary=True, R=1, B=1))
            
            draw(graph, os.path.join(VIS_DIR, f"{step_num}a_{vis_prefix}_marked_edges.png"))

            split_count = 0
            while p4.can_apply(graph):
                graph.apply(p4)
                split_count += 1
            
            draw(graph, os.path.join(VIS_DIR, f"{step_num}b_{vis_prefix}_p4_splits.png"))
            print(f"  P4 applied {split_count} times.")

        # Mark Q
        graph.remove_edge(q_element)
        graph.add_edge(HyperEdge(q_element.nodes, "Q", R=1, B=q_element.B))
        
        draw(graph, os.path.join(VIS_DIR, f"{step_num}c_{vis_prefix}_q_marked.png"))
        
        if p5.can_apply(graph):
            graph.apply(p5)
            draw(graph, os.path.join(VIS_DIR, f"{step_num}d_{vis_prefix}_p5_applied.png"))
            print(f"  P5 applied successfully.")
            return "p5"
        
        # If P5 failed, maybe P2 can apply? (Hanging node resolution)
        p2 = P2()
        if p2.can_apply(graph):
            graph.apply(p2)
            draw(graph, os.path.join(VIS_DIR, f"{step_num}d_{vis_prefix}_p2_applied.png"))
            print(f"  P5 failed, but P2 applied (hanging node resolution).")
            return "p2"
            
        print(f"  P5 and P2 failed.")
        return "fail"


    # --- GENERIC RECURSIVE TRAPEZOID SPLITTING ---
    print("\n=== Starting Generic Trapezoid Splitting at v5 ===")

    # Define target directions (nodes roughly in the direction we want to find Qs)
    targets = [
        # Trapezoid 1 (Top): Closest to v4
        "v4",
        # Trapezoid 2 (Right): Closest to v8
        "v8",
    ]

    step_counter = 9
    
    # Process each direction
    for i, target_label in enumerate(targets):
        print(f"\n--- Processing Direction {i + 1}: Towards {target_label} ---")
        
        # Retry loop for this direction (in case P2 splits the Q into something closer)
        retry_count = 0
        while retry_count < 3: # Limit retries to avoid infinite loops
            current_q, adjacent_nodes = find_q_closest_to_target(
                graph, "v5", target_label
            )
            
            if not current_q:
                print(f"  No trapezoid found for these edge directions. (Done for this direction)")
                break
            
            print(f"  Found Q: {[n.label for n in current_q.nodes]}")
            print(f"  Adjacent to v5 (closest): {[n.label for n in adjacent_nodes]}")
            
            v5_node = find_node_by_label("v5", graph)
            vis_prefix = f"v5_trap_{i + 1}_{retry_count}"
            
            # Attempt split
            result = split_trapezoid(
                graph,
                current_q,
                v5_node,
                adjacent_nodes,
                p4,
                p5,
                step_counter,
                vis_prefix,
            )
            
            step_counter += 1
            
            # Common stability loop helper
            def run_stability():
                p2 = P2()
                p3 = P3()
                stab_iter = 0
                while True:
                    broken_something = False
                    if p4.can_apply(graph):
                        graph.apply(p4)
                        broken_something = True
                    elif p2.can_apply(graph):
                        graph.apply(p2)
                        broken_something = True
                    elif p3.can_apply(graph):
                        graph.apply(p3)
                        broken_something = True
                    if not broken_something:
                        break
                    stab_iter += 1
                if stab_iter > 0:
                    print(f"  Stability loop finished in {stab_iter} iterations.")
            
            if result == "p5":
                print("  Success (P5 applied). Running stability and moving to next direction.")
                run_stability()
                break # Done with this direction
                
            elif result == "p2":
                print("  Partial Success (P2 applied). Running stability and retrying direction...")
                run_stability()
                retry_count += 1
                continue # Retry finding Q for this direction
                
            else:
                print("  Failed to split. Stopping this direction.")
                break

    print(f"\n=== Finished Generic Processing ===")


if __name__ == "__main__":
    run_derivation()
