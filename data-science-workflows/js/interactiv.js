/* ===========================================================================
   Componentele interactive din lecții.

   Se cheama o singura data pe pagina:  porneste();
   Scaneaza dupa <div data-ix="nume"> si deseneaza inauntru.
   Datele componentei vin din <script type="application/json"> pus inauntru.
   =========================================================================== */

import GRAFICE from "./grafice.js?v=68";
import EXERCITII from "./exercitii.js?v=68";
import VIZUAL from "./vizual.js?v=68";
import HARTA from "./harta-sci.js?v=68";

const C = { ...GRAFICE, ...EXERCITII, ...VIZUAL, ...HARTA };

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
    const m = await import("/data-science-workflows/js/colectare.js?v=68");
    await m.salveazaCod({ exercitiuId:id, cod:String(ce).slice(0, 800), trecut:true });
  } catch { /* fără cont, poarta se deschide oricum */ }
}

/* --- 1. Explorator de etape --------------------------------------------- */
C.etape = (gazda, date) => {
  /* static: e un cuprins (agenda orei), nu o interacțiune; se citește dintr-o privire */
  if (date.static){
    gazda.innerHTML = `<div class="etp-st" role="list">${date.etape.map((e, k) =>
      `<div class="etp-st__r" role="listitem"><i>${String(k + 1).padStart(2, "0")}</i><b>${e.nume}</b><span>${e.text}</span></div>`).join("")}</div>`;
    return;
  }
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

C.agenda = (gazda, date) => C.etape(gazda, { ...date, static: true });

/* --- 1b. Adresa, bucată cu bucată ---------------------------------------
   Adresa e desenată ca un șir de plăci separate; partea de după „?” e o
   singură placă, cu perechile cheie=valoare înăuntru, pentru că rolul ei e
   unul singur. Alegi o placă, apoi rolul ei din legendă; răspunsul vine pe
   loc. O placă e rezolvată dinainte, ca exemplu. Când toate sunt numite, se
   arată legătura dintre parametri și dicționarul `params` din requests.
   ------------------------------------------------------------------------- */

C.url = (gazda, date) => {
  gazda.closest(".ix")?.classList.add("exc");
  const P = date.parti || [], R = date.roluri || [];
  const pus = P.map((p, i) => i === date.rezolvat ? p.e : null);
  let activ = null, gresite = 0;
  const esc = x => String(x).replace(/&/g,"&amp;").replace(/</g,"&lt;");
  const rol = e => R.find(r => r.e === e) || {};

  gazda.innerHTML = `
    ${date.sarcina ? `<p class="ex__sarcina">${date.sarcina}</p>` : ""}
    <div class="adr">
      <div class="adr__bara">${P.map((p, i) => `
        <button type="button" class="adr__p" data-i="${i}">
          <span class="adr__t">${p.kv ? p.kv.map((x, k) => `${k ? '<i class="adr__amp">&amp;</i>' : '<i class="adr__amp">?</i>'}<span class="adr__kv">${esc(x)}</span>`).join("") : esc(p.t)}</span>
          <span class="adr__rol"></span>
        </button>`).join("")}</div>
      <div class="adr__roluri">${R.map(r => `
        <button type="button" class="adr__r" data-e="${esc(r.e)}" style="--c:var(--${r.c})">
          <b>${esc(r.e)}</b><span>${r.d}</span></button>`).join("")}</div>
      <p class="adr__aj"></p>
      <div class="adr__dupa" hidden>${date.dupa || ""}</div>
      <p class="ex__stare"></p>
    </div>`;

  const aj = gazda.querySelector(".adr__aj");
  const placi = [...gazda.querySelectorAll(".adr__p")];
  const scrie = () => {
    placi.forEach((b, i) => {
      const e = pus[i];
      b.classList.toggle("on", activ === i);
      b.classList.toggle("are", !!e);
      b.style.setProperty("--c", e ? `var(--${rol(e).c})` : "var(--linie-2)");
      b.querySelector(".adr__rol").textContent = e || "";
    });
    gazda.querySelectorAll(".adr__r").forEach(r => r.classList.toggle("tinta", activ !== null));
    const rest = pus.filter(x => !x).length;
    aj.textContent = activ !== null ? `Ce rol are placa ${activ + 1}? Alege din legendă.`
      : rest === 1 ? "Mai e o placă fără rol." : rest ? `Mai sunt ${rest} plăci fără rol.` : "";
  };

  gazda.querySelector(".adr__bara").addEventListener("click", e => {
    const b = e.target.closest(".adr__p"); if (!b) return;
    const i = +b.dataset.i;
    if (pus[i]) return;                       // placa e deja numită corect
    activ = activ === i ? null : i; scrie();
  });

  gazda.querySelector(".adr__roluri").addEventListener("click", async e => {
    const b = e.target.closest(".adr__r"); if (!b || activ === null) return;
    const i = activ, ales = b.dataset.e;
    if (ales === P[i].e){
      pus[i] = ales; activ = null; scrie();
    } else {
      gresite++;
      const pl = placi[i]; pl.classList.add("rau");
      aj.innerHTML = `<b>Nu e ${esc(ales)}.</b> ${rol(ales).d ? "Citește din nou ce face fiecare rol." : ""}`;
      setTimeout(() => pl.classList.remove("rau"), 700);
      return;
    }
    if (pus.every(Boolean)){
      gazda.querySelector(".adr__dupa").hidden = false;
      aj.textContent = !gresite ? "Toate plăcile au rol." : gresite === 1 ? "Toate plăcile au rol, cu o încercare greșită pe drum." : `Toate plăcile au rol, cu ${gresite} încercări greșite pe drum.`;
      gazda.closest(".ix")?.classList.add("gata");
      document.dispatchEvent(new CustomEvent("poarta:gata", { detail:{ id:date.id } }));
      const st = gazda.querySelector(".ex__stare");
      try {
        const m = await import("/data-science-workflows/js/colectare.js?v=68");
        const salvat = await m.salveazaCod({ exercitiuId: date.id, cod: `${pus.join(" | ")} · greșite: ${gresite}`, trecut: true });
        st.textContent = salvat ? "Rezolvare înregistrată." : "Nu e înregistrată: nu ești autentificat.";
        st.classList.add("vazut");
      } catch {}
    }
  });

  scrie();
};

/* --- 2. Terminal pentru mediul virtual -----------------------------------
   Pornește în folderul utilizatorului, ca un terminal adevărat. Ordinea
   contează: întâi folderul proiectului, apoi intri în el, abia apoi .venv.
   Un .venv făcut în altă parte e semnalat, pentru că e greșeala cea mai
   frecventă de la prima oră. */
C.terminal = (gazda) => {
  const SARCINI = [["mkdir","faci folderul"],["cd","intri în el"],["venv","creezi .venv"],
                   ["install","instalezi pachetele"],["dir","te uiți în folder"]];
  const ACASA = "C:\\Users\\student";
  let cwd = ACASA, proiecte = new Set(), cuVenv = new Set(), instalate = [], activ = false;
  const facute = new Set();
  let linii = ["Windows PowerShell", "", "_"];

  gazda.innerHTML = `
    <div class="trm__sarcini">${SARCINI.map(([,e]) => `<span class="trm__chip">${e}</span>`).join("")}</div>
    <div class="trm__ecran"></div>
    <div class="trm__linie"><span class="trm__pr"></span>
      <input autocomplete="off" spellcheck="false" aria-label="Comandă" placeholder="scrie o comandă; ajutor, dacă te blochezi"></div>`;
  const ecran = gazda.querySelector(".trm__ecran"), prompt = gazda.querySelector(".trm__pr");
  const intrare = gazda.querySelector("input"), chipuri = [...gazda.querySelectorAll(".trm__chip")];
  const pr = () => `${activ ? "(.venv) " : ""}PS ${cwd}&gt;`;
  const esc = t => String(t).replace(/&/g, "&amp;").replace(/</g, "&lt;");
  const deseneaza = () => {
    ecran.innerHTML = linii.map(l => l.startsWith("!") ? `<div class="er">${l.slice(1)}</div>`
      : l.startsWith("~") ? `<div class="ok">${l.slice(1)}</div>` : `<div>${l}</div>`).join("");
    ecran.scrollTop = 99999;
    chipuri.forEach((c, k) => c.classList.toggle("gata", facute.has(SARCINI[k][0])));
    prompt.innerHTML = pr();
  };
  const scrie = (cmd, iesire) => {
    linii.splice(linii.length - 1, 1);
    linii.push(`<span class="pr">${pr()}</span> ${esc(cmd)}`);
    iesire.forEach(x => linii.push(x)); linii.push("", "_");
  };
  const nume = () => cwd.split("\\").pop();
  const inProiect = () => cwd !== ACASA;
  const instaleaza = (c, pk) => {
    if (!pk.length) return scrie(c, ["!Spune ce instalezi. De exemplu: pandas ipykernel"]);
    instalate = [...new Set([...instalate, ...pk])]; facute.add("install");
    scrie(c, ["", ...pk.map(x => `Collecting ${x}`), `~Successfully installed ${pk.join(" ")} (în ${nume()}\\.venv)`]);
  };

  const ruleaza = brut => {
    const c = brut.trim(); if (!c) return;
    let m;
    if ((m = c.match(/^(mkdir|md)\s+(\S+)$/))){
      if (inProiect()) scrie(c, ["!Ești deja în folderul unui proiect. Un proiect nu stă în alt proiect."]);
      else { proiecte.add(m[2]); facute.add("mkdir"); scrie(c, ["", `    Directory: ${ACASA}`, "", `d----   ${m[2]}`]); } }
    else if ((m = c.match(/^cd\s+(\S+)$/))){
      if (m[1] === "..") { cwd = ACASA; activ = false; scrie(c, []); }
      else if (!inProiect() && proiecte.has(m[1])) { cwd = ACASA + "\\" + m[1]; facute.add("cd"); scrie(c, []); }
      else scrie(c, [`!cd : Cannot find path '${cwd}\\${m[1]}' because it does not exist.`]); }
    else if (/^(py|python3?)\s+-m\s+venv\s+\S+$/.test(c)){
      const dir = c.split(/\s+/).pop();
      if (!inProiect()) scrie(c, ["", `!Ai creat ${dir} direct în ${ACASA}, nu într-un proiect.`,
        "!Fă întâi folderul proiectului (mkdir) și intră în el (cd), apoi creează mediul acolo."]);
      else { cuVenv.add(cwd); facute.add("venv");
        scrie(c, ["", `~Mediul e în ${cwd}\\${dir}. Nu scrii nimic acolo: e al lui Python.`]); } }
    else if (/^\.?\\?\.venv\\Scripts\\activate(\.ps1)?$/.test(c)){
      if (!cuVenv.has(cwd)) scrie(c, ["!Aici nu există .venv. Ești în folderul bun?"]);
      else { activ = true; scrie(c, []); } }
    else if ((m = c.match(/^\.?\\?\.venv\\Scripts\\python(?:\.exe)?\s+-m\s+pip\s+install\s*(.*)$/))){
      if (!cuVenv.has(cwd)) scrie(c, ["!Aici nu există .venv. Creează-l întâi, în folderul proiectului."]);
      else instaleaza(c, m[1].split(/\s+/).filter(Boolean)); }
    else if ((m = c.match(/^pip\s+install\s*(.*)$/))){
      if (!activ) scrie(c, ["!Atenție: fără mediu activ, pip instalează în Python-ul global.",
        "!Folosește .venv\\Scripts\\python -m pip install …, sau activează întâi mediul."]);
      else instaleaza(c, m[1].split(/\s+/).filter(Boolean)); }
    else if (/^(pip\s+list|\.?\\?\.venv\\Scripts\\python(?:\.exe)?\s+-m\s+pip\s+list)$/.test(c)){
      const glob = /^pip/.test(c) && !activ;
      scrie(c, ["", "Package    Version", "---------- -------", ...(glob ? ["(pachetele globale, nu ale proiectului)"]
        : instalate.length ? instalate.map(x => `${x.padEnd(11)}…`) : ["pip        …", "(încă nimic instalat)"])]); }
    else if (/^(dir|ls)$/.test(c)){
      facute.add("dir");
      if (!inProiect()) scrie(c, ["", `    Directory: ${cwd}`, "", ...[...proiecte].map(x => `d----   ${x}`), "d----   Desktop", "d----   Documents"]);
      else scrie(c, ["", `    Directory: ${cwd}`, "", ...(cuVenv.has(cwd) ? ["d----   .venv        <span class=\"c\"># al lui Python, nu umbli aici</span>"] : []),
        "d----   data", "d----   notebooks", "d----   code", "-a---   README.md"]); }
    else if (/^deactivate$/.test(c)){ if (activ) { activ = false; scrie(c, []); } else scrie(c, ["!Niciun mediu activ."]); }
    else if (/^(ajutor|help)$/.test(c)) scrie(c, ["", "Comenzile, în ordine:",
      "  mkdir proiect-dsw", "  cd proiect-dsw", "  py -m venv .venv",
      "  .venv\\Scripts\\python -m pip install pandas ipykernel", "  dir",
      "Și: cd .., .venv\\Scripts\\activate, pip list, deactivate, curata"]);
    else if (/^(curata|clear|cls)$/.test(c)) linii = ["_"];
    else scrie(c, [`!${esc(c.split(" ")[0])} : The term is not recognized. Scrie ajutor.`]);
    deseneaza();
  };
  intrare.addEventListener("keydown", e => { if (e.key === "Enter"){ ruleaza(intrare.value); intrare.value = ""; } });
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

  const rad = date.radacina || "raspuns";
  const P = date.provocari || [];
  gazda.innerHTML = `${P.length ? `<div class="jsn__prov"><span>Ajunge la:</span>${P.map((x, i) =>
        `<span class="jsn__pv" data-i="${i}"><i>○</i>${x.t}</span>`).join("")}</div>` : ""}
    <label class="jsn__scrie"><span>Scrie drumul</span>
      <input type="text" spellcheck="false" autocomplete="off" placeholder='${rad}[1][0]["date"]'></label>
    <div class="jsn__arb">${randuri.map((r,k) =>
      `<span class="jsn__r" data-k="${k}">${r.html}</span>`).join("")}</div>
    <p class="jsn__out">Scrie un drum sau apasă pe orice rând din arbore.</p>`;
  const out = gazda.querySelector(".jsn__out");
  const inp = gazda.querySelector(".jsn__scrie input");

  /* drumul scris de student: îl parcurgem pas cu pas, ca să spunem unde se rupe */
  const ce = v => ({ tablou: "o listă", obiect: "un dicționar", text: "un text", "număr": "un număr", null: "null", boolean: "o valoare logică" })[fel(v)];
  const fara = t => t.replace(/\s+/g, "").replace(/'/g, '"');
  function parcurge(text){
    const t = fara(text);
    if (!t.startsWith(rad)) return { err: `Drumul pornește de la <code>${rad}</code>.` };
    const re = /\[(\d+)\]|\["([^"]*)"\]/y;
    let i = rad.length, v = date.date, cale = rad;
    re.lastIndex = i;
    while (i < t.length){
      re.lastIndex = i;
      const m = re.exec(t);
      if (!m) return { err: `Nu înțeleg ce vine după <code>${cale}</code>. Un pas e <code>[0]</code> (poziție) sau <code>["cheie"]</code> (cheie).`, cale };
      if (m[1] !== undefined){
        const n = +m[1];
        if (!Array.isArray(v)) return { err: `<code>${cale}</code> e ${ce(v)}, nu o listă: aici se cere o cheie între ghilimele, nu o poziție.`, cale };
        if (n >= v.length) return { err: `<code>${cale}</code> are doar ${v.length} elemente, pe pozițiile 0–${v.length - 1}.`, cale };
        v = v[n]; cale += `[${n}]`;
      } else {
        const k = m[2];
        if (!v || typeof v !== "object" || Array.isArray(v))
          return { err: `<code>${cale}</code> e ${ce(v)}, nu un dicționar: aici se cere o poziție, de exemplu <code>[0]</code>.`, cale };
        if (!(k in v)) return { err: `<code>${cale}</code> nu are cheia <code>"${k}"</code>. Are: ${Object.keys(v).map(x => `<code>"${x}"</code>`).join(", ")}.`, cale };
        v = v[k]; cale += `["${k}"]`;
      }
      i = re.lastIndex;
    }
    return { cale, v };
  }
  function aprinde(cale){
    gazda.querySelectorAll(".jsn__r").forEach(x => x.classList.remove("sel"));
    const k = randuri.findIndex(r => r.cale === cale);
    const el = gazda.querySelector(`.jsn__r[data-k="${k}"]`);
    if (el){ el.classList.add("sel"); el.scrollIntoView({ block: "nearest" }); }
    return randuri[k];
  }
  inp.addEventListener("input", () => {
    if (!inp.value.trim()){ out.innerHTML = "Scrie un drum sau apasă pe orice rând din arbore."; return; }
    const r = parcurge(inp.value);
    if (r.err){ if (r.cale) aprinde(r.cale); out.innerHTML = `<span class="jsn__pil rau">încă nu</span>${r.err}`; return; }
    const rr = aprinde(r.cale);
    const val = (r.v !== null && typeof r.v === "object") ? "" : ` = <b>${JSON.stringify(r.v)}</b>`;
    out.innerHTML = `<span class="jsn__pil">${rr ? rr.fel : fel(r.v)}</span><b>${r.cale}</b>${val}<br>${DESC[fel(r.v)] || ""}`;
    P.forEach((x, i) => {
      if (fara(x.cale) === r.cale){
        const pv = gazda.querySelector(`.jsn__pv[data-i="${i}"]`);
        pv.classList.add("ok"); pv.querySelector("i").textContent = "✓";
      }
    });
  });
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
  /* blocurile de cod scrise în slide-uri fără culori primesc tema editorului;
     cele colorate de mână rămân cum sunt */
  document.querySelectorAll("pre > code").forEach(c => {
    if (c.children.length) return;
    const t = c.textContent;
    const lb = /^\s*(\$|pip |git |cd |python |source |mkdir )/m.test(t) ? "sh"
             : /^\s*(SELECT|CREATE|INSERT)\b/im.test(t) ? "sql"
             : /^https?:\/\//.test(t.trim()) ? null : "py";
    if (lb) c.innerHTML = EXERCITII.coloreaza ? EXERCITII.coloreaza(t, lb) : c.innerHTML;
  });
  document.querySelectorAll("[data-ix]").forEach(g => {
    const nume = g.dataset.ix;
    const f = C[nume];
    if (!f) return;
    let date = {};
    const s = g.querySelector('script[type="application/json"]');
    if (s) { try { date = JSON.parse(s.textContent); } catch {} }
    /* "poarta": false = componentă de încercat, nu sarcină: nu oprește
       slide-ul, nu intră la notă, nu se salvează */
    if (date && date.poarta === false){
      g.classList.add("liber");
      (globalThis.dswFaraPoarta ||= new Set()).add(date.id);
    }
    const corp = document.createElement("div");
    g.appendChild(corp);
    if (date && date.intai) intai(g, corp, date.intai);
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

/* --- Întâi ghicești ---------------------------------------------------------
   `intai: {q, variante, corect, dupa}` pus în datele oricărei componente:
   componenta stă acoperită până alegi un răspuns, ca să nu vezi rezultatul
   înainte să-l prezici. Nu se notează; apoi te joci cu ea normal. */
function intai(g, corp, d){
  const esc = t => String(t).replace(/[&<>]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));
  const box = document.createElement("div");
  box.className = "intai";
  box.innerHTML = `<p class="intai__et">întâi ghicești</p><p class="pz__q">${d.q}</p>
    <div class="pz__v">${(d.variante || []).map((v, i) =>
      `<button class="pz__b" type="button" data-i="${i}">${esc(v)}</button>`).join("")}</div>
    <p class="intai__dupa" hidden></p>`;
  g.insertBefore(box, corp);
  corp.classList.add("intai-ascuns");
  box.querySelectorAll(".pz__b").forEach(b => b.onclick = () => {
    const i = +b.dataset.i, bine = i === d.corect;
    box.querySelectorAll(".pz__b").forEach(x => {
      x.disabled = true;
      if (+x.dataset.i === d.corect) x.classList.add("bun");
    });
    if (!bine) b.classList.add("rau");
    const p = box.querySelector(".intai__dupa");
    p.innerHTML = `<b>${bine ? "Exact." : "Nu chiar."}</b> ${d.dupa || ""} <span class="intai__acum">Acum verifică singur, mai jos.</span>`;
    p.hidden = false;
    corp.classList.remove("intai-ascuns");
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
      const s = await import("/data-science-workflows/js/sesiune.js?v=68");
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

  const frunza = t => `<button class="trb__f ${t.imut ? "imut" : ""} ${t.noi ? "noi" : ""}"
      data-n="${t.n}" type="button">
      ${t.noi ? `<span class="trb__noi">noi</span>` : ""}
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
    /* textul însuși ajunge și la poartă (legat de ora pornită), ca profesorul
       să-l vadă în rezultatele orei și pe tablă, nu doar cuvântul „scris” */
    poarta(gazda, date.id, t.value.trim());
    try {
      const s = await import("/data-science-workflows/js/sesiune.js?v=68");
      /* `tip` ajunge în jurnal și decide în ce sumar apare textul la profesor */
      await s.jurnal(date.tip || "asteptari", { text: t.value.trim().slice(0, 600) });
    } catch {}
  };
};
