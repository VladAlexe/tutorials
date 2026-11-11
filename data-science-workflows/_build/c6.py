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
    '<div><small>3 · relațiile</small><b>asocieri, grupuri, niveluri de analiză</b></div>'
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
_REGN = {"regiuni": E2["regiuni"], "var_reg": E2["var_reg"]}          # cu denumirile, pentru legendă
_PER = E2["perechi"]
_EXT = {k: E2[k] for k in ["sus", "jos", "sus2", "jos2", "medie_sci", "mediana_sci"]}


def concept(t):
    """Definiția conceptului, deasupra graficului."""
    return f'<p class="def6"><b>Conceptul.</b> {t}</p>'


def vede(t):
    """Rezultatul pe datele SCI, sub grafic."""
    return f'<p class="noi6"><i>Pe datele SCI</i><span>{t}</span></p>'


def caiet(sectiune, pasi, incercat=None):
    """Ce se face în caietul 06: pașii, apoi o modificare de încercat."""
    h = (f'<div class="nota nota--sobru"><div class="nota__et">În caiet, secțiunea {sectiune}</div><ol>'
         + "".join(f"<li>{p}</li>" for p in pasi) + "</ol>")
    if incercat:
        h += f"<p><b>De încercat.</b> {incercat}</p>"
    return h + "</div>"


sl("s3", "Profilul datelor", "Unitatea de analiză",
   "<h2>Unitatea de analiză și tipurile de variabile</h2>"
   + concept("<b>Unitatea de analiză</b> este entitatea descrisă de un rând. <b>Tipul</b> fiecărei coloane "
             "(identificator, numerică, categorică nominală sau ordinală, binară) determină rezumatele și graficele "
             "care au sens.")
   + ix("edTipuri", "Tipurile coloanelor din tabelul perechilor", {"tip": E2["tip"], "n": E2["n"], "same": E2["same"]})
   + vede(f"Unitatea de analiză este <b>perechea de regiuni</b>: {nr(D['n'])} de perechi formate din 298 de regiuni. "
          "Fiecare regiune intră în 297 de perechi, deci observațiile nu sunt independente."),
   manual=
   "<h2>Unitatea de analiză și tipurile de variabile</h2>"
   "<p>Primul pas al analizei exploratorii este stabilirea <b>unității de analiză</b>: entitatea pe care o descrie un "
   "rând. Tabelul perechilor are ca unitate perechea de regiuni, cu SCI-ul ei; tabelul regiunilor are ca unitate "
   "regiunea. Aceeași întrebare de cercetare („cât de conectată este o regiune cu străinătatea?”) se operaționalizează "
   "diferit pe cele două tabele: pe perechi, ca valori SCI individuale; pe regiuni, ca un indicator agregat "
   "(deschiderea, construită în caiet).</p>"
   "<p>Unitatea de analiză are două consecințe practice. Prima: numărul de rânduri trebuie să corespundă construcției "
   f"tabelului; din 298 de regiuni rezultă 298 × 297 / 2 = {nr(D['n'])} de perechi neordonate. A doua: perechile nu "
   "sunt observații independente, pentru că fiecare regiune apare în 297 dintre ele; o regiune atipică influențează "
   "simultan sute de rânduri. Această dependență contează la orice test statistic ulterior.</p>"
   "<p>Tipul fiecărei coloane (Stevens, 1946; Bruce și colegii, 2020, cap. 1) decide operațiile admisibile:</p>"
   + tabel(["Coloana", "Tipul", "Rezumate adecvate", "Graficul", "Fără sens"], [
       ["<code>regiune_1</code>", "identificator", "niciunul; leagă tabelele", "niciunul", "media sau frecvența codurilor"],
       ["<code>tara_1</code>", "categorică nominală", "frecvențe, moda", "bare ordonate după frecvență", "mediana (categoriile nu au ordine)"],
       ["<code>distanta_km</code>", "numerică continuă", "medie, mediană, cuantile, abatere", "histogramă, boxplot", "frecvențele valorilor individuale"],
       ["<code>interval_km</code>", "categorică ordinală", "frecvențe, mediana", "bare în ordinea intervalelor", "media (intervalele au lățimi diferite)"],
       ["<code>aceeasi_tara</code>", "binară", "proporția", "o proporție", "orice rezumat în plus"],
       ["<code>sci</code>", "numerică continuă, foarte asimetrică", "mediana, cuantile; media pe scara log", "histogramă pe scară log", "media pe scara obișnuită"]])
   + "<p>În exercițiul de mai jos se alege o coloană, apoi tipul ei; după un răspuns corect apar rezumatele adecvate și "
     "cele lipsite de sens.</p>"
   + ix("edTipuri", "Tipurile coloanelor din tabelul perechilor", {"tip": E2["tip"], "n": E2["n"], "same": E2["same"]})
   + nota("pandas și tipurile", "<code>dtypes</code> arată tipul de stocare, nu tipul statistic: <code>interval_km</code> "
          "este <code>category</code>, dar ordinea trebuie declarată explicit (<code>pd.cut</code> o creează ordonată); un cod "
          "numeric, de exemplu SIRUTA, ar apărea ca <code>int64</code>, deși este un identificator.", True)
   + caiet("0 și 1.1", [
       "Celula de pregătire citește <code>regiuni</code>, <code>perechi</code> și <code>tari</code> din <code>data/dsw.db</code>, "
       "apoi calculează <code>distanta_km</code> din centrele regiunilor, <code>interval_km</code> cu <code>pd.cut</code> și "
       "<code>aceeasi_tara</code>. Tot aici se construiește <code>deschidere</code>, folosită în secțiunile 4 și 5.",
       "<code>perechi.head()</code> și <code>perechi.dtypes</code>: pentru fiecare coloană se notează tipul statistic, "
       "comparat cu tipul din <code>dtypes</code>.",
       f"<code>len(perechi), 298 * 297 // 2</code>: cele două numere trebuie să fie egale ({nr(D['n'])}).",
       "Suma populației regiunilor din România se compară cu o sursă externă (aproximativ 19 milioane): un control al "
       "unităților de măsură."],
       "Același control pentru o altă țară, de exemplu <code>\"HU\"</code> (aproximativ 9,6 milioane)."))


V_LIPS = verif("c6-v-lips", 1,
               "Rețelele sociale lipsesc în toate regiunile Germaniei și Franței. Ce descrie o medie calculată fără ele?",
               ["Media tuturor regiunilor", "Media regiunilor cu date, fără DE și FR",
                "O medie invalidă", "Media Germaniei și a Franței"],
               "Lipsa depinde de țară (de sursa datelor), nu de întâmplare. Media rămâne corectă pentru regiunile cu "
               "date, dar nu descrie Germania și Franța; rezultatul trebuie raportat cu numărul de regiuni pe care a fost calculat.")

