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

from comun import Lectie, ix, verif, tabel, nota, RAD

L = Lectie(6, "c6-analiza-exploratorie", "Analiza exploratorie",
           "Privitul datelor înainte de a le modela: distribuții, relații, "
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
            tinta = "var(--ceas)" if g else "var(--accent)"
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
    ("Întrebările", "azi", "Ce vrem să aflăm, din cadrul de la cursul 3."),
    ("O variabilă", "azi", "Distribuții, asimetrie, logaritm, top-uri."),
    ("Două variabile", "azi", "Nor de puncte, corelații, și ce nu spun ele."),
    ("Categorii și grupuri", "azi", "Tabelul de contingență, χ², grupuri comparate."),
    ("Harta", "azi", "Comunitățile: cine e legat de cine, pe regiuni."),
    ("Grafice care mint", "azi", "Axa tăiată, și alte feluri de a induce în eroare."),
]

sl("s1", "Cursul", "Despre ce e ora de azi",
   "<h2>Analiza exploratorie</h2>"
   "<p class=\"cheie\">Te uiți la date înainte să le crezi. Și înainte să le "
   "modelezi.</p>"
   + ix("etape", "Agenda",
        {"titlu": "Ora de azi", "intro": "Apasă pe oricare.",
         "etape": [{"nume": n, "unde": u, "text": d} for n, u, d in AGENDA]}),
   manual=
   "<h2>Analiza exploratorie</h2>"
   "<p>Analiza exploratorie (EDA) e partea în care te uiți la date fără să "
   "testezi încă nimic formal. Scopul e dublu: să vezi dacă datele sunt ce "
   "crezi că sunt, și să vezi ce tipare merită apoi testate. Lucrăm pe trei "
   "direcții: o variabilă, două variabile, și categorii.</p>"
   f"<p>Toate graficele de mai jos sunt pe aceleași {N} perechi de țări: cele "
   "pentru care avem și SCI-ul, și migrația în ambele direcții. E tabelul "
   "făcut la cursurile 4 și 5.</p>"
   + ix("etape", "Agenda",
        {"titlu": "Ora de azi", "intro": "Apasă pe oricare.",
         "etape": [{"nume": n, "unde": u, "text": d} for n, u, d in AGENDA]}))

sl("s2", "Cursul", "Întrebările",
   "<h2>Ce căutăm</h2>"
   + '<div class="reg">'
   + "".join(f'<div class="reg__c"><span class="reg__n">{i}</span><b>{t}</b><p>{d}</p></div>'
             for i, (t, d) in enumerate([
                 ("Legături × distanță", "perechile apropiate sunt mai legate?"),
                 ("Legături × migrație", "perechile cu mai mulți migranți sunt mai legate?"),
                 ("Legături × graniță", "vecinii sunt mai legați decât restul?"),
                 ("Ce iese din tipar", "care perechi sunt mult peste sau sub ce ne-am aștepta?"),
             ], 1))
   + "</div>"
   + nota("De unde vin",
          "Din templul de la cursul 3: fiecare întrebare leagă doi piloni. EDA "
          "nu le răspunde definitiv, doar arată dacă merită testate.", True),
   manual=
   "<h2>Întrebările, din cadru</h2>"
   "<p>EDA fără întrebări devine o colecție de grafice. Întrebările de azi "
   "vin din cadrul teoretic de la cursul 3, unde pilonii erau legăturile "
   "(SCI), oamenii (migrația) și locul (distanța, granița).</p>"
   "<ol>"
   "<li><em>Legături × loc:</em> perechile apropiate sunt mai legate?</li>"
   "<li><em>Legături × oameni:</em> perechile cu mai mulți migranți sunt mai legate?</li>"
   "<li><em>Legături × graniță:</em> vecinii sunt mai legați, la aceeași distanță?</li>"
   "<li><em>Ce iese din tipar:</em> care perechi sunt mult peste sau sub ce ar "
   "prezice distanța și migrația?</li>"
   "</ol>"
   + nota("Ce nu face EDA",
          "Nu dovedește nimic. Un tipar văzut într-un grafic e o ipoteză. La "
          "cursul 7 o testăm cu un model, care ține cont de toate variabilele "
          "deodată."))


# ===========================================================================
#  3-6. O variabilă
# ===========================================================================

