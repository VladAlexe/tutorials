# -*- coding: utf-8 -*-
"""
Lecția 8: Raportul, README-ul și prezentarea.

Cinci slide-uri. Lecția spune ce intră în fiecare dintre cele trei documente
ale proiectului; sarcina ei este feedback-ul pentru curs (anonim, db/34);
restul orei este lucru în echipă.
Prezentarea proiectelor are loc la cursul 9, fără slide-uri.

Rulare:  python _build/c8.py
"""

from comun import Lectie, ix, tabel, nota, surse

L = Lectie(8, "c8-raportare", "Raportul, README-ul și prezentarea",
           "Cele trei documente ale proiectului: README-ul pentru un vizitator din afară, raportul complet în "
           "docs/ și prezentarea de la cursul 9.")
sl = L.sl


# ===========================================================================
#  1. Cursul
# ===========================================================================

CURSUL = tabel(["", "Conținutul", "Rezultatul"], [
    ["C1", "proiectul, mediul de lucru, tipurile de date și JSON", "<code>dsw/</code>, cu <code>.venv</code>"],
    ["C2", "colectarea datelor prin API: Eurostat, Banca Mondială", "<code>data/raw</code>"],
    ["C3", "surse diverse, preprocesare, Git și depozitul echipei", "<code>data/processed</code>, <code>proiect/</code>"],
    ["C4", "curățarea datelor și tabelul regiunilor", "<code>regiuni_nuts2.csv</code>"],
    ["C5", "integrare, baze de date și agregare", "perechile, în <code>dsw.db</code>"],
    ["C6", "analiza exploratorie", "deciziile pentru model"],
    ["C7", "variabile derivate și model", "modelul SCI și reziduurile lui"],
    ["<b>C8</b>", "<b>azi: raportul, README-ul și planul prezentării</b>",
     "<b><code>README.md</code>, <code>docs/report.pdf</code></b>"],
    ["C9", "prezentarea proiectelor", "nota proiectului"],
])

sl("s1", "Cursul", "Unde suntem",
   "<h2>Unde suntem în curs</h2>"
   "<p class=\"cheie\">Analiza este gata. Azi: cele trei documente prin care altcineva o înțelege, README-ul, "
   "raportul și prezentarea. La final, feedback-ul pentru curs; restul orei, lucru în echipă.</p>"
   + CURSUL,
   manual=
   "<h2>Raportul, README-ul și prezentarea</h2>"
   "<p>Un proiect de analiză este folosit de alții abia când îl pot înțelege fără autorii lui. Proiectul echipei "
   "are de aceea trei documente, fiecare pentru alt cititor:</p>"
   + tabel(["Documentul", "Cititorul", "Ce caută"], [
       ["<code>README.md</code>", "un vizitator din afară: un posibil colaborator sau angajator",
        "într-un minut: întrebarea, rezultatul, seriozitatea muncii"],
       ["<code>docs/report.pdf</code>", "cine vrea dovezile", "datele, metoda, figurile, rezultatele, limitele, contribuțiile"],
       ["prezentarea, la C9", "grupa și profesorul", "drumul de la date la rezultat, spus de toți membrii echipei"]])
   + "<p>Raportul este documentul complet; README-ul îl rezumă, iar prezentarea îl parcurge. După cele patru "
     "slide-uri, ora este pentru lucrul în echipă: raportul, README-ul și planul prezentării.</p>"
   + CURSUL)


# ===========================================================================
#  2. README-ul
# ===========================================================================

README = (
    '<div class="pd5"><figure><figcaption>README.md, schița</figcaption><pre>'
    '<span class="k1"># Migration and social ties in Europe</span>\n'
    'Country pairs with twice as many migrants between\n'
    'them are about 56% more connected on Facebook,\n'
    'at the same distance and border.\n\n'
    '![Observed and predicted SCI](figures/model.png)\n\n'
    '<span class="k1">## Question</span>      <span class="k3">why it matters, in two sentences</span>\n'
    '<span class="k1">## Data</span>          <span class="k3">sources, access, terms of use</span>\n'
    '<span class="k1">## Methods</span>       <span class="k3">notebooks 01 to 05, one line each</span>\n'
    '<span class="k1">## Results</span>       <span class="k3">findings, each with its notebook</span>\n'
    '<span class="k1">## Limitations</span>   <span class="k3">what the data cannot show</span>\n'
    '<span class="k1">## Reproduce</span>     <span class="k3">setup, run order, run time</span>\n'
    '<span class="k1">## Repository</span>    <span class="k3">the folders, as a tree</span>\n'
    '<span class="k1">## License</span>       <span class="k3">code MIT, data per source</span>\n\n'
    'Full report: <span class="k2">docs/report.pdf</span></pre></figure></div>')

