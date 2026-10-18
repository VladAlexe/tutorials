# -*- coding: utf-8 -*-
"""
Lecția 3: Versionare și colaborare cu Git.

Urmează prezentarea Curs_3.pptx: ce face Git, repository-uri, credențiale,
GitHub, legarea depozitului local de cel de pe GitHub, și încadrarea teoretică
a proiectului, cu exemplul lucrat pe tranzițiile energetice.

Ce am adăugat peste prezentare, și de ce:
  - cele trei zone (lucru, pregătire, istoric), pentru că fără ele comenzile
    lui Git se învață pe de rost și se uită până săptămâna următoare;
  - .gitignore, pentru că prima greșeală serioasă a unei echipe e un fișier
    cu parole urcat din neatenție, și se repară greu;
  - ramurile și pull request-ul, anunțate în titlul cursului, dar fără slide;
  - explorarea inițială a datelor colectate la cursul 2, care închide bucla.

Rulare:  python _build/c3.py
"""

from comun import Lectie, ix, verif, tabel, nota

def templu(acoperis, stalpi, baza, et_sus="Întrebarea"):
    """Un cadru teoretic desenat ca templu: literatura e temelia, pilonii
    sunt conceptele cu datele lor, iar întrebarea stă deasupra, pe toți."""
    st = "".join(
        f'<div class="pil__s"><div class="pil__n">{n}</div>'
        f'<div class="pil__d">{d}</div><div class="pil__r">{r}</div></div>'
        for n, d, r in stalpi)
    return (f'<div class="pil" style="--n:{len(stalpi)}">'
            f'<div class="pil__acoperis"><span>{et_sus}</span><b>{acoperis}</b></div>'
            f'<div class="pil__stalpi">{st}</div>'
            f'<div class="pil__baza"><span>temelia</span>{baza}</div></div>')


L = Lectie(3, "c3-versionare-git", "Versionare și colaborare cu Git",
           "Ce face Git, cum se leagă depozitul local de GitHub, cum lucrează "
           "o echipă fără să se calce, și cum se încadrează teoretic un proiect.")
sl = L.sl


# ===========================================================================
#  1-2. Cursul
# ===========================================================================

AGENDA = [
    ("Ce face Git", "azi", "Istoric, reveniri, și de ce lucrează local."),
    ("Depozitul și contul", "azi", "git init, credențiale, primul commit."),
    ("GitHub", "azi", "Legarea depozitului local de cel de pe internet."),
    ("Lucrul în echipă", "azi", "Ramuri, pull request, conflicte."),
    ("Încadrarea teoretică", "azi", "De la o grămadă de date la o întrebare de cercetare."),
    ("Explorarea inițială", "azi", "Prima privire peste migrația colectată săptămâna trecută."),
]

sl("s1", "Cursul", "Despre ce e ora de azi",
   "<h2>Versionare și colaborare cu Git</h2>"
   "<p class=\"cheie\">Săptămâna trecută ai adus date. Azi faci în așa fel "
   "încât ele, și codul care le-a adus, să nu se mai piardă.</p>"
   + ix("etape", "Agenda",
        {"titlu": "Ora de azi", "intro": "Apasă pe oricare.",
         "etape": [{"nume": n, "unde": u, "text": d} for n, u, d in AGENDA]},
        "Apasă pe un punct ca să vezi ce intră în el."),
   manual=
   "<h2>Versionare și colaborare cu Git</h2>"
   "<p>Ora de azi are două jumătăți care par fără legătură, dar nu sunt. În "
   "prima învățăm Git, adică felul în care un proiect își ține minte propria "
   "istorie. În a doua punem întrebarea de cercetare a proiectului vostru.</p>"
   "<p>Legătura dintre ele e asta: un proiect de analiză nu e o grămadă de "
   "fișiere, e un drum. Git păstrează drumul, iar cadrul teoretic spune "
   "încotro duce. Fără primul, nu poți arăta cum ai ajuns; fără al doilea, nu "
   "poți spune de ce ai pornit.</p>"
   + ix("etape", "Agenda",
        {"titlu": "Ora de azi", "intro": "Apasă pe oricare.",
         "etape": [{"nume": n, "unde": u, "text": d} for n, u, d in AGENDA]}))

sl("s2", "Cursul", "Unde ai rămas",
   "<h2>De la cursul trecut</h2>"
   "<ul>"
   "<li>un script care cere date de la un API</li>"
   "<li><code>migratie.csv</code> și indicatorii, în <code>date/brute/</code></li>"
   "<li>amândouă, deocamdată, doar pe laptopul tău</li>"
   "</ul>"
   "<p>Exact asta reparăm azi.</p>")


# ===========================================================================
#  3-5. Ce face Git
# ===========================================================================

CE_FACE = [
    ("Ține minte fiecare schimbare", "istoric",
     "Nu doar ultima versiune: toate, cu cine a făcut-o și când."),
    ("Te duce înapoi", "reveniri",
     "La orice versiune de dinainte, fără să pierzi ce ai acum."),
    ("Lasă mai mulți oameni să lucreze", "colaborare",
     "Pe aceleași fișiere, în același timp, și le îmbină după."),
    ("Ține tot într-un singur dosar", "un singur loc",
     "Istoria întreagă stă în <code>.git</code>, lângă proiect. Nu în cloud, nu la altcineva."),
    ("Permite încercări fără risc", "ramuri",
     "Faci o ramură, strici ce vrei pe ea, iar codul principal rămâne întreg."),
    ("Funcționează local", "fără internet",
     "Git merge în tren. GitHub e doar locul unde sincronizezi."),
]

sl("s3", "Ce face Git", "La ce e bun",
   "<h2>Ce face Git</h2>"
   + ix("etape", "Șase lucruri",
        {"titlu": "Git, pe scurt", "intro": "Apasă pe oricare.",
         "etape": [{"nume": n, "unde": u, "text": d} for n, u, d in CE_FACE]},
        "Ultimul e cel care se înțelege cel mai greu și contează cel mai mult.")
   + "<p class=\"cheie\">Git lucrează pe calculatorul tău. GitHub e doar locul "
     "unde îți sincronizezi proiectele.</p>",
   manual=
   "<h2>Ce face Git</h2>"
   "<p>Un sistem de versionare rezolvă o problemă pe care toată lumea a avut-o "
   "înainte să știe că are un nume: fișiere numite "
   "<code>analiza_final_v2_FINAL_bun.py</code>, și nimeni care să-și amintească "
   "ce era diferit în <code>v1</code>.</p>"
   + ix("etape", "Șase lucruri",
        {"titlu": "Git, pe scurt", "intro": "Apasă pe oricare.",
         "etape": [{"nume": n, "unde": u, "text": d} for n, u, d in CE_FACE]})
   + nota("Distincția care se uită cel mai des",
          "Git și GitHub nu sunt același lucru. Git e programul de pe "
          "calculatorul tău, care ține istoria. GitHub e un site care "
          "găzduiește copii ale acelei istorii. Poți folosi Git fără GitHub "
          "toată viața; invers, nu."))