sl("s4", "Profilul datelor", "Valorile lipsă",
   "<h2>Valorile lipsă: distribuție și mecanism</h2>"
   + concept("O valoare poate lipsi <b>complet aleator</b>, <b>condiționat de o variabilă observată</b> (aici, țara, "
             "adică sursa) sau <b>în funcție de valoarea însăși</b>. Mecanismul determină ce descrie un rezultat "
             "calculat pe datele rămase.")
   + ix("edLipsuri", "Valorile lipsă din tabelul regiunilor", _REG)
   + vede("Ordonate după țară, lipsurile formează blocuri: rețelele sociale lipsesc în DE, FR și TR, PIB-ul în CH și "
          "NO. Mecanismul este condiționat de țară."),
   manual=
   "<h2>Valorile lipsă: distribuție și mecanism</h2>"
   "<p>Numărul valorilor lipsă spune puțin; contează unde se află și de ce. Rubin (1976) distinge trei mecanisme, "
   "definite prin relația dintre probabilitatea lipsei și date:</p>"
   + tabel(["Mecanismul", "Probabilitatea lipsei depinde de", "Rezultatul calculat pe datele rămase"], [
       ["complet aleator (MCAR)", "nimic", "nedeplasat, doar mai puțin precis"],
       ["aleator condiționat (MAR)", "o variabilă observată, de exemplu țara", "deplasat global, dar corectabil pe grupele acelei variabile"],
       ["neîntâmplător (MNAR)", "chiar valoarea care lipsește", "deplasat, fără posibilitate de corecție din datele observate"]])
   + "<p>Harta lipsurilor are un rând pe variabilă și o coloană pe regiune. În ordine întâmplătoare, lipsurile par "
     "împrăștiate; ordonate după țară, apar blocuri. Blocurile indică un mecanism condiționat de țară: datele provin din "
     "surse naționale, iar unele țări nu raportează anumiți indicatori. Ultima cifră din panou arată efectul analizei "
     "pe cazuri complete: păstrarea doar a regiunilor cu o variabilă schimbă și distribuția celorlalte variabile, "
     "pentru că schimbă componența eșantionului.</p>"
   + "<p>Fila „simularea mecanismelor” elimină o proporție aleasă din valorile PIB-ului prin fiecare mecanism și compară "
     "mediana observată cu cea adevărată. Prin eliminare complet aleatoare, abaterea rămâne mică și fără direcție; prin "
     "eliminarea unor țări întregi, abaterea depinde de țările pierdute; prin eliminarea preferențială a valorilor mari, "
     "abaterea are direcție constantă și crește cu proporția lipsă, iar datele rămase nu semnalează nimic.</p>"
   + ix("edLipsuri", "Valorile lipsă din tabelul regiunilor", _REG)
   + "<p>Consecința pentru analiză: o comparație care folosește PIB-ul pierde Elveția și Norvegia, două țări bogate; "
     "una care folosește rețelele sociale pierde Germania, Franța și Turcia. Fiecare rezultat se raportează împreună cu "
     "numărul de regiuni sau de perechi pe care a fost calculat.</p>"
   + caiet("1.2", [
       "<code>regiuni.isna().sum()</code>: numărul valorilor lipsă pe coloane.",
       "<code>value_counts()</code> pe țara regiunilor cu valori lipsă, pentru rețelele sociale și pentru PIB: lipsurile "
       "se concentrează în câteva țări.",
       "Se notează, pentru fișa echipei, mecanismul probabil al fiecărei lipse și variabilele afectate."],
       "Pentru <code>somaj</code>: se compară numărul regiunilor cu valori lipsă din fiecare țară cu numărul total de "
       "regiuni al țării (<code>regiuni[\"tara\"].value_counts()</code>). Lipsesc țări întregi sau regiuni izolate?"),
   dupa=V_LIPS)


sl("s5", "Profilul datelor", "Valorile extreme",
   "<h2>Valorile extreme: fenomen sau artefact</h2>"
   + concept("Cele mai mari și cele mai mici valori se citesc individual. SCI este o <b>rată</b>; la un numitor foarte "
             "mic, variația întâmplătoare plasează unitatea la oricare dintre capetele clasamentului.")
   + ix("edExtreme", "Cele mai mari și cele mai mici valori SCI", _EXT)
   + vede("Svalbard, cu câteva mii de locuitori, apare la ambele capete: cea mai mare valoare (cu Nord-Norge) și "
          "aproape toate minimele. Fără Svalbard, extremele devin plauzibile. Decizie: Svalbard se exclude din model."),
   manual=
   "<h2>Valorile extreme: fenomen sau artefact</h2>"
   "<p>Peng recomandă citirea primelor și ultimelor rânduri înainte de orice grafic. Valorile extreme sunt fie cazurile "
   "cele mai informative, fie erori ori artefacte ale construcției indicatorului; distincția se face caz cu caz, "
   "folosind cunoștințe despre date.</p>"
   "<p>SCI este o rată: numărul prieteniilor dintre două regiuni raportat la produsul numerelor de utilizatori. Variația "
   "întâmplătoare a unei rate scade cu rădăcina pătrată a numitorului (Wainer, 2007, numește această relație „cea mai "
   "periculoasă ecuație”). Unitățile foarte mici au deci rate instabile și apar la ambele capete ale oricărui clasament, "
   "fără ca aceasta să reflecte un fenomen real.</p>"
   + ix("edExtreme", "Cele mai mari și cele mai mici valori SCI", _EXT)
   + "<p>Butonul „exclude Svalbard” arată clasamentul fără regiunea problematică. Maximele devin perechi de regiuni "
     "vecine din aceeași țară (cele două regiuni ale Sloveniei, Groningen și Drenthe), iar minimele, perechi aflate la "
     "mii de kilometri (teritoriile franceze de peste mări și estul Turciei): valori plauzibile, explicabile prin distanță "
     "și graniță. Media SCI scade ușor, mediana aproape deloc, ceea ce anticipează slide-ul următor.</p>"
   + "<p>La celelalte regiuni efectul numitorului mic nu apare: împrăștierea SCI nu este mai mare la regiunile mici, "
     "probabil pentru că valorile publicate sunt deja netezite de Meta. Doar cazul extrem iese din tipar.</p>"
   + caiet("1.3", [
       "<code>perechi.nlargest(5, \"sci\")</code> și <code>perechi.nsmallest(5, \"sci\")</code>: se identifică regiunile "
       "care se repetă.",
       "Se caută codul <code>NO0B</code> în tabelul regiunilor: populația și denumirea.",
       "Se notează decizia (excluderea) și motivul ei, pentru fișa echipei."],
       "Se repetă cele două clasamente fără perechile care conțin <code>NO0B</code> "
       "(<code>perechi[(perechi[\"regiune_1\"] != \"NO0B\") &amp; (perechi[\"regiune_2\"] != \"NO0B\")]</code>)."))


# ===========================================================================
#  C. O variabilă numerică
# ===========================================================================

_EX = {"sci": D["esantion"], "sus": E2["sus"]}

V_REZ = verif("c6-v-rez", 2,
              "Se adaugă cele 8 perechi cu cele mai mari valori SCI la 60 de perechi obișnuite. Ce statistică rămâne aproape neschimbată?",
              ["Media", "Abaterea standard", "Mediana", "Toate se schimbă în aceeași măsură"],
              "Media și abaterea standard au punctul de cedare 1/n: o singură valoare extremă le poate muta oricât. "
              "Mediana, IQR și MAD au punctul de cedare 50%. De aceea SCI se rezumă cu mediana.")

