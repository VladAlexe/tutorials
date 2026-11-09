# -*- coding: utf-8 -*-
"""
Lecția 5: Integrare, baze de date și agregare.

Urmează caietul 05_agregare_si_baze_de_date (9 noiembrie 2026): baza de date
SQLite a cursului (un fișier, data/dsw.db), legată de pandas prin SQLAlchemy;
cele patru tabele din C3 și C4 încărcate cu to_sql; primele interogări;
integrarea (join în SQL, merge în pandas); agregarea (group by, groupby);
perechile de țări; baza echipei (data/processed/proiect.db).

Partea despre bazele de date urmează prezentarea cursului 5 din 2025: unirea
tabelelor, Neon, PostgreSQL și MySQL. Neon apare ca variantă din cloud, nu
se folosește la seminar.

Numerele vin din date/c5-baza.json (tabelele produse de caietele 04 și 05)
și din rularea caietului 05 pe SQLite (9 noiembrie 2026).

Rulare:  python _build/c5.py
"""

import json

from comun import Lectie, ix, verif, tabel, nota, surse, RAD

L = Lectie(5, "c5-agregare-si-baze-de-date", "Agregare și baze de date",
           "Baza de date SQLite a cursului, legată de pandas prin SQLAlchemy; unde mai poate sta o bază "
           "(server, cloud, Neon); unirea tabelelor și agregarea, în SQL și în pandas.")
sl = L.sl

D = json.loads((RAD / "date" / "c5-baza.json").read_text(encoding="utf-8"))
T = D["tabele"]
nr = lambda v: f"{v:,}".replace(",", ".")
_NB5 = "05_agregare_si_baze_de_date.ipynb"
ET_VERIF = '<p class="ex-et">Verificare</p>'


# ===========================================================================
#  0. Unde suntem în curs
# ===========================================================================

CURSUL = tabel(["", "Conținutul", "Rezultatul"], [
    ["C1", "proiectul, mediul de lucru, tipurile de date și JSON", "<code>dsw/</code>, cu <code>.venv</code>"],
    ["C2", "colectarea datelor prin API: Eurostat, Banca Mondială", "<code>data/raw</code>"],
    ["C3", "surse diverse, preprocesare, Git și depozitul echipei", "<code>data/processed</code>, <code>proiect/</code>"],
    ["C4", "curățarea datelor și tabelul regiunilor", "<code>regiuni_nuts2.csv</code>"],
    ["<b>C5</b>", "<b>azi: integrare, baze de date și agregare, în SQL și în Python</b>", "<b>perechile, în <code>dsw.db</code></b>"],
    ["C6", "analiza exploratorie: ipoteze, grafice, rețele", "primele rezultate"],
    ["C7", "variabile derivate și model", "modelul SCI"],
    ["C8", "raportul și prezentarea proiectului", "raportul echipei"],
])

AGENDA = [
    ("Baza de date", "azi", "Un singur loc pentru date: fișier, server sau cloud. Baza cursului, SQLite."),
    ("SQL", "azi", "O interogare se citește ca o propoziție: select, from, where, order by."),
    ("Integrarea", "azi", "Tipurile de join; join în SQL, merge în pandas; numărarea rândurilor."),
    ("Agregarea", "azi", "group by și groupby, capcana mediilor, perechile de țări."),
]
PLAN = ix("agenda", "Planul lecției", {"static": True, "titlu": "Planul lecției",
          "etape": [{"nume": n, "unde": u, "text": d} for n, u, d in AGENDA]})

sl("s0", "Cursul", "Unde suntem",
   "<h2>Unde suntem în curs</h2>"
   "<p class=\"cheie\">Tabelele curate din C3 și C4 ajung într-o bază de date, se unesc în perechi și se rezumă. "
   "Azi: pasul 5.</p>"
   + CURSUL,
   manual=
   "<h2>Unde suntem în curs</h2>"
   "<p>Datele colectate în C2 au fost aduse la aceeași formă în C3 și verificate în C4. Lecția le mută într-o bază "
   "de date, le unește în perechi de regiuni și de țări și le rezumă: de la multe rânduri la puține. Aceeași "
   "succesiune o urmează și proiectul fiecărei echipe.</p>"
   + CURSUL + PLAN
   + nota("Caietul lecției", f"<code>{_NB5}</code>, în <code>dsw/curs/</code>, lângă caietele 01-04.", True))


# ===========================================================================
#  1-3. Baza de date
# ===========================================================================

def _ic_fis():
    return ('<svg class="ic" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.3" '
            'stroke-linejoin="round"><path d="M4 1.5h5.2L12.5 4.8V14.5h-8.5z"/><path d="M9 1.7V5h3.3"/></svg>')

def _ic_pc():
    return ('<svg class="ic" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.3">'
            '<rect x="2.5" y="3" width="11" height="7.5" rx="1"/><path d="M1 13h14"/></svg>')

def _ic_om():
    return ('<svg class="ic" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.3">'
            '<circle cx="8" cy="5.5" r="2.6"/><path d="M3 14c.6-2.8 2.6-4.3 5-4.3s4.4 1.5 5 4.3"/></svg>')

_FIS = [("perechi_tari.csv", ""), ("perechi_tari_v2.csv", ""), ("perechi_tari_final.csv", ""),
        ("perechi_tari (1).csv", "rau"), ("perechi_tari_FINAL2.csv", "rau")]
