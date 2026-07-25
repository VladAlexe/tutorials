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

Funcția poate fi `async` (componentele capitolului 2 sunt): randorul nu așteaptă
rezultatul, componenta se desenează singură când e gata.

## Datele componentelor (`continut/date/`)

Componentele capitolului 2 rulează pe fișiere din `continut/date/`, încărcate cu ajutorul
din `js/interactive/date.js` (`incarcaDate("nume.json")`). **Nu există niciun apel către
un API extern**; singurul `fetch` e către fișierele proprii ale cursului, la fel ca
încărcarea capitolelor. În JSON, blocul trimite doar numele fișierului prin
`parametri.sursa`.

De unde provin fișierele și cum se regenerează:

- `restaurant.json`, `taxonomie.json`, `anatomie.json`, `harta-doc.json`, `secrete.json`,
  `surse.json` — scrise manual, ca material didactic. `surse.json` conține surse reale, cu
  documentația oficială; legăturile au fost verificate. Se editează direct.
- `wb-data.json` — **eșantion ilustrativ**, salvat local, care reproduce forma răspunsului
  Băncii Mondiale (populație și CO2 pentru RO/IT/ES, 2018–2023). Valorile sunt un eșantion
  mic, nu o extragere live. Se regenerează dintr-o cerere reală la
  `https://api.worldbank.org/v2/country/ro;it;es/indicator/SP.POP.TOTL?format=json`,
  păstrând forma `valori["<cod>|<indicator>"] = { an: valoare }`.
- `coduri.json`, `json-tabel.json` — răspunsuri și scenarii pre-salvate care reproduc
  comportamentul real al celor două API-uri (200 cu eroare în corp la Banca Mondială, 400
  la Eurostat; JSON vs JSON-stat). Se editează manual.

Componentele care construiesc răspunsuri (constructor, paginare, json_tabel) folosesc
`js/interactive/wb.js`, care împachetează eșantionul local în forma cu două elemente a
Băncii Mondiale. Tot fără rețea.

Capitolul 3 adaugă `versiuni.json`, `anulare.json` (arbore de decizie), `conflict.json`
(două scenarii, cu și fără conflict) și `gitignore.json` (arbore de fișiere + fișierul
deja urmărit, capcana). Toate scrise manual, se editează direct. `terminal_git` nu are
fișier de date — starea Git e construită în componentă din `parametri`.

## Componentele capitolului 2

`restaurant`, `taxonomie`, `surse`, `anatomie`, `constructor`, `coduri`, `harta_doc`,
`secrete`, `cod_parametri`, `paginare`, `json_tabel`. Fiecare e o demonstrație sau un
exercițiu pe date locale, nu o cerere reală — munca reală se face în editorul studentului.

## Componentele capitolului 3 (Git)

`versiuni`, `terminal_git`, `zone`, `anulare`, `ramuri`, `conflict`, `sincronizare`,
`gitignore`. Niciuna nu rulează Git real; sunt reproduceri.

- **`terminal_git`** e cea mai importantă și se refolosește (3.2, 3.5, 3.7). Are un model
  de stare adevărat — fișiere, cele trei zone, commituri, ramuri, depozit la distanță,
  config — și răspunde cu mesajele reale ale Git-ului, inclusiv la comenzi în ordine
  greșită. Comenzi de simulare în plus: `nou <fisier>`, `edit <fisier>`, `ajutor`,
  `curata`. Parametri: `fisiere` (semințe), `sarcini` (bife), `preInit` (pornește dintr-un
  depozit cu un commit, pentru secțiunile despre ramuri), `remote` + `scenariu`
  (`push-auth` / `push-reject`) pentru a demonstra respingerea/eșecul la push.
- **`ramuri`** și graful din el desenează commiturile în **SVG**, fără biblioteci; graful
  se derulează pe orizontală pe ecran îngust, nu se micșorează.
- `versiuni`, `anulare`, `conflict`, `gitignore` citesc din `continut/date/`
  (`versiuni.json`, `anulare.json`, `conflict.json`, `gitignore.json`). `zone`,
  `ramuri`, `sincronizare` au stare proprie, configurată prin `parametri`.

## Tipurile de bloc

| tip | câmpuri | ce face |
|---|---|---|
| `text` | `continut` | paragraf; acceptă `<strong>` și `<code>` |
| `lista` | `elemente` | listă neordonată (fiecare element acceptă HTML) |
| `nota` | `eticheta`, `continut` | casetă evidențiată, cu etichetă scurtă |
| `cod` | `limbaj`, `continut` | bloc de cod, needitabil |
| `tabel` | `antet`, `randuri` | tabel simplu |
| `verificare` | `id`, `intrebare`, `optiuni`, `corect`, `explicatie` | grilă cu explicație după răspuns |
| `interactiv` | `componenta`, `titlu`, `sarcina`, `parametri` | inserează o componentă din registru |
| `in_lucru` | `continut` | marchează vizibil o bucată nescrisă încă |
| `la_proiect` | `continut` | aplicarea noțiunii generale la sursele proiectului; bandă laterală, etichetă |
| `rezultat` | `continut` | constatarea cu care se închide un capitol; evidențiat |
| `limite` | `continut` | ce nu poate spune ce tocmai am făcut; sobru |
| `lecturi` | `titlu`, `referinte` | referințe, fiecare cu `autor`, `an`, `titlu`, `sursa`, `url` (opțional) |

`la_proiect`, `rezultat` și `limite` primesc `continut` HTML (pot conține mai multe
`<p>`). `lecturi` primește o listă `referinte`; `url` e opțional (fără el, titlul nu e
legătură).

**Id-ul verificărilor.** Fiecare bloc `verificare` are un câmp `id` stabil, de forma
`"2.3-v1"`. Acesta e cheia sub care se salvează răspunsul, deci nu se schimbă și nu se
refolosește. Dacă lipsește, se cade înapoi pe poziția blocului în secțiune (`v0`, `v1`…),
dar la conținut nou pune întotdeauna un `id`.

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
