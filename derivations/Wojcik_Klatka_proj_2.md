# Sprawozdanie z Projektu 2: Łamanie grafu do punktu
**Autorzy:** Wójcik, Klatka (Grupa 5)

## Cel zadania
Celem drugiej części projektu było napisanie sterownika (procedury pilotującej), który automatycznie przeprowadzi wywód gramatyki grafowej. Wywód ten miał na celu zagęszczenie (połamanie) siatki w kierunku wybranego punktu (w naszym przypadku wierzchołka `v5`) na grafie startowym, wykorzystując przygotowane wcześniej produkcje.

---

## 1. Szczegółowa wizualizacja wywodu

Poniżej przedstawiono każdy krok wywodu wygenerowany przez nasz sterownik. Każdy obraz odpowiada jednemu stanowi pośredniemu grafu.

### Faza 1: Inicjalizacja i podział Pentagonu

#### Krok 0: Graf Początkowy
Stan początkowy siatki. Widoczne trzy elementy czworokątne (trapezy 2D) oraz jeden element pięciokątny po prawej stronie.

![Step 0](../visualizations/group5/0_initial.png)

#### Krok 1: Oznaczenie Pentagonu
Znaleziono element typu `P` (pięciokąt) i zmieniono jego atrybut `R` na `1`. Oznacza to, że jest on przeznaczony do dalszego podziału.

![Step 1](../visualizations/group5/1_marked.png)

#### Krok 2: Aplikacja P7 (Marking)
Zastosowano produkcję `P7`. Produkcja ta oznacza wszystkie krawędzie należące do wybranego pięciokąta (atrybut `R` krawędzi zmienia się na `1`), przygotowując je do podziału.

![Step 2](../visualizations/group5/2_p7_applied.png)

#### Krok 3: Łamanie Krawędzi (Breaking Edges)
Pętla stabilizująca wielokrotnie aplikowała produkcje `P4` (dla krawędzi brzegowych) oraz `P2` (dla krawędzi wewnętrznych), dzieląc wszystkie oznaczone krawędzie na pół i wstawiając nowe wierzchołki.

![Step 3](../visualizations/group5/3_edges_broken.png)

#### Krok 4: Aplikacja P8 (Podział Pentagonu)
Zastosowano produkcję `P8`, która wstawia nowy element do wnętrza "połamanego" pięciokąta, finalizując jego podział.

![Step 4](../visualizations/group5/4_p8_applied.png)

### Faza 2: Podział Górnego Trapezu

#### Krok 5: Oznaczenie Górnego Trapezu
Sterownik zidentyfikował górny trapez sąsiadujący z `v5` (na podstawie wierzchołków `v4` i `v5`) i oznaczył go atrybutem `R=1`.

![Step 5](../visualizations/group5/5_top_trap_marked.png)

#### Krok 6: Aplikacja P1 (Marking)
Zastosowano produkcję `P1` na oznaczonym trapezie `Q`. Produkcja ta oznacza krawędzie tego czworokąta do podziału (atrybut `R=1`).

![Step 6](../visualizations/group5/6_p1_applied.png)

#### Krok 7: Łamanie Krawędzi
Ponownie uruchomiono pętlę stabilizującą. Krawędzie trapezu zostały podzielone przez produkcje `P4` (brzegowe) oraz `P2`/`P3` (wewnętrzne).

![Step 7](../visualizations/group5/7_edges_broken_top.png)

#### Krok 8: Aplikacja P5 (Podział Trapezu)
Na przygotowanym trapezie (z podzielonymi krawędziami) wykonano produkcję `P5`, dzieląc go na cztery mniejsze elementy.

![Step 8](../visualizations/group5/8_p5_applied.png)

### Faza 3: Łamanie do punktu `v5` - Iteracja 1 (Kierunek v4-v5)

W tej fazie sterownik precyzyjnie wybiera mniejszy trapez przylegający do wierzchołka `v5` od strony krawędzi `v4-v5`.

#### Krok 9a: Oznaczenie Krawędzi
Znaleziono odpowiedni mały trapez przy `v5`. Oznaczono jego krawędzie (wewnętrzne i brzegowe) do podziału.

