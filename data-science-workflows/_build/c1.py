# -*- coding: utf-8 -*-
"""
Lecția 1: Introducere și configurare.

Rescrisă ca să fie mai scurtă și mai vizuală: 18 slide-uri în loc de 22, cu
tabelele și listele lungi înlocuite de blocuri pe care le atingi.

Ce s-a schimbat față de prima versiune, și de ce:
  - arborele tipurilor e desenat ca arbore, cu ramuri, nu ca un grid de
    cartonașe: ierarhia e tot rostul lui;
  - tipurile din SQL se aleg uitându-te la valorile adevărate ale tabelului,
    nu dintr-un tabel de referință urmat de un exercițiu cu trei goluri;
  - JSON-ul se desface sub ochii lor, pas cu pas, în loc să fie descris;
  - fiecare exercițiu cu cod are cel mult două goluri, și toate sunt pe
    datele cu care lucrăm chiar acum;
  - slide-urile care spuneau același lucru de două ori sunt unite.

Partea lungă nu s-a pierdut: stă în manual, care are aceleași exerciții.

Rulare:  python _build/c1.py
"""

from literatura import lecturi
from comun import Lectie, ix, verif, tabel, nota, surse


def carduri(lista):
    """Șase cutii cu titlul și întrebarea la vedere. Nimic de apăsat: pe un
    slide de alegere, textul ascuns sub un clic e text pe care nu-l citește
    nimeni."""
    return ('<div class="grila grila--3">' + "".join(
        f'<div class="card"><div class="card__t">{n}</div>'
        f'<p class="card__d">{d}</p></div>' for n, d in lista) + "</div>")

L = Lectie(1, "c1-introducere-si-mediu", "Introducere și configurare",
           "Proiectul, pașii unui proiect de analiză de date, tipurile de "
           "date, JSON și mediul de lucru.")
sl = L.sl


# --------------------------------------------------------------------------
# Mediul de dinaintea exercițiilor cu cod. Nimeni nu scrie un filtru fără să
# se uite întâi la tabel. Rândurile sunt adevărate, din date/sci-ro-tari.json.
# --------------------------------------------------------------------------

DATE_SCI = {
    "nume": "d",
    "fisier": "data/country.csv",
    "randuri": 31684,
    "coloane": [
        {"nume": "user_country", "tip": "object",
         "d": "codul de doua litere al tarii de unde pleaca legatura"},
        {"nume": "friend_country", "tip": "object",
         "d": "codul tarii spre care merge legatura"},
        {"nume": "user_region", "tip": "object",
         "d": "la nivel de țară, același cod ca user_country; în fișierele NUTS e codul regiunii"},
        {"nume": "friend_region", "tip": "object",
         "d": "la fel, pentru capătul celălalt"},
        {"nume": "scaled_sci", "tip": "int64",
         "d": "taria legaturii, scalata; se compara intre perechi, "
              "nu se citeste ca numar de prietenii"},
    ],
    "cap": [
        ["RO", "RO", "RO", "RO", 6252768],
        ["RO", "MD", "RO", "MD", 173794],
        ["RO", "AT", "RO", "AT", 124693],
    ],
    "capNota": "Cinci rânduri adevărate din fișier, dintre cele cu România pe "
               "primul capăt. Toate cele 178 de țări au aceleași cinci "
               "coloane. La nivel de țară, coloanele de regiune repetă codul țării; "
               "sunt acolo ca fișierul să arate la fel ca cele pe regiuni.",
}


# ===========================================================================
#  1-2. Cursul
# ===========================================================================

TEME = [
    (1, "Introducere și instalarea softurilor",
     "Ce unelte folosim și de ce fiecare. Mediul de lucru, structura unui proiect."),
    (1, "Concepte cheie pentru analiza datelor",
     "Tipuri de date în Python, în SQL și în fișiere spațiale. Tipuri de fișiere. Formatul JSON."),
    (2, "Colectarea datelor prin API",
     "Ce e un API, cum se citește o documentație, cum se face o cerere din cod."),
    (3, "Versionare și colaborare cu Git",
     "Istoric, reveniri, ramuri, pull request. Cum lucrează o echipă pe același cod fără să se calce."),
    (4, "Explorarea preliminară și curățarea",
     "Lipsuri, duplicate, tipuri greșite, coduri care nu se potrivesc între surse."),
    (5, "Baze de date",
     "Tabele, chei, interogări SQL. De ce un tabel de 31.684 de rânduri nu stă bine într-un fișier."),
    (5, "Agregarea datelor din surse diverse",
     "Îmbinarea pe o cheie comună. La date diadice, două îmbinări: una pentru fiecare capăt al perechii."),
    (6, "Analiza exploratorie și vizualizare",
     "Distribuții, relații, valori extreme, hărți. Grafice care lămuresc și grafice care induc în eroare."),
    (7, "Feature engineering",
     "Variabilele care răspund la întrebare nu se descarcă, se construiesc: rate, ponderi, distanțe, diferențe."),
    (7, "Aplicarea modelelor statistice",
     "Testarea formală a relației observate. Non-independența observațiilor, la date diadice."),
    (8, "Raportarea analizei și a rezultatelor",
     "Raport reproductibil, grafice pentru publicare, prezentarea proiectului."),
]

# Fișa fiecărei ședințe: ce înveți, ce faci la laborator, ce adaugi la
# proiect, cu ce unelte, și în ce etapă a fluxului de lucru ești. Etapele au
# culorile lor, aceleași ca în schema fluxului de la slide-ul 4.
SEDINTE = [
    {"c": 1, "scurt": "Introducere", "titlu": "Introducere și configurare", "etapa": "pregatire",
     "invata": ["ce e un flux de lucru în știința datelor", "ce măsoară SCI și ce formă au datele diadice",
                "tipurile de date în Python, SQL și fișiere spațiale", "cum se citește un JSON"],
     "caiet": "01_introducere_si_datele_proiectului.ipynb",
     "lab": "Primul caiet rulat pe date adevărate: country.csv, România și partenerii ei.",
     "proiect": "Mediul de lucru gata. Echipele se formează până la cursul 2.",
     "unelte": ["VS Code", "Python", "mediu virtual", "Jupyter", "pandas"]},
    {"c": 2, "scurt": "API", "titlu": "Colectarea datelor prin API", "etapa": "colectare",
     "invata": ["ce e un API REST și cum se citește documentația", "cererea, parametrii, paginarea, codurile de stare",
                "cum devine un răspuns JSON un tabel", "cubul JSON-stat de la Eurostat"],
     "caiet": "02_colectarea_datelor_prin_api.ipynb",
     "lab": "De la prima cerere la migrația de la Eurostat, salvată brut, cu data descărcării.",
     "proiect": "Primele date ale echipei: SCI și migrația, aduse din cod.",
     "unelte": ["requests", "API Eurostat", "HDX", "JSON"]},
    {"c": 3, "scurt": "Git", "titlu": "Versionare și colaborare cu Git", "etapa": "colectare",
     "invata": ["cele trei zone ale Git și commit-ul", "GitHub, ramuri, pull request, conflicte",
                "cum se caută literatura pe teorie și pe metodă", "cum se scrie o întrebare de cercetare"],
     "caiet": "03_surse_diverse_si_preprocesare.ipynb",
     "lab": "Nomenclatorul regiunilor, tabelul regional, migrația fără grupuri de țări; apoi Git.",
     "proiect": "Depozitul echipei pe GitHub, direcția proiectului și întrebarea voastră.",
     "unelte": ["Git", "GitHub", "pandas"]},
    {"c": 4, "scurt": "Curățare", "titlu": "Curățarea datelor", "etapa": "curatare",
     "invata": ["cele șase etape ale curățării", "lipsuri, duplicate, valori extreme, coduri care mint",
                "formatul lung și formatul lat", "dicționarul de date"],
     "caiet": "04_curatarea_si_integrarea_datelor.ipynb",
     "lab": "Calitatea și acoperirea datelor, capcanele codurilor de țară, secțiunile 1–3 și 6–7.",
     "proiect": "Datele curățate, cu dicționarul lor, în depozit.",
     "unelte": ["pandas", "Git"]},
    {"c": 5, "scurt": "Agregare și SQL", "titlu": "Agregare și baze de date", "etapa": "agregare",
     "invata": ["îmbinarea tabelelor și tipurile de join", "unitatea de analiză și agregarea",
                "două îmbinări la date diadice", "SQL, cât vă trebuie"],
     "caiet": "04_curatarea_si_integrarea_datelor.ipynb",
     "lab": "Tabelul lat al regiunilor, perechile și îmbinările, secțiunile 4–5 și 8.",
     "proiect": "Tabelul final, la unitatea de analiză aleasă de echipă.",
     "unelte": ["pandas", "SQL", "PostgreSQL"]},
    {"c": 6, "scurt": "Explorare", "titlu": "Analiza exploratorie", "etapa": "explorare",
     "invata": ["distribuții cu coadă lungă și top-uri", "norul de puncte și corelațiile",
                "comunitățile din rețea, pe hartă", "graficele care induc în eroare"],
     "caiet": "05_explorare_si_ipoteze.ipynb · 06_retele_si_indicatori_regionali.ipynb",
     "lab": "Distribuția, distanța, granița; apoi rețeaua județelor și comunitățile ei.",
     "proiect": "Explorarea echipei și primul tipar găsit în date.",
     "unelte": ["matplotlib", "geopandas", "networkx"]},
    {"c": 7, "scurt": "Model", "titlu": "Variabile derivate și model", "etapa": "model",
     "invata": ["construcția, transformarea și selecția variabilelor", "un model cu toate variabilele deodată",
                "cum se citesc coeficienții", "reziduurile și limitele modelului"],
     "caiet": "07_variabile_derivate_si_model.ipynb",
     "lab": "Patru modele, fiecare cu o variabilă în plus: distanța, migranții, rata la mie, granița.",
     "proiect": "Variabilele echipei și modelul care răspunde la întrebare.",
     "unelte": ["pandas", "statsmodels"]},
    {"c": 8, "scurt": "Raportare", "titlu": "Raportarea", "etapa": "raport",
     "invata": ["cum arată un raport reproductibil", "grafice pentru publicare",
                "ce aveți voie să spuneți din rezultate", "cum prezentați un proiect"],
     "caiet": "08_raport_si_proiect_final.ipynb",
     "lab": "Raportul final, pornit din depozitul echipei.",
     "proiect": "Prezentarea echipelor. La final, rezultatele articolului de la care a pornit cursul.",
     "unelte": ["Jupyter", "GitHub", "Markdown"]},
]

ETAPE = {
    "pregatire": "Definirea problemei", "colectare": "Colectarea datelor",
    "curatare": "Curățarea datelor", "agregare": "Baza de date și agregarea",
    "explorare": "Analiza exploratorie", "model": "Feature engineering și modelare",
    "raport": "Raportare și vizualizare",
}

CRONOLOGIE = {
    "titlu": "Apasă pe o ședință",
    "intro": "Unsprezece teme, opt ședințe. Fiecare ședință adaugă o piesă la proiectul echipei.",
    "sedinte": 8,
    "teme": [{"c": c, "n": n, "d": d} for c, n, d in TEME],
    "fise": SEDINTE,
    "etape": ETAPE,
    "azi": 1,
}

# Pașii pentru lecția 1, luați celulă cu celulă din 01_introducere_si_datele_proiectului.ipynb.
# Se lipesc în _build/c1.py.

PAS_TIPURI = {
    "fisier": "01_introducere.ipynb · 2. Variabile și tipuri",
    "intro": "Celulele de la începutul caietului. Rulează rând cu rând: în stânga e codul, în dreapta ce ține minte Python și ce afișează.",
    "cod": "tara = \"RO\"\nnumar_tari = 178\nore_de_studiu = 8.5\neste_student = True\nocupatie = None\n\n"
           "print(type(tara))\nprint(type(numar_tari))\nprint(type(ore_de_studiu))\nprint(type(este_student))\nprint(type(ocupatie))",
    "pasi": [
        {"l": 1, "set": {"tara": {"t": "str", "v": "RO"}},
         "txt": "<code>=</code> pune o valoare sub un nume. Ghilimelele fac din RO un <b>text</b> (<code>str</code>): un cod de țară e text, chiar dacă identifică ceva."},
        {"l": 2, "set": {"numar_tari": {"t": "int", "v": 178}},
         "txt": "Fără ghilimele, 178 e un <b>număr întreg</b> (<code>int</code>). Cu el se poate socoti."},
        {"l": 3, "set": {"ore_de_studiu": {"t": "float", "v": 8.5}},
         "txt": "Cu punct zecimal: <code>float</code>. În Python zecimalele se scriu cu punct, nu cu virgulă."},
        {"l": 4, "set": {"este_student": {"t": "bool", "v": True}},
         "txt": "<code>True</code> și <code>False</code>, cu majusculă: valori logice (<code>bool</code>). Orice comparație dă una dintre ele."},
        {"l": 5, "set": {"ocupatie": {"t": "NoneType", "v": None}},
         "txt": "<code>None</code> înseamnă „lipsește”. Nu e zero și nu e text gol: e absența valorii."},
        {"l": 7, "out": "<class 'str'>",
         "txt": "<code>type()</code> spune ce fel de valoare e sub un nume. E prima întrebare când ceva nu merge cum te aștepți."},
        {"l": 8, "out": "<class 'int'>", "txt": "178 e întreg."},
        {"l": 9, "out": "<class 'float'>", "txt": "8.5 are zecimale."},
        {"l": 10, "out": "<class 'bool'>", "txt": "True e o valoare logică."},
        {"l": 11, "out": "<class 'NoneType'>",
         "txt": "Și lipsa are un tip. Acum ai văzut toate cele cinci tipuri simple: le recunoști imediat, pe slide-ul următor."},
    ],
}

PAS_LISTE = {
    "fisier": "01_introducere.ipynb · liste și dicționare",
    "intro": "Două feluri de a ține mai multe valori împreună. Urmărește în memorie cum arată fiecare.",
    "cod": "tari = [\"RO\", \"IT\", \"ES\"]\nprint(tari[0])  # prima pozitie are indicele 0\nprint(len(tari))\n\n"
           "persoana = {\"name\": \"Ana\", \"age\": 24, \"city\": \"Cluj-Napoca\"}\nprint(persoana.keys())\nprint(persoana[\"city\"])",
    "pasi": [
        {"l": 1, "set": {"tari": {"t": "list", "v": ["RO", "IT", "ES"]}},
         "txt": "Parantezele drepte fac o <b>listă</b>: valori puse în ordine. Fiecare are o <b>poziție</b>, scrisă deasupra căsuței."},
        {"l": 2, "out": "RO", "hl": {"var": "tari", "k": 0},
         "txt": "<code>tari[0]</code> cere valoarea de pe poziția 0. Numărătoarea începe de la <b>0</b>, nu de la 1: prima țară e la 0."},
        {"l": 3, "out": "3", "txt": "<code>len()</code> numără elementele: 3. Ultima poziție e deci 2."},
        {"l": 5, "set": {"persoana": {"t": "dict", "v": {"name": "Ana", "age": 24, "city": "Cluj-Napoca"}}},
         "txt": "Acoladele fac un <b>dicționar</b>: perechi <b>cheie: valoare</b>. Aici nu contează ordinea, contează numele cheii."},
        {"l": 6, "out": "dict_keys(['name', 'age', 'city'])",
         "txt": "<code>.keys()</code> arată cheile. E primul lucru pe care îl ceri unui dicționar pe care nu-l cunoști."},
        {"l": 7, "out": "Cluj-Napoca", "hl": {"var": "persoana", "k": "city"},
         "txt": "<code>persoana[\"city\"]</code> cere valoarea cheii <code>city</code>. Listă: <b>poziție</b>. Dicționar: <b>cheie</b>. Cu asta citești orice JSON."},
    ],
}

PERS = [
    {"id": 1, "name": "Ana Popescu", "age": 24, "city": "Cluj-Napoca",
     "hobbies": ["lectură", "drumeții", "fotografie"], "student": True,
     "study_hours_per_week": 8.5, "occupation": None},
    {"id": 2, "name": "Mihai Ionescu", "age": 29, "city": "București",
     "hobbies": ["ciclism", "muzică"], "student": False,
     "study_hours_per_week": 0.0, "occupation": "bibliotecar"},
    {"id": 3, "name": "Elena Marin", "age": 26, "city": "Timișoara",
     "hobbies": ["înot", "lectură", "călătorii"], "student": True,
     "study_hours_per_week": 6.0, "occupation": "asistent de cercetare"},
]

PAS_JSON = {
    "fisier": "01_introducere.ipynb · 4. JSON",
    "intro": "Fișierul persoane.json din caiet: trei persoane fictive. Coborâm pas cu pas până la o singură valoare.",
    "cod": "import json\nwith open(\"exemple_curs1/persoane.json\",\n"
           "          encoding=\"utf-8\") as fisier:\n"
           "    user_data = json.load(fisier)\n\nprint(user_data.keys())\n"
           "users = user_data[\"users\"]\nprint(len(users))\n\n"
           "prima_persoana = users[0]\nprint(prima_persoana[\"name\"])\n"
           "print(user_data[\"users\"][0][\"hobbies\"][1])",
    "pasi": [
        {"l": 4, "set": {"user_data": {"t": "dict", "v": {"users": PERS}}},
         "txt": "<code>json.load</code> citește fișierul și îl transformă în dicționare și liste Python. Ce e afară e un dicționar cu o singură cheie."},
        {"l": 6, "out": "dict_keys(['users'])",
         "txt": "Prima întrebare, mereu: ce chei are? Una singură, <code>users</code>."},
        {"l": 7, "set": {"users": {"t": "list", "v": PERS}}, "hl": {"var": "user_data", "k": "users"},
         "txt": "Intrăm pe cheia <code>users</code>. Valoarea ei e o <b>listă</b>: fiecare căsuță e o persoană."},
        {"l": 8, "out": "3", "txt": "Trei persoane, pe pozițiile 0, 1 și 2."},
        {"l": 10, "set": {"prima_persoana": {"t": "dict", "v": PERS[0]}}, "hl": {"var": "users", "k": 0},
         "txt": "<code>users[0]</code> e prima persoană. Ea însăși e un dicționar, cu nume, oraș, hobby-uri…"},
        {"l": 11, "out": "Ana Popescu", "hl": {"var": "prima_persoana", "k": "name"},
         "txt": "Cheia <code>name</code> dă numele. Am ajuns la o valoare."},
        {"l": 12, "out": "drumeții", "hl": {"var": "prima_persoana", "k": "hobbies"},
         "txt": "Tot drumul, într-un rând, citit de la stânga la dreapta: lista <code>users</code> → poziția 0 → cheia <code>hobbies</code> → poziția 1. Al doilea hobby: drumeții."},
    ],
}

