# -*- coding: utf-8 -*-
"""
Lecția 2: Colectarea datelor prin API.

Urmează prezentarea Curs_2.pptx, slide cu slide, în aceeași ordine:
analogia restaurantului, tipurile de API, cronologia, stilurile, arhitectura
REST, metodele HTTP, endpoint-ul și structura lui, sursele de date, requests.

Ce am adăugat peste prezentare, și de ce:
  - codurile de răspuns, pentru că fără ele prima cerere care eșuează pare o
    pană de internet;
  - exercițiile cu cod, pentru că o cerere se învață scriind-o;
  - pasul de proiect de la final, ca ora să lase ceva în depozit.

Datele proiectului nu sunt încă toate adunate, deci exercițiile lucrează pe
API-ul Băncii Mondiale, care e public, nu cere cheie și e deja folosit la
cursul 1.

Rulare:  python _build/c2.py
"""

from comun import Lectie, ix, verif, tabel, nota

L = Lectie(2, "c2-colectarea-prin-api", "Colectarea datelor prin API",
           "Ce este un API, cum se citește o documentație, cum arată o cerere "
           "și cum aduci primele date reale în proiect.")
sl = L.sl


# ===========================================================================
#  1-2. Unde suntem
# ===========================================================================

AGENDA = [
    ("Ce este un API", "azi", "Analogia restaurantului, tipurile de API, de ce ne trebuie unul."),
    ("Cum arată o cerere", "azi", "Metode HTTP, endpoint, parametri, coduri de răspuns."),
    ("Postman", "azi", "Aceeași cerere, făcută cu mâna, înainte de a o scrie în cod."),
    ("requests", "azi", "Biblioteca din Python cu care colectăm de acum înainte."),
    ("Primele date în proiect", "azi", "O cerere adevărată, salvată în depozitul echipei."),
    ("Git și colaborare", "cursul 3", "Cum lucrează patru oameni pe același cod."),
]

sl("s1", "Cursul", "Despre ce e ora de azi",
   "<h2>Colectarea datelor prin API</h2>"
   "<p class=\"cheie\">Până acum ai citit un fișier primit de-a gata. "
   "De azi, ți-l aduci singur.</p>"
   "<p>Cinci lucruri, în ordinea asta.</p>"
   + ix("etape", "Agenda",
        {"titlu": "Ora de azi", "intro": "Apasă pe oricare.",
         "etape": [{"nume": n, "unde": u, "text": d} for n, u, d in AGENDA]},
        "Apasă pe un punct ca să vezi ce intră în el."),
   manual=
   "<h2>Colectarea datelor prin API</h2>"
   "<p>La cursul 1 ai deschis un fișier care era deja pe disc. E felul cel mai "
   "simplu de a ajunge la date și, din păcate, și cel mai fragil: cineva l-a "
   "descărcat cândva, de undeva, și nimeni nu mai știe exact de unde, când, și "
   "cu ce filtre. Dacă mâine apare o versiune nouă, trebuie refăcut totul cu "
   "mâna.</p>"
   "<p>Un API rezolvă exact asta. Datele nu mai vin printr-un om care apasă "
   "„Download”, ci printr-o linie de cod care se poate rula din nou, mâine, de "
   "altcineva, și care dă același rezultat sau spune răspicat de ce nu.</p>"
   + ix("etape", "Agenda",
        {"titlu": "Ora de azi", "intro": "Apasă pe oricare.",
         "etape": [{"nume": n, "unde": u, "text": d} for n, u, d in AGENDA]}))

sl("s2", "Cursul", "Unde ai rămas",
   "<h2>Înainte de a începe</h2>"
   "<ul>"
   "<li>mediul virtual creat și activat</li>"
   "<li>depozitul echipei pe GitHub</li>"
   "<li>primul caiet, cu fișierul SCI deschis</li>"
   "</ul>"
   "<p>Dacă unul lipsește, îl faci acum: tot ce urmează se adaugă peste el.</p>"
   + verif("c2-v1", 1,
           "De ce lucrăm într-un mediu virtual și nu direct în Python-ul de sistem?",
           ["Ca să meargă mai repede",
            "Ca fiecare proiect să-și aibă pachetele lui, cu versiunile lui",
            "Ca să ocupe mai puțin spațiu",
            "Nu contează, e doar o convenție"],
           "Două proiecte pot cere versiuni diferite ale aceleiași biblioteci. "
           "Fără medii separate, al doilea îl strică pe primul, iar vina cade "
           "pe cod, nu pe mediu."),
   manual=
   "<h2>Înainte de a începe</h2>"
   "<p>Lecția de azi presupune trei lucruri de la cursul 1: un mediu virtual "
   "activat, depozitul echipei pe GitHub, și un caiet în care ai deschis "
   "fișierul SCI. Dacă îți lipsește vreunul, întoarce-te la "
   "<a class=\"leg\" href=\"../../c1-introducere-si-mediu/tutorial/\">manualul "
   "cursului 1</a> și fă-l acum: tot ce urmează se adaugă peste.</p>"
   + verif("c2-v1", 1,
           "De ce lucrăm într-un mediu virtual și nu direct în Python-ul de sistem?",
           ["Ca să meargă mai repede",
            "Ca fiecare proiect să-și aibă pachetele lui, cu versiunile lui",
            "Ca să ocupe mai puțin spațiu",
            "Nu contează, e doar o convenție"],
           "Două proiecte pot cere versiuni diferite ale aceleiași biblioteci. "
           "Fără medii separate, al doilea îl strică pe primul."))


# ===========================================================================
#  3-5. Ce este un API
# ===========================================================================

RESTAURANT = [
    ("Clientul", "codul tău",
     "Știe ce vrea, dar nu intră în bucătărie. Formulează o comandă și o dă mai departe."),
    ("Ospătarul", "API-ul",
     "Intermediarul. Preia comanda, o duce la bucătărie, aduce răspunsul înapoi. "
     "Nu gătește el, dar fără el nu ajungi la bucătărie."),
    ("Meniul", "documentația",
     "Ce se poate cere, cu ce opțiuni și în ce condiții. Dacă ceri ceva care nu e "
     "în meniu, primești un refuz, nu o surpriză."),
    ("Bucătăria", "serverul",
     "Acolo se întâmplă lucrul adevărat. Nu vezi cum, și nici nu te privește: "
     "te privește doar ce iese."),
    ("Preparatul", "răspunsul",
     "Ce primești înapoi, în forma convenită. La API, de cele mai multe ori, JSON."),
]

