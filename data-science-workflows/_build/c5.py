# -*- coding: utf-8 -*-
"""
Lecția 5: Agregare și baze de date.

Urmează caietul 05_agregare_si_baze_de_date (2 noiembrie 2026): baza
PostgreSQL pe Neon, adresa ei în .env, cele trei tabele din C4 încărcate cu
to_sql, primele interogări (select, where, order by), agregarea cu group by,
aceeași agregare în pandas și baza echipei. Unirea tabelelor a trecut la C4,
unde o face acum caietul 04.

Toate numerele vin din date/c5-baza.json, scos din tabelele produse de
caietele 04 și 05 (regiuni_nuts2, perechi_regiuni, perechi_tari).

Rulare:  python _build/c5.py
"""

import json

from comun import Lectie, ix, verif, tabel, nota, surse, RAD

L = Lectie(5, "c5-agregare-si-baze-de-date", "Agregare și baze de date",
           "Baza de date a echipei pe Neon, adresa ei în .env, primele interogări SQL "
           "și agregarea: de la multe rânduri la un rezumat pe grup, în SQL și în pandas.")
sl = L.sl

D = json.loads((RAD / "date" / "c5-baza.json").read_text(encoding="utf-8"))
T = D["tabele"]
nr = lambda v: f"{v:,}".replace(",", ".")
_NB5 = "05_agregare_si_baze_de_date.ipynb"


# ===========================================================================
#  1. Planul
# ===========================================================================

AGENDA = [
    ("Baza de date", "azi", "Neon, adresa în .env, cele trei tabele din C4."),
    ("SQL", "azi", "O interogare se citește ca o propoziție: select, from, where, order by."),
    ("Agregarea", "azi", "group by, aceeași idee în pandas, capcana mediilor."),
    ("Echipa", "azi", "O singură bază pentru tot proiectul."),
]
PLAN = ix("agenda", "Planul lecției", {"static": True, "titlu": "Planul lecției",
          "etape": [{"nume": n, "unde": u, "text": d} for n, u, d in AGENDA]})

sl("s1", "Cursul", "Planul lecției",
   "<h2>Agregare și baze de date</h2>"
   "<p class=\"cheie\">Tabelele curate din C4 ajung într-un singur loc, comun pentru toată echipa, "
   "și se rezumă: de la multe rânduri la puține.</p>"
   + PLAN
   + nota("Caietul lecției", f"<code>{_NB5}</code>. Interogările din caiet rulează pe baza fiecăruia, pe Neon.", True),
   manual=
   "<h2>Agregare și baze de date</h2>"
   "<p>Până acum datele au stat în fișiere CSV, câte o copie pe fiecare calculator. Lecția le mută într-o "
   "bază de date PostgreSQL, găzduită de Neon: un singur loc, la care se conectează toată echipa, "
   "interogat cu SQL, limbajul comun al bazelor de date.</p>"
   "<p>A doua idee a lecției este agregarea: trecerea de la multe rânduri la puține, un rezumat pe grup "
   "(o medie pe țară, un total pe regiune). Se face în SQL și în pandas, pentru că este aceeași idee.</p>"
   + PLAN
   + nota("Caietul lecției", f"<code>{_NB5}</code>, în <code>dsw/curs/</code>, lângă caietele 01-04.", True))


# ===========================================================================
#  2-5. Baza de date
# ===========================================================================

def _ic_fis():
    return ('<svg class="ic" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.3" '
            'stroke-linejoin="round"><path d="M4 1.5h5.2L12.5 4.8V14.5h-8.5z"/><path d="M9 1.7V5h3.3"/></svg>')

def _ic_pc():
    return ('<svg class="ic" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.3">'
            '<rect x="2.5" y="3" width="11" height="7.5" rx="1"/><path d="M1 13h14"/></svg>')

COPII = (
    '<div class="cp5">'
    '<div class="cp5__p"><h4>Cu fișiere<span>câte o copie pe fiecare calculator</span></h4><ul class="cp5__l">'
    + "".join(f'<li class="{c}">{_ic_pc()}{n}<code>{f}</code></li>' for n, f, c in [
        ("Andrei", "perechi_tari.csv", ""), ("Maria", "perechi_tari_v2.csv", ""),
        ("Ioana", "perechi_tari_final.csv", ""), ("Radu", "perechi_tari (1).csv", "rau"),
        ("Elena", "perechi_tari_FINAL2.csv", "rau")])
    + "</ul></div>"
    '<div class="cp5__p"><h4>Cu o bază de date<span>un singur loc, pentru toți</span></h4>'
    '<div class="cp5__baza"><div class="cp5__cil">PostgreSQL<small>pe Neon</small></div><ul class="cp5__l">'
    + "".join(f'<li>{_ic_pc()}{n}<code>pd.read_sql(...)</code></li>' for n in ["Andrei", "Maria", "Ioana", "Radu", "Elena"])
    + "</ul></div></div>"
    '<p class="cp5__nota">Cinci copii ale aceluiași tabel ajung, în câteva săptămâni, cinci tabele diferite. '
    "O bază are o singură versiune, iar fiecare citește din ea.</p></div>")

