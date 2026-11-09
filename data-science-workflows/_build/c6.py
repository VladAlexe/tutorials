# -*- coding: utf-8 -*-
"""
Lecția 6: Analiza exploratorie.

Urmează caietul 06_analiza_exploratorie (2 noiembrie 2026): patru ipoteze din
literatură (H1 distanța, H2 granița, H3 economia, H4 oamenii care circulă),
distribuția SCI pe scara logaritmică, mediane pe intervale de distanță,
comparația la aceeași distanță, rata migranților în locul numărului, apoi
aceleași perechi ca rețea: forța, partenerii unei regiuni, comunitățile.

Numerele vin din date/c6-ipoteze.json, calculat din tabelele produse de
caietele 04-06 și din contururile GISCO NUTS 2024 (20M, EPSG:3035), ca în caiet.
Hărțile folosesc date/explorator.json (aceleași SCI și aceleași 16 comunități).

Rulare:  python _build/c6.py
"""

import json

from literatura import lecturi
from comun import Lectie, ix, verif, tabel, nota, surse, RAD

L = Lectie(6, "c6-analiza-exploratorie", "Analiza exploratorie",
           "Patru ipoteze verificate exploratoriu pe datele proiectului: distanța, granița, "
           "economia și oamenii care circulă; apoi aceleași perechi, privite ca rețea.")
sl = L.sl

D = json.loads((RAD / "date" / "c6-ipoteze.json").read_text(encoding="utf-8"))
nr = lambda v: f"{v:,}".replace(",", ".")
ro = lambda x, z=2: f"{x:.{z}f}".replace(".", ",").replace("-", "−")
_NB6 = "06_analiza_exploratorie.ipynb"
H1, H2, H3, H4 = D["h1"], D["h2"], D["h3"], D["h4"]


# ===========================================================================
#  1-2. Planul și ipotezele
# ===========================================================================

AGENDA = [
    ("Ipotezele", "azi", "Patru așteptări din literatură, scrise înainte de date."),
    ("O pereche obișnuită", "azi", "Distribuția SCI, media și mediana, scara logaritmică."),
    ("Distanța și granița", "azi", "H1 și H2: mediane pe intervale, comparația la aceeași distanță."),
    ("Economia și oamenii", "azi", "H3 și H4: decalajul de PIB, migrația ca număr și ca rată."),
    ("Rețeaua", "azi", "Forța unei regiuni, partenerii ei, comunitățile."),
]
PLAN = ix("agenda", "Planul lecției", {"static": True, "titlu": "Planul lecției",
          "etape": [{"nume": n, "unde": u, "text": d} for n, u, d in AGENDA]})

sl("s1", "Cursul", "Planul lecției",
   "<h2>Analiza exploratorie</h2>"
   "<p class=\"cheie\">Ce tipare se văd în date și ce explicații merită verificate: întâi așteptarea, "
   "apoi graficul.</p>"
   + PLAN
   + nota("Caietul lecției", f"<code>{_NB6}</code>. Datele vin din baza din C5, <code>data/dsw.db</code>, cu <code>pd.read_sql</code>.", True),
   manual=
   "<h2>Analiza exploratorie</h2>"
   "<p>Datele sunt curate (C4) și în baza de date (C5). Lecția pornește de la ipoteze din literatură, scrie ce "
   "ar trebui să se vadă dacă sunt adevărate și abia apoi se uită la date. În a doua parte, aceleași perechi "
   "sunt privite împreună, ca rețea.</p>"
   + PLAN
   + nota("Caietul lecției", f"<code>{_NB6}</code>, în <code>dsw/curs/</code>. Pachete noi: <code>geopandas</code>, "
                             "<code>networkx</code>, <code>scipy</code>, toate în <code>requirements.txt</code>.", True))


IPOTEZE = (
    '<table class="tabel ip6"><thead><tr><th>Ipoteza</th><th>Ce ar trebui să se vadă</th><th>Cum se verifică</th></tr></thead><tbody>'
    "<tr><td><b>H1</b> Distanța</td><td>SCI scade cu distanța</td><td>mediane pe intervale de distanță, Spearman</td></tr>"
    "<tr><td><b>H2</b> Granița</td><td>la aceeași distanță, două regiuni din aceeași țară sunt mai legate</td><td>aceeași țară față de țări diferite, pe intervale</td></tr>"
    "<tr><td><b>H3</b> Economia</td><td>regiunile asemănătoare economic sunt mai legate</td><td>decalajul de PIB și SCI</td></tr>"
    "<tr><td><b>H4</b> Oamenii care circulă</td><td>țările cu mulți migranți între ele sunt mai legate</td><td>migranții, ca număr și ca rată</td></tr>"
    "</tbody></table>")

