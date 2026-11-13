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
    ["migrația contează ca rată", "log rata migranților la mie, nu numărul"],
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
       "<code>cheie</code>: codurile țărilor în ordine alfabetică, ca „AT, RO” și „RO, AT” să fie aceeași pereche; "
       "apoi distanța ca mediană a distanțelor dintre regiuni (<code>groupby(\"cheie\")</code>).",
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
            "Scorul z se aplică ratei migranților (pe log). Ce se schimbă?",
            ["Forma distribuției: devine normală",
             "Doar unitatea: media devine 0, abaterea standard 1; forma rămâne",
             "Valorile extreme dispar",
             "Ordinea perechilor"],
            "Scorul z scade media și împarte la abaterea standard: o transformare liniară. Forma și ordinea rămân "
            "aceleași; pentru a schimba forma e nevoie de o transformare neliniară, ca logaritmul.")

sl("s5", "Variabilele", "Scalarea",
   "<h2>Scalarea: aceeași scară pentru toate</h2>"
   + concept(f"Predictorii au unități diferite, deci coeficienții lor nu se pot compara direct. {gl('z', 'Scorul z')} "
             "aduce fiecare variabilă la media 0 și abaterea standard 1: se schimbă unitatea, nu forma.")
   + ix("edScalare", "Trei variabile, înainte și după scorul z", _T)
   + vede(f"În modelul pe scoruri z, rata migranților are coeficientul {ro(M['m4z']['z_log_la_mie'])}, distanța "
          f"{ro(M['m4z']['z_log_distanta'])}: migrația contează de aproape patru ori mai mult."),
   dupa=V_Z,
   manual=
   "<h2>Scalarea</h2>"
   "<p>Scalarea aduce variabilele pe aceeași scară numerică. Scorul z, z = (x − media) / abaterea standard, este cea "
   "mai folosită: media devine 0, abaterea standard 1. Este o transformare liniară, deci nu schimbă forma "
   "distribuției și nici ordinea valorilor. Alte variante sunt scalarea min-max (între 0 și 1) și scalarea robustă "
   "(cu mediana și IQR, pentru date cu valori extreme).</p>"
   + ix("edScalare", "Trei variabile, înainte și după scorul z", _T)
   + "<p>Într-un model, scalarea are un rol precis: cu toate variabilele în scor z, fiecare coeficient spune cu câte "
     "abateri standard se schimbă log SCI când predictorul crește cu o abatere standard. Coeficienții devin "
     "comparabili:</p>"
   + tabel(["Predictorul", "Coeficientul în M2", "Coeficientul pe scoruri z"], [
       ["log distanța", ro(B4["log_distanta"]), ro(M["m4z"]["z_log_distanta"])],
       ["log migranți la mie", ro(B4["log_la_mie"]), ro(M["m4z"]["z_log_la_mie"])],
       ["granița (0/1, nescalată)", ro(B4["granita"]), ro(M["m4z"]["granita"])]])
   + V_Z
   + glosar("z")
   + caiet("2.2", [
       "Funcția <code>scor_z(x)</code>: <code>(x - x.mean()) / x.std()</code>.",
       "Coloanele <code>z_log_sci</code>, <code>z_log_distanta</code>, <code>z_log_la_mie</code>; "
       "<code>describe()</code> arată media 0 și abaterea standard 1."],
       "<code>skew()</code> înainte și după scorul z: se schimbă asimetria?"))


_GRUPE = tabel(["Tipul de regiune", "Regiuni", "PIB/loc.", "Studii sup. (%)", "Șomaj (%)", "Vârsta medie", "Densitate", "Exemple"], [
    ["metropolitane", "36", "60.100", "50,0", "4,7", "41,4", "740", "capitalele: Praga, Bratislava, Budapesta, Varșovia, București-Ilfov, Madrid"],
    ["dezvoltate", "119", "38.300", "34,6", "3,7", "45,1", "139", "Germania, Austria, nordul Italiei, Polonia vestică"],
    ["periferice, îmbătrânite", "90", "27.350", "27,9", "7,7", "45,8", "65", "Grecia, sudul Spaniei și al Italiei, România fără București, Bulgaria"],
    ["tinere, cu șomaj ridicat", "21", "20.500", "22,8", "10,3", "34,2", "140", "Turcia, teritoriile franceze de peste mări, Ceuta"]])

