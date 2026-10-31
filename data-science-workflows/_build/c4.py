# -*- coding: utf-8 -*-
"""
Lecția 4: Curățarea datelor.

Urmează prezentarea Curs_4.pptx: Git în practică (staging, commit, undo,
ramuri, depozitul pe GitHub), fluxul complet al lui Git, cât timp ia curățarea
în meseria asta, și cele șase etape ale curățării.

Ce am adăugat peste prezentare, și de ce:
  - fiecare etapă de curățare are un exercițiu cu cod, pentru că o curățare se
    învață scriind-o, nu citind lista etapelor;
  - valorile extreme au un prag pe care îl muți cu mâna, pe datele noastre
    adevărate, ca să se vadă că „1,5 × IQR” e o alegere, nu o lege;
  - dicționarul de date, pentru că fără el curățarea rămâne în capul unuia
    singur și proiectul nu se mai poate reface.

Rulare:  python _build/c4.py
"""

import json
import pathlib

from comun import Lectie, ix, verif, tabel, nota, surse, RAD

L = Lectie(4, "c4-curatarea-datelor", "Curățarea datelor",
           "Git în practică, cele șase etape ale curățării, valorile lipsă, "
           "duplicatele, valorile extreme și dicționarul de date.")
sl = L.sl


# --------------------------------------------------------------------------
# Datele pentru exercițiul cu valori extreme: SCI-ul României cu fiecare țară.
# Adevărate, citite din fișierul pe care îl au și ei. Nu inventez numere, mai
# ales aici: tot rostul exercițiului e să vadă că ce iese „extrem” sunt
# Moldova, Austria și Ungaria, adică exact răspunsul, nu o greșeală.
# --------------------------------------------------------------------------

def valori_sci():
    f = RAD / "date" / "sci-ro-tari.json"
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
    except Exception:
        return []
    return [{"t": x.get("nume") or x["cod"], "v": x["sci"]} for x in d["tari"]]


SCI = valori_sci()


# ===========================================================================
#  1-2. Cursul
# ===========================================================================

AGENDA = [
    ("Git, în practică", "azi", "Staging, commit, anulări, ramuri: comenzile de uz curent."),
    ("De ce este necesară curățarea", "azi", "Ce parte din timpul unui proiect ocupă curățarea și de ce."),
    ("Cele șase etape", "azi", "De la profilare la validarea finală, în ordine."),
    ("Pe datele cursului", "azi", "Fiecare etapă, cu cod, pe datele de migrație colectate la cursul 2."),
    ("Două direcții, un rând", "azi", "Migrația adusă la forma SCI-ului: o pereche pe rând."),
    ("Dicționarul de date", "azi", "Modificările făcute, documentate astfel încât curățarea să poată fi refăcută."),
]

# Pașii pentru lecția 4, din 04_curatarea_si_integrarea_datelor.ipynb.
# Cifrele regionale: rularea caietului 04 pe data/c3/regional.csv (31 octombrie 2026).
# Migrația: Eurostat migr_pop1ctz, 2024.

PAS_PROFIL = {
    "fisier": "04_curatarea.ipynb · 2. Calitatea",
    "intro": "Înainte de orice modificare, tabelul se inspectează. Indicatorii regionali din C3, la nivel NUTS 2.",
    "cod": "regional = pd.read_csv(\"data/c3/regional.csv\")\n"
           "regional = regional[regional[\"nivel\"] == 2]\n\n"
           "print(\"Duplicate:\", regional.duplicated([\"regiune\", \"indicator\"]).sum())\n"
           "print(\"Valori negative:\", (regional[\"valoare\"] < 0).sum())\n\n"
           "regional.groupby(\"indicator\")[\"valoare\"].describe().round(1)\n\n"
           "populatie = regional[regional[\"indicator\"] == \"populatie\"]\n"
           "populatie.nsmallest(3, \"valoare\")",
    "pasi": [
        {"l": 1, "set": {"regional": {"t": "DataFrame", "v": {"cols": ["regiune", "indicator", "valoare"],
            "rows": [["BE10", "populatie", 1264371], ["BE21", "populatie", 1932876], ["…", "…", "…"], ["RO11", "densitate", 74.7]],
            "nota": "format lung: un rând pe regiune și indicator"}}},
         "txt": "Tabelul salvat în C3. Un rând este identificat de două coloane împreună: <b>regiune + indicator</b>."},
        {"l": 2, "txt": "Se păstrează doar nivelul NUTS 2 (în România, regiunile de dezvoltare): nivelul la care există SCI pe regiuni. Județele (NUTS 3) rămân pentru proiectele echipelor."},
        {"l": 4, "out": "Duplicate: 0",
         "txt": "<code>duplicated</code> cu o listă de coloane caută apariția repetată a aceleiași <b>chei</b>. Rezultatul 0 arată că fiecare regiune are fiecare indicator o singură dată."},
        {"l": 5, "out": "Valori negative: 0",
         "txt": "Populația și densitatea nu pot fi negative. Comparația produce True sau False pe fiecare rând; <code>.sum()</code> numără valorile True."},
        {"l": 7, "out": "              count       mean      min        50%         max\n"
                        "densitate     285.0      336.7      3.5      113.9      7827.4\n"
                        "pib_locuitor  276.0    35810.9  11700.0    33550.0    107200.0\n"
                        "populatie     292.0  1913881.4      0.0  1483574.0  15655924.0",
         "txt": "Un rezumat pe indicator (aici, cinci coloane din opt). Două valori ies în evidență: o densitate de 7.827 de locuitori pe km² și o <b>populație 0</b>."},
        {"l": 9, "set": {"populatie": {"t": "DataFrame", "v": {"cols": ["regiune", "valoare", "indicator", "nivel"],
            "rows": [["BE10", 1264371, "populatie", 2], ["BE21", 1932876, "populatie", 2], ["…", "…", "…", "…"]],
            "nota": "doar populația"}}},
         "txt": "Pentru populația 0, se păstrează doar rândurile cu indicatorul populație."},
        {"l": 10, "out": "regiune  valoare\nNO0B         0.0\nFI20     30541.0\nLI00     40015.0",
         "txt": "<code>NO0B</code> este Svalbard, arhipelagul norvegian: Eurostat raportează efectiv 0. Valoarea 7.827 este Bruxelles, un oraș-regiune. Nu sunt erori. De aceea, valorile neobișnuite nu se șterg automat: mai întâi se verifică sursa."},
    ],
}

PAS_CODURI = {
    "fisier": "04_curatarea.ipynb · 6. Migrația: coduri",
    "intro": "Două capcane care nu produc nicio eroare: unele țări se pierd fără avertisment, iar lipsa lor devine vizibilă abia în rezultate.",
    "cod": "gresit = pd.read_csv(\"data/c3/migratie.csv\")\n"
           "migratie = pd.read_csv(\"data/c3/migratie.csv\",\n"
           "                       keep_default_na=False, na_values=[\"\"])\n\n"
           "coduri = {\"EL\": \"GR\", \"UK\": \"GB\"}\n"
           "migratie = migratie.replace({\"tara_rezidenta\": coduri, \"cetatenie\": coduri})\n"
           "print(migratie[\"cetatenie\"].isin([\"EL\", \"UK\"]).sum())",
    "pasi": [
        {"l": 1, "set": {"gresit": {"t": "DataFrame", "v": {"cols": ["tara_rezidenta", "cetatenie", "persoane"],
            "rows": [["DE", "NaN", "…"], ["DE", "EL", 303375], ["ES", "UK", 272402], ["…", "…", "…"]],
            "nota": "Namibia (NA) a devenit NaN"}}},
         "txt": "Citire cu parametrii impliciți. Pandas are o listă de șiruri pe care le interpretează ca valori lipsă, iar <code>NA</code> se află pe ea. Namibienii din Germania au rămas fără cod de țară."},
        {"l": 2, "set": {"migratie": {"t": "DataFrame", "v": {"cols": ["tara_rezidenta", "cetatenie", "persoane"],
            "rows": [["DE", "NA", "…"], ["DE", "EL", 303375], ["ES", "UK", 272402], ["…", "…", "…"]],
            "nota": "NA este din nou Namibia"}}},
         "txt": "<code>keep_default_na=False</code> dezactivează lista implicită; <code>na_values=[\"\"]</code> stabilește că doar celula goală este valoare lipsă. Aceeași setare a fost folosită în C1 pentru SCI."},
        {"l": 5, "set": {"coduri": {"t": "dict", "v": {"EL": "GR", "UK": "GB"}}},
         "txt": "A doua capcană: Eurostat codifică Grecia <code>EL</code> și Regatul Unit <code>UK</code>, iar SCI folosește <code>GR</code> și <code>GB</code>. Un dicționar stabilește corespondența."},
        {"l": 6, "set": {"migratie": {"t": "DataFrame", "v": {"cols": ["tara_rezidenta", "cetatenie", "persoane"],
            "rows": [["DE", "NA", "…"], ["DE", "GR", 303375], ["ES", "GB", 272402], ["…", "…", "…"]],
            "nota": "codurile, ca în SCI"}}},
         "hl": {"var": "coduri", "k": "EL"},
         "txt": "<code>replace</code> primește, pentru fiecare coloană, dicționarul de înlocuiri. Cei 303.375 de greci din Germania nu se mai pierd la join."},
        {"l": 7, "out": "0",
         "txt": "Verificarea ulterioară: nu a rămas niciun cod EL sau UK. Dicționarul <code>coduri</code> documentează și decizia: cine citește codul mai târziu vede de ce Grecia apare ca GR."},
    ],
}

_LUNG = [["RO11", "densitate", 74.7], ["RO12", "densitate", 67.4],
         ["RO11", "pib_locuitor", 28300.0], ["RO12", "pib_locuitor", 28400.0],
         ["RO11", "populatie", 2539784.0], ["RO12", "populatie", 2288061.0]]

