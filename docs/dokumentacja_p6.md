# Dokumentacja Produkcji P6

## Gramatyka Hipergrafów

**Produkcja P6** 
Produkcja P6 jest operacją sterującą procesem zagęszczania siatki (refinement). Jej zadaniem jest oznaczenie elementu centralnego (pięciokąta) do podziału poprzez zmianę atrybutu $R$ z **0** na **1**.

Ważnym aspektem tej produkcji jest warunek **RFC** (Refinement Flow Control). Oznacza on, że podział elementu głównego nie zachodzi samoczynnie, lecz jest wymuszony przez otoczenie — jeśli przynajmniej jedna z krawędzi ograniczających element została już oznaczona do podziału ($R=1$), element centralny również musi zostać podzielony, aby zachować spójność topologiczną siatki.

---

## Lewa strona produkcji

Produkcja P6 znajduje podgraf, który posiada następujące cechy:
* **Hiperkrawędź**: 
  * typu `P`
  * połaczona z 5-cioma wierzchołkami
  * Atrybut $R = 0$ (element nie jest jeszcze oznaczony do podziału)
* **Warunek RFC**:
  * Przynajmniej jedna z hiperkrawędzi typu `E` łącząca wierzchołki elementu `P` posiada atrybut $R = 1$.

```
---
     v4 -----| E |---- v3
      | \     ---     /  \ 
      |  \           /    \---
      |   \         /     | E |
      |    \       /       ---
      |     \R=0  /          \  
     ---     \---/            \
    | E |    | P |------------ v5
     ---     /---\            /
      |     /     \          /
      |    /       \       ---
      |   /         \     | E | (RFC: Przynajmniej jedno E ma R=1)
      |  /           \    /---
      | /     ---     \  /
     v1 -----| E |---- v2
              ---
```

## Prawa strona produkcji

Po zastosowaniu produkcji P6:
- Hiperkrawędź typu `P` zmienia wartość atrybutu $R$ na **1**.
- Wszystkie pozostałe elementy grafu (wierzchołki, krawędzie boczne `E`, ich atrybuty `B`) pozostają niezmienione.

```
              ---
     v4 -----| E |---- v3
      | \     ---     /  \ 
      |  \           /    \---
      |   \         /     | E |
      |    \       /       ---
      |     \ R=1 /          \  
     ---     \---/            \
    | E |    | P |------------ v5
     ---     /---\            /
      |     /     \          /
      |    /       \       ---
      |   /         \     | E |
      |  /           \    /---
      | /     ---     \  /
     v1 -----| E |---- v2
              ---
```
---

## Implementacja

### Sprawdzanie izomorfizmu z lewą stroną produkcji

Metoda `find_match()` weryfikuje strukturę Pentagonu oraz sprawdza, czy spełniony jest warunek wymuszenia podziału (RFC):

```python
def find_match(self, graph: Graph) -> Optional[HyperEdge]:
        for p_edge in graph.hyperedges:
            # 1. Sprawdzenie typu, liczby węzłów i braku wcześniejszego oznaczenia
            if p_edge.hypertag == "P" and len(p_edge.nodes) == 5 and p_edge.R == 0:
                
                # 2. Pobranie krawędzi krawędziowych (E) stykających się z tym elementem P
                boundary_edges = [e for e in graph.hyperedges 
                                  if e.hypertag == "E" and any(n in p_edge.nodes for n in e.nodes)]
                
                # 3. Weryfikacja RFC: Czy którakolwiek krawędź boczna ma R=1?
                if any(e.R == 1 for e in boundary_edges):
                    return p_edge
        return None
```

Warunki izomorfizmu:
1. Musi istnieć hiperkrawędź typu `P`.
2. Krawędź `P` musi być połączona z dokładnie **5** wierzchołkami.
3. Krawędź `P` musi mieć atrybut $R=0$ (brak wcześniejszego oznaczenia do podziału).
4. Warunek **RFC**: Musi istnieć przynajmniej jedna krawędź typu `E` incydentna z wierzchołkami elementu `P`, która posiada atrybut $R=1$.

#### Produkcja jest stosowana do pierwszej znalezionej hiperkrawędzi spełniającej powyższe warunki.