HISTO = {
    "valori": [p["sci"] for p in P],
    "txtLin": f"Aproape toate perechile stau în primele bare. Câteva, ca "
              f"{TOP['t']} ({mii(TOP['sci'])}), trag axa spre dreapta.",
    "txtLog": "Pe logaritm, distribuția se desface și devine aproape simetrică. "
              "Diferențele de ordin de mărime devin distanțe egale.",
}

sl("s3", "O variabilă", "Coada lungă",
   "<h2>Cum arată SCI-ul</h2>"
   + ix("histo", f"SCI-ul celor {N} perechi", HISTO)
   + nota("De ce logaritm",
          "Când o variabilă se întinde pe mai multe ordine de mărime, "
          "logaritmul compară proporții, nu diferențe: de zece ori mai mult "
          "e mereu același pas.", True),
   manual=
   "<h2>Coada lungă</h2>"
   "<p>Prima întrebare despre orice variabilă: cum e distribuită? Media și "
   "abaterea standard spun ceva util doar dacă distribuția e cât de cât "
   "simetrică. SCI-ul nu e: cele mai multe perechi au valori de câteva mii "
   "sau zeci de mii, iar câteva au sute de mii.</p>"
   + ix("histo", f"SCI-ul celor {N} perechi", HISTO)
   + "<p>Asimetria (skew) măsoară cât de lungă e coada. Peste 1 e o asimetrie "
     "puternică. Pe logaritm scade aproape de zero, de aceea modelul de la "
     "cursul 7 folosește logaritmul SCI-ului, nu SCI-ul.</p>")

sl("s4", "O variabilă", "Descrierea, în cod",
   "<h2>Trei linii, un portret</h2>"
   + ix("prezice", "Media și mediana", {
       "id": "c6-prezice-coada", "fisier": "05_explorare.ipynb · 1. O pereche obișnuită",
       "cod": "import pandas as pd\n\n"
              "sci = pd.Series([2, 3, 4, 5, 100])   # o pereche foarte legata\n"
              "print(sci.mean(), sci.median())",
       "intrebare": "Ce afișează?",
       "variante": ["4.0 4.0", "22.8 4.0", "22.8 22.8", "4.0 22.8"],
       "corect": 1,
       "indiciu": "Media adună tot și împarte la 5. Mediana e valoarea din mijloc, după sortare.",
       "laBine": "O singură valoare uriașă trage media în sus; mediana nu se clintește.",
       "explicatie": "Media e (2 + 3 + 4 + 5 + 100) / 5 = 22,8, mediana e 4. Când media e mult peste mediană, "
                     "distribuția are coadă spre dreapta: exact ce are SCI-ul. De aceea raportăm mediana și "
                     "lucrăm pe logaritm."})
   + ix("cod", "Descrie variabila", {
       "id": "c6-cod-descrie", "indiciu": "Portretul complet al unei coloane numerice e o „descriere”: describe. Asimetria, în engleză „skewness”, e metoda skew. Logaritmul din numpy e np.log.",
       "iesire": "count       702.0\nmean       1863.4\n50%         812.0\n...\n7.61\n0.49", "fisier": "eda/univariat.py",
       "sarcina": "Descrie SCI-ul perechilor, măsoară asimetria, apoi "
                  "compar-o cu cea a logaritmului.",
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
       "laBine": "De la 7,6 la 0,5: logaritmul a făcut variabila aproape simetrică.",
       "laRau": "Primele două sunt metode ale coloanei. A treia e funcția "
                "numpy pentru logaritm.",
       "explicatie": "Uită-te în <code>describe()</code> la medie și mediană. "
                     "Media e mult peste mediană: semnul unei cozi spre "
                     "dreapta, chiar înainte să calculezi asimetria."}),
   dupa=verif("c6-v1", 2,
              "Media SCI-ului e de peste două ori mai mare decât mediana. Ce "
              "îți spune asta?",
              ["Că datele sunt greșite",
               "Că jumătate din perechi au SCI zero",
               "Că o coadă de valori foarte mari trage media în sus",
               "Nimic, media și mediana sunt de obicei diferite"],
              "Câteva perechi uriașe trag media în sus, mediana nu se mișcă. "
              "Când diferența e mare, raportezi mediana sau lucrezi pe logaritm."))