![Step 9a](../visualizations/group5/9a_v5_trap_1_0_marked_edges.png)

#### Krok 9b: Podział Krawędzi (P4)
Wykonano produkcję `P4`, dzieląc oznaczone krawędzie brzegowe i wstawiając nowe wierzchołki.

![Step 9b](../visualizations/group5/9b_v5_trap_1_0_p4_splits.png)

#### Krok 9c: Oznaczenie Elementu Q
Oznaczono sam element `Q` (trapez) do podziału (`R=1`).

![Step 9c](../visualizations/group5/9c_v5_trap_1_0_q_marked.png)

#### Krok 9d: Aplikacja P5
Zastosowano produkcję `P5`, dzieląc ten mały trapez na cztery jeszcze mniejsze. Zagęszczenie przy `v5` wzrosło.

![Step 9d](../visualizations/group5/9d_v5_trap_1_0_p5_applied.png)

### Faza 4: Łamanie do punktu `v5` - Iteracja 2 (Kierunek v5-v8)

Następnie sterownik zajmuje się drugim kierunkiem wychodzącym z `v5` (w stronę `v8`), aby zagęścić siatkę również z tej strony.

#### Krok 10a: Oznaczenie Krawędzi
Zidentyfikowano kolejny trapez przy `v5` (tym razem w kierunku `v8`). Oznaczono jego krawędzie.

![Step 10a](../visualizations/group5/10a_v5_trap_2_0_marked_edges.png)

#### Krok 10b: Podział Krawędzi (P4)
Produkcja `P4` podzieliła krawędzie brzegowe tego trapezu.

![Step 10b](../visualizations/group5/10b_v5_trap_2_0_p4_splits.png)

#### Krok 10c: Oznaczenie Elementu Q
Oznaczono trapez `Q` do podziału (`R=1`).

![Step 10c](../visualizations/group5/10c_v5_trap_2_0_q_marked.png)

#### Krok 10d: Aplikacja P5
Finalny podział trapezu produkcją `P5`. W rezultacie wokół punktu `v5` siatka jest znacznie gęstsza niż w pozostałych obszarach.

![Step 10d](../visualizations/group5/10d_v5_trap_2_0_p5_applied.png)


---

## 2. Weryfikacja poprawności

### a) Zgodność grafów pośrednich
Analiza powyższych 17 kroków potwierdza:
1.  **Ciągłość Topologiczna**: W żadnym kroku (nawet 3, 7, 9b, 10b) nie dochodzi do rozerwania siatki w sposób niezgodny z logiką FEM. Każdy "wiszący" wierzchołek powstały na krawędzi jest obsługiwany przez produkcję `P2` (propagacja pęknięcia) lub `P5` (podział wnętrza), co widać na finalnych obrazach każdej fazy (4, 8, 9d, 10d).
2.  **Poprawność Atrybutów**: Mechanizm oznaczania (`Marking`) działa bezbłędnie. Na obrazach `1`, `5`, `9c`, `10c` widać zmianę stanu elementu `Q`/`P` (zmiana koloru/etykiety). Na obrazach z serii `a` (np. `9a`) widać oznaczone krawędzie.
3.  **Spójność Wierzchołków**: Wierzchołki są współdzielone poprawnie między sąsiednimi elementami.

### b) Zastosowanie odpowiednich produkcji warunkowych
Kluczowym aspektem jest kolejność. Sterownik zawsze najpierw oznacza element (`Marking`), potem krawędzie, a następnie w pętli wykonuje `Breaking Edges`. Dopiero gdy struktura brzegowa jest gotowa, następuje `Splitting`. Zapobiega to sytuacji, w której `P5` próbowałoby się wykonać na "niepołamanym" otoczeniu, co byłoby niezgodne z lewą stroną produkcji.

---

## 3. Szczegółowy opis sterownika (procedury pilotującej)

Sterownik został zaprojektowany w sposób **generyczny**, aby unikać "hardcodowania" (sztywnego wpisywania) ID elementów. Zamiast tego, sterownik analizuje geometrię grafu w czasie rzeczywistym.

