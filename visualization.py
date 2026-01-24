import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
from graph_model import Graph


def draw(graph: Graph, output_path: str) -> None:
    figure, axes = plt.subplots(figsize=(12, 12))

    positions = {}
    colors = []
    sizes = []
    node_labels = {}

    nodes_normal = []
    nodes_x = []

    for node_label, node_data in graph._graph.nodes(data=True):
        current_node = node_data["node"]
        positions[node_label] = (current_node.x, current_node.y)

        if node_data.get("is_hyper", False):
            colors.append("red")
            sizes.append(800)
            nodes_normal.append(node_label)
            if current_node.hyperref:
                tag = current_node.hyperref.hypertag
                r_val = current_node.hyperref.R
                node_labels[node_label] = f"{tag}\nR={r_val}"
            else:
                node_labels[node_label] = node_label.split("_")[0]
        else:
            if node_label == "X":
                colors.append("blue")
                nodes_x.append(node_label)
            else:
                if current_node.hanging:
                    colors.append("grey")
                else:
                    colors.append("yellow")
                nodes_normal.append(node_label)

            sizes.append(1200)
            node_labels[node_label] = node_label

    nx.draw(
        graph._graph,
        pos=positions,
        ax=axes,
        with_labels=False,
        node_color=colors,
        node_size=sizes,
        edge_color="gray",
        width=2.0,
    )

    labels_normal = {n: node_labels[n] for n in nodes_normal}
    nx.draw_networkx_labels(
        graph._graph,
        pos=positions,
        labels=labels_normal,
        font_color="black",
        font_size=11,
        font_weight="bold",
        ax=axes
    )

    if nodes_x:
        labels_x = {n: node_labels[n] for n in nodes_x}
        nx.draw_networkx_labels(
            graph._graph,
            pos=positions,
            labels=labels_x,
            font_color="white",
            font_size=11,
            font_weight="bold",
            ax=axes
        )

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Visualization saved as {output_path}")
