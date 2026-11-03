#!/usr/bin/env python3
"""
Catalogul datelor, ca pagină: c3-versionare-git/catalog/index.html.

Sursa rămâne una singură: curs/data/CATALOG.md din depozitul cursului
(C:\\PROJECTS\\DSW2026). Pagina se refă din el, ca să nu existe două versiuni:

    python3 _build/catalog.py                  # citește ../../../DSW2026/curs/data/CATALOG.md
    python3 _build/catalog.py cale/CATALOG.md  # sau din altă parte

Se rulează după fiecare schimbare din CATALOG.md, apoi versiune.py.
Aspectul e cel al fișei „Lucrul cu Git” (c3-versionare-git/git/).
"""
import html, re, sys
from pathlib import Path

RAD = Path(__file__).resolve().parent.parent
SURSA = Path(sys.argv[1]) if len(sys.argv) > 1 else RAD.parents[2] / "DSW2026" / "curs" / "data" / "CATALOG.md"
V = (RAD / "_build" / "VERSIUNE").read_text().strip()
GITHUB = "https://github.com/dsw-ubb-2026/-DSW2026/blob/main/curs/data/CATALOG.md"


def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<![\w*])\*([^*]+)\*(?![\w*])", r"<em>\1</em>", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a class="leg" href="\2" target="_blank" rel="noopener">\1</a>', t)
    return t


def slug(t):
    t = re.sub(r"^\d+\.\s*", "", t).lower()
    for a, b in zip("ăâîșțş", "aaists"):
        t = t.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def corp(md):
    linii = md.splitlines()
    out, cup, i = [], [], 0
    titlu = deck = None
    while i < len(linii):
        l = linii[i]
        if l.startswith("# "):
            titlu = l[2:].strip(); i += 1; continue
        if l.startswith("```"):
            j = i + 1
            while not linii[j].startswith("```"):
                j += 1
            cod = html.escape("\n".join(linii[i + 1:j]), quote=False)
            cod = re.sub(r"(#[^\n]*)", r'<span class="c">\1</span>', cod)
            out.append(f"<pre><code>{cod}</code></pre>"); i = j + 1; continue
        if l.startswith("## "):
            t = l[3:].strip(); s = slug(t); cup.append((s, re.sub(r"^\d+\.\s*", "", t)))
            out.append(f'<h2 id="{s}">{inline(t)}</h2>'); i += 1; continue
        if l.startswith("|"):
            rows = []
            while i < len(linii) and linii[i].startswith("|"):
                cel = [c.strip() for c in linii[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", c) for c in cel):
                    rows.append(cel)
                i += 1
            cap, rest = rows[0], rows[1:]
            out.append('<div class="tbw"><table class="tb tb--cat"><thead><tr>'
                       + "".join(f"<th>{inline(c)}</th>" for c in cap) + "</tr></thead><tbody>"
                       + "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rest)
                       + "</tbody></table></div>")
            continue
        if l.startswith("- "):
            items = []
            while i < len(linii) and linii[i].startswith("- "):
                items.append(linii[i][2:]); i += 1
            out.append('<ul class="src">' + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ul>")
            continue
        if l.strip():
            par = [l]
            i += 1
            while i < len(linii) and linii[i].strip() and not re.match(r"(#|\||- |```)", linii[i]):
                par.append(linii[i]); i += 1
            p = inline(" ".join(par))
            if deck is None and not cup:
                deck = p
            else:
                out.append(f"<p>{p}</p>")
            continue
        i += 1
    return titlu, deck, cup, "\n  ".join(out)


titlu, deck, cup, continut = corp(SURSA.read_text(encoding="utf-8"))
cuprins = "".join(f'<li><a href="#{s}">{html.escape(t)}</a></li>' for s, t in cup)

# stilul fișei Git, luat din pagina ei, ca cele două să arate la fel
git = (RAD / "c3-versionare-git" / "git" / "index.html").read_text(encoding="utf-8")
stil = re.search(r"<style>(.*?)</style>", git, re.S).group(1)
stil += """
  .tb--cat th{font-family:var(--sans);font-size:var(--t1);font-weight:600;text-align:left;color:var(--text-3);
    text-transform:uppercase;letter-spacing:.04em;padding:6px 12px 6px 0;border-bottom:1px solid var(--linie-2)}
  .tb--cat td:first-child{width:auto}
  .tb--cat code{cursor:text;white-space:normal}
  .tb--cat code:hover{color:var(--text)}
"""

pagina = f'''<!DOCTYPE html>
<html lang="ro">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Catalogul datelor · Fluxuri de lucru</title>
<meta name="description" content="Seturile de date pentru proiect, aduse prin API: perechi de țări, regiuni NUTS2 și țări, cu codurile și filtrele lor.">
<meta name="robots" content="index,nofollow">
<link rel="stylesheet" href="../../css/fonturi.css?v={V}">
<link rel="stylesheet" href="../../css/sistem.css?v={V}">
<script src="../../js/tema.js?v={V}"></script>
<style>{stil}</style>
</head>
<body>

<div id="antet" data-aici="Cursul 3 · Catalogul datelor"></div>

<main>
<div class="gf">
  <a class="gf__inapoi" href="../" data-inapoi>← Înapoi</a>
  <p class="supratitlu">Cursul 3 · Resursă</p>
  <h1>{html.escape(titlu)}</h1>
  <p class="deck">{deck}</p>
  <p>Aceeași listă stă în depozitul cursului, ca <a class="leg" href="{GITHUB}" target="_blank" rel="noopener">curs/data/CATALOG.md</a>; pagina de față se refă din ea.</p>
  <ul class="gf__cup">{cuprins}</ul>

  {continut}

  <div class="gf__jos">
    <a href="../" data-inapoi>← Înapoi</a>
    <a href="../">Pagina cursului 3</a>
    <a href="../lectie/#1">Slide-urile cursului 3</a>
    <a href="../tutorial/">Manualul cursului 3</a>
    <a href="../git/">Lucrul cu Git</a>
  </div>
</div>
</main>

<div id="subsol"></div>
<script type="module" src="../../js/antet.js?v={V}"></script>
<script type="module" src="../../js/subsol.js?v={V}"></script>
<script>
/* Înapoi: dacă ai venit dintr-o pagină a sitului (slide-uri, manual), te
   întorci exact acolo; altfel, la pagina cursului 3. */
document.querySelectorAll("[data-inapoi]").forEach(a => a.addEventListener("click", e => {{
  try {{
    const r = document.referrer ? new URL(document.referrer) : null;
    if (r && r.origin === location.origin && r.pathname !== location.pathname && history.length > 1){{
      e.preventDefault(); history.back();
    }}
  }} catch (_) {{}}
}}));
</script>
</body>
</html>
'''
d = RAD / "c3-versionare-git" / "catalog"
d.mkdir(exist_ok=True)
(d / "index.html").write_text(pagina, encoding="utf-8")
print("scris", d / "index.html", "din", SURSA)
