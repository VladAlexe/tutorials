# Statusul lecției — Sociologie computațională

Ultima actualizare: 2026-07-21 (tranșa 2 — completă)

Cursul conține o singură lecție: `highschool` (secțiunea 4). Statusul: **completă, 36 de carduri + 2 add-on quiz-uri = 38 blocuri**. Este ediția finală conform specificației.

- Fișier lecție: `lessons/highschool.json`
- Fișier curs (index): `data/course.json`
- Punct de intrare: `lesson.html?id=highschool`
- Titlu lecție: **Zvonul**

Numerotarea este stabilă. Sufixul `b` (#19b, #31b) indică un quiz add-on legat de cardul dinaintea lui.

---

## Metadate lecție

- **id:** `highschool`
- **sectionNumber:** 4
- **format:** `slides` (38 slide-uri navigabile, quiz+vote+quizset gating, resume banner)
- **title:** Zvonul
- **statsSource:** `data/highschool-stats.json` (substituție automată `{{...}}`)
- **Date reale:** SocioPatterns, liceul Thiers, Marsilia, 2013 (Mastrandrea et al., PLoS ONE 10(9), e0136497, 2015)
- **Rețeaua principală (MIN_WEIGHT = 3, ziua 1):** 93 elevi, 250 muchii

---

## Card #01 — text: „Întrebări vechi, urme noi"

- **type:** `text` · **id:** `s01-intrebari-vechi`
- **title:** Întrebări vechi, urme noi
- **content:**
  > Sociologia pune de peste un secol întrebări precise: cine se leagă de cine, cum circulă o idee, de ce apar și se mențin inegalitățile. Instrumentele ei clasice — sondajul reprezentativ, interviul, observația — rămân standardul pentru multe dintre aceste întrebări. Ce s-a schimbat e altceva: aproape orice acțiune lasă azi o înregistrare — un mesaj, o plată, o validare de card, o căutare. Sociologia computațională folosește aceste urme, împreună cu instrumentele clasice, ca să răspundă la aceleași întrebări la o scară imposibilă înainte.

---

## Card #02 — quiz: „Scara, măsura, simularea" (gating)

- **type:** `quiz` · **id:** `s02-scara-masura-simularea`
- **title:** Scara, măsura, simularea
- **intro (paragraf integral deasupra întrebării):**
  > Calculul aduce trei lucruri. Scara: milioane de interacțiuni analizate, nu sute de chestionare. Măsura: concepte discutate până acum calitativ — influență, popularitate, izolare — pot fi definite operațional și comparate numeric. Simularea: putem construi modele ale unui proces social și le putem rula de o mie de ori, întrebând ce s-ar schimba dacă regulile ar fi altele — un experiment pe care realitatea nu ni-l permite.
- **question:** Care dintre următoarele este o urmă digitală în sens strict?
- **options:**
  1. `[0]` „O opinie exprimată într-un interviu"
  2. `[1]` „Validarea unui abonament de transport" ← **corect (correctIndex: 1)**
  3. `[2]` „O amintire personală"
  4. `[3]` „Intenția de vot declarată la telefon"
- **explanation:** Urma digitală e înregistrarea automată a unui comportament, nu o declarație despre el. Distincția revine în lecție — și o vom vedea trădându-i chiar pe cei măsurați.

---

## Card #03 — text: „Marsilia, decembrie 2013" + preview

- **type:** `text` · **id:** `s03-marsilia`
- **title:** Marsilia, decembrie 2013
- **content:**
  > Într-un liceu francez, sute de elevi au purtat cinci zile senzori care înregistrau, la fiecare 20 de secunde, cine se află față în față cu cine. Nu conținutul discuțiilor — doar faptul și durata întâlnirii. Rezultatul: peste 180.000 de înregistrări, anonimizate și publicate pentru cercetare de proiectul SocioPatterns. Le-am atribuit prenume fictive, pentru lizibilitate. Lucrăm cu o felie: trei clase, o zi.
- **preview (monospace):**
  - legend: primele 5 rânduri din datele reale · coloane: timp (secunde unix), elev A, elev B, clasa A, clasa B
  - lines:
    ```
    1385982020  454  640  MP     MP
    1385982020    1  939  2BIO3  2BIO3
    1385982020  185  258  PC*    PC*
    1385982020   55  170  2BIO3  2BIO3
    1385982020    9  453  PC     PC
    ```
  - caption: Sursa: Mastrandrea, Fournet, Barrat. „Contact patterns in a high school." PLoS ONE 10(9): e0136497 (2015).

---

## Card #04 — text: „Vineri, 11:42"

- **type:** `text` · **id:** `s04-vineri-1142`
- **title:** Vineri, 11:42
- **content:**
  > Vineri, în pauza mare, un zvon a traversat școala: luni se anulează prima oră. Până la finalul programului îl cunoșteau zeci de elevi din clase diferite. Luni, ora s-a ținut. Zvonul e construit de noi pentru această analiză; școala, elevii și întâlnirile sunt reale. Miza nu e anecdotică: același mecanism duce o informație falsă prin milioane de conturi în câteva ore. Școala e laboratorul nostru la scară mică.

---

## Card #05 — text: „Cele trei întrebări"

- **type:** `text` · **id:** `s05-cele-trei-intrebari`
- **title:** Cele trei întrebări
- **content:**
  > Unu: cine avea poziția din care zvonul putea porni? Doi: pe ce trasee a circulat între clase? Trei: unde ar trebui plasată o informație ca să se răspândească maximal — și, simetric, cum se apără cineva de o asemenea plasare? Instrumentele: statistică descriptivă, analiza structurii, simulare. Orice analiză începe însă cu o decizie: cum transformăm oameni în date.

---

## Card #06 — interactive add-node: „Nodul"

- **type:** `interactive` · **id:** `s06-nodul` · **mode:** `add-node`
- **title:** Nodul
- **intro:** Reducem fiecare persoană la un punct. E o pierdere asumată — biografie, intenții, context dispar — în schimbul posibilității de a vedea structura întregului. La finalul lecției revenim la ce anume s-a pierdut. Adaugă primul elev.
- **buttonLabel:** „Adaugă un elev"
- **hint:** „Apasă butonul pentru a adăuga primul elev."
- **successText:** „Un nod: o persoană, redusă la poziția ei în structură."

---

## Card #07 — interactive add-edge: „Muchia: prima decizie"

- **type:** `interactive` · **id:** `s07-muchia` · **mode:** `add-edge`
- **title:** Muchia: prima decizie
- **intro:** O muchie e o relație — dar ce numim relație? Decizia noastră: două persoane sunt legate dacă au petrecut suficient timp față în față. Puteam decide altfel: prietenie declarată, contact online. Fiecare definiție produce altă rețea și alte concluzii.
- **buttonLabel:** „Conectează-i"
- **hint:** „Doi elevi, încă neconectați. Apasă butonul."
- **successText:** „În metodologie, asta se numește definiție operațională — locul unde cercetătorul își exercită și își asumă puterea. Revenim la consecințe în final."

---

## Card #08 — interactive mini-network: „Rețeaua de antrenament"

- **type:** `interactive` · **id:** `s08-reteaua-de-antrenament` · **mode:** `mini-network`
- **data:** `data/mini-network.json`
- **title:** Rețeaua de antrenament
- **intro:** Șase persoane, câteva legături. Atinge un nod: i se evidențiază vecinii și i se afișează gradul — numărul de legături directe. Prima operaționalizare: „cât de conectat ești" devine un număr întreg.
- **buttonLabel:** „Resetează" · **hint:** „Atinge un nod pentru a-i vedea vecinii și gradul."
- **Interacțiune:** tap pe nod → panoul afișează `nume — clasa — grad N`.

---

## Card #09 — quiz: „Ce reprezintă un nod?" (gating)

- **type:** `quiz` · **id:** `s09-quiz-nod`
- **question:** Într-o rețea socială, ce reprezintă un nod?
- **options:** [0] „O relație" · [1] „O persoană sau o entitate" ← **corect** · [2] „O medie statistică" · [3] „Un fișier"
- **explanation:** Nodurile sunt entitățile; muchiile, relațiile dintre ele. Definițiile ambelor sunt alegeri ale analistului.

---

## Card #10 — visualization network: „Felia: 93 de elevi, 250 de legături"

- **type:** `visualization` · **id:** `s10-felia` · **kind:** `network`
- **data:** `data/highschool-network.json`
- **title:** Felia: 93 de elevi, 250 de legături
- **description:** Trei clase, o zi. Culoarea: clasa.
- **caption:**
  > Structura se vede imediat: cele două clase de biologie comunică între ele; clasa de matematică-fizică e aproape închisă, legată de rest prin foarte puține legături. Observația are consecințe măsurabile — dar întâi: de unde a apărut desenul ăsta?

---

## Card #11 — code (Pyodide, instance = `prag`)

- **type:** `code` · **id:** `code-prag` · **instance:** `prag`
- **title:** Din 180.000 de rânduri: pragul
- **intro:** Am numărat întâlnirile fiecărei perechi și am păstrat perechile cu cel puțin PRAG întâlniri. Iată chiar regula. Modific-o și rulează.
- **initial (Python vizibil):**
  ```python
  PRAG = 3
  # O legatura exista daca perechea are cel putin PRAG intalniri de 20 de secunde.
  edges = [p for p in pairs if p["weight"] >= max(PRAG, prag_minim)]
  {"edges": edges, "prag": PRAG}
  ```
- **Context Pyodide:** `pairs` (493 perechi din `highschool-pairs.json`), `prag_minim` (1 — `edgeCountByThreshold[1]=493 < 800`, garda nu se activează)
- **La Run:** rețeaua de deasupra se redesenează cu edges returnate; contor „N muchii · prag X"
- **caption:** Rețeaua nu e un fapt natural: e rezultatul unei decizii de măsurare. Alt prag, altă rețea, alte concluzii. Cine controlează definițiile controlează rezultatele.

---

## Card #12 — chart freq: „Școala în cifre: frecvențele"

- **type:** `chart` · **variant:** `freq` · **id:** `s12-freq`
- **title:** Școala în cifre: frecvențele
- **intro:** Cea mai simplă întrebare statistică: câți sunt în fiecare grup?
- **Date:** `classFreq` din `data/highschool-stats.json`. Tabel + bare F/M per clasă.
- **caption:** Clasa 2BIO1 e predominant feminină (27 fete din 35 de elevi); clasa de matematică-fizică MP*1 e predominant masculină (20 băieți din 26). Compoziția grupurilor nu e detaliu — profilurile atrag diferit, iar asta va conta mai jos.

---

## Card #13 — chart grouped-strip: „Media pe grupuri"

- **type:** `chart` · **variant:** `grouped-strip` · **id:** `s13-grouped-strip`
- **title:** Media pe grupuri
- **intro:** Gradul mediu al unui elev, pe fiecare clasă. Prima comparație între grupuri: sunt clasele la fel de dense social?
- **Date:** `classMeanDegree` din stats. Per clasă: bară cu media (2BIO1=5,2 · 2BIO2=6,6 · MP*1=4,2) + puncte suprapuse (grad individual).
- **caption:** O medie pe grup ascunde variația din interiorul lui — punctele suprapuse pe bare arată exact cât. Diferența dintre medii e începutul oricărei analize comparative; variația din jurul lor e avertismentul ei.

---

## Card #14 — chart stacked: „Înăuntru și între"

- **type:** `chart` · **variant:** `stacked` · **id:** `s14-stacked`
- **title:** Înăuntru și între
- **intro:** Din tot timpul de contact, cât se petrece în interiorul claselor și cât între ele?
- **Date:** `classContactSplit` (bară procentuală intern/extern per clasă).
- **caption:** Global, doar **1,9%** (`{{classContactSplit.globalBetweenPct}}`) din timpul de contact traversează granițele de clasă. Când aproape toată variația e „înăuntru", apartenența la grup explică mult din cine cu cine vorbește — la noi, aproape tot. Zvonul a circulat totuși între clase: ne interesează exact excepțiile. Dosarul unu: cine avea poziția?

---

## Card #15 — chart dots: „93 de numere"

- **type:** `chart` · **variant:** `dots` · **id:** `s15-dots`
- **title:** 93 de numere
- **intro:** Pentru fiecare elev, gradul lui. Iată toate cele 93 de valori, fără nicio ordine.
- **Date:** `stats.degrees` (array 93). Randare: puncte împrăștiate cu seed fix.
- **caption:** Ilizibil — intenționat. Prima operație a statisticii: ordonarea.

---

## Card #16 — chart strip: „Ordinea"

- **type:** `chart` · **variant:** `strip` · **id:** `s16-strip`
- **title:** Ordinea
- **intro:** Aceleași valori, aliniate crescător.
- **topLabel:** `{{name:topDegree}}` → **Octav**
- **caption:** Majoritatea între 3 și 8 — și o valoare izolată sus: `{{name:topDegree}}` (**Octav**), `{{stats.maxDegree}}` (**15**) contacte. Primul suspect. Extremele se văd; proporțiile, încă nu.

---

## Card #17 — chart histogram fără slider: „Cutiile"

- **type:** `chart` · **variant:** `histogram` · **id:** `s17-histogram-static`
- **slider:** false · **defaultBinWidth:** 3
- **title:** Cutiile
- **intro:** Grupăm valorile pe intervale și numărăm câți elevi cad în fiecare.
- **caption:** Construcția pe care ai urmărit-o pas cu pas are un nume: histogramă. Uită-te la forma ei — nu e simetrică. Exact forma asta domină lumea socială.

---

## Card #18 — code (Pyodide, instance = `bins`)

- **type:** `code` · **id:** `code-bins` · **instance:** `bins`
- **title:** Coada lungă
- **intro:** Mulți cu puțin, puțini cu mult: distribuție asimetrică, cu coadă dreaptă. Aceeași formă la venituri, audiențe, dimensiunea orașelor, citări academice. Dar cât de netedă pare depinde de o alegere.
- **initial (Python):**
  ```python
  LATIME_CUTIE = 3
  # Aceleasi 93 de valori, regrupate pe intervale de LATIME_CUTIE.
  {"binWidth": LATIME_CUTIE}
  ```
- **Context Pyodide:** `degrees` (93 grade). La Run: histograma se re-desenează cu noua lățime.
- **caption:** Zimțat sau neted — din aceleași date. Un grafic corect factual poate induce în eroare prin alegeri de reprezentare nedeclarate. De-acum, la orice histogramă, întreabă cine a ales cutiile.

---

## Card #19 — chart meanmedian: „Media și medianul"

- **type:** `chart` · **variant:** `meanmedian` · **id:** `s19-meanmedian`
- **title:** Media și medianul
- **intro:** Media: `{{stats.meanDegree}}` (**5,4**). Medianul: `{{stats.medianDegree}}` (**5**). Apropiate — deocamdată. Trage cursorul: adaugă în școală un elev cu gradul pe care îl alegi, până la 200.
- **Interacțiune:** slider 0-200. La fiecare mișcare: histograma se re-bin-uiește cu noua valoare adăugată; linia medie (brună) și linia medianului (verde punctată) se mută live; contor sub grafic afișează valorile actualizate.
- **caption:** Media urcă abrupt; medianul abia se mișcă. În distribuții cu coadă, media e sensibilă la extreme; medianul descrie poziția tipică.

---

## Card #19b — quiz add-on: „Medie versus median" (gating)

- **type:** `quiz` · **id:** `s19b-quiz-medie`
- **title:** Medie versus median
- **question:** Venitul mediu dintr-o țară crește cu 10%, venitul median stagnează. Ce s-a întâmplat, cel mai probabil?
- **options:** [0] „Toți câștigă cu 10% mai mult" · [1] „Creșterea s-a concentrat la vârf" ← **corect** · [2] „Medianul e calculat greșit" · [3] „Oamenii declară venituri false"
- **explanation:** Exact ce ai văzut la cursor: coada trage media, medianul rămâne la omul din mijloc.

---

## Card #20 — vote cu reveal: „Votează, apoi verifică" (gating)

- **type:** `vote` · **id:** `s20-paradox`
- **title:** Votează, apoi verifică
- **question:** Prietenii tăi au, în medie, mai mulți prieteni decât tine, la fel, sau mai puțini?
- **options:** [0] Mai mulți · [1] Cam la fel · [2] Mai puțini
- **reveal:**
  - **text:** În școala noastră, un elev are în medie `{{friendshipParadox.meanDegree}}` (**5,4**) contacte; prietenii unui elev au în medie `{{friendshipParadox.meanFriendDegree}}` (**6,7**). `{{friendshipParadox.pctBelow}}` (**75**)% dintre elevi stau sub media prietenilor lor. Nu e psihologie, e eșantionare: persoanele cu multe legături apar, prin definiție, în listele multor altora — lista ta de prieteni supra-reprezintă popularii. Fenomenul e documentat de Scott Feld (1991). Orice feed îți arată o selecție deplasată spre cei vizibili; comparația zilnică cu ea e o comparație cu un eșantion deformat. Pentru anchetă: percepția despre „cine e excepțional" e distorsionată de structură — ne trebuie măsuri, nu impresii.
  - **bars:** 5,4 (elevul tipic) vs 6,7 (prietenii, verde)
  - **messagesByOption:**
    - `0` → „Ai votat împotriva intuiției comune — și datele îți dau dreptate, dar nu din motivul la care te gândești."
    - `1`/`2` → „Ai votat ca majoritatea — și, ca majoritatea, datele te contrazic."
- **Gating:** „Continuă" blocat până la vot. Persistat în `progress.votes.s20-paradox`.

---

## Card #21 — diffusion temporal: „Rețeaua respiră"

- **type:** `diffusion` · **mode:** `temporal` · **id:** `s21-temporal`
- **data:** `data/highschool-network.json` (baza noduri) · **hoursSource:** `data/highschool-hours.json`
- **title:** Rețeaua respiră
- **intro:** Desenul nostru adună o zi întreagă într-o singură imagine — o simplificare cu un cost precis. Datele au timpul la 20 de secunde. Trage cursorul peste orele zilei.
- **Interacțiune:** slider 0-4 (5 ore în ziua 1). La fiecare mișcare: rețeaua se re-desenează cu doar muchiile active în acea oră; ceas afișat („8:00" până „12:00"); contor „N legături active".
- **caption:** În ore, contactele se restrâng; în pauze, explodează — inclusiv între clase. Consecința metodologică: un drum care există în graful agregat poate să nu fi existat niciodată în realitate, dacă întâlnirile s-au petrecut în ordinea greșită. Informația nu circulă înapoi în timp. Rețelele cu timp se numesc rețele temporale — un domeniu activ de cercetare.

---

## Card #22 — code (Pyodide, instance = `diffuz`): „Modelul 1: pragul"

- **type:** `code` · **id:** `code-diffuz` · **instance:** `diffuz`
- **title:** Modelul 1: pragul
- **intro:** Primul model de răspândire, cu regula minimă: zvonul trece de la un elev la vecinii cu care legătura e suficient de strânsă.
- **initial (Python vizibil):**
  ```python
  SURSA = "Octav"
  PRAG_TRANSMITERE = 3
  # Zvonul pleaca de la SURSA si trece pe orice muchie cu greutate >= PRAG_TRANSMITERE.
  {"source_name": SURSA, "threshold": PRAG_TRANSMITERE}
  ```
- **Context Pyodide:** `nodes`, `edges` (rețeaua completă). La Run: modifică sursa+prag pe viz-ul de deasupra (BFS deterministic redesenat animat); meta: „Sursă: X · Prag: N · Acoperire: K din 93".
- **caption:** Din `{{name:topDegree}}` (Octav), zvonul acoperă biologia — dar cu prag ridicat nu atinge matematica. Pornit din matematică, moare acolo. Modelul e transparent și util. E și fals într-un punct precis — îl reparăm după ce îl exploatăm.

---

## Card #23 — diffusion investigation: „Patru definiții, patru suspecți"

- **type:** `diffusion` · **mode:** `investigation` · **id:** `s23-investigation`
- **title:** Patru definiții, patru suspecți
- **intro:** „Cine a răspândit zvonul?" sunt de fapt patru întrebări. Apasă fiecare definiție.
- **Interacțiune:** 4 butoane — Grad · Timp petrecut · Intermediere · Rază de răspândire. Fiecare marchează cel mai bun candidat pe rețea, cu numele lui în panou.
- **caption:** Persoane diferite, la fiecare apăsare. Poziția în structură prevalează asupra numărului de legături. Grad (`{{name:topDegree}}` = Octav, `{{stats.maxDegree}}` = 15 contacte). Timp petrecut (`{{name:topTime}}` = Denis — campion la prezență, dar într-o clasă aproape închisă: timpul lui nu scoate zvonul din clasă). Intermediere (puntea: prin cine trec drumurile dintre grupuri). Rază de răspândire (din simulare).

---

## Card #24 — diffusion game: „Concursul de viralitate"

- **type:** `diffusion` · **mode:** `game` · **id:** `s24-game` · **attempts:** 3
- **title:** Concursul de viralitate
- **intro:** Sarcina ta: alege sursa care duce zvonul la cei mai mulți. Trei încercări. Recordul posibil: `{{spreadRanking.max}}` (**67**).
- **Interacțiune:**
  - Tap pe nod → BFS deterministic din el, scor „N din 93 · recordul: 67"
  - 3 încercări; scoruri afișate: `#1: X · #2: Y · #3: Z`
  - După 3 încercări → buton „Clasamentul complet" → heatmap pe toată rețeaua (gradient gri → brun după `simulate.size`)
- **caption:** Aceeași optimizare o fac echipele de marketing, campaniile politice și operațiunile de dezinformare: nu „la câți ajung direct", ci „din cine se rostogolește". A ști cum se face e prima condiție ca s-o recunoști.

---

## Card #25 — diffusion sir (probabilistic, calibrat bimodal): „Modelul 2: oamenii nu sunt relee"

- **type:** `diffusion` · **mode:** `sir` · **id:** `s25-sir`
- **pTransmit:** 0.10 · **pStop:** 0.20 (calibrate empiric — vezi Note tehnice)
- **title:** Modelul 2: oamenii nu sunt relee
- **intro:** Pragul presupune transmitere garantată: cine aude, spune mai departe. Fals — oamenii uită, se plictisesc, se îndoiesc. Modelele serioase de zvon vin din epidemiologie: SIR (Kermack & McKendrick, 1927) și, pentru zvonuri, Daley–Kendall (1964), unde purtătorii se sting. La noi: transmiterea devine probabilitate.
- **Interacțiune:**
  - Buton „Rulează o dată" → animație SIR (fiecare purtător I încearcă să contamineze fiecare vecin S cu p=0,10; apoi fiecare purtător I trece în R cu p=0,20)
  - Buton „Rulează de 100 de ori" → nu animă, colectează 100 acoperiri finale, desenează histograma sub controale
  - Sursa: `shared.sourceId` dacă e setată, altfel default Octav
- **caption:** Un proces social nu are un viitor — are o distribuție de viitoruri. Întrebarea corectă nu e „ce se va întâmpla", ci „cu ce probabilitate". Cu p transmitere 0,1 și p stingere 0,2, rulările sunt bimodale: fie zvonul moare sub 5 elevi, fie ajunge la 45-60. Aproape nimic la mijloc.

---

## Card #26 — diffusion majority (interactiv, opțiunea B): „Iluzia majorității"

- **type:** `diffusion` · **mode:** `majority` · **id:** `s26-majority`
- **title:** Iluzia majorității
- **intro:** De ce l-au crezut toți atât de repede? Dacă zvonul e știut de câțiva elevi cu multe legături, un elev obișnuit vede o parte mare din vecinii lui știindu-l — și conchide că „toată lumea vorbește". Trage cursorul: alege câți elevi „știu" și vezi câți se simt înconjurați.
- **Interacțiune:**
  - Slider 1-20: câți dintre cei mai populari elevi „știu" zvonul; ei sunt marcați ca sursă
  - Contor live: „X% dintre elevi văd majoritatea prietenilor „știind" (deși doar K din 93 știu de fapt)"
  - Tap pe un elev non-sursă: „`nume`: N din M vecini știu zvonul (P%)"
- **Notă implementare (opțiunea B, aleasă de utilizator):** Cu 4 seed-uri de vârf iluzia iese 0% pe felia noastră (topologia nu o produce cu atât de puține seed-uri). Cardul e refăcut ca demo interactiv: elevul vede pragul la care se manifestă iluzia. Se stabilizează pe la 8-10 seed-uri.
- **caption:** O minoritate bine plasată produce percepția de majoritate (Lerman, Yan & Wu, 2016). Chiar și când o minoritate mică cunoaște ceva, dacă e formată din oameni bine conectați, o mare parte a rețelei se poate simți înconjurată de „ei toți știu". Același mecanism face opinii marginale să pară dominante în rețelele sociale.

---

## Card #27 — diffusion path: „Distanțe scurte"

- **type:** `diffusion` · **mode:** `path` · **id:** `s27-path`
- **title:** Distanțe scurte
- **intro:** Cât de departe sunt doi elevi oarecare? Atinge doi elevi din clase diferite.
- **Interacțiune:**
  - Primul tap: marchează sursa
  - Al doilea tap: rulează BFS între cele două, evidențiază drumul minim (noduri + muchii) și afișează lungimea + șirul de nume
  - Buton „Alegere nouă" → resetează
- **caption:** Drumul mediu pe componenta mare: `{{smallWorld.avgPath}}` (**3,0**) pași; cel mai lung drum minim: `{{smallWorld.diameter}}` (**6**). Experimentul scrisorilor al lui Milgram (1967) a găsit același lucru la scara unei țări: distanțele sociale sunt sistematic mai mici decât intuiția. Pentru un zvon, câteva trepte ajung.

---

## Card #28 — diffusion photo-film: „Fotografia și filmul"

- **type:** `diffusion` · **mode:** `photo-film` · **id:** `s28-photo-film`
- **title:** Fotografia și filmul
- **intro:** Iată rezultatul final al unei răspândiri: cine știe, cine nu. Poți identifica sursa doar din această imagine? Atinge nodul bănuit. Apoi: Derulează filmul.
- **hiddenSourceId:** implicit unul dintre spreaderii care ating componenta mare (Ana / Bianca / Bogdan — top 3 din `spreadRanking.champions`)
- **Interacțiune:**
  - Rețeaua e desenată în starea finală (toți cei atinși marcați ca „knows")
  - Tap pe nod „bănuit" (doar dintre cei care apar în starea finală) → marcaj + buton „Derulează filmul"
  - „Derulează filmul" animă BFS pas cu pas → la final: sursa reală se aprinde; verdict:
    - dacă a nimerit: „Ai nimerit. Sursa a fost X."
    - dacă nu: „Nu era Y — sursa a fost X. Din fotografie nu poți fi sigur."
- **caption:** Mai multe surse pot produce aceeași fotografie; doar ordinea în timp separă cauza de consecință. Nouă ne e ușor — deținem filmul complet. În cercetarea reală, despre epidemii sau dezinformare, observațiile sunt fragmente rare, iar identificarea sursei e o problemă deschisă. Datele fără timp descriu; pentru cauze, e nevoie de timp.

---

## Card #29 — text: „Verdictul: vinovatul depinde de definiție"

- **type:** `text` · **id:** `s29-verdict`
- **title:** Verdictul: vinovatul depinde de definiție
- **content:**
  > Patru măsuri, patru persoane. Campionul prezenței — irelevant prin izolare. Un elev cu 4 contacte — răspânditor de top prin poziție. Sursa — vizibilă doar în timp. Concluzia are un nume: operaționalizare. „Influența" nu există în date; apare când alegem cum s-o măsurăm, iar alegerea are consecințe — în cercetare, în presă, în deciziile platformelor. Ultima datorie a analistului: îndoiala față de propriile instrumente. Ne întoarcem la promisiunea de la muchie.

---

## Card #30 — diffusion compare-three: „Ce este un prieten? Trei măsurători"

- **type:** `diffusion` · **mode:** `compare-three` · **id:** `s30-compare-three`
- **data:** `data/highschool-three-networks.json`
- **title:** Ce este un prieten? Trei măsurători
- **intro:** Aceiași elevi au fost măsurați în trei moduri: senzori (proximitate fizică), chestionar (prietenie declarată), Facebook (legătură online). Trei rețele. Coincid?
- **Randare:** trei mini-rețele pe același set de noduri, în grilă responsivă (una sub alta pe mobil, alături pe desktop). Fiecare cu titlul sursei și contorul de legături. 8 elevi cu cel mai mare grad global marcați cu contur negru și label — apar identici în toate 3.
- **caption:** Nu. Pe elevii noștri: `{{threeNetworks.overlapSensorDeclared}}` (**43%**) suprapunere senzor–declarat, `{{threeNetworks.overlapSensorFacebook}}` (**26,3%**) senzor–Facebook; iar dintre prieteniile declarate, `{{threeNetworks.reciprocityPct}}` (**87%**) sunt declarate din ambele părți. Instrumentele computaționale înregistrează comportamentul — că doi oameni stau împreună; sensul relației — ce înseamnă ea pentru ei — rămâne accesibil interviului și chestionarului (Sato, 2024). Sociologia computațională și cea clasică nu sunt rivale: măsoară straturi diferite ale aceleiași realități, iar cercetarea bună le combină.

---

## Card #31 — diffusion recolor-sex: „Homofilia"

- **type:** `diffusion` · **mode:** `recolor-sex` · **id:** `s31-recolor-sex`
- **data:** `data/highschool-network.json`
- **title:** Homofilia
- **intro:** O ipoteză testabilă: elevii petrec mai mult timp cu colegi de același sex decât ar rezulta din amestec pur întâmplător?
- **Randare:** aceeași rețea de 93 noduri, dar recolorată pe sex — fete verde (`#3d7a52`), băieți brun (`#8b4a1e`), necunoscut gri. Legendă F/M/necunoscut sub grafic.
- **caption:** Rețeaua recolorată pe sex arată răspunsul vizual. Observat: `{{homophilySex.observedPct}}` (**74,7%**) din timpul de contact e între persoane de același sex. Așteptat la amestec întâmplător (dat 52 fete, 41 băieți): `{{homophilySex.expectedPct}}` (**50,2%**). Diferența are un nume: homofilie — similaritatea structurează legăturile: sex, clasă, pasiuni, mai târziu profesie și venit. Consecința serioasă: dacă legăturile urmează similaritatea, informația, oportunitățile și resursele circulă preferențial în interiorul grupurilor. Inegalitatea are o structură de rețea, nu doar cauze individuale.

---

## Card #31b — quiz add-on: „Homofilia, consecințe" (gating)

- **type:** `quiz` · **id:** `s31b-quiz-homofilie`
- **title:** Homofilia, consecințe
- **question:** Dacă elevii cu rezultate bune se împrietenesc preponderent între ei, ce se întâmplă cu informațiile utile despre admitere și facultăți?
- **options:** [0] „Se distribuie uniform" · [1] „Circulă preponderent în interiorul grupului lor" ← **corect** · [2] „Dispar" · [3] „Ajung mai repede la toți"
- **explanation:** Homofilia canalizează resursele, nu doar simpatiile — unul dintre mecanismele prin care avantajele se reproduc.

---

## Card #32 — text: „Etica măsurării"

- **type:** `text` · **id:** `s32-etica`
- **title:** Etica măsurării
- **content:**
  > Datele sunt anonimizate. Suficient? „Elevul cu `{{stats.maxDegree}}` (**15**) contacte, punte între două clase" poate fi identificabil în școala lui fără niciun nume: când poziția e unică, structura te dă de gol la fel de bine ca identitatea. Re-identificarea prin structură e un risc documentat — de aceea cercetarea serioasă adaugă consimțământ, agregare, acces controlat. Și simetria care trebuie spusă direct: instrumentele din această lecție sunt cu dublă utilizare. Aceleași calcule găsesc nodul optim pentru o campanie de vaccinare sau pentru una de dezinformare. Competența tehnică fără judecată despre folosire e exact ce reproșăm algoritmilor.

---

## Card #33 — text: „Ce ai făcut, de fapt"

- **type:** `text` · **id:** `s33-ce-ai-facut`
- **title:** Ce ai făcut, de fapt
- **content:**
  > Ai transformat 180.000 de înregistrări într-o structură analizabilă. Ai construit o histogramă treaptă cu treaptă și ai văzut cum lățimea intervalului îi schimbă înfățișarea. Ai despărțit media de median și știi când diverg. Ai testat o intuiție personală contra datelor și ai pierdut — din motive de eșantionare, nu de psihologie. Ai comparat grupuri prin frecvențe, medii și variație internă. Ai rulat un proces social de o sută de ori și ai citit distribuția rezultatelor. Ai văzut că trei instrumente de măsură produc trei versiuni ale „prieteniei". Asta nu a fost o lecție despre rețele. A fost metoda: cum devine viața socială date, ce se câștigă, ce se pierde, cine decide definițiile.

---

## Card #34 — text: „Domeniul"

- **type:** `text` · **id:** `s34-domeniul`
- **title:** Domeniul
- **content:**
  > Sociologia computațională stă la intersecția sociologiei cu știința datelor. Se practică în cercetare, politici publice, sănătate publică, planificare urbană, jurnalism de date, etica algoritmilor. Se studiază la Amsterdam, Dublin, Berkeley, Linköping, Koç — și programe în formare în România. Ce ai parcurs azi e, la scară redusă și cu date publice, chiar fluxul de lucru al domeniului.

---

## Card #35 — quizset: „Proba analistului" (3 întrebări, gating pe toate)

- **type:** `quizset` · **id:** `s35-proba`
- **title:** Proba analistului
- **intro:** Trei întrebări care condensează întreaga lecție. Răspunde la toate.
- **questions:**
  1. **Q1:** Un articol anunță că venitul mediu a crescut cu 10%. Ce verifici înainte de orice concluzie?
     - options: [0] „Ce a făcut medianul, între timp" ← **corect** · [1] „Cine a scris articolul" · [2] „Dacă e vară sau iarnă" · [3] „Câte pagini are raportul"
     - explanation: Media e sensibilă la vârf; medianul spune ce s-a întâmplat cu omul din mijloc. Fără el, „media a crescut" poate ascunde că majoritatea stagnează.
  2. **Q2:** În feedul tău, „toată lumea" susține o poziție. Ce știi acum despre această impresie?
     - options: [0] „Poziția e cu adevărat majoritară" · [1] „Feedul e un eșantion deformat; o minoritate bine plasată poate părea majoritate" ← **corect** · [2] „Algoritmul e stricat" · [3] „Nu poți spune nimic"
     - explanation: Paradoxul prieteniei și iluzia majorității produc împreună exact acest efect. Vezi în special cei populari; și vezi „toți vecinii mei știu" chiar când doar câțiva știu.
  3. **Q3:** Vrei ca o informație corectă să ajungă în toate grupurile unei comunități. După ce criteriu alegi primii oameni cărora le-o dai?
     - options: [0] „Cel mai popular" · [1] „Cel care petrece cel mai mult timp cu ceilalți" · [2] „Cel care leagă grupuri diferite (intermediere / punte)" ← **corect** · [3] „Aleatoriu"
     - explanation: Poziția de punte, nu numărul de contacte. Un popular în interiorul unui grup rămâne în grupul lui. O punte trece.
- **Gating:** „Continuă" blocat până când toate 3 sunt răspunse. Fiecare sub-quiz persistat separat sub id `s35-proba-0`, `s35-proba-1`, `s35-proba-2`.

---

## Card #36 — conclusion: „Caz închis"

- **type:** `conclusion` · **id:** `s36-caz-inchis`
- **title:** Caz închis
- **content:**
  > Ancheta s-a bazat pe datele reale ale unui liceu din Marsilia, colectate și publicate de SocioPatterns. Citare: R. Mastrandrea, J. Fournet, A. Barrat, „Contact patterns in a high school", *PLoS ONE* 10(9), e0136497 (2015). Zvonul a fost construit de noi; școala, oamenii și întâlnirile sunt reale. Ediția următoare: aceeași anchetă, cu clasa voastră ca noduri vii.
- **La atingere:** `markLessonCompleted("highschool")`. Butonul „Continuă" devine „Înapoi la curs".

---

## Note tehnice tranșa 2

### Câmpuri statistici obținute din date (`highschool-stats.json`)

| câmp | valoare | folosit în |
|---|---|---|
| `meanDegree` | **5,4** | #19 |
| `medianDegree` | **5** | #19 |
| `maxDegree` | **15** | #16, #32 |
| `friendshipParadox.meanDegree` | **5,4** | #20 |
| `friendshipParadox.meanFriendDegree` | **6,7** | #20 |
| `friendshipParadox.pctBelow` | **75** | #20 |
| `topByDegree[0].name` | **Octav** (id 177, 2BIO1) | #16, #22, #23 |
| `topByWeighted[0].name` | **Denis** (id 513, MP*1) | #23 |
| `classContactSplit.globalBetweenPct` | **1,9** | #14 |
| `classFreq.2BIO1` | 35 elevi (27F, 8M) | #12 |
| `classFreq.2BIO2` | 32 elevi (19F, 13M) | #12 |
| `classFreq.MP*1` | 26 elevi (6F, 20M) | #12 |
| `classMeanDegree.*` | 5,2 · 6,6 · 4,2 | #13 |
| `edgeCountByThreshold` | 493 / 326 / 250 / 218 / 197 / 178 / 153 / 136 / 126 / 119 (prag 1..10) | #11 (context) |
| `spreadRanking.max` | **67** | #24 |
| `spreadRanking.champions[0].name` | Ana | #28 (default `hiddenSourceId`) |
| `smallWorld.avgPath` | **3,0** | #27 |
| `smallWorld.diameter` | **6** | #27 |
| `homophilySex.observedPct` | **74,7** | #31 |
| `homophilySex.expectedPct` | **50,2** | #31 |
| `homophilySex.nF` / `nM` | 52 / 41 | #31 |
| `majorityIllusion.pctSeeMajority` | 0,0 (cu 4 seed-uri de vârf) | #26 explanation |
| `threeNetworks.overlapSensorDeclared` | **43,0** | #30 |
| `threeNetworks.overlapSensorFacebook` | **26,3** | #30 |
| `threeNetworks.overlapDeclaredFacebook` | 17,4 | (nefolosit direct) |
| `threeNetworks.reciprocityPct` | **87,0** (prietenie declarată) | #30 |
| `threeNetworks.diariesReciprocityPct` | 66,7 (jurnal) | (referință) |
| `threeNetworks.sensorPairs` / `.diariesPairs` / `.friendshipPairs` / `.facebookPairs` | 250 / 86 / 52 / 137 | #30 (contoare) |
| `threeNetworks.nodesInSensor` / `.nodesInDiaries` / `.nodesInFriendship` / `.nodesInFacebook` | 93 / 82 / 74 / 71 | (info) |

### Câmpuri suplimentare relevante

- `hoursCount = 5` — snapshoturi orare disponibile pentru `#21`.
- `friendship_reciprocity = 87%` este suprinzător de mare — indica calitate ridicată a chestionarului.
- `overlap_sensor_diaries = 43%` — 43% din perechile din jurnal (declarat) apar și la senzor. Text #30 se sprijină pe această divergență și e valid.

### Calibrare SIR (Card #25)

- Grid: `p_transmit ∈ [0.10, 0.30]`, `p_stop ∈ [0.15, 0.40]`, 200 rulări per punct, sursă = Octav.
- Cea mai bimodală distribuție: **p_transmit = 0,10, p_stop = 0,20**.
- Statistici la parametrii aleși: media 43,4 · std 17,2 · 11% mor sub 5 elevi · 85% ajung peste 30 elevi.
- Distribuție ilustrativă (bin 5):
  ```
  [ 0-4]   22  ####################
  [ 5-9]    2  #
  [10-14]   3  ##
  [15-19]   0
  [20-24]   2  #
  [25-29]   1
  [30-34]   1
  [35-39]  10  ########
  [40-44]  17  ##############
  [45-49]  42  ###################################
  [50-54]  59  ####################################################
  [55-59]  34  ############################
  [60-64]   7  #####
  ```
- Poanta cardului („un proces social nu are un viitor — are o distribuție de viitoruri") funcționează perfect: gol clar la mijloc, două moduri.

### Iluzia majorității (Card #26) — decizie de proiectare

Cu seed = top 4 după grad, `pctSeeMajority = 0,0` pe felia noastră. Utilizatorul a ales opțiunea **B**: cardul devine demo interactiv. Slider 1-20; utilizatorul vede pragul la care iluzia apare. Empiric, pe felia noastră procentul pornește de la 0% la 4 seed-uri și crește peste 30% în jur de 10-12 seed-uri. Slot de tap adăugat pentru „ce văd vecinii tăi".

### Componente noi implementate în tranșa 2

- **`diffusion.js`** — 8 moduri noi: `temporal`, `sir` (probabilistic + outcome histogram), `game` (3 încercări + heatmap), `majority` (interactiv), `path` (BFS între două noduri), `photo-film` (ghicit sursă + film + verdict), `compare-three` (grilă 3 rețele pe același set de noduri), `recolor-sex` (paletă F/M/necunoscut + legendă). Export nou `setShared({sourceId, threshold})` pentru sincronizare cross-card.
- **`slides.js`** — bloc `quizset` (2-3 quiz-uri secvențiale cu gating unic pe toate); wire `code-diffuz` (a treia instanță code cu Pyodide).
- **`css/slides.css`** — `.quizset`, `.compare-three` (grid responsiv).

### Componente rămase de la tranșa 1 (neschimbate)

- `charts.js` — 6 variante (`dots`, `strip`, `freq`, `grouped-strip`, `stacked`, `meanmedian`) + `histogram` (cu / fără slider) + `bars`.
- `code-runner.js` — `renderCodeRunner` (clasic) + `renderCodeInteractive` (context Python + result → callback).
- `pyodide-worker.js` — acceptă `context` (Python globals).
- `quiz.js` — `renderQuiz` + `renderVote` (persistat separat).
- `visualizations.js` — `renderNetwork` cu suport `inlineData`; mini-network arată gradul la tap.
- `progress.js` — `markVote` / `getVote`.
- `build_network.py` — scrie `classFreq`, `classMeanDegree`, `classContactSplit`, `interClassPct`, `majorityIllusion`, `smallWorld`, `homophilySex`, `spreadRanking`, `edgeCountByThreshold`; fișiere auxiliare `highschool-hours.json`, `highschool-pairs.json`, `highschool-three-networks.json`.

### Cache-busting

`?v=20260721c` pe toate HTML-urile (index.html, lesson.html, course.html). Bumpează la orice modificare a componentelor JS/CSS.

---

## Convenție de actualizare (neschimbată)

1. Actualizează linia **Ultima actualizare** de sus la orice modificare.
2. Numerele `Card #XX` sunt stabile. Adăugările între carduri primesc sufix literal (`#19b`, `#31b`).
3. La modificarea unui card, rescrie complet secțiunea lui în acest document, cu textul integral.
4. Dacă rerulezi `data/build_network.py` și cifrele se schimbă, actualizează secțiunea **Note tehnice** + toate textele din carduri care conțin cifre.
5. Fișiere de date curente: `highschool-network.json`, `highschool-stats.json`, `mini-network.json`, `highschool-hours.json`, `highschool-pairs.json`, `highschool-three-networks.json`.
