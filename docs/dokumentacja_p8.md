# Dokumentacja Produkcji P8

## Gramatyka Hipergrafów – Metoda PolyDPG

### Opis Produkcji P8

**Produkcja P8** jest operacją finalizującą proces podziału (refinementu) elementu pięciokątnego. Jest ona stosowana w momencie, gdy otoczenie elementu wymusiło już podział wszystkich jego krawędzi brzegowych. Produkcja ta przekształca jeden element pięciokątny w pięć mniejszych elementów czworokątnych, wykorzystując istniejące węzły wiszące na brzegach.

---

## Lewa strona produkcji

Produkcja P8 wyszukuje podgraf o następujących właściwościach:

* **Hiperkrawędź centralna**: typu `P` (Pentagon)
* **R = 1**: element oznaczony do podziału (refinement)
* **5 wierzchołków narożnych**: element musi być rozpięty na dokładnie 5 węzłach
* **5 węzłów wiszących**: na każdym boku pięciokąta musi znajdować się węzeł wiszący (`hanging=True`)

```
        v0
       /  \
     h4    h0
     /      \
   v4        v1
    |        |
   h3       h1
    |        |
   v3---h2---v2

   + HyperEdge P(v0,v1,v2,v3,v4) z R=1
```

## Prawa strona produkcji

Po zastosowaniu produkcji P8:

1. Tworzony jest nowy **węzeł centralny** w środku ciężkości pięciokąta.
2. Węzeł centralny łączony jest krawędziami wewnętrznymi (`boundary=False`) ze wszystkimi węzłami wiszącymi.
3. Oryginalna hiperkrawędź `P` zostaje usunięta.
4. Powstaje **5 nowych elementów czworokątnych** (typu `Q`).
5. Nowe elementy mają **R=0** (nie są już oznaczone do podziału).

```
        v0
       /  \
     h4----h0
     /  Q   \
   v4   *    v1      (* = center)
    | Q | Q  |
   h3---*---h1
    |   Q   |
   v3---h2---v2
```

gdzie `center` to węzeł centralny o współrzędnych:

* `x = (v0.x + v1.x + v2.x + v3.x + v4.x) / 5`
* `y = (v0.y + v1.y + v2.y + v3.y + v4.y) / 5`

Każdy element `Q` jest zdefiniowany przez czwórkę węzłów: `[narożnik, sąsiedni węzeł wiszący, środek, poprzedni węzeł wiszący]`.

---

## Implementacja

### Sprawdzanie izomorfizmu z lewą stroną produkcji

Metoda `can_apply()` w połączeniu z `find_match()` sprawdza, czy podgraf jest izomorficzny z lewą stroną produkcji poprzez weryfikację:

```python
def can_apply(self, graph: Graph) -> bool:
    return self.find_match(graph) is not None

def find_match(self, graph: Graph) -> Optional[HyperEdge]:
    for p_edge in graph.hyperedges:
        # Szukamy hiperkrawędzi P, R=1, 5 wierzchołków
        if p_edge.hypertag == "P" and p_edge.R == 1 and len(p_edge.nodes) == 5:
            corners = list(p_edge.nodes)
            hanging_nodes = []
            found_all_hanging = True

            # Sprawdzamy każdy bok pięciokąta
            for i in range(5):
                u = corners[i]
                v = corners[(i + 1) % 5]

                # Szukamy węzła wiszącego h pomiędzy u i v
                h_found = None

                # Znajdź sąsiadów u połączonych krawędzią E
                neighbors_u = set()
                for edge in graph.hyperedges:
                    if edge.hypertag == "E" and u in edge.nodes:
                        other = edge.nodes[1] if edge.nodes[0] == u else edge.nodes[0]
                        neighbors_u.add(other)

                # Sprawdź czy któryś z sąsiadów jest odpowiednim węzłem wiszącym
                for h_cand in neighbors_u:
                    # Węzeł wiszący nie może być wierzchołkiem narożnym
                    if h_cand == u or h_cand == v:
                        continue

                    # Wymagamy, aby węzeł miał flagę hanging=True
                    if not h_cand.hanging:
                        continue

                    # Sprawdzamy czy węzeł jest połączony również z v
                    is_connected_to_v = False
                    for edge in graph.hyperedges:
                        if edge.hypertag == "E" and h_cand in edge.nodes and v in edge.nodes:
                            is_connected_to_v = True
                            break

                    if is_connected_to_v:
                        h_found = h_cand
                        break

                if h_found:
                    hanging_nodes.append(h_found)
                else:
                    found_all_hanging = False
                    break

            if found_all_hanging:
                all_nodes = corners + hanging_nodes
                return HyperEdge(tuple(all_nodes), "MATCH_CONTAINER", R=1)

    return None
```

