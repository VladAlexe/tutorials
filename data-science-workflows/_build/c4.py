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

from comun import Lectie, ix, verif, tabel, nota, RAD

L = Lectie(4, "c4-curatarea-datelor", "Curățarea datelor",
           "Git în practică, cele șase etape ale curățării, lipsurile, "
           "duplicatele, valorile extreme, și dicționarul de date.")
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
    ("Git, în practică", "azi", "Staging, commit, anulări, ramuri. Comenzile de care chiar ai nevoie."),
    ("De ce curățăm", "azi", "Cât din timpul unui proiect se duce aici, și de ce."),
    ("Cele șase etape", "azi", "De la profilare la validare finală, în ordine."),
    ("Pe datele noastre", "azi", "Fiecare etapă, cu cod, pe migrația colectată la cursul 2."),
    ("Două direcții, un rând", "azi", "Migrația pusă în forma SCI-ului: o pereche pe rând."),
    ("Dicționarul de date", "azi", "Ce ați schimbat, scris astfel încât să se poată reface."),
]

# Pașii pentru lecția 4, din 04_curatarea_si_integrarea_datelor.ipynb.
# Cifrele regionale: data/analiza_c4/referinta_c2_20261013/nuts2/regional_lung.csv (Eurostat, 2024).
# Migrația: Eurostat migr_pop1ctz, 2024.

PAS_PROFIL = {
    "fisier": "04_curatarea.ipynb · 2. Calitatea",
    "intro": "Înainte să schimbi ceva într-un tabel, te uiți la el. Indicatorii regionali din C3, la nivel NUTS 2.",
    "cod": "regional = pd.read_csv(DATE / \"c3\" / \"regional.csv\")\n"
           "regional = regional[regional[\"nivel\"] == 2]\n\n"
           "print(\"Duplicate:\", regional.duplicated([\"regiune\", \"indicator\"]).sum())\n"
           "print(\"Valori negative:\", (regional[\"valoare\"] < 0).sum())\n\n"
           "regional.groupby(\"indicator\")[\"valoare\"].describe().round(1)\n\n"
           "regional.nsmallest(1, \"valoare\")",
    "pasi": [
        {"l": 1, "set": {"regional": {"t": "DataFrame", "v": {"cols": ["regiune", "indicator", "valoare"],
            "rows": [["BE10", "populatie", 1264371], ["BE21", "populatie", 1932876], ["…", "…", "…"], ["RO11", "densitate", 74.7]],
            "nota": "format lung: un rând pe regiune și indicator"}}},
         "txt": "Tabelul salvat în C3. Un rând e identificat de două coloane împreună: <b>regiune + indicator</b>."},
        {"l": 2, "txt": "Păstrăm doar nivelul NUTS 2 (regiunile de dezvoltare, la noi). La seminar lucrați pe NUTS 3, județele."},
        {"l": 4, "out": "Duplicate: 0",
         "txt": "<code>duplicated</code> cu o listă de coloane caută aceeași <b>cheie</b> de două ori. Zero: fiecare regiune are fiecare indicator o singură dată."},
        {"l": 5, "out": "Valori negative: 0",
         "txt": "Populația și densitatea nu pot fi negative. Comparația dă True sau False pe fiecare rând; <code>.sum()</code> numără True-urile."},
        {"l": 7, "out": "              count       mean      min        50%         max\n"
                        "densitate     284.0      337.0      3.5      113.2      7827.4\n"
                        "pib_locuitor  276.0    35810.9  11700.0    33550.0    107200.0\n"
                        "populatie     291.0  1920320.8      0.0  1484402.0  15655924.0",
         "txt": "Un rezumat pe indicator (aici, cinci coloane din opt). Două lucruri sar în ochi: o densitate de 7.827 de locuitori pe km² și o <b>populație 0</b>."},
        {"l": 9, "out": "  regiune               denumire  indicator  valoare\n  NO0B    Svalbard og Jan Mayen  populatie      0.0",
         "txt": "Cine are populație 0? Svalbard, arhipelagul norvegian: Eurostat chiar raportează 0. Iar 7.827 e Bruxelles, un oraș-regiune. Nu sunt greșeli. De aceea nu ștergem automat: întâi căutăm în sursă."},
    ],
}

PAS_CODURI = {
    "fisier": "04_curatarea.ipynb · 7. Capcana codurilor",
    "intro": "Două capcane care nu dau nicio eroare. Pierzi țări în tăcere, și afli abia când lipsesc din grafic.",
    "cod": "gresit = pd.read_csv(DATE / \"c3\" / \"migratie.csv\")\n"
           "migratie = pd.read_csv(DATE / \"c3\" / \"migratie.csv\",\n"
           "                       keep_default_na=False, na_values=[\"\"])\n\n"
           "coduri = {\"EL\": \"GR\", \"UK\": \"GB\"}\n"
           "migratie = migratie.replace({\"tara_rezidenta\": coduri, \"cetatenie\": coduri})\n"
           "print(migratie[\"cetatenie\"].isin([\"EL\", \"UK\"]).sum())",
    "pasi": [
        {"l": 1, "set": {"gresit": {"t": "DataFrame", "v": {"cols": ["tara_rezidenta", "cetatenie", "persoane"],
            "rows": [["DE", "NaN", "…"], ["DE", "EL", 303375], ["ES", "UK", 272402], ["…", "…", "…"]],
            "nota": "Namibia (NA) a devenit NaN"}}},
         "txt": "Citit fără grijă. Pandas are o listă de texte pe care le ia drept „lipsă”, iar <code>NA</code> e pe ea. Namibienii din Germania au rămas fără țară."},
        {"l": 2, "set": {"migratie": {"t": "DataFrame", "v": {"cols": ["tara_rezidenta", "cetatenie", "persoane"],
            "rows": [["DE", "NA", "…"], ["DE", "EL", 303375], ["ES", "UK", 272402], ["…", "…", "…"]],
            "nota": "NA e din nou Namibia"}}},
         "txt": "<code>keep_default_na=False</code> oprește lista; <code>na_values=[\"\"]</code> spune că doar celula goală e lipsă. Același lucru l-ai făcut în C1 cu SCI."},
        {"l": 5, "set": {"coduri": {"t": "dict", "v": {"EL": "GR", "UK": "GB"}}},
         "txt": "A doua capcană: Eurostat scrie Grecia <code>EL</code> și Regatul Unit <code>UK</code>. SCI scrie <code>GR</code> și <code>GB</code>. Un dicționar spune ce devine ce."},
        {"l": 6, "set": {"migratie": {"t": "DataFrame", "v": {"cols": ["tara_rezidenta", "cetatenie", "persoane"],
            "rows": [["DE", "NA", "…"], ["DE", "GR", 303375], ["ES", "GB", 272402], ["…", "…", "…"]],
            "nota": "codurile, ca în SCI"}}},
         "hl": {"var": "coduri", "k": "EL"},
         "txt": "<code>replace</code> primește, pentru fiecare coloană, dicționarul de schimbat. Cei 303.375 de greci din Germania nu se mai pierd la join."},
        {"l": 7, "out": "0",
         "txt": "Verificarea de după: niciun EL sau UK n-a rămas. Dicționarul <code>coduri</code> e și documentația deciziei: peste trei luni, din el afli de ce Grecia e GR."},
    ],
}

