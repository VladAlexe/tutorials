# -*- coding: utf-8 -*-
"""
Lecția 4: Curățarea și integrarea datelor.

Urmează caietul 04_curatarea_si_integrarea_datelor.ipynb, secțiune cu
secțiune, pe datele cursului (tabelele din C3, citite din depozitul
cursului). Din prezentarea Curs_4.pptx (2025) au rămas cele șase etape ale
curățării, ca hartă a lecției, și o recapitulare scurtă de Git; restul de Git
s-a făcut la C3 și stă în fișa „Lucrul cu Git”.

Ce am lăsat deliberat în afară:
  - valorile extreme cu prag IQR: țin de explorare (C6), unde lucrăm cu
    distribuțiile; aici rămân valorile imposibile sau neobișnuite;
  - completarea lipsurilor ca procedură (ffill, interpolare): la datele
    noastre decizia este să nu completăm; fillna și dropna apar doar ca
    demonstrație a ceea ce s-ar pierde.

Rulare:  python _build/c4.py
"""

from comun import Lectie, ix, verif, tabel, nota, surse

L = Lectie(4, "c4-curatarea-datelor", "Curățarea și integrarea datelor",
           "Profilarea, tipurile, duplicatele, valorile imposibile, lipsurile și codurile, "
           "apoi integrarea tabelelor și validarea finală, pe datele cursului.")
sl = L.sl

CAIET = "<code>04_curatarea_si_integrarea_datelor.ipynb</code>"
FISA = '<a class="leg" href="../../c3-versionare-git/git/">Lucrul cu Git</a>'
ET_VERIF = '<p class="ex-et">Verificare</p>'   # pe slide, deasupra exercițiului


def metode(randuri):
    """Metodele folosite în exercițiu, explicate înaintea lui: ce face fiecare și cum se scrie."""
    return tabel(["Metoda", "Ce face"], [r[:2] for r in randuri])


# ===========================================================================
#  1. Recapitulare Git
# ===========================================================================

FLUX_SCURT = tabel(["Când", "Comenzile"], [
    ["la începutul lucrului", "~git switch dev ; git pull"],
    ["după un pas încheiat", "~git add fisier ; git commit -m \"mesaj\" ; git pull ; git push"],
    ["o greșeală înainte de commit", "~git restore fisier ; git restore --staged fisier"],
    ["un commit greșit, deja publicat", "~git revert &lt;cod&gt;"],
])

FLUX_ZI = tabel(["Când", "Comenzile", "Ce fac"], [
    ["la începutul lucrului", "~git switch dev ; git pull", "ramura de lucru, la zi cu colegii"],
    ["după un pas încheiat", "~git add fisier ; git commit -m \"mesaj\"", "pasul intră în istoric"],
    ["imediat după", "~git pull ; git push", "întâi ce au trimis colegii, apoi trimiterea proprie"],
    ["o modificare greșită, înainte de add", "~git restore fisier", "fișierul revine la ultimul commit"],
    ["un add greșit", "~git restore --staged fisier", "fișierul iese din pregătire; modificarea rămâne"],
    ["un commit greșit, deja publicat", "~git revert &lt;cod&gt;", "un commit nou care îl anulează; istoricul colegilor rămâne intact"],
])

V_RESTORE = verif("c4-v1", 1,
    "Ai modificat din greșeală caietul echipei și încă nu ai dat <code>git add</code>. "
    "Cum revii la versiunea din ultimul commit?",
    ["git restore --staged caiet.ipynb", "git restore caiet.ipynb",
     "git revert caiet.ipynb", "git rm caiet.ipynb"],
    "<code>git restore</code> aduce fișierul la starea din ultimul commit. Varianta cu "
    "<code>--staged</code> doar îl scoate din pregătire, <code>revert</code> lucrează cu commit-uri, "
    "nu cu fișiere, iar <code>git rm</code> l-ar scoate din depozit.")

sl("s1", "Recapitulare", "Git, pe scurt",
   "<h2>Git, pe scurt: lucrul zilnic pe dev</h2>"
   "<p class=\"cheie\">Din C3: <code>pull</code> la început, <code>commit</code> și <code>push</code> după fiecare pas. "
   "Nou azi: cum se anulează o greșeală.</p>"
   + FLUX_SCURT + V_RESTORE,
   manual=
   "<h2>Git, pe scurt: lucrul zilnic pe dev</h2>"
   "<p>Lecția 3 a introdus depozitul echipei și ramura <code>dev</code>. De aici încolo, Git devine un obicei de "
   "lucru, nu un subiect separat: fiecare pas al proiectului se încheie cu un commit pe <code>dev</code>. Tabelul "
   "rezumă ciclul zilnic și adaugă cele trei anulări de care este nevoie cel mai des.</p>"
   + FLUX_ZI
   + "<p>Cele trei anulări lucrează la niveluri diferite. <code>git restore</code> și "
     "<code>git restore --staged</code> lucrează la nivel de fișier, înainte de commit. <code>git revert</code> "
     "lucrează la nivel de commit și este singura variantă sigură după publicare, pentru că adaugă un commit nou în "
     "loc să rescrie istoricul pe care colegii l-au preluat deja.</p>"
   + V_RESTORE
   + nota("Toate comenzile", f"Fișa {FISA}, din lecția 3.", True))


# ===========================================================================
#  2. Planul: ce este curățarea
# ===========================================================================

ETAPE = tabel(["Etapa", "Întrebarea", "În caiet"], [
    ["Profilarea", "ce conține tabelul?", "2. <code>info</code>, <code>value_counts</code>"],
    ["Tipurile", "numerele sunt numere, codurile sunt text?", "3. <code>dtypes</code>, <code>to_numeric</code>"],
    ["Duplicatele", "apare aceeași cheie de două ori?", "4. <code>duplicated</code>, <code>drop_duplicates</code>"],
    ["Valorile imposibile", "există procente peste 100, valori neobișnuite?", "5. <code>describe</code>, <code>nsmallest</code>"],
    ["Lipsurile", "ce înseamnă „lipsă”, câte lipsesc și unde?", "6. <code>isna</code>, <code>count</code>"],
    ["Codurile", "aceeași țară are același cod peste tot?", "7. <code>replace</code>"],
    ["Transformarea și integrarea", "cum ajungem la tabelul de analiză?", "8-11. <code>pivot</code>, <code>merge</code>"],
    ["Validarea", "tabelul final respectă regulile lui?", "12. o celulă de verificări"],
])

sl("s2", "Cursul", "Planul lecției",
   "<h2>Curățarea și integrarea datelor</h2>"
   "<p class=\"cheie\">În C3, sursele au primit aceeași formă. Azi verificăm dacă valorile sunt corecte, complete "
   "și comparabile, apoi unim tabelele.</p>"
   + ETAPE
   + nota("Caietul lecției", f"{CAIET}. Tabelele din C3 se citesc din depozitul cursului, ca toți să lucreze pe aceleași date.", True),
   manual=
   "<h2>Curățarea și integrarea datelor</h2>"
   "<p>Preprocesarea (C3) a adus sursele la o structură comună: coloanele necesare, denumiri consecvente, unitatea "
   "de analiză corectă. Curățarea pune o întrebare diferită: dacă valorile din această structură sunt corecte, "
   "complete și comparabile între surse. Integrarea unește apoi tabelele într-un tabel de analiză.</p>"
   "<p>Etapele urmează o ordine stabilă, pentru că fiecare presupune rezultatele celei anterioare: profilarea "
   "precede orice decizie, codurile se aliniază înainte de unire, iar validarea încheie procesul. Tabelul leagă "
   "fiecare etapă de secțiunea caietului în care este aplicată.</p>"
   + ETAPE
   + nota("Cât timp ocupă curățarea",
          "O estimare citată frecvent (CrowdFlower, 2016) atribuie curățării și organizării datelor aproximativ 60% "
          "din timpul unui proiect. Cifra provine dintr-un sondaj comercial, nu dintr-un studiu riguros, și trebuie "
          "citită ca ordin de mărime: curățarea ocupă o parte importantă a muncii, iar deciziile luate acum "
          "determină validitatea tuturor rezultatelor ulterioare.")
   + nota("Caietul lecției", f"{CAIET}. Tabelele din C3 se citesc din depozitul cursului, ca toți să lucreze pe aceleași date.", True))


