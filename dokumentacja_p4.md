# Dokumentacja Produkcji P4

## Gramatyka Hipergrafow - Metoda PolyDPG

### Opis Produkcji P4

**Produkcja P4** lamie krawedzie brzegowe oznaczone do podzialu (refinement). Jest to czesc procesu adaptacji siatki w metodzie PolyDPG.

---

## Lewa strona produkcji

Produkcja P4 wyszukuje krawedz o nastepujacych wlasciwosciach:
- **Etykieta**: `E` (krawedz)
- **B = 1**: krawedz brzegowa (boundary)
- **R = 1**: krawedz oznaczona do podzialu (refinement)

```
     v1 ----E(R=1, B=1)---- v2
```

## Prawa strona produkcji

Po zastosowaniu produkcji P4:
1. Tworzony jest nowy **wezel wiszacy** (hanging node) w srodku krawedzi
2. Oryginalna krawedz jest zastepowana **dwoma nowymi krawedziami**
3. Nowe krawedzie maja **R=0** (nie sa juz oznaczone do podzialu)

```
     v1 ----E(R=0, B=1)---- h ----E(R=0, B=1)---- v2
```

gdzie `h` to wezel wiszacy o wspolrzednych:
- `x = (v1.x + v2.x) / 2`
- `y = (v1.y + v2.y) / 2`

---

## Implementacja

### Sprawdzanie izomorfizmu z lewa strona produkcji

Metoda `is_isomorphic_to_left_side()` sprawdza, czy podgraf jest izomorficzny z lewa strona produkcji poprzez weryfikacje:

```python
def is_isomorphic_to_left_side(self, subgraph: Graph) -> bool:
    nodes = subgraph.nodes
    edges = subgraph.hyperedges
    
    # Musi miec dokladnie 2 wezly
    if len(nodes) != 2:
        return False
    
    # Musi miec dokladnie 1 krawedz
    if len(edges) != 1:
        return False
    
    edge = edges[0]
    
    # Krawedz musi miec etykiete 'E', byc brzegowa (B=1) i oznaczona (R=1)
    if edge.hypertag != "E":
        return False
    if edge.B != 1:
        return False
    if edge.R != 1:
        return False
    
    # Krawedz musi laczyc oba wezly
    if set(edge.nodes) != set(nodes):
        return False
    
    return True
```

### Decyzja o miejscu zastosowania produkcji

Produkcja jest stosowana do **pierwszej znalezionej** krawedzi brzegowej oznaczonej do podzialu. Metoda `find_match()` przeszukuje graf:

```python
def find_match(self, graph: Graph) -> Optional[HyperEdge]:
    for edge in graph.hyperedges:
        if edge.hypertag == "E" and edge.R == 1 and edge.B == 1:
            return edge
    return None
```

### Wyszukiwanie podgrafu izomorficznego w duzym grafie

Metoda `find_all_matches()` znajduje wszystkie pasujace krawedzie w grafie:

```python
def find_all_matches(self, graph: Graph) -> list:
    matches = []
    for edge in graph.hyperedges:
        if edge.hypertag == "E" and edge.R == 1 and edge.B == 1:
            matches.append(edge)
    return matches
```

Algorytm przeszukuje wszystkie hiperkrawedzie grafu i sprawdza:
1. Czy etykieta to `E`
2. Czy R = 1 (oznaczona do podzialu)
3. Czy B = 1 (krawedz brzegowa)

### Sprawdzanie poprawnosci wynikowego grafu

Po zastosowaniu produkcji sprawdzamy:

1. **Liczba wezlow**: powinna zwiekszyc sie o 1 (nowy wezel wiszacy)
2. **Liczba krawedzi E**: powinna zwiekszyc sie o 1 (1 -> 2)
3. **Atrybuty nowych krawedzi**: R=0, B=1
4. **Pozycja wezla wiszacego**: srodek oryginalnej krawedzi
5. **Zachowanie innych krawedzi**: pozostale krawedzie powinny byc nienaruszone

