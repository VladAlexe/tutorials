# -*- coding: utf-8 -*-
"""
Lecția 5: Agregare și baze de date.

Urmează prezentarea Curs_5.pptx: felurile de a uni tabele în pandas (concat,
merge, tipurile de join, join pe index), baza de date Neon, și comparația
PostgreSQL / MySQL.

Ce am adăugat peste prezentare, și de ce:
  - un bloc în care se vede ce iese din fiecare fel de îmbinare, pe două
    tabele mici, pentru că `inner` și `left` se învață numărând rânduri, nu
    citind definiții;
  - capcanele merge-ului (chei care nu se potrivesc, rânduri care se
    înmulțesc), pentru că acolo se pierd datele în tăcere, nu la sintaxă;
  - unitatea de analiză, pentru că proiectul lor are nevoie de un răspuns
    explicit la întrebarea „ce e un rând în tabelul final”;
  - partea de SQL propriu-zis: fără un `select` scris cu mâna, baza de date
    rămâne un loc unde se pune ceva, nu o unealtă.

Rulare:  python _build/c5.py
"""

from comun import Lectie, ix, verif, tabel, nota, surse

L = Lectie(5, "c5-agregare-si-baze-de-date", "Agregare și baze de date",
           "Unirea tabelelor în pandas, tipurile de join și capcanele lor, "
           "unitatea de analiză și transferul datelor într-o bază PostgreSQL.")
sl = L.sl


# --------------------------------------------------------------------------
# Tabelele mici pe care se învață îmbinările. Valorile sunt adevărate: SCI-ul
# României cu patru parteneri, și câți cetățeni români trăiesc în patru țări
# (Eurostat migr_pop1ctz, 2024). Cheia care lipsește din dreapta e MD:
# Moldova nu raportează la Eurostat, deci cel mai puternic partener al
# României dispare la un inner join. Problema e reală, nu de exercițiu.
# --------------------------------------------------------------------------

STANGA = {"nume": "sci", "randuri": [
    {"cod": "MD", "sci": 173794},
    {"cod": "AT", "sci": 124693},
    {"cod": "DE", "sci": 91228},
    {"cod": "HU", "sci": 85021},
]}

DREAPTA = {"nume": "romani", "randuri": [
    {"cod": "AT", "romani": 153427},
    {"cod": "DE", "romani": 776424},
    {"cod": "HU", "romani": 15740},
    {"cod": "IT", "romani": 1073196},
]}

EXPLIC = {
    "concat": "<b>Una sub alta.</b> Opt rânduri: <code>concat</code> nu "
              "compară cheile, ci așază rândurile unul sub altul. "
              "Coloanele se reunesc, iar acolo unde un tabel nu avea o coloană "
              "rămâne <code>NaN</code>. Este operația potrivită pentru ani "
              "diferiți din aceeași sursă, nu pentru adăugarea de coloane.",
    "inner": "<b>Doar cheile comune.</b> Trei rânduri: AT, DE, HU. Moldova, "
             "cel mai puternic partener al României, a fost eliminată doar "
             "pentru că nu raportează migrația. Rezultatul nu are nicio celulă "
             "goală și nicio urmă a ei. De aceea <code>inner</code> este o "
             "valoare implicită riscantă.",
    "left": "<b>Toate rândurile din stânga.</b> Patru rânduri, câte avea tabelul "
            "<code>sci</code>. MD rămâne, cu <code>NaN</code> la români: valoarea "
            "lipsește, iar lipsa rămâne vizibilă. IT nu apare, fiindcă tabelul "
            "din stânga conține doar patru parteneri. Este tipul potrivit când "
            "tabelul din stânga este tabelul de bază.",
    "right": "<b>Toate rândurile din dreapta.</b> Simetricul lui <code>left</code>: "
             "IT rămâne, cu <code>NaN</code> la SCI, iar MD dispare. "
             "Se folosește rar: de obicei se inversează ordinea tabelelor și "
             "se scrie <code>left</code>, care se citește mai ușor.",
    "outer": "<b>Toate cheile, din ambele tabele.</b> Cinci rânduri: cele trei "
             "comune, plus MD fără migrație, plus IT fără SCI. Este tipul folosit "
             "pentru verificare: diferența dintre numărul de rânduri din "
             "<code>outer</code> și din <code>inner</code> arată exact câte "
             "rânduri s-ar fi pierdut.",
}

DUBLE = {"nume": "an_pop", "randuri": [
    {"cod": "MD", "an": 2020, "pop": 2.6},
    {"cod": "MD", "an": 2021, "pop": 2.6},
    {"cod": "MD", "an": 2022, "pop": 2.5},
    {"cod": "DE", "an": 2020, "pop": 83.2},
]}


# ===========================================================================
#  1-2. Cursul
# ===========================================================================

AGENDA = [
    ("Unirea tabelelor", "azi", "Una sub alta sau una lângă alta: două operații "
                                "diferite, adesea confundate."),
    ("Tipurile de join", "azi", "inner, left, right, outer: ce rânduri păstrează "
                                "fiecare și, mai ales, ce rânduri elimină."),
    ("Capcanele", "azi", "Chei care nu se potrivesc și rânduri multiplicate. "
                         "Aici se pierd date fără niciun avertisment."),
    ("Unitatea de analiză", "azi", "Ce reprezintă un rând în tabelul final. "
                                   "Fără acest răspuns, agregarea nu poate fi definită."),
    ("Baza de date", "azi", "Când un fișier nu mai este suficient și cum se încarcă "
                            "datele într-o bază PostgreSQL pe Neon."),
]

# Pașii pentru lecția 5.
# Regiunile și perechile: data/analiza_c4/referinta_c2_20261013/nuts2 (SCI ianuarie 2026, Eurostat 2024).
# Migrația: Eurostat migr_pop1ctz, 2024. SCI între țări: data/country.csv.

PAS_MERGE = {
    "fisier": "04_curatarea.ipynb · 5. Perechile de regiuni",
    "intro": "Un rând este o pereche de regiuni. Fiecărui rând i se adaugă populația <b>ambelor</b> regiuni din pereche, ceea ce cere două îmbinări, nu una.",
    "cod": "perechi = sci[sci[\"regiune_1\"] < sci[\"regiune_2\"]]\n"
           "atribute = regiuni[[\"regiune\", \"populatie\"]]\n\n"
           "capat_1 = atribute.add_suffix(\"_1\")\n"
           "perechi = perechi.merge(capat_1, on=\"regiune_1\", how=\"left\")\n"
           "perechi = perechi.merge(atribute.add_suffix(\"_2\"), on=\"regiune_2\", how=\"left\")\n"
           "print(len(perechi))",
    "pasi": [
        {"l": 1, "set": {"perechi": {"t": "DataFrame", "v": {"cols": ["regiune_1", "regiune_2", "sci"],
            "rows": [["HU11", "RO11", 34160], ["RO11", "RO12", 308881], ["…", "…", "…"]],
            "nota": "44.253 de perechi, fiecare o singură dată"}}},
         "txt": "SCI conține fiecare pereche de două ori: (Budapesta, Nord-Vest) și (Nord-Vest, Budapesta). Condiția <code>&lt;</code> între coduri păstrează doar una dintre ele."},
        {"l": 2, "set": {"atribute": {"t": "DataFrame", "v": {"cols": ["regiune", "populatie"],
            "rows": [["HU11", 1686222], ["RO11", 2539784], ["RO12", 2288061], ["…", "…"]],
            "nota": "un rând pe regiune (în caiet: și densitatea, și PIB-ul)"}}},
         "txt": "Tabelul regiunilor are o coloană <code>regiune</code>. Perechile au două: <code>regiune_1</code> și <code>regiune_2</code>. Numele coloanelor diferă."},
        {"l": 4, "set": {"capat_1": {"t": "DataFrame", "v": {"cols": ["regiune_1", "populatie_1"],
            "rows": [["HU11", 1686222], ["RO11", 2539784], ["RO12", 2288061], ["…", "…"]]}}},
         "txt": "<code>add_suffix(\"_1\")</code> pune <code>_1</code> la toate coloanele, inclusiv la cheie. Acum cheia are același nume ca în tabelul perechilor."},
        {"l": 5, "set": {"perechi": {"t": "DataFrame", "v": {"cols": ["regiune_1", "regiune_2", "sci", "populatie_1"],
            "rows": [["HU11", "RO11", 34160, 1686222], ["RO11", "RO12", 308881, 2539784], ["…", "…", "…", "…"]]}}},
         "txt": "Prima îmbinare: fiecare pereche primește populația primei regiuni (Budapesta pe primul rând, Nord-Vest pe al doilea)."},
        {"l": 6, "set": {"perechi": {"t": "DataFrame", "v": {"cols": ["regiune_1", "regiune_2", "sci", "populatie_1", "populatie_2"],
            "rows": [["HU11", "RO11", 34160, 1686222, 2539784], ["RO11", "RO12", 308881, 2539784, 2288061], ["…", "…", "…", "…", "…"]]}}}, "sterge": ["capat_1", "atribute"],
         "txt": "A doua îmbinare folosește același tabel de atribute, cu alt sufix. Nord-Vest apare acum ca a doua regiune pe primul rând și ca prima pe al doilea."},
        {"l": 7, "out": "44253",
         "txt": "Verificarea din exercițiul de mai jos: tot 44.253. Cheile din dreapta sunt unice, deci niciun rând nu a fost multiplicat."},
    ],
}

PAS_AGREG = {
    "fisier": "tabelul regiunilor din C4 · de la regiuni la țări",
    "intro": "Tabelul are un rând pe regiune; rezultatul trebuie să aibă un rând pe țară. Unitatea de analiză se schimbă cu <code>groupby</code>.",
    "cod": "regiuni = pd.read_csv(DATE / \"c4\" / \"regiuni_nuts2.csv\")\n\n"
           "pe_tara = regiuni.groupby(\"tara\")[\"populatie\"].agg([\"size\", \"sum\"])\n"
           "pe_tara.loc[[\"RO\", \"HU\", \"IT\", \"DE\"]]\n\n"
           "print(pe_tara.loc[\"RO\", \"sum\"] - 19051804)",
    "pasi": [
        {"l": 1, "set": {"regiuni": {"t": "DataFrame", "v": {"cols": ["regiune", "tara", "populatie"],
            "rows": [["RO11", "RO", 2539784], ["RO12", "RO", 2288061], ["HU11", "HU", 1686222], ["…", "…", "…"]],
            "nota": "298 de regiuni NUTS 2"}}},
         "txt": "Unitatea curentă: regiunea. Coloana <code>tara</code> indică grupul căruia îi aparține fiecare regiune."},
        {"l": 3, "set": {"pe_tara": {"t": "DataFrame", "v": {"cols": ["size", "sum"], "index": ["…", "DE", "…", "HU", "IT", "…", "RO", "…"],
            "rows": [["…", "…"], [38, 83456045], ["…", "…"], [8, 9584627], [21, 58971230], ["…", "…"], [8, 19067576], ["…", "…"]],
            "nota": "un rând pe țară, în ordine alfabetică"}}},
         "txt": "<code>groupby(\"tara\")</code> grupează regiunile fiecărei țări; <code>agg</code> aplică două funcții deodată: <code>size</code> numără regiunile, <code>sum</code> însumează populația."},
        {"l": 4, "out": "      size         sum\ntara\nRO       8  19067576.0\nHU       8   9584627.0\nIT      21  58971230.0\nDE      38  83456045.0",
         "txt": "România are 8 regiuni, Germania 38. Țara a devenit unitatea de analiză și, totodată, indexul tabelului: de aceea <code>.loc</code> o selectează după cod."},
        {"l": 6, "out": "15772.0",
         "txt": "Suma regiunilor (Eurostat) față de cifra Băncii Mondiale din C2: diferența este de 15.772 de persoane. Cele două surse au momente de referință și estimări diferite. În proiect se folosește o singură sursă, menționată explicit."},
    ],
}