# ===========================================================================
#  3. Profilarea
# ===========================================================================

PAS_PROFIL = {
    "fisier": "04_curatarea_si_integrarea_datelor.ipynb · 2. Profilarea",
    "intro": "Înaintea oricărei decizii, tabelul se descrie: dimensiunea, tipurile, valorile prezente și valorile distincte.",
    "cod": "indicatori = pd.read_csv(DATE_C3 + \"indicatori.csv\")\n\n"
           "indicatori.info()\n\n"
           "indicatori[\"indicator\"].value_counts()\n\n"
           "indicatori[\"regiune\"].str.len().value_counts()",
    "pasi": [
        {"l": 1, "set": {"indicatori": {"t": "DataFrame", "v": {"cols": ["regiune", "valoare", "indicator"],
            "rows": [["BE10", 1264371.0, "populatie"], ["BE21", 1932876.0, "populatie"], ["…", "…", "…"]],
            "nota": "format lung: un rând pe regiune și indicator"}}},
         "txt": "Tabelul salvat în C3, citit din depozitul cursului. Un rând este identificat de <b>regiune + indicator</b>."},
        {"l": 3, "out": "RangeIndex: 2281 entries, 0 to 2280\n #   Column     Non-Null Count  Dtype\n 0   regiune    2281 non-null   object\n 1   valoare    1893 non-null   float64\n 2   indicator  2281 non-null   object",
         "txt": "<code>info()</code>: 2.281 de rânduri, dar doar 1.893 de valori în <code>valoare</code>. Diferența, 388, sunt valori lipsă."},
        {"l": 5, "out": "varsta_medie         354\nstudii_superioare    351\nsomaj                351\npopulatie            350\ndensitate            340\npib_locuitor         309\nretele_sociale       226",
         "txt": "<code>value_counts()</code> numără fiecare valoare distinctă. Indicatorii acoperă între 226 și 354 de regiuni: lipsurile nu sunt distribuite uniform."},
        {"l": 7, "out": "4    2281",
         "txt": "Lungimea codului indică nivelul (C3). Toate codurile au 4 caractere, deci tabelul conține doar regiuni NUTS 2."},
    ],
}

M_PROFIL = metode([
    ["~info()", "rezumatul tabelului: rânduri, coloane, tipuri, câte valori are fiecare coloană", "<code>indicatori.info()</code>"],
    ["~value_counts()", "de câte ori apare fiecare valoare dintr-o coloană", "<code>indicatori[\"indicator\"].value_counts()</code>"],
    ["~str.len()", "lungimea fiecărui text dintr-o coloană", "<code>indicatori[\"regiune\"].str.len()</code>"],
])

COD_PROFIL = {
    "id": "c4-cod-profil", "fisier": "04_curatarea.ipynb",
    "sarcina": "Trei întrebări de pus oricărui tabel nou, înainte de orice modificare.",
    "cod": "# 1. ce coloane, ce tipuri, cate valori are fiecare\n"
           "indicatori.{{1}}()\n\n"
           "# 2. de cate ori apare fiecare indicator\n"
           "indicatori[\"indicator\"].{{2}}()\n\n"
           "# 3. ce lungime au codurile regiunilor\n"
           "indicatori[\"regiune\"].str.{{3}}().value_counts()",
    "goluri": {
        "1": {"ok": ["info"], "ajutor": "metoda"},
        "2": {"ok": ["value_counts"], "ajutor": "metoda"},
        "3": {"ok": ["len"], "ajutor": "metoda"}},
    "iesire": "RangeIndex: 2281 entries\n...\nvarsta_medie    354\n...\n4    2281",
    "indiciu": "Rezumatul pe coloane înseamnă „informații”. Numărarea valorilor distincte este value_counts. "
               "Lungimea unui text se obține cu metoda len, din grupul .str.",
    "laBine": "Cele trei rezultate descriu tabelul fără să-l modifice.",
    "laRau": "Toate trei sunt metode: se scriu fără ghilimele.",
    "explicatie": "<code>info()</code> arată lipsurile pe coloane, <code>value_counts()</code> arată distribuția unei "
                  "coloane categoriale, iar <code>str.len()</code> verifică forma codurilor. Împreună răspund la "
                  "prima întrebare a curățării: ce conține tabelul."}

M_PRIVIRE = tabel(["Metoda", "Ce arată", "La noi"], [
    ["~shape", "(rânduri, coloane); atribut, fără paranteze", "~(2281, 3)"],
    ["~columns", "numele coloanelor", "~regiune, valoare, indicator"],
    ["~head(), tail()", "primele, ultimele 5 rânduri (sau câte cerem)", "<code>BE10</code> … <code>RS22</code>"],
    ["~describe()", "minim, medie, cuartile, maxim pe coloanele numerice", "o populație minimă de 0"],
    ["~nunique()", "câte valori distincte are fiecare coloană", "385 de regiuni, 7 indicatori"],
    ["~unique()", "care sunt valorile distincte", "numele celor 7 indicatori"],
    ["~value_counts(normalize=True)", "proporții în loc de număr de rânduri", "varsta_medie 0,155"],
])

COD_PRIVIRE = ("<pre><code>indicatori.shape                  <span class=\"c\"># (2281, 3)</span>\n"
               "indicatori.head()                 <span class=\"c\"># primele 5 rânduri</span>\n"
               "indicatori.nunique()              <span class=\"c\"># regiune 385, valoare 1282, indicator 7</span>\n"
               "nume.describe(include=\"object\")  <span class=\"c\"># 1.971 coduri distincte, dar doar 1.879 nume</span></code></pre>")

sl("s3a", "Profilarea", "Prima privire",
   "<h2>Prima privire asupra unui tabel</h2>"
   + M_PRIVIRE + COD_PRIVIRE,
   manual=
   "<h2>Prima privire asupra unui tabel</h2>"
   "<p>Primele întrebări puse unui tabel nou sunt descriptive: cât de mare este, ce coloane are, cum arată primele "
   "și ultimele rânduri și câte valori distincte are fiecare coloană. Metodele de mai jos nu modifică tabelul; ele "
   "se pot rula oricând, de oricâte ori, și sunt primul lucru de făcut după fiecare citire sau unire.</p>"
   + M_PRIVIRE + COD_PRIVIRE
   + "<p><code>describe()</code> lucrează implicit pe coloanele numerice. Cu <code>include=\"object\"</code> descrie "
     "coloanele text: câte valori sunt, câte sunt distincte, care apare cel mai des. Pe nomenclatorul "
     "<code>nume</code>, codurile sunt toate diferite (1.971), dar numele nu: „Kýpros” apare de 4 ori, o dată pe "
     "fiecare nivel, de la țară până la NUTS 3. De aceea tabelele se unesc după coduri, niciodată după nume.</p>"
   + nota("Atribut sau metodă",
          "<code>shape</code> și <code>columns</code> sunt atribute: proprietăți ale tabelului, scrise fără paranteze. "
          "<code>head()</code>, <code>describe()</code> sunt metode: operații, scrise cu paranteze, care pot primi "
          "argumente (<code>head(10)</code>).", True))

