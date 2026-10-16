# Plan: ora, butoanele, punctajul

Stare: decis în discuția din 16 octombrie 2026. Nimic din ce e aici nu e
implementat încă. Perechea vizuală e artifactul „Ora, pas cu pas", unde fiecare
stare a benzii e desenată cu culorile cursului.

Documentul are nouă părți. Primele cinci sunt despre cum se predă și ce butoane
există. Ultimele patru sunt despre ce se întâmplă cu ce fac ei: punctaj,
resetare, contul lor, catalogul tău.

---

## Regula din care iese tot restul

**Conduci din lecție, întotdeauna.**

Lecția e ce proiectezi, deci acolo stai oricum. Nu există o a doua pagină cu
butoane care să facă același lucru. Tot ce ai nevoie în timpul orei intră într-o
bandă subțire, jos, în pagina lecției.

Asta rezolvă nemulțumirea ta de fond. Nu erau prea multe butoane, ci **aceeași
oră avea două volane**, unul în lecție și unul în panou, iar tu nu știai la care
să te uiți.

---

## Partea I. Ce există acum, și ce rămâne

Acum comenzile orei sunt împrăștiate pe trei suprafețe: banda lecției, bara
panoului, și meniul de sus. Douăsprezece butoane în total.

| Acum, unde | Buton | Ce se întâmplă cu el |
|---|---|---|
| banda lecției | Pornește ora | **rămâne**, e singura pornire din sit |
| banda lecției | Lasă-i singuri / Ține-i cu mine | **rămâne** |
| banda lecției | Panoul live | devine **al doilea ecran ↗**, se deschide tab nou |
| banda lecției | Oprește ora | **rămâne**, redenumit Închide ora |
| bara panoului | ← Înapoi | **dispare**, slide-ul se schimbă din lecție |
| bara panoului | Înainte → | **dispare** |
| bara panoului | Proiector | **dispare**, ecranul tău chiar e proiectorul |
| bara panoului | Treci pe ritm propriu | **dispare**, e deja în bandă |
| bara panoului | Închide ora | **dispare**, e deja în bandă |
| meniu | Lecțiile | **rămâne** |
| meniu | Ora | **dispare**, nu mai e o pagină unde mergi |
| meniu | Ședințele | **se unește** cu Semestrul |
| meniu | Semestrul | devine **Catalogul** |

Rămân patru butoane, pe o singură suprafață, și niciodată toate patru deodată.

---

## Partea II. Banda din lecție

Există doar când ești profesor pe pagina unei lecții. Înălțime fixă, circa 44px,
pe cromul aplicației (`--crom`), ca să nu pară parte din slide. Când apare,
scena coboară cu înălțimea ei, ca să nu acopere numărul slide-ului.

### Stările ei

**Nu predai.** Pastilă rece, „Nu predai acum", „umbli prin lecție de unul
singur", și un buton: **Pornește ora**.

**Ora merge.** Pastilă vie, codul într-o casetă monospațiată, câți sunt în
clasă, în ce mod merg. La dreapta: **al doilea ecran ↗**, **Lasă-i singuri**,
**Închide ora**.

**Slide cu quiz.** Aceeași bandă, plus un rând de stări: ceasul, apoi cele patru
cifre cu glifele lor (✓ corect, ✕ greșit, ◉ trimis gol, ○ n-a trimis). Nimic nu
se mută, doar se adaugă.

**Panoul deschis.** Banda se simplifică la pastilă, cod, ceas, și **strânge
panoul**. Restul comenzilor sunt sub panou, nu dispar, doar nu se mai văd.

### Pornirea

Un singur buton, fără formular. Grupa se alege singură: dacă ai una, aia e; dacă
n-ai niciuna, se face „Grupa 1" pe loc și o redenumești când ai chef. Modul e
întotdeauna live la pornire, pentru că asta faci când intri la clasă.

Imediat după pornire, codul apare mare peste slide, cu QR și adresa scurtă. Se
închide cu Esc sau cu un clic. Codul rămâne pe urmă în bandă, pentru întârziați,
și se poate redeschide mare apăsând pe el.

### Taste

