# -*- coding: utf-8 -*-
"""
Lecția 6: Analiza exploratorie și vizualizarea.

Urmează caietul 06_analiza_exploratorie (11 noiembrie 2026), organizat după tipul
datelor, ca în cursurile de vizualizare: verificările de dinainte de grafice, o
variabilă numerică, o variabilă categorică și lipsurile, numeric × numeric,
categoric × numeric, categoric × categoric, mai multe variabile, spațiul și
rețelele, apoi principiile unui grafic bun. Exemplele sunt ipotezele H1-H4 pe
datele SCI.

Numerele vin din date/c6-ipoteze.json și date/c6-vizual.json, calculate din
tabelele produse de caietele 04-06 și din contururile GISCO NUTS 2024 (20M,
EPSG:3035), ca în caiet. Hărțile folosesc date/explorator.json.

Rulare:  python _build/c6.py
"""

import json

from literatura import lecturi
from comun import Lectie, ix, verif, tabel, nota, surse, RAD

L = Lectie(6, "c6-analiza-exploratorie", "Analiza exploratorie și vizualizarea",
           "Analiza exploratorie și graficul potrivit tipului de date: o variabilă, două variabile numerice sau "
           "categorice, mai multe variabile, hărți și rețele, pe datele SCI.")
sl = L.sl

D = json.loads((RAD / "date" / "c6-ipoteze.json").read_text(encoding="utf-8"))
nr = lambda v: f"{v:,}".replace(",", ".")
ro = lambda x, z=2: f"{x:.{z}f}".replace(".", ",").replace("-", "−")
_NB6 = "06_analiza_exploratorie.ipynb"
H1, H2, H3, H4 = D["h1"], D["h2"], D["h3"], D["h4"]
X = json.loads((RAD / "date" / "c6-vizual.json").read_text(encoding="utf-8"))


def pas(date, vad, apoi):
    """Ciclul analizei pe un slide (titlul este întrebarea): datele și graficul, ce se vede, ce urmează."""
    return ('<span class="pas6">'
            f'<span><i>Datele, graficul</i>{date}</span>'
            f'<span><i>Ce se vede</i>{vad}</span>'
            f'<span class="pas6__apoi"><i>Mai departe</i>{apoi}</span></span>')


PAS = lambda *a: '<p class="pas6w">' + pas(*a) + "</p>"


# ===========================================================================
#  1-3. Cursul și analiza exploratorie
# ===========================================================================

CURSUL = tabel(["", "Conținutul", "Rezultatul"], [
    ["C1", "proiectul, mediul de lucru, tipurile de date și JSON", "<code>dsw/</code>, cu <code>.venv</code>"],
    ["C2", "colectarea datelor prin API: Eurostat, Banca Mondială", "<code>data/raw</code>"],
    ["C3", "surse diverse, preprocesare, Git și depozitul echipei", "<code>data/processed</code>, <code>proiect/</code>"],
    ["C4", "curățarea datelor și tabelul regiunilor", "<code>regiuni_nuts2.csv</code>"],
    ["C5", "integrare, baze de date și agregare", "perechile, în <code>dsw.db</code>"],
    ["<b>C6</b>", "<b>azi: analiza exploratorie și vizualizarea</b>", "<b>deciziile pentru model</b>"],
    ["C7", "variabile derivate și model", "modelul SCI"],
    ["C8", "raportul și prezentarea proiectului", "raportul echipei"],
])

sl("s1", "Cursul", "Unde suntem",
   "<h2>Unde suntem în curs</h2>"
   "<p class=\"cheie\">Perechile sunt în baza de date. Înainte de model: ce arată datele și ce merită verificat.</p>"
   + CURSUL,
   manual=
   "<h2>Analiza exploratorie</h2>"
   "<p>Datele sunt curate (C4) și în baza de date (C5). Înainte de orice model, analiza exploratorie caută ce "
   "merită verificat, iar instrumentul ei principal este graficul. Graficul potrivit depinde de tipul datelor: o "
   "variabilă sau două, numerice sau categorice, în spațiu sau în rețea. Lecția urmează această ordine, cu "
   "exemplele luate din datele SCI.</p>"
   + CURSUL
   + nota("Caietul lecției", f"<code>{_NB6}</code>, în <code>dsw/curs/</code>. Pachete noi: <code>seaborn</code>, "
                             "<code>geopandas</code>, <code>networkx</code>, toate în <code>requirements.txt</code> "
                             "(se instalează din nou cu <code>pip install -r requirements.txt</code>).", True))


CICLU = (
    '<div class="ed6">'
    '<div><small>1 · întrebarea</small><b>Legăturile scad cu distanța?</b></div>'
    '<div><small>2 · datele, graficul</small><b>două variabile numerice: SCI median pe intervale de distanță</b></div>'
    '<div><small>3 · ce se vede</small><b>scad; dar regiunile din aceeași țară sunt și apropiate</b></div>'
    '<div class="nou"><small>4 · mai departe</small><b>E granița sau distanța?</b></div>'
    '</div>'
    '<p class="ed6__inapoi">întrebarea nouă reia ciclul</p>'
    '<div class="ed6o">'
    '<div><b>Ipoteze</b><span>ce intră în modelul din C7</span></div>'
    '<div><b>Decizii</b><span>scara, ce perechi intră, ce se exclude</span></div>'
    '<div><b>Excepții</b><span>cazurile de explicat după model</span></div>'
    '</div>')

sl("s2", "Analiza exploratorie", "Un ciclu, nu o listă",
   "<h2>Analiza exploratorie: un ciclu</h2>"
   "<p class=\"cheie\">Analiza exploratorie nu confirmă o teorie: caută ce merită verificat. Fiecare grafic răspunde "
   "la o întrebare și ridică, de obicei, una nouă. Slide-urile care urmează parcurg ciclul: titlul este întrebarea.</p>"
   + CICLU,
   manual=
   "<h2>Analiza exploratorie: un ciclu</h2>"
   "<p>Tukey (1977), care a dat numele metodei, o descrie ca pe o muncă de detectiv: se caută indicii înainte de "
   "a se judeca un caz. Wickham și colegii (R for Data Science, 2023) o descriu ca pe un ciclu: o întrebare, un "
   "grafic sau un tabel care îi răspunde, apoi întrebarea nouă pe care o ridică răspunsul. Nu există o listă "
   "completă de grafice de făcut; există întrebări bune.</p>"
   + CICLU
   + "<p>Analiza se termină cu trei rezultate: ipotezele care intră în model, deciziile despre date (scara, ce se "
     "exclude, ce lipsește) și excepțiile care trebuie explicate. Fără ele, analiza exploratorie rămâne o colecție "
     "de grafice.</p>"
   + nota("Exploratoriu și confirmatoriu",
          "Aceleași date nu pot și genera o ipoteză, și o confirma. Ce se găsește aici rămâne de verificat: în model, "
          "pe alte date sau în literatură.", True))


