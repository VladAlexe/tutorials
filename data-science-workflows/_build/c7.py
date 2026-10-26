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

from literatura import lecturi
from comun import Lectie, ix, verif, tabel, nota, surse, RAD

L = Lectie(7, "c7-variabile-si-model", "Variabile derivate și model",
           "Construirea, transformarea și selecția variabilelor, apoi un "
           "model care le include simultan și analiza reziduurilor.")
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
    ("Coeficienții", "azi", "Interpretarea unui model pe logaritmi."),
    ("Reziduurile", "azi", "Perechile mai legate sau mai puțin legate decât prezice modelul."),
    ("Ce se poate concluziona", "azi", "Asociere, nu cauzalitate."),
]

sl("s1", "Cursul", "Planul lecției",
   "<h2>Variabile derivate și model</h2>"
   "<p class=\"cheie\">EDA a evidențiat tipare. Modelul le include simultan, "
   "pentru a estima ce rămâne din fiecare.</p>"
   + ix("agenda", "Planul lecției",
        {"static": True, "titlu": "Planul lecției",
         "etape": [{"nume": n, "unde": u, "text": d} for n, u, d in AGENDA]})
   + nota("Caietul lecției", "<code>07_variabile_derivate_si_model.ipynb</code>.", True),
   manual=
   "<h2>Variabile derivate și model</h2>"
   "<p>La cursul 6, analiza exploratorie a arătat că SCI scade cu distanța, "
   "crește cu migrația și este mai mare între vecini. Vecinii sunt însă și apropiați geografic, și "
   "au adesea migrație între ei, deci cele trei tipare se suprapun. Un model "
   "le include simultan și estimează contribuția fiecăreia când celelalte "
   "sunt ținute constante.</p>"
   "<p>Modelul este precedat de ingineria variabilelor: ce variabile se "
   "construiesc, ce se transformă, ce se păstrează. În această etapă se iau cele mai "
   "multe decizii, iar multe dintre ele nu sunt vizibile în rezultatul "
   "final.</p>"
   + ix("agenda", "Planul lecției",
        {"static": True, "titlu": "Planul lecției",
         "etape": [{"nume": n, "unde": u, "text": d} for n, u, d in AGENDA]})
   + nota("Caietul lecției", "<code>07_variabile_derivate_si_model.ipynb</code>.", True))


# ===========================================================================
#  2-6. Ingineria variabilelor
# ===========================================================================

ETAPE_FE = {
    "titlu": "Cinci etape", "intro": "Descrierea apare la selectarea unei etape.",
    "buton": "Parcurge etapele", "dus": "de la date brute la variabile",
    "intors": "revenire, dacă modelul o impune", "gata": "variabilele sunt pregătite pentru model",
    "statii": [
        {"n": "Construcție", "et": "variabile noi", "ic": "🧱", "c": "ceas",
         "d": "Din variabilele existente se obțin altele noi: distanța din coordonate, rata din efective."},
        {"n": "Transformare", "et": "forma", "ic": "〰️", "c": "salvie",
         "d": "Se modifică forma distribuției, de obicei prin logaritmare."},
        {"n": "Extragere", "et": "mai puține", "ic": "🧪", "c": "accent",
         "d": "Mai mulți indicatori sunt rezumați într-unul singur, de exemplu prin PCA."},
        {"n": "Scalare", "et": "aceeași scară", "ic": "📏", "c": "text-2",
         "d": "Variabilele sunt aduse la scări comparabile, de exemplu prin scorul z."},
        {"n": "Selecție", "et": "setul final", "ic": "✂️", "c": "text-3",
         "d": "Se păstrează un set restrâns, justificat teoretic și fără redundanță."}],
}

ETAPE_FE_LISTA = {"etape": [{"nume": x["n"], "text": x["d"]} for x in ETAPE_FE["statii"]]}

sl("s2", "Variabilele", "Cinci etape",
   "<h2>Ingineria variabilelor</h2>"
   "<p class=\"cheie\">De la date brute la variabilele modelului, în cinci etape.</p>"
   + ix("etape", "De la date brute la variabile", ETAPE_FE_LISTA)
   + nota("În această lecție",
          "Trei variabile sunt construite, logaritmate și verificate pentru "
          "redundanță. Extragerea și scalarea sunt tratate în caiet.", True),
   manual=
   "<h2>Ingineria variabilelor</h2>"
   "<p>Ingineria variabilelor (feature engineering) este ansamblul deciziilor "
   "prin care variabilele care intră în analiză sunt construite, transformate, "
   "rezumate și selectate. Planul cursului distinge cinci etape:</p>"
   + ix("etape", "De la date brute la variabile", ETAPE_FE_LISTA)
   + "<p>Nu toate cele cinci etape apar în fiecare proiect. În analiza "
     "de față, construcția și transformarea sunt esențiale, selecția are rol "
     "de verificare, iar extragerea și scalarea devin importante atunci când "
     "există mai mulți indicatori pentru același concept.</p>")

