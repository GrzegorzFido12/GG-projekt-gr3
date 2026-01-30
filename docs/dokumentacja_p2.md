# Dokumentacja Produkcji P2

## Gramatyka Hipergrafów


**Produkcja P2** 
jest operacją wykonawczą procesu refinementu krawędzi. Jest stosowana w momencie, gdy długa krawędź jest oznaczona do podziału ($R=1$), a jej struktura geometryczna została już przygotowana (istnieje węzeł w środku). Produkcja ta usuwa starą krawędź, zostawia dwie, które już istniały i zmienia im wartość $R$ na **0**, finalizując podział.
---

## Lewa strona produkcji

Produkcja P2 znajduje podgraf, który posiada następujące cechy:

* **Hiperkrawędzie**: typu `E`
* **R = 1**: element oznaczony do podziału
* **B = 0**: element oznaczony do podziału
* **3 wierzchołki**: wierzchołek, który nie jest połączony z krawędzią do usunięcia i staje się punktem łączącym dwie mniejsze krawędzie $E$ (`v3`), ma każdą współrzędną o wartości średniej arytmetycznej współrzędnych pozostałych dwóch wierzchołków

```
      v2 (x2, y2, z2)
      |  \ 
      |   \---
      |   | E |
      |    ---
      |      \  
     ---      \
R=1 | E |      v3 ((x1+x2)/2, (y1+y2)/2, (z1+z2)/2))
B=0  ---      /
      |      /
      |    ---
      |   | E |
      |   /---
      |  /
      v1 (x1, y1, z1)
```

## Prawa strona produkcji

Po zastosowaniu produkcji P2:

1. Usunięta jest krawędź z oznaczeniami $R=1, B=0$
2. Pozostałe krawędzie mają zmienioną wartość $R$ na 0

```
      v2 (x2, y2, z2)
      |
     ---   
    | E | R=0
     ---   
      |  
      |  
      v3 ((x1+x2)/2, (y1+y2)/2, (z1+z2)/2)
      |  
      |  
     ---
    | E | R=0
     ---
      | 
      v1 (x1, y1, z1)
```
---

## Implementacja

### Sprawdzanie izomorfizmu z lewą stroną produkcji

Metoda `can_apply()` wykorzystuje metodę `find_match()`, aby sprawdzić czy podgraf jest izomorficzny z lewą stroną produkcji:

```python
def can_apply(self, graph: Graph) -> bool:
    return self.find_match(graph) is not None

def find_match(self, graph: Graph) -> Optional[HyperEdge]:
    for e1 in graph.hyperedges:
        if e1.hypertag == "E" and e1.R == 1 and e1.B == 0 and len(e1.nodes) == 2:
            u, v = e1.nodes[0], e1.nodes[1]

            target_x = (u.x + v.x) / 2
            target_y = (u.y + v.y) / 2

            w = next((n for n in graph.nodes if math.isclose(n.x, target_x)
                      and math.isclose(n.y, target_y) and n not in (u, v)), None)

            if w:
                has_u_w = any(set(e.nodes) == {u, w} for e in graph.hyperedges)
                has_v_w = any(set(e.nodes) == {v, w} for e in graph.hyperedges)

                if has_u_w and has_v_w:
                    return HyperEdge((u, v, w), "E", R=1, B=0)
    return None
```

### Warunki izomorfizmu:
1. Musi istnieć krawędź łącząca dokładnie **2** wierzchołki.
2. Krawędź musi być typu `E`
3. Krawędź musi mieć atrybut $R=1$
4. Krawędź musi mieć atrybut $B=0$
5. Dwa wierzchołki krawędzi (`u`, `v`) połączone są przez dwie inne krawędzie przechodzące przez oddzielny wierzchołek `w`, którego współrzędne spełniają następujące zależności:
    * $w.x=\frac{u.x+v.x}{2}$
    * $w.y=\frac{u.y+v.y}{2}$
 
#### Produkcja jest stosowana do pierwszej znalezionej krawędzi spełniającej warunki.

### Tworzenie prawej strony produkcji

```python
def get_right_side(self, matched: Graph, level: int) -> Graph:
    main_edge = next(e for e in matched.hyperedges if e.R == 1)
    u, v = main_edge.nodes[0], main_edge.nodes[1]

    w = next(n for n in matched.nodes if n not in (u, v))

    result = Graph()

    for n in [u, v, w]:
        result.add_node(n)

    result.add_edge(HyperEdge((u, w), "E", R=0, B=main_edge.B))
    result.add_edge(HyperEdge((w, v), "E", R=0, B=main_edge.B))

    return result
```