sl("s2", "Ipotezele", "Patru ipoteze",
   "<h2>Patru ipoteze, scrise înainte de date</h2>"
   + IPOTEZE
   + nota("Ce înseamnă „verificare” aici",
          "Căutarea unor tipare compatibile sau nu cu așteptarea. Nu se demonstrează cauze.", True),
   manual=
   "<h2>Patru ipoteze, scrise înainte de date</h2>"
   "<p>Bailey și colegii (2020) găsesc pentru Europa efecte puternice ale distanței și ale granițelor; "
   "Bailey și colegii (2018) arată că SCI este asociat cu migrația. Din aceste rezultate vin patru așteptări, "
   "fiecare cu felul în care se verifică.</p>"
   + IPOTEZE
   + nota("Ce înseamnă „verificare” aici",
          "Căutarea unor tipare compatibile sau nu cu așteptarea. Nu se demonstrează cauze: o corelație nu spune "
          "care variabilă o produce pe cealaltă.", True)
   + lecturi(["bailey2018", "bailey2020"], "Literatura ipotezelor"))


# ===========================================================================
#  3-4. O pereche obișnuită
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

sl("s3", "O pereche obișnuită", "Coada lungă",
   "<h2>Cum arată o pereche obișnuită</h2>"
   + ix("histo", "SCI pe perechi de regiuni", HISTO),
   manual=
   "<h2>Cum arată o pereche obișnuită</h2>"
   f"<p>Înainte de orice comparație, distribuția: {nr(D['n'])} de perechi de regiuni NUTS2. Histograma de aici "
   f"desenează {len(D['esantion']):,} de perechi alese la întâmplare; statisticile sunt calculate pe toate.</p>".replace(",", ".")
   + ix("histo", "SCI pe perechi de regiuni", HISTO)
   + "<p>În caiet: <code>perechi[\"sci\"].describe()</code> pentru rezumat, apoi aceeași histogramă pe "
     "<code>np.log10(perechi[\"sci\"])</code>.</p>")


COADA = {
    "id": "c6-prezice-coada", "fisier": "06_analiza_exploratorie.ipynb · 2. O pereche obișnuită",
    "cod": "import pandas as pd\n\n"
           "sci = pd.Series([2, 3, 4, 5, 100])   # o pereche foarte legata\n"
           "print(sci.mean(), sci.median())",
    "intrebare": "Ce afișează?",
    "variante": ["4.0 4.0", "22.8 4.0", "22.8 22.8", "4.0 22.8"],
    "corect": 1,
    "indiciu": "Media este suma valorilor împărțită la 5. Mediana este valoarea din mijloc a șirului sortat.",
    "laBine": "O singură valoare extremă ridică media; mediana rămâne aceeași.",
    "explicatie": f"Media este 22,8, mediana 4. Pe perechile de regiuni, la fel: media {nr(D['medie'])}, mediana "
                  f"{nr(D['mediana'])}. De aceea se raportează mediana."}

sl("s4", "O pereche obișnuită", "Media sau mediana",
   "<h2>Media sau mediana</h2>"
   + ix("prezice", "Media și mediana", COADA))


# ===========================================================================
#  5-7. Distanța și granița
# ===========================================================================

RANG = {
    "id": "c6-prezice-rang", "fisier": "06_analiza_exploratorie.ipynb · 3. H1, distanța",
    "cod": "import pandas as pd\n\n"
           "d = pd.DataFrame({\"distanta\": [100, 500, 1000, 3000],\n"
           "                  \"sci\":      [900, 200, 150, 20]})\n\n"
           "print(d[\"distanta\"].corr(d[\"sci\"], method=\"spearman\"))",
    "intrebare": "Ce afișează?",
    "variante": ["1.0", "-1.0", "0.0", "-0.5"],
    "corect": 1,
    "indiciu": "Spearman ține cont doar de ordinea valorilor. Când distanța crește, cum variază SCI?",
    "laBine": "Ordinea este perfect inversă: -1.",
    "explicatie": "Spearman înlocuiește valorile cu rangurile lor: distanța are rangurile 1, 2, 3, 4, SCI rangurile "
                  "4, 3, 2, 1. Relația este perfect descrescătoare, deci -1, oricât de inegale ar fi diferențele."}
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