sl("s6", "O variabilă numerică", "Locația și variabilitatea",
   "<h2>Locația, variabilitatea și rezistența</h2>"
   + concept("Locația se măsoară cu <b>media</b>, <b>media trunchiată</b> sau <b>mediana</b>; variabilitatea, cu "
             "<b>abaterea standard</b>, <b>IQR</b> sau <b>MAD</b>. <b>Punctul de cedare</b> este proporția de valori "
             "contaminate pe care o statistică o suportă înainte de a deveni arbitrar de mare.")
   + ix("edRezistenta", "Rezistența statisticilor la valori extreme", _EX)
   + vede(f"Pe toate perechile, media SCI este {nr(S['medie'])}, iar mediana {nr(S['mediana'])}: raport de aproximativ 8 la 1. "
          "Rezumatul adecvat este mediana."),
   manual=
   "<h2>Locația, variabilitatea și rezistența</h2>"
   "<p><b>Locația</b> (tendința centrală) se măsoară cu media, media trunchiată (media după eliminarea unei proporții "
   "fixe din fiecare capăt) sau mediana. <b>Variabilitatea</b> se măsoară cu abaterea standard, cu <b>IQR</b> (distanța "
   "dintre a 25-a și a 75-a percentilă) sau cu <b>MAD</b> (mediana abaterilor absolute față de mediană). Rezistența unei "
   "statistici se descrie prin <b>punctul de cedare</b>: proporția de valori care pot fi înlocuite cu valori arbitrar "
   "de mari fără ca statistica să devină arbitrar de mare (Velleman și Hoaglin, 1981; Bruce și colegii, 2020).</p>"
   + tabel(["Statistica", "Măsoară", "Punctul de cedare"], [
       ["media", "locația", "1/n (o singură valoare)"], ["media trunchiată 10%", "locația", "10%"], ["mediana", "locația", "50%"],
       ["abaterea standard", "variabilitatea", "1/n"], ["IQR", "variabilitatea", "25%"], ["MAD", "variabilitatea", "50%"]])
   + "<p>Graficul folosește 60 de perechi, câte una din 50 de-a lungul distribuției SCI. Primul glisor adaugă cele mai "
     "mari valori reale; al doilea înlocuiește progresiv valori cu maximul observat, pentru a ilustra punctul de cedare: "
     "media se mută de la prima valoare înlocuită, media trunchiată după 10%, mediana abia la 50%. Punctele sunt "
     "desenate pe scara logaritmică, dar toate statisticile sunt calculate pe valorile obișnuite.</p>"
   + ix("edRezistenta", "Rezistența statisticilor la valori extreme", _EX)
   + tabel(["SCI, toate perechile", "Valoarea"], [["media", nr(S["medie"])], ["media fără Svalbard", nr(S["medie_fara_svalbard"])],
                                                  ["media trunchiată 10%", nr(S["trunchiata10"])], ["mediana", nr(S["mediana"])],
                                                  ["abaterea standard", nr(S["sd"])], ["IQR", nr(S["iqr"])], ["MAD", nr(S["mad"])]])
   + "<p>Abaterea standard depășește de 24 de ori IQR-ul: aproape toată varianța SCI provine din câteva sute de perechi "
     "de regiuni vecine. Pentru o variabilă cu asemenea asimetrie, media și abaterea standard descriu coada, nu perechea "
     "tipică.</p>"
   + caiet("2.1", [
       "Celula cu cele șase statistici pe <code>perechi[\"sci\"]</code>: se compară media cu mediana și abaterea standard cu IQR.",
       "Celula care elimină cele 8 cele mai mari valori: se compară deplasarea mediei cu deplasarea medianei."],
       "Aceleași calcule pentru <code>distanta_km</code>. Raportul medie/mediană este mai apropiat de 1? Ce spune asta "
       "despre forma distribuției?"),
   dupa=V_REZ)


_DIS = {"sci": D["esantion"], "perechi": _PER[:3000], **_REG}

sl("s7", "O variabilă numerică", "Distribuția",
   "<h2>Distribuția unei variabile numerice</h2>"
   + concept("Distribuția descrie locația, împrăștierea și forma valorilor (simetrie, cozi, moduri). Histograma "
             "depinde de lățimea și originea claselor, densitatea de lățimea de bandă; <b>ECDF</b> (proporția valorilor ≤ x) "
             "nu depinde de nicio alegere.")
   + ix("edDistributie", "Distribuția unei variabile", _DIS)
   + vede("SCI pe scara log10: unimodal, cu o coadă spre valorile mari. Vârsta medie a regiunilor: asimetrie la stânga, "
          "generată de regiunile din Turcia. Boxplotul nu arată forma; violinul cu puncte o arată."),
   manual=
   "<h2>Distribuția unei variabile numerice</h2>"
   "<p>Cele cinci grafice ale unei distribuții răspund la întrebări diferite:</p>"
   + tabel(["Graficul", "Arată", "Depinde de"], [
       ["histograma", "frecvențele pe clase de valori", "numărul (lățimea) claselor și originea lor"],
       ["densitatea (KDE)", "o estimare netedă a formei", "lățimea de bandă"],
       ["ECDF", "proporția valorilor ≤ x; cuantilele se citesc direct", "nimic"],
       ["boxplotul", "mediana, cuartilele, valorile din afara mustăților", "regula de 1,5 × IQR"],
       ["violinul cu puncte", "forma și observațiile individuale", "lățimea de bandă"]])
   + "<p>Aceleași date pot părea unimodale sau bimodale după numărul claselor și originea lor (McNamara și Lunzer). "
     "De aceea forma se verifică pe mai multe valori ale parametrilor sau pe ECDF. Pe ECDF, mutarea pointerului afișează "
     "proporția valorilor de sub prag: la 0,5 se citește mediana, la 0,25 și 0,75 cuartilele.</p>"
   + ix("edDistributie", "Distribuția unei variabile", _DIS)
   + "<p>Boxplotul este util pentru comparația multor grupuri, dar ascunde forma: o distribuție bimodală și una "
     "uniformă pot avea același boxplot. Violinul cu puncte păstrează forma și arată și numărul observațiilor.</p>"
   + caiet("2.2", [
       "Celula cu patru grafice ale SCI pe scara logaritmică: histograma cu 8 și cu 40 de clase, ECDF, boxplotul. Se "
       "notează ce informație apare doar într-unul dintre ele.",
       "Celula cu boxplotul și violinul vârstei medii: se identifică regiunile din coada stângă "
       "(<code>regiuni.nsmallest(10, \"varsta_medie\")</code>)."],
       "Histograma SCI cu <code>bins=8</code>, <code>20</code>, <code>80</code>; densitatea cu <code>bw_adjust=0.2</code> și "
       "<code>2</code>. Care dintre ele ascund forma și care adaugă zgomot?"))


_REX = {"sci": D["esantion"], "perechi": _PER[:3000], **_REG}

