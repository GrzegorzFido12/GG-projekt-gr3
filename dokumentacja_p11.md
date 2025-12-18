# Dokumentacja Produkcji P11

## Gramatyka Hipergrafow - Metoda PolyDPG

### Opis Produkcji P11

**Produkcja P11** lamie elementy szesciokatne oznaczone do podzialu (refinement), jesli wszystkie ich krawedzie sa podzielone.

---

## Lewa strona produkcji

Produkcja P11 wyszukuje element szesciokatny o nastepujacych wlasciwosciach:
- **Etykieta**: `Q` (element)
- **R = 1**: oznaczony do podzialu (refinement)
- Wszystkie krawedzie **E** maja **R = 0** (podzielone)

```
     v1 ----E(R=0, B=1)---- v2
      |                    |
     v6 ----E(R=0, B=1)---- v3
      |                    |
     v5 ----E(R=0, B=1)---- v4
```

## Prawa strona produkcji

Po zastosowaniu produkcji P11:
1. Tworzony jest nowy **wezel centralny** w srodku elementu
2. Szesciokat jest dzielony na mniejsze elementy (trojkaty lub czworokaty)
3. Nowe elementy maja **R=0** (nie sa oznaczone do podzialu)

```
     v1 ----E(R=0, B=1)---- v2
      |\                  /|
      | \                / |
     v6  \----Q(R=0)----  v3
      | /                \ |
      |/                  \|
     v5 ----E(R=0, B=1)---- v4
```

---

## Implementacja

### Sprawdzanie izomorfizmu z lewa strona produkcji

Metoda `is_isomorphic_to_left_side()` sprawdza, czy podgraf jest izomorficzny z lewa strona produkcji poprzez weryfikacje:

```python
if len(nodes) != 6 or len(edges) != 7:
    return False

edge_counts = {
    "E": sum(1 for e in edges if e.hypertag == "E" and e.R == 0),
    "Q": sum(1 for e in edges if e.hypertag == "Q" and e.R == 1),
}

return edge_counts["E"] == 6 and edge_counts["Q"] == 1
```

### Decyzja o miejscu zastosowania produkcji

Produkcja jest stosowana do **pierwszego znalezionego** elementu szesciokatnego oznaczonego do podzialu. Metoda `find_match()` przeszukuje graf:

```python
def find_match(self, graph: Graph) -> Optional[HyperEdge]:
    for edge in graph.hyperedges:
        if edge.hypertag == "Q" and edge.R == 1:
            hexagon_nodes = edge.nodes
            if all(
                any(e.nodes == (hexagon_nodes[i], hexagon_nodes[(i + 1) % len(hexagon_nodes)]) and e.R == 0
                    for e in graph.hyperedges)
                for i in range(len(hexagon_nodes))
            ):
                return edge
    return None
```

### Wyszukiwanie podgrafu izomorficznego w duzym grafie

Metoda `find_all_matches()` znajduje wszystkie pasujace elementy w grafie:

```python
def find_all_matches(self, graph: Graph) -> list:
    matches = []
    for edge in graph.hyperedges:
        if edge.hypertag == "Q" and edge.R == 1:
            hexagon_nodes = edge.nodes
            if all(
                any(e.nodes == (hexagon_nodes[i], hexagon_nodes[(i + 1) % len(hexagon_nodes)]) and e.R == 0
                    for e in graph.hyperedges)
                for i in range(len(hexagon_nodes))
            ):
                matches.append(edge)
    return matches
```

### Sprawdzanie poprawnosci wynikowego grafu

Po zastosowaniu produkcji sprawdzamy:

1. **Liczba wezlow**: powinna zwiekszyc sie o 1 (nowy wezel centralny)
2. **Liczba krawedzi Q**: powinna zwiekszyc sie o liczbe mniejszych elementow
3. **Atrybuty nowych elementow**: R=0
4. **Pozycja wezla centralnego**: srodek oryginalnego elementu
5. **Zachowanie innych krawedzi**: pozostale krawedzie powinny byc nienaruszone