sl("s4", "Ce face Git", "Cele trei zone",
   "<h2>Unde stau fișierele tale</h2>"
   "<p>Comenzile lui Git par arbitrare până vezi că mută lucruri între trei "
   "zone. După aceea se țin minte singure.</p>"
   + ix("zone", "Mută-le tu",
        {"id": "c3-zone",
         "sarcina": "Ai două fișiere în dosar. Du-le până pe GitHub, apăsând "
                    "comenzile în ordinea potrivită. <code>git status</code> "
                    "nu mută nimic, dar îți spune unde ești.",
         "fisiere": ["colectare.py", "README.md"]})
   + ix("sortare", "Ce face fiecare comandă", {
       "id": "c3-sort-zone", "poarta": False,
       "sarcina": "Pune fiecare comandă în dreptul a ceea ce face.",
       "elemente": [{"t": "git add", "cos": 0}, {"t": "git commit", "cos": 1},
                    {"t": "git push", "cos": 2}, {"t": "git pull", "cos": 3},
                    {"t": "git status", "cos": 4}],
       "cosuri": [{"t": "Alege ce intră", "d": "din dosar în pregătire"},
                  {"t": "Scrie în istoric", "d": "din pregătire în istoricul local"},
                  {"t": "Trimite sus", "d": "din local pe GitHub"},
                  {"t": "Aduce jos", "d": "de pe GitHub în local"},
                  {"t": "Spune unde ești", "d": "nu mută nimic"}],
       "laBine": "Dacă ții minte tabloul ăsta, nu mai trebuie să ții minte "
                 "comenzile: le deduci.",
       "explicatie": "<code>git status</code> e singura care nu schimbă nimic, "
                     "și tocmai de aceea se dă cel mai des. Când nu știi ce se "
                     "întâmplă, o dai pe ea întâi."}),
   manual=
   "<h2>Cele trei zone</h2>"
   "<p>Ăsta e modelul mental fără de care Git pare un set de incantații. Nu e "
   "în prezentarea de la curs, dar fără el comenzile se învață pe de rost și "
   "se uită până săptămâna viitoare.</p>"
   + ix("zone", "Mută-le tu",
        {"id": "c3-zone",
         "sarcina": "Du cele două fișiere până pe GitHub, apăsând comenzile.",
         "fisiere": ["colectare.py", "README.md"]})
   + tabel(["Zona", "Ce e acolo", "Cum ajunge mai departe"], [
       ["Dosarul de lucru", "fișierele pe care le editezi", "~git add"],
       ["Zona de pregătire", "ce ai ales pentru următorul commit", "~git commit"],
       ["Istoricul local", "commit-urile tale, pe laptop", "~git push"],
       ["GitHub", "copia de pe internet", "~git pull, înapoi"],
   ])
   + "<p>Zona de pregătire pare un pas în plus, inutil. Rostul ei e să poți "
     "face un commit cu trei din cele șapte fișiere pe care le-ai atins, "
     "pentru că numai alea trei țin de aceeași schimbare.</p>"
   + ix("sortare", "Ce face fiecare comandă", {
       "id": "c3-sort-zone", "poarta": False,
       "sarcina": "Pune fiecare comandă în dreptul a ceea ce face.",
       "elemente": [{"t": "git add", "cos": 0}, {"t": "git commit", "cos": 1},
                    {"t": "git push", "cos": 2}, {"t": "git pull", "cos": 3},
                    {"t": "git status", "cos": 4}],
       "cosuri": [{"t": "Alege ce intră", "d": "din dosar în pregătire"},
                  {"t": "Scrie în istoric", "d": "din pregătire în istoricul local"},
                  {"t": "Trimite sus", "d": "din local pe GitHub"},
                  {"t": "Aduce jos", "d": "de pe GitHub în local"},
                  {"t": "Spune unde ești", "d": "nu mută nimic"}],
       "laBine": "Dacă ții minte tabloul ăsta, nu mai trebuie să ții minte comenzile.",
       "explicatie": "<code>git status</code> nu schimbă nimic, deci se poate "
                     "da oricând, de oricâte ori."}))

sl("s5", "Ce face Git", "Verificare",
   "<h2>Git sau GitHub</h2>")


# ===========================================================================
#  6-9. Primii pași
# ===========================================================================

sl("s6", "Primii pași", "Depozitul",
   "<h2>Repository</h2>"
   "<p>Un depozit e dosarul unui proiect pe care îl urmărești cu Git. Poți "
   "avea oricâte, pentru proiecte diferite, pe același calculator.</p>"
   + tabel(["Local", "Remote"], [
       ["pe laptopul tău", "pe GitHub"],
       ["acolo lucrezi", "acolo se întâlnesc colegii"],
       ["se face cu <code>git init</code>", "se face din interfața GitHub"],
   ])
   + "<pre><code><span class=\"c\"># o singura data pe laptop: e instalat?</span>\n"
     "git --version\n\n"
     "<span class=\"c\"># in dosarul proiectului</span>\n"
     "git init\ngit status</code></pre>",
   manual=
   "<h2>Repository</h2>"
   "<p>Un depozit (repository, sau pe scurt repo) e un dosar obișnuit, în care "
   "Git a făcut un subdosar ascuns, <code>.git</code>. Acolo ține toată "
   "istoria.</p>"
   + tabel(["Local", "Remote"], [
       ["pe laptopul tău", "pe GitHub"],
       ["acolo lucrezi", "acolo se întâlnesc colegii"],
       ["se face cu <code>git init</code>", "se face din interfața GitHub"],
   ])
   + "<pre><code><span class=\"c\"># deschizi terminalul in dosarul proiectului</span>\n"
     "cd C:\\PROIECTE\\dsw-echipa-3\n\n"
     "<span class=\"c\"># porneste urmarirea</span>\ngit init\n\n"
     "<span class=\"c\"># prima intrebare, mereu: unde sunt?</span>\n"
     "git status</code></pre>"
   + nota("Greșeala de început",
          "<code>git init</code> dat din greșeală în dosarul tău de acasă "
          "pune sub urmărire tot ce ai pe calculator. Dacă ți se întâmplă, "
          "ștergi dosarul <code>.git</code> de acolo și nu s-a pierdut nimic. "
          "În PowerShell, din dosarul acela: "
          "<code>Remove-Item -Recurse -Force .git</code>."))

