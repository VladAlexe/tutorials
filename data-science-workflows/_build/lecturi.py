"""Pagina „Literatura proiectului": lecturi/index.html.

Aceeași listă ca în lecții (literatura.py), pusă într-o singură pagină, în
ordinea fluxului de lucru: de unde vin datele, ce spune teoria, ce metode
au folosit alții, unde găsești restul.

Rulare:  python _build/lecturi.py
"""
import pathlib
from literatura import REF, FEL

RAD = pathlib.Path(__file__).resolve().parent.parent
TITLU_LECTIE = {1: "Introducere", 2: "API", 3: "Git și cadrul teoretic", 4: "Curățarea",
                5: "Agregare și baze de date", 6: "Analiza exploratorie", 7: "Variabile și model",
                8: "Raportul"}

PILONI = [
    ("Legăturile", "Cine cu cine e legat, și cât de tare.", ["bailey2018", "johnston2026"]),
    ("Oamenii", "Rețelele de migranți și câmpurile de migrație: pe unde au plecat cei care țin legăturile.",
     ["palloni2001", "dehaas2010", "sandu2005", "sandu2025"]),
    ("Locul", "Ce explică legăturile fără nicio migrație: distanța, granița, limba, istoria.",
     ["bailey2020"]),
]


def a(k):
    return f'<a class="lit__a" href="{REF[k][3]}" target="_blank" rel="noopener">{REF[k][1]}</a>'