_MIGR = [["IT", "RO", 1073196], ["IT", "AL", 416229], ["DE", "RO", 776424], ["ES", "RO", 620463], ["…", "…", "…"]]

PAS_SQL = {
    "fisier": "baza/intrebari.sql",
    "memoria": "rezultatul intermediar",
    "intro": "O interogare SQL se scrie începând cu <code>select</code>, dar baza de date nu o execută în această ordine. Pașii urmează ordinea reală de execuție, de aceea numerele de linie nu sunt consecutive.",
    "cod": "select m.geo, m.persoane, s.sci\n"
           "from migratie m\n"
           "join legaturi s on s.tara_1 = 'RO' and s.tara_2 = m.geo\n"
           "where m.citizen = 'RO'\n"
           "order by m.persoane desc\n"
           "limit 3;",
    "pasi": [
        {"l": 2, "set": {"rezultat": {"t": "DataFrame", "v": {"cols": ["geo", "citizen", "persoane"], "rows": _MIGR,
            "nota": "tot tabelul migratie"}}},
         "txt": "Întâi <code>from</code>: tabelul sursă. <code>m</code> este un alias pentru <code>migratie</code>."},
        {"l": 3, "set": {"rezultat": {"t": "DataFrame", "v": {"cols": ["geo", "citizen", "persoane", "sci"],
            "rows": [["IT", "RO", 1073196, 69327], ["IT", "AL", 416229, 69327], ["DE", "RO", 776424, 91228], ["ES", "RO", 620463, 54179], ["…", "…", "…", "…"]],
            "nota": "fiecare rând a primit SCI-ul dintre România și țara de rezidență"}}},
         "txt": "<code>join ... on</code> este echivalentul lui <code>merge</code>: fiecărui rând i se adaugă SCI-ul dintre România și țara de rezidență. Rândul albanezilor din Italia primește tot SCI-ul dintre România și Italia: indicele descrie o legătură între țări, nu între cetățenii lor."},
        {"l": 4, "set": {"rezultat": {"t": "DataFrame", "v": {"cols": ["geo", "citizen", "persoane", "sci"],
            "rows": [["IT", "RO", 1073196, 69327], ["DE", "RO", 776424, 91228], ["ES", "RO", 620463, 54179], ["FR", "RO", 161220, 18075], ["…", "…", "…", "…"]],
            "nota": "doar românii"}}},
         "txt": "<code>where</code> filtrează rândurile, ca <code>d[d[\"citizen\"] == \"RO\"]</code>. Rândul albanezilor a fost eliminat."},
        {"l": 5, "txt": "<code>order by ... desc</code> sortează descrescător. Aici ordinea era deja cea corectă; în general nu este așa."},
        {"l": 6, "set": {"rezultat": {"t": "DataFrame", "v": {"cols": ["geo", "citizen", "persoane", "sci"],
            "rows": [["IT", "RO", 1073196, 69327], ["DE", "RO", 776424, 91228], ["ES", "RO", 620463, 54179]],
            "nota": "primele trei"}}},
         "txt": "<code>limit</code> se aplică la final. Baza a parcurs oricum întregul tabel."},
        {"l": 1, "set": {"rezultat": {"t": "DataFrame", "v": {"cols": ["geo", "persoane", "sci"],
            "rows": [["IT", 1073196, 69327], ["DE", 776424, 91228], ["ES", 620463, 54179]]}}},
         "out": " geo | persoane |   sci\n-----+----------+-------\n IT  |  1073196 | 69327\n DE  |   776424 | 91228\n ES  |   620463 | 54179",
         "txt": "Abia la final <code>select</code> alege coloanele afișate. Ordinea după numărul de migranți nu coincide cu ordinea după SCI: Germania are un SCI mai mare cu România decât Italia."},
    ],
}


sl("s1", "Cursul", "Planul lecției",
   "<h2>Agregare și baze de date</h2>"
   "<p class=\"cheie\">Tabelele curate devin un singur tabel, mutat apoi "
   "dintr-un folder într-o bază de date care poate fi interogată.</p>"
   + ix("agenda", "Planul lecției",
        {"static": True, "titlu": "Planul lecției",
         "etape": [{"nume": n, "unde": u, "text": d} for n, u, d in AGENDA]},
        "Prima parte a lecției este despre pandas, a doua despre SQL.")
   + nota("Caietul lecției", "<code>04_curatarea_si_integrarea_datelor.ipynb</code>, secțiunile 4, 5 și 8: tabelul lat al regiunilor, perechile și îmbinările. Partea de baze de date nu are caiet: se lucrează pe site și în Neon.", True),
   manual=
   "<h2>Agregare și baze de date</h2>"
   "<p>Până acum fiecare sursă a stat în propriul fișier: SCI într-unul, "
   "migrația în altul, indicatorii Eurostat în al treilea. Această organizare "
   "funcționează cât timp sursele sunt analizate separat. Pentru o afirmație "
   "de forma „perechile de țări cu mulți migranți sunt și mai legate” este "
   "nevoie de un singur tabel.</p>"
   "<p>Unirea tabelelor pare o operație tehnică, dar este de fapt o decizie de "
   "cercetare: ce se păstrează atunci când o sursă nu conține o țară pe care "
   "cealaltă o conține. Fiecare tip de join dă un alt răspuns la această "
   "întrebare, iar răspunsul determină câte rânduri rămân în analiză.</p>"
   "<p>A doua parte a lecției mută rezultatul dintr-un CSV într-o bază de date "
   "PostgreSQL. Motivul nu este modernitatea, ci colaborarea: din momentul în "
   "care mai multe persoane lucrează pe aceleași date, fișierul devine o sursă "
   "de probleme.</p>"
   + ix("agenda", "Planul lecției",
        {"static": True, "titlu": "Planul lecției",
         "etape": [{"nume": n, "unde": u, "text": d} for n, u, d in AGENDA]})
   + nota("Caietul lecției", "<code>04_curatarea_si_integrarea_datelor.ipynb</code>, secțiunile 4, 5 și 8: tabelul lat al regiunilor, perechile și îmbinările. Partea de baze de date nu are caiet: se lucrează pe site și în Neon.", True))


sl("s2", "Cursul", "De ce nu ajunge un fișier",
   "<h2>Momentul în care CSV-ul devine o problemă</h2>"
   "<p>Criteriul nu este dimensiunea datelor, ci numărul de persoane care lucrează cu ele.</p>"
   + tabel(["Situație", "Cu fișiere", "Cu o bază de date"],
           [["Două persoane modifică simultan",
             "~date_final_v2_ANA.csv", "o singură copie, în care scriu ambele"],
            ["Selecția țărilor din UE, în 2022",
             "citirea întregului fișier și filtrarea în memorie", "~where ue and an = 2022"],
            ["Verificarea absenței duplicatelor",
             "cod scris de fiecare dată", "~primary key, baza refuză"],
            ["Zece tabele legate între ele",
             "zece fișiere și o convenție de nume", "~join, scris o dată"],
            ["Revenirea după o greșeală",
             "restaurare dintr-un backup, dacă există", "o ramură sau un punct de restaurare"]])
   + nota("De reținut", "Un CSV este suficient până la prima colaborare. Pragul "
                        "nu este numărul de rânduri, ci numărul de persoane."),
   manual=
   "<h2>Momentul în care CSV-ul devine o problemă</h2>"
   "<p>Întrebarea „de la câte rânduri este nevoie de o bază de date” este "
   "formulată greșit, pentru că dimensiunea este rareori motivul. Pandas "
   "lucrează fără dificultate cu câteva milioane de rânduri pe un laptop "
   "obișnuit, iar datele din proiectele cursului sunt mult sub acest volum.</p>"
   "<p>Motivele reale sunt altele: mai multe persoane care scriu în același "
   "loc, reguli care trebuie impuse automat (o țară nu poate apărea de două "
   "ori în același an) și interogări care nu trebuie rescrise de fiecare "
   "dată în Python.</p>"
   + tabel(["Situație", "Cu fișiere", "Cu o bază de date"],
           [["Două persoane modifică simultan",
             "~date_final_v2_ANA.csv", "o singură copie, în care scriu ambele"],
            ["Selecția țărilor din UE, în 2022",
             "citirea întregului fișier și filtrarea în memorie", "~where ue and an = 2022"],
            ["Verificarea absenței duplicatelor",
             "cod scris de fiecare dată", "~primary key, baza refuză"],
            ["Zece tabele legate între ele",
             "zece fișiere și o convenție de nume", "~join, scris o dată"],
            ["Revenirea după o greșeală",
             "restaurare dintr-un backup, dacă există", "o ramură sau un punct de restaurare"]])
   + nota("De reținut", "Un CSV este suficient până la prima colaborare. Pragul "
                        "nu este numărul de rânduri, ci numărul de persoane."),
   dupa=verif("c5-v1", 1,
              "O echipă are un tabel de 40.000 de rânduri și trei membri care "
              "lucrează pe el. Care este cel mai bun argument pentru o bază de date?",
              ["40.000 de rânduri sunt prea multe pentru pandas",
               "Trei persoane au nevoie de o singură copie a datelor, nu de trei",
               "Bazele de date sunt mai rapide",
               "Este practica obișnuită în industrie"],
              "Dimensiunea nu este problema. Problema sunt trei copii ale "
              "aceluiași fișier, modificate de trei persoane."))


# ===========================================================================
#  3-9. Unirea tabelelor
# ===========================================================================

sl("s3", "Unirea tabelelor", "Două operații, nu una",
   "<h2>Una sub alta sau una lângă alta</h2>"
   "<p>În limbajul curent, ambele operații se numesc „unirea tabelelor”. În cod "
   "sunt două funcții diferite, care răspund la întrebări diferite.</p>"
   + tabel(["", "Concatenare", "Merge / join"],
           [["Ce adaugă", "rânduri", "coloane"],
            ["Când", "aceleași coloane, surse diferite",
             "tabele diferite, cu o cheie comună"],
            ["Exemplu din proiect", "2020, 2021, 2022, descărcate separat",
             "SCI plus migrație, pe cod de țară"],
            ["În cod", "~pd.concat([a, b])", "~pd.merge(a, b, on=\"cod\")"],
            ["Risc principal", "coloane cu nume ușor diferite",
             "chei care nu se potrivesc"]])
   + nota("Criteriul de alegere",
          "Rezultatul trebuie să aibă mai multe rânduri sau mai multe coloane? "
          "Pentru rânduri, <code>concat</code>; pentru coloane, <code>merge</code>."),
   manual=
   "<h2>Una sub alta sau una lângă alta</h2>"
   "<p>Confuzia dintre cele două operații este cea mai frecventă greșeală la "
   "agregare și se evită ușor dacă întrebarea este pusă în forma potrivită: "
   "tabelul trebuie să crească pe verticală sau pe orizontală?</p>"
   "<p>Dacă datele Eurostat sunt descărcate an cu an și trebuie reunite într-un "
   "singur tabel cu toți anii, cresc rândurile, deci se folosește "
   "<code>concat</code>. Dacă tabelului cu SCI trebuie să i se adauge populația "
   "fiecărei țări, cresc coloanele, deci se folosește <code>merge</code>.</p>"
   + tabel(["", "Concatenare", "Merge / join"],
           [["Ce adaugă", "rânduri", "coloane"],
            ["Când", "aceleași coloane, surse diferite",
             "tabele diferite, cu o cheie comună"],
            ["Exemplu din proiect", "2020, 2021, 2022, descărcate separat",
             "SCI plus migrație, pe cod de țară"],
            ["În cod", "~pd.concat([a, b])", "~pd.merge(a, b, on=\"cod\")"],
            ["Risc principal", "coloane cu nume ușor diferite",
             "chei care nu se potrivesc"]])
   + nota("Criteriul de alegere",
          "Rezultatul trebuie să aibă mai multe rânduri sau mai multe coloane? "
          "Pentru rânduri, <code>concat</code>; pentru coloane, <code>merge</code>."))