sl("s8", "O variabilă numerică", "Reexprimarea",
   "<h2>Asimetria și reexprimarea</h2>"
   + concept("O transformare monotonă (rădăcina, logaritmul) schimbă scala fără a schimba ordinea valorilor. "
             "<b>Scara puterilor lui Tukey</b> ordonează transformările după intensitate; cu cât asimetria este mai mare, "
             "cu atât transformarea necesară este mai puternică.")
   + ix("edReexprimare", "Scara puterilor lui Tukey", _REX)
   + vede("SCI, densitatea și PIB-ul devin aproximativ simetrice la logaritm; populația trece de simetrie (asimetrie "
          "negativă). Pe scara simetrică, media și mediana coincid aproape. Analiza SCI continuă pe scara log10."),
   manual=
   "<h2>Asimetria și reexprimarea</h2>"
   "<p>O distribuție cu <b>asimetrie pozitivă</b> are coada spre valorile mari și media peste mediană. "
   "<b>Reexprimarea</b> înlocuiește fiecare valoare cu o funcție monotonă a ei. Scara puterilor (x, √x, log x, −1/√x, −1/x) "
   "ordonează transformările de la slabe la puternice; semnul minus de la puterile negative păstrează ordinea. Se alege "
   "transformarea cea mai slabă care aduce asimetria aproape de 0. Reexprimarea are trei efecte utile: face "
   "distribuțiile simetrice, stabilizează împrăștierea între grupuri și liniarizează relațiile curbe (Velleman și "
   "Hoaglin, 1981). Logaritmul are în plus o interpretare directă: diferențele devin rapoarte.</p>"
   + ix("edReexprimare", "Scara puterilor lui Tukey", _REX)
   + tabel(["Asimetria", "x", "√x", "log x"], [["SCI", "18,9", "6,3", "0,65"], ["PIB pe locuitor", "1,35", "0,63", "0,00"],
                                               ["populația", "3,32", "1,20", "−0,58"], ["densitatea", "5,74", "3,29", "0,37"]])
   + "<p>Media calculată pe scara logaritmică și readusă la scara inițială este media geometrică; pentru o distribuție "
     "simetrică pe log, ea este apropiată de mediană. Vârsta medie are asimetrie negativă și nu se transformă logaritmic.</p>"
   + "<p>Aceeași logică se aplică numărului de migranți dintre două țări: ca număr absolut, el depinde de mărimea "
     "țărilor; ca rată la 1.000 de locuitori, devine o măsură relativă, comparabilă cu SCI.</p>"
   + caiet("2.3", [
       "Funcția <code>scara()</code> calculează asimetria pentru patru transformări; tabelul rezultat se citește pe coloane.",
       "Corelația Spearman dintre SCI și numărul de migranți, apoi dintre SCI și rata la mie: se compară cele două valori. "
       "Rezultatul cu rata intră în verificarea de la finalul lecției."],
       "Funcția <code>scara()</code> aplicată distanței (<code>perechi[\"distanta_km\"]</code>). Ce transformare este suficientă?"))


# ===========================================================================
#  D. Variabile categorice
# ===========================================================================

_K = VZ["contingenta"]
CONT_SCI = {"r": [t.replace("peste 2000", "2000+") for t in _K["intervale"]], "c": ["aceeași țară", "țări diferite"],
            "v": [[a, b] for a, b in zip(_K["da"], _K["nu"])], "er": "distanța, km", "ec": "perechea"}
_P100 = _K["da"][0] / (_K["da"][0] + _K["nu"][0])

sl("s9", "Variabile categorice", "Tabelul de contingență",
   "<h2>Tabelul de contingență</h2>"
   + concept("Un <b>tabel de contingență</b> dă frecvențele combinațiilor a două variabile categorice. Procentele pe "
             "<b>rând</b> și pe <b>coloană</b> răspund la întrebări diferite; direcția se alege după variabila "
             "considerată explicativă.")
   + ix("edContingenta", "Distanța și apartenența la aceeași țară", {"sci": CONT_SCI})
   + vede(f"Sub 100 km, {_P100:.0%} din perechi sunt în aceeași țară; peste 1.000 km, sub 1%: distanța și granița "
          "sunt puternic asociate."),
   manual=
   "<h2>Frecvențe, proporții și tabelul de contingență</h2>"
   "<p>O variabilă categorică se rezumă prin frecvențe și proporții, reprezentate ca bare ordonate. Două variabile "
   "categorice se rezumă printr-un tabel de contingență. Procentele pe rând dau <b>distribuțiile condiționate</b> ale "
   "variabilei din coloane, pentru fiecare categorie din rânduri: „dintre perechile aflate la 100-250 km, ce proporție "
   "este în aceeași țară?”. Procentele pe coloană răspund la întrebarea inversă: „dintre perechile din aceeași țară, ce "
   "proporție se află la 100-250 km?”. Cele două proporții pot fi foarte diferite; confuzia lor este o eroare frecventă "
   "de interpretare.</p>"
   "<p>Barele stivuite 100% arată distribuțiile condiționate pe rând. <b>Mozaicul</b> adaugă, prin lățimea fiecărei "
   "coloane, numărul de cazuri al categoriei: intervalele cu puține perechi devin înguste. Un clic pe o celulă a "
   "tabelului afișează ambele citiri.</p>"
   + ix("edContingenta", "Distanța și apartenența la aceeași țară", {"sci": CONT_SCI})
   + "<p>Asocierea puternică dintre distanță și apartenența la aceeași țară are o consecință pentru analiză: o comparație "
     "a SCI între perechile din aceeași țară și cele din țări diferite, făcută pe toate perechile, amestecă efectul "
     "graniței cu efectul distanței. Separarea lor se face în secțiunea 5.</p>"
   + caiet("3", [
       "<code>pd.crosstab</code> cu numere, apoi cu <code>normalize=\"index\"</code> (procente pe rând).",
       "Se formulează în cuvinte o propoziție pentru un rând al tabelului procentual."],
       "<code>normalize=\"columns\"</code>: aceeași celulă, citită pe coloană. Se formulează propoziția corespunzătoare și se "
       "compară cu cea de mai sus."))


# ===========================================================================
#  E. Două variabile numerice
# ===========================================================================

_COR = {"perechi": _PER[:300], **_REG}
V_COR = verif("c6-v-cor", 3,
              f"Pe valorile brute, coeficientul Pearson dintre distanță și SCI este {ro(S['pearson_brut'])}. Ce se poate afirma?",
              ["Relația este slabă", "Nu există relație", "Distanța nu influențează SCI",
               "Pearson e sensibil la extreme; pe log sau cu Spearman, relația e clară"],
              f"Pe log-log, Pearson = {ro(S['pearson_log'])}; Spearman = {ro(S['spearman'])}; Kendall = {ro(S['kendall'])}. "
              "Coeficientul se alege după forma relației, examinată întâi pe grafic.")

