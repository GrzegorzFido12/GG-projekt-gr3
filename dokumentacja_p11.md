# Dokumentacja Produkcji P11

## Gramatyka Hipergrafów - Metoda Polihedralne Graph Grammars

### Wstęp

Produkcja P11 jest częścią systemu gramatyki hipergrafów, która realizuje podziały (refinement) elementów sześciokątnych. Dokumentacja opisuje implementację, metodologię testowania oraz wyniki weryfikacji.

---

## 1. Opis Produkcji P11 - Implementacja i Przygotowanie Testów

### 1.1 Koncepcja Produkcji

**Produkcja P11** przekształca element sześciokątny (ze wskaźnikiem refinementu `R=1`) w strukturę złożoną z:
- Centralnego węzła (center node)
- 6 elementów czworokątnych (Q - quadrilaterals) z `R=0`
- Zachowaniem struktury brzegowej (boundary edges `E`)

### 1.2 Lewa Strona Produkcji (Left-Hand Side)

Struktura wejściowa, którą produkcja szuka w grafie:

```
Komponenty:
- 6 węzłów narożnikowych (v1, v2, v3, v4, v5, v6)
- 6 węzłów wiszczących (h0, h1, h2, h3, h4, h5) na krawędziach
- 1 hiperkrawędź główna S(v1, v2, v3, v4, v5, v6) z R=1
- 6 hiperkrawędzi brzegowych E łączących narożniki przez węzły wiszczące
```

Wizualnie:
```
        v1 --- h0 --- v2
       /               \
      h5               h1
     /                   \
    v6         S          v3
     \                   /
      h4               h2
       \               /
        v5 --- h3 --- v4
```

Właściwości:
- `S` - hiperkrawędź sześciokątna z `R=1` (do przetworzenia)
- `E` - krawędzie brzegowe z `B=1` (boundary)
- Węzły `hanging=True` - węzły wiszczące na krawędziach

### 1.3 Prawa Strona Produkcji (Right-Hand Side)

Struktura wynikowa po zastosowaniu produkcji:

```
Komponenty:
- 6 węzłów narożnikowych (zachowane)
- 6 węzłów wiszczących (zmienione na hanging=False)
- 1 węzeł centralny v_center (nowy)
- 6 hiperkrawędzi Q (quadrilaterals) z R=0
- 6 hiperkrawędzi E (boundary preservation)
- 6 hiperkrawędzi E typu "spoke" (linie od centrum do midpoints)
```

Wizualnie:
```
        v1 ----E---- h0 ----E---- v2
        |            |            |
        |          h5|h1          |
        |            |            |
        h5 ---E--- v_center ---E--- h1
        |            |            |
        |          h4|h2          |
        |            |            |
        v6 ----E---- h3 ----E---- v3
        
        + analogicznie po drugiej stronie
```

---

## 2. Metodologia Sprawdzania Izomorfizmu

### 2.1 Algorytm Sprawdzania Izomorfizmu

Metoda `is_isomorphic(subgraph: Graph) -> bool` implementuje wieloetapowe sprawdzenie:

#### Etap 1: Weryfikacja Liczby Elementów
```python
if len(subgraph.nodes) != len(lhs.nodes): return False
if len(subgraph.hyperedges) != len(lhs.hyperedges): return False
```

#### Etap 2: Podział Węzłów na Kategorie
```python
corners1 = [n for n in lhs.nodes if not getattr(n, 'hanging', False)]
hanging1 = [n for n in lhs.nodes if getattr(n, 'hanging', False)]
corners2 = [n for n in subgraph.nodes if not getattr(n, 'hanging', False)]
hanging2 = [n for n in subgraph.nodes if getattr(n, 'hanging', False)]
```

**Kluczowa obserwacja**: Prawidłowy graf musi mieć:
- Dokładnie 6 węzłów narożnikowych (`hanging=False`)
- Dokładnie 6 węzłów wiszczących (`hanging=True`)

#### Etap 3: Permutacyjne Mapowanie Węzłów Narożnikowych
Dla każdej permutacji 6 węzłów narożnikowych:
- Próbujemy zmapować węzły lewej strony na węzły podgrafu
- Dla każdego węzła wiszczącego w LHS szukamy odpowiadającego węzła w podgrafie
- Węzeł wiszczący musi mieć dokładnie 2 sąsiadów narożnikowych (poprzez krawędzie E)