sl("s3", "Profilarea", "Ce conține tabelul",
   "<h2>Profilarea: ce conține tabelul</h2>"
   + M_PROFIL
   + ET_VERIF + ix("cod", "Profilarea tabelului", COD_PROFIL),
   manual=
   "<h2>Profilarea: ce conține tabelul</h2>"
   "<p>Profilarea descrie tabelul fără să-l modifice. Răspunde la trei întrebări: ce dimensiune și ce tipuri are, câte "
   "valori are fiecare coloană și ce valori distincte apar în coloanele categoriale. Deciziile din etapele următoare "
   "se sprijină pe aceste răspunsuri.</p>"
   + ix("pas", "Profilarea indicatorilor regionali", PAS_PROFIL)
   + M_PROFIL
   + ix("cod", "Profilarea tabelului", COD_PROFIL)
   + tabel(["Metoda", "Ce arată"], [
       ["~df.info()", "dimensiunea, tipul fiecărei coloane, câte valori are fiecare"],
       ["~df[\"col\"].value_counts()", "valorile distincte ale unei coloane și frecvența lor"],
       ["~df[\"col\"].str.len().value_counts()", "lungimile textelor: o verificare rapidă a codurilor"],
       ["~df.describe()", "minimul, media, cuartilele și maximul coloanelor numerice"],
   ]))


# ===========================================================================
#  4. Tipurile
# ===========================================================================

V_TIP = verif("c4-v6", 3,
    "<code>info()</code> arată o coloană de valori ca <code>object</code>, nu ca număr. Ce înseamnă?",
    ["Fișierul este corupt", "Pandas nu poate reprezenta valorile", "Valorile sunt prea mari",
     "Coloana conține cel puțin o valoare nenumerică"],
    "Pandas a găsit cel puțin o valoare pe care nu o poate interpreta ca număr: <code>:</code> la Eurostat, o virgulă "
    "zecimală, un spațiu. O singură valoare de acest fel este suficientă pentru ca întreaga coloană să fie citită ca "
    "text; <code>pd.to_numeric(..., errors=\"coerce\")</code> o transformă în valoare lipsă.")

TO_NUM = ("<pre><code>exemplu = pd.Series([\"12.5\", \":\", \"7\"])     <span class=\"c\"># o coloană citită ca text</span>\n"
          "pd.to_numeric(exemplu, errors=\"coerce\")      <span class=\"c\"># 12.5, NaN, 7.0</span></code></pre>")

sl("s4", "Profilarea", "Tipurile",
   "<h2>Tipurile: numerele sunt numere?</h2>"
   "<p class=\"cheie\">La noi, <code>valoare</code> este <code>float64</code>, iar codurile sunt <code>object</code> "
   "(text). Un singur text printre numere schimbă tipul întregii coloane.</p>"
   + TO_NUM + V_TIP,
   manual=
   "<h2>Tipurile: numerele sunt numere?</h2>"
   "<p>Tipul unei coloane decide ce operații se pot face cu ea. În tabelul indicatorilor, <code>valoare</code> este "
   "<code>float64</code> (număr cu zecimale, cu <code>NaN</code> pentru lipsuri), iar <code>regiune</code> și "
   "<code>indicator</code> sunt <code>object</code>, adică text.</p>"
   "<p>Când printre numere apare un text, de exemplu <code>:</code>, cu care Eurostat marchează uneori o valoare "
   "indisponibilă, pandas citește toată coloana ca text, iar calculele nu mai funcționează. "
   "<code>pd.to_numeric</code> cu <code>errors=\"coerce\"</code> transformă textul în numere, iar ce nu poate fi "
   "număr devine valoare lipsă:</p>"
   + TO_NUM
   + "<p>Când toate valorile se pot converti, <code>astype</code> schimbă tipul direct. Dacă o singură valoare nu se "
     "poate converti, <code>astype</code> dă eroare; de aceea funcționează și ca verificare.</p>"
     "<pre><code>pd.Series([\"2022\", \"2023\", \"2024\"]).astype(int)   <span class=\"c\"># 2022, 2023, 2024, ca numere întregi</span></code></pre>"
   + V_TIP)


# ===========================================================================
#  5. Duplicatele
# ===========================================================================

M_DUP = metode([
    ["~duplicated(coloane)", "<code>True</code> pentru fiecare rând care repetă o cheie deja întâlnită", "<code>indicatori.duplicated([\"regiune\", \"indicator\"])</code>"],
    ["~sum()", "pe <code>True</code>/<code>False</code>: câte valori <code>True</code> sunt", "<code>....sum()</code> dă numărul de rânduri repetate"],
    ["~drop_duplicates()", "păstrează doar prima apariție a fiecărei valori", "<code>sci[\"regiune_1\"].drop_duplicates()</code>"],
])

COD_DUP = {
    "id": "c4-cod-duplicate", "fisier": "04_curatarea.ipynb",
    "sarcina": "Câte rânduri repetă cheia tabelului, apoi lista regiunilor din SCI, fiecare o singură dată.",
    "cod": "# cheia indicatorilor: regiune + indicator\n"
           "indicatori.{{1}}([\"regiune\", \"indicator\"]).sum()\n\n"
           "# fiecare regiune din SCI, o singura data\n"
           "regiuni_sci = sci[\"regiune_1\"].{{2}}()\n"
           "len(regiuni_sci)",
    "goluri": {
        "1": {"ok": ["duplicated"], "ajutor": "metoda"},
        "2": {"ok": ["drop_duplicates"], "ajutor": "metoda"}},
    "iesire": "0\n298",
    "indiciu": "Metoda care marchează rândurile repetate se numește „duplicat”; cea care le elimină păstrând prima "
               "apariție începe cu drop_.",
    "laBine": "Nicio cheie repetată, iar aria proiectului are 298 de regiuni.",
    "laRau": "Ambele sunt metode ale tabelului sau ale coloanei, fără ghilimele.",
    "explicatie": "<code>duplicated</code> marchează rândurile care repetă o cheie deja întâlnită; <code>sum()</code> "
                  "le numără. <code>drop_duplicates</code> păstrează prima apariție a fiecărei valori."}

sl("s5", "Curățarea", "Duplicatele",
   "<h2>Duplicatele: cheie repetată sau conținut dublat</h2>"
   "<p>Cheia: coloanele care identifică un rând. În SCI nu se repetă, dar RO11-ITC4 și ITC4-RO11 sunt aceeași "
   "legătură: o dublură de conținut, rezolvată la integrare.</p>"
   + M_DUP
   + ET_VERIF + ix("cod", "Duplicatele", COD_DUP),
   manual=
   "<h2>Duplicatele: cheie repetată sau conținut dublat</h2>"
   "<p>Un tabel are o <b>cheie</b>: coloanele care identifică un rând. În tabelul indicatorilor, cheia este "
   "<b>regiune + indicator</b>. O cheie repetată înseamnă două rânduri pentru aceeași observație, iar orice medie sau "
   "sumă calculată ulterior o numără de două ori.</p>"
   "<p>Există și o dublură pe care <code>duplicated</code> nu o detectează: aceeași informație scrisă în două rânduri "
   "cu chei diferite. În SCI, perechea RO11-ITC4 și perechea ITC4-RO11 au chei diferite, dar descriu aceeași "
   "legătură, cu aceeași valoare. Această dublură de conținut se rezolvă la integrare, păstrând o singură ordine a "
   "fiecărei perechi.</p>"
   + tabel(["regiune_1", "regiune_2", "sci", ""], [
       ["~RO11", "~ITC4", "9.760", "Nord-Vest, Lombardia"],
       ["~ITC4", "~RO11", "9.760", "aceeași legătură, în ordine inversă"],
   ])
   + M_DUP
   + ix("cod", "Duplicatele", COD_DUP))


# ===========================================================================
#  6. Valorile imposibile sau neobișnuite
# ===========================================================================