sl("s10", "Două variabile numerice", "Corelația",
   "<h2>Coeficienții de corelație: Pearson, Spearman, Kendall</h2>"
   + concept("<b>Pearson</b> măsoară asocierea liniară. <b>Spearman</b> este Pearson calculat pe ranguri și măsoară "
             "asocierea monotonă. <b>Kendall</b> este diferența dintre proporția perechilor de observații concordante și "
             "a celor discordante.")
   + ix("edCorelatie", "Trei coeficienți; punctele se pot trage", _COR)
   + vede(f"Distanța și SCI: Pearson {ro(S['pearson_brut'])} pe valorile brute și {ro(S['pearson_log'])} pe log-log; "
          f"Spearman {ro(S['spearman'])} și Kendall {ro(S['kendall'])} pe ambele scări."),
   manual=
   "<h2>Coeficienții de corelație</h2>"
   + tabel(["Coeficientul", "Definiția", "Măsoară", "Sensibil la"], [
       ["Pearson r", "covarianța raportată la produsul abaterilor standard", "asocierea liniară", "valori extreme, curbură"],
       ["Spearman ρ", "Pearson calculat pe ranguri", "asocierea monotonă", "puțin; nu detectează relații ne-monotone"],
       ["Kendall τ", "(concordante − discordante) / numărul perechilor de observații", "asocierea monotonă", "puțin; valori mai mici decât ρ, interpretare probabilistică"]])
   + "<p>Spearman și Kendall depind doar de ordinea valorilor, deci sunt invarianți la orice transformare monotonă, "
     "inclusiv la logaritm; Pearson nu este. Kendall are o interpretare directă: τ = 0,33 înseamnă că, pentru două "
     "observații alese la întâmplare, probabilitatea ca ordinea lor să coincidă pe cele două variabile depășește cu 33 "
     "de puncte procentuale probabilitatea ca ordinea să fie inversă. Niciun coeficient nu detectează o relație în formă "
     "de U, motiv pentru care graficul precedă coeficientul.</p>"
   + "<p>În graficul de mai jos punctele pot fi trase cu mouse-ul. Mutarea unui singur punct departe de nor schimbă "
     "considerabil coeficientul Pearson și dreapta celor mai mici pătrate, dar abia mișcă Spearman și Kendall. Butonul "
     "„scară logaritmică” arată aceeași invarianță: doar Pearson se schimbă.</p>"
   + ix("edCorelatie", "Trei coeficienți; punctele se pot trage", _COR)
   + caiet("4.1", [
       "Spearman, Pearson pe valorile brute și pe log-log, apoi Kendall, pentru distanță și SCI. Rezultatul Spearman "
       "intră în verificarea de la finalul lecției (aproximativ −0,46).",
       "Se explică în cuvinte de ce Pearson pe valorile brute este mult mai mic în valoare absolută."],
       "Cele trei metode pentru <code>pib_locuitor</code> și <code>densitate</code> în tabelul regiunilor "
       "(<code>regiuni[\"pib_locuitor\"].corr(regiuni[\"densitate\"], method=...)</code>), apoi Pearson pe "
       "<code>np.log10</code> al densității."),
   dupa=V_COR)


sl("s11", "Două variabile numerice", "Suprapunerea punctelor",
   "<h2>Suprapunerea punctelor în graficele de dispersie</h2>"
   + concept("La zeci de mii de observații, punctele se suprapun și densitatea lor nu mai este vizibilă. Alternativele: "
             "<b>transparența</b>, <b>histograma bidimensională</b> (celule colorate după frecvență) și <b>rezumatele "
             "condiționate</b> (mediana și cuartilele lui y pe intervale ale lui x).")
   + ix("edMulte", "Distanța și SCI, pe 10.000 de perechi", {"perechi": _PER})
   + vede("Medianele pe intervale arată forma relației: SCI scade rapid până la câteva sute de kilometri, apoi mai lent; "
          "pe log-log, scăderea este aproximativ liniară."),
   manual=
   "<h2>Graficul înaintea coeficientului; suprapunerea punctelor</h2>"
   "<p>Cvartetul lui Anscombe (1973) a arătat că patru seturi de date cu aceeași medie, aceeași varianță și aceeași "
   "corelație pot avea grafice complet diferite; Matejka și Fitzmaurice (2017) au generalizat rezultatul. Graficul "
   "precedă deci orice coeficient.</p>"
   "<p>La volume mari apare o problemă diferită: <b>suprapunerea</b> (overplotting). Cu 10.000 de puncte, zona cu cele "
   "mai multe observații arată la fel ca o zonă cu puține. Soluțiile depind de volum:</p>"
   + tabel(["Metoda", "Parametrul", "Potrivită pentru"], [
       ["transparența", "opacitatea fiecărui punct", "până la câteva mii de puncte"],
       ["histograma bidimensională (hexbin)", "numărul celulelor", "zeci de mii de puncte și peste"],
       ["mediane și cuartile pe intervale", "lățimea intervalelor", "forma relației și împrăștierea ei"]])
   + "<p>Cei doi parametri se pot ajusta în grafic. Opacitatea potrivită scade odată cu numărul de puncte; celulele "
     "prea mici produc zgomot, cele prea mari ascund forma. Numerele de deasupra medianelor arată câte perechi intră în "
     "fiecare interval: estimările de la capete se bazează pe mai puține observații.</p>"
   + ix("edMulte", "Distanța și SCI, pe 10.000 de perechi", {"perechi": _PER})
   + caiet("4.2", [
       "<code>sns.histplot</code> cu <code>x</code> și <code>y</code> și <code>log_scale=True</code>: histograma "
       "bidimensională a tuturor perechilor.",
       "<code>groupby(\"interval_km\")</code> cu mediana SCI: forma relației, ca tabel."],
       "<code>sns.scatterplot</code> cu <code>alpha=0.02</code>, apoi <code>0.2</code>, pe toate perechile, cu "
       "<code>ax.set(xscale=\"log\", yscale=\"log\")</code>. Care valoare arată densitatea?"))


sl("s12", "Două variabile numerice", "Lineup",
   "<h2>Inferența vizuală: protocolul lineup</h2>"
   + concept("Un grafic se interpretează prin comparație cu ce ar arăta în absența relației. <b>Protocolul lineup</b> "
             "plasează graficul real printre grafice în care o variabilă a fost <b>permutată</b> între observații. "
             "Identificarea lui indică un tipar distinct de zgomot.")
   + ix("edLineup", "Graficul real, printre grafice permutate", _REG)
   + vede("PIB-ul și studiile: graficul real se identifică imediat. Deschiderea și longitudinea: se identifică, mai "
          "greu. Deschiderea și populația: graficul real nu se distinge de permutări."),
   manual=
   "<h2>Inferența vizuală: protocolul lineup</h2>"
   "<p>Orice grafic exploratoriu este citit în raport cu un model implicit, de obicei absența relației (Gelman, 2004; "
   "Hullman și Gelman, 2021), iar percepția vizuală detectează tipare și în date aleatoare. <b>Protocolul lineup</b> "
   "(Buja și colegii, 2009) face comparația explicită. Valorile unei variabile se permută aleator între observații: "
   "permutarea distruge relația, dar păstrează exact ambele distribuții marginale. Graficul real se ascunde printre "
   "graficele permutate.</p>"
   "<p>Logica este cea a unui test statistic. Dacă relația nu există, graficul real este doar una dintre cele 8 "
   "permutări posibile, iar probabilitatea de a-l alege este 1/8; cu 20 de grafice, 1/20, echivalentul pragului de "
   "0,05. Fiecare punct este o regiune, desenată pe ranguri, ca să nu conteze asimetria variabilelor.</p>"
   "<p><b>Deschiderea</b> unei regiuni spre străinătate este definită în caiet ca mediana SCI-ului ei cu regiunile din "
   "alte țări, fiecare valoare fiind raportată la mediana tuturor perechilor din același interval de distanță. O valoare "
   "de 2 înseamnă legături de două ori mai puternice decât ar sugera distanța.</p>"
   + ix("edLineup", "Graficul real, printre grafice permutate", _REG)
   + caiet("4.3", [
       "Funcția <code>lineup(x, y)</code> desenează 8 grafice și întoarce poziția graficului real; răspunsul se afișează "
       "în celula următoare, după alegere.",
       "Lineup pentru PIB și studii, apoi pentru longitudine și deschidere. Se notează, înainte de a afișa răspunsul, "
       "graficul ales."],
       "<code>lineup(cu_desc[\"populatie\"], cu_desc[\"deschidere\"])</code>. Graficul real se poate identifica?"))


