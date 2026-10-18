# -*- coding: utf-8 -*-
"""
Lecția 7: Variabile derivate și model.

Urmează planul cursului de anul trecut (Curs 7. Feature Engineering): cele
cinci etape ale ingineriei variabilelor (construcție, transformare, extragere,
scalare, selecție), apoi modelul, ca în caietul C7 de seminar: patru modele
pe același eșantion și reziduurile lor.

Cifrele vin din caietul C7, rulat pe datele cursului (date/modele-c7.json și
reziduurile din date/explorator.json). Nimic estimat de mână.

Rulare:  python _build/c7.py
"""

import json
import math

from comun import Lectie, ix, verif, tabel, nota, RAD

L = Lectie(7, "c7-variabile-si-model", "Variabile derivate și model",
           "Construirea variabilelor, transformarea și selecția lor, apoi un "
           "model care le pune pe toate deodată, și reziduurile lui.")
sl = L.sl

MOD = json.loads((RAD / "date" / "modele-c7.json").read_text(encoding="utf-8"))
M4 = MOD["M4"]["coef"]


def ro(x, z=2):
    return f"{x:.{z}f}".replace(".", ",")


def efect10(b):
    """Cu cât se schimbă SCI-ul, în procente, când variabila crește cu 10%."""
    return (1.1 ** b - 1) * 100


GR_PROC = (math.exp(M4["granita[T.True]"]) - 1) * 100


# ===========================================================================
#  1-2. Cursul
# ===========================================================================

AGENDA = [
    ("Variabilele", "azi", "Construcție, transformare, extragere, scalare, selecție."),
    ("Modelul", "azi", "Patru modele, fiecare cu o variabilă în plus."),
    ("Coeficienții", "azi", "Cum se citește un model pe logaritmi."),
    ("Reziduurile", "azi", "Perechile mai legate sau mai puțin legate decât prezice modelul."),
    ("Ce avem voie să spunem", "azi", "Și ce nu."),
]

sl("s1", "Cursul", "Despre ce e ora de azi",
   "<h2>Variabile derivate și model</h2>"
   "<p class=\"cheie\">EDA a arătat tipare. Azi le punem pe toate în același "
   "model, ca să vedem ce rămâne din fiecare.</p>"
   + ix("etape", "Agenda",
        {"titlu": "Ora de azi", "intro": "Apasă pe oricare.",
         "etape": [{"nume": n, "unde": u, "text": d} for n, u, d in AGENDA]}),
   manual=
   "<h2>Variabile derivate și model</h2>"
   "<p>La cursul 6 am văzut că SCI-ul scade cu distanța, crește cu migrația "
   "și e mai mare între vecini. Dar vecinii sunt și aproape, și au adesea "
   "migrație între ei, deci cele trei tipare se amestecă. Un model le pune "
   "pe toate deodată și spune cât contează fiecare când celelalte stau pe "
   "loc.</p>"
   "<p>Înainte de model vine ingineria variabilelor: ce construiești, ce "
   "transformi, ce păstrezi. E partea în care se iau cele mai multe decizii, "
   "și cele mai multe nu se văd în rezultatul final.</p>"
   + ix("etape", "Agenda",
        {"titlu": "Ora de azi", "intro": "Apasă pe oricare.",
         "etape": [{"nume": n, "unde": u, "text": d} for n, u, d in AGENDA]}))


# ===========================================================================
#  2-6. Ingineria variabilelor
# ===========================================================================

ETAPE_FE = {
    "titlu": "Cinci etape", "intro": "Apasă pe oricare stație.",
    "buton": "Urmează drumul", "dus": "de la date brute la variabile",
    "intors": "înapoi, dacă modelul cere altceva", "gata": "variabilele sunt gata de model",
    "statii": [
        {"n": "Construcție", "et": "variabile noi", "ic": "🧱", "c": "ceas",
         "d": "Faci din ce ai ceva ce n-aveai: distanța din coordonate, rata din numere."},
        {"n": "Transformare", "et": "forma", "ic": "〰️", "c": "salvie",
         "d": "Schimbi forma distribuției, de obicei cu logaritmul."},
        {"n": "Extragere", "et": "mai puține", "ic": "🧪", "c": "accent",
         "d": "Mai mulți indicatori devin unul singur, de exemplu cu PCA."},
        {"n": "Scalare", "et": "aceeași scară", "ic": "📏", "c": "text-2",
         "d": "Aduci variabilele la scări comparabile, de exemplu cu scorul z."},
        {"n": "Selecție", "et": "ce păstrezi", "ic": "✂️", "c": "text-3",
         "d": "Păstrezi un set mic, cu sens teoretic și fără redundanță."}],
}