V_SVALBARD = verif("c4-v7", 2,
    "Populația minimă din tabel este 0, la regiunea <code>NO0B</code>. Ce se face cu acest rând?",
    ["Se șterge: o regiune nu poate avea 0 locuitori",
     "Se înlocuiește cu media populației",
     "Se verifică în sursă înainte de orice decizie",
     "Se transformă în valoare lipsă"],
    "<code>NO0B</code> este Svalbard, arhipelagul norvegian, iar Eurostat raportează efectiv 0. Valoarea este "
    "neobișnuită, dar nu greșită. Regula: o valoare neobișnuită se verifică în sursă; doar o valoare imposibilă "
    "(un procent de 140, o populație negativă) se corectează sau se elimină.")

sl("s6", "Curățarea", "Valorile imposibile",
   "<h2>Valorile imposibile sau neobișnuite</h2>"
   + tabel(["Verificarea", "În caiet", "Rezultatul"], [
       ["rezumatul pe indicator", "~groupby(\"indicator\")[\"valoare\"].describe()", "o populație minimă de 0"],
       ["cele mai mici valori", "~populatie.nsmallest(3, \"valoare\")", "<code>NO0B</code>, Svalbard"],
       ["cele mai mari valori", "~populatie.sort_values(\"valoare\", ascending=False).head(3)", "Istanbul, Île-de-France, Lombardia"],
       ["procentele", "~(procente[\"valoare\"] &gt; 100).sum()", "0 valori peste 100"],
   ])
   + V_SVALBARD,
   manual=
   "<h2>Valorile imposibile sau neobișnuite</h2>"
   "<p>Două categorii trebuie ținute separat. O valoare <b>imposibilă</b> încalcă o regulă logică: un procent peste "
   "100, o populație negativă. Ea se corectează sau se elimină, iar decizia se notează. O valoare <b>neobișnuită</b> "
   "este doar departe de celelalte. Ea se verifică în sursă și, de cele mai multe ori, se păstrează: poate fi chiar "
   "fenomenul studiat.</p>"
   + tabel(["Verificarea", "În caiet", "Rezultatul"], [
       ["rezumatul pe indicator", "~groupby(\"indicator\")[\"valoare\"].describe()", "o populație minimă de 0"],
       ["cele mai mici valori", "~populatie.nsmallest(3, \"valoare\")", "<code>NO0B</code>, Svalbard"],
       ["cele mai mari valori", "~populatie.sort_values(\"valoare\", ascending=False).head(3)", "Istanbul, Île-de-France, Lombardia"],
       ["procentele", "~(procente[\"valoare\"] &gt; 100).sum()", "0 valori peste 100"],
   ])
   + V_SVALBARD
   + nota("Valorile extreme statistice",
          "Regulile statistice pentru valori extreme (de exemplu, pragul de 1,5 ori intervalul intercuartilic) țin "
          "de explorarea distribuțiilor, în C6. La curățare contează regulile logice formulate explicit.", True))


# ===========================================================================
#  7-8. Lipsurile
# ===========================================================================

PAS_NA = {
    "fisier": "04_curatarea_si_integrarea_datelor.ipynb · 6.1. Ce înseamnă „lipsă”",
    "intro": "La citire, pandas transformă automat în valoare lipsă câteva texte: celula goală, dar și NA, N/A, null. La noi, NA este codul Namibiei.",
    "cod": "gresit = pd.read_csv(DATE_C3 + \"migratie.csv\")\n"
           "migratie = pd.read_csv(DATE_C3 + \"migratie.csv\",\n"
           "                       keep_default_na=False, na_values=[\"\"])\n\n"
           "gresit[\"cetatenie\"].isna().sum()\n"
           "migratie[\"cetatenie\"].isna().sum()",
    "pasi": [
        {"l": 1, "set": {"gresit": {"t": "DataFrame", "v": {"cols": ["tara_rezidenta", "cetatenie", "persoane"],
            "rows": [["DE", "NaN", "…"], ["…", "…", "…"]], "nota": "Namibia (NA) a devenit NaN"}}},
         "txt": "Citirea implicită: <code>NA</code> se află pe lista de texte pe care pandas le consideră lipsă."},
        {"l": 2, "set": {"migratie": {"t": "DataFrame", "v": {"cols": ["tara_rezidenta", "cetatenie", "persoane"],
            "rows": [["DE", "NA", "…"], ["…", "…", "…"]], "nota": "NA este din nou Namibia"}}},
         "txt": "<code>keep_default_na=False</code> dezactivează lista; <code>na_values=[\"\"]</code> păstrează ca lipsă doar celula goală."},
        {"l": 5, "out": "44", "txt": "44 de rânduri cu cetățeni namibieni ar fi devenit lipsă, fără niciun mesaj."},
        {"l": 6, "out": "0", "txt": "Citirea corectă: niciun cod de țară lipsă."},
    ],
}

P_NAN = {
    "id": "c4-prezice-nan", "fisier": "04_curatarea.ipynb",
    "cod": "s = pd.Series([10, None, 30])\n"
           "print(s.mean(), s.isna().sum())",
    "intrebare": "Ce afișează?",
    "variante": ["13.33 0", "20.0 1", "NaN 1", "Eroare"],
    "corect": 1,
    "indiciu": "La medie, pandas ignoră valorile lipsă. Câte valori lipsesc?",
    "laBine": "Media se calculează din valorile prezente: (10 + 30) / 2.",
    "explicatie": "<code>None</code> devine <code>NaN</code>, iar <code>mean()</code> îl ignoră: media vine din două "
                  "valori, nu din trei. Comportamentul este comod, dar riscant: dacă lipsesc tocmai valorile mari sau "
                  "mici, media se deplasează fără avertisment. De aceea lipsurile se numără întâi, cu "
                  "<code>isna().sum()</code>. Adunarea a două coloane se comportă invers: o valoare lipsă dă suma "
                  "lipsă, ca la migranții din secțiunea 11.",
    "iesire": "20.0 1"}

NA_TAB = tabel(["Citirea", "Codul NA", "Rânduri pierdute"], [
    ["~pd.read_csv(fisier)", "devine NaN (lipsă)", "44 de rânduri cu Namibia"],
    ["~pd.read_csv(fisier, keep_default_na=False, na_values=[\"\"])", "rămâne Namibia", "0"],
])

sl("s7", "Lipsurile", "Ce înseamnă „lipsă”",
   "<h2>Ce înseamnă „lipsă”</h2>"
   "<p class=\"cheie\">Pandas citește ca lipsă nu doar celula goală, ci și texte ca <code>NA</code>. La noi, "
   "<code>NA</code> este Namibia.</p>"
   + NA_TAB
   + ET_VERIF + ix("prezice", "Media și valorile lipsă", P_NAN),
   manual=
   "<h2>Ce înseamnă „lipsă”</h2>"
   "<p>Pentru pandas, o valoare lipsă este <code>NaN</code>. Două consecințe practice decurg de aici. Prima ține de "
   "citire: pandas transformă automat în <code>NaN</code> nu doar celula goală, ci și câteva texte (<code>NA</code>, "
   "<code>N/A</code>, <code>null</code>). În datele noastre, <code>NA</code> este codul Namibiei, deci citirea "
   "implicită ar pierde 44 de rânduri fără niciun mesaj. De aceea codurile de țară se citesc întotdeauna cu "
   "<code>keep_default_na=False</code>.</p>"
   + ix("pas", "Namibia și valorile lipsă", PAS_NA)
   + "<p>A doua consecință ține de calcule: statisticile (media, suma pe o coloană) ignoră valorile lipsă, în timp ce "
     "operațiile între coloane le propagă.</p>"
   + ix("prezice", "Media și valorile lipsă", P_NAN)
   + "<p><code>value_counts()</code> ascunde implicit valorile lipsă; cu <code>dropna=False</code> le numără și pe "
     "ele. Pe zboruri, 418 dintre perechi nu au pasageri raportați.</p>"
   "<pre><code>zboruri[\"pasageri\"].isna().value_counts(dropna=False)   <span class=\"c\"># False 1087, True 418</span></code></pre>")