sl("s4", "Unirea tabelelor", "Rezultatul fiecărui tip",
   "<h2>Câte rânduri rămân</h2>"
   "<p>Două tabele mici, cu aceeași cheie; fiecare are o valoare fără "
   "corespondent în celălalt. Fiecare tip de îmbinare se selectează pe rând.</p>"
   + ix("imbinare", "Pe două tabele reale", {
       "id": "c5-imbinare-feluri", "intai": {"q": "În stânga: MD, AT, DE, HU. În dreapta: AT, DE, HU, IT. Câte rânduri dă un inner join?", "variante": ["4", "3", "5", "8"], "corect": 1, "dupa": "Inner join păstrează doar cheile prezente în ambele tabele: AT, DE, HU. Moldova și Italia sunt eliminate fără niciun mesaj de eroare."}, "cheie": "cod",
       "stanga": STANGA, "dreapta": DREAPTA, "numeRez": "rezultat",
       "sarcina": "Câte rânduri rezultă din fiecare dintre cele cinci variante "
                  "și unde apar celule goale?",
       "explicatii": EXPLIC})
   + nota("De ce contează",
          "Cazul Moldovei nu este un artificiu didactic: pe datele cursului, "
          "<code>inner</code> elimină din analiză toate țările care nu "
          "raportează migrația, fără niciun semnal că au fost eliminate."),
   manual=
   "<h2>Câte rânduri rămân</h2>"
   "<p>Definițiile din documentație sunt corecte, dar abstracte: se rețin "
   "greu și se confundă ușor. Un join se înțelege cel mai bine pe două "
   "tabele mici, numărând rândurile rezultate.</p>"
   "<p>Tabelele de mai jos au trei chei comune (AT, DE, HU), una doar în "
   "stânga (MD: Moldova nu raportează migrația la Eurostat) și una doar în "
   "dreapta (IT, pentru că tabelul din stânga include doar patru parteneri ai "
   "României).</p>"
   + ix("imbinare", "Pe două tabele reale", {
       "id": "c5-imbinare-feluri", "intai": {"q": "În stânga: MD, AT, DE, HU. În dreapta: AT, DE, HU, IT. Câte rânduri dă un inner join?", "variante": ["4", "3", "5", "8"], "corect": 1, "dupa": "Inner join păstrează doar cheile prezente în ambele tabele: AT, DE, HU. Moldova și Italia sunt eliminate fără niciun mesaj de eroare."}, "cheie": "cod",
       "stanga": STANGA, "dreapta": DREAPTA, "numeRez": "rezultat",
       "sarcina": "Câte rânduri rezultă din fiecare dintre cele cinci variante?",
       "explicatii": EXPLIC})
   + nota("De ce contează",
          "Diferența dintre <code>inner</code> și <code>left</code> poate "
          "însemna douăzeci de țări eliminate din analiză fără niciun "
          "avertisment."))


sl("s5", "Unirea tabelelor", "Îmbinarea, în cod",
   "<h2>Îmbinarea în pandas</h2>"
   + ix("pas", "Două regiuni, două îmbinări", PAS_MERGE),
   manual="<h2>Îmbinarea în pandas</h2>"
   "<p>Sintaxa este scurtă; atenția trebuie să cadă pe verificările de după. "
   "Cele două linii de verificare de la final sunt mai importante decât "
   "îmbinarea în sine.</p>"
   + ix("pas", "Două regiuni, două îmbinări", PAS_MERGE)
   + ix("cod", "Adăugarea populației la tabelul SCI", {
       "id": "c5-cod-merge", "indiciu": "Coloana-cheie se indică prin parametrul on. Pentru a păstra toate rândurile din tabelul din stânga, tipul este \"left\". Valorile lipsă se identifică cu isna.",
       "iesire": "178 -> 178\n142", "fisier": "agregare/uneste.py",
       "sarcina": "Îmbinarea trebuie să păstreze toate țările din tabelul cu SCI.",
       "cod": "import pandas as pd\n\n"
              "sci = pd.read_csv(\"date/curat/sci.csv\")\n"
              "rom = pd.read_csv(\"date/curat/romani.csv\")\n\n"
              "d = pd.merge(sci, rom, {{1}}=\"cod\", how={{2}})\n\n"
              "print(len(sci), \"->\", len(d))\n"
              "print(d[\"romani\"].{{3}}().sum())",
       "goluri": {
           "1": {"ok": ["on"], "ajutor": "parametrul"},
           "2": {"ok": ["\"left\"", "'left'"], "ajutor": "tipul"},
           "3": {"ok": ["isna", "isnull"], "ajutor": "metoda"}},
       "laBine": "Verificările de la final sunt partea importantă.",
       "laRau": "Tipul îmbinării se scrie între ghilimele.",
       "explicatie": "Dacă <code>len(d)</code> este mai mare decât "
                     "<code>len(sci)</code>, tabelul din dreapta are chei duplicate."}))

sl("s5b", "Unirea tabelelor", "Adăugarea populației",
   "<h2>Adăugarea populației la tabelul SCI</h2>"
   + ix("cod", "Adăugarea populației la tabelul SCI", {
       "id": "c5-cod-merge", "indiciu": "Coloana-cheie se indică prin parametrul on. Pentru a păstra toate rândurile din tabelul din stânga, tipul este \"left\". Valorile lipsă se identifică cu isna.",
       "iesire": "178 -> 178\n142", "fisier": "agregare/uneste.py",
       "sarcina": "Îmbinarea trebuie să păstreze toate țările din tabelul cu SCI, inclusiv cele "
                  "fără date de migrație.",
       "cod": "import pandas as pd\n\n"
              "sci = pd.read_csv(\"date/curat/sci.csv\")\n"
              "rom = pd.read_csv(\"date/curat/romani.csv\")\n\n"
              "# tot ce este in sci ramane; din rom se adauga ce se potriveste\n"
              "d = pd.merge(sci, rom, {{1}}=\"cod\", how={{2}})\n\n"
              "# verificare: numarul de randuri nu trebuie sa creasca\n"
              "print(len(sci), \"->\", len(d))\n\n"
              "# cate tari au ramas fara date de migratie\n"
              "print(d[\"romani\"].{{3}}().sum())",
       "goluri": {
           "1": {"ok": ["on"], "ajutor": "parametrul"},
           "2": {"ok": ["\"left\"", "'left'"], "ajutor": "tipul, între ghilimele"},
           "3": {"ok": ["isna", "isnull"], "ajutor": "metoda"}},
       "laBine": "Cele două linii de verificare de la final sunt cele care "
                 "detectează erorile de îmbinare.",
       "laRau": "Tipul îmbinării se scrie ca șir de caractere, între ghilimele. "
                "Ultima metodă întoarce True acolo unde valoarea lipsește.",
       "explicatie": "<code>how=\"left\"</code> indică explicit tabelul de "
                     "bază. Verificarea de după este necesară: dacă "
                     "<code>len(d)</code> este mai mare decât <code>len(sci)</code>, "
                     "tabelul din dreapta are chei duplicate, iar îmbinarea a "
                     "multiplicat rândurile. Este problema de la slide-ul următor."}),
   manual="")


sl("s6", "Unirea tabelelor", "Rânduri multiplicate",
   "<h2>O eroare fără mesaj de eroare</h2>"
   "<p>Același tabel <code>sci</code>, dar în dreapta populația este dată pe ani. "
   "Patru rânduri în stânga, patru în dreapta. Se selectează <code>left</code>.</p>"
   + ix("imbinare", "Cheie duplicată în dreapta", {
       "id": "c5-imbinare-explozie", "intai": {"q": "În stânga sunt 4 țări. În dreapta, Moldova apare de trei ori (trei ani). Câte rânduri dă un left join?", "variante": ["4", "6", "12"], "corect": 1, "dupa": "Rândul Moldovei din stânga se potrivește cu toate cele trei rânduri ale ei din dreapta: un rând devine trei. 4 − 1 + 3 = 6."}, "poarta": False, "cheie": "cod",
       "stanga": STANGA, "dreapta": DUBLE, "numeRez": "rezultat",
       "feluri": ["inner", "left"],
       "sarcina": "Câte rânduri rezultă? Tabelul din stânga avea patru.",
       "explicatii": {
           "inner": "<b>Patru rânduri, din două chei.</b> Se potrivesc doar "
                    "MD și DE, dar MD apare de trei ori, fiindcă în dreapta "
                    "are trei ani. Valoarea SCI a fost copiată identic pe toate "
                    "trei. O medie a SCI calculată acum ar da Moldovei o "
                    "pondere de trei ori mai mare decât Germaniei.",
           "left": "<b>Șase rânduri din patru.</b> MD de trei ori, DE o "
                   "dată, plus AT și HU cu valori lipsă. Tabelul a crescut cu "
                   "cincizeci la sută fără niciun mesaj de eroare. Aici este "
                   "riscul: codul rulează, dar rezultatele finale sunt "
                   "greșite."}}),
   manual="<h2>O eroare fără mesaj de eroare</h2>"
   "<p>Un join potrivește fiecare rând din stânga cu fiecare rând din dreapta "
   "care are aceeași cheie. Când cheia este unică în ambele tabele, rezultatul "
   "este cel așteptat. Când nu este, tabelul crește, iar valorile din stânga "
   "se copiază pe fiecare rând nou.</p>"
   "<p>Nu apare niciun mesaj de eroare. Codul rulează, fișierul se scrie, iar "
   "mediile calculate după aceea sunt ponderate greșit, fiindcă unele țări "
   "apar de mai multe ori.</p>"
   + ix("imbinare", "Cheie duplicată în dreapta", {
       "id": "c5-imbinare-explozie", "intai": {"q": "În stânga sunt 4 țări. În dreapta, Moldova apare de trei ori (trei ani). Câte rânduri dă un left join?", "variante": ["4", "6", "12"], "corect": 1, "dupa": "Rândul Moldovei din stânga se potrivește cu toate cele trei rânduri ale ei din dreapta: un rând devine trei. 4 − 1 + 3 = 6."}, "poarta": False, "cheie": "cod",
       "stanga": STANGA, "dreapta": DUBLE, "numeRez": "rezultat",
       "feluri": ["inner", "left"],
       "sarcina": "Câte rânduri rezultă?",
       "explicatii": {
           "inner": "<b>Patru rânduri, din două chei.</b> MD apare de trei ori.",
           "left": "<b>Șase rânduri din patru.</b> Tabelul a crescut fără "
                   "niciun mesaj de eroare."}})
   + nota("Prevenire",
          "<code>validate=\"one_to_one\"</code> produce o eroare dacă cheia nu "
          "este unică. Dacă unitatea dorită este într-adevăr țara-an, cheia "
          "este <code>on=[\"cod\", \"an\"]</code>, nu doar codul."))