---

## Przeprowadzone Testy

### 1. Test podstawowej krawedzi brzegowej (test_p4_basic_boundary_edge)

**Opis**: Test P4 na prostej krawedzi brzegowej oznaczonej do podzialu.

**Graf przed**:
- 2 wezly: v1(0,0), v2(4,0)
- 1 krawedz E z R=1, B=1

**Graf po**:
- 3 wezly (dodany wezel wiszacy w (2,0))
- 2 krawedzie E z R=0, B=1

**Wynik**: PASSED

Wizualizacja: `visualizations/test_p4_basic_before.png`, `visualizations/test_p4_basic_after.png`

---

### 2. Test niemoznosci zastosowania do krawedzi wspoldzielonej (test_p4_cannot_apply_to_shared_edge)

**Opis**: P4 nie powinno byc stosowane do krawedzi wspoldzielonych (B=0).

**Graf**:
- 2 wezly
- 1 krawedz E z R=1, B=0 (wspoldzielona, nie brzegowa)

**Wynik**: PASSED (produkcja nie zostala zastosowana)

---

### 3. Test niemoznosci zastosowania do nieoznaczonej krawedzi (test_p4_cannot_apply_to_unmarked_edge)

**Opis**: P4 nie powinno byc stosowane do krawedzi nieoznaczonych do podzialu.

**Graf**:
- 2 wezly
- 1 krawedz E z R=0, B=1 (brzegowa, ale nieoznaczona)

**Wynik**: PASSED (produkcja nie zostala zastosowana)

---

### 4. Test na kwadracie (test_p4_on_square)

**Opis**: Test P4 na kwadracie z jedna krawedzia brzegowa oznaczona do podzialu.

**Graf przed**:
- 4 wezly (kwadrat)
- 4 krawedzie E (3 z R=0, 1 z R=1)
- 1 hiperkrawedz Q

**Graf po**:
- 5 wezlow
- 5 krawedzi E (wszystkie R=0)
- 1 hiperkrawedz Q (zachowana)

**Wynik**: PASSED

Wizualizacja: `visualizations/test_p4_square_before.png`, `visualizations/test_p4_square_after.png`

---

### 5. Test na zlozonej siatce (test_p4_on_complex_mesh)

**Opis**: Test P4 na siatce z wieloma elementami.

**Graf przed**:
- 6 wezlow
- Wiele krawedzi E (brzegowych i wspoldzielonych)
- 2 hiperkrawedzie Q

**Wynik**: PASSED (tylko krawedz brzegowa oznaczona zostala podzielona)

Wizualizacja: `visualizations/test_p4_complex_before.png`, `visualizations/test_p4_complex_after.png`

---

### 6. Test zachowania innych krawedzi (test_p4_preserves_other_edges)

**Opis**: Sprawdzenie, czy P4 nie modyfikuje krawedzi, ktore nie sa podzielone.

**Wynik**: PASSED

---

### 7. Test pozycji wezla wiszacego (test_p4_hanging_node_position)

**Opis**: Weryfikacja, czy wezel wiszacy jest tworzony we wlasciwym punkcie srodkowym.

**Graf przed**:
- Wezly: p1(2,6), p2(10,14)
- Krawedz ukosna

**Graf po**:
- Wezel wiszacy w (6, 10) - punkt srodkowy

**Wynik**: PASSED

Wizualizacja: `visualizations/test_p4_diagonal_before.png`, `visualizations/test_p4_diagonal_after.png`

---

### 8. Test sprawdzania izomorfizmu (test_p4_isomorphism_check)

**Opis**: Test metody `is_isomorphic_to_left_side()`.

**Przypadki testowe**:
- Poprawna lewa strona (E, R=1, B=1)
- Niepoprawna lewa strona (R=0)
- Niepoprawna lewa strona (B=0)

**Wynik**: PASSED

---

### 9. Test brakujacego wezla (test_p4_missing_node)