sl("s3", "Ce este un API", "Analogia restaurantului",
   "<h2>Analogia restaurantului</h2>"
   "<p class=\"cheie\">Un API e ospătarul. Nu gătește, dar fără el nu ajungi "
   "la bucătărie.</p>"
   + ix("flux", "Comanda, de la masă la bucătărie",
        {"titlu": "Apasă „Trimite comanda”",
         "intro": "Sau apasă pe oricare dintre stații, ca să vezi cu ce se potrivește din cod.",
         "buton": "Trimite comanda",
         "dus": "comanda pleacă spre bucătărie",
         "intors": "preparatul se întoarce la masă",
         "gata": "gata: ai primit ce ai cerut, în forma convenită",
         "statii": [{"n": n, "et": u, "d": d, "ic": ic}
                    for (n, u, d), ic in zip(RESTAURANT, ["🙋", "🧑‍🍳", "📋", "🍳", "🍽"])]}),
   manual=
   "<h2>Analogia restaurantului</h2>"
   "<p>Analogia e veche și merită spusă o dată, pentru că fixează un lucru care "
   "altfel se învață greu: tu nu vorbești cu baza de date a celuilalt. Vorbești "
   "cu un intermediar care are voie să intre acolo, în numele tău, în niște "
   "condiții scrise dinainte.</p>"
   + ix("flux", "Comanda, de la masă la bucătărie",
        {"titlu": "Apasă „Trimite comanda”",
         "intro": "Sau apasă pe oricare dintre stații.",
         "buton": "Trimite comanda",
         "dus": "comanda pleacă spre bucătărie",
         "intors": "preparatul se întoarce la masă",
         "gata": "gata: ai primit ce ai cerut",
         "statii": [{"n": n, "et": u, "d": d, "ic": ic}
                    for (n, u, d), ic in zip(RESTAURANT, ["🙋", "🧑‍🍳", "📋", "🍳", "🍽"])]})
   + "<p>Analogia are și o limită, și e bine s-o știi: ospătarul e politicos, "
     "pe când API-ul nu. Dacă ceri greșit, nu-ți explică nimeni ce ai greșit; "
     "primești un număr și atât. De aceea citirea documentației nu e opțională.</p>")

sl("s4", "Ce este un API", "Verificare pe analogie",
   "<h2>Cine e cine</h2>"
   + verif("c2-v2", 2,
           "În analogia restaurantului, documentația API-ului este…",
           ["ospătarul", "bucătăria", "meniul", "preparatul"],
           "Meniul. Spune ce se poate cere și cu ce opțiuni. Un API fără "
           "documentație e un restaurant fără meniu: poți ghici, dar pierzi "
           "seara întrebând.")
   + verif("c2-v3", 0,
           "Și serverul?",
           ["bucătăria", "clientul", "meniul", "ospătarul"],
           "Bucătăria. Acolo se face treaba, și tocmai de aceea nu ai acces "
           "direct: ar fi și periculos, și inutil."))

sl("s5", "Ce este un API", "De ce nu descărcăm cu mâna",
   "<h2>De ce prin API</h2>"
   + tabel(["Cu mâna", "Prin API"], [
       ["cineva a apăsat Download, cândva", "o linie de cod, cu data în ea"],
       ["nu se știe ce filtre erau puse", "filtrele sunt în cerere, scrise"],
       ["refacerea cere același om", "refacerea cere o rulare"],
       ["actualizarea = totul de la capăt", "actualizarea = aceeași rulare"],
   ])
   + "<p class=\"cheie\">Diferența nu e comoditatea. E că al doilea drum se "
     "poate parcurge din nou.</p>"
   + verif("c2-v4", 1,
           "Care e argumentul cel mai serios pentru colectarea prin API?",
           ["E mai rapid",
            "Colectarea devine reproductibilă: altcineva o poate reface identic",
            "Datele sunt mai corecte",
            "Nu trebuie citită documentația"],
           "Reproductibilitatea. Datele nu devin mai corecte pentru că vin "
           "prin API; devine însă verificabil de unde vin și cum au fost "
           "filtrate, ceea ce e condiția ca cineva să te poată crede."),
   manual=
   "<h2>De ce prin API și nu cu mâna</h2>"
   "<p>Întrebarea apare mereu, și pe bună dreptate: dacă fișierul e acolo, de "
   "ce să scriu cod ca să-l aduc?</p>"
   + tabel(["Cu mâna", "Prin API"], [
       ["cineva a apăsat Download, cândva", "o linie de cod, cu data în ea"],
       ["nu se știe ce filtre erau puse", "filtrele sunt în cerere, scrise"],
       ["refacerea cere același om", "refacerea cere o rulare"],
       ["actualizarea = totul de la capăt", "actualizarea = aceeași rulare"],
   ])
   + "<p>Răspunsul scurt: pentru că peste trei luni, când un recenzent te "
     "întreabă de unde ai luat cifra aia, vrei să poți arăta linia care a "
     "adus-o, nu să-ți amintești.</p>"
   + verif("c2-v4", 1,
           "Care e argumentul cel mai serios pentru colectarea prin API?",
           ["E mai rapid",
            "Colectarea devine reproductibilă: altcineva o poate reface identic",
            "Datele sunt mai corecte",
            "Nu trebuie citită documentația"],
           "Reproductibilitatea."))


# ===========================================================================
#  6-9. Tipuri de API
# ===========================================================================

TIPURI_API = [
    {"nume": "API-uri web", "copii": [
        {"nume": "REST", "text": "Cel mai răspândit pentru API-uri publice. Resurse la adrese, metode HTTP."},
        {"nume": "GraphQL", "text": "O singură adresă, iar clientul spune exact ce câmpuri vrea."},
        {"nume": "gRPC", "text": "Rapid și strâns tipizat. Între servicii, rar expus publicului."},
        {"nume": "SOAP", "text": "Vechi, cu plic XML. Încă viu în bănci și administrație."}]},
    {"nume": "După cine are acces", "copii": [
        {"nume": "Public / Open", "text": "Oricine, uneori cu o cheie gratuită. Banca Mondială, Eurostat."},
        {"nume": "Partner", "text": "Doar pentru parteneri, cu contract."},
        {"nume": "Privat / intern", "text": "Doar înăuntrul organizației."}]},
    {"nume": "Orientate pe evenimente", "copii": [
        {"nume": "Webhooks", "text": "Nu ceri tu; te sună el când s-a întâmplat ceva."},
        {"nume": "Streaming", "text": "Un flux continuu, nu o cerere și un răspuns."},
        {"nume": "WebSockets, SSE", "text": "Legătură deschisă, în timp real."}]},
    {"nume": "Specializate", "copii": [
        {"nume": "Baze de date", "text": "PostgreSQL, MongoDB."},
        {"nume": "Cloud", "text": "Azure, AWS."},
        {"nume": "AI / ML", "text": "OpenAI, HuggingFace."},
        {"nume": "IoT", "text": "Senzori, case inteligente."}]},
    {"nume": "Comerciale", "copii": [
        {"nume": "Plăți", "text": "Stripe."},
        {"nume": "Comerț", "text": "Shopify."},
        {"nume": "Rețele sociale", "text": "YouTube Data API."}]},
]