#### Prawa strona produkcji charakteryzuje się następującymi cechami:
1. Liczba wierzchołków pozostaje stała
2. Liczba krawędzi zostaje zmniejszona o 1
3. Krawędzie, które pozostały trymują nowe wartości atrybutów `R=0,  B=B1`
4. Współrzędne wierzchołków pozostają niezmienione
---

## Przeprowadzenie Testów

#### Opis Testów Jednostkowych
Wszystkie testy zostały przeprowadzone przy użyciu frameworka `unittest`. Ich celem jest weryfikacja poprawności działania mechanizmu izomorfizmu (metoda `can_apply`) oraz samej transformacji grafu (metoda `apply`)

### 1. Sprawdzenie wykrywalności poprawnego grafu (`test_can_apply_positive`)
- **Cel**: Weryfikacja, czy produkcja poprawnie rozpoznaje graf, który jest w pełni zgodny z lewą stroną (LHS).
- **Scenariusz**: Tworzony jest graf bazowy zawierający krawędź $R=1$ oraz wierzchołek pośredni połączony odpowiednimi krawędziami.
- **Oczekiwany wynik**: Funkcja `can_apply` zwraca `True`.

#### Wygenerowany obrazek:
![test_positive_before](visualizations/p2_visualisations/test_positive_before.png)

**Uwaga:**
Ze względu na fakt, że współrzędne wierzchołka środkowego są wyliczane jako średnia arytmetyczna położeń wierzchołków skrajnych, na wygenerowanym schemacie etykieta wierzchołka pokrywa się z etykietą hiperkrawędzi łączącej wierzchołki $v_1$ i $v_2$.

### 2. Brak wierzchołka środkowego (`test_missing_vertex_fails`)
- **Cel**: Sprawdzenie, czy brak wierzchołka $v_3$ (środkowego) blokuje produkcję.
- **Scenariusz**: Z grafu wzorcowego usuwany jest wierzchołek znajdujący się w punkcie $(\frac{x_1+x_2}{2}, \frac{y_1+y_2}{2})$.
- **Oczekiwany wynik**: Funkcja can_apply zwraca False.

#### Wygenerowany obrazek:
![test_missing_vertex_fails](visualizations/p2_visualisations/test_missing_vertex_fails.png)

### 3. Błędna geometria wierzchołka pośredniego (`test_wrong_geometry_fails`)
- **Cel**: Weryfikacja rygoru geometrycznego produkcji.
- **Scenariusz**: Wierzchołek $v_3$ zostaje umieszczony na linii między $v_1$ i $v_2$, ale w innym miejscu niż dokładnie połowa odległości (np. w 75% długości).
- **Oczekiwany wynik**: Funkcja can_apply zwraca False ze względu na niespełnienie warunku średniej arytmetycznej współrzędnych.

#### Wygenerowany obrazek:
![test_wrong_geometry](visualizations/p2_visualisations/test_wrong_geometry.png)

### 4. Brak krawędzi bocznej (`test_missing_edge_breaks_isomorphism`)
- **Cel**: Sprawdzenie, czy kompletność krawędzi bocznych jest wymagana.
- **Scenariusz**: Usuwana jest jedna z krawędzi typu E łącząca wierzchołek środkowy z wierzchołkiem skrajnym.
- **Oczekiwany wynik**: Produkcja nie może zostać zaaplikowana.

### 5. Niepoprawne atrybuty krawędzi (`test_wrong_attributes_fails`)
- **Cel**: Weryfikacja wrażliwości na atrybuty hiperkrawędzi.
- **Scenariusz**: Główna krawędź łącząca $v_1$ i $v_2$ ma zmieniony atrybut $R$ z $1$ na $0$.
- **Oczekiwany wynik**: can_apply zwraca False, ponieważ produkcja P2 służy wyłącznie do finalizacji podziału krawędzi oznaczonych jako $R=1$.

### 6. Poprawność transformacji strukturalnej (`test_transformation_correctness`)
- **Cel**: Sprawdzenie, czy stan grafu po aplikacji produkcji odpowiada prawej stronie (RHS).
- **Scenariusz**: Wykonanie g.apply(prod) na poprawnym grafie.
- **Oczekiwany wynik**: 
  - Stara krawędź $R=1$ zostaje usunięta.
  - W grafie pozostają 2 krawędzie krawędziowe.
  - Wszystkie krawędzie mają teraz atrybut $R=0$.

