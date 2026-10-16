/* ===========================================================================
   Componentele interactive din lecții.

   Se cheama o singura data pe pagina:  porneste();
   Scaneaza dupa <div data-ix="nume"> si deseneaza inauntru.
   Datele componentei vin din <script type="application/json"> pus inauntru.
   =========================================================================== */

import GRAFICE from "./grafice.js?v=36";
import EXERCITII from "./exercitii.js?v=36";
import VIZUAL from "./vizual.js?v=36";

const C = { ...GRAFICE, ...EXERCITII, ...VIZUAL };

/* O poartă trecută, scrisă şi în baza de date.

   Fără asta, trei dintre sarcinile lecţiei (recunoaşterea tipurilor,
   autoevaluarea, aşteptările) deschideau slide-ul următor dar nu se vedeau
   nicăieri: nici la profesor, nici în punctajul de la teme, care le-ar fi
   cerut şi nu le-ar fi primit niciodată. */
async function poarta(gazda, id, ce = ""){
  const ix = gazda.closest(".ix");
  if (ix){
    if (ix.classList.contains("gata")) return;
    ix.classList.add("gata");
  }
  document.dispatchEvent(new CustomEvent("poarta:gata", { detail:{ id } }));
  try {
    const m = await import("/data-science-workflows/js/colectare.js?v=36");
    await m.salveazaCod({ exercitiuId:id, cod:String(ce).slice(0, 400), trecut:true });
  } catch { /* fără cont, poarta se deschide oricum */ }
}

/* --- 1. Explorator de etape --------------------------------------------- */
C.etape = (gazda, date) => {
  gazda.innerHTML = `<div class="etp">
    <div class="etp__b"></div>
    <div class="etp__i"><h5>${date.titlu||"Alege o etapă"}</h5><p>${date.intro||""}</p></div>
  </div>`;
  const b = gazda.querySelector(".etp__b"), i = gazda.querySelector(".etp__i");
  b.innerHTML = date.etape.map((e,k) =>
    `<button class="etp__p ${e.depozit?"dep":""}" data-k="${k}" type="button">
       <i>${e.depozit ? "▣" : String(k+1).padStart(2,"0")}</i>${e.nume}</button>`).join("");
  b.addEventListener("click", ev => {
    const p = ev.target.closest(".etp__p"); if (!p) return;
    b.querySelectorAll(".etp__p").forEach(x => x.classList.remove("on"));
    p.classList.add("on");
    const e = date.etape[+p.dataset.k];
    i.innerHTML = `<h5>${e.nume}</h5><p>${e.text}</p>` +
                  (e.unde ? `<p class="unde">${e.unde}</p>` : "");
  });
};

/* --- 1b. Disecția unei adrese -------------------------------------------
   Adresa e arătată întreagă, cu bucățile ei. Apeși pe o bucată, îi alegi
   numele. Ideea e să o vezi în context, nu ruptă în fișe: când o cerere nu
   merge, greșeala e aproape mereu într-una dintre bucăți, și prima condiție
   ca s-o găsești e să o poți numi.
   ------------------------------------------------------------------------- */