sl("s6", "Tipuri de API", "Ce fel de API-uri există",
   "<h2>Tipuri de API</h2>"
   "<p>Clasificările sunt multe pentru că se taie după criterii diferite: "
   "după protocol, după cine are acces, după cine pornește conversația.</p>"
   + ix("arbore", "Harta tipurilor",
        {"titlu": "Tipuri de API", "intro": "Apasă pe orice ramură.",
         "ramuri": TIPURI_API},
        "Nouă ne trebuie o singură ramură: REST, public. Restul, ca să știi "
        "ce vezi când dai peste altceva."),
   manual=
   "<h2>Tipuri de API</h2>"
   "<p>Nu trebuie să le știi pe toate. Trebuie să știi că există mai multe "
   "feluri, ca să nu te blochezi când documentația unui serviciu arată cu "
   "totul altfel decât te aștepți.</p>"
   + ix("arbore", "Harta tipurilor",
        {"titlu": "Tipuri de API", "intro": "Apasă pe orice ramură.",
         "ramuri": TIPURI_API})
   + "<p>La curs folosim exclusiv REST public: adrese pe care le poți deschide "
     "și în browser, fără cheie, cu răspuns în JSON.</p>")

CRONOLOGIE = [
    ("1991 · CORBA", "obiecte la distanță", "Apeluri între obiecte pe mașini diferite. Greu, dar a pus întrebarea."),
    ("1993 · RDA", "acces la date", "Standard pentru acces la distanță la baze de date."),
    ("1998 · XML-RPC", "apeluri în XML", "Prima formă simplă: un apel de funcție, împachetat în XML."),
    ("1999 · SOAP", "plicul", "XML-RPC cu reguli stricte și un plic în jur. Mult standard, mult ceremonial."),
    ("2000 · REST", "resurse", "Teza lui Roy Fielding. Nu un protocol, un stil: resurse la adrese, metode HTTP."),
    ("2005 · JSON-RPC", "mai ușor", "Același apel, dar în JSON, care e mult mai ușor de citit."),
    ("2007 · OData", "interogări", "REST cu interogări standardizate peste el."),
    ("2015 · GraphQL", "ceri ce-ți trebuie", "Facebook. O adresă, iar clientul descrie forma răspunsului."),
    ("2016 · gRPC", "între servicii", "Google. Binar, rapid, pentru comunicarea dintre servicii."),
]

sl("s7", "Tipuri de API", "De unde vine REST",
   "<h2>Un sfert de secol de încercări</h2>"
   "<p>REST n-a fost inventat ca să fie modern. A fost descris ca să "
   "simplifice ce exista deja și era greoi.</p>"
   + ix("cronologie", "Un sfert de secol de încercări",
        {"titlu": "Apasă pe oricare an",
         "intro": "Se vede ritmul: patru încercări în primii zece ani, apoi "
                  "liniște, apoi încă două.",
         "puncte": [{"an": int(n.split(" · ")[0]), "nume": n.split(" · ")[1],
                     "et": u, "text": d} for n, u, d in CRONOLOGIE]},
        "Ce supraviețuiește nu e ce e mai puternic, ci ce e mai ușor de citit "
        "de un om obosit."))

sl("s8", "Tipuri de API", "REST, SOAP, GraphQL, gRPC",
   "<h2>Patru stiluri, față în față</h2>"
   + tabel(["", "RPC", "SOAP", "REST", "GraphQL"], [
       ["organizat în jur de", "apel de funcție", "plic de mesaj", "resurse", "schemă și tipuri"],
       ["format", "~JSON, XML, Protobuf", "~doar XML", "~JSON, XML, text", "~JSON"],
       ["cât de greu se învață", "ușor", "greu", "ușor", "mediu"],
       ["comunitate", "mare", "mică", "mare", "în creștere"],
       ["unde apare", "între servicii interne", "bănci, administrație", "API-uri publice", "aplicații mobile"],
   ])
   + verif("c2-v5", 2,
           "Pentru un API public, simplu, pe care îl folosesc mulți necunoscuți, "
           "ce stil alegi?",
           ["SOAP, pentru că e standardizat",
            "gRPC, pentru că e rapid",
            "REST, pentru că e ușor de învățat și merge din browser",
            "GraphQL, pentru că e cel mai nou"],
           "REST. Un API public trăiește din cât de repede îl poate încerca un "
           "străin. O adresă pe care o deschizi în browser și vezi JSON e cea "
           "mai scurtă cale. gRPC e mai rapid, dar nu se încearcă din bara de "
           "adrese; SOAP e standardizat, dar costă o zi doar ca să faci prima "
           "cerere."))


# ===========================================================================
#  10-13. Cum arată o cerere
# ===========================================================================

sl("s9", "Cum arată o cerere", "Arhitectura REST",
   "<h2>Cerere, metodă, răspuns</h2>"
   "<p class=\"cheie\">Clientul trimite o cerere. Serverul trimite un răspuns. "
   "Între ele, o metodă HTTP care spune ce vrei să se întâmple.</p>"
   + ix("flux", "Aceeași drumeție, în cod",
        {"titlu": "Apasă „Trimite cererea”",
         "intro": "Exact stațiile de la restaurant, cu alte nume.",
         "buton": "Trimite cererea",
         "dus": "cererea pleacă: metodă, adresă, parametri",
         "intors": "răspunsul se întoarce: cod, antete, corp",
         "gata": "ai codul de stare și corpul, de obicei JSON",
         "statii": [
             {"n": "Codul tău", "et": "client", "ic": "💻",
              "d": "Construiește cererea: metoda, adresa, parametrii, antetele."},
             {"n": "Internetul", "et": "HTTP", "ic": "🌐",
              "d": "Cererea călătorește. Dacă pică aici, primești o eroare de rețea, nu un cod de stare."},
             {"n": "Serverul", "et": "API", "ic": "🖥",
              "d": "Primește cererea, verifică dacă are sens, caută resursa, aplică filtrele."},
             {"n": "Baza de date", "et": "resursa", "ic": "🗄",
              "d": "Acolo stau datele propriu-zise. Tu nu ajungi niciodată aici direct."}]})
   + nota("De ce poți relua o colectare căzută",
          "Nimic nu rămâne deschis între două cereri: fiecare cerere poartă cu "
          "ea tot ce-i trebuie. De aceea a treia cerere merge și dacă primele "
          "două s-au făcut ieri, de pe alt calculator."),
   manual=
   "<h2>Arhitectura REST</h2>"
   "<p>REST nu e un protocol, ci un set de constrângeri peste HTTP. Dintre "
   "ele, una contează pentru tine de la prima zi: fiecare cerere e "
   "independentă. Serverul nu ține minte că ai mai întrebat ceva acum o "
   "secundă.</p>"
   + tabel(["Pleacă de la tine", "Ajunge la server", "Se întoarce"], [
       ["metoda și adresa", "serverul caută resursa", "un cod de stare"],
       ["parametrii", "aplică filtrele", "antetele"],
       ["antetele", "pregătește răspunsul", "corpul, de obicei JSON"],
   ])
   + "<p>Consecința practică e bună pentru noi: dacă o colectare cade la "
     "jumătate, o poți relua de unde a rămas, fără să refaci tot.</p>")

