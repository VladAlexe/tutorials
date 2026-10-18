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

from comun import Lectie, ix, verif, tabel, nota

L = Lectie(5, "c5-agregare-si-baze-de-date", "Agregare și baze de date",
           "Unirea tabelelor în pandas, tipurile de join, capcanele lor, "
           "unitatea de analiză, și mutarea datelor într-o bază Postgres.")
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
    "concat": "<b>Una sub alta.</b> Opt rânduri: nimic nu se potrivește cu "
              "nimic, fiindcă <code>concat</code> nici nu se uită la chei. "
              "Coloanele se reunesc, iar unde tabelul nu avea coloana aceea "
              "rămâne <code>NaN</code>. E ce vrei când lipești ani diferiți "
              "din aceeași sursă, nu când adaugi coloane.",
    "inner": "<b>Doar ce e în amândouă.</b> Trei rânduri: AT, DE, HU. Moldova "
             "a dispărut, adică cel mai puternic partener al României, doar "
             "pentru că nu raportează migrația. Nicio celulă goală și nicio "
             "urmă a ei. De asta <code>inner</code> e periculos ca implicit.",
    "left": "<b>Tot ce e în stânga.</b> Patru rânduri, câte avea tabelul "
            "<code>sci</code>. MD rămâne, cu <code>NaN</code> la români: nu "
            "știm, și se vede că nu știm. IT nu apare, fiindcă în stânga am pus "
            "doar patru parteneri. Ăsta e felul pe care îl vrei când stânga e "
            "tabelul tău de bază.",
    "right": "<b>Tot ce e în dreapta.</b> Oglinda lui <code>left</code>: "
             "acum IT rămâne cu <code>NaN</code> la SCI, iar MD dispare. "
             "Se folosește rar: de obicei schimbi ordinea tabelelor și "
             "scrii <code>left</code>, care se citește mai ușor.",
    "outer": "<b>Tot, de peste tot.</b> Cinci rânduri: cele trei comune, plus "
             "MD fără migrație, plus IT fără SCI. E felul cu care verifici: "
             "dacă <code>outer</code> dă mai multe rânduri decât "
             "<code>inner</code>, știi exact cât ai fi pierdut.",
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
    ("Unirea tabelelor", "azi", "Una sub alta, sau una lângă alta. Două operații "
                                "complet diferite, cu nume care seamănă."),
    ("Tipurile de join", "azi", "inner, left, right, outer. Care ce păstrează "
                                "și, mai ales, ce aruncă."),
    ("Capcanele", "azi", "Chei care nu se potrivesc și rânduri care se înmulțesc. "
                         "Aici se pierd datele."),
    ("Unitatea de analiză", "azi", "Ce e un rând în tabelul vostru final. "
                                   "Fără răspunsul ăsta, agregarea n-are formă."),
    ("Baza de date", "azi", "Când fișierul nu mai ajunge, și cum se pun datele "
                            "într-un Postgres pe Neon."),
]

sl("s1", "Cursul", "Despre ce e ora de azi",
   "<h2>Agregare și baze de date</h2>"
   "<p class=\"cheie\">Ai mai multe tabele curate. Azi devin unul singur, "
   "și pleacă dintr-un folder într-un loc din care se poate întreba.</p>"
   + ix("etape", "Agenda",
        {"titlu": "Ora de azi", "intro": "Apasă pe oricare.",
         "etape": [{"nume": n, "unde": u, "text": d} for n, u, d in AGENDA]},
        "Prima jumătate e pandas, a doua e SQL."),
   manual=
   "<h2>Agregare și baze de date</h2>"
   "<p>Până acum fiecare sursă a stat în fișierul ei: SCI într-unul, "
   "migrația în altul, indicatorii de la Eurostat în al treilea. Funcționează "
   "cât timp te uiți la ele pe rând. În momentul în care vrei să spui ceva "
   "de forma „perechile de țări cu mulți migranți sunt și mai legate”, îți "
   "trebuie un singur tabel.</p>"
   "<p>Unirea tabelelor pare o operație tehnică și e, de fapt, o decizie de "
   "cercetare: ce păstrezi când o sursă n-are o țară pe care cealaltă o are. "
   "Fiecare fel de join e un răspuns diferit la întrebarea asta, iar "
   "răspunsul schimbă câte rânduri rămân în analiză.</p>"
   "<p>A doua jumătate mută rezultatul dintr-un CSV într-o bază de date "
   "Postgres. Nu pentru că e mai modern, ci pentru că din momentul în care "
   "lucrați mai mulți pe aceleași date, fișierul devine problema.</p>"
   + ix("etape", "Agenda",
        {"titlu": "Ora de azi", "intro": "Apasă pe oricare.",
         "etape": [{"nume": n, "unde": u, "text": d} for n, u, d in AGENDA]}))


sl("s2", "Cursul", "De ce nu ajunge un fișier",
   "<h2>Momentul în care CSV-ul devine problema</h2>"
   "<p>Nu e despre mărime. E despre ce se întâmplă când nu mai ești singur.</p>"
   + tabel(["Ce faci", "Cu fișiere", "Cu o bază de date"],
           [["Doi oameni modifică în același timp",
             "~date_final_v2_ANA.csv", "o singură copie, amândoi scriu în ea"],
            ["Vrei doar țările din UE, în 2022",
             "citești tot și filtrezi în memorie", "~where ue and an = 2022"],
            ["Verifici că nu ai duplicate",
             "scrii cod de fiecare dată", "~primary key, baza refuză"],
            ["Zece tabele legate între ele",
             "zece fișiere și o convenție de nume", "~join, scris o dată"],
            ["Ai greșit și vrei înapoi",
             "speri că ai un backup", "o ramură, sau un punct de restaurare"]])
   + nota("ȚINE MINTE", "Un CSV e bun până la prima colaborare. Pragul nu e "
                        "numărul de rânduri, e numărul de oameni."),
   manual=
   "<h2>Momentul în care CSV-ul devine problema</h2>"
   "<p>Întrebarea „de la câte rânduri trebuie o bază de date” are un răspuns "
   "prost, pentru că mărimea e rareori motivul. Pandas duce fără probleme "
   "câteva milioane de rânduri pe un laptop obișnuit, iar datele voastre sunt "
   "mult sub atât.</p>"
   "<p>Motivele adevărate sunt altele: mai mulți oameni care scriu în același "
   "loc, reguli care trebuie să țină singure (o țară nu poate apărea de două "
   "ori în același an), și întrebări pe care nu vrei să le rescrii de fiecare "
   "dată în Python.</p>"
   + tabel(["Ce faci", "Cu fișiere", "Cu o bază de date"],
           [["Doi oameni modifică în același timp",
             "~date_final_v2_ANA.csv", "o singură copie, amândoi scriu în ea"],
            ["Vrei doar țările din UE, în 2022",
             "citești tot și filtrezi în memorie", "~where ue and an = 2022"],
            ["Verifici că nu ai duplicate",
             "scrii cod de fiecare dată", "~primary key, baza refuză"],
            ["Zece tabele legate între ele",
             "zece fișiere și o convenție de nume", "~join, scris o dată"],
            ["Ai greșit și vrei înapoi",
             "speri că ai un backup", "o ramură, sau un punct de restaurare"]])
   + nota("ȚINE MINTE", "Un CSV e bun până la prima colaborare. Pragul nu e "
                        "numărul de rânduri, e numărul de oameni."),
   dupa=verif("c5-v1", 1,
              "Echipa voastră are 40.000 de rânduri și trei oameni care "
              "lucrează pe ele. Ce argument e cel mai bun pentru o bază de date?",
              ["Că 40.000 de rânduri sunt prea multe pentru pandas",
               "Că trei oameni au nevoie de o singură copie, nu de trei",
               "Că bazele de date sunt mai rapide",
               "Că așa se face în industrie"],
              "Mărimea nu e problema. Trei oameni cu trei copii ale aceluiași "
              "fișier sunt."))


# ===========================================================================
#  3-9. Unirea tabelelor
# ===========================================================================

