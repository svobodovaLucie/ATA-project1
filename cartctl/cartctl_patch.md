Pomocí automatických testů v souboru `cartctl_test.py` byla odhalena chyba v implementaci souboru `cartctl.py`.  

Popis chyby:  
V případě, že prioritní požadavek na přesun materiálu vozíkem není odbaven do 1 minuty od nastavení tohoto požadavku, požadavek byl v původní implementaci jednoduše zahozen a uživatel o tom nebyl žádným způsobem informován.   

Popis opravy:  
V případě, že nastane situace, že prioritní požadavek není odbaven do 1 minuty od jeho nastavení, je vyvolána výjimka PrioRequestTimeout.