def pagina():
    feluri = "".join(
        f'<div class="lp__fel"><div class="lit__f lit__f--{f}">{et}</div><p>{ce}.</p></div>'
        for f, (et, ce) in FEL.items())
    piloni = "".join(
        f'<div class="pil__s"><div class="pil__n">{n}</div><div class="pil__d">{d}</div>'
        f'<div class="pil__r">{", ".join(a(k) for k in ks)}</div></div>' for n, d, ks in PILONI)
    pe_lectii = "".join(
        f'<tr><td class="mono">C{n}</td><td>{t}</td><td>'
        + ", ".join(a(k) for k, r in REF.items() if n in r[5] and r[0] != "documentatie")
        + "</td></tr>"
        for n, t in TITLU_LECTIE.items()
        if any(n in r[5] and r[0] != "documentatie" for r in REF.values()))
    complete = ""
    for f, (et, ce) in FEL.items():
        if f == "documentatie":
            continue
        li = "".join(
            f'<li><p class="lp__ref">{r[2]} <a href="{r[3]}" target="_blank" rel="noopener">{r[3]}</a></p>'
            f'<p class="lp__ce"><b>Ce luăm:</b> {r[4]}</p></li>'
            for k, r in REF.items() if r[0] == f)
        complete += f'<h3><span class="lit__f lit__f--{f}">{et}</span></h3><ul class="lp__lista">{li}</ul>'
    unelte = ", ".join(a(k) for k, r in REF.items() if r[0] == "documentatie")
    return f"""<!DOCTYPE html>
<html lang="ro">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Literatura proiectului · Fluxuri de lucru</title>
<meta name="description" content="Literatura pe care se sprijină proiectul cursului: datele SCI, teoria rețelelor și sistemelor migratorii, metodele folosite.">
<link rel="stylesheet" href="../css/fonturi.css?v=57">
<link rel="stylesheet" href="../css/sistem.css?v=57">
<link rel="stylesheet" href="../css/slide.css?v=57">
<link rel="stylesheet" href="../css/interactiv.css?v=57">
<script src="../js/tema.js?v=57"></script>
<style>
  .lp{{max-width:74ch;margin:0 auto;padding:44px 28px 80px}}
  .lp h2{{font-size:20px;margin:40px 0 12px}}
  .lp h3{{font-size:16px;margin:26px 0 8px}}
  .lp__feluri{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin:14px 0}}
  .lp__fel{{border:1px solid var(--linie);border-radius:10px;padding:10px 14px;background:var(--panza)}}
  .lp__fel p{{margin:4px 0 0;font-family:var(--sans);font-size:14px;color:var(--text-2)}}
  .lp table{{width:100%;border-collapse:collapse;font-family:var(--sans);font-size:14.5px}}
  .lp td{{padding:9px 12px 9px 0;border-bottom:1px solid var(--linie);vertical-align:top}}
  .lp td.mono{{font-family:var(--mono);color:var(--text-3)}}
  .lp__lista{{list-style:none;padding:0;margin:0}}
  .lp__lista li{{padding:10px 0;border-bottom:1px solid var(--linie)}}
  .lp__lista li::before{{content:none !important}}
  .lp__ref{{font-family:var(--serif);font-size:16px;line-height:1.5;margin:0}}
  .lp__ref a{{font-family:var(--mono);font-size:12px;color:var(--text-3);word-break:break-all}}
  .lp__ce{{font-family:var(--sans);font-size:14px;color:var(--text-2);margin:4px 0 0}}
  .lp ol.pasi{{display:block !important;font-family:var(--sans);font-size:15px;line-height:1.55;padding-left:1.5em;list-style:decimal;counter-reset:none}}
  .lp ol.pasi>li{{display:list-item !important;padding:0 !important;margin:0 0 8px;max-width:none}}
  .lp ol.pasi>li::before{{content:none !important;display:none !important}}
  @media(max-width:640px){{.lp{{padding:28px 16px 60px}}.lp__feluri{{grid-template-columns:1fr}}}}
</style>
</head>
<body>
<div id="antet" data-aici="Literatura proiectului"></div>
<main>
<div class="lp">
  <p class="supratitlu">Proiectul cursului</p>
  <h1>Literatura proiectului</h1>
  <p class="deck">Nu toată literatura despre SCI și migrație: doar ce folosesc caietele și ce
  susține direct pașii proiectului. Fiecare lectură apare și în lecția în care o folosim.</p>

  <h2>Patru feluri de surse</h2>
  <p>Într-un flux de lucru, literatura nu e un capitol scris la final. Intră în momente precise:
  teoria la definirea întrebării, metoda la analiză și model, documentația la fiecare pas tehnic,
  iar descrierea datelor oriunde le folosești.</p>
  <div class="lp__feluri">{feluri}</div>

  <h2>Cadrul proiectului</h2>
  <p>Întrebarea: <b>cât din legăturile dintre locuri se explică prin oamenii care au migrat între ele,
  și ce rămâne după distanță și migrație?</b> Ea stă pe trei piloni, fiecare cu literatura lui.</p>
  <div class="pil" style="--n:3"><div class="pil__stalpi">{piloni}</div>
  <div class="pil__baza"><span>regula</span>SCI nu e o măsură a migrației, iar un SCI din 2026 nu poate
  explica o migrație de dinainte: spunem „merg împreună”, nu „una o produce pe cealaltă” (de Haas, 2010).</div></div>

  <h2>Pe lecții</h2>
  <table><tbody>{pe_lectii}</tbody></table>

  <h2>Referințele complete</h2>
  {complete}

  <h2>Cum cauți mai departe</h2>
  <ol class="pasi">
    <li><b>Pornești de la un articol-ancoră</b>, de exemplu Bailey și colegii (2018).</li>
    <li><b>Mergi înapoi:</b> din referințele lui alegi ce ține de întrebarea voastră.</li>
    <li><b>Mergi înainte:</b> „Citat de” arată lucrările mai noi care l-au folosit.</li>
    <li><b>Cauți în engleză</b>, cu cuvintele din titluri: <i>social connectedness index</i>,
    <i>migrant networks</i>, <i>migration systems</i>, plus țara sau coridorul vostru.</li>
    <li><b>Citești întâi rezumatul și metoda</b>, apoi decizi dacă merită tot articolul.</li>
    <li><b>Notezi fiecare lucrare pe un rând:</b> întrebarea, datele, metoda, rezultatul și ce luați de acolo.
    Asta e matricea literaturii, din care scrieți partea de cadru a raportului.</li>
  </ol>
  <p>Unelte: {unelte}.</p>
</div>
</main>
<script type="module" src="../js/antet.js?v=57"></script>
</body>
</html>
"""


if __name__ == "__main__":
    d = RAD / "lecturi"
    d.mkdir(exist_ok=True)
    (d / "index.html").write_text(pagina(), encoding="utf-8")
    print("scris lecturi/index.html")
