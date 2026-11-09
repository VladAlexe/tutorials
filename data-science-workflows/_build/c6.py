# -*- coding: utf-8 -*-
"""
Lecția 6: Analiza exploratorie.

Urmează caietul 06_analiza_exploratorie (9 noiembrie 2026), organizat pe cinci
întrebări generale ale unei analize exploratorii, aplicate datelor SCI:
1. ce conțin datele (numărul de rânduri, o sursă externă, extremele, lipsurile);
2. cum arată o valoare obișnuită (distribuția, scara logaritmică);
3. ce variază împreună (H1 distanța, H2 granița, H3 economia, H4 migrația);
4. ce iese din tipar (SCI raportat la mediana perechilor de la aceeași distanță);
5. ce grupuri apar (comunitățile rețelei).
Aceleași cinci întrebări formează fișa EDA a echipei, pe datele proprii.

Numerele vin din date/c6-ipoteze.json, calculat din tabelele produse de
caietele 04-06 și din contururile GISCO NUTS 2024 (20M, EPSG:3035), ca în caiet.
Hărțile folosesc date/explorator.json (aceleași SCI, aceleași 16 comunități,
variabilele lipsă din regiuni_nuts2).

Rulare:  python _build/c6.py
"""

import json

from literatura import lecturi
from comun import Lectie, ix, verif, tabel, nota, surse, RAD

L = Lectie(6, "c6-analiza-exploratorie", "Analiza exploratorie",
           "Cinci întrebări ale analizei exploratorii, puse datelor SCI: ce conțin datele, cum arată o valoare "
           "obișnuită, ce variază împreună, ce iese din tipar și ce grupuri apar.")
sl = L.sl

D = json.loads((RAD / "date" / "c6-ipoteze.json").read_text(encoding="utf-8"))
nr = lambda v: f"{v:,}".replace(",", ".")
ro = lambda x, z=2: f"{x:.{z}f}".replace(".", ",").replace("-", "−")
_NB6 = "06_analiza_exploratorie.ipynb"
H1, H2, H3, H4 = D["h1"], D["h2"], D["h3"], D["h4"]
Q = ["1. Ce conțin datele", "2. Valoarea obișnuită", "3. Ce variază împreună", "4. Ce iese din tipar",
     "5. Ce grupuri apar"]


# ===========================================================================
#  1-3. Cursul și analiza exploratorie
# ===========================================================================

CURSUL = tabel(["", "Conținutul", "Rezultatul"], [
    ["C1", "proiectul, mediul de lucru, tipurile de date și JSON", "<code>dsw/</code>, cu <code>.venv</code>"],
    ["C2", "colectarea datelor prin API: Eurostat, Banca Mondială", "<code>data/raw</code>"],
    ["C3", "surse diverse, preprocesare, Git și depozitul echipei", "<code>data/processed</code>, <code>proiect/</code>"],
    ["C4", "curățarea datelor și tabelul regiunilor", "<code>regiuni_nuts2.csv</code>"],
    ["C5", "integrare, baze de date și agregare", "perechile, în <code>dsw.db</code>"],
    ["<b>C6</b>", "<b>azi: analiza exploratorie</b>", "<b>deciziile pentru model</b>"],
    ["C7", "variabile derivate și model", "modelul SCI"],
    ["C8", "raportul și prezentarea proiectului", "raportul echipei"],
])

sl("s1", "Cursul", "Unde suntem",
   "<h2>Unde suntem în curs</h2>"
   "<p class=\"cheie\">Perechile sunt în baza de date. Înainte de model: ce arată datele și ce merită verificat.</p>"
   + CURSUL,
   manual=
   "<h2>Analiza exploratorie</h2>"
   "<p>Datele sunt curate (C4) și în baza de date (C5). Înainte de orice model, analiza exploratorie răspunde la "
   "cinci întrebări: ce conțin datele, cum arată o valoare obișnuită, ce variază împreună, ce iese din tipar și ce "
   "grupuri apar. Lecția le pune pe datele SCI; fișa echipei le pune pe datele proiectului.</p>"
   + CURSUL
   + nota("Caietul lecției", f"<code>{_NB6}</code>, în <code>dsw/curs/</code>. Pachete noi: <code>geopandas</code>, "
                             "<code>networkx</code>, <code>scipy</code>, toate în <code>requirements.txt</code>.", True))


CICLU = (
    '<div class="ed6">'
    '<div><small>1 · întrebarea</small><b>Legăturile scad cu distanța?</b></div>'
    '<div><small>2 · graficul</small><b>SCI median, pe intervale de distanță</b></div>'
    '<div><small>3 · surpriza</small><b>Nord-Vest și Spania, la 2.000 km: mult peste mediană</b></div>'
    '<div class="nou"><small>4 · întrebarea nouă</small><b>Ce explică abaterea? Migrația?</b></div>'
    '</div>'
    '<p class="ed6__inapoi">întrebarea nouă reia ciclul</p>'
    '<div class="ed6o">'
    '<div><b>Ipoteze</b><span>ce intră în modelul din C7</span></div>'
    '<div><b>Decizii</b><span>scara, ce perechi intră, ce se exclude</span></div>'
    '<div><b>Excepții</b><span>cazurile de explicat după model</span></div>'
    '</div>')

