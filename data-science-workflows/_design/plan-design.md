# Plan de design: infrastructura de predare

Stare: a treia versiune, octombrie 2026. Nimic din ce e aici nu e implementat încă.
Documentul are patru părți: ce e în neregulă acum, ce model propun, cum arată, și
în ce ordine s-ar face. Perechea lui vizuală e `propunere.html`, unde fiecare
lucru de mai jos e desenat, nu descris.

Față de prima versiune s-au schimbat trei lucruri, pentru că prima dată le
nimerisem greșit:

- **Panoul live** are acum și cifra globală pe slide-ul curent (cerc), și tabelul
  cu fiecare student. Amândouă deodată, pe același ecran, nu una după alta.
- **Progresul pe GitHub** e un instantaneu datat, nu un flux. Se reîmprospătează
  când rulezi scriptul, exact ca la cursul de AI engineering.
- **Paleta** e cea caldă din TranscriptionLab, nu albastrul-oțel de acum.

A treia versiune adaugă intrarea în oră și grupa ca obiect, și pune în text
deciziile luate: ședința se leagă de grupă și de lecție, reluarea e liberă dar
nota o dă prima încercare, prezența vine din activitate, iar ștergerea unei
ședințe o arhivează.

---

## Partea I. Audit

### Diagnosticul de fond

Situl încearcă să fie trei produse purtând o singură haină:

1. **Produsul studentului.** Lecția, manualul, contul, progresul lui.
2. **Instrumentul de predare.** Conducerea orei, camera, ce fac ei acum.
3. **Registrul profesorului.** Note, prezențe, loguri, exporturi.

Acum al doilea și al treilea sunt construite ca *adăugiri peste primul*. Panoul e
o pagină în plus lângă contul de student, nu un produs cu logica lui. De aici vin
aproape toate lucrurile care te-au deranjat, inclusiv „Progresul meu" pe pagina
cursului, când tu predai, nu parcurgi.

### Obiectul care lipsește: ședința

Asta e piesa centrală, și explică de ce nu se poate face nimic din ce ai cerut
(marcarea zilei, închiderea, statisticile pe acea zi, ștergerea logului, exportul).

Ce există acum în bază:

| Tabel | Cheie | Problema |
|---|---|---|
| `ritm` | `capitol` | O singură stare „live" per lecție, fără istoric. Nu se poate închide, pentru că nu e nimic de închis. |
| `prezente` | `(user_id, curs)` | O singură prezență per student per curs, **vreodată**. Nu poți ține aceeași lecție de două ori, nici anul viitor. |
| `sesiuni` | `user_id` | Numele înșală: e sesiunea de browser a studentului, nu ședința de curs. |
| `raspunsuri`, `rulari_cod` | `creat_la`, `context` | Au o oră, dar nu aparțin nimănui. „Ce s-a întâmplat marți" se poate obține doar ghicind după interval orar. |

**Nu există nicăieri un obiect care să însemne „ora de marți, 14 octombrie,
grupa 1, lecția 3".** Fără el, „adună statisticile pe ziua aia" nu are subiect.

### Pe ecrane

**Pagina cursului.** Îți arată ție „Progresul meu" și „Cum se pune nota". Sunt
corecte pentru student, absurde pentru tine. Antetul e identic pentru amândoi, cu
un singur buton în plus.

**Contul.** O pagină cu patru stări foarte diferite (neautentificat, fără
matricol, student, profesor) înghesuite în același fișier. Pentru profesor,
jumătate din ea nu are sens și cealaltă jumătate redirecționează imediat. Nota,
Lecțiile, Ce ai lucrat, Resetare: toate sunt despre un student.

**Panoul.** Două pagini (`panou/` și `panou/statistici/`) care împart aceeași
muncă fără o linie clară între ele. Statisticile au șase file: *Cine ce a făcut,
Prezența, Slide cu slide, Codul scris, Ce au scris, Nota*. Șase file înseamnă
șase feluri de a nu găsi ce cauți. Nicăieri nu scrie **ce zi e** sau **ce
ședință**, pentru că nu există conceptul.

**Lecția live.** Funcționează, dar starea e ambiguă. Un student nu poate spune cu
certitudine dacă e „prins" în ora ta sau liber, iar tu nu poți spune dacă cineva
e offline sau doar nu a mai dat refresh.

### Ce lipsește cu totul