# ===========================================================================
#  F. Trei sau mai multe variabile
# ===========================================================================

_H2 = D["h2"]
_I = _H2["intervale"].index("250-500")
_R = _H2["da"]["med"][_I] / _H2["nu"]["med"][_I]

sl("s13", "Trei sau mai multe variabile", "Grupuri și confuzie",
   "<h2>Comparația grupurilor și variabila de confuzie</h2>"
   + concept("O variabilă numerică se compară între grupuri prin <b>distribuții</b> (boxplot, violin, puncte), nu doar "
             "prin medii. O <b>variabilă de confuzie</b> este asociată atât cu gruparea, cât și cu rezultatul; "
             "<b>stratificarea</b> o menține constantă.")
   + ix("edGrupuri", "SCI pe intervale de distanță", {"perechi": _PER[:4000]})
   + vede(f"La aceeași distanță, perechile din aceeași țară au mediana SCI de {_R:.0f} ori mai mare (250-500 km). "
          "Comparația fără intervale ar atribui graniței și efectul distanței."),
   manual=
   "<h2>Comparația grupurilor și variabila de confuzie</h2>"
   "<p>Bara cu media și eroarea ei standard ascunde distribuția din fiecare grup. Pentru o variabilă cu asimetrie "
   "puternică, ca SCI, media pe scara obișnuită este dominată de câteva perechi foarte legate: barele nu descriu perechea "
   "tipică, iar erorile sunt mari. Boxploturile, violinele și punctele individuale pe scara logaritmică arată mediana, "
   "împrăștierea și forma fiecărui grup; numărul de cazuri de sub fiecare grup arată pe ce se bazează comparația.</p>"
   "<p>O <b>variabilă de confuzie</b> este asociată atât cu variabila de grupare, cât și cu rezultatul. Perechile din "
   "aceeași țară sunt aproape toate apropiate (secțiunea 3), iar apropierea crește SCI-ul. O comparație între perechile "
   "din aceeași țară și cele din țări diferite, făcută pe toate perechile, atribuie graniței și efectul distanței. "
   "<b>Stratificarea</b>, adică comparația în interiorul fiecărui interval de distanță, menține distanța aproximativ "
   "constantă. Alte variabile asociate cu granița (limba, istoria comună, instituțiile) rămân însă amestecate cu efectul ei.</p>"
   "<p>În grafic, butonul „separat” adaugă apartenența la aceeași țară ca a treia variabilă, prin culoare; butonul "
   "„fără intervale” reunește toate distanțele. Raportul medianelor afișat în panou se compară între cele două situații.</p>"
   + ix("edGrupuri", "SCI pe intervale de distanță", {"perechi": _PER[:4000]})
   + caiet("5.1", [
       "Bara cu media pe intervale, alături de boxplotul pe scara log, separat după <code>aceeasi_tara</code>: se compară "
       "ce arată fiecare.",
       "Tabelul <code>h2</code> cu medianele și raportul lor pe intervale: efectul graniței la distanță aproximativ constantă."],
       "Raportul medianelor pe toate perechile, fără intervale "
       "(<code>perechi.groupby(\"aceeasi_tara\")[\"sci\"].median()</code>). De ce este mai mare decât în interiorul intervalelor?"))


_NV = S["nivele"]
V_NIV = verif("c6-v-niv", 1,
              f"Între țări, populația și deschiderea au ρ = {ro(_NV['intre'])}; în interiorul țărilor, {ro(_NV['in'])}. "
              "Ce afirmație este corectă?",
              ["Regiunile mari sunt mai închise", "În aceeași țară, regiunile mari sunt mai deschise",
               "Nu există asociere", "Corelația totală este suficientă"],
              "Relația dintre țări și relația din interiorul țărilor răspund la întrebări diferite. Corelația totală "
              f"({ro(_NV['total'])}) le combină și se anulează. O concluzie despre regiuni nu se trage din corelația "
              "dintre țări (eroarea ecologică).")

sl("s14", "Trei sau mai multe variabile", "Nivelul de analiză",
   "<h2>Nivelul de analiză și eroarea ecologică</h2>"
   + concept("Pe date ierarhice (regiuni în țări), relația <b>dintre grupuri</b>, relația <b>din interiorul "
             "grupurilor</b> și relația <b>totală</b> pot diferi, inclusiv ca semn. Inferența despre unități pornind de "
             "la relația dintre grupuri este <b>eroarea ecologică</b> (Robinson, 1950).")
   + ix("edNivele", "Populația și deschiderea spre străinătate", _REGN)
   + vede(f"Între țări, ρ = {ro(_NV['intre'])} (țările mici sunt mai deschise); în interiorul lor, {ro(_NV['in'])} "
          f"(capitalele sunt mai deschise); pe total, {ro(_NV['total'])}."),
   manual=
   "<h2>Nivelul de analiză și eroarea ecologică</h2>"
   "<p>Robinson (1950) a comparat, pe recensământul american din 1930, corelația dintre a fi născut în străinătate și "
   "analfabetism: la nivel individual, 0,118; la nivelul statelor, −0,526. Semnul se inversează între niveluri. Pe date "
   "ierarhice se pot calcula trei relații distincte:</p>"
   + tabel(["Relația", "Se calculează pe", "Răspunde la întrebarea"], [
       ["dintre grupuri", "medianele (sau mediile) fiecărei țări", "țările cu regiuni mai populate sunt mai deschise?"],
       ["din interiorul grupurilor", "regiunile fiecărei țări, separat", "în aceeași țară, regiunile mai populate sunt mai deschise?"],
       ["totală", "toate regiunile, împreună", "o combinație a celor două, greu de interpretat"]])
   + "<p>Rezultatul depinde și de felul în care sunt trasate unitățile: <b>problema unității areale modificabile</b> "
     "(Openshaw, 1984). În grafic, cele trei butoane adaugă dreptele fiecărui nivel; un clic pe o țară din legendă "
     "evidențiază regiunile ei și afișează corelația din interiorul acelei țări.</p>"
   + ix("edNivele", "Populația și deschiderea spre străinătate", _REGN)
   + noi(f"ρ = {ro(_NV['intre'])} între țări, {ro(_NV['in'])} mediana din interiorul celor {_NV['n_tari']} țări cu cel "
         f"puțin 5 regiuni, {ro(_NV['total'])} pe total. Tiparul se replică la NUTS 3 (1.323 de regiuni): −0,15 total, "
         "+0,44 în interiorul țărilor.")
   + caiet("5.2", [
       "Celula calculează cele trei corelații Spearman: totală, între țări (pe medianele țărilor) și mediana corelațiilor "
       "din interiorul țărilor cu cel puțin 5 regiuni.",
       "Se formulează pentru fiecare valoare întrebarea la care răspunde."],
       "Seria <code>in_tari</code> sortată: în ce țări relația este negativă? Câte regiuni au acestea?"),
   dupa=V_NIV)


