"""
Skrypt uruchamiający pełny wywód dla Grupy 5.

Generuje wizualizację krok po kroku i zapisuje obrazy PNG
do katalogu visualizations/derivation/.

Autor: Grupa 5 - GG Projekt
"""

import os
import sys

# Dodaj katalog główny do ścieżki
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from driver import HexagonalMeshDriver
from visualization import draw_step, draw


def run_derivation(output_dir: str = "visualizations/derivation"):
    """
    Uruchamia pełny wywód i zapisuje wizualizacje.

    Args:
        output_dir: Katalog wyjściowy dla obrazów
    """
    # Utwórz katalog wyjściowy
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 70)
    print("WIZUALIZACJA WYWODU DLA GRUPY 5")
    print("=" * 70)
    print(f"Katalog wyjściowy: {output_dir}")
    print()

    # Utwórz sterownik i wykonaj wywód
    driver = HexagonalMeshDriver(radius=10.0)
    history = driver.run_full_derivation()

    # Zapisz wizualizację każdego kroku
    print("\n" + "-" * 70)
    print("GENEROWANIE WIZUALIZACJI")
    print("-" * 70)

    for step in history:
        filename = os.path.join(
            output_dir, f"step_{step.step_number:02d}_{step.production_name}.png"
        )
        title = f"Krok {step.step_number}: {step.production_name}\n{step.description}"
        draw(step.graph_state, filename=filename, title=title)
        print(f"  ✓ {filename}")

    # Wygeneruj podsumowanie
    summary_file = os.path.join(output_dir, "SUMMARY.md")
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write("# Wywód dla Grupy 5 - Siatka Heksagonalna\n\n")
        f.write("## Sekwencja kroków\n\n")
        f.write("| Krok | Produkcja | Opis |\n")
        f.write("|------|-----------|------|\n")
        for step in history:
            f.write(
                f"| {step.step_number} | {step.production_name} | {step.description} |\n"
            )
        f.write("\n## Obrazy\n\n")
        for step in history:
            img_name = f"step_{step.step_number:02d}_{step.production_name}.png"
            f.write(f"### Krok {step.step_number}: {step.production_name}\n")
            f.write(f"![{step.description}]({img_name})\n\n")

    print(f"\n  ✓ Podsumowanie zapisane: {summary_file}")

    print("\n" + "=" * 70)
    print(f"WYWÓD ZAKOŃCZONY - Wygenerowano {len(history)} obrazów")
    print("=" * 70)

    return history


def generate_single_graph_visualization():
    """Generuje pojedynczą wizualizację końcowego grafu."""
    output_dir = "visualizations/derivation"
    os.makedirs(output_dir, exist_ok=True)

    driver = HexagonalMeshDriver(radius=10.0)
    driver.run_full_derivation()

    final_graph = driver.get_current_graph()
    filename = os.path.join(output_dir, "final_graph.png")
    draw(final_graph, filename=filename, title="Graf końcowy po wywodzie")
    print(f"Zapisano: {filename}")


if __name__ == "__main__":
    run_derivation()