- Închiderea unei ore și raportul ei.
- Export (CSV) al oricărui lucru.
- Ștergerea unui log, când a fost o repetiție sau o ședință ratată.
- Starea „a trimis, dar nu a completat".
- Legătura către depozitul echipei și progresul ei.

---

## Partea II. Modelul propus

### 1. Ședința, obiectul central

```
grupe
  id            text        -- 'g1'
  curs          text        -- 'dsw-2026'
  nume          text        -- 'Grupa 1'
  zi            text        -- 'marți'
  ora           text        -- '10:00'
  an            text        -- '2026'

sedinte
  id            uuid
  capitol       text        -- 'c3'
  grupa_id      text        -- 'g1'; null = toate grupele
  titlu         text        -- 'Cursul 3, grupa 1'
  mod           text        -- 'live' | 'propriu'
  cod           text        -- 'K7MQ2X', doar cât e deschisă
  deschisa_la   timestamptz
  inchisa_la    timestamptz -- null = în desfășurare
  slide_nr      int         -- unde ești acum
  note          text        -- ce ai scris tu despre ora asta
```

Apoi, **o singură coloană adăugată** la ce există deja:

```
raspunsuri.sedinta_id    uuid null
rulari_cod.sedinta_id    uuid null
prezente.sedinta_id      uuid not null   -- și cheia devine (user_id, sedinta_id)
evenimente.sedinta_id    uuid null
```

`null` înseamnă „a lucrat singur, în afara orei". Asta înlocuiește coloana
`context` cu ceva verificabil: nu mai e o etichetă pe care o scrie clientul, e o
legătură.

**Ce deblochează, imediat:**

| Ce ai cerut | Cum iese |
|---|---|
| Marchezi ziua | Deschizi o ședință. Data e în `deschisa_la`. |
| Închizi ora | `inchisa_la = now()`. Codul moare. |
| Statisticile zilei | Tot ce are `sedinta_id = X`. |
| Ștergi logul | `delete from sedinte where id = X`, în cascadă. |
| Export | Un CSV per ședință, sau unul pe tot semestrul. |
| Aceeași lecție de două ori | Două ședințe. Rezolvă și bug-ul de prezență. |
| Anul viitor | Alte ședințe. Nimic de curățat manual. |

Grupa e acum o coloană de text pe `studenti`, scrisă de mână. Devine un rând cu
ziua și ora ei, ca ședința să se deschidă dintr-un clic („Marți 10:00, grupa 1"
apare pe buton, nu îl scrii de fiecare dată), ca ecranul de intrare să arate
exact oamenii din grupa aia, și ca anul viitor să fie altă grupă, nu aceiași
studenți suprascriși.

### 2. Intrarea în oră

Codul de intrare există deja: `jetoane_prezenta`, șase semne din care lipsesc
O/0 și I/1/L tocmai ca să nu se citească greșit de pe proiector, cu expirare.
Ce lipsește e legătura cu ședința și cu grupa.

Odată legat, apare consecința bună: **codul duce contextul, iar studentul duce
doar numele lui.** Nimeni nu alege grupa dintr-o listă, deci nimeni nu o alege
greșit. QR-ul de pe proiector, codul tastat și linkul pus pe Teams duc toate în
același loc, `/intra/?c=K7MQ2X`.

**Prima dată.** După autentificare (GitHub sau invitat, amândouă există deja),
ecranul arată lista grupei: cei 21 de oameni, nimic altceva. Un tap. Fără
matricol de tastat, fără grupă de ales, fără formular. Ultimele trei cifre din
matricol apar doar ca să deosebești doi oameni cu același nume. Cine nu e în
listă (venit mai târziu, transferat) apasă „nu mă găsesc" și ajunge într-o
căsuță pe care o aprobi tu, nu direct în date.

**După aceea.** Te știe. „Bine ai revenit, Bogdan. Intri în Cursul 3, grupa 1."
Un buton.

#### GitHub: o ușă, nu un câmp

Întrebarea era dacă să le ceri contul de GitHub în formularul de la început.
Nu, și nici mai târziu ca text scris de ei, pentru că „GitHub" înseamnă două
lucruri diferite la două momente diferite:

