import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx
from graph_model import Graph


def draw(graph: Graph, output_path: str) -> None:
    figure, axes = plt.subplots(figsize=(12, 12))

    positions = {}
    colors = []
    sizes = []
    node_labels = {}

    for node_label, node_data in graph._graph.nodes(data=True):
        current_node = node_data['node']
        positions[node_label] = (current_node.x, current_node.y)

        if node_data.get('is_hyper', False):
            colors.append('red')
            sizes.append(800)
            
            if current_node.hyperref:
                tag = current_node.hyperref.hypertag
                r_val = current_node.hyperref.R
                b_val = current_node.hyperref.B
                node_labels[node_label] = f"{tag}\nR={r_val}\nB={b_val}"
            else:
                node_labels[node_label] = node_label.split('_')[0]
        else:
            if current_node.hanging:
                colors.append('grey')
            else:
                colors.append('yellow')
            sizes.append(1200)
            node_labels[node_label] = node_label

    nx.draw(
        graph._graph,
        pos=positions,
        ax=axes,
        with_labels=True,
        labels=node_labels,
        node_color=colors,
        node_size=sizes,
        font_size=11,
        font_weight='bold',
        edge_color='gray',
        width=2.0
    )
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"Visualization saved as {output_path}")