_LUNG = [["RO11", "densitate", 74.7], ["RO12", "densitate", 67.4],
         ["RO11", "pib_locuitor", 28300.0], ["RO12", "pib_locuitor", 28400.0],
         ["RO11", "populatie", 2539784.0], ["RO12", "populatie", 2288061.0]]

PAS_PIVOT = {
    "fisier": "04_curatarea.ipynb · 4. Tabelul regiunilor",
    "intro": "Din lung în lat și înapoi, pe două regiuni: Nord-Vest (RO11, cu Clujul) și Centru (RO12).",
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
            "nota": "lat: 2 rânduri, regiunea e din nou coloană"}}},
         "txt": "<code>reset_index</code> scoate regiunea din index înapoi într-o coloană obișnuită, ca să poată fi folosită la <code>merge</code>."},
        {"l": 6, "set": {"inapoi": {"t": "DataFrame", "v": {"cols": ["regiune", "indicator", "valoare"], "rows": _LUNG,
            "nota": "din nou 6 rânduri"}}},
         "txt": "<code>melt</code> e drumul invers: coloanele de indicatori se „topesc” într-o coloană de nume și una de valori. Pe asta o scrii tu, mai jos."},
    ],
}


sl("s1", "Cursul", "Despre ce e ora de azi",
   "<h2>Curățarea datelor</h2>"
   "<p class=\"cheie\">Etapa cea mai lungă, cea mai plictisitoare, și singura "
   "care decide dacă restul are vreun sens.</p>"
   + ix("etape", "Agenda",
        {"titlu": "Ora de azi", "intro": "Apasă pe oricare.",
         "etape": [{"nume": n, "unde": u, "text": d} for n, u, d in AGENDA]},
        "Prima jumătate e Git, a doua e curățarea."),
   manual=
   "<h2>Curățarea datelor</h2>"
   "<p>Ora are două părți. Prima duce mai departe Git-ul de săptămâna trecută, "
   "cu comenzile care apar abia când lucrezi serios: cum scoți un fișier din "
   "pregătire, cum anulezi un commit, cum ștergi o ramură după ce ai îmbinat-o. "
   "A doua e despre curățarea datelor, adică despre ce faci cu ce ai colectat "
   "înainte să te uiți la rezultate.</p>"
   + ix("etape", "Agenda",
        {"titlu": "Ora de azi", "intro": "Apasă pe oricare.",
         "etape": [{"nume": n, "unde": u, "text": d} for n, u, d in AGENDA]}))

sl("s2", "Cursul", "Cât timp ia",
   "<h2>Cu ce își petrec timpul oamenii din meseria asta</h2>"
   + ix("cote", "Un studiu din 2016",
        {"cote": [
            {"t": "Curățarea și organizarea datelor", "v": 60, "ac": True},
            {"t": "Colectarea datelor", "v": 19},
            {"t": "Căutarea tiparelor în date", "v": 9},
            {"t": "Altele", "v": 5},
            {"t": "Reglarea algoritmilor", "v": 4},
            {"t": "Pregătirea seturilor de antrenament", "v": 3}],
         "sursa": "CrowdFlower, 2016 · ce au răspuns oameni care fac asta zilnic"},
        "Șaizeci la sută. Nu analiza, nu modelele: curățarea."),
   manual=
   "<h2>Cât timp ia curățarea</h2>"
   "<p>Cifra asta circulă de zece ani și e cam singura pe care toată lumea din "
   "domeniu o recunoaște ca adevărată.</p>"
   + ix("cote", "Un studiu din 2016",
        {"cote": [
            {"t": "Curățarea și organizarea datelor", "v": 60, "ac": True},
            {"t": "Colectarea datelor", "v": 19},
            {"t": "Căutarea tiparelor în date", "v": 9},
            {"t": "Altele", "v": 5},
            {"t": "Reglarea algoritmilor", "v": 4},
            {"t": "Pregătirea seturilor de antrenament", "v": 3}],
         "sursa": "CrowdFlower, 2016"})
   + "<p>Patru cincimi din timp se duc pe adus și curățat date; o zecime pe "
     "ceea ce lumea crede că e meseria. Nu e o anomalie a domeniului, e forma "
     "lui.</p>")


# ===========================================================================
#  3-7. Git în practică
# ===========================================================================

sl("s3", "Git în practică", "Fluxul complet",
   "<h2>Cele patru locuri și drumurile dintre ele</h2>"
   + ix("flux", "Drumul unei schimbări",
        {"titlu": "Apasă „Urmărește o schimbare”",
         "intro": "Dus: add, commit, push. Întors: fetch și merge, adică pull.",
         "buton": "Urmărește o schimbare",
         "dus": "add → commit → push",
         "intors": "pull: fetch, apoi merge",
         "gata": "ce ai scris tu e la toată lumea, și ce au scris ei e la tine",
         "statii": [
             {"n": "Dosarul de lucru", "et": "editezi", "ic": "📝", "c": "ceas",
              "d": "Fișierele așa cum sunt acum pe disc. Git le vede schimbate, dar nu le urmărește încă."},
             {"n": "Pregătire", "et": "git add", "ic": "📥", "c": "salvie",
              "d": "Ce ai ales să intre în următorul commit. Poți alege trei fișiere din șapte."},
             {"n": "Istoric local", "et": "git commit", "ic": "📦", "c": "accent",
              "d": "Scris definitiv, pe laptopul tău. Până aici nu ai avut nevoie de internet."},
             {"n": "GitHub", "et": "git push", "ic": "☁", "c": "text-2",
              "d": "Copia de pe internet. Abia acum munca ta există în două locuri."}]}))