### Tworzenie prawej strony produkcji

```python
def get_right_side(self, matched: Graph, level: int) -> Graph:
    old_p_edge = next(e for e in matched.hyperedges if e.hypertag == "P")

    result = Graph()
    for node in matched.nodes:
        result.add_node(node)

    for edge in matched.hyperedges:
        if edge.hypertag == "E":
            result.add_edge(edge)

    result.add_edge(HyperEdge(old_p_edge.nodes, "P", R=1))

    return result
```
#### Prawa strona produkcji charakteryzuje się następującymi cechami:
1. Liczba wierzchołków pozostaje stała.
2. Atrybut $R$ hiperkrawędzi typu `P` zmienia wartość z **0** na **1**.
3. Wszystkie krawędzie typu `E` oraz ich atrybuty ($R, B$) pozostają niezmienione.
4. Współrzędne wierzchołków pozostają niezmienione.

---

## Przeprowadzone Testy

#### Opis Testów Jednostkowych
Wszystkie testy zostały przeprowadzone przy użyciu frameworka `unittest`. Ich celem jest weryfikacja poprawności działania mechanizmu izomorfizmu (metoda `can_apply`) oraz samej transformacji grafu (metoda `apply`).

### 1. Sprawdzenie poprawnej aplikacji przy spełnionym RFC (`test_p6_transformation_success`)
- **Cel**: Weryfikacja zmiany atrybutu $R$ z 0 na 1, gdy warunek wymuszenia podziału jest spełniony.
- **Scenariusz**: Graf posiada pentagon $P$ ($R=0$) oraz przynajmniej jedną krawędź $E$ ($R=1$).
- **Oczekiwany wynik**: Funkcja zwraca sukces, a $R$ pentagonu wynosi **1**.

#### Wygenerowane obrazki:
Graf **przed** aplikacją:
![test_p6_before](visualizations/p6_visualisations/test_p6_before.png)
Graf **po** aplikacji:
![test_p6_after](visualizations/p6_visualisations/test_p6_after.png)

### 2. Aktywacja przez inną krawędź boczną (`test_p6_success_with_different_edge_rfc`)
- **Cel**: Sprawdzenie, czy dowolna krawędź incydentna z $R=1$ aktywuje produkcję.
- **Scenariusz**: Wszystkie krawędzie $E$ mają $R=0$, poza jedną (np. ostatnią na liście).
- **Oczekiwany wynik**: `can_apply` zwraca `True`.

#### Wygenerowany obrazek:
Graf **przed** aplikacją:
![test_p6_before](visualizations/p6_visualisations/test_p6_different_edge_rfc.png)

### 3. Blokada dla krawędzi już oznaczonych (`test_p6_already_marked_fails`)
- **Cel**: Upewnienie się, że produkcja nie aplikuje się do elementów, które mają już $R=1$.
- **Scenariusz**: Pentagon posiada atrybut $R=1$.
- **Oczekiwany wynik**: Wynik aplikacji wynosi **0**.

#### Wygenerowany obrazek:
![test_p6_already_marked](visualizations/p6_visualisations/test_p6_already_marked.png)

### 4.Błędna topologia (`test_p6_wrong_topology_fails`)
- **Cel**: Weryfikacja wymogu posiadania dokładnie 5 węzłów.
- **Scenariusz**: Tworzony jest graf, gdzie krawędź $P$ łączy 4 węzły.
- **Oczekiwany wynik**: `can_apply` zwraca `False`.

#### Wygenerowany obrazek:
![test_p6_wrong_topology](visualizations/p6_visualisations/test_p6_wrong_topology.png)

### 5. Stabilność współrzędnych (`test_p6_vertex_coordinates_preserved`)
- **Cel**: Sprawdzenie, czy produkcja nie przesuwa punktów w przestrzeni.
- **Scenariusz**: Porównanie współrzędnych przed i po transformacji.
- **Oczekiwany wynik**: Współrzędne są identyczne.