sl("s2", "Analiza exploratorie", "Un ciclu, nu o listă",
   "<h2>Analiza exploratorie: un ciclu</h2>"
   "<p class=\"cheie\">Analiza exploratorie nu confirmă o teorie: caută ce merită verificat. Fiecare grafic răspunde "
   "la o întrebare și ridică, de obicei, una nouă.</p>"
   + CICLU,
   manual=
   "<h2>Analiza exploratorie: un ciclu</h2>"
   "<p>Tukey (1977), care a dat numele metodei, o descrie ca pe o muncă de detectiv: se caută indicii înainte de "
   "a se judeca un caz. Wickham și colegii (R for Data Science, 2023) o descriu ca pe un ciclu: o întrebare, un "
   "grafic sau un tabel care îi răspunde, apoi întrebarea nouă pe care o ridică răspunsul. Nu există o listă "
   "completă de grafice de făcut; există întrebări bune.</p>"
   + CICLU
   + "<p>Analiza se termină cu trei rezultate: ipotezele care intră în model, deciziile despre date (scara, ce se "
     "exclude, ce lipsește) și excepțiile care trebuie explicate. Fără ele, analiza exploratorie rămâne o colecție "
     "de grafice.</p>"
   + nota("Exploratoriu și confirmatoriu",
          "Aceleași date nu pot și genera o ipoteză, și o confirma. Ce se găsește aici rămâne de verificat: în model, "
          "pe alte date sau în literatură.", True))


INTREBARI = [
    ("Ce conțin datele?", "numărul de rânduri, cheile, lipsurile, valorile imposibile, o comparație cu o sursă externă",
     "shape · isna().sum() · nunique()"),
    ("Cum arată o valoare obișnuită?", "distribuția fiecărei variabile, coada, extremele, scara potrivită",
     "describe() · hist() · nlargest()"),
    ("Ce variază împreună?", "relația cu variabila de interes, pe grupuri comparabile",
     "pd.cut · groupby · corr(method=\"spearman\")"),
    ("Ce iese din tipar?", "cazurile mult peste sau sub ce ar fi de așteptat",
     "valoarea / mediana grupului"),
    ("Ce grupuri apar?", "structura: regiuni, comunități, tipuri de cazuri",
     "hartă · rețea · louvain_communities"),
]
CINCI = ('<div class="q6">' + "".join(
    f'<div><i>{k}</i><b>{q}</b><span>{c}</span><code>{u}</code></div>'
    for k, (q, c, u) in enumerate(INTREBARI, 1)) + "</div>")

sl("s3", "Analiza exploratorie", "Cinci întrebări",
   "<h2>Cinci întrebări, pe orice date</h2>"
   + CINCI
   + "<p class=\"cub__regula\">Azi, pe perechile SCI. În proiect, aceleași întrebări, pe datele echipei.</p>",
   manual=
   "<h2>Cinci întrebări, pe orice date</h2>"
   "<p>Listele de verificare ale analizei exploratorii (Peng, Exploratory Data Analysis with R; Riley, Good Data "
   "Analysis, Google) se pot strânge în cinci întrebări. Primele două privesc o variabilă, a treia perechi de "
   "variabile, ultimele două cazurile și grupurile.</p>"
   + CINCI
   + tabel(["Pasul", "De ce"], [
       ["numărul de rânduri, verificat cu o socoteală", "un join greșit sau un filtru uitat se vede întâi aici"],
       ["un total comparat cu o sursă externă", "unitatea sau anul greșit se văd la ordinul de mărime"],
       ["primele și ultimele valori", "extremele sunt adesea erori sau cazuri speciale"],
       ["lipsurile, pe grupuri", "dacă lipsesc la întâmplare sau pe țări întregi"],
       ["comparații în grupuri comparabile", "altfel o variabilă ascunsă produce diferența"],
       ["cea mai simplă explicație, întâi", "o diferență mare poate veni din construcția indicatorului"],
   ]))


# ===========================================================================
#  4-5. Ce conțin datele
# ===========================================================================

_SUS, _JOS = D["extreme"]["sus"][0], D["extreme"]["jos"][0]
VERIF_DATE = (
    '<div class="ck6">'
    '<div><i class="da">✓</i><b>Numărul de perechi</b>'
    '<span>298 de regiuni, fiecare cu toate celelalte, o singură dată: 298 × 297 / 2</span>'
    f'<code>{nr(D["n"])}</code></div>'
    '<div><i class="da">✓</i><b>O sursă externă</b>'
    '<span>populația României, adunată pe cele 8 regiuni, are ordinul de mărime cunoscut</span>'
    f'<code>{ro(D["ro_pop"] / 1e6)} mil.</code></div>'
    '<div><i class="nu">✗</i><b>Extremele</b>'
    f'<span>cea mai legată pereche ({_SUS[1]} și {_SUS[3]}, {nr(_SUS[4])}) și cea mai puțin legată '
    f'({_JOS[1]} și {_JOS[3]}, {_JOS[4]}) au aceeași regiune: Svalbard</span>'
    '<code>populația: 0</code></div>'
    '</div>')