M_LIPS = metode([
    ["~isna()", "<code>True</code> în fiecare celulă în care lipsește o valoare", "<code>regiuni.isna()</code>"],
    ["~sum()", "numără valorile <code>True</code>, pe fiecare coloană", "<code>regiuni.isna().sum()</code>: câte lipsesc"],
    ["~mean()", "media valorilor <code>True</code> (1) și <code>False</code> (0), adică proporția", "<code>regiuni.isna().mean()</code>: ce proporție lipsește"],
])

COD_LIPSURI = {
    "id": "c4-cod-lipsuri", "fisier": "04_curatarea.ipynb",
    "sarcina": "Câte valori lipsesc pe fiecare coloană a tabelului regiunilor și ce procent reprezintă.",
    "cod": "# cate valori lipsesc, pe coloana\n"
           "regiuni.{{1}}().sum()\n\n"
           "# ce proportie din regiuni, in procente\n"
           "(regiuni.isna().{{2}}() * 100).round(1)",
    "goluri": {
        "1": {"ok": ["isna", "isnull"], "ajutor": "metoda"},
        "2": {"ok": ["mean"], "ajutor": "metoda"}},
    "iesire": "pib_locuitor       22\nretele_sociale    124\n...\npib_locuitor       7.4\nretele_sociale    41.6",
    "indiciu": "Metoda care întoarce True unde lipsește o valoare este isna. Proporția valorilor True este media lor.",
    "laBine": "Rețelele sociale lipsesc la 42% dintre regiuni; ceilalți indicatori, la sub 8%.",
    "laRau": "Ambele goluri sunt metode, fără argumente.",
    "explicatie": "<code>isna()</code> produce <code>True</code> unde lipsește o valoare. <code>sum()</code> numără "
                  "valorile <code>True</code>, iar <code>mean()</code> dă proporția lor, deoarece <code>True</code> "
                  "valorează 1 și <code>False</code> 0."}

SORT_LIPSURI = {
    "id": "c4-sort-lipsuri", "poarta": False,
    "sarcina": "Ce tratament este potrivit fiecărei situații?",
    "elemente": [
        {"t": "3 rânduri din 30.000, la întâmplare", "cos": 0},
        {"t": "o coloană goală în proporție de 80%", "cos": 1},
        {"t": "o țară care nu raportează deloc migranții", "cos": 2},
        {"t": "serie de timp, lipsește un an la mijloc", "cos": 3}],
    "cosuri": [
        {"t": "Eliminarea rândurilor", "d": "puține și fără un tipar"},
        {"t": "Eliminarea coloanei", "d": "prea puțină informație"},
        {"t": "Păstrarea și documentarea", "d": "lipsa are un tipar"},
        {"t": "Completarea din valorile vecine", "d": "interpolare, ultima valoare cunoscută"}],
    "laBine": "Al treilea caz este cel al datelor noastre: lipsa are un tipar, deci se păstrează și se documentează.",
    "explicatie": "Completarea cu media este metoda cea mai răspândită și cea mai riscantă: reduce artificial variația "
                  "și face rezultatele să pară mai precise decât sunt."}

sl("s8", "Lipsurile", "Cât și unde lipsește",
   "<h2>Cât lipsește și unde</h2>"
   + M_LIPS
   + ET_VERIF + ix("cod", "Lipsurile pe coloane", COD_LIPSURI),
   manual=
   "<h2>Cât lipsește și unde</h2>"
   "<p>După ce știm ce înseamnă „lipsă”, măsurăm cât lipsește și unde. Două măsuri sunt suficiente: numărul valorilor "
   "lipsă pe coloană și proporția lor. A doua permite compararea coloanelor între ele.</p>"
   + M_LIPS
   + ix("cod", "Lipsurile pe coloane", COD_LIPSURI)
   + "<p>Întrebarea decisivă este însă <em>de ce</em> lipsesc valorile. Dacă lipsurile sunt puține și fără tipar, "
     "rândurile pot fi eliminate fără consecințe. Dacă au un tipar (anumite țări nu raportează un indicator), "
     "eliminarea lor schimbă compoziția datelor, iar completarea lor inventează valori. În acest caz, lipsa se "
     "păstrează și se documentează.</p>"
   + "<p>Consecințele celor două variante se pot măsura direct. <code>dropna()</code> elimină fiecare rând cu cel puțin "
     "o valoare lipsă; <code>fillna(valoare)</code> pune o valoare în locul fiecărei lipse.</p>"
     "<pre><code>complete = regiuni.dropna()                          <span class=\"c\"># 161 din 298 regiuni, 24 din 37 țări</span>\n\n"
     "pib = regiuni[\"pib_locuitor\"]\n"
     "completat = pib.fillna(pib.median())                 <span class=\"c\"># 22 de regiuni primesc mediana</span>\n"
     "pib.std(), completat.std()                           <span class=\"c\"># 14503, 13968</span></code></pre>"
     "<p>Eliminarea ar scoate aproape jumătate dintre regiuni și 13 țări întregi. Completarea cu mediana reduce "
     "abaterea standard: datele par mai omogene decât sunt, pentru că 22 de regiuni primesc aceeași valoare, "
     "inventată.</p>"
   + ix("sortare", "Tratamentul potrivit fiecărui caz", SORT_LIPSURI)
   + nota("Decizia noastră",
          "Păstrăm toate cele 298 de regiuni, fără să completăm valorile lipsă, și alegem pentru fiecare analiză doar "
          "coloanele de care are nevoie. Regiunile fără PIB sunt din Elveția, Norvegia, Albania, Bosnia și Herțegovina, "
          "Kosovo și Islanda: o eliminare ar scoate din analiză tocmai aceste țări.", True))


# ===========================================================================
#  9. Codurile
# ===========================================================================

M_COD = metode([
    ["~keep_default_na=False", "la citire: textele ca <code>NA</code> rămân text, nu devin lipsă", "Namibia rămâne <code>NA</code>"],
    ["~na_values=[\"\"]", "la citire: doar celula goală e valoare lipsă", "lipsurile reale rămân lipsă"],
    ["~replace(dicționar)", "înlocuiește valorile după un dicționar <code>{vechi: nou}</code>", "<code>migratie.replace({\"cetatenie\": {\"EL\": \"GR\"}})</code>"],
])

COD_STANDARD = {
    "id": "c4-cod-standard", "fisier": "04_curatarea.ipynb",
    "sarcina": "Citirea migrației fără pierderea Namibiei, apoi alinierea codurilor Eurostat la cele din SCI.",
    "cod": "# NA este Namibia: lipsa este doar celula goala\n"
           "migratie = pd.read_csv(DATE_C3 + \"migratie.csv\",\n"
           "                       keep_default_na={{1}}, na_values=[\"\"])\n\n"
           "# Eurostat scrie altfel doua tari\n"
           "coduri = {\"EL\": \"GR\", \"UK\": {{2}}}\n"
           "migratie = migratie.{{3}}({\"tara_rezidenta\": coduri, \"cetatenie\": coduri})\n\n"
           "migratie[\"tara_rezidenta\"].isin([\"EL\", \"UK\"]).sum()",
    "goluri": {
        "1": {"ok": ["False"], "ajutor": "valoarea"},
        "2": {"ok": ["\"GB\"", "'GB'"], "ajutor": "codul"},
        "3": {"ok": ["replace"], "ajutor": "metoda"}},
    "iesire": "0",
    "indiciu": "Lista implicită de valori lipsă se dezactivează cu valoarea logică „fals”. Codul Regatului Unit în SCI "
               "este GB. Metoda care înlocuiește valori după un dicționar este replace.",
    "laBine": "Nu mai rămâne niciun EL sau UK: migrația și SCI folosesc aceleași coduri.",
    "laRau": "Primul gol este o valoare logică; codul este un text, între ghilimele.",
    "explicatie": "Dicționarul <code>coduri</code> documentează și decizia: cine citește codul mai târziu află din el că "
                  "EL și GR au fost tratate ca aceeași țară."}

