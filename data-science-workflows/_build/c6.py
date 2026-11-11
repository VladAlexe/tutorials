# -*- coding: utf-8 -*-
"""
Lecția 6: Analiza exploratorie.

Un curs despre analiza exploratorie, în ordinea fluxului ei: ce este, profilul
datelor, o variabilă numerică, variabilele categorice, două variabile numerice,
trei sau mai multe variabile, tipar și reziduu, verificarea, tipurile de grafice.
Fiecare concept are un grafic interactiv pe date generale (js/eda.js); dedesubt,
o fâșie scurtă „Pe datele noastre” cu același concept pe SCI.

Cifrele SCI vin din date/c6-eda.json, date/c6-ipoteze.json și date/c6-vizual.json,
calculate din tabelele produse de caietele 04-05 (NUTS 2, centrele GISCO NUTS 2024,
EPSG:3035) și, pentru replicare, din baza_completa.db (NUTS 3), la 11 noiembrie 2026.

Rulare:  python _build/c6.py
"""

import json

from comun import Lectie, ix, verif, tabel, nota, surse, RAD

L = Lectie(6, "c6-analiza-exploratorie", "Analiza exploratorie",
           "Analiza exploratorie, în ordinea fluxului ei: profilul datelor, o variabilă, variabile categorice, "
           "două și mai multe variabile, tipar și reziduu, verificarea. Fiecare concept, interactiv, apoi pe datele SCI.")
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
   "concept cu concept, pe exemple generale; fiecare concept se aplică apoi, pe scurt, pe datele SCI.</p>"
   + CURSUL
   + nota("Caietul lecției", f"<code>{_NB6}</code>, în <code>dsw/curs/</code>. Pachete noi: <code>seaborn</code>, "
                             "<code>scipy</code>, toate în <code>requirements.txt</code> (se instalează din nou cu "
                             "<code>pip install -r requirements.txt</code>).", True))


FLUX = (
    '<div class="ed6 ed6--5">'
    '<div><small>1 · profilul datelor</small><b>ce conțin, se poate avea încredere în ele?</b></div>'
    '<div><small>2 · o variabilă</small><b>cum variază: centrul, împrăștierea, forma</b></div>'
    '<div><small>3 · relațiile</small><b>ce variază împreună, în ce grupuri, la ce nivel</b></div>'
    '<div><small>4 · tipar și reziduu</small><b>ce rămâne după tiparul puternic</b></div>'
    '<div class="nou"><small>5 · verificarea</small><b>e tipar sau zgomot? se replică?</b></div>'
    '</div>'
    '<p class="ed6__inapoi">fiecare răspuns ridică o întrebare nouă și reia ciclul</p>')

sl("s2", "Analiza exploratorie", "Scopul și fluxul",
   "<h2>Analiza exploratorie: scopul și fluxul</h2>"
   "<p class=\"cheie\">Să înțelegi datele înainte de a le modela. Tukey: analiza exploratorie formulează acuzarea; "
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
   "ce te aștepți; de aici, ultima etapă: verificarea.</p>"
   + FLUX
   + nota("Întrebarea ascuțită", "Peng (2019): analiza exploratorie ascute întrebarea. O întrebare vagă („ce "
          "legături au regiunile?”) devine una precisă („la aceeași distanță, granița mai contează?”), iar o întrebare "
          "precisă scoate din date mai multă informație.", True))


# ===========================================================================
#  B. Profilul datelor
# ===========================================================================

sl("s3", "Profilul datelor", "Tipurile de variabile",
   "<h2>Ce este un rând și ce fel de variabile are?</h2>"
   + ix("edTipuri", "Tipurile de variabile", {})
   + noi(f"Un rând este o <b>pereche de regiuni</b> ({nr(D['n'])} de perechi), nu o regiune: fiecare dintre cele 298 de "
         "regiuni apare în 297 de perechi. Perechile nu sunt observații independente."),
   manual=
   "<h2>Structura datelor și tipurile de variabile</h2>"
   "<p>Primul pas este <b>unitatea de analiză</b>: ce reprezintă un rând. Apoi tipul fiecărei variabile, care "
   "decide ce rezumat și ce grafic au sens (Stevens, 1946; Bruce și colegii, 2020, cap. 1):</p>"
   + tabel(["Tipul", "Exemplu", "Se rezumă cu", "Graficul"], [
       ["numerică continuă", "vârsta, venitul", "medie, mediană, abatere, cuantile", "histogramă, boxplot, densitate"],
       ["numerică discretă", "numărul de copii", "frecvența fiecărei valori", "bare pe valori"],
       ["categorică ordinală", "nivelul de studii", "frecvențe, mediană; nu media", "bare în ordinea categoriilor"],
       ["categorică nominală", "județul", "frecvențe, moda", "bare ordonate după frecvență"],
       ["binară", "a votat sau nu", "proporția", "o proporție, bare"]])
   + ix("edTipuri", "Tipurile de variabile", {})
   + noi(f"Un rând este o pereche de regiuni: {nr(D['n'])} de perechi din 298 de regiuni, fiecare în 297 de perechi. "
         "De aceea, în caiet nu se fac teste: perechile care au o regiune comună nu sunt independente.")
   + cod("perechi.shape            # (44253, ...)\nperechi.dtypes           # tipul fiecărei coloane\nperechi.head()"))


