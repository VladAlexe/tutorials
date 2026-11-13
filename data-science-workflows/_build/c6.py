# -*- coding: utf-8 -*-
"""
Lecția 6: Analiza exploratorie.

Un curs despre analiza exploratorie, în ordinea fluxului ei: ce este, profilul
datelor, o variabilă numerică, variabilele categorice, două variabile numerice,
granița și distanța, partenerii pe hartă, rețeaua și comunitățile, verificarea, tipurile de grafice.
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
           "relațiile, harta partenerilor și comunitățile rețelei, verificarea. Fiecare concept, interactiv, pe datele SCI.")
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
    '<div class="ed6 ed6--4">'
    '<div><small>1 · profilul datelor</small><b>conținutul, calitatea, lipsurile, extremele</b></div>'
    '<div><small>2 · o variabilă</small><b>locația, variabilitatea, forma</b></div>'
    '<div><small>3 · relațiile</small><b>asocieri, granița, hartă și rețea</b></div>'
    '<div class="nou"><small>4 · verificarea</small><b>tipar real sau întâmplare</b></div>'
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
   "apoi comparația grupurilor, apoi relația x-y, apoi tiparul și reziduurile lui. Tiparul și reziduurile se fac în C7, "
   "cu modelul. Gelman (2004) adaugă că orice grafic exploratoriu este o comparație cu ce ar produce întâmplarea; de "
   "aici, ultima etapă a lecției: verificarea.</p>"
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
_REGN = {"regiuni": E2["regiuni"], "var_reg": E2["var_reg"]}      # cu denumirile regiunilor
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
    "cramer": ("V al lui Cramér", "Cramér's V", "intensitatea legăturii dintre două variabile categorice, de la 0 (nicio legătură) la 1 (legătură perfectă); peste 0,5, puternică."),
    "chi2": ("testul χ² (hi-pătrat)", "chi-squared test", "compară tabelul de contingență cu cel așteptat dacă variabilele n-ar fi legate; dă valoarea p a legăturii."),
    "pearson": ("corelația Pearson", "Pearson correlation coefficient", "măsoară cât de bine se așază punctele pe o dreaptă; între −1 și 1."),
    "rang": ("rangul", "rank", "poziția unei valori după ordonare: cea mai mică are rangul 1, următoarea 2 etc."),
    "spearman": ("corelația Spearman", "Spearman's rank correlation", "corelația Pearson calculată pe ranguri: măsoară dacă cele două variabile cresc împreună, chiar și pe o curbă."),
    "kendall": ("corelația Kendall", "Kendall's tau", "se iau toate perechile de observații; τ este proporția celor ordonate la fel pe ambele variabile minus proporția celor ordonate invers."),
    "monoton": ("asociere monotonă", "monotonic association", "când una dintre variabile crește, cealaltă crește (sau scade) mereu, nu neapărat după o dreaptă."),
    "supra": ("suprapunerea punctelor", "overplotting", "situația în care punctele unui grafic se acoperă unele pe altele și nu se mai vede unde sunt cele mai multe."),
    "perm": ("permutarea", "permutation", "amestecarea aleatoare a valorilor unei coloane între rânduri; distruge relația cu alte coloane, dar păstrează valorile."),
    "lineup": ("protocolul lineup", "lineup protocol, visual inference", "graficul real este ascuns între grafice cu datele permutate; dacă poate fi recunoscut, tiparul nu este doar întâmplător."),
    "confuzie": ("factorul de confuzie", "confounder", "o a treia variabilă legată atât de grupare, cât și de rezultat, care poate crea sau ascunde o relație. Aici: distanța, pentru efectul graniței."),
    "strat": ("stratificarea", "stratification", "comparația făcută separat în grupuri în care factorul de confuzie este aproximativ constant (aici, intervale de distanță)."),
    "reziduu": ("reziduul", "residual", "diferența dintre valoarea observată și valoarea prezisă de model (de dreaptă)."),
    "mcmp": ("metoda celor mai mici pătrate", "least squares", "alege dreapta pentru care suma pătratelor reziduurilor este cea mai mică."),
    "prag": ("pragul de semnificație de 5%", "significance level", "o corelație care depășește pragul ar apărea din întâmplare, fără o relație reală, în cel mult 5% din cazuri."),
    "permtest": ("testul de permutare", "permutation test", "se amestecă datele de multe ori; dacă relația reală e mai puternică decât aproape toate relațiile din amestecări, nu e întâmplătoare."),
    "pval": ("valoarea p", "p-value", "proporția amestecărilor (sau a eșantioanelor ipotetice) cu un rezultat cel puțin la fel de mare ca cel real; sub 0,05, rezultatul se consideră real."),
    "retea": ("rețeaua", "network", "noduri (aici, regiuni) legate prin legături (aici, perechi), fiecare cu o greutate (aici, SCI)."),
    "comunitate": ("comunitatea", "community", "un grup de noduri mai legate între ele decât cu restul rețelei."),
    "louvain": ("algoritmul Louvain", "Louvain method", "caută comunitățile mutând nodurile dintre grupuri cât timp grupurile devin mai închise (modularitate mai mare); folosește doar greutățile legăturilor."),
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
       "Celula de pregătire citește <code>regiuni</code>, <code>perechi</code> și <code>tari</code> din baza de date <code>dsw.db</code>, descărcată din depozitul cursului (GitHub), "
       "apoi calculează <code>distanta_km</code> din centrele regiunilor, <code>interval_km</code> cu <code>pd.cut</code> și "
       "<code>aceeasi_tara</code>.",
       "<code>perechi.head()</code> și <code>perechi.dtypes</code>: tipul fiecărei coloane.",
       f"<code>len(perechi), 298 * 297 // 2</code>: cele două numere trebuie să fie egale ({nr(D['n'])}).",
       "Suma populației regiunilor din România, comparată cu o sursă externă (aproximativ 19 milioane): un control al "
       "unităților de măsură."],
       "Același control pentru Ungaria (<code>\"HU\"</code>, aproximativ 9,6 milioane)."))


V_LIPS = verif("c6-v-lips", 1,
               "PIB-ul pe locuitor lipsește în toate regiunile Elveției și Norvegiei. Ce descrie o mediană calculată fără ele?",
               ["Mediana tuturor regiunilor", "Mediana regiunilor cu date, fără CH și NO",
                "O mediană invalidă", "Mediana Elveției și a Norvegiei"],
               "Lipsa depinde de țară (de sursa datelor), nu de întâmplare. Mediana rămâne corectă pentru regiunile cu "
               "date, dar nu descrie Elveția și Norvegia, două țări bogate; rezultatul se raportează cu numărul de "
               "regiuni pe care a fost calculat.")

sl("s4", "Profilul datelor", "Valorile lipsă",
   "<h2>Unde lipsesc date și de ce?</h2>"
   + concept(f"O valoare poate lipsi {gl('mcar', 'complet aleator')}, {gl('mar', 'în funcție de o variabilă cunoscută')} "
             f"(aici, țara) sau {gl('mnar', 'în funcție de valoarea însăși')}. De motiv depinde ce descrie un rezultat "
             "calculat pe datele rămase.")
   + ix("edLipsuri", "Valorile lipsă din tabelul regiunilor", _REG)
   + vede("Ordonate după țară, PIB-ul lipsește în blocuri: toată Elveția, toată Norvegia, Islanda și Balcanii de Vest. "
          "Șomajul lipsește doar în regiuni izolate. Lipsa PIB-ului depinde de țară, adică de sursa datelor."),
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
   + "<p>Două tipare se văd pe hartă. PIB-ul lipsește pe țări întregi (Elveția, Norvegia, Islanda, Albania, Bosnia și "
     "Herțegovina, Kosovo): lipsa depinde de țară. Șomajul lipsește în câteva regiuni izolate (una în Germania, una în "
     "Polonia, una în Finlanda), mai aproape de o lipsă întâmplătoare. Consecința pentru PIB: o comparație care îl "
     "folosește pierde două țări bogate, iar mediana europeană iese ușor subestimată. Fiecare rezultat se raportează cu "
     "numărul de regiuni sau de perechi pe care a fost calculat.</p>"
   + glosar("mcar", "mar", "mnar")
   + caiet("1.2", [
       "<code>regiuni.isna().sum()</code>: numărul valorilor lipsă pe coloane.",
       "<code>value_counts()</code> pe țara regiunilor fără PIB: lipsesc țări întregi.",
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
   + tabel(["Graficul", "Arată", "Depinde de", "Se folosește când"], [
       ["histograma", "câte valori cad în fiecare interval", "numărul și începutul intervalelor", "prima privire asupra formei unei variabile"],
       ["densitatea (KDE)", "o curbă netedă a formei", "gradul de netezire", "se suprapun câteva grupuri pe același grafic"],
       ["ECDF", "proporția valorilor ≤ x; mediana se citește la 0,5", "nimic", "contează proporții și praguri („ce parte din perechi are SCI sub 1.000?”) sau se compară grupuri fără alegeri arbitrare"],
       ["boxplotul", "mediana, jumătatea din mijloc, valorile extreme", "regula mustăților (1,5 × IQR)", "se compară multe grupuri deodată"],
       ["violinul cu puncte", "forma și fiecare observație", "gradul de netezire", "se compară puține grupuri și forma contează"]])
   + "<p>Aceleași date pot părea diferite după numărul barelor histogramei și locul unde încep (McNamara și Lunzer). "
     "De aceea forma se verifică cu mai multe setări sau pe ECDF. Pe ECDF, pointerul afișează proporția valorilor de sub "
     "prag: la 0,5 se citește mediana, la 0,25 și 0,75 cuartilele. Boxplotul este util pentru comparația multor grupuri, "
     "dar ascunde forma; violinul cu puncte o păstrează.</p>"
   + ix("edDistributie", "Distribuția unei variabile", _DIS)
   + "<h3>Codul, pe scurt</h3><p>Sub graficul interactiv apare codul vederii alese. Toate variantele, la un loc:</p>"
   + cod("import seaborn as sns\n\n"
         "# histograma: bins = numărul barelor; log_scale=True pune axa x pe scară logaritmică\n"
         "sns.histplot(perechi, x=\"sci\", log_scale=True, bins=20)\n\n"
         "# densitatea: bw_adjust mai mic = curbă mai puțin netezită\n"
         "sns.kdeplot(perechi, x=\"sci\", log_scale=True, bw_adjust=0.5)\n\n"
         "# ECDF: pentru fiecare valoare x, proporția perechilor cu SCI ≤ x\n"
         "sns.ecdfplot(perechi, x=\"sci\", log_scale=True)\n"
         "(perechi[\"sci\"] &lt;= 1000).mean()          # aceeași idee, ca număr: proporția sub 1.000\n\n"
         "# boxplotul și violinul, pentru vârsta medie a regiunilor\n"
         "sns.boxplot(regiuni, x=\"varsta_medie\")\n"
         "sns.violinplot(regiuni, x=\"varsta_medie\", inner=\"point\")   # inner=\"point\": și observațiile")
   + glosar("distributie", "hist", "kde", "ecdf", "box")
   + caiet("2.2", [
       "Câte o celulă pentru fiecare grafic al SCI pe scara logaritmică: histograma și ECDF; apoi proporția perechilor "
       "cu SCI sub 1.000, calculată direct.",
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
   + "<h3>Codul, pe scurt</h3>"
   + cod("import numpy as np\n\n"
         "perechi[\"sci\"].skew()                     # asimetria valorilor inițiale\n"
         "np.sqrt(perechi[\"sci\"]).skew()            # după rădăcina pătrată\n"
         "np.log10(perechi[\"sci\"]).skew()           # după logaritm\n\n"
         "sns.histplot(perechi, x=\"sci\", log_scale=True)   # histograma direct pe axa logaritmică")
   + tabel(["Asimetria", "x", "√x", "log x"], [["SCI", "18,9", "6,3", "0,65"], ["PIB pe locuitor", "1,35", "0,63", "0,00"],
                                               ["populația", "3,32", "1,20", "−0,58"], ["densitatea", "5,74", "3,29", "0,37"]])
   + "<p>Vârsta medie are asimetrie negativă (coada spre stânga) și nu se transformă logaritmic. Aceeași logică se "
     "aplică numărului de migranți dintre două țări: ca număr absolut depinde de mărimea țărilor; ca rată la 1.000 de "
     "locuitori devine comparabil cu SCI.</p>"
   + glosar("asim", "log", "scara")
   + caiet("2.3", [
       "Asimetria SCI pentru x, √x și log x, apoi histograma lui log10(SCI).",
       "Corelația Spearman dintre SCI și numărul de migranți, apoi dintre SCI și rata la mie. Rezultatul cu rata intră în "
       "verificarea de la finalul lecției."],
       "Aceleași trei asimetrii pentru <code>perechi[\"distanta_km\"]</code> și <code>regiuni[\"densitate\"]</code>: ce "
       "transformare este suficientă?"))


# ===========================================================================
#  D. Variabile categorice
# ===========================================================================

_K = VZ["contingenta"]
CONT_SCI = {"r": [t.replace("peste 2000", "2000+") for t in _K["intervale"]], "c": ["aceeași țară", "țări diferite"],
            "v": [[a, b] for a, b in zip(_K["da"], _K["nu"])], "er": "distanța, km", "ec": "perechea"}
_P100 = _K["da"][0] / (_K["da"][0] + _K["nu"][0])

sl("s9", "Variabile categorice", "Tabelul de contingență",
   "<h2>Două variabile categorice: tabelul de contingență</h2>"
   + concept(f"{gl('conting', 'Tabelul de contingență')} numără perechile pentru fiecare combinație de distanță și "
             "țară. Un procent <b>pe rând</b> împarte celula la totalul rândului, unul <b>pe coloană</b> la totalul "
             "coloanei. Un clic pe o celulă arată ambele calcule.")
   + ix("edContingenta", "Distanța și apartenența la aceeași țară", {"sci": CONT_SCI})
   + vede(f"Sub 100 km, {_P100:.0%} din perechi sunt în aceeași țară; peste 1.000 km, sub 1%. "
          f"{gl('cramer', 'V Cramér')} = 0,48: legătură puternică."),
   manual=
   "<h2>Două variabile categorice: tabelul de contingență</h2>"
   "<p>O variabilă categorică se rezumă prin frecvențe și proporții. Două variabile categorice se rezumă printr-un "
   "tabel de contingență. Procentele pe rând răspund la întrebarea „dintre perechile aflate la 100-250 km, ce proporție "
   "este în aceeași țară?”; procentele pe coloană, la întrebarea inversă: „dintre perechile din aceeași țară, ce proporție "
   "se află la 100-250 km?”. Cele două proporții pot fi foarte diferite; confuzia lor este o eroare frecventă.</p>"
   "<p>Exemplul calculului, pe celula „0-100 km și aceeași țară”, cu 168 de perechi. Pe rând: 168 ÷ 223 (toate perechile "
   "aflate la 0-100 km) = 75,3%, adică trei sferturi din perechile foarte apropiate sunt în aceeași țară. Pe coloană: "
   "168 ÷ 2.379 (toate perechile din aceeași țară) = 7,1%, adică doar 7% din perechile din aceeași țară sunt la sub "
   "100 km. Aceeași celulă, două întrebări, două răspunsuri foarte diferite.</p>"
   + tabel(["Graficul", "Ce arată", "Când se folosește"], [
       ["matricea colorată (<code>sns.heatmap</code>)", "tabelul însuși, cu culoarea după valoare", "tabele mari, unde cifrele nu se pot citi toate"],
       ["barele stivuite 100%", "procentele pe rând: o bară pe interval, împărțită între cele două grupuri", "comparația proporțiilor între intervale de mărimi diferite"],
       ["barele grupate (<code>countplot</code>)", "numerele absolute, două bare pe interval", "când grupurile au mărimi apropiate; aici, grupul mic abia se vede"],
       ["mozaicul", "procentele pe rând, iar lățimea barei = câte perechi are intervalul", "proporțiile și mărimea grupurilor, deodată"]])
   + ix("edContingenta", "Distanța și apartenența la aceeași țară", {"sci": CONT_SCI})
   + "<h3>Codul, pe scurt</h3>"
   + cod("tabel = pd.crosstab(perechi[\"interval_km\"], perechi[\"aceeasi_tara\"])                       # numere\n"
         "pe_rand = pd.crosstab(perechi[\"interval_km\"], perechi[\"aceeasi_tara\"], normalize=\"index\")   # % pe rând\n\n"
         "sns.countplot(perechi, x=\"interval_km\", hue=\"aceeasi_tara\")      # bare grupate\n"
         "pe_rand.plot(kind=\"bar\", stacked=True)                            # bare stivuite 100%\n\n"
         "from statsmodels.graphics.mosaicplot import mosaic\n"
         "mosaic(perechi, [\"interval_km\", \"aceeasi_tara\"])                  # mozaicul")
   + "<h3>Cât de puternică este legătura: V al lui Cramér</h3>"
     "<p>Tabelul arată legătura; un singur număr o măsoară. Pentru două variabile categorice, <b>testul χ²</b> "
     "(hi-pătrat) compară tabelul real cu cel care ar ieși dacă variabilele n-ar fi legate și dă valoarea p: dacă "
     "legătura se deosebește de întâmplare. <b>V al lui Cramér</b> spune cât de puternică este: 0 înseamnă nicio "
     "legătură, 1 o legătură perfectă. Pentru un tabel 2 × 2 se folosește φ (phi), care este același lucru.</p>"
   + tabel(["V Cramér", "Intensitatea (Cohen, 1988)"], [
       ["sub 0,1", "neglijabilă"], ["0,1-0,3", "slabă"], ["0,3-0,5", "moderată"], ["peste 0,5", "puternică"]])
   + cod("from scipy import stats\n"
         "from scipy.stats.contingency import association\n\n"
         "stats.chi2_contingency(tabel).pvalue          # p: practic 0\n"
         "association(tabel, method=\"cramer\")         # V = 0,48")
   + "<p>Pe tabelul perechilor, p este practic 0, iar V = 0,48: o legătură puternică, la limita dintre moderată și "
     "puternică. Pragurile sunt convenții, nu reguli. Același rol îl au ρ și r pentru două variabile numerice "
     "(secțiunea următoare).</p>"
   + "<p>Legătura puternică dintre distanță și apartenența la aceeași țară are o consecință: o comparație a SCI între "
     "perechile din aceeași țară și cele din țări diferite, făcută pe toate perechile, amestecă efectul graniței cu cel "
     "al distanței. Separarea lor se face în secțiunea 5.</p>"
   + glosar("conting", "chi2", "cramer")
   + caiet("3", [
       "<code>pd.crosstab</code> cu numere, apoi cu <code>normalize=\"index\"</code> (procente pe rând).",
       "O propoziție în cuvinte pentru un rând al tabelului procentual.",
       "Testul χ² și V al lui Cramér: dacă legătura se deosebește de întâmplare și cât de puternică este."],
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
   + concept(f"Trei întrebări diferite despre aceleași puncte. {gl('pearson', 'Pearson')}: stau pe o dreaptă? "
             f"{gl('spearman', 'Spearman')}: când una crește, crește și cealaltă, chiar pe o curbă? (calculat pe "
             f"{gl('rang', 'ranguri')}). {gl('kendall', 'Kendall')}: luând două regiuni la întâmplare, cea cu PIB mai mare "
             "are și mai mulți absolvenți?")
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


# ===========================================================================
#  F. Trei sau mai multe variabile
# ===========================================================================

_H2 = D["h2"]
_I = _H2["intervale"].index("250-500")
_R = _H2["da"]["med"][_I] / _H2["nu"]["med"][_I]

sl("s11", "Trei sau mai multe variabile", "Granița și distanța",
   "<h2>Contează granița sau doar distanța?</h2>"
   + concept("Perechile din aceeași țară au SCI mult mai mare. Dar ele sunt aproape toate apropiate, iar apropierea "
             "crește singură SCI-ul. Ca să vedem efectul graniței, comparăm doar perechi aflate <b>la aceeași distanță</b>. "
             f"Distanța este aici un {gl('confuzie')}.")
   + ix("edGrupuri", "SCI în aceeași țară și în țări diferite", {"perechi": _PER})
   + vede("Pe toate perechile: aceeași țară, SCI de aproximativ 47 de ori mai mare. La aceeași distanță, mult mai puțin: "
          "de 7 ori la ~100 km, de 15 ori la ~300 km. Granița contează, dar comparația directă îi exagera efectul."),
   manual=
   "<h2>Contează granița sau doar distanța?</h2>"
   "<p>Întrebarea: sunt regiunile din aceeași țară mai legate pe Facebook decât cele din țări diferite? Comparația "
   "directă, pe toate perechile, spune că da, de aproximativ 47 de ori (mediana SCI).</p>"
   "<p>Comparația este însă nedreaptă. Graficul din stânga arată de ce: punctele portocalii (aceeași țară) stau aproape "
   "toate în partea stângă, la distanțe mici, iar acolo SCI este mare pentru orice pereche, din aceeași țară sau nu. "
   "Comparăm, de fapt, perechi apropiate cu perechi îndepărtate. O parte din diferență vine din distanță, nu din graniță.</p>"
   "<p>Soluția este o comparație între lucruri comparabile: doar perechi aflate la aproximativ aceeași distanță. "
   "Glisorul alege o distanță, banda colorată arată perechile comparate, iar în dreapta apar cele două mediane. La "
   "~100 km, perechile din aceeași țară sunt de 7 ori mai legate; la ~300 km, de 15 ori. Mult mai puțin decât 47, dar "
   "mult peste 1: granița contează și separat de distanță.</p>"
   "<p>O a treia variabilă care încurcă astfel o comparație (aici distanța, legată și de graniță, și de SCI) se "
   "numește <b>factor de confuzie</b> (engl. <i>confounder</i>). Exemplul clasic: cafeaua pare legată de bolile de "
   "inimă pentru că fumătorii beau mai multă cafea; fumatul este factorul de confuzie. Comparația la aceeași distanță "
   "se numește <b>stratificare</b>. Ea ține constantă doar distanța: limba, istoria comună și instituțiile rămân "
   "amestecate cu efectul graniței.</p>"
   + ix("edGrupuri", "SCI în aceeași țară și în țări diferite", {"perechi": _PER})
   + tabel(["Distanța", "toate", "~100 km", "~200 km", "~300 km", "~500 km", "~800 km"],
           [["aceeași țară / țări diferite (raportul medianelor)", "47×", "7×", "12×", "15×", "20×", "28×"]])
   + "<p>Calculat pe un eșantion de 10.000 de perechi. Peste 1.000 km, perechile din aceeași țară sunt foarte puține "
     "(teritoriile de peste mări ale Franței, Insulele Canare, Azore), deci rapoartele de acolo nu sunt de încredere.</p>"
   "<p>Consecința pentru C7: distanța și granița intră amândouă în model. Modelul face automat ce am făcut aici de "
   "mână: compară la aceeași distanță.</p>"
   + glosar("confuzie", "strat")
   + caiet("5", [
       "Mediana SCI pe toate perechile, după <code>aceeasi_tara</code>, și raportul celor două.",
       "Aceeași comparație doar pentru perechile aflate la 250-400 km "
       "(<code>perechi[perechi[\"distanta_km\"].between(250, 400)]</code>).",
       "Tabelul medianelor pe toate intervalele de distanță."],
       "Aceeași comparație la 80-130 km și la 600-1.000 km."))


# ===========================================================================
#  G. Pe hartă și ca rețea
# ===========================================================================

HARTA_PARTENERI = {
    "niveluri": ["regiuni"], "nivel": "regiuni", "masura": "dist", "ales": "RO11", "masuri": ["dist", "sci"],
    "povesti": [
        {"t": "Nord-Vest (România)", "nivel": "regiuni", "masura": "dist", "ales": "RO11",
         "text": "Peste așteptare: regiuni din Spania (La Rioja, Castilla-La Mancha, Aragón), Irlanda, Bruxelles și "
                 "Austria, de 20 până la 60 de ori mai legate decât sugerează distanța. Sunt țările migrației românești."},
        {"t": "Luxemburg", "nivel": "regiuni", "masura": "dist", "ales": "LU00",
         "text": "Toate regiunile Portugaliei, de 70 până la 180 de ori peste așteptare: portughezii sunt cea mai mare "
                 "comunitate străină din Luxemburg."},
        {"t": "Norte (Portugalia)", "nivel": "regiuni", "masura": "dist", "ales": "PT11",
         "text": "Luxemburg, Elveția și Corsica: destinațiile emigrației portugheze, de 30 până la 125 de ori peste așteptare."},
    ]}

HARTA_COM = {
    "niveluri": ["regiuni"], "nivel": "regiuni", "masura": "com", "ales": "RO11", "masuri": ["com", "sci"],
    "povesti": [
        {"t": "România și Germania", "nivel": "regiuni", "masura": "com", "ales": "RO11",
         "text": "Cele opt regiuni ale României sunt în aceeași comunitate cu Germania: migrația spre Germania și "
                 "legăturile istorice (sașii, șvabii) trec peste distanță."},
        {"t": "Austria și fosta Iugoslavie", "nivel": "regiuni", "masura": "com", "ales": "AT13",
         "text": "Austria formează o comunitate cu Slovenia, Croația, Serbia, Bosnia și Herțegovina și Muntenegru: "
                 "migrația din fosta Iugoslavie spre Austria."},
        {"t": "Polonia, Irlanda, Lituania", "nivel": "regiuni", "masura": "com", "ales": "PL91",
         "text": "Polonia împreună cu Irlanda, Lituania și Islanda: după 2004, polonezii au devenit cea mai mare "
                 "comunitate străină din Irlanda și din Islanda."},
        {"t": "Portugalia și Luxemburg", "nivel": "regiuni", "masura": "com", "ales": "LU00",
         "text": "Luxemburg intră în comunitatea Portugaliei, nu a vecinilor lui: aceeași poveste ca pe harta partenerilor."},
        {"t": "Cehia și Slovacia", "nivel": "regiuni", "masura": "com", "ales": "CZ01",
         "text": "O singură comunitate, ca fosta Cehoslovacie, despărțită în 1993."},
    ]}

sl("s12", "Pe hartă și ca rețea", "Partenerii unei regiuni",
   "<h2>Cu cine e legată o regiune, peste așteptare?</h2>"
   + concept("SCI-ul fiecărei perechi, împărțit la mediana perechilor aflate <b>la aceeași distanță</b>: 1× este cât "
             "sugerează distanța, 20× de 20 de ori mai mult. Clic pe hartă alege regiunea.")
   + ix("harta", "Partenerii unei regiuni, față de distanță", HARTA_PARTENERI)
   + vede("Nord-Vest e legată peste așteptare de Spania, Irlanda și Austria: coridoarele migrației, nu vecinii."),
   manual=
   "<h2>Cu cine e legată o regiune, peste așteptare?</h2>"
   "<p>SCI scade puternic cu distanța: regiunile vecine sunt aproape întotdeauna cele mai legate. Harta brută a "
   "legăturilor unei regiuni arată deci mai ales vecinii. Ca să se vadă ce iese din tipar, fiecare pereche se compară "
   "cu perechile aflate la aceeași distanță: SCI-ul ei se împarte la mediana SCI a tuturor perechilor din intervalul "
   "ei de distanță. Rezultatul se citește ca un raport: 1× înseamnă exact cât sugerează distanța, 2× de două ori mai "
   "mult, ½× jumătate. Este o primă formă a reziduului din modelul din C7.</p>"
   "<p>Pe hartă se alege o regiune (clic pe ea sau căutare); celelalte se colorează după raportul lor cu ea. Măsura "
   "„Legături” arată, pentru comparație, SCI-ul brut, unde domină vecinii. Butoanele din „Cazuri din date” duc la trei "
   "exemple.</p>"
   + ix("harta", "Partenerii unei regiuni, față de distanță", HARTA_PARTENERI)
   + tabel(["Regiunea", "Partenerii peste așteptare", "De câte ori"], [
       ["Nord-Vest (RO11)", "La Rioja, Castilla-La Mancha, Aragón (ES), Eastern and Midland (IE), Bruxelles, Steiermark (AT)", "20-62×"],
       ["Luxemburg (LU00)", "toate regiunile Portugaliei", "70-177×"],
       ["Norte (PT11)", "Luxemburg, regiunile Elveției, Corsica", "30-125×"]])
   + "<p>Partenerii peste așteptare nu sunt vecinii, ci destinațiile migrației. De aici decizia pentru C7: migrația "
     "intră în model, ca rată.</p>"
   + "<p>Ghicitoarea din C1 se rezolvă la fel. Italia are cei mai mulți migranți români (peste un milion) și cea mai "
     "mare rată, dar este abia a cincea după SCI: Austria, Germania, Ungaria și Irlanda sunt mai legate de România. "
     "Ungaria are puțini migranți români, dar o minoritate maghiară numeroasă în România. Migrația explică mult din "
     "SCI, dar nu tot.</p>"
   + caiet("6", [
       "<code>fata_de_distanta</code>: SCI-ul fiecărei perechi împărțit la mediana intervalului ei de distanță "
       "(<code>transform(\"median\")</code>).",
       "Pentru <code>REGIUNE = \"RO11\"</code>, cei 10 parteneri din alte țări cu raportul cel mai mare, apoi harta cu "
       "linii de la regiune la fiecare partener.",
       "Ghicitoarea din C1: perechile României cu SCI-ul, migranții și rata lor."],
       "Aceeași hartă pentru <code>\"LU00\"</code>, <code>\"PL91\"</code> sau regiunea echipei."))


sl("s13", "Pe hartă și ca rețea", "Comunitățile",
   "<h2>În ce grupuri se împarte Europa?</h2>"
   + concept(f"Perechile formează o {gl('retea', 'rețea')}: fiecare regiune e un nod, fiecare pereche o legătură, cu SCI "
             f"ca greutate. Algoritmul {gl('louvain', 'Louvain')} caută {gl('comunitate', 'comunități')}: grupuri de "
             "regiuni mai legate între ele decât cu restul. Nu știe nimic despre țări sau hartă.")
   + ix("harta", "Comunitățile rețelei SCI", HARTA_COM)
   + vede("16 comunități, cele mai multe pe granițe. Unele le trec: România cu Germania, Austria cu fosta Iugoslavie."),
   manual=
   "<h2>În ce grupuri se împarte Europa?</h2>"
   "<p>Tabelul perechilor se poate citi ca o <b>rețea</b>: fiecare regiune este un <b>nod</b>, fiecare pereche o "
   "<b>legătură</b>, iar SCI-ul este <b>greutatea</b> ei. Cele 298 de regiuni și 44.253 de perechi formează o rețea "
   "completă, în care orice regiune e legată de oricare alta, dar cu greutăți foarte diferite.</p>"
   "<p>O <b>comunitate</b> este un grup de noduri mai legate între ele decât cu restul rețelei. Algoritmul "
   "<b>Louvain</b> (Blondel și colegii, 2008) le caută mutând nodurile dintr-un grup în altul cât timp grupurile devin "
   "mai „închise” (măsura se numește modularitate). Algoritmul folosește doar greutățile legăturilor: nu știe ce țară "
   "are fiecare regiune și nici unde se află. Dacă totuși comunitățile urmează granițele, înseamnă că granițele sunt în "
   "date.</p>"
   + ix("harta", "Comunitățile rețelei SCI", HARTA_COM)
   + tabel(["Comunitatea", "Regiunile", "Explicația probabilă"], [
       ["România și Germania", "8 regiuni RO, 38 DE", "migrația spre Germania; sașii și șvabii"],
       ["Austria și fosta Iugoslavie", "AT, SI, HR, RS, BA, ME", "migrația din fosta Iugoslavie spre Austria"],
       ["Polonia, Irlanda, Lituania, Islanda", "17 PL, 3 IE, 2 LT, 1 IS", "migrația poloneză după 2004"],
       ["Portugalia și Luxemburg", "9 PT, 1 LU", "migrația portugheză"],
       ["Italia, Elveția, Malta", "21 IT, 7 CH, 1 MT", "limba italiană; vecinătatea"],
       ["Cehia și Slovacia", "8 CZ, 4 SK", "fosta Cehoslovacie"],
       ["Grecia, Cipru, Albania", "13 GR, 1 CY, 3 AL", "limba greacă; migrația albaneză"]])
   + "<p>Culorile sunt etichete, nu valori: comunitatea 3 nu este „mai mult” decât comunitatea 2. Gruparea arată "
     "<i>că</i> unele regiuni sunt legate peste granițe, dar nu <i>de ce</i>: explicațiile din tabel sunt ipoteze, de "
     "verificat cu alte date (migrația, limba).</p>"
   + glosar("retea", "comunitate", "louvain")
   + caiet("7", [
       "<code>nx.from_pandas_edgelist</code>: rețeaua, cu regiunile ca noduri și SCI ca greutate.",
       "<code>nx.community.louvain_communities(G, weight=\"sci\", seed=1)</code>: comunitățile, apoi numărul fiecărei "
       "regiuni pus în tabelul hărții.",
       "Harta comunităților, colorată pe categorii."],
       "<code>resolution=0.5</code>, apoi <code>2</code>, în <code>louvain_communities</code>: câte comunități ies?"))


# ===========================================================================
#  H. Verificarea
# ===========================================================================

sl("s14", "Verificarea", "Tipar sau întâmplare",
   "<h2>Relație reală sau întâmplare?</h2>"
   + concept("Amestecăm la întâmplare valorile unei coloane între regiuni: valorile rămân, legătura dispare. Corelațiile "
             "datelor amestecate arată cât de mare poate ieși o corelație <b>doar din întâmplare</b>. Dacă cea reală e "
             f"mult mai mare decât toate, relația e reală ({gl('permtest')}).")
   + ix("edLineup", "Corelația reală față de corelațiile datelor amestecate", _REG)
   + vede("PIB și studii (ρ = 0,61): nicio amestecare nu ajunge aproape, deci relația e reală. Vârsta și studiile "
          "(−0,23): tot reală, deși slabă. PIB și vârsta (−0,02): amestecările dau des corelații mai mari, deci poate "
          "fi doar întâmplare."),
   manual=
   "<h2>Relație reală sau întâmplare?</h2>"
   "<p>Orice corelație calculată pe date reale iese diferită de zero, chiar dacă variabilele nu au nicio legătură: "
   "întâmplarea produce mereu mici corelații. Întrebarea este dacă o corelație este mai mare decât ar produce "
   "întâmplarea.</p>"
   "<p>Răspunsul se poate obține direct, prin <b>amestecare</b> (permutare). Se iau valorile unei coloane, de exemplu "
   "studiile superioare, și se mută la întâmplare între regiuni, ca un pachet de cărți. Fiecare valoare rămâne în date, "
   "dar nu mai aparține regiunii ei, deci orice legătură cu PIB-ul dispare. Corelația datelor amestecate este o "
   "corelație „din întâmplare”. Repetată de 200 de ori, amestecarea arată cât de mari pot ieși corelațiile doar din "
   "întâmplare.</p>"
   "<p>Comparația este simplă. Dacă corelația reală iese mult în afara corelațiilor din amestecări, relația nu este "
   "întâmplătoare. Dacă multe amestecări dau corelații la fel de mari, relația poate fi doar întâmplare. Proporția "
   "amestecărilor cu o corelație cel puțin la fel de mare ca cea reală este <b>valoarea p</b>; sub 5% (1 din 20), "
   "relația se consideră reală. Procedeul se numește <b>test de permutare</b>.</p>"
   + ix("edLineup", "Corelația reală față de corelațiile datelor amestecate", _REG)
   + tabel(["Variabilele", "ρ real", "Corelațiile din amestecări", "Concluzia"], [
       ["PIB pe locuitor și studiile superioare", "0,61", "aproximativ între −0,15 și 0,15", "reală"],
       ["vârsta medie și studiile superioare", "−0,23", "aproximativ între −0,15 și 0,15", "reală, deși slabă"],
       ["PIB pe locuitor și vârsta medie", "−0,02", "aproximativ între −0,15 și 0,15", "poate fi întâmplare"]])
   + "<p>Aceeași logică explică problema <b>comparațiilor multiple</b>. Dacă se încearcă multe variabile, unele vor "
     "trece pragul de 5% doar din întâmplare: una din 20. Echipele vor încerca în C7 mai mulți predictori pentru SCI; "
     "ce se găsește explorând se verifică pe alte date (alt an, NUTS 3) înainte de a fi tratat ca rezultat.</p>"
   + glosar("perm", "permtest", "pval", "multiple")
   + caiet("8", [
       "<code>stats.spearmanr(x, y, nan_policy=\"omit\")</code>: intensitatea (ρ) și valoarea p, într-un singur apel. "
       "Formula dă direct ce arată amestecarea de pe slide.",
       "Cele trei perechi de variabile, pe rând: PIB și studii (ρ = 0,61, p practic 0), vârsta și studiile (ρ = −0,23, "
       "p &lt; 0,001), PIB și vârsta (ρ = −0,02, p ≈ 0,74)."],
       "<code>stats.spearmanr(regiuni[\"densitate\"], regiuni[\"somaj\"], nan_policy=\"omit\")</code>: cât de "
       "puternică este relația și se deosebește de întâmplare?"))


# ===========================================================================
#  I. Încheierea
# ===========================================================================

sl("s15", "Încheierea", "Tipurile de grafice",
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
    ("Relațiile", f"distanța: Spearman {ro(S['spearman'])}; granița contează și la aceeași distanță; "
                  "comunitățile urmează granițele, cu excepția coridoarelor migrației"),
    ("Verificarea", "relațiile puternice se deosebesc de întâmplare; cele slabe rămân de verificat în C7"),
]
DECIZII = [
    ("SCI: asimetrie pozitivă", "scara logaritmică și mediana"),
    ("Svalbard: numitor foarte mic", "se exclude"),
    ("lipsurile pe țări", "pe câte perechi, spus la fiecare rezultat"),
    ("distanța și granița, legate", "două variabile separate în model"),
    ("migrația contează ca rată", "rata la mie, nu numărul"),
]
PE_SCI_HTML = ('<div class="q6 q6--h q6--sci">' + "".join(f'<div><i>{k}</i><b>{a}</b><span>{b}</span></div>'
                                                          for k, (a, b) in enumerate(PE_SCI, 1)) + "</div>")
FIN_C6 = ('<div class="dc6">' + "".join(f'<div><span>{a}</span><b>{b}</b></div>' for a, b in DECIZII) + "</div>")

sl("s16", "Pe datele noastre", "Fluxul pe SCI",
   "<h2>Fluxul, pe datele noastre, și deciziile pentru C7</h2>"
   + PE_SCI_HTML + FIN_C6,
   manual=
   "<h2>Fluxul, pe datele noastre</h2>"
   "<p>Aceleași etape, pe perechile de regiuni. Fiecare constatare se încheie cu o decizie pentru modelul din C7.</p>"
   + PE_SCI_HTML + FIN_C6)


DOVADA = {
    "id": "c6-dovada",
    "sarcina": "Trei rezultate din caiet, rulate pe datele proprii. Ieșirea fiecăruia se lipește în câmpul lui.",
    "indiciu": "Celulele sunt în caietul 06: secțiunile 4.1, 4.2 și 2.3.",
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
         "daca_nu": "Corelația cu rata trebuie să fie în jur de 0.68. Populația vine din raw/bm.csv, din depozitul cursului, anul 2024."},
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

sl("s17", "Echipa", "Verificarea în caiet",
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