Warunki izomorfizmu:
1. Musi istnieć hiperkrawędź typu `P` z atrybutem `R=1`.
2. Hiperkrawędź musi mieć dokładnie 5 węzłów (narożników).
3. Każdy bok pięciokąta (para sąsiednich narożników) musi mieć węzeł wiszący.
4. Węzeł wiszący musi mieć flagę `hanging=True`.
5. Węzeł wiszący musi być połączony krawędziami `E` z oboma narożnikami danego boku.

### Decyzja o miejscu zastosowania produkcji

Produkcja jest stosowana do **pierwszego znalezionego** pięciokąta spełniającego warunki. Metoda `find_match()` przeszukuje graf i zwraca pierwszy pasujący element:

```python
def find_match(self, graph: Graph) -> Optional[HyperEdge]:
    for p_edge in graph.hyperedges:
        if p_edge.hypertag == "P" and p_edge.R == 1 and len(p_edge.nodes) == 5:
            # ... sprawdzenie węzłów wiszących ...
            if found_all_hanging:
                return HyperEdge(tuple(all_nodes), "MATCH_CONTAINER", R=1)
    return None
```

### Wyszukiwanie podgrafu izomorficznego w dużym grafie

Algorytm przeszukuje wszystkie hiperkrawędzie grafu i dla każdej potencjalnej kandydatury:

1. Filtruje hiperkrawędzie typu `P` z `R=1` i 5 węzłami.
2. Dla każdego boku pięciokąta (5 boków):
   - Znajduje sąsiadów pierwszego narożnika połączonych krawędzią `E`.
   - Sprawdza, czy któryś z sąsiadów jest węzłem wiszącym (`hanging=True`).
   - Weryfikuje połączenie węzła wiszącego z drugim narożnikiem.
3. Jeśli wszystkie 5 boków ma węzły wiszące, zwraca kontener z 10 węzłami.

### Sprawdzanie poprawności wynikowego grafu

Po zastosowaniu produkcji sprawdzamy:

1. **Liczba węzłów**: powinna zwiększyć się o 1 (nowy węzeł centralny).
2. **Liczba elementów Q**: powinno powstać dokładnie 5 nowych czworokątów.
3. **Usunięcie elementu P**: oryginalny pięciokąt powinien zniknąć.
4. **Atrybuty nowych elementów**: wszystkie Q mają `R=0`.
5. **Pozycja węzła centralnego**: środek ciężkości 5 narożników.
6. **Zachowanie kontekstu**: pozostałe elementy grafu nie powinny być zmienione.

---

## Przeprowadzone Testy

### 1. Test podstawowy izomorfizmu (test_apply_isomorphic)

**Opis**: Fundamentalny test sprawdzający aplikację produkcji do idealnego grafu wejściowego (pięciokąt foremny z idealnie podzielonymi krawędziami).

**Graf przed**:

* 10 węzłów: 5 narożnych + 5 wiszących
* 1 hiperkrawędź P z R=1
* 10 krawędzi E (po 2 na każdy bok)

**Graf po**:

* 11 węzłów (dodany węzeł centralny)
* 5 hiperkrawędzi Q z R=0
* 15 krawędzi E (10 brzegowych + 5 wewnętrznych do centrum)

**Wynik**: PASSED

|  **Przed**                                    | **Po**                                  |
|----------------------------------------------|------------------------------------------|
| ![](../visualizations/p8_visualizations/test_apply_isomorphic_before.png) | ![](../visualizations/p8_visualizations/test_apply_isomorphic_after.png) |

---

### 2. Test brakującego węzła wiszącego (test_apply_missing_break)

**Opis**: Test negatywny sprawdzający, czy produkcja NIE aplikuje się, gdy jedna krawędź nie jest podzielona (brak węzła wiszącego).

**Graf**:

* Pięciokąt z 4 podzielonymi bokami
* 1 bok ciągły (bez węzła wiszącego)

**Wynik**: PASSED (produkcja nie została zastosowana)

|  **Przed**                                    | **Po**                                  |
|----------------------------------------------|------------------------------------------|
| ![](../visualizations/p8_visualizations/test_apply_missing_break_before.png) | ![](../visualizations/p8_visualizations/test_apply_missing_break_after.png) |

---

### 3. Test elementu z R=0 (test_apply_R0)

**Opis**: Test negatywny sprawdzający, czy produkcja NIE aplikuje się do elementu z R=0 (nieoznaczonego do podziału).

**Graf**:

* Idealny pięciokąt z wszystkimi węzłami wiszącymi
* Hiperkrawędź P z R=0

**Wynik**: PASSED (produkcja nie została zastosowana)