V1 = verif("c5-v1", 1,
           "O echipă de cinci are un tabel de 44.253 de rânduri. Care este cel mai bun argument pentru o bază de date?",
           ["44.253 de rânduri sunt prea multe pentru pandas",
            "Cinci persoane au nevoie de o singură copie a datelor, nu de cinci",
            "Bazele de date sunt mai rapide",
            "Este practica obișnuită în industrie"],
           "Pandas lucrează ușor cu sute de mii de rânduri. Problema sunt cinci copii ale aceluiași fișier, "
           "modificate de cinci persoane.")

sl("s2", "Baza de date", "De ce o bază",
   "<h2>Cinci copii sau un singur loc</h2>"
   + COPII,
   manual=
   "<h2>Cinci copii sau un singur loc</h2>"
   "<p>Întrebarea „de la câte rânduri este nevoie de o bază de date” este formulată greșit: dimensiunea "
   "este rareori motivul. Pandas lucrează fără dificultate cu milioane de rânduri, iar datele proiectului "
   "sunt mult sub acest volum. Motivul real este colaborarea: mai multe persoane care lucrează pe aceleași "
   "date au nevoie de o singură versiune a lor.</p>"
   + COPII,
   dupa=V1)


FLUX = {
    "id": "c5-flux-neon",
    "intai": {"q": "Prima interogare din ziua respectivă durează o secundă, a doua o zecime de secundă. De ce?",
              "variante": ["Baza a păstrat rezultatul în memorie", "Componenta de calcul era oprită și a pornit la prima cerere",
                           "Conexiunea la internet era mai lentă la început"],
              "corect": 1,
              "dupa": "Neon oprește componenta de calcul când nu este folosită; datele rămân. Prima cerere o repornește."},
    "buton": "Trimite o interogare",
    "dus": "interogarea este trimisă", "intors": "rândurile sunt returnate", "gata": "rezultatul a fost primit",
    "titlu": "Selectează o componentă",
    "intro": "Patru componente prin care trece un <code>select</code>.",
    "statii": [
        {"n": "Caietul", "et": "pd.read_sql", "ic": "🐍", "c": "ceas",
         "d": "<code>pd.read_sql(\"select ...\", engine)</code>. Interogarea este un text trimis mai departe; "
              "înapoi vine un tabel pandas."},
        {"n": "Conexiunea", "et": "SQLAlchemy și psycopg", "ic": "🔌", "c": "salvie",
         "d": "<code>create_engine</code> citește adresa bazei din <code>.env</code> și deschide un canal criptat."},
        {"n": "Calculul", "et": "pornește la cerere", "ic": "⚡", "c": "accent",
         "d": "Partea care execută interogarea. Se oprește după câteva minute fără cereri; prima cerere o repornește."},
        {"n": "Datele", "et": "permanente", "ic": "🗄️", "c": "text-2",
         "d": "Tabelele propriu-zise, separate de calcul. Rămân pe server și când calculul este oprit."}]}

sl("s3", "Baza de date", "Neon",
   "<h2>PostgreSQL, găzduit de Neon</h2>"
   "<p class=\"cheie\">O bază PostgreSQL obișnuită, pe un server din cloud: nimic de instalat, nimic de ținut pornit.</p>"
   + ix("flux", "Drumul unei interogări", FLUX),
   manual=
   "<h2>PostgreSQL, găzduit de Neon</h2>"
   "<p>Neon oferă PostgreSQL standard, găzduit în cloud. Contul se face cu GitHub, iar planul gratuit "
   "ajunge pentru proiectul cursului.</p>"
   + tabel(["Pasul", "Unde"], [
       ["autentificarea cu contul GitHub", "neon.tech"],
       ["un proiect nou: numele <code>dsw</code>, regiunea Frankfurt", "New Project"],
       ["adresa de conectare (connection string)", "Connect"],
   ])
   + ix("flux", "Drumul unei interogări", FLUX))


ADRESA = (
    '<div class="adr5">'
    + "".join(f'<span class="{c}" style="--pc:var(--{col})"><b>{t}</b><small>{e}</small></span>' for t, e, c, col in [
        ("postgresql://", "felul bazei", "", "accent"),
        ("utilizator", "utilizatorul", "", "ardezie"),
        (":parola", "parola: secretul", "secret", "nu"),
        ("@ep-....neon.tech", "serverul", "", "ambra"),
        ("/neondb", "baza", "", "roza"),
        ("?sslmode=require", "canal criptat", "", "text-3")])
    + "</div>")