PAS_PIVOT = {
    "fisier": "04_curatarea.ipynb · 4. Tabelul regiunilor",
    "intro": "Din format lung în format lat și înapoi, pe două regiuni: Nord-Vest (RO11, care include Clujul) și Centru (RO12).",
    "cod": "lung = regional[regional[\"regiune\"].isin([\"RO11\", \"RO12\"])]\n\n"
           "lat = lung.pivot(index=\"regiune\", columns=\"indicator\", values=\"valoare\")\n"
           "lat = lat.reset_index()\n\n"
           "inapoi = lat.melt(id_vars=\"regiune\", var_name=\"indicator\", value_name=\"valoare\")",
    "pasi": [
        {"l": 1, "set": {"lung": {"t": "DataFrame", "v": {"cols": ["regiune", "indicator", "valoare"], "rows": _LUNG,
            "nota": "lung: 6 rânduri, un rând pe regiune și indicator"}}},
         "txt": "Forma <b>lungă</b>: fiecare regiune apare de trei ori, o dată pentru fiecare indicator."},
        {"l": 3, "set": {"lat": {"t": "DataFrame", "v": {"cols": ["densitate", "pib_locuitor", "populatie"],
            "index": ["RO11", "RO12"], "rows": [[74.7, 28300.0, 2539784.0], [67.4, 28400.0, 2288061.0]],
            "nota": "lat: regiunea a ajuns în index"}}},
         "txt": "<code>pivot</code>: <code>index</code> spune ce devine rând, <code>columns</code> ce devine coloană, <code>values</code> ce se pune în celule. Un rând pe regiune."},
        {"l": 4, "set": {"lat": {"t": "DataFrame", "v": {"cols": ["regiune", "densitate", "pib_locuitor", "populatie"],
            "rows": [["RO11", 74.7, 28300.0, 2539784.0], ["RO12", 67.4, 28400.0, 2288061.0]],
            "nota": "lat: 2 rânduri, regiunea este din nou coloană"}}},
         "txt": "<code>reset_index</code> scoate regiunea din index înapoi într-o coloană obișnuită, ca să poată fi folosită la <code>merge</code>."},
        {"l": 6, "set": {"inapoi": {"t": "DataFrame", "v": {"cols": ["regiune", "indicator", "valoare"], "rows": _LUNG,
            "nota": "din nou 6 rânduri"}}},
         "txt": "<code>melt</code> face operația inversă: coloanele de indicatori se „topesc” (de aici numele) într-o coloană de nume și una de valori. Exercițiul următor aplică această operație."},
    ],
}


sl("s1", "Cursul", "Planul lecției",
   "<h2>Curățarea datelor</h2>"
   "<p class=\"cheie\">Etapa cea mai lungă a unui proiect și cea de care "
   "depinde validitatea întregii analize.</p>"
   + ix("agenda", "Planul lecției",
        {"static": True, "titlu": "Planul lecției",
         "etape": [{"nume": n, "unde": u, "text": d} for n, u, d in AGENDA]},
        "Prima parte: Git. A doua parte: curățarea datelor.")
   + nota("Caietul lecției", "<code>04_curatarea_si_integrarea_datelor.ipynb</code>, secțiunile 1-3 și 6-7: calitatea, acoperirea, codurile de țară.", True),
   manual=
   "<h2>Curățarea datelor</h2>"
   "<p>Lecția are două părți. Prima continuă introducerea în Git din lecția "
   "precedentă cu operațiile necesare în lucrul curent: scoaterea unui fișier "
   "din zona de pregătire, anularea unui commit, ștergerea unei ramuri după "
   "îmbinare. A doua parte tratează curățarea datelor, adică prelucrarea "
   "datelor colectate înainte de orice analiză a rezultatelor.</p>"
   + ix("agenda", "Planul lecției",
        {"static": True, "titlu": "Planul lecției",
         "etape": [{"nume": n, "unde": u, "text": d} for n, u, d in AGENDA]})
   + nota("Caietul lecției", "<code>04_curatarea_si_integrarea_datelor.ipynb</code>, secțiunile 1-3 și 6-7: calitatea, acoperirea, codurile de țară.", True))

sl("s2", "Cursul", "Timpul curățării",
   "<h2>Cum își împart timpul specialiștii în date</h2>"
   + ix("cote", "Un sondaj din 2016",
        {"cote": [
            {"t": "Curățarea și organizarea datelor", "v": 60, "ac": True},
            {"t": "Colectarea datelor", "v": 19},
            {"t": "Căutarea tiparelor în date", "v": 9},
            {"t": "Altele", "v": 5},
            {"t": "Reglarea algoritmilor", "v": 4},
            {"t": "Pregătirea seturilor de antrenament", "v": 3}],
         "sursa": "CrowdFlower, 2016 · răspunsurile unor specialiști în date"},
        "60%: curățarea, nu analiza sau modelarea."),
   manual=
   "<h2>Cât timp ocupă curățarea</h2>"
   "<p>Cifra circulă de zece ani și este una dintre cele mai citate estimări "
   "din domeniu.</p>"
   + ix("cote", "Un sondaj din 2016",
        {"cote": [
            {"t": "Curățarea și organizarea datelor", "v": 60, "ac": True},
            {"t": "Colectarea datelor", "v": 19},
            {"t": "Căutarea tiparelor în date", "v": 9},
            {"t": "Altele", "v": 5},
            {"t": "Reglarea algoritmilor", "v": 4},
            {"t": "Pregătirea seturilor de antrenament", "v": 3}],
         "sursa": "CrowdFlower, 2016"})
   + "<p>Patru cincimi din timp revin colectării și curățării datelor; "
     "aproximativ o zecime, căutării tiparelor, activitatea asociată de obicei "
     "cu această profesie. Nu este o anomalie a domeniului, ci o trăsătură "
     "structurală a lui.</p>")


# ===========================================================================
#  3-7. Git în practică
# ===========================================================================

sl("s3", "Git în practică", "Fluxul complet",
   "<h2>Cele patru zone și trecerile dintre ele</h2>"
   + ix("flux", "Traseul unei modificări",
        {"titlu": "Butonul „Urmărește o schimbare” pornește animația", "intai": {"q": "Un coleg a trimis un commit pe GitHub în această dimineață. Între timp, în depozitul local s-a lucrat, s-a creat un commit și se rulează git push. Ce se întâmplă?", "variante": ["Funcționează: fiecare își trimite modificările", "Este refuzat: mai întâi trebuie adus commit-ul colegului, cu git pull", "Commit-ul colegului se șterge"], "corect": 1, "dupa": "Depozitul de pe GitHub conține un commit care lipsește din depozitul local. Ca acesta să nu se piardă, push-ul este refuzat până când commit-ul este adus local cu pull, adică pe drumul invers."},
         "intro": "Spre GitHub: add, commit, push. Înapoi: fetch și merge, adică pull.",
         "buton": "Urmărește o schimbare",
         "dus": "add → commit → push",
         "intors": "pull: fetch, apoi merge",
         "gata": "modificările locale au ajuns la colaboratori, iar ale lor, în depozitul local",
         "statii": [
             {"n": "Dosarul de lucru", "et": "editare", "ic": "📝", "c": "ceas",
              "d": "Fișierele în starea lor curentă de pe disc. Git le compară cu ultimul commit; modificările nu sunt încă pregătite pentru commit."},
             {"n": "Pregătire", "et": "git add", "ic": "📥", "c": "salvie",
              "d": "Modificările selectate pentru următorul commit. Se pot selecta, de exemplu, trei fișiere din șapte."},
             {"n": "Istoric local", "et": "git commit", "ic": "📦", "c": "accent",
              "d": "Înregistrat definitiv, pe calculatorul propriu. Până aici nu este necesară conexiunea la internet."},
             {"n": "GitHub", "et": "git push", "ic": "☁", "c": "text-2",
              "d": "Copia de pe server. Abia acum lucrul există în două locuri."}]}))

