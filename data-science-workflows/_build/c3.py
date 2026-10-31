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

from literatura import lecturi
from comun import Lectie, ix, verif, tabel, nota, REPO_ORG

def templu(acoperis, stalpi, baza, et_sus="Întrebarea"):
    """Un cadru teoretic desenat ca templu: literatura e temelia, pilonii
    sunt conceptele cu datele lor, iar întrebarea stă deasupra, pe toți."""
    st = "".join(
        f'<div class="pil__s"><div class="pil__n">{n}</div>'
        f'<div class="pil__d">{d}</div><div class="pil__r">{r}</div></div>'
        for n, d, r in stalpi)
    return (f'<div class="pil" style="--n:{len(stalpi)}">'
            f'<div class="pil__acoperis"><span>{et_sus}</span><b>{acoperis}</b></div>'
            f'<div class="pil__stalpi">{st}</div>'
            f'<div class="pil__baza"><span>temelia</span>{baza}</div></div>')


L = Lectie(3, "c3-versionare-git", "Versionare și colaborare cu Git",
           "Ce face Git, cum se leagă depozitul local de GitHub, cum lucrează "
           "în paralel membrii unei echipe și cum se încadrează teoretic un proiect de cercetare.")
sl = L.sl


# ===========================================================================
#  1-2. Cursul
# ===========================================================================

AGENDA = [
    ("Ce face Git", "azi", "Istoricul, revenirea la versiuni anterioare și lucrul local."),
    ("Depozitul și contul", "azi", "git init, credențiale, primul commit."),
    ("GitHub", "azi", "Legarea depozitului local de un depozit la distanță."),
    ("Lucrul în echipă", "azi", "Ramuri, pull request, conflicte."),
    ("Încadrarea teoretică", "azi", "De la un set de date la o întrebare de cercetare."),
    ("Explorarea inițială", "azi", "Prima examinare a datelor de migrație colectate la cursul 2."),
]

# Pașii pentru lecția 3: Git (caietul 03, secțiunea 6) și migrația (caietul 03, secțiunea 5).
# Cifrele migrației: Eurostat migr_pop1ctz, 2024, din rularea caietului (31 octombrie 2026).

_NB3 = "notebooks/03_surse_diverse_si_preprocesare.ipynb"
_MSG = "Pregatim tabelele regionale si migratia"
_Z = lambda v, e: {"t": "list", "v": v, "e": e}

