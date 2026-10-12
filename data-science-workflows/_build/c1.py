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

from comun import Lectie, ix, verif, tabel, nota


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
    "fisier": "date/brute/country.csv",
    "randuri": 31684,
    "coloane": [
        {"nume": "user_country", "tip": "object",
         "d": "codul de doua litere al tarii de unde pleaca legatura"},
        {"nume": "friend_country", "tip": "object",
         "d": "codul tarii spre care merge legatura"},
        {"nume": "scaled_sci", "tip": "int64",
         "d": "taria legaturii, scalata; se compara intre perechi, "
              "nu se citeste ca numar de prietenii"},
    ],
    "cap": [
        ["RO", "RO", 6252768],
        ["RO", "MD", 173794],
        ["RO", "AT", 124693],
        ["RO", "DE", 91228],
        ["RO", "HU", 85021],
    ],
    "capNota": "Cinci rânduri adevărate din fișier, dintre cele cu România pe "
               "primul capăt. Toate cele 178 de țări au exact aceleași trei "
               "coloane; se schimbă doar codurile.",
}


# ===========================================================================
#  1-2. Cursul
# ===========================================================================

TEME = [
    (1, "Introducere și instalarea softurilor",
     "Ce unelte folosim și de ce fiecare. Conturile, mediul de lucru, structura unui proiect."),
    (1, "Concepte cheie pentru analiza datelor",
     "Tipuri de date în Python, în SQL și în fișiere spațiale. Tipuri de fișiere. Formatul JSON."),
    (2, "Colectarea datelor prin API",
     "Ce e un API, cum se citește o documentație, cum se face o cerere. Postman, apoi requests."),
    (3, "Versionare și colaborare cu Git",
     "Istoric, reveniri, branch-uri, pull request. Cum lucrează patru oameni pe același cod fără să se calce."),
    (4, "Explorarea preliminară și curățarea",
     "Lipsuri, duplicate, tipuri greșite, coduri care nu se potrivesc între surse. Etapa cea mai lungă."),
    (5, "Baze de date cu Neon",
     "PostgreSQL în cloud. Tabele, chei, interogări. De ce un tabel de 31.684 de rânduri nu stă într-un fișier."),
    (5, "Agregarea datelor din surse diverse",
     "Îmbinarea pe o cheie comună. La date diadice, două îmbinări: una pentru fiecare capăt al perechii."),
    (6, "Analiza exploratorie și vizualizare",
     "Distribuții, relații, valori extreme. Grafice care lămuresc și grafice care induc în eroare."),
    (7, "Feature engineering",
     "Variabilele care răspund la întrebare nu se descarcă, se construiesc: rate, ponderi, distanțe, diferențe."),
    (7, "Aplicarea modelelor statistice",
     "Testarea formală a relației observate. Non-independența observațiilor, la date diadice."),
    (8, "Raportarea analizei și a rezultatelor",
     "Raport reproductibil, grafice pentru publicare, prezentarea proiectului."),
]

CRONOLOGIE = {
    "titlu": "Apasă pe o temă",
    "intro": "Unsprezece teme, opt ședințe. Punctele pline sunt ședințele care "
             "au temă nouă.",
    "sedinte": 8,
    "teme": [{"c": c, "n": n, "d": d} for c, n, d in TEME],
}

sl("s1", "Cursul", "Despre ce e cursul",
   "<h2>Fluxuri de lucru pentru știința datelor</h2>"
   "<p class=\"cheie\">Un drum complet, de la o întrebare la un rezultat în "
   "care poți avea încredere.</p>"
   + ix("semestru", "Temele semestrului", CRONOLOGIE)
   + nota("La final de oră", "Ai mediul de lucru pregătit, cont de GitHub legat "
          "de numărul matricol, o echipă, și primul tău notebook rulat pe date "
          "adevărate."),
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
   + ix("semestru", "Temele semestrului", CRONOLOGIE)
   + "<h3>Agenda primei ore</h3>"
   "<ol><li>Evaluarea cunoștințelor și a așteptărilor</li>"
   "<li>Prezentarea proiectului</li>"
   "<li>Pașii unui proiect de analiză de date</li>"
   "<li>Configurarea unui mediu de lucru virtual</li>"
   "<li>Tipuri de date în știința datelor</li>"
   "<li>Formatul JSON</li></ol>"
   + nota("La final de oră", "Ai mediul de lucru pregătit, cont de GitHub legat "
          "de numărul matricol, o echipă, și primul tău notebook rulat pe date "
          "adevărate."))


sl("s2", "Cursul", "Ce știi deja",
   "<h2>Unde ești acum</h2>"
   "<p>Un minut. Nu se notează.</p>"
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
    ['<a class="leg" href="https://code.visualstudio.com/" target="_blank" rel="noopener">Visual Studio Code</a>',
     "Editorul în care scriem cod", "~azi"],
    ['<a class="leg" href="https://www.python.org/downloads/" target="_blank" rel="noopener">Python 3.11+</a>',
     "Limbajul. Bifează <em>Add Python to PATH</em>", "~azi"],
    ['<a class="leg" href="https://github.com/signup" target="_blank" rel="noopener">GitHub</a>, cont',
     "Versionare, backup, colaborare", "~azi"],
    ['<a class="leg" href="https://neon.com/" target="_blank" rel="noopener">Neon</a>, cont',
     "Baze de date PostgreSQL, în cloud", "~cursul 5"],
    ['<a class="leg" href="https://www.postman.com/downloads/" target="_blank" rel="noopener">Postman</a>',
     "Testarea și explorarea API-urilor", "~cursul 2"],
]