sl("s4", "Git în practică", "Staging și commit",
   "<h2>Comenzile de uz curent</h2>"
   + tabel(["Comanda", "Ce face"], [
       ["~git status", "ce s-a modificat și ce este în pregătire"],
       ["~git pull", "aduce modificările noi; se rulează când <code>git status</code> nu arată modificări"],
       ["~git add .", "adaugă toate modificările în pregătire"],
       ["~git add nume", "adaugă un singur fișier"],
       ["~git reset -- nume", "scoate un fișier din pregătire; rămâne pe disc"],
       ["~git rm --cached nume", "Git nu mai urmărește fișierul, dar acesta rămâne în proiect"],
       ["~git commit -m \"mesaj\"", "înregistrează în istoric"],
       ["~git log --oneline", "istoricul, în formă scurtă"],
       ["~git show &lt;id&gt;", "modificările exacte dintr-un commit"],
   ]),
   manual=
   "<h2>Comenzile de uz curent</h2>"
   + tabel(["Comanda", "Ce face"], [
       ["~git status", "ce s-a modificat și ce este în pregătire"],
       ["~git pull", "aduce modificările noi; se rulează când <code>git status</code> nu arată modificări"],
       ["~git add .", "adaugă toate modificările în pregătire"],
       ["~git add nume", "adaugă un singur fișier"],
       ["~git reset -- nume", "scoate un fișier din pregătire; rămâne pe disc"],
       ["~git rm --cached nume", "Git nu mai urmărește fișierul, dar acesta rămâne în proiect"],
       ["~git commit -m \"mesaj\"", "înregistrează în istoric"],
       ["~git log --oneline", "istoricul, în formă scurtă"],
       ["~git show &lt;id&gt;", "modificările exacte dintr-un commit"],
   ])
   + ix("cod", "Scoaterea unui fișier din pregătire", {
       "id": "c4-cod-staging", "indiciu": "Conținutul zonei de pregătire îl arată comanda folosită cel mai des. Opțiunea care scoate fișierul doar din pregătire, nu și de pe disc, este --cached. Mesajul de commit este la alegere.",
       "iesire": "rm '.env'\n[dev 4f2a9c1] curatare initiala\n 2 files changed, 18 insertions(+)", "fisier": "terminal.sh",
       "sarcina": "După <code>git add .</code>, în pregătire a intrat și <code>.env</code>. "
                  "Cum se scoate fișierul din pregătire înainte de commit?",
       "cod": "# ce este in pregatire\ngit {{1}}\n\n"
              "# scoate .env din pregatire, dar lasa-l pe disc\n"
              "git rm {{2}} .env\n\n"
              "# pentru viitor, fisierul intra in .gitignore\n"
              "echo \".env\" >> .gitignore\n\n"
              "# acum commit-ul se poate face\n"
              "git commit -m {{3}}",
       "goluri": {
           "1": {"ok": ["status"], "ajutor": "comanda"},
           "2": {"ok": ["--cached"], "ajutor": "opțiunea"},
           "3": {"ok": ["\"curatare initiala\"", "'curatare initiala'",
                        "\"colectare\"", "\"primul commit\""],
                 "re": "^[\"'].{3,}[\"']$",
                 "ajutor": "un mesaj, în ghilimele"}},
       "laBine": "Opțiunea esențială este <code>--cached</code>: fără ea, "
                 "<code>git rm</code> șterge fișierul și de pe disc.",
       "laRau": "Opțiunea începe cu două liniuțe. Mesajul se scrie între ghilimele.",
       "explicatie": "<code>git rm --cached</code> scoate fișierul din "
                     "urmărire, dar îl lasă pe disc. Este comportamentul potrivit "
                     "pentru un fișier cu parole: nu mai ajunge în depozit, dar "
                     "rămâne local, astfel încât programul să funcționeze în continuare."}))

sl("s4b", "Git în practică", "Scoaterea din pregătire",
   "<h2>Scoaterea unui fișier din pregătire</h2>"
   + ix("cod", "Scoaterea unui fișier din pregătire", {
       "id": "c4-cod-staging", "indiciu": "Conținutul zonei de pregătire îl arată comanda folosită cel mai des. Opțiunea care scoate fișierul doar din pregătire, nu și de pe disc, este --cached. Mesajul de commit este la alegere.",
       "iesire": "rm '.env'\n[dev 4f2a9c1] curatare initiala\n 2 files changed, 18 insertions(+)", "fisier": "terminal.sh",
       "sarcina": "După <code>git add .</code>, în pregătire a intrat și <code>.env</code>. "
                  "Cum se scoate fișierul din pregătire înainte de commit?",
       "cod": "# ce este in pregatire\ngit {{1}}\n\n"
              "# scoate .env din pregatire, dar lasa-l pe disc\n"
              "git rm {{2}} .env\n\n"
              "# pentru viitor, fisierul intra in .gitignore\n"
              "echo \".env\" >> .gitignore\n\n"
              "# acum commit-ul se poate face\n"
              "git commit -m {{3}}",
       "goluri": {
           "1": {"ok": ["status"], "ajutor": "comanda"},
           "2": {"ok": ["--cached"], "ajutor": "opțiunea"},
           "3": {"ok": ["\"curatare initiala\"", "'curatare initiala'",
                        "\"colectare\"", "\"primul commit\""],
                 "re": "^[\"'].{3,}[\"']$",
                 "ajutor": "un mesaj, în ghilimele"}},
       "laBine": "Opțiunea esențială este <code>--cached</code>: fără ea, "
                 "<code>git rm</code> șterge fișierul și de pe disc.",
       "laRau": "Opțiunea începe cu două liniuțe. Mesajul se scrie între ghilimele.",
       "explicatie": "<code>git rm --cached</code> scoate fișierul din "
                     "urmărire, dar îl lasă pe disc. Este comportamentul potrivit "
                     "pentru un fișier cu parole: nu mai ajunge în depozit, dar "
                     "rămâne local, astfel încât programul să funcționeze în continuare."}),
   manual="")

sl("s5", "Git în practică", "Anulări",
   "<h2>Anularea modificărilor</h2>"
   "<p>Patru situații, patru comenzi diferite. Confuzia dintre ele este o "
   "cauză frecventă de pierdere a lucrului.</p>"
   + ix("prezice", "Anularea unui commit publicat", {
       "id": "c4-prezice-undo", "poarta": False, "fisier": "terminal.sh",
       "cod": "# commit-ul a3f9c21 a stricat tabelul curat,\n"
              "# iar colegii l-au tras deja la ei\n"
              "git ??? a3f9c21",
       "intrebare": "Ce se scrie în locul ??? pentru a corecta eroarea fără a afecta istoricul colegilor?",
       "variante": ["reset --hard", "revert", "restore", "checkout"],
       "corect": 1,
       "indiciu": "Este nevoie de o comandă care lucrează la nivel de commit și adaugă, nu șterge.",
       "laBine": "revert anulează prin adăugarea unui commit, nu prin ștergere.",
       "explicatie": "<code>revert</code> creează un commit nou care inversează modificările; istoricul rămâne intact, iar colegii primesc doar un commit în plus. "
                     "<code>reset --hard</code> mută ramura înapoi și scoate commit-ul din istoricul local; dacă acesta fusese publicat, corectura cere un push forțat, care rescrie istoricul colegilor. "
                     "<code>restore</code> lucrează la nivel de fișier (un fișier modificat greșit sau, cu <code>--staged</code>, un <code>add</code> greșit), "
                     "iar <code>checkout</code> mută poziția curentă în istoric, pentru inspectare, fără să creeze un commit de corecție.",
       "iesire": "[main 7d10e4b] Revert \"curatare: tabel final\"\n 1 file changed"}),
   manual=
   "<h2>Anulări</h2>"
   "<p>Git are reputația unui instrument dificil în mare parte pentru că "
   "oferă patru moduri de a anula o modificare, iar numele lor nu indică "
   "direct ce face fiecare.</p>"
   + ix("prezice", "Anularea unui commit publicat", {
       "id": "c4-prezice-undo", "poarta": False, "fisier": "terminal.sh",
       "cod": "# commit-ul a3f9c21 a stricat tabelul curat,\n"
              "# iar colegii l-au tras deja la ei\n"
              "git ??? a3f9c21",
       "intrebare": "Ce se scrie în locul ??? pentru a corecta eroarea fără a afecta istoricul colegilor?",
       "variante": ["reset --hard", "revert", "restore", "checkout"],
       "corect": 1,
       "indiciu": "Este nevoie de o comandă care lucrează la nivel de commit și adaugă, nu șterge.",
       "laBine": "revert anulează prin adăugarea unui commit, nu prin ștergere.",
       "explicatie": "<code>revert</code> creează un commit nou care inversează modificările; istoricul rămâne intact, iar colegii primesc doar un commit în plus. "
                     "<code>reset --hard</code> mută ramura înapoi și scoate commit-ul din istoricul local; dacă acesta fusese publicat, corectura cere un push forțat, care rescrie istoricul colegilor. "
                     "<code>restore</code> lucrează la nivel de fișier (un fișier modificat greșit sau, cu <code>--staged</code>, un <code>add</code> greșit), "
                     "iar <code>checkout</code> mută poziția curentă în istoric, pentru inspectare, fără să creeze un commit de corecție.",
       "iesire": "[main 7d10e4b] Revert \"curatare: tabel final\"\n 1 file changed"})
   + nota("Regula generală",
          "Dacă eroarea există doar în depozitul local, oricare dintre comenzi "
          "este acceptabilă. Dacă a ajuns pe GitHub și a fost preluată de alții, "
          "singura variantă sigură este <code>revert</code>."))

sl("s6", "Git în practică", "Ramuri, în practică",
   "<h2>Ciclul complet al unei ramuri</h2>"
   + tabel(["Comanda", "Ce face"], [
       ["~git branch", "ramurile locale"],
       ["~git branch -r / -a", "ramurile de pe GitHub / toate"],
       ["~git branch -vv", "fiecare ramură și ramura de la distanță pe care o urmărește (upstream)"],
       ["~git switch -c nume", "creează o ramură și trece pe ea"],
       ["~git switch nume", "trece pe o ramură existentă"],
       ["~git merge nume", "îmbină ramura în ramura curentă"],
       ["~git branch -d nume", "șterge ramura, dacă a fost îmbinată"],
       ["~git branch -D nume", "șterge ramura necondiționat; rar și cu precauție"],
   ])
   + nota("Dacă Git deschide editorul Vim",
          "La <code>git merge</code> sau la <code>git commit</code> fără "
          "<code>-m</code>, Git deschide un editor de text pentru mesaj. Dacă "
          "editorul implicit este Vim, terminalul pare blocat. Pentru a salva "
          "și a ieși: <kbd>Esc</kbd>, apoi <code>:wq</code> și <kbd>Enter</kbd>."))

sl("s7", "Git în practică", "Depozitul pe GitHub",
   "<h2>Recapitulare în două cazuri</h2>"
   + tabel(["Există deja un depozit local", "Nu există niciun depozit"], [
       ["se creează un depozit gol pe GitHub", "se creează depozitul pe GitHub"],
       ["<code>git remote add origin &lt;url&gt;</code>", "<code>git clone &lt;url&gt;</code>"],
       ["<code>git push -u origin main</code>", "depozitul clonat este deja legat de GitHub"],
   ]))


# ===========================================================================
#  8-9. Curățarea: harta
# ===========================================================================