COPII = (
    '<div class="cc5">'
    '<div class="cc5__p">'
    '<h4>Cinci fișiere</h4>'
    '<div class="cc5__fis">'
    + "".join(f'<span class="cc5__f {c}" style="--r:{(i - 2) * 2.5}deg">{_ic_fis()}<code>{n}</code></span>'
              for i, (n, c) in enumerate(_FIS))
    + '</div><p class="cc5__jos cc5__jos--rau">Care este versiunea bună?</p></div>'
    '<div class="cc5__sag" aria-hidden="true"></div>'
    '<div class="cc5__p cc5__p--b">'
    '<h4>O bază de date</h4>'
    '<div class="cc5__baza">'
    '<div class="cc5__oameni">' + "".join(f'<span>{_ic_om()}</span>' for _ in range(5)) + '</div>'
    '<div class="cc5__cil"><b>dsw.db</b></div>'
    '</div><p class="cc5__jos">Toți citesc același tabel.</p></div>'
    "</div>")

sl("s1", "Baza de date", "De ce o bază",
   "<h2>Cinci copii sau un singur loc</h2>"
   + COPII,
   manual=
   "<h2>Cinci copii sau un singur loc</h2>"
   "<p>Întrebarea „de la câte rânduri este nevoie de o bază de date” este formulată greșit: dimensiunea "
   "este rareori motivul. Pandas lucrează fără dificultate cu milioane de rânduri, iar datele proiectului "
   "sunt mult sub acest volum. Motivul real este ordinea: cinci copii ale aceluiași tabel ajung, în câteva "
   "săptămâni, cinci tabele diferite. O bază are o singură versiune, din care citește oricine lucrează pe date.</p>"
   + COPII)


def _carte(cls, et, titlu, sub, adr, puncte):
    li = "".join(f"<li>{p}</li>" for p in puncte)
    return (f'<div class="loc5__c {cls}"><span class="loc5__et">{et}</span><h4>{titlu}</h4>'
            f'<p class="loc5__sub">{sub}</p><code class="loc5__adr">{adr}</code><ul>{li}</ul></div>')

LOCURI = (
    '<div class="loc5">'
    + _carte("loc5__c--azi", "la seminar", "Într-un fișier", "SQLite",
             "sqlite:///data/dsw.db",
             ["fără server, cont sau parolă", "un singur fișier, ușor de mutat", "un singur scriitor odată"])
    + _carte("", "în instituții", "Pe un server", "PostgreSQL, MySQL",
             "postgresql://utilizator:parola@server/baza",
             ["mulți utilizatori deodată", "acces cu utilizator și parolă", "cineva întreține serverul"])
    + _carte("", "găzduit", "În cloud", "Neon, Supabase, Azure SQL",
             "postgresql://...@ep-....neon.tech/neondb",
             ["același PostgreSQL, întreținut de firmă", "pornește la cerere, se oprește singur",
              "plan gratuit pentru proiecte mici"])
    + "</div>"
    '<p class="loc5__motto">„SQLite nu concurează cu serverele de baze de date. SQLite concurează cu '
    "<code>fopen()</code>.”<small>sqlite.org, „Appropriate Uses For SQLite”</small></p>")

FOLOSITE = [("PostgreSQL", 55.6), ("MySQL", 40.5), ("SQLite", 37.5), ("SQL Server", 30.1),
            ("Redis", 28.0), ("MongoDB", 24.0)]
SONDAJ = ('<div class="sv5"><div class="sv5__t">Bazele de date folosite în ultimul an, Stack Overflow 2025 '
          '(26.083 de respondenți)</div>'
          + "".join(f'<div class="sv5__r"><span>{n}</span><i style="--w:{v/60*100:.1f}%"></i>'
                    f'<b>{str(v).replace(".", ",")}%</b></div>' for n, v in FOLOSITE)
          + "</div>")

PG_MYSQL = tabel(["", "PostgreSQL", "MySQL"], [
    ["Tipuri de date", "JSONB, GIS (PostGIS), tablouri, tipuri proprii", "tipuri clasice, JSON simplu"],
    ["Performanță", "scrieri concurente și interogări analitice", "citiri rapide, aplicații web"],
    ["Folosire", "analiză, date eterogene, date geografice", "site-uri mari, comerț online"],
])

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


sl("s2", "Baza de date", "Unde stă o bază",
   "<h2>Unde stă o bază de date</h2>"
   + LOCURI,
   manual=
   "<h2>Unde stă o bază de date</h2>"
   "<p>O bază de date relațională ține datele în tabele, interogate cu SQL. Aceleași tabele și aceleași "
   "interogări pot sta în trei locuri, care diferă prin cine are acces și cine întreține baza.</p>"
   + LOCURI
   + "<p><b>SQLite</b> este o bază într-un singur fișier, inclusă în Python. Nu are server: programul citește și "
     "scrie direct fișierul. Este potrivită pentru analiză, pentru învățare și ca format de fișier pentru date; "
     "nu este potrivită când mulți utilizatori scriu în același timp, prin rețea.</p>"
     "<p><b>PostgreSQL</b> și <b>MySQL</b> sunt baze cu server: un program care rulează permanent și la care se "
     "conectează mai mulți utilizatori, fiecare cu contul și drepturile lui. Sunt cele mai folosite baze de date, "
     "alături de SQLite.</p>"
   + SONDAJ
   + "<p>Diferențele dintre cele două, pe scurt:</p>"
   + PG_MYSQL
   + "<p><b>Neon</b> oferă PostgreSQL găzduit în cloud: contul se face cu GitHub, iar baza primește o adresă de "
     "conectare. Componenta care execută interogările pornește la prima cerere și se oprește după câteva minute "
     "fără activitate; datele rămân. Supabase și Azure SQL oferă servicii asemănătoare.</p>"
   + ix("flux", "Drumul unei interogări în cloud", FLUX))