---

## Przeprowadzone Testy

### 1. Test podstawowego elementu szesciokatnego (test_p11_basic_hexagon)

**Opis**: Test P11 na prostym szesciokacie oznaczonym do podzialu.

**Graf przed**:
- 6 wezlow: v1, v2, v3, v4, v5, v6
- 6 krawedzi E z R=0, B=1
- 1 krawedz Q z R=1

**Graf po**:
- 7 wezlow (dodany wezel centralny)
- 6 krawedzi E z R=0, B=1
- 6 krawedzi Q z R=0

**Wynik**: PASSED

Wizualizacja: `visualizations/test_p11_basic_before.png`, `visualizations/test_p11_basic_after.png`

---

### 2. Test nieoznaczonego szesciokata (test_p11_cannot_apply_to_unmarked_hexagon)

**Opis**: Test weryfikuje, czy produkcja P11 nie jest stosowana do szesciokatow, ktore nie sa oznaczone do podzialu.

**Graf przed**:
- 6 wezlow: v1, v2, v3, v4, v5, v6
- 6 krawedzi E z R=0, B=1
- 1 krawedz Q z R=0

**Graf po**:
- Bez zmian

**Wynik**: PASSED

Wizualizacja: `visualizations/test_p11_unmarked_before.png`, `visualizations/test_p11_unmarked_after.png`

---

### 3. Test zachowania innych krawedzi (test_p11_preserves_other_edges)

**Opis**: Test sprawdza, czy krawedzie niezalezne od szesciokata pozostaja nienaruszone po zastosowaniu produkcji P11.

**Graf przed**:
- 6 wezlow: v1, v2, v3, v4, v5, v6
- 6 krawedzi E z R=0, B=1
- 1 krawedz Q z R=1
- 1 dodatkowa krawedz niezalezna

**Graf po**:
- 7 wezlow (dodany wezel centralny)
- 6 krawedzi E z R=0, B=1
- 6 krawedzi Q z R=0
- 1 dodatkowa krawedz niezalezna (nienaruszona)

**Wynik**: PASSED

Wizualizacja: `visualizations/test_p11_edges_before.png`, `visualizations/test_p11_edges_after.png`

---

### 4. Test pozycji wezla centralnego (test_p11_hanging_node_position)

**Opis**: Test sprawdza, czy nowy wezel centralny jest poprawnie umiejscowiony w srodku szesciokata.

**Graf przed**:
- 6 wezlow: v1, v2, v3, v4, v5, v6
- 6 krawedzi E z R=0, B=1
- 1 krawedz Q z R=1

**Graf po**:
- 7 wezlow (dodany wezel centralny w srodku)
- 6 krawedzi E z R=0, B=1
- 6 krawedzi Q z R=0

**Wynik**: PASSED

Wizualizacja: `visualizations/test_p11_hanging_before.png`, `visualizations/test_p11_hanging_after.png`

---

### 5. Test wielu szesciokatow (test_p11_multiple_hexagons)

**Opis**: Test weryfikuje, czy produkcja P11 przeksztalca tylko oznaczony szesciokat, pozostawiajac inne szesciokaty bez zmian.

**Graf przed**:
- 12 wezlow: v1, v2, ..., v12
- 12 krawedzi E z R=0, B=1
- 2 krawedzie Q z R=1 (tylko jeden oznaczony do podzialu)

**Graf po**:
- 13 wezlow (dodany wezel centralny dla oznaczonego szesciokata)
- 12 krawedzi E z R=0, B=1
- 6 krawedzi Q z R=0 (dla podzielonego szesciokata)
- 1 krawedz Q z R=1 (dla niepodzielonego szesciokata)

**Wynik**: PASSED

Wizualizacja: `visualizations/test_p11_multiple_before.png`, `visualizations/test_p11_multiple_after.png`

---