# -*- coding: utf-8 -*-
"""
Lecția 3: Versionare și colaborare cu Git.

Ordinea: întâi Git (ce face, cele trei zone), apoi depozitul echipei, așa cum
îl găsesc studenții (echipa-N pe GitHub, creat din șablon): clonarea,
.gitignore, primul commit pe main, ramura dev, pull înainte de push,
conflictele, verificarea. La final, cadrul teoretic și datele proiectului.

Ce am adăugat peste prezentare, și de ce:
  - cele trei zone (lucru, pregătire, istoric), pentru că fără ele comenzile
    lui Git se învață pe de rost și se uită până săptămâna următoare;
  - .gitignore, pentru că prima greșeală serioasă a unei echipe e un fișier
    cu parole urcat din neatenție, și se repară greu;
  - ramurile și pull request-ul, anunțate în titlul cursului, dar fără slide;
  - explorarea inițială a datelor colectate la cursul 2, care închide bucla.

Rulare:  python _build/c3.py
"""

import json

from literatura import lecturi
from comun import Lectie, ix, verif, tabel, nota, REPO_ORG, RAD

L = Lectie(3, "c3-versionare-git", "Versionare și colaborare cu Git",
           "Ce face Git, cum se leagă depozitul local de GitHub, cum lucrează "
           "în paralel membrii unei echipe și cum se încadrează teoretic un proiect de cercetare.")
sl = L.sl


# ===========================================================================
#  1-2. Cursul
# ===========================================================================

AGENDA = [
    ("Ce face Git", "azi", "Istoricul, Git și GitHub, cele trei zone."),
    ("Depozitul echipei", "azi", "Clonarea din șablon, .gitignore, primul commit."),
    ("Lucrul în echipă", "azi", "main și dev, pull înainte de push, conflictele."),
    ("Verificarea", "azi", "git status și depozitul, local și pe GitHub."),
    ("Cadrul proiectului", "azi", "Ce explică legăturile dintre locuri; întrebarea echipei."),
    ("Datele proiectului", "azi", "Tabelele pregătite în caietul 03, gata de unit la cursul 4."),
]

# Pașii pentru lecția 3: Git (caietul 03, secțiunea 6) și migrația (caietul 03, secțiunea 5).
# Cifrele migrației: Eurostat migr_pop1ctz, 2024, din rularea caietului (31 octombrie 2026).

FISA = '<a class="leg" href="../git/">Lucrul cu Git</a>'   # pagina cu toate comenzile
_MSG = "Pregatim tabelele regionale si migratia"

# --------------------------------------------------------------------------
# Cele trei zone, exercițiul: două fișiere noi, comenzile ca butoane, iar
# terminalul răspunde ca Git (inclusiv la ordinea greșită).
# --------------------------------------------------------------------------

ZONE = {
    "id": "c3-zone",
    "sarcina": "Cele două fișiere trebuie să ajungă pe GitHub. Comenzile se dau ca în terminal, iar dedesubt "
               "apare ce răspunde Git; <code>git status</code> arată oricând unde se află fiecare fișier.",
    "fisiere": ["colectare.py", "README.md"],
    "mesaje": {"colectare.py": "colectarea migratiei", "README.md": "README",
               "colectare.py + README.md": "colectarea si README"},
}

# --------------------------------------------------------------------------
# Depozitul echipei, pe calculator. Repo-urile echipa-N sunt create din
# șablonul proiect-template de butonul „Sincronizează GitHub” din Predau
# (db/26); membrii cu numele legat de un cont GitHub primesc invitația.
# Structura: cea din caietul 03, secțiunea 7 (aceeași pentru toate echipele).
# --------------------------------------------------------------------------

_ARB0 = [[0, "dsw/", "", ""], [1, ".venv/", "mediul virtual", ""], [1, "curs/", "caietele cursului, fără Git", ""]]
_PROIECT = [[1, "proiect/", "depozitul echipei, cu Git"], [2, ".git/", "istoricul"],
            [2, "data/raw/", "datele originale"], [2, "data/processed/", "tabelele produse de caiete"],
            [2, "notebooks/", "câte un caiet pe pas"], [2, "src/", "cod comun, .py"],
            [2, "figures/", "figurile"], [2, "docs/", "raportul"], [2, "README.md", "descrierea proiectului"]]
_ARB_NOU = _ARB0 + [r + ["nou"] for r in _PROIECT]
_ARB_GATA = _ARB0 + [r + [""] for r in _PROIECT]

CLONA = {
    "repo": {"org": "dsw-ubb-2026", "nume": "echipa-4", "sablon": "proiect-template",
             "fisiere": ["data/", "notebooks/", "src/", "figures/", "docs/", "README.md"],
             "adresa": "https://github.com/dsw-ubb-2026/echipa-4.git",
             "membri": ["Andrei", "Maria", "Ioana", "Radu", "Elena"]},
    "inceput": "Terminalul este deschis în dosarul dsw, cel cu .venv/ și curs/.",
    "start": "Repo-ul echipei există deja pe GitHub, făcut din șablonul cursului, iar membrii au primit "
             "invitația. Pașii de sus îi face fiecare membru, o singură dată.",
    "stari": [
        {"arbore": _ARB0, "dir": "~/dsw", "ghActiv": True},
        {"acces": [0], "arbore": _ARB0, "dir": "~/dsw", "ghActiv": True},
        {"acces": [0], "adresa": True, "arbore": _ARB0, "dir": "~/dsw", "ghActiv": True},
        {"acces": [0], "adresa": True, "clona": True, "arbore": _ARB_NOU, "dir": "~/dsw", "pcActiv": True},
        {"acces": [0], "arbore": _ARB_GATA, "dir": "~/dsw", "pcActiv": True},
        {"acces": [0], "arbore": _ARB_GATA, "dir": "~/dsw/proiect", "ramura": "main", "pcActiv": True},
    ],
    "pasi": [
        {"cmd": "invitația", "edit": True, "t": "Accesul",
         "txt": "Invitația vine pe e-mailul contului GitHub și se acceptă o dată. Vine doar dacă numele de pe "
                "site este legat de contul GitHub; expiră după 7 zile.",
         "out": [["g", "github.com/dsw-ubb-2026/echipa-4/invitations  →  Accept invitation"]]},
        {"cmd": "adresa", "edit": True, "t": "Adresa",
         "txt": "Pe pagina repo-ului: butonul verde <b>Code</b>, fila <b>HTTPS</b>, apoi copierea adresei.",
         "out": [["g", "https://github.com/dsw-ubb-2026/echipa-4.git"]]},
        {"cmd": "git clone", "full": "git clone https://github.com/dsw-ubb-2026/echipa-4.git proiect", "t": "Clonarea",
         "txt": "Din dosarul <code>dsw</code>. Git copiază repo-ul, cu tot istoricul, în dosarul <code>proiect</code> "
                "și ține minte de unde l-a luat (<code>origin</code>). Ultimul cuvânt al comenzii este numele dosarului.",
         "out": [["", "Cloning into 'proiect'..."], ["", "remote: Enumerating objects: 7, done."],
                 ["", "Receiving objects: 100% (7/7), done."]]},
        {"cmd": "cd proiect", "t": "În depozit",
         "txt": "Comenzile Git de azi se dau de aici, din <code>proiect</code>. Promptul arată acum dosarul și "
                "ramura curentă: main.",
         "out": [["", "~/dsw/proiect (main) $"]]},
        {"cmd": "git status", "t": "Verificarea",
         "txt": "Pe main, la zi cu GitHub, nimic schimbat. Depozitul echipei este pe calculator, legat de GitHub.",
         "out": [["", "On branch main"], ["", "Your branch is up to date with 'origin/main'."],
                 ["", "nothing to commit, working tree clean"]]},
    ],
}

# --------------------------------------------------------------------------
# Primul commit al echipei, pe main, ca în caietul 03 (7.3): un membru
# completează README.md (titlul, întrebarea, unitatea de analiză, sursele);
# altul urcă la fel src/date_api.py. git add pune în pregătire o copie;
# originalul rămâne în dosar.
# --------------------------------------------------------------------------

_MSG1 = "Tema si intrebarea provizorie"
COMMIT = {
    "ramura": "main",
    "fisiere": {"rd": {"t": "README.md"}},
    "notaDosar": "neschimbate: <code>data/</code>, <code>notebooks/</code>, <code>src/</code>, <code>figures/</code>, <code>docs/</code>",
    "commituri": {"c0": {"h": "9f8e7d6", "m": "Initial commit", "x": "din șablon", "vechi": True},
                  "c1": {"h": "a1b2c3d", "m": _MSG1, "x": "1 fișier"}},
    "inceput": "Depozitul tocmai a fost clonat: dosarul, istoricul și GitHub au același commit, cel din șablon.",
    "start": "Primul commit îl face un singur membru, pe main: completează <code>README.md</code>. "
             "Comenzile de sus se apasă pe rând.",
    "stari": [
        {"dosar": {"rd": ""}, "ist": ["c0"], "gh": ["c0"]},
        {"dosar": {"rd": "modificat"}, "ist": ["c0"], "gh": ["c0"], "activ": [0]},
        {"dosar": {"rd": "modificat"}, "ist": ["c0"], "gh": ["c0"], "activ": [3]},
        {"dosar": {"rd": "modificat"}, "ist": ["c0"], "gh": ["c0"], "activ": [0]},
        {"dosar": {"rd": "pregatit"}, "preg": ["rd"], "ist": ["c0"], "gh": ["c0"], "activ": [1], "punte": 1},
        {"dosar": {"rd": "salvat"}, "ist": ["c1", "c0"], "gh": ["c0"], "activ": [2], "punte": 2},
        {"dosar": {"rd": "salvat"}, "ist": ["c1", "c0"], "gh": ["c1", "c0"], "activ": [3], "punte": 3},
    ],
    "pasi": [
        {"cmd": "README.md", "edit": True, "t": "În VS Code",
         "txt": "În <code>README.md</code>, provizoriu: titlul, întrebarea de cercetare, unitatea de analiză și "
                "tabelul surselor de date.",
         "out": [["g", "README.md: titlul, întrebarea, unitatea de analiză, sursele"]]},
        {"cmd": "git pull", "t": "Întâi pull",
         "txt": "Înainte de orice commit: ce au trimis colegii. Aici, nimic nou.",
         "out": [["", "Already up to date."]]},
        {"cmd": "git status", "t": "Ce vede Git",
         "txt": "Un fișier modificat, încă neadăugat. În terminal apare cu roșu.",
         "out": [["", "On branch main"], ["", "Your branch is up to date with 'origin/main'."],
                 ["", "Changes not staged for commit:"], ["nu", "        modified:   README.md"]]},
        {"cmd": "git add", "full": "git add README.md", "t": "Ce intră în commit",
         "txt": "<code>git add</code> pune în pregătire o copie a fișierului, așa cum este acum. Originalul rămâne în dosar.",
         "out": [["g", "git add nu afișează nimic: copia stă în pregătire."]]},
        {"cmd": "git commit", "full": f"git commit -m \"{_MSG1}\"", "t": "Fotografia",
         "txt": "Copia devine un commit: fotografia fișierului, cu autorul, data și mesajul. Deocamdată există "
                "doar pe calculator.",
         "out": [["", f"[main a1b2c3d] {_MSG1}"], ["", " 1 file changed, 14 insertions(+), 3 deletions(-)"]]},
        {"cmd": "git push", "t": "Pe GitHub",
         "txt": "Commit-ul ajunge pe GitHub, pe main. Alt membru urcă la fel <code>src/date_api.py</code>; "
                "ceilalți le iau pe amândouă cu <code>git pull</code>.",
         "out": [["", "To https://github.com/dsw-ubb-2026/echipa-4.git"], ["", "   9f8e7d6..a1b2c3d  main -> main"]]},
    ],
}

# --------------------------------------------------------------------------
# git status, citit: ieșirea adevărată, în engleză, cu culorile terminalului,
# pe dev, cu fișierele din structura șablonului (notebooks/, src/).
# --------------------------------------------------------------------------