sl("s7", "Primii pași", "Cine ești",
   "<h2>Credențiale</h2>"
   "<p>Fiecare commit poartă un nume și un email. Se setează o dată, pe "
   "calculator, nu la fiecare proiect.</p>"
   + ix("cod", "Spune-i lui Git cine ești", {
       "id": "c3-cod-config", "indiciu": "Steagul care face setarea valabilă pe tot calculatorul înseamnă „global”, cu două liniuțe în față. "
                  "Adresa e a ta (cea de pe GitHub), scrisă între ghilimele.",
       "iesire": "user.name=Numele Tau\nuser.email=nume@stud.ubbcluj.ro\ncore.autocrlf=true", "fisier": "terminal.sh",
       "sarcina": "Completează comenzile de configurare și de verificare.",
       "cod": "# verifici ce stie deja despre tine\n"
              "git config user.name\ngit config user.email\n\n"
              "# le setezi pentru tot calculatorul, nu doar pentru proiectul asta\n"
              "git config {{1}} user.name \"Numele Tau\"\n"
              "git config {{1}} user.email {{2}}\n\n"
              "# te uiti la tot ce s-a setat\n"
              "git config --list",
       "goluri": {
           "1": {"ok": ["--global"], "ajutor": "steagul"},
           "2": {"ok": ["\"adresa@exemplu.com\"", "'adresa@exemplu.com'",
                        "\"nume@stud.ubbcluj.ro\"", "\"adresa@ta.ro\""],
                 "re": "^[\"'][^\"'\\s]+@[^\"'\\s]+\\.[a-z]{2,}[\"']$",
                 "ajutor": "adresa ta, în ghilimele"}},
       "laBine": "Folosește adresa cu care ai contul de GitHub: altfel "
                 "commit-urile tale nu se leagă de profilul tău.",
       "laRau": "Steagul începe cu două liniuțe. Adresa se scrie între ghilimele.",
       "explicatie": "<code>--global</code> scrie în configurarea "
                     "utilizatorului, deci e valabil pentru toate proiectele. "
                     "Fără el, setarea rămâne doar în depozitul curent, ceea ce "
                     "e util exact într-un caz: când lucrezi și pentru o firmă, "
                     "cu altă identitate."}),
   manual=
   "<h2>Credențiale</h2>"
   "<p>Git scrie în fiecare commit cine l-a făcut. Nu verifică nimic: scrie ce "
   "i-ai spus. De aceea, dacă pui o adresă greșită, commit-urile tale apar pe "
   "GitHub ca ale nimănui.</p>"
   + ix("cod", "Spune-i lui Git cine ești", {
       "id": "c3-cod-config", "indiciu": "Steagul care face setarea valabilă pe tot calculatorul înseamnă „global”, cu două liniuțe în față. "
                  "Adresa e a ta (cea de pe GitHub), scrisă între ghilimele.",
       "iesire": "user.name=Numele Tau\nuser.email=nume@stud.ubbcluj.ro\ncore.autocrlf=true", "fisier": "terminal.sh",
       "sarcina": "Completează comenzile de configurare și de verificare.",
       "cod": "# verifici ce stie deja despre tine\n"
              "git config user.name\ngit config user.email\n\n"
              "# le setezi pentru tot calculatorul, nu doar pentru proiectul asta\n"
              "git config {{1}} user.name \"Numele Tau\"\n"
              "git config {{1}} user.email {{2}}\n\n"
              "# te uiti la tot ce s-a setat\n"
              "git config --list",
       "goluri": {
           "1": {"ok": ["--global"], "ajutor": "steagul"},
           "2": {"ok": ["\"adresa@exemplu.com\"", "'adresa@exemplu.com'",
                        "\"nume@stud.ubbcluj.ro\"", "\"adresa@ta.ro\""],
                 "re": "^[\"'][^\"'\\s]+@[^\"'\\s]+\\.[a-z]{2,}[\"']$",
                 "ajutor": "adresa ta, în ghilimele"}},
       "laBine": "Folosește adresa cu care ai contul de GitHub.",
       "laRau": "Steagul începe cu două liniuțe.",
       "explicatie": "<code>--global</code> e valabil pentru toate proiectele."}))

sl("s8", "Primii pași", "Primul commit",
   "<h2>add, apoi commit</h2>"
   "<p>Două comenzi, în ordinea asta, de fiecare dată.</p>"
   + ix("prezice", "Ce spune git status", {
       "id": "c3-prezice-status", "fisier": "terminal.sh",
       "cod": "# ai modificat doua fisiere: migratie.py si README.md\n"
              "git add migratie.py\n"
              "git status --short",
       "intrebare": "Ce arată git status, pe scurt?",
       "variante": ["M  migratie.py\n M README.md", "M  migratie.py\nM  README.md",
                    " M migratie.py\n M README.md", "nothing to commit"],
       "corect": 0,
       "indiciu": "În --short, prima coloană e zona de pregătire, a doua e dosarul de lucru. Ce fișier ai pus cu add?",
       "laBine": "Doar ce ai pus cu add intră în commit.",
       "explicatie": "<code>M</code> pe prima coloană: modificat și pus în pregătire (intră în commit). "
                     "<code>M</code> pe a doua: modificat, dar încă doar în dosar. Un <code>git commit</code> "
                     "acum ar lua doar <code>migratie.py</code>; <code>README.md</code> rămâne pe dinafară."})
   + ix("ordine", "Pune pașii în ordine", {
       "id": "c3-ordine-commit", "indiciu": "Întâi faci dosarul depozit. Apoi te uiți ce vede Git, pui fișierul în pregătire, verifici, și abia apoi salvezi în istoric.",
       "iesire": "a1b2c3d (HEAD -> main) colectare migratie, Eurostat migr_pop1ctz",
       "sarcina": "Ordinea unui prim commit, de la dosar gol la istoric.",
       "linii": [
           "git init",
           "git status                      # ce vede Git",
           "git add colectare/migratie.py",
           "git status                      # acum e in pregatire",
           "git commit -m \"colectare migratie, Eurostat migr_pop1ctz\"",
           "git log --oneline               # a ramas scris"],
       "explicatie": "<code>git status</code> apare de două ori pentru că e "
                     "comanda pe care o dai cel mai des: o dată ca să vezi ce "
                     "e nesalvat, încă o dată ca să confirmi că ai pus în "
                     "pregătire exact ce voiai."}),
   manual=
   "<h2>Ciclul de lucru</h2>"
   "<p>În practică, o zi de lucru arată așa:</p>"
   "<pre><code><span class=\"c\"># unde sunt?</span>\ngit status\n\n"
   "<span class=\"c\"># aleg ce intra in commit-ul asta</span>\n"
   "git add colectare/migratie.py\n\n"
   "<span class=\"c\"># il scriu in istoric, cu un mesaj care spune ceva</span>\n"
   "git commit -m \"colectare migratie, Eurostat migr_pop1ctz\"\n\n"
   "<span class=\"c\"># il trimit colegilor</span>\ngit push</code></pre>"
   + nota("Cât de des faci commit",
          "Mai des decât crezi. Un commit nu e o livrare, e un punct la care "
          "te poți întoarce. Regula practică: de fiecare dată când ai terminat "
          "un lucru care are un nume.")
   + ix("ordine", "Pune pașii în ordine", {
       "id": "c3-ordine-commit", "indiciu": "Întâi faci dosarul depozit. Apoi te uiți ce vede Git, pui fișierul în pregătire, verifici, și abia apoi salvezi în istoric.",
       "iesire": "a1b2c3d (HEAD -> main) colectare migratie, Eurostat migr_pop1ctz",
       "sarcina": "Ordinea unui prim commit, de la dosar gol la istoric.",
       "linii": [
           "git init",
           "git status                      # ce vede Git",
           "git add colectare/migratie.py",
           "git status                      # acum e in pregatire",
           "git commit -m \"colectare migratie, Eurostat migr_pop1ctz\"",
           "git log --oneline               # a ramas scris"],
       "explicatie": "<code>git status</code> e comanda pe care o dai cel mai des."}))