C.url = (gazda, date) => {
  gazda.closest(".ix")?.classList.add("exc");
  const P = date.parti || [];
  const ET = date.etichete || [];
  const ales = new Array(P.length).fill(null);
  let activ = null;

  const esc = x => String(x).replace(/&/g,"&amp;").replace(/</g,"&lt;");

  gazda.innerHTML = `
    ${date.sarcina ? `<p class="ex__sarcina">${date.sarcina}</p>` : ""}
    <div class="url__bara">${P.map((x, i) =>
      `<button class="url__p" data-i="${i}" type="button">${esc(x.t)}</button>`).join("")}</div>
    <div class="url__et" hidden>${ET.map(e =>
      `<button class="url__e" data-e="${esc(e)}" type="button">${esc(e)}</button>`).join("")}</div>
    <p class="url__aj">Apasă pe o bucată din adresă, apoi alege cum se cheamă.</p>
    <div class="ex__jos">
      <button class="btn btn--mic btn--tare" data-rol="verifica" type="button">Verifică</button>
      <button class="btn btn--mic" data-rol="din-nou" type="button" hidden>Încearcă din nou</button>
      <span class="ex__raspuns"></span>
    </div>
    <p class="ex__ex"></p>
    <p class="ex__stare"></p>`;

  const bara = gazda.querySelector(".url__bara");
  const cos  = gazda.querySelector(".url__et");
  const aj   = gazda.querySelector(".url__aj");
  const btV  = gazda.querySelector('[data-rol="verifica"]');
  const btN  = gazda.querySelector('[data-rol="din-nou"]');
  const out  = gazda.querySelector(".ex__raspuns");
  const ex   = gazda.querySelector(".ex__ex");
  const st   = gazda.querySelector(".ex__stare");

  const scrie = () => {
    bara.querySelectorAll(".url__p").forEach((b, i) => {
      b.classList.toggle("are", !!ales[i]);
      b.classList.toggle("on", activ === i);
      b.dataset.et = ales[i] || "";
    });
  };

  bara.addEventListener("click", e => {
    const b = e.target.closest(".url__p");
    if (!b) return;
    activ = +b.dataset.i;
    cos.hidden = false;
    aj.textContent = `Cum se cheamă „${P[activ].t}”?`;
    scrie();
  });

  cos.addEventListener("click", e => {
    const b = e.target.closest(".url__e");
    if (!b || activ === null) return;
    ales[activ] = b.dataset.e;
    activ = null; cos.hidden = true;
    aj.textContent = ales.every(Boolean)
      ? "Toate au nume. Apasă Verifică."
      : "Mai apasă pe o bucată.";
    scrie();
  });

  btV.onclick = async () => {
    let bune = 0;
    bara.querySelectorAll(".url__p").forEach((b, i) => {
      const ok = ales[i] === P[i].e;
      b.classList.toggle("bun", ok);
      b.classList.toggle("rau", !ok);
      if (ok) bune++;
    });
    const tot = bune === P.length;
    out.innerHTML = tot ? "<b>Corect.</b>" : `<b>${bune} din ${P.length}.</b>`;
    btN.hidden = tot;
    if (!tot) return;

    btV.disabled = true;
    ex.classList.add("vazut");
    ex.innerHTML = (date.explicatie || "") +
      "<ul class=\"url__lista\">" + P.map(x =>
        `<li><code>${esc(x.t)}</code> <b>${esc(x.e)}</b> ${x.d || ""}</li>`).join("") + "</ul>";
    gazda.closest(".ix")?.classList.add("gata");
    document.dispatchEvent(new CustomEvent("poarta:gata", { detail:{ id:date.id } }));
    try {
      const m = await import("/data-science-workflows/js/colectare.js?v=36");
      const salvat = await m.salveazaCod({
        exercitiuId: date.id, cod: ales.join(" | "), trecut: true });
      st.textContent = salvat ? "Rezolvare înregistrată."
                              : "Nu e înregistrată: nu ești autentificat.";
      st.classList.add("vazut");
    } catch {}
  };

  btN.onclick = () => {
    bara.querySelectorAll(".url__p").forEach(b => b.classList.remove("bun", "rau"));
    out.textContent = ""; btN.hidden = true;
  };

  scrie();
};