**Opis**: Test obslugi grafow z brakujacymi wezlami.

**Wynik**: PASSED (produkcja nie zostala zastosowana)

---

### 10. Test zlej etykiety krawedzi (test_p4_wrong_edge_label)

**Opis**: P4 nie powinno byc stosowane do krawedzi z etykieta inna niz E.

**Wynik**: PASSED

---

### 11. Test znajdowania wielu dopasowan (test_p4_find_all_matches)

**Opis**: Test metody `find_all_matches()` dla wielu krawedzi brzegowych oznaczonych do podzialu.

**Graf przed**:
- 4 wezly w linii
- 3 krawedzie E z R=1, B=1

**Po 3 zastosowaniach P4**:
- 7 wezlow
- 6 krawedzi E z R=0

**Wynik**: PASSED

Wizualizacja: `visualizations/test_p4_multiple_before.png`, `visualizations/test_p4_multiple_after.png`

---

### 12. Test osadzenia w wiekszym grafie (test_p4_embedded_in_larger_graph)

**Opis**: Test P4 gdy pasujacy podgraf jest czescia wiekszego grafu.

**Graf przed**:
- Siatka 3x3 (9 wezlow)
- Wiele krawedzi (brzegowych i wewnetrznych)
- 4 hiperkrawedzie Q

**Graf po**:
- 10 wezlow
- Wszystkie hiperkrawedzie Q zachowane
- Tylko jedna krawedz brzegowa podzielona

**Wynik**: PASSED

Wizualizacja: `visualizations/test_p4_large_mesh_before.png`, `visualizations/test_p4_large_mesh_after.png`

---

### 13. Test trojkata (test_p4_triangle_boundary)

**Opis**: Test P4 na trojkacie z krawedziami brzegowymi.

**Graf przed**:
- 3 wezly (trojkat)
- 3 krawedzie E (1 z R=1)

**Graf po**:
- 4 wezly
- 4 krawedzie E (wszystkie R=0)

**Wynik**: PASSED

Wizualizacja: `visualizations/test_p4_triangle_before.png`, `visualizations/test_p4_triangle_after.png`

---

## Podsumowanie Testow

| Numer | Nazwa testu                      | Status |
|-------|----------------------------------|--------|
| 1     | P4 BASIC BOUNDARY EDGE           | PASSED |
| 2     | P4 CANNOT APPLY TO SHARED EDGE   | PASSED |
| 3     | P4 CANNOT APPLY TO UNMARKED EDGE | PASSED |
| 4     | P4 ON SQUARE                     | PASSED |
| 5     | P4 ON COMPLEX MESH               | PASSED |
| 6     | P4 PRESERVES OTHER EDGES         | PASSED |
| 7     | P4 HANGING NODE POSITION         | PASSED |
| 8     | P4 ISOMORPHISM CHECK             | PASSED |
| 9     | P4 MISSING NODE                  | PASSED |
| 10    | P4 WRONG EDGE LABEL              | PASSED |
| 11    | P4 FIND ALL MATCHES              | PASSED |
| 12    | P4 EMBEDDED IN LARGER GRAPH      | PASSED |
| 13    | P4 TRIANGLE BOUNDARY             | PASSED |

**Wynik koncowy: 13/13 testow zaliczonych**

---

## Uruchomienie testow

```bash
# Instalacja zaleznosci
pip install -r requirements.txt

# Uruchomienie testow P4
python test_p4.py

# Uruchomienie za pomoca pytest
pytest test_p4.py -v
```

---

## Struktura plikow

```
graph_model.py        # Model grafu i hiperkrawedzi
production_base.py    # Klasa bazowa produkcji
p4.py                 # Implementacja produkcji P4
test_p4.py            # Testy jednostkowe P4
visualization.py      # Wizualizacja grafow
visualizations/       # Folder z wizualizacjami
    test_p4_*.png     # Wizualizacje testow P4
dokumentacja_p4.md    # Ten plik dokumentacji
```

---