| | Când | Cum |
|---|---|---|
| **Ușă de intrare** | Ziua întâi | Butonul „Intru cu GitHub" există deja. Cine are cont intră cu el, și numele de utilizator vine verificat, din jeton. Cine nu are, intră ca invitat. |
| **Identitate pentru echipă** | Cursul 3 | Numele de utilizator îți trebuie abia când faci depozitele. Cursul 3 e chiar lecția de Git: „fă-ți cont și leagă-l" nu e birocrație acolo, e primul exercițiu din lecție. |

Un câmp de text liber ar produce profiluri `github.com/x` în loc de `x`, conturi
vechi pe care le abandonează, litere lipsă, și „fac mai târziu". Prin
autentificare, numele vine corect sau nu vine deloc.

Între cursul 1 și cursul 3, un singur rând în contul lor, care nu ceartă pe
nimeni: „GitHub: nelegat, îl legi la cursul 3". Și o singură cifră în panoul
tău: „14 din 21 au contul legat", cu lista celor care nu.

#### Prezența, din activitate

Regula e a ta și e corectă: cine n-a completat nimic nu e prezent. Ca s-o poți
vedea, scanarea și prezența devin două stări diferite, cu una între ele:

| Stare | Ce înseamnă | Ce faci cu ea |
|---|---|---|
| `intrat` | a scanat, n-a trimis nimic | e în sală, sau măcar telefonul lui; nu e prezență |
| `intrat, inactiv` | a scanat, și de 20 de minute nimic | rândul de care ai nevoie în timpul orei: un nume, o întrebare |
| `prezent` | a trimis cel puțin o sarcină | prezența, calculată singură la închiderea ședinței |

Două fire de prins. Pragul e *o trimitere*, nu *o trimitere corectă*: cine a
încercat și a greșit a fost acolo, altfel prezența ajunge să măsoare
performanța. Și la închidere poți răsturna o prezență cu un clic, pentru că
uneori moare bateria, iar regula automată n-are cum să știe. Calculată automat,
corectabilă manual, cu urmă în raport că ai corectat-o.

### 3. Cele două moduri

Modelul e cel din Nearpod, care are exact distincția pe care o vrei: sesiune
sincronă condusă de profesor, și sesiune în ritm propriu, iar **fiecare sesiune
lansată produce un raport**.

**Live (condusă de mine)**
- Slide-ul lor = slide-ul meu. Butoanele înainte/înapoi nu există pentru ei.
- Pot deschide manualul într-un alt tab, oricând. Ce fac acolo se înregistrează
  separat și nu se notează.
- Când trimit un răspuns, **văd imediat dacă e bun**. Asta lipsește acum.
- Când trec eu mai departe, ce e în lucru se trimite automat, așa cum e.

**În ritm propriu**
- Merg singuri, porțile funcționează ca acum.
- Eu văd unde e fiecare, în timp real, dar nu îi mut.
- Util pentru laborator și pentru recuperări.

Modul stă pe ședință, nu global. Poți ține cursul 3 live cu grupa 1 și în ritm
propriu cu grupa 2, în aceeași zi.

### 4. Patru stări pentru o sarcină, nu două

Acum `rulari_cod.trecut` e boolean, iar porțile se deschid doar la reușită. Un
student care trimite necompletat e invizibil. Propun:

| Stare | Glif | Când | La notă |
|---|---|---|---|
| `trecut` | bifă plină | a completat corect | punct |
| `trimis_gresit` | x plin | a completat, dar greșit | zero, dar a încercat |
| `trimis_gol` | cerc cu punct | a apăsat Verifică fără să completeze | zero |
| `nefacut` | cerc gol | nu a atins sarcina | zero |

Pentru notă, ultimele trei sunt la fel. Dar pentru tine, în timpul orei,
diferența e tot: `trimis_gresit` înseamnă „a înțeles greșit, vorbim acum",
`trimis_gol` înseamnă „e blocat sau se grăbește", `nefacut` înseamnă „nu e
acolo". Trei conversații diferite.

**Forma poartă informația, culoarea doar o întărește.** Cele patru glife se
deosebesc între ele și pe un proiector decolorat, și alb-negru, și pentru un
daltonist. Culoarea e al doilea semn, niciodată singurul.

#### Reluarea: o dată se notează, după aceea e al lor

Regula ta, și partea bună e că nu cere niciun tabel nou: răspunsurile se
păstrează oricum toate, cu ora lor. Se schimbă doar care dintre ele se citește
la notă.