V_LIPS = verif("c6-v-lips", 1,
               "Venitul lipsește mai des la persoanele în vârstă, iar vârsta e cunoscută. Ce se poate face?",
               ["Nimic: lipsurile deplasează orice medie", "Media pe grupe de vârstă, ponderată, corectează deplasarea",
                "Se șterg persoanele în vârstă", "Media cazurilor complete e corectă"],
               "Când lipsurile depind de o variabilă observată (aleatoare condiționat), media se poate reface pe grupe "
               "ale acelei variabile. Când depind de valoarea lipsă însăși, nicio corecție din date nu ajunge.")

sl("s4", "Profilul datelor", "Lipsurile",
   "<h2>Lipsurile: unde și de ce?</h2>"
   + ix("edLipsuri", "Trei mecanisme ale lipsurilor", {})
   + noi(f"Rețelele sociale lipsesc în toate regiunile Germaniei ({D['lips_rs']['DE']}), Franței ({D['lips_rs']['FR']}) și "
         "Turciei; PIB-ul, în Elveția și Norvegia. Lipsurile depind de țară, adică de sursă: orice rezultat spune pe câte "
         "perechi a fost calculat."),
   manual=
   "<h2>Lipsurile: unde și de ce?</h2>"
   "<p>Numărul de valori lipsă spune puțin; contează mecanismul (Rubin, 1976; Little și Rubin, 2019):</p>"
   + tabel(["Mecanismul", "Lipsa depinde de", "Media cazurilor complete"], [
       ["complet aleator (MCAR)", "nimic", "nedeplasată, doar mai puțin precisă"],
       ["aleator condiționat (MAR)", "o variabilă observată (vârsta)", "deplasată; se poate corecta pe grupe ale acelei variabile"],
       ["neîntâmplător (MNAR)", "valoarea lipsă însăși (venitul mare)", "deplasată; datele singure nu o pot corecta"]])
   + ix("edLipsuri", "Trei mecanisme ale lipsurilor", {})
   + noi(f"Rețelele sociale lipsesc în {D['lips']['retele_sociale']} de regiuni, toate din câteva țări; PIB-ul pe locuitor "
         f"în {D['lips']['pib_locuitor']}. Mecanismul este „aleator condiționat” de țară: o comparație pe cazurile complete "
         "pierde țări întregi.")
   + cod("regiuni.isna().sum()                                     # câte lipsesc, pe coloane\n"
         "regiuni[regiuni[\"retele_sociale\"].isna()][\"tara\"].value_counts()   # unde"),
   dupa=V_LIPS)


sl("s5", "Profilul datelor", "Numerele mici",
   "<h2>De ce unitățile mici sunt la ambele capete ale clasamentului?</h2>"
   + ix("edMici", "300 de unități, aceeași rată", {})
   + noi("Svalbard, cea mai mică regiune, apare atât în cele mai legate perechi, cât și în cele mai puțin legate. În rest, "
         "împrăștierea SCI nu crește la regiunile mici: valorile publicate sunt probabil netezite."),
   manual=
   "<h2>Numerele mici</h2>"
   "<p>O rată calculată pe o populație mică variază mult din întâmplare: abaterea ei standard este "
   "√(p(1−p)/n), deci scade cu rădăcina mărimii. Wainer (2007) o numește „cea mai periculoasă ecuație”: unitățile "
   "mici (școli, județe) apar la ambele capete ale oricărui clasament, iar explicațiile cauzale inventate pentru ele "
   "sunt, de fapt, zgomot. <b>Graficul-pâlnie</b> (Spiegelhalter, 2005) pune rata față de mărime, cu limitele "
   "așteptate din întâmplare.</p>"
   + ix("edMici", "300 de unități, aceeași rată", {})
   + noi("SCI se împarte la produsul numărului de utilizatori din cele două regiuni. Svalbard, cu câteva mii de "
         "locuitori, este la ambele capete ale distribuției și se exclude din model. Verificarea pe celelalte regiuni nu "
         "arată un efect al mărimii: abaterea standard a log-SCI (față de perechile de la aceeași distanță) este 0,63 la "
         "perechile cu cele mai mici regiuni și 0,62 la cele mai mari; la NUTS 3, la fel. Absența unui efect așteptat "
         "este și ea un rezultat.")
   + cod("perechi.nlargest(3, \"sci\")      # extremele, citite una câte una\nperechi.nsmallest(3, \"sci\")"))