### 6. Osadzenie w większym grafie (`test_p6_embedded_in_larger_graph`)
- **Cel**: Weryfikacja działania mechanizmu w złożonym otoczeniu.
- **Scenariusz**: Pentagon współdzieli krawędzie z dodatkowymi strukturami (np. kwadratem).
- **Oczekiwany wynik**: Produkcja modyfikuje tylko pentagon, nie naruszając struktur zewnętrznych.

#### Wygenerowane obrazki:
Graf **przed** aplikacją:
![test_p6_embedded_before](visualizations/p6_visualisations/test_p6_embedded_before.png)
Graf **po** aplikacji:
![test_p6_embedded_after](visualizations/p6_visualisations/test_p6_embedded_after.png)

### 7. Wiele kandydatów i atomowość (`test_p6_multiple_candidates`)
- **Cel**: Sprawdzenie, czy w jednym kroku modyfikowany jest tylko jeden pentagon.
- **Scenariusz**: Graf zawiera dwa pentagony spełniające warunki LHS.
- **Oczekiwany wynik**: Po jednej aplikacji liczba pentagonów z $R=0$ spada z 2 do 1.

#### Wygenerowane obrazki:
Graf **przed** aplikacją:
![test_p6_multiple_before](visualizations/p6_visualisations/test_p6_multiple_before.png)
Graf **po** aplikacji:
![test_p6_multiple_after](visualizations/p6_visualisations/test_p6_multiple_after.png)

### 8. Szczelność filtrów etykiet (`test_p6_no_match_with_similar_label`)
- **Cel**: Sprawdzenie, czy etykiety inne niż P są ignorowane.
- **Scenariusz**: Graf posiada strukturę 5-węzłową z etykietą Q.
- **Oczekiwany wynik**: `can_apply` zwraca `False`.

#### Wygenerowany obrazek:
![test_p6_no_edge_is_marked](visualizations/p6_visualisations/test_p6_no_match_with_similar_label.png)

### 9. Rygor warunku RFC (`test_p6_fails_if_no_edge_is_marked`)
- **Cel**: Sprawdzenie, czy produkcja zostanie odrzucona przy braku wymuszenia (wszystkie $E$ mają $R=0$).
- **Scenariusz**: Pentagon ma $R=0$, ale żadna krawędź boczna nie ma $R=1$.
- **Oczekiwany wynik**: `can_apply` zwraca `False`.

#### Wygenerowany obrazek:
![test_p6_no_edge_is_marked](visualizations/p6_visualisations/test_p6_no_edge_is_marked.png)

### 10. Zachowanie warunków brzegowych (`test_p6_preserves_boundary_conditions`)
- **Cel**: Sprawdzenie, czy produkcja nie uszkadza atrybutów $B$ na krawędziach.
- **Scenariusz**: Porównanie wartości $B$ przed i po aplikacji.
- **Oczekiwany wynik**: Wartości $B$ pozostają **niezmienione**.

### Wyniki testów:

|Nazwa testu                  |Wynik |Opis weryfikacji                                             |
|-----------------------------|------|-------------------------------------------------------------|
|transformation_success     |PASSED|Poprawna zmiana R pentagonu przy spełnionym RFC.             |
|success_with_different_edge_rfc|PASSED|Produkcja działa niezależnie od tego, która krawędź E ma R=1.|
|already_marked_fails       |PASSED|Odrzucenie aplikacji, gdy pentagon ma już R=1.               |
|wrong_topology_fails       |PASSED|Wymuszenie posiadania dokładnie 5 węzłów przez krawędź P.    |
|vertex_coordinates_preserved |PASSED|Potwierdzenie braku przesunięć geometrycznych.               |
|embedded_in_larger_graph   |PASSED|Poprawna praca w złożonym otoczeniu bez uszkadzania sąsiadów.|
|multiple_candidates        |PASSED|Atomowość operacji przy wielu pentagonach w grafie.          |
|no_match_with_similar_label |PASSED|Prawidłowe filtrowanie po etykiecie "P".                     |
|fails_if_no_edge_is_marked |PASSED|RFC: Brak aplikacji przy braku oznaczeń na krawędziach E.    |
|preserves_boundary_conditions |PASSED|Brak niepożądanych zmian w atrybutach B krawędzi bocznych.   |

## Pokrycie wymagań testowych