PAS_SCI = {
    "fisier": "01_introducere.ipynb · 5. Primul contact cu SCI",
    "intro": "Fișierul adevărat, country.csv. Aceleași idei, pe un tabel: întâi te uiți cât e de mare, apoi păstrezi doar ce te interesează.",
    "cod": "import pandas as pd\nsci = pd.read_csv(\"data/country.csv\", keep_default_na=False)\nprint(sci.shape)\n\n"
           "conditie_ro = sci[\"user_country\"] == \"RO\"\nro = sci[conditie_ro]\nprint(len(ro))\n\n"
           "ro_extern = ro[ro[\"friend_country\"] != \"RO\"]\nprint(len(ro_extern))\n\n"
           "top_ro = ro_extern.sort_values(\"scaled_sci\", ascending=False)\n"
           "print(top_ro[\"friend_country\"].head(6).tolist())",
    "pasi": [
        {"l": 2, "set": {"sci": {"t": "DataFrame", "v": {
            "cols": ["user_country", "friend_country", "scaled_sci"],
            "rows": [["NI", "BS", 2066], ["…", "…", "…"]],
            "nota": "31.684 de rânduri: câte unul pentru fiecare pereche de țări"}}},
         "txt": "<code>pd.read_csv</code> citește fișierul într-un <b>tabel</b> (DataFrame). <code>keep_default_na=False</code>: NA e Namibia, nu o valoare lipsă."},
        {"l": 3, "out": "(31684, 5)",
         "txt": "<code>.shape</code> dă (rânduri, coloane). 31.684 = 178 × 178: fiecare țară cu fiecare, inclusiv cu ea însăși."},
        {"l": 5, "set": {"conditie_ro": {"t": "Series", "v": {
            "rows": [["0", "False"], ["1", "False"], ["…", "…"]],
            "nota": "câte un True sau False pentru fiecare rând; 178 sunt True"}}},
         "txt": "<code>==</code> compară (un singur <code>=</code> atribuie!). Comparația se face pe fiecare rând și dă o coloană de True și False."},
        {"l": 6, "set": {"ro": {"t": "DataFrame", "v": {
            "cols": ["user_country", "friend_country", "scaled_sci"],
            "rows": [["RO", "CI", 640], ["RO", "ES", 54179], ["RO", "MW", 205]],
            "nota": "178 de rânduri"}}},
         "txt": "<code>sci[conditie_ro]</code> păstrează doar rândurile unde condiția e True: perechile care pleacă din România."},
        {"l": 7, "out": "178", "txt": "178 de rânduri: România cu fiecare țară, inclusiv RO–RO."},
        {"l": 9, "set": {"ro_extern": {"t": "DataFrame", "v": {
            "cols": ["user_country", "friend_country", "scaled_sci"],
            "rows": [["RO", "CI", 640], ["RO", "ES", 54179], ["RO", "MW", 205]],
            "nota": "177 de rânduri, fără RO–RO"}}},
         "txt": "<code>!=</code> înseamnă „diferit de”. Scoatem perechea România–România: vrem partenerii din afară."},
        {"l": 10, "out": "177", "txt": "177 de parteneri externi."},
        {"l": 12, "set": {"top_ro": {"t": "DataFrame", "v": {
            "cols": ["friend_country", "scaled_sci"],
            "rows": [["MD", 173794], ["AT", 124693], ["DE", 91228]],
            "nota": "aceleași 177 de rânduri, de la cel mai legat în jos"}}},
         "txt": "<code>sort_values</code> ordonează după o coloană; <code>ascending=False</code> pune valorile mari primele."},
        {"l": 13, "out": "['MD', 'AT', 'DE', 'HU', 'IE', 'IT']",
         "txt": "Primii șase parteneri. Italia, cu cei mai mulți români, e abia a șasea. Ghicitoarea semestrului."},
    ],
}


PZ_INDEX = ix("prezice", "Liste și dicționare", {
       "id": "c1-prezice-index", "fisier": "01_introducere.ipynb · liste și dicționare",
       "cod": "tari = [\"RO\", \"IT\", \"ES\"]\n"
              "persoana = {\"name\": \"Ana\", \"city\": \"Cluj-Napoca\"}\n\n"
              "print(tari[1], persoana[\"city\"])",
       "intrebare": "Ce afișează?",
       "variante": ["RO Ana", "IT Cluj-Napoca", "RO Cluj-Napoca", "IT city"],
       "corect": 1,
       "indiciu": "Într-o listă, numărătoarea începe de la 0. Într-un dicționar, între paranteze pui cheia și primești valoarea.",
       "laBine": "Indice pentru liste, cheie pentru dicționare: asta e tot drumul prin JSON.",
       "explicatie": "<code>tari[1]</code> e al doilea element, pentru că primul e <code>tari[0]</code>. "
                     "<code>persoana[\"city\"]</code> dă valoarea cheii. Cu aceste două mișcări "
                     "ajungi la orice valoare dintr-un răspuns JSON, oricât de adânc."})

DIADIC_SLIDE = ix("cod", "Taie o felie din matrice", {
       "id": "c1-cod-diadic", "fisier": "diadic.py", "date": DATE_SCI,
       "sarcina": "Păstrează doar perechile care pleacă din România. Numele coloanelor sunt în panou.",
       "cod": "import pandas as pd\n\n"
              "d = pd.read_csv(\"data/country.csv\", keep_default_na=False)\n"
              "print(len(d))                  # 31684\n\n"
              "# doar perechile care pleaca din Romania\n"
              "ro = d[d[{{1}}] == {{2}}]\n"
              "print(len(ro))                 # 178",
       "goluri": {
           "1": {"ok": ["\"user_country\"", "'user_country'"], "ajutor": "coloana"},
           "2": {"ok": ["\"RO\"", "'RO'"], "ajutor": "codul"}},
       "indiciu": "Pe stânga lui <code>==</code> stă coloana (o alegi cu <code>d[\"...\"]</code>), "
                  "pe dreapta valoarea căutată. Amândouă sunt text, deci între ghilimele.",
       "iesire": "31684\n178",
       "laBine": "178 de rânduri: România cu fiecare țară din set, inclusiv cu ea însăși.",
       "laRau": "Numele coloanei și codul se scriu între ghilimele, ca text.",
       "explicatie": "Fixezi un capăt al perechii și obții o listă monadică: "
                     "178 de rânduri, câte unul pentru fiecare țară. Asta e "
                     "mișcarea pe care o faci de fiecare dată când vrei să te "
                     "uiți la date diadice cu ochiul."})

DIADIC_MANUAL = ix("cod", "Taie o felie din matrice", {
       "id": "c1-cod-diadic", "fisier": "diadic.py", "date": DATE_SCI,
       "sarcina": "Păstrează doar perechile care pleacă din România.",
       "cod": "import pandas as pd\n\n"
              "d = pd.read_csv(\"data/country.csv\", keep_default_na=False)\n"
              "print(len(d))                  # 31684\n\n"
              "ro = d[d[{{1}}] == {{2}}]\n"
              "print(len(ro))                 # 178",
       "goluri": {
           "1": {"ok": ["\"user_country\"", "'user_country'"], "ajutor": "coloana"},
           "2": {"ok": ["\"RO\"", "'RO'"], "ajutor": "codul"}},
       "laBine": "178 de rânduri: România cu fiecare țară, inclusiv cu ea însăși.",
       "laRau": "Numele coloanei se scrie între ghilimele.",
       "explicatie": "Fixezi un capăt al perechii și obții o listă monadică."})


import json as _json, pathlib as _pl
_EXPL = _json.loads((_pl.Path(__file__).resolve().parent.parent / "date" / "explorator.json").read_text(encoding="utf-8"))
ROMANI = _EXPL["migratie"]["RO"]
RAPORT = _EXPL["raportoare"]

sl("s1", "Cursul", "Despre ce e cursul",
   "<h2>Fluxuri de lucru pentru știința datelor</h2>"
   "<p class=\"cheie\">Un drum complet, de la o întrebare la un rezultat în "
   "care poți avea încredere.</p>"
   + ix("semestru", "Opt ședințe", CRONOLOGIE),
   manual=
   "<h2>Fluxuri de lucru pentru știința datelor</h2>"
   "<p>Cursul acoperă drumul complet al unui proiect de analiză de date: de la "
   "formularea întrebării până la un raport pe care altcineva îl poate citi, "
   "reproduce și critica. Nu e un curs de statistică și nu e un curs de "
   "programare; e despre felul în care se leagă ele într-un proces care "
   "funcționează și în echipă, nu doar pe laptopul tău.</p>"
   "<p>Unsprezece teme, împărțite pe opt ședințe. Fiecare ședință adaugă o "
   "piesă la proiectul vostru, iar la final predați un depozit de cod, nu un "
   "fișier.</p>"
   "<p>Tot semestrul lucrăm pe aceeași întrebare, ca într-o cercetare "
   "adevărată: cât de legate sunt locurile Europei pe Facebook, și cât din "
   "asta se explică prin oamenii care au migrat între ele. Eu o duc până la "
   "un articol, voi o duceți până la proiectul echipei.</p>"
   + ix("semestru", "Temele semestrului", CRONOLOGIE)
   + nota("Caietul de azi", "<code>01_introducere_si_datele_proiectului.ipynb</code>. Pentru cine vrea mai mult: <code>00_explorare_sci.ipynb</code>, o primă explorare a SCI pe județe.", True)
   + "<h3>Agenda primei ore</h3>"
   "<ol><li>Evaluarea cunoștințelor și a așteptărilor</li>"
   "<li>Prezentarea proiectului</li>"
   "<li>Pașii unui proiect de analiză de date</li>"
   "<li>Configurarea unui mediu de lucru virtual</li>"
   "<li>Tipuri de date în știința datelor</li>"
   "<li>Formatul JSON</li></ol>"
   + nota("La final de oră", "Ai mediul de lucru pregătit și primul tău caiet "
          "rulat pe date adevărate. Echipa o formezi până la cursul 2."))


sl("s2", "Cursul", "Ce știi deja",
   "<h2>Unde ești acum</h2>"
   + ix("autoevaluare", "Un minut, nu se notează", {
       "id": "c1-autoevaluare",
       "teme": [
           {"cheie": "python", "t": "Python", "d": "variabile, liste, dicționare, funcții"},
           {"cheie": "linie", "t": "Linia de comandă", "d": "terminal, cd, rularea unui script"},
           {"cheie": "git", "t": "Git și GitHub", "d": "commit, branch, lucru în echipă"},
           {"cheie": "sql", "t": "SQL", "d": "SELECT, JOIN, tabele"},
           {"cheie": "api", "t": "API-uri", "d": "a cere date unui serviciu, prin cod"},
           {"cheie": "stat", "t": "Statistică", "d": "distribuții, corelație, regresie"},
       ]})
   + ix("asteptari", "Ce aștepți de la curs", {
       "id": "c1-asteptari",
       "sarcina": "Două-trei rânduri. Le citesc pe toate înainte de cursul "
                  "următor, și ajustez ce pot.",
       "exemplu": "De exemplu: vreau să pot lua singur date de pe un site și "
                  "să le pun cap la cap, fără să aștept pe cineva."}),
   manual=
   "<h2>Unde ești acum</h2>"
   "<p>Cursul pornește de la zero pe partea de unelte, dar o grupă nu e "
   "niciodată omogenă. Evaluarea de mai jos nu contează la notă: îmi spune de "
   "unde pornim, ca să nu pierd o oră explicând ce știe toată lumea, nici să "
   "sar peste ce nu știe nimeni.</p>"
   + ix("autoevaluare", "Nu se notează", {
       "id": "c1-autoevaluare",
       "teme": [
           {"cheie": "python", "t": "Python", "d": "variabile, liste, dicționare, funcții"},
           {"cheie": "linie", "t": "Linia de comandă", "d": "terminal, cd, rularea unui script"},
           {"cheie": "git", "t": "Git și GitHub", "d": "commit, branch, lucru în echipă"},
           {"cheie": "sql", "t": "SQL", "d": "SELECT, JOIN, tabele"},
           {"cheie": "api", "t": "API-uri", "d": "a cere date unui serviciu, prin cod"},
           {"cheie": "stat", "t": "Statistică", "d": "distribuții, corelație, regresie"},
       ]})
   + "<h3>Și așteptările</h3>"
   "<p>Cealaltă jumătate a întrebării. Un curs se poate preda în multe feluri, "
   "iar ce scrieți aici chiar schimbă accentele: dacă jumătate din grupă vrea "
   "în primul rând să scoată date din surse publice, insist pe API-uri; dacă "
   "majoritatea vine cu o temă de licență în cap, insist pe formularea "
   "întrebării și pe raport.</p>"
   + ix("asteptari", "Ce aștepți de la curs", {
       "id": "c1-asteptari",
       "sarcina": "Două-trei rânduri. Le citesc pe toate.",
       "exemplu": "De exemplu: vreau să pot lua singur date de pe un site și "
                  "să le pun cap la cap, fără să aștept pe cineva."}))


# ===========================================================================
#  3. Softuri și conturi
# ===========================================================================

UNELTE = [
    # (grupa, nume cu link, la ce, când)
    ("Pe calculatorul tău", [
        ('<a class="leg" href="https://code.visualstudio.com/" target="_blank" rel="noopener">Visual Studio Code</a>',
         "editorul: caiete și fișiere de cod, în același loc", "azi"),
        ('<a class="leg" href="https://marketplace.visualstudio.com/items?itemName=ms-python.python" target="_blank" rel="noopener">extensiile Python și Jupyter</a>',
         "rulează caietele direct în VS Code", "azi"),
        ('<a class="leg" href="https://www.python.org/downloads/" target="_blank" rel="noopener">Python 3.11+</a>',
         "limbajul; pe Windows bifezi <em>Add Python to PATH</em>", "azi"),
        ('<a class="leg" href="https://docs.python.org/3/library/venv.html" target="_blank" rel="noopener">mediul virtual (venv)</a>',
         "pachetele proiectului, separate de restul calculatorului", "azi"),
        ('<a class="leg" href="https://git-scm.com/downloads" target="_blank" rel="noopener">Git</a>',
         "istoricul proiectului și lucrul în echipă", "cursul 3"),
    ]),
    ("În mediul virtual, pachetele Python", [
        ('<a class="leg" href="https://pandas.pydata.org/docs/" target="_blank" rel="noopener">pandas</a>',
         "tabelele: citire, filtrare, îmbinare, agregare", "azi"),
        ('<a class="leg" href="https://requests.readthedocs.io/" target="_blank" rel="noopener">requests</a>',
         "cererile către API-uri", "cursul 2"),
        ('<a class="leg" href="https://matplotlib.org/stable/" target="_blank" rel="noopener">matplotlib</a>, '
         '<a class="leg" href="https://geopandas.org/" target="_blank" rel="noopener">geopandas</a>',
         "grafice și hărți", "cursul 6"),
        ('<a class="leg" href="https://networkx.org/documentation/stable/" target="_blank" rel="noopener">networkx</a>',
         "rețeaua județelor și comunitățile ei", "cursul 6"),
        ('<a class="leg" href="https://www.statsmodels.org/stable/" target="_blank" rel="noopener">statsmodels</a>',
         "modelele statistice", "cursul 7"),
    ]),
    ("În browser", [
        ('<a class="leg" href="https://github.com/" target="_blank" rel="noopener">GitHub</a>',
         "contul cu care intri pe site și depozitul echipei", "înainte de curs"),
        ('<a class="leg" href="../../">site-ul cursului</a>',
         "lecțiile, exercițiile, manualul și Exploratorul", "azi"),
        ("Teams", "temele, încărcate ca fișiere", "de la tema 1"),
    ]),
]


def unelte_html(compact=False):
    """Trei grupe de unelte, fiecare cu momentul în care intră. Fără card,
    fără cont plătit."""
    out = ['<div class="unl">']
    for grupa, rand in UNELTE:
        out.append(f'<section class="unl__g"><h4>{grupa}</h4><ul>')
        for n, d, cand in rand:
            azi = " unl__c--azi" if cand == "azi" else ""
            out.append(f'<li><span class="unl__n">{n}</span>'
                       f'<span class="unl__d">{d}</span>'
                       f'<span class="unl__c{azi}">{cand}</span></li>')
        out.append("</ul></section>")
    out.append("</div>")
    return "".join(out)


def unelte_slide():
    """Pe slide: două coloane, azi și pe parcurs. Fără cutii."""
    azi, apoi = [], []
    for _, rand in UNELTE:
        for n, d, cand in rand:
            (azi if cand == "azi" else apoi).append((n, d, cand))
    li = lambda x, cu: (f'<li><span class="un2__n">{x[0]}</span><span class="un2__d">{x[1]}</span>'
                        + (f'<span class="un2__c">{x[2]}</span>' if cu else "") + "</li>")
    return ('<div class="un2"><section><h4>Azi</h4><ul>' + "".join(li(x, False) for x in azi)
            + '</ul></section><section><h4>Pe parcurs</h4><ul>' + "".join(li(x, True) for x in apoi)
            + "</ul></section></div>")


sl("s3", "Softuri și conturi", "Uneltele semestrului",
   "<h2>Uneltele semestrului</h2>"
   "<p class=\"cheie\">Toate gratuite. Azi instalezi doar coloana din stânga.</p>"
   + unelte_slide()
   + nota("Contul GitHub", "Îl ai deja, de pe "
          '<a class="leg" href="../">pagina cursului</a>. Cu el intri pe site și, de la cursul 3, '
          "în depozitul echipei.", True),
   manual=
   "<h2>Uneltele semestrului</h2>"
   "<p>Toate uneltele sunt gratuite și niciuna nu cere card. Azi instalezi editorul, "
   "Python și mediul virtual; restul intră la lecția în care e nevoie de el.</p>"
   + unelte_html()
   + "<h3>De ce caiete și fișiere de cod</h3>"
   "<p>Caietul (<code>.ipynb</code>) e bun ca să te uiți la date pas cu pas: rulezi o "
   "celulă, vezi tabelul, mergi mai departe. Un fișier <code>.py</code> e bun pentru ce "
   "rulezi din nou, la fel, de fiecare dată: descărcarea datelor, curățarea, construirea "
   "tabelului final. Într-un proiect adevărat le ai pe amândouă, și VS Code le deschide "
   "în același loc.</p>"
   "<h3>De ce un mediu virtual</h3>"
   "<p>Fiecare proiect are pachetele lui, în versiunile lui. Mediul virtual le ține "
   "separat, ca proiectul echipei să ruleze la fel pe toate cele cinci calculatoare, și "
   "peste un an.</p>"
   + nota("Contul GitHub", "Îl faci înainte de prima oră, după pașii de pe "
          '<a class="leg" href="../">pagina cursului</a>. La prima oră intri cu el pe site și '
          "îți alegi numele din lista grupei, o singură dată. De la cursul 3, tot cu el "
          "lucrezi în depozitul echipei.")
   + nota("Ce se salvează despre tine",
          "Răspunsurile la întrebări, exercițiile făcute, prezența la oră. Detaliile sunt în "
          '<a class="leg" href="../../date-personale/">politica de confidențialitate</a>.'))