| Încercarea | Ce se întâmplă cu ea | Ce vede studentul |
|---|---|---|
| Prima completată | se notează, rămâne așa | „Nota ta la sarcina asta: corect." |
| Trimiterea automată goală | se vede în panou și în raport, dar nu îngheață nota | „N-ai apucat. Poți relua." |
| Reluările, în ritm propriu | oricâte, nu schimbă nota | „Ai refăcut de 3 ori, ultima corect." |

Rândul al treilea e cel care face sistemul sănătos: un student care a greșit la
oră și a refăcut acasă până i-a ieșit are scris pe ecran că i-a ieșit, chiar
dacă nota a rămas cea de la prima încercare. Nota măsoară ora, linia de dedesubt
măsoară dacă au învățat, iar pentru tine sunt două coloane diferite în raport.

**O contradicție de rezolvat înainte de cod.** Dacă prima încercare e cea notată
*și* la schimbarea slide-ului se trimite automat ce e în lucru, atunci un
student mai lent primește un „trimis gol" ca primă încercare și rămâne cu zero,
deși știa. Propunerea mea: **încercarea notată e prima încercare completată.**
Trimiterile automate goale se înregistrează și se văd, dar nu îngheață nota.
Altfel regula de auto-trimitere pedepsește exact oamenii pe care vrei să-i
prinzi din urmă.

### 5. Două produse, nu unul cu un buton în plus

**Produsul tău (profesor).** Rădăcină proprie, antet propriu, fără nimic din
limbajul studentului. Trei locuri, atât:

```
/predau                  Astăzi: ce urmează, pornește ora, ultima ședință
/predau/ora              Ora în desfășurare: camera + comanda
/predau/clasa            Semestrul: note, prezențe, echipe, exporturi
```

Nicăieri „Contul meu", „Progresul meu", „Nota mea".

**Produsul studentului.** Rămâne ce e, curățat:

```
/                        Cursul
/cN-.../lectie           Lecția
/cN-.../tutorial         Manualul
/cont                    Al meu: progres, notă, echipa mea
```

Antetul își schimbă conținutul după rol, nu doar adaugă un buton.

### 6. Ora, pe două ecrane

Separare clară, pentru că fac lucruri diferite:

- **Proiector.** Doar slide-ul. Curat, mare, fără cifre. Banda de sus: codul de
  intrare și câți sunt în clasă. Atât.
- **Laptop.** Comanda: panoul live de mai jos, plus butoanele (înainte, înapoi,
  închide ora).

Acum ai „Pe alt ecran", dar ambele arată cam același lucru. Trebuie să fie două
vederi diferite ale aceleiași ședințe.

### 7. Panoul live, pe slide-ul curent

Asta e piesa pe care prima versiune a ratat-o. Panoul nu e „progresul general al
clasei". E **slide-ul de pe ecran, chiar acum**, și arată două lucruri deodată:

**Stânga: cifra globală, ca la Nearpod.** Un cerc (inel), cu numărul mare în
mijloc și „din 18 au trimis" sub el. Inelul e tăiat în cele patru stări, cu
legenda și numărătoarea sub el:

```
         ╭─────────╮          ✓  corect        8
        │    11     │         ✕  greșit        3
        │ din 18 au │         ◉  trimis gol    2
         ╰─────────╯          ○  n-a trimis    5
```

Răspunde dintr-o privire, de la doi metri, la singura întrebare care contează
când stai în fața clasei: **pot merge mai departe?**

**Dreapta: tabelul, cine ce a făcut.** Patru coloane:

| Student | Acest slide | Ce a ales | Toată ora |
|---|---|---|---|
| Andreea Pop | ✓ | `fetch și merge` | ▓▓▓▓▓░░ 7/9 |
| Bogdan Ilie | ✕ | `add și commit` | ▓▓▓░░░░ 4/9 |
| Carmen Radu | ◉ | *trimis fără răspuns* | ▓▓░░░░░ 2/9 |
| Dan Marin | ○ | — | ▓░░░░░░ 1/9 |

Coloana **„ce a ales"** e cea care își merită locul: nu-ți spune doar *că* au
greșit, ci *ce* au greșit. Dacă trei au ales aceeași variantă falsă, aia e
următoarea ta propoziție. Fără ea, tabelul e doar o listă de bife.

Sub tabel, o singură linie de atenționare: **blocații acum** — cine stă pe
același slide de prea mult timp, cine a trimis gol de mai multe ori la rând.
Nimic altceva; panoul nu e un raport, e o unealtă pentru următoarele 30 de
secunde.

