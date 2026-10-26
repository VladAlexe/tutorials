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
from comun import Lectie, ix, verif, tabel, nota, surse, REPO, REPO_ZIP, REPO_FOLDER, repo_fisier


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
        {"nume": "user_country", "tip": "str",
         "d": "codul de două litere al primei țări din pereche"},
        {"nume": "friend_country", "tip": "str",
         "d": "codul celei de-a doua țări din pereche"},
        {"nume": "user_region", "tip": "str",
         "d": "la nivel de țară, același cod ca user_country; în fișierele NUTS e codul regiunii"},
        {"nume": "friend_region", "tip": "str",
         "d": "la fel, pentru celălalt capăt al perechii"},
        {"nume": "scaled_sci", "tip": "int64",
         "d": "indicele, scalat; se compară între perechi, nu se citește ca număr de prietenii"},
    ],
    "cap": [
        ["RO", "RO", "RO", "RO", 6252768],
        ["RO", "MD", "RO", "MD", 173794],
        ["RO", "AT", "RO", "AT", 124693],
    ],
    "capNota": "Trei rânduri reale din fișier, cu România pe primul capăt al perechii. "
               "La nivel de țară, coloanele de regiune repetă codul țării; există pentru ca "
               "fișierul să aibă aceeași structură ca fișierele pe regiuni.",
}

DATE_SCI_SIMPLU = dict(DATE_SCI, simplu=True, capNota="")



# ===========================================================================
#  1-2. Cursul
# ===========================================================================

TEME = [
    (1, "Introducere și instalarea softurilor",
     "Ce unelte folosim și de ce fiecare. Mediul de lucru, structura unui proiect."),
    (1, "Concepte-cheie pentru analiza datelor",
     "Tipuri de date în Python, în SQL și în fișiere spațiale. Tipuri de fișiere. Formatul JSON."),
    (2, "Colectarea datelor prin API",
     "Ce e un API, cum se citește o documentație, cum se face o cerere din cod."),
    (3, "Versionare și colaborare cu Git",
     "Istoric, reveniri, ramuri, pull request. Cum lucrează o echipă pe același cod fără să își suprascrie munca."),
    (4, "Explorarea preliminară și curățarea",
     "Lipsuri, duplicate, tipuri greșite, coduri care nu se potrivesc între surse."),
    (5, "Baze de date",
     "Tabele, chei, interogări SQL. De ce 1,8 milioane de perechi de regiuni se interoghează mai bine dintr-o bază de date decât dintr-un fișier."),
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
     "lab": "Primul caiet rulat pe date reale: country.csv, România și partenerii ei.",
     "proiect": "Folderul cursului, dsw, cu mediul de lucru configurat. Echipele se formează până la cursul 2.",
     "unelte": ["VS Code", "Python", "mediu virtual", "Jupyter", "pandas"]},
    {"c": 2, "scurt": "API", "titlu": "Colectarea datelor prin API", "etapa": "colectare",
     "invata": ["ce e un API REST și cum se citește documentația", "cererea, parametrii, paginarea, codurile de stare",
                "cum devine un răspuns JSON un tabel", "cubul JSON-stat de la Eurostat"],
     "caiet": "02_colectarea_datelor_prin_api.ipynb",
     "lab": "De la prima cerere la indicatorii Băncii Mondiale și migrația de la Eurostat, salvate în curs/data/c2.",
     "proiect": "Depozitul echipei, clonat în dsw/proiect, și primele date, aduse din cod.",
     "unelte": ["requests", "API Banca Mondială", "API Eurostat", "JSON"]},
    {"c": 3, "scurt": "Git", "titlu": "Versionare și colaborare cu Git", "etapa": "colectare",
     "invata": ["cele trei zone ale Git și commit-ul", "GitHub, ramuri, pull request, conflicte",
                "cum se caută literatura pe teorie și pe metodă", "cum se scrie o întrebare de cercetare"],
     "caiet": "03_surse_diverse_si_preprocesare.ipynb",
     "lab": "Nomenclatorul regiunilor, tabelul regional, migrația fără grupuri de țări; apoi Git.",
     "proiect": "Direcția proiectului, întrebarea voastră și primele commit-uri în depozitul echipei.",
     "unelte": ["Git", "GitHub", "pandas"]},
    {"c": 4, "scurt": "Curățare", "titlu": "Curățarea datelor", "etapa": "curatare",
     "invata": ["cele șase etape ale curățării", "lipsuri, duplicate, valori extreme, coduri care nu se potrivesc între surse",
                "formatul lung și formatul lat", "dicționarul de date"],
     "caiet": "04_curatarea_si_integrarea_datelor.ipynb",
     "lab": "Calitatea și acoperirea datelor, capcanele codurilor de țară, secțiunile 1-3 și 6-7.",
     "proiect": "Datele curățate, cu dicționarul lor, în depozit.",
     "unelte": ["pandas", "Git"]},
    {"c": 5, "scurt": "Agregare și SQL", "titlu": "Agregare și baze de date", "etapa": "agregare",
     "invata": ["îmbinarea tabelelor și tipurile de join", "unitatea de analiză și agregarea",
                "două îmbinări la date diadice", "SQL, la nivelul necesar proiectului"],
     "caiet": "04_curatarea_si_integrarea_datelor.ipynb",
     "lab": "Tabelul lat al regiunilor, perechile și îmbinările, secțiunile 4-5 și 8.",
     "proiect": "Tabelul final, la unitatea de analiză aleasă de echipă.",
     "unelte": ["pandas", "SQL", "PostgreSQL"]},
    {"c": 6, "scurt": "Explorare", "titlu": "Analiza exploratorie", "etapa": "explorare",
     "invata": ["distribuții cu coadă lungă și clasamente", "norul de puncte și corelațiile",
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
                "ce se poate afirma pe baza rezultatelor", "cum se prezintă un proiect"],
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
    "intro": "Unsprezece subiecte, opt ședințe. Fiecare ședință adaugă o piesă la proiectul echipei.",
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
    "intro": "Aceleași tipuri ca în partea 2 a caietului. Rulează rând cu rând: în stânga, codul; în dreapta, valorile din memorie și ce se afișează.",
    "cod": "tara = \"RO\"\nnumar_tari = 178\nore_de_studiu = 8.5\neste_student = True\nocupatie = None\n\n"
           "print(type(tara))\nprint(type(numar_tari))\nprint(type(ore_de_studiu))\nprint(type(este_student))\nprint(type(ocupatie))",
    "pasi": [
        {"l": 1, "set": {"tara": {"t": "str", "v": "RO"}},
         "txt": "<code>=</code> pune o valoare sub un nume. Ghilimelele fac din RO un <b>text</b> (<code>str</code>): un cod de țară e text, chiar dacă identifică ceva."},
        {"l": 2, "set": {"numar_tari": {"t": "int", "v": 178}},
         "txt": "Fără ghilimele, 178 e un <b>număr întreg</b> (<code>int</code>). Cu el se pot face calcule."},
        {"l": 3, "set": {"ore_de_studiu": {"t": "float", "v": 8.5}},
         "txt": "Cu punct zecimal: <code>float</code>. În Python zecimalele se scriu cu punct, nu cu virgulă."},
        {"l": 4, "set": {"este_student": {"t": "bool", "v": True}},
         "txt": "<code>True</code> și <code>False</code>, cu majusculă: valori logice (<code>bool</code>). Orice comparație dă una dintre ele."},
        {"l": 5, "set": {"ocupatie": {"t": "NoneType", "v": None}},
         "txt": "<code>None</code> înseamnă „lipsește”. Nu e zero și nu e text gol: e absența valorii."},
        {"l": 7, "out": "<class 'str'>",
         "txt": "<code>type()</code> spune ce fel de valoare e sub un nume. Este primul lucru de verificat când rezultatul diferă de cel așteptat."},
        {"l": 8, "out": "<class 'int'>", "txt": "178 e întreg."},
        {"l": 9, "out": "<class 'float'>", "txt": "8.5 are zecimale."},
        {"l": 10, "out": "<class 'bool'>", "txt": "True e o valoare logică."},
        {"l": 11, "out": "<class 'NoneType'>",
         "txt": "Și lipsa are un tip. Acestea sunt cele cinci tipuri simple folosite la curs."},
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
         "txt": "<code>.keys()</code> arată cheile. Este primul pas în explorarea unui dicționar necunoscut."},
        {"l": 7, "out": "Cluj-Napoca", "hl": {"var": "persoana", "k": "city"},
         "txt": "<code>persoana[\"city\"]</code> cere valoarea cheii <code>city</code>. Listă: <b>poziție</b>. Dicționar: <b>cheie</b>. Cu aceste două operații se citește orice JSON."},
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
    "intro": "Fișierul real, country.csv. Aceleași idei, pe un tabel: întâi se verifică dimensiunea, apoi se păstrează doar rândurile relevante.",
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
         "txt": "<code>==</code> compară (un singur <code>=</code> atribuie). Comparația se face pe fiecare rând și dă o coloană de True și False."},
        {"l": 6, "set": {"ro": {"t": "DataFrame", "v": {
            "cols": ["user_country", "friend_country", "scaled_sci"],
            "rows": [["RO", "CI", 640], ["RO", "ES", 54179], ["RO", "MW", 205]],
            "nota": "178 de rânduri"}}},
         "txt": "<code>sci[conditie_ro]</code> păstrează doar rândurile unde condiția e True: perechile care pleacă din România."},
        {"l": 7, "out": "178", "txt": "178 de rânduri: România cu fiecare țară, inclusiv perechea RO-RO."},
        {"l": 9, "set": {"ro_extern": {"t": "DataFrame", "v": {
            "cols": ["user_country", "friend_country", "scaled_sci"],
            "rows": [["RO", "CI", 640], ["RO", "ES", 54179], ["RO", "MW", 205]],
            "nota": "177 de rânduri, fără perechea RO-RO"}}},
         "txt": "<code>!=</code> înseamnă „diferit de”. Scoatem perechea România-România: păstrăm doar partenerii externi."},
        {"l": 10, "out": "177", "txt": "177 de parteneri externi."},
        {"l": 12, "set": {"top_ro": {"t": "DataFrame", "v": {
            "cols": ["friend_country", "scaled_sci"],
            "rows": [["MD", 173794], ["AT", 124693], ["DE", 91228]],
            "nota": "aceleași 177 de rânduri, în ordinea descrescătoare a indicelui"}}},
         "txt": "<code>sort_values</code> ordonează după o coloană; <code>ascending=False</code> pune valorile mari primele."},
        {"l": 13, "out": "['MD', 'AT', 'DE', 'HU', 'IE', 'IT']",
         "txt": "Primii șase parteneri. Italia, cu cei mai mulți români, este abia a șasea: întrebarea la care revenim pe tot parcursul semestrului."},
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
       "laBine": "Indice pentru liste, cheie pentru dicționare: cu aceste două operații se parcurge orice JSON.",
       "explicatie": "<code>tari[1]</code> e al doilea element, pentru că primul e <code>tari[0]</code>. "
                     "<code>persoana[\"city\"]</code> dă valoarea cheii. Cu aceste două operații "
                     "se ajunge la orice valoare dintr-un răspuns JSON, oricât de adânc ar fi imbricată."})

DIADIC_SLIDE = ix("cod", "Filtrare pe primul capăt al perechii", {
       "id": "c1-cod-diadic", "fisier": "diadic.py", "date": DATE_SCI_SIMPLU,
       "sarcina": "Păstrează doar perechile în care primul capăt e România.",
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
       "explicatie": "Fixezi un capăt al perechii și obții un tabel monadic: "
                     "178 de rânduri, câte unul pentru fiecare țară parteneră. "
                     "Este operația de bază pentru a citi date diadice."})

DIADIC_MANUAL = ix("cod", "Filtrare pe primul capăt al perechii", {
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
       "explicatie": "Fixezi un capăt al perechii și obții un tabel monadic: un rând "
                     "pentru fiecare țară parteneră."})


import json as _json, pathlib as _pl
_EXPL = _json.loads((_pl.Path(__file__).resolve().parent.parent / "date" / "explorator.json").read_text(encoding="utf-8"))
ROMANI = _EXPL["migratie"]["RO"]
RAPORT = _EXPL["raportoare"]

sl("s1", "Cursul", "Despre curs",
   "<h2>Fluxuri de lucru pentru știința datelor</h2>"
   "<p class=\"cheie\">Un flux complet, de la întrebarea de cercetare la un "
   "rezultat verificabil.</p>"
   + ix("semestru", "Opt ședințe", CRONOLOGIE),
   manual=
   "<h2>Fluxuri de lucru pentru știința datelor</h2>"
   "<p>Cursul urmărește drumul complet al unui proiect de analiză de date, de la "
   "formularea întrebării până la un raport pe care alți cercetători îl pot citi, "
   "reproduce și evalua. Nu este un curs de statistică și nici unul de programare: "
   "tema lui este felul în care cele două se leagă într-un proces de lucru "
   "reproductibil, care funcționează în echipă, nu doar pe un singur calculator.</p>"
   "<p>Materia are unsprezece subiecte, distribuite pe opt ședințe. Fiecare ședință "
   "adaugă o componentă la proiectul echipei, iar la final proiectul se predă ca "
   "depozit de cod pe GitHub, cu istoricul lui, nu ca fișier izolat. Pe site, ședințele "
   "sunt numerotate „cursul 1” până la „cursul 8”; fiecare are o parte de curs, cu lecția "
   "și manualul de pe site, și un laborator, cu caietul ei.</p>"
   "<p>Pe tot parcursul semestrului lucrăm la aceeași întrebare, ca într-o cercetare "
   "reală: cât de conectate sunt regiunile Europei prin prieteniile de pe Facebook și "
   "în ce măsură aceste legături se explică prin migrația dintre ele. Analiza completă "
   "a profesorului devine un articol; fiecare echipă dezvoltă, pe aceleași date, o "
   "întrebare proprie.</p>"
   + ix("semestru", "Subiectele semestrului", CRONOLOGIE)
   + nota("Caietul lecției",
          f'<a class="leg" href="{repo_fisier("curs/01_introducere_si_datele_proiectului.ipynb")}" '
          'target="_blank" rel="noopener"><code>01_introducere_si_datele_proiectului.ipynb</code></a>, '
          "în <code>dsw/curs/</code>. Un caiet (notebook Jupyter, <code>.ipynb</code>) reunește "
          "text, cod și rezultatele codului într-un singur document.", True)
   + "<h3>Ordinea primei ore</h3>"
   "<ol><li>Evaluarea cunoștințelor și a așteptărilor</li>"
   "<li>Uneltele semestrului</li>"
   "<li>Pașii unui proiect de analiză de date</li>"
   "<li>Proiectul: SCI, migrația, echipele și notarea</li>"
   "<li>Datele proiectului și forma lor</li>"
   "<li>Tipuri de date în Python, în SQL și spațiale; tipuri de fișiere</li>"
   "<li>Liste, dicționare și formatul JSON</li>"
   "<li>Primul contact cu SCI</li>"
   "<li>Mediul virtual și folderul cursului</li></ol>"
   "<p>La laborator, aceleași idei se lucrează în caietul 01, în șase părți: mediul de "
   "lucru, variabile și tipuri, fișiere și căi, citirea unui JSON, primul contact cu SCI "
   "și exerciții pe cont propriu. Fiecare pas urmează aceeași succesiune: citirea codului, "
   "anticiparea rezultatului, rularea și interpretarea.</p>"
   + nota("La finalul orei", "Folderul cursului, <code>dsw</code>, are mediul virtual "
          "creat, iar caietul 01 rulează de sus până jos, pe date reale. Echipa se "
          "formează până la cursul 2."))