sl("s9", "Primii pași", "Ce nu urci niciodată",
   "<h2>.gitignore</h2>"
   "<p class=\"cheie\">Un depozit e public până la proba contrarie, și "
   "istoria nu se uită. O parolă urcată o dată rămâne în istoric chiar dacă "
   "ștergi fișierul mâine.</p>"
   + ix("sortare", "Intră sau nu intră în depozit", {
       "id": "c3-sort-gitignore",
       "sarcina": "Pune fiecare lucru unde îi e locul.",
       "elemente": [
           {"t": "colectare.py", "cos": 0}, {"t": ".env cu parole", "cos": 1},
           {"t": "README.md", "cos": 0}, {"t": "venv/", "cos": 1},
           {"t": "date/brute/mic.csv", "cos": 0}, {"t": "date/brute/20GB.csv", "cos": 1},
           {"t": ".gitignore", "cos": 0}, {"t": "cheia de API", "cos": 1}],
       "cosuri": [{"t": "În depozit", "d": "cod, documentație, date mici"},
                  {"t": "Niciodată", "d": "secrete, mediul, fișiere uriașe"}],
       "laBine": "Fișierul <code>.gitignore</code> intră în depozit: e o "
                 "regulă de echipă, nu o preferință personală.",
       "explicatie": "Mediul virtual nu se urcă pentru că se reface din "
                     "<code>requirements.txt</code> în zece secunde, și ocupă "
                     "sute de megabytes. Datele mari nu se urcă pentru că Git "
                     "ține fiecare versiune: un fișier de 20 GB modificat de "
                     "trei ori înseamnă 60 GB de istorie."})
   + verif("c3-v6", 3,
           "Ai urcat din greșeală un fișier cu o parolă și ai făcut push. Ce faci?",
           ["Ștergi fișierul și faci alt commit",
            "Îl adaugi în .gitignore",
            "Nu e nicio problemă, depozitul e privat",
            "Schimbi parola imediat, apoi cureți istoricul"],
           "Schimbi parola. Orice altceva lasă parola în istoric, de unde se "
           "scoate în zece secunde de cine știe unde să se uite. Curățarea "
           "istoricului se face după, și e partea ușoară."),
   manual=
   "<h2>.gitignore</h2>"
   "<p>Un fișier text, în rădăcina proiectului, cu ce nu trebuie urmărit:</p>"
   "<pre><code><span class=\"c\"># mediul virtual si secretele</span>\n"
   "venv/\n.env\n\n"
   "<span class=\"c\"># datele: se aduc cu scriptul de colectare</span>\n"
   "data/\n*.csv\n*.parquet\n*.xlsx\n\n"
   "<span class=\"c\"># gunoiul uneltelor</span>\n"
   ".ipynb_checkpoints/\n__pycache__/\n*.pyc\n.vscode/\n.DS_Store\nThumbs.db</code></pre>"
   + "<p>După ce îl scrii, îl urci ca pe orice fișier: "
     "<code>git add .gitignore</code>, <code>git commit -m \"add gitignore\"</code>, "
     "<code>git push</code>.</p>"
   + tabel(["Ai pus din greșeală un fișier și vrei…", "Comanda"], [
       ["doar să-l scoți din pregătire; rămâne pe disc", "~git reset -- \"nume fisier.ipynb\""],
       ["ca Git să nu-l mai urmărească deloc, dar să rămână în proiect", "~git rm --cached nume_fisier"],
   ])
   + ix("sortare", "Intră sau nu intră în depozit", {
       "id": "c3-sort-gitignore",
       "sarcina": "Pune fiecare lucru unde îi e locul.",
       "elemente": [
           {"t": "colectare.py", "cos": 0}, {"t": ".env cu parole", "cos": 1},
           {"t": "README.md", "cos": 0}, {"t": "venv/", "cos": 1},
           {"t": "date/brute/mic.csv", "cos": 0}, {"t": "date/brute/20GB.csv", "cos": 1},
           {"t": ".gitignore", "cos": 0}, {"t": "cheia de API", "cos": 1}],
       "cosuri": [{"t": "În depozit", "d": "cod, documentație, date mici"},
                  {"t": "Niciodată", "d": "secrete, mediul, fișiere uriașe"}],
       "laBine": "<code>.gitignore</code> intră în depozit: e o regulă de echipă.",
       "explicatie": "Git ține fiecare versiune a fiecărui fișier."}))


# ===========================================================================
#  10-13. GitHub
# ===========================================================================

sl("s10", "GitHub", "Ce este GitHub",
   "<h2>GitHub</h2>"
   "<ul>"
   "<li>o platformă online care găzduiește depozite Git</li>"
   "<li>un loc unde proiectul există și dacă laptopul nu mai există</li>"
   "<li>locul unde echipa se întâlnește, fără să-și trimită arhive pe mail</li>"
   "<li>un portofoliu: se vede cine ce a făcut, și când</li>"
   "</ul>"
   + nota("Pentru voi, concret",
          "Nota de la proiect se dă pe ce se vede în depozit. Nu pe fișierul "
          "final, ci pe drum: ce ați încercat, ce ați aruncat, cine a lucrat. "
          "Un depozit cu un singur commit în ziua predării spune o poveste, "
          "și nu una bună."))

sl("s11", "GitHub", "Legarea celor două",
   "<h2>Două feluri de a începe</h2>"
   + tabel(["Varianta 1: <code>git init</code>", "Varianta 2: <code>git clone</code>"], [
       ["nu există încă depozit pe GitHub", "depozitul echipei există deja pe GitHub"],
       ["<code>git init</code>, <code>add</code>, <code>commit</code>", "<code>git clone &lt;adresa&gt; Proiect</code>"],
       ["<code>git branch -m master main</code>", "<code>cd Proiect</code>"],
       ["<code>git remote add origin &lt;adresa&gt;</code>", "<code>git branch -vv</code>: main urmărește origin/main"],
       ["<code>git push -u origin main</code>", "gata, e deja legat"],
   ])
   + nota("La curs: varianta 2",
          "Depozitul echipei îl face unul dintre voi pe GitHub, iar ceilalți îl "
          "clonează. Clonarea aduce fișierele, toată istoria, și leagă singură "
          "<code>origin</code>.", True)
   + ix("cod", "Leagă-l de GitHub", {
       "id": "c3-cod-remote", "indiciu": "Comanda care gestionează depozitele de la distanță se numește chiar „remote”. "
                  "La primul push, -u ține minte legătura; ramura principală e main.",
       "iesire": "origin  https://github.com/echipa/proiect.git (fetch)\norigin  https://github.com/echipa/proiect.git (push)\nbranch 'main' set up to track 'origin/main'.", "fisier": "terminal.sh",
       "sarcina": "Varianta 1: ai deja un depozit local. Completează comenzile.",
       "cod": "# ramura principala se cheama azi main\n"
              "git branch -m master main\n\n"
              "# „origin” e numele obisnuit al depozitului de pe GitHub\n"
              "git {{1}} add origin https://github.com/echipa/proiect.git\n"
              "git remote -v\n\n"
              "# prima trimitere: -u leaga main local de origin/main\n"
              "git push {{2}} origin {{3}}",
       "goluri": {
           "1": {"ok": ["remote"], "ajutor": "comanda"},
           "2": {"ok": ["-u", "--set-upstream"], "ajutor": "steagul"},
           "3": {"ok": ["main"], "ajutor": "ramura"}},
       "laBine": "După prima dată cu <code>-u</code>, e de ajuns <code>git push</code>.",
       "laRau": "Numele depozitului de pe internet e „origin”. Ramura e „main”.",
       "explicatie": "<code>-u</code> înseamnă „ține minte legătura” (upstream). "
                     "De atunci, <code>git push</code> și <code>git pull</code> "
                     "știu singure unde să meargă."}),
   manual=
   "<h2>Două feluri de a începe</h2>"
   "<p>Ca în fișa „Lucrul cu Git” de la curs, sunt două variante, după cum "
   "există sau nu deja depozitul pe GitHub.</p>"
   "<h3>Varianta 1: <code>git init</code></h3>"
   "<p>Doar dacă nu există încă depozit pe GitHub.</p>"
   "<pre><code>git init                          <span class=\"c\"># depozit local, gol</span>\n"
   "git add .                         <span class=\"c\"># fisierele existente</span>\n"
   "git commit -m \"first commit\"\n"
   "git branch -m master main         <span class=\"c\"># ramura principala devine main</span>\n"
   "git remote add origin &lt;GitHub_URL&gt;\n"
   "git push -u origin main</code></pre>"
   "<h3>Varianta 2: <code>git clone</code>, cea de la curs</h3>"
   "<p>Când depozitul echipei există deja pe GitHub.</p>"
   "<pre><code>git clone https://github.com/DSW2026-ORG/TeamX.git Proiect\n"
   "cd Proiect\n"
   "git status\n"
   "git branch -vv            <span class=\"c\"># main urmareste origin/main</span></code></pre>"
   "<h3>Caz special</h3>"
   "<p>Ai făcut local <code>git init</code>, dar depozitul de pe GitHub "
   "există deja și are conținut (de exemplu un README). Istoriile nu au "
   "legătură, deci le unești o dată:</p>"
   "<pre><code>git remote add origin &lt;GitHub_URL&gt;\n"
   "git pull origin main --allow-unrelated-histories\n"
   "git branch -u origin/main</code></pre>"
   + tabel(["Verificare", "Ce vezi"], [
       ["~git branch", "ramurile locale"],
       ["~git branch -r", "ramurile de pe GitHub (origin/...)"],
       ["~git branch -a", "toate"],
       ["~git branch -vv", "fiecare ramură și pe cine urmărește (upstream)"],
       ["~git remote -v", "adresa lui origin"],
   ])
   + ix("cod", "Leagă-l de GitHub", {
       "id": "c3-cod-remote", "indiciu": "Comanda care gestionează depozitele de la distanță se numește chiar „remote”. "
                  "La primul push, -u ține minte legătura; ramura principală e main.",
       "iesire": "origin  https://github.com/echipa/proiect.git (fetch)\norigin  https://github.com/echipa/proiect.git (push)\nbranch 'main' set up to track 'origin/main'.", "fisier": "terminal.sh",
       "sarcina": "Varianta 1: completează comenzile.",
       "cod": "git branch -m master main\n"
              "git {{1}} add origin https://github.com/echipa/proiect.git\n"
              "git push {{2}} origin {{3}}",
       "goluri": {
           "1": {"ok": ["remote"], "ajutor": "comanda"},
           "2": {"ok": ["-u", "--set-upstream"], "ajutor": "steagul"},
           "3": {"ok": ["main"], "ajutor": "ramura"}},
       "laBine": "După prima dată cu <code>-u</code>, e de ajuns <code>git push</code>.",
       "laRau": "Ramura e „main”.",
       "explicatie": "<code>-u</code> leagă ramura locală de cea de pe GitHub."}))