sl("s3", "Softuri și conturi", "Ce instalezi, ce cont faci",
   "<h2>Cinci unelte, toate gratuite</h2>"
   + tabel(["Unealtă", "La ce", "Când"], [list(x) for x in UNELTE])
   + "<p class=\"cheie\">Singurul lucru cu termen azi: contul de GitHub.</p>"
   "<ol>"
   '<li><a class="leg" href="https://github.com/signup" target="_blank" rel="noopener">github.com/signup</a>, '
   "cu un nume de utilizator pe care să-l poți pune în CV</li>"
   "<li>Confirmă emailul</li>"
   '<li>Intră cu el <a class="leg" href="../../cont/">pe site-ul ăsta</a>, cu numărul matricol</li>'
   "</ol>",
   manual=
   "<h2>Softuri și conturi</h2>"
   "<p>Cinci unelte pentru tot semestrul. Primele trei se instalează azi, "
   "restul la lecția în care apar. Niciuna nu cere card.</p>"
   + tabel(["Unealtă", "La ce", "Când"], [list(x) for x in UNELTE])
   + "<h3>De ce Neon și nu PostgreSQL pe laptop</h3>"
   "<p>Pentru că o bază de date în cloud e vizibilă pentru toată echipa "
   "deodată. Un PostgreSQL instalat local rezolvă problema interogării, dar nu "
   "și pe cea a colaborării, care e jumătate din curs. În plus, nu pierdem o "
   "ședință pe instalare și pe diferențele dintre Windows și macOS.</p>"
   "<h3>De ce Postman, dacă tot scriem cod</h3>"
   "<p>Pentru că un API necunoscut se explorează mai repede cu un clic decât "
   "cu un script. Vezi imediat ce parametri acceptă, ce coduri de răspuns "
   "întoarce și ce formă are JSON-ul, și abia apoi scrii codul.</p>"
   "<h3>Contul GitHub</h3>"
   "<p>E singurul lucru din lecția asta care are termen azi. Toate celelalte se "
   "pot recupera; contul GitHub blochează lecția 3 pentru toată echipa dacă "
   "lipsește.</p>"
   "<ol>"
   '<li>Intră pe <a class="leg" href="https://github.com/signup" target="_blank" rel="noopener">github.com/signup</a>. '
   "Alege un nume de utilizator pe care să-l poți pune în CV: rămâne cu tine "
   "mult după curs.</li>"
   "<li>Confirmă adresa de email.</li>"
   '<li>Intră cu el <a class="leg" href="../../cont/">pe acest site</a> și '
   "leagă-l de numărul matricol.</li>"
   "</ol>"
   + nota("Ce se salvează despre tine",
          "Răspunsurile la verificări, exercițiile făcute, și pe ce slide ai "
          "ajuns. Nimic altceva. Detaliile sunt în "
          '<a class="leg" href="../../date-personale/">pagina despre date '
          'personale</a>, iar progresul ți-l poți șterge singur, oricând, din '
          '<a class="leg" href="../../cont/">contul tău</a>.'),
   dupa=verif("c1-v8", 1,
              "De ce versionăm codul într-un proiect de analiză de date?",
              ["Ca să ocupe mai puțin spațiu pe disc",
               "Ca să se vadă ce s-a schimbat, când și de cine, și ca să se poată reveni",
               "Pentru că e obligatoriu la publicare",
               "Ca să ruleze codul mai repede"],
              "Un rezultat se schimbă pentru că s-a schimbat codul, datele, sau "
              "amândouă. Fără istoric nu poți spune care. Spațiul pe disc chiar "
              "crește."))


# ===========================================================================
#  4. Pașii unui proiect
# ===========================================================================

DRUM = {
    "titlu": "Apasă pe o etapă",
    "intro": "Sus curge analiza datelor, jos ingineria modelelor. "
             "Baza de date stă deoparte fiindcă nu e o etapă.",
    "bandaSus": "Analiza datelor", "bandaJos": "Ingineria modelelor",
    "sus": [
        {"n": "Definirea problemei", "unde": "cursul 1",
         "d": "Tema, unitatea de analiză, întrebarea. Aici decizi ce înseamnă un "
              "rând în tabelul final: o țară, o pereche de județe, un an. Tot "
              "restul depinde de alegerea asta."},
        {"n": "Colectarea datelor", "unde": "cursul 2",
         "d": "Aduci datele prin API sau din fișiere. Salvezi întotdeauna "
              "varianta brută, neatinsă, ca să poți reveni la ea când descoperi "
              "o greșeală de curățare."},
        {"n": "Curățarea datelor", "unde": "cursul 4",
         "d": "Tipuri greșite, valori lipsă, duplicate, coduri care nu se "
              "potrivesc între surse. Etapa cea mai lungă și cea care decide "
              "dacă rezultatul înseamnă ceva."},
        {"n": "Analiza exploratorie", "unde": "cursul 6",
         "d": "Te uiți la date înainte de a le modela. Scopul nu e să "
              "demonstrezi ceva, e să înțelegi ce ai."}],
    "jos": [
        {"n": "Feature engineering", "unde": "cursul 7",
         "d": "Construiești variabilele care răspund la întrebare: rate, "
              "ponderi, distanțe, diferențe între capetele perechii."},
        {"n": "Modelare", "unde": "cursul 7",
         "d": "Testezi formal relația observată. Un model simplu, bine "
              "interpretat, bate unul complicat pe care nu îl poți explica."},
        {"n": "Implementare", "unde": "dincolo de curs",
         "d": "Modelul ajunge undeva unde îl folosește altcineva. La noi lanțul "
              "se oprește la raport, dar el continuă."},
        {"n": "Optimizare", "unde": "dincolo de curs",
         "d": "Parametri, performanță, costuri. Zona de inginerie."}],
    "final": {"n": "Raportare și vizualizare", "unde": "cursul 8",
              "d": "Rezultatul devine util abia când altcineva îl poate citi, "
                   "reproduce și critica. Graficele nu sunt decor, sunt "
                   "argumentul."},
    "baza": {"n": "Popularea și gestionarea bazei de date", "unde": "cursul 5",
             "d": "Nu e o etapă în lanț, e depozitul la care se întorc mai "
                  "multe etape. Colectarea scrie datele brute, curățarea "
                  "versiunea curată, agregarea tabelul final. Fără ea, într-o "
                  "echipă de patru, al doilea nu poate începe până nu-i trimite "
                  "primul un fișier pe chat."},
}

