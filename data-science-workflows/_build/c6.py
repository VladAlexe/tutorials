# -*- coding: utf-8 -*-
"""
Lecția 6: Analiza exploratorie.

Un curs despre analiza exploratorie, în ordinea fluxului ei: ce este, profilul
datelor, o variabilă numerică, variabilele categorice, două variabile numerice,
trei sau mai multe variabile, tipar și reziduu, verificarea, tipurile de grafice.
Fiecare concept are o definiție, un grafic interactiv pe datele SCI (js/eda.js)
și rezultatul pe aceste date; manualul adaugă detaliile și pașii din caietul 06.

Cifrele SCI vin din date/c6-eda.json, date/c6-ipoteze.json și date/c6-vizual.json,
calculate din tabelele produse de caietele 04-05 (NUTS 2, centrele GISCO NUTS 2024,
EPSG:3035) și, pentru replicare, din baza_completa.db (NUTS 3), la 11 noiembrie 2026.

Rulare:  python _build/c6.py
"""

import json

from comun import Lectie, ix, verif, tabel, nota, surse, RAD

L = Lectie(6, "c6-analiza-exploratorie", "Analiza exploratorie",
           "Analiza exploratorie, în ordinea fluxului ei: profilul datelor, o variabilă, variabile categorice, "
           "două și mai multe variabile, tipar și reziduu, verificarea. Fiecare concept, interactiv, pe datele SCI.")
sl = L.sl

D = json.loads((RAD / "date" / "c6-ipoteze.json").read_text(encoding="utf-8"))
S = json.loads((RAD / "date" / "c6-eda.json").read_text(encoding="utf-8"))
VZ = json.loads((RAD / "date" / "c6-vizual.json").read_text(encoding="utf-8"))
nr = lambda v: f"{v:,.0f}".replace(",", ".")
ro = lambda v, z=2: f"{v:.{z}f}".replace(".", ",").replace("-", "−")
_NB6 = "06_analiza_exploratorie.ipynb"


def noi(text):
    """Fâșia de sub concept: același concept, pe datele SCI."""
    return f'<p class="noi6"><i>Pe datele noastre</i><span>{text}</span></p>'


def cod(t):
    return f"<pre><code>{t}</code></pre>"


# ===========================================================================
#  A. Ce este analiza exploratorie
# ===========================================================================

CURSUL = tabel(["", "Conținutul", "Rezultatul"], [
    ["C1", "proiectul, mediul de lucru, tipurile de date și JSON", "<code>dsw/</code>, cu <code>.venv</code>"],
    ["C2", "colectarea datelor prin API: Eurostat, Banca Mondială", "<code>data/raw</code>"],
    ["C3", "surse diverse, preprocesare, Git și depozitul echipei", "<code>data/processed</code>, <code>proiect/</code>"],
    ["C4", "curățarea datelor și tabelul regiunilor", "<code>regiuni_nuts2.csv</code>"],
    ["C5", "integrare, baze de date și agregare", "perechile, în <code>dsw.db</code>"],
    ["<b>C6</b>", "<b>azi: analiza exploratorie</b>", "<b>deciziile pentru model</b>"],
    ["C7", "variabile derivate și model", "modelul SCI"],
    ["C8", "raportul și prezentarea proiectului", "raportul echipei"],
])

sl("s1", "Cursul", "Unde suntem",
   "<h2>Unde suntem în curs</h2>"
   "<p class=\"cheie\">Datele sunt curate și în bază. Înainte de model: ce conțin, ce structură au, ce merită verificat.</p>"
   + CURSUL,
   manual=
   "<h2>Analiza exploratorie</h2>"
   "<p>Datele sunt curate (C4) și în baza de date (C5). Înainte de orice model, analiza exploratorie le privește: "
   "ce conțin, cum variază fiecare variabilă, ce variază împreună, ce iese din tipar. Lecția urmează fluxul ei, "
   "concept cu concept. Fiecare concept are o definiție, un grafic interactiv pe datele SCI și pașii corespunzători din caietul lecției.</p>"
   + CURSUL
   + nota("Caietul lecției", f"<code>{_NB6}</code>, în <code>dsw/curs/</code>. Pachete noi: <code>seaborn</code>, "
                             "<code>scipy</code>, toate în <code>requirements.txt</code> (se instalează din nou cu "
                             "<code>pip install -r requirements.txt</code>).", True))


FLUX = (
    '<div class="ed6 ed6--5">'
    '<div><small>1 · profilul datelor</small><b>conținutul, calitatea, lipsurile, extremele</b></div>'
    '<div><small>2 · o variabilă</small><b>locația, variabilitatea, forma</b></div>'
    '<div><small>3 · relațiile</small><b>asocieri, grupuri, multe variabile</b></div>'
    '<div><small>4 · tipar și reziduu</small><b>ce rămâne după tiparul dominant</b></div>'
    '<div class="nou"><small>5 · verificarea</small><b>tipar sau zgomot; replicarea</b></div>'
    '</div>'
    '<p class="ed6__inapoi">fiecare rezultat generează întrebări noi și reia ciclul</p>')

sl("s2", "Analiza exploratorie", "Scopul și fluxul",
   "<h2>Analiza exploratorie: scopul și fluxul</h2>"
   "<p class=\"cheie\">Înțelegerea datelor înainte de modelare. Tukey: analiza exploratorie formulează acuzarea; "
   "analiza confirmatorie, pe alte date, hotărăște condamnarea. Rezultatul nu sunt concluzii, ci decizii și "
   "întrebări mai bune.</p>"
   + FLUX,
   manual=
   "<h2>Analiza exploratorie: scopul și fluxul</h2>"
   "<p>Tukey (1977), care a dat numele metodei, o descrie ca pe o atitudine și o încredere în grafice, nu ca pe o "
   "colecție de tehnici: înainte de a testa o ipoteză, datele trebuie privite, ca să se vadă ce conțin și ce merită "
   "testat. Behrens (1997) rezumă distincția: scopul analizei exploratorii este acuzarea, al celei confirmatorii, "
   "condamnarea. Un tipar găsit explorând este provizoriu: aceleași date nu pot și genera o ipoteză, și o confirma.</p>"
   "<p>Studiile despre cum lucrează analiștii (Wongsuphasawat, Liu și Heer, 2019) găsesc aceeași ordine: întâi "
   "<b>profilul datelor</b> (ce conțin, calitatea, lipsurile, extremele), făcut de toți și întotdeauna; abia apoi "
   "<b>descoperirea</b> (relații, ipoteze). Velleman și Hoaglin (1981) dau ordinea clasică a tehnicilor: o variabilă, "
   "apoi comparația grupurilor, apoi relația x-y, apoi tiparul și reziduurile lui; și patru ingrediente: graficele, "
   "reziduurile, reexprimarea, rezistența. Gelman (2004) adaugă că orice grafic exploratoriu este o comparație cu "
   "un model de referință; de aici, ultima etapă: verificarea.</p>"
   + FLUX
   + nota("Întrebarea ascuțită", "Peng (2019): analiza exploratorie ascute întrebarea. O întrebare vagă („ce "
          "legături au regiunile?”) devine una precisă („la aceeași distanță, granița mai contează?”), iar o întrebare "
          "precisă scoate din date mai multă informație.", True))


# ===========================================================================
#  B. Profilul datelor
# ===========================================================================

E2 = json.loads((RAD / "date" / "c6-eda2.json").read_text(encoding="utf-8"))
_REG = {"regiuni": [r[:2] + [""] + r[3:] for r in E2["regiuni"]], "var_reg": E2["var_reg"]}
_PER = E2["perechi"]
_EXT = {k: E2[k] for k in ["sus", "jos", "sus2", "jos2", "medie_sci", "mediana_sci"]}