/* --- 2. Terminal pentru mediul virtual ----------------------------------- */
C.terminal = (gazda) => {
  const SARCINI = [["venv","creezi mediul"],["activate","îl activezi"],
                   ["install","instalezi"],["list","verifici"],["deactivate","ieși"]];
  let activ = false, instalate = [], facute = new Set();
  let linii = ["Windows PowerShell","Copyright (c) Microsoft Corporation","","_"];

  gazda.innerHTML = `
    <div class="trm__sarcini">${SARCINI.map(([,e]) =>
      `<span class="trm__chip">${e}</span>`).join("")}</div>
    <div class="trm__ecran" id="ecran"></div>
    <div class="trm__linie"><span id="prompt">PS C:\\proiect&gt;</span>
      <input id="intrare" autocomplete="off" spellcheck="false" aria-label="Comandă"></div>`;

  const ecran = gazda.querySelector("#ecran");
  const prompt = gazda.querySelector("#prompt");
  const intrare = gazda.querySelector("#intrare");
  const chipuri = [...gazda.querySelectorAll(".trm__chip")];

  const deseneaza = () => {
    ecran.innerHTML = linii.map(l =>
      l.startsWith("!") ? `<div class="er">${l.slice(1)}</div>` : `<div>${l}</div>`).join("");
    ecran.scrollTop = 99999;
    chipuri.forEach((c,k) => c.classList.toggle("gata", facute.has(SARCINI[k][0])));
    prompt.textContent = (activ ? "(venv) " : "") + "PS C:\\proiect>";
  };
  const scrie = (cmd, iesire) => {
    linii.splice(linii.length - 1, 1);
    linii.push(`<span class="pr">${activ?"(venv) ":""}PS C:\\proiect&gt;</span> ${cmd}`);
    iesire.forEach(x => linii.push(x));
    linii.push("", "_");
  };

  const ruleaza = brut => {
    const c = brut.trim(); if (!c) return;
    if (/^python -m venv/.test(c)) { facute.add("venv");
      scrie(c, ["", "Se creează mediul virtual în .\\venv ...", "Gata."]); }
    else if (/activate$/.test(c) && !/deactivate/.test(c)) {
      if (!facute.has("venv")) scrie(c, ["!Nu există folderul venv. Creează întâi mediul."]);
      else { activ = true; facute.add("activate"); scrie(c, [""]); } }
    else if (/^deactivate/.test(c)) {
      if (!activ) scrie(c, ["!Niciun mediu activ."]);
      else { activ = false; facute.add("deactivate"); scrie(c, [""]); } }
    else if (/^pip install/.test(c)) {
      if (!activ) scrie(c, ["!Atenție: instalezi în Python-ul global, nu în mediu.",
                            "!Activează mediul întâi."]);
      else { const p = c.replace(/^pip install\s*/, "").split(/\s+/).filter(Boolean);
        if (!p.length) scrie(c, ["!Specifică ce instalezi. Exemplu: pip install requests pandas"]);
        else { instalate = [...new Set([...instalate, ...p])]; facute.add("install");
          scrie(c, ["", ...p.map(x => `Collecting ${x}`),
                    `Successfully installed ${p.join(" ")}`]); } } }
    else if (/^pip list/.test(c)) {
      if (!activ) scrie(c, ["!Listezi pachetele globale. Activează mediul."]);
      else { facute.add("list"); scrie(c, ["", "Package    Version", "---------- -------",
        ...(instalate.length ? instalate.map(x => `${x.padEnd(11)}(latest)`)
                             : ["(niciun pachet încă)"])]); } }
    else if (/^(ajutor|help)$/.test(c)) scrie(c, ["", "Comenzi:",
      "  python -m venv venv", "  venv\\Scripts\\activate",
      "  pip install requests pandas", "  pip list", "  deactivate", "  curata"]);
    else if (/^(curata|clear|cls)$/.test(c)) { linii = ["_"]; }
    else scrie(c, [`!'${c.split(" ")[0]}' nu este recunoscut. Scrie ajutor.`]);
    deseneaza();
  };

  intrare.addEventListener("keydown", e => {
    if (e.key === "Enter") { ruleaza(intrare.value); intrare.value = ""; }
  });
  deseneaza();
};

/* --- 3. Exercițiu de tipuri ---------------------------------------------- */
C.tipuri = (gazda, date) => {
  gazda.closest(".ix")?.classList.add("exc");
  const OPT = ["str","int","float","bool","None","list","tuple","dict"];
  const Q = date.valori;
  let i = 0, ok = 0, raspuns = [];

  const deseneaza = () => {
    if (i >= Q.length) {
      gazda.innerHTML = `
        <div class="tip__bara">${raspuns.map(a=>`<span class="${a?"ok":"nu"}"></span>`).join("")}</div>
        <div class="tip__val">${ok} / ${Q.length}</div>
        <p class="tip__fb">${ok === Q.length
          ? "<b>Tot corect.</b> Distincția dintre <code>'2024'</code> și <code>2024</code> produce cele mai multe erori tăcute la citirea fișierelor."
          : "<b>Reia.</b> Cazurile ratate se întorc la curățarea datelor, în lecția 4."}</p>
        <button class="btn btn--mic" id="din-nou" type="button">Încă o dată</button>`;
      gazda.querySelector("#din-nou").onclick = () => { i=0; ok=0; raspuns=[]; deseneaza(); };
      /* poarta se deschide când ai parcurs toate valorile, indiferent de scor:
         scopul e să treci prin ele, nu să le nimerești din prima */
      poarta(gazda, "c1-tipuri", `${ok}/${Q.length}`);
      return;
    }
    const q = Q[i];
    gazda.innerHTML = `
      <div class="tip__bara">${Q.map((_,k) =>
        `<span class="${raspuns[k]===undefined?"":(raspuns[k]?"ok":"nu")}"></span>`).join("")}</div>
      <div class="tip__val">${q.v.replace(/</g,"&lt;")}</div>
      <div class="tip__opt">${OPT.map(o =>
        `<button class="tip__o" data-o="${o}" type="button">${o}</button>`).join("")}</div>
      <p class="tip__fb"></p>`;
    gazda.querySelectorAll(".tip__o").forEach(b => b.onclick = () => {
      const bun = b.dataset.o === q.t;
      gazda.querySelectorAll(".tip__o").forEach(x => { x.disabled = true;
        if (x.dataset.o === q.t) x.classList.add("ok");
        else if (x === b) x.classList.add("nu"); });
      raspuns[i] = bun; if (bun) ok++;
      gazda.querySelector(".tip__fb").innerHTML = `<b>${bun?"Corect.":"Nu."}</b> ${q.e}`;
      setTimeout(() => { i++; deseneaza(); }, bun ? 1150 : 2300);
    });
  };
  deseneaza();
};