STATUS = {
    "id": "c3-status",
    "sarcina": "Înainte de commit. Ce intră în commit dacă se rulează acum <code>git commit</code>? "
               "Rândurile se aleg cu un clic.",
    "antet": ["On branch main", "Your branch is up to date with 'origin/main'."],
    "grupuri": [
        {"t": "Changes to be committed:", "cls": "pr", "zona": "pregătire: intră în commit",
         "fisiere": [{"t": "modified:   README.md", "ok": True},
                     {"t": "new file:   src/date_api.py", "ok": True}]},
        {"t": "Changes not staged for commit:", "cls": "ds", "zona": "dosar: modificat, nu intră",
         "fisiere": [{"t": "modified:   notebooks/01_collection.ipynb", "ok": False}]},
        {"t": "Untracked files:", "cls": "ds", "zona": "dosar: nou, neurmărit",
         "fisiere": [{"t": "figures/test.png", "ok": False}]},
    ],
    "indiciu": "Git împarte ieșirea în trei grupuri. Doar unul are legătură cu <code>git add</code>.",
    "indiciu2": "În terminal, grupul care intră în commit este scris cu verde.",
    "laRau": "Intră doar ce a trecut prin <code>git add</code>.",
    "laBine": "Intră doar grupul „Changes to be committed”.",
    "explicatie": "Celelalte două nu au trecut prin <code>git add</code>. Pentru a intra și ele: "
                  "<code>git add notebooks/01_collection.ipynb figures/test.png</code>, apoi din nou <code>git status</code>.",
}

# --------------------------------------------------------------------------
# Ramurile, cum lucrează echipa: main stabil, dev pentru lucrul de zi cu zi.
# Un membru creează dev și îl urcă; ceilalți trec pe el; la o sarcină
# încheiată, dev intră în main. Lângă graf: ce conține dosarul.
# --------------------------------------------------------------------------

_AUT = {"an": {"t": "Andrei", "c": "ambra"}, "ma": {"t": "Maria", "c": "accent"}}
_C5 = ["c0", "c1", "a1", "m1"]
RAMURI = {
    "id": "c3-ramuri", "ramura": "dev", "dosar": "proiect/",
    "autori": _AUT,
    "commituri": {
        "c0": {"x": 0, "lane": "m", "m": "din șablon"},
        "c1": {"x": 1, "lane": "m", "m": "tema și întrebarea", "parinti": ["c0"]},
        "a1": {"x": 2, "lane": "r", "m": "colectarea", "a": "an", "parinti": ["c1"]},
        "m1": {"x": 3, "lane": "r", "m": "preprocesarea", "a": "ma", "parinti": ["a1"]},
        "mg": {"x": 4, "lane": "m", "m": "merge dev", "merge": True, "parinti": ["c1", "m1"]},
    },
    "linii": [{"c": "c1", "t": "README.md"}, {"c": "a1", "t": "notebooks/01_collection.ipynb"},
              {"c": "m1", "t": "notebooks/02_preprocessing.ipynb"}],
    "start": "main conține commit-ul din șablon și primul commit al echipei, README-ul. main este versiunea "
             "stabilă, cea care se predă; lucrul de zi cu zi se face pe o a doua ramură, dev.",
    "stari": [
        {"com": ["c0", "c1"], "ram": False, "aici": "m", "gh": {"m": True}, "vede": ["c1"]},
        {"com": ["c0", "c1"], "ram": True, "din": "c1", "aici": "r", "gh": {"m": True}, "vede": ["c1"]},
        {"com": ["c0", "c1"], "ram": True, "din": "c1", "aici": "r", "gh": {"m": True, "r": True}, "vede": ["c1"]},
        {"com": ["c0", "c1"], "ram": True, "din": "c1", "aici": "r", "gh": {"m": True, "r": True}, "vede": ["c1"]},
        {"com": ["c0", "c1", "a1"], "ram": True, "aici": "r", "gh": {"m": True, "r": True}, "vede": ["c1", "a1"]},
        {"com": _C5, "ram": True, "aici": "r", "gh": {"m": True, "r": True}, "vede": ["c1", "a1", "m1"]},
        {"com": _C5, "ram": True, "aici": "m", "gh": {"m": True, "r": True}, "vede": ["c1"]},
        {"com": _C5 + ["mg"], "ram": True, "aici": "m", "gh": {"m": "☁ pe GitHub, încă fără merge", "r": True},
         "vede": ["c1", "a1", "m1"]},
        {"com": _C5 + ["mg"], "ram": True, "aici": "m", "gh": {"m": True, "r": True}, "vede": ["c1", "a1", "m1"]},
    ],
    "pasi": [
        {"cine": "Andrei", "cc": "ambra", "cmd": "switch -c dev", "full": "git switch -c dev", "t": "Ramura de lucru",
         "txt": "Un singur membru creează dev, o singură dată, pornind din main. Nu se copiază nimic: apare o linie "
                "nouă de lucru, iar Andrei trece pe ea."},
        {"cine": "Andrei", "cc": "ambra", "cmd": "push -u origin dev", "full": "git push -u origin dev",
         "t": "dev, pe GitHub",
         "txt": "Ramura ajunge pe GitHub, ca să o vadă și colegii. <code>-u</code> leagă dev de origin/dev: de acum, "
                "<code>git push</code> și <code>git pull</code> știu unde merg."},
        {"cine": "Maria", "cc": "accent", "cmd": "switch dev", "full": "git fetch ; git switch dev",
         "t": "Toată echipa pe dev",
         "txt": "Ceilalți aduc noutățile de pe GitHub (<code>git fetch</code>) și trec pe dev. De aici înainte, "
                "toată echipa lucrează pe dev, iar main nu se atinge."},
        {"cine": "Andrei", "cc": "ambra", "cmd": "commit", "full": "git commit -m \"colectarea\"",
         "t": "Lucrul pe dev",
         "txt": "Fiecare lucrează în caietul pasului lui. Andrei, colectarea: <code>notebooks/01_collection.ipynb</code>. "
                "main rămâne neschimbat."},
        {"cine": "Maria", "cc": "accent", "cmd": "commit", "full": "git commit -m \"preprocesarea\"",
         "t": "Și Maria",
         "txt": "Maria, preprocesarea: <code>notebooks/02_preprocessing.ipynb</code>. Cum ajung cele două "
                "commit-uri de pe un laptop pe altul, cu pull și push: slide-ul următor."},
        {"cine": "Andrei", "cc": "ambra", "cmd": "switch main", "full": "git switch main", "t": "Sarcina e gata",
         "txt": "Colectarea și preprocesarea sunt gata, deci intră în main. Întâi trecerea pe main: din dosar "
                "dispar cele două caiete, pentru că pe main nu sunt încă. Nu s-au pierdut, sunt pe dev."},
        {"cine": "Andrei", "cc": "ambra", "cmd": "merge dev", "full": "git merge dev", "t": "Îmbinarea",
         "txt": "main primește tot ce s-a lucrat pe dev, iar caietele apar din nou în dosar. Deocamdată, doar pe calculator."},
        {"cine": "Andrei", "cc": "ambra", "cmd": "push", "full": "git push", "t": "main, pe GitHub",
         "txt": "main de pe GitHub are acum caietele: versiunea stabilă, cea care se predă. Lucrul continuă pe dev."},
    ],
}

# --------------------------------------------------------------------------
# Lucrul în echipă pe dev: doi colegi și GitHub. Fiecare coloană e git log,
# cu cel mai nou commit sus. Push refuzat: în coloana lui Andrei apare locul
# commit-ului care îi lipsește.
# --------------------------------------------------------------------------

_B = ["c1", "c0"]
_DUPA = ["mg", "m1", "a1"] + _B
SINCRON = {
    "coloane": [{"k": "an", "t": "Andrei", "d": "dev, pe laptop"},
                {"k": "gh", "t": "GitHub", "d": "origin/dev", "gh": True},
                {"k": "ma", "t": "Maria", "d": "dev, pe laptop"}],
    "autori": {"baza": {"et": "commit-urile de pe main", "c": "text-3"},
               "an": {"et": "Andrei", "c": "ambra", "cine": "Andrei"},
               "ma": {"et": "Maria", "c": "accent", "cine": "Maria"}},
    "commituri": {"c0": {"m": "din șablon", "a": "baza"},
                  "c1": {"m": "tema și întrebarea", "a": "baza"},
                  "a1": {"m": "colectarea", "a": "an"},
                  "m1": {"m": "preprocesarea", "a": "ma"},
                  "mg": {"m": "îmbinare", "a": "an", "merge": True}},
    "respins": "push respins: aici există un commit care lipsește la Andrei",
    "start": "Andrei, Maria și GitHub au același dev. Fiecare coloană arată commit-urile, cel mai nou sus.",
    "stari": [
        {"an": _B, "gh": _B, "ma": _B},
        {"an": ["a1"] + _B, "gh": _B, "ma": _B},
        {"an": ["a1"] + _B, "gh": _B, "ma": ["m1"] + _B},
        {"an": ["a1"] + _B, "gh": ["m1"] + _B, "ma": ["m1"] + _B, "din": {"gh": "ma"}, "sag": {"2": "push"}},
        {"an": ["a1"] + _B, "gh": ["m1"] + _B, "ma": ["m1"] + _B, "rau": "gh", "lipsa": {"col": "an", "id": "m1"},
         "sag": {"1": "push:rau"}},
        {"an": _DUPA, "gh": ["m1"] + _B, "ma": ["m1"] + _B, "din": {"an": "gh"}, "sag": {"1": "pull"}},
        {"an": _DUPA, "gh": _DUPA, "ma": ["m1"] + _B, "din": {"gh": "an"}, "sag": {"1": "push"}},
        {"an": _DUPA, "gh": _DUPA, "ma": _DUPA, "din": {"ma": "gh"}, "sag": {"2": "pull"}},
    ],
    "pasi": [
        {"cine": "Andrei", "cc": "ambra", "cmd": "commit", "full": "git commit -m \"colectarea\"",
         "t": "Local", "txt": "Andrei salvează caietul colectării. Commit-ul există doar pe laptopul lui."},
        {"cine": "Maria", "cc": "accent", "cmd": "commit", "full": "git commit -m \"preprocesarea\"",
         "t": "În același timp", "txt": "Maria salvează caietul preprocesării, pe laptopul ei."},
        {"cine": "Maria", "cc": "accent", "cmd": "push", "full": "git push", "t": "Maria trimite prima",
         "txt": "Commit-ul Mariei ajunge pe GitHub."},
        {"cine": "Andrei", "cc": "ambra", "cmd": "push", "rau": True,
         "full": "git push      ! [rejected]  dev -> dev (fetch first)", "t": "Refuzat",
         "txt": "GitHub are un commit pe care Andrei nu îl are: locul lui gol, în coloana lui Andrei. Git refuză "
                "push-ul, ca să nu se piardă munca Mariei."},
        {"cine": "Andrei", "cc": "ambra", "cmd": "pull", "full": "git pull", "t": "Întâi pull",
         "txt": "Andrei aduce commit-ul Mariei, iar Git le unește într-un commit de îmbinare. Caietele sunt fișiere "
                "diferite, deci nu apare niciun conflict."},
        {"cine": "Andrei", "cc": "ambra", "cmd": "push", "full": "git push", "t": "Apoi push",
         "txt": "Acum push-ul trece: GitHub are ambele caiete."},
        {"cine": "Maria", "cc": "accent", "cmd": "pull", "full": "git pull", "t": "La zi",
         "txt": "Maria aduce ce îi lipsea. Toți trei au același dev. Regula: <b>pull înainte de lucru și "
                "înainte de push</b>."},
    ],
}

# --------------------------------------------------------------------------
# Cadrul proiectului, construit factor cu factor. R² vin din modelele din
# C7 (date/modele-c7.json), estimate între țări; exemplele, din datele
# cursului: C1 (Cluj, Franța și Austria, Suceava, Dolj) și sci_nuts2.csv
# (Nord-Vest cu Észak-Alföld, 42.688, și cu Lombardia, 9.760).
# --------------------------------------------------------------------------

_MOD = json.loads((RAD / "date" / "modele-c7.json").read_text(encoding="utf-8"))
_R1, _R3, _R4 = (_MOD[k]["r2"] for k in ("M1", "M3", "M4"))
_pct = lambda x: f"{x * 100:.0f}"