# Glosarul: termenul românesc, echivalentul englezesc și o definiție scurtă.
# În pagină, termenul are o linie punctată; caseta se deschide la trecerea mouse-ului sau la atingere.
G = {
    "unitate": ("unitatea de analiză", "unit of analysis", "entitatea descrisă de un rând al tabelului: aici, o pereche de regiuni."),
    "medie": ("media", "mean", "suma valorilor împărțită la numărul lor."),
    "mediana": ("mediana", "median", "valoarea din mijloc după ordonare: jumătate din valori sunt sub ea, jumătate peste."),
    "sd": ("abaterea standard", "standard deviation", "distanța tipică a valorilor față de medie; calculată din pătratele abaterilor, deci foarte sensibilă la valori extreme."),
    "iqr": ("intervalul intercuartilic (IQR)", "interquartile range", "lățimea intervalului care conține jumătatea din mijloc a valorilor: de la prima cuartilă (25%) la a treia (75%)."),
    "robust": ("robustă", "robust, resistant", "o statistică pe care câteva valori extreme nu o modifică mult; mediana și IQR sunt robuste, media și abaterea standard nu."),
    "extrema": ("valoare extremă", "outlier", "o valoare mult mai mare sau mai mică decât celelalte; poate fi un caz real interesant sau o eroare."),
    "rata": ("rată", "rate", "un număr raportat la mărimea populației; SCI raportează prieteniile la numărul de utilizatori."),
    "mcar": ("lipsă complet aleatoare", "missing completely at random, MCAR", "probabilitatea ca valoarea să lipsească nu depinde de nimic."),
    "mar": ("lipsă aleatoare condiționat", "missing at random, MAR", "probabilitatea lipsei depinde de o variabilă cunoscută (aici, țara). Denumirea englezească induce în eroare: lipsa nu este întâmplătoare."),
    "mnar": ("lipsă neîntâmplătoare", "missing not at random, MNAR", "probabilitatea lipsei depinde de valoarea care lipsește (de exemplu, regiunile cele mai bogate nu raportează)."),
    "distributie": ("distribuția", "distribution", "felul în care se repartizează valorile unei variabile: unde se adună, cât de împrăștiate sunt, ce formă au."),
    "hist": ("histograma", "histogram", "bare care numără câte valori cad în fiecare interval (clasă) de valori."),
    "kde": ("densitatea", "kernel density estimate, KDE", "o curbă netedă care estimează forma distribuției; o variantă netezită a histogramei."),
    "ecdf": ("funcția de repartiție empirică (ECDF)", "empirical cumulative distribution function", "pentru fiecare valoare x, proporția observațiilor mai mici sau egale cu x."),
    "box": ("boxplotul", "box plot", "cutia arată jumătatea din mijloc a valorilor (de la 25% la 75%), linia din cutie mediana, mustățile restul valorilor obișnuite."),
    "asim": ("asimetria", "skewness", "măsura dezechilibrului unei distribuții: 0 pentru o distribuție simetrică, pozitivă pentru o coadă lungă spre valorile mari."),
    "log": ("transformarea logaritmică", "log transformation", "fiecare valoare x este înlocuită cu log10 x: 10 devine 1, 1.000 devine 3, 1.000.000 devine 6. Ordinea se păstrează, iar diferențele mari se comprimă."),
    "scara": ("scara transformărilor lui Tukey", "Tukey's ladder of powers", "transformările x, √x, log x, −1/x, ordonate de la slabe la puternice; Tukey numea transformarea re-expression."),
    "conting": ("tabelul de contingență", "contingency table, crosstab", "tabelul care numără cazurile pentru fiecare combinație a categoriilor a două variabile."),
    "pearson": ("corelația Pearson", "Pearson correlation coefficient", "măsoară cât de bine se așază punctele pe o dreaptă; între −1 și 1."),
    "rang": ("rangul", "rank", "poziția unei valori după ordonare: cea mai mică are rangul 1, următoarea 2 etc."),
    "spearman": ("corelația Spearman", "Spearman's rank correlation", "corelația Pearson calculată pe ranguri: măsoară dacă cele două variabile cresc împreună, chiar și pe o curbă."),
    "kendall": ("corelația Kendall", "Kendall's tau", "se iau toate perechile de observații; τ este proporția celor ordonate la fel pe ambele variabile minus proporția celor ordonate invers."),
    "monoton": ("asociere monotonă", "monotonic association", "când una dintre variabile crește, cealaltă crește (sau scade) mereu, nu neapărat după o dreaptă."),
    "supra": ("suprapunerea punctelor", "overplotting", "situația în care punctele unui grafic se acoperă unele pe altele și nu se mai vede unde sunt cele mai multe."),
    "h2d": ("histograma bidimensională", "2D histogram, hexbin", "planul este împărțit în căsuțe, iar fiecare căsuță este colorată după numărul de puncte din ea."),
    "perm": ("permutarea", "permutation", "amestecarea aleatoare a valorilor unei coloane între rânduri; distruge relația cu alte coloane, dar păstrează valorile."),
    "lineup": ("protocolul lineup", "lineup protocol, visual inference", "graficul real este ascuns între grafice cu datele permutate; dacă poate fi recunoscut, tiparul nu este doar întâmplător."),
    "confuzie": ("factorul de confuzie", "confounder", "o a treia variabilă legată atât de grupare, cât și de rezultat, care poate crea sau ascunde o relație. Aici: distanța, pentru efectul graniței."),
    "strat": ("stratificarea", "stratification", "comparația făcută separat în grupuri în care factorul de confuzie este aproximativ constant (aici, intervale de distanță)."),
    "matrcor": ("matricea de corelație", "correlation matrix", "tabelul coeficienților de corelație pentru fiecare pereche de variabile."),
    "pairplot": ("matricea de grafice", "scatterplot matrix, pair plot", "câte un grafic de dispersie pentru fiecare pereche de variabile, cu distribuțiile pe diagonală."),
    "multicol": ("multicoliniaritatea", "multicollinearity", "situația în care predictorii unui model sunt puternic corelați între ei, astfel încât efectul fiecăruia se estimează greu."),
    "reziduu": ("reziduul", "residual", "diferența dintre valoarea observată și valoarea prezisă de model (de dreaptă)."),
    "mcmp": ("metoda celor mai mici pătrate", "least squares", "alege dreapta pentru care suma pătratelor reziduurilor este cea mai mică."),
    "prag": ("pragul de semnificație de 5%", "significance level", "o corelație care depășește pragul ar apărea din întâmplare, fără o relație reală, în cel mult 5% din cazuri."),
    "multiple": ("comparațiile multiple", "multiple comparisons", "testarea multor variabile sau ipoteze; cu cât sunt mai multe, cu atât mai multe rezultate par importante doar din întâmplare."),
}


def gl(k, text=None):
    """Un termen din glosar, cu caseta lui."""
    ro_, en, d = G[k]
    return (f'<span class="gl" tabindex="0">{text or ro_}<span class="gl__def"><b>{ro_[0].upper() + ro_[1:]}</b> '
            f'(engl. <i>{en}</i>): {d}</span></span>')


def concept(t):
    return f'<p class="def6"><b>Conceptul.</b> {t}</p>'


def vede(t):
    return f'<p class="noi6"><i>Pe datele SCI</i><span>{t}</span></p>'


def caiet(sectiune, pasi, incercat=None):
    """Ce se face în caietul 06: pașii, apoi o modificare de încercat."""
    h = (f'<div class="nota nota--sobru"><div class="nota__et">În caiet, secțiunea {sectiune}</div><ol>'
         + "".join(f"<li>{p}</li>" for p in pasi) + "</ol>")
    if incercat:
        h += f"<p><b>De încercat.</b> {incercat}</p>"
    return h + "</div>"


def glosar(*chei):
    """Tabelul termenilor unei secțiuni, cu echivalentul englezesc, în manual."""
    return tabel(["Termenul", "În engleză", "Pe scurt"], [[G[k][0], f"<i>{G[k][1]}</i>", G[k][2]] for k in chei])


_TIP = {"tip": E2["tip"], "n": E2["n"], "same": E2["same"]}