CONECTARE = {
    "id": "c5-cod-conectare",
    "indiciu": "Funcția care citește .env, funcția din os care citește o variabilă (get + env) și funcția care face conexiunea.",
    "iesire": "   conexiunea\n0           1", "fisier": "curs/05_agregare_si_baze_de_date.ipynb",
    "sarcina": "Ce lipsește ca adresa să fie citită din <code>.env</code>, nu scrisă în caiet?",
    "cod": "import os\n"
           "import pandas as pd\n"
           "from dotenv import load_dotenv\n"
           "from sqlalchemy import create_engine\n"
           "{{1}}()                                        # citește .env\n"
           "engine = {{3}}(os.{{2}}(\"DATABASE_URL\"))   # conexiunea\n"
           "pd.read_sql(\"select 1 as conexiunea\", engine)",
    "goluri": {
        "1": {"ok": ["load_dotenv"], "ajutor": "funcția"},
        "2": {"ok": ["getenv", "environ.get"], "ajutor": "funcția"},
        "3": {"ok": ["create_engine"], "ajutor": "funcția"}},
    "laBine": "Adresa nu apare nicăieri în caiet, deci nici pe GitHub.",
    "laRau": "Toate trei sunt importate în primele rânduri.",
    "explicatie": "<code>load_dotenv()</code> caută <code>.env</code> în dosarul caietului și în cele de deasupra, "
                  "deci îl găsește și din <code>curs/</code>, și din <code>proiect/notebooks/</code>."}

sl("s4", "Baza de date", "Adresa, în .env",
   "<h2>Adresa bazei stă în .env</h2>"
   + ADRESA
   + "<p>Stă în <code>dsw/.env</code>: <code>DATABASE_URL=postgresql://...</code>. <code>.gitignore</code> conține "
     "<code>.env</code>, deci parola nu ajunge pe GitHub.</p>"
   + ix("cod", "Conectarea", CONECTARE),
   manual=
   "<h2>Adresa bazei stă în .env</h2>"
   "<p>Neon dă o adresă de forma de mai jos. Ea conține tot ce trebuie pentru acces, inclusiv parola, în clar. "
   "De aceea nu se scrie niciodată în caiet și nu ajunge pe GitHub.</p>"
   + ADRESA
   + '<div class="adr5__jos">'
     '<div class="adr5__f"><div><code>dsw/.env</code>, doar pe calculator</div><pre>DATABASE_URL=postgresql://...</pre></div>'
     '<div class="adr5__f"><div><code>.gitignore</code>, în depozit</div><pre><span class="c"># secretele</span>\n.env</pre></div>'
     '<div class="adr5__f"><div><code>.env.exemplu</code>, în depozit</div><pre>DATABASE_URL=postgresql://utilizator:parola@...</pre></div>'
     "</div>"
   + "<p>În <code>dsw/</code> există <code>.env.exemplu</code>: copia lui se numește <code>.env</code>, iar adresa de "
     "exemplu se înlocuiește cu cea de pe Neon. Pachetele noi (<code>sqlalchemy</code>, <code>psycopg</code>, "
     "<code>python-dotenv</code>) sunt în <code>requirements.txt</code>: <code>pip install -r requirements.txt</code>.</p>"
   + ix("cod", "Conectarea", CONECTARE)
   + nota("Dacă apare o eroare",
          "Fișierul se numește exact <code>.env</code> (nu <code>.env.txt</code>), stă în <code>dsw/</code>, iar adresa "
          "este copiată întreagă. O parolă ajunsă într-un commit se schimbă din Neon: ștergerea din fișier nu o "
          "scoate din istoric."))


TABELE_BAZA = (
    '<div class="tb5">'
    '<div class="tb5__col"><h4>în <code>data/processed</code>, din C4</h4>'
    + "".join(f'<div class="tb5__i">{_ic_fis()}<code>{f}</code><small>{nr(n)} rânduri</small></div>' for f, n in [
        ("regiuni_nuts2.csv", T["regiuni"]), ("perechi_regiuni.csv", T["perechi_regiuni"]), ("perechi_tari.csv", T["perechi_tari"])])
    + '</div><div class="tb5__s"><code>to_sql</code><i></i></div>'
    '<div class="tb5__col tb5__col--b"><h4>în baza de pe Neon</h4>'
    + "".join(f'<div class="tb5__i"><code>{t}</code><small>un rând = {u}</small></div>' for t, u in [
        ("regiuni", "o regiune"), ("perechi_regiuni", "o pereche de regiuni"), ("perechi_tari", "o pereche de țări")])
    + "</div></div>")

TOSQL = {
    "id": "c5-cod-tosql",
    "indiciu": "Dacă tabelul există deja, este înlocuit: „replace”, între ghilimele. Citirea din bază se face cu read_sql.",
    "iesire": "     n\n0  298", "fisier": "curs/05_agregare_si_baze_de_date.ipynb",
    "sarcina": "Ce lipsește ca celula să poată fi rulată de mai multe ori, iar verificarea să citească din bază?",
    "cod": "regiuni = pd.read_csv(\"data/processed/regiuni_nuts2.csv\")\n"
           "regiuni.to_sql(\"regiuni\", engine, if_exists={{1}}, index=False)\n\n"
           "pd.{{2}}(\"select count(*) as n from regiuni\", engine)",
    "goluri": {
        "1": {"ok": ["\"replace\"", "'replace'"], "ajutor": "dacă tabelul există"},
        "2": {"ok": ["read_sql", "read_sql_query"], "ajutor": "funcția"}},
    "laBine": "298 de rânduri au plecat, 298 sunt în bază.",
    "laRau": "Primul gol este un text, între ghilimele.",
    "explicatie": "<code>\"replace\"</code> șterge tabelul și îl scrie din nou, deci celula se poate rula oricând. "
                  "Pentru tabelul mare, <code>method=\"multi\", chunksize=1000</code> trimite rândurile în pachete de "
                  "câte 1.000, nu unul câte unul."}

