# -*- coding: utf-8 -*-
"""
Lecția 2: Colectarea datelor prin API.

Povestea lecției, aceeași pe slide-uri și în manual: de ce datele trebuie
aduse reproductibil, ce este un API (un contract), peisajul (tipuri, istorie,
stiluri), protocolul HTTP piesă cu piesă, de unde vin datele, aceeași cerere
în Python, un al doilea format (cubul Eurostat) și prima colectare în proiect.

Rolurile:
  - slide-urile predau conceptul, vizual, și verifică după ce l-au predat;
  - caietul 02 (02_colectarea_datelor_prin_api.ipynb) are codul complet;
  - manualul e capitolul de manual: conceptul, de ce contează în analiza
    datelor, codul minim, capcanele, sursele.

Cererea folosită în toată lecția e cea din caietul 02: populația României,
Banca Mondială, 2022 la 2024. Valorile vin din colectarea de referință
(data/colectari_c2/referinta_c2_20261013).

Rulare:  python _build/c2.py
"""

from comun import Lectie, ix, verif, tabel, nota, surse, REPO, REPO_ORG, repo_fisier

L = Lectie(2, "c2-colectarea-prin-api", "Colectarea datelor prin API",
           "Ce este un API, cum arată o cerere HTTP, cum se citește un răspuns "
           "și cum se aduc primele date reale în proiect.")
sl = L.sl

CAIET = "02_colectarea_datelor_prin_api.ipynb"
URL_BM = "https://api.worldbank.org/v2/country/RO/indicator/SP.POP.TOTL"


# ===========================================================================
#  1-2. Unde suntem
# ===========================================================================

AGENDA = [
    ("Ce este un API", "Un intermediar cu un contract; de ce colectăm prin API și ce costă."),
    ("Tipuri de API", "Criteriile de clasificare, trei decenii de istorie, patru stiluri."),
    ("Cum arată o cerere", "Mesajul HTTP: metoda, endpoint-ul, adresa cu parametrii, codul de stare."),
    ("De unde vin datele", "Surse accesibile prin API și sursele proiectului."),
    ("requests", "Aceeași cerere în Python; paginarea."),
    ("Eurostat", "Cererea pe dimensiuni și cubul JSON-stat, pe datele migrației."),
    ("Primele date și echipa", "O colectare reală, în curs/data/c2; apoi depozitul echipei, în proiect/."),
]
CAIET_NOTA = (f'<a class="leg" href="{repo_fisier("curs/" + CAIET)}" target="_blank" rel="noopener">'
              f"<code>{CAIET}</code></a>, salvat în <code>dsw/curs/</code>, lângă caietul 01. "
              "Fișierele colectate ajung în <code>curs/data/c2</code>.")
AGENDA_IX = {"static": True, "titlu": "Planul lecției",
             "etape": [{"nume": n, "unde": "azi", "text": d} for n, d in AGENDA]}

sl("s1", "Cursul", "Planul lecției",
   "<h2>Colectarea datelor prin API</h2>"
   "<p class=\"cheie\">Datele nu mai vin dintr-un fișier primit, ci dintr-o cerere "
   "scrisă, care se poate rula din nou.</p>"
   + ix("agenda", "Planul lecției", AGENDA_IX)
   + nota("Caietul lecției", CAIET_NOTA, True),
   manual=
   "<h2>Colectarea datelor prin API</h2>"
   "<p>La cursul 1, datele au venit dintr-un fișier descărcat dinainte. Pentru o analiză "
   "care trebuie refăcută, verificată și actualizată, drumul de la sursă la tabel trebuie "
   "să fie el însuși reproductibil: cine citește rezultatul trebuie să poată afla de unde "
   "vine fiecare valoare, cu ce filtre a fost cerută și când.</p>"
   "<p>Un API (<em>application programming interface</em>, interfață de programare a "
   "aplicațiilor) face drumul acesta explicit. Datele vin printr-o cerere scrisă, care "
   "conține sursa, setul și filtrele, și care se poate rula din nou, de altcineva, cu "
   "același rezultat sau cu o diferență care se poate explica.</p>"
   "<p>Capitolul urmează ordinea de la curs. Codul complet e în caietul cursului; aici "
   "stau conceptele, motivele și capcanele.</p>"
   + ix("agenda", "Planul lecției", AGENDA_IX)
   + nota("Caietul lecției", CAIET_NOTA, True))

sl("s2", "Cursul", "Unde am rămas",
   "<h2>Unde am rămas</h2>"
   "<ul>"
   "<li><strong>Folderul <code>dsw</code></strong>, cu <code>.venv</code> și pachetele din "
   "<code>requirements.txt</code>, și caietul 01 rulat de sus până jos.</li>"
   "<li><strong>Echipa de cinci</strong>, formată.</li>"
   "<li><strong>Contul GitHub</strong>, folosit pentru autentificarea pe site.</li>"
   "</ul>"
   "<p>Caietul lecției se descarcă separat, în <code>dsw/curs/</code>. <code>requests</code> e deja "
   "în mediu, din <code>requirements.txt</code>.</p>",
   manual=
   "<h2>Unde am rămas</h2>"
   "<p>Lecția pornește de la ce s-a construit la cursul 1: folderul cursului, <code>dsw</code>, "
   "cu mediul virtual <code>.venv</code> și pachetele din <code>requirements.txt</code>, și caietul 01 "
   "rulat de sus până jos. Dacă lipsește ceva, "
   "pașii sunt în <a class=\"leg\" href=\"../../c1-introducere-si-mediu/tutorial/\">manualul "
   "cursului 1</a>. Echipa de cinci e formată; la finalul orei își clonează depozitul, iar direcția "
   "proiectului se alege la cursul 3.</p>"
   "<p>Caietul lecției se descarcă separat, nu odată cu toată arhiva: pe "
   f'<a class="leg" href="{repo_fisier("curs/" + CAIET)}" target="_blank" rel="noopener">pagina lui de pe GitHub</a> '
   "se alege <em>Download raw file</em>, iar fișierul se salvează în <code>dsw/curs/</code>, lângă caietul 01. "
   "Arhiva întreagă, despachetată din nou peste <code>dsw</code>, ar putea suprascrie caietele deja completate.</p>"
   "<p>Biblioteca de azi, <code>requests</code>, e deja în mediu: e în <code>requirements.txt</code>. "
   "Dacă lipsește, cu mediul activ:</p>"
   "<pre><code>pip install -r requirements.txt</code></pre>")


# ===========================================================================
#  3-4. Ce este un API
# ===========================================================================

REST_COL = [
    {"sus": "Masa", "dsus": "clientul comandă", "jos": "scriptul", "djos": "clientul", "c": "accent"},
    {"sus": "Meniul", "dsus": "ce se poate cere", "jos": "documentația", "djos": "contractul API-ului", "c": "ceas"},
    {"sus": "Ospătarul", "dsus": "duce comanda", "jos": "API-ul", "djos": "singura intrare", "c": "ambra"},
    {"sus": "Bucătăria", "dsus": "pregătește felul", "jos": "serverul", "djos": "aplicația furnizorului", "c": "roza"},
    {"sus": "Cămara", "dsus": "ingredientele", "jos": "baza de date", "djos": "datele furnizorului", "c": "ardezie"},
]
_CER = "GET /v2/country/RO/indicator/SP.POP.TOTL?date=2024"
REST_SC = [
    {"t": "Drumul unei comenzi", "pasi": [
        {"col": [0, 1], "la": 0, "bon": "o ciorbă, fără ardei", "cer": _CER,
         "sus": "Clientul citește meniul și scrie pe bon exact ce vrea, în forma din meniu.",
         "jos": "Scriptul urmează documentația: adresa resursei și parametrii acceptați."},
        {"col": [2], "la": 2, "bon": "o ciorbă, fără ardei", "cer": _CER,
         "sus": "Ospătarul duce bonul. Clientul nu intră în bucătărie.",
         "jos": "Cererea ajunge la API, singura intrare prin care se ajunge la datele furnizorului."},
        {"col": [3, 4], "la": 3, "bon": "o ciorbă, fără ardei", "cer": _CER,
         "sus": "Bucătăria ia din cămară ce scrie pe bon și pregătește felul.",
         "jos": "Serverul interoghează baza de date și aplică filtrele din cerere: țara RO, anul 2024."},
        {"col": [0], "la": 0, "intors": True, "bon": "ciorba, fără ardei",
         "cer": "200 OK · [{\"page\": 1, …}, [{\"value\": 19051804, …}]]",
         "sus": "Farfuria se întoarce pe același drum.",
         "jos": "Răspunsul se întoarce: un cod de stare, apoi corpul, în JSON."}],
     "concluzie": "Clientul și bucătăria nu se văd: tot ce trece între ei trece prin meniu și prin ospătar."},
    {"t": "Bucătăria se schimbă, meniul nu", "pasi": [
        {"col": [3, 4], "schimb": [3, 4], "la": 0, "bon": "o ciorbă, fără ardei", "cer": _CER,
         "sus": "Restaurantul schimbă bucătarul și furnizorul de ingrediente.",
         "jos": "Furnizorul mută datele pe alt server și schimbă baza de date."},
        {"col": [1], "schimb": [3, 4], "la": 0, "bon": "o ciorbă, fără ardei", "cer": _CER,
         "sus": "Meniul rămâne același: aceleași feluri, cu aceleași nume.",
         "jos": "Documentația rămâne aceeași: aceleași adrese, aceiași parametri, același format al răspunsului."},
        {"col": [0, 1, 2, 3, 4], "schimb": [3, 4], "la": 0, "intors": True, "bon": "ciorba, fără ardei",
         "cer": "200 OK · același JSON",
         "sus": "Aceeași comandă aduce același fel.",
         "jos": "Aceeași cerere aduce același răspuns; scriptul rămâne neschimbat."}],
     "concluzie": "Scriptul depinde de contract, nu de felul în care e construit serverul. "
                  "Asta e abstractizarea: documentația separă cererea de implementare."},
    {"t": "Meniul are o ediție", "pasi": [
        {"col": [1], "la": 0, "bon": "comandă după meniul vechi", "cer": "GET /v2/country/RO/…",
         "sus": "Restaurantul tipărește un meniu nou, dar îl păstrează un timp și pe cel vechi.",
         "jos": "Furnizorul publică o versiune nouă a API-ului; versiunea veche rămâne în funcțiune o perioadă."},
        {"col": [1, 2], "la": 2, "bon": "comandă după meniul vechi", "cer": "GET /v2/country/RO/…",
         "sus": "O comandă după meniul vechi e servită în continuare.",
         "jos": "Versiunea e scrisă în adresă (/v2): o cerere veche primește formatul vechi, iar codul existent nu se strică."},
        {"col": [1], "la": 0, "intors": True, "bon": "felul, ca înainte", "cer": "200 OK · formatul /v2",
         "sus": "Meniul vechi se retrage la o dată anunțată.",
         "jos": "Versiunile vechi au o dată de retragere; o colectare care rulează ani de zile urmărește anunțurile furnizorului."}],
     "concluzie": "Versiunea din adresă face ca schimbările furnizorului să nu strice, fără avertisment, codul care îl folosește."},
    {"t": "Ospătarul nu ține minte", "pasi": [
        {"col": [0], "la": 0, "bon": "masa 4: o ciorbă, fără ardei", "cer": "GET …SP.POP.TOTL?page=3&per_page=50",
         "sus": "Fiecare bon e complet: masa, felul, cantitatea.",
         "jos": "Fiecare cerere conține adresa și toți parametrii, inclusiv pagina cerută."},
        {"col": [2], "la": 2, "bon": "masa 4: o ciorbă, fără ardei", "cer": "GET …SP.POP.TOTL?page=3&per_page=50",
         "sus": "Ospătarul nu reține comenzile anterioare.",
         "jos": "Serverul nu păstrează nicio informație de la o cerere la alta."},
        {"col": [2, 3], "la": 3, "bon": "masa 4: o ciorbă, fără ardei", "cer": "GET …SP.POP.TOTL?page=3&per_page=50",
         "sus": "Orice ospătar poate prelua bonul, pentru că pe bon scrie tot.",
         "jos": "Orice server din spatele API-ului poate răspunde, pentru că cererea are tot ce trebuie."},
        {"col": [0], "la": 0, "intors": True, "bon": "ciorba de la masa 4", "cer": "200 OK · pagina 3",
         "sus": "O comandă pierdută se dă din nou, cu același bon.",
         "jos": "O colectare întreruptă se reia de la pagina la care a rămas, cu aceeași cerere."}],
     "concluzie": "Asta înseamnă „fără stare” (stateless): toată informația stă în cerere, nu pe server."},
]
RESTAURANT = {"coloane": REST_COL, "scenarii": REST_SC}

V_CONTRACT = verif(
    "c2-v2b", 1,
    "Banca Mondială își mută datele pe alt server și schimbă baza de date, dar păstrează "
    "adresele și parametrii din documentație. Ce se întâmplă cu scriptul tău de colectare?",
    ["Trebuie rescris, pentru că baza de date e alta",
     "Funcționează la fel: contractul nu s-a schimbat",
     "Funcționează doar pe calculatorul pe care a fost scris",
     "Primește 404 la prima cerere"],
    "Scriptul depinde de contract (adrese, parametri, formatul răspunsului), nu de felul în "
    "care e construit serverul. Documentația, nu infrastructura furnizorului, e ce trebuie "
    "urmărit.")