ZONE = ('<ol>'
        '<li><b>Titlul și rezultatul</b>, cu un număr: primul ecran spune ce s-a găsit, nu ce s-a făcut.</li>'
        '<li><b>Figura principală</b>, chiar sub rezultat.</li>'
        '<li><b>Datele</b>: de unde vin, cum se obțin și în ce condiții se pot folosi.</li>'
        '<li><b>Reproducerea</b>: versiunea Python, instalarea, ordinea caietelor, timpul de rulare; '
        'fiecare rezultat, cu caietul care îl produce.</li>'
        '<li><b>Licența</b> și legătura spre raport.</li>'
        '</ol>'
        '<p class="def6">În engleză, ca un CV al proiectului: fără „proiect pentru cursul…”, fără lista '
        'membrilor și a rolurilor.</p>')

sl("s2", "README", "README-ul ca un CV",
   "<h2>README-ul, un CV al proiectului</h2>"
   '<div class="rm8">' + README + ZONE + "</div>",
   manual=
   "<h2>README-ul, un CV al proiectului</h2>"
   "<p>README-ul este prima pagină a depozitului pe GitHub. Cititorul lui nu este grupa, ci cineva din afară: un "
   "cercetător care caută date asemănătoare, un posibil colaborator, un angajator care se uită la profilul GitHub. "
   "Ca la un CV, primul ecran decide dacă citește mai departe. De aceea README-ul începe cu rezultatul, nu cu "
   "istoria proiectului. Al doilea cititor este cel care vrea să refacă analiza: pentru el, README-ul spune de unde "
   "se iau datele, ce trebuie instalat, în ce ordine rulează caietele și ce rezultat produce fiecare.</p>"
   '<div class="rm8">' + README + ZONE + "</div>"
   + tabel(["Secțiunea", "Ce conține"], [
       ["titlul și rezultatul", "o frază cu rezultatul principal, cu un număr și cu condițiile lui"],
       ["figura principală", "cea care rezumă rezultatul; restul figurilor stau în raport"],
       ["Question", "întrebarea și de ce contează, în două fraze"],
       ["Data", "sursele, cu legături; unitatea de analiză; perioada; condițiile de folosire ale fiecărei surse "
                "și cum se obțin datele care nu stau în depozit"],
       ["Methods", "pașii 01-05, câte un rând fiecare, cu caietul lui"],
       ["Results", "două-trei constatări, cu cifre; lângă fiecare, caietul și figura din care vine"],
       ["Limitations", "ce nu pot arăta datele și metoda"],
       ["Reproduce", "versiunea Python, mediul (<code>requirements.txt</code>), comenzile de instalare, ordinea "
                     "caietelor și timpul de rulare"],
       ["Repository", "structura depozitului, ca arbore"],
       ["License", "licența codului, în fișierul <code>LICENSE</code> (de exemplu MIT); datele rămân sub "
                   "condițiile surselor lor"]])
   + "<p>Testul unui README bun: cineva care vede depozitul pentru prima dată reface analiza doar din el, "
     "într-un dosar gol, pe alt calculator.</p>"
   + nota("Fără membri și roluri",
          "README-ul descrie proiectul, nu echipa. Cine ce a făcut apare în raport, în secțiunea Contributions, "
          "și în istoricul commit-urilor.", True))


# ===========================================================================
#  3. Raportul
# ===========================================================================

RAPORT = tabel(["Secțiunea", "Ce conține"], [
    ["1. Introduction", "întrebarea, de ce contează, câteva lucrări din literatură"],
    ["2. Data", "sursele, colectarea, preprocesarea, curățarea; tabelele finale; deciziile, cu motivul lor"],
    ["3. Exploration", "figurile principale și ipotezele pe care le-au produs"],
    ["4. Model", "modelul, rezultatele, interpretarea"],
    ["5. Conclusions and limitations", "răspunsul la întrebare, ce nu se poate concluziona, ce ar urma"],
    ["6. Contributions", "fiecare membru: ce a făcut, caietele, partea scrisă din raport"],
    ["Appendix", "jurnalul deciziilor; cum se rulează analiza"],
])