sl("s4", "Git în practică", "Staging și commit",
   "<h2>Comenzile de zi cu zi</h2>"
   + tabel(["Comanda", "Ce face"], [
       ["~git status", "ce e schimbat și ce e în pregătire"],
       ["~git pull", "aduce ce e nou; dă-l când <code>git status</code> e curat"],
       ["~git add .", "adaugă tot în pregătire"],
       ["~git add nume", "adaugă un singur fișier"],
       ["~git reset -- nume", "scoate un fișier din pregătire; rămâne pe disc"],
       ["~git rm --cached nume", "Git nu-l mai urmărește deloc, dar rămâne în proiect"],
       ["~git commit -m \"mesaj\"", "scrie în istoric"],
       ["~git log --oneline", "istoricul, pe scurt"],
       ["~git show &lt;id&gt;", "exact ce s-a schimbat într-un commit"],
   ])
   + ix("cod", "Scoate fișierul care n-avea ce căuta", {
       "id": "c4-cod-staging", "indiciu": "Ce e în pregătire îți arată comanda pe care o dai cel mai des. Steagul care scoate doar din pregătire, nu și de pe disc, e --cached. Mesajul îl alegi tu.",
       "iesire": "rm '.env'\n[dev 4f2a9c1] curatare initiala\n 2 files changed, 18 insertions(+)", "fisier": "terminal.sh",
       "sarcina": "Ai dat <code>git add .</code> și a intrat și <code>.env</code>. "
                  "Scoate-l înainte de commit.",
       "cod": "# vezi ce ai in pregatire\ngit {{1}}\n\n"
              "# scoate .env din pregatire, dar lasa-l pe disc\n"
              "git rm {{2}} .env\n\n"
              "# ca sa nu se mai intample, il treci in .gitignore\n"
              "echo \".env\" >> .gitignore\n\n"
              "# acum poti face commit linistit\n"
              "git commit -m {{3}}",
       "goluri": {
           "1": {"ok": ["status"], "ajutor": "comanda"},
           "2": {"ok": ["--cached"], "ajutor": "steagul"},
           "3": {"ok": ["\"curatare initiala\"", "'curatare initiala'",
                        "\"colectare\"", "\"primul commit\""],
                 "re": "^[\"'].{3,}[\"']$",
                 "ajutor": "un mesaj, în ghilimele"}},
       "laBine": "<code>--cached</code> e cuvântul care contează: fără el, "
                 "<code>git rm</code> șterge fișierul de pe disc.",
       "laRau": "Steagul începe cu două liniuțe. Mesajul se scrie între ghilimele.",
       "explicatie": "<code>git rm --cached</code> scoate fișierul din "
                     "urmărire, dar îl lasă acolo unde e. E exact ce vrei "
                     "pentru un fișier cu parole: să nu mai plece nicăieri, dar "
                     "să rămână la tine, ca programul să meargă."}))

sl("s5", "Git în practică", "Anulări",
   "<h2>Când ai greșit</h2>"
   "<p>Patru situații diferite, patru comenzi diferite. Confuzia dintre ele e "
   "cea mai frecventă sursă de muncă pierdută.</p>"
   + ix("sortare", "Ce comandă, în ce situație", {
       "id": "c4-sort-undo", "poarta": False,
       "sarcina": "Potrivește situația cu comanda care o repară.",
       "elemente": [
           {"t": "git restore fisier", "cos": 0},
           {"t": "git restore --staged fisier", "cos": 1},
           {"t": "git revert <id>", "cos": 2},
           {"t": "git checkout <id>", "cos": 3}],
       "cosuri": [
           {"t": "Am stricat un fișier", "d": "și vreau versiunea din ultimul commit"},
           {"t": "Am dat add din greșeală", "d": "vreau doar să-l scot din pregătire"},
           {"t": "Un commit vechi era greșit", "d": "vreau să-l anulez, dar să rămână urma"},
           {"t": "Vreau doar să mă uit", "d": "cum arăta proiectul atunci"}],
       "laBine": "<code>revert</code> nu șterge istoria: adaugă un commit care "
                 "face pe dos. De aceea e singurul sigur într-un depozit pe "
                 "care îl folosesc și alții.",
       "explicatie": "<code>restore</code> lucrează pe fișiere, "
                     "<code>revert</code> pe commit-uri, "
                     "<code>checkout</code> te plimbă prin istorie fără să "
                     "schimbe nimic. Ce nu e în listă e <code>reset --hard</code>: "
                     "aruncă munca fără să întrebe, și nu are ce căuta "
                     "într-un depozit de echipă."}),
   manual=
   "<h2>Anulări</h2>"
   "<p>Git are faima că e greu tocmai pentru că are patru moduri de a „da "
   "înapoi”, iar numele lor nu spun de la sine care ce face.</p>"
   + ix("sortare", "Ce comandă, în ce situație", {
       "id": "c4-sort-undo", "poarta": False,
       "sarcina": "Potrivește situația cu comanda care o repară.",
       "elemente": [
           {"t": "git restore fisier", "cos": 0},
           {"t": "git restore --staged fisier", "cos": 1},
           {"t": "git revert <id>", "cos": 2},
           {"t": "git checkout <id>", "cos": 3}],
       "cosuri": [
           {"t": "Am stricat un fișier", "d": "și vreau versiunea din ultimul commit"},
           {"t": "Am dat add din greșeală", "d": "vreau doar să-l scot din pregătire"},
           {"t": "Un commit vechi era greșit", "d": "vreau să-l anulez, dar să rămână urma"},
           {"t": "Vreau doar să mă uit", "d": "cum arăta proiectul atunci"}],
       "laBine": "<code>revert</code> nu șterge istoria.",
       "explicatie": "<code>reset --hard</code> nu e în listă pentru că aruncă "
                     "munca fără să întrebe."})
   + nota("Regula simplă",
          "Dacă greșeala e doar la tine, pe laptop, poți folosi orice. Dacă a "
          "ajuns pe GitHub și altcineva a luat-o, singura variantă politicoasă "
          "e <code>revert</code>."))

sl("s6", "Git în practică", "Ramuri, în practică",
   "<h2>Ciclul complet al unei ramuri</h2>"
   + tabel(["Comanda", "Ce face"], [
       ["~git branch", "ramurile locale"],
       ["~git branch -r / -a", "ramurile de pe GitHub / toate"],
       ["~git branch -vv", "fiecare ramură și pe cine urmărește (upstream)"],
       ["~git switch -c nume", "creează și trece pe ea"],
       ["~git switch nume", "trece pe una existentă"],
       ["~git merge nume", "aduce ramura în cea pe care ești"],
       ["~git branch -d nume", "o șterge, dacă a fost îmbinată"],
       ["~git branch -D nume", "o șterge oricum; rar, și cu grijă"],
   ])
   + nota("Dacă ți se deschide Vim și nu mai poți ieși",
          "La <code>git merge</code> sau <code>git commit</code> fără "
          "<code>-m</code>, Git deschide un editor. Dacă e Vim, ecranul pare "
          "blocat. Nu e: apeși <kbd>Esc</kbd>, apoi scrii <code>:wq</code> și "
          "<kbd>Enter</kbd>. Scrie și iese."))