sl("s10", "Cum arată o cerere", "Metodele HTTP",
   "<h2>Cinci metode, patru operații</h2>"
   "<p>Metoda spune ce vrei să se întâmple cu resursa. Noi vom folosi aproape "
   "numai una.</p>"
   + ix("sortare", "Metodă și operație",
        {"id": "c2-sort-metode",
         "sarcina": "Pune fiecare metodă HTTP în dreptul operației pe care o face.",
         "elemente": [{"t": "GET", "cos": 0}, {"t": "POST", "cos": 1},
                      {"t": "PUT", "cos": 2}, {"t": "PATCH", "cos": 2},
                      {"t": "DELETE", "cos": 3}],
         "cosuri": [{"t": "Citește", "d": "nu schimbă nimic"},
                    {"t": "Creează", "d": "adaugă ceva nou"},
                    {"t": "Modifică", "d": "schimbă ce există"},
                    {"t": "Șterge", "d": "scoate definitiv"}],
         "laBine": "La colectarea de date folosești GET în 99% din cazuri. "
                   "Celelalte apar când scrii undeva, nu când citești.",
         "explicatie": "PUT înlocuiește toată resursa, PATCH doar o bucată din "
                       "ea. Diferența contează când scrii; la citit, nu."}),
   manual=
   "<h2>Metodele HTTP și CRUD</h2>"
   "<p>Cele patru operații pe care le poți face cu orice colecție de date se "
   "numesc, pe scurt, CRUD: create, read, update, delete. HTTP le dă câte o "
   "metodă.</p>"
   + ix("sortare", "Metodă și operație",
        {"id": "c2-sort-metode",
         "sarcina": "Pune fiecare metodă HTTP în dreptul operației pe care o face.",
         "elemente": [{"t": "GET", "cos": 0}, {"t": "POST", "cos": 1},
                      {"t": "PUT", "cos": 2}, {"t": "PATCH", "cos": 2},
                      {"t": "DELETE", "cos": 3}],
         "cosuri": [{"t": "Citește", "d": "nu schimbă nimic"},
                    {"t": "Creează", "d": "adaugă ceva nou"},
                    {"t": "Modifică", "d": "schimbă ce există"},
                    {"t": "Șterge", "d": "scoate definitiv"}],
         "laBine": "La colectarea de date folosești GET în 99% din cazuri.",
         "explicatie": "PUT înlocuiește toată resursa, PATCH doar o bucată."})
   + nota("Proprietatea care te salvează",
          "<code>GET</code> e <em>sigur</em>: oricâte ori l-ai repeta, nu "
          "schimbă nimic pe server. De aceea o colectare căzută se poate "
          "relua fără teamă. Cu <code>POST</code> nu e așa: de două ori "
          "înseamnă de două ori."))

sl("s11", "Cum arată o cerere", "Endpoint-ul",
   "<h2>Ce este un endpoint</h2>"
   "<p class=\"cheie\">Adresa la care ceri un anumit lucru. Fiecare endpoint "
   "dă altceva.</p>"
   "<pre><code>https://api.worldbank.org/v2/country/RO/indicator/SP.POP.TOTL</code></pre>"
   "<p>Un API nu are o singură adresă, are zeci. Documentația e lista lor.</p>"
   + verif("c2-v6", 1,
           "Două endpoint-uri diferite ale aceluiași API…",
           ["întorc aceleași date, în formate diferite",
            "întorc lucruri diferite: fiecare e o altă resursă sau funcție",
            "sunt același lucru, scris în două feluri",
            "se folosesc pe rând, în ordine"],
           "Fiecare endpoint e o altă resursă. Ca în meniu: la „supe” scrie "
           "altceva decât la „deserturi”."))

sl("s12", "Cum arată o cerere", "Structura unei adrese",
   "<h2>Din ce e făcută o adresă</h2>"
   "<p>Cinci bucăți, fiecare cu rostul ei. Pe asta se sprijină tot ce scriem "
   "mai jos.</p>"
   + ix("url", "Taie adresa în bucăți",
        {"id": "c2-url",
         "url": "https://api.exemplu.com:443/resursa/detalii?culoare=rosu#sectiune",
         "parti": [
             {"t": "https", "e": "protocol",
              "d": "Cum se vorbește. <code>https</code> e criptat, <code>http</code> nu."},
             {"t": "api.exemplu.com", "e": "host",
              "d": "Ce server. Numele mașinii care răspunde."},
             {"t": "443", "e": "port",
              "d": "Pe ce ușă. Se scrie rar: 443 pentru https și 80 pentru http se subînțeleg."},
             {"t": "/resursa/detalii", "e": "cale",
              "d": "Ce resursă ceri. Aici se vede ce anume vrei din tot ce oferă serverul."},
             {"t": "?culoare=rosu", "e": "parametri",
              "d": "Opțiuni: filtre, format, pagină. Aici ajung argumentele tale."},
             {"t": "#sectiune", "e": "fragment",
              "d": "Pentru browser, nu pentru server. Nu pleacă în cerere."}],
         "etichete": ["protocol", "host", "port", "cale", "parametri", "fragment"],
         "explicatie": "Fragmentul e singurul care nu ajunge niciodată la "
                       "server: browserul îl folosește ca să sară la o bucată "
                       "din pagină. Dacă pui ceva important după <code>#</code>, "
                       "nu se trimite."}),
   manual=
   "<h2>Structura unui endpoint</h2>"
   "<p>O adresă pare un șir de caractere, dar are o gramatică. Când o cerere "
   "nu merge, aproape întotdeauna greșeala e într-una dintre bucățile astea, "
   "și e util să le poți numi.</p>"
   + ix("url", "Taie adresa în bucăți",
        {"id": "c2-url",
         "url": "https://api.exemplu.com:443/resursa/detalii?culoare=rosu#sectiune",
         "parti": [
             {"t": "https", "e": "protocol", "d": "Cum se vorbește."},
             {"t": "api.exemplu.com", "e": "host", "d": "Ce server răspunde."},
             {"t": "443", "e": "port", "d": "Pe ce ușă. De obicei se subînțelege."},
             {"t": "/resursa/detalii", "e": "cale", "d": "Ce resursă ceri."},
             {"t": "?culoare=rosu", "e": "parametri", "d": "Filtre și opțiuni."},
             {"t": "#sectiune", "e": "fragment", "d": "Pentru browser, nu pentru server."}],
         "etichete": ["protocol", "host", "port", "cale", "parametri", "fragment"],
         "explicatie": "Fragmentul nu ajunge niciodată la server."})
   + verif("c2-v7", 2,
           "Unde pui filtrele unei cereri, de exemplu anul sau formatul?",
           ["în protocol", "în host", "în parametri, după semnul întrebării",
            "în fragment, după diez"],
           "În parametri. Fragmentul, de după <code>#</code>, nici măcar nu "
           "pleacă spre server: rămâne la browser."))