sl("s6b", "Unirea tabelelor", "Prevenirea",
   "<h2>Prevenirea multiplicării rândurilor</h2>"
   + nota("Prevenire",
          "<code>pd.merge(..., validate=\"one_to_one\")</code> produce o eroare "
          "dacă cheia nu este unică. Un singur parametru în plus evită "
          "refacerea analizei."),
   manual="",
   dupa=verif("c5-v4", 2,
              "Ce parametru face ca merge-ul să se oprească cu o eroare dacă o "
              "cheie apare de mai multe ori în dreapta?",
              ["how=\"inner\"",
               "on=[\"cod\", \"an\"]",
               "validate=\"one_to_one\"",
               "indicator=True"],
              "<code>validate</code> verifică relația dintre chei și produce o "
              "eroare dacă relația nu este cea declarată. "
              "<code>indicator=True</code> este și el util, dar doar adaugă o "
              "coloană care arată din ce tabel provine fiecare rând."))


sl("s7", "Unirea tabelelor", "Când cheile nu se potrivesc",
   "<h2>Aceeași țară, notații diferite</h2>"
   "<p>A doua capcană: cheile sunt scrise diferit, deci nu se potrivesc, iar "
   "<code>inner</code> întoarce un tabel gol, fără nicio explicație.</p>"
   + tabel(["Sursă", "Codul României", "Tip de cod"],
           [["Facebook SCI", "~RO", "ISO 3166-1 alpha-2"],
            ["Banca Mondială", "~ROU", "ISO 3166-1 alpha-3"],
            ["Eurostat", "~RO", "NUTS 0; excepții: Grecia este EL, Regatul Unit este UK"],
            ["Un fișier completat manual", "~Romania, România, ROMANIA", "niciun standard"]]),
   manual="<h2>Aceeași țară, notații diferite</h2>"
   "<p>Fiecare sursă are propriul nomenclator, iar codurile seamănă suficient "
   "de mult încât să pară interschimbabile, deși nu sunt.</p>"
   + tabel(["Sursă", "Codul României", "Tip de cod"],
           [["Facebook SCI", "~RO", "ISO 3166-1 alpha-2"],
            ["Banca Mondială", "~ROU", "ISO 3166-1 alpha-3"],
            ["Eurostat", "~RO", "NUTS 0; excepții: Grecia este EL, Regatul Unit este UK"],
            ["Un fișier completat manual", "~Romania, România, ROMANIA", "niciun standard"]])
   + "<p>O altă capcană nu este vizibilă la inspecție: tipul de date. "
     "<code>2020</code> citit ca șir de caractere nu se potrivește cu "
     "<code>2020</code> citit ca număr: când o cheie este numerică și cealaltă text, "
     "<code>merge</code> se oprește cu o eroare (<code>ValueError</code>); când ambele sunt "
     "text, dar scrise diferit (<code>\"2020\"</code> și <code>\"2020.0\"</code>), îmbinarea "
     "rulează fără eroare și pur și simplu nu găsește potriviri.</p>"
   + ix("cod", "Armonizarea cheilor", {
       "id": "c5-cod-chei", "indiciu": "Prima îmbinare se face după o coloană cu același nume în ambele tabele, deci on. Cheile comune sunt intersecția a două mulțimi: operatorul &. Când coloanele-cheie au nume diferite, se folosesc left_on și right_on.",
       "iesire": "171 chei comune din 178", "fisier": "agregare/chei.py",
       "sarcina": "Aducerea tabelului Băncii Mondiale la cheia SCI și verificarea potrivirii.",
       "cod": "harta = pd.read_csv(\"date/referinta/coduri.csv\")  # iso3, iso2\n"
              "bm = bm.merge(harta, {{1}}=\"iso3\", how=\"left\")\n\n"
              "comune = set(sci[\"cod\"]) {{2}} set(bm[\"iso2\"])\n"
              "print(len(comune), \"chei comune din\", len(set(sci[\"cod\"])))\n\n"
              "d = sci.merge(bm, left_on=\"cod\", {{3}}=\"iso2\", how=\"left\")",
       "goluri": {
           "1": {"ok": ["on"], "ajutor": "parametrul"},
           "2": {"ok": ["&", "intersection"], "ajutor": "operatorul"},
           "3": {"ok": ["right_on"], "ajutor": "parametrul"}},
       "laBine": "Cheile comune se numără înainte de îmbinare.",
       "laRau": "Intersecția a două mulțimi se scrie cu un singur caracter.",
       "explicatie": "Dacă din 178 de chei se potrivesc 12, problema ține de "
                     "coduri, nu de <code>merge</code>."}))

sl("s7b", "Unirea tabelelor", "Armonizarea cheilor",
   "<h2>Armonizarea cheilor</h2>"
   + ix("cod", "Armonizarea cheilor", {
       "id": "c5-cod-chei", "indiciu": "Prima îmbinare se face după o coloană cu același nume în ambele tabele, deci on. Cheile comune sunt intersecția a două mulțimi: operatorul &. Când coloanele-cheie au nume diferite, se folosesc left_on și right_on.",
       "iesire": "171 chei comune din 178", "fisier": "agregare/chei.py",
       "sarcina": "Banca Mondială folosește coduri de trei litere, SCI coduri "
                  "de două litere. Tabelul Băncii Mondiale se aduce la cheia SCI, "
                  "apoi se verifică potrivirea.",
       "cod": "# tabelul de traducere, adus o singura data\n"
              "harta = pd.read_csv(\"date/referinta/coduri.csv\")  # iso3, iso2\n\n"
              "# codul de 3 litere, adus la cel de 2\n"
              "bm = bm.merge(harta, {{1}}=\"iso3\", how=\"left\")\n\n"
              "# INAINTE de imbinare: cate chei se potrivesc\n"
              "comune = set(sci[\"cod\"]) {{2}} set(bm[\"iso2\"])\n"
              "print(len(comune), \"chei comune din\", len(set(sci[\"cod\"])))\n\n"
              "# abia acum, imbinarea\n"
              "d = sci.merge(bm, left_on=\"cod\", {{3}}=\"iso2\", how=\"left\")",
       "goluri": {
           "1": {"ok": ["on"], "ajutor": "parametrul"},
           "2": {"ok": ["&", "intersection"], "ajutor": "operatorul"},
           "3": {"ok": ["right_on"], "ajutor": "parametrul"}},
       "laBine": "Numărarea cheilor comune înainte de îmbinare previne "
                 "majoritatea erorilor de potrivire.",
       "laRau": "În Python, intersecția a două mulțimi se scrie cu un singur "
                "caracter. Când coloanele-cheie au nume diferite, "
                "<code>on</code> se înlocuiește cu doi parametri.",
       "explicatie": "Numărul tipărit la mijloc este diagnosticul: dacă din "
                     "178 de chei se potrivesc 12, problema nu ține de "
                     "<code>merge</code>, ci de coduri, și se rezolvă înainte "
                     "de îmbinare, nu după."}),
   manual="")


sl("s8", "Unirea tabelelor", "Unitatea de analiză",
   "<h2>Ce reprezintă un rând în tabelul final</h2>"
   "<p>Răspunsul se stabilește înainte de orice îmbinare. După îmbinare, "
   "tabelul are deja o formă, adesea alta decât cea necesară.</p>"
   + ix("sortare", "Ce unitate cere fiecare întrebare", {
       "id": "c5-sort-unitate", "poarta": False,
       "sarcina": "Ce unitate de analiză corespunde fiecărei întrebări de "
                  "cercetare?",
       "elemente": [
           {"t": "În ce țări trăiesc cei mai mulți români?", "cos": 0},
           {"t": "Care județe au cele mai multe legături în afara țării?", "cos": 1},
           {"t": "Perechile de țări cu mai mulți migranți sunt mai legate?", "cos": 2},
           {"t": "Județele din Moldova sunt legate de alte regiuni italiene decât cele din Ardeal?", "cos": 3}],
       "cosuri": [
           {"t": "o țară", "d": "un rând = o țară"},
           {"t": "o regiune", "d": "un rând = un județ sau o regiune"},
           {"t": "o pereche de țări", "d": "un rând = o legătură între țări"},
           {"t": "o pereche de regiuni", "d": "un rând = o legătură între regiuni"}],
       "laBine": "Datele SCI sunt diadice: unitatea naturală este perechea, nu "
                 "țara. Trecerea la unitatea „țară” cere o agregare explicită, "
                 "cu o funcție aleasă deliberat: sumă, medie sau maxim.",
       "explicatie": "Unitatea de analiză determină tot ce urmează: cheile "
                     "folosite la îmbinare, relația verificată cu "
                     "<code>validate</code> și sensul unei medii. Scrisă în "
                     "<code>decizii.md</code>, ocupă o propoziție; nescrisă, "
                     "devine o sursă frecventă de confuzie în proiect."})
   + nota("Pentru proiect",
          "Unitatea se formulează într-o propoziție: „un rând în tabelul final "
          "înseamnă ___”. Dacă membrii echipei dau răspunsuri diferite, aceasta "
          "este prima problemă de rezolvat, înaintea codului."),
   manual=
   "<h2>Ce reprezintă un rând în tabelul final</h2>"
   "<p>Unitatea de analiză este nivelul la care se fac observațiile: țara, "
   "perechea de țări, țara-an, individul, gospodăria. Pare o chestiune de "
   "vocabular, dar determină forma tabelului final și, prin aceasta, "
   "întrebările care pot fi puse.</p>"
   "<p>Datele cursului pornesc de la o unitate diadică: SCI măsoară legătura "
   "<em>dintre</em> două locuri, deci un rând este o pereche. O afirmație "
   "despre o țară cere agregarea perechilor, iar alegerea funcției de "
   "agregare este o decizie teoretică: suma indică „cât de conectată este "
   "țara în total”, media „cât de conectată este în medie”, iar maximul „cât "
   "de puternică este cea mai puternică legătură a ei”. Sunt trei mărimi "
   "diferite.</p>"
   + ix("sortare", "Ce unitate cere fiecare întrebare", {
       "id": "c5-sort-unitate", "poarta": False,
       "sarcina": "Ce unitate de analiză corespunde fiecărei întrebări?",
       "elemente": [
           {"t": "În ce țări trăiesc cei mai mulți români?", "cos": 0},
           {"t": "Care județe au cele mai multe legături în afara țării?", "cos": 1},
           {"t": "Perechile de țări cu mai mulți migranți sunt mai legate?", "cos": 2},
           {"t": "Județele din Moldova sunt legate de alte regiuni italiene decât cele din Ardeal?", "cos": 3}],
       "cosuri": [
           {"t": "o țară", "d": "un rând = o țară"},
           {"t": "o regiune", "d": "un rând = un județ sau o regiune"},
           {"t": "o pereche de țări", "d": "un rând = o legătură între țări"},
           {"t": "o pereche de regiuni", "d": "un rând = o legătură între regiuni"}],
       "laBine": "Datele SCI sunt diadice: unitatea naturală este perechea.",
       "explicatie": "Unitatea de analiză decide ce chei se folosesc la "
                     "îmbinare și ce înseamnă o medie."}))


