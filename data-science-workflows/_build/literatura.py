"""Literatura proiectului, într-un singur loc.

Nu e toată literatura despre SCI și migrație. E ce folosesc caietele și ce
susține direct pașii proiectului: o întrebare despre legături și migrație,
perechi de țări și de regiuni, un model log-log și reziduurile lui.

Patru feluri de surse, în ordinea în care intră în fluxul de lucru:
  date        de unde vin datele și ce înseamnă (citezi setul, nu doar site-ul)
  teorie      de ce ar fi legate două locuri; de aici vin ipotezele
  metoda      cum au analizat alții aceeași întrebare; de aici vin alegerile
  documentatie cum faci tehnic un pas (API, pandas, networkx, statsmodels)

Sursa listei: harta literaturii și revizuirea pentru articolele pe SCI și
sistemele migratorii (2026), restrânse la ce intră în curs.
"""

FEL = {
    "date": ("Datele", "de unde vin datele și ce înseamnă"),
    "teorie": ("Teoria", "de ce ar fi legate două locuri: de aici vin ipotezele"),
    "metoda": ("Metoda", "cum au analizat alții aceeași întrebare: de aici vin alegerile"),
    "documentatie": ("Documentația", "cum faci tehnic pasul"),
}

# cheie: (fel, citare scurtă, referința completă, link, ce luăm de acolo, lecțiile)
REF = {
    # --- datele ---------------------------------------------------------------
    "johnston2026": ("date", "Johnston, Kuchler, Kulkarni și Stroebel (2026)",
        "Johnston, D., Kuchler, T., Kulkarni, M. și Stroebel, J. (2026). The Social Connectedness Index: "
        "A large-scale dataset of social ties across geographic locations. <i>Data in Brief</i>, 67, 112905.",
        "https://doi.org/10.1016/j.dib.2026.112905",
        "descrierea exactă a setului pe care lucrăm: instantaneul din ianuarie 2026, 178 de țări, "
        "nivelurile geografice, cine intră (utilizatori activi, cu peste 20 de prieteni) și de ce "
        "valorile nu se compară între fișiere. E referința pe care o citezi pentru date.", [1, 8]),

    # --- teoria ---------------------------------------------------------------
    "bailey2018": ("teorie", "Bailey și colegii (2018)",
        "Bailey, M., Cao, R., Kuchler, T., Stroebel, J. și Wong, A. (2018). Social connectedness: "
        "Measurement, determinants, and effects. <i>Journal of Economic Perspectives</i>, 32(3), 259–280.",
        "https://doi.org/10.1257/jep.32.3.259",
        "articolul care a introdus indicele: ce măsoară (o probabilitate relativă de prietenie), "
        "că scade puternic cu distanța și că urmează migrația, inclusiv cea veche.", [1, 3, 6]),
    "palloni2001": ("teorie", "Palloni și colegii (2001)",
        "Palloni, A., Massey, D. S., Ceballos, M., Espinosa, K. și Spittel, M. (2001). Social capital "
        "and international migration: A test using information on family networks. "
        "<i>American Journal of Sociology</i>, 106(5), 1262–1298.",
        "https://doi.org/10.1086/320817",
        "teoria rețelelor de migranți: legăturile cu cei plecați înainte fac drumul mai ieftin și mai "
        "sigur pentru cei care vin după. De aici ideea că migrația și legăturile merg împreună.", [3]),
    "dehaas2010": ("teorie", "de Haas (2010)",
        "de Haas, H. (2010). The internal dynamics of migration processes: A theoretical inquiry. "
        "<i>Journal of Ethnic and Migration Studies</i>, 36(10), 1587–1617.",
        "https://doi.org/10.1080/1369183X.2010.489361",
        "migrația și legăturile se întrețin una pe alta (feedback), dar nu la nesfârșit. De aici "
        "regula noastră: legătura dintre SCI și migrație e în ambele sensuri, deci nu spunem cine pe cine produce.", [3, 7]),
    "sandu2005": ("teorie", "Sandu (2005)",
        "Sandu, D. (2005). Emerging transnational migration from Romanian villages. "
        "<i>Current Sociology</i>, 53(4), 555–582.",
        "https://doi.org/10.1177/0011392105052715",
        "migrația românească nu pleacă uniform: localitățile se organizează în câmpuri de migrație, "
        "fiecare cu destinațiile lui (între altele Germania, Ungaria, Italia, Turcia, Spania). Cadrul românesc al întrebării noastre.", [3]),
    "sandu2025": ("teorie", "Sandu (2025)",
        "Sandu, D. (2025). A multi-level migration system between regions of origin and the European "
        "hexagon of attraction. <i>International Migration</i>, 63(5), e70092.",
        "https://doi.org/10.1111/imig.70092",
        "județele României și cele șase destinații mari (Italia, Spania, Germania, Regatul Unit, Franța, "
        "Austria), pe fluxuri 2011–2021. Reperul cu care se compară orice hartă a diasporei făcută din SCI.", [3]),

    # --- metoda ---------------------------------------------------------------
    "bailey2020": ("metoda", "Bailey și colegii (2020)",
        "Bailey, M., Johnston, D., Kuchler, T., Russel, D., State, B. și Stroebel, J. (2020). The "
        "determinants of social connectedness in Europe. În <i>Social Informatics (SocInfo 2020)</i>, "
        "LNCS 12467 (pp. 1–14). Springer.",
        "https://doi.org/10.1007/978-3-030-60975-7_1",
        "aceeași întrebare, pe regiunile Europei: log SCI explicat prin log distanță, graniță, limbă, "
        "istorie. Precedentul pentru ipotezele din C6 și pentru modelul din C7; folosește și Oltenia ca exemplu.", [6, 7]),
    "blondel2008": ("metoda", "Blondel și colegii (2008)",
        "Blondel, V. D., Guillaume, J.-L., Lambiotte, R. și Lefebvre, E. (2008). Fast unfolding of "
        "communities in large networks. <i>Journal of Statistical Mechanics: Theory and Experiment</i>, 2008(10), P10008.",
        "https://doi.org/10.1088/1742-5468/2008/10/P10008",
        "algoritmul Louvain, cu care găsim comunitățile. Exemplul lor, o rețea de telefonie din Belgia, "
        "regăsește granița dintre limbi: aceeași logică ca la noi.", [6]),
    "aronow2015": ("metoda", "Aronow, Samii și Assenova (2015)",
        "Aronow, P. M., Samii, C. și Assenova, V. A. (2015). Cluster-robust variance estimation for "
        "dyadic data. <i>Political Analysis</i>, 23(4), 564–577.",
        "https://doi.org/10.1093/pan/mpv018",
        "de ce perechile nu sunt observații independente (România–Italia și România–Spania au un capăt "
        "comun) și ce înseamnă asta pentru erorile standard. Limita principală a modelului din C7.", [7]),

    # --- căutarea literaturii -------------------------------------------------
    "scholar": ("documentatie", "Google Scholar",
        "Google Scholar: căutare de articole, cu „Citat de” pentru lucrările mai noi.",
        "https://scholar.google.com/", "căutarea pornind de la un articol-ancoră: cine l-a citat de atunci.", [3]),
    "semantic": ("documentatie", "Semantic Scholar",
        "Semantic Scholar: căutare de articole, cu referințe și citări navigabile.",
        "https://www.semanticscholar.org/", "referințele și citările unui articol, una lângă alta.", [3]),
    "zotero": ("documentatie", "Zotero",
        "Zotero: program gratuit pentru gestionarea referințelor și formatarea bibliografiei.",
        "https://www.zotero.org/", "salvezi articolele din browser și scoți bibliografia gata formatată în raport.", [3, 8]),
}


def lecturi(chei, titlu="De citit"):
    """Un bloc de lecturi, grupat pe feluri, în ordinea din flux."""
    grupe = {}
    for k in chei:
        f = REF[k][0]
        grupe.setdefault(f, []).append(k)
    h = ""
    for f in ["date", "teorie", "metoda", "documentatie"]:
        if f not in grupe:
            continue
        et, ce = FEL[f]
        li = "".join(
            f'<li><a class="lit__a" href="{REF[k][3]}" target="_blank" rel="noopener">{REF[k][1]}</a>'
            f'<span>{REF[k][4]}</span></li>' for k in grupe[f])
        h += f'<div class="lit__g"><div class="lit__f lit__f--{f}">{et}<small>{ce}</small></div><ul>{li}</ul></div>'
    return (f'<div class="lit"><div class="lit__et">{titlu}'
            f'<a class="lit__toata" href="../../lecturi/">toată literatura proiectului</a></div>{h}</div>')