sl("s3", "Variabilele", "Construcția",
   "<h2>Trei variabile noi</h2>"
   + tabel(["Variabila", "Sursa", "Justificarea"], [
       ["<strong>distanța</strong>", "centrele țărilor, ponderate cu populația regiunilor NUTS 3",
        "contează unde locuiește populația, nu centrul geometric"],
       ["<strong>granița</strong>", "contururile GISCO, cu o toleranță de 10 km",
        "contururile nu se ating exact"],
       ["<strong>migranți la mie</strong>", "migranții în ambele direcții, raportați la populația celor două țări",
        "un milion de migranți are altă pondere între țări mari decât între țări mici"],
   ])
   + ix("cod", "Construcția ratei", {
       "id": "c7-cod-rata", "indiciu": "Populația perechii este suma populațiilor celor două țări. „La mie” înseamnă înmulțirea cu o mie.",
       "iesire": "count    702.00\nmean       4.81\n50%        0.62\nmax      160.30", "fisier": "model/variabile.py",
       "sarcina": "Calculul ratei migranților la mia de locuitori ai celor două țări.",
       "cod": "# migranti = din_1_in_2 + din_2_in_1 (cursul 4)\n"
              "d[\"populatie\"] = d[\"pop_1\"] {{1}} d[\"pop_2\"]\n\n"
              "d[\"la_mie\"] = d[\"migranti\"] / d[\"populatie\"] * {{2}}\n\n"
              "print(d[\"la_mie\"].describe())",
       "goluri": {
           "1": {"ok": ["+"], "ajutor": "operatorul"},
           "2": {"ok": ["1000"], "ajutor": "cât"}},
       "laBine": "Rata permite compararea unor perechi de țări de mărimi foarte "
                 "diferite, de exemplu Luxemburg-Portugalia și Germania-Polonia.",
       "laRau": "Populația perechii este suma celor două populații; „la mie” înseamnă înmulțirea cu o mie.",
       "explicatie": "Numărul absolut de migranți favorizează țările mari. "
                     "Rata îl raportează la populația totală a perechii. "
                     "Diferența se vede în model: cu rata, R² se dublează."}),
   manual=
   "<h2>Construcția</h2>"
   "<p>Niciuna dintre surse nu oferă direct aceste trei variabile. Fiecare "
   "presupune o decizie metodologică, iar decizia trebuie documentată.</p>"
   + tabel(["Variabila", "Sursa", "Justificarea"], [
       ["<strong>distanța</strong>", "centrele țărilor, ponderate cu populația regiunilor NUTS 3",
        "contează unde locuiește populația, nu centrul geometric al teritoriului"],
       ["<strong>granița</strong>", "contururile GISCO, cu o toleranță de 10 km",
        "contururile simplificate nu se ating exact, iar fără toleranță unele țări vecine ar apărea ca neînvecinate"],
       ["<strong>migranți la mie</strong>", "migranții în ambele direcții, raportați la populația celor două țări",
        "un milion de migranți are altă pondere între Germania și Polonia decât între Luxemburg și Portugalia"],
   ])
   + "<p>Distanța ponderată cu populația merită o precizare: centrul geometric "
     "al Norvegiei se află într-o zonă muntoasă, departe de Oslo, în timp ce "
     "centrul ponderat cu populația se află acolo unde locuiește majoritatea "
     "populației. Pentru legăturile sociale, acesta este centrul relevant.</p>"
   + ix("cod", "Construcția ratei", {
       "id": "c7-cod-rata", "indiciu": "Populația perechii este suma populațiilor celor două țări. „La mie” înseamnă înmulțirea cu o mie.",
       "iesire": "count    702.00\nmean       4.81\n50%        0.62\nmax      160.30", "fisier": "model/variabile.py",
       "sarcina": "Calculul ratei migranților la mia de locuitori.",
       "cod": "d[\"populatie\"] = d[\"pop_1\"] {{1}} d[\"pop_2\"]\n"
              "d[\"la_mie\"] = d[\"migranti\"] / d[\"populatie\"] * {{2}}",
       "goluri": {
           "1": {"ok": ["+"], "ajutor": "operatorul"},
           "2": {"ok": ["1000"], "ajutor": "cât"}},
       "laBine": "Rata permite compararea unor perechi de mărimi foarte diferite.",
       "laRau": "Populația perechii este suma celor două populații.",
       "explicatie": "Cu rata, R² se dublează față de numărul absolut."}))

