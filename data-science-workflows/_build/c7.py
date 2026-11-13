# -*- coding: utf-8 -*-
"""
Lecția 7: Variabile derivate și model.

Planul: ingineria variabilelor în cinci etape (construcție, transformare,
scalare, extragere, selecție), după planul cursului 7 din 2025, apoi modelul,
ca în caietul 07: trei modele pe aceleași perechi de țări, interpretarea
coeficienților, reziduurile. Același stil ca lecția 6: conceptul, un grafic
interactiv pe datele cursului, fâșia „Pe datele SCI”, pașii din caiet.

Cifrele vin din caietul 07 (date/c7-model.json): perechile de țări cu
migrația cunoscută, după deciziile din C6.

Rulare:  python _build/c7.py
"""

import json

from literatura import lecturi
from comun import Lectie, ix, verif, tabel, nota, surse, RAD

L = Lectie(7, "c7-variabile-si-model", "Variabile derivate și model",
           "Ingineria variabilelor (construcție, transformare, scalare, selecție), apoi un model care include "
           "simultan distanța, migrația și granița, cu interpretarea coeficienților și a reziduurilor.")
sl = L.sl

M = json.loads((RAD / "date" / "c7-model.json").read_text(encoding="utf-8"))
MOD, CI = M["modele"], M["ci"]
B4 = MOD["m4"]["coef"]
ro = lambda v, z=2: f"{v:.{z}f}".replace(".", ",").replace("-", "−")
pct = lambda v: f"{abs(v - 1) * 100:.0f}%"
_NB7 = "07_variabile_derivate_si_model.ipynb"
_T = {"tari": M["tari"]}
_REG = {"reg": json.loads((RAD / "date" / "c7-model.json").read_text(encoding="utf-8"))["regiuni"]}

# Glosarul lecției: termenul, echivalentul englezesc, o definiție scurtă.
G = {
    "fe": ("ingineria variabilelor", "feature engineering", "deciziile prin care variabilele unei analize sunt construite, transformate, scalate, rezumate și selectate."),
    "derivata": ("variabila derivată", "derived variable, feature", "o variabilă calculată din altele: o rată, o distanță, o diferență, un logaritm."),
    "rata": ("rata", "rate", "un număr raportat la mărimea populației; face comparabile țările mari și mici."),
    "binara": ("variabila binară", "dummy variable", "o variabilă cu două valori, 0 și 1: aici, 1 pentru țările vecine."),
    "log": ("logaritmul", "log transformation", "log10 x: 10 devine 1, 1.000 devine 3. Comprimă valorile mari și transformă relațiile multiplicative în relații liniare."),
    "z": ("scorul z", "z-score, standardization", "(x − media) / abaterea standard: media devine 0, abaterea standard 1; forma distribuției rămâne aceeași."),
    "pca": ("analiza componentelor principale", "principal component analysis, PCA", "rezumă mai mulți indicatori corelați într-unul sau câteva scoruri care păstrează cât mai mult din variația lor."),
    "multicol": ("multicoliniaritatea", "multicollinearity", "predictorii sunt puternic corelați între ei, astfel încât efectul fiecăruia se separă greu."),
    "vif": ("factorul de inflație a varianței (VIF)", "variance inflation factor", "1 / (1 − R²), unde R² arată cât de bine este explicat un predictor de ceilalți. Sub 5: acceptabil."),
    "model": ("modelul liniar", "linear regression model", "scrie variabila dependentă ca o sumă de predictori înmulțiți cu coeficienți, plus un reziduu."),
    "predictor": ("predictorul", "predictor, independent variable", "o variabilă folosită pentru a explica variabila dependentă (aici: distanța, migrația, granița)."),
    "coef": ("coeficientul", "coefficient", "cât se schimbă variabila dependentă când predictorul crește cu o unitate, ceilalți predictori rămânând la fel."),
    "mcmp": ("metoda celor mai mici pătrate", "ordinary least squares, OLS", "alege coeficienții pentru care suma pătratelor reziduurilor este cea mai mică."),
    "r2": ("R²", "coefficient of determination", "partea din variația variabilei dependente explicată de model, între 0 și 1."),
    "reziduu": ("reziduul", "residual", "valoarea observată minus valoarea prezisă de model."),
    "elast": ("elasticitatea", "elasticity", "pe logaritmi, coeficientul spune cu cât la sută se schimbă y când x crește cu 1%; dacă x se dublează, y se înmulțește cu 2 la puterea coeficientului."),
    "cluster": ("gruparea", "cluster analysis, clustering", "împarte observațiile în grupe, astfel încât observațiile din aceeași grupă să fie cât mai asemănătoare pe toți indicatorii."),
    "kmeans": ("k-means", "k-means", "fiecare observație merge la cel mai apropiat dintre k centre; fiecare centru se mută în media grupei lui; pașii se repetă până nu se mai schimbă nimic."),
    "inertia": ("inerția", "inertia, within-cluster sum of squares", "suma pătratelor distanțelor de la fiecare observație la centrul grupei ei; scade când k crește."),
    "r2a": ("R² ajustat", "adjusted R-squared", "R² penalizat pentru numărul de predictori; crește doar dacă un predictor nou aduce mai mult decât ar aduce întâmplarea."),
    "ic": ("intervalul de încredere", "confidence interval", "valorile plauzibile ale unui coeficient; dacă intervalul de 95% nu conține 0, coeficientul se deosebește de întâmplare."),
}


def gl(k, text=None):
    ro_, en, d = G[k]
    return (f'<span class="gl" tabindex="0">{text or ro_}<span class="gl__def"><b>{ro_[0].upper() + ro_[1:]}</b> '
            f'(engl. <i>{en}</i>): {d}</span></span>')


def concept(t):
    return f'<p class="def6"><b>Conceptul.</b> {t}</p>'


def vede(t):
    return f'<p class="noi6"><i>Pe datele SCI</i><span>{t}</span></p>'


def caiet(sectiune, pasi, incercat=None):
    h = (f'<div class="nota nota--sobru"><div class="nota__et">În caiet, secțiunea {sectiune}</div><ol>'
         + "".join(f"<li>{p}</li>" for p in pasi) + "</ol>")
    if incercat:
        h += f"<p><b>De încercat.</b> {incercat}</p>"
    return h + "</div>"


def glosar(*chei):
    return tabel(["Termenul", "În engleză", "Pe scurt"], [[G[k][0], f"<i>{G[k][1]}</i>", G[k][2]] for k in chei])


def cod(t):
    return f"<pre><code>{t}</code></pre>"


# ===========================================================================
#  A. Cursul
# ===========================================================================

CURSUL = tabel(["", "Conținutul", "Rezultatul"], [
    ["C1", "proiectul, mediul de lucru, tipurile de date și JSON", "<code>dsw/</code>, cu <code>.venv</code>"],
    ["C2", "colectarea datelor prin API: Eurostat, Banca Mondială", "<code>data/raw</code>"],
    ["C3", "surse diverse, preprocesare, Git și depozitul echipei", "<code>data/processed</code>, <code>proiect/</code>"],
    ["C4", "curățarea datelor și tabelul regiunilor", "<code>regiuni_nuts2.csv</code>"],
    ["C5", "integrare, baze de date și agregare", "perechile, în <code>dsw.db</code>"],
    ["C6", "analiza exploratorie", "deciziile pentru model"],
    ["<b>C7</b>", "<b>azi: variabile derivate și model</b>", "<b>modelul SCI și reziduurile lui</b>"],
    ["C8", "raportul și prezentarea proiectului", "raportul echipei"],
])

sl("s1", "Cursul", "Unde suntem",
   "<h2>Unde suntem în curs</h2>"
   "<p class=\"cheie\">Analiza exploratorie a găsit tipare: distanța, granița, migrația. Modelul le pune împreună "
   "și estimează ce rămâne din fiecare.</p>"
   + CURSUL,
   manual=
   "<h2>Variabile derivate și model</h2>"
   "<p>Analiza exploratorie (C6) a găsit trei tipare: SCI scade cu distanța, este mai mare peste o graniță comună și "
   "crește cu migrația. Tiparele se suprapun: țările vecine sunt și apropiate, și au mai mulți migranți între ele. "
   "Un model le include simultan și estimează contribuția fiecăruia când celelalte sunt ținute constante.</p>"
   "<p>Modelul este precedat de ingineria variabilelor: ce variabile se construiesc, cum se transformă, ce se "
   "păstrează. În această etapă se iau cele mai multe decizii, iar multe dintre ele nu se văd în rezultatul final.</p>"
   + CURSUL
   + nota("Caietul lecției", f"<code>{_NB7}</code>, în <code>dsw/curs/</code>. Pachet nou: <code>statsmodels</code>, "
                             "deja în <code>requirements.txt</code>.", True))


FLUX7 = (
    '<div class="ed6 ed6--5">'
    '<div><small>1 · construcția</small><b>variabile noi din cele existente</b></div>'
    '<div><small>2 · transformarea</small><b>forma distribuției: logaritmul</b></div>'
    '<div><small>3 · scalarea</small><b>aceeași scară: scorul z</b></div>'
    '<div><small>4 · extragerea</small><b>mai mulți indicatori: un scor sau o grupă</b></div>'
    '<div class="nou"><small>5 · selecția</small><b>setul final, fără redundanță</b></div>'
    '</div>'
    '<p class="ed6__inapoi">dacă modelul arată o problemă, se revine la o etapă anterioară</p>')

DECIZII = tabel(["Din C6", "În model"], [
    ["SCI: asimetrie pozitivă", "log SCI"],
    ["Svalbard: numitor foarte mic", "exclus"],
    ["distanța și granița, legate", "două variabile separate: log distanța și granița"],
    ["migrația contează ca rată", "log rata migranților la mie; în M4, cu efectele de țară, numărul de migranți"],
    ["partenerii și comunitățile urmează migrația", "reziduurile arată ce rămâne după migrație"],
])

sl("s2", "Variabilele", "Cinci etape",
   "<h2>Ingineria variabilelor</h2>"
   + concept(f"Între datele curate și model stă {gl('fe')}: deciziile prin care se construiesc, se transformă și se "
             f"aleg variabilele modelului. O {gl('derivata', 'variabilă derivată')} este calculată din altele.")
   + FLUX7
   + vede("Deciziile din C6 devin variabile: SCI și distanța pe logaritm, migrația ca rată, granița ca variabilă "
          "separată, Svalbard exclus."),
   manual=
   "<h2>Ingineria variabilelor</h2>"
   "<p>Ingineria variabilelor (engl. <i>feature engineering</i>) este ansamblul deciziilor prin care variabilele unei "
   "analize sunt construite, transformate, scalate, rezumate și selectate. În științele sociale scopul ei nu este "
   "predicția, ci comparația și interpretarea: fiecare variabilă trebuie să corespundă unui concept și să poată fi "
   "citită.</p>"
   + FLUX7
   + "<p>Nu toate etapele apar în fiecare proiect. Pe datele SCI, construcția și transformarea sunt esențiale; "
     "scalarea servește la compararea coeficienților; extragerea, prin gruparea regiunilor, produce o variabilă nouă, "
     "tipul de regiune; selecția verifică redundanța. Deciziile din analiza exploratorie trec direct în model:</p>"
   + DECIZII
   + glosar("fe", "derivata"))


# ===========================================================================
#  B. Ingineria variabilelor
# ===========================================================================