# ===========================================================================
#  4. Pașii unui proiect
# ===========================================================================

DRUM = {
    "titlu": "Apasă pe o etapă",
    "intro": "Sus curge analiza datelor, jos ingineria modelelor. Baza de date stă "
             "deoparte, fiindcă nu e o etapă: e locul la care se întorc toate.",
    "bandaSus": "Analiza datelor", "bandaJos": "Ingineria modelelor",
    "sus": [
        {"n": "Definirea problemei", "unde": "cursurile 1 și 3", "et": "pregatire",
         "d": "Tema, unitatea de analiză, întrebarea. Aici decizi ce înseamnă un rând în "
              "tabelul final: o țară, o pereche de județe, un an. Tot restul depinde de "
              "alegerea asta.",
         "noi": "Cât de legate sunt locurile Europei, și cât din asta explică migrația. "
                "Fiecare echipă alege o parte din întrebare.",
         "lit": "Teoria: de ce ar fi legate două locuri. Ce s-a aflat deja despre SCI și "
                "despre migrație, și ce a rămas neexplicat.",
         "capcana": "O unitate de analiză nehotărâtă: amesteci țări cu județe și nu mai "
                    "poți compara nimic."},
        {"n": "Colectarea datelor", "unde": "cursul 2", "et": "colectare",
         "d": "Aduci datele prin API sau din fișiere. Salvezi întotdeauna varianta brută, "
              "neatinsă, ca să poți reveni la ea când descoperi o greșeală.",
         "noi": "SCI de pe HDX, migrația de la Eurostat prin API, fiecare salvată brut, "
                "cu data descărcării.",
         "lit": "Documentația API-ului și nota metodologică a datelor: ce măsoară, cum, "
                "și ce lipsește.",
         "capcana": "Lucrezi direct pe fișierul descărcat. După prima greșeală, nu mai "
                    "ai de unde să o iei de la capăt."},
        {"n": "Curățarea datelor", "unde": "cursul 4", "et": "curatare",
         "d": "Tipuri greșite, valori lipsă, duplicate, coduri care nu se potrivesc între "
              "surse. Etapa cea mai lungă, și cea care decide dacă rezultatul înseamnă ceva.",
         "noi": "Grecia e EL la Eurostat și GR în SCI; Namibia (NA) devine valoare lipsă; "
                "migrația vine cu grupuri de țări amestecate printre țări.",
         "lit": "Documentația surselor: ce înseamnă fiecare cod și fiecare lipsă.",
         "capcana": "Ștergi rândurile cu lipsuri și îți schimbi eșantionul fără să vezi."},
        {"n": "Analiza exploratorie", "unde": "cursul 6", "et": "explorare",
         "d": "Te uiți la date înainte de a le modela. Scopul nu e să demonstrezi ceva, "
              "e să înțelegi ce ai.",
         "noi": "Coada lungă a SCI, distanța, granița, comunitățile de județe pe hartă.",
         "lit": "Ce tipare au găsit alții, ca să știi ce cauți și ce te surprinde.",
         "capcana": "Te uiți doar după ce confirmă ce credeai deja."}],
    "jos": [
        {"n": "Feature engineering", "unde": "cursul 7", "et": "model",
         "d": "Construiești variabilele care răspund la întrebare: rate, ponderi, "
              "distanțe, diferențe între capetele perechii.",
         "noi": "Distanța, migranții la mie de locuitori, granița comună.",
         "lit": "Metoda: cum au construit alții variabilele, și de ce.",
         "capcana": "Pui numărul absolut acolo unde contează rata."},
        {"n": "Modelare", "unde": "cursul 7", "et": "model",
         "d": "Testezi formal relația observată. Un model simplu, bine interpretat, bate "
              "unul complicat pe care nu îl poți explica.",
         "noi": "Patru modele pe logaritmi, fiecare cu o variabilă în plus.",
         "lit": "Metoda: modelele gravitaționale și erorile standard la date diadice.",
         "capcana": "Erori standard prea mici: același loc apare în sute de perechi, deci "
                    "observațiile nu sunt independente."},
        {"n": "Implementare", "unde": "dincolo de curs", "et": "model",
         "d": "Modelul ajunge undeva unde îl folosește altcineva: o aplicație, un raport "
              "care se actualizează singur.",
         "noi": "La noi lanțul se oprește la un depozit pe care oricine îl poate rula de "
                "la zero.",
         "lit": "Documentația uneltelor.",
         "capcana": "Codul merge doar pe laptopul tău."},
        {"n": "Optimizare", "unde": "dincolo de curs", "et": "model",
         "d": "Parametri, performanță, costuri. Zona de inginerie, nu de analiză.",
         "noi": "Nu intră în proiectul cursului.",
         "lit": "Documentația și literatura de inginerie.",
         "capcana": "Optimizezi un model înainte să știi dacă răspunde la întrebare."}],
    "final": {"n": "Raportare și vizualizare", "unde": "cursul 8", "et": "raport",
              "d": "Rezultatul devine util abia când altcineva îl poate citi, reproduce și "
                   "critica. Graficele nu sunt decor, sunt argumentul.",
              "noi": "Raportul echipei și prezentarea, din depozitul de pe GitHub.",
              "lit": "Literatura revine: unde se potrivesc rezultatele cu ce s-a mai găsit, "
                     "și unde nu.",
              "capcana": "Un grafic cu axa tăiată, care face o diferență mică să pară mare."},
    "baza": {"n": "Popularea și gestionarea bazei de date", "unde": "cursul 5", "et": "agregare",
             "d": "Nu e o etapă în lanț, e depozitul la care se întorc mai multe etape. "
                  "Colectarea scrie datele brute, curățarea versiunea curată, agregarea "
                  "tabelul final.",
             "noi": "Tabelele echipei, în trei straturi: brut, curat, final.",
             "lit": "Documentația SQL și a bazei de date.",
             "capcana": "Cinci versiuni ale aceluiași fișier, trimise pe chat."},
}

LITERATURA_FLUX = (
    "<div class=\"litf\">"
    "<p class=\"litf__t\">Literatura nu e o etapă și nici un capitol scris la final. E un fir "
    "care trece prin toată cercetarea, ca baza de date prin toate etapele.</p>"
    "<ol class=\"litf__pasi\">"
    "<li><b>Înainte de întrebare</b><span>ce se știe deja și unde e golul. Întrebarea bună "
    "vine din gol, nu din date.</span></li>"
    "<li><b>Teoria</b><span>de ce ar fi legate două locuri: sisteme migratorii, rețele "
    "sociale, distanță, granițe. Din ea ies ipotezele.</span></li>"
    "<li><b>Metoda</b><span>cum au măsurat alții, ce variabile au construit, ce modele au "
    "folosit, ce greșeli au evitat.</span></li>"
    "<li><b>Documentația</b><span>a datelor și a uneltelor, la fiecare pas de cod.</span></li>"
    "<li><b>După rezultate</b><span>le pui înapoi în literatură: ce confirmă, ce contrazice, "
    "ce e nou. Și de multe ori te trimit să mai citești.</span></li>"
    "</ol>"
    "<p class=\"litf__l\">Fiecare etapă din schemă îți spune, mai sus, ce citești acolo. Lista "
    "întreagă, pe teorie, metodă și date: <a class=\"leg\" href=\"../../lecturi/\">Literatura "
    "proiectului</a>.</p></div>"
)

def _dsw():
    """Etapele schemei, din DRUM, cu cheile desenului."""
    t = {x["n"]: x for x in DRUM["sus"] + DRUM["jos"] + [DRUM["final"], DRUM["baza"]]}
    pe = lambda cheie, **k: {**{c: t[cheie][c] for c in ("n", "unde", "d", "noi") if c in t[cheie]}, **k}
    return {
        "def": pe("Definirea problemei"), "col": pe("Colectarea datelor"),
        "cur": pe("Curățarea datelor"), "eda": pe("Analiza exploratorie"),
        "rap": pe("Raportare și vizualizare"), "db": pe("Popularea și gestionarea bazei de date"),
        "fe": pe("Feature engineering"), "mod": pe("Modelare", n="Modelare (statistică sau ML)"),
        "imp": pe("Implementare", n="Implementarea modelului"), "opt": pe("Optimizare", n="Optimizarea modelului"),
    }


DSW = {"etape": _dsw(),
       "intro": "Apasă pe o etapă. Săgețile pline sunt drumul; cele punctate sunt întoarcerile, la fel de normale."}

sl("s4", "Pașii unui proiect", "Data Science Workflow",
   "<h2>Pașii unui proiect de analiză de date</h2>"
   + ix("dsw", "Data Science Workflow", DSW),
   manual=
   "<h2>Pașii unui proiect de analiză de date</h2>"
   "<p>Schema are trei benzi. Etapele de sus, de la definirea problemei până la analiza "
   "exploratorie, sunt <strong>analiza datelor</strong>. Implementarea și optimizarea modelului "
   "sunt <strong>ML engineering</strong>. Împreună, cu baza de date care le leagă, fac "
   "<strong>știința datelor</strong>.</p>"
   + ix("dsw", "Data Science Workflow", DSW)
   + "<p>Săgețile punctate arată întoarcerile, și sunt partea cea mai "
   "importantă. Descoperi la curățare că un indicator lipsește pentru jumătate "
   "din unități și revii la colectare. Nu e un semn că ai greșit, e felul "
   "normal de a lucra.</p>"
   + nota("Baza de date nu e o etapă",
          "E locul unde etapele își lasă rezultatele. Într-o echipă de cinci, fără ea, "
          "al doilea nu poate începe până nu-i trimite primul un fișier pe chat.")
   + "<h3>Unde intră literatura</h3>" + LITERATURA_FLUX)


sl("s4l", "Pașii unui proiect", "Unde intră literatura",
   "<h2>Literatura, de-a lungul întregii cercetări</h2>"
   + LITERATURA_FLUX,
   manual="")


# ===========================================================================
#  5-8. Proiectul
# ===========================================================================

PUNCTAJ = {
    "unitate": " p",
    "sursa": "Maximum 11. La activitate, un răspuns corect dat la oră valorează întreg, unul dat acasă jumătate.",
    "cote": [
        {"t": "Proiectul de echipă", "v": 5, "ac": True},
        {"t": "Trei teme, pe Teams", "v": 3},
        {"t": "Activitate la seminar", "v": 2},
        {"t": "Din oficiu", "v": 1},
    ],
}

DIRECTII = [
    ("Coridoare de muncă", "România cu Italia sau Spania, Polonia cu Germania, Bulgaria cu Spania. Unde au plecat oamenii, și cât de legați au rămas."),
    ("Minorități și granițe vechi", "România cu Ungaria, Slovacia cu Ungaria, Austria cu Cehia. Legături care nu vin din migrația recentă."),
    ("Vecinii din est", "Moldova și Ucraina: legături puternice, dar cu date de migrație puține. Ce se vede doar în SCI?"),
    ("Diaspora pe județe", "Care județ e legat de care regiune din Italia, Spania sau Germania, și de ce tocmai de ea."),
    ("Orașe și bani", "Capitalele, centrele universitare și PIB-ul regional: cine are legături departe și cine doar aproape."),
    ("O țară, pe regiuni", "Alegeți o țară și o desfaceți pe județe: unde e legată de restul Europei, și unde nu."),
]

# --------------------------------------------------------------------------
# Indicele, pe scurt. Numerele de utilizatori sunt ilustrative, rotunde, ca
# aritmetica să se poată face cu capul; proporțiile dintre locuri sunt însă
# cele reale, și de asta are nevoie demonstrația.
# --------------------------------------------------------------------------

INDICE = {
    "sarcina": "Aceleași 1.200 de legături, trei locuri partenere de mărimi "
               "diferite. Apasă pe rând.",
    "a": {"n": "Cluj", "u": 300},
    "b": [
        {"n": "Republica Moldova", "u": 600,
         "d": "Loc mic, deci cele 1.200 de legături cântăresc mult. "
              "Indicele iese mare."},
        {"n": "Ungaria", "u": 4800,
         "d": "De opt ori mai mulți utilizatori. Aceleași legături, indice de "
              "opt ori mai mic."},
        {"n": "Italia", "u": 32000,
         "d": "Aici e capcana. Italia are cea mai mare comunitate de români în "
              "cifre absolute, dar numitorul e uriaș, deci indicele iese mic. "
              "<b>SCI nu măsoară mărimea diasporei.</b>"},
    ],
}
# fără „întâi ghicești”: formula se construiește întâi, nu se ghicește


SCI_IX = {"concluzie": "<b>Mai multe prietenii, indice mai mic.</b> SCI e o probabilitate, nu o numărătoare. "
                        "În <code>country.csv</code>: România–Moldova 173.794, România–Italia 69.327."}

sl("s5", "Proiectul", "Ce măsurăm, de fapt",
   "<h2>Social Connectedness Index</h2>"
   "<p class=\"cheie\">Cât de probabilă e o prietenie pe Facebook între doi oameni, unul din fiecare loc.</p>"
   + ix("sci", "Aceleași calcule, două perechi de locuri", SCI_IX),
   sci=True,
   manual=
   "<h2>Social Connectedness Index</h2>"
   "<p>Indicele e produs de Data for Good at Meta din rețeaua de prietenii "
   "Facebook, agregat și anonimizat. Pentru fiecare pereche de locuri spune "
   "cât de probabil e ca doi oameni de acolo, unul din fiecare, să fie "
   "prieteni, <em>relativ</em> la celelalte perechi. Numărul e scalat (maximul "
   "din fișier e exact 1.000.000.000), deci nu e o probabilitate între 0 și 1: "
   "se compară, nu se citește singur.</p>"
   "<p>Definiția, în cuvinte: numărul de legături observate între cele două "
   "locuri, împărțit la produsul numerelor de <em>utilizatori Facebook</em> "
   "din fiecare. Numitorul nu e populația, sunt utilizatorii, și asta are "
   "două consecințe pe care le vom relua tot semestrul.</p>"
   + ix("sci", "Aceleași calcule, două perechi de locuri", SCI_IX)
   + "<h3>Ce nu e</h3>"
   "<ul>"
   "<li><strong>Nu e numărul de prietenii.</strong> Nu se adună și nu se "
   "mediază naiv între perechi.</li>"
   "<li><strong>Nu e mărimea diasporei.</strong> Un clasament după SCI arată "
   "altfel decât unul după câți români trăiesc acolo. Confuzia dintre ele e "
   "prima greșeală pe care o face oricine deschide datele.</li>"
   "<li><strong>Nu acoperă toată populația.</strong> Baza sunt utilizatorii "
   "Facebook activi în cele 30 de zile dinainte de 25 ianuarie 2026, cu peste 20 de "
   "prieteni; locurile cu sub 500 de utilizatori lipsesc (Johnston și colegii, 2026). "
   "Acoperirea diferă pe vârste, medii și țări.</li>"
   "<li><strong>Nu se compară între fișiere.</strong> Fiecare fișier e scalat separat, de la 1 "
   "la 1.000.000.000: valorile din fișierul pe țări și cele din fișierul pe județe nu se pun "
   "una lângă alta.</li>"
   "</ul>"
   + surse("Surse oficiale despre SCI", [
       ("Meta, Data for Good: SCI", "https://ai.meta.com/ai-for-good/datasets/social-connectedness-index/",
        "ce e indicele, pe scurt, de la cei care îl produc"),
       ("HDX: fișierele SCI", "https://data.humdata.org/dataset/social-connectedness-index",
        "de aici descarci datele; nota metodologică e printre resurse"),
       ("Bailey și colegii (2018), JEP", "https://www.aeaweb.org/articles?id=10.1257/jep.32.3.259",
        "articolul care a introdus indicele: definiția, ce îl explică, primele rezultate"),
   ])
   + nota("Instantaneul pe care lucrăm",
          "25 ianuarie 2026, 178 de țări, pe clasificările NUTS 2024, GADM 4.1 "
          "și geoBoundaries 6.0.0. E un instantaneu: nu are dimensiune "
          "temporală, deci nimic longitudinal. Harta noastră, pe județe, "
          "regiuni și țări, e mai jos și în "
          '<a class="leg" href="../../explorator/">Exploratorul legăturilor sociale</a>.')
   + lecturi(["johnston2026", "bailey2018"]))


HARTA_JUDETE = {
    "niveluri": ["judete"], "nivel": "judete", "masura": "sci", "ales": "RO113",
    "povesti": [
        {"t": "Cluj", "nivel": "judete", "masura": "sci", "ales": "RO113",
         "text": "În țară, Clujul e legat întâi de Sălaj și Bistrița-Năsăud. "
                 "În afara ei, de Lleida și Huesca, în nord-estul Spaniei."},
        {"t": "Harghita", "nivel": "judete", "masura": "sci", "ales": "RO124",
         "text": "Cu Covasna, cea mai puternică legătură dintre două județe "
                 "românești. Afară: Ungaria și, neașteptat, cantonul elvețian Thurgau."},
        {"t": "Bihor", "nivel": "judete", "masura": "sci", "ales": "RO111",
         "text": "Peste graniță, Hajdú-Bihar, cealaltă jumătate a vechiului "
                 "comitat. Apoi Straubing, în Bavaria."},
        {"t": "Suceava", "nivel": "judete", "masura": "sci", "ales": "RO215",
         "text": "Primul partener din afară e Turnhout, în Belgia. Un singur "
                 "județ, o singură destinație, foarte clar."},
        {"t": "Dolj", "nivel": "judete", "masura": "sci", "ales": "RO411",
         "text": "Districte agricole din nordul Germaniei, apoi Huelva, regiunea "
                 "căpșunilor din sudul Spaniei. Munca sezonieră lasă urme."},
    ],
}
HARTA_JUDETE["intai"] = {"q": "Clujul e legat întâi de județele vecine. Dar în afara României, unde crezi că sunt cei mai legați parteneri ai lui?", "variante": ["În Ungaria, peste graniță", "În nord-estul Spaniei", "În nordul Italiei"], "corect": 1, "dupa": "Lleida și Huesca, în Catalonia și Aragon: de 31 și de 20 de ori peste mediana partenerilor Clujului. Liniile portocalii duc spre cei mai legați parteneri din alte țări. Deschide harta mare (⤢) și caută alt județ."}