TIPURI = [
    ("0", "Înainte de grafice", "numărul de rânduri, o sursă externă, extremele", "shape · nlargest()"),
    ("1", "O variabilă numerică", "histogramă, boxplot, scara logaritmică", "sns.histplot · sns.boxplot"),
    ("2", "O variabilă categorică", "grafic cu bare; lipsurile, pe hartă", "sns.countplot · isna()"),
    ("3", "Numeric × numeric", "histogramă bidimensională, mediane pe intervale, matricea de corelație", "histplot(x=, y=) · heatmap"),
    ("4", "Categoric × numeric", "boxplot sau mediane pe grupuri", "sns.boxplot(x=, y=)"),
    ("5", "Categoric × categoric", "tabel de contingență, ca heatmap", "pd.crosstab · sns.heatmap"),
    ("6", "Mai multe variabile", "culoarea ca a treia variabilă, fațete", "hue= · col="),
    ("7", "Spațiu", "hartă coropletă: scara secvențială sau divergentă", "harta.plot(column=)"),
    ("8", "Rețele", "noduri, legături, comunități", "networkx"),
]
TIP_HTML = ('<div class="q6 q6--tip">' + "".join(
    f'<div><i>{k}</i><b>{q}</b><span>{c}</span><code>{u}</code></div>' for k, q, c, u in TIPURI) + "</div>")

sl("s3", "Vizualizarea", "Graficul, după tipul datelor",
   "<h2>Graficul potrivit depinde de tipul datelor</h2>"
   + TIP_HTML,
   manual=
   "<h2>Graficul potrivit depinde de tipul datelor</h2>"
   "<p>Cursurile și ghidurile de vizualizare (Wilke, <i>Fundamentals of Data Visualization</i>; Holtz și Healy, "
   "<i>From Data to Viz</i>) aleg graficul după datele de arătat: câte variabile, de ce tip, câte observații. "
   "Lecția urmează aceeași ordine; în caiet, graficele folosesc <code>seaborn</code>, construit peste "
   "<code>matplotlib</code>: un tabel, coloana de pe fiecare axă și, eventual, coloana care dă culoarea.</p>"
   + TIP_HTML
   + "<pre><code>import seaborn as sns\n"
     "sns.set_theme(style=\"whitegrid\")      # același aspect pentru toate graficele\n"
     "sns.histplot(perechi, x=\"sci\", log_scale=True)</code></pre>"
   + nota("Exemplele", "Patru ipoteze din literatură (distanța, granița, economia, migrația) dau exemplele "
                        "părților 3-6. Fiecare grafic răspunde la o întrebare și se încheie cu o decizie pentru "
                        "modelul din C7. Nu se fac teste: aceeași regiune apare în 297 de perechi, deci perechile nu sunt "
                        "observații independente; corelațiile descriu datele, nu dovedesc cauze.", True))


# ===========================================================================
#  4-5. Ce conțin datele
# ===========================================================================

_SUS, _JOS = D["extreme"]["sus"][0], D["extreme"]["jos"][0]
VERIF_DATE = (
    '<div class="ck6">'
    '<div><i class="da">✓</i><b>Numărul de perechi</b>'
    '<span>298 de regiuni, fiecare cu toate celelalte, o singură dată: 298 × 297 / 2</span>'
    f'<code>{nr(D["n"])}</code></div>'
    '<div><i class="da">✓</i><b>O sursă externă</b>'
    '<span>populația României, adunată pe cele 8 regiuni, are ordinul de mărime cunoscut</span>'
    f'<code>{ro(D["ro_pop"] / 1e6)} mil.</code></div>'
    '<div><i class="nu">✗</i><b>Extremele</b>'
    f'<span>cea mai legată pereche ({_SUS[1]} și {_SUS[3]}, {nr(_SUS[4])}) și cea mai puțin legată '
    f'({_JOS[1]} și {_JOS[3]}, {_JOS[4]}) au aceeași regiune: Svalbard</span>'
    '<code>populația: 0</code></div>'
    '</div>')

sl("s4", "Înainte de grafice", "Ce conțin datele?",
   "<h2>Ce conțin datele?</h2>"
   + VERIF_DATE
   + PAS("toate perechile, înainte de orice grafic: o socoteală, o sursă externă, extremele",
         "numărul și totalul se potrivesc; extremele au aceeași regiune, Svalbard: SCI se împarte la numărul de "
         "utilizatori, iar cu un numitor atât de mic raportul este instabil",
         "Svalbard se exclude din model. Cum arată o pereche obișnuită?"),
   manual=
   "<h2>Ce conțin datele: trei verificări</h2>"
   "<p>Înainte de primul grafic, trei verificări care nu cer nicio ipoteză. Numărul de rânduri se compară cu o "
   "socoteală făcută dinainte; un total se compară cu o sursă externă; primele și ultimele valori se citesc una "
   "câte una.</p>"
   + VERIF_DATE
   + tabel(["Cele mai legate", "SCI", "Cele mai puțin legate", "SCI"],
           [[f"{a[1]} · {a[3]}", nr(a[4]), f"{b[1]} · {b[3]}", nr(b[4])]
            for a, b in zip(D["extreme"]["sus"], D["extreme"]["jos"])])
   + f"<p>Svalbard apare în {sum('NO0B' in (p[0], p[2]) for p in D['extreme']['sus'] + D['extreme']['jos'])} din aceste șase perechi. Tabelul regiunilor îi dă populația 0: locuitorii sunt "
     "numărați în altă parte. Este un caz de manual pentru extreme: nu sunt descoperiri, ci o consecință a felului în "
     "care se construiește indicatorul.</p>"
   + "<pre><code>len(perechi), 298 * 297 // 2\n"
     "regiuni[regiuni[\"tara\"] == \"RO\"][\"populatie\"].sum()\n"
     "perechi.nlargest(3, \"sci\")\n"
     "perechi.nsmallest(3, \"sci\")</code></pre>")


# ===========================================================================
#  1-2. O variabilă
# ===========================================================================

HISTO = {
    "valori": D["esantion"], "bare": 28,
    "etLin": "scara originală", "etLog": "scara log10",
    "axaX": "SCI", "axaY": "perechi",
    "txtLin": f"Aproape toate perechile stau în prima bară. Media este {nr(D['medie'])}, mediana doar "
              f"{nr(D['mediana'])}: câteva perechi foarte legate (maximul: {nr(D['max'])}) trag media în sus.",
    "txtLog": "Pe scara logaritmică (3 = 1.000, 4 = 10.000) distribuția se vede. De aici înainte, SCI se citește pe "
              "această scară.",
}

sl("s6", "O variabilă numerică", "Cum arată o pereche obișnuită?",
   "<h2>Cum arată o pereche obișnuită?</h2>"
   + ix("histo", "SCI pe perechi de regiuni", HISTO)
   + PAS("o variabilă numerică: histograma, pe două scări",
         f"asimetrie pozitivă: media e de {D['medie'] / D['mediana']:.0f} ori mediana",
         "SCI pe scara logaritmică, comparații cu mediana. Ce lipsește din date?"),
   manual=
   "<h2>Cum arată o pereche obișnuită</h2>"
   f"<p>Distribuția celor {nr(D['n'])} de perechi. Histograma de aici desenează "
   f"{nr(len(D['esantion']))} de perechi alese la întâmplare; statisticile sunt calculate pe toate. Media "
   f"({nr(D['medie'])}) este de opt ori mediana ({nr(D['mediana'])}): asimetrie pozitivă, cu o coadă lungă "
   "trasă de câteva perechi foarte legate. <b>Decizie</b>: SCI se citește pe scara logaritmică, iar comparațiile folosesc mediana.</p>"
   + ix("histo", "SCI pe perechi de regiuni", HISTO)
   + "<p>Boxplotul rezumă aceeași distribuție: cutia merge de la prima la a treia cuartilă (lungimea ei este "
     "abaterea intercuartilică, IQR), linia din cutie este mediana, mustățile ajung până la cea mai depărtată valoare "
     "aflată la cel mult 1,5 × IQR de cutie, iar punctele de dincolo sunt valorile extreme după regula lui Tukey. Cu "
     "zeci de mii de perechi, regula marchează sute de puncte: nu sunt erori, ci coada distribuției. Boxplotul este "
     "util mai ales pentru a compara grupuri (partea 4).</p>"
   + "<pre><code>perechi[\"sci\"].describe()\n"
     "sns.histplot(perechi, x=\"sci\", bins=40, log_scale=True)\n"
     "sns.boxplot(perechi, x=\"sci\", log_scale=True)</code></pre>")