ADRESE = (
    '<div class="adr5">'
    + "".join(f'<span style="--pc:var(--{col})"><b>{t}</b><small>{e}</small></span>' for t, e, col in [
        ("sqlite://", "felul bazei", "accent"), ("/data/dsw.db", "fișierul, față de caiet", "ambra")])
    + '</div><div class="adr5">'
    + "".join(f'<span class="{c}" style="--pc:var(--{col})"><b>{t}</b><small>{e}</small></span>' for t, e, c, col in [
        ("postgresql://", "felul bazei", "", "accent"), ("utilizator", "utilizatorul", "", "ardezie"),
        (":parola", "parola: secretul", "secret", "nu"), ("@ep-....neon.tech", "serverul", "", "ambra"),
        ("/neondb", "baza", "", "roza")])
    + "</div>")

def cod_explicat(linii, note):
    """Cod scurt cu numere pe rânduri și explicațiile alături; nu este exercițiu."""
    cod = "\n".join(linii)
    li = "".join(f'<li><span class="ce5__n">{i}</span><span>{t}</span></li>' for i, t in enumerate(note, 1))
    return f'<div class="ce5"><pre class="ce5__cod"><code>{cod}</code></pre><ol class="ce5__note">{li}</ol></div>'

def _n(i):
    return f'<span class="ce5__n">{i}</span>'

COD_CONECTARE = cod_explicat(
    ['import pandas as pd',
     f'from sqlalchemy import create_engine              {_n(1)}',
     '',
     f'engine = create_engine("sqlite:///data/dsw.db")   {_n(2)}',
     f'pd.read_sql("select 1 as conexiunea", engine)     {_n(3)}'],
    ["SQLAlchemy face legătura dintre pandas și orice bază de date.",
     "Adresa bazei: aici, un fișier din <code>curs/data/</code>, creat la prima scriere.",
     "O interogare de probă: dacă răspunsul este 1, legătura funcționează."])

sl("s3", "Baza de date", "O adresă, orice bază",
   "<h2>O adresă, orice bază</h2>"
   "<p class=\"cheie\">SQLAlchemy leagă pandas de bază printr-o adresă. Se schimbă adresa, codul rămâne același.</p>"
   + ADRESE
   + COD_CONECTARE,
   manual=
   "<h2>O adresă, orice bază</h2>"
   "<p><code>create_engine</code>, din SQLAlchemy, primește adresa bazei și întoarce o conexiune, numită de obicei "
   "<code>engine</code>. Pandas o folosește în ambele sensuri: <code>to_sql</code> scrie un tabel în bază, "
   "<code>read_sql</code> aduce rezultatul unei interogări ca tabel pandas.</p>"
   "<p>Pentru SQLite, adresa este calea fișierului, față de dosarul caietului: <code>sqlite:///data/dsw.db</code> "
   "înseamnă fișierul <code>dsw.db</code> din <code>curs/data/</code>. Pentru o bază pe un server, adresa conține "
   "utilizatorul, parola și serverul:</p>"
   + ADRESE
   + COD_CONECTARE
   + "<p>O adresă cu parolă nu se scrie niciodată în caiet: se pune într-un fișier <code>.env</code>, exclus din Git "
     "prin <code>.gitignore</code>, și se citește cu <code>python-dotenv</code>. Baza SQLite a cursului nu are parolă, "
     "deci acest pas nu este necesar.</p>")


def _ic_tab():
    return ('<svg class="ic" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.3">'
            '<rect x="2" y="3" width="12" height="10" rx="1"/><path d="M2 6.5h12M6.5 6.5V13"/></svg>')

TABELE_BAZA = (
    '<div class="tb5">'
    '<div class="tb5__col"><h4>în <code>data/processed</code>, din C3 și C4</h4>'
    + "".join(f'<div class="tb5__i">{_ic_fis()}<code>{f}</code><small>{nr(n)} rânduri</small></div>' for f, n in [
        ("regiuni_nuts2.csv", 298), ("sci_regiuni.csv", 88804), ("migratie_curata.csv", 9900), ("zboruri_curate.csv", 1505)])
    + '</div><div class="tb5__s"><code>to_sql</code><i></i></div>'
    '<div class="tb5__col tb5__col--b"><h4>în <code>data/dsw.db</code>: entitatea și cheia</h4>'
    + "".join(f'<div class="tb5__i">{_ic_tab()}<code>{t}</code><small>{u}</small></div>' for t, u in [
        ("regiuni", "o regiune · <code>regiune</code>"), ("sci", "o pereche de regiuni · <code>regiune_1, regiune_2</code>"),
        ("migratie", "o cetățenie într-o țară · <code>tara_rezidenta, cetatenie</code>"),
        ("zboruri", "o pereche de țări · <code>tara_1, tara_2</code>")])
    + "</div></div>")

COD_TOSQL = cod_explicat(
    ['regiuni = pd.read_csv(DATE + "regiuni_nuts2.csv")',
     f'regiuni.to_sql("regiuni", engine, if_exists="replace", index=False)   {_n(1)}',
     f'pd.read_sql("select count(*) as n from regiuni", engine)            {_n(2)}'],
    ["Scrie tabelul în bază, cu numele <code>regiuni</code>; <code>\"replace\"</code> îl înlocuiește dacă există, "
     "deci celula se poate rula din nou.",
     "Verificarea: 298 de rânduri au plecat, 298 sunt în bază."])