|  **Przed**                                    | **Po**                                  |
|----------------------------------------------|------------------------------------------|
| ![](../visualizations/p8_visualizations/test_apply_R0_before.png) | ![](../visualizations/p8_visualizations/test_apply_R0_after.png) |

---

### 4. Test współrzędnych środka (test_center_coordinates)

**Opis**: Weryfikacja poprawności matematycznej. Dla pięciokąta wpisanego w okrąg o środku (0,0), nowo wyliczony środek ciężkości również musi wypaść w punkcie (0,0).

**Graf**:

* Pięciokąt foremny ze środkiem w (0,0)

**Weryfikacja**:

* Sprawdzenie współrzędnych (x, y) węzła centralnego z dokładnością do 5 miejsc po przecinku.

**Wynik**: PASSED

| **Wizualizacja** |
|------------------|
| ![](../visualizations/p8_visualizations/test_center_coordinates_after.png) |

---

### 5. Test osadzenia w większym grafie (test_apply_on_complex_graph_preserves_context)

**Opis**: Test izolacji – produkcja nigdy nie działa w próżni. Dodajemy do grafu "szum" (węzły i krawędzie niepołączone z pięciokątem).

**Graf przed**:

* Pięciokąt z węzłami wiszącymi
* Dodatkowy węzeł "noise_1" połączony z jednym narożnikiem

**Graf po**:

* Pięciokąt podzielony na 5 czworokątów
* Węzeł "noise_1" i jego krawędź niezmienione

**Wynik**: PASSED

|  **Przed**                                    | **Po**                                  |
|----------------------------------------------|------------------------------------------|
| ![](../visualizations/p8_visualizations/test_apply_on_complex_graph_preserves_context_before.png) | ![](../visualizations/p8_visualizations/test_apply_on_complex_graph_preserves_context_after.png) |

---

### 6. Test złej etykiety hiperkrawędzi (test_wrong_hypertag)

**Opis**: Test negatywny – podmiana etykiety elementu z `P` na `Q` (zachowując resztę struktury).

**Graf**:

* Pięciokąt z prawidłową topologią
* Hiperkrawędź z etykietą Q zamiast P

**Wynik**: PASSED (produkcja nie została zastosowana)

|  **Przed**                                    | **Po**                                  |
|----------------------------------------------|------------------------------------------|
| ![](../visualizations/p8_visualizations/test_wrong_hypertag_before.png) | ![](../visualizations/p8_visualizations/test_wrong_hypertag_after.png) |

---

### 7. Test brakującego wierzchołka narożnego (test_missing_corner_node)

**Opis**: Symulacja uszkodzonego grafu (błąd danych). Usuwamy jeden z wierzchołków narożnych.

**Graf**:

* Pięciokąt z usuniętym wierzchołkiem v0
* Wszystkie krawędzie związane z v0 również usunięte

**Wynik**: PASSED (produkcja nie została zastosowana, brak wyjątku)

|  **Przed**                                    | **Po**                                  |
|----------------------------------------------|------------------------------------------|
| ![](../visualizations/p8_visualizations/test_missing_corner_node_before.png) | ![](../visualizations/p8_visualizations/test_missing_corner_node_after.png) |

---

### 8. Test zniekształconego pięciokąta (test_apply_distorted_pentagon)

**Opis**: Metoda PolyDPG działa na siatkach adaptacyjnych, które często są nieregularne. Test sprawdza, czy algorytm zadziała poprawnie na "krzywym", asymetrycznym pięciokącie.

**Graf**:

* Nieregularny pięciokąt z ręcznie zdefiniowanymi współrzędnymi
* Węzły wiszące lekko przesunięte względem środków geometrycznych

**Weryfikacja**:

* Potwierdzenie, że logika opiera się na topologii (połączeniach), a nie na idealnej geometrii węzłów.

**Wynik**: PASSED

|  **Przed**                                    | **Po**                                  |
|----------------------------------------------|------------------------------------------|
| ![](../visualizations/p8_visualizations/test_apply_distorted_pentagon_before.png) | ![](../visualizations/p8_visualizations/test_apply_distorted_pentagon_after.png) |

---

### 9. Test dwóch pięciokątów – selektywność (test_two_pentagons_one_ready)

**Opis**: Test selektywności. W grafie umieszczamy dwa pięciokąty: jeden spełnia warunki (wszystkie boki połamane), a drugiemu brakuje jednego węzła wiszącego.

**Graf przed**:

* Lewy pięciokąt (L_) – gotowy do podziału (R=1, wszystkie boki połamane)
* Prawy pięciokąt (R_) – niegotowy (R=1, ale jeden bok ciągły)

**Graf po**:

* Lewy pięciokąt podzielony na 5 czworokątów
* Prawy pięciokąt niezmieniony (nadal jako P)

**Wynik**: PASSED