sl("s3", "Unirea tabelelor", "Două operații, nu una",
   "<h2>Una sub alta, sau una lângă alta</h2>"
   "<p>Amândouă se numesc, în vorbire, „am unit tabelele”. În cod sunt două "
   "funcții diferite, care răspund la întrebări diferite.</p>"
   + tabel(["", "Concatenare", "Merge / join"],
           [["Ce adaugă", "rânduri", "coloane"],
            ["Când", "aceleași coloane, surse diferite",
             "tabele diferite, cu o cheie comună"],
            ["Exemplu la voi", "2020, 2021, 2022, descărcate separat",
             "SCI plus migrație, pe cod de țară"],
            ["În cod", "~pd.concat([a, b])", "~pd.merge(a, b, on=\"cod\")"],
            ["Ce poate strica", "coloane cu nume ușor diferite",
             "chei care nu se potrivesc"]])
   + nota("ÎNTREBAREA CARE LE SEPARĂ",
          "„Vreau mai multe rânduri sau mai multe coloane?” Dacă răspunsul e "
          "rânduri, e <code>concat</code>. Dacă e coloane, e <code>merge</code>."),
   manual=
   "<h2>Una sub alta, sau una lângă alta</h2>"
   "<p>Confuzia dintre cele două e cea mai frecventă greșeală la agregare, și "
   "e ușor de evitat dacă pui întrebarea în forma potrivită: vreau ca tabelul "
   "să crească în jos sau în lateral?</p>"
   "<p>Descarci datele Eurostat an cu an și vrei un singur tabel cu toți "
   "anii: cresc rândurile, deci <code>concat</code>. Ai tabelul cu SCI și vrei "
   "să-i adaugi populația fiecărei țări: cresc coloanele, deci "
   "<code>merge</code>.</p>"
   + tabel(["", "Concatenare", "Merge / join"],
           [["Ce adaugă", "rânduri", "coloane"],
            ["Când", "aceleași coloane, surse diferite",
             "tabele diferite, cu o cheie comună"],
            ["Exemplu la voi", "2020, 2021, 2022, descărcate separat",
             "SCI plus migrație, pe cod de țară"],
            ["În cod", "~pd.concat([a, b])", "~pd.merge(a, b, on=\"cod\")"],
            ["Ce poate strica", "coloane cu nume ușor diferite",
             "chei care nu se potrivesc"]])
   + nota("ÎNTREBAREA CARE LE SEPARĂ",
          "„Vreau mai multe rânduri sau mai multe coloane?” Dacă răspunsul e "
          "rânduri, e <code>concat</code>. Dacă e coloane, e <code>merge</code>."),
   dupa=verif("c5-v2", 2,
              "Ai câte un fișier pentru fiecare an, toate cu aceleași coloane. "
              "Ce folosești?",
              ["pd.merge, pentru că sunt fișiere diferite",
               "df.join, pentru că anul e indexul",
               "pd.concat, pentru că vrei mai multe rânduri",
               "Depinde de mărimea fișierelor"],
              "Aceleași coloane, surse diferite: rândurile cresc, coloanele "
              "nu. <code>concat</code>."))


sl("s4", "Unirea tabelelor", "Ce iese din fiecare fel",
   "<h2>Numără rândurile</h2>"
   "<p>Două tabele mici, cu o cheie comună și câte una care nu se potrivește. "
   "Apasă pe fiecare fel de îmbinare și uită-te ce rămâne jos.</p>"
   + ix("imbinare", "Pe două tabele adevărate", {
       "id": "c5-imbinare-feluri", "cheie": "cod",
       "stanga": STANGA, "dreapta": DREAPTA, "numeRez": "rezultat",
       "sarcina": "Încearcă-le pe toate cinci. Urmărește două lucruri: câte "
                  "rânduri ies, și unde apar celule goale.",
       "explicatii": EXPLIC})
   + nota("DE CE CONTEAZĂ",
          "Moldova nu e un detaliu de exercițiu: la datele noastre, "
          "<code>inner</code> scoate din analiză toate țările care nu "
          "raportează migrația, fără să scrie nicăieri că au dispărut."),
   manual=
   "<h2>Numără rândurile</h2>"
   "<p>Definițiile din documentație sunt corecte și inutile: se rețin cu "
   "greu și se confundă între ele. Felul în care se învață un join e să te "
   "uiți la două tabele mici și să numeri ce iese.</p>"
   "<p>Tabelele de mai jos au trei chei comune (AT, DE, HU), una doar în "
   "stânga (MD: Moldova nu raportează migrația la Eurostat) și una doar în "
   "dreapta (IT, pentru că în stânga am pus doar patru parteneri ai "
   "României).</p>"
   + ix("imbinare", "Pe două tabele adevărate", {
       "id": "c5-imbinare-feluri", "cheie": "cod",
       "stanga": STANGA, "dreapta": DREAPTA, "numeRez": "rezultat",
       "sarcina": "Încearcă-le pe toate cinci.",
       "explicatii": EXPLIC})
   + nota("DE CE CONTEAZĂ",
          "Diferența dintre <code>inner</code> și <code>left</code> poate "
          "însemna douăzeci de țări care dispar din analiză fără să scrie "
          "nicăieri că au dispărut."))


sl("s5", "Unirea tabelelor", "Îmbinarea, în cod",
   "<h2>Scrie-o</h2>"
   + ix("cod", "Lipește populația peste SCI", {
       "id": "c5-cod-merge", "fisier": "agregare/uneste.py",
       "sarcina": "Vrei să păstrezi toate țările din tabelul cu SCI, chiar "
                  "dacă n-au date de migrație.",
       "cod": "import pandas as pd\n\n"
              "sci = pd.read_csv(\"date/curat/sci.csv\")\n"
              "rom = pd.read_csv(\"date/curat/romani.csv\")\n\n"
              "# pastram tot ce e in sci, adaugam ce gasim in rom\n"
              "d = pd.merge(sci, rom, {{1}}=\"cod\", how={{2}})\n\n"
              "# verificare: numarul de randuri nu trebuie sa creasca\n"
              "print(len(sci), \"->\", len(d))\n\n"
              "# cate tari au ramas fara date de migratie\n"
              "print(d[\"romani\"].{{3}}().sum())",
       "goluri": {
           "1": {"ok": ["on"], "ajutor": "parametrul"},
           "2": {"ok": ["\"left\"", "'left'"], "ajutor": "felul, cu ghilimele"},
           "3": {"ok": ["isna", "isnull"], "ajutor": "metoda"}},
       "laBine": "Cele două linii de verificare de la final sunt partea pe "
                 "care o sare toată lumea și e singura care prinde greșelile.",
       "laRau": "Felul îmbinării se scrie ca text, între ghilimele. Ultima "
                "metodă întoarce True acolo unde lipsește ceva.",
       "explicatie": "<code>how=\"left\"</code> spune limpede cine e tabelul "
                     "de bază. Verificarea de după nu e paranoia: dacă "
                     "<code>len(d)</code> e mai mare decât <code>len(sci)</code>, "
                     "ai chei duplicate în dreapta și tocmai ți-ai înmulțit "
                     "rândurile — exact capcana de la slide-ul următor."})
   + verif("c5-v3", 0,
           "După un <code>merge</code> cu <code>how=\"left\"</code>, tabelul "
           "are mai multe rânduri decât cel din stânga. Ce s-a întâmplat?",
           ["Tabelul din dreapta are cheia repetată pe mai multe rânduri",
            "Merge-ul a eșuat",
            "Trebuia folosit inner",
            "Au apărut rânduri goale"],
           "Un join potrivește fiecare rând din stânga cu <em>fiecare</em> "
           "rând din dreapta care are aceeași cheie. Dacă dreapta are cheia "
           "de trei ori, rândul din stânga iese de trei ori."),
   manual=
   "<h2>Scrie-o</h2>"
   "<p>Sintaxa e scurtă; grija e la ce scrii după ea. Cele două linii de "
   "verificare de la final valorează mai mult decât îmbinarea în sine.</p>"
   + ix("cod", "Lipește populația peste SCI", {
       "id": "c5-cod-merge", "fisier": "agregare/uneste.py",
       "sarcina": "Păstrezi toate țările din tabelul cu SCI.",
       "cod": "import pandas as pd\n\n"
              "sci = pd.read_csv(\"date/curat/sci.csv\")\n"
              "rom = pd.read_csv(\"date/curat/romani.csv\")\n\n"
              "d = pd.merge(sci, rom, {{1}}=\"cod\", how={{2}})\n\n"
              "print(len(sci), \"->\", len(d))\n"
              "print(d[\"romani\"].{{3}}().sum())",
       "goluri": {
           "1": {"ok": ["on"], "ajutor": "parametrul"},
           "2": {"ok": ["\"left\"", "'left'"], "ajutor": "felul"},
           "3": {"ok": ["isna", "isnull"], "ajutor": "metoda"}},
       "laBine": "Verificările de la final sunt partea importantă.",
       "laRau": "Felul îmbinării se scrie între ghilimele.",
       "explicatie": "Dacă <code>len(d)</code> e mai mare decât "
                     "<code>len(sci)</code>, ai chei duplicate în dreapta."}))