sl("s7", "Git în practică", "Depozitul pe GitHub",
   "<h2>Recapitulare în două cazuri</h2>"
   + tabel(["Ai deja depozit local", "Nu ai nimic"], [
       ["faci un depozit gol pe GitHub", "faci depozitul pe GitHub"],
       ["<code>git remote add origin &lt;url&gt;</code>", "<code>git clone &lt;url&gt;</code>"],
       ["<code>git push -u origin main</code>", "gata, e deja legat"],
   ]))


# ===========================================================================
#  8-9. Curățarea: harta
# ===========================================================================

ETAPE_CUR = [
    ("1. Profilare", "înțelegi ce ai",
     "Verifici tipurile, distribuțiile, lipsurile, valorile suspecte. "
     "Identifici erorile evidente și problemele de structură. Nu schimbi nimic încă."),
    ("2. Integrare și standardizare", "aliniezi surse",
     "Aduci sursele diferite la aceeași formă: etichete, formate, unități, "
     "tipuri. Corectezi textul, codurile și convențiile."),
    ("3. Curățare de bază", "scoți ce nu trebuie",
     "Elimini ce e irelevant sau redundant, scoți duplicatele, repari erorile "
     "structurale și categoriile incoerente."),
    ("4. Lipsuri și anomalii", "decizi",
     "Analizezi lipsurile și hotărăști ce faci cu ele. Te uiți la valorile "
     "extreme sau imposibile. Verifici regulile logice."),
    ("5. Transformări", "pregătești analiza",
     "Reorganizezi structura (long sau wide), faci agregări și variabile noi, "
     "aplici scalări, completezi cu informații externe."),
    ("6. Validare și documentare", "închizi",
     "Verifici cheile unice și coerența. Compari statisticile înainte și după. "
     "Notezi transformările, versiunile, și dicționarul de date."),
]

sl("s8", "Curățarea", "Cele șase etape",
   "<h2>De la date brute la date pe care te poți baza</h2>"
   + ix("etape", "Harta curățării",
        {"titlu": "Șase etape, în ordine", "intro": "Apasă pe oricare.",
         "etape": [{"nume": n, "unde": u, "text": d} for n, u, d in ETAPE_CUR]},
        "Ordinea contează: nu poți decide ce faci cu lipsurile înainte să știi "
        "câte sunt și unde.")
   + "<p class=\"cheie\">Prima etapă nu schimbă nimic. Doar te uiți. E și cea "
     "pe care o sare toată lumea.</p>",
   manual=
   "<h2>Cele șase etape</h2>"
   "<p>Curățarea nu e o listă de trucuri, e un drum cu o ordine. Fiecare etapă "
   "presupune ce s-a aflat la cea dinainte.</p>"
   + ix("etape", "Harta curățării",
        {"titlu": "Șase etape, în ordine", "intro": "Apasă pe oricare.",
         "etape": [{"nume": n, "unde": u, "text": d} for n, u, d in ETAPE_CUR]})
   + nota("De ce se sare peste prima",
          "Pentru că nu produce nimic. După o oră de profilare, fișierul arată "
          "exact la fel. Dar fără ea, toate deciziile de mai târziu se iau pe "
          "ghicite, iar unele nu se mai pot întoarce."))

sl("s9", "Curățarea", "Profilarea",
   "<h2>Prima etapă: te uiți</h2>"
   + ix("pas", "Te uiți înainte să schimbi", PAS_PROFIL)
   + ix("cod", "Profilează tabelul", {
       "id": "c4-cod-profil", "indiciu": "Rezumatul pe coloane e „informații” (info). Statisticile numerice sunt o „descriere” (describe). Valorile distincte, cu frecvența lor, se numără cu value_counts.",
       "iesire": "(5104, 3)\n          valoare\ncount     4292.0\nmean     18736.2\n...\nRO    37\nPL    37\nBG    36", "fisier": "profilare.py",
       "sarcina": "Cinci întrebări pe care le pui oricărui tabel nou, înainte "
                  "să schimbi ceva în el.",
       "cod": "import pandas as pd\n\n"
              "d = pd.read_csv(\"date/brute/migratie.csv\")\n\n"
              "# 1. cat de mare e\nprint(d.shape)\n\n"
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
       "laBine": "Cele cinci se dau în ordinea asta, pe orice tabel nou.",
       "laRau": "Toate trei sunt metode, deci se scriu fără ghilimele și cu paranteze.",
       "explicatie": "<code>value_counts()</code> e cea mai bună pentru "
                     "coloanele categoriale. La migrație îți arată o "
                     "surpriză: Namibia lipsește, deși Eurostat o are. "
                     "Pandas a citit codul ei, <code>NA</code>, ca valoare "
                     "lipsă. O reparăm pe slide-ul următor."})
   + verif("c4-v6", 3,
           "<code>info()</code> arată o coloană de prețuri ca "
           "<code>object</code>, nu ca număr. Ce înseamnă?",
           ["Că fișierul e corupt",
            "Că pandas nu suportă prețuri",
            "Că valorile sunt prea mari",
            "Că în coloană e cel puțin o valoare care nu e număr"],
           "Că pandas a găsit ceva ce nu poate citi ca număr: o virgulă "
           "zecimală, un spațiu, un „n/a” scris cu litere. O singură valoare "
           "stricată din zece mii face toată coloana text."))


# ===========================================================================
#  10-12. Standardizare, duplicate, structuri
# ===========================================================================