ORD_CUR = {
 "id": "c4-ordine-curatare",
 "poarta": False,
 "sarcina": "Șase etape, în ordine aleatorie. Care este succesiunea în care se efectuează? La o ordine greșită, se afișează consecința.",
 "linii": [
  "Profilare: inspecția datelor, fără modificarea lor",
  "Integrare: aducerea codurilor la aceeași formă (EL devine GR)",
  "Curățare de bază: eliminarea duplicatelor",
  "Valori lipsă și anomalii: alegerea tratamentului",
  "Transformări: pivot, rate, variabile noi",
  "Validare: comparația înainte și după, documentarea deciziilor"
 ],
 "consecinte": {
  "0": "Profilarea vine prima: fără ea, deciziile nu au o bază. Nu se știe încă câte valori lipsă există, nici că NA înseamnă Namibia.",
  "1": "Codurile se aliniază înaintea eliminării duplicatelor: cât timp Grecia apare și ca EL, și ca GR, dublura nu este detectată.",
  "2": "Duplicatele se elimină înaintea tratării valorilor lipsă: altfel media folosită la completare se calculează pe rânduri numărate de două ori.",
  "3": "Valorile lipsă se tratează înainte de transformări: după un pivot, o singură lipsă se poate extinde în mai multe coloane, iar originea ei nu mai este evidentă.",
  "4": "Transformările vin după curățare: altfel se calculează rate pe valori care urmează să fie modificate.",
  "5": "Validarea încheie procesul: compară tabelul final cu cel inițial. Aplicată mai devreme, nu are încă un rezultat final de comparat."
 },
 "indiciu": "Pentru fiecare etapă: ce informații trebuie să existe deja pentru a o putea efectua?",
 "laBine": "Fiecare etapă se sprijină pe rezultatele celei anterioare.",
 "explicatie": "Ordinea nu este o convenție: fiecare etapă presupune rezultatele celei anterioare. Fără profilare, toate deciziile ulterioare sunt luate fără temei."
}

ETAPE_CUR = [
    ("1. Profilare", "înțelegerea datelor",
     "Se verifică tipurile, distribuțiile, valorile lipsă și valorile suspecte. "
     "Se identifică erorile evidente și problemele de structură. Datele nu se modifică încă."),
    ("2. Integrare și standardizare", "alinierea surselor",
     "Sursele diferite se aduc la aceeași formă: etichete, formate, unități, "
     "tipuri. Se corectează textul, codurile și convențiile."),
    ("3. Curățare de bază", "eliminarea redundanțelor",
     "Se elimină ce este irelevant sau redundant, inclusiv duplicatele, și se "
     "corectează erorile structurale și categoriile incoerente."),
    ("4. Valori lipsă și anomalii", "alegerea tratamentului",
     "Se analizează valorile lipsă și se stabilește modul de tratare. Se examinează "
     "valorile extreme sau imposibile. Se verifică regulile logice."),
    ("5. Transformări", "pregătirea analizei",
     "Se reorganizează structura (format lung sau lat), se fac agregări, se construiesc "
     "variabile noi, se aplică scalări și se adaugă informații externe."),
    ("6. Validare și documentare", "încheierea",
     "Se verifică unicitatea cheilor și coerența. Se compară statisticile dinainte și "
     "de după. Se documentează transformările, versiunile și dicționarul de date."),
]

sl("s8", "Curățarea", "Cele șase etape",
   "<h2>De la date brute la date fiabile</h2>"
   + ix("ordine", "Harta curățării", ORD_CUR)
   + "<p class=\"cheie\">Prima etapă nu modifică nimic: doar inspectează "
     "datele. Este și etapa omisă cel mai des.</p>",
   manual=
   "<h2>Cele șase etape</h2>"
   "<p>Curățarea nu este o colecție de procedee independente, ci un proces cu "
   "o ordine stabilă. Fiecare etapă presupune rezultatele celei anterioare.</p>"
   + ix("etape", "Harta curățării",
        {"titlu": "Șase etape, în ordine", "intro": "Detaliile apar la selectarea unei etape.",
         "etape": [{"nume": n, "unde": u, "text": d} for n, u, d in ETAPE_CUR]})
   + ix("ordine", "Ordonarea etapelor", ORD_CUR)
   + nota("De ce este omisă profilarea",
          "Pentru că nu produce un rezultat vizibil: după o oră de profilare, "
          "fișierul este neschimbat. Fără ea însă, deciziile ulterioare se iau "
          "fără temei, iar unele sunt ireversibile."))

sl("s9", "Curățarea", "Profilarea",
   "<h2>Prima etapă: inspecția datelor</h2>"
   + ix("pas", "Inspecția înaintea modificării", PAS_PROFIL)
   + verif("c4-v6", 3,
           "<code>info()</code> arată o coloană de prețuri ca "
           "<code>object</code>, nu ca număr. Ce înseamnă?",
           ["Fișierul este corupt",
            "Pandas nu poate reprezenta prețuri",
            "Valorile sunt prea mari",
            "Coloana conține cel puțin o valoare nenumerică"],
           "Pandas a găsit cel puțin o valoare pe care nu o poate interpreta ca "
           "număr: o virgulă zecimală, un spațiu, o cratimă „-” pusă în locul unei valori lipsă. O "
           "singură valoare nevalidă din zece mii este suficientă pentru ca "
           "întreaga coloană să fie citită ca text."),
   manual=
   "<h2>Prima etapă: inspecția datelor</h2>"
   + ix("pas", "Inspecția înaintea modificării", PAS_PROFIL)
   + ix("cod", "Profilarea tabelului", {
       "id": "c4-cod-profil", "indiciu": "Rezumatul pe coloane înseamnă „informații” (info). Statisticile numerice sunt o „descriere” (describe). Valorile distincte, cu frecvența lor, se numără cu value_counts.",
       "iesire": "(5104, 3)\n          valoare\ncount     4292.0\nmean     18736.2\n...\nRO    37\nPL    37\nBG    36", "fisier": "profilare.py",
       "sarcina": "Cinci întrebări de pus oricărui tabel nou, înainte de "
                  "orice modificare.",
       "cod": "import pandas as pd\n\n"
              "d = pd.read_csv(\"date/brute/migratie.csv\")\n\n"
              "# 1. dimensiunea tabelului\nprint(d.shape)\n\n"
              "# 2. ce coloane, ce tipuri, cate valori non-nule\n"
              "d.{{1}}()\n\n"
              "# 3. cum arata numeric: medie, minim, maxim, cuartile\n"
              "print(d.{{2}}())\n\n"
              "# 4. cate lipsuri, pe coloana\n"
              "print(d.isna().sum())\n\n"
              "# 5. ce valori distincte are o coloana categoriala\n"
              "print(d[\"citizen\"].{{3}}())",
       "goluri": {
           "1": {"ok": ["info"], "ajutor": "metoda"},
           "2": {"ok": ["describe"], "ajutor": "metoda"},
           "3": {"ok": ["value_counts", "unique"], "ajutor": "metoda"}},
       "laBine": "Cele cinci verificări se fac în această ordine, pe orice tabel nou.",
       "laRau": "Toate trei sunt metode, deci se scriu fără ghilimele și cu paranteze.",
       "explicatie": "<code>value_counts()</code> este metoda potrivită pentru "
                     "coloanele categoriale. Pe datele de migrație scoate la "
                     "iveală o problemă: Namibia lipsește, deși Eurostat o "
                     "raportează. Pandas a citit codul ei, <code>NA</code>, ca "
                     "valoare lipsă. Corecția apare pe slide-ul următor."})
   + verif("c4-v6", 3,
           "<code>info()</code> arată o coloană de prețuri ca "
           "<code>object</code>, nu ca număr. Ce înseamnă?",
           ["Fișierul este corupt",
            "Pandas nu poate reprezenta prețuri",
            "Valorile sunt prea mari",
            "Coloana conține cel puțin o valoare nenumerică"],
           "Pandas a găsit cel puțin o valoare pe care nu o poate interpreta ca "
           "număr: o virgulă zecimală, un spațiu, o cratimă „-” pusă în locul unei valori lipsă. O "
           "singură valoare nevalidă din zece mii este suficientă pentru ca "
           "întreaga coloană să fie citită ca text."))

sl("s9b", "Curățarea", "Profilarea tabelului",
   "<h2>Profilarea tabelului</h2>"
   + ix("cod", "Profilarea tabelului", {
       "id": "c4-cod-profil", "indiciu": "Rezumatul pe coloane înseamnă „informații” (info). Statisticile numerice sunt o „descriere” (describe). Valorile distincte, cu frecvența lor, se numără cu value_counts.",
       "iesire": "(5104, 3)\n          valoare\ncount     4292.0\nmean     18736.2\n...\nRO    37\nPL    37\nBG    36", "fisier": "profilare.py",
       "sarcina": "Cinci întrebări de pus oricărui tabel nou, înainte de "
                  "orice modificare.",
       "cod": "import pandas as pd\n\n"
              "d = pd.read_csv(\"date/brute/migratie.csv\")\n\n"
              "# 1. dimensiunea tabelului\nprint(d.shape)\n\n"
              "# 2. ce coloane, ce tipuri, cate valori non-nule\n"
              "d.{{1}}()\n\n"
              "# 3. cum arata numeric: medie, minim, maxim, cuartile\n"
              "print(d.{{2}}())\n\n"
              "# 4. cate lipsuri, pe coloana\n"
              "print(d.isna().sum())\n\n"
              "# 5. ce valori distincte are o coloana categoriala\n"
              "print(d[\"citizen\"].{{3}}())",
       "goluri": {
           "1": {"ok": ["info"], "ajutor": "metoda"},
           "2": {"ok": ["describe"], "ajutor": "metoda"},
           "3": {"ok": ["value_counts", "unique"], "ajutor": "metoda"}},
       "laBine": "Cele cinci verificări se fac în această ordine, pe orice tabel nou.",
       "laRau": "Toate trei sunt metode, deci se scriu fără ghilimele și cu paranteze.",
       "explicatie": "<code>value_counts()</code> este metoda potrivită pentru "
                     "coloanele categoriale. Pe datele de migrație scoate la "
                     "iveală o problemă: Namibia lipsește, deși Eurostat o "
                     "raportează. Pandas a citit codul ei, <code>NA</code>, ca "
                     "valoare lipsă. Corecția apare pe slide-ul următor."}),
   manual="")