sl("s2", "Cursul", "Punctul de pornire",
   "<h2>Punctul de pornire</h2>"
   + ix("autoevaluare", "Autoevaluare, fără notă", {
       "id": "c1-autoevaluare",
       "teme": [
           {"cheie": "python", "t": "Python", "d": "variabile, liste, dicționare, funcții"},
           {"cheie": "linie", "t": "Linia de comandă", "d": "terminal, cd, rularea unui script"},
           {"cheie": "git", "t": "Git și GitHub", "d": "commit, branch, lucru în echipă"},
           {"cheie": "sql", "t": "SQL", "d": "SELECT, JOIN, tabele"},
           {"cheie": "api", "t": "API-uri", "d": "a cere date unui serviciu, prin cod"},
           {"cheie": "stat", "t": "Statistică", "d": "distribuții, corelație, regresie"},
       ]}),
   manual=
   "<h2>Punctul de pornire</h2>"
   "<p>Cursul presupune experiență anterioară cu Python, dar experiența cu linia de "
   "comandă, Git, SQL și API-urile diferă de la un student la altul. Evaluarea de mai jos "
   "nu intră în notă. Ea stabilește punctul de pornire al grupei, pentru ca timpul de "
   "curs să meargă acolo unde este nevoie de el.</p>"
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
   + "<h3>Așteptările</h3>"
   "<p>A doua parte a evaluării privește așteptările, iar răspunsurile schimbă "
   "accentele cursului. Dacă o parte importantă a grupei urmărește în primul rând "
   "colectarea datelor din surse publice, mai mult timp va fi alocat API-urilor; dacă mulți "
   "își scriu deja disertația, accentul cade pe formularea întrebării "
   "și pe raport.</p>"
   + ix("asteptari", "Ce aștepți de la curs", {
       "id": "c1-asteptari",
       "sarcina": "Două-trei rânduri. Răspunsurile sunt citite înainte de cursul următor.",
       "exemplu": "De exemplu: vreau să pot colecta singur date de pe un site și "
                  "să le integrez într-un singur tabel."}))


# ===========================================================================
#  3. Softuri și conturi
# ===========================================================================

UNELTE = [
    # (grupa, nume cu link, la ce, când)
    ("Pe calculatorul tău", [
        ('<a class="leg" href="https://code.visualstudio.com/" target="_blank" rel="noopener">Visual Studio Code</a>',
         "editorul: caiete și fișiere de cod, în același loc", "azi"),
        ('<a class="leg" href="https://marketplace.visualstudio.com/items?itemName=ms-python.python" target="_blank" rel="noopener">extensiile Python și Jupyter</a>',
         "rulează caietele direct în VS Code; "
         '<a class="leg" href="../scurtaturi/">comenzile rapide din caiet</a>', "azi"),
        ('<a class="leg" href="https://www.python.org/downloads/" target="_blank" rel="noopener">Python 3.11+</a>',
         "limbajul; pe Windows bifezi <em>Add Python to PATH</em>", "azi"),
        ('<a class="leg" href="https://docs.python.org/3/library/venv.html" target="_blank" rel="noopener">mediul virtual (venv)</a>',
         "pachetele proiectului, separate de restul calculatorului", "azi"),
        ('<a class="leg" href="https://git-scm.com/downloads" target="_blank" rel="noopener">Git</a>',
         "depozitul echipei, adus pe calculator; istoricul lui", "cursul 2"),
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



sl("s2b", "Cursul", "Așteptările",
   "<h2>Ce aștepți de la curs</h2>"
   + ix("asteptari", "Așteptările", {
       "id": "c1-asteptari",
       "sarcina": "Două-trei rânduri. Răspunsurile sunt citite înainte de cursul "
                  "următor, iar cursul se ajustează în funcție de ele.",
       "exemplu": "De exemplu: vreau să pot colecta singur date de pe un site și "
                  "să le integrez într-un singur tabel."}),
   manual="")

sl("s3", "Softuri și conturi", "Uneltele semestrului",
   "<h2>Uneltele semestrului</h2>"
   "<p class=\"cheie\">Toate gratuite. Azi instalezi doar coloana din stânga.</p>"
   + unelte_slide()
   + nota("Contul GitHub", "Creat înainte de curs, după pașii de pe "
          '<a class="leg" href="../">pagina cursului</a>. Cu el intri pe site și, de la cursul 2, '
          "în depozitul echipei.", True),
   manual=
   "<h2>Uneltele semestrului</h2>"
   "<p>Toate uneltele sunt gratuite; Teams se folosește prin contul instituțional. Astăzi "
   "se instalează editorul și Python și se creează mediul virtual. Celelalte intră în lecția în care devin "
   "necesare, iar pachetele Python se instalează în mediul virtual al cursului, nu în "
   "Python-ul calculatorului.</p>"
   + unelte_html()
   + "<h3>Caiete și fișiere de cod</h3>"
   "<p>Caietul (<code>.ipynb</code>) este potrivit pentru explorare: se rulează o celulă, se "
   "examinează rezultatul, se decide pasul următor. Fișierul <code>.py</code> este potrivit pentru ce se "
   "rulează din nou, identic, de fiecare dată: descărcarea datelor, curățarea, construirea "
   "tabelului final. Un proiect de date folosește ambele forme, iar VS Code le deschide în "
   "același mediu de lucru.</p>"
   "<h3>De ce un mediu virtual</h3>"
   "<p>Fiecare proiect are pachetele lui, în versiunile lui. Mediul virtual le izolează de "
   "restul calculatorului, astfel încât proiectul echipei să ruleze cu aceleași pachete pe "
   "toate cele cinci calculatoare. Când versiunile sunt fixate în <code>requirements.txt</code> "
   "(de exemplu <code>pandas==3.1.0</code>), mediul se poate reface identic și peste un an.</p>"
   + nota("Contul GitHub", "Se creează înainte de prima oră, după pașii de pe "
          '<a class="leg" href="../">pagina cursului</a>. La prima oră intri cu el pe site și '
          "îți alegi numele din lista grupei, o singură dată. De la cursul 2, același cont îți "
          "dă acces la depozitul echipei.")
   + nota("Ce se salvează despre tine",
          "Răspunsurile la întrebări, exercițiile rezolvate și prezența la orele de curs. Detaliile sunt în "
          '<a class="leg" href="../../date-personale/">politica de confidențialitate</a>.'))


# ===========================================================================
#  4. Pașii unui proiect
# ===========================================================================

DRUM = {
    "titlu": "Apasă pe o etapă",
    "intro": "Sus, etapele analizei datelor; jos, ingineria modelelor. Baza de date e "
             "figurată separat: nu este o etapă, ci locul la care revin toate celelalte.",
    "bandaSus": "Analiza datelor", "bandaJos": "Ingineria modelelor",
    "sus": [
        {"n": "Definirea problemei", "unde": "cursurile 1 și 3", "et": "pregatire",
         "d": "Tema, unitatea de analiză, întrebarea. Aici se decide ce înseamnă un rând în "
              "tabelul final: o țară, o pereche de județe, un an. Toate etapele următoare "
              "depind de această alegere.",
         "noi": "Cât de conectate sunt regiunile Europei și în ce măsură migrația explică aceste "
                "legături. Fiecare echipă alege o parte din întrebare.",
         "lit": "Teoria: de ce ar fi conectate două locuri. Ce se știe deja despre SCI și "
                "despre migrație și ce a rămas neexplicat.",
         "capcana": "O unitate de analiză nedefinită: țări amestecate cu județe, care nu mai "
                    "pot fi comparate."},
        {"n": "Colectarea datelor", "unde": "cursul 2", "et": "colectare",
         "d": "Datele se aduc prin API sau din fișiere. Varianta brută se salvează întotdeauna "
              "nemodificată, pentru a putea reveni la ea când se descoperă o eroare.",
         "noi": "SCI de pe HDX; indicatorii de țară și migrația, prin API, de la Banca "
                "Mondială și de la Eurostat.",
         "lit": "Documentația API-ului și nota metodologică a datelor: ce măsoară, cum, "
                "și ce lipsește.",
         "capcana": "Lucrul direct pe fișierul descărcat: după prima eroare, nu mai există "
                    "o versiune de la care analiza să fie reluată."},
        {"n": "Curățarea datelor", "unde": "cursul 4", "et": "curatare",
         "d": "Tipuri greșite, valori lipsă, duplicate, coduri care nu se potrivesc între "
              "surse. Este etapa cea mai lungă și cea de care depinde validitatea rezultatului.",
         "noi": "Grecia e EL la Eurostat și GR în SCI; Namibia (NA) devine valoare lipsă; "
                "migrația vine cu grupuri de țări amestecate printre țări.",
         "lit": "Documentația surselor: ce înseamnă fiecare cod și fiecare lipsă.",
         "capcana": "Eliminarea rândurilor cu valori lipsă, care modifică eșantionul fără ca "
                    "schimbarea să fie observată."},
        {"n": "Analiza exploratorie", "unde": "cursul 6", "et": "explorare",
         "d": "Datele se examinează înainte de modelare. Scopul nu este demonstrarea unei "
              "ipoteze, ci înțelegerea datelor.",
         "noi": "Coada lungă a SCI, distanța, granița, comunitățile de județe pe hartă.",
         "lit": "Tiparele raportate în studiile anterioare: ce merită căutat și ce ar fi neașteptat.",
         "capcana": "Căutarea selectivă a tiparelor care confirmă așteptările inițiale."}],
    "jos": [
        {"n": "Feature engineering", "unde": "cursul 7", "et": "model",
         "d": "Se construiesc variabilele care răspund la întrebare: rate, ponderi, "
              "distanțe, diferențe între capetele perechii.",
         "noi": "Distanța, migranții la mie de locuitori, granița comună.",
         "lit": "Metoda: cum au construit alți autori variabilele și de ce.",
         "capcana": "Folosirea numărului absolut acolo unde relevantă este rata."},
        {"n": "Modelare", "unde": "cursul 7", "et": "model",
         "d": "Relația observată se testează formal. Un model simplu, bine interpretat, este "
              "preferabil unuia complex, care nu poate fi explicat.",
         "noi": "Patru modele pe logaritmi, fiecare cu o variabilă în plus.",
         "lit": "Metoda: modelele gravitaționale și erorile standard la date diadice.",
         "capcana": "Erori standard prea mici: același loc apare în sute de perechi, deci "
                    "observațiile nu sunt independente."},
        {"n": "Implementare", "unde": "dincolo de curs", "et": "model",
         "d": "Modelul este pus la dispoziția altor utilizatori: o aplicație, un raport "
              "care se actualizează automat.",
         "noi": "Fluxul se oprește la un depozit pe care oricine îl poate rula de "
                "la zero.",
         "lit": "Documentația uneltelor.",
         "capcana": "Cod care rulează doar pe calculatorul autorului."},
        {"n": "Optimizare", "unde": "dincolo de curs", "et": "model",
         "d": "Parametri, performanță, costuri. Zona de inginerie, nu de analiză.",
         "noi": "Nu intră în proiectul cursului.",
         "lit": "Documentația și literatura de inginerie.",
         "capcana": "Optimizarea unui model înainte de a verifica dacă răspunde la întrebare."}],
    "final": {"n": "Raportare și vizualizare", "unde": "cursul 8", "et": "raport",
              "d": "Rezultatul devine util abia când altcineva îl poate citi, reproduce și "
                   "critica. Graficele nu sunt decor: ele poartă argumentul.",
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
             "capcana": "Cinci versiuni ale aceluiași fișier, circulate prin mesaje."},
}

LITERATURA_FLUX = (
    "<div class=\"litf\">"
    "<p class=\"litf__t\">Literatura nu e o etapă și nici un capitol scris la final. E un fir "
    "care trece prin toată cercetarea, ca baza de date prin toate etapele.</p>"
    "<ol class=\"litf__pasi\">"
    "<li><b>Înainte de întrebare</b><span>ce se știe deja și unde este lacuna. O întrebare bună "
    "pornește de la o lacună în literatură, nu de la date.</span></li>"
    "<li><b>Teoria</b><span>de ce ar fi legate două locuri: sisteme migratorii, rețele "
    "sociale, distanță, granițe. Din ea ies ipotezele.</span></li>"
    "<li><b>Metoda</b><span>cum au măsurat alți autori, ce variabile au construit, ce modele au "
    "folosit, ce erori au evitat.</span></li>"
    "<li><b>Documentația</b><span>a datelor și a uneltelor, la fiecare pas de cod.</span></li>"
    "<li><b>După rezultate</b><span>rezultatele se raportează la literatură: ce confirmă, ce "
    "contrazice, ce e nou. Adesea, ele trimit înapoi la lectură.</span></li>"
    "</ol>"
    "<p class=\"litf__l\">Pentru fiecare etapă, schema de mai sus indică lecturile relevante. Lista "
    "întreagă, pe teorie, metodă și date: <a class=\"leg\" href=\"../../lecturi/\">Literatura "
    "proiectului</a>.</p></div>"
)

LIT2 = (
    '<div class="lit2"><p class="lit2__t">Literatura nu e o etapă și nici un capitol scris la final: '
    "e un fir care trece prin toată cercetarea.</p>"
    '<ol class="lit2__l">'
    '<li><span class="lit2__n">01</span><b>Înainte de întrebare</b><span>Ce se știe deja și unde este lacuna.</span></li>'
    '<li><span class="lit2__n">02</span><b>Teoria</b><span>De ce ar fi legate două locuri. De aici vin ipotezele.</span></li>'
    '<li><span class="lit2__n">03</span><b>Metoda</b><span>Cum au măsurat alți autori și ce modele au folosit.</span></li>'
    '<li><span class="lit2__n">04</span><b>Documentația</b><span>A datelor și a uneltelor, la fiecare pas de cod.</span></li>'
    '<li><span class="lit2__n">05</span><b>După rezultate</b><span>Ce confirmă, ce contrazice, ce e nou.</span></li>'
    "</ol>"
    '<p class="lit2__jos">Lista întreagă, pe teorie, metodă și date: '
    '<a class="leg" href="../../lecturi/">Literatura proiectului</a>.</p></div>')


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
       "intro": "Apasă pe o etapă. Săgețile pline marchează succesiunea etapelor; cele punctate, revenirile, care fac parte firească din proces."}

sl("s4", "Pașii unui proiect", "Data Science Workflow",
   "<h2>Pașii unui proiect de analiză de date</h2>"
   + ix("dsw", "Data Science Workflow", DSW),
   manual=
   "<h2>Pașii unui proiect de analiză de date</h2>"
   "<p>Schema are trei benzi. Prima, <strong>analiza datelor</strong>, acoperă etapele de "
   "sus, de la definirea problemei până la analiza exploratorie. A doua, <strong>ML "
   "engineering</strong>, acoperă implementarea și optimizarea modelului. A treia, "
   "<strong>știința datelor</strong>, le cuprinde pe toate, împreună cu construirea "
   "variabilelor, modelarea și baza de date care leagă etapele. Raportarea încheie drumul: "
   "un rezultat devine util abia când poate fi citit și verificat de altcineva.</p>"
   + ix("dsw", "Data Science Workflow", DSW)
   + "<p>Săgețile punctate marchează revenirile și descriu cel mai bine felul real de "
   "lucru. Dacă la curățare reiese că un indicator lipsește pentru jumătate dintre unități, "
   "se revine la colectare; dacă analiza exploratorie arată o relație neașteptată, se "
   "revine la definirea problemei. Revenirile nu sunt abateri de la metodă, ci fac "
   "parte din ea.</p>"
   + nota("Baza de date nu este o etapă",
          "Este locul în care etapele își depun rezultatele: datele brute, versiunea curățată, "
          "tabelul final. Într-o echipă, ea permite fiecărui membru să lucreze pe aceeași "
          "versiune a datelor, fără fișiere trimise de la unul la altul.")
   + "<h3>Unde intră literatura</h3>" + LIT2)


sl("s4l", "Pașii unui proiect", "Unde intră literatura",
   "<h2>Literatura, de-a lungul întregii cercetări</h2>"
   + LIT2,
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
    ("Coridoare de muncă", "România cu Italia sau Spania, Polonia cu Germania, Bulgaria cu Spania. Destinațiile migrației și legăturile păstrate cu locurile de origine."),
    ("Minorități și granițe vechi", "România cu Ungaria, Slovacia cu Ungaria, Austria cu Cehia. Legături care nu vin din migrația recentă."),
    ("Vecinii din est", "Republica Moldova și Ucraina: legături puternice, dar cu date de migrație puține. Ce se vede doar în SCI?"),
    ("Diaspora pe județe", "Ce județe sunt conectate cu ce regiuni din Italia, Spania sau Germania și de ce."),
    ("Orașe și bani", "Capitalele, centrele universitare și PIB-ul regional: care locuri au legături la distanță mare și care doar în proximitate."),
    ("O țară, pe regiuni", "O țară analizată pe regiuni: care dintre ele sunt conectate cu restul Europei și care nu."),
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
         "d": "Loc mic, deci cele 1.200 de legături au o pondere mare. "
              "Indicele este mare."},
        {"n": "Ungaria", "u": 4800,
         "d": "De opt ori mai mulți utilizatori. Aceleași legături, indice de "
              "opt ori mai mic."},
        {"n": "Italia", "u": 32000,
         "d": "Italia are cea mai mare comunitate de români în "
              "cifre absolute, dar numitorul este foarte mare, deci indicele este mic. "
              "<b>SCI nu măsoară mărimea diasporei.</b>"},
    ],
}
# fără „întâi ghicești”: formula se construiește întâi, nu se ghicește