sl("s3", "Variabilele", "Construcția",
   "<h2>Construcția: aceeași informație, altă variabilă</h2>"
   + concept(f"Numărul de migranți depinde de mărimea țărilor. Împărțit la populația celor două țări, devine o "
             f"{gl('rata', 'rată')}, comparabilă între țări mari și mici. Butoanele schimbă variabila de pe axa orizontală.")
   + ix("edModelVar", "SCI și migrația, pe perechi de țări", {**_T, "mod": "constr"})
   + vede(f"Singur, numărul de migranți explică {ro(M['r2_simplu']['migranti'])} din variația lui log SCI; rata, "
          f"{ro(M['r2_simplu']['la_mie'])}. Aceeași informație, construită altfel, explică de trei ori mai mult."),
   manual=
   "<h2>Construcția</h2>"
   "<p>Construcția produce variabile noi din cele existente. Modelul se face pe perechi de țări, pentru că migrația "
   f"există doar între țări: {M['n']} de perechi cu migrația cunoscută. Tabelului îi lipsesc trei variabile.</p>"
   + tabel(["Variabila", "Cum se construiește", "De ce"], [
       ["<b>migranți la mie</b>", "migranții în ambele sensuri, împărțiți la populația celor două țări (Banca Mondială, 2024), × 1.000",
        "numărul brut favorizează țările mari"],
       ["<b>distanța dintre țări</b>", "mediana distanțelor dintre toate regiunile celor două țări (din C6)",
        "mediana nu e trasă de insule și teritoriile de peste mări"],
       ["<b>granița comună</b>", "țările lipite din regiuni (<code>dissolve</code>), lărgite cu 10 km, care se ating (<code>sjoin</code>)",
        f"o {gl('binara', 'variabilă binară')}: 1 pentru vecine, 0 în rest"]])
   + ix("edModelVar", "SCI și migrația, pe perechi de țări", {**_T, "mod": "constr"})
   + f"<p>Rata și numărul conțin aceeași informație despre migranți, dar rata o raportează la mărimea țărilor. Pe "
     "datele SCI, care sunt și ele raportate la numărul de utilizatori, rata se potrivește mai bine: corelația pe "
     "logaritmi crește, iar R² urcă de la {ro(M['r2_simplu']['migranti'])} la {ro(M['r2_simplu']['la_mie'])}. Alegerea unei variabile derivate este o decizie de măsurare, nu un "
     "detaliu tehnic.</p>"
   + glosar("rata", "binara")
   + caiet("1", [
       "<code>la_mie</code>: migranții împărțiți la populația celor două țări, din <code>raw/bm.csv</code>, din depozitul cursului.",
       "Numele perechii (<code>pereche</code>): cele două coduri în ordine alfabetică, „AT-RO”, scris mereu la fel; "
       "distanța dintre țări este mediana distanțelor dintre regiunile lor (<code>groupby(\"pereche\")</code>, apoi "
       "<code>map</code>).",
       "<code>granita</code>, pas cu pas, fiecare cu harta lui: țările lipite din regiuni (<code>dissolve</code>), "
       "România lărgită cu 10 km (<code>buffer(10_000)</code>), România și vecinii ei (<code>sjoin</code>)."],
       "<code>tari[\"granita\"].sum()</code>: câte perechi de țări vecine?"))


sl("s4", "Variabilele", "Transformarea",
   "<h2>Transformarea: logaritmul</h2>"
   + concept(f"SCI și distanța au coadă lungă. {gl('log', 'Logaritmul')} le aduce aproape de simetrie și face "
             "relația aproape o dreaptă, ce poate fi descrisă de un model liniar. Granița (0 sau 1) nu se logaritmează.")
   + ix("edModelVar", "SCI și distanța, pe perechi de țări", {**_T, "mod": "transf"})
   + vede("Pe valorile brute, câteva perechi foarte legate trag dreapta; pe logaritmi, norul are formă de dreaptă, "
          "iar asimetria lui SCI scade de la 7,6 la 0,5."),
   manual=
   "<h2>Transformarea</h2>"
   "<p>Transformarea schimbă forma distribuției. Pe datele SCI, trei variabile au coadă lungă spre dreapta: SCI "
   "(asimetria 7,6), rata migranților (3,6) și, mai puțin, distanța (0,7). După logaritm, asimetriile lui SCI și a "
   "ratei ajung la 0,5 și aproape 0. Logaritmul are un al doilea efect, mai important pentru model: o relație "
   "multiplicativă („de două ori mai departe, cu o cincime mai puțin legat”) devine una liniară.</p>"
   + ix("edModelVar", "SCI și distanța, pe perechi de țări", {**_T, "mod": "transf"})
   + tabel(["Se logaritmează", "Nu se logaritmează"], [
       ["mărimi cu coadă lungă: SCI, distanța, migranții, populația", "variabile binare (granița), procente și indici mărginiți"],
       ["rate cu coadă lungă: migranții la mie", "variabile cu valoarea 0 (log 0 nu există)"]])
   + "<p>Baza logaritmului nu schimbă concluziile: log10 și ln diferă doar printr-un factor constant, iar "
     "coeficienții unui model cu logaritmi pe ambele părți sunt aceiași în orice bază. Caietul folosește log10, ca "
     "în C6.</p>"
   + glosar("log")
   + caiet("2", [
       "Asimetria lui <code>sci</code>, <code>distanta_km</code> și <code>la_mie</code>, înainte și după <code>np.log10</code>.",
       "Coloanele <code>log_sci</code>, <code>log_distanta</code>, <code>log_migranti</code>, <code>log_la_mie</code>.",
       "<code>sns.regplot</code> pe log-log; apoi același eșantion pentru toate modelele (<code>dropna</code>, o singură dată)."],
       "<code>sns.regplot(tari, x=\"distanta_km\", y=\"sci\")</code>, pe valorile brute."))


V_Z = verif("c7-v-z", 1,
            "Scorul z se aplică ratei migranților. Ce se schimbă?",
            ["Forma distribuției",
             "Media și abaterea standard: devin 0 și 1",
             "Ordinea perechilor"],
            "Scorul z doar mută și întinde axa. Forma și ordinea rămân; forma o schimbă logaritmul.",
            indiciu="z = (valoarea − media) / abaterea standard: se scade un număr și se împarte la un număr. "
                    "Ce poate schimba o asemenea operație?")

_Z = {**_T, "alese": ["IT–RO", "HU–RO", "DE–TR", "IS–NO"]}

sl("s5", "Variabilele", "Scalarea",
   "<h2>Scalarea: aceeași scară pentru toate</h2>"
   + concept("Este distanța de 1.100 km dintre Italia și România mare sau mică? Dar 13,9 migranți la mie? Kilometrii "
             f"și migranții la mie nu se pot compara direct. {gl('z', 'Scorul z')}, z = (valoarea − media) / abaterea "
             "standard, spune cu câte abateri standard este o pereche peste (z &gt; 0) sau sub (z &lt; 0) perechea "
             "medie: aceeași unitate pentru toate variabilele.")
   + ix("edScalare", "O pereche, pe trei variabile: valorile, apoi scorul z", _Z)
   + vede("IT-RO: distanța are z = −0,2 (obișnuită), rata migranților z = +2,4 (printre cele mai mari din Europa). "
          "Scorul z schimbă doar centrul și unitatea: asimetria fiecărei variabile rămâne aceeași."),
   dupa=V_Z,
   manual=
   "<h2>Scalarea</h2>"
   "<p><b>Problema.</b> Variabilele au unități diferite: SCI e o probabilitate relativă, distanța e în kilometri, "
   "migrația în migranți la mie. O pereche de țări are pe fiecare o valoare, dar valorile nu se pot compara între ele: "
   "1.100 km și 13,9 la mie nu spun, singure, care dintre ele e neobișnuită.</p>"
   "<p><b>Soluția: scorul z.</b> z = (valoarea − media) / abaterea standard spune cu câte abateri standard este o "
   "pereche peste (z pozitiv) sau sub (z negativ) perechea medie. Perechea Italia-România are distanța de 1.100 km, "
   "deci z = −0,2: aproape de medie. Rata ei de migranți, 13,9 la mie, are z = +2,4: printre cele mai mari din Europa. "
   "În abateri standard, cele două se pot compara: perechea e obișnuită ca distanță și excepțională ca migrație. "
   "După scorul z, fiecare variabilă are media 0 și abaterea standard 1.</p>"
   + ix("edScalare", "O pereche, pe trei variabile: valorile, apoi scorul z", _Z)
   + "<p><b>Ce nu se schimbă.</b> Scorul z scade o constantă și împarte la o constantă: este o transformare liniară. "
     "Forma distribuției (asimetria, valorile extreme) și ordinea perechilor rămân aceleași; graficul arată aceeași "
     "asimetrie înainte și după. Pentru a schimba forma e nevoie de o transformare neliniară, ca logaritmul din "
     "slide-ul anterior. Alte variante de scalare sunt min-max (între 0 și 1) și scalarea robustă (cu mediana și IQR, "
     "pentru date cu valori extreme).</p>"
     "<p><b>De ce contează mai departe.</b> Scorul z va servi de două ori: la gruparea regiunilor (k-means "
     "calculează distanțe pe toți indicatorii deodată) și la compararea coeficienților modelului (slide-ul cu "
     "interpretarea).</p>"
   + V_Z
   + glosar("z")
   + caiet("2.2", [
       "Funcția <code>scor_z(x)</code>: <code>(x - x.mean()) / x.std()</code>.",
       "Coloanele <code>z_log_sci</code>, <code>z_log_distanta</code>, <code>z_log_la_mie</code>; "
       "<code>describe()</code> arată media 0 și abaterea standard 1."],
       "<code>skew()</code> înainte și după scorul z: se schimbă asimetria?"))


VIF = M.get("vif") or {"log_distanta": 1.7, "log_la_mie": 1.15, "granita": 1.72}
COR = M["corr"]
TAB_SEL = tabel(["Predictorul", "Corelația cu distanța", "Corelația cu rata", "VIF"], [
    ["log distanța", "1", ro(COR[0][1]), ro(VIF["log_distanta"])],
    ["log migranți la mie", ro(COR[1][0]), "1", ro(VIF["log_la_mie"])],
    ["granița", ro(COR[2][0]), ro(COR[2][1]), ro(VIF["granita"])]])

sl("s7", "Variabilele", "Selecția",
   "<h2>Selecția: predictori fără redundanță</h2>"
   + concept(f"Doi predictori care spun aproape același lucru nu se pot separa în model ({gl('multicol')}). "
             f"{gl('vif', 'VIF')} măsoară cât de bine e explicat un predictor de ceilalți: sub 5, acceptabil; "
             "peste 10, unul se scoate.")
   + TAB_SEL
   + vede(f"Distanța și granița sunt legate (r = {ro(COR[0][2])}: vecinii sunt apropiați), dar toate VIF-urile sunt "
          "sub 2. Toți trei predictorii rămân."),
   manual=
   "<h2>Selecția</h2>"
   "<p>Selecția păstrează un set restrâns de predictori, fiecare pentru un concept distinct. Criteriile sunt două: "
   "teoretic, fiecare predictor are un sens (distanța, migrația, granița); statistic, predictorii nu sunt redundanți. "
   "Un predictor este redundant dacă ceilalți îl explică aproape complet; atunci modelul nu poate spune cât contează "
   "fiecare, iar coeficienții devin instabili.</p>"
   "<p>VIF se calculează direct din definiție: fiecare predictor se explică prin ceilalți printr-un model, iar "
   "VIF = 1 / (1 − R²). Un R² de 0,8 dă VIF = 5; un R² de 0,9 dă VIF = 10.</p>"
   + TAB_SEL
   + "<p>Nu se includ în același model nivelul și o transformare a aceleiași variabile (de exemplu, numărul de "
     "migranți și rata lor): ele măsoară același concept. De aceea modelul folosește rata, nu și "
     "numărul; un exercițiu din caiet le compară.</p>"
   + glosar("multicol", "vif")
   + caiet("3", [
       "<code>date[predictori].corr()</code>: corelațiile dintre cei trei predictori.",
       "O buclă: pentru fiecare predictor, <code>smf.ols</code> pe ceilalți, apoi <code>1 / (1 - r2)</code>."]))


