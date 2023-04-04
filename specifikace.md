Pokud je požadováno přemístění nákladu z jednoho místa do druhého, vozík si materiál vyzvedne do 1 minuty.

- OMISSION, to, že si vozík materiál vyzvedne, není důsledek - ten chybí.
- AMB_TEMPORAL, není specifikováno do 1 minuty od čeho.
- AMB_LOGIC, implicitní spojka mezi první a druhou větou. 
- AMB_STATEMENT, nejezdnoznačná slova místo, náklad a materiál.

*Pokud je nastaven požadavek na přesun materiálu vozíkem ze zdrojové stanice do cílové stanice a pokud vozík přijede do zdrojové stanice do 1 minuty od nastavení tohoto požadavku, pak bude tento materiál naložen.*

Pokud se to nestihne, materiálu se nastavuje prioritní vlastnost. 

- AMB_REFERENCE, odkaz na "to".
- UNSPECIFIED_SUBJECT, není jasné, co se nestihne.
- IMPLICIT, implicitně se předpokládá, že nastavení prioritní vlastnosti vytvoří i prioritní požadavek.

*Pokud je nastaven požadavek na přesun materiálu vozíkem ze zdrojové stanice do cílové stanice a pokud vozík nepřijede do zdrojové stanice do 1 minuty od nastavení tohoto požadavku, pak je materiálu nastavena prioritní vlastnost  a je nastaven prioritní požadavek na přesun materiálu s prioritní vlastností.*

Každý prioritní materiál musí být vyzvednutý vozíkem do 1 minuty od nastavení prioritního požadavku. 

- DANGLING_ELSE, není uvedeno, co se stane, pokud materiál nebude vyzvednutý.
- AMB_SUBJECT, prioritním materiálem se myslí materiál s prioritní vlastností.
- AMB_STATEMENT, zaměňování slov naložit a vyzvednout.

*Pokud je nastaven požadavek na přesun materiálu s prioritní vlastností a pokud vozík přijede do zdrojové stanice do 1 minuty od nastavení tohoto požadavku, pak je tento materiál naložen. Pokud je nastaven požadavek na přesun materiálu s prioritní vlastností a pokud vozík do zdrojové stanice nepřijede do 1 minuty od nastavení tohoto požadavku, pak je vyvolána výjimka EX_PRIOR.*

Pokud vozík nakládá prioritní materiál, přepíná se do režimu pouze-vykládka. 

- AMB_STATEMENT, prioritním materiálem se myslí prioritní požadavek na přesun materiálu.
- UNSPECIFIED_SUBJECT, není jasné, kdo nebo co se přepíná.

*Pokud vozík naložil materiál s prioritní vlastností, pak se vozík přepne do režimu pouze-vykládka.*

V tomto režimu zůstává, dokud nevyloží všechen takový materiál. 

- DANGLING_ELSE, není řečeno, co se stane, pokud je materiál vyložen.
- UNSPECIFIED_SUBJECT, není jasné, kdo v tomto režimu zůstává.
- AMB_REFERENCE, není jasně specifikované v jakém režimu a jaký materiál.

*Pokud je vozík v režimu pouze-vykládka a pokud má naložen materiál s prioritní vlastností, pak zůstává v režimu pouze-vykládka. Pokud je vozík v režimu pouze-vykládka a nemá naložen žádný materiál s prioritní vlastností, pak se vozík přepne do režimu nakládka-vykládka.*

Normálně vozík během své jízdy může nabírat a vykládat další materiály v jiných zastávkách. 

- DANGLING ELSE, může.
- AMB_STATEMENT, není specifikováno, co znamená normálně, nejednoznačná slova nabírat, zastávka.
- AMB_TEMPORAL, není jasné, jaký časový úsek znamená "během své jízdy". 

*Pokud je vozík v režimu nakládka-vykládka a pokud má vozík volný alespoň jeden slot a pokud naložení materiálu nepřevýší maximální nosnost vozíku, vozík tento materiál naloží. Pokud je vozík v režimu nakládka-vykládka a pokud je vozík v cílové stanici alespoň jednoho materiálu, který je na vozíku naložen, pak vozík tento materiál ve stanici vyloží. Pokud je vozík v režimu pouze-vykládka, pak vozík nenaloží žádný materiál a vyloží pouze již vyzvednuté materiály v jejich cílových stanicích.*

Na jednom místě může vozík akceptovat nebo vyložit jeden i více materiálů. 

- DANGLING_ELSE, může.
- AMB_STATEMENT, nejasná slova místo a akceptovat.

*Pokud je ve zdrojové stanici jeden a více materiálů a pokud má vozík volný alespoň jeden slot, pak je na vozík naloženo takové množství materiálu, které nepřevýší maximální nosnost vozíku ani počet volných slotů. Pokud je vozík ve stanici, pak vozík vyloží všechen materiál, který má tuto stanici jako cílovou stanici.*

Pořadí vyzvednutí materiálů nesouvisí s pořadím vytváření požadavků. 

- OMISSION, nejsou jasné příčiny a důsledky.
- UNSPECIFIED_SUBJECT, není jasné, kdo nebo co materiál vyzvedává.

*Pokud je nastaven požadavek na přesun materiálu ze zdrojové stanice, pak je tento materiál na vozík naložen ve chvíli, kdy se vozík v dané zdrojové stanici nachází.*

Vozík neakceptuje materiál, pokud jsou všechny jeho sloty obsazené nebo by jeho převzetím byla překročena maximální nosnost.

- AMB_STATEMENT, nejasné slovo "neakceptuje".
- AMB_REFERENCE, jeho sloty znamená sloty vozíku, ale jeho převzetím znamená převzetím materiálu.

*Pokud je nastaven požadavek na přesun materiálu a pokud má vozík všechny sloty obsazené, pak tento materiál není naložen. Pokud je nastaven požadavek na přesun materiálu a pokud by naložením tohoto materiálu byla překročena maximální nosnost vozíku, pak není tento materiál naložen. Pokud je nastaven požadavek na přesun materiálu a pokud má vozík volný alespoň jeden slot a pokud naložením tohoto materiálu nebude překročena nosnost tohoto vozíku, vozík materiál naloží.*