sl("s3", "Ce este un API", "Analogia restaurantului",
   "<h2>Analogia restaurantului</h2>"
   "<p class=\"cheie\">Un API e intermediarul dintre codul clientului și datele furnizorului, "
   "cu un contract scris: ce se poate cere și în ce formă.</p>"
   + ix("restaurant", "Același drum, pe două straturi", RESTAURANT),
   dupa=V_CONTRACT,
   manual=
   "<h2>Ce este un API</h2>"
   "<p>Analogia restaurantului fixează un principiu esențial: codul clientului nu "
   "comunică direct cu baza de date a furnizorului. Comunică cu un intermediar, care o "
   "accesează în numele clientului, în condiții stabilite dinainte. Condițiile acestea sunt contractul "
   "API-ului, iar documentația e forma lui citibilă.</p>"
   + ix("restaurant", "Același drum, pe două straturi", RESTAURANT)
   + tabel(["La restaurant", "La un API"], [
       ["masa, clientul", "scriptul"],
       ["meniul", "documentația: ce resurse există, ce parametri primesc, ce formă are răspunsul"],
       ["bonul", "cererea: metoda, adresa, parametrii"],
       ["ospătarul", "API-ul, singura intrare spre date"],
       ["bucătăria și cămara", "serverul și baza de date"],
       ["farfuria", "răspunsul: un cod de stare și corpul"],
   ])
   + "<h3>Patru proprietăți, nu doar un drum</h3>"
   "<p><strong>Contractul.</strong> Documentația descrie complet ce se poate cere. Multe "
   "API-uri publică o descriere citibilă de mașini, în formatul OpenAPI, din care se "
   "generează documentație și cod.</p>"
   "<p><strong>Abstractizarea.</strong> Clientul depinde de contract, nu de implementare. "
   "Furnizorul își poate schimba serverele și baza de date fără ca scriptul clientului să se "
   "schimbe.</p>"
   "<p><strong>Versionarea.</strong> Când contractul se schimbă, furnizorul publică o "
   "versiune nouă (la Banca Mondială, <code>/v2</code> din adresă), iar versiunea veche "
   "rămâne în funcțiune până la o dată anunțată.</p>"
   "<p><strong>Lipsa stării.</strong> Serverul nu păstrează nimic de la o cerere la alta. "
   "Fiecare cerere conține tot ce trebuie, deci o colectare întreruptă se reia de la "
   "pagina la care a rămas.</p>"
   "<h3>Limitele analogiei</h3>"
   "<p>Un API nu negociază și nu interpretează. O cerere care nu respectă contractul nu "
   "primește o explicație, ci un cod de eroare și, uneori, un mesaj scurt. De aceea "
   "documentația se citește înainte de prima cerere, nu după primul eșec.</p>")

MOTIVE = (
    '<div class="mtv">'
    '<div class="mtv__f" style="--c:var(--accent)"><h4>Știință</h4><dl>'
    "<div><dt>Proveniență</dt><dd>Cererea înregistrează sursa, setul, filtrele și data colectării: "
    "e documentația colectării.</dd></div>"
    "<div><dt>Reproductibilitate</dt><dd>Altcineva rulează același cod și obține același tabel, "
    "sau vede exact ce s-a schimbat.</dd></div>"
    "<div><dt>Principiile FAIR</dt><dd>Accesul printr-un protocol standard e una dintre condițiile "
    "datelor reutilizabile (Wilkinson et al., 2016).</dd></div>"
    "</dl></div>"
    '<div class="mtv__f" style="--c:var(--ambra)"><h4>Inginerie</h4><dl>'
    "<div><dt>Scară</dt><dd>Toate regiunile NUTS 3, pe ani și pe indicatori: mii de valori, "
    "într-o singură buclă.</dd></div>"
    "<div><dt>Actualizare</dt><dd>Statisticile oficiale se revizuiesc; aceeași cerere, rulată din "
    "nou, aduce versiunea curentă.</dd></div>"
    "<div><dt>Filtrare la sursă</dt><dd>Serverul trimite doar felia cerută, nu tot setul.</dd></div>"
    "<div><dt>Automatizare</dt><dd>Colectarea se poate programa, repeta și verifica fără "
    "intervenție manuală.</dd></div>"
    "</dl></div>"
    '<div class="mtv__f" style="--c:var(--roza)"><h4>Calitatea datelor</h4><dl>'
    "<div><dt>Integritate</dt><dd>Fără copieri și conversii manuale. Aproximativ o cincime din "
    "articolele cu liste de gene în anexe Excel aveau nume de gene transformate în date "
    "calendaristice (Ziemann et al., 2016).</dd></div>"
    "<div><dt>Metadate</dt><dd>Unitățile, etichetele și indicatorii de stare (estimat, provizoriu, "
    "ruptură de serie) vin odată cu valoarea.</dd></div>"
    "<div><dt>Acces legitim</dt><dd>API-ul e calea prevăzută de furnizor, cu condiții și limite "
    "scrise.</dd></div>"
    "</dl></div></div>"
    '<div class="mtv__cost"><b>Ce costă</b><p>Dependență de furnizor (versiuni, întreruperi), '
    "limite de cereri, chei de acces, timpul de citit documentația. Un fișier publicat, datat și "
    "versionat, cum e SCI de pe HDX, rămâne o alegere corectă.</p></div>")

sl("s5", "Ce este un API", "De ce prin API",
   "<h2>De ce prin API</h2>" + MOTIVE,
   manual=
   "<h2>De ce colectăm prin API</h2>"
   "<p>Întrebarea apare firesc: dacă fișierul se poate descărca dintr-un clic, de ce ar fi "
   "nevoie de cod pentru a-l obține? Motivele țin de știință, de inginerie și de calitatea "
   "datelor, iar fiecare are și un cost.</p>"
   + MOTIVE
   + "<h3>Știință</h3>"
   "<p>O analiză e credibilă în măsura în care drumul de la sursă la rezultat poate fi "
   "verificat. O cerere scrisă e documentația colectării: conține sursa, setul, filtrele "
   "și, dacă este salvată, momentul colectării. Principiile FAIR (<em>Findable, Accessible, "
   "Interoperable, Reusable</em>) cer ca datele să poată fi accesate printr-un protocol "
   "standard, deschis (Wilkinson et al., 2016).</p>"
   "<h3>Inginerie</h3>"
   "<p>Proiectul lucrează cu sute de regiuni, pe mai mulți ani și pe mai mulți indicatori. "
   "Statisticile oficiale se revizuiesc după publicare, așa că aceeași colectare trebuie "
   "să poată fi rulată din nou, iar diferențele să poată fi comparate. Filtrarea la sursă "
   "reduce volumul transferat la felia de care e nevoie.</p>"
   "<h3>Calitatea datelor</h3>"
   "<p>Fiecare pas manual poate introduce erori sistematice. Exemplul cel mai citat vine "
   "din genetică: aproximativ o cincime din articolele cu liste de gene în anexe Excel "
   "conțineau nume de gene convertite automat în date calendaristice (Ziemann, Eren și "
   "El-Osta, 2016). Un răspuns structurat păstrează și metadatele: unități, etichete, "
   "indicatori de stare, pe care un export manual îi poate pierde.</p>"
   "<h3>Ce costă</h3>"
   "<p>Un API creează o dependență de furnizor: versiunile se schimbă, serviciile au "
   "întreruperi, iar limitele de cereri și cheile de acces trebuie gestionate. Un fișier "
   "publicat, datat și versionat rămâne o alegere corectă: SCI-ul din cursul 1 vine de pe "
   "HDX tocmai ca un instantaneu de felul acesta.</p>"
   "<p>În practică, proveniența se păstrează simplu: data colectării în numele fișierului "
   "salvat, iar în caiet, celula care l-a produs.</p>"
   + surse("Referințe", [
       ("Wilkinson et al. (2016), The FAIR Guiding Principles", "https://doi.org/10.1038/sdata.2016.18",
        "<em>Scientific Data</em> 3, 160018"),
       ("Ziemann, Eren și El-Osta (2016), Gene name errors", "https://doi.org/10.1186/s13059-016-1044-7",
        "<em>Genome Biology</em> 17, 177"),
   ]))


# ===========================================================================
#  5-7. Tipuri de API
# ===========================================================================

def _t(n, ce, cum, ex, ds, noi=False):
    d = {"n": n, "ce": ce, "cum": cum, "ex": ex, "ds": ds}
    if noi:
        d["noi"] = True
    return d

CRITERII = {"ales": "REST", "coloane": [
    {"t": "După stil", "q": "cum arată cererea", "c": "accent", "tipuri": [
        _t("REST", "Stil de API construit pe HTTP: fiecare resursă are o adresă.",
           "Metode HTTP standard pe adrese; serverul nu păstrează stare între cereri; răspunsurile se pot păstra în cache.",
           "Banca Mondială, Eurostat Statistics API, GitHub REST API.",
           "Forma cea mai frecventă a surselor publice de date; se poate încerca și din browser.", True),
        _t("GraphQL", "Limbaj de interogare pentru API-uri, făcut public de Facebook în 2015.",
           "O singură adresă; clientul trimite o interogare care descrie exact câmpurile dorite, iar schema tipizată spune ce se poate cere.",
           "GitHub GraphQL API, Shopify.",
           "Aduce exact câmpurile necesare, într-o singură cerere, în locul mai multor cereri REST."),
        _t("gRPC", "Cadru de apeluri de funcții la distanță, făcut public de Google în 2015.",
           "Funcțiile și mesajele se definesc în Protocol Buffers; schimbul e binar, peste HTTP/2, cu contract strict.",
           "Comunicarea între serviciile interne ale unei platforme.",
           "Rar în sursele publice de date; apare la integrarea cu sisteme de producție."),
        _t("SOAP", "Protocol de mesaje XML, cu reguli stricte.",
           "Fiecare mesaj e un plic XML; operațiile sunt descrise într-un fișier WSDL.",
           "Sisteme bancare, administrație, servicii instituționale mai vechi.",
           "Apare la integrarea cu sisteme instituționale."),
    ]},
    {"t": "După acces", "q": "cine are voie", "c": "ambra", "tipuri": [
        _t("public", "Deschis oricui, uneori cu o cheie gratuită.",
           "Accesul e liber sau condiționat de o cheie personală; limitele de cereri sunt publicate.",
           "Banca Mondială și Eurostat, fără cheie.",
           "Sursa principală pentru cercetare; condițiile de reutilizare se citesc înainte.", True),
        _t("partener", "Deschis doar organizațiilor cu un acord.",
           "Accesul se dă prin contract, cu chei dedicate și garanții de serviciu.",
           "Integrarea dintre un magazin online și procesatorul lui de plăți.",
           "Datele vin cu condițiile contractului, nu cu o licență publică."),
        _t("intern", "Folosit doar în interiorul organizației.",
           "Accesibil doar în rețeaua ei, între serviciile proprii.",
           "Serviciul care alimentează tabloul de bord intern al unei companii.",
           "Cea mai frecventă sursă de date în industrie, deși nu se vede din afară."),
    ]},
    {"t": "După inițiativă", "q": "cine pornește schimbul", "c": "roza", "tipuri": [
        _t("cerere și răspuns", "Clientul cere, serverul răspunde.",
           "Fiecare schimb pornește de la client; fără cerere nu vine nimic.",
           "O cerere GET la Banca Mondială.",
           "Modelul colectării din curs: datele se cer atunci când sunt necesare.", True),
        _t("webhooks", "Serverul anunță clientul când apare un eveniment.",
           "Clientul îi comunică furnizorului o adresă proprie; la eveniment, furnizorul trimite acolo o cerere HTTP, de obicei POST.",
           "GitHub anunță un server la fiecare push într-un depozit.",
           "Declanșează o colectare când apar date noi, fără interogări repetate."),
        _t("WebSocket și fluxuri", "O legătură deschisă, prin care datele curg continuu.",
           "WebSocket (RFC 6455, 2011) ține o conexiune bidirecțională; fluxurile trimit evenimente pe măsură ce apar.",
           "Cotații bursiere, poziții de vehicule, senzori, în timp real.",
           "Date care se analizează pe măsură ce sosesc, nu în loturi."),
    ]},
    {"t": "După domeniu", "q": "ce fel de date dă", "c": "ardezie", "tipuri": [
        _t("statistici oficiale", "API-urile institutelor de statistică.",
           "Standarde comune: SDMX, susținut de Eurostat, BCE, FMI, OCDE, ONU, Banca Mondială și BIS, și JSON-stat.",
           "Eurostat oferă un API SDMX 2.1, unul SDMX 3.0 și Statistics API, în JSON-stat 2.0.",
           "Sursele proiectului: datele vin cu metadate și coduri standard.", True),
        _t("baze de date", "Baze de date expuse direct ca API.",
           "Fiecare tabel devine o resursă REST; o cerere HTTP devine o interogare.",
           "PostgREST și Supabase, peste PostgreSQL.",
           "Citirea și scrierea în bază se fac prin aceleași cereri HTTP."),
        _t("cloud", "Infrastructură controlată prin API.",
           "Stocarea și calculul se comandă prin cereri autentificate.",
           "Amazon S3, Azure Blob Storage.",
           "Seturile mari stau în stocare de obiecte și se citesc prin API."),
        _t("servicii AI", "Modele oferite ca serviciu.",
           "Clientul trimite textul sau datele și primește rezultatul modelului; plata e de obicei pe volum.",
           "OpenAI, Anthropic, Hugging Face.",
           "Clasificare, extragere de informații, anotare, ca pas într-un flux de date."),
        _t("IoT", "Dispozitive care trimit măsurători.",
           "Senzorii publică valori, adesea prin MQTT, un protocol de mesaje mai ușor decât HTTP.",
           "Stații meteo, contoare inteligente.",
           "Serii de timp dense, cu valori lipsă și erori de senzor."),
    ]},
]}