# ===========================================================================
#  C. O variabilă numerică
# ===========================================================================

V_REZ = verif("c6-v-rez", 2,
              "Din 40 de valori, 6 sunt mutate foarte departe. Ce statistică rămâne aproape neschimbată?",
              ["Media", "Abaterea standard", "Mediana", "Media trunchiată 10%"],
              "Media cedează la o singură valoare (punctul de cedare 1/n); media trunchiată 10% rezistă până la 4 "
              "valori din 40; mediana, până la jumătate. Același lucru pentru împrăștiere: abaterea standard cedează, "
              "IQR și MAD rezistă.")

sl("s6", "O variabilă numerică", "Centrul, împrăștierea, rezistența",
   "<h2>Centrul și împrăștierea: ce statistici rezistă?</h2>"
   + ix("edRezistenta", "Rezistența la valori extreme", {})
   + noi(f"Media SCI este {nr(S['medie'])}, mediana {nr(S['mediana'])}: de opt ori mai mică. Media trunchiată 10% "
         f"({nr(S['trunchiata10'])}) e aproape de mediană; abaterea standard ({nr(S['sd'])}) e de 24 de ori IQR "
         f"({nr(S['iqr'])})."),
   manual=
   "<h2>Locația, variabilitatea și rezistența</h2>"
   "<p><b>Locația</b> (centrul): media, media trunchiată (fără un procent din fiecare capăt), mediana. "
   "<b>Variabilitatea</b>: abaterea standard, abaterea intercuartilică (IQR, între a 25-a și a 75-a percentilă), "
   "abaterea absolută mediană (MAD). <b>Rezistența</b> este măsura în care câteva valori extreme nu mută rezultatul; "
   "<b>punctul de cedare</b> este proporția de valori care pot fi stricate înainte ca statistica să o ia razna: 1/n "
   "pentru medie și abaterea standard, 10% pentru media trunchiată 10%, 50% pentru mediană și MAD (Velleman și "
   "Hoaglin, 1981; Bruce și colegii, 2020).</p>"
   + ix("edRezistenta", "Rezistența la valori extreme", {})
   + tabel(["SCI", "Valoarea"], [["media", nr(S["medie"])], ["media fără Svalbard", nr(S["medie_fara_svalbard"])],
                                 ["media trunchiată 10%", nr(S["trunchiata10"])], ["mediana", nr(S["mediana"])],
                                 ["abaterea standard", nr(S["sd"])], ["IQR", nr(S["iqr"])], ["MAD", nr(S["mad"])]])
   + cod("from scipy import stats\n"
         "perechi[\"sci\"].describe()\n"
         "stats.trim_mean(perechi[\"sci\"], 0.1)            # media trunchiată 10%\n"
         "stats.median_abs_deviation(perechi[\"sci\"])       # MAD"),
   dupa=V_REZ)


