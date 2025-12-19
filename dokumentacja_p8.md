# Dokumentacja Produkcji P8

## Gramatyka Hipergrafów – Metoda PolyDPG

### Opis Produkcji P8

**Produkcja P8** jest operacją finalizującą proces podziału (refinementu) elementu pięciokątnego. Jest ona stosowana w momencie, gdy otoczenie elementu wymusiło już podział wszystkich jego krawędzi brzegowych. Produkcja ta przekształca jeden element pięciokątny w pięć mniejszych elementów czworokątnych, wykorzystując istniejące węzły wiszące na brzegach.

---

## Lewa strona produkcji (LHS)

Produkcja P8 poszukuje w grafie podgrafu spełniającego rygorystyczne warunki topologiczne i atrybutowe:

1.  **Element centralny**: Wymagana jest obecność hiperkrawędzi typu `P` (Pentagon).
2.  **Atrybut sterujący**: Element ten musi posiadać atrybut `R=1`, co oznacza, że został on oznaczony do podziału przez wcześniejsze reguły (np. P0 lub w wyniku propagacji).
3.  **Geometria węzłów**: Element musi być rozpięty na dokładnie 5 wierzchołkach narożnych.
4.  **Warunek otoczenia (Kluczowy)**: Algorytm weryfikuje otoczenie każdego z 5 boków pięciokąta. Aby produkcja mogła zostać wykonana, **każda** krawędź brzegowa musi być już podzielona. Oznacza to, że pomiędzy każdą parą sąsiednich wierzchołków narożnych musi znajdować się węzeł wiszący (`hanging node`), połączony z nimi krawędziami typu `E`.

## Prawa strona produkcji (RHS)

Po pomyślnym dopasowaniu lewej strony, następuje transformacja struktury grafu:

1.  **Wyznaczenie środka**: Obliczany jest nowy węzeł centralny. Jego współrzędne $(x, y)$ są średnią arytmetyczną współrzędnych pięciu wierzchołków narożnych.
2.  **Rekonfiguracja topologii**:
    * Węzeł centralny zostaje połączony nowymi krawędziami wewnętrznymi (`boundary=False`) ze wszystkimi pięcioma węzłami wiszącymi, które znajdowały się na brzegach.
    * Oryginalna hiperkrawędź `P` zostaje usunięta.
3.  **Tworzenie elementów potomnych**: W miejsce jednego pięciokąta powstaje **5 nowych elementów czworokątnych** (typu `Q`). Każdy nowy element `Q` jest zdefiniowany przez czwórkę węzłów: [narożnik, sąsiedni węzeł wiszący, środek, poprzedni węzeł wiszący].
4.  **Reset atrybutów**: Nowo powstałe elementy otrzymują atrybut `R=0`, co kończy proces podziału w tej iteracji.

---

## Szczegółowy opis implementacji

Implementacja produkcji znajduje się w klasie `P8` w pliku `productions/p8.py`. Poniżej omówiono kluczowe fragmenty logiki.

### 1. Algorytm dopasowania (`find_match`)

Metoda `find_match` nie opiera się tylko na znalezieniu elementu `P`, ale musi zweryfikować jego kompletne sąsiedztwo.

* **Fragment: Filtracja kandydata**
    Kod najpierw iteruje po wszystkich hiperkrawędziach grafu, szukając takiej, która ma etykietę "P", atrybut `R=1` i dokładnie 5 węzłów. To jest wstępne sito selekcji.

* **Fragment: Weryfikacja "połamania" krawędzi**
    Dla każdego boku pięciokąta (definiowanego przez parę narożników $u$ i $v$), algorytm przeszukuje sąsiedztwo w poszukiwaniu węzła wiszącego $h$.
    Algorytm sprawdza sąsiadów węzła $u$ połączonych krawędzią `E`. Następnie weryfikuje, czy znaleziony kandydat $h$ jest połączony również z węzłem $v$.
    **Ważne zabezpieczenie:** Kod explicite sprawdza, czy znaleziony węzeł pośredni posiada flagę `hanging=True` oraz czy nie jest tożsamy z wierzchołkami narożnymi. Zapobiega to błędnym dopasowaniom w grafach o nietypowej topologii (np. trójkąty zdegenerowane).

* **Fragment: Zwracanie kontenera**
    Zamiast zwracać samą krawędź `P`, metoda zwraca syntetyczną hiperkrawędź `MATCH_CONTAINER`, która zawiera listę wszystkich 10 węzłów (5 narożnych + 5 wiszących). Jest to konieczne, aby mechanizm `apply` wiedział, które węzły są częścią transformowanego podgrafu.

### 2. Algorytm transformacji (`get_right_side`)

Metoda ta odpowiada za utworzenie wynikowego fragmentu grafu.

* **Fragment: Odtwarzanie struktury**
    Na podstawie przekazanego podgrafu, kod identyfikuje, które węzły są narożnikami (z oryginalnej krawędzi P), a które są węzłami wiszącymi. Zachowana jest kolejność cykliczna, co jest kluczowe dla poprawnego utworzenia czworokątów.