sl("s4", "Baza de date", "Tabelele, în bază",
   "<h2>Patru tabele, patru entități</h2>"
   + TABELE_BAZA
   + COD_TOSQL,
   manual=
   "<h2>Patru tabele, patru entități</h2>"
   "<p>O bază relațională ține fiecare lucru despre care există date, o <b>entitate</b>, într-un tabel separat. "
   "Fiecare tabel are o <b>cheie</b>: coloanele care identifică un rând, ca în C4. Tabelele se leagă prin coloane "
   "comune: <code>regiune_1</code> din <code>sci</code> arată spre <code>regiune</code> din <code>regiuni</code>.</p>"
   + TABELE_BAZA
   + "<p>Tabelele se citesc din depozitul cursului, ca toți să aibă aceleași date, și se încarcă cu <code>to_sql</code>. "
     "Fișierele din <code>data/processed</code> rămân sursa; baza este locul din care se citește de acum înainte. "
     "<code>index=False</code> nu scrie indexul pandas ca o coloană în plus.</p>"
   + COD_TOSQL
   + "<p>Baza își ține singură evidența tabelelor, într-un catalog care se interoghează ca orice tabel. În SQLite: "
     "<code>select name from sqlite_master where type = 'table'</code>; în PostgreSQL, catalogul se numește "
     "<code>information_schema.tables</code>.</p>")



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


sl("s5", "SQL", "O interogare",
   "<h2>O interogare se citește ca o propoziție</h2>"
   + ix("sqlpas", "O interogare, pas cu pas", SQLPAS),
   manual=
   "<h2>O interogare se citește ca o propoziție</h2>"
   "<p>„Din tabelul perechilor de țări, rândurile cu România, coloanele țară, SCI și migranți, de la SCI-ul "
   "cel mai mare, primele cinci.” Fiecare bucată a propoziției este un cuvânt SQL. Tabelul perechilor de țări "
   "se construiește la sfârșitul lecției; aici el servește doar ca exemplu.</p>"
   + ix("sqlpas", "O interogare, pas cu pas", SQLPAS)
   + SQL_TAB
   + "<p>În Python, interogarea este un text trimis cu <code>pd.read_sql(\"...\", engine)</code>; interogările "
     "lungi se scriu între trei ghilimele, pe mai multe rânduri. Valorile lipsă se numesc în SQL "
     "<code>null</code>; <code>nulls last</code> le pune la final, oricare ar fi baza de date.</p>")


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


REGIUNI_MOSTRA = (
    '<div class="ms5"><div class="ms5__n">tabelul <code>regiuni</code>, primele rânduri din 298</div>'
    + tabel(["regiune", "tara", "denumire", "pib_locuitor", "populatie", "…"], [
        ["~RO22", "~RO", "Sud-Est", "23.600", "2.345.172", "…"],
        ["~RO42", "~RO", "Vest", "31.300", "1.672.978", "…"],
        ["~HU11", "~HU", "Budapest", "67.200", "1.686.222", "…"],
    ])
    + "</div>")

sl("s6", "SQL", "Interogarea, scrisă",
   "<h2>Regiunile României, după PIB</h2>"
   + REGIUNI_MOSTRA
   + ix("cod", "Prima interogare", EX_SQL),
   manual=
   "<h2>Regiunile României, după PIB</h2>"
   + REGIUNI_MOSTRA
   + ix("cod", "Prima interogare", EX_SQL)
   + SQL_TAB)



# Exemplul de unire: date reale, alese mici. Stânga: perechile regiunii Nord-Vest (RO11) cu trei regiuni;
# dreapta: trei regiuni ale României, cu PIB-ul pe locuitor. HU11 nu este în dreapta, RO42 nu este în stânga.
_ST = [("RO12", "308.881"), ("RO32", "154.045"), ("HU11", "34.160")]
_DR = [("RO12", "28.400"), ("RO32", "75.000"), ("RO42", "31.300")]
_MOD = [
    ("inner", "inner join", "Doar regiunile găsite în ambele tabele.", ["RO12", "RO32"]),
    ("left", "left join", "Toate rândurile din stânga; unde dreapta nu are pereche, rămâne o valoare lipsă.",
     ["RO12", "RO32", "HU11"]),
    ("outer", "outer join", "Toate rândurile din ambele tabele, cu valori lipsă de ambele părți.",
     ["RO12", "RO32", "HU11", "RO42"]),
]


def _jx_tab(titlu, sub, cap, randuri):
    th = "".join(f"<th>{c}</th>" for c in cap)
    tr = "".join(f'<tr class="{cls}">' + "".join(f"<td>{v}</td>" for v in r) + "</tr>" for cls, r in randuri)
    return (f'<div class="jx5__t"><div class="jx5__n">{titlu}<small>{sub}</small></div>'
            f"<table><tr>{th}</tr>{tr}</table></div>")


def _cls(k):
    return {"RO12": "jx5--da", "RO32": "jx5--da", "HU11": "jx5--st", "RO42": "jx5--dr"}[k]


