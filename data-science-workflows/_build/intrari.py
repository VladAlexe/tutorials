"""Paginile de intrare ale lecțiilor (cN-.../index.html), toate din același tipar.

Ca la Ingineria AI: o bară subțire sus, cu drumul înapoi la curs și cu
butoanele lecției; apoi secțiuni etichetate, una sub alta. Fără fișe cu
„90 de minute”, fără inel de progres, fără „Celelalte lecții”: înapoi la curs
se ajunge mereu din bară.

  Începe lecția  -> lectie/#1, mereu de la primul slide
  Manualul       -> tutorial/
  Caietul        -> notebook-ul de pe GitHub
  Predă          -> doar profesorul; pornește ora și deschide lecția

Conținutul stă în _build/intrari.json. Rulează: python3 _build/intrari.py
"""
import json, re, pathlib, html

R = pathlib.Path(__file__).resolve().parent.parent
V = (R / "_build" / "VERSIUNE").read_text().strip() if (R / "_build" / "VERSIUNE").exists() else "1"
from comun import REPO, REPO_ZIP, REPO_FOLDER

# În intrari.json, depozitul cursului se scrie @REPO@ (pagina lui), @ZIP@
# (arhiva) și @FOLDER@ (numele folderului din arhivă): așa, o redenumire pe
# GitHub se schimbă într-un singur loc, în comun.py.
_T = (R / "_build" / "intrari.json").read_text(encoding="utf-8")
_T = _T.replace("@ZIP@", REPO_ZIP).replace("@FOLDER@", REPO_FOLDER).replace("@REPO@", REPO)
D = json.loads(_T)

ETICHETE = {
    "Despre lecția asta": ("despre", "Despre lecție"),
    "Ce va conține": ("despre", "Despre lecție"),
    "Obiective": ("obiective", "Obiectivele lecției"),
    "Pregătire": ("nevoie", "Pregătire"),
    "Ce se adaugă la proiect": ("proiect", "Ce se adaugă la proiect"),
}


def curata(h):
    return re.sub(r"\n\s+", "\n", h)