HARTA_LIPS = {
    "niveluri": ["regiuni"], "nivel": "regiuni", "masura": "lips", "ales": "DE21", "masuri": ["lips"],
    "faraLinii": True,
    "povesti": [
        {"t": "Germania și Franța", "nivel": "regiuni", "masura": "lips", "ales": "DE21",
         "text": f"Rețelele sociale lipsesc în toate cele {D['lips_rs']['DE']} de regiuni ale Germaniei, la fel în "
                 f"Franța ({D['lips_rs']['FR']}), Turcia ({D['lips_rs']['TR']}) și Grecia ({D['lips_rs']['EL']}). "
                 "O variabilă cu astfel de lipsuri scoate din analiză țări întregi."},
        {"t": "Elveția și Norvegia", "nivel": "regiuni", "masura": "lips", "ales": "CH01",
         "text": "PIB-ul pe locuitor lipsește în toate regiunile Elveției și ale Norvegiei, deci H3 se calculează fără "
                 "ele: două țări bogate lipsesc din comparația economică."},
        {"t": "Balcanii de vest", "nivel": "regiuni", "masura": "lips", "ales": "AL01",
         "text": "Albania, Bosnia și Herțegovina, Kosovo: aproape toate variabilele lipsesc. Pentru SCI sunt în date, "
                 "pentru restul indicatorilor, nu."},
    ]}

sl("s5", "O variabilă categorică", "Unde lipsesc datele?",
   "<h2>Unde lipsesc datele?</h2>"
   + ix("harta", "Variabilele lipsă, pe regiuni", HARTA_LIPS)
   + PAS("o variabilă categorică, lipsește sau nu: numărată pe regiuni, pe hartă",
         "lipsurile vin pe țări întregi, nu la întâmplare",
         "fiecare rezultat spune pe câte perechi s-a calculat. Acum, întrebările."),
   manual=
   "<h2>Ce lipsește și unde</h2>"
   "<p>Pentru o variabilă categorică, graficul este o bară pe categorie (<code>sns.countplot</code>). Tot aici, "
   "o variabilă categorică deosebită: lipsește sau nu.</p>"
   f"<p>Numărul de valori lipsă spune puțin; contează unde sunt. Din cele 298 de regiuni, rețelele sociale lipsesc "
   f"la {D['lips']['retele_sociale']}, PIB-ul pe locuitor la {D['lips']['pib_locuitor']}. Pe hartă se vede că "
   "lipsurile nu sunt la întâmplare: vin pe țări întregi.</p>"
   + ix("harta", "Variabilele lipsă, pe regiuni", HARTA_LIPS)
   + "<p>Consecința pentru analiză: o comparație care folosește PIB-ul pierde Elveția și Norvegia, una care folosește "
     "rețelele sociale pierde Germania și Franța. Câte perechi rămân se spune de fiecare dată.</p>"
   + "<pre><code>sns.countplot(regiuni, y=\"tara\")      # câte regiuni are fiecare țară\n"
     "regiuni.isna().sum()\n"
     "regiuni[regiuni[\"retele_sociale\"].isna()][\"tara\"].value_counts()</code></pre>")


# ===========================================================================
#  3. Numeric × numeric
# ===========================================================================

IPOTEZE = tabel(["Ipoteza", "Ce ar trebui să se vadă", "Graficul (partea)"], [
    ["<b>H1</b> Distanța", "SCI scade cu distanța", "histogramă bidimensională, mediane pe intervale (3)"],
    ["<b>H2</b> Granița", "la aceeași distanță, regiunile din aceeași țară sunt mai legate", "boxplot pe grupuri (4), tabel de contingență (5)"],
    ["<b>H3</b> Economia", "legăturile depind de decalajul economic", "decalajul de PIB, Spearman (3)"],
    ["<b>H4</b> Migrația", "țările cu mulți migranți între ele sunt mai legate", "scatter log-log, număr și rată (3); culoarea (6)"],
])
INTREBARI = [
    ("H1", "Scad legăturile cu distanța?", "numeric × numeric", "mediane pe intervale"),
    ("H3", "Contează decalajul economic?", "numeric × numeric", "matricea de corelație"),
    ("H2", "La aceeași distanță, aceeași țară e mai legată?", "categoric × numeric", "grupuri pe straturi de distanță"),
    ("H4", "Mai mulți migranți, mai multe legături?", "numeric × numeric, apoi trei variabile", "dispersie log-log, culoare"),
]
INTREB_HTML = ('<div class="q6 q6--h">' + "".join(
    f'<div><i>{k}</i><b>{q}</b><span>{t}</span><code>{g}</code></div>' for k, q, t, g in INTREBARI) + "</div>")

sl("h0", "Întrebările", "Ce întrebăm datele?",
   "<h2>Ce întrebăm datele? Patru ipoteze</h2>"
   + INTREB_HTML
   + "<p class=\"cub__regula\">Ipotezele vin din literatură și se scriu înainte de grafice; tipul variabilelor alege "
     "graficul. Fără teste: aceeași regiune apare în 297 de perechi, deci perechile nu sunt independente.</p>",
   manual=
   "<h2>Ce întrebăm datele? Patru ipoteze</h2>"
   "<p>De aici, graficele leagă două sau mai multe variabile, iar alegerea lor are nevoie de ipoteze, altfel orice "
   "pereche de variabile ar fi de comparat. Bailey și colegii (2020) găsesc pentru Europa efecte puternice ale "
   "distanței și ale granițelor; Bailey și colegii (2018) arată că SCI este asociat cu migrația. De aici, patru "
   "așteptări, scrise înainte de date, fiecare cu graficul potrivit tipului de variabile.</p>"
   + IPOTEZE
   + "<p>Ordinea slide-urilor urmează ciclul: fiecare răspuns ridică întrebarea următoare. După distanță vine "
     "economia; apoi întrebarea dacă diferența dintre aceeași țară și țări diferite ține de graniță sau de distanță; "
     "apoi migrația, care trece granița.</p>"
   + lecturi(["bailey2018", "bailey2020"], "Literatura ipotezelor"))


V2 = verif("c6-v2", 1,
           f"Corelația Spearman dintre distanță și SCI este {ro(H1['rho'])}. Ce se poate spune?",
           ["Distanța reduce legăturile cu 46%", "Perechile mai îndepărtate tind să fie mai puțin legate",
            "46% din SCI vine din distanță", "Relația este liniară"],
           "Spearman arată că ordinea celor două variabile merge împreună, invers. Nu este un procent și nu spune "
           "ce produce relația: distanța poate fi și ea un înlocuitor pentru graniță, limbă sau istorie.")
_SC = H1["med"][0] / H1["med"][-1]
TREPTE_H1 = {
    "titlu": "SCI median pe intervale de distanță",
    "intervale": H1["intervale"],
    "serii": [{"t": "toate perechile", "c": "accent", "med": H1["med"], "n": H1["n"]}],
    "axaX": "distanța dintre centrele regiunilor, km", "axaY": "SCI median (scară logaritmică)",
    "text": pas(f"două variabile numerice, {nr(D['n'])} de perechi: medianele pe intervale de distanță",
                f"<b>ρ Spearman = {ro(H1['rho'])}</b>; de la 0-100 km la peste 2.000 km, mediana scade de aproximativ "
                f"{round(_SC, -1):.0f} de ori",
                "Ce alte variabile ale regiunilor contează?"),
}