def join_vizual(suf):
    st = dict(_ST)
    dr = dict(_DR)
    sus = ('<div class="jx5__sus">'
           + _jx_tab("stânga: <code>perechi</code>", "perechile regiunii Nord-Vest", ["regiune_2", "sci"],
                     [(_cls(k), [k, v]) for k, v in _ST])
           + '<div class="jx5__on"><code>on regiune_2 = regiune</code></div>'
           + _jx_tab("dreapta: <code>regiuni</code>", "regiuni din România", ["regiune", "pib"],
                     [(_cls(k), [k, v]) for k, v in _DR])
           + "</div>")
    radio = "".join(f'<input type="radio" name="jx5-{suf}" id="jx5-{suf}-{m}" class="jx5__r jx5__r--{m}"'
                    f'{" checked" if m == "inner" else ""}>' for m, *_ in _MOD)
    tab = '<div class="jx5__tab">' + "".join(
        f'<label for="jx5-{suf}-{m}" class="jx5__b jx5__b--{m}">{et}<small>{len(k)} rânduri</small></label>'
        for m, et, _, k in _MOD) + "</div>"
    rez = ""
    for m, et, txt, chei in _MOD:
        rows = [(_cls(k), [k, st.get(k, "null"), dr.get(k, "null")]) for k in chei]
        rez += (f'<div class="jx5__rez jx5__rez--{m}">'
                + _jx_tab(f"<code>{et}</code>", f"{len(chei)} rânduri", ["regiune", "sci", "pib"], rows)
                + f'<p class="jx5__txt">{txt}</p></div>')
    return f'<div class="jx5">{radio}{sus}{tab}<div class="jx5__jos">{rez}</div></div>'


UNIRI = tabel(["Unirea", "Ce face", "pandas", "SQL"], [
    ["una sub alta", "tabele cu aceleași coloane, rândurile se adună (C3)", "~pd.concat([a, b])", "~union all"],
    ["după o cheie", "tabele diferite, cu o coloană comună; se adaugă coloane (C4)", "~a.merge(b, on=\"regiune\")", "~join ... on ..."],
    ["inner", "doar rândurile găsite în ambele tabele", "~how=\"inner\"", "~inner join"],
    ["left", "toate rândurile din stânga; lipsă unde nu se găsește", "~how=\"left\"", "~left join"],
    ["outer", "toate rândurile din ambele tabele", "~how=\"outer\"", "~full outer join"],
])

V_JOIN = verif("c5-v-join", 1,
               "Tabelul <code>sci</code> are 44.253 de perechi, iar fiecare regiune apare o singură dată în "
               "<code>regiuni</code>. Câte rânduri dă <code>sci left join regiuni</code>?",
               ["Mai puțin de 44.253, dacă unele regiuni lipsesc", "Exact 44.253",
                "Mai mult de 44.253", "298, câte regiuni sunt"],
               "<code>left join</code> păstrează toate rândurile din stânga, iar cheia din dreapta este unică, deci "
               "fiecare pereche găsește cel mult un rând. Dacă cheia din dreapta s-ar repeta, rândurile s-ar înmulți.")

sl("s7", "Integrarea", "Tipurile de join",
   "<h2>Cum se unesc două tabele</h2>"
   + join_vizual("s"),
   manual=
   "<h2>Cum se unesc două tabele</h2>"
   "<p>Două tabele se unesc în două feluri. <code>concat</code> le pune unul sub altul, când au aceleași coloane: "
   "s-a folosit în C3. <code>merge</code> le alătură după o cheie comună, adăugând coloane: s-a folosit în C4. "
   "La unirea după cheie, tipul unirii hotărăște ce se întâmplă cu rândurile care nu își găsesc perechea.</p>"
   "<p>În exemplu, cu date reale, stânga are trei perechi ale regiunii Nord-Vest, iar dreapta trei regiuni ale "
   "României. <code>HU11</code> (Budapesta) nu este în dreapta, iar <code>RO42</code> (Vest) nu este în stânga. "
   "Butoanele schimbă tipul unirii.</p>"
   + join_vizual("m") + UNIRI,
   dupa=V_JOIN)



JM = (
    '<div class="pd5">'
    '<figure><figcaption>SQL, în bază</figcaption><pre>'
    'select p.*, r1.pib_locuitor as pib_1\n'
    'from sci p\n'
    '<span class="k1">left join</span> regiuni r1\n'
    '  <span class="k2">on</span> p.regiune_1 = r1.regiune</pre></figure>'
    '<figure><figcaption>pandas, în caiet</figcaption><pre>'
    'perechi.<span class="k1">merge</span>(\n'
    '    atribute.add_suffix("_1"),\n'
    '    <span class="k2">on</span>="regiune_1", <span class="k1">how="left"</span>)</pre></figure>'
    "</div>")

NUMARARE = ('<div class="nr5"><span><small>perechi, înainte</small><b>44.253</b></span>'
            '<i aria-hidden="true">→</i><span><small>rânduri, după unire</small><b>44.253</b></span>'
            '<p>Niciun rând pierdut, niciunul înmulțit.</p></div>')