sl("s3", "Profilul datelor", "Unitatea de analiză",
   "<h2>Ce descrie un rând?</h2>"
   + concept(f"{gl('unitate', 'Unitatea de analiză')} este ceea ce descrie un rând al tabelului. Tipurile de variabile "
             "(din C1) decid apoi ce rezumat și ce grafic se potrivesc fiecărei coloane.")
   + ix("edTipuri", "Tabelul perechilor", _TIP)
   + vede(f"Un rând este o <b>pereche de regiuni</b>, nu o regiune: {nr(D['n'])} de perechi formate din 298 de regiuni. "
          "Fiecare regiune apare în 297 de perechi, deci rândurile nu sunt independente unele de altele."),
   manual=
   "<h2>Ce descrie un rând?</h2>"
   "<p>Primul pas al analizei exploratorii este stabilirea <b>unității de analiză</b>: entitatea descrisă de un rând. "
   "Tabelul perechilor are ca unitate perechea de regiuni, cu SCI-ul ei; tabelul regiunilor are ca unitate regiunea. "
   "Aceeași întrebare („cât de conectată este o regiune cu străinătatea?”) se tratează diferit pe cele două tabele: pe "
   "perechi, prin valorile SCI individuale; pe regiuni, printr-un indicator agregat (deschiderea, construită în caiet).</p>"
   "<p>Unitatea de analiză are două consecințe practice. Prima: numărul de rânduri trebuie să corespundă construcției "
   f"tabelului; din 298 de regiuni rezultă 298 × 297 / 2 = {nr(D['n'])} de perechi. A doua: perechile nu sunt "
   "independente, pentru că fiecare regiune apare în 297 dintre ele; o regiune atipică influențează sute de rânduri.</p>"
   "<p>Tipurile de variabile au fost introduse în C1. Pe tabelul perechilor, ele decid rezumatele: un identificator "
   "(<code>regiune_1</code>) nu se rezumă; o variabilă categorică (<code>tara_1</code>) se rezumă prin frecvențe; una "
   "ordinală (<code>interval_km</code>) prin frecvențe în ordinea categoriilor; o variabilă numerică "
   "(<code>distanta_km</code>, <code>sci</code>) prin medie, mediană și histogramă. Un clic pe numele unei coloane arată "
   "tipul și rezumatul ei.</p>"
   + ix("edTipuri", "Tabelul perechilor", _TIP)
   + glosar("unitate")
   + caiet("0 și 1.1", [
       "Celula de pregătire citește <code>regiuni</code>, <code>perechi</code> și <code>tari</code> din <code>data/dsw.db</code>, "
       "apoi calculează <code>distanta_km</code> din centrele regiunilor, <code>interval_km</code> cu <code>pd.cut</code> și "
       "<code>aceeasi_tara</code>. Tot aici se construiește <code>deschidere</code>, folosită mai târziu.",
       "<code>perechi.head()</code> și <code>perechi.dtypes</code>: tipul fiecărei coloane.",
       f"<code>len(perechi), 298 * 297 // 2</code>: cele două numere trebuie să fie egale ({nr(D['n'])}).",
       "Suma populației regiunilor din România, comparată cu o sursă externă (aproximativ 19 milioane): un control al "
       "unităților de măsură."],
       "Același control pentru Ungaria (<code>\"HU\"</code>, aproximativ 9,6 milioane)."))


V_LIPS = verif("c6-v-lips", 1,
               "Rețelele sociale lipsesc în toate regiunile Germaniei și Franței. Ce descrie o medie calculată fără ele?",
               ["Media tuturor regiunilor", "Media regiunilor cu date, fără DE și FR",
                "O medie invalidă", "Media Germaniei și a Franței"],
               "Lipsa depinde de țară (de sursa datelor), nu de întâmplare. Media rămâne corectă pentru regiunile cu "
               "date, dar nu descrie Germania și Franța; rezultatul se raportează cu numărul de regiuni pe care a fost calculat.")

sl("s4", "Profilul datelor", "Valorile lipsă",
   "<h2>Unde lipsesc date și de ce?</h2>"
   + concept(f"O valoare poate lipsi {gl('mcar', 'complet aleator')}, {gl('mar', 'în funcție de o variabilă cunoscută')} "
             f"(aici, țara) sau {gl('mnar', 'în funcție de valoarea însăși')}. De motiv depinde ce descrie un rezultat "
             "calculat pe datele rămase.")
   + ix("edLipsuri", "Valorile lipsă din tabelul regiunilor", _REG)
   + vede("Ordonate după țară, lipsurile formează blocuri: rețelele sociale lipsesc în DE, FR și TR, PIB-ul în CH și "
          "NO. Lipsa depinde de țară, adică de sursa datelor."),
   manual=
   "<h2>Unde lipsesc date și de ce?</h2>"
   "<p>Numărul valorilor lipsă spune puțin; contează unde se află și de ce. Rubin (1976) distinge trei mecanisme:</p>"
   + tabel(["Mecanismul", "Lipsa depinde de", "Rezultatul calculat pe datele rămase"], [
       ["lipsă complet aleatoare", "nimic", "corect, doar mai puțin precis"],
       ["lipsă aleatoare condiționat", "o variabilă cunoscută, de exemplu țara", "corect pentru grupurile cu date; se poate corecta pe grupe"],
       ["lipsă neîntâmplătoare", "chiar valoarea care lipsește", "deplasat, fără posibilitate de corecție din datele rămase"]])
   + "<p>Harta lipsurilor are un rând pe variabilă și o coloană pe regiune. În ordine întâmplătoare, lipsurile par "
     "împrăștiate; ordonate după țară, apar blocuri, semn că lipsa depinde de țară. Ultima cifră din panou arată efectul "
     "păstrării doar a cazurilor complete: eliminarea regiunilor fără o variabilă schimbă și distribuția celorlalte.</p>"
   "<p>Fila „simularea mecanismelor” elimină o parte din valorile PIB-ului în fiecare dintre cele trei feluri și compară "
   "mediana rămasă cu cea adevărată. La eliminarea complet aleatoare, abaterea rămâne mică; la eliminarea pe țări întregi, "
   "depinde de țările pierdute; la eliminarea preferențială a valorilor mari, mediana scade constant, iar datele rămase "
   "nu arată că lipsește ceva.</p>"
   + ix("edLipsuri", "Valorile lipsă din tabelul regiunilor", _REG)
   + "<p>Consecința: o comparație care folosește PIB-ul pierde Elveția și Norvegia, două țări bogate; una care folosește "
     "rețelele sociale pierde Germania, Franța și Turcia. Fiecare rezultat se raportează cu numărul de regiuni sau de "
     "perechi pe care a fost calculat.</p>"
   + glosar("mcar", "mar", "mnar")
   + caiet("1.2", [
       "<code>regiuni.isna().sum()</code>: numărul valorilor lipsă pe coloane.",
       "<code>value_counts()</code> pe țara regiunilor cu valori lipsă, pentru rețelele sociale și pentru PIB.",
       "Pentru fiecare variabilă afectată se notează mecanismul probabil."],
       "Pentru <code>somaj</code>: se compară numărul regiunilor cu valori lipsă din fiecare țară cu numărul total de "
       "regiuni al țării (<code>regiuni[\"tara\"].value_counts()</code>). Lipsesc țări întregi sau regiuni izolate?"),
   dupa=V_LIPS)


sl("s5", "Profilul datelor", "Valorile extreme",
   "<h2>Valorile extreme: fenomen real sau artefact?</h2>"
   + concept(f"Cele mai mari și cele mai mici valori se citesc una câte una. SCI este o {gl('rata')}: la o populație "
             "foarte mică, câteva prietenii în plus sau în minus o duc la oricare dintre capetele clasamentului.")
   + ix("edExtreme", "Cele mai mari și cele mai mici valori SCI", _EXT)
   + vede("Svalbard, cu câteva mii de locuitori, apare la ambele capete. Fără Svalbard, extremele devin plauzibile. "
          "Decizie: Svalbard se exclude din model."),
   manual=
   "<h2>Valorile extreme: fenomen real sau artefact?</h2>"
   "<p>Peng recomandă citirea primelor și ultimelor rânduri înainte de orice grafic. O <b>valoare extremă</b> este fie "
   "cazul cel mai informativ, fie o eroare sau un artefact al felului în care s-a construit indicatorul; distincția se "
   "face caz cu caz.</p>"
   "<p>SCI este o rată: prieteniile dintre două regiuni raportate la numărul de utilizatori. O rată calculată pe un "
   "numitor mic variază mult din întâmplare (Wainer, 2007), deci unitățile foarte mici apar la ambele capete ale oricărui "
   "clasament, fără ca aceasta să reflecte un fenomen real.</p>"
   + ix("edExtreme", "Cele mai mari și cele mai mici valori SCI", _EXT)
   + "<p>Butonul „exclude Svalbard” arată clasamentul fără regiunea problematică. Sus rămân regiuni vecine din aceeași "
     "țară (cele două regiuni ale Sloveniei, Groningen și Drenthe); jos, perechi aflate la mii de kilometri (teritoriile "
     "franceze de peste mări și estul Turciei). Ambele sunt explicabile prin distanță și graniță.</p>"
   + glosar("extrema", "rata")
   + caiet("1.3", [
       "<code>perechi.nlargest(5, \"sci\")</code> și <code>perechi.nsmallest(5, \"sci\")</code>: regiunile care se repetă.",
       "<code>regiuni[regiuni[\"regiune\"] == \"NO0B\"]</code>: populația și denumirea.",
       "Decizia (excluderea) și motivul ei."],
       "Cele două clasamente fără perechile care conțin <code>NO0B</code>."))