sl("s5", "O variabilă", "Top-uri",
   "<h2>Primele zece, și capcana lor</h2>"
   + ix("bare", "Partenerii României, după SCI", {"cate": 12})
   + nota("Un top depinde de ce numeri",
          "După SCI, Moldova e prima. După numărul de români, Italia. Un top "
          "spune ceva doar dacă știi ce măsoară.", True),
   manual=
   "<h2>Top-uri</h2>"
   "<p>Un top e cel mai simplu grafic de explorare, și cel mai ușor de citit "
   "greșit. Depinde de ce numeri: SCI-ul e o probabilitate relativă, deci "
   "favorizează țările mici legate de România (Moldova). Numărul de "
   "migranți favorizează țările mari în care au plecat mulți (Italia).</p>"
   + ix("bare", "Partenerii României, după SCI", {"cate": 12})
   + nota("Exercițiu",
          "Fă același top după numărul de români care trăiesc acolo și pune "
          "cele două liste una lângă alta. Diferența dintre ele e ghicitoarea "
          "de la cursul 1."))


# ===========================================================================
#  6-8. Două variabile
# ===========================================================================

NOR = {
    "puncte": [{"t": p["t"], "y": p["sci"], "g": p["g"],
                "x": {"dist": p["dist"], "migr": p["la_mie"]}} for p in P],
    "variabile": [
        {"k": "dist", "et": "distanța, km",
         "text": "Cu cât mai departe, cu atât mai puțin legate. Punctele "
                 "chihlimbar, vecinii, stau sus și la stânga."},
        {"k": "migr", "et": "migranți la mie",
         "text": "Legătura cea mai strânsă dintre toate. Punctul din dreapta "
                 "sus e Luxemburg–Portugalia: multă migrație, legătură uriașă, "
                 "deși sunt departe."},
    ],
    "etY": "SCI (scară logaritmică)",
}

sl("s6", "Două variabile", "Norul de puncte",
   "<h2>Fiecare punct e o pereche de țări</h2>"
   + ix("nor", "SCI față de distanță și față de migrație", NOR),
   manual=
   "<h2>Norul de puncte</h2>"
   "<p>Când ai două variabile numerice, primul grafic e norul de puncte. Pe "
   "verticală SCI-ul, pe orizontală pe rând distanța și migranții la mia de "
   "locuitori ai celor două țări. Amândouă pe logaritm, din motivul de la "
   "slide-ul cu coada lungă.</p>"
   + ix("nor", "SCI față de distanță și față de migrație", NOR)
   + "<p>Treci cu mouse-ul peste punctele care ies din nor. Ele sunt cele mai "
     "interesante: perechi mult mai legate sau mult mai puțin legate decât "
     "vecinii lor din grafic. La cursul 7 le numim reziduuri.</p>")

sl("s7", "Două variabile", "Corelațiile",
   "<h2>Toate perechile de variabile, dintr-o privire</h2>"
   + TAB_CORR
   + nota("Cum se citește",
          f"Teal: cresc împreună. Cărămiziu: una crește, cealaltă scade. "
          f"Distanța și granița merg împreună (r = {ro(r_('dist', 'gr'))}): "
          "vecinii sunt aproape. De aceea nu le poți judeca separat.", True),
   dupa=ix("prezice", "Spearman, pe ranguri", {
       "id": "c6-prezice-rang", "fisier": "05_explorare.ipynb · 3. H1, distanța",
       "cod": "import pandas as pd\n\n"
              "d = pd.DataFrame({\"distanta\": [100, 500, 1000, 3000],\n"
              "                  \"sci\":      [900, 200, 150, 20]})\n\n"
              "print(d[\"distanta\"].corr(d[\"sci\"], method=\"spearman\"))",
       "intrebare": "Ce afișează?",
       "variante": ["1.0", "-1.0", "0.0", "-0.5"],
       "corect": 1,
       "indiciu": "Spearman se uită doar la ordine. Când distanța crește pas cu pas, ce face SCI-ul, mereu?",
       "laBine": "Ordine perfect inversă: -1.",
       "explicatie": "Spearman înlocuiește valorile cu rangurile lor. Distanța urcă 1, 2, 3, 4, iar SCI-ul coboară "
                     "4, 3, 2, 1: o relație perfect descrescătoare, deci -1, oricât de inegale ar fi pașii. "
                     "Pe SCI și distanță e o alegere bună, pentru că nu cere o linie dreaptă."})
   + verif("c6-v2", 1,
              f"Migrația și SCI-ul au r = {ro(r_('sci', 'migr'))}. Ce poți spune?",
              ["Că migrația produce legăturile",
               "Că cele două cresc împreună; de ce, nu știm încă",
               "Că legăturile produc migrația",
               "Că 70% din SCI se explică prin migrație"],
              "Corelația spune că merg împreună, nu cine pe cine produce. Poate "
              "migrația face legături, poate legăturile vechi atrag migrație, "
              "poate amândouă vin din vecinătate. Modelul de la cursul 7 "
              "separă o parte din asta."),
   manual=
   "<h2>Matricea de corelații</h2>"
   "<p>Coeficientul lui Pearson, <em>r</em>, merge de la -1 la 1. Aproape de "
   "1, două variabile cresc împreună; aproape de -1, una crește când "
   "cealaltă scade; aproape de 0, nu au o relație liniară. Matricea le pune "
   "pe toate perechile de variabile deodată.</p>"
   + TAB_CORR
   + "<p>Două lucruri de citit în ea. Primul: migrația e mai strâns legată de "
     "SCI decât distanța. Al doilea: distanța și granița sunt legate între "
     "ele, deci efectul uneia se amestecă în al celeilalte. Un model care le "
     "pune pe amândouă deodată le poate separa; o corelație, nu.</p>"
   + "<pre><code>cols = [\"log_sci\", \"log_distanta\", \"log_la_mie\", \"granita\"]\n"
     "d[cols].corr()</code></pre>")