HARTA_TARI = {
    "niveluri": ["tari"], "nivel": "tari", "masura": "migr", "ales": "RO",
    "masuri": ["migr", "sci"],
    "povesti": [
        {"t": "Unde trăiesc românii", "nivel": "tari", "masura": "migr", "ales": "RO",
         "text": "Cetățeni români după țara în care locuiesc (Eurostat, 2024). "
                 "Italia e prima, cu 1,07 milioane, apoi Germania și Spania."},
        {"t": "Cât de legați suntem", "nivel": "tari", "masura": "sci", "ales": "RO",
         "text": "Aceeași hartă, dar după SCI. Moldova, Austria, Germania și "
                 "Ungaria trec în față. Italia coboară."},
        {"t": "Polonia", "nivel": "tari", "masura": "migr", "ales": "PL",
         "text": "Cei mai mulți polonezi trăiesc în Germania. Comută pe "
                 "Legături: pe primul loc trece Islanda, o țară mică în care "
                 "polonezii sunt cea mai mare comunitate străină."},
    ],
}

sl("s5h", "Proiectul", "Harta, pe județe",
   "<h2>Cu cine e legat județul tău?</h2>"
   + ix("harta", "1.343 de regiuni NUTS 3 din toată Europa", HARTA_JUDETE),
   sci=True,
   manual=
   "<h2>Harta, pe județe</h2>"
   "<p>Asta e harta la care ajungem. Fiecare din cele 1.343 de regiuni NUTS3 "
   "ale Europei, pentru România chiar județele, se colorează după cât de "
   "legată e de județul ales. Numărul din listă e un raport: de câte ori e "
   "mai mare SCI-ul cu locul acela decât SCI-ul median al județului ales.</p>"
   + ix("harta", "1.343 de regiuni NUTS 3 din toată Europa", HARTA_JUDETE)
   + "<p>Două lucruri sar în ochi imediat. Primul: aproape tot ce e foarte "
   "legat e aproape, în aceeași țară. Distanța și granița sunt regula. Al "
   "doilea: fiecare județ are, totuși, câteva locuri îndepărtate cu care e "
   "neobișnuit de legat, și ele nu sunt aceleași pentru județe vecine. "
   "Suceava are Belgia, Clujul are nord-estul Spaniei, Doljul are Germania "
   "de nord și Huelva.</p>"
   "<p>Hărțile astea seamănă cu hărțile migrației, dar nu sunt hărți ale migrației: "
   "SCI-ul nu știe cine unde locuiește. De aici întrebarea cursului: cât din legături "
   "se explică prin oamenii care au plecat? Migrația intră pe slide-ul următor.</p>"
   + nota("De unde vine harta",
          "Din fișierul <code>nuts3_2024.csv</code> pe care îl veți descărca la "
          "cursul 2, și din contururile NUTS 2024 de la Eurostat. Pe toată "
          "Europa, cu toate nivelurile, e în "
          '<a class="leg" href="../../explorator/">Exploratorul legăturilor sociale</a>.'))


sl("s5m", "Proiectul", "Oameni și legături",
   "<h2>Unde sunt românii, și unde sunt prietenii lor?</h2>"
   + ix("harta", "Migrația (Eurostat) și SCI, pe aceeași hartă", HARTA_TARI),
   sci=True,
   manual=
   "<h2>Oameni și legături</h2>"
   "<p>A doua sursă a cursului e migrația: câți cetățeni ai fiecărei țări "
   "trăiesc în fiecare altă țară. O luăm tot prin API, de la Eurostat "
   "(<code>migr_pop1ctz</code>), la cursul 2. Pe hartă, prima poveste arată "
   "unde trăiesc românii, a doua arată cât de legată e România de fiecare țară.</p>"
   + ix("harta", "Migrația (Eurostat) și SCI, pe aceeași hartă", HARTA_TARI)
   + nota("Ce date de migrație avem",
          "Stocul de cetățeni străini, pe 1 ianuarie 2024, pentru țările care raportează pe "
          "țări de cetățenie. Printre cele care nu o fac: Polonia, Danemarca, Grecia, Croația, "
          "Cipru, Malta, Elveția, Regatul Unit și cele mai multe țări din afara UE (Moldova, "
          "Ucraina, Serbia). Acolo harta rămâne gri: e o limită a datelor, nu o eroare."),
   dupa=verif("c1-v11", 2,
              "Pe ce loc e Italia printre partenerii României, după SCI?",
              ["primul", "al treilea", "al șaselea", "al doisprezecelea"],
              "Al șaselea, după Moldova, Austria, Germania, Ungaria și Irlanda. "
              "La migrație e prima. Diferența dintre cele două clasamente e "
              "chiar întrebarea proiectului."))


# --------------------------------------------------------------------------
# Legătura dintre migrație și SCI, pe datele noastre. Populația țărilor e
# suma județelor (NUTS 3) din Eurostat, 2024; românii din fiecare țară sunt
# din migr_pop1ctz, 2024; SCI din country.csv.
# --------------------------------------------------------------------------
POP_TARI = {"AT": 9158750, "BE": 11817096, "BG": 6445481, "CZ": 10900555, "DE": 83456045,
            "DK": 5961249, "EE": 1374687, "ES": 48619695, "FI": 5603851, "FR": 68669303,
            "HU": 9584627, "IE": 5351681, "IS": 383567, "IT": 58971230, "LT": 2885891,
            "LU": 672050, "LV": 1878575, "NL": 17942942, "NO": 5550203, "PT": 10639726,
            "SE": 10551707, "SI": 2123949, "SK": 5424687, "TR": 85372377}
_SCI_RO = {x["cod"]: x for x in _json.loads((_pl.Path(__file__).resolve().parent.parent / "date" / "sci-ro-tari.json").read_text(encoding="utf-8"))["tari"]}


def _panta():
    toate = [{"cod": c, "nume": _SCI_RO[c]["nume"], "nr": v, "mie": round(v / POP_TARI[c] * 1000, 1),
              "sci": _SCI_RO[c]["sci"]} for c, v in ROMANI.items() if c in POP_TARI and c in _SCI_RO]
    sus = sorted(toate, key=lambda r: -r["sci"])[:10]
    if not any(r["cod"] == "FR" for r in sus):
        sus.append(next(r for r in toate if r["cod"] == "FR"))
    note = {"IT": "Cei mai mulți români, dar Italia e mare: la SCI coboară.",
            "AT": "A cincea după număr, a doua la mie, prima după SCI.",
            "HU": "Puțini români, dar SCI mare: minoritatea și granița, nu migrația recentă.",
            "FR": "A patra după număr, dar puțini la mie: SCI mic."}
    for r in sus:
        if r["cod"] in note:
            r["nota"] = note[r["cod"]]
    return sus


PANTA = {
    "coloane": [{"k": "nr", "t": "câți români trăiesc acolo", "scurt": "români"},
                {"k": "mie", "t": "români la 1.000 de locuitori", "scurt": "la mie", "fmt": "mie"},
                {"k": "sci", "t": "SCI cu România", "scurt": "SCI"}],
    "randuri": _panta(), "evidentiate": ["IT", "AT", "HU", "FR"],
    "intro": "Apasă pe o țară. Verde: urcă de la număr la SCI. Roșu: coboară.",
}

sl("s5r", "Proiectul", "Migrația și SCI",
   "<h2>Legăturile urmează proporția, nu numărul</h2>"
   + ix("panta", "Aceleași țări, ordonate în trei feluri", PANTA)
   + "<p class=\"cheie\">Pe logaritmi, în cele 23 de țări care raportează: numărul de români se "
   "potrivește cu SCI-ul la 0,78; românii la mie, la 0,87. Ce rămâne neexplicat, ca Ungaria, "
   "e o întrebare de proiect.</p>",
   sci=True,
   manual=
   "<h2>Legăturile urmează proporția, nu numărul</h2>"
   "<p>Aceleași țări, ordonate în trei feluri: după câți români trăiesc acolo, după câți "
   "români sunt la 1.000 de locuitori ai țării, și după SCI. Dacă SCI-ul ar urma numărul de "
   "români, liniile ar fi orizontale. Nu sunt.</p>"
   + ix("panta", "Aceleași țări, ordonate în trei feluri", PANTA)
   + "<p>Corelația pe logaritmi, în cele 23 de țări care raportează cetățeniile: 0,78 cu "
   "numărul de români, 0,87 cu românii la mie. E exact ce găsim în modelul de la cursul 7, "
   "unde rata la mie explică mult mai mult decât numărul. Explicația ține de numitorul "
   "indicelui: SCI împarte la utilizatorii din ambele locuri, deci o comunitate mare într-o "
   "țară mare cântărește puțin.</p>"
   + nota("Calculul", "Românii din fiecare țară: Eurostat, <code>migr_pop1ctz</code>, 2024. "
          "Populația țărilor: suma regiunilor NUTS 3, Eurostat, 2024. SCI: <code>country.csv</code>."))


ECHIPE = (
    '<ol class="ech">'
    "<li><span>cursurile 1–2</span><b>Faceți echipa</b><p>Cinci oameni. Cine nu are echipă, e repartizat.</p></li>"
    "<li><span>cursul 3</span><b>Alegeți direcția</b><p>Întrebarea voastră, cadrul teoretic și depozitul echipei pe GitHub.</p></li>"
    "<li><span>cursurile 4–7</span><b>Construiți, bucată cu bucată</b><p>Datele curate, tabelul final, explorarea, modelul: toate în depozit.</p></li>"
    "<li><span>cursul 8</span><b>Prezentați</b><p>Raportul și drumul până la el.</p></li>"
    "</ol>"
    '<div class="ech__reguli">'
    "<p><b>Un depozit pe echipă.</b> Tot ce faceți stă pe GitHub, cu istoricul lui.</p>"
    "<p><b>Fiecare are partea lui.</b> Din istoric se vede cine ce a făcut.</p>"
    "<p><b>Nota e pe om.</b> Proiectul e al echipei, nota la proiect e a fiecăruia.</p>"
    "</div>")

sl("s5b", "Proiectul", "Echipele",
   "<h2>Echipe de cinci, un depozit comun</h2>"
   "<p class=\"cheie\">Aceleași date pentru toți, SCI și migrație. Întrebarea e a voastră.</p>"
   + ECHIPE,
   manual=
   "<h2>Echipe de cinci, un depozit comun</h2>"
   "<p>Proiectul se face în echipe de cinci, pe aceleași date pentru toată grupa: SCI și "
   "migrația. Ce diferă de la o echipă la alta e întrebarea. Până la cursul 2 formați echipa; "
   "direcția o alegeți la cursul 3, după ce ați văzut datele și literatura.</p>"
   + ECHIPE
   + tabel(["Cursul", "Ce adaugi în depozit"], [
       ["~1–2", "Echipa, mediul de lucru, primele date"],
       ["~3", "Depozitul de echipă, direcția, întrebarea, cadrul teoretic"],
       ["~4", "Dataseturile curățate și dicționarul de date"],
       ["~5", "Tabelul final, la unitatea de analiză aleasă"],
       ["~6", "Analiza exploratorie"],
       ["~7", "Variabilele derivate și modelul"],
       ["~8", "Raportul final și prezentarea"],
   ]))


DIRECTII2 = [
    ("Migrația și legăturile", [
        ("Număr sau proporție?", "SCI-ul urmărește câți români trăiesc într-o țară, sau ce parte din populația ei sunt?", "SCI · migrație · populație"),
        ("Coridoare comparate", "România–Italia, Polonia–Germania, Bulgaria–Spania: aceeași regulă peste tot?", "SCI · migrație"),
        ("Diaspora pe județe", "De ce e Clujul legat de Lleida, Suceava de Belgia, Doljul de Huelva?", "SCI județ–regiune"),
    ]),
    ("Istorie și granițe", [
        ("Granițele vechi", "Se mai vede granița Imperiului Habsburgic în legăturile dintre județe?", "SCI județe · granițe istorice"),
        ("Minoritățile", "Județele cu mulți vorbitori de maghiară sunt mai legate de Ungaria?", "SCI județ–țară · recensământ"),
        ("Vecinii din est", "Moldova și Ucraina: legături puternice, fără date de migrație. Ce spune doar SCI?", "SCI"),
    ]),
    ("Distanță și geografie", [
        ("Cât contează distanța", "Cât de repede scad legăturile cu distanța, și e la fel în toate țările?", "SCI · centroizi NUTS"),
        ("Granița de stat", "La aceeași distanță, peste graniță e mai puțin legat decât în aceeași țară?", "SCI · contururi NUTS"),
        ("Munții", "Despart Carpații legăturile dintre județe?", "SCI județe · relief"),
    ]),
    ("Orașe, bani, rețele", [
        ("Orașele mari", "Capitalele și centrele universitare au legături mai departe decât restul?", "SCI · populație"),
        ("Bogați cu bogați", "Regiunile bogate sunt legate mai ales de alte regiuni bogate?", "SCI · PIB regional"),
        ("Comunitățile", "În câte „regiuni de prietenie” se împarte Europa, și urmează ele granițele?", "SCI · rețele"),
    ]),
]


def directii_html():
    out = ['<div class="dir2">']
    for tema, qs in DIRECTII2:
        out.append(f'<section><h4>{tema}</h4>')
        for t, q, date in qs:
            out.append(f'<div class="dir2__q"><b>{t}</b><p>{q}</p><span>{date}</span></div>')
        out.append("</section>")
    out.append("</div>")
    return "".join(out)


sl("s5d", "Proiectul", "Direcții posibile",
   "<h2>Douăsprezece întrebări de la care puteți porni</h2>"
   + directii_html()
   + "<p class=\"dir2__jos\">Sunt sugestii, nu un meniu închis. Direcția o alegeți la cursul 3, după ce vedeți datele și literatura.</p>",
   manual=
   "<h2>Direcții posibile</h2>"
   "<p>Toate pornesc din aceleași fișiere, SCI și migrație, la care se adaugă, după întrebare, "
   "câteva surse de context. Le-am grupat după felul întrebării. Fiecare vine cu datele de care "
   "are nevoie. Dacă aveți altă întrebare, cu atât mai bine.</p>"
   + directii_html()
   + "<p>Mai multe idei, și articolele din care vin, sunt pe pagina "
   '<a class="leg" href="../../lecturi/">Literatura proiectului</a>.</p>')


NOTA = (
    '<div class="nt">'
    '<div class="nt__c nt__c--p"><b>5</b><span>Proiectul</span><p>Depozitul echipei și raportul. Se notează drumul care se vede în depozit. Nota e pe om.</p></div>'
    '<div class="nt__c"><b>3</b><span>Temele</span><p>Trei teme, încărcate pe Teams, notate de mine.</p></div>'
    '<div class="nt__c"><b>2</b><span>Activitatea</span><p>Întrebările din lecții. Corect la oră: întreg. Corect acasă: jumătate.</p></div>'
    '<div class="nt__c"><b>1</b><span>Din oficiu</span><p>Îl ai de la început.</p></div>'
    "</div>"
    '<p class="nt__tot"><b>11 puncte</b> în total. Fiecare întrebare are două șanse, una la oră și una acasă; '
    "contează prima. Regulile le vezi oricând în contul tău.</p>")

sl("s5n", "Proiectul", "Cum se dă nota",
   "<h2>Cum se dă nota</h2>"
   + NOTA
   + "<p class=\"cheie\">Nota vine din drum, nu din rezultat. Un rezultat negativ bine argumentat ia "
   "aceeași notă ca unul spectaculos.</p>",
   manual=
   "<h2>Cum se dă nota</h2>"
   + NOTA
   + tabel(["Componentă", "Puncte", "Din ce iese"], [
       ["Proiect", "~5", "Depozitul de echipă și raportul final. Se notează drumul care se vede în "
                         "depozit, nu spectaculozitatea rezultatului. Nota e pe om."],
       ["Teme", "~3", "Trei teme de seminar, încărcate pe Teams. N-au legătură cu lecțiile de pe "
                      "sit; le citesc și le notez eu."],
       ["Activitate", "~2", "Întrebările din lecții. Fiecare din cele 7 seminare valorează la fel. "
                            "La fiecare întrebare ai două șanse, una la oră și una acasă; contează "
                            "primul răspuns din fiecare. Corect la oră = întreg, corect acasă = jumătate."],
       ["Din oficiu", "~1", "Îl ai de la început."],
   ]))


# ===========================================================================
#  Datele proiectului: ce folosim, ce formă au, și un exemplu pe hartă
# ===========================================================================

SURSE_APOI = [
    ["Migrație pe regiuni", "străini pe provincii, pentru un coridor", "ISTAT, INE"],
    ["Comerț bilateral", "țară cu țară, pe produs", "Eurostat Comext, UN Comtrade"],
    ["Rețeaua rutieră", "distanță și timp de drum, nu doar în linie dreaptă", "OpenStreetMap"],
    ["Relief", "munții ca barieră, ca măsură continuă", "Copernicus, GISCO"],
    ["Granițe istorice", "cui au aparținut locurile, pe ferestre de timp", "CShapes și surse istorice"],
    ["Acces la internet", "ca să știm pe cine nu vedem în date", "ANCOM"],
]

DATE_PROIECT = [
    ("Diadice", "un rând = o pereche de locuri", "dia", [
        ("SCI, țară cu țară", "country.csv", "178 × 178 = 31.684 de rânduri", "Meta, HDX"),
        ("SCI, regiune cu regiune", "nuts3_2024.csv", "1,8 milioane de rânduri", "Meta, HDX"),
        ("SCI, județ cu țară", "nuts3_2024_to_country.csv", "245.770 de rânduri", "Meta, HDX"),
        ("Migrația", "migr_pop1ctz", "cetățenie × țară de rezidență", "Eurostat, API"),
    ]),
    ("Monadice", "un rând = un loc", "mon", [
        ("Populație și densitate", "demo_r_pjangrp3", "pe județ, anual", "Eurostat, API"),
        ("PIB pe locuitor", "nama_10r_3gdp", "pe județ", "Eurostat, API"),
        ("Indicatori de țară", "SP.POP.TOTL și altele", "pe țară", "Banca Mondială, API"),
        ("Recensământul 2021", "etnie, limbă, religie", "pe județ", "INS"),
    ]),
    ("Geografice", "un rând = o formă pe hartă", "geo", [
        ("Contururile NUTS 2024", "NUTS_RG_20M_2024_3035", "poligoane, în metri", "Eurostat GISCO"),
        ("Centroizii", "calculați din contururi", "puncte, pentru distanțe", "noi"),
    ]),
]


def date_proiect_html():
    out = ['<div class="dp">']
    for t, sub, k, rand in DATE_PROIECT:
        out.append(f'<section class="dp__g dp__g--{k}"><h4><i></i>{t}<span>{sub}</span></h4><table>')
        for n, f, cat, sursa in rand:
            out.append(f'<tr><td>{n}</td><td><code>{f}</code></td><td>{cat}</td><td>{sursa}</td></tr>')
        out.append("</table></section>")
    out.append("</div>")
    return "".join(out)