sl("s15", "Trei sau mai multe variabile", "Multe variabile",
   "<h2>Analiza multivariată: matricea de grafice și matricea de corelație</h2>"
   + concept("<b>Matricea de grafice</b> arată fiecare pereche de variabile, cu distribuțiile pe diagonală; "
             "<b>matricea de corelație</b> rezumă fiecare pereche printr-un coeficient, pe o scară divergentă centrată pe 0. "
             "Predictorii puternic corelați produc <b>multicoliniaritate</b>.")
   + ix("edMultivar", "Indicatorii regiunilor", _REG)
   + vede("PIB-ul este asociat cu studiile (ρ = 0,61) și cu densitatea (0,52), negativ cu șomajul (−0,45). Efectele "
          "acestor predictori sunt greu de separat într-un model."),
   manual=
   "<h2>Analiza multivariată</h2>"
   "<p>O a treia variabilă se adaugă unui grafic prin <b>culoare</b> (<code>hue=</code>) sau prin <b>fațete</b>, adică "
   "același grafic repetat pe grupuri, cu aceleași axe (<code>col=</code>). Pentru mai multe variabile numerice simultan "
   "se folosesc matricea de grafice (<code>pairplot</code>) și matricea de corelație (<code>heatmap</code>). Matricea de "
   "corelație se desenează pe o scară de culori <b>divergentă</b>, centrată pe 0, cu limitele fixate la −1 și 1, astfel "
   "încât intensitatea culorii să fie comparabilă între celule.</p>"
   "<p>Variabilele puternic corelate între ele transmit informație parțial redundantă. Într-un model de regresie, "
   "efectele lor individuale se estimează imprecis (<b>multicoliniaritate</b>); de aceea matricea de corelație a "
   "predictorilor se examinează înaintea modelului din C7.</p>"
   "<p>În componenta de mai jos, un clic pe o celulă a oricărei matrice selectează aceeași pereche în ambele. Butoanele "
   "comută între Spearman și Pearson și între densitatea brută și densitatea logaritmată: cu Pearson, scala densității "
   "schimbă coeficienții; cu Spearman, nu.</p>"
   + ix("edMultivar", "Indicatorii regiunilor", _REG)
   + caiet("5.3", [
       "<code>sns.pairplot</code> pe cinci indicatori: se identifică perechile cu relație vizibilă și variabilele asimetrice.",
       "<code>sns.heatmap</code> cu matricea Spearman.",
       "<code>len(economice), len(perechi)</code>: perechile cu PIB la ambele capete, rezultat folosit în verificarea finală "
       "(37.950 din 44.253)."],
       "Aceeași matrice cu <code>method=\"pearson\"</code>, apoi cu densitatea logaritmată. Care coeficienți se schimbă?"))


# ===========================================================================
#  G. Tipar și reziduu
# ===========================================================================

sl("s16", "Tipar și reziduu", "Tipar și reziduu",
   "<h2>Tipar și reziduu</h2>"
   + concept("Datele se descompun în <b>tipar</b> și <b>reziduu</b>. Tiparul dominant (scăderea SCI cu distanța) se "
             "estimează cu dreapta celor mai mici pătrate; <b>reziduul</b> este diferența dintre valoarea observată și "
             "cea dată de dreaptă. Tiparele secundare apar în reziduuri.")
   + ix("edReziduu", "SCI față de distanță", {"perechi": _PER[:1500]})
   + vede("După dreapta celor mai mici pătrate, perechile din aceeași țară au reziduul median aproape +1 pe scara "
          "log10: legături de aproximativ 10 ori mai puternice decât prezice distanța."),
   manual=
   "<h2>Tipar și reziduu</h2>"
   "<p>Tukey descrie datele ca sumă dintre un tipar și un rest: <i>date = tipar + reziduu</i>. După identificarea "
   "tiparului dominant, acesta se elimină printr-un model simplu, iar tiparele secundare se caută în reziduuri. Exemplul "
   "din <i>R for Data Science</i>: calitatea diamantelor pare să scadă prețul până când se ține seama de mărimea lor. "
   "Un grafic al reziduurilor fără structură indică un tipar complet; o curbură sau grupuri distincte în reziduuri "
   "indică ce lipsește din model.</p>"
   "<p><b>Dreapta celor mai mici pătrate</b> este dreapta care minimizează suma pătratelor reziduurilor. În componenta de "
   "mai jos, panta și nivelul se ajustează manual; panoul arată suma pătratelor și diferența față de minimul posibil. "
   "Butonul „reziduurile, ca segmente” desenează distanța verticală dintre fiecare punct și dreaptă, adică mărimea "
   "minimizată. Butonul „cele mai mici pătrate” calculează soluția exactă.</p>"
   + ix("edReziduu", "SCI față de distanță", {"perechi": _PER[:1500]})
   + "<p>În graficul reziduurilor, perechile din aceeași țară (portocaliu) se situează sistematic deasupra liniei 0: "
     "granița apare ca tipar secundar, după eliminarea distanței. Reziduurile unei singure regiuni, pe hartă, arată cu ce "
     "regiuni este mai legată decât ar prezice distanța: pentru Nord-Vest, Spania și Irlanda, unde migrația este mare. "
     "Modelul din C7 extinde aceeași logică la mai mulți predictori.</p>"
   + caiet("6", [
       "<code>np.polyfit</code> pe log10 al distanței și al SCI: panta și nivelul dreptei.",
       "Reziduul fiecărei perechi și mediana lui după <code>aceeasi_tara</code>.",
       "Graficul în două panouri: dreapta peste date și reziduurile față de distanță, pe un eșantion de 3.000 de perechi.",
       "Harta reziduurilor pentru <code>REGIUNE = \"RO11\"</code>: roșu, legături mai puternice decât prezice distanța; "
       "albastru, mai slabe."],
       "Harta pentru altă regiune, de exemplu <code>\"LU00\"</code> sau regiunea proprie a echipei. Ce regiuni ies în "
       "evidență și ce le-ar putea explica?"))


# ===========================================================================
#  H. Verificarea
# ===========================================================================

V_POT = verif("c6-v-pot", 1,
              "Dintre 40 de variabile aleatoare, una are ρ = 0,15 cu deschiderea regiunilor. Cum se interpretează?",
              ["Variabila explică deschiderea", "Maximul așteptat a 40 de corelații întâmplătoare",
               "Eșantionul e prea mic", "Trebuie Pearson"],
              "Maximul mai multor corelații întâmplătoare crește cu numărul variabilelor încercate. Ce se găsește "
              "explorând se verifică pe alte date.")