sl("s5", "Baza de date", "Tabelele, în bază",
   "<h2>Cele trei tabele din C4, în bază</h2>"
   + TABELE_BAZA
   + ix("cod", "Încărcarea", TOSQL),
   manual=
   "<h2>Cele trei tabele din C4, în bază</h2>"
   "<p><code>to_sql</code> trimite un tabel pandas în baza de date, <code>read_sql</code> aduce înapoi rezultatul "
   "unei interogări. Fișierele din <code>data/processed</code> rămân sursa; baza este copia comună, din care se "
   "citește de acum înainte.</p>"
   + TABELE_BAZA
   + ix("cod", "Încărcarea", TOSQL)
   + "<p>Baza își ține singură evidența tabelelor, într-un catalog care se interoghează ca orice tabel: "
     "<code>select table_name from information_schema.tables where table_schema = 'public'</code>. "
     "Pe neon.tech, la <b>Tables</b>, tabelele se văd și în browser.</p>")


# ===========================================================================
#  6-7. SQL
# ===========================================================================

Q = D["sql"]
_RO = [i for i, r in enumerate(Q["randuri"]) if r[1] == "RO"]
_ORD = sorted(_RO, key=lambda i: -Q["randuri"][i][2])
_TOATE = list(range(len(Q["randuri"])))
_C = [0, 2, 3]
SQLPAS = {
    "coloane": Q["coloane"], "randuri": Q["randuri"],
    "interogare": [
        {"c": "select", "t": "select tara_1, sci, migranti"},
        {"c": "from", "t": "from perechi_tari"},
        {"c": "where", "t": "where tara_2 = 'RO'"},
        {"c": "order", "t": "order by sci desc"},
        {"c": "limit", "t": "limit 5"}],
    "start": "Interogarea se scrie începând cu <code>select</code>, dar baza o execută în altă ordine. "
             "Pașii de sus urmează ordinea bazei.",
    "stari": [
        {"facut": [], "rand": _TOATE, "col": [0, 1, 2, 3, 4],
         "n": f"Tabelul <code>perechi_tari</code> are <b>{Q['total']}</b> de rânduri; aici se văd zece."},
        {"facut": ["from"], "acum": "from", "rand": _TOATE, "col": [0, 1, 2, 3, 4],
         "n": f"<b>{Q['total']}</b> de rânduri"},
        {"facut": ["from", "where"], "acum": "where", "rand": _RO, "col": [0, 1, 2, 3, 4],
         "n": f"<b>{Q['ro']}</b> rânduri; aici se văd {len(_RO)}"},
        {"facut": ["from", "where", "select"], "acum": "select", "rand": _RO, "col": _C,
         "n": f"<b>{Q['ro']}</b> rânduri, trei coloane"},
        {"facut": ["from", "where", "select", "order"], "acum": "order", "rand": _ORD, "col": _C,
         "n": f"<b>{Q['ro']}</b> rânduri, de la SCI-ul cel mai mare"},
        {"facut": ["from", "where", "select", "order", "limit"], "acum": "limit", "rand": _ORD[:5], "col": _C,
         "n": "<b>5</b> rânduri: rezultatul"},
    ],
    "pasi": [
        {"cmd": "from", "full": "from perechi_tari", "t": "Tabelul",
         "txt": f"Baza pornește de la tabel: toate cele {Q['total']} de perechi de țări."},
        {"cmd": "where", "full": "where tara_2 = 'RO'", "t": "Rândurile",
         "txt": "Rămân rândurile în care condiția este adevărată. Perechile sunt în ordine alfabetică, deci "
                "Austria cu România este <code>AT-RO</code>. Textul se scrie între apostrofuri: <code>'RO'</code>."},
        {"cmd": "select", "full": "select tara_1, sci, migranti", "t": "Coloanele",
         "txt": "Abia acum se aleg coloanele. <code>select</code> se scrie primul, dar se execută al treilea."},
        {"cmd": "order by", "full": "order by sci desc", "t": "Ordinea",
         "txt": "<code>desc</code>: de la mare la mic. Fără el, ordinea este crescătoare."},
        {"cmd": "limit", "full": "limit 5", "t": "Câte rânduri",
         "txt": "Primele cinci. Italia, țara cu cei mai mulți migranți români, este abia a cincea după SCI."},
    ],
}