sl("s3", "Raportul", "Raportul, în docs/",
   "<h2>Raportul: tot proiectul, într-un PDF</h2>"
   "<p class=\"cheie\">Documentul complet: ce s-a făcut, ce a ieșit, cu figurile și tabelele lui, și cine ce a "
   "făcut. README-ul îl rezumă; prezentarea îl parcurge.</p>"
   + RAPORT
   + nota("În depozit", "<code>docs/report.pdf</code>, pe <code>main</code>. GitHub deschide PDF-ul direct în "
                        "browser; sursa lui, oricare ar fi, poate sta alături, în <code>docs/</code>.", True),
   manual=
   "<h2>Raportul: tot proiectul, într-un PDF</h2>"
   "<p>Raportul este documentul complet al proiectului. Conține tot ce s-a făcut și tot ce a ieșit: datele și "
   "deciziile luate asupra lor, figurile, modelul, rezultatele și limitele lor, plus contribuția fiecărui membru. "
   "README-ul îl rezumă pentru un vizitator, iar prezentarea de la C9 îl parcurge.</p>"
   + RAPORT
   + "<p>Fiecare figură și fiecare tabel are o legendă care spune ce arată; fiecare decizie are motivul ei. "
     "Lungimea potrivită este de 8-12 pagini, cu figuri. Raportul îl scrie toată echipa, dar fiecare parte are un "
     "autor, trecut în secțiunea Contributions.</p>"
   + nota("PDF-ul pe GitHub",
          "GitHub afișează PDF-urile direct în browser, deci raportul se citește din depozit, fără descărcare. "
          "Fiind un fișier binar, Git nu arată ce s-a schimbat între versiuni: PDF-ul se exportă o dată, la "
          "final. Sursa (Markdown, Word sau alt format) poate sta lângă el, în <code>docs/</code>.", True))


# ===========================================================================
#  4. Prezentarea, la C9
# ===========================================================================

BARA = ('<div class="pr8">'
        '<div style="--ec:var(--accent)"><small>2 min</small><b>Proiectul</b><span>din README</span></div>'
        '<div style="--ec:var(--ambra)"><small>15 min</small><b>Contribuțiile, din raport</b>'
        '<span>câte un segment de 3 minute pentru fiecare membru, în ordinea pașilor</span>'
        '<div class="pr8__m"><i>membrul 1</i><i>membrul 2</i><i>membrul 3</i><i>membrul 4</i><i>membrul 5</i></div></div>'
        '<div style="--ec:var(--ardezie)"><small>3 min</small><b>Întrebări</b><span>oricui din echipă</span></div>'
        '</div>')

SEGMENT = ('<div class="ed6 ed6--3">'
           '<div><small>1 · afirmația</small><b>o frază: ce a făcut sau ce a găsit</b></div>'
           '<div><small>2 · dovada</small><b>figura sau tabelul din raport</b></div>'
           '<div class="nou"><small>3 · cum s-a făcut</small><b>o celulă din caietul lui, deja rulată</b></div>'
           '</div>')

PLAN = tabel(["Membrul", "Afirmația segmentului", "Figura sau tabelul din raport", "Celula din caiet"],
             [["", "", "", ""], ["", "", "", ""]])

SURSE_C8 = surse("Pentru README și raport", [
    ("GitHub Docs: About READMEs", "https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes",
     "unde se afișează README-ul și ce poate conține"),
    ("Make a README", "https://www.makeareadme.com/", "secțiunile unui README bun, cu exemple"),
    ("ZBW Open Economics (2026): The README File", "https://openeconomics.zbw.eu/en/2026/07/the-readme-file-practical-tips-for-documenting-your-replication-package/",
     "README-ul unui pachet de replicare: datele, cerințele, ordinea rulării, licența"),
    ("Wilson și colegii (2017): Good Enough Practices in Scientific Computing", "https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1005510",
     "organizarea unui proiect de date și documentarea lui"),
    ("The Turing Way", "https://book.the-turing-way.org/", "cercetarea reproductibilă, de la date la raport"),
])

sl("s4", "Prezentarea", "Prezentarea la C9",
   "<h2>Prezentarea, la C9: 20 de minute, toți membrii</h2>"
   + BARA + SEGMENT
   + nota("Azi, în echipă", "Raportul, README-ul și planul prezentării: cine, ce afirmație, ce figură, ce celulă. "
                            "Prezentarea se face din README, raport și caiete, fără slide-uri separate.", True),
   manual=
   "<h2>Prezentarea, la C9: 20 de minute, toți membrii</h2>"
   "<p>Prezentarea parcurge raportul. Începe cu README-ul, pentru imaginea de ansamblu, apoi fiecare membru "
   "prezintă o contribuție a lui, în segmente egale, în ordinea pașilor proiectului: întâi datele, apoi rezultatele. "
   "Modelul, concluziile și limitele le poate prezenta oricine din echipă.</p>"
   + BARA
   + "<p>Fiecare segment are aceeași formă:</p>"
   + SEGMENT
   + "<p>Prezentarea se face din documentele proiectului, fără slide-uri separate: README-ul pe GitHub, raportul "
     "PDF și caietele, deja rulate. Rularea completă pe un kernel nou se verifică la evaluare, nu în fața grupei. "
     "La o echipă cu alt număr de membri, timpul se împarte la fel: cu patru membri, aproape 4 minute fiecare; cu "
     "șase, 2,5 minute. La întrebări, oricare membru trebuie să poată răspunde și despre alte părți decât a lui.</p>"
   + "<p>Planul prezentării se face azi, în echipă, și intră în secțiunea Contributions a raportului:</p>"
   + PLAN
   + SURSE_C8)