```python
def get_corner_neighbors(g, h_node, all_corners):
    neighbors = set()
    for e in g.hyperedges:
        if h_node in e.nodes and e.hypertag == 'E':
            for n in e.nodes:
                if n in all_corners:
                    neighbors.add(n)
    return neighbors
```

#### Etap 4: Weryfikacja Hiperkrawędzi S
```python
s_edges1 = [e for e in lhs.hyperedges if e.hypertag == 'S']
s_edges2 = [e for e in subgraph.hyperedges if e.hypertag == 'S']
if s_edges1 and s_edges2:
    if s_edges1[0].R != s_edges2[0].R: continue
```

### 2.2 Opis Testów Izomorfizmu

**Test 1: Sprawdzanie izomorfizmu (test_isomorphism_check)**

- *Przypadek pozytywny*: Idealnie pasujący graf
- *Przypadek negatywny 1*: Brak węzła wiszczącego
- *Przypadek negatywny 2*: Zła etykieta krawędzi głównej

---

## 3. Metodologia Decyzji o Miejscu Zastosowania Produkcji

### 3.1 Algorytm Wyszukiwania Dopasowania

Metoda `find_match(graph: Graph) -> Optional[HyperEdge]` implementuje strategię:

```python
def find_match(self, graph: Graph) -> Optional[HyperEdge]:
    for edge in graph.hyperedges:
        if edge.hypertag == 'S' and edge.R == 1 and len(edge.nodes) == 6:
            if self._check_all_edges_broken(graph, edge):
                # Znaleźliśmy match
                return HyperEdge(all_involved_nodes, "S", R=1)
    return None
```

### 3.2 Kryteria Dopasowania

Produkcja jest zastosowana do hiperkrawędzi `S`, jeśli spełnione są warunki:

1. **Hyperkrawędź musi być typu S** (`edge.hypertag == 'S'`)
2. **Hyperkrawędź musi mieć R=1** (`edge.R == 1`) - wyznacza ona miejsca do przetworzenia
3. **Hyperkrawędź musi mieć 6 węzłów** (`len(edge.nodes) == 6`)
4. **Wszystkie krawędzie brzegowe muszą być podzielone** - każda z 6 krawędzi między narożnikami musi mieć węzeł wiszczący

### 3.3 Mechanizm Sprawdzenia Podzielenia Krawędzi

```python
def _check_all_edges_broken(self, graph: Graph, s_edge: HyperEdge) -> bool:
    corners = list(s_edge.nodes)
    sorted_corners = self._sort_angularly(corners, center_x, center_y)
    
    for i in range(6):
        c1 = sorted_corners[i]
        c2 = sorted_corners[(i + 1) % 6]
        if not self._has_hanging_node(graph, c1, c2):
            return False
    return True
```

Węzeł wiszczący musi spełniać:
- **Geometrycznie**: Być pośrodku linii między dwoma narożnikami (tolerancja 1e-4)
- **Topologicznie**: Być połączonym z obydwoma narożnikami krawędziami typu E

### 3.4 Test Decyzji o Miejscu (test_location_decision_based_on_R)

- *R=0*: Produkcja NIE jest stosowana (graf ignorowany)
- *R=1*: Produkcja jest stosowana (dopasowanie znalezione)

---

## 4. Metodologia Wyszukiwania Podgrafu w Dużym Grafie

### 4.1 Algorytm Wyszukiwania

Algorytm iteracyjnie przeszukuje wszystkie hiperkrawędzie w grafie:

```python
def find_match(self, graph: Graph) -> Optional[HyperEdge]:
    for edge in graph.hyperedges:  # Iteracja przez wszystkie krawędzie
        if self._check_all_edges_broken(graph, edge):
            # Znaleziono dopasowanie
            return HyperEdge(all_involved_nodes, "S", R=1)
    return None
```

### 4.2 Mechanizm Filtowania

