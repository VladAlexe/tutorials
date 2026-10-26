"""Pagina „Literatura proiectului": lecturi/index.html.

Aceeași listă ca în lecții (literatura.py), pusă într-o singură pagină, în
ordinea fluxului de lucru: sursa datelor, cadrul teoretic, metodologia și
uneltele de căutare.

Rulare:  python _build/lecturi.py
"""
import pathlib
from literatura import REF, FEL

RAD = pathlib.Path(__file__).resolve().parent.parent
TITLU_LECTIE = {1: "Introducere", 2: "API", 3: "Git și cadrul teoretic", 4: "Curățarea",
                5: "Agregare și baze de date", 6: "Analiza exploratorie", 7: "Variabile și model",
                8: "Raportul"}

PILONI = [
    ("Legăturile", "Ce locuri sunt legate între ele și cât de puternic.", ["bailey2018", "johnston2026"]),
    ("Oamenii", "Rețelele de migranți și câmpurile de migrație: destinațiile celor care întrețin legăturile.",
     ["palloni2001", "dehaas2010", "sandu2005", "sandu2025"]),
    ("Locul", "Factorii care explică legăturile independent de migrație: distanța, granița, limba, istoria.",
     ["bailey2020"]),
]


def a(k):
    return f'<a class="lit__a" href="{REF[k][3]}" target="_blank" rel="noopener">{REF[k][1]}</a>'


V = (RAD / "_build" / "VERSIUNE").read_text().strip() if (RAD / "_build" / "VERSIUNE").exists() else "1"

ROL = {"date": "Sursa datelor", "teorie": "Cadrul teoretic", "metoda": "Metodologia"}