sl("s4", "Pașii unui proiect", "Data Science Workflow",
   "<h2>Pașii unui proiect de analiză de date</h2>"
   "<p class=\"cheie\">Fluxul e ciclic, nu liniar.</p>"
   + ix("drum", "Data Science Workflow", DRUM),
   manual=
   "<h2>Pașii unui proiect de analiză de date</h2>"
   "<p>Schema de mai jos are trei straturi. Partea de sus, de la definirea "
   "problemei până la raportare, e <strong>analiza datelor</strong>. Partea de "
   "jos, de la feature engineering până la optimizare, e <strong>ingineria "
   "modelelor</strong>. Împreună, cu baza de date care le leagă, fac "
   "<strong>știința datelor</strong>.</p>"
   + ix("drum", "Data Science Workflow", DRUM)
   + "<p>Săgețile punctate arată întoarcerile, și sunt partea cea mai "
   "importantă. Descoperi la curățare că un indicator lipsește pentru jumătate "
   "din unități și revii la colectare. Nu e un semn că ai greșit, e felul "
   "normal de a lucra.</p>"
   + nota("Baza de date nu e o etapă",
          "E locul unde etapele își lasă rezultatele. Într-un proiect de patru "
          "oameni, fără ea, al doilea nu poate începe până nu-i trimite primul "
          "un fișier pe chat."),
   dupa=verif("c1-v1", 1,
              "O echipă descoperă la analiza exploratorie că indicatorul ales "
              "nu are date pentru 40% din unități. Ce face?",
              ["Continuă doar pe unitățile care au date, fără să menționeze",
               "Se întoarce la colectare și caută un indicator alternativ",
               "Completează lipsurile cu media",
               "Schimbă modelul ca să tolereze lipsurile"],
              "Întoarcerea la o etapă anterioară e normală, nu e un eșec. "
              "Celelalte variante rămân discutabile, dar niciuna nu se ia "
              "înainte de a verifica dacă problema se rezolvă la sursă."))


# ===========================================================================
#  5-8. Proiectul
# ===========================================================================

DIRECTII = [
    ("Distanță și graniță", "Cât din conectivitate se explică prin apropiere geografică, și unde se rupe regula."),
    ("Diaspora", "Migrație față de conectivitate: unde coincid și unde nu."),
    ("Minorități și istorie", "Granițe vechi, regiuni istorice, comunități lingvistice."),
    ("Orașe mari", "Centrele universitare și bazinele lor de atracție."),
    ("Dezvoltare economică", "Conectivitate față de PIB regional, educație, urbanizare."),
    ("Europa", "Aceleași întrebări la nivel de țară sau regiune europeană."),
]

sl("s5", "Proiectul", "Proiectul și echipele",
   "<h2>Un depozit de echipă în care se vede tot drumul</h2>"
   "<p>Trei sau patru oameni. Aceleași date, întrebări diferite.</p>"
   + carduri(DIRECTII)
   + nota("Alegeți una până data viitoare",
          "Cine nu e într-o echipă, îl repartizez eu.", True)
   + nota("Nota vine din drum, nu din rezultat",
          "Se notează ce se vede în depozit: datele colectate, curățarea, "
          "deciziile scrise. Un rezultat negativ bine argumentat ia aceeași "
          "notă ca unul spectaculos."),
   manual=
   "<h2>Proiectul final</h2>"
   "<p>Proiectul se construiește bucată cu bucată, la fiecare curs.</p>"
   + tabel(["Cursul", "Ce adaugi"], [
       ["~1", "Mediul de lucru, conturile, echipa, primul notebook"],
       ["~2", "Primele date colectate prin API"],
       ["~3", "Depozitul de echipă și a doua sursă"],
       ["~4", "Dataseturile curățate și documentate"],
       ["~5", "Tabelul unificat, în baza de date"],
       ["~6", "Analiza exploratorie"],
       ["~7", "Variabilele derivate și modelul"],
       ["~8", "Raportul final și prezentarea"],
   ])
   + "<h3>Direcțiile</h3>"
   "<p>Toate pornesc din aceleași fișiere. Ce se schimbă e întrebarea.</p>"
   + carduri(DIRECTII)
   + nota("Până data viitoare", "Trimiteți componența echipei, cu numerele "
          "matricole și direcția aleasă."))


sl("s6", "Proiectul", "Sursele de date",
   "<h2>Pe ce lucrăm tot semestrul</h2>"
   + tabel(["Sursă", "Ce luăm", "Cum"], [
       ["<strong>Social Connectedness Index</strong><br>Data for Good at Meta",
        "Legăturile de prietenie dintre perechi de locuri, 178 de țări",
        "~fișiere, HDX"],
       ["<strong>Eurostat</strong>",
        "Populație, PIB regional, educație, la nivel de județ", "~API, JSON-stat"],
       ["<strong>Banca Mondială</strong> (WDI)",
        "Populație, PIB, urbanizare, la nivel de țară", "~API, JSON"],
   ])
   + ix("bare", "Partenerii României", {"cate": 15})
   + nota("Indicele e normalizat",
          "Spune cât de <em>probabilă</em> e o prietenie între doi oameni din "
          "cele două locuri, nu câți oameni de acolo trăiesc aici. Două "
          "întrebări diferite, și prima confuzie pe care o face oricine "
          "deschide datele astea.", True),
   manual=
   "<h2>Sursele de date</h2>"
   "<p>Sursa principală e <strong>Social Connectedness Index</strong>, produs "
   "de Data for Good at Meta din rețeaua de prietenii Facebook, agregat și "
   "anonimizat. Pentru fiecare pereche de locuri, indicele spune cât de "
   "probabil e ca doi oameni de acolo, unul din fiecare, să fie prieteni.</p>"
   + tabel(["Sursă", "Ce luăm", "Cum"], [
       ["<strong>Social Connectedness Index</strong><br>Data for Good at Meta",
        "Legăturile de prietenie dintre perechi de locuri, 178 de țări, până la nivel de județ în Europa",
        "~fișiere, HDX"],
       ["<strong>Eurostat</strong>",
        "Populație, PIB regional, educație, la nivel de județ", "~API, JSON-stat"],
       ["<strong>Banca Mondială</strong> (WDI)",
        "Populație, PIB, urbanizare, la nivel de țară", "~API, JSON"],
   ])
   + "<h3>Ce înseamnă „normalizat”</h3>"
   "<p>Indicele împarte numărul de legături observate la produsul populațiilor "
   "celor două locuri. Fără normalizare, orice clasament ar fi dominat de "
   "locurile mari: București ar fi pe primul loc peste tot, pentru că are cei "
   "mai mulți oameni. Cu normalizare, răspunde la întrebarea „cât de probabilă "
   "e o prietenie între doi oameni luați la întâmplare, unul din fiecare "
   "loc”.</p>"
   "<p>Consecința practică: un clasament după SCI nu e același lucru cu un "
   "clasament după mărimea diasporei.</p>"
   + ix("bare", "Partenerii României", {"cate": 15}))