sl("s9", "Unirea tabelelor", "Agregarea",
   "<h2>De la perechi la țări</h2>"
   + ix("prezice", "Ce face groupby", {
       "id": "c5-prezice-grup", "fisier": "agregare/proba.py",
       "cod": "import pandas as pd\n\n"
              "d = pd.DataFrame({\"tara\": [\"RO\", \"RO\", \"IT\"],\n"
              "                  \"sci\":  [10, 30, 5]})\n\n"
              "print(d.groupby(\"tara\")[\"sci\"].sum())",
       "intrebare": "Ce afișează?",
       "variante": ["tara\nIT     5\nRO    40", "tara\nRO    10\nRO    30\nIT     5",
                    "45", "tara\nRO    40\nIT     5"],
       "corect": 0,
       "indiciu": "groupby formează câte un grup pentru fiecare valoare distinctă din tara; sum însumează valorile din fiecare grup. În plus, grupurile sunt sortate după cheie.",
       "laBine": "Trei rânduri inițiale devin două rânduri, unul pe țară.",
       "explicatie": "Rândurile cu aceeași țară formează un grup, iar valorile se însumează: RO = 10 + 30 = 40, IT = 5. "
                     "Grupurile sunt afișate în ordine alfabetică, de aceea IT apare primul. Este aceeași schimbare a "
                     "unității de analiză, de la pereche la țară, ca în exercițiul de mai jos."}),
   manual="<h2>De la perechi la țări</h2>"
   "<p>Agregarea este etapa în care datele își schimbă unitatea de analiză. "
   "Este și etapa în care se iau, adesea implicit, decizii teoretice: funcția "
   "folosită pentru a rezuma mai multe rânduri într-unul singur.</p>"
   + ix("pas", "De la regiuni la țări", PAS_AGREG)
   + ix("cod", "Schimbarea unității de analiză", {
       "id": "c5-cod-agregare", "indiciu": "Gruparea se face cu groupby. Media se cere ca șir de caractere, la fel ca \"sum\" de deasupra: \"mean\". La final, reset_index transformă indexul de grupare înapoi în coloană.",
       "iesire": "(31684, 3)\n(178, 4)", "fisier": "agregare/agrega.py",
       "sarcina": "De la un rând pe pereche la un rând pe țară.",
       "cod": "print(d.shape)\n\n"
              "t = (d\n"
              "     .{{1}}(\"tara_sursa\")\n"
              "     .agg(total=(\"sci\", \"sum\"),\n"
              "          medie=(\"sci\", {{2}}),\n"
              "          parteneri=(\"tara_tinta\", \"nunique\"))\n"
              "     .{{3}}())\n\n"
              "print(t.shape)",
       "goluri": {
           "1": {"ok": ["groupby"], "ajutor": "metoda"},
           "2": {"ok": ["\"mean\"", "'mean'"], "ajutor": "funcția"},
           "3": {"ok": ["reset_index"], "ajutor": "metoda"}},
       "laBine": "<code>reset_index()</code> transformă cheia înapoi în coloană.",
       "laRau": "Al doilea gol se scrie ca șir de caractere, între ghilimele.",
       "explicatie": "Suma favorizează țările cu mulți parteneri, media nu "
                     "depinde de numărul de parteneri, iar numărul de parteneri "
                     "măsoară întinderea, nu intensitatea."}))

sl("s9b", "Unirea tabelelor", "De la regiuni la țări",
   "<h2>De la regiuni la țări</h2>"
   + ix("pas", "De la regiuni la țări", PAS_AGREG),
   manual="")

sl("s9c", "Unirea tabelelor", "Schimbarea unității",
   "<h2>Schimbarea unității de analiză</h2>"
   + ix("cod", "Schimbarea unității de analiză", {
       "id": "c5-cod-agregare", "indiciu": "Gruparea se face cu groupby. Media se cere ca șir de caractere, la fel ca \"sum\" de deasupra: \"mean\". La final, reset_index transformă indexul de grupare înapoi în coloană.",
       "iesire": "(31684, 3)\n(178, 4)", "fisier": "agregare/agrega.py",
       "sarcina": "Tabelul are un rând pe pereche. Obține un rând pe țară, "
                  "cu trei măsuri diferite ale conectării.",
       "cod": "# un rand pe perechea (tara_sursa, tara_tinta)\n"
              "print(d.shape)\n\n"
              "t = (d\n"
              "     .{{1}}(\"tara_sursa\")\n"
              "     .agg(total=(\"sci\", \"sum\"),\n"
              "          medie=(\"sci\", {{2}}),\n"
              "          parteneri=(\"tara_tinta\", \"nunique\"))\n"
              "     .{{3}}())\n\n"
              "# acum, un rand pe tara\n"
              "print(t.shape)",
       "goluri": {
           "1": {"ok": ["groupby"], "ajutor": "metoda"},
           "2": {"ok": ["\"mean\"", "'mean'"], "ajutor": "funcția, între ghilimele"},
           "3": {"ok": ["reset_index"], "ajutor": "metoda"},
       },
       "laBine": "<code>reset_index()</code> de la final transformă cheia "
                 "înapoi într-o coloană obișnuită. Fără el, cheia rămâne în index, "
                 "iar tabelul nu mai are o coloană pentru fiecare variabilă.",
       "laRau": "Primul gol este metoda de grupare. Al doilea se scrie ca șir "
                "de caractere, între ghilimele, la fel ca <code>\"sum\"</code> "
                "de deasupra.",
       "explicatie": "Cele trei măsuri nu sunt variante ale aceluiași lucru. "
                     "<code>total</code> favorizează țările cu mulți "
                     "parteneri, <code>medie</code> nu depinde de numărul de "
                     "parteneri, iar <code>parteneri</code> nu măsoară "
                     "intensitatea legăturilor, ci întinderea lor. Alegerea "
                     "dintre ele este teoretică, nu tehnică."}),
   manual="")


sl("s10", "Unirea tabelelor", "Join pe index",
   "<h2>Când cheia este indexul</h2>"
   "<p><code>df1.join(df2)</code> este un <code>merge</code> cu o singură "
   "presupunere: potrivirea se face pe index, nu pe o coloană.</p>"
   + tabel(["Cod", "Se potrivește pe", "Când se folosește"],
           [["~a.merge(b, on=\"cod\")", "coloana cod, în ambele tabele",
             "cazul obișnuit"],
            ["~a.join(b)", "indexul ambelor tabele", "după un groupby sau la serii de timp"],
            ["~a.merge(b, left_on=\"cod\", right_index=True)",
             "coloană în stânga, index în dreapta", "cazul mixt"],
            ["~a.join(b, how=\"inner\")", "index, doar potrivirile",
             "implicit, join este left, nu inner"]])
   + nota("De reținut",
          "<code>join</code> are implicit <code>how=\"left\"</code>, iar "
          "<code>merge</code> are <code>how=\"inner\"</code>. Două funcții "
          "care fac același lucru, cu valori implicite diferite: de aici "
          "provine o parte din confuzie."))


# ===========================================================================
#  11-18. Baze de date
# ===========================================================================

sl("s11", "Baze de date", "Ce este Neon",
   "<h2>Postgres, fără server de întreținut</h2>"
   "<p>Neon oferă PostgreSQL standard, găzduit în cloud: nu trebuie instalat "
   "și nu trebuie menținut pornit.</p>"
   + ix("flux", "Drumul unei interogări", {
       "id": "c5-flux-neon", "intai": {"q": "Prima interogare din ziua respectivă durează o secundă, a doua o zecime de secundă. De ce?", "variante": ["Baza a păstrat rezultatul în memorie", "Componenta de calcul era oprită și a pornit la prima cerere", "Conexiunea la internet era mai lentă la început"], "corect": 1, "dupa": "Neon oprește componenta de calcul (compute) când nu este folosită; datele (storage) rămân disponibile. Prima cerere o repornește, de aici secunda în plus."},
       "buton": "Trimite o interogare",
       "dus": "interogarea este trimisă", "intors": "rândurile sunt returnate",
       "gata": "rezultatul a fost primit",
       "titlu": "Selectează o componentă",
       "intro": "Patru componente prin care trece un <code>select</code>.",
       "statii": [
           {"n": "Scriptul Python", "et": "pandas", "ic": "🐍", "c": "ceas",
            "d": "<code>pd.read_sql(\"select ...\", con)</code>. Aici nu are "
                 "loc nicio prelucrare: interogarea este un șir de caractere "
                 "trimis mai departe."},
           {"n": "Conexiunea", "et": "psycopg", "ic": "🔌", "c": "salvie",
            "d": "Șirul de conectare specifică adresa bazei, utilizatorul și "
                 "canalul criptat. Se păstrează în <code>.env</code>, niciodată "
                 "în cod."},
           {"n": "Compute", "et": "pornește la cerere", "ic": "⚡", "c": "accent",
            "d": "Componenta care execută interogarea. Dacă nu a primit nicio "
                 "cerere timp de câteva minute, este oprită, iar prima cerere "
                 "o repornește. De aici denumirea „serverless” și tot de aici "
                 "întârzierea de o secundă la prima cerere."},
           {"n": "Storage", "et": "permanent", "ic": "🗄️", "c": "text-2",
            "d": "Datele propriu-zise, separate de componenta de calcul. "
                 "Separarea permite crearea unei ramuri: o copie a bazei pe "
                 "care se pot face experimente fără a modifica originalul."}]})
   + nota("De reținut",
          "Separarea dintre compute și storage permite ramuri similare celor "
          "din Git: datele rămân pe loc, iar peste ele pornește doar o altă "
          "componentă de calcul."),
   manual=
   "<h2>Postgres, fără server de întreținut</h2>"
   "<p>Neon este o platformă care oferă PostgreSQL complet gestionat, "
   "accesibil prin SQL standard. Tot ce este valabil pentru Postgres rămâne "
   "valabil: aceleași comenzi și aceleași tipuri; dintre extensii, sunt disponibile cele acceptate de platformă, printre ele PostGIS.</p>"
   "<p>Trei caracteristici o deosebesc de un Postgres instalat pe un server "
   "propriu:</p>"
   "<ul>"
   "<li><strong>Serverless.</strong> Componenta care execută interogările "
   "pornește automat la prima cerere și se oprește când nu mai este folosită. "
   "Costul depinde de utilizare, iar pentru un proiect de curs este, de "
   "obicei, zero.</li>"
   "<li><strong>Branching.</strong> Se poate crea o copie izolată a bazei, "
   "similară unei ramuri Git, pentru a testa o transformare fără a afecta "
   "datele validate.</li>"
   "<li><strong>Compute separat de storage.</strong> Mecanismul tehnic care "
   "face posibile primele două.</li>"
   "</ul>"
   + ix("flux", "Drumul unei interogări", {
       "id": "c5-flux-neon", "intai": {"q": "Prima interogare din ziua respectivă durează o secundă, a doua o zecime de secundă. De ce?", "variante": ["Baza a păstrat rezultatul în memorie", "Componenta de calcul era oprită și a pornit la prima cerere", "Conexiunea la internet era mai lentă la început"], "corect": 1, "dupa": "Neon oprește componenta de calcul (compute) când nu este folosită; datele (storage) rămân disponibile. Prima cerere o repornește, de aici secunda în plus."},
       "buton": "Trimite o interogare",
       "dus": "interogarea este trimisă", "intors": "rândurile sunt returnate",
       "gata": "rezultatul a fost primit",
       "titlu": "Selectează o componentă",
       "intro": "Patru componente prin care trece un <code>select</code>.",
       "statii": [
           {"n": "Scriptul Python", "et": "pandas", "ic": "🐍", "c": "ceas",
            "d": "O interogare SQL, trimisă mai departe ca șir de caractere."},
           {"n": "Conexiunea", "et": "psycopg", "ic": "🔌", "c": "salvie",
            "d": "Șirul de conectare se păstrează în <code>.env</code>, niciodată în cod."},
           {"n": "Compute", "et": "pornește la cerere", "ic": "⚡", "c": "accent",
            "d": "Pornește la prima cerere; de aici întârzierea de o secundă."},
           {"n": "Storage", "et": "permanent", "ic": "🗄️", "c": "text-2",
            "d": "Datele, separate de componenta de calcul. De aceea se pot "
                 "crea ramuri."}]}))