sl("s10", "Curățarea", "Codurile care mint",
   "<h2>Aceeași țară, alt cod</h2>"
   + tabel(["Țara", "SCI", "Eurostat", "Ce se întâmplă"], [
       ["Grecia", "~GR", "~EL", "join-ul o pierde, fără eroare"],
       ["Regatul Unit", "~GB", "~UK", "la fel"],
       ["Namibia", "~NA", "~NA", "pandas o citește ca valoare lipsă"],
   ])
   + ix("pas", "Două capcane tăcute", PAS_CODURI)
   + ix("cod", "Repară codurile", {
       "id": "c4-cod-standard", "indiciu": "Ca NA (Namibia) să nu devină lipsă, oprești lista implicită de lipsuri: keep_default_na = valoarea logică „nu”. Codul britanic din SCI e GB. Metoda care schimbă valori după un dicționar e replace.",
       "iesire": "0", "fisier": "standardizare.py",
       "sarcina": "Citește fișierul fără să piardă Namibia, apoi adu codurile "
                  "Eurostat la cele din SCI.",
       "cod": "# NA e Namibia, nu o valoare lipsa: doar celula goala e lipsa\n"
              "d = pd.read_csv(\"date/brute/migratie.csv\",\n"
              "                keep_default_na={{1}}, na_values=[\"\"])\n\n"
              "# Eurostat scrie altfel doua tari; le aducem la codurile din SCI\n"
              "coduri = {\"EL\": \"GR\", \"UK\": {{2}}}\n"
              "d[\"citizen\"] = d[\"citizen\"].{{3}}(coduri)\n"
              "d[\"geo\"] = d[\"geo\"].replace(coduri)\n\n"
              "print(d[\"citizen\"].isin([\"EL\", \"UK\"]).sum())   # 0",
       "goluri": {
           "1": {"ok": ["False"], "ajutor": "valoarea"},
           "2": {"ok": ["\"GB\"", "'GB'"], "ajutor": "codul"},
           "3": {"ok": ["replace"], "ajutor": "metoda"}},
       "laBine": "Zero rânduri cu EL sau UK. Acum migrația și SCI-ul vorbesc "
                 "aceeași limbă.",
       "laRau": "Prima e o valoare logică. Codul e text, între ghilimele.",
       "explicatie": "Dicționarul <code>coduri</code> e documentația deciziei "
                     "tale. Peste trei luni, din el se află că ai hotărât că "
                     "EL și GR sunt aceeași țară. Fără el, Grecia ar dispărea "
                     "la primul join și nimeni n-ar ști de ce."}),
   manual=
   "<h2>Standardizarea: codurile care mint</h2>"
   "<p>Când aduni două surse, aceeași țară poate avea coduri diferite. "
   "Eurostat folosește <code>EL</code> pentru Grecia și <code>UK</code> "
   "pentru Regatul Unit; Meta folosește codurile ISO, <code>GR</code> și "
   "<code>GB</code>. Pentru calculator sunt țări diferite, iar un join pe "
   "coduri le pierde fără niciun mesaj de eroare.</p>"
   "<p>A doua capcană e mai perfidă: Namibia are codul <code>NA</code>, iar "
   "pandas citește <code>NA</code> ca valoare lipsă. Rândurile Namibiei nu "
   "dispar, dar codul lor devine gol, și orice filtru sau join pe țară le "
   "pierde.</p>"
   + tabel(["Țara", "SCI", "Eurostat", "Ce se întâmplă"], [
       ["Grecia", "~GR", "~EL", "join-ul o pierde, fără eroare"],
       ["Regatul Unit", "~GB", "~UK", "la fel"],
       ["Namibia", "~NA", "~NA", "pandas o citește ca valoare lipsă"],
   ])
   + ix("pas", "Două capcane tăcute", PAS_CODURI)
   + ix("cod", "Repară codurile", {
       "id": "c4-cod-standard", "indiciu": "Ca NA (Namibia) să nu devină lipsă, oprești lista implicită de lipsuri: keep_default_na = valoarea logică „nu”. Codul britanic din SCI e GB. Metoda care schimbă valori după un dicționar e replace.",
       "iesire": "0", "fisier": "standardizare.py",
       "sarcina": "Citește fără să piardă Namibia și aliniază codurile.",
       "cod": "d = pd.read_csv(\"date/brute/migratie.csv\",\n"
              "                keep_default_na={{1}}, na_values=[\"\"])\n\n"
              "coduri = {\"EL\": \"GR\", \"UK\": {{2}}}\n"
              "d[\"citizen\"] = d[\"citizen\"].{{3}}(coduri)\n"
              "d[\"geo\"] = d[\"geo\"].replace(coduri)",
       "goluri": {
           "1": {"ok": ["False"], "ajutor": "valoarea"},
           "2": {"ok": ["\"GB\"", "'GB'"], "ajutor": "codul"},
           "3": {"ok": ["replace"], "ajutor": "metoda"}},
       "laBine": "Acum migrația și SCI-ul vorbesc aceeași limbă.",
       "laRau": "Prima e o valoare logică. Codul e text, între ghilimele.",
       "explicatie": "Dicționarul <code>coduri</code> e documentația deciziei."})
   + nota("Aceeași regulă și pentru SCI",
          "Fișierul <code>country.csv</code> are și el Namibia. Îl citești tot "
          "cu <code>keep_default_na=False</code>, altfel pierzi perechile ei."))

sl("s11", "Curățarea", "Duplicatele",
   "<h2>Același rând, de două ori</h2>"
   "<p>Vin din colectări reluate, din îmbinări greșite, din export de două "
   "ori. Un duplicat nu se vede în medie, dar o schimbă.</p>"
   + ix("cod", "Scoate duplicatele", {
       "id": "c4-cod-duplicate", "indiciu": "Metoda care marchează rândurile repetate e duplicated. Păstrăm prima apariție: \"first\". Cheia e perechea de coloane citizen și geo, ca listă.",
       "iesire": "584\n0", "fisier": "duplicate.py",
       "sarcina": "Numără duplicatele, apoi scoate-le păstrând prima apariție.",
       "cod": "# cate randuri sunt identice cu altul de mai sus\n"
              "print(d.{{1}}().sum())\n\n"
              "# le scoatem, pastrand prima aparitie\n"
              "d = d.drop_duplicates(keep={{2}})\n\n"
              "# atentie: uneori duplicatul nu e pe tot randul, ci pe cheie\n"
              "# o pereche cetatenie-tara nu are voie sa apara de doua ori\n"
              "print(d.duplicated(subset={{3}}).sum())",
       "goluri": {
           "1": {"ok": ["duplicated"], "ajutor": "metoda"},
           "2": {"ok": ["\"first\"", "'first'"], "ajutor": "care rămâne"},
           "3": {"ok": ["[\"citizen\", \"geo\"]", "['citizen','geo']", "[\"citizen\",\"geo\"]",
                        "['citizen', 'geo']"],
                 "re": "^\\[\\s*[\"']citizen[\"']\\s*,\\s*[\"']geo[\"']\\s*\\]$",
                 "ajutor": "lista de coloane"}},
       "laBine": "Al doilea caz e cel periculos: rânduri care diferă printr-o "
                 "coloană neimportantă, dar care descriu aceeași observație.",
       "laRau": "Prima e o metodă. A doua e text, între ghilimele. A treia e o "
                "listă de nume de coloane.",
       "explicatie": "<code>drop_duplicates()</code> fără <code>subset</code> "
                     "compară tot rândul. La date diadice, cheia e perechea: "
                     "dacă aceeași pereche de locuri apare de două ori cu "
                     "valori diferite, ai o problemă de colectare, nu de "
                     "curățare, și merită întâi aflat de unde vine."}))

