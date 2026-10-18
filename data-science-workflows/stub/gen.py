# -*- coding: utf-8 -*-
import pathlib, html, json

LECTII = [
 (2,"c2-colectarea-prin-api","Colectarea datelor prin API",
  "Ce este un API, cum se citește o documentație, și cum aduci primele date reale în proiect.",
  "https://github.com/VladAlexe/tutorials/blob/main/data-science-workflows/caiete/c2_api.ipynb",
  ["Ce este un API și cum citești o documentație fără să o citești toată",
   "Cereri HTTP: parametri, coduri de răspuns, limite de rată, ce faci când primești 429",
   "API-ul Băncii Mondiale: structura tabulară, paginarea, și de ce rădăcina e un tablou",
   "API-ul Eurostat: JSON-stat, dimensiuni, categorii și indexarea liniară a valorilor",
   "Fișierele SCI de pe HDX: ce descarci, ce nu, și cum salvezi varianta brută"],
  [("API Banca Mondială","https://datahelpdesk.worldbank.org/knowledgebase/articles/898581-api-basic-call-structures","docs"),
   ("API Eurostat","https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access/api-getting-started","docs"),
   ("JSON-stat","https://json-stat.org/format/","spec"),
   ("requests","https://requests.readthedocs.io/","docs")]),

 (3,"c3-versionare-git","Versionare cu Git",
  "De ce versionăm, cum lucrează o echipă pe același proiect, și ce nu se urcă niciodată.",
  None,
  ["De ce versionăm: istoric, reveniri, și lucrul în paralel fără să vă suprascrieți",
   "commit, branch, merge: cele trei operații din care e făcut aproape tot",
   "Depozitul de echipă pe GitHub și fluxul prin pull request",
   "<code>.gitignore</code>: datele, mediul virtual și secretele nu se urcă niciodată",
   "Conflicte: de ce apar, cum arată, și cum se rezolvă fără panică"],
  [("Pro Git (carte, gratuită)","https://git-scm.com/book/ro/v2","carte"),
   ("GitHub Docs","https://docs.github.com/en/get-started","docs"),
   ("gitignore.io","https://www.toptal.com/developers/gitignore","unealtă")]),

 (4,"c4-curatarea-datelor","Curățarea datelor",
  "Lipsuri, duplicate, unități care nu se potrivesc. Etapa cea mai lungă și cea care decide tot.",
  "https://github.com/VladAlexe/tutorials/blob/main/data-science-workflows/caiete/c4_curatare.ipynb",
  ["Tipuri greșite la citire și conversiile care pierd informație în tăcere",
   "Valori lipsă: <code>null</code>, <code>0</code> și textul gol nu înseamnă același lucru",
   "Duplicate, și de ce la date diadice un duplicat poate fi o pereche inversată",
   "Coduri de regiune: NUTS, ISO, FIPS, și nepotrivirile dintre surse",
   "Documentarea deciziilor: orice curățare e o alegere care se scrie în raport"],
  [("pandas: lucrul cu date lipsă","https://pandas.pydata.org/docs/user_guide/missing_data.html","docs"),
   ("Nomenclatorul NUTS","https://ec.europa.eu/eurostat/web/nuts/overview","Eurostat"),
   ("Tidy Data (Wickham)","https://vita.had.co.nz/papers/tidy-data.pdf","articol")]),

 (5,"c5-agregare-si-baze-de-date","Agregare și baze de date",
  "Îmbinarea surselor, unitatea de analiză, și de ce un tabel mare are nevoie de o bază de date.",
  "https://github.com/VladAlexe/tutorials/blob/main/data-science-workflows/caiete/c5_agregare.ipynb",
  ["Unitatea de analiză și cheia de îmbinare: ce decide ce e un rând",
   "Cele două merge-uri ale datelor diadice, unul pentru fiecare capăt al perechii",
   "De la fișiere la o bază de date relațională: tabele, chei, indecși",
   "SELECT, JOIN, GROUP BY pe un tabel pe care nu îl poți citi cu ochiul",
   "Încărcarea tabelului unificat, de unde citește toată echipa"],
  [("SQL, tutorial","https://www.postgresql.org/docs/current/tutorial.html","PostgreSQL"),
   ("DuckDB","https://duckdb.org/docs/","docs"),
   ("pandas merge","https://pandas.pydata.org/docs/user_guide/merging.html","docs")]),

 (6,"c6-analiza-exploratorie","Analiza exploratorie",
  "Privitul datelor înainte de a le modela: distribuții, relații, și grafice care induc în eroare.",
  "https://github.com/VladAlexe/tutorials/blob/main/data-science-workflows/caiete/c6_eda.ipynb",
  ["Distribuții, valori extreme, și când o transformare logaritmică e justificată",
   "Relații între variabile: ce arată o corelație și ce nu arată niciodată",
   "Grafice care induc în eroare, intenționat sau nu",
   "Explorare pe date diadice: matrice, hărți, top-uri, și capcanele lor",
   "Primele tipare din SCI: distanță, graniță, limbă, istorie"],
  [("Fundamentals of Data Visualization","https://clauswilke.com/dataviz/","carte"),
   ("matplotlib","https://matplotlib.org/stable/users/index.html","docs"),
   ("seaborn","https://seaborn.pydata.org/tutorial.html","docs")]),

 (7,"c7-variabile-si-model","Variabile derivate și model",
  "De la descriere la explicație: variabile construite de tine și un model pe care îl poți apăra.",
  "https://github.com/VladAlexe/tutorials/blob/main/data-science-workflows/caiete/c7_model.ipynb",
  ["Rate, ponderi, distanțe și diferențe între capetele perechii",
   "Variabile diadice construite: distanță geografică, graniță comună, limbă comună",
   "Modelul gravitațional, folosit în comerț și migrație, aplicat pe conectivitate",
   "Non-independența observațiilor și ce faci cu erorile standard",
   "Interpretarea coeficienților: ce propoziție ai dreptul să scrii în raport"],
  [("statsmodels","https://www.statsmodels.org/stable/index.html","docs"),
   ("Bailey et al., Social Connectedness","https://www.aeaweb.org/articles?id=10.1257/jep.32.3.259","JEP"),
   ("scikit-learn","https://scikit-learn.org/stable/user_guide.html","docs")]),

 (8,"c8-raportare","Raportare și proiect final",
  "Rezultatul devine util abia când altcineva îl poate citi, reproduce și critica.",
  None,
  ["Structura unui raport reproductibil: întrebare, date, metodă, rezultat, limite",
   "Grafice și tabele pregătite pentru publicare, nu pentru ecranul tău",
   "<code>README.md</code> ca raport: cum se rulează tot, de la zero",
   "Prezentarea proiectului și întrebările la care trebuie să poți răspunde",
   "Criteriile de evaluare, punct cu punct"],
  [("Good Enough Practices","https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1005510","PLOS"),
   ("The Turing Way","https://book.the-turing-way.org/","carte"),
   ("Quarto","https://quarto.org/docs/guide/","docs")]),
]