SQL_TAB = tabel(["Cuvântul", "Ce face", "În pandas"], [
    ["~select", "ce coloane", "~tabel[[\"a\", \"b\"]]"],
    ["~from", "din ce tabel", ""],
    ["~where", "ce rânduri", "un filtru"],
    ["~order by ... desc", "în ce ordine", "~sort_values(..., ascending=False)"],
    ["~limit", "câte rânduri", "~head()"],
])

sl("s6", "SQL", "O interogare",
   "<h2>O interogare se citește ca o propoziție</h2>"
   + ix("sqlpas", "O interogare, pas cu pas", SQLPAS),
   manual=
   "<h2>O interogare se citește ca o propoziție</h2>"
   "<p>„Din tabelul perechilor de țări, rândurile cu România, coloanele țară, SCI și migranți, de la SCI-ul "
   "cel mai mare, primele cinci.” Fiecare bucată a propoziției este un cuvânt SQL.</p>"
   + ix("sqlpas", "O interogare, pas cu pas", SQLPAS)
   + SQL_TAB
   + "<p>În Python, interogarea este un text trimis cu <code>pd.read_sql(\"...\", engine)</code>; interogările "
     "lungi se scriu între trei ghilimele, pe mai multe rânduri. Valorile lipsă se numesc în SQL "
     "<code>null</code>; la <code>order by ... desc</code>, PostgreSQL le pune primele, iar <code>nulls last</code> "
     "le mută la final.</p>")


RO_PIB = "\n".join(f"{c:<7}{n:<18}{v:>8}" for c, n, v in D["ro_pib"])
EX_SQL = {
    "id": "c5-cod-sql",
    "indiciu": "Tabelul este cel al regiunilor. Codul țării este text, deci între apostrofuri. De la mare la mic: descending, pe scurt.",
    "iesire": f"regiune denumire          pib_locuitor\n{RO_PIB}", "fisier": "curs/05_agregare_si_baze_de_date.ipynb",
    "sarcina": "Regiunile României, cu denumirea și PIB-ul pe locuitor, de la cel mai mare PIB la cel mai mic.",
    "cod": "pd.read_sql(\"\"\"\n"
           "    select regiune, denumire, pib_locuitor\n"
           "    from {{1}}\n"
           "    where tara = {{2}}\n"
           "    order by pib_locuitor {{3}} nulls last\n"
           "\"\"\", engine)",
    "goluri": {
        "1": {"ok": ["regiuni"], "ajutor": "tabelul"},
        "2": {"ok": ["'RO'"], "ajutor": "țara, ca text"},
        "3": {"ok": ["desc", "DESC"], "ajutor": "ordinea"}},
    "laBine": "București-Ilfov are un PIB pe locuitor de două ori și jumătate mai mare decât a doua regiune.",
    "laRau": "În SQL, textul se scrie între apostrofuri: <code>'RO'</code>.",
    "explicatie": "Aceeași interogare în pandas: <code>regiuni[regiuni[\"tara\"] == \"RO\"].sort_values(\"pib_locuitor\", ascending=False)</code>."}

sl("s7", "SQL", "Interogarea, scrisă",
   "<h2>Regiunile României, după PIB</h2>"
   + ix("cod", "Prima interogare", EX_SQL),
   manual=
   "<h2>Regiunile României, după PIB</h2>"
   + ix("cod", "Prima interogare", EX_SQL)
   + SQL_TAB)


# ===========================================================================
#  8-10. Agregarea
# ===========================================================================

TIP = D["tip"]
_RAP = TIP["aceeasi tara"]["m"] / TIP["tari diferite"]["m"]
GRUPARE = {
    "grupuri": [{"t": "aceeași țară", "n": TIP["aceeasi tara"]["n"], "m": TIP["aceeasi tara"]["m"], "c": "accent"},
                {"t": "țări diferite", "n": TIP["tari diferite"]["n"], "m": TIP["tari diferite"]["m"], "c": "text-3"}],
    "puncte": 368,
    "raport": f"În aceeași țară, SCI-ul mediu este de {_RAP:.0f} de ori mai mare.",
    "start": f"Tabelul <code>perechi_regiuni</code>: {nr(T['perechi_regiuni'])} de rânduri, câte unul pe pereche.",
    "pasi": [
        {"cmd": "from perechi_regiuni", "t": "Rândurile",
         "txt": "Fiecare punct ține locul a 120 de perechi de regiuni. Cele două regiuni din aceeași țară sunt colorate."},
        {"cmd": "group by tip",
         "full": "group by case when tara_1 = tara_2 then 'aceeasi tara' else 'tari diferite' end",
         "t": "Grupurile",
         "txt": "<code>case when ... then ... else ... end</code> dă fiecărei perechi un tip, ca un „dacă”; "
                "<code>group by</code> le strânge după tip."},
        {"cmd": "count(*), avg(sci)", "full": "select tip, count(*) as perechi, avg(sci) as sci_mediu", "t": "Un rând pe grup",
         "txt": f"Fiecare grup devine un singur rând: câte perechi are și SCI-ul lor mediu. Din {nr(T['perechi_regiuni'])} "
                "de rânduri, două: asta este agregarea."},
    ],
}