sl("s2", "Variabilele", "Cinci etape",
   "<h2>Ingineria variabilelor</h2>"
   + ix("flux", "De la date brute la variabile", ETAPE_FE)
   + nota("Ce facem noi azi",
          "Construim trei variabile, le punem pe logaritm, verificăm că nu se "
          "repetă una pe alta. Extragerea și scalarea le vedeți în caiet.", True),
   manual=
   "<h2>Ingineria variabilelor</h2>"
   "<p>Ingineria variabilelor (feature engineering) e ansamblul deciziilor prin "
   "care construiești, transformi, rezumi și alegi variabilele care intră în "
   "analiză. Cinci etape, ca în planul cursului:</p>"
   + ix("flux", "De la date brute la variabile", ETAPE_FE)
   + "<p>Nu toate cinci apar la fiecare proiect. La noi, construcția și "
     "transformarea sunt esențiale; selecția e o verificare; extragerea și "
     "scalarea devin importante când aveți mulți indicatori pentru același "
     "concept.</p>")

sl("s3", "Variabilele", "Construcția",
   "<h2>Trei variabile pe care nu le aveam</h2>"
   + tabel(["Variabila", "Din ce o facem", "De ce așa"], [
       ["<strong>distanța</strong>", "centrele țărilor, ponderate cu populația județelor",
        "contează unde trăiesc oamenii, nu centrul hărții"],
       ["<strong>granița</strong>", "contururile GISCO, cu o toleranță de 10 km",
        "contururile nu se ating perfect"],
       ["<strong>migranți la mie</strong>", "migranții în ambele direcții, la populația celor două țări",
        "un milion de migranți înseamnă altceva între țări mari și mici"],
   ])
   + ix("cod", "Construiește rata", {
       "id": "c7-cod-rata", "indiciu": "Populația perechii e suma celor două țări. „La mie” înseamnă înmulțit cu o mie.",
       "iesire": "count    702.00\nmean       4.81\n50%        0.62\nmax      160.30", "fisier": "model/variabile.py",
       "sarcina": "Fă rata migranților la mia de locuitori ai celor două țări.",
       "cod": "# migranti = din_1_in_2 + din_2_in_1 (cursul 4)\n"
              "d[\"populatie\"] = d[\"pop_1\"] {{1}} d[\"pop_2\"]\n\n"
              "d[\"la_mie\"] = d[\"migranti\"] / d[\"populatie\"] * {{2}}\n\n"
              "print(d[\"la_mie\"].describe())",
       "goluri": {
           "1": {"ok": ["+"], "ajutor": "operatorul"},
           "2": {"ok": ["1000"], "ajutor": "cât"}},
       "laBine": "Rata compară perechi de țări de mărimi foarte diferite: "
                 "Luxemburg–Portugalia cu Germania–Polonia.",
       "laRau": "Populația perechii e suma celor două. La mie înseamnă înmulțit cu o mie.",
       "explicatie": "Numărul absolut de migranți favorizează țările mari. "
                     "Rata îl pune în raport cu câți oameni sunt în total. La "
                     "model se vede diferența: cu rata, R² aproape se dublează."}),
   manual=
   "<h2>Construcția</h2>"
   "<p>Trei variabile pe care niciuna dintre surse nu le dă de-a gata. Fiecare "
   "e o decizie, iar decizia trebuie scrisă.</p>"
   + tabel(["Variabila", "Din ce o facem", "De ce așa"], [
       ["<strong>distanța</strong>", "centrele țărilor, ponderate cu populația județelor",
        "contează unde trăiesc oamenii, nu centrul geometric al hărții"],
       ["<strong>granița</strong>", "contururile GISCO, cu o toleranță de 10 km",
        "contururile simplificate nu se ating perfect, iar fără toleranță vecinii par despărțiți"],
       ["<strong>migranți la mie</strong>", "migranții în ambele direcții, la populația celor două țări",
        "un milion de migranți înseamnă altceva între Germania și Polonia decât între Luxemburg și Portugalia"],
   ])
   + "<p>Distanța ponderată cu populația merită o propoziție în plus: centrul "
     "geometric al Norvegiei e în munți, departe de Oslo; centrul ponderat cu "
     "populația e lângă oameni. Pentru legături sociale, ăsta e centrul care "
     "contează.</p>"
   + ix("cod", "Construiește rata", {
       "id": "c7-cod-rata", "indiciu": "Populația perechii e suma celor două țări. „La mie” înseamnă înmulțit cu o mie.",
       "iesire": "count    702.00\nmean       4.81\n50%        0.62\nmax      160.30", "fisier": "model/variabile.py",
       "sarcina": "Fă rata migranților la mia de locuitori.",
       "cod": "d[\"populatie\"] = d[\"pop_1\"] {{1}} d[\"pop_2\"]\n"
              "d[\"la_mie\"] = d[\"migranti\"] / d[\"populatie\"] * {{2}}",
       "goluri": {
           "1": {"ok": ["+"], "ajutor": "operatorul"},
           "2": {"ok": ["1000"], "ajutor": "cât"}},
       "laBine": "Rata compară perechi de mărimi foarte diferite.",
       "laRau": "Populația perechii e suma celor două.",
       "explicatie": "Cu rata, R² aproape se dublează față de numărul absolut."}))