PAS_GIT = {
    "fisier": "terminal.sh · caietul 03, secțiunea 6",
    "memoria": "cele trei zone (și GitHub)",
    "fixa": True,
    "intro": "Pasul de Git din caietul 03, aplicat în depozitul echipei. Panoul din dreapta nu mai arată memoria Python, "
             "ci cele trei zone ale lui Git și trecerea fișierelor dintr-o zonă în alta.",
    "cod": "git init\n"
           "git status --short\n\n"
           "echo \"data/\" > .gitignore\n"
           "git status --short\n\n"
           f"git add {_NB3} README.md .gitignore\n"
           "git status --short\n\n"
           f"git commit -m \"{_MSG}\"\n"
           "git log -1 --oneline\n"
           "git push",
    "pasi": [
        {"l": 1, "set": {"dosarul": _Z(["03_….ipynb", "README.md", "data/"], "zona 1"),
                         "pregătire": _Z([], "zona 2"), "istoric": _Z([], "zona 3")},
         "out": "Initialized empty Git repository in .../proiect/.git/",
         "txt": "<code>git init</code> transformă dosarul într-un depozit. Fișierele se află în <b>dosar</b> (03_….ipynb este caietul din <code>notebooks/</code>), dar zona de pregătire și istoricul sunt goale: Git nu a înregistrat încă nimic."},
        {"l": 2, "out": "?? README.md\n?? data/\n?? notebooks/",
         "txt": "<code>??</code> înseamnă că Git vede fișierul, dar nu îl urmărește. Apare și <code>data/</code>: zeci de MB care nu trebuie încărcați în depozit."},
        {"l": 4, "set": {"dosarul": _Z(["03_….ipynb", "README.md", ".gitignore"], "zona 1")},
         "txt": "<code>.gitignore</code> conține lista fișierelor pe care Git trebuie să le ignore. Datele nu se versionează: se descarcă din nou rulând caietul."},
        {"l": 5, "out": "?? .gitignore\n?? README.md\n?? notebooks/",
         "txt": "<code>data/</code> nu mai apare în listă. În schimb apare <code>.gitignore</code>: și el este un fișier al proiectului."},
        {"l": 7, "set": {"dosarul": _Z([], "zona 1"), "pregătire": _Z([".gitignore", "README.md", "03_….ipynb"], "zona 2")},
         "hl": {"var": "pregătire", "k": 2},
         "txt": "<code>git add</code> mută fișierele indicate în zona de <b>pregătire</b>. Se mută doar fișierele numite explicit."},
        {"l": 8, "out": f"A  .gitignore\nA  README.md\nA  {_NB3}",
         "txt": "<code>A</code> pe prima coloană: fișier adăugat în zona de pregătire. Aceste fișiere vor intra în commit."},
        {"l": 10, "set": {"pregătire": _Z([], "zona 2"), "istoric": _Z(["a1b2c3d Pregatim tabelele…"], "zona 3")},
         "out": f"[main (root-commit) a1b2c3d] {_MSG}\n 3 files changed",
         "txt": "<code>git commit</code> golește zona de pregătire și adaugă un punct în <b>istoric</b>, împreună cu mesajul. Mesajul descrie <b>ce</b> s-a schimbat, nu doar „update”."},
        {"l": 11, "out": f"a1b2c3d (HEAD -> main) {_MSG}",
         "txt": "Commit-ul este înregistrat în istoric. Se poate reveni oricând la această versiune."},
        {"l": 12, "set": {"GitHub": _Z(["a1b2c3d Pregatim tabelele…"], "acolo")},
         "txt": "Până în acest punct, totul exista doar pe calculatorul local. <code>git push</code> trimite istoricul pe GitHub, unde devine accesibil colegilor."},
    ],
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

sl("s7", "Primii pași", "Identitatea autorului",
   "<h2>Credențiale</h2>"
   "<p>Fiecare commit conține un nume și o adresă de email. Se configurează "
   "o singură dată pe calculator, nu pentru fiecare proiect.</p>"
   + ix("cod", "Configurarea identității", {
       "id": "c3-cod-config", "indiciu": "Opțiunea care face setarea valabilă pe tot calculatorul este „global”, precedată de două cratime. "
                  "Adresa este cea a contului de GitHub, scrisă între ghilimele.",
       "iesire": "user.name=Numele Tau\nuser.email=nume@stud.ubbcluj.ro\ncore.autocrlf=true", "fisier": "terminal.sh",
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
       "laBine": "Adresa trebuie să fie cea asociată contului de GitHub; altfel "
                 "commit-urile nu sunt legate de profilul respectiv.",
       "laRau": "Opțiunea începe cu două cratime. Adresa se scrie între ghilimele.",
       "explicatie": "<code>--global</code> scrie în configurarea "
                     "utilizatorului, deci setarea este valabilă pentru toate proiectele. "
                     "Fără această opțiune, setarea se aplică doar depozitului curent, "
                     "ceea ce este util atunci când un anumit proiect cere altă "
                     "identitate (de exemplu, un proiect realizat pentru o firmă)."}),
   manual=
   "<h2>Credențiale</h2>"
   "<p>Git înregistrează în fiecare commit autorul acestuia. Nu verifică "
   "datele: folosește exact valorile configurate. De aceea, cu o adresă "
   "greșită, commit-urile apar pe GitHub fără legătură cu vreun cont.</p>"
   + ix("cod", "Configurarea identității", {
       "id": "c3-cod-config", "indiciu": "Opțiunea care face setarea valabilă pe tot calculatorul este „global”, precedată de două cratime. "
                  "Adresa este cea a contului de GitHub, scrisă între ghilimele.",
       "iesire": "user.name=Numele Tau\nuser.email=nume@stud.ubbcluj.ro\ncore.autocrlf=true", "fisier": "terminal.sh",
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
       "laBine": "Adresa trebuie să fie cea asociată contului de GitHub.",
       "laRau": "Opțiunea începe cu două cratime.",
       "explicatie": "<code>--global</code> face setarea valabilă pentru toate proiectele."}))

sl("s8", "Primii pași", "Primul commit",
   "<h2>add, apoi commit</h2>"
   + ix("pas", "Primul commit, pas cu pas", PAS_GIT),
   manual="<h2>Ciclul de lucru</h2>"
   "<p>În practică, ciclul obișnuit de lucru este următorul:</p>"
   "<pre><code><span class=\"c\"># unde sunt?</span>\ngit status\n\n"
   "<span class=\"c\"># ce intra in acest commit</span>\n"
   "git add colectare/migratie.py\n\n"
   "<span class=\"c\"># il scriu in istoric, cu un mesaj care spune ceva</span>\n"
   "git commit -m \"colectare migratie, Eurostat migr_pop1ctz\"\n\n"
   "<span class=\"c\"># il trimit colegilor</span>\ngit push</code></pre>"
   + ix("pas", "Primul commit, pas cu pas", PAS_GIT)
   + nota("Frecvența commit-urilor",
          "Un commit nu este o livrare, ci un punct de revenire. Regula "
          "practică: câte un commit pentru fiecare unitate de lucru încheiată "
          "care poate fi descrisă printr-un mesaj scurt.")
   + ix("ordine", "Ordinea pașilor", {
       "id": "c3-ordine-commit", "poarta": False, "indiciu": "Întâi dosarul devine depozit. Urmează verificarea a ceea ce vede Git, adăugarea fișierului în zona de pregătire, o nouă verificare și abia apoi înregistrarea în istoric.",
       "iesire": "a1b2c3d (HEAD -> main) colectare migratie, Eurostat migr_pop1ctz",
       "sarcina": "Ordinea unui prim commit, de la dosar gol la istoric.",
       "linii": [
           "git init",
           "git status                      # ce vede Git",
           "git add colectare/migratie.py",
           "git status                      # acum e in pregatire",
           "git commit -m \"colectare migratie, Eurostat migr_pop1ctz\"",
           "git log --oneline               # a ramas scris"],
       "explicatie": "<code>git status</code> este comanda folosită cel mai des."}))

sl("s8b", "Primii pași", "Ce afișează git status",
   "<h2>Ce afișează git status</h2>"
   + ix("prezice", "Ce afișează git status", {
       "id": "c3-prezice-status", "fisier": "terminal.sh",
       "cod": "# doua fisiere modificate: migratie.py si README.md\n"
              "git add migratie.py\n"
              "git status --short",
       "intrebare": "Ce afișează git status --short?",
       "variante": ["M  migratie.py\n M README.md", "M  migratie.py\nM  README.md",
                    " M migratie.py\n M README.md", "nothing to commit"],
       "corect": 0,
       "indiciu": "În formatul --short, prima coloană corespunde zonei de pregătire, a doua dosarului de lucru. Ce fișier a fost adăugat cu add?",
       "laBine": "În commit intră doar ce a fost adăugat cu add.",
       "explicatie": "<code>M</code> pe prima coloană: modificat și adăugat în zona de pregătire (intră în commit). "
                     "<code>M</code> pe a doua: modificat, dar prezent doar în dosarul de lucru. Un <code>git commit</code> "
                     "rulat acum ar include doar <code>migratie.py</code>; <code>README.md</code> ar rămâne în afara commit-ului."}),
   manual="")

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
          "automat <code>origin</code>.", True),
   manual="<h2>Două feluri de a începe</h2>"
   "<p>Ca în fișa „Lucrul cu Git” de la curs, există două variante, în funcție "
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
   "<h2>Rolul ramurilor</h2>"
   "<p>O ramură este o linie de lucru paralelă. Modificările de pe ea nu "
   "afectează <code>main</code>.</p>"
   + ix("ramuri", "Graful ramurilor",
        {"id": "c3-ramuri",
         "sarcina": "Secvența de lucru: crearea unei ramuri, două commit-uri pe ea, "
                    "revenirea pe main și îmbinarea ramurii. Graful se actualizează la fiecare pas."})
   + "<p class=\"cheie\">Regula echipei: <code>main</code> trebuie să funcționeze "
     "în orice moment. Lucrul în desfășurare se face pe o ramură separată.</p>",
   manual=
   "<h2>Ramuri</h2>"
   "<p>O ramură este o linie de lucru paralelă. Modificările de pe ea nu "
   "afectează <code>main</code>, care rămâne funcțional și gata de predare "
   "în orice moment.</p>"
   + ix("ramuri", "Graful ramurilor",
        {"id": "c3-ramuri",
         "sarcina": "Secvența de lucru: crearea unei ramuri, două commit-uri pe ea, "
                    "revenirea pe main și îmbinarea ramurii."})
   + tabel(["Comanda", "Ce face"], [
       ["~git branch", "listează ramurile și o marchează pe cea curentă"],
       ["~git switch -c curatare", "creează o ramură nouă și trece pe ea"],
       ["~git switch main", "revine pe main"],
       ["~git merge curatare", "integrează în main modificările de pe ramură"],
   ])
   + nota("De ce nu se lucrează direct pe main",
          "Pentru că orice modificare neterminată ar afecta întreaga echipă. "
          "Cu ramuri, main rămâne permanent o versiune funcțională, iar lucrul "
          "în desfășurare este izolat până la finalizare."))