sl("s8", "Integrarea", "join și merge",
   "<h2>join în SQL, merge în pandas</h2>"
   "<p class=\"cheie\">Aceeași unire, în două limbaje. Regula din C4 rămâne: după fiecare unire, numărăm rândurile.</p>"
   + JM + NUMARARE,
   manual=
   "<h2>join în SQL, merge în pandas</h2>"
   "<p><code>left join regiuni r1 on p.regiune_1 = r1.regiune</code> caută, pentru fiecare pereche, rândul din "
   "<code>regiuni</code> cu același cod. Este exact ce face <code>merge</code> în pandas, cu <code>how=\"left\"</code>. "
   "Culorile arată ce corespunde. Tabelul <code>regiuni</code> se unește de două ori, câte o dată pentru fiecare capăt "
   "al perechii, cu două nume scurte: <code>r1</code> și <code>r2</code>.</p>"
   + JM + NUMARARE
   + "<p>În caiet, aceeași unire se face și în pandas, cu toți cei șapte indicatori, iar tabelul rezultat, "
     "<code>perechi_regiuni</code>, se scrie în bază. SQL lasă baza să facă munca și aduce doar ce se cere, ceea ce "
     "contează când tabelele sunt mari sau stau pe un server; pandas este mai comod când urmează alți pași în Python. "
     "În proiect, tabelele finale se fac o singură dată, într-un singur caiet; celelalte caiete doar le citesc.</p>")



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
    "intrebare": "Ambele variante dau aceeași medie pe țară. Câte rânduri ajung din bază în pandas în fiecare caz?",
    "variante": ["A: 44.253 · B: 44.253", "A: 44.253 · B: câte unul pe țară",
                 "A: câte unul pe țară · B: câte unul pe țară", "A: un rând · B: un rând"],
    "corect": 1,
    "indiciu": "În A, ce aduce select *? În B, gruparea o face baza, înainte de transfer.",
    "laBine": "Baza reduce datele; în pandas ajunge doar rezultatul.",
    "explicatie": "A aduce tot tabelul în memorie și abia apoi grupează. În B, baza grupează și trimite câte un rând pe țară.",
    "iesire": "A: 44.253 de rânduri aduse\nB: 37 de rânduri aduse"}


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
# Exemplul pentru group by: șase regiuni reale, din România și Ungaria, cu populația.
_GR = [("RO11", "RO", 2539784), ("HU11", "HU", 1686222), ("RO12", "RO", 2288061),
       ("HU12", "HU", 1333257), ("RO21", "RO", 3226814), ("HU21", "HU", 1057303)]


def _gb_tab(cap, randuri, cls=""):
    th = "".join(f"<th>{c}</th>" for c in cap)
    tr = "".join(f'<tr class="gb5--{t.lower()}">' + "".join(f"<td>{v}</td>" for v in r) + "</tr>" for t, r in randuri)
    return f'<table class="gb5__tb {cls}"><tr>{th}</tr>{tr}</table>'


def _grupuri():
    out = ""
    for t in ("RO", "HU"):
        rs = [(t, [r, nr(p)]) for r, tt, p in _GR if tt == t]
        out += f'<div class="gb5__g gb5__g--{t.lower()}"><span class="gb5__gt">{t}</span>' + _gb_tab(["regiune", "populatie"], rs) + "</div>"
    return out


_SUM = {t: (sum(1 for _, tt, _ in _GR if tt == t), sum(p for _, tt, p in _GR if tt == t)) for t in ("RO", "HU")}
GRUP_VIZ = (
    '<div class="gb5">'
    '<div class="gb5__c"><h4><span>1</span>tabelul</h4>'
    + _gb_tab(["regiune", "tara", "populatie"], [(t, [r, t, nr(p)]) for r, t, p in _GR])
    + '</div><div class="gb5__s" aria-hidden="true"></div>'
    '<div class="gb5__c"><h4><span>2</span>împarte după <code>tara</code></h4>' + _grupuri()
    + '</div><div class="gb5__s" aria-hidden="true"></div>'
    '<div class="gb5__c"><h4><span>3</span>un rând pe grup</h4>'
    + _gb_tab(["tara", "regiuni", "locuitori"], [(t, [t, str(_SUM[t][0]), nr(_SUM[t][1])]) for t in ("RO", "HU")],
              "gb5__tb--rez")
    + '<p class="gb5__f"><code>count(*)</code> numără rândurile grupului, <code>sum(populatie)</code> le adună.</p></div>'
    "</div>")
GRUP_COD = (
    '<div class="gb5__cod">'
    '<figure><figcaption>SQL</figcaption><pre>select tara, count(*) as regiuni, sum(populatie) as locuitori\n'
    'from regiuni\n<span class="k1">group by tara</span></pre></figure>'
    '<figure><figcaption>pandas</figcaption><pre>regiuni.<span class="k1">groupby("tara")</span>.agg(\n'
    '    regiuni=("regiune", "count"), locuitori=("populatie", "sum"))</pre></figure>'
    "</div>")

V_GRUP = verif("c5-v-grup", 1,
               "Tabelul <code>regiuni</code> are 298 de rânduri, din 37 de țări. Câte rânduri are rezultatul cu "
               "<code>group by tara</code>?",
               ["298", "37", "1", "Depinde de populație"],
               "Un rând pe grup: câte țări, atâtea rânduri. <code>count(*)</code> spune apoi câte regiuni are fiecare țară.")