# ===========================================================================
#  14-15. Răspunsul
# ===========================================================================

sl("s13", "Răspunsul", "Codurile de stare",
   "<h2>Ce îți răspunde serverul</h2>"
   "<p>Înainte de date, vine un număr. Dacă nu te uiți la el, vei petrece "
   "jumătate de oră întrebându-te de ce tabelul e gol.</p>"
   + ix("raspuns", "Trimite și vezi ce primești",
        {"id": "c2-raspuns",
         "sarcina": "Încearcă-le pe toate. Fiecare e o greșeală pe care o vei face.",
         "cazuri": [
             {"et": "cerere bună", "cod": 200, "nume": "OK",
              "url": "api.worldbank.org/v2/country/RO/indicator/SP.POP.TOTL?format=json",
              "corp": "[{\"page\":1,\"pages\":2,\"total\":64}, [ … 50 de randuri … ]]",
              "ce": "A mers. Dar uită-te și la ce e înăuntru: un <code>200</code> "
                    "cu zero rânduri tot <code>200</code> se cheamă."},
             {"et": "adresa greșită", "cod": 404, "nume": "Not Found",
              "url": "api.worldbank.org/v2/country/RO/indicatorr/SP.POP.TOTL?format=json",
              "corp": "<html><head><title>404</title></head> …",
              "ce": "Calea nu există. Observă și că răspunsul nu mai e JSON, ci "
                    "HTML: dacă dai direct <code>r.json()</code>, crapă acolo, "
                    "nu la adresă, și cauți în locul greșit."},
             {"et": "parametru aiurea", "cod": 400, "nume": "Bad Request",
              "url": "api.worldbank.org/v2/country/RO/indicator/SP.POP.TOTL?format=json&date=anul-trecut",
              "corp": "[{\"message\":[{\"id\":\"120\",\"value\":\"Invalid value\"}]}]",
              "ce": "Cererea a ajuns și a fost înțeleasă, dar e greșită. "
                    "Greșeala e la tine, și de obicei scrie în corp care anume."},
             {"et": "prea des", "cod": 429, "nume": "Too Many Requests",
              "url": "api.worldbank.org/v2/country/RO/indicator/SP.POP.TOTL?page=97",
              "corp": "Retry-After: 30",
              "ce": "Ai depășit limita. Soluția nu e să reîncerci mai des, ci "
                    "mai rar: o pauză între cereri, care crește după fiecare refuz."},
             {"et": "a crăpat la ei", "cod": 503, "nume": "Service Unavailable",
              "url": "api.worldbank.org/v2/country/RO/indicator/SP.POP.TOTL?format=json",
              "corp": "Service temporarily unavailable",
              "ce": "Nu e vina ta. Reiei mai târziu. Un script bun de colectare "
                    "reîncearcă singur, de câteva ori, cu pauze tot mai mari."}]})
   + verif("c2-v8", 3,
           "Primești codul <code>429</code>. Ce s-a întâmplat?",
           ["Adresa e greșită",
            "Serverul e stricat",
            "Nu ai cheie de acces",
            "Ai trimis prea multe cereri prea repede"],
           "429 înseamnă „ai depășit limita”. Soluția nu e să reîncerci mai "
           "des, ci mai rar: o pauză între cereri, iar la colectări mari, o "
           "pauză care crește după fiecare refuz."),
   manual=
   "<h2>Codurile de stare</h2>"
   "<p>Prezentarea de la curs nu le avea, dar fără ele prima cerere care "
   "eșuează pare o pană de internet. Primul lucru pe care îl faci după orice "
   "cerere e să te uiți la cod.</p>"
   + tabel(["Cod", "Ce înseamnă", "Ce faci"], [
       ["~200", "a mers", "citești datele"],
       ["~400", "cererea ta e greșită", "verifici parametrii"],
       ["~401 / 403", "nu ai voie", "cheie lipsă sau greșită"],
       ["~404", "adresa nu există", "verifici calea, nu internetul"],
       ["~429", "prea multe cereri", "aștepți și reiei mai rar"],
       ["~500", "a crăpat la ei", "reiei mai târziu"],
   ])
   + nota("Greșeala clasică",
          "Un răspuns cu codul <code>200</code> poate conține zero rânduri. "
          "„A mers” înseamnă că întrebarea a fost înțeleasă, nu că există un "
          "răspuns. Deci verifici și codul, și câte rânduri ai primit.")
   + verif("c2-v8", 3,
           "Primești codul <code>429</code>. Ce s-a întâmplat?",
           ["Adresa e greșită", "Serverul e stricat", "Nu ai cheie de acces",
            "Ai trimis prea multe cereri prea repede"],
           "429 înseamnă „ai depășit limita”."))


# ===========================================================================
#  16-17. Surse de date
# ===========================================================================

SURSE = [
    ("Baze de date", "PostgreSQL, MongoDB", "Le vom folosi la cursul 5, prin Neon."),
    ("Servicii externe", "vreme, cursuri valutare", "Clasicul exemplu de API public."),
    ("Stocare în cloud", "Azure Blob, AWS S3", "Fișiere mari, ținute în altă parte."),
    ("Rețele sociale", "YouTube Data API", "Cu limite stricte și cheie."),
    ("Procesatori de plăți", "Stripe", "Nu ne privește la curs, dar e același mecanism."),
    ("Senzori, IoT", "case inteligente", "Flux continuu, nu cerere și răspuns."),
    ("Pagini web", "HTML de parcurs", "Când nu există API. Ultima soluție, și cea mai fragilă."),
    ("Date publice", "data.gov, INS, Eurostat", "Sursa noastră principală."),
    ("Servicii financiare", "AlphaVantage, Yahoo Finance", "Serii de timp, gratuite până la o limită."),
    ("Comerț", "Shopify", "Date de vânzări, pentru cine lucrează cu firme."),
    ("Hărți și locație", "OpenStreetMap, Nominatim", "Geocodare: de la adresă la coordonate."),
    ("Servicii AI", "OpenAI, HuggingFace", "Tot un API, cu aceleași reguli."),
]

sl("s14", "Surse de date", "De unde se pot lua date",
   "<h2>Surse accesibile prin API</h2>"
   + ix("etape", "Douăsprezece feluri de surse",
        {"titlu": "Surse de date", "intro": "Apasă pe oricare.",
         "etape": [{"nume": n, "unde": u, "text": d} for n, u, d in SURSE]},
        "Pentru proiectul nostru, două dintre ele contează.")
   + "<p class=\"cheie\">Noi folosim date publice. Fără cheie, fără cont, "
     "fără limite care să ne oprească la oră.</p>")