sl("s7", "Proiectul", "Cluj sau București?",
   "<h2>Cluj sau București?</h2>"
   "<p>Pentru fiecare județ: cu care dintre cele două are legături mai probabile.</p>"
   + ix("diverg", "Cluj sau București", {"a": "Cluj", "b": "București"})
   + nota("Nu analizăm azi",
          "Analiza exploratorie e cursul 6. Deocamdată doar vedem spre ce "
          'lucrăm. Întrebarea e luată de la <a class="leg" '
          'href="https://socialcapital.org/" target="_blank" rel="noopener">Social '
          "Capital Lab</a>, care a pus-o pentru Madrid și Barcelona.", True),
   manual=
   "<h2>Cluj sau București?</h2>"
   "<p>Social Capital Lab a publicat o hartă a Europei care răspunde la o "
   "singură întrebare: fiecare regiune are mai mulți prieteni la Madrid sau la "
   "Barcelona? Harta a circulat mult, pentru că răspunsul nu se poate ghici și "
   "nu seamănă cu nicio hartă administrativă.</p>"
   "<p>Mai jos e aceeași întrebare pentru România, calculată din exact "
   "fișierele pe care le veți descărca la cursul 2.</p>"
   + ix("diverg", "Cluj sau București", {"a": "Cluj", "b": "București"})
   + "<p>Interpretarea o lăsăm pentru cursul 6. Dacă vă vine acum o explicație "
   "în minte, scrieți-o undeva și verificați-o peste zece săptămâni.</p>")


sl("s8", "Proiectul", "Ce formă au datele",
   "<h2>Date diadice</h2>"
   "<p class=\"cheie\">Un rând nu descrie un loc. Descrie o relație între două locuri.</p>"
   + ix("matrice", "1.764 de rânduri")
   + ix("cod", "Taie o felie din matrice", {
       "id": "c1-cod-diadic", "fisier": "diadic.py", "date": DATE_SCI,
       "sarcina": "Din 31.684 de rânduri vrei doar perechile care pleacă din "
                  "România. Uită-te în panoul de deasupra la numele coloanelor.",
       "cod": "import pandas as pd\n\n"
              "d = pd.read_csv(\"date/brute/country.csv\")\n"
              "print(len(d))                  # 31684\n\n"
              "# doar perechile care pleaca din Romania\n"
              "ro = d[d[{{1}}] == {{2}}]\n"
              "print(len(ro))                 # 178",
       "goluri": {
           "1": {"ok": ["\"user_country\"", "'user_country'"], "ajutor": "coloana"},
           "2": {"ok": ["\"RO\"", "'RO'"], "ajutor": "codul"}},
       "laBine": "178 de rânduri: România cu fiecare țară din set, inclusiv cu ea însăși.",
       "laRau": "Numele coloanei și codul se scriu între ghilimele, ca text.",
       "explicatie": "Fixezi un capăt al perechii și obții o listă monadică: "
                     "178 de rânduri, câte unul pentru fiecare țară. Asta e "
                     "mișcarea pe care o faci de fiecare dată când vrei să te "
                     "uiți la date diadice cu ochiul."}),
   manual=
   "<h2>Date diadice</h2>"
   "<p>Particularitatea datelor noastre schimbă fiecare etapă de mai târziu, "
   "deci merită înțeleasă de la început: un rând din fișierele SCI nu descrie "
   "un loc, ci o relație între două locuri.</p>"
   + tabel(["Monadic", "Diadic"], [
       ["un rând = o entitate", "un rând = o relație între două entități"],
       ["„de ce e locul ăsta așa?”", "„de ce sunt astea două legate?”"],
       ["42 de județe = 42 de rânduri", "42 de județe = 42 × 42 de rânduri"],
       ["un merge pentru atribute", "două merge-uri, câte unul pe capăt"],
       ["observații independente", "același loc apare în sute de rânduri"],
   ])
   + "<h3>Trei consecințe care revin tot semestrul</h3>"
   "<ol><li><strong>Tabelul crește cu pătratul.</strong> Nu se mai poate citi "
   "cu ochiul, deci trebuie interogat. De aici nevoia de bază de date.</li>"
   "<li><strong>Atributele se lipesc de două ori.</strong> Populația „de unde” "
   "și populația „către unde” sunt două coloane diferite, din același tabel "
   "sursă.</li>"
   "<li><strong>Observațiile nu sunt independente.</strong> Cluj apare în 41 "
   "de rânduri doar pentru România. Un model care presupune independență dă "
   "erori standard prea mici.</li></ol>"
   + ix("matrice", "1.764 de rânduri")
   + ix("cod", "Taie o felie din matrice", {
       "id": "c1-cod-diadic", "fisier": "diadic.py", "date": DATE_SCI,
       "sarcina": "Păstrează doar perechile care pleacă din România.",
       "cod": "import pandas as pd\n\n"
              "d = pd.read_csv(\"date/brute/country.csv\")\n"
              "print(len(d))                  # 31684\n\n"
              "ro = d[d[{{1}}] == {{2}}]\n"
              "print(len(ro))                 # 178",
       "goluri": {
           "1": {"ok": ["\"user_country\"", "'user_country'"], "ajutor": "coloana"},
           "2": {"ok": ["\"RO\"", "'RO'"], "ajutor": "codul"}},
       "laBine": "178 de rânduri: România cu fiecare țară, inclusiv cu ea însăși.",
       "laRau": "Numele coloanei se scrie între ghilimele.",
       "explicatie": "Fixezi un capăt al perechii și obții o listă monadică."}),
   dupa=verif("c1-v5", 2,
              "Cu cele 178 de țări din SCI, câte rânduri are matricea completă?",
              ["178", "356", "31.684", "15.753"],
              "178 × 178 = 31.684, exact câte rânduri are fișierul "
              "<code>country.csv</code> pe care îl descărcați azi. Creșterea cu "
              "pătratul e motivul pentru care, de la cursul 5, lucrăm cu o bază "
              "de date."))


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
             "ex": "an = 2024\npopulatie = 19051562",
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
         "ex": "rand = {\"tara\": \"RO\",\n        \"an\": 2023,\n        \"valoare\": 19051562}\nprint(rand[\"valoare\"])",
         "la": "Fiecare răspuns de API ajunge aici."}]},
    {"nume": "Altele", "tipuri": [
        {"n": "funcții", "cls": "callable",
         "d": "Funcțiile sunt și ele valori: le poți pune într-o listă sau da ca argument.",
         "ex": "def curata(x):\n    return x.strip()\n\nnume = [curata(n) for n in brute]"},
        {"n": "module", "cls": "class module",
         "d": "Un fișier de Python importat devine un obiect cu propriul tip.",
         "ex": "import pandas as pd\nprint(type(pd))          # module"}]},
]