Sortarea se schimbă după ce cauți: după stare pe slide (vezi grupul blocat),
după nume (cauți pe cineva anume), după cât a făcut în toată ora (vezi cine
rămâne în urmă de la început).

### 8. Raportul de ședință

Când închizi ora, se generează și rămâne:

```
Cursul 3, grupa 1 · marți, 14 octombrie, 10:02 - 11:38 (96 min)

  18 din 21 prezenți
  14 sarcini parcurse din 23
  La ce s-a împotmolit grupa: slide 9 (doar 6 din 18 au trecut)
  3 texte scrise de ei

  [Export CSV]  [Arhivează]  [Notițele mele]
```

Lista ședințelor e istoricul cursului. Asta e „să văd ce s-a întâmplat în acea
zi", și e și singurul loc de unde se șterge ceva.

#### Ștergerea, cu plasă dedesubt

Ai ales arhivarea pe un număr de zile, și e varianta bună: o repetiție sau o
ședință deschisă din greșeală trebuie să dispară din listă imediat, dar nu din
existență imediat.

1. **Arhivezi.** Ședința iese din listă și din toate statisticile, în aceeași
   secundă. Butonul nu cere confirmare, pentru că nu e distructiv.
2. **Stă 30 de zile.** Într-o listă separată, „Arhivate", cu zilele rămase
   scrise pe fiecare rând. Un clic o aduce înapoi, întreagă.
3. **Se șterge singură.** După termen, definitiv, cu tot ce atârnă de ea. Sau
   mai devreme, din arhivă, cu o confirmare adevărată.

Treizeci de zile e o propunere, nu o lege: se schimbă într-un singur loc.
Important e că singurul buton pe care îl apeși în grabă, la sfârșitul orei, e
cel care *nu* distruge nimic.

### 9. Echipele pe GitHub: un instantaneu, nu un flux

Aici am scris confuz prima dată, și merită spus limpede: **progresul pe GitHub nu
e live și nici nu trebuie să fie.** E o fotografie, făcută când rulezi scriptul.

Exact ca la cursul de AI engineering, care face lucrul ăsta corect: pagina
`ai-engineering/progress/` citește un `progress.json` comis în depozit, iar în
antet scrie `Actualizat: 2026-06-22 23:38`. Toată lumea știe la ce se uită.
Nicăieri nu pretinde că e în timp real, și de aceea nimeni nu e dezamăgit când
nu e.

Portez același model: un `progres/echipe.json` generat de un script, cu echipe,
depozite, milestones pe lecție, issues închise și deschise, membri, commit-uri și
blocaje.

**Constrângerea, spusă pe față:** un browser nu poate citi API-ul GitHub pentru
depozite private fără token, iar un token nu are ce căuta într-un depozit public.
Deci: script local, commit la JSON, pagina îl citește. Butonul „Reîmprospătează"
din interfață înseamnă „rulează scriptul și fă un commit", nu o cerere din
pagină. Nu e o limitare a designului, e o condiție de securitate.

**Ce preiau de la AI engineering, dincolo de mecanism:**