1. **Filtr 1 - Typ krawędzi**: Szukamy tylko krawędzi typu `S`
2. **Filtr 2 - Flaga refinementu**: Wierzymy tylko w krawędzie z `R=1`
3. **Filtr 3 - Liczba węzłów**: Muszą być dokładnie 4 węzły narożnikowe
4. **Filtr 4 - Topologia**: Każda krawędź między narożnikami musi mieć węzeł wiszczący

### 4.3 Analiza Złożoności

- **Złożoność czasowa**: O(E × N) gdzie E = liczba krawędzi, N = liczba węzłów
- **Pierwsza znaleziona krawędź**: Produkcja zwraca pierwszą znalezioną zgodną hiperkrawędź

### 4.4 Test Wyszukiwania w Dużym Grafie (test_finding_subgraph_in_large_graph)

Graf zawiera:
- Szum (niepowiązane węzły)
- Prawidłowy sześciokąt z `R=1`
- Produkcja musi znaleźć sześciokąt i ignorować szum

---

## 5. Metodologia Sprawdzania Poprawności Wyniku

### 5.1 Warunki Poprawności (Post-conditions)

Po zastosowaniu produkcji P11 graf musi spełniać:

#### 5.1.1 Liczba i Typ Elementów

```python
centers = [n for n in graph.nodes if n.label == "v_center"]
assert len(centers) == 1  # Dokładnie jeden węzeł centralny

hanging_now = [n for n in graph.nodes if getattr(n, 'hanging', False)]
assert len(hanging_now) == 0  # Węzły wiszczące zmienią się w zwykłe

q_edges = [e for e in graph.hyperedges if e.hypertag == "Q"]
assert len(q_edges) == 6  # Dokładnie 6 elementów czworokątnych
```

#### 5.1.2 Atrybuty Nowych Elementów

```python
assert all(q.R == 0 for q in q_edges)  # Nowe Q mają R=0
```

#### 5.1.3 Zachowanie Struktury Brzegowej

- Krawędzie `E` o `B=1` są zachowywane
- Krawędzie "spoke" (od centrum do midpoints) mają `B=0`

### 5.2 Implementacja Transformacji

```python
def get_right_side(self, matched: Graph, level: int) -> Graph:
    new_graph = Graph()
    
    # 1. Znalezienie węzła centralnego
    center_x = sum(n.x for n in corners) / len(corners)
    center_y = sum(n.y for n in corners) / len(corners)
    new_center = Node(center_x, center_y, "v_center", hanging=False)
    new_graph.add_node(new_center)
    
    # 2. Sortowanie narożników angularnie
    corners = self._sort_angularly(corners, center_x, center_y)
    
    # 3. Tworzenie 6 czworokątów (Q)
    for i in range(n_corners):
        # Dla każdej strony sześciokąta tworzymy czworokąt
        q_nodes = (new_center, h_prev, c_curr, h_next)
        new_graph.add_edge(HyperEdge(q_nodes, "Q", R=0))
        
        # Odtwarzamy krawędzie brzegowe
        new_graph.add_edge(HyperEdge((c_curr, h_next), "E", B=1))
        new_graph.add_edge(HyperEdge((h_prev, c_curr), "E", B=1))
        
        # Tworzymy spoke edges
        new_graph.add_edge(HyperEdge((new_center, h_next), "E", B=0))
```

### 5.3 Test Poprawności Wyniku (test_result_correctness)

Weryfikuje transformację PRZED → PO:
- Liczba węzłów centralnych: 1
- Liczba elementów Q: 6
- Atrybuty R=0 dla elementów Q
- Brak węzłów wiszczących po transformacji

---

## 6. Przeprowadzone Testy

### 6.1 Test 1: Sprawdzanie Izomorfizmu (test_isomorphism_check)

**Cel**: Weryfikacja algorytmu sprawdzania izomorfizmu

**Scenariusze**:
1. Graf idealnie pasujący
2. Brak węzła wiszczącego
3. Zła etykieta krawędzi głównej

**Wyniki**: ✓ PASSED

#### Wizualizacja - Przypadek Pozytywny
![Sześciokąt prawidłowy dla izomorfizmu](visualizations/test_p11_isomorphism_check__before.png)

**Struktura**: 6 narożników, 6 węzłów wiszczących, krawędź S z R=1