# --------------------------------------------------------------------------
# Fluxul echipei din fișa „Lucrul cu Git”: main și dev. Fiecare pas e o
# comandă; panourile arată ce commit-uri are fiecare depozit și unde stau
# etichetele (ramurile). x = coloana, r = rândul pe desen.
# --------------------------------------------------------------------------

COMMITURI = {
    "c1": {"x": 0, "r": 0, "autor": "baza", "mesaj": "structura proiectului"},
    "c2": {"x": 1, "r": 0, "autor": "baza", "mesaj": "colectare migratie", "parinti": ["c1"]},
    "y1": {"x": 2, "r": 1, "autor": "tu", "mesaj": "curatare migratie", "parinti": ["c2"]},
    "m1": {"x": 2, "r": 2, "autor": "maria", "mesaj": "harta pe judete", "parinti": ["c2"]},
    "x1": {"x": 3, "r": 1, "autor": "tu", "merge": True, "mesaj": "merge origin/dev", "parinti": ["y1", "m1"]},
}


def stare(commits, et, head=None):
    return {"commits": commits, "et": et, "head": head}


B = ["c1", "c2"]
GITDAG = {
    "commituri": COMMITURI,
    "autori": {"baza": {"et": "commit-urile inițiale", "c": "text-3"},
               "tu": {"et": "commit-urile locale", "c": "ceas"},
               "maria": {"et": "commit-urile Mariei", "c": "accent"}},
    "pasi": [
        {"t": "Depozitul clonat", "cmd": "git clone <adresa> proiect",
         "txt": "Depozitul local și cel de pe GitHub au aceleași două commit-uri. "
                "Eticheta <code>main</code> indică ultimul commit. HEAD arată ramura curentă.",
         "L": stare(B, {"main": "c2"}, "main"), "R": stare(B, {"main": "c2"})},
        {"t": "Un membru al echipei creează dev", "cmd": "git switch -c dev",
         "txt": "O ramură nouă este doar o etichetă nouă pe același commit; nu se "
                "copiază nimic. HEAD trece pe dev.",
         "L": stare(B, {"main": "c2", "dev": "c2"}, "dev"), "R": stare(B, {"main": "c2"})},
        {"t": "Ramura dev pe GitHub", "cmd": "git push -u origin dev", "sus": True,
         "txt": "Acum există și <code>origin/dev</code>. Colegii o preiau cu "
                "<code>git fetch</code> și <code>git switch dev</code>.",
         "L": stare(B, {"main": "c2", "dev": "c2"}, "dev"), "R": stare(B, {"main": "c2", "dev": "c2"})},
        {"t": "Un commit local", "cmd": "git commit -m \"curatare migratie\"",
         "txt": "Un commit nou, doar în depozitul local. Eticheta dev avansează "
                "pe el; main rămâne neschimbat.",
         "L": stare(B + ["y1"], {"main": "c2", "dev": "y1"}, "dev"),
         "R": stare(B, {"main": "c2", "dev": "c2"})},
        {"t": "Între timp, Maria", "cmd": "git push", "cine": "maria $",
         "txt": "Maria a lucrat tot pe dev și a trimis modificările mai devreme. Pe GitHub, "
                "dev indică acum commit-ul ei. Depozitul local nu conține încă acest commit.",
         "L": stare(B + ["y1"], {"main": "c2", "dev": "y1"}, "dev"),
         "R": stare(B + ["m1"], {"main": "c2", "dev": "m1"})},
        {"t": "Push refuzat", "cmd": "git push   ✗ rejected (fetch first)", "rau": True,
         "txt": "GitHub are un commit care lipsește local. Git refuză push-ul, pentru a nu "
                "suprascrie commit-ul Mariei. De aceea regula din fișă este: <b>pull, apoi push</b>.",
         "L": stare(B + ["y1"], {"main": "c2", "dev": "y1"}, "dev"),
         "R": stare(B + ["m1"], {"main": "c2", "dev": "m1"})},
        {"t": "Preluarea modificărilor", "cmd": "git pull", "jos": True,
         "txt": "Commit-ul Mariei este adus local, iar Git îl reunește cu commit-ul local "
                "într-un commit de îmbinare (cel cu contur). Dacă aceleași rânduri "
                "au fost modificate de ambele părți, în acest punct apare un conflict.",
         "L": stare(B + ["y1", "m1", "x1"], {"main": "c2", "dev": "x1"}, "dev"),
         "R": stare(B + ["m1"], {"main": "c2", "dev": "m1"})},
        {"t": "Push reușit", "cmd": "git push", "sus": True,
         "txt": "Commit-ul local și cel de îmbinare ajung pe GitHub. Depozitul local "
                "și cel de pe GitHub au din nou același dev.",
         "L": stare(B + ["y1", "m1", "x1"], {"main": "c2", "dev": "x1"}, "dev"),
         "R": stare(B + ["y1", "m1", "x1"], {"main": "c2", "dev": "x1"})},
        {"t": "Sarcină încheiată: trecerea pe main", "cmd": "git switch main && git pull",
         "txt": "Curățarea este finalizată, deci poate fi integrată în main. Mai "
                "întâi, main devine ramura curentă și este adus la zi.",
         "L": stare(B + ["y1", "m1", "x1"], {"main": "c2", "dev": "x1"}, "main"),
         "R": stare(B + ["y1", "m1", "x1"], {"main": "c2", "dev": "x1"})},
        {"t": "Integrarea dev în main", "cmd": "git merge dev",
         "txt": "Main nu are commit-uri noi, deci eticheta main avansează direct pe "
                "ultimul commit din dev (fast-forward). Commit-urile nu se mută și nu "
                "se copiază: se mută doar eticheta.",
         "L": stare(B + ["y1", "m1", "x1"], {"main": "x1", "dev": "x1"}, "main"),
         "R": stare(B + ["y1", "m1", "x1"], {"main": "c2", "dev": "x1"})},
        {"t": "Ramura main pe GitHub", "cmd": "git push", "sus": True,
         "txt": "Ramura main de pe GitHub conține acum tot ce s-a lucrat și verificat "
                "pe dev. Ciclul se reia de la pasul 4.",
         "L": stare(B + ["y1", "m1", "x1"], {"main": "x1", "dev": "x1"}, "main"),
         "R": stare(B + ["y1", "m1", "x1"], {"main": "x1", "dev": "x1"})},
    ],
}