- Data actualizării în antet, nu îngropată în subsol.
- Rapoarte, nu numere singure: `485/509`, `31/31`, nu `485` și `31`.
- O propoziție scrisă care rezumă starea, generată din cifre („C2 Models este
  etapa curentă; backlog-ul cel mai mare este în C6 cu 7 task-uri deschise").
- O bară de etape C1…C9 pentru fiecare echipă, pe același rând cu numele ei.
- O singură **acțiune** numită, nu o listă de recomandări.

- **Studentul** vede, în contul lui: cardul echipei sale, linkul către depozit,
  cât s-a închis din milestone-ul lecției curente, ce issue-uri are el deschise.
- **Tu** vezi, în `/predau/clasa`: toate echipele, una lângă alta, cu procentele
  pe etape și lista blocajelor (issue-uri fără mișcare de X zile).

---

## Partea III. Designul vizual

### Paleta: caldă, și verificată

Situl e acum pe un albastru-oțel rece, cu neutre reci. Trecerea e la o familie
caldă, luată direct din captura TranscriptionLab: hârtia bate în cremă, grijile
bat în măsliniu, accentul e salvie. Aceeași structură, altă temperatură. Vizual,
cursul încetează să semene cu un tablou de bord corporativ și începe să semene cu
un caiet.

**Luate din captură, fără schimbări:**

| Rol | Închis | Deschis |
|---|---|---|
| Fundal | `#292921` | `#F7F6F1` |
| Pânză (carduri) | `#31312A` | `#FFFFFF` |
| Accent (salvie) | `#8DAE9F` | `#0E7A6E` |
| Text | `#E9E7E0` | `#23231A` |
| Text secundar | `#A9A79D` | `#5A594E` |
| Linii | `#4D4D44` | `#E2E0D7` |

Butonul verde din captură are **scris închis pe umplere deschisă**, nu alb pe
verde. Raportul de contrast iese 6,55:1, mult peste prag, și arată mai cald decât
orice buton alb-pe-culoare. E regula pentru acțiunea principală din tot situl.

**Culorile de stare, și de ce nu verde și roșu.** „Corect" și „greșit" sunt exact
locul unde verdele și roșul n-au voie să fie singura diferență: e perechea pe
care n-o deosebește cel mai frecvent tip de daltonism. Am verificat cu un
validator, nu din ochi: verde-roșu dă o separare de 6,2 pentru deuteranopie, sub
prag. Teal și teracotă dau 11,1, iar în temă închisă 10,5.

| Stare | Deschis | Închis |
|---|---|---|
| Trecut | `#0E8A7A` | `#35A89A` |
| Greșit | `#AB3E24` | `#D4664E` |

Amândouă trec toate cele cinci verificări: bandă de luminozitate, saturație
minimă, separare pentru daltonism, separare pentru vedere normală, și contrast
față de fundal. Și, ca mai sus: forma glifului rămâne primul semn, culoarea al
doilea.

### Regulile pe care le propun

1. **O pagină, o treabă.** Dacă o pagină are patru stări, sunt patru pagini.
2. **O singură acțiune principală, vizibilă.** Pe `/predau`, aceea e „Pornește
   ora". Restul sunt secundare și arată secundar.
3. **Filele se folosesc pentru vederi ale aceluiași lucru, nu ca sertare.** Cele
   șase file din statistici devin un tabel cu filtre, plus o vedere „azi".
4. **Starea se scrie, nu se deduce.** O bandă permanentă care spune exact: ora e
   deschisă sau nu, în ce mod, de când, câți sunt.
5. **Cifrele capătă context.** „14" nu înseamnă nimic. „14 din 21" înseamnă.
6. **Nimic nu se ascunde sub un clic dacă încape pe ecran.** Lecția 1 a arătat
   cât costă asta.

### Ce se schimbă concret

| Acum | Propus |
|---|---|
| Antet identic, cu un buton „Panou" | Antet după rol: student vede cursul, tu vezi „Predau" |
| `/cont` cu patru stări | `/intra` (autentificare), `/cont` (doar student) |
| `panou/` + `panou/statistici/` | `/predau` (azi), `/predau/ora`, `/predau/clasa` |
| Șase file de statistici | Un tabel, filtre, și o vedere separată pentru ora în curs |
| „Predai acum" ca bandă verde | Bandă de stare permanentă, cu ședința și cronometrul |
| Fără istoric | Lista ședințelor, cu raport, export și ștergere |

### Mărunțișurile care se adună

Lucruri de câteva minute fiecare, dar împreună fac diferența dintre „merge" și
„e făcut cu grijă". Lista completă, cu machete, e în `propunere.html`, secțiunea 08.

| Ce e acum | Ce propun |
|---|---|
| Opt linkuri „Caietul lecției" trimit către fișiere `.ipynb` inexistente; `surse-de-date.html` e linkat din toate lecțiile și din pagina cursului, dar nu e în depozit | Ori le facem, ori le ascundem până există. Un link mort în lecția 1 strică încrederea în tot restul. |
| Un link extern (Eurostat) arată la fel ca unul intern | Un indicator mic de „pleacă din sit", în temă închisă sau apăsată |
| „Cod 12", „Verificări 31", „Prezențe 3" — cifre fără numitor | Orice cifră de progres se scrie ca raport: `31/31`, `485/509` |
| „Resetează" stă în aceeași coloană cu nota; un clic greșit șterge tot progresul | Mutat în Setări, cu o confirmare care cere scris cuvântul |
| Toate lecțiile se numesc la fel în istoricul browserului | `Slide 9 · Cursul 3 · Fluxuri de lucru`, în ordinea asta |
| Scris sub 11px în tabelul de statistici (10px în subsol) | Prag minim 11,5px în interfață, 13px în tot ce se proiectează |
| Antetul nu spune unde ești: nici rolul, nici dacă e ședință deschisă | Antetul capătă starea: rolul, și ședința dacă e una deschisă |
| Un student fără echipă vede o liniuță; un profesor fără ședințe vede un tabel gol | Fiecare stare goală primește o propoziție și o acțiune |
| Același fel de card pentru o notă, pentru o acțiune și pentru un rezultat | Trei forme distincte: notă (bară laterală), acțiune (umplere salvie), rezultat (cifră mare) |
| Nu există stare de „se încarcă" | Schelete, nu rotițe: formele apar goale, apoi se umplu |
| Nimic nu e de tipărit | O foaie de stil de tipar pentru raportul de ședință și pentru tabelul de note |
| Conturul de focus lipsește pe chipuri | Contur de 2px în salvie, peste tot, și o ordine care urmează citirea |

---

## Partea IV. Ordinea lucrului

Fiecare etapă se poate opri și lăsa situl funcțional.

**Etapa 1. Ședințele.** Tabelul, coloanele în plus, funcțiile de deschidere și
închidere. Fără schimbări vizibile, dar nimic din restul nu merge fără ea.
Riscul: migrarea prezențelor existente. Sunt puține, se pot arunca.

**Etapa 2. Produsul tău.** `/predau` cu cele trei pagini, raportul de ședință,
exportul. Scoaterea limbajului de student din tot ce vezi tu.

**Etapa 3. Live-ul ca lumea.** Modul pe ședință, blocarea navigării, panoul live
(cercul plus tabelul pentru slide-ul curent), feedback imediat la trimitere,
cele patru stări, auto-trimitere la schimbarea slide-ului.

**Etapa 4. Culorile și mărunțișurile.** Paleta caldă peste tot, apoi lista din
Partea III. Se poate face în paralel cu orice, și nu strică nimic dacă rămâne pe
jumătate.

**Etapa 5. Echipele.** Scriptul de generare, `echipe.json`, cardul din contul
studentului, tabloul tău. Complet independentă de restul.

### Fezabil?

Da, cu o observație. Etapele 1, 2 și 3 sunt grosul muncii și se țin una de alta:
nu are rost să începem etapa 3 fără 1. Etapele 4 și 5 sunt independente și pot
merge oricând, în orice ordine.

Ce ar fi nerezonabil de cerut: progres GitHub în timp real în browser (vezi
constrângerea de mai sus), și sincronizare live sub o secundă (acum se face prin
interogare la 5 secunde, ceea ce e suficient pentru o sală de curs și mult mai
simplu de întreținut decât websockets).

---

## De decis împreună

1. Ședințele se leagă de **grupă** sau doar de lecție? Dacă predai aceeași lecție
   la două grupe în zile diferite, grupa trebuie să fie pe ședință.
2. Când treci la slide-ul următor în live, ce se întâmplă cu un exercițiu
   început? Propunerea mea: se trimite automat, așa cum e. Alternativa: rămâne
   deschis și îl pot termina mai târziu, dar atunci nu mai e „live".
3. Prezența: se marchează o singură dată la intrare, sau contează și că au fost
   activi pe parcurs? A doua variantă e mai corectă și mai greu de păcălit.
4. Studenții văd notele colegilor în clasament, chiar anonimizat? Eu aș evita.
5. Ștergerea unei ședințe: definitivă, sau arhivată și ascunsă? Prefer arhivată,
   ca să nu existe pierderi accidentale.

---

## Surse

- [Nearpod, în Technology in the Curriculum (eCampusOntario)](https://ecampusontario.pressbooks.pub/techinthecurriculum/chapter/nearpod/),
  pentru distincția sincron / ritm propriu și pentru raportul generat de fiecare
  sesiune lansată.
- Cursul de AI engineering din acest depozit, `ai-engineering/progress/`, pentru
  modelul de tablou al echipelor pe issue-uri GitHub: instantaneu datat, rapoarte
  în loc de numere singure, o propoziție de stare, o singură acțiune.
- Captura TranscriptionLab trimisă de tine, pentru neutrele calde și salvie.
- Verificarea culorilor de stare: rulată cu validatorul de palete (bandă de
  luminozitate, saturație minimă, separare pentru daltonism, separare pentru
  vedere normală, contrast), nu estimată din ochi.