sl("s12", "GitHub", "Drumul complet",
   "<h2>De la dosar gol la depozit de echipă</h2>"
   + ix("ordine", "Pune pașii în ordine", {
       "id": "c3-ordine-github", "poarta": False,
       "sarcina": "Drumul de la un dosar cu fișiere la un depozit pe GitHub.",
       "linii": [
           "git init",
           "scrii .gitignore, ca secretele sa nu intre din prima",
           "git add .",
           "git commit -m \"structura proiectului si colectarea\"",
           "git branch -m master main",
           "creezi pe GitHub un depozit gol, fara README",
           "git remote add origin <adresa>",
           "git push -u origin main"],
       "explicatie": "<code>.gitignore</code> se scrie înainte de primul "
                     "<code>git add .</code>, nu după. Iar depozitul de pe "
                     "GitHub se face gol: un README creat acolo e un commit pe "
                     "care laptopul tău nu-l are, și primul push e refuzat."}))


# ===========================================================================
#  14-16. În echipă
# ===========================================================================

sl("s14", "În echipă", "Ramuri",
   "<h2>De ce ramuri</h2>"
   "<p>O ramură e o linie de lucru paralelă. Strici ce vrei pe ea, iar "
   "<code>main</code> rămâne întreg.</p>"
   + ix("ramuri", "Desenează-l tu",
        {"id": "c3-ramuri",
         "sarcina": "Fă o ramură, pune două commit-uri pe ea, întoarce-te pe "
                    "main și îmbin-o. Graful crește sub mână."})
   + "<p class=\"cheie\">Regula echipei: <code>main</code> trebuie să meargă "
     "întotdeauna. Tot ce e în lucru stă pe o ramură.</p>",
   manual=
   "<h2>Ramuri</h2>"
   "<p>O ramură e o linie de lucru paralelă. Pe ea strici ce vrei, iar "
   "<code>main</code> rămâne întreg și gata de predat oricând.</p>"
   + ix("ramuri", "Desenează-l tu",
        {"id": "c3-ramuri",
         "sarcina": "Fă o ramură, pune două commit-uri pe ea, întoarce-te pe "
                    "main și îmbin-o."})
   + tabel(["Comanda", "Ce face"], [
       ["~git branch", "ce ramuri există și pe care ești"],
       ["~git switch -c curatare", "faci una nouă și treci pe ea"],
       ["~git switch main", "te întorci"],
       ["~git merge curatare", "aduci în main ce ai făcut pe ea"],
   ])
   + nota("De ce nu lucrează toți direct pe main",
          "Pentru că atunci orice lucru neterminat al oricui blochează pe "
          "toată lumea. Cu ramuri, main e întotdeauna o versiune care "
          "funcționează, iar ce e în lucru stă deoparte până e gata."))

# --------------------------------------------------------------------------
# Fluxul echipei din fișa „Lucrul cu Git”: main și dev. Fiecare pas e o
# comandă; panourile arată ce commit-uri are fiecare depozit și unde stau
# etichetele (ramurile). x = coloana, r = rândul pe desen.
# --------------------------------------------------------------------------

COMMITURI = {
    "c1": {"x": 0, "r": 0, "autor": "baza", "mesaj": "structura proiectului"},
    "c2": {"x": 1, "r": 0, "autor": "baza", "mesaj": "colectare migratie", "parinti": ["c1"]},
    "y1": {"x": 2, "r": 1, "autor": "tu", "mesaj": "curatare migratie", "parinti": ["c2"]},
    "m1": {"x": 2, "r": 2, "autor": "maria", "mesaj": "harta pe judete", "parinti": ["c2"]},
    "x1": {"x": 3, "r": 1, "autor": "tu", "merge": True, "mesaj": "merge origin/dev", "parinti": ["y1", "m1"]},
}


def stare(commits, et, head=None):
    return {"commits": commits, "et": et, "head": head}