#### Wygenerowane obrazki:
Graf **przed** transformacją:
![test_transformation_before](visualizations/p2_visualisations/test_transformation_before.png)
Graf **po** transformacji:
![test_transformation_after](visualizations/p2_visualisations/test_transformation_after.png)

### 7. Stabilność współrzędnych wierzchołków (`test_vertex_coordinates_preserved`)
- **Cel**: Upewnienie się, że produkcja jest stabilna geometrycznie i nie przesuwa punktów w przestrzeni.
- **Scenariusz**: Porównanie współrzędnych $(x, y)$ wszystkich wierzchołków przed i po transformacji.
- **Oczekiwany wynik**: Współrzędne są identyczne co do bita.

### 8. Brak połączeń między elementami (`test_missing_adjacent_edges_fails`)
- **Cel**: Sprawdzenie, czy sama obecność wierzchołka w środku wystarczy do podziału (nie powinna).
- **Scenariusz**: Istnieje krawędź $R=1$ i wierzchołek $v_3$ w połowie drogi, ale nie są one połączone krawędziami bocznymi.
- **Oczekiwany wynik**: Brak dopasowania (wymagana jest pełna struktura grafu).

#### Wygenerowane obrazki:
![test_missing_adj_fails](visualizations/p2_visualisations/test_missing_adj_fails.png)

### 9. Aplikacja wewnątrz większego grafu (`test_p2_embedded_in_larger_graph`)
- **Cel**: Weryfikacja działania mechanizmu w kontekście większego, złożonego grafu.
- **Scenariusz**: Do struktury P2 dołączane są dodatkowe wierzchołki i krawędzie, które nie biorą udziału w produkcji.
- **Oczekiwany wynik**: Produkcja znajduje poprawny podgraf i modyfikuje tylko jego elementy, nie naruszając reszty struktury.

#### Wygenerowane obrazki:
Graf **przed** aplikacją:
![test_p2_embedded_before](visualizations/p2_visualisations/test_p2_embedded_before.png)
Graf **po** aplikacji:
![test_p2_embedded_after](visualizations/p2_visualisations/test_p2_embedded_after.png)

### 10. Wybór jednego kandydata z wielu (`test_p2_multiple_candidates_only_one_applied`)
- **Cel**: Sprawdzenie zachowania przy wielu potencjalnych miejscach aplikacji.
- **Scenariusz**: Graf zawiera dwa rozłączne miejsca, w których można zastosować produkcję P2.
- **Oczekiwany wynik**: Jednorazowe wywołanie apply() zmienia tylko jeden obszar, pozostawiając drugi do kolejnej iteracji (zgodnie z logiką systemów gramatycznych).

#### Wygenerowane obrazki:
Graf **przed** wyborem i aplikacją:
![test_p2_multiple_before](visualizations/p2_visualisations/test_p2_multiple_before.png)
Graf **po** aplikacji:
![test_p2_multiple_after](visualizations/p2_visualisations/test_p2_multiple_after.png)


### 11. Rozpoznawanie etykiet hiperkrawędzi (`test_p2_no_match_with_different_label`)
- **Cel**: Sprawdzenie szczelności filtrów etykiet.
- **Scenariusz**: Struktura geometryczna i atrybuty $R, B$ są poprawne, ale krawędzie mają etykietę "Q" zamiast "E".
- **Oczekiwany wynik**: Produkcja ignoruje takie krawędzie.

### Wyniki testów:

| Nazwa testu | Wynik | Opis weryfikacji                                                  |
| --- | --- |-------------------------------------------------------------------|
| can_apply_positive | PASSED | Poprawne wykrycie wzorca LHS w idealnych warunkach.               |
| missing_adjacent_edges_fails | PASSED | Odrzucenie dopasowania przy braku krawędzi bocznych.              |
| missing_edge_breaks_isomorphism | PASSED | "Potwierdzenie, że usunięcie dowolnej krawędzi psuje izomorfizm." |
| missing_vertex_fails | PASSED | Odrzucenie dopasowania przy braku wierzchołka środkowego.         |
| p2_embedded_in_larger_graph | PASSED | Poprawna izolacja i aplikacja produkcji w złożonym grafie.        |
| p2_multiple_candidates_only_one_applied | PASSED | Stabilność systemu przy wielu kandydatach (atomowość produkcji).  |
| p2_no_match_with_different_label | PASSED | "Poprawność filtrowania po etykietach hiperkrawędzi (tag ""E"")." |
| transformation_correctness | PASSED | Zgodność grafu wynikowego z definicją prawej strony (RHS).        |
| vertex_coordinates_preserved | PASSED | Brak niepożądanych modyfikacji geometrii wierzchołków.            |
| wrong_attributes_fails | PASSED | "Weryfikacja atrybutów sterujących (wymagane R=1,B=0)."           |
| wrong_geometry_fails | PASSED | Restrykcyjne sprawdzanie geometrycznego środka krawędzi.          |