sl("s6", "Datele proiectului", "Ce date folosim",
   "<h2>Datele proiectului, după forma lor</h2>"
   + date_proiect_html(),
   manual=
   "<h2>Datele proiectului, după forma lor</h2>"
   "<p>Un proiect de date nu începe cu toate sursele adunate, ci cu un nucleu peste care se "
   "adaugă module, după întrebare. Nucleul nostru are trei feluri de date, și forma lor "
   "decide cum le lipim între ele: datele <strong>diadice</strong> descriu perechi de locuri, "
   "cele <strong>monadice</strong> descriu un singur loc, cele <strong>geografice</strong> "
   "descriu forma locului pe hartă.</p>"
   + date_proiect_html()
   + nota("Fișierul care nu se poate reconstrui",
          "<code>nuts3_2024_to_country.csv</code> leagă fiecare județ cu fiecare țară. "
          "Combinația asta nu există în celelalte fișiere și nu iese din ele prin niciun calcul.")
   + "<h3>Ce se adaugă mai târziu, după întrebare</h3>"
   + tabel(["Ce", "La ce ajută", "De unde"], SURSE_APOI)
   + nota("Un lucru de reținut despre reproducibilitate",
          "API-urile Eurostat servesc versiunea curentă, nu un istoric. Deci se salvează "
          "răspunsul brut și data descărcării, nu doar codul care face cererea."))


def _diadic():
    d = _json.loads((_pl.Path(__file__).resolve().parent.parent / "date" / "sci-ro-nuts3.json").read_text(encoding="utf-8"))
    ix_ = {n: i for i, n in enumerate(d["judete"])}
    pop = {"Cluj": 693507, "Sălaj": 210656, "Bihor": 555957}
    nume = ["Cluj", "Sălaj", "Bihor"]
    return {"judete": [{"nume": n, "sigla": d["sigle"][ix_[n]], "pop": pop[n]} for n in nume],
            "matrice": [[d["matrice"][ix_[a]][ix_[b]] for b in nume] for a in nume]}


DIADIC = _diadic()

sl("s8", "Datele proiectului", "Date diadice",
   "<h2>Date diadice: un rând e o pereche</h2>"
   + ix("diadic", "Trei județe, nouă perechi", DIADIC)
   + "<p class=\"dd__jos\">La 42 de județe: 42 × 42 = 1.764 de rânduri. La toate cele 1.343 de regiuni "
   "din Europa: 1,8 milioane. De aici nevoia de cod și de bază de date.</p>",
   sci=True,
   manual=
   "<h2>Date diadice</h2>"
   "<p>Particularitatea datelor noastre schimbă fiecare etapă de mai târziu, "
   "deci merită înțeleasă de la început: un rând din fișierele SCI nu descrie "
   "un loc, ci o relație între două locuri.</p>"
   + ix("diadic", "Trei județe, nouă perechi", DIADIC)
   + "<h3>Trei consecințe care revin tot semestrul</h3>"
   "<ol><li><strong>Tabelul crește cu pătratul.</strong> Nu se mai poate citi "
   "cu ochiul, deci trebuie interogat. De aici nevoia de bază de date.</li>"
   "<li><strong>Atributele se lipesc de două ori.</strong> Populația „de unde” "
   "și populația „spre unde” sunt două coloane diferite, din același tabel "
   "sursă.</li>"
   "<li><strong>Observațiile nu sunt independente.</strong> În tabelul județelor, "
   "Clujul apare în 83 din cele 1.764 de rânduri. Un model care presupune independență dă "
   "erori standard prea mici.</li></ol>"
   + nota("SCI și migrația, două feluri de perechi",
          "SCI-ul e simetric: România cu Italia e același număr ca Italia cu "
          "România. Migrația are direcție: românii din Italia nu sunt italienii "
          "din România.")
   + ix("matrice", "1.764 de rânduri", {"cauta": {
       "din": "CJ", "tinta": "SM", "vecini": ["BH", "SJ", "MM", "BN", "MS", "AB"],
       "t": "județul cel mai legat de Cluj dintre cele care <b>nu</b> se învecinează cu el.",
       "dupa": "Satu Mare: 541.340, mai mult decât Bihorul, care e vecin. Deci vecinătatea nu explică tot."}}))


def _harta_ro():
    """Județele României, din conturul NUTS 3 folosit pe tot situl, cu raportul
    SCI(Cluj) / SCI(București) pentru fiecare."""
    import re as _re
    rad = _pl.Path(__file__).resolve().parent.parent / "date"
    geo = [x for x in _json.loads((rad / "harta" / "judete.json").read_text(encoding="utf-8"))["judete"] if x["tara"] == "RO"]
    d = _json.loads((rad / "sci-ro-nuts3.json").read_text(encoding="utf-8"))
    pe_cod = {c: i for i, c in enumerate(d["coduri"])}
    ia, ib = d["judete"].index("Cluj"), d["judete"].index("București")
    xs, ys, out = [], [], []
    for g in geo:
        nums = list(map(float, _re.findall(r"-?\d+(?:\.\d+)?", g["d"])))
        px, py = nums[0::2], nums[1::2]
        xs += px; ys += py
        i = pe_cod.get(g["cod"])
        r = None if i is None or i in (ia, ib) else round(d["matrice"][ia][i] / d["matrice"][ib][i], 3)
        out.append({"cod": g["cod"], "nume": d["judete"][i] if i is not None else g["nume"], "d": g["d"], "r": r,
                    "cx": round(sum(px) / len(px)), "cy": round(sum(py) / len(py))})
    m = 6
    vb = f"{min(xs) - m} {min(ys) - m} {max(xs) - min(xs) + 2 * m} {max(ys) - min(ys) + 2 * m}"
    return {"judete": out, "vb": vb, "a": "Cluj", "b": "București",
            "intro": "Treci cu mouse-ul peste un județ. Granița nu urmează Carpații: Brașovul trage "
                     "spre București, Suceava și Botoșani spre Cluj."}


HARTA_RO = _harta_ro()

sl("s7", "Datele proiectului", "Cluj sau București?",
   "<h2>Cluj sau București?</h2>"
   "<p>Pentru fiecare județ, două rânduri din tabelul de perechi: cu Clujul și cu Bucureștiul. Care e mai mare?</p>"
   + ix("ro", "Același tabel diadic, pe hartă", HARTA_RO),
   sci=True,
   manual=
   "<h2>Cluj sau București?</h2>"
   "<p>Social Capital Lab a publicat o hartă a Europei care răspunde la o "
   "singură întrebare: fiecare regiune are mai mulți prieteni la Madrid sau la "
   "Barcelona? Mai jos e aceeași întrebare pentru România, calculată din exact "
   "fișierele pe care le veți descărca la cursul 2. Pentru fiecare județ se compară "
   "două rânduri din tabelul diadic: perechea cu Clujul și perechea cu Bucureștiul.</p>"
   + ix("ro", "Același tabel diadic, pe hartă", HARTA_RO)
   + "<p>Interpretarea o lăsăm pentru cursul 6. Dacă vă vine acum o explicație "
   "în minte, scrieți-o undeva și verificați-o peste zece săptămâni.</p>")


# ===========================================================================
#  9-14. Tipuri de date
# ===========================================================================

RAMURI_PY = [
    {"nume": "Nimic", "tipuri": [
        {"n": "None", "cls": "NoneType", "imut": True,
         "d": "Absența unei valori. Nu e zero și nu e text gol: înseamnă „nu știm”.",
         "ex": "valoare = None\nprint(valoare is None)   # True",
         "la": "O măsurătoare care lipsește. În pandas devine NaN."}]},
    {"nume": "Numere", "sub": [
        {"nume": "întregi", "tipuri": [
            {"n": "int", "cls": "class int", "imut": True,
             "d": "Numere întregi, fără limită de mărime în Python.",
             "ex": "an = 2024\npopulatie = 19051804",
             "la": "Ani, populație, numărători."},
            {"n": "bool", "cls": "class bool", "imut": True,
             "d": "Adevărat sau fals. Tehnic e un fel de int: True valorează 1.",
             "ex": "are_date = True\nprint(True + True)       # 2",
             "la": "Rezultatul oricărei condiții; filtrele din pandas."}]},
        {"nume": "reale", "tipuri": [
            {"n": "float", "cls": "class float", "imut": True,
             "d": "Numere cu zecimale. 0.1 + 0.2 nu dă exact 0.3, din cauza reprezentării binare.",
             "ex": "rata = 3.7\nprint(0.1 + 0.2 == 0.3)  # False",
             "la": "Aproape toți indicatorii calculați."},
            {"n": "complex", "cls": "class complex", "imut": True,
             "d": "Numere complexe. Există, dar nu le folosim la curs.",
             "ex": "z = 2 + 3j"}]}]},
    {"nume": "Secvențe", "sub": [
        {"nume": "nemodificabile", "tipuri": [
            {"n": "str", "cls": "class str", "imut": True,
             "d": "Text. Orice vine dintr-un fișier necurățat e text până îl converteșt tu.",
             "ex": "cod = \"RO113\"\nan = \"2024\"              # text!\nprint(int(an) + 1)       # 2025",
             "la": "Nume, coduri NUTS, orice coloană necurățată."},
            {"n": "tuple", "cls": "class tuple", "imut": True,
             "d": "Secvență ordonată care nu se mai poate modifica după creare.",
             "ex": "coord = (46.77, 23.59)\nperechea = (\"RO113\", \"RO116\")",
             "la": "Coordonate, și cheia unei perechi de județe."},
            {"n": "bytes", "cls": "class bytes", "imut": True,
             "d": "Octeți bruți. Apare când citești un fișier binar sau un răspuns HTTP neinterpretat.",
             "ex": "r = requests.get(url)\nprint(type(r.content))   # bytes"}]},
        {"nume": "modificabile", "tipuri": [
            {"n": "list", "cls": "class list",
             "d": "Secvență ordonată, modificabilă. Cel mai folosit tip din Python.",
             "ex": "judete = [\"Cluj\", \"Sălaj\"]\njudete.append(\"Alba\")",
             "la": "Un tablou dintr-un JSON devine listă."},
            {"n": "bytearray", "cls": "class bytearray",
             "d": "Ca bytes, dar modificabil. Rar în analiza de date."}]}]},
    {"nume": "Mulțimi", "tipuri": [
        {"n": "set", "cls": "class set",
         "d": "Colecție neordonată, fără duplicate. Verificarea apartenenței e foarte rapidă.",
         "ex": "coduri = {\"RO113\", \"RO116\"}\nprint(\"RO113\" in coduri)  # True",
         "la": "Codurile care apar într-o sursă dar nu în alta, la cursul 4."},
        {"n": "frozenset", "cls": "class frozenset", "imut": True,
         "d": "Mulțime nemodificabilă. Poate fi cheie de dicționar."}]},
    {"nume": "Dicționare", "tipuri": [
        {"n": "dict", "cls": "class dict",
         "d": "Perechi cheie și valoare. Structura oricărui obiect JSON convertit în Python.",
         "ex": "rand = {\"tara\": \"RO\",\n        \"an\": 2024,\n        \"valoare\": 19051804}\nprint(rand[\"valoare\"])",
         "la": "Fiecare răspuns de API ajunge aici."}]},
    {"nume": "Altele", "tipuri": [
        {"n": "funcții", "cls": "callable",
         "d": "Funcțiile sunt și ele valori: le poți pune într-o listă sau da ca argument.",
         "ex": "def curata(x):\n    return x.strip()\n\nnume = [curata(n) for n in brute]"},
        {"n": "module", "cls": "class module",
         "d": "Un fișier de Python importat devine un obiect cu propriul tip.",
         "ex": "import pandas as pd\nprint(type(pd))          # module"}]},
]

TIPURI_LISTA = [
    ("Valori simple", "var(--accent)", [
        ("int", "număr întreg", "Numere fără zecimale. Cu ele se numără și se socotește.", "178", "anul, populația, numărul de țări"),
        ("float", "număr real", "Numere cu zecimale, scrise cu punct, nu cu virgulă.", "8.5", "densitatea, PIB-ul pe locuitor, ratele"),
        ("str", "șir de caractere", "Text: orice stă între ghilimele, chiar dacă arată ca un număr.", "\"RO\"", "codurile de țară și de județ, numele"),
        ("bool", "valoare logică", "True sau False, cu majusculă. Rezultatul oricărei comparații.", "True", "filtrele: user_country == \"RO\""),
        ("NoneType", "lipsa valorii", "None înseamnă „nu știm”. Nu e zero și nu e text gol.", "None", "o valoare lipsă; în pandas devine NaN"),
    ]),
    ("Colecții", "var(--ambra)", [
        ("list", "listă", "Valori în ordine, cerute după poziție, de la 0. Se poate modifica.", "[\"RO\", \"IT\"]", "un tablou dintr-un JSON"),
        ("tuple", "tuplu", "Ca lista, dar nu se mai poate modifica după ce l-ai creat.", "(46.77, 23.59)", "coordonatele, o pereche de județe"),
        ("dict", "dicționar", "Perechi cheie: valoare, cerute după cheie.", "{\"tara\": \"RO\"}", "un obiect dintr-un JSON"),
        ("set", "mulțime", "Valori fără duplicate și fără ordine.", "{\"RO\", \"HU\"}", "codurile dintr-o sursă care lipsesc din alta"),
    ]),
]


def tipuri_lista():
    """Două tabele simple: valorile simple și colecțiile. Fără carduri."""
    SCURT = {"int": "ani, populații, numărători", "float": "densitate, PIB, rate",
             "str": "coduri și nume", "bool": "rezultatul unei comparații",
             "NoneType": "o valoare care lipsește", "list": "în ordine, ceri după poziție",
             "tuple": "ca lista, dar nu se mai schimbă", "dict": "perechi cheie: valoare",
             "set": "fără duplicate, fără ordine"}
    out = ['<div class="tp2">']
    for grupa, _, rand in TIPURI_LISTA:
        out.append(f'<section><h4>{grupa}</h4><table>')
        for n, ro, d, ex, la in rand:
            out.append(f'<tr><td class="tp2__n"><code>{n}</code></td><td class="tp2__ro">{ro}'
                       f'<span>{SCURT[n]}</span></td><td class="tp2__ex"><code>{ex.replace("<", "&lt;")}</code></td></tr>')
        out.append("</table></section>")
    out.append("</div>")
    return "".join(out)


def tipuri_lista_manual():
    out = ['<div class="tpl">']
    for grupa, c, rand in TIPURI_LISTA:
        out.append(f'<section class="tpl__g"><h4>{grupa}</h4><div class="tpl__l tpl__l--{len(rand)}">')
        for n, ro, d, ex, la in rand:
            out.append(f'<div class="tpl__c" style="--c:{c}"><div class="tpl__n"><code>{n}</code><span>{ro}</span></div>'
                       f'<p class="tpl__d">{d}</p><code class="tpl__ex">{ex.replace("<", "&lt;")}</code>'
                       f'<p class="tpl__la">La noi: {la}</p></div>')
        out.append("</div></section>")
    out.append("</div>")
    return "".join(out)


TIPURI_CONSOLA = {
    "id": "c1-tipuri", "fisier": "01_introducere.ipynb · 2. Variabile și tipuri",
    "sarcina": "Scrie tipul fiecărei variabile, cum îl numește Python.",
    "cod": ['tara = "RO"', "numar_tari = 178", "ore_de_studiu = 8.5", "este_student = True",
            "ocupatie = None", 'tari = ["RO", "IT", "ES"]', 'persoana = {"name": "Ana", "city": "Cluj-Napoca"}'],
    "env": {"tara": "RO", "numar_tari": 178, "ore_de_studiu": 8.5, "este_student": True,
            "ocupatie": None, "tari": ["RO", "IT", "ES"], "persoana": {"name": "Ana", "city": "Cluj-Napoca"}},
    "vars": [
        {"n": "tara", "t": "str", "e": "Ghilimelele fac din RO un text."},
        {"n": "numar_tari", "t": "int", "e": "Fără ghilimele și fără zecimale: număr întreg."},
        {"n": "ore_de_studiu", "t": "float", "e": "Punctul zecimal îl face float."},
        {"n": "este_student", "t": "bool", "e": "True și False, cu majusculă: valori logice."},
        {"n": "ocupatie", "t": "NoneType", "e": "None e lipsa valorii; tipul lui se numește NoneType."},
        {"n": "tari", "t": "list", "e": "Paranteze drepte: listă."},
        {"n": "persoana", "t": "dict", "e": "Acolade cu perechi cheie: valoare: dicționar."},
    ],
}

sl("s9o", "Tipuri de date", "Ce tipuri de date există",
   "<h2>Tipurile de date din Python</h2>"
   "<p class=\"cheie\">Tipul decide ce poți face cu o valoare: cu numere socotești, "
   "textele le lipești, listele le parcurgi.</p>"
   + tipuri_lista(),
   manual=
   "<h2>Tipurile de date din Python</h2>"
   "<p>Tipul unei valori decide ce poți face cu ea. Nu e o chestiune de "
   "pedanterie: o coloană de populații citită ca text se sortează ca text: "
   "„19051804” (România) ajunge înaintea lui „9584627” (Ungaria), pentru că 1 "
   "vine înaintea lui 9. Și nimeni nu primește vreo eroare.</p>"
   + tipuri_lista_manual()
   + "<h3>Toată familia</h3><p>Lista de sus are tipurile pe care le folosim. Python mai are câteva, "
   "mai rare la analiza datelor: le vezi pe toate în arborele de mai jos.</p>"
   + ix("arbore", "Arborele tipurilor",
        {"titlu": "Apasă pe orice tip",
         "intro": "Vezi ce e, cum arată, și unde apare la noi.",
         "legenda": True, "radacina": "valoare", "ramuri": RAMURI_PY}))


sl("s9", "Tipuri de date", "Ce tip are fiecare valoare",
   "<h2>Ce tip are fiecare valoare?</h2>"
   + ix("consola", "Celula de la începutul caietului", TIPURI_CONSOLA),
   manual=
   "<h2>Ce tip are fiecare valoare?</h2>"
   "<p>În Jupyter, ultima linie a unei celule se afișează singură: scrii "
   "<code>type(tara)</code> și primești <code>str</code>, fără <code>print</code>. "
   "Într-un fișier <code>.py</code> ai nevoie de <code>print(type(tara))</code>, care "
   "afișează <code>&lt;class 'str'&gt;</code>. E același răspuns, scris altfel.</p>"
   + ix("consola", "Scrie tipul, apoi verifică", TIPURI_CONSOLA)
   + ix("pas", "Cinci valori, cinci tipuri", PAS_TIPURI))