sl("s5", "Distanța și granița", "H1: distanța",
   "<h2>H1: legăturile scad cu distanța</h2>"
   + ix("trepte", "SCI median, pe intervale de distanță", TREPTE_H1),
   manual=
   "<h2>H1: legăturile scad cu distanța</h2>"
   "<p>Distanța dintre două regiuni se ia între centrele lor, pe hartă în proiecția europeană EPSG:3035, care "
   "măsoară în metri. Centrul geometric nu este capitala și nici centrul populației, dar ajunge pentru explorare. "
   "<code>pd.cut</code> pune fiecare distanță în intervalul ei; apoi se agregă, ca în C5.</p>"
   + ix("trepte", "SCI median, pe intervale de distanță", TREPTE_H1)
   + "<pre><code>praguri = [0, 100, 250, 500, 1000, 2000, 10000]\n"
     "perechi[\"interval_km\"] = pd.cut(perechi[\"distanta_km\"], praguri)\n"
     "perechi.groupby(\"interval_km\", observed=True)[\"sci\"].agg([\"size\", \"median\"])</code></pre>",
   dupa=V2)


sl("s6", "Distanța și granița", "Spearman",
   "<h2>Spearman: ordinea, nu valorile</h2>"
   + ix("prezice", "Spearman, pe ranguri", RANG),
   manual=
   "<h2>Spearman: ordinea, nu valorile</h2>"
   "<p>Coeficientul Spearman compară ordinea valorilor și este între -1 și 1: negativ înseamnă că, atunci când una "
   "crește, cealaltă tinde să scadă. Nu presupune o relație în linie dreaptă și nu este tras de câteva valori "
   "uriașe, deci se potrivește pentru SCI.</p>"
   + ix("prezice", "Spearman, pe ranguri", RANG))


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

sl("s7", "Distanța și granița", "H2: granița",
   "<h2>H2: granița, la aceeași distanță</h2>"
   + ix("trepte", "Aceeași țară, țări diferite", TREPTE_H2),
   manual=
   "<h2>H2: granița, la aceeași distanță</h2>"
   "<p>În C5, SCI-ul mediu era mult mai mare în aceeași țară. Dar perechile interne sunt și mai apropiate, deci "
   "comparația amesteca granița cu distanța. De aceea se compară în același interval de distanță.</p>"
   + ix("trepte", "Aceeași țară, țări diferite", TREPTE_H2)
   + "<p>Nu este încă efectul cauzal al graniței: două regiuni din aceeași țară au și aceeași limbă, aceeași "
     "istorie și aceleași instituții.</p>"
   + "<pre><code>perechi[\"aceeasi_tara\"] = perechi[\"tara_1\"] == perechi[\"tara_2\"]\n"
     "perechi.groupby([\"interval_km\", \"aceeasi_tara\"], observed=True)[\"sci\"].median().unstack()</code></pre>",
   dupa=V3)


# ===========================================================================
#  8-10. Economia și oamenii
# ===========================================================================

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

sl("s8", "Economia și oamenii", "H3: economia",
   "<h2>H3: asemănarea economică</h2>"
   "<p class=\"cheie\">Perechea nu are sens (A-B este tot una cu B-A), deci se folosește diferența absolută.</p>"
   + ECON
   + f"<p class=\"cub__regula\">Pe cele {nr(H3['n'])} de perechi cu PIB la ambele capete: <b>ρ = {ro(H3['rho'])}</b>. Semnul este opus "
     "așteptării: decalajele mai mari merg cu legături puțin mai puternice. O explicație posibilă este migrația, "
     "din regiunile mai sărace spre cele mai bogate.</p>",
   manual=
   "<h2>H3: asemănarea economică</h2>"
   "<p>Perechea nu are sens, deci variabila este diferența absolută de PIB pe locuitor. Analiza folosește doar "
   "perechile care au PIB la ambele capete și spune câte sunt.</p>"
   + ECON
   + f"<p>Pe cele {nr(H3['n'])} de perechi cu PIB la ambele capete, din {nr(D['n'])}: <b>ρ = {ro(H3['rho'])}</b>. "
     "Bailey și colegii (2020) găsesc tot că decalajele mai mari pot merge cu legături mai puternice; migrația este "
     "o explicație posibilă, ceea ce duce la H4.</p>"
   + "<pre><code>economice = perechi.dropna(subset=[\"pib_locuitor_1\", \"pib_locuitor_2\"]).copy()\n"
     "economice[\"decalaj_pib\"] = (economice[\"pib_locuitor_1\"] - economice[\"pib_locuitor_2\"]).abs()</code></pre>")