FLUX_DEV = [
    ["o dată, un membru al echipei", "~git switch -c dev", "~git push -u origin dev"],
    ["o dată, ceilalți", "~git fetch", "~git switch dev"],
    ["zilnic, fiecare", "~git switch dev", "~git pull"],
    ["la fiecare commit", "~git add . ; git commit -m \"...\"", "~git pull ; git push"],
    ["după o sarcină importantă", "~git switch main ; git pull", "~git merge dev ; git push"],
]

sl("s14b", "În echipă", "Fluxul echipei",
   "<h2>main și dev, pas cu pas</h2>"
   + ix("gitdag", "Ce se întâmplă cu commit-urile", GITDAG),
   manual=
   "<h2>Fluxul echipei: main și dev</h2>"
   "<p>Fluxul din fișa „Lucrul cu Git” folosește două ramuri. <code>main</code> "
   "este versiunea funcțională, cea care se predă. <code>dev</code> este ramura "
   "pe care lucrează zilnic întreaga echipă. Conținutul din dev se integrează "
   "în main după fiecare sarcină importantă încheiată (curățarea datelor, setul "
   "de vizualizări, modelul): nu la fiecare commit, dar nici doar la final.</p>"
   + ix("gitdag", "Ce se întâmplă cu commit-urile", GITDAG)
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
   "<h2>Patru reguli pentru acest semestru</h2>"
   + '<table class="tabel md reg2"><tbody>'
   + "".join(f'<tr><td class="md__n">{i}</td><td><b>{t}</b></td><td>{d}</td></tr>'
             for i, (t, d) in enumerate([
                 ("<code>git pull</code> întâi", "pe dev, înainte de a începe lucrul și înainte de push"),
                 ("Lucrul se face pe dev", "<code>main</code> primește doar sarcini încheiate"),
                 ("Mesaje descriptive", "ce s-a schimbat, nu „update”"),
                 ("Fără secrete, fără fișiere mari", "parolele și datele mari rămân în afara depozitului"),
             ], 1))
   + "</tbody></table>"
   + nota("Responsabilități",
          "În <code>README.md</code> se notează cine răspunde de fiecare etapă: "
          "colectare, curățare, analiză, raport. Scopul este ca fiecare membru "
          "să știe cui se adresează pentru o anumită parte.", True))