sl("s4", Q[0], "Verificări înainte de grafice",
   "<h2>Ce conțin datele: trei verificări</h2>"
   + VERIF_DATE
   + "<p class=\"cub__regula\">Svalbard are câteva mii de locuitori, iar SCI este împărțit la numărul de utilizatori. "
     "O regiune aproape goală dă rapoarte extreme, în ambele sensuri: <b>decizie</b>, se exclude din model.</p>",
   manual=
   "<h2>Ce conțin datele: trei verificări</h2>"
   "<p>Înainte de primul grafic, trei verificări care nu cer nicio ipoteză. Numărul de rânduri se compară cu o "
   "socoteală făcută dinainte; un total se compară cu o sursă externă; primele și ultimele valori se citesc una "
   "câte una.</p>"
   + VERIF_DATE
   + tabel(["Cele mai legate", "SCI", "Cele mai puțin legate", "SCI"],
           [[f"{a[1]} · {a[3]}", nr(a[4]), f"{b[1]} · {b[3]}", nr(b[4])]
            for a, b in zip(D["extreme"]["sus"], D["extreme"]["jos"])])
   + f"<p>Svalbard apare în {sum('NO0B' in (p[0], p[2]) for p in D['extreme']['sus'] + D['extreme']['jos'])} din aceste șase perechi. Tabelul regiunilor îi dă populația 0: locuitorii sunt "
     "numărați în altă parte. Este un caz de manual pentru extreme: nu sunt descoperiri, ci o consecință a felului în "
     "care se construiește indicatorul.</p>"
   + "<pre><code>len(perechi), 298 * 297 // 2\n"
     "regiuni[regiuni[\"tara\"] == \"RO\"][\"populatie\"].sum()\n"
     "perechi.nlargest(3, \"sci\")\n"
     "perechi.nsmallest(3, \"sci\")</code></pre>")


HARTA_LIPS = {
    "niveluri": ["regiuni"], "nivel": "regiuni", "masura": "lips", "ales": "DE21", "masuri": ["lips"],
    "faraLinii": True,
    "povesti": [
        {"t": "Germania și Franța", "nivel": "regiuni", "masura": "lips", "ales": "DE21",
         "text": f"Rețelele sociale lipsesc în toate cele {D['lips_rs']['DE']} de regiuni ale Germaniei, la fel în "
                 f"Franța ({D['lips_rs']['FR']}), Turcia ({D['lips_rs']['TR']}) și Grecia ({D['lips_rs']['EL']}). "
                 "O variabilă cu astfel de lipsuri scoate din analiză țări întregi."},
        {"t": "Elveția și Norvegia", "nivel": "regiuni", "masura": "lips", "ales": "CH01",
         "text": "PIB-ul pe locuitor lipsește în toate regiunile Elveției și ale Norvegiei, deci H3 se calculează fără "
                 "ele: două țări bogate lipsesc din comparația economică."},
        {"t": "Balcanii de vest", "nivel": "regiuni", "masura": "lips", "ales": "AL01",
         "text": "Albania, Bosnia și Herțegovina, Kosovo: aproape toate variabilele lipsesc. Pentru SCI sunt în date, "
                 "pentru restul indicatorilor, nu."},
    ]}

sl("s5", Q[0], "Ce lipsește și unde",
   "<h2>Ce lipsește și unde</h2>"
   + ix("harta", "Variabilele lipsă, pe regiuni", HARTA_LIPS),
   manual=
   "<h2>Ce lipsește și unde</h2>"
   f"<p>Numărul de valori lipsă spune puțin; contează unde sunt. Din cele 298 de regiuni, rețelele sociale lipsesc "
   f"la {D['lips']['retele_sociale']}, PIB-ul pe locuitor la {D['lips']['pib_locuitor']}. Pe hartă se vede că "
   "lipsurile nu sunt la întâmplare: vin pe țări întregi.</p>"
   + ix("harta", "Variabilele lipsă, pe regiuni", HARTA_LIPS)
   + "<p>Consecința pentru analiză: o comparație care folosește PIB-ul pierde Elveția și Norvegia, una care folosește "
     "rețelele sociale pierde Germania și Franța. Câte perechi rămân se spune de fiecare dată.</p>"
   + "<pre><code>regiuni.isna().sum()\n"
     "regiuni[regiuni[\"retele_sociale\"].isna()][\"tara\"].value_counts()</code></pre>")


# ===========================================================================
#  6. Valoarea obișnuită
# ===========================================================================

HISTO = {
    "valori": D["esantion"], "bare": 28,
    "etLin": "scara originală", "etLog": "scara log10",
    "axaX": "SCI", "axaY": "perechi",
    "txtLin": f"Aproape toate perechile stau în prima bară. Media este {nr(D['medie'])}, mediana doar "
              f"{nr(D['mediana'])}: câteva perechi foarte legate (maximul: {nr(D['max'])}) trag media în sus.",
    "txtLog": "Pe scara logaritmică (3 = 1.000, 4 = 10.000) distribuția se vede. De aici înainte, SCI se citește pe "
              "această scară.",
}