sl("s4", "Variabilele", "Transformarea",
   "<h2>Ce pui pe logaritm</h2>"
   + ix("prezice", "Ce face logaritmul", {
       "id": "c7-prezice-log", "fisier": "07_model.ipynb · 3. Același eșantion",
       "cod": "import numpy as np\n\n"
              "km = np.array([10, 100, 1000])\n"
              "print(np.log10(km))",
       "intrebare": "Ce afișează?",
       "variante": ["[1. 2. 3.]", "[10. 100. 1000.]", "[2.3 4.6 6.9]", "[0.1 0.01 0.001]"],
       "corect": 0,
       "indiciu": "log10 întreabă: „10 la ce putere dă numărul ăsta?”",
       "laBine": "Fiecare înmulțire cu 10 devine un pas de 1.",
       "explicatie": "10 = 10¹, 100 = 10², 1000 = 10³. Logaritmul transformă înmulțirile în adunări: "
                     "de la 100 la 1000 km e același pas ca de la 10 la 100. De aceea distanța și SCI-ul "
                     "intră în model pe logaritm, iar coeficientul se citește în procente."})
   + ix("sortare", "Logaritm sau nu", {
       "id": "c7-sort-log",
       "sarcina": "Pune fiecare variabilă unde îi e locul.",
       "elemente": [
           {"t": "SCI", "cos": 0}, {"t": "distanța, în km", "cos": 0},
           {"t": "numărul de migranți", "cos": 0}, {"t": "populația", "cos": 0},
           {"t": "granița (da / nu)", "cos": 1}, {"t": "procentul de populație urbană", "cos": 1},
           {"t": "un indice între 0 și 100", "cos": 1}],
       "cosuri": [
           {"t": "Logaritm", "d": "mărimi cu coadă lungă, relații multiplicative"},
           {"t": "Rămâne așa", "d": "proporții, procente, indici, variabile 0/1"}],
       "laBine": "Regula din planul cursului: logaritmezi mărimile cu coadă "
                 "lungă, nu logaritmezi proporții, procente sau indici.",
       "explicatie": "O variabilă 0/1 nu are logaritm la zero. Un procent are "
                     "deja o scară închisă, de la 0 la 100; logaritmul îl "
                     "deformează fără niciun câștig."}),
   manual=
   "<h2>Transformarea</h2>"
   "<p>La cursul 6 am văzut că SCI-ul are o coadă lungă și că logaritmul o "
   "strânge. Același lucru e adevărat pentru distanță, populație și "
   "migranți. Există și un motiv de fond: efectele sunt multiplicative. "
   "Dublarea distanței contează la fel între 100 și 200 km ca între 1.000 și "
   "2.000.</p>"
   + ix("sortare", "Logaritm sau nu", {
       "id": "c7-sort-log",
       "sarcina": "Pune fiecare variabilă unde îi e locul.",
       "elemente": [
           {"t": "SCI", "cos": 0}, {"t": "distanța, în km", "cos": 0},
           {"t": "numărul de migranți", "cos": 0}, {"t": "populația", "cos": 0},
           {"t": "granița (da / nu)", "cos": 1}, {"t": "procentul de populație urbană", "cos": 1},
           {"t": "un indice între 0 și 100", "cos": 1}],
       "cosuri": [
           {"t": "Logaritm", "d": "mărimi cu coadă lungă"},
           {"t": "Rămâne așa", "d": "proporții, procente, indici, 0/1"}],
       "laBine": "Logaritmezi mărimile, nu proporțiile.",
       "explicatie": "O variabilă 0/1 nu are logaritm la zero."})
   + nota("Rata migranților",
          "E o rată, dar cu coadă lungă: între 0,001 și 14 la mie. O punem pe "
          "logaritm din același motiv ca SCI-ul. Regula nu e mecanică: te "
          "uiți la distribuție."))

