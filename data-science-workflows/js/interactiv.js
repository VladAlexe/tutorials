/* ===========================================================================
   Componentele interactive din lecții.

   Se cheama o singura data pe pagina:  porneste();
   Scaneaza dupa <div data-ix="nume"> si deseneaza inauntru.
   Datele componentei vin din <script type="application/json"> pus inauntru.
   =========================================================================== */

import GRAFICE from "./grafice.js?v=78";
import EXERCITII from "./exercitii.js?v=78";
import VIZUAL from "./vizual.js?v=78";
import HARTA from "./harta-sci.js?v=78";

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
    const m = await import("/data-science-workflows/js/colectare.js?v=78");
    await m.salveazaCod({ exercitiuId:id, cod:String(ce).slice(0, 800), trecut:true });
  } catch { /* fără cont, poarta se deschide oricum */ }
}

/* --- 1. Explorator de etape --------------------------------------------- */
C.etape = (gazda, date) => {
  /* Pașii stau la vedere, pe rânduri: numărul, numele, ce se face și, unde
     există, fișierul în care se face. Nimic ascuns sub un clic. */
  gazda.innerHTML = `<div class="etp-st" role="list">${date.etape.map((e, k) =>
    `<div class="etp-st__r" role="listitem"><i>${e.depozit ? "▣" : String(k + 1).padStart(2, "0")}</i><b>${e.nume}</b>`
    + `<span>${e.text}${e.unde && !date.static ? `<code class="etp-st__u">${e.unde}</code>` : ""}</span></div>`).join("")}</div>`;
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
    aj.textContent = activ !== null ? `Ce rol are placa ${activ + 1}? Rolul se alege din legendă.`
      : rest === 1 ? "Mai este o placă fără rol." : rest ? `Mai sunt ${rest} plăci fără rol.` : "";
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
      aj.innerHTML = `<b>Nu este ${esc(ales)}.</b> ${rol(ales).d ? "Recitește descrierea fiecărui rol." : ""}`;
      setTimeout(() => pl.classList.remove("rau"), 700);
      return;
    }
    if (pus.every(Boolean)){
      gazda.querySelector(".adr__dupa").hidden = false;
      aj.textContent = !gresite ? "Toate plăcile au rol." : gresite === 1 ? "Toate plăcile au rol, după o încercare greșită." : `Toate plăcile au rol, după ${gresite} încercări greșite.`;
      gazda.closest(".ix")?.classList.add("gata");
      document.dispatchEvent(new CustomEvent("poarta:gata", { detail:{ id:date.id } }));
      const st = gazda.querySelector(".ex__stare");
      try {
        const m = await import("/data-science-workflows/js/colectare.js?v=78");
        const salvat = await m.salveazaCod({ exercitiuId: date.id, cod: `${pus.join(" | ")} · greșite: ${gresite}`, trecut: true });
        st.textContent = salvat ? "Rezolvare înregistrată." : "Rezolvarea nu a fost înregistrată: nu ești autentificat.";
        st.classList.add("vazut");
      } catch {}
    }
  });

  scrie();
};

/* --- 2. Terminal pentru mediul virtual -----------------------------------
   Pornește în folderul utilizatorului, ca un terminal adevărat, unde stă
   deja dsw (arhiva cursului, dezarhivată și redenumită). Ordinea contează:
   întâi intri în dsw, apoi .venv, apoi activarea, abia apoi pip. Un .venv
   făcut în altă parte și un pip fără mediu activ sunt semnalate, pentru că
   sunt greșelile cele mai frecvente de la prima oră. Prima activare dă
   eroarea de execution policy, ca pe multe calculatoare cu Windows. */
