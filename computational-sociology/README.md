# Introducere în sociologia computațională — prototip

Prototip de curs web interactiv pentru liceeni, izolat în directorul `computational-sociology/`.
Nu depinde de și nu modifică celelalte cursuri din repo (`ai-engineering/`, `git-guide/`, `progress/`, `Progres/`).

## Scop

Această etapă construiește **infrastructura vizuală și funcțională** a cursului:

- pagină de curs;
- pagină de lecție cu renderer bazat pe blocuri JSON;
- componentă de quiz;
- executor Python în browser (Pyodide într-un Web Worker);
- vizualizare de rețea (Cytoscape.js încărcat la cerere);
- progres local prin `localStorage`.

Doar prima lecție este populată minimal, cu conținut demonstrativ.

## Structura fișierelor

```
computational-sociology/
├── index.html           pagina principală a cursului
├── course.html          cuprinsul cursului
├── lesson.html          pagina generică de lecție
├── css/
│   ├── variables.css    tokens: culori, fonturi, spațiere
│   ├── base.css         reset, tipografie, focus
│   ├── layout.css       header, footer, breadcrumb, grid
│   └── components.css   butoane, quiz, code-runner, viz
├── js/
│   ├── app.js           logica paginii principale
│   ├── course.js        logica paginii de cuprins
│   ├── lesson.js        renderer de lecție (blocuri)
│   ├── progress.js      wrapper peste localStorage
│   ├── quiz.js          componentă de quiz
│   ├── code-runner.js   integrare Pyodide + editor
│   └── visualizations.js  Cytoscape.js + rețea
├── workers/
│   └── pyodide-worker.js  Web Worker pentru Python
├── data/
│   ├── course.json         structura cursului
│   ├── demo-network.json   date sintetice pentru rețea
│   └── demo-survey.json    date sintetice pentru sondaj
├── lessons/
│   └── demo.json           prima lecție demonstrativă
├── assets/                 imagini SVG / statice
└── README.md
```

## Cum se rulează local

Are nevoie de un server HTTP local (Pyodide și `fetch()` pentru JSON nu funcționează
de pe `file://`).

Din directorul `computational-sociology/`:

```
# Python 3
python -m http.server 8000

# sau Node
npx --yes http-server -p 8000 -c-1
```

Apoi deschide: <http://localhost:8000/index.html>

## De ce e necesar un server HTTP local

- Modulele ES (`type="module"`) nu se încarcă din `file://` în Chrome.
- `fetch()` pentru JSON local eșuează din `file://`.
- Web Worker-ul care încarcă Pyodide are nevoie de un origin `http(s)://`.

## Cum se testează Pyodide

1. Deschide `lesson.html?id=demo`.
2. Găsește exercițiul „Media vârstelor”.
3. Apasă „Încarcă Python”. La prima încărcare durează ~5–15 secunde.
4. Apasă „Rulează”. Rezultatul așteptat: `17.0`.
5. Verifică în `localStorage` cheia `computationalSociologyProgress`; câmpul
   `code["avg-age"].executed` ar trebui să fie `true`.

## Cum adaugi o lecție nouă

1. Creează `lessons/<slug>.json` după modelul din `lessons/demo.json`.
2. Setează câmpurile `prev` și `next` cu slug-uri de lecție (sau `null`).
3. În `data/course.json`, la secțiunea potrivită, setează `lesson: "<slug>"` și
   `status: "available"`.
4. Deschide `lesson.html?id=<slug>` pentru a o vedea.

## Cum adaugi un quiz

Introdu un bloc de tipul `quiz` în lecția JSON:

```json
{
  "type": "quiz",
  "id": "unique-id",
  "question": "Întrebarea?",
  "options": ["A", "B", "C", "D"],
  "correctIndex": 2,
  "explanation": "De ce răspunsul corect este C."
}
```

Cerință: `id` unic pentru fiecare quiz (folosit ca cheie în `localStorage`).

## Cum adaugi o vizualizare

1. Pune datele în `data/<name>.json`.
2. Adaugă un bloc `visualization` cu `kind: "network"` și `data: "data/<name>.json"`.
3. Momentan e implementat doar `kind: "network"`. Alte tipuri (grafic de bare etc.)
   se pot adăuga în `js/visualizations.js`.

## Cum publici prin Cloudflare Pages

Prototipul este 100% static. Cloudflare Pages servește `computational-sociology/`
ca subcale a repo-ului `courses/tutorials`, fără modificări la configurația existentă:

- publish directory rămâne rădăcina repo-ului;
- accesul se face la `<domeniu>/computational-sociology/`;
- fără build step, fără functions, fără variabile de mediu.

Nu se modifică nici root `index.html`, nici configurația actuală.

## Ce NU este încă implementat

- Scor real / notare pentru quiz-uri.
- Mai multe lecții — doar `demo` este populată.
- Pachete Python în plus (pandas, numpy). Prototipul rulează doar Python standard.
- Vizualizări în afară de rețea.
- Cont / autentificare / sincronizare între dispozitive.
- Traducere în alte limbi.
- Testare automată.
- Video real (există doar un placeholder).
- Meniu global / căutare.

## Note despre date

Toate datele din prototip sunt **sintetice** și marcate ca atare. Nu reprezintă
persoane reale sau rezultate ale unui sondaj real.