# ===========================================================================
#  C. Modelul
# ===========================================================================

_PT = [[round(__import__("math").log10(r[5]), 4), round(__import__("math").log10(r[2]), 4), r[6]] for r in M["tari"]]
_M1 = MOD["m1"]["coef"]
REZ1 = {"perechi": _PT, "dy": [3, 6.6], "rm": 1.2, "a0": 6, "b0": -0.4, "r2": True,
        "et": ["țări nevecine", "țări vecine (portocaliu)"],
        "cod": 'm1 = smf.ols("log_sci ~ log_distanta", data=date).fit()\nm1.params        # constanta (Intercept) și panta\ndate["reziduu"] = m1.resid'}

sl("s8", "Modelul", "Tipar și reziduu",
   "<h2>Modelul: tipar plus reziduu</h2>"
   + concept(f"{gl('model', 'Modelul liniar')} scrie fiecare valoare ca tipar plus {gl('reziduu', 'reziduu')}: log SCI = constantă + "
             f"pantă × log distanța + reziduu. Constanta (<i>intercept</i>) fixează înălțimea dreptei; panta, "
             f"înclinarea ei. {gl('mcmp', 'Cele mai mici pătrate')} aleg dreapta cu suma pătratelor reziduurilor minimă.")
   + ix("edReziduu", "Distanța și SCI, pe perechi de țări", REZ1)
   + vede(f"Doar cu distanța: panta {ro(_M1['log_distanta'])} și {gl('r2', 'R²')} = {ro(MOD['m1']['r2'])}. Distanța "
          "explică doar o șesime din variația SCI între țări."),
   manual=
   "<h2>Modelul: tipar plus reziduu</h2>"
   "<p>Un model liniar descrie variabila dependentă ca tipar plus reziduu. Cu un singur predictor, tiparul este o "
   "dreaptă: log SCI = constantă + pantă × log distanța. <b>Constanta</b> (engl. <i>intercept</i>, în statsmodels "
   "<code>Intercept</code>) este log SCI prezis când log distanța este 0, adică la 1 km: o distanță care nu există "
   "între țări, deci constanta doar fixează înălțimea dreptei și nu se interpretează. <b>Panta</b> spune cu cât se "
   "schimbă log SCI când distanța se înmulțește cu 10. Reziduul este ce rămâne: diferența dintre valoarea observată "
   "și dreaptă. Metoda celor mai mici pătrate alege constanta și panta pentru care suma pătratelor reziduurilor este "
   "cea mai mică; în graficul de mai jos, ele se pot căuta și de mână, cu glisoarele.</p>"
   + ix("edReziduu", "Distanța și SCI, pe perechi de țări", REZ1)
   + "<p>R² compară suma pătratelor reziduurilor cu variația totală a lui log SCI: R² = 1 − (suma pătratelor "
     f"reziduurilor) / (suma pătratelor abaterilor de la medie). Cu distanța singură, R² = {ro(MOD['m1']['r2'])}. Este "
     "aceeași idee ca raportul „față de distanță” din C6: ce iese din tipar, acum față de o dreaptă.</p>"
   + glosar("model", "reziduu", "mcmp", "r2")
   + caiet("4.1", [
       "<code>smf.ols(\"log_sci ~ log_distanta\", data=date).fit()</code>: formula are variabila dependentă la stânga "
       "lui <code>~</code> și predictorii la dreapta.",
       "<code>m1.params</code> (constanta și panta) și <code>m1.rsquared</code>."]))


def _mod(k, nume, formula, text):
    c = MOD[k]["coef"]
    return {"nume": nume, "formula": formula, "r2": MOD[k]["r2"], "text": text,
            "coef": {"dist": c.get("log_distanta"), "migr": c.get("log_migranti"),
                     "rata": c.get("log_la_mie"), "gr": c.get("granita")}}


MODELE = {
    "lim": 0.8,
    "variabile": [
        {"k": "dist", "et": "log distanța", "c": "ceas"},
        {"k": "rata", "et": "log migranți la mie", "c": "accent"},
        {"k": "gr", "et": "granița", "c": "text-2"},
    ],
    "modele": [
        _mod("m1", "M1", "log_sci ~ log_distanta", f"Doar distanța: R² = {ro(MOD['m1']['r2'])}."),
        _mod("m4", "M2", "log_sci ~ log_distanta + log_la_mie + granita",
             f"Cu migrația și granița, R² crește la {ro(MOD['m4']['r2'])}, iar coeficientul distanței scade: o parte "
             "din „efectul distanței” era migrație."),
    ],
}

TAB_TEORIE = tabel(["Variabila", "De ce ar conta", "Semnul așteptat"], [
    ["distanța", "contactul costă mai mult la distanță mare (modelul gravitațional)", "negativ"],
    ["rata migranților", "cei plecați păstrează legăturile cu cei de acasă (rețelele de migrație)", "pozitiv"],
    ["granița comună", "contact zilnic, istorie și minorități comune", "pozitiv"]])

PRED = {**_T, "alese": ["IT–RO", "HU–RO", "DE–RO", "DE–TR", "IS–NO"],
        "modele": [{"nume": "M1: doar distanța", "var": "m1", "coef": MOD["m1"]["coef"]},
                   {"nume": "M2: trei variabile", "var": "m2", "coef": B4}]}

sl("s9", "Modelul", "Trei variabile",
   "<h2>Trei variabile, fiecare cu o explicație</h2>"
   + concept(f"Fiecare {gl('predictor', 'predictor')} are un motiv teoretic: distanța (contactul costă), migrația "
             "(cei plecați păstrează legăturile), granița (contact zilnic). Predicția unei perechi este o sumă: "
             f"constanta plus, pentru fiecare predictor, {gl('coef', 'coeficientul')} înmulțit cu valoarea perechii.")
   + ix("edPredictie", "Cum prezice modelul SCI-ul unei perechi", PRED)
   + vede("Constanta, plus câte o bară pentru fiecare predictor, dă SCI-ul prezis. IT-RO: M2 prezice mai mult decât "
          "se observă (×0,70); HU-RO e de 1,9 ori peste model: minoritatea maghiară nu e în model."),
   manual=
   "<h2>Trei variabile, două modele</h2>"
   "<p>Fiecare predictor are un motiv teoretic și o direcție așteptată, stabilite înainte de estimare:</p>"
   + TAB_TEORIE
   + "<p>Selecția (slide-ul anterior) a arătat că cele trei nu se suprapun: VIF sub 2. M1 conține doar distanța, M2 "
     f"pe toate trei. Ambele se estimează pe aceleași {M['n']} de perechi de țări: dacă eșantionul s-ar schimba de la "
     "un model la altul, diferențele dintre coeficienți ar putea veni din perechile diferite, nu din variabile.</p>"
   + ix("modele", "Coeficienții și R², M1 și M2", MODELE)
   + "<p>Aceeași formulă, pe o pereche concretă: constanta, apoi contribuția fiecărui predictor (coeficientul "
     "înmulțit cu valoarea perechii, pe logaritm), apoi comparația cu SCI-ul observat. Diferența este reziduul. "
     "Butoanele schimbă perechea și modelul: în M1, distanța „preia” și efectul migrației.</p>"
   + ix("edPredictie", "Cum prezice modelul SCI-ul unei perechi", PRED)
   + tabel(["", "M1", "M2"], [
       ["log distanța", ro(MOD["m1"]["coef"]["log_distanta"]), ro(B4["log_distanta"])],
       ["log migranți la mie", "", ro(B4["log_la_mie"])],
       ["granița", "", ro(B4["granita"])],
       ["R²", ro(MOD["m1"]["r2"]), ro(MOD["m4"]["r2"])]])
   + "<p>Coeficientul distanței scade când intră migrația: țările apropiate au mai mulți migranți între ele, deci fără "
     "migrație în model distanța „preia” și o parte din efectul ei. Construcția variabilei contează: cu numărul de "
     "migranți în locul ratei, R² este 0,26, nu 0,53 (exercițiul din caiet).</p>"
   + lecturi(["bailey2020", "aronow2015", "dehaas2010"], "Modelul, în literatură")
   + glosar("coef", "predictor")
   + caiet("4.2 și 4.3", [
       "<code>m2</code> cu <code>smf.ols</code>; tabelul <code>modele</code>, cu M1, M2 și R² pe ultimul rând.",
       "Exercițiul: același model cu numărul de migranți în locul ratei.",
       "<code>m2z</code>: același model pe scorurile z, pentru compararea coeficienților."]))



# Ieșirea lui m2.summary(), cu câmpurile care se explică la clic
SU = M["sumar"]
_C = SU["coef"]
e3 = lambda v: f"{v:.2e}" if v < 1e-3 else f"{v:.3f}"


def _r(nume, k):
    c = _C[nume]
    return [[f"{nume:<15}", None], [f"{c['b']:8.4f}", "coef"], [f"{c['se']:11.3f}", "se"], [f"{c['t']:11.3f}", "t"],
            [f"{c['p']:11.3f}", "p_" + k], [f"{c['lo']:12.3f}", "ic_" + k], [f"{c['hi']:12.3f}", "ic_" + k]]


def _d(st, dr):
    """Un rând cu două câmpuri: (eticheta, valoarea, cheia) la stânga și la dreapta, ca în statsmodels."""
    o = []
    if st:
        et, v, k = st
        o += [[et, k], [v.rjust(36 - len(et)), k]]
    else:
        o += [[" " * 36, None]]
    o += [["   ", None]]
    if dr:
        et, v, k = dr
        o += [[et, k], [v.rjust(41 - len(et)), k]]
    return o