# ===========================================================================
#  17-20. Încadrarea teoretică
# ===========================================================================

sl("s17", "Cadrul teoretic", "De ce un cadru",
   "<h2>Încadrarea teoretică</h2>"
   "<p class=\"cheie\">Datele nu generează întrebări. Întrebările provin din "
   "teorie, iar datele pot susține sau infirma răspunsurile propuse.</p>"
   + tabel(["Tipul", "La ce răspunde", "Când intră în flux", "În proiectul cursului"], [
       ["<strong>Teoria</strong>", "mecanismele care explică fenomenul: concepte și ipoteze", "la definirea întrebării", "rețelele de migranți, câmpurile de migrație"],
       ["<strong>Metoda</strong>", "cum au fost măsurate conceptele și ce modele s-au folosit", "la analiză și la model", "log SCI explicat prin distanță și graniță"],
       ["<strong>Documentația</strong>", "cum se folosește corect fiecare sursă și unealtă", "la fiecare pas de cod", "API-ul Eurostat, pandas, networkx"],
       ["<strong>Datele</strong>", "proveniența datelor și ce măsoară fiecare variabilă", "oriunde sunt folosite", "articolul care descrie SCI 2026"],
   ]),
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
   + tabel(["Tipul", "La ce răspunde", "Când intră în flux", "În proiectul cursului"], [
       ["<strong>Teoria</strong>", "mecanismele care explică fenomenul: concepte și ipoteze", "la definirea întrebării", "rețelele de migranți, câmpurile de migrație"],
       ["<strong>Metoda</strong>", "cum au fost măsurate conceptele și ce modele s-au folosit", "la analiză și la model", "log SCI explicat prin distanță și graniță"],
       ["<strong>Documentația</strong>", "cum se folosește corect fiecare sursă și unealtă", "la fiecare pas de cod", "API-ul Eurostat, pandas, networkx"],
       ["<strong>Datele</strong>", "proveniența datelor și ce măsoară fiecare variabilă", "oriunde sunt folosite", "articolul care descrie SCI 2026"],
   ]))