# ===========================================================================
#  13-15. Lipsuri și valori extreme
# ===========================================================================

sl("s13", "Lipsuri", "Ce faci cu ce lipsește",
   "<h2>Lipsurile nu sunt toate la fel</h2>"
   "<p>Înainte de a alege o metodă, întrebarea e <em>de ce</em> lipsește.</p>"
   + ix("sortare", "Ce faci în fiecare caz", {
       "id": "c4-sort-lipsuri", "poarta": False,
       "sarcina": "Potrivește situația cu ce e rezonabil să faci.",
       "elemente": [
           {"t": "3 rânduri din 30.000, la întâmplare", "cos": 0},
           {"t": "O coloană goală în proporție de 80%", "cos": 1},
           {"t": "Polonia nu raportează deloc migranții", "cos": 2},
           {"t": "Serie de timp, lipsește un an la mijloc", "cos": 3}],
       "cosuri": [
           {"t": "Le scoți", "d": "sunt puține și nu par sistematice"},
           {"t": "Scoți coloana", "d": "nu mai e informație, e zgomot"},
           {"t": "Le păstrezi și scrii asta", "d": "lipsa însăși e o informație"},
           {"t": "Completezi din vecini", "d": "interpolare sau ultima valoare"}],
       "laBine": "Al treilea caz e cel important, și e la noi: Polonia, "
                 "Danemarca, Grecia, Croația nu raportează. Lipsa are un tipar, "
                 "deci o păstrezi ca lipsă și o scrii. Nu e zero polonezi în Germania.",
       "explicatie": "Completarea cu media e cea mai populară și cea mai "
                     "periculoasă metodă: reduce artificial variația și face "
                     "rezultatele să pară mai sigure decât sunt. Dacă o "
                     "folosești, o scrii în raport."}))

sl("s14", "Lipsuri", "Lipsurile, în cod",
   "<h2>Cum arată în pandas</h2>"
   + ix("prezice", "Media și golurile", {
       "id": "c4-prezice-nan", "fisier": "04_curatarea.ipynb",
       "cod": "import pandas as pd\n\n"
              "s = pd.Series([10, None, 30])\n"
              "print(s.mean(), s.isna().sum())",
       "intrebare": "Ce afișează?",
       "variante": ["13.33 0", "20.0 1", "NaN 1", "Eroare"],
       "corect": 1,
       "indiciu": "pandas sare peste valorile lipsă când calculează media. Câte valori lipsesc?",
       "laBine": "Media se face din ce există: (10 + 30) / 2.",
       "explicatie": "<code>None</code> devine <code>NaN</code>, iar <code>mean()</code> îl ignoră: "
                     "media e din două valori, nu din trei. Comod, dar periculos: dacă lipsesc tocmai "
                     "valorile mari sau mici, media se mută fără să-ți spună. De aceea numeri întâi "
                     "lipsurile, cu <code>isna().sum()</code>."})
   + ix("cod", "Tratează lipsurile", {
       "id": "c4-cod-lipsuri", "indiciu": "Lipsurile se găsesc cu isna. Mediana e median. „Forward fill”, adică ia valoarea de dinainte, se scrie ffill.",
       "iesire": "5104 4292 0", "fisier": "lipsuri.py",
       "sarcina": "Numără, apoi aplică trei strategii diferite, fiecare "
                  "potrivită altei situații.",
       "cod": "# cate lipsuri, pe coloana\nprint(d.{{1}}().sum())\n\n"
              "# cazul 1: putine si imprastiate, le scoatem\n"
              "d1 = d.dropna(subset=[\"valoare\"])\n\n"
              "# cazul 2: completam cu mediana, mai robusta decat media\n"
              "d2 = d.copy()\n"
              "d2[\"valoare\"] = d2[\"valoare\"].fillna(d2[\"valoare\"].{{2}}())\n\n"
              "# cazul 3: serie de timp, luam ultima valoare cunoscuta\n"
              "d3 = d.sort_values(\"an\")\n"
              "d3[\"valoare\"] = d3[\"valoare\"].{{3}}()\n\n"
              "print(len(d), len(d1), d2[\"valoare\"].isna().sum())",
       "goluri": {
           "1": {"ok": ["isna", "isnull"], "ajutor": "metoda"},
           "2": {"ok": ["median"], "ajutor": "statistica"},
           "3": {"ok": ["ffill", "fillna(method='ffill')"], "ajutor": "metoda"}},
       "laBine": "Mediana, nu media: o singură valoare extremă mută media și "
                 "n-atinge mediana.",
       "laRau": "Prima și a treia sunt metode fără argumente. A doua e o "
                "statistică, tot metodă.",
       "explicatie": "<code>ffill</code> duce ultima valoare cunoscută mai "
                     "departe. Are sens la serii de timp, unde anul lipsă "
                     "seamănă cu cel dinainte, și n-are niciun sens la date "
                     "fără ordine, unde „rândul dinainte” nu înseamnă nimic."}))

sl("s15", "Lipsuri", "Valorile extreme",
   "<h2>Unde tai?</h2>"
   "<p>Regula obișnuită: tot ce trece de Q3 plus de 1,5 ori intervalul "
   "intercuartilic. Mută pragul și vezi ce se întâmplă.</p>"
   + ix("prag", "Pe datele voastre", {
       "id": "c4-prag",
       "sarcina": "Legătura socială a României cu fiecare dintre cele 177 de "
                  "țări din set. Mută pragul.",
       "valori": SCI,
       "intrebare": "Țările marcate sunt greșeli de date?",
       "laBine": "Sunt Moldova, Austria, Germania, Ungaria: diaspora și "
                 "vecinătatea. Nu sunt greșeli, sunt răspunsul. Dacă le tai ca "
                 "„valori extreme”, arunci exact ce aveai de explicat.",
       "laRau": "Uită-te ce țări sunt. Moldova, Austria, Germania, Ungaria: "
                "diaspora și vecinătatea, adică fenomenul pe care îl studiem. "
                "O valoare extremă statistic nu e automat o greșeală."})
   + nota("Când o valoare extremă chiar e o greșeală",
          "Când e imposibilă: o vârstă de 210 ani, un procent de 140, o dată "
          "din 1900 într-un set despre 2020. Pentru astea nu-ți trebuie IQR, "
          "îți trebuie o regulă logică scrisă de tine."),
   manual=
   "<h2>Valorile extreme</h2>"
   "<p>Metoda clasică se numește regula intervalului intercuartilic: calculezi "
   "primul și al treilea cuartil, iei diferența dintre ele, și marchezi tot ce "
   "iese în afara lui Q3 plus de 1,5 ori diferența.</p>"
   "<pre><code>q1 = d[\"sci\"].quantile(0.25)\n"
   "q3 = d[\"sci\"].quantile(0.75)\niqr = q3 - q1\n"
   "prag = q3 + 1.5 * iqr\n"
   "extreme = d[d[\"sci\"] &gt; prag]</code></pre>"
   "<p>Cifra 1,5 nu vine de nicăieri anume: e o convenție. Mută pragul mai jos "
   "și ai mai multe „valori extreme”, mai sus și n-ai niciuna.</p>"
   + ix("prag", "Pe datele voastre", {
       "id": "c4-prag",
       "sarcina": "Legătura socială a României cu fiecare țară din set. Mută pragul.",
       "valori": SCI,
       "intrebare": "Țările marcate sunt greșeli de date?",
       "laBine": "Sunt Moldova, Austria, Germania, Ungaria. Nu sunt greșeli, "
                 "sunt răspunsul.",
       "laRau": "Uită-te ce țări sunt: diaspora și vecinătatea, adică fenomenul "
                "pe care îl studiem."})
   + nota("Deosebirea care contează",
          "O valoare <em>extremă</em> e departe de restul. O valoare "
          "<em>greșită</em> e imposibilă. Prima se păstrează și se explică; a "
          "doua se repară sau se scoate. Confuzia dintre ele e felul cel mai "
          "elegant de a-ți șterge propria descoperire."))


