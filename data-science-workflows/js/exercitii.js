/* ===========================================================================
   EXERCIȚII CU COD

   Două feluri, amândouă fără Python în browser: se verifică forma a ceea ce
   scrii, nu rezultatul rulării. E o alegere, nu o scurtătură. Un interpretor
   în pagină ar însemna câteva megaocteți descărcați la începutul orei, pe
   același wifi, de 25 de oameni deodată. Rularea adevărată se face în caiet,
   la ei în VS Code, unde și trebuie să se întâmple.

     <div class="ix" data-ix="cod">      completezi golurile dintr-un cod
     <div class="ix" data-ix="ordine">   pui liniile în ordinea corectă

   Amândouă contează ca poartă: nu treci la slide-ul următor până nu le faci,
   exact ca la verificări. Se salvează prin salveazaCod, deci apar la mine în
   panou ca activitate.
   =========================================================================== */

import { salveazaCod } from "./colectare.js?v=36";

const E = {};

const SVG_SUS = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19V6M6 11.5 12 5.5l6 6"/></svg>';
const SVG_JOS = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5v13M6 12.5l6 6 6-6"/></svg>';

const esc = s => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

/* Colorare minimală: suficient cât să semene cu un editor, fără bibliotecă.

   Se face dintr-o singură trecere, nu din patru `replace` unul peste altul.
   Varianta cu patru treceri avea un defect care se vedea pe ecran: prima
   trecere scotea un comentariu ca `<span class="c">#…</span>`, iar trecerea
   pentru șiruri găsea `"c"` din atributul proaspăt scris și îl împacheta la
   rândul ei. Pe pagină ieșea `"c">#` în loc de comentariu. Aici, textul deja
   colorat nu mai e niciodată recitit. */