# ===========================================================================
#  9-10. Categorii și grupuri
# ===========================================================================

sl("s8", "Categorii", "Din numere în categorii",
   "<h2>Vecinii, pe treimi de SCI</h2>"
   + TAB_CT
   + nota("χ² și Cramér's V",
          f"χ² = {ro(CHI2, 1)}, iar Cramér's V = {ro(CRAMER)}: o asociere "
          f"moderată. Niciun vecin nu e în treimea slabă.", True),
   manual=
   "<h2>Din numere în categorii</h2>"
   "<p>Uneori e mai clar să tai o variabilă numerică în categorii. Aici SCI-ul "
   "e tăiat în trei treimi egale (slab, mediu, tare), iar granița e deja o "
   "categorie: au sau nu au graniță comună.</p>"
   + TAB_CT
   + "<p>Testul χ² (hi-pătrat) spune dacă distribuția pe treimi diferă între "
     "cele două grupuri mai mult decât din întâmplare. Cramér's V spune cât de "
     "tare: 0 înseamnă nicio legătură, 0,1 slabă, 0,3 medie, peste 0,5 "
     f"puternică. Aici V = {ro(CRAMER)}.</p>"
   + ix("cod", "Tabelul de contingență", {
       "id": "c6-cod-ct", "indiciu": "Tabelul de contingență se face cu pd.crosstab; procentele pe rând cer normalize=\"index\".", "fisier": "eda/categorii.py",
       "sarcina": "Taie SCI-ul în trei treimi, fă tabelul cu granița și "
                  "testează asocierea.",
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
       "laBine": f"χ² în jur de {ro(CHI2, 0)}, cu p foarte mic.",
       "laRau": "<code>qcut</code> taie în grupuri egale; <code>crosstab</code> "
                "numără combinațiile.",
       "explicatie": "<code>qcut</code> taie după quantile, deci fiecare "
                     "treime are același număr de perechi. <code>cut</code> "
                     "ar tăia după valori, și treimea de sus ar avea doar "
                     "câteva perechi."}))

sl("s9", "Categorii", "Grupuri comparate",
   "<h2>Vecinii, față de restul</h2>"
   + tabel(["", "Perechi", "SCI median"], [
       ["cu graniță comună", str(NG), mii(MED_G)],
       ["fără graniță", str(N - NG), mii(MED_N)],
   ])
   + f"<p class=\"cheie\">Vecinii au un SCI median de aproape "
     f"{round(MED_G / MED_N)} ori mai mare.</p>"
   + nota("Kruskal–Wallis",
          "Testul compară grupurile fără să presupună distribuții normale. "
          "Cu SCI-ul, care are coada lungă, e alegerea potrivită.", True),
   dupa=verif("c6-v3", 3,
              f"Vecinii au SCI median de {round(MED_G / MED_N)} ori mai mare. "
              "Înseamnă că granița produce legăturile?",
              ["Da, diferența e prea mare ca să fie altfel",
               "Da, testul e semnificativ",
               "Nu, pentru că sunt doar 30 de perechi",
               "Nu neapărat: vecinii sunt și aproape, și au adesea migrație între ei"],
              "Granița vine la pachet cu distanța mică și cu migrația. Ca să "
              "vezi cât contează granița singură, ții celelalte constante, "
              "adică faci un model. Asta e cursul 7."))