SCI_IX = {"concluzie": "Italia are mai multe prietenii cu Clujul, <b>9 față de 6</b>, dar indicele e mai mic: "
                        "prieteniile se împart la mai multe perechi posibile. În <code>country.csv</code>: "
                        "România și Republica Moldova, 173.794; România și Italia, 69.327."}

sl("s5", "Proiectul", "Ce măsoară SCI",
   "<h2>Social Connectedness Index</h2>"
   "<p class=\"cheie\">Cât de probabilă e o prietenie pe Facebook între doi oameni, unul din fiecare loc.</p>"
   + ix("sci", "Aceleași calcule, două perechi de locuri", SCI_IX),
   sci=True,
   manual=
   "<h2>Social Connectedness Index</h2>"
   "<p>Indicele este produs de Data for Good at Meta din rețeaua de prietenii Facebook, "
   "agregată și anonimizată. Pentru fiecare pereche de locuri, el exprimă cât de probabil "
   "este ca doi utilizatori Facebook, câte unul din fiecare loc, să fie prieteni, "
   "<em>relativ</em> la celelalte perechi. Valorile sunt scalate: în fișier, cea mai mare "
   "este exact 1.000.000.000, iar cea mai mică 1. SCI nu este, așadar, o probabilitate "
   "între 0 și 1 și nu se interpretează izolat, ci prin comparație între perechi.</p>"
   "<p>Definiția, în cuvinte: numărul de prietenii dintre utilizatorii celor două locuri, "
   "împărțit la produsul numerelor de <em>utilizatori Facebook</em> din fiecare loc. "
   "Numitorul are două consecințe, la care revenim tot semestrul. Prima: un loc cu mulți "
   "utilizatori are nevoie de mult mai multe prietenii pentru același indice, deci o "
   "comunitate mare de migranți într-o țară mare are o pondere mică. A doua: indicele "
   "descrie utilizatorii platformei, nu populația, iar acoperirea Facebook diferă de la o "
   "țară la alta.</p>"
   + ix("sci", "Aceleași calcule, două perechi de locuri", SCI_IX)
   + "<h3>Ce nu este SCI</h3>"
   "<ul>"
   "<li><strong>Nu este un număr de prietenii.</strong> Valorile nu se adună și nu "
   "li se calculează direct media între perechi.</li>"
   "<li><strong>Nu este mărimea diasporei.</strong> Clasamentul partenerilor după SCI diferă "
   "de clasamentul după numărul de migranți: Italia are cei mai mulți cetățeni români, dar "
   "este abia al șaselea partener al României după SCI.</li>"
   "<li><strong>Nu acoperă toată populația.</strong> Baza sunt utilizatorii Facebook activi "
   "în cele 30 de zile dinainte de 25 ianuarie 2026, cu peste 20 de prieteni; locurile cu "
   "mai puțin de 500 de utilizatori lipsesc (Johnston et al., 2026). Acoperirea diferă "
   "în funcție de vârstă, mediul de rezidență și țară.</li>"
   "<li><strong>Nu se compară între fișiere.</strong> Fiecare fișier este scalat separat, de "
   "la 1 la 1.000.000.000: valorile din fișierul pe țări și cele din fișierul pe regiuni nu "
   "sunt direct comparabile.</li>"
   "<li><strong>Nu are direcție.</strong> Prefixele <code>user_</code> și <code>friend_</code> din numele coloanelor marchează cele "
   "două capete ale perechii, nu o direcție a migrației: valoarea pentru România și Ungaria "
   "este aceeași în ambele sensuri.</li>"
   "</ul>"
   "<p>Dintr-o valoare SCI se poate spune cât de conectați sunt, relativ, utilizatorii "
   "Facebook din două locuri. Nu se poate spune câți migranți trăiesc într-un loc sau de "
   "ce sunt legate locurile: pentru aceasta este nevoie de alte date, iar a doua sursă a cursului "
   "este migrația.</p>"
   + surse("Surse oficiale despre SCI", [
       ("Meta, Data for Good: SCI", "https://ai.meta.com/ai-for-good/datasets/social-connectedness-index/",
        "descrierea indicelui, pe scurt, de la producătorii lui"),
       ("HDX: fișierele SCI", "https://data.humdata.org/dataset/social-connectedness-index",
        "sursa fișierelor de date; nota metodologică este printre resurse"),
       ("Bailey et al. (2018), JEP", "https://www.aeaweb.org/articles?id=10.1257/jep.32.3.259",
        "articolul care a introdus indicele: definiția, ce îl explică, primele rezultate"),
   ])
   + nota("Instantaneul cu care lucrăm",
          "25 ianuarie 2026, 178 de țări, pe nomenclatorul NUTS 2024 și pe limitele administrative "
          "GADM 4.1 și geoBoundaries 6.0.0. Fiind un instantaneu, setul nu are dimensiune "
          "temporală și nu permite analize longitudinale. Harta pe județe, "
          "regiuni și țări este mai jos și în "
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
                 "românești. În afara țării: Ungaria și, mai neașteptat, cantonul elvețian Thurgau."},
        {"t": "Bihor", "nivel": "judete", "masura": "sci", "ales": "RO111",
         "text": "Peste graniță, Hajdú-Bihar, cealaltă jumătate a vechiului "
                 "comitat. Apoi Straubing, în Bavaria."},
        {"t": "Suceava", "nivel": "judete", "masura": "sci", "ales": "RO215",
         "text": "Primul partener din afara țării este Turnhout, în Belgia: o "
                 "legătură concentrată pe o singură destinație."},
        {"t": "Dolj", "nivel": "judete", "masura": "sci", "ales": "RO411",
         "text": "Districte agricole din nordul Germaniei, apoi Huelva, regiunea "
                 "căpșunilor din sudul Spaniei: o urmă probabilă a migrației sezoniere pentru muncă."},
    ],
}
HARTA_JUDETE["intai"] = {"q": "Clujul este conectat în primul rând cu județele vecine. În afara României, unde se află partenerii lui cel mai puternic conectați?", "variante": ["În Ungaria, peste graniță", "În nord-estul Spaniei", "În nordul Italiei"], "corect": 1, "dupa": "Lleida și Huesca, în Catalonia și Aragon: de 31 și de 20 de ori peste mediana partenerilor Clujului. Liniile portocalii indică partenerii cel mai puternic conectați din alte țări. Deschide harta mare (⤢) și alege alt județ."}

HARTA_TARI = {
    "niveluri": ["tari"], "nivel": "tari", "masura": "migr", "ales": "RO",
    "masuri": ["migr", "sci"],
    "povesti": [
        {"t": "Unde trăiesc românii", "nivel": "tari", "masura": "migr", "ales": "RO",
         "text": "Cetățeni români după țara în care locuiesc (Eurostat, 2024). "
                 "Italia e prima, cu 1,07 milioane, apoi Germania și Spania."},
        {"t": "Legăturile, după SCI", "nivel": "tari", "masura": "sci", "ales": "RO",
         "text": "Aceeași hartă, dar după SCI. Republica Moldova, Austria, Germania și "
                 "Ungaria trec în față. Italia coboară."},
        {"t": "Polonia", "nivel": "tari", "masura": "migr", "ales": "PL",
         "text": "Cei mai mulți polonezi trăiesc în Germania. După măsura "
                 "Legături (SCI), pe primul loc trece Islanda, o țară mică în care "
                 "polonezii sunt cea mai mare comunitate străină."},
    ],
}

sl("s5h", "Proiectul", "Harta, pe județe",
   "<h2>Legăturile unui județ, pe hartă</h2>"
   + ix("harta", "1.343 de regiuni NUTS 3 din toată Europa", HARTA_JUDETE),
   sci=True,
   manual=
   "<h2>Harta, pe județe</h2>"
   "<p>Harta arată unde duce analiza. Fiecare dintre cele 1.343 de regiuni NUTS 3 ale "
   "Europei (pentru România, județele) este colorată după cât de legată este de județul "
   "ales. Valoarea din listă este un raport: de câte ori este mai mare SCI-ul cu locul "
   "respectiv decât SCI-ul median al județului ales.</p>"
   + ix("harta", "1.343 de regiuni NUTS 3 din toată Europa", HARTA_JUDETE)
   + "<p>Două regularități se văd imediat. Prima: aproape toate legăturile foarte puternice "
   "sunt cu regiuni apropiate, din aceeași țară; distanța și granița de stat organizează cea mai mare "
   "parte a hărții. A doua: fiecare județ are și câteva legături îndepărtate neobișnuit de "
   "puternice, diferite chiar între județe vecine. Pentru Suceava, Belgia (Turnhout); pentru "
   "Cluj, nord-estul Spaniei (Lleida și Huesca); pentru Dolj, nordul Germaniei și Huelva.</p>"
   "<p>Aceste hărți seamănă cu hărțile migrației, dar nu sunt hărți ale migrației: SCI "
   "plasează utilizatorii după locul în care trăiesc, fără informații despre originea sau "
   "migrația lor. De aici întrebarea cursului: cât "
   "din aceste legături se explică prin oamenii care au migrat? Migrația este tema secțiunii "
   "următoare.</p>"
   + nota("De unde vine harta",
          "Din fișierul SCI pe regiuni NUTS 3, <code>nuts3_2024.csv</code>, publicat pe HDX, "
          "și din contururile NUTS 2024 de la Eurostat GISCO. Harta completă a Europei, pe "
          'toate nivelurile, este în <a class="leg" href="../../explorator/">Exploratorul '
          "legăturilor sociale</a>."))


