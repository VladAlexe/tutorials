# -*- coding: utf-8 -*-
"""
Lecția 3: Versionare și colaborare cu Git.

Urmează prezentarea Curs_3.pptx: ce face Git, repository-uri, credențiale,
GitHub, legarea depozitului local de cel de pe GitHub, și încadrarea teoretică
a proiectului, pe datele SCI și ale migrației.

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
    ("Ce face Git", "azi", "Istoricul, revenirea la versiuni anterioare și cele trei zone."),
    ("Primul commit", "azi", "git status, .gitignore, add, commit, push."),
    ("GitHub", "azi", "Legarea depozitului local de depozitul echipei."),
    ("Lucrul în echipă", "azi", "Ramuri, pull înainte de push, conflicte."),
    ("Cadrul proiectului", "azi", "Ce explică legăturile dintre locuri și întrebarea echipei."),
    ("Datele proiectului", "azi", "Cele patru tabele pregătite în caietul 03."),
]

# Pașii pentru lecția 3: Git (caietul 03, secțiunea 6) și migrația (caietul 03, secțiunea 5).
# Cifrele migrației: Eurostat migr_pop1ctz, 2024, din rularea caietului (31 octombrie 2026).

_NB3 = "notebooks/03_surse_diverse_si_preprocesare.ipynb"
FISA = '<a class="leg" href="../git/">Lucrul cu Git</a>'   # pagina cu toate comenzile
_MSG = "Pregatim tabelele regionale si migratia"

# --------------------------------------------------------------------------
# Primul commit, desenat: patru zone, fișierele reale ale echipei, o comandă
# pe pas. git add pune în pregătire o copie; originalul rămâne în dosar.
# data/ are aproximativ 3 MB după caietele 02 și 03 (măsurat pe rularea din
# 31 octombrie 2026); nu se versionează pentru că se reface din caiete.
# --------------------------------------------------------------------------

_SALVAT = {"nb": "salvat", "rd": "salvat", "gi": "salvat", "dt": "ignorat"}
COMMIT = {
    "zone": [{"t": "Dosarul proiectului", "d": "proiect/, pe calculator"},
             {"t": "Pregătire", "d": "ce intră în commit"},
             {"t": "Istoric local", "d": "commit-urile salvate"},
             {"t": "GitHub", "d": "depozitul echipei"}],
    "fisiere": {"nb": {"t": "notebooks/03_….ipynb"}, "rd": {"t": "README.md"},
                "gi": {"t": ".gitignore"}, "dt": {"t": "data/", "tip": "d", "m": "3 MB"}},
    "commituri": {"c0": {"h": "9f8e7d6", "m": "Initial commit", "x": "de la clonare", "vechi": True},
                  "c1": {"h": "a1b2c3d", "m": _MSG, "x": "3 fișiere"}},
    "start": "Caietul 03 a fost copiat în <code>proiect/notebooks/</code> și rulat, iar în "
             "<code>README.md</code> s-a completat fișa echipei. Comenzile de sus se apasă pe rând.",
    "stari": [
        {"dosar": {"nb": "", "rd": "", "dt": ""}, "ist": ["c0"], "gh": ["c0"]},
        {"dosar": {"nb": "nou", "rd": "modificat", "dt": "nou"}, "ist": ["c0"], "gh": ["c0"], "activ": [0]},
        {"dosar": {"nb": "nou", "rd": "modificat", "gi": "nou", "dt": "ignorat"}, "ist": ["c0"], "gh": ["c0"], "activ": [0]},
        {"dosar": {"nb": "pregatit", "rd": "pregatit", "gi": "pregatit", "dt": "ignorat"},
         "preg": ["nb", "rd", "gi"], "ist": ["c0"], "gh": ["c0"], "activ": [1]},
        {"dosar": _SALVAT, "ist": ["c1", "c0"], "gh": ["c0"], "activ": [2]},
        {"dosar": _SALVAT, "ist": ["c1", "c0"], "gh": ["c1", "c0"], "activ": [3]},
    ],
    "pasi": [
        {"cmd": "git status", "t": "Ce vede Git",
         "txt": "Două elemente noi, pe care Git nu le urmărește încă, și <code>README.md</code>, modificat. "
                "<code>git status</code> nu schimbă nimic: doar arată."},
        {"cmd": ".gitignore", "edit": True, "full": "data/        un rând nou în .gitignore, scris în VS Code",
         "t": "Ce nu intră",
         "txt": "<code>data/</code> se reface oricând rulând caietele, deci nu se versionează. "
                "Trecut în <code>.gitignore</code>, nu mai apare în <code>git status</code>."},
        {"cmd": "git add", "full": f"git add {_NB3} README.md .gitignore", "t": "Ce intră în commit",
         "txt": "<code>git add</code> pune în pregătire o copie a fișierelor numite, așa cum sunt acum. "
                "Originalele rămân în dosar."},
        {"cmd": "git commit", "full": f"git commit -m \"{_MSG}\"", "t": "Fotografia",
         "txt": "Copiile din pregătire devin un commit: fotografia celor trei fișiere, cu autorul, data "
                "și mesajul. La ea se poate reveni oricând."},
        {"cmd": "git push", "t": "Pe GitHub",
         "txt": "Până aici, totul exista doar pe calculatorul local. <code>git push</code> copiază "
                "commit-ul pe GitHub, unde îl văd colegii."},
    ],
}

# --------------------------------------------------------------------------
# git status, citit: ieșirea adevărată, în engleză, cu culorile terminalului.
# --------------------------------------------------------------------------

STATUS = {
    "id": "c3-status",
    "sarcina": "A doua zi, înainte de commit. Ce intră în commit dacă se rulează acum "
               "<code>git commit</code>? Rândurile se aleg cu un clic.",
    "antet": ["On branch dev", "Your branch is up to date with 'origin/dev'."],
    "grupuri": [
        {"t": "Changes to be committed:", "cls": "pr", "zona": "pregătire: intră în commit",
         "fisiere": [{"t": f"modified:   {_NB3}", "ok": True},
                     {"t": "new file:   code/harta.py", "ok": True}]},
        {"t": "Changes not staged for commit:", "cls": "ds", "zona": "dosar: modificat, nu intră",
         "fisiere": [{"t": "modified:   README.md", "ok": False}]},
        {"t": "Untracked files:", "cls": "ds", "zona": "dosar: nou, neurmărit",
         "fisiere": [{"t": "grafic_test.png", "ok": False}]},
    ],
    "indiciu": "Git împarte ieșirea în trei grupuri. Doar unul are legătură cu <code>git add</code>.",
    "indiciu2": "În terminal, grupul care intră în commit este scris cu verde.",
    "laRau": "Intră doar ce a trecut prin <code>git add</code>.",
    "laBine": "Intră doar grupul „Changes to be committed”.",
    "explicatie": "Celelalte două nu au trecut prin <code>git add</code>. Pentru a intra și ele: "
                  "<code>git add README.md grafic_test.png</code>, apoi din nou <code>git status</code>.",
}

# --------------------------------------------------------------------------
# Ramurile: commit-uri cu nume, și ce conține fișierul din dosar la fiecare
# pas. La git switch main, curățarea dispare din fișier și revine la merge.
# --------------------------------------------------------------------------

RAMURI = {
    "id": "c3-ramuri",
    "ramura": "curatare",
    "fisier": "notebooks/03_….ipynb",
    "commituri": {
        "m1": {"x": 0, "lane": "m", "m": "structura"},
        "m2": {"x": 1, "lane": "m", "m": "colectare migrație", "parinti": ["m1"]},
        "r1": {"x": 2, "lane": "r", "m": "scoate grupurile", "parinti": ["m2"]},
        "r2": {"x": 3, "lane": "r", "m": "redenumește coloane", "parinti": ["r1"]},
        "mm": {"x": 4, "lane": "m", "m": "merge curatare", "merge": True, "parinti": ["m2", "r2"]},
    },
    "linii": [{"c": "m2", "t": "migrația, colectată"},
              {"c": "r1", "t": "fără grupurile de țări"},
              {"c": "r2", "t": "coloane cu nume clare"}],
    "stari": [
        {"com": ["m1", "m2"], "ram": False, "aici": "m", "vede": ["m2"]},
        {"com": ["m1", "m2"], "ram": True, "din": "m2", "aici": "r", "vede": ["m2"]},
        {"com": ["m1", "m2", "r1"], "ram": True, "aici": "r", "vede": ["m2", "r1"]},
        {"com": ["m1", "m2", "r1", "r2"], "ram": True, "aici": "r", "vede": ["m2", "r1", "r2"]},
        {"com": ["m1", "m2", "r1", "r2"], "ram": True, "aici": "m", "vede": ["m2"]},
        {"com": ["m1", "m2", "r1", "r2", "mm"], "ram": True, "aici": "m", "vede": ["m2", "r1", "r2"]},
    ],
    "start": "Pe <code>main</code> sunt două commit-uri, iar caietul funcționează. Curățarea migrației se face "
             "pe o ramură separată, ca <code>main</code> să rămână în orice moment o versiune care merge.",
    "pasi": [
        {"cmd": "git switch -c curatare", "t": "Ramura nouă",
         "txt": "Pornește din ultimul commit. Nu se copiază nimic: apare doar o linie nouă de lucru, "
                "iar lucrul continuă pe ea."},
        {"cmd": "git commit", "full": "git commit -m \"scoate grupurile de tari\"", "t": "Pe ramură",
         "txt": "Commit-ul intră doar pe <code>curatare</code>. Pe <code>main</code> nu se schimbă nimic."},
        {"cmd": "git commit", "full": "git commit -m \"redenumeste coloanele\"", "t": "Încă un commit",
         "txt": "Pe ramură se lucrează cât este nevoie, cu oricâte commit-uri."},
        {"cmd": "git switch main", "t": "Înapoi pe main",
         "txt": "Fișierul din dosar revine la versiunea de pe <code>main</code>: curățarea nu se mai vede. "
                "Nu s-a pierdut, așteaptă pe ramură."},
        {"cmd": "git merge curatare", "t": "Îmbinarea",
         "txt": "Curățarea intră în <code>main</code>. Abia acum o primesc toți cei care lucrează pe "
                "<code>main</code>."},
    ],
}

# --------------------------------------------------------------------------
# Lucrul în echipă pe dev: doi colegi și GitHub. Fiecare coloană e git log,
# cu cel mai nou commit sus. Pull înainte de push, pe un caz care se
# întâmplă în prima săptămână: push refuzat.
# --------------------------------------------------------------------------

_B = ["c2", "c1"]
_DUPA = ["mg", "m1", "a1"] + _B
SINCRON = {
    "coloane": [{"k": "an", "t": "Andrei", "d": "dev, pe laptop"},
                {"k": "gh", "t": "GitHub", "d": "origin/dev", "gh": True},
                {"k": "ma", "t": "Maria", "d": "dev, pe laptop"}],
    "autori": {"baza": {"et": "commit-urile de la început", "c": "text-3"},
               "an": {"et": "Andrei", "c": "ambra", "cine": "Andrei"},
               "ma": {"et": "Maria", "c": "accent", "cine": "Maria"}},
    "commituri": {"c1": {"m": "structura proiectului", "a": "baza"},
                  "c2": {"m": "colectare migrație", "a": "baza"},
                  "a1": {"m": "curățare migrație", "a": "an"},
                  "m1": {"m": "hartă pe județe", "a": "ma"},
                  "mg": {"m": "îmbinare", "a": "an", "merge": True}},
    "respins": "push respins: aici există un commit care lipsește la Andrei",
    "start": "Andrei, Maria și GitHub au același <code>dev</code>: fiecare și-a clonat depozitul. "
             "Fiecare coloană arată commit-urile, cel mai nou sus.",
    "stari": [
        {"an": _B, "gh": _B, "ma": _B},
        {"an": ["a1"] + _B, "gh": _B, "ma": _B},
        {"an": ["a1"] + _B, "gh": _B, "ma": ["m1"] + _B},
        {"an": ["a1"] + _B, "gh": ["m1"] + _B, "ma": ["m1"] + _B, "din": {"gh": "ma"}, "sag": {"2": "push"}},
        {"an": ["a1"] + _B, "gh": ["m1"] + _B, "ma": ["m1"] + _B, "rau": "gh", "sag": {"1": "push:rau"}},
        {"an": _DUPA, "gh": ["m1"] + _B, "ma": ["m1"] + _B, "din": {"an": "gh"}, "sag": {"1": "pull"}},
        {"an": _DUPA, "gh": _DUPA, "ma": ["m1"] + _B, "din": {"gh": "an"}, "sag": {"1": "push"}},
        {"an": _DUPA, "gh": _DUPA, "ma": _DUPA, "din": {"ma": "gh"}, "sag": {"2": "pull"}},
    ],
    "pasi": [
        {"cine": "Andrei", "cc": "ambra", "cmd": "commit", "full": "git commit -m \"curatare migratie\"",
         "t": "Local", "txt": "Commit-ul lui Andrei există doar pe laptopul lui."},
        {"cine": "Maria", "cc": "accent", "cmd": "commit", "full": "git commit -m \"harta pe judete\"",
         "t": "În paralel", "txt": "Maria lucrează la altceva și salvează și ea un commit."},
        {"cine": "Maria", "cc": "accent", "cmd": "push", "full": "git push", "t": "Maria trimite",
         "txt": "Commit-ul Mariei ajunge pe GitHub."},
        {"cine": "Andrei", "cc": "ambra", "cmd": "push", "rau": True,
         "full": "git push      ! [rejected]  dev -> dev (fetch first)", "t": "Refuzat",
         "txt": "GitHub are un commit pe care Andrei nu îl are. Git refuză push-ul, ca să nu se piardă "
                "munca Mariei."},
        {"cine": "Andrei", "cc": "ambra", "cmd": "pull", "full": "git pull", "t": "Întâi pull",
         "txt": "Commit-ul Mariei ajunge la Andrei și se unește cu al lui într-un commit de îmbinare. "
                "Dacă amândoi au schimbat aceleași rânduri, aici apare un conflict."},
        {"cine": "Andrei", "cc": "ambra", "cmd": "push", "full": "git push", "t": "Apoi push",
         "txt": "Acum push-ul trece: GitHub are ambele commit-uri."},
        {"cine": "Maria", "cc": "accent", "cmd": "pull", "full": "git pull", "t": "La zi",
         "txt": "Maria aduce ce îi lipsea. Toți trei au din nou același <code>dev</code>. Regula: "
                "<b>pull înainte de lucru și înainte de push</b>."},
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
    "sarcina": "Trei comenzi în terminal, în <code>proiect/</code>, și o adresă de pe GitHub. Rezultatul "
               "fiecăreia se lipește în câmpul ei.",
    "pasi": [
        {"t": "Pe dev, la zi cu GitHub", "cmd": "git status", "gol": "primele două rânduri",
         "cauta": r"\bdev\b[\s\S]*origin/dev",
         "daca_nu": "Rezultatul trebuie să conțină dev și origin/dev. Pe altă ramură: git switch dev. "
                    "Fără origin/dev, ramura nu este încă pe GitHub: git push -u origin dev."},
        {"t": "Commit-ul a ajuns pe GitHub", "cmd": "git log --oneline -3", "gol": "liniile afișate",
         "cauta": r"^(?:[^\n]*git log[^\n]*\n)?\s*[0-9a-f]{7,}[^\n]*origin/dev",
         "daca_nu": "Pe rândul ultimului commit trebuie să apară origin/dev. Dacă lipsește, commit-ul este "
                    "doar local: git pull, apoi git push."},
        {"t": "Datele nu sunt în depozit", "cmd": "git ls-files", "gol": "lista afișată",
         "cauta": r"^(?![\s\S]*\.csv)[\s\S]*\.ipynb",
         "daca_nu": "Lista arată ce urmărește Git: trebuie să conțină caietul și niciun .csv. Pentru un "
                    ".csv urmărit: git rm --cached cu numele lui, apoi data/ în .gitignore."},
        {"t": "Commit-ul, pe GitHub",
         "unde": "Pagina depozitului <b>›</b> Commits <b>›</b> commit-ul propriu <b>›</b> adresa din bara browserului",
         "gol": "https://github.com/dsw-ubb-2026/…/commit/…",
         "cauta": r"github\.com/dsw-ubb-2026/[^/\s]+/commit/[0-9a-f]{7,40}",
         "daca_nu": "Adresa trebuie să fie a unui commit din organizația dsw-ubb-2026."},
    ],
    "explicatie": "Munca echipei există acum în două locuri, local și pe GitHub, pe <code>dev</code>. Pe pagina "
                  "commit-ului se văd autorul, fișierele schimbate și rândurile modificate. Dacă lângă commit "
                  "apare un nume fără cont de GitHub, adresa de email din Git nu este cea a contului: "
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


sl("s1", "Cursul", "Planul lecției",
   "<h2>Versionare și colaborare cu Git</h2>"
   "<p class=\"cheie\">Datele colectate la cursul anterior intră acum, "
   "împreună cu codul de colectare, sub controlul versiunilor.</p>"
   + ix("agenda", "Planul lecției",
        {"static": True, "titlu": "Planul lecției",
         "etape": [{"nume": n, "unde": u, "text": d} for n, u, d in AGENDA]},
        "Detaliile apar la selectarea unei etape.")
   + nota("Caietul lecției", "<code>03_surse_diverse_si_preprocesare.ipynb</code>. Secțiunile 1-5 tratează datele (nomenclatorul, tabelul regional, migrația curățată de grupuri), iar secțiunea 6, Git.", True),
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
   "<li><b>Echipa</b><span>aleasă pe site, la cursul 2; depozitul ei se creează în această lecție.</span></li>"
   "</ul>"
   "<p>Deocamdată, toate există doar pe calculatorul local. Git le păstrează istoricul, "
   "iar GitHub le pune în comun pentru echipă.</p>"
   + ix("agenda", "Planul lecției",
        {"static": True, "titlu": "Planul lecției",
         "etape": [{"nume": n, "unde": u, "text": d} for n, u, d in AGENDA]})
   + nota("Caietul lecției", "<code>03_surse_diverse_si_preprocesare.ipynb</code>. Secțiunile 1-5 tratează datele (nomenclatorul, tabelul regional, migrația curățată de grupuri), iar secțiunea 6, Git.", True))

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

sl("s3", "Ce face Git", "Funcțiile lui Git",
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

sl("s4", "Ce face Git", "Cele trei zone",
   "<h2>Unde se află fișierele</h2>"
   "<p>Comenzile Git devin coerente odată ce se observă că fiecare mută "
   "fișiere între trei zone.</p>"
   + ix("zone", "Fișierele prin cele trei zone",
        {"id": "c3-zone",
         "sarcina": "Dosarul conține două fișiere. În ce ordine se selectează "
                    "comenzile pentru a le trimite pe GitHub? <code>git status</code> "
                    "nu mută nimic, dar arată starea curentă.",
         "fisiere": ["colectare.py", "README.md"]}),
   manual="<h2>Cele trei zone</h2>"
   "<p>Acesta este modelul conceptual care dă sens comenzilor Git. Fără el, "
   "comenzile rămân o listă de proceduri memorate, fără o logică comună.</p>"
   + ix("zone", "Fișierele prin cele trei zone",
        {"id": "c3-zone",
         "sarcina": "În ce ordine se selectează comenzile pentru a trimite cele două fișiere pe GitHub?",
         "fisiere": ["colectare.py", "README.md"]})
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

sl("s5", "Ce face Git", "Git sau GitHub",
   "<h2>Git sau GitHub</h2>"
   "<p class=\"cheie\">Două unelte diferite: una ține istoricul, cealaltă îl pune în comun.</p>"
   + GIT_GITHUB + EVALUARE,
   manual=
   "<h2>Git sau GitHub</h2>"
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
       ["se creează cu <code>git init</code>", "se creează din interfața GitHub"],
   ])
   + "<pre><code><span class=\"c\"># deschizi terminalul in dosarul proiectului</span>\n"
     "cd C:\\PROIECTE\\dsw-echipa-3\n\n"
     "<span class=\"c\"># porneste urmarirea</span>\ngit init\n\n"
     "<span class=\"c\"># prima intrebare, mereu: unde sunt?</span>\n"
     "git status</code></pre>"
   + nota("O eroare frecventă",
          "Rulat din greșeală în dosarul personal (home), <code>git init</code> "
          "pune sub urmărire întregul conținut al acestuia. Remedierea constă în "
          "ștergerea dosarului <code>.git</code> creat acolo; fișierele nu sunt "
          "afectate. În PowerShell, din dosarul respectiv: "
          "<code>Remove-Item -Recurse -Force .git</code>."))


# ===========================================================================
#  6-9. Primii pași
# ===========================================================================

# Depozitul echipei: pașii și folderul, mutați aici de la cursul 2; apar în
# manualul slide-ului „Depozitul echipei”, de la finalul lecției.
ARBORE_PROIECT = (
    '<span class="a">dsw/</span>\n'
    '├── <span class="x">.venv/</span>\n'
    '├── curs/            <span class="c"># personal, fără Git</span>\n'
    '└── <span class="a">proiect/</span>         <span class="c"># al echipei, cu Git</span>\n'
    '    ├── .git/        <span class="c"># istoricul</span>\n'
    '    └── README.md')

PE4_HTML = (
    '<ol class="pe4">'
    f'<li><span>1</span><b>Organizația</b><p><a class="leg" href="https://github.com/{REPO_ORG}" target="_blank" rel="noopener">{REPO_ORG}</a>, comună pentru grupă. Invitația vine pe e-mail.</p></li>'
    "<li><span>2</span><b>Depozitul echipei</b><p>Un membru îl creează în organizație și îi adaugă pe ceilalți.</p></li>"
    "<li><span>3</span><b>Adresa</b><p>Pe pagina depozitului: Code → HTTPS.</p></li>"
    "<li><span>4</span><b>Clonarea</b><p>În terminal, în dsw: <code>git clone &lt;adresa&gt; proiect</code></p></li>"
    "</ol>"
    '<div class="pe4__arb"><pre><code>' + ARBORE_PROIECT + "</code></pre>"
    '<p>Munca echipei stă în proiect/, cu Git; exercițiile de la curs rămân în curs/, fără Git.</p></div>')

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

sl("s8", "Primii pași", "Primul commit",
   "<h2>De la dosar la GitHub</h2>"
   + ix("commit", "Primul commit al echipei", COMMIT),
   manual="<h2>Primul commit</h2>"
   "<p>Pasul de Git din caietul 03, secțiunea 6, rulat în depozitul echipei, pe ramura <code>dev</code>. "
   "Fiecare comandă mută ceva între cele patru zone de la slide-ul anterior. Desenul pornește după "
   "clonare: istoricul local și GitHub au deja primul commit, creat odată cu depozitul.</p>"
   + ix("commit", "Primul commit al echipei", COMMIT)
   + "<p>În practică, ciclul obișnuit de lucru este același la fiecare pas al proiectului:</p>"
   "<pre><code><span class=\"c\"># unde sunt, ce s-a schimbat?</span>\ngit status\n\n"
   "<span class=\"c\"># ce intra in acest commit</span>\n"
   f"git add {_NB3}\n\n"
   "<span class=\"c\"># il scriu in istoric, cu un mesaj care spune ceva</span>\n"
   f"git commit -m \"{_MSG}\"\n\n"
   "<span class=\"c\"># il trimit colegilor</span>\ngit push</code></pre>"
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
       "id": "c3-ordine-commit", "poarta": False, "indiciu": "Întâi dosarul devine depozit. Urmează verificarea a ceea ce vede Git, adăugarea fișierului în zona de pregătire, o nouă verificare și abia apoi înregistrarea în istoric.",
       "iesire": "a1b2c3d (HEAD -> main) colectare migratie, Eurostat migr_pop1ctz",
       "sarcina": "Ordinea unui prim commit, de la dosar gol la istoric.",
       "linii": [
           "git init",
           "git status                      # ce vede Git",
           "git add code/migratie.py",
           "git status                      # acum e in pregatire",
           "git commit -m \"colectare migratie, Eurostat migr_pop1ctz\"",
           "git log --oneline               # a ramas scris"],
       "explicatie": "<code>git status</code> este comanda folosită cel mai des."}))

sl("s8b", "Primii pași", "Ce afișează git status",
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

sl("s9", "Primii pași", "Ce nu se versionează",
   "<h2>.gitignore</h2>"
   "<p class=\"cheie\">Depozitul se tratează ca public: o parolă urcată o dată rămâne în istoric.</p>"
   + ix("sortare", "Ce intră în depozit", {
       "id": "c3-sort-gitignore",
       "sarcina": "În ce categorie intră fiecare element?",
       "elemente": [
           {"t": "colectare.py", "cos": 0}, {"t": ".env cu parole", "cos": 1},
           {"t": "README.md", "cos": 0}, {"t": "venv/", "cos": 1},
           {"t": "date/brute/mic.csv", "cos": 0}, {"t": "date/brute/20GB.csv", "cos": 1},
           {"t": ".gitignore", "cos": 0}, {"t": "cheia de API", "cos": 1}],
       "cosuri": [{"t": "În depozit", "d": "cod, documentație, date mici"},
                  {"t": "Niciodată", "d": "secrete, mediul virtual, fișiere foarte mari"}],
       "laBine": "Fișierul <code>.gitignore</code> intră în depozit: este o "
                 "regulă comună a echipei, nu o preferință personală.",
       "explicatie": "Mediul virtual nu se versionează: se reface din "
                     "<code>requirements.txt</code> cu o singură comandă și ocupă "
                     "sute de megabytes. Datele mari nu se versionează pentru că Git "
                     "păstrează fiecare versiune: fiecare modificare a unui fișier de "
                     "mai mulți gigabytes adaugă încă o copie în istoric."})
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
   "<p>Un fișier text, aflat în rădăcina proiectului, care enumeră ce nu trebuie urmărit:</p>"
   "<pre><code><span class=\"c\"># mediul virtual si secretele</span>\n"
   "venv/\n.env\n\n"
   "<span class=\"c\"># datele: se aduc cu scriptul de colectare</span>\n"
   "data/\n*.csv\n*.parquet\n*.xlsx\n\n"
   "<span class=\"c\"># gunoiul uneltelor</span>\n"
   ".ipynb_checkpoints/\n__pycache__/\n*.pyc\n.vscode/\n.DS_Store\nThumbs.db</code></pre>"
   + "<p>După ce este scris, se adaugă în depozit ca orice alt fișier: "
     "<code>git add .gitignore</code>, <code>git commit -m \"add gitignore\"</code>, "
     "<code>git push</code>.</p>"
   + tabel(["Un fișier adăugat din greșeală trebuie…", "Comanda"], [
       ["doar scos din zona de pregătire (rămâne pe disc)", "~git reset -- \"nume fisier.ipynb\""],
       ["scos complet de sub urmărirea Git, dar păstrat în proiect", "~git rm --cached nume_fisier"],
   ])
   + ix("sortare", "Ce intră în depozit", {
       "id": "c3-sort-gitignore",
       "sarcina": "În ce categorie intră fiecare element?",
       "elemente": [
           {"t": "colectare.py", "cos": 0}, {"t": ".env cu parole", "cos": 1},
           {"t": "README.md", "cos": 0}, {"t": "venv/", "cos": 1},
           {"t": "date/brute/mic.csv", "cos": 0}, {"t": "date/brute/20GB.csv", "cos": 1},
           {"t": ".gitignore", "cos": 0}, {"t": "cheia de API", "cos": 1}],
       "cosuri": [{"t": "În depozit", "d": "cod, documentație, date mici"},
                  {"t": "Niciodată", "d": "secrete, mediul virtual, fișiere foarte mari"}],
       "laBine": "<code>.gitignore</code> intră în depozit: este o regulă comună a echipei.",
       "explicatie": "Git păstrează fiecare versiune a fiecărui fișier."}))


# ===========================================================================
#  10-13. GitHub
# ===========================================================================

sl("s11", "GitHub", "Legarea depozitelor",
   "<h2>Două feluri de a începe</h2>"
   + tabel(["Varianta 1: <code>git init</code>", "Varianta 2: <code>git clone</code>"], [
       ["nu există încă depozit pe GitHub", "depozitul echipei există deja pe GitHub"],
       ["<code>git init</code>, <code>add</code>, <code>commit</code>", "<code>git clone &lt;adresa&gt; proiect</code>"],
       ["<code>git branch -m master main</code>", "<code>cd proiect</code>"],
       ["<code>git remote add origin &lt;adresa&gt;</code>", "<code>git branch -vv</code>: main urmărește origin/main"],
       ["<code>git push -u origin main</code>", "legătura există deja"],
   ])
   + nota("La curs: varianta 2",
          "Un membru al echipei creează depozitul pe GitHub, iar ceilalți îl "
          "clonează. Clonarea aduce fișierele și întreaga istorie și configurează "
          f"automat <code>origin</code>. Toate comenzile: fișa {FISA}.", True),
   manual="<h2>Două feluri de a începe</h2>"
   f"<p>Ca în fișa {FISA}, există două variante, în funcție "
   "de existența depozitului pe GitHub.</p>"
   "<h3>Varianta 1: <code>git init</code></h3>"
   "<p>Se folosește doar dacă depozitul nu există încă pe GitHub.</p>"
   "<pre><code>git init                          <span class=\"c\"># depozit local, gol</span>\n"
   "git add .                         <span class=\"c\"># fisierele existente</span>\n"
   "git commit -m \"first commit\"\n"
   "git branch -m master main         <span class=\"c\"># ramura principala devine main</span>\n"
   "git remote add origin &lt;GitHub_URL&gt;\n"
   "git push -u origin main</code></pre>"
   "<h3>Varianta 2: <code>git clone</code>, cea de la curs</h3>"
   "<p>Se folosește când depozitul echipei există deja pe GitHub.</p>"
   "<pre><code>git clone https://github.com/dsw-ubb-2026/depozitul-echipei.git proiect\n"
   "cd proiect\n"
   "git status\n"
   "git branch -vv            <span class=\"c\"># main urmareste origin/main</span></code></pre>"
   "<h3>Caz special</h3>"
   "<p>Depozitul local a fost creat cu <code>git init</code>, dar depozitul de "
   "pe GitHub există deja și are conținut (de exemplu, un README). Cele două "
   "istorii nu au un punct comun, deci se unesc o singură dată:</p>"
   "<pre><code>git remote add origin &lt;GitHub_URL&gt;\n"
   "git pull origin main --allow-unrelated-histories\n"
   "git branch -u origin/main</code></pre>"
   + tabel(["Verificare", "Ce afișează"], [
       ["~git branch", "ramurile locale"],
       ["~git branch -r", "ramurile de pe GitHub (origin/...)"],
       ["~git branch -a", "toate ramurile"],
       ["~git branch -vv", "fiecare ramură și pe cine urmărește (upstream)"],
       ["~git remote -v", "adresa lui origin"],
   ])
   + ix("cod", "Legarea de GitHub", {
       "id": "c3-cod-remote", "poarta": False, "indiciu": "Comanda care gestionează depozitele la distanță se numește „remote”. "
                  "La primul push, -u memorează legătura; ramura principală este main.",
       "iesire": "origin  https://github.com/echipa/proiect.git (fetch)\norigin  https://github.com/echipa/proiect.git (push)\nbranch 'main' set up to track 'origin/main'.", "fisier": "terminal.sh",
       "sarcina": "Varianta 1: ce lipsește din comenzi?",
       "cod": "git branch -m master main\n"
              "git {{1}} add origin https://github.com/echipa/proiect.git\n"
              "git push {{2}} origin {{3}}",
       "goluri": {
           "1": {"ok": ["remote"], "ajutor": "comanda"},
           "2": {"ok": ["-u", "--set-upstream"], "ajutor": "opțiunea"},
           "3": {"ok": ["main"], "ajutor": "ramura"}},
       "laBine": "După primul push cu <code>-u</code>, este suficient <code>git push</code>.",
       "laRau": "Ramura este „main”.",
       "explicatie": "<code>-u</code> leagă ramura locală de cea de pe GitHub."})
   + ix("ordine", "De la dosar gol la depozit de echipă", {
       "id": "c3-ordine-github", "poarta": False,
       "sarcina": "Varianta 1, de la un dosar cu fișiere la un depozit pe GitHub.",
       "linii": [
           "git init",
           "se scrie .gitignore, ca secretele sa nu intre in primul commit",
           "git add .",
           "git commit -m \"structura proiectului si colectarea\"",
           "git branch -m master main",
           "se creeaza pe GitHub un depozit gol, fara README",
           "git remote add origin <adresa>",
           "git push -u origin main"],
       "explicatie": "<code>.gitignore</code> se scrie înainte de primul "
                     "<code>git add .</code>, nu după. Depozitul de pe "
                     "GitHub se creează gol: un README creat acolo este un commit "
                     "care nu există local, iar primul push este refuzat."}))

# ===========================================================================
#  14-16. În echipă
# ===========================================================================

sl("s14", "În echipă", "Ramuri",
   "<h2>Ramuri: o linie de lucru paralelă</h2>"
   + ix("ramuri", "Ramura de curățare", RAMURI),
   manual=
   "<h2>Ramuri</h2>"
   "<p>O ramură este o linie de lucru paralelă. Modificările de pe ea nu "
   "afectează <code>main</code>, care rămâne funcțional și gata de predare "
   "în orice moment. Comenzile se apasă în ordine; lângă graf, lista arată ce "
   "conține fișierul din dosar după fiecare comandă.</p>"
   + ix("ramuri", "Ramura de curățare", RAMURI)
   + tabel(["Comanda", "Ce face"], [
       ["~git branch", "listează ramurile și o marchează pe cea curentă"],
       ["~git switch -c curatare", "creează o ramură nouă și trece pe ea"],
       ["~git switch main", "revine pe main; fișierele din dosar devin cele de pe main"],
       ["~git merge curatare", "integrează în main modificările de pe ramură"],
       ["~git log --oneline --graph --decorate --all", "același graf, desenat în terminal"],
   ])
   + nota("De ce nu se lucrează direct pe main",
          "Pentru că orice modificare neterminată ar afecta întreaga echipă. "
          "Cu ramuri, main rămâne permanent o versiune funcțională, iar lucrul "
          "în desfășurare este izolat până la finalizare."))

FLUX_DEV = [
    ["o dată, un membru al echipei", "~git switch -c dev", "~git push -u origin dev"],
    ["o dată, ceilalți", "~git fetch", "~git switch dev"],
    ["zilnic, fiecare", "~git switch dev", "~git pull"],
    ["la fiecare commit", "~git add . ; git commit -m \"...\"", "~git pull ; git push"],
    ["după o sarcină importantă", "~git switch main ; git pull", "~git merge dev ; git push"],
]

sl("s14b", "În echipă", "Fluxul echipei",
   "<h2>Pull, apoi push</h2>"
   + ix("sincron", "Doi colegi și GitHub, pe dev", SINCRON),
   manual=
   "<h2>Fluxul echipei: main și dev</h2>"
   f"<p>Fluxul din fișa {FISA} folosește două ramuri. <code>main</code> "
   "este versiunea funcțională, cea care se predă. <code>dev</code> este ramura "
   "pe care lucrează zilnic întreaga echipă. Desenul arată ce se întâmplă pe "
   "<code>dev</code> când doi colegi lucrează în același timp: fiecare coloană este "
   "istoricul unui depozit, cu cel mai nou commit sus.</p>"
   + ix("sincron", "Doi colegi și GitHub, pe dev", SINCRON)
   + "<p>Conținutul din <code>dev</code> se integrează în <code>main</code> după fiecare sarcină "
     "importantă încheiată (curățarea datelor, setul de vizualizări, modelul): nu la fiecare commit, "
     "dar nici doar la final. Integrarea este îmbinarea de la slide-ul anterior: "
     "<code>git switch main</code>, <code>git merge dev</code>, <code>git push</code>.</p>"
   + tabel(["Cine, când", "Comanda", "Apoi"], FLUX_DEV)
   + nota("Fișiere separate",
          "Pe cât posibil, fiecare membru lucrează în fișiere separate (de exemplu "
          "<code>analiza_vlad.ipynb</code>, <code>analiza_maria.ipynb</code>). "
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
       "id": "c3-conflict", "fisier": "analiza.py", "ramura": "curatare",
       "sarcina": "O colegă a redenumit fișierul de date, iar codul local folosește "
                  "încă numele vechi. Care variantă trebuie să rămână în fișier?",
       "alMeu": 'd = pd.read_csv("date/brute/pop.csv")',
       "alLor": 'd = pd.read_csv("date/brute/populatie_ro.csv")',
       "bun": "lor",
       "deCe": "Fișierul cu numele vechi nu mai există: colega l-a redenumit "
               "și a trimis modificarea pe GitHub. Varianta locală ar produce o eroare la prima rulare.",
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
       "id": "c3-conflict", "fisier": "analiza.py", "ramura": "curatare",
       "sarcina": "O colegă a redenumit fișierul de date, iar codul local folosește "
                  "încă numele vechi. Care variantă trebuie să rămână în fișier?",
       "alMeu": 'd = pd.read_csv("date/brute/pop.csv")',
       "alLor": 'd = pd.read_csv("date/brute/populatie_ro.csv")',
       "bun": "lor",
       "deCe": "Fișierul cu numele vechi nu mai există.",
       "explicatie": "Git nu verifică dacă alegerea este corectă; verificarea revine persoanei care rezolvă conflictul."}))

sl("s16", "În echipă", "Regulile echipei",
   "<h2>Cinci reguli pentru acest semestru</h2>"
   + '<table class="tabel md reg2"><tbody>'
   + "".join(f'<tr><td class="md__n">{i}</td><td><b>{t}</b></td><td>{d}</td></tr>'
             for i, (t, d) in enumerate([
                 ("Lucrul se face pe dev", "<code>main</code> rămâne stabil și primește doar sarcini încheiate"),
                 ("Fiecare în fișierele lui", "caietele nu se îmbină ușor: două persoane în același caiet înseamnă conflict"),
                 ("<code>git pull</code> întâi", "la începutul lucrului și înainte de fiecare push"),
                 ("Mesaje descriptive", "ce s-a schimbat, nu „update”"),
                 ("Fără secrete, fără fișiere mari", "parolele și datele rămân în afara depozitului"),
             ], 1))
   + "</tbody></table>"
   + nota("Toate comenzile, pe o pagină",
          f"Fișa {FISA}: configurarea, clonarea, <code>.gitignore</code>, ramura dev, lucrul zilnic "
          "și îmbinarea în main. În <code>README.md</code> se notează cine răspunde de fiecare etapă.", True))


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

FACTORI_TAB = tabel(["Factorul", "Ipoteza", "Variabila", "Sursa"], [
    ["Distanța", "mai departe, legătură mai slabă", "distanța în km, granița comună", "GISCO; construite în C7"],
    ["Migrația", "mai mulți migranți la mie, legătură mai puternică", "migranți la 1.000 de locuitori", "Eurostat <code>migr_pop1ctz</code>; C2-C4"],
    ["Istoria comună", "minoritățile și granițele vechi păstrează legături", "limba, minoritățile, granițele vechi", "surse noi, alese de echipă"],
    ["Locurile", "orașele mari și bogate au legături mai întinse", "populația, densitatea, PIB pe locuitor", "Eurostat; C2-C3"],
])

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


sl("s22", "Proiectul echipei", "Depozitul echipei",
   "<h2>Depozitul echipei</h2>"
   + tabel(["Pasul", "Acțiunea"], [
       ["1", "un membru creează depozitul echipei în organizația <code>dsw-ubb-2026</code> și îi adaugă pe ceilalți"],
       ["2", "fiecare membru îl clonează local"],
       ["3", "<code>.gitignore</code> se scrie înainte de primul <code>add</code>"],
       ["4", "un membru creează ramura <code>dev</code>; ceilalți o preiau cu <code>git fetch</code>"],
       ["5", "scripturile de colectare de la cursul 2 se încarcă pe dev"],
       ["6", "în <code>README.md</code>: întrebarea de cercetare și responsabilitățile"],
   ]),
   manual=
   "<h2>Depozitul echipei</h2>"
   + tabel(["Pasul", "Acțiunea"], [
       ["1", "un membru creează depozitul echipei în organizația <code>dsw-ubb-2026</code> și îi adaugă pe ceilalți"],
       ["2", "fiecare membru îl clonează local"],
       ["3", "<code>.gitignore</code> se scrie înainte de primul <code>add</code>"],
       ["4", "un membru creează ramura <code>dev</code>; ceilalți o preiau cu <code>git fetch</code>"],
       ["5", "scripturile de colectare de la cursul 2 se încarcă pe dev"],
       ["6", "în <code>README.md</code>: întrebarea de cercetare și responsabilitățile"],
   ])
   + "<h3>Primii doi pași, în detaliu</h3>"
   + PE4_HTML
   + "<p><code>git clone</code> copiază depozitul cu tot cu istoricul lui, în folderul <code>.git/</code>, "
   "și reține adresa de la care a fost copiat. Ultimul cuvânt din comandă e numele folderului: fără el, "
   "folderul ar purta numele depozitului. Comanda se dă o singură dată, din <code>dsw</code>; dacă e dată "
   "din alt folder, de exemplu din <code>curs/</code>, depozitul ajunge acolo, iar căile din caiete nu "
   "mai sunt cele din manual.</p>"
   + nota("Git",
          'Se instalează de pe <a class="leg" href="https://git-scm.com/downloads" target="_blank" '
          'rel="noopener">git-scm.com</a>; instalarea se verifică cu <code>git --version</code>. La prima '
          "clonare, Git poate cere autentificarea în contul GitHub, într-o fereastră din browser.")
   + ix("dovada", "Verificarea depozitului", DOVADA))

sl("s22b", "Proiectul echipei", "Verificarea depozitului",
   "<h2>Verificarea depozitului</h2>"
   + ix("dovada", "Verificarea depozitului", DOVADA),
   manual="")

sl("s23", "Mai departe", "Pentru cursul următor",
   "<h2>La cursul 4: curățarea datelor</h2>"
   '<div class="fin3"><div class="fin3__g">'
   "<section><h4>Ce urmează la cursul 4</h4><ul>"
   "<li>Versionarea și colaborarea, aplicate pe depozitul echipei.</li>"
   "<li>Curățarea datelor: valori lipsă, duplicate, coduri ambigue (EL, NA).</li>"
   "<li>SCI și migrația, reunite în același tabel.</li>"
   "<li>Explorarea inițială, aprofundată.</li></ul></section>"
   "<section><h4>Pregătirea pentru cursul 4</h4><ul>"
   "<li>Depozitul echipei, cu scriptul de colectare.</li>"
   "<li><code>README.md</code> completat: întrebarea de cercetare și responsabilitățile fiecărui membru.</li>"
   "<li>Cel puțin un commit de la fiecare membru, ca dovadă că toți au acces la depozit.</li></ul></section>"
   "</div>"
   '<p class="fin3__a"><a class="leg" href="../">Pagina cursului 3</a>'
   '<a class="leg" href="../../c4-curatarea-datelor/">Cursul 4</a></p></div>')


if __name__ == "__main__":
    L.scrie_tot()
