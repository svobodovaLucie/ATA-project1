# Dokumentace testovací sady pro řízení vozíku v robotické továrně

Automatizované testování a dynamická analýza (ATA), Projekt 1  
FIT VUT 2022/2023  
Autor: Lucie Svobodová, xsvobo1x@stud.fit.vutbr.cz  

## Graf příčin a důsledků (CEG)
Graf příčin a důsledků, který byl vygenerován pomocí nástroje [ceg.testos.org](http://ceg.testos.org/), je přiložen v souborech `ceg.txt` (konfigurace) a `ceg.png` (vygenerovaný graf ve formě obrázku). Z vygenerovaných testovacích scénářů bylo vybráno 5 scénářů tak, aby byly pokryty všechny příčiny a důsledky.

### Rozhodovací tabulka pro vybraných 5 testovacích scénářů
TestId | Popis                                                               | `test_ceg1` | `test_ceg2` | `test_ceg3` | `test_ceg4` | `test_ceg5` |
| :--: | :-----------------------------------------------------------------: | :---------: | :---------: | :---------: | :---------: | :---------: |
| t1   | časové pásmo kratší než 1 minuta od nastavení požadavku             | 0 | 1 | 1 | 1 | 1 | 
| t2   | časové pásmo od 1 minuty od nastavení požadavku                     | 0 | 1 | 1 | 0 | 1 |
| t3   | časové pásmo kratší než 1 minuta od nastavení prioritního požadavku | 0 | 1 | 1 | 0 | 1 |
| t4   | časové pásmo od 1 minuty od nastavení prioritního požadavku         | 0 | 0 | 1 | 0 | 0 |
| 1    | je nastaven požadavek na přesun materiálu bez prioritní vlastnosti  | 0 | 1 | 1 | 0 | 1 |
| 2    | vozík přijel do zdrojové stanice v časovém pásmu t1                 | 0 | 0 | 0 | 1 | 0 |
| 3    | je nastaven požadavek na přesun materiálu s prioritní vlastností    | 0 | 1 | 1 | 0 | 1 |
| 4    | vozík přijel do zdrojové stanice v časovém pásmu t3                 | 0 | 1 | 0 | 0 | 1 |
| 5    | vozík nemá naložený materiál s prioritní vlastností                 | 1 | 1 | 1 | 0 | 1 |
| 6    | vozík má alespoň jeden volný slot                                   | 1 | 1 | 0 | 1 | 1 |
| 7    | naložení materiálu na vozík nepřekročí maximální nosnost vozíku     | 1 | 0 | 1 | 1 | 1 |
| 71   | materiál bez prioritní vlastnosti je naložen                        | false | false | false | true  | false |
| 72   | nastavení prioritního požadavku                                     | false | true  | true  | false | true  |
| 73   | materiál s prioritní vlastností je naložen                          | false | false | false | false | true  |
| 74   | vyvolání výjimky PrioRequestTimeout                                 | false | false | true  | false | false |
| 75   | přepnutí do režimu pouze_vykládka                                   | false | true  | false | false | true  |
| 76   | přepnutí do režimu nakládka_vykládka                                | false | true  | false | false | true  |

## Vstupní parametry testu
Vstupní parametry testu, které byly identifikovány jako nejdůležitější, jsou vypsány v následující tabulce.
| Identifikátor parametru               | Popis                                        |
| ------------------------------------- | -------------------------------------------- |
| cart_slots_count                      | počet slotů vozíku                           |
| cart_max_capacity                     | maximální nosnost vozíku                     |
| req_count                             | počet požadavků                              |
| req_weight                            | součet váhy požadavků na vozíku              |
| req_track_path                        | délka dráhy požadavku                        |
| num_requests_to_load_in_one_station   | počet požadavků se shodnou zdrojovou stanicí |
| num_requests_to_unload_in_one_station | počet požadavků se shodnou cílovou stanicí   |
| time_between_two_requests             | čas mezi naplánováním více požadavků         |

### Charakteristiky parametrů
V následujících tabulkách jsou vypsány identifikované charakteristiky vstupních parametrů, jejich rozdělení na bloky a omezení mezi jednotlivými bloky.

| cart_slots_count | počet slotů vozíku |
| :-------------: | :----: |
| 1 | cart_slots_count = 1 |
| 2 | cart_slots_count = 2 |
| 3 | cart_slots_count = 3 or cart_slots_count = 4 |
- `cart_slots_count.1 -> !more_req_to_unload_in_one_station.1`
- `cart_slots_count.1 -> !cart_max_capacity.1`
- `cart_slots_count.3 -> !cart_max_capacity.3`

| cart_max_capacity | maximální nosnost vozíku |
| :-------------: | :----: |
| 1 | cart_max_capacity = 50 |
| 2 | cart_max_capacity = 150 |
| 3 | cart_max_capacity = 500 |
- `cart_max_capacity.1 -> !cart_slots_count.1`
- `cart_max_capacity.3 -> !cart_slots_count.3`

| req_count | počet požadavků |
| :-------------: | :----: |
| 1 | req_count < 1 |
| 2 | req_count = 1 |
| 3 | req_count > 1 |
- `req_count.1 -> cart_capacity_full.2`
- `req_count.1 -> req_track_path_longer_than_one.2`
- `req_count.1 -> more_req_to_unload_in_one_station.2`
- `req_count.2 -> more_req_to_unload_in_one_station.2`
- `req_count.1 -> more_req_to_load_in_one_station.2`
- `req_count.2 -> more_req_to_load_in_one_station.2`
- `req_count.1 -> time_between_two_requests_less_than_minute.2`
- `req_count.2 -> time_between_two_requests_less_than_minute.2`

| cart_capacity_full | součet váhy materiálu na vozíku je roven maximální nosnosti vozíku |
| :-------------: | :----: |
| 1 | true |
| 2 | false |

| req_track_path_longer_than_one | dráha na přesun alespoň jednoho materiálu je větší než 1 |
| :-------------: | :----: |
| 1 | true |
| 2 | false |

| more_req_to_load_in_one_station | existují alespoň 2 požadavky se stejnou zdrojovou stanicí |
| :-------------: | :----: |
| 1 | true |
| 2 | false |

| more_req_to_unload_in_one_station | existují alespoň 2 požadavky se stejnou cílovou stanicí |
| :-------------: | :----: |
| 1 | true |
| 2 | false |

| time_between_two_requests_less_than_minute | doba mezi vytvořením dvou požadavků (u alespoň jedné dvojice požadavků) je menší než 1 minuta |
| :-------------: | :----: |
| 1 | true |
| 2 | false |

### Kombinace bloků charakteristik
Charakteristiky parametrů a omezení kombinací bloků byla uložena do souboru `combine.json`. Tento soubor byl použit pro nástroj [combine.testos.org](http://combine.testos.org/), pomocí něhož byly vygenerovány minimální kombinace dvojic charakteristik.

TestId | cart_slots_count | cart_max_capacity | req_count | cart_capacity_full | req_track_path_longer_than_one |  more_req_to_load_in_one_station |  more_req_to_unload_in_one_station | time_between_two_requests_less_than_minute |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
`combine1` | 1 | 2 | 1 | false | false | false | false | false
`combine2` | 1 | 3 | 2 | true  | true  | false | false | false
`combine3` | 2 | 1 | 1 | false | false | false | false | false
`combine4` | 2 | 2 | 2 | true  | true  | false | false | false
`combine5` | 2 | 3 | 3 | false | true  | true  | true  | true
`combine6` | 3 | 1 | 2 | true  | false | false | false | false
`combine7` | 3 | 2 | 3 | true  | true  | true  | true  | true
`combine8` | 3 | 1 | 1 | false | false | false | false | false
`combine9` | 2 | 1 | 3 | true  | true  | true  | false | true
`combine10`| 1 | 2 | 3 | true  | false | true  | false | true
`combine11`| 2 | 2 | 2 | false | true  | false | false | false
`combine12`| 2 | 3 | 3 | true  | false | false | true  | false
`combine13`| 2 | 1 | 3 | true  | true  | true  | true  | false
`combine14`| 2 | 2 | 3 | true  | true  | false | false | true

## Pokrytí požadavků na test automatizovanými testy
Následující tabulky zobrazují pokrytí požadavků na test automatizovanými testy. První sloupec reprezentuje jednotlivá TestId testovacích případů z rozhodovací tabulky a z tabulky kombinací bloků charakteristik, druhý sloupec pak metody implementované v souboru `cartctl_test.py`. 

### Pokrytí kombinací z rozhodovací tabulky automatickými testy
| TestId | Název implementované metody |
| :----: | :-------------------------: |
| `ceg1` | `test_ceg1_combine1`        |
| `ceg2` | `test_ceg2`                 |
| `ceg3` | `test_ceg3`                 |
| `ceg4` | `test_ceg4`                 |
| `ceg5` | `test_ceg5`                 |

### Pokrytí kombinací bloků charakteristik automatickými testy
| TestId      | Název implementované metody |
| :---------: | :-------------------------: | 
| `combine1`  | `test_ceg1_combine1`        |
| `combine2`  | `test_combine2`             |
| `combine3`  | `test_combine3`             |
| `combine4`  | `test_combine4`             |
| `combine5`  | `test_combine5`             |
| `combine6`  | `test_combine6`             |
| `combine7`  | `test_combine7`             |
| `combine8`  | `test_combine8`             |
| `combine9`  | `test_combine9`             |
| `combine10` | `test_combine10`            |
| `combine11` | `test_combine11`            |
| `combine12` | `test_combine12`            |
| `combine13` | `test_combine13`            |
| `combine14` | `test_combine14`            |
