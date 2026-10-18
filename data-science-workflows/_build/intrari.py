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
D = json.loads((R / "_build" / "intrari.json").read_text(encoding="utf-8"))

ETICHETE = {
    "Despre lecția asta": ("despre", "Despre"),
    "Ce va conține": ("despre", "Despre"),
    "La final vei putea": ("obiective", "La final vei putea"),
    "De ce ai nevoie, înainte": ("nevoie", "De ce ai nevoie, înainte"),
    "Ce adaugi la proiect": ("proiect", "Ce adaugi la proiect"),
}

IC = {
    "lectie": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4.5" width="18" height="12" rx="1.5"/><path d="M8.5 20h7M12 16.5V20"/></svg>',
    "manual": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v15H6.5A2.5 2.5 0 0 0 4 20.5z"/><path d="M8 7.5h8M8 11h6"/></svg>',
    "caiet": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"><path d="M4 4h11l5 5v11H4z"/><path d="M15 4v5h5M8 13h8M8 16.5h5"/></svg>',
    "alt": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M9 7H6a3 3 0 0 0 0 6h3M15 7h3a3 3 0 0 1 0 6h-3M8 10h8"/></svg>',
}


def curata(h):
    h = re.sub(r"\n\s+", "\n", h)
    h = h.replace("cu atribute aduse prin API de la Eurostat și Banca Mondială",
                  "cu migrația adusă prin API de la Eurostat și câțiva indicatori de la Banca Mondială")
    h = h.replace(' style="color:var(--text-2);font-size:16.5px"', "")
    return h


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

    mat = [("lectie/#1", IC["lectie"], "Lecția", "Slide-urile, cu exercițiile din oră. Se pornește mereu de la primul.", False),
           ("tutorial/", IC["manual"], "Manualul", "Tot materialul, pe larg, de citit în ritmul tău.", False)]
    if x["caiet"]:
        mat.append((x["caiet"], IC["caiet"], "Caietul", "Notebook-ul lecției, pe GitHub. Codul de la seminar.", True))
    for r in x["resurse"]:
        mat.append((r["href"], IC["alt"], r["t"], r["d"], r["href"].startswith("http")))
    materiale = f'''
  <section class="sec">
    <p class="sec__et">Materiale</p>
    <div class="mat">{"".join(f"""
      <a class="mat__c" href="{h}"{' target="_blank" rel="noopener"' if ext else ""}>
        <span class="mat__ic">{ic}</span>
        <span class="mat__t">{t}{" ↗" if ext else ""}</span>
        <span class="mat__d">{d}</span>
      </a>""" for h, ic, t, d, ext in mat)}
    </div>
  </section>'''
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
    are_lectie = (R / cheie / "lectie" / "index.html").exists()
    incepe = ('<a class="bl__b bl__b--tare" href="lectie/#1" data-rol="incepe">Începe lecția</a>'
              if are_lectie else '<span class="bl__b bl__b--stins">Lecția vine curând</span>')
    preda = ('<a class="bl__b bl__b--preda" href="lectie/?preda=1#1" data-rol="preda" hidden '
             'title="Pornește ora pentru grupă și deschide lecția">Predă</a>' if are_lectie else "")

    return f'''<!DOCTYPE html>
<html lang="ro">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lecția {nr}. {titlu} · Fluxuri de lucru</title>
<meta name="description" content="{html.escape(x["descriere"], quote=True)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap" rel="stylesheet">
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
      <a class="bl__b" href="tutorial/">Manualul</a>
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
    <p class="intr__inchis" id="inchis" hidden>Lecția se deschide după ce o facem la oră.
    Până atunci poți citi ce urmează, mai jos.</p>
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
      if (viu){{ b.textContent = "● Mergi la oră"; b.href = "lectie/"; b.title = "Ora e pornită"; }}
    }}
  }} else if (p.autentificat){{
    /* deschisă dacă a fost predată grupei sau dacă ai lucrat deja în ea */
    let atinsa = false;
    try {{ atinsa = !!localStorage.getItem("dsw.parcurs.c{nr}"); }} catch {{}}
    const pred = atinsa ? null : await O.predate();
    if (!atinsa && pred && !pred.has("c{nr}")){{
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