sl("s6", "Tipuri de API", "Tipuri de API",
   "<h2>Tipuri de API</h2>"
   "<p class=\"cheie\">Clasificările nu se contrazic: se fac după criterii diferite. "
   "Banca Mondială e, în același timp, REST, publică și de tip cerere și răspuns.</p>"
   + ix("criterii", "Patru criterii", CRITERII),
   manual=
   "<h2>Tipuri de API</h2>"
   "<p>Un API se descrie după mai multe criterii deodată: după stilul cererii, după cine "
   "are acces, după cine pornește schimbul și după domeniul datelor. Criteriile nu se "
   "exclud, deci aceeași sursă apare în mai multe coloane. La curs folosim o singură "
   "combinație: REST, public, cerere și răspuns, statistici oficiale.</p>"
   + ix("criterii", "Patru criterii", CRITERII)
   + surse("Documentații", [
       ("GraphQL", "https://graphql.org/learn/", "limbajul de interogare, schema, introspecția"),
       ("gRPC", "https://grpc.io/docs/what-is-grpc/introduction/", "Protocol Buffers, serviciile, streaming"),
       ("SDMX", "https://sdmx.org/", "standardul schimbului de date statistice"),
       ("JSON-stat", "https://json-stat.org/format/", "formatul răspunsurilor Eurostat"),
   ]))

def _p(an, n, problema, cum, azi, data=None):
    d = {"an": an, "n": n, "problema": problema, "cum": cum, "azi": azi}
    if data:
        d["data"] = data
    return d

BENZI = {"de": 1990, "pana": 2026, "ales": [1, 0],
         "repere": [{"an": 1996.5, "n": "HTTP/1.0 și 1.1"}, {"an": 2015, "n": "HTTP/2"}, {"an": 2022, "n": "HTTP/3"}],
         "benzi": [
    {"t": "Apeluri la distanță", "c": "roza", "puncte": [
        _p(1991, "CORBA", "Programe scrise în limbaje diferite, pe mașini diferite, trebuiau să-și apeleze funcțiile.",
           "Un intermediar de obiecte transmite apelurile; interfețele se descriu într-un limbaj neutru (IDL).",
           "Sisteme industriale și de telecomunicații vechi."),
        _p(1998, "XML-RPC", "Apelurile la distanță cereau infrastructură grea.",
           "Un apel de funcție, împachetat în XML și trimis prin HTTP.",
           "Sisteme vechi de publicare a conținutului."),
        _p(1999, "SOAP", "XML-RPC nu avea reguli pentru tipuri, erori și securitate.",
           "Mesaj XML într-un plic standard; operațiile se descriu în WSDL.",
           "Bănci, administrație, integrarea sistemelor instituționale."),
        _p(2005, "JSON-RPC", "XML era greu de citit și de produs.",
           "Același apel de funcție, scris în JSON.",
           "Noduri blockchain și protocolul MCP, care folosește JSON-RPC 2.0."),
        _p(2015, "gRPC", "Serviciile unei platforme mari schimbă un volum uriaș de mesaje, iar textul e lent.",
           "Funcții și mesaje definite în Protocol Buffers; schimb binar peste HTTP/2. Versiunea 1.0, august 2016.",
           "Comunicarea dintre microservicii."),
    ]},
    {"t": "Resurse și interogări", "c": "accent", "puncte": [
        _p(2000, "REST", "Cum se descrie arhitectura care a permis webului să funcționeze la scară.",
           "Resurse identificate prin adrese, metode standard, fără stare între cereri, răspunsuri care se pot păstra în cache. "
           "Teza de doctorat a lui Roy Fielding.",
           "Majoritatea API-urilor publice de date, inclusiv Banca Mondială și Eurostat."),
        _p(2007, "OData", "Fiecare API REST își inventa propria sintaxă de filtrare.",
           "Interogări standardizate în adresă: $filter, $select, $orderby.",
           "Produse Microsoft și SAP; standard OASIS din 2014, ISO/IEC din 2016."),
        _p(2015, "GraphQL", "Aplicațiile mobile primeau dintr-o cerere REST fie prea multe date, fie prea puține.",
           "O singură adresă; clientul descrie exact forma răspunsului.",
           "GitHub, Shopify; GraphQL Foundation, din noiembrie 2018.", "14 sept. 2015"),
    ]},
    {"t": "Contracte și evenimente", "c": "ambra", "puncte": [
        _p(2007, "webhooks", "Clientul trebuia să întrebe mereu dacă s-a schimbat ceva.",
           "Serverul trimite el o cerere la o adresă dată de client, când apare evenimentul. Termenul: Jeff Lindsay.",
           "GitHub, plăți online, notificări."),
        _p(2010, "Swagger", "Documentația unui API era text pentru oameni, nu pentru programe.",
           "Un fișier descrie toate adresele, parametrii și răspunsurile; din el se generează documentație și cod.",
           "Devine OpenAPI în 2015."),
        _p(2011, "WebSocket", "Serverul nu putea trimite date din proprie inițiativă.",
           "O conexiune deschisă, bidirecțională, standardizată în RFC 6455.",
           "Cotații, colaborare și jocuri în timp real.", "dec. 2011"),
        _p(2015, "OpenAPI", "Fiecare organizație își descria API-urile în alt fel.",
           "Swagger trece la OpenAPI Initiative (Linux Foundation) și devine standard deschis: 3.0 în 2017, 3.1 în 2021, 3.2 în 2025.",
           "Documentația celor mai multe API-uri REST de azi.", "nov. 2015"),
    ]},
    {"t": "Date statistice", "c": "salvie", "puncte": [
        _p(2005, "SDMX", "Băncile centrale și institutele de statistică schimbau date în formate diferite.",
           "Un model comun pentru serii statistice: dimensiuni, coduri, atribute. Specificație tehnică ISO din 2005 (ISO/TS 17369); versiunea 2.1 a devenit standard ISO 17369 în 2013.",
           "Eurostat, BCE, FMI, OCDE, ONU, Banca Mondială, BIS."),
        _p(2011, "SDMX 2.1", "Schimbul de date statistice trebuia să meargă prin servicii web obișnuite.",
           "Versiunea care include interogarea datelor prin adrese, în stil REST.",
           "API-ul SDMX 2.1 al Eurostat.", "mai 2011"),
        _p(2021, "SDMX 3.0", "Modelul trebuia simplificat și extins.",
           "Versiune nouă a standardului și a interogărilor.",
           "API-ul SDMX 3.0 al Eurostat.", "sept. 2021"),
    ]},
    {"t": "Agenți AI", "c": "ardezie", "puncte": [
        _p(2024, "MCP", "Fiecare aplicație AI își scria propriii conectori spre unelte și date.",
           "Model Context Protocol, anunțat de Anthropic: un protocol comun, peste JSON-RPC 2.0, prin care un model "
           "folosește unelte și surse de date.",
           "Adoptat de OpenAI în martie 2025; donat în decembrie 2025 către Agentic AI Foundation (Linux Foundation).",
           "25 nov. 2024"),
        _p(2025, "A2A", "Agenții AI ai unor furnizori diferiți nu puteau colabora.",
           "Agent2Agent: agenții își descriu capacitățile și schimbă mesaje și sarcini printr-un protocol comun.",
           "Anunțat de Google; la Linux Foundation din iunie 2025.", "9 apr. 2025"),
    ]},
]}

sl("s7", "Tipuri de API", "Trei decenii de API-uri",
   "<h2>Trei decenii de API-uri</h2>"
   "<p class=\"cheie\">Fiecare stil a apărut ca răspuns la costul celui dinainte; contractele "
   "au făcut API-urile descriptibile de mașini, iar MCP și A2A extind ideea la agenții AI.</p>"
   + ix("benzi", "Cinci familii, pe aceeași axă", BENZI),
   manual=
   "<h2>Trei decenii de API-uri</h2>"
   "<p>Istoria API-urilor nu e o succesiune în care fiecare tehnologie o înlocuiește pe "
   "cea dinainte. Sunt mai multe familii care au evoluat în paralel: apelurile la "
   "distanță, resursele și interogările, contractele și evenimentele, standardele "
   "statistice și, recent, protocoalele pentru agenți AI. Dedesubt, protocolul HTTP s-a "
   "schimbat și el, de la HTTP/1.0 la HTTP/3, fără să schimbe înțelesul unei cereri.</p>"
   + ix("benzi", "Cinci familii, pe aceeași axă", BENZI)
   + "<p>REST e descris în 2000, în teza de doctorat a lui Roy Fielding, ca stil "
     "arhitectural al webului. Banda statisticilor e cea care ne privește direct: Eurostat "
     "publică datele prin SDMX și prin JSON-stat, iar Banca Mondială e unul dintre "
     "sponsorii SDMX.</p>"
   + surse("Surse pentru cronologie", [
       ("Fielding (2000), teza despre REST", "https://ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm", "capitolul 5, stilul REST"),
       ("OpenAPI Specification", "https://en.wikipedia.org/wiki/OpenAPI_Specification", "Swagger 2010, OpenAPI Initiative 2015, versiunile 3.x"),
       ("SDMX", "https://en.wikipedia.org/wiki/SDMX", "1.0 (ISO/TS, 2005), 2.1 (2011; ISO 17369:2013), 3.0 (2021)"),
       ("GraphQL", "https://en.wikipedia.org/wiki/GraphQL", "public în 2015, GraphQL Foundation în 2018"),
       ("gRPC", "https://en.wikipedia.org/wiki/GRPC", "făcut public în 2015, 1.0 în 2016"),
       ("Model Context Protocol", "https://en.wikipedia.org/wiki/Model_Context_Protocol", "anunțat în noiembrie 2024"),
       ("Agent2Agent", "https://en.wikipedia.org/wiki/Agent2Agent", "anunțat în aprilie 2025"),
   ]))

STILURI = (
    '<div class="stl-w"><div class="stl">'
    '<span></span>'
    '<div class="stl__h noi" style="--c:var(--accent)"><b>REST</b><span>folosim</span></div>'
    '<div class="stl__h" style="--c:color-mix(in srgb,var(--accent) 55%,var(--panza))"><b>GraphQL</b></div>'
    '<div class="stl__h" style="--c:var(--roza)"><b>gRPC</b></div>'
    '<div class="stl__h" style="--c:color-mix(in srgb,var(--roza) 55%,var(--panza))"><b>SOAP</b></div>'
    '<span class="stl__l">aceeași întrebare: populația României în 2024</span>'
    '<pre class="stl__cod">GET /v2/country/RO/\n  indicator/SP.POP.TOTL\n  ?date=2024<em>real: Banca Mondială</em></pre>'
    '<pre class="stl__cod">POST /graphql\n{ country(code: "RO") {\n  population(year: 2024)\n} }<em>ilustrativ</em></pre>'
    '<pre class="stl__cod">rpc Populatie (Cerere)\n  returns (Valoare);\n\n{tara: "RO", an: 2024}<em>ilustrativ</em></pre>'
    '<pre class="stl__cod">&lt;Envelope&gt;&lt;Body&gt;\n &lt;Populatie&gt;\n  &lt;tara&gt;RO&lt;/tara&gt;\n  &lt;an&gt;2024&lt;/an&gt; …<em>ilustrativ</em></pre>'
    '<span class="stl__l">unitatea de bază</span>'
    '<span class="stl__v">resursa, la o adresă</span><span class="stl__v">câmpul, dintr-o schemă</span>'
    '<span class="stl__v">funcția</span><span class="stl__v">operația, într-un mesaj</span>'
    '<span class="stl__l">formatul</span>'
    '<span class="stl__v">JSON, uneori XML sau CSV</span><span class="stl__v">JSON</span>'
    '<span class="stl__v">Protocol Buffers, binar</span><span class="stl__v">XML</span>'
    '<span class="stl__l">contractul</span>'
    '<span class="stl__v">OpenAPI, opțional</span><span class="stl__v">schemă, obligatorie</span>'
    '<span class="stl__v">fișier .proto, obligatoriu</span><span class="stl__v">WSDL, obligatoriu</span>'
    '<span class="stl__l">forma răspunsului o decide</span>'
    '<span class="stl__v">serverul</span><span class="stl__v">clientul</span>'
    '<span class="stl__v">contractul</span><span class="stl__v">contractul</span>'
    '<span class="stl__l">unde se întâlnește</span>'
    '<span class="stl__v">date publice, servicii web</span><span class="stl__v">aplicații web și mobile</span>'
    '<span class="stl__v">între serviciile unei platforme</span><span class="stl__v">bănci, administrație</span>'
    '</div></div>')

