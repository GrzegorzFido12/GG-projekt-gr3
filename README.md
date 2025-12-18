Implementacja gramatyk grafowych dla adaptacji siatek wielokątnych (PolyDPG).

## Instalacja

```bash
pip install networkx matplotlib --break-system-packages
```

## Struktura plików

```
graph_model.py      - Model grafu
production_base.py  - Klasa bazowa dla produkcji
p0.py              - Produkcja P0 (oznaczanie elementów)
visualization.py    - Rysowanie grafów
test_p0.py         - Testy P0
```

## Jak to działa?

### Graf
- **Node** - węzeł z pozycją (x, y) i etykietą
- **HyperEdge** - hiperkrawędź łącząca 2+ węzły, przedstawiona jako Node ze względu na ograniczenia networkx
- **Graph** - kontener na węzły i hiperkrawędzie

### Atrybuty hiperkrawędzi
- **R** - czy oznaczona do refinementu (0=nie, 1=tak)
- **B** - czy brzegowa (0=nie, 1=tak)
- **hypertag** - typ (Q=element, E=krawędź)


### Wizualizacja
- **Żółte kółka** - węzły (wierzchołki wielokąta)
- **Czerwone kółka** - hiperkrawędzie (elementy, krawędzie)
- **Szare linie** - połączenia

## Wymagania

- Python 3.8+
- NetworkX
- Matplotlib