CAPCANE = (
    '<div class="capc">'
    '<div><code class="capc__e">"2024" &lt; "999"</code><code class="capc__r">True</code>'
    "<p>Textele se compară literă cu literă, iar 2 vine înaintea lui 9.</p></div>"
    '<div><code class="capc__e">float("3,7")</code><code class="capc__r">ValueError</code>'
    "<p>Virgula zecimală, din fișierele românești. Aici măcar crapă.</p></div>"
    '<div><code class="capc__e">None   0   ""</code><code class="capc__r">trei lucruri</code>'
    "<p>Lipsă, zero, text gol. Într-un tabel arată la fel, într-o medie nu.</p></div>"
    "</div>")

sl("s11", "Tipuri de date", "Capcanele de tip",
   "<h2>Greșelile care nu dau eroare</h2>"
   + CAPCANE
   + ix("prezice", "Text plus text", {
       "id": "c1-prezice-tip", "fisier": "01_introducere.ipynb · 2. Variabile",
       "sarcina": "Nu o rula: ghicește.",
       "cod": "varsta_text = \"24\"\nprint(varsta_text + \"1\")",
       "intrebare": "Ce afișează?",
       "variante": ["25", "241", "Eroare", "24 1"],
       "corect": 1,
       "indiciu": "Ghilimelele fac din 24 un text. Ce face <code>+</code> cu două texte?",
       "laBine": "Plusul lipește textele, nu le adună.",
       "explicatie": "Cu ghilimele, <code>\"24\"</code> e <code>str</code>, iar <code>+</code> "
                     "între două texte le lipește. Exact asta pățește un an citit din CSV ca text."}),
   manual=
   "<h2>Greșelile care nu dau eroare</h2>"
   "<p>Greșelile de tip care crapă se repară în două minute. Problema o fac "
   "cele care trec: codul rulează, fișierul se scrie, iar rezultatul e greșit "
   "fără ca nimic să semnaleze.</p>"
   + ix("prezice", "Text plus text", {
       "id": "c1-prezice-tip", "fisier": "01_introducere.ipynb · 2. Variabile",
       "sarcina": "Aceeași celulă ca în caietul de azi. Nu o rula: ghicește.",
       "cod": "varsta_text = \"24\"\nprint(varsta_text + \"1\")",
       "intrebare": "Ce afișează?",
       "variante": ["25", "241", "Eroare", "24 1"],
       "corect": 1,
       "indiciu": "Ghilimelele fac din 24 un text. Ce face <code>+</code> cu două texte?",
       "laBine": "Plusul lipește textele, nu le adună.",
       "explicatie": "Cu ghilimele, <code>\"24\"</code> e <code>str</code>, iar <code>+</code> "
                     "între două texte le lipește. Exact asta pățește un an citit din CSV ca text. "
                     "Mai jos îl repari cu <code>int()</code>."})
   + ix("cod", "Repară două conversii", {
       "id": "c1-cod-tipuri", "fisier": "tipuri.py",
       "sarcina": "Anul a venit ca text. Fă din el un număr ca să poți aduna, apoi din nou text ca să-l lipești într-o propoziție.",
       "cod": "an_text = \"2024\"\n\n"
              "# din text in numar, ca sa poti aduna\n"
              "urmatorul = {{1}}(an_text) + 1\n"
              "print(urmatorul)                 # 2025\n\n"
              "# din numar inapoi in text, ca sa-l lipesti\n"
              "mesaj = \"Datele merg pana in \" + {{2}}(urmatorul)\n"
              "print(mesaj)",
       "goluri": {
           "1": {"ok": ["int"], "ajutor": "funcția"},
           "2": {"ok": ["str"], "ajutor": "funcția"}},
       "indiciu": "Funcțiile de conversie au numele tipurilor: <code>int</code> face un număr întreg, <code>str</code> face text.",
       "iesire": "2025\nDatele merg pana in 2025",
       "laBine": "int și str, înainte și înapoi. Le vei folosi la fiecare curățare.",
       "laRau": "Fără ghilimele: aici se cer numele a două funcții.",
       "explicatie": "Fără conversii, <code>\"2024\" + 1</code> dă eroare, iar <code>\"Anul \" + 2025</code> la fel: "
                     "Python nu lipește text de număr. Mai periculos e cazul fără eroare, cel de mai sus: "
                     "<code>\"2024\" + \"1\"</code> dă liniștit <code>\"20241\"</code>."})
   + "<h3>A treia capcană: virgula zecimală</h3>"
   "<p>Un fișier românesc scrie <code>3,7</code>. "
   "<code>float(\"3,7\")</code> crapă, ceea ce e vestea bună. Vestea proastă e "
   "că un fișier întreg citit greșit îți dă o coloană de text pe care o "
   "sortezi alfabetic fără să observi. Reparația e "
   "<code>float(x.replace(\",\", \".\"))</code>, sau "
   "<code>decimal=\",\"</code> la citire.</p>"
   + nota("Confuzia care costă cel mai mult",
          "<code>None</code>, <code>0</code> și <code>\"\"</code> arată la fel "
          "într-un tabel gol. Zero e o măsurătoare; <code>None</code> e absența "
          "ei. Tratate la fel într-o medie, rezultatul e greșit fără nicio "
          "eroare."))


OCTETI = (
    '<div class="oct"><h4>Înainte să alegi: cât ocupă un număr întreg</h4>'
    '<div class="oct__r"><code>SMALLINT</code><span class="oct__b"><i></i><i></i></span>'
    '<span class="oct__t"><b>2 octeți</b> · până la 32.767</span></div>'
    '<div class="oct__r"><code>INT</code><span class="oct__b"><i></i><i></i><i></i><i></i></span>'
    '<span class="oct__t"><b>4 octeți</b> · până la 2.147.483.647</span></div>'
    '<div class="oct__r oct__r--big"><code>BIGINT</code><span class="oct__b"><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i></span>'
    '<span class="oct__t"><b>8 octeți</b> · până la 9.223.372.036.854.775.807</span></div>'
    '<p class="oct__n">Fiecare valoare din coloană ocupă atâția octeți, pe fiecare rând. Alegi cel mai mic tip în '
    'care încape <b>cea mai mare valoare posibilă</b>, nu cea mai mare pe care ai văzut-o. La cele 1,8 milioane de '
    'rânduri din fișierul pe județe, diferența dintre INT și BIGINT e de 7,2 MB, doar pentru o coloană. '
    'Detaliile: <a class="leg" href="https://www.postgresql.org/docs/current/datatype-numeric.html" '
    'target="_blank" rel="noopener">tipurile numerice în PostgreSQL</a>.</p></div>')


sl("s11c", "Tipuri de date", "Conversiile",
   "<h2>Din text în număr, și înapoi</h2>"
   + ix("cod", "Repară două conversii", {
       "id": "c1-cod-tipuri", "fisier": "tipuri.py",
       "sarcina": "Din text în număr, ca să aduni; apoi înapoi în text, ca să-l lipești.",
       "cod": "an_text = \"2024\"\n"
              "urmatorul = {{1}}(an_text) + 1           # 2025\n"
              "mesaj = \"Datele merg pana in \" + {{2}}(urmatorul)\n"
              "print(mesaj)",
       "goluri": {
           "1": {"ok": ["int"], "ajutor": "funcția"},
           "2": {"ok": ["str"], "ajutor": "funcția"}},
       "indiciu": "Funcțiile de conversie au numele tipurilor: <code>int</code> face un număr întreg, <code>str</code> face text.",
       "iesire": "Datele merg pana in 2025",
       "laBine": "int și str, înainte și înapoi. Le vei folosi la fiecare curățare.",
       "laRau": "Fără ghilimele: aici se cer numele a două funcții.",
       "explicatie": "Fără conversii, <code>\"2024\" + 1</code> dă eroare, iar <code>\"Anul \" + 2025</code> la fel: "
                     "Python nu lipește text de număr. Mai periculos e cazul fără eroare: "
                     "<code>\"2024\" + \"1\"</code> dă liniștit <code>\"20241\"</code>."}),
   manual="")


sl("s12", "Tipuri de date", "Tipuri în SQL",
   "<h2>În baza de date, tipul se declară</h2>"
   "<p>Ce nu se potrivește, e respins. Uită-te la valori și alege.</p>"
   + OCTETI
   + ix("coloane", "Tabelul SCI, la cursul 5", {
       "id": "c1-sql-coloane", "poarta": False,
       "fisier": "create table sci (…)",
       "nota": "valori adevărate din country.csv",
       "sarcina": "Pentru fiecare coloană, tipul potrivit.",
       "tipuri": ["CHAR(2)", "VARCHAR(50)", "TEXT", "INT", "BIGINT", "BOOLEAN"],
       "coloane": [
           {"nume": "user_country", "ok": "CHAR(2)",
            "de_ce": "lungime fixă, exact două caractere; orice altceva e respins la inserare"},
           {"nume": "friend_country", "ok": "CHAR(2)",
            "de_ce": "același cod, aceeași regulă"},
           {"nume": "scaled_sci", "ok": "INT",
            "de_ce": "Meta scalează indicele astfel încât maximul să fie exact 1.000.000.000, sub limita lui INT (2.147.483.647). BIGINT ar merge și el, dar ocupă dublu fără motiv"}],
       "cap": [["RO", "RO", 6252768], ["RO", "MD", 173794],
               ["RO", "AT", 124693], ["RO", "HU", 85021]],
       "laBine": "Exact tabelul pe care îl vei crea în baza de date, la cursul 5.",
       "laRau": "Codurile au lungime fixă. Pentru indice, uită-te cât de mare "
                "poate fi valoarea."}),
   manual=
   "<h2>Tipuri de date în SQL</h2>"
   "<p>De la cursul 5 datele stau într-o bază de date, nu în fișiere. Acolo "
   "tipurile nu se ghicesc la citire, se declară la crearea tabelului, iar "
   "baza refuză ce nu se potrivește. E mai strict decât Python, și e un "
   "avantaj: greșeala apare la inserare, nu peste trei săptămâni.</p>"
   + tabel(["Familie", "Tipuri", "Pentru ce"], [
       ["Numerice", "~INT, BIGINT, REAL, NUMERIC", "Numărători, valori calculate"],
       ["Dată și timp", "~DATE, TIME, TIMESTAMP", "Momente; nu le ține niciodată ca text"],
       ["Caractere", "~CHAR, VARCHAR, TEXT", "Nume, coduri, descrieri"],
       ["Logic", "~BOOLEAN", "Adevărat sau fals"],
       ["Structurat", "~JSON, JSONB", "Răspunsuri de API păstrate ca atare"],
   ])
   + "<h3>CHAR, VARCHAR sau TEXT</h3>"
   "<ul>"
   "<li><code>CHAR(n)</code> are lungime fixă și completează cu spații. Bun "
   "pentru coduri de lungime constantă.</li>"
   "<li><code>VARCHAR(n)</code> are lungime variabilă, cu o limită.</li>"
   "<li><code>TEXT</code> e fără limită. În PostgreSQL nu e mai lent decât "
   "VARCHAR, deci e alegerea implicită rezonabilă.</li></ul>"
   + OCTETI
   + ix("coloane", "Tabelul SCI, la cursul 5", {
       "id": "c1-sql-coloane", "poarta": False,
       "fisier": "create table sci (…)",
       "nota": "valori adevărate din country.csv",
       "sarcina": "Pentru fiecare coloană, tipul potrivit.",
       "tipuri": ["CHAR(2)", "VARCHAR(50)", "TEXT", "INT", "BIGINT", "BOOLEAN"],
       "coloane": [
           {"nume": "user_country", "ok": "CHAR(2)",
            "de_ce": "lungime fixă, exact două caractere"},
           {"nume": "friend_country", "ok": "CHAR(2)",
            "de_ce": "același cod, aceeași regulă"},
           {"nume": "scaled_sci", "ok": "INT",
            "de_ce": "maximul e 1.000.000.000, sub limita lui INT"}],
       "cap": [["RO", "RO", 6252768], ["RO", "MD", 173794],
               ["RO", "AT", 124693], ["RO", "HU", 85021]],
       "laBine": "Exact tabelul din baza de date, la cursul 5.",
       "laRau": "Codurile au lungime fixă."})
   + nota("Și cheia primară",
          "<code>primary key (user_country, friend_country)</code> e ce "
          "împiedică aceeași pereche să intre de două ori: greșeala clasică la "
          "reîncărcarea unui fișier."))


RAMURI_GEO = [
    {"nume": "De bază", "tipuri": [
        {"n": "Point", "cls": "geometry", "d": "Un punct: o pereche de coordonate.",
         "ex": "POINT(23.59 46.77)", "la": "Centrul unui județ, de unde calculăm distanțe."},
        {"n": "Curve", "cls": "abstract", "d": "Categoria liniilor. Nu se folosește direct."},
        {"n": "Surface", "cls": "abstract", "d": "Categoria suprafețelor. Nu se folosește direct."}]},
    {"nume": "Linii", "tipuri": [
        {"n": "LineString", "cls": "Curve", "d": "O linie: o succesiune de puncte.",
         "ex": "LINESTRING(23.5 46.7, 23.6 46.8)", "la": "Un râu, un drum, o graniță."},
        {"n": "CircularString", "cls": "Curve", "d": "Linie din arce de cerc, nu din segmente."},
        {"n": "CompoundCurve", "cls": "Curve", "d": "Segmente drepte și arce, lipite într-o singură linie."}]},
    {"nume": "Suprafețe", "tipuri": [
        {"n": "Polygon", "cls": "Surface", "d": "O suprafață închisă, eventual cu găuri.",
         "ex": "POLYGON((23.5 46.7, 23.6 46.7,\n         23.6 46.8, 23.5 46.7))",
         "la": "Conturul unui județ. Două județe sunt vecine dacă poligoanele lor se ating."},
        {"n": "CurvePolygon", "cls": "Surface", "d": "Poligon cu laturi curbe."}]},
    {"nume": "Colecții", "tipuri": [
        {"n": "MultiPoint", "cls": "GeometryCollection", "d": "Mai multe puncte, ca o singură înregistrare."},
        {"n": "MultiLineString", "cls": "GeometryCollection", "d": "Mai multe linii, ca o singură înregistrare."},
        {"n": "MultiPolygon", "cls": "GeometryCollection",
         "d": "Mai multe suprafețe, ca o singură înregistrare.",
         "la": "România cu insulele din Deltă: un rând, nu trei."},
        {"n": "GeometryCollection", "cls": "geometry",
         "d": "Amestec de geometrii diferite. Rar; de obicei semn că datele nu sunt curate."}]},
]

GEOMETRII = [
    {"k": "point", "n": "Point", "et": "punct", "dim": 0,
     "def": "O poziție: o pereche de coordonate (x, y), opțional cu z (altitudine) și m (o măsură). "
            "În standardul Simple Features (OGC, ISO 19125) e geometria de dimensiune 0.",
     "wkt": "POINT (23.59 46.77)",
     "py": "shapely.Point(23.59, 46.77)\ngdf.geometry.x, gdf.geometry.y",
     "pg": "geometry(Point, 4326)\nST_X(geom), ST_Y(geom), ST_Distance(a, b)",
     "valid": "Orice pereche de numere. Atenție la ordine: în WKT și GeoJSON e x, y, adică "
              "longitudine, apoi latitudine, invers față de cum le spunem de obicei.",
     "la": "Centroidul fiecărui județ (<code>harta.centroid</code>). Distanța dintre două județe e "
           "distanța dintre centroizii lor, în metri, împărțită la 1.000."},
    {"k": "multipoint", "n": "MultiPoint", "et": "mai multe puncte", "dim": 0,
     "def": "O colecție de puncte, păstrată ca o singură geometrie, într-un singur rând.",
     "wkt": "MULTIPOINT ((23.59 46.77), (26.10 44.43))",
     "py": "shapely.MultiPoint([(23.59, 46.77), (26.10, 44.43)])",
     "pg": "ST_NumGeometries(geom), ST_GeometryN(geom, 1)",
     "valid": "Punctele se pot repeta. <code>ST_IsSimple</code> îți spune dacă nu se repetă.",
     "la": "Nu o folosim. Ar fi, de exemplu, toate centrele universitare ale unei țări ca un singur obiect."},
    {"k": "linestring", "n": "LineString", "et": "linie", "dim": 1,
     "def": "O succesiune de cel puțin două puncte, unite prin segmente drepte. Geometria de dimensiune 1.",
     "wkt": "LINESTRING (23.59 46.77, 24.01 46.54, 26.10 44.43)",
     "py": "shapely.LineString([...]).length",
     "pg": "ST_Length(geom), ST_LineInterpolatePoint(geom, 0.5)",
     "valid": "Cel puțin două puncte distincte. E <em>simplă</em> dacă nu se intersectează singură. "
              "Închisă, cu primul punct egal cu ultimul, devine <code>LinearRing</code>: inelul unui poligon.",
     "la": "Liniile dintre un județ și partenerii lui, pe harta de la cursul 6."},
    {"k": "multilinestring", "n": "MultiLineString", "et": "mai multe linii", "dim": 1,
     "def": "Mai multe linii, ca o singură geometrie.",
     "wkt": "MULTILINESTRING ((…), (…))",
     "py": "shapely.MultiLineString([[...], [...]])",
     "pg": "ST_LineMerge(geom), ST_Length(geom)",
     "valid": "Fiecare linie trebuie să fie validă; liniile se pot atinge și intersecta.",
     "la": "Granița României cu Ucraina, care e în două bucăți: una la nord, una în Delta Dunării."},
    {"k": "polygon", "n": "Polygon", "et": "poligon", "dim": 2,
     "def": "O suprafață mărginită de un inel exterior închis, cu zero sau mai multe inele interioare, "
            "adică găuri. Geometria de dimensiune 2.",
     "wkt": "POLYGON ((0 0, 6 0, 6 6, 0 6, 0 0),\n         (2 2, 4 2, 4 4, 2 4, 2 2))",
     "py": "shapely.Polygon(exterior, [gaura])\n.area, .centroid, .touches(alt), .is_valid",
     "pg": "ST_Area, ST_Centroid, ST_Touches, ST_Intersects, ST_IsValid, ST_MakeValid",
     "valid": "Inelele sunt închise (primul punct e și ultimul) și au cel puțin 4 puncte; nu se "
              "autointersectează; găurile stau înăuntru și ating exteriorul cel mult într-un punct. "
              "Repari cu <code>make_valid</code>. GeoJSON (RFC 7946) cere inelul exterior în sens "
              "invers acelor de ceasornic.",
     "la": "Conturul fiecărui județ și al fiecărei regiuni NUTS. De aici ies centroizii, ariile și vecinătatea."},
    {"k": "multipolygon", "n": "MultiPolygon", "et": "mai multe poligoane", "dim": 2,
     "def": "Mai multe poligoane, ca o singură înregistrare.",
     "wkt": "MULTIPOLYGON (((…)), ((…)), ((…)))",
     "py": "harta.dissolve(\"CNTR_CODE\")   # județele lipite pe țări",
     "pg": "ST_Union(geom), ST_Collect(geom)",
     "valid": "Interioarele poligoanelor nu au voie să se suprapună; se pot atinge doar în puncte izolate.",
     "la": "Țările: un rând pe țară, cu insulele în aceeași geometrie. În caietul 07 lipim județele pe "
           "țări cu <code>dissolve</code>, ca să aflăm care țări au graniță comună."},
    {"k": "collection", "n": "GeometryCollection", "et": "amestec", "dim": 3,
     "def": "Un amestec de geometrii de feluri diferite: puncte, linii și poligoane laolaltă.",
     "wkt": "GEOMETRYCOLLECTION (POINT (…), LINESTRING (…))",
     "py": "shapely.GeometryCollection([...])",
     "pg": "ST_CollectionExtract(geom, 3)   # păstrează doar poligoanele",
     "valid": "Standardul o permite, dar o coloană de date are de obicei un singur fel de geometrie.",
     "la": "Nu o folosim. Apare des ca rezultat al unei intersecții; atunci extragi ce îți trebuie."},
]