sl("s8", "Tipuri de API", "Aceeași întrebare, patru stiluri",
   "<h2>Aceeași întrebare, patru stiluri</h2>" + STILURI,
   manual=
   "<h2>Patru stiluri, față în față</h2>"
   "<p>Diferența dintre stiluri se vede cel mai clar pe aceeași întrebare, formulată "
   "în fiecare stil. Doar exemplul REST e un API real, al Băncii Mondiale; celelalte trei "
   "arată forma pe care ar avea-o aceeași cerere.</p>"
   + STILURI
   + "<p>Diferența de fond e cine decide forma răspunsului. În REST o decide serverul, "
     "pentru fiecare resursă; în GraphQL o decide clientul, prin interogare; în gRPC și "
     "SOAP e fixată de contract. Pentru colectarea datelor publice, REST rămâne stilul "
     "dominant pentru că se poate încerca din browser, nu cere unelte speciale și "
     "răspunde de obicei în JSON.</p>")


# ===========================================================================
#  8-13. Cum arată o cerere
# ===========================================================================

PARTI = {"linie": {"n": "prima linie", "c": "accent"}, "antet": {"n": "antete", "c": "ambra"},
         "gol": {"n": "rândul gol", "c": "text-3"}, "corp": {"n": "corpul", "c": "ardezie"}}
MESAJ = {
    "parti": PARTI, "ales": ["cerere", 0],
    "cerere": [
        {"t": "GET /v2/country/RO/indicator/SP.POP.TOTL?format=json&date=2022%3A2024&per_page=2&page=1 HTTP/1.1",
         "p": "linie", "e": "Metoda (GET: citește), ținta (calea și parametrii) și versiunea protocolului. "
                           "„:” din <code>2022:2024</code> apare codificat, ca <code>%3A</code>."},
        {"t": "Host: api.worldbank.org", "p": "antet", "e": "Serverul căruia îi e adresată cererea."},
        {"t": "User-Agent: python-requests/2.34.2", "p": "antet",
         "e": "Programul care trimite cererea: aici biblioteca requests, cu versiunea ei."},
        {"t": "Accept: */*", "p": "antet", "e": "Ce formate acceptă clientul în răspuns: aici, orice format."},
        {"t": "Accept-Encoding: gzip, deflate", "p": "antet", "e": "Răspunsul poate veni comprimat; requests îl decomprimă automat."},
        {"t": "", "p": "gol", "e": "Rândul gol încheie antetele. După el ar urma corpul cererii."},
        {"t": "(fără corp)", "p": "corp", "e": "O cerere GET nu are corp: tot ce cere stă în prima linie."},
    ],
    "raspuns": [
        {"t": "HTTP/1.1 200 OK", "p": "linie", "e": "Versiunea, codul de stare și textul lui. 200 înseamnă că cererea a reușit."},
        {"t": "Content-Type: application/json;charset=utf-8", "p": "antet",
         "e": "Formatul corpului: JSON, cu caractere UTF-8. Valoare reală, din caietul cursului."},
        {"t": "…", "p": "antet", "e": "Alte antete: data, dimensiunea, regulile de păstrare în cache."},
        {"t": "", "p": "gol", "e": "Rândul gol desparte antetele de corp."},
        {"t": "[{\"page\": 1, \"pages\": 2, \"per_page\": 2, \"total\": 3,", "p": "corp",
         "e": "Corpul, în JSON. Primul element al listei descrie paginarea: 3 valori în total, câte 2 pe pagină."},
        {"t": "  \"sourceid\": \"2\", \"lastupdated\": \"2026-10-08\"},", "p": "corp",
         "e": "Aceeași paginare: sursa și data ultimei actualizări a setului."},
        {"t": " [{\"country\": {\"id\": \"RO\", …}, \"date\": \"2024\", \"value\": 19051804, …},", "p": "corp",
         "e": "Al doilea element e lista valorilor. Prima: România, 2024, 19.051.804 locuitori."},
        {"t": "  {…, \"date\": \"2023\", \"value\": 19061062, …}]]", "p": "corp",
         "e": "A doua valoare de pe pagină: 2023. A treia, 2022, e pe pagina 2."},
    ],
}

sl("s9", "Cum arată o cerere", "O cerere și un răspuns",
   "<h2>O cerere și un răspuns</h2>"
   "<p class=\"cheie\">HTTP e un schimb de două mesaje text cu aceeași structură: "
   "o primă linie, antete, un rând gol, corpul.</p>"
   + ix("mesaj", "Cererea din caietul 02, întreagă", MESAJ)
   + '<div class="c2-idei">'
   "<p><b>REST e un stil peste HTTP:</b> resurse la adrese, metode standard, fără stare.</p>"
   "<p><b>Fără stare:</b> serverul nu păstrează nimic între cereri; tot ce trebuie e în mesaj, "
   "de aceea o colectare se poate relua de la orice pagină.</p></div>",
   manual=
   "<h2>Mesajul HTTP</h2>"
   "<p>Tot ce face un API REST trece prin HTTP, iar HTTP e, la bază, un schimb de două "
   "mesaje text. Cererea și răspunsul au aceeași structură: o primă linie, un șir de "
   "antete de forma <code>Nume: valoare</code>, un rând gol și, opțional, corpul.</p>"
   + ix("mesaj", "Cererea din caietul 02, întreagă", MESAJ)
   + "<h3>Antetele care contează la colectare</h3>"
   + tabel(["Antet", "În", "Ce spune"], [
       ["~Accept", "cerere", "ce formate acceptă clientul"],
       ["~User-Agent", "cerere", "ce program trimite cererea; unele API-uri cer o valoare descriptivă"],
       ["~Content-Type", "răspuns", "formatul corpului; dacă nu e JSON, corpul nu se citește cu <code>.json()</code>"],
       ["~Retry-After", "răspuns", "câte secunde trebuie așteptat după un refuz de tip 429 sau 503"],
   ])
   + "<p><strong>REST</strong> e un stil arhitectural construit peste HTTP: resursele au "
     "adrese, operațiile folosesc metodele standard, iar serverul nu păstrează stare între "
     "cereri. Consecința practică pentru colectare: o cerere poate fi repetată oricând, de "
     "oriunde, cu același efect.</p>"
   + "<p><strong>HTTPS</strong> e același HTTP, criptat. Versiunile HTTP/2 și HTTP/3 "
     "schimbă felul în care mesajele circulă (binar, multiplexat, peste QUIC la HTTP/3), nu "
     "înțelesul lor: metoda, adresa, antetele și codul de stare rămân aceleași.</p>"
   + "<p>Antetele cererii se pot vedea din Python cu <code>raspuns.request.headers</code>, "
     "iar cele ale răspunsului cu <code>raspuns.headers</code>.</p>")

VERBE = {
    "fise": [{"id": 5, "nume": "Echipa 5", "tema": "diaspora"},
             {"id": 6, "nume": "Echipa 6", "tema": "coridoare"},
             {"id": 7, "nume": "Echipa 7", "tema": "număr sau proporție"}],
    "metode": [
        {"m": "GET", "c": "accent", "crud": "citește", "op": "citeste", "tinta": 7, "cale": "/echipe/7",
         "sigura": True, "idem": "da",
         "efect": "Citește fișa 7. Nimic nu se schimbă pe server, oricâte cereri ar veni."},
        {"m": "POST", "c": "ambra", "crud": "creează", "op": "adauga", "cale": "/echipe",
         "corp": '{"nume": "Echipa 8", "tema": "rețele"}', "nou": {"id": 8, "nume": "Echipa 8", "tema": "rețele"},
         "sigura": False, "idem": "nu",
         "efect": "Creează o fișă nouă, iar serverul îi atribuie numărul. Repetată, creează încă una."},
        {"m": "PUT", "c": "roza", "crud": "înlocuiește", "op": "inlocuieste", "tinta": 7, "cale": "/echipe/7",
         "corp": '{"nume": "Echipa 7", "tema": "coridoare"}', "nou": {"nume": "Echipa 7", "tema": "coridoare"},
         "sigura": False, "idem": "da",
         "efect": "Înlocuiește fișa 7 întreagă cu conținutul trimis. Repetată, rezultatul e același."},
        {"m": "PATCH", "c": "ceas", "crud": "modifică", "op": "modifica", "tinta": 7, "cale": "/echipe/7",
         "corp": '{"tema": "coridoare"}', "camp": "tema", "valoare": "coridoare",
         "sigura": False, "idem": "nu, în general",
         "efect": "Schimbă doar câmpurile trimise; restul fișei rămâne cum era."},
        {"m": "DELETE", "c": "ardezie", "crud": "șterge", "op": "sterge", "tinta": 7, "cale": "/echipe/7",
         "sigura": False, "idem": "da",
         "efect": "Șterge fișa 7. Repetată, fișa rămâne ștearsă."},
    ],
}

SORTARE = {
       "id": "c2-sort-metode2",
       "sarcina": "Pune fiecare situație în dreptul metodei potrivite.",
       "elemente": [{"t": "aduci populația județelor", "cos": 0},
                    {"t": "adaugi o echipă nouă", "cos": 1},
                    {"t": "înlocuiești toată fișa unui student", "cos": 2},
                    {"t": "corectezi doar tema unei echipe", "cos": 3},
                    {"t": "scoți o colectare greșită", "cos": 4}],
       "cosuri": [{"t": "GET", "d": "citește"}, {"t": "POST", "d": "creează"},
                  {"t": "PUT", "d": "înlocuiește"}, {"t": "PATCH", "d": "modifică"},
                  {"t": "DELETE", "d": "șterge"}],
       "laBine": "Colectarea folosește numai GET; celelalte metode apar la scrierea într-un sistem.",
       "laRau": "Distincția de verificat: PUT trimite resursa întreagă, PATCH doar câmpurile modificate.",
       "explicatie": "Situațiile de citire corespund lui GET. PUT trimite resursa întreagă, PATCH doar "
                     "partea care se schimbă, POST creează o resursă nouă, DELETE o șterge."}

sl("s10", "Cum arată o cerere", "Metodele HTTP",
   "<h2>Metodele HTTP</h2>"
   "<p class=\"cheie\">Metoda indică operația cerută asupra resursei. La colectare se "
   "folosește GET: e sigură și idempotentă, deci o cerere eșuată se poate relua.</p>"
   + ix("verbe", "Cinci metode, o colecție de exemplu", VERBE),
   manual=
   "<h2>Metodele HTTP</h2>"
   "<p>Metoda e primul cuvânt din cerere și spune ce operație se cere asupra resursei. "
   "Cele patru operații de bază asupra unei colecții de date se numesc, pe scurt, CRUD "
   "(<em>create, read, update, delete</em>), iar HTTP le dă câte o metodă; modificarea "
   "are două: PUT înlocuiește resursa întreagă, PATCH doar câmpurile trimise.</p>"
   + ix("verbe", "Cinci metode, o colecție de exemplu", VERBE)
   + "<p>Două proprietăți contează la colectare. O metodă e <strong>sigură</strong> dacă nu "
     "schimbă nimic pe server, și <strong>idempotentă</strong> dacă repetarea ei are același "
     "efect ca o singură execuție. GET le are pe amândouă, deci o colectare întreruptă se "
     "poate relua fără riscuri. PUT și DELETE sunt idempotente, deși schimbă ceva; POST nu "
     "e: două cereri identice creează două resurse.</p>"
   + ix("sortare", "Ce metodă folosești", SORTARE)
   + surse("Documentație", [
       ("MDN: metodele HTTP", "https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods",
        "fiecare metodă, cu proprietățile ei"),
   ]))

sl("s10v", "Cum arată o cerere", "Exercițiu: metodele HTTP",
   "<h2>Exercițiu: metodele HTTP</h2>"
   + ix("sortare", "Ce metodă folosești", SORTARE),
   manual="")

sl("s11", "Cum arată o cerere", "Endpoint-ul",
   "<h2>Ce este un endpoint</h2>"
   "<p class=\"cheie\">Adresa la care se cere o anumită resursă. Fiecare endpoint "
   "întoarce altceva.</p>"
   "<pre><code>https://api.worldbank.org/v2/country/RO/indicator/SP.POP.TOTL</code></pre>"
   "<p>Un API are de obicei zeci de adrese; documentația le enumeră.</p>")