CODURI_TAB = tabel(["Țara", "SCI", "Eurostat", "Fără corecție"], [
    ["Grecia", "~GR", "~EL", "se pierde la unire, fără eroare"],
    ["Regatul Unit", "~GB", "~UK", "la fel"],
    ["Namibia", "~NA", "~NA", "citită ca valoare lipsă"],
])

sl("s9", "Curățarea", "Codurile",
   "<h2>Aceeași țară, alt cod</h2>"
   "<p>Eurostat scrie Grecia <code>EL</code> și Regatul Unit <code>UK</code>; SCI, <code>GR</code> și <code>GB</code>.</p>"
   + M_COD
   + ET_VERIF + ix("cod", "Alinierea codurilor", COD_STANDARD),
   manual=
   "<h2>Aceeași țară, alt cod</h2>"
   "<p>Când se combină două surse, aceeași țară poate avea coduri diferite. Eurostat folosește <code>EL</code> pentru "
   "Grecia și <code>UK</code> pentru Regatul Unit, iar SCI folosește codurile ISO, <code>GR</code> și <code>GB</code>. "
   "Pentru program sunt țări diferite, iar o unire pe coduri le pierde fără niciun mesaj de eroare. Corecția se face "
   "înainte de unire, cu un dicționar explicit.</p>"
   + CODURI_TAB
   + M_COD
   + ix("cod", "Alinierea codurilor", COD_STANDARD)
   + "<p>Codurile noastre vin de la API-uri și sunt consecvente. În datele introduse de mână (chestionare, "
     "registre), aceeași categorie apare des în mai multe forme: cu spații, cu litere mici. Metodele din grupul "
     "<code>.str</code> le aduc la aceeași formă înainte de numărare sau de unire:</p>"
     "<pre><code>scrise = pd.Series([\" RO\", \"ro\", \"Ro \"])     <span class=\"c\"># 3 valori distincte</span>\n"
     "scrise.str.strip().str.upper()                <span class=\"c\"># RO, RO, RO</span></code></pre>"
   + nota("Aceeași regulă pentru SCI pe țări",
          "<code>country.csv</code> conține și el Namibia; se citește tot cu <code>keep_default_na=False</code>.", True))


# ===========================================================================
#  10. Din lung în lat
# ===========================================================================

_LUNG = [["RO11", 74.7, "densitate"], ["RO12", 67.4, "densitate"],
         ["RO11", 28300.0, "pib_locuitor"], ["RO12", 28400.0, "pib_locuitor"],
         ["RO11", 2539784.0, "populatie"], ["RO12", 2288061.0, "populatie"]]

PAS_PIVOT = {
    "fisier": "04_curatarea_si_integrarea_datelor.ipynb · 8. Din lung în lat",
    "intro": "Pe două regiuni și trei indicatori: Nord-Vest (RO11, cu Clujul) și Centru (RO12).",
    "cod": "lung = in_sci[in_sci[\"regiune\"].isin([\"RO11\", \"RO12\"])]\n\n"
           "lat = lung.pivot(index=\"regiune\", columns=\"indicator\", values=\"valoare\")\n"
           "lat = lat.reset_index()",
    "pasi": [
        {"l": 1, "set": {"lung": {"t": "DataFrame", "v": {"cols": ["regiune", "valoare", "indicator"], "rows": _LUNG,
            "nota": "lung: un rând pe regiune și indicator"}}},
         "txt": "Forma <b>lungă</b>: fiecare regiune apare o dată pentru fiecare indicator."},
        {"l": 3, "set": {"lat": {"t": "DataFrame", "v": {"cols": ["densitate", "pib_locuitor", "populatie"],
            "index": ["RO11", "RO12"], "rows": [[74.7, 28300.0, 2539784.0], [67.4, 28400.0, 2288061.0]],
            "nota": "lat: regiunea a ajuns în index"}}},
         "txt": "<code>pivot</code>: <code>index</code> spune ce devine rând, <code>columns</code> ce devine coloană, "
                "<code>values</code> ce se pune în celule."},
        {"l": 4, "set": {"lat": {"t": "DataFrame", "v": {"cols": ["regiune", "densitate", "pib_locuitor", "populatie"],
            "rows": [["RO11", 74.7, 28300.0, 2539784.0], ["RO12", 67.4, 28400.0, 2288061.0]],
            "nota": "lat: un rând pe regiune"}}},
         "txt": "<code>reset_index</code> readuce regiunea într-o coloană obișnuită, ca să poată fi folosită la "
                "<code>merge</code>."},
    ],
}

sl("s10", "Integrarea", "Din lung în lat",
   "<h2>Din lung în lat: un rând pe regiune</h2>"
   + ix("pas", "Din lung în lat", PAS_PIVOT),
   manual=
   "<h2>Din lung în lat: un rând pe regiune</h2>"
   "<p>Tabelul indicatorilor este în format <b>lung</b>: un rând pe regiune și indicator. Formatul este potrivit pentru "
   "colectare și pentru verificări (un indicator nou înseamnă doar rânduri noi), dar analiza regiunilor cere un rând pe "
   "regiune, cu câte o coloană pe indicator: formatul <b>lat</b>. <code>pivot</code> face trecerea.</p>"
   + ix("pas", "Din lung în lat", PAS_PIVOT)
   + "<p>În caiet, tabelul lat se lipește apoi de lista celor 298 de regiuni din SCI, cu <code>how=\"left\"</code>, "
     "ca să rămână și regiunile fără date. Numărul de rânduri se verifică imediat: 298 înainte, 298 după.</p>")


# ===========================================================================
#  11. Unirea, cu verificare
# ===========================================================================

P_MERGE = {
    "id": "c4-prezice-merge", "fisier": "04_curatarea.ipynb",
    "cod": "perechi = sci[sci[\"regiune_1\"] < sci[\"regiune_2\"]]     # 44253 de perechi\n\n"
           "inainte = len(perechi)\n"
           "perechi = perechi.merge(atribute.add_suffix(\"_1\"), on=\"regiune_1\", how=\"left\")\n"
           "print(inainte, \"->\", len(perechi))",
    "intrebare": "<code>atribute</code> are un singur rând pe regiune. Câte rânduri are <code>perechi</code> după unire?",
    "variante": ["Tot 44.253", "Mai multe: se adaugă coloane noi", "Mai puține: perechile fără date dispar",
                 "88.804: fiecare pereche, în ambele ordini"],
    "corect": 0,
    "indiciu": "how=\"left\" păstrează toate rândurile din stânga. Ce s-ar întâmpla dacă o regiune ar apărea de două ori în dreapta?",
    "laBine": "Același număr: fiecare pereche a primit exact un rând de atribute.",
    "explicatie": "<code>how=\"left\"</code> păstrează toate perechile, chiar și pe cele fără date. Numărul ar crește "
                  "doar dacă o regiune ar apărea de mai multe ori în <code>atribute</code>: atunci fiecare pereche cu "
                  "ea s-ar multiplica. De aceea numărăm rândurile după fiecare <code>merge</code>.",
    "iesire": "44253 -> 44253"}

