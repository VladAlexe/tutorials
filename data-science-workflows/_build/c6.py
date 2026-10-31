# -*- coding: utf-8 -*-
"""
Lecția 6: Analiza exploratorie.

Urmează planul cursului de anul trecut (Curs 6. EDA și EDA Multivariate):
întrebările care vin din cadru, analiza univariată (describe, asimetrie,
transformarea logaritmică, top-uri), analiza bivariată (nor de puncte,
corelații), variabilele categorice (tabel de contingență, χ², Cramér's V,
diferențe între grupuri) și harta.

Toate graficele sunt pe datele adevărate ale cursului: cele 263 de perechi de
țări pentru care avem și SCI, și migrația în ambele direcții (date/eda-perechi.json,
făcut din caietul cursului 7). Nimic inventat: dacă un număr apare pe slide,
iese din fișierul ăla.

Rulare:  python _build/c6.py
"""

import json
import math

from literatura import lecturi
from comun import Lectie, ix, verif, tabel, nota, surse, RAD

L = Lectie(6, "c6-analiza-exploratorie", "Analiza exploratorie",
           "Examinarea datelor înainte de modelare: distribuții, relații, "
           "categorii, hărți și grafice care induc în eroare.")
sl = L.sl


# --------------------------------------------------------------------------
# Datele. Statisticile de pe slide-uri se calculează aici, din același fișier
# pe care îl desenează componentele, ca să nu poată diverge.
# --------------------------------------------------------------------------

D = json.loads((RAD / "date" / "eda-perechi.json").read_text(encoding="utf-8"))
P = D["perechi"]


def pearson(x, y):
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    return sxy / math.sqrt(sxx * syy)


LS = [math.log10(p["sci"]) for p in P]
LD = [math.log10(p["dist"]) for p in P]
LM = [math.log10(p["la_mie"]) for p in P]
GR = [1.0 if p["g"] else 0.0 for p in P]
R = {("sci", "dist"): pearson(LS, LD), ("sci", "migr"): pearson(LS, LM),
     ("sci", "gr"): pearson(LS, GR), ("dist", "migr"): pearson(LD, LM),
     ("dist", "gr"): pearson(LD, GR), ("migr", "gr"): pearson(LM, GR)}


def r_(a, b):
    return 1.0 if a == b else R.get((a, b), R.get((b, a)))


def ro(x, z=2):
    return f"{x:.{z}f}".replace(".", ",")


def mii(x):
    return f"{x:,.0f}".replace(",", ".")


# tabelul colorat al corelațiilor: teal pozitiv, cărămiziu negativ
VAR = [("sci", "SCI"), ("dist", "distanța"), ("migr", "migranți la mie"), ("gr", "graniță")]


def culoare(r):
    tinta = "var(--accent)" if r >= 0 else "var(--nu)"
    p = round(abs(r) * 70)
    return f"background:color-mix(in srgb,{tinta} {p}%,var(--panza))" + (
        ";color:var(--panza)" if abs(r) > .55 else "")


TAB_CORR = ('<table class="tcol"><tr><th></th>'
            + "".join(f"<th>{e}</th>" for _, e in VAR) + "</tr>"
            + "".join("<tr><th class=\"st\">" + e1 + "</th>" + "".join(
                f'<td style="{culoare(r_(k1, k2))}">{ro(r_(k1, k2))}</td>'
                for k2, _ in VAR) + "</tr>" for k1, e1 in VAR)
            + "</table>")