sl("s7", "O variabilă numerică", "Distribuția",
   "<h2>Aceleași date, cinci grafice</h2>"
   + ix("edDistributie", "Distribuția unei variabile", {"sci": D["esantion"]})
   + noi("Fila „SCI (log10)” arată 3.000 de perechi alese la întâmplare: pe scara logaritmică, o singură cocoașă, "
         "cu o coadă spre valorile mari."),
   manual=
   "<h2>Distribuția: cinci grafice pentru aceleași date</h2>"
   "<p>Histograma depinde de două alegeri, lățimea barelor și locul unde încep; cu alte alegeri, aceleași date pot "
   "arăta o cocoașă sau două (McNamara și Lunzer). <b>Densitatea</b> netezește histograma, iar lățimea netezirii "
   "joacă același rol. <b>ECDF</b> (funcția de distribuție empirică) nu cere nicio alegere: pentru fiecare valoare x, "
   "proporția valorilor ≤ x; cuantilele se citesc direct. <b>Boxplotul</b> rezumă în cuartile și ascunde forma "
   "(două cocoașe pot da aceeași cutie); <b>violinul cu puncte</b> arată și forma, și datele.</p>"
   + ix("edDistributie", "Distribuția unei variabile", {"sci": D["esantion"]})
   + cod("sns.histplot(perechi, x=\"sci\", log_scale=True, bins=40)\n"
         "sns.kdeplot(perechi, x=\"sci\", log_scale=True, bw_adjust=0.5)\n"
         "sns.ecdfplot(perechi, x=\"sci\", log_scale=True)\n"
         "sns.boxplot(perechi, x=\"sci\", log_scale=True)\n"
         "sns.violinplot(perechi, x=\"sci\", log_scale=True)"))


sl("s8", "O variabilă numerică", "Forma și reexprimarea",
   "<h2>Asimetria și reexprimarea</h2>"
   + ix("edReexprimare", "Scara puterilor lui Tukey", {"sci": D["esantion"]})
   + noi("SCI se întinde pe șase ordine de mărime. Pe scara log10 devine aproape simetric; de aici înainte, SCI se "
         "citește pe această scară, iar comparațiile folosesc mediana."),
   manual=
   "<h2>Forma și reexprimarea</h2>"
   "<p>O distribuție cu <b>asimetrie pozitivă</b> (coada spre dreapta) are media peste mediană. <b>Reexprimarea</b> "
   "înlocuiește valorile cu o funcție a lor care păstrează ordinea. Scara puterilor lui Tukey (x, √x, log x, −1/√x, "
   "−1/x) merge de la transformări slabe la tari: cu cât coada e mai lungă, cu atât trebuie urcat mai sus pe scară. "
   "Logaritmul are un avantaj de interpretare: diferențele devin rapoarte („de 10 ori mai mult”). Reexprimarea "
   "face distribuțiile mai simetrice, stabilizează împrăștierea și îndreaptă relațiile curbe (Velleman și Hoaglin, "
   "1981).</p>"
   + ix("edReexprimare", "Scara puterilor lui Tukey", {"sci": D["esantion"]})
   + cod("np.log10(perechi[\"sci\"]).skew()        # asimetria după transformare\n"
         "sns.histplot(perechi, x=\"sci\", log_scale=True)"))


# ===========================================================================
#  D. Variabile categorice
# ===========================================================================

_K = VZ["contingenta"]
CONT_SCI = {"r": [t.replace("peste 2000", "2000+") for t in _K["intervale"]], "c": ["aceeași țară", "țări diferite"],
            "v": [[a, b] for a, b in zip(_K["da"], _K["nu"])], "er": "distanța, km", "ec": "perechea"}
_P100 = _K["da"][0] / (_K["da"][0] + _K["nu"][0])

sl("s9", "Variabile categorice", "Tabelul de contingență",
   "<h2>Frecvențe, proporții, tabelul de contingență</h2>"
   + ix("edContingenta", "Două variabile categorice", {"sci": CONT_SCI})
   + noi(f"Fila „SCI”: sub 100 km, {_P100:.0%} din perechi sunt în aceeași țară; peste 1.000 km, sub 1%. Granița și "
         "distanța merg împreună."),
   manual=
   "<h2>Frecvențe, proporții, tabelul de contingență</h2>"
   "<p>Pentru o variabilă categorică: frecvențele și proporțiile, ca bare ordonate. Pentru două: <b>tabelul de "
   "contingență</b>, câte rânduri are fiecare combinație. Procentele se calculează pe direcția întrebării: pe rând "
   "(dintre cei din mediul urban, câți au studii superioare?) sau pe coloană (dintre cei cu studii superioare, câți "
   "sunt din mediul urban?). Barele stivuite 100% arată distribuțiile condiționate; <b>mozaicul</b> arată în plus, prin "
   "lățime, mărimea fiecărui grup.</p>"
   + ix("edContingenta", "Două variabile categorice", {"sci": CONT_SCI})
   + cod("pd.crosstab(perechi[\"interval_km\"], perechi[\"aceeasi_tara\"])                      # numere\n"
         "pd.crosstab(perechi[\"interval_km\"], perechi[\"aceeasi_tara\"], normalize=\"index\")   # % pe rând"))