# ===========================================================================
#  16-18. Transformări și validare
# ===========================================================================

sl("s16", "Transformări", "Lung sau lat",
   "<h2>Aceleași date, două forme</h2>"
   + tabel(["Lat (wide)", "Lung (long)"], [
       ["o coloană pe an", "o coloană „an” și una „valoare”"],
       ["bun de citit cu ochiul", "bun de calculat și de desenat"],
       ["<code>2020, 2021, 2022</code> ca nume de coloane", "anul devine o valoare"],
   ])
   + ix("pas", "Din lung în lat și înapoi", PAS_PIVOT)
   + ix("cod", "Treci din lat în lung", {
       "id": "c4-cod-melt", "indiciu": "Din lat în lung: „topești” tabelul, melt. Înapoi, din lung în lat: îl „rotești”, pivot.",
       "iesire": "   tara    an  valoare  pe_locuitor\n0    RO  2022   1044.0     0.000055\n1    IT  2022   5030.0     0.000085", "fisier": "forma.py",
       "sarcina": "Transformă tabelul cu o coloană pe an într-unul cu o linie "
                  "pe țară și an.",
       "cod": "# din lat in lung: anii devin valori intr-o coloana\n"
              "lung = d.{{1}}(id_vars=[\"tara\"], var_name=\"an\",\n"
              "                value_name=\"valoare\")\n\n"
              "# si inapoi, daca e nevoie\n"
              "lat = lung.{{2}}(index=\"tara\", columns=\"an\", values=\"valoare\")\n\n"
              "# o variabila noua, calculata\n"
              "lung[\"pe_locuitor\"] = lung[\"valoare\"] / lung[\"populatie\"]\n"
              "print(lung.head())",
       "goluri": {
           "1": {"ok": ["melt"], "ajutor": "metoda"},
           "2": {"ok": ["pivot"], "ajutor": "metoda"}},
       "laBine": "Forma lungă e cea cu care lucrează aproape tot ce urmează: "
                 "agregările, graficele, modelele.",
       "laRau": "Amândouă sunt metode ale tabelului.",
       "explicatie": "Un an nu e o proprietate a țării, e o observație despre "
                     "ea. Când anul e nume de coloană, nu poți filtra după el, "
                     "nu poți grupa după el, și orice an nou cere o coloană "
                     "nouă. În forma lungă, anul e o valoare ca oricare alta."}))

DIRECTII = {
    "randuri": [
        {"a": "RO", "b": "IT", "ab": 1073196, "ba": 14856},
        {"a": "RO", "b": "HU", "ab": 15740, "ba": 4879},
        {"a": "PL", "b": "DE", "ab": 741784, "ba": None},
    ],
    "t0": "Migrația are sens: românii din Italia sunt un rând, italienii din "
          "România sunt alt rând. SCI-ul are un singur rând pe pereche.",
    "t1": "Cele două direcții stau acum pe același rând, ca la SCI. Germanii din "
          "Polonia lipsesc: Polonia nu raportează.",
    "t2": "Suma. La Polonia–Germania iese lipsă, nu 741.784: nu știm câți germani "
          "sunt în Polonia, deci nu știm totalul.",
}

sl("s16b", "Transformări", "Două direcții, un rând",
   "<h2>Migrația în forma SCI-ului</h2>"
   + ix("directii", "Românii din Italia și italienii din România", DIRECTII)
   + nota("Lipsă plus număr dă lipsă",
          "E alegerea corectă: o pereche cu o direcție necunoscută nu are "
          "un total cunoscut. Dacă puneai zero, Polonia–Germania ar fi părut "
          "cunoscută, și greșită.", True),
   manual=
   "<h2>Două direcții, un rând</h2>"
   "<p>SCI-ul e simetric: o valoare pe pereche de țări. Migrația are sens: "
   "un rând pentru românii din Italia, alt rând pentru italienii din "
   "România. Ca să le punem în același tabel, aducem cele două direcții pe "
   "același rând, cu două merge-uri: unul pentru fiecare direcție.</p>"
   + ix("directii", "Românii din Italia și italienii din România", DIRECTII)
   + "<pre><code>din_1_in_2 = migratie.rename(columns={\"citizen\": \"tara_1\", "
     "\"geo\": \"tara_2\", \"persoane\": \"din_1_in_2\"})\n"
     "din_2_in_1 = migratie.rename(columns={\"citizen\": \"tara_2\", "
     "\"geo\": \"tara_1\", \"persoane\": \"din_2_in_1\"})\n\n"
     "tari = tari.merge(din_1_in_2, on=[\"tara_1\", \"tara_2\"], how=\"left\")\n"
     "tari = tari.merge(din_2_in_1, on=[\"tara_1\", \"tara_2\"], how=\"left\")\n"
     "tari[\"migranti\"] = tari[\"din_1_in_2\"] + tari[\"din_2_in_1\"]</code></pre>"
   + "<p>Codul e în caietul cursului 4. Ce merită reținut: cu "
     "<code>how=\"left\"</code> păstrăm toate perechile din SCI, iar cele fără "
     "migrație rămân cu valoare lipsă. Suma a două coloane dă lipsă dacă "
     "oricare lipsește, ceea ce e exact ce vrem.</p>")