sl("s9", "Tipuri de date", "Tipuri în Python",
   "<h2>Tipuri de date în Python</h2>"
   "<p>Tipul decide ce poți face cu valoarea. Sortarea pune 1990 după 189 dacă "
   "anii au venit ca text.</p>"
   + ix("arbore", "Arborele tipurilor",
        {"titlu": "Apasă pe orice tip",
         "intro": "Vezi ce e, cum arată, și unde apare la noi.",
         "legenda": True, "radacina": "valoare", "ramuri": RAMURI_PY}),
   manual=
   "<h2>Tipuri de date în Python</h2>"
   "<p>Tipul unei valori decide ce poți face cu ea. Nu e o chestiune de "
   "pedanterie: o coloană de ani citită ca text se sortează alfabetic, deci "
   "1990 ajunge după 189, și nimeni nu primește vreo eroare.</p>"
   + ix("arbore", "Arborele tipurilor",
        {"titlu": "Apasă pe orice tip",
         "intro": "Vezi ce e, cum arată, și unde apare la noi.",
         "legenda": True, "radacina": "valoare", "ramuri": RAMURI_PY})
   + "<p>Împărțirea care contează cel mai des în practică e cea dintre tipuri "
   "modificabile și nemodificabile. O listă se schimbă pe loc; un tuplu nu. De "
   "aceea un tuplu poate fi cheie de dicționar, iar o listă nu.</p>")


sl("s10", "Tipuri de date", "Recunoaște tipul",
   "<h2>Opt valori</h2>"
   + ix("tipuri", "Pune fiecare valoare la tipul ei", {"id": "c1-tipuri", "valori": [
       {"v": "'2024'", "t": "str", "e": "Ghilimelele fac diferența. Arată ca un an, dar e text: exact capcana din CSV."},
       {"v": "2024", "t": "int", "e": "Fără ghilimele, număr întreg. Se compară și se sortează corect."},
       {"v": "3.7", "t": "float", "e": "Punctul zecimal îl face float. Cu virgulă, în fișiere românești, ajunge text."},
       {"v": "None", "t": "None", "e": "Absența valorii. Nu e zero și nu e text gol."},
       {"v": "True", "t": "bool", "e": "Cu majusculă în Python. Rezultatul oricărei condiții."},
       {"v": "[1, 2, 3]", "t": "list", "e": "Paranteze drepte: listă, ordonată și modificabilă."},
       {"v": "(45.7, 21.2)", "t": "tuple", "e": "Paranteze rotunde: tuplu, nemodificabil. Tipic pentru coordonate."},
       {"v": "{'tara': 'RO'}", "t": "dict", "e": "Perechi cheie și valoare. Structura unui obiect JSON."},
   ]}))