sl("s5", "Variabilele", "Scalare și extragere",
   "<h2>Două unelte pentru mai târziu</h2>"
   + tabel(["", "Ce face", "Când"], [
       ["<strong>Scorul z</strong>", "(x − media) / abaterea standard",
        "când vrei să compari coeficienți ai unor variabile cu unități diferite"],
       ["<strong>PCA</strong>", "mai mulți indicatori devin un scor",
        "când ai cinci măsuri ale aceluiași concept, de exemplu dezvoltarea"],
   ])
   + verif("c7-v1", 1,
           "Scalarea cu scorul z schimbă forma distribuției?",
           ["Da, o face normală",
            "Nu, doar o mută și o întinde; forma rămâne",
            "Da, scoate valorile extreme",
            "Doar dacă variabila are coadă lungă"],
           "Scorul z mută media la zero și abaterea la unu. Forma rămâne exact "
           "aceeași: o coadă lungă rămâne coadă lungă. Pentru formă ai nevoie "
           "de o transformare, ca logaritmul."),
   manual=
   "<h2>Scalare și extragere</h2>"
   "<p>Două etape pe care nu le folosim în modelul de bază, dar pe care le "
   "veți întâlni când adăugați variabile. Scalarea aduce variabilele la "
   "aceeași scară, ca să le poți compara coeficienții. Extragerea face din "
   "mai mulți indicatori corelați unul singur, ca modelul să nu primească de "
   "cinci ori aceeași informație.</p>"
   "<pre><code>from sklearn.preprocessing import StandardScaler\n"
   "z = StandardScaler().fit_transform(d[[\"log_distanta\", \"log_la_mie\"]])</code></pre>"
   + verif("c7-v1", 1,
           "Scalarea cu scorul z schimbă forma distribuției?",
           ["Da, o face normală",
            "Nu, doar o mută și o întinde; forma rămâne",
            "Da, scoate valorile extreme",
            "Doar dacă variabila are coadă lungă"],
           "Forma rămâne aceeași. Pentru formă ai nevoie de logaritm."))

sl("s6", "Variabilele", "Selecția",
   "<h2>Nu se repetă una pe alta?</h2>"
   + tabel(["Variabila", "VIF", "Verdict"], [
       ["distanța (log)", "1,81", "în regulă"],
       ["migranți la mie (log)", "1,15", "în regulă"],
       ["granița", "1,81", "în regulă"],
   ])
   + nota("Regula VIF",
          "Sub 5, în regulă. Între 5 și 10, atenție. Peste 10, scoți una. "
          "Distanța și granița sunt corelate (r = −0,66), dar nu atât cât să "
          "nu le poți pune împreună.", True),
   manual=
   "<h2>Selecția</h2>"
   "<p>Două variabile care spun aproape același lucru încurcă modelul: "
   "coeficienții lor devin instabili, iar erorile standard cresc. Factorul "
   "de inflație a varianței (VIF) măsoară cât de bine e prezisă fiecare "
   "variabilă de celelalte.</p>"
   + tabel(["Variabila", "VIF", "Verdict"], [
       ["distanța (log)", "1,81", "în regulă"],
       ["migranți la mie (log)", "1,15", "în regulă"],
       ["granița", "1,81", "în regulă"],
   ])
   + "<pre><code>from statsmodels.stats.outliers_influence import variance_inflation_factor as vif\n"
     "X = sm.add_constant(d[[\"log_distanta\", \"log_la_mie\", \"granita\"]].astype(float))\n"
     "[vif(X.values, i) for i in range(1, X.shape[1])]</code></pre>")


# ===========================================================================
#  7-10. Modelul
# ===========================================================================