# ===========================================================================
#  C. O variabilă numerică
# ===========================================================================

_EX = {"sci": D["esantion"], "sus": E2["sus"]}

V_REZ = verif("c6-v-rez", 2,
              "Se adaugă cele 8 perechi cu cele mai mari valori SCI la 60 de perechi obișnuite. Ce rămâne aproape neschimbat?",
              ["Media", "Abaterea standard", "Mediana", "Toate se schimbă la fel"],
              "Media și abaterea standard folosesc mărimea fiecărei valori, deci o singură valoare foarte mare le mută. "
              "Mediana depinde doar de valoarea din mijloc. De aceea SCI se rezumă cu mediana.")

sl("s6", "O variabilă numerică", "Media și mediana",
   "<h2>Media sau mediana?</h2>"
   + concept(f"{gl('medie', 'Media')} se mută mult când apar câteva valori foarte mari; {gl('mediana')}, valoarea din "
             f"mijloc, aproape deloc. La fel {gl('sd')} față de {gl('iqr', 'IQR')}. Statisticile care rezistă la "
             f"valori extreme se numesc {gl('robust', 'robuste')}.")
   + ix("edRezistenta", "Media și mediana, cu și fără valori foarte mari", _EX)
   + vede(f"Pe toate perechile, media SCI este {nr(S['medie'])}, iar mediana {nr(S['mediana'])}: media e de opt ori "
          "mai mare din cauza câtorva sute de perechi vecine. Rezumatul potrivit este mediana."),
   manual=
   "<h2>Media sau mediana?</h2>"
   "<p>Media folosește mărimea fiecărei valori, deci o singură valoare foarte mare o poate muta oricât. Mediana depinde "
   "doar de ordinea valorilor: este valoarea din mijloc, iar valorile mari pot crește oricât fără să o schimbe. "
   "Aceeași diferență există între cele două măsuri ale împrăștierii: abaterea standard (calculată din pătratele "
   "abaterilor față de medie) și intervalul intercuartilic, IQR (lățimea jumătății din mijloc a valorilor). O statistică "
   "pe care câteva valori extreme nu o modifică mult se numește <b>robustă</b> (Velleman și Hoaglin, 1981).</p>"
   "<p>Graficul folosește 60 de perechi, câte una din 50 de-a lungul distribuției SCI. Glisorul adaugă, una câte una, "
   "cele 8 perechi cu cele mai mari valori: media și abaterea standard cresc mult, mediana și IQR aproape deloc. Punctele "
   "sunt desenate pe o axă logaritmică, pentru a încăpea toate, dar statisticile sunt calculate pe valorile obișnuite.</p>"
   + ix("edRezistenta", "Media și mediana, cu și fără valori foarte mari", _EX)
   + tabel(["SCI, toate perechile", "Valoarea"], [["media", nr(S["medie"])], ["media fără Svalbard", nr(S["medie_fara_svalbard"])],
                                                  ["mediana", nr(S["mediana"])], ["abaterea standard", nr(S["sd"])], ["IQR", nr(S["iqr"])]])
   + "<p>Abaterea standard este de 24 de ori mai mare decât IQR: aproape toată variația SCI vine din câteva sute de "
     "perechi de regiuni vecine. Pentru asemenea variabile, media și abaterea standard descriu coada distribuției, nu "
     "perechea obișnuită. O variantă intermediară este <b>media trunchiată</b>: media după eliminarea a 10% din valori de "
     "la fiecare capăt (pentru SCI, " + nr(S["trunchiata10"]) + ").</p>"
   + glosar("medie", "mediana", "sd", "iqr", "robust")
   + caiet("2.1", [
       "Celula cu statisticile SCI: se compară media cu mediana și abaterea standard cu IQR.",
       "Celula care elimină cele 8 cele mai mari valori: cât se mută media și cât mediana."],
       "Aceleași calcule pentru <code>distanta_km</code>. Media și mediana sunt mai apropiate? De ce?"),
   dupa=V_REZ)


_DIS = {"sci": D["esantion"], "perechi": _PER[:3000], **_REG}

sl("s7", "O variabilă numerică", "Distribuția",
   "<h2>Cum arată distribuția unei variabile?</h2>"
   + concept(f"{gl('distributie', 'Distribuția')} se poate desena în mai multe feluri: {gl('hist')}, {gl('kde')}, "
             f"{gl('ecdf', 'ECDF')}, {gl('box')}, violin. Primele două depind de alegeri (numărul barelor, netezirea); "
             "ECDF nu depinde de nicio alegere.")
   + ix("edDistributie", "Distribuția unei variabile", _DIS)
   + vede("Pe scara logaritmică, SCI are un singur vârf și o coadă spre valorile mari. Vârsta medie a regiunilor are "
          "o coadă spre stânga (regiunile tinere din Turcia), pe care boxplotul nu o arată."),
   manual=
   "<h2>Cum arată distribuția unei variabile?</h2>"
   + tabel(["Graficul", "Arată", "Depinde de"], [
       ["histograma", "câte valori cad în fiecare interval", "numărul și începutul intervalelor"],
       ["densitatea (KDE)", "o curbă netedă a formei", "gradul de netezire"],
       ["ECDF", "proporția valorilor ≤ x; mediana se citește la 0,5", "nimic"],
       ["boxplotul", "mediana, jumătatea din mijloc, valorile extreme", "regula mustăților (1,5 × IQR)"],
       ["violinul cu puncte", "forma și fiecare observație", "gradul de netezire"]])
   + "<p>Aceleași date pot părea diferite după numărul barelor histogramei și locul unde încep (McNamara și Lunzer). "
     "De aceea forma se verifică cu mai multe setări sau pe ECDF. Pe ECDF, pointerul afișează proporția valorilor de sub "
     "prag: la 0,5 se citește mediana, la 0,25 și 0,75 cuartilele. Boxplotul este util pentru comparația multor grupuri, "
     "dar ascunde forma; violinul cu puncte o păstrează.</p>"
   + ix("edDistributie", "Distribuția unei variabile", _DIS)
   + glosar("distributie", "hist", "kde", "ecdf", "box")
   + caiet("2.2", [
       "Celula cu patru grafice ale SCI pe scara logaritmică: histograma cu 8 și cu 40 de bare, ECDF, boxplotul.",
       "Celula cu boxplotul și violinul vârstei medii; regiunile din coada stângă: "
       "<code>regiuni.nsmallest(10, \"varsta_medie\")</code>."],
       "Histograma SCI cu <code>bins=8</code>, <code>20</code>, <code>80</code>. Care ascunde forma și care adaugă zgomot?"))


_REX = {"sci": D["esantion"], **_REG}