# ===========================================================================
#  10-12. Standardizare, duplicate, structuri
# ===========================================================================

sl("s10", "Curățarea", "Coduri incompatibile",
   "<h2>Aceeași țară, alt cod</h2>"
   + tabel(["Țara", "SCI", "Eurostat", "Ce se întâmplă"], [
       ["Grecia", "~GR", "~EL", "se pierde la join, fără eroare"],
       ["Regatul Unit", "~GB", "~UK", "la fel"],
       ["Namibia", "~NA", "~NA", "pandas o citește ca valoare lipsă"],
   ])
   + ix("pas", "Două erori fără avertisment", PAS_CODURI),
   manual="<h2>Standardizarea codurilor</h2>"
   "<p>Când se combină două surse, aceeași țară poate avea coduri diferite. "
   "Eurostat folosește <code>EL</code> pentru Grecia și <code>UK</code> "
   "pentru Regatul Unit; Meta folosește codurile ISO, <code>GR</code> și "
   "<code>GB</code>. Pentru program sunt țări diferite, iar un join pe "
   "coduri le pierde fără niciun mesaj de eroare.</p>"
   "<p>A doua capcană este mai greu de observat: Namibia are codul "
   "<code>NA</code>, iar pandas citește <code>NA</code> ca valoare lipsă. "
   "Rândurile Namibiei nu dispar, dar codul lor devine valoare lipsă, iar "
   "orice filtru sau join pe țară le pierde.</p>"
   + tabel(["Țara", "SCI", "Eurostat", "Ce se întâmplă"], [
       ["Grecia", "~GR", "~EL", "se pierde la join, fără eroare"],
       ["Regatul Unit", "~GB", "~UK", "la fel"],
       ["Namibia", "~NA", "~NA", "pandas o citește ca valoare lipsă"],
   ])
   + ix("pas", "Două erori fără avertisment", PAS_CODURI)
   + ix("cod", "Repararea codurilor", {
       "id": "c4-cod-standard", "indiciu": "Pentru ca NA (Namibia) să nu devină valoare lipsă, lista implicită de valori lipsă se dezactivează: keep_default_na primește valoarea logică „fals”. Codul Regatului Unit în SCI este GB. Metoda care înlocuiește valori pe baza unui dicționar este replace.",
       "iesire": "0", "fisier": "standardizare.py",
       "sarcina": "Citirea fișierului fără pierderea Namibiei și alinierea codurilor.",
       "cod": "d = pd.read_csv(\"date/brute/migratie.csv\",\n"
              "                keep_default_na={{1}}, na_values=[\"\"])\n\n"
              "coduri = {\"EL\": \"GR\", \"UK\": {{2}}}\n"
              "d[\"citizen\"] = d[\"citizen\"].{{3}}(coduri)\n"
              "d[\"geo\"] = d[\"geo\"].replace(coduri)",
       "goluri": {
           "1": {"ok": ["False"], "ajutor": "valoarea"},
           "2": {"ok": ["\"GB\"", "'GB'"], "ajutor": "codul"},
           "3": {"ok": ["replace"], "ajutor": "metoda"}},
       "laBine": "Migrația și SCI-ul folosesc acum aceleași coduri.",
       "laRau": "Primul gol este o valoare logică. Codul este un șir de caractere, între ghilimele.",
       "explicatie": "Dicționarul <code>coduri</code> documentează decizia."})
   + nota("Aceeași regulă și pentru SCI",
          "Fișierul <code>country.csv</code> conține și el Namibia. Se citește "
          "tot cu <code>keep_default_na=False</code>; altfel, perechile "
          "Namibiei se pierd."))

sl("s10b", "Curățarea", "Repararea codurilor",
   "<h2>Repararea codurilor</h2>"
   + ix("cod", "Repararea codurilor", {
       "id": "c4-cod-standard", "indiciu": "Pentru ca NA (Namibia) să nu devină valoare lipsă, lista implicită de valori lipsă se dezactivează: keep_default_na primește valoarea logică „fals”. Codul Regatului Unit în SCI este GB. Metoda care înlocuiește valori pe baza unui dicționar este replace.",
       "iesire": "0", "fisier": "standardizare.py",
       "sarcina": "Citirea fișierului fără pierderea Namibiei, apoi alinierea "
                  "codurilor Eurostat la cele din SCI.",
       "cod": "# NA este Namibia, nu o valoare lipsa: lipsa este doar celula goala\n"
              "d = pd.read_csv(\"date/brute/migratie.csv\",\n"
              "                keep_default_na={{1}}, na_values=[\"\"])\n\n"
              "# Eurostat scrie altfel doua tari; codurile se aliniaza la SCI\n"
              "coduri = {\"EL\": \"GR\", \"UK\": {{2}}}\n"
              "d[\"citizen\"] = d[\"citizen\"].{{3}}(coduri)\n"
              "d[\"geo\"] = d[\"geo\"].replace(coduri)\n\n"
              "print(d[\"citizen\"].isin([\"EL\", \"UK\"]).sum())   # 0",
       "goluri": {
           "1": {"ok": ["False"], "ajutor": "valoarea"},
           "2": {"ok": ["\"GB\"", "'GB'"], "ajutor": "codul"},
           "3": {"ok": ["replace"], "ajutor": "metoda"}},
       "laBine": "Nu mai există rânduri cu EL sau UK: migrația și SCI-ul "
                 "folosesc acum aceleași coduri.",
       "laRau": "Primul gol este o valoare logică. Codul este un șir de caractere, între ghilimele.",
       "explicatie": "Dicționarul <code>coduri</code> documentează decizia: "
                     "oricine citește codul mai târziu află din el că EL și GR "
                     "au fost tratate ca aceeași țară. Fără el, Grecia ar "
                     "dispărea la primul join, fără o explicație vizibilă."}),
   manual="")

sl("s11", "Curățarea", "Duplicatele",
   "<h2>Același rând, de două ori</h2>"
   "<p>Provin din colectări reluate, din îmbinări greșite sau din exporturi "
   "repetate. Un duplicat nu este vizibil în medie, dar o modifică.</p>"
   + ix("cod", "Eliminarea duplicatelor", {
       "id": "c4-cod-duplicate", "indiciu": "Metoda care marchează rândurile repetate este duplicated. Se păstrează prima apariție: \"first\". Cheia este perechea de coloane citizen și geo, sub formă de listă.",
       "iesire": "584\n0", "fisier": "duplicate.py",
       "sarcina": "Numărarea duplicatelor, apoi eliminarea lor, cu păstrarea primei apariții.",
       "cod": "# cate randuri sunt identice cu altul de mai sus\n"
              "print(d.{{1}}().sum())\n\n"
              "# eliminarea lor, cu pastrarea primei aparitii\n"
              "d = d.drop_duplicates(keep={{2}})\n\n"
              "# uneori duplicatul nu este pe tot randul, ci pe cheie\n"
              "# o pereche cetatenie-tara nu are voie sa apara de doua ori\n"
              "print(d.duplicated(subset={{3}}).sum())",
       "goluri": {
           "1": {"ok": ["duplicated"], "ajutor": "metoda"},
           "2": {"ok": ["\"first\"", "'first'"], "ajutor": "care rămâne"},
           "3": {"ok": ["[\"citizen\", \"geo\"]", "['citizen','geo']", "[\"citizen\",\"geo\"]",
                        "['citizen', 'geo']"],
                 "re": "^\\[\\s*[\"']citizen[\"']\\s*,\\s*[\"']geo[\"']\\s*\\]$",
                 "ajutor": "lista de coloane"}},
       "laBine": "Al doilea caz este cel problematic: rânduri care diferă "
                 "printr-o coloană secundară, dar descriu aceeași observație.",
       "laRau": "Primul gol este o metodă. Al doilea este un șir de caractere, "
                "între ghilimele. Al treilea este o listă de nume de coloane.",
       "explicatie": "<code>drop_duplicates()</code> fără <code>subset</code> "
                     "compară tot rândul. La date diadice, cheia este perechea: "
                     "dacă aceeași pereche de locuri apare de două ori cu "
                     "valori diferite, problema ține de colectare, nu de "
                     "curățare, iar originea ei trebuie identificată înainte "
                     "de orice eliminare."}))

# ===========================================================================
#  13-15. Lipsuri și valori extreme
# ===========================================================================