sl("s6", "Unirea tabelelor", "Când rândurile se înmulțesc",
   "<h2>Capcana care nu dă eroare</h2>"
   "<p>Același tabel <code>sci</code>, dar în dreapta populația e pe ani. "
   "Patru rânduri în stânga, patru în dreapta. Apasă <code>left</code>.</p>"
   + ix("imbinare", "Patru plus patru nu dau patru", {
       "id": "c5-imbinare-explozie", "cheie": "cod",
       "stanga": STANGA, "dreapta": DUBLE, "numeRez": "rezultat",
       "feluri": ["inner", "left"],
       "sarcina": "Numără rândurile care ies. Erau patru în stânga.",
       "explicatii": {
           "inner": "<b>Patru rânduri, din două chei.</b> Se potrivesc doar "
                    "MD și DE, dar MD apare de trei ori, fiindcă în dreapta "
                    "are trei ani. Valoarea SCI s-a copiat identic pe toate "
                    "trei. Dacă acum faci o medie pe SCI, MD cântărește de "
                    "trei ori cât DE.",
           "left": "<b>Șase rânduri, din patru.</b> MD de trei ori, DE o "
                   "dată, plus AT și HU cu goluri. Tabelul a crescut cu "
                   "cincizeci la sută fără să dea nicio eroare. Ăsta e tot "
                   "pericolul: codul merge, iar numerele de la final sunt "
                   "greșite."}})
   + nota("CUM TE APERI",
          "<code>pd.merge(..., validate=\"one_to_one\")</code> aruncă o eroare "
          "dacă cheia nu e unică. E o linie în plus care te scutește de o "
          "analiză refăcută."),
   dupa=verif("c5-v4", 2,
              "Vrei ca merge-ul să crape dacă o cheie apare de mai multe ori "
              "în dreapta. Ce adaugi?",
              ["how=\"inner\"",
               "on=[\"cod\", \"an\"]",
               "validate=\"one_to_one\"",
               "indicator=True"],
              "<code>validate</code> verifică relația dintre chei și aruncă "
              "eroare dacă nu e cea pe care ai promis-o. "
              "<code>indicator=True</code> e util și el, dar doar adaugă o "
              "coloană care spune de unde vine fiecare rând."),
   manual=
   "<h2>Capcana care nu dă eroare</h2>"
   "<p>Un join potrivește fiecare rând din stânga cu fiecare rând din dreapta "
   "care are aceeași cheie. Când cheia e unică de ambele părți, asta e ce "
   "aștepți. Când nu e, tabelul crește, iar valorile din stânga se copiază "
   "pe fiecare rând nou.</p>"
   "<p>Nu apare nicio eroare. Codul rulează, fișierul se scrie, iar mediile "
   "calculate după aceea sunt ponderate greșit, fiindcă unele țări apar de "
   "mai multe ori.</p>"
   + ix("imbinare", "Patru plus patru nu dau patru", {
       "id": "c5-imbinare-explozie", "cheie": "cod",
       "stanga": STANGA, "dreapta": DUBLE, "numeRez": "rezultat",
       "feluri": ["inner", "left"],
       "sarcina": "Numără rândurile care ies.",
       "explicatii": {
           "inner": "<b>Patru rânduri, din două chei.</b> MD apare de trei ori.",
           "left": "<b>Șase rânduri, din patru.</b> Tabelul a crescut fără "
                   "nicio eroare."}})
   + nota("CUM TE APERI",
          "<code>validate=\"one_to_one\"</code> aruncă o eroare dacă cheia nu "
          "e unică. Dacă vrei într-adevăr un rând pe țară și an, atunci cheia "
          "e <code>on=[\"cod\", \"an\"]</code>, nu doar codul."))


sl("s7", "Unirea tabelelor", "Când cheile nu se potrivesc",
   "<h2>Aceeași țară, trei scrieri</h2>"
   "<p>A doua capcană: cheile arată diferit, deci nu se potrivesc, deci "
   "<code>inner</code> întoarce un tabel gol și nimeni nu înțelege de ce.</p>"
   + tabel(["Sursă", "Cum scrie România", "Ce fel de cod"],
           [["Facebook SCI", "~RO", "ISO 3166-1 alpha-2"],
            ["Banca Mondială", "~ROU", "ISO 3166-1 alpha-3"],
            ["Eurostat", "~RO", "NUTS 0; dar Grecia e EL și Regatul Unit e UK"],
            ["Un fișier făcut de om", "~Romania, România, ROMANIA", "nimic"]])
   + ix("cod", "Fă-le să se potrivească", {
       "id": "c5-cod-chei", "fisier": "agregare/chei.py",
       "sarcina": "Banca Mondială dă coduri de trei litere, SCI dă două. "
                  "Aduci tabelul mare la cheia celui mic și verifici.",
       "cod": "# tabelul de traducere, adus o singura data\n"
              "harta = pd.read_csv(\"date/referinta/coduri.csv\")  # iso3, iso2\n\n"
              "# aducem codul de 3 litere la cel de 2\n"
              "bm = bm.merge(harta, {{1}}=\"iso3\", how=\"left\")\n\n"
              "# INAINTE de a imbina: cate chei chiar se potrivesc?\n"
              "comune = set(sci[\"cod\"]) {{2}} set(bm[\"iso2\"])\n"
              "print(len(comune), \"chei comune din\", len(set(sci[\"cod\"])))\n\n"
              "# abia acum\n"
              "d = sci.merge(bm, left_on=\"cod\", {{3}}=\"iso2\", how=\"left\")",
       "goluri": {
           "1": {"ok": ["on"], "ajutor": "parametrul"},
           "2": {"ok": ["&", "intersection"], "ajutor": "operatorul"},
           "3": {"ok": ["right_on"], "ajutor": "parametrul"}},
       "laBine": "Linia care numără cheile comune înainte de îmbinare e "
                 "obiceiul care te scutește de cele mai multe surprize.",
       "laRau": "Pentru intersecția a două mulțimi în Python e un singur "
                "caracter. Când coloanele-cheie au nume diferite, "
                "<code>on</code> se desface în două.",
       "explicatie": "Numărul tipărit de la mijloc e diagnosticul: dacă din "
                     "178 de chei se potrivesc 12, nu e o problemă de "
                     "<code>merge</code>, e o problemă de coduri, și se "
                     "repară înainte, nu după."})
   + verif("c5-v5", 3,
           "Un <code>merge</code> cu <code>how=\"inner\"</code> întoarce zero "
           "rânduri. Care e prima verificare?",
           ["Dacă fișierele s-au citit corect",
            "Dacă pandas e actualizat",
            "Dacă tabelele au aceeași mărime",
            "Dacă valorile cheii arată la fel în amândouă"],
           "Zero rânduri la <code>inner</code> înseamnă, aproape întotdeauna, "
           "chei care nu se potrivesc: <code>\"RO\"</code> față de "
           "<code>\"ROU\"</code>, sau <code>\"RO \"</code> cu un spațiu la "
           "final, sau <code>2020</code> ca text față de <code>2020</code> ca "
           "număr."),
   manual=
   "<h2>Aceeași țară, trei scrieri</h2>"
   "<p>Fiecare sursă are nomenclatorul ei, iar codurile seamănă suficient cât "
   "să pară interschimbabile. Nu sunt.</p>"
   + tabel(["Sursă", "Cum scrie România", "Ce fel de cod"],
           [["Facebook SCI", "~RO", "ISO 3166-1 alpha-2"],
            ["Banca Mondială", "~ROU", "ISO 3166-1 alpha-3"],
            ["Eurostat", "~RO", "NUTS 0; dar Grecia e EL și Regatul Unit e UK"],
            ["Un fișier făcut de om", "~Romania, România, ROMANIA", "nimic"]])
   + "<p>Mai există o capcană care nu se vede cu ochiul: tipul. "
     "<code>2020</code> citit ca text nu se potrivește cu <code>2020</code> "
     "citit ca număr, iar <code>merge</code> nu te avertizează, pur și simplu "
     "nu găsește nimic.</p>"
   + ix("cod", "Fă-le să se potrivească", {
       "id": "c5-cod-chei", "fisier": "agregare/chei.py",
       "sarcina": "Aduci tabelul mare la cheia celui mic și verifici.",
       "cod": "harta = pd.read_csv(\"date/referinta/coduri.csv\")  # iso3, iso2\n"
              "bm = bm.merge(harta, {{1}}=\"iso3\", how=\"left\")\n\n"
              "comune = set(sci[\"cod\"]) {{2}} set(bm[\"iso2\"])\n"
              "print(len(comune), \"chei comune din\", len(set(sci[\"cod\"])))\n\n"
              "d = sci.merge(bm, left_on=\"cod\", {{3}}=\"iso2\", how=\"left\")",
       "goluri": {
           "1": {"ok": ["on"], "ajutor": "parametrul"},
           "2": {"ok": ["&", "intersection"], "ajutor": "operatorul"},
           "3": {"ok": ["right_on"], "ajutor": "parametrul"}},
       "laBine": "Numără cheile comune înainte de îmbinare.",
       "laRau": "Intersecția a două mulțimi e un singur caracter.",
       "explicatie": "Dacă din 178 de chei se potrivesc 12, e o problemă de "
                     "coduri, nu de <code>merge</code>."}))