sl("s4", "Variabilele", "Transformarea",
   "<h2>Ce variabile se logaritmează</h2>"
   + ix("prezice", "Ce face logaritmul", {
       "id": "c7-prezice-log", "fisier": "07_model.ipynb · 3. Același eșantion",
       "cod": "import numpy as np\n\n"
              "km = np.array([10, 100, 1000])\n"
              "print(np.log10(km))",
       "intrebare": "Ce afișează?",
       "variante": ["[1. 2. 3.]", "[10. 100. 1000.]", "[2.3 4.6 6.9]", "[0.1 0.01 0.001]"],
       "corect": 0,
       "indiciu": "log10(x) este puterea la care trebuie ridicat 10 pentru a obține x.",
       "laBine": "Fiecare înmulțire cu 10 corespunde unei creșteri cu 1.",
       "explicatie": "10 = 10¹, 100 = 10², 1000 = 10³. Logaritmul transformă înmulțirile în adunări: "
                     "de la 100 la 1000 km este același pas ca de la 10 la 100. De aceea distanța și SCI "
                     "intră în model logaritmate, iar coeficientul se interpretează în procente."})
   + ix("sortare", "Cu sau fără logaritm", {
       "id": "c7-sort-log",
       "sarcina": "În ce categorie se încadrează fiecare variabilă?",
       "elemente": [
           {"t": "SCI", "cos": 0}, {"t": "distanța, în km", "cos": 0},
           {"t": "numărul de migranți", "cos": 0}, {"t": "populația", "cos": 0},
           {"t": "granița (da / nu)", "cos": 1}, {"t": "procentul de populație urbană", "cos": 1},
           {"t": "un indice între 0 și 100", "cos": 1}],
       "cosuri": [
           {"t": "Logaritm", "d": "mărimi cu coadă lungă, relații multiplicative"},
           {"t": "Scara originală", "d": "proporții, procente, indici, variabile 0/1"}],
       "laBine": "Regula din planul cursului: se logaritmează mărimile cu "
                 "coadă lungă, nu proporțiile, procentele sau indicii.",
       "explicatie": "Logaritmul lui zero nu este definit, deci o variabilă 0/1 "
                     "nu poate fi logaritmată. Un procent are deja o scară "
                     "închisă, de la 0 la 100; logaritmul o deformează fără "
                     "niciun beneficiu."}),
   manual=
   "<h2>Transformarea</h2>"
   "<p>La cursul 6 s-a arătat că distribuția SCI are o coadă lungă și că "
   "logaritmul o comprimă. Același lucru este valabil pentru distanță, "
   "populație și numărul de migranți. Există și un motiv de fond: efectele "
   "sunt multiplicative. Dublarea distanței are același efect între 100 și "
   "200 km ca între 1.000 și 2.000 km.</p>"
   + ix("sortare", "Cu sau fără logaritm", {
       "id": "c7-sort-log",
       "sarcina": "În ce categorie se încadrează fiecare variabilă?",
       "elemente": [
           {"t": "SCI", "cos": 0}, {"t": "distanța, în km", "cos": 0},
           {"t": "numărul de migranți", "cos": 0}, {"t": "populația", "cos": 0},
           {"t": "granița (da / nu)", "cos": 1}, {"t": "procentul de populație urbană", "cos": 1},
           {"t": "un indice între 0 și 100", "cos": 1}],
       "cosuri": [
           {"t": "Logaritm", "d": "mărimi cu coadă lungă"},
           {"t": "Scara originală", "d": "proporții, procente, indici, 0/1"}],
       "laBine": "Se logaritmează mărimile, nu proporțiile.",
       "explicatie": "Logaritmul lui zero nu este definit."})
   + nota("Rata migranților",
          "Este o rată, dar are o distribuție cu coadă lungă: între 0,001 și "
          "14 la mie. Se logaritmează din același motiv ca SCI. Regula nu se "
          "aplică mecanic: decizia depinde de forma distribuției."))