sl("s15", "Surse de date", "Ce folosim noi",
   "<h2>Sursele proiectului</h2>"
   + tabel(["Sursa", "Cum vine", "Ce ne dă"], [
       ["Social Connectedness Index", "fișier descărcat", "legăturile dintre locuri; e deja la voi"],
       ["Banca Mondială", "~API REST public", "indicatori pe țară și an"],
       ["Eurostat", "~API REST public", "indicatori pe regiuni NUTS"],
       ["INS Tempo", "~API", "date despre România, mai greu de citit"],
   ])
   + "<p>Azi lucrăm cu Banca Mondială, pentru că nu cere nimic și răspunde "
     "imediat. Eurostat vine la seminar.</p>"
   + verif("c2-v9", 1,
           "Fișierul SCI de la cursul 1 e o sursă prin API?",
           ["Da, orice sursă de date e un API",
            "Nu, e un fișier descărcat; API-ul e un serviciu pe care îl întrebi",
            "Da, pentru că l-am luat de pe internet",
            "Depinde de format"],
           "Un fișier descărcat e un fișier. Diferența nu e unde stă, ci dacă "
           "îl poți întreba: un API răspunde la cereri, cu parametri, de "
           "fiecare dată."))


# ===========================================================================
#  18-21. requests
# ===========================================================================

sl("s16", "requests", "Prima cerere",
   "<h2>requests: prima cerere</h2>"
   "<p>O bibliotecă mică, cu reputația de a fi cea mai plăcut de folosit din "
   "tot Python-ul. Trei linii și ai datele.</p>"
   + ix("cod", "Scrie cererea", {
       "id": "c2-cod-prima", "fisier": "prima_cerere.py",
       "sarcina": "Completează metoda, verificarea codului de stare și "
                  "transformarea răspunsului în date Python.",
       "cod": "import requests\n\n"
              "url = \"https://api.worldbank.org/v2/country/RO/indicator/SP.POP.TOTL\"\n\n"
              "# metoda prin care se citeste, fara sa se schimbe nimic\n"
              "r = requests.{{1}}(url, params={\"format\": \"json\"}, timeout=30)\n\n"
              "# primul lucru dupa orice cerere: codul de stare\n"
              "print(r.{{2}})            # 200\n\n"
              "# corpul raspunsului, din text JSON in liste si dictionare\n"
              "date = r.{{3}}()\n"
              "print(len(date))            # 2",
       "goluri": {
           "1": {"ok": ["get"], "ajutor": "metoda"},
           "2": {"ok": ["status_code"], "ajutor": "atributul"},
           "3": {"ok": ["json"], "ajutor": "metoda"}},
       "laBine": "Astea trei linii sunt tot ce-ți trebuie pentru nouă zecimi "
                 "din colectările de la curs.",
       "laRau": "Nu pune ghilimele: se cer un nume de metodă și un atribut, nu text.",
       "explicatie": "<code>requests.get</code> trimite cererea. "
                     "<code>r.status_code</code> e numărul despre care am vorbit. "
                     "<code>r.json()</code> traduce textul primit în liste și "
                     "dicționare. Dacă răspunsul nu e JSON valid, aici crapă, "
                     "ceea ce e bine: afli imediat, nu peste trei pași."}),
   manual=
   "<h2>requests</h2>"
   "<p>Se instalează în mediul virtual, o singură dată:</p>"
   "<pre><code>pip install requests</code></pre>"
   "<p>Și apoi se folosește așa. Reține ordinea: ceri, verifici codul, abia pe "
   "urmă te uiți la date.</p>"
   + ix("cod", "Scrie cererea", {
       "id": "c2-cod-prima", "fisier": "prima_cerere.py",
       "sarcina": "Completează metoda, verificarea codului de stare și "
                  "transformarea răspunsului în date Python.",
       "cod": "import requests\n\n"
              "url = \"https://api.worldbank.org/v2/country/RO/indicator/SP.POP.TOTL\"\n\n"
              "# metoda prin care se citeste, fara sa se schimbe nimic\n"
              "r = requests.{{1}}(url, params={\"format\": \"json\"}, timeout=30)\n\n"
              "# primul lucru dupa orice cerere: codul de stare\n"
              "print(r.{{2}})            # 200\n\n"
              "# corpul raspunsului, din text JSON in liste si dictionare\n"
              "date = r.{{3}}()\n"
              "print(len(date))            # 2",
       "goluri": {
           "1": {"ok": ["get"], "ajutor": "metoda"},
           "2": {"ok": ["status_code"], "ajutor": "atributul"},
           "3": {"ok": ["json"], "ajutor": "metoda"}},
       "laBine": "Astea trei linii sunt tot ce-ți trebuie pentru nouă zecimi "
                 "din colectările de la curs.",
       "laRau": "Nu pune ghilimele: se cer un nume de metodă și un atribut.",
       "explicatie": "<code>r.json()</code> traduce textul primit în liste și "
                     "dicționare."})
   + nota("timeout",
          "<code>timeout=30</code> nu e decorativ. Fără el, o cerere către un "
          "server care nu răspunde blochează programul la nesfârșit, iar la o "
          "colectare de o mie de cereri asta înseamnă un script care pare "
          "pornit toată noaptea și n-a făcut nimic."))

sl("s17", "requests", "Parametrii se dau separat",
   "<h2>Nu lipi parametrii în adresă</h2>"
   "<p>Tentația e să construiești adresa cu <code>+</code>. Nu face asta: "
   "spațiile, diacriticele și semnele speciale strică adresa fără să-ți spună.</p>"
   + ix("cod", "Pune parametrii cum trebuie", {
       "id": "c2-cod-param", "fisier": "parametri.py",
       "sarcina": "Mută filtrele din adresă în dicționarul de parametri.",
       "cod": "import requests\n\n"
              "baza = \"https://api.worldbank.org/v2/country/RO/indicator/SP.POP.TOTL\"\n\n"
              "# anii si formatul nu se lipesc in adresa, se dau separat\n"
              "p = {\n"
              "    \"format\": \"json\",\n"
              "    \"date\": {{1}},\n"
              "    \"per_page\": {{2}},\n"
              "}\n\n"
              "r = requests.get(baza, {{3}}=p, timeout=30)\n"
              "print(r.url)",
       "goluri": {
           "1": {"ok": ["\"2000:2023\"", "'2000:2023'"], "ajutor": "intervalul"},
           "2": {"ok": ["100", "\"100\"", "'100'"], "ajutor": "numărul"},
           "3": {"ok": ["params"], "ajutor": "argumentul"}},
       "laBine": "<code>r.url</code> îți arată adresa construită de bibliotecă, "
                 "cu tot ce a codificat ea. E cel mai rapid fel de a verifica "
                 "ce ai cerut de fapt.",
       "laRau": "Intervalul de ani e text, între ghilimele. Argumentul funcției nu e.",
       "explicatie": "Biblioteca codifică singură ce trebuie codificat: spații, "
                     "diacritice, semne. Dacă lipești adresa cu mâna, o faci tu, "
                     "și o vei uita exact la parametrul care conține o virgulă."}),
   manual=
   "<h2>Parametrii</h2>"
   "<p>Tot ce ține de filtrare merge în <code>params</code>, nu în șirul "
   "adresei. Două motive: codificarea se face singură, și adresa rămâne "
   "lizibilă atunci când o citești peste o lună.</p>"
   + ix("cod", "Pune parametrii cum trebuie", {
       "id": "c2-cod-param", "fisier": "parametri.py",
       "sarcina": "Mută filtrele din adresă în dicționarul de parametri.",
       "cod": "import requests\n\n"
              "baza = \"https://api.worldbank.org/v2/country/RO/indicator/SP.POP.TOTL\"\n\n"
              "# anii si formatul nu se lipesc in adresa, se dau separat\n"
              "p = {\n"
              "    \"format\": \"json\",\n"
              "    \"date\": {{1}},\n"
              "    \"per_page\": {{2}},\n"
              "}\n\n"
              "r = requests.get(baza, {{3}}=p, timeout=30)\n"
              "print(r.url)",
       "goluri": {
           "1": {"ok": ["\"2000:2023\"", "'2000:2023'"], "ajutor": "intervalul"},
           "2": {"ok": ["100", "\"100\"", "'100'"], "ajutor": "numărul"},
           "3": {"ok": ["params"], "ajutor": "argumentul"}},
       "laBine": "<code>r.url</code> îți arată adresa construită de bibliotecă.",
       "laRau": "Intervalul de ani e text, între ghilimele.",
       "explicatie": "Biblioteca codifică singură ce trebuie codificat."}))