# ===========================================================================
#  11. Harta
# ===========================================================================

HARTA_COM = {
    "niveluri": ["regiuni"], "nivel": "regiuni", "masura": "com", "ales": "RO11",
    "masuri": ["com", "sci"],
    "povesti": [
        {"t": "România și Germania", "nivel": "regiuni", "masura": "com", "ales": "RO11",
         "text": "Algoritmul pune toate regiunile României în același grup cu "
                 "Germania, nu cu vecinii. Urma migrației de muncă."},
        {"t": "Polonia și Irlanda", "nivel": "regiuni", "masura": "com", "ales": "PL91",
         "text": "Polonia, Irlanda, Islanda și Lituania: o singură comunitate, "
                 "urma emigrației de după 2004."},
        {"t": "Luxemburg și Portugalia", "nivel": "regiuni", "masura": "com", "ales": "LU00",
         "text": "Cea mai puternică pereche din tot setul. Aproape unul din "
                 "șapte locuitori ai Luxemburgului e cetățean portughez."},
        {"t": "Fosta Iugoslavie", "nivel": "regiuni", "masura": "com", "ales": "SI04",
         "text": "Slovenia, Croația, Bosnia, Serbia, Muntenegru, plus Austria: "
                 "o graniță veche, încă vizibilă în legături."},
    ],
}

sl("s10", "Harta", "Comunitățile",
   "<h2>Cine e legat de cine, fără să-i spunem noi</h2>"
   + ix("harta", "Comunitățile SCI, pe regiuni", HARTA_COM)
   + nota("Cum s-au făcut",
          "Algoritmul Louvain grupează regiunile mai legate între ele decât "
          "cu restul. Culorile sunt doar etichete. Pe toate nivelurile, în "
          '<a class="leg" href="../../explorator/">Exploratorul legăturilor sociale</a>.', True),
   manual=
   "<h2>Comunitățile</h2>"
   "<p>Harta e felul de a explora date diadice pe care un tabel nu-l poate "
   "înlocui. Aici fiecare regiune NUTS2 e colorată după comunitatea în care "
   "o pune algoritmul Louvain, care caută grupuri de regiuni mai legate între "
   "ele decât cu restul. Nu îi spunem nimic despre țări sau granițe; le "
   "găsește singur.</p>"
   + ix("harta", "Comunitățile SCI, pe regiuni", HARTA_COM)
   + "<p>Cele mai multe comunități urmează granițele de stat, ceea ce nu "
     "surprinde. Interesante sunt excepțiile: România cu Germania, Polonia cu "
     "Irlanda, Luxemburg cu Portugalia. Toate trei se explică prin migrație, "
     "ceea ce e exact întrebarea proiectului.</p>"
   + nota("În caiet",
          "Comunitățile se calculează în caietul cursului 6, cu "
          "<code>networkx</code>, și se compară cu comunitățile din rețeaua "
          "migrației. Harta de aici e făcută din rezultatul acelui caiet."))


# ===========================================================================
#  12. Grafice care mint
# ===========================================================================

AXA = {
    "bare": [{"t": "România–Italia", "v": 69327}, {"t": "România–Spania", "v": 54179}],
    "taie": 50000,
    "txtZero": "Legăturile cu Italia și cu Spania sunt apropiate.",
    "txtTaiat": "Aceleași cifre. Doar axa nu mai pornește de la zero.",
}