## Pokrycie wymagań testowych

### Czy produkcja dobrze sprawdza izomorfizm z lewą stroną?

|Wymaganie|Status     |Testy       |
|---------|-----------|------------|
|Czy wykrywa graf izomorficzny z lewą stroną|✅          |#1, #9, #10 |
|Brak wierzchołka środkowego blokuje produkcję|✅          |#2          |
|Brak wymaganej krawędzi bocznej blokuje produkcję|✅          |#4, #8      |
|Zła geometria (wierzchołek nie w środku) blokuje produkcję|✅          |#3          |
|Zmiana etykiety (tagu) na inny niż "E" blokuje produkcję|✅          |#11         |
|Niezgodność atrybutów (R=1) blokuje produkcję|✅          |#5          |


### Czy produkcja dobrze się wykonała (transformacja)?

|Wymaganie|Status     |Testy       |
|---------|-----------|------------|
|Stara krawędź (R=1) zostaje poprawnie usunięta|✅          |#6          |
|Nowe krawędzie mają poprawne atrybuty (R=0,B=0)|✅          |#6          |
|Liczba wierzchołków pozostaje stała|✅          |#6          |
|Pozycje wierzchołków nie ulegają zmianie|✅          |#7          |
|Produkcja modyfikuje tylko jeden podgraf na raz (atomowość)|✅          |#10         |


### Czy graf po zastosowaniu produkcji dobrze się rysuje?

|Wymaganie|Status     | Testy                  |
|---------|-----------|------------------------|
|Wizualizacja poprawnie generuje pliki przed i po transformacji|✅          | #1, #2, #3, #8, #9, #10 |
|Wierzchołki zachowują spójność wizualną z danymi|✅          | #7                     |
|Oznaczenia nakładają się zgodnie z przewidywaną geometrią|✅          | Wizualizacje, logi     |


### Czy zostały przygotowane różne grafy do testowania?

|Wymaganie                               |Status|Testy|
|----------------------------------------|------|-----|
|Graf wzorcowy (minimalny pasujący)      |✅     |#1   |
|Graf osadzony w większej strukturze     |✅     |#9   |
|Graf z wieloma kandydatami do produkcji |✅     |#10  |
|Graf z błędną geometrią (zniekształcony)|✅     |#3   |
|Graf z błędnymi atrybutami krawędzi     |✅     |#5   |
|Graf z niepoprawnymi etykietami         |✅     |#11  |


### Czy wynik uzyskany po zastosowaniu produkcji został dobrze sprawdzony?

|Wymaganie                               |Status|Testy|
|----------------------------------------|------|-----|
|Produkcja nie uruchamia się na niepełnych strukturach|✅     |#2, #4, #8|
|Produkcja nie uszkadza elementów zewnętrznych|✅     |#9   |
|Sprawdzenie liczby krawędzi po transformacji|✅     |#6   |
|Weryfikacja niezmienności współrzędnych (stabilność geometryczna)|✅     |#7   |

## Uruchomienie testów

```bash
# Będąc w głównym katalogu
python tests/test_p2.py
```

---

## Struktura plików

```
docs/
    dokumentacja_p2.md
graphs
graph_model.py
productions/
    p2.py
production_base.py
README.md
requirements.txt
tests/
    test_p2.py
venv
visualization.py
visualizations/             
    p2_visualizations/      
        test_missing_adj_fails.png
        test_missing_vertex_fails.png
        test_p2_embedded_after.png
        test_p2_embedded_before.png
        test_p2_multiple_after.png
        test_p2_multiple_before.png
        test_positive_before.png
        test_transformation_after.png
        test_transformation_before.png
        test_wrong_geometry.png  
```