sl("s13", "Valori lipsă și extreme", "Tratarea valorilor lipsă",
   "<h2>Valorile lipsă nu sunt toate de același tip</h2>"
   "<p>Înainte de alegerea unei metode, întrebarea este <em>de ce</em> lipsesc valorile.</p>"
   + ix("sortare", "Tratamentul potrivit fiecărui caz", {
       "id": "c4-sort-lipsuri", "poarta": False,
       "sarcina": "Care este tratamentul adecvat pentru fiecare situație?",
       "elemente": [
           {"t": "3 rânduri din 30.000, la întâmplare", "cos": 0},
           {"t": "O coloană goală în proporție de 80%", "cos": 1},
           {"t": "Polonia nu raportează deloc migranții", "cos": 2},
           {"t": "Serie de timp, lipsește un an la mijloc", "cos": 3}],
       "cosuri": [
           {"t": "Eliminarea rândurilor", "d": "sunt puține și nu par sistematice"},
           {"t": "Eliminarea coloanei", "d": "conține prea puțină informație"},
           {"t": "Păstrarea și documentarea", "d": "lipsa însăși este informativă"},
           {"t": "Completarea din valorile vecine", "d": "interpolare sau ultima valoare cunoscută"}],
       "laBine": "Al treilea caz este cel relevant pentru datele cursului: "
                 "Polonia, Danemarca, Grecia și Croația nu raportează. Lipsa are "
                 "un tipar, deci se păstrează ca valoare lipsă și se documentează. "
                 "Nu înseamnă zero străini în Polonia.",
       "explicatie": "Completarea cu media este metoda cea mai răspândită și "
                     "cea mai riscantă: reduce artificial variația și face "
                     "rezultatele să pară mai precise decât sunt. Dacă este "
                     "folosită, trebuie menționată în raport."}))

sl("s14", "Valori lipsă și extreme", "Valorile lipsă, în cod",
   "<h2>Valorile lipsă în pandas</h2>"
   + ix("prezice", "Media și valorile lipsă", {
       "id": "c4-prezice-nan", "fisier": "04_curatarea.ipynb",
       "cod": "import pandas as pd\n\n"
              "s = pd.Series([10, None, 30])\n"
              "print(s.mean(), s.isna().sum())",
       "intrebare": "Ce afișează?",
       "variante": ["13.33 0", "20.0 1", "NaN 1", "Eroare"],
       "corect": 1,
       "indiciu": "pandas ignoră valorile lipsă la calculul mediei. Câte valori lipsesc?",
       "laBine": "Media se calculează din valorile existente: (10 + 30) / 2.",
       "explicatie": "<code>None</code> devine <code>NaN</code>, iar <code>mean()</code> îl ignoră: "
                     "media este calculată din două valori, nu din trei. Comportamentul este comod, dar riscant: "
                     "dacă lipsesc tocmai valorile mari sau cele mici, media se deplasează fără niciun avertisment. "
                     "De aceea valorile lipsă se numără întâi, cu <code>isna().sum()</code>."}),
   manual=
   "<h2>Valorile lipsă în pandas</h2>"
   + ix("prezice", "Media și valorile lipsă", {
       "id": "c4-prezice-nan", "fisier": "04_curatarea.ipynb",
       "cod": "import pandas as pd\n\n"
              "s = pd.Series([10, None, 30])\n"
              "print(s.mean(), s.isna().sum())",
       "intrebare": "Ce afișează?",
       "variante": ["13.33 0", "20.0 1", "NaN 1", "Eroare"],
       "corect": 1,
       "indiciu": "pandas ignoră valorile lipsă la calculul mediei. Câte valori lipsesc?",
       "laBine": "Media se calculează din valorile existente: (10 + 30) / 2.",
       "explicatie": "<code>None</code> devine <code>NaN</code>, iar <code>mean()</code> îl ignoră: "
                     "media este calculată din două valori, nu din trei. Comportamentul este comod, dar riscant: "
                     "dacă lipsesc tocmai valorile mari sau cele mici, media se deplasează fără niciun avertisment. "
                     "De aceea valorile lipsă se numără întâi, cu <code>isna().sum()</code>."})
   + ix("cod", "Tratarea valorilor lipsă", {
       "id": "c4-cod-lipsuri", "indiciu": "Valorile lipsă se identifică cu isna. Mediana este median. „Forward fill”, adică preluarea valorii anterioare, se scrie ffill.",
       "iesire": "5104 4292 0", "fisier": "lipsuri.py",
       "sarcina": "Numărarea valorilor lipsă, apoi trei strategii de tratare, "
                  "fiecare potrivită altei situații.",
       "cod": "# cate lipsuri, pe coloana\nprint(d.{{1}}().sum())\n\n"
              "# cazul 1: putine si imprastiate, se elimina\n"
              "d1 = d.dropna(subset=[\"valoare\"])\n\n"
              "# cazul 2: completare cu mediana, mai robusta decat media\n"
              "d2 = d.copy()\n"
              "d2[\"valoare\"] = d2[\"valoare\"].fillna(d2[\"valoare\"].{{2}}())\n\n"
              "# cazul 3: serie de timp, ultima valoare cunoscuta\n"
              "d3 = d.sort_values(\"an\")\n"
              "d3[\"valoare\"] = d3[\"valoare\"].{{3}}()\n\n"
              "print(len(d), len(d1), d2[\"valoare\"].isna().sum())",
       "goluri": {
           "1": {"ok": ["isna", "isnull"], "ajutor": "metoda"},
           "2": {"ok": ["median"], "ajutor": "statistica"},
           "3": {"ok": ["ffill"], "ajutor": "metoda"}},
       "laBine": "Mediana, nu media: o singură valoare extremă deplasează "
                 "media, dar nu afectează mediana.",
       "laRau": "Primul și al treilea gol sunt metode fără argumente. Al doilea "
                "este o statistică, calculată tot printr-o metodă.",
       "explicatie": "<code>ffill</code> propagă ultima valoare cunoscută. "
                     "Este justificat la serii de timp, unde anul lipsă "
                     "seamănă cu cel anterior, și nejustificat la date fără "
                     "ordine, unde „rândul anterior” nu are semnificație."}))

sl("s14b", "Valori lipsă și extreme", "Tratarea valorilor lipsă",
   "<h2>Tratarea valorilor lipsă</h2>"
   + ix("cod", "Tratarea valorilor lipsă", {
       "id": "c4-cod-lipsuri", "indiciu": "Valorile lipsă se identifică cu isna. Mediana este median. „Forward fill”, adică preluarea valorii anterioare, se scrie ffill.",
       "iesire": "5104 4292 0", "fisier": "lipsuri.py",
       "sarcina": "Numărarea valorilor lipsă, apoi trei strategii de tratare, "
                  "fiecare potrivită altei situații.",
       "cod": "# cate lipsuri, pe coloana\nprint(d.{{1}}().sum())\n\n"
              "# cazul 1: putine si imprastiate, se elimina\n"
              "d1 = d.dropna(subset=[\"valoare\"])\n\n"
              "# cazul 2: completare cu mediana, mai robusta decat media\n"
              "d2 = d.copy()\n"
              "d2[\"valoare\"] = d2[\"valoare\"].fillna(d2[\"valoare\"].{{2}}())\n\n"
              "# cazul 3: serie de timp, ultima valoare cunoscuta\n"
              "d3 = d.sort_values(\"an\")\n"
              "d3[\"valoare\"] = d3[\"valoare\"].{{3}}()\n\n"
              "print(len(d), len(d1), d2[\"valoare\"].isna().sum())",
       "goluri": {
           "1": {"ok": ["isna", "isnull"], "ajutor": "metoda"},
           "2": {"ok": ["median"], "ajutor": "statistica"},
           "3": {"ok": ["ffill"], "ajutor": "metoda"}},
       "laBine": "Mediana, nu media: o singură valoare extremă deplasează "
                 "media, dar nu afectează mediana.",
       "laRau": "Primul și al treilea gol sunt metode fără argumente. Al doilea "
                "este o statistică, calculată tot printr-o metodă.",
       "explicatie": "<code>ffill</code> propagă ultima valoare cunoscută. "
                     "Este justificat la serii de timp, unde anul lipsă "
                     "seamănă cu cel anterior, și nejustificat la date fără "
                     "ordine, unde „rândul anterior” nu are semnificație."}),
   manual="")

sl("s15", "Valori lipsă și extreme", "Valorile extreme",
   "<h2>Unde se fixează pragul?</h2>"
   "<p>Regula uzuală: se marchează tot ce depășește Q3 plus de 1,5 ori "
   "intervalul intercuartilic. Efectul pragului se observă prin deplasarea lui.</p>"
   + ix("prag", "Pe datele SCI", {
       "id": "c4-prag",
       "sarcina": "Legătura socială a României cu fiecare dintre cele 177 de "
                  "țări din set, cu prag ajustabil.",
       "valori": SCI,
       "intrebare": "Țările marcate sunt greșeli de date?",
       "laBine": "În frunte: Republica Moldova, Austria, Germania, Ungaria, Irlanda, Italia, adică diaspora și "
                 "vecinătatea. Nu sunt erori, ci chiar fenomenul studiat. "
                 "Eliminate ca „valori extreme”, ar dispărea exact observațiile "
                 "care trebuie explicate.",
       "laRau": "În fruntea țărilor marcate sunt Republica Moldova, Austria, Germania și Ungaria: "
                "diaspora și vecinătatea, adică fenomenul studiat. O valoare "
                "extremă statistic nu este automat o eroare."})
   + nota("Când o valoare extremă este o eroare",
          "Atunci când este imposibilă: o vârstă de 210 ani, un procent de 140, "
          "o dată din 1900 într-un set despre 2020. Pentru astfel de cazuri nu "
          "este nevoie de IQR, ci de o regulă logică formulată explicit."),
   manual=
   "<h2>Valorile extreme</h2>"
   "<p>Metoda clasică este regula intervalului intercuartilic: se calculează "
   "primul și al treilea cuartil, se ia diferența dintre ele și se marchează "
   "tot ce depășește Q3 plus de 1,5 ori această diferență.</p>"
   "<pre><code>q1 = d[\"sci\"].quantile(0.25)\n"
   "q3 = d[\"sci\"].quantile(0.75)\niqr = q3 - q1\n"
   "prag = q3 + 1.5 * iqr\n"
   "extreme = d[d[\"sci\"] &gt; prag]</code></pre>"
   "<p>Factorul 1,5 este o convenție, nu o constantă derivată teoretic. Cu un "
   "prag mai jos apar mai multe „valori extreme”; cu unul suficient de sus, "
   "niciuna.</p>"
   + ix("prag", "Pe datele SCI", {
       "id": "c4-prag",
       "sarcina": "Legătura socială a României cu fiecare țară din set, cu prag ajustabil.",
       "valori": SCI,
       "intrebare": "Țările marcate sunt greșeli de date?",
       "laBine": "În frunte: Republica Moldova, Austria, Germania, Ungaria. Nu sunt erori, "
                 "ci chiar fenomenul studiat.",
       "laRau": "Țările marcate reprezintă diaspora și vecinătatea, adică "
                "fenomenul studiat."})
   + nota("Distincția esențială",
          "O valoare <em>extremă</em> este departe de restul distribuției. O "
          "valoare <em>greșită</em> este imposibilă. Prima se păstrează și se "
          "explică; a doua se corectează sau se elimină. Confuzia dintre ele "
          "poate duce la eliminarea tocmai a rezultatului relevant."))