def model(k, formula, text):
    c = MOD[k]["coef"]
    return {"nume": k, "formula": formula, "r2": MOD[k]["r2"], "text": text,
            "coef": {"dist": c["log_distanta"], "migr": c["log_migranti"],
                     "rata": c["log_la_mie"], "gr": c["granita[T.True]"]}}


MODELE = {
    "lim": 0.8,
    "variabile": [
        {"k": "dist", "et": "distanța (log)", "c": "ceas"},
        {"k": "migr", "et": "migranți (log)", "c": "salvie"},
        {"k": "rata", "et": "migranți la mie (log)", "c": "accent"},
        {"k": "gr", "et": "graniță", "c": "text-2"},
    ],
    "modele": [
        model("M1", "log_sci ~ log_distanta",
              f"Doar distanța. Explică {round(MOD['M1']['r2'] * 100)}% din variația SCI-ului."),
        model("M2", "log_sci ~ log_distanta + log_migranti",
              "Intră numărul de migranți. Coeficientul distanței scade: o parte din "
              "ce părea distanță era migrație."),
        model("M3", "log_sci ~ log_distanta + log_la_mie",
              f"Cu rata în loc de număr, R² sare la {ro(MOD['M3']['r2'])}. Rata e "
              "variabila potrivită. Distanța scade din nou."),
        model("M4", "log_sci ~ log_distanta + log_la_mie + granita",
              "Granița adaugă foarte puțin peste distanță și migrație. Efectul ei, "
              "văzut la EDA, era în mare parte distanță."),
    ],
}

sl("s7", "Modelul", "Patru modele",
   "<h2>O variabilă în plus, de fiecare dată</h2>"
   + ix("modele", "Coeficienții și R², model cu model", MODELE),
   manual=
   "<h2>Patru modele, pas cu pas</h2>"
   "<p>Regresia liniară pe logaritmi (OLS) estimează cât se schimbă "
   "logaritmul SCI-ului când o variabilă crește, cu celelalte ținute "
   "constante. Pornim cu distanța singură și adăugăm câte o variabilă. "
   "Toate cele patru modele sunt pe același eșantion de 263 de perechi, ca "
   "să le putem compara.</p>"
   + ix("modele", "Coeficienții și R², model cu model", MODELE)
   + "<p>Lucrul de urmărit e bara chihlimbar, distanța. De la M1 la M4 se "
     "micșorează la o treime. Asta nu înseamnă că distanța nu contează; "
     "înseamnă că o parte din efectul ei trecea prin migrație: țările "
     "apropiate au mai mulți migranți între ele, iar migranții țin "
     "legăturile.</p>")

sl("s8", "Modelul", "Modelul, în cod",
   "<h2>O formulă, un rând</h2>"
   + ix("cod", "Scrie modelul", {
       "id": "c7-cod-ols", "indiciu": "Regresia liniară cu cele mai mici pătrate: ols. Estimarea se face cu fit. R² e atributul rsquared, fără paranteze.",
       "iesire": "Intercept       11.92\nlog_distanta    -0.25\nlog_la_mie       0.41\ngranita          0.38\n0.56", "fisier": "model/model.py",
       "sarcina": "Estimează modelul complet și uită-te la coeficienți și la R².",
       "cod": "import statsmodels.formula.api as smf\n\n"
              "m = smf.{{1}}(\"log_sci ~ log_distanta + log_la_mie + granita\",\n"
              "            data=d).{{2}}()\n\n"
              "print(m.params)\n"
              "print(m.{{3}})        # cat explica modelul\n\n"
              "# ce ramane neexplicat, pereche cu pereche\n"
              "d[\"rezidual\"] = m.resid",
       "goluri": {
           "1": {"ok": ["ols"], "ajutor": "funcția"},
           "2": {"ok": ["fit"], "ajutor": "metoda"},
           "3": {"ok": ["rsquared"], "ajutor": "atributul"}},
       "laBine": f"R² = {ro(MOD['M4']['r2'])}: modelul explică puțin peste jumătate "
                 "din variația SCI-ului.",
       "laRau": "<code>ols</code> construiește modelul, <code>fit</code> îl "
                "estimează. R² e un atribut, fără paranteze.",
       "explicatie": "Formula se citește ca o propoziție: SCI-ul, pe logaritm, "
                     "explicat de distanță, rata migranților și graniță. "
                     "<code>m.summary()</code> dă tabelul complet, cu erori "
                     "standard și p-valori."}),
   manual=
   "<h2>Modelul, în cod</h2>"
   "<p>Cu <code>statsmodels</code>, un model se scrie ca o formulă. Partea din "
   "stânga lui <code>~</code> e ce explici, partea din dreapta e cu ce.</p>"
   + ix("cod", "Scrie modelul", {
       "id": "c7-cod-ols", "indiciu": "Regresia liniară cu cele mai mici pătrate: ols. Estimarea se face cu fit. R² e atributul rsquared, fără paranteze.",
       "iesire": "Intercept       11.92\nlog_distanta    -0.25\nlog_la_mie       0.41\ngranita          0.38\n0.56", "fisier": "model/model.py",
       "sarcina": "Estimează modelul complet.",
       "cod": "import statsmodels.formula.api as smf\n\n"
              "m = smf.{{1}}(\"log_sci ~ log_distanta + log_la_mie + granita\",\n"
              "            data=d).{{2}}()\n"
              "print(m.params)\n"
              "print(m.{{3}})\n"
              "d[\"rezidual\"] = m.resid",
       "goluri": {
           "1": {"ok": ["ols"], "ajutor": "funcția"},
           "2": {"ok": ["fit"], "ajutor": "metoda"},
           "3": {"ok": ["rsquared"], "ajutor": "atributul"}},
       "laBine": f"R² = {ro(MOD['M4']['r2'])}.",
       "laRau": "R² e un atribut, fără paranteze.",
       "explicatie": "<code>m.summary()</code> dă tabelul complet."}))