sl("s8", "O variabilă numerică", "Transformarea logaritmică",
   "<h2>De ce SCI se citește pe scara logaritmică?</h2>"
   + concept(f"SCI merge de la 1 la peste 4 milioane: pe axa obișnuită, aproape toate valorile stau într-o singură bară. "
             f"{gl('log')} comprimă valorile mari: 10 → 1, 1.000 → 3, 1.000.000 → 6. Ordinea se păstrează, iar "
             f"{gl('asim')} scade spre 0.")
   + ix("edReexprimare", "Valorile inițiale, rădăcina pătrată, logaritmul", _REX)
   + vede("Pe log10, SCI, densitatea și PIB-ul devin aproape simetrice, iar media se apropie de mediană. Populația, cu "
          "asimetrie mai mică, se transformă deja prea mult (coada trece în stânga)."),
   manual=
   "<h2>De ce SCI se citește pe scara logaritmică?</h2>"
   "<p>O variabilă cu <b>asimetrie pozitivă</b> are multe valori mici și câteva foarte mari: coada distribuției se "
   "întinde spre dreapta, iar media este mai mare decât mediana. Pe o asemenea variabilă, histograma pe axa obișnuită "
   "arată o singură bară înaltă, iar graficele de dispersie sunt dominate de câteva puncte.</p>"
   "<p><b>Transformarea</b> înlocuiește fiecare valoare cu o funcție a ei care păstrează ordinea. Cele mai folosite sunt "
   "rădăcina pătrată (√x, mai slabă) și logaritmul (log x, mai puternic). Logaritmul în baza 10 are o citire simplă: "
   "arată, aproximativ, câte cifre are numărul (log10 1.000 = 3), iar o diferență de 1 pe scara log înseamnă un raport "
   "de 10 pe scara inițială. Se alege transformarea cea mai slabă care face distribuția aproape simetrică.</p>"
   "<p>Tukey (1977) a ordonat transformările de la slabe la puternice într-o <b>scară</b> (x, √x, log x, −1/x) și le-a "
   "numit <i>re-expression</i>, reexprimare; în manualele românești, termenul obișnuit este <b>transformarea "
   "variabilelor</b>. Transformarea are trei efecte utile: face distribuțiile simetrice, face împrăștierea comparabilă "
   "între grupuri și îndreaptă relațiile curbe.</p>"
   + ix("edReexprimare", "Valorile inițiale, rădăcina pătrată, logaritmul", _REX)
   + tabel(["Asimetria", "x", "√x", "log x"], [["SCI", "18,9", "6,3", "0,65"], ["PIB pe locuitor", "1,35", "0,63", "0,00"],
                                               ["populația", "3,32", "1,20", "−0,58"], ["densitatea", "5,74", "3,29", "0,37"]])
   + "<p>Vârsta medie are asimetrie negativă (coada spre stânga) și nu se transformă logaritmic. Aceeași logică se "
     "aplică numărului de migranți dintre două țări: ca număr absolut depinde de mărimea țărilor; ca rată la 1.000 de "
     "locuitori devine comparabil cu SCI.</p>"
   + glosar("asim", "log", "scara")
   + caiet("2.3", [
       "Funcția <code>scara()</code> calculează asimetria pentru x, √x, log x și −1/x; tabelul se citește pe coloane.",
       "Corelația Spearman dintre SCI și numărul de migranți, apoi dintre SCI și rata la mie. Rezultatul cu rata intră în "
       "verificarea de la finalul lecției."],
       "<code>scara(perechi[\"distanta_km\"])</code>: ce transformare este suficientă pentru distanță?"))


# ===========================================================================
#  D. Variabile categorice
# ===========================================================================

_K = VZ["contingenta"]
CONT_SCI = {"r": [t.replace("peste 2000", "2000+") for t in _K["intervale"]], "c": ["aceeași țară", "țări diferite"],
            "v": [[a, b] for a, b in zip(_K["da"], _K["nu"])], "er": "distanța, km", "ec": "perechea"}
_P100 = _K["da"][0] / (_K["da"][0] + _K["nu"][0])

sl("s9", "Variabile categorice", "Tabelul de contingență",
   "<h2>Două variabile categorice: tabelul de contingență</h2>"
   + concept(f"{gl('conting', 'Tabelul de contingență')} numără cazurile pentru fiecare combinație. Procentele "
             "<b>pe rând</b> și <b>pe coloană</b> răspund la întrebări diferite; un clic pe o celulă le arată pe amândouă.")
   + ix("edContingenta", "Distanța și apartenența la aceeași țară", {"sci": CONT_SCI})
   + vede(f"Sub 100 km, {_P100:.0%} din perechi sunt în aceeași țară; peste 1.000 km, sub 1%: distanța și granița "
          "merg împreună."),
   manual=
   "<h2>Două variabile categorice: tabelul de contingență</h2>"
   "<p>O variabilă categorică se rezumă prin frecvențe și proporții. Două variabile categorice se rezumă printr-un "
   "tabel de contingență. Procentele pe rând răspund la întrebarea „dintre perechile aflate la 100-250 km, ce proporție "
   "este în aceeași țară?”; procentele pe coloană, la întrebarea inversă: „dintre perechile din aceeași țară, ce proporție "
   "se află la 100-250 km?”. Cele două proporții pot fi foarte diferite; confuzia lor este o eroare frecventă.</p>"
   "<p>Barele stivuite 100% arată procentele pe rând. <b>Mozaicul</b> adaugă, prin lățimea coloanelor, numărul de cazuri "
   "din fiecare interval: intervalele cu puține perechi devin înguste.</p>"
   + ix("edContingenta", "Distanța și apartenența la aceeași țară", {"sci": CONT_SCI})
   + "<p>Legătura puternică dintre distanță și apartenența la aceeași țară are o consecință: o comparație a SCI între "
     "perechile din aceeași țară și cele din țări diferite, făcută pe toate perechile, amestecă efectul graniței cu cel "
     "al distanței. Separarea lor se face în secțiunea 5.</p>"
   + glosar("conting")
   + caiet("3", [
       "<code>pd.crosstab</code> cu numere, apoi cu <code>normalize=\"index\"</code> (procente pe rând).",
       "O propoziție în cuvinte pentru un rând al tabelului procentual."],
       "<code>normalize=\"columns\"</code>: aceeași celulă, citită pe coloană, și propoziția corespunzătoare."))


# ===========================================================================
#  E. Două variabile numerice
# ===========================================================================

_COR = {"perechi": _PER[:300], **_REG}
V_COR = verif("c6-v-cor", 3,
              f"Pe valorile brute, corelația Pearson dintre distanță și SCI este {ro(S['pearson_brut'])}. Ce se poate afirma?",
              ["Relația este slabă", "Nu există relație", "Distanța nu influențează SCI",
               "Pearson e sensibil la extreme; pe log sau cu Spearman, relația e clară"],
              f"Pe log-log, Pearson = {ro(S['pearson_log'])}; Spearman = {ro(S['spearman'])}; Kendall = {ro(S['kendall'])}. "
              "Coeficientul se alege după forma relației, văzută întâi pe grafic.")

sl("s10", "Două variabile numerice", "Corelația",
   "<h2>Trei coeficienți de corelație</h2>"
   + concept(f"{gl('pearson', 'Pearson')}: cât de bine se așază punctele pe o dreaptă. {gl('spearman', 'Spearman')}: "
             f"același calcul, pe {gl('rang', 'ranguri')}, deci măsoară dacă variabilele cresc împreună. "
             f"{gl('kendall', 'Kendall')}: cât de des două observații sunt ordonate la fel pe ambele variabile.")
   + ix("edCorelatie", "Trei coeficienți; punctele se pot trage cu mouse-ul", _COR)
   + vede(f"Distanța și SCI: Pearson {ro(S['pearson_brut'])} pe valorile brute și {ro(S['pearson_log'])} pe log-log; "
          f"Spearman {ro(S['spearman'])} și Kendall {ro(S['kendall'])} pe ambele scări."),
   manual=
   "<h2>Trei coeficienți de corelație</h2>"
   + tabel(["Coeficientul", "Cum se calculează", "Măsoară", "Sensibil la"], [
       ["Pearson r", "covarianța, raportată la produsul abaterilor standard", "relația liniară", "valori extreme, curbură"],
       ["Spearman ρ", "Pearson, calculat pe ranguri", "relația monotonă", "puțin"],
       ["Kendall τ", "(perechi ordonate la fel − perechi ordonate invers) / toate perechile", "relația monotonă", "puțin; valori mai mici decât ρ"]])
   + "<p>Spearman și Kendall folosesc doar ordinea valorilor, deci nu se schimbă la o transformare care păstrează "
     "ordinea, cum este logaritmul; Pearson se schimbă. Kendall are o citire directă: τ = 0,33 înseamnă că, pentru două "
     "observații alese la întâmplare, ordonarea la fel pe ambele variabile este cu 33 de puncte procentuale mai probabilă "
     "decât ordonarea inversă. Niciun coeficient nu detectează o relație în formă de U; de aceea graficul vine înaintea "
     "coeficientului.</p>"
   "<p>În graficul de mai jos punctele pot fi trase cu mouse-ul. Un singur punct mutat departe de nor schimbă mult "
   "coeficientul Pearson și dreapta, dar abia mișcă Spearman și Kendall. Butonul „scară logaritmică” arată același "
   "lucru: doar Pearson se schimbă.</p>"
   + ix("edCorelatie", "Trei coeficienți; punctele se pot trage cu mouse-ul", _COR)
   + glosar("pearson", "rang", "spearman", "kendall", "monoton")
   + caiet("4.1", [
       "Spearman, Pearson pe valorile brute și pe log-log, apoi Kendall, pentru distanță și SCI. Rezultatul Spearman "
       "intră în verificarea de la finalul lecției (aproximativ −0,46).",
       "De ce Pearson pe valorile brute este mult mai mic în valoare absolută?"],
       "Cele trei metode pentru <code>pib_locuitor</code> și <code>densitate</code> în tabelul regiunilor, apoi Pearson "
       "pe <code>np.log10</code> al densității."),
   dupa=V_COR)