CADRU = {
    "intrebare": "Cât din legătura dintre două locuri se explică prin oamenii care au migrat între ele?",
    "start": "De explicat este legătura dintre două locuri, măsurată prin SCI. Factorii se adaugă pe rând, "
             "ca în modelul din C7.",
    "rezultat": {"t": "legătura dintre două locuri", "d": "SCI"},
    "factori": [
        {"k": "dist", "t": "Distanța", "semn": "−",
         "ip": "Cu cât locurile sunt mai departe, cu atât legătura este mai slabă.",
         "dece": "Prieteniile se leagă mai ales față în față: la școală, la muncă, între vecini.",
         "date": [["distanța, în km", "GISCO"], ["granița comună", "GISCO"]],
         "ex": "Primii parteneri ai Clujului sunt vecinii lui, Sălajul și Bistrița-Năsăud. "
               "Granița adaugă foarte puțin peste distanță și migrație.",
         "lit": "Bailey și colegii (2018)"},
        {"k": "migr", "t": "Migrația", "semn": "+",
         "ip": "Cu cât o parte mai mare din populația unui loc vine din celălalt, cu atât legătura este "
               "mai puternică.",
         "dece": "Cei plecați păstrează prieteniile de acasă și îi ajută pe cei care pleacă după ei.",
         "date": [["migranți la 1.000 de locuitori", "Eurostat, migr_pop1ctz"]],
         "ex": "Franța și Austria au aproape același număr de români, dar SCI-ul cu Austria este de 6,9 ori "
               "mai mare: acolo, un locuitor din 60 este român; în Franța, unul din 426.",
         "lit": "Palloni și colegii (2001); de Haas (2010); Sandu (2005, 2025)"},
        {"k": "ist", "t": "Istoria comună", "semn": "+",
         "ip": "Minoritățile și granițele vechi păstrează legături pe care migrația recentă nu le explică.",
         "dece": "Familiile și comunitățile despărțite de o graniță rămân conectate.",
         "date": [["limba, minoritățile, granițele vechi", "surse alese de echipă"]],
         "ex": "Cel mai puternic partener din afara țării al regiunii Nord-Vest este Észak-Alföld, peste "
               "graniță, în Ungaria: SCI 42.688, față de 9.760 cu Lombardia.",
         "lit": "Bailey și colegii (2020)"},
        {"k": "loc", "t": "Locurile", "semn": "+",
         "ip": "Orașele mari, bogate și universitare au legături mai întinse.",
         "dece": "Studiile, munca și turismul aduc oameni din locuri îndepărtate.",
         "date": [["populația, densitatea, PIB pe locuitor", "Eurostat"]],
         "ex": "Ipoteză de verificat: are Bucureștiul parteneri mai îndepărtați decât un județ rural?"},
    ],
    "rest": {"k": "rest", "t": "Ce rămâne",
             "ip": "Legăturile mai puternice sau mai slabe decât prezic factorii măsurați.",
             "dece": "Aici se caută istoria, locurile și explicațiile pe care încă nu le are nimeni.",
             "ex": "Suceava și Turnhout, în Belgia; Doljul și Huelva, în Spania: legături concentrate pe "
                   "o singură destinație.",
             "lit": "De aici pornește întrebarea fiecărei echipe."},
    "bara": {"titlu": "Între țări, în modelul din C7 (263 de perechi): cât din variația SCI explică factorii măsurați",
             "seg": [{"k": "dist", "v": round(_R1 * 100, 2), "et": f"distanța {_pct(_R1)} %", "de": 1},
                     {"k": "migr", "v": round((_R3 - _R1) * 100, 2), "et": f"migrația +{_pct(_R3 - _R1)} %", "de": 2},
                     {"k": "rest", "v": round((1 - _R4) * 100, 2), "et": f"ce rămâne {_pct(1 - _R4)} %", "de": 3}],
             "note": ["",
                      f"Doar distanța explică {_pct(_R1)} % din variația SCI între țări.",
                      f"Cu migranții la mie, {_pct(_R3)} %. Granița mai adaugă sub un punct.",
                      f"Istoria nu are încă o variabilă în model: se caută în cei {_pct(1 - _R4)} % rămași.",
                      f"Nici locurile nu intră în modelul din C7: se verifică tot în cei {_pct(1 - _R4)} %.",
                      "Aproape jumătate din variație rămâne de explicat: aici intră întrebările echipelor."]},
}

# --------------------------------------------------------------------------
# Datele proiectului după caietul 03: patru tabele în data/c3. Numărul de
# rânduri și rândurile-exemplu vin din rularea caietului (31 octombrie 2026).
# --------------------------------------------------------------------------

TABELE = {
    "tabele": [
        {"f": "sci_nuts2.csv", "tag": "legăturile", "c": "text-2", "n": 88804,
         "col": ["tara_1", "tara_2", "regiune_1", "regiune_2", "sci"],
         "rows": [["RO", "HU", "RO11", "HU32", 42688], ["RO", "IT", "RO11", "ITC4", 9760]],
         "leg": {"tara_1": "tara", "tara_2": "tara", "regiune_1": "reg", "regiune_2": "reg"},
         "rand": "o pereche de regiuni NUTS 2 și SCI-ul ei.",
         "nota": "298 × 298: fiecare regiune cu fiecare, în ambele ordini."},
        {"f": "migratie.csv", "tag": "migrația", "c": "accent", "n": 9900,
         "col": ["tara_rezidenta", "cetatenie", "persoane"],
         "rows": [["IT", "RO", 1073196], ["DE", "RO", 776424]],
         "leg": {"tara_rezidenta": "tara", "cetatenie": "tara"},
         "rand": "câți cetățeni ai unei țări trăiesc în altă țară.",
         "nota": "Fără grupurile de țări; <code>NA</code> este Namibia. Doar 4.422 de rânduri au valoare."},
        {"f": "regional.csv", "tag": "locurile", "c": "ardezie", "n": 5543,
         "col": ["regiune", "valoare", "indicator", "nivel"],
         "rows": [["RO113", 693507, "populatie", 3], ["RO113", 44800, "pib_locuitor", 3]],
         "leg": {"regiune": "reg"},
         "rand": "un indicator pentru o regiune.",
         "nota": "Șase fișiere din C2, puse unul sub altul: format lung."},
        {"f": "nuts.csv", "tag": "nomenclatorul", "c": "text-3", "n": 1971,
         "col": ["regiune", "tara", "denumire", "nivel"],
         "rows": [["RO11", "RO", "Nord-Vest", 2], ["RO113", "RO", "Cluj", 3]],
         "leg": {"regiune": "reg", "tara": "tara"},
         "rand": "o regiune, cu numele ei.",
         "nota": "Lungimea codului dă nivelul: 2 caractere țara, 4 regiunea, 5 județul."},
    ],
    "leg": "Coloanele cu același fel de cod se aprind împreună la trecerea mouse-ului: după ele se unesc "
           "tabelele la cursul 4.",
}

# --------------------------------------------------------------------------
# Verificarea depozitului: comenzile folosite la curs (status, log) și o
# privire pe GitHub. Toate merg la fel în PowerShell și în Git Bash.
# --------------------------------------------------------------------------

DOVADA = {
    "id": "c3-dovada-depozit",
    "sarcina": "După primul commit (caietul 03, secțiunea 7.3): trei comenzi în terminal, în <code>proiect/</code>, "
               "și o adresă de pe GitHub. Rezultatul fiecăreia se lipește în câmpul ei.",
    "indiciu": "Terminalul trebuie să fie în dosarul <code>proiect</code>: promptul se termină cu "
               "<code>proiect</code>, iar Git Bash arată și ramura, <code>(main)</code>. Altfel: <code>cd proiect</code>.",
    "pasi": [
        {"t": "La zi cu GitHub", "cmd": "git status", "gol": "primele două rânduri",
         "cauta": r"branch\s*(main|dev)[\s\S]*origin/(main|dev)",
         "ind": "Se copiază primele două rânduri: <code>On branch main</code> și "
                "<code>Your branch is up to date with 'origin/main'.</code>",
         "daca_nu": "Rezultatul trebuie să conțină ramura și perechea ei de pe GitHub, de exemplu main și "
                    "origin/main. Fără origin/, dosarul nu este clonat din repo-ul echipei."},
        {"t": "Commit-ul a ajuns pe GitHub", "cmd": "git log --oneline -3", "gol": "liniile afișate",
         "cauta": r"^(?:[^\n]*git log[^\n]*\n)?\s*[0-9a-f]{7,}[^\n]*origin/(main|dev)",
         "ind": "Se copiază rândul de sus: codul scurt al commit-ului, apoi "
                "<code>(HEAD -&gt; main, origin/main)</code> și mesajul.",
         "daca_nu": "Pe rândul ultimului commit trebuie să apară origin/main. Dacă lipsește, commit-ul este "
                    "doar local: git pull, apoi git push."},
        {"t": "Depozitul echipei", "cmd": "git remote -v", "gol": "cele două rânduri cu origin",
         "cauta": r"github\.com[/:]dsw-ubb-2026/echipa-\d+",
         "ind": "Două rânduri care încep cu <code>origin</code>, cu adresa repo-ului echipei: "
                "<code>https://github.com/dsw-ubb-2026/echipa-N.git</code>.",
         "daca_nu": "Adresa trebuie să fie a repo-ului echipei din dsw-ubb-2026. Altă adresă: dosarul nu este "
                    "clona repo-ului echipei; clonarea se reface din dsw."},
        {"t": "Commit-ul, pe GitHub",
         "unde": "Pagina depozitului <b>›</b> Commits <b>›</b> commit-ul propriu <b>›</b> adresa din bara browserului",
         "gol": "https://github.com/dsw-ubb-2026/…/commit/…",
         "cauta": r"github\.com/dsw-ubb-2026/[^/\s]+/commit/[0-9a-f]{7,40}",
         "ind": "Pe pagina repo-ului, deasupra listei de fișiere: <b>Commits</b> (iconița cu ceas). Clic pe "
                "mesajul commit-ului propriu; adresa se termină cu <code>/commit/</code> și un cod lung.",
         "daca_nu": "Adresa trebuie să fie a unui commit din organizația dsw-ubb-2026."},
    ],
    "explicatie": "Munca există acum în două locuri, local și pe GitHub. Pe pagina commit-ului se văd autorul, "
                  "fișierele schimbate și rândurile modificate. Dacă lângă commit apare un nume fără cont de "
                  "GitHub, adresa de email din Git nu este cea a contului: "
                  "<code>git config --global user.email \"adresa contului\"</code>; commit-urile următoare "
                  "apar apoi pe cont.",
}