# ===========================================================================
#  E. Două variabile numerice
# ===========================================================================

V_COR = verif("c6-v-cor", 3,
              "Relația dintre distanță și SCI e puternică, dar curbă, cu câteva valori uriașe. Pearson pe valorile brute "
              f"dă {ro(S['pearson_brut'])}. Ce se poate spune?",
              ["Relația e slabă", "Nu există relație", "Distanța nu contează",
               "Pearson măsoară relația liniară și e tras de extreme; Spearman sau Pearson pe log arată relația"],
              f"Pe valorile brute, Pearson = {ro(S['pearson_brut'])}; pe log-log, {ro(S['pearson_log'])}; Spearman, "
              f"{ro(S['spearman'])}; Kendall, {ro(S['kendall'])}. Coeficientul se alege după forma relației, văzută "
              "întâi pe grafic.")

sl("s10", "Două variabile numerice", "Corelația",
   "<h2>Pearson, Spearman, Kendall: ce măsoară fiecare?</h2>"
   + ix("edCorelatie", "Trei coeficienți de corelație", {})
   + noi(f"Distanța și SCI: Pearson pe valorile brute {ro(S['pearson_brut'])}, pe log-log {ro(S['pearson_log'])}; "
         f"Spearman {ro(S['spearman'])}; Kendall {ro(S['kendall'])}. Aceeași relație, patru numere."),
   manual=
   "<h2>Corelația: Pearson, Spearman, Kendall</h2>"
   + tabel(["Coeficientul", "Măsoară", "Sensibil la"], [
       ["Pearson r", "relația liniară", "valori extreme, curbură"],
       ["Spearman ρ", "relația monotonă (Pearson pe ranguri)", "puțin; nu vede relațiile ne-monotone"],
       ["Kendall τ", "perechile de observații în aceeași ordine, minus cele în ordine inversă, ca proporție",
        "puțin; valori mai mici decât ρ, cu interpretare directă"]])
   + "<p>Niciunul nu vede o relație în U: o corelație aproape zero nu înseamnă lipsa relației. Coeficientul nu ține "
     "locul graficului: întâi forma relației, apoi numărul potrivit ei.</p>"
   + ix("edCorelatie", "Trei coeficienți de corelație", {})
   + noi(f"Pe cele {nr(D['n'])} de perechi: Pearson brut {ro(S['pearson_brut'])}, pe log-log {ro(S['pearson_log'])}, "
         f"Spearman {ro(S['spearman'])}, Kendall {ro(S['kendall'])}. Pearson pe valorile brute subestimează relația, "
         "pentru că e curbă și are valori uriașe; reexprimarea o face aproape liniară.")
   + cod("for m in [\"pearson\", \"spearman\", \"kendall\"]:\n"
         "    print(m, perechi[\"distanta_km\"].corr(perechi[\"sci\"], method=m))\n"
         "np.log10(perechi[\"distanta_km\"]).corr(np.log10(perechi[\"sci\"]))     # Pearson pe log-log"),
   dupa=V_COR)


sl("s11", "Două variabile numerice", "Graficul înaintea coeficientului",
   "<h2>Aceleași statistici, alte grafice; prea multe puncte</h2>"
   + ix("edAnscombe", "Anscombe și suprapunerea", {})
   + noi(f"{nr(D['n'])} de perechi: un grafic de dispersie devine o pată. Pentru distanță și SCI, graficul potrivit este "
         "histograma bidimensională sau medianele pe intervale de distanță."),
   manual=
   "<h2>Graficul înaintea coeficientului</h2>"
   "<p>Cele patru seturi ale lui Anscombe (1973) au aceeași medie, aceeași varianță, aceeași corelație și aceeași "
   "dreaptă de regresie; graficele lor sunt complet diferite: o relație liniară, una curbă, una perfectă cu o "
   "valoare extremă, una determinată de un singur punct. Matejka și Fitzmaurice (2017) au generalizat ideea: oricât "
   "de multe statistici se potrivesc, graficul poate fi altul.</p>"
   "<p>Cu foarte multe observații apare problema inversă: punctele se acoperă (suprapunere). Soluțiile: "
   "transparența, histograma bidimensională sau hexbin (căsuțe colorate după număr), medianele și cuartilele pe "
   "intervale ale lui x.</p>"
   + ix("edAnscombe", "Anscombe și suprapunerea", {})
   + cod("sns.lmplot(anscombe, x=\"x\", y=\"y\", col=\"setul\")       # valorile sunt scrise în caiet\n"
         "sns.histplot(perechi, x=\"distanta_km\", y=\"sci\", log_scale=True, bins=50)   # histograma 2D"))