V_GRUP = verif("c5-v-grup", 1,
               f"SCI-ul mediu este de {_RAP:.0f} de ori mai mare în aceeași țară. Ce altceva diferă între cele două "
               "grupuri, în afară de graniță?",
               ["Numărul de țări", "Distanța: în aceeași țară, perechile sunt mai apropiate",
                "Anul datelor", "Nimic, doar granița"],
               "Perechile din aceeași țară sunt, în medie, mai apropiate, deci rezultatul amestecă granița cu distanța. "
               "La cursul 6, cele două se despart: comparația se face la aceeași distanță.")

sl("s8", "Agregarea", "group by",
   "<h2>De la 44.253 de rânduri la două</h2>"
   + ix("grupare", "group by, pas cu pas", GRUPARE),
   manual=
   "<h2>De la 44.253 de rânduri la două</h2>"
   "<p><code>group by</code> împarte rândurile în grupuri și calculează câte un rezultat pe grup: "
   "<code>count(*)</code> (câte rânduri), <code>avg</code> (media), <code>sum</code> (totalul), <code>min</code>, "
   "<code>max</code>. Orice coloană din <code>select</code> care nu este calculată trebuie să apară în "
   "<code>group by</code>.</p>"
   + ix("grupare", "group by, pas cu pas", GRUPARE)
   + "<pre><code>select case when tara_1 = tara_2 then 'aceeasi tara' else 'tari diferite' end as tip,\n"
     "       count(*) as perechi,\n       avg(sci) as sci_mediu\nfrom perechi_regiuni\ngroup by tip</code></pre>",
   dupa=V_GRUP)


PT = D["pe_tara"]
PANDAS = (
    '<div class="pd5">'
    '<figure><figcaption>SQL, în bază</figcaption><pre>'
    'select tara,\n'
    '       <span class="k2">count</span>(*)       as regiuni,\n'
    '       <span class="k3">sum</span>(populatie) as locuitori\n'
    'from regiuni\n'
    '<span class="k1">group by tara</span>\n'
    'order by locuitori desc</pre></figure>'
    '<figure><figcaption>pandas, în caiet</figcaption><pre>'
    'regiuni.<span class="k1">groupby("tara")</span>.agg(\n'
    '    regiuni=("regiune", <span class="k2">"count"</span>),\n'
    '    locuitori=("populatie", <span class="k3">"sum"</span>),\n'
    ').sort_values("locuitori", ascending=False)</pre></figure>'
    "</div>")
REZ_TARA = tabel(["tara", "regiuni", "locuitori"],
                 [[t, str(n), nr(l)] for t, n, l in PT["top"]] + [["…", "", f"{PT['tari']} de țări în tot"]])
CAND = ('<div class="pd5__cand">'
        "<p><b>SQL:</b> baza face munca și trimite doar rezultatul. Contează când tabelul este mare sau stă pe un server.</p>"
        "<p><b>pandas:</b> mai comod pentru pașii de după, graficele și modelele. În practică: SQL ca să alegi și să "
        "rezumi, pandas ca să analizezi.</p></div>")

UNDE = {
    "id": "c5-prezice-unde", "poarta": False, "fisier": "unde.py",
    "cod": "# A\n"
           "d = pd.read_sql(\"select * from perechi_regiuni\", engine)\n"
           "m = d.groupby(\"tara_1\")[\"sci\"].mean()\n\n"
           "# B\n"
           "m = pd.read_sql(\"select tara_1, avg(sci) from perechi_regiuni \"\n"
           "                \"group by tara_1\", engine)",
    "intrebare": "Ambele variante dau aceeași medie pe țară. Câte rânduri se transferă prin rețea în fiecare caz?",
    "variante": ["A: 44.253 · B: 44.253", "A: 44.253 · B: câte unul pe țară",
                 "A: câte unul pe țară · B: câte unul pe țară", "A: un rând · B: un rând"],
    "corect": 1,
    "indiciu": "În A, ce aduce select *? În B, gruparea o face baza, înainte de transfer.",
    "laBine": "Baza reduce datele; în pandas ajunge doar rezultatul.",
    "explicatie": "A aduce tot tabelul în memorie și abia apoi grupează. În B, baza grupează și trimite câte un rând pe țară.",
    "iesire": "A: 44.253 de rânduri aduse\nB: 37 de rânduri aduse"}