sl("s9", "Modelul", "Cum se citește",
   "<h2>Ce înseamnă coeficienții</h2>"
   + tabel(["Variabila", "Coeficient", "În cuvinte"], [
       ["distanța (log)", ro(M4["log_distanta"]),
        f"cu 10% mai departe: SCI cu {ro(abs(efect10(M4['log_distanta'])), 1)}% mai mic"],
       ["migranți la mie (log)", ro(M4["log_la_mie"]),
        f"cu 10% mai mulți migranți: SCI cu {ro(efect10(M4['log_la_mie']), 1)}% mai mare"],
       ["granița", ro(M4["granita[T.True]"]),
        f"vecinii: cu {round(GR_PROC)}% mai mult, dar nesigur"],
   ])
   + nota("„Nesigur”",
          "Eroarea standard a graniței e aproape cât coeficientul. Cu 263 de "
          "perechi și doar 30 de vecini, nu putem spune că granița adaugă "
          "ceva peste distanță și migrație.", True),
   dupa=verif("c7-v2", 2,
              f"Coeficientul distanței e {ro(M4['log_distanta'])}. Ce înseamnă?",
              ["Că la fiecare kilometru SCI-ul scade cu 0,25",
               "Că distanța explică 25% din SCI",
               "Că la o distanță cu 10% mai mare, SCI-ul e cu aproximativ 2,4% mai mic",
               "Că distanța nu contează"],
              "Pe logaritmi, coeficientul e o elasticitate: procent la procent. "
              "Cu 10% mai departe, SCI-ul scade cu aproximativ 2,4%, cu migrația "
              "și granița ținute pe loc."),
   manual=
   "<h2>Cum se citește un model pe logaritmi</h2>"
   "<p>Când și variabila explicată, și cea explicativă sunt pe logaritm, "
   "coeficientul e o elasticitate: cu câte procente se schimbă SCI-ul când "
   "variabila crește cu un procent. Pentru o variabilă 0/1, ca granița, "
   "coeficientul se citește prin exponențială: e la puterea coeficientului, "
   "minus unu, dă diferența procentuală.</p>"
   + tabel(["Variabila", "Coeficient", "În cuvinte"], [
       ["distanța (log)", ro(M4["log_distanta"]),
        f"cu 10% mai departe: SCI cu {ro(abs(efect10(M4['log_distanta'])), 1)}% mai mic"],
       ["migranți la mie (log)", ro(M4["log_la_mie"]),
        f"cu 10% mai mulți migranți: SCI cu {ro(efect10(M4['log_la_mie']), 1)}% mai mare"],
       ["granița", ro(M4["granita[T.True]"]),
        f"vecinii: cu {round(GR_PROC)}% mai mult, dar nesigur"],
   ])
   + "<p>Granița e lecția cea mai utilă: la EDA, vecinii aveau un SCI median "
     "de aproape cinci ori mai mare. În model, după ce ținem distanța și "
     "migrația pe loc, rămâne un plus mic și nesigur. Diferența văzută la EDA "
     "era în mare parte distanță.</p>")