B = ["c1", "c2"]
GITDAG = {
    "commituri": COMMITURI,
    "autori": {"baza": {"et": "commit-urile de la început", "c": "text-3"},
               "tu": {"et": "commit-urile tale", "c": "ceas"},
               "maria": {"et": "commit-urile Mariei", "c": "accent"}},
    "pasi": [
        {"t": "Depozitul clonat", "cmd": "git clone <adresa> Proiect",
         "txt": "Laptopul tău și GitHub au aceleași două commit-uri. Eticheta "
                "<code>main</code> stă pe ultimul. HEAD arată pe ce ramură ești.",
         "L": stare(B, {"main": "c2"}, "main"), "R": stare(B, {"main": "c2"})},
        {"t": "Unul din echipă face dev", "cmd": "git switch -c dev",
         "txt": "O ramură nouă e doar o etichetă nouă pe același commit. Nu se "
                "copiază nimic. HEAD trece pe dev.",
         "L": stare(B, {"main": "c2", "dev": "c2"}, "dev"), "R": stare(B, {"main": "c2"})},
        {"t": "Dev ajunge pe GitHub", "cmd": "git push -u origin dev", "sus": True,
         "txt": "Acum există și <code>origin/dev</code>. Colegii o aduc cu "
                "<code>git fetch</code> și <code>git switch dev</code>.",
         "L": stare(B, {"main": "c2", "dev": "c2"}, "dev"), "R": stare(B, {"main": "c2", "dev": "c2"})},
        {"t": "Lucrezi și salvezi", "cmd": "git commit -m \"curatare migratie\"",
         "txt": "Un commit nou, doar pe laptopul tău. Eticheta dev avansează "
                "pe el; main rămâne pe loc.",
         "L": stare(B + ["y1"], {"main": "c2", "dev": "y1"}, "dev"),
         "R": stare(B, {"main": "c2", "dev": "c2"})},
        {"t": "Între timp, Maria", "cmd": "git push", "cine": "maria $",
         "txt": "Maria a lucrat și ea pe dev și a urcat primul. Pe GitHub, "
                "dev e acum pe commit-ul ei. Laptopul tău nu știe încă.",
         "L": stare(B + ["y1"], {"main": "c2", "dev": "y1"}, "dev"),
         "R": stare(B + ["m1"], {"main": "c2", "dev": "m1"})},
        {"t": "Push refuzat", "cmd": "git push   ✗ rejected (fetch first)", "rau": True,
         "txt": "GitHub are un commit pe care tu nu-l ai. Git refuză, ca să nu "
                "ștergi munca Mariei. De aceea în fișă scrie: <b>pull, apoi push</b>.",
         "L": stare(B + ["y1"], {"main": "c2", "dev": "y1"}, "dev"),
         "R": stare(B + ["m1"], {"main": "c2", "dev": "m1"})},
        {"t": "Aduci ce a făcut ea", "cmd": "git pull", "jos": True,
         "txt": "Commit-ul Mariei coboară, iar Git le unește pe ale voastre "
                "într-un commit de îmbinare (cel cu contur). Dacă ați atins "
                "aceleași rânduri, aici apare un conflict.",
         "L": stare(B + ["y1", "m1", "x1"], {"main": "c2", "dev": "x1"}, "dev"),
         "R": stare(B + ["m1"], {"main": "c2", "dev": "m1"})},
        {"t": "Acum merge", "cmd": "git push", "sus": True,
         "txt": "Commit-ul tău și cel de îmbinare urcă. GitHub și laptopul tău "
                "au din nou același dev.",
         "L": stare(B + ["y1", "m1", "x1"], {"main": "c2", "dev": "x1"}, "dev"),
         "R": stare(B + ["y1", "m1", "x1"], {"main": "c2", "dev": "x1"})},
        {"t": "Task terminat: treci pe main", "cmd": "git switch main && git pull",
         "txt": "Curățarea e gata, deci e momentul să ajungă în main. Întâi "
                "treci pe main și te asiguri că e la zi.",
         "L": stare(B + ["y1", "m1", "x1"], {"main": "c2", "dev": "x1"}, "main"),
         "R": stare(B + ["y1", "m1", "x1"], {"main": "c2", "dev": "x1"})},
        {"t": "Aduci dev în main", "cmd": "git merge dev",
         "txt": "Main nu avea nimic nou, deci eticheta main doar sare pe ultimul "
                "commit din dev. Commit-urile nu se mută și nu se copiază: "
                "se mută eticheta.",
         "L": stare(B + ["y1", "m1", "x1"], {"main": "x1", "dev": "x1"}, "main"),
         "R": stare(B + ["y1", "m1", "x1"], {"main": "c2", "dev": "x1"})},
        {"t": "Main ajunge pe GitHub", "cmd": "git push", "sus": True,
         "txt": "Gata: main de pe GitHub conține tot ce s-a făcut și verificat "
                "pe dev. Ciclul se reia de la pasul 4.",
         "L": stare(B + ["y1", "m1", "x1"], {"main": "x1", "dev": "x1"}, "main"),
         "R": stare(B + ["y1", "m1", "x1"], {"main": "x1", "dev": "x1"})},
    ],
}

FLUX_DEV = [
    ["o dată, unul din echipă", "~git switch -c dev", "~git push -u origin dev"],
    ["o dată, ceilalți", "~git fetch", "~git switch dev"],
    ["zilnic, fiecare", "~git switch dev", "~git pull"],
    ["când salvezi", "~git add . ; git commit -m \"...\"", "~git pull ; git push"],
    ["după un task important", "~git switch main ; git pull", "~git merge dev ; git push"],
]

sl("s14b", "În echipă", "Fluxul echipei",
   "<h2>main și dev, pas cu pas</h2>"
   + ix("gitdag", "Ce se întâmplă cu commit-urile", GITDAG),
   manual=
   "<h2>Fluxul echipei: main și dev</h2>"
   "<p>Fluxul din fișa „Lucrul cu Git” are două ramuri. <code>main</code> e "
   "versiunea care merge și care se predă. <code>dev</code> e ramura pe "
   "care lucrează toată echipa zi de zi. Ce e pe dev ajunge în main după "
   "fiecare task important terminat: curățarea datelor, setul de "
   "vizualizări, modelul. Nu la fiecare commit, și nu doar la final.</p>"
   + ix("gitdag", "Ce se întâmplă cu commit-urile", GITDAG)
   + tabel(["Cine, când", "Comanda", "Apoi"], FLUX_DEV)
   + nota("Fișiere separate",
          "Lucrați, pe cât se poate, în fișiere separate (de exemplu "
          "<code>analiza_vlad.ipynb</code>, <code>analiza_maria.ipynb</code>). "
          "Conflictele apar doar când doi oameni schimbă aceleași rânduri.")
   + nota("Ce face <code>git merge dev</code>",
          "Ia toate commit-urile care există în dev, dar nu încă în main, și "
          "le aduce în main. Dacă main n-a primit nimic între timp, eticheta "
          "main doar avansează (fast-forward)."))


sl("s15", "În echipă", "Conflictele",
   "<h2>Când doi oameni schimbă aceleași rânduri</h2>"
   + "<p>La <code>git pull</code>, Git nu poate alege, deci îți pune amândouă "
     "variantele în fișier și te lasă pe tine. Rezolvi, apoi "
     "<code>git add .</code>, <code>git commit -m \"rezolvat conflict\"</code>, "
     "<code>git push</code>.</p>"
   + ix("conflict", "Rezolvă-l", {
       "id": "c3-conflict", "fisier": "analiza.py", "ramura": "curatare",
       "sarcina": "Colega ta a redenumit fișierul de date, tu ai rămas cu "
                  "numele vechi. Alege ce rămâne în fișier.",
       "alMeu": 'd = pd.read_csv("date/brute/pop.csv")',
       "alLor": 'd = pd.read_csv("date/brute/populatie_ro.csv")',
       "bun": "lor",
       "deCe": "Fișierul cu numele vechi nu mai există: colega l-a redenumit "
               "și a urcat schimbarea. Varianta ta ar da eroare la prima rulare.",
       "explicatie": "Oricare ai alege, marcajele dispar și fișierul redevine "
                     "cod valid. Git nu verifică dacă ai ales bine: asta e "
                     "treaba ta, și de aceea un conflict se rezolvă uitându-te "
                     "la cod, nu apăsând repede."}),
   manual=
   "<h2>Conflictele</h2>"
   "<p>Un conflict apare la <code>git pull</code> (sau la <code>git merge</code>) "
   "când tu și un coleg ați schimbat aceleași rânduri. După rezolvare: "
   "<code>git add .</code>, <code>git commit -m \"rezolvat conflict\"</code>, "
   "<code>git push</code>.</p>"
   + nota("Pull request",
          "Pe GitHub, aducerea lui dev în main se poate face și printr-un pull "
          "request: ceri îmbinarea, iar un coleg se uită întâi peste ea. Pentru "
          "proiectul nostru ajunge <code>git merge dev</code> din terminal; "
          "pull request-ul e un pas în plus, util când echipa vrea să citească "
          "înainte.")
   + "<h3>Conflictele nu sunt o avarie</h3>"
   + "<p>Sunt felul în care Git spune că nu poate decide în locul tău. Sus e ce "
     "ai tu, jos e ce vine.</p>"
   + ix("conflict", "Rezolvă-l", {
       "id": "c3-conflict", "fisier": "analiza.py", "ramura": "curatare",
       "sarcina": "Colega ta a redenumit fișierul de date, tu ai rămas cu "
                  "numele vechi. Alege ce rămâne în fișier.",
       "alMeu": 'd = pd.read_csv("date/brute/pop.csv")',
       "alLor": 'd = pd.read_csv("date/brute/populatie_ro.csv")',
       "bun": "lor",
       "deCe": "Fișierul cu numele vechi nu mai există.",
       "explicatie": "Git nu verifică dacă ai ales bine: asta e treaba ta."}))