#### Wizualizacja - Przypadek Negatywny 1 (Brak węzła wiszczącego)
![Sześciokąt bez węzła wiszczącego](visualizations/test_p11_isomorphism_check__broken_topology.png)

**Struktura**: Brakuje węzła wiszczącego h - graf NIE jest izomorficzny

#### Wizualizacja - Przypadek Negatywny 2 (Zła etykieta)
![Sześciokąt ze złą etykietą](visualizations/test_p11_isomorphism_check__wrong_label.png)

**Struktura**: Krawędź S zmieniona na X - graf NIE jest izomorficzny

---

### 6.2 Test 2: Decyzja o Miejscu Zastosowania (test_location_decision_based_on_R)

**Cel**: Sprawdzenie czy produkcja uwzględnia flagę R

**Scenariusze**:
- R=0: Produkcja ignoruje grafy
- R=1: Produkcja znajduje dopasowanie

**Wyniki**: ✓ PASSED

#### Wizualizacja - R=0 (Ignorowany)
![Sześciokąt z R=0](visualizations/test_p11_location_decision_based_on_R__R0_ignored.png)

**Decyzja**: Produkcja NIE znajduje match (R=0)

#### Wizualizacja - R=1 (Przetwarzany)
![Sześciokąt z R=1](visualizations/test_p11_location_decision_based_on_R__R1_matched.png)

**Decyzja**: Produkcja ZNAJDUJE match (R=1)

---

### 6.3 Test 3: Wyszukiwanie Podgrafu w Dużym Grafie (test_finding_subgraph_in_large_graph)

**Cel**: Weryfikacja czy produkcja znalazła prawidłowy podgraf wśród szumu

**Scenariusz**: 
- Graf zawiera szum (niepowiązane węzły)
- Prawidłowy sześciokąt z R=1 osadzony w grafie
- Produkcja musi znaleźć sześciokąt i ignorować szum

**Wyniki**: ✓ PASSED

#### Wizualizacja - Duży Graf z Szumem
![Duży graf z szumem](visualizations/test_p11_finding_subgraph_in_large_graph__before.png)

**Struktura**: Szum (noise1, noise2) + prawidłowy sześciokąt

**Wynik**: Produkcja znalazła prawidłowy sześciokąt (6 węzłów narożnikowych + 6 węzłów wiszczących)

---

### 6.4 Test 4: Poprawność Wyniku (test_result_correctness)

**Cel**: Weryfikacja transformacji (PRZED → PO)

**Warunki do sprawdzenia**:
- Dokładnie 1 węzeł centralny
- 6 elementów Q z R=0
- Brak węzłów wiszczących po transformacji

**Wyniki**: ✓ PASSED

#### Wizualizacja - PRZED
![Sześciokąt przed transformacją](visualizations/test_p11_result_correctness__before.png)

**Struktura**: Sześciokąt z węzłami wiszczącymi, R=1

#### Wizualizacja - PO
![Sześciokąt po transformacji](visualizations/test_p11_result_correctness__after.png)

**Struktura**: 1 węzeł centralny + 6 czworokątów (Q), wszystkie węzły wiszczące są teraz zwykłymi węzłami

---

### 6.5 Test 5: Nieregularna Geometria (test_p11_irregular_geometry)

**Cel**: Weryfikacja czy P11 obsługuje sześciokąty o nieregularnej geometrii

**Scenariusz**: Sześciokąt zniekształcony (squashed hexagon)

**Wyniki**: ✓ PASSED

#### Wizualizacja - PRZED (Nieregularna Geometria)
![Sześciokąt zniekształcony - przed](visualizations/test_p11_irregular_geometry_before.png)

**Struktura**: Nieregularny sześciokąt, ale topologia prawidłowa

#### Wizualizacja - PO
![Sześciokąt zniekształcony - po](visualizations/test_p11_irregular_geometry_after.png)

**Wynik**: Transformacja prawidłowa mimo nieregularnej geometrii (otrzymane 6 czworokątów Q)

---

### 6.6 Test 6: Brak Flagi Wiszczącej (test_p11_missing_hanging_flag)

**Cel**: Weryfikacja czy P11 odrzuca grafy gdzie węzły midpoint nie mają flagi `hanging=True`