CRS = (
    "<h3>Coordonatele n-au sens fără sistemul lor</h3>"
    '<div class="crs">'
    "<div><b>EPSG:4326</b><span>WGS 84, grade</span>"
    "<p>Latitudine și longitudine. Bun ca să stochezi și să afișezi, rău pentru distanțe: un grad de "
    "longitudine are 111 km la Ecuator și vreo 76 km la Cluj.</p></div>"
    "<div><b>EPSG:3035</b><span>ETRS89 / LAEA Europe, metri</span>"
    "<p>Proiecția cu arii egale a Uniunii Europene. În ea calculăm distanțele și ariile. Hărțile NUTS de "
    "la Eurostat (GISCO) vin direct în 3035.</p></div>"
    "<div><b>1:20 milioane</b><span>contururi generalizate</span>"
    "<p>Pe harta simplificată, granițele vecinilor nu se ating perfect. De aceea, în caietul 07, granița "
    "comună se caută cu o zonă-tampon de 10 km, nu cu <code>touches</code>.</p></div>"
    "</div>")

sl("s13", "Tipuri de date", "Tipuri spațiale",
   "<h2>Tipuri de date spațiale</h2>"
   "<p>Ne trebuie ca să definim „vecin” și „distanță”. Apasă pe fiecare geometrie.</p>"
   + ix("geom", "Geometriile din Simple Features", {"geometrii": GEOMETRII}),
   manual=
   "<h2>Tipuri de date spațiale</h2>"
   "<p>Datele spațiale au tipuri ale lor, definite de standardul Simple Features (OGC, ISO 19125), pe care "
   "îl urmează Shapely, GeoPandas și PostGIS deopotrivă. Ierarhia are trei forme de bază, după "
   "dimensiune: punctul (0), linia (1) și suprafața (2), fiecare cu varianta ei „multi”.</p>"
   + ix("geom", "Geometriile din Simple Features", {"geometrii": GEOMETRII})
   + CRS
   + "<p>Standardul mai are și curbe din arce de cerc (<code>CircularString</code>, "
   "<code>CompoundCurve</code>, <code>CurvePolygon</code>), din extensia SQL/MM. Apar rar în datele publice; "
   "contururile NUTS, de exemplu, sunt numai segmente drepte.</p>"
   + surse("Documentația", [
       ("Shapely: geometrii", "https://shapely.readthedocs.io/en/stable/geometry.html",
        "tipurile, construcția lor, operațiile"),
       ("GeoPandas: proiecții", "https://geopandas.org/en/stable/docs/user_guide/projections.html",
        "CRS, to_crs, de ce contează"),
       ("PostGIS: tipul geometry", "https://postgis.net/docs/using_postgis_dbmanagement.html",
        "geometrii în baza de date"),
       ("Eurostat GISCO: NUTS", "https://ec.europa.eu/eurostat/web/gisco/geodata/statistical-units/territorial-units-statistics",
        "contururile NUTS 2024, la scări și proiecții diferite"),
   ]))


sl("s13c", "Tipuri de date", "Coordonate și proiecții",
   "<h2>Coordonatele n-au sens fără sistemul lor</h2>"
   + CRS.replace("<h3>Coordonatele n-au sens fără sistemul lor</h3>", ""),
   manual="")


sl("s14", "Tipuri de date", "Tipuri de fișiere",
   "<h2>Text sau binar</h2>"
   "<p class=\"cheie\">Text îl citești cu ochiul. Binar are nevoie de programul lui.</p>"
   + ix("sortare", "Pune fiecare extensie în coșul ei", {
       "id": "c1-cod-fisiere", "poarta": False,
       "sarcina": "Întrebarea de control: poate Git să-ți arate ce s-a schimbat "
                  "în el, rând cu rând?",
       "cosuri": [{"t": "Text", "d": "lizibil, versionabil"},
                  {"t": "Binar", "d": "are nevoie de un program"}],
       "elemente": [{"t": ".csv", "cos": 0}, {"t": ".json", "cos": 0},
                    {"t": ".xlsx", "cos": 1}, {"t": ".parquet", "cos": 1},
                    {"t": ".geojson", "cos": 0}, {"t": ".shp", "cos": 1},
                    {"t": ".md", "cos": 0}, {"t": ".pkl", "cos": 1},
                    {"t": ".yaml", "cos": 0}, {"t": ".sqlite", "cos": 1},
                    {"t": ".xml", "cos": 0}, {"t": ".png", "cos": 1}],
       "laBine": "Regula: dacă îl poți deschide în Notepad și înțelegi ceva, e text.",
       "laRau": "Gândește-te ce se întâmplă dacă îl deschizi într-un editor simplu.",
       "explicatie": "<code>.geojson</code> și <code>.xml</code> păcălesc pentru "
                     "că par „tehnice”, dar sunt text simplu. <code>.parquet</code> "
                     "și <code>.shp</code> păcălesc invers: conțin tabele, dar "
                     "binar. Consecința: într-un depozit Git, o modificare "
                     "într-un <code>.csv</code> se vede rând cu rând, una "
                     "într-un <code>.xlsx</code> apare ca „fișier schimbat”, atât."}),
   manual=
   "<h2>Tipuri de fișiere</h2>"
   "<p>Prima împărțire, și cea mai importantă: un fișier <strong>text</strong> "
   "îl poți deschide în orice editor și îl poți citi cu ochiul liber. Un fișier "
   "<strong>binar</strong> nu, are nevoie de programul care îl înțelege. "
   "Distincția decide și dacă Git îți poate arăta ce s-a schimbat.</p>"
   + ix("sortare", "Pune fiecare extensie în coșul ei", {
       "id": "c1-cod-fisiere", "poarta": False,
       "sarcina": "Poate Git să-ți arate ce s-a schimbat în el, rând cu rând?",
       "cosuri": [{"t": "Text", "d": "lizibil, versionabil"},
                  {"t": "Binar", "d": "are nevoie de un program"}],
       "elemente": [{"t": ".csv", "cos": 0}, {"t": ".json", "cos": 0},
                    {"t": ".xlsx", "cos": 1}, {"t": ".parquet", "cos": 1},
                    {"t": ".geojson", "cos": 0}, {"t": ".shp", "cos": 1},
                    {"t": ".md", "cos": 0}, {"t": ".pkl", "cos": 1},
                    {"t": ".yaml", "cos": 0}, {"t": ".sqlite", "cos": 1},
                    {"t": ".xml", "cos": 0}, {"t": ".png", "cos": 1}],
       "laBine": "Dacă îl poți deschide în Notepad și înțelegi ceva, e text.",
       "laRau": "Gândește-te ce vezi într-un editor simplu.",
       "explicatie": "<code>.geojson</code> și <code>.xml</code> par „tehnice”, "
                     "dar sunt text simplu."})
   + tabel(["Format", "Când îl folosești"], [
       ["~.csv", "Tabele simple, plate. Universal, dar nu păstrează tipurile."],
       ["~.json", "Date cu structură imbricată. Ce întorc aproape toate API-urile."],
       ["~.parquet", "Tabele mari. Binar, compact, rapid, păstrează tipurile."],
       ["~.geojson", "Date cu geometrie. Text, deci lizibil și versionabil."],
       ["~.shp", "Shapefile: geometrie, dar binar și format din mai multe fișiere."],
       ["~.env", "Chei și parole. Niciodată în depozit."],
   ]))


# ===========================================================================
#  15-16. JSON
# ===========================================================================

ANATOMIE = {
    "id": "c1-json-anatomie", "poarta": False, "cerute": 4,
    "intro": "Apasă pe o parte ca s-o vezi aprinsă în cod.",
    "linii": [
        "{",
        "  \"paginare\": { \"pagina\": 1, \"total\": 3 },",
        "  \"date\": [",
        "    {",
        "      \"tara\": { \"cod\": \"RO\", \"nume\": \"Romania\" },",
        "      \"an\": \"2024\",",
        "      \"valoare\": 19051804,",
        "      \"coordonate\": [46.77, 23.59],",
        "      \"estimat\": false",
        "    },",
        "    {",
        "      \"tara\": { \"cod\": \"RO\", \"nume\": \"Romania\" },",
        "      \"an\": \"2022\",",
        "      \"valoare\": null,",
        "      \"coordonate\": [46.77, 23.59],",
        "      \"estimat\": true",
        "    }",
        "  ]",
        "}",
    ],
    "parti": [
        {"et": "Obiectul rădăcină", "py": "dict", "l": [0, 18],
         "d": "Tot răspunsul, între acolade. Un <b>obiect</b> e o colecție de perechi nume/valoare. "
              "În Python devine un <code>dict</code> cu două chei: <code>paginare</code> și <code>date</code>."},
        {"et": "Tablou", "py": "list", "l": [2, 17],
         "d": "Între paranteze drepte: o listă ordonată de valori. Aici, de obiecte. Numai asta "
              "devine tabel: fiecare element al tabloului e un rând."},
        {"et": "Element al tabloului", "py": "dict", "l": [3, 9],
         "d": "Un obiect din tablou: un rând al viitorului tabel. Numele lui devin coloane."},
        {"et": "Obiect imbricat", "py": "dict în dict", "l": [4, 4],
         "d": "O valoare care e, la rândul ei, un obiect. În tabel, <code>json_normalize</code> îl "
              "desface în două coloane: <code>tara.cod</code> și <code>tara.nume</code>."},
        {"et": "Pereche nume/valoare", "py": "cheie: valoare", "l": [6, 6],
         "d": "Numele e mereu un șir între ghilimele, urmat de două puncte și de valoare. Aici valoarea "
              "e un <b>număr</b>, fără ghilimele, care devine <code>int</code>."},
        {"et": "Șir de caractere", "py": "str", "l": [5, 5],
         "d": "<code>\"2024\"</code> are ghilimele, deci e un <b>șir</b> (string), nu un număr. Capcana "
              "clasică: <code>\"2024\" + 1</code> dă eroare, iar <code>\"2024\" &lt; \"999\"</code> e "
              "adevărat, fiindcă textul se compară literă cu literă."},
        {"et": "Tablou de numere", "py": "list", "l": [7, 7],
         "d": "Un tablou ca valoare. Într-un tabel plat nu încape ca atare: îl desfaci în două coloane "
              "sau îl lași ca listă într-o celulă, ceea ce de obicei doare mai târziu."},
        {"et": "true / false", "py": "bool", "l": [8, 8],
         "d": "Valorile logice se scriu cu literă mică în JSON și devin <code>True</code> și "
              "<code>False</code> în Python."},
        {"et": "null", "py": "None", "l": [13, 13],
         "d": "<code>null</code> spune explicit „nu există valoare”. Nu e zero. În Python devine "
              "<code>None</code>, în pandas <code>NaN</code>."},
    ],
}


LISTE_ACCES = {
    "vedere": "memorie",
    "env": {"tari": ["RO", "IT", "ES", "DE"],
            "persoana": {"name": "Ana", "age": 24, "city": "Cluj-Napoca", "student": True}},
    "provocari": [
        {"t": "prima țară", "cale": "tari[0]", "indiciu": "Numărătoarea începe de la 0."},
        {"t": "ultima țară, fără să numeri", "cale": "tari[-1]", "exact": True,
         "indiciu": "Pozițiile negative numără de la coadă: -1 e ultima."},
        {"t": "orașul Anei", "cale": "persoana[\"city\"]", "indiciu": "Într-un dicționar ceri cheia, între ghilimele."},
        {"t": "dacă Ana e studentă", "cale": "persoana[\"student\"]"},
    ],
    "exemplu": "tari[1]",
}

sl("s14l", "JSON", "Liste și dicționare",
   "<h2>Mai multe valori, împreună</h2>"
   "<p class=\"cheie\">Listă: valori în ordine, cerute după <b>poziție</b>. "
   "Dicționar: perechi, cerute după <b>cheie</b>.</p>"
   + ix("acces", "Apasă pe o căsuță sau scrie în consolă", LISTE_ACCES),
   manual=
   "<h2>Liste și dicționare</h2>"
   "<p>O listă ține valori în ordine; fiecare are o poziție, numărată de la 0. "
   "Un dicționar ține perechi cheie–valoare; o valoare se cere după numele "
   "cheii. Diferența dintre poziție și cheie e tot ce trebuie ca să citești "
   "un JSON, oricât de adânc.</p>"
   + ix("acces", "Apasă pe o căsuță sau scrie în consolă", LISTE_ACCES)
   + ix("pas", "Poziție și cheie, rând cu rând", PAS_LISTE)
   + PZ_INDEX)

sl("s14p", "JSON", "Poziție sau cheie",
   "<h2>Poziție pentru liste, cheie pentru dicționare</h2>"
   + PZ_INDEX,
   manual="")

sl("s15", "JSON", "Formatul JSON",
   "<h2>Două structuri, imbricate oricât de adânc</h2>"
   "<p class=\"cheie\">Obiectul <code>{ }</code> devine <code>dict</code>. Tabloul <code>[ ]</code> devine <code>list</code>.</p>"
   + ix("anatomie", "Un răspuns, simplificat, pe bucăți", ANATOMIE),
   manual=
   "<h2>Formatul JSON</h2>"
   "<p>JSON are exact două structuri: <strong>obiectul</strong>, între acolade, "
   "care e o colecție de perechi cheie–valoare, și <strong>tabloul</strong>, "
   "între paranteze drepte, care e o listă ordonată. Se pot cuibări una în "
   "alta oricât de adânc, iar din asta ies toate răspunsurile de API pe care "
   "le veți vedea.</p>"
   + tabel(["În JSON", "În Python"], [
       ["~string", "~str"], ["~number", "~int / float"],
       ["~true / false", "~True / False"], ["~null", "~None"],
       ["~object", "~dict"], ["~array", "~list"],
   ])
   + "<p>Rădăcina poate fi oricare dintre cele două. Banca Mondială întoarce un "
   "tablou cu două elemente: paginarea, apoi datele.</p>"
   + ix("anatomie", "Un răspuns, simplificat, pe bucăți", ANATOMIE)
   + "<h3>Și cum devine tabel</h3>"
   "<p>Structura de sus nu e un tabel. Pasul care o face tabel e tot timpul "
   "același: alegi lista dinăuntru, și fiecare element al ei devine un "
   "rând.</p>"
   + ix("desfa", "Cum devine un răspuns un tabel", {
       "id": "c1-desfa",
       "sursa": "api.worldbank.org",
       "buton": "Arată-mi lista",
       "cheieCap": "paginare", "cheieLista": "date",
       "coloane": ["tara", "an", "populatie"],
       "elemente": [
           {"tara": "RO", "an": 2024, "populatie": 19051804},
           {"tara": "RO", "an": 2023, "populatie": 19061062},
           {"tara": "HU", "an": 2024, "populatie": 9562065},
       ],
       "p0": "Tot răspunsul, așa cum vine de la API.",
       "p1": "Lista dinăuntru: numai asta devine tabel.",
       "p2": "Fiecare element al listei a devenit un rând."})
   + nota("De aici vine json_normalize",
          "Operația pe care ai văzut-o are un nume și o funcție în pandas. "
          "O scriem la cursul 2, dar e bine să fi văzut întâi ce face."))


def _pers_py(x):
    """Persoanele din caiet, cu 0.0 păstrat ca float (în JSON e doar 0)."""
    y = dict(x)
    if isinstance(y["study_hours_per_week"], float) and y["study_hours_per_week"].is_integer():
        y["study_hours_per_week"] = {"__f": y["study_hours_per_week"]}
    return y


PERS_ACCES = {
    "vedere": "coborare",
    "env": {"user_data": {"users": [_pers_py(x) for x in PERS]}},
    "provocari": [
        {"t": "al doilea hobby al Anei", "cale": "user_data[\"users\"][0][\"hobbies\"][1]"},
        {"t": "orașul Elenei", "cale": "user_data[\"users\"][2][\"city\"]"},
        {"t": "ocupația lui Mihai", "cale": "user_data[\"users\"][1][\"occupation\"]"},
    ],
    "exemplu": "user_data[\"users\"][0]",
}

sl("s15p", "JSON", "Drumul prin persoane.json",
   "<h2>Coborâm până la o valoare</h2>"
   "<p class=\"cheie\">La fiecare nivel te întrebi un singur lucru: ce am în mână? "
   "Dicționar: ceri o cheie. Listă: ceri o poziție.</p>"
   + ix("acces", "Intră din cutie în cutie", PERS_ACCES),
   manual=
   "<h2>Drumul până la o valoare</h2>"
   "<p>Exemplul din caiet: <code>persoane.json</code>, trei persoane fictive. "
   "Tiparul e același în orice răspuns de API: la fiecare nivel verifici "
   "tipul, apoi ceri o cheie (dicționar) sau o poziție (listă).</p>"
   + ix("acces", "Intră din cutie în cutie", PERS_ACCES)
   + ix("pas", "Același drum, în cod", PAS_JSON))

WB_RASPUNS = [
    {"page": 1, "pages": 2, "per_page": 2, "total": 3},
    [{"indicator": {"id": "SP.POP.TOTL", "value": "Population, total"},
      "country": {"id": "RO", "value": "Romania"},
      "countryiso3code": "ROU", "date": "2024", "value": 19051804},
     {"indicator": {"id": "SP.POP.TOTL", "value": "Population, total"},
      "country": {"id": "RO", "value": "Romania"},
      "countryiso3code": "ROU", "date": "2023", "value": 19061062}]]