sl("s6", Q[1], "Coada lungă",
   "<h2>Cum arată o pereche obișnuită</h2>"
   + ix("histo", "SCI pe perechi de regiuni", HISTO),
   manual=
   "<h2>Cum arată o pereche obișnuită</h2>"
   f"<p>Distribuția celor {nr(D['n'])} de perechi. Histograma de aici desenează "
   f"{nr(len(D['esantion']))} de perechi alese la întâmplare; statisticile sunt calculate pe toate. Media "
   f"({nr(D['medie'])}) este de opt ori mediana ({nr(D['mediana'])}): o coadă lungă, trasă de câteva perechi "
   "foarte legate. <b>Decizie</b>: SCI se citește pe scara logaritmică, iar comparațiile folosesc mediana.</p>"
   + ix("histo", "SCI pe perechi de regiuni", HISTO)
   + "<pre><code>perechi[\"sci\"].describe()\n"
     "np.log10(perechi[\"sci\"]).hist(bins=40)</code></pre>")


# ===========================================================================
#  7-10. Ce variază împreună
# ===========================================================================

IPOTEZE = tabel(["Ipoteza", "Ce ar trebui să se vadă", "Cum se verifică"], [
    ["<b>H1</b> Distanța", "SCI scade cu distanța", "mediane pe intervale de distanță, Spearman"],
    ["<b>H2</b> Granița", "la aceeași distanță, regiunile din aceeași țară sunt mai legate", "aceeași țară față de țări diferite, pe intervale"],
    ["<b>H3</b> Economia", "regiunile asemănătoare economic sunt mai legate", "decalajul de PIB și SCI"],
    ["<b>H4</b> Migrația", "țările cu mulți migranți între ele sunt mai legate", "migranții, ca număr și ca rată"],
])
V2 = verif("c6-v2", 1,
           f"Corelația Spearman dintre distanță și SCI este {ro(H1['rho'])}. Ce se poate spune?",
           ["Distanța reduce legăturile cu 46%", "Perechile mai îndepărtate tind să fie mai puțin legate",
            "46% din SCI vine din distanță", "Relația este liniară"],
           "Spearman arată că ordinea celor două variabile merge împreună, invers. Nu este un procent și nu spune "
           "ce produce relația: distanța poate fi și ea un înlocuitor pentru graniță, limbă sau istorie.")
_SC = H1["med"][0] / H1["med"][-1]
TREPTE_H1 = {
    "titlu": "SCI median pe intervale de distanță",
    "intervale": H1["intervale"],
    "serii": [{"t": "toate perechile", "c": "accent", "med": H1["med"], "n": H1["n"]}],
    "axaX": "distanța dintre centrele regiunilor, km", "axaY": "SCI median (scară logaritmică)",
    "text": f"<b>ρ Spearman = {ro(H1['rho'])}</b>, pe {nr(D['n'])} de perechi. De la regiunile vecine (0-100 km) la "
            f"cele aflate la peste 2.000 km, mediana scade de aproximativ {round(_SC, -1):.0f} de ori.",
}

sl("s7", Q[2], "H1: distanța",
   "<h2>H1: legăturile scad cu distanța</h2>"
   + ix("trepte", "SCI median, pe intervale de distanță", TREPTE_H1),
   manual=
   "<h2>Ce variază împreună: patru ipoteze</h2>"
   "<p>A treia întrebare are nevoie de ipoteze, altfel orice pereche de variabile ar fi de comparat. Bailey și "
   "colegii (2020) găsesc pentru Europa efecte puternice ale distanței și ale granițelor; Bailey și colegii (2018) "
   "arată că SCI este asociat cu migrația. De aici, patru așteptări, scrise înainte de date.</p>"
   + IPOTEZE
   + "<h3>H1: legăturile scad cu distanța</h3>"
   "<p>Distanța dintre două regiuni se ia între centrele lor, pe harta în proiecția europeană EPSG:3035, care măsoară "
   "în metri. <code>pd.cut</code> pune fiecare distanță în intervalul ei; apoi se agregă, ca în C5. Spearman compară "
   "ordinea valorilor, între -1 și 1, și nu este tras de câteva valori uriașe.</p>"
   + ix("trepte", "SCI median, pe intervale de distanță", TREPTE_H1)
   + "<pre><code>praguri = [0, 100, 250, 500, 1000, 2000, 10000]\n"
     "perechi[\"interval_km\"] = pd.cut(perechi[\"distanta_km\"], praguri)\n"
     "perechi.groupby(\"interval_km\", observed=True)[\"sci\"].agg([\"size\", \"median\"])</code></pre>"
   + lecturi(["bailey2018", "bailey2020"], "Literatura ipotezelor"),
   dupa=V2)