sl("s11", "Două variabile numerice", "Prea multe puncte",
   "<h2>Prea multe puncte: cum se vede relația?</h2>"
   + concept(f"La zeci de mii de puncte apare {gl('supra')}: nu se mai vede unde sunt cele mai multe. Soluțiile: "
             f"transparența, {gl('h2d')} și medianele pe intervale.")
   + ix("edMulte", "Distanța și SCI, pe 10.000 de perechi", {"perechi": _PER})
   + vede("Medianele pe intervale arată forma relației: SCI scade repede până la câteva sute de kilometri, apoi mai "
          "încet; pe log-log, scăderea este aproape o dreaptă."),
   manual=
   "<h2>Prea multe puncte: cum se vede relația?</h2>"
   "<p>Cvartetul lui Anscombe (1973) a arătat că seturi de date cu aceeași medie, aceeași varianță și aceeași corelație "
   "pot avea grafice complet diferite: graficul vine înaintea coeficientului. La volume mari apare o altă problemă: "
   "punctele se acoperă, iar o zonă cu mii de observații arată la fel ca una cu zece.</p>"
   + tabel(["Metoda", "Se reglează", "Potrivită pentru"], [
       ["transparența", "opacitatea punctelor", "până la câteva mii de puncte"],
       ["histograma bidimensională", "mărimea căsuțelor", "zeci de mii de puncte"],
       ["medianele pe intervale", "lățimea intervalelor", "forma relației și împrăștierea ei"]])
   + "<p>Cu cât sunt mai multe puncte, cu atât opacitatea trebuie să fie mai mică. Căsuțele prea mici arată zgomot, "
     "cele prea mari ascund forma. Numerele de deasupra medianelor arată câte perechi are fiecare interval.</p>"
   + ix("edMulte", "Distanța și SCI, pe 10.000 de perechi", {"perechi": _PER})
   + glosar("supra", "h2d")
   + caiet("4.2", [
       "<code>sns.histplot</code> cu <code>x</code>, <code>y</code> și <code>log_scale=True</code>: histograma "
       "bidimensională a tuturor perechilor.",
       "<code>groupby(\"interval_km\")</code> cu mediana SCI: forma relației, ca tabel."],
       "<code>sns.scatterplot</code> pe toate perechile, cu <code>alpha=0.02</code>, apoi <code>0.2</code>. Care arată densitatea?"))


sl("s12", "Două variabile numerice", "Lineup",
   "<h2>Tipar real sau întâmplare?</h2>"
   + concept(f"Percepția vizuală găsește tipare și în date fără nicio relație. {gl('lineup', 'Protocolul lineup')} ascunde graficul "
             f"real printre grafice în care valorile au fost amestecate ({gl('perm', 'permutate')}) între regiuni. Dacă "
             "graficul real se recunoaște, tiparul nu este întâmplător.")
   + ix("edLineup", "Graficul real, printre grafice permutate", _REG)
   + vede("PIB-ul și studiile: graficul real se recunoaște imediat. Deschiderea și longitudinea: se recunoaște, mai "
          "greu. Deschiderea și populația: nu se deosebește de permutări."),
   manual=
   "<h2>Tipar real sau întâmplare?</h2>"
   "<p>Percepția vizuală găsește tipare și în date aleatoare. <b>Protocolul lineup</b> (Buja și colegii, 2009) verifică "
   "un grafic prin comparație: valorile unei variabile se amestecă aleator între rânduri, ceea ce distruge orice relație, "
   "dar păstrează valorile. Graficul real se ascunde printre 7 grafice amestecate. Dacă relația nu există, probabilitatea "
   "de a nimeri graficul real este 1 din 8; cu 20 de grafice, 1 din 20, adică pragul obișnuit de 5%.</p>"
   "<p>Fiecare punct este o regiune, desenată după ranguri, ca să nu conteze asimetria variabilelor. <b>Deschiderea</b> "
   "unei regiuni spre străinătate este definită în caiet ca mediana SCI-ului ei cu regiunile din alte țări, fiecare "
   "valoare raportată la mediana tuturor perechilor aflate la aceeași distanță; o valoare de 2 înseamnă legături de două "
   "ori mai puternice decât ar sugera distanța.</p>"
   + ix("edLineup", "Graficul real, printre grafice permutate", _REG)
   + glosar("perm", "lineup")
   + caiet("4.3", [
       "Funcția <code>lineup(x, y)</code> desenează 8 grafice; răspunsul se afișează în celula următoare.",
       "Lineup pentru PIB și studii, apoi pentru longitudine și deschidere; alegerea se notează înainte de a afișa răspunsul."],
       "<code>lineup(cu_desc[\"populatie\"], cu_desc[\"deschidere\"])</code>. Graficul real se poate recunoaște?"))


# ===========================================================================
#  F. Trei sau mai multe variabile
# ===========================================================================

_H2 = D["h2"]
_I = _H2["intervale"].index("250-500")
_R = _H2["da"]["med"][_I] / _H2["nu"]["med"][_I]

sl("s13", "Trei sau mai multe variabile", "Grupuri și factorul de confuzie",
   "<h2>Granița contează sau doar distanța?</h2>"
   + concept(f"Perechile din aceeași țară sunt și mai apropiate, iar apropierea crește SCI-ul. Distanța este un "
             f"{gl('confuzie')} pentru efectul graniței. Soluția este {gl('strat')}: comparația se face separat, pe "
             "intervale de distanță.")
   + ix("edGrupuri", "SCI pe intervale de distanță", {"perechi": _PER[:4000]})
   + vede(f"La aceeași distanță, perechile din aceeași țară au mediana SCI de {_R:.0f} ori mai mare (250-500 km). "
          "Fără intervale, comparația ar atribui graniței și efectul distanței."),
   manual=
   "<h2>Granița contează sau doar distanța?</h2>"
   "<p>O variabilă numerică se compară între grupuri prin distribuții, nu doar prin medii. Bara cu media ascunde "
   "distribuția; pentru SCI, media pe axa obișnuită este dominată de câteva perechi foarte legate. Boxploturile, "
   "violinele și punctele pe scara logaritmică arată mediana, împrăștierea și forma fiecărui grup, iar numărul de cazuri "
   "de sub fiecare grup arată pe ce se bazează comparația.</p>"
   "<p>Un <b>factor de confuzie</b> (engl. <i>confounder</i>) este o a treia variabilă legată atât de gruparea "
   "studiată, cât și de rezultat. Exemplul clasic din epidemiologie: consumul de cafea pare legat de bolile de inimă, "
   "pentru că fumătorii beau mai multă cafea. Aici, perechile din aceeași țară sunt aproape toate apropiate (secțiunea 3), "
   "iar apropierea crește SCI-ul; o comparație pe toate perechile ar atribui graniței și efectul distanței. "
   "<b>Stratificarea</b> compară grupurile separat, în intervale în care distanța este aproximativ aceeași. Alte "
   "diferențe legate de graniță (limba, istoria, instituțiile) rămân însă amestecate cu efectul ei.</p>"
   "<p>Butonul „separat” adaugă apartenența la aceeași țară, prin culoare; butonul „fără intervale” reunește toate "
   "distanțele. Raportul medianelor din panou se compară între cele două situații.</p>"
   + ix("edGrupuri", "SCI pe intervale de distanță", {"perechi": _PER[:4000]})
   + glosar("confuzie", "strat")
   + caiet("5.1", [
       "Bara cu media pe intervale, lângă boxplotul pe scara log, separat după <code>aceeasi_tara</code>.",
       "Tabelul <code>h2</code>: medianele și raportul lor pe intervale."],
       "Raportul medianelor pe toate perechile, fără intervale "
       "(<code>perechi.groupby(\"aceeasi_tara\")[\"sci\"].median()</code>). De ce este mai mare?"))