/* --- 4. Explorator JSON --------------------------------------------------- */
C.json = (gazda, date) => {
  const DESC = {
    tablou:"Listă ordonată. Accesezi elementele după poziție, de la 0.",
    obiect:"Perechi cheie și valoare. În Python devine dicționar.",
    text:"Șir de caractere. Chiar dacă arată ca un an, rămâne text până îl converteșt tu.",
    "număr":"Valoare numerică.",
    null:"Valoarea lipsește explicit. În pandas devine NaN, nu zero.",
    boolean:"Adevărat sau fals."
  };
  const randuri = [];
  const fel = v => v === null ? "null" : Array.isArray(v) ? "tablou"
    : typeof v === "object" ? "obiect" : typeof v === "number" ? "număr"
    : typeof v === "boolean" ? "boolean" : "text";

  (function mergi(v, cheie, adanc, cale){
    const sp = "  ".repeat(adanc);
    const k = cheie !== null ? `<span class="jk">"${cheie}"</span><span class="jp">: </span>` : "";
    if (Array.isArray(v)) {
      randuri.push({ cale, fel:"tablou", n:v.length,
        html:`${sp}<span class="jtog">▾</span>${k}<span class="jp">[</span>` });
      v.forEach((x,j) => mergi(x, null, adanc+1, `${cale}[${j}]`));
      randuri.push({ gol:true, html:`${sp}   <span class="jp">]</span>` });
    } else if (v && typeof v === "object") {
      randuri.push({ cale, fel:"obiect", n:Object.keys(v).length,
        html:`${sp}<span class="jtog">▾</span>${k}<span class="jp">{</span>` });
      Object.entries(v).forEach(([kk,vv]) => mergi(vv, kk, adanc+1, `${cale}["${kk}"]`));
      randuri.push({ gol:true, html:`${sp}   <span class="jp">}</span>` });
    } else {
      const afis = v === null ? '<span class="jl">null</span>'
        : typeof v === "string"  ? `<span class="js">"${v}"</span>`
        : typeof v === "boolean" ? `<span class="jb">${v}</span>`
        : `<span class="jn">${v}</span>`;
      randuri.push({ cale, fel:fel(v), html:`${sp}   ${k}${afis}` });
    }
  })(date.date, null, 0, date.radacina || "raspuns");

  gazda.innerHTML = `<div class="jsn__arb">${randuri.map((r,k) =>
      `<span class="jsn__r" data-k="${k}">${r.html}</span>`).join("")}</div>
    <p class="jsn__out">Apasă pe orice rând din arbore.</p>`;
  const out = gazda.querySelector(".jsn__out");
  gazda.querySelectorAll(".jsn__r").forEach(el => el.onclick = () => {
    const r = randuri[+el.dataset.k]; if (r.gol) return;
    gazda.querySelectorAll(".jsn__r").forEach(x => x.classList.remove("sel"));
    el.classList.add("sel");
    const plus = r.n !== undefined
      ? ` cu ${r.n} ${r.fel === "tablou" ? "elemente" : "chei"}` : "";
    out.innerHTML = `<span class="jsn__pil">${r.fel}</span><b>${r.cale}</b>${plus}<br>${DESC[r.fel]||""}`;
  });
};