sl("s11", "Integrarea", "Unirea, cu verificare",
   "<h2>Unirea tabelelor, cu o singură regulă</h2>"
   "<p class=\"cheie\">La unire se pierd sau se multiplică rânduri fără nicio eroare. După fiecare <code>merge</code>, "
   "numărăm rândurile.</p>"
   + ET_VERIF + ix("prezice", "Câte rânduri după merge?", P_MERGE),
   manual=
   "<h2>Unirea tabelelor, cu o singură regulă</h2>"
   "<p>Perechile de regiuni se obțin din SCI în doi pași. Întâi se rezolvă dublura de conținut: se păstrează perechea "
   "în care primul cod este mai mic alfabetic, ceea ce elimină și perechile unei regiuni cu ea însăși "
   "(298 × 297 / 2 = 44.253 de perechi). Apoi se lipesc atributele fiecărui capăt, de două ori: o dată cu sufixul "
   "<code>_1</code>, o dată cu <code>_2</code>.</p>"
   + ix("prezice", "Câte rânduri după merge?", P_MERGE)
   + tabel(["Rezultatul unui merge", "Ce înseamnă"], [
       ["același număr de rânduri", "fiecare rând a găsit cel mult o potrivire: corect"],
       ["mai multe rânduri", "cheia se repetă în tabelul din dreapta: rânduri multiplicate"],
       ["mai puține rânduri", "s-a folosit altă unire decât <code>how=\"left\"</code>: rânduri pierdute"],
   ]))


# ===========================================================================
#  12. Perechile de țări
# ===========================================================================

DIRECTII = {
    "randuri": [
        {"a": "RO", "b": "IT", "ab": 1073196, "ba": 14856},
        {"a": "RO", "b": "HU", "ab": 15740, "ba": 4879},
        {"a": "PL", "b": "DE", "ab": 741784, "ba": None},
    ],
    "t0": "Migrația are direcție: românii din Italia ocupă un rând, italienii din România alt rând. SCI are un singur "
          "rând pe pereche.",
    "t1": "Cele două direcții sunt acum pe același rând, ca în SCI. Germanii din Polonia lipsesc: Polonia nu raportează.",
    "t2": "Suma. Pentru perechea Polonia-Germania rezultatul este valoare lipsă, nu 741.784: numărul germanilor din "
          "Polonia este necunoscut, deci și totalul.",
    "intai": {"q": "Polonezii din Germania: 741.784. Germanii din Polonia: Polonia nu raportează. Câți migranți sunt, în "
                   "total, între cele două țări?",
              "variante": ["741.784", "741.784 plus o estimare", "Nu se poate spune"], "corect": 2,
              "dupa": "O direcție lipsește, deci lipsește și suma. Zero ar fi o afirmație falsă, iar o estimare ar fi o "
                      "decizie de documentat în jurnal, nu un calcul."},
}

sl("s12", "Integrarea", "Perechile de țări",
   "<h2>Migrația în forma SCI: două direcții, un rând</h2>"
   + ix("directii", "Românii din Italia și italienii din România", DIRECTII)
   + nota("Acoperirea", "Rămân doar țările care raportează cel puțin 20 de cetățenii: 24 de țări, 276 de perechi.", True),
   manual=
   "<h2>Migrația în forma SCI: două direcții, un rând</h2>"
   "<p>SCI este simetric: o singură valoare pe pereche de țări. Migrația are direcție. Pentru a le aduce în același "
   "tabel, cele două direcții se lipesc pe același rând, prin două uniri, câte una pentru fiecare sens, iar apoi se "
   "adună.</p>"
   + ix("directii", "Românii din Italia și italienii din România", DIRECTII)
   + "<p>Înainte de unire se verifică acoperirea: nu toate țările raportează migranții pe cetățenii. O țară care nu "
     "raportează are valoare lipsă la toate perechile ei, iar perechile cu ea ar avea migrația incompletă. Caietul "
     "păstrează doar țările care raportează cel puțin 20 de cetățenii: 24 de țări, deci 276 de perechi.</p>"
   + nota("Valoare lipsă plus număr dă valoare lipsă",
          "Este comportamentul corect: o pereche cu o direcție necunoscută nu are un total cunoscut. Cu zero în locul "
          "valorii lipsă, perechea Polonia-Germania ar părea cunoscută, dar ar fi greșită.", True))


# ===========================================================================
#  13. Validarea finală
# ===========================================================================

M_VAL = metode([
    ["~duplicated(cheie).sum()", "câte rânduri repetă cheia: trebuie 0", "<code>regiuni.duplicated(\"regiune\").sum()</code>"],
    ["~isna().sum()", "câte valori lipsesc într-o coloană: la SCI trebuie 0", "<code>perechi[\"sci\"].isna().sum()</code>"],
    ["~len(tabel)", "câte rânduri are tabelul", "<code>len(perechi)</code>: 44.253"],
])

COD_VALIDARE = {
    "id": "c4-cod-validare", "fisier": "04_curatarea.ipynb",
    "sarcina": "Validarea finală a celor trei tabele de analiză, înainte de salvare.",
    "cod": "# cheia fiecarui tabel este unica\n"
           "print(regiuni.duplicated(\"regiune\").sum())\n"
           "print(perechi.{{1}}([\"regiune_1\", \"regiune_2\"]).sum())\n"
           "print(tari.duplicated([\"tara_1\", \"tara_2\"]).sum())\n\n"
           "# variabila de explicat este completa\n"
           "print(perechi[\"sci\"].{{2}}().sum(), tari[\"sci\"].isna().sum())\n\n"
           "# cate randuri are fiecare tabel\n"
           "print(len(regiuni), len(perechi), {{3}}(tari))",
    "goluri": {
        "1": {"ok": ["duplicated"], "ajutor": "metoda"},
        "2": {"ok": ["isna", "isnull"], "ajutor": "metoda"},
        "3": {"ok": ["len"], "ajutor": "funcția"}},
    "iesire": "0\n0\n0\n0 0\n298 44253 276",
    "indiciu": "Cheile se verifică la fel ca la secțiunea duplicatelor. Lipsurile se numără cu isna. Numărul de rânduri "
               "îl dă funcția len.",
    "laBine": "0 chei repetate, 0 perechi fără SCI, iar numărul de rânduri este cel așteptat.",
    "laRau": "Primele două goluri sunt metode; ultimul este o funcție Python.",
    "explicatie": "Celula se rulează la fiecare refacere a curățării. Dacă o cifră diferă de cea așteptată, un pas "
                  "anterior a schimbat datele, iar tabelele nu se salvează până nu se află de ce."}

sl("s13", "Validarea", "Validarea finală",
   "<h2>Validarea finală</h2>"
   "<p>Înainte de salvare, o singură celulă verifică regulile fiecărui tabel.</p>"
   + M_VAL
   + ET_VERIF + ix("cod", "Verificările finale", COD_VALIDARE),
   manual=
   "<h2>Validarea finală</h2>"
   "<p>Validarea compară tabelele finale cu regulile lor. Fiecare tabel de analiză are o cheie (regiunea, perechea de "
   "regiuni, perechea de țări), care trebuie să fie unică, și o variabilă de explicat, SCI, care trebuie să fie "
   "completă. Numărul de rânduri trebuie să fie cel calculat: 298 de regiuni, 44.253 de perechi de regiuni, 276 de "
   "perechi de țări.</p>"
   + M_VAL
   + ix("cod", "Verificările finale", COD_VALIDARE)
   + "<p>Celula se păstrează în caiet și se rulează la fiecare refacere a curățării. Rolul ei nu este să găsească "
     "erori o singură dată, ci să semnaleze imediat când o modificare ulterioară schimbă datele.</p>")


# ===========================================================================
#  14. Jurnalul deciziilor
# ===========================================================================

JURNAL = tabel(["Tema", "Decizia", "De ce"], [
    ["populația 0 la Svalbard", "păstrată", "raportată așa de sursă"],
    ["codul <code>NA</code> (Namibia)", "citit ca text", "altfel 44 de rânduri devin lipsă"],
    ["regiuni fără date", "păstrate, fără completare", "lipsurile nu sunt întâmplătoare"],
    ["perechi A-B și B-A", "o singură apariție", "aceeași valoare, de două ori"],
    ["codurile EL și UK", "aliniate la GR și GB", "altfel se pierd țări la unire"],
    ["țări care nu raportează migrația", "scoase din perechile de țări", "migrația lor este necunoscută"],
    ["zboruri raportate de ambele țări", "valoarea raportată de țara 1", "o singură valoare pe pereche"],
])