sl("s8", "Unirea tabelelor", "Unitatea de analiză",
   "<h2>Ce e un rând în tabelul vostru</h2>"
   "<p>Înainte de orice îmbinare, răspunsul la întrebarea asta. După, e prea "
   "târziu: tabelul are deja o formă, și de obicei nu cea pe care o voiai.</p>"
   + ix("sortare", "Ce unitate cere fiecare întrebare", {
       "id": "c5-sort-unitate",
       "sarcina": "Potrivește întrebarea de cercetare cu forma pe care "
                  "trebuie s-o aibă un rând.",
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
       "laBine": "Datele SCI sunt diadice: unitatea naturală e perechea, nu "
                 "țara. Ca să ajungi la o unitate „țară”, trebuie să agregi "
                 "explicit, și atunci alegi cum: sumă, medie, maxim.",
       "explicatie": "Unitatea de analiză decide tot ce urmează: ce chei "
                     "folosești la îmbinare, ce verifici cu "
                     "<code>validate</code>, și ce înseamnă o medie. Scris în "
                     "<code>decizii.md</code>, e o propoziție. Nescris, e "
                     "sursa a jumătate din confuziile unui proiect."})
   + nota("LA PROIECTUL VOSTRU",
          "Scrieți undeva, într-o propoziție: „un rând în tabelul nostru final "
          "înseamnă ___”. Dacă echipa dă două răspunsuri diferite, ăsta e "
          "lucrul de rezolvat azi, înaintea codului."),
   manual=
   "<h2>Ce e un rând în tabelul vostru</h2>"
   "<p>Unitatea de analiză e nivelul la care observi: țara, perechea de țări, "
   "țara-an, individul, gospodăria. Pare o chestiune de vocabular, dar "
   "decide forma tabelului final și, prin ea, ce întrebări poți pune.</p>"
   "<p>Datele voastre pornesc de la o unitate diadică: SCI măsoară legătura "
   "<em>dintre</em> două locuri, deci un rând e o pereche. Dacă vreți să "
   "spuneți ceva despre o țară, trebuie să agregați perechile, și atunci "
   "alegerea funcției de agregare e o decizie teoretică: suma spune „cât de "
   "conectată e în total”, media spune „cât de conectată e în medie”, iar "
   "maximul spune „cât de tare e cea mai puternică legătură a ei”. Trei "
   "lucruri diferite.</p>"
   + ix("sortare", "Ce unitate cere fiecare întrebare", {
       "id": "c5-sort-unitate",
       "sarcina": "Potrivește întrebarea cu forma unui rând.",
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
       "laBine": "Datele SCI sunt diadice: unitatea naturală e perechea.",
       "explicatie": "Unitatea de analiză decide ce chei folosești la "
                     "îmbinare și ce înseamnă o medie."}))


sl("s9", "Unirea tabelelor", "Agregarea",
   "<h2>De la perechi la țări</h2>"
   + ix("cod", "Adu datele la unitatea pe care o vrei", {
       "id": "c5-cod-agregare", "fisier": "agregare/agrega.py",
       "sarcina": "Ai un rând pe pereche. Vrei un rând pe țară, cu trei "
                  "măsuri diferite ale conectării.",
       "cod": "# un rand pe perechea (tara_sursa, tara_tinta)\n"
              "print(d.shape)\n\n"
              "t = (d\n"
              "     .{{1}}(\"tara_sursa\")\n"
              "     .agg(total=(\"sci\", \"sum\"),\n"
              "          medie=(\"sci\", {{2}}),\n"
              "          parteneri=(\"tara_tinta\", \"nunique\"))\n"
              "     .{{3}}())\n\n"
              "# acum un rand pe tara\n"
              "print(t.shape)",
       "goluri": {
           "1": {"ok": ["groupby"], "ajutor": "metoda"},
           "2": {"ok": ["\"mean\"", "'mean'"], "ajutor": "funcția, ca text"},
           "3": {"ok": ["reset_index"], "ajutor": "metoda"},
       },
       "laBine": "<code>reset_index()</code> de la final aduce cheia înapoi "
                 "ca o coloană obișnuită. Fără el, rămâne index, iar "
                 "<code>merge</code> de după n-o mai găsește.",
       "laRau": "Prima e metoda care grupează. A doua se scrie ca text, între "
                "ghilimele, ca și <code>\"sum\"</code> de deasupra.",
       "explicatie": "Cele trei măsuri nu sunt variante ale aceluiași lucru. "
                     "<code>total</code> favorizează țările cu mulți "
                     "parteneri, <code>medie</code> le pune pe toate pe picior "
                     "de egalitate, iar <code>parteneri</code> nu măsoară "
                     "deloc tăria, ci întinderea. Alegerea dintre ele e "
                     "teoretică, nu tehnică."})
   + verif("c5-v6", 1,
           "După <code>groupby</code> uiți <code>reset_index()</code>. Ce se "
           "întâmplă la <code>merge</code>-ul de după?",
           ["Merge-ul funcționează la fel",
            "Coloana-cheie nu mai există ca și coloană, e index",
            "Datele se pierd",
            "Pandas dă eroare de memorie"],
           "După <code>groupby</code>, cheia devine indexul. "
           "<code>merge(on=\"tara\")</code> caută o coloană cu numele ăsta și "
           "nu o găsește. Ori pui <code>reset_index()</code>, ori folosești "
           "<code>left_index=True</code>."),
   manual=
   "<h2>De la perechi la țări</h2>"
   "<p>Agregarea e locul în care datele își schimbă unitatea. E și locul în "
   "care se iau, pe tăcute, decizii teoretice: ce funcție folosești ca să "
   "rezumi mai multe rânduri într-unul singur.</p>"
   + ix("cod", "Adu datele la unitatea pe care o vrei", {
       "id": "c5-cod-agregare", "fisier": "agregare/agrega.py",
       "sarcina": "De la un rând pe pereche, la un rând pe țară.",
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
       "laBine": "<code>reset_index()</code> aduce cheia înapoi ca o coloană.",
       "laRau": "A doua se scrie ca text, între ghilimele.",
       "explicatie": "Suma favorizează țările cu mulți parteneri, media le "
                     "egalizează, numărul de parteneri măsoară întinderea, nu "
                     "tăria."}))


sl("s10", "Unirea tabelelor", "Join pe index",
   "<h2>Când cheia e chiar indexul</h2>"
   "<p><code>df1.join(df2)</code> e <code>merge</code> cu o singură "
   "presupunere: că te potrivești pe index, nu pe o coloană.</p>"
   + tabel(["Scrii", "Se potrivește pe", "Când e bun"],
           [["~a.merge(b, on=\"cod\")", "coloana cod, în amândouă",
             "cazul obișnuit"],
            ["~a.join(b)", "indexul amândurora", "după un groupby, sau la serii de timp"],
            ["~a.merge(b, left_on=\"cod\", right_index=True)",
             "coloană în stânga, index în dreapta", "amestecat"],
            ["~a.join(b, how=\"inner\")", "index, dar numai potrivirile",
             "join implicit e left, nu inner"]])
   + nota("DE REȚINUT",
          "<code>join</code> are <code>how=\"left\"</code> din oficiu, iar "
          "<code>merge</code> are <code>how=\"inner\"</code>. Două funcții "
          "care fac același lucru, cu implicit diferit: de aici vine o parte "
          "din confuzie."),
   dupa=verif("c5-v7", 2,
              "<code>pd.merge(a, b, on=\"cod\")</code>, fără "
              "<code>how</code>. Ce fel de îmbinare s-a făcut?",
              ["left, pentru că a e primul",
               "outer, ca să nu se piardă nimic",
               "inner, adică doar cheile comune",
               "Depinde de date"],
              "Implicitul lui <code>merge</code> e <code>inner</code>. De "
              "aceea se recomandă să scrii <code>how</code> de fiecare dată, "
              "chiar și când e cel implicit: cine citește codul vede ce ai "
              "vrut, nu ce s-a întâmplat."))