_L = [
    [["OLS Regression Results".center(80), None]],
    [["=" * 80, None]],
    _d(("Dep. Variable:", "log_sci", None), ("R-squared:", f"{SU['r2']:.3f}", "r2")),
    _d(("Model:", "OLS", None), ("Adj. R-squared:", f"{SU['r2a']:.3f}", "r2a")),
    _d(("Method:", "Least Squares", None), ("F-statistic:", f"{SU['F']:.2f}", "F")),
    _d(("No. Observations:", f"{SU['n']}", "n"), ("Prob (F-statistic):", f"{SU['pF']:.2e}", "F")),
    _d(("Df Residuals:", f"{SU['df_resid']}", "df"), ("Log-Likelihood:", f"{SU['ll']:.3f}", "aic")),
    _d(("Df Model:", f"{SU['df_model']}", "df"), ("AIC:", f"{SU['aic']:.1f}", "aic")),
    _d(None, ("BIC:", f"{SU['bic']:.1f}", "aic")),
    [["=" * 80, None]],
    [[" " * 15, None], ["coef".rjust(8), "coef"], ["std err".rjust(11), "se"], ["t".rjust(11), "t"],
     ["P>|t|".rjust(11), "p_dist"], ["[0.025".rjust(12), "ic_gr"], ["0.975]".rjust(12), "ic_gr"]],
    [["-" * 80, None]],
    _r("Intercept", "int"), _r("log_distanta", "dist"), _r("log_la_mie", "rata"), _r("granita", "gr"),
    [["=" * 80, None]],
    _d(("Omnibus:", f"{SU['omnibus']:.3f}", "norm"), ("Durbin-Watson:", f"{SU['dw']:.3f}", "dw")),
    _d(("Prob(Omnibus):", f"{SU['p_omnibus']:.3f}", "norm"), ("Jarque-Bera (JB):", f"{SU['jb']:.3f}", "norm")),
    _d(("Skew:", f"{SU['skew']:.3f}", "skew"), ("Prob(JB):", f"{SU['p_jb']:.2e}", "norm")),
    _d(("Kurtosis:", f"{SU['kurt']:.3f}", "skew"), ("Cond. No.", f"{SU['cond']:.1f}", "cond")),
    [["=" * 80, None]],
]
_X = {
    "r2": ("R² (R-squared)", f"{ro(SU['r2'], 3)}", "Partea din variația lui log SCI explicată de model: 53%. Restul de 47% este în reziduuri."),
    "r2a": ("R² ajustat (Adj. R-squared)", f"{ro(SU['r2a'], 3)}", "R² penalizat pentru numărul de predictori. R² crește la orice predictor adăugat, chiar fără legătură; R² ajustat crește doar dacă predictorul aduce mai mult decât întâmplarea. Se folosește la compararea modelelor cu număr diferit de predictori."),
    "F": ("Testul F", f"F = {ro(SU['F'], 1)}; p = {SU['pF']:.1e}".replace(".", ","), "Testează ipoteza că niciun predictor nu contează (toți coeficienții sunt 0). Valoarea p este practic 0: modelul, în ansamblu, explică ceva."),
    "n": ("Numărul de observații", f"{SU['n']}", "Perechile de țări cu toate variabilele: eșantionul comun al tuturor modelelor."),
    "df": ("Gradele de libertate", f"model {SU['df_model']}, reziduuri {SU['df_resid']}", "Model: numărul de predictori (3). Reziduuri: observațiile minus parametrii estimați (263 − 4 = 259, cu constanta). Intră în calculul erorilor standard și al valorilor p."),
    "aic": ("Log-Likelihood, AIC, BIC", f"AIC {ro(SU['aic'], 1)}, BIC {ro(SU['bic'], 1)}", "Compară modele estimate pe aceleași date: valoarea mai mică e mai bună. Spre deosebire de R², penalizează fiecare predictor în plus (BIC mai tare decât AIC)."),
    "coef": ("Coeficientul (coef)", f"log_la_mie: {ro(_C['log_la_mie']['b'], 3)}", "Estimarea efectului fiecărui predictor, cu ceilalți ținuți constanți. Pe logaritmi, o elasticitate (slide-ul următor)."),
    "se": ("Eroarea standard (std err)", f"log_la_mie: {ro(_C['log_la_mie']['se'], 3)}", "Cât de precisă este estimarea: cât ar varia coeficientul de la un eșantion la altul. Mai mică înseamnă mai precisă."),
    "t": ("Statistica t", f"log_la_mie: {ro(_C['log_la_mie']['t'], 1)}", "Coeficientul împărțit la eroarea lui standard: de câte ori e mai mare estimarea decât incertitudinea ei. Regula practică: peste 2 în valoare absolută, p sub 0,05."),
    "p_int": ("Valoarea p, constanta", e3(_C["Intercept"]["p"]), "Constanta este log SCI prezis la 1 km și o rată de 1 la mie: o extrapolare, fără sens direct. Valoarea ei p nu se interpretează."),
    "p_dist": ("Valoarea p, distanța", f"{_C['log_distanta']['p']:.3f}".replace(".", ","), "Proporția estimărilor la fel de mari care ar apărea dacă distanța nu ar conta (ca la amestecarea din C6). Sub 0,05: distanța contează, la aceeași migrație și graniță."),
    "p_rata": ("Valoarea p, rata migranților", "practic 0", "t = 13,7: rata migranților este predictorul cel mai puternic și cel mai precis."),
    "p_gr": ("Valoarea p, granița", f"{_C['granita']['p']:.3f}".replace(".", ","), "Peste 0,05: efectul graniței nu se deosebește de întâmplare, odată ce distanța și migrația sunt în model."),
    "ic_int": ("Intervalul de 95%, constanta", f"{ro(_C['Intercept']['lo'])} … {ro(_C['Intercept']['hi'])}", "Valorile plauzibile ale constantei."),
    "ic_dist": ("Intervalul de 95%, distanța", f"{ro(_C['log_distanta']['lo'])} … {ro(_C['log_distanta']['hi'])}", "Nu conține 0: efectul distanței este negativ, între −0,51 și −0,10."),
    "ic_rata": ("Intervalul de 95%, rata", f"{ro(_C['log_la_mie']['lo'])} … {ro(_C['log_la_mie']['hi'])}", "Îngust și departe de 0: estimarea cea mai sigură a modelului."),
    "ic_gr": ("Intervalul de 95%, granița", f"{ro(_C['granita']['lo'])} … {ro(_C['granita']['hi'])}", "Conține 0: efectul graniței poate fi la fel de bine nul. Aceeași concluzie ca valoarea p de 0,21."),
    "norm": ("Normalitatea reziduurilor: Omnibus, Jarque-Bera", f"p = {SU['p_omnibus']:.0e}; p = {SU['p_jb']:.0e}".replace(".", ","), "Testează dacă reziduurile au distribuție normală. Ambele p sunt sub 0,001: reziduurile nu sunt perfect normale. Cu 263 de perechi, abaterea moderată nu schimbă mult coeficienții, dar se spune în raport."),
    "skew": ("Asimetria și aplatizarea reziduurilor", f"skew {ro(SU['skew'])}, kurtosis {ro(SU['kurt'])}", "Asimetria 0,65: coadă spre dreapta, câteva perechi mult peste model (Islanda). Aplatizarea 3,57, puțin peste 3, valoarea distribuției normale."),
    "dw": ("Durbin-Watson", f"{ro(SU['dw'])}", "Aproape de 2: fără autocorelație între rândurile vecine. Contează mai ales la serii de timp; aici ordinea rândurilor este arbitrară."),
    "cond": ("Numărul de condiționare (Cond. No.)", f"{ro(SU['cond'], 1)}", "Valorile mari (statsmodels avertizează peste 1.000) semnalează multicoliniaritate sau scări foarte diferite. Aici e mic, ca VIF-urile."),
}
SUMAR = {"linii": _L, "expl": _X, "prim": "r2"}

V_EL = verif("c7-v-el", 1,
             f"În M2, coeficientul ratei migranților este {ro(B4['log_la_mie'])}. Ce înseamnă?",
             [f"La fiecare migrant în plus, SCI crește cu {ro(B4['log_la_mie'])}",
              "O rată cu 10% mai mare merge cu un SCI cu aproximativ 4% mai mare",
              "Migrația produce un SCI mai mare"],
             "Ambele variabile sunt pe logaritm, deci coeficientul se citește în procente. Este o asociere, nu o cauză.",
             indiciu="SCI și rata sunt amândouă pe logaritm. Pe logaritmi, schimbările se citesc în procente, nu în unități.")

MANUAL_EL = (
   "<h2>Interpretarea coeficienților</h2>"
   "<p>Când variabila dependentă și predictorul sunt amândouă pe logaritm, coeficientul este o elasticitate: arată "
   "cu cât la sută se schimbă SCI la o schimbare de 1% a predictorului. Cu rata migranților (0,44): o rată cu 1% "
   "mai mare merge cu un SCI cu aproximativ 0,44% mai mare; o rată cu 10% mai mare, cu un SCI cu aproximativ 4% mai "
   "mare, la aceeași distanță și graniță. Pentru schimbări mari, citirea exactă este "
   "multiplicativă: dacă predictorul se înmulțește cu k, SCI se înmulțește cu k la puterea coeficientului. Pentru o "
   "variabilă binară (granița), SCI se înmulțește cu 10 la puterea coeficientului (cu log10).</p>"
   + ix("edElasticitate", "SCI prezis de M2, când se schimbă predictorii", {"coef": B4})
   + tabel(["Predictorul", "Coeficientul", "Intervalul de 95%", "Citirea"], [
       ["log distanța", ro(B4["log_distanta"]), f"{ro(CI['log_distanta'][0])} … {ro(CI['log_distanta'][1])}",
        f"distanța dublă: SCI × {ro(2 ** B4['log_distanta'])} ({pct(2 ** B4['log_distanta'])} mai puțin)"],
       ["log migranți la mie", ro(B4["log_la_mie"]), f"{ro(CI['log_la_mie'][0])} … {ro(CI['log_la_mie'][1])}",
        f"rata dublă: SCI × {ro(2 ** B4['log_la_mie'])} ({pct(2 ** B4['log_la_mie'])} mai mult)"],
       ["granița", ro(B4["granita"]), f"{ro(CI['granita'][0])} … {ro(CI['granita'][1])}",
        f"țări vecine: SCI × {ro(10 ** B4['granita'])}; intervalul conține 0"]])
   + "<p><b>Care predictor contează mai mult?</b> Coeficienții de mai sus nu se compară direct: un pas de 1 pe "
     "logaritm înseamnă o înmulțire cu 10, iar între perechile de țări distanța variază de obicei de 1,9 ori, rata "
     "migranților de 5 ori. Pe scoruri z (slide-ul cu scalarea), pasul devine o diferență tipică între perechi:</p>"
   + tabel(["Predictorul", "Coeficientul în M2", "Coeficientul pe scoruri z"], [
       ["log distanța", ro(B4["log_distanta"]), ro(M["m4z"]["z_log_distanta"])],
       ["log migranți la mie", ro(B4["log_la_mie"]), ro(M["m4z"]["z_log_la_mie"])],
       ["granița (0/1, nescalată)", ro(B4["granita"]), ro(M["m4z"]["granita"])]])
   + "<p>La o diferență tipică, migrația contează de aproape patru ori mai mult decât distanța. Granița rămâne 0/1: "
     "o variabilă binară nu se scalează.</p>"
   + "<p>Intervalul de încredere arată valorile plauzibile ale coeficientului. Intervalele distanței și ale migrației "
     "nu conțin 0: aceste asocieri se deosebesc de întâmplare (aceeași idee ca valoarea p din C6). Intervalul graniței "
     "conține 0: pe aceste perechi de țări, la aceeași distanță și migrație, efectul graniței nu se distinge clar. "
     "Intervalele sunt, în plus, prea înguste: aceeași țară apare în multe perechi, deci perechile nu sunt independente "
     "(C6). Corecția uzuală sunt erorile standard grupate pe țară.</p>"
   + V_EL
   + glosar("elast", "ic"))