PAS_TARI = {
    "fisier": "03_surse_diverse.ipynb · 5. Migrația: țări și grupuri de țări",
    "intro": "Prima decizie de curățare din caietul 03. Eurostat raportează în aceeași coloană țări și grupuri de țări, care trebuie separate.",
    "cod": "migratie = pd.read_csv(\"data/c2/migratie.csv\",\n"
           "                       keep_default_na=False, na_values=[\"\"])\n"
           "migratie[\"citizen\"].unique()\n\n"
           "cetatenie_tara = migratie[\"citizen\"].str.len() == 2\n"
           "rezidenta_tara = migratie[\"geo\"].str.len() == 2\n"
           "migratie = migratie[cetatenie_tara & rezidenta_tara]\n\n"
           "migratie = migratie[migratie[\"citizen\"] != migratie[\"geo\"]]\n"
           "migratie = migratie[[\"geo\", \"citizen\", \"valoare\"]]\n"
           "migratie.columns = [\"tara_rezidenta\", \"cetatenie\", \"persoane\"]\n\n"
           "romani = migratie[migratie[\"cetatenie\"] == \"RO\"]\n"
           "romani.sort_values(\"persoane\", ascending=False).head(10)",
    "pasi": [
        {"l": 1, "set": {"migratie": {"t": "DataFrame", "v": {"cols": ["citizen", "valoare", "geo"],
            "rows": [["RO", 1073196, "IT"], ["TOTAL", "…", "IT"], ["IT", "…", "IT"], ["EU27_2020_FOR", "…", "DE"], ["…", "…", "…"]],
            "nota": "țări și grupuri de țări, amestecate"}}},
         "txt": "<code>keep_default_na=False</code>: <code>NA</code> este codul Namibiei, nu o valoare lipsă. Doar celulele goale sunt tratate ca valori lipsă."},
        {"l": 3, "out": "array([..., 'RO', 'RS', 'RU', ..., 'EU27_2020_FOR', 'FOR', 'NAT', 'TOTAL'], dtype=object)",
         "txt": "<code>unique()</code> afișează valorile distincte. Printre țări apar și grupuri: străinii din UE, toți străinii, cetățenii proprii, totalul. Dacă nu sunt eliminate, aceiași oameni sunt numărați de mai multe ori."},
        {"l": 5, "set": {"cetatenie_tara": {"t": "Series", "v": {"rows": [["0", "True"], ["1", "False"], ["2", "True"], ["3", "False"], ["…", "…"]],
            "nota": "True unde cetățenia are două litere"}}},
         "txt": "Codurile de țară au exact două litere. <code>.str.len()</code> măsoară lungimea textului, iar comparația dă True sau False pe fiecare rând."},
        {"l": 6, "set": {"rezidenta_tara": {"t": "Series", "v": {"rows": [["0", "True"], ["1", "True"], ["2", "True"], ["3", "True"], ["…", "…"]],
            "nota": "True unde țara de rezidență are două litere"}}},
         "txt": "Aceeași verificare pentru țara de rezidență: în <code>geo</code> apare și <code>EU27_2020</code>, totalul Uniunii."},
        {"l": 7, "set": {"migratie": {"t": "DataFrame", "v": {"cols": ["citizen", "valoare", "geo"],
            "rows": [["RO", 1073196, "IT"], ["IT", "…", "IT"], ["…", "…", "…"]], "nota": "doar țări"}}},
         "txt": "<code>&</code> cere ca <b>ambele</b> condiții să fie adevărate. Grupurile au fost eliminate; rămân însă rândurile în care cetățenia coincide cu țara, de exemplu italienii din Italia."},
        {"l": 9, "set": {"migratie": {"t": "DataFrame", "v": {"cols": ["citizen", "valoare", "geo"],
            "rows": [["RO", 1073196, "IT"], ["…", "…", "…"]], "nota": "fără cetățenii propriei țări"}}},
         "txt": "<code>!=</code> păstrează rândurile în care cetățenia diferă de țara de rezidență. Românii din România nu sunt migranți."},
        {"l": 11, "set": {"migratie": {"t": "DataFrame", "v": {"cols": ["tara_rezidenta", "cetatenie", "persoane"],
            "rows": [["IT", "RO", 1073196], ["DE", "RO", 776424], ["DE", "IT", 571379], ["…", "…", "…"]],
            "nota": "un rând = câte persoane cu o cetățenie trăiesc într-o țară"}}},
         "txt": "Trei coloane, în ordinea dorită, cu nume care spun ce conțin. Peste o lună, <code>tara_rezidenta</code> rămâne inteligibil; <code>geo</code> nu."},
        {"l": 13, "set": {"romani": {"t": "DataFrame", "v": {"cols": ["tara_rezidenta", "cetatenie", "persoane"],
            "rows": [["IT", "RO", 1073196], ["DE", "RO", 776424], ["ES", "RO", 620463], ["…", "…", "…"]], "nota": "românii, după țara în care trăiesc"}}},
         "txt": "Filtrul din C1, aplicat pe tabelul curățat."},
        {"l": 14, "out": "tara_rezidenta  persoane\nIT              1073196\nDE               776424\nES               620463\nFR               161220\nAT               153427\nBE               127539\nNL                52265\nIE                48220\nSE                21442\nPT                19692",
         "txt": "Italia, Germania, Spania. În C1, după SCI, Italia era abia pe locul șase. Acum sunt disponibile ambele surse ale comparației: conectivitatea socială și migrația."},
    ],
}


# Caietul 03, secțiunea 3: șase fișiere din C2, un singur tabel.
# Cifrele: rularea caietului pe fișierele din data/c2 (31 octombrie 2026).

PAS_NUTS = {
    "fisier": "03_surse_diverse.ipynb · 3. Indicatorii într-un singur tabel",
    "intro": "Din C2 provin șase fișiere: trei indicatori pe două niveluri, fiecare cu un rând pe regiune. O funcție mică citește un fișier și notează de unde vine; apoi toate șase se pun unul sub altul.",
    "cod": "def citeste(indicator, nivel):\n"
           "    tabel = pd.read_csv(f\"data/c2/{indicator}_nuts{nivel}.csv\")\n"
           "    tabel[\"indicator\"] = indicator\n"
           "    tabel[\"nivel\"] = nivel\n"
           "    tabel = tabel.rename(columns={\"geo\": \"regiune\"})\n"
           "    return tabel\n\n"
           "tabele = [citeste(\"populatie\", 2), citeste(\"populatie\", 3),\n"
           "          citeste(\"densitate\", 2), citeste(\"densitate\", 3),\n"
           "          citeste(\"pib_locuitor\", 2), citeste(\"pib_locuitor\", 3)]\n"
           "regional = pd.concat(tabele)\n"
           "regional[regional[\"regiune\"] == \"RO113\"]\n\n"
           "regional.groupby([\"nivel\", \"indicator\"])[\"valoare\"].agg([\"size\", \"count\"])",
    "pasi": [
        {"l": 1,
         "txt": "<code>def</code> definește funcția: pașii pentru un singur fișier. Deocamdată nu se citește nimic; pașii rulează la fiecare apel."},
        {"l": 2, "set": {"tabel": {"t": "DataFrame", "v": {"cols": ["geo", "valoare"],
            "rows": [["BE10", 1264371], ["BE21", 1932876], ["…", "…"]], "nota": "primul apel: populația, NUTS 2"}}},
         "txt": "La primul apel, <code>indicator</code> este <code>\"populatie\"</code> și <code>nivel</code> este 2, deci adresa devine <code>data/c2/populatie_nuts2.csv</code>. Fișierul are două coloane: regiunea și valoarea."},
        {"l": 4, "set": {"tabel": {"t": "DataFrame", "v": {"cols": ["geo", "valoare", "indicator", "nivel"],
            "rows": [["BE10", 1264371, "populatie", 2], ["BE21", 1932876, "populatie", 2], ["…", "…", "…", "…"]]}}},
         "txt": "Două coloane noi spun de unde vine fiecare rând. Fără ele, după lipire nu s-ar mai putea deosebi populația de densitate."},
        {"l": 5, "set": {"tabel": {"t": "DataFrame", "v": {"cols": ["regiune", "valoare", "indicator", "nivel"],
            "rows": [["BE10", 1264371, "populatie", 2], ["…", "…", "…", "…"]]}}},
         "txt": "<code>geo</code> devine <code>regiune</code>, același nume ca în nomenclatorul NUTS, ca în C4 tabelele să se poată uni."},
        {"l": 8, "set": {"tabele": {"t": "list", "v": ["populatie · 2", "populatie · 3", "densitate · 2", "densitate · 3", "pib_locuitor · 2", "pib_locuitor · 3"]}},
         "sterge": ["tabel"],
         "txt": "Șase apeluri, șase tabele, într-o listă (aici, doar numele lor). <code>tabel</code> a existat doar în interiorul funcției."},
        {"l": 11, "set": {"regional": {"t": "DataFrame", "v": {"cols": ["regiune", "valoare", "indicator", "nivel"],
            "rows": [["BE10", 1264371, "populatie", 2], ["…", "…", "…", "…"], ["RO113", 104.8, "densitate", 3], ["…", "…", "…", "…"]],
            "nota": "un singur tabel lung, din șase fișiere"}}},
         "txt": "<code>pd.concat</code> așază tabelele unul sub altul, ca la Banca Mondială în C2."},
        {"l": 12, "out": "regiune   valoare     indicator\nRO113   693507.0     populatie\nRO113      104.8     densitate\nRO113    44800.0  pib_locuitor",
         "txt": "Clujul apare de trei ori, câte un rând pe indicator: tabelul este în format <b>lung</b>. În C4 devine lat, cu un rând pe regiune."},
        {"l": 14, "out": "                    size  count\nnivel indicator\n2     densitate      340    285\n      pib_locuitor   309    276\n      populatie      350    292\n3     densitate     1580   1279\n      pib_locuitor  1343    524\n      populatie     1621   1326",
         "txt": "<code>size</code> numără rândurile, <code>count</code> doar valorile prezente. Diferența reprezintă valorile lipsă: PIB-ul pe județ are valori doar pentru 524 din 1.343 de rânduri. Tratarea lor se decide în C4."},
    ],
}


# ===========================================================================
#  3-5. Ce face Git
# ===========================================================================

CE_FACE = [
    ("Înregistrează fiecare schimbare", "istoric",
     "Nu doar ultima versiune, ci toate, cu autorul și data fiecărei schimbări."),
    ("Permite revenirea", "reveniri",
     "La orice versiune anterioară, fără pierderea stării curente."),
    ("Permite lucrul în paralel", "colaborare",
     "Mai multe persoane lucrează pe aceleași fișiere, iar Git îmbină apoi modificările."),
    ("Păstrează totul în dosarul proiectului", "un singur loc",
     "Întreaga istorie se află în subdosarul <code>.git</code>, nu într-un serviciu extern."),
    ("Izolează experimentele", "ramuri",
     "Modificările experimentale se fac pe o ramură separată, iar codul principal rămâne neatins."),
    ("Funcționează local", "fără internet",
     "Git nu necesită conexiune la internet. GitHub este doar locul de sincronizare."),
]

FUNCTII = ('<ol class="fn6">' + "".join(
    f'<li><span class="fn6__n">{i:02d}</span><div><b>{n}</b><em>{u}</em><p>{d}</p></div></li>'
    for i, (n, u, d) in enumerate(CE_FACE, 1)) + "</ol>")


GIT_GITHUB = ('<div class="doi2">'
   '<div><b>Git</b><span>program instalat pe calculator</span>'
   '<ul><li>păstrează istoricul proiectului</li><li>funcționează fără internet</li>'
   '<li>se folosește din terminal</li></ul></div>'
   '<div><b>GitHub</b><span>platformă online</span>'
   '<ul><li>găzduiește depozitele, ca o copie independentă de calculator</li>'
   '<li>spațiul comun al echipei, fără arhive trimise prin email</li>'
   '<li>arată cine ce a făcut și când</li></ul></div>'
   '</div>')
EVALUARE = nota("Evaluarea proiectului",
                "Proiectul se evaluează pe baza depozitului: întregul parcurs, nu doar "
                "rezultatul final. Un singur commit în ziua predării nu documentează acest parcurs.")


# ===========================================================================
#  Depozitul echipei
# ===========================================================================

# Depozitul echipei: pașii și dosarul, în manualul slide-ului „Depozitul echipei”.
ARBORE_PROIECT = (
    '<span class="a">dsw/</span>\n'
    '├── <span class="x">.venv/</span>\n'
    '├── curs/                 <span class="c"># caietele cursului și src/date_api.py, fără Git</span>\n'
    '└── <span class="a">proiect/</span>              <span class="c"># depozitul echipei, cu Git</span>\n'
    '    ├── data/raw/         <span class="c"># datele originale, neschimbate</span>\n'
    '    ├── data/processed/   <span class="c"># tabelele produse de caiete</span>\n'
    '    ├── notebooks/        <span class="c"># câte un caiet pe pas</span>\n'
    '    ├── src/              <span class="c"># cod comun, în fișiere .py</span>\n'
    '    ├── figures/          <span class="c"># figurile pentru raport</span>\n'
    '    ├── docs/             <span class="c"># raportul</span>\n'
    '    └── README.md         <span class="c"># descrierea proiectului</span>')

PE4_HTML = (
    '<ol class="pe4">'
    f'<li><span>1</span><b>Organizația</b><p><a class="leg" href="https://github.com/{REPO_ORG}" target="_blank" rel="noopener">{REPO_ORG}</a>, comună pentru grupă.</p></li>'
    "<li><span>2</span><b>Invitația</b><p>Pentru <code>echipa-N</code>, pe e-mailul contului GitHub sau la <code>github.com/dsw-ubb-2026/echipa-N/invitations</code>.</p></li>"
    "<li><span>3</span><b>Adresa</b><p>Pe pagina repo-ului: Code → HTTPS.</p></li>"
    "<li><span>4</span><b>Clonarea</b><p>În terminal, în dsw: <code>git clone &lt;adresa&gt; proiect</code></p></li>"
    "</ol>"
    '<div class="pe4__arb"><pre><code>' + ARBORE_PROIECT + "</code></pre>"
    '<p>Munca echipei stă în proiect/, cu Git; caietele și datele de la curs rămân în curs/, fără Git.</p></div>')