PILONI = [
    ("Economie", "WDI: PIB/locuitor, populație, urbanizare",
     "Peisajul: capacitatea de a investi și cererea de energie. Explică "
     "diferențele dintre țări și intră în regresii."),
    ("Instituții", "WGI: Government Effectiveness",
     "Modelul de guvernanță: capacitatea de a pune în practică. Explică "
     "variația dintre țări aflate la același nivel economic."),
    ("Sistem energetic", "EIA: cărbune, eolian, solar, hidro, nuclear, CO₂",
     "Regimul și nișele: structura energetică, blocajele moștenite, creșterea "
     "regenerabilelor. Baza clusterizării."),
]

sl("s18", "Cadrul teoretic", "Căutarea literaturii",
   "<h2>Căutarea literaturii</h2>"
   "<p>Scopul nu este „tot ce s-a scris”, ci literatura relevantă pentru "
   "întrebarea echipei, pornind de la o sursă de încredere.</p>"
   + ix("ordine", "Pașii căutării", {
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
                     "secțiunea de cadru teoretic a raportului."}),
   manual="<h2>Căutarea literaturii</h2>"
   "<p>O căutare bună nu începe cu un motor de căutare, ci cu un articol de "
   "încredere. Pentru proiectul cursului, acesta este Bailey și colegii (2018), "
   "articolul care a introdus indicele SCI. De la el, căutarea merge în două "
   "direcții: înapoi, prin referințele lui, și înainte, prin lucrările care l-au "
   "citat ulterior.</p>"
   + ix("ordine", "Pașii căutării", {
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
                     "secțiunea de cadru teoretic a raportului."})
   + "<p>Fiecare lucrare găsită se notează pe un rând, cu aceleași coloane. Matricea "
   "este principalul rezultat al căutării: din ea se scrie secțiunea de cadru "
   "teoretic a raportului, și tot ea arată ce nu a fost încă studiat.</p>"
   + tabel(["Lucrarea", "Întrebarea", "Datele", "Metoda", "Ce se preia"], [
       ["Bailey și colegii (2018)", "ce măsoară SCI, ce îl explică", "SCI, comitate SUA și țări", "descriptiv, regresii pe distanță", "definiția, scăderea cu distanța, legătura cu migrația"],
       ["Sandu (2025)", "cum se leagă județele de destinațiile emigrației", "fluxuri NUTS3 × 6 țări, 2011-2021", "regresii, analiză factorială", "reperul de comparație pentru harta diasporei din SCI"],
   ])
   + lecturi(["scholar", "semantic", "zotero"], "Unelte"))

PILONI_NOI = [
    ("Legăturile", "SCI, Meta: perechi de țări, regiuni, județe",
     "Ce locuri sunt conectate și cât de puternic."),
    ("Oamenii", "Eurostat migr_pop1ctz: cetățeni pe țări",
     "Unde au emigrat persoanele care mențin legăturile."),
    ("Locul", "GISCO: distanță, graniță; Eurostat: PIB, populație",
     "Factorii care explică legăturile independent de migrație."),
]

sl("s19", "Cadrul teoretic", "Cadrul proiectului",
   "<h2>Cadrul proiectului, ca un templu</h2>"
   + templu("Cât din legăturile dintre locuri se explică prin oamenii care "
            "au migrat între ele?", PILONI_NOI,
            "Bailey și colegii (2018, 2020) despre legături; Palloni și colegii (2001) și de Haas (2010) despre rețelele de migranți; Sandu (2005, 2025) despre migrația românească")
   + "<p class=\"cheie\">Distanța explică mult, migrația explică o parte "
     "suplimentară. Întrebarea centrală: ce rămâne neexplicat de ambele?</p>",
   manual="<h2>Cadrul proiectului: legături și migrație</h2>"
   "<p>Un cadru teoretic poate fi reprezentat ca un templu: întrebarea deasupra, conceptele cu datele lor ca piloni, literatura ca temelie. "
   "Temelia este literatura despre sistemele migratorii: locurile legate prin "
   "migrație rămân legate și prin fluxuri de informație, bani și vizite, iar "
   "rețelele de migranți facilitează migrația celor care urmează. Indicele SCI "
   "permite observarea directă a unei părți din aceste legături.</p>"
   + templu("Cât din legăturile dintre locuri se explică prin oamenii care "
            "au migrat între ele?", PILONI_NOI,
            "Bailey și colegii (2018, 2020) despre legături; Palloni și colegii (2001) și de Haas (2010) despre rețelele de migranți; Sandu (2005, 2025) despre migrația românească")
   + "<h3>Întrebările derivate din cadru</h3>"
   "<ol>"
   "<li><em>Migrația:</em> sunt perechile de țări cu mai mulți migranți mai "
   "puternic conectate, la aceeași distanță?</li>"
   "<li><em>Istoria:</em> generează granițele istorice și minoritățile (de "
   "exemplu, în cazul României și al Ungariei) legături pe care migrația "
   "recentă nu le explică?</li>"
   "<li><em>Ce rămâne:</em> unde sunt legăturile mai puternice decât prezic "
   "distanța și migrația împreună și ce au în comun aceste locuri?</li>"
   "</ol>"
   + nota("Contribuția echipelor",
          "Fiecare echipă alege o parte a cadrului: un coridor (de exemplu, "
          "România și Italia) sau o țară analizată la nivel regional. Se poate "
          "adăuga un pilon nou, de exemplu limba sau religia, cu condiția să "
          "poată fi măsurat.")
   + lecturi(["bailey2018", "palloni2001", "dehaas2010", "sandu2005", "sandu2025", "bailey2020"], "Literatura cadrului"))