ADRESA = {
    "id": "c2-url",
    "sarcina": "Alege o placă, apoi rolul ei din legendă. Prima e rezolvată, ca exemplu.",
    "rezolvat": 0,
    "parti": [
        {"t": "https://", "e": "protocol"},
        {"t": "api.worldbank.org", "e": "host"},
        {"t": "/v2", "e": "versiune"},
        {"t": "/country/RO", "e": "resursa: țara"},
        {"t": "/indicator/SP.POP.TOTL", "e": "resursa: indicatorul"},
        {"t": "?format=json&date=2022:2024&per_page=2&page=1", "e": "parametri",
         "kv": ["format=json", "date=2022:2024", "per_page=2", "page=1"]},
    ],
    "roluri": [
        {"e": "protocol", "c": "ardezie", "d": "regulile de comunicare; <code>https</code> e criptat"},
        {"e": "host", "c": "roza", "d": "ce server răspunde"},
        {"e": "versiune", "c": "ceas", "d": "ediția contractului"},
        {"e": "resursa: țara", "c": "accent", "d": "prima resursă din cale"},
        {"e": "resursa: indicatorul", "c": "accent", "d": "a doua resursă: ce măsură"},
        {"e": "parametri", "c": "ambra", "d": "filtrele, după <code>?</code>, legate cu <code>&amp;</code>"},
    ],
    "dupa": '<div class="c2-idei" style="margin-top:0">'
            "<p><b>Calea indică ce se cere</b> (țara, indicatorul); <b>parametrii, cum se cere</b> "
            "(formatul, anii, pagina).</p>"
            "<p><b>Parametrii sunt dicționarul <code>params</code></b> din requests: biblioteca "
            "îi adaugă la adresă și codifică automat caracterele speciale.</p></div>"
            '<div class="c2-dict" style="margin-top:10px"><code>{"format": "json", "date": "2022:2024", '
            '"per_page": 2, "page": 1}</code><i>→</i>'
            "<code>?format=json&amp;date=2022%3A2024&amp;per_page=2&amp;page=1</code></div>",
}

sl("s12", "Cum arată o cerere", "Componentele adresei",
   "<h2>Componentele adresei</h2>"
   + ix("url", "Adresa primei cereri din caietul 02", ADRESA),
   manual=
   "<h2>Structura unei adrese</h2>"
   "<p>O adresă pare un simplu șir de caractere, dar are o gramatică. Când o cerere eșuează, "
   "eroarea se află aproape întotdeauna într-una dintre componente, iar pentru a o găsi, "
   "componentele trebuie să poată fi numite.</p>"
   + ix("url", "Adresa primei cereri din caietul 02", ADRESA)
   + "<p>Calea identifică resursa, iar parametrii o filtrează. Un cod de indicator greșit "
     "în cale duce la o eroare sau la altă resursă; un an greșit în parametri duce la un "
     "răspuns gol sau la un mesaj de eroare în corp. Mai există o componentă, fragmentul de "
     "după <code>#</code>, care nu se trimite niciodată la server: rămâne în browser.</p>"
   + "<p>Codificarea (<em>percent-encoding</em>) înlocuiește caracterele care au alt rol "
     "în adresă: „:” devine <code>%3A</code>, spațiul devine <code>%20</code> sau "
     "<code>+</code>. Cu <code>params=</code>, requests face codificarea; într-o adresă scrisă "
     "manual, codificarea trebuie făcută explicit.</p>"
   + verif("c2-v7", 2,
           "Unde pui filtrele unei cereri, de exemplu anul sau formatul?",
           ["în protocol", "în host", "în parametri, după semnul întrebării",
            "în fragment, după diez"],
           "În parametri. Fragmentul, de după <code>#</code>, nu se trimite la server: "
           "rămâne în browser."))

CLASE = [{"k": "1", "n": "informare", "c": "text-3"}, {"k": "2", "n": "reușită", "c": "accent"},
         {"k": "3", "n": "redirecționare", "c": "ceas"}, {"k": "4", "n": "eroare a cererii", "c": "ambra"},
         {"k": "5", "n": "eroare a serverului", "c": "roza"}]
RASPUNS = {
    "id": "c2-raspuns", "clase": CLASE,
    "cazuri": [
        {"et": "cerere bună", "cod": 200, "nume": "OK",
         "url": "api.worldbank.org/v2/country/RO/indicator/SP.POP.TOTL?format=json&date=1960:2024",
         "antete": ["Content-Type: application/json;charset=utf-8"],
         "corp": "[{\"page\": 1, \"pages\": 2, \"total\": 65, …}, [ … 50 de valori … ]]",
         "ce": "Cererea a reușit; corpul e JSON, pe pagini.",
         "faci": "Se citește corpul. Un 200 poate avea și zero valori, deci se verifică și câte au venit."},
        {"et": "adresă greșită", "cod": 404, "nume": "Not Found",
         "url": "api.worldbank.org/v2/country/RO/indicatorr/SP.POP.TOTL?format=json",
         "antete": ["Content-Type: text/html"],
         "corp": "<html><head><title>404</title></head> …",
         "ce": "Calea nu există. Corpul nu mai e JSON, ci o pagină HTML.",
         "faci": "Se verifică adresa în documentație. <code>.json()</code> ar eșua aici, pentru că corpul nu este JSON."},
        {"et": "parametru invalid", "cod": 200, "nume": "OK, cu eroare în corp",
         "url": "api.worldbank.org/v2/country/RO/indicator/SP.POP.TOTL?format=json&date=anul-trecut",
         "antete": ["Content-Type: application/json;charset=utf-8"],
         "corp": "[{\"message\": [{\"id\": \"120\", \"key\": \"Invalid value\", \"value\": \"The provided parameter value is not valid\"}]}]",
         "ce": "Banca Mondială răspunde 200 și la un parametru invalid; eroarea e în corp, sub <code>message</code>. "
               "Alte API-uri dau aici 400.",
         "faci": "După cod, se verifică structura: primul element trebuie să conțină <code>page</code>, nu <code>message</code>."},
        {"et": "prea multe cereri", "cod": 429, "nume": "Too Many Requests",
         "url": "api.worldbank.org/v2/country/RO/indicator/SP.POP.TOTL?page=97",
         "antete": ["Retry-After: 30"],
         "corp": "(corpul poate lipsi)",
         "ce": "Limita de cereri a fost depășită. Exemplu ilustrativ: valorile din antet diferă de la un API la altul.",
         "faci": "Se așteaptă cât indică <code>Retry-After</code>, apoi se reia, cu pauze care cresc după fiecare refuz."},
        {"et": "server indisponibil", "cod": 503, "nume": "Service Unavailable",
         "url": "api.worldbank.org/v2/country/RO/indicator/SP.POP.TOTL?format=json",
         "antete": ["Content-Type: text/html"],
         "corp": "Service temporarily unavailable",
         "ce": "Problema e la server, nu în cerere.",
         "faci": "Cererea se reia mai târziu; un script de colectare reîncearcă de câteva ori, cu pauze tot mai mari."},
    ],
}

sl("s13", "Cum arată o cerere", "Răspunsul începe cu un cod",
   "<h2>Răspunsul începe cu un cod</h2>"
   "<p class=\"cheie\">Clasa codului arată unde e problema: în cerere (4xx) sau la server (5xx). "
   "Un 2xx înseamnă reușită, dar nu garantează date; corpul se verifică separat.</p>"
   + ix("raspuns", "Cinci situații tipice ale aceleiași cereri", RASPUNS)
   + verif("c2-v8", 3,
           "Răspunsul are codul <code>429</code>. Ce înseamnă?",
           ["Adresa e greșită",
            "Serverul nu funcționează",
            "Lipsește cheia de acces",
            "Au fost trimise prea multe cereri într-un interval scurt"],
           "429 înseamnă depășirea limitei de cereri. Se reia mai rar: după pauza din "
           "<code>Retry-After</code>, iar la colectări mari, cu pauze care cresc după fiecare refuz."),
   manual=
   "<h2>Codurile de stare</h2>"
   "<p>Primul câmp al răspunsului e codul de stare, un număr de trei cifre. Prima cifră "
   "dă clasa: 2xx reușită, 3xx redirecționare, 4xx eroare a cererii, 5xx eroare a "
   "serverului. Codul se verifică înaintea corpului, pentru că la o eroare corpul poate fi "
   "o pagină HTML sau poate lipsi.</p>"
   + ix("raspuns", "Cinci situații tipice ale aceleiași cereri", RASPUNS)
   + tabel(["Cod", "Ce înseamnă", "Ce se face"], [
       ["~200", "cererea a reușit", "se citește corpul și se verifică numărul de valori primite"],
       ["~301 / 302", "resursa s-a mutat", "requests urmează automat redirecționarea"],
       ["~400", "cererea e greșită", "se verifică parametrii"],
       ["~401 / 403", "lipsește accesul", "cheie lipsă, greșită sau fără drepturi"],
       ["~404", "resursa nu există", "se verifică calea"],
       ["~429", "prea multe cereri", "se așteaptă (<code>Retry-After</code>) și se reia mai rar"],
       ["~500 / 503", "eroare la server", "se reia mai târziu"],
   ])
   + "<p>La 429 și 503, un script de colectare reîncearcă automat, cu pauze care cresc "
     "după fiecare refuz (de exemplu 1, 2, 4, 8 secunde). Strategia se numește "
     "<em>exponential backoff</em> și protejează atât colectarea, cât și serverul.</p>"
   + nota("Banca Mondială și codul 200",
          "La un parametru invalid, API-ul Băncii Mondiale răspunde cu 200 și pune eroarea în "
          "corp, sub cheia <code>message</code>. După cod se verifică și structura răspunsului.")
   + verif("c2-v8", 3,
           "Răspunsul are codul <code>429</code>. Ce înseamnă?",
           ["Adresa e greșită", "Serverul nu funcționează", "Lipsește cheia de acces",
            "Au fost trimise prea multe cereri într-un interval scurt"],
           "429 înseamnă depășirea limitei de cereri.")
   + surse("Documentație", [
       ("MDN: codurile de stare HTTP", "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status",
        "toate clasele și codurile"),
   ]))


# ===========================================================================
#  14-15. De unde vin datele
# ===========================================================================

_M = [  # familia, [deschis, cheie gratuită, cont/contract/plată]
    ("Statistici oficiale și date publice", ["Eurostat, Banca Mondială, data.gov.ro", "FRED (Rezerva Federală)", "microdate, cu acord de acces"]),
    ("Geospațiale", ["Eurostat GISCO, OpenStreetMap (cu limite de utilizare)", "Mapbox", "Google Maps Platform"]),
    ("Economice și financiare", ["BCE, portalul de date", "Alpha Vantage", "Bloomberg, Refinitiv"]),
    ("Sociale și web", ["Wikipedia (API MediaWiki)", "YouTube Data API, cu cotă zilnică", "X (Twitter) API"]),
    ("Senzori și IoT", ["Open-Meteo", "OpenWeatherMap", "platforme industriale de senzori"]),
    ("Servicii AI și cloud", ["", "Hugging Face, cu token", "OpenAI, Anthropic, AWS, Azure"]),
    ("Baze de date", ["Wikidata (SPARQL)", "Supabase, proiect gratuit", "baze gestionate în cloud"]),
]
SURSE_MATRICE = (
    '<div class="srs">'
    '<span class="srs__h" style="--c:var(--linie-2)">familia</span>'
    '<span class="srs__h" style="--c:var(--accent)">deschis, fără cheie</span>'
    '<span class="srs__h" style="--c:var(--ambra)">cheie gratuită, cu limite</span>'
    '<span class="srs__h" style="--c:var(--roza)">cont, contract sau plată</span>'
    + "".join(f'<span class="srs__f">{f}</span>' + "".join(
        f'<span class="srs__c{" noi" if (k == 0 and j == 0) else ""}">{c}</span>'
        for j, c in enumerate(cel)) for k, (f, cel) in enumerate(_M))
    + '</div><div class="srs__web"><b>Pagini web, prin extragere</b>'
    "<span>Când nu există API. Structura paginii se poate schimba oricând, iar condițiile de "
    "utilizare pot interzice extragerea.</span></div>")

sl("s14", "De unde vin datele", "Surse de date",
   "<h2>Surse de date</h2>"
   "<p class=\"cheie\">Două întrebări despre orice sursă: ce fel de date oferă și în ce condiții. "
   "Proiectul folosește statistici oficiale, deschise.</p>"
   + SURSE_MATRICE,
   manual=
   "<h2>Surse accesibile prin API</h2>"
   "<p>Aproape orice sursă de date importantă are azi un API. Pentru o analiză contează "
   "două lucruri: ce fel de date oferă sursa și în ce condiții se poate accesa. Condițiile se "
   "schimbă în timp, așa că se verifică în documentația fiecărei surse, la data colectării.</p>"
   + SURSE_MATRICE
   + "<p>Cheile de acces sunt personale. Nu se scriu în cod și nu se publică pe GitHub: se păstrează în "
     "variabile de mediu sau într-un fișier exclus prin <code>.gitignore</code>. Extragerea "
     "din pagini web (<em>web scraping</em>) e soluția pentru situațiile fără API, cu două "
     "riscuri: pagina se poate schimba fără avertisment, iar condițiile de utilizare pot "
     "interzice extragerea.</p>")