# ===========================================================================
#  11-18. Baze de date
# ===========================================================================

sl("s11", "Baze de date", "Ce e Neon",
   "<h2>Postgres, fără server de întreținut</h2>"
   "<p>Neon e PostgreSQL obișnuit, pus într-un loc în care nu trebuie să-l "
   "instalezi și nu trebuie să-l ții pornit.</p>"
   + ix("flux", "Ce se întâmplă când pui o întrebare", {
       "id": "c5-flux-neon",
       "buton": "Trimite o interogare",
       "dus": "întrebarea pleacă", "intors": "rândurile se întorc",
       "gata": "gata, ai rezultatul",
       "titlu": "Apasă pe o stație",
       "intro": "Patru locuri prin care trece un <code>select</code>.",
       "statii": [
           {"n": "Scriptul tău", "et": "pandas", "ic": "🐍", "c": "ceas",
            "d": "<code>pd.read_sql(\"select ...\", con)</code>. Aici nu se "
                 "întâmplă nimic special: e doar un text trimis mai departe."},
           {"n": "Conexiunea", "et": "psycopg", "ic": "🔌", "c": "salvie",
            "d": "Șirul de conectare spune unde e baza, cine ești și pe ce "
                 "canal criptat. Stă în <code>.env</code>, niciodată în cod."},
           {"n": "Compute", "et": "pornește la cerere", "ic": "⚡", "c": "accent",
            "d": "Partea care execută interogarea. Dacă n-a mai fost "
                 "întrebată nimic de câteva minute, e oprită, și prima "
                 "întrebare o trezește. De aici vine „serverless”, și tot de "
                 "aici vine întârzierea de o secundă la prima cerere."},
           {"n": "Storage", "et": "mereu acolo", "ic": "🗄️", "c": "text-2",
            "d": "Datele propriu-zise, separate de partea care calculează. "
                 "Fiindcă sunt separate, se poate face o ramură: o copie a "
                 "bazei pe care experimentezi, fără să atingi originalul."}]})
   + nota("CE SE VEDE DIN SLIDE-UL ĂSTA",
          "Separarea dintre compute și storage e motivul pentru care Neon "
          "poate face ramuri la fel ca Git: datele stau pe loc, se pornește "
          "doar altă parte care calculează peste ele."),
   manual=
   "<h2>Postgres, fără server de întreținut</h2>"
   "<p>Neon e o platformă care oferă PostgreSQL complet gestionat, accesibil "
   "prin SQL standard. Tot ce știți despre Postgres rămâne valabil: aceleași "
   "comenzi, aceleași tipuri, aceleași extensii.</p>"
   "<p>Trei lucruri o deosebesc de un Postgres pus pe un server:</p>"
   "<ul>"
   "<li><strong>Serverless.</strong> Partea care execută interogările pornește "
   "automat la prima cerere și se oprește când nu mai e folosită. Plătești "
   "cât folosești, iar pentru un proiect de curs asta înseamnă, de obicei, "
   "zero.</li>"
   "<li><strong>Branching.</strong> Poți face o copie izolată a bazei, ca o "
   "ramură în Git, ca să încerci o transformare fără să strici datele "
   "bune.</li>"
   "<li><strong>Compute separat de storage.</strong> Motivul tehnic din "
   "spatele primelor două.</li>"
   "</ul>"
   + ix("flux", "Ce se întâmplă când pui o întrebare", {
       "id": "c5-flux-neon",
       "buton": "Trimite o interogare",
       "dus": "întrebarea pleacă", "intors": "rândurile se întorc",
       "gata": "gata, ai rezultatul",
       "titlu": "Apasă pe o stație",
       "intro": "Patru locuri prin care trece un <code>select</code>.",
       "statii": [
           {"n": "Scriptul tău", "et": "pandas", "ic": "🐍", "c": "ceas",
            "d": "Un text SQL trimis mai departe."},
           {"n": "Conexiunea", "et": "psycopg", "ic": "🔌", "c": "salvie",
            "d": "Șirul de conectare stă în <code>.env</code>, niciodată în cod."},
           {"n": "Compute", "et": "pornește la cerere", "ic": "⚡", "c": "accent",
            "d": "Se trezește la prima întrebare. De aici întârzierea de o "
                 "secundă la prima cerere."},
           {"n": "Storage", "et": "mereu acolo", "ic": "🗄️", "c": "text-2",
            "d": "Datele, separate de partea care calculează. De aceea se pot "
                 "face ramuri."}]}))


sl("s12", "Baze de date", "Postgres sau MySQL",
   "<h2>Două baze, două profiluri</h2>"
   + ix("sortare", "Care bază, pentru ce", {
       "id": "c5-sort-baze",
       "sarcina": "Pune fiecare situație la baza care i se potrivește mai bine.",
       "elemente": [
           {"t": "Date geografice, cu PostGIS", "cos": 0},
           {"t": "Analitică pe date eterogene, cu JSONB", "cos": 0},
           {"t": "Magazin online cu trafic mare, multe citiri", "cos": 1},
           {"t": "Aplicație web simplă, CRUD", "cos": 1},
           {"t": "Căutare pe vectori, cu pgvector", "cos": 0},
           {"t": "Scrieri concurente multe, în paralel", "cos": 0}],
       "cosuri": [
           {"t": "PostgreSQL", "d": "puternic, flexibil, multe funcții avansate"},
           {"t": "MySQL", "d": "simplu, rapid pe citiri, foarte folosit în web"}],
       "laBine": "Proiectul vostru cade limpede pe Postgres: date eterogene, "
                 "potențial geografic, și analiză mai degrabă decât trafic.",
       "explicatie": "Niciuna nu e „mai bună”. MySQL e simplu și foarte rapid "
                     "la citiri, ceea ce îl face potrivit pentru aplicații web "
                     "cu trafic intens. Postgres are tipuri bogate (JSONB, "
                     "array-uri, tipuri proprii) și extensii puternice "
                     "(PostGIS pentru date geografice, pgvector pentru "
                     "căutare semantică), ceea ce îl face potrivit pentru "
                     "analiză."})
   + tabel(["Diferență", "PostgreSQL", "MySQL"],
           [["Caracter", "puternic, flexibil, multe funcții avansate",
             "simplu, ușor, foarte rapid în aplicații web"],
            ["Tipuri de date", "JSONB, PostGIS, array-uri, tipuri proprii",
             "tipuri clasice, plus JSON simplu"],
            ["Performanță", "scrieri concurente și analitic",
             "citiri rapide, CRUD"],
            ["Ecosistem", "extensii puternice: PostGIS, pgvector",
             "simplu, stabil, foarte răspândit în web"]]),
   manual=
   "<h2>Două baze, două profiluri</h2>"
   "<p>Întrebarea „care e mai bună” n-are răspuns; întrebarea „care e mai "
   "potrivită pentru ce fac eu” are.</p>"
   + tabel(["Diferență", "PostgreSQL", "MySQL"],
           [["Caracter", "puternic, flexibil, multe funcții avansate",
             "simplu, ușor, foarte rapid în aplicații web"],
            ["Tipuri de date", "JSONB, PostGIS, array-uri, tipuri proprii",
             "tipuri clasice, plus JSON simplu"],
            ["Performanță", "scrieri concurente și analitic",
             "citiri rapide, CRUD"],
            ["Folosire", "analitică, aplicații complexe, date eterogene, GIS",
             "aplicații web mari, e-commerce, trafic intens"],
            ["Ecosistem", "extensii puternice: PostGIS, pgvector",
             "simplu, stabil, foarte răspândit în web"]])
   + ix("sortare", "Care bază, pentru ce", {
       "id": "c5-sort-baze",
       "sarcina": "Pune fiecare situație la baza potrivită.",
       "elemente": [
           {"t": "Date geografice, cu PostGIS", "cos": 0},
           {"t": "Analitică pe date eterogene, cu JSONB", "cos": 0},
           {"t": "Magazin online cu trafic mare, multe citiri", "cos": 1},
           {"t": "Aplicație web simplă, CRUD", "cos": 1},
           {"t": "Căutare pe vectori, cu pgvector", "cos": 0},
           {"t": "Scrieri concurente multe, în paralel", "cos": 0}],
       "cosuri": [
           {"t": "PostgreSQL", "d": "puternic, flexibil, funcții avansate"},
           {"t": "MySQL", "d": "simplu, rapid pe citiri, web"}],
       "laBine": "Proiectul vostru cade limpede pe Postgres.",
       "explicatie": "Niciuna nu e „mai bună”: au profiluri diferite."}))