NOR = {
    "variabile": [
        {"k": "nr", "et": "migranți, număr", "rho": H4["rho_nr"],
         "text": "Un milion de migranți înseamnă mult pentru Austria și puțin pentru Germania."},
        {"k": "rata", "et": "migranți la 1.000 de locuitori", "rho": H4["rho_rata"],
         "text": "Raportată la populația celor două țări, corelația aproape se dublează: SCI este și el o măsură relativă."}],
    "puncte": [{"t": t, "x": {"nr": m, "rata": r}, "y": s, "g": bool(g)} for t, s, m, r, g in H4["puncte"]],
    "etY": "SCI (scară logaritmică)", "etG": "perechile României", "etN": "celelalte perechi",
}

sl("s9", "Economia și oamenii", "H4: migrația",
   "<h2>H4: migranți, ca număr sau ca rată</h2>"
   + ix("nor", "Migrația și SCI, pe perechi de țări", NOR),
   manual=
   "<h2>H4: migranți, ca număr sau ca rată</h2>"
   f"<p>Perechile de țări cu migrația cunoscută în ambele sensuri: {H4['n']}. Corelația cu numărul de migranți este "
   f"pozitivă, dar nu foarte mare ({ro(H4['rho_nr'])}). SCI este însă relativ: împărțit la numărul de utilizatori din "
   "cele două țări. Comparabilă cu el este o rată: migranți la 1.000 de locuitori ai celor două țări, cu populația "
   "de la Banca Mondială, din C2.</p>"
   + ix("nor", "Migrația și SCI, pe perechi de țări", NOR)
   + f"<p>Zborurile, exercițiul din caiet: pe {H4['zboruri']['n']} de perechi cu pasageri, ρ = "
     f"{ro(H4['zboruri']['rho'])}, mult sub migrație. Numărul de pasageri depinde mai ales de mărimea țărilor.</p>")


RO = D["ro"]
_NUME = {"AT": "Austria", "DE": "Germania", "HU": "Ungaria", "IE": "Irlanda", "IT": "Italia", "BE": "Belgia",
         "ES": "Spania", "LU": "Luxemburg"}
DUBLU = {"randuri": [{"t": _NUME.get(c, c), "sci": s, "rata": r, "ev": c in ("IT", "HU")} for c, s, m, r, p in RO]}
V_RO = verif("c6-v-ro", 1,
             "Ungaria are un SCI mare cu România, dar puțini migranți la mie. Care explicație este cea mai plauzibilă?",
             ["O eroare în date", "Minoritatea maghiară: legături vechi, fără migrație", "Turismul", "Distanța"],
             "O parte din legături vin din minoritatea maghiară din România, nu din migrație. La cursul 7, distanța și "
             "migrația intră în același model, iar ce rămâne neexplicat arată astfel de cazuri.")