# tabelul de contingență: granița × treimea de SCI
sorted_sci = sorted(p["sci"] for p in P)
T1, T2 = sorted_sci[len(P) // 3], sorted_sci[2 * len(P) // 3]


def treime(v):
    return "slab" if v < T1 else "mediu" if v < T2 else "tare"


CT = {(g, t): 0 for g in (False, True) for t in ("slab", "mediu", "tare")}
for p in P:
    CT[(p["g"], treime(p["sci"]))] += 1
N = len(P)
rand = {g: sum(CT[(g, t)] for t in ("slab", "mediu", "tare")) for g in (False, True)}
col = {t: CT[(False, t)] + CT[(True, t)] for t in ("slab", "mediu", "tare")}
CHI2 = sum((CT[(g, t)] - rand[g] * col[t] / N) ** 2 / (rand[g] * col[t] / N)
           for g in (False, True) for t in ("slab", "mediu", "tare"))
CRAMER = math.sqrt(CHI2 / N)


def tab_ct():
    rd = ""
    for g, et in ((False, "fără graniță"), (True, "cu graniță")):
        rd += f"<tr><th class=\"st\">{et}</th>"
        for t in ("slab", "mediu", "tare"):
            pc = CT[(g, t)] / rand[g]
            tinta = "var(--ambra)" if g else "var(--accent)"
            rd += (f'<td style="background:color-mix(in srgb,{tinta} {round(pc * 85)}%,var(--panza))'
                   f'{";color:var(--panza)" if pc > .5 else ""}">{CT[(g, t)]}'
                   f'<br><small>{round(pc * 100)}%</small></td>')
        rd += f"<td>{rand[g]}</td></tr>"
    return ('<table class="tcol"><tr><th></th><th>SCI slab</th><th>mediu</th><th>tare</th>'
            '<th>total</th></tr>' + rd + "</table>")


TAB_CT = tab_ct()

# mediana SCI pe grup
def mediana(v):
    v = sorted(v)
    n = len(v)
    return v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2


MED_G = mediana([p["sci"] for p in P if p["g"]])
MED_N = mediana([p["sci"] for p in P if not p["g"]])
NG = sum(1 for p in P if p["g"])

TOP = sorted(P, key=lambda p: -p["sci"])[0]


# ===========================================================================
#  1-2. Cursul
# ===========================================================================

AGENDA = [
    ("Întrebările", "azi", "Întrebările care decurg din cadrul de la cursul 3."),
    ("O variabilă", "azi", "Distribuții, asimetrie, logaritm, clasamente."),
    ("Două variabile", "azi", "Norul de puncte, corelațiile și limitele lor."),
    ("Categorii și grupuri", "azi", "Tabelul de contingență, testul χ², compararea grupurilor."),
    ("Harta", "azi", "Comunitățile de regiuni din rețeaua SCI."),
    ("Grafice înșelătoare", "azi", "Axa trunchiată și alte procedee care induc în eroare."),
]

# Pașii pentru lecția 6, din caietele 05 (explorarea) și 06 (rețele).
# Cifrele: data/analiza_c4 și data/explorare_c5/referinta_c2_20261013/nuts2 (perechi de regiuni NUTS 2).

PAS_COADA = {
    "fisier": "05_explorare.ipynb · 1. Cum arată o pereche obișnuită?",
    "intro": "Histograma și exercițiul de pe slide folosesc cele 263 de perechi de <b>țări</b> pentru care există și date de migrație. Caietul 05 lucrează pe perechi de <b>regiuni</b>: 44.253, de 168 de ori mai multe. Distribuția are aceeași formă, la o altă unitate de analiză.",
    "cod": "perechi[\"sci\"].describe().round(0)\n\n"
           "perechi.nlargest(1, \"sci\")\n\n"
           "log_sci = np.log10(perechi[\"sci\"])\n"
           "log_sci.describe().round(2)",
    "pasi": [
        {"l": 1, "out": "count      44253.0\nmean       10254.0\nstd        62609.0\nmin            1.0\n25%          495.0\n50%         1233.0\n75%         3075.0\nmax      4001835.0",
         "txt": "Media este de opt ori mai mare decât mediana. Trei sferturi din perechi sunt sub 3.075, iar maximul depășește patru milioane: distribuția are o coadă foarte lungă."},
        {"l": 3, "out": " regiune_1  regiune_2      sci\n NO07       NO0B       4001835",
         "txt": "Extremul cozii: Nord-Norge și Svalbard. Svalbard are populația raportată 0 în C4. SCI este o măsură relativă, împărțită la numărul de utilizatori, astfel încât câțiva utilizatori pot produce un indice foarte mare."},
        {"l": 5, "set": {"log_sci": {"t": "Series", "v": {"rows": [["HU11–RO11", "4.53"], ["RO11–RO12", "5.49"], ["NO07–NO0B", "6.60"], ["…", "…"]],
            "nota": "log10: 100 → 2, 1.000 → 3, 1.000.000 → 6"}}},
         "txt": "<code>np.log10</code> exprimă valorile în ordine de mărime: 34.160 devine 4,53, iar patru milioane devine 6,6. Diferențele foarte mari dintre valori se comprimă."},
        {"l": 6, "out": "count    44253.00\nmean         3.14\nstd          0.71\nmin          0.00\n25%          2.69\n50%          3.09\n75%          3.49\nmax          6.60",
         "txt": "Pe scara logaritmică, media (3,14) și mediana (3,09) aproape coincid: distribuția este aproximativ simetrică. De aici înainte, analiza folosește scara logaritmică, ca în caiet."},
    ],
}

PAS_INTERVALE = {
    "fisier": "05_explorare.ipynb · 3-4. H1 și H2",
    "intro": "Un singur coeficient descrie puțin din relație. Distanța se împarte în intervale, iar mediana SCI se calculează pentru fiecare interval.",
    "cod": "print(perechi[\"distanta_km\"].corr(perechi[\"sci\"], method=\"spearman\"))\n\n"
           "praguri = [0, 100, 250, 500, 1000, 2000, 4000, np.inf]\n"
           "perechi[\"interval_km\"] = pd.cut(perechi[\"distanta_km\"], praguri)\n"
           "perechi.groupby(\"interval_km\", observed=True)[\"sci\"].agg([\"size\", \"median\"])\n\n"
           "perechi[\"aceeasi_tara\"] = perechi[\"tara_1\"] == perechi[\"tara_2\"]\n"
           "(perechi.groupby([\"interval_km\", \"aceeasi_tara\"], observed=True)[\"sci\"]\n"
           "        .median().unstack())",
    "pasi": [
        {"l": 1, "out": "-0.46460232789747474",
         "txt": "Coeficientul Spearman, calculat pe toate perechile, este negativ: legăturile scad cu distanța. Un singur coeficient nu arată însă forma acestei scăderi."},
        {"l": 3, "set": {"praguri": {"t": "list", "v": [0, 100, 250, 500, 1000, 2000, 4000, "inf"]}},
         "txt": "Limitele intervalelor. <code>np.inf</code> reprezintă infinitul: ultimul interval cuprinde toate distanțele de peste 4.000 km."},
        {"l": 4, "set": {"interval_km": {"t": "Series", "v": {"rows": [["…", "(250, 500]"], ["…", "(1000, 2000]"], ["…", "(500, 1000]"]],
            "nota": "o categorie pentru fiecare pereche"}}}, "sterge": ["praguri"],
         "txt": "<code>pd.cut</code> transformă o valoare numerică într-o categorie: intervalul în care se încadrează. <code>(250, 500]</code> înseamnă peste 250 și cel mult 500."},
        {"l": 5, "out": "interval_km   size    median\n(0, 100]       223  242323.0\n(100, 250]    1445   31405.0\n(250, 500]    3972    3465.0\n(500, 1000]  10454    1593.5\n(1000, 2000] 16855    1095.0\n(2000, 4000]  9453     650.0\n(4000, inf]   1851     185.0",
         "txt": "Mediana scade abrupt în primele sute de kilometri, apoi tot mai lent. Între 0-100 și 250-500 km scade de 70 de ori; după 1.000 km scade mult mai lent."},
        {"l": 7, "set": {"aceeasi_tara": {"t": "Series", "v": {"rows": [["HU11–RO11", "False"], ["RO11–RO12", "True"], ["…", "…"]],
            "nota": "2.385 de perechi din aceeași țară"}}},
         "txt": "H2: comparația produce o coloană de valori True și False. Nord-Vest și Centru sunt în aceeași țară; Budapesta nu."},
        {"l": 8, "out": "aceeasi_tara     False      True\ninterval_km\n(0, 100]       27814.0  317411.0\n(100, 250]      6492.5   99996.0\n(250, 500]      2370.0   36415.0\n(500, 1000]     1498.0   39067.5\n…",
         "txt": "<code>unstack</code> mută al doilea nivel al grupării pe coloane. La 250-500 km, perechile din aceeași țară au o mediană de 15 ori mai mare. Granița de stat contează la orice distanță."},
    ],
}

PAS_RETEA = {
    "fisier": "06_retele.ipynb · 1. O rețea mică",
    "intro": "Înainte de harta comunităților, o rețea de cinci noduri: aceleași întrebări, pe valori care se pot verifica manual.",
    "cod": "mica = nx.Graph()\n"
           "mica.add_weighted_edges_from([(\"A\", \"B\", 9), (\"A\", \"C\", 7), (\"B\", \"C\", 8),\n"
           "                              (\"C\", \"D\", 1), (\"D\", \"E\", 9)])\n\n"
           "legaturi = dict(mica.degree())\n"
           "forta = dict(mica.degree(weight=\"weight\"))\n"
           "pd.DataFrame({\"legaturi\": legaturi, \"forta\": forta})",
    "pasi": [
        {"l": 1, "set": {"mica": {"t": "dict", "e": "Graph", "v": {}}},
         "txt": "O rețea goală. În <code>networkx</code>, rețeaua reține, pentru fiecare nod, nodurile cu care este legat."},
        {"l": 2, "set": {"mica": {"t": "dict", "e": "Graph", "v": {"A": {"B": 9, "C": 7}, "B": {"A": 9, "C": 8}, "C": {"A": 7, "B": 8, "D": 1}, "D": {"C": 1, "E": 9}, "E": {"D": 9}}}},
         "txt": "Fiecare legătură este un triplet: două noduri și o pondere, analog unei perechi de regiuni și SCI-ului ei. Legătura este neorientată: merge în ambele sensuri."},
        {"l": 5, "set": {"legaturi": {"t": "dict", "v": {"A": 2, "B": 2, "C": 3, "D": 2, "E": 1}}}, "hl": {"var": "legaturi", "k": "C"},
         "txt": "<code>degree()</code> numără legăturile fiecărui nod (gradul). C are cele mai multe: trei."},
        {"l": 6, "set": {"forta": {"t": "dict", "v": {"A": 16, "B": 17, "C": 16, "D": 10, "E": 9}}}, "hl": {"var": "forta", "k": "C"},
         "txt": "Cu <code>weight=</code>, se adună ponderile: rezultatul este <b>forța</b> nodului. C: 7 + 8 + 1 = 16, cât A, care are doar două legături. B, cu două legături puternice, are forța cea mai mare."},
        {"l": 7, "out": "   legaturi  forta\nA         2     16\nB         2     17\nC         3     16\nD         2     10\nE         1      9",
         "txt": "În SCI, fiecare regiune este legată de toate celelalte, deci gradul nu mai diferențiază regiunile; relevantă rămâne forța. O <b>comunitate</b> este un grup de noduri ca A, B, C, mai puternic legate între ele decât cu restul rețelei. Algoritmul folosit pentru hartă identifică astfel de grupuri."},
    ],
}


import json as _json, pathlib as _pl
_EXPL = _json.loads((_pl.Path(__file__).resolve().parent.parent / "date" / "explorator.json").read_text(encoding="utf-8"))
ROMANI = _EXPL["migratie"]["RO"]
RAPORT = _EXPL["raportoare"]

sl("s1", "Cursul", "Planul lecției",
   "<h2>Analiza exploratorie</h2>"
   "<p class=\"cheie\">Datele se examinează înainte de a fi interpretate "
   "și modelate.</p>"
   + ix("agenda", "Planul lecției",
        {"static": True, "titlu": "Planul lecției",
         "etape": [{"nume": n, "unde": u, "text": d} for n, u, d in AGENDA]})
   + nota("Caietul lecției", "<code>05_explorare_si_ipoteze.ipynb</code> (distribuția, distanța, granița) și <code>06_retele_si_indicatori_regionali.ipynb</code> (rețeaua și comunitățile).", True),
   manual=
   "<h2>Analiza exploratorie</h2>"
   "<p>Analiza exploratorie a datelor (EDA) este etapa în care datele sunt "
   "examinate înainte de orice testare formală. Are două scopuri: "
   "verificarea faptului că datele corespund presupunerilor făcute despre "
   "ele și identificarea tiparelor care merită testate ulterior. Analiza "
   "urmează trei direcții: o variabilă, două variabile și variabile categorice.</p>"
   f"<p>Toate graficele de mai jos folosesc aceleași {N} perechi de țări, "
   "cele pentru care sunt disponibile atât SCI, cât și migrația în ambele direcții. Este "
   "tabelul construit la cursurile 4 și 5.</p>"
   + ix("agenda", "Planul lecției",
        {"static": True, "titlu": "Planul lecției",
         "etape": [{"nume": n, "unde": u, "text": d} for n, u, d in AGENDA]})
   + nota("Caietul lecției", "<code>05_explorare_si_ipoteze.ipynb</code> (distribuția, distanța, granița) și <code>06_retele_si_indicatori_regionali.ipynb</code> (rețeaua și comunitățile).", True))

sl("s2", "Cursul", "Întrebările",
   "<h2>Patru întrebări</h2>"
   + '<div class="reg">'
   + "".join(f'<div class="reg__c"><span class="reg__n">{i}</span><b>{t}</b><p>{d}</p></div>'
             for i, (t, d) in enumerate([
                 ("Legături × distanță", "perechile apropiate sunt mai legate?"),
                 ("Legături × migrație", "perechile cu mai mulți migranți sunt mai legate?"),
                 ("Legături × graniță", "vecinii sunt mai legați decât restul?"),
                 ("Abaterile de la tipar", "ce perechi sunt mult peste sau sub valoarea așteptată?"),
             ], 1))
   + "</div>"
   + nota("De unde vin",
          "Din cadrul teoretic de la cursul 3: fiecare întrebare pune legătura "
          "(SCI) față de un factor. EDA nu oferă răspunsuri definitive; arată doar "
          "ce merită testat.", True)
   + lecturi(["bailey2018", "bailey2020", "blondel2008"], "De unde vin ipotezele"),
   manual=
   "<h2>Întrebările, din cadru</h2>"
   "<p>Fără întrebări, EDA devine o simplă colecție de grafice. Întrebările "
   "acestei lecții provin din cadrul teoretic de la cursul 3: legătura dintre "
   "două locuri (SCI) și factorii care o pot explica, distanța, migrația, "
   "istoria comună și locurile.</p>"
   "<ol>"
   "<li><em>Legături × loc:</em> perechile apropiate sunt mai legate?</li>"
   "<li><em>Legături × oameni:</em> perechile cu mai mulți migranți sunt mai legate?</li>"
   "<li><em>Legături × graniță:</em> vecinii sunt mai legați, la aceeași distanță?</li>"
   "<li><em>Abaterile de la tipar:</em> ce perechi sunt mult peste sau sub "
   "valoarea prezisă de distanță și migrație?</li>"
   "</ol>"
   + nota("Ce nu face EDA",
          "EDA nu dovedește nimic: un tipar observat într-un grafic rămâne o "
          "ipoteză. La cursul 7, ipoteza se testează cu un model care ține cont simultan "
          "de toate variabilele.")
   + lecturi(["bailey2018", "bailey2020", "blondel2008"], "De unde vin ipotezele"))


# ===========================================================================
#  3-6. O variabilă
# ===========================================================================

HISTO = {
    "valori": [p["sci"] for p in P],
    "txtLin": f"Aproape toate perechile se află în primele intervale. Câteva "
              f"valori extreme, ca {TOP['t']} ({mii(TOP['sci'])}), întind axa "
              f"spre dreapta.",
    "txtLog": "Pe scara logaritmică, distribuția devine aproape simetrică: "
              "fiecare ordin de mărime ocupă un interval egal pe axă.",
}

sl("s3", "O variabilă", "Coada lungă",
   "<h2>Distribuția SCI</h2>"
   + ix("histo", f"SCI-ul celor {N} perechi", HISTO)
   + nota("De ce logaritmul",
          "Când o variabilă acoperă mai multe ordine de mărime, logaritmul "
          "compară rapoarte, nu diferențe: o creștere de zece ori corespunde "
          "mereu aceluiași pas.", True),
   manual=
   "<h2>Coada lungă</h2>"
   "<p>Prima întrebare despre orice variabilă privește distribuția ei. Media "
   "și abaterea standard sunt informative doar dacă distribuția este "
   "aproximativ simetrică. Distribuția SCI nu este: cele mai multe perechi au "
   "valori de ordinul miilor sau al zecilor de mii, iar câteva ajung la sute "
   "de mii.</p>"
   + ix("histo", f"SCI-ul celor {N} perechi", HISTO)
   + "<p>Coeficientul de asimetrie (skewness) măsoară cât de lungă este coada "
     "distribuției. O valoare peste 1 indică o asimetrie puternică. După "
     "logaritmare, asimetria scade sub 0,5; de aceea modelul de la "
     "cursul 7 folosește logaritmul SCI, nu valorile brute.</p>")

sl("s4", "O variabilă", "Media și mediana",
   "<h2>Descrierea unei variabile</h2>"
   + ix("prezice", "Media și mediana", {
       "id": "c6-prezice-coada", "fisier": "05_explorare.ipynb · 1. O pereche obișnuită",
       "cod": "import pandas as pd\n\n"
              "sci = pd.Series([2, 3, 4, 5, 100])   # o pereche foarte legata\n"
              "print(sci.mean(), sci.median())",
       "intrebare": "Ce afișează?",
       "variante": ["4.0 4.0", "22.8 4.0", "22.8 22.8", "4.0 22.8"],
       "corect": 1,
       "indiciu": "Media este suma valorilor împărțită la 5. Mediana este valoarea din mijloc a șirului sortat.",
       "laBine": "O singură valoare extremă ridică media; mediana rămâne neschimbată.",
       "explicatie": "Media este (2 + 3 + 4 + 5 + 100) / 5 = 22,8, iar mediana este 4. Când media este mult peste "
                     "mediană, distribuția are o coadă spre dreapta, cum este cazul SCI. De aceea se raportează "
                     "mediana, iar analiza folosește scara logaritmică."}),
   manual="<h2>Descrierea unei variabile</h2>"
   + ix("prezice", "Media și mediana", {
       "id": "c6-prezice-coada", "fisier": "05_explorare.ipynb · 1. O pereche obișnuită",
       "cod": "import pandas as pd\n\n"
              "sci = pd.Series([2, 3, 4, 5, 100])   # o pereche foarte legata\n"
              "print(sci.mean(), sci.median())",
       "intrebare": "Ce afișează?",
       "variante": ["4.0 4.0", "22.8 4.0", "22.8 22.8", "4.0 22.8"],
       "corect": 1,
       "indiciu": "Media este suma valorilor împărțită la 5. Mediana este valoarea din mijloc a șirului sortat.",
       "laBine": "O singură valoare extremă ridică media; mediana rămâne neschimbată.",
       "explicatie": "Media este (2 + 3 + 4 + 5 + 100) / 5 = 22,8, iar mediana este 4. Când media este mult peste "
                     "mediană, distribuția are o coadă spre dreapta, cum este cazul SCI. De aceea se raportează "
                     "mediana, iar analiza folosește scara logaritmică."})
   + ix("pas", "Coada lungă, pe datele reale", PAS_COADA)
   + ix("cod", "Descrierea variabilei", {
       "id": "c6-cod-descrie", "indiciu": "Statisticile descriptive ale unei coloane numerice se obțin cu metoda describe. Asimetria (în engleză, „skewness”) se calculează cu metoda skew. Logaritmul din numpy este np.log.",
       "iesire": "count       263.0\nmean      39432.6\n50%       15543.0\n...\n7.57\n0.49", "fisier": "eda/univariat.py",
       "sarcina": "Statisticile descriptive ale SCI, asimetria variabilei "
                  "și comparația cu asimetria logaritmului.",
       "cod": "import numpy as np\nimport pandas as pd\n\n"
              "d = pd.read_csv(\"date/curat/perechi_tari.csv\")\n\n"
              "# media, mediana, quartilele, minimul, maximul\n"
              "print(d[\"sci\"].{{1}}())\n\n"
              "# cat de lunga e coada\n"
              "print(d[\"sci\"].{{2}}())          # in jur de 7,6\n\n"
              "# acelasi lucru, pe logaritm\n"
              "d[\"log_sci\"] = np.{{3}}(d[\"sci\"])\n"
              "print(d[\"log_sci\"].skew())      # in jur de 0,5",
       "goluri": {
           "1": {"ok": ["describe"], "ajutor": "metoda"},
           "2": {"ok": ["skew"], "ajutor": "metoda"},
           "3": {"ok": ["log", "log10"], "ajutor": "funcția"}},
       "laBine": "Asimetria scade de la 7,6 la 0,5: după logaritmare, variabila este aproape simetrică.",
       "laRau": "Primele două sunt metode ale coloanei; a treia este funcția "
                "numpy pentru logaritm.",
       "explicatie": "În rezultatul <code>describe()</code>, media se compară cu "
                     "mediana. O medie mult peste mediană indică o coadă spre "
                     "dreapta, chiar înainte de calculul asimetriei."}))

sl("s4b", "O variabilă", "Coada lungă, în date",
   "<h2>Coada lungă, pe datele reale</h2>"
   + ix("pas", "Coada lungă, pe datele reale", PAS_COADA),
   manual="",
   dupa=verif("c6-v1", 2,
              "Media SCI este de peste două ori mai mare decât mediana. Ce "
              "indică acest lucru?",
              ["Datele sunt eronate",
               "Jumătate din perechi au SCI zero",
               "O coadă de valori foarte mari ridică media",
               "Nimic: media și mediana diferă de obicei"],
              "Câteva perechi cu valori foarte mari ridică media, în timp ce "
              "mediana nu se modifică. Când diferența este mare, se raportează "
              "mediana sau se lucrează pe scara logaritmică."))

sl("s4c", "O variabilă", "Descrierea, în cod",
   "<h2>Descrierea unei variabile, în cod</h2>"
   + ix("cod", "Descrierea variabilei", {
       "id": "c6-cod-descrie", "indiciu": "Statisticile descriptive ale unei coloane numerice se obțin cu metoda describe. Asimetria (în engleză, „skewness”) se calculează cu metoda skew. Logaritmul din numpy este np.log.",
       "iesire": "count       263.0\nmean      39432.6\n50%       15543.0\n...\n7.57\n0.49", "fisier": "eda/univariat.py",
       "sarcina": "Statisticile descriptive ale SCI, asimetria variabilei "
                  "și comparația cu asimetria logaritmului.",
       "cod": "import numpy as np\nimport pandas as pd\n\n"
              "d = pd.read_csv(\"date/curat/perechi_tari.csv\")\n\n"
              "# media, mediana, quartilele, minimul, maximul\n"
              "print(d[\"sci\"].{{1}}())\n\n"
              "# cat de lunga e coada\n"
              "print(d[\"sci\"].{{2}}())          # in jur de 7,6\n\n"
              "# acelasi lucru, pe logaritm\n"
              "d[\"log_sci\"] = np.{{3}}(d[\"sci\"])\n"
              "print(d[\"log_sci\"].skew())      # in jur de 0,5",
       "goluri": {
           "1": {"ok": ["describe"], "ajutor": "metoda"},
           "2": {"ok": ["skew"], "ajutor": "metoda"},
           "3": {"ok": ["log", "log10"], "ajutor": "funcția"}},
       "laBine": "Asimetria scade de la 7,6 la 0,5: după logaritmare, variabila este aproape simetrică.",
       "laRau": "Primele două sunt metode ale coloanei; a treia este funcția "
                "numpy pentru logaritm.",
       "explicatie": "În rezultatul <code>describe()</code>, media se compară cu "
                     "mediana. O medie mult peste mediană indică o coadă spre "
                     "dreapta, chiar înainte de calculul asimetriei."}),
   manual="")

sl("s5", "O variabilă", "Clasamente",
   "<h2>Un clasament și limitele lui</h2>"
   + ix("bare", "Partenerii României, după SCI", {"cate": 12, "romani": ROMANI, "raport": RAPORT, "intai": {"q": "Italia este țara cu cei mai mulți români stabiliți în străinătate. Pe ce loc se află printre partenerii României, după SCI?", "variante": ["Pe primul", "Pe al treilea", "Pe al șaselea"], "corect": 2, "dupa": "Pe locul al șaselea, după Moldova, Austria, Germania, Ungaria și Irlanda. SCI este normalizat la numărul de utilizatori, astfel că o țară mare, cu o diasporă numeroasă, nu ocupă neapărat un loc fruntaș."}}),
   manual=
   "<h2>Clasamente</h2>"
   "<p>Clasamentul este cel mai simplu grafic exploratoriu și, totodată, cel "
   "mai ușor de interpretat greșit. Rezultatul depinde de măsura aleasă: SCI "
   "este o probabilitate relativă, deci favorizează țările mici puternic "
   "legate de România (Moldova), în timp ce numărul de migranți favorizează "
   "țările mari în care au emigrat mulți români (Italia).</p>"
   + ix("bare", "Partenerii României, după SCI", {"cate": 12, "romani": ROMANI, "raport": RAPORT, "intai": {"q": "Italia este țara cu cei mai mulți români stabiliți în străinătate. Pe ce loc se află printre partenerii României, după SCI?", "variante": ["Pe primul", "Pe al treilea", "Pe al șaselea"], "corect": 2, "dupa": "Pe locul al șaselea, după Moldova, Austria, Germania, Ungaria și Irlanda. SCI este normalizat la numărul de utilizatori, astfel că o țară mare, cu o diasporă numeroasă, nu ocupă neapărat un loc fruntaș."}})
   + nota("Exercițiu",
          "Construirea aceluiași clasament după numărul de români care trăiesc "
          "în fiecare țară și compararea celor două liste. Diferența dintre ele "
          "este întrebarea semestrului, formulată la cursul 1."))


# ===========================================================================
#  6-8. Două variabile
# ===========================================================================

NOR = {
    "puncte": [{"t": p["t"], "y": p["sci"], "g": p["g"],
                "x": {"dist": p["dist"], "migr": p["la_mie"]}} for p in P],
    "variabile": [
        {"k": "dist", "et": "distanța, km",
         "text": "Cu cât distanța este mai mare, cu atât legătura este mai "
                 "slabă. Punctele chihlimbar (vecinii) se află sus, în stânga."},
        {"k": "migr", "et": "migranți la mie",
         "text": "Asocierea cea mai puternică: punctele sunt mai apropiate de dreaptă decât în cazul distanței."},
    ],
    "etY": "SCI (scară logaritmică)",
    "cauta": {"v": "dist",
              "t": "perechea situată cel mai sus deasupra dreptei, adică mult mai legată decât ar prezice distanța.",
              "dupa": "Aproape unul din șapte locuitori ai Luxemburgului este cetățean portughez. La selectarea variabilei "
                      "„migranți la mie”, punctul se apropie de dreaptă. Migrația explică o bună parte din ceea ce distanța nu explica."},
}

sl("s6", "Două variabile", "Norul de puncte",
   "<h2>Fiecare punct este o pereche de țări</h2>"
   + ix("nor", "SCI față de distanță și față de migrație", NOR),
   manual=
   "<h2>Norul de puncte</h2>"
   "<p>Pentru două variabile numerice, primul grafic este norul de puncte. Pe "
   "verticală se află SCI, iar pe orizontală, pe rând, distanța și numărul de "
   "migranți la mia de locuitori ai celor două țări. Ambele axe sunt pe scară "
   "logaritmică, din motivele discutate la distribuția cu coadă lungă.</p>"
   + ix("nor", "SCI față de distanță și față de migrație", NOR)
   + "<p>Punctele care se abat de la nor, ale căror detalii apar la trecerea "
     "cursorului, sunt cele mai informative: perechi mult mai legate sau mult mai puțin legate "
     "decât cele cu valori apropiate pe axa orizontală. La cursul 7, aceste "
     "abateri devin reziduuri.</p>")

sl("s7", "Două variabile", "Corelațiile",
   "<h2>Matricea de corelații</h2>"
   + TAB_CORR
   + nota("Cum se citește",
          f"Teal: corelație pozitivă. Cărămiziu: corelație negativă. "
          f"Distanța și granița sunt corelate (r = {ro(r_('dist', 'gr'))}), "
          "deoarece vecinii sunt apropiați. De aceea efectele lor nu pot fi "
          "evaluate separat.", True),
   manual="<h2>Matricea de corelații</h2>"
   "<p>Coeficientul de corelație Pearson, <em>r</em>, ia valori între -1 și "
   "1. O valoare apropiată de 1 indică variabile care cresc împreună; una "
   "apropiată de -1, variabile care evoluează în sens opus; una apropiată de "
   "0, absența unei relații liniare. Matricea de corelații prezintă "
   "coeficienții pentru toate perechile de variabile.</p>"
   + TAB_CORR
   + "<p>Matricea arată două lucruri. Primul: migrația este mai puternic "
     "asociată cu SCI decât distanța. Al doilea: distanța și granița sunt "
     "corelate între ele, deci efectul uneia se suprapune parțial peste al "
     "celeilalte. Un model care le include pe amândouă le poate separa; o "
     "corelație simplă, nu.</p>"
   + "<pre><code>cols = [\"log_sci\", \"log_distanta\", \"log_la_mie\", \"granita\"]\n"
     "d[cols].corr()</code></pre>")

sl("s7b", "Două variabile", "Spearman",
   "<h2>Spearman, pe ranguri</h2>",
   manual="",
   dupa=ix("prezice", "Spearman, pe ranguri", {
       "id": "c6-prezice-rang", "fisier": "05_explorare.ipynb · 3. H1, distanța",
       "cod": "import pandas as pd\n\n"
              "d = pd.DataFrame({\"distanta\": [100, 500, 1000, 3000],\n"
              "                  \"sci\":      [900, 200, 150, 20]})\n\n"
              "print(d[\"distanta\"].corr(d[\"sci\"], method=\"spearman\"))",
       "intrebare": "Ce afișează?",
       "variante": ["1.0", "-1.0", "0.0", "-0.5"],
       "corect": 1,
       "indiciu": "Coeficientul Spearman ține cont doar de ordinea valorilor. Când distanța crește, cum variază SCI?",
       "laBine": "Ordinea este perfect inversă: -1.",
       "explicatie": "Coeficientul Spearman înlocuiește valorile cu rangurile lor. Rangurile distanței sunt 1, 2, 3, 4, "
                     "iar cele ale SCI sunt 4, 3, 2, 1: o relație perfect descrescătoare, deci -1, indiferent cât de "
                     "inegale sunt diferențele. Pentru SCI și distanță este o alegere potrivită, deoarece nu "
                     "presupune o relație liniară."})
   + verif("c6-v2", 1,
              f"Corelația dintre migrație și SCI este r = {ro(r_('sci', 'migr'))}. Ce se poate concluziona?",
              ["Migrația produce legăturile",
               "Cele două variabile cresc împreună; cauza nu este încă stabilită",
               "Legăturile produc migrația",
               "70% din SCI se explică prin migrație"],
              "Corelația arată că variabilele variază împreună, nu care o "
              "determină pe cealaltă. Migrația poate crea legături, legăturile "
              "vechi pot atrage migrație sau ambele pot proveni din proximitate. "
              "Modelul de la cursul 7 separă o parte din aceste efecte."))


# ===========================================================================
#  9-10. Categorii și grupuri
# ===========================================================================

sl("s8", "Categorii", "Din numere în categorii",
   "<h2>Vecinii, pe treimi de SCI</h2>"
   + TAB_CT
   + nota("χ² și Cramér's V",
          f"χ² = {ro(CHI2, 1)}, iar Cramér's V = {ro(CRAMER)}: o asociere "
          f"moderată. Nicio pereche de vecini nu se află în treimea slabă.", True)
   + ix("pas", "Distanța, împărțită în intervale", PAS_INTERVALE),
   manual=
   "<h2>Din numere în categorii</h2>"
   "<p>Uneori este util ca o variabilă numerică să fie împărțită în "
   "categorii. Aici SCI este împărțit în trei grupe cu efective egale (slab, "
   "mediu, tare), iar granița este deja o variabilă categorică: perechile au "
   "sau nu au graniță comună.</p>"
   + TAB_CT
   + "<p>Testul χ² (hi-pătrat) arată dacă distribuția pe treimi diferă între "
     "cele două grupuri mai mult decât s-ar aștepta din întâmplare. Cramér's V "
     "măsoară intensitatea asocierii: 0 înseamnă absența asocierii, 0,1 o "
     "asociere slabă, 0,3 medie, peste 0,5 puternică. "
     f"Aici V = {ro(CRAMER)}.</p>"
   + ix("pas", "Distanța, împărțită în intervale", PAS_INTERVALE)
   + ix("cod", "Tabelul de contingență", {
       "id": "c6-cod-ct", "indiciu": "Grupele egale ca număr de perechi se obțin cu pd.qcut, tabelul de contingență cu pd.crosstab, iar testul χ² cu chi2_contingency.", "fisier": "eda/categorii.py",
       "sarcina": "Împărțirea SCI în trei grupe egale, tabelul de "
                  "contingență cu granița și testul de asociere.",
       "cod": "from scipy.stats import chi2_contingency\n\n"
              "# trei grupuri egale ca numar de perechi\n"
              "d[\"treime\"] = pd.{{1}}(d[\"sci\"], 3, labels=[\"slab\", \"mediu\", \"tare\"])\n\n"
              "ct = pd.{{2}}(d[\"granita\"], d[\"treime\"])\n"
              "print(ct)\n\n"
              "chi2, p, dof, asteptat = {{3}}(ct)\n"
              "print(round(chi2, 1), p)",
       "goluri": {
           "1": {"ok": ["qcut"], "ajutor": "funcția"},
           "2": {"ok": ["crosstab"], "ajutor": "funcția"},
           "3": {"ok": ["chi2_contingency"], "ajutor": "funcția"}},
       "laBine": f"χ² este aproximativ {ro(CHI2, 0)}, cu p foarte mic.",
       "laRau": "<code>qcut</code> împarte în grupuri cu efective egale; "
                "<code>crosstab</code> numără combinațiile de categorii.",
       "explicatie": "<code>qcut</code> împarte după cuantile, deci fiecare "
                     "treime are același număr de perechi. <code>cut</code> "
                     "ar împărți după valori, iar intervalul superior ar "
                     "conține doar câteva perechi."}))

sl("s9", "Categorii", "Grupuri comparate",
   "<h2>Vecinii față de celelalte perechi</h2>"
   + tabel(["", "Perechi", "SCI median"], [
       ["cu graniță comună", str(NG), mii(MED_G)],
       ["fără graniță", str(N - NG), mii(MED_N)],
   ])
   + f"<p class=\"cheie\">Vecinii au un SCI median de aproape "
     f"{round(MED_G / MED_N)} ori mai mare.</p>"
   + nota("Kruskal-Wallis",
          "Testul compară grupurile fără a presupune distribuții normale. "
          "Pentru SCI, care are o distribuție cu coadă lungă, este alegerea "
          "potrivită.", True),
   dupa=verif("c6-v3", 3,
              f"Vecinii au un SCI median de {round(MED_G / MED_N)} ori mai mare. "
              "Rezultă că granița comună produce legăturile?",
              ["Da, diferența este prea mare pentru a avea altă explicație",
               "Da, testul este semnificativ statistic",
               "Nu, pentru că sunt doar 30 de perechi de vecini",
               "Nu neapărat: vecinii sunt și apropiați geografic, și au adesea migrație între ei"],
              "Granița comună este asociată cu distanța mică și cu migrația. "
              "Pentru a estima efectul graniței separat, celelalte variabile "
              "trebuie ținute constante, adică este nevoie de un model. "
              "Acesta este subiectul cursului 7."))


# ===========================================================================
#  11. Harta
# ===========================================================================

HARTA_COM = {
    "niveluri": ["regiuni"], "nivel": "regiuni", "masura": "com", "ales": "RO11",
    "masuri": ["com", "sci"],
    "povesti": [
        {"t": "România și Germania", "nivel": "regiuni", "masura": "com", "ales": "RO11",
         "text": "Algoritmul plasează toate regiunile României în aceeași "
                 "comunitate cu Germania, nu cu țările vecine: o urmă a "
                 "migrației de muncă."},
        {"t": "Polonia și Irlanda", "nivel": "regiuni", "masura": "com", "ales": "PL91",
         "text": "Polonia, Irlanda, Islanda și Lituania formează o singură "
                 "comunitate, urmă a emigrației de după 2004."},
        {"t": "Luxemburg și Portugalia", "nivel": "regiuni", "masura": "com", "ales": "LU00",
         "text": "Perechea cu cea mai puternică legătură din întregul set. "
                 "Aproape unul din șapte locuitori ai Luxemburgului este "
                 "cetățean portughez."},
        {"t": "Fosta Iugoslavie", "nivel": "regiuni", "masura": "com", "ales": "SI04",
         "text": "Slovenia, Croația, Bosnia, Serbia, Muntenegru, plus Austria: "
                 "o graniță veche, încă vizibilă în legături."},
    ],
}

sl("s10", "Harta", "Comunitățile",
   "<h2>Comunități detectate doar din legături</h2>"
   + ix("pas", "O rețea de cinci noduri", PAS_RETEA),
   manual="<h2>Comunitățile</h2>"
   "<p>Harta este un mod de explorare a datelor diadice pe care un tabel nu "
   "îl poate înlocui. Fiecare regiune NUTS 2 este colorată după comunitatea "
   "în care o plasează algoritmul Louvain, care identifică grupuri de regiuni "
   "mai puternic legate între ele decât cu restul. Algoritmul nu primește "
   "nicio informație despre țări sau granițe; grupurile rezultă exclusiv din "
   "legături.</p>"
   + ix("pas", "O rețea de cinci noduri", PAS_RETEA)
   + ix("harta", "Comunitățile SCI, pe regiuni", HARTA_COM)
   + "<p>Cele mai multe comunități urmează granițele de stat, ceea ce era de "
     "așteptat. Informative sunt excepțiile: România cu Germania, Polonia cu "
     "Irlanda, Luxemburg cu Portugalia. Toate trei corespund unor fluxuri de migrație cunoscute, "
     "adică exact tema întrebării de cercetare a proiectului.</p>"
   + nota("În caiet",
          "Comunitățile se calculează în caietul cursului 6, cu "
          "<code>networkx</code>, și se compară cu comunitățile din rețeaua "
          "migrației. Harta de aici este construită din rezultatele acelui "
          "caiet."))

sl("s10b", "Harta", "Comunitățile SCI",
   "<h2>Comunitățile SCI, pe regiuni</h2>"
   + ix("harta", "Comunitățile SCI, pe regiuni", HARTA_COM)
   + nota("Metoda",
          "Algoritmul Louvain grupează regiunile mai puternic legate între ele "
          "decât cu restul. Culorile sunt doar etichete. Toate nivelurile sunt "
          'disponibile în <a class="leg" href="../../explorator/">Exploratorul legăturilor sociale</a>.', True),
   manual="")


# ===========================================================================
#  12. Grafice care mint
# ===========================================================================

AXA = {
    "bare": [{"t": "România-Italia", "v": 69327}, {"t": "România-Spania", "v": 54179}],
    "taie": 50000,
    "txtZero": "Legăturile cu Italia și cu Spania au valori apropiate.",
    "txtTaiat": "Aceleași valori; doar axa nu mai pornește de la zero.",
}

sl("s11", "Grafice înșelătoare", "Axa trunchiată",
   "<h2>Aceleași cifre, altă impresie</h2>"
   + ix("axa", "SCI-ul României cu Italia și cu Spania", AXA)
   + nota("Regula",
          "La graficele cu bare, axa pornește de la zero. La linii și la norii "
          "de puncte poate fi trunchiată, cu condiția ca trunchierea să fie "
          "marcată clar.", True),
   manual="<h2>Grafice care induc în eroare</h2>"
   "<p>Un grafic poate fi corect în fiecare valoare și totuși să inducă în "
   "eroare. Cel mai frecvent, prin axa care nu pornește de la zero: la "
   "graficele cu bare, cititorul compară lungimi, iar o axă trunchiată "
   "modifică raportul dintre ele.</p>"
   + ix("axa", "SCI-ul României cu Italia și cu Spania", AXA)
   + "<p>Alte procedee frecvente: două axe verticale cu scări diferite, culori "
     "care sugerează o ordine inexistentă, hărți colorate după valori absolute "
     "(pe care țările mari ies mereu în evidență) și medii raportate fără "
     "distribuție. Sunt tratate pe larg în cartea lui Claus Wilke, menționată "
     "la „Legături”.</p>")

sl("s11b", "Grafice înșelătoare", "Axa și scara",
   "<h2>Când axa poate să nu pornească de la zero</h2>",
   manual="",
   dupa=verif("c6-v4", 0,
              "Când este acceptabil ca axa să nu pornească de la zero?",
              ["La un grafic cu linii sau cu puncte, unde contează forma, nu lungimea",
               "La orice grafic, dacă diferențele sunt mici",
               "Niciodată",
               "La graficele cu bare care au valori mari"],
              "La graficele cu bare, informația este transmisă de lungime, deci "
              "o axă trunchiată o distorsionează. La linii și puncte contează "
              "poziția și forma, iar o axă trunchiată, marcată ca atare, este "
              "acceptabilă."))


# ===========================================================================
#  13-14. Proiectul
# ===========================================================================

sl("s12", "Proiectul echipei", "Explorarea echipei",
   "<h2>Trei grafice și o propoziție</h2>"
   + tabel(["Pasul", "Ce se realizează"], [
       ["1", "o distribuție: variabila principală, pe scară liniară și logaritmică"],
       ["2", "o relație: norul de puncte între SCI și variabila proiectului"],
       ["3", "o hartă sau un clasament, cu abaterile de la tipar"],
       ["4", "în <code>README.md</code>: primul tipar găsit, într-o propoziție"],
   ])
   + ix("dovada", "Dovada", {
       "id": "c6-dovada-eda",
       "sarcina": "Rezultatul afișat de scriptul de explorare, copiat din terminal.",
       "pasi": [
           {"t": "Asimetria este calculată pe scară liniară și logaritmică",
            "cmd": "python eda/univariat.py",
            "gol": "cele două valori",
            "cauta": r"\d[.,]\d+[\s\S]*\d[.,]\d+",
            "daca_nu": "Sunt necesare două numere cu zecimale: asimetria "
                       "înainte și după logaritmare."},
           {"t": "Graficele sunt salvate în depozit",
            "cmd": "git ls-files figuri",
            "gol": "lista fișierelor",
            "cauta": r"\.(png|svg|html)",
            "daca_nu": "Sunt necesare fișiere .png, .svg sau .html în figuri/. "
                       "Graficele se salvează cu plt.savefig, apoi se face un commit."}],
       "explicatie": "Graficele exploratorii nu sunt destinate raportului, ci "
                     "analizei din echipă. Se păstrează totuși în depozit, "
                     "pentru ca parcursul analizei să fie documentat."}),
   manual=
   "<h2>Explorarea echipei</h2>"
   "<p>Pasul de proiect al lecției: trei grafice și o propoziție. Graficele "
   "servesc analizei din echipă, nu raportului; propoziția formulează prima "
   "ipoteză, care va fi testată la cursul 7.</p>"
   + tabel(["Pasul", "Ce se realizează"], [
       ["1", "o distribuție: variabila principală, pe scară liniară și logaritmică"],
       ["2", "o relație: norul de puncte între SCI și variabila proiectului"],
       ["3", "o hartă sau un clasament, cu abaterile de la tipar"],
       ["4", "în <code>README.md</code>: primul tipar găsit, într-o propoziție"],
   ]))

sl("s13", "Proiectul echipei", "Primul tipar",
   "<h2>Primul tipar observat</h2>"
   + ix("asteptari", "Primul tipar al echipei", {
       "id": "c6-tipar", "tip": "tipar", "minim": 50,
       "sarcina": "Descrierea primului tipar identificat de echipă și a "
                  "graficului în care apare.",
       "exemplu": "De exemplu: Luxemburg-Portugalia se află mult deasupra "
                  "norului în raport cu distanța, dar în interiorul norului "
                  "în raport cu migrația; legătura pare, așadar, explicată "
                  "de migrație.",
       "multumesc": "Răspunsul va fi citit înainte de cursul următor."}))

SURSE_C6 = surse("Documentația analizei", [
    ("pandas: cut", "https://pandas.pydata.org/docs/reference/api/pandas.cut.html", "împărțirea unei variabile numerice în intervale"),
    ("pandas: corr", "https://pandas.pydata.org/docs/reference/api/pandas.Series.corr.html", "Pearson și Spearman, cu <code>method=</code>"),
    ("networkx: Louvain", "https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.community.louvain.louvain_communities.html", "<code>louvain_communities</code>, <code>weight</code>, <code>resolution</code>, <code>seed</code>"),
    ("scikit-learn: Adjusted Rand", "https://scikit-learn.org/stable/modules/generated/sklearn.metrics.adjusted_rand_score.html", "gradul de asemănare dintre două partiții în grupuri"),
])

FIN_C6 = ('<div class="fin3"><div class="fin3__g">'
   "<section><h4>Ce urmează la cursul 7</h4><ul>"
   "<li>Variabile derivate: migranți la mie, distanța pe scară logaritmică, granița comună.</li>"
   "<li>Un model care include simultan variabilele.</li>"
   "<li>Reziduurile: perechile mai legate decât prezice modelul.</li></ul></section>"
   "<section><h4>Pregătirea pentru cursul 7</h4><ul>"
   "<li>Cele trei grafice ale echipei, în depozit.</li>"
   "<li>Tiparul echipei, descris în <code>README.md</code>.</li></ul></section>"
   "</div>"
   '<p class="fin3__a"><a class="leg" href="../">Pagina cursului 6</a>'
   '<a class="leg" href="../../c7-variabile-si-model/">Cursul 7</a></p></div>')

sl("s14", "Mai departe", "Pentru cursul următor",
   "<h2>La cursul 7: variabile derivate și model</h2>" + FIN_C6,
   manual="<h2>La cursul 7: variabile derivate și model</h2>" + FIN_C6 + SURSE_C6)


if __name__ == "__main__":
    L.scrie_tot()