SURSE_TABEL = tabel(["Sursa", "Cum vine", "Ce ne dă"], [
    ["Social Connectedness Index", "fișier descărcat (HDX)", "legăturile dintre locuri; disponibil de la cursul 1"],
    ["Banca Mondială", "~API REST public", "indicatori pe țară și an"],
    ["Eurostat", "~API REST public", "indicatori pe regiuni NUTS"],
    ["<strong>Eurostat, migrație</strong>", "~migr_pop1ctz", "câți cetățeni ai unei țări trăiesc în alta"],
])
SURSE_DOC = surse("Documentația necesară", [
    ("Banca Mondială: structura unei cereri", "https://datahelpdesk.worldbank.org/knowledgebase/articles/898581",
     "țara, indicatorul, <code>format</code>, <code>date</code>, <code>per_page</code>, <code>page</code>"),
    ("Banca Mondială: despre API", "https://datahelpdesk.worldbank.org/knowledgebase/articles/889392-about-the-indicators-api",
     "ce date conține, cum se găsește codul unui indicator"),
    ("Eurostat: primii pași cu API-ul", "https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access/api-getting-started",
     "adresa de bază, primul exemplu, filtrele"),
    ("Eurostat: ghidul detaliat", "https://ec.europa.eu/eurostat/en/web/user-guides/data-browser/api-data-access/api-detailed-guidelines",
     "toți parametrii și formatele"),
    ("Eurostat: setul migr_pop1ctz", "https://ec.europa.eu/eurostat/databrowser/view/migr_pop1ctz/default/table",
     "dimensiunile, în browser"),
    ("JSON-stat: formatul", "https://json-stat.org/format/",
     "<code>id</code>, <code>size</code>, <code>dimension</code>, <code>value</code>"),
    ("requests: ghidul rapid", "https://requests.readthedocs.io/en/latest/user/quickstart/",
     "<code>get</code>, <code>params</code>, <code>status_code</code>, <code>json()</code>"),
    ("MDN: codurile de stare HTTP", "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status",
     "fiecare cod, de la 200 la 503"),
])

sl("s15", "De unde vin datele", "Sursele proiectului",
   "<h2>Sursele proiectului</h2>"
   '<div class="c2doi"><div>' + SURSE_TABEL
   + "<p>Întâi Banca Mondială, care are un format de răspuns simplu. Apoi Eurostat, cu indicatorii pe "
     "regiuni și cu migrația.</p>"
     "<p>Când o cerere eșuează, se consultă întâi documentația: acolo sunt parametrii și "
     "sensul lor.</p></div>"
   + "<div>" + SURSE_DOC + "</div></div>",
   manual=
   "<h2>Sursele proiectului</h2>"
   + SURSE_TABEL
   + "<p>Întâi Banca Mondială, care are un format de răspuns simplu, o listă de înregistrări. Apoi "
     "Eurostat, cu indicatorii pe regiuni și cu migrația, într-un format diferit, JSON-stat.</p>"
   + SURSE_DOC
   + "<p>Când o cerere eșuează, se consultă întâi documentația: acolo sunt descriși "
     "parametrii, valorile acceptate și sensul lor.</p>")


# ===========================================================================
#  16-18. requests
# ===========================================================================

HARTA_REQ = (
    '<div class="rqm">'
    '<span class="rqm__h">În mesajul HTTP</span><span class="rqm__h"></span><span class="rqm__h">În Python, cu requests</span>'
    '<div class="rqm__m" style="--c:var(--accent)">GET, adresa, parametrii<small>prima linie a cererii</small></div>'
    '<span class="rqm__s">→</span>'
    '<div class="rqm__p"><code>raspuns = requests.get(url, params=parametri, timeout=30)</code>'
    "<small>trimite cererea; <code>params</code> e dicționarul de filtre</small></div>"
    '<div class="rqm__m" style="--c:var(--text-3)">răspunsul întreg<small>tot ce vine înapoi</small></div>'
    '<span class="rqm__s">→</span>'
    '<div class="rqm__p"><code>raspuns</code><small>un obiect <code>Response</code></small></div>'
    '<div class="rqm__m" style="--c:var(--accent)">HTTP/1.1 200 OK<small>prima linie a răspunsului</small></div>'
    '<span class="rqm__s">→</span>'
    '<div class="rqm__p"><code>raspuns.status_code</code><small>200; se verifică primul</small></div>'
    '<div class="rqm__m" style="--c:var(--ambra)">Content-Type: application/json<small>antetele</small></div>'
    '<span class="rqm__s">→</span>'
    '<div class="rqm__p"><code>raspuns.headers["Content-Type"]</code><small>un dicționar cu antetele</small></div>'
    '<div class="rqm__m" style="--c:var(--ardezie)">[{"page": 1, …}, [{…}, {…}]]<small>corpul, text JSON</small></div>'
    '<span class="rqm__s">→</span>'
    '<div class="rqm__p"><code>raspuns.json()</code><small>liste și dicționare, ca în cursul 1</small></div>'
    '<div class="rqm__m" style="--c:var(--ambra)">…?format=json&amp;date=2022%3A2024<small>adresa construită</small></div>'
    '<span class="rqm__s">→</span>'
    '<div class="rqm__p"><code>raspuns.url</code><small>ce s-a cerut de fapt, după codificare</small></div>'
    "</div>")

DOC_REQ = surse("Documentația requests", [
    ("Ghidul rapid", "https://requests.readthedocs.io/en/latest/user/quickstart/",
     "cereri, parametri, răspunsuri, JSON, timeout"),
    ("Referința bibliotecii", "https://requests.readthedocs.io/en/latest/api/",
     "toți parametrii lui <code>get</code> și atributele lui <code>Response</code>"),
])

sl("s16", "requests", "Aceeași cerere, în Python",
   "<h2>Aceeași cerere, în Python</h2>"
   "<p class=\"cheie\">Ordinea e mereu aceeași: cererea, verificarea codului, abia apoi citirea datelor.</p>"
   + HARTA_REQ
   + '<div class="c2doi" style="margin-top:14px"><div>'
   + "<p><code>timeout=30</code>: fără el, o cerere la care serverul nu "
     "răspunde blochează programul. <code>requests</code> este deja instalat în mediul cursului, "
     "din <code>requirements.txt</code>.</p></div><div>"
   + DOC_REQ + "</div></div>",
   manual=
   "<h2>requests</h2>"
   "<p><code>requests</code> e biblioteca standard de facto pentru HTTP în Python. Fiecare "
   "parte a mesajului HTTP are în ea un corespondent direct.</p>"
   + HARTA_REQ
   + "<h3>Ordinea de lucru</h3>"
   "<p>Întâi se trimite cererea, apoi se verifică codul de stare și abia apoi se citește corpul. "
   "Dacă cererea nu a reușit, "
   "corpul poate fi o pagină HTML, iar <code>.json()</code> eșuează cu o eroare care pare "
   "să nu aibă legătură cu cauza reală. <code>raspuns.raise_for_status()</code> transformă "
   "orice cod 4xx sau 5xx într-o excepție, deci colectarea se oprește exact acolo unde apare problema.</p>"
   + ix("pas", "Prima cerere din caiet, pas cu pas", {
       "fisier": f"{CAIET} · 3. Banca Mondială: prima cerere",
       "intro": "Prima cerere din caiet: populația României, de la Banca Mondială.",
       "cod": "url = \"" + URL_BM + "\"\n"
              "parametri = {\"format\": \"json\", \"date\": \"2022:2024\", \"per_page\": 2, \"page\": 1}\n\n"
              "raspuns = requests.get(url, params=parametri)\n"
              "print(raspuns.url)\n"
              "print(raspuns.status_code)\n\n"
              "date = raspuns.json()\n"
              "meta = date[0]\nvalori = date[1]",
       "pasi": [
           {"l": 1, "set": {"url": {"t": "str", "v": URL_BM}},
            "txt": "Adresa: serverul, țara (RO) și indicatorul (populația totală)."},
           {"l": 2, "set": {"parametri": {"t": "dict", "v": {"format": "json", "date": "2022:2024", "per_page": 2, "page": 1}}},
            "txt": "Filtrele stau într-un dicționar. Doar 2 valori pe pagină, ca să se vadă paginarea."},
           {"l": 4, "set": {"raspuns": {"t": "Response", "v": "<Response [200]>"}},
            "txt": "<code>requests.get</code> trimite cererea; cu <code>params=</code>, biblioteca construiește adresa."},
           {"l": 5, "out": URL_BM + "?format=json&date=2022%3A2024&per_page=2&page=1",
            "txt": "Adresa construită: „:” a devenit <code>%3A</code>."},
           {"l": 6, "out": "200", "txt": "Codul de stare, verificat înaintea corpului."},
           {"l": 8, "set": {"date": {"t": "list", "v": [{"page": 1, "pages": 2, "per_page": 2, "total": 3}, ["…", "…"]]}},
            "txt": "<code>.json()</code> transformă corpul în liste și dicționare."},
           {"l": 9, "set": {"meta": {"t": "dict", "v": {"page": 1, "pages": 2, "per_page": 2, "total": 3}}}, "hl": {"var": "date", "k": 0},
            "txt": "Poziția 0: paginarea."},
           {"l": 10, "set": {"valori": {"t": "list", "v": ["2024: 19051804", "2023: 19061062"]}}, "hl": {"var": "date", "k": 1},
            "txt": "Poziția 1: valorile de pe pagina aceasta."},
       ]})
   + DOC_REQ)

R_JSON = [
    {"page": 1, "pages": 2, "per_page": 2, "total": 3, "sourceid": "2", "lastupdated": "2026-10-08"},
    [{"indicator": {"id": "SP.POP.TOTL", "value": "Population, total"},
      "country": {"id": "RO", "value": "Romania"}, "countryiso3code": "ROU",
      "date": "2024", "value": 19051804, "unit": "", "obs_status": "", "decimal": 0},
     {"indicator": {"id": "SP.POP.TOTL", "value": "Population, total"},
      "country": {"id": "RO", "value": "Romania"}, "countryiso3code": "ROU",
      "date": "2023", "value": 19061062, "unit": "", "obs_status": "", "decimal": 0}],
]
JUPYTER = {
    "id": "c2-cerere",
    "celula": "url = \"" + URL_BM + "\"\n"
              "parametri = {\"format\": \"json\", \"date\": \"2022:2024\", \"per_page\": 2}\n"
              "raspuns = requests.get(url, params=parametri, timeout=30)",
    "loc": "raspuns.status_code",
    "taie": 240,
    "env": {
        "url": URL_BM,
        "parametri": {"format": "json", "date": "2022:2024", "per_page": 2},
        "raspuns": {"__py": "Response", "__cls": "requests.models.Response", "__repr": "<Response [200]>",
                    "__attr": {"status_code": 200, "ok": True, "reason": "OK",
                               "url": URL_BM + "?format=json&date=2022%3A2024&per_page=2",
                               "headers": {"Content-Type": "application/json;charset=utf-8"}},
                    "__met": {"json": R_JSON}},
    },
    "tinte": [
        {"t": "Codul de stare al răspunsului", "v": 200,
         "ind": "Un atribut al lui <code>raspuns</code>, fără paranteze; numele lui începe cu <code>status</code>."},
        {"t": "Câte valori există în total", "v": 3,
         "ind": "<code>raspuns.json()</code> e o listă; paginarea e primul element, la poziția 0, iar numărul stă la cheia <code>\"total\"</code>."},
        {"t": "Populația României în 2024", "v": 19051804,
         "ind": "Valorile sunt al doilea element al listei; prima înregistrare e 2024, iar numărul stă la cheia <code>\"value\"</code>."},
    ],
}

sl("s17", "requests", "Exercițiu: inspectarea răspunsului",
   "<h2>Exercițiu: inspectarea răspunsului</h2>"
   + ix("jupyter", "Trei lucruri de aflat din raspuns", JUPYTER,
        "Prima celulă e rulată. Scrie expresii în consolă și apasă Enter, ca în Jupyter."),
   manual=
   "<h2>Exercițiu: inspectarea răspunsului</h2>"
   "<p>Celula de mai jos e cea din caiet, deja rulată. Răspunsul se află în <code>raspuns</code>; "
   "consola funcționează ca o celulă Jupyter. Sunt trei valori de aflat, toate obținute prin cod, "
   "nu transcrise manual.</p>"
   + ix("jupyter", "Trei lucruri de aflat din raspuns", JUPYTER)
   + "<p>Se poate lucra și cu o variabilă intermediară: <code>date = raspuns.json()</code>, "
     "apoi <code>date[0][\"total\"]</code>. Aceeași structură, o listă cu paginarea și cu "
     "valorile, apare la toți indicatorii Băncii Mondiale.</p>")

PREZICE_PAGINI = {
       "id": "c2-prezice-pagini", "fisier": f"{CAIET} · 4. Paginarea",
       "cod": "date = raspuns.json()\n"
              "meta, valori = date[0], date[1]\n\n"
              "# meta = {\"page\": 1, \"pages\": 4, \"per_page\": 50, \"total\": 180}\n"
              "print(meta[\"total\"], len(valori))",
       "intrebare": "Ce afișează?",
       "variante": ["180 180", "180 50", "50 180", "4 50"],
       "corect": 1,
       "indiciu": "total numără toate valorile; len(valori) numără câte au venit pe pagina aceasta.",
       "laBine": "Pe prima pagină au venit 50 din 180 de valori; mai sunt trei pagini de cerut.",
       "explicatie": "În total sunt 180 de valori, câte 50 pe pagină, pe 4 pagini; pe pagina 1 au "
                     "venit 50. Se cer fie paginile pe rând, până la <code>pages</code>, fie "
                     "<code>per_page=1000</code> dintr-odată."}

