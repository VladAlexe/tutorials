# -*- coding: utf-8 -*-
"""
Lecția 2: Colectarea datelor prin API.

Povestea lecției, aceeași pe slide-uri și în manual: de ce datele trebuie
aduse reproductibil, ce este un API (un contract), peisajul (tipuri, istorie,
stiluri), protocolul HTTP piesă cu piesă, de unde vin datele, aceeași cerere
în Python, un al doilea API (Eurostat, cu valorile numerotate) și prima
colectare în proiect.

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
    ("Ce este un API", "Cum cere un program date de la altul; de ce se colectează așa."),
    ("Tipuri de API", "Cinci familii și trei decenii de istorie."),
    ("Cum arată o cerere", "Adresa, mesajul HTTP, metoda și codul de stare."),
    ("De unde vin datele", "Sursele proiectului și documentația lor."),
    ("requests", "Aceeași cerere în Python; paginarea."),
    ("Eurostat", "Indicatori pe regiuni; o funcție aduce direct tabelul."),
    ("Prima colectare și echipele", "Cererea adaptată la alt indicator; echipele de proiect."),
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

# Pe slide: folderul de la cursul 1, cu caietul nou marcat, și cele trei lucruri
# de verificat înainte de prima cerere.
START_HTML = (
    '<div class="pp2">'
    '<pre class="pp2__arb"><code><span class="a">dsw/</span>\n'
    '├── .venv/          <span class="c"># mediul, de la cursul 1</span>\n'
    '├── requirements.txt\n'
    '└── <span class="a">curs/</span>\n'
    '    ├── 01_introducere_si_datele_proiectului.ipynb\n'
    '    ├── <b>02_colectarea_datelor_prin_api.ipynb</b>\n'
    '    └── data/c2/     <span class="c"># aici ajung datele de azi</span></code></pre>'
    '<ol class="pp2__l">'
    "<li><b>Caietul 02</b><span>descărcat de pe GitHub, cu Download raw file, în <code>dsw/curs/</code>.</span></li>"
    "<li><b>Kernelul .venv</b><span>în VS Code: Select Kernel → Python Environments → .venv.</span></li>"
    "<li><b>Contul pe site</b><span>cu GitHub, ca răspunsurile să se salveze.</span></li>"
    "</ol></div>")

sl("s2", "Cursul", "Punctul de plecare",
   "<h2>Punctul de plecare</h2>"
   "<p class=\"cheie\">Folderul de la cursul 1, plus caietul de azi.</p>"
   + START_HTML,
   manual=
   "<h2>Punctul de plecare</h2>"
   "<p>Lecția pornește de la ce s-a construit la cursul 1: folderul cursului, <code>dsw</code>, "
   "cu mediul virtual <code>.venv</code> și pachetele din <code>requirements.txt</code>, și caietul 01 "
   "rulat de sus până jos. Dacă lipsește ceva, "
   "pașii sunt în <a class=\"leg\" href=\"../../c1-introducere-si-mediu/tutorial/\">manualul "
   "cursului 1</a>. Echipele de cel mult cinci membri se formează la finalul acestei lecții, pe site.</p>"
   + START_HTML
   + "<p>Caietul lecției se descarcă separat, nu odată cu toată arhiva: pe "
   f'<a class="leg" href="{repo_fisier("curs/" + CAIET)}" target="_blank" rel="noopener">pagina lui de pe GitHub</a> '
   "se alege <em>Download raw file</em>, iar fișierul se salvează în <code>dsw/curs/</code>, lângă caietul 01. "
   "Arhiva întreagă, despachetată din nou peste <code>dsw</code>, ar putea suprascrie caietele deja completate.</p>"
   "<p>În VS Code, caietul rulează cu kernelul mediului: Select Kernel → Python Environments → "
   "<code>.venv</code>. Dacă lista nu oferă nicio sursă, lipsesc extensiile Python și Jupyter; "
   "VS Code le propune chiar în fereastra Select Kernel.</p>"
   "<p>Biblioteca folosită în această lecție, <code>requests</code>, este deja în mediu, din <code>requirements.txt</code>. "
   "Dacă lipsește, cu mediul activ:</p>"
   "<pre><code>pip install -r requirements.txt</code></pre>")


# ===========================================================================
#  3-4. Ce este un API
# ===========================================================================

# Pictogramele restaurantului și ale API-ului, din linii.
def _ic(k, x, y, cls):
    """Pictograme simple, din linii; (x, y) este centrul."""
    g = f'<g class="rst2__ic {cls}" transform="translate({x - 22},{y - 22})">'
    d = {
        "client": '<circle cx="22" cy="12" r="7"/><path d="M8 40c0-9 6-15 14-15s14 6 14 15"/>',
        "meniu": '<rect x="11" y="4" width="22" height="36" rx="2"/><path d="M16 13h12M16 20h12M16 27h8"/>',
        "ospatar": '<circle cx="18" cy="11" r="6"/><path d="M7 40c0-8 5-14 11-14 4 0 7 2 9 5"/><path d="M26 22h16M30 22c0-4 2-6 4-6s4 2 4 6"/>',
        "bucatarie": '<path d="M8 22h28v12a6 6 0 0 1-6 6H14a6 6 0 0 1-6-6z"/><path d="M4 22h36"/><path d="M16 15c0-3 3-3 3-6M24 15c0-3 3-3 3-6"/>',
        "script": '<path d="M10 4h17l8 8v28H10z"/><path d="M27 4v8h8"/><path d="M19 22l-4 4 4 4M26 22l4 4-4 4"/>',
        "doc": '<path d="M8 8c5-3 10-3 14 0v32c-4-3-9-3-14 0zM36 8c-5-3-10-3-14 0v32c4-3 9-3 14 0z"/>',
        "api": '<rect x="8" y="6" width="28" height="34" rx="2"/><path d="M14 23h14M24 18l5 5-5 5"/>',
        "bd": '<ellipse cx="22" cy="10" rx="13" ry="5"/><path d="M9 10v24c0 3 6 5 13 5s13-2 13-5V10M9 22c0 3 6 5 13 5s13-2 13-5"/>',
    }[k]
    return g + d + "</g>"


def _restaurant_svg():
    """Restaurantul, ca o singură scenă: sala, la vedere, și bucătăria, în spatele
    unui perete cu o singură ușă. Sub fiecare personaj, în verde, perechea lui
    de la un API. Bonul și felul se mută pas cu pas (V.rmt, în vizual.js)."""
    o = ['<svg class="rmt" viewBox="0 0 980 300" role="img" aria-label="Restaurantul și API-ul: clientul e scriptul, '
         'meniul e documentația, ospătarul e API-ul, bucătăria e serverul cu datele">',
         '<defs><marker id="rmt-s" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">'
         '<path d="M0,0 L10,5 L0,10 z"/></marker></defs>',
         '<rect class="rmt__buc" x="716" y="0" width="264" height="300"/>',
         '<path class="rmt__zid" d="M716,0 V198 M716,286 V300 M706,198 H726 M706,286 H726"/>',
         '<text class="rmt__zona" x="0" y="16">sala, la vedere</text>',
         '<text class="rmt__zona" x="736" y="16">bucătăria, nevăzută</text>',
         '<text class="rmt__usa" x="726" y="247">ușa</text>']
    for i, (k, x, n, api) in enumerate([("client", 110, "Clientul", "= scriptul"),
                                        ("meniu", 262, "Meniul", "= documentația"),
                                        ("ospatar", 520, "Ospătarul", "= API-ul, singura intrare"),
                                        ("bucatarie", 848, "Bucătăria", "= serverul, cu datele")]):
        g = _ic(k, 0, 0, "rmt__ic").replace('transform="translate(-22,-22)"', f'transform="translate({x - 40},30) scale(1.8)"')
        o.append(f'<g class="rmt__st" data-st="{i}">' + g
                 + f'<text class="rmt__n" x="{x}" y="144">{n}</text><text class="rmt__a" x="{x}" y="167">{api}</text></g>')
    o.append('<path class="rmt__dus" data-dir="dus" d="M110,222 H900" marker-end="url(#rmt-s)"/>')
    o.append('<text class="rmt__s" x="290" y="213">comanda <tspan class="a">= cererea</tspan></text>')
    o.append('<path class="rmt__dus" data-dir="intors" d="M900,268 H110" marker-end="url(#rmt-s)"/>')
    o.append('<text class="rmt__s" x="290" y="259">felul <tspan class="a">= răspunsul</tspan></text>')
    # bonul și felul acoperit: desenate în jurul lui (0, 0), mutate din V.rmt
    o.append('<g class="rmt__bon"><path d="M0 0h22v26l-3.7-3-3.6 3-3.7-3-3.7 3-3.6-3L0 26z"/>'
             '<path d="M5 7h12M5 13h12M5 19h7"/></g>')
    o.append('<g class="rmt__fel"><path d="M3 15a13 13 0 0 1 26 0z"/><path d="M0 15h32M16 0v2"/></g>')
    o.append("</svg>")
    return "".join(o)


# Povestea, pas cu pas: st = personajele aprinse (0 clientul, 1 meniul, 2 ospătarul,
# 3 bucătăria); bon, fel = unde sunt pe drum (x); dir = săgeata aprinsă.
RESTAURANT_IX = {"svg": _restaurant_svg(), "pasi": [
    {"st": [0, 1], "bon": None, "fel": None, "dir": None,
     "sus": "Clientul citește meniul: ce se poate comanda.",
     "jos": "Scriptul citește documentația: ce date se pot cere și cum."},
    {"st": [0, 2], "bon": 500, "fel": None, "dir": "dus",
     "sus": "Clientul îi dă ospătarului comanda, pe un bon.",
     "jos": "Scriptul trimite cererea la API."},
    {"st": [2, 3], "bon": 820, "fel": None, "dir": "dus",
     "sus": "Ospătarul duce bonul în bucătărie. Clientul nu intră acolo.",
     "jos": "API-ul duce cererea la server. Scriptul nu ajunge direct la baza de date."},
    {"st": [3], "bon": None, "fel": 820, "dir": None,
     "sus": "Bucătăria pregătește exact felul de pe bon.",
     "jos": "Serverul caută în baza de date exact ce s-a cerut."},
    {"st": [3, 2, 0], "bon": None, "fel": 140, "dir": "intors",
     "sus": "Felul ajunge la masă, pe același drum, prin ospătar.",
     "jos": "Răspunsul ajunge la script: un cod de stare, apoi datele."},
]}


sl("s3", "Ce este un API", "Analogia restaurantului",
   "<h2>Un API funcționează ca un restaurant</h2>"
   "<p class=\"cheie\">Clientul nu intră în bucătărie: comandă din meniu, prin ospătar. "
   "La fel, scriptul cere datele prin API, după documentație.</p>"
   + ix("rmt", "Drumul unei comenzi", RESTAURANT_IX),
   manual=
   "<h2>Ce este un API</h2>"
   "<p>Analogia restaurantului fixează un principiu esențial: codul clientului nu "
   "comunică direct cu baza de date a furnizorului. Comunică cu un intermediar, API-ul, care o "
   "accesează în numele clientului, după reguli stabilite dinainte. Regulile acestea sunt contractul "
   "API-ului, iar documentația e forma lui citibilă.</p>"
   + ix("rmt", "Drumul unei comenzi", RESTAURANT_IX)
   + tabel(["La restaurant", "La un API"], [
       ["masa, clientul", "scriptul"],
       ["meniul", "documentația: ce resurse există, ce parametri primesc, ce formă are răspunsul"],
       ["comanda", "cererea: metoda, adresa, parametrii"],
       ["ospătarul", "API-ul, singura intrare spre date"],
       ["bucătăria", "serverul și baza de date"],
       ["felul adus la masă", "răspunsul: un cod de stare și corpul"],
   ])
   + "<h3>Patru proprietăți, nu doar un drum</h3>"
   "<p><strong>Contractul.</strong> Documentația descrie complet ce se poate cere. Multe "
   "API-uri publică o descriere citibilă de mașini, în formatul OpenAPI, din care se "
   "generează documentație și cod.</p>"
   "<p><strong>Abstractizarea.</strong> Clientul depinde de contract, nu de implementare. "
   "Furnizorul își poate schimba serverele și baza de date fără ca scriptul clientului să se "
   "schimbe, la fel cum un restaurant își poate schimba bucătarul fără să schimbe meniul.</p>"
   "<p><strong>Versionarea.</strong> Când contractul se schimbă, furnizorul publică o "
   "versiune nouă (la Banca Mondială, <code>/v2</code> din adresă), iar versiunea veche "
   "rămâne în funcțiune până la o dată anunțată, ca un meniu vechi încă servit o vreme.</p>"
   "<p><strong>Lipsa stării.</strong> Serverul nu păstrează nimic de la o cerere la alta. "
   "Fiecare cerere conține tot ce trebuie, ca un bon complet pe care îl poate prelua orice "
   "ospătar; de aceea o colectare întreruptă se reia de la pagina la care a rămas.</p>"
   "<h3>Limitele analogiei</h3>"
   "<p>Un API nu negociază și nu interpretează. O cerere care nu respectă contractul nu "
   "primește o explicație, ci un cod de eroare și, uneori, un mesaj scurt. De aceea "
   "documentația se citește înainte de prima cerere, nu după primul eșec.</p>")


# Trei coloane, câte trei motive, aliniate pe rânduri; costul, pe toată lățimea.
_MOTIVE = [
    ("Știință", "accent", [("Proveniența", "sursa, filtrele și data, scrise în cerere"),
                           ("Reproductibilitatea", "același cod, același tabel"),
                           ("Principiile FAIR", "acces printr-un protocol standard")]),
    ("Inginerie", "ambra", [("Scara", "mii de valori, într-o singură buclă"),
                            ("Actualizarea", "aceeași cerere, versiunea curentă"),
                            ("Filtrarea la sursă", "vine doar felia cerută")]),
    ("Calitatea datelor", "roza", [("Integritatea", "fără copieri și conversii manuale"),
                                   ("Metadatele", "unitățile și stările vin cu valoarea"),
                                   ("Accesul legitim", "calea prevăzută de furnizor")]),
]
MOTIVE_SLIDE = (
    '<div class="mtv5">'
    + "".join(f'<h4 style="--c:var(--{c})">{t}</h4>' for t, c, _ in _MOTIVE)
    + "".join(f'<p class="mtv5__i"><b>{it[k][0]}</b><span>{it[k][1]}</span></p>'
              for k in range(3) for _, _, it in _MOTIVE)
    + '<p class="mtv5__cost"><b>Ce costă</b>dependența de furnizor, limitele de cereri, cheile de acces. '
      "Un fișier publicat și datat, ca SCI de pe HDX, rămâne o alegere bună.</p></div>")

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


# ===========================================================================
#  Cum arată o cerere
# ===========================================================================

# Pe slide: adresa primei cereri, în trei bucăți colorate, fiecare cu
# componentele ei dedesubt; apoi alte endpoint-uri pe aceeași adresă de bază.
def _bucata(cod, et, sens, parti, c):
    return (f'<div class="adr4__b" style="--c:var(--{c})"><code class="adr4__u">{cod}</code>'
            f'<b>{et}</b><small>{sens}</small><dl>'
            + "".join(f"<dt><code>{a}</code></dt><dd>{b}</dd>" for a, b in parti) + "</dl></div>")

ADRESA_SLIDE = (
    '<div class="adr4"><div class="adr4__url">'
    + _bucata("https://api.worldbank.org/v2", "adresa de bază", "serverul",
              [("https://", "protocolul"), ("api.worldbank.org", "serverul"), ("/v2", "versiunea")], "ardezie")
    + _bucata("/country/RO/indicator/SP.POP.TOTL", "endpoint-ul", "resursa cerută",
              [("/country/RO", "țara"), ("/indicator/SP.POP.TOTL", "indicatorul: populația")], "accent")
    + _bucata("?date=2024&amp;format=json", "parametrii", "filtrele",
              [("date=2024", "anul"), ("format=json", "formatul"), ("&amp;", "leagă perechile")], "ambra")
    + "</div>"
    '<table class="tabel adr4__alte"><thead><tr><th>Alt endpoint, aceeași adresă de bază</th><th>Ce întoarce</th></tr></thead><tbody>'
    "<tr><td><code>/country</code></td><td>lista țărilor</td></tr>"
    "<tr><td><code>/indicator</code></td><td>lista indicatorilor</td></tr>"
    "<tr><td><code>/country/RO/indicator/SP.URB.TOTL.IN.ZS</code></td><td>ponderea populației urbane din România</td></tr>"
    "</tbody></table></div>")

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
        {"t": "?format=json&date=2022:2024", "e": "parametri",
         "kv": ["format=json", "date=2022:2024"]},
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
            "(formatul, anii).</p>"
            "<p><b>Parametrii sunt dicționarul <code>params</code></b> din requests: biblioteca "
            "îi adaugă la adresă și codifică automat caracterele speciale.</p></div>"
            '<div class="c2-dict" style="margin-top:10px"><code>{"format": "json", "date": "2022:2024"}</code><i>→</i>'
            "<code>?format=json&amp;date=2022%3A2024</code></div>",
}

sl("s11", "Cum arată o cerere", "Adresa unei cereri",
   "<h2>Adresa unei cereri</h2>"
   "<p class=\"cheie\">Adresa de bază arată serverul, endpoint-ul arată resursa cerută, "
   "iar parametrii o filtrează.</p>"
   + ADRESA_SLIDE,
   manual=
   "<h2>Adresa unei cereri</h2>"
   "<p>O cerere către un API REST pornește de la o adresă. Adresa are trei părți: adresa de "
   "bază, aceeași pentru tot API-ul, care arată serverul și versiunea; endpoint-ul, care arată "
   "resursa cerută; și parametrii, care o filtrează. Un <strong>endpoint</strong> este, deci, "
   "adresa la care se cere o anumită resursă, iar fiecare endpoint întoarce altceva.</p>"
   + ADRESA_SLIDE
   + "<p>O adresă pare un simplu șir de caractere, dar are o gramatică. Când o cerere eșuează, "
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

sl("s8", "Cum arată o cerere", "Aceeași întrebare, patru stiluri",
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


# Pe slide: cele două mesaje, unul sub altul; fiecare rând are partea, textul
# ei exact și, în dreapta, ce spune. Rândul gol rămâne în manual.
def _rh(cls, parte, text, sens, gol=False):
    g = ' class="gol"' if gol else ""
    return (f'<div class="htp2__r {cls}"><span>{parte}</span>'
            f'<code{g}>{text}</code><em>{sens}</em></div>')

HTTP_SLIDE = (
    '<div class="htp2">'
    '<section><h4>Cererea<small>scriptul → serverul</small></h4>'
    + _rh("p1", "prima linie", "GET /v2/country/RO/indicator/SP.POP.TOTL?date=2024 HTTP/1.1", "metoda și adresa")
    + _rh("p2", "antete", "Host: api.worldbank.org", "detalii despre cerere")
    + _rh("p4", "corp", "gol", "o cerere GET nu are corp", True)
    + "</section>"
    '<section><h4>Răspunsul<small>serverul → scriptul</small></h4>'
    + _rh("p1", "prima linie", "HTTP/1.1 200 OK", "codul de stare")
    + _rh("p2", "antete", "Content-Type: application/json", "formatul corpului")
    + _rh("p4", "corp", '[{"page": 1, …}, [{"date": "2024", "value": 19051804}]]', "datele cerute")
    + "</section></div>")

HTTP_MANUAL = (
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
   "<p class=\"cheie\">Scriptul trimite o cerere, serverul trimite un răspuns: două mesaje text, cu aceeași structură.</p>"
   + HTTP_SLIDE,
   manual=
   "<h2>Mesajul HTTP</h2>"
   "<p>Tot ce face un API REST trece prin HTTP, iar HTTP e, la bază, un schimb de două "
   "mesaje text. Cererea și răspunsul au aceeași structură: o primă linie, un șir de "
   "antete de forma <code>Nume: valoare</code>, un rând gol și, opțional, corpul.</p>"
   + HTTP_MANUAL
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
#  De unde vin datele
# ===========================================================================


SURSE_SLIDE = (
    '<table class="tabel srs2"><thead><tr><th>Domeniul</th><th>Deschise, fără cheie</th><th>Cu cheie, cont sau plată</th></tr></thead><tbody>'
    '<tr class="on"><td>Statistici oficiale</td><td>Eurostat, Banca Mondială, data.gov.ro</td><td>microdate, cu acord de acces</td></tr>'
    "<tr><td>Hărți și locuri</td><td>Eurostat GISCO, OpenStreetMap</td><td>Google Maps Platform</td></tr>"
    "<tr><td>Rețele sociale și web</td><td>Wikipedia</td><td>YouTube Data API, X API</td></tr>"
    "<tr><td>Vreme și senzori</td><td>Open-Meteo</td><td>OpenWeatherMap</td></tr>"
    "<tr><td>Servicii AI</td><td></td><td>OpenAI, Anthropic, Hugging Face</td></tr>"
    "</tbody></table>")

# Pe slide: cele patru surse ale proiectului, câte una în fiecare colț, fiecare cu
# legătura spre date și spre documentație.
def _sursa(nume, cum, ce, date, doc, c):
    return (f'<div class="srs3__s" style="--c:var(--{c})"><h4>{nume}</h4><small>{cum}</small><p>{ce}</p>'
            f'<span class="srs3__l"><a class="leg" href="{date}" target="_blank" rel="noopener">Datele ↗</a>'
            f'<a class="leg" href="{doc}" target="_blank" rel="noopener">Documentația ↗</a></span></div>')

SURSE_PROIECT = (
    '<div class="srs3">'
    + _sursa("Social Connectedness Index", "fișier, de pe HDX · de la cursul 1", "legăturile de prietenie dintre locuri",
             "https://data.humdata.org/dataset/social-connectedness-index",
             "https://pages.stern.nyu.edu/~jstroebe/PDF/JKKS_SCI.pdf", "roza")
    + _sursa("Banca Mondială", "API REST public, fără cheie", "indicatori pe țară și an",
             "https://data.worldbank.org/indicator/SP.POP.TOTL?locations=RO",
             "https://datahelpdesk.worldbank.org/knowledgebase/articles/898581", "accent")
    + _sursa("Eurostat", "API REST public, fără cheie", "indicatori pe regiuni NUTS",
             "https://ec.europa.eu/eurostat/databrowser/",
             "https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access/api-getting-started", "ambra")
    + _sursa("Eurostat, migrația", "setul migr_pop1ctz, același API", "câți cetățeni ai unei țări trăiesc în alta",
             "https://ec.europa.eu/eurostat/databrowser/view/migr_pop1ctz/default/table",
             "https://json-stat.org/format/", "ardezie")
    + "</div>")

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
     "formatul răspunsurilor Eurostat, pentru detalii"),
    ("requests: ghidul rapid", "https://requests.readthedocs.io/en/latest/user/quickstart/",
     "<code>get</code>, <code>params</code>, <code>status_code</code>, <code>json()</code>"),
    ("MDN: codurile de stare HTTP", "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status",
     "fiecare cod, de la 200 la 503"),
])

sl("s15", "De unde vin datele", "Sursele proiectului",
   "<h2>Sursele proiectului</h2>"
   "<p class=\"cheie\">Un fișier, de la cursul 1, și două API-uri, de azi; fiecare cu datele și documentația lui.</p>"
   + SURSE_PROIECT
   + '<p class="c2__jos">Alte surse cu API deschis: data.gov.ro, OpenStreetMap, Open-Meteo, Wikipedia. Lista, în manual.</p>',
   manual=
   "<h2>Sursele proiectului</h2>"
   "<p>Proiectul folosește un fișier, SCI, descărcat la cursul 1, și două API-uri publice. Întâi "
   "Banca Mondială, care are un format de răspuns simplu, o listă de înregistrări. Apoi Eurostat, "
   "cu indicatorii pe regiuni și cu migrația, într-un format diferit, JSON-stat.</p>"
   + SURSE_PROIECT
   + "<p>Când o cerere eșuează, se consultă întâi documentația: acolo sunt descriși "
     "parametrii, valorile acceptate și sensul lor.</p>"
   + SURSE_DOC
   + "<h3>Alte surse accesibile prin API</h3>"
   "<p>Aproape orice sursă de date importantă are azi un API. Pentru o analiză contează "
   "două lucruri: ce fel de date oferă sursa și în ce condiții se poate accesa. Condițiile se "
   "schimbă în timp, așa că se verifică în documentația fiecărei surse, la data colectării.</p>"
   + SURSE_SLIDE
   + "<p>Cheile de acces sunt personale: nu se scriu în cod și nu se publică, ci se păstrează în "
     "variabile de mediu. Extragerea din pagini web (<em>web scraping</em>) e soluția pentru "
     "situațiile fără API, cu două riscuri: pagina se poate schimba fără avertisment, iar "
     "condițiile de utilizare pot interzice extragerea.</p>")


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
    "<tr><td>cererea: metoda, adresa, parametrii</td><td><code>raspuns = requests.get(url, params=parametri)</code></td></tr>"
    "<tr><td>codul de stare</td><td><code>raspuns.status_code</code></td></tr>"
    "<tr><td>antetele</td><td><code>raspuns.headers</code></td></tr>"
    "<tr><td>corpul, în JSON</td><td><code>raspuns.json()</code></td></tr>"
    "<tr><td>adresa construită, după codificare</td><td><code>raspuns.url</code></td></tr>"
    "</tbody></table>")

# Pe slide: fiecare parte a mesajului HTTP, în culoarea ei de la slide-ul cu
# mesajul, și numele ei în requests.
def _rq(cls, parte, cod, rez=""):
    r = f'<span class="c">  # {rez}</span>' if rez else ""
    return f'<div class="rq3__r {cls}"><span>{parte}</span><i>→</i><code>{cod}{r}</code></div>'

REQ_SLIDE = (
    '<div class="rq3"><div class="rq3__cap"><span>În mesajul HTTP</span><i></i><span>În Python, cu requests</span></div>'
    + _rq("p0", "cererea", "raspuns = requests.get(url, params=parametri)")
    + _rq("p1", "codul de stare", "raspuns.status_code", "200")
    + _rq("p2", "antetele", "raspuns.headers", "Content-Type: application/json")
    + _rq("p4", "corpul", "raspuns.json()", "liste și dicționare")
    + "</div>")

sl("s16", "requests", "Aceeași cerere, în Python",
   "<h2>Aceeași cerere, în Python</h2>"
   "<p class=\"cheie\">Fiecare parte a mesajului HTTP are un nume în requests. Ordinea: cererea, codul de stare, abia apoi corpul.</p>"
   + REQ_SLIDE,
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
   "orice cod 4xx sau 5xx într-o excepție, deci colectarea se oprește exact acolo unde apare problema. "
   "La colectările lungi, <code>timeout=30</code> în <code>requests.get</code> oprește după 30 de secunde "
   "o cerere la care serverul nu mai răspunde; altfel, programul ar aștepta la nesfârșit.</p>"
   + ix("pas", "Prima cerere din caiet, pas cu pas", {
       "fisier": f"{CAIET} · 3. Banca Mondială: prima cerere",
       "intro": "Prima cerere din caiet: populația României, de la Banca Mondială.",
       "cod": "url = \"" + URL_BM + "\"\n"
              "parametri = {\"format\": \"json\", \"date\": \"2022:2024\"}\n\n"
              "raspuns = requests.get(url, params=parametri)\n"
              "print(raspuns.url)\n"
              "print(raspuns.status_code)\n\n"
              "date = raspuns.json()\n"
              "meta = date[0]\nvalori = date[1]",
       "pasi": [
           {"l": 1, "set": {"url": {"t": "str", "v": URL_BM}},
            "txt": "Adresa: serverul, țara (RO) și indicatorul (populația totală)."},
           {"l": 2, "set": {"parametri": {"t": "dict", "v": {"format": "json", "date": "2022:2024"}}},
            "txt": "Filtrele stau într-un dicționar: formatul și anii."},
           {"l": 4, "set": {"raspuns": {"t": "Response", "v": "<Response [200]>"}},
            "txt": "<code>requests.get</code> trimite cererea; cu <code>params=</code>, biblioteca construiește adresa."},
           {"l": 5, "out": URL_BM + "?format=json&date=2022%3A2024",
            "txt": "Adresa construită: „:” a devenit <code>%3A</code>."},
           {"l": 6, "out": "200", "txt": "Codul de stare, verificat înaintea corpului."},
           {"l": 8, "set": {"date": {"t": "list", "v": [{"page": 1, "pages": 1, "per_page": 50, "total": 3}, ["…", "…", "…"]]}},
            "txt": "<code>.json()</code> transformă corpul în liste și dicționare."},
           {"l": 9, "set": {"meta": {"t": "dict", "v": {"page": 1, "pages": 1, "per_page": 50, "total": 3}}}, "hl": {"var": "date", "k": 0},
            "txt": "Poziția 0: câte valori sunt (3) și pe câte pagini (1): a venit tot."},
           {"l": 10, "set": {"valori": {"t": "list", "v": ["2024: 19051804", "2023: 19061062", "2022: …"]}}, "hl": {"var": "date", "k": 1},
            "txt": "Poziția 1: valorile, de la anul cel mai recent."},
       ]})
   + DOC_REQ)


# Exercițiul: în stânga, ce a venit în răspuns; în dreapta, trei rânduri de cod,
# fiecare cu un gol. Nimic de tastat liber: se completează golurile și se rulează.
RASPUNS_TEXT = """[{"page": 1, "pages": 1, "total": 3},
 [{"date": "2024", "value": 19051804},
  {"date": "2023", "value": 19061062}, …]]"""

COD_RASPUNS = {
    "id": "c2-cod-raspuns", "fisier": CAIET,
    "sarcina": "<b>1</b> codul de stare · <b>2</b> câte valori există · <b>3</b> populația în 2024",
    "cod": "print(raspuns.{{1}})\n"
           "print(raspuns.json()[0][{{2}}])\n"
           "print(raspuns.json()[{{3}}][0][\"value\"])",
    "goluri": {"1": {"ok": ["status_code"], "ajutor": "atributul"},
               "2": {"ok": ["\"total\"", "'total'"], "ajutor": "cheia"},
               "3": {"ok": ["1"], "ajutor": "poziția"}},
    "indiciu": "Codul de stare e atributul <code>status_code</code> (slide-ul de dinainte). În stânga: "
               "paginarea e pe poziția 0, cu cheia <code>\"total\"</code>; valorile sunt pe poziția 1.",
    "iesire": "200\n3\n19051804",
    "laBine": "Codul de stare, apoi corpul: aceeași ordine la orice cerere.",
    "laRau": "Cheia se scrie între ghilimele; pozițiile încep de la 0.",
    "explicatie": "<code>raspuns.status_code</code> e 200, deci cererea a reușit. <code>raspuns.json()</code> "
                  "e o listă: pe poziția 0 paginarea, unde <code>\"total\"</code> spune câte valori există; "
                  "pe poziția 1 valorile, de la anul cel mai recent.",
}

INSPECT_HTML = (
    '<div class="wbv"><figure class="wbv__json"><figcaption>Ce conține raspuns.json()</figcaption><pre><code>'
    + RASPUNS_TEXT + "</code></pre>"
    '<p class="wbv__leg"><span>poziția 0</span>paginarea<br><span>poziția 1</span>valorile, câte una pe an</p></figure>'
    + '<div class="wbv__ex">' + ix("cod", "Trei rânduri, trei goluri", COD_RASPUNS) + "</div></div>")

sl("s17", "requests", "Exercițiu: ce a venit în răspuns",
   "<h2>Exercițiu: ce a venit în răspuns</h2>"
   "<p class=\"cheie\">Cererea a rulat, iar răspunsul e în variabila <code>raspuns</code>. "
   "Se completează cele trei goluri de dedesubt, apoi Rulează.</p>"
   + INSPECT_HTML,
   manual=
   "<h2>Exercițiu: ce a venit în răspuns</h2>"
   "<p>Cererea din caiet a rulat, iar răspunsul se află în variabila <code>raspuns</code>. În stânga e "
   "conținutul lui, simplificat; în dreapta, trei rânduri de cod care scot din el codul de stare, "
   "numărul de valori și populația din 2024.</p>"
   + INSPECT_HTML
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
                     "venit 50. Restul vin doar dacă se cer paginile 2, 3 și 4."}

# Exercițiul: funcția din caiet (4.3), cu trei goluri. Prima cerere ia partea cu
# paginarea, [0]; bucla cere fiecare pagină și ia partea cu valorile, [1].
COD_PAGINI = {
    "id": "c2-cod-pagini", "fisier": f"{CAIET} · 4.3. O funcție care aduce toate paginile",
    "sarcina": "<b>1</b> partea cu paginarea · <b>2</b> câte pagini sunt · <b>3</b> partea cu valorile",
    "cod": "def cere_tot(url, parametri):\n"
           "    meta = requests.get(url, params=parametri).json()[{{1}}]       # câte pagini sunt\n"
           "    toate = []\n"
           "    for pagina in range(1, meta[{{2}}] + 1):                       # fiecare pagină\n"
           "        valori = requests.get(url, params={**parametri, \"page\": pagina}).json()[{{3}}]\n"
           "        toate = toate + valori\n"
           "        print(\"pagina\", pagina, \"din\", meta[\"pages\"], \"·\", len(toate), \"valori\")\n"
           "    return toate\n\n"
           "valori = cere_tot(url, {\"format\": \"json\", \"date\": \"1960:2024\", \"per_page\": 20})",
    "goluri": {"1": {"ok": ["0"], "ajutor": "poziția"},
               "2": {"ok": ["\"pages\"", "'pages'"], "ajutor": "cheia"},
               "3": {"ok": ["1"], "ajutor": "poziția"}},
    "indiciu": "Răspunsul Băncii Mondiale e o listă cu două părți: pe poziția 0 paginarea, unde cheia "
               "<code>\"pages\"</code> spune câte pagini sunt; pe poziția 1 valorile.",
    "iesire": "pagina 1 din 4 · 20 valori\npagina 2 din 4 · 40 valori\npagina 3 din 4 · 60 valori\npagina 4 din 4 · 65 valori",
    "laBine": "Prima cerere află că sunt 4 pagini (65 de valori, câte 20); bucla le cere pe toate patru și le adună.",
    "laRau": "Pozițiile încep de la 0; cheia se scrie între ghilimele.",
    "explicatie": "Prima cerere ia doar partea cu paginarea, <code>[0]</code>: de acolo, <code>meta[\"pages\"]</code> "
                  "spune câte pagini sunt. Bucla trece prin paginile 1, 2, 3 și 4 și din fiecare ia partea cu "
                  "valorile, <code>[1]</code>. La final, lista are toate cele 65 de valori."}

PAGINI = {"ani": list(range(2024, 1959, -1)), "optiuni": [10, 50, 1000], "implicit": 50}

CHEI_PAGINARE = tabel(["Cheia", "Ce spune"], [
    ["~total", "câte valori există în total"],
    ["~per_page", "câte valori încap pe o pagină"],
    ["~pages", "câte pagini sunt: <code>total ÷ per_page</code>, rotunjit în sus"],
    ["~page", "ce pagină a venit acum"],
])

sl("s18", "requests", "Paginarea",
   "<h2>Paginarea</h2>"
   "<p class=\"cheie\">Implicit, Banca Mondială trimite doar 50 de valori. Pentru 65 de ani, ultimii 15 "
   "stau pe pagina 2 și vin doar dacă sunt ceruți.</p>"
   + ix("pagini2", "Populația României, 1960 la 2024: 65 de valori", PAGINI)
   + '<p class="c2__jos"><code>pages</code> = <code>total</code> ÷ <code>per_page</code>, rotunjit în sus. '
   "Dacă e 1, a venit tot; dacă e mai mare, restul paginilor trebuie cerute.</p>",
   manual=
   "<h2>Paginarea</h2>"
   "<p>Un API nu trimite un set mare dintr-o dată. Îl împarte în pagini, ca fiecare răspuns să rămână "
   "mic și rapid. La Banca Mondială, o pagină are implicit 50 de valori. Problema este că serverul nu "
   "anunță că a trimis doar o parte: codul este tot 200 și nu apare nicio eroare. Singurul semn este "
   "primul element al răspunsului, cel cu paginarea.</p>"
   + CHEI_PAGINARE
   + "<p>Dacă <code>pages</code> este 1, a venit tot. Dacă este mai mare, a venit doar prima pagină, "
     "iar celelalte trebuie cerute.</p>"
   + ix("pagini2", "Populația României, 1960 la 2024: 65 de valori", PAGINI)
   + "<h3>Ce vine fără per_page</h3>"
   "<p>Populația României pentru 1960 la 2024 are 65 de valori. Cererea fără <code>per_page</code> "
   "primește 50, de la 2024 la 1975; anii 1960 la 1974 stau pe pagina 2. Pagina a doua se cere cu "
   "aceeași cerere și un singur parametru în plus, <code>page</code>:</p>"
   "<pre><code>parametri = {\"format\": \"json\", \"date\": \"1960:2024\"}\n"
   "meta, valori = requests.get(url, params=parametri).json()\n"
   "print(meta[\"total\"], meta[\"pages\"], len(valori))     # 65 2 50\n\n"
   "meta2, valori2 = requests.get(url, params={**parametri, \"page\": 2}).json()\n"
   "print(len(valori2))                                  # 15</code></pre>"
   "<p><code>{**parametri, \"page\": 2}</code> este o copie a dicționarului, cu <code>page</code> "
   "adăugat; dicționarul inițial rămâne neschimbat.</p>"
   + ix("prezice", "Câte valori au venit", PREZICE_PAGINI)
   + "<h3>Două căi spre tot răspunsul</h3>"
   "<p><strong>Pagini mari.</strong> Cu <code>per_page=1000</code>, cei 65 de ani vin într-o singură "
   "pagină. Calea e scurtă, dar „destul de mare” depinde de cerere: pentru cele 37 de țări ale "
   "proiectului și 65 de ani sunt 2.405 valori, deci tot 3 pagini.</p>"
   "<p><strong>O funcție care cere toate paginile.</strong> Ea face ce s-ar face de mână: o primă "
   "cerere află câte pagini sunt, apoi o buclă le cere pe toate, de la 1 la ultima, și adună valorile. "
   "Funcția nu se schimbă când datele cresc: cere câte pagini sunt.</p>"
   + ix("cod", "Toate paginile, cu o funcție", COD_PAGINI)
   + "<p>În caiet, <code>cere_bm</code> le folosește pe amândouă: cere pagini mari, ca să fie cât mai "
     "puține cereri, iar <code>cere_tot</code> le aduce pe toate. Banca Mondială întoarce valorile de la "
     "anul cel mai recent spre cel mai vechi.</p>"
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


sl("s18x", "requests", "Exercițiu: toate paginile",
   "<h2>Exercițiu: toate paginile, cu o funcție</h2>"
   "<p class=\"cheie\">O cerere aduce o singură pagină. Funcția întreabă întâi câte pagini sunt, apoi le "
   "cere pe toate. Se completează cele trei goluri, apoi Rulează.</p>"
   + ix("cod", "Toate paginile, cu o funcție", COD_PAGINI),
   manual="")


# ===========================================================================
#  Eurostat
# ===========================================================================

EUROSTAT_BAZA = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"

# Pe slide: cererea din caiet, cu setul și filtrele colorate, și tabelul care
# vine din ea. Cum se desface răspunsul rămâne în manual.
EU_FUNCTIE = (
    '<div class="euf"><div class="euf__cod">'
    '<pre><code>cere_eurostat(<span class="d">"demo_r_d3dens"</span>,\n'
    '    {<span class="f">"geo": ["RO113", "RO111"]</span>,\n'
    '     <span class="f">"time": 2024</span>})</code></pre>'
    '<dl class="euf__leg"><dt class="d">setul</dt><dd>densitatea populației</dd>'
    '<dt class="f">filtrele</dt><dd>ce regiuni, ce an</dd></dl></div>'
    '<i class="euf__s" aria-hidden="true">→</i>'
    '<figure class="euf__t"><figcaption>tabelul</figcaption>'
    '<table class="tabel"><thead><tr><th>geo</th><th>valoare</th></tr></thead><tbody>'
    '<tr><td>RO111 · Bihor</td><td>74,2</td></tr>'
    '<tr><td>RO113 · Cluj</td><td>104,8</td></tr>'
    "</tbody></table></figure></div>")

# În manual: ce face funcția. Stânga, valorile cu numărul lor; mijloc, ce număr
# are fiecare regiune; dreapta, tabelul. Aceeași culoare, același număr.
EU_NUMERE = (
    '<div class="eun">'
    '<div class="eun__r">'
    '<figure><figcaption><code>value</code><span>valorile, cu numărul lor</span></figcaption>'
    '<pre><code>{<span class="n0">"0": 74.2</span>,\n <span class="n1">"1": 104.8</span>}</code></pre></figure>'
    '<figure><figcaption><code>dimension → geo → index</code><span>ce număr are fiecare regiune</span></figcaption>'
    '<pre><code>{<span class="n0">"RO111": 0</span>,\n <span class="n1">"RO113": 1</span>}</code></pre></figure>'
    '<i class="eun__s" aria-hidden="true">→</i>'
    '<figure><figcaption>tabelul<span>potrivite după număr</span></figcaption>'
    '<table class="tabel eun__t"><thead><tr><th>geo</th><th>valoare</th></tr></thead><tbody>'
    '<tr class="n0"><td>RO111 · Bihor</td><td>74,2</td></tr>'
    '<tr class="n1"><td>RO113 · Cluj</td><td>104,8</td></tr>'
    "</tbody></table></figure></div></div>")

# În manual: migrația, cu ce fixează cererea și ce rămâne deschis.
EU2_HTML = (
    '<p class="eu2__adr"><code>' + EUROSTAT_BAZA + '<b>migr_pop1ctz</b>?citizen=RO&amp;sex=T&amp;age=TOTAL&amp;unit=NR&amp;time=2024</code></p>'
    '<table class="tabel eu2"><tbody>'
    "<tr><td>Fixate, câte o valoare</td><td><code>citizen=RO</code> · <code>sex=T</code> · <code>age=TOTAL</code> · "
    "<code>unit=NR</code> · <code>time=2024</code></td></tr>"
    '<tr class="on"><td>Variază, un rând pe cod</td><td><code>geo</code> (țara de reședință)</td></tr>'
    "</tbody></table>")

sl("s20", "Eurostat", "Eurostat: o funcție, un tabel",
   "<h2>Eurostat: o funcție, un tabel</h2>"
   "<p class=\"cheie\">Cererea numește setul și filtrele, ca la Banca Mondială. "
   "Funcția <code>cere_eurostat</code> aduce direct tabelul.</p>"
   + EU_FUNCTIE
   + '<p class="c2__jos"><code>geo</code> cere regiuni anume; <code>geoLevel</code>, un nivel întreg: '
     '<code>"nuts3"</code> aduce toate județele Europei.</p>',
   manual=
   "<h2>Eurostat: date pe regiuni</h2>"
   "<p>Eurostat publică indicatori pe regiuni NUTS: țări, regiuni mari (NUTS 2) și județe sau "
   "echivalentele lor (NUTS 3). O cerere numește setul și filtrele: o regiune "
   "(<code>geo</code>) sau un nivel întreg (<code>geoLevel</code>), anul (<code>time</code>), unitatea "
   "(<code>unit</code>) și altele, după set. Codul unui set și filtrele lui se găsesc în "
   '<a class="leg" href="https://ec.europa.eu/eurostat/databrowser/" target="_blank" rel="noopener">Data Browser</a>, '
   "unde tabelul se poate vedea înainte de a fi cerut din cod.</p>"
   + EU_FUNCTIE
   + "<p>În caiet, funcția <code>cere_eurostat</code> face cererea și întoarce direct un tabel, un rând pe "
     "regiune. Se folosește la fel ca <code>cere_bm</code>: primul argument este setul, al doilea sunt "
     "filtrele. Regula ei: într-o cerere variază un singur lucru, regiunea; celelalte filtre au câte o "
     "singură valoare, iar dacă lipsește unul, funcția spune care.</p>"
   + "<h3>Ce face funcția</h3>"
   "<p>Răspunsul are alt format decât la Banca Mondială, care trimite înregistrări, fiecare cu țara și "
   "anul ei. Eurostat trimite valorile numerotate și, separat, ce număr are fiecare regiune; funcția le "
   "potrivește.</p>"
   + EU_NUMERE
   + "<p>Numerele urmează ordinea Eurostat, nu ordinea din cerere, deci se citesc din răspuns, nu se "
     "presupun. Formatul se numește JSON-stat: codurile se scriu o singură dată, nu pe fiecare rând, așa că "
     "răspunsul rămâne mic și când are zeci de mii de valori. O valoare care lipsește nu apare deloc în "
     "<code>value</code>; în tabel devine <code>None</code>, nu zero.</p>"
   + "<h3>Migrația, a doua sursă a proiectului</h3>"
   "<p>Setul <code>migr_pop1ctz</code> spune câți oameni cu o anumită cetățenie trăiesc într-o "
   "țară, la 1 ianuarie. Un rând e o pereche de țări, ca la SCI, dar cu direcție. Cetățenia "
   "e preferată țării nașterii (<code>migr_pop3ctb</code>) pentru că mai multe țări mari, "
   "printre ele Germania, nu raportează nașterile pe țări. Și cetățenia are o limită: persoanele "
   "care au dobândit cetățenia țării de reședință nu mai apar ca migranți.</p>"
   "<p>Pentru o întrebare ca „unde trăiesc cetățenii români” se fixează și cetățenia; variază doar țara "
   "de reședință. Tabelul cu toate perechile, pentru proiect, se cere în caiet țară cu țară: pentru "
   "fiecare țară de reședință, toate cetățeniile, iar tabelele se lipesc la final.</p>"
   + EU2_HTML
   + "<p>Doar o parte dintre țări raportează pe țări de cetățenie; o valoare lipsă nu "
   "înseamnă zero. Harta din <a class=\"leg\" href=\"../../c1-introducere-si-mediu/tutorial/#s5m\">cursul 1</a> "
   "folosește exact aceste date: 1.073.196 de cetățeni români în Italia, la 1 ianuarie 2024. "
   "Aceasta este întrebarea empirică a semestrului: Italia, țara cu cei mai mulți cetățeni români, e abia a "
   "șasea după indicele SCI.</p>"
   + ix("pas", "Unde trăiesc cetățenii români", {
       "fisier": f"{CAIET} · 8. Migrația: două țări pe un rând",
       "intro": "Migrația: unde trăiesc cetățenii români.",
       "cod": "filtre = {\"sex\": \"T\", \"age\": \"TOTAL\", \"unit\": \"NR\", \"time\": 2024}\n\n"
              "romani = cere_eurostat(\"migr_pop1ctz\", {**filtre, \"citizen\": \"RO\"})\n"
              "romani.sort_values(\"valoare\", ascending=False).head(6)",
       "pasi": [
           {"l": 1, "set": {"filtre": {"t": "dict", "v": {"sex": "T", "age": "TOTAL", "unit": "NR", "time": 2024}}},
            "txt": "Filtrele comune: toată populația, în număr de persoane, în 2024."},
           {"l": 3, "set": {"romani": {"t": "DataFrame", "v": {"cols": ["geo", "valoare"],
                                                             "rows": [["EU27_2020", "None"], ["BE", 127539], ["BG", 1595], ["…", "…"]],
                                                             "nota": "un rând pe țară de reședință"}}},
            "txt": "Cetățenia fixată la RO; variază doar țara. <code>None</code>: Eurostat nu are valoarea."},
           {"l": 4, "out": "geo    valoare\n RO  18780989\n IT   1073196\n DE    776424\n ES    620463\n FR    161220\n AT    153427",
            "txt": "Ordonate descrescător. Primul rând e chiar România, cu românii din țară; urmează Italia, Germania și Spania."},
       ]})
   + nota("Coduri care pot produce erori",
          "Eurostat scrie Grecia <code>EL</code>, nu <code>GR</code>. Iar <code>NA</code> e Namibia, pe "
          "care pandas o interpretează implicit ca valoare lipsă. Se reiau la curățare, la cursul 4."))


# ===========================================================================
#  Prima colectare și echipele
# ===========================================================================

# Exercițiul pregătește alegerea echipei: aceeași cerere, alt indicator și alți
# ani. Restul cererii rămâne neschimbat.
COD_INDICATOR = {
    "id": "c2-cod-indicator", "fisier": f"{CAIET} · 9. Echipele: ce date încercați",
    "sarcina": "Aceeași cerere, pentru ponderea populației urbane din România, cod "
               "<code>SP.URB.TOTL.IN.ZS</code>, în anii 2000 la 2023. Ce se completează?",
    "cod": "url = \"https://api.worldbank.org/v2/country/RO/indicator/{{1}}\"\n"
           "parametri = {\"format\": \"json\", \"date\": {{2}}, \"per_page\": 100}\n\n"
           "raspuns = requests.get(url, params=parametri)\n"
           "meta, valori = raspuns.json()\n"
           "print(meta[\"pages\"], len(valori))",
    "goluri": {"1": {"ok": ["SP.URB.TOTL.IN.ZS"], "ajutor": "codul indicatorului"},
               "2": {"ok": ["\"2000:2023\"", "'2000:2023'"], "ajutor": "anii, ca text"}},
    "indiciu": "Indicatorul stă în cale, după <code>/indicator/</code>. Anii se scriu ca text, "
               "între ghilimele, cu două puncte între primul și ultimul an.",
    "iesire": "1 24",
    "laBine": "O pagină, 24 de valori: câte una pentru fiecare an. Pentru proiect, echipa schimbă la fel indicatorul și anii.",
    "laRau": "Codul indicatorului se scrie exact, cu puncte; anii, ca text: \"2000:2023\".",
    "explicatie": "Calea alege resursa, deci indicatorul se schimbă în <code>url</code>; parametrii "
                  "filtrează, deci anii se schimbă în <code>date</code>. Cu <code>per_page</code> 100, "
                  "cei 24 de ani încap pe o singură pagină.",
}

PASI_COLECTARE = tabel(["Pasul", "Ce se face"], [
    ["1", "se deschide caietul 02 din <code>dsw/curs/</code>, cu kernelul <code>.venv</code>"],
    ["2", "se rulează secțiunile 1 la 5: prima cerere, paginarea, cei trei indicatori"],
    ["3", "se verifică faptul că au venit toate valorile: ultimul rând afișat este „pagina N din N”"],
    ["4", "se salvează tabelul în <code>data/c2/bm.csv</code>"],
])

sl("s21", "Proiectul echipei", "Exercițiu: alt indicator",
   "<h2>Exercițiu: aceeași cerere, alt indicator</h2>"
   "<p class=\"cheie\">Pentru proiect, cererea rămâne aceeași; se schimbă doar indicatorul, în cale, "
   "și anii, în parametri.</p>"
   + ix("cod", "Ponderea populației urbane", COD_INDICATOR),
   manual=
   "<h2>Prima colectare, în caiet</h2>"
   "<p>Colectarea se face în caietul 02, din <code>dsw/curs/</code>. Căile pornesc de acolo: "
   "<code>data/c2/bm.csv</code> înseamnă <code>dsw/curs/data/c2/bm.csv</code>. Folderul este creat de "
   "prima celulă a caietului, cu <code>Path(\"data/c2\").mkdir(exist_ok=True)</code>.</p>"
   + PASI_COLECTARE
   + "<p>Pentru proiect, echipa caută un indicator potrivit întrebării ei și îl cere la fel. "
     "Cererea nu se rescrie: se schimbă indicatorul, în cale, și anii, în parametri.</p>"
   + ix("cod", "Ponderea populației urbane", COD_INDICATOR)
   + "<p>În caiet, cererea pentru proiect este o funcție, <code>cere_bm</code>, care primește "
     "indicatorul și țările și folosește <code>cere_tot</code>, deci aduce toate paginile. Pentru indicatorul "
     "echipei se schimbă doar codul și, la nevoie, anii:</p>"
   + "<pre><code>def cere_bm(indicator, tari, ani=\"2022:2024\"):\n"
     "    url = \"https://api.worldbank.org/v2/country/\" + \";\".join(tari) + \"/indicator/\" + indicator\n"
     "    valori = cere_tot(url, {\"format\": \"json\", \"date\": ani, \"per_page\": 1000})\n"
     "    tabel = pd.json_normalize(valori)[[\"country.id\", \"date\", \"value\"]]\n"
     "    tabel.columns = [\"tara\", \"an\", \"valoare\"]\n"
     "    return tabel\n\n"
     "urban = cere_bm(\"SP.URB.TOTL.IN.ZS\", [\"RO\"], ani=\"2000:2023\")\n"
     "urban.to_csv(\"data/c2/urban_ro.csv\", index=False)</code></pre>"
   + nota("Fișierele mari și cheile de acces",
          "Datele de la curs rămân în <code>curs/data/c2</code>, pe calculatorul personal. Fișierele de zeci de "
          "megabytes și cheile de acces nu se trimit nimănui: se păstrează codul care le colectează, "
          "iar datele se refac din el."))

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


_ETAPE8 = ["Introducere", "API", "Git", "Curățare", "Agregare", "Explorare", "Model", "Raport"]
PROGRES = ('<ol class="prg">' + "".join(
    f'<li class="{"gata" if k <= 2 else "prg__urm" if k == 3 else ""}"><span>{k}</span><small>{t}</small></li>'
    for k, t in enumerate(_ETAPE8, 1)) + "</ol>")

sl("s22", "Mai departe", "Pentru cursul următor",
   "<h2>La cursul 3: versionare și colaborare</h2>"
   + PROGRES
   + '<div class="fin4">'
   "<section><h4>Ce urmează</h4>"
   "<p>Git: commit-ul și istoricul</p>"
   "<p>Lucrul în echipă, pe același depozit</p>"
   "<p>Tema echipei</p></section>"
   "<section><h4>Pregătirea</h4>"
   "<p>Caietul 02 rulat, cu datele în <code>curs/data/c2</code></p>"
   "<p>Git instalat: <code>git --version</code></p>"
   "<p>Fișa echipei, de la finalul caietului</p></section>"
   "</div>"
   '<p class="fin4__a"><a class="leg" href="../">Pagina cursului 2</a></p>')

if __name__ == "__main__":
    L.scrie_tot()