sl("s13", "Baze de date", "Conectarea",
   "<h2>Șirul de conectare, și unde stă</h2>"
   "<p>Un singur șir conține adresa, utilizatorul și parola. Dacă ajunge pe "
   "GitHub, baza voastră e a oricui.</p>"
   + ix("cod", "Conectează-te fără să scrii parola în cod", {
       "id": "c5-cod-conectare", "fisier": "baza/conecteaza.py",
       "sarcina": "Șirul vine din <code>.env</code>, nu din fișierul cu cod.",
       "cod": "import os\n"
              "import pandas as pd\n"
              "from dotenv import load_dotenv\n"
              "from sqlalchemy import create_engine\n\n"
              "# citeste .env si pune valorile in mediu\n"
              "{{1}}()\n\n"
              "# postgresql+psycopg://user:parola@host/baza?sslmode=require\n"
              "url = os.{{2}}(\"DATABASE_URL\")\n"
              "if not url:\n"
              "    raise SystemExit(\"lipseste DATABASE_URL din .env\")\n\n"
              "motor = {{3}}(url)\n\n"
              "# proba: daca merge linia asta, conexiunea e buna\n"
              "print(pd.read_sql(\"select version()\", motor).iloc[0, 0])",
       "goluri": {
           "1": {"ok": ["load_dotenv"], "ajutor": "funcția"},
           "2": {"ok": ["getenv", "environ.get"], "ajutor": "funcția"},
           "3": {"ok": ["create_engine"], "ajutor": "funcția"}},
       "laBine": "Linia cu <code>raise</code> pare de prisos până în ziua în "
                 "care cineva clonează depozitul fără <code>.env</code> și "
                 "primește o eroare de conectare de neînțeles.",
       "laRau": "Toate trei sunt importate sus, în primele patru linii.",
       "explicatie": "<code>.env</code> intră în <code>.gitignore</code> "
                     "înainte de primul <code>add</code>. În depozit pui un "
                     "<code>.env.exemplu</code> cu numele variabilelor și "
                     "valori false, ca să știe colegii ce le trebuie."})
   + nota("ATENȚIE", "Șirul de conectare conține parola în clar. Dacă îl pui "
                     "din greșeală într-un commit, nu e destul să-l ștergi: "
                     "rămâne în istorie. Schimbi parola din Neon, imediat."),
   manual=
   "<h2>Șirul de conectare, și unde stă</h2>"
   "<p>Neon vă dă un șir de forma "
   "<code>postgresql://utilizator:parola@gazdă/bază?sslmode=require</code>. "
   "Conține tot ce trebuie ca să intri în bază, inclusiv parola, în clar.</p>"
   "<p>Regula e simplă și n-are excepții: șirul stă într-un fișier "
   "<code>.env</code>, iar <code>.env</code> e în <code>.gitignore</code> de "
   "la început. În depozit pui un <code>.env.exemplu</code> cu numele "
   "variabilelor și valori false.</p>"
   + ix("cod", "Conectează-te fără să scrii parola în cod", {
       "id": "c5-cod-conectare", "fisier": "baza/conecteaza.py",
       "sarcina": "Șirul vine din <code>.env</code>.",
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
       "laBine": "Verificarea explicită scutește colegii de erori de neînțeles.",
       "laRau": "Toate trei sunt importate în primele patru linii.",
       "explicatie": "Dacă parola ajunge într-un commit, o schimbi din Neon: "
                     "ștergerea din fișier nu o scoate din istorie."}))


sl("s14", "Baze de date", "Scrii și citești",
   "<h2>Tabelul vostru, în bază</h2>"
   + ix("cod", "Pune tabelul curat în Postgres", {
       "id": "c5-cod-tosql", "fisier": "baza/incarca.py",
       "sarcina": "Scrii tabelul, apoi îl citești înapoi ca să verifici.",
       "cod": "d = pd.read_csv(\"date/curat/tabel_final.csv\")\n\n"
              "# scrie tabelul; daca exista deja, il inlocuieste\n"
              "d.to_sql(\"sci_tari\", motor, if_exists={{1}}, index=False)\n\n"
              "# citeste inapoi si compara\n"
              "verif = pd.{{2}}(\"select count(*) as n from sci_tari\", motor)\n"
              "print(len(d), \"scrise,\", verif[\"n\"][0], \"gasite\")\n\n"
              "# o cheie primara, ca baza sa refuze duplicatele\n"
              "with motor.begin() as c:\n"
              "    c.exec_driver_sql(\n"
              "        \"alter table sci_tari add {{3}} (cod)\")",
       "goluri": {
           "1": {"ok": ["\"replace\"", "'replace'"], "ajutor": "ce face dacă există"},
           "2": {"ok": ["read_sql", "read_sql_query"], "ajutor": "funcția"},
           "3": {"ok": ["primary key", "primary key", "PRIMARY KEY"],
                 "ajutor": "constrângerea"}},
       "laBine": "Cheia primară e lucrul pe care un CSV nu-l poate face: de "
                 "acum baza refuză un al doilea rând cu același cod.",
       "laRau": "Primul se scrie ca text, între ghilimele: "
                "<code>\"replace\"</code>, <code>\"append\"</code> sau "
                "<code>\"fail\"</code>.",
       "explicatie": "<code>if_exists=\"replace\"</code> șterge tabelul și-l "
                     "scrie din nou. E ce vrei cât timp construiești, dar "
                     "atenție: într-o bază pe care o folosesc și alții, "
                     "<code>\"append\"</code> e mai cuminte, iar "
                     "<code>\"fail\"</code> e cel mai cuminte."})
   + verif("c5-v8", 0,
           "Rulezi scriptul de încărcare de două ori, cu "
           "<code>if_exists=\"append\"</code> și fără cheie primară. Ce ai în "
           "bază?",
           ["Fiecare rând de două ori",
            "Același lucru ca la prima rulare",
            "O eroare",
            "Doar rândurile noi"],
           "<code>append</code> adaugă, fără să se uite dacă rândul există "
           "deja. Cheia primară e singura care oprește asta, și o oprește cu "
           "o eroare — ceea ce e exact ce vrei."),
   manual=
   "<h2>Tabelul vostru, în bază</h2>"
   "<p><code>to_sql</code> și <code>read_sql</code> sunt cele două capete ale "
   "drumului. Între ele, singura grijă e ce se întâmplă când rulezi scriptul "
   "a doua oară.</p>"
   + ix("cod", "Pune tabelul curat în Postgres", {
       "id": "c5-cod-tosql", "fisier": "baza/incarca.py",
       "sarcina": "Scrii tabelul, apoi îl citești înapoi ca să verifici.",
       "cod": "d = pd.read_csv(\"date/curat/tabel_final.csv\")\n\n"
              "d.to_sql(\"sci_tari\", motor, if_exists={{1}}, index=False)\n\n"
              "verif = pd.{{2}}(\"select count(*) as n from sci_tari\", motor)\n"
              "print(len(d), \"scrise,\", verif[\"n\"][0], \"gasite\")\n\n"
              "with motor.begin() as c:\n"
              "    c.exec_driver_sql(\n"
              "        \"alter table sci_tari add {{3}} (cod)\")",
       "goluri": {
           "1": {"ok": ["\"replace\"", "'replace'"], "ajutor": "ce face dacă există"},
           "2": {"ok": ["read_sql", "read_sql_query"], "ajutor": "funcția"},
           "3": {"ok": ["primary key", "PRIMARY KEY"], "ajutor": "constrângerea"}},
       "laBine": "Cheia primară e lucrul pe care un CSV nu-l poate face.",
       "laRau": "Primul se scrie între ghilimele.",
       "explicatie": "<code>\"replace\"</code> cât timp construiești, "
                     "<code>\"append\"</code> sau <code>\"fail\"</code> "
                     "într-o bază folosită și de alții."}))