sl("s12", "Două variabile numerice", "Lineup",
   "<h2>Graficul e o comparație: e tipar sau zgomot?</h2>"
   + ix("edLineup", "Graficul real, printre grafice permutate", {"regiuni": S["regiuni"]})
   + noi("Rundele SCI: „deschiderea” fiecărei regiuni spre străinătate (SCI cu regiunile din alte țări, față de ce ar "
         "da distanța), față de longitudine și față de populație. Primul tipar se recunoaște; al doilea, nu."),
   manual=
   "<h2>Graficul e o comparație cu ce te aștepți</h2>"
   "<p>Orice grafic exploratoriu se citește față de un model implicit: „fără relație”, „distribuție normală” "
   "(Gelman, 2004; Hullman și Gelman, 2021). Ochiul găsește tipare și în zgomot. <b>Protocolul lineup</b> (Buja și "
   "colegii, 2009) face comparația explicită: graficul real se ascunde între grafice în care valorile unei variabile "
   "au fost amestecate (permutate), ceea ce distruge relația dar păstrează distribuțiile. Dacă graficul real se "
   "recunoaște, tiparul e puțin probabil să fie zgomot; cu 8 grafice, șansa de a-l nimeri la întâmplare este 1 din "
   "8; cu 20, 1 din 20, echivalentul unui prag de 0,05.</p>"
   + ix("edLineup", "Graficul real, printre grafice permutate", {"regiuni": S["regiuni"]})
   + cod("permutat = regiuni.copy()\n"
         "permutat[\"deschidere\"] = np.random.permutation(permutat[\"deschidere\"])   # relația distrusă"))


# ===========================================================================
#  F. Trei sau mai multe variabile
# ===========================================================================

_H2 = D["h2"]
_I = _H2["intervale"].index("250-500")
_R = _H2["da"]["med"][_I] / _H2["nu"]["med"][_I]

sl("s13", "Trei sau mai multe variabile", "Categoric × numeric",
   "<h2>Grupuri comparate: ce ascunde bara cu media?</h2>"
   + ix("edGrupuri", "O variabilă numerică pe grupuri", {})
   + noi(f"Aceeași țară sau nu și SCI, pe intervale de distanță: la 250-500 km, mediana perechilor din aceeași țară este "
         f"de {_R:.0f} ori mai mare. Comparația se face la aceeași distanță, pentru că perechile din aceeași țară sunt și "
         "mai apropiate: distanța este o variabilă de confuzie."),
   manual=
   "<h2>Categoric × numeric</h2>"
   "<p>Bara cu media și eroarea ei ascunde distribuția: o grupă simetrică, una cu două cocoașe, una asimetrică și una "
   "cu șase observații pot avea bare aproape egale. Boxploturile, violinele și punctele pe grupuri arată ce ascunde "
   "media; cu grupuri mici, punctele însele.</p>"
   + ix("edGrupuri", "O variabilă numerică pe grupuri", {})
   + cod("sns.boxplot(perechi, x=\"interval_km\", y=\"sci\", hue=\"aceeasi_tara\", log_scale=True)\n"
         "sns.violinplot(perechi, x=\"interval_km\", y=\"sci\", hue=\"aceeasi_tara\", log_scale=True)"))


_NV = S["nivele"]
V_NIV = verif("c6-v-niv", 1,
              f"Între țări, populația și deschiderea au ρ = {ro(_NV['intre'])}; în interiorul țărilor, {ro(_NV['in'])}. "
              "Ce afirmație e corectă?",
              ["Regiunile mari sunt mai închise", "În aceeași țară, regiunile mari (capitalele) tind să fie mai deschise",
               "Populația nu are legătură cu deschiderea", "Corelația totală spune tot"],
              "Relația dintre țări și relația din interiorul țărilor răspund la întrebări diferite. Corelația totală "
              f"({ro(_NV['total'])}) le amestecă și se anulează. O concluzie despre regiuni nu se trage din corelația "
              "dintre țări (eroarea ecologică).")