sl("s5", "Variabilele", "Scalare și extragere",
   "<h2>Două instrumente suplimentare</h2>"
   + tabel(["", "Ce face", "Când se folosește"], [
       ["<strong>Scorul z</strong>", "(x − media) / abaterea standard",
        "pentru compararea coeficienților unor variabile cu unități de măsură diferite"],
       ["<strong>PCA</strong>", "rezumă mai mulți indicatori într-un scor",
        "când există mai multe măsuri ale aceluiași concept, de exemplu dezvoltarea"],
   ])
   + verif("c7-v1", 1,
           "Scalarea cu scorul z schimbă forma distribuției?",
           ["Da, o transformă într-o distribuție normală",
            "Nu, doar o translatează și o rescalează; forma rămâne aceeași",
            "Da, elimină valorile extreme",
            "Doar dacă variabila are coadă lungă"],
           "Scorul z aduce media la zero și abaterea standard la unu. Forma "
           "distribuției rămâne aceeași: o coadă lungă rămâne o coadă lungă. "
           "Pentru a modifica forma este necesară o transformare neliniară, "
           "cum este logaritmul."),
   manual=
   "<h2>Scalare și extragere</h2>"
   "<p>Două etape care nu intervin în modelul de bază, dar devin necesare "
   "când se adaugă variabile. Scalarea aduce variabilele la aceeași scară, "
   "astfel încât coeficienții lor să poată fi comparați. Extragerea rezumă "
   "mai mulți indicatori corelați într-unul singur, astfel încât modelul să "
   "nu primească de mai multe ori aceeași informație.</p>"
   "<pre><code>from sklearn.preprocessing import StandardScaler\n"
   "z = StandardScaler().fit_transform(d[[\"log_distanta\", \"log_la_mie\"]])</code></pre>"
   + verif("c7-v1", 1,
           "Scalarea cu scorul z schimbă forma distribuției?",
           ["Da, o transformă într-o distribuție normală",
            "Nu, doar o translatează și o rescalează; forma rămâne aceeași",
            "Da, elimină valorile extreme",
            "Doar dacă variabila are coadă lungă"],
           "Forma rămâne aceeași. Pentru a o modifica este necesară o "
           "transformare, cum este logaritmul."))

sl("s6", "Variabilele", "Selecția",
   "<h2>Redundanța variabilelor</h2>"
   + tabel(["Variabila", "VIF", "Verdict"], [
       ["distanța (log)", "1,81", "acceptabil"],
       ["migranți la mie (log)", "1,15", "acceptabil"],
       ["granița", "1,81", "acceptabil"],
   ])
   + nota("Regula VIF",
          "Sub 5: acceptabil. Între 5 și 10: necesită atenție. Peste 10: una "
          "dintre variabile se elimină. Distanța și granița sunt corelate "
          "(r = −0,66), dar nu suficient de puternic pentru a nu putea fi "
          "incluse împreună.", True),
   manual=
   "<h2>Selecția</h2>"
   "<p>Două variabile care conțin aproape aceeași informație afectează "
   "estimarea: coeficienții lor devin instabili, iar erorile standard cresc. "
   "Factorul de inflație a varianței (VIF) măsoară cât de bine este prezisă "
   "fiecare variabilă de celelalte.</p>"
   + tabel(["Variabila", "VIF", "Verdict"], [
       ["distanța (log)", "1,81", "acceptabil"],
       ["migranți la mie (log)", "1,15", "acceptabil"],
       ["granița", "1,81", "acceptabil"],
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
              f"Doar distanța. Explică {round(MOD['M1']['r2'] * 100)}% din variația SCI."),
        model("M2", "log_sci ~ log_distanta + log_migranti",
              "Se adaugă numărul de migranți. Coeficientul distanței scade: o parte "
              "din efectul atribuit distanței ținea de migrație."),
        model("M3", "log_sci ~ log_distanta + log_la_mie",
              f"Cu rata în locul numărului absolut, R² crește la {ro(MOD['M3']['r2'])}. "
              "Rata este specificarea mai potrivită. Coeficientul distanței scade din nou."),
        model("M4", "log_sci ~ log_distanta + log_la_mie + granita",
              "Granița adaugă foarte puțin peste distanță și migrație. Efectul "
              "observat la EDA era în mare parte un efect al distanței."),
    ],
}
MODELE["intai"] = {"q": "M1 conține doar distanța; M2 adaugă numărul de migranți. Cum se modifică efectul distanței?", "variante": ["Crește", "Scade", "Rămâne la fel"], "corect": 1, "dupa": "Țările apropiate au și mai mulți migranți între ele. Fără migrație în model, coeficientul distanței preia și o parte din efectul acesteia; după includerea migrației, această parte dispare."}