PAGINI = {"ani": list(range(2024, 1959, -1)), "optiuni": [10, 50, 1000], "implicit": 50}

sl("s18", "requests", "Paginarea",
   "<h2>Paginarea</h2>"
   "<p class=\"cheie\">Un răspuns mare vine pe pagini. Primul element spune câte valori "
   "există și câte pagini sunt; restul e pagina cerută.</p>"
   + ix("pagini", "Populația României, 1960 la 2024: 65 de valori", PAGINI)
   + '<div class="c2-idei"><p><b>Pagină cu pagină:</b> se cer <code>page=1, 2, …</code> până la '
     "<code>pages</code>.</p><p><b>O singură pagină mare:</b> se cere <code>per_page=1000</code> și "
     "se verifică faptul că <code>pages</code> e 1. Așa procedează caietul.</p></div>"
   + ix("prezice", "Câte valori au venit", PREZICE_PAGINI),
   manual=
   "<h2>Paginarea</h2>"
   "<p>Un API nu trimite un set mare dintr-o dată. Trimite o pagină și, separat, informația "
   "de paginare: pagina curentă, numărul de pagini, câte valori pe pagină și câte în total. "
   "La Banca Mondială, informația aceasta e primul element al listei din răspuns.</p>"
   + ix("pagini", "Populația României, 1960 la 2024: 65 de valori", PAGINI)
   + "<p>Sunt două strategii. Prima cere pagină după pagină, până la ultima; e singura "
     "posibilă când API-ul limitează <code>per_page</code>. A doua cere o pagină destul de "
     "mare încât să încapă totul și verifică apoi că a venit o singură pagină; caietul "
     "folosește a doua. Banca Mondială întoarce valorile de la anul cel mai recent spre cel "
     "mai vechi.</p>"
   + ix("prezice", "Câte valori au venit", PREZICE_PAGINI)
   + ix("pas", "Unde e a treia valoare", {
       "fisier": f"{CAIET} · 4. Paginarea",
       "intro": "Trei ani ceruți, câte două valori pe pagină.",
       "cod": "print(\"Pagina\", meta[\"page\"], \"din\", meta[\"pages\"], \"· valori în total:\", meta[\"total\"])\n\n"
              "parametri[\"page\"] = 2\n"
              "pagina2 = requests.get(url, params=parametri).json()\n"
              "pagina2[1]",
       "pasi": [
           {"l": 1, "out": "Pagina 1 din 2 · valori în total: 3",
            "txt": "Pagina 1 din 2; în total 3 valori, dintre care au venit 2."},
           {"l": 3, "set": {"parametri": {"t": "dict", "v": {"format": "json", "date": "2022:2024", "per_page": 2, "page": 2}}},
            "hl": {"var": "parametri", "k": "page"}, "txt": "Se schimbă o singură cheie: <code>page</code>."},
           {"l": 4, "set": {"pagina2": {"t": "list", "v": [{"page": 2, "pages": 2, "per_page": 2, "total": 3}, ["2022: 19048502"]]}},
            "txt": "Aceeași cerere, pagina 2."},
           {"l": 5, "out": "[{…, 'date': '2022', 'value': 19048502, …}]", "hl": {"var": "pagina2", "k": 1},
            "txt": "A treia valoare: 2022."},
       ]})
   + "<h3>Scriptul complet, cu buclă</h3>"
   "<pre><code>import time\n"
   "import pandas as pd\n"
   "import requests\n\n"
   "def aduce(url, parametri):\n"
   "    pagina, toate = 1, []\n"
   "    while True:\n"
   "        r = requests.get(url, params={**parametri, \"page\": pagina}, timeout=30)\n"
   "        r.raise_for_status()\n"
   "        meta, valori = r.json()\n"
   "        toate.extend(valori or [])\n"
   "        if pagina >= meta[\"pages\"]:\n"
   "            return toate\n"
   "        pagina += 1\n"
   "        time.sleep(0.5)</code></pre>"
   "<h3>Din JSON în tabel</h3>"
   "<p>Lista de înregistrări devine tabel cu <code>pd.json_normalize</code>: dicționarele "
   "dinăuntru devin coloane cu punct în nume, de exemplu <code>country.id</code>. Tabelul se "
   "salvează în <code>data/c2</code> cu <code>index=False</code>, ca să nu se adauge o coloană "
   "de numerotare inutilă. Calea pornește din folderul caietului, deci fișierul ajunge în "
   "<code>dsw/curs/data/c2/</code>.</p>"
   "<pre><code>tabel = pd.json_normalize(valori)[[\"country.id\", \"date\", \"value\"]]\n"
   "tabel.to_csv(\"data/c2/populatie_ro.csv\", index=False)</code></pre>"
   + nota("Fișierul brut nu se modifică",
          "Ce vine de la API se salvează o dată și nu se mai editează. Curățarea, la cursul 4, "
          "scrie fișiere noi, alături. Așa se poate reface oricând drumul de la sursă la tabelul final."))


# ===========================================================================
#  19-20. Eurostat
# ===========================================================================

EUROSTAT_BAZA = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
DIMENSIUNI = [
    ("freq", "frecvența", ["A"], "A", "fix"),
    ("citizen", "cetățenia", ["BG", "PL", "RO", "…"], None, "des"),
    ("age", "vârsta", ["TOTAL", "Y15-64", "…"], "TOTAL", "fix"),
    ("sex", "sexul", ["T", "M", "F"], "T", "fix"),
    ("unit", "unitatea", ["NR"], "NR", "fix"),
    ("geo", "țara de reședință", ["DE", "ES", "IT", "…"], None, "des"),
    ("time", "anul", ["2024", "2023", "…"], "2024", "fix"),
]
EUROSTAT_CERERE = (
    '<div class="eus__adr">'
    f'<div class="eus__t" style="--c:var(--roza)"><code>{EUROSTAT_BAZA}</code><span>baza</span></div>'
    '<div class="eus__t" style="--c:var(--accent)"><code>migr_pop1ctz</code><span>setul</span></div>'
    '<div class="eus__t" style="--c:var(--ambra)"><code>?sex=T&amp;age=TOTAL&amp;unit=NR&amp;time=2024</code><span>felia</span></div>'
    "</div>"
    '<div class="eus__dim">'
    + "".join(
        f'<div class="eus__d {st}" style="--c:var(--{"ambra" if st == "fix" else "accent"})"><b>{i}</b><small>{n}</small>'
        + "".join(f'<span class="{"ales" if c == a else ""}">{c}</span>' for c in cod)
        + f'<em>{"fixată" if st == "fix" else "rămâne deschisă"}</em></div>'
        for i, n, cod, a, st in DIMENSIUNI)
    + "</div>")

sl("s19e", "Eurostat", "Eurostat: structura cererii",
   "<h2>Eurostat: structura cererii</h2>"
   "<p class=\"cheie\">La Banca Mondială, calea indică ce se cere. La Eurostat, calea indică setul, "
   "iar parametrii aleg felia: unele dimensiuni se fixează, celelalte rămân deschise.</p>"
   + EUROSTAT_CERERE
   + '<div class="c2-idei"><p><b>Ce rămâne deschis devine cubul:</b> aici cetățenia × țara de '
     "reședință, adică perechi de țări.</p><p><b>Codul setului și dimensiunile</b> se văd în "
     '<a class="leg" href="https://ec.europa.eu/eurostat/databrowser/view/migr_pop1ctz/default/table" '
     'target="_blank" rel="noopener">Data Browser</a>, înainte de a le cere din cod.</p></div>',
   manual=
   "<h2>Eurostat: cererea pe dimensiuni</h2>"
   "<p>Un set Eurostat e un tabel cu mai multe dimensiuni: frecvența, regiunea, anul, "
   "sexul, vârsta, unitatea și altele, după set. O cerere fixează unele dimensiuni la o "
   "singură valoare și le lasă deschise pe celelalte. Ce rămâne deschis formează cubul "
   "din răspuns.</p>"
   + EUROSTAT_CERERE
   + "<p>Eurostat oferă mai multe API-uri: Statistics API, care răspunde în JSON-stat și "
     "pe care îl folosim, și API-urile SDMX 2.1 și SDMX 3.0, pentru schimbul standardizat "
     "între instituții. Codul unui set și codurile dimensiunilor lui se găsesc în Data "
     "Browser, unde tabelul se poate vedea înainte de a fi cerut din cod.</p>"
   + "<p>Caietul pornește cu un exemplu mai mic: densitatea populației în județele Cluj "
     "(<code>RO113</code>) și Bihor (<code>RO111</code>), din setul <code>demo_r_d3dens</code>. "
     "Exemplul arată un detaliu important: răspunsul nu păstrează ordinea cerută. Bihorul "
     "vine pe poziția 0, deși a fost cerut al doilea, deci pozițiile se citesc din "
     "<code>index</code>, nu se presupun.</p>")

CUB = {
    "randuri": {"id": "citizen", "coduri": ["BG", "PL", "RO"], "nume": ["Bulgaria", "Polonia", "România"]},
    "coloane": {"id": "geo", "coduri": ["DE", "ES", "IT"], "nume": ["Germania", "Spania", "Italia"]},
    "valori": [371128, 112834, 48659, 741784, 59132, 73320, 776424, 620463, 1073196],
    "ales": [2, 2],
}

PREZICE_CUB = {
       "id": "c2-prezice-cub2", "fisier": f"{CAIET} · 6.1. Cum citim JSON-stat",
       "cod": "citizen = [\"BG\", \"PL\", \"RO\"]\n"
              "geo     = [\"DE\", \"ES\", \"IT\"]\n"
              "value   = [371128, 112834, 48659, 741784, 59132, 73320, 776424, 620463, 1073196]\n\n"
              "i = citizen.index(\"PL\") * 3 + geo.index(\"ES\")\n"
              "print(i, value[i])",
       "intrebare": "Ce afișează?",
       "variante": ["4 59132", "2 48659", "3 741784", "5 73320"],
       "corect": 0,
       "indiciu": "citizen.index(\"PL\") e 1, geo.index(\"ES\") e tot 1. Câte valori are un rând de cetățenie?",
       "laBine": "Același calcul îl face, pentru fiecare valoare, funcția jsonstat_in_tabel din caiet.",
       "explicatie": "Fiecare cetățenie are 3 valori, câte una pentru fiecare țară. Polonia e a doua "
                     "cetățenie (poziția 1), deci se trece peste 1 × 3 = 3 valori; Spania e a doua țară "
                     "(poziția 1): 3 + 1 = 4. <code>value[4]</code> e 59.132."}