sl("s10", "Economia și oamenii", "Ghicitoarea din C1",
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
#  11-13. Rețeaua
# ===========================================================================

_POZ = {"DE21": (80, 170), "AT13": (220, 70), "HU32": (400, 62), "RO11": (530, 165), "RO32": (400, 255)}
RETEA = {
    "noduri": [{"k": c, "t": n, "x": _POZ[c][0], "y": _POZ[c][1]} for c, n in D["retea"]["noduri"]],
    "muchii": D["retea"]["muchii"],
    "start": "Cinci regiuni, toate legate între ele; grosimea liniei crește cu SCI-ul. <b>Un clic pe o regiune</b> "
             "îi aprinde legăturile și îi calculează forța.",
    "dupa": "În rețeaua întreagă, fiecare regiune are 297 de legături, deci forța adună 297 de valori.",
}
TF = D["retea"]["top_forta"]

sl("s11", "Rețeaua", "Nod, legătură, forță",
   "<h2>Aceleași perechi, ca rețea</h2>"
   "<p class=\"cheie\">Fiecare regiune este un nod, fiecare pereche o legătură, iar SCI-ul este ponderea ei. "
   "Forța unei regiuni este suma ponderilor.</p>"
   + ix("retea", "O rețea de cinci regiuni", RETEA),
   manual=
   "<h2>Aceleași perechi, ca rețea</h2>"
   "<p>Până acum, perechile au fost privite una câte una. O rețea le privește împreună: <code>networkx</code> o "
   "construiește direct din tabel, cu <code>nx.from_pandas_edgelist(perechi, \"regiune_1\", \"regiune_2\", "
   "edge_attr=\"sci\")</code>.</p>"
   + ix("retea", "O rețea de cinci regiuni", RETEA)
   + f"<p>Numărul de legături nu spune nimic aici, pentru că fiecare regiune este legată de toate celelalte. Forța "
     f"însă diferă. Primele regiuni după forță sunt {TF[0][1]} și câteva regiuni grecești: forța este o sumă de "
     "indici relativi, nu un număr de prieteni, iar regiunile mici urcă pentru că SCI este împărțit la numărul de "
     "utilizatori. Aceeași capcană ca la migrație.</p>")


HARTA_P = {
    "niveluri": ["regiuni"], "nivel": "regiuni", "masura": "sci", "ales": "RO41", "masuri": ["sci"],
    "povesti": [
        {"t": "Sud-Vest Oltenia", "nivel": "regiuni", "masura": "sci", "ales": "RO41",
         "text": "Partenerii din alte țări: Germania de sud (Mittelfranken, Niederbayern, Karlsruhe), Bruxelles, Viena, "
                 "Aragón și La Rioja. Drumurile migrației de muncă."},
        {"t": "Nord-Vest", "nivel": "regiuni", "masura": "sci", "ales": "RO11",
         "text": "Primul partener extern este Észak-Alföld, regiunea vecină din Ungaria, apoi Steiermark și Budapesta: "
                 "granița, minoritatea maghiară, apoi migrația."},
    ]}

sl("s12", "Rețeaua", "Partenerii unei regiuni",
   "<h2>Partenerii unei regiuni, din alte țări</h2>"
   + ix("harta", "Partenerii regiunii, pe hartă", HARTA_P),
   manual=
   "<h2>Partenerii unei regiuni, din alte țări</h2>"
   "<p>Pentru o regiune, cei mai legați parteneri din alte țări. Regiunea poate fi pe oricare capăt al perechii, "
   "deci caietul ia ambele cazuri și le pune unul sub altul, cu <code>pd.concat</code>. Liniile unesc centrele "
   "regiunilor; nu sunt drumuri.</p>"
   + ix("harta", "Partenerii regiunii, pe hartă", HARTA_P)
   + nota("Anticipare", "Înainte de hartă, se notează în ce țări vor fi partenerii. Comparația cu harta este partea "
                        "care învață ceva."))


HARTA_COM = {
    "niveluri": ["regiuni"], "nivel": "regiuni", "masura": "com", "ales": "RO11", "masuri": ["com", "sci"],
    "povesti": [
        {"t": "România și Germania", "nivel": "regiuni", "masura": "com", "ales": "RO11",
         "text": "Toate regiunile României sunt în aceeași comunitate cu Germania, nu cu țările vecine: o urmă a "
                 "migrației de muncă."},
        {"t": "Polonia și Irlanda", "nivel": "regiuni", "masura": "com", "ales": "PL91",
         "text": "Polonia, Irlanda, Islanda și Lituania formează o singură comunitate, urmă a emigrației de după 2004."},
        {"t": "Luxemburg și Portugalia", "nivel": "regiuni", "masura": "com", "ales": "LU00",
         "text": "Luxemburgul și regiunile Portugaliei, împreună: una dintre cele mai mari comunități portugheze din "
                 "afara țării."},
    ]}

sl("s13", "Rețeaua", "Comunitățile",
   "<h2>Comunitățile rețelei</h2>"
   + ix("harta", "Comunitățile SCI, pe regiuni", HARTA_COM),
   manual=
   "<h2>Comunitățile rețelei</h2>"
   f"<p>O comunitate este un grup de regiuni mai legate între ele decât cu restul. Algoritmul Louvain le caută "
   f"doar din ponderi: nu știe nimic despre țări sau hartă. Cu <code>seed=1</code>, rezultatul este același la "
   f"fiecare rulare: {D['comunitati']} comunități.</p>"
   + ix("harta", "Comunitățile SCI, pe regiuni", HARTA_COM)
   + "<p>Culorile sunt doar etichete. Cele mai multe comunități urmează granițele; informative sunt excepțiile, care "
     "trec de o graniță. Gruparea singură nu spune de ce (migrație, limbă, istorie): pentru asta trebuie alte date.</p>")


# ===========================================================================
#  14-16. Echipa
# ===========================================================================

DOVADA = {
    "id": "c6-dovada",
    "sarcina": "Trei rezultate din caiet, rulate pe datele proprii. Ieșirea fiecăruia se lipește în câmpul lui.",
    "indiciu": "Celulele se rulează în caietul 06, în ordine: datele din bază (1), distanța (3.1), economia (4.1), migrația (4.2).",
    "pasi": [
        {"t": "H1: distanța",
         "cmd": "perechi[\"distanta_km\"].corr(perechi[\"sci\"], method=\"spearman\")",
         "gol": "numărul afișat",
         "cauta": r"-0[.,]46\d",
         "ind": "Un singur număr, negativ, în jur de -0,46.",
         "daca_nu": "Corelația trebuie să fie în jur de -0.46. Distanța se calculează din centrele regiunilor (secțiunea 3.1)."},
        {"t": "H3: perechile cu PIB",
         "cmd": "print(len(economice), \"perechi cu PIB, din\", len(perechi))",
         "gol": "rândul afișat",
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


sl("s15", "Echipa", "Fișa echipei",
   "<h2>Fișa echipei</h2>"
   + ix("asteptari", "Ce a găsit echipa", {
       "id": "c6-fisa", "tip": "fisa", "minim": 80,
       "sarcina": "Pentru coridorul echipei: ce arată H1-H4 (un număr, cu câte perechi), dacă tiparul este compatibil "
                  "cu așteptarea, o explicație alternativă și o limită.",
       "exemplu": "De exemplu: perechea Italia-România are SCI 69.327, 1.088.052 de migranți (13,9 la mie), deci este "
                  "sub perechile cu o rată asemănătoare; o explicație alternativă: distanța.",
       "multumesc": "Fișa a fost înregistrată. Feedbackul vine înainte de cursul următor."}),
   manual=
   "<h2>Fișa echipei</h2>"
   + tabel(["Ce se raportează", "Din rulare"], [
       ["H1-H4: ce s-a găsit (un număr, cu câte perechi)", "..."],
       ["compatibile, incompatibile sau mixte cu așteptarea?", "..."],
       ["partenerii externi ai unei regiuni din coridor", "..."],
       ["o explicație alternativă și o limită", "..."],
   ])
   + ix("asteptari", "Ce a găsit echipa", {
       "id": "c6-fisa", "tip": "fisa", "minim": 80,
       "sarcina": "Pentru coridorul echipei: ce arată H1-H4, dacă tiparul este compatibil cu așteptarea, o explicație "
                  "alternativă și o limită.",
       "exemplu": "De exemplu: perechea Italia-România, cu SCI, migranții, rata și pasagerii.",
       "multumesc": "Fișa a fost înregistrată."}))


FIN_C6 = ('<div class="fin3"><div class="fin3__g">'
   "<section><h4>Ce urmează la cursul 7</h4><ul>"
   "<li>Variabilele: distanța, granița, rata migranților.</li>"
   "<li>Toate în același model.</li>"
   "<li>Ce rămâne neexplicat: perechile mai legate decât prezice modelul.</li></ul></section>"
   "<section><h4>Pregătirea pentru cursul 7</h4><ul>"
   "<li>Fișa echipei, în <code>README.md</code>.</li>"
   "<li>Perechea coridorului: SCI, migranții, rata și pasagerii.</li>"
   "<li>O explicație alternativă, de verificat în model.</li></ul></section>"
   "</div>"
   '<p class="fin3__a"><a class="leg" href="../">Pagina cursului 6</a></p></div>')

SURSE_C6 = surse("Documentația analizei", [
    ("pandas: cut", "https://pandas.pydata.org/docs/reference/api/pandas.cut.html", "împărțirea unei variabile numerice în intervale"),
    ("pandas: corr", "https://pandas.pydata.org/docs/reference/api/pandas.Series.corr.html", "Pearson și Spearman, cu <code>method=</code>"),
    ("GeoPandas: centroid", "https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoSeries.centroid.html", "centrul unei regiuni, într-o proiecție în metri"),
    ("networkx: Louvain", "https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.community.louvain.louvain_communities.html", "<code>louvain_communities</code>, <code>weight</code>, <code>seed</code>"),
])

sl("s16", "Mai departe", "Pentru cursul următor",
   "<h2>La cursul 7: variabile derivate și model</h2>" + FIN_C6,
   manual="<h2>La cursul 7: variabile derivate și model</h2>" + FIN_C6 + SURSE_C6)


if __name__ == "__main__":
    L.scrie_tot()