| Tastă | Ce face |
|---|---|
| → ← | slide-ul următor, slide-ul anterior |
| `V` | deschide sau strânge panoul peste treimea de jos |
| `C` | codul mare, de proiectat |
| Esc | închide ce e deschis peste slide |

---

## Partea III. Panoul

Același conținut, două forme. Nu sunt două pagini, e aceeași vedere desenată în
două locuri.

**Sertarul**, peste treimea de jos a lecției, pentru când ai un singur ecran.
Apare la `V`, se strânge la `V` sau Esc. Studenții nu văd nimic, slide-ul rămâne
întreg pe proiector.

**Al doilea ecran**, la `/predau/ora/`, pentru când ai două. Se deschide dintr-un
link din bandă, într-un tab nou, deja legat la ora care merge. Fără cod de
tastat, fără ales lecția, fără autentificare din nou.

Ce arată, în ambele forme:

- întrebarea care e pe ecran acum, scrisă întreagă
- un rând per student: numele, ce a ales, dacă e corect, cât a făcut din toată ora
- cifrele pe cele patru stări, și ceasul
- sortare după slide, după nume, sau după cât a făcut

Ce **nu** are, în niciuna dintre forme: niciun buton care schimbă ora. Fără
înainte, înapoi, mod, închidere. Panoul doar se uită. Se mișcă singur după tine:
când treci la slide-ul următor în lecție, trece și el.

---

## Partea IV. Ceasul

Numără în sus de când a apărut slide-ul pe ecran, nu de la începutul orei. Ăla e
numărul care îți spune când să mergi mai departe.

- Verde (`--ok`) până la un prag.
- Chihlimbar (`--ceas`, jeton nou) după prag.
- Pragul e două minute, și se poate schimba o singură dată, din setări, nu la
  fiecare slide.

Nu e numărătoare inversă și nu dă pe nimeni afară din întrebare. Doar se vede că
timpul trece.

**Îl văd și ei**, în banda lor, cu aceeași culoare. Aici am făcut o schimbare
față de ce ai cerut: nu folosesc portocaliul-cărămiziu al temei, pentru că e
deja culoarea pentru „greșit". Un ceas de aceeași culoare se citește cu coada
ochiului, de la distanță, ca „am greșit". Chihlimbarul păstrează regula curată:
cărămiziu înseamnă greșit, și nimic altceva.

---

## Partea V. Meniul profesorului

Două intrări, nu patru.

**Lecțiile.** Lista celor șapte seminare, în ordine, cu starea fiecăruia (ținut
pe data cutare, urmează, neținut) și un buton care deschide lecția. De aici
pleci spre clasă. Ora nu se pornește de aici, se pornește din lecție.

**Catalogul.** Studenți pe rânduri, seminare pe coloane. În celulă, de câte ori a
fost live și de câte ori a făcut lecția singur. Apeși pe celulă și vezi ora aia
în detaliu, cu raportul ei. Tot aici:

- coloanele în care scrii tu nota la teme și la proiect
- totalul calculat automat, pe om
- selecția de grupe și butonul de export

„Ora" dispare din meniu pentru că nu mai e o pagină unde mergi, e o stare în care
te afli. „Ședințele" și „Semestrul" se unesc pentru că răspund la aceeași
întrebare: ce a ieșit.

### Exportul

Un CSV, toate cursurile deodată, cu selecția de grupe. O linie per student:

```
matricol; nume; grupa;
c1_live; c1_singur; c2_live; c2_singur; ... c7_live; c7_singur;
seminare_live; activitate; prezenta; teme; proiect; total
```

Punct și virgulă, cu BOM, ca Excel în română să desfacă corect coloanele și să nu
strice diacriticele.

---

## Partea VI. Punctajul

Nota se face din patru bucăți. Trei le calculează situl, una o scrii tu.

| Bucată | Puncte | Cine o pune |
|---|---|---|
| Teme de seminar | 3 | tu, de mână, în catalog |
| Activitate la seminar (quiz-uri) | 2 | situl |
| Prezență | 1 | situl |
| Proiect în echipă | 5 | tu, de mână, în catalog |
| **Total** | **11** | |

Nota maximă e 11, deci punctul de prezență e peste 10.

### Activitatea, 2 puncte

