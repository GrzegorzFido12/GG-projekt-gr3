# Dokumentacja Produkcji P11

## Opis produkcji

Produkcja **P11** transformuje sześciokąt z oznaczoną etykietą `S` (powierzchnia) na strukturę wewnętrzną złożoną z sześciu ścian trójkątnych (Q-edges) i wierzchołka centralnego. Produkcja implementuje podziału sześciokąta na sześć trójkątów ze wspólnym wierzchołkiem w centrum.

### Struktura lewej strony produkcji (LHS - Left-Hand Side)

Lewa strona produkcji definiuje szablon grafu do dopasowania:

- **Węzły**: 12 węzłów (6 narożników + 6 punktów pośrednich)
- **Krawędzie S**: Jedna hiperłącze `S` z atrybutem `R=1` łącząca wszystkie 6 narożników sześciokąta
- **Krawędzie E**: 12 krawędzi typu E (boundary edges) łączących każdy narożnik z sąsiadującymi punktami pośrednimi
  - Każdy punkt pośredni jest połączony z dwoma narożnikami
  - Atrybuty: `B=1` (boundary edges)

Geometria: 6 narożników sześciokąta regularnego + 6 punktów pośrednich na krawędziach

### Struktura prawej strony produkcji (RHS - Right-Hand Side)

Prawa strona produkcji definiuje wynik transformacji:

- **Nowy węzeł centralny**: Wierzchołek w geometrycznym centrum sześciokąta
- **Zachowane węzły**: Wszystkie węzły z lewej strony pozostają
- **Nowe hiperłącze Q**: 6 ścian czworokątnych `(center, h_prev, c, h_next)` z `R=0`
  - Każda ściana ma wierzchołek centralny, dwa punkty pośrednie i jeden narożnik
- **Krawędzie wewnętrzne E**: Nowe krawędzie łączące centrum z punktami pośrednimi
  - Atrybuty: `R=0, B=0` (krawędzie wewnętrzne)
- **Zachowane krawędzie graniczne**: Krawędzie graniczne z lewej strony zachowują atrybuty

---

## Metody implementacji

### 1. Weryfikacja izomorfizmu grafu (`is_isomorphic`)

**Cel**: Sprawdzenie, czy dany podgraf jest izomorficzny z lewą stroną produkcji.

**Algorytm**:

```
1. Pobranie lewej strony produkcji (szablon)
2. Sprawdzenie warunku koniecznego:
   - Liczba węzłów w podgrafie == 12
   - Istnieje jedna hiperłącze S z R=1 i 6 węzłami
3. Identyfikacja narożników i punktów pośrednich:
   - Narożniki: węzły z hiperłącze S
   - Punkty pośrednie: pozostałe węzły
   - Sprawdzenie: każdej ma być dokładnie 6
4. Sprawdzenie topologii poprzez permutacje:
   - Dla każdej permutacji narożników testowych:
     a) Mapowanie węzłów lewej strony na badane węzły
     b) Dla każdego punktu pośredniego LHS:
        - Znalezienie jego dwóch sąsiadujących narożników
        - Mapowanie ich na narożniki z badanego grafu
        - Znalezienie punktu pośredniego, który ma dokładnie tych samych sąsiadów
     c) Jeśli wszystkie punkty pośrednie się mapują poprawnie - IZOMORFICZNY
5. Zwrócenie wyniku
```

**Szczegółowe kroki**:

- **Liczenie węzłów**: Gwarantuje prawidłową strukturę rozmiaru
- **Weryfikacja S-edge**: Hiperkrawędź `S` musi mieć dokładnie 6 węzłów (narożniki) i `R=1`
- **Permutacje narożników**: Próbuje wszystkich możliwych mapowań narożników szablonu na węzły badanego grafu
- **Walidacja topologiczna**: Każdy punkt pośredni musi mieć dokładnie 2 sąsiadów spośród narożników
- **Ekwiwalentność struktury**: Struktura połączeń musi być identyczna jak w szablonie