CONFIG = {
    "id": "c3-cod-config", "poarta": False, "fisier": "terminal.sh",
    "indiciu": "Opțiunea care face setarea valabilă pe tot calculatorul este „global”, precedată de două cratime. "
               "Adresa este cea a contului de GitHub, scrisă între ghilimele.",
    "iesire": "user.name=Numele Tau\nuser.email=nume@stud.ubbcluj.ro\ncore.autocrlf=true",
    "sarcina": "Ce lipsește din comenzile de configurare și de verificare?",
    "cod": "# ce stie Git deja despre autor\n"
           "git config user.name\ngit config user.email\n\n"
           "# pentru tot calculatorul, nu doar pentru acest proiect\n"
           "git config {{1}} user.name \"Numele Tau\"\n"
           "git config {{1}} user.email {{2}}\n\n"
           "# tot ce s-a setat\n"
           "git config --list",
    "goluri": {
        "1": {"ok": ["--global"], "ajutor": "opțiunea"},
        "2": {"ok": ["\"adresa@exemplu.com\"", "'adresa@exemplu.com'",
                     "\"nume@stud.ubbcluj.ro\"", "\"adresa@ta.ro\""],
              "re": "^[\"'][^\"'\\s]+@[^\"'\\s]+\\.[a-z]{2,}[\"']$",
              "ajutor": "adresa de email, în ghilimele"}},
    "laBine": "Adresa trebuie să fie cea asociată contului de GitHub; altfel commit-urile nu sunt legate de profilul respectiv.",
    "laRau": "Opțiunea începe cu două cratime. Adresa se scrie între ghilimele.",
    "explicatie": "<code>--global</code> scrie în configurarea utilizatorului, deci setarea este valabilă pentru "
                  "toate proiectele. Fără această opțiune, setarea se aplică doar depozitului curent."}



# ===========================================================================
#  14-16. În echipă
# ===========================================================================


FLUX_DEV = [
    ["o dată, un membru al echipei", "~git switch -c dev", "~git push -u origin dev"],
    ["o dată, ceilalți", "~git fetch", "~git switch dev"],
    ["zilnic, fiecare", "~git switch dev", "~git pull"],
    ["la fiecare commit", "~git add . ; git commit -m \"...\"", "~git pull ; git push"],
    ["după o sarcină importantă", "~git switch main ; git pull", "~git merge dev ; git push"],
]


# ===========================================================================
#  17-20. Încadrarea teoretică
# ===========================================================================

CAUTARE = {
    "id": "c3-ordine-literatura", "poarta": False,
    "sarcina": "În ce ordine se desfășoară căutarea literaturii pentru întrebarea echipei?",
    "linii": [
        "căutarea pornește de la un articol-ancoră: Bailey și colegii (2018)",
        "căutarea înapoi: din referințele lui se selectează ce ține de întrebarea echipei",
        "căutarea înainte: „Citat de” arată lucrările mai noi",
        "se caută în engleză, cu termenii din titluri și coridorul studiat",
        "se citesc rezumatul și metoda, apoi se decide",
        "lucrarea se notează pe un rând din matricea literaturii"],
    "indiciu": "Întâi este necesar un punct de plecare sigur; abia apoi căutarea se lărgește, iar la final lucrările se notează.",
    "laBine": "Căutarea pornește de la o sursă de încredere și se extinde sistematic, nu la întâmplare.",
    "explicatie": "Un articol-ancoră bun evită căutarea nesistematică: referințele lui acoperă literatura "
                  "anterioară, iar citările, cercetarea ulterioară. Din matricea de la final se scrie "
                  "secțiunea de cadru teoretic a raportului."}

TIPURI_LIT = tabel(["Tipul", "La ce răspunde", "Când intră în flux", "În proiectul cursului"], [
    ["<strong>Teoria</strong>", "mecanismele care explică fenomenul: concepte și ipoteze", "la definirea întrebării", "rețelele de migranți, câmpurile de migrație"],
    ["<strong>Metoda</strong>", "cum au fost măsurate conceptele și ce modele s-au folosit", "la analiză și la model", "log SCI explicat prin distanță și graniță"],
    ["<strong>Documentația</strong>", "cum se folosește corect fiecare sursă și unealtă", "la fiecare pas de cod", "API-ul Eurostat, pandas, networkx"],
    ["<strong>Datele</strong>", "proveniența datelor și ce măsoară fiecare variabilă", "oriunde sunt folosite", "articolul care descrie SCI 2026"],
])


FACTORI_TAB = tabel(["Factorul", "Ipoteza", "Variabila", "Sursa"], [
    ["Distanța", "mai departe, legătură mai slabă", "distanța în km, granița comună", "GISCO; construite în C7"],
    ["Migrația", "mai mulți migranți la mie, legătură mai puternică", "migranți la 1.000 de locuitori", "Eurostat <code>migr_pop1ctz</code>; C2-C4"],
    ["Istoria comună", "minoritățile și granițele vechi păstrează legături", "limba, minoritățile, granițele vechi", "surse noi, alese de echipă"],
    ["Locurile", "orașele mari și bogate au legături mai întinse", "populația, densitatea, PIB pe locuitor", "Eurostat; C2-C3"],
])


# ===========================================================================
#  Datele și proiectul
# ===========================================================================

EXPLORARE = {
    "id": "c3-cod-explorare", "poarta": False,
    "indiciu": "Dimensiunea tabelului este un atribut (fără paranteze), numit „formă” în engleză. Rezumatul pe coloane este metoda „informații”. Valorile lipsă se însumează cu metoda „sumă”.",
    "iesire": "(12915, 8)\n<class 'pandas.core.frame.DataFrame'>\nRangeIndex: 12915 entries, 0 to 12914\n...\n"
              "citizen      45\n...\nvaloare    7564", "fisier": "explorare.py",
    "sarcina": "Ce lipsește din primele patru operații aplicate unui tabel nou?",
    "cod": "import pandas as pd\n\n"
           "migratie = pd.read_csv(\"data/c2/migratie.csv\")\n\n"
           "# cate randuri si cate coloane\nprint(migratie.{{1}})\n\n"
           "# ce coloane, ce tipuri, cate valori lipsesc\nmigratie.{{2}}()\n\n"
           "# cum arata primele randuri\nprint(migratie.head())\n\n"
           "# cate valori lipsesc, pe coloana\nprint(migratie.isna().{{3}}())",
    "goluri": {
        "1": {"ok": ["shape"], "ajutor": "atributul"},
        "2": {"ok": ["info"], "ajutor": "metoda"},
        "3": {"ok": ["sum"], "ajutor": "metoda"}},
    "laBine": "<code>citizen</code> are 45 de valori lipsă: este codul Namibiei, <code>NA</code>, citit ca "
              "valoare lipsă. De aceea caietul citește fișierul cu <code>keep_default_na=False</code>.",
    "laRau": "Prima este un atribut, deci se scrie fără paranteze. Celelalte sunt metode.",
    "explicatie": "<code>info()</code> este cea mai informativă: afișează simultan "
                  "numărul de rânduri, tipurile coloanelor și numărul de valori "
                  "nenule din fiecare. O coloană care ar trebui să fie "
                  "numerică, dar apare ca <code>object</code>, semnalează o "
                  "problemă încă de la început."}


# ===========================================================================
#  Slide-urile, în ordinea lecției: Git, depozitul echipei, lucrul în echipă,
#  verificarea, cadrul teoretic, datele.
# ===========================================================================

sl("s1", "Cursul", "Planul lecției",
   "<h2>Versionare și colaborare cu Git</h2>"
   "<p class=\"cheie\">Datele colectate la cursul anterior intră acum, "
   "împreună cu codul de colectare, sub controlul versiunilor.</p>"
   + ix("agenda", "Planul lecției",
        {"static": True, "titlu": "Planul lecției",
         "etape": [{"nume": n, "unde": u, "text": d} for n, u, d in AGENDA]},
        "Detaliile apar la selectarea unei etape.")
   + nota("Caietul lecției", "<code>03_surse_diverse_si_preprocesare.ipynb</code>. Secțiunile 1-6 pregătesc datele (funcțiile în <code>src/date_api.py</code>, nomenclatorul, indicatorii, SCI, migrația și zborurile), iar secțiunea 7, depozitul echipei.", True),
   manual=
   "<h2>Versionare și colaborare cu Git</h2>"
   "<p>Lecția de azi are două părți, aparent fără legătură. Prima "
   "tratează Git, adică mecanismul prin care un proiect își păstrează propria "
   "istorie. A doua este dedicată formulării întrebării de cercetare a proiectului.</p>"
   "<p>Legătura dintre ele: un proiect de analiză nu este o colecție de "
   "fișiere, ci un parcurs. Git documentează parcursul, iar cadrul teoretic "
   "îi stabilește direcția. Fără primul, rezultatul nu poate fi reconstituit; "
   "fără al doilea, nu poate fi justificat.</p>"
   "<h3>Punctul de plecare</h3>"
   '<ul class="bif">'
   "<li><b>Colectarea</b><span>cererile către Banca Mondială și Eurostat, în caietul 02.</span></li>"
   "<li><b>Datele</b><span><code>bm.csv</code> și <code>migratie.csv</code>, în <code>curs/data/c2</code>.</span></li>"
   "<li><b>Echipa</b><span>aleasă pe site; repo-ul ei, <code>echipa-N</code>, există deja pe GitHub, creat din șablonul cursului.</span></li>"
   "</ul>"
   "<p>Deocamdată, toate există doar pe calculatorul local. Git le păstrează istoricul, "
   "iar GitHub le pune în comun pentru echipă.</p>"
   + ix("agenda", "Planul lecției",
        {"static": True, "titlu": "Planul lecției",
         "etape": [{"nume": n, "unde": u, "text": d} for n, u, d in AGENDA]})
   + nota("Caietul lecției", "<code>03_surse_diverse_si_preprocesare.ipynb</code>. Secțiunile 1-6 pregătesc datele (funcțiile în <code>src/date_api.py</code>, nomenclatorul, indicatorii, SCI, migrația și zborurile), iar secțiunea 7, depozitul echipei.", True))

sl("s3", "Ce face Git", "De ce Git",
   "<h2>Ce face Git</h2>"
   "<p class=\"cheie\">Git rulează pe calculatorul local. GitHub este doar "
   "platforma pe care se sincronizează proiectele.</p>"
   + FUNCTII,
   manual=
   "<h2>Ce face Git</h2>"
   "<p>Un sistem de versionare rezolvă o problemă frecventă: fișiere numite "
   "<code>analiza_final_v2_FINAL_bun.py</code>, fără nicio evidență a "
   "diferențelor față de <code>v1</code>.</p>"
   + FUNCTII
   + nota("O distincție esențială",
          "Git și GitHub nu sunt același lucru. Git este programul instalat "
          "local, care păstrează istoria. GitHub este o platformă care "
          "găzduiește copii ale acestei istorii. Git poate fi folosit fără "
          "GitHub; invers, nu."))

sl("s5", "Ce face Git", "Git și GitHub",
   "<h2>Git și GitHub</h2>"
   "<p class=\"cheie\">Două unelte diferite: una ține istoricul, cealaltă îl pune în comun.</p>"
   + GIT_GITHUB + EVALUARE,
   manual=
   "<h2>Git și GitHub</h2>"
   "<p>Două unelte diferite: una ține istoricul, cealaltă îl pune în comun.</p>"
   + GIT_GITHUB
   + nota("Evaluarea proiectului",
          "Proiectul se evaluează pe baza depozitului: nu doar rezultatul "
          "final, ci întregul parcurs (ce s-a încercat, ce s-a abandonat, cine "
          "a contribuit). Un depozit cu un singur commit în ziua predării nu "
          "documentează acest parcurs.")
   + "<h3>Depozitul (repository)</h3>"
   "<p>Un depozit (repository, pe scurt repo) este un dosar obișnuit în care "
   "Git a creat un subdosar ascuns, <code>.git</code>. Acolo se păstrează "
   "întreaga istorie.</p>"
   + tabel(["Local", "Remote"], [
       ["pe calculatorul local", "pe GitHub"],
       ["locul de lucru", "locul de sincronizare al echipei"],
       ["se copiază de pe GitHub cu <code>git clone</code>", "la curs, creat din șablonul cursului"],
   ])
   + "<p>La curs, repo-ul de pe GitHub există deja pentru fiecare echipă; copia locală se face "
     "la pasul următor, cu <code>git clone</code>.</p>")