sl("s20", "Eurostat", "Cubul JSON-stat",
   "<h2>Cubul JSON-stat</h2>"
   "<p class=\"cheie\">Codurile se scriu o singură dată, cu poziția lor; valorile stau pe un "
   "singur rând, iar ultima dimensiune se schimbă cel mai repede, ca secundele la ceas.</p>"
   + ix("cub", "Migrația, 2024: trei cetățenii, trei țări", CUB)
   + nota("Un rând, o pereche de țări",
          "Ca la SCI, date diadice, dar cu direcție: românii din Italia nu sunt italienii din "
          "România. O valoare care lipsește nu apare deloc în <code>value</code>; nu înseamnă zero.", True),
   manual=
   "<h2>Cubul JSON-stat</h2>"
   "<p>Banca Mondială trimite o listă de înregistrări, din care tabelul se face direct. "
   "Eurostat trimite JSON-stat, un format pentru tabele cu multe dimensiuni. În loc să "
   "repete codurile pe fiecare rând, le scrie o singură dată, cu poziția lor, iar valorile "
   "le pune pe un singur rând, în ordinea în care ultima dimensiune se schimbă cel mai "
   "repede.</p>"
   + ix("cub", "Migrația, 2024: trei cetățenii, trei țări", CUB)
   + tabel(["Cheie", "Ce conține"], [
       ["~id", "numele dimensiunilor, în ordine"],
       ["~size", "câte coduri are fiecare dimensiune"],
       ["~dimension", "codurile fiecărei dimensiuni și poziția lor (<code>index</code>)"],
       ["~value", "valorile, după poziție; ce lipsește nu apare deloc"],
       ["~status", "indicatorii de stare ai valorilor, unde există"],
   ])
   + "<p>Cu două dimensiuni, poziția e <code>i_citizen × 3 + i_geo</code>. Cu șapte "
     "dimensiuni regula e aceeași, doar mai lungă, de aceea e scrisă o dată, în funcția "
     "<code>jsonstat_in_tabel</code> din caiet, iar <code>cere_eurostat</code> face cererea "
     "și desfacerea împreună.</p>"
   + ix("prezice", "Poziția din cub", PREZICE_CUB)
   + "<h3>Migrația, a doua sursă a proiectului</h3>"
   "<p>Setul <code>migr_pop1ctz</code> spune câți oameni cu o anumită cetățenie trăiesc într-o "
   "țară, la 1 ianuarie. Un rând e o pereche de țări, ca la SCI, dar cu direcție. Cetățenia "
   "e preferată țării nașterii (<code>migr_pop3ctb</code>) pentru că mai multe țări mari, "
   "printre ele Germania, nu raportează nașterile pe țări. Și cetățenia are o limită: persoanele "
   "care au dobândit cetățenia țării de reședință nu mai apar ca migranți.</p>"
   "<p>Doar o parte dintre țări raportează pe țări de cetățenie; o valoare lipsă nu "
   "înseamnă zero. Harta din <a class=\"leg\" href=\"../../c1-introducere-si-mediu/tutorial/#s5m\">cursul 1</a> "
   "folosește exact aceste date: 1.073.196 de cetățeni români în Italia, la 1 ianuarie 2024. "
   "Aceasta este întrebarea empirică a semestrului: Italia, țara cu cei mai mulți cetățeni români, e abia a "
   "șasea după indicele SCI.</p>"
   + ix("pas", "Câți români în Italia", {
       "fisier": f"{CAIET} · 8. Migrația: două țări pe un rând",
       "intro": "Migrația: câți oameni cu o cetățenie trăiesc în fiecare țară.",
       "cod": "parametri = {\"sex\": \"T\", \"age\": \"TOTAL\", \"unit\": \"NR\", \"time\": 2024}\n"
              "migratie = cere_eurostat(\"migr_pop1ctz\", parametri)\n\n"
              "in_italia = migratie[\"geo\"] == \"IT\"\n"
              "romani = migratie[\"citizen\"] == \"RO\"\n"
              "migratie[in_italia & romani]",
       "pasi": [
           {"l": 1, "set": {"parametri": {"t": "dict", "v": {"sex": "T", "age": "TOTAL", "unit": "NR", "time": 2024}}},
            "txt": "Dimensiunile fixate: toată populația, în număr de persoane, în 2024."},
           {"l": 2, "set": {"migratie": {"t": "DataFrame", "v": {"cols": ["geo", "citizen", "valoare"],
                                                               "rows": [["DE", "BG", 371128], ["ES", "RO", 620463], ["IT", "RO", 1073196], ["…", "…", "…"]],
                                                               "nota": "un rând pe pereche cetățenie, țară"}}},
            "txt": "<code>cere_eurostat</code> face cererea și desface cubul în tabel."},
           {"l": 4, "set": {"in_italia": {"t": "Series", "v": {"rows": [["0", "False"], ["1", "False"], ["2", "True"], ["…", "…"]]}}},
            "txt": "Prima condiție: trăiesc în Italia."},
           {"l": 5, "set": {"romani": {"t": "Series", "v": {"rows": [["0", "False"], ["1", "True"], ["2", "True"], ["…", "…"]]}}},
            "txt": "A doua condiție: au cetățenie română."},
           {"l": 6, "out": "     geo citizen  valoare\n4812  IT      RO  1073196",
            "txt": "<code>&amp;</code> păstrează rândurile unde ambele sunt adevărate."},
       ]})
   + nota("Coduri care pot produce erori",
          "Eurostat scrie Grecia <code>EL</code>, nu <code>GR</code>. Iar <code>NA</code> e Namibia, pe "
          "care pandas o interpretează implicit ca valoare lipsă. Se reiau la curățare, la cursul 4."))


sl("s20v", "Eurostat", "Poziția din cub",
   "<h2>Poziția din cub</h2>"
   "<p class=\"cheie\">Aceeași regulă, scrisă în Python: poziția e indexul cetățeniei "
   "înmulțit cu numărul de țări, plus indexul țării.</p>"
   + ix("prezice", "Poziția din cub", PREZICE_CUB),
   manual="")


# ===========================================================================
#  21-22. Proiectul
# ===========================================================================

DOVADA = {
    "id": "c2-dovada-colectare",
    "sarcina": "Rulează în caietul 02, după secțiunea 5, cele două celule de mai jos și lipește ce afișează.",
    "pasi": [
        {"t": "Indicatorul a venit pe o singură pagină",
         "cmd": "tabel = cere_bm(\"SP.POP.TOTL\", TARI)",
         "gol": "lipește linia cu numărul de pagini",
         "cauta": r"pagini:\s*1\b",
         "daca_nu": "Se așteaptă „pagini: 1”. Mai multe pagini înseamnă că per_page e prea mic; o eroare "
                    "înseamnă, de obicei, că celulele de deasupra nu au rulat."},
        {"t": "Tabelul s-a scris în data/c2, cu rânduri în el",
         "cmd": "len(pd.read_csv(\"data/c2/bm.csv\"))",
         "gol": "numărul de rânduri",
         "cauta": r"\b[1-9]\d{0,4}\b",
         "daca_nu": "Se așteaptă un număr mai mare decât zero. FileNotFoundError înseamnă că celula care salvează "
                    "nu a rulat sau că acest caiet nu se află în dsw/curs/."}],
    "explicatie": "Cererile au reușit, iar datele sunt salvate în curs/data/c2, lângă celulele care le refac.",
}
PASI_COLECTARE = tabel(["Pasul", "Ce faci"], [
    ["1", "deschizi caietul 02 din <code>dsw/curs/</code>, cu kernelul <code>.venv</code>"],
    ["2", "rulezi secțiunile 1 la 5: prima cerere, paginarea, cei trei indicatori"],
    ["3", "verifici că fiecare indicator a venit pe o singură pagină"],
    ["4", "salvezi tabelul în <code>data/c2/bm.csv</code>"],
])

sl("s21", "Proiectul tău", "Prima colectare",
   "<h2>Prima colectare, în caiet</h2>"
   '<div class="c2doi"><div>'
   "<p>Caietul cere, verifică și salvează datele. Rulează-l și lipește rezultatul afișat.</p>"
   + PASI_COLECTARE + "</div><div>"
   + ix("dovada", "Dovada colectării", DOVADA) + "</div></div>",
   manual=
   "<h2>Prima colectare, în caiet</h2>"
   "<p>Colectarea se face în caietul 02, din <code>dsw/curs/</code>. Căile pornesc de acolo: "
   "<code>data/c2/bm.csv</code> înseamnă <code>dsw/curs/data/c2/bm.csv</code>. Folderul este creat de "
   "prima celulă a caietului, cu <code>Path(\"data/c2\").mkdir(exist_ok=True)</code>.</p>"
   + PASI_COLECTARE
   + "<p>Mai jos, aceeași idee, scrisă complet, cu paginarea tratată pas cu pas: o funcție care "
   "cere pagină după pagină, până la ultima. Se poate rula într-o celulă nouă, la finalul "
   "caietului, și se adaptează la indicatorul echipei.</p>"
   + "<pre><code>import time\n"
     "import pandas as pd\n"
     "import requests\n\n"
     "URL = \"" + URL_BM + "\"\n\n"
     "def aduce(url, parametri):\n"
     "    pagina, toate = 1, []\n"
     "    while True:\n"
     "        r = requests.get(url, params={**parametri, \"page\": pagina}, timeout=30)\n"
     "        print(\"pagina\", pagina, \"cod\", r.status_code)\n"
     "        r.raise_for_status()\n"
     "        meta, valori = r.json()\n"
     "        toate.extend(valori or [])\n"
     "        if pagina >= meta[\"pages\"]:\n"
     "            return toate\n"
     "        pagina += 1\n"
     "        time.sleep(0.5)\n\n"
     "randuri = aduce(URL, {\"format\": \"json\", \"date\": \"2000:2023\", \"per_page\": 100})\n"
     "tabel = pd.json_normalize(randuri)\n"
     "tabel.to_csv(\"data/c2/populatie_ro.csv\", index=False)\n"
     "print(\"salvate\", len(tabel), \"rânduri\")</code></pre>"
   + nota("Ce rămâne local și ce ajunge în depozitul echipei",
          "Datele și caietele de la curs rămân în <code>curs/</code>. În depozitul echipei, "
          "<code>proiect/</code>, ajunge munca echipei. Acolo nu se publică fișierele mari și cheile de "
          "acces: pentru datele de zeci de megabytes se publică doar codul care le colectează.")
   + ix("dovada", "Dovada colectării", DOVADA))


ARBORE_PROIECT = (
    '<span class="a">dsw/</span>\n'
    '├── <span class="x">.venv/</span>\n'
    '├── curs/            <span class="c"># al tău, fără Git</span>\n'
    '└── <span class="a">proiect/</span>         <span class="c"># al echipei, cu Git</span>\n'
    '    ├── .git/        <span class="c"># istoricul</span>\n'
    '    └── README.md')

PASI_ECHIPA = (
    '<ol class="venvp__pasi">'
    "<li><b>Echipa de cinci primește un depozit</b> al ei, în organizația "
    f'<a class="leg" href="https://github.com/{REPO_ORG}" target="_blank" rel="noopener">{REPO_ORG}</a>, '
    "pornit din același șablon pentru toate echipele.</li>"
    "<li><b>Accepți invitația</b> de pe GitHub, primită pe e-mail, pentru dreptul de scriere în depozit.</li>"
    "<li><b>Copiezi adresa depozitului</b>: pe pagina lui, <em>Code → HTTPS</em>.</li>"
    "<li><b>În terminalul din VS Code</b>, în <code>dsw</code>:<br>"
    "<code>git clone &lt;adresa&gt; proiect</code>"
    '<span class="venvp__os">ultimul cuvânt e numele folderului: proiect</span></li>'
    "</ol>")

sl("s21e", "Proiectul tău", "Depozitul echipei",
   "<h2>Depozitul echipei, în dsw/proiect</h2>"
   "<p class=\"cheie\">O singură comandă, o singură dată. Munca echipei stă în "
   "<code>proiect/</code>; exercițiile de la curs rămân în <code>curs/</code>.</p>"
   '<div class="c2doi"><div>' + PASI_ECHIPA + "</div><div>"
   '<div class="venvp__fld">' + ARBORE_PROIECT + "</div>"
   + nota("Git", "Trebuie să fie instalat: <code>git --version</code> afișează un număr de versiune. La prima "
          "clonare, Git poate cere autentificarea în contul GitHub, într-o fereastră din browser. Lucrul "
          "în <code>proiect/</code> continuă la cursul 3.")
   + "</div></div>",
   manual=
   "<h2>Depozitul echipei, în dsw/proiect</h2>"
   "<p>Până acum, tot ce s-a lucrat se află în <code>curs/</code>, pe calculatorul personal, fără Git. "
   "Proiectul de semestru funcționează diferit: la el lucrează cinci persoane, iar fiecare trebuie să "
   "vadă ce au făcut ceilalți. De aceea fiecare echipă are un depozit al ei pe GitHub, în organizația "
   f'<a class="leg" href="https://github.com/{REPO_ORG}" target="_blank" rel="noopener">{REPO_ORG}</a>, '
   "pornit din același șablon pentru toate echipele, iar fiecare membru îl clonează pe calculatorul propriu, "
   "în <code>dsw/proiect</code>.</p>"
   + PASI_ECHIPA
   + '<div class="venvp__fld" style="margin:14px 0">' + ARBORE_PROIECT + "</div>"
   + "<p><code>git clone</code> copiază depozitul cu tot cu istoricul lui, în folderul <code>.git/</code>, "
   "și reține adresa de la care a fost copiat. Ultimul cuvânt din comandă e numele folderului: fără el, "
   "folderul ar purta numele depozitului. Comanda se dă o singură dată, din <code>dsw</code>; dacă e dată "
   "din alt folder, de exemplu din <code>curs/</code>, depozitul ajunge acolo, iar căile din caiete nu "
   "mai sunt cele din manual.</p>"
   + nota("Git",
          'Se instalează de pe <a class="leg" href="https://git-scm.com/downloads" target="_blank" '
          'rel="noopener">git-scm.com</a>; instalarea se verifică cu <code>git --version</code>. La prima '
          "clonare, Git poate cere autentificarea în contul GitHub, într-o fereastră din browser. Commit, push și "
          "lucrul pe ramuri, în <code>proiect/</code>, sunt la cursul 3."))


sl("s22", "Mai departe", "Pentru cursul următor",
   "<h2>Cursul 3: versionare și colaborare</h2>"
   "<ul>"
   "<li>Git în <code>proiect/</code>: istoricul și lucrul în echipă</li>"
   "<li>pregătirea și explorarea datelor colectate</li>"
   "<li>cadrul teoretic al proiectului</li>"
   "<li>tema echipei și împărțirea sarcinilor</li>"
   "</ul>"
   + nota("De făcut până atunci",
          "Caietul 02 rulat, cu <code>bm.csv</code> și <code>migratie.csv</code> în "
          "<code>curs/data/c2</code>. Depozitul echipei, clonat în <code>dsw/proiect</code>. Fișa "
          "echipei de la finalul caietului, completată: direcția provizorie și indicatorul încercat.", True))


if __name__ == "__main__":
    L.scrie_tot()