sl("s6", "Variabilele", "Extragerea",
   "<h2>Extragerea: gruparea regiunilor</h2>"
   + concept(f"{gl('cluster', 'Gruparea')} rezumă mai mulți indicatori într-o categorie: tipul de regiune. "
             f"{gl('kmeans')} pune fiecare regiune la cel mai apropiat centru. Distanța se calculează pe toți indicatorii "
             "deodată, deci scorul z este obligatoriu.")
   + ix("edKmeans", "Regiunile după PIB și studii, în k grupe", _REG)
   + vede("Pe cinci indicatori, patru tipuri de regiuni. București-Ilfov intră cu metropolele, restul României cu periferiile."),
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

sl("s9", "Modelul", "Trei variabile",
   "<h2>Trei variabile, fiecare cu o explicație</h2>"
   + concept(f"Un {gl('predictor', 'predictor')} intră în model doar cu un motiv teoretic și o direcție așteptată. "
             f"Fiecare {gl('coef', 'coeficient')} arată efectul lui cu ceilalți ținuți constanți: când intră "
             "predictori noi, coeficientul distanței se schimbă.")
   + ix("modele", "Coeficienții și R², M1 și M2", MODELE)
   + vede(f"Toate trei au semnul așteptat. Coeficientul distanței scade de la {ro(MOD['m1']['coef']['log_distanta'])} "
          f"la {ro(B4['log_distanta'])}; R² urcă de la {ro(MOD['m1']['r2'])} la {ro(MOD['m4']['r2'])}."),
   manual=
   "<h2>Trei variabile, două modele</h2>"
   "<p>Fiecare predictor are un motiv teoretic și o direcție așteptată, stabilite înainte de estimare:</p>"
   + TAB_TEORIE
   + "<p>Selecția (slide-ul anterior) a arătat că cele trei nu se suprapun: VIF sub 2. M1 conține doar distanța, M2 "
     f"pe toate trei. Ambele se estimează pe aceleași {M['n']} de perechi de țări: dacă eșantionul s-ar schimba de la "
     "un model la altul, diferențele dintre coeficienți ar putea veni din perechile diferite, nu din variabile.</p>"
   + ix("modele", "Coeficienții și R², M1 și M2", MODELE)
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
   + glosar("r2a")
   + caiet("5.1 și 5.3", [
       "<code>m2.summary()</code>: cele trei blocuri, cu explicațiile din caiet.",
       "Interpretarea, ca într-un raport: un paragraf care spune mărimea efectelor, incertitudinea și limitele."],
       "<code>m_numar.summary()</code>: modelul cu numărul de migranți; cum se schimbă R² ajustat și AIC?"))


V_EL = verif("c7-v-el", 2,
             f"În M2, coeficientul ratei migranților este {ro(B4['log_la_mie'])}. Ce înseamnă?",
             [f"SCI crește cu {ro(B4['log_la_mie'])} la fiecare migrant în plus",
              f"SCI crește cu {round(B4['log_la_mie'] * 100)}% la fiecare migrant la mie în plus",
              f"Rata dublă: SCI × 2<sup>{ro(B4['log_la_mie'])}</sup> = {ro(2 ** B4['log_la_mie'])}, la aceeași distanță și graniță",
              f"Migrația produce un SCI cu {round(B4['log_la_mie'] * 100)}% mai mare"],
             "Ambele părți sunt pe logaritm, deci coeficientul este o elasticitate: se citește în rapoarte, nu în "
             "unități. Este o asociere, la aceeași distanță și graniță, nu un efect cauzal.")

sl("s11", "Modelul", "Interpretarea coeficienților",
   "<h2>Ce înseamnă coeficienții</h2>"
   + concept(f"Pe logaritmi, coeficientul este o {gl('elast', 'elasticitate')}: dacă predictorul se dublează, SCI se înmulțește cu 2 "
             "la puterea coeficientului. Pentru granița (0 sau 1), cu 10 la puterea coeficientului. Glisoarele schimbă "
             "predictorii.")
   + ix("edElasticitate", "SCI prezis de M2, când se schimbă predictorii", {"coef": B4})
   + vede(f"Distanța dublă: SCI −{pct(2 ** B4['log_distanta'])}. Rata dublă: "
          f"+{pct(2 ** B4['log_la_mie'])}. Granița: +{pct(10 ** B4['granita'])}, dar "
          f"{gl('ic', 'intervalul')} ei ({ro(CI['granita'][0])} … {ro(CI['granita'][1])}) conține 0."),
   dupa=V_EL,
   manual=
   "<h2>Interpretarea coeficienților</h2>"
   "<p>Când variabila dependentă și predictorul sunt amândouă pe logaritm, coeficientul este o elasticitate: arată "
   "cu cât la sută se schimbă SCI la o schimbare de 1% a predictorului. Pentru schimbări mari, citirea exactă este "
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
   + "<p>Intervalul de încredere arată valorile plauzibile ale coeficientului. Intervalele distanței și ale migrației "
     "nu conțin 0: aceste asocieri se deosebesc de întâmplare (aceeași idee ca valoarea p din C6). Intervalul graniței "
     "conține 0: pe aceste perechi de țări, la aceeași distanță și migrație, efectul graniței nu se distinge clar. "
     "Intervalele sunt, în plus, prea înguste: aceeași țară apare în multe perechi, deci perechile nu sunt independente "
     "(C6). Corecția uzuală sunt erorile standard grupate pe țară.</p>"
   + V_EL
   + glosar("elast", "ic")
   + caiet("5.2", [
       "<code>2 ** b[\"log_distanta\"]</code> și <code>2 ** b[\"log_la_mie\"]</code>: efectul unei dublări; "
       "<code>10 ** b[\"granita\"]</code>: efectul graniței.",
       "<code>m2.conf_int()</code>: intervalele de încredere de 95%."]))


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
               "Modelul arată o asociere puternică între migrație și SCI. De ce nu se poate afirma că migrația produce "
               "legăturile?",
               ["Pentru că R² este sub 1",
                "Pentru că legăturile existente pot atrage și ele migrație, iar SCI e măsurat într-un singur moment",
                "Pentru că eșantionul are doar 263 de perechi",
                "Pentru că modelul folosește logaritmi"],
               "Relația poate funcționa în ambele sensuri: oamenii migrează unde au deja cunoscuți. Cu o singură "
               "măsurare, direcțiile nu se pot separa. Modelul arată asocieri, la aceeași distanță și graniță.")

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
   + caiet("6 și 9", [
       "<code>m2.fittedvalues</code> și <code>m2.resid</code>; graficul observat față de prezis, cu linia de 45°.",
       "Perechile cele mai mult sub și peste model; partenerii României, cu <code>10 ** reziduu</code>.",
       "Harta reziduurilor României, pe contururile țărilor; reziduul mediu pe țară: țările mari sub model, cele "
       "mici peste.",
       "Rețeaua regiunilor „peste model” (secțiunea 9): comunitățile Louvain după ce distanța și granițele sunt "
       "scoase, cu rezoluția aleasă prin stabilitate (ARI). Ies cinci blocuri peste granițe; România se împarte "
       "între blocul italo-spaniol și spațiul dunărean.",
       "Regresia QAP pe rețeaua țărilor (9.6): semnificația prin permutarea țărilor; în M2 rezistă doar migrația, "
       "ca la erorile grupate."],
       "Partenerii Turciei, de la cel mai mult sub model la cel mai mult peste; comunitățile la rezoluția 1,25."))