sl("s4", "Ce face Git", "Cele trei zone",
   "<h2>Cele trei zone, și GitHub</h2>"
   + ix("zone", "Fișierele prin cele trei zone", ZONE),
   manual="<h2>Cele trei zone</h2>"
   "<p>Acesta este modelul conceptual care dă sens comenzilor Git. Fără el, "
   "comenzile rămân o listă de proceduri memorate, fără o logică comună.</p>"
   + "<p>Fiecare comandă mută ceva dintr-o zonă în următoarea, iar săgeata dintre zone poartă numele "
     "comenzii. Terminalul de sub desen răspunde ca Git, inclusiv când o comandă vine prea devreme: "
     "<code>git commit</code> fără nimic în pregătire primește „nothing added to commit”.</p>"
   + ix("zone", "Fișierele prin cele trei zone", ZONE)
   + tabel(["Zona", "Ce conține", "Cum ajunge mai departe"], [
       ["Dosarul de lucru", "fișierele în curs de editare", "~git add"],
       ["Zona de pregătire", "modificările alese pentru următorul commit", "~git commit"],
       ["Istoricul local", "commit-urile, pe calculatorul local", "~git push"],
       ["GitHub", "copia de pe server", "~git pull, înapoi"],
   ])
   + "<p>Zona de pregătire poate părea un pas redundant. Rolul ei este de a "
     "permite un commit care include doar trei din cele șapte fișiere "
     "modificate, atunci când numai cele trei țin de aceeași schimbare.</p>"
   + ix("prezice", "Instantaneul de la git add", {
       "id": "c3-prezice-add", "poarta": False, "fisier": "terminal.sh",
       "cod": "# analiza.py a fost modificat\n"
              "git add analiza.py\n\n"
              "# inca un rand schimbat in analiza.py, apoi:\n"
              "git commit -m \"analiza pe migratie\"",
       "intrebare": "Ce intră în commit?",
       "variante": ["Ambele schimbări", "Doar prima, cea de dinainte de add",
                    "Nimic: fișierul s-a schimbat după add", "Doar a doua"],
       "corect": 1,
       "indiciu": "git add salvează conținutul fișierului din momentul rulării comenzii; nu urmărește fișierul în continuare.",
       "laBine": "git add salvează un instantaneu al fișierului, nu urmărește modificările ulterioare.",
       "explicatie": "Zona de pregătire păstrează fișierul în starea de la momentul <code>add</code>. A doua schimbare rămâne doar în dosarul de lucru, "
                     "iar <code>git status</code> afișează fișierul de două ori: o dată în pregătire, o dată ca modificat. "
                     "Pentru a include și a doua schimbare, se rulează din nou <code>git add</code>. Acesta este și avantajul zonei de pregătire: "
                     "controlul exact asupra conținutului unui commit.",
       "iesire": "[main 4f2a9c1] analiza pe migratie\n 1 file changed"}))

sl("s6c", "Depozitul echipei", "Depozitul echipei",
   "<h2>Depozitul echipei, pe calculator</h2>"
   + ix("clona", "De pe GitHub, pe calculator", CLONA),
   manual=
   "<h2>Depozitul echipei</h2>"
   "<p>Fiecare echipă are deja pe GitHub un repo, <code>echipa-N</code>, în organizația "
   f"<code>{REPO_ORG}</code>, creat din șablonul cursului. Nu se creează nimic de la zero: fiecare "
   "membru acceptă invitația și copiază repo-ul pe calculator o singură dată, cu <code>git clone</code>.</p>"
   + PE4_HTML
   + ix("clona", "De pe GitHub, pe calculator", CLONA)
   + "<p><code>git clone</code> copiază repo-ul cu tot istoricul, în dosarul <code>.git/</code>, și reține "
     "adresa de la care l-a copiat, sub numele <code>origin</code>. Ultimul cuvânt al comenzii este numele "
     "dosarului: fără el, dosarul ar purta numele repo-ului. Comanda se dă din <code>dsw</code>; dată din "
     "alt dosar, de exemplu din <code>curs/</code>, repo-ul ajunge acolo, iar căile din caiete nu mai "
     "corespund.</p>"
   + "<h3>Ce conține șablonul</h3>"
   + tabel(["În repo", "Ce este", "Cine îl schimbă"], [
       ["<code>data/raw/</code>", "datele aduse de la sursă, exact cum au venit", "caietul de colectare"],
       ["<code>data/processed/</code>", "tabelele produse de caiete", "caietele următoare"],
       ["<code>notebooks/</code>", "câte un caiet pe pas: <code>01_collection.ipynb</code>, <code>02_preprocessing.ipynb</code>", "membrul care are pasul"],
       ["<code>src/</code>", "codul comun, în fișiere <code>.py</code>: <code>date_api.py</code>, copiat din <code>curs/src/</code>", "oricine, cu grijă"],
       ["<code>figures/</code>", "figurile pentru raport", "caietele de explorare"],
       ["<code>docs/</code>", "raportul", "toată echipa, la final"],
       ["<code>README.md</code>", "descrierea proiectului: titlul, întrebarea, unitatea de analiză, sursele", "un membru, la primul commit"],
   ])
   + "<p>Datele de la curs rămân în <code>curs/data</code>; datele proiectului stau în "
     "<code>proiect/data</code> și se urcă pe GitHub. Fișierele de peste 50 MB nu se urcă: caietul care le "
     "folosește spune de unde se descarcă.</p>"
   + nota("Dacă invitația nu a venit",
          "Invitațiile se văd și la <code>https://github.com/dsw-ubb-2026/echipa-N/invitations</code>. "
          "Pleacă doar către membrii care și-au legat numele de pe site de contul GitHub "
          "(Contul meu → „Caută-mi numele”). După legare, invitația se trimite la următoarea "
          "sincronizare făcută de profesor. O invitație expiră după 7 zile și se cere din nou.", True)
   + nota("Git",
          'Se instalează de pe <a class="leg" href="https://git-scm.com/downloads" target="_blank" '
          'rel="noopener">git-scm.com</a>; instalarea se verifică cu <code>git --version</code>. La prima '
          "clonare, Git poate cere autentificarea în contul GitHub, într-o fereastră din browser.")
   + tabel(["Verificare", "Ce afișează"], [
       ["~git remote -v", "adresa lui origin, repo-ul de pe GitHub"],
       ["~git branch -vv", "ramura locală și pe cine urmărește: main urmărește origin/main"],
       ["~git branch -a", "toate ramurile, locale și de pe GitHub (origin/...)"],
   ])
   + "<h3>Pentru un proiect nou, fără repo pe GitHub</h3>"
   "<p>Drumul invers, de la un dosar local la GitHub, este cel din fișa "
   f"{FISA}: depozitul se creează local, apoi se leagă de un repo gol de pe GitHub.</p>"
   "<pre><code>git init                          <span class=\"c\"># depozit local, gol</span>\n"
   "git add .                         <span class=\"c\"># după ce .gitignore este scris</span>\n"
   "git commit -m \"first commit\"\n"
   "git branch -m master main         <span class=\"c\"># ramura principala devine main</span>\n"
   "git remote add origin &lt;GitHub_URL&gt;\n"
   "git push -u origin main</code></pre>"
   "<p>Dacă repo-ul de pe GitHub are deja conținut (de exemplu, un README), cele două istorii nu au un "
   "punct comun și se unesc o singură dată: <code>git pull origin main --allow-unrelated-histories</code>, "
   "apoi <code>git branch -u origin/main</code>.</p>"
   + nota("O eroare frecventă",
          "Rulat din greșeală în dosarul personal (home), <code>git init</code> pune sub urmărire întregul "
          "lui conținut. Remedierea: ștergerea dosarului <code>.git</code> creat acolo; fișierele nu sunt "
          "afectate. În PowerShell, din dosarul respectiv: <code>Remove-Item -Recurse -Force .git</code>.")
   + ix("cod", "Legarea de GitHub", {
       "id": "c3-cod-remote", "poarta": False, "indiciu": "Comanda care gestionează depozitele la distanță se numește „remote”. "
                  "La primul push, -u memorează legătura; ramura principală este main.",
       "iesire": "origin  https://github.com/echipa/proiect.git (fetch)\norigin  https://github.com/echipa/proiect.git (push)\nbranch 'main' set up to track 'origin/main'.", "fisier": "terminal.sh",
       "sarcina": "Un proiect nou, legat de un repo gol de pe GitHub: ce lipsește din comenzi?",
       "cod": "git branch -m master main\n"
              "git {{1}} add origin https://github.com/echipa/proiect.git\n"
              "git push {{2}} origin {{3}}",
       "goluri": {
           "1": {"ok": ["remote"], "ajutor": "comanda"},
           "2": {"ok": ["-u", "--set-upstream"], "ajutor": "opțiunea"},
           "3": {"ok": ["main"], "ajutor": "ramura"}},
       "laBine": "După primul push cu <code>-u</code>, este suficient <code>git push</code>.",
       "laRau": "Ramura este „main”.",
       "explicatie": "<code>-u</code> leagă ramura locală de cea de pe GitHub."}))

sl("s9", "Depozitul echipei", "Ce intră în depozit",
   "<h2>.gitignore</h2>"
   "<p class=\"cheie\">Depozitul se tratează ca public: o parolă urcată o dată rămâne în istoric.</p>"
   + ix("sortare", "Ce intră în depozit", {
       "id": "c3-sort-gitignore",
       "sarcina": "În ce categorie intră fiecare element?",
       "elemente": [
           {"t": "01_collection.ipynb", "cos": 0}, {"t": ".env cu parole", "cos": 1},
           {"t": "README.md", "cos": 0}, {"t": ".venv/", "cos": 1},
           {"t": "un CSV de 1 MB", "cos": 0}, {"t": "un CSV de 2 GB", "cos": 1},
           {"t": "date_api.py", "cos": 0}, {"t": "cheia de API", "cos": 1}],
       "cosuri": [{"t": "În depozit", "d": "caiete, cod, documentație, date mici"},
                  {"t": "Niciodată", "d": "secrete, mediul virtual, fișiere uriașe"}],
       "laBine": "Datele mici intră în depozit: oricine din echipă poate reface analiza din ele.",
       "explicatie": "Mediul virtual se reface din <code>requirements.txt</code> și ocupă sute de megabytes. "
                     "Datele proiectului se urcă, în <code>data/raw</code> și <code>data/processed</code>; "
                     "GitHub avertizează de la 50 MB și refuză fișierele de peste 100 MB. Pentru acestea, "
                     "caietul spune de unde se descarcă."})
   + verif("c3-v6", 3,
           "Un fișier cu o parolă a fost inclus din greșeală într-un commit și trimis cu push. Ce trebuie făcut?",
           ["Ștergerea fișierului și un commit nou",
            "Adăugarea fișierului în .gitignore",
            "Nu este necesar nimic, depozitul este privat",
            "Schimbarea imediată a parolei, apoi curățarea istoricului"],
           "Prima măsură este schimbarea parolei. Celelalte variante lasă parola "
           "în istoric, de unde poate fi extrasă imediat de oricine știe unde să "
           "caute. Curățarea istoricului urmează și este mai dificilă: cere rescrierea istoricului, iar copiile deja descărcate rămân."),
   manual=
   "<h2>.gitignore</h2>"
   "<p>Un fișier text, aflat în rădăcina proiectului, care enumeră ce nu trebuie urmărit. Datele mici ale "
   "proiectului intră în depozit (<code>data/raw</code>, <code>data/processed</code>), ca analiza să poată fi "
   "refăcută; în <code>.gitignore</code> rămân mediul virtual, secretele, gunoiul uneltelor și fișierele uriașe, "
   "trecute pe nume:</p>"
   "<pre><code><span class=\"c\"># mediul virtual și gunoiul uneltelor</span>\n"
   ".venv/\n__pycache__/\n.ipynb_checkpoints/\n\n"
   "<span class=\"c\"># secretele</span>\n.env\n\n"
   "<span class=\"c\"># fișierele de peste 50 MB, câte unul; caietul spune de unde se descarcă</span>\n"
   "data/raw/sci_nuts3.csv</code></pre>"
   + "<p>Alte rânduri utile, după nevoie: <code>.vscode/</code>, <code>.DS_Store</code>, <code>Thumbs.db</code>. "
     "Fișierul <code>.gitignore</code> intră în depozit ca orice alt fișier.</p>"
   + tabel(["Un fișier adăugat din greșeală trebuie…", "Comanda"], [
       ["doar scos din zona de pregătire (rămâne pe disc)", "~git reset -- \"nume fisier.ipynb\""],
       ["scos complet de sub urmărirea Git, dar păstrat în proiect", "~git rm --cached nume_fisier"],
   ])
   + ix("sortare", "Ce intră în depozit", {
       "id": "c3-sort-gitignore",
       "sarcina": "În ce categorie intră fiecare element?",
       "elemente": [
           {"t": "01_collection.ipynb", "cos": 0}, {"t": ".env cu parole", "cos": 1},
           {"t": "README.md", "cos": 0}, {"t": ".venv/", "cos": 1},
           {"t": "un CSV de 1 MB", "cos": 0}, {"t": "un CSV de 2 GB", "cos": 1},
           {"t": "date_api.py", "cos": 0}, {"t": "cheia de API", "cos": 1}],
       "cosuri": [{"t": "În depozit", "d": "caiete, cod, documentație, date mici"},
                  {"t": "Niciodată", "d": "secrete, mediul virtual, fișiere uriașe"}],
       "laBine": "Datele mici intră în depozit: oricine din echipă poate reface analiza din ele.",
       "explicatie": "GitHub avertizează de la 50 MB și refuză fișierele de peste 100 MB."}))