sl("s20", "Cadrul teoretic", "Întrebarea echipei",
   "<h2>Întrebarea echipei</h2>"
   "<p>Două sau trei rânduri. Formularea nu trebuie să fie definitivă, dar "
   "trebuie să existe.</p>"
   + ix("asteptari", "Întrebarea de cercetare", {
       "id": "c3-intrebare", "tip": "intrebare", "minim": 60,
       "sarcina": "Care este întrebarea la care vrea să răspundă echipa și "
                  "din ce pilon provine contribuția ei?",
       "exemplu": "De exemplu: sunt regiunile din Italia cu mai mulți români "
                  "și cele mai conectate cu România, sau legătura urmează altă "
                  "logică decât migrația?",
       "multumesc": "Răspunsul a fost înregistrat. Feedbackul va fi transmis înainte de cursul următor."}))


# ===========================================================================
#  21-23. Datele și proiectul
# ===========================================================================

sl("s21n", "Datele", "Regiunile, într-un tabel",
   "<h2>Șase fișiere, un tabel</h2>"
   + ix("pas", "Indicatorii într-un singur tabel", PAS_NUTS),
   manual=
   "<h2>Regiunile, într-un tabel</h2>"
   "<p>Fiecare fișier din C2 are câte un rând pe regiune, cu un cod NUTS. Denumirile "
   "regiunilor provin din nomenclatorul Eurostat GISCO, pe care caietul îl descarcă cu "
   "<code>requests</code>; lungimea codului indică nivelul: 2 caractere țara, 4 regiunea, "
   "5 județul. Indicatorii se pun apoi într-un singur tabel.</p>"
   + ix("pas", "Indicatorii într-un singur tabel", PAS_NUTS)
   + nota("De ce format lung, nu lat",
          "Un rând pentru fiecare combinație de regiune, indicator și nivel. Astfel, un "
          "indicator nou se adaugă fără coloane noi, iar valorile lipsă se numără direct. "
          "În C4, tabelul se transformă în format lat, cu un rând pe regiune.", True)
   + "<p>Același pas se aplică și datelor SCI: coloanele cu nume în engleză sunt "
     "redenumite după semnificația lor în proiect (<code>user_region</code> devine "
     "<code>regiune_1</code>, <code>scaled_sci</code> devine <code>sci</code>). "
     "La NUTS 2, tabelul are 298 × 298 = 88.804 rânduri: fiecare regiune cu fiecare, "
     "inclusiv cu ea însăși, iar fiecare pereche apare în ambele ordini.</p>")