_I = H2["intervale"].index("250-500")
_R = H2["da"]["med"][_I] / H2["nu"]["med"][_I]
TREPTE_H2 = {
    "titlu": "SCI median, aceeași țară și țări diferite",
    "intervale": H2["intervale"], "raport": True,
    "serii": [{"t": "aceeași țară", "c": "accent", "med": H2["da"]["med"], "n": H2["da"]["n"]},
              {"t": "țări diferite", "c": "text-3", "med": H2["nu"]["med"], "n": H2["nu"]["n"]}],
    "axaX": "distanța dintre centrele regiunilor, km", "axaY": "SCI median (scară logaritmică)",
    "text": f"La 250-500 km, perechile din aceeași țară au mediana de {_R:.0f} ori mai mare. Diferența rămâne la toate distanțele.",
}
V3 = verif("c6-v3", 1,
           "De ce se compară aceeași țară cu țări diferite pe intervale de distanță, nu pe toate perechile deodată?",
           ["Ca să fie mai puține perechi", "Perechile interne sunt și mai apropiate",
            "SCI nu are sens peste 2.000 km", "Așa cere pd.cut"],
           "În C5, SCI-ul mediu era de 43 de ori mai mare în aceeași țară, dar perechile interne sunt și mai apropiate. "
           "Comparația în același interval scoate distanța din diferență. Limba și istoria rămân însă amestecate.")

sl("s8", Q[2], "H2: granița",
   "<h2>H2: granița, la aceeași distanță</h2>"
   + ix("trepte", "Aceeași țară, țări diferite", TREPTE_H2),
   manual=
   "<h2>H2: granița, la aceeași distanță</h2>"
   "<p>În C5, SCI-ul mediu era mult mai mare în aceeași țară. Dar perechile interne sunt și mai apropiate, deci "
   "comparația amesteca granița cu distanța. Comparația în grupuri comparabile, pe același interval de distanță, "
   "scoate distanța din diferență.</p>"
   + ix("trepte", "Aceeași țară, țări diferite", TREPTE_H2)
   + "<p>Nu este încă efectul cauzal al graniței: două regiuni din aceeași țară au și aceeași limbă, aceeași "
     "istorie și aceleași instituții.</p>"
   + "<pre><code>perechi[\"aceeasi_tara\"] = perechi[\"tara_1\"] == perechi[\"tara_2\"]\n"
     "perechi.groupby([\"interval_km\", \"aceeasi_tara\"], observed=True)[\"sci\"].median().unstack()</code></pre>",
   dupa=V3)


E = H3["exemplu"]
_DEC = abs(E["a"][2] - E["b"][2])
_MX = max(E["a"][2], E["b"][2])
ECON = (
    '<div class="h3x">'
    + "".join(f'<div class="h3x__r"><b>{nr(v)}</b><div class="h3x__b" style="height:{round(v / _MX * 150)}px"></div>'
              f'<small>{n}<br><code>{c}</code></small></div>' for c, n, v in [E["a"], E["b"]])
    + f'<div class="h3x__d"><code>|{nr(E["a"][2])} − {nr(E["b"][2])}|</code><b>{nr(_DEC)}</b>'
      '<small>decalajul de PIB pe locuitor</small></div>'
    + "</div>")

sl("s9", Q[2], "H3: economia",
   "<h2>H3: asemănarea economică</h2>"
   "<p class=\"cheie\">Perechea nu are sens (A-B este tot una cu B-A), deci se folosește diferența absolută.</p>"
   + ECON
   + f"<p class=\"cub__regula\">Pe cele {nr(H3['n'])} de perechi cu PIB la ambele capete: <b>ρ = {ro(H3['rho'])}</b>. Semnul este opus "
     "așteptării: decalajele mai mari merg cu legături puțin mai puternice. O explicație posibilă este migrația, "
     "din regiunile mai sărace spre cele mai bogate.</p>",
   manual=
   "<h2>H3: asemănarea economică</h2>"
   "<p>Perechea nu are sens, deci variabila este diferența absolută de PIB pe locuitor. Analiza folosește doar "
   "perechile care au PIB la ambele capete și spune câte sunt: fără Elveția și Norvegia (slide-ul cu lipsurile).</p>"
   + ECON
   + f"<p>Pe cele {nr(H3['n'])} de perechi cu PIB la ambele capete, din {nr(D['n'])}: <b>ρ = {ro(H3['rho'])}</b>. "
     "Bailey și colegii (2020) găsesc tot că decalajele mai mari pot merge cu legături mai puternice; migrația este "
     "o explicație posibilă, ceea ce duce la H4.</p>"
   + "<pre><code>economice = perechi.dropna(subset=[\"pib_locuitor_1\", \"pib_locuitor_2\"])\n"
     "decalaj = (economice[\"pib_locuitor_1\"] - economice[\"pib_locuitor_2\"]).abs()\n"
     "decalaj.corr(economice[\"sci\"], method=\"spearman\")</code></pre>")


NOR = {
    "variabile": [
        {"k": "nr", "et": "migranți, număr", "rho": H4["rho_nr"],
         "text": "Un milion de migranți înseamnă mult pentru Austria și puțin pentru Germania."},
        {"k": "rata", "et": "migranți la 1.000 de locuitori", "rho": H4["rho_rata"],
         "text": "Raportată la populația celor două țări, corelația aproape se dublează: SCI este și el o măsură relativă."}],
    "puncte": [{"t": t, "x": {"nr": m, "rata": r}, "y": s, "g": bool(g)} for t, s, m, r, g in H4["puncte"]],
    "etY": "SCI (scară logaritmică)", "etG": "perechile României", "etN": "celelalte perechi",
}