sl("s9", "Agregarea", "Aceeași idee în pandas",
   "<h2>group by în SQL, groupby în pandas</h2>"
   + PANDAS + f'<div class="pd5__rez">{REZ_TARA}</div>',
   manual=
   "<h2>group by în SQL, groupby în pandas</h2>"
   "<p>Același rezumat, scris în ambele limbaje: câte regiuni NUTS2 are fiecare țară și câți locuitori au împreună. "
   "Culorile arată ce corespunde.</p>"
   + PANDAS + f'<div class="pd5__rez">{REZ_TARA}</div>' + CAND
   + "<p>Unele țări au o singură regiune NUTS2 (" + ", ".join(PT["o_regiune"]) + "): în comparațiile dintre regiuni, "
     "o astfel de regiune este de fapt o țară întreagă. <code>sum</code> ignoră valorile lipsă, dar o țară la care "
     "lipsesc toate valorile rămâne fără total.</p>"
   + ix("prezice", "Ce se transferă prin rețea", UNDE))


LT = D["lt"]
MEDII = {
    "axa": "PIB pe locuitor (PPS)",
    "regiuni": [{"t": "Vilnius și împrejurimile" if c == "LT01" else "restul Lituaniei", "pop": p, "v": v}
                for c, n, p, v in LT["regiuni"]],
    "simpla": LT["simpla"], "ponderata": LT["ponderata"],
    "txtSimpla": f"Media celor două valori, <b>{nr(LT['simpla'])}</b>, dă aceeași greutate ambelor regiuni, deși "
                 "restul țării are de peste două ori mai mulți locuitori.",
    "txtPonderata": f"Fiecare locuitor contează o dată: <b>{nr(LT['ponderata'])}</b>. Aceasta este media țării, "
                    "mai aproape de regiunea cu mai mulți oameni.",
}
V_MEDII = verif("c5-v-medii", 1,
                "Vârsta medie a unei țări, calculată din vârstele medii ale regiunilor ei: ce mai trebuie știut?",
                ["Câte regiuni are țara", "Câți locuitori are fiecare regiune",
                 "Care este capitala", "Nimic în plus"],
                "Fiecare regiune cântărește cât populația ei. Înainte de orice agregare: ce reprezintă un rând?")

sl("s10", "Agregarea", "Media pe țară",
   "<h2>Media regiunilor nu este media țării</h2>"
   + ix("medii", "Lituania, două regiuni", MEDII),
   manual=
   "<h2>Media regiunilor nu este media țării</h2>"
   "<p>Lituania are două regiuni NUTS2: Vilnius și împrejurimile, cu PIB-ul pe locuitor mare, și restul "
   "țării, cu mai mulți oameni. Lățimea fiecărui dreptunghi este populația, înălțimea este PIB-ul pe locuitor.</p>"
   + ix("medii", "Lituania, două regiuni", MEDII)
   + "<p>Media unei variabile pe țară nu este media țării, pentru că regiunile au populații diferite. Când se "
     "agregă, întrebarea de pus întâi este ce reprezintă un rând: aici, o regiune, nu un om.</p>",
   dupa=V_MEDII)


# ===========================================================================
#  11-13. Echipa
# ===========================================================================

ECHIPA = (
    '<ol class="ec5">'
    "<li><b>O bază pentru echipă</b>Un membru creează un proiect Neon pentru proiect, ca la pasul de la curs.</li>"
    "<li><b>Adresa, pe Teams</b>Adresa se dă colegilor pe Teams, nu pe GitHub: conține parola.</li>"
    "<li><b>În <code>dsw/.env</code></b>Fiecare pune adresa echipei în <code>.env</code>; "
    "<code>git status</code> nu trebuie să arate <code>.env</code>.</li>"
    "<li><b>Cine scrie, cine citește</b>Caietul de curățare și integrare încarcă tabelele cu <code>to_sql</code>; "
    "celelalte citesc cu <code>pd.read_sql</code>.</li>"
    "</ol>")

sl("s11", "Echipa", "Baza proiectului",
   "<h2>O singură bază pentru proiect</h2>"
   "<p class=\"cheie\">Toată echipa lucrează pe aceleași date: cele din baza ei.</p>"
   + ECHIPA,
   manual=
   "<h2>O singură bază pentru proiect</h2>"
   "<p>Baza de la curs este a fiecăruia. Pentru proiect, echipa folosește una singură, ca toți să lucreze pe "
   "aceleași date.</p>"
   + ECHIPA
   + nota("În depozit", "<code>.gitignore</code> din depozitul echipei conține <code>.env</code>. Verificarea: "
                        "<code>git status</code> nu trebuie să arate fișierul în listă."))