# ===========================================================================
#  11. Reziduurile
# ===========================================================================

HARTA_MODEL = {
    "niveluri": ["tari"], "nivel": "tari", "masura": "model", "ales": "RO",
    "masuri": ["model", "sci", "migr"],
    "povesti": [
        {"t": "România", "nivel": "tari", "masura": "model", "ales": "RO",
         "text": "Austria și Ungaria peste model, Italia sub. Pentru Ungaria, "
                 "explicația probabilă e minoritatea maghiară, pe care modelul "
                 "nu o știe."},
        {"t": "Turcia", "nivel": "tari", "masura": "model", "ales": "TR",
         "text": "Aproape toate perechile cu Turcia sunt mult sub model. Poate "
                 "limba, poate cine folosește Facebook: modelul nu știe niciuna."},
        {"t": "Islanda", "nivel": "tari", "masura": "model", "ales": "IS",
         "text": "Islanda e peste model cu aproape toată lumea. Posibil un "
                 "efect al măsurii: o țară foarte mică, cu un numitor mic."},
        {"t": "Portugalia", "nivel": "tari", "masura": "model", "ales": "PT",
         "text": "Luxemburg–Portugalia e cea mai mare abatere pozitivă din tot "
                 "setul, chiar și după migrație."},
    ],
}

sl("s10", "Reziduurile", "Peste și sub model",
   "<h2>Ce nu explică modelul</h2>"
   + ix("harta", "Reziduurile, pe hartă", HARTA_MODEL)
   + nota("Cum se citește",
          "Teal: legătură mai puternică decât prezic distanța, migrația și "
          "granița. Cărămiziu: mai slabă. Reziduurile sunt întrebările "
          "următoare.", True),
   manual=
   "<h2>Reziduurile</h2>"
   "<p>Reziduul e diferența dintre SCI-ul observat și cel prezis, pe "
   "logaritm. Pe hartă, alegi o țară și vezi, pentru fiecare partener, dacă "
   "legătura e mai puternică sau mai slabă decât ar prezice modelul.</p>"
   + ix("harta", "Reziduurile, pe hartă", HARTA_MODEL)
   + "<p>Reziduurile mari nu sunt erori. Sunt locurile în care modelul nu "
     "știe ceva: o minoritate (Ungaria–România), o limbă comună, o "
     "particularitate a măsurării (Islanda, Turcia). Pentru proiect, ele sunt "
     "partea cea mai interesantă: fiecare reziduu mare e o ipoteză nouă.</p>")


# ===========================================================================
#  12. Ce avem voie să spunem
# ===========================================================================

sl("s11", "Limite", "Ce avem voie să spunem",
   "<h2>Asociere, nu cauză</h2>"
   + tabel(["Putem spune", "Nu putem spune"], [
       ["perechile cu mai mulți migranți sunt mai legate, la aceeași distanță",
        "migrația produce legăturile"],
       ["modelul explică puțin peste jumătate din variație", "am explicat legăturile"],
       ["vecinii nu par mai legați decât prezic distanța și migrația",
        "granițele nu contează"],
   ])
   + nota("Observațiile nu sunt independente",
          "Germania apare în zeci de perechi. Un model obișnuit presupune că "
          "fiecare pereche e independentă, deci erorile standard ies prea "
          "mici. În articol folosim erori standard grupate pe țară.", True),
   dupa=verif("c7-v3", 1,
              "Modelul arată o asociere puternică între migrație și SCI. De ce nu "
              "putem spune că migrația produce legăturile?",
              ["Pentru că R² e sub 1",
               "Pentru că legăturile vechi pot atrage și ele migrație, iar datele "
               "sunt dintr-un singur moment",
               "Pentru că eșantionul e mic",
               "Pentru că am folosit logaritmi"],
              "Direcția poate merge în ambele sensuri: oamenii migrează unde au "
              "deja cunoscuți. Cu un singur instantaneu SCI, nu putem separa "
              "cele două. Asta e o limită de scris în raport, nu de ascuns."),
   manual=
   "<h2>Ce avem voie să spunem</h2>"
   "<p>Un model pe date observaționale, dintr-un singur moment, arată "
   "asocieri. Direcția nu reiese din el: migrația poate crea legături, dar "
   "și legăturile vechi pot atrage migrație, prin rețelele de migranți "
   "despre care vorbea cadrul de la cursul 3.</p>"
   + tabel(["Putem spune", "Nu putem spune"], [
       ["perechile cu mai mulți migranți sunt mai legate, la aceeași distanță",
        "migrația produce legăturile"],
       ["modelul explică puțin peste jumătate din variație", "am explicat legăturile"],
       ["vecinii nu par mai legați decât prezic distanța și migrația",
        "granițele nu contează"],
   ])
   + nota("Erori standard",
          "Aceeași țară apare în multe perechi, deci perechile nu sunt "
          "independente. Erorile standard obișnuite ies prea mici. Corecția "
          "obișnuită sunt erorile grupate pe țară; în caiet e un rând în plus "
          "la <code>fit</code>."))


