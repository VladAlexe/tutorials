/* ===========================================================================
   Componentele interactive din lecții.

   Se cheama o singura data pe pagina:  porneste();
   Scaneaza dupa <div data-ix="nume"> si deseneaza inauntru.
   Datele componentei vin din <script type="application/json"> pus inauntru.
   =========================================================================== */

const C = {};

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
      const afis = v === null ? '<span class="jb">null</span>'
        : typeof v === "string" ? `<span class="js">"${v}"</span>`
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
    try { f(corp, date); } catch(e) { corp.innerHTML =
      `<p style="color:var(--nu)">Componenta nu a pornit: ${e.message}</p>`; }
  });
}