### Mechanizm 1: Geometryczne Wyszukiwanie "Następnego Kroku"
Głównym wyzwaniem było: *"Który z wielu trapezów przy `v5` podzielić teraz?"*.
Wcześniejsze podejście oparte na kierunkach krawędzi okazało się niewystarczające. Zastąpiliśmy je bardziej robustną funkcją `find_q_closest_to_target`.

Działa ona następująco:
1.  Pobiera punkt centralny (`v5`) i punkt docelowy (target), który wskazuje "kierunek" (np. `v4` dla górnego trapezu, `v8` dla prawego).
2.  Szuka w grafie wszystkich elementów `Q` zawierających `v5`.
3.  Dla każdego kandydata oblicza metrykę odległości wszystkich jego węzłów do punktu docelowego.
4.  Wybiera ten `Q`, który jest przestrzennie najbliżej celu.

Dzięki temu sterownik wie, że w kroku 9 ma wziąć trapez "idący w stronę v4" (góra), a w kroku 10 trapez "idący w stronę v8" (prawo).

```python
# Przykład użycia w pętli głównej sterownika:
targets = [
    "v4", # Kierunek Góra (Trapezoid 1)
    "v8", # Kierunek Prawo (Trapezoid 2)
]

# Funkcja wybiera trapez na podstawie bliskości do targetu
current_q, adjacent_nodes = find_q_closest_to_target(
    graph, "v5", target_label
)
```

### Mechanizm 2: Funkcja `split_trapezoid`
Jest to główna "procedura wykonawcza". Nie jest to proste wywołanie produkcji, ale złożony algorytm:

1.  **Identyfikacja Centrum**: Znajduje "strukturalny środek" dzielonego czworokąta. Nowa logika szuka węzła z etykietą zaczynającą się od `c_` lub `center_`. Jest to znacznie pewniejsze niż heurystyki odległościowe.
2.  **Inteligentne Oznaczanie Krawędzi**:
    *   Analizuje sąsiadów. Jeśli sąsiad jest już "zagęszczony" (posiada w nazwie `h_` itp.), pomija oznaczanie tej krawędzi.
    *   Jeśli krawędź jest "świeża", oznacza ją `B=1, R=1`.
3.  **Proaktywne Krawędzie Wewnętrzne**: Funkcja szuka też krawędzi "szprych" (od rogów do środka) i też je oznacza.

```python
def split_trapezoid(...):
    # ...
    # 1. Identfikacja Centrum po etykiecie
    center_node = None
    for n in q_element.nodes:
        if n.label.startswith("c_") or n.label.startswith("center"):
            center_node = n
            break
    
    # 2. Oznaczanie krawędzi (tylko tych niezagęszczonych)
    for neighbor in adjacent_nodes:
        if is_refined_node(neighbor):
            continue 
        # ... oznacz krawędź ...

    # 3. Aplikuj pętlę P4 (Breaking Boundaries)
    while p4.can_apply(graph):
        graph.apply(p4)
    
    # 4. Zaznacz Q i wykonaj P5
    graph.add_edge(HyperEdge(q_element.nodes, "Q", R=1, ...))
    if p5.can_apply(graph):
        graph.apply(p5)
```

### Mechanizm 3: Pętla Stabilności (Stability Loop)
Po każdej operacji `split_trapezoid`, sterownik uruchamia tzw. *Stability Loop*. Jest to `while True`, który próbuje uruchomić JAKĄKOLWIEK produkcję naprawczą (`P2`, `P3`, `P4`).
Gwarantuje ona spójność topologiczną siatki (eliminacja wiszących węzłów).

```python
def run_stability():
    while True:
        broken = False
        if p4.can_apply(graph): graph.apply(p4); broken=True
        elif p2.can_apply(graph): graph.apply(p2); broken=True
        elif p3.can_apply(graph): graph.apply(p3); broken=True
        if not broken: break
```

Dzięki temu podejściu (Geometryczne Szukanie celu -> Inteligentny Split -> Stabilizacja), sterownik poprawnie realizuje zadane zageszczenie siatki.