C.terminal = (gazda) => {
  const SARCINI = [["cd","intri în dsw"],["venv","creezi .venv"],["activ","activezi mediul"],
                   ["install","instalezi pachetele"],["dir","listezi conținutul folderului"]];
  const ACASA = "C:\\Users\\student";
  const NB = "01_introducere_si_datele_proiectului.ipynb";
  /* folderele, cu ce e în ele; "d:" = dosar */
  const FS = {
    "": ["d:Desktop", "d:Documents", "d:Downloads", "d:dsw"],
    "dsw": ["d:curs", "-a---:.gitignore", "-a---:README.md", "-a---:requirements.txt"],
    "dsw\\curs": ["d:data", "d:exemple_curs1", "-a---:" + NB],
    "dsw\\curs\\data": ["-a---:country.csv"],
    "dsw\\curs\\exemple_curs1": ["-a---:activitati.txt", "-a---:persoane.json"],
  };
  let cwd = "", cuVenv = new Set(), instalate = [], activ = false, politica = false, prAcum = "";
  const facute = new Set();
  let linii = ["Windows PowerShell", "", "_"];

  gazda.innerHTML = `
    <div class="trm__sarcini">${SARCINI.map(([,e]) => `<span class="trm__chip">${e}</span>`).join("")}</div>
    <div class="trm__ecran"></div>
    <div class="trm__linie"><span class="trm__pr"></span>
      <input autocomplete="off" spellcheck="false" aria-label="Comandă" placeholder="o comandă (help afișează lista comenzilor)"></div>`;
  const ecran = gazda.querySelector(".trm__ecran"), prompt = gazda.querySelector(".trm__pr");
  const intrare = gazda.querySelector("input"), chipuri = [...gazda.querySelectorAll(".trm__chip")];
  const cale = (c = cwd) => c ? ACASA + "\\" + c : ACASA;
  const pr = () => `${activ ? "(.venv) " : ""}PS ${cale()}&gt;`;
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
    linii.push(`<span class="pr">${prAcum}</span> ${esc(cmd)}`);   /* promptul de dinaintea comenzii */
    iesire.forEach(x => linii.push(x)); linii.push("", "_");
  };
  const continut = c => FS[c] || [];
  const areDosar = (c, n) => continut(c).some(x => x.toLowerCase() === "d:" + n.toLowerCase());
  const numeDosar = (c, n) => continut(c).find(x => x.toLowerCase() === "d:" + n.toLowerCase()).slice(2);
  const inDsw = () => cwd === "dsw";
  const mergi = tinta => {
    /* cd relativ: dsw, dsw\curs, .., ~ */
    if (tinta === "~" || tinta === ACASA) return "";
    let c = cwd;
    for (const p of tinta.replace(/\//g, "\\").split("\\").filter(Boolean)){
      if (p === ".") continue;
      if (p === "..") { c = c.includes("\\") ? c.slice(0, c.lastIndexOf("\\")) : ""; continue; }
      if (!areDosar(c, p)) return null;
      c = (c ? c + "\\" : "") + numeDosar(c, p);
    }
    return c;
  };
  const instaleaza = (c, pk, dinLista) => {
    if (!pk.length) return scrie(c, ["!Specifică pachetele de instalat. Aici: pip install -r requirements.txt"]);
    instalate = [...new Set([...instalate, ...pk])]; facute.add("install");
    scrie(c, ["", ...pk.map((x, i) => `Collecting ${x}${dinLista ? ` (from -r requirements.txt (line ${i + 1}))` : ""}`),
      `~Successfully installed ${pk.join(" ")} (în dsw\\.venv)`]);
  };
  const pip = (c, rest) => {
    const r = rest.trim();
    if (/^-r\s+requirements\.txt$/i.test(r)){
      if (!continut(cwd).some(x => /:requirements\.txt$/i.test(x)))
        return scrie(c, ["!ERROR: Could not open requirements file: [Errno 2] No such file or directory: 'requirements.txt'",
          "!Fișierul requirements.txt se află în dsw. Intră mai întâi în acest folder."]);
      return instaleaza(c, ["pandas", "requests", "ipykernel"], true);
    }
    return instaleaza(c, r.split(/\s+/).filter(Boolean), false);
  };

  const ruleaza = brut => {
    const c = brut.trim(); if (!c) return;
    prAcum = pr();
    let m;
    if ((m = c.match(/^(cd|chdir|set-location)\s+(.+)$/i))){
      const t = m[2].trim().replace(/^["']|["']$/g, "");
      const nou = mergi(t);
      if (nou === null) scrie(c, [`!cd : Cannot find path '${cale()}\\${esc(t)}' because it does not exist.`]);
      else { cwd = nou; if (cwd === "dsw") facute.add("cd"); scrie(c, []); } }
    else if (/^cd$/i.test(c)) scrie(c, ["", cale()]);
    else if ((m = c.match(/^(mkdir|md)\s+(\S+)$/i))){
      if (areDosar(cwd, m[2])) scrie(c, [`!mkdir : An item with the specified name ${cale()}\\${esc(m[2])} already exists.`]);
      else { (FS[cwd] ||= []).push("d:" + m[2]); FS[(cwd ? cwd + "\\" : "") + m[2]] = [];
        scrie(c, ["", `    Directory: ${cale()}`, "", `d----   ${esc(m[2])}`,
          ...(m[2].toLowerCase().startsWith("dsw") || /proiect/i.test(m[2]) ? ["", "~Nu este nevoie de un folder nou: dsw există deja, din arhiva cursului."] : [])]); } }
    else if (/^(py|python3?)\s+-m\s+venv\s+\S+$/i.test(c)){
      const dir = c.split(/\s+/).pop();
      if (!inDsw()) scrie(c, ["", `!Ai creat ${esc(dir)} în ${cale()}, nu în dsw.`,
        cwd.startsWith("dsw\\") ? "!Mediul virtual se creează direct în dsw, lângă requirements.txt. Revino un nivel mai sus (cd ..) și creează-l acolo."
                                : "!Intră mai întâi în folderul cursului (cd dsw), apoi creează mediul acolo."]);
      else { cuVenv.add(cwd); facute.add("venv");
        if (!FS.dsw.includes("d:.venv")) FS.dsw.unshift("d:.venv");
        scrie(c, ["", `~Mediul virtual a fost creat în ${cale()}\\${esc(dir)}. Conținutul lui este gestionat de Python și nu se editează manual.`]); } }
    else if (/^(\.[\\/])?\.venv[\\/]scripts[\\/]activate(\.ps1|\.bat)?$/i.test(c)){
      if (!cuVenv.has(cwd)) scrie(c, [`!${esc(c)} : The term '${esc(c)}' is not recognized.`, "!În acest folder nu există .venv. Verifică dacă ești în dsw și dacă mediul a fost creat."]);
      else if (!politica) scrie(c, [
        `!${esc(c)} : File ${cale()}\\.venv\\Scripts\\Activate.ps1 cannot be loaded because running scripts is disabled on this system.`,
        "!Rulează o singură dată: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser",
        "!apoi activează din nou mediul."]);
      else { activ = true; facute.add("activ"); scrie(c, []); } }
    else if (/^set-executionpolicy\b/i.test(c)){
      if (!/remotesigned/i.test(c)) scrie(c, ["!Folosește: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser"]);
      else { politica = true; scrie(c, ["", "~Politica de execuție a fost modificată. Mediul poate fi activat acum."]); } }
    else if (/^source\s+\.venv\/bin\/activate$/i.test(c))
      scrie(c, ["!Aceasta este comanda pentru macOS. În PowerShell: .\\.venv\\Scripts\\Activate.ps1"]);
    else if ((m = c.match(/^(?:\.[\\/])?\.venv[\\/]scripts[\\/]python(?:\.exe)?\s+-m\s+pip\s+install\s*(.*)$/i))){
      if (!cuVenv.has(cwd)) scrie(c, ["!În acest folder nu există .venv. Creează-l mai întâi, în dsw."]);
      else pip(c, m[1]); }
    else if ((m = c.match(/^(?:python\s+-m\s+)?pip3?\s+install\s*(.*)$/i))){
      if (!activ) scrie(c, ["!Atenție: fără un mediu activ, pip instalează pachetele în instalarea globală de Python.",
        "!Activează mai întâi mediul: .\\.venv\\Scripts\\Activate.ps1"]);
      else pip(c, m[1]); }
    else if (/^(pip3?\s+list|(\.[\\/])?\.venv[\\/]scripts[\\/]python(\.exe)?\s+-m\s+pip\s+list)$/i.test(c)){
      const glob = /^pip/i.test(c) && !activ;
      scrie(c, ["", "Package    Version", "---------- -------", ...(glob ? ["(pachetele instalării globale, nu ale mediului)"]
        : instalate.length ? instalate.map(x => `${x.padEnd(11)}…`) : ["pip        …", "(niciun pachet instalat încă)"])]); }
    else if (/^(dir|ls|gci|get-childitem)$/i.test(c)){
      facute.add("dir");
      scrie(c, ["", `    Directory: ${cale()}`, "", ...continut(cwd).map(x => {
        const [fel, n] = x.startsWith("d:") ? ["d----", x.slice(2)] : x.split(/:(.*)/s);
        return `${fel}   ${esc(n)}${n === ".venv" ? '   <span class="c"># gestionat de Python, nu se editează</span>' : ""}`;
      })]); }
    else if (/^deactivate$/i.test(c)){ if (activ) { activ = false; scrie(c, []); } else scrie(c, ["!Niciun mediu activ."]); }
    else if (/^(ajutor|help)$/i.test(c)) scrie(c, ["", "Comenzile, în ordine:",
      "  cd dsw", "  py -m venv .venv", "  .\\.venv\\Scripts\\Activate.ps1",
      "  pip install -r requirements.txt", "  dir",
      "Alte comenzi: cd .., pip list, deactivate, curata"]);
    else if (/^(curata|clear|cls)$/i.test(c)) linii = ["_"];
    else scrie(c, [`!${esc(c.split(" ")[0])} : The term is not recognized. Comanda help afișează lista comenzilor.`]);
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
          ? "<b>Toate răspunsurile sunt corecte.</b> Distincția dintre <code>'2024'</code> și <code>2024</code> produce cele mai multe erori tăcute la citirea fișierelor."
          : "<b>Unele răspunsuri sunt greșite.</b> Aceste cazuri sunt reluate la curățarea datelor, în lecția 4."}</p>
        <button class="btn btn--mic" id="din-nou" type="button">Reia exercițiul</button>`;
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
      gazda.querySelector(".tip__fb").innerHTML = `<b>${bun?"Corect.":"Incorect."}</b> ${q.e}`;
      setTimeout(() => { i++; deseneaza(); }, bun ? 1150 : 2300);
    });
  };
  deseneaza();
};

/* --- 4. Explorator JSON --------------------------------------------------- */
C.json = (gazda, date) => {
  const DESC = {
    tablou:"Listă ordonată. Elementele se accesează după poziție, începând de la 0.",
    obiect:"Perechi cheie-valoare. În Python devine dicționar.",
    text:"Șir de caractere. Chiar dacă arată ca un an, rămâne text până la o conversie explicită.",
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
    <label class="jsn__scrie"><span>Scrie calea</span>
      <input type="text" spellcheck="false" autocomplete="off" placeholder='${rad}[1][0]["date"]'></label>
    <div class="jsn__arb">${randuri.map((r,k) =>
      `<span class="jsn__r" data-k="${k}">${r.html}</span>`).join("")}</div>
    <p class="jsn__out">Scrie o cale sau apasă pe un rând din arbore.</p>`;
  const out = gazda.querySelector(".jsn__out");
  const inp = gazda.querySelector(".jsn__scrie input");

  /* drumul scris de student: îl parcurgem pas cu pas, ca să spunem unde se rupe */
  const ce = v => ({ tablou: "o listă", obiect: "un dicționar", text: "un text", "număr": "un număr", null: "null", boolean: "o valoare logică" })[fel(v)];
  const fara = t => t.replace(/\s+/g, "").replace(/'/g, '"');
  function parcurge(text){
    const t = fara(text);
    if (!t.startsWith(rad)) return { err: `Calea pornește de la <code>${rad}</code>.` };
    const re = /\[(\d+)\]|\["([^"]*)"\]/y;
    let i = rad.length, v = date.date, cale = rad;
    re.lastIndex = i;
    while (i < t.length){
      re.lastIndex = i;
      const m = re.exec(t);
      if (!m) return { err: `Expresia de după <code>${cale}</code> nu este validă. Un pas este <code>[0]</code> (poziție) sau <code>["cheie"]</code> (cheie).`, cale };
      if (m[1] !== undefined){
        const n = +m[1];
        if (!Array.isArray(v)) return { err: `<code>${cale}</code> este ${ce(v)}, nu o listă: aici se cere o cheie între ghilimele, nu o poziție.`, cale };
        if (n >= v.length) return { err: `<code>${cale}</code> are doar ${v.length} elemente, pe pozițiile de la 0 la ${v.length - 1}.`, cale };
        v = v[n]; cale += `[${n}]`;
      } else {
        const k = m[2];
        if (!v || typeof v !== "object" || Array.isArray(v))
          return { err: `<code>${cale}</code> este ${ce(v)}, nu un dicționar: aici se cere o poziție, de exemplu <code>[0]</code>.`, cale };
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
    if (!inp.value.trim()){ out.innerHTML = "Scrie o cale sau apasă pe un rând din arbore."; return; }
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
      `<p style="color:var(--nu);font-family:var(--sans);font-size:var(--t2)">
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
  box.innerHTML = `<p class="intai__et">mai întâi, o predicție</p><p class="pz__q">${d.q}</p>
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
    p.innerHTML = `<b>${bine ? "Corect." : "Incorect."}</b> ${d.dupa || ""} <span class="intai__acum">Verifică rezultatul în componenta de mai jos.</span>`;
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
    ["nu am auzit de", "am citit despre", "am folosit o dată", "folosesc des"];
  const T = date.teme;
  const ales = new Array(T.length).fill(null);

  gazda.innerHTML = `
    <p class="ex__sarcina">${date.sarcina || "Pentru fiecare temă, alege nivelul actual. Răspunsurile nu se notează și nu sunt vizibile colegilor. Și prima coloană, bifată peste tot, este un răspuns valid."}</p>
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
      ? "<b>Mulțumim.</b> Cursul pornește de la noțiunile de bază."
      : medie < 2
        ? "<b>Mulțumim.</b> Există deja o bază; restul se construiește pe parcursul cursului."
        : "<b>Mulțumim.</b> Accentul cursului cade pe fluxul de lucru, nu pe sintaxă.";
    poarta(gazda, date.id, ales.join(","));
    try {
      const s = await import("/data-science-workflows/js/sesiune.js?v=78");
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
         <span class="trb__lc">list</span>se poate modifica
         <span class="trb__lc trb__lc--i">tuple</span>nu se poate modifica</p>` : ""}
      <div class="trb__i"><h5>${date.titlu || "Selectează un tip"}</h5>
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
    <p class="ex__sarcina">${date.sarcina || "Două-trei rânduri. Toate răspunsurile sunt citite de profesor."}</p>
    <div class="ast">
      <textarea class="ast__t" rows="4" maxlength="600" spellcheck="true"
        placeholder="${date.exemplu || "De exemplu: vreau să pot colecta singur date de pe un site și să le combin, fără să depind de altcineva."}"></textarea>
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
    out.innerHTML = `<b>Mulțumim.</b> ${date.multumesc
      || "Răspunsurile sunt citite înainte de cursul următor."}`;
    /* textul însuși ajunge și la poartă (legat de ora pornită), ca profesorul
       să-l vadă în rezultatele orei și pe tablă, nu doar cuvântul „scris” */
    poarta(gazda, date.id, t.value.trim());
    try {
      const s = await import("/data-science-workflows/js/sesiune.js?v=78");
      /* `tip` ajunge în jurnal și decide în ce sumar apare textul la profesor */
      await s.jurnal(date.tip || "asteptari", { text: t.value.trim().slice(0, 600) });
    } catch {}
  };
};