SABLON = """<!DOCTYPE html>
<html lang="ro">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lecția {nr}. {titlu} — Fluxuri de lucru</title>
<meta name="description" content="{rezumat}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../css/sistem.css?v=39">
<link rel="stylesheet" href="../css/intrare.css?v=39">
<script src="../js/tema.js?v=39"></script>
</head>
<body>

<div id="antet" data-aici="Lecția {nr}" data-lectie="{cheie}"></div>

<main>
<div class="pagina">

  <header class="intrare">
    <div class="intrare__sus">
      <span class="intrare__nr">Lecția {nr}</span>
      <span class="et">în lucru</span>
    </div>
    <h1>{titlu}</h1>
    <p class="deck">{rezumat}</p>

    <div class="intrare__fapte" style="margin-top:28px">
      <span class="btn" style="cursor:default;opacity:.6">Lecția se publică înainte de curs</span>
      {buton_caiet}
    </div>
  </header>

  <div class="doi">
    <div>
      <section class="bloc">
        <div class="bloc__cap"><span class="nr">01</span><h2>Ce va conține</h2></div>
        <p style="color:var(--text-2);font-size:16.5px">Planul lecției. Conținutul interactiv,
        verificările și caietul se adaugă înainte de ședința din semestru.</p>
        <ul class="obiective">
{puncte}
        </ul>
      </section>

      <section class="bloc">
        <div class="bloc__cap"><span class="nr">02</span><h2>Ce adaugi la proiect</h2></div>
        <p>{proiect}</p>
        <p>Lucrăm pe aceleași date tot semestrul: <strong>Social Connectedness Index</strong>,
        cu atribute aduse prin API de la Eurostat și Banca Mondială. Dacă vrei să te uiți
        peste surse din timp, sunt toate adunate în
        <a class="leg" href="../surse-de-date.html">pagina cu sursele de date</a>.</p>
      </section>
    </div>

    <aside class="doi__dr">
      <div class="panou-c">
        <span class="panou__et">Pregătire</span>
        <p style="font-family:var(--sans);font-size:13.5px;line-height:1.5;color:var(--text-2);max-width:none">
        Până atunci, mergi mai departe cu
        <a class="leg" href="../c{prec}-{prec_slug}/">lecția {prec}</a> și ține mediul de
        lucru pregătit.</p>
      </div>
      <div class="panou-c">
        <span class="panou__et">Legături oficiale</span>
        <div class="legaturi">
{legaturi}
        </div>
      </div>
    </aside>
  </div>

  <section class="altele">
    <div class="bloc__cap"><span class="nr">03</span><h2>Celelalte lecții</h2></div>
    <div class="altele__sina" id="altele"></div>
  </section>

</div>
</main>

<div id="subsol"></div>

<script type="module">
import {{ LECTII, RADACINA }} from "../js/curs.js?v=39";
document.getElementById("altele").innerHTML = LECTII.map(l => `
  <a class="mini ${{l.cheie === "{cheie}" ? "aceasta" : ""}}" href="${{RADACINA}}/${{l.cheie}}/">
    <span class="mini__n">${{String(l.nr).padStart(2,"0")}}</span>
    <span class="mini__t">${{l.titlu}}</span>
    <span class="mini__s">${{l.stare === "gata" ? "gata" : "în lucru"}}</span>
  </a>`).join("");
</script>
<script type="module" src="../js/antet.js?v=39"></script>
<script type="module" src="../js/subsol.js?v=39"></script>
</body>
</html>
"""