sl("s10", Q[2], "H4: migrația",
   "<h2>H4: migranți, ca număr sau ca rată</h2>"
   + ix("nor", "Migrația și SCI, pe perechi de țări", NOR),
   manual=
   "<h2>H4: migranți, ca număr sau ca rată</h2>"
   f"<p>Perechile de țări cu migrația cunoscută în ambele sensuri: {H4['n']}. Corelația cu numărul de migranți este "
   f"pozitivă, dar nu foarte mare ({ro(H4['rho_nr'])}). SCI este însă relativ: împărțit la numărul de utilizatori din "
   "cele două țări. Comparabilă cu el este o rată: migranți la 1.000 de locuitori ai celor două țări, cu populația "
   "de la Banca Mondială, din C2. <b>Decizie</b>: în model intră rata, nu numărul.</p>"
   + ix("nor", "Migrația și SCI, pe perechi de țări", NOR)
   + f"<p>Zborurile, exercițiul din caiet: pe {H4['zboruri']['n']} de perechi cu pasageri, ρ = "
     f"{ro(H4['zboruri']['rho'])}, mult sub migrație. Numărul de pasageri depinde mai ales de mărimea țărilor.</p>")


# ===========================================================================
#  11-12. Ce iese din tipar
# ===========================================================================

HARTA_AB = {
    "niveluri": ["regiuni"], "nivel": "regiuni", "masura": "dist", "ales": "RO11", "masuri": ["dist", "sci"],
    "povesti": [
        {"t": "Nord-Vest", "nivel": "regiuni", "masura": "dist", "ales": "RO11",
         "text": "La peste 2.000 km, regiuni din Spania (La Rioja, Castilla-La Mancha, Aragón) și Irlanda au legături de "
                 "zeci de ori peste mediana distanței lor: drumurile migrației de muncă."},
        {"t": "Luxemburg", "nivel": "regiuni", "masura": "dist", "ales": "LU00",
         "text": "Toate regiunile Portugaliei, de peste 50 de ori peste mediana distanței; vecinii din Belgia și Țările "
                 "de Jos, sub ea. Una dintre cele mai mari comunități portugheze din afara țării."},
        {"t": "Varșovia", "nivel": "regiuni", "masura": "dist", "ales": "PL91",
         "text": "Islanda, mult peste mediană: emigrația poloneză de după 2004. Svalbard apare din nou sus, ca la "
                 "verificarea extremelor: o regiune aproape nelocuită."},
    ]}

sl("s11", Q[3], "Harta abaterilor",
   "<h2>Mai legate decât distanța le-ar da</h2>"
   + ix("harta", "SCI raportat la mediana distanței", HARTA_AB),
   manual=
   "<h2>Mai legate decât distanța le-ar da</h2>"
   "<p>După H1, distanța singură explică o mare parte din SCI. Pentru a vedea ce iese din tipar, fiecare pereche "
   "se compară cu perechile aflate la aceeași distanță: SCI-ul ei împărțit la mediana intervalului ei. Peste 1 "
   "înseamnă mai legată decât distanța ar sugera; sub 1, mai puțin. Este o primă formă a reziduului din modelul C7.</p>"
   + ix("harta", "SCI raportat la mediana distanței", HARTA_AB)
   + "<pre><code>mediana_intervalului = perechi.groupby(\"interval_km\", observed=True)[\"sci\"].transform(\"median\")\n"
     "perechi[\"fata_de_distanta\"] = perechi[\"sci\"] / mediana_intervalului</code></pre>"
   + "<p>Pe hartă, distanța se măsoară între centrele contururilor desenate, deci valorile diferă puțin de cele din "
     "caiet. Tiparul este același.</p>")


RO = D["ro"]
_NUME = {"AT": "Austria", "DE": "Germania", "HU": "Ungaria", "IE": "Irlanda", "IT": "Italia", "BE": "Belgia",
         "ES": "Spania", "LU": "Luxemburg"}
DUBLU = {"randuri": [{"t": _NUME.get(c, c), "sci": s, "rata": r, "ev": c in ("IT", "HU")} for c, s, m, r, p in RO]}
V_RO = verif("c6-v-ro", 1,
             "Ungaria are un SCI mare cu România, dar puțini migranți la mie. Care explicație este cea mai plauzibilă?",
             ["O eroare în date", "Minoritatea maghiară: legături vechi, fără migrație", "Turismul", "Distanța"],
             "O parte din legături vin din minoritatea maghiară din România, nu din migrație. La cursul 7, distanța și "
             "migrația intră în același model, iar ce rămâne neexplicat arată astfel de cazuri.")

