from production_base import Production
from graph_model import Graph, HyperEdge


@Production.register
class P0(Production):
    def get_left_side(self) -> Graph:
        return Graph()

    def get_right_side(self, matched: Graph, level: int) -> Graph:
        result = Graph()
        
        for node in matched.nodes:
            result.add_node(node)
        
        for edge in matched.hyperedges:
            if edge.hypertag == "Q":
                result.add_edge(HyperEdge(edge.nodes, edge.hypertag, edge.boundary, R=1, B=edge.B))
            else:
                result.add_edge(HyperEdge(edge.nodes, edge.hypertag, edge.boundary, edge.R, edge.B))
        
        return result

    def can_apply(self, graph: Graph) -> bool:
        for edge in graph.hyperedges:
            if edge.hypertag == "Q" and edge.R == 0 and self._has_boundary_edges(graph, edge):
                return True
        return False

    def find_match(self, graph: Graph):
        for edge in graph.hyperedges:
            if edge.hypertag == "Q" and edge.R == 0 and self._has_boundary_edges(graph, edge):
                return edge
        return None

    def _has_boundary_edges(self, graph: Graph, q_edge: HyperEdge) -> bool:
        q_nodes = set(q_edge.nodes)
        
        if len(q_nodes) != 4:
            return False
            
        found_edges_subgraph = set()
        candidate_edges = self._get_incident_hyperedges(graph, q_nodes)
        
        for edge in candidate_edges:
            if edge.hypertag == "E" and q_nodes.issuperset(edge.nodes):
                found_edges_subgraph.add(frozenset(edge.nodes))
        
        if len(found_edges_subgraph) != 4:
            return False
            
        node_degrees = {n: 0 for n in q_nodes}
        
        for edge_pair in found_edges_subgraph:
            for node in edge_pair:
                if node in node_degrees:
                    node_degrees[node] += 1
        
        return all(degree == 2 for degree in node_degrees.values())
    
    def _get_incident_hyperedges(self, graph: Graph, nodes: set) -> set:
        relevant_edges = set()
        
        nx_graph = graph._graph 
        
        for node in nodes:
            if node.label not in nx_graph:
                continue
                
            neighbor_labels = nx_graph.neighbors(node.label)
            
            for label in neighbor_labels:
                node_data = nx_graph.nodes[label]
                
                if node_data.get('is_hyper'):
                    hyper_edge_obj = node_data['node'].hyperref 
                    if hyper_edge_obj:
                        relevant_edges.add(hyper_edge_obj)
                        
        return relevant_edges