* **Fragment: Generowanie nowych elementów**
    W pętli `for i in range(5)` tworzone są nowe struktury.
    Kod pobiera atrybuty brzegowe (`B`) ze starych krawędzi łączących narożniki z węzłami wiszącymi, aby przenieść je na nowe krawędzie w grafie wynikowym.
    Następnie tworzona jest nowa hiperkrawędź `Q` (czworokąt) łącząca: `[u, h, center, h_prev]` z atrybutem `R=0`.

---

## Raport z testów (Idee i scenariusze)

Testy w pliku `tests/test_p8.py` zostały zaprojektowane tak, aby pokryć nie tylko ścieżkę pozytywną, ale również szereg przypadków brzegowych i potencjalnych błędów w danych wejściowych.

### 1. Testy poprawności strukturalnej i geometrycznej

* **Test: `test_apply_isomorphic`**
    * **Idea:** Jest to fundamentalny test sprawdzenia ("sanity check"). Przygotowujemy "idealny" graf wejściowy (pięciokąt foremny z idealnie podzielonymi krawędziami).
    * **Weryfikacja:** Sprawdzamy, czy produkcja w ogóle zadziałała (zwróciła 1), czy liczba węzłów wzrosła o 1 (nowy środek), czy zniknął element P i czy pojawiło się dokładnie 5 elementów Q.
* **Test: `test_center_coordinates`**
    * **Idea:** Weryfikacja poprawności matematycznej. Dla pięciokąta wpisanego w okrąg o środku (0,0), nowo wyliczony środek ciężkości również musi wypaść w punkcie (0,0).
    * **Weryfikacja:** Sprawdzenie współrzędnych $(x, y)$ węzła centralnego z dokładnością do 5 miejsc po przecinku.
* **Test: `test_apply_distorted_pentagon`**
    * **Idea:** Metoda PolyDPG działa na siatkach adaptacyjnych, które często są nieregularne. Test ten sprawdza, czy algorytm zadziała poprawnie na "krzywym", asymetrycznym pięciokącie.
    * **Weryfikacja:** Potwierdzenie, że logika opiera się na topologii (połączeniach), a nie na idealnej geometrii węzłów.

### 2. Testy kontekstu i izolacji (Embedding)

* **Test: `test_apply_on_complex_graph_preserves_context`**
    * **Idea:** Produkcja nigdy nie działa w próżni, lecz na fragmencie większego grafu. Ten test dodaje do grafu "szum" (węzły i krawędzie niepołączone z pięciokątem lub połączone tylko z jednym wierzchołkiem).
    * **Weryfikacja:** Upewniamy się, że produkcja zmodyfikowała tylko wskazany pięciokąt, a reszta grafu ("szum") pozostała nienaruszona.
* **Test: `test_two_pentagons_one_ready`**
    * **Idea:** Test selektywności. W grafie umieszczamy dwa pięciokąty: jeden spełnia warunki (wszystkie boki połamane), a drugiemu brakuje jednego węzła wiszącego.
    * **Weryfikacja:** Sprawdzamy, czy produkcja wybierze tylko ten poprawny, a niepoprawny pozostawi bez zmian. To symuluje realną sytuację na siatce FEM.

### 3. Testy negatywne (Odpuszczanie błędnych dopasowań)

* **Test: `test_apply_missing_break`**
    * **Idea:** Sprawdzenie głównego warunku produkcji P8. Usuwamy węzeł wiszący z **jednego** boku pięciokąta (przywracamy tam ciągłą krawędź).
    * **Weryfikacja:** Produkcja **nie może** się wykonać. Pięciokąt nie jest gotowy do podziału, dopóki wszystkie jego boki nie zostaną podzielone przez sąsiadów.
* **Test: `test_missing_corner_node`**
    * **Idea:** Symulacja uszkodzonego grafu (błąd danych). Usuwamy jeden z wierzchołków narożnych.
    * **Weryfikacja:** Algorytm `find_match` powinien bezpiecznie odrzucić taki element, nie powodując błędu wykonania (wyjątku), lecz po prostu nie znajdując dopasowania.
* **Test: `test_apply_R0`**
    * **Idea:** Weryfikacja flagi sterującej. Nawet jeśli geometria jest idealna, a topologia kompletna (wszystkie boki połamane), produkcja nie może ruszyć, jeśli atrybut `R` wynosi 0.
    * **Weryfikacja:** Produkcja zwraca 0 (brak zmian).
* **Test: `test_wrong_hypertag`**
    * **Idea:** Zabezpieczenie przed pomyleniem typów elementów. Podmieniamy etykietę elementu z `P` na `Q` (zachowując resztę struktury).
    * **Weryfikacja:** Produkcja musi być czuła na typ elementu i nie aplikować się do elementu `Q`, nawet jeśli wygląda on podobnie.

---

## Podsumowanie pokrycia wymagań

Zestaw testów pokrywa wszystkie krytyczne aspekty działania produkcji P8:
1.  **Poprawność algorytmiczną** (działanie na danych idealnych i zaszumionych).
2.  **Odporność na błędy** (brakujące elementy, złe atrybuty).
3.  **Poprawność matematyczną** (wyznaczanie środka).
4.  **Izolację w grafie** (nieinwazyjność względem sąsiadów).