sl("s17", "Verificarea", "Comparațiile multiple",
   "<h2>Comparațiile multiple: grădina potecilor care se bifurcă</h2>"
   + concept("Printre multe variabile fără legătură reală cu rezultatul, unele apar corelate din întâmplare; cea mai "
             "mare corelație întâmplătoare crește cu numărul variabilelor încercate. Constatările exploratorii se "
             "<b>verifică pe date independente</b>.")
   + ix("edPoteci", "Indicatorii reali și variabile aleatoare", _REG)
   + vede("Între 20 și 60 de variabile aleatoare, maximul ajunge de obicei la 0,13-0,16. Tiparul populație-deschidere "
          "s-a replicat la NUTS 3; celelalte constatări rămân ipoteze pentru C7."),
   manual=
   "<h2>Comparațiile multiple: grădina potecilor care se bifurcă</h2>"
   "<p>O analiză exploratorie implică multe alegeri: variabilele, subgrupurile, transformările, excluderile. Gelman și "
   "Loken numesc această situație <b>grădina potecilor care se bifurcă</b>: chiar fără intenție, dintre multe comparații "
   "posibile, cea mai interesantă este supraestimată. Pentru o singură variabilă fără efect, probabilitatea de a depăși "
   "pragul de 5% este 5%; pentru 40 de variabile independente, probabilitatea ca cel puțin una să-l depășească este "
   "1 − 0,95<sup>40</sup> ≈ 87%.</p>"
   "<p>Componenta de mai jos are două moduri. „O încercare” adaugă k variabile de numere aleatoare lângă indicatorii "
   "reali și le ordonează după corelația cu deschiderea. „200 de repetări” repetă experimentul și desenează distribuția "
   "maximului celor k corelații întâmplătoare, cu indicatorii reali marcați: un indicator real este convingător doar "
   "dacă depășește clar această distribuție, nu doar pragul pentru o singură variabilă (|ρ| ≈ 0,11 la 290 de regiuni).</p>"
   + ix("edPoteci", "Indicatorii reali și variabile aleatoare", _REG)
   + "<p>Hullman și Gelman (2021) recomandă verificarea constatărilor exploratorii pe date păstrate deoparte: alt an, "
     "alt nivel de agregare, altă sursă. Pentru tiparul populație-deschidere, verificarea s-a făcut la NUTS 3, pe "
     "<code>baza_completa.db</code>: −0,15 total și +0,44 în interiorul țărilor, același tipar ca la NUTS 2.</p>"
   + caiet("7", [
       "Celula generează 40 de variabile aleatoare și calculează corelația Spearman a fiecăreia cu deschiderea, alături "
       "de indicatorii reali.",
       "Se compară cea mai mare corelație întâmplătoare cu corelațiile indicatorilor reali."],
       "Celula rulată de mai multe ori, cu <code>rng</code> nedeterminat (<code>np.random.default_rng()</code>), și cu "
       "100 de variabile în loc de 40: cât de mare devine maximul?"),
   dupa=V_POT)


# ===========================================================================
#  I. Încheierea
# ===========================================================================

sl("s18", "Încheierea", "Tipurile de grafice",
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
    ("O variabilă", "asimetrie puternică: media de 8 ori mediana; scara log10 și mediana"),
    ("Relațiile", f"distanța: Spearman {ro(S['spearman'])}; granița, comparată la aceeași distanță; populația și "
                  "deschiderea, cu semne opuse între țări și în interiorul lor"),
    ("Tipar și reziduu", "după distanță rămân granița și coridoarele migrației"),
    ("Verificarea", "tiparul nivelurilor se replică la NUTS 3"),
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

sl("s19", "Pe datele noastre", "Fluxul pe SCI",
   "<h2>Fluxul, pe datele noastre, și deciziile pentru C7</h2>"
   + PE_SCI_HTML + FIN_C6,
   manual=
   "<h2>Fluxul, pe datele noastre</h2>"
   "<p>Aceleași etape, pe perechile de regiuni. Fiecare constatare se încheie cu o decizie pentru modelul din C7.</p>"
   + PE_SCI_HTML + FIN_C6)


FISA = [
    ("Profilul", "ce este un rând; câte rânduri, câte ar trebui; un total față de o sursă externă; lipsurile și mecanismul lor; unitățile mici"),
    ("O variabilă", "distribuția variabilei principale: forma, centrul, împrăștierea; scara potrivită"),
    ("Relațiile", "o ipoteză din literatură, cu graficul potrivit tipurilor; o variabilă de confuzie posibilă; nivelul de analiză"),
    ("Tipar și reziduu", "ce rămâne după tiparul cel mai puternic; o excepție care merită explicată"),
    ("Verificarea", "o constatare verificată pe alte date: alt an, alt nivel, altă sursă"),
]
FISA_HTML = ('<div class="q6 q6--fisa">' + "".join(
    f'<div><i>{k}</i><b>{q}</b><span>{c}</span></div>' for k, (q, c) in enumerate(FISA, 1)) + "</div>")
FORM = {
    "id": "c6-fisa", "tip": "fisa", "minim": 80,
    "sarcina": "Primul EDA pe datele echipei: o constatare pentru fiecare etapă a fluxului și o decizie pentru model.",
    "exemplu": "De exemplu: un rând este o pereche de regiuni, 44.253 de perechi; rețelele sociale lipsesc pe țări "
               "întregi; decizie: Svalbard se exclude, SCI pe scara logaritmică.",
    "multumesc": "Fișa a fost înregistrată."}

sl("s20", "Echipa", "Fișa EDA a echipei",
   "<h2>Fișa EDA a echipei</h2>"
   + FISA_HTML
   + ix("asteptari", "Primul EDA al echipei", FORM),
   manual=
   "<h2>Fișa EDA a echipei</h2>"
   "<p>Aceleași etape, pe datele proiectului. Fiecare grafic are o întrebare și o propoziție de interpretare; fiecare "
   "număr spune pe câte cazuri a fost calculat. Fișa intră în <code>README.md</code>, iar caietul care o produce în "
   "<code>notebooks/</code>.</p>"
   + FISA_HTML
   + ix("asteptari", "Primul EDA al echipei", FORM))


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
    ("Robinson (1950): Ecological correlations", "https://www.stats.uwo.ca/faculty/aim/2015/9938/articles/Robinson1950AmericanSociologicalReview.pdf", "corelația pe grupuri față de cea pe indivizi"),
    ("Wainer (2007): The most dangerous equation", "https://sites.stat.washington.edu/people/peter/498.Sp16/Equation.pdf", "numerele mici la ambele capete"),
    ("Bruce, Bruce și Gedeck: Practical Statistics for Data Scientists, cap. 1", "https://oreilly.com/library/view/practical-statistics-for/9781491952955/ch01.html", "locația, variabilitatea, distribuția, corelația"),
    ("Wilke: Fundamentals of Data Visualization, directorul de grafice", "https://clauswilke.com/dataviz/directory-of-visualizations.html", "tipurile de grafice"),
    ("Matejka și Fitzmaurice (2017): Same Stats, Different Graphs", "https://www.research.autodesk.com/publications/same-stats-different-graphs/", "aceleași statistici, alte grafice"),
    ("R for Data Science: Exploratory data analysis", "https://r4ds.hadley.nz/eda.html", "variația, covariația, valorile neobișnuite"),
    ("Peng: Exploratory Data Analysis Checklist", "https://bookdown.org/rdpeng/exdata/exploratory-data-analysis-checklist.html", "verificările de dinainte de grafice"),
    ("seaborn: Overview of plotting functions", "https://seaborn.pydata.org/tutorial/function_overview.html", "funcțiile pentru distribuții, relații, categorii"),
])

sl("s21", "Echipa", "Verificarea în caiet",
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