sl("s7", "Modelul", "Patru modele",
   "<h2>O variabilă în plus, de fiecare dată</h2>"
   + ix("modele", "Coeficienții și R², model cu model", MODELE),
   manual="<h2>Patru modele, pas cu pas</h2>"
   "<p>Regresia liniară pe logaritmi (OLS) estimează cât se schimbă "
   "logaritmul SCI când o variabilă crește, cu celelalte ținute constante. "
   "Primul model conține doar distanța, iar fiecare model următor adaugă o "
   "variabilă. Toate cele patru "
   "modele sunt estimate pe același eșantion de 263 de perechi, pentru a "
   "putea fi comparate.</p>"
   + ix("modele", "Coeficienții și R², model cu model", MODELE)
   + "<p>Elementul de urmărit este bara chihlimbar, a distanței. De la M1 la "
     "M4, coeficientul ei se reduce la o treime. Aceasta nu înseamnă că "
     "distanța nu contează, ci că o parte din efectul ei trecea prin "
     "migrație: țările apropiate au mai mulți migranți între ele, iar "
     "migranții mențin legăturile.</p>"
   + lecturi(["bailey2020", "aronow2015", "dehaas2010"], "Modelul, în literatură"))

sl("s7b", "Modelul", "Modelul, în literatură",
   "<h2>Modelul, în literatură</h2>"
   + lecturi(["bailey2020", "aronow2015", "dehaas2010"], "Modelul, în literatură"),
   manual="")

sl("s8", "Modelul", "Modelul, în cod",
   "<h2>Modelul ca formulă</h2>"
   + ix("cod", "Specificarea modelului", {
       "id": "c7-cod-ols", "indiciu": "Regresia liniară prin metoda celor mai mici pătrate: ols. Estimarea se face cu fit. R² este atributul rsquared, fără paranteze.",
       "iesire": "Intercept          11.92\n"
                 f"log_distanta       {MOD['M4']['coef']['log_distanta']:.2f}\n"
                 f"log_la_mie          {MOD['M4']['coef']['log_la_mie']:.2f}\n"
                 f"granita[T.True]     {MOD['M4']['coef']['granita[T.True]']:.2f}\n"
                 f"{MOD['M4']['r2']:.2f}", "fisier": "model/model.py",
       "sarcina": "Estimarea modelului complet și examinarea coeficienților și a R².",
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
                 "din variația SCI.",
       "laRau": "<code>ols</code> specifică modelul, <code>fit</code> îl "
                "estimează. R² este un atribut, fără paranteze.",
       "explicatie": "Formula se citește astfel: logaritmul SCI, explicat prin "
                     "distanță, rata migranților și graniță. "
                     "<code>m.summary()</code> afișează tabelul complet, cu "
                     "erori standard și valori p."}),
   manual=
   "<h2>Modelul, în cod</h2>"
   "<p>În <code>statsmodels</code>, un model se specifică printr-o formulă. "
   "În stânga lui <code>~</code> se află variabila explicată, iar în dreapta, "
   "variabilele explicative.</p>"
   + ix("cod", "Specificarea modelului", {
       "id": "c7-cod-ols", "indiciu": "Regresia liniară prin metoda celor mai mici pătrate: ols. Estimarea se face cu fit. R² este atributul rsquared, fără paranteze.",
       "iesire": "Intercept          11.92\n"
                 f"log_distanta       {MOD['M4']['coef']['log_distanta']:.2f}\n"
                 f"log_la_mie          {MOD['M4']['coef']['log_la_mie']:.2f}\n"
                 f"granita[T.True]     {MOD['M4']['coef']['granita[T.True]']:.2f}\n"
                 f"{MOD['M4']['r2']:.2f}", "fisier": "model/model.py",
       "sarcina": "Estimarea modelului complet.",
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
       "laRau": "R² este un atribut, fără paranteze.",
       "explicatie": "<code>m.summary()</code> afișează tabelul complet."}))