### 2. Sprawdzenie możliwości aplikacji produkcji (`can_apply`)

**Cel**: Szybkie sprawdzenie, czy produkcja może być zastosowana do grafu.

**Implementacja**: Delegacja do metody `find_match()` - jeśli znaleziono dopasowanie, zwraca `True`.

### 3. Wyszukiwanie dopasowania w dużym grafie (`find_match`)

**Cel**: Znalezienie w dużym grafie podgrafu izomorficznego z lewą stroną produkcji.

**Algorytm**:

```
1. Dla każdej hiperłącze w grafie:
   a) Sprawdzenie warunków kandydata:
      - Typ: S
      - Atrybut: R = 1
      - Liczba węzłów: 6 (narożniki)
   
   b) Jeśli warunki spełnione:
      - Pobranie węzłów jako potencjalne narożniki
      - Znalezienie wszystkich węzłów w grafie, które NIE są narożnikami
      - Filtrowanie: pozostają tylko węzły będące punktami pośrednimi
      
   c) Sprawdzenie punktów pośrednich:
      - Dla każdego kandydata na punkt pośredni:
        * Sprawdzenie czy jest połączony E-krawędzią z dokładnie 2 narożnikami
        * Sprawdzenie czy leży geometrycznie na odcinku między tymi narożnikami
      
   d) Jeśli znaleziono dokładnie 6 punktów pośrednich - DOPASOWANIE ZNALEZIONE

2. Zwrócenie znalezionego dopasowania (lub None)
```

**Funkcje pomocnicze**:

- **`is_midpoint()`**: Sprawdza, czy węzeł jest punktem pośrednim
  - Ma dokładnie 2 sąsiadów E-krawędzią
  - Leży na geometrycznym odcinku między sąsiadami (kollinearność z tolerancją 1e-4)
  
- **`_corner_neighbors()`**: Zwraca narożniki połączone E-krawędzią z danym węzłem

### 4. Walidacja wyniku aplikacji produkcji

**Metody weryfikacji**:

1. **Liczba ścian Q**: Powinno powstać dokładnie 6 ścian typu Q
2. **Atrybut R nowych ścian**: Wszystkie nowe ściany Q powinny mieć `R=0`
3. **Wierzchołek centralny**: Powinien powstać dokładnie 1 wierzchołek "v_center"
4. **Spójność krawędzi**: 
   - Krawędzie graniczne zachowują swoje atrybuty z lewej strony
   - Krawędzie wewnętrzne mają `R=0, B=0`
5. **Topologia**: Każda ściana Q powinna mieć 4 węzły (center, 2 punkty pośrednie, 1 narożnik)

---

## Przygotowanie testów

### Struktura testów

Testy weryfikują:

1. **Poprawność dopasowania**: Czy algorytm poprawnie identyfikuje izomorficzne podgrafy
2. **Atrybuty topologiczne**: Czy struktura wynikowa jest prawidłowa
3. **Obsługa niestandardowych geometrii**: Czy produkcja działa dla nieregularnych sześciokątów
4. **Izolacja produkcji**: Czy produkcja nie zmienia reszty grafu
5. **Idempotenencja**: Czy produkcja nie może być zastosowana dwukrotnie do tej samej struktury

### Funkcje pomocnicze do tworzenia testów

```python
create_valid_hexagon(r_val=1, prefix="v")
```
- Tworzy poprawny sześciokąt zgodny z LHS
- Parametr `r_val`: wartość atrybutu R w S-edge (domyślnie 1)
- Parametr `prefix`: przedrostek dla etykiet węzłów

```python
create_valid_hexagon_with_b0(r_val=1, prefix="v")
```
- Wariant sześciokąta z mieszanymi atrybutami B (niektóre krawędzie mają `B=0`)

---

## Przeprowadzone testy

### Test 1: Weryfikacja izomorfizmu (`test_isomorphism`)

