# -*- coding: utf-8 -*-
"""
Mașinăria comună a lecțiilor.

Fiecare lecție se scrie într-un singur fișier, `_build/cN.py`, care conține
numai conținutul. Tot ce se repetă, adică felul în care conținutul devine
două pagini, stă aici:

  lectie/index.html    slide-uri: text scurt, mult interactiv. Profesorul
                       vorbește, pagina susține. Nimic de citit cu voce tare.
  tutorial/index.html  manualul: același drum, explicat pe larg și tehnic, cu
                       exact aceleași exerciții, pentru reluat după curs.
  date/harta-cN.json   ce sarcini stau pe ce slide, pentru panoul profesorului.

Exercițiile au aceleași id-uri în amândouă paginile, deci ce faci la curs se
vede ca făcut și în manual, și invers.

Nu se rulează singur. Se importă din `_build/cN.py`.
"""

import json
import pathlib
import re

RAD = pathlib.Path(__file__).resolve().parent.parent

# Ștampila împotriva memoriei browserului. Nu se scrie de mână aici: o
# rescrie `_build/versiune.py` peste toate fișierele deodată, la fiecare push.
V = "?v=16"


# ---------------------------------------------------------------- bucăți ---

FEL = {"etape": "Explorator", "terminal": "Terminal", "tipuri": "Exercițiu",
       "json": "Explorator", "arbore": "Explorator", "autoevaluare": "Evaluare",
       "matrice": "Date reale", "bare": "Date reale", "diverg": "Date reale",
       "cod": "Scrii cod", "ordine": "Exercițiu", "sortare": "Exercițiu",
       "dovada": "Verificare la tine", "asteptari": "Scrii tu",
       "url": "Disecție", "metode": "Potrivire", "cronologie": "Cronologie",
       "flux": "Vezi cum circulă", "raspuns": "Trimite și vezi",
       "zone": "Mută tu", "ramuri": "Desenează tu", "conflict": "Rezolvă tu",
       "cote": "Date reale", "prag": "Unde tai",
       "imbinare": "Încearcă felurile", "tabel": "Tabel",
       "coloane": "Declară tipul", "desfa": "Vezi cum se desface"}
fel_et = lambda f: FEL.get(f, "Interactiv")


def ix(fel, titlu, date=None, sarcina=None, corp=""):
    """Un bloc interactiv, identic în slide și în manual."""
    j = ""
    if date is not None:
        j = ('<script type="application/json">'
             + json.dumps(date, ensure_ascii=False) + "</script>")
    s = f'<p class="ix__sarcina">{sarcina}</p>' if sarcina else ""
    return (f'<div class="ix" data-ix="{fel}">\n'
            f'  <div class="ix__cap"><span class="ix__fel">{fel_et(fel)}</span>'
            f'<span class="ix__t">{titlu}</span></div>\n'
            f'  <div class="ix__corp">{s}{corp}{j}</div>\n</div>')


def verif(id_, corect, q, optiuni, ex):
    o = "\n    ".join(f"<button>{x}</button>" for x in optiuni)
    return (f'<div class="verif" data-id="{id_}" data-corect="{corect}">\n'
            f'    <p class="verif__q">{q}</p>\n    {o}\n'
            f'    <p class="verif__ex">{ex}</p>\n  </div>')


def tabel(capete, randuri):
    c = "".join(f"<th>{x}</th>" for x in capete)
    r = "".join("<tr>" + "".join(
        f'<td class="mono">{v[1:]}</td>' if v.startswith("~") else f"<td>{v}</td>"
        for v in rand) + "</tr>" for rand in randuri)
    return f'<table class="tabel"><thead><tr>{c}</tr></thead><tbody>{r}</tbody></table>'


def nota(et, txt, sobru=False):
    return (f'<div class="nota{" nota--sobru" if sobru else ""}">'
            f'<div class="nota__et">{et}</div><p>{txt}</p></div>')


# --------------------------------------------------------------- șabloane ---

CAP = """<!DOCTYPE html>
<html lang="ro">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titlu}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="index,nofollow">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../css/sistem.css{v}">
<link rel="stylesheet" href="../../css/{stil}.css{v}">
<link rel="stylesheet" href="../../css/interactiv.css{v}">
<link rel="stylesheet" href="../../css/grafice.css{v}">
<link rel="stylesheet" href="../../css/exercitii.css{v}">
<script src="../../js/tema.js{v}"></script>
</head>
<body{corp}>
"""