### Czy produkcja dobrze sprawdza izomorfizm z lewą stroną?

|Wymaganie                         |Status|Testy                                                        |
|----------------------------------|------|-------------------------------------------------------------|
|Czy wykrywa graf izomorficzny z lewą stroną (LHS)|✅     |#1, #6, #7                                                   |
|Warunek RFC: Brak krawędzi E z R=1 blokuje produkcję|✅     |#9                                                           |
|Dowolna krawędź boczna z R=1 aktywuje produkcję|✅     |#2                                                           |
|Zła liczba wierzchołków krawędzi P (np. 4 zamiast 5) blokuje produkcję|✅     |#4                                                           |
|Zmiana etykiety (tagu) na inny niż "P" blokuje produkcję|✅     |#8                                                           |
|Pentagon posiadający już atrybut R=1 jest ignorowany|✅     |#3                                                           |

### Czy produkcja dobrze się wykonała (transformacja)?

|Wymaganie                         |Status|Testy                                                        |
|----------------------------------|------|-------------------------------------------------------------|
|Atrybut R krawędzi P zostaje zmieniony na 1|✅     |#1                                                           |
|Atrybuty B krawędzi bocznych pozostają nienaruszone|✅     |#10                                                          |
|Liczba wierzchołków w grafie pozostaje stała|✅     |#5                                                           |
|Pozycje wierzchołków nie ulegają zmianie (stabilność)|✅     |#5                                                           |
|Produkcja modyfikuje tylko jeden podgraf na raz (atomowość)|✅     |#7                                                           |

### Czy graf po zastosowaniu produkcji dobrze się rysuje?

|Wymaganie                         |Status|Testy                                                        |
|----------------------------------|------|-------------------------------------------------------------|
|Wizualizacja generuje pliki PNG przed i po aplikacji|✅     |#1, #4, #6, #7                                               |
|Topologia na rysunku odpowiada danym w pamięci|✅     |Wizualizacje                                                 |
|Zmiana koloru/etykiety R jest widoczna na schemacie|✅     |Wizualizacje                                                 |

### Czy zostały przygotowane różne grafy do testowania?

|Wymaganie                         |Status|Testy                                                        |
|----------------------------------|------|-------------------------------------------------------------|
|Graf wzorcowy (pięciokąt z jedną krawędzią R=1)|✅     |#1                                                           |
|Graf osadzony w większej strukturze (współdzielone węzły)|✅     |#6                                                           |
|Graf z wieloma kandydatami (dwa pentagony)|✅     |#7                                                           |
|Graf niepoprawny (zła liczba węzłów)|✅     |#4                                                           |
|Graf niepoprawny (brak spełnionego warunku RFC)|✅     |#9                                                           |
|Graf z niepoprawnymi etykietami   |✅     |#8                                                           |

### Czy wynik uzyskany po zastosowaniu produkcji został dobrze sprawdzony?

|Wymaganie                        |Status|Testy                                                        |
|---------------------------------|------|-------------------------------------------------------------|
|Weryfikacja wartości atrybutu R po transformacji|✅     |#1, #2, #6                                                   |
|Sprawdzenie, czy produkcja nie uszkadza elementów zewnętrznych|✅     |#6                                                           |
|Potwierdzenie braku zmian w atrybutach B|✅     |#10                                                          |
|Sprawdzenie współrzędnych|✅     |#5                                                           |

## Uruchomienie testów

```bash
# Będąc w głównym katalogu
python tests/test_p6.py
```

## Struktura plików

```
docs/
    dokumentacja_p6.md
graphs
graph_model.py
productions/
    p6.py
production_base.py
README.md
requirements.txt
tests/
    test_p6.py
venv
visualization.py
visualizations/             
    p6_visualizations/      
        test_p6_after.png
        test_p6_already_marked.png
        test_p6_before.png
        test_p6_different_edge_rfc.png
        test_p6_embedded_after.png
        test_p6_embedded_before.png
        test_p6_multiple_after.png
        test_p6_multiple_before.png
        test_p6_no_edge_is_marked.png
        test_p6_no_match_with_similar_label.png
        test_p6_wrong_topology.png
```