**Cel**: Sprawdzenie algorytmu `is_isomorphic()` na grabach identycznych i zniekształconych.

**Scenariusze**:

| Scenariusz | Graf | Oczekiwany wynik | Opis |
|-----------|------|-----------------|------|
| Poprawny sześciokąt | 6 narożników, 6 punktów pośrednich, S-edge R=1 |  Izomorficzny | Idealny szablonowy graf |
| Zła hiperłącze | Identyczna topologia, ale S-edge zamieniają na "X" | ✗ Nie izomorficzny | Błędny typ krawędzi |
| Brakująca krawędź | Usunia się jedna E-krawędź | ✗ Nie izomorficzny | Niekompleta topologia |

**Wizualizacje**:

**Poprawny graf** - 
<img src="../visualizations/p11_visualizations/test_p11_isomorphism_ok.png" alt="Poprawny sześciokąt" style="width:50%" />

**Błędny typ krawędzi** - 
<img src="../visualizations/p11_visualizations/test_p11_isomorphism_bad.png" alt="Sześciokąt ze złą etykietą krawędzi" style="width:50%" />

**Brakująca krawędź** - 
<img src="../visualizations/p11_visualizations/test_p11_isomorphism_missing_edge.png" alt="Sześciokąt z brakującą krawędzią" style="width:50%" />

---

### Test 2: Weryfikacja atrybutu R (`test_r_flag`)

**Cel**: Sprawdzenie, że produkcja działa tylko dla S-edge z `R=1`.

**Scenariusze**:

| R-wartość | Można aplikować? | Opis |
|-----------|-----------------|------|
| R=0 | ✗ Nie | Produkcja nie powinna się aplikować |
| R=1 |  Tak | Produkcja powinna się aplikować |

**Wizualizacje**:

**Sześciokąt z R=0** - 
<img src="../visualizations/p11_visualizations/test_p11_r_flag_r0.png" alt="Sześciokąt z R=0 - produkcja nie aplikuje się" style="width:50%" />

**Sześciokąt z R=1** - 
<img src="../visualizations/p11_visualizations/test_p11_r_flag_r1.png" alt="Sześciokąt z R=1 - produkcja aplikuje się" style="width:50%" />

---

### Test 3: Wyszukiwanie w dużym grafie (`test_subgraph_in_large_graph`)

**Cel**: Weryfikacja, że produkcja prawidłowo znajduje i transformuje podgraf w większym grafie, ignorując resztę.

**Struktura testu**:
1. Tworzenie dużego grafu:
   - Dodanie szumu (2 dodatkowe węzły z krawędzią)
   - Dodanie poprawnego sześciokąta
2. Aplikacja produkcji P11
3. Weryfikacja:
   - Szum pozostaje niezmieniony
   - Powstało dokładnie 6 ścian Q
   - Struktura sześciokąta się transformowała

**Przed aplikacją** - 
<img src="../visualizations/p11_visualizations/test_p11_subgraph_in_large_graph_before.png" alt="Duży graf z wbudowanym sześciokątem - przed" style="width:50%" />

**Po aplikacji** - 
<img src="../visualizations/p11_visualizations/test_p11_subgraph_in_large_graph_after.png" alt="Duży graf z wbudowanym sześciokątem - po transformacji" style="width:50%" />


---

### Test 4: Poprawność wyniku (`test_result_correctness`)

**Cel**: Weryfikacja strukturalnej poprawności grafu wynikowego.

**Weryfikacje**:
1. Istnieje dokładnie 1 wierzchołek centralny `v_center`
2. Powstało dokładnie 6 ścian Q
3. Wszystkie ściany Q mają `R=0`

**Wejście** - 
<img src="../visualizations/p11_visualizations/test_p11_result_correctness_before.png" alt="Sześciokąt wejściowy - poprawność wyniku" style="width:50%" />

**Wynik po transformacji** - 
<img src="../visualizations/p11_visualizations/test_p11_result_correctness_after.png" alt="Sześciokąt po transformacji - 6 ścian Q i centrum" style="width:50%" />