DOVADA = {
    "id": "c5-dovada-baza",
    "sarcina": "Trei interogări din caiet, rulate pe baza proprie. Ieșirea fiecăreia se lipește în câmpul ei.",
    "indiciu": "Celulele se rulează în caietul 05, după conectare (secțiunea 1) și după încărcarea tabelelor (secțiunea 2).",
    "pasi": [
        {"t": "Tabelele din bază",
         "cmd": "pd.read_sql(\"select table_name from information_schema.tables where table_schema = 'public'\", engine)",
         "gol": "lista afișată",
         "cauta": r"^(?=[\s\S]*perechi_regiuni)(?=[\s\S]*perechi_tari)(?=[\s\S]*\bregiuni\b)",
         "ind": "Trei rânduri, în orice ordine: <code>regiuni</code>, <code>perechi_regiuni</code>, <code>perechi_tari</code>.",
         "daca_nu": "Lipsește un tabel: celula cu to_sql din secțiunea 2 trebuie rulată din nou."},
        {"t": "Un rând pe țară",
         "cmd": "pd.read_sql(\"select tara, count(*) as regiuni from regiuni group by tara\", engine).shape",
         "gol": "(rânduri, coloane)",
         "cauta": r"\(\s*37\s*,\s*2\s*\)",
         "ind": "<code>.shape</code> dă forma tabelului: (rânduri, coloane). Un rând pe țară, două coloane.",
         "daca_nu": "Rezultatul trebuie să fie (37, 2): 37 de țări, două coloane."},
        {"t": "Aceeași țară, țări diferite",
         "cmd": "pd.read_sql(\"select case when tara_1 = tara_2 then 'aceeasi tara' else 'tari diferite' end as tip, "
                "count(*) as perechi from perechi_regiuni group by tip\", engine)",
         "gol": "tabelul afișat",
         "cauta": r"aceeasi tara\s+2385",
         "ind": "Două rânduri; cel cu <code>aceeasi tara</code> are 2385 de perechi.",
         "daca_nu": "Rândul aceeasi tara trebuie să aibă 2385 de perechi. Altfel, tabelul perechi_regiuni nu este cel din C4."},
    ],
    "explicatie": "Cele trei tabele sunt în bază, iar agregarea dă aceleași rezultate ca în caiet. La cursul 6, "
                  "caietul citește direct de aici, cu <code>pd.read_sql</code>.",
}

sl("s12", "Echipa", "Verificarea bazei",
   "<h2>Verificarea bazei</h2>"
   + ix("dovada", "Verificarea bazei", DOVADA),
   manual=
   "<h2>Verificarea bazei</h2>"
   "<p>Verificarea arată, cu ieșirea interogărilor rulate pe baza proprie, că tabelele sunt încărcate și că "
   "agregarea dă rezultatele din caiet. Butonul <b>Indiciu</b> arată ce trebuie să conțină fiecare rezultat.</p>"
   + ix("dovada", "Verificarea bazei", DOVADA))


sl("s13", "Echipa", "Interogarea echipei",
   "<h2>O întrebare despre coridor, cu group by</h2>"
   + ix("asteptari", "Interogarea echipei", {
       "id": "c5-interogare", "tip": "interogare", "minim": 60,
       "sarcina": "Interogarea echipei despre coridorul ei, cu <code>group by</code>, și ce arată rezultatul.",
       "exemplu": "De exemplu: perechile de regiuni dintre Italia și România (<code>tara_1 in ('IT', 'RO')</code>, "
                  "<code>tara_1 &lt;&gt; tara_2</code>), grupate după cele două țări: câte perechi și SCI-ul lor mediu.",
       "multumesc": "Interogarea a fost înregistrată. Feedbackul vine înainte de cursul următor."}))


sl("s14", "Mai departe", "Pentru cursul următor",
   "<h2>La cursul 6: analiza exploratorie</h2>"
   '<div class="fin3"><div class="fin3__g">'
   "<section><h4>Ce urmează la cursul 6</h4><ul>"
   "<li>Patru ipoteze din literatură: distanța, granița, economia, migrația.</li>"
   "<li>Cum arată o pereche obișnuită: distribuția SCI și scara logaritmică.</li>"
   "<li>Aceleași perechi, privite ca rețea.</li></ul></section>"
   "<section><h4>Pregătirea pentru cursul 6</h4><ul>"
   "<li>Baza echipei pe Neon, cu cele trei tabele.</li>"
   "<li>Adresa în <code>dsw/.env</code> la fiecare membru, nu pe GitHub.</li>"
   "<li>Interogarea echipei despre coridor, cu <code>group by</code>.</li></ul></section>"
   "</div>"
   '<p class="fin3__a"><a class="leg" href="../">Pagina cursului 5</a></p></div>',
   manual=
   "<h2>Cursul 6: analiza exploratorie</h2>"
   "<p>Cu tabelele în bază, lecția următoare le examinează: ce tipare apar și ce explicații merită verificate, "
   "pornind de la ipoteze din literatură.</p>"
   + surse("Documentația", [
       ("Neon: conectarea din Python", "https://neon.tech/docs/guides/python", "adresa, SQLAlchemy, psycopg"),
       ("pandas: read_sql și to_sql", "https://pandas.pydata.org/docs/reference/api/pandas.read_sql.html", "citirea și scrierea tabelelor"),
       ("PostgreSQL: select", "https://www.postgresql.org/docs/current/sql-select.html", "<code>where</code>, <code>group by</code>, <code>order by</code>"),
       ("pandas: groupby", "https://pandas.pydata.org/docs/user_guide/groupby.html", "gruparea și <code>agg</code>"),
   ]))


if __name__ == "__main__":
    L.scrie_tot()