# ===========================================================================
#  5. Feedback pentru curs
# ===========================================================================

GR_A, GR_B, GR_C = "Cum s-a predat", "Ce pot face singur acum", "Proiectul"

FEEDBACK = {
    "id": "c8-feedback",
    "capitol": "c8",
    "scala": ["1 deloc", "2", "3", "4", "5 întru totul"],
    "intrebari": [
        {"pas": 1, "fel": "scala", "cheie": "a1_slide", "grup": GR_A,
         "t": "Slide-urile interactive (graficele, harta, exercițiile de pe slide) m-au ajutat să înțeleg conceptele."},
        {"pas": 1, "fel": "scala", "cheie": "a2_manual", "grup": GR_A, "t": "Manualul lecției mi-a fost util după oră."},
        {"pas": 1, "fel": "scala", "cheie": "a3_caiete", "grup": GR_A,
         "t": "În caietele de seminar am scris eu cod, nu doar am rulat celule gata făcute."},
        {"pas": 1, "fel": "scala", "cheie": "a4_date", "grup": GR_A,
         "t": "Lucrul pe aceleași date în toate lecțiile (SCI și migrația) m-a ajutat să văd cum se leagă pașii analizei."},
        {"pas": 1, "fel": "scala", "cheie": "c1_echipa", "grup": GR_C,
         "t": "Împărțirea proiectului pe pași, cu un responsabil pentru fiecare caiet, a funcționat în echipa mea."},
        {"pas": 2, "fel": "scala", "cheie": "b1_api", "grup": GR_B,
         "t": "Pot colecta date printr-un API (Eurostat, Banca Mondială)."},
        {"pas": 2, "fel": "scala", "cheie": "b2_curatare", "grup": GR_B,
         "t": "Pot curăța și uni tabele, în pandas și în SQL."},
        {"pas": 2, "fel": "scala", "cheie": "b3_model", "grup": GR_B,
         "t": "Pot interpreta un model de regresie: coeficienții ca elasticități, reziduurile."},
        {"pas": 2, "fel": "scala", "cheie": "b4_git", "grup": GR_B,
         "t": "Pot lucra cu Git și GitHub într-o echipă: ramura dev, pull, push, conflictele."},
        {"pas": 2, "fel": "alege", "cheie": "ritm", "t": "Ritmul cursului a fost:",
         "ops": ["prea încet", "potrivit", "prea repede"]},
        {"pas": 2, "fel": "alege", "cheie": "lectia", "t": "Care lecție ar fi avut nevoie de mai mult timp?",
         "ops": ["C1 Introducere", "C2 API", "C3 Git", "C4 Curățare", "C5 Agregare", "C6 Explorare", "C7 Model",
                 "niciuna"]},
        {"pas": 3, "fel": "text", "cheie": "in_plus", "t": "Ce ar fi trebuit să conțină în plus acest curs?",
         "exemplu": "O temă, o unealtă, un tip de date sau un exercițiu care a lipsit."},
        {"pas": 3, "fel": "text", "cheie": "greu", "optional": True,
         "t": "Ce a fost cel mai greu de urmat și ce ar fi ajutat acolo? (opțional)",
         "exemplu": "Lecția sau pasul, și ce ar fi făcut diferența: un exemplu, mai mult timp, alt exercițiu."},
    ],
}

sl("s5", "Feedback", "Feedback pentru curs",
   "<h2>Feedback pentru curs</h2>"
   + ix("feedback", "Anonim: contul primește doar punctajul pentru completare", FEEDBACK),
   manual=
   "<h2>Feedback pentru curs</h2>"
   "<p>Ultima sarcină a cursului este o evaluare a lui: nouă afirmații pe o scală de la 1 la 5, ritmul, lecția "
   "care ar fi avut nevoie de mai mult timp și două întrebări deschise. Răspunsurile sunt anonime: se salvează "
   "fără cont și fără oră, separat de evidența celor care au completat. Contul primește doar punctajul pentru "
   "completare, ca la orice altă sarcină a lecției.</p>"
   + ix("feedback", "Anonim: contul primește doar punctajul pentru completare", FEEDBACK))


if __name__ == "__main__":
    L.scrie_tot()