JS_COMUN = """<script type="module" src="../../js/antet.js{v}"></script>
<script type="module">
import {{ porneste as pornesteIx }} from "../../js/interactiv.js{v}";
import {{ porneste as pornesteVerif }} from "../../js/verificare.js{v}";
{imp}
pornesteIx();
pornesteVerif("{capitol}");
{pornire}
</script>
</body>
</html>
"""


# ------------------------------------------------------------- o lecție ---

class Lectie:
    """Conținutul unei lecții, plus cele trei fișiere care ies din el."""

    def __init__(self, nr, cheie, titlu, desc):
        self.nr = nr                     # 1, 2, …
        self.cheie = cheie               # "c2-colectarea-prin-api"
        self.capitol = f"c{nr}"          # "c2"
        self.titlu = titlu
        self.desc = desc
        self.S = []

    def sl(self, id_, grup, t, slide, manual=None, dupa=""):
        """Un slide. `manual` e versiunea lungă; dacă lipsește, e aceeași."""
        self.S.append(dict(id=id_, grup=grup, t=t, slide=slide,
                           manual=manual if manual is not None else slide,
                           dupa=dupa))

    # --------------------------------------------------------------------
    def scrie_lectie(self):
        b = [CAP.format(titlu=f"Cursul {self.nr} — Fluxuri de lucru pentru știința datelor",
                        desc=self.desc, v=V, stil="slide", corp=' class="corp--app"')]
        b.append(f'<div id="antet" data-aici="Cursul {self.nr} · {self.titlu}" '
                 f'data-crom="1"></div>\n')
        b.append('<div class="rnr">\n<main class="rnr__scena" tabindex="-1">\n')
        for s in self.S:
            b.append(f'\n<section class="sld" id="{s["id"]}" data-grup="{s["grup"]}" '
                     f'data-t="{s["t"]}">\n{s["slide"]}\n{s["dupa"]}\n</section>\n')
        b.append('\n</main>\n</div>\n\n')
        b.append(JS_COMUN.format(
            v=V, capitol=self.capitol,
            imp=f'import {{ porneste as pornesteSlide }} from "../../js/slide.js{V}";',
            pornire=f'pornesteSlide({{ capitol:"{self.capitol}", lectie:"{self.cheie}" }});'))
        d = RAD / self.cheie / "lectie"
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text("".join(b), encoding="utf-8")

    # --------------------------------------------------------------------
    def scrie_tutorial(self):
        grupuri = []
        for s in self.S:
            if not grupuri or grupuri[-1][0] != s["grup"]:
                grupuri.append((s["grup"], []))
            grupuri[-1][1].append(s)

        cuprins = "".join(
            f'<div class="tut__g">{g}</div>' +
            "".join(f'<a href="#{s["id"]}"><span class="n">{self.S.index(s)+1}</span>'
                    f'<span>{s["t"]}</span></a>' for s in lst)
            for g, lst in grupuri)

        b = [CAP.format(titlu=f"Cursul {self.nr}, manual — Fluxuri de lucru pentru știința datelor",
                        desc=f"Suportul de curs pentru cursul {self.nr}, explicat pe larg, "
                             f"cu aceleași exerciții ca la clasă.",
                        v=V, stil="tutorial", corp="")]
        b.append(f'<div id="antet" data-aici="Cursul {self.nr} · Manual"></div>\n')
        b.append('<main><div class="pagina"><div class="tut">\n')
        b.append(f'''<aside class="tut__stanga">
  <div class="tut__cap"><span class="tut__et">Manual</span>
    <span class="tut__t">Cursul {self.nr}</span>
    <span class="tut__st">{self.titlu}</span></div>
  <nav class="tut__nav">{cuprins}</nav>
  <div class="tut__jos">
    <a href="../lectie/">Slide-urile de la curs</a>
    <a href="../">Pagina cursului</a>
    <a href="../../cont/">Contul meu</a>
  </div>
</aside>\n''')
        b.append('<article class="tut__corp">\n')
        b.append(f'''<header class="tut__intro">
  <p class="supratitlu">Cursul {self.nr} · Manual</p>
  <h1>{self.titlu}</h1>
  <p class="deck">Același drum ca la curs, explicat pe larg și cu aceleași
  exerciții. Dacă le-ai făcut la clasă, apar deja rezolvate; dacă vrei să le
  reiei, îți poți reseta progresul din
  <a class="leg" href="../../cont/">contul tău</a>.</p>
</header>\n''')
        for i, s in enumerate(self.S, 1):
            b.append(f'\n<section class="tut__s" id="{s["id"]}">\n'
                     f'<span class="tut__nr">{i:02d} · {s["grup"]}</span>\n'
                     f'{s["manual"]}\n{s["dupa"]}\n</section>\n')
        b.append('</article>\n</div></div></main>\n<div id="subsol"></div>\n\n')
        b.append(JS_COMUN.format(
            v=V, capitol=self.capitol,
            imp=f'import {{ porneste as pornesteTut }} from "../../js/tutorial.js{V}";',
            pornire=f'pornesteTut("{self.capitol}");'))
        d = RAD / self.cheie / "tutorial"
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text("".join(b), encoding="utf-8")

    # --------------------------------------------------------------------
    # Ce fel de bloc interactiv produce un rând în baza de date. „cod" ajunge
    # în rulari_cod și se poate arăta pe slide în panoul profesorului.
    FEL_SARCINA = {"cod": "cod", "ordine": "cod", "sortare": "cod",
                   "dovada": "cod", "tipuri": "cod", "autoevaluare": "cod",
                   "asteptari": "cod", "url": "cod", "metode": "cod",
                   "raspuns": "cod", "zone": "cod", "ramuri": "cod",
                   "conflict": "cod", "prag": "cod", "imbinare": "cod",
                   "coloane": "cod", "desfa": "cod"}

    def scrie_harta(self):
        """Ce sarcini stau pe fiecare slide.

        Panoul profesorului are nevoie de ea ca să poată spune „la slide-ul
        10, uite cum a răspuns grupa". Baza de date știe răspunsurile, dar nu
        știe pe ce slide stă fiecare întrebare: asta se știe doar aici.
        Se rescrie la fiecare rulare, deci nu are cum să rămână în urmă.
        """
        slides = []
        for i, s in enumerate(self.S, 1):
            # și ce stă în `dupa`: o verificare pusă sub slide e tot o
            # poartă în browser, deci trebuie să apară și în hartă,
            # altfel profesorul n-o vede la slide-ul pe care e.
            h, gasite = s["slide"] + s.get("dupa", ""), []

            for m in re.finditer(r'class="verif" data-id="([^"]+)"', h):
                gasite.append((m.start(), {"id": m.group(1), "fel": "verificare"}))

            for m in re.finditer(r'data-ix="(\w+)"', h):
                fel = self.FEL_SARCINA.get(m.group(1))
                if not fel:
                    continue
                j = h.find('<script type="application/json">', m.end())
                if j < 0:
                    continue
                k = h.index("</script>", j)
                try:
                    date = json.loads(h[j + len('<script type="application/json">'):k])
                except Exception:
                    continue
                if isinstance(date, dict) and date.get("id"):
                    gasite.append((m.start(), {"id": date["id"], "fel": fel}))

            gasite.sort(key=lambda x: x[0])
            vazute, sarcini = set(), []
            for _, x in gasite:
                if x["id"] in vazute:
                    continue
                vazute.add(x["id"])
                sarcini.append(x)

            slides.append({"nr": i, "id": s["id"], "grup": s["grup"],
                           "titlu": s["t"], "sarcini": sarcini})

        harta = {"capitol": self.capitol, "total": len(self.S),
                 "sarcini": sum(len(x["sarcini"]) for x in slides),
                 "slide": slides}
        (RAD / "date").mkdir(parents=True, exist_ok=True)
        (RAD / f"date/harta-{self.capitol}.json").write_text(
            json.dumps(harta, ensure_ascii=False, indent=1), encoding="utf-8")
        return harta

    # --------------------------------------------------------------------
    def scrie_tot(self):
        self.scrie_lectie()
        self.scrie_tutorial()
        h = self.scrie_harta()
        porti = sum(len(re.findall(r'class="verif"', s["slide"] + s.get("dupa", ""))) +
                    len(re.findall(r'data-ix="(?:' + "|".join(self.FEL_SARCINA) + r')"',
                                   s["slide"] + s.get("dupa", "")))
                    for s in self.S)
        print(f"Cursul {self.nr}: {len(self.S)} slide-uri, {porti} porți, "
              f"{h['sarcini']} sarcini în hartă")
        print(f"  (în js/curs.js, lecția {self.nr} trebuie să aibă sarcini:{h['sarcini']})")
        for i, s in enumerate(self.S, 1):
            n = len([x for x in h["slide"][i-1]["sarcini"]])
            print(f'  {i:>2} [{s["grup"]:<18}] {s["t"]:<30} {"◆"*n}')
        return h