sl("s9", "Agregarea", "group by",
   "<h2>group by: împarte, calculează, adună</h2>"
   "<p class=\"cheie\"><code>select tara, count(*), sum(populatie) from regiuni group by tara</code></p>"
   + GRUP_VIZ,
   manual=
   "<h2>group by: împarte, calculează, adună</h2>"
   "<p><code>group by</code> face trei pași: împarte rândurile în grupuri după o coloană, calculează câte un rezultat "
   "pe fiecare grup și pune rezultatele într-un tabel nou, cu un rând pe grup. Funcțiile de calcul sunt "
   "<code>count(*)</code> (câte rânduri), <code>sum</code> (totalul), <code>avg</code> (media), <code>min</code>, "
   "<code>max</code>. Orice coloană din <code>select</code> care nu este calculată trebuie să apară în "
   "<code>group by</code>. În pandas, aceiași pași îi face <code>groupby</code> urmat de <code>agg</code>.</p>"
   + GRUP_VIZ
   + "<p>Pe tot tabelul, rezultatul are câte un rând pentru fiecare dintre cele 37 de țări:</p>"
   + PANDAS + f'<div class="pd5__rez">{REZ_TARA}</div>' + CAND
   + "<p>Unele țări au o singură regiune NUTS2 (" + ", ".join(PT["o_regiune"]) + "): în comparațiile dintre regiuni, "
     "o astfel de regiune este de fapt o țară întreagă.</p>"
   + "<h3>Aceeași țară sau țări diferite</h3>"
     "<p>Gruparea se poate face și după o coloană calculată. Cu <code>case when</code>, perechile de regiuni se împart "
     "în două grupuri: din aceeași țară și din țări diferite.</p>"
   + ix("grupare", "group by, pas cu pas", GRUPARE)
   + "<h3>Atenție la medii</h3>"
     "<p>Media unei variabile pe regiunile unei țări nu este valoarea țării, pentru că regiunile au populații diferite: "
     "o regiune mică cântărește cât una mare. Când se agregă, întrebarea de pus întâi este ce reprezintă un rând.</p>"
   + ix("medii", "Lituania, două regiuni", MEDII)
   + ix("prezice", "Ce se transferă de la bază", UNDE),
   dupa=V_GRUP)



_IT = next(r for r in D["sql"]["randuri"] if r[0] == "IT" and r[1] == "RO")
MIGR = (
    '<div class="mi5">'
    '<div class="mi5__c"><h4><code>migratie</code>: un rând = o cetățenie într-o țară</h4>'
    + tabel(["tara_rezidenta", "cetatenie", "persoane"], [
        ['<span class="mi5__a mono">RO</span>', '<span class="mi5__a mono">IT</span>', '<span class="mi5__a">14.856</span>'],
        ['<span class="mi5__b mono">IT</span>', '<span class="mi5__b mono">RO</span>', '<span class="mi5__b">1.073.196</span>'],
    ])
    + '<p class="mi5__x"><span class="mi5__a">italieni în România</span> · '
      '<span class="mi5__b">români în Italia</span></p></div>'
    '<div class="mi5__s" aria-hidden="true"><span>două uniri</span></div>'
    '<div class="mi5__c"><h4><code>perechi_tari</code>: un rând = o pereche</h4>'
    + tabel(["tara_1", "tara_2", "din_1_in_2", "din_2_in_1", "migranti"], [
        ["~IT", "~RO", '<span class="mi5__a">14.856</span>', '<span class="mi5__b">1.073.196</span>',
         f"<b>{nr(_IT[3])}</b>"],
    ])
    + '<ol class="mi5__pasi">'
      '<li><span class="mi5__a">unirea 1</span>: <code>cetatenie</code> = <code>tara_1</code>, '
      '<code>tara_rezidenta</code> = <code>tara_2</code></li>'
      '<li><span class="mi5__b">unirea 2</span>: <code>cetatenie</code> = <code>tara_2</code>, '
      '<code>tara_rezidenta</code> = <code>tara_1</code></li>'
      '<li><b>suma</b>: <code>migranti = din_1_in_2 + din_2_in_1</code>; dacă un sens lipsește, suma rămâne lipsă</li>'
      "</ol></div>"
    "</div>")

sl("s10", "Agregarea", "Perechile de țări",
   "<h2>Migrația are direcție</h2>"
   "<p class=\"cheie\">Un rând din <code>migratie</code> are un sens. O pereche de țări are două: tabelul se unește de două ori.</p>"
   + MIGR,
   manual=
   "<h2>Migrația are direcție</h2>"
   "<p>Al treilea tabel de analiză are câte un rând pe pereche de țări: SCI, migrația și zborurile. În tabelul "
   "<code>migratie</code>, un rând spune câți cetățeni ai unei țări trăiesc în altă țară, deci are un sens: "
   "italienii din România nu sunt același lucru cu românii din Italia. Perechea Italia-România are însă un singur "
   "rând, cu ambele sensuri.</p>"
   "<p>De aceea, tabelul migrației se unește de două ori. La prima unire, cetățenia se potrivește cu prima țară a "
   "perechii și țara de rezidență cu a doua; la a doua unire, invers. Coloanele se redenumesc înainte de fiecare "
   "unire, ca să se potrivească cu cheile perechii. La final, cele două sensuri se adună.</p>"
   + MIGR
   + f"<p>Pentru Italia și România, cele două sensuri diferă de peste 70 de ori. SCI-ul perechii este {nr(_IT[2])}, "
     f"iar zborurile dintre ele au transportat {nr(_IT[4])} de pasageri într-un an.</p>"
     "<p>Înainte de unire, încă o agregare: nu toate țările raportează la Eurostat migranții pe fiecare cetățenie. "
     "Se numără, pentru fiecare țară de rezidență, câte cetățenii au o valoare (<code>count</code> numără doar "
     "valorile prezente), iar perechile se păstrează doar pentru țările care raportează cel puțin 20. Rămân "
     f"{T['perechi_tari']} de perechi de țări.</p>")



