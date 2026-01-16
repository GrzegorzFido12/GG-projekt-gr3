"""
Sterownik (Driver) - Procedura Pilotująca dla Grupy 5

Implementuje sekwencję produkcji dla wywodu siatki heksagonalnej:
1. Utworzenie grafu początkowego (heksagon)
2. Oznaczenie elementu S do podziału (P9: R=0 -> R=1)
3. Oznaczenie krawędzi E do podziału (P10)
4. Łamanie krawędzi brzegowych (P4)
5. Łamanie krawędzi współdzielonych (P3)

Autor: Grupa 5 - GG Projekt
"""

import math
import copy
from typing import List, Tuple, Optional
from graph_model import Graph, Node, HyperEdge

# Import produkcji
from productions.p9 import P9
from productions.p10 import P10
from productions.p4 import P4
from productions.p3 import P3


class DerivationStep:
    """Reprezentuje pojedynczy krok wywodu."""

    def __init__(
        self,
        step_number: int,
        production_name: str,
        description: str,
        graph_state: Graph,
    ):
        self.step_number = step_number
        self.production_name = production_name
        self.description = description
        self.graph_state = graph_state


class HexagonalMeshDriver:
    """
    Sterownik wywodu dla siatki heksagonalnej (Grupa 5).

    Odpowiada za:
    - Utworzenie grafu początkowego
    - Sekwencyjne stosowanie produkcji w odpowiedniej kolejności
    - Zapisywanie historii wywodu
    """

    def __init__(self, radius: float = 10.0, center: Tuple[float, float] = (0, 0)):
        self.radius = radius
        self.center = center
        self.graph = Graph()
        self.history: List[DerivationStep] = []
        self.step_counter = 0

    def create_initial_hexagon(self) -> None:
        """
        Tworzy początkowy graf heksagonalny.

        Graf zawiera:
        - 6 wierzchołków narożnych
        - 1 hiperkrawędź S (element heksagonalny) z R=0
        - 6 krawędzi E (brzegowe) z B=1, R=0
        """
        self.graph = Graph()
        nodes = []

        # Tworzenie 6 wierzchołków
        for i in range(6):
            angle = 2 * math.pi * i / 6
            x = self.center[0] + self.radius * math.cos(angle)
            y = self.center[1] + self.radius * math.sin(angle)
            node = Node(x, y, f"v{i}")
            nodes.append(node)
            self.graph.add_node(node)

        # Hiperkrawędź S - element heksagonalny z R=0 (nie oznaczony do podziału)
        self.graph.add_edge(HyperEdge(tuple(nodes), "S", boundary=False, R=0, B=0))

        # Krawędzie E - brzegowe (B=1), nie oznaczone do podziału (R=0)
        for i in range(6):
            u = nodes[i]
            v = nodes[(i + 1) % 6]
            self.graph.add_edge(HyperEdge((u, v), "E", boundary=True, R=0, B=1))

        self._record_step("INIT", "Utworzenie początkowego heksagonu")

    def _record_step(self, production_name: str, description: str) -> None:
        """Zapisuje bieżący stan grafu jako krok wywodu."""
        self.step_counter += 1
        step = DerivationStep(
            step_number=self.step_counter,
            production_name=production_name,
            description=description,
            graph_state=copy.deepcopy(self.graph),
        )
        self.history.append(step)
        print(f"Krok {self.step_counter}: {production_name} - {description}")

    def apply_p9_mark_hexagon(self) -> bool:
        """
        Stosuje produkcję P9: Oznacza heksagon S do podziału (R=0 -> R=1).

        Returns:
            True jeśli produkcja została zastosowana, False w przeciwnym razie.
        """
        prod = P9()
        if prod.can_apply(self.graph):
            result = self.graph.apply(prod)
            if result > 0:
                self._record_step("P9", "Oznaczenie heksagonu S do podziału (R=1)")
                return True
        return False

    def apply_p10_mark_edges(self) -> bool:
        """
        Stosuje produkcję P10: Oznacza krawędzie E heksagonu do podziału.

        Returns:
            True jeśli produkcja została zastosowana, False w przeciwnym razie.
        """
        prod = P10()
        if prod.can_apply(self.graph):
            result = self.graph.apply(prod)
            if result > 0:
                self._record_step(
                    "P10", "Oznaczenie krawędzi E heksagonu do podziału (R=1)"
                )
                return True
        return False

    def apply_p4_break_boundary_edges(self) -> int:
        """
        Stosuje produkcję P4 wielokrotnie: Łamie krawędzie brzegowe oznaczone do podziału.

        Returns:
            Liczba zastosowanych produkcji P4.
        """
        prod = P4()
        count = 0
        while prod.can_apply(self.graph):
            result = self.graph.apply(prod)
            if result > 0:
                count += 1
                self._record_step(
                    "P4", f"Łamanie krawędzi brzegowej (tworzy węzeł wiszący)"
                )
            else:
                break
        return count

    def apply_p3_break_shared_edges(self) -> int:
        """
        Stosuje produkcję P3 wielokrotnie: Łamie krawędzie współdzielone (nie-brzegowe).

        Returns:
            Liczba zastosowanych produkcji P3.
        """
        prod = P3()
        count = 0
        while prod.can_apply(self.graph):
            result = self.graph.apply(prod)
            if result > 0:
                count += 1
                self._record_step("P3", "Łamanie krawędzi współdzielonej")
            else:
                break
        return count

    def run_full_derivation(self) -> List[DerivationStep]:
        """
        Wykonuje pełny wywód dla Grupy 5.

        Sekwencja:
        1. Tworzenie początkowego heksagonu
        2. P9: Oznaczenie elementu S do podziału
        3. P10: Oznaczenie krawędzi E do podziału
        4. P4: Łamanie wszystkich krawędzi brzegowych
        5. P3: Łamanie krawędzi współdzielonych (jeśli są)

        Returns:
            Lista kroków wywodu.
        """
        print("=" * 60)
        print("WYWÓD DLA GRUPY 5 - SIATKA HEKSAGONALNA")
        print("=" * 60)

        # Faza 1: Tworzenie grafu
        print("\n[FAZA 1] Tworzenie grafu początkowego")
        self.create_initial_hexagon()

        # Faza 2: Oznaczenie heksagonu do podziału
        print("\n[FAZA 2] Oznaczenie elementu do podziału")
        self.apply_p9_mark_hexagon()

        # Faza 3: Oznaczenie krawędzi do podziału
        print("\n[FAZA 3] Oznaczenie krawędzi do podziału")
        self.apply_p10_mark_edges()

        # Faza 4: Łamanie krawędzi brzegowych
        print("\n[FAZA 4] Łamanie krawędzi brzegowych")
        p4_count = self.apply_p4_break_boundary_edges()
        print(f"   Zastosowano P4 {p4_count} razy")

        # Faza 5: Łamanie krawędzi współdzielonych
        print("\n[FAZA 5] Łamanie krawędzi współdzielonych")
        p3_count = self.apply_p3_break_shared_edges()
        print(f"   Zastosowano P3 {p3_count} razy")

        print("\n" + "=" * 60)
        print(f"WYWÓD ZAKOŃCZONY - Łącznie {len(self.history)} kroków")
        print("=" * 60)

        return self.history

    def get_current_graph(self) -> Graph:
        """Zwraca bieżący stan grafu."""
        return self.graph

    def get_history(self) -> List[DerivationStep]:
        """Zwraca historię wywodu."""
        return self.history


def create_driver() -> HexagonalMeshDriver:
    """Tworzy i zwraca instancję sterownika."""
    return HexagonalMeshDriver()


if __name__ == "__main__":
    # Przykładowe uruchomienie
    driver = create_driver()
    history = driver.run_full_derivation()

    print("\n\nPodsumowanie kroków:")
    for step in history:
        print(f"  {step.step_number}. {step.production_name}: {step.description}")