```
pe seminar      = 2 / 7 = 0,2857
pe quiz         = 0,2857 / câte quiz-uri are seminarul
la oră          = întreg
acasă           = jumătate
se ia cel mai bun dintre cele două
```

Numărul de quiz-uri dintr-un seminar **nu schimbă cât valorează seminarul**. Zece
sau patru, seminarul face tot 0,2857. Deci tai din quiz-uri pentru atenția lor,
nu pentru notă, și nu trebuie să echilibrezi lecțiile între ele.

### Prezența, 1 punct

```
pe seminar      = 1 / 7 = 0,1429
se ia dacă ai răspuns la cel puțin 75% din quiz-urile seminarului,
corect sau nu, în timpul orei live
altfel zero
```

### Ce iese din asta

| Cum faci seminarul | Cât iei, cel mult |
|---|---|
| La oră, tot | 0,2857 + 0,1429 = **0,4286** |
| Acasă, tot | 0,2857 × 0,5 = **0,1429** |

**Ora live valorează exact de trei ori cât aceeași lecție făcută acasă.** E o
propoziție pe care le-o spui o dată, la început de semestru, și nu mai explici
nimic tot anul.

### Ce intră la punctaj

Numai quiz-urile: verificările cu variante, și exercițiile de cod care au un
răspuns verificabil. **Interacțiunile nu sunt quiz-uri**: exploratoarele,
hărțile, terminalele, lucrurile de umblat cu mâna rămân ce sunt, fără punctaj.

---

## Partea VII. Resetarea răspunsurilor

**Fiecare deschidere a lecției e o încercare nouă. Pagina pornește curată.**

Acum rămân bifele de data trecută, și de aici vine problema reală: dacă vin la
oră și văd deja răspunsul de acasă, întrebarea live nu mai măsoară nimic.

Istoricul rămâne întreg în bază, pentru că din el se face nota. Dacă vor să vadă
ce au răspuns altă dată, un rând discret sub lecție („ai mai făcut lecția asta de
două ori, vezi ce ai răspuns"), nu bife pe opțiuni.

---

## Partea VIII. Contul studentului

Problema de acum: arată progres pe sarcini, procente și bare, care nu mai
înseamnă nimic de când nota se face altfel. Nu răspunde la singura lui întrebare,
**cât am**.

Trei rânduri, sus:

```
Ai fost la 5 din 7 seminare.
Ai 1,24 din 3 la activitate.
Îți mai pot aduce puncte 2 seminare.
```

Dedesubt, lista lecțiilor, fiecare cu un cuvânt (la oră, acasă, nefăcută) și un
buton de deschis. Fără procente, fără bare de progres.

---

## Partea IX. În ce ordine

1. **Resetarea răspunsurilor** și încercările. E cea mai mică schimbare și cea
   care strică cel mai mult acum, la fiecare oră ținută.
2. **Banda din lecție**, cu ceasul și rândul de stări. După asta poți ține o oră
   fără să deschizi altă pagină.
3. **Panoul ca sertar**, și `/predau/ora/` devine oglindă fără butoane.
4. **Punctajul**, în bază: funcția care calculează cele 3 puncte pe om.
5. **Catalogul**, cu coloanele de mână și exportul.
6. **Contul studentului**, cele trei rânduri.
7. **Echipele**, după ce se lămuresc regulile proiectului.

---

## Ce nu e încă decis

- **Pragul de 75% la prezență.** Acum e tăios: cine răspunde la 74% dintr-un
  seminar ia zero pe toată ora aia, deși a stat acolo aproape tot timpul. Rămâne
  tăios, sau sub prag se ia proporțional?
- **Exercițiile de cod la punctaj.** Dacă intră, un student care se împiedică de
  o virgulă pierde puncte pentru o problemă de tastat, nu de înțeles.
- **Echipele.** Nota de proiect e pe om, dar cum se leagă de echipă, și cine
  formează echipele, rămâne de detaliat.
- **Lecțiile 6, 7, 8.** Sunt stub-uri. Dacă seminarele sunt 7 și lecțiile scrise
  sunt 5, numitorul fix de 7 înseamnă că nimeni nu poate trece de 1,43 din 2.