sl("s18", "requests", "Paginarea",
   "<h2>Răspunsul vine pe pagini</h2>"
   "<p>Niciun API serios nu-ți dă zece mii de rânduri dintr-o dată. Îți dă o "
   "pagină și îți spune câte mai sunt.</p>"
   "<pre><code><span class=\"c\"># primul element al raspunsului, la Banca Mondiala</span>\n"
   "{\"page\": 1, \"pages\": 2, \"per_page\": 50, \"total\": 64}</code></pre>"
   + ix("ordine", "Bucla de colectare", {
       "id": "c2-ordine-paginare",
       "sarcina": "Pune pașii unei colectări paginate în ordine.",
       "linii": [
           "pagina = 1; tot = []",
           "r = requests.get(url, params={**p, \"page\": pagina}, timeout=30)",
           "if r.status_code != 200: break",
           "cap, date = r.json()",
           "tot.extend(date)",
           "if pagina >= cap[\"pages\"]: break",
           "pagina += 1; time.sleep(0.5)"],
       "explicatie": "Verificarea codului vine înaintea citirii datelor, iar "
                     "pauza la final e politețea care te ține sub limita de "
                     "cereri. Fără <code>sleep</code>, o buclă de o sută de "
                     "pagini ajunge la 429 în câteva secunde."})
   + verif("c2-v10", 0,
           "De ce pui o pauză între cereri, într-o buclă de colectare?",
           ["Ca să nu depășesc limita de cereri a serverului",
            "Ca să am timp să citesc rezultatele",
            "Ca să consume mai puțină memorie",
            "Nu e nevoie, serverul se descurcă"],
           "Ca să rămâi sub limită. O pauză de jumătate de secundă nu te costă "
           "nimic la o sută de pagini, dar te scutește de a fi blocat temporar."))

sl("s19", "requests", "Din JSON în tabel",
   "<h2>Ultimul pas: un tabel</h2>"
   "<p>Răspunsul e o structură cu mai multe niveluri. Analiza vrea rânduri și "
   "coloane.</p>"
   + ix("cod", "Fă tabelul", {
       "id": "c2-cod-tabel", "fisier": "in_tabel.py",
       "sarcina": "Transformă lista de înregistrări într-un tabel și salvează-l.",
       "cod": "import pandas as pd\n\n"
              "# `date` e lista de inregistrari din raspuns\n"
              "d = pd.{{1}}(date)\n\n"
              "# structurile incuibate devin coloane separate\n"
              "d = pd.json_normalize(date)\n"
              "print(d.columns.tolist())\n\n"
              "# il salvam ca sa nu mai cerem de doua ori acelasi lucru\n"
              "d.to_csv(\"date/brute/populatie_ro.csv\", index={{2}})",
       "goluri": {
           "1": {"ok": ["DataFrame"], "ajutor": "constructorul"},
           "2": {"ok": ["False"], "ajutor": "valoarea"}},
       "laBine": "De aici încolo e pandas, adică teren cunoscut de la cursul 1.",
       "laRau": "Numele constructorului se scrie cu majuscule unde trebuie. "
                "La index, răspunsul e una dintre cele două valori logice.",
       "explicatie": "<code>json_normalize</code> desface dicționarele "
                     "încuibate în coloane cu punct în nume, de tipul "
                     "<code>indicator.value</code>. <code>index=False</code> "
                     "împiedică pandas să adauge o coloană de numerotare care "
                     "nu înseamnă nimic și care încurcă la reîncărcare."})
   + nota("Salvează brutul, nu doar curățatul",
          "Fișierul din <code>date/brute/</code> se scrie o dată și nu se mai "
          "atinge. Curățarea lucrează pe o copie. Altfel, peste două "
          "săptămâni, nu mai știi ce ai schimbat și nu te mai poți întoarce."))


# ===========================================================================
#  22. Postman
# ===========================================================================

sl("s20", "Postman", "Aceeași cerere, cu mâna",
   "<h2>Postman</h2>"
   "<p>Înainte de a scrie cod, merită să faci cererea într-un loc unde vezi "
   "tot: adresa, parametrii, antetele, codul de stare și corpul răspunsului.</p>"
   + tabel(["În Postman", "Ce vezi"], [
       ["metoda și adresa", "ce ceri"],
       ["tabul Params", "parametrii, pe rânduri, ușor de modificat"],
       ["butonul Send", "codul de stare și cât a durat"],
       ["panoul de jos", "JSON-ul, pliat pe niveluri"],
   ])
   + "<p>Când cererea merge acolo, o treci în cod. Când nu merge în cod, te "
     "întorci acolo ca să vezi care bucată diferă.</p>"
   + ix("dovada", "Arată că ți-a mers", {
       "id": "c2-dovada-postman",
       "sarcina": "Fă în Postman cererea către Banca Mondială și lipește aici "
                  "prima linie a răspunsului, cea cu paginarea.",
       "pasi": [
           {"t": "Cererea a mers, iar răspunsul are paginare",
            "cmd": "GET https://api.worldbank.org/v2/country/RO/indicator/SP.POP.TOTL?format=json",
            "gol": "lipește prima linie a răspunsului",
            "cauta": r"\"?page\"?\s*:\s*1",
            "daca_nu": "Caut câmpul page cu valoarea 1, din primul element al "
                       "răspunsului. Îl vezi sus de tot în JSON-ul din Postman."}],
       "explicatie": "Dacă ai asta, ai făcut o cerere adevărată către un server "
                     "adevărat și ai citit răspunsul. Restul lecției e același "
                     "lucru, scris în Python."}))