sl("s12", "Baze de date", "Postgres sau MySQL",
   "<h2>Două baze, două profiluri</h2>"
   + ix("prezice", "Alegerea bazei de date", {
       "id": "c5-prezice-baza", "poarta": False, "fisier": "baza/intrebari.sql",
       "cod": "-- contururile judetelor, in baza\n"
              "-- intrebarea: ce regiuni se invecineaza cu Clujul?\n"
              "select b.nume\n"
              "from regiuni a join regiuni b\n"
              "  on st_touches(a.contur, b.contur)\n"
              "where a.cod = 'RO113';",
       "intrebare": "Interogarea folosește o funcție spațială. Ce bază de date se folosește la curs pentru astfel de interogări?",
       "variante": ["MySQL: este mai rapid la citiri", "PostgreSQL, cu extensia PostGIS", "Pe orice bază SQL", "Pe niciuna: se poate face doar în Python"],
       "corect": 1,
       "indiciu": "st_touches este o funcție geografică. Care dintre cele două baze de date are o extensie geografică consacrată?",
       "laBine": "Pentru date eterogene, hărți și analiză: Postgres.",
       "explicatie": "<code>st_touches</code> este o funcție spațială standard; la curs este folosită din PostGIS, extensia geografică a lui Postgres. MySQL are și el funcții spațiale, dar mai puține. Niciuna dintre baze nu este "
                     "„mai bună” în absolut: MySQL este simplu și foarte rapid la citiri, potrivit pentru aplicații web cu trafic mare. "
                     "Postgres are tipuri bogate (JSONB) și extensii (PostGIS, pgvector), potrivite pentru analiză. "
                     "Proiectul cursului se potrivește clar cu Postgres.",
       "iesire": "  nume\n------------\n Bihor\n Sălaj\n Maramureș\n Bistrița-Năsăud\n Mureș\n Alba"})
   + tabel(["Diferență", "PostgreSQL", "MySQL"],
           [["Caracter", "puternic, flexibil, multe funcții avansate",
             "simplu, ușor, foarte rapid în aplicații web"],
            ["Tipuri de date", "JSONB, PostGIS, array-uri, tipuri proprii",
             "tipuri clasice, plus JSON simplu"],
            ["Performanță", "scrieri concurente și interogări analitice",
             "citiri rapide, CRUD"],
            ["Ecosistem", "extensii puternice: PostGIS, pgvector",
             "simplu, stabil, foarte răspândit în web"]]),
   manual=
   "<h2>Două baze, două profiluri</h2>"
   "<p>Întrebarea „care este mai bună” nu are răspuns; întrebarea „care este "
   "mai potrivită pentru o anumită utilizare” are.</p>"
   + tabel(["Diferență", "PostgreSQL", "MySQL"],
           [["Caracter", "puternic, flexibil, multe funcții avansate",
             "simplu, ușor, foarte rapid în aplicații web"],
            ["Tipuri de date", "JSONB, PostGIS, array-uri, tipuri proprii",
             "tipuri clasice, plus JSON simplu"],
            ["Performanță", "scrieri concurente și interogări analitice",
             "citiri rapide, CRUD"],
            ["Folosire", "analitică, aplicații complexe, date eterogene, GIS",
             "aplicații web mari, e-commerce, trafic intens"],
            ["Ecosistem", "extensii puternice: PostGIS, pgvector",
             "simplu, stabil, foarte răspândit în web"]])
   + ix("prezice", "Alegerea bazei de date", {
       "id": "c5-prezice-baza", "poarta": False, "fisier": "baza/intrebari.sql",
       "cod": "-- contururile judetelor, in baza\n"
              "-- intrebarea: ce regiuni se invecineaza cu Clujul?\n"
              "select b.nume\n"
              "from regiuni a join regiuni b\n"
              "  on st_touches(a.contur, b.contur)\n"
              "where a.cod = 'RO113';",
       "intrebare": "Interogarea folosește o funcție spațială. Ce bază de date se folosește la curs pentru astfel de interogări?",
       "variante": ["MySQL: este mai rapid la citiri", "PostgreSQL, cu extensia PostGIS", "Pe orice bază SQL", "Pe niciuna: se poate face doar în Python"],
       "corect": 1,
       "indiciu": "st_touches este o funcție geografică. Care dintre cele două baze de date are o extensie geografică consacrată?",
       "laBine": "Pentru date eterogene, hărți și analiză: Postgres.",
       "explicatie": "<code>st_touches</code> este o funcție spațială standard; la curs este folosită din PostGIS, extensia geografică a lui Postgres. MySQL are și el funcții spațiale, dar mai puține. Niciuna dintre baze nu este "
                     "„mai bună” în absolut: MySQL este simplu și foarte rapid la citiri, potrivit pentru aplicații web cu trafic mare. "
                     "Postgres are tipuri bogate (JSONB) și extensii (PostGIS, pgvector), potrivite pentru analiză. "
                     "Proiectul cursului se potrivește clar cu Postgres.",
       "iesire": "  nume\n------------\n Bihor\n Sălaj\n Maramureș\n Bistrița-Năsăud\n Mureș\n Alba"}))


sl("s13", "Baze de date", "Conectarea",
   "<h2>Șirul de conectare și păstrarea lui</h2>"
   "<p>Un singur șir conține adresa, utilizatorul și parola. Dacă ajunge pe "
   "GitHub, baza de date devine accesibilă oricui.</p>"
   + ix("cod", "Conectarea fără parolă în cod", {
       "id": "c5-cod-conectare", "indiciu": "Toate trei sunt importate în primele rânduri: funcția care citește .env, funcția din os care citește o variabilă de mediu (getenv) și funcția care creează motorul de conectare.",
       "iesire": "PostgreSQL 17.5 on x86_64-pc-linux-gnu, compiled by gcc ...", "fisier": "baza/conecteaza.py",
       "sarcina": "Șirul de conectare se citește din <code>.env</code>, nu din fișierul cu cod.",
       "cod": "import os\n"
              "import pandas as pd\n"
              "from dotenv import load_dotenv\n"
              "from sqlalchemy import create_engine\n\n"
              "# citirea .env: valorile intra in mediu\n"
              "{{1}}()\n\n"
              "# postgresql+psycopg://user:parola@host/baza?sslmode=require\n"
              "url = os.{{2}}(\"DATABASE_URL\")\n"
              "if not url:\n"
              "    raise SystemExit(\"lipseste DATABASE_URL din .env\")\n\n"
              "motor = {{3}}(url)\n\n"
              "# proba: daca aceasta linie ruleaza, conexiunea functioneaza\n"
              "print(pd.read_sql(\"select version()\", motor).iloc[0, 0])",
       "goluri": {
           "1": {"ok": ["load_dotenv"], "ajutor": "funcția"},
           "2": {"ok": ["getenv", "environ.get"], "ajutor": "funcția"},
           "3": {"ok": ["create_engine"], "ajutor": "funcția"}},
       "laBine": "Linia cu <code>raise</code> afișează un mesaj clar atunci "
                 "când depozitul este clonat fără <code>.env</code>, în locul "
                 "unei erori de conectare greu de interpretat.",
       "laRau": "Toate trei sunt importate în primele patru linii.",
       "explicatie": "<code>.env</code> se adaugă în <code>.gitignore</code> "
                     "înainte de primul <code>add</code>. În depozit se pune un "
                     "<code>.env.exemplu</code> cu numele variabilelor și "
                     "valori fictive, ca colegii să știe ce variabile trebuie "
                     "definite."}),
   manual=
   "<h2>Șirul de conectare și păstrarea lui</h2>"
   "<p>Neon furnizează un șir de forma "
   "<code>postgresql://utilizator:parola@gazdă/bază?sslmode=require</code>. "
   "Acesta conține tot ce este necesar pentru accesul la bază, inclusiv "
   "parola, în clar.</p>"
   "<p>Regula este simplă și nu are excepții: șirul se păstrează într-un fișier "
   "<code>.env</code>, iar <code>.env</code> este trecut în "
   "<code>.gitignore</code> de la început. În depozit se pune un "
   "<code>.env.exemplu</code> cu numele variabilelor și valori fictive.</p>"
   + ix("cod", "Conectarea fără parolă în cod", {
       "id": "c5-cod-conectare", "indiciu": "Toate trei sunt importate în primele rânduri: funcția care citește .env, funcția din os care citește o variabilă de mediu (getenv) și funcția care creează motorul de conectare.",
       "iesire": "PostgreSQL 17.5 on x86_64-pc-linux-gnu, compiled by gcc ...", "fisier": "baza/conecteaza.py",
       "sarcina": "Șirul de conectare se citește din <code>.env</code>.",
       "cod": "import os\n"
              "import pandas as pd\n"
              "from dotenv import load_dotenv\n"
              "from sqlalchemy import create_engine\n\n"
              "{{1}}()\n"
              "url = os.{{2}}(\"DATABASE_URL\")\n"
              "if not url:\n"
              "    raise SystemExit(\"lipseste DATABASE_URL din .env\")\n\n"
              "motor = {{3}}(url)\n"
              "print(pd.read_sql(\"select version()\", motor).iloc[0, 0])",
       "goluri": {
           "1": {"ok": ["load_dotenv"], "ajutor": "funcția"},
           "2": {"ok": ["getenv", "environ.get"], "ajutor": "funcția"},
           "3": {"ok": ["create_engine"], "ajutor": "funcția"}},
       "laBine": "Verificarea explicită înlocuiește o eroare de conectare greu "
                 "de interpretat cu un mesaj clar.",
       "laRau": "Toate trei sunt importate în primele patru linii.",
       "explicatie": "Dacă parola ajunge într-un commit, trebuie schimbată din "
                     "Neon: ștergerea din fișier nu o elimină din istoric."})
   + nota("Atenție", "Șirul de conectare conține parola în clar. Dacă ajunge "
                     "din greșeală într-un commit, ștergerea lui nu este "
                     "suficientă, pentru că rămâne în istoric. Parola trebuie "
                     "schimbată imediat din Neon."))