sl("s8", "Depozitul echipei", "Primul commit",
   "<h2>Primul commit al echipei</h2>"
   + ix("commit", "Primul commit al echipei", COMMIT),
   manual="<h2>Primul commit</h2>"
   "<p>Primul commit al echipei, ca în caietul 03 (secțiunea 7.3), pe main: un membru completează, "
   "provizoriu, <code>README.md</code> (titlul, întrebarea de cercetare, unitatea de analiză, tabelul "
   "surselor), iar altul adaugă <code>src/date_api.py</code>. Fiecare urcă ce a făcut, cu "
   "<code>git pull</code> înainte. Istoricul local și GitHub au deja commit-ul din șablon.</p>"
   + ix("commit", "Primul commit al echipei", COMMIT)
   + "<p>Același ciclu se repetă la fiecare pas al proiectului, din caietul pasului "
     "(pe dev, de la slide-ul următor):</p>"
   "<pre><code><span class=\"c\"># unde sunt, ce s-a schimbat?</span>\ngit status\n\n"
   "<span class=\"c\"># ce intra in acest commit</span>\n"
   "git add notebooks/01_collection.ipynb\n\n"
   "<span class=\"c\"># il scriu in istoric, cu un mesaj care spune ceva</span>\n"
   f"git commit -m \"{_MSG}\"\n\n"
   "<span class=\"c\"># intai ce au trimis colegii, apoi trimit si eu</span>\ngit pull\ngit push</code></pre>"
   + nota("Frecvența commit-urilor",
          "Un commit nu este o livrare, ci un punct de revenire. Regula "
          "practică: câte un commit pentru fiecare unitate de lucru încheiată "
          "care poate fi descrisă printr-un mesaj scurt.")
   + "<h3>Înainte de primul commit: identitatea autorului</h3>"
   "<p>Fiecare commit conține un nume și o adresă de email. Git nu verifică datele: folosește exact "
   "valorile configurate, o singură dată pe calculator. Cu o adresă diferită de cea a contului de GitHub, "
   "commit-urile apar pe GitHub fără legătură cu vreun cont; verificarea se face la finalul lecției, pe "
   "pagina commit-ului.</p>"
   + ix("cod", "Configurarea identității", CONFIG)
   + ix("ordine", "Ordinea pașilor", {
       "id": "c3-ordine-commit", "poarta": False,
       "indiciu": "Întâi intrarea în depozit. Urmează verificarea a ceea ce vede Git, adăugarea în zona de "
                  "pregătire, o nouă verificare, commit-ul și trimiterea pe GitHub.",
       "iesire": f"a1b2c3d (HEAD -> main, origin/main) {_MSG1}\n9f8e7d6 Initial commit",
       "sarcina": "Ordinea primului commit al echipei, de la repo-ul clonat la GitHub.",
       "linii": [
           "cd proiect",
           "git pull                        # intai ce au trimis colegii",
           "git status                      # ce vede Git",
           "git add README.md",
           f"git commit -m \"{_MSG1}\"",
           "git push",
           "git log --oneline               # commit-ul, local si pe GitHub"],
       "explicatie": "<code>git status</code> este comanda folosită cel mai des: înainte de "
                     "<code>add</code> și înainte de <code>commit</code>."}))

sl("s14", "În echipă", "Ramurile",
   "<h2>main și dev</h2>"
   + ix("ramuri", "main și dev", RAMURI),
   manual=
   "<h2>Ramurile: main și dev</h2>"
   "<p>O ramură este o linie de lucru paralelă. Echipa folosește două: <code>main</code>, versiunea "
   "stabilă, cea care se predă, și <code>dev</code>, pe care se lucrează zilnic. Ce se face pe dev nu "
   "afectează main până la îmbinare. Comenzile de sus se apasă în ordine; lângă graf, dosarul arată ce "
   "fișiere există pe ramura curentă.</p>"
   + ix("ramuri", "main și dev", RAMURI)
   + tabel(["Cine, când", "Comanda", "Ce face"], [
       ["un membru, o dată", "~git switch -c dev", "creează dev din main și trece pe ea"],
       ["același membru", "~git push -u origin dev", "urcă dev pe GitHub și o leagă de origin/dev"],
       ["ceilalți, o dată", "~git fetch ; git switch dev", "aduc dev de pe GitHub și trec pe ea"],
       ["oricine", "~git branch", "listează ramurile; cea curentă are *"],
       ["la o sarcină încheiată", "~git switch main ; git pull", "trece pe main, la zi cu GitHub"],
       ["", "~git merge dev ; git push", "main primește tot ce s-a lucrat pe dev"],
       ["oricând", "~git log --oneline --graph --all", "același graf, desenat în terminal"],
   ])
   + nota("De ce nu se lucrează direct pe main",
          "Pentru că orice modificare neterminată ar afecta întreaga echipă. Cu dev, main rămâne "
          "permanent o versiune care rulează, iar lucrul în desfășurare stă separat până la final."))

sl("s14b", "În echipă", "Pull, apoi push",
   "<h2>Pull, apoi push</h2>"
   + ix("sincron", "Doi colegi și GitHub, pe dev", SINCRON),
   manual=
   "<h2>Pull, apoi push</h2>"
   "<p>Pe dev lucrează toată echipa, deci GitHub primește commit-uri de la mai mulți membri. Desenul "
   "arată ce se întâmplă când doi colegi lucrează în același timp: fiecare coloană este istoricul unui "
   "depozit, cu cel mai nou commit sus. Push-ul celui care a rămas în urmă este refuzat până aduce, cu "
   "<code>git pull</code>, ce îi lipsește.</p>"
   + ix("sincron", "Doi colegi și GitHub, pe dev", SINCRON)
   + "<p>Conținutul din <code>dev</code> se integrează în <code>main</code> după fiecare sarcină "
     "importantă încheiată (curățarea datelor, setul de vizualizări, modelul): nu la fiecare commit, "
     "dar nici doar la final. Integrarea este îmbinarea de la slide-ul despre ramuri: "
     "<code>git switch main</code>, <code>git merge dev</code>, <code>git push</code>.</p>"
   + f"<p>Tot fluxul, pe un singur tabel (și în fișa {FISA}):</p>"
   + tabel(["Cine, când", "Comanda", "Apoi"], FLUX_DEV)
   + nota("Fișiere separate",
          "Fiecare membru lucrează în caietul pasului lui (<code>notebooks/01_collection.ipynb</code>, "
          "<code>notebooks/02_preprocessing.ipynb</code>); codul comun stă în <code>src/</code>. "
          "Conflictele apar doar când două persoane modifică aceleași rânduri.")
   + nota("Ce face <code>git merge dev</code>",
          "Integrează în main toate commit-urile care există în dev, dar nu și "
          "în main. Dacă main nu a primit commit-uri noi între timp, eticheta "
          "main doar avansează (fast-forward)."))

sl("s15", "În echipă", "Conflictele",
   "<h2>Când două persoane modifică aceleași rânduri</h2>"
   + "<p>La <code>git pull</code>, Git nu poate alege între variante: le inserează "
     "pe amândouă în fișier, iar alegerea se face manual. După rezolvare: "
     "<code>git add .</code>, <code>git commit -m \"rezolvat conflict\"</code>, "
     "<code>git push</code>.</p>"
   + ix("conflict", "Rezolvarea conflictului", {
       "id": "c3-conflict", "fisier": "src/tabele.py", "ramura": "dev",
       "sarcina": "O colegă a schimbat caietul de preprocesare, iar tabelul are acum alt nume. Codul "
                  "local îl citește încă după numele vechi. Care variantă rămâne?",
       "alMeu": 'regional = pd.read_csv("data/processed/indicatori.csv")',
       "alLor": 'regional = pd.read_csv("data/processed/regional.csv")',
       "bun": "lor",
       "deCe": "Fișierul cu numele vechi nu mai este scris de caiet: colega l-a redenumit "
               "și a trimis modificarea pe dev. Varianta locală ar produce o eroare la prima rulare.",
       "explicatie": "Indiferent de alegere, marcajele dispar și fișierul redevine "
                     "cod valid. Git nu verifică dacă alegerea este corectă; această "
                     "verificare revine persoanei care rezolvă conflictul, de aceea un "
                     "conflict se rezolvă citind codul, nu alegând la întâmplare."}),
   manual=
   "<h2>Conflictele</h2>"
   "<p>Un conflict apare la <code>git pull</code> (sau la <code>git merge</code>) "
   "când două persoane au modificat aceleași rânduri. După rezolvare: "
   "<code>git add .</code>, <code>git commit -m \"rezolvat conflict\"</code>, "
   "<code>git push</code>.</p>"
   + nota("Pull request",
          "Pe GitHub, integrarea lui dev în main se poate face și printr-un pull "
          "request: se solicită îmbinarea, iar un coleg o revizuiește înainte. "
          "Pentru proiectul echipei este suficient <code>git merge dev</code> din "
          "terminal; pull request-ul este un pas suplimentar, util când echipa "
          "dorește o revizuire prealabilă a codului.")
   + "<h3>Conflictele nu sunt erori</h3>"
   + "<p>Prin conflict, Git semnalează că nu poate decide automat între două "
     "modificări. În fișier, varianta locală apare deasupra, iar cea preluată, "
     "dedesubt.</p>"
   + ix("conflict", "Rezolvarea conflictului", {
       "id": "c3-conflict", "fisier": "src/tabele.py", "ramura": "dev",
       "sarcina": "O colegă a schimbat caietul de preprocesare, iar tabelul are acum alt nume. Codul "
                  "local îl citește încă după numele vechi. Care variantă rămâne?",
       "alMeu": 'regional = pd.read_csv("data/processed/indicatori.csv")',
       "alLor": 'regional = pd.read_csv("data/processed/regional.csv")',
       "bun": "lor",
       "deCe": "Fișierul cu numele vechi nu mai există.",
       "explicatie": "Git nu verifică dacă alegerea este corectă; verificarea revine persoanei care rezolvă conflictul."}))

sl("s16", "În echipă", "Regulile echipei",
   "<h2>Cinci reguli pentru acest semestru</h2>"
   + '<table class="tabel md reg2"><tbody>'
   + "".join(f'<tr><td class="md__n">{i}</td><td><b>{t}</b></td><td>{d}</td></tr>'
             for i, (t, d) in enumerate([
                 ("Fiecare în fișierul lui", "un caiet pe pas, cu un autor; două persoane în același caiet înseamnă conflict"),
                 ("<code>git pull</code> întâi", "la începutul lucrului și înainte de fiecare push"),
                 ("main rămâne stabil", "lucrul zilnic, pe dev; în main intră doar pași încheiați"),
                 ("Mesaje descriptive", "ce s-a schimbat, nu „update”"),
                 ("Fără secrete, fără fișiere uriașe", "parolele nu intră deloc; peste 50 MB, doar adresa de unde se descarcă"),
             ], 1))
   + "</tbody></table>"
   + nota("Toate comenzile, pe o pagină",
          f"Fișa {FISA}: configurarea, clonarea, <code>.gitignore</code>, ramura dev, lucrul zilnic "
          "și îmbinarea în main. În <code>README.md</code> se notează cine răspunde de fiecare etapă.", True))

sl("s8b", "Verificarea", "Citirea lui git status",
   "<h2>Citirea lui git status</h2>"
   + ix("status", "Ce intră în commit", STATUS),
   manual="<h2>Citirea lui git status</h2>"
   "<p><code>git status</code> este comanda folosită cel mai des: se rulează înainte de fiecare "
   "<code>add</code> și înainte de fiecare <code>commit</code>. Ieșirea are trei grupuri, fiecare "
   "corespunzând unei zone: ce intră în commit (verde), ce s-a modificat, dar nu a trecut prin "
   "<code>git add</code>, și fișierele noi, pe care Git nu le urmărește încă (roșu). În terminalul "
   "real, fiecare grup are dedesubt și o indicație între paranteze, de exemplu "
   "<code>(use \"git add &lt;file&gt;...\" to update what will be committed)</code>.</p>"
   + ix("status", "Ce intră în commit", STATUS)
   + tabel(["În git status", "Zona", "Intră în commit?"], [
       ["Changes to be committed", "pregătire", "da"],
       ["Changes not staged for commit", "dosar, fișier urmărit și modificat", "nu, până la <code>git add</code>"],
       ["Untracked files", "dosar, fișier nou", "nu, până la <code>git add</code>"],
   ])
   + "<p>Varianta scurtă, <code>git status --short</code>, pune aceleași informații pe două coloane: "
     "prima pentru pregătire, a doua pentru dosar. <code>M </code> înseamnă modificat și pregătit, "
     "<code> M</code> modificat, dar nepregătit, iar <code>??</code> fișier neurmărit.</p>")