sl("s9", "Modelul", "Interpretarea coeficienților",
   "<h2>Ce înseamnă coeficienții</h2>"
   + tabel(["Variabila", "Coeficient", "Interpretare"], [
       ["distanța (log)", ro(M4["log_distanta"]),
        f"distanță cu 10% mai mare: SCI cu {ro(abs(efect10(M4['log_distanta'])), 1)}% mai mic"],
       ["migranți la mie (log)", ro(M4["log_la_mie"]),
        f"cu 10% mai mulți migranți: SCI cu {ro(efect10(M4['log_la_mie']), 1)}% mai mare"],
       ["granița", ro(M4["granita[T.True]"]),
        f"vecinii: SCI cu {round(GR_PROC)}% mai mare, dar incert"],
   ])
   + nota("De ce incert",
          "Eroarea standard a coeficientului graniței este aproape egală cu "
          "coeficientul. Cu 263 de perechi, dintre care doar 30 de vecini, nu "
          "se poate afirma că granița adaugă ceva peste distanță și migrație.", True),
   dupa=verif("c7-v2", 2,
              f"Coeficientul distanței este {ro(M4['log_distanta'])}. Cum se interpretează?",
              ["La fiecare kilometru în plus, SCI scade cu 0,25",
               "Distanța explică 25% din SCI",
               "La o distanță cu 10% mai mare, SCI este cu aproximativ 2,4% mai mic",
               "Distanța nu contează"],
              "Într-un model log-log, coeficientul este o elasticitate: "
              "variație procentuală la variație procentuală. La o distanță cu "
              "10% mai mare, SCI scade cu aproximativ 2,4%, cu migrația și "
              "granița ținute constante."),
   manual=
   "<h2>Cum se citește un model pe logaritmi</h2>"
   "<p>Când atât variabila explicată, cât și cea explicativă sunt "
   "logaritmate, coeficientul este o elasticitate: variația procentuală a "
   "SCI când variabila explicativă crește cu un procent. Pentru o variabilă "
   "0/1, cum este granița, coeficientul se interpretează prin funcția "
   "exponențială: e la puterea coeficientului, minus unu, dă diferența "
   "procentuală.</p>"
   + tabel(["Variabila", "Coeficient", "Interpretare"], [
       ["distanța (log)", ro(M4["log_distanta"]),
        f"distanță cu 10% mai mare: SCI cu {ro(abs(efect10(M4['log_distanta'])), 1)}% mai mic"],
       ["migranți la mie (log)", ro(M4["log_la_mie"]),
        f"cu 10% mai mulți migranți: SCI cu {ro(efect10(M4['log_la_mie']), 1)}% mai mare"],
       ["granița", ro(M4["granita[T.True]"]),
        f"vecinii: SCI cu {round(GR_PROC)}% mai mare, dar incert"],
   ])
   + "<p>Granița ilustrează cel mai clar diferența dintre explorare și "
     "model: la EDA, vecinii aveau un SCI median de circa cinci ori mai "
     "mare. În model, cu distanța și migrația ținute constante, rămâne un "
     "plus mic și incert. Diferența observată la EDA era în mare parte un "
     "efect al distanței.</p>")


# ===========================================================================
#  11. Reziduurile
# ===========================================================================

HARTA_MODEL = {
    "niveluri": ["tari"], "nivel": "tari", "masura": "model", "ales": "RO",
    "masuri": ["model", "sci", "migr"],
    "povesti": [
        {"t": "România", "nivel": "tari", "masura": "model", "ales": "RO",
         "text": "Austria și Ungaria sunt peste valoarea prezisă, Italia sub. "
                 "Pentru Ungaria, explicația probabilă este minoritatea "
                 "maghiară, care nu este inclusă în model."},
        {"t": "Turcia", "nivel": "tari", "masura": "model", "ales": "TR",
         "text": "Aproape toate perechile cu Turcia sunt mult sub valoarea "
                 "prezisă. Explicații posibile: limba sau profilul "
                 "utilizatorilor Facebook, niciuna inclusă în model."},
        {"t": "Islanda", "nivel": "tari", "masura": "model", "ales": "IS",
         "text": "Islanda este peste valoarea prezisă cu aproape toți "
                 "partenerii. Posibil un efect al măsurii: o țară foarte "
                 "mică, deci cu un numitor mic."},
        {"t": "Portugalia", "nivel": "tari", "masura": "model", "ales": "PT",
         "text": "Luxemburg-Portugalia are cea mai mare abatere pozitivă din "
                 "întregul set, chiar și după controlul migrației."},
    ],
}