sl("s10", "Modelul", "Rezultatul complet",
   "<h2>Rezultatul complet al modelului</h2>"
   + concept(f"Trei blocuri: modelul în ansamblu ({gl('r2a', 'R² ajustat')}, testul F, AIC), coeficienții (eroarea "
             "standard, t, valoarea p, intervalul) și diagnosticul reziduurilor. Un clic pe un câmp îl explică.")
   + ix("edSumar", "m2.summary(), pe datele cursului", SUMAR)
   + vede("Modelul explică 53%; rata migranților (t = 13,7) și distanța (p = 0,004) contează; granița nu (p = 0,21). "
          "Reziduurile nu sunt perfect normale."),
   manual=
   "<h2>Rezultatul complet al modelului</h2>"
   "<p><code>m2.summary()</code> dă tot rezultatul modelului, în trei blocuri. Sus, modelul în ansamblu: numărul de "
   "observații, R² și R² ajustat, testul F, criteriile de comparație AIC și BIC. La mijloc, coeficienții, fiecare cu "
   "eroarea standard, statistica t, valoarea p și intervalul de încredere de 95%. Jos, diagnosticul reziduurilor: "
   "normalitatea (Omnibus, Jarque-Bera, asimetria, aplatizarea), autocorelația (Durbin-Watson) și numărul de "
   "condiționare. Un clic pe fiecare câmp îl explică, cu valoarea lui pe datele cursului.</p>"
   + ix("edSumar", "m2.summary(), pe datele cursului", SUMAR)
   + tabel(["", "coef", "std err", "t", "P>|t|", "interval 95%", "Citirea"], [
       ["Intercept", ro(_C["Intercept"]["b"]), ro(_C["Intercept"]["se"]), ro(_C["Intercept"]["t"], 1), "0,000",
        f"{ro(_C['Intercept']['lo'])} … {ro(_C['Intercept']['hi'])}", "extrapolare, fără sens direct"],
       ["log_distanta", ro(_C["log_distanta"]["b"]), ro(_C["log_distanta"]["se"]), ro(_C["log_distanta"]["t"], 1),
        ro(_C["log_distanta"]["p"], 3), f"{ro(_C['log_distanta']['lo'])} … {ro(_C['log_distanta']['hi'])}", "semnificativ"],
       ["log_la_mie", ro(_C["log_la_mie"]["b"]), ro(_C["log_la_mie"]["se"]), ro(_C["log_la_mie"]["t"], 1), "0,000",
        f"{ro(_C['log_la_mie']['lo'])} … {ro(_C['log_la_mie']['hi'])}", "cel mai puternic și cel mai precis"],
       ["granita", ro(_C["granita"]["b"]), ro(_C["granita"]["se"]), ro(_C["granita"]["t"], 1), ro(_C["granita"]["p"], 3),
        f"{ro(_C['granita']['lo'])} … {ro(_C['granita']['hi'])}", "nesemnificativ"]])
   + "<p>Interpretarea, ca într-un raport: pe 263 de perechi de țări europene, un model liniar cu distanța, rata "
     "migranților și granița comună explică 53% din variația lui log SCI (R² ajustat 0,52). Migrația este predictorul "
     "cel mai puternic: la aceeași distanță și graniță, o rată a migranților de două ori mai mare merge cu un SCI cu "
     "aproximativ 36% mai mare (coeficient 0,44, interval de 95% între 0,38 și 0,51). Distanța rămâne semnificativă, "
     "dar mult mai slabă decât părea singură: coeficientul ei scade de la −0,76 în M1 la −0,30 în M2. Granița comună "
     "nu adaugă un efect clar odată ce distanța și migrația sunt în model (p = 0,21). Rezultatele sunt asocieri între "
     "perechi de țări, nu efecte cauzale; reziduurile nu sunt perfect normale, iar erorile standard sunt subestimate, "
     "pentru că aceeași țară apare în multe perechi.</p>"
   + "<p><b>Codul.</b></p>"
   + cod('formula_m2 = "log_sci ~ log_distanta + log_la_mie + granita"   # variabila explicată ~ predictorii\n'
         'm2 = smf.ols(formula_m2, data=date).fit()    # ols: cele mai mici pătrate; fit: estimarea\n'
         'm2.summary()                                 # tot rezultatul, în trei blocuri')
   + MANUAL_EL
   + glosar("r2a")
   + caiet("5.1 și 5.2", [
       "<code>m2.summary()</code>: cele trei blocuri, cu explicațiile din caiet.",
       "Interpretarea, ca într-un raport: un paragraf care spune mărimea efectelor, incertitudinea și limitele."],
       "<code>m_numar.summary()</code>: modelul cu numărul de migranți; cum se schimbă R² ajustat și AIC?"))


# ===========================================================================
#  D. Reziduurile
# ===========================================================================

HARTA_MODEL = {
    "niveluri": ["tari"], "nivel": "tari", "masura": "model", "ales": "RO", "masuri": ["model", "sci", "migr"],
    "povesti": [
        {"t": "România", "nivel": "tari", "masura": "model", "ales": "RO",
         "text": "Ungaria, Austria și Irlanda sunt peste model; Italia, cu cei mai mulți migranți români, este sub. "
                 "Pentru Ungaria, explicația probabilă este minoritatea maghiară, pe care modelul nu o include."},
        {"t": "Turcia", "nivel": "tari", "masura": "model", "ales": "TR",
         "text": "Aproape toate perechile cu Turcia sunt mult sub model. Explicații posibile: limba, profilul "
                 "utilizatorilor Facebook; niciuna nu este în model."},
        {"t": "Islanda", "nivel": "tari", "masura": "model", "ales": "IS",
         "text": "Peste model cu aproape toate țările: o țară mică, deci un numitor mic, ca Svalbard în C6."},
    ]}

V_CONC = verif("c7-v-conc", 1,
               "Perechile cu mai mulți migranți sunt mai legate. De ce nu putem spune că migrația produce legăturile?",
               ["Pentru că R² este sub 1",
                "Pentru că legăturile pot atrage și ele migrație: oamenii pleacă unde au deja cunoscuți",
                "Pentru că avem doar 263 de perechi"],
               "Relația poate merge în ambele sensuri, iar SCI e măsurat o singură dată: direcțiile nu se pot separa.",
               indiciu="Gândiți-vă la ordinea lucrurilor: întâi pleacă oamenii și apoi apar prieteniile, sau invers?")

sl("s12", "Reziduurile", "Peste și sub model",
   "<h2>Reziduurile: unde greșește modelul</h2>"
   + concept("Reziduul este SCI-ul observat față de cel prezis de M2. Peste 1×: perechea e mai legată decât prezic "
             "distanța, migrația și granița; sub 1×, mai puțin. Clic pe o țară o alege.")
   + ix("harta", "SCI față de model, pe țări", HARTA_MODEL)
   + vede("Italia, cu cei mai mulți migranți români, este sub model (0,7×); Ungaria peste (1,9×): ce lipsește din model."),
   manual=
   "<h2>Reziduurile</h2>"
   "<p>Reziduul este diferența dintre log SCI observat și log SCI prezis de M2; 10 la puterea reziduului spune de câte "
   "ori este perechea mai legată (sau mai puțin legată) decât prezice modelul. Pe hartă, după alegerea unei țări, "
   "fiecare partener se colorează după raportul lui.</p>"
   + ix("harta", "SCI față de model, pe țări", HARTA_MODEL)
   + "<p><b>Codul.</b></p>"
   + cod('date["prezis"] = m2.fittedvalues           # log SCI prezis de M2, pentru fiecare pereche\n'
         'date["reziduu"] = m2.resid                 # observat - prezis, pe logaritm\n'
         'cu_ro = date[date["pereche"].str.contains("RO")].copy()       # perechile cu România\n'
         'cu_ro["de_cate_ori"] = 10 ** cu_ro["reziduu"]                 # observat / prezis')
   + "<p>Reziduurile mari nu sunt erori de calcul. Ele arată factori pe care modelul nu îi include: o minoritate "
     "(Ungaria și România), o limbă comună, o particularitate a măsurării (Islanda și Luxemburgul, țări mici). Pentru "
     "proiect, ele sunt partea cea mai informativă: fiecare reziduu mare este o întrebare de cercetare.</p>"
   + tabel(["Se poate afirma", "Nu se poate afirma"], [
       ["perechile cu o rată mai mare de migrație sunt mai legate, la aceeași distanță și graniță",
        "migrația produce legăturile"],
       ["modelul explică puțin peste jumătate din variația lui log SCI", "legăturile sunt explicate"],
       ["la aceeași distanță și migrație, efectul graniței nu se distinge clar", "granițele nu contează"],
       ["rezultatele descriu perechi de țări", "rezultatele descriu persoane"]])
   + V_CONC
   + caiet("6", [
       "<code>m2.fittedvalues</code> și <code>m2.resid</code>; graficul observat față de prezis, cu linia de 45°: "
       "distanța pe verticală până la linie este reziduul.",
       "Perechile cele mai mult sub și peste model; partenerii României, cu <code>10 ** reziduu</code>.",
       "Harta reziduurilor României, pe contururile țărilor; reziduul mediu pe țară: țările mari sub model, cele "
       "mici peste."],
       "Partenerii Turciei, de la cel mai mult sub model la cel mai mult peste."))


TAB_M3 = tabel(["", "M2: coef.", "M2: t grupat", "M3: coef.", "M3: t grupat"], [
    ["log distanța", "−0,30", "−1,4", "−0,30", "−3,8"],
    ["log migranți la mie", "0,44", "8,2", "0,57", "21,3"],
    ["granița", "0,11", "1,0", "0,15", "2,9"],
    ["R²", "0,53", "", "0,92", ""]])

HARTA_M3 = {
    "niveluri": ["tari"], "nivel": "tari", "masura": "model3", "ales": "RO", "masuri": ["model", "model3"],
    "povesti": [
        {"t": "România", "nivel": "tari", "masura": "model3", "ales": "RO",
         "text": "Cu M3, Islanda și Luxemburgul nu mai ies peste model, iar Italia ajunge exact cât prezice modelul "
                 "(×1,0). Rămân peste model Ungaria (×2,9, minoritatea maghiară) și Irlanda (×2,1)."},
        {"t": "Islanda", "nivel": "tari", "masura": "model3", "ales": "IS",
         "text": "În M2, Islanda era peste model cu aproape toți partenerii: un efect de mărime. Cu efectele de "
                 "țară, el dispare; rămân legăturile cu țările nordice."},
        {"t": "Cehia", "nivel": "tari", "masura": "model3", "ales": "CZ",
         "text": "Cehia și Slovacia: de 2,8 ori peste M3. Fostul stat comun nu este în model."},
        {"t": "Turcia", "nivel": "tari", "masura": "model3", "ales": "TR",
         "text": "În M2, Turcia era sub model cu aproape toți. Cu efectele de țară, diferențele dintre partenerii ei "
                 "devin mici."},
    ]}