sl("s15", "Trei sau mai multe variabile", "Nivelul de analiză",
   "<h2>Între grupuri, în interiorul lor, total</h2>"
   + ix("edNivele", "Nivelul de analiză", {"regiuni": S["regiuni"]})
   + noi(f"Fila „SCI”: populația regiunii și deschiderea ei spre străinătate. Între țări, ρ = {ro(_NV['intre'])} (țările "
         f"mici, mai deschise); în interiorul țărilor, {ro(_NV['in'])} (capitalele, mai deschise); total, "
         f"{ro(_NV['total'])}. La NUTS 3, la fel: −0,15 total, +0,44 în interiorul țărilor."),
   manual=
   "<h2>Nivelul de analiză: eroarea ecologică</h2>"
   "<p>Robinson (1950) a comparat, pe recensământul american din 1930, corelația dintre a fi născut în străinătate și "
   "analfabetism: pe indivizi, 0,118; pe state, −0,526. Semnul se inversează. O corelație calculată pe grupuri "
   "(state, țări) nu spune nimic sigur despre unitățile din interiorul lor: <b>eroarea ecologică</b>. Pe date "
   "grupate, trei relații pot fi diferite: cea dintre grupuri (mediile lor), cea din interiorul grupurilor și cea "
   "totală, care le amestecă. Rezultatul depinde și de cum sunt trasate grupurile: <b>problema unității areale "
   "modificabile</b>.</p>"
   + ix("edNivele", "Nivelul de analiză", {"regiuni": S["regiuni"]})
   + noi(f"„Deschiderea” unei regiuni: mediana SCI cu regiunile din alte țări, fiecare raportată la mediana perechilor "
         f"de la aceeași distanță. Față de populație: ρ = {ro(_NV['intre'])} între țări, {ro(_NV['in'])} mediana din "
         f"interiorul celor {_NV['n_tari']} țări cu cel puțin 5 regiuni, {ro(_NV['total'])} pe total. Tiparul se replică "
         "la NUTS 3 (1.323 de regiuni): −0,15 total, +0,44 în interiorul țărilor.")
   + cod("tari = regiuni.groupby(\"tara\")[[\"populatie\", \"deschidere\"]].median()\n"
         "tari[\"populatie\"].corr(tari[\"deschidere\"], method=\"spearman\")      # între țări\n"
         "regiuni.groupby(\"tara\")[[\"populatie\", \"deschidere\"]].corr(method=\"spearman\")   # în fiecare țară"),
   dupa=V_NIV)


sl("s16", "Trei sau mai multe variabile", "Multe variabile",
   "<h2>Multe variabile: culoare, fațete, matrice</h2>"
   + ix("edMultivar", "Matricea de grafice și matricea de corelație", {"cor": VZ["cor"]})
   + noi("Fila „SCI”: șase indicatori ai regiunilor. PIB-ul merge cu studiile și cu densitatea: într-un model, "
         "predictori puternic corelați se separă greu (multicoliniaritate)."),
   manual=
   "<h2>Multe variabile</h2>"
   "<p>O a treia variabilă intră în grafic ca <b>culoare</b> (<code>hue=</code>) sau ca <b>fațete</b>, același grafic "
   "repetat pe grupuri, cu aceleași axe (<code>col=</code>). Pentru mai multe variabile numerice: <b>matricea de "
   "grafice</b> (fiecare pereche, cu distribuțiile pe diagonală) și <b>matricea de corelație</b>, cu o scară de "
   "culori divergentă, centrată pe 0.</p>"
   + ix("edMultivar", "Matricea de grafice și matricea de corelație", {"cor": VZ["cor"]})
   + cod("sns.pairplot(regiuni[indicatori])\n"
         "sns.heatmap(regiuni[indicatori].corr(method=\"spearman\"), annot=True, cmap=\"RdBu_r\", vmin=-1, vmax=1)"))


# ===========================================================================
#  G. Tipar și reziduu
# ===========================================================================