sl("s14", "Trei sau mai multe variabile", "Multe variabile",
   "<h2>Multe variabile deodată</h2>"
   + concept(f"{gl('pairplot', 'Matricea de grafice')} arată fiecare pereche de variabile; {gl('matrcor', 'matricea de corelație')} "
             f"rezumă fiecare pereche printr-un număr. Variabilele puternic corelate între ele produc "
             f"{gl('multicol')} într-un model.")
   + ix("edMultivar", "Indicatorii regiunilor", _REG)
   + vede("PIB-ul merge cu studiile (ρ = 0,61) și cu densitatea (0,52), invers cu șomajul (−0,45). Într-un model, "
          "efectele lor se separă greu."),
   manual=
   "<h2>Multe variabile deodată</h2>"
   "<p>O a treia variabilă se adaugă unui grafic prin <b>culoare</b> (<code>hue=</code>) sau prin <b>fațete</b>: același "
   "grafic repetat pe grupuri, cu aceleași axe (<code>col=</code>). Pentru mai multe variabile numerice deodată se "
   "folosesc matricea de grafice (<code>pairplot</code>) și matricea de corelație (<code>heatmap</code>), desenată cu o "
   "scară de culori centrată pe 0 și limitată la −1 și 1.</p>"
   "<p>Variabilele puternic corelate între ele spun aproape același lucru. Într-un model de regresie, efectul fiecăreia "
   "se estimează imprecis (multicoliniaritate); de aceea matricea de corelație a predictorilor se examinează înaintea "
   "modelului din C7. Butoanele comută între Spearman și Pearson și între densitatea brută și cea logaritmată: cu "
   "Pearson, transformarea densității schimbă coeficienții; cu Spearman, nu.</p>"
   + ix("edMultivar", "Indicatorii regiunilor", _REG)
   + glosar("pairplot", "matrcor", "multicol")
   + caiet("5.2", [
       "<code>sns.pairplot</code> pe cinci indicatori: perechile cu relație vizibilă și variabilele asimetrice.",
       "<code>sns.heatmap</code> cu matricea Spearman.",
       "<code>len(economice), len(perechi)</code>: perechile cu PIB la ambele capete, rezultat folosit în verificarea finală "
       "(37.950 din 44.253)."],
       "Matricea cu <code>method=\"pearson\"</code>, apoi cu densitatea logaritmată. Care coeficienți se schimbă?"))


# ===========================================================================
#  G. Tipar și reziduu
# ===========================================================================

sl("s15", "Tipar și reziduu", "Tipar și reziduu",
   "<h2>Ce rămâne după distanță?</h2>"
   + concept(f"Distanța explică cea mai mare parte din SCI. Se trage dreapta prin {gl('mcmp')}; {gl('reziduu')} este "
             "distanța fiecărui punct față de dreaptă. În reziduuri apar relațiile mai fine, ascunse de distanță.")
   + ix("edReziduu", "SCI față de distanță", {"perechi": _PER[:1500]})
   + vede("Perechile din aceeași țară (portocaliu) au reziduul median aproape +1 pe scara log10: legături de "
          "aproximativ 10 ori mai puternice decât prezice distanța."),
   manual=
   "<h2>Ce rămâne după distanță?</h2>"
   "<p>Tukey descrie datele ca sumă dintre un tipar și un rest: <i>date = tipar + reziduu</i>. După ce tiparul principal "
   "este găsit, el se scoate cu un model simplu, iar relațiile mai fine se caută în reziduuri. Exemplul din <i>R for Data "
   "Science</i>: diamantele de calitate slabă par mai scumpe, până când se ține seama de mărimea lor. Un grafic al "
   "reziduurilor fără structură înseamnă că tiparul a prins tot; o curbă sau grupuri în reziduuri arată ce lipsește.</p>"
   "<p><b>Metoda celor mai mici pătrate</b> alege dreapta pentru care suma pătratelor reziduurilor este minimă. În "
   "componenta de mai jos, panta și nivelul se ajustează de mână; panoul arată suma pătratelor și cât de departe este de "
   "minim. Butonul „reziduurile, ca segmente” desenează distanța verticală dintre puncte și dreaptă, adică exact mărimea "
   "minimizată.</p>"
   + ix("edReziduu", "SCI față de distanță", {"perechi": _PER[:1500]})
   + "<p>Reziduurile unei singure regiuni, pe hartă, arată cu ce regiuni este mai legată decât ar prezice distanța: "
     "pentru Nord-Vest, Spania și Irlanda, unde migrația este mare. Modelul din C7 extinde aceeași logică la mai mulți "
     "predictori.</p>"
   + glosar("reziduu", "mcmp")
   + caiet("6", [
       "<code>np.polyfit</code> pe log10 al distanței și al SCI: panta și nivelul dreptei.",
       "Reziduul fiecărei perechi și mediana lui după <code>aceeasi_tara</code>.",
       "Graficul în două panouri: dreapta peste date și reziduurile față de distanță.",
       "Harta reziduurilor pentru <code>REGIUNE = \"RO11\"</code>: roșu, legături mai puternice decât prezice distanța; "
       "albastru, mai slabe."],
       "Harta pentru altă regiune, de exemplu <code>\"LU00\"</code> sau regiunea echipei. Ce regiuni ies în evidență?"))


# ===========================================================================
#  H. Verificarea
# ===========================================================================

V_POT = verif("c6-v-pot", 1,
              "Dintre 40 de variabile formate din numere aleatoare, două trec pragul de 5%. Ce înseamnă?",
              ["Cele două explică deschiderea", "Nimic: din 40 de încercări, cam 2 trec pragul din întâmplare",
               "Eșantionul e prea mic", "Trebuie Pearson"],
              "La pragul de 5%, din 40 de variabile fără nicio legătură reală, în medie 2 par legate de rezultat. Ce se "
              "găsește explorând se verifică pe alte date.")

sl("s16", "Verificarea", "Multe încercări",
   "<h2>Multe încercări, rezultate întâmplătoare</h2>"
   + concept(f"Variabilele din grafic sunt numere aleatoare, fără nicio legătură cu deschiderea regiunilor. Totuși, la "
             f"{gl('prag')}, cam 1 din 20 trece pragul. Cu cât se încearcă mai multe variabile, cu atât apar mai multe "
             f"rezultate false: problema {gl('multiple', 'comparațiilor multiple')}.")
   + ix("edPoteci", "Indicatorii reali și cele mai mari 6 corelații ale variabilelor aleatoare", _REG)
   + vede("PIB-ul, studiile și densitatea depășesc clar orice variabilă aleatoare; vârsta medie (0,11) nu. "
          "Constatările din această lecție rămân ipoteze, de verificat în C7 și pe alte date."),
   manual=
   "<h2>Multe încercări, rezultate întâmplătoare</h2>"
   "<p>O analiză exploratorie încearcă multe variabile, subgrupuri și transformări. Fiecare încercare are o șansă mică "
   "de a produce un rezultat aparent doar din întâmplare; la pragul obișnuit de 5%, una din 20. Cu 40 de încercări, "
   "probabilitatea ca cel puțin una să treacă pragul fără nicio relație reală este 1 − 0,95<sup>40</sup> ≈ 87%. Gelman "
   "și Loken numesc situația <i>garden of forking paths</i>, „grădina potecilor care se bifurcă”: fiecare alegere a "
   "analistului este o potecă, iar dintre multe poteci, cea mai interesantă pare mai importantă decât este.</p>"
   "<p>În componenta de mai jos, glisorul adaugă variabile formate din numere aleatoare. Graficul arată corelația "
   "fiecăreia cu deschiderea regiunilor, lângă indicatorii reali; linia punctată este pragul de 5% (|ρ| ≈ 0,11 la 290 de "
   "regiuni). Variabilele aleatoare care trec pragul sunt rezultate false.</p>"
   + ix("edPoteci", "Indicatorii reali și cele mai mari 6 corelații ale variabilelor aleatoare", _REG)
   + "<p>Hullman și Gelman (2021) recomandă ca ce se găsește explorând să fie verificat pe date păstrate deoparte: alt "
     "an, alt nivel de agregare (de exemplu NUTS 3), altă sursă.</p>"
   + glosar("prag", "multiple")
   + caiet("7", [
       "Celula generează 40 de variabile aleatoare și calculează corelația fiecăreia cu deschiderea, lângă indicatorii reali.",
       "Cea mai mare corelație întâmplătoare, comparată cu corelațiile indicatorilor reali."],
       "Celula rulată de mai multe ori cu <code>rng = np.random.default_rng()</code> și cu 100 de variabile în loc de 40."),
   dupa=V_POT)