sl("s14", "Baze de date", "Scriere și citire",
   "<h2>Tabelul final, în baza de date</h2>"
   + ix("cod", "Încărcarea tabelului în Postgres", {
       "id": "c5-cod-tosql", "indiciu": "Dacă tabelul există deja, este înlocuit: \"replace\". Citirea din bază se face cu read_sql. Constrângerea care impune unicitatea cheii este primary key.",
       "iesire": "178 scrise, 178 gasite", "fisier": "baza/incarca.py",
       "sarcina": "Scrierea tabelului în bază, apoi citirea lui înapoi pentru verificare.",
       "cod": "d = pd.read_csv(\"date/curat/tabel_final.csv\")\n\n"
              "# scrierea tabelului; daca exista deja, este inlocuit\n"
              "d.to_sql(\"sci_tari\", motor, if_exists={{1}}, index=False)\n\n"
              "# citirea inapoi, pentru comparare\n"
              "verif = pd.{{2}}(\"select count(*) as n from sci_tari\", motor)\n"
              "print(len(d), \"scrise,\", verif[\"n\"][0], \"gasite\")\n\n"
              "# o cheie primara: baza refuza duplicatele\n"
              "with motor.begin() as c:\n"
              "    c.exec_driver_sql(\n"
              "        \"alter table sci_tari add {{3}} (cod)\")",
       "goluri": {
           "1": {"ok": ["\"replace\"", "'replace'"], "ajutor": "comportamentul dacă tabelul există"},
           "2": {"ok": ["read_sql", "read_sql_query"], "ajutor": "funcția"},
           "3": {"ok": ["primary key", "primary key", "PRIMARY KEY"],
                 "ajutor": "constrângerea"}},
       "laBine": "Cheia primară oferă o garanție pe care un CSV nu o are: "
                 "de acum baza respinge un al doilea rând cu același cod.",
       "laRau": "Primul gol se scrie ca șir de caractere, între ghilimele: "
                "<code>\"replace\"</code>, <code>\"append\"</code> sau "
                "<code>\"fail\"</code>.",
       "explicatie": "<code>if_exists=\"replace\"</code> șterge tabelul și îl "
                     "scrie din nou. Este opțiunea potrivită în faza de "
                     "construcție; într-o bază folosită și de alții, "
                     "<code>\"append\"</code> este mai prudent, iar "
                     "<code>\"fail\"</code> este cel mai prudent."}),
   manual=
   "<h2>Tabelul final, în baza de date</h2>"
   "<p><code>to_sql</code> și <code>read_sql</code> sunt cele două capete ale "
   "transferului. Între ele, principala grijă este comportamentul scriptului "
   "la a doua rulare.</p>"
   + ix("cod", "Încărcarea tabelului în Postgres", {
       "id": "c5-cod-tosql", "indiciu": "Dacă tabelul există deja, este înlocuit: \"replace\". Citirea din bază se face cu read_sql. Constrângerea care impune unicitatea cheii este primary key.",
       "iesire": "178 scrise, 178 gasite", "fisier": "baza/incarca.py",
       "sarcina": "Scrierea tabelului în bază, apoi citirea lui înapoi pentru verificare.",
       "cod": "d = pd.read_csv(\"date/curat/tabel_final.csv\")\n\n"
              "d.to_sql(\"sci_tari\", motor, if_exists={{1}}, index=False)\n\n"
              "verif = pd.{{2}}(\"select count(*) as n from sci_tari\", motor)\n"
              "print(len(d), \"scrise,\", verif[\"n\"][0], \"gasite\")\n\n"
              "with motor.begin() as c:\n"
              "    c.exec_driver_sql(\n"
              "        \"alter table sci_tari add {{3}} (cod)\")",
       "goluri": {
           "1": {"ok": ["\"replace\"", "'replace'"], "ajutor": "comportamentul dacă tabelul există"},
           "2": {"ok": ["read_sql", "read_sql_query"], "ajutor": "funcția"},
           "3": {"ok": ["primary key", "PRIMARY KEY"], "ajutor": "constrângerea"}},
       "laBine": "Cheia primară oferă o garanție pe care un CSV nu o are.",
       "laRau": "Primul gol se scrie între ghilimele.",
       "explicatie": "<code>\"replace\"</code> în faza de construcție, "
                     "<code>\"append\"</code> sau <code>\"fail\"</code> "
                     "într-o bază folosită și de alții."}))


sl("s15", "Baze de date", "SQL: noțiunile de bază",
   "<h2>Patru clauze și ordinea lor</h2>"
   "<p>Aceleași operații ca în pandas, scrise în limbajul bazei de date. "
   "Avantajul: filtrarea are loc în bază, iar înapoi vine doar rezultatul cerut.</p>"
   + ix("pas", "Ordinea de execuție", PAS_SQL),
   manual="<h2>Patru clauze și ordinea lor</h2>"
   "<p>Proiectul nu cere SQL avansat. Sunt suficiente cinci construcții, care "
   "acoperă aproape toate operațiile făcute în pandas.</p>"
   + tabel(["În pandas", "În SQL"],
           [["~d[d.cod == 'RO']", "~where cod = 'RO'"],
            ["~d.merge(t, on='cod')", "~join tari t on t.cod = d.cod"],
            ["~d.groupby('cod').sum()", "~group by cod"],
            ["~d.sort_values('sci', ascending=False)", "~order by sci desc"],
            ["~d.head(10)", "~limit 10"]])
   + ix("pas", "Ordinea de execuție", PAS_SQL)
   + ix("cod", "Scrierea interogării", {
       "id": "c5-cod-sql", "indiciu": "Două tabele se leagă cu join. Rândurile se filtrează cu where. Cele mai mari valori primele: ordine descrescătoare, desc.",
       "iesire": " geo | persoane |   sci\n-----+----------+--------\n IT  |  1073196 |  69327\n DE  |   776424 |  91228\n ES  |   620463 |  54179", "fisier": "baza/intrebari.sql",
       "sarcina": "Cele zece țări cu cei mai mulți cetățeni români, cu SCI-ul lor.",
       "cod": "select m.geo, m.persoane, s.sci\n"
              "from migratie m\n"
              "{{1}} legaturi s on s.tara_1 = 'RO' and s.tara_2 = m.geo\n"
              "{{2}} m.citizen = 'RO'\n"
              "order by m.persoane {{3}}\n"
              "limit 10;",
       "goluri": {
           "1": {"ok": ["join", "inner join", "JOIN"], "ajutor": "legarea tabelelor"},
           "2": {"ok": ["where", "WHERE"], "ajutor": "filtrarea"},
           "3": {"ok": ["desc", "DESC"], "ajutor": "ordinea"}},
       "laBine": "<code>join ... on</code> este echivalentul lui <code>pd.merge</code>.",
       "laRau": "Al treilea gol așază valorile mari primele.",
       "explicatie": "Ordinea de scriere nu este ordinea de execuție: "
                     "<code>where</code>, apoi grupare, apoi sortare, apoi "
                     "<code>limit</code>."}))

sl("s15b", "Baze de date", "Scrierea interogării",
   "<h2>Scrierea interogării</h2>"
   + ix("cod", "Scrierea interogării", {
       "id": "c5-cod-sql", "indiciu": "Două tabele se leagă cu join. Rândurile se filtrează cu where. Cele mai mari valori primele: ordine descrescătoare, desc.",
       "iesire": " geo | persoane |   sci\n-----+----------+--------\n IT  |  1073196 |  69327\n DE  |   776424 |  91228\n ES  |   620463 |  54179", "fisier": "baza/intrebari.sql",
       "sarcina": "Cele zece țări cu cei mai mulți cetățeni români și SCI-ul "
                  "României cu fiecare dintre ele.",
       "cod": "select\n"
              "    m.geo,\n"
              "    m.persoane,\n"
              "    s.sci\n"
              "from migratie m\n"
              "{{1}} legaturi s\n"
              "  on s.tara_1 = 'RO' and s.tara_2 = m.geo\n"
              "{{2}} m.citizen = 'RO'\n"
              "order by m.persoane {{3}}\n"
              "limit 10;",
       "goluri": {
           "1": {"ok": ["join", "inner join", "JOIN"], "ajutor": "legarea tabelelor"},
           "2": {"ok": ["where", "WHERE"], "ajutor": "filtrarea"},
           "3": {"ok": ["desc", "DESC"], "ajutor": "ordinea"}},
       "laBine": "<code>join ... on</code> este echivalentul lui "
                 "<code>pd.merge(..., on=...)</code>. Există aceleași tipuri: "
                 "<code>left join</code>, <code>full outer join</code>.",
       "laRau": "Primul gol leagă două tabele pe baza unei condiții. Al doilea "
                "filtrează rândurile. Al treilea așază cele mai mari valori primele.",
       "explicatie": "Ordinea de scriere nu este ordinea de execuție: baza "
                     "filtrează întâi (<code>where</code>), apoi grupează, "
                     "apoi sortează și, la final, limitează rezultatul "
                     "(<code>limit</code>). Cu <code>order by</code>, baza ordonează "
                     "întregul rezultat înainte să păstreze primele zece rânduri, "
                     "deci <code>limit 10</code> nu face interogarea de zece ori mai rapidă."})
   + nota("Rezultatul",
          "Italia, Germania și Spania conduc la migrație, dar SCI-urile lor nu "
          "urmează aceeași ordine. Este întrebarea din cursul 1, reprodusă de "
          "această dată printr-o interogare.", True),
   manual="")


sl("s16", "Baze de date", "Ramurile bazei",
   "<h2>Ramuri pentru date</h2>"
   "<p>Aceeași idee ca în Git, aplicată bazei de date în locul codului.</p>"
   + tabel(["Situație", "Fără ramură", "Cu ramură"],
           [["Testarea unei transformări mari",
             "copie manuală a bazei", "o ramură, în câteva secunde"],
            ["Testarea scriptului de încărcare",
             "scriere peste datele validate", "scriere în ramură, apoi comparare"],
            ["Doi colegi lucrează în paralel",
             "modifică aceleași tabele", "fiecare pe ramura proprie"],
            ["O eroare introdusă în date",
             "restaurare din backup, dacă există", "ștergerea ramurii"]])
   + nota("Pentru proiect",
          "Pasul nu este obligatoriu, dar are un cost mic: o ramură se creează "
          "înainte de încărcarea principală și se șterge după verificare. Este cea mai "
          "simplă protecție împotriva pierderii datelor."))


sl("s17", "Baze de date", "Bază sau pandas",
   "<h2>În bază sau în pandas?</h2>"
   "<p>Aceeași operație se poate scrie în ambele. Regula practică: "
   "<strong>filtrarea și agregarea în bază, analiza în pandas.</strong></p>"
   + ix("prezice", "Ce se transferă prin rețea", {
       "id": "c5-prezice-unde", "poarta": False, "fisier": "baza/unde.py",
       "cod": "# in baza: 40 de milioane de randuri (tara, an, sci)\n\n"
              "# A\n"
              "d = pd.read_sql(\"select * from legaturi\", con)\n"
              "m = d[d[\"an\"] == 2022].groupby(\"tara\")[\"sci\"].mean()\n\n"
              "# B\n"
              "m = pd.read_sql(\"select tara, avg(sci) from legaturi \"\n"
              "                \"where an = 2022 group by tara\", con)",
       "intrebare": "Ambele variante dau aceeași medie pe țară. Câte rânduri se transferă prin rețea în fiecare caz?",
       "variante": ["A: 40 de milioane · B: 40 de milioane", "A: 40 de milioane · B: câte un rând pe țară, sub 200",
                    "A: sub 200 · B: sub 200", "A: un rând · B: un rând"],
       "corect": 1,
       "indiciu": "În A, ce întoarce select *? În B, filtrarea și gruparea sunt făcute de bază, înainte de transfer.",
       "laBine": "Baza reduce datele; în pandas ajunge doar rezultatul.",
       "explicatie": "A aduce întregul tabel în memorie și abia apoi filtrează. În B, baza filtrează și grupează, apoi trimite înapoi un rând pe țară. "
                     "Regula: în bază, operațiile care reduc volume mari de date (filtrare, grupare, îmbinarea tabelelor mari); în pandas, "
                     "operațiile exploratorii pe volume mici (grafice, modele, variante de transformare).",
       "iesire": "A: 40.000.000 de rânduri aduse\nB: 178 de rânduri aduse"}),
   manual=
   "<h2>În bază sau în pandas?</h2>"
   "<p>Întrebarea apare la fiecare pas, iar răspunsul este aproape mereu "
   "același: baza reduce datele, iar în pandas se aduce doar rezultatul.</p>"
   "<p>Motivul nu este viteza bazei în sine, ci rețeaua: fiecare rând "
   "transferat are un cost. Un <code>select count(*) group by tara</code> "
   "trimite înapoi cel mult câteva sute de rânduri, câte unul pe țară; același calcul făcut prin citirea "
   "întregului tabel în pandas transferă milioane.</p>"
   + ix("prezice", "Ce se transferă prin rețea", {
       "id": "c5-prezice-unde", "poarta": False, "fisier": "baza/unde.py",
       "cod": "# in baza: 40 de milioane de randuri (tara, an, sci)\n\n"
              "# A\n"
              "d = pd.read_sql(\"select * from legaturi\", con)\n"
              "m = d[d[\"an\"] == 2022].groupby(\"tara\")[\"sci\"].mean()\n\n"
              "# B\n"
              "m = pd.read_sql(\"select tara, avg(sci) from legaturi \"\n"
              "                \"where an = 2022 group by tara\", con)",
       "intrebare": "Ambele variante dau aceeași medie pe țară. Câte rânduri se transferă prin rețea în fiecare caz?",
       "variante": ["A: 40 de milioane · B: 40 de milioane", "A: 40 de milioane · B: câte un rând pe țară, sub 200",
                    "A: sub 200 · B: sub 200", "A: un rând · B: un rând"],
       "corect": 1,
       "indiciu": "În A, ce întoarce select *? În B, filtrarea și gruparea sunt făcute de bază, înainte de transfer.",
       "laBine": "Baza reduce datele; în pandas ajunge doar rezultatul.",
       "explicatie": "A aduce întregul tabel în memorie și abia apoi filtrează. În B, baza filtrează și grupează, apoi trimite înapoi un rând pe țară. "
                     "Regula: în bază, operațiile care reduc volume mari de date (filtrare, grupare, îmbinarea tabelelor mari); în pandas, "
                     "operațiile exploratorii pe volume mici (grafice, modele, variante de transformare).",
       "iesire": "A: 40.000.000 de rânduri aduse\nB: 178 de rânduri aduse"}))