sl("s12", Q[3], "Ghicitoarea din C1",
   "<h2>Ghicitoarea din C1: partenerii României</h2>"
   + ix("dublu", "SCI și migranții la mie", DUBLU)
   + "<p class=\"cub__regula\">Italia are cea mai mare rată de migranți, dar Austria, Germania, Ungaria și Irlanda "
     "au SCI mai mare. Migrația explică mult, dar nu tot.</p>",
   manual=
   "<h2>Ghicitoarea din C1: partenerii României</h2>"
   "<p>La C1, Italia, țara cu cei mai mulți români, era abia pe locul cinci după SCI. Cu migrația raportată la "
   "populație, ghicitoarea se lămurește doar în parte.</p>"
   + ix("dublu", "SCI și migranții la mie", DUBLU)
   + tabel(["Țara", "SCI", "migranți", "la mie", "pasageri"],
           [[_NUME.get(c, c), nr(s), nr(m), ro(r, 1), nr(p)] for c, s, m, r, p in RO]),
   dupa=V_RO)


# ===========================================================================
#  13. Ce grupuri apar
# ===========================================================================

HARTA_COM = {
    "niveluri": ["regiuni"], "nivel": "regiuni", "masura": "com", "ales": "RO11", "masuri": ["com", "sci"],
    "povesti": [
        {"t": "România și Germania", "nivel": "regiuni", "masura": "com", "ales": "RO11",
         "text": "Toate regiunile României sunt în aceeași comunitate cu Germania, nu cu țările vecine: o urmă a "
                 "migrației de muncă."},
        {"t": "Polonia și Irlanda", "nivel": "regiuni", "masura": "com", "ales": "PL91",
         "text": "Polonia, Irlanda, Islanda și Lituania formează o singură comunitate, urmă a emigrației de după 2004."},
        {"t": "Luxemburg și Portugalia", "nivel": "regiuni", "masura": "com", "ales": "LU00",
         "text": "Luxemburgul și regiunile Portugaliei, împreună: aceeași excepție ca pe harta abaterilor."},
    ]}

sl("s13", Q[4], "Comunitățile",
   "<h2>Ce grupuri apar: comunitățile rețelei</h2>"
   + ix("harta", "Comunitățile SCI, pe regiuni", HARTA_COM),
   manual=
   "<h2>Ce grupuri apar: comunitățile rețelei</h2>"
   "<p>Aceleași perechi, privite împreună: fiecare regiune este un nod, fiecare pereche o legătură, iar SCI-ul este "
   "ponderea ei. O comunitate este un grup de regiuni mai legate între ele decât cu restul. Algoritmul Louvain le "
   f"caută doar din ponderi: nu știe nimic despre țări sau hartă. Cu <code>seed=1</code>, rezultatul este același la "
   f"fiecare rulare: {D['comunitati']} comunități.</p>"
   + ix("harta", "Comunitățile SCI, pe regiuni", HARTA_COM)
   + "<p>Culorile sunt doar etichete. Cele mai multe comunități urmează granițele; informative sunt excepțiile, care "
     "trec de o graniță, iar ele sunt aceleași ca pe harta abaterilor. Gruparea singură nu spune de ce (migrație, "
     "limbă, istorie): pentru asta trebuie alte date.</p>"
   + "<pre><code>G = nx.from_pandas_edgelist(perechi, \"regiune_1\", \"regiune_2\", edge_attr=\"sci\")\n"
     "grupuri = nx.community.louvain_communities(G, weight=\"sci\", seed=1)</code></pre>")


# ===========================================================================
#  14-16. Echipa și mai departe
# ===========================================================================

DOVADA = {
    "id": "c6-dovada",
    "sarcina": "Trei rezultate din caiet, rulate pe datele proprii. Ieșirea fiecăruia se lipește în câmpul lui.",
    "indiciu": "Celulele se rulează în caietul 06, în ordine: datele din bază (1), distanța (3.1), economia (3.3), migrația (3.4).",
    "pasi": [
        {"t": "H1: distanța",
         "cmd": "perechi[\"distanta_km\"].corr(perechi[\"sci\"], method=\"spearman\")",
         "gol": "numărul afișat",
         "cauta": r"-0[.,]46\d",
         "ind": "Un singur număr, negativ, în jur de -0,46.",
         "daca_nu": "Corelația trebuie să fie în jur de -0.46. Distanța se calculează din centrele regiunilor (secțiunea 3.1)."},
        {"t": "H3: perechile cu PIB",
         "cmd": "len(economice), len(perechi)",
         "gol": "perechea de numere afișată",
         "cauta": r"37950\D+44253",
         "ind": "Două numere: perechile cu PIB la ambele capete și toate perechile.",
         "daca_nu": "Trebuie să iasă 37950 din 44253. Altfel, tabelul perechilor nu este cel din C4."},
        {"t": "H4: migranții la mie",
         "cmd": "cu_migratie[\"la_mie\"].corr(cu_migratie[\"sci\"], method=\"spearman\")",
         "gol": "numărul afișat",
         "cauta": r"0[.,]67\d",
         "ind": "Un număr pozitiv, în jur de 0,68.",
         "daca_nu": "Corelația cu rata trebuie să fie în jur de 0.68. Populația vine din data/raw/bm.csv, anul 2024."},
    ],
    "explicatie": "Rezultatele sunt cele din caiet: H1 și H4 se văd clar, H3 are semnul opus așteptării.",
}