TAB_M3 = tabel(["", "M2: coef.", "M2: t grupat", "M3: coef.", "M3: t grupat"], [
    ["log distanța", "−0,30", "−1,4", "−0,30", "−3,8"],
    ["log migranți la mie", "0,44", "8,2", "0,57", "21,3"],
    ["granița", "0,11", "1,0", "0,15", "2,9"],
    ["R²", "0,53", "", "0,92", ""]])

sl("s13", "Modelul final", "Efectele de țară",
   "<h2>Un model mai bun: efectele de țară</h2>"
   + concept("Reziduurile se adunau în jurul câtorva țări: lipsea ceva de nivelul țării (folosirea Facebook, "
             "mărimea, limba). <b>Efectele fixe</b> dau fiecărei țări o variabilă 0/1 și absorb tot ce e constant la "
             "nivelul ei. <b>Erorile grupate</b> țin cont că perechile aceleiași țări nu sunt independente.")
   + TAB_M3
   + vede("Cu erorile grupate, în M2 doar migrația rezistă. În M3 contează toate trei: distanța dublă −19%, rata "
          "dublă +49%, granița +40%. VIF rămâne sub 5."),
   manual=
   "<h2>Un model mai bun: efectele de țară</h2>"
   "<p>Reziduul mediu pe țară (caietul, secțiunea 6) a arătat că reziduurile mari nu sunt răspândite la "
   "întâmplare: țările mari (Turcia, Franța, Spania, Italia) sunt sub model, cele mici (Islanda, Luxemburgul) peste. Lipsește deci din model un factor de "
   "nivelul țării: cât de mult se folosește Facebook, cât de mică e țara, cât de izolată e lingvistic. Efectele fixe "
   "rezolvă asta fără să măsoare acești factori: fiecare țară primește o variabilă 0/1, egală cu 1 dacă țara apare în "
   "pereche (una rămâne referința). Coeficienții se citesc atunci în interiorul țării: pentru aceeași țară, partenerii "
   "mai apropiați și cu mai mulți migranți sunt mai legați?</p>"
   + TAB_M3
   + "<p>R² urcă la 0,92, dar creșterea vine mai ales din variabilele de țară; ce contează sunt cei trei coeficienți. "
     "Două verificări însoțesc modelul. <b>VIF</b>, calculat pentru cele trei variabile cu efectele de țară printre "
     "ceilalți predictori, crește (distanța la aproximativ 3,8) dar rămâne sub 5. <b>Erorile standard grupate</b> pe "
     "țara 1 și pe țara 2 (<code>cov_type=\"cluster\"</code>) țin cont că perechile cu o țară comună seamănă între ele. "
     "Cu ele, în M2 distanța și granița nu se mai deosebesc de întâmplare; în M3 toate trei trec pragul. Concluzia lui M2 "
     "despre distanță depindea de presupunerea, greșită, că perechile sunt independente.</p>"
   + caiet("7", [
       "Variabilele de țară, cu o buclă; <code>m3</code> cu formula lui M2 plus efectele.",
       "VIF-ul celor trei variabile, cu efectele de țară; erorile grupate (<code>cov_type=\"cluster\"</code>) pentru M2 și M3."],
       "Limba oficială comună, ca variabilă 0/1: are sens teoretic, dar se suprapune cu granița."))


