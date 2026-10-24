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

import { salveazaCod } from "./colectare.js?v=63";

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

/* Tema „DSW”, ca un theme de VS Code, din paleta cursului: cuvinte-cheie
   teal, șiruri chihlimbar, numere și True/False/None roz, funcții incluse
   (print, len, type…) aurii, apeluri de funcții și metode salvie,
   comentarii gri-verzui, cursive. Grupurile din tipar dau clasele:
     1 c comentariu · 2 s șir · 3 k cuvânt-cheie · 4 v constantă
     5 b funcție inclusă · 6 f apel · 7 n număr */
const TIPARE = {
  py: /(#[^\n]*)|((?:f|r|b)?'(?:[^'\\]|\\.)*'|(?:f|r|b)?"(?:[^"\\]|\\.)*")|\b(import|from|as|def|return|if|else|elif|for|in|while|with|not|and|or|is|lambda|try|except|class|pass|break|continue|yield|global)\b|\b(None|True|False)\b|\b(print|len|type|int|str|float|bool|list|dict|tuple|set|range|open|sorted|sum|min|max|round|abs|enumerate|zip|isinstance)\b(?=\s*\()|\b([A-Za-z_]\w*)(?=\s*\()|\b(\d+(?:\.\d+)?)\b/g,
  sql: /(--[^\n]*)|('(?:[^']|'')*')|\b(CREATE|TABLE|PRIMARY|KEY|FOREIGN|REFERENCES|SELECT|FROM|WHERE|JOIN|LEFT|INNER|OUTER|ON|AND|OR|AS|ORDER|GROUP|BY|DESC|ASC|LIMIT|HAVING|COUNT|SUM|AVG|DISTINCT|INSERT|INTO|VALUES|UPDATE|DELETE|NOT|NULL|DEFAULT|UNIQUE|CHAR|VARCHAR|TEXT|INT|INTEGER|BIGINT|SMALLINT|NUMERIC|REAL|BOOLEAN|DATE|TIMESTAMP|JSONB|JSON)\b|\b(\d+(?:\.\d+)?)\b/gi,
  sh: /(#[^\n]*)|('[^']*'|"[^"]*")|\b(cd|ls|mkdir|source|pip|python|git|echo|export|activate|install|freeze)\b|\b(\d+(?:\.\d+)?)\b/g
};

/** Ce limbă colorăm, după extensia numelui de fișier. */
function limba(fisier = ""){
  if (/\.sql$/i.test(fisier)) return "sql";
  if (/\.(sh|bash|txt)$/i.test(fisier)) return "sh";
  return "py";
}

export function coloreaza(s, lb = "py"){
  const re = TIPARE[lb] || TIPARE.py;
  re.lastIndex = 0;
  let iesire = "", ultim = 0, m;
  while ((m = re.exec(s)) !== null){
    if (m[0] === ""){ re.lastIndex++; continue; }
    iesire += esc(s.slice(ultim, m.index));
    const cls = m[1] ? "c" : m[2] ? "s" : m[3] ? "k" : m[4] ? "v"
              : m[5] ? "b" : m[6] ? "f" : "n";
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

/* --- indiciul și ieșirea ---------------------------------------------------
   Fiecare exercițiu de cod are un buton de indiciu. Primul clic spune ideea
   (din `indiciu`, sau din ce cere fiecare gol); al doilea arată începutul
   răspunsului. Nu dă rezolvarea întreagă: o completezi tu.

   După ce e corect, apare ce ar afișa codul dacă l-ai rula (`iesire`), ca
   într-un terminal: vezi efectul, nu doar bifa verde. */
function iesireHTML(t){
  return t ? `<div class="ex__out"><span class="ex__out-et">ieșire</span><pre>${esc(t)}</pre></div>` : "";
}
function arataIesire(gazda, t){
  const g = gazda.querySelector(".ex__iesire");
  if (!g || !t) return;
  g.innerHTML = iesireHTML(t);
  const pre = g.querySelector("pre");
  const tot = pre.textContent; pre.textContent = "";
  let i = 0;
  const pas = () => { pre.textContent = tot.slice(0, i += 3); if (i < tot.length) setTimeout(pas, 12); };
  if (matchMedia("(prefers-reduced-motion: reduce)").matches) pre.textContent = tot; else pas();
}
function legaIndiciu(gazda, nivele){
  const b = gazda.querySelector('[data-rol="indiciu"]');
  const g = gazda.querySelector(".ex__ind");
  if (!b || !g) return;
  let k = 0;
  b.onclick = () => {
    const lista = (typeof nivele === "function" ? nivele() : nivele).filter(Boolean);
    if (!lista.length) return;
    g.innerHTML = lista.slice(0, k + 1).map(t => `<p>💡 ${t}</p>`).join("");
    g.classList.add("vazut");
    k = Math.min(k + 1, lista.length - 1);
    b.textContent = k >= lista.length - 1 && g.children.length >= lista.length ? "Indiciu" : "Încă un indiciu";
  };
}
function stareSalvare(salvat, gazda){
  if (gazda.closest(".ix")?.classList.contains("liber")) return "Exercițiu de încercat: nu se notează.";
  return salvat ? "Rezolvare înregistrată." : "Nu e înregistrată: nu ești autentificat.";
}
function sarbatoare(gazda){
  const ix = gazda.closest(".ix") || gazda;
  ix.classList.remove("ura"); void ix.offsetWidth; ix.classList.add("ura");
}

function cadruJos(eticheta = "▶ Rulează"){
  return `<div class="ex__jos">
      <button class="btn btn--mic btn--tare" data-rol="verifica" type="button">${eticheta}</button>
      <button class="btn btn--mic btn--ind" data-rol="indiciu" type="button">Indiciu</button>
      <button class="btn btn--mic" data-rol="din-nou" type="button" hidden>Încearcă din nou</button>
      <span class="ex__raspuns"></span>
    </div>
    <div class="ex__ind"></div>
    <div class="ex__iesire"></div>
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
    const lat = Math.max(5, (g.ok?.[0] || "").length + 2, (g.ajutor || "").length + 2);
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
  /* indiciul: întâi ideea, apoi începutul fiecărui gol încă greșit */
  legaIndiciu(gazda, () => [
    d.indiciu || goluri.map(g => d.goluri[g.dataset.k]?.ajutor).filter(Boolean)
                  .map((a, i) => `golul ${i + 1}: ${a}`).join(" · "),
    "Începutul răspunsului: " + goluri.filter(g => !g.classList.contains("bun")).map(g => {
      const r = String(d.goluri[g.dataset.k]?.ok?.[0] || "");
      return `<code>${esc(r.slice(0, Math.max(1, Math.ceil(r.length / 3))))}…</code>`;
    }).join(" · ")
  ]);

  btV.onclick = async () => {
    let bune = 0;
    goluri.forEach(g => {
      const gg = d.goluri[g.dataset.k] || {};
      const asteptat = (gg.ok || []).map(normal);
      /* un gol poate accepta orice potrivire a unui tipar (de ex. orice
         adresă de email între ghilimele), nu doar o listă fixă */
      const ok = asteptat.includes(normal(g.value)) || (gg.re ? new RegExp(gg.re).test(normal(g.value)) : false);
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
      arataIesire(gazda, d.iesire);
      sarbatoare(gazda);
      gata(gazda, id);
      const salvat = await salveazaCod({
        exercitiuId: id,
        cod: goluri.map(g => `${g.dataset.k}=${g.value}`).join(" | "),
        trecut: true
      });
      st.textContent = stareSalvare(salvat, gazda);
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
    ${cadruJos("Verifică ordinea")}`;

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
  legaIndiciu(gazda, () => [
    d.indiciu || "Întreabă-te: ce trebuie să existe înainte ca linia asta să poată rula?",
    `Prima linie e: <code>${esc(d.linii[0])}</code>`
  ]);

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

  /* consecinte: {indexul corect al liniei: ce se strică dacă nu e la locul ei}.
     Se arată pentru primul rând greșit, ca greșeala să spună ceva, nu doar „nu”. */
  function consecinta(){
    if (!d.consecinte) return "";
    const poz = ordine.findIndex((k, p) => k !== p);
    const k = ordine[poz];
    const t = d.consecinte[k] ?? d.consecinte[String(k)];
    return t ? `Pe locul ${poz + 1} ai pus <i>${esc(d.linii[k].split(":")[0])}</i>. ${t}` : "";
  }
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
      : `<b>${bune} din ${n} pe locul lor.</b> ${consecinta() || d.laRau || "Mută-le pe celelalte."}`;
    btN.hidden = tot;
    if (tot){
      btV.disabled = true;
      lista.querySelectorAll("button").forEach(b => b.disabled = true);
      ex.classList.add("vazut");
      ex.innerHTML = d.explicatie || "";
      arataIesire(gazda, d.iesire);
      sarbatoare(gazda);
      gata(gazda, id);
      const salvat = await salveazaCod({
        exercitiuId: id, cod: ordine.join(","), trecut: true
      });
      st.textContent = stareSalvare(salvat, gazda);
      st.classList.add("vazut");
    }
  };
  btN.onclick = () => {
    lista.querySelectorAll(".ord__r").forEach(r => r.classList.remove("bun", "rau"));
    out.textContent = ""; btN.hidden = true;
  };
};

/* ==========================================================================
   3. Ce afișează? — citești codul și ghicești ce iese
   Cel mai scurt drum spre un concept: nu scrii nimic, doar citești și alegi.
   Greșeala e ieftină și se vede pe loc ce ar fi afișat de fapt.
     { id, fisier, cod, intrebare, variante:[...], corect, explicatie,
       indiciu, iesire }
   ========================================================================== */

E.prezice = (gazda, d) => {
  const id = d.id || "prezice";
  gazda.closest(".ix")?.classList.add("exc");
  const lb = limba(d.fisier);
  const linii = String(d.cod || "").replace(/\t/g, "    ").split("\n");
  gazda.innerHTML = `
    ${d.sarcina ? `<p class="ex__sarcina">${d.sarcina}</p>` : ""}
    <div class="ed">
      <div class="ed__bara"><span class="ed__pct"><i></i><i></i><i></i></span>
        <span class="ed__nume">${esc(d.fisier || "exercitiu.py")}</span></div>
      <div class="ed__corp">
        <div class="ed__nr">${linii.map((_, i) => `<span>${i + 1}</span>`).join("")}</div>
        <div class="ed__cod">${linii.map(l => coloreaza(l, lb) || "&nbsp;").join("\n")}</div>
      </div>
    </div>
    <p class="pz__q">${d.intrebare || "Ce afișează?"}</p>
    <div class="pz__v">${(d.variante || []).map((v, i) =>
      `<button type="button" class="pz__b" data-i="${i}"><code>${esc(v)}</code></button>`).join("")}</div>
    <div class="ex__jos">
      <button class="btn btn--mic btn--ind" data-rol="indiciu" type="button">Indiciu</button>
      <span class="ex__raspuns"></span>
    </div>
    <div class="ex__ind"></div>
    <div class="ex__iesire"></div>
    <p class="ex__ex"></p>
    <p class="ex__stare"></p>`;
  const out = gazda.querySelector(".ex__raspuns");
  const ex  = gazda.querySelector(".ex__ex");
  const st  = gazda.querySelector(".ex__stare");
  legaIndiciu(gazda, [d.indiciu || "Citește rândul cu print și întreabă-te ce tip are valoarea dinăuntru."]);
  let incercari = 0;
  gazda.querySelectorAll(".pz__b").forEach(b => b.onclick = async () => {
    if (gazda.closest(".ix")?.classList.contains("gata")) return;
    incercari++;
    const ok = +b.dataset.i === +d.corect;
    b.classList.add(ok ? "bun" : "rau");
    if (!ok){
      b.disabled = true;
      out.innerHTML = `<b>Nu chiar.</b> ${d.laRau || "Mai încearcă: uită-te încă o dată la tipuri."}`;
      return;
    }
    gazda.querySelectorAll(".pz__b").forEach(x => x.disabled = true);
    out.innerHTML = `<b>${incercari === 1 ? "Din prima!" : "Corect."}</b> ${d.laBine || ""}`;
    ex.classList.add("vazut");
    ex.innerHTML = d.explicatie || "";
    arataIesire(gazda, d.iesire ?? d.variante[d.corect]);
    sarbatoare(gazda);
    gata(gazda, id);
    const salvat = await salveazaCod({ exercitiuId: id, cod: String(d.variante[+b.dataset.i]), trecut: true });
    st.textContent = stareSalvare(salvat, gazda);
    st.classList.add("vazut");
  });
};

/* ==========================================================================
   4. Pas cu pas — înveți întâi, abia apoi te verifici
   Codul din caiet, rulat rând cu rând. La fiecare pas se luminează rândul,
   apare ce s-a schimbat în memorie (variabilele, desenate: o listă ca șir de
   căsuțe cu pozițiile lor, un dicționar ca chei și valori, un tabel ca tabel)
   și ce s-a afișat. Nu e sarcină și nu se notează: e explicația, jucată.
     { fisier, cod, memoria?, fixa?, pasi: [{ l, set:{nume:{t,v,e?}}, sterge:[...], out, hl:{var,k}, txt }] }
   memoria = eticheta panoului; fixa = nu reordona; e = ce scrie pe insignă în loc de tip.
   ========================================================================== */

const TIP_CLS = { str: "s", int: "n", float: "n", bool: "v", NoneType: "v",
                  list: "l", dict: "d", tuple: "l", DataFrame: "t", Series: "t" };

function repr(v){
  if (v === null) return "None";
  if (v === true) return "True";
  if (v === false) return "False";
  if (typeof v === "string") return `"${v}"`;
  if (Array.isArray(v)) return "[" + v.map(repr).join(", ") + "]";
  if (typeof v === "object") return "{" + Object.entries(v).map(([k, x]) => `"${k}": ${repr(x)}`).join(", ") + "}";
  return String(v);
}
/* o valoare încuibată, prea lungă pentru o căsuță, se arată pe scurt */
function scurt(x){
  const r = repr(x);
  if (r.length <= 34) return r;
  if (Array.isArray(x)) return `[… ${x.length} elemente]`;
  if (x && typeof x === "object") return `{… ${Object.keys(x).length} chei}`;
  return r.slice(0, 32) + "…";
}
function valoareHTML(sp, hl){
  const t = sp.t, v = sp.v;
  if (t === "list" || t === "tuple"){
    return `<span class="ps-lista">${(v || []).map((x, i) => `<span class="ps-c ${hl === i ? "hl" : ""}">
      <i>${i}</i><b class="${typeof x === "string" ? "s" : typeof x === "object" && x ? "x" : "n"}">${esc(scurt(x))}</b></span>`).join("")}</span>`;
  }
  if (t === "dict"){
    return `<span class="ps-dict">${Object.entries(v || {}).map(([k, x]) => `<span class="ps-kv ${hl === k ? "hl" : ""}">
      <i>"${esc(k)}"</i><b class="${typeof x === "string" ? "s" : Array.isArray(x) || (x && typeof x === "object") ? "x" : "n"}">${esc(scurt(x))}</b></span>`).join("")}</span>`;
  }
  if (t === "DataFrame"){
    const c = v.cols || [], r = v.rows || [];
    return `<span class="ps-df"><table><thead><tr><th></th>${c.map(x => `<th>${esc(x)}</th>`).join("")}</tr></thead>
      <tbody>${r.map((row, i) => `<tr><th>${esc((v.index || [])[i] ?? i)}</th>${row.map(x => `<td>${esc(x)}</td>`).join("")}</tr>`).join("")}</tbody></table>
      ${v.nota ? `<small>${esc(v.nota)}</small>` : ""}</span>`;
  }
  if (t === "Series"){
    return `<span class="ps-df"><table><tbody>${(v.rows || []).map(([k, x]) => `<tr><th>${esc(k)}</th><td>${esc(x)}</td></tr>`).join("")}</tbody></table>
      ${v.nota ? `<small>${esc(v.nota)}</small>` : ""}</span>`;
  }
  return `<span class="ps-sc ${TIP_CLS[t] || ""}">${esc(t === "str" ? `"${v}"` : repr(v))}</span>`;
}

E.pas = (gazda, d) => {
  const lb = limba(d.fisier);
  const linii = String(d.cod || "").replace(/\t/g, "    ").split("\n");
  const P = d.pasi || [];
  let i = -1;                                    // -1 = încă n-a pornit
  gazda.innerHTML = `
    ${d.sarcina ? `<p class="ex__sarcina">${d.sarcina}</p>` : ""}
    <div class="ps">
      <div class="ed ps__ed">
        <div class="ed__bara"><span class="ed__pct"><i></i><i></i><i></i></span>
          <span class="ed__nume">${esc(d.fisier || "caiet.ipynb")}</span></div>
        <div class="ed__corp">
          <div class="ed__nr">${linii.map((_, k) => `<span data-l="${k + 1}">${k + 1}</span>`).join("")}</div>
          <div class="ed__cod">${linii.map((l, k) => `<span class="ps__r" data-l="${k + 1}">${coloreaza(l, lb) || "&nbsp;"}</span>`).join("")}</div>
        </div>
      </div>
      <div class="ps__dr">
        <div class="ps__p"><span class="ps__et">${esc(d.memoria || "memoria")}</span><div class="ps__mem"></div></div>
        <div class="ps__p ps__p--out"><span class="ps__et">ieșire</span><pre class="ps__out"></pre></div>
      </div>
    </div>
    <div class="ps__txt"></div>
    <div class="ps__nav">
      <button class="btn btn--mic" type="button" data-rol="inapoi">◀ Înapoi</button>
      <span class="ps__puncte">${P.map((_, k) => `<i data-k="${k}"></i>`).join("")}</span>
      <button class="btn btn--mic btn--tare" type="button" data-rol="inainte">▶ Rulează primul rând</button>
    </div>`;
  const $ = q => gazda.querySelector(q);

  let ultimul = {};
  function stare(pana){
    const mem = {}, out = [];
    ultimul = {};
    for (let k = 0; k <= pana; k++){
      const p = P[k];
      Object.entries(p.set || {}).forEach(([n, sp]) => { mem[n] = sp; ultimul[n] = k; });
      (p.sterge || []).forEach(n => delete mem[n]);
      if (p.out != null) out.push(p.out);
    }
    return { mem, out };
  }
  function arata(){
    const p = P[i] || {};
    const { mem, out } = stare(i);
    gazda.querySelectorAll(".ps__r, .ed__nr span").forEach(r => r.classList.toggle("on", +r.dataset.l === p.l));
    gazda.querySelectorAll(".ps__r").forEach(r => r.classList.toggle("trecut", i >= 0 && +r.dataset.l < (p.l || 0)));
    const noi = new Set(Object.keys(p.set || {}));
    /* cea mai nouă variabilă sus: acolo se uită ochiul după fiecare rând */
    /* d.fixa: ordinea rămâne cea de la prima apariție (zone, nu variabile) */
    const ord = d.fixa ? Object.entries(mem) : Object.entries(mem).sort(([a], [b]) => (noi.has(b) ? 1 : 0) - (noi.has(a) ? 1 : 0) || ultimul[b] - ultimul[a]);
    $(".ps__mem").innerHTML = ord.length ? ord.map(([n, sp]) => `
      <div class="ps-v ${noi.has(n) ? "nou" : ""}">
        <span class="ps-v__n">${esc(n)}</span>
        <span class="ps-v__t ${TIP_CLS[sp.t] || ""}">${esc(sp.e || sp.t)}</span>
        <span class="ps-v__v">${valoareHTML(sp, p.hl?.var === n ? p.hl.k : undefined)}</span>
      </div>`).join("") : `<p class="ps__gol">${i < 0 ? "Încă nimic: apasă ▶ și rulăm primul rând." : "Rândul ăsta n-a creat nimic nou."}</p>`;
    $(".ps__out").textContent = out.join("\n");
    $(".ps__txt").innerHTML = i < 0 ? (d.intro || "Rulează rând cu rând și urmărește ce apare în memorie și la ieșire.")
                                    : `<b>Rândul ${p.l}.</b> ${p.txt || ""}`;
    gazda.querySelectorAll(".ps__puncte i").forEach(e => e.classList.toggle("on", +e.dataset.k <= i));
    $('[data-rol="inapoi"]').disabled = i < 0;
    $('[data-rol="inainte"]').textContent = i < 0 ? "▶ Rulează primul rând" : i >= P.length - 1 ? "↺ De la capăt" : "▶ Rândul următor";
  }
  $('[data-rol="inainte"]').onclick = () => { i = i >= P.length - 1 ? -1 : i + 1; arata(); };
  $('[data-rol="inapoi"]').onclick = () => { i = Math.max(-1, i - 1); arata(); };
  arata();
};

function amesteca(a){
  const b = a.slice();
  for (let i = b.length - 1; i > 0; i--){
    const j = Math.floor(Math.random() * (i + 1));
    [b[i], b[j]] = [b[j], b[i]];
  }
  return b;
}

E.coloreaza = coloreaza;   /* folosit de interactiv.js pentru blocurile statice */
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
      st.textContent = stareSalvare(salvat, gazda);
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