# ===========================================================================
#  13-14. Proiectul
# ===========================================================================

sl("s12", "Proiectul tău", "Modelul vostru",
   "<h2>Un model, o hartă a reziduurilor, trei propoziții</h2>"
   + tabel(["Pasul", "Ce faceți"], [
       ["1", "variabilele voastre, construite și scrise în <code>decizii.md</code>"],
       ["2", "același eșantion pentru toate modelele"],
       ["3", "modelele, pas cu pas, cu R² și coeficienți"],
       ["4", "reziduurile: cele mai mari cinci în sus și în jos"],
       ["5", "în <code>README.md</code>: ce putem spune și ce nu"],
   ])
   + ix("dovada", "Dovada", {
       "id": "c7-dovada-model",
       "sarcina": "Rulează scriptul și lipește ce scrie.",
       "pasi": [
           {"t": "Modelul are un R²",
            "cmd": "python model/model.py",
            "gol": "lipește linia cu R²",
            "cauta": r"0[.,]\d+",
            "daca_nu": "Caut un număr între 0 și 1. Tipărește m.rsquared."},
           {"t": "Reziduurile sunt salvate",
            "cmd": "python -c \"import pandas as pd; print(pd.read_csv('date/curat/reziduuri.csv').shape)\"",
            "gol": "lipește forma",
            "cauta": r"\(\s*\d+\s*,\s*\d+\s*\)",
            "daca_nu": "Salvează tabelul cu coloana rezidual în date/curat/."}],
       "explicatie": "Modelul și reziduurile lui sunt baza raportului de la cursul 8."}),
   manual=
   "<h2>Modelul vostru</h2>"
   "<p>Pasul de proiect: un model pe întrebarea voastră, pas cu pas, ca în "
   "lecție. Reziduurile sunt partea pe care o veți discuta cel mai mult în "
   "raport.</p>"
   + tabel(["Pasul", "Ce faceți"], [
       ["1", "variabilele voastre, construite și scrise în <code>decizii.md</code>"],
       ["2", "același eșantion pentru toate modelele"],
       ["3", "modelele, pas cu pas, cu R² și coeficienți"],
       ["4", "reziduurile: cele mai mari cinci în sus și în jos"],
       ["5", "în <code>README.md</code>: ce putem spune și ce nu"],
   ]))

sl("s13", "Proiectul tău", "Un reziduu",
   "<h2>Un reziduu care vă interesează</h2>"
   + ix("asteptari", "Reziduul vostru", {
       "id": "c7-reziduu", "tip": "reziduu", "minim": 50,
       "sarcina": "Alege o pereche cu reziduu mare și scrie o explicație "
                  "posibilă, pe care ați putea-o verifica.",
       "exemplu": "De exemplu: Ungaria–România e peste model; explicația "
                  "posibilă e minoritatea maghiară; o verificăm pe județe, "
                  "comparând Harghita și Covasna cu restul.",
       "multumesc": "O citesc înainte de cursul următor."}))

sl("s14", "Mai departe", "Până data viitoare",
   "<h2>Cursul 8: raportul</h2>"
   "<ul>"
   "<li>figura principală și tabelul modelelor</li>"
   "<li>README-ul care permite refacerea întregului drum</li>"
   "<li>prezentarea echipei</li>"
   "</ul>"
   + nota("De făcut până atunci",
          "Modelul și reziduurile în depozit, plus cele trei propoziții despre "
          "ce putem spune.", True))


if __name__ == "__main__":
    L.scrie_tot()