sl("s22b", "Verificarea", "Verificarea depozitului",
   "<h2>Verificarea depozitului</h2>"
   + ix("dovada", "Verificarea depozitului", DOVADA),
   manual=
   "<h2>Verificarea depozitului</h2>"
   "<p>Ultimul pas de Git al lecției, făcut de fiecare membru după primul commit (caietul 03, "
   "secțiunea 7.3). Verificarea arată, cu ieșirea comenzilor de pe propriul calculator, că munca există în "
   "două locuri: local și pe GitHub. Butonul <b>Indiciu</b> arată unde se găsește fiecare rezultat.</p>"
   + ix("dovada", "Verificarea depozitului", DOVADA)
   + tabel(["Dacă", "Cauza", "Ce se face"], [
       ["<code>fatal: not a git repository</code>", "terminalul nu este în <code>proiect</code>", "~cd proiect"],
       ["<code>Your branch is ahead of 'origin/main'</code>", "commit-ul este doar local", "~git push"],
       ["push refuzat: <code>fetch first</code>", "pe GitHub sunt commit-uri ale colegilor", "~git pull, apoi git push"],
       ["<code>git remote -v</code> nu arată nimic", "dosarul nu este clonat din repo-ul echipei", "~git clone, din dsw"],
       ["un fișier de peste 50 MB, refuzat la push", "fișierul a intrat în commit", "~git rm --cached cu numele lui"],
       ["commit-ul apare pe GitHub fără cont", "adresa din Git nu este cea a contului", "~git config --global user.email \"adresa contului\""],
   ]))

sl("s17", "Cadrul teoretic", "De ce un cadru",
   "<h2>Încadrarea teoretică</h2>"
   "<p class=\"cheie\">Datele nu generează întrebări. Întrebările provin din "
   "teorie, iar datele pot susține sau infirma răspunsurile propuse.</p>"
   + TIPURI_LIT,
   manual=
   "<h2>Încadrarea teoretică</h2>"
   "<p>Datele nu generează întrebări. Întrebările provin din teorie, iar datele "
   "pot susține sau infirma răspunsurile propuse. Fără un cadru, un proiect "
   "devine o colecție de grafice a căror relevanță nu poate fi evaluată.</p>"
   "<p>În fluxul de lucru, literatura intervine în patru moduri, fiecare "
   "răspunzând la altă întrebare. Teoria vine prima, la definirea întrebării. "
   "Metoda intervine la analiză: dacă alte studii au abordat deja o întrebare "
   "asemănătoare, analiza pornește de la modelul lor, nu de la zero. "
   "Documentația se consultă la fiecare pas de cod, iar descrierea datelor se "
   "citează oriunde acestea sunt folosite.</p>"
   + TIPURI_LIT
   + "<h3>Căutarea literaturii</h3>"
   "<p>O căutare bună nu începe cu un motor de căutare, ci cu un articol de "
   "încredere. Pentru proiectul cursului, acesta este Bailey și colegii (2018), "
   "articolul care a introdus indicele SCI. De la el, căutarea merge în două "
   "direcții: înapoi, prin referințele lui, și înainte, prin lucrările care l-au "
   "citat ulterior.</p>"
   + ix("ordine", "Pașii căutării", CAUTARE)
   + "<p>Fiecare lucrare găsită se notează pe un rând, cu aceleași coloane. Matricea "
   "este principalul rezultat al căutării: din ea se scrie secțiunea de cadru "
   "teoretic a raportului, și tot ea arată ce nu a fost încă studiat.</p>"
   + tabel(["Lucrarea", "Întrebarea", "Datele", "Metoda", "Ce se preia"], [
       ["Bailey și colegii (2018)", "ce măsoară SCI, ce îl explică", "SCI, comitate SUA și țări", "descriptiv, regresii pe distanță", "definiția, scăderea cu distanța, legătura cu migrația"],
       ["Sandu (2025)", "cum se leagă județele de destinațiile emigrației", "fluxuri NUTS3 × 6 țări, 2011-2021", "regresii, analiză factorială", "reperul de comparație pentru harta diasporei din SCI"],
   ])
   + lecturi(["scholar", "semantic", "zotero"], "Unelte"))

sl("s19", "Cadrul teoretic", "Cadrul proiectului",
   "<h2>Ce explică legăturile dintre locuri</h2>"
   + ix("cadru", "Modelul conceptual al proiectului", CADRU),
   manual="<h2>Cadrul proiectului: ce explică legăturile dintre locuri</h2>"
   "<p>Un cadru teoretic spune ce trebuie explicat, prin ce și de ce. În proiectul cursului, de explicat "
   "este legătura dintre două locuri, măsurată prin SCI. Patru factori o pot explica, fiecare cu "
   "mecanismul lui și cu variabila care îl măsoară. Ce nu explică niciunul este reziduul: legăturile mai "
   "puternice sau mai slabe decât prezic factorii. Din el pornesc întrebările echipelor.</p>"
   + ix("cadru", "Modelul conceptual al proiectului", CADRU)
   + FACTORI_TAB
   + "<p>Literatura de la temelia cadrului este cea despre sistemele migratorii: locurile legate prin "
     "migrație rămân legate și prin fluxuri de informație, bani și vizite, iar rețelele de migranți "
     "facilitează migrația celor care urmează. SCI permite observarea directă a unei părți din aceste "
     "legături. Distanța și migrația intră în modelul din C7; istoria și locurile nu au încă o variabilă "
     "gata făcută, deci echipa care le alege își construiește măsura.</p>"
   + "<h3>Întrebările derivate din cadru</h3>"
   "<ol>"
   "<li><em>Migrația:</em> sunt perechile de țări cu mai mulți migranți la mie mai "
   "puternic conectate, la aceeași distanță?</li>"
   "<li><em>Istoria:</em> generează granițele istorice și minoritățile (de "
   "exemplu, în cazul României și al Ungariei) legături pe care migrația "
   "recentă nu le explică?</li>"
   "<li><em>Ce rămâne:</em> unde sunt legăturile mai puternice decât prezic "
   "distanța și migrația împreună și ce au în comun aceste locuri?</li>"
   "</ol>"
   + nota("Contribuția echipelor",
          "Fiecare echipă alege un factor și un loc: un coridor (de exemplu, "
          "România și Italia) sau o țară analizată la nivel regional. Se poate "
          "adăuga un factor nou, de exemplu limba sau religia, cu condiția să "
          "poată fi măsurat.")
   + lecturi(["bailey2018", "palloni2001", "dehaas2010", "sandu2005", "sandu2025", "bailey2020"], "Literatura cadrului"))

sl("s20", "Cadrul teoretic", "Întrebarea echipei",
   "<h2>Întrebarea echipei</h2>"
   "<p>Două sau trei rânduri. Formularea nu trebuie să fie definitivă, dar "
   "trebuie să existe.</p>"
   + ix("asteptari", "Întrebarea de cercetare", {
       "id": "c3-intrebare", "tip": "intrebare", "minim": 60,
       "sarcina": "Care este întrebarea la care vrea să răspundă echipa și "
                  "pe ce factor din cadru se sprijină?",
       "exemplu": "De exemplu: sunt regiunile din Italia cu mai mulți români "
                  "și cele mai conectate cu România, sau legătura urmează altă "
                  "logică decât migrația?",
       "multumesc": "Răspunsul a fost înregistrat. Feedbackul va fi transmis înainte de cursul următor."}))

sl("s21d", "Datele", "Datele proiectului",
   "<h2>Ce date are proiectul acum</h2>"
   "<p class=\"cheie\">Patru tabele în <code>data/c3</code>, pregătite în caietul 03. "
   "La cursul 4 se unesc într-un singur tabel.</p>"
   + ix("tabele", "Tabelele din data/c3", TABELE),
   manual=
   "<h2>Datele proiectului, după caietul 03</h2>"
   "<p>Caietul 03 aduce datele într-o formă comună: patru tabele, fiecare cu un rând bine definit și "
   "cu aceleași nume de coloane pentru același fel de cod. Legăturile (SCI) sunt variabila de explicat; "
   "migrația și indicatorii regionali sunt doi dintre factorii din cadru; nomenclatorul dă numele "
   "regiunilor și leagă celelalte tabele.</p>"
   + ix("tabele", "Tabelele din data/c3", TABELE)
   + "<h3>Indicatorii regionali, într-un tabel</h3>"
   "<p>Fiecare fișier din C2 are câte un rând pe regiune, cu un cod NUTS. Denumirile "
   "regiunilor provin din nomenclatorul Eurostat GISCO, pe care caietul îl descarcă cu "
   "<code>requests</code>; lungimea codului indică nivelul: 2 caractere țara, 4 regiunea, "
   "5 județul. Indicatorii se pun apoi într-un singur tabel, cu o funcție care citește un fișier "
   "și notează de unde vine.</p>"
   + ix("pas", "Indicatorii într-un singur tabel", PAS_NUTS)
   + nota("De ce format lung, nu lat",
          "Un rând pentru fiecare combinație de regiune, indicator și nivel. Astfel, un "
          "indicator nou se adaugă fără coloane noi, iar valorile lipsă se numără direct. "
          "În C4, tabelul se transformă în format lat, cu un rând pe regiune.", True)
   + "<p>Același pas se aplică și datelor SCI: coloanele cu nume în engleză sunt "
     "redenumite după semnificația lor în proiect (<code>user_region</code> devine "
     "<code>regiune_1</code>, <code>scaled_sci</code> devine <code>sci</code>). "
     "La NUTS 2, tabelul are 298 × 298 = 88.804 rânduri: fiecare regiune cu fiecare, "
     "inclusiv cu ea însăși, iar fiecare pereche apare în ambele ordini.</p>"
   + "<h3>Migrația: țări și grupuri de țări</h3>"
   "<p>Înainte de orice analiză, aceleași patru operații, de fiecare dată.</p>"
   + ix("cod", "Explorare inițială", EXPLORARE)
   + "<p>Eurostat raportează în aceeași coloană țări și grupuri de țări (Uniunea, toți străinii, "
     "cetățenii proprii), iar grupurile trebuie scoase: altfel aceiași oameni sunt numărați de mai "
     "multe ori. Caietul păstrează doar codurile de două litere și scoate rândurile în care cetățenia "
     "coincide cu țara de rezidență.</p>"
   + ix("pas", "Țări și grupuri de țări", PAS_TARI)
   + nota("Scopul explorării inițiale",
          "Scopul nu sunt rezultatele, ci semnele că datele nu corespund "
          "așteptărilor: un număr de rânduri diferit de cel estimat, o coloană "
          "text care ar trebui să fie numerică, valori lipsă neașteptate. "
          "Analiza propriu-zisă începe la cursul 6; acum se verifică doar că "
          "datele pot fi analizate."))

sl("s23", "Mai departe", "Pentru cursul următor",
   "<h2>La cursul 4: curățarea datelor</h2>"
   '<div class="fin3"><div class="fin3__g">'
   "<section><h4>Ce urmează la cursul 4</h4><ul>"
   "<li>Curățarea datelor: valori lipsă, duplicate, coduri ambigue (EL, NA).</li>"
   "<li>SCI, migrația, zborurile și indicatorii, reunite în același tabel.</li>"
   "<li>Ramura dev, pe care lucrează toată echipa.</li></ul></section>"
   "<section><h4>Pregătirea pentru cursul 4</h4><ul>"
   "<li>Depozitul echipei pe calculatorul fiecărui membru, cu primul commit pe GitHub.</li>"
   "<li><code>README.md</code>: tema, întrebarea provizorie, unitatea de analiză, sursele și rolul fiecăruia.</li>"
   "<li>Tema 1, pe Teams: tema proiectului, datele și rolul ales, cu propriile cuvinte.</li></ul></section>"
   "</div>"
   '<p class="fin3__a"><a class="leg" href="../">Pagina cursului 3</a>'
   '<a class="leg" href="../../c4-curatarea-datelor/">Cursul 4</a></p></div>')


if __name__ == "__main__":
    L.scrie_tot()