sl("s7", "Numeric × numeric", "H1: distanța",
   "<h2>Scad legăturile cu distanța?</h2>"
   + ix("trepte", "SCI median, pe intervale de distanță", TREPTE_H1),
   manual=
   "<h2>H1: scad legăturile cu distanța?</h2>"
   "<p>Cu 44.253 de puncte, un grafic de dispersie (scatter) devine o pată: punctele se acoperă unele pe altele. "
   "Histograma bidimensională împarte planul în căsuțe și colorează fiecare căsuță după câte perechi cad în ea; "
   "medianele pe intervale arată forma relației într-o singură linie.</p>"
   "<p>Distanța dintre două regiuni se ia între centrele lor, pe harta în proiecția europeană EPSG:3035, care măsoară "
   "în metri. <code>pd.cut</code> pune fiecare distanță în intervalul ei; apoi se agregă, ca în C5. Intervalele au lățimi "
   "diferite, alese ca fiecare să aibă destule perechi. Coeficientul de corelație Spearman (ρ) înlocuiește valorile "
   "cu rangurile lor și măsoară cât de monoton variază cele două variabile împreună, între -1 și 1. Nu presupune o "
   "relație liniară, nu este tras de valorile extreme și nu se schimbă pe scara logaritmică, pentru că logaritmul "
   "păstrează ordinea.</p>"
   + ix("trepte", "SCI median, pe intervale de distanță", TREPTE_H1)
   + "<pre><code>praguri = [0, 100, 250, 500, 1000, 2000, 10000]\n"
     "perechi[\"interval_km\"] = pd.cut(perechi[\"distanta_km\"], praguri)\n"
     "sns.histplot(perechi, x=\"distanta_km\", y=\"sci\", log_scale=True, bins=50, cmap=\"mako_r\")\n"
     "sns.pointplot(perechi, x=\"interval_km\", y=\"sci\", estimator=\"median\", errorbar=None, log_scale=True)</code></pre>",
   dupa=V2)

E = H3["exemplu"]
_DEC = abs(E["a"][2] - E["b"][2])
_MX = max(E["a"][2], E["b"][2])
ECON = (
    '<div class="h3x">'
    + "".join(f'<div class="h3x__r"><b>{nr(v)}</b><div class="h3x__b" style="height:{round(v / _MX * 150)}px"></div>'
              f'<small>{n}<br><code>{c}</code></small></div>' for c, n, v in [E["a"], E["b"]])
    + f'<div class="h3x__d"><code>|{nr(E["a"][2])} − {nr(E["b"][2])}|</code><b>{nr(_DEC)}</b>'
      '<small>decalajul de PIB pe locuitor</small></div>'
    + "</div>")

_ET = {"pib_locuitor": "PIB/loc.", "studii_superioare": "studii sup.", "somaj": "șomaj", "varsta_medie": "vârsta",
       "densitate": "densitate", "retele_sociale": "rețele soc."}
_CV = X["cor"]["var"]
_ton = lambda v: min(7, max(1, round(4 + v * 3)))          # -1 → 1 (roșu), 0 → 4 (neutru), 1 → 7 (verde)
CORELATII = ('<div class="cm6" style="--n:%d">' % len(_CV) + "<span></span>"
             + "".join(f"<b>{_ET[c]}</b>" for c in _CV)
             + "".join(f"<b class=\"cm6__r\">{_ET[a]}</b>" + "".join(
                 f'<i class="t{_ton(v)}" title="{_ET[a]} × {_ET[b]}: ρ = {ro(v)}">{ro(round(v, 1) or 0.0, 1) if a != b else ""}</i>'
                 for b, v in zip(_CV, rand)) for a, rand in zip(_CV, X["cor"]["v"]))
             + "</div>")

sl("s9", "Numeric × numeric", "H3: indicatorii regiunilor",
   "<h2>Ce indicatori merg împreună? Contează economia?</h2>"
   "<div class=\"cm6w\">" + CORELATII
   + PAS("șase variabile numerice, 298 de regiuni: matricea de corelație Spearman, scară divergentă",
         f"PIB-ul merge cu studiile și cu densitatea (multicoliniaritate); între perechi, decalajul de PIB abia contează "
         f"(ρ = {ro(H3['rho'])})",
         "Regiunile din aceeași țară sunt și apropiate: e granița sau distanța?") + "</div>",
   manual=
   "<h2>Matricea de corelație</h2>"
   "<p>Cu mai multe variabile numerice, perechile se văd toate odată într-o matrice de corelație, desenată ca "
   "heatmap. Scara de culori este divergentă: mijlocul neutru este 0, cele două capete, simetrice, sunt -1 și 1. Fiecare "
   "coeficient folosește regiunile care au ambele valori, deci numărul de regiuni diferă puțin de la o căsuță la "
   "alta.</p>"
   + "<div class=\"cm6w\">" + CORELATII + "</div>"
   + "<pre><code>indicatori = [\"pib_locuitor\", \"studii_superioare\", \"somaj\", \"varsta_medie\", \"densitate\", \"retele_sociale\"]\n"
     "corelatii = regiuni[indicatori].corr(method=\"spearman\")\n"
     "sns.heatmap(corelatii, annot=True, fmt=\".1f\", cmap=\"RdBu_r\", vmin=-1, vmax=1)</code></pre>"
   + "<h3>H3: asemănarea economică</h3>"
   "<p>Perechea nu are ordine (A-B este tot una cu B-A), deci variabila este diferența absolută de PIB pe locuitor. Analiza folosește doar "
   "perechile care au PIB la ambele capete și spune câte sunt: fără Elveția și Norvegia (slide-ul cu lipsurile).</p>"
   + ECON
   + f"<p>Pe cele {nr(H3['n'])} de perechi cu PIB la ambele capete, din {nr(D['n'])}: <b>ρ = {ro(H3['rho'])}</b>. "
     "Corelația este pozitivă, dar slabă. Bailey și colegii (2020) găsesc, pentru venit, că regiunile cu venituri "
     "diferite sunt mai legate și o pun pe seama migrației din regiunile mai sărace spre cele mai bogate; pentru "
     "vârstă și educație găsesc invers, că regiunile asemănătoare sunt mai legate. Corelația de aici nu ține seama de "
     "distanță: regiunile apropiate au și PIB asemănător, și SCI mare. Distanța se ține constantă abia în modelul "
     "din C7.</p>"
   + "<pre><code>economice = perechi.dropna(subset=[\"pib_locuitor_1\", \"pib_locuitor_2\"])\n"
     "decalaj = (economice[\"pib_locuitor_1\"] - economice[\"pib_locuitor_2\"]).abs()\n"
     "decalaj.corr(economice[\"sci\"], method=\"spearman\")</code></pre>")


_K = X["contingenta"]
_PROC = [d / (d + n) for d, n in zip(_K["da"], _K["nu"])]
_tare = lambda v: ' class="tare"' if v > .55 else ""
_pr = lambda v: f"{v:.0%}" if v >= .1 else f"{v:.1%}".replace(".", ",")
CONTINGENTA = ('<div class="ct6"><span></span><b>aceeași țară</b><b>țări diferite</b>'
               + "".join(f'<b class="ct6__r">{t} km</b>'
                         f'<i style="--p:{p:.3f}"{_tare(p)}>{_pr(p)}<small>{nr(d)}</small></i>'
                         f'<i style="--p:{1 - p:.3f}"{_tare(1 - p)}>{_pr(1 - p)}<small>{nr(n)}</small></i>'
                         for t, p, d, n in zip(_K["intervale"], _PROC, _K["da"], _K["nu"]))
               + "</div>")