sl("s14", "Validarea", "Jurnalul deciziilor",
   "<h2>Jurnalul deciziilor</h2>"
   "<p class=\"cheie\">Orice curățare înseamnă decizii. Fiecare se scrie, cu motivul ei, ca oricine să o poată "
   "verifica.</p>"
   + JURNAL,
   manual=
   "<h2>Jurnalul deciziilor</h2>"
   "<p>Curățarea nu este o succesiune de operații tehnice, ci o succesiune de decizii: ce se păstrează, ce se "
   "elimină, ce se înlocuiește. Fiecare decizie schimbă datele pe care se sprijină analiza, deci trebuie scrisă, "
   "împreună cu motivul ei. În proiect, jurnalul stă în <code>README.md</code>.</p>"
   + JURNAL
   + nota("Criteriul unui jurnal complet",
          "Un coleg care nu a participat la discuțiile echipei trebuie să poată reface curățarea doar pe baza caietului "
          "și a jurnalului. Dacă are nevoie de explicații suplimentare, documentația este incompletă.", True))


# ===========================================================================
#  15. Proiectul echipei
# ===========================================================================

DOVADA = {
    "id": "c4-dovada-curatare",
    "sarcina": "În depozitul echipei, după ce caietul de curățare a fost urcat pe <code>dev</code>: rezultatul fiecărei "
               "comenzi se lipește în câmpul ei.",
    "pasi": [
        {"t": "Validarea finală", "cmd": "celula de validare din caietul echipei",
         "gol": "rezultatul celulei",
         "cauta": r"\d+[\s\S]*\d+",
         "daca_nu": "Se așteaptă cifrele celulei de validare: chei repetate, lipsuri, numărul de rânduri."},
        {"t": "Pe ramura dev", "cmd": "git branch",
         "gol": "ramura marcată cu *",
         "cauta": r"\*\s*dev",
         "daca_nu": "Ramura curentă trebuie să fie dev: git switch dev."},
        {"t": "Caietul este în depozit", "cmd": "git log --oneline -1",
         "gol": "linia afișată",
         "cauta": r"[0-9a-f]{7}",
         "daca_nu": "Se așteaptă codul unui commit. Dacă nu există, caietul nu a fost încă salvat cu git commit."}],
    "explicatie": "Datele brute rămân neschimbate în <code>data/raw</code>, cele curate stau în "
                  "<code>data/processed</code>, iar trecerea de la unele la altele este un caiet care poate fi rulat "
                  "din nou. Acestea sunt condițiile unei curățări reproductibile."}

DECIZIE = {
    "id": "c4-decizie", "tip": "decizie", "minim": 60,
    "sarcina": "Cea mai importantă decizie de curățare luată pentru datele proiectului și motivul ei: ce anume s-a "
               "modificat și de ce, nu o formulare generală.",
    "exemplu": "De exemplu: migrația a fost păstrată ca valoare lipsă pentru perechile cu Polonia, în loc de zero, "
               "deoarece Polonia nu raportează; aceste perechi sunt excluse doar din model, nu din tabel.",
    "multumesc": "Răspunsul va fi citit înainte de cursul următor."}

PASI_ECHIPA = tabel(["Pasul", "Ce se face"], [
    ["1", "caietul de curățare, <code>notebooks/03_cleaning.ipynb</code>, citește din <code>data/raw</code> sau <code>data/processed</code>"],
    ["2", "aceleași verificări ca la curs: profilare, tipuri, duplicate, valori imposibile, lipsuri, coduri"],
    ["3", "tabelele curate se scriu în <code>data/processed</code>, niciodată peste datele brute"],
    ["4", "celula de validare finală și deciziile, în <code>README.md</code>"],
    ["5", "pe <code>dev</code>: <code>git pull</code>, <code>git add</code>, <code>git commit</code>, <code>git push</code>"],
])

sl("s15", "Proiectul echipei", "Curățarea datelor proprii",
   "<h2>Curățarea datelor proiectului</h2>"
   + PASI_ECHIPA
   + ET_VERIF
   + "<p>Cea mai importantă decizie de curățare luată pentru datele proiectului și motivul ei, în două sau trei rânduri.</p>"
   + ix("asteptari", "Decizia de curățare", DECIZIE),
   manual=
   "<h2>Curățarea datelor proiectului</h2>"
   "<p>Fiecare echipă aplică aceleași verificări pe datele proprii, într-un caiet separat, responsabilul pasului de "
   "curățare coordonând lucrul. Caietul are aceeași structură ca cel de la curs și se încheie cu celula de validare "
   "și cu jurnalul deciziilor.</p>"
   + PASI_ECHIPA
   + ix("asteptari", "Decizia de curățare", DECIZIE)
   + ix("dovada", "Dovada curățării", DOVADA))

sl("s15b", "Proiectul echipei", "Dovada curățării",
   "<h2>Dovada curățării</h2>"
   + ET_VERIF + ix("dovada", "Dovada curățării", DOVADA),
   manual="")


# ===========================================================================
#  16. Mai departe
# ===========================================================================

sl("s16", "Mai departe", "Pentru cursul următor",
   "<h2>La cursul 5: agregare și baze de date</h2>"
   '<div class="fin3"><div class="fin3__g">'
   "<section><h4>Ce urmează la cursul 5</h4><ul>"
   "<li>Cele trei tabele de analiză, încărcate într-o bază de date PostgreSQL.</li>"
   "<li>Interogări SQL: selecție, filtrare, grupare.</li>"
   "<li>Agregarea, în SQL și în pandas.</li></ul></section>"
   "<section><h4>Pregătirea pentru cursul 5</h4><ul>"
   "<li>Caietul de curățare al echipei, pe <code>dev</code>, cu celula de validare.</li>"
   "<li>Deciziile de curățare, în <code>README.md</code>.</li>"
   "<li>Un cont pe Neon, pentru baza de date.</li></ul></section>"
   "</div></div>"
   + surse("Documentația curățării", [
       ("pandas: 10 minutes to pandas", "https://pandas.pydata.org/docs/user_guide/10min.html",
        "prima privire asupra unui tabel: <code>head</code>, <code>describe</code>, <code>sort_values</code>"),
       ("pandas: describe", "https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.describe.html",
        "rezumatul numeric și, cu <code>include=\"object\"</code>, al coloanelor text"),
       ("pandas: date lipsă", "https://pandas.pydata.org/docs/user_guide/missing_data.html",
        "ce înseamnă <code>NaN</code>, cum se propagă și cum se tratează"),
       ("pandas: read_csv", "https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html",
        "<code>keep_default_na</code> și <code>na_values</code>, pentru cazul Namibiei"),
       ("pandas: duplicate", "https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.duplicated.html",
        "<code>duplicated</code> și <code>subset</code>"),
       ("pandas: lung și lat", "https://pandas.pydata.org/docs/user_guide/reshaping.html",
        "<code>pivot</code>, cu diagrame"),
       ("pandas: merge", "https://pandas.pydata.org/docs/user_guide/merging.html",
        "unirea tabelelor și tipurile de unire"),
       ("Eurostat: codurile țărilor", "https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Glossary:Country_codes",
        "de ce Grecia este EL și Regatul Unit este UK"),
       ("Kaggle: Data Cleaning", "https://www.kaggle.com/learn/data-cleaning",
        "un curs scurt: valori lipsă, codificarea caracterelor, înregistrări inconsecvente"),
   ]))


if __name__ == "__main__":
    L.scrie_tot()
