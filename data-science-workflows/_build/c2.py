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
    ("Ce este un API", "Un intermediar cu un contract; motivele colectării prin API și costurile ei."),
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
   + '<p class="c2__jos">Caietul lecției: <code>02_colectarea_datelor_prin_api.ipynb</code>, în dsw/curs/, lângă caietul 01.</p>',
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
   "<p>Capitolul urmează ordinea de la curs. Codul complet se află în caietul cursului; "
   "capitolul de față prezintă conceptele, motivele și capcanele.</p>"
   + ix("agenda", "Planul lecției", AGENDA_IX)
   + nota("Caietul lecției", CAIET_NOTA, True))

sl("s2", "Cursul", "Punctul de plecare",
   "<h2>Punctul de plecare</h2>"
   "<p class=\"cheie\">Ce trebuie să existe înainte de prima cerere.</p>"
   '<ul class="bif">'
   "<li><b>Folderul <code>dsw</code></b><span>cu mediul <code>.venv</code> și pachetele din "
   "<code>requirements.txt</code>; caietul 01 rulează de sus până jos.</span></li>"
   "<li><b>Caietul 02</b><span>descărcat separat, în <code>dsw/curs/</code>, lângă caietul 01.</span></li>"
   "<li><b>Git</b><span>instalat; la finalul orei se clonează depozitul echipei.</span></li>"
   "<li><b>Contul GitHub</b><span>cel folosit pe site de la cursul 1.</span></li>"
   "</ul>",
   manual=
   "<h2>Punctul de plecare</h2>"
   "<p>Lecția pornește de la ce s-a construit la cursul 1: folderul cursului, <code>dsw</code>, "
   "cu mediul virtual <code>.venv</code> și pachetele din <code>requirements.txt</code>, și caietul 01 "
   "rulat de sus până jos. Dacă lipsește ceva, "
   "pașii sunt în <a class=\"leg\" href=\"../../c1-introducere-si-mediu/tutorial/\">manualul "
   "cursului 1</a>. Echipele de cinci se formează în această lecție, pe site; la finalul orei, "
   "fiecare echipă își clonează depozitul, iar direcția proiectului se alege la cursul 3.</p>"
   "<p>Caietul lecției se descarcă separat, nu odată cu toată arhiva: pe "
   f'<a class="leg" href="{repo_fisier("curs/" + CAIET)}" target="_blank" rel="noopener">pagina lui de pe GitHub</a> '
   "se alege <em>Download raw file</em>, iar fișierul se salvează în <code>dsw/curs/</code>, lângă caietul 01. "
   "Arhiva întreagă, despachetată din nou peste <code>dsw</code>, ar putea suprascrie caietele deja completate.</p>"
   "<p>Biblioteca folosită în această lecție, <code>requests</code>, este deja în mediu, din <code>requirements.txt</code>. "
   "Dacă lipsește, cu mediul activ:</p>"
   "<pre><code>pip install -r requirements.txt</code></pre>")


# ===========================================================================
#  3-4. Ce este un API
# ===========================================================================

_CER = "GET /v2/country/RO/indicator/SP.POP.TOTL?date=2024"

# Pe slide: un singur desen. Sus restaurantul, jos API-ul, aceleași cinci locuri,
# una sub alta. În dreapta, partea furnizorului, pe care clientul nu o vede.
def _ic(k, x, y, cls):
    """Pictograme simple, din linii; (x, y) este centrul."""
    g = f'<g class="rst2__ic {cls}" transform="translate({x - 22},{y - 22})">'
    d = {
        "client": '<circle cx="22" cy="12" r="7"/><path d="M8 40c0-9 6-15 14-15s14 6 14 15"/>',
        "meniu": '<rect x="11" y="4" width="22" height="36" rx="2"/><path d="M16 13h12M16 20h12M16 27h8"/>',
        "ospatar": '<circle cx="18" cy="11" r="6"/><path d="M7 40c0-8 5-14 11-14 4 0 7 2 9 5"/><path d="M26 22h16M30 22c0-4 2-6 4-6s4 2 4 6"/>',
        "bucatarie": '<path d="M8 22h28v12a6 6 0 0 1-6 6H14a6 6 0 0 1-6-6z"/><path d="M4 22h36"/><path d="M16 15c0-3 3-3 3-6M24 15c0-3 3-3 3-6"/>',
        "camara": '<path d="M6 6h32v34H6zM6 18h32M6 30h32"/><path d="M12 14v-4M18 14v-4M14 26v-4M26 26v-4M32 26v-4M20 38v-4"/>',
        "script": '<path d="M10 4h17l8 8v28H10z"/><path d="M27 4v8h8"/><path d="M19 22l-4 4 4 4M26 22l4 4-4 4"/>',
        "doc": '<path d="M8 8c5-3 10-3 14 0v32c-4-3-9-3-14 0zM36 8c-5-3-10-3-14 0v32c4-3 9-3 14 0z"/>',
        "api": '<rect x="8" y="6" width="28" height="34" rx="2"/><path d="M14 23h14M24 18l5 5-5 5"/>',
        "server": '<rect x="8" y="6" width="28" height="10" rx="2"/><rect x="8" y="18" width="28" height="10" rx="2"/><rect x="8" y="30" width="28" height="10" rx="2"/><path d="M13 11h2M13 23h2M13 35h2"/>',
        "bd": '<ellipse cx="22" cy="10" rx="13" ry="5"/><path d="M9 10v24c0 3 6 5 13 5s13-2 13-5V10M9 22c0 3 6 5 13 5s13-2 13-5"/>',
    }[k]
    return g + d + "</g>"