sl("s15", "Baze de date", "SQL, cât vă trebuie",
   "<h2>Patru cuvinte și o ordine</h2>"
   "<p>Aceeași operație pe care o faceți în pandas, scrisă în limba bazei. "
   "Avantajul e că filtrarea se face acolo, și vine înapoi doar ce ai cerut.</p>"
   + ix("cod", "Scrie interogarea", {
       "id": "c5-cod-sql", "fisier": "baza/intrebari.sql",
       "sarcina": "Cele zece țări cu cei mai mulți români, și cât de legată "
                  "e România de fiecare.",
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
           "1": {"ok": ["join", "inner join", "JOIN"], "ajutor": "cum legi tabelele"},
           "2": {"ok": ["where", "WHERE"], "ajutor": "filtrarea"},
           "3": {"ok": ["desc", "DESC"], "ajutor": "ordinea"}},
       "laBine": "<code>join ... on</code> e exact <code>pd.merge(..., "
                 "on=...)</code>, scris altfel. Aceleași feluri: "
                 "<code>left join</code>, <code>full outer join</code>.",
       "laRau": "Primul leagă două tabele pe o condiție. Al doilea filtrează "
                "rândurile. Al treilea pune cele mai mari valori sus.",
       "explicatie": "Ordinea în care se scrie nu e ordinea în care se "
                     "execută: baza filtrează întâi "
                     "(<code>where</code>), apoi grupează, apoi sortează, "
                     "apoi taie (<code>limit</code>). De asta "
                     "<code>limit 10</code> nu face interogarea de zece ori "
                     "mai rapidă: tot tabelul a fost parcurs oricum."})
   + nota("Ce iese",
          "Italia, Germania, Spania sus la migrație, cu SCI-uri care nu urmează "
          "aceeași ordine. E ghicitoarea din cursul 1, de data asta scoasă cu "
          "o interogare.", True),
   manual=
   "<h2>Patru cuvinte și o ordine</h2>"
   "<p>N-aveți nevoie de SQL avansat. Aveți nevoie de cinci construcții, care "
   "acoperă aproape tot ce faceți în pandas.</p>"
   + tabel(["În pandas", "În SQL"],
           [["~d[d.cod == 'RO']", "~where cod = 'RO'"],
            ["~d.merge(t, on='cod')", "~join tari t on t.cod = d.cod"],
            ["~d.groupby('cod').sum()", "~group by cod"],
            ["~d.sort_values('sci', ascending=False)", "~order by sci desc"],
            ["~d.head(10)", "~limit 10"]])
   + ix("cod", "Scrie interogarea", {
       "id": "c5-cod-sql", "fisier": "baza/intrebari.sql",
       "sarcina": "Cele zece țări cu cei mai mulți români, cu SCI-ul lor.",
       "cod": "select m.geo, m.persoane, s.sci\n"
              "from migratie m\n"
              "{{1}} legaturi s on s.tara_1 = 'RO' and s.tara_2 = m.geo\n"
              "{{2}} m.citizen = 'RO'\n"
              "order by m.persoane {{3}}\n"
              "limit 10;",
       "goluri": {
           "1": {"ok": ["join", "inner join", "JOIN"], "ajutor": "cum legi tabelele"},
           "2": {"ok": ["where", "WHERE"], "ajutor": "filtrarea"},
           "3": {"ok": ["desc", "DESC"], "ajutor": "ordinea"}},
       "laBine": "<code>join ... on</code> e <code>pd.merge</code> scris altfel.",
       "laRau": "Al treilea pune valorile mari sus.",
       "explicatie": "Ordinea de scriere nu e ordinea de execuție: "
                     "<code>where</code>, apoi grupare, apoi sortare, apoi "
                     "<code>limit</code>."}))


sl("s16", "Baze de date", "Ramurile bazei",
   "<h2>Un branch, dar pentru date</h2>"
   "<p>Aceeași idee ca la Git, altceva ramificat: nu codul, ci baza.</p>"
   + tabel(["Situație", "Fără ramură", "Cu ramură"],
           [["Vrei să încerci o transformare mare",
             "faci o copie a bazei, manual", "o ramură, în câteva secunde"],
            ["Vrei să testezi scriptul de încărcare",
             "scrii peste datele bune", "scrii în ramură, le compari"],
            ["Doi colegi lucrează în paralel",
             "se calcă pe tabele", "fiecare pe ramura lui"],
            ["Ai stricat ceva",
             "restaurezi din backup, dacă ai", "ștergi ramura"]])
   + nota("PENTRU PROIECT",
          "Nu e obligatoriu, dar e ieftin: faceți o ramură înainte de "
          "încărcarea mare, și o ștergeți după ce ați verificat. E cel mai "
          "simplu fel de a nu pierde o după-amiază."),
   dupa=verif("c5-v9", 1,
              "De ce poate Neon să facă ramuri atât de repede?",
              ["Pentru că bazele sunt mici",
               "Pentru că datele stau separat de partea care calculează",
               "Pentru că folosește Git intern",
               "Pentru că face copii noaptea"],
              "Separarea compute–storage: ramura nu copiază datele, pornește "
              "doar altă parte care calculează peste aceleași date, și scrie "
              "separat doar ce se schimbă."))


sl("s17", "Baze de date", "Unde faci ce",
   "<h2>În bază, sau în pandas?</h2>"
   "<p>Aceeași operație se poate scrie în amândouă. Regula practică: "
   "<strong>filtrezi și agregi în bază, analizezi în pandas.</strong></p>"
   + ix("sortare", "Unde e mai bine", {
       "id": "c5-sort-unde",
       "sarcina": "Unde faci fiecare lucru?",
       "elemente": [
           {"t": "Iei doar anii 2018–2022 din 40 de milioane de rânduri", "cos": 0},
           {"t": "Numeri rândurile pe fiecare țară", "cos": 0},
           {"t": "Faci un grafic", "cos": 1},
           {"t": "Rulezi o regresie", "cos": 1},
           {"t": "Legi două tabele mari, pe cheie", "cos": 0},
           {"t": "Încerci cinci variante de transformare, rând pe rând", "cos": 1}],
       "cosuri": [
           {"t": "În bază, cu SQL", "d": "unde datele sunt multe și vrei puține"},
           {"t": "În pandas", "d": "unde datele sunt deja puține și vrei să te joci"}],
       "laBine": "Linia de despărțire e cantitatea: adu în memorie ce ai "
                 "nevoie, nu tot.",
       "explicatie": "Un <code>select</code> cu <code>where</code> și "
                     "<code>group by</code> lasă baza să facă munca grea și "
                     "aduce înapoi un tabel mic. Odată ce tabelul e mic și "
                     "încape în memorie, pandas e mai comod pentru orice "
                     "altceva: încerci, greșești, încerci din nou, fără să "
                     "mai aștepți rețeaua."}),
   manual=
   "<h2>În bază, sau în pandas?</h2>"
   "<p>Întrebarea apare la fiecare pas, iar răspunsul e aproape mereu același: "
   "lasă baza să reducă datele, și adu în pandas doar ce a rămas.</p>"
   "<p>Motivul nu e viteza bazei în sine, ci rețeaua: fiecare rând adus "
   "costă. Un <code>select count(*) group by tara</code> trimite înapoi "
   "câteva sute de rânduri; același lucru făcut prin citirea întregului "
   "tabel în pandas trimite milioane.</p>"
   + ix("sortare", "Unde e mai bine", {
       "id": "c5-sort-unde",
       "sarcina": "Unde faci fiecare lucru?",
       "elemente": [
           {"t": "Iei doar anii 2018–2022 din 40 de milioane de rânduri", "cos": 0},
           {"t": "Numeri rândurile pe fiecare țară", "cos": 0},
           {"t": "Faci un grafic", "cos": 1},
           {"t": "Rulezi o regresie", "cos": 1},
           {"t": "Legi două tabele mari, pe cheie", "cos": 0},
           {"t": "Încerci cinci variante de transformare, rând pe rând", "cos": 1}],
       "cosuri": [
           {"t": "În bază, cu SQL", "d": "datele sunt multe, vrei puține"},
           {"t": "În pandas", "d": "datele sunt deja puține"}],
       "laBine": "Adu în memorie ce ai nevoie, nu tot.",
       "explicatie": "Baza face munca grea, pandas face explorarea."}))