sl("s16", "În echipă", "Regulile voastre",
   "<h2>Patru reguli, pentru semestrul ăsta</h2>"
   + '<div class="reg">'
   + "".join(f'<div class="reg__c"><span class="reg__n">{i}</span><b>{t}</b><p>{d}</p></div>'
             for i, (t, d) in enumerate([
                 ("<code>git pull</code> întâi", "pe dev, înainte să începi; și înainte de push"),
                 ("lucrați pe dev", "<code>main</code> primește doar task-uri terminate"),
                 ("mesaje care spun ceva", "ce s-a schimbat, nu „update”"),
                 ("nimic secret, nimic uriaș", "parolele și datele mari rămân afară"),
             ], 1))
   + "</div>"
   + nota("Cine ce face",
          "Scrieți în <code>README.md</code> cine răspunde de ce: colectare, "
          "curățare, analiză, raport. Nu ca să vă împărțiți vina, ci ca să "
          "știe fiecare pe cine întreabă.", True))


# ===========================================================================
#  17-20. Încadrarea teoretică
# ===========================================================================

sl("s17", "Cadrul teoretic", "De ce un cadru",
   "<h2>Încadrarea teoretică</h2>"
   "<p class=\"cheie\">Datele nu produc întrebări. Teoria produce întrebări, "
   "iar datele răspund la ele sau refuză.</p>"
   "<p>Fără un cadru, un proiect de analiză devine o colecție de grafice "
   "despre care nimeni nu poate spune dacă sunt importante.</p>")

PILONI = [
    ("Economie", "WDI: PIB/locuitor, populație, urbanizare",
     "Peisajul: capacitatea de a investi și cererea de energie. Explică "
     "diferențele dintre țări și intră în regresii."),
    ("Instituții", "WGI: Government Effectiveness",
     "Modelul de guvernanță: capacitatea de a pune în practică. Explică "
     "variația dintre țări aflate la același nivel economic."),
    ("Sistem energetic", "EIA: cărbune, eolian, solar, hidro, nuclear, CO₂",
     "Regimul și nișele: structura energetică, blocajele moștenite, creșterea "
     "regenerabilelor. Baza clusterizării."),
]

sl("s18", "Cadrul teoretic", "Un exemplu lucrat",
   "<h2>Tranzițiile energetice</h2>"
   "<p>Literatura găsește trei dimensiuni care revin. Ele devin pilonii; "
   "întrebarea stă pe toți trei.</p>"
   + templu("Cum diferă traiectoriile energetice ale țărilor, și de ce?",
            [(n, u, d.split(".")[0] + ".") for n, u, d in PILONI],
            "literatura despre tranziții energetice și economia energiei")
   + "<h3>Întrebările care ies din cadru</h3>"
   + "<ol>"
     "<li>Țările cu PIB pe locuitor mai mare reduc mai repede cărbunele și "
     "cresc regenerabilele?</li>"
     "<li>Țările cu instituții mai eficiente cresc mai repede eolianul și "
     "solarul?</li>"
     "<li>Ce tipuri de sisteme energetice se disting, după mixul de "
     "electricitate și emisii?</li>"
     "</ol>",
   manual=
   "<h2>Un exemplu lucrat: tranzițiile energetice</h2>"
   "<p>Exemplul e dintr-o cercetare adevărată, și merită urmărit pas cu pas "
   "pentru că arată forma pe care trebuie s-o aibă și proiectul vostru.</p>"
   "<p>Punctul de plecare e literatura: mai mulți autori, care studiază "
   "tranzițiile energetice și economia energiei, ajung la aceeași structură în "
   "trei dimensiuni. Nu e o alegere a cercetătorului, e ce spune domeniul.</p>"
   + templu("Cum diferă traiectoriile energetice ale țărilor, și de ce?",
            [(n, u, d.split(".")[0] + ".") for n, u, d in PILONI],
            "literatura despre tranziții energetice și economia energiei")
   + tabel(["Pilon", "Date și sursă", "Rol teoretic"],
           [[n, u, d] for n, u, d in PILONI])
   + "<p>Abia după ce există tabelul ăsta se pot scrie întrebările, și fiecare "
     "întrebare atinge cel puțin doi piloni:</p>"
   + "<ol>"
     "<li><em>Economia și tranziția:</em> țările cu PIB pe locuitor mai mare "
     "reduc mai repede ponderea cărbunelui și cresc ponderea regenerabilelor?</li>"
     "<li><em>Instituțiile:</em> țările cu un nivel mai ridicat al eficienței "
     "guvernamentale au o creștere mai rapidă a energiei eoliene și solare?</li>"
     "<li><em>Regimurile energetice:</em> ce tipuri de sisteme energetice se "
     "disting între țări, pe baza mixului de electricitate și a emisiilor?</li>"
     "</ol>"
   + nota("Ce se vede în tabelul ăla",
          "Fiecare rând leagă trei lucruri: un concept, o sursă de date "
          "concretă, și rolul pe care îl joacă în argument. Dacă unul dintre "
          "cele trei lipsește, pilonul nu ține: un concept fără date nu se "
          "poate testa, iar date fără rol teoretic sunt doar coloane."))

PILONI_NOI = [
    ("Legăturile", "SCI, Meta: perechi de țări, regiuni, județe",
     "Cine cu cine e legat, și cât de tare."),
    ("Oamenii", "Eurostat migr_pop1ctz: cetățeni pe țări",
     "Pe unde au plecat oamenii care țin legăturile."),
    ("Locul", "GISCO: distanță, graniță; Eurostat: PIB, populație",
     "Ce explică legăturile fără nicio migrație."),
]

sl("s19", "Cadrul teoretic", "Cadrul nostru",
   "<h2>Aceeași formă, pe datele noastre</h2>"
   + templu("Cât din legăturile dintre locuri se explică prin oamenii care "
            "au migrat între ele?", PILONI_NOI,
            "sistemele migratorii, rețelele de migranți, Bailey și colegii (2018) despre SCI")
   + "<p class=\"cheie\">Distanța explică mult. Migrația, încă ceva. "
     "Întrebarea interesantă e ce rămâne după amândouă.</p>",
   manual=
   "<h2>Cadrul nostru: legături și migrație</h2>"
   "<p>Aceeași formă ca la tranzițiile energetice, pe datele cursului. "
   "Temelia e literatura despre sistemele migratorii: locurile legate prin "
   "migrație rămân legate și prin informație, bani și vizite, iar rețelele "
   "de migranți fac drumul mai ușor pentru cei care vin după. Indicele SCI "
   "ne lasă să vedem o parte din legăturile astea, măsurate direct.</p>"
   + templu("Cât din legăturile dintre locuri se explică prin oamenii care "
            "au migrat între ele?", PILONI_NOI,
            "sistemele migratorii, rețelele de migranți, Bailey și colegii (2018) despre SCI")
   + "<h3>Întrebările care ies din cadru</h3>"
   "<ol>"
   "<li><em>Migrația:</em> perechile de țări cu mai mulți migranți sunt mai "
   "legate, la aceeași distanță?</li>"
   "<li><em>Istoria:</em> granițele vechi și minoritățile, cum e cazul "
   "României cu Ungaria, dau legături pe care migrația recentă nu le "
   "explică?</li>"
   "<li><em>Ce rămâne:</em> unde sunt legăturile mai puternice decât prezic "
   "distanța și migrația împreună, și ce au în comun locurile acelea?</li>"
   "</ol>"
   + nota("Unde intrați voi",
          "Fiecare echipă alege un colț din templu: un coridor, de exemplu "
          "România și Italia, sau o țară privită pe regiuni. Puteți adăuga un "
          "pilon, de exemplu limba sau religia, dacă îl puteți măsura."))