V_CT = verif("c6-v-ct", 1,
             "Ce ar arăta comparația „aceeași țară față de țări diferite” pe toate perechile deodată?",
             ["Doar efectul graniței", "Granița și distanța, amestecate", "Nimic", "Doar efectul distanței"],
             "Perechile din aceeași țară sunt aproape toate apropiate, deci o comparație fără distanță amestecă cele două "
             "efecte. Distanța este aici o variabilă de confuzie; de aceea H2 se compară pe intervale.")

sl("x1", "Categoric × categoric", "Tabelul de contingență",
   "<h2>Sunt perechile din aceeași țară și mai apropiate?</h2>"
   "<div class=\"ct6w\">" + CONTINGENTA
   + PAS("două variabile categorice: tabel de contingență, proporții pe rând",
         f"sub 100 km, {_PROC[0]:.0%} din perechi sunt în aceeași țară; peste 1.000 km, sub 1%",
         "distanța este o <b>variabilă de confuzie</b>: granița se compară la aceeași distanță") + "</div>",
   manual=
   "<h2>Două variabile categorice: tabelul de contingență</h2>"
   "<p>Două variabile categorice se încrucișează cu <code>pd.crosstab</code>: câte rânduri are fiecare combinație. "
   "Cu <code>normalize=\"index\"</code>, fiecare rând se împarte la totalul lui și devine o distribuție "
   "condiționată; ca heatmap, tabelul se citește "
   "dintr-o privire. Aici, ce parte din perechile fiecărui interval de distanță sunt în aceeași țară.</p>"
   + "<div class=\"ct6w\">" + CONTINGENTA + "</div>"
   + "<p>Distanța este legată și de grupare (aceeași țară sau nu), și de SCI: este o variabilă de confuzie pentru "
     "comparația din slide-ul anterior. O comparație pe toate perechile ar fi atribuit graniței și efectul distanței; "
     "comparația pe intervale de distanță (stratificarea) ține distanța aproximativ constantă în fiecare strat. Același tabel, cu țările pe rânduri și comunitățile rețelei pe coloane, arată "
     "cât urmează comunitățile granițele (partea 8).</p>"
   + "<pre><code>tabel = pd.crosstab(perechi[\"interval_km\"], perechi[\"aceeasi_tara\"], normalize=\"index\")\n"
     "sns.heatmap(tabel, annot=True, fmt=\".0%\", cmap=\"Blues\")</code></pre>",
   dupa=V_CT)


# ===========================================================================
#  4-6. Grupuri și mai multe variabile
# ===========================================================================

_I = H2["intervale"].index("250-500")
_R = H2["da"]["med"][_I] / H2["nu"]["med"][_I]
TREPTE_H2 = {
    "titlu": "SCI median, aceeași țară și țări diferite",
    "intervale": H2["intervale"], "raport": True,
    "serii": [{"t": "aceeași țară", "c": "accent", "med": H2["da"]["med"], "n": H2["da"]["n"]},
              {"t": "țări diferite", "c": "text-3", "med": H2["nu"]["med"], "n": H2["nu"]["n"]}],
    "axaX": "distanța dintre centrele regiunilor, km", "axaY": "SCI median (scară logaritmică)",
    "text": pas("categoric × numeric: medianele celor două grupuri, pe straturi de distanță",
                f"la 250-500 km, mediana internă e de {_R:.0f} ori mai mare; diferența rămâne la toate distanțele",
                "Ce legături trec totuși granița? Migrația."),
}
V3 = verif("c6-v3", 1,
           "La aceeași distanță, mediana internă e de 15 ori mai mare. Ce rămâne amestecat în această diferență?",
           ["Nimic: este efectul graniței", "Limba, istoria, instituțiile", "Distanța", "Numărul de perechi"],
           "Stratificarea ține distanța aproximativ constantă, dar două regiuni din aceeași țară au și aceeași limbă, "
           "aceeași istorie, aceleași instituții. Diferența este asocierea cu granița, nu efectul ei cauzal.")

sl("s8", "Categoric × numeric", "H2: granița",
   "<h2>Contează granița, la aceeași distanță?</h2>"
   + ix("trepte", "Aceeași țară, țări diferite", TREPTE_H2),
   manual=
   "<h2>H2: granița, la aceeași distanță</h2>"
   "<p>O variabilă categorică (aceeași țară sau nu) și una numerică (SCI): graficul compară grupurile, cu un "
   "boxplot sau cu medianele lor. În C5, SCI-ul mediu era mult mai mare în aceeași țară. Dar perechile interne sunt și mai apropiate, deci "
   "comparația amesteca granița cu distanța. Comparația în grupuri comparabile, pe același interval de distanță, "
   "scoate distanța din diferență.</p>"
   + ix("trepte", "Aceeași țară, țări diferite", TREPTE_H2)
   + "<p>Nu este încă efectul cauzal al graniței: două regiuni din aceeași țară au și aceeași limbă, aceeași "
     "istorie și aceleași instituții.</p>"
   + "<pre><code>perechi[\"aceeasi_tara\"] = perechi[\"tara_1\"] == perechi[\"tara_2\"]\n"
     "sns.boxplot(perechi, x=\"interval_km\", y=\"sci\", hue=\"aceeasi_tara\", log_scale=True, showfliers=False)\n"
     "perechi.groupby([\"interval_km\", \"aceeasi_tara\"], observed=True)[\"sci\"].median().unstack()</code></pre>",
   dupa=V3)




NOR = {
    "variabile": [
        {"k": "nr", "et": "migranți, număr", "rho": H4["rho_nr"],
         "text": "Un milion de migranți înseamnă mult pentru Austria și puțin pentru Germania."},
        {"k": "rata", "et": "migranți la 1.000 de locuitori", "rho": H4["rho_rata"],
         "text": "Raportată la populația celor două țări, corelația aproape se dublează: SCI este și el o măsură relativă. "
                 "<b>Decizie</b>: în model intră rata. Mai departe: perechile care nu se potrivesc."}],
    "puncte": [{"t": t, "x": {"nr": m, "rata": r}, "y": s, "g": bool(g)} for t, s, m, r, g in H4["puncte"]],
    "etY": "SCI (scară logaritmică)", "etG": "perechile României", "etN": "celelalte perechi",
}

sl("s10", "Numeric × numeric", "H4: migrația",
   "<h2>Mai mulți migranți, mai multe legături?</h2>"
   + ix("nor", "Migrația și SCI, pe perechi de țări", NOR),
   manual=
   "<h2>H4: migranți, ca număr sau ca rată</h2>"
   f"<p>Perechile de țări cu migrația cunoscută în ambele sensuri: {H4['n']}. Corelația cu numărul de migranți este "
   f"pozitivă, dar nu foarte mare ({ro(H4['rho_nr'])}). SCI este însă relativ: împărțit la numărul de utilizatori din "
   "cele două țări. Comparabilă cu el este o rată: migranți la 1.000 de locuitori ai celor două țări, cu populația "
   "de la Banca Mondială, din C2. <b>Decizie</b>: în model intră rata, nu numărul.</p>"
   "<p>Rămâne o rezervă: două rapoarte cu numitori corelați (utilizatori, populație) pot fi corelate și din "
   "construcție. Corelația este un indiciu, nu o dovadă.</p>"
   + ix("nor", "Migrația și SCI, pe perechi de țări", NOR)
   + f"<p>Zborurile, exercițiul din caiet: pe {H4['zboruri']['n']} de perechi cu pasageri, ρ = "
     f"{ro(H4['zboruri']['rho'])}, mult sub migrație. Numărul de pasageri depinde mai ales de mărimea țărilor.</p>")