# ===========================================================================
#  I. Încheierea
# ===========================================================================

sl("s17", "Încheierea", "Tipurile de grafice",
   "<h2>Ce grafic, pentru ce date</h2>"
   + ix("edTipGrafice", "Tipurile de grafice, după Wilke", {})
   + "<p class=\"cub__regula\">Un grafic de raport: o idee, formulată în titlu; scara spusă pe axă; culoarea după date "
     "(secvențială, divergentă, categorică); grupurile pe aceeași axă, cu numărul de cazuri; sursa sub grafic.</p>",
   manual=
   "<h2>Tipurile de grafice și un grafic bun</h2>"
   "<p>Wilke (2019) organizează graficele după ce arată: cantități, distribuții, proporții, relații x-y, date "
   "spațiale, incertitudine. Pentru fiecare, câteva grafice standard, cu funcția din <code>seaborn</code>.</p>"
   + ix("edTipGrafice", "Tipurile de grafice, după Wilke", {})
   + "<p>Câteva reguli comune ghidurilor: o idee pe grafic, spusă în titlu; scara logaritmică spusă pe axă; culoarea "
     "după date (secvențială pentru mărimi, divergentă pentru abateri, categorică pentru câteva grupuri); grupurile "
     "comparate pe aceeași axă; numărul de cazuri spus, mai ales la grupurile mici; graficul de raport cu axe cu "
     "unități și sursa datelor.</p>")


PE_SCI = [
    ("Profilul", "un rând = o pereche; Svalbard la ambele capete (numitor mic); lipsurile pe țări întregi"),
    ("O variabilă", "asimetrie puternică: media de 8 ori mai mare decât mediana; scara log10 și mediana"),
    ("Relațiile", f"distanța: Spearman {ro(S['spearman'])}; granița, comparată la aceeași distanță; indicatorii "
                  "economici, puternic corelați între ei"),
    ("Tipar și reziduu", "după distanță rămân granița și coridoarele migrației"),
    ("Verificarea", "constatările rămân ipoteze, de verificat în C7 și pe alte date"),
]
DECIZII = [
    ("SCI: asimetrie pozitivă", "scara logaritmică și mediana"),
    ("Svalbard: numitor foarte mic", "se exclude"),
    ("lipsurile pe țări", "pe câte perechi, spus la fiecare rezultat"),
    ("distanța și granița, legate", "două variabile separate în model"),
    ("migrația contează ca rată", "rata la mie, nu numărul"),
    ("excepțiile: Spania, Irlanda, Moldova", "de urmărit în reziduurile modelului"),
]
PE_SCI_HTML = ('<div class="q6 q6--h q6--sci">' + "".join(f'<div><i>{k}</i><b>{a}</b><span>{b}</span></div>'
                                                          for k, (a, b) in enumerate(PE_SCI, 1)) + "</div>")
FIN_C6 = ('<div class="dc6">' + "".join(f'<div><span>{a}</span><b>{b}</b></div>' for a, b in DECIZII) + "</div>")

sl("s18", "Pe datele noastre", "Fluxul pe SCI",
   "<h2>Fluxul, pe datele noastre, și deciziile pentru C7</h2>"
   + PE_SCI_HTML + FIN_C6,
   manual=
   "<h2>Fluxul, pe datele noastre</h2>"
   "<p>Aceleași etape, pe perechile de regiuni. Fiecare constatare se încheie cu o decizie pentru modelul din C7.</p>"
   + PE_SCI_HTML + FIN_C6)


DOVADA = {
    "id": "c6-dovada",
    "sarcina": "Trei rezultate din caiet, rulate pe datele proprii. Ieșirea fiecăruia se lipește în câmpul lui.",
    "indiciu": "Celulele se rulează în partea „Pe datele noastre” a caietului 06.",
    "pasi": [
        {"t": "Distanța și SCI",
         "cmd": "perechi[\"distanta_km\"].corr(perechi[\"sci\"], method=\"spearman\")",
         "gol": "numărul afișat",
         "cauta": r"-0[.,]46\d",
         "ind": "Un singur număr, negativ, în jur de -0,46.",
         "daca_nu": "Corelația trebuie să fie în jur de -0.46. Distanța se calculează din centrele regiunilor."},
        {"t": "Perechile cu PIB",
         "cmd": "len(economice), len(perechi)",
         "gol": "perechea de numere afișată",
         "cauta": r"37950\D+44253",
         "ind": "Două numere: perechile cu PIB la ambele capete și toate perechile.",
         "daca_nu": "Trebuie să iasă 37950 din 44253. Altfel, tabelul perechilor nu este cel din C4."},
        {"t": "Migranții la mie",
         "cmd": "cu_migratie[\"la_mie\"].corr(cu_migratie[\"sci\"], method=\"spearman\")",
         "gol": "numărul afișat",
         "cauta": r"0[.,]67\d",
         "ind": "Un număr pozitiv, în jur de 0,68.",
         "daca_nu": "Corelația cu rata trebuie să fie în jur de 0.68. Populația vine din data/raw/bm.csv, anul 2024."},
    ],
    "explicatie": "Rezultatele sunt cele din caiet.",
}

SURSE_C6 = surse("Documentația analizei", [
    ("Wongsuphasawat, Liu și Heer (2019): Goals, process, and challenges of EDA", "https://ar5iv.arxiv.org/html/1911.00568", "cum lucrează analiștii: profilul datelor, apoi descoperirea"),
    ("Velleman și Hoaglin (1981): Applications, Basics, and Computing of EDA", "https://ecommons.cornell.edu/bitstream/handle/1813/78/A-B-C_of_EDA_040127.pdf", "ordinea tehnicilor; grafice, reziduuri, reexprimare, rezistență"),
    ("Behrens (1997): Principles and procedures of EDA", "https://pengdsci.github.io/STA551/w04/w04-PrinciplesProceduresEDA-paper.pdf", "Tukey pentru științele sociale; acuzarea și condamnarea"),
    ("Gelman (2004): Exploratory data analysis for complex models", "https://www.cs.princeton.edu/courses/archive/fall09/cos597A/papers/Gelman2004.pdf", "graficul ca comparație cu un model de referință"),
    ("Hullman și Gelman (2021): Theories of graphical inference", "https://mucollective.northwestern.edu/files/2021-hdsr-paper.pdf", "riscurile explorării interactive; date păstrate deoparte"),
    ("Buja și colegii (2009): Statistical inference for EDA", "https://friendly.github.io/6135/papers/Buja-etal-2009.pdf", "protocolul lineup"),
    ("Wainer (2007): The most dangerous equation", "https://sites.stat.washington.edu/people/peter/498.Sp16/Equation.pdf", "numerele mici la ambele capete"),
    ("Bruce, Bruce și Gedeck: Practical Statistics for Data Scientists, cap. 1", "https://oreilly.com/library/view/practical-statistics-for/9781491952955/ch01.html", "locația, variabilitatea, distribuția, corelația"),
    ("Wilke: Fundamentals of Data Visualization, directorul de grafice", "https://clauswilke.com/dataviz/directory-of-visualizations.html", "tipurile de grafice"),
    ("Matejka și Fitzmaurice (2017): Same Stats, Different Graphs", "https://www.research.autodesk.com/publications/same-stats-different-graphs/", "aceleași statistici, alte grafice"),
    ("R for Data Science: Exploratory data analysis", "https://r4ds.hadley.nz/eda.html", "variația, covariația, valorile neobișnuite"),
    ("Peng: Exploratory Data Analysis Checklist", "https://bookdown.org/rdpeng/exdata/exploratory-data-analysis-checklist.html", "verificările de dinainte de grafice"),
    ("seaborn: Overview of plotting functions", "https://seaborn.pydata.org/tutorial/function_overview.html", "funcțiile pentru distribuții, relații, categorii"),
])

sl("s19", "Echipa", "Verificarea în caiet",
   "<h2>Verificarea analizei</h2>"
   + ix("dovada", "Verificarea analizei", DOVADA),
   manual=
   "<h2>Verificarea analizei</h2>"
   "<p>Trei rezultate din caiet, cu ieșirea de pe calculatorul propriu. Butonul <b>Indiciu</b> arată ce trebuie "
   "să conțină fiecare.</p>"
   + ix("dovada", "Verificarea analizei", DOVADA)
   + SURSE_C6)


if __name__ == "__main__":
    L.scrie_tot()