sl("s21b", "Datele", "Țări și grupuri de țări",
   "<h2>Țări și grupuri de țări</h2>"
   + ix("pas", "Țări și grupuri de țări", PAS_TARI),
   manual=
   "<h2>Țări și grupuri de țări</h2>"
   "<p>Înainte de orice analiză: aceleași patru comenzi, de fiecare dată.</p>"
   + ix("cod", "Explorare inițială", {
       "id": "c3-cod-explorare", "poarta": False, "indiciu": "Dimensiunea tabelului este un atribut (fără paranteze), numit „formă” în engleză. Rezumatul pe coloane este metoda „informații”. Valorile lipsă se însumează cu metoda „sumă”.",
       "iesire": "(5104, 3)\n<class 'pandas.core.frame.DataFrame'>\nRangeIndex: 5104 entries ...\ngeo           0\ncitizen       0\nvaloare     812", "fisier": "explorare.py",
       "sarcina": "Ce lipsește din primele patru operații aplicate unui tabel nou?",
       "cod": "import pandas as pd\n\n"
              "d = pd.read_csv(\"date/brute/migratie.csv\")\n\n"
              "# cate randuri si cate coloane\nprint(d.{{1}})\n\n"
              "# ce coloane, ce tipuri, cate valori lipsesc\nd.{{2}}()\n\n"
              "# cum arata primele randuri\nprint(d.head())\n\n"
              "# cate valori lipsesc, pe coloana\nprint(d.isna().{{3}}())",
       "goluri": {
           "1": {"ok": ["shape"], "ajutor": "atributul"},
           "2": {"ok": ["info"], "ajutor": "metoda"},
           "3": {"ok": ["sum"], "ajutor": "metoda"}},
       "laBine": "Cele patru comenzi se aplică în această ordine pe orice "
                 "tabel nou. Datele de migrație au multe valori lipsă, "
                 "corespunzătoare țărilor care nu raportează. Tratarea lor se face la cursul 4.",
       "laRau": "Prima este un atribut, deci se scrie fără paranteze. Celelalte sunt metode.",
       "explicatie": "<code>info()</code> este cea mai informativă: afișează simultan "
                     "numărul de rânduri, tipurile coloanelor și numărul de valori "
                     "non-nule din fiecare. O coloană care ar trebui să fie "
                     "numerică, dar apare ca <code>object</code>, semnalează o "
                     "problemă încă de la început."})
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
   + ix("dovada", "Verificarea depozitului", {
       "id": "c3-dovada-depozit",
       "sarcina": "Comenzile se rulează local; rezultatul din terminal se lipește în câmpul lui.",
       "pasi": [
           {"t": "Depozitul este legat de GitHub",
            "cmd": "git remote -v",
            "gol": "prima linie afișată",
            "cauta": r"github\.com",
            "daca_nu": "Rezultatul nu conține o adresă GitHub: comanda "
                       "git remote add origin nu a fost încă rulată."},
           {"t": "Cel puțin două commit-uri",
            "cmd": "git log --oneline | head -3",
            "gol": "liniile afișate",
            "cauta": r"[0-9a-f]{7}[\s\S]*[0-9a-f]{7}",
            "daca_nu": "Sunt necesare cel puțin două hash-uri de commit. Unul "
                       "singur indică faptul că toată munca a fost încărcată "
                       "într-un singur commit, la final."},
           {"t": "Ramura dev există și pe GitHub",
            "cmd": "git branch -a",
            "gol": "lista afișată",
            "cauta": r"remotes/origin/dev",
            "daca_nu": "Lipsește remotes/origin/dev. Un membru al echipei rulează "
                       "git switch -c dev și git push -u origin dev; ceilalți "
                       "rulează git fetch."},
           {"t": "Secretele sunt excluse",
            "cmd": "git check-ignore -v .env venv",
            "gol": "rezultatul afișat",
            "cauta": r"\.gitignore",
            "daca_nu": "Rezultatul trebuie să conțină numele fișierului .gitignore. "
                       "Dacă comanda nu afișează nimic, regulile nu se aplică."}],
       "explicatie": "Dacă toate cele patru verificări trec, munca echipei există în "
                     "două locuri și se poate urmări cine ce a făcut. De aici înainte, "
                     "fiecare curs adaugă o componentă în același depozit."}))

sl("s22b", "Proiectul echipei", "Verificarea depozitului",
   "<h2>Verificarea depozitului</h2>"
   + ix("dovada", "Verificarea depozitului", {
       "id": "c3-dovada-depozit",
       "sarcina": "Comenzile se rulează local; rezultatul din terminal se lipește în câmpul lui.",
       "pasi": [
           {"t": "Depozitul este legat de GitHub",
            "cmd": "git remote -v",
            "gol": "prima linie afișată",
            "cauta": r"github\.com",
            "daca_nu": "Rezultatul nu conține o adresă GitHub: comanda "
                       "git remote add origin nu a fost încă rulată."},
           {"t": "Cel puțin două commit-uri",
            "cmd": "git log --oneline | head -3",
            "gol": "liniile afișate",
            "cauta": r"[0-9a-f]{7}[\s\S]*[0-9a-f]{7}",
            "daca_nu": "Sunt necesare cel puțin două hash-uri de commit. Unul "
                       "singur indică faptul că toată munca a fost încărcată "
                       "într-un singur commit, la final."},
           {"t": "Ramura dev există și pe GitHub",
            "cmd": "git branch -a",
            "gol": "lista afișată",
            "cauta": r"remotes/origin/dev",
            "daca_nu": "Lipsește remotes/origin/dev. Un membru al echipei rulează "
                       "git switch -c dev și git push -u origin dev; ceilalți "
                       "rulează git fetch."},
           {"t": "Secretele sunt excluse",
            "cmd": "git check-ignore -v .env venv",
            "gol": "rezultatul afișat",
            "cauta": r"\.gitignore",
            "daca_nu": "Rezultatul trebuie să conțină numele fișierului .gitignore. "
                       "Dacă comanda nu afișează nimic, regulile nu se aplică."}],
       "explicatie": "Dacă toate cele patru verificări trec, munca echipei există în "
                     "două locuri și se poate urmări cine ce a făcut. De aici înainte, "
                     "fiecare curs adaugă o componentă în același depozit."}),
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