# ===========================================================================
#  16-18. Transformări și validare
# ===========================================================================

sl("s16", "Transformări", "Lung sau lat",
   "<h2>Aceleași date, două forme</h2>"
   + tabel(["Lat (wide)", "Lung (long)"], [
       ["o coloană pe an", "o coloană „an” și una „valoare”"],
       ["potrivit pentru citire directă", "potrivit pentru calcule și grafice"],
       ["<code>2020, 2021, 2022</code> ca nume de coloane", "anul devine o valoare"],
   ])
   + ix("pas", "Din lung în lat și înapoi", PAS_PIVOT),
   manual=
   "<h2>Aceleași date, două forme</h2>"
   + tabel(["Lat (wide)", "Lung (long)"], [
       ["o coloană pe an", "o coloană „an” și una „valoare”"],
       ["potrivit pentru citire directă", "potrivit pentru calcule și grafice"],
       ["<code>2020, 2021, 2022</code> ca nume de coloane", "anul devine o valoare"],
   ])
   + ix("pas", "Din lung în lat și înapoi", PAS_PIVOT)
   + ix("cod", "Trecerea din lat în lung", {
       "id": "c4-cod-melt", "indiciu": "Din lat în lung: tabelul se „topește”, cu melt. Înapoi, din lung în lat: tabelul se „rotește”, cu pivot.",
       "iesire": "   tara    an  valoare  pe_locuitor\n0    RO  2022   1044.0     0.000055\n1    IT  2022   5030.0     0.000085", "fisier": "forma.py",
       "sarcina": "Transformarea tabelului cu o coloană pe an într-unul cu un "
                  "rând pe țară și an.",
       "cod": "# din lat in lung: anii devin valori intr-o coloana\n"
              "lung = d.{{1}}(id_vars=[\"tara\"], var_name=\"an\",\n"
              "                value_name=\"valoare\")\n\n"
              "# si inapoi, la nevoie\n"
              "lat = lung.{{2}}(index=\"tara\", columns=\"an\", values=\"valoare\")\n\n"
              "# o variabila noua, calculata\n"
              "lung[\"pe_locuitor\"] = lung[\"valoare\"] / lung[\"populatie\"]\n"
              "print(lung.head())",
       "goluri": {
           "1": {"ok": ["melt"], "ajutor": "metoda"},
           "2": {"ok": ["pivot"], "ajutor": "metoda"}},
       "laBine": "Forma lungă este cea folosită în aproape toate etapele "
                 "următoare: agregări, grafice, modele.",
       "laRau": "Ambele sunt metode ale obiectului DataFrame.",
       "explicatie": "Anul nu este o proprietate a țării, ci un atribut al "
                     "observației. Când anul este nume de coloană, nu se poate "
                     "filtra sau grupa după el, iar fiecare an nou cere o "
                     "coloană nouă. În forma lungă, anul este o valoare ca "
                     "oricare alta."}))

sl("s16m", "Transformări", "Din lat în lung",
   "<h2>Trecerea din lat în lung</h2>"
   + ix("cod", "Trecerea din lat în lung", {
       "id": "c4-cod-melt", "indiciu": "Din lat în lung: tabelul se „topește”, cu melt. Înapoi, din lung în lat: tabelul se „rotește”, cu pivot.",
       "iesire": "   tara    an  valoare  pe_locuitor\n0    RO  2022   1044.0     0.000055\n1    IT  2022   5030.0     0.000085", "fisier": "forma.py",
       "sarcina": "Transformarea tabelului cu o coloană pe an într-unul cu un "
                  "rând pe țară și an.",
       "cod": "# din lat in lung: anii devin valori intr-o coloana\n"
              "lung = d.{{1}}(id_vars=[\"tara\"], var_name=\"an\",\n"
              "                value_name=\"valoare\")\n\n"
              "# si inapoi, la nevoie\n"
              "lat = lung.{{2}}(index=\"tara\", columns=\"an\", values=\"valoare\")\n\n"
              "# o variabila noua, calculata\n"
              "lung[\"pe_locuitor\"] = lung[\"valoare\"] / lung[\"populatie\"]\n"
              "print(lung.head())",
       "goluri": {
           "1": {"ok": ["melt"], "ajutor": "metoda"},
           "2": {"ok": ["pivot"], "ajutor": "metoda"}},
       "laBine": "Forma lungă este cea folosită în aproape toate etapele "
                 "următoare: agregări, grafice, modele.",
       "laRau": "Ambele sunt metode ale obiectului DataFrame.",
       "explicatie": "Anul nu este o proprietate a țării, ci un atribut al "
                     "observației. Când anul este nume de coloană, nu se poate "
                     "filtra sau grupa după el, iar fiecare an nou cere o "
                     "coloană nouă. În forma lungă, anul este o valoare ca "
                     "oricare alta."}),
   manual="")

DIRECTII = {
    "randuri": [
        {"a": "RO", "b": "IT", "ab": 1073196, "ba": 14856},
        {"a": "RO", "b": "HU", "ab": 15740, "ba": 4879},
        {"a": "PL", "b": "DE", "ab": 741784, "ba": None},
    ],
    "t0": "Migrația are direcție: românii din Italia ocupă un rând, italienii "
          "din România alt rând. SCI-ul are un singur rând pe pereche.",
    "t1": "Cele două direcții se află acum pe același rând, ca în SCI. Germanii "
          "din Polonia lipsesc: Polonia nu raportează.",
    "t2": "Suma. Pentru perechea Polonia-Germania rezultatul este valoare lipsă, "
          "nu 741.784: numărul germanilor din Polonia este necunoscut, deci și "
          "totalul.",
}
DIRECTII["intai"] = {"q": "Polonezii din Germania: 741.784. Germanii din Polonia: Polonia nu raportează. Câți migranți sunt, în total, între cele două țări?", "variante": ["741.784", "741.784 plus o estimare", "Nu se poate spune"], "corect": 2, "dupa": "O direcție lipsește, deci lipsește și suma. Zero ar fi o afirmație falsă („nu există niciun german în Polonia”), iar o estimare ar fi o decizie de documentat în jurnal, nu un calcul."}

sl("s16b", "Transformări", "Două direcții, un rând",
   "<h2>Migrația în forma SCI-ului</h2>"
   + ix("directii", "Românii din Italia și italienii din România", DIRECTII)
   + nota("Valoare lipsă plus număr dă valoare lipsă",
          "Este comportamentul corect: o pereche cu o direcție necunoscută nu "
          "are un total cunoscut. Cu zero în locul valorii lipsă, perechea "
          "Polonia-Germania ar fi părut cunoscută, dar ar fi fost greșită.", True),
   manual=
   "<h2>Două direcții, un rând</h2>"
   "<p>SCI-ul este simetric: o singură valoare pe pereche de țări. Migrația "
   "are direcție: un rând pentru românii din Italia, alt rând pentru "
   "italienii din România. Pentru a le reuni în același tabel, cele două "
   "direcții se aduc pe același rând prin două operații merge, câte una pentru "
   "fiecare direcție.</p>"
   + ix("directii", "Românii din Italia și italienii din România", DIRECTII)
   + "<pre><code>din_1_in_2 = migratie.rename(columns={\"citizen\": \"tara_1\", "
     "\"geo\": \"tara_2\", \"persoane\": \"din_1_in_2\"})\n"
     "din_2_in_1 = migratie.rename(columns={\"citizen\": \"tara_2\", "
     "\"geo\": \"tara_1\", \"persoane\": \"din_2_in_1\"})\n\n"
     "tari = tari.merge(din_1_in_2, on=[\"tara_1\", \"tara_2\"], how=\"left\")\n"
     "tari = tari.merge(din_2_in_1, on=[\"tara_1\", \"tara_2\"], how=\"left\")\n"
     "tari[\"migranti\"] = tari[\"din_1_in_2\"] + tari[\"din_2_in_1\"]</code></pre>"
   + "<p>Codul complet se află în caietul cursului 4. De reținut: cu "
     "<code>how=\"left\"</code> se păstrează toate perechile din SCI, iar cele "
     "fără date de migrație rămân cu valoare lipsă. Suma a două coloane dă "
     "valoare lipsă dacă oricare dintre ele lipsește, ceea ce este "
     "comportamentul dorit.</p>")


