# -*- coding: utf-8 -*-
"""
Lecția 7: Variabile derivate și model.

Planul: ingineria variabilelor în cinci etape (construcție, transformare,
scalare, extragere, selecție), după planul cursului 7 din 2025, apoi modelul,
ca în caietul 07: patru modele pe aceleași perechi de țări, interpretarea
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
    '<div><small>4 · extragerea</small><b>mai mulți indicatori într-unul</b></div>'
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
     "scalarea servește la compararea coeficienților; selecția verifică redundanța; extragerea nu este necesară, "
     "pentru că fiecare concept are o singură variabilă. Deciziile din analiza exploratorie trec direct în model:</p>"
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
       "<code>la_mie</code>: migranții împărțiți la populația celor două țări, din <code>data/raw/bm.csv</code>.",
       "<code>cheie</code>: codurile țărilor în ordine alfabetică, ca „AT, RO” și „RO, AT” să fie aceeași pereche; "
       "apoi distanța ca mediană a distanțelor dintre regiuni (<code>groupby(\"cheie\")</code>).",
       "<code>granita</code>: <code>dissolve</code>, <code>buffer(10_000)</code>, <code>sjoin</code>."],
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
   "<h2>Scalarea și extragerea</h2>"
   "<p>Scalarea aduce variabilele pe aceeași scară numerică. Scorul z, z = (x − media) / abaterea standard, este cea "
   "mai folosită: media devine 0, abaterea standard 1. Este o transformare liniară, deci nu schimbă forma "
   "distribuției și nici ordinea valorilor. Alte variante sunt scalarea min-max (între 0 și 1) și scalarea robustă "
   "(cu mediana și IQR, pentru date cu valori extreme).</p>"
   + ix("edScalare", "Trei variabile, înainte și după scorul z", _T)
   + "<p>Într-un model, scalarea are un rol precis: cu toate variabilele în scor z, fiecare coeficient spune cu câte "
     "abateri standard se schimbă log SCI când predictorul crește cu o abatere standard. Coeficienții devin "
     "comparabili:</p>"
   + tabel(["Predictorul", "Coeficientul în M4", "Coeficientul pe scoruri z"], [
       ["log distanța", ro(B4["log_distanta"]), ro(M["m4z"]["z_log_distanta"])],
       ["log migranți la mie", ro(B4["log_la_mie"]), ro(M["m4z"]["z_log_la_mie"])],
       ["granița (0/1, nescalată)", ro(B4["granita"]), ro(M["m4z"]["granita"])]])
   + f"<p><b>Extragerea</b> rezumă mai mulți indicatori ai aceluiași concept într-un singur scor, de obicei prin "
     f"{gl('pca')}: de exemplu, PIB-ul, studiile și șomajul într-un scor al dezvoltării. Pe datele SCI fiecare concept "
     "are o singură variabilă, deci extragerea nu este necesară. Înainte de PCA, variabilele se scalează "
     "obligatoriu.</p>"
   + V_Z
   + glosar("z", "pca")
   + caiet("3", [
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

sl("s6", "Variabilele", "Selecția",
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
     "migranți și rata lor): ele măsoară același concept. De aceea M2 și M3, în secțiunea următoare, folosesc fie "
     "numărul, fie rata, nu amândouă.</p>"
   + glosar("multicol", "vif")
   + caiet("4", [
       "<code>date[predictori].corr()</code>: corelațiile dintre cei trei predictori.",
       "O buclă: pentru fiecare predictor, <code>smf.ols</code> pe ceilalți, apoi <code>1 / (1 - r2)</code>."]))


# ===========================================================================
#  C. Modelul
# ===========================================================================

_PT = [[round(__import__("math").log10(r[5]), 4), round(__import__("math").log10(r[2]), 4), r[6]] for r in M["tari"]]
_M1 = MOD["m1"]["coef"]
REZ1 = {"perechi": _PT, "dy": [3, 6.6], "rm": 1.2, "a0": 6, "b0": -0.4, "r2": True,
        "et": ["țări nevecine", "țări vecine (portocaliu)"],
        "cod": 'm1 = smf.ols("log_sci ~ log_distanta", data=date).fit()\nm1.params        # nivelul și panta\ndate["reziduu"] = m1.resid'}

sl("s7", "Modelul", "Tipar și reziduu",
   "<h2>Modelul: tipar plus reziduu</h2>"
   + concept(f"{gl('model', 'Modelul liniar')} scrie fiecare valoare ca tipar plus {gl('reziduu', 'reziduu')}: log SCI = nivel + "
             f"pantă × log distanța + reziduu. {gl('mcmp', 'Cele mai mici pătrate')} aleg dreapta cu suma pătratelor "
             "reziduurilor minimă. Glisoarele mută dreapta.")
   + ix("edReziduu", "Distanța și SCI, pe perechi de țări", REZ1)
   + vede(f"Doar cu distanța: panta {ro(_M1['log_distanta'])} și {gl('r2', 'R²')} = {ro(MOD['m1']['r2'])}. Distanța "
          "explică doar o șesime din variația SCI între țări."),
   manual=
   "<h2>Modelul: tipar plus reziduu</h2>"
   "<p>Un model liniar descrie variabila dependentă ca tipar plus reziduu. Cu un singur predictor, tiparul este o "
   "dreaptă: log SCI = nivel + pantă × log distanța. Reziduul este ce rămâne: diferența dintre valoarea observată și "
   "dreaptă. Metoda celor mai mici pătrate alege nivelul și panta pentru care suma pătratelor reziduurilor este cea "
   "mai mică; în graficul de mai jos, ele se pot căuta și de mână, cu glisoarele.</p>"
   + ix("edReziduu", "Distanța și SCI, pe perechi de țări", REZ1)
   + "<p>R² compară suma pătratelor reziduurilor cu variația totală a lui log SCI: R² = 1 − (suma pătratelor "
     f"reziduurilor) / (suma pătratelor abaterilor de la medie). Cu distanța singură, R² = {ro(MOD['m1']['r2'])}. Este "
     "aceeași idee ca raportul „față de distanță” din C6: ce iese din tipar, acum față de o dreaptă.</p>"
   + glosar("model", "reziduu", "mcmp", "r2")
   + caiet("5.1", [
       "<code>smf.ols(\"log_sci ~ log_distanta\", data=date).fit()</code>: formula are variabila dependentă la stânga "
       "lui <code>~</code> și predictorii la dreapta.",
       "<code>m1.params</code> (nivelul și panta) și <code>m1.rsquared</code>."]))


def _mod(k, formula, text):
    c = MOD[k]["coef"]
    return {"nume": k.upper(), "formula": formula, "r2": MOD[k]["r2"], "text": text,
            "coef": {"dist": c.get("log_distanta"), "migr": c.get("log_migranti"),
                     "rata": c.get("log_la_mie"), "gr": c.get("granita")}}


MODELE = {
    "lim": 0.8,
    "variabile": [
        {"k": "dist", "et": "log distanța", "c": "ceas"},
        {"k": "migr", "et": "log migranți", "c": "salvie"},
        {"k": "rata", "et": "log migranți la mie", "c": "accent"},
        {"k": "gr", "et": "granița", "c": "text-2"},
    ],
    "modele": [
        _mod("m1", "log_sci ~ log_distanta", f"Doar distanța: R² = {ro(MOD['m1']['r2'])}."),
        _mod("m2", "log_sci ~ log_distanta + log_migranti",
             "Se adaugă numărul de migranți. Coeficientul distanței scade: o parte din „efectul distanței” era migrație."),
        _mod("m3", "log_sci ~ log_distanta + log_la_mie",
             f"Cu rata în locul numărului, R² crește la {ro(MOD['m3']['r2'])}. Coeficientul distanței scade din nou."),
        _mod("m4", "log_sci ~ log_distanta + log_la_mie + granita",
             "Granița adaugă foarte puțin peste distanță și migrație: R² rămâne aproape același."),
    ],
}

sl("s8", "Modelul", "Patru modele",
   "<h2>Patru modele, câte o variabilă în plus</h2>"
   + concept(f"Fiecare {gl('coef', 'coeficient')} arată efectul unui {gl('predictor', 'predictor')} cu ceilalți ținuți constanți. "
             "Când intră un predictor nou, coeficienții celorlalți se schimbă: o parte din efectul lor era al "
             "predictorului nou. Modelele se compară pe exact aceleași perechi.")
   + ix("modele", "Coeficienții și R², model cu model", MODELE)
   + vede(f"Coeficientul distanței scade de la {ro(MOD['m1']['coef']['log_distanta'])} la "
          f"{ro(B4['log_distanta'])}; cu rata migranților, R² ajunge la {ro(MOD['m4']['r2'])}."),
   manual=
   "<h2>Patru modele, pas cu pas</h2>"
   "<p>Primul model conține doar distanța; fiecare model următor adaugă sau înlocuiește o variabilă. Toate se estimează "
   f"pe aceleași {M['n']} de perechi de țări: dacă eșantionul s-ar schimba de la un model la altul, diferențele dintre "
   "coeficienți ar putea veni din perechile diferite, nu din variabile.</p>"
   + ix("modele", "Coeficienții și R², model cu model", MODELE)
   + tabel(["", "M1", "M2", "M3", "M4"], [
       ["log distanța"] + [ro(MOD[k]["coef"]["log_distanta"]) for k in ["m1", "m2", "m3", "m4"]],
       ["log migranți", "", ro(MOD["m2"]["coef"]["log_migranti"]), "", ""],
       ["log migranți la mie", "", "", ro(MOD["m3"]["coef"]["log_la_mie"]), ro(B4["log_la_mie"])],
       ["granița", "", "", "", ro(B4["granita"])],
       ["R²"] + [ro(MOD[k]["r2"]) for k in ["m1", "m2", "m3", "m4"]]])
   + "<p>Trei lecturi. Coeficientul distanței scade pe măsură ce intră migrația: țările apropiate au mai mulți "
     "migranți între ele, deci fără migrație în model distanța „preia” și o parte din efectul ei. Rata explică de două "
     "ori mai mult decât numărul de migranți (R² de la 0,25 la 0,53): efectul unei variabile derivate bine construite. "
     "Granița adaugă foarte puțin peste distanță și migrație.</p>"
   + lecturi(["bailey2020", "aronow2015", "dehaas2010"], "Modelul, în literatură")
   + glosar("coef", "predictor")
   + caiet("5.2 și 5.3", [
       "<code>m2</code>, <code>m3</code>, <code>m4</code> cu <code>smf.ols</code>; tabelul <code>modele</code>, cu R² pe "
       "ultimul rând.",
       "<code>m4z</code>: același model pe scorurile z, pentru compararea coeficienților."]))


V_EL = verif("c7-v-el", 2,
             f"În M4, coeficientul ratei migranților este {ro(B4['log_la_mie'])}. Ce înseamnă?",
             [f"SCI crește cu {ro(B4['log_la_mie'])} la fiecare migrant în plus",
              f"SCI crește cu {round(B4['log_la_mie'] * 100)}% la fiecare migrant la mie în plus",
              f"Rata dublă: SCI × 2<sup>{ro(B4['log_la_mie'])}</sup> = {ro(2 ** B4['log_la_mie'])}, la aceeași distanță și graniță",
              f"Migrația produce un SCI cu {round(B4['log_la_mie'] * 100)}% mai mare"],
             "Ambele părți sunt pe logaritm, deci coeficientul este o elasticitate: se citește în rapoarte, nu în "
             "unități. Este o asociere, la aceeași distanță și graniță, nu un efect cauzal.")

sl("s9", "Modelul", "Interpretarea coeficienților",
   "<h2>Ce înseamnă coeficienții</h2>"
   + concept(f"Pe logaritmi, coeficientul este o {gl('elast', 'elasticitate')}: dacă predictorul se dublează, SCI se înmulțește cu 2 "
             "la puterea coeficientului. Pentru granița (0 sau 1), cu 10 la puterea coeficientului. Glisoarele schimbă "
             "predictorii.")
   + ix("edElasticitate", "SCI prezis de M4, când se schimbă predictorii", {"coef": B4})
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
   + ix("edElasticitate", "SCI prezis de M4, când se schimbă predictorii", {"coef": B4})
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
   + caiet("6", [
       "<code>2 ** b[\"log_distanta\"]</code> și <code>2 ** b[\"log_la_mie\"]</code>: efectul unei dublări; "
       "<code>10 ** b[\"granita\"]</code>: efectul graniței.",
       "<code>m4.conf_int()</code>: intervalele de încredere de 95%."]))


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

sl("s10", "Reziduurile", "Peste și sub model",
   "<h2>Reziduurile: unde greșește modelul</h2>"
   + concept("Reziduul este SCI-ul observat față de cel prezis de M4. Peste 1×: perechea e mai legată decât prezic "
             "distanța, migrația și granița; sub 1×, mai puțin. Clic pe o țară o alege.")
   + ix("harta", "SCI față de model, pe țări", HARTA_MODEL)
   + vede("Italia, cu cei mai mulți migranți români, este sub model (0,7×); Ungaria peste (1,9×): ce lipsește din model."),
   manual=
   "<h2>Reziduurile</h2>"
   "<p>Reziduul este diferența dintre log SCI observat și log SCI prezis de M4; 10 la puterea reziduului spune de câte "
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
   + caiet("7 și 8", [
       "<code>m4.fittedvalues</code> și <code>m4.resid</code>; graficul observat față de prezis, cu linia de 45°.",
       "Perechile cele mai mult sub și peste model; partenerii României, cu <code>10 ** reziduu</code>.",
       "Harta reziduurilor României, pe contururile țărilor."],
       "Aceeași hartă pentru Turcia (<code>\"TR\"</code>) și Islanda (<code>\"IS\"</code>)."))


sl("s11", "Reziduurile", "Ce se poate concluziona",
   "<h2>Ce se poate concluziona</h2>"
   + tabel(["Se poate afirma", "Nu se poate afirma"], [
       ["perechile cu o rată mai mare de migrație sunt mai legate, la aceeași distanță și graniță",
        "migrația produce legăturile"],
       ["modelul explică puțin peste jumătate din variația lui log SCI", "legăturile sunt explicate"],
       ["la aceeași distanță și migrație, efectul graniței nu se distinge clar", "granițele nu contează"],
       ["rezultatele descriu perechi de țări", "rezultatele descriu persoane"]])
   + nota("Perechile nu sunt independente",
          "Germania apare în 23 de perechi. Intervalele de încredere obișnuite presupun observații independente, deci "
          "sunt prea înguste; corecția uzuală sunt erorile standard grupate pe țară.", True),
   dupa=V_CONC,
   manual="")


# ===========================================================================
#  E. Verificarea
# ===========================================================================

_N = M["n"]
DOVADA = {
    "id": "c7-dovada",
    "sarcina": "Trei rezultate din caiet, rulate pe datele proprii. Ieșirea fiecăruia se lipește în câmpul lui.",
    "indiciu": "Celulele sunt în caietul 07: secțiunile 2, 5.2 și 6.",
    "pasi": [
        {"t": "Perechile modelului",
         "cmd": "len(date)",
         "gol": "numărul afișat",
         "cauta": rf"\b{_N}\b",
         "ind": f"Un singur număr: perechile de țări cu toate variabilele, {_N}.",
         "daca_nu": f"Trebuie să iasă {_N}. Perechile fără migrație se scot înainte (dropna pe migranti)."},
        {"t": "R² al modelului M4",
         "cmd": "m4.rsquared",
         "gol": "numărul afișat",
         "cauta": r"0[.,]5[0-6]\d*",
         "ind": f"Un număr între 0 și 1, în jur de {ro(MOD['m4']['r2'])}.",
         "daca_nu": "R² trebuie să fie în jur de 0.53. Variabilele intră pe logaritm, iar rata se calculează la mie."},
        {"t": "Rata dublă",
         "cmd": "2 ** m4.params[\"log_la_mie\"]",
         "gol": "numărul afișat",
         "cauta": r"1[.,]3\d*",
         "ind": f"Un număr puțin peste 1, în jur de {ro(2 ** B4['log_la_mie'])}.",
         "daca_nu": "Trebuie să iasă în jur de 1.36. Coeficientul se ia din M4, cu distanța și granița în model."},
    ],
    "explicatie": "Rezultatele sunt cele din caiet.",
}

SURSE_C7 = surse("Documentația modelului", [
    ("statsmodels: Fitting models using R-style formulas", "https://www.statsmodels.org/stable/example_formulas.html", "smf.ols, formula, params, rsquared"),
    ("statsmodels: OLS results", "https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.RegressionResults.html", "conf_int, resid, fittedvalues"),
    ("geopandas: dissolve și sjoin", "https://geopandas.org/en/stable/docs/user_guide/aggregation_with_dissolve.html", "contururile țărilor din regiuni; vecinii"),
    ("Kuhn și Johnson: Feature Engineering and Selection", "https://bookdown.org/max/FES/", "construcția, transformarea și selecția variabilelor"),
    ("Gelman, Hill și Vehtari: Regression and Other Stories, cap. 12", "https://avehtari.github.io/ROS-Examples/", "logaritmi, scalare și interpretarea coeficienților"),
])

sl("s12", "Verificarea", "Verificarea în caiet",
   "<h2>Verificarea modelului</h2>"
   + ix("dovada", "Verificarea modelului", DOVADA),
   manual=
   "<h2>Verificarea modelului</h2>"
   "<p>Trei rezultate din caiet, pe datele proprii: numărul de perechi din model, R² al modelului M4 și efectul unei "
   "rate a migranților de două ori mai mari. Ele verifică cele trei părți ale lecției: eșantionul, modelul și "
   "interpretarea.</p>"
   + ix("dovada", "Verificarea modelului", DOVADA)
   + SURSE_C7)


if __name__ == "__main__":
    L.scrie_tot()