RO = D["ro"]
_NUME = {"AT": "Austria", "DE": "Germania", "HU": "Ungaria", "IE": "Irlanda", "IT": "Italia", "BE": "Belgia",
         "ES": "Spania", "LU": "Luxemburg"}
DUBLU = {"randuri": [{"t": _NUME.get(c, c), "sci": s, "rata": r, "ev": c in ("IT", "HU")} for c, s, m, r, p in RO]}
V_RO = verif("c6-v-ro", 1,
             "Ungaria are un SCI mare cu România, dar puțini migranți la mie. Care explicație este cea mai plauzibilă?",
             ["O eroare în date", "Minoritatea maghiară: legături vechi, fără migrație", "Turismul", "Distanța"],
             "O parte din legături vin din minoritatea maghiară din România, nu din migrație. La cursul 7, distanța și "
             "migrația intră în același model, iar ce rămâne neexplicat arată astfel de cazuri.")

sl("s12", "Numeric × numeric", "Ghicitoarea din C1",
   "<h2>De ce Italia e abia a cincea?</h2>"
   + ix("dublu", "SCI și migranții la mie", DUBLU)
   + PAS("perechile României: SCI și rata la mie, una lângă alta",
         "Italia: cea mai mare rată, abia a cincea după SCI; Ungaria: SCI mare, puțini migranți",
         "Peste graniță, la aceeași distanță, contează migrația?"),
   manual=
   "<h2>Ghicitoarea din C1: partenerii României</h2>"
   "<p>La C1, Italia, țara cu cei mai mulți români, era abia pe locul cinci după SCI. Cu migrația raportată la "
   "populație, ghicitoarea se lămurește doar în parte.</p>"
   + ix("dublu", "SCI și migranții la mie", DUBLU)
   + tabel(["Țara", "SCI", "migranți", "la mie", "pasageri"],
           [[_NUME.get(c, c), nr(s), nr(m), ro(r, 1), nr(p)] for c, s, m, r, p in RO])
   + "<p>În caietul 06, după partea 3.4, cu tabelul <code>cu_migratie</code>:</p>"
   + "<pre><code>cu_ro = cu_migratie[(cu_migratie[\"tara_1\"] == \"RO\") | (cu_migratie[\"tara_2\"] == \"RO\")]\n"
     "cu_ro.sort_values(\"sci\", ascending=False).head(8)</code></pre>",
   dupa=V_RO)


_M = X["migr"]
_K0 = 2                                                    # de la 250 km: mai jos, unele grupe au câteva perechi
_RAP = [_M["mare"]["med"][k] / _M["mică"]["med"][k] for k in range(_K0, 6)]
TREPTE_MIGR = {
    "titlu": "SCI median peste graniță, după migrația dintre țări",
    "intervale": D["h1"]["intervale"][_K0:],
    "serii": [{"t": f"migrație {g}", "c": c, "med": _M[g]["med"][_K0:], "n": _M[g]["n"][_K0:]}
              for g, c in [("mică", "sci-1"), ("medie", "sci-3"), ("mare", "sci-6")]],
    "axaX": "distanța dintre centrele regiunilor, km", "axaY": "SCI median (scară logaritmică)",
    "text": pas("trei variabile: distanța (axa), grupa de migrație (culoarea), SCI median; doar perechi peste graniță",
                f"la aceeași distanță, migrația mare: mediana de {ro(min(_RAP), 1)} până la {ro(max(_RAP), 1)} ori mai mare "
                "decât migrația mică",
                "Unde, pe hartă, ies legăturile din tipar?"),
}

sl("m1", "Mai multe variabile", "Granița, distanța, migrația",
   "<h2>Contează migrația, la aceeași distanță?</h2>"
   + ix("trepte", "Peste graniță, după migrație", TREPTE_MIGR),
   manual=
   "<h2>Mai multe variabile: culoare și fațete</h2>"
   "<p>A treia variabilă intră în grafic ca <b>culoare</b> (<code>hue=</code>) sau ca <b>fațete</b>, adică același "
   "grafic repetat pentru fiecare grup (<code>col=</code>). Aici, perechile de regiuni din țări diferite primesc "
   f"grupa de migrație a perechii lor de țări (H4). Grupele se fac pe cele {X['n_tari_migr']} de perechi de țări cu "
   "<code>pd.qcut</code>: limitele sunt terțilele ratei la mie, deci fiecare grupă are aproximativ o treime din "
   f"perechile de țări. La perechile de regiuni, grupele nu mai sunt egale ({nr(X['n_migr'])} de perechi în total), "
   "pentru că țările mari au multe regiuni. Scara de culori este secvențială: grupele au o ordine.</p>"
   + ix("trepte", "Peste graniță, după migrație", TREPTE_MIGR)
   + "<p>Sub 250 km, vecinii au aproape toți migrație mare, iar unele grupe au doar câteva perechi: o mediană pe "
     "câteva cazuri nu se compară cu una pe mii, deci graficul pornește de la 250 km. Graficul arată o asociere, nu ce o produce: SCI dintre țări cu multă migrație e mare și "
     "pentru că migranții înșiși au prieteni acasă.</p>"
   + "<pre><code>cu_migratie[\"migratia\"] = pd.qcut(cu_migratie[\"la_mie\"], 3, labels=[\"mică\", \"medie\", \"mare\"])\n"
     "granita = perechi.merge(cu_migratie[[\"pereche\", \"migratia\"]], on=\"pereche\")\n"
     "peste_250 = granita[granita[\"distanta_km\"] > 250]\n"
     "sns.pointplot(peste_250, x=\"interval_km\", y=\"sci\", hue=\"migratia\", estimator=\"median\",\n"
     "              errorbar=None, log_scale=True)\n\n"
     "sns.displot(perechi, x=\"distanta_km\", y=\"sci\", col=\"aceeasi_tara\", log_scale=True,\n"
     "            stat=\"percent\", common_norm=False)       # fațete, fiecare în procente din propriile perechi</code></pre>")


# ===========================================================================
#  7-8. Spațiu și rețele
# ===========================================================================

HARTA_AB = {
    "niveluri": ["regiuni"], "nivel": "regiuni", "masura": "dist", "ales": "RO11", "masuri": ["dist", "sci"],
    "povesti": [
        {"t": "Nord-Vest", "nivel": "regiuni", "masura": "dist", "ales": "RO11",
         "text": "La peste 2.000 km, regiuni din Spania (La Rioja, Castilla-La Mancha, Aragón) și Irlanda au legături de "
                 "zeci de ori peste mediana distanței lor: drumurile migrației de muncă."},
        {"t": "Luxemburg", "nivel": "regiuni", "masura": "dist", "ales": "LU00",
         "text": "Toate regiunile Portugaliei, de peste 50 de ori peste mediana distanței; vecinii din Belgia și Țările "
                 "de Jos, sub ea. Una dintre cele mai mari comunități portugheze din afara țării."},
        {"t": "Varșovia", "nivel": "regiuni", "masura": "dist", "ales": "PL91",
         "text": "Islanda, mult peste mediană: emigrația poloneză de după 2004. Svalbard apare din nou sus, ca la "
                 "verificarea extremelor: o regiune aproape nelocuită."},
    ]}