---

### Test 5: Nieregularna geometria (`test_irregular_geometry`)

**Cel**: Weryfikacja, że produkcja działa dla sześciokątów o nieregularnej geometrii.

**Nieregularny sześciokąt** - 
<img src="../visualizations/p11_visualizations/test_p11_irregular_geometry_before.png" alt="Sześciokąt o asymetrycznej geometrii" style="width:50%" />

**Po transformacji** - 
<img src="../visualizations/p11_visualizations/test_p11_irregular_geometry_after.png" alt="Transformacja sześciokąta nieregularnego" style="width:50%" />
- Sześciokąt z wierzchołkami rozmieszczonymi asymetrycznie
- Rozstaw punktów pośrednich odpowiadający asymetrii

**Wynik**:  Produkcja poprawnie transformuje nieregularne sześciokąty


---

### Test 6: Podwójna aplikacja (`test_double_application`)

**Cel**: Weryfikacja idempotenencji - produkcja nie powinna się aplikować dwukrotnie.

**Scenariusz**:
1. Aplikacja P11 do sześciokąta
2. Próba aplikacji P11 ponownie

**Wynik**: 
-  Pierwsze zastosowanie: `can_apply() = True`
-  Drugie zastosowanie: `can_apply() = False`

**Wniosek**: Produkcja nie tworzy struktur, do których mogłaby się ponownie aplikować

---

### Test 7: Wbudowany sześciokąt (`test_embedded_hexagon`)

**Cel**: Weryfikacja działania produkcji dla sześciokąta z zewnętrznymi połączeniami.

**Struktura testu**:
1. Tworzenie sześciokąta
2. Dodanie dla każdego narożnika:
3. Aplikacja produkcji
4. Weryfikacja transformacji wewnętrznej przy zachowaniu zewnętrznych połączeń

**Wynik**:  Produkcja prawidłowo transformuje strukturę wewnętrzną zachowując zewnętrzne połączenia

**Wizualizacje**:
<img src="../visualizations/p11_visualizations/test_p11_embedded_hexagon_before.png" alt="Sześciokąt z wbudowanymi węzłami zewnętrznymi" style="width:50%" />
<img src="../visualizations/p11_visualizations/test_p11_embedded_hexagon_after.png" alt="Sześciokąt z wbudowanymi węzłami - po transformacji" style="width:50%" />

---

### Test 8: Atrybuty krawędzi (`test_label`)

**Cel**: Weryfikacja prawidłowego propagowania atrybutów B w krawędziach.

**Wzór**: 
```
B=0 krawędzie po = B=0 krawędzie przed + 11
```

**Wynik**:  Atrybuty krawędzi propagują się prawidłowo

**Wizualizacje**:

**Graf wejściowy** - 
<img src="../visualizations/p11_visualizations/test_p11_label_before.png" alt="Sześciokąt ze zmieszanymi atrybutami B" style="width:50%" />

**Graf wynikowy** - 
<img src="../visualizations/p11_visualizations/test_p11_label_after.png" alt="Graf wynikowy z propagowanymi atrybutami B" style="width:50%" />
  (dodane 12 nowych krawędzi wewnętrznych z `B=0`, ale zmienią się atrybuty istniejących)

---

## Podsumowanie

Produkcja P11 została pomyślnie zaimplementowana z:

 **Algorytmem dopasowania**: Wieloetapowa weryfikacja izomorfizmu z optymalizacją permutacji  
 **Transformacją**: Prawidłowe budowanie grafu wynikowego z atrybutami krawędzi  
 **Kompletnymi testami**: 8 scenariuszy testowych weryfikujących różne aspekty  
 **Obsługą geometrii**: Działanie zarówno dla regularnych, jak i nieregularnych sześciokątów  
 **Izolacją operacji**: Niezmienność reszty grafu podczas transformacji sześciokąta  

Wszystkie testy przechodzą pomyślnie 
