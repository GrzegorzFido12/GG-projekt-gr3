import networkx as nx
from dataclasses import dataclass
from typing import Tuple, List, Set, Optional, Any


@dataclass
class Node:
    x: float
    y: float
    label: str
    hanging: bool = False
    hyperref: Optional[Any] = None

    def __hash__(self):
        return hash(self.label)

    def __eq__(self, other):
        return isinstance(other, Node) and self.label == other.label

    def __repr__(self):
        return f"Node({self.label}, {self.x}, {self.y})"


@dataclass
class HyperEdge:
    nodes: Tuple[Node, ...]
    hypertag: str
    boundary: bool = False
    R: int = 0
    B: int = 0

    def __post_init__(self):
        if len(self.nodes) < 2:
            raise ValueError(f"HyperEdge needs at least 2 nodes, got {len(self.nodes)}")

    @property
    def label(self) -> str:
        return f"{self.hypertag}_{'_'.join(n.label for n in self.nodes)}"

    def __hash__(self):
        return hash((self.hypertag, self.nodes))

    def __eq__(self, other):
        if not isinstance(other, HyperEdge):
            return False
        return self.hypertag == other.hypertag and set(self.nodes) == set(other.nodes)

    def __repr__(self):
        node_labels = ", ".join(n.label for n in self.nodes)
        return f"HyperEdge({self.hypertag}[{node_labels}], R={self.R}, B={self.B})"


class NodeCount:
    def __init__(self, normal: int, hyper: int):
        self.normal = normal
        self.hyper = hyper


class Graph:
    def __init__(self):
        self._graph = nx.Graph()
        self._hyperedges: Set[HyperEdge] = set()
        self._nodes: Set[Node] = set()

    def add_node(self, node: Node) -> None:
        self._nodes.add(node)
        self._graph.add_node(node.label, node=node, is_hyper=False)

    def add_edge(self, edge: HyperEdge) -> None:
        self._hyperedges.add(edge)

        avg_x = sum(n.x for n in edge.nodes) / len(edge.nodes)
        avg_y = sum(n.y for n in edge.nodes) / len(edge.nodes)

        hyper_node = Node(avg_x, avg_y, edge.label, hyperref=edge)
        self._graph.add_node(edge.label, node=hyper_node, is_hyper=True)

        for node in edge.nodes:
            if node.label not in self._graph:
                self.add_node(node)
            self._graph.add_edge(edge.label, node.label)

    def remove_edge(self, edge: HyperEdge) -> None:
        if edge in self._hyperedges:
            self._hyperedges.remove(edge)
            if edge.label in self._graph:
                self._graph.remove_node(edge.label)

    def remove_node(self, node: Node) -> None:
        if node in self._nodes:
            self._nodes.remove(node)
            if node.label in self._graph:
                self._graph.remove_node(node.label)

    @property
    def nodes(self) -> List[Node]:
        return list(self._nodes)

    @property
    def hyperedges(self) -> List[HyperEdge]:
        return list(self._hyperedges)

    def get_node(self, label: str) -> Optional[Node]:
        for node in self._nodes:
            if node.label == label:
                return node
        return None

    def get_hyperedge(self, label: str) -> Optional[HyperEdge]:
        for edge in self._hyperedges:
            if edge.label == label:
                return edge
        return None

    def count_nodes(self) -> NodeCount:
        return NodeCount(normal=len(self._nodes), hyper=len(self._hyperedges))

    def apply(self, production) -> int:
        if not production.can_apply(self):
            return 0

        matched_edge = production.find_match(self)
        if matched_edge is None:
            return 0

        matched_subgraph = Graph()

        for node in matched_edge.nodes:
            matched_subgraph.add_node(node)

        for edge in self.hyperedges:
            if all(n in matched_edge.nodes for n in edge.nodes):
                matched_subgraph.add_edge(
                    HyperEdge(edge.nodes, edge.hypertag, edge.boundary, edge.R, edge.B)
                )

        edges_to_remove = []
        for edge in matched_subgraph.hyperedges:
            for main_edge in self.hyperedges:
                if (
                    main_edge.hypertag == edge.hypertag
                    and set(main_edge.nodes) == set(edge.nodes)
                    and main_edge.R == edge.R
                    and main_edge.B == edge.B
                ):
                    edges_to_remove.append(main_edge)
                    break

        for edge in edges_to_remove:
            self.remove_edge(edge)

        right_graph = production.get_right_side(matched_subgraph, 0)

        for edge in right_graph.hyperedges:
            self.add_edge(edge)

        return 1