WB_ACCES = {
    "vedere": "arbore", "limbaj": "json",
    "env": {"raspuns": WB_RASPUNS},
    "provocari": [
        {"t": "câte pagini are răspunsul", "cale": "raspuns[0][\"pages\"]",
         "indiciu": "Paginarea e primul element al listei: poziția 0."},
        {"t": "populația din 2024", "cale": "raspuns[1][0][\"value\"]",
         "indiciu": "Datele sunt al doilea element, [1]. Prima înregistrare e [0]."},
        {"t": "anul celei de-a doua înregistrări", "cale": "raspuns[1][1][\"date\"]"},
        {"t": "numele țării", "cale": "raspuns[1][0][\"country\"][\"value\"]",
         "indiciu": "country e un obiect imbricat: mai ceri o cheie."},
    ],
    "exemplu": "raspuns[1][0]",
}

COD_JSON = {
    "id": "c1-cod-json", "fisier": "populatie.py",
    "sarcina": "Ai găsit mai sus drumul până la populația din 2024. Acum scrie-l în cod.",
    "cod": "raspuns = requests.get(url, params={\"format\": \"json\"}).json()\n\n"
           "date = raspuns[{{1}}]          # lista cu înregistrările\n"
           "populatie = date[0][{{2}}]     # numărul, din prima înregistrare\n"
           "print(populatie)              # 19051804",
    "goluri": {"1": {"ok": ["1"], "ajutor": "poziția"},
               "2": {"ok": ["\"value\"", "'value'"], "ajutor": "cheia"}},
    "indiciu": "Uită-te la „ce ai în mână” de mai sus: datele sunt pe poziția 1, iar numărul stă la cheia "
               "<code>\"value\"</code>.",
    "iesire": "19051804",
    "laBine": "Ăsta e drumul pe care îl vei scrie la cursul 2, de zeci de ori.",
    "laRau": "Numerotarea începe de la zero. Cheia se scrie între ghilimele.",
    "explicatie": "<code>raspuns[1]</code> sare peste obiectul de paginare. "
                  "<code>[\"value\"]</code> scoate numărul. Dacă valoarea lipsește, primești "
                  "<code>None</code>, nu zero."}

sl("s16", "JSON", "Drumul până la valoare",
   "<h2>Un răspuns real, desfăcut</h2>"
   "<p>Banca Mondială, populația României. Apasă pe orice rând: vezi drumul până la el și ce ai în mână la fiecare pas.</p>"
   + ix("acces", "API Banca Mondială", WB_ACCES),
   manual=
   "<h2>Drumul până la o valoare</h2>"
   "<p>Un răspuns adevărat de la API-ul Băncii Mondiale. Rădăcina e o listă cu două elemente: "
   "paginarea pe poziția 0, datele pe poziția 1. Fiecare înregistrare e un dicționar.</p>"
   + ix("acces", "API Banca Mondială", WB_ACCES)
   + ix("cod", "Scrie drumul", COD_JSON))


MASCA = {
    "coloane": ["user_country", "friend_country", "scaled_sci"],
    "coloana": "user_country", "valoare": "RO", "total": "31.684", "ramase": "178",
    "randuri": [["HU", "RO", "85021"], ["RO", "MD", "173794"], ["IT", "RO", "69327"],
                ["RO", "IT", "69327"], ["DE", "AT", "132496"], ["MD", "RO", "173794"],
                ["RO", "ES", "54179"], ["RO", "HU", "85021"]],
}

sl("s16c", "JSON", "Scrie drumul",
   "<h2>Același drum, în cod</h2>"
   + ix("cod", "Scrie drumul", COD_JSON),
   manual="")


sl("s16s", "Primul contact cu SCI", "Un tabel adevărat",
   "<h2>country.csv: păstrezi doar ce te interesează</h2>"
   "<p class=\"cheie\">O comparație pe o coloană dă True sau False pe fiecare rând. "
   "Tabelul păstrează doar rândurile True.</p>"
   + ix("masca", "Cum lucrează un filtru, pas cu pas", MASCA),
   sci=True,
   manual=
   "<h2>Primul contact cu SCI</h2>"
   "<p>Secțiunea 5 din caiet. Un rând din <code>country.csv</code> e o "
   "pereche de țări, deci fișierul are 178 × 178 = 31.684 de rânduri. Ca să "
   "te uiți la o singură țară, fixezi un capăt al perechii: o comparație pe "
   "coloană dă True sau False pe fiecare rând, iar tabelul păstrează doar "
   "rândurile adevărate.</p>"
   + ix("masca", "Cum lucrează un filtru, pas cu pas", MASCA)
   + "<p>Observă două rânduri din tabelul de sus: Ungaria cu România și România cu Ungaria au același "
   "indice, 85.021. SCI-ul e simetric, deci fiecare pereche apare de două ori.</p>"
   + ix("pas", "România și partenerii ei", PAS_SCI)
   + DIADIC_MANUAL)


sl("s16x", "Primul contact cu SCI", "Taie o felie",
   "<h2>Acum tu: doar perechile României</h2>"
   + DIADIC_SLIDE,
   sci=True, manual="")


# ===========================================================================
#  17-18. Mediul și proiectul
# ===========================================================================

FOLDER_VENV = (
    '<span class="a">proiect-dsw/</span>    <span class="c"># aici lucrezi</span>\n'
    '├── <span class="x">.venv/</span>      <span class="c"># nu umbli aici</span>\n'
    '├── data/       <span class="c"># datele</span>\n'
    '├── notebooks/  <span class="c"># caietele</span>\n'
    '└── code/       <span class="c"># fișierele .py</span>')

PASI_VENV = (
    '<ol class="venvp__pasi">'
    "<li><b>Faci folderul proiectului</b> și îl deschizi în VS Code: <em>File → Open Folder</em>.</li>"
    "<li><b>Deschizi terminalul</b>: <em>Terminal → New Terminal</em>. Pornește deja în folderul proiectului.</li>"
    "<li><b>Creezi mediul</b>, o singură dată:<br><code>py -m venv .venv</code>"
    '<span class="venvp__os">macOS / Linux: python3 -m venv .venv</span></li>'
    "<li><b>Instalezi pachetele în el</b>, cu Python-ul mediului:<br>"
    "<code>.venv\\Scripts\\python -m pip install pandas ipykernel</code>"
    '<span class="venvp__os">macOS / Linux: .venv/bin/python -m pip install pandas ipykernel</span></li>'
    "<li><b>În caiet</b> alegi <em>Select Kernel → Python Environments → .venv</em>. Gata.</li>"
    "</ol>")

sl("s17", "Mediul de lucru", "Mediul virtual",
   "<h2>Mediul virtual, în folderul proiectului</h2>"
   "<p class=\"cheie\">Lucrezi în folderul proiectului. Mediul virtual stă în el, în "
   "<code>.venv</code>, și acolo nu scrii nimic.</p>"
   + '<div class="venvp"><div class="venvp__fld">' + FOLDER_VENV + "</div>" + PASI_VENV + "</div>",
   manual=
   "<h2>Medii de lucru virtuale în Python</h2>"
   "<p>Python instalează pachetele într-un singur loc comun. Dacă lucrezi la "
   "două proiecte care au nevoie de versiuni diferite ale aceleiași "
   "biblioteci, al doilea îl strică pe primul în tăcere. Un mediu virtual e un "
   "dosar al proiectului, cu propria copie de Python și propriile pachete.</p>"
   "<p>Două reguli: mediul stă <strong>în folderul proiectului</strong>, iar tu "
   "<strong>nu lucrezi în el</strong>. Caietele, datele și codul tău stau alături, nu "
   "înăuntrul lui <code>.venv</code>.</p>"
   + '<div class="venvp"><div class="venvp__fld">' + FOLDER_VENV + "</div>" + PASI_VENV + "</div>"
   + "<h3>Și activarea?</h3>"
   "<p>Comenzile de mai sus folosesc direct Python-ul din <code>.venv</code>, deci nu trebuie "
   "activat nimic. Dacă vrei să scrii doar <code>pip</code> și <code>python</code>, activezi mediul: "
   "<code>.venv\\Scripts\\activate</code> pe Windows, <code>source .venv/bin/activate</code> pe macOS. "
   "Promptul începe atunci cu <code>(.venv)</code>. Pe Windows, PowerShell poate refuza scriptul de "
   "activare; VS Code activează oricum mediul singur în terminalele noi, după ce l-ai ales ca "
   "interpretor.</p>"
   + ix("terminal", "Exersează aici, înainte să o faci la tine", None,
        "Terminalul răspunde ca unul adevărat, inclusiv la greșeli.")
   + nota("De ce .venv nu urcă pe GitHub",
          "E mare, e făcut pentru calculatorul tău și se reface dintr-o comandă. Pe GitHub urcă lista "
          "pachetelor, <code>requirements.txt</code>, iar colegul își face propriul <code>.venv</code> din ea."))


sl("s17t", "Mediul de lucru", "Exersează",
   "<h2>Exersează, înainte să o faci la tine</h2>"
   + ix("terminal", "Terminalul pornește în folderul tău de utilizator", None,
        "Fă proiectul, intră în el, apoi creează mediul. Scrie <code>ajutor</code> dacă te blochezi."),
   manual="",
   dupa=ix("ordine", "Ordinea comenzilor", {
       "id": "c1-cod-venv",
       "sarcina": "Pune comenzile în ordinea în care se dau, de la folderul tău de utilizator până la "
                  "pachetele instalate.",
       "linii": ["mkdir proiect-dsw", "cd proiect-dsw", "py -m venv .venv",
                 ".venv\\Scripts\\python -m pip install pandas ipykernel",
                 ".venv\\Scripts\\python -m pip freeze > requirements.txt"],
       "indiciu": "Mediul se face în folderul proiectului, deci întâi folderul și intrarea în el. "
                  "Lista pachetelor are sens abia după ce le-ai instalat.",
       "iesire": "PS C:\\Users\\student\\proiect-dsw> .venv\\Scripts\\python -m pip freeze > requirements.txt\n"
                 "PS C:\\Users\\student\\proiect-dsw>",
       "laBine": "Exact asta faci la începutul fiecărui proiect.",
       "laRau": "Gândește-te în ce folder ești în momentul fiecărei comenzi.",
       "explicatie": "Dacă <code>py -m venv .venv</code> vine înainte de <code>cd</code>, mediul ajunge în "
                     "folderul tău de utilizator, nu în proiect, și nu dă nicio eroare. "
                     "<code>pip freeze</code> înainte de instalare scrie o listă goală."}))


NODURI_FOLDER = [
    {"n": "proiect-dsw/", "ind": 0, "scurt": "aici lucrezi",
     "d": "Folderul proiectului. Pe el îl deschizi în VS Code, în el pornește terminalul, iar toate "
          "căile din cod pornesc de aici. De la cursul 3, el devine depozitul echipei pe GitHub.",
     "cine": "tu", "git": "da: e chiar depozitul"},
    {"n": ".venv/", "ind": 1, "scurt": "nu umbli aici", "interzis": True,
     "d": "Python-ul proiectului și pachetele lui, făcute de <code>py -m venv .venv</code> și de "
          "<code>pip install</code>. Nu deschizi nimic de aici, nu salvezi nimic aici. Dacă se strică, "
          "îl ștergi și îl faci din nou.",
     "cine": "Python și pip, niciodată tu", "ex": "Lib/, Scripts/, pyvenv.cfg",
     "git": "nu: e trecut în <code>.gitignore</code>"},
    {"n": "data/", "ind": 1,
     "d": "Datele, așa cum au venit: le descarci o dată și nu le mai modifici. Ce produce curățarea "
          "salvezi în fișiere noi, alături, nu peste cele brute.",
     "cine": "descărcarea, apoi codul de curățare",
     "ex": "<code>country.csv</code> de pe HDX, migrația de la Eurostat",
     "git": "fișierele mici da; cele mari nu, se descarcă din cod"},
    {"n": "notebooks/", "ind": 1,
     "d": "Caietele Jupyter, pentru explorare: rulezi pas cu pas și te uiți la rezultat. Un caiet bun "
          "rulează de sus până jos după <em>Restart Kernel → Run All</em>.",
     "cine": "tu", "ex": "<code>01_introducere_si_datele_proiectului.ipynb</code>", "git": "da"},
    {"n": "code/", "ind": 1,
     "d": "Fișierele <code>.py</code>: ce rulezi din nou, la fel, de fiecare dată. Descărcarea datelor, "
          "funcțiile de curățare, construirea tabelului final.",
     "cine": "tu", "ex": "<code>descarca_migratie.py</code>", "git": "da"},
    {"n": "requirements.txt", "ind": 1, "fel": "fis",
     "d": "Lista pachetelor, cu versiunile lor. Din ea, un coleg își face propriul <code>.venv</code> "
          "identic: <code>pip install -r requirements.txt</code>.",
     "cine": "<code>pip freeze &gt; requirements.txt</code>", "git": "da"},
    {"n": ".gitignore", "ind": 1, "fel": "fis",
     "d": "Ce nu urcă pe GitHub: <code>.venv/</code>, fișierul <code>.env</code> cu chei și parole, "
          "fișierele mari de date.",
     "cine": "tu, o dată, la început", "git": "da"},
    {"n": "README.md", "ind": 1, "fel": "fis",
     "d": "Prima pagină a proiectului: ce întrebare are, de unde vin datele, cum se rulează.",
     "cine": "echipa", "git": "da: GitHub îl arată pe prima pagină a depozitului"},
]

sl("s18", "Proiectul tău", "Proiectul, pe disc",
   "<h2>Proiectul tău, pe disc</h2>"
   "<p class=\"cheie\">Un singur folder, cu un loc pentru fiecare lucru. Apasă pe fiecare.</p>"
   + ix("folder", "Folderul proiectului", {"noduri": NODURI_FOLDER}),
   manual=
   "<h2>Proiectul tău, pe disc</h2>"
   "<p>Un proiect de date nu e un caiet, e un folder: datele, caietele, codul și mediul virtual, "
   "fiecare la locul lui. Structura de mai jos e cea din caietele cursului.</p>"
   + ix("folder", "Folderul proiectului", {"noduri": NODURI_FOLDER})
   + ix("sortare", "Unde pui fiecare fișier?", {
       "id": "c1-folder",
       "sarcina": "Trage fiecare fișier în folderul lui.",
       "cosuri": [{"t": "data/", "d": "datele"}, {"t": "notebooks/", "d": "caietele"},
                  {"t": "code/", "d": "fișierele .py"}, {"t": "proiect-dsw/", "d": "direct în rădăcină"}],
       "elemente": [{"t": "country.csv", "cos": 0}, {"t": "migratie_2024.json", "cos": 0},
                    {"t": "01_introducere.ipynb", "cos": 1}, {"t": "explorare.ipynb", "cos": 1},
                    {"t": "descarca_migratie.py", "cos": 2}, {"t": "curatare.py", "cos": 2},
                    {"t": "requirements.txt", "cos": 3}, {"t": "README.md", "cos": 3}],
       "laBine": "Fiecare lucru la locul lui.",
       "laRau": "Ce descrie tot proiectul stă în rădăcină."})
   + nota("Datele",
          'Fișierul <code>country.csv</code> se ia de pe '
          '<a class="leg" href="https://data.humdata.org/dataset/social-connectedness-index" '
          'target="_blank" rel="noopener">HDX</a>, 0,6 MB. Îl pui în '
          "<code>data/</code> și nu îl mai modifici niciodată."))


sl("s18s", "Proiectul tău", "Unde pui fiecare fișier",
   "<h2>Unde pui fiecare fișier?</h2>"
   + ix("sortare", "Unde pui fiecare fișier?", {
       "id": "c1-folder",
       "sarcina": "Trage fiecare fișier în folderul lui. În <code>.venv</code> nu pui nimic.",
       "cosuri": [{"t": "data/", "d": "datele"}, {"t": "notebooks/", "d": "caietele"},
                  {"t": "code/", "d": "fișierele .py"}, {"t": "proiect-dsw/", "d": "direct în rădăcină"}],
       "elemente": [{"t": "country.csv", "cos": 0}, {"t": "migratie_2024.json", "cos": 0},
                    {"t": "01_introducere.ipynb", "cos": 1}, {"t": "explorare.ipynb", "cos": 1},
                    {"t": "descarca_migratie.py", "cos": 2}, {"t": "curatare.py", "cos": 2},
                    {"t": "requirements.txt", "cos": 3}, {"t": "README.md", "cos": 3}],
       "laBine": "Fiecare lucru la locul lui. Peste o lună, oricine din echipă găsește orice.",
       "laRau": "Datele, caietele și codul au fiecare folderul lor; ce descrie tot proiectul stă în rădăcină.",
       "explicatie": "<code>requirements.txt</code> și <code>README.md</code> descriu tot proiectul, deci stau "
                     "în rădăcină, unde le caută și GitHub, și colegii."}),
   manual="")


sl("s19", "Mai departe", "Ce urmează la cursul 2",
   "<h2>La cursul 2: datele vin prin API</h2>"
   '<div class="urm__flux"><span>codul tău</span><i>→ cerere →</i><span>API-ul Eurostat</span>'
   "<i>→ răspuns JSON →</i><span>tabel pandas</span><i>→</i><span>data/</span></div>"
   '<div class="urm">'
   "<div><b>Ce e un API</b><p>Cum citești documentația, ce e un endpoint, ce înseamnă codurile de stare.</p></div>"
   "<div><b>Prima cerere</b><p>Cu <code>requests</code>, din cod: parametrii, paginarea, din JSON în tabel.</p></div>"
   "<div><b>Cubul Eurostat</b><p>Răspunsul JSON-stat, desfăcut într-un tabel obișnuit.</p></div>"
   "<div><b>Migrația, adusă de voi</b><p>Câți cetățeni ai fiecărei țări trăiesc în fiecare altă țară.</p></div>"
   "</div>"
   "<h3>Până atunci</h3>"
   "<ol>"
   "<li><strong>Mediul de lucru</strong>: folderul proiectului, <code>.venv</code> cu pandas, și caietul 01 rulat "
   "de sus până jos (<em>Restart Kernel → Run All</em>).</li>"
   "<li><strong>Echipa de cinci</strong>, formată. Direcția proiectului o alegem la cursul 3.</li>"
   '<li><strong>Contul GitHub</strong>, cu care intri pe <a class="leg" href="../../cont/">site</a>.</li>'
   "</ol>"
   + '<div class="grila grila--2" style="margin-top:22px">'
   '<a class="resursa" href="../"><span class="resursa__ic">→</span>'
   '<span class="resursa__txt"><span class="resursa__t">Pagina cursului 1</span>'
   '<span class="resursa__d">Materiale și legături</span></span></a>'
   '<a class="resursa" href="../../c2-colectarea-prin-api/"><span class="resursa__ic">→</span>'
   '<span class="resursa__txt"><span class="resursa__t">Cursul 2</span>'
   '<span class="resursa__d">Colectarea datelor prin API</span></span></a></div>')


L.scrie_tot()