# ===========================================================================
#  19-21. Proiectul
# ===========================================================================

sl("s19", "Proiectul tău", "Fă tabelul final",
   "<h2>Un tabel, o unitate, o bază</h2>"
   "<p>Ce aveți de făcut până data viitoare.</p>"
   + ix("etape", "Pașii", {
       "titlu": "Patru pași", "intro": "Apasă pe fiecare.",
       "etape": [
           {"nume": "Scrieți unitatea", "unde": "decizii.md",
            "text": "O propoziție: „un rând în tabelul nostru final înseamnă "
                    "___”. Toată echipa trebuie să dea același răspuns."},
           {"nume": "Îmbinați", "unde": "agregare/uneste.py",
            "text": "Un script care pornește de la fișierele curate și scoate "
                    "un singur tabel. Cu <code>how</code> scris explicit, cu "
                    "<code>validate</code>, și cu numărul de rânduri tipărit "
                    "înainte și după."},
           {"nume": "Încărcați", "unde": "baza/incarca.py",
            "text": "Tabelul în Neon, cu o cheie primară. Șirul de conectare "
                    "în <code>.env</code>, și <code>.env</code> în "
                    "<code>.gitignore</code>."},
           {"nume": "Puneți o întrebare", "unde": "baza/intrebari.sql",
            "text": "Un <code>select</code> scris de voi, care răspunde la "
                    "ceva din întrebarea voastră de cercetare. Nu trebuie să "
                    "fie complicat, trebuie să fie al vostru."}]})
   + ix("dovada", "Dovada", {
       "id": "c5-dovada-baza",
       "sarcina": "Rulează comenzile și lipește ce scrie.",
       "pasi": [
           {"t": "Îmbinarea nu a înmulțit rândurile",
            "cmd": "python agregare/uneste.py",
            "gol": "lipește linia cu înainte -> după",
            "cauta": r"\d+[\s\S]*\d+",
            "daca_nu": "Caut două numere: câte rânduri aveai și câte ai acum. "
                       "Dacă scriptul nu le tipărește, adaugă linia de la "
                       "slide-ul 5."},
           {"t": "Tabelul e în bază",
            "cmd": "python -c \"import baza.conecteaza as b, pandas as pd; "
                   "print(pd.read_sql('select count(*) from sci_tari', b.motor))\"",
            "gol": "lipește numărul",
            "cauta": r"\d+",
            "daca_nu": "Caut numărul de rânduri din tabel. Dacă dă eroare de "
                       "conectare, verifică DATABASE_URL din .env."},
           {"t": "Secretele nu sunt în depozit",
            "cmd": "git check-ignore -v .env",
            "gol": "lipește linia",
            "cauta": r"gitignore",
            "daca_nu": "Dacă nu scrie nimic, <code>.env</code> NU e ignorat. "
                       "Adaugă-l în <code>.gitignore</code> acum."}],
       "explicatie": "Ultimul pas e cel mai important dintre cele trei. "
                     "Celelalte două se pot repara oricând; o parolă ajunsă "
                     "în istorie, nu."}),
   manual=
   "<h2>Un tabel, o unitate, o bază</h2>"
   "<p>Pasul de proiect al acestei lecții are patru bucăți, iar a patra e cea "
   "care arată că baza de date v-a folosit la ceva, nu doar că există.</p>"
   + ix("etape", "Pașii", {
       "titlu": "Patru pași", "intro": "Apasă pe fiecare.",
       "etape": [
           {"nume": "Scrieți unitatea", "unde": "decizii.md",
            "text": "„Un rând în tabelul nostru final înseamnă ___”."},
           {"nume": "Îmbinați", "unde": "agregare/uneste.py",
            "text": "Un script de la fișierele curate la un singur tabel."},
           {"nume": "Încărcați", "unde": "baza/incarca.py",
            "text": "Tabelul în Neon, cu cheie primară, cu secretele în .env."},
           {"nume": "Puneți o întrebare", "unde": "baza/intrebari.sql",
            "text": "Un select al vostru, legat de întrebarea de cercetare."}]})
   + ix("dovada", "Dovada", {
       "id": "c5-dovada-baza",
       "sarcina": "Rulează comenzile și lipește ce scrie.",
       "pasi": [
           {"t": "Îmbinarea nu a înmulțit rândurile",
            "cmd": "python agregare/uneste.py",
            "gol": "lipește linia cu înainte -> după",
            "cauta": r"\d+[\s\S]*\d+",
            "daca_nu": "Caut două numere: înainte și după."},
           {"t": "Tabelul e în bază",
            "cmd": "python -c \"import baza.conecteaza as b, pandas as pd; "
                   "print(pd.read_sql('select count(*) from sci_tari', b.motor))\"",
            "gol": "lipește numărul",
            "cauta": r"\d+",
            "daca_nu": "Verifică DATABASE_URL din .env."},
           {"t": "Secretele nu sunt în depozit",
            "cmd": "git check-ignore -v .env",
            "gol": "lipește linia",
            "cauta": r"gitignore",
            "daca_nu": "Dacă nu scrie nimic, .env nu e ignorat."}],
       "explicatie": "Ultimul pas e cel mai important dintre cele trei."}))


sl("s20", "Proiectul tău", "Unitatea voastră",
   "<h2>Scrieți-o acum</h2>"
   + ix("asteptari", "Un rând în tabelul vostru", {
       "id": "c5-unitate", "tip": "unitate", "minim": 40,
       "sarcina": "Completează: „Un rând în tabelul nostru final înseamnă "
                  "___, iar cheia care îl identifică e ___.”",
       "exemplu": "De exemplu: un rând înseamnă o pereche de țări, cu SCI, "
                  "migranții în ambele direcții și distanța, iar cheia e "
                  "(tara_1, tara_2). Sau: un rând e o pereche județ românesc, "
                  "provincie italiană, cu cheia (judet, provincie).",
       "multumesc": "O citesc înainte de cursul următor, și o compar cu ce "
                    "scrie în decizii.md."}),
   manual=
   "<h2>Scrieți-o acum</h2>"
   "<p>Propoziția asta pare banală până o scrieți: de obicei e momentul în "
   "care echipa descoperă că doi membri lucrau la tabele cu forme diferite.</p>"
   + ix("asteptari", "Un rând în tabelul vostru", {
       "id": "c5-unitate", "tip": "unitate", "minim": 40,
       "sarcina": "Completează: „Un rând în tabelul nostru final înseamnă "
                  "___, iar cheia care îl identifică e ___.”",
       "exemplu": "De exemplu: o pereche de țări, cu cheia (tara_1, tara_2).",
       "multumesc": "O citesc înainte de cursul următor."}))


sl("s21", "Mai departe", "Până data viitoare",
   "<h2>Cursul 6: analiza exploratorie</h2>"
   "<p>Aveți un tabel. Data viitoare ne uităm la el: statistici descriptive, "
   "vizualizare exploratorie, și ce se vede într-un grafic dar nu într-un "
   "rezumat numeric.</p>"
   + tabel(["Ce aduceți", "Unde"],
           [["Tabelul final, îmbinat", "~date/curat/tabel_final.csv"],
            ["Scriptul de îmbinare", "~agregare/uneste.py"],
            ["Tabelul încărcat în Neon", "o captură cu numărul de rânduri"],
            ["Unitatea de analiză, scrisă", "~decizii.md"],
            ["Un select al vostru", "~baza/intrebari.sql"]])
   + nota("DACĂ V-A RĂMAS CEVA",
          "Manualul lecției are tot ce am spus azi, pe larg, și puteți relua "
          "exercițiile de câte ori vreți. Ce faceți acolo se vede la mine, "
          "dar nu e obligatoriu și nu se notează."),
   manual=
   "<h2>Cursul 6: analiza exploratorie</h2>"
   "<p>Cu tabelul final în mână, lecția următoare e despre cum te uiți la el: "
   "statistici descriptive, distribuții, și vizualizare exploratorie, adică "
   "graficele pe care le faci pentru tine, nu pentru raport.</p>"
   + tabel(["Ce aduceți", "Unde"],
           [["Tabelul final, îmbinat", "~date/curat/tabel_final.csv"],
            ["Scriptul de îmbinare", "~agregare/uneste.py"],
            ["Tabelul încărcat în Neon", "o captură cu numărul de rânduri"],
            ["Unitatea de analiză, scrisă", "~decizii.md"],
            ["Un select al vostru", "~baza/intrebari.sql"]]))


L.scrie_tot()