**Scenariusz**: Węzeł midpoint istnieje geometrycznie, ale `hanging=False`

**Wyniki**: ✓ PASSED

#### Wizualizacja - PRZED
![Sześciokąt bez flagi hanging](visualizations/test_p11_missing_hanging_flag_before.png)

**Struktura**: Węzły wygładają jak zwykłe węzły (hanging=False)

**Decyzja**: Produkcja NIE jest stosowana (warunek: hanging node musi mieć hanging=True)

#### Wizualizacja - PO
![Sześciokąt bez flagi hanging - po](visualizations/test_p11_missing_hanging_flag_after.png)

**Wynik**: Graf NIEZMIENIONY (produkcja nie zastosowana)

---

### 6.7 Test 7: Rozłączny Węzeł Wiszczący (test_p11_disconnected_hanging_node)

**Cel**: Weryfikacja czy P11 odrzuca grafy gdzie węzły wiszczące są geometrycznie prawidłowe ale topologicznie rozłączne

**Scenariusz**: 
- Węzeł h_0 istnieje w prawidłowej pozycji geometrycznej
- Ale krawędzie go łączące są usunięte
- Zamiast tego dodana jest krawędź bezpośrednio między narożnikami

**Wyniki**: ✓ PASSED

#### Wizualizacja - PRZED
![Rozłączny węzeł wiszczący - przed](visualizations/test_p11_disconnected_hanging_node_before.png)

**Struktura**: Węzeł h_0 istnieje ale nie jest połączony

**Decyzja**: Produkcja NIE jest stosowana (warunek topologiczny: h musi być w krawędziach E)

#### Wizualizacja - PO
![Rozłączny węzeł wiszczący - po](visualizations/test_p11_disconnected_hanging_node_after.png)

**Wynik**: Graf NIEZMIENIONY

---

### 6.8 Test 8: Podwójne Zastosowanie (test_p11_double_application)

**Cel**: Weryfikacja czy P11 nie może być zastosowana dwukrotnie do tego samego miejsca

**Scenariusz**:
- Pierwsza aplikacja przekształca S z R=1 w 6 elementów Q z R=0
- Druga aplikacja powinna być niemożliwa (nie ma S z R=1)

**Wyniki**: ✓ PASSED

#### Wizualizacja - PRZED (Pierwsza Aplikacja)
![Podwójna aplikacja - przed](visualizations/test_p11_double_application_before.png)

**Struktura**: Sześciokąt z S, R=1

#### Wizualizacja - PO Pierwsza Aplikacja
![Podwójna aplikacja - po pierwszy raz](visualizations/test_p11_double_application_step1.png)

**Struktura**: 6 czworokątów Q z R=0

#### Wizualizacja - PO Druga Próba
![Podwójna aplikacja - po drugi raz](visualizations/test_p11_double_application_after.png)

**Wynik**: Graf NIEZMIENIONY (produkcja P11 nie znajduje S z R=1)

---

## 7. Podsumowanie

### 7.1 Klucze Techniczne Implementacji

| Aspekt | Rozwiązanie |
|--------|------------|
| **Izomorfizm** | Permutacyjne mapowanie 6 narożników + weryfikacja topologii |
| **Lokalizacja** | Flaga R=1 + weryfikacja podzielenia wszystkich krawędzi |
| **Wyszukiwanie** | Iteracja przez wszystkie krawędzie S |
| **Walidacja** | Geometryczna (1e-4 tolerancja) + topologiczna (krawędzie E) |

### 7.2 Wyniki Testów

Wszystkie 8 testów: **✓ PASSED**

- 3 testy poprawności algorytmu (izomorfizm, lokalizacja, wyszukiwanie)
- 1 test transformacji (poprawność wyniku)
- 4 testy walidacji (geometria, flagi, topologia, podwójne aplikacje)

### 7.3 Wnioski

Implementacja produkcji P11:
- ✓ Prawidłowo identyfikuje sześciokąty do przetworzenia
- ✓ Prawidłowo transformuje grafy
- ✓ Obsługuje nieregularną geometrię
- ✓ Sprawdza warunki topologiczne
- ✓ Uniemożliwia wielokrotne zastosowanie na tym samym elemencie