# ===========================================================================
#  19-21. Proiectul
# ===========================================================================

sl("s19", "Proiectul echipei", "Tabelul final",
   "<h2>Un tabel, o unitate, o bază</h2>"
   + ix("etape", "Pașii până la cursul următor", {
       "titlu": "Patru pași", "intro": "Detaliile apar la selectarea fiecărui pas.",
       "etape": [
           {"nume": "Formularea unității", "unde": "decizii.md",
            "text": "O propoziție: „un rând în tabelul final înseamnă "
                    "___”. Toată echipa trebuie să dea același răspuns."},
           {"nume": "Îmbinarea", "unde": "agregare/uneste.py",
            "text": "Un script care pornește de la fișierele curate și produce "
                    "un singur tabel, cu <code>how</code> scris explicit, cu "
                    "<code>validate</code> și cu numărul de rânduri tipărit "
                    "înainte și după îmbinare."},
           {"nume": "Încărcarea", "unde": "baza/incarca.py",
            "text": "Tabelul în Neon, cu o cheie primară. Șirul de conectare "
                    "în <code>.env</code>, iar <code>.env</code> în "
                    "<code>.gitignore</code>."},
           {"nume": "Interogarea", "unde": "baza/intrebari.sql",
            "text": "Un <code>select</code> scris de echipă, care răspunde la "
                    "un aspect al întrebării de cercetare. Nu trebuie să fie "
                    "complex, dar trebuie să fie propriu."}]}),
   manual="<h2>Un tabel, o unitate, o bază</h2>"
   "<p>Etapa de proiect a acestei lecții are patru părți, iar a patra arată "
   "că baza de date a fost folosită efectiv, nu doar creată.</p>"
   + ix("etape", "Pașii", {
       "titlu": "Patru pași", "intro": "Detaliile apar la selectarea fiecărui pas.",
       "etape": [
           {"nume": "Formularea unității", "unde": "decizii.md",
            "text": "„Un rând în tabelul final înseamnă ___”."},
           {"nume": "Îmbinarea", "unde": "agregare/uneste.py",
            "text": "Un script de la fișierele curate la un singur tabel."},
           {"nume": "Încărcarea", "unde": "baza/incarca.py",
            "text": "Tabelul în Neon, cu cheie primară, cu secretele în .env."},
           {"nume": "Interogarea", "unde": "baza/intrebari.sql",
            "text": "Un select propriu, legat de întrebarea de cercetare."}]})
   + ix("dovada", "Dovada", {
       "id": "c5-dovada-baza",
       "sarcina": "Comenzile se rulează, iar rezultatul afișat se lipește în câmpul corespunzător.",
       "pasi": [
           {"t": "Îmbinarea nu a multiplicat rândurile",
            "cmd": "python agregare/uneste.py",
            "gol": "linia cu înainte -> după",
            "cauta": r"\d+[\s\S]*\d+",
            "daca_nu": "Sunt necesare două numere: înainte și după."},
           {"t": "Tabelul este în bază",
            "cmd": "python -c \"import baza.conecteaza as b, pandas as pd; "
                   "print(pd.read_sql('select count(*) from sci_tari', b.motor))\"",
            "gol": "numărul afișat",
            "cauta": r"\d+",
            "daca_nu": "Trebuie verificată variabila DATABASE_URL din .env."},
           {"t": "Secretele nu sunt în depozit",
            "cmd": "git check-ignore -v .env",
            "gol": "linia afișată",
            "cauta": r"gitignore",
            "daca_nu": "Dacă nu se afișează nimic, .env nu este ignorat."}],
       "explicatie": "Ultimul pas este cel mai important dintre cele trei."}))

sl("s19d", "Proiectul echipei", "Dovada tabelului final",
   "<h2>Dovada tabelului final</h2>"
   "<p class=\"cheie\">Trei verificări, rulate local, cu rezultatul lipit în câmp.</p>"
   + ix("dovada", "Dovada", {
       "id": "c5-dovada-baza",
       "sarcina": "Comenzile se rulează, iar rezultatul afișat se lipește în câmpul corespunzător.",
       "pasi": [
           {"t": "Îmbinarea nu a multiplicat rândurile",
            "cmd": "python agregare/uneste.py",
            "gol": "linia cu înainte -> după",
            "cauta": r"\d+[\s\S]*\d+",
            "daca_nu": "Sunt necesare două numere: rândurile dinainte și cele "
                       "de după îmbinare. Dacă scriptul nu le tipărește, îi lipsește "
                       "linia de verificare de la slide-ul 5."},
           {"t": "Tabelul este în bază",
            "cmd": "python -c \"import baza.conecteaza as b, pandas as pd; "
                   "print(pd.read_sql('select count(*) from sci_tari', b.motor))\"",
            "gol": "numărul afișat",
            "cauta": r"\d+",
            "daca_nu": "Este necesar numărul de rânduri din tabel. Dacă apare o "
                       "eroare de conectare, trebuie verificată variabila DATABASE_URL din .env."},
           {"t": "Secretele nu sunt în depozit",
            "cmd": "git check-ignore -v .env",
            "gol": "linia afișată",
            "cauta": r"gitignore",
            "daca_nu": "Dacă nu se afișează nimic, <code>.env</code> nu este "
                       "ignorat și trebuie adăugat în <code>.gitignore</code> înainte de "
                       "următorul commit."}],
       "explicatie": "Ultimul pas este cel mai important dintre cele trei. "
                     "Celelalte două se pot corecta oricând; o parolă ajunsă "
                     "în istoricul depozitului, nu."}),
   manual="")


sl("s20", "Proiectul echipei", "Unitatea proiectului",
   "<h2>Formularea unității de analiză</h2>"
   + ix("asteptari", "Un rând în tabelul final", {
       "id": "c5-unitate", "tip": "unitate", "minim": 40,
       "sarcina": "Propoziția de completat: „Un rând în tabelul final înseamnă "
                  "___, iar cheia care îl identifică este ___.”",
       "exemplu": "Exemplu: un rând înseamnă o pereche de țări, cu SCI, "
                  "migranții în ambele direcții și distanța, iar cheia este "
                  "(tara_1, tara_2). Alt exemplu: un rând este o pereche "
                  "(județ românesc, provincie italiană), cu cheia (judet, provincie).",
       "multumesc": "Răspunsul va fi citit înainte de cursul următor și "
                    "comparat cu ce scrie în decizii.md."}),
   manual=
   "<h2>Formularea unității de analiză</h2>"
   "<p>Propoziția pare banală, dar formularea ei explicită scoate la iveală "
   "situațiile în care membrii echipei lucrează cu tabele de forme diferite.</p>"
   + ix("asteptari", "Un rând în tabelul final", {
       "id": "c5-unitate", "tip": "unitate", "minim": 40,
       "sarcina": "Propoziția de completat: „Un rând în tabelul final înseamnă "
                  "___, iar cheia care îl identifică este ___.”",
       "exemplu": "Exemplu: o pereche de țări, cu cheia (tara_1, tara_2).",
       "multumesc": "Răspunsul va fi citit înainte de cursul următor."}))


sl("s21", "Mai departe", "Pentru cursul următor",
   "<h2>La cursul 6: analiza exploratorie</h2>"
   "<p class=\"cheie\">Tabelul final se examinează: statistici descriptive, distribuții "
   "și ce arată un grafic, dar nu și un rezumat numeric.</p>"
   + tabel(["Pregătirea pentru cursul 6", "Unde"],
           [["Tabelul final, îmbinat", "~date/curat/tabel_final.csv"],
            ["Scriptul de îmbinare", "~agregare/uneste.py"],
            ["Tabelul încărcat în Neon", "o captură de ecran cu numărul de rânduri"],
            ["Unitatea de analiză, scrisă", "~decizii.md"],
            ["Un select propriu", "~baza/intrebari.sql"]])
   + surse("Documentația agregării și a bazei", [
       ("pandas: merge, join, concat", "https://pandas.pydata.org/docs/user_guide/merging.html", "cele cinci tipuri de îmbinare și <code>validate</code>"),
       ("pandas: groupby", "https://pandas.pydata.org/docs/user_guide/groupby.html", "grupare, <code>agg</code>, mai multe funcții deodată"),
       ("PostgreSQL: tutorialul", "https://www.postgresql.org/docs/current/tutorial.html", "<code>select</code>, <code>where</code>, <code>join</code>, <code>group by</code>, de la zero"),
       ("Neon: documentația", "https://neon.com/docs/introduction", "proiect, conectare, ramuri"),
   ]),
   manual=
   "<h2>Cursul 6: analiza exploratorie</h2>"
   "<p>Cu tabelul final construit, lecția următoare tratează examinarea lui: "
   "statistici descriptive, distribuții și vizualizare exploratorie, adică "
   "graficele făcute pentru analiză, nu pentru raport.</p>"
   + tabel(["Ce se aduce", "Unde"],
           [["Tabelul final, îmbinat", "~date/curat/tabel_final.csv"],
            ["Scriptul de îmbinare", "~agregare/uneste.py"],
            ["Tabelul încărcat în Neon", "o captură de ecran cu numărul de rânduri"],
            ["Unitatea de analiză, scrisă", "~decizii.md"],
            ["Un select propriu", "~baza/intrebari.sql"]])
   + surse("Documentația agregării și a bazei", [
       ("pandas: merge, join, concat", "https://pandas.pydata.org/docs/user_guide/merging.html", "cele cinci tipuri de îmbinare și <code>validate</code>"),
       ("pandas: groupby", "https://pandas.pydata.org/docs/user_guide/groupby.html", "grupare, <code>agg</code>, mai multe funcții deodată"),
       ("PostgreSQL: tutorialul", "https://www.postgresql.org/docs/current/tutorial.html", "<code>select</code>, <code>where</code>, <code>join</code>, <code>group by</code>, de la zero"),
       ("Neon: documentația", "https://neon.com/docs/introduction", "proiect, conectare, ramuri"),
   ]))


L.scrie_tot()