const TIPARE = {
  py: /(#[^\n]*)|('(?:[^'\\]|\\.)*'|"(?:[^"\\]|\\.)*")|\b(import|from|as|def|return|if|else|elif|for|in|while|with|open|print|None|True|False|not|and|or|lambda|try|except|class)\b|\b(\d+(?:\.\d+)?)\b/g,
  sql: /(--[^\n]*)|('(?:[^']|'')*')|\b(CREATE|TABLE|PRIMARY|KEY|FOREIGN|REFERENCES|SELECT|FROM|WHERE|INSERT|INTO|VALUES|UPDATE|DELETE|NOT|NULL|DEFAULT|UNIQUE|CHAR|VARCHAR|TEXT|INT|INTEGER|BIGINT|SMALLINT|NUMERIC|REAL|BOOLEAN|DATE|TIMESTAMP|JSONB|JSON)\b|\b(\d+(?:\.\d+)?)\b/gi,
  sh: /(#[^\n]*)|('[^']*'|"[^"]*")|\b(cd|ls|mkdir|source|pip|python|git|echo|export|activate|install|freeze)\b|\b(\d+(?:\.\d+)?)\b/g
};

/** Ce limbă colorăm, după extensia numelui de fișier. */
function limba(fisier = ""){
  if (/\.sql$/i.test(fisier)) return "sql";
  if (/\.(sh|bash|txt)$/i.test(fisier)) return "sh";
  return "py";
}

function coloreaza(s, lb = "py"){
  const re = TIPARE[lb] || TIPARE.py;
  re.lastIndex = 0;
  let iesire = "", ultim = 0, m;
  while ((m = re.exec(s)) !== null){
    if (m[0] === ""){ re.lastIndex++; continue; }
    iesire += esc(s.slice(ultim, m.index));
    const cls = m[1] ? "c" : m[2] ? "s" : m[3] ? "k" : "n";
    iesire += `<span class="${cls}">${esc(m[0])}</span>`;
    ultim = m.index + m[0].length;
  }
  return iesire + esc(s.slice(ultim));
}

/** Normalizare înainte de comparație: spațiile și ghilimelele nu contează. */
const normal = s => String(s).trim()
  .replace(/\s+/g, " ")
  .replace(/[“”„]/g, '"')
  .replace(/[‘’]/g, "'");

/** Marchează exercițiul ca poartă trecută și anunță rulatorul de slide-uri. */
function gata(gazda, id){
  const ix = gazda.closest(".ix") || gazda;
  ix.classList.add("gata");
  document.dispatchEvent(new CustomEvent("poarta:gata", { detail:{ id } }));
}

function cadruJos(){
  return `<div class="ex__jos">
      <button class="btn btn--mic btn--tare" data-rol="verifica" type="button">Verifică</button>
      <button class="btn btn--mic" data-rol="din-nou" type="button" hidden>Încearcă din nou</button>
      <span class="ex__raspuns"></span>
    </div>
    <p class="ex__ex"></p>
    <p class="ex__stare"></p>`;
}

/* --------------------------------------------------------------------------
   Mediul de dinaintea exercițiului

   Nimeni nu scrie un filtru fără să se uite întâi la tabel. Panoul ăsta pune
   deasupra codului exact lucrurile pe care le tastezi primele într-un caiet,
   cu răspunsul deja scris: `head()`, `columns`, `dtypes`, `shape`.

   Nu rulează Python. Afișează ce ar afișa pandas pentru fișierul descris în
   `date`, cu rânduri adevărate din el. Dacă un exercițiu nu are `date`,
   panoul nu apare și nu se schimbă nimic.
   -------------------------------------------------------------------------- */

function consolaDate(z){
  if (!z || !z.coloane?.length) return "";
  const nume = z.nume || "d";
  const col  = z.coloane;
  const lat  = Math.max(...col.map(c => c.nume.length));
  const pad  = s => esc(s) + " ".repeat(Math.max(0, lat - s.length));

  /* head(): tabel adevărat, ca să se alinieze coloanele ca în terminal */
  const cap = (z.cap || []).map((r, i) => `<tr><th>${z.index?.[i] ?? i}</th>${
    r.map(v => `<td class="${typeof v === "number" ? "nr" : ""}">${esc(v)}</td>`)
     .join("")}</tr>`).join("");

  const vederi = {
    head: `<table class="cns__t"><thead><tr><th></th>${
             col.map(c => `<th>${esc(c.nume)}</th>`).join("")}</tr></thead>
           <tbody>${cap}</tbody></table>${
           z.capNota ? `<p class="cns__n">${z.capNota}</p>` : ""}`,
    columns: `<pre class="cns__p">Index([${col.map(c => `'${esc(c.nume)}'`).join(", ")}],\n      dtype='object')</pre>`,
    dtypes: `<pre class="cns__p">${col.map(c => `${pad(c.nume)}    ${esc(c.tip)}`).join("\n")}\ndtype: object</pre>`,
    shape: `<pre class="cns__p">(${z.randuri ?? "?"}, ${col.length})</pre>`,
    ce: `<dl class="cns__d">${col.map(c =>
           `<dt>${esc(c.nume)}</dt><dd>${c.d || ""}</dd>`).join("")}</dl>`
  };

  const file = [
    ["head", `${nume}.head()`], ["columns", `${nume}.columns`],
    ["dtypes", `${nume}.dtypes`], ["shape", `${nume}.shape`],
    ["ce", "ce înseamnă"]
  ];

  return `<div class="cns">
    <div class="cns__cap">
      <span class="cns__f">${esc(z.fisier || "date")}</span>
      <span class="cns__m">${z.randuri ? z.randuri.toLocaleString("ro-RO") + " rânduri × " : ""}${col.length} coloane</span>
    </div>
    <div class="cns__file" role="tablist">${file.map(([k, et], i) =>
      `<button class="cns__fi${i ? "" : " on"}" data-v="${k}" type="button">${esc(et)}</button>`).join("")}</div>
    ${file.map(([k], i) => `<div class="cns__v" data-v="${k}"${i ? " hidden" : ""}>${vederi[k]}</div>`).join("")}
  </div>`;
}

/** Leagă butoanele panoului. Fără el, panoul rămâne pe prima vedere. */
function legaConsola(gazda){
  const c = gazda.querySelector(".cns");
  if (!c) return;
  c.querySelectorAll(".cns__fi").forEach(b => b.onclick = () => {
    c.querySelectorAll(".cns__fi").forEach(x => x.classList.toggle("on", x === b));
    c.querySelectorAll(".cns__v").forEach(v => v.hidden = v.dataset.v !== b.dataset.v);
  });
}

/* ==========================================================================
   1. Completează golurile
   ========================================================================== */

E.cod = (gazda, d) => {
  const id = d.id || "cod";
  gazda.closest(".ix")?.classList.add("exc");

  /* `cod` e un bloc de text cu {{1}}, {{2}} … în locurile de completat */
  /* Golurile se taie din linie ÎNAINTE de colorare. Altfel colorarea vede
     cifra din {{1}} ca pe un număr, o înfășoară în <span>, iar tiparul nu se
     mai potrivește și linia rămâne fără câmp de completat. */
  const camp = k => {
    const g = d.goluri[k] || {};
    const lat = Math.max(5, (g.ok?.[0] || "").length + 2);
    return `<input class="gol" data-k="${k}" size="${lat}" spellcheck="false"
              autocapitalize="off" autocomplete="off"
              placeholder="${esc(g.ajutor || "…")}" aria-label="Golul ${k}">`;
  };
  const lb = limba(d.fisier);
  const linii = d.cod.replace(/\t/g, "    ").split("\n");
  const corp = linii.map(l => {
    const bucati = l.split(/\{\{(\w+)\}\}/);   // text, cheie, text, cheie, …
    const h = bucati.map((x, i) => i % 2 ? camp(x) : coloreaza(x, lb)).join("");
    return h || "&nbsp;";
  }).join("\n");

  gazda.innerHTML = `
    ${d.sarcina ? `<p class="ex__sarcina">${d.sarcina}</p>` : ""}
    ${consolaDate(d.date)}
    <div class="ed">
      <div class="ed__bara"><span class="ed__pct"><i></i><i></i><i></i></span>
        <span class="ed__nume">${esc(d.fisier || "exercitiu.py")}</span></div>
      <div class="ed__corp">
        <div class="ed__nr">${linii.map((_, i) => `<span>${i + 1}</span>`).join("")}</div>
        <div class="ed__cod">${corp}</div>
      </div>
    </div>
    ${cadruJos()}`;

  legaConsola(gazda);

  const goluri = [...gazda.querySelectorAll(".gol")];
  const btV = gazda.querySelector('[data-rol="verifica"]');
  const btN = gazda.querySelector('[data-rol="din-nou"]');
  const out = gazda.querySelector(".ex__raspuns");
  const ex  = gazda.querySelector(".ex__ex");
  const st  = gazda.querySelector(".ex__stare");

  goluri.forEach(g => g.addEventListener("keydown", e => {
    if (e.key === "Enter"){ e.preventDefault(); btV.click(); }
  }));

  btV.onclick = async () => {
    let bune = 0;
    goluri.forEach(g => {
      const asteptat = (d.goluri[g.dataset.k]?.ok || []).map(normal);
      const ok = asteptat.includes(normal(g.value));
      g.classList.toggle("bun", ok);
      g.classList.toggle("rau", !ok);
      if (ok) bune++;
    });
    const tot = bune === goluri.length;
    out.innerHTML = tot
      ? `<b>Corect.</b> ${d.laBine || ""}`
      : `<b>${bune} din ${goluri.length}.</b> ${d.laRau || "Golurile roșii nu sunt încă bune."}`;
    btN.hidden = tot;
    if (tot){
      btV.disabled = true;
      goluri.forEach(g => g.disabled = true);
      ex.classList.add("vazut");
      ex.innerHTML = d.explicatie || "";
      gata(gazda, id);
      const salvat = await salveazaCod({
        exercitiuId: id,
        cod: goluri.map(g => `${g.dataset.k}=${g.value}`).join(" | "),
        trecut: true
      });
      st.textContent = salvat ? "Rezolvare înregistrată."
                              : "Nu e înregistrată: nu ești autentificat.";
      st.classList.add("vazut");
    }
  };
  btN.onclick = () => {
    goluri.forEach(g => { g.classList.remove("bun", "rau"); });
    out.textContent = ""; btN.hidden = true;
    goluri[0]?.focus();
  };
};

/* ==========================================================================
   2. Pune liniile în ordine
   ========================================================================== */

E.ordine = (gazda, d) => {
  const id = d.id || "ordine";
  gazda.closest(".ix")?.classList.add("exc");

  /* amestecăm, dar niciodată în ordinea corectă din prima */
  const n = d.linii.length;
  let ordine = d.linii.map((_, i) => i);
  do { ordine = amesteca(ordine); } while (ordine.every((v, i) => v === i) && n > 1);

  gazda.innerHTML = `
    ${d.sarcina ? `<p class="ex__sarcina">${d.sarcina}</p>` : ""}
    <div class="ord"></div>
    ${cadruJos()}`;

  const lista = gazda.querySelector(".ord");
  const btV = gazda.querySelector('[data-rol="verifica"]');
  const btN = gazda.querySelector('[data-rol="din-nou"]');
  const out = gazda.querySelector(".ex__raspuns");
  const ex  = gazda.querySelector(".ex__ex");
  const st  = gazda.querySelector(".ex__stare");

  function deseneaza(){
    lista.innerHTML = ordine.map((k, poz) => `
      <div class="ord__r" data-poz="${poz}">
        <span class="ord__p">${poz + 1}</span>
        <span class="ord__t">${coloreaza(d.linii[k])}</span>
        <span class="ord__b">
          <button type="button" data-m="-1" ${poz === 0 ? "disabled" : ""}
            aria-label="Mută mai sus">${SVG_SUS}</button>
          <button type="button" data-m="1" ${poz === n - 1 ? "disabled" : ""}
            aria-label="Mută mai jos">${SVG_JOS}</button>
        </span>
      </div>`).join("");
  }
  deseneaza();

  lista.addEventListener("click", e => {
    const b = e.target.closest("button[data-m]");
    if (!b) return;
    const poz = +b.closest(".ord__r").dataset.poz;
    const la = poz + (+b.dataset.m);
    if (la < 0 || la >= n) return;
    [ordine[poz], ordine[la]] = [ordine[la], ordine[poz]];
    deseneaza();
    out.textContent = "";
  });

  btV.onclick = async () => {
    const randuri = [...lista.querySelectorAll(".ord__r")];
    let bune = 0;
    ordine.forEach((k, poz) => {
      const ok = k === poz;
      randuri[poz].classList.toggle("bun", ok);
      randuri[poz].classList.toggle("rau", !ok);
      if (ok) bune++;
    });
    const tot = bune === n;
    out.innerHTML = tot
      ? `<b>Corect.</b> ${d.laBine || ""}`
      : `<b>${bune} din ${n} pe locul lor.</b> ${d.laRau || "Mută-le pe celelalte."}`;
    btN.hidden = tot;
    if (tot){
      btV.disabled = true;
      lista.querySelectorAll("button").forEach(b => b.disabled = true);
      ex.classList.add("vazut");
      ex.innerHTML = d.explicatie || "";
      gata(gazda, id);
      const salvat = await salveazaCod({
        exercitiuId: id, cod: ordine.join(","), trecut: true
      });
      st.textContent = salvat ? "Rezolvare înregistrată."
                              : "Nu e înregistrată: nu ești autentificat.";
      st.classList.add("vazut");
    }
  };
  btN.onclick = () => {
    lista.querySelectorAll(".ord__r").forEach(r => r.classList.remove("bun", "rau"));
    out.textContent = ""; btN.hidden = true;
  };
};

function amesteca(a){
  const b = a.slice();
  for (let i = b.length - 1; i > 0; i--){
    const j = Math.floor(Math.random() * (i + 1));
    [b[i], b[j]] = [b[j], b[i]];
  }
  return b;
}

export default E;

/* ==========================================================================
   3. Sortare în două coșuri
   Pentru distincții binare care se rețin prin mână, nu prin citit:
   text / binar, monadic / diadic, lizibil / nelizibil.
   ========================================================================== */

E.sortare = (gazda, d) => {
  const id = d.id || "sortare";
  gazda.closest(".ix")?.classList.add("exc");
  let puse = {};            /* eticheta elementului -> cosul ales */

  gazda.innerHTML = `
    ${d.sarcina ? `<p class="ex__sarcina">${d.sarcina}</p>` : ""}
    <div class="srt__banc" id="banc">${d.elemente.map((e, i) =>
      `<button class="srt__e" data-i="${i}" type="button">${esc(e.t)}</button>`).join("")}</div>
    <div class="srt__cosuri">
      ${d.cosuri.map((c, k) => `<div class="srt__c" data-k="${k}">
        <span class="srt__ct">${esc(c.t)}</span>
        <span class="srt__cd">${esc(c.d || "")}</span>
        <div class="srt__in"></div></div>`).join("")}
    </div>
    ${cadruJos()}`;

  const banc = gazda.querySelector("#banc");
  const cosuri = [...gazda.querySelectorAll(".srt__c")];
  const btV = gazda.querySelector('[data-rol="verifica"]');
  const btN = gazda.querySelector('[data-rol="din-nou"]');
  const out = gazda.querySelector(".ex__raspuns");
  const ex  = gazda.querySelector(".ex__ex");
  const st  = gazda.querySelector(".ex__stare");
  let ales = null;

  /* două atingeri: alegi elementul, apoi coșul. Merge și cu mouse, și pe telefon. */
  gazda.addEventListener("click", e => {
    const el = e.target.closest(".srt__e");
    const cos = e.target.closest(".srt__c");
    /* Când am deja ceva ales, orice atingere într-un coș e o punere — chiar
       dacă nimeresc peste o etichetă pusă acolo mai devreme. Altfel, un coș
       plin devine imposibil de nimerit, iar cel care mută crede că nu merge. */
    if (el && !(cos && ales && ales !== el)){
      if (ales === el){ ales.classList.remove("ales"); ales = null; return; }
      gazda.querySelectorAll(".srt__e").forEach(x => x.classList.remove("ales"));
      el.classList.add("ales"); ales = el;
      cosuri.forEach(c => c.classList.add("tinta"));
      return;
    }
    if (cos && ales){
      cos.querySelector(".srt__in").appendChild(ales);
      puse[ales.dataset.i] = +cos.dataset.k;
      ales.classList.remove("ales"); ales = null;
      cosuri.forEach(c => c.classList.remove("tinta"));
      out.textContent = "";
      btV.disabled = Object.keys(puse).length < d.elemente.length;
      return;
    }
    if (e.target.closest("#banc") && ales){
      banc.appendChild(ales);
      delete puse[ales.dataset.i];
      ales.classList.remove("ales"); ales = null;
      cosuri.forEach(c => c.classList.remove("tinta"));
      btV.disabled = true;
    }
  });
  btV.disabled = true;

  btV.onclick = async () => {
    let bune = 0;
    gazda.querySelectorAll(".srt__e").forEach(el => {
      const i = +el.dataset.i;
      const ok = puse[i] === d.elemente[i].cos;
      el.classList.toggle("bun", ok); el.classList.toggle("rau", !ok);
      if (ok) bune++;
    });
    const tot = bune === d.elemente.length;
    out.innerHTML = tot ? `<b>Tot corect.</b> ${d.laBine || ""}`
                        : `<b>${bune} din ${d.elemente.length}.</b> ${d.laRau || ""}`;
    btN.hidden = tot;
    if (tot){
      btV.disabled = true;
      ex.classList.add("vazut"); ex.innerHTML = d.explicatie || "";
      gata(gazda, id);
      const salvat = await salveazaCod({ exercitiuId:id,
        cod:JSON.stringify(puse), trecut:true });
      st.textContent = salvat ? "Rezolvare înregistrată."
                              : "Nu e înregistrată: nu ești autentificat.";
      st.classList.add("vazut");
    }
  };
  btN.onclick = () => {
    gazda.querySelectorAll(".srt__e").forEach(el => el.classList.remove("bun","rau"));
    out.textContent = ""; btN.hidden = true;
  };
};

/* ==========================================================================
   4. Dovada: ai făcut-o cu adevărat?
   Fiecare rând cere o comandă rulată la tine și textul pe care ea îl scoate.
   Nu se poate completa din cap: ieșirea depinde de starea calculatorului tău.
   ========================================================================== */

E.dovada = (gazda, d) => {
  const id = d.id || "dovada";
  gazda.closest(".ix")?.classList.add("exc");

  gazda.innerHTML = `
    ${d.sarcina ? `<p class="ex__sarcina">${d.sarcina}</p>` : ""}
    <div class="dov">${d.pasi.map((p, i) => `
      <div class="dov__r" data-i="${i}">
        <div class="dov__sus"><span class="dov__n">${i + 1}</span>
          <span class="dov__t">${p.t}</span>
          <span class="dov__s" data-s="${i}"></span></div>
        <div class="dov__cmd"><code>${esc(p.cmd)}</code>
          <button class="dov__copie" data-c="${i}" type="button">copiază</button></div>
        <input class="dov__in" data-i="${i}" spellcheck="false" autocomplete="off"
          placeholder="${esc(p.gol || "lipește aici ce a scris terminalul")}">
        <p class="dov__aj" data-a="${i}"></p>
      </div>`).join("")}</div>
    ${cadruJos()}`;

  const btV = gazda.querySelector('[data-rol="verifica"]');
  const btN = gazda.querySelector('[data-rol="din-nou"]');
  const out = gazda.querySelector(".ex__raspuns");
  const ex  = gazda.querySelector(".ex__ex");
  const st  = gazda.querySelector(".ex__stare");
  btN.textContent = "Mai încerc";

  gazda.querySelectorAll(".dov__copie").forEach(b => b.onclick = async () => {
    try { await navigator.clipboard.writeText(d.pasi[+b.dataset.c].cmd);
          b.textContent = "copiat"; setTimeout(() => b.textContent = "copiază", 1400); }
    catch { b.textContent = "selectează manual"; }
  });

  btV.onclick = async () => {
    let bune = 0;
    d.pasi.forEach((p, i) => {
      const camp = gazda.querySelector(`.dov__in[data-i="${i}"]`);
      const sem  = gazda.querySelector(`.dov__s[data-s="${i}"]`);
      const aj   = gazda.querySelector(`.dov__aj[data-a="${i}"]`);
      const val  = (camp.value || "").trim();
      const ok   = val !== "" && new RegExp(p.cauta, "i").test(val);
      camp.classList.toggle("bun", ok); camp.classList.toggle("rau", !ok);
      sem.textContent = ok ? "✓" : (val ? "✕" : "—");
      sem.className = `dov__s ${ok ? "bun" : val ? "rau" : ""}`;
      aj.textContent = ok ? "" : (val ? (p.daca_nu || "Nu pare să fie ieșirea comenzii de mai sus.") : "");
      aj.classList.toggle("vazut", !ok && !!val);
      if (ok) bune++;
    });
    const tot = bune === d.pasi.length;
    out.innerHTML = tot ? `<b>Gata.</b> ${d.laBine || ""}`
                        : `<b>${bune} din ${d.pasi.length}.</b> ${d.laRau || ""}`;
    btN.hidden = tot;
    if (tot){
      btV.disabled = true;
      gazda.querySelectorAll(".dov__in").forEach(x => x.disabled = true);
      ex.classList.add("vazut"); ex.innerHTML = d.explicatie || "";
      gata(gazda, id);
      const salvat = await salveazaCod({ exercitiuId:id, trecut:true,
        cod:[...gazda.querySelectorAll(".dov__in")].map(x => x.value).join(" ⏎ ") });
      st.textContent = salvat ? "Înregistrat. Apare la mine în panou."
                              : "Nu e înregistrat: nu ești autentificat.";
      st.classList.add("vazut");
    }
  };
  btN.onclick = () => {
    gazda.querySelectorAll(".dov__in").forEach(x => x.classList.remove("bun","rau"));
    out.textContent = ""; btN.hidden = true;
  };
};