sl("s11", "Grafice care mint", "Axa tăiată",
   "<h2>Aceleași cifre, altă impresie</h2>"
   + ix("axa", "SCI-ul României cu Italia și cu Spania", AXA)
   + nota("Regula",
          "La bare, axa pornește de la zero. La linii și la norii de puncte se "
          "poate tăia, dar se vede clar că e tăiată.", True),
   dupa=verif("c6-v4", 0,
              "Când e acceptabil să nu pornești axa de la zero?",
              ["La un grafic cu linii sau cu puncte, unde contează forma, nu lungimea",
               "La orice grafic, dacă diferențele sunt mici",
               "Niciodată",
               "La barele care au valori mari"],
              "La bare, lungimea e mesajul, deci axa tăiată o falsifică. La "
              "linii și puncte, contează poziția și forma, iar o axă tăiată, "
              "marcată, e normală."),
   manual=
   "<h2>Grafice care induc în eroare</h2>"
   "<p>Un grafic poate fi corect în fiecare cifră și totuși să mintă. Cel mai "
   "des, prin axa care nu pornește de la zero: la bare, ochiul compară "
   "lungimi, iar o axă tăiată schimbă raportul dintre ele.</p>"
   + ix("axa", "SCI-ul României cu Italia și cu Spania", AXA)
   + "<p>Alte feluri obișnuite: două axe verticale cu scări diferite, culori "
     "care sugerează o ordine acolo unde nu e, hărți colorate după valori "
     "absolute (țările mari ies mereu în față), și medii raportate fără "
     "distribuție. Le găsiți pe larg în cartea lui Claus Wilke, la "
     "„Legături”.</p>")


# ===========================================================================
#  13-14. Proiectul
# ===========================================================================

sl("s12", "Proiectul tău", "Explorarea voastră",
   "<h2>Trei grafice și o propoziție</h2>"
   + tabel(["Pasul", "Ce faceți"], [
       ["1", "o distribuție: variabila voastră principală, liniar și pe logaritm"],
       ["2", "o relație: norul de puncte între SCI și variabila voastră"],
       ["3", "o hartă sau un top, cu ce iese din tipar"],
       ["4", "în <code>README.md</code>: primul tipar găsit, într-o propoziție"],
   ])
   + ix("dovada", "Dovada", {
       "id": "c6-dovada-eda",
       "sarcina": "Rulează scriptul de explorare și lipește ce scrie.",
       "pasi": [
           {"t": "Ai calculat asimetria, liniar și pe logaritm",
            "cmd": "python eda/univariat.py",
            "gol": "lipește cele două valori",
            "cauta": r"\d[.,]\d+[\s\S]*\d[.,]\d+",
            "daca_nu": "Caut două numere cu zecimale: asimetria înainte și "
                       "după logaritm."},
           {"t": "Graficele sunt salvate în depozit",
            "cmd": "git ls-files figuri",
            "gol": "lipește lista",
            "cauta": r"\.(png|svg|html)",
            "daca_nu": "Caut fișiere .png, .svg sau .html în figuri/. Salvează "
                       "graficele cu plt.savefig și fă commit."}],
       "explicatie": "Graficele de explorare nu sunt pentru raport, sunt "
                     "pentru voi. Dar stau în depozit, ca să se vadă drumul."}),
   manual=
   "<h2>Explorarea voastră</h2>"
   "<p>Pasul de proiect al lecției: trei grafice și o propoziție. Graficele "
   "sunt pentru voi, nu pentru raport; propoziția e prima ipoteză pe care o "
   "veți testa la cursul 7.</p>"
   + tabel(["Pasul", "Ce faceți"], [
       ["1", "o distribuție: variabila voastră principală, liniar și pe logaritm"],
       ["2", "o relație: norul de puncte între SCI și variabila voastră"],
       ["3", "o hartă sau un top, cu ce iese din tipar"],
       ["4", "în <code>README.md</code>: primul tipar găsit, într-o propoziție"],
   ]))

sl("s13", "Proiectul tău", "Primul tipar",
   "<h2>Ce ați văzut</h2>"
   + ix("asteptari", "Primul vostru tipar", {
       "id": "c6-tipar", "tip": "tipar", "minim": 50,
       "sarcina": "Scrie primul tipar pe care l-a găsit echipa și graficul "
                  "în care se vede.",
       "exemplu": "De exemplu: Luxemburg–Portugalia iese mult deasupra norului "
                  "față de distanță, dar intră în nor față de migrație; deci "
                  "legătura pare să vină din migrație.",
       "multumesc": "O citesc înainte de cursul următor."}))

sl("s14", "Mai departe", "Până data viitoare",
   "<h2>Cursul 7: variabile derivate și model</h2>"
   "<ul>"
   "<li>variabile noi: migranți la mie, distanța pe logaritm, granița</li>"
   "<li>un model care le pune pe toate deodată</li>"
   "<li>reziduurile: perechile mai legate decât prezice modelul</li>"
   "</ul>"
   + nota("De făcut până atunci",
          "Cele trei grafice în depozit și tiparul vostru în "
          "<code>README.md</code>.", True))


if __name__ == "__main__":
    L.scrie_tot()