sl("s10", "Reziduurile", "Abateri de la model",
   "<h2>Ce nu explică modelul</h2>"
   + ix("harta", "Reziduurile, pe hartă", HARTA_MODEL)
   + nota("Cum se citește",
          "Teal: legătură mai puternică decât prezic distanța, migrația și "
          "granița. Cărămiziu: mai slabă. Reziduurile indică întrebările de "
          "cercetare următoare.", True),
   manual=
   "<h2>Reziduurile</h2>"
   "<p>Reziduul este diferența dintre SCI observat și SCI prezis, pe scara "
   "logaritmică. Pe hartă, după selectarea unei țări, se vede pentru fiecare "
   "partener dacă legătura este mai puternică sau mai slabă decât prezice "
   "modelul.</p>"
   + ix("harta", "Reziduurile, pe hartă", HARTA_MODEL)
   + "<p>Reziduurile mari nu sunt erori de calcul. Ele semnalează factori pe "
     "care modelul nu îi include: o minoritate (Ungaria-România), o limbă "
     "comună, o particularitate a măsurării (Islanda, Turcia). Pentru proiect, "
     "ele sunt partea cea mai informativă: fiecare reziduu mare sugerează o "
     "ipoteză nouă.</p>")


# ===========================================================================
#  12. Ce avem voie să spunem
# ===========================================================================

sl("s11", "Limite", "Ce se poate concluziona",
   "<h2>Asociere, nu cauzalitate</h2>"
   + tabel(["Se poate afirma", "Nu se poate afirma"], [
       ["perechile cu mai mulți migranți sunt mai legate, la aceeași distanță",
        "migrația produce legăturile"],
       ["modelul explică puțin peste jumătate din variație", "legăturile au fost explicate"],
       ["vecinii nu par mai legați decât prezic distanța și migrația",
        "granițele nu contează"],
   ])
   + nota("Observațiile nu sunt independente",
          "Germania apare în zeci de perechi. Erorile standard obișnuite "
          "presupun că fiecare pereche este independentă, deci sunt "
          "subestimate. De aceea, erorile standard se grupează pe țară.", True),
   dupa=verif("c7-v3", 1,
              "Modelul arată o asociere puternică între migrație și SCI. De ce nu "
              "se poate afirma că migrația produce legăturile?",
              ["Pentru că R² este sub 1",
               "Pentru că legăturile preexistente pot atrage la rândul lor "
               "migrație, iar datele provin dintr-un singur moment",
               "Pentru că eșantionul este mic",
               "Pentru că modelul folosește logaritmi"],
              "Relația poate funcționa în ambele sensuri: oamenii migrează "
              "acolo unde au deja cunoscuți. Cu o singură măsurare a SCI, "
              "cele două direcții nu pot fi separate. Este o limită care "
              "trebuie menționată explicit în raport."),
   manual=
   "<h2>Ce se poate concluziona</h2>"
   "<p>Un model estimat pe date observaționale, dintr-un singur moment, "
   "arată asocieri. Direcția relației nu reiese din el: migrația poate crea "
   "legături, dar și legăturile preexistente pot atrage migrație, prin "
   "rețelele de migranți discutate în cadrul teoretic de la cursul 3.</p>"
   + tabel(["Se poate afirma", "Nu se poate afirma"], [
       ["perechile cu mai mulți migranți sunt mai legate, la aceeași distanță",
        "migrația produce legăturile"],
       ["modelul explică puțin peste jumătate din variație", "legăturile au fost explicate"],
       ["vecinii nu par mai legați decât prezic distanța și migrația",
        "granițele nu contează"],
   ])
   + nota("Erori standard",
          "Aceeași țară apare în multe perechi, deci perechile nu sunt "
          "independente, iar erorile standard obișnuite sunt subestimate. "
          "Corecția uzuală constă în erori standard grupate pe țară; în caiet, "
          "ea necesită un singur rând în plus la <code>fit</code>."))


# ===========================================================================
#  13-14. Proiectul
# ===========================================================================