# ===========================================================================
#  23-24. Proiectul
# ===========================================================================

sl("s21", "Proiectul tău", "Colectează, acum",
   "<h2>Prima colectare din proiect</h2>"
   "<p>Un script care cere, verifică, salvează. Rulează-l și lipește ce iese.</p>"
   + tabel(["Pasul", "Ce faci"], [
       ["1", "creezi <code>colectare/banca_mondiala.py</code> în depozit"],
       ["2", "ceri indicatorul pentru România, anii 2000–2023"],
       ["3", "verifici codul de stare și câte rânduri ai primit"],
       ["4", "salvezi în <code>date/brute/</code> și faci commit"],
   ])
   + ix("dovada", "Dovada colectării", {
       "id": "c2-dovada-colectare",
       "sarcina": "Lipește ce a tipărit scriptul tău: codul de stare și "
                  "numărul de rânduri salvate.",
       "pasi": [
           {"t": "Cererea a primit 200",
            "cmd": "python colectare/banca_mondiala.py",
            "gol": "lipește linia cu codul de stare",
            "cauta": r"\b200\b",
            "daca_nu": "Caut un 200. Dacă vezi 404, greșeala e în adresă; "
                       "dacă vezi 429, ai cerut prea des."},
           {"t": "Fișierul s-a scris, cu rânduri în el",
            "cmd": "python -c \"import pandas as pd; print(len(pd.read_csv('date/brute/populatie_ro.csv')))\"",
            "gol": "numărul de rânduri",
            "cauta": r"\b[1-9]\d{0,4}\b",
            "daca_nu": "Caut un număr mai mare ca zero. Zero rânduri înseamnă "
                       "că cererea a mers dar filtrul n-a lăsat nimic."},
           {"t": "Colectarea e în depozit",
            "cmd": "git log --oneline -1",
            "gol": "lipește linia",
            "cauta": r"[0-9a-f]{7}",
            "daca_nu": "Caut începutul unui hash de commit. Dacă n-ai niciunul, "
                       "mai întâi git add și git commit."}],
       "explicatie": "Trei lucruri care, împreună, înseamnă că datele sunt în "
                     "depozit și că se poate reface drumul până la ele."}),
   manual=
   "<h2>Prima colectare din proiect</h2>"
   "<p>Scriptul, întreg, ca să-l poți porni de la ceva și să-l schimbi pe "
   "indicatorul echipei tale:</p>"
   "<pre><code><span class=\"k\">import</span> time\n"
   "<span class=\"k\">import</span> pandas <span class=\"k\">as</span> pd\n"
   "<span class=\"k\">import</span> requests\n\n"
   "URL = <span class=\"s\">\"https://api.worldbank.org/v2/country/RO/indicator/SP.POP.TOTL\"</span>\n\n"
   "<span class=\"k\">def</span> adu(url, p):\n"
   "    pagina, tot = <span class=\"n\">1</span>, []\n"
   "    <span class=\"k\">while</span> <span class=\"k\">True</span>:\n"
   "        r = requests.get(url, params={**p, <span class=\"s\">\"page\"</span>: pagina}, timeout=<span class=\"n\">30</span>)\n"
   "        <span class=\"k\">if</span> r.status_code != <span class=\"n\">200</span>:\n"
   "            <span class=\"k\">print</span>(<span class=\"s\">\"a cazut la pagina\"</span>, pagina, r.status_code)\n"
   "            <span class=\"k\">break</span>\n"
   "        cap, date = r.json()\n"
   "        tot.extend(date <span class=\"k\">or</span> [])\n"
   "        <span class=\"k\">if</span> pagina >= cap[<span class=\"s\">\"pages\"</span>]:\n"
   "            <span class=\"k\">break</span>\n"
   "        pagina += <span class=\"n\">1</span>\n"
   "        time.sleep(<span class=\"n\">0.5</span>)\n"
   "    <span class=\"k\">return</span> tot\n\n"
   "randuri = adu(URL, {<span class=\"s\">\"format\"</span>: <span class=\"s\">\"json\"</span>, "
   "<span class=\"s\">\"date\"</span>: <span class=\"s\">\"2000:2023\"</span>, "
   "<span class=\"s\">\"per_page\"</span>: <span class=\"n\">100</span>})\n"
   "d = pd.json_normalize(randuri)\n"
   "d.to_csv(<span class=\"s\">\"date/brute/populatie_ro.csv\"</span>, index=<span class=\"k\">False</span>)\n"
   "<span class=\"k\">print</span>(<span class=\"s\">\"salvate\"</span>, len(d), <span class=\"s\">\"randuri\"</span>)</code></pre>"
   + nota("Ce nu urci în depozit",
          "Fișierele mari și cheile. Datele brute mici, de câțiva kilobytes, "
          "pot sta în depozit și e chiar util să stea. Cele de zeci de "
          "megabytes nu: pentru ele se urcă scriptul care le aduce.")
   + ix("dovada", "Dovada colectării", {
       "id": "c2-dovada-colectare",
       "sarcina": "Lipește ce a tipărit scriptul tău.",
       "pasi": [
           {"t": "Cererea a primit 200",
            "cmd": "python colectare/banca_mondiala.py",
            "gol": "lipește linia cu codul de stare",
            "cauta": r"\b200\b",
            "daca_nu": "Caut un 200. Dacă vezi 404, greșeala e în adresă; "
                       "dacă vezi 429, ai cerut prea des."},
           {"t": "Fișierul s-a scris, cu rânduri în el",
            "cmd": "python -c \"import pandas as pd; print(len(pd.read_csv('date/brute/populatie_ro.csv')))\"",
            "gol": "numărul de rânduri",
            "cauta": r"\b[1-9]\d{0,4}\b",
            "daca_nu": "Caut un număr mai mare ca zero. Zero rânduri înseamnă "
                       "că cererea a mers dar filtrul n-a lăsat nimic."},
           {"t": "Colectarea e în depozit",
            "cmd": "git log --oneline -1",
            "gol": "lipește linia",
            "cauta": r"[0-9a-f]{7}",
            "daca_nu": "Caut începutul unui hash de commit. Dacă n-ai niciunul, "
                       "mai întâi git add și git commit."}],
       "explicatie": "Datele sunt în depozit și drumul până la ele se poate reface."}))

sl("s22", "Mai departe", "Până data viitoare",
   "<h2>Cursul 3: versionare și colaborare</h2>"
   "<ul>"
   "<li>Git: istoric, reveniri, ramuri, pull request</li>"
   "<li>pregătirea și explorarea datelor colectate</li>"
   "<li>cadrul teoretic al proiectului</li>"
   "<li>tema echipei și cine ce face</li>"
   "</ul>"
   + nota("De făcut până atunci",
          "Scriptul de colectare, rulat și urcat în depozit. Plus o propunere "
          "de temă pentru echipă, în două-trei rânduri, în "
          "<code>README.md</code>.", True))


if __name__ == "__main__":
    L.scrie_tot()