|  **Przed**                                    | **Po**                                  |
|----------------------------------------------|------------------------------------------|
| ![](../visualizations/p8_visualizations/test_two_pentagons_one_ready_before.png) | ![](../visualizations/p8_visualizations/test_two_pentagons_one_ready_after.png) |

---

## Podsumowanie Testów

| Numer | Nazwa testu | Status |
| --- | --- | --- |
| 1 | TEST APPLY ISOMORPHIC | PASSED |
| 2 | TEST APPLY MISSING BREAK | PASSED |
| 3 | TEST APPLY R0 | PASSED |
| 4 | TEST CENTER COORDINATES | PASSED |
| 5 | TEST APPLY ON COMPLEX GRAPH PRESERVES CONTEXT | PASSED |
| 6 | TEST WRONG HYPERTAG | PASSED |
| 7 | TEST MISSING CORNER NODE | PASSED |
| 8 | TEST APPLY DISTORTED PENTAGON | PASSED |
| 9 | TEST TWO PENTAGONS ONE READY | PASSED |

**Wynik końcowy: 9/9 testów zaliczonych**

---

## Pokrycie wymagań testowych

### 1. Czy produkcja dobrze sprawdza izomorfizm z lewą stroną (czy da się ją wykonać)?

| Wymaganie | Status | Testy |
| --- | --- | --- |
| Czy da się wykonać produkcję do grafu izomorficznego z lewą stroną | ✅ | #1, #8 |
| Usunięcie losowego wierzchołka nie psuje mechanizmu | ✅ | #7 |
| Usunięcie losowej krawędzi (węzła wiszącego) nie psuje mechanizmu | ✅ | #2 |
| Zmiana etykiety hiperkrawędzi nie psuje mechanizmu | ✅ | #6 |
| Osadzenie w większym grafie nie psuje mechanizmu | ✅ | #5, #9 |

### 2. Czy produkcja dobrze się wykonała?

| Wymaganie | Status | Testy |
| --- | --- | --- |
| Produkcja nie uszkadza większego grafu | ✅ | #5, #9 |
| Produkcja dobrze transformuje osadzenie | ✅ | #5, #9 |
| Graf prawej strony jest poprawny (wierzchołki, krawędzie, etykiety) | ✅ | #1, #4 |
| Współrzędne nowych wierzchołków są poprawne | ✅ | #4 |

### 3. Czy graf po zastosowaniu produkcji dobrze się rysuje?

| Wymaganie | Status | Testy |
| --- | --- | --- |
| Czy są wszystkie wierzchołki i krawędzie | ✅ | #1 |
| Czy wierzchołki są w poprawnych współrzędnych | ✅ | #4, #8 |
| Czy są narysowane etykiety wierzchołków | ✅ | #1-#9 (wizualizacje) |

### 4. Czy zostały przygotowane różne grafy do testowania?

| Wymaganie | Status | Testy |
| --- | --- | --- |
| Graf izomorficzny z lewą stroną | ✅ | #1 |
| Graf zawierający lewą stronę jako podgraf | ✅ | #5, #9 |
| Graf niepoprawny (brak wierzchołka) | ✅ | #7 |
| Graf niepoprawny (brak krawędzi/węzła wiszącego) | ✅ | #2 |
| Graf niepoprawny (zła etykieta) | ✅ | #6 |
| Graf z różnymi współrzędnymi (zniekształcony) | ✅ | #8 |

### 5. Czy wynik uzyskany po zastosowaniu produkcji został dobrze sprawdzony?

| Wymaganie | Status | Testy |
| --- | --- | --- |
| Produkcja wykonała się na poprawnym, nie na niepoprawnym grafie | ✅ | #2, #3, #6, #7 |
| Produkcja nie uszkadza większego grafu | ✅ | #5, #9 |
| Produkcja dobrze transformuje osadzenie | ✅ | #5 |
| Graf prawej strony jest poprawny | ✅ | #1 |
| Współrzędne nowych wierzchołków są poprawne | ✅ | #4, #8 |

---

## Uruchomienie testów

```bash
# Instalacja zależności
pip install -r requirements.txt

# Uruchomienie testów P8
python tests/test_p8.py

# Uruchomienie za pomocą pytest
pytest tests/test_p8.py -v
```

---

## Struktura plików

```
graph_model.py              # Model grafu i hiperkrawędzi
production_base.py          # Klasa bazowa produkcji
productions/
    p8.py                   # Implementacja produkcji P8
tests/
    test_p8.py              # Testy jednostkowe P8
visualization.py            # Wizualizacja grafów
visualizations/             # Folder z wizualizacjami
    p8_visualizations/      # Wizualizacje testów P8
        test_*.png
docs/
    dokumentacja_p8.md      # Ten plik dokumentacji
```

---