/* --- pornire -------------------------------------------------------------- */
export function porneste(){
  document.querySelectorAll("[data-ix]").forEach(g => {
    const nume = g.dataset.ix;
    const f = C[nume];
    if (!f) return;
    let date = {};
    const s = g.querySelector('script[type="application/json"]');
    if (s) { try { date = JSON.parse(s.textContent); } catch {} }
    const corp = document.createElement("div");
    g.appendChild(corp);
    /* unele componente aduc date de pe disc, deci pot întoarce o promisiune */
    const cad = e => { corp.innerHTML =
      `<p style="color:var(--nu);font-family:var(--sans);font-size:13.5px">
         Componenta nu a pornit: ${e.message}</p>`; };
    try {
      const rez = f(corp, date);
      if (rez && typeof rez.catch === "function") rez.catch(cad);
    } catch(e) { cad(e); }
  });
}

/* --- 5. Autoevaluare: ce știi deja ---------------------------------------
   Prima sarcină din curs, din planul cursului: evaluarea cunoștințelor și a
   așteptărilor. Nu se notează. Se înregistrează ca eveniment, ca să văd
   profilul grupei înainte de a începe să predau, nu după.
   ------------------------------------------------------------------------ */
C.autoevaluare = (gazda, date) => {
  gazda.closest(".ix")?.classList.add("exc");
  const NIVELE = date.nivele ||
    ["n-am auzit", "am citit despre", "am folosit o dată", "folosesc des"];
  const T = date.teme;
  const ales = new Array(T.length).fill(null);

  gazda.innerHTML = `
    <p class="ex__sarcina">${date.sarcina || "Pentru fiecare, alege unde te afli acum. Nu se notează, nu se vede la colegi, și nu e nicio problemă dacă bifezi peste tot prima coloană: cursul pornește de la zero."}</p>
    <div class="aev">
      <div class="aev__cap"><span></span>${NIVELE.map(n =>
        `<span class="aev__h">${n}</span>`).join("")}</div>
      ${T.map((t, i) => `<div class="aev__r" data-i="${i}">
        <span class="aev__t">${t.t}<small>${t.d || ""}</small></span>
        ${NIVELE.map((_, k) => `<button class="aev__b" data-i="${i}" data-k="${k}"
            type="button" aria-label="${t.t}: ${NIVELE[k]}"></button>`).join("")}
      </div>`).join("")}
    </div>
    <div class="ex__jos">
      <button class="btn btn--mic btn--tare" data-rol="trimite" type="button" disabled>Trimite</button>
      <span class="ex__raspuns"></span>
    </div>`;

  const out = gazda.querySelector(".ex__raspuns");
  const bt = gazda.querySelector('[data-rol="trimite"]');

  gazda.querySelectorAll(".aev__b").forEach(b => b.onclick = () => {
    const i = +b.dataset.i;
    ales[i] = +b.dataset.k;
    gazda.querySelectorAll(`.aev__b[data-i="${i}"]`)
         .forEach(x => x.classList.toggle("on", x === b));
    gazda.querySelector(`.aev__r[data-i="${i}"]`).classList.add("ales");
    const cate = ales.filter(x => x !== null).length;
    bt.disabled = cate < T.length;
    out.textContent = cate < T.length ? `${cate} din ${T.length}` : "";
  });

  bt.onclick = async () => {
    bt.disabled = true;
    gazda.querySelectorAll(".aev__b").forEach(x => x.disabled = true);
    const medie = ales.reduce((a, b) => a + b, 0) / T.length;
    out.innerHTML = medie < 1
      ? "<b>Mulțumesc.</b> Pornim de la început, exact cum trebuie."
      : medie < 2
        ? "<b>Mulțumesc.</b> Ai pe unde să te agăți, restul construim împreună."
        : "<b>Mulțumesc.</b> O să ai de lucru pe partea de flux, nu pe sintaxă.";
    poarta(gazda, date.id, ales.join(","));
    try {
      const s = await import("/data-science-workflows/js/sesiune.js?v=36");
      await s.jurnal("autoevaluare", Object.fromEntries(T.map((t, i) => [t.cheie, ales[i]])));
    } catch {}
  };
};