def pagina():
    feluri = "".join(f"<dt>{et}</dt><dd>{ce[0].upper() + ce[1:]}.</dd>" for f, (et, ce) in FEL.items())
    piloni = "".join(
        f'<div class="lp__pil"><h3>{n}</h3><p>{d}</p><p class="lp__pr">{"; ".join(a(k) for k in ks)}</p></div>'
        for n, d, ks in PILONI)
    pe_lectii = "".join(
        f'<tr><th scope="row">C{n}</th><td>{t}</td><td>'
        + "; ".join(a(k) for k, r in REF.items() if n in r[5] and r[0] != "documentatie")
        + "</td></tr>"
        for n, t in TITLU_LECTIE.items()
        if any(n in r[5] and r[0] != "documentatie" for r in REF.values()))
    bib = ""
    for f in ["date", "teorie", "metoda"]:
        li = "".join(
            f'<li id="{k}"><p class="lp__ref">{r[2]} <a class="lp__doi" href="{r[3]}" target="_blank" rel="noopener">'
            f'{r[3].replace("https://", "")}</a></p>'
            f'<p class="lp__rol">{r[4][0].upper() + r[4][1:]}</p>'
            f'<p class="lp__lect">{" · ".join("C" + str(n) for n in r[5])}</p></li>'
            for k, r in REF.items() if r[0] == f)
        bib += f'<h3 class="lp__gr">{ROL[f]}</h3><ol class="lp__bib">{li}</ol>'
    unelte = "".join(
        f'<li><a class="leg" href="{r[3]}" target="_blank" rel="noopener">{r[1]}</a>: {r[4]}</li>'
        for k, r in REF.items() if r[0] == "documentatie")
    return f"""<!DOCTYPE html>
<html lang="ro">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Literatura proiectului · Fluxuri de lucru</title>
<meta name="description" content="Literatura pe care se sprijină proiectul cursului: datele SCI, teoria rețelelor și a sistemelor migratorii, metodele folosite.">
<link rel="stylesheet" href="../css/fonturi.css?v={V}">
<link rel="stylesheet" href="../css/sistem.css?v={V}">
<script src="../js/tema.js?v={V}"></script>
<style>
  .lp{{max-width:780px;margin:0 auto;padding:36px 28px 90px}}
  .lp__inapoi{{display:inline-flex;align-items:center;gap:6px;font-family:var(--sans);font-size:var(--t2);
    color:var(--text-2);text-decoration:none;margin:0 0 30px;padding:5px 12px 5px 9px;border:1px solid var(--linie-2);
    border-radius:999px;background:var(--panza)}}
  .lp__inapoi:hover{{color:var(--text);border-color:var(--text-3)}}
  .lp h1{{margin:0 0 14px}}
  .lp .deck{{margin-bottom:44px}}
  .lp__sec{{display:grid;grid-template-columns:150px minmax(0,1fr);gap:28px;padding:30px 0;border-top:1px solid var(--linie)}}
  .lp__sec > h2{{font-family:var(--sans);font-size:var(--t2);font-weight:600;color:var(--text-3);margin:4px 0 0;line-height:1.4}}
  .lp__sec p,.lp__sec li,.lp__sec dd,.lp__sec td{{font-family:var(--sans);font-size:var(--t3);line-height:1.6;color:var(--text-2)}}
  .lp__q{{font-family:var(--titlu)!important;font-size:var(--t5)!important;line-height:1.45!important;color:var(--text)!important;margin:0 0 22px;max-width:none}}
  .lp__pils{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:22px}}
  .lp__pil h3{{font-family:var(--sans);font-size:var(--t3);font-weight:600;margin:0 0 4px}}
  .lp__pil p{{font-size:var(--t2)!important;margin:0 0 6px}}
  .lp__pr a{{font-size:var(--t2)}}
  .lp__regula{{margin:22px 0 0!important;font-size:var(--t2)!important;padding-left:14px;border-left:2px solid var(--linie-2)}}
  .lp dl{{display:grid;grid-template-columns:120px minmax(0,1fr);gap:8px 18px;margin:0}}
  .lp dt{{font-family:var(--sans);font-size:var(--t3);font-weight:600;color:var(--text)}}
  .lp dd{{margin:0}}
  .lp__gr{{font-family:var(--sans);font-size:var(--t3);font-weight:600;margin:0 0 10px}}
  .lp__gr:not(:first-child){{margin-top:28px}}
  .lp__bib{{list-style:none;margin:0;padding:0;max-width:none}}
  .lp__bib li{{margin:0 0 18px;padding:0}}
  .lp__bib li::before{{content:none!important}}
  .lp__ref{{font-family:var(--serif)!important;font-size:var(--t4)!important;line-height:1.5!important;color:var(--text)!important;
    margin:0;padding-left:2em;text-indent:-2em}}
  .lp__doi{{font-family:var(--sans);font-size:var(--t1);color:var(--text-3);text-decoration:none;word-break:break-all}}
  .lp__doi:hover{{color:var(--text);text-decoration:underline}}
  .lp__rol{{font-size:var(--t2)!important;margin:5px 0 0 2em;line-height:1.55!important}}
  .lp__lect{{font-size:var(--t1)!important;color:var(--text-3)!important;margin:3px 0 0 2em;font-variant-numeric:tabular-nums}}
  .lp table{{width:100%;border-collapse:collapse}}
  .lp th,.lp td{{text-align:left;vertical-align:top;padding:9px 14px 9px 0;border-bottom:1px solid var(--linie);font-family:var(--sans)}}
  .lp th{{font-size:var(--t2);font-weight:600;color:var(--text-3);width:40px}}
  .lp td{{font-size:var(--t2)!important}}
  .lp td:nth-child(2){{width:170px;color:var(--text)}}
  .lp tr:last-child th,.lp tr:last-child td{{border-bottom:0}}
  .lp__pasi{{margin:0;padding-left:1.4em;max-width:none;list-style:decimal!important;counter-reset:none}}
  .lp__pasi li{{display:list-item!important;margin:0 0 8px;padding-left:4px!important}}
  .lp__pasi li::marker{{color:var(--text-3);font-size:var(--t2)}}
  .lp__pasi li::before{{content:none!important}}
  .lp__un{{list-style:none;margin:14px 0 0;padding:0}}
  .lp__un li{{margin:0 0 4px;font-size:var(--t2)!important}}
  .lp__un li::before{{content:none!important}}
  .lit__a{{color:var(--text);text-decoration:underline;text-decoration-color:var(--linie-2);text-underline-offset:3px}}
  .lit__a:hover{{text-decoration-color:var(--text)}}
  @media(max-width:720px){{.lp{{padding:24px 16px 60px}}.lp__sec{{grid-template-columns:1fr;gap:12px}}
    .lp__pils{{grid-template-columns:1fr}}.lp dl{{grid-template-columns:1fr;gap:2px}}.lp dd{{margin-bottom:8px}}}}
</style>
</head>
<body>
<div id="antet" data-aici="Literatura proiectului"></div>
<main>
<div class="lp">
  <a class="lp__inapoi" href="../" id="inapoi">← Înapoi</a>
  <p class="supratitlu">Proiectul cursului</p>
  <h1>Literatura proiectului</h1>
  <p class="deck">Lucrările pe care se sprijină proiectul: sursa datelor, cadrul teoretic și metodologia.
  Selecția nu acoperă întreaga literatură despre SCI și migrație, ci doar lucrările folosite în caiete
  și în pașii proiectului.</p>

  <section class="lp__sec">
    <h2>Întrebarea de cercetare</h2>
    <div>
      <p class="lp__q">În ce măsură se explică legăturile sociale dintre locuri prin migrația dintre ele
      și ce rămâne neexplicat după distanță și migrație?</p>
      <div class="lp__pils">{piloni}</div>
      <p class="lp__regula">SCI nu este o măsură a migrației, iar un indice din 2026 nu poate explica o migrație
      anterioară. Relația se formulează ca asociere, nu ca relație cauzală (de Haas, 2010).</p>
    </div>
  </section>

  <section class="lp__sec">
    <h2>Tipurile de surse</h2>
    <dl>{feluri}</dl>
  </section>

  <section class="lp__sec">
    <h2>Bibliografie</h2>
    <div>{bib}</div>
  </section>

  <section class="lp__sec">
    <h2>Lecturile, pe lecții</h2>
    <table><tbody>{pe_lectii}</tbody></table>
  </section>

  <section class="lp__sec">
    <h2>Extinderea căutării</h2>
    <div>
      <ol class="lp__pasi">
        <li>Căutarea pornește de la un articol-ancoră, de exemplu Bailey și colegii (2018).</li>
        <li>Căutarea înapoi: din referințele articolului se rețin lucrările relevante pentru întrebarea de cercetare.</li>
        <li>Căutarea înainte: funcția „Citat de” arată lucrările mai noi care citează articolul.</li>
        <li>Căutarea se face în engleză, cu termenii din titluri: <i>social connectedness index</i>,
        <i>migrant networks</i>, <i>migration systems</i>, la care se adaugă țara sau coridorul studiat.</li>
        <li>Se citesc întâi rezumatul și secțiunea de metodă; lectura integrală urmează doar pentru lucrările relevante.</li>
        <li>Fiecare lucrare se notează pe un rând: întrebarea, datele, metoda, rezultatul și elementul preluat în proiect.
        Rândurile formează matricea literaturii, din care se scrie secțiunea de cadru teoretic a raportului.</li>
      </ol>
      <ul class="lp__un">{unelte}</ul>
    </div>
  </section>
</div>
</main>
<div id="subsol"></div>
<script>
  /* înapoi la pagina de unde s-a venit, dacă e din același sit; altfel, la curs */
  (function(){{
    var a = document.getElementById("inapoi");
    try {{
      if (document.referrer && new URL(document.referrer).origin === location.origin && history.length > 1)
        a.addEventListener("click", function(e){{ e.preventDefault(); history.back(); }});
    }} catch (e) {{}}
  }})();
</script>
<script type="module" src="../js/antet.js?v={V}"></script>
<script type="module" src="../js/subsol.js?v={V}"></script>
</body>
</html>
"""


if __name__ == "__main__":
    d = RAD / "lecturi"
    d.mkdir(exist_ok=True)
    (d / "index.html").write_text(pagina(), encoding="utf-8")
    print("scris lecturi/index.html")