sl("s11", "Spațiu", "Harta abaterilor",
   "<h2>Ce regiuni ies din tipar?</h2>"
   + ix("harta", "SCI raportat la mediana distanței", HARTA_AB)
   + PAS("SCI împărțit la mediana perechilor de la aceeași distanță, pe hartă: scară divergentă",
         "Nord-Vest: Spania și Irlanda, de zeci de ori peste ce ar da distanța",
         "excepțiile se urmăresc în reziduurile modelului. Ce grupuri apar?"),
   manual=
   "<h2>Mai legate decât distanța le-ar da</h2>"
   "<p>După H1, distanța singură explică o mare parte din SCI. Pentru a vedea ce iese din tipar, fiecare pereche "
   "se compară cu perechile aflate la aceeași distanță: SCI-ul ei împărțit la mediana intervalului ei. Peste 1 "
   "înseamnă mai legată decât distanța ar sugera; sub 1, mai puțin. Este o primă formă a reziduului din modelul C7.</p>"
   "<p>Pe o hartă coropletă, scara de culori se alege după date. Pentru mărimi (populația, SCI), o scară "
   "<b>secvențială</b>, de la deschis la închis. Pentru abateri de la o valoare de referință, ca aici, o scară "
   "<b>divergentă</b>: două culori și un mijloc neutru, care înseamnă „cât ar da distanța”.</p>"
   + ix("harta", "SCI raportat la mediana distanței", HARTA_AB)
   + "<pre><code>mediana_intervalului = perechi.groupby(\"interval_km\", observed=True)[\"sci\"].transform(\"median\")\n"
     "perechi[\"fata_de_distanta\"] = perechi[\"sci\"] / mediana_intervalului\n\n"
     "harta.plot(column=\"abatere\", cmap=\"RdBu_r\", vmin=-1, vmax=1, legend=True)   # divergentă, centrată pe 0</code></pre>"
   + "<p>Pe hartă, distanța se măsoară între centrele contururilor desenate, deci valorile diferă puțin de cele din "
     "caiet. Tiparul este același.</p>")



HARTA_COM = {
    "niveluri": ["regiuni"], "nivel": "regiuni", "masura": "com", "ales": "RO11", "masuri": ["com", "sci"],
    "povesti": [
        {"t": "România și Germania", "nivel": "regiuni", "masura": "com", "ales": "RO11",
         "text": "Toate regiunile României sunt în aceeași comunitate cu Germania, nu cu țările vecine: o urmă a "
                 "migrației de muncă."},
        {"t": "Polonia și Irlanda", "nivel": "regiuni", "masura": "com", "ales": "PL91",
         "text": "Polonia, Irlanda, Islanda și Lituania formează o singură comunitate, urmă a emigrației de după 2004."},
        {"t": "Luxemburg și Portugalia", "nivel": "regiuni", "masura": "com", "ales": "LU00",
         "text": "Luxemburgul și regiunile Portugaliei, împreună: aceeași excepție ca pe harta abaterilor."},
    ]}

sl("s13", "Rețele", "Comunitățile",
   "<h2>Ce grupuri apar?</h2>"
   + ix("harta", "Comunitățile SCI, pe regiuni", HARTA_COM)
   + PAS("rețeaua: regiunile sunt noduri, SCI e ponderea legăturii; comunități Louvain, culori categorice",
         "cele mai multe comunități urmează granițele; România e cu Germania",
         "grupurile nu spun de ce; distanța, granița și migrația intră împreună în modelul din C7"),
   manual=
   "<h2>Rețele: noduri, legături, comunități</h2>"
   "<p>Aceleași perechi, privite împreună: fiecare regiune este un nod, fiecare pereche o legătură, iar SCI-ul este "
   "ponderea ei. Rețeaua este completă: fiecare regiune este legată de toate celelalte, iar informația stă în ponderi. O "
   "comunitate este un grup de regiuni mai legate între ele decât cu restul. Algoritmul Louvain caută împărțirea cu "
   "modularitatea cea mai mare, doar din ponderi: nu știe nimic despre țări sau hartă. Pornește dintr-o ordine "
   f"aleatoare a nodurilor, pe care <code>seed=1</code> o fixează: {D['comunitati']} comunități. Altă valoare poate "
   "da o împărțire puțin diferită.</p>"
   + ix("harta", "Comunitățile SCI, pe regiuni", HARTA_COM)
   + "<p>Culorile sunt doar etichete, iar peste opt categorii se deosebesc greu. Cele mai multe comunități urmează granițele; informative sunt excepțiile, care "
     "trec de o graniță, iar ele sunt aceleași ca pe harta abaterilor. Gruparea singură nu spune de ce (migrație, "
     "limbă, istorie): pentru asta trebuie alte date.</p>"
   + "<pre><code>G = nx.from_pandas_edgelist(perechi, \"regiune_1\", \"regiune_2\", edge_attr=\"sci\")\n"
     "grupuri = nx.community.louvain_communities(G, weight=\"sci\", seed=1)\n\n"
     "sns.heatmap(pd.crosstab(harta[\"tara\"], harta[\"comunitate\"]), annot=True, cmap=\"Blues\")   # țări × comunități</code></pre>"
   + "<p>Harta comunităților folosește o scară de culori <b>categorică</b>: culori distincte, fără ordine. Tabelul de "
     "contingență țări × comunități (partea 5) arată aceleași grupuri ca numere: o țară într-o singură coloană "
     "înseamnă o comunitate „națională”.</p>")




PRINCIPII = [
    ("o idee pe grafic", "spusă în titlu"),
    ("valori pe mai multe ordine de mărime", "scara logaritmică, spusă pe axă"),
    ("mărimi", "culori secvențiale"),
    ("abateri de la o referință", "culori divergente, mijlocul neutru"),
    ("grupuri fără ordine", "culori categorice, puține"),
    ("zeci de mii de puncte", "histogramă 2D sau mediane, nu scatter"),
    ("comparații între grupuri", "aceeași axă și scară; numărul de cazuri"),
    ("graficul din raport", "titlu, axe cu unități, sursa datelor"),
]
PRINC_HTML = ('<div class="dc6">' + "".join(f'<div><span>{a}</span><b>{b}</b></div>' for a, b in PRINCIPII) + "</div>")

sl("g1", "Un grafic bun", "Principiile unui grafic bun",
   "<h2>Un grafic bun</h2>"
   + PRINC_HTML
   + "<p class=\"cub__regula\">Graficul de <b>explorare</b> e rapid și pentru sine; graficul de <b>raport</b> e "
     "pentru alții și trebuie să se înțeleagă fără explicații.</p>",
   manual=
   "<h2>Principiile unui grafic bun</h2>"
   "<p>Câteva reguli, comune ghidurilor de vizualizare (Wilke, <i>Fundamentals of Data Visualization</i>, capitolele "
   "despre culoare și despre scările axelor; Healy, <i>Data Visualization</i>). Fiecare a apărut în lecție.</p>"
   + PRINC_HTML
   + "<p>Analiza exploratorie produce zeci de grafice rapide, fără titluri îngrijite. În raportul din C8 ajung "
     "puține, refăcute: un titlu care spune constatarea, axe cu unități, sursa datelor sub grafic.</p>")


# ===========================================================================
#  14-16. Echipa și mai departe
# ===========================================================================

