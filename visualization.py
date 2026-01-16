"""
Moduł wizualizacji grafu dla gramatyki grafowej.

Kolory i oznaczenia:
- Węzły normalne: żółte
- Węzły wiszące (hanging): niebieskie z niebieskim obramowaniem
- Hiperkrawędzie R=1 (do złamania): czerwone
- Hiperkrawędzie R=0: szare
- Krawędzie brzegowe (B=1): grubsze linie
- Tekst: wyświetla typ i atrybuty (R, B)
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
from graph_model import Graph, Node, HyperEdge
from typing import Optional
import os


def draw(
    graph: Graph,
    filename: Optional[str] = None,
    title: Optional[str] = None,
    show_attributes: bool = True,
    figsize: tuple = (12, 10),
):
    """
    Rysuje graf z kolorowaniem atrybutów.

    Args:
        graph: Graf do narysowania
        filename: Ścieżka do zapisu obrazu (opcjonalne)
        title: Tytuł wykresu (opcjonalne)
        show_attributes: Czy pokazywać wartości atrybutów R i B
        figsize: Rozmiar figury
    """
    fig, ax = plt.subplots(figsize=figsize)

    # Kolory
    NODE_NORMAL = "#FFD700"  # Złoty dla normalnych węzłów
    NODE_HANGING = "#4169E1"  # Niebieski dla wiszących
    EDGE_R1 = "#DC143C"  # Czerwony dla R=1
    EDGE_R0 = "#808080"  # Szary dla R=0
    EDGE_BOUNDARY = "#000080"  # Granatowy dla brzegowych

    # Zbierz pozycje węzłów
    pos = {}
    for node in graph.nodes:
        pos[node.label] = (node.x, node.y)

    # Rysuj hiperkrawędzie (jako wielokąty/linie łączące węzły)
    for edge in graph.hyperedges:
        nodes = edge.nodes
        if len(nodes) < 2:
            continue

        # Kolor na podstawie R
        if edge.R == 1:
            color = EDGE_R1
            alpha = 0.8
        else:
            color = EDGE_R0
            alpha = 0.4

        # Grubość na podstawie B (brzegowa)
        linewidth = 3.0 if edge.B == 1 else 1.5

        # Dla krawędzi E (2 węzły) - rysuj linię
        if len(nodes) == 2:
            n1, n2 = nodes
            x = [n1.x, n2.x]
            y = [n1.y, n2.y]
            ax.plot(x, y, color=color, linewidth=linewidth, alpha=alpha, zorder=1)

            # Etykieta krawędzi
            if show_attributes:
                mid_x = (n1.x + n2.x) / 2
                mid_y = (n1.y + n2.y) / 2
                label = f"{edge.hypertag}"
                if edge.R == 1:
                    label += f" R={edge.R}"
                if edge.B == 1:
                    label += f" B={edge.B}"
                ax.annotate(
                    label,
                    (mid_x, mid_y),
                    fontsize=7,
                    ha="center",
                    va="center",
                    bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.7),
                )
        else:
            # Dla elementów (Q, S, P, T) - rysuj wielokąt
            xs = [n.x for n in nodes]
            ys = [n.y for n in nodes]

            # Zamknij wielokąt
            xs.append(xs[0])
            ys.append(ys[0])

            # Wypełnienie
            fill_color = EDGE_R1 if edge.R == 1 else "#E8E8E8"
            fill_alpha = 0.3 if edge.R == 1 else 0.15
            ax.fill(xs, ys, color=fill_color, alpha=fill_alpha, zorder=0)

            # Obrys
            ax.plot(xs, ys, color=color, linewidth=linewidth, alpha=alpha, zorder=1)

            # Etykieta elementu w środku
            if show_attributes:
                center_x = sum(n.x for n in nodes) / len(nodes)
                center_y = sum(n.y for n in nodes) / len(nodes)
                label = f"{edge.hypertag}"
                if edge.R == 1:
                    label += f"\nR=1"
                ax.annotate(
                    label,
                    (center_x, center_y),
                    fontsize=9,
                    ha="center",
                    va="center",
                    fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
                )

    # Rysuj węzły
    for node in graph.nodes:
        if node.hanging:
            color = NODE_HANGING
            edgecolor = "#00008B"
            marker_size = 150
        else:
            color = NODE_NORMAL
            edgecolor = "#B8860B"
            marker_size = 200

        ax.scatter(
            node.x,
            node.y,
            c=color,
            s=marker_size,
            edgecolors=edgecolor,
            linewidths=2,
            zorder=3,
        )

        # Etykieta węzła
        ax.annotate(
            node.label,
            (node.x, node.y),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=8,
            zorder=4,
        )

    # Legenda
    legend_elements = [
        mpatches.Patch(
            facecolor=NODE_NORMAL, edgecolor="#B8860B", label="Węzeł normalny"
        ),
        mpatches.Patch(
            facecolor=NODE_HANGING, edgecolor="#00008B", label="Węzeł wiszący"
        ),
        mpatches.Patch(facecolor=EDGE_R1, alpha=0.8, label="R=1 (do złamania)"),
        mpatches.Patch(facecolor=EDGE_R0, alpha=0.4, label="R=0"),
        plt.Line2D([0], [0], color="black", linewidth=3, label="B=1 (brzegowa)"),
        plt.Line2D([0], [0], color="black", linewidth=1.5, label="B=0"),
    ]
    ax.legend(handles=legend_elements, loc="upper right", fontsize=8)

    # Ustawienia
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3)

    if title:
        ax.set_title(title, fontsize=14, fontweight="bold")

    plt.tight_layout()

    # Zapis lub wyświetlenie
    if filename:
        os.makedirs(
            os.path.dirname(filename) if os.path.dirname(filename) else ".",
            exist_ok=True,
        )
        plt.savefig(filename, dpi=150, bbox_inches="tight", facecolor="white")
        plt.close(fig)
    else:
        plt.show()


def draw_step(
    graph: Graph,
    step_number: int,
    production_name: str,
    output_dir: str = "visualizations/derivation",
):
    """
    Zapisuje wizualizację pojedynczego kroku wywodu.

    Args:
        graph: Graf do narysowania
        step_number: Numer kroku
        production_name: Nazwa zastosowanej produkcji
        output_dir: Katalog wyjściowy
    """
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"step_{step_number:02d}_{production_name}.png")
    title = f"Krok {step_number}: {production_name}"
    draw(graph, filename=filename, title=title)
    print(f"Zapisano: {filename}")