PROIECT = {2:"Primele date colectate prin API, salvate brut în <code>date/brute/</code>, plus scriptul care le aduce.",
 3:"Depozitul de echipă pe GitHub, cu structura convenită, <code>.gitignore</code> și a doua sursă de date.",
 4:"Dataseturile curățate, în <code>date/curate/</code>, cu un document care spune ce s-a schimbat și de ce.",
 5:"Tabelul unificat, încărcat în baza de date, de unde citesc toți membrii echipei.",
 6:"Analiza exploratorie, cu primele tipare găsite și graficele care le arată.",
 7:"Variabilele derivate, modelul, și interpretarea coeficienților.",
 8:"Raportul final și prezentarea."}

SLUG_PREC = {2:"introducere-si-mediu",3:"colectarea-prin-api",4:"versionare-git",
 5:"curatarea-datelor",6:"agregare-si-baze-de-date",7:"analiza-exploratorie",8:"variabile-si-model"}

iesire = pathlib.Path("out"); iesire.mkdir(exist_ok=True)
for nr, cheie, titlu, rezumat, caiet, puncte, legaturi in LECTII:
    d = iesire / cheie; d.mkdir(exist_ok=True)
    t = SABLON.format(
        nr=nr, cheie=cheie, titlu=titlu, rezumat=rezumat,
        buton_caiet=(f'<a class="btn" href="{caiet}" target="_blank" rel="noopener">Caietul lecției</a>' if caiet else ""),
        puncte="\n".join(f"          <li>{p}</li>" for p in puncte),
        proiect=PROIECT[nr],
        prec=nr-1, prec_slug=SLUG_PREC[nr],
        legaturi="\n".join(
            f'          <a class="legatura" href="{u}" target="_blank" rel="noopener">'
            f'<span class="legatura__t">{n}</span><span class="legatura__g">{g}</span></a>'
            for n,u,g in legaturi))
    (d/"index.html").write_text(t, encoding="utf-8")
    print("scris", cheie, len(t))