def _restaurant_svg():
    X = [215, 395, 575, 760, 905]
    SUS = [("client", "Clientul", "comandă"), ("meniu", "Meniul", "ce se poate cere"),
           ("ospatar", "Ospătarul", "duce comanda"), ("bucatarie", "Bucătăria", "pregătește felul"),
           ("camara", "Cămara", "ingredientele")]
    JOS = [("script", "Scriptul", "codul clientului"), ("doc", "Documentația", "ce se poate cere"),
           ("api", "API-ul", "singura intrare"), ("server", "Serverul", "aplicația furnizorului"),
           ("bd", "Baza de date", "datele furnizorului")]
    o = ['<svg class="rst2" viewBox="0 0 980 298" role="img" aria-label="Restaurantul și API-ul: aceleași cinci locuri, '
         'clientul, meniul, ospătarul, bucătăria, cămara; scriptul, documentația, API-ul, serverul, baza de date">',
         '<defs><marker id="rst2-s" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
         '<path d="M0,0 L10,5 L0,10 z"/></marker></defs>',
         '<rect class="rst2__furn" x="665" y="0" width="315" height="298" rx="0"/>',
         '<text class="rst2__zona" x="150" y="18">partea clientului</text>',
         '<text class="rst2__zona" x="680" y="18">partea furnizorului, nevăzută de client</text>',
         '<text class="rst2__rand" x="0" y="58">La restaurant</text>',
         '<text class="rst2__rand rst2__rand--api" x="0" y="226">La un API</text>']
    for c, ((k, n, dsc), (k2, n2, d2), x) in enumerate(zip(SUS, JOS, X)):
        o.append(f'<g class="rst2__col" data-col="{c}" data-x="{x}">')
        o.append(_ic(k, x, 54, "rst2__ic--sus"))
        o.append(f'<text class="rst2__n" x="{x}" y="100">{n}</text><text class="rst2__d" x="{x}" y="117">{dsc}</text>')
        o.append(_ic(k2, x, 222, "rst2__ic--jos"))
        o.append(f'<text class="rst2__n" x="{x}" y="268">{n2}</text><text class="rst2__d" x="{x}" y="285">{d2}</text>')
        o.append("</g>")
    o.append('<path class="rst2__dus" d="M150,156 L955,156" marker-end="url(#rst2-s)"/>')
    o.append('<text class="rst2__s" x="0" y="160">comanda, cererea</text>')
    o.append('<path class="rst2__intors" d="M955,172 L150,172" marker-end="url(#rst2-s)"/>')
    o.append('<text class="rst2__s" x="0" y="176">felul, răspunsul</text>')
    o.append('<text class="rst2__cer" x="420" y="148">GET /v2/country/RO/indicator/SP.POP.TOTL?date=2024</text>')
    o.append('<text class="rst2__rsp" x="420" y="189">200 OK, apoi datele, în JSON</text>')
    o.append('<circle class="rst2__bon" cx="150" cy="156" r="7"/>')
    o.append("</svg>")
    return "".join(o)


RESTAURANT_SCENARII = [
    {"t": "Drumul unei comenzi", "pasi": [
        {"col": [0, 1], "la": 1, "sus": "Clientul citește meniul și scrie pe bon ce vrea.",
         "jos": "Scriptul urmează documentația: adresa resursei și parametrii acceptați."},
        {"col": [2], "la": 2, "sus": "Ospătarul duce bonul. Clientul nu intră în bucătărie.",
         "jos": "Cererea ajunge la API, singura intrare spre datele furnizorului."},
        {"col": [3, 4], "la": 4, "sus": "Bucătăria ia din cămară ce scrie pe bon.",
         "jos": "Serverul interoghează baza de date și aplică filtrele: țara RO, anul 2024."},
        {"col": [0], "la": 0, "intors": True, "sus": "Farfuria se întoarce la masă, pe același drum.",
         "jos": "Răspunsul se întoarce: codul 200, apoi datele, în JSON."}]},
    {"t": "Bucătăria se schimbă", "pasi": [
        {"col": [3, 4], "schimb": True, "la": 4, "sus": "Restaurantul schimbă bucătarul și furnizorul.",
         "jos": "Furnizorul mută datele pe alt server și schimbă baza de date."},
        {"col": [1], "schimb": True, "la": 1, "sus": "Meniul rămâne același: aceleași feluri, cu aceleași nume.",
         "jos": "Documentația rămâne aceeași: aceleași adrese și aceiași parametri."},
        {"col": [0, 1, 2, 3, 4], "schimb": True, "la": 0, "intors": True, "sus": "Aceeași comandă aduce același fel.",
         "jos": "Aceeași cerere aduce același răspuns; scriptul nu se schimbă. Aceasta este abstractizarea."}]},
    {"t": "Meniul are o ediție", "pasi": [
        {"col": [1], "la": 1, "sus": "Apare un meniu nou, dar cel vechi rămâne un timp.",
         "jos": "Furnizorul publică o versiune nouă a API-ului; cea veche rămâne în funcțiune o perioadă."},
        {"col": [1, 2], "la": 2, "sus": "O comandă după meniul vechi este servită în continuare.",
         "jos": "Versiunea scrisă în adresă, /v2, păstrează formatul vechi: codul existent nu se strică."}]},
    {"t": "Ospătarul nu ține minte", "pasi": [
        {"col": [0], "la": 0, "sus": "Fiecare bon este complet: masa, felul, cantitatea.",
         "jos": "Fiecare cerere conține adresa și toți parametrii, inclusiv pagina cerută."},
        {"col": [2, 3], "la": 3, "sus": "Orice ospătar poate prelua bonul, pentru că pe el scrie tot.",
         "jos": "Orice server poate răspunde: nu se păstrează nimic între cereri. Aceasta înseamnă „fără stare”."}]},
]
RESTAURANT_IX = {"svg": _restaurant_svg(), "scenarii": RESTAURANT_SCENARII}


