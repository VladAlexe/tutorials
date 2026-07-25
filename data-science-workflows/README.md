# Fluxuri de lucru pentru știința datelor

Curs de masterat (UBB · ADC) format din două pagini statice:

- `index.html` — pagina de prezentare a cursului.
- `carte.html` — cartea interactivă (suportul de curs). Cuprins lateral, o secțiune
  pe ecran, blocuri de text și componente interactive.

Tot conținutul cărții stă în JSON, în `continut/`. Codul (randare, rutare, progres,
componente) stă în `js/`. Nu există build, framework sau dependințe externe: HTML, CSS
și JavaScript simplu, ca în restul repo-ului.

## Cum se rulează local

Ca și celelalte cursuri, are nevoie de un server HTTP local — `fetch()` pentru JSON și
modulele ES nu funcționează din `file://`.

```
# din folderul data-science-workflows/
python -m http.server 8000       # sau: npx --yes http-server -p 8000 -c-1
```

Apoi: <http://localhost:8000/index.html>

## Structura folderului

`continut/` = manifestul (`carte.json`) plus un fișier per capitol (`cap-00.json` …
`cap-08.json`). `js/` = încărcarea și randarea (`carte.js`, `blocuri.js`), stratul de
progres (`progres.js`) și componentele interactive (`js/interactive/`). `css/` = paleta și
aspectul, izolate la acest curs.

```
data-science-workflows/
  index.html            pagina cursului
  carte.html            cartea
  css/
    curs.css            pagina cursului
    carte.css           cartea: cuprins, coloană de lectură, blocuri (aici stau variabilele)
    interactive.css     carcasa și cele patru componente
  js/
    carte.js            încărcare, rutare cu ancoră, randarea secțiunii, cuprins
    blocuri.js          un renderer per tip de bloc
    progres.js          SINGURUL loc care atinge localStorage
    interactive/
      index.js          registrul: nume de componentă -> funcție
      flux.js  tipuri.js  json.js  terminal.js
  continut/
    carte.json          manifestul (titlu, capitole, secțiuni — sursa cuprinsului)
    cap-00.json         introducerea cărții
    cap-01.json         capitolul 1 (complet)
    cap-02.json … cap-08.json   capitolele 2–8 (schiță)
  assets/prototip/      prototipul original, ca material de lucru
```

Manifestul `carte.json` este **indexul**: cuprinsul lateral se desenează numai din el,
fără să încarce toate capitolele. Fiecare capitol se încarcă la cerere, când intri în el.
Titlul și starea fiecărei secțiuni apar și în manifest, și în fișierul capitolului;
pentru cuprins, manifestul este autoritatea.

## Cum adaug o secțiune nouă

1. Deschide fișierul capitolului potrivit din `continut/`, de ex. `cap-02.json`.
2. Adaugă un obiect în `sectiuni` cu: `id` (ex. `"2.10"`), `titlu`, `rezumat` (o propoziție,
   apare sub titlu), `stare` și `blocuri`.
3. `stare` are două valori:
   - `"gata"` — secțiunea are conținut și se afișează normal;
   - `"schita"` — apare în cuprins estompată; dacă nu are blocuri, se afișează o casetă
     „Secțiune în lucru”.
4. Adaugă **aceeași** secțiune (doar `id`, `titlu`, `stare`) în `continut/carte.json`, la
   capitolul respectiv, ca să apară în cuprins. (Manifestul e ușor, fără blocuri.)

Nu trebuie atins niciun fișier JavaScript.

## Cum adaug o componentă interactivă nouă

1. Scrie-o în `js/interactive/<nume>.js`, exportând **o singură funcție** implicită cu
   semnătura `(gazda, parametri)`. `gazda` e elementul în care randezi; `parametri` e
   obiectul din JSON. Fără stare globală comună.
2. Înregistreaz-o în `js/interactive/index.js`: importă funcția și adaug-o în obiectul
   `REGISTRU` sub numele pe care îl vei folosi din JSON.
3. Cheam-o dintr-un bloc `interactiv`:

```json
{
  "tip": "interactiv",
  "componenta": "numele-din-registru",
  "titlu": "Titlu scurt",
  "sarcina": "Ce are de făcut cititorul.",
  "parametri": { "orice": "date are nevoie componenta" }
}
```

Randorul de blocuri nu cunoaște componentele: le cere registrului după nume. Datele de
care are nevoie o componentă se pun în `parametri`, nu în codul ei.

## Tipurile de bloc

| tip | câmpuri | ce face |
|---|---|---|
| `text` | `continut` | paragraf; acceptă `<strong>` și `<code>` |
| `lista` | `elemente` | listă neordonată (fiecare element acceptă HTML) |
| `nota` | `eticheta`, `continut` | casetă evidențiată, cu etichetă scurtă |
| `cod` | `limbaj`, `continut` | bloc de cod, needitabil |
| `tabel` | `antet`, `randuri` | tabel simplu |
| `verificare` | `intrebare`, `optiuni`, `corect`, `explicatie` | grilă cu explicație după răspuns |
| `interactiv` | `componenta`, `titlu`, `sarcina`, `parametri` | inserează o componentă din registru |
| `in_lucru` | `continut` | marchează vizibil o bucată nescrisă încă |

La `verificare`, `corect` este indicele (de la 0) al opțiunii corecte. Răspunsul dat se
salvează și se restaurează la reîncărcare; fiecare verificare dintr-o secțiune primește
automat un id (`v0`, `v1`, …) după poziția ei în secțiune, deci nu muta verificările fără
să te aștepți ca un răspuns salvat să se re-asocieze.

## Progresul și trecerea la cont / server

Progresul (secțiuni vizitate, răspunsuri la verificări) se ține în `localStorage`, sub o
singură cheie (`dswProgress`), cu un câmp `versiune` în obiect. **Numai `js/progres.js`**
atinge `localStorage`; restul aplicației folosește doar interfața:

```
init(config)                                config.total = nr. secțiunilor numărate (1.x–8.x)
getStare()
marcheazaVizitata(idSectiune)
salveazaRaspuns(idSectiune, idIntrebare, raspuns, corect)
getProcentGeneral()                         0–100, doar pe secțiunile numărate
onSchimbare(callback)                        notifică interfața la fiecare scriere
```

(`reset()` este un utilitar de întreținere pentru golire completă, nu face parte din
interfața stabilă.)

**Pentru a muta progresul pe cont și pe o bază de date**, se schimbă doar `js/progres.js`,
păstrând aceeași interfață:

- `init()` devine `async` și face autentificarea / preîncărcarea stării de pe server
  (de ex. Supabase), păstrând o copie în memorie pentru citiri sincrone;
- `citeste()`/`scrie()` se rescriu peste API-ul serverului, în locul lui `localStorage`;
  `scrie()` poate rămâne „optimist” (actualizează local, apoi trimite la server);
- `getStare`, `marcheazaVizitata`, `salveazaRaspuns`, `getProcentGeneral`, `onSchimbare`
  rămân neschimbate ca semnătură, deci `carte.js` și `blocuri.js` nu se modifică.

Cheia unică și câmpul de versiune sunt gândite tocmai pentru migrare: la o schimbare de
schemă, `citeste()` migrează din versiunea veche în cea nouă.

## Prototipul

`assets/prototip/dsw-carte.html` este prototipul original, păstrat ca material de lucru și
referință de aspect. Nu face parte din sit. Conținutul lui a fost extras în `continut/`,
iar scriptul inline a fost înlocuit cu o notă, fiindcă logica trăiește acum în `js/`.