sl("s17", "Validare", "Înainte și după",
   "<h2>Ultima etapă: dovedești că n-ai stricat nimic</h2>"
   + ix("cod", "Verificările de la final", {
       "id": "c4-cod-validare", "indiciu": "O cheie unică are zero duplicate. Un număr de oameni nu poate fi sub zero.",
       "iesire": "brut 5104, curat 4290, pierdute 814", "fisier": "validare.py",
       "sarcina": "Patru verificări care se fac după curățare, de fiecare dată.",
       "cod": "# 1. cheia chiar e unica?\n"
              "assert d.duplicated(subset=[\"citizen\", \"geo\"]).sum() == {{1}}\n\n"
              "# 2. codurile tarilor n-au lipsuri (Namibia e inca acolo)\n"
              "assert d[\"citizen\"].isna().sum() == 0\n\n"
              "# 3. nimeni nu are un numar negativ de migranti\n"
              "assert (d[\"persoane\"].dropna() >= {{2}}).all()\n\n"
              "# 4. cate randuri am pierdut pe drum\n"
              "print(f\"brut {len(brut)}, curat {len(d)}, \"\n"
              "      f\"pierdute {len(brut) - len(d)}\")",
       "goluri": {
           "1": {"ok": ["0"], "ajutor": "câte"},
           "2": {"ok": ["0"], "ajutor": "minimul"}},
       "laBine": "<code>assert</code> oprește programul dacă nu e adevărat. E "
                 "cel mai ieftin fel de a prinde o stricăciune la câteva "
                 "secunde după ce ai făcut-o, nu peste trei săptămâni.",
       "laRau": "O cheie unică înseamnă zero duplicate. Un număr de oameni nu "
                "e negativ.",
       "explicatie": "Ultima linie e cea pe care o citești cu atenție: dacă ai "
                     "pierdut un sfert din rânduri și nu știi de ce, curățarea "
                     "n-a fost o curățare, a fost o tăiere."}))

sl("s18", "Validare", "Dicționarul de date",
   "<h2>Ce scrii, ca să se poată reface</h2>"
   "<p>Un fișier, lângă date, în care stă ce înseamnă fiecare coloană și ce "
   "ați hotărât pe parcurs.</p>"
   + tabel(["Ce scrii", "Exemplu"], [
       ["numele coloanei", "<code>scaled_sci</code>"],
       ["ce înseamnă", "tăria legăturii dintre două locuri, scalată"],
       ["unitatea sau scara", "index relativ, se compară între perechi"],
       ["sursa și versiunea", "Meta SCI, instantaneul din ianuarie 2026"],
       ["ce ați schimbat", "„EL și UK aduse la GR și GB; NA păstrat ca Namibia”"],
   ])
   + nota("Testul dicționarului bun",
          "Un coleg care n-a fost la ședințele voastre trebuie să poată "
          "reface curățarea citind doar fișierul ăsta și codul. Dacă îi "
          "trebuie și o discuție cu voi, mai aveți de scris.", True))


# ===========================================================================
#  19-21. Proiectul
# ===========================================================================

sl("s19", "Proiectul tău", "Curăță-ți datele",
   "<h2>Pe datele voastre, acum</h2>"
   + tabel(["Pasul", "Ce faci"], [
       ["1", "<code>curatare/curata.py</code>, care citește din <code>date/brute/</code>"],
       ["2", "profilare: shape, info, describe, isna"],
       ["3", "duplicate, standardizare, lipsuri, valori extreme"],
       ["4", "scrie rezultatul în <code>date/curat/</code>, nu peste brut"],
       ["5", "cele patru verificări finale, cu <code>assert</code>"],
   ])
   + ix("dovada", "Dovada curățării", {
       "id": "c4-dovada-curatare",
       "sarcina": "Rulează scriptul și lipește ce scrie.",
       "pasi": [
           {"t": "Știi cu ce ai pornit și cu ce ai rămas",
            "cmd": "python curatare/curata.py",
            "gol": "lipește linia cu brut, curat, pierdute",
            "cauta": r"\d+[\s\S]*\d+",
            "daca_nu": "Caut două numere: câte rânduri aveai și câte ai rămas. "
                       "Dacă scriptul nu le tipărește, adaugă linia de la slide-ul 17."},
           {"t": "Fișierul curat există și e separat de cel brut",
            "cmd": "python -c \"import pandas as pd; d=pd.read_csv('date/curat/date.csv'); print(d.shape)\"",
            "gol": "lipește forma",
            "cauta": r"\(\s*\d+\s*,\s*\d+\s*\)",
            "daca_nu": "Caut ceva de forma (rânduri, coloane). Dacă dă eroare "
                       "de fișier negăsit, scriptul n-a scris în date/curat/."},
           {"t": "Curățarea e în depozit",
            "cmd": "git log --oneline -1",
            "gol": "lipește linia",
            "cauta": r"[0-9a-f]{7}",
            "daca_nu": "Caut un hash de commit."}],
       "explicatie": "Datele brute rămân neatinse, cele curate stau separat, "
                     "iar drumul dintre ele e un script care se poate rula din "
                     "nou. Asta e tot ce înseamnă o curățare reproductibilă."}))

sl("s20", "Proiectul tău", "Scrieți dicționarul",
   "<h2>Ce ați hotărât</h2>"
   "<p>Două-trei rânduri despre cea mai importantă decizie de curățare pe care "
   "ați luat-o și de ce.</p>"
   + ix("asteptari", "Decizia voastră de curățare", {
       "id": "c4-decizie", "tip": "decizie", "minim": 60,
       "sarcina": "Scrie o decizie de curățare pe care ați luat-o la datele "
                  "voastre, și motivul. Nu „am curățat datele”: ce anume, și de ce așa.",
       "exemplu": "De exemplu: am lăsat migrația lipsă pentru perechile cu "
                  "Polonia, în loc să punem zero, pentru că Polonia nu raportează; "
                  "le scoatem doar din model, nu din tabel.",
       "multumesc": "O citesc înainte de cursul următor."}))

sl("s21", "Mai departe", "Până data viitoare",
   "<h2>Cursul 5: agregare și baze de date</h2>"
   "<ul>"
   "<li>îmbinarea surselor pe o cheie comună: SCI, migrație, distanță</li>"
   "<li>la date diadice, două îmbinări: una pentru fiecare capăt</li>"
   "<li>unitatea de analiză: la ce nivel răspunzi la întrebare</li>"
   "<li>de ce un tabel de 31.684 de rânduri vrea o bază de date</li>"
   "</ul>"
   + nota("De făcut până atunci",
          "Scriptul de curățare, rulat și urcat, cu datele curate în "
          "<code>date/curat/</code>. Plus dicționarul de date, fie și scurt, "
          "în depozit.", True))


if __name__ == "__main__":
    L.scrie_tot()