sl("s17", "Tipar și reziduu", "Date = tipar + reziduu",
   "<h2>Scoate tiparul puternic, privește ce rămâne</h2>"
   + ix("edReziduu", "Tipar și reziduu", {"perechi": S["perechi"]})
   + noi("Fila „SCI”: log SCI față de log distanță, pe 1.500 de perechi. După dreaptă, reziduurile perechilor din aceeași "
         "țară (portocaliu) sunt aproape toate pozitive: granița, văzută în ce rămâne după distanță."),
   manual=
   "<h2>Date = tipar + reziduu</h2>"
   "<p>Tukey: datele sunt un tipar plus un rest. Odată găsit tiparul puternic, se scoate cu un model simplu, iar în "
   "<b>reziduuri</b> apar tiparele mai fine (Wickham și colegii, <i>R for Data Science</i>, exemplul diamantelor: "
   "calitatea pare să scadă prețul până se ține cont de mărime). Un grafic al reziduurilor fără structură înseamnă că "
   "tiparul prinde tot; o curbă sau grupuri în reziduuri arată ce lipsește din el.</p>"
   + ix("edReziduu", "Tipar și reziduu", {"perechi": S["perechi"]})
   + noi("Pe SCI, tiparul puternic este distanța. Reziduurile față de ea, pe hartă: pentru Nord-Vest, Spania și Irlanda "
         "de zeci de ori peste; la nivelul județelor României, Suceava, Iași, Botoșani și Vaslui sunt cele mai deschise "
         "spre străinătate față de distanță, Teleorman, Covasna și Harghita cele mai puțin. Modelul din C7 face același "
         "lucru, cu mai multe variabile.")
   + cod("panta, nivel = np.polyfit(np.log10(perechi[\"distanta_km\"]), np.log10(perechi[\"sci\"]), 1)\n"
         "perechi[\"reziduu\"] = np.log10(perechi[\"sci\"]) - (nivel + panta * np.log10(perechi[\"distanta_km\"]))\n"
         "perechi.groupby(\"aceeasi_tara\")[\"reziduu\"].median()"))


# ===========================================================================
#  H. Verificarea
# ===========================================================================

V_POT = verif("c6-v-pot", 1,
              "Din 40 de variabile de zgomot pur, cea mai mare corelație între ele este 0,6. Ce înseamnă?",
              ["Cele două variabile sunt legate", "Nimic: printre 780 de perechi, o corelație mare apare din întâmplare",
               "Eșantionul e prea mare", "Trebuie folosit Spearman"],
              "Cu cât se fac mai multe comparații, cu atât cea mai bună dintre ele e mai mare din întâmplare. Ce se "
              "găsește explorând se verifică pe alte date.")

sl("s18", "Verificarea", "Grădina potecilor",
   "<h2>Cu cât cauți mai mult, cu atât găsești</h2>"
   + ix("edPoteci", "Corelații în zgomot pur", {})
   + noi("Lecția a calculat zeci de corelații. Ce s-a găsit la NUTS 2 (populația și deschiderea) s-a verificat pe alte "
         "date, la NUTS 3: tiparul se replică. Celelalte constatări rămân ipoteze pentru modelul din C7."),
   manual=
   "<h2>Grădina potecilor care se bifurcă</h2>"
   "<p>O analiză exploratorie are multe alegeri posibile: ce variabile, ce subgrupe, ce transformări, ce excepții. "
   "Gelman și Loken numesc asta grădina potecilor care se bifurcă: chiar fără intenție, dintre multe comparații "
   "posibile, cea mai interesantă este supraestimată. Cu k variabile sunt k(k−1)/2 perechi; în zgomot pur, 5% dintre "
   "ele trec de pragul obișnuit. Hullman și Gelman (2021) recomandă ca ce se găsește explorând să fie verificat pe "
   "date păstrate deoparte: alt an, alt nivel de agregare, altă sursă.</p>"
   + ix("edPoteci", "Corelații în zgomot pur", {})
   + cod("zgomot = pd.DataFrame(np.random.normal(size=(30, 40)))\n"
         "c = zgomot.corr().abs().where(~np.eye(40, dtype=bool))\n"
         "c.max().max()                      # cea mai mare corelație, din întâmplare"),
   dupa=V_POT)


# ===========================================================================
#  I. Încheierea
# ===========================================================================

sl("s19", "Încheierea", "Tipurile de grafice",
   "<h2>Ce grafic, pentru ce date</h2>"
   + ix("edTipGrafice", "Tipurile de grafice, după Wilke", {})
   + "<p class=\"cub__regula\">Un grafic bun: o idee, spusă în titlu; scara spusă pe axă; culoarea după date "
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
    ("Profilul", "un rând = o pereche; Svalbard instabil (numerele mici); lipsurile pe țări întregi"),
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

sl("s20", "Pe datele noastre", "Fluxul pe SCI",
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

sl("s21", "Echipa", "Fișa EDA a echipei",
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

sl("s22", "Echipa", "Verificarea în caiet",
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