sl("s3", "Ce este un API", "Analogia restaurantului",
   "<h2>Un API funcționează ca un restaurant</h2>"
   "<p class=\"cheie\">Clientul nu intră în bucătărie: comandă din meniu, prin ospătar.</p>"
   + ix("rst2", "Patru situații, același drum", RESTAURANT_IX),
   manual=
   "<h2>Ce este un API</h2>"
   "<p>Analogia restaurantului fixează un principiu esențial: codul clientului nu "
   "comunică direct cu baza de date a furnizorului. Comunică cu un intermediar, care o "
   "accesează în numele clientului, în condiții stabilite dinainte. Condițiile acestea sunt contractul "
   "API-ului, iar documentația e forma lui citibilă.</p>"
   + ix("rst2", "Patru situații, același drum", RESTAURANT_IX)
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


MOTIVE_SLIDE = (
    '<div class="mtv4">'
    '<section style="--c:var(--accent)"><h4>Știință</h4><dl>'
    "<dt>Proveniența</dt><dd>Cererea înregistrează sursa, setul, filtrele și data.</dd>"
    "<dt>Reproductibilitatea</dt><dd>Același cod dă același tabel, pentru oricine.</dd>"
    "<dt>Principiile FAIR</dt><dd>Acces printr-un protocol standard, deschis.</dd>"
    "</dl></section>"
    '<section style="--c:var(--ambra)"><h4>Inginerie</h4><dl>'
    "<dt>Scara</dt><dd>Mii de valori, pe regiuni și pe ani, într-o singură buclă.</dd>"
    "<dt>Actualizarea</dt><dd>Statisticile se revizuiesc; aceeași cerere aduce versiunea curentă.</dd>"
    "<dt>Filtrarea la sursă</dt><dd>Serverul trimite doar felia cerută.</dd>"
    "<dt>Automatizarea</dt><dd>Colectarea se programează și se repetă singură.</dd>"
    "</dl></section>"
    '<section style="--c:var(--roza)"><h4>Calitatea datelor</h4><dl>'
    "<dt>Integritatea</dt><dd>Fără copieri și conversii manuale.</dd>"
    "<dt>Metadatele</dt><dd>Unitățile și indicatorii de stare vin odată cu valoarea.</dd>"
    "<dt>Accesul legitim</dt><dd>Calea prevăzută de furnizor, cu condiții și limite scrise.</dd>"
    "</dl></section></div>"
    '<p class="mtv4__cost"><b>Ce costă</b>dependența de furnizor, limitele de cereri, cheile de acces. '
    "Un fișier publicat și versionat, ca SCI de pe HDX, rămâne o alegere bună.</p>")

sl("s5", "Ce este un API", "De ce prin API",
   "<h2>De ce prin API</h2>"
   "<p class=\"cheie\">Un fișier se descarcă dintr-un clic. De ce o cerere scrisă?</p>"
   + MOTIVE_SLIDE,
   manual=
   "<h2>Motivele colectării prin API</h2>"
   "<p>Când un fișier se poate descărca dintr-un clic, obținerea lui prin cod trebuie "
   "justificată. Motivele țin de știință, de inginerie și de calitatea datelor, iar "
   "fiecare are și un cost.</p>"
   + MOTIVE_SLIDE
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


def _f(n, ce, ex, da, curs=False):
    return {"n": n, "ce": ce, "ex": ex, "da": da, "curs": curs}

TIPURI_ARBORE = {"ales": [0, 0], "ramuri": [
    {"t": "API-uri web", "q": "după stilul cererii", "c": "accent", "frunze": [
        _f("REST", "Resurse la adrese, cerute cu metodele HTTP; serverul nu păstrează nimic între cereri.",
           "Banca Mondială, Eurostat, GitHub.", "Forma cea mai frecventă a surselor publice de date; se poate încerca din browser.", True),
        _f("GraphQL", "O singură adresă; clientul descrie exact câmpurile pe care le vrea, după o schemă tipizată.",
           "GitHub GraphQL, Shopify.", "Aduce exact câmpurile necesare, într-o singură cerere."),
        _f("gRPC", "Apeluri de funcții la distanță, definite în Protocol Buffers; schimb binar, peste HTTP/2.",
           "Serviciile interne ale unei platforme.", "Rar în sursele publice; apare la integrarea cu sisteme de producție."),
        _f("SOAP", "Mesaje XML într-un plic standard, cu operații descrise într-un fișier WSDL.",
           "Bănci, administrație, sisteme instituționale.", "Apare la integrarea cu sisteme instituționale vechi.")]},
    {"t": "După cine are acces", "q": "public, partener, intern", "c": "ambra", "frunze": [
        _f("Public", "Deschis oricui, uneori cu o cheie gratuită; limitele de cereri sunt publicate.",
           "Banca Mondială și Eurostat, fără cheie.", "Sursa principală pentru cercetare; condițiile de reutilizare se citesc înainte.", True),
        _f("Partener", "Deschis doar organizațiilor cu un acord, cu chei dedicate.",
           "Un magazin online și procesatorul lui de plăți.", "Datele vin cu condițiile contractului, nu cu o licență publică."),
        _f("Intern", "Folosit doar în interiorul organizației, între serviciile proprii.",
           "Serviciul din spatele tabloului de bord al unei companii.", "Cea mai frecventă sursă de date în industrie, deși nu se vede din afară.")]},
    {"t": "Orientate pe evenimente", "q": "datele vin fără să fie cerute", "c": "roza", "frunze": [
        _f("Webhooks", "Serverul trimite el o cerere la o adresă dată de client, când apare un eveniment.",
           "GitHub anunță un server la fiecare push.", "Pornește o colectare când apar date noi, fără interogări repetate."),
        _f("Streaming", "Datele curg continuu, pe măsură ce apar, pe o conexiune care rămâne deschisă.",
           "Cotații bursiere; răspunsurile modelelor de limbaj, trimise pe bucăți.", "Date analizate pe măsură ce sosesc, nu în loturi."),
        _f("WebSocket, SSE", "WebSocket: o conexiune în ambele sensuri (RFC 6455). SSE: serverul trimite evenimente prin HTTP.",
           "Chat, colaborare în timp real, notificări.", "Fluxuri în timp real, care se salvează pe măsură ce vin.")]},
    {"t": "Specializate", "q": "după domeniul serviciului", "c": "ardezie", "frunze": [
        _f("Baze de date", "Tabelele unei baze devin resurse; o cerere HTTP devine o interogare.",
           "PostgREST și Supabase, peste PostgreSQL.", "Citirea și scrierea în bază se fac prin aceleași cereri."),
        _f("Cloud", "Stocarea și calculul se comandă prin cereri autentificate.",
           "Amazon S3, Azure Blob Storage.", "Seturile mari stau în stocare și se citesc prin API."),
        _f("AI și ML", "Modele oferite ca serviciu: se trimite textul, vine rezultatul modelului.",
           "OpenAI, Anthropic, Hugging Face.", "Clasificare, extragere de informații, adnotare, ca pas într-un flux de date."),
        _f("IoT", "Dispozitive care trimit măsurători, adesea prin MQTT, un protocol mai ușor decât HTTP.",
           "Stații meteo, contoare inteligente.", "Serii de timp dense, cu valori lipsă și erori de senzor.")]},
    {"t": "Comerciale", "q": "servicii pentru afaceri", "c": "ceas", "frunze": [
        _f("Plăți", "Plăți, abonamente și facturi, prin cereri autentificate; evenimentele vin prin webhooks.",
           "Stripe.", "Tranzacții cu marcaj de timp, dar date personale și financiare sensibile."),
        _f("Comerț", "Produse, comenzi și stocuri ale unui magazin online.",
           "Shopify.", "Date de vânzări, pe produs și pe zi."),
        _f("Rețele sociale", "Conținut public și statistici, cu cheie de acces și o cotă zilnică de cereri.",
           "YouTube Data API.", "Corpusuri de texte și reacții; condițiile de utilizare limitează ce se poate păstra.")]},
]}

sl("s6", "Tipuri de API", "Tipuri de API",
   "<h2>Tipuri de API</h2>"
   "<p class=\"cheie\">Clasificările se fac după criterii diferite; Banca Mondială este în același timp un API web REST și unul public.</p>"
   + ix("tipuri2", "Cinci familii", TIPURI_ARBORE),
   manual=
   "<h2>Tipuri de API</h2>"
   "<p>Un API se descrie după mai multe criterii deodată: după stilul cererii (API-urile web), "
   "după cine are acces, după cine pornește schimbul (cele orientate pe evenimente), după "
   "domeniul serviciului și după piața căreia i se adresează. Criteriile nu se exclud, deci "
   "aceeași sursă apare în mai multe ramuri. Cursul folosește o singură combinație: un API web "
   "REST, public, de statistici oficiale. Fiecare frunză a arborelui are fișa ei.</p>"
   + ix("tipuri2", "Cinci familii", TIPURI_ARBORE)
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

_PE_SLIDE = {"CORBA", "SOAP", "gRPC", "REST", "GraphQL", "webhooks", "OpenAPI", "SDMX", "SDMX 3.0", "MCP", "A2A"}
BENZI_SLIDE = dict(BENZI, repere=[], ales=[1, 0],
                   benzi=[dict(b, puncte=[p for p in b["puncte"] if p["n"] in _PE_SLIDE]) for b in BENZI["benzi"]])

sl("s7", "Tipuri de API", "Trei decenii de API-uri",
   "<h2>Trei decenii de API-uri</h2>"
   "<p class=\"cheie\">Fiecare stil a apărut ca răspuns la limitele celui dinainte.</p>"
   + ix("benzi", "Cinci familii, pe aceeași axă", BENZI_SLIDE),
   manual=
   "<h2>Trei decenii de API-uri</h2>"
   "<p>Istoria API-urilor nu e o succesiune în care fiecare tehnologie o înlocuiește pe "
   "cea dinainte. Sunt mai multe familii care au evoluat în paralel: apelurile la "
   "distanță, resursele și interogările, contractele și evenimentele, standardele "
   "statistice și, recent, protocoalele pentru agenți AI. Dedesubt, protocolul HTTP s-a "
   "schimbat și el, de la HTTP/1.0 la HTTP/3, fără să schimbe înțelesul unei cereri.</p>"
   + ix("benzi", "Cinci familii, pe aceeași axă", BENZI)
   + "<p>REST e descris în 2000, în teza de doctorat a lui Roy Fielding, ca stil "
     "arhitectural al webului. Banda statisticilor este direct relevantă pentru curs: Eurostat "
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


STILURI_SLIDE = (
    '<div class="stl3">'
    '<div class="stl3__r"><div><h4>REST</h4><p>o resursă la o adresă; forma o decide serverul</p></div>'
    '<pre><code>GET /v2/country/RO/indicator/SP.POP.TOTL?date=2024</code></pre></div>'
    '<div class="stl3__r"><div><h4>GraphQL</h4><p>o interogare; forma o decide clientul</p></div>'
    '<pre><code>{ country(code: "RO") { population(year: 2024) } }</code></pre></div>'
    '<div class="stl3__r"><div><h4>gRPC</h4><p>o funcție la distanță; forma o fixează contractul</p></div>'
    '<pre><code>Populatie({tara: "RO", an: 2024})</code></pre></div>'
    '<div class="stl3__r"><div><h4>SOAP</h4><p>un mesaj XML; forma o fixează contractul</p></div>'
    '<pre><code>&lt;Populatie&gt;&lt;tara&gt;RO&lt;/tara&gt;&lt;an&gt;2024&lt;/an&gt;&lt;/Populatie&gt;</code></pre></div>'
    '</div>'
    '<p class="stl2__nota">Doar exemplul REST este un API real, al Băncii Mondiale; celelalte arată forma aceleiași cereri.</p>')

sl("s8", "Tipuri de API", "Aceeași întrebare, patru stiluri",
   "<h2>Aceeași întrebare, patru stiluri</h2>"
   "<p class=\"cheie\">Populația României în 2024, cerută în fiecare stil.</p>" + STILURI_SLIDE,
   manual=
   "<h2>Patru stiluri, față în față</h2>"
   "<p>Diferența dintre stiluri se vede cel mai clar pe aceeași întrebare, formulată "
   "în fiecare stil. Doar exemplul REST e un API real, al Băncii Mondiale; celelalte trei "
   "arată forma pe care ar avea-o aceeași cerere.</p>"
   + STILURI_SLIDE
   + tabel(["", "REST", "GraphQL", "gRPC", "SOAP"], [
       ["unitatea de bază", "resursa, la o adresă", "câmpul, dintr-o schemă", "funcția", "operația, într-un mesaj"],
       ["formatul", "JSON, uneori XML sau CSV", "JSON", "Protocol Buffers, binar", "XML"],
       ["contractul", "OpenAPI, opțional", "schemă, obligatorie", "fișier .proto, obligatoriu", "WSDL, obligatoriu"],
       ["forma răspunsului o decide", "serverul", "clientul", "contractul", "contractul"],
       ["unde se întâlnește", "date publice, servicii web", "aplicații web și mobile", "între serviciile unei platforme", "bănci, administrație"],
   ])
   + "<p>Diferența de fond e cine decide forma răspunsului. În REST o decide serverul, "
     "pentru fiecare resursă; în GraphQL o decide clientul, prin interogare; în gRPC și "
     "SOAP e fixată de contract. Pentru colectarea datelor publice, REST rămâne stilul "
     "dominant pentru că se poate încerca din browser, nu cere unelte speciale și "
     "răspunde de obicei în JSON.</p>")


# ===========================================================================
#  8-13. Cum arată o cerere
# ===========================================================================


HTTP_SLIDE = (
    '<div class="htp">'
    '<section><h4>Cererea</h4><dl>'
    '<dt class="p1">prima linie</dt><dd><code>GET /v2/country/RO/indicator/SP.POP.TOTL?date=2024 HTTP/1.1</code></dd>'
    '<dt class="p2">antete</dt><dd><code>Host: api.worldbank.org</code><code>Accept: */*</code></dd>'
    '<dt class="p3">rând gol</dt><dd></dd>'
    '<dt class="p4">corp</dt><dd class="htp__nu">lipsește: o cerere GET are totul în prima linie</dd>'
    '</dl></section>'
    '<section><h4>Răspunsul</h4><dl>'
    '<dt class="p1">prima linie</dt><dd><code>HTTP/1.1 200 OK</code></dd>'
    '<dt class="p2">antete</dt><dd><code>Content-Type: application/json;charset=utf-8</code></dd>'
    '<dt class="p3">rând gol</dt><dd></dd>'
    '<dt class="p4">corp</dt><dd><code>[{"page": 1, "pages": 1, "total": 1, …}, [{"date": "2024", "value": 19051804, …}]]</code></dd>'
    '</dl></section></div>')

sl("s9", "Cum arată o cerere", "O cerere și un răspuns",
   "<h2>O cerere și un răspuns</h2>"
   "<p class=\"cheie\">HTTP este un schimb de două mesaje text, cu aceeași structură în patru părți.</p>"
   + HTTP_SLIDE,
   manual=
   "<h2>Mesajul HTTP</h2>"
   "<p>Tot ce face un API REST trece prin HTTP, iar HTTP e, la bază, un schimb de două "
   "mesaje text. Cererea și răspunsul au aceeași structură: o primă linie, un șir de "
   "antete de forma <code>Nume: valoare</code>, un rând gol și, opțional, corpul.</p>"
   + HTTP_SLIDE
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


SORTARE = {
       "id": "c2-sort-metode2",
       "sarcina": "Ce metodă corespunde fiecărei situații?",
       "elemente": [{"t": "aducerea populației județelor", "cos": 0},
                    {"t": "adăugarea unei echipe noi", "cos": 1},
                    {"t": "înlocuirea întregii fișe a unui student", "cos": 2},
                    {"t": "corectarea numai a temei unei echipe", "cos": 3},
                    {"t": "eliminarea unei colectări greșite", "cos": 4}],
       "cosuri": [{"t": "GET", "d": "citește"}, {"t": "POST", "d": "creează"},
                  {"t": "PUT", "d": "înlocuiește"}, {"t": "PATCH", "d": "modifică"},
                  {"t": "DELETE", "d": "șterge"}],
       "laBine": "Colectarea folosește numai GET; celelalte metode apar la scrierea într-un sistem.",
       "laRau": "Distincția de verificat: PUT trimite resursa întreagă, PATCH doar câmpurile modificate.",
       "explicatie": "Situațiile de citire corespund lui GET. PUT trimite resursa întreagă, PATCH doar "
                     "partea care se schimbă, POST creează o resursă nouă, DELETE o șterge."}

METODE_SLIDE = (
    '<table class="tabel mt2"><thead><tr><th>Metoda</th><th>Ce face</th><th>Schimbă ceva pe server</th>'
    '<th>Repetată, are același efect</th></tr></thead><tbody>'
    '<tr class="on"><td>GET</td><td>citește</td><td>nu</td><td>da</td></tr>'
    "<tr><td>POST</td><td>creează</td><td>da</td><td>nu</td></tr>"
    "<tr><td>PUT</td><td>înlocuiește</td><td>da</td><td>da</td></tr>"
    "<tr><td>PATCH</td><td>modifică</td><td>da</td><td>nu, în general</td></tr>"
    "<tr><td>DELETE</td><td>șterge</td><td>da</td><td>da</td></tr>"
    "</tbody></table>")

sl("s10", "Cum arată o cerere", "Metodele HTTP",
   "<h2>Metodele HTTP</h2>"
   "<p class=\"cheie\">La colectare se folosește doar GET: nu schimbă nimic, deci o cerere eșuată se poate relua.</p>"
   + METODE_SLIDE,
   manual=
   "<h2>Metodele HTTP</h2>"
   "<p>Metoda e primul cuvânt din cerere și spune ce operație se cere asupra resursei. "
   "Cele patru operații de bază asupra unei colecții de date se numesc, pe scurt, CRUD "
   "(<em>create, read, update, delete</em>), iar HTTP le dă câte o metodă; modificarea "
   "are două: PUT înlocuiește resursa întreagă, PATCH doar câmpurile trimise.</p>"
   + METODE_SLIDE
   + "<p>Două proprietăți contează la colectare. O metodă e <strong>sigură</strong> dacă nu "
     "schimbă nimic pe server, și <strong>idempotentă</strong> dacă repetarea ei are același "
     "efect ca o singură execuție. GET le are pe amândouă, deci o colectare întreruptă se "
     "poate relua fără riscuri. PUT și DELETE sunt idempotente, deși schimbă ceva; POST nu "
     "e: două cereri identice creează două resurse.</p>"
   + ix("sortare", "Ce metodă se folosește", SORTARE)
   + surse("Documentație", [
       ("MDN: metodele HTTP", "https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods",
        "fiecare metodă, cu proprietățile ei"),
   ]))

sl("s10v", "Cum arată o cerere", "Exercițiu: metodele HTTP",
   "<h2>Exercițiu: metodele HTTP</h2>"
   "<p class=\"cheie\">Fiecare situație, în coloana metodei potrivite.</p>"
   + ix("sortare", "Ce metodă se folosește", SORTARE),
   manual="")

ENDPOINTURI = (
    '<p class="ep__baza"><span>Adresa de bază</span><code>https://api.worldbank.org/v2</code></p>'
    + tabel(["Endpoint-ul", "Ce întoarce"], [
        ["~/country", "lista țărilor: cod, nume, regiune, nivel de venit"],
        ["~/indicator", "lista indicatorilor: cod și denumire"],
        ["~/country/RO/indicator/SP.POP.TOTL", "valorile unui indicator pentru o țară: populația României, pe ani"],
    ])
    + '<p class="ep__jos">Aceeași adresă de bază, trei resurse diferite. Documentația API-ului enumeră '
    "toate endpoint-urile; proiectul folosește ultimul tip.</p>")

sl("s11", "Cum arată o cerere", "Endpoint-ul",
   "<h2>Ce este un endpoint</h2>"
   "<p class=\"cheie\">Adresa la care se cere o anumită resursă. Fiecare endpoint întoarce altceva.</p>"
   + ENDPOINTURI)

ADRESA = {
    "id": "c2-url",
    "sarcina": "Ce rol din legendă are fiecare placă? Prima este rezolvată, ca exemplu.",
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
           "Unde se pun filtrele unei cereri, de exemplu anul sau formatul?",
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


SURSE_SLIDE = (
    '<table class="tabel srs2"><thead><tr><th>Domeniul</th><th>Deschise, fără cheie</th><th>Cu cheie, cont sau plată</th></tr></thead><tbody>'
    '<tr class="on"><td>Statistici oficiale</td><td>Eurostat, Banca Mondială, data.gov.ro</td><td>microdate, cu acord de acces</td></tr>'
    "<tr><td>Hărți și locuri</td><td>Eurostat GISCO, OpenStreetMap</td><td>Google Maps Platform</td></tr>"
    "<tr><td>Rețele sociale și web</td><td>Wikipedia</td><td>YouTube Data API, X API</td></tr>"
    "<tr><td>Vreme și senzori</td><td>Open-Meteo</td><td>OpenWeatherMap</td></tr>"
    "<tr><td>Servicii AI</td><td></td><td>OpenAI, Anthropic, Hugging Face</td></tr>"
    "</tbody></table>")
SURSE_JOS = ('<p class="c2__jos">Fără API, datele se pot extrage din pagini web, dar pagina se poate schimba oricând, '
    "iar condițiile de utilizare pot interzice extragerea.</p>")

sl("s14", "De unde vin datele", "Surse de date",
   "<h2>Surse de date</h2>"
   "<p class=\"cheie\">Două întrebări despre orice sursă: ce date oferă și în ce condiții.</p>"
   + SURSE_SLIDE + SURSE_JOS,
   manual=
   "<h2>Surse accesibile prin API</h2>"
   "<p>Aproape orice sursă de date importantă are azi un API. Pentru o analiză contează "
   "două lucruri: ce fel de date oferă sursa și în ce condiții se poate accesa. Condițiile se "
   "schimbă în timp, așa că se verifică în documentația fiecărei surse, la data colectării.</p>"
   + SURSE_SLIDE
   + "<p>Cheile de acces sunt personale. Nu se scriu în cod și nu se publică pe GitHub: se păstrează în "
     "variabile de mediu sau într-un fișier exclus prin <code>.gitignore</code>. Extragerea "
     "din pagini web (<em>web scraping</em>) e soluția pentru situațiile fără API, cu două "
     "riscuri: pagina se poate schimba fără avertisment, iar condițiile de utilizare pot "
     "interzice extragerea.</p>")

SURSE_TABEL = tabel(["Sursa", "Cum vine", "Ce oferă"], [
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
   "<p class=\"cheie\">Un fișier, la cursul 1, și două API-uri, de azi.</p>"
   + SURSE_TABEL
   + '<p class="c2__jos">În caiet: întâi Banca Mondială, cu un răspuns simplu, apoi Eurostat. '
   "Documentația fiecărei surse este în manual.</p>",
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


DOC_REQ = surse("Documentația requests", [
    ("Ghidul rapid", "https://requests.readthedocs.io/en/latest/user/quickstart/",
     "cereri, parametri, răspunsuri, JSON, timeout"),
    ("Referința bibliotecii", "https://requests.readthedocs.io/en/latest/api/",
     "toți parametrii lui <code>get</code> și atributele lui <code>Response</code>"),
])

REQ_TABEL = (
    '<table class="tabel rq2"><thead><tr><th>În mesajul HTTP</th><th>În Python, cu requests</th></tr></thead><tbody>'
    "<tr><td>cererea: metoda, adresa, parametrii</td><td><code>raspuns = requests.get(url, params=parametri, timeout=30)</code></td></tr>"
    "<tr><td>codul de stare</td><td><code>raspuns.status_code</code></td></tr>"
    "<tr><td>antetele</td><td><code>raspuns.headers</code></td></tr>"
    "<tr><td>corpul, în JSON</td><td><code>raspuns.json()</code></td></tr>"
    "<tr><td>adresa construită, după codificare</td><td><code>raspuns.url</code></td></tr>"
    "</tbody></table>")

sl("s16", "requests", "Aceeași cerere, în Python",
   "<h2>Aceeași cerere, în Python</h2>"
   "<p class=\"cheie\">Ordinea este mereu aceeași: cererea, codul de stare, abia apoi datele.</p>"
   + REQ_TABEL
   + '<p class="c2__jos">Fără <code>timeout</code>, o cerere la care serverul nu răspunde blochează programul.</p>',
   manual=
   "<h2>requests</h2>"
   "<p><code>requests</code> e biblioteca standard de facto pentru HTTP în Python. Fiecare "
   "parte a mesajului HTTP are în ea un corespondent direct.</p>"
   + REQ_TABEL
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
    "structura": "<code>raspuns.json()</code> este o listă cu două elemente: "
                 "<code>[0]</code> paginarea, <code>[1]</code> lista valorilor, de la anul cel mai recent.",
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
   "<p class=\"cheie\">Prima celulă este rulată. Trei valori de aflat, scriind expresii în celula de dedesubt, ca în Jupyter.</p>"
   + ix("jupyter", "Trei lucruri de aflat din răspuns", JUPYTER),
   manual=
   "<h2>Exercițiu: inspectarea răspunsului</h2>"
   "<p>Celula de mai jos e cea din caiet, deja rulată. Răspunsul se află în <code>raspuns</code>; "
   "consola funcționează ca o celulă Jupyter. Sunt trei valori de aflat, toate obținute prin cod, "
   "nu transcrise manual.</p>"
   + ix("jupyter", "Trei lucruri de aflat din răspuns", JUPYTER)
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
   + '<p class="c2__jos">Două strategii: paginile, pe rând, până la <code>pages</code>; sau o singură pagină mare, '
   "cu <code>per_page=1000</code>, verificând că <code>pages</code> este 1. Caietul o folosește pe a doua.</p>",
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


sl("s18x", "requests", "Exercițiu: paginarea",
   "<h2>Exercițiu: câte valori au venit</h2>"
   "<p class=\"cheie\">Prima pagină a unui răspuns cu 180 de valori, câte 50 pe pagină.</p>"
   + ix("prezice", "Câte valori au venit", PREZICE_PAGINI),
   manual="")


# ===========================================================================
#  19-20. Eurostat
# ===========================================================================

EUROSTAT_BAZA = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"

EU2_HTML = (
    '<p class="eu2__adr"><code>' + EUROSTAT_BAZA + '<b>migr_pop1ctz</b>?sex=T&amp;age=TOTAL&amp;unit=NR&amp;time=2024</code></p>'
    '<table class="tabel eu2"><tbody>'
    "<tr><td>Fixate, câte o valoare</td><td><code>freq=A</code> · <code>sex=T</code> · <code>age=TOTAL</code> · "
    "<code>unit=NR</code> · <code>time=2024</code></td></tr>"
    '<tr class="on"><td>Deschise, toate valorile</td><td><code>citizen</code> (cetățenia) · <code>geo</code> (țara de reședință)</td></tr>'
    "</tbody></table>")

sl("s19e", "Eurostat", "Eurostat: structura cererii",
   "<h2>Eurostat: structura cererii</h2>"
   "<p class=\"cheie\">Calea alege setul; parametrii fixează unele dimensiuni, iar celelalte rămân deschise.</p>"
   + EU2_HTML
   + '<p class="c2__jos">Ce rămâne deschis formează cubul din răspuns: aici, perechi de țări. Dimensiunile '
   'setului se văd în <a class="leg" href="https://ec.europa.eu/eurostat/databrowser/view/migr_pop1ctz/default/table" '
   'target="_blank" rel="noopener">Data Browser</a>.</p>',
   manual=
   "<h2>Eurostat: cererea pe dimensiuni</h2>"
   "<p>Un set Eurostat e un tabel cu mai multe dimensiuni: frecvența, regiunea, anul, "
   "sexul, vârsta, unitatea și altele, după set. O cerere fixează unele dimensiuni la o "
   "singură valoare și le lasă deschise pe celelalte. Ce rămâne deschis formează cubul "
   "din răspuns.</p>"
   + EU2_HTML
   + "<p>Eurostat oferă mai multe API-uri: Statistics API, care răspunde în JSON-stat și "
     "pe care îl folosește cursul, și API-urile SDMX 2.1 și SDMX 3.0, pentru schimbul standardizat "
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
   "<p class=\"cheie\">Codurile au fiecare o poziție; valorile stau pe un singur rând, rând după rând.</p>"
   + ix("cub", "Migrația, 2024: trei cetățenii, trei țări", dict(CUB, simplu=True)),
   manual=
   "<h2>Cubul JSON-stat</h2>"
   "<p>Banca Mondială trimite o listă de înregistrări, din care tabelul se face direct. "
   "Eurostat trimite JSON-stat, un format pentru tabele cu multe dimensiuni. În loc să "
   "repete codurile pe fiecare rând, le scrie o singură dată, cu poziția lor, iar valorile "
   "le pune pe un singur rând, în ordinea în care ultima dimensiune se schimbă cel mai "
   "repede.</p>"
   + ix("cub", "Migrația, 2024: trei cetățenii, trei țări", dict(CUB, simplu=True))
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
    "sarcina": "Cele două celule de mai jos se rulează în caietul 02, după secțiunea 5, iar ce afișează se lipește aici.",
    "pasi": [
        {"t": "Indicatorul a venit pe o singură pagină",
         "cmd": "tabel = cere_bm(\"SP.POP.TOTL\", TARI)",
         "gol": "linia cu numărul de pagini",
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
PASI_COLECTARE = tabel(["Pasul", "Ce se face"], [
    ["1", "se deschide caietul 02 din <code>dsw/curs/</code>, cu kernelul <code>.venv</code>"],
    ["2", "se rulează secțiunile 1 la 5: prima cerere, paginarea, cei trei indicatori"],
    ["3", "se verifică faptul că fiecare indicator a venit pe o singură pagină"],
    ["4", "se salvează tabelul în <code>data/c2/bm.csv</code>"],
])

sl("s21", "Proiectul echipei", "Prima colectare",
   "<h2>Prima colectare, în caiet</h2>"
   "<p class=\"cheie\">Caietul 02, secțiunile 1 la 5: cererile, paginarea și salvarea în data/c2. "
   "Ce afișează cele două celule de verificare se lipește mai jos.</p>"
   + ix("dovada", "Dovada colectării", DOVADA),
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
    '├── curs/            <span class="c"># personal, fără Git</span>\n'
    '└── <span class="a">proiect/</span>         <span class="c"># al echipei, cu Git</span>\n'
    '    ├── .git/        <span class="c"># istoricul</span>\n'
    '    └── README.md')

# Organizația GitHub e comună pentru toată grupa; fiecare echipă își face în ea
# depozitul ei. Pașii, pe rânduri.

PE4_HTML = (
    '<ol class="pe4">'
    f'<li><span>1</span><b>Organizația</b><p><a class="leg" href="https://github.com/{REPO_ORG}" target="_blank" rel="noopener">{REPO_ORG}</a>, comună pentru grupă. Invitația vine pe e-mail.</p></li>'
    "<li><span>2</span><b>Depozitul echipei</b><p>Un membru îl creează în organizație și îi adaugă pe ceilalți.</p></li>"
    "<li><span>3</span><b>Adresa</b><p>Pe pagina depozitului: Code → HTTPS.</p></li>"
    "<li><span>4</span><b>Clonarea</b><p>În terminal, în dsw: <code>git clone &lt;adresa&gt; proiect</code></p></li>"
    "</ol>"
    '<div class="pe4__arb"><pre><code>' + ARBORE_PROIECT + "</code></pre>"
    '<p>Munca echipei stă în proiect/, cu Git; exercițiile de la curs rămân în curs/, fără Git.</p></div>')

sl("s21t", "Proiectul echipei", "Echipele",
   "<h2>Alegerea echipelor</h2>"
   "<p class=\"cheie\">Echipe de cel mult cinci membri, fiecare cu numele membrilor ei. "
   'Aceeași alegere, pe o pagină separată: <a class="leg" href="../../echipe/">Echipele de proiect</a>.</p>'
   + ix("echipe", "Echipele grupei", {}),
   manual=
   "<h2>Echipele de proiect</h2>"
   "<p>Proiectul se realizează în echipe de cel mult cinci membri. Echipa se alege pe slide-ul "
   "de la curs, pe pagina <a class=\"leg\" href=\"../../echipe/\">Echipele de proiect</a> sau din "
   "<a class=\"leg\" href=\"../../cont/#echipa\">contul personal</a>, unde rămâne vizibilă tot semestrul.</p>"
   "<ul>"
   "<li>Cât timp alegerea este deschisă, fiecare student intră singur într-o echipă cu locuri libere "
   "și se poate muta în alta.</li>"
   "<li>După închiderea alegerii, un student fără echipă trimite o cerere unei echipe cu locuri "
   "libere; oricare membru al echipei o acceptă sau o refuză.</li>"
   "<li>Dacă toate echipele sunt complete, studentul fără echipă deschide o echipă nouă, iar "
   "următorii pot cere să intre în ea.</li>"
   "<li>Echipele și numele membrilor sunt vizibile pentru studenții grupei. Numărul matricol și "
   "contul GitHub nu apar.</li>"
   "</ul>"
   + ix("echipe", "Echipele grupei", {}))

sl("s21e", "Proiectul echipei", "Depozitul echipei",
   "<h2>Depozitul echipei, în dsw/proiect</h2>"
   "<p class=\"cheie\">O organizație comună, câte un depozit pentru fiecare echipă, clonat în dsw/proiect.</p>"
   + PE4_HTML,
   manual=
   "<h2>Depozitul echipei, în dsw/proiect</h2>"
   "<p>Până acum, tot ce s-a lucrat se află în <code>curs/</code>, pe calculatorul personal, fără Git. "
   "Proiectul de semestru funcționează diferit: la el lucrează cinci persoane, iar fiecare trebuie să "
   "vadă ce au făcut ceilalți. Organizația GitHub a cursului, "
   f'<a class="leg" href="https://github.com/{REPO_ORG}" target="_blank" rel="noopener">{REPO_ORG}</a>, '
   "este comună pentru toată grupa; în ea, fiecare echipă își creează depozitul propriu, iar fiecare "
   "membru îl clonează pe calculatorul personal, în <code>dsw/proiect</code>.</p>"
   + PE4_HTML
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


_ETAPE8 = ["Introducere", "API", "Git", "Curățare", "Agregare", "Explorare", "Model", "Raport"]
PROGRES = ('<ol class="prg">' + "".join(
    f'<li class="{"gata" if k <= 2 else "prg__urm" if k == 3 else ""}"><span>{k}</span><small>{t}</small></li>'
    for k, t in enumerate(_ETAPE8, 1)) + "</ol>")

sl("s22", "Mai departe", "Pentru cursul următor",
   "<h2>La cursul 3: versionare și colaborare</h2>"
   + PROGRES
   + '<div class="fin3 fin3--mare"><div class="fin3__g">'
   "<section><h4>Ce urmează la cursul 3</h4><ul>"
   "<li>Git în proiect/: commit-ul, istoricul, lucrul în echipă.</li>"
   "<li>Pregătirea și explorarea datelor colectate.</li>"
   "<li>Cadrul teoretic al proiectului și căutarea literaturii.</li>"
   "<li>Tema echipei și împărțirea sarcinilor.</li></ul></section>"
   "<section><h4>Pregătirea pentru cursul 3</h4><ul>"
   "<li>Caietul 02 rulat, cu bm.csv și migratie.csv în curs/data/c2.</li>"
   "<li>Depozitul echipei, clonat în dsw/proiect.</li>"
   "<li>Fișa echipei, de la finalul caietului: direcția provizorie și indicatorul încercat.</li></ul></section>"
   "</div>"
   '<p class="fin3__a"><a class="leg" href="../">Pagina cursului 2</a></p></div>')

if __name__ == "__main__":
    L.scrie_tot()