sl("s12", "Proiectul echipei", "Modelul echipei",
   "<h2>Un model, o hartă a reziduurilor, trei propoziții</h2>"
   + tabel(["Pasul", "Ce se realizează"], [
       ["1", "variabilele proiectului, construite și documentate în <code>decizii.md</code>"],
       ["2", "același eșantion pentru toate modelele"],
       ["3", "modelele, pas cu pas, cu R² și coeficienți"],
       ["4", "reziduurile: cele mai mari cinci, pozitive și negative"],
       ["5", "în <code>README.md</code>: ce se poate afirma și ce nu"],
   ])
   + ix("dovada", "Dovada", {
       "id": "c7-dovada-model",
       "sarcina": "Rezultatul afișat de script, copiat din terminal.",
       "pasi": [
           {"t": "Modelul are un R²",
            "cmd": "python model/model.py",
            "gol": "linia cu R²",
            "cauta": r"0[.,]\d+",
            "daca_nu": "Este necesar un număr între 0 și 1, afișat cu m.rsquared."},
           {"t": "Reziduurile sunt salvate",
            "cmd": "python -c \"import pandas as pd; print(pd.read_csv('date/curat/reziduuri.csv').shape)\"",
            "gol": "dimensiunile tabelului",
            "cauta": r"\(\s*\d+\s*,\s*\d+\s*\)",
            "daca_nu": "Tabelul cu coloana rezidual se salvează în date/curat/."}],
       "explicatie": "Modelul și reziduurile sale stau la baza raportului de la cursul 8."}),
   manual=
   "<h2>Modelul echipei</h2>"
   "<p>Pasul de proiect: un model construit pas cu pas pentru întrebarea de "
   "cercetare a echipei, ca în lecție. Reziduurile sunt partea centrală a "
   "discuției din raport.</p>"
   + tabel(["Pasul", "Ce se realizează"], [
       ["1", "variabilele proiectului, construite și documentate în <code>decizii.md</code>"],
       ["2", "același eșantion pentru toate modelele"],
       ["3", "modelele, pas cu pas, cu R² și coeficienți"],
       ["4", "reziduurile: cele mai mari cinci, pozitive și negative"],
       ["5", "în <code>README.md</code>: ce se poate afirma și ce nu"],
   ]))

sl("s13", "Proiectul echipei", "Un reziduu",
   "<h2>Un reziduu de investigat</h2>"
   + ix("asteptari", "Reziduul ales de echipă", {
       "id": "c7-reziduu", "tip": "reziduu", "minim": 50,
       "sarcina": "Alegerea unei perechi cu reziduu mare și formularea unei "
                  "explicații posibile, care poate fi verificată.",
       "exemplu": "De exemplu: Ungaria-România este peste valoarea prezisă de "
                  "model; o explicație posibilă este minoritatea maghiară, "
                  "verificabilă la nivel de județ, comparând Harghita și "
                  "Covasna cu celelalte județe.",
       "multumesc": "Răspunsul va fi citit înainte de cursul următor."}))

SURSE_C7 = surse("Documentația modelului", [
    ("statsmodels: formule", "https://www.statsmodels.org/stable/example_formulas.html", "<code>smf.ols(\"log_sci ~ log_distanta\", data=d)</code>, pas cu pas"),
    ("statsmodels: regresia liniară", "https://www.statsmodels.org/stable/regression.html", "ce înseamnă fiecare rând din <code>summary()</code>"),
    ("geopandas: dissolve și sjoin", "https://geopandas.org/en/stable/docs/user_guide/aggregation_with_dissolve.html", "agregarea județelor în țări, pentru calculul graniței"),
])

FIN_C7 = ('<div class="fin3"><div class="fin3__g">'
   "<section><h4>Ce urmează la cursul 8</h4><ul>"
   "<li>Figura principală și tabelul modelelor.</li>"
   "<li>Un <code>README.md</code> care permite reproducerea întregii analize.</li>"
   "<li>Prezentarea echipei.</li></ul></section>"
   "<section><h4>Pregătirea pentru cursul 8</h4><ul>"
   "<li>Modelul și reziduurile, în depozit.</li>"
   "<li>Trei propoziții despre ce se poate afirma pe baza modelului.</li></ul></section>"
   "</div>"
   '<p class="fin3__a"><a class="leg" href="../">Pagina cursului 7</a>'
   '<a class="leg" href="../../c8-raportare/">Cursul 8</a></p></div>')

sl("s14", "Mai departe", "Pentru cursul următor",
   "<h2>La cursul 8: raportul</h2>" + FIN_C7,
   manual="<h2>La cursul 8: raportul</h2>" + FIN_C7 + SURSE_C7)


if __name__ == "__main__":
    L.scrie_tot()