SURSE_C7 = surse("Documentația modelului", [
    ("statsmodels: Fitting models using R-style formulas", "https://www.statsmodels.org/stable/example_formulas.html", "smf.ols, formula, params, rsquared"),
    ("statsmodels: OLS results", "https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.RegressionResults.html", "conf_int, resid, fittedvalues"),
    ("geopandas: dissolve și sjoin", "https://geopandas.org/en/stable/docs/user_guide/aggregation_with_dissolve.html", "contururile țărilor din regiuni; vecinii"),
    ("Kuhn și Johnson: Feature Engineering and Selection", "https://bookdown.org/max/FES/", "construcția, transformarea și selecția variabilelor"),
    ("Gelman, Hill și Vehtari: Regression and Other Stories, cap. 12", "https://avehtari.github.io/ROS-Examples/", "logaritmi, scalare și interpretarea coeficienților"),
])

sl("s14", "Modelul final", "Ce se poate concluziona",
   "<h2>Ce se poate concluziona</h2>"
   + tabel(["Se poate afirma", "Nu se poate afirma"], [
       ["în interiorul aceleiași țări, partenerii cu o rată mai mare de migrație sunt mai legați (M3)",
        "migrația produce legăturile"],
       ["distanța, migrația și granița contează, cu erorile grupate", "efectul e același pentru fiecare țară"],
       ["fiecare variabilă are semnul așteptat de teorie", "legăturile sunt explicate"],
       ["rezultatele descriu perechi de țări", "rezultatele descriu persoane"]])
   + nota("De la M2 la M3",
          "Reziduurile s-au adunat în jurul câtorva țări; efectele de țară au corectat modelul, iar erorile grupate "
          "au arătat ce rezistă. Diagnosticul a schimbat modelul.", True),
   dupa=V_CONC,
   manual=
   "<h2>Ce se poate concluziona</h2>"
   + SURSE_C7)


if __name__ == "__main__":
    L.scrie_tot()