sl("s14", "Echipa", "Verificarea",
   "<h2>Verificarea analizei</h2>"
   + ix("dovada", "Verificarea analizei", DOVADA),
   manual=
   "<h2>Verificarea analizei</h2>"
   "<p>Trei rezultate din caiet, cu ieșirea de pe calculatorul propriu. Butonul <b>Indiciu</b> arată ce trebuie "
   "să conțină fiecare.</p>"
   + ix("dovada", "Verificarea analizei", DOVADA))


FISA = [
    ("Ce conțin datele?", "câte rânduri, câte ar trebui să fie; un total față de o sursă externă; ce lipsește și unde"),
    ("Cum arată o valoare obișnuită?", "distribuția variabilei principale, scara, extremele citite una câte una"),
    ("Ce variază împreună?", "o ipoteză din literatură, verificată în grupuri comparabile, cu numărul de cazuri"),
    ("Ce iese din tipar?", "două cazuri mult peste sau sub așteptare și o explicație posibilă"),
    ("Ce grupuri apar?", "o hartă sau o grupare, cu o excepție care merită explicată"),
]
FISA_HTML = ('<div class="q6 q6--fisa">' + "".join(
    f'<div><i>{k}</i><b>{q}</b><span>{c}</span></div>' for k, (q, c) in enumerate(FISA, 1)) + "</div>")
FORM = {
    "id": "c6-fisa", "tip": "fisa", "minim": 80,
    "sarcina": "Primul EDA pe datele echipei: o constatare pentru fiecare întrebare și o decizie pentru model.",
    "exemplu": "De exemplu: 298 de regiuni, deci 44.253 de perechi; rețelele sociale lipsesc în Germania și Franța; "
               "decizie: Svalbard se exclude, SCI pe scara logaritmică.",
    "multumesc": "Fișa a fost înregistrată."}

sl("s15", "Echipa", "Fișa EDA a echipei",
   "<h2>Fișa EDA a echipei</h2>"
   + FISA_HTML
   + ix("asteptari", "Primul EDA al echipei", FORM),
   manual=
   "<h2>Fișa EDA a echipei</h2>"
   "<p>Aceleași cinci întrebări, pe datele proiectului. Fiecare răspuns are un număr și spune pe câte cazuri a fost "
   "calculat. Fișa intră în <code>README.md</code>, iar caietul care o produce în <code>notebooks/</code>.</p>"
   + FISA_HTML
   + ix("asteptari", "Primul EDA al echipei", FORM))


DECIZII = [
    ("SCI are o coadă lungă", "scara logaritmică și mediana"),
    ("Svalbard: populația 0, extreme în ambele sensuri", "se exclude"),
    ("PIB lipsește în Elveția, Norvegia și Balcanii de vest", f"H3 pe {nr(H3['n'])} de perechi, spus explicit"),
    ("distanța și granița, ambele clare", "două variabile separate"),
    ("migrația contează ca rată", "rata la mie, nu numărul"),
    ("Spania, Irlanda, Portugalia, Ungaria", "excepțiile de urmărit în reziduuri"),
]
FIN_C6 = ('<div class="dc6">'
          + "".join(f'<div><span>{a}</span><b>{b}</b></div>' for a, b in DECIZII)
          + "</div>"
          '<p class="fin3__a"><a class="leg" href="../">Pagina cursului 6</a></p>')

SURSE_C6 = surse("Documentația analizei", [
    ("R for Data Science: Exploratory data analysis", "https://r4ds.hadley.nz/eda.html", "analiza exploratorie ca ciclu: variație, covariație, valori neobișnuite"),
    ("Peng: Exploratory Data Analysis Checklist", "https://bookdown.org/rdpeng/exdata/exploratory-data-analysis-checklist.html", "întrebarea, numărul de rânduri, o sursă externă, extremele"),
    ("Google: Good Data Analysis", "https://developers.google.com/machine-learning/guides/good-data-analysis", "validare, descriere, evaluare; comparații pe grupuri"),
    ("pandas: cut", "https://pandas.pydata.org/docs/reference/api/pandas.cut.html", "împărțirea unei variabile numerice în intervale"),
    ("pandas: corr", "https://pandas.pydata.org/docs/reference/api/pandas.Series.corr.html", "Pearson și Spearman, cu <code>method=</code>"),
    ("networkx: Louvain", "https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.community.louvain.louvain_communities.html", "<code>louvain_communities</code>, <code>weight</code>, <code>seed</code>"),
])

sl("s16", "Mai departe", "Deciziile pentru model",
   "<h2>Ce duce analiza la cursul 7</h2>" + FIN_C6,
   manual="<h2>Ce duce analiza la cursul 7</h2>"
   "<p>Fiecare constatare se încheie cu o decizie pentru modelul din C7: variabilele, scara, ce se exclude și ce "
   "excepții se urmăresc în reziduuri.</p>" + FIN_C6 + SURSE_C6)


if __name__ == "__main__":
    L.scrie_tot()