sl("s5m", "Proiectul", "Oameni și legături",
   "<h2>Unde trăiesc românii și unde au legături</h2>"
   + ix("harta", "Migrația (Eurostat) și SCI, pe aceeași hartă", HARTA_TARI),
   sci=True,
   manual=
   "<h2>Oameni și legături</h2>"
   "<p>A doua sursă a cursului este migrația: câți cetățeni ai fiecărei țări trăiesc în "
   "fiecare altă țară. Datele vin tot prin API, de la Eurostat (<code>migr_pop1ctz</code>), "
   "și le aducem la cursul 2. Pe hartă, prima vizualizare arată unde trăiesc cetățenii români; "
   "a doua arată cât de legată este România de fiecare țară, după SCI.</p>"
   + ix("harta", "Migrația (Eurostat) și SCI, pe aceeași hartă", HARTA_TARI)
   + nota("Ce date de migrație avem",
          "Stocul de cetățeni străini la 1 ianuarie 2024, pentru țările care raportează "
          "populația pe țări de cetățenie. Printre cele care nu raportează: Polonia, Danemarca, "
          "Grecia, Croația, Cipru, Malta, Elveția, Regatul Unit și cele mai multe țări din afara "
          "UE (Republica Moldova, Ucraina, Serbia). Acolo harta rămâne gri: este o limită a datelor, nu o "
          "eroare."),
   dupa=verif("c1-v11", 2,
              "Pe ce loc este Italia printre partenerii României, după SCI?",
              ["primul", "al treilea", "al șaselea", "al doisprezecelea"],
              "Al șaselea, după Republica Moldova, Austria, Germania, Ungaria și Irlanda. "
              "La migrație este prima. Diferența dintre cele două clasamente e "
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
    note = {"IT": "Cei mai mulți români, dar o populație mare: după SCI, coboară.",
            "AT": "A cincea după număr, a doua la mie, prima după SCI.",
            "HU": "Puțini români, dar SCI mare: probabil minoritatea maghiară și granița, nu migrația recentă.",
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

def _nori():
    r = [{"cod": c, "nume": _SCI_RO[c]["nume"], "nr": v, "mie": round(v / POP_TARI[c] * 1000, 3),
          "sci": _SCI_RO[c]["sci"]} for c, v in ROMANI.items() if c in POP_TARI and c in _SCI_RO]
    return sorted(r, key=lambda x: -x["sci"])


NORI = {
    "randuri": _nori(), "etichete": ["IT", "AT", "HU", "DE", "FR"],
    "yEt": "SCI cu România, scară logaritmică",
    "paneluri": [
        {"k": "nr", "t": "față de numărul de români", "ax": "români care trăiesc în țară",
         "ticks": [100, 1000, 10000, 100000, 1000000]},
        {"k": "mie", "t": "față de românii la 1.000 de locuitori", "ax": "români la 1.000 de locuitori",
         "ticks": [0.1, 1, 10], "stanga": ["HU"]},
    ],
    "nota": "Un punct e o țară care raportează cetățeniile (23 de țări); ambele axe sunt logaritmice. "
            "Cu cât punctele sunt mai aproape de dreaptă, cu atât relația e mai strânsă: r e mai mare "
            "în graficul din dreapta. Ungaria se abate de la tipar: puțini români, legături puternice.",
}


sl("s5r", "Proiectul", "Migrația și SCI",
   "<h2>Legăturile urmează mai degrabă proporția decât numărul</h2>"
   + ix("doiNori", "SCI și migrația, în 23 de țări", NORI),
   sci=True,
   manual=
   "<h2>Legăturile urmează mai degrabă proporția decât numărul</h2>"
   "<p>Două grafice cu aceleași 23 de țări. În stânga, SCI cu România față de numărul de "
   "români care trăiesc în fiecare țară; în dreapta, față de numărul de români la 1.000 de "
   "locuitori. Ambele axe sunt logaritmice, pentru că valorile acoperă câteva ordine de "
   "mărime.</p>"
   + ix("doiNori", "SCI și migrația, în 23 de țări", NORI)
   + "<p>Pe valorile logaritmate, în cele 23 de țări care raportează cetățeniile, corelația cu SCI "
   "este 0,78 pentru numărul de români și 0,87 pentru românii la mie. Aceeași relație revine "
   "în modelul de la cursul 7, unde rata la mie explică mult mai mult decât numărul absolut. "
   "Explicația ține de numitorul indicelui: SCI împarte la utilizatorii din ambele locuri, "
   "deci o comunitate mare într-o țară mare are o pondere mică. Țările care rămân în afara "
   "tiparului, ca Ungaria, sunt întrebări de proiect.</p>"
   + nota("Calculul", "Românii din fiecare țară: Eurostat, <code>migr_pop1ctz</code>, 2024. "
          "Populația țărilor: suma populațiilor regiunilor NUTS 3, Eurostat, 2024. SCI: <code>country.csv</code>."))


ECHIPE = (
    '<ol class="ech">'
    "<li><span>cursurile 1 și 2</span><b>Formați echipa</b><p>Cinci membri. La cursul 2, echipa primește depozitul ei pe GitHub.</p></li>"
    "<li><span>cursul 3</span><b>Alegeți direcția</b><p>Întrebarea voastră și cadrul teoretic.</p></li>"
    "<li><span>cursurile 4-7</span><b>Construiți proiectul, treptat</b><p>Datele curate, tabelul final, explorarea, modelul: toate în depozit.</p></li>"
    "<li><span>cursul 8</span><b>Prezentați</b><p>Raportul și procesul care a dus la el.</p></li>"
    "</ol>"
    '<div class="ech__reguli">'
    "<p><b>Un depozit pe echipă.</b> Tot ce faceți stă pe GitHub, cu istoricul lui.</p>"
    "<p><b>Fiecare are partea lui.</b> Din istoric se vede cine ce a făcut.</p>"
    "<p><b>Nota este individuală.</b> Proiectul e al echipei, nota la proiect e a fiecăruia.</p>"
    "</div>")

ECH2 = (
    '<div class="ech2">'
    "<div><b>Cinci membri</b><span>aceleași date, întrebarea voastră</span></div>"
    '<div style="--c:var(--ambra)"><b>Un depozit</b><span>pe GitHub, cu istoricul fiecăruia</span></div>'
    '<div style="--c:var(--salvie)"><b>Notă individuală</b><span>proiectul e comun, nota e a fiecăruia</span></div>'
    "</div>"
    '<ol class="ech2t">'
    "<li><span>cursurile 1-2</span><b>Formați echipa</b></li>"
    "<li><span>cursul 3</span><b>Alegeți direcția</b></li>"
    "<li><span>cursurile 4-7</span><b>Construiți proiectul</b></li>"
    "<li><span>cursul 8</span><b>Prezentați</b></li>"
    "</ol>")


sl("s5b", "Proiectul", "Echipele",
   "<h2>Echipe de cinci, un depozit comun</h2>"
   + ECH2,
   manual=
   "<h2>Echipe de cinci, un depozit comun</h2>"
   "<p>Proiectul se face în echipe de cinci, pe aceleași date pentru toată grupa: SCI și "
   "migrația. Echipele diferă prin întrebare. Echipa se formează până la cursul 2, când "
   "primește depozitul ei pe GitHub; direcția proiectului se alege la cursul 3, după ce "
   "datele și literatura au fost discutate. Studenții fără echipă sunt repartizați.</p>"
   + ECHIPE
   + tabel(["Cursul", "Ce adaugi în depozit"], [
       ["~1, 2", "Echipa, depozitul ei, primele date"],
       ["~3", "Direcția, întrebarea, cadrul teoretic"],
       ["~4", "Seturile de date curățate și dicționarul de date"],
       ["~5", "Tabelul final, la unitatea de analiză aleasă"],
       ["~6", "Analiza exploratorie"],
       ["~7", "Variabilele derivate și modelul"],
       ["~8", "Raportul final și prezentarea"],
   ]))


DIRECTII2 = [
    ("Migrația și legăturile", [
        ("Număr sau proporție?", "SCI urmărește numărul de români dintr-o țară sau ponderea lor în populația ei?", "SCI · migrație · populație"),
        ("Coridoare comparate", "România și Italia, Polonia și Germania, Bulgaria și Spania: aceeași regulă peste tot?", "SCI · migrație"),
        ("Diaspora pe județe", "De ce e Clujul legat de Lleida, Suceava de Belgia, Doljul de Huelva?", "SCI județ-regiune"),
    ]),
    ("Istorie și granițe", [
        ("Granițele vechi", "Se mai vede granița Imperiului Habsburgic în legăturile dintre județe?", "SCI județe · granițe istorice"),
        ("Minoritățile", "Județele cu mulți vorbitori de maghiară sunt mai legate de Ungaria?", "SCI județ-țară · recensământ"),
        ("Vecinii din est", "Republica Moldova și Ucraina: legături puternice, fără date de migrație. Ce spune doar SCI?", "SCI"),
    ]),
    ("Distanță și geografie", [
        ("Cât contează distanța", "Cât de repede scad legăturile cu distanța și este ritmul același în toate țările?", "SCI · centroizi NUTS"),
        ("Granița de stat", "La aceeași distanță, regiunile de peste graniță sunt mai slab conectate decât cele din aceeași țară?", "SCI · contururi NUTS"),
        ("Munții", "Sunt Carpații o barieră pentru legăturile dintre județe?", "SCI județe · relief"),
    ]),
    ("Orașe, bani, rețele", [
        ("Orașele mari", "Capitalele și centrele universitare au legături la distanțe mai mari decât restul?", "SCI · populație"),
        ("Regiunile bogate", "Regiunile bogate sunt legate mai ales de alte regiuni bogate?", "SCI · PIB regional"),
        ("Comunitățile", "În câte „regiuni de prietenie” se împarte Europa și urmează ele granițele?", "SCI · rețele"),
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
   + "<p class=\"dir2__jos\">Sunt sugestii, nu o listă închisă. Direcția o alegeți la cursul 3, după ce vedeți datele și literatura.</p>",
   manual=
   "<h2>Direcții posibile</h2>"
   "<p>Toate direcțiile pornesc din aceleași fișiere, SCI și migrația, la care se adaugă, "
   "după întrebare, câteva surse de context. Sunt grupate după tipul întrebării și au trecute "
   "alături datele de care au nevoie. Sunt sugestii, nu o listă închisă: o întrebare proprie, "
   "bine argumentată, este binevenită.</p>"
   + directii_html()
   + "<p>Alte idei, împreună cu articolele din care provin, sunt pe pagina "
   '<a class="leg" href="../../lecturi/">Literatura proiectului</a>.</p>')


NOTA = (
    '<div class="nt">'
    '<div class="nt__c nt__c--p"><b>5</b><span>Proiectul</span><p>Depozitul echipei și raportul. Se evaluează procesul documentat în depozit. Nota este individuală.</p></div>'
    '<div class="nt__c"><b>3</b><span>Temele</span><p>Trei teme, încărcate pe Teams și notate de profesor.</p></div>'
    '<div class="nt__c"><b>2</b><span>Activitatea</span><p>Întrebările din lecții. Corect la oră: întreg. Corect acasă: jumătate.</p></div>'
    '<div class="nt__c"><b>1</b><span>Din oficiu</span><p>Se acordă de la început.</p></div>'
    "</div>"
    '<p class="nt__tot"><b>11 puncte</b> în total. Fiecare întrebare are două ocazii de răspuns, una la oră și una acasă; '
    "din fiecare contează primul răspuns, iar la notă intră rezultatul mai bun. Regulile complete sunt în contul tău.</p>")

NOTA2 = (
    '<div class="nt2">'
    "<div><b>5</b><span>Proiectul</span><p>Depozitul echipei și raportul. Se evaluează procesul documentat în depozit.</p></div>"
    "<div><b>3</b><span>Temele</span><p>Trei teme, pe Teams, notate de profesor.</p></div>"
    "<div><b>2</b><span>Activitatea</span><p>Întrebările din lecții, calculate de site.</p></div>"
    "<div><b>1</b><span>Din oficiu</span><p>Se acordă de la început.</p></div>"
    "</div>"
    '<div class="nt2a"><h4>Cum se calculează activitatea</h4>'
    '<div class="nt2a__f">'
    "<div><b>2 p</b><span>activitatea, în total</span></div><i>÷</i>"
    "<div><b>7</b><span>seminare</span></div><i>=</i>"
    "<div><b>0,29 p</b><span>pe seminar, împărțite<br>egal pe întrebări</span></div><i>→</i>"
    '<div class="ora"><b>întreg</b><span>răspuns corect la oră</span></div>'
    '<div class="acasa"><b>jumătate</b><span>răspuns corect acasă</span></div>'
    "</div>"
    '<p class="nt2a__r">Fiecare întrebare are două ocazii de răspuns, una la oră și una acasă; din fiecare '
    "contează primul răspuns, iar la notă intră rezultatul mai bun. <b>Prezența la curs contează "
    "prin activitate:</b> un răspuns corect dat în timpul orei valorează dublu față de unul dat acasă. "
    "11 puncte în total.</p></div>")


sl("s5n", "Proiectul", "Calculul notei",
   "<h2>Cum se calculează nota</h2>"
   + NOTA2,
   manual=
   "<h2>Cum se calculează nota</h2>"
   + NOTA2
   + "<p>Nota evaluează procesul, nu rezultatul: un rezultat nul, bine argumentat, primește "
   "aceeași notă ca unul pozitiv.</p>"
   + tabel(["Componentă", "Puncte", "Din ce se calculează"], [
       ["Proiect", "~5", "Depozitul echipei și raportul final. Se evaluează procesul documentat în "
                         "depozit, nu sensul rezultatului. Nota este individuală."],
       ["Teme", "~3", "Trei teme de seminar, încărcate pe Teams și notate de profesor. Nu au "
                      "legătură cu lecțiile de pe site."],
       ["Activitate", "~2", "Întrebările din lecții; cele 7 seminare valorează la fel. Fiecare "
                            "întrebare are două ocazii de răspuns, una la oră și una acasă, iar din fiecare "
                            "contează primul răspuns. Un răspuns corect la oră valorează întreg, "
                            "unul corect acasă jumătate; la notă intră rezultatul mai bun. "
                            "Exercițiile cu cod se punctează când sunt rezolvate, inclusiv cu indicii."],
       ["Din oficiu", "~1", "Se acordă de la început."],
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
    ["Acces la internet", "pentru a estima cine lipsește din date", "ANCOM"],
]

DATE_PROIECT = [
    ("Diadice", "un rând = o pereche de locuri", "dia", [
        ("SCI, țară cu țară", "country.csv", "178 × 178 = 31.684 de rânduri", "Meta, HDX"),
        ("SCI, regiune cu regiune", "nuts3_2024.csv", "1,8 milioane de rânduri", "Meta, HDX"),
        ("SCI, regiune cu țară", "nuts3_2024_to_country.csv", "245.770 de rânduri", "Meta, HDX"),
        ("Migrația", "migr_pop1ctz", "cetățenie × țară de rezidență", "Eurostat, API"),
    ]),
    ("Monadice", "un rând = un loc", "mon", [
        ("Populație", "demo_r_pjangrp3", "pe regiune NUTS 3, sex și vârstă", "Eurostat, API"),
        ("Densitate", "demo_r_d3dens", "pe regiune NUTS 3", "Eurostat, API"),
        ("PIB pe locuitor", "nama_10r_3gdp", "pe regiune NUTS 3", "Eurostat, API"),
        ("Indicatori de țară", "SP.POP.TOTL și altele", "pe țară", "Banca Mondială, API"),
        ("Recensământul 2021", "etnie, limbă, religie", "pe județ", "INS"),
    ]),
    ("Geografice", "un rând = o formă pe hartă", "geo", [
        ("Contururile NUTS 2024", "NUTS_RG_20M_2024_3035", "poligoane, în metri", "Eurostat GISCO"),
        ("Centroizii", "calculați din contururi", "puncte, pentru distanțe", "calcul propriu"),
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
   "<p>Un proiect de date nu începe cu toate sursele adunate, ci cu un nucleu la care se "
   "adaugă module, în funcție de întrebare. Nucleul nostru conține trei tipuri de date, iar "
   "forma lor decide cum se combină: datele <strong>diadice</strong> descriu perechi de "
   "locuri, cele <strong>monadice</strong> descriu un singur loc, iar cele "
   "<strong>geografice</strong> descriu forma locului pe hartă.</p>"
   + date_proiect_html()
   + nota("Fișierul care nu se poate reconstrui",
          "<code>nuts3_2024_to_country.csv</code> leagă fiecare regiune NUTS 3 de fiecare țară. "
          "Combinația nu există în celelalte fișiere și nu se poate obține din ele prin calcul: "
          "agregarea ar cere numărul de utilizatori din fiecare regiune, care nu este publicat.")
   + "<h3>Ce se adaugă mai târziu, după întrebare</h3>"
   + tabel(["Ce", "La ce ajută", "De unde"], SURSE_APOI)
   + nota("Reproductibilitatea",
          "API-ul Eurostat furnizează versiunea curentă a datelor, nu un istoric al versiunilor. "
          "De aceea se păstrează fișierul descărcat și data descărcării, nu doar codul care face "
          "cererea."))


def _diadic():
    d = _json.loads((_pl.Path(__file__).resolve().parent.parent / "date" / "sci-ro-nuts3.json").read_text(encoding="utf-8"))
    ix_ = {n: i for i, n in enumerate(d["judete"])}
    pop = {"Cluj": 693507, "Sălaj": 210656, "Bihor": 555957}
    nume = ["Cluj", "Sălaj", "Bihor"]
    return {"judete": [{"nume": n, "sigla": d["sigle"][ix_[n]], "pop": pop[n]} for n in nume],
            "matrice": [[d["matrice"][ix_[a]][ix_[b]] for b in nume] for a in nume]}


DIADIC = _diadic()

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
            "intro": "Treci cu mouse-ul peste un județ. Linia de separare nu urmează Carpații: Brașovul "
                     "e mai legat de București, iar Suceava și Botoșani, de Cluj."}


HARTA_RO = _harta_ro()

VEDERI_DIADIC = {"vederi": [
    {"t": "Perechi", "ix": "pereche", "date": DIADIC},
    {"t": "Hartă: Cluj sau București", "ix": "ro", "date": HARTA_RO,
     "text": "Pentru fiecare județ, două rânduri din tabelul de perechi: cu Clujul și cu Bucureștiul. Care e mai mare?"},
]}

sl("s8", "Datele proiectului", "Date diadice",
   "<h2>Date diadice: un rând e o pereche</h2>"
   + ix("vederi", "Trei județe, nouă perechi", VEDERI_DIADIC)
   + "<p class=\"dd__jos\">La 42 de județe, 1.764 de perechi; la cele 1.343 de regiuni ale Europei, "
   "1,8 milioane. De aici nevoia de cod și de bază de date.</p>",
   sci=True,
   manual=
   "<h2>Date diadice</h2>"
   "<p>Particularitatea datelor noastre influențează toate etapele care urmează, de aceea "
   "o fixăm de la început: un rând din fișierele SCI nu descrie un loc, ci relația dintre "
   "două locuri.</p>"
   + ix("vederi", "Trei județe, nouă perechi", VEDERI_DIADIC)
   + "<h3>Trei consecințe, la care revenim tot semestrul</h3>"
   "<ol><li><strong>Tabelul crește cu pătratul numărului de locuri.</strong> La cele 42 de "
   "unități NUTS 3 ale României (41 de județe și municipiul București) sunt 1.764 de perechi; la 1.343 de regiuni, 1,8 milioane. Un astfel de tabel nu "
   "se mai citește direct, ci se interoghează: de aici nevoia de cod și de bază de date.</li>"
   "<li><strong>Atributele se atașează de două ori.</strong> Populația locului de pe primul "
   "capăt și populația locului de pe al doilea sunt două coloane diferite, venite din același "
   "tabel sursă, prin două îmbinări.</li>"
   "<li><strong>Observațiile nu sunt independente.</strong> În tabelul județelor, Clujul apare "
   "în 83 dintre cele 1.764 de rânduri. Un model care presupune independența observațiilor "
   "subestimează erorile standard.</li></ol>"
   + nota("SCI și migrația, două tipuri de perechi",
          "SCI este simetric: valoarea pentru România și Italia este aceeași cu cea pentru "
          "Italia și România. Migrația are direcție: românii care trăiesc în Italia și italienii "
          "care trăiesc în România sunt două valori diferite.")
   + ix("matrice", "1.764 de rânduri", {"cauta": {
       "din": "CJ", "tinta": "SM", "vecini": ["BH", "SJ", "MM", "BN", "MS", "AB"],
       "t": "județul cel mai legat de Cluj dintre cele care <b>nu</b> se învecinează cu el.",
       "dupa": "Satu Mare: 541.340, mai mult decât Bihorul, care este vecin. Vecinătatea nu explică, așadar, toate legăturile."}})
   + "<h3>Cluj sau București?</h3>"
   "<p>Social Capital Lab a publicat o hartă a Europei construită pe o singură întrebare: "
   "sunt utilizatorii din fiecare regiune mai conectați cu Madridul sau cu Barcelona? Comparația de mai sus pune "
   "aceeași întrebare pentru România, pe fișierul SCI pe regiuni NUTS 3 (a doua vedere, „Hartă”). Pentru fiecare județ "
   "se compară două rânduri din tabelul diadic: perechea cu Clujul și perechea cu "
   "Bucureștiul.</p>"
   + "<p>Interpretarea revine la cursul 6, în analiza exploratorie. O explicație formulată "
   "acum poate fi notată și verificată atunci, pe date.</p>")


# ===========================================================================
#  9-14. Tipuri de date
# ===========================================================================

RAMURI_PY = [
    {"nume": "Nimic", "tipuri": [
        {"n": "None", "cls": "NoneType", "imut": True,
         "d": "Absența unei valori. Nu e zero și nu e text gol: marchează o valoare necunoscută.",
         "ex": "valoare = None\nprint(valoare is None)   # True",
         "la": "O măsurătoare care lipsește. În pandas devine NaN."}]},
    {"nume": "Numere", "sub": [
        {"nume": "întregi", "tipuri": [
            {"n": "int", "cls": "class int", "imut": True,
             "d": "Numere întregi, fără limită de mărime în Python.",
             "ex": "an = 2024\npopulatie = 19051804",
             "la": "Ani, populație, numărători."},
            {"n": "bool", "cls": "class bool", "imut": True,
             "d": "Adevărat sau fals. Tehnic, este un subtip al lui int: True valorează 1.",
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
             "d": "Text. Ce se citește dintr-un fișier text, linie cu linie, rămâne text până la o conversie explicită.",
             "ex": "cod = \"RO113\"\nan = \"2024\"              # text!\nprint(int(an) + 1)       # 2025",
             "la": "Nume, coduri de țară și coduri NUTS."},
            {"n": "tuple", "cls": "class tuple", "imut": True,
             "d": "Secvență ordonată care nu se mai poate modifica după creare.",
             "ex": "coord = (46.77, 23.59)\nperechea = (\"RO113\", \"RO116\")",
             "la": "Coordonate, și cheia unei perechi de județe."},
            {"n": "bytes", "cls": "class bytes", "imut": True,
             "d": "Octeți bruți. Apare la citirea unui fișier binar sau a unui răspuns HTTP neinterpretat.",
             "ex": "r = requests.get(url)\nprint(type(r.content))   # bytes"}]},
        {"nume": "modificabile", "tipuri": [
            {"n": "list", "cls": "class list",
             "d": "Secvență ordonată, modificabilă. Unul dintre tipurile cele mai folosite.",
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
         "d": "Perechi cheie-valoare. Structura oricărui obiect JSON convertit în Python.",
         "ex": "rand = {\"tara\": \"RO\",\n        \"an\": 2024,\n        \"valoare\": 19051804}\nprint(rand[\"valoare\"])",
         "la": "Un obiect JSON dintr-un răspuns de API devine, în Python, un dicționar."}]},
    {"nume": "Altele", "tipuri": [
        {"n": "funcții", "cls": "class function",
         "d": "Funcțiile sunt și ele valori: pot fi puse într-o listă sau transmise ca argument.",
         "ex": "def curata(x):\n    return x.strip()\n\nnume = [curata(n) for n in brute]"},
        {"n": "module", "cls": "class module",
         "d": "Un modul importat e și el un obiect, cu tipul lui.",
         "ex": "import pandas as pd\nprint(type(pd))          # module"}]},
]

TIPURI_LISTA = [
    ("Valori simple", "var(--accent)", [
        ("int", "număr întreg", "Numere fără zecimale, pentru numărători și calcule.", "178", "anul, populația, numărul de țări"),
        ("float", "număr real", "Numere cu zecimale, scrise cu punct, nu cu virgulă.", "8.5", "densitatea, PIB-ul pe locuitor, ratele"),
        ("str", "șir de caractere", "Text: orice stă între ghilimele, chiar dacă arată ca un număr.", "\"RO\"", "codurile de țară și de județ, numele"),
        ("bool", "valoare logică", "True sau False, cu majusculă. Rezultatul oricărei comparații.", "True", "filtrele, ca user_country == \"RO\""),
        ("NoneType", "lipsa valorii", "None marchează o valoare necunoscută. Nu e zero și nu e text gol.", "None", "o valoare lipsă; în coloanele numerice din pandas, NaN"),
    ]),
    ("Colecții", "var(--ambra)", [
        ("list", "listă", "Valori în ordine, accesate după poziție, numerotată de la 0. Se poate modifica.", "[\"RO\", \"IT\"]", "un tablou dintr-un JSON"),
        ("tuple", "tuplu", "Ca lista, dar nu mai poate fi modificat după creare.", "(46.77, 23.59)", "coordonatele, o pereche de județe"),
        ("dict", "dicționar", "Perechi cheie: valoare, accesate după cheie.", "{\"tara\": \"RO\"}", "un obiect dintr-un JSON"),
        ("set", "mulțime", "Valori fără duplicate și fără ordine.", "{\"RO\", \"HU\"}", "codurile dintr-o sursă care lipsesc din alta"),
    ]),
]

def tipuri_slide():
    """Pe slide: exemplul, tipul, numele în română. Atât."""
    out = ['<div class="tp3">']
    for grupa, _, rand in TIPURI_LISTA:
        out.append(f"<section><h4>{grupa}</h4><ul>")
        for n, ro, d, ex, la in rand:
            out.append(f'<li><code class="tp3__ex">{ex.replace("<", "&lt;")}</code>'
                       f'<span class="tp3__t">{n}</span><span class="tp3__ro">{ro}</span></li>')
        out.append("</ul></section>")
    out.append("</div>")
    return "".join(out)



def tipuri_lista():
    """Două tabele simple: valorile simple și colecțiile. Fără carduri."""
    SCURT = {"int": "ani, populații, numărători", "float": "densitate, PIB, rate",
             "str": "coduri și nume", "bool": "rezultatul unei comparații",
             "NoneType": "o valoare care lipsește", "list": "ordonată, accesată după poziție",
             "tuple": "ca lista, dar nemodificabil", "dict": "perechi cheie: valoare",
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
                       f'<p class="tpl__la">În proiect: {la}</p></div>')
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
        {"n": "persoana", "t": "dict", "e": "Acolade cu perechi cheie-valoare: dicționar. Un set ar avea acolade fără două puncte."},
    ],
}

sl("s9o", "Tipuri de date", "Ce tipuri de date există",
   "<h2>Tipurile de date din Python</h2>"
   "<p class=\"cheie\">Tipul determină operațiile posibile: numerele se adună, "
   "textele se concatenează, listele se parcurg.</p>"
   + tipuri_slide(),
   manual=
   "<h2>Tipurile de date din Python</h2>"
   "<p>Tipul unei valori decide ce operații sunt posibile cu ea, iar diferența are consecințe "
   "practice. O coloană de populații citită ca text se sortează lexicografic, caracter cu caracter: „19051804” "
   "(România) ajunge înaintea lui „9584627” (Ungaria), pentru că 1 vine înaintea lui 9. Codul "
   "rulează fără nicio eroare, iar rezultatul este greșit.</p>"
   "<p>Regula inversă contează la fel de mult: codurile rămân text, chiar dacă arată ca "
   "numere. Un cod poștal ca <code>\"010011\"</code>, transformat în număr, își pierde zeroul "
   "din față, iar codul de țară <code>NA</code> al Namibiei este citit de pandas ca valoare "
   "lipsă dacă nu se specifică altfel.</p>"
   + tipuri_lista_manual()
   + "<h3>Toate tipurile</h3><p>Tabelul de mai sus conține tipurile folosite la curs. Python are și "
   "altele, mai rare în analiza datelor; arborele de mai jos le arată pe toate, grupate.</p>"
   + ix("arbore", "Arborele tipurilor",
        {"titlu": "Apasă pe orice tip",
         "intro": "Pentru fiecare tip: definiția, un exemplu și locul în care apare în proiect.",
         "legenda": True, "radacina": "valoare", "ramuri": RAMURI_PY}))


sl("s9", "Tipuri de date", "Ce tip are fiecare valoare",
   "<h2>Ce tip are fiecare valoare?</h2>"
   + ix("consola", "Tipurile din partea 2 a caietului", TIPURI_CONSOLA),
   manual=
   "<h2>Ce tip are fiecare valoare?</h2>"
   "<p>Funcția <code>type()</code> răspunde la prima întrebare de diagnostic: ce fel de "
   "valoare se află sub un nume. În Jupyter, valoarea ultimei linii dintr-o celulă se afișează "
   "automat: <code>type(tara)</code> afișează <code>str</code>, fără <code>print</code>. "
   "Într-un fișier <code>.py</code> este nevoie de <code>print(type(tara))</code>, care afișează "
   "<code>&lt;class 'str'&gt;</code>. Răspunsul este același, în altă formă.</p>"
   + ix("consola", "Scrie tipul, apoi verifică", TIPURI_CONSOLA)
   + ix("pas", "Cinci valori, cinci tipuri", PAS_TIPURI))


CAPCANE = (
    '<div class="capc">'
    '<div><code class="capc__e">"2024" &lt; "999"</code><code class="capc__r">True</code>'
    "<p>Textele se compară literă cu literă, iar 2 vine înaintea lui 9.</p></div>"
    '<div><code class="capc__e">float("3,7")</code><code class="capc__r">ValueError</code>'
    "<p>Virgula zecimală din fișierele românești. Aici, cel puțin, apare o eroare explicită.</p></div>"
    '<div><code class="capc__e">None   0   ""</code><code class="capc__r">trei lucruri</code>'
    "<p>Lipsă, zero, text gol. Într-un tabel pot arăta la fel, într-o medie nu.</p></div>"
    "</div>")

sl("s11", "Tipuri de date", "Capcanele de tip",
   "<h2>Greșelile care nu dau eroare</h2>"
   + CAPCANE
   + ix("prezice", "Text plus text", {
       "id": "c1-prezice-tip", "fisier": "01_introducere.ipynb · 2. Variabile",
       "sarcina": "Anticipează rezultatul fără să rulezi codul.",
       "cod": "varsta_text = \"24\"\nprint(varsta_text + \"1\")",
       "intrebare": "Ce afișează?",
       "variante": ["25", "241", "Eroare", "24 1"],
       "corect": 1,
       "indiciu": "Ghilimelele fac din 24 un text. Ce face <code>+</code> cu două texte?",
       "laBine": "Operatorul + concatenează textele, nu le adună.",
       "explicatie": "Cu ghilimele, <code>\"24\"</code> e <code>str</code>, iar <code>+</code> "
                     "între două texte le concatenează. La fel se întâmplă cu un an citit ca text dintr-un fișier."}),
   manual=
   "<h2>Greșelile care nu dau eroare</h2>"
   "<p>Erorile de tip care opresc execuția se corectează ușor: mesajul spune unde și de "
   "ce. Mai greu de observat sunt cele care nu opresc nimic: codul rulează, fișierul se "
   "scrie, iar rezultatul este greșit fără niciun semnal.</p>"
   + ix("prezice", "Text plus text", {
       "id": "c1-prezice-tip", "fisier": "01_introducere.ipynb · 2. Variabile",
       "sarcina": "Aceeași celulă ca în caietul de azi. Anticipează rezultatul fără să rulezi codul.",
       "cod": "varsta_text = \"24\"\nprint(varsta_text + \"1\")",
       "intrebare": "Ce afișează?",
       "variante": ["25", "241", "Eroare", "24 1"],
       "corect": 1,
       "indiciu": "Ghilimelele fac din 24 un text. Ce face <code>+</code> cu două texte?",
       "laBine": "Operatorul + concatenează textele, nu le adună.",
       "explicatie": "Cu ghilimele, <code>\"24\"</code> e <code>str</code>, iar <code>+</code> "
                     "între două texte le concatenează. La fel se întâmplă cu un an citit ca text dintr-un "
                     "fișier. Mai jos, conversia corectă se face cu <code>int()</code>."})
   + ix("cod", "Repară două conversii", {
       "id": "c1-cod-tipuri", "fisier": "tipuri.py",
       "sarcina": "Anul a fost citit ca text. Convertește-l în număr, pentru adunare, apoi înapoi în text, pentru a-l include într-o propoziție.",
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
       "laBine": "int și str, în ambele sensuri: conversii folosite frecvent la curățarea datelor.",
       "laRau": "Fără ghilimele: aici se cer numele a două funcții.",
       "explicatie": "Fără conversii, <code>\"2024\" + 1</code> dă eroare, iar <code>\"Anul \" + 2025</code> la fel: "
                     "Python nu concatenează text cu număr. Mai periculos este cazul fără eroare, cel de mai sus: "
                     "<code>\"2024\" + \"1\"</code> produce, fără niciun avertisment, <code>\"20241\"</code>."})
   + "<h3>Virgula zecimală</h3>"
   "<p>Într-un fișier românesc, zecimalele se scriu cu virgulă: <code>3,7</code>. "
   "<code>float(\"3,7\")</code> produce o excepție <code>ValueError</code>, iar aici eroarea este un avantaj. Problema apare la citirea unui "
   "fișier întreg: coloana rămâne text, se sortează lexicografic și nu semnalează nimic. "
   "Corecția este <code>float(x.replace(\",\", \".\"))</code> pentru o valoare, sau "
   "<code>decimal=\",\"</code> în <code>pd.read_csv</code>, pentru tot fișierul.</p>"
   + nota("Lipsă, zero, text gol",
          "<code>None</code>, <code>0</code> și <code>\"\"</code> sunt trei lucruri diferite. "
          "Zero este o valoare măsurată; <code>None</code> înseamnă că valoarea lipsește. În "
          "caiet, Ana are ocupația <code>None</code>: ocupația ei este necunoscută. Mihai are "
          "<code>0.0</code> ore de studiu: studiază zero ore. Dacă valorile lipsă sunt tratate ca "
          "zerouri, media scade fără nicio eroare."))


OCTETI = (
    '<div class="oct"><h4>Cât spațiu ocupă un număr întreg</h4>'
    '<div class="oct__r"><code>SMALLINT</code><span class="oct__b"><i></i><i></i></span>'
    '<span class="oct__t"><b>2 octeți</b> · până la 32.767</span></div>'
    '<div class="oct__r"><code>INT</code><span class="oct__b"><i></i><i></i><i></i><i></i></span>'
    '<span class="oct__t"><b>4 octeți</b> · până la 2.147.483.647</span></div>'
    '<div class="oct__r oct__r--big"><code>BIGINT</code><span class="oct__b"><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i></span>'
    '<span class="oct__t"><b>8 octeți</b> · până la 9.223.372.036.854.775.807</span></div>'
    '<p class="oct__n">Fiecare valoare din coloană ocupă atâția octeți, pe fiecare rând. Se alege cel mai mic tip în '
    'care încape <b>cea mai mare valoare posibilă</b>, nu cea mai mare valoare observată. La cele 1,8 milioane de '
    'rânduri din fișierul pe regiuni NUTS 3, diferența dintre INT și BIGINT e de 7,2 MB, doar pentru o coloană. '
    'Detaliile: <a class="leg" href="https://www.postgresql.org/docs/current/datatype-numeric.html" '
    'target="_blank" rel="noopener">tipurile numerice în PostgreSQL</a>.</p></div>')


sl("s11c", "Tipuri de date", "Conversiile",
   "<h2>Din text în număr, și înapoi</h2>"
   + ix("cod", "Repară două conversii", {
       "id": "c1-cod-tipuri", "fisier": "tipuri.py",
       "sarcina": "Din text în număr, pentru adunare; apoi înapoi în text, pentru concatenare.",
       "cod": "an_text = \"2024\"\n"
              "urmatorul = {{1}}(an_text) + 1           # 2025\n"
              "mesaj = \"Datele merg pana in \" + {{2}}(urmatorul)\n"
              "print(mesaj)",
       "goluri": {
           "1": {"ok": ["int"], "ajutor": "funcția"},
           "2": {"ok": ["str"], "ajutor": "funcția"}},
       "indiciu": "Funcțiile de conversie au numele tipurilor: <code>int</code> face un număr întreg, <code>str</code> face text.",
       "iesire": "Datele merg pana in 2025",
       "laBine": "int și str, în ambele sensuri: conversii folosite frecvent la curățarea datelor.",
       "laRau": "Fără ghilimele: aici se cer numele a două funcții.",
       "explicatie": "Fără conversii, <code>\"2024\" + 1</code> dă eroare, iar <code>\"Anul \" + 2025</code> la fel: "
                     "Python nu concatenează text cu număr. Mai periculos e cazul fără eroare: "
                     "<code>\"2024\" + \"1\"</code> produce, fără niciun avertisment, <code>\"20241\"</code>."}),
   manual="")


sl("s12", "Tipuri de date", "Tipuri în SQL",
   "<h2>În baza de date, tipul se declară</h2>"
   "<p>Valorile care nu corespund tipului sunt respinse. Alege tipul după valori.</p>"
   + OCTETI
   + ix("coloane", "Tabelul SCI, la cursul 5", {
       "id": "c1-sql-coloane", "poarta": False,
       "fisier": "create table sci (…)",
       "nota": "valori reale din country.csv",
       "sarcina": "Pentru fiecare coloană, tipul potrivit.",
       "tipuri": ["CHAR(2)", "VARCHAR(50)", "TEXT", "INT", "BIGINT", "BOOLEAN"],
       "coloane": [
           {"nume": "user_country", "ok": "CHAR(2)",
            "de_ce": "lungime fixă, exact două caractere; un cod mai lung e respins la inserare"},
           {"nume": "friend_country", "ok": "CHAR(2)",
            "de_ce": "același cod, aceeași regulă"},
           {"nume": "scaled_sci", "ok": "INT",
            "de_ce": "Meta scalează indicele astfel încât maximul să fie exact 1.000.000.000, sub limita lui INT (2.147.483.647). BIGINT ar funcționa și el, dar ocupă dublu fără motiv"}],
       "cap": [["RO", "RO", 6252768], ["RO", "MD", 173794],
               ["RO", "AT", 124693], ["RO", "HU", 85021]],
       "laBine": "Aceasta este structura tabelului din baza de date de la cursul 5.",
       "laRau": "Codurile au lungime fixă. Pentru indice, verifică valoarea "
                "maximă posibilă."}),
   manual=
   "<h2>Tipuri de date în SQL</h2>"
   "<p>De la cursul 5, datele proiectului stau într-o bază de date, nu în fișiere. Acolo "
   "tipurile nu se deduc la citire, ci se declară la crearea tabelului, iar baza de date "
   "respinge valorile care nu se potrivesc (așa procedează PostgreSQL, baza de date a cursului). "
   "Regimul este mai strict decât în Python, cu un "
   "avantaj: o greșeală de tip apare la inserare, nu mai târziu, în analiză.</p>"
   + tabel(["Familie", "Tipuri", "Pentru ce"], [
       ["Numerice", "~INT, BIGINT, NUMERIC, DOUBLE PRECISION", "Valori întregi (frecvențe, ani), valori calculate"],
       ["Dată și timp", "~DATE, TIME, TIMESTAMP", "Momente în timp; nu se păstrează ca text"],
       ["Caractere", "~CHAR, VARCHAR, TEXT", "Nume, coduri, descrieri"],
       ["Logic", "~BOOLEAN", "Adevărat sau fals"],
       ["Structurat", "~JSON, JSONB", "Răspunsuri de API păstrate ca atare"],
   ])
   + "<h3>CHAR, VARCHAR sau TEXT</h3>"
   "<ul>"
   "<li><code>CHAR(n)</code> are lungime fixă și completează cu spații valorile mai scurte. "
   "Potrivit pentru coduri de lungime constantă, ca codurile de țară din două litere.</li>"
   "<li><code>VARCHAR(n)</code> are lungime variabilă, cu o limită maximă.</li>"
   "<li><code>TEXT</code> nu are o limită declarată. În PostgreSQL nu este mai lent decât "
   "<code>VARCHAR</code>, de aceea este alegerea implicită pentru text liber.</li></ul>"
   "<p>Documentația PostgreSQL notează că <code>CHAR(n)</code> nu aduce un câștig de "
   "performanță față de celelalte două; aici îl folosim pentru că exprimă explicit regula "
   "„exact două caractere”. <code>VARCHAR(2)</code> ar fi o alegere la fel de corectă.</p>"
   + OCTETI
   + ix("coloane", "Tabelul SCI, la cursul 5", {
       "id": "c1-sql-coloane", "poarta": False,
       "fisier": "create table sci (…)",
       "nota": "valori reale din country.csv",
       "sarcina": "Pentru fiecare coloană, tipul potrivit.",
       "tipuri": ["CHAR(2)", "VARCHAR(50)", "TEXT", "INT", "BIGINT", "BOOLEAN"],
       "coloane": [
           {"nume": "user_country", "ok": "CHAR(2)",
            "de_ce": "lungime fixă, exact două caractere"},
           {"nume": "friend_country", "ok": "CHAR(2)",
            "de_ce": "același cod, aceeași regulă"},
           {"nume": "scaled_sci", "ok": "INT",
            "de_ce": "Meta scalează indicele astfel încât maximul să fie exact 1.000.000.000, sub limita lui INT (2.147.483.647). BIGINT ar funcționa și el, dar ocupă dublu fără motiv"}],
       "cap": [["RO", "RO", 6252768], ["RO", "MD", 173794],
               ["RO", "AT", 124693], ["RO", "HU", 85021]],
       "laBine": "Aceasta este structura tabelului din baza de date de la cursul 5.",
       "laRau": "Codurile au lungime fixă. Pentru indice, verifică valoarea maximă posibilă."})
   + nota("Cheia primară",
          "<code>primary key (user_country, friend_country)</code> împiedică inserarea "
          "aceleiași perechi de două ori, greșeala tipică la reîncărcarea unui fișier."))


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
        {"n": "CompoundCurve", "cls": "Curve", "d": "Segmente drepte și arce, unite într-o singură linie."}]},
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
              "longitudine, apoi latitudine, invers față de ordinea uzuală.",
     "la": "Centroidul fiecărui județ (<code>harta.centroid</code>). Distanța dintre două județe e "
           "distanța dintre centroizii lor, în metri, împărțită la 1.000."},
    {"k": "multipoint", "n": "MultiPoint", "et": "mai multe puncte", "dim": 0,
     "def": "O colecție de puncte, păstrată ca o singură geometrie, într-un singur rând.",
     "wkt": "MULTIPOINT ((23.59 46.77), (26.10 44.43))",
     "py": "shapely.MultiPoint([(23.59, 46.77), (26.10, 44.43)])",
     "pg": "ST_NumGeometries(geom), ST_GeometryN(geom, 1)",
     "valid": "Punctele se pot repeta. <code>ST_IsSimple</code> verifică dacă există puncte repetate.",
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
     "la": "Granița României cu Ucraina, formată din două segmente separate: unul la nord, unul în Delta Dunării."},
    {"k": "polygon", "n": "Polygon", "et": "poligon", "dim": 2,
     "def": "O suprafață mărginită de un inel exterior închis, cu zero sau mai multe inele interioare, "
            "adică găuri. Geometria de dimensiune 2.",
     "wkt": "POLYGON ((0 0, 6 0, 6 6, 0 6, 0 0),\n         (2 2, 4 2, 4 4, 2 4, 2 2))",
     "py": "shapely.Polygon(exterior, [gaura])\n.area, .centroid, .touches(alt), .is_valid",
     "pg": "ST_Area, ST_Centroid, ST_Touches, ST_Intersects, ST_IsValid, ST_MakeValid",
     "valid": "Inelele sunt închise (primul punct e și ultimul) și au cel puțin 4 puncte; nu se "
              "autointersectează; găurile stau înăuntru și ating exteriorul cel mult într-un punct. "
              "Geometriile invalide se corectează cu <code>make_valid</code>. GeoJSON (RFC 7946) recomandă inelul exterior în sens "
              "invers acelor de ceasornic.",
     "la": "Conturul fiecărui județ și al fiecărei regiuni NUTS. De aici ies centroizii, ariile și vecinătatea."},
    {"k": "multipolygon", "n": "MultiPolygon", "et": "mai multe poligoane", "dim": 2,
     "def": "Mai multe poligoane, ca o singură înregistrare.",
     "wkt": "MULTIPOLYGON (((…)), ((…)), ((…)))",
     "py": "harta.dissolve(\"CNTR_CODE\")   # județele lipite pe țări",
     "pg": "ST_Union(geom), ST_Collect(geom)",
     "valid": "Interioarele poligoanelor nu au voie să se suprapună; se pot atinge doar în puncte izolate.",
     "la": "Țările: un rând pe țară, cu insulele în aceeași geometrie. În caietul 07, județele se unesc pe "
           "țări cu <code>dissolve</code>, pentru a determina care țări au graniță comună."},
    {"k": "collection", "n": "GeometryCollection", "et": "amestec", "dim": 3,
     "def": "Un amestec de geometrii de feluri diferite: puncte, linii și poligoane laolaltă.",
     "wkt": "GEOMETRYCOLLECTION (POINT (…), LINESTRING (…))",
     "py": "shapely.GeometryCollection([...])",
     "pg": "ST_CollectionExtract(geom, 3)   # păstrează doar poligoanele",
     "valid": "Standardul o permite, dar o coloană de date are de obicei un singur fel de geometrie.",
     "la": "Nu o folosim. Apare des ca rezultat al unei intersecții; în acest caz, se extrage tipul de geometrie necesar."},
]

CRS = (
    "<h3>Coordonatele nu au sens fără sistemul de referință</h3>"
    '<div class="crs">'
    "<div><b>EPSG:4326</b><span>WGS 84, grade</span>"
    "<p>Latitudine și longitudine. Potrivit pentru stocare și afișare, nepotrivit pentru distanțe: un "
    "grad de longitudine măsoară circa 111 km la ecuator și circa 76 km la latitudinea Clujului.</p></div>"
    "<div><b>EPSG:3035</b><span>ETRS89 / LAEA Europe, metri</span>"
    "<p>Proiecția azimutală echivalentă Lambert, pentru Europa. Păstrează ariile; pe întinderea "
    "Europei, distanțele au erori mici. GISCO publică și contururile NUTS în 3035.</p></div>"
    "<div><b>1:20 milioane</b><span>contururi generalizate</span>"
    "<p>Pe harta simplificată, granițele vecinilor nu se ating perfect. De aceea, în caietul 07, granița "
    "comună se caută cu o zonă-tampon de 10 km, nu cu <code>touches</code>.</p></div>"
    "</div>")

sl("s13", "Tipuri de date", "Tipuri spațiale",
   "<h2>Tipuri de date spațiale</h2>"
   "<p>Sunt necesare pentru a defini „vecin” și „distanță”. Apasă pe fiecare geometrie.</p>"
   + ix("geom", "Geometriile din Simple Features", {"geometrii": GEOMETRII}),
   manual=
   "<h2>Tipuri de date spațiale</h2>"
   "<p>Datele spațiale au tipuri proprii, definite de standardul Simple Features (OGC, "
   "ISO 19125), pe care îl urmează deopotrivă Shapely, GeoPandas și PostGIS. Ierarhia pornește "
   "de la trei forme de bază, după dimensiune: punctul (0), linia (1) și suprafața (2), fiecare "
   "cu varianta ei „multi”. În proiect, aceste tipuri definesc două noțiuni de care depind "
   "multe întrebări: vecinătatea și distanța.</p>"
   + ix("geom", "Geometriile din Simple Features", {"geometrii": GEOMETRII})
   + CRS
   + "<p>Standardul cuprinde și curbe din arce de cerc (<code>CircularString</code>, "
   "<code>CompoundCurve</code>, <code>CurvePolygon</code>), din extensia SQL/MM. Ele apar rar "
   "în datele publice; contururile NUTS, de exemplu, sunt formate numai din segmente drepte.</p>"
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


sl("s14", "Tipuri de date", "Tipuri de fișiere",
   "<h2>Text sau binar</h2>"
   "<p class=\"cheie\">Un fișier text se citește direct; unul binar, doar cu programul lui.</p>"
   + ix("sortare", "Clasifică extensiile: text sau binar", {
       "id": "c1-cod-fisiere", "poarta": False,
       "sarcina": "Criteriul: poate Git să arate modificările din fișier, "
                  "rând cu rând?",
       "cosuri": [{"t": "Text", "d": "lizibil, versionabil"},
                  {"t": "Binar", "d": "are nevoie de un program"}],
       "elemente": [{"t": ".csv", "cos": 0}, {"t": ".json", "cos": 0},
                    {"t": ".xlsx", "cos": 1}, {"t": ".parquet", "cos": 1},
                    {"t": ".geojson", "cos": 0}, {"t": ".shp", "cos": 1},
                    {"t": ".md", "cos": 0}, {"t": ".pkl", "cos": 1},
                    {"t": ".yaml", "cos": 0}, {"t": ".sqlite", "cos": 1},
                    {"t": ".xml", "cos": 0}, {"t": ".png", "cos": 1}],
       "laBine": "Regula: un fișier care poate fi citit într-un editor de text simplu, ca Notepad, este text.",
       "laRau": "Criteriul: ce se vede la deschiderea fișierului într-un editor de text simplu.",
       "explicatie": "<code>.geojson</code> și <code>.xml</code> par „tehnice”, "
                     "dar sunt text simplu. <code>.parquet</code> și <code>.shp</code> "
                     "induc în eroare invers: conțin date tabelare, dar în format "
                     "binar. Consecința: într-un depozit Git, o modificare "
                     "într-un <code>.csv</code> se vede rând cu rând, una "
                     "într-un <code>.xlsx</code> apare doar ca „fișier modificat”."}),
   manual=
   "<h2>Tipuri de fișiere</h2>"
   "<p>Prima distincție, și cea mai importantă: un fișier <strong>text</strong> se poate "
   "deschide în orice editor și citi direct. Un fișier <strong>binar</strong> are nevoie de "
   "programul care îi cunoaște formatul. Distincția decide și ce poate arăta Git: într-un "
   "fișier text, modificările se văd rând cu rând; într-un fișier binar, Git vede doar că "
   "fișierul s-a schimbat.</p>"
   + ix("sortare", "Clasifică extensiile: text sau binar", {
       "id": "c1-cod-fisiere", "poarta": False,
       "sarcina": "Criteriul: poate Git să arate modificările din fișier, rând cu rând?",
       "cosuri": [{"t": "Text", "d": "lizibil, versionabil"},
                  {"t": "Binar", "d": "are nevoie de un program"}],
       "elemente": [{"t": ".csv", "cos": 0}, {"t": ".json", "cos": 0},
                    {"t": ".xlsx", "cos": 1}, {"t": ".parquet", "cos": 1},
                    {"t": ".geojson", "cos": 0}, {"t": ".shp", "cos": 1},
                    {"t": ".md", "cos": 0}, {"t": ".pkl", "cos": 1},
                    {"t": ".yaml", "cos": 0}, {"t": ".sqlite", "cos": 1},
                    {"t": ".xml", "cos": 0}, {"t": ".png", "cos": 1}],
       "laBine": "Un fișier care poate fi citit într-un editor de text simplu, ca Notepad, este text.",
       "laRau": "Criteriul: ce se vede la deschiderea fișierului într-un editor de text simplu.",
       "explicatie": "<code>.geojson</code> și <code>.xml</code> par „tehnice”, "
                     "dar sunt text simplu. <code>.parquet</code> și <code>.shp</code> "
                     "conțin date tabelare, dar în format binar."})
   + tabel(["Format", "Când se folosește"], [
       ["~.csv", "Tabele simple, plate. Universal, dar nu păstrează tipurile coloanelor."],
       ["~.json", "Date cu structură imbricată. Formatul în care răspund aproape toate API-urile."],
       ["~.ipynb", "Caietele Jupyter. Sunt fișiere JSON, deci text, dar conțin și rezultatele celulelor."],
       ["~.parquet", "Tabele mari. Binar, compact, rapid, păstrează tipurile coloanelor."],
       ["~.geojson", "Date cu geometrie. Text, deci lizibil și versionabil."],
       ["~.shp", "Shapefile: geometrie, dar binar și format din mai multe fișiere."],
       ["~.env", "Chei și parole. Nu se pune niciodată într-un depozit."],
   ])
   + "<h3>Un fișier text, citit în Python</h3>"
   "<p>Partea 3 din caiet citește <code>exemple_curs1/activitati.txt</code>, un jurnal fictiv "
   "cu patru evenimente, câte unul pe linie. Trei detalii contează la orice fișier text:</p>"
   "<ul>"
   "<li><code>encoding=\"utf-8\"</code> citește corect diacriticele; fără el, în versiunile "
   "de Python anterioare lui 3.15, codificarea implicită depinde de sistem, iar pe Windows "
   "textul poate apărea deformat.</li>"
   "<li><code>with open(...)</code> închide fișierul automat, la sfârșitul blocului.</li>"
   "<li>Fiecare linie se termină cu <code>\\n</code>, caracterul de linie nouă; "
   "<code>strip()</code> îl elimină, împreună cu spațiile de la margini.</li>"
   "</ul>"
   "<pre><code>with open(\"exemple_curs1/activitati.txt\", encoding=\"utf-8\") as fisier:\n"
   "    log_content = fisier.readlines()   # o listă, câte un element pe linie\n\n"
   "print(len(log_content))           # 4\n"
   "print(log_content[0].strip())     # prima linie, fără \\n</code></pre>"
   + nota("Căile",
          "Calea <code>exemple_curs1/activitati.txt</code> pornește din folderul caietului, "
          "<code>dsw/curs/</code>. Dacă apare <code>FileNotFoundError</code>, compară calea "
          "scrisă cu folderul afișat de <code>Path.cwd()</code>. Regula căilor este explicată pe "
          "larg la folderul cursului, la finalul manualului."))


# ===========================================================================
#  15-16. JSON
# ===========================================================================

ANATOMIE = {
    "id": "c1-json-anatomie", "poarta": False, "cerute": 4,
    "intro": "Alege o parte: este evidențiată în cod.",
    "linii": [
        "{",
        "  \"paginare\": { \"pagina\": 1, \"total\": 2 },",
        "  \"date\": [",
        "    {",
        "      \"tara\": { \"cod\": \"RO\", \"nume\": \"România\" },",
        "      \"an\": \"2024\",",
        "      \"populatie\": 19051804,",
        "      \"coordonate\": [45.94, 24.97],",
        "      \"estimat\": false,",
        "      \"nota\": null",
        "    }",
        "  ]",
        "}",
    ],
    "parti": [
        {"et": "Obiectul rădăcină", "py": "dict", "l": [0, 12],
         "d": "Tot răspunsul, între acolade. Un <b>obiect</b> e o colecție de perechi nume/valoare. "
              "În Python devine un <code>dict</code> cu două chei: <code>paginare</code> și <code>date</code>."},
        {"et": "Tablou", "py": "list", "l": [2, 11],
         "d": "Între paranteze drepte: o listă ordonată de valori, aici de obiecte. Din el se face "
              "tabelul: fiecare element al tabloului devine un rând. Aici e unul singur; un răspuns "
              "real are câte un element pentru fiecare an sau țară."},
        {"et": "Element al tabloului", "py": "dict", "l": [3, 10],
         "d": "Un obiect din tablou: un rând al viitorului tabel. Numele lui devin coloane."},
        {"et": "Obiect imbricat", "py": "dict în dict", "l": [4, 4],
         "d": "O valoare care e, la rândul ei, un obiect. În tabel, <code>json_normalize</code> îl "
              "desface în două coloane: <code>tara.cod</code> și <code>tara.nume</code>."},
        {"et": "Pereche nume/valoare", "py": "cheie: valoare", "l": [6, 6],
         "d": "Numele e mereu un șir între ghilimele, urmat de două puncte și de valoare. Aici numele "
              "e <code>populatie</code>, iar valoarea e un <b>număr</b>, fără ghilimele, care devine <code>int</code>."},
        {"et": "Șir de caractere", "py": "str", "l": [5, 5],
         "d": "<code>\"2024\"</code> are ghilimele, deci e un <b>șir</b>, nu un număr. "
              "<code>\"2024\" + 1</code> dă eroare, iar <code>\"2024\" &lt; \"999\"</code> e "
              "adevărat, fiindcă textul se compară caracter cu caracter."},
        {"et": "Tablou de numere", "py": "list", "l": [7, 7],
         "d": "Un tablou ca valoare. Într-un tabel plat nu încape ca atare: se desface în două coloane "
              "sau rămâne listă într-o celulă, ceea ce complică pașii următori."},
        {"et": "true / false", "py": "bool", "l": [8, 8],
         "d": "Valorile logice se scriu cu literă mică în JSON și devin <code>True</code> și "
              "<code>False</code> în Python."},
        {"et": "null", "py": "None", "l": [9, 9],
         "d": "Spune explicit că valoarea lipsește: aici nu există o notă. Nu e zero. În Python devine "
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
         "indiciu": "Pozițiile negative se numără de la sfârșit: -1 este ultima."},
        {"t": "orașul Anei", "cale": "persoana[\"city\"]", "indiciu": "Într-un dicționar, accesul se face după cheie, scrisă între ghilimele."},
        {"t": "dacă Ana e studentă", "cale": "persoana[\"student\"]"},
    ],
    "exemplu": "tari[1]",
}

CALE_LISTE = {
    "env": {"tari": ["RO", "IT", "ES", "DE"],
            "persoana": {"name": "Ana", "age": 24, "city": "Cluj-Napoca", "student": True}},
    "tinte": [{"t": "prima țară", "cale": "tari[0]"},
              {"t": "orașul Anei", "cale": "persoana[\"city\"]"},
              {"t": "dacă Ana e studentă", "cale": "persoana[\"student\"]"}],
}


sl("s14l", "JSON", "Liste și dicționare",
   "<h2>Mai multe valori, împreună</h2>"
   "<p class=\"cheie\">Listă: alegi o <b>poziție</b>. Dicționar: alegi o <b>cheie</b>.</p>"
   + ix("cale", "Alege, nivel cu nivel", CALE_LISTE),
   manual=
   "<h2>Liste și dicționare</h2>"
   "<p>O listă păstrează valori în ordine; fiecare are o poziție, numerotată de la 0. Un "
   "dicționar păstrează perechi cheie-valoare; o valoare se accesează după numele cheii. "
   "Distincția dintre poziție și cheie este tot ce trebuie pentru a citi un JSON, oricât de "
   "adânc ar fi imbricat.</p>"
   + ix("cale", "Alege, nivel cu nivel", CALE_LISTE)
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
   "<p>JSON are exact două structuri: <strong>obiectul</strong>, între acolade, o colecție de "
   "perechi nume-valoare, și <strong>tabloul</strong>, între paranteze drepte, o listă "
   "ordonată de valori. Cele două se pot imbrica una în alta oricât de adânc, iar din această "
   "combinație sunt construite răspunsurile API-urilor folosite la curs.</p>"
   + tabel(["În JSON", "În Python"], [
       ["~string", "~str"], ["~number", "~int / float"],
       ["~true / false", "~True / False"], ["~null", "~None"],
       ["~object", "~dict"], ["~array", "~list"],
   ])
   + "<p>În răspunsurile de API, rădăcina este de regulă un obiect sau un tablou. API-ul Băncii Mondiale "
   "întoarce un tablou cu două elemente: informațiile despre paginare, apoi datele.</p>"
   + ix("anatomie", "Un răspuns, simplificat, pe bucăți", ANATOMIE)
   + "<h3>Din JSON în tabel</h3>"
   "<p>Structura de mai sus nu este un tabel. Pasul care o transformă în tabel este mereu "
   "același: se selectează lista din interior, iar fiecare element al ei devine un rând.</p>"
   + ix("desfa", "Cum devine un răspuns un tabel", {
       "id": "c1-desfa",
       "sursa": "api.worldbank.org",
       "buton": "Arată lista",
       "cheieCap": "paginare", "cheieLista": "date",
       "coloane": ["tara", "an", "populatie"],
       "elemente": [
           {"tara": "RO", "an": 2024, "populatie": 19051804},
           {"tara": "RO", "an": 2023, "populatie": 19061062},
           {"tara": "HU", "an": 2024, "populatie": 9562065},
       ],
       "p0": "Răspunsul complet, așa cum este returnat de API.",
       "p1": "Lista din interior: doar ea devine tabel.",
       "p2": "Fiecare element al listei a devenit un rând."})
   + nota("De aici vine json_normalize",
          "Operația de mai sus are o funcție dedicată în pandas, <code>pd.json_normalize</code>. "
          "O folosim la cursul 2; aici contează să fie clar ce face."))


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

CALE_PERS = {
    "env": {"user_data": {"users": [_pers_py(x) for x in PERS]}},
    "tinte": [{"t": "al doilea hobby al Anei", "cale": "user_data[\"users\"][0][\"hobbies\"][1]"},
              {"t": "orașul Elenei", "cale": "user_data[\"users\"][2][\"city\"]"},
              {"t": "ocupația lui Mihai", "cale": "user_data[\"users\"][1][\"occupation\"]"}],
}


sl("s15p", "JSON", "Drumul prin persoane.json",
   "<h2>Coborâm până la o valoare</h2>"
   "<p class=\"cheie\">La fiecare nivel: dicționar, alegi o cheie; listă, alegi o poziție.</p>"
   + ix("cale", "Nivel cu nivel, până la o valoare", CALE_PERS),
   manual=
   "<h2>Drumul până la o valoare</h2>"
   "<p>Exemplul din partea 4 a caietului: <code>persoane.json</code>, trei persoane fictive, "
   "cu aceleași chei ca fișa personală din partea 2. Tiparul este același în orice răspuns de API: "
   "la fiecare nivel se verifică tipul valorii curente, apoi se accesează o cheie (dicționar) sau o "
   "poziție (listă). La citire, <code>true</code> devine <code>True</code>, iar <code>null</code> "
   "devine <code>None</code>.</p>"
   "<p>Fișierele de exemplu ale caietului sunt în ZIP-ul cursului, în "
   "<code>dsw/curs/exemple_curs1/</code>, lângă caietul 01. Dacă lipsesc, se descarcă "
   f'de pe GitHub: <a class="leg" href="{repo_fisier("curs/exemple_curs1/persoane.json")}" '
   'target="_blank" rel="noopener">persoane.json</a> și '
   f'<a class="leg" href="{repo_fisier("curs/exemple_curs1/activitati.txt")}" '
   'target="_blank" rel="noopener">activitati.txt</a>, cu <em>Download raw file</em>, '
   "în același folder.</p>"
   + ix("cale", "Nivel cu nivel, până la o valoare", CALE_PERS)
   + ix("pas", "Aceeași cale, în cod", PAS_JSON))

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
         "indiciu": "country e un obiect imbricat: mai este nevoie de o cheie."},
    ],
    "exemplu": "raspuns[1][0]",
}

CALE_WB = {
    "env": {"raspuns": WB_RASPUNS},
    "tinte": [{"t": "câte pagini are răspunsul", "cale": "raspuns[0][\"pages\"]"},
              {"t": "populația din 2024", "cale": "raspuns[1][0][\"value\"]"},
              {"t": "numele țării", "cale": "raspuns[1][0][\"country\"][\"value\"]"}],
}


COD_JSON = {
    "id": "c1-cod-json", "fisier": "populatie.py",
    "sarcina": "Scrie în cod calea până la populația din 2024, identificată mai sus.",
    "cod": "raspuns = requests.get(url, params={\"format\": \"json\"}).json()\n\n"
           "date = raspuns[{{1}}]          # lista cu înregistrările\n"
           "populatie = date[0][{{2}}]     # numărul, din prima înregistrare\n"
           "print(populatie)              # 19051804",
    "goluri": {"1": {"ok": ["1"], "ajutor": "poziția"},
               "2": {"ok": ["\"value\"", "'value'"], "ajutor": "cheia"}},
    "indiciu": "Consultă structura de mai sus: datele sunt pe poziția 1, iar numărul se află la cheia "
               "<code>\"value\"</code>.",
    "iesire": "19051804",
    "laBine": "Același tip de cale se scrie la cursul 2, la fiecare răspuns de API.",
    "laRau": "Numerotarea începe de la zero. Cheia se scrie între ghilimele.",
    "explicatie": "<code>raspuns[1]</code> ocolește obiectul de paginare. "
                  "<code>[\"value\"]</code> extrage numărul. Dacă valoarea lipsește, rezultatul este "
                  "<code>None</code>, nu zero."}

sl("s16", "JSON", "Drumul până la valoare",
   "<h2>Un răspuns real, desfăcut</h2>"
   "<p class=\"cheie\">Aceeași cale, pe un răspuns real: populația României, de la Banca Mondială.</p>"
   + ix("cale", "Răspunsul Băncii Mondiale", CALE_WB),
   manual=
   "<h2>Un răspuns real, desfăcut</h2>"
   "<p>Un răspuns al API-ului Băncii Mondiale pentru populația României, simplificat la "
   "câmpurile folosite aici. Rădăcina este o listă cu două elemente: paginarea pe poziția 0, "
   "datele pe poziția 1. Fiecare înregistrare este un dicționar, iar unele valori, ca "
   "<code>country</code>, sunt la rândul lor dicționare.</p>"
   + ix("cale", "Răspunsul Băncii Mondiale", CALE_WB))


MASCA = {
    "coloane": ["user_country", "friend_country", "scaled_sci"],
    "coloana": "user_country", "valoare": "RO", "total": "31.684", "ramase": "178",
    "randuri": [["HU", "RO", "85021"], ["RO", "MD", "173794"], ["IT", "RO", "69327"],
                ["RO", "IT", "69327"], ["DE", "AT", "132496"], ["MD", "RO", "173794"],
                ["RO", "ES", "54179"], ["RO", "HU", "85021"]],
}

sl("s16s", "Primul contact cu SCI", "Un tabel real",
   "<h2>country.csv: filtrarea rândurilor</h2>"
   "<p class=\"cheie\">O comparație pe o coloană dă True sau False pe fiecare rând. "
   "Tabelul păstrează doar rândurile True.</p>"
   + ix("masca", "Cum lucrează un filtru, pas cu pas", MASCA),
   sci=True,
   manual=
   "<h2>Primul contact cu SCI</h2>"
   "<p>Partea 5 a caietului. Un rând din <code>country.csv</code> este o pereche de țări, iar "
   "prefixele <code>user_</code> și <code>friend_</code> marchează cele două capete ale perechii, nu o direcție. "
   "Fișierul are 178 × 178 = 31.684 de rânduri: fiecare țară cu fiecare, inclusiv cu ea însăși. "
   "Pentru a studia o singură țară, se fixează un capăt al perechii: o comparație pe o coloană dă "
   "<code>True</code> sau <code>False</code> pe fiecare rând, iar selecția întoarce un tabel nou, "
   "cu doar rândurile <code>True</code>; tabelul inițial rămâne neschimbat.</p>"
   + ix("masca", "Cum lucrează un filtru, pas cu pas", MASCA)
   + "<p>Două rânduri din tabelul de mai sus, Ungaria cu România și România cu Ungaria, au "
   "același indice, 85.021. SCI este simetric, deci fiecare pereche de țări diferite apare de "
   "două ori.</p>"
   + nota("keep_default_na=False",
          "pandas citește implicit textul <code>NA</code> ca valoare lipsă. În SCI, <code>NA</code> "
          "este codul Namibiei; argumentul <code>keep_default_na=False</code> îl păstrează ca text. "
          "Efectul secundar: celulele goale devin text gol (<code>\"\"</code>), nu <code>NaN</code>.")
   + ix("pas", "România și partenerii ei", PAS_SCI)
   + DIADIC_MANUAL
   + "<h3>Întrebarea semestrului</h3>"
   "<p>În clasamentul partenerilor României după SCI, Italia este abia pe locul 6, după "
   "Republica Moldova, Austria, Germania, Ungaria și Irlanda, deși are cei mai mulți cetățeni români. "
   "Explicația se construiește pas cu pas: aducem migrația la cursul 2, o pregătim și o curățăm "
   "la cursurile 3 și 4, o unim cu SCI la cursul 5, o explorăm la cursul 6 și o modelăm la "
   "cursul 7. Caietul cere, în acest punct, o explicație provizorie, verificată la final.</p>")


sl("s16x", "Primul contact cu SCI", "Exercițiu: perechile României",
   "<h2>Exercițiu: perechile României</h2>"
   + DIADIC_SLIDE,
   sci=True, manual="")


# ===========================================================================
#  17-18. Mediul și proiectul
# ===========================================================================

FOLDER_VENV = (
    '<span class="a">dsw/</span>                  <span class="c"># aici lucrezi</span>\n'
    '├── <span class="x">.venv/</span>            <span class="c"># nu se modifică</span>\n'
    '├── README.md\n'
    '├── requirements.txt  <span class="c"># pachetele</span>\n'
    '├── curs/             <span class="c"># caietele tale</span>\n'
    '└── proiect/          <span class="c"># de la cursul 2</span>')

PASI_VENV = (
    '<ol class="venvp__pasi">'
    f'<li><b>Descarci <a class="leg" href="{REPO_ZIP}">ZIP-ul cursului</a></b>, îl dezarhivezi și '
    f'redenumești folderul <code style="white-space:nowrap">{REPO_FOLDER}</code> în <code>dsw</code>.</li>'
    "<li><b>Deschizi <code>dsw</code> în VS Code</b> (<em>File → Open Folder</em>) și pornești "
    "<em>Terminal → New Terminal</em>. Terminalul pornește în <code>dsw</code>.</li>"
    "<li><b>Creezi mediul</b>, o singură dată:<br><code>py -m venv .venv</code>"
    '<span class="venvp__os">macOS: python3 -m venv .venv</span></li>'
    "<li><b>Îl activezi și instalezi pachetele</b>:<br><code>.\\.venv\\Scripts\\Activate.ps1</code><br>"
    "<code>pip install -r requirements.txt</code>"
    '<span class="venvp__os">macOS: source .venv/bin/activate</span></li>'
    "<li><b>În caiet</b> alegi <em>Select Kernel → Python Environments → .venv</em>.</li>"
    "</ol>")

VENV_BOX = '<div class="venvp"><div class="venvp__fld">' + FOLDER_VENV + "</div>" + PASI_VENV + "</div>"

VENV2 = (
    '<div class="venv2">'
    "<div><h4>1. Folderul</h4>"
    f'<p>Descarci <a class="leg" href="{REPO_ZIP}">ZIP-ul cursului</a>, îl dezarhivezi, îl redenumești '
    "<code>dsw</code> și îl deschizi în VS Code.</p></div>"
    '<div style="--c:var(--ambra)"><h4>2. Mediul</h4>'
    "<p>În terminalul din VS Code, o singură dată:</p>"
    "<pre><code>py -m venv .venv\n.\\.venv\\Scripts\\Activate.ps1\npip install -r requirements.txt</code></pre>"
    '<p class="venv2__os">macOS: <code>python3 -m venv .venv</code>, apoi <code>source .venv/bin/activate</code></p></div>'
    '<div style="--c:var(--salvie)"><h4>3. Caietul</h4>'
    "<p>În caiet alegi <em>Select Kernel → Python Environments → .venv</em>. De acum, codul "
    "rulează cu pachetele cursului.</p></div>"
    "</div>")

sl("s17", "Mediul de lucru", "Mediul virtual",
   "<h2>Mediul virtual, în folderul cursului</h2>"
   "<p class=\"cheie\">Python-ul și pachetele cursului, în <code>dsw/.venv</code>, separate de "
   "restul calculatorului.</p>"
   + VENV2,
   manual=
   "<h2>Medii de lucru virtuale în Python</h2>"
   "<p>Fără un mediu virtual, Python instalează pachetele într-un loc comun pentru tot "
   "calculatorul. Dacă două proiecte au nevoie de versiuni diferite ale aceleiași biblioteci, "
   "instalarea pentru al doilea o poate înlocui pe cea a primului, fără niciun avertisment. Un "
   "mediu virtual este un folder al proiectului, cu propriul interpretor Python și propriile "
   "pachete, separate de restul sistemului.</p>"
   "<p>Două reguli: mediul se află <strong>în folderul cursului</strong>, <code>dsw</code>, și "
   "<strong>nu se lucrează în el</strong>. Caietele și datele stau alături, în <code>curs/</code>, "
   "nu în interiorul lui <code>.venv</code>.</p>"
   f'<p>Folderul cursului vine dintr-o arhivă, <a class="leg" href="{REPO_ZIP}">ZIP-ul cursului</a>, '
   f'descărcată din <a class="leg" href="{REPO}" target="_blank" rel="noopener">depozitul cursului</a> '
   "de pe GitHub, cu caietul 01, datele lui și <code>requirements.txt</code>, lista pachetelor: <code>pandas</code> "
   "pentru tabele, <code>requests</code> pentru cererile de la cursul 2 și <code>ipykernel</code>, ca "
   "Python să ruleze în caiet. Arhiva se descarcă o singură dată. De la cursul 2 se descarcă doar "
   "caietul zilei, în <code>dsw/curs/</code>: arhiva întreagă, dezarhivată peste <code>dsw</code>, "
   "ar putea înlocui caietele deja completate.</p>"
   + VENV_BOX
   + "<h3>Activarea</h3>"
   "<p>După activare, <code>pip</code> și <code>python</code> din terminal sunt cele din "
   "<code>.venv</code>, iar linia din terminal începe cu <code>(.venv)</code>. Fără activare, "
   "<code>pip install</code> pune pachetele în Python-ul comun al calculatorului, iar caietul nu "
   "le găsește în mediu.</p>"
   "<p>Pe Windows, PowerShell poate refuza scriptul de activare, cu o eroare despre "
   "<em>execution policy</em>. Soluția: comanda de mai jos, rulată o singură dată, apoi o nouă activare.</p>"
   "<pre><code><span>Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser</span></code></pre>"
   "<p>Funcționează și fără activare, cu interpretorul mediului apelat prin calea completă: "
   "<code>.venv\\Scripts\\python -m pip install -r requirements.txt</code> pe Windows, "
   "<code>.venv/bin/python -m pip install -r requirements.txt</code> pe macOS. VS Code activează "
   "oricum automat mediul în terminalele noi, după ce acesta a fost ales ca interpretor.</p>"
   + ix("terminal", "Terminal simulat, pentru exercițiu", None,
        "Terminalul simulat răspunde ca unul real, inclusiv la comenzi greșite.")
   + nota("De ce .venv nu este în arhivă",
          "Este mare, este construit pentru calculatorul tău și se reface din două comenzi. În "
          "arhivă se află doar lista pachetelor, <code>requirements.txt</code>, din care fiecare "
          "își construiește propriul <code>.venv</code>, cu aceleași pachete. La fel se procedează și în "
          "depozitul echipei.")
   + "<h3>Cum se verifică mediul activ</h3>"
   "<p>Prima celulă de cod din caiet afișează <code>sys.executable</code>, adică interpretorul "
   "Python care rulează caietul. Calea afișată trebuie să conțină <code>.venv</code>. Dacă un "
   "<code>import</code> nu funcționează, primul lucru de verificat este kernelul ales în "
   "dreapta sus.</p>"
   "<pre><code>import sys\nprint(sys.executable)   # calea trebuie să conțină .venv</code></pre>"
   "<h3>Cum rulează un caiet</h3>"
   "<p>Un caiet are două feluri de celule: <strong>Markdown</strong>, cu text, și "
   "<strong>Code</strong>, cu Python. Variabilele create într-o celulă rămân în memoria "
   "kernelului, procesul Python din spatele caietului, de aceea celulele se rulează de sus în "
   "jos. Un <code>NameError</code> înseamnă, de obicei, că a fost sărită celula care definea "
   "variabila. <em>Restart</em> golește memoria kernelului, iar <em>Run All</em> rulează toate "
   "celulele în ordine; un caiet corect rulează fără erori după <em>Restart</em> urmat de <em>Run All</em>. Tastele de lucru sunt "
   'pe pagina <a class="leg" href="../scurtaturi/">Comenzile rapide din Jupyter</a>.</p>')





sl("s17t", "Mediul de lucru", "Exercițiu în terminal",
   "<h2>Exercițiu: mediul virtual, în terminalul simulat</h2>"
   + ix("terminal", "Terminalul pornește în folderul tău de utilizator", None,
        "Intră în <code>dsw</code>, creează mediul, activează-l și instalează pachetele. "
        "Comanda <code>ajutor</code> afișează comenzile necesare, în ordine."),
   manual="")

sl("s17o", "Mediul de lucru", "Ordinea comenzilor",
   "<h2>Ordinea comenzilor</h2>",
   manual="",
   dupa=ix("ordine", "Mediul virtual, de la zero", {
       "id": "c1-cod-venv",
       "sarcina": "Pune comenzile în ordinea în care se dau, de la folderul tău de utilizator până la "
                  "pachetele instalate.",
       "linii": ["cd dsw", "py -m venv .venv", ".\\.venv\\Scripts\\Activate.ps1",
                 "pip install -r requirements.txt", "pip list"],
       "indiciu": "Mediul se creează în dsw, deci primul pas este intrarea în acest folder. pip instalează "
                  "în mediu numai după activarea acestuia.",
       "iesire": "(.venv) PS C:\\Users\\student\\dsw> pip list\n"
                 "Package    Version\n---------- -------\nipykernel  …\npandas     …\nrequests   …",
       "laBine": "Aceasta este secvența care se execută o singură dată, la cursul 1.",
       "laRau": "Verifică, pentru fiecare comandă, folderul curent și interpretorul Python care o execută.",
       "explicatie": "Dacă <code>py -m venv .venv</code> vine înainte de <code>cd dsw</code>, mediul ajunge "
                     "în folderul tău de utilizator, fără nicio eroare. <code>pip install</code> înainte de "
                     "activare pune pachetele în Python-ul comun, iar <code>requirements.txt</code> se "
                     "găsește doar în <code>dsw</code>."}))


NODURI_FOLDER = [
    {"n": "dsw/", "ind": 0, "scurt": "aici lucrezi",
     "d": "Folderul cursului: arhiva de pe GitHub, dezarhivată și redenumită din "
          f"<code>{REPO_FOLDER}</code>. Pe el îl deschizi în VS Code și în el pornește terminalul.",
     "cine": "tu, o singură dată, la cursul 1",
     "git": "nu ca folder: e copia ta a depozitului cursului, fără Git"},
    {"n": ".venv/", "ind": 1, "scurt": "nu se modifică", "interzis": True,
     "d": "Python-ul cursului și pachetele lui, făcute de <code>py -m venv .venv</code> și de "
          "<code>pip install -r requirements.txt</code>. Aici nu se deschide și nu se salvează nimic. "
          "Dacă se deteriorează, se șterge și se recreează cu aceleași comenzi.",
     "cine": "Python și pip, niciodată tu", "ex": "Lib/, Scripts/, pyvenv.cfg",
     "git": "nu: se reface din <code>requirements.txt</code>"},
    {"n": "README.md", "ind": 1, "fel": "fis",
     "d": "Prima pagină a depozitului cursului: ce e în folder și cum pornești.",
     "cine": "profesorul", "git": "da: GitHub o arată sub lista fișierelor"},
    {"n": "requirements.txt", "ind": 1, "fel": "fis",
     "d": "Lista pachetelor cursului: <code>pandas</code>, <code>requests</code>, <code>ipykernel</code>. "
          "Din ea, fiecare își face un mediu cu aceleași pachete: <code>pip install -r requirements.txt</code>.",
     "cine": "profesorul; tu doar o folosești", "git": "da, în depozitul cursului"},
    {"n": "curs/", "ind": 1, "scurt": "caietele tale",
     "d": "Caietele cursului, pe care le completezi la oră. La fiecare curs nou descarci doar caietul "
          "zilei aici, lângă celelalte. Căile din caiete pornesc din <code>curs/</code>: "
          "<code>data/country.csv</code> înseamnă <code>curs/data/country.csv</code>.",
     "cine": "tu", "ex": "<code>01_introducere_si_datele_proiectului.ipynb</code>",
     "git": "caietele goale, în depozitul cursului; ce completezi tu rămâne la tine"},
    {"n": "data/", "ind": 2,
     "d": "Datele brute, așa cum au fost descărcate: nu se modifică. Rezultatele curățării se salvează "
          "în fișiere noi, alături, nu peste cele brute. De la cursul 2, fiecare curs are folderul lui, ca "
          "<code>data/c2/</code>.",
     "cine": "arhiva cursului, apoi codul din caiete",
     "ex": "<code>country.csv</code> de pe HDX, apoi <code>c2/migratie.csv</code> de la Eurostat",
     "git": "<code>country.csv</code> da; ce colectezi tu, nu"},
    {"n": "exemple_curs1/", "ind": 2,
     "d": "Două fișiere mici, fictive, pentru partea de JSON și de text din caietul 01.",
     "cine": "arhiva cursului", "ex": "<code>persoane.json</code>, <code>activitati.txt</code>",
     "git": "da, în depozitul cursului"},
    {"n": "proiect/", "ind": 1, "scurt": "de la cursul 2",
     "d": "Depozitul echipei, adus de pe GitHub la cursul 2, cu o singură comandă dată în "
          "<code>dsw</code>: <code>git clone &lt;adresa depozitului echipei&gt; proiect</code>. "
          "E singurul folder cu Git: munca echipei stă aici, exercițiile de la curs rămân în "
          "<code>curs/</code>.",
     "cine": "echipa", "git": "da: e chiar depozitul echipei"},
]

SORTARE_FOLDER = {
    "id": "c1-folder",
    "cosuri": [{"t": "curs/data/", "d": "datele cursului"}, {"t": "curs/", "d": "caietele tale"},
               {"t": "proiect/", "d": "munca echipei"}],
    "elemente": [{"t": "country.csv", "cos": 0}, {"t": "c2/migratie.csv", "cos": 0},
                 {"t": "01_introducere.ipynb", "cos": 1}, {"t": "02_colectarea.ipynb", "cos": 1},
                 {"t": "raport.ipynb, al echipei", "cos": 2}, {"t": "intrebarea.md, a echipei", "cos": 2}],
}

sl("s18", "Proiectul tău", "Folderul cursului, pe disc",
   "<h2>Folderul cursului, pe disc</h2>"
   "<p class=\"cheie\">Un singur folder, cu un loc pentru fiecare tip de fișier. Apasă pe fiecare element.</p>"
   + ix("folder", "Folderul cursului", {"noduri": NODURI_FOLDER}),
   manual=
   "<h2>Folderul cursului, pe disc</h2>"
   "<p>Un proiect de date nu este un caiet, ci un folder: datele, caietele, codul și mediul "
   "virtual, fiecare la locul lui. Structura de mai jos este cea din depozitul cursului și din "
   "caiete. <code>curs/</code> este al tău, fără Git; <code>proiect/</code> este al echipei, cu "
   "Git.</p>"
   + ix("folder", "Folderul cursului", {"noduri": NODURI_FOLDER})
   + "<h3>Căile pornesc din folderul caietului</h3>"
   "<p>Căile relative pornesc din directorul de lucru al kernelului, care în VS Code este "
   "implicit folderul caietului, adică <code>curs/</code>; <code>Path.cwd()</code> îl afișează. <code>data/country.csv</code> "
   "înseamnă: din <code>curs/</code>, intră în <code>data/</code>. <code>..</code> înseamnă: "
   "urcă un nivel, deci <code>../proiect</code> înseamnă: din <code>curs/</code>, urcă în "
   "<code>dsw/</code>, apoi intră în <code>proiect/</code>.</p>"
   + ix("sortare", "Trei foldere, șase fișiere", dict(SORTARE_FOLDER, **{
       "sarcina": "Alege un fișier, apoi folderul lui.",
       "laBine": "Fiecare fișier este în folderul potrivit.",
       "laRau": "Ce este al tău stă în curs/, ce este al echipei în proiect/."}))
   + nota("Datele",
          "Fișierul <code>country.csv</code> (0,6 MB) este deja în arhivă, în <code>curs/data/</code>. Vine de pe "
          '<a class="leg" href="https://data.humdata.org/dataset/social-connectedness-index" '
          'target="_blank" rel="noopener">pagina SCI de pe HDX</a>, din lista de resurse; dacă se pierde, '
          f'se descarcă din nou de acolo sau din <a class="leg" href="{repo_fisier("curs/data/country.csv")}" '
          'target="_blank" rel="noopener">depozitul cursului</a>. Fișierul nu se modifică niciodată.'))


sl("s18s", "Proiectul tău", "Unde pui fiecare fișier",
   "<h2>Unde pui fiecare fișier?</h2>"
   + ix("sortare", "Trei foldere, șase fișiere", dict(SORTARE_FOLDER, **{
       "sarcina": "Alege un fișier, apoi folderul lui.",
       "laBine": "Fiecare fișier este în folderul potrivit.",
       "laRau": "Caietele de la curs stau în curs/, datele lor în curs/data/, iar ce face echipa, în proiect/.",
       "explicatie": "<code>curs/</code> e al tău, fără Git. <code>proiect/</code> e al echipei: ce pui "
                     "acolo ajunge, după commit, în istoricul pe care îl vede toată echipa."})),
   manual="")


sl("s19", "Mai departe", "Pentru cursul următor",
   "<h2>La cursul 2: datele vin prin API</h2>"
   '<div class="fin2">'
   '<div class="fin2__flux"><span>codul tău</span><i>→</i><span>cererea</span><i>→</i><span>API-ul</span>'
   "<i>→</i><span>răspunsul JSON</span><i>→</i><span>tabelul</span><i>→</i><span>curs/data/c2</span></div>"
   "<h3>Până atunci</h3>"
   '<ul class="fin2__l">'
   "<li>Folderul <code>dsw</code>, cu <code>.venv</code>, și caietul 01 rulat de sus până jos.</li>"
   '<li>Echipa de cinci, formată, și <a class="leg" href="https://git-scm.com/downloads" target="_blank" rel="noopener">Git</a> instalat.</li>'
   '<li>Contul GitHub, cu care intri pe <a class="leg" href="../../cont/">site</a>.</li>'
   "</ul>"
   '<div class="fin2__a"><a href="../">Pagina cursului 1</a>'
   f'<a href="{REPO_ZIP}">↓ Folderul cursului, ZIP</a>'
   '<a href="../../c2-colectarea-prin-api/">Cursul 2 →</a></div>'
   "</div>")


L.scrie_tot()