sl("s17", "Validare", "Înainte și după",
   "<h2>Ultima etapă: verificarea integrității datelor</h2>"
   + ix("cod", "Verificările finale", {
       "id": "c4-cod-validare", "indiciu": "O cheie unică are zero duplicate. Un număr de persoane nu poate fi negativ.",
       "iesire": "brut 5104, curat 4290, pierdute 814", "fisier": "validare.py",
       "sarcina": "Patru verificări care se fac după fiecare curățare.",
       "cod": "# 1. cheia este unica\n"
              "assert d.duplicated(subset=[\"citizen\", \"geo\"]).sum() == {{1}}\n\n"
              "# 2. codurile tarilor nu au lipsuri (Namibia este inca acolo)\n"
              "assert d[\"citizen\"].isna().sum() == 0\n\n"
              "# 3. niciun numar negativ de migranti\n"
              "assert (d[\"persoane\"].dropna() >= {{2}}).all()\n\n"
              "# 4. cate randuri s-au pierdut la curatare\n"
              "print(f\"brut {len(brut)}, curat {len(d)}, \"\n"
              "      f\"pierdute {len(brut) - len(d)}\")",
       "goluri": {
           "1": {"ok": ["0"], "ajutor": "câte"},
           "2": {"ok": ["0"], "ajutor": "minimul"}},
       "laBine": "<code>assert</code> oprește programul dacă condiția este "
                 "falsă. Este cel mai simplu mod de a detecta o eroare imediat "
                 "după ce a fost introdusă, nu cu mult mai târziu.",
       "laRau": "O cheie unică înseamnă zero duplicate. Un număr de persoane "
                "nu poate fi negativ.",
       "explicatie": "Ultima linie trebuie citită cu atenție: dacă s-a pierdut "
                     "un sfert din rânduri fără o explicație, operația nu a "
                     "fost o curățare, ci o eliminare nejustificată de date."}))

sl("s18", "Validare", "Dicționarul de date",
   "<h2>Documentația care permite reproducerea</h2>"
   "<p>Un fișier, păstrat lângă date, care descrie semnificația fiecărei "
   "coloane și deciziile luate pe parcurs.</p>"
   + tabel(["Ce conține", "Exemplu"], [
       ["numele coloanei", "<code>scaled_sci</code>"],
       ["semnificația", "intensitatea legăturii dintre două locuri, scalată"],
       ["unitatea sau scara", "indice relativ, comparabil între perechi"],
       ["sursa și versiunea", "Meta SCI, instantaneul din ianuarie 2026"],
       ["modificările făcute", "„EL și UK aduse la GR și GB; NA păstrat ca Namibia”"],
   ])
   + nota("Criteriul unui dicționar complet",
          "Un coleg care nu a participat la discuțiile echipei trebuie să poată "
          "reface curățarea doar pe baza acestui fișier și a codului. Dacă are "
          "nevoie de explicații suplimentare, documentația este incompletă.", True))


# ===========================================================================
#  19-21. Proiectul
# ===========================================================================

sl("s19", "Proiectul echipei","Curățarea datelor proprii",
   "<h2>Aplicare pe datele proiectului</h2>"
   + tabel(["Pasul", "Ce se face"], [
       ["1", "<code>curatare/curata.py</code>, care citește din <code>date/brute/</code>"],
       ["2", "profilare: shape, info, describe, isna"],
       ["3", "duplicate, standardizare, valori lipsă, valori extreme"],
       ["4", "rezultatul se scrie în <code>date/curat/</code>, nu peste datele brute"],
       ["5", "cele patru verificări finale, cu <code>assert</code>"],
   ]),
   manual=
   "<h2>Aplicare pe datele proiectului</h2>"
   + tabel(["Pasul", "Ce se face"], [
       ["1", "<code>curatare/curata.py</code>, care citește din <code>date/brute/</code>"],
       ["2", "profilare: shape, info, describe, isna"],
       ["3", "duplicate, standardizare, valori lipsă, valori extreme"],
       ["4", "rezultatul se scrie în <code>date/curat/</code>, nu peste datele brute"],
       ["5", "cele patru verificări finale, cu <code>assert</code>"],
   ])
   + ix("dovada", "Dovada curățării", {
       "id": "c4-dovada-curatare",
       "sarcina": "Rezultatul afișat de fiecare comandă, copiat în câmpul corespunzător.",
       "pasi": [
           {"t": "Numărul de rânduri, înainte și după curățare",
            "cmd": "python curatare/curata.py",
            "gol": "linia cu brut, curat, pierdute",
            "cauta": r"\d+[\s\S]*\d+",
            "daca_nu": "Sunt necesare două numere: rândurile inițiale și rândurile rămase. "
                       "Dacă scriptul nu le afișează, trebuie adăugată linia de la slide-ul 17."},
           {"t": "Fișierul curat există și este separat de cel brut",
            "cmd": "python -c \"import pandas as pd; d=pd.read_csv('date/curat/date.csv'); print(d.shape)\"",
            "gol": "dimensiunile (shape)",
            "cauta": r"\(\s*\d+\s*,\s*\d+\s*\)",
            "daca_nu": "Se așteaptă un rezultat de forma (rânduri, coloane). O eroare "
                       "de fișier negăsit arată că scriptul nu a scris în date/curat/."},
           {"t": "Curățarea este în depozit",
            "cmd": "git log --oneline -1",
            "gol": "linia afișată",
            "cauta": r"[0-9a-f]{7}",
            "daca_nu": "Se așteaptă un hash de commit."}],
       "explicatie": "Datele brute rămân nemodificate, cele curate sunt păstrate "
                     "separat, iar trecerea de la unele la altele este un script "
                     "care poate fi rulat din nou. Acestea sunt condițiile unei "
                     "curățări reproductibile."}))

sl("s19b", "Proiectul echipei","Dovada curățării",
   "<h2>Dovada curățării</h2>"
   + ix("dovada", "Dovada curățării", {
       "id": "c4-dovada-curatare",
       "sarcina": "Rezultatul afișat de fiecare comandă, copiat în câmpul corespunzător.",
       "pasi": [
           {"t": "Numărul de rânduri, înainte și după curățare",
            "cmd": "python curatare/curata.py",
            "gol": "linia cu brut, curat, pierdute",
            "cauta": r"\d+[\s\S]*\d+",
            "daca_nu": "Sunt necesare două numere: rândurile inițiale și rândurile rămase. "
                       "Dacă scriptul nu le afișează, trebuie adăugată linia de la slide-ul 17."},
           {"t": "Fișierul curat există și este separat de cel brut",
            "cmd": "python -c \"import pandas as pd; d=pd.read_csv('date/curat/date.csv'); print(d.shape)\"",
            "gol": "dimensiunile (shape)",
            "cauta": r"\(\s*\d+\s*,\s*\d+\s*\)",
            "daca_nu": "Se așteaptă un rezultat de forma (rânduri, coloane). O eroare "
                       "de fișier negăsit arată că scriptul nu a scris în date/curat/."},
           {"t": "Curățarea este în depozit",
            "cmd": "git log --oneline -1",
            "gol": "linia afișată",
            "cauta": r"[0-9a-f]{7}",
            "daca_nu": "Se așteaptă un hash de commit."}],
       "explicatie": "Datele brute rămân nemodificate, cele curate sunt păstrate "
                     "separat, iar trecerea de la unele la altele este un script "
                     "care poate fi rulat din nou. Acestea sunt condițiile unei "
                     "curățări reproductibile."}),
   manual="")

sl("s20", "Proiectul echipei","Documentarea deciziilor",
   "<h2>Deciziile de curățare</h2>"
   "<p>Două sau trei rânduri despre cea mai importantă decizie de curățare "
   "luată în proiect și despre motivul ei.</p>"
   + ix("asteptari", "Decizia de curățare", {
       "id": "c4-decizie", "tip": "decizie", "minim": 60,
       "sarcina": "O decizie de curățare luată pentru datele proiectului și motivul "
                  "ei: nu o formulare generală („datele au fost curățate”), ci ce anume "
                  "s-a modificat și de ce.",
       "exemplu": "De exemplu: migrația a fost păstrată ca valoare lipsă pentru perechile "
                  "cu Polonia, în loc de zero, deoarece Polonia nu raportează; aceste "
                  "perechi sunt excluse doar din model, nu din tabel.",
       "multumesc": "Răspunsul va fi citit înainte de cursul următor."}))

sl("s21", "Mai departe", "Pentru cursul următor",
   "<h2>La cursul 5: agregare și baze de date</h2>"
   '<div class="fin3"><div class="fin3__g">'
   "<section><h4>Ce urmează la cursul 5</h4><ul>"
   "<li>Îmbinarea surselor pe o cheie comună: SCI, migrație, distanță.</li>"
   "<li>La date diadice, două îmbinări: una pentru fiecare capăt.</li>"
   "<li>Unitatea de analiză: nivelul la care se răspunde la întrebare.</li>"
   "<li>De ce un tabel de 31.684 de rânduri justifică o bază de date.</li></ul></section>"
   "<section><h4>Pregătirea pentru cursul 5</h4><ul>"
   "<li>Scriptul de curățare, rulat și trimis în depozit, cu datele curate în <code>date/curat/</code>.</li>"
   "<li>Dicționarul de date, chiar și într-o formă scurtă, în depozit.</li></ul></section>"
   "</div></div>"
   + surse("Documentația curățării", [
       ("pandas: date lipsă", "https://pandas.pydata.org/docs/user_guide/missing_data.html", "NaN, <code>isna</code>, <code>dropna</code>, <code>fillna</code> și ce face fiecare"),
       ("pandas: lung și lat", "https://pandas.pydata.org/docs/user_guide/reshaping.html", "<code>pivot</code>, <code>melt</code>, cu diagrame"),
       ("pandas: duplicate", "https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.duplicated.html", "<code>duplicated</code> și <code>subset</code>"),
       ("pandas: read_csv", "https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html", "<code>keep_default_na</code> și <code>na_values</code>, relevante pentru cazul Namibiei"),
       ("Eurostat: migr_pop1ctz", "https://ec.europa.eu/eurostat/databrowser/view/migr_pop1ctz/default/table", "tabelul online, cu notele și marcajele (flags) fiecărei valori"),
   ]))


if __name__ == "__main__":
    L.scrie_tot()