def pagina(cheie, x):
    nr = x["nr"]
    sec = []
    for s in x["sectiuni"]:
        cls, et = ETICHETE.get(s["t"], ("alt", s["t"]))
        sec.append(f'''
  <section class="sec sec--{cls}">
    <p class="sec__et">{et}</p>
    <div class="sec__corp">{curata(s["html"])}</div>
  </section>''')
        if cls == "obiective":
            sec.append("@@MATERIALE@@")
    corp = "".join(sec)

    are_lectie = (R / cheie / "lectie" / "index.html").exists()
    # materialele: rânduri simple, titlu și o propoziție; fără iconițe, fără cartonașe
    mat = []
    if are_lectie:
        mat += [("lectie/#1", "Lecția", "Slide-urile lecției, cu exercițiile de la curs. Se deschid de la primul slide.", False),
                ("tutorial/", "Manualul", "Materialul complet al lecției, pentru studiu individual.", False)]
    if x["caiet"]:
        mat.append((x["caiet"], "Caietul",
                    x.get("caiet_d") or "Caietul Jupyter al lecției, pe GitHub, cu codul de la seminar.", True))
    for r in x["resurse"]:
        mat.append((r["href"], r["t"], r["d"], r["href"].startswith("http")))
    materiale = f'''
  <section class="sec">
    <p class="sec__et">Materiale</p>
    <div class="mat">{"".join(f"""
      <a class="mat__c" href="{h}"{' target="_blank" rel="noopener"' if ext else ""}>
        <span class="mat__t">{t}{" ↗" if ext else ""}</span>
        <span class="mat__d">{d}</span>
      </a>""" for h, t, d, ext in mat)}
    </div>
  </section>''' if mat else ""
    if "@@MATERIALE@@" in corp:
        corp = corp.replace("@@MATERIALE@@", materiale, 1)
    else:
        corp = materiale + corp

    if x["legaturi"]:
        corp += f'''
  <section class="sec">
    <p class="sec__et">Legături</p>
    <div class="leg-lista">{"".join(f"""
      <a href="{l["href"]}" target="_blank" rel="noopener"><span>{l["t"]}</span><small>{l["g"]}</small></a>""" for l in x["legaturi"])}
    </div>
  </section>'''

    caiet_btn = (f'<a class="bl__b" href="{x["caiet"]}" target="_blank" rel="noopener">Caietul ↗</a>'
                 if x["caiet"] else "")
    titlu = html.unescape(x["titlu"])
    incepe = ('<a class="bl__b bl__b--tare" href="lectie/#1" data-rol="incepe">Începe lecția</a>'
              if are_lectie else '<span class="bl__b bl__b--stins">Lecție în pregătire</span>')
    preda = ('<a class="bl__b bl__b--preda" href="lectie/?preda=1#1" data-rol="preda" hidden '
             'title="Pornește ora pentru grupă și deschide lecția">Predă</a>' if are_lectie else "")

    return f'''<!DOCTYPE html>
<html lang="ro">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lecția {nr}. {titlu} · Fluxuri de lucru</title>
<meta name="description" content="{html.escape(x["descriere"], quote=True)}">
<link rel="stylesheet" href="../css/fonturi.css?v={V}">
<link rel="stylesheet" href="../css/sistem.css?v={V}">
<link rel="stylesheet" href="../css/intrare.css?v={V}">
<script src="../js/tema.js?v={V}"></script>
</head>
<body>

<div id="antet" data-aici="Lecția {nr}"></div>

<div class="bl">
  <div class="pagina bl__in">
    <a class="bl__inapoi" href="../">← Fluxuri de lucru</a>
    <span class="bl__sep"></span>
    <span class="bl__aici">Lecția {nr}</span>
    <span class="bl__sp"></span>
    <span class="bl__fapte" id="fapte">
      {incepe}
      {'<a class="bl__b" href="tutorial/">Manualul</a>' if are_lectie else ""}
      {caiet_btn}
      {preda}
    </span>
  </div>
</div>

<main>
<div class="pagina intr">

  <header class="intr__erou">
    <p class="intr__tag">Lecția {nr} din 8</p>
    <h1>{titlu}</h1>
    <p class="deck">{x["deck"]}</p>
    <p class="intr__inchis" id="inchis" hidden>Lecția se deschide după ce este predată la curs.
    Până atunci, descrierea de mai jos rămâne disponibilă.</p>
  </header>
{corp}

  <p class="intr__jos"><a href="../">← Înapoi la curs</a></p>

</div>
</main>

<div id="subsol"></div>

<script type="module">
/* Profesorul vede în plus „Predă”. Studentul, dacă lecția nu i-a fost
   predată încă, vede pagina, dar fără intrare în lecție. */
try {{
  const [{{ profil }}, O, {{ LECTII }}] = await Promise.all([
    import("../js/auth.js?v={V}"), import("../js/ora.js?v={V}"), import("../js/curs.js?v={V}")]);
  const p = await profil();
  if (p.profesor){{
    const b = document.querySelector('[data-rol="preda"]');
    if (b){{
      b.removeAttribute("hidden");
      /* dacă ora lecției ăsteia e deja pornită, butonul te duce în ea */
      const viu = await O.deschisa("c{nr}");
      if (viu){{ b.textContent = "● Înapoi la oră"; b.href = "lectie/#" + (viu.slide_nr || 1); b.title = "Ora este în desfășurare"; }}
      /* altfel butonul pornește ora direct: nu alegi nicio grupă, cine are
         codul intră, iar fiecare student e deja în grupa lui din listă */
    }}
  }} else {{
    /* deschisă doar după ce a fost predată: o oră pornită, nearhivată */
    const pred = await O.predate();
    if (pred && !pred.has("c{nr}")){{
      document.getElementById("inchis").hidden = false;
      document.querySelectorAll('[data-rol="incepe"], .mat__c[href^="lectie"]').forEach(a => {{
        a.removeAttribute("href"); a.classList.add("bl__b--stins", "stins");
      }});
      const b = document.querySelector('[data-rol="incepe"]');
      if (b) b.textContent = "Se deschide la oră";
    }}
  }}
}} catch {{ /* fără cont sau fără rețea, pagina rămâne cum e */ }}
</script>
<script type="module" src="../js/antet.js?v={V}"></script>
<script type="module" src="../js/subsol.js?v={V}"></script>
</body>
</html>
'''


for cheie, x in D.items():
    (R / cheie / "index.html").write_text(pagina(cheie, x), encoding="utf-8")
    print("scris", cheie)