sl("s13", "Modele mai bune", "Efectele de țară",
   "<h2>Un model mai bun: efectele de țară</h2>"
   + concept("Unele țări sunt legate puternic de aproape oricine (Islanda, Luxemburgul: țări mici), altele slab "
             "(Turcia). M2 nu știe asta și greșește la fel pentru toți partenerii lor. <b>Efectele de țară</b> dau "
             "fiecărei țări nivelul ei de pornire; apoi modelul (M3) compară partenerii aceleiași țări între ei. "
             "Butoanele comută între M2 și M3.")
   + ix("harta", "SCI față de model: M2 și M3, pe țări", HARTA_M3)
   + vede("Cu M3, efectul de mărime dispare. Rămân legăturile cu o explicație proprie: Ungaria-România ×2,9, "
          "Cehia-Slovacia ×2,8, Luxemburg-Portugalia ×4,5."),
   manual=
   "<h2>Un model mai bun: efectele de țară</h2>"
   "<p><b>Ideea, cu o analogie.</b> Doi profesori notează aceeași clasă: unul dă note mari tuturor, altul note "
   "mici. Ca să afli cine învață mai bine, compari elevii <i>aceluiași</i> profesor, nu notele de la profesori "
   "diferiți. Aici „profesorii” sunt țările: Islanda are SCI mare cu aproape oricine (o țară mică, deci un numitor "
   "mic), Turcia mic. Efectele de țară dau fiecărei țări nivelul ei, iar coeficienții se citesc apoi în interiorul "
   "țării: pentru România, de exemplu, se compară partenerii României între ei.</p>"
   "<p>Reziduul mediu pe țară (caietul, secțiunea 6) a arătat exact asta: țările mari (Turcia, Franța, Spania, "
   "Italia) sunt sub M2, cele mici (Islanda, Luxemburgul) peste. Efectele fixe rezolvă problema fără să măsoare "
   "cauzele (folosirea Facebook, mărimea, limba): fiecare țară primește o variabilă 0/1, egală cu 1 dacă apare în "
   "pereche; una rămâne referința.</p>"
   "<p><b>Codul.</b></p>"
   + cod('for t in tarile[1:]:                                   # fiecare țară, în afară de referință\n'
         '    date["fe_" + t] = date["pereche"].str.contains(t).astype(int)   # 1 dacă țara e în pereche\n'
         'm3 = smf.ols(formula_m2 + efecte, data=date).fit()      # formula lui M2, plus variabilele de țară\n'
         'm3g = smf.ols(formula_m3, data=date).fit(cov_type="cluster", cov_kwds={"groups": grupe})   # erorile grupate')
   + ix("harta", "SCI față de model: M2 și M3, pe țări", HARTA_M3)
   + TAB_M3
   + "<p>R² urcă la 0,92, dar creșterea vine mai ales din variabilele de țară; ce contează sunt cei trei coeficienți. "
     "Două verificări însoțesc modelul. <b>VIF</b>, calculat pentru cele trei variabile cu efectele de țară printre "
     "ceilalți predictori, crește (distanța la aproximativ 3,8) dar rămâne sub 5. <b>Erorile standard grupate</b> pe "
     "țara 1 și pe țara 2 (<code>cov_type=\"cluster\"</code>) țin cont că perechile cu o țară comună seamănă între ele. "
     "Cu ele, în M2 distanța și granița nu se mai deosebesc de întâmplare; în M3 toate trei trec pragul.</p>"
   + "<p>Harta după M3 arată ce rămâne: reziduurile nu mai urmează mărimea țărilor, ci legături particulare, fiecare "
     "cu o explicație de verificat (o minoritate, un fost stat comun, o comunitate de migranți).</p>"
   + caiet("7", [
       "Variabilele de țară, cu o buclă; <code>m3</code> cu formula lui M2 plus efectele.",
       "VIF-ul celor trei variabile, cu efectele de țară; erorile grupate (<code>cov_type=\"cluster\"</code>) pentru M2 și M3.",
       "Harta partenerilor României, după M2 și după M3."]))


# ===========================================================================
#  M4: reziduurile cele mai mici
# ===========================================================================

OP = {"op": M["op"]}

TAB_M4 = tabel(["Variabila", "Coeficientul", "t grupat", "VIF", "De ce"], [
    ["log distanța", "−0,22", "−3,7", "4,0", "distanța rămâne o barieră"],
    ["log număr de migranți", "0,63", "25,3", "3,8", "câți oameni fac legătura; mărimea țărilor e deja în efectele de țară"],
    ["granița", "0,14", "3,6", "2,2", "vecinătatea"],
    ["fost stat comun", "0,27", "4,0", "1,4", "Cehoslovacia, URSS: rude, colegi, limbă apropiată"]])

TAB_REZ_M = tabel(["", "R²", "greșește de obicei", "perechi prezise sub ×1,5"], [
    ["M2", "0,53", "× 2,21", "41%"],
    ["M3", "0,92", "× 1,38", "79%"],
    ["<b>M4</b>", "<b>0,94</b>", "<b>× 1,33</b>", "<b>87%</b>"]])

sl("s16", "Modele mai bune", "Reziduuri mici",
   "<h2>M4: reziduurile cele mai mici</h2>"
   + concept("Două schimbări cu motiv teoretic: <b>numărul</b> de migranți în locul ratei (mărimea țărilor e deja "
             "în efectele de țară) și <b>fostul stat comun</b> (Cehia-Slovacia, țările baltice). Fiecare punct e o "
             "pereche: cu cât e mai aproape de diagonală, cu atât reziduul e mai mic.")
   + ix("edObsPrez", "SCI observat față de prezis: M2, M3, M4", OP),
   manual=
   "<h2>M4: reziduurile cele mai mici</h2>"
   "<p>Reziduurile lui M3 sugerează două schimbări. Fiecare are o justificare teoretică, stabilită înainte de a "
   "vedea efectul asupra reziduurilor.</p>"
   "<p><b>Numărul de migranți în locul ratei.</b> În M2, rata era mult mai bună decât numărul (R² 0,53 față de "
   "0,26), pentru că numărul depinde de mărimea țărilor. În M3, mărimea fiecărei țări este deja în efectele de țară. "
   "Rămâne ce măsoară numărul: câți oameni fac legătura între cele două țări. Construcția potrivită a unei variabile "
   "depinde deci de model.</p>"
   "<p><b>Fostul stat comun.</b> Cehia-Slovacia este de 2,8 ori peste M3. Cehoslovacia s-a despărțit în 1993; "
   "Estonia, Letonia și Lituania au făcut parte din URSS până în 1991. Rudele, colegii și limba înțeleasă reciproc "
   "nu dispar odată cu statul. Variabila este 0/1, ca granița.</p>"
   + TAB_M4
   + "<p>Toate patru au semnul așteptat, |t| peste 3 cu erorile grupate și VIF sub 5. <b>Cât de mici sunt "
     "reziduurile?</b> Abaterea standard a reziduurilor este pe logaritm; 10 la puterea ei spune de câte ori greșește "
     "de obicei modelul, în plus sau în minus.</p>"
   + TAB_REZ_M
   + ix("edObsPrez", "SCI observat față de prezis: M2, M3, M4", OP)
   + "<p>Cea mai mare parte a câștigului vine din efectele de țară (M3); M4 îl rafinează. Rămân departe "
     "Luxemburg-Portugalia (×3,3) și Ungaria-România (×3,1). O variabilă „minoritate” pentru Ungaria-România ar "
     "micșora reziduul, dar ar fi aleasă după ce s-a văzut reziduul: ar învăța datele pe de rost. O variabilă intră "
     "în model pentru un motiv teoretic stabilit dinainte. Limba oficială comună are un astfel de motiv, dar adăugată "
     "la M4 are coeficientul aproape 0 (t ≈ 1): perechile cu limbă comună sunt vecine și cu mulți migranți, iar "
     "granița și migrația au preluat deja efectul.</p>"
   + "<p><b>Codul.</b></p>"
   + cod('fost_stat = ["CZ-SK", "EE-LT", "EE-LV", "LT-LV"]                 # Cehoslovacia; țările baltice\n'
         'date["stat_comun"] = date["pereche"].isin(fost_stat).astype(int)   # 1 pentru aceste perechi\n'
         'formula_m4 = "log_sci ~ log_distanta + log_migranti + granita + stat_comun" + efecte\n'
         'm4 = smf.ols(formula_m4, data=date).fit(cov_type="cluster", cov_kwds=grupuri)\n'
         '10 ** m4.resid.std()                       # de câte ori greșește de obicei: 1,33')
   + caiet("7.6", [
       "<code>stat_comun</code> cu <code>isin</code>; M4 cu erorile grupate; VIF cu efectele de țară.",
       "R² și „greșește de obicei de ×” pentru M2, M3, M4; graficul observat față de prezis, M2 și M4.",
       "Perechile cele mai departe de M4; harta partenerilor României după M4."],
       "Limba oficială comună adăugată la M4: coeficientul și t-ul ei."))

HARTA_M4 = {
    "niveluri": ["tari"], "nivel": "tari", "masura": "model4", "ales": "RO", "masuri": ["model", "model3", "model4"],
    "povesti": [
        {"t": "România", "nivel": "tari", "masura": "model4", "ales": "RO",
         "text": "După M4, aproape toți partenerii sunt între ×0,7 și ×1,4. Rămân peste model Ungaria (×3,1, "
                 "minoritatea maghiară), Irlanda și Germania (×1,8)."},
        {"t": "Cehia", "nivel": "tari", "masura": "model4", "ales": "CZ",
         "text": "Cehia-Slovacia scade de la ×2,8 (M3) la ×1,35: fostul stat comun explică legătura. Rămâne "
                 "Cehia-Estonia (×2,1)."},
        {"t": "Portugalia", "nivel": "tari", "masura": "model4", "ales": "PT",
         "text": "Luxemburg-Portugalia rămâne cea mai mare abatere (×3,3): migrația portugheză în Luxemburg este "
                 "foarte mare raportat la o țară mică."},
        {"t": "Turcia", "nivel": "tari", "masura": "model4", "ales": "TR",
         "text": "În M2, Turcia era mult sub model cu aproape toți partenerii. După M4, diferențele sunt mici: "
                 "sub model rămân Ungaria (×0,55) și Cehia."},
    ]}

sl("s17", "Modele mai bune", "Harta după M4",
   "<h2>Ce rămâne după M4</h2>"
   + concept("Aceeași hartă a reziduurilor, pentru cele trei modele: butoanele comută între M2, M3 și M4. Clic pe "
             "o țară o alege; culoarea partenerului arată de câte ori e perechea peste sau sub model.")
   + ix("harta", "SCI față de model: M2, M3 și M4, pe țări", HARTA_M4)
   + vede("De la M2 la M4, harta se stinge: reziduurile mari dispar. Rămân câteva legături cu o explicație proprie: "
          "Ungaria-România, Luxemburg-Portugalia."),
   manual=
   "<h2>Ce rămâne după M4</h2>"
   "<p>Pe hartă, după alegerea unei țări, fiecare partener se colorează după reziduul perechii: verde, peste "
   "model; cărămiziu, sub. Comparând cele trei modele pentru aceeași țară se vede ce a preluat fiecare: M3, efectul de "
   "mărime (Islanda, Luxemburgul); M4, fostul stat comun (Cehia-Slovacia).</p>"
   + ix("harta", "SCI față de model: M2, M3 și M4, pe țări", HARTA_M4)
   + "<p><b>Codul.</b> Ca în secțiunea 7.5 a caietului, cu reziduurile lui M4:</p>"
   + cod('cu_ro["reziduu_m4"] = m4.resid                       # reziduul fiecărei perechi cu România\n'
         'reziduu_m4_ro = cu_ro.set_index("partener")["reziduu_m4"]\n'
         'contur["reziduu_m4"] = contur["tara"].map(reziduu_m4_ro)   # pe conturul fiecărui partener\n'
         'contur.plot(column="reziduu_m4", cmap="RdBu", vmin=-0.5, vmax=0.5, legend=True)')
   + "<p>Un reziduu mic nu înseamnă că modelul a găsit cauza: înseamnă doar că perechea se comportă ca perechile "
     "asemănătoare ei. Reziduurile mari rămase sunt întrebări de cercetare pentru proiect.</p>")


_GRUPE = tabel(["Tipul de regiune", "Regiuni", "PIB/loc.", "Studii sup. (%)", "Șomaj (%)", "Vârsta medie", "Densitate", "Exemple"], [
    ["metropolitane", "36", "60.100", "50,0", "4,7", "41,4", "740", "capitalele: Praga, Bratislava, Budapesta, Varșovia, București-Ilfov, Madrid"],
    ["dezvoltate", "119", "38.300", "34,6", "3,7", "45,1", "139", "Germania, Austria, nordul Italiei, Polonia vestică"],
    ["periferice, îmbătrânite", "90", "27.350", "27,9", "7,7", "45,8", "65", "Grecia, sudul Spaniei și al Italiei, România fără București, Bulgaria"],
    ["tinere, cu șomaj ridicat", "21", "20.500", "22,8", "10,3", "34,2", "140", "Turcia, teritoriile franceze de peste mări, Ceuta"]])