DOVADA = {
    "id": "c5-dovada-baza",
    "sarcina": "Trei interogări din caiet, rulate pe baza proprie, <code>data/dsw.db</code>. Ieșirea fiecăreia se lipește în câmpul ei.",
    "indiciu": "Celulele se rulează la finalul caietului 05, după ce toate tabelele sunt în bază.",
    "pasi": [
        {"t": "Tabelele din bază",
         "cmd": "pd.read_sql(\"select name from sqlite_master where type = 'table'\", engine)",
         "gol": "lista afișată",
         "cauta": r"^(?=[\s\S]*perechi_regiuni)(?=[\s\S]*perechi_tari)(?=[\s\S]*\bregiuni\b)",
         "ind": "Printre tabele, în orice ordine: <code>regiuni</code>, <code>perechi_regiuni</code>, <code>perechi_tari</code>.",
         "daca_nu": "Lipsește un tabel: celulele cu to_sql din caiet trebuie rulate din nou."},
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
         "daca_nu": "Rândul aceeasi tara trebuie să aibă 2385 de perechi. Altfel, tabelul perechi_regiuni nu este cel din caiet."},
    ],
    "explicatie": "Cele trei tabele sunt în bază, iar agregarea dă aceleași rezultate ca în caiet. La cursul 6, "
                  "caietul citește direct de aici, cu <code>pd.read_sql</code>.",
}


sl("s11", "Echipa", "Verificarea bazei",
   "<h2>Verificarea bazei</h2>"
   + ix("dovada", "Verificarea bazei", DOVADA),
   manual=
   "<h2>Verificarea bazei</h2>"
   "<p>Verificarea arată, cu ieșirea interogărilor rulate pe baza proprie, că tabelele sunt încărcate și că "
   "agregarea dă rezultatele din caiet. Butonul <b>Indiciu</b> arată ce trebuie să conțină fiecare rezultat.</p>"
   + ix("dovada", "Verificarea bazei", DOVADA))



def _caiet(n, nume, rol, cls=""):
    return (f'<div class="eb5__k {cls}"><code>{n}_{nume}.ipynb</code><small>{rol}</small></div>')

ECHIPA = (
    '<div class="eb5">'
    '<div class="eb5__col">'
    + _caiet("01", "collection", "colectarea") + _caiet("02", "preprocessing", "preprocesarea")
    + _caiet("03", "cleaning_integration", "curățarea și integrarea", "eb5__k--scrie")
    + '</div>'
    '<div class="eb5__sag eb5__sag--scrie"><code>to_sql</code><span>scrie</span></div>'
    '<div class="eb5__db"><div class="eb5__cil"><b>proiect.db</b></div><small>data/processed/</small></div>'
    '<div class="eb5__sag eb5__sag--citeste"><code>read_sql</code><span>citesc</span></div>'
    '<div class="eb5__col">'
    + _caiet("04", "exploration", "explorarea", "eb5__k--citeste") + _caiet("05", "model", "modelul", "eb5__k--citeste")
    + "</div></div>"
    '<div class="eb5__jos">'
    '<span><b>Pe GitHub</b>Fișierul se urcă împreună cu caietul 03; colegii îl primesc cu <code>git pull</code>.</span>'
    '<span><b>Un singur scriitor</b>Git nu poate uni două versiuni ale aceluiași fișier de bază de date.</span>'
    '<span><b>La cursul 6</b>Explorarea: ipoteze din literatură, grafice, rețele.</span>'
    "</div>")

sl("s12", "Mai departe", "Baza echipei, cursul 6",
   "<h2>Baza echipei</h2>"
   + ECHIPA,
   manual=
   "<h2>Baza echipei</h2>"
   "<p>Baza de la seminar este a fiecăruia, pe calculatorul lui. Pentru proiect, echipa folosește una singură, ca "
   "toți să lucreze pe aceleași date: un fișier SQLite din depozit, <code>data/processed/proiect.db</code>. Caietul "
   "03 o creează și încarcă tabelele finale; caietele 04 și 05 doar citesc din ea. Caietele stau în "
   "<code>notebooks/</code>, deci adresa urcă un nivel: <code>sqlite:///../data/processed/proiect.db</code>.</p>"
   + ECHIPA
   + "<p>Cu tabelele în bază, lecția următoare le examinează: ce tipare apar și ce explicații merită verificate, "
     "pornind de la ipoteze din literatură.</p>"
   + surse("Documentația", [
       ("SQLite: când se folosește", "https://sqlite.org/whentouse.html", "baza într-un fișier, față de bazele cu server"),
       ("SQLAlchemy: create_engine", "https://docs.sqlalchemy.org/en/21/core/engines.html", "adresele bazelor de date"),
       ("pandas: read_sql și to_sql", "https://pandas.pydata.org/docs/reference/api/pandas.read_sql.html", "citirea și scrierea tabelelor"),
       ("pandas: merge", "https://pandas.pydata.org/docs/user_guide/merging.html", "<code>concat</code>, <code>merge</code>, tipurile de unire"),
       ("pandas: groupby", "https://pandas.pydata.org/docs/user_guide/groupby.html", "gruparea și <code>agg</code>"),
       ("CS50 SQL", "https://cs50.harvard.edu/sql/", "curs deschis: interogări, legături, agregare, pe SQLite"),
       ("Neon: conectarea cu SQLAlchemy", "https://neon.com/docs/guides/sqlalchemy", "PostgreSQL în cloud"),
   ]))


if __name__ == "__main__":
    L.scrie_tot()