/* --- 6. Arborele tipurilor din Python ------------------------------------ */
C.arbore = (gazda, date) => {
  /* Arbore de sus în jos, cu săgeți care se desfac din părinte spre copii,
     ca în schemele din curs. Fiecare familie e un arbore mic de sine
     stătător, iar familiile curg una după alta: un singur arbore cu șase
     ramuri ar fi prea lat ca să se citească de pe proiector.

     Cutiile sunt HTML (se pot apăsa, se pot citi de un cititor de ecran),
     săgețile sunt SVG desenat după ce browserul a așezat cutiile. */
  const R = date.ramuri || [];

  const frunza = t => `<button class="trb__f ${t.imut ? "imut" : ""}"
      data-n="${t.n}" type="button">
      <span class="trb__fn">${t.n}</span>
      ${t.cls ? `<span class="trb__fc">${t.cls}</span>` : ""}</button>`;

  gazda.innerHTML = `
    ${date.sarcina ? `<p class="ix__sarcina">${date.sarcina}</p>` : ""}
    <div class="trb">
      <div class="trb__plan">
        <svg class="trb__linii" aria-hidden="true"></svg>
        ${R.map((g, i) => {
          /* O familie cu multe frunze are nevoie de două coloane, altfel
             rândul de frunze se rupe și traversa trece peste ele. */
          const nr = g.sub ? g.sub.reduce((n, s) => n + s.tipuri.length, 0)
                           : g.tipuri.length;
          const lat = (g.sub && nr >= 5) || nr >= 5;
          return `
          <div class="trb__ram${lat ? " trb__ram--lat" : ""}">
            <div class="trb__nod trb__nod--g" data-nod="g${i}">${g.nume}</div>
            ${g.sub ? `
              <div class="trb__copii">
                ${g.sub.map((sb, j) => `
                  <div class="trb__sub">
                    <div class="trb__nod trb__nod--s" data-nod="s${i}-${j}">${sb.nume}</div>
                    <div class="trb__copii trb__copii--f">
                      ${sb.tipuri.map(frunza).join("")}</div>
                  </div>`).join("")}
              </div>`
            : `<div class="trb__copii trb__copii--f">
                 ${g.tipuri.map(frunza).join("")}</div>`}
          </div>`;
        }).join("")}
      </div>
      ${date.legenda ? `<p class="trb__leg">
         <span class="trb__lc">list</span>se poate schimba
         <span class="trb__lc trb__lc--i">tuple</span>nu se poate schimba</p>` : ""}
      <div class="trb__i"><h5>${date.titlu || "Apasă pe orice tip"}</h5>
        <p>${date.intro || ""}</p></div>
    </div>`;

  const toate = R.flatMap(g => g.sub ? g.sub.flatMap(s => s.tipuri) : g.tipuri);
  const info  = gazda.querySelector(".trb__i");
  const plan  = gazda.querySelector(".trb__plan");
  const svg   = gazda.querySelector(".trb__linii");

  /* ---- săgețile -------------------------------------------------------
     Din mijlocul de jos al părintelui coboară o tulpină scurtă, de acolo
     pleacă o traversă până deasupra fiecărui copil, și din traversă coboară
     o săgeată. Asta e forma care se citește ca „se desface în”. */
  function trage(){
    const P = plan.getBoundingClientRect();
    if (!P.width) return;
    svg.setAttribute("viewBox", `0 0 ${P.width} ${P.height}`);
    svg.setAttribute("width", P.width);
    svg.setAttribute("height", P.height);

    const cut = el => {
      const r = el.getBoundingClientRect();
      return { x: r.left - P.left + r.width / 2,
               sus: r.top - P.top, jos: r.bottom - P.top };
    };

    const d = [];
    const varf = [];
    const leaga = (parinte, copii) => {
      if (!copii.length) return;
      const A = cut(parinte);
      const C = copii.map(cut);
      const mij = (A.jos + Math.min(...C.map(c => c.sus))) / 2;
      d.push(`M${A.x.toFixed(1)},${A.jos.toFixed(1)} V${mij.toFixed(1)}`);
      if (C.length > 1){
        d.push(`M${Math.min(...C.map(c => c.x)).toFixed(1)},${mij.toFixed(1)} ` +
               `H${Math.max(...C.map(c => c.x)).toFixed(1)}`);
      }
      C.forEach(c => {
        d.push(`M${c.x.toFixed(1)},${mij.toFixed(1)} V${(c.sus - 5).toFixed(1)}`);
        varf.push(`${c.x.toFixed(1)},${c.sus.toFixed(1)} ` +
                  `${(c.x - 3.6).toFixed(1)},${(c.sus - 5.4).toFixed(1)} ` +
                  `${(c.x + 3.6).toFixed(1)},${(c.sus - 5.4).toFixed(1)}`);
      });
    };

    plan.querySelectorAll(".trb__ram").forEach(ram => {
      const g = ram.querySelector(".trb__nod--g");
      const subs = [...ram.querySelectorAll(".trb__nod--s")];
      if (subs.length){
        leaga(g, subs);
        subs.forEach(s => leaga(s,
          [...s.parentElement.querySelectorAll(".trb__f")]));
      } else {
        leaga(g, [...ram.querySelectorAll(".trb__f")]);
      }
    });

    svg.innerHTML =
      `<path d="${d.join(" ")}" fill="none" stroke="currentColor"
         stroke-width="1.2"/>` +
      varf.map(v => `<polygon points="${v}" fill="currentColor"/>`).join("");
  }

  trage();
  requestAnimationFrame(trage);
  if (window.ResizeObserver) new ResizeObserver(trage).observe(plan);

  /* ---- apăsarea pe un tip --------------------------------------------- */
  plan.addEventListener("click", ev => {
    const b = ev.target.closest(".trb__f");
    if (!b) return;
    gazda.querySelectorAll(".trb__f").forEach(x => x.classList.remove("on"));
    b.classList.add("on");
    const t = toate.find(x => x.n === b.dataset.n);
    if (!t) return;
    info.innerHTML = `<h5><code>${t.n}</code> ${t.cls ? `<small>${t.cls}</small>` : ""}</h5>
      <p>${t.d}</p>
      ${t.ex ? `<pre class="trb__ex"><code>${t.ex.replace(/</g,"&lt;")}</code></pre>` : ""}
      ${t.la ? `<p class="trb__la">${t.la}</p>` : ""}`;
  });
};