HARTA_TIP = {
    "niveluri": ["regiuni"], "nivel": "regiuni", "masura": "tip", "ales": "RO32", "masuri": ["tip"],
    "povesti": [
        {"t": "România", "nivel": "regiuni", "masura": "tip", "ales": "RO32",
         "text": "București-Ilfov intră cu metropolele; celelalte șapte regiuni ale României, cu periferiile îmbătrânite."},
        {"t": "Metropolele", "nivel": "regiuni", "masura": "tip", "ales": "CZ01",
         "text": "Praga, Bratislava, Budapesta, Varșovia, Madrid: capitalele ies împreună, deși algoritmul nu știe nimic "
                 "despre hartă."},
    ]}

sl("s6", "Gruparea", "Tipurile de regiuni",
   "<h2>Extragerea: gruparea regiunilor</h2>"
   + concept(f"{gl('cluster', 'Gruparea')} rezumă mai mulți indicatori într-o categorie: tipul de regiune. "
             f"{gl('kmeans')} pune fiecare regiune la cel mai apropiat centru. Distanța se calculează pe toți indicatorii "
             "deodată, deci scorul z este obligatoriu.")
   + ix("harta", "Cele patru tipuri de regiuni (k-means)", HARTA_TIP)
   + vede("Metropolele (capitalele, inclusiv București-Ilfov), regiunile dezvoltate (Germania, Austria, nordul Italiei), "
          "periferiile îmbătrânite (sudul Europei, România fără București) și regiunile tinere cu șomaj ridicat (Turcia)."),
   manual=
   "<h2>Extragerea: gruparea regiunilor</h2>"
   "<p>Extragerea rezumă mai mulți indicatori într-o singură variabilă. "
   f"{gl('pca')} dă un scor numeric (de exemplu, un scor al dezvoltării din PIB, studii și șomaj); gruparea dă o "
   "categorie: regiunile asemănătoare pe toți indicatorii ajung în aceeași grupă. Rezultatul este o variabilă "
   "derivată nouă, tipul de regiune, utilă unui proiect pe regiuni.</p>"
   "<p>Algoritmul k-means alege k centre, pune fiecare regiune la cel mai apropiat centru, mută fiecare centru în "
   "media regiunilor lui și repetă până nu se mai schimbă nimic. Pornirea este aleatoare, deci se repornește de mai "
   "multe ori (<code>n_init</code>), iar <code>random_state</code> face rezultatul reproductibil. Distanța folosește "
   "toți indicatorii deodată: fără scorul z, indicatorul cu valorile cele mai mari (PIB-ul, în euro) decide singur "
   "grupele. În graficul de mai jos, pe doi indicatori, butonul „valorile inițiale” arată efectul.</p>"
   + ix("edKmeans", "Regiunile după PIB și studii, în k grupe", _REG)
   + "<p>Numărul de grupe este o decizie. "
     f"{gl('inertia', 'Inerția')} (suma distanțelor la pătrat până la centrul grupei) scade mereu când k crește; se "
     "caută punctul după care scade mult mai încet, cotul. Pe datele cursului cotul nu este foarte clar; k = 4 dă "
     "grupe care se pot descrie. În caiet, gruparea se face pe cinci indicatori (PIB, studii, șomaj, vârsta medie, "
     "log densitatea), pe cele 266 de regiuni care îi au pe toți:</p>"
   + _GRUPE
   + ix("harta", "Cele patru tipuri de regiuni (k-means)", HARTA_TIP)
   + "<p><b>Codul.</b></p>"
   + cod('z = scor_z(reg[indicatori])                       # cei cinci indicatori, pe aceeași scară\n'
         'kmeans = KMeans(n_clusters=4, n_init=10, random_state=1)   # 4 grupe; 10 porniri; rezultat reproductibil\n'
         'reg["grupa"] = kmeans.fit(z).labels_                # grupa fiecărei regiuni\n'
         'reg.groupby("grupa")[initiali].median()           # profilul grupelor, pe scara inițială')
   + "<p>Numerele grupelor sunt doar etichete și pot ieși în altă ordine; grupele se numesc după profil. Ca la "
     "comunitățile din C6, gruparea arată <i>că</i> regiunile se aseamănă, nu <i>de ce</i>: capitalele ies împreună, "
     "deși algoritmul nu știe nimic despre țări sau hartă.</p>"
   + glosar("cluster", "kmeans", "inertia", "pca")
   + caiet("8", [
       "<code>reg</code>: regiunile cu toți cei cinci indicatori; densitatea pe logaritm; scorul z.",
       "Inerția pentru k de la 1 la 8, într-un grafic (cotul).",
       "<code>KMeans(n_clusters=4, n_init=10, random_state=1)</code>; profilul grupelor cu "
       "<code>groupby(\"grupa\").median()</code>; harta grupelor."],
       "Aceeași grupare fără scorul z: ce indicator decide grupele? Apoi <code>n_clusters=3</code> și <code>6</code>."))




HARTA_C7 = {
    "niveluri": ["regiuni"], "nivel": "regiuni", "masura": "c7", "ales": "RO42", "masuri": ["c7", "com"],
    "povesti": [
        {"t": "România, în două", "nivel": "regiuni", "masura": "c7", "ales": "RO42",
         "text": "Vestul și Centrul (Banatul și Transilvania) intră în spațiul dunărean, cu Ungaria, Austria și sudul "
                 "Germaniei; celelalte regiuni ale României intră cu Italia și Spania."},
        {"t": "Diaspora turcă", "nivel": "regiuni", "masura": "c7", "ales": "DEA1",
         "text": "Vestul și nordul Germaniei sunt în aceeași comunitate cu Turcia: migrația turcă de după 1960."},
        {"t": "Vestul francofon", "nivel": "regiuni", "masura": "c7", "ales": "PT11",
         "text": "Portugalia cu Franța, Luxemburgul și Valonia: limba franceză și migrația portugheză."},
        {"t": "Comparația cu C6", "nivel": "regiuni", "masura": "com", "ales": "RO42",
         "text": "Pe SCI brut (C6), comunitățile urmau, în mare, țările. După model, ele trec peste granițe."},
    ]}

TAB_REZ = tabel(["Rezoluția", "Comunități", "Stabilitatea (ARI între rulări)", "ARI cu țara"], [
    ["0,5", "1", "1,00 (fără informație)", "0"],
    ["0,75", "3", "0,90", "0,17"],
    ["<b>1</b>", "<b>5</b>", "<b>0,93</b>", "<b>0,25</b>"],
    ["1,25", "8", "0,89", "0,30"],
    ["1,5", "13", "0,90", "0,32"]])

# Rețeaua țărilor după M3: noduri pe hartă (mediana centrelor regiunilor fiecărei țări),
# contururile țărilor ca fundal (simplificate), perechile cu reziduul lui M3 (log10).
def _pct(d):
    """Punctele unui contur SVG „M x,y x,y ... Z”, ca listă de inele."""
    inele = []
    for bucata in d.replace("Z", "").split("M"):
        pt = [tuple(map(float, q.split(","))) for q in bucata.split() if "," in q]
        if len(pt) >= 3:
            inele.append(pt)
    return inele


def _retea():
    import statistics
    ex = json.loads((RAD / "date" / "explorator.json").read_text(encoding="utf-8"))
    tari_m = sorted({t for p_ in M["rez_m3"] for t in p_.split("-")})
    centre = {}
    for r in ex["regiuni"]:
        inele = _pct(r["d"])
        if not inele:
            continue
        pt = max(inele, key=len)
        centre.setdefault(r["tara"], []).append((sum(x for x, _ in pt) / len(pt), sum(y for _, y in pt) / len(pt)))
    noduri = [{"c": t, "x": round(statistics.median(x for x, _ in centre[t])), "y": round(statistics.median(y for _, y in centre[t]))}
              for t in tari_m if t in centre]
    xs = [n["x"] for n in noduri]; ys = [n["y"] for n in noduri]
    x0, x1, y0, y1 = min(xs) - 120, max(xs) + 120, min(ys) - 100, max(ys) + 100
    contur = []
    for t in ex["tari"]:
        if t["cod"] in ("RU", "UA", "BY"):
            continue
        for inel in _pct(t["d"]):
            pt = inel[::3]
            if len(pt) >= 4:
                contur.append("M" + " ".join(f"{x:.0f},{y:.0f}" for x, y in pt) + "Z")
    perechi = [[a, b, v] for k, v in M["rez_m3"].items() for a, b in [k.split("-")]]
    return {"noduri": noduri, "perechi": perechi, "contur": contur, "cutie": [x0, y0, x1 - x0, y1 - y0]}


RETEA = _retea()

TAB_QAP = tabel(["Variabila", "Coeficientul în M2", "p, erori obișnuite", "p, QAP (rețea)"], [
    ["log distanța", "−0,30", "0,004", "0,21"],
    ["log migranți la mie", "0,44", "&lt; 0,001", "&lt; 0,001"],
    ["granița", "0,11", "0,21", "0,45"]])

sl("s15", "Rețeaua", "Rețeaua după model",
   "<h2>Rețeaua: legăturile pe care modelul nu le explică</h2>"
   + concept("Fiecare țară e un nod. Două țări se leagă dacă perechea lor e mult mai legată decât prezice M3 (de cel "
             "puțin 1,5 ori, pragul se schimbă din glisor). Ce rămâne după distanță, migrație, graniță și efectele de "
             "țară formează o rețea: legături particulare, fiecare cu o poveste.")
   + ix("edRetea", "Perechile de țări mult peste (sau sub) M3", RETEA)
   + vede("Cehia-Slovacia și țările baltice (fostul stat comun, preluat apoi de M4), Ungaria-România, "
          "Luxemburg-Portugalia. Sub model: Germania-Franța, Germania-Țările de Jos."),
   manual=
   "<h2>Rețeaua: legăturile pe care modelul nu le explică</h2>"
   "<p>Rețeaua pornește de la reziduurile lui M3. O pereche de țări devine o legătură dacă SCI-ul ei observat e de "
   "cel puțin 1,5 ori mai mare decât prezice M3 (sau, cu butonul „mai puțin legate”, de 1,5 ori mai mic). Grosimea "
   "liniei crește cu reziduul; mărimea nodului, cu numărul de legături. Cu mouse-ul pe o țară, partenerii ei.</p>"
   + ix("edRetea", "Perechile de țări mult peste (sau sub) M3", RETEA)
   + "<p>Rețeaua folosește M3, nu M4: în ea se vede de unde a venit variabila „fost stat comun” (Cehia-Slovacia, "
     "țările baltice între ele). Celelalte legături rămân ipoteze de verificat: o minoritate, o comunitate de "
     "migranți, o limbă.</p>"
   + "<p><b>Codul.</b></p>"
   + cod('date["reziduu_m3"] = m3.resid                           # reziduul fiecărei perechi în M3\n'
         'legate = date[10 ** date["reziduu_m3"] >= 1.5]          # perechile de cel puțin 1,5 ori peste M3\n'
         'R = nx.from_pandas_edgelist(legate, "tara_1", "tara_2")   # rețeaua: o legătură pe pereche\n'
         'dict(R.degree())                                         # câte legături are fiecare țară')
   + caiet("9.1", ["Rețeaua țărilor după M3: perechile mult peste model, desenate pe hartă."]))


QAP = {"qap": M["qap"], "tari": sorted({t for p_ in M["rez_m3"] for t in p_.split("-")})}