sl("s20", "Cadrul teoretic", "Scrieți întrebarea voastră",
   "<h2>Întrebarea echipei</h2>"
   "<p>Două-trei rânduri. Nu trebuie să fie definitivă; trebuie să existe.</p>"
   + ix("asteptari", "Întrebarea de cercetare", {
       "id": "c3-intrebare", "tip": "intrebare", "minim": 60,
       "sarcina": "Scrie întrebarea la care vrea să răspundă echipa ta, și "
                  "spune din ce pilon vine partea pe care o aduceți voi.",
       "exemplu": "De exemplu: regiunile din Italia cu mai mulți români sunt "
                  "și cele mai legate de România, sau legătura urmează altă "
                  "logică decât migrația?",
       "multumesc": "O citesc înainte de cursul următor și vă scriu ce cred."}))


# ===========================================================================
#  21-23. Datele și proiectul
# ===========================================================================

sl("s21", "Datele", "Explorarea inițială",
   "<h2>Prima privire peste ce ai colectat</h2>"
   "<p>Înainte de orice analiză, patru comenzi. Întotdeauna aceleași.</p>"
   + ix("cod", "Prima privire", {
       "id": "c3-cod-explorare", "indiciu": "Dimensiunea tabelului e un atribut (fără paranteze), cu „formă” în engleză. Rezumatul pe coloane e metoda „informații”. Lipsurile se adună cu metoda „sumă”.",
       "iesire": "(5104, 3)\n<class 'pandas.core.frame.DataFrame'>\nRangeIndex: 5104 entries ...\ngeo           0\ncitizen       0\nvaloare     812", "fisier": "explorare.py",
       "sarcina": "Completează primele patru lucruri pe care le ceri de la un tabel nou.",
       "cod": "import pandas as pd\n\n"
              "d = pd.read_csv(\"date/brute/migratie.csv\")\n\n"
              "# cate randuri si cate coloane\nprint(d.{{1}})\n\n"
              "# ce coloane, ce tipuri, cate valori lipsesc\nd.{{2}}()\n\n"
              "# cum arata primele randuri\nprint(d.head())\n\n"
              "# cate valori lipsesc, pe coloana\nprint(d.isna().{{3}}())",
       "goluri": {
           "1": {"ok": ["shape"], "ajutor": "atributul"},
           "2": {"ok": ["info"], "ajutor": "metoda"},
           "3": {"ok": ["sum"], "ajutor": "metoda"}},
       "laBine": "Cele patru se dau în ordinea asta, de fiecare dată, pe orice "
                 "tabel nou. La migrație vei vedea multe valori lipsă: țările "
                 "care nu raportează. Le tratăm la cursul 4.",
       "laRau": "Prima e un atribut, deci fără paranteze. Celelalte sunt metode.",
       "explicatie": "<code>info()</code> e cea mai densă: îți dă dintr-o dată "
                     "numărul de rânduri, tipurile coloanelor și câte valori "
                     "non-nule are fiecare. Dacă o coloană care ar trebui să fie "
                     "numerică apare ca <code>object</code>, ai găsit o problemă "
                     "înainte s-o cauți."})
   + nota("Ce cauți la prima privire",
          "Nu rezultate. Cauți semne că datele nu sunt ce crezi: un număr de "
          "rânduri diferit de ce așteptai, o coloană text care ar trebui să fie "
          "numerică, valori lipsă unde n-ar trebui. Analiza începe la cursul 6; "
          "acum doar verifici că ai ce analiza."))

sl("s22", "Proiectul tău", "Fă-ți depozitul, acum",
   "<h2>Depozitul echipei</h2>"
   + tabel(["Pasul", "Ce faci"], [
       ["1", "unul din echipă face depozitul pe GitHub și îi adaugă pe ceilalți"],
       ["2", "fiecare îl clonează la el"],
       ["3", "scrieți <code>.gitignore</code> înainte de primul <code>add</code>"],
       ["4", "unul face ramura <code>dev</code>; ceilalți o aduc cu <code>git fetch</code>"],
       ["5", "urcați pe dev scriptele de colectare de săptămâna trecută"],
       ["6", "în <code>README.md</code>: întrebarea și cine ce face"],
   ])
   + ix("dovada", "Dovada", {
       "id": "c3-dovada-depozit",
       "sarcina": "Rulează comenzile la tine și lipește ce scrie terminalul.",
       "pasi": [
           {"t": "Depozitul e legat de GitHub",
            "cmd": "git remote -v",
            "gol": "lipește prima linie",
            "cauta": r"github\.com",
            "daca_nu": "Caut adresa de GitHub. Dacă nu apare nimic, n-ai dat "
                       "încă git remote add origin."},
           {"t": "Ai cel puțin două commit-uri",
            "cmd": "git log --oneline | head -3",
            "gol": "lipește liniile",
            "cauta": r"[0-9a-f]{7}[\s\S]*[0-9a-f]{7}",
            "daca_nu": "Caut două hash-uri de commit. Unul singur înseamnă că "
                       "ai urcat tot dintr-o dată, la final."},
           {"t": "Ramura dev există și pe GitHub",
            "cmd": "git branch -a",
            "gol": "lipește lista",
            "cauta": r"remotes/origin/dev",
            "daca_nu": "Caut remotes/origin/dev. Unul din echipă face "
                       "git switch -c dev și git push -u origin dev; ceilalți "
                       "dau git fetch."},
           {"t": "Secretele sunt ținute afară",
            "cmd": "git check-ignore -v .env venv",
            "gol": "lipește ce scrie",
            "cauta": r"\.gitignore",
            "daca_nu": "Caut numele fișierului .gitignore în răspuns. Dacă "
                       "comanda nu scrie nimic, regulile nu prind."}],
       "explicatie": "Dacă toate trei merg, munca echipei există în două locuri "
                     "și se poate urmări cine ce a făcut. De aici încolo, "
                     "fiecare curs adaugă o piesă la același depozit."}))

sl("s23", "Mai departe", "Până data viitoare",
   "<h2>Cursul 4: curățarea datelor</h2>"
   "<ul>"
   "<li>versionare și colaborare, în practică, pe depozitul vostru</li>"
   "<li>curățarea datelor: lipsuri, duplicate, coduri care încurcă (EL, NA)</li>"
   "<li>SCI și migrația, puse în același tabel</li>"
   "<li>explorarea inițială, mai în adâncime</li>"
   "</ul>"
   + nota("De făcut până atunci",
          "Depozitul echipei, cu scriptul de colectare în el și cu "
          "<code>README.md</code> scris: întrebarea de cercetare și cine "
          "răspunde de ce. Plus un commit de la fiecare membru, ca să știu că "
          "toată lumea a intrat în el.", True))


if __name__ == "__main__":
    L.scrie_tot()