DOVADA = {
    "id": "c6-dovada",
    "sarcina": "Trei rezultate din caiet, rulate pe datele proprii. Ieșirea fiecăruia se lipește în câmpul lui.",
    "indiciu": "Celulele se rulează în caietul 06, în ordine: datele din bază (0), distanța (3.1), economia (3.3), migrația (3.4).",
    "pasi": [
        {"t": "H1: distanța",
         "cmd": "perechi[\"distanta_km\"].corr(perechi[\"sci\"], method=\"spearman\")",
         "gol": "numărul afișat",
         "cauta": r"-0[.,]46\d",
         "ind": "Un singur număr, negativ, în jur de -0,46.",
         "daca_nu": "Corelația trebuie să fie în jur de -0.46. Distanța se calculează din centrele regiunilor (secțiunea 3.1)."},
        {"t": "H3: perechile cu PIB",
         "cmd": "len(economice), len(perechi)",
         "gol": "perechea de numere afișată",
         "cauta": r"37950\D+44253",
         "ind": "Două numere: perechile cu PIB la ambele capete și toate perechile.",
         "daca_nu": "Trebuie să iasă 37950 din 44253. Altfel, tabelul perechilor nu este cel din C4."},
        {"t": "H4: migranții la mie",
         "cmd": "cu_migratie[\"la_mie\"].corr(cu_migratie[\"sci\"], method=\"spearman\")",
         "gol": "numărul afișat",
         "cauta": r"0[.,]67\d",
         "ind": "Un număr pozitiv, în jur de 0,68.",
         "daca_nu": "Corelația cu rata trebuie să fie în jur de 0.68. Populația vine din data/raw/bm.csv, anul 2024."},
    ],
    "explicatie": "Rezultatele sunt cele din caiet: H1 și H4 se văd clar, H3 are semnul opus așteptării.",
}

sl("s14", "Echipa", "Verificarea",
   "<h2>Verificarea analizei</h2>"
   + ix("dovada", "Verificarea analizei", DOVADA),
   manual=
   "<h2>Verificarea analizei</h2>"
   "<p>Trei rezultate din caiet, cu ieșirea de pe calculatorul propriu. Butonul <b>Indiciu</b> arată ce trebuie "
   "să conțină fiecare.</p>"
   + ix("dovada", "Verificarea analizei", DOVADA))


FISA = [
    ("Verificări", "câte rânduri, câte ar trebui să fie; un total față de o sursă externă; ce lipsește și unde"),
    ("O variabilă", "distribuția variabilei principale: histogramă, scara potrivită, extremele citite una câte una"),
    ("Două variabile", "o ipoteză din literatură, cu graficul potrivit tipului celor două variabile"),
    ("Grupuri", "comparația în grupuri comparabile; a treia variabilă, ca culoare sau ca fațete"),
    ("Hartă sau rețea", "ce iese din tipar și o excepție care merită explicată"),
]
FISA_HTML = ('<div class="q6 q6--fisa">' + "".join(
    f'<div><i>{k}</i><b>{q}</b><span>{c}</span></div>' for k, (q, c) in enumerate(FISA, 1)) + "</div>")
FORM = {
    "id": "c6-fisa", "tip": "fisa", "minim": 80,
    "sarcina": "Primul EDA pe datele echipei: o constatare pentru fiecare rând al fișei și o decizie pentru model.",
    "exemplu": "De exemplu: 298 de regiuni, deci 44.253 de perechi; rețelele sociale lipsesc în Germania și Franța; "
               "decizie: Svalbard se exclude, SCI pe scara logaritmică.",
    "multumesc": "Fișa a fost înregistrată."}

sl("s15", "Echipa", "Fișa EDA a echipei",
   "<h2>Fișa EDA a echipei</h2>"
   + FISA_HTML
   + ix("asteptari", "Primul EDA al echipei", FORM),
   manual=
   "<h2>Fișa EDA a echipei</h2>"
   "<p>Pașii lecției, pe datele proiectului. Fiecare grafic are o întrebare și o propoziție de interpretare; fiecare "
   "număr spune pe câte cazuri a fost calculat. Fișa intră în <code>README.md</code>, iar caietul care o produce în <code>notebooks/</code>.</p>"
   + FISA_HTML
   + ix("asteptari", "Primul EDA al echipei", FORM))



DECIZII = [
    ("SCI: asimetrie pozitivă, coadă lungă", "scara logaritmică și mediana"),
    ("Svalbard: numitor foarte mic, valori instabile", "se exclude"),
    ("PIB lipsește în Elveția, Norvegia și Balcanii de vest", f"H3 pe {nr(H3['n'])} de perechi, spus explicit"),
    ("distanța și granița, ambele clare", "două variabile separate"),
    ("migrația contează ca rată", "rata la mie, nu numărul"),
    ("Spania, Irlanda, Portugalia, Ungaria", "excepțiile de urmărit în reziduuri"),
]
FIN_C6 = ('<div class="dc6">'
          + "".join(f'<div><span>{a}</span><b>{b}</b></div>' for a, b in DECIZII)
          + "</div>"
          '<p class="fin3__a"><a class="leg" href="../">Pagina cursului 6</a></p>')

SURSE_C6 = surse("Documentația analizei", [
    ("R for Data Science: Exploratory data analysis", "https://r4ds.hadley.nz/eda.html", "analiza exploratorie ca ciclu: variație, covariație, valori neobișnuite"),
    ("Peng: Exploratory Data Analysis Checklist", "https://bookdown.org/rdpeng/exdata/exploratory-data-analysis-checklist.html", "întrebarea, numărul de rânduri, o sursă externă, extremele"),
    ("Google: Good Data Analysis", "https://developers.google.com/machine-learning/guides/good-data-analysis", "validare, descriere, evaluare; comparații pe grupuri"),
    ("pandas: cut", "https://pandas.pydata.org/docs/reference/api/pandas.cut.html", "împărțirea unei variabile numerice în intervale"),
    ("pandas: corr", "https://pandas.pydata.org/docs/reference/api/pandas.Series.corr.html", "Pearson și Spearman, cu <code>method=</code>"),
    ("seaborn: An introduction", "https://seaborn.pydata.org/tutorial/introduction.html", "un tabel, coloanele de pe axe, <code>hue</code> și <code>col</code>"),
    ("seaborn: Overview of plotting functions", "https://seaborn.pydata.org/tutorial/function_overview.html", "grafice pentru distribuții, relații și variabile categorice"),
    ("Holtz și Healy: From Data to Viz", "https://www.data-to-viz.com/", "graficul ales după tipul și numărul variabilelor"),
    ("Wilke: Fundamentals of Data Visualization", "https://clauswilke.com/dataviz/", "scările axelor, culoarea ca instrument, principiile unui grafic"),
    ("pandas: crosstab", "https://pandas.pydata.org/docs/reference/api/pandas.crosstab.html", "tabelul de contingență, cu <code>normalize=</code>"),
    ("networkx: Louvain", "https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.community.louvain.louvain_communities.html", "<code>louvain_communities</code>, <code>weight</code>, <code>seed</code>"),
])

sl("s16", "Mai departe", "Deciziile pentru model",
   "<h2>Ce duce analiza la cursul 7</h2>" + FIN_C6,
   manual="<h2>Ce duce analiza la cursul 7</h2>"
   "<p>Fiecare constatare se încheie cu o decizie pentru modelul din C7: variabilele, scara, ce se exclude și ce "
   "excepții se urmăresc în reziduuri.</p>" + FIN_C6 + SURSE_C6)


if __name__ == "__main__":
    L.scrie_tot()