sl("s18", "Rețeaua", "Un model de rețea",
   "<h2>Un model de rețea: regresia QAP</h2>"
   + concept("În rețea, perechile aceleiași țări nu sunt independente. QAP amestecă de 1.000 de ori numele țărilor: "
             "rețeaua rămâne aceeași, legătura dintre SCI și predictori se rupe. Coeficientul real se compară cu cei "
             "1.000 de coeficienți amestecați.")
   + ix("edQAP", "Coeficienții lui M2, față de 1.000 de amestecări ale țărilor", QAP),
   manual=
   "<h2>Un model de rețea: regresia QAP</h2>"
   "<p>Perechile de țări formează o rețea: 24 de noduri, câte o legătură între fiecare două țări. Modelele liniare "
   "tratează perechile ca rânduri independente ale unui tabel; în rețea, perechile aceleiași țări seamănă între ele. "
   "<b>Regresia QAP</b> (engl. <i>quadratic assignment procedure</i>, Krackhardt, 1988) este modelul clasic de rețea "
   "pentru astfel de date: aceeași formulă ca M2, dar semnificația se calculează prin permutarea nodurilor.</p>"
   "<p>Ideea, ca la amestecarea din C6: se amestecă etichetele țărilor (Austria devine, de exemplu, Portugalia), iar "
   "fiecare pereche primește SCI-ul perechii amestecate. Structura rețelei rămâne aceeași (fiecare țară își păstrează "
   "toate legăturile, doar sub alt nume), dar legătura dintre SCI și predictori se rupe. Valoarea p este proporția "
   "amestecărilor în care coeficientul iese, în valoare absolută, cel puțin cât cel real.</p>"
   + ix("edQAP", "Coeficienții lui M2, față de 1.000 de amestecări ale țărilor", QAP)
   + TAB_QAP
   + "<p>Rezistă doar migrația. Este aceeași concluzie ca la erorile grupate pentru M2, obținută pe altă cale: când "
     "se ține cont că perechile aceleiași țări seamănă între ele, fără efectele de țară rezistă doar migrația.</p>"
   + "<p><b>Codul.</b></p>"
   + cod('for i in range(1000):\n'
         '    noile_nume = generator.permutation(tarile)          # țările, în altă ordine\n'
         '    amestec = dict(zip(tarile, noile_nume))             # fiecare țară primește numele alteia\n'
         '    ...                                                 # SCI-ul perechii amestecate, apoi M2\n'
         '    coeficienti_amestecati.append(model.params)\n'
         'amestecati = pd.DataFrame(coeficienti_amestecati)\n'
         '(amestecati["log_la_mie"].abs() >= abs(m2.params["log_la_mie"])).mean()   # p QAP')
   + caiet("9.2", ["SCI-ul fiecărei perechi, căutat după cele două coduri; 1.000 de amestecări ale țărilor.",
                   "Valoarea p QAP pentru fiecare predictor."]))


_RR = M["retea_reg"]
COMUNITATI = {"retea": {"noduri": _RR["noduri"], "brut": _RR["brut"], "model": _RR["model"]},
              "stat": _RR["stat"], "brut_stat": _RR["brut_stat"],
              "nume": ["vestul francofon", "blocul latin", "sud-estul și diaspora turcă", "spațiul dunărean",
                       "nordul și centrul-estul"],
              "culori": ["#4e79a7", "#e15759", "#f28e2b", "#59a14f", "#b07aa1"]}

sl("s19", "Rețeaua", "Comunitățile",
   "<h2>Comunitățile regiunilor: înainte și după model</h2>"
   + concept("Rețeaua celor 297 de regiuni, cu două greutăți: SCI (ca în C6) și de câte ori e perechea peste un model "
             "de bază (distanța și „aceeași țară”). Louvain caută grupurile legate între ele; rezoluția se alege prin "
             "stabilitate.")
   + ix("edComunitati", "Comunitățile Louvain pe rețeaua regiunilor", COMUNITATI),
   manual=
   "<h2>Comunitățile regiunilor: înainte și după model</h2>"
   "<p>Aceeași idee ca la țări, pe cele 44 de mii de perechi de regiuni. Un model de bază (log SCI din log distanță "
   "și „aceeași țară”, R² 0,45) dă fiecărei legături greutatea 10<sup>reziduu</sup>: de câte ori este perechea mai "
   "legată decât prezice modelul. Louvain caută apoi grupurile de regiuni legate între ele peste așteptări.</p>"
   "<p><b>Desenul.</b> Cu 44 de mii de legături, rețeaua completă ar fi o pată. Se desenează un schelet: arborele "
   "care leagă toate regiunile prin legăturile cele mai puternice, plus cele patru legături cele mai puternice ale "
   "fiecărei regiuni. Așezarea (<code>spring_layout</code>) trage regiunile legate una spre alta. Pe SCI, rețeaua "
   "se strânge în ciorchini care sunt țările; după model, ciorchinii se amestecă.</p>"
   + ix("edComunitati", "Comunitățile Louvain pe rețeaua regiunilor", COMUNITATI)
   + "<p><b>Rezoluția.</b> Sub 1, comunitățile sunt mai puține și mai mari; peste 1, mai multe și mai mici. O "
     "rezoluție bună dă comunități stabile: aproape aceleași la fiecare rulare. Stabilitatea se măsoară cu ARI între "
     "prima rulare și alte patru, cu alt seed (ARI compară două împărțiri: 1 = identice, 0 = la întâmplare).</p>"
   + TAB_REZ
   + "<p><b>Codul.</b></p>"
   + cod('m_regiuni = smf.ols("log_sci ~ log_distanta + aceeasi_tara", data=perechi).fit()\n'
         'perechi["peste_model"] = 10 ** m_regiuni.resid          # observat / prezis\n'
         'G_peste = nx.from_pandas_edgelist(perechi, "regiune_1", "regiune_2", edge_attr="peste_model")\n'
         'comunitati = louvain(G_peste, "peste_model", rezolutie=1)\n'
         'S = schelet(G_peste, "peste_model")                       # pentru desen\n'
         'nx.draw(S, nx.spring_layout(S, seed=1), node_color=[comunitati[r] for r in S.nodes])')
   + caiet("9.3-9.5", [
       "Modelul de bază pe regiuni; greutatea „peste model”; cele două rețele.",
       "Rezoluția aleasă prin stabilitate (ARI între rulări) și ARI cu țara.",
       "Cele cinci comunități pe hartă și ca rețea (schelet, <code>spring_layout</code>)."]))

sl("s20", "Rețeaua", "Harta comunităților",
   "<h2>Cinci comunități peste granițe</h2>"
   + concept("Aceleași comunități, pe hartă. Fiecare regiune are culoarea comunității ei; butonul „Comunități” "
             "arată, pentru comparație, comunitățile din C6, pe SCI brut.")
   + ix("harta", "Comunitățile rețelei „peste model”, pe regiuni", HARTA_C7)
   + vede("România se împarte: Vestul și Centrul cu spațiul dunărean (Ungaria, Austria, sudul Germaniei), celelalte "
          "regiuni cu blocul latin (Italia, Spania)."),
   manual=
   "<h2>Cinci comunități peste granițe</h2>"
   + ix("harta", "Comunitățile rețelei „peste model”, pe regiuni", HARTA_C7)
   + tabel(["Comunitatea", "Regiunile principale", "Explicația plauzibilă"], [
       ["vestul francofon", "Franța, Portugalia, Valonia, Luxemburg, Elveția romandă", "limba franceză; migrația portugheză"],
       ["blocul latin", "Italia, Spania, șase regiuni ale României", "migrația românească spre Italia și Spania"],
       ["sud-estul și diaspora turcă", "Turcia, Grecia, Bulgaria, vestul și nordul Germaniei, Țările de Jos", "migrația turcă"],
       ["spațiul dunărean", "sudul și estul Germaniei, Austria, Ungaria, fosta Iugoslavie, Vestul și Centrul României",
        "istoria comună, minoritățile germane și maghiare"],
       ["nordul și centrul-estul", "Polonia, Cehia, Slovacia, țările nordice și baltice", "migrația poloneză și baltică"]])
   + "<p>Comparate cu tipurile de regiuni din k-means, comunitățile au ARI aproape 0: regiunile nu se leagă după cât "
     "sunt de bogate sau de dense, ci după migrație, limbă și istorie. Explicațiile sunt ipoteze: rețeaua arată "
     "<i>că</i> perechile sunt mai legate decât prezice modelul, nu <i>de ce</i>.</p>"
   + "<p><b>Codul.</b></p>"
   + cod('harta["comunitate"] = harta["regiune"].map(comunitati)   # comunitatea fiecărei regiuni\n'
         'harta.plot(column="comunitate", categorical=True, cmap="Set2", legend=True)\n'
         'adjusted_rand_score(reg["grupa"], comunitati[reg.index])   # față de k-means: aproape 0'))

SURSE_C7 = surse("Documentația modelului", [
    ("statsmodels: Fitting models using R-style formulas", "https://www.statsmodels.org/stable/example_formulas.html", "smf.ols, formula, params, rsquared"),
    ("statsmodels: OLS results", "https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.RegressionResults.html", "conf_int, resid, fittedvalues"),
    ("geopandas: dissolve și sjoin", "https://geopandas.org/en/stable/docs/user_guide/aggregation_with_dissolve.html", "contururile țărilor din regiuni; vecinii"),
    ("Kuhn și Johnson: Feature Engineering and Selection", "https://bookdown.org/max/FES/", "construcția, transformarea și selecția variabilelor"),
    ("Gelman, Hill și Vehtari: Regression and Other Stories, cap. 12", "https://avehtari.github.io/ROS-Examples/", "logaritmi, scalare și interpretarea coeficienților"),
])

sl("s14", "Concluzia", "Ce se poate concluziona",
   "<h2>Ce se poate concluziona</h2>"
   "<p class=\"cheie\">Modelele compară perechi de țări (SCI, migrația și distanța sunt între țări); comunitățile "
   "compară perechi de regiuni. Niciunul nu descrie persoane.</p>"
   + tabel(["Se poate afirma", "Nu se poate afirma"], [
       ["perechile de țări cu mai mulți migranți între ele sunt mai legate, la aceeași distanță și graniță",
        "migrația produce legăturile"],
       ["comparând partenerii aceleiași țări (M4), contează distanța, numărul de migranți, granița și fostul stat comun",
        "modelul explică toate legăturile: rămân Ungaria-România, Luxemburg-Portugalia"],
       ["pe regiuni, cinci comunități trec granițele, după migrație, limbă și istorie",
        "explicațiile comunităților sunt demonstrate"]]),
   dupa=V_CONC,
   manual=
   "<h2>Ce se poate concluziona</h2>"
   "<p>Modelele compară perechi de țări: SCI-ul țărilor (calculat în C5 din regiuni), migrația și distanța sunt "
   "toate între țări. Comunitățile compară perechi de regiuni. Niciun rezultat nu descrie persoane.</p>"
   + tabel(["Se poate afirma", "Nu se poate afirma"], [
       ["perechile de țări cu mai mulți migranți între ele sunt mai legate, la aceeași distanță și graniță",
        "migrația produce legăturile"],
       ["comparând partenerii aceleiași țări (M4), contează distanța, numărul de migranți, granița și fostul stat comun",
        "efectul e același pentru fiecare țară"],
       ["unele perechi rămân mult peste model: Ungaria-România, Luxemburg-Portugalia",
        "modelul explică toate legăturile"],
       ["pe regiuni, cinci comunități trec granițele, după migrație, limbă și istorie",
        "explicațiile comunităților sunt demonstrate"]])
   + nota("De la M2 la M4",
          "Reziduurile lui M2 s-au adunat pe țări: efectele de țară le-au corectat (M3). Rețeaua reziduurilor lui M3 "
          "a arătat fostul stat comun (M4). Modelul final greșește de obicei de 1,33 ori, față de 2,2 ori în M2.", True)
   + SURSE_C7)


if __name__ == "__main__":
    L.scrie_tot()