/* --- 7. Așteptări: text liber, citit de profesor -------------------------
   A doua jumătate a primului punct din planul cursului: „evaluarea
   cunoștințelor ȘI a așteptărilor”. Cunoștințele se bifează, așteptările se
   scriu. Ajung în jurnal și apar la profesor, cu numele celui care a scris.
   ------------------------------------------------------------------------ */
C.asteptari = (gazda, date) => {
  gazda.closest(".ix")?.classList.add("exc");
  const MIN = date.minim || 25;

  gazda.innerHTML = `
    <p class="ex__sarcina">${date.sarcina || "Două-trei rânduri. Le citesc pe toate."}</p>
    <div class="ast">
      <textarea class="ast__t" rows="4" maxlength="600" spellcheck="true"
        placeholder="${date.exemplu || "De exemplu: vreau să pot lua singur date de pe un site și să le pun cap la cap, fără să aștept pe cineva."}"></textarea>
      <div class="ast__jos"><span class="ast__nr">0</span>
        <button class="btn btn--mic btn--tare" data-rol="trimite" type="button" disabled>Trimite</button></div>
    </div>
    <p class="ex__raspuns"></p>`;

  const t = gazda.querySelector(".ast__t");
  const nr = gazda.querySelector(".ast__nr");
  const bt = gazda.querySelector('[data-rol="trimite"]');
  const out = gazda.querySelector(".ex__raspuns");

  t.addEventListener("input", () => {
    const n = t.value.trim().length;
    nr.textContent = n < MIN ? `încă ${MIN - n} caractere` : `${n} caractere`;
    nr.classList.toggle("gata", n >= MIN);
    bt.disabled = n < MIN;
  });

  bt.onclick = async () => {
    bt.disabled = true; t.disabled = true;
    out.innerHTML = `<b>Mulțumesc.</b> ${date.multumesc
      || "Le citesc pe toate înainte de cursul următor."}`;
    poarta(gazda, date.id, "scris");
    try {
      const s = await import("/data-science-workflows/js/sesiune.js?v=36");
      /* `tip` ajunge în jurnal și decide în ce sumar apare textul la profesor */
      await s.jurnal(date.tip || "asteptari", { text: t.value.trim().slice(0, 600) });
    } catch {}
  };
};