sl("s11", "Tipuri de date", "Capcanele de tip",
   "<h2>Greșelile care nu dau eroare</h2>"
   "<p class=\"cheie\"><code>None</code>, <code>0</code> și <code>\"\"</code> "
   "arată la fel într-un tabel gol. Zero e o măsurătoare; <code>None</code> e "
   "absența ei.</p>"
   + ix("cod", "Repară două conversii", {
       "id": "c1-cod-tipuri", "fisier": "tipuri.py",
       "sarcina": "Două greșeli de tip, dintre cele care nu crapă imediat.",
       "cod": "# anul a venit ca text din CSV\n"
              "an_text = \"2024\"\n"
              "urmatorul = {{1}}(an_text) + 1\n"
              "print(urmatorul)             # 2025\n\n"
              "# codul NUTS trebuie sa ramana text, cu zerourile din fata\n"
              "d = pd.read_csv(\"coduri.csv\", dtype={\"cod\": {{2}}})\n"
              "print(d.cod.iloc[0])         # 01234",
       "goluri": {
           "1": {"ok": ["int"], "ajutor": "funcția"},
           "2": {"ok": ["str"], "ajutor": "tipul"}},
       "laBine": "Amândouă apar în primele zece minute de curățare, la cursul 4.",
       "laRau": "Fără ghilimele: aici se cer o funcție și un tip, nu text.",
       "explicatie": "Niciuna nu dă eroare dacă o lași așa. "
                     "<code>\"2024\" + \"1\"</code> dă liniștit "
                     "<code>\"20241\"</code>, iar fără "
                     "<code>dtype={\"cod\": str}</code> zerourile din fața "
                     "codurilor dispar în tăcere."}),
   manual=
   "<h2>Greșelile care nu dau eroare</h2>"
   "<p>Greșelile de tip care crapă se repară în două minute. Problema o fac "
   "cele care trec: codul rulează, fișierul se scrie, iar rezultatul e greșit "
   "fără ca nimic să semnaleze.</p>"
   + ix("cod", "Repară două conversii", {
       "id": "c1-cod-tipuri", "fisier": "tipuri.py",
       "sarcina": "Două greșeli de tip, dintre cele care nu crapă imediat.",
       "cod": "an_text = \"2024\"\n"
              "urmatorul = {{1}}(an_text) + 1\n"
              "print(urmatorul)             # 2025\n\n"
              "d = pd.read_csv(\"coduri.csv\", dtype={\"cod\": {{2}}})\n"
              "print(d.cod.iloc[0])         # 01234",
       "goluri": {
           "1": {"ok": ["int"], "ajutor": "funcția"},
           "2": {"ok": ["str"], "ajutor": "tipul"}},
       "laBine": "Amândouă apar la cursul 4.",
       "laRau": "Fără ghilimele: o funcție și un tip.",
       "explicatie": "<code>\"2024\" + \"1\"</code> dă <code>\"20241\"</code> "
                     "fără să se plângă nimeni."})
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


sl("s12", "Tipuri de date", "Tipuri în SQL",
   "<h2>În baza de date, tipul se declară</h2>"
   "<p>Ce nu se potrivește, e respins. Uită-te la valori și alege.</p>"
   + ix("coloane", "Tabelul SCI, la cursul 5", {
       "id": "c1-sql-coloane",
       "fisier": "create table sci (…)",
       "nota": "valori adevărate din country.csv",
       "sarcina": "Pentru fiecare coloană, tipul potrivit.",
       "tipuri": ["CHAR(2)", "VARCHAR(50)", "TEXT", "INT", "BIGINT", "BOOLEAN"],
       "coloane": [
           {"nume": "user_country", "ok": "CHAR(2)",
            "de_ce": "lungime fixă, exact două caractere; orice altceva e respins la inserare"},
           {"nume": "friend_country", "ok": "CHAR(2)",
            "de_ce": "același cod, aceeași regulă"},
           {"nume": "scaled_sci", "ok": "BIGINT",
            "de_ce": "6.252.768 încape în INT, dar la nivel de regiune valorile trec de 2.147.483.647"}],
       "cap": [["RO", "RO", 6252768], ["RO", "MD", 173794],
               ["RO", "AT", 124693], ["RO", "HU", 85021]],
       "laBine": "Exact tabelul pe care îl vei crea în Neon, la cursul 5.",
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
   + ix("coloane", "Tabelul SCI, la cursul 5", {
       "id": "c1-sql-coloane",
       "fisier": "create table sci (…)",
       "nota": "valori adevărate din country.csv",
       "sarcina": "Pentru fiecare coloană, tipul potrivit.",
       "tipuri": ["CHAR(2)", "VARCHAR(50)", "TEXT", "INT", "BIGINT", "BOOLEAN"],
       "coloane": [
           {"nume": "user_country", "ok": "CHAR(2)",
            "de_ce": "lungime fixă, exact două caractere"},
           {"nume": "friend_country", "ok": "CHAR(2)",
            "de_ce": "același cod, aceeași regulă"},
           {"nume": "scaled_sci", "ok": "BIGINT",
            "de_ce": "la nivel de regiune valorile trec de limita lui INT"}],
       "cap": [["RO", "RO", 6252768], ["RO", "MD", 173794],
               ["RO", "AT", 124693], ["RO", "HU", 85021]],
       "laBine": "Exact tabelul din Neon, la cursul 5.",
       "laRau": "Codurile au lungime fixă."})
   + nota("Și cheia primară",
          "<code>primary key (user_country, friend_country)</code> e ce "
          "împiedică aceeași pereche să intre de două ori: greșeala clasică la "
          "reîncărcarea unui fișier."),
   dupa=verif("c1-v9", 2,
              "Coduri de județ de forma <code>RO113</code>, toate de cinci "
              "caractere. Ce tip alegi?",
              ["<code>INT</code>, pentru că par numere",
               "<code>TEXT</code>, pentru că nu se știe niciodată",
               "<code>CHAR(5)</code>, pentru că lungimea e fixă",
               "<code>VARCHAR</code> fără limită"],
              "Un cod nu e un număr: nu se adună, nu se sortează numeric, iar "
              "<code>INT</code> ar distruge zerourile din față. "
              "<code>CHAR(5)</code> transformă o regulă pe care o știi tu "
              "într-una pe care o verifică baza de date."))


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

sl("s13", "Tipuri de date", "Tipuri spațiale",
   "<h2>Tipuri de date spațiale</h2>"
   "<p>Ne trebuie ca să definim „vecin” și „distanță”.</p>"
   + ix("arbore", "Ierarhia geometriilor",
        {"titlu": "Apasă pe oricare",
         "intro": "<code>Point</code>, <code>Curve</code> și <code>Surface</code> "
                  "sunt formele de bază; restul sunt cazurile lor concrete.",
         "radacina": "geometry", "ramuri": RAMURI_GEO})
   + nota("De ce contează pentru noi",
          "Ca să spui „județele vecine sunt mai legate” îți trebuie o definiție "
          "pentru vecin, iar aceea se calculează din poligoane.", True))


sl("s14", "Tipuri de date", "Tipuri de fișiere",
   "<h2>Text sau binar</h2>"
   "<p class=\"cheie\">Text îl citești cu ochiul. Binar are nevoie de programul lui.</p>"
   + ix("sortare", "Pune fiecare extensie în coșul ei", {
       "id": "c1-cod-fisiere",
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
       "id": "c1-cod-fisiere",
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
   ]),
   dupa=verif("c1-v10", 0,
              "Ai salvat tabelul în CSV. La recitire, coloana cu coduri care "
              "începeau cu zero a devenit numerică și zerourile au dispărut. De ce?",
              ["CSV nu păstrează tipurile; la recitire, fiecare coloană e reinterpretată din conținut",
               "Fișierul s-a corupt la salvare",
               "Pandas are o eroare cunoscută",
               "Codurile trebuiau salvate cu majuscule"],
              "CSV e text simplu: nu are unde să scrie că o coloană e text. "
              "Trei ieșiri: specifici tipul la citire "
              "(<code>dtype={\"cod\": str}</code>), salvezi în Parquet, sau ții "
              "datele în baza de date."))


# ===========================================================================
#  15-16. JSON
# ===========================================================================

sl("s15", "JSON", "Formatul JSON",
   "<h2>Două structuri, cuibărite oricât de adânc</h2>"
   + '<div class="grila grila--2">'
   '<div class="card"><div class="card__t">Obiect <span class="mono">{ }</span></div>'
   '<p class="card__d" style="margin-top:8px">Perechi cheie–valoare. În Python: <code>dict</code>.</p></div>'
   '<div class="card"><div class="card__t">Tablou <span class="mono">[ ]</span></div>'
   '<p class="card__d" style="margin-top:8px">Listă ordonată. În Python: <code>list</code>.</p></div>'
   "</div>"
   + ix("desfa", "Cum devine un răspuns un tabel", {
       "id": "c1-desfa",
       "sursa": "api.worldbank.org",
       "buton": "Arată-mi lista",
       "cheieCap": "paginare", "cheieLista": "date",
       "coloane": ["tara", "an", "populatie"],
       "elemente": [
           {"tara": "RO", "an": 2023, "populatie": 19051562},
           {"tara": "RO", "an": 2022, "populatie": 19047009},
           {"tara": "HU", "an": 2023, "populatie": 9589872},
       ],
       "p0": "Tot răspunsul, așa cum vine de la API.",
       "p1": "Lista dinăuntru: numai asta devine tabel.",
       "p2": "Fiecare element al listei a devenit un rând."},
      "Apasă de două ori și uită-te ce se aprinde."),
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
   + ix("desfa", "Cum devine un răspuns un tabel", {
       "id": "c1-desfa",
       "sursa": "api.worldbank.org",
       "buton": "Arată-mi lista",
       "cheieCap": "paginare", "cheieLista": "date",
       "coloane": ["tara", "an", "populatie"],
       "elemente": [
           {"tara": "RO", "an": 2023, "populatie": 19051562},
           {"tara": "RO", "an": 2022, "populatie": 19047009},
           {"tara": "HU", "an": 2023, "populatie": 9589872},
       ],
       "p0": "Tot răspunsul, așa cum vine de la API.",
       "p1": "Lista dinăuntru: numai asta devine tabel.",
       "p2": "Fiecare element al listei a devenit un rând."})
   + nota("De aici vine json_normalize",
          "Operația pe care ai văzut-o are un nume și o funcție în pandas. "
          "O scriem la cursul 2, dar e bine să fi văzut întâi ce face."))


sl("s16", "JSON", "Drumul până la valoare",
   "<h2>Un răspuns real, desfăcut</h2>"
   "<p>Banca Mondială, populația României.</p>"
   + ix("json", "API Banca Mondială", {
       "radacina": "raspuns",
       "date": [
           {"page": 1, "pages": 3, "per_page": 2, "total": 6},
           [{"indicator": {"id": "SP.POP.TOTL", "value": "Population, total"},
             "country": {"id": "RO", "value": "Romania"},
             "countryiso3code": "ROU", "date": "2023", "value": 19051562},
            {"indicator": {"id": "SP.POP.TOTL", "value": "Population, total"},
             "country": {"id": "RO", "value": "Romania"},
             "countryiso3code": "ROU", "date": "2022", "value": None}]]},
      "Apasă pe orice rând ca să vezi cum se ajunge la el.")
   + ix("cod", "Scrie drumul", {
       "id": "c1-cod-json", "fisier": "populatie.py",
       "sarcina": "Mergi până la populația din 2023.",
       "cod": "raspuns = requests.get(url, params={\"format\": \"json\"}).json()\n\n"
              "# paginarea e primul element, datele sunt in al doilea\n"
              "date = raspuns[{{1}}]\n\n"
              "# prima inregistrare, cea mai recenta\n"
              "populatie = date[0][{{2}}]\n"
              "print(populatie)             # 19051562",
       "goluri": {"1": {"ok": ["1"], "ajutor": "indice"},
                  "2": {"ok": ["\"value\"", "'value'"], "ajutor": "cheia"}},
       "laBine": "Ăsta e drumul pe care îl vei scrie la cursul 2, de zeci de ori.",
       "laRau": "Numerotarea începe de la zero. Cheia se scrie între ghilimele.",
       "explicatie": "<code>raspuns[1]</code> sare peste obiectul de paginare. "
                     "<code>[\"value\"]</code> scoate numărul. Dacă valoarea "
                     "lipsește primești <code>None</code>, nu zero."}),
   dupa=verif("c1-v4", 1,
              "Ce diferență e între <code>\"value\": null</code> și lipsa "
              "completă a cheii <code>value</code>?",
              ["Niciuna",
               "null spune explicit că valoarea lipsește; cheia absentă înseamnă că serviciul nu raportează deloc câmpul",
               "null înseamnă zero",
               "Cheia absentă e o eroare a serverului"],
              "Un null devine o valoare lipsă pe care o poți număra și raporta. "
              "O cheie absentă poate deveni o coloană care lipsește cu totul "
              "pentru anumite înregistrări, iar codul cade abia mai târziu."))


# ===========================================================================
#  17-18. Mediul și proiectul
# ===========================================================================

sl("s17", "Mediul de lucru", "Mediul virtual",
   "<h2>Un dosar cu propriul Python</h2>"
   "<p>Ca două proiecte să nu-și strice reciproc pachetele.</p>"
   + ix("terminal", "Încearcă aici, înainte să o faci la tine", None,
        "Terminalul răspunde ca unul adevărat, inclusiv la greșeli. Scrie "
        "<code>ajutor</code> dacă te blochezi.")
   + nota("Cum știi că e activ",
          "Promptul începe cu <code>(venv)</code>. Fără paranteza aceea, "
          "instalezi în Python-ul global: cea mai frecventă sursă de „la mine "
          "mergea”."),
   manual=
   "<h2>Medii de lucru virtuale în Python</h2>"
   "<p>Python instalează pachetele într-un singur loc comun. Dacă lucrezi la "
   "două proiecte care au nevoie de versiuni diferite ale aceleiași "
   "biblioteci, al doilea îl strică pe primul în tăcere. Un mediu virtual e un "
   "dosar separat, al proiectului tău, cu propria copie de Python și propriile "
   "pachete.</p>"
   "<pre><code><span class=\"c\"># creare, o singură dată, în folderul proiectului</span>\n"
   "python -m venv venv\n\n<span class=\"c\"># activare (Windows)</span>\nvenv\\Scripts\\activate\n\n"
   "<span class=\"c\"># activare (macOS / Linux)</span>\nsource venv/bin/activate\n\n"
   "<span class=\"c\"># instalare pachete, în mediul activ</span>\npip install requests pandas\n\n"
   "<span class=\"c\"># lista pachetelor, ca altcineva să refacă mediul</span>\n"
   "pip freeze &gt; requirements.txt\n\n<span class=\"c\"># dezactivare</span>\ndeactivate</code></pre>"
   + ix("terminal", "Încearcă aici, înainte să o faci la tine", None,
        "Terminalul răspunde ca unul adevărat, inclusiv la greșeli.")
   + nota("Cum știi că e activ",
          "Promptul începe cu <code>(venv)</code>. Folderul <code>venv</code> "
          "nu se urcă niciodată în depozit: e mare, e al sistemului tău, și se "
          "reface dintr-o comandă, din <code>requirements.txt</code>."),
   dupa=ix("ordine", "Ordinea comenzilor", {
       "id": "c1-cod-venv",
       "sarcina": "Pune comenzile în ordinea în care se dau. Două dintre ele "
                  "fac altceva decât crezi dacă vin prea devreme.",
       "linii": ["python -m venv venv", "venv\\Scripts\\activate",
                 "pip install requests pandas", "pip freeze > requirements.txt",
                 "deactivate"],
       "laBine": "Exact asta vei face la începutul fiecărui proiect.",
       "laRau": "Gândește-te ce există pe disc în momentul fiecărei comenzi.",
       "explicatie": "<code>pip install</code> înainte de activare instalează în "
                     "Python-ul global și nu dă nicio eroare, doar te trezești "
                     "peste o zi că importul nu merge. <code>pip freeze</code> "
                     "are sens abia după instalare, altfel scrie un fișier gol."})
   + verif("c1-v3", 1,
           "Ai activat mediul, ai instalat pandas, ai închis laptopul. A doua "
           "zi <code>import pandas</code> dă eroare. De ce?",
           ["Pandas s-a dezinstalat singur", "Ai uitat să activezi mediul virtual",
            "Mediul expiră după 24 de ore", "Trebuie reinstalat Python"],
           "Mediul nu se activează singur într-un terminal nou. VS Code o face "
           "automat dacă îi selectezi interpretorul din folderul "
           "<code>venv</code>: <span class=\"mono\">Ctrl+Shift+P → Python: "
           "Select Interpreter</span>."))


STRUCTURA = """proiect/
├── date/
│   ├── brute/          <span class="c"># exact cum au venit, nu se modifică</span>
│   └── curate/         <span class="c"># rezultatul curățării</span>
├── caiete/             <span class="c"># Jupyter: explorare</span>
├── cod/                <span class="c"># funcții refolosite</span>
├── rezultate/          <span class="c"># grafice și tabele</span>
├── venv/               <span class="c"># mediul; NU se urcă</span>
├── .gitignore
├── requirements.txt
└── README.md"""

sl("s18", "Proiectul tău", "Fă-ți proiectul, acum",
   "<h2>Proiectul tău, la laborator</h2>"
   f"<pre><code>{STRUCTURA}</code></pre>"
   + ix("dovada", "Rulezi la tine, lipești aici", {
       "id": "c1-dovada-mediu",
       "sarcina": "Fiecare rând cere o comandă rulată la tine, în terminalul "
                  "din VS Code. Nu se poate completa din cap.",
       "pasi": [
           {"t": "Mediul virtual e creat și activat",
            "cmd": "python -c \"import sys; print(sys.prefix)\"",
            "gol": "calea afișată",
            "cauta": "venv",
            "daca_nu": "Calea nu conține „venv”, deci rulezi Python-ul global. Activează mediul întâi."},
           {"t": "Pachetele sunt instalate în mediu",
            "cmd": "pip freeze",
            "gol": "lipește linia cu pandas",
            "cauta": r"pandas\s*==\s*\d",
            "daca_nu": "Caut o linie de forma pandas==2.x. Rulează pip install requests pandas, cu mediul activat."},
           {"t": "Datele brute sunt descărcate",
            "cmd": "python -c \"import pandas as pd; print(pd.read_csv('date/brute/country.csv').shape)\"",
            "gol": "forma tabelului",
            "cauta": r"\(\s*31684\s*,\s*5\s*\)",
            "daca_nu": "Aștept (31684, 5). Dacă primești altceva, fișierul nu e cel bun sau nu e în date/brute/."},
       ],
       "laBine": "Mediul, datele și primul calcul sunt la locul lor.",
       "laRau": "Rândurile roșii încă nu sunt gata.",
       "explicatie": "Ultimul rând e deja o verificare de date: ai citit 31.684 "
                     "de rânduri și ai confirmat că fișierul e cel bun, înainte "
                     "să construiești ceva peste el."})
   + nota("Datele",
          'Fișierul <code>country.csv</code> se ia de pe '
          '<a class="leg" href="https://data.humdata.org/dataset/social-connectedness-index" '
          'target="_blank" rel="noopener">HDX</a>, 0,6 MB. Îl pui în '
          "<code>date/brute/</code> și nu îl mai modifici niciodată.")
   + "<h3>Până data viitoare</h3>"
   "<ol>"
   '<li><strong>Cont GitHub</strong>, legat de numărul matricol <a class="leg" href="../../cont/">aici</a></li>'
   "<li><strong>Echipa</strong>: trei sau patru oameni, cu o direcție aleasă</li>"
   "<li><strong>Proiectul</strong>: folder, mediu virtual, date descărcate</li>"
   "</ol>"
   + '<div class="grila grila--2" style="margin-top:22px">'
   '<a class="resursa" href="../"><span class="resursa__ic">→</span>'
   '<span class="resursa__txt"><span class="resursa__t">Pagina cursului 1</span>'
   '<span class="resursa__d">Materiale și legături</span></span></a>'
   '<a class="resursa" href="../../c2-colectarea-prin-api/"><span class="resursa__ic">→</span>'
   '<span class="resursa__txt"><span class="resursa__t">Cursul 2</span>'
   '<span class="resursa__d">Colectarea datelor prin API</span></span></a></div>')


L.scrie_tot()
