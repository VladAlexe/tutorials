/* ===========================================================================
   COMPONENTE VIZUALE

   Lucrurile pe care un tabel le descrie, dar nu le arată: un pachet care
   pleacă și se întoarce, un fișier care trece prin zonele lui Git, o ramură
   care se desprinde și se întoarce, un conflict care trebuie rezolvat cu
   mâna.

   Toate sunt desenate cu HTML și SVG, fără biblioteci: pagina trebuie să se
   deschidă repede pe wifi-ul facultății, cu douăzeci și cinci de oameni pe el.

   Cele care cer o decizie sunt porți: se salvează, apar la profesor, și
   deschid slide-ul următor. Cele care doar arată ceva, nu.
   =========================================================================== */

const V = {};

const esc = s => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;");

/** O poartă trecută, scrisă și în baza de date. */
async function poarta(gazda, id, ce = ""){
  const ix = gazda.closest(".ix");
  if (ix){
    if (ix.classList.contains("gata")) return;
    ix.classList.add("gata");
  }
  document.dispatchEvent(new CustomEvent("poarta:gata", { detail:{ id } }));
  try {
    const m = await import("/data-science-workflows/js/colectare.js?v=105");
    await m.salveazaCod({ exercitiuId: id, cod: String(ce).slice(0, 400), trecut: true });
  } catch { /* fără cont, poarta se deschide oricum */ }
}


/* ===========================================================================
   1. FLUX — un pachet care pleacă și se întoarce

   Pentru analogia restaurantului și pentru arhitectura REST: aceleași stații,
   alt vocabular. Apeși „trimite" și vezi unde ajunge cererea, pas cu pas.
   =========================================================================== */

V.flux = (gazda, d) => {
  const S = d.statii || [];
  let pas = -1, ceas = null;

  gazda.innerHTML = `
    ${d.sarcina ? `<p class="ix__sarcina">${d.sarcina}</p>` : ""}
    <div class="flx">
      <div class="flx__sina">
        ${S.map((s, i) => `
          <div class="flx__s${s.c ? " flx__s--c" : ""}" data-i="${i}"${s.c ? ` style="--fc:var(--${s.c})"` : ""}>
            <span class="flx__ic">${s.ic || "●"}</span>
            <span class="flx__n">${esc(s.n)}</span>
            <span class="flx__et">${esc(s.et || "")}</span>
          </div>
          ${i < S.length - 1 ? `<div class="flx__leg" data-l="${i}">
             <span class="flx__pachet"></span></div>` : ""}`).join("")}
      </div>
      <div class="flx__act">
        <button class="btn btn--mic btn--tare" data-rol="porneste" type="button">
          ${esc(d.buton || "Trimite cererea")}</button>
        <span class="flx__stare"></span>
      </div>
      <div class="flx__i"><h5>${esc(d.titlu || "Selectează o stație")}</h5>
        <p>${d.intro || ""}</p></div>
    </div>`;

  const sine  = [...gazda.querySelectorAll(".flx__s")];
  const legi  = [...gazda.querySelectorAll(".flx__leg")];
  const info  = gazda.querySelector(".flx__i");
  const stare = gazda.querySelector(".flx__stare");
  const bt    = gazda.querySelector('[data-rol="porneste"]');

  const arata = i => {
    const s = S[i];
    sine.forEach((x, k) => x.classList.toggle("on", k === i));
    info.innerHTML = `<h5>${esc(s.n)}${s.et ? ` <small>${esc(s.et)}</small>` : ""}</h5>
      <p>${s.d || ""}</p>`;
  };

  gazda.addEventListener("click", e => {
    const s = e.target.closest(".flx__s");
    if (s){ pas = +s.dataset.i; arata(pas); }
  });

  bt.onclick = () => {
    clearInterval(ceas);
    sine.forEach(x => x.classList.remove("on", "atins"));
    legi.forEach(x => x.classList.remove("dus", "intors"));
    let i = 0, inapoi = false;
    stare.textContent = d.dus || "cererea este trimisă";
    arata(0); sine[0].classList.add("atins");

    ceas = setInterval(() => {
      if (!inapoi){
        if (i >= S.length - 1){
          inapoi = true;
          stare.textContent = d.intors || "răspunsul revine";
          return;
        }
        legi[i].classList.add("dus");
        i++; sine[i].classList.add("atins"); arata(i);
      } else {
        if (i <= 0){
          clearInterval(ceas);
          stare.textContent = d.gata || "răspunsul a fost primit";
          return;
        }
        i--; legi[i].classList.add("intors"); arata(i);
      }
    }, 820);
  };

  arata(0);
};


/* ===========================================================================
   4. ZONE — cele trei zone ale lui Git

   Modelul mental fără de care comenzile lui Git se învață pe de rost. Aici nu
   se citește, se mută: apeși comanda și vezi unde ajung fișierele.
   =========================================================================== */

V.zone = (gazda, d) => {
  gazda.closest(".ix")?.classList.add("exc");
  const ZONE = [
    { t: "Dosarul de lucru", d: "fișierele editate" },
    { t: "Pregătire", d: "ce intră în commit" },
    { t: "Istoric local", d: "commit-urile locale" },
    { t: "GitHub", d: "depozitul de la distanță" },
  ];
  const COM = [
    { c: "git status", z: null, d: "nu mută nimic; afișează starea" },
    { c: "git add", z: 1, d: "din dosar în pregătire" },
    { c: "git commit", z: 2, d: "din pregătire în istoricul local" },
    { c: "git push", z: 3, d: "din local pe GitHub" },
  ];
  const F = (d.fisiere || ["colectare.py", "README.md"]).map(t => ({ t, z: 0 }));
  let jurnal = [];

  gazda.innerHTML = `
    ${d.sarcina ? `<p class="ix__sarcina">${d.sarcina}</p>` : ""}
    <div class="zn">
      <div class="zn__zone">${ZONE.map((z, i) => `
        <div class="zn__z" data-z="${i}">
          <span class="zn__zt">${esc(z.t)}</span>
          <span class="zn__zd">${esc(z.d)}</span>
          <div class="zn__in"></div>
        </div>`).join("")}</div>
      <div class="zn__com">${COM.map((c, i) =>
        `<button class="zn__cb" data-c="${i}" type="button">${esc(c.c)}</button>`).join("")}
        <button class="zn__cb zn__cb--rau" data-rol="reset" type="button">de la capăt</button>
      </div>
      <p class="zn__msg"></p>
      <p class="ex__stare"></p>
    </div>`;

  const cosuri = [...gazda.querySelectorAll(".zn__in")];
  const msg = gazda.querySelector(".zn__msg");
  const st  = gazda.querySelector(".ex__stare");

  const deseneaza = () => {
    cosuri.forEach((c, i) => {
      c.innerHTML = F.filter(f => f.z === i)
        .map(f => `<span class="zn__f">${esc(f.t)}</span>`).join("");
    });
    gazda.querySelectorAll(".zn__z").forEach((z, i) =>
      z.classList.toggle("plin", F.some(f => f.z === i)));
  };

  gazda.addEventListener("click", async e => {
    if (e.target.closest('[data-rol="reset"]')){
      F.forEach(f => f.z = 0); jurnal = []; msg.textContent = ""; deseneaza(); return;
    }
    const b = e.target.closest(".zn__cb");
    if (!b || b.dataset.c === undefined) return;
    const c = COM[+b.dataset.c];
    jurnal.push(c.c);

    if (c.z === null){
      const pe = ZONE.map((z, i) => `${F.filter(f => f.z === i).length} în „${z.t}”`).join(", ");
      msg.textContent = `${c.c}: ${pe}. Nu s-a mutat nimic.`;
      return;
    }
    const muta = F.filter(f => f.z === c.z - 1);
    if (!muta.length){
      msg.textContent = `${c.c}: nimic de mutat. Zona „${ZONE[c.z - 1].t}” este goală.`;
      return;
    }
    muta.forEach(f => f.z = c.z);
    msg.textContent = `${c.c}: ${muta.length} ${muta.length === 1 ? "fișier" : "fișiere"} → ${ZONE[c.z].t}.`;
    deseneaza();

    if (F.every(f => f.z === 3)){
      msg.textContent = "Toate fișierele au ajuns pe GitHub. Acesta este traseul, la fiecare modificare.";
      await poarta(gazda, d.id, jurnal.join(" → "));
      st.textContent = "Exercițiul este rezolvat.";
      st.classList.add("vazut");
    }
  });

  deseneaza();
};


/* ===========================================================================
   6. CONFLICT — îl rezolvi cu mâna, cum se face și în viață

   Marcajele acelea cu paranteze unghiulare sperie prima dată. Aici le vezi,
   alegi, și vezi ce rămâne în fișier.
   =========================================================================== */

V.conflict = (gazda, d) => {
  gazda.closest(".ix")?.classList.add("exc");
  let ales = null;

  const randuri = () => {
    if (ales === null){
      return `<span class="cf__m">&lt;&lt;&lt;&lt;&lt;&lt;&lt; HEAD</span>\n` +
             `<span class="cf__a">${esc(d.alMeu)}</span>\n` +
             `<span class="cf__m">=======</span>\n` +
             `<span class="cf__b">${esc(d.alLor)}</span>\n` +
             `<span class="cf__m">&gt;&gt;&gt;&gt;&gt;&gt;&gt; ${esc(d.ramura || "curatare")}</span>`;
    }
    if (ales === "meu")  return `<span class="cf__a">${esc(d.alMeu)}</span>`;
    if (ales === "lor")  return `<span class="cf__b">${esc(d.alLor)}</span>`;
    return `<span class="cf__a">${esc(d.alMeu)}</span>\n<span class="cf__b">${esc(d.alLor)}</span>`;
  };

  gazda.innerHTML = `
    ${d.sarcina ? `<p class="ix__sarcina">${d.sarcina}</p>` : ""}
    <div class="cf">
      <div class="ed">
        <div class="ed__bara"><span class="ed__pct"><i></i><i></i><i></i></span>
          <span class="ed__nume">${esc(d.fisier || "analiza.py")}</span></div>
        <div class="ed__corp"><div class="ed__cod"><pre class="cf__cod"></pre></div></div>
      </div>
      <div class="cf__alege">
        <button class="zn__cb" data-k="meu" type="button">păstrez versiunea mea</button>
        <button class="zn__cb" data-k="lor" type="button">păstrez versiunea primită</button>
        <button class="zn__cb" data-k="ambele" type="button">păstrez ambele versiuni</button>
      </div>
      <div class="ex__jos">
        <button class="btn btn--mic btn--tare" data-rol="verifica" type="button" disabled>
          git add și commit</button>
        <span class="ex__raspuns"></span>
      </div>
      <p class="ex__ex"></p>
      <p class="ex__stare"></p>
    </div>`;

  const cod = gazda.querySelector(".cf__cod");
  const btV = gazda.querySelector('[data-rol="verifica"]');
  const out = gazda.querySelector(".ex__raspuns");
  const ex  = gazda.querySelector(".ex__ex");
  const st  = gazda.querySelector(".ex__stare");

  const scrie = () => { cod.innerHTML = randuri(); };

  gazda.addEventListener("click", e => {
    const b = e.target.closest("[data-k]");
    if (!b) return;
    ales = b.dataset.k;
    gazda.querySelectorAll("[data-k]").forEach(x => x.classList.toggle("on", x === b));
    btV.disabled = false;
    out.textContent = "";
    scrie();
  });

  btV.onclick = async () => {
    const bun = ales === (d.bun || "lor");
    out.innerHTML = bun
      ? "<b>Corect.</b> Marcajele au fost eliminate, iar fișierul rulează din nou."
      : `<b>Funcționează, dar nu este varianta potrivită.</b> ${d.deCe || ""}`;
    ex.classList.add("vazut");
    ex.innerHTML = d.explicatie || "";
    btV.disabled = true;
    gazda.querySelectorAll("[data-k]").forEach(x => x.disabled = true);
    await poarta(gazda, d.id, ales);
    st.textContent = "Exercițiul este rezolvat.";
    st.classList.add("vazut");
  };

  scrie();
};


/* ===========================================================================
   7. COTE — cât din întreg

   Un cerc tăiat în felii se citește prost: ochiul compară greu unghiuri. Bare
   orizontale, sortate, cu aceeași culoare, se citesc dintr-o privire. Culoarea
   nu poartă informație aici: lungimea o poartă.
   =========================================================================== */

V.cote = (gazda, d) => {
  const C = (d.cote || []).slice().sort((a, b) => b.v - a.v);
  const max = Math.max(...C.map(x => x.v), 1);

  gazda.innerHTML = `
    ${d.sarcina ? `<p class="ix__sarcina">${d.sarcina}</p>` : ""}
    <div class="cot">
      ${C.map(x => `
        <div class="cot__r ${x.ac ? "ac" : ""}">
          <span class="cot__t">${esc(x.t)}</span>
          <span class="cot__b"><i style="width:${(x.v / max) * 100}%"></i></span>
          <span class="cot__v">${x.v}${d.unitate || "%"}</span>
        </div>`).join("")}
      ${d.sursa ? `<p class="cot__s">${d.sursa}</p>` : ""}
    </div>`;
};


/* ===========================================================================
   8. PRAG — unde tai valorile extreme

   Regula „peste 1,5 ori intervalul intercuartilic" pare obiectivă până muți
   pragul și vezi că numărul de „valori extreme" se schimbă cum vrei tu. Asta
   e lecția: pragul e o alegere, iar o valoare extremă nu e automat o greșeală.
   =========================================================================== */

V.prag = (gazda, d) => {
  gazda.closest(".ix")?.classList.add("exc");
  const X = (d.valori || []).slice().sort((a, b) => a.v - b.v);
  if (!X.length) return;
  const vals = X.map(x => x.v);
  const cuant = q => {
    const i = (vals.length - 1) * q, j = Math.floor(i), r = i - j;
    return vals[j] + (vals[Math.min(j + 1, vals.length - 1)] - vals[j]) * r;
  };
  const q1 = cuant(0.25), q3 = cuant(0.75), iqr = q3 - q1;
  const maxv = vals[vals.length - 1];
  /* o margine de fiecare parte, ca bulina cea mai mare să nu fie tăiată de
     marginea benzii, exact ca la cronologie */
  const MARG = 2;
  const poz = v => MARG + (Math.min(1, v / maxv)) * (100 - 2 * MARG);
  let k = 1.5, raspuns = null;

  gazda.innerHTML = `
    ${d.sarcina ? `<p class="ix__sarcina">${d.sarcina}</p>` : ""}
    <div class="prg">
      <div class="prg__banda">
        ${X.map((x, i) => `<span class="prg__p" data-v="${x.v}"
            style="left:${poz(x.v)}%;bottom:${(i % 4) * 9}px" title="${esc(x.t)}: ${x.v}"></span>`).join("")}
        ${X.slice(-3).map((x, i) => `<span class="prg__nume${i === 2 ? " dr" : ""}" style="left:${poz(x.v)}%">${esc(x.t)}</span>`).join("")}
        <span class="prg__linie"></span>
      </div>
      <div class="prg__ctrl">
        <label>prag = Q3 + <b class="prg__k">1,5</b> × IQR</label>
        <input class="prg__s" type="range" min="5" max="50" step="1" value="15">
      </div>
      <p class="prg__cif"></p>
      <p class="prg__lista"></p>
      <div class="prg__intreb">
        <p>${d.intrebare || "Valorile marcate sunt greșeli de date?"}</p>
        <div class="cf__alege">
          <button class="zn__cb" data-r="scot" type="button">Da, sunt erori: se elimină</button>
          <button class="zn__cb" data-r="pastrez" type="button">Nu, sunt valori reale: se păstrează</button>
        </div>
        <p class="ex__raspuns"></p>
      </div>
      <p class="ex__stare"></p>
    </div>`;

  const banda = gazda.querySelector(".prg__banda");
  const cif   = gazda.querySelector(".prg__cif");
  const lst   = gazda.querySelector(".prg__lista");
  const out   = gazda.querySelector(".ex__raspuns");
  const st    = gazda.querySelector(".ex__stare");

  function deseneaza(){
    const prag = q3 + k * iqr;
    const peste = X.filter(x => x.v > prag);
    gazda.querySelector(".prg__k").textContent = String(k).replace(".", ",");
    gazda.querySelector(".prg__linie").style.left = poz(prag) + "%";
    banda.querySelectorAll(".prg__p").forEach(p =>
      p.classList.toggle("peste", +p.dataset.v > prag));
    cif.innerHTML = `prag <b>${Math.round(prag).toLocaleString("ro-RO")}</b> · ` +
      `<b>${peste.length}</b> din ${X.length} depășesc pragul`;
    lst.innerHTML = peste.length
      ? "marcate: " + peste.slice(-8).reverse().map(x => esc(x.t)).join(", ") +
        (peste.length > 8 ? ", …" : "")
      : "nicio valoare peste prag";
  }

  gazda.querySelector(".prg__s").addEventListener("input", e => {
    k = (+e.target.value) / 10;
    deseneaza();
  });

  gazda.addEventListener("click", async e => {
    const b = e.target.closest("[data-r]");
    if (!b || raspuns) return;
    raspuns = b.dataset.r;
    gazda.querySelectorAll("[data-r]").forEach(x => { x.disabled = true;
      x.classList.toggle("on", x === b); });
    out.innerHTML = raspuns === "pastrez"
      ? `<b>Corect.</b> ${d.laBine || ""}`
      : `<b>Nu încă.</b> ${d.laRau || ""}`;
    out.classList.add("vazut");
    await poarta(gazda, d.id, `k=${k} raspuns=${raspuns}`);
    st.textContent = "Exercițiul este rezolvat.";
    st.classList.add("vazut");
  });

  deseneaza();
};


/* ===========================================================================
   9. ÎMBINARE — ce rămâne când lipești două tabele

   `inner`, `left`, `outer` se învață prost din definiție și bine din numărare.
   Aici stau două tabele mici, unul lângă altul, cu cheile colorate după cum se
   potrivesc sau nu. Apeși un fel de îmbinare și vezi tabelul care iese: câte
   rânduri, care au goluri, care au dispărut.

   Poarta se deschide după ce au fost încercate toate felurile: scopul nu e să
   nimerească unul, e să le vadă pe toate patru una după alta.
   =========================================================================== */

V.imbinare = (gazda, d) => {
  gazda.closest(".ix")?.classList.add("exc");

  const chS = d.cheie || "cod";                     /* coloana-cheie */
  const A = d.stanga || { nume: "stânga", randuri: [] };
  const B = d.dreapta || { nume: "dreapta", randuri: [] };
  const colA = Object.keys(A.randuri[0] || {});
  const colB = Object.keys(B.randuri[0] || {});
  const doarB = colB.filter(c => c !== chS);        /* ce aduce tabelul din dreapta */

  const FELURI = d.feluri || ["concat", "inner", "left", "right", "outer"];
  const NUME = { concat: "concat", inner: "inner", left: "left",
                 right: "right", outer: "outer" };
  const vazute = new Set();
  let fel = null;

  /* ---- ce iese din fiecare fel de îmbinare ---------------------------- */
  function rezultat(f){
    const cheiA = A.randuri.map(r => r[chS]);
    const cheiB = B.randuri.map(r => r[chS]);

    if (f === "concat"){
      /* una sub alta: coloanele se reunesc, ce lipsește rămâne gol */
      const col = [...new Set([...colA, ...colB])];
      const r = [...A.randuri.map(x => ({ ...x, _din: "a" })),
                 ...B.randuri.map(x => ({ ...x, _din: "b" }))];
      return { col, randuri: r };
    }

    const col = [...colA, ...doarB];
    const out = [];
    const potrivit = k => B.randuri.filter(x => x[chS] === k);

    if (f === "inner" || f === "left"){
      for (const a of A.randuri){
        const p = potrivit(a[chS]);
        if (p.length) p.forEach(b => out.push({ ...a, ...b, _din: "ab" }));
        else if (f === "left") out.push({ ...a, _din: "a" });
      }
    }
    if (f === "right"){
      for (const b of B.randuri){
        const p = A.randuri.filter(x => x[chS] === b[chS]);
        if (p.length) p.forEach(a => out.push({ ...a, ...b, _din: "ab" }));
        else out.push({ ...b, _din: "b" });
      }
    }
    if (f === "outer"){
      for (const a of A.randuri){
        const p = potrivit(a[chS]);
        if (p.length) p.forEach(b => out.push({ ...a, ...b, _din: "ab" }));
        else out.push({ ...a, _din: "a" });
      }
      for (const b of B.randuri)
        if (!cheiA.includes(b[chS])) out.push({ ...b, _din: "b" });
    }
    return { col, randuri: out };
  }

  /* ---- tabelele de sus, cu cheile colorate ---------------------------- */
  const cheiComune = new Set(A.randuri.map(r => r[chS])
    .filter(k => B.randuri.some(x => x[chS] === k)));

  const tabel = (t, col, randuri, lat) => `
    <div class="imb__t">
      <span class="imb__tn">${esc(t)}<small>${randuri.length} rânduri</small></span>
      <table class="imb__tb">
        <thead><tr>${col.map(c =>
          `<th class="${c === chS ? "ch" : ""}">${esc(c)}</th>`).join("")}</tr></thead>
        <tbody>${randuri.map(r => `<tr>${col.map(c => {
          const v = r[c];
          const gol = v === undefined || v === null || v === "";
          const ch = c === chS;
          const sg = ch && !cheiComune.has(r[c]);
          return `<td class="${ch ? "ch " : ""}${sg ? "sg " : ""}${gol ? "gol" : ""}">${
            gol ? (lat ? "NaN" : "—") : esc(v)}</td>`;
        }).join("")}</tr>`).join("")}</tbody>
      </table>
    </div>`;

  gazda.innerHTML = `
    ${d.sarcina ? `<p class="ix__sarcina">${d.sarcina}</p>` : ""}
    <div class="imb">
      <div class="imb__sus">
        ${tabel(A.nume, colA, A.randuri)}
        <span class="imb__plus">+</span>
        ${tabel(B.nume, colB, B.randuri)}
      </div>
      <p class="imb__leg">
        <span class="imb__pct imb__pct--ab"></span>cheie în ambele tabele
        <span class="imb__pct imb__pct--un"></span>cheie într-un singur tabel
      </p>
      <div class="imb__fel">
        ${FELURI.map(f => `<button class="imb__b" data-f="${f}" type="button">${
          f === "concat" ? "pd.concat" : `how=&quot;${NUME[f]}&quot;`}</button>`).join("")}
      </div>
      <div class="imb__jos"><p class="imb__gol">Rezultatul apare după selectarea unui tip de îmbinare.</p></div>
      <p class="imb__exp"></p>
      <p class="ex__stare"></p>
    </div>`;

  const jos = gazda.querySelector(".imb__jos");
  const exp = gazda.querySelector(".imb__exp");
  const st  = gazda.querySelector(".ex__stare");

  gazda.addEventListener("click", async e => {
    const b = e.target.closest(".imb__b");
    if (!b) return;
    fel = b.dataset.f;
    gazda.querySelectorAll(".imb__b").forEach(x => x.classList.toggle("on", x === b));
    const r = rezultat(fel);
    jos.innerHTML = tabel(d.numeRez || "rezultat", r.col, r.randuri, true);
    jos.querySelectorAll("tbody tr").forEach((tr, i) =>
      tr.classList.add("din-" + (r.randuri[i]._din || "ab")));
    exp.innerHTML = (d.explicatii || {})[fel] || "";

    vazute.add(fel);
    if (vazute.size >= FELURI.length){
      await poarta(gazda, d.id || "imbinare", [...vazute].join(","));
      st.textContent = "Toate tipurile de îmbinare au fost parcurse.";
      st.classList.add("vazut");
    } else {
      st.textContent = `${vazute.size} din ${FELURI.length} încercate.`;
      st.classList.add("vazut");
    }
  });
};


/* ===========================================================================
   10. COLOANE — ce tip are fiecare coloană

   Un tabel de tipuri cu patru rânduri se citește și se uită. Aici se vede
   tabelul adevărat, cu valorile lui, și pentru fiecare coloană trebuie ales
   un tip. Alegerea se face uitându-te la valori, care e exact ce faci în
   realitate când scrii un `create table`.
   =========================================================================== */

V.coloane = (gazda, d) => {
  gazda.closest(".ix")?.classList.add("exc");
  const C = d.coloane || [];
  const T = d.tipuri || [];
  let verificat = false;

  gazda.innerHTML = `
    ${d.sarcina ? `<p class="ix__sarcina">${d.sarcina}</p>` : ""}
    <div class="col">
      <div class="col__t">
        <span class="col__tn">${esc(d.fisier || "tabel")}<small>${
          d.nota || `${C.length} coloane`}</small></span>
        <table class="col__tb">
          <thead><tr>${C.map(c => `<th>${esc(c.nume)}</th>`).join("")}</tr></thead>
          <tbody>${(d.cap || []).map(r => `<tr>${r.map(v =>
            `<td class="${typeof v === "number" ? "nr" : ""}">${esc(v)}</td>`
            ).join("")}</tr>`).join("")}</tbody>
          <tfoot><tr>${C.map((c, i) => `<td>
            <select class="col__s" data-i="${i}">
              <option value="">tipul…</option>
              ${T.map(t => `<option value="${esc(t)}">${esc(t)}</option>`).join("")}
            </select></td>`).join("")}</tr></tfoot>
        </table>
      </div>
      <div class="col__act">
        <button class="btn btn--mic btn--tare" data-rol="verifica" type="button"
          disabled>Verifică</button>
        <button class="btn btn--mic" data-rol="din-nou" type="button" hidden>Încearcă din nou</button>
      </div>
      <p class="ex__raspuns"></p>
      <div class="col__de"></div>
      <p class="ex__stare"></p>
    </div>`;

  const sel = [...gazda.querySelectorAll(".col__s")];
  const btV = gazda.querySelector('[data-rol="verifica"]');
  const btN = gazda.querySelector('[data-rol="din-nou"]');
  const out = gazda.querySelector(".ex__raspuns");
  const de  = gazda.querySelector(".col__de");
  const st  = gazda.querySelector(".ex__stare");

  const gata = () => sel.every(s => s.value);
  sel.forEach(s => s.addEventListener("change", () => {
    btV.disabled = !gata();
    if (verificat) return;
    s.classList.remove("bun", "rau");
  }));

  btV.onclick = async () => {
    verificat = true;
    let bune = 0;
    sel.forEach((s, i) => {
      const ok = String(s.value).toUpperCase() === String(C[i].ok).toUpperCase();
      s.classList.toggle("bun", ok); s.classList.toggle("rau", !ok);
      if (ok) bune++;
    });
    const tot = bune === C.length;
    out.innerHTML = tot ? `<b>Corect.</b> ${d.laBine || ""}`
                        : `<b>${bune} din ${C.length}.</b> ${d.laRau || ""}`;
    btN.hidden = tot;
    if (!tot) return;
    btV.disabled = true;
    de.innerHTML = C.map(c => `<p><code>${esc(c.nume)}</code>
      <b>${esc(c.ok)}</b> ${c.de_ce || ""}</p>`).join("");
    de.classList.add("vazut");
    await poarta(gazda, d.id || "coloane", sel.map(s => s.value).join(","));
    st.textContent = "Exercițiul este rezolvat.";
    st.classList.add("vazut");
  };

  btN.onclick = () => {
    verificat = false; btN.hidden = true; out.textContent = "";
    sel.forEach(s => s.classList.remove("bun", "rau"));
    btV.disabled = !gata();
  };
};


/* ===========================================================================
   11. DESFĂ — cum devine un JSON un tabel

   Ce se întâmplă între răspunsul unui API și `DataFrame` e operația pe care
   toată lumea o scrie fără s-o vadă. Aici se vede: apeși, se aprinde lista
   dinăuntru, apoi fiecare element devine un rând, unul câte unul.
   =========================================================================== */

V.desfa = (gazda, d) => {
  /* E poartă: se deschide după ce au apăsat de două ori, adică după ce au
     văzut și lista aprinsă, și tabelul făcut din ea. */
  if (d.id) gazda.closest(".ix")?.classList.add("exc");
  const EL = d.elemente || [];
  const COL = d.coloane || [];
  const PASI = [
    d.p0 || "Răspunsul complet, în forma primită.",
    d.p1 || "Lista interioară: aceasta devine tabel.",
    d.p2 || "Fiecare element al listei devine un rând.",
  ];
  let pas = 0;

  gazda.innerHTML = `
    ${d.sarcina ? `<p class="ix__sarcina">${d.sarcina}</p>` : ""}
    <div class="dsf">
      <div class="dsf__doi">
        <div class="dsf__st">
          <span class="dsf__et">${esc(d.sursa || "răspunsul API")}</span>
          <pre class="dsf__j"></pre>
        </div>
        <div class="dsf__dr">
          <span class="dsf__et">DataFrame</span>
          <table class="dsf__tb">
            <thead><tr>${COL.map(c => `<th>${esc(c)}</th>`).join("")}</tr></thead>
            <tbody></tbody>
          </table>
          <p class="dsf__gol">Niciun rând încă.</p>
        </div>
      </div>
      <div class="dsf__act">
        <button class="btn btn--mic btn--tare" data-rol="pas" type="button"></button>
        <span class="dsf__stare"></span>
      </div>
    </div>`;

  const j    = gazda.querySelector(".dsf__j");
  const tb   = gazda.querySelector(".dsf__tb tbody");
  const gol  = gazda.querySelector(".dsf__gol");
  const bt   = gazda.querySelector('[data-rol="pas"]');
  const stare= gazda.querySelector(".dsf__stare");

  /* JSON-ul scris de mână, ca să pot aprinde exact ce vreau */
  function scrieJson(aprins){
    const cap = `{\n  "${esc(d.cheieCap || "cap")}": { "pagina": 1, "total": ${EL.length} },\n`;
    const lista = EL.map((e, i) =>
      `    {${COL.map(c => ` "${esc(c)}": ${
        typeof e[c] === "number" ? e[c] : `"${esc(e[c])}"`}`).join(",")} }`
    ).join(",\n");
    const corp = `  "${esc(d.cheieLista || "date")}": [\n${lista}\n  ]\n}`;
    j.innerHTML = aprins
      ? esc(cap) + `<mark>${esc(corp.slice(0, corp.length))}</mark>`
      : esc(cap + corp);
  }

  function deseneaza(){
    scrieJson(pas >= 1);
    tb.innerHTML = "";
    if (pas >= 2){
      EL.forEach((e, i) => {
        const tr = document.createElement("tr");
        tr.innerHTML = COL.map(c => `<td class="${
          typeof e[c] === "number" ? "nr" : ""}">${esc(e[c])}</td>`).join("");
        tr.style.animationDelay = (i * 90) + "ms";
        tb.appendChild(tr);
      });
    }
    gol.hidden = pas >= 2;
    stare.textContent = PASI[Math.min(pas, PASI.length - 1)];
    bt.textContent = pas === 0 ? (d.buton || "Evidențiază lista")
                   : pas === 1 ? "Construiește tabelul"
                   : "Reia";
  }

  bt.onclick = async () => {
    pas = pas >= 2 ? 0 : pas + 1;
    deseneaza();
    if (pas === 2 && d.id) await poarta(gazda, d.id, d.cheieLista || "date");
  };

  deseneaza();
};


/* ===========================================================================
   12. DRUM — fluxul unui proiect de analiză, ca schemă

   Zece cartonașe egale într-un grid nu spun nimic despre ordine. Schema de
   la curs spune: etapele curg spre dreapta, sunt două benzi (analiza sus,
   ingineria jos), baza de date stă deoparte fiindcă nu e o etapă, iar
   săgețile punctate sunt întoarcerile, adică partea cea mai importantă.

   Forma e fixă, ca în prezentare. Ce se schimbă e textul, care vine din
   lecție. Apeși pe o etapă și îi citești rostul.
   =========================================================================== */

V.drum = (gazda, d) => {
  const SUS = (d.sus || []).slice(0, 4);
  const JOS = (d.jos || []).slice(0, 4);
  const FIN = d.final || { n: "Raportare" };
  const BAZA = d.baza || { n: "Baza de date" };
  const toate = [...SUS, ...JOS, FIN, BAZA];

  const chev = (x, i, banda) => `
    <button class="drm__e drm__e--${banda} et--${esc(x.et || "")}" data-i="${esc(x.n)}"
      style="--k:${i}" type="button">
      <span class="drm__nr">${String(i + 1).padStart(2, "0")}</span>
      <span class="drm__n">${esc(x.n)}</span>
    </button>`;

  gazda.innerHTML = `
    ${d.sarcina ? `<p class="ix__sarcina">${d.sarcina}</p>` : ""}
    <div class="drm">
      <div class="drm__plan">
        <svg class="drm__linii" aria-hidden="true"></svg>

        <span class="drm__banda drm__banda--sus">${esc(d.bandaSus || "Analiza datelor")}</span>
        <div class="drm__rand drm__rand--sus">${SUS.map((x, i) => chev(x, i, "a")).join("")}</div>

        <button class="drm__fin et--${esc(FIN.et || "raport")}" data-i="${esc(FIN.n)}" type="button">${esc(FIN.n)}</button>

        <button class="drm__baza et--${esc(BAZA.et || "agregare")}" data-i="${esc(BAZA.n)}" type="button">
          <span class="drm__bt">${esc(BAZA.n)}</span>
          <span class="drm__bd">nu este o etapă, ci spațiul de stocare</span>
        </button>

        <div class="drm__rand drm__rand--jos">${JOS.map((x, i) => chev(x, i + 4, "b")).join("")}</div>
        <span class="drm__banda drm__banda--jos">${esc(d.bandaJos || "Ingineria modelelor")}</span>
      </div>

      <p class="drm__leg">
        <span class="drm__lp"></span>fluxul principal
        <span class="drm__lp drm__lp--p"></span>revenirile, parte firească a fluxului
      </p>
      <div class="drm__i"><h5>${esc(d.titlu || "Selectează o etapă")}</h5>
        <p>${d.intro || ""}</p></div>
    </div>`;

  const plan = gazda.querySelector(".drm__plan");
  const svg  = gazda.querySelector(".drm__linii");
  const info = gazda.querySelector(".drm__i");

  function trage(){
    const P = plan.getBoundingClientRect();
    if (!P.width) return;
    svg.setAttribute("viewBox", `0 0 ${P.width} ${P.height}`);
    svg.setAttribute("width", P.width); svg.setAttribute("height", P.height);

    const c = sel => {
      const el = plan.querySelector(sel);
      if (!el) return null;
      const r = el.getBoundingClientRect();
      return { st: r.left - P.left, dr: r.right - P.left,
               sus: r.top - P.top, jos: r.bottom - P.top,
               x: r.left - P.left + r.width / 2,
               y: r.top - P.top + r.height / 2 };
    };

    const ultimSus = c(".drm__rand--sus .drm__e:last-child");
    const primJos  = c(".drm__rand--jos .drm__e:first-child");
    const alDoiJos = c(".drm__rand--jos .drm__e:nth-child(2)");
    const fin      = c(".drm__fin");
    const baza     = c(".drm__baza");
    const primSus  = c(".drm__rand--sus .drm__e:nth-child(2)");

    const pline = [], punct = [], varf = [];
    const sageata = (x, y, rot) => {
      const p = [[0,0],[-4.4,-6.4],[4.4,-6.4]]
        .map(([a,b]) => { const r = rot * Math.PI / 180;
          return `${(x + a*Math.cos(r) - b*Math.sin(r)).toFixed(1)},` +
                 `${(y + a*Math.sin(r) + b*Math.cos(r)).toFixed(1)}`; });
      varf.push(p.join(" "));
    };

    if (ultimSus && fin){                       /* EDA → raportare */
      const m = (ultimSus.dr + fin.st) / 2;
      pline.push(`M${ultimSus.dr},${ultimSus.y} H${fin.st - 7}`);
      sageata(fin.st, ultimSus.y, 90);
    }
    if (ultimSus && primJos){                   /* EDA ↓ feature engineering */
      pline.push(`M${ultimSus.x},${ultimSus.jos} V${primJos.sus - 7}`);
      sageata(primJos.x, primJos.sus, 180);
      pline.push(`M${ultimSus.x},${ultimSus.jos} V${(ultimSus.jos + primJos.sus)/2} ` +
                 `H${primJos.x}`);
    }
    if (alDoiJos && fin){                       /* modelare ↗ raportare */
      pline.push(`M${alDoiJos.x},${alDoiJos.sus} V${fin.jos + 7}`);
      sageata(alDoiJos.x, fin.jos, 0);
    }
    if (primSus && baza){                       /* colectarea ↕ baza */
      pline.push(`M${primSus.x},${primSus.jos} V${baza.sus - 7}`);
      sageata(primSus.x, baza.sus, 180);
    }
    if (baza && fin){                           /* intoarcerile, punctate */
      punct.push(`M${baza.dr},${baza.y} H${fin.st - 14} V${fin.jos + 10}`);
      sageata(fin.st - 14, fin.jos + 8, 0);
    }
    if (baza && primJos){
      punct.push(`M${primJos.st - 10},${primJos.jos + 12} H${baza.x} V${baza.jos + 7}`);
      sageata(baza.x, baza.jos + 9, 0);
    }

    svg.innerHTML =
      `<path d="${pline.join(" ")}" fill="none" stroke="currentColor" stroke-width="1.6"/>` +
      `<path d="${punct.join(" ")}" fill="none" stroke="currentColor" stroke-width="1.3"
         stroke-dasharray="3 4" opacity=".65"/>` +
      varf.map(v => `<polygon points="${v}" fill="currentColor"/>`).join("");
  }

  trage();
  requestAnimationFrame(trage);
  if (window.ResizeObserver) new ResizeObserver(trage).observe(plan);

  plan.addEventListener("click", ev => {
    const b = ev.target.closest("[data-i]");
    if (!b) return;
    plan.querySelectorAll("[data-i]").forEach(x => x.classList.remove("on"));
    b.classList.add("on");
    const x = toate.find(t => t.n === b.dataset.i);
    if (!x) return;
    info.className = `drm__i drm__i--plin et--${x.et || ""}`;
    info.innerHTML = `<h5>${esc(x.n)}${x.unde ? ` <small>${esc(x.unde)}</small>` : ""}</h5>
      <p>${x.d || ""}</p>
      ${x.noi || x.lit || x.capcana ? `<div class="drm__blocuri">
        ${x.noi ? `<div><h6>În proiectul cursului</h6><p>${x.noi}</p></div>` : ""}
        ${x.lit ? `<div><h6>Literatura relevantă</h6><p>${x.lit}</p></div>` : ""}
        ${x.capcana ? `<div class="drm__cap"><h6>Eroare frecventă</h6><p>${x.capcana}</p></div>` : ""}
      </div>` : ""}`;
  });
};


/* ===========================================================================
   13. SEMESTRU, ca hartă de metrou

   Ședințele sunt stații pe trei linii care merg împreună: datele și codul
   (toate ședințele), cercetarea (întrebarea, literatura, ipotezele, modelul,
   raportul) și echipa (de la formarea ei, la cursul 2, până la prezentare).
   O stație unde opresc mai multe linii e o stație de corespondență. Linia
   care nu oprește la o ședință trece pe deasupra ei. Apăsarea pe o stație
   deschide fișa ședinței.
   =========================================================================== */

V.semestru = (gazda, d) => {
  const T = d.teme || [], F = d.fise || [], N = d.sedinte || 8;
  const LIN = d.linii || [{ id: "date", nume: "Date și cod", c: "accent", opriri: Array.from({ length: N }, (_, i) => i + 1) }];
  const fisa = k => F.find(f => f.c === k) || { c: k, titlu: "" };
  let ales = d.azi || 1;

  /* geometria: stațiile pe x, liniile pe benzi paralele, ocolul deasupra */
  const W = 800, X0 = 50, DX = (W - 2 * X0) / (N - 1);
  const x = k => X0 + (k - 1) * DX;
  const Y0 = 84, PAS = 12, SUS = 50, R = 30;
  const y = i => Y0 + i * PAS;
  const opreste = (L, k) => L.opriri.includes(k);

  function drum(L, i){
    const o = [...L.opriri].sort((a, b) => a - b), yy = y(i);
    let p = `M${x(o[0])},${yy}`;
    for (let j = 1; j < o.length; j++){
      const a = o[j - 1], b = o[j];
      if (b === a + 1){ p += ` L${x(b)},${yy}`; continue; }
      /* ocolește stațiile la care nu oprește: urcă la 45°, merge sus, coboară */
      const h = yy - SUS;
      p += ` L${x(a) + 16},${yy} L${x(a) + 16 + h},${SUS} L${x(b) - 16 - h},${SUS} L${x(b) - 16},${yy} L${x(b)},${yy}`;
    }
    return p;
  }

  /* fiecare linie are un contur în culoarea fundalului, ca pe hărțile de
     metrou: unde se apropie sau se încrucișează, liniile rămân separate */
  const linii = LIN.map((L, i) => `<path class="mt__contur" d="${drum(L, i)}"/>
    <path class="mt__l" d="${drum(L, i)}" style="--lc:var(--${L.c});--i:${i}" pathLength="1"/>`).join("");

  const statii = Array.from({ length: N }, (_, j) => {
    const k = j + 1, f = fisa(k);
    const idx = LIN.map((L, i) => opreste(L, k) ? i : -1).filter(i => i >= 0);
    const y1 = y(Math.min(...idx)) - 9, y2 = y(Math.max(...idx)) + 9;
    const nume = String(f.scurt || f.titlu);
    const rand = nume.includes(" și ") ? nume.split(" și ").map((t, q) => q ? "și " + t : t) : [nume];
    return `<g class="mt__st" data-c="${k}" tabindex="0" role="button" aria-label="Cursul ${k}: ${esc(f.titlu || nume)}" style="--j:${j}">
      <rect class="mt__hit" x="${x(k) - DX / 2}" y="40" width="${DX}" height="150"/>
      <rect class="mt__halo" x="${x(k) - 15}" y="${y1 - 6}" width="30" height="${y2 - y1 + 12}" rx="15"/>
      <rect class="mt__statie" x="${x(k) - 9}" y="${y1}" width="18" height="${y2 - y1}" rx="9"/>
      <text class="mt__nr" x="${x(k)}" y="${Y0 + (LIN.length - 1) * PAS + R}">C${k}</text>
      ${rand.map((t, q) => `<text class="mt__nume" x="${x(k)}" y="${Y0 + (LIN.length - 1) * PAS + R + 18 + q * 15}">${esc(t)}</text>`).join("")}
    </g>`;
  }).join("");

  const H = Y0 + (LIN.length - 1) * PAS + R + 18 + 22;
  gazda.innerHTML = `
    <div class="mt">
      <div class="mt__leg">${LIN.map(L => `<span style="--lc:var(--${L.c})"><i></i>${esc(L.nume)}</span>`).join("")}</div>
      <svg class="mt__svg" viewBox="0 38 ${W} ${H - 38}" role="group" aria-label="Harta semestrului">
        <g class="mt__linii">${linii}</g>${statii}
      </svg>
      <div class="mt__det" aria-live="polite"></div>
    </div>`;

  /* legenda urcă în capul blocului, lângă titlu, ca să nu stea peste linii */
  const cap = gazda.closest(".ix")?.querySelector(".ix__cap"), leg = gazda.querySelector(".mt__leg");
  if (cap && leg){ cap.querySelector(".mt__leg")?.remove(); leg.classList.add("mt__leg--cap"); cap.append(leg); }

  const det = gazda.querySelector(".mt__det");
  function arata(k){
    ales = k; const f = fisa(k);
    gazda.querySelectorAll(".mt__st").forEach(g => g.classList.toggle("on", +g.dataset.c === k));
    const teme = T.filter(t => t.c === k);
    /* fișa, simplă: temele ședinței și laboratorul ei */
    det.innerHTML = `
      <div class="mt__fcap"><span class="mt__fnr">Cursul ${k}</span><h5>${esc(f.titlu || "")}</h5></div>
      <div class="mt__g">
        <div><h6>La curs</h6>${teme.map(t => `<p class="mt__tema"><b>${esc(t.n)}</b>${esc(t.d || "")}</p>`).join("")}</div>
        <div><h6>Laboratorul</h6><p>${esc(f.lab || "")}</p>
          ${f.caiet ? `<p class="mt__caiet"><code>${esc(f.caiet)}</code></p>` : ""}</div>
      </div>`;
  }
  gazda.querySelector(".mt__svg").addEventListener("click", ev => {
    const g = ev.target.closest(".mt__st"); if (g) arata(+g.dataset.c);
  });
  gazda.querySelector(".mt__svg").addEventListener("keydown", ev => {
    const g = ev.target.closest(".mt__st"); if (!g) return;
    if (ev.key === "Enter" || ev.key === " "){ ev.preventDefault(); arata(+g.dataset.c); }
    if (ev.key === "ArrowRight" || ev.key === "ArrowLeft"){
      const k = Math.min(N, Math.max(1, ales + (ev.key === "ArrowRight" ? 1 : -1)));
      arata(k); gazda.querySelector(`.mt__st[data-c="${k}"]`)?.focus(); ev.preventDefault();
    }
  });
  arata(ales);
};


/* ===========================================================================
   14. ANATOMIE — părțile unui JSON, arătate pe el

   Un tabel „object → dict, array → list" se învață pe de rost și nu ajută la
   primul răspuns real. Aici stă JSON-ul întreg, iar fiecare parte se aprinde
   pe el: obiectul principal, tabloul, un obiect din tablou, o pereche
   cheie–valoare, un tablou de numere. Se vede unde începe și unde se termină
   fiecare, care e tot ce lipsea.
   =========================================================================== */

V.anatomie = (gazda, d) => {
  /* Poartă după ce au deschis câteva părți: scopul e să se uite pe cod, nu
     să nimerească un răspuns. */
  if (d.id) gazda.closest(".ix")?.classList.add("exc");
  const L = d.linii || [];
  const P = d.parti || [];
  const CERUT = d.cerute || 4;
  const vazute = new Set();
  let ales = null;

  gazda.innerHTML = `
    ${d.sarcina ? `<p class="ix__sarcina">${d.sarcina}</p>` : ""}
    <div class="ana">
      <div class="ana__parti">
        ${P.map((x, i) => `<button class="ana__p" data-i="${i}" type="button">
          <span class="ana__pe">${esc(x.et)}</span>
          ${x.py ? `<span class="ana__py">${esc(x.py)}</span>` : ""}
        </button>`).join("")}
      </div>
      <div class="ana__cod">
        <span class="ana__acolada"></span>
        ${L.map((l, i) => `<span class="ana__l" data-l="${i}">${
          esc(l) || "&nbsp;"}</span>`).join("")}
      </div>
      <p class="ana__i">${d.intro || "Selectează o parte pentru a o evidenția în cod."}</p>
      <p class="ex__stare ana__st"></p>
    </div>`;

  const cod = gazda.querySelector(".ana__cod");
  const acol = gazda.querySelector(".ana__acolada");
  const info = gazda.querySelector(".ana__i");
  const linii = [...gazda.querySelectorAll(".ana__l")];

  gazda.querySelector(".ana__parti").addEventListener("click", ev => {
    const b = ev.target.closest(".ana__p");
    if (!b) return;
    const i = +b.dataset.i, x = P[i];
    if (ales === i){                       /* a doua apăsare stinge */
      ales = null;
      b.classList.remove("on");
      linii.forEach(l => l.classList.remove("on"));
      acol.style.display = "none";
      info.textContent = d.intro || "";
      return;
    }
    ales = i;
    gazda.querySelectorAll(".ana__p").forEach(y => y.classList.remove("on"));
    b.classList.add("on");
    const a = Math.max(0, Math.min(x.l[0], linii.length - 1));
    const z = Math.max(a, Math.min(x.l[1], linii.length - 1));
    linii.forEach((l, k) => l.classList.toggle("on", k >= a && k <= z));

    /* acolada din stânga, exact cât ține partea aleasă */
    const r1 = linii[a].getBoundingClientRect();
    const r2 = linii[Math.min(z, linii.length - 1)].getBoundingClientRect();
    const rc = cod.getBoundingClientRect();
    acol.style.display = "block";
    acol.style.top = (r1.top - rc.top + cod.scrollTop) + "px";
    acol.style.height = (r2.bottom - r1.top) + "px";

    info.innerHTML = `<b>${esc(x.et)}</b> ${x.d || ""}`;

    vazute.add(i);
    const st = gazda.querySelector(".ana__st");
    if (vazute.size >= CERUT && d.id){
      poarta(gazda, d.id, [...vazute].join(","));
      st.textContent = "Părțile cerute au fost parcurse.";
    } else if (d.id){
      st.textContent = `${vazute.size} din ${CERUT} părți deschise.`;
    }
    st.classList.add("vazut");
  });
};


/* ===========================================================================
   15. INDICE — ce măsoară SCI, și ce nu

   Prima oră trebuie să lase un singur lucru în cap: indicele e o
   probabilitate, nu o numărătoare. Formula scrisă pe tablă se uită; aici se
   mută un cursor și se vede cum aceeași legătură dă alt indice când locul
   partener e mare sau mic. Asta e exact capcana în care cade oricine
   deschide datele.
   =========================================================================== */

V.indice = (gazda, d) => {
  const A = d.a || { n: "Cluj", u: 300 };
  const B = d.b || [];                       /* locuri partenere, cu marimea */
  let i = 0;

  const linii = 1200;                        /* legaturi observate, fix */
  const maxSci = Math.max(...B.map(x => linii / (A.u * x.u) * 1e6), 1);

  gazda.innerHTML = `
    ${d.sarcina ? `<p class="ix__sarcina">${d.sarcina}</p>` : ""}
    <div class="ind">
      <div class="ind__scena">
        <div class="ind__loc ind__loc--a">
          <span class="ind__ln">${esc(A.n)}</span>
          <span class="ind__lu"><b>${A.u}</b> mii de utilizatori</span>
        </div>
        <div class="ind__pod"><i class="ind__banda"></i>
          <span class="ind__pn"><b>${linii}</b> de legături</span></div>
        <div class="ind__loc ind__loc--b">
          <span class="ind__ln ind__ln--b"></span>
          <span class="ind__lu ind__lu--b"></span>
        </div>
      </div>

      <div class="ind__alege">
        ${B.map((x, k) => `<button class="ind__b" data-k="${k}" type="button">${
          esc(x.n)}</button>`).join("")}
      </div>

      <div class="ind__calcul">
        <span class="ind__f">
          <i>SCI</i> =
          <span class="ind__fr">
            <span class="ind__sus">legături</span>
            <span class="ind__jos">utilizatori ${esc(A.n)} × utilizatori partener</span>
          </span>
        </span>
        <span class="ind__rez">= <b class="ind__v">—</b></span>
      </div>

      <p class="ind__i">${d.intro || ""}</p>
    </div>`;

  const nume = gazda.querySelector(".ind__ln--b");
  const util = gazda.querySelector(".ind__lu--b");
  const val  = gazda.querySelector(".ind__v");
  const info = gazda.querySelector(".ind__i");
  const banda = gazda.querySelector(".ind__banda");

  function arata(k){
    const x = B[k]; if (!x) return;
    i = k;
    gazda.querySelectorAll(".ind__b").forEach((b, j) =>
      b.classList.toggle("on", j === k));
    nume.textContent = x.n;
    util.innerHTML = `<b>${x.u.toLocaleString("ro-RO")}</b> mii de utilizatori`;
    const sci = Math.round(linii / (A.u * x.u) * 1e6);
    val.textContent = sci.toLocaleString("ro-RO");
    /* marimea locului partener se vede in cerc, indicele in grosimea benzii */
    gazda.querySelector(".ind__loc--b").style.setProperty("--m",
      Math.min(2.4, 0.5 + Math.sqrt(x.u / A.u)));
    /* grosimea benzii o raportez la cel mai mare indice dintre variante:
       altfel se lovește de limită la toate și nu se mai vede scăderea */
    banda.style.setProperty("--g", (3 + 23 * (sci / maxSci)).toFixed(1));
    info.innerHTML = x.d || "";
  }

  gazda.querySelector(".ind__alege").addEventListener("click", ev => {
    const b = ev.target.closest(".ind__b");
    if (b) arata(+b.dataset.k);
  });

  arata(0);
};


/* ===========================================================================
   18. DIRECȚII — migrația are sens, SCI-ul nu
   Tabelul de migrație are un rând pe direcție: românii din Italia, apoi
   italienii din România. Ca să stea lângă SCI, care are o valoare pe pereche,
   cele două direcții se pun pe același rând. Aici se vede mutarea, și se vede
   ce se întâmplă când o direcție lipsește: suma iese lipsă, nu zero.
   =========================================================================== */
V.directii = (gazda, d) => {
  const R = d.randuri || [];        // [{a, b, ab, ba}] ab = din a în b, ba = din b în a (null = lipsă)
  const f = x => x == null ? `<span class="dir__gol">lipsă</span>` : Number(x).toLocaleString("ro-RO");
  let pas = 0;
  gazda.innerHTML = `
    ${d.sarcina ? `<p class="ix__sarcina">${d.sarcina}</p>` : ""}
    <div class="dir">
      <div class="dsf__doi">
        <div>
          <span class="dsf__et">${esc(d.etSt || "migratie.csv: un rând pe direcție")}</span>
          <table class="dsf__tb dir__tb"><thead><tr><th>cetățenie</th><th>rezidență</th><th>persoane</th></tr></thead>
          <tbody>${R.map((r, i) => `
            <tr class="d1" data-i="${i}"><td>${esc(r.a)}</td><td>${esc(r.b)}</td><td class="nr">${f(r.ab)}</td></tr>
            <tr class="d2" data-i="${i}"><td>${esc(r.b)}</td><td>${esc(r.a)}</td><td class="nr">${f(r.ba)}</td></tr>`).join("")}</tbody></table>
        </div>
        <div>
          <span class="dsf__et">${esc(d.etDr || "perechi: un rând pe pereche")}</span>
          <table class="dsf__tb dir__tb"><thead><tr><th>tara_1</th><th>tara_2</th><th class="c1">din_1_in_2</th><th class="c2">din_2_in_1</th><th class="c3">migranti</th></tr></thead>
          <tbody></tbody></table>
          <p class="dsf__gol">Niciun rând încă.</p>
        </div>
      </div>
      <p class="cub__regula"></p>
      <div class="dsf__act">
        <button class="btn btn--mic btn--tare" data-rol="pas" type="button"></button>
      </div>
    </div>`;
  const tb = gazda.querySelectorAll(".dir__tb tbody")[1], gol = gazda.querySelector(".dsf__gol");
  const reg = gazda.querySelector(".cub__regula"), bt = gazda.querySelector('[data-rol="pas"]');
  const TEXT = [
    d.t0 || "Fiecare pereche apare de două ori, o dată pe direcție.",
    d.t1 || "Cele două direcții sunt acum pe același rând, ca la SCI.",
    d.t2 || "Suma: unde lipsește o direcție, lipsește și suma. Valoarea nu este cunoscută, deci nu se înlocuiește cu zero.",
  ];
  function deseneaza(){
    gazda.querySelector(".dir").classList.toggle("aprins", pas >= 1);
    tb.innerHTML = pas < 1 ? "" : R.map(r => `<tr><td>${esc(r.a)}</td><td>${esc(r.b)}</td>
      <td class="nr c1">${f(r.ab)}</td><td class="nr c2">${f(r.ba)}</td>
      <td class="nr c3">${pas < 2 ? "" : (r.ab == null || r.ba == null) ? f(null) : f(r.ab + r.ba)}</td></tr>`).join("");
    gol.hidden = pas >= 1;
    reg.innerHTML = TEXT[pas];
    bt.textContent = pas === 0 ? "Pune direcțiile pe același rând" : pas === 1 ? "Adună direcțiile" : "Reia";
  }
  bt.onclick = () => { pas = (pas + 1) % 3; deseneaza(); };
  deseneaza();
};

/* ===========================================================================
   19. HISTO — aceeași variabilă, pe scară liniară și pe scară logaritmică
   SCI-ul perechilor de țări are o coadă lungă: câteva perechi uriașe, multe
   mici. Pe scară liniară aproape toate stau într-o singură bară. Apeși
   „logaritm” și distribuția se desface. Asimetria (skew) e scrisă sub fiecare.
   =========================================================================== */
V.histo = (gazda, d) => {
  const X = (d.valori || []).filter(v => v > 0);
  const NB = d.bare || 24;
  let log = false;
  const asim = a => {               // skew, aceeași formulă ca pandas
    const n = a.length, m = a.reduce((s, v) => s + v, 0) / n;
    const s2 = a.reduce((s, v) => s + (v - m) ** 2, 0) / (n - 1);
    const s3 = a.reduce((s, v) => s + (v - m) ** 3, 0) / n;
    return (Math.sqrt(n * (n - 1)) / (n - 2)) * (s3 / Math.pow(s2 * (n - 1) / n, 1.5));
  };
  const fmt = v => v >= 1000 ? Math.round(v).toLocaleString("ro-RO") : v.toLocaleString("ro-RO", { maximumFractionDigits: 1 });
  gazda.innerHTML = `
    ${d.sarcina ? `<p class="ix__sarcina">${d.sarcina}</p>` : ""}
    <div class="hst">
      <div class="cmd__sc hst__sc">
        <button type="button" data-l="0">${esc(d.etLin || "scară liniară")}</button>
        <button type="button" data-l="1">${esc(d.etLog || "scară logaritmică")}</button>
      </div>
      <svg class="hst__svg" viewBox="0 0 600 232" role="img" aria-label="histogramă"></svg>
      <p class="cub__regula hst__txt"></p>
    </div>`;
  const svg = gazda.querySelector("svg"), txt = gazda.querySelector(".hst__txt");
  function deseneaza(){
    gazda.querySelectorAll(".hst__sc button").forEach(b => b.classList.toggle("on", +b.dataset.l === +log));
    const v = X.map(x => log ? Math.log10(x) : x);
    const lo = Math.min(...v), hi = Math.max(...v), w = (hi - lo) / NB;
    const nr = Array(NB).fill(0);
    v.forEach(x => nr[Math.min(NB - 1, Math.floor((x - lo) / w))]++);
    const max = Math.max(...nr), L = 40, R = 580, T = 28, B = 180, bw = (R - L) / NB;
    const ticks = log
      ? [3, 4, 5, 6].filter(t => t >= lo - .01 && t <= hi + .01).map(t => [t, (10 ** t).toLocaleString("ro-RO")])
      : [0, .25, .5, .75, 1].map(f => [lo + f * (hi - lo), fmt(lo + f * (hi - lo))]);
    const xp = x => L + (x - lo) / (hi - lo) * (R - L);
    svg.innerHTML = `
      <line x1="${L}" y1="${B}" x2="${R}" y2="${B}" class="hst__axa"/>
      ${nr.map((n, i) => n ? `<rect x="${L + i * bw + 1}" y="${B - n / max * (B - T)}" width="${bw - 2}" height="${n / max * (B - T)}" rx="2" class="hst__b${log ? " log" : ""}"><title>${n} perechi</title></rect>` : "").join("")}
      ${ticks.map(([t, e], i) => `<text x="${xp(t)}" y="${B + 18}" class="hst__et"${xp(t) > R - 30 ? ' style="text-anchor:end"' : ""}>${e}</text>`).join("")}
      <text x="${L}" y="${T - 12}" class="hst__et hst__et--y">${max} perechi în bara cea mai înaltă</text>
      <text x="${R}" y="${B + 36}" class="hst__et hst__titlu" style="text-anchor:end">${esc(d.axaX || "SCI")}${log ? ", scară logaritmică" : ""} →</text>
      <text x="${L - 10}" y="${(T + B) / 2}" class="hst__et hst__titlu" transform="rotate(-90 ${L - 10} ${(T + B) / 2})" style="text-anchor:middle">${esc(d.axaY || "număr de perechi")}</text>`;
    const s = asim(v);
    txt.innerHTML = log ? (d.txtLog || "") + ` Asimetria: <b>${s.toFixed(2).replace(".", ",")}</b>.`
                        : (d.txtLin || "") + ` Asimetria: <b>${s.toFixed(2).replace(".", ",")}</b>.`;
  }
  gazda.querySelectorAll(".hst__sc button").forEach(b => b.onclick = () => { log = b.dataset.l === "1"; deseneaza(); });
  deseneaza();
};

/* ===========================================================================
   20. NOR — două variabile, un nor de puncte
   Fiecare punct e o pereche de țări. Pe verticală logaritmul SCI-ului, pe
   orizontală alegi: distanța sau migranții. Perechile vecine sunt în
   chihlimbar. Dreapta e cea mai bună linie prin nor; r e scris dedesubt.
   Treci cu mouse-ul peste un punct și vezi perechea.
   =========================================================================== */
V.nor = (gazda, d) => {
  const P = d.puncte || [];             // [{t, x: {cheie: val}, y, g}]
  const VX = d.variabile || [];         // [{k, et, log}]
  let vx = 0;
  gazda.innerHTML = `
    ${d.sarcina ? `<p class="ix__sarcina">${d.sarcina}</p>` : ""}
    <div class="nor">
      <div class="cmd__sc nor__sc">${VX.map((v, i) => `<button type="button" data-v="${i}">${esc(v.et)}</button>`).join("")}</div>
      <div class="nor__desen">
        <svg viewBox="0 0 600 330" role="img" aria-label="nor de puncte"></svg>
        <div class="hs__balon nor__balon" hidden></div>
      </div>
      <div class="nor__leg"><span><i class="nor__p nor__p--g"></i>${esc(d.etG || "au graniță comună")}</span>
        <span><i class="nor__p"></i>${esc(d.etN || "fără graniță comună")}</span></div>
      <p class="cub__regula nor__txt"></p>
      ${d.cauta ? `<p class="nor__cauta"><b>Găsește:</b> ${d.cauta.t} <span>Apasă pe punctul corespunzător.</span></p>` : ""}
    </div>`;
  const svg = gazda.querySelector("svg"), bal = gazda.querySelector(".nor__balon"), txt = gazda.querySelector(".nor__txt");
  const cauta = gazda.querySelector(".nor__cauta");
  let gasit = false;
  const L = 78, R = 588, T = 18, B = 290;
  function deseneaza(){
    gazda.querySelectorAll(".nor__sc button").forEach(b => b.classList.toggle("on", +b.dataset.v === vx));
    const v = VX[vx];
    const pts = P.filter(p => p.x[v.k] != null && p.x[v.k] > 0).map(p => ({ ...p, xx: Math.log10(p.x[v.k]), yy: Math.log10(p.y) }));
    const xs = pts.map(p => p.xx), ys = pts.map(p => p.yy);
    const x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = Math.min(...ys), y1 = Math.max(...ys);
    const X = x => L + (x - x0) / (x1 - x0) * (R - L), Y = y => B - (y - y0) / (y1 - y0) * (B - T);
    const n = pts.length, mx = xs.reduce((a, b) => a + b, 0) / n, my = ys.reduce((a, b) => a + b, 0) / n;
    let sxy = 0, sxx = 0, syy = 0;
    pts.forEach(p => { sxy += (p.xx - mx) * (p.yy - my); sxx += (p.xx - mx) ** 2; syy += (p.yy - my) ** 2; });
    const b = sxy / sxx, a = my - b * mx, r = sxy / Math.sqrt(sxx * syy);
    const div = (a0, a1) => { const r = [];      // diviziuni 1, 2, 5 × 10^k în interval
      for (let k = Math.floor(a0); k <= Math.ceil(a1); k++) for (const m of [1, 2, 5]) {
        const t = k + Math.log10(m); if (t >= a0 - 1e-9 && t <= a1 + 1e-9) r.push(t); }
      return r.length > 7 ? r.filter(t => Math.abs(t - Math.round(t)) < 1e-9 || Math.abs(t - Math.round(t) - Math.log10(5)) < 1e-9) : r; };
    const tx = div(x0, x1), ty = div(y0, y1);
    const et = t => { const v = 10 ** t; return v >= 1 ? Math.round(v).toLocaleString("ro-RO") : v.toLocaleString("ro-RO", { maximumSignificantDigits: 1 }); };
    svg.innerHTML = `
      ${ty.map(t => `<line x1="${L}" x2="${R}" y1="${Y(t)}" y2="${Y(t)}" class="nor__grila"/><text x="${L - 6}" y="${Y(t) + 4}" class="hst__et nor__ety">${et(t)}</text>`).join("")}
      ${tx.map(t => `<text x="${X(t)}" y="${B + 18}" class="hst__et">${et(t)}</text>`).join("")}
      <text x="${R}" y="${B + 36}" class="hst__et nor__titlu-x">${esc(v.et)} (scară logaritmică)</text>
      <text x="${L}" y="${T - 6}" class="hst__et nor__titlu-y">${esc(d.etY || "SCI")}</text>
      <line x1="${X(x0)}" y1="${Y(a + b * x0)}" x2="${X(x1)}" y2="${Y(a + b * x1)}" class="nor__dreapta"/>
      ${pts.map((p, i) => `<circle cx="${X(p.xx)}" cy="${Y(p.yy)}" r="4.2" class="nor__p${p.g ? " nor__p--g" : ""}" data-i="${i}"/>`).join("")}`;
    svg.querySelectorAll("circle").forEach(c => {
      c.onmouseenter = () => { const p = pts[+c.dataset.i];
        bal.innerHTML = `<b>${esc(p.t)}</b><span>SCI ${Math.round(p.y).toLocaleString("ro-RO")} · ${esc(v.et)} ${p.x[v.k].toLocaleString("ro-RO", { maximumFractionDigits: 1 })}</span>`;
        bal.hidden = false; const rc = svg.getBoundingClientRect(), k = rc.width / 600;
        bal.style.left = Math.min(rc.width - 200, +c.getAttribute("cx") * k + 10) + "px"; bal.style.top = (+c.getAttribute("cy") * k - 10) + "px"; };
      c.onmouseleave = () => { bal.hidden = true; };
      /* căutarea: cât de departe e punctul ales deasupra dreptei, față de toate */
      if (d.cauta) c.onclick = () => {
        if (VX[vx].k !== (d.cauta.v || VX[0].k)){
          cauta.innerHTML = `<b>Găsește:</b> ${d.cauta.t} <span>Selectează mai întâi „${esc((VX.find(x => x.k === (d.cauta.v || VX[0].k)) || VX[0]).et)}”.</span>`; return; }
        const rez = pts.map(q => q.yy - (a + b * q.xx));
        const i = +c.dataset.i, ord = rez.map((r, k) => [r, k]).sort((u, w) => w[0] - u[0]);
        const loc = ord.findIndex(([, k]) => k === i);
        svg.querySelectorAll("circle").forEach(x => x.classList.remove("nor__p--ales"));
        c.classList.add("nor__p--ales");
        if (loc === 0){ gasit = true;
          cauta.innerHTML = `<b>Găsit: ${esc(pts[i].t)}.</b> ${d.cauta.dupa || ""}`; cauta.classList.add("ok"); }
        else if (!gasit) cauta.innerHTML = `<b>Găsește:</b> ${d.cauta.t} <span>${esc(pts[i].t)} este ${rez[i] < 0
          ? "sub dreaptă: mai puțin legată decât indică distanța"
          : `a ${loc + 1}-a din ${pts.length} după înălțimea deasupra dreptei`}. Caută un punct mai sus, mai departe de dreaptă.</span>`;
      };
    });
    txt.innerHTML = `<b>r = ${r.toFixed(2).replace(".", ",")}</b>, pe ${n} perechi. ${v.text || ""}`;
  }
  gazda.querySelectorAll(".nor__sc button").forEach(b => b.onclick = () => { vx = +b.dataset.v; deseneaza(); });
  deseneaza();
};

/* ===========================================================================
   21. AXA — același grafic, axa tăiată
   Două bare cu valori adevărate. Pe axa care pornește de la zero, diferența
   e cât e. Tai axa și diferența pare de trei ori mai mare. Graficul nu
   minte în cifre, minte în proporții.
   =========================================================================== */
V.axa = (gazda, d) => {
  const BR = d.bare || [];
  let taiat = false;
  gazda.innerHTML = `
    ${d.sarcina ? `<p class="ix__sarcina">${d.sarcina}</p>` : ""}
    <div class="axa">
      <div class="cmd__sc axa__sc">
        <button type="button" data-t="0">axa de la zero</button>
        <button type="button" data-t="1">axa tăiată la ${Number(d.taie).toLocaleString("ro-RO")}</button>
      </div>
      <svg viewBox="0 0 600 230" role="img" aria-label="bare"></svg>
      <p class="cub__regula axa__txt"></p>
    </div>`;
  const svg = gazda.querySelector("svg"), txt = gazda.querySelector(".axa__txt");
  function deseneaza(){
    gazda.querySelectorAll(".axa__sc button").forEach(b => b.classList.toggle("on", +b.dataset.t === +taiat));
    const lo = taiat ? d.taie : 0, hi = Math.max(...BR.map(b => b.v)) * 1.05;
    const L = 70, R = 590, T = 16, B = 196, bw = (R - L) / BR.length;
    const Y = v => B - (v - lo) / (hi - lo) * (B - T);
    svg.innerHTML = `
      <line x1="${L}" y1="${B}" x2="${R}" y2="${B}" class="hst__axa"/>
      <text x="${L - 8}" y="${B + 4}" class="hst__et nor__ety">${lo.toLocaleString("ro-RO")}</text>
      ${BR.map((b, i) => `<rect x="${L + i * bw + bw * .2}" y="${Y(b.v)}" width="${bw * .6}" height="${B - Y(b.v)}" rx="3" class="axa__b axa__b--${i}"/>
        <text x="${L + i * bw + bw / 2}" y="${Y(b.v) - 6}" class="hst__et axa__v">${b.v.toLocaleString("ro-RO")}</text>
        <text x="${L + i * bw + bw / 2}" y="${B + 18}" class="hst__et">${esc(b.t)}</text>`).join("")}
      ${taiat ? `<path d="M${L - 6} ${B - 8} l12 -6 M${L - 6} ${B - 2} l12 -6" class="axa__rupt"/>` : ""}`;
    const [a, b] = BR, raport = (h => h)((a.v - lo) / (b.v - lo));
    txt.innerHTML = taiat
      ? `Bara din stânga pare de <b>${raport.toFixed(1).replace(".", ",")} ori</b> mai înaltă. ${d.txtTaiat || ""}`
      : `Bara din stânga este de <b>${(a.v / b.v).toFixed(2).replace(".", ",")} ori</b> mai înaltă, exact cât raportul valorilor. ${d.txtZero || ""}`;
  }
  gazda.querySelectorAll(".axa__sc button").forEach(b => b.onclick = () => { taiat = b.dataset.t === "1"; deseneaza(); });
  deseneaza();
};

/* ===========================================================================
   22. MODELE — patru modele, pas cu pas
   Fiecare model adaugă o variabilă. Coeficienții stau ca bare în jurul lui
   zero, fiecare variabilă cu culoarea ei, iar R² crește dedesubt. Se vede
   lucrul care contează: când intră migrația, coeficientul distanței se
   micșorează. O parte din ce părea efectul distanței era migrație.
   =========================================================================== */
V.modele = (gazda, d) => {
  const M = d.modele || [];             // [{nume, formula, r2, coef: {k: v}, text}]
  const VAR = d.variabile || [];        // [{k, et, c}]
  const LIM = d.lim || 0.8;
  let i = 0;
  gazda.innerHTML = `
    ${d.sarcina ? `<p class="ix__sarcina">${d.sarcina}</p>` : ""}
    <div class="mdl">
      <div class="cmd__sc mdl__sc">${M.map((m, k) => `<button type="button" data-m="${k}">${esc(m.nume)}</button>`).join("")}</div>
      <code class="mdl__f"></code>
      <div class="mdl__rand mdl__cap"><span></span><span class="mdl__axa"><i>−${LIM}</i><i>0</i><i>+${LIM}</i></span><span></span></div>
      ${VAR.map(v => `<div class="mdl__rand" data-k="${v.k}" style="--vc:var(--${v.c})">
          <span class="mdl__n">${esc(v.et)}</span>
          <span class="mdl__pista"><span class="mdl__zero"></span><span class="mdl__b"></span></span>
          <span class="mdl__v"></span></div>`).join("")}
      <div class="mdl__r2"><span class="mdl__n">R²</span>
        <span class="mdl__pista mdl__pista--r2"><span class="mdl__b mdl__b--r2"></span></span>
        <span class="mdl__v mdl__v--r2"></span></div>
      <p class="cub__regula mdl__txt"></p>
      <div class="dsf__act"><button class="btn btn--mic btn--tare" data-rol="urm" type="button">Modelul următor</button></div>
    </div>`;
  const $ = q => gazda.querySelector(q);
  function deseneaza(){
    const m = M[i];
    gazda.querySelectorAll(".mdl__sc button").forEach(b => b.classList.toggle("on", +b.dataset.m === i));
    $(".mdl__f").textContent = m.formula;
    VAR.forEach(v => {
      const r = gazda.querySelector(`.mdl__rand[data-k="${v.k}"]`), c = m.coef[v.k];
      const b = r.querySelector(".mdl__b"), val = r.querySelector(".mdl__v");
      r.classList.toggle("absent", c == null);
      if (c == null){ b.style.width = "0"; val.textContent = "nu este inclusă"; return; }
      const w = Math.min(1, Math.abs(c) / LIM) * 50;
      b.style.width = w + "%";
      b.style.left = c >= 0 ? "50%" : (50 - w) + "%";
      val.textContent = (c >= 0 ? "+" : "−") + Math.abs(c).toFixed(2).replace(".", ",");
    });
    $(".mdl__b--r2").style.width = (m.r2 * 100) + "%";
    $(".mdl__v--r2").textContent = m.r2.toFixed(2).replace(".", ",");
    $(".mdl__txt").innerHTML = m.text || "";
    $('[data-rol="urm"]').textContent = i === M.length - 1 ? "De la capăt" : "Modelul următor";
  }
  gazda.querySelectorAll(".mdl__sc button").forEach(b => b.onclick = () => { i = +b.dataset.m; deseneaza(); });
  $('[data-rol="urm"]').onclick = () => { i = (i + 1) % M.length; deseneaza(); };
  deseneaza();
};

/* ===========================================================================
   23. GIT, ARĂTAT — comenzile ca bandă de pași

   Primul commit, ramurile și lucrul în echipă au aceeași mecanică: un șir de
   comenzi, iar fiecare comandă mută ceva pe desen. Comanda următoare e
   aprinsă; cele deja rulate rămân bifate și se pot apăsa, ca să revii la
   ele. Desenul e o funcție de k, câte comenzi s-au rulat, deci înainte și
   înapoi desenează la fel.
   =========================================================================== */

const LINISTE = () => matchMedia("(prefers-reduced-motion: reduce)").matches;

const SVG_FIS = '<svg class="ic" viewBox="0 0 16 16" aria-hidden="true"><path d="M4 1.5h5.2L12.5 4.8V14.5h-8.5z" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/><path d="M9 1.7V5h3.3" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/></svg>';
const SVG_DIR = '<svg class="ic" viewBox="0 0 16 16" aria-hidden="true"><path d="M1.5 3.5h4.3l1.5 1.6h7.2v8.4h-13z" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/></svg>';
const SVG_PC  = '<svg class="ic" viewBox="0 0 16 16" aria-hidden="true"><rect x="2.5" y="3" width="11" height="7.5" rx="1" fill="none" stroke="currentColor" stroke-width="1.3"/><path d="M1 13h14" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/></svg>';
const SVG_NOR = '<svg class="ic" viewBox="0 0 16 16" aria-hidden="true"><path d="M4.6 12.5a3 3 0 0 1-.3-6 4 4 0 0 1 7.6-.9 3.2 3.2 0 0 1 .3 6.9z" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/></svg>';

/* Mișcarea: ce exista înainte alunecă din locul vechi în cel nou; o copie
   (data-din) pleacă din locul originalului; ce e nou apare. Doar pentru
   HTML: în SVG, pixelii de pe ecran nu sunt unitățile desenului. */
function flip(cont, schimba, anim = true){
  const vechi = new Map();
  if (anim) cont.querySelectorAll("[data-k]").forEach(e => vechi.set(e.dataset.k, e.getBoundingClientRect()));
  schimba();
  if (!anim || LINISTE()) return;
  cont.querySelectorAll("[data-k]").forEach(e => {
    const b = e.getBoundingClientRect();
    const eraAici = vechi.has(e.dataset.k);
    const a = eraAici ? vechi.get(e.dataset.k) : (e.dataset.din && vechi.get(e.dataset.din));
    if (a){
      const dx = a.left - b.left, dy = a.top - b.top;
      if (Math.abs(dx) + Math.abs(dy) < 1) return;
      e.animate([{ transform:`translate(${dx}px,${dy}px)`, opacity: eraAici ? 1 : .4 },
                 { transform:"none", opacity:1 }],
                { duration:560, easing:"cubic-bezier(.3,.9,.35,1)" });
    } else {
      e.animate([{ transform:"scale(.7)", opacity:0 }, { transform:"none", opacity:1 }],
                { duration:380, easing:"cubic-bezier(.3,1.4,.6,1)" });
    }
  });
}

/* Banda de comenzi. `pasi`: [{cmd, full?, cine?, cc?, rau?, t?, txt}].
   `deseneaza(k, anim)` pune desenul în starea de după k comenzi. */
function banda(gazda, pasi, deseneaza, { start = "", laFinal } = {}){
  const n = pasi.length;
  const $c = gazda.querySelector(".bg__cmd");
  const $t = gazda.querySelector(".bg__txt");
  let k = 0, terminat = false;
  $c.innerHTML = pasi.map((p, i) => `<button type="button" class="bg__c${p.rau ? " bg__c--rau" : ""}" data-i="${i}">${
      p.cine ? `<i class="bg__cine" style="--pc:var(--${p.cc || "accent"})" title="${esc(p.cine)}">${esc(p.cine[0])}</i>` : ""}<code>${esc(p.cmd)}</code></button>`).join("")
    + `<span class="bg__nav"><button type="button" class="bg__n" data-rol="inapoi" title="pasul anterior" aria-label="pasul anterior">←</button>`
    + `<button type="button" class="bg__n" data-rol="reset" title="de la capăt" aria-label="de la capăt">↺</button></span>`;
  const arata = (anim = true) => {
    $c.querySelectorAll(".bg__c").forEach((b, i) => {
      b.classList.toggle("facut", i < k);
      b.classList.toggle("bg__c--acum", i === k);
      b.disabled = i > k;
    });
    $c.querySelector('[data-rol="inapoi"]').disabled = k === 0;
    $c.querySelector('[data-rol="reset"]').disabled = k === 0;
    const p = pasi[k - 1];
    $t.innerHTML = k === 0 ? `<p>${start}</p>`
      : `<code class="bg__full${p.rau ? " rau" : ""}${p.edit ? " edit" : ""}"><span>${p.edit ? "✎" : p.cine ? esc(p.cine) + " $" : "$"}</span>${esc(p.full || p.cmd)}</code>`
      + `<p>${p.t ? `<b>${p.t}.</b> ` : ""}${p.txt || ""}</p>`;
    deseneaza(k, anim);
    if (k === n && !terminat){ terminat = true; laFinal?.(); }
  };
  $c.addEventListener("click", e => {
    const r = e.target.closest("[data-rol]");
    if (r){ if (r.disabled) return; k = r.dataset.rol === "reset" ? 0 : Math.max(0, k - 1); arata(); return; }
    const b = e.target.closest(".bg__c");
    if (!b || b.disabled) return;
    k = +b.dataset.i + 1; arata();
  });
  arata(false);
}


/* --- Primul commit ---------------------------------------------------------
   Patru zone, ca la slide-ul cu zonele, dar cu fișierele reale ale echipei.
   git add nu mută fișierul: pune în pregătire o copie, așa cum e în acel
   moment; originalul rămâne în dosar. commit face din copii o fotografie în
   istoric, iar push o copiază pe GitHub. */

V.commit = (gazda, d) => {
  const Z = d.zone, F = d.fisiere, S = d.stari, CM = d.commituri;
  const ET = { nou:"nou", modificat:"modificat", ignorat:"ignorat", pregatit:"în pregătire", salvat:"salvat" };
  gazda.innerHTML = `
    <div class="bg">
      <div class="bg__cmd"></div>
      <div class="cz">${Z.map((z, i) => `
        <div class="cz__z" data-z="${i}">
          <span class="cz__t">${i === 0 ? SVG_PC : i === 3 ? SVG_NOR : ""}${esc(z.t)}</span>
          <span class="cz__d">${esc(z.d)}</span>
          <div class="cz__in"></div>
        </div>`).join("")}</div>
      <div class="bg__txt"></div>
    </div>`;
  const cos = [...gazda.querySelectorAll(".cz__in")];
  const fis = (k, st, cheie = k, din = "") => {
    const f = F[k];
    return `<span class="cz__f${st ? " cz__f--" + st : ""}" data-k="${cheie}"${din ? ` data-din="${din}"` : ""}>`
      + `${f.tip === "d" ? SVG_DIR : SVG_FIS}<code>${esc(f.t)}</code>`
      + `${f.m && st !== "ignorat" ? `<small>${esc(f.m)}</small>` : ""}`
      + `${st && ET[st] ? `<em>${ET[st]}</em>` : ""}</span>`;
  };
  const com = (id, loc, din = "") => {
    const c = CM[id];
    return `<span class="cz__c${c.vechi ? " vechi" : ""}" data-k="${loc}:${id}"${din ? ` data-din="${din}"` : ""}>`
      + `<span class="cz__ch"><i></i><code>${esc(c.h)}</code><small>${esc(c.x)}</small></span><b>${esc(c.m)}</b></span>`;
  };
  const deseneaza = (k, anim) => flip(gazda.querySelector(".cz"), () => {
    const s = S[k];
    cos[0].innerHTML = Object.entries(s.dosar).map(([cheie, st]) => fis(cheie, st)).join("");
    cos[1].innerHTML = (s.preg || []).map(cheie => fis(cheie, "", "p:" + cheie, cheie)).join("")
      || `<span class="cz__gol">gol</span>`;
    cos[2].innerHTML = (s.ist || []).map(id => com(id, "i")).join("");
    cos[3].innerHTML = (s.gh || []).map(id => com(id, "g", "i:" + id)).join("");
    gazda.querySelectorAll(".cz__z").forEach((z, i) => z.classList.toggle("activ", (s.activ || []).includes(i)));
  }, anim);
  banda(gazda, d.pasi, deseneaza, { start: d.start });
};


/* --- Ramurile --------------------------------------------------------------
   Graful, cu commit-uri care au nume, nu buline. Lângă el, ce conține
   fișierul din dosar: la git switch se schimbă și fișierul, iar munca de pe
   ramură nu se pierde, doar nu se vede pe main până la merge. Studentul
   apasă el comenzile, în ordine; la merge, poarta e trecută. */

V.ramuri = (gazda, d) => {
  gazda.closest(".ix")?.classList.add("exc");
  const C = d.commituri, S = d.stari, L = d.linii;
  const W = 960, H = 168, Y = { m: 122, r: 40 }, CW = 160, CH = 40;
  const X = col => 104 + col * 172;
  gazda.innerHTML = `
    <div class="bg">
      <div class="bg__cmd"></div>
      <div class="rg"><svg class="rg__svg" viewBox="0 0 ${W} ${H}" role="img" aria-label="graful ramurilor"></svg></div>
      <div class="rg__jos">
        <div class="bg__txt"></div>
        <div class="rg__dos"><span class="rg__dt">${SVG_FIS}<code>${esc(d.fisier)}</code><small>în dosar, acum</small></span><ul></ul></div>
      </div>
      <p class="ex__stare"></p>
    </div>`;
  const svg = gazda.querySelector(".rg__svg");
  const ul = gazda.querySelector(".rg__dos ul");
  let vazute = new Set();

  const margine = (id, parte) => {
    const c = C[id], x = X(c.x), y = Y[c.lane];
    return parte === "dr" ? [x + CW, y] : [x, y];
  };
  function deseneaza(k, anim){
    const s = S[k], are = new Set(s.com);
    const muchii = [], noduri = [];
    s.com.forEach(id => {
      const c = C[id];
      (c.parinti || []).filter(p => are.has(p)).forEach(p => {
        const [x1, y1] = margine(p, "dr"), [x2, y2] = margine(id, "st");
        const dd = y1 === y2 ? `M${x1} ${y1} H${x2}` : `M${x1} ${y1} C${x1 + 40} ${y1} ${x2 - 40} ${y2} ${x2} ${y2}`;
        const nou = anim && !vazute.has(id);
        muchii.push(`<path d="${dd}" pathLength="1" class="rg__m rg__m--${C[id].lane}${nou ? " nou" : ""}"/>`);
      });
      const nou = anim && !vazute.has(id);
      const x = X(c.x), y = Y[c.lane] - CH / 2;
      noduri.push(`<g class="rg__c rg__c--${c.lane}${c.merge ? " merge" : ""}${nou ? " nou" : ""}">
        <rect x="${x}" y="${y}" width="${CW}" height="${CH}" rx="9"/>
        <circle cx="${x + 14}" cy="${y + CH / 2}" r="4.5"/>
        <text x="${x + 25}" y="${y + CH / 2 + 4.2}">${esc(c.m)}</text></g>`);
    });
    /* ramura nouă, fără commit-uri încă: un ciot punctat */
    if (s.ram && !s.com.some(id => C[id].lane === "r")){
      const [x1, y1] = margine(s.din, "dr");
      noduri.unshift(`<path d="M${x1} ${y1} C${x1 + 40} ${y1} ${X(2) - 40} ${Y.r} ${X(2)} ${Y.r}" class="rg__ciot"/>`);
    }
    const eticheta = (lane, t) => `<g class="rg__e rg__e--${lane}${s.aici === lane ? " aici" : ""}">
        <rect x="4" y="${Y[lane] - 13}" width="${t.length * 7.4 + 22}" height="26" rx="13"/>
        <text x="15" y="${Y[lane] + 4.5}">${esc(t)}</text></g>`;
    svg.innerHTML = muchii.join("") + noduri.join("")
      + eticheta("m", "main") + (s.ram ? eticheta("r", d.ramura) : "");
    s.com.forEach(id => vazute.add(id));
    vazute = new Set([...vazute].filter(id => are.has(id)));

    const vede = new Set(s.vede);
    ul.innerHTML = L.map(l => `<li class="${vede.has(l.c) ? "da" : "nu"}"><i>${vede.has(l.c) ? "✓" : "○"}</i>${esc(l.t)}</li>`).join("");
  }
  banda(gazda, d.pasi, deseneaza, {
    start: d.start,
    laFinal: async () => {
      await poarta(gazda, d.id, d.pasi.map(p => p.cmd).join(" → "));
      const st = gazda.querySelector(".ex__stare");
      st.textContent = "Ramura a fost creată, folosită și îmbinată în main.";
      st.classList.add("vazut");
    }
  });
};


/* --- Lucrul în echipă ------------------------------------------------------
   Trei coloane: doi colegi și GitHub, la mijloc. Fiecare coloană e git log
   pe dev, cu cel mai nou commit sus, colorat după autor. push și pull
   copiază commit-uri dintr-o coloană în alta; un push refuzat se vede. */

V.sincron = (gazda, d) => {
  const P = d.coloane, CM = d.commituri, A = d.autori, S = d.stari;
  const coloana = (c, i) => `
    <div class="sy__col${c.gh ? " sy__col--gh" : ""}" data-col="${c.k}">
      <div class="sy__cap">${c.gh ? SVG_NOR : SVG_PC}<b>${esc(c.t)}</b><span>${esc(c.d)}</span></div>
      <div class="sy__in"></div>
      <p class="sy__rau"></p>
    </div>`;
  const sageti = g => `
    <div class="sy__s" data-g="${g}">
      <span class="sy__a" data-a="${g === 1 ? "push" : "pull"}">${g === 1 ? "push →" : "pull →"}</span>
      <span class="sy__a" data-a="${g === 1 ? "pull" : "push"}">${g === 1 ? "← pull" : "← push"}</span>
    </div>`;
  gazda.innerHTML = `
    <div class="bg">
      <div class="bg__cmd"></div>
      <div class="sy">${coloana(P[0])}${sageti(1)}${coloana(P[1])}${sageti(2)}${coloana(P[2])}</div>
      <div class="sy__leg">${Object.entries(A).map(([k, a]) => `<span><i style="background:var(--${a.c})"></i>${esc(a.et)}</span>`).join("")}</div>
      <div class="bg__txt"></div>
    </div>`;
  const sy = gazda.querySelector(".sy");
  const card = (col, id, din) => {
    const c = CM[id], a = A[c.a] || {};
    return `<span class="sy__c${c.merge ? " merge" : ""}" data-k="${col}:${id}"${din ? ` data-din="${din}:${id}"` : ""} style="--cc:var(--${a.c || "text-3"})">`
      + `<i></i><b>${esc(c.m)}</b><small>${esc(a.cine || "")}</small></span>`;
  };
  const deseneaza = (k, anim) => flip(sy, () => {
    const s = S[k];
    P.forEach(c => {
      const col = sy.querySelector(`[data-col="${c.k}"]`);
      col.querySelector(".sy__in").innerHTML = (s[c.k] || []).map(id => card(c.k, id, (s.din || {})[c.k])).join("");
      col.classList.toggle("respins", s.rau === c.k);
      col.querySelector(".sy__rau").textContent = s.rau === c.k ? d.respins : "";
    });
    sy.querySelectorAll(".sy__a").forEach(a => a.classList.remove("on", "rau"));
    Object.entries(s.sag || {}).forEach(([g, v]) => {
      const [ce, rau] = v.split(":");
      sy.querySelector(`.sy__s[data-g="${g}"] [data-a="${ce}"]`)?.classList.add("on", ...(rau ? ["rau"] : []));
    });
  }, anim);
  banda(gazda, d.pasi, deseneaza, { start: d.start });
};


/* ===========================================================================
   24. CADRUL — ce explică legătura dintre două locuri

   Modelul conceptual al proiectului, construit factor cu factor, cum îl
   estimează și modelul din C7. Fiecare factor are o ipoteză, un mecanism,
   variabila care îl măsoară și un exemplu din datele cursului. Dedesubt,
   cât explică factorii măsurați între țări (R² din C7) și cât rămâne: acolo
   stau istoria, locurile și întrebările echipelor.
   =========================================================================== */

V.cadru = (gazda, d) => {
  const F = d.factori, R = d.rest, B = d.bara;
  const n = F.length + 1;
  const W = 560, H = 250, BX = 352, BY = 70, BW = 200, BH = 100;
  const yF = i => 10 + i * 58;
  const capete = [94, 110, 128, 144];
  const uid = Math.random().toString(36).slice(2, 8);
  let k = 0;

  const factor = (f, i) => {
    const y = yF(i), ye = capete[i], ym = (y + 22 + ye) / 2;
    return `<g class="cd__f cd--${f.k}" data-i="${i + 1}" tabindex="0" role="button" aria-label="${esc(f.t)}">
      <path class="cd__s" data-m="cd-${uid}-${f.k}" d="M182 ${y + 22} C262 ${y + 22} 270 ${ye} ${BX - 8} ${ye}"/>
      <circle class="cd__semn" cx="268" cy="${ym}" r="10"/><text class="cd__semnt" x="268" y="${ym + 4.5}">${f.semn}</text>
      <rect class="cd__b" x="2" y="${y}" width="180" height="44" rx="10"/>
      <circle class="cd__nr" cx="24" cy="${y + 22}" r="11"/><text class="cd__nrt" x="24" y="${y + 26}">${i + 1}</text>
      <text class="cd__t" x="44" y="${y + 27}">${esc(f.t)}</text></g>`;
  };
  const sageti = F.map(f => `<marker id="cd-${uid}-${f.k}" viewBox="0 0 10 10" refX="8" refY="5" markerUnits="userSpaceOnUse" markerWidth="11" markerHeight="11" orient="auto-start-reverse">
      <path d="M0 0 L10 5 L0 10z" class="cd__v cd--${f.k}"/></marker>`).join("");

  gazda.innerHTML = `
    <div class="cd">
      <div class="cd__st">
        <svg class="cd__svg" viewBox="0 0 ${W} ${H}" role="img" aria-label="Modelul conceptual al proiectului">
          <defs>${sageti}</defs>
          ${F.map(factor).join("")}
          <g class="cd__rez">
            <rect x="${BX}" y="${BY}" width="${BW}" height="${BH}" rx="14"/>
            <text class="cd__rt" x="${BX + BW / 2}" y="${BY + 26}">${esc(d.rezultat.t)}</text>
            <line x1="${BX + 46}" y1="${BY + 62}" x2="${BX + BW - 46}" y2="${BY + 62}"/>
            <circle cx="${BX + 46}" cy="${BY + 62}" r="15"/><circle cx="${BX + BW - 46}" cy="${BY + 62}" r="15"/>
            <text class="cd__loc" x="${BX + 46}" y="${BY + 67}">A</text><text class="cd__loc" x="${BX + BW - 46}" y="${BY + 67}">B</text>
            <text class="cd__sci" x="${BX + BW / 2}" y="${BY + 54}">${esc(d.rezultat.d)}</text>
          </g>
          <g class="cd__f cd__f--rest cd--rest" data-i="${n}" tabindex="0" role="button" aria-label="${esc(R.t)}">
            <path class="cd__s" d="M${BX + BW / 2} ${BY + BH} V${BY + BH + 22}"/>
            <rect class="cd__b" x="${BX + 20}" y="${BY + BH + 22}" width="${BW - 40}" height="44" rx="10"/>
            <circle class="cd__nr" cx="${BX + 42}" cy="${BY + BH + 44}" r="11"/><text class="cd__nrt" x="${BX + 42}" y="${BY + BH + 48}">${n}</text>
            <text class="cd__t" x="${BX + 60}" y="${BY + BH + 49}">${esc(R.t)}</text>
          </g>
        </svg>
        <div class="cd__bara">
          <div class="cd__bt">${B.titlu}</div>
          <div class="cd__bb">${B.seg.map(s => `<span class="cd__sg cd--${s.k}" style="flex:${s.v}" data-k="${s.k}"><b>${esc(s.et)}</b></span>`).join("")}</div>
          <p class="cd__bn"></p>
        </div>
        <div class="cd__nav">
          <button class="bg__n" data-rol="inapoi" type="button">← Înapoi</button>
          <span class="cd__pct">${Array.from({ length: n }, (_, i) => `<i data-p="${i + 1}"></i>`).join("")}</span>
          <button class="bg__n bg__n--tare" data-rol="inainte" type="button">Următorul factor →</button>
        </div>
      </div>
      <div class="cd__card" aria-live="polite"></div>
    </div>`;

  const $card = gazda.querySelector(".cd__card");
  const chips = a => (a || []).map(([v, s]) => `<span class="cd__chip"><b>${esc(v)}</b>${s ? `<i>${esc(s)}</i>` : ""}</span>`).join("");
  function arata(){
    gazda.querySelectorAll(".cd__f").forEach(g => {
      const i = +g.dataset.i;
      g.classList.toggle("on", i <= k);
      g.classList.toggle("acum", i === k);
      const s = g.querySelector(".cd__s[data-m]");
      if (s){ if (i <= k) s.setAttribute("marker-end", `url(#${s.dataset.m})`); else s.removeAttribute("marker-end"); }
    });
    gazda.querySelector(".cd__rez").classList.toggle("on", k > 0);
    gazda.querySelectorAll(".cd__pct i").forEach(p => p.classList.toggle("on", +p.dataset.p <= k));
    gazda.querySelector('[data-rol="inapoi"]').disabled = k === 0;
    gazda.querySelector('[data-rol="inainte"]').textContent = k === n ? "De la capăt" : k === n - 1 ? "Ce rămâne →" : "Următorul factor →";
    gazda.querySelectorAll(".cd__sg").forEach(s => {
      const i = B.seg.findIndex(x => x.k === s.dataset.k);
      const seg = B.seg[i];
      s.classList.toggle("on", seg.de ? k >= seg.de : false);
      s.classList.toggle("acum", seg.k === "rest" ? k === n : seg.de === k);
    });
    gazda.querySelector(".cd__bn").textContent = (B.note || [])[k] || "";
    const f = k === 0 ? null : k === n ? R : F[k - 1];
    $card.className = `cd__card${f ? " cd--" + (f.k || "rest") : ""}`;
    $card.innerHTML = !f
      ? `<span class="cd__et">Întrebarea proiectului</span><p class="cd__ip">${d.intrebare}</p><p class="cd__dece">${d.start}</p>`
      : `<span class="cd__et">${k === n ? "" : `${k}. `}${esc(f.t)}${f.semn ? `<i class="cd__sm">${f.semn}</i>` : ""}</span>
         <p class="cd__ip">${f.ip}</p>
         ${f.dece ? `<p class="cd__dece">${f.dece}</p>` : ""}
         ${f.date ? `<div class="cd__rand"><span>În date</span><div>${chips(f.date)}</div></div>` : ""}
         ${f.ex ? `<div class="cd__rand"><span>Exemplu</span><p>${f.ex}</p></div>` : ""}
         ${f.lit ? `<p class="cd__lit">${f.lit}</p>` : ""}`;
  }
  gazda.addEventListener("click", e => {
    const r = e.target.closest("[data-rol]");
    if (r && !r.disabled){
      k = r.dataset.rol === "inapoi" ? Math.max(0, k - 1) : (k === n ? 0 : k + 1);
      arata(); return;
    }
    const g = e.target.closest(".cd__f");
    if (g){ k = +g.dataset.i; arata(); }
  });
  gazda.addEventListener("keydown", e => {
    const g = e.target.closest(".cd__f");
    if (g && (e.key === "Enter" || e.key === " ")){ e.preventDefault(); k = +g.dataset.i; arata(); }
  });
  arata();
};


/* ===========================================================================
   25. TABELELE — ce date are proiectul acum

   Cele patru tabele din data/c3, fiecare cu ce reprezintă un rând și două
   rânduri adevărate. Coloanele care leagă tabelele se aprind împreună: la
   cursul 4, după ele se unesc.
   =========================================================================== */

V.tabele = (gazda, d) => {
  const fmt = v => typeof v === "number" ? v.toLocaleString("ro-RO") : esc(v);
  gazda.innerHTML = `<div class="tb4">${d.tabele.map(t => `
    <div class="tb4__t" style="--tc:var(--${t.c || "text-3"})">
      <div class="tb4__cap"><code>${esc(t.f)}</code><span class="tb4__tag">${esc(t.tag)}</span>
        <span class="tb4__n">${t.n.toLocaleString("ro-RO")} rânduri</span></div>
      <table><thead><tr>${t.col.map(c => `<th${t.leg?.[c] ? ` data-leg="${t.leg[c]}" tabindex="0"` : ""}>${esc(c)}</th>`).join("")}</tr></thead>
        <tbody>${t.rows.map(r => `<tr>${r.map((v, j) => `<td class="${typeof v === "number" ? "nr" : ""}"${t.leg?.[t.col[j]] ? ` data-leg="${t.leg[t.col[j]]}"` : ""}>${fmt(v)}</td>`).join("")}</tr>`).join("")}</tbody></table>
      <p class="tb4__r"><b>Un rând:</b> ${t.rand}</p>
      ${t.nota ? `<p class="tb4__nota">${t.nota}</p>` : ""}
    </div>`).join("")}</div>
    ${d.leg ? `<p class="tb4__leg">${d.leg}</p>` : ""}`;
  const aprinde = leg => gazda.querySelectorAll("[data-leg]").forEach(e => e.classList.toggle("on", !!leg && e.dataset.leg === leg));
  let fix = null;
  gazda.addEventListener("mouseover", e => { const c = e.target.closest("[data-leg]"); if (!fix) aprinde(c?.dataset.leg); });
  gazda.addEventListener("mouseleave", () => { if (!fix) aprinde(null); });
  gazda.addEventListener("click", e => {
    const c = e.target.closest("th[data-leg]");
    fix = c && fix !== c.dataset.leg ? c.dataset.leg : null;
    aprinde(fix || c?.dataset.leg);
  });
  gazda.addEventListener("focusin", e => { const c = e.target.closest("th[data-leg]"); if (c) aprinde(c.dataset.leg); });
};


/* ===========================================================================
   SCI — indicele construit sub ochii lor, pas cu pas

   Formula scrisă pe tablă se uită. Aici se vede de unde vine fiecare bucată:
   punctele sunt utilizatori, liniile gri sunt toate prieteniile posibile
   (numitorul), liniile colorate sunt prieteniile reale (numărătorul). Apoi
   intră un loc mare, cu mai multe prietenii și indice mai mic, apoi o rețea
   de cinci locuri în care ordinea se schimbă după ce măsori. La final,
   scalarea din fișier. Numerele sunt mici, ca să se poată număra; raporturile
   sunt alese ca aritmetica să iasă rotund.
   =========================================================================== */

V.sci = (gazda, d) => {
  /* Fiecare pătrat e o pereche posibilă de utilizatori, unul din fiecare loc;
     pătratele colorate sunt prieteniile. SCI e partea colorată din grilă. */
  const CAZ = d.cazuri || [
    { n: "Republica Moldova", u: 4, f: [[0,0],[0,3],[1,1],[2,2],[4,0],[5,3]] },
    { n: "Italia", u: 12, f: [[0,1],[1,5],[2,3],[2,8],[3,10],[4,4],[4,11],[5,6],[1,9]] },
  ];
  const A = 6, nf = x => x.toLocaleString("ro-RO", { maximumFractionDigits: 3 });
  const panou = c => {
    const pr = new Set(c.f.map(([i, j]) => i + "-" + j));
    const cel = [];
    for (let i = 0; i < A; i++) for (let j = 0; j < c.u; j++) cel.push(`<i${pr.has(i + "-" + j) ? ' class="da"' : ""}></i>`);
    const tot = A * c.u;
    return `<figure class="sci2__p">
      <figcaption class="sci2__t">Cluj <span>×</span> ${esc(c.n)}</figcaption>
      <div class="sci2__ax">
        <span class="sci2__axx">${c.u} utilizatori din ${esc(c.n)} →</span>
        <span class="sci2__axy">${A} utilizatori din Cluj →</span>
        <div class="sci2__g" style="--n:${c.u}">${cel.join("")}</div>
      </div>
      <p class="sci2__calc"><b>${c.f.length}</b> prietenii ÷ (<b>${A}</b> × <b>${c.u}</b> utilizatori)</p>
      <p class="sci2__v">${nf(c.f.length / tot)}</p>
    </figure>`;
  };
  gazda.innerHTML = `<div class="sci2">
      <p class="sci2__formula"><i>SCI<sub>i,j</sub></i><span>=</span><span class="sci2__fr"><span>Prietenii<sub>i,j</sub></span><span>Utilizatori<sub>i</sub> × Utilizatori<sub>j</sub></span></span></p>
      <p class="sci2__def"><b>i, j</b>: cele două locuri; <b>Prietenii</b>: prieteniile Facebook dintre utilizatorii din i și cei din j; <b>Utilizatori</b>: utilizatorii Facebook din fiecare loc.</p>
      <p class="sci2__leg"><i></i>o pereche posibilă de utilizatori, unul din fiecare loc <i class="da"></i>o prietenie</p>
      <div class="sci2__duo">${CAZ.map(panou).join("")}</div>
      ${d.concluzie ? `<p class="sci2__conc">${d.concluzie}</p>` : ""}
    </div>`;
};


/* ===========================================================================
   PY — un Python foarte mic, cât să răspundă ca o celulă Jupyter

   Știe exact ce trebuie la tipuri, liste, dicționare și JSON: nume, numere,
   texte, indexare (și negativă), type(), len(), print(), str(), int(),
   float(), .keys(), .values(). Răspunsurile și erorile au forma celor
   adevărate, ca să le recunoască în VS Code. Valorile vin din JSON, deci
   un float întreg (0.0) se scrie {"__f": 0}, iar un tuplu {"__t": [...]}.
   =========================================================================== */
const PY = (() => {
  const T = v => v === null ? "NoneType" : typeof v === "boolean" ? "bool"
    : typeof v === "string" ? "str"
    : typeof v === "number" ? (Number.isInteger(v) ? "int" : "float")
    : Array.isArray(v) ? "list"
    : v && typeof v === "object" && "__f" in v ? "float"
    : v && typeof v === "object" && "__t" in v ? "tuple"
    : v && v.__py ? v.__py : "dict";
  const nr = v => v && typeof v === "object" && "__f" in v ? v.__f : v;
  const fl = x => { const s = String(x); return /[.e]/.test(s) || !isFinite(x) ? s : s + ".0"; };
  const strRepr = s => {
    const q = s.includes("'") && !s.includes('"') ? '"' : "'";
    return q + s.replace(/\\/g, "\\\\").replace(new RegExp(q, "g"), "\\" + q).replace(/\n/g, "\\n") + q;
  };
  const repr = v => {
    if (v && typeof v === "object" && v.__repr) return v.__repr;
    const t = T(v);
    if (t === "NoneType") return "None";
    if (t === "bool") return v ? "True" : "False";
    if (t === "str") return strRepr(v);
    if (t === "int") return String(v);
    if (t === "float") return fl(nr(v));
    if (t === "tuple") return "(" + v.__t.map(repr).join(", ") + (v.__t.length === 1 ? ",)" : ")");
    if (t === "list") return "[" + v.map(repr).join(", ") + "]";
    if (t === "type") return `<class '${v.n}'>`;
    if (t === "dict_keys" || t === "dict_values") return `${t}([${v.v.map(repr).join(", ")}])`;
    return "{" + Object.entries(v).map(([k, x]) => strRepr(k) + ": " + repr(x)).join(", ") + "}";
  };
  /* ce afișează Jupyter pentru rezultatul unei celule */
  const afis = v => T(v) === "type" ? v.n : repr(v);
  const prt = v => T(v) === "str" ? v : repr(v);

  class Er extends Error { constructor(tip, msg){ super(msg); this.tip = tip; } }

  function tokeni(src){
    const t = [], re = /\s*(?:(\d+\.\d*|\d*\.\d+|\d+)|("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')|([A-Za-z_]\w*)|(.))/gy;
    let m; re.lastIndex = 0;
    while (re.lastIndex < src.length && (m = re.exec(src))){
      if (m[1] !== undefined) t.push({ k: "n", v: m[1] });
      else if (m[2] !== undefined) t.push({ k: "s", v: m[2].slice(1, -1).replace(/\\(.)/g, "$1") });
      else if (m[3] !== undefined) t.push({ k: "i", v: m[3] });
      else if (m[4] !== undefined && m[4].trim()) t.push({ k: "p", v: m[4] });
    }
    return t;
  }

  function evalueaza(src, env){
    /* o atribuire simplă, nume = expresie: Jupyter nu afișează nimic */
    const at = src.trim().match(/^([A-Za-z_]\w*)\s*=(?!=)\s*(.+)$/s);
    if (at){ const r = evalueaza(at[2], env); env[at[1]] = r.v; return { v: null, tiparit: r.tiparit, atrib: true }; }
    const tk = tokeni(src.trim()); let i = 0, tiparit = null;
    const vezi = () => tk[i], ia = () => tk[i++];
    const cere = v => { const x = ia(); if (!x || x.v !== v) throw new Er("SyntaxError", "invalid syntax"); };
    const FN = {
      type: a => ({ __py: "type", n: (a && a.__cls) || T(a) }),
      len: a => { const t = T(a);
        if (t === "str" || t === "list") return a.length;
        if (t === "tuple") return a.__t.length;
        if (t === "dict") return Object.keys(a).length;
        throw new Er("TypeError", `object of type '${t}' has no len()`); },
      print: a => { tiparit = (tiparit === null ? "" : tiparit + "\n") + prt(a); return null; },
      str: a => prt(a),
      int: a => { const t = T(a);
        if (t === "str"){ if (!/^\s*-?\d+\s*$/.test(a)) throw new Er("ValueError", `invalid literal for int() with base 10: ${strRepr(a)}`); return parseInt(a, 10); }
        if (t === "int" || t === "bool") return +a;
        if (t === "float") return Math.trunc(nr(a));
        throw new Er("TypeError", `int() argument must be a string or a number, not '${t}'`); },
      float: a => { const t = T(a);
        if (t === "str"){ if (!/^\s*-?(\d+\.?\d*|\.\d+)\s*$/.test(a)) throw new Er("ValueError", `could not convert string to float: ${strRepr(a)}`); return { __f: parseFloat(a) }; }
        if (t === "int" || t === "float" || t === "bool") return { __f: +nr(a) };
        throw new Er("TypeError", `float() argument must be a string or a real number, not '${t}'`); },
    };
    function primar(){
      const x = ia(); if (!x) throw new Er("SyntaxError", "invalid syntax");
      if (x.k === "n") return x.v.includes(".") ? { __f: parseFloat(x.v) } : parseInt(x.v, 10);
      if (x.k === "s") return x.v;
      if (x.k === "p" && x.v === "-"){ const y = primar(); const t = T(y);
        if (t === "int") return -y; if (t === "float") return { __f: -nr(y) };
        throw new Er("TypeError", `bad operand type for unary -: '${t}'`); }
      if (x.k === "p" && x.v === "("){ const v = expr(); cere(")"); return v; }
      if (x.k === "i"){
        if (x.v === "True") return true; if (x.v === "False") return false; if (x.v === "None") return null;
        if (vezi() && vezi().v === "(" && FN[x.v]){ ia(); const a = expr(); cere(")"); return FN[x.v](a); }
        if (!(x.v in env)) throw new Er("NameError", `name '${x.v}' is not defined`);
        return env[x.v];
      }
      throw new Er("SyntaxError", "invalid syntax");
    }
    function postfix(){
      let v = primar();
      for (;;){
        const x = vezi(); if (!x || x.k !== "p") break;
        if (x.v === "["){ ia(); const k = expr(); cere("]"); v = indexeaza(v, k); continue; }
        if (x.v === "."){ ia(); const m = ia();
          if (!m || m.k !== "i") throw new Er("SyntaxError", "invalid syntax");
          const apel = vezi() && vezi().v === "(";
          let arg;
          if (apel){ ia(); if (vezi() && vezi().v !== ")") arg = expr(); cere(")"); }
          /* obiecte simulate (de exemplu un răspuns requests): atribute și metode fără argumente */
          if (v && typeof v === "object" && (v.__attr || v.__met)){
            if (v.__met && m.v in v.__met){
              v = apel ? v.__met[m.v] : { __py: "method", __repr: `<bound method ${T(v)}.${m.v} of ${repr(v)}>` };
              continue;
            }
            if (v.__attr && m.v in v.__attr){
              if (apel) throw new Er("TypeError", `'${T(v.__attr[m.v])}' object is not callable`);
              v = v.__attr[m.v]; continue;
            }
            throw new Er("AttributeError", `'${T(v)}' object has no attribute '${m.v}'`);
          }
          if (T(v) === "dict" && apel && m.v === "keys") { v = { __py: "dict_keys", v: Object.keys(v) }; continue; }
          if (T(v) === "dict" && apel && m.v === "values") { v = { __py: "dict_values", v: Object.values(v) }; continue; }
          if (T(v) === "dict" && apel && m.v === "get") { v = (arg !== undefined && String(arg) in v) ? v[arg] : null; continue; }
          throw new Er("AttributeError", `'${T(v)}' object has no attribute '${m.v}'`); }
        break;
      }
      return v;
    }
    function expr(){
      let a = postfix();
      while (vezi() && vezi().k === "p" && (vezi().v === "+" || vezi().v === "-")){
        const op = ia().v, b = postfix(), ta = T(a), tb = T(b);
        const num = t => t === "int" || t === "float" || t === "bool";
        if (op === "+" && ta === "str" && tb === "str") a = a + b;
        else if (op === "+" && ta === "list" && tb === "list") a = [...a, ...b];
        else if (num(ta) && num(tb)){
          const r = op === "+" ? nr(a) + nr(b) : nr(a) - nr(b);
          a = ta === "float" || tb === "float" ? { __f: r } : r;
        }
        else if (op === "+" && ta === "str") throw new Er("TypeError", `can only concatenate str (not "${tb}") to str`);
        else throw new Er("TypeError", `unsupported operand type(s) for ${op}: '${ta}' and '${tb}'`);
      }
      return a;
    }
    const v = expr();
    if (i < tk.length) throw new Er("SyntaxError", "invalid syntax");
    return { v, tiparit };
  }

  function indexeaza(v, k){
    const t = T(v), tk = T(k);
    if (t === "list" || t === "tuple" || t === "str"){
      const a = t === "tuple" ? v.__t : v;
      if (tk !== "int") throw new Er("TypeError", `${t === "str" ? "string" : t} indices must be integers${t === "str" ? "" : " or slices"}, not ${tk}`);
      const j = k < 0 ? a.length + k : k;
      if (j < 0 || j >= a.length) throw new Er("IndexError", `${t === "str" ? "string" : t} index out of range`);
      return a[j];
    }
    if (t === "dict"){
      if (!(String(k) in v) || tk !== "str") throw new Er("KeyError", repr(k));
      return v[k];
    }
    throw new Er("TypeError", `'${t}' object is not subscriptable`);
  }

  /* drumul unei expresii de tip a[1]["b"]: rădăcina și pașii, pentru evidențiere */
  function drum(src){
    const m = src.trim().match(/^([A-Za-z_]\w*)((?:\s*\[[^\]]+\])*)\s*$/);
    if (!m) return null;
    const pasi = [...m[2].matchAll(/\[\s*([^\]]+?)\s*\]/g)].map(x => {
      const s = x[1]; return /^-?\d+$/.test(s) ? parseInt(s, 10) : s.replace(/^["']|["']$/g, "");
    });
    return { rad: m[1], pasi };
  }

  return { T, repr, afis, prt, evalueaza, indexeaza, drum, Er };
})();


/* Consola, ca o celulă Jupyter: scrii o expresie, apeși Enter, primești Out.
   Săgeata în sus aduce comanda de dinainte. Întoarce o funcție care spune
   de câte ori a fost folosită. */
function consolaJupyter(gazda, env, { start = 2, loc = "", laRulare = null, taie = 0 } = {}){
  let n = start, ist = [], poz = 0;
  gazda.innerHTML = `<div class="jc__ist"></div>
    <label class="jc__linie"><span class="jc__in">In [${n}]:</span>
      <input class="jc__intrare" autocomplete="off" spellcheck="false" placeholder="${esc(loc)}" aria-label="Expresie Python, rulată cu Enter"></label>`;
  const istEl = gazda.querySelector(".jc__ist"), inp = gazda.querySelector(".jc__intrare");
  const eticheta = gazda.querySelector(".jc__in");
  inp.addEventListener("keydown", ev => {
    if (ev.key === "ArrowUp" && ist.length){ poz = Math.max(0, poz - 1); inp.value = ist[poz] || ""; ev.preventDefault(); return; }
    if (ev.key === "ArrowDown" && ist.length){ poz = Math.min(ist.length, poz + 1); inp.value = ist[poz] || ""; ev.preventDefault(); return; }
    if (ev.key !== "Enter") return;
    const src = inp.value.trim(); if (!src) return;
    ist.push(src); poz = ist.length;
    let html = `<div class="jc__r"><span class="jc__in">In [${n}]:</span><code>${esc(src)}</code></div>`;
    let rez = null;
    try {
      rez = PY.evalueaza(src, env);
      if (rez.tiparit !== null) html += `<pre class="jc__print">${esc(rez.tiparit)}</pre>`;
      if (rez.atrib) { /* atribuirea nu afișează nimic, ca în Jupyter */ }
      else if (rez.v === null && rez.tiparit === null)
        html += `<div class="jc__nota">nimic afișat: Jupyter nu afișează rezultatul atunci când este None</div>`;
      else if (!(rez.v === null && rez.tiparit !== null))
        { let o = PY.afis(rez.v);
          /* un răspuns întreg are mii de caractere; pe slide se arată începutul */
          if (taie && o.length > taie) o = o.slice(0, taie) + " … (" + o.length + " caractere)";
          html += `<div class="jc__r jc__r--out"><span class="jc__out">Out[${n}]:</span><code>${esc(o)}</code></div>`; }
    } catch (e){
      html += `<pre class="jc__err"><b>${esc(e.tip || "Error")}</b>: ${esc(e.message)}</pre>`;
    }
    istEl.insertAdjacentHTML("beforeend", html);
    istEl.scrollTop = istEl.scrollHeight;
    n++; eticheta.textContent = `In [${n}]:`; inp.value = "";
    if (laRulare) laRulare(src, rez);
  });
  return { folosiri: () => ist.length, focus: () => inp.focus() };
}


/* ===========================================================================
   CONSOLA DE TIPURI — ghicești tipul, iar dacă nu ești sigur, întrebi Python

   Valorile le-au văzut deja în caiet; aici nu le mai arăt pas cu pas. Scriu
   tipul fiecăreia, iar consola de dedesubt le răspunde ca Jupyter la
   type(variabila). Se înregistrează scorul și de câte ori au întrebat consola.
   =========================================================================== */
V.consola = (gazda, d) => {
  /* În stânga, codul și tipul scris de student; în dreapta, o celulă Python,
     mereu la vedere, în care se poate întreba direct: type(tara). „Verifică”
     compară răspunsurile scrise cu tipurile reale. */
  if (d.id) gazda.closest(".ix")?.classList.add("exc");
  const VARS = d.vars || [], COD = d.cod || [];
  const SIN = { none: "nonetype" };
  const norm = x => { const k = x.trim().replace(/^<class '|'>$/g, "").toLowerCase(); return SIN[k] || k; };
  let verificat = false;
  const primul = VARS[0]?.n || "x";

  gazda.innerHTML = `
    ${d.sarcina ? `<p class="ix__sarcina">${d.sarcina}</p>` : ""}
    <div class="tcs3">
      <div class="tcs3__st">
        <div class="tcs2">
          <div class="tcs2__cap"><span>Codul</span><span>Tipul</span></div>
          ${VARS.map((x, k) => `<label class="tcs2__r" data-k="${k}">
            <code class="tcs2__cod">${esc(COD[k] || x.n)}</code>
            <span class="tcs2__in"><input autocomplete="off" spellcheck="false" placeholder="tipul" aria-label="tipul lui ${esc(x.n)}"><span class="tcs2__st" aria-hidden="true"></span></span>
            <span class="tcs2__e"></span>
          </label>`).join("")}
        </div>
        <div class="tcs2__act">
          <button class="btn btn--mic btn--tare" data-rol="verifica" type="button">Verifică</button>
          <span class="tcs2__scor"></span>
        </div>
      </div>
      <div class="tcs3__dr">
        <p class="tcs3__et">Celulă Python, cu variabilele din tabel deja definite</p>
        <div class="jc"></div>
        <p class="tcs3__nota">De exemplu <code>type(${esc(primul)})</code>, apoi Enter.</p>
      </div>
    </div>`;

  const env = JSON.parse(JSON.stringify(d.env || {}));
  const cons = consolaJupyter(gazda.querySelector(".jc"), env, { start: 2, loc: `type(${primul})` });
  const randuri = [...gazda.querySelectorAll(".tcs2__r")];

  gazda.querySelector('[data-rol="verifica"]').onclick = async () => {
    let ok = 0, goale = 0;
    randuri.forEach((r, k) => {
      const x = VARS[k], v = r.querySelector("input").value;
      if (!v.trim()){ goale++; r.className = "tcs2__r gol"; r.querySelector(".tcs2__e").textContent = ""; r.querySelector(".tcs2__st").textContent = ""; return; }
      const bun = norm(v) === x.t.toLowerCase();
      if (bun) ok++;
      r.className = "tcs2__r " + (bun ? "ok" : "nu");
      r.querySelector(".tcs2__st").textContent = bun ? "✓" : "✗";
      r.querySelector(".tcs2__e").innerHTML = bun ? "" : (x.e || "");
    });
    const sc = gazda.querySelector(".tcs2__scor");
    sc.innerHTML = goale
      ? `<b>${ok} din ${VARS.length}</b> corecte; ${goale} ${goale === 1 ? "rând necompletat" : "rânduri necompletate"}.`
      : `<b>${ok} din ${VARS.length}</b>${ok === VARS.length ? ", toate corecte" : " corecte"}`;
    if (!verificat && d.id && !goale){
      verificat = true;
      await poarta(gazda, d.id, `${ok}/${VARS.length} consola:${cons.folosiri()}`);
    }
  };
};


/* ===========================================================================
   ACCES — drumul până la o valoare, construit cu clicul sau scris

   Trei feluri de a privi aceleași date:
     memorie   listele ca șir de căsuțe cu poziții (și pozițiile negative),
               dicționarele ca etichete cheie → valoare;
     coborare  vezi doar nivelul la care ai ajuns, ca niște cutii una în alta:
               intri într-o cutie și expresia crește cu un pas;
     arbore    tot răspunsul, cu fiecare rând apăsabil.
   Sub fiecare: expresia Python, „ce ai în mână” la fiecare pas (tipul și
   mărimea), Out ca în Jupyter, o consolă, și câteva ținte de găsit.
   =========================================================================== */
V.acces = (gazda, d) => {
  const ENV = d.env || {};
  const RAD = d.radacini || Object.keys(ENV);
  const VED = d.vedere || "arbore";
  const JSN = d.limbaj === "json";
  const PROV = d.provocari || [];
  const gasite = new Set();
  let cale = { rad: d.start || RAD[0], pasi: [] };

  const fmtCale = c => c.rad + c.pasi.map(p => typeof p === "number" ? `[${p}]` : `["${p}"]`).join("");
  const laCale = c => c.pasi.reduce((v, p) => PY.indexeaza(v, p), ENV[c.rad]);
  const norm = c => { let v = ENV[c.rad]; const o = [c.rad];
    for (const p of c.pasi){ const a = PY.T(v) === "tuple" ? v.__t : v;
      o.push(typeof p === "number" && p < 0 && Array.isArray(a) ? a.length + p : p); v = PY.indexeaza(v, p); }
    return JSON.stringify(o); };
  const marime = v => { const t = PY.T(v);
    if (t === "list") return `${v.length} ${v.length === 1 ? "element" : "elemente"}`;
    if (t === "tuple") return `${v.__t.length} elemente`;
    if (t === "dict") { const n = Object.keys(v).length; return `${n} ${n === 1 ? "cheie" : "chei"}`; }
    if (t === "str") return `${v.length} caractere`;
    return ""; };
  const NUME_T = { dict: "un dicționar", list: "o listă", tuple: "un tuplu", str: "un șir de caractere (str)",
    int: "un număr întreg", float: "un număr cu zecimale", bool: "o valoare logică", NoneType: "None (lipsa unei valori)" };
  const CE_FACI = { dict: "Pasul următor este o <b>cheie</b>, între ghilimele: <code>[\"nume\"]</code>.",
    list: "Pasul următor este o <b>poziție</b>, numărată de la 0: <code>[0]</code>, <code>[1]</code>… sau de la sfârșit: <code>[-1]</code>.",
    tuple: "Pasul următor este o <b>poziție</b>, ca la listă." };
  const scurt = (v, n = 34) => { const r = PY.repr(v); return r.length > n ? r.slice(0, n - 1) + "…" : r; };
  const jsonVal = v => { const t = PY.T(v);
    if (t === "NoneType") return "null"; if (t === "bool") return v ? "true" : "false";
    if (t === "str") return JSON.stringify(v); if (t === "float") return String(v.__f ?? v); return String(v); };
  const cheie = k => JSN ? `"${esc(k)}"` : `'${esc(k)}'`;

  gazda.innerHTML = `
    ${d.sarcina ? `<p class="ix__sarcina">${d.sarcina}</p>` : ""}
    <div class="acs acs--${VED}">
      ${PROV.length ? `<div class="acs__tinte"><span class="acs__tet">Găsește</span>${PROV.map((x, k) =>
        `<button class="acs__tinta" data-k="${k}" type="button"><i></i>${x.t}</button>`).join("")}</div>` : ""}
      <div class="acs__scena"></div>
      <div class="acs__expr"><span class="acs__eet">expresia</span><code class="acs__ec"></code></div>
      <div class="acs__mana"></div>
      <div class="acs__out"></div>
      ${d.consola !== false ? `<details class="acs__cons"${d.consolaDeschisa ? " open" : ""}><summary>Expresia se poate scrie și direct în consolă</summary><div class="jc"></div></details>` : ""}
    </div>`;

  const $ = q => gazda.querySelector(q);
  const scena = $(".acs__scena");

  /* ---------- memorie: căsuțe pentru liste, etichete pentru dicționare ---- */
  function deseneazaMemorie(){
    scena.innerHTML = RAD.map(r => {
      const v = ENV[r], t = PY.T(v);
      if (t === "list" || t === "tuple"){
        const a = t === "tuple" ? v.__t : v;
        return `<div class="mem"><div class="mem__n"><code>${esc(r)}</code><span>${t}</span></div>
          <div class="mem__lista">${a.map((x, i) => `<div class="mem__cel">
            <button class="mem__i" data-c='${esc(JSON.stringify({ rad: r, pasi: [i] }))}' type="button">${i}</button>
            <button class="mem__v" data-c='${esc(JSON.stringify({ rad: r, pasi: [i] }))}' type="button">${esc(PY.repr(x))}</button>
            <button class="mem__i mem__i--neg" data-c='${esc(JSON.stringify({ rad: r, pasi: [i - a.length] }))}' type="button">${i - a.length}</button>
          </div>`).join("")}</div></div>`;
      }
      if (t === "dict"){
        return `<div class="mem"><div class="mem__n"><code>${esc(r)}</code><span>dict</span></div>
          <div class="mem__dict">${Object.entries(v).map(([k, x]) => `<button class="mem__pereche" data-c='${esc(JSON.stringify({ rad: r, pasi: [k] }))}' type="button">
            <span class="mem__k">${cheie(k)}</span><span class="mem__sag">→</span><span class="mem__dv">${esc(scurt(x, 26))}</span></button>`).join("")}</div></div>`;
      }
      return `<div class="mem"><button class="mem__simplu" data-c='${esc(JSON.stringify({ rad: r, pasi: [] }))}' type="button"><code>${esc(r)}</code> = ${esc(PY.repr(v))}</button></div>`;
    }).join("");
  }

  /* ---------- arbore: tot răspunsul, fiecare rând apăsabil --------------- */
  function nod(v, c, ind, eticheta){
    const t = PY.T(v), dc = esc(JSON.stringify(c));
    const pad = `style="--ind:${ind}"`;
    const et = eticheta ? `<span class="arb__k">${eticheta}</span><span class="arb__p">: </span>` : "";
    if (t === "dict" || t === "list" || t === "tuple"){
      const des = t === "dict" ? "{" : t === "list" ? "[" : "(", inc = t === "dict" ? "}" : t === "list" ? "]" : ")";
      const copii = t === "dict" ? Object.entries(v).map(([k, x]) => nod(x, { rad: c.rad, pasi: [...c.pasi, k] }, ind + 1, cheie(k)))
        : (t === "tuple" ? v.__t : v).map((x, i) => nod(x, { rad: c.rad, pasi: [...c.pasi, i] }, ind + 1, `<span class="arb__idx">${i}</span>`));
      return `<div class="arb__r arb__r--des" data-c='${dc}' ${pad}>${et}<span class="arb__b">${des}</span><span class="arb__m">${marime(v)}</span></div>
        ${copii.join("")}<div class="arb__r arb__r--inc" ${pad}><span class="arb__b">${inc}</span></div>`;
    }
    return `<div class="arb__r" data-c='${dc}' ${pad}>${et}<span class="arb__v arb__v--${t}">${esc(JSN ? jsonVal(v) : PY.repr(v))}</span></div>`;
  }
  function deseneazaArbore(){
    scena.innerHTML = `<div class="arb">${RAD.map(r => `<div class="arb__rad"><code>${esc(r)}</code> =</div>` + nod(ENV[r], { rad: r, pasi: [] }, 0, "")).join("")}</div>`;
  }

  /* ---------- coborâre: doar nivelul curent, ca niște cutii -------------- */
  function deseneazaCoborare(){
    let v; try { v = laCale(cale); } catch { cale = { rad: cale.rad, pasi: [] }; v = ENV[cale.rad]; }
    const t = PY.T(v);
    let corp;
    if (t === "dict" || t === "list" || t === "tuple"){
      const intrari = t === "dict" ? Object.entries(v) : (t === "tuple" ? v.__t : v).map((x, i) => [i, x]);
      corp = `<div class="cob__cutii cob__cutii--${t}">${intrari.map(([k, x]) => {
        const tx = PY.T(x), dc = esc(JSON.stringify({ rad: cale.rad, pasi: [...cale.pasi, k] }));
        return `<button class="cob__cut cob__cut--${tx === "dict" || tx === "list" ? "cont" : "frunza"}" data-c='${dc}' type="button">
          <span class="cob__acc">${typeof k === "number" ? `[${k}]` : `["${esc(k)}"]`}</span>
          <span class="cob__tip">${tx}${marime(x) ? ` · ${marime(x)}` : ""}</span>
          <span class="cob__prev">${esc(scurt(x, 40))}</span>
        </button>`; }).join("")}</div>`;
    } else {
      corp = `<div class="cob__frunza"><span class="cob__tip">${t}</span><b>${esc(PY.repr(v))}</b><span>Aceasta este o valoare simplă; nu există niveluri inferioare.</span></div>`;
    }
    const sus = cale.pasi.length ? `<button class="cob__sus" type="button">↑ un nivel mai sus</button>` : "";
    scena.innerHTML = `<div class="cob__cadru" style="--niv:${cale.pasi.length}">
      <div class="cob__cap"><span class="cob__niv">nivelul ${cale.pasi.length}</span>${sus}</div>${corp}</div>`;
    scena.querySelector(".cob__sus")?.addEventListener("click", () => { cale = { rad: cale.rad, pasi: cale.pasi.slice(0, -1) }; arata(); });
  }

  const deseneaza = { memorie: deseneazaMemorie, arbore: deseneazaArbore, coborare: deseneazaCoborare }[VED];

  function arata(){
    if (VED === "coborare") deseneaza();
    /* evidențierea în scenă */
    const tinta = JSON.stringify(cale);
    scena.querySelectorAll("[data-c]").forEach(e => {
      const c = JSON.parse(e.dataset.c);
      const egal = e.dataset.c === tinta;
      const stramos = c.rad === cale.rad && c.pasi.length < cale.pasi.length &&
        c.pasi.every((p, i) => p === cale.pasi[i]);
      e.classList.toggle("on", egal); e.classList.toggle("drum", stramos);
    });
    /* expresia, colorată pe pași */
    $(".acs__ec").innerHTML = `<span class="ex__r">${esc(cale.rad)}</span>` + cale.pasi.map(p =>
      typeof p === "number" ? `<span class="ex__i">[${p}]</span>` : `<span class="ex__k">["${esc(p)}"]</span>`).join("");
    /* ce ai în mână, la fiecare pas */
    let v = ENV[cale.rad]; const lant = [{ acc: cale.rad, v }];
    let er = null;
    for (const p of cale.pasi){ try { v = PY.indexeaza(v, p); lant.push({ acc: typeof p === "number" ? `[${p}]` : `["${p}"]`, v, p }); }
      catch (e){ er = e; break; } }
    $(".acs__mana").innerHTML = `<span class="acs__met">valoarea curentă</span><div class="acs__lant">${lant.map((x, i) => {
      const t = PY.T(x.v);
      return `${i ? `<span class="acs__sag">→</span>` : ""}<button class="acs__za" data-i="${i}" type="button">
        <code>${esc(x.acc)}</code><span class="acs__zt acs__zt--${t}">${t}</span><span class="acs__zm">${marime(x.v)}</span></button>`; }).join("")}</div>
      <p class="acs__sfat">${er ? "" : (() => { const t = PY.T(v);
        return `Valoarea curentă este ${NUME_T[t] || t}. ${CE_FACI[t] || "Este o valoare simplă: calea se oprește aici."}`; })()}</p>`;
    $(".acs__out").innerHTML = er
      ? `<pre class="jc__err"><b>${esc(er.tip)}</b>: ${esc(er.message)}</pre>`
      : `<span class="jc__out">Out:</span><code>${esc((t => t.length > 170 ? t.slice(0, 169) + " …" : t)(PY.afis(v)))}</code>`;
    /* în arbore, rândul ales rămâne la vedere */
    if (VED === "arbore"){
      const box = scena.querySelector(".arb"), on = scena.querySelector(".arb__r.on");
      if (box && on && (on.offsetTop < box.scrollTop || on.offsetTop > box.scrollTop + box.clientHeight - 30))
        box.scrollTop = Math.max(0, on.offsetTop - 80);
    }
    /* ținte */
    PROV.forEach((x, k) => {
      if (gasite.has(k)) return;
      try { const c = PY.drum(x.cale);
        if (c && c.rad === cale.rad && (x.exact ? fmtCale(c) === fmtCale(cale) : norm(c) === norm(cale))) gasite.add(k); } catch {}
    });
    gazda.querySelectorAll(".acs__tinta").forEach((b, k) => b.classList.toggle("gata", gasite.has(k)));
  }

  scena.addEventListener("click", ev => {
    const e = ev.target.closest("[data-c]"); if (!e) return;
    cale = JSON.parse(e.dataset.c); arata();
  });
  $(".acs__mana").addEventListener("click", ev => {
    const b = ev.target.closest(".acs__za"); if (!b) return;
    cale = { rad: cale.rad, pasi: cale.pasi.slice(0, +b.dataset.i) }; arata();
  });
  gazda.querySelectorAll(".acs__tinta").forEach(b => b.addEventListener("click", () => {
    const x = PROV[+b.dataset.k];
    b.classList.add("ales"); setTimeout(() => b.classList.remove("ales"), 600);
    if (x.indiciu) $(".acs__mana .acs__sfat").innerHTML = `<b>Indiciu:</b> ${x.indiciu}`;
  }));
  if (d.consola !== false){
    consolaJupyter($(".jc"), ENV, { start: 1, loc: d.exemplu || `${RAD[0]}[0]`, laRulare: (src, rez) => {
      const c = PY.drum(src);
      if (c && c.rad in ENV){ try { c.pasi.reduce((v, p) => PY.indexeaza(v, p), ENV[c.rad]); cale = c; arata(); } catch {} }
    }});
  }
  if (VED !== "coborare") deseneaza();
  arata();
};


/* ===========================================================================
   GEOM — geometriile din Simple Features, desenate, cu fișa fiecăreia

   Arborele cu liniuțe arăta ierarhia, dar nu forma. Aici fiecare tip e
   desenat cum arată pe hartă, grupat după dimensiune (0 puncte, 1 linii,
   2 suprafețe), iar la clic primești fișa tehnică: definiția, WKT-ul, cum
   îl scrii în Shapely și PostGIS, regulile de validitate și ce facem noi cu
   el în proiect.
   =========================================================================== */
V.geom = (gazda, d) => {
  const G = d.geometrii || [];
  const I = {
    point: `<circle cx="40" cy="28" r="5"/>`,
    multipoint: `<circle cx="20" cy="18" r="4.5"/><circle cx="46" cy="36" r="4.5"/><circle cx="62" cy="16" r="4.5"/>`,
    linestring: `<polyline points="8,44 26,20 44,34 72,10" fill="none" class="g__l"/><circle cx="8" cy="44" r="3"/><circle cx="26" cy="20" r="3"/><circle cx="44" cy="34" r="3"/><circle cx="72" cy="10" r="3"/>`,
    multilinestring: `<polyline points="6,40 24,22 38,30" fill="none" class="g__l"/><polyline points="46,46 60,24 76,30" fill="none" class="g__l"/>`,
    polygon: `<path d="M10,46 L18,10 L52,6 L72,30 L54,50 Z M30,22 L44,20 L46,34 L32,36 Z" fill-rule="evenodd" class="g__s"/>`,
    multipolygon: `<path d="M6,40 L14,12 L38,10 L42,38 Z" class="g__s"/><path d="M50,22 L66,14 L76,30 L62,46 L50,40 Z" class="g__s"/><path d="M58,6 L66,4 L68,10 L60,12 Z" class="g__s"/>`,
    collection: `<circle cx="14" cy="16" r="4.5"/><polyline points="8,46 24,30 36,40" fill="none" class="g__l"/><path d="M46,12 L72,10 L70,40 L48,36 Z" class="g__s"/>`,
  };
  const DIM = ["0 · puncte", "1 · linii", "2 · suprafețe", "amestec"];
  let ales = d.start ?? G.findIndex(g => g.k === "polygon");

  gazda.innerHTML = `
    ${d.sarcina ? `<p class="ix__sarcina">${d.sarcina}</p>` : ""}
    <div class="geo">
      <div class="geo__grila">${G.map((g, k) => `<button class="geo__c geo__c--d${g.dim}" data-k="${k}" type="button">
        <svg viewBox="0 0 80 56" aria-hidden="true">${I[g.k] || ""}</svg>
        <span class="geo__n">${esc(g.n).replace(/^(Multi|Geometry)(?=[A-Z])/, "$1<wbr>")}</span><span class="geo__et">${esc(g.et)}</span>
      </button>`).join("")}</div>
      <div class="geo__fisa" aria-live="polite"></div>
    </div>`;

  const fisa = gazda.querySelector(".geo__fisa");
  function arata(k){
    ales = k; const g = G[k]; if (!g) return;
    gazda.querySelectorAll(".geo__c").forEach((b, j) => b.classList.toggle("on", j === k));
    const rand = (et, v, cod) => v ? `<div class="geo__r"><span class="geo__re">${et}</span>${cod ? `<code>${esc(v)}</code>` : `<p>${v}</p>`}</div>` : "";
    fisa.className = `geo__fisa geo__fisa--d${g.dim}`;
    fisa.innerHTML = `
      <div class="geo__fc">
        <svg viewBox="0 0 80 56" aria-hidden="true">${I[g.k] || ""}</svg>
        <div><h5>${esc(g.n)} <small>${esc(g.et)}</small></h5>
          <span class="geo__dim">dimensiune ${DIM[g.dim] ?? ""}</span></div>
      </div>
      <p class="geo__def">${g.def || ""}</p>
      <div class="geo__rs">
        ${rand("WKT", g.wkt, true)}
        ${rand("Python", g.py, true)}
        ${rand("PostGIS", g.pg, true)}
        ${rand("Este validă dacă", g.valid)}
        ${rand("În proiect", g.la)}
      </div>`;
  }
  gazda.querySelector(".geo__grila").addEventListener("click", ev => {
    const b = ev.target.closest(".geo__c"); if (b) arata(+b.dataset.k);
  });
  arata(ales < 0 ? 0 : ales);
};


/* ===========================================================================
   MASCA — cum păstrează pandas doar rândurile care te interesează

   Trei pași, fiecare cu bucata lui de cod aprinsă: alegi coloana, o compari
   (iese o coloană de True și False), apoi tabelul păstrează doar rândurile
   True. Rândurile sunt adevărate, din country.csv.
   =========================================================================== */
V.masca = (gazda, d) => {
  const R = d.randuri || [], C = d.coloane || [], col = d.coloana, val = d.valoare;
  const df = d.df || "df";
  const ki = C.indexOf(col);
  let pas = 0;
  const final = `${df}[${df}["${col}"] == "${val}"]`;
  const PASI = [
    { cod: df, txt: `Tabelul complet, <code>${df}</code>. Aici sunt afișate ${R.length} rânduri din cele ${d.total || "?"}.` },
    { cod: `${df}["${col}"]`, txt: `<code>${df}["${col}"]</code> selectează o singură coloană: rezultatul este o serie, cu o valoare pe fiecare rând.` },
    { cod: `${df}["${col}"] == "${val}"`, txt: `<code>==</code> compară <b>fiecare rând</b> cu <code>"${val}"</code>. Rezultatul este tot o coloană, cu valori <code>True</code> și <code>False</code>: o mască.` },
    { cod: final, txt: `Plasată între parantezele drepte ale tabelului, masca păstrează doar rândurile <code>True</code>. Din întregul fișier rămân ${d.ramase || "?"} de rânduri.` },
  ];
  gazda.innerHTML = `
    ${d.intrebare ? `<div class="msk__q"><p>${d.intrebare}</p><p class="msk__qc"><span>În cod</span><code>${esc(final)}</code></p></div>` : ""}
    <div class="msk">
      <div class="msk__cod"><code></code></div>
      <div class="msk__tab"><table>
        <thead><tr>${C.map((c, j) => `<th class="${j === ki ? "msk__k" : ""}">${esc(c)}</th>`).join("")}<th class="msk__m">== "${esc(val)}"</th></tr></thead>
        <tbody>${R.map(r => `<tr class="${r[ki] === val ? "da" : "nu"}">${r.map((x, j) => `<td class="${j === ki ? "msk__k" : ""}">${esc(x)}</td>`).join("")}
          <td class="msk__m">${r[ki] === val ? "True" : "False"}</td></tr>`).join("")}</tbody></table></div>
      <p class="msk__txt"></p>
      <div class="msk__nav">
        <button class="btn btn--mic" data-rol="inapoi" type="button">Înapoi</button>
        <span class="msk__pct">${PASI.map((_, k) => `<i data-k="${k}"></i>`).join("")}</span>
        <button class="btn btn--mic btn--tare" data-rol="inainte" type="button">Pasul următor</button>
      </div>
    </div>`;
  const $ = q => gazda.querySelector(q);
  function arata(){
    const m = $(".msk"); m.dataset.pas = pas;
    $(".msk__cod code").textContent = PASI[pas].cod;
    $(".msk__txt").innerHTML = PASI[pas].txt;
    gazda.querySelectorAll(".msk__pct i").forEach((e, k) => e.classList.toggle("on", k <= pas));
    $('[data-rol="inapoi"]').disabled = pas === 0;
    $('[data-rol="inainte"]').textContent = pas === PASI.length - 1 ? "De la capăt" : "Pasul următor";
  }
  $('[data-rol="inainte"]').onclick = () => { pas = pas === PASI.length - 1 ? 0 : pas + 1; arata(); };
  $('[data-rol="inapoi"]').onclick = () => { pas = Math.max(0, pas - 1); arata(); };
  arata();
};


/* ===========================================================================
   FOLDER — cum arată proiectul pe disc, și ce stă în fiecare dosar

   Lucrezi în folderul proiectului. Mediul virtual stă în el, în .venv, dar
   tu nu scrii acolo nimic. La clic pe fiecare dosar: ce pui în el, cine
   scrie acolo, și dacă urcă pe GitHub.
   =========================================================================== */
const IC_DOS = '<svg viewBox="0 0 16 16" width="15" height="15"><path d="M1.5 4.2c0-.6.5-1.1 1.1-1.1h3.3l1.4 1.5h6.1c.6 0 1.1.5 1.1 1.1v6.6c0 .6-.5 1.1-1.1 1.1H2.6c-.6 0-1.1-.5-1.1-1.1z" fill="currentColor"/></svg>';
const IC_FIS = '<svg viewBox="0 0 16 16" width="15" height="15"><path d="M3.5 1.5h6l3 3v10h-9z" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/><path d="M9.5 1.5v3h3" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/></svg>';
V.folder = (gazda, d) => {
  const N = d.noduri || [];
  let ales = d.start ?? 0;
  gazda.innerHTML = `
    <div class="fld">
      <div class="fld__arb">${N.map((x, k) => `<button class="fld__n fld__n--${x.fel || "dir"}${x.interzis ? " fld__n--x" : ""}" data-k="${k}" style="--ind:${x.ind || 0}" type="button">
        <span class="fld__ic" aria-hidden="true">${x.fel === "fis" ? IC_FIS : IC_DOS}</span><code>${esc(x.n)}</code>${x.scurt ? `<span class="fld__sc">${esc(x.scurt)}</span>` : ""}
      </button>`).join("")}</div>
      <div class="fld__fisa" aria-live="polite"></div>
    </div>`;
  const fisa = gazda.querySelector(".fld__fisa");
  function arata(k){
    ales = k; const x = N[k];
    gazda.querySelectorAll(".fld__n").forEach((b, j) => b.classList.toggle("on", j === k));
    fisa.className = "fld__fisa" + (x.interzis ? " fld__fisa--x" : "");
    fisa.innerHTML = `<h5><code>${esc(x.n)}</code></h5><p>${x.d || ""}</p>
      <dl>${x.cine ? `<dt>Cine scrie aici</dt><dd>${x.cine}</dd>` : ""}
          ${x.ex ? `<dt>De exemplu</dt><dd>${x.ex}</dd>` : ""}
          ${x.git ? `<dt>Pe GitHub</dt><dd>${x.git}</dd>` : ""}</dl>`;
  }
  gazda.querySelector(".fld__arb").addEventListener("click", ev => {
    const b = ev.target.closest(".fld__n"); if (b) arata(+b.dataset.k);
  });
  arata(ales);
};


/* ===========================================================================
   DSW — schema „Data Science Workflow”, exact ca la curs

   Aceleași piese și aceleași legături ca în schema din prezentare: banda
   „Analiza datelor” peste primele patru etape, raportarea în dreapta, baza
   de date jos în stânga, „ML engineering” sub implementare și optimizare,
   „Data science” dedesubt, peste tot. Săgețile pline sunt drumul, cele
   punctate sunt întoarcerile. Culorile sunt ale paletei sitului.
   =========================================================================== */
V.dsw = (gazda, d) => {
  const E = d.etape || {};
  const ch = (x0, y0, x1, y1, n = 46) => { const m = (y0 + y1) / 2;
    return `M${x0},${y0} L${x1 - n},${y0} L${x1},${m} L${x1 - n},${y1} L${x0},${y1} L${x0 + n},${m} Z`; };
  const txt = (x, y, linii, cls = "") => `<text x="${x}" y="${y - (linii.length - 1) * 14}" class="dsw__tx ${cls}" text-anchor="middle">${
    linii.map((l, i) => `<tspan x="${x}" dy="${i ? 28 : 0}">${esc(l)}</tspan>`).join("")}</text>`;
  const etapa = (k, forma, cx, cy, linii, cls) => `<g class="dsw__e dsw__e--${k}" data-k="${k}" tabindex="0" role="button" aria-label="${esc((E[k] || {}).n || k)}">
      ${forma}${txt(cx, cy + 8, linii, cls)}</g>`;
  const banda = (x, y, w, h, t, cls) => `<g class="dsw__b ${cls}"><rect x="${x}" y="${y}" width="${w}" height="${h}"/>${txt(x + w / 2, y + h / 2 + 9, [t], "dsw__bt")}</g>`;
  const sag = (id, w = 5) => `<marker id="${id}" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="${w}" markerHeight="${w}" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z"/></marker>`;

  gazda.innerHTML = `
    <div class="dsw">
      <svg viewBox="0 0 1720 800" role="img" aria-label="Schema fluxului de lucru în știința datelor">
        <defs>${sag("dsw-a", 3.4)}${sag("dsw-p", 3.6)}${sag("dsw-g", 2.3)}</defs>
        ${banda(5, 3, 890, 74, "ANALIZA DATELOR", "dsw__b--ad")}
        ${banda(1149, 612, 482, 74, "ML ENGINEERING", "dsw__b--ml")}
        ${banda(40, 713, 1591, 74, "DATA SCIENCE", "dsw__b--ds")}

        <!-- săgețile punctate: întoarcerile -->
        <path d="M525,352 C600,300 690,330 735,420" class="dsw__p" marker-start="url(#dsw-p)" marker-end="url(#dsw-p)"/>
        <path d="M795,268 C830,360 930,410 1030,425" class="dsw__p" marker-start="url(#dsw-p)" marker-end="url(#dsw-p)"/>
        <path d="M1060,422 C1200,340 1450,345 1565,425" class="dsw__p" marker-start="url(#dsw-p)" marker-end="url(#dsw-p)"/>
        <path d="M1325,425 C1350,370 1395,330 1425,298" class="dsw__p" marker-start="url(#dsw-p)" marker-end="url(#dsw-p)"/>
        <path d="M360,642 C540,700 900,705 1045,600" class="dsw__p" marker-start="url(#dsw-p)" marker-end="url(#dsw-p)"/>

        ${etapa("def", `<path d="${ch(7, 93, 260, 263)}"/>`, 140, 178, ["DEFINIREA", "PROBLEMEI"], "")}
        ${etapa("col", `<path d="${ch(225, 93, 478, 263)}"/>`, 360, 178, ["COLECTAREA", "DATELOR"], "")}
        ${etapa("cur", `<path d="${ch(440, 93, 693, 263)}"/>`, 575, 178, ["CURĂȚAREA", "DATELOR"], "")}
        ${etapa("eda", `<path d="${ch(653, 93, 932, 263)}"/>`, 800, 178, ["ANALIZA", "EXPLORATORIE", "(EDA)"], "")}
        ${etapa("rap", `<rect x="1253" y="63" width="357" height="235" rx="50"/>`, 1432, 180, ["RAPORTARE", "VIZUALIZARE"], "dsw__tx--inv")}
        ${etapa("db", `<rect x="148" y="358" width="405" height="282" rx="46"/>`, 350, 499, ["POPULAREA ȘI", "GESTIONAREA UNEI", "BAZE DE DATE"], "dsw__tx--inv")}
        ${etapa("fe", `<path d="${ch(657, 428, 927, 598)}"/>`, 800, 513, ["FEATURE", "ENGINEERING"], "")}
        ${etapa("mod", `<path d="${ch(890, 428, 1205, 598)}"/>`, 1055, 513, ["MODELARE", "(Statistică/ML)"], "")}
        ${etapa("imp", `<path d="${ch(1173, 428, 1470, 598)}"/>`, 1328, 513, ["IMPLEMENTAREA", "MODELULUI"], "")}
        ${etapa("opt", `<path d="${ch(1438, 428, 1705, 598)}"/>`, 1580, 513, ["OPTIMIZAREA", "MODELULUI"], "")}
        <!-- săgețile pline: drumul -->
        <line x1="935" y1="178" x2="1238" y2="178" class="dsw__s dsw__s--sub" marker-end="url(#dsw-a)"/>
        <line x1="350" y1="268" x2="350" y2="353" class="dsw__s dsw__s--dublu" marker-start="url(#dsw-a)" marker-end="url(#dsw-a)"/>
        <line x1="555" y1="268" x2="385" y2="355" class="dsw__s dsw__s--dublu" marker-start="url(#dsw-a)" marker-end="url(#dsw-a)"/>
        <line x1="792" y1="268" x2="792" y2="398" class="dsw__s dsw__s--gros" marker-end="url(#dsw-g)"/>
        <line x1="1040" y1="425" x2="1225" y2="290" class="dsw__s dsw__s--gros dsw__s--mod" marker-end="url(#dsw-g)"/>

      </svg>
      <div class="dsw__i" aria-live="polite"><p class="dsw__d">${d.intro || ""}</p></div>
    </div>`;

  const info = gazda.querySelector(".dsw__i");
  const alege = k => {
    const x = E[k]; if (!x) return;
    gazda.querySelectorAll(".dsw__e").forEach(g => g.classList.toggle("on", g.dataset.k === k));
    info.innerHTML = `<p class="dsw__d"><b>${esc(x.n)}</b>${x.unde ? `<span class="dsw__u">${esc(x.unde)}</span>` : ""} ${x.d || ""}</p>
      ${x.noi ? `<p class="dsw__noi">În proiect: ${x.noi}</p>` : ""}`;
  };
  gazda.querySelector("svg").addEventListener("click", ev => { const g = ev.target.closest(".dsw__e"); if (g) alege(g.dataset.k); });
  gazda.querySelector("svg").addEventListener("keydown", ev => { if (ev.key === "Enter" || ev.key === " "){ const g = ev.target.closest(".dsw__e"); if (g){ ev.preventDefault(); alege(g.dataset.k); } } });
};


/* ===========================================================================
   PANTA — aceeași listă de țări, ordonată în trei feluri

   Stânga: câți români trăiesc acolo. Mijloc: câți români la 1.000 de
   locuitori ai țării. Dreapta: SCI. Liniile arată cum urcă sau coboară
   fiecare țară. Apeși pe o țară și i se aprinde drumul.
   =========================================================================== */
V.panta = (gazda, d) => {
  const R = d.randuri || [], COL = d.coloane || [];
  const W = 760, H = 30 + R.length * 30, X = [150, 380, 610];
  const loc = k => { const o = [...R].sort((a, b) => b[k] - a[k]); return Object.fromEntries(o.map((r, i) => [r.cod, i])); };
  const L = COL.map(c => loc(c.k));
  const y = i => 30 + i * 30;
  const fmt = (v, c) => c.fmt === "mie" ? v.toLocaleString("ro-RO", { maximumFractionDigits: 1 }) : Math.round(v).toLocaleString("ro-RO");
  const evid = new Set(d.evidentiate || []);
  let ales = d.start || null;
  gazda.innerHTML = `
    <div class="pt">
      <svg viewBox="0 0 ${W} ${H + 10}" role="img" aria-label="Țările ordonate după numărul de români, după români la mie și după SCI">
        ${COL.map((c, j) => `<text x="${X[j]}" y="14" text-anchor="middle" class="pt__h">${esc(c.t)}</text>`).join("")}
        ${R.map(r => {
          const sus = L[2][r.cod] < L[0][r.cod], jos = L[2][r.cod] > L[0][r.cod];
          return `<g class="pt__r${evid.has(r.cod) ? " ev" : ""} ${sus ? "sus" : jos ? "jos" : ""}" data-c="${r.cod}">
            <polyline points="${X.map((x, j) => `${x},${y(L[j][r.cod]) + 6}`).join(" ")}" class="pt__l"/>
            ${COL.map((c, j) => `<circle cx="${X[j]}" cy="${y(L[j][r.cod]) + 6}" r="4.5" class="pt__c"/>`).join("")}
            <text x="${X[0] - 12}" y="${y(L[0][r.cod]) + 10}" text-anchor="end" class="pt__n">${esc(r.nume)} <tspan class="pt__v">${fmt(r[COL[0].k], COL[0])}</tspan></text>
            <text x="${X[2] + 12}" y="${y(L[2][r.cod]) + 10}" class="pt__n">${esc(r.nume)}</text>
          </g>`; }).join("")}
      </svg>
      <p class="pt__i" aria-live="polite"></p>
    </div>`;
  const info = gazda.querySelector(".pt__i");
  function arata(cod){
    ales = cod;
    gazda.querySelectorAll(".pt__r").forEach(g => g.classList.toggle("on", g.dataset.c === cod));
    gazda.querySelector(".pt").classList.toggle("pt--ales", !!cod);
    const r = R.find(x => x.cod === cod);
    info.innerHTML = r ? `<b>${esc(r.nume)}</b>: ${COL.map((c, j) => `${esc(c.scurt || c.t)} ${fmt(r[c.k], c)} (locul ${L[j][cod] + 1})`).join(" · ")}${r.nota ? `. ${r.nota}` : ""}` : (d.intro || "");
  }
  gazda.querySelector("svg").addEventListener("click", ev => { const g = ev.target.closest(".pt__r"); arata(g ? (g.dataset.c === ales ? null : g.dataset.c) : null); });
  arata(ales);
};


/* ===========================================================================
   DIADIC — de la un tabel de locuri la un tabel de perechi

   Trei județe. În stânga, tabelul lor obișnuit: un rând pe județ. În mijloc,
   matricea SCI: fiecare căsuță e o pereche. În dreapta, aceeași matrice
   scrisă ca tabel lung: un rând pe pereche, cu populația „de unde” și „spre
   unde” lipite din tabelul din stânga. Apeși o căsuță și vezi de unde vine
   fiecare valoare din rând.
   =========================================================================== */
V.diadic = (gazda, d) => {
  const J = d.judete || [], M = d.matrice || [];
  const n = J.length, f = x => Math.round(x).toLocaleString("ro-RO");
  let a = 0, b = 1;
  gazda.innerHTML = `
    <div class="dd">
      <section class="dd__c"><h4>Un rând = un județ</h4>
        <table class="dd__t dd__mon"><thead><tr><th>județ</th><th>populație</th></tr></thead>
        <tbody>${J.map((x, i) => `<tr data-i="${i}"><td>${esc(x.nume)}</td><td>${f(x.pop)}</td></tr>`).join("")}</tbody></table>
        <p class="dd__n">${n} rânduri</p></section>
      <section class="dd__c"><h4>Matricea SCI: o căsuță = o pereche</h4>
        <table class="dd__t dd__mat"><thead><tr><th></th>${J.map(x => `<th>${esc(x.sigla)}</th>`).join("")}</tr></thead>
        <tbody>${J.map((x, i) => `<tr><th>${esc(x.sigla)}</th>${J.map((y, j) => `<td><button data-a="${i}" data-b="${j}" type="button">${f(M[i][j] / 1000)}</button></td>`).join("")}</tr>`).join("")}</tbody></table>
        <p class="dd__n">în mii; apasă o căsuță</p></section>
      <section class="dd__c dd__c--lat"><h4>Un rând = o pereche</h4>
        <table class="dd__t dd__lung"><thead><tr><th>de unde</th><th>spre unde</th><th>SCI</th><th>pop. de unde</th><th>pop. spre unde</th></tr></thead>
        <tbody>${J.flatMap((x, i) => J.map((y, j) => `<tr data-a="${i}" data-b="${j}"><td>${esc(x.sigla)}</td><td>${esc(y.sigla)}</td><td>${f(M[i][j] / 1000)}</td><td class="dd__pa">${f(x.pop)}</td><td class="dd__pb">${f(y.pop)}</td></tr>`)).join("")}</tbody></table>
        <p class="dd__n">${n} × ${n} = ${n * n} rânduri</p></section>
    </div>
    <p class="dd__i" aria-live="polite"></p>`;
  const info = gazda.querySelector(".dd__i");
  function arata(){
    gazda.querySelectorAll(".dd__mat button").forEach(e => e.classList.toggle("on", +e.dataset.a === a && +e.dataset.b === b));
    gazda.querySelectorAll(".dd__mat button").forEach(e => e.classList.toggle("sim", +e.dataset.a === b && +e.dataset.b === a && a !== b));
    gazda.querySelectorAll(".dd__lung tr[data-a]").forEach(e => e.classList.toggle("on", +e.dataset.a === a && +e.dataset.b === b));
    gazda.querySelectorAll(".dd__mon tr[data-i]").forEach(e => { const i = +e.dataset.i;
      e.classList.toggle("ea", i === a); e.classList.toggle("eb", i === b); });
    const A = J[a], B = J[b];
    info.innerHTML = a === b
      ? `<b>${esc(A.nume)} cu ${esc(A.nume)}</b>: și perechea unui loc cu el însuși este un rând, cu prieteniile din interiorul județului.`
      : `<b>${esc(A.nume)} → ${esc(B.nume)}</b>: SCI-ul provine din matrice. Populația „de unde” este preluată din rândul ${esc(A.nume)}, cea „spre unde” din rândul ${esc(B.nume)}: <b>două îmbinări</b> cu același tabel. Căsuța cu contur punctat este perechea inversă, care la SCI are aceeași valoare.`;
  }
  gazda.querySelector(".dd__mat").addEventListener("click", ev => { const e = ev.target.closest("button[data-a]"); if (!e) return; a = +e.dataset.a; b = +e.dataset.b; arata(); });
  arata();
};


/* ===========================================================================
   RO — harta României, colorată după o întrebare simplă

   Pentru fiecare județ: e mai legat de Cluj sau de București? Culoarea arată
   încotro, intensitatea de câte ori. Treci cu mouse-ul peste un județ.
   =========================================================================== */
V.ro = (gazda, d) => {
  const J = d.judete || [], A = d.a || "Cluj", B = d.b || "București";
  const max = Math.max(...J.filter(x => x.r).map(x => Math.abs(Math.log2(x.r))));
  const cul = x => { if (!x.r) return "var(--ro-c)"; const t = Math.min(1, Math.abs(Math.log2(x.r)) / max);
    const p = Math.round(18 + 72 * Math.sqrt(t)); return `color-mix(in srgb,var(${x.r > 1 ? "--ro-a" : "--ro-b"}) ${p}%,var(--panza))`; };
  const spreA = J.filter(x => x.r > 1).length, spreB = J.filter(x => x.r && x.r < 1).length;
  gazda.innerHTML = `
    <div class="ro">
      <svg viewBox="${d.vb}" role="img" aria-label="Județele României, după legătura cu ${esc(A)} sau ${esc(B)}">
        ${J.map(x => `<path d="${x.d}" data-c="${x.cod}" class="ro__j${x.r ? "" : " ro__j--ref"}" style="fill:${cul(x)}"><title>${esc(x.nume)}</title></path>`).join("")}
        ${J.filter(x => !x.r).map(x => `<text x="${x.cx}" y="${x.cy}" text-anchor="middle" class="ro__et">${esc(x.nume)}</text>`).join("")}
      </svg>
      <aside class="ro__p">
        <div class="ro__leg"><span><i style="background:var(--ro-a)"></i>mai legat de ${esc(A)}</span><span><i style="background:var(--ro-b)"></i>mai legat de ${esc(B)}</span></div>
        <p class="ro__nr"><b>${spreA}</b> județe spre ${esc(A)}, <b>${spreB}</b> spre ${esc(B)}</p>
        <p class="ro__i" aria-live="polite">${d.intro || ""}</p>
      </aside>
    </div>`;
  const info = gazda.querySelector(".ro__i");
  const arata = cod => { const x = J.find(j => j.cod === cod); if (!x) return;
    gazda.querySelectorAll(".ro__j").forEach(p => p.classList.toggle("on", p.dataset.c === cod));
    info.innerHTML = !x.r ? `<b>${esc(x.nume)}</b>: unul dintre cele două orașe comparate.`
      : `<b>${esc(x.nume)}</b>: de ${(x.r > 1 ? x.r : 1 / x.r).toLocaleString("ro-RO", { maximumFractionDigits: 1 })} ori mai legat de ${esc(x.r > 1 ? A : B)} decât de ${esc(x.r > 1 ? B : A)}.`; };
  const svg = gazda.querySelector("svg");
  svg.addEventListener("mouseover", ev => { const p = ev.target.closest(".ro__j"); if (p) arata(p.dataset.c); });
  svg.addEventListener("click", ev => { const p = ev.target.closest(".ro__j"); if (p) arata(p.dataset.c); });
};


/* ===========================================================================
   CURSUL 2: componentele lecției despre API-uri

   O regulă comună: fiecare componentă pornește cu ceva deja ales, ca să nu
   existe panouri goale, iar culorile vin numai din variabilele paletei, ca
   să meargă la fel în modul întunecat.
   =========================================================================== */

/* --- RESTAURANT: aceeași scenă pe două straturi --------------------------
   Sus, sala restaurantului; jos, același lucru în realitate. Bonul și
   cererea HTTP se mișcă împreună, iar fiecare scenariu arată o proprietate a
   unui API: drumul unei cereri, abstractizarea, versiunea, lipsa stării.
   ------------------------------------------------------------------------- */
V.restaurant = (gazda, d) => {
  const COL = d.coloane || [], SC = d.scenarii || [];
  let sc = 0, pas = 0;
  const poz = i => i === 0 ? "left:0;transform:none"
                : i === COL.length - 1 ? "left:100%;transform:translateX(-100%)"
                : `left:${(i + .5) * (100 / COL.length)}%;transform:translateX(-50%)`;

  gazda.innerHTML = `
    <div class="rst">
      <div class="rst__sc" role="tablist">${SC.map((s, k) =>
        `<button type="button" role="tab" data-sc="${k}">${esc(s.t)}</button>`).join("")}</div>
      <div class="rst__scena">
        <span class="rst__et">La restaurant</span>
        <div class="rst__rand">${COL.map((c, i) => `<div class="rst__c" data-i="${i}" style="--c:var(--${c.c})">
          <b>${esc(c.sus)}</b><span>${esc(c.dsus || "")}</span><em class="rst__sch">schimbat</em></div>`).join("")}</div>
        <span></span>
        <div class="rst__pista"><div class="rst__tok"><span class="rst__bon"></span><code class="rst__cer"></code></div></div>
        <span class="rst__et">În realitate</span>
        <div class="rst__rand rst__rand--jos">${COL.map((c, i) => `<div class="rst__c" data-i="${i}" style="--c:var(--${c.c})">
          <b>${esc(c.jos)}</b><span>${esc(c.djos || "")}</span><em class="rst__sch">schimbat</em></div>`).join("")}</div>
      </div>
      <div class="rst__txt" aria-live="polite"></div>
      <div class="rst__nav">
        <button type="button" class="btn btn--mic" data-rol="inapoi">‹</button>
        <span class="rst__pas"></span>
        <button type="button" class="btn btn--mic btn--tare" data-rol="inainte">Pasul următor ›</button>
      </div>
    </div>`;

  const $ = s => gazda.querySelector(s);
  const tok = $(".rst__tok");
  function deseneaza(){
    const S = SC[sc], P = S.pasi[pas];
    gazda.querySelectorAll(".rst__sc button").forEach((b, k) => b.classList.toggle("on", k === sc));
    gazda.querySelectorAll(".rst__c").forEach(c => {
      const i = +c.dataset.i;
      c.classList.toggle("on", (P.col || []).includes(i));
      c.classList.toggle("schimbat", (P.schimb || []).includes(i));
    });
    tok.style.cssText = poz(P.la ?? 0);
    tok.classList.toggle("intors", !!P.intors);
    tok.classList.toggle("rau", !!P.rau);
    $(".rst__bon").textContent = P.bon || "";
    $(".rst__cer").textContent = P.cer || "";
    $(".rst__txt").innerHTML = `<p><i>La restaurant</i>${P.sus || ""}</p><p><i>În realitate</i>${P.jos || ""}</p>` +
      (pas === S.pasi.length - 1 && S.concluzie ? `<p class="rst__concl">${S.concluzie}</p>` : "");
    $(".rst__pas").textContent = `Pasul ${pas + 1} din ${S.pasi.length}`;
    $('[data-rol="inapoi"]').disabled = pas === 0;
    $('[data-rol="inainte"]').textContent = pas < S.pasi.length - 1 ? "Pasul următor ›"
      : sc < SC.length - 1 ? "Scenariul următor ›" : "De la început ↺";
  }
  $(".rst__sc").addEventListener("click", e => {
    const b = e.target.closest("button"); if (!b) return;
    sc = +b.dataset.sc; pas = 0; deseneaza();
  });
  $('[data-rol="inapoi"]').onclick = () => { pas = Math.max(0, pas - 1); deseneaza(); };
  $('[data-rol="inainte"]').onclick = () => {
    if (pas < SC[sc].pasi.length - 1) pas++;
    else { sc = (sc + 1) % SC.length; pas = 0; }
    deseneaza();
  };
  deseneaza();
};


/* --- CRITERII: tipurile de API, pe criteriile după care se taie -----------
   Patru coloane, fiecare cu întrebarea ei. Clasificările nu se contrazic:
   același API e REST, public și de tip cerere și răspuns în același timp.
   ------------------------------------------------------------------------- */
V.criterii = (gazda, d) => {
  const C = d.coloane || [];
  const toate = C.flatMap((c, k) => c.tipuri.map(t => ({ ...t, k, ct: c.t })));
  let ales = Math.max(0, toate.findIndex(t => t.n === d.ales));

  gazda.innerHTML = `
    <div class="crt">
      <div class="crt__col">${C.map((c, k) => { const o = C.slice(0, k).reduce((s, x) => s + x.tipuri.length, 0); return `
        <div class="crt__c" style="--c:var(--${c.c || "accent"})">
          <div class="crt__cap"><b>${esc(c.t)}</b><span>${esc(c.q || "")}</span></div>
          ${c.tipuri.map((t, q) =>
            `<button type="button" class="crt__t${t.noi ? " noi" : ""}" data-j="${o + q}">${esc(t.n)}${t.noi ? `<i>la curs</i>` : ""}</button>`).join("")}
        </div>`; }).join("")}</div>
      <div class="crt__det" aria-live="polite"></div>
    </div>`;

  const det = gazda.querySelector(".crt__det");
  function arata(j){
    ales = j; const t = toate[j];
    gazda.querySelectorAll(".crt__t").forEach(b => b.classList.toggle("on", +b.dataset.j === j));
    det.style.setProperty("--c", `var(--${C[t.k].c || "accent"})`);
    det.innerHTML = `<h5>${esc(t.n)} <small>${esc(t.ct)}</small></h5>
      <dl><div><dt>Ce este</dt><dd>${t.ce || ""}</dd></div>
      <div><dt>Cum funcționează</dt><dd>${t.cum || ""}</dd></div>
      <div><dt>Un exemplu real</dt><dd>${t.ex || ""}</dd></div>
      <div><dt>Pentru analiza datelor</dt><dd>${t.ds || ""}</dd></div></dl>`;
  }
  gazda.querySelector(".crt__col").addEventListener("click", e => {
    const b = e.target.closest(".crt__t"); if (b) arata(+b.dataset.j);
  });
  arata(ales);
};


/* --- BENZI: cronologia pe familii -------------------------------------------
   O axă singură amestecă lucruri care nu se înlocuiesc unele pe altele. Pe
   benzi se vede ce a venit după ce, în aceeași familie, și ce s-a petrecut
   în paralel. Versiunile HTTP stau ca repere pe axă: transportul de dedesubt.
   ------------------------------------------------------------------------- */
V.benzi = (gazda, d) => {
  const A0 = d.de || 1990, A1 = d.pana || 2026, B = d.benzi || [], R = d.repere || [];
  const x = an => ((an - A0) / (A1 - A0) * 100).toFixed(2);
  const ani = []; for (let a = Math.ceil(A0 / 5) * 5; a <= A1; a += 5) ani.push(a);
  let ales = d.ales || [0, 0];

  const banda = (b, k) => {
    const P = b.puncte.slice().sort((p, q) => p.an - q.an);
    return `<div class="bnz__b" style="--c:var(--${b.c})">
      <span class="bnz__n">${esc(b.t)}</span>
      <div class="bnz__pista">${P.map(p => {
        const xp = +x(p.an);
        const j = b.puncte.indexOf(p);
        return `<button type="button" class="bnz__p" data-b="${k}" data-p="${j}" style="left:${xp}%"
          aria-label="${p.an}, ${esc(p.n)}"><i></i><span>${esc(p.n)}</span></button>`; }).join("")}</div>
    </div>`;
  };

  gazda.innerHTML = `
    <div class="bnz">
      ${B.map(banda).join("")}
      <div class="bnz__axa"><span></span><div class="bnz__ani">
        ${ani.map(a => `<i style="left:${x(a)}%">${a}</i>`).join("")}
        ${R.map(r => `<b style="left:${x(r.an)}%" title="${esc(r.n)}, ${r.an}">${esc(r.n)}</b>`).join("")}
      </div></div>
      <div class="bnz__det" aria-live="polite"></div>
    </div>`;

  const det = gazda.querySelector(".bnz__det");
  function arata(k, j){
    ales = [k, j]; const b = B[k], p = b.puncte[j];
    gazda.querySelectorAll(".bnz__p").forEach(e => e.classList.toggle("on", +e.dataset.b === k && +e.dataset.p === j));
    det.style.setProperty("--c", `var(--${b.c})`);
    det.innerHTML = `<h5><span class="bnz__an">${p.data || p.an}</span> ${esc(p.n)} <small>${esc(b.t)}</small></h5>
      <dl><div><dt>Ce problemă rezolva</dt><dd>${p.problema || ""}</dd></div>
      <div><dt>Cum funcționează</dt><dd>${p.cum || ""}</dd></div>
      <div><dt>Unde se folosește azi</dt><dd>${p.azi || ""}</dd></div></dl>`;
  }
  gazda.addEventListener("click", e => {
    const p = e.target.closest(".bnz__p"); if (p) arata(+p.dataset.b, +p.dataset.p);
  });
  /* etichetele: deasupra punctului, iar dacă s-ar suprapune cu cea dinainte,
     dedesubt. Se calculează când componenta are lățime (slide-ul ascuns are
     zero) și din nou la fiecare redimensionare. */
  const aseaza = () => {
    gazda.querySelectorAll(".bnz__pista").forEach(pista => {
      const P = [...pista.querySelectorAll(".bnz__p")].sort((a, b) => parseFloat(a.style.left) - parseFloat(b.style.left));
      let sus = -1e9, jos = -1e9;
      P.forEach(p => {
        p.classList.remove("jos", "dr");
        const sp = p.querySelector("span"), s = sp.getBoundingClientRect();
        if (!s.width) return;
        if (s.left >= sus + 8){ sus = s.right; return; }
        if (s.left >= jos + 8){ p.classList.add("jos"); jos = s.right; return; }
        /* ambele locuri ocupate: eticheta rămâne deasupra, dar pleacă din punct spre dreapta */
        p.classList.add("dr"); sus = sp.getBoundingClientRect().right;
      });
    });
  };
  if ("ResizeObserver" in window) new ResizeObserver(aseaza).observe(gazda);
  arata(ales[0], ales[1]);
};


/* --- MESAJ: o cerere și un răspuns HTTP, ca două texte ------------------------
   HTTP e text cu o structură fixă. Fiecare rând se poate apăsa, iar
   explicația lui apare dedesubt, într-un loc care nu se mișcă.
   ------------------------------------------------------------------------- */
V.mesaj = (gazda, d) => {
  const P = d.parti || {};                       // {linie:{n,c}, antet:{…}, gol:{…}, corp:{…}}
  const M = [["cerere", d.titluCerere || "Cererea"], ["raspuns", d.titluRaspuns || "Răspunsul"]];
  let ales = d.ales || ["cerere", 0];

  const rand = (r, s, i) => `<button type="button" class="msj__r msj__r--${r.p}" data-s="${s}" data-i="${i}"
      style="--c:var(--${(P[r.p] || {}).c || "text-3"})">${r.t ? esc(r.t) : "&nbsp;"}</button>`;
  gazda.innerHTML = `
    <div class="msj">
      <div class="msj__doi">${M.map(([s, t]) => `
        <div class="msj__m"><span class="msj__t">${esc(t)}</span>
          <div class="msj__text">${(d[s] || []).map((r, i) => rand(r, s, i)).join("")}</div></div>`).join("")}</div>
      <div class="msj__leg">${Object.entries(P).map(([k, p]) =>
        `<span style="--c:var(--${p.c})"><i></i>${esc(p.n)}</span>`).join("")}</div>
      <div class="msj__det" aria-live="polite"></div>
    </div>`;

  const det = gazda.querySelector(".msj__det");
  function arata(s, i){
    ales = [s, i]; const r = d[s][i], p = P[r.p] || {};
    gazda.querySelectorAll(".msj__r").forEach(b => b.classList.toggle("on", b.dataset.s === s && +b.dataset.i === i));
    det.style.setProperty("--c", `var(--${p.c || "text-3"})`);
    det.innerHTML = `<b>${esc(p.n || "")}</b><span>${r.e || ""}</span>`;
  }
  gazda.addEventListener("click", e => {
    const b = e.target.closest(".msj__r"); if (b) arata(b.dataset.s, +b.dataset.i);
  });
  arata(ales[0], ales[1]);
};


/* --- VERBE: ce face fiecare metodă HTTP cu o resursă ---------------------------
   O colecție mică de fișe și cinci metode. Apeși o metodă și vezi efectul ei
   asupra fișelor, cererea care l-a produs și cele două proprietăți care
   contează la colectare: sigură și idempotentă.
   ------------------------------------------------------------------------- */
V.verbe = (gazda, d) => {
  const F = d.fise || [], M = d.metode || [];
  let ales = 0;
  gazda.innerHTML = `
    <div class="vrb">
      <div class="vrb__m">${M.map((m, k) => `<button type="button" data-k="${k}" style="--c:var(--${m.c})">
        <b>${m.m}</b><span>${esc(m.crud)}</span></button>`).join("")}</div>
      <div class="vrb__scena">
        <code class="vrb__cer"></code>
        <div class="vrb__fise"></div>
        <p class="vrb__efect"></p>
      </div>
      <table class="vrb__prop"><thead><tr><th></th><th>sigură</th><th>idempotentă</th></tr></thead>
        <tbody>${M.map((m, k) => `<tr data-k="${k}"><td>${m.m}</td><td>${m.sigura ? "da" : "nu"}</td><td>${m.idem}</td></tr>`).join("")}</tbody></table>
    </div>`;
  const fise = gazda.querySelector(".vrb__fise");
  function arata(k){
    ales = k; const m = M[k];
    gazda.querySelectorAll(".vrb__m button").forEach(b => b.classList.toggle("on", +b.dataset.k === k));
    gazda.querySelectorAll(".vrb__prop tr[data-k]").forEach(r => r.classList.toggle("on", +r.dataset.k === k));
    gazda.querySelector(".vrb__scena").style.setProperty("--c", `var(--${m.c})`);
    gazda.querySelector(".vrb__cer").innerHTML = `<b>${m.m}</b> ${esc(m.cale)}${m.corp ? ` <span>${esc(m.corp)}</span>` : ""}`;
    let L = F.map(f => ({ ...f, st: "" }));
    const t = L.find(f => f.id === m.tinta);
    if (m.op === "citeste" && t) t.st = "citit";
    if (m.op === "adauga") L.push({ ...m.nou, st: "nou" });
    if (m.op === "inlocuieste" && t){ Object.assign(t, m.nou); t.st = "inlocuit"; t.toate = true; }
    if (m.op === "modifica" && t){ t[m.camp] = m.valoare; t.st = "modificat"; t.ce = m.camp; }
    if (m.op === "sterge" && t) t.st = "sters";
    fise.innerHTML = L.map(f => `<div class="vrb__f ${f.st}">
      <span class="vrb__id">/echipe/${f.id}</span>
      <span class="${f.toate || f.ce === "nume" ? "sch" : ""}">${esc(f.nume)}</span>
      <span class="${f.toate || f.ce === "tema" ? "sch" : ""}">${esc(f.tema)}</span>
      ${f.st ? `<em>${{ citit: "citită", nou: "creată", inlocuit: "înlocuită", modificat: "modificată", sters: "ștearsă" }[f.st]}</em>` : ""}
    </div>`).join("");
    gazda.querySelector(".vrb__efect").innerHTML = m.efect || "";
  }
  gazda.querySelector(".vrb__m").addEventListener("click", e => {
    const b = e.target.closest("button"); if (b) arata(+b.dataset.k);
  });
  arata(0);
};


/* --- RĂSPUNS: cinci situații ale aceleiași cereri ---------------------------
   Codul de stare e primul câmp al răspunsului; clasa lui spune unde e
   problema. Antetul Content-Type arată dacă mai urmează JSON sau o pagină
   de eroare. Poarta se deschide după ce au fost încercate toate.
   ------------------------------------------------------------------------- */
V.raspuns = (gazda, d) => {
  gazda.closest(".ix")?.classList.add("exc");
  const C = d.cazuri || [], K = d.clase || [];
  const clasa = cod => Math.floor(cod / 100);
  const incercate = new Set();
  let ales = 0;
  gazda.innerHTML = `
    <div class="rsc">
      <div class="rsc__clase">${K.map(k => `<span data-k="${k.k}" style="--c:var(--${k.c})"><b>${k.k}xx</b>${esc(k.n)}</span>`).join("")}</div>
      <div class="rsc__cazuri">${C.map((c, i) => `<button type="button" data-i="${i}">${esc(c.et)}</button>`).join("")}</div>
      <div class="rsc__bara"><span class="rsc__met">GET</span><code class="rsc__url"></code>
        <button type="button" class="btn btn--mic btn--tare" data-rol="trimite">Trimite</button></div>
      <div class="rsc__out" hidden>
        <div class="rsc__st"><b class="rsc__cod"></b><span class="rsc__nume"></span></div>
        <pre class="rsc__ant"></pre>
        <pre class="rsc__corp"></pre>
        <dl class="rsc__ce"><div><dt>Ce înseamnă</dt><dd></dd></div><div><dt>Pasul următor</dt><dd></dd></div></dl>
      </div>
      <p class="rsc__nr"></p>
      <p class="ex__stare"></p>
    </div>`;
  const $ = s => gazda.querySelector(s);
  const numara = () => { $(".rsc__nr").textContent = `${incercate.size} din ${C.length} încercate`;
    $(".rsc__nr").classList.toggle("gata", incercate.size >= C.length); };
  function alege(i){
    ales = i;
    gazda.querySelectorAll(".rsc__cazuri button").forEach(b => b.classList.toggle("on", +b.dataset.i === i));
    $(".rsc__url").textContent = C[i].url || "";
    $(".rsc__out").hidden = true;
    gazda.querySelectorAll(".rsc__clase span").forEach(s => s.classList.remove("on"));
  }
  $(".rsc__cazuri").addEventListener("click", e => { const b = e.target.closest("button"); if (b) alege(+b.dataset.i); });
  $('[data-rol="trimite"]').onclick = async () => {
    const c = C[ales], k = clasa(c.cod), kk = K.find(x => +x.k === k) || {};
    $(".rsc__out").hidden = false;
    $(".rsc__out").style.setProperty("--c", `var(--${kk.c || "text-3"})`);
    $(".rsc__cod").textContent = c.cod;
    $(".rsc__nume").textContent = c.nume || "";
    $(".rsc__ant").textContent = (c.antete || []).join("\n");
    $(".rsc__corp").textContent = c.corp || "";
    const dd = gazda.querySelectorAll(".rsc__ce dd");
    dd[0].innerHTML = c.ce || ""; dd[1].innerHTML = c.faci || "";
    gazda.querySelectorAll(".rsc__clase span").forEach(s => s.classList.toggle("on", +s.dataset.k === k));
    incercate.add(ales); numara();
    if (incercate.size >= C.length){
      await poarta(gazda, d.id, [...incercate].join(","));
      $(".ex__stare").textContent = "Toate cele cinci situații au fost încercate.";
      $(".ex__stare").classList.add("vazut");
    }
  };
  alege(0); numara();
};


/* --- JUPYTER: un răspuns requests, cercetat ca într-un caiet --------------------
   Prima celulă e deja rulată: în `r` stă răspunsul. Trei ținte, fiecare cu
   indiciul ei; o țintă se bifează când o expresie care pornește de la date
   (nu un număr scris de mână) dă valoarea căutată.
   ------------------------------------------------------------------------- */
V.jupyter = (gazda, d) => {
  if (d.id) gazda.closest(".ix")?.classList.add("exc");
  const T = d.tinte || [];
  const atinse = new Array(T.length).fill(null);
  const egal = (a, b) => JSON.stringify(a) === JSON.stringify(b);
  gazda.innerHTML = `
    <div class="jpy">
      <div class="jpy__tinte">${T.map((t, k) => `<div class="jpy__ti" data-k="${k}"><span class="jpy__nr" aria-hidden="true">${k + 1}</span>
        <span class="jpy__t">${t.t}</span><span class="jpy__v"></span><button type="button" class="jpy__ind">indiciu</button>
        <span class="jpy__h" hidden>${t.ind || ""}</span><code class="jpy__e"></code></div>`).join("")}</div>
      <div class="jpy__caiet">
        <div class="jpy__celula"><span class="jc__in">In [1]:</span><pre>${esc(d.celula || "")}</pre></div>
        ${d.structura ? `<p class="jpy__str">${d.structura}</p>` : ""}
        <div class="jc"></div>
      </div>
      <p class="ex__stare"></p>
    </div>`;
  gazda.querySelector(".jpy__tinte").addEventListener("click", e => {
    const b = e.target.closest(".jpy__ind"); if (!b) return;
    const h = b.parentElement.querySelector(".jpy__h"); h.hidden = !h.hidden;
  });
  const env = JSON.parse(JSON.stringify(d.env || {}));
  consolaJupyter(gazda.querySelector(".jc"), env, { start: 2, loc: d.loc || "r.status_code", taie: d.taie || 260,
    laRulare: async (src, rez) => {
      if (!rez || rez.atrib || !/[A-Za-z_]/.test(src)) return;
      T.forEach((t, k) => {
        if (atinse[k] === null && egal(rez.v, t.v)){
          atinse[k] = src;
          const li = gazda.querySelector(`.jpy__ti[data-k="${k}"]`);
          li.classList.add("ok"); li.querySelector(".jpy__e").textContent = src;
          li.querySelector(".jpy__v").textContent = typeof t.v === "number" ? t.v.toLocaleString("ro-RO") : String(t.v);
        }
      });
      if (atinse.every(x => x !== null) && d.id){
        await poarta(gazda, d.id, atinse.join(" | "));
        const st = gazda.querySelector(".ex__stare");
        st.textContent = "Toate cele trei ținte au fost găsite."; st.classList.add("vazut");
      }
    } });
};


/* --- PAGINI: aceleași 65 de valori, tăiate în pagini --------------------------
   Schimbi per_page și vezi pe loc câte pagini ies și ce are fiecare. Primul
   element al răspunsului, dicționarul de paginare, se rescrie odată cu ele.
   ------------------------------------------------------------------------- */
V.pagini = (gazda, d) => {
  const ANI = d.ani || [], N = ANI.length, OPT = d.optiuni || [10, 50, 1000];
  const CUL = ["accent", "ambra", "roza", "ardezie", "ceas", "salvie", "text-3"];
  let pp = d.implicit || 50, pg = 1;
  gazda.innerHTML = `
    <div class="pgn">
      <div class="pgn__sus">
        <span class="pgn__et">per_page</span>
        <div class="pgn__opt">${OPT.map(o => `<button type="button" data-o="${o}">${o}</button>`).join("")}</div>
        <code class="pgn__meta"></code>
      </div>
      <div class="pgn__celule">${ANI.map((a, i) => `<i data-i="${i}" title="${a}"></i>`).join("")}</div>
      <div class="pgn__leg"></div>
    </div>`;
  const $ = s => gazda.querySelector(s);
  function deseneaza(){
    const pagini = Math.max(1, Math.ceil(N / pp));
    pg = Math.min(pg, pagini);
    gazda.querySelectorAll(".pgn__opt button").forEach(b => b.classList.toggle("on", +b.dataset.o === pp));
    gazda.querySelectorAll(".pgn__celule i").forEach(c => {
      const p = Math.floor(+c.dataset.i / pp) + 1;
      c.style.setProperty("--c", `var(--${CUL[(p - 1) % CUL.length]})`);
      c.classList.toggle("on", p === pg);
    });
    $(".pgn__meta").innerHTML = `{"page": <b>${pg}</b>, "pages": <b>${pagini}</b>, "per_page": ${pp}, "total": ${N}}`;
    $(".pgn__leg").innerHTML = Array.from({ length: pagini }, (_, k) => {
      const a = k * pp, b = Math.min(N, (k + 1) * pp) - 1;
      return `<button type="button" data-p="${k + 1}" class="${k + 1 === pg ? "on" : ""}" style="--c:var(--${CUL[k % CUL.length]})">
        <i></i>pagina ${k + 1}<span>${ANI[a]}${a !== b ? ` până la ${ANI[b]}` : ""} · ${b - a + 1} valori</span></button>`; }).join("");
  }
  $(".pgn__opt").addEventListener("click", e => { const b = e.target.closest("button"); if (b){ pp = +b.dataset.o; pg = 1; deseneaza(); } });
  $(".pgn__leg").addEventListener("click", e => { const b = e.target.closest("button"); if (b){ pg = +b.dataset.p; deseneaza(); } });
  deseneaza();
};


/* --- PAGINI2: aceleași 65 de valori, câte o cutie pentru fiecare pagină ---------
   Fiecare pagină e o cutie cu valorile ei; per_page schimbă câte cutii ies.
   Sub ele, dicționarul de paginare, cu cele două chei care contează.
   ------------------------------------------------------------------------- */
V.pagini2 = (gazda, d) => {
  const ANI = d.ani || [], N = ANI.length, OPT = d.optiuni || [10, 50, 1000];
  let pp = d.implicit || 50, pg = 1;
  gazda.innerHTML = `
    <div class="pgn2">
      <div class="pgn2__sus"><span>per_page</span>
        <div class="pgn2__opt">${OPT.map(o => `<button type="button" data-o="${o}">${o}</button>`).join("")}</div></div>
      <div class="pgn2__pag"></div>
      <p class="pgn2__meta"></p>
    </div>`;
  const $ = s => gazda.querySelector(s);
  function deseneaza(){
    const pagini = Math.max(1, Math.ceil(N / pp));
    pg = Math.min(pg, pagini);
    gazda.querySelectorAll(".pgn2__opt button").forEach(b => b.classList.toggle("on", +b.dataset.o === pp));
    $(".pgn2__pag").innerHTML = Array.from({ length: pagini }, (_, k) => {
      const a = k * pp, b = Math.min(N, (k + 1) * pp);
      return `<button type="button" data-p="${k + 1}" class="${k + 1 === pg ? "on" : ""}">
        <b>pagina ${k + 1}</b><span class="pgn2__v">${ANI.slice(a, b).map(an => `<i title="${an}"></i>`).join("")}</span>
        <small>${b - a} valori · ${ANI[a]}${b - a > 1 ? `–${ANI[b - 1]}` : ""}</small></button>`; }).join("");
    $(".pgn2__meta").innerHTML = `<code>{"page": ${pg}, "pages": <b>${pagini}</b>, "per_page": ${pp}, "total": <b>${N}</b>}</code>`
      + `<span><b>pages</b> câte pagini sunt</span><span><b>total</b> câte valori există</span>`;
  }
  $(".pgn2__opt").addEventListener("click", e => { const b = e.target.closest("button"); if (b){ pp = +b.dataset.o; pg = 1; deseneaza(); } });
  $(".pgn2__pag").addEventListener("click", e => { const b = e.target.closest("button"); if (b){ pg = +b.dataset.p; deseneaza(); } });
  deseneaza();
};


/* --- CUB: un răspuns JSON-stat, desfăcut ----------------------------------------
   Grila e cubul cu două dimensiuni. JSON-stat scrie codurile o singură dată,
   cu poziția lor, iar valorile le pune pe un singur rând, în ordinea în care
   ultima dimensiune se schimbă cea mai repede. Apeși o celulă: se aprind
   pozițiile, calculul și rândul din tabelul lung.
   ------------------------------------------------------------------------- */
V.cub = (gazda, d) => {
  const R = d.randuri, K = d.coloane, VAL = d.valori || [];
  const n = K.coduri.length;
  const fmt = v => Number(v).toLocaleString("ro-RO");
  let [ri, ci] = d.ales || [0, 0];
  const idx = o => "{" + o.coduri.map((c, i) => `<span data-c="${c}">"${c}": ${i}</span>`).join(", ") + "}";
  if (d.simplu) return cubSimplu(gazda, d);
  gazda.innerHTML = `
    <div class="cbx">
      <div class="cbx__grila">
        <table><thead><tr><th class="cbx__colt"><span class="r">${esc(R.id)}</span> \\ <span class="k">${esc(K.id)}</span></th>
          ${K.coduri.map((c, j) => `<th class="k" data-j="${j}">${c}<small>${esc(K.nume[j])}</small></th>`).join("")}</tr></thead>
        <tbody>${R.coduri.map((c, i) => `<tr><th class="r" data-i="${i}">${c}<small>${esc(R.nume[i])}</small></th>
          ${K.coduri.map((_, j) => `<td><button type="button" data-i="${i}" data-j="${j}">${fmt(VAL[i * n + j])}</button></td>`).join("")}</tr>`).join("")}</tbody></table>
      </div>
      <div class="cbx__js">
        <div><span class="cbx__k">"id":</span> ["<span class="r">${esc(R.id)}</span>", "<span class="k">${esc(K.id)}</span>"]</div>
        <div><span class="cbx__k">"size":</span> [${R.coduri.length}, ${n}]</div>
        <div><span class="cbx__k">"dimension":</span></div>
        <div class="cbx__ind r">${esc(R.id)} → index ${idx(R)}</div>
        <div class="cbx__ind k">${esc(K.id)} → index ${idx(K)}</div>
        <div><span class="cbx__k">"value":</span></div>
        <div class="cbx__val">${VAL.map((v, p) => `<span data-p="${p}"><i>${p}</i>${fmt(v)}</span>`).join("")}</div>
      </div>
      <div class="cbx__calc" aria-live="polite"></div>
    </div>`;
  function arata(i, j){
    ri = i; ci = j; const p = i * n + j;
    gazda.querySelectorAll(".cbx__grila td button").forEach(b => b.classList.toggle("on", +b.dataset.i === i && +b.dataset.j === j));
    gazda.querySelectorAll(".cbx__grila th.r").forEach(t => t.classList.toggle("on", +t.dataset.i === i));
    gazda.querySelectorAll(".cbx__grila th.k").forEach(t => t.classList.toggle("on", +t.dataset.j === j));
    gazda.querySelectorAll(".cbx__ind.r span").forEach(s => s.classList.toggle("on", s.dataset.c === R.coduri[i]));
    gazda.querySelectorAll(".cbx__ind.k span").forEach(s => s.classList.toggle("on", s.dataset.c === K.coduri[j]));
    gazda.querySelectorAll(".cbx__val span").forEach(s => s.classList.toggle("on", +s.dataset.p === p));
    gazda.querySelector(".cbx__calc").innerHTML =
      `<p><span class="cbx__et">poziția</span> <span class="r">${i}</span> × ${n} + <span class="k">${j}</span> = <b>${p}</b></p>
       <p><span class="cbx__et">rândul din tabelul lung</span> <span class="r">${esc(R.id)} ${R.coduri[i]}</span> · <span class="k">${esc(K.id)} ${K.coduri[j]}</span> · <b>${fmt(VAL[p])}</b></p>`;
  }
  gazda.querySelector(".cbx__grila").addEventListener("click", e => {
    const b = e.target.closest("td button"); if (b) arata(+b.dataset.i, +b.dataset.j);
  });
  arata(ri, ci);
};



/* ===========================================================================
   CURSUL 1, versiunea simplă: patru componente noi

   DOI NORI   SCI față de numărul de români și față de românii la mie, două
              grafice de puncte, cu corelația și dreapta de regresie.
   PERECHE    trei județe, un tabel cu un rând pe județ și unul cu un rând pe
              pereche: ce înseamnă „diadic”, fără matrice.
   VEDERI     două vederi pe același slide, cu un comutator.
   CALE       drumul până la o valoare, nivel cu nivel: alegi o cheie sau o
              poziție, iar expresia Python crește cu un pas.
   =========================================================================== */

V.doiNori = (gazda, d) => {
  const R = d.randuri || [];
  const P = d.paneluri || [];
  const et = new Set(d.etichete || []);
  const W = 380, H = 260, m = { l: 58, r: 14, t: 12, b: 44 };
  const lg = Math.log10;
  const fmt = v => v >= 1e6 ? (v / 1e6).toLocaleString("ro-RO") + " mil." : v.toLocaleString("ro-RO");
  const yT = d.yTicks || [3000, 10000, 30000, 100000];
  const yMin = lg(Math.min(yT[0], ...R.map(r => r.sci))) - 0.05, yMax = lg(Math.max(yT.at(-1), ...R.map(r => r.sci))) + 0.05;
  const Y = v => m.t + (1 - (lg(v) - yMin) / (yMax - yMin)) * (H - m.t - m.b);
  const corel = (x, y) => { const n = x.length, mx = x.reduce((a, b) => a + b) / n, my = y.reduce((a, b) => a + b) / n;
    let sxy = 0, sxx = 0, syy = 0; x.forEach((a, i) => { sxy += (a - mx) * (y[i] - my); sxx += (a - mx) ** 2; syy += (y[i] - my) ** 2; });
    return { r: sxy / Math.sqrt(sxx * syy), b: sxy / sxx, a: my - (sxy / sxx) * mx }; };
  const panou = p => {
    const xs = R.map(r => r[p.k]);
    const xMin = lg(Math.min(p.ticks[0], ...xs)) - 0.1, xMax = lg(Math.max(p.ticks.at(-1), ...xs)) + 0.1;
    const X = v => m.l + (lg(v) - xMin) / (xMax - xMin) * (W - m.l - m.r);
    const c = corel(xs.map(lg), R.map(r => lg(r.sci)));
    const lx = [xMin, xMax].map(v => 10 ** v), ly = lx.map(v => 10 ** (c.a + c.b * lg(v)));
    return `<figure class="nr2__p">
      <figcaption><span>${esc(p.t)}</span><b>r = ${c.r.toLocaleString("ro-RO", { maximumFractionDigits: 2, minimumFractionDigits: 2 })}</b></figcaption>
      <svg viewBox="0 0 ${W} ${H}" role="img" aria-label="SCI ${esc(p.t)}">
        ${yT.map(v => `<line x1="${m.l}" x2="${W - m.r}" y1="${Y(v)}" y2="${Y(v)}" class="nr2__g"/><text x="${m.l - 8}" y="${Y(v) + 4}" text-anchor="end" class="nr2__tk">${fmt(v)}</text>`).join("")}
        ${p.ticks.map(v => `<text x="${X(v)}" y="${H - m.b + 18}" text-anchor="middle" class="nr2__tk">${fmt(v)}</text>`).join("")}
        <text x="${(m.l + W - m.r) / 2}" y="${H - 6}" text-anchor="middle" class="nr2__ax">${esc(p.ax)}</text>
        <line x1="${X(lx[0])}" y1="${Y(ly[0])}" x2="${X(lx[1])}" y2="${Y(ly[1])}" class="nr2__fit"/>
        ${R.map(r => `<circle cx="${X(r[p.k])}" cy="${Y(r.sci)}" r="${et.has(r.cod) ? 5.5 : 4}" class="nr2__pt${et.has(r.cod) ? " ev" : ""}"><title>${esc(r.nume)}</title></circle>`).join("")}
        ${R.filter(r => et.has(r.cod)).map(r => { const x = X(r[p.k]), st = x > W - 92 || (p.stanga || []).includes(r.cod);
          return `<text x="${st ? x - 9 : x + 9}" y="${Y(r.sci) + 4}" text-anchor="${st ? "end" : "start"}" class="nr2__et">${esc(r.nume)}</text>`; }).join("")}
      </svg></figure>`;
  };
  gazda.innerHTML = `<div class="nr2">
      <p class="nr2__y">${esc(d.yEt || "SCI cu România")}</p>
      <div class="nr2__duo">${P.map(panou).join("")}</div>
      ${d.nota ? `<p class="nr2__n">${d.nota}</p>` : ""}
    </div>`;
};


V.pereche = (gazda, d) => {
  /* Stânga: tabelul monadic și, sub el, ce înseamnă rândul ales. Dreapta: tabelul
     diadic. Rândul ales din dreapta aprinde în stânga cele două județe din care vine. */
  const J = d.judete || [], M = d.matrice || [], n = J.length;
  const f = x => Math.round(x).toLocaleString("ro-RO");
  let a = 0, b = 1;
  gazda.innerHTML = `<div class="per">
      <div class="per__st">
        <section><h4>Un rând = un județ</h4>
          <table class="tabel per__t per__m"><thead><tr><th>județul</th><th class="num">populația</th><th></th></tr></thead>
          <tbody>${J.map((x, i) => `<tr data-i="${i}"><td>${esc(x.nume)}</td><td class="num">${f(x.pop)}</td><td class="per__rol"></td></tr>`).join("")}</tbody></table>
          <p class="per__n">${n} rânduri</p></section>
        <p class="per__i" aria-live="polite"></p>
        ${d.jos ? `<p class="per__jos">${d.jos}</p>` : ""}
      </div>
      <div class="per__s" aria-hidden="true"><b>${n} × ${n}</b><span>→</span></div>
      <section><h4>Un rând = o pereche</h4>
        <table class="tabel per__t per__p"><thead><tr><th>județul 1</th><th>județul 2</th><th class="num">SCI, în mii</th></tr></thead>
        <tbody>${J.flatMap((x, i) => J.map((y, j) => `<tr data-a="${i}" data-b="${j}"><td>${esc(x.nume)}</td><td>${esc(y.nume)}</td><td class="num">${f(M[i][j] / 1000)}</td></tr>`)).join("")}</tbody></table>
        <p class="per__n">${n * n} rânduri</p></section>
    </div>`;
  const info = gazda.querySelector(".per__i");
  const arata = () => {
    gazda.querySelectorAll(".per__p tr[data-a]").forEach(e => e.classList.toggle("on", +e.dataset.a === a && +e.dataset.b === b));
    gazda.querySelectorAll(".per__m tr[data-i]").forEach(e => {
      const i = +e.dataset.i, rol = i === a && i === b ? "1 și 2" : i === a ? "1" : i === b ? "2" : "";
      e.classList.toggle("on", !!rol);
      e.querySelector(".per__rol").textContent = rol ? "județul " + rol : "";
    });
    info.innerHTML = a === b
      ? `<b>${esc(J[a].nume)} cu ${esc(J[a].nume)}</b>: și perechea unui loc cu el însuși este un rând, cu prieteniile din interiorul județului.`
      : `<b>${esc(J[a].nume)} și ${esc(J[b].nume)}</b>: un singur rând, care descrie o relație. Populația fiecărui județ provine din tabelul de mai sus.`;
  };
  const alege = ev => { const r = ev.target.closest("tr[data-a]"); if (!r) return; a = +r.dataset.a; b = +r.dataset.b; arata(); };
  const tb = gazda.querySelector(".per__p");
  tb.addEventListener("mouseover", alege); tb.addEventListener("click", alege);
  arata();
};


V.vederi = (gazda, d) => {
  const VD = d.vederi || [];
  gazda.innerHTML = `<div class="vdr">
      <div class="vdr__b" role="tablist">${VD.map((v, i) => `<button type="button" role="tab" data-i="${i}">${esc(v.t)}</button>`).join("")}</div>
      ${VD.map((v, i) => `<div class="vdr__v" data-i="${i}" hidden>${v.text ? `<p class="vdr__t">${v.text}</p>` : ""}<div class="vdr__c"></div></div>`).join("")}
    </div>`;
  const facut = new Set();
  const arata = i => {
    gazda.querySelectorAll(".vdr__b button").forEach(b => { const on = +b.dataset.i === i; b.classList.toggle("on", on); b.setAttribute("aria-selected", on); });
    gazda.querySelectorAll(".vdr__v").forEach(v => { v.hidden = +v.dataset.i !== i; });
    if (!facut.has(i)){
      facut.add(i);
      const v = VD[i], fn = V[v.ix];
      if (fn) fn(gazda.querySelector(`.vdr__v[data-i="${i}"] .vdr__c`), v.date || {});
    }
  };
  gazda.querySelector(".vdr__b").addEventListener("click", e => { const b = e.target.closest("button"); if (b) arata(+b.dataset.i); });
  arata(0);
};


V.cale = (gazda, d) => {
  const ENV = d.env || {}, T = d.tinte || [];
  const nume = Object.keys(ENV);
  const start = nume.length === 1 ? [nume[0]] : [];
  let drum = [...start], k = 0, blocat = false;
  const eF = v => v && typeof v === "object" && !Array.isArray(v) && "__f" in v;
  const tip = v => v === null ? "NoneType" : Array.isArray(v) ? "list" : eF(v) ? "float"
    : typeof v === "object" ? "dict" : typeof v === "string" ? "str" : typeof v === "boolean" ? "bool"
    : Number.isInteger(v) ? "int" : "float";
  const py = v => v === null ? "None" : v === true ? "True" : v === false ? "False"
    : typeof v === "string" ? `'${v}'` : typeof v === "number" ? String(v)
    : eF(v) ? Number(v.__f).toFixed(1)
    : Array.isArray(v) ? "[" + v.map(py).join(", ") + "]"
    : "{" + Object.entries(v).map(([x, y]) => `'${x}': ${py(y)}`).join(", ") + "}";
  const scurt = (s, n = 44) => s.length > n ? s.slice(0, n - 1) + "…" : s;
  const valoare = () => { let v = ENV[drum[0]]; for (const p of drum.slice(1)) v = v[p]; return v; };
  const pas = p => typeof p === "number" ? `[${p}]` : `["${p}"]`;
  const expr = () => drum.length ? drum[0] + drum.slice(1).map(pas).join("") : "";
  const norm = s => s.replace(/\s+/g, "").replace(/'/g, '"');
  const marime = v => Array.isArray(v) ? `${v.length} elemente` : `${Object.keys(v).length} ${Object.keys(v).length === 1 ? "cheie" : "chei"}`;
  const compus = v => v !== null && typeof v === "object" && !eF(v);

  gazda.innerHTML = `${d.prima ? `<div class="cale__prima">
        <p class="cale__pt"><b>1.</b> ${d.prima.t || "Prima privire asupra datelor"}</p>
        <div class="jpy__celula"><span class="jc__in">In [1]:</span><pre>${esc(d.prima.celula || "")}</pre></div>
        <div class="jc"></div>
      </div>
      <p class="cale__pt cale__pt--2"><b>2.</b> ${d.prima.t2 || "Drumul până la valoare"}</p>` : ""}
    <div class="cale${d.prima ? " cale--blocat" : ""}">
      <p class="cale__sarc"></p>
      <div class="cale__expr"><code></code><span class="cale__tip"></span></div>
      <p class="cale__regula"></p>
      <div class="cale__nivel"></div>
      <div class="cale__nav"><button type="button" data-rol="sus" class="btn btn--mic">Un nivel mai sus</button></div>
    </div>`;
  const $ = s => gazda.querySelector(s);
  /* prima privire: o comandă scrisă în consolă (de obicei .keys()) deschide drumul */
  if (d.prima){
    const envC = JSON.parse(JSON.stringify(ENV));
    consolaJupyter(gazda.querySelector(".cale__prima .jc"), envC, { start: 2, loc: d.prima.loc || "",
      laRulare: (src, rez) => { if (rez && !rez.atrib) $(".cale").classList.remove("cale--blocat"); } });
  }

  function deseneaza(mesaj){
    const tinta = T[k];
    $(".cale__sarc").innerHTML = tinta
      ? `<span>De găsit:</span> <b>${esc(tinta.t)}</b> <span class="cale__nr">${k + 1} din ${T.length}</span>`
      : `<span class="cale__gata">Toate cele ${T.length} valori au fost găsite.</span> Explorarea poate continua liber.`;
    const radacina = !drum.length;
    const v = radacina ? null : valoare();
    $(".cale__expr code").textContent = radacina ? "o variabilă, pentru început" : expr();
    $(".cale__expr code").classList.toggle("gol", radacina);
    $(".cale__tip").textContent = radacina ? "" : tip(v) + (compus(v) ? ` · ${marime(v)}` : "");
    $(".cale__regula").innerHTML = mesaj || (radacina ? "Variabilele din caiet; drumul pornește de la una dintre ele."
      : Array.isArray(v) ? "Valoarea curentă este o listă: următorul pas este o <b>poziție</b>, numerotată de la 0."
      : compus(v) ? "Valoarea curentă este un dicționar: următorul pas este o <b>cheie</b>."
      : "Aceasta este o valoare simplă.");
    let h;
    if (radacina){
      h = `<div class="cale__rs">${nume.map(x => `<button type="button" class="cale__r" data-p="${esc(x)}"><code class="cale__k">${esc(x)}</code><span class="cale__v">${esc(scurt(py(ENV[x])))}</span><span class="cale__t">${tip(ENV[x])}</span></button>`).join("")}</div>`;
    } else if (Array.isArray(v) && v.every(x => !compus(x)) && v.length <= 6){
      h = `<div class="cale__lista">${v.map((x, i) => `<button type="button" class="cale__cel" data-p="${i}"><span class="cale__i">${i}</span><code>${esc(py(x))}</code></button>`).join("")}</div>`;
    } else if (compus(v)){
      const chei = Array.isArray(v) ? v.map((_, i) => i) : Object.keys(v);
      /* multe chei: pe două coloane, ca nivelul să încapă pe ecran */
      const doua = chei.length > 4;
      h = `<div class="cale__rs${doua ? " cale__rs--2" : ""}">${chei.map(c => `<button type="button" class="cale__r" data-p="${esc(c)}"><code class="cale__k">${esc(pas(c))}</code><span class="cale__v">${esc(scurt(py(v[c]), doua ? 26 : 44))}</span><span class="cale__t">${tip(v[c])}</span></button>`).join("")}</div>`;
    } else {
      h = `<div class="cale__val"><code>${esc(py(v))}</code></div>`;
    }
    $(".cale__nivel").innerHTML = h;
    $('[data-rol="sus"]').disabled = drum.length <= start.length;
  }

  $(".cale__nivel").addEventListener("click", e => {
    const b = e.target.closest("[data-p]"); if (!b || blocat) return;
    const v = drum.length ? valoare() : null;
    drum.push(drum.length && Array.isArray(v) ? +b.dataset.p : b.dataset.p);
    const tinta = T[k];
    if (tinta && norm(expr()) === norm(tinta.cale)){
      blocat = true;
      deseneaza(`<span class="cale__ok">✓ ${esc(tinta.t)}: <code>${esc(expr())}</code></span>`);
      setTimeout(() => { k++; drum = [...start]; blocat = false; deseneaza(); }, 1600);
      return;
    }
    deseneaza();
  });
  $('[data-rol="sus"]').addEventListener("click", () => { if (drum.length > start.length && !blocat){ drum.pop(); deseneaza(); } });
  deseneaza();
};



/* ===========================================================================
   ECHIPELE — alegerea echipelor, pe slide (C2). Studentul își alege echipa
   sau trimite o cerere; pe proiector, profesorul vede toate echipele, cu
   numele, plus pornirea și închiderea alegerii. Logica stă în echipe.js.
   =========================================================================== */
V.echipe = async (gazda) => {
  const R = "/data-science-workflows";
  try {
    const [E, A] = await Promise.all([import(`${R}/js/echipe.js?v=105`), import(`${R}/js/auth.js?v=105`)]);
    const p = await A.profil().catch(() => ({}));
    if (p.profesorReal) await E.echipeSlideProfesor(gazda);
    else await E.echipeStudent(gazda, { slide: true });
  } catch {
    gazda.innerHTML = `<p class="echp__gol">Alegerea echipelor nu este disponibilă acum.</p>`;
  }
};

export default V;


/* ===========================================================================
   RST2 — restaurantul, ca desen, cu patru situații. Sus restaurantul, jos
   API-ul, pe aceleași coloane. Fiecare pas aprinde coloanele implicate,
   mută bonul pe săgeată și spune, într-un rând, ce se întâmplă în fiecare.
   =========================================================================== */
V.rst2 = (gazda, d) => {
  const SC = d.scenarii || [];
  let s = 0, p = 0;
  gazda.innerHTML = `<div class="rst3">
      <div class="rst3__file" role="tablist"${SC.length < 2 ? " hidden" : ""}>${SC.map((x, i) => `<button type="button" data-s="${i}">${esc(x.t)}</button>`).join("")}</div>
      ${d.svg || ""}
      <div class="rst3__txt">
        <p><span>La restaurant</span><b class="rst3__sus"></b></p>
        <p><span>La un API</span><b class="rst3__jos"></b></p>
      </div>
      <div class="rst3__nav"><button type="button" data-p="-1" aria-label="Pasul anterior">‹</button>
        <span class="rst3__nr"></span><button type="button" data-p="1" aria-label="Pasul următor">›</button></div>
    </div>`;
  const svg = gazda.querySelector("svg"), bon = gazda.querySelector(".rst2__bon");
  const col = [...gazda.querySelectorAll(".rst2__col")];
  function arata(){
    const sc = SC[s], ps = sc.pasi[p];
    gazda.querySelectorAll(".rst3__file button").forEach((b, i) => b.classList.toggle("on", i === s));
    svg.classList.add("focus");
    col.forEach((g, i) => { g.classList.toggle("on", ps.col.includes(i)); g.classList.toggle("schimb", !!ps.schimb && i >= 3); });
    const x = +col[ps.la]?.dataset.x || 150;
    if (bon){ bon.setAttribute("cx", ps.intors ? 150 : x); bon.setAttribute("cy", ps.intors ? 172 : 156); bon.classList.toggle("intors", !!ps.intors); }
    svg.querySelector(".rst2__dus")?.classList.toggle("on", !ps.intors);
    svg.querySelector(".rst2__intors")?.classList.toggle("on", !!ps.intors);
    gazda.querySelector(".rst3__sus").textContent = ps.sus;
    gazda.querySelector(".rst3__jos").textContent = ps.jos;
    gazda.querySelector(".rst3__nr").textContent = `pasul ${p + 1} din ${sc.pasi.length}`;
    gazda.querySelector('[data-p="-1"]').disabled = p === 0;
    gazda.querySelector('[data-p="1"]').disabled = p === sc.pasi.length - 1;
  }
  gazda.querySelector(".rst3__file").addEventListener("click", e => { const b = e.target.closest("button"); if (b){ s = +b.dataset.s; p = 0; arata(); } });
  gazda.querySelector(".rst3__nav").addEventListener("click", e => { const b = e.target.closest("button"); if (b){ p = Math.max(0, Math.min(SC[s].pasi.length - 1, p + +b.dataset.p)); arata(); } });
  col.forEach((g, i) => g.addEventListener("click", () => {
    const k = SC[s].pasi.findIndex(x => x.col.includes(i)); if (k >= 0){ p = k; arata(); }
  }));
  arata();
};


/* ===========================================================================
   RMT — restaurantul ca poveste, pas cu pas. Scena (SVG) vine din c2.py:
   personajele sunt .rmt__st[data-st], săgețile .rmt__dus[data-dir], bonul
   .rmt__bon și felul .rmt__fel. Fiecare pas: ce personaje se aprind (st),
   unde e bonul (bon, x) sau felul (fel, x), ce săgeată (dir), și două rânduri
   de text: la restaurant și la un API.
   =========================================================================== */
V.rmt = (gazda, d) => {
  const P = d.pasi || [];
  let p = 0;
  gazda.innerHTML = `<div class="rmt-w">
      ${d.svg || ""}
      <div class="rst3__txt">
        <p><span>La restaurant</span><b class="rmt__sus"></b></p>
        <p><span>La un API</span><b class="rmt__jos"></b></p>
      </div>
      <div class="rst3__nav"><button type="button" data-p="-1" aria-label="Pasul anterior">‹</button>
        <span class="rmt__nr"></span><button type="button" data-p="1" aria-label="Pasul următor">›</button></div>
    </div>`;
  const svg = gazda.querySelector("svg");
  const st = [...gazda.querySelectorAll(".rmt__st")];
  const bon = gazda.querySelector(".rmt__bon"), fel = gazda.querySelector(".rmt__fel");
  const muta = (el, x, y) => { if (!el) return; el.style.opacity = x == null ? 0 : 1; if (x != null) el.style.transform = `translate(${x}px, ${y}px)`; };
  // locul de pornire: bonul la masă, felul în bucătărie (ascunse până la pasul lor)
  if (bon) bon.style.transform = "translate(130px, 203px)";
  if (fel) fel.style.transform = "translate(820px, 250px)";
  function arata(){
    const ps = P[p];
    svg.classList.add("focus");
    st.forEach(g => g.classList.toggle("on", ps.st.includes(+g.dataset.st)));
    svg.querySelectorAll(".rmt__dus").forEach(a => a.classList.toggle("on", a.dataset.dir === ps.dir));
    muta(bon, ps.bon, 203);
    muta(fel, ps.fel, 250);
    gazda.querySelector(".rmt__sus").textContent = ps.sus;
    gazda.querySelector(".rmt__jos").textContent = ps.jos;
    gazda.querySelector(".rmt__nr").textContent = `pasul ${p + 1} din ${P.length}`;
    gazda.querySelector('[data-p="-1"]').disabled = p === 0;
    gazda.querySelector('[data-p="1"]').disabled = p === P.length - 1;
  }
  gazda.querySelector(".rst3__nav").addEventListener("click", e => {
    const b = e.target.closest("button"); if (b){ p = Math.max(0, Math.min(P.length - 1, p + +b.dataset.p)); arata(); }
  });
  st.forEach(g => g.addEventListener("click", () => {
    const k = P.findIndex(x => x.st.includes(+g.dataset.st)); if (k >= 0){ p = k; arata(); }
  }));
  arata();
};


/* ===========================================================================
   TIPURI2 — tipurile de API ca arbore, după schema din prezentare: rădăcina,
   cinci ramuri, frunzele pe rând. La clic pe o frunză, fișa ei, într-un loc
   fix, sub arbore. Pornește cu REST ales.
   =========================================================================== */
V.tipuri2 = (gazda, d) => {
  const RM = d.ramuri || [];
  let [ri, fi] = d.ales || [0, 0];
  gazda.innerHTML = `<div class="tpa">
      <div class="tpa__arb">
        <span class="tpa__rad">API</span>
        <div class="tpa__ramuri">${RM.map((r, i) => `<div class="tpa__r" style="--c:var(--${r.c})">
          <span class="tpa__rn">${esc(r.t)}<small>${esc(r.q)}</small></span>
          <span class="tpa__fr">${r.frunze.map((f, j) => `<button type="button" data-r="${i}" data-f="${j}"${f.curs ? ' class="curs"' : ""}>${esc(f.n)}</button>`).join("")}</span>
        </div>`).join("")}</div>
      </div>
      <div class="tpa__fisa" aria-live="polite"></div>
    </div>`;
  function arata(i, j){
    ri = i; fi = j; const r = RM[i], f = r.frunze[j];
    gazda.querySelectorAll(".tpa__fr button").forEach(b => b.classList.toggle("on", +b.dataset.r === i && +b.dataset.f === j));
    const fs = gazda.querySelector(".tpa__fisa");
    fs.style.setProperty("--c", `var(--${r.c})`);
    fs.innerHTML = `<h5>${esc(f.n)}<small>${esc(r.t)}${f.curs ? " · folosit la curs" : ""}</small></h5>
      <dl><div><dt>Ce este</dt><dd>${f.ce}</dd></div><div><dt>Un exemplu</dt><dd>${f.ex}</dd></div>
      <div><dt>Pentru analiza datelor</dt><dd>${f.da}</dd></div></dl>`;
  }
  gazda.querySelector(".tpa__ramuri").addEventListener("click", e => { const b = e.target.closest("button"); if (b) arata(+b.dataset.r, +b.dataset.f); });
  arata(ri, fi);
};


/* Cubul, varianta de pe slide: grila 3 × 3 și, sub ea, același conținut pe un
   singur rând, cum stă în "value". La clic pe o celulă se aprinde poziția ei. */
function cubSimplu(gazda, d){
  const R = d.randuri, K = d.coloane, VAL = d.valori || [], n = K.coduri.length;
  const fmt = v => Number(v).toLocaleString("ro-RO");
  let [ri, ci] = d.ales || [0, 0];
  gazda.innerHTML = `<div class="cb2${d.culori ? " cb2--culori" : ""}">
      <div class="cb2__sus">
        <table class="cb2__g"><thead><tr><th></th>${K.coduri.map((c, j) => `<th class="k" data-j="${j}">${c}<small>${esc(K.nume[j])}</small></th>`).join("")}</tr></thead>
          <tbody>${R.coduri.map((c, i) => `<tr class="r${i}"><th class="r" data-i="${i}">${c}<small>${esc(R.nume[i])}</small></th>
            ${K.coduri.map((_, j) => `<td><button type="button" data-i="${i}" data-j="${j}">${fmt(VAL[i * n + j])}</button></td>`).join("")}</tr>`).join("")}</tbody></table>
        ${d.nota ? `<div class="cb2__nota">${d.nota}</div>` : `<div class="cb2__ind">
          <p><span class="r">${esc(R.id)}</span>${R.coduri.map((c, i) => `<i data-ri="${i}">${c} <b>${i}</b></i>`).join("")}</p>
          <p><span class="k">${esc(K.id)}</span>${K.coduri.map((c, j) => `<i data-kj="${j}">${c} <b>${j}</b></i>`).join("")}</p>
          <p class="cb2__calc"></p>
        </div>`}
      </div>
      <p class="cb2__et">${esc(d.et || '"value", pe un singur rând')}</p>
      <div class="cb2__val">${VAL.map((v, p) => `<span data-p="${p}" class="r${Math.floor(p / n)}${p % n === 0 && p ? " nou" : ""}"><i>${p}</i>${fmt(v)}</span>`).join("")}</div>
    </div>`;
  function arata(i, j){
    ri = i; ci = j; const p = i * n + j;
    gazda.querySelectorAll(".cb2__g td button").forEach(b => b.classList.toggle("on", +b.dataset.i === i && +b.dataset.j === j));
    gazda.querySelectorAll(".cb2__g th.r").forEach(t => t.classList.toggle("on", +t.dataset.i === i));
    gazda.querySelectorAll(".cb2__g th.k").forEach(t => t.classList.toggle("on", +t.dataset.j === j));
    gazda.querySelectorAll("[data-ri]").forEach(t => t.classList.toggle("on", +t.dataset.ri === i));
    gazda.querySelectorAll("[data-kj]").forEach(t => t.classList.toggle("on", +t.dataset.kj === j));
    gazda.querySelectorAll(".cb2__val span").forEach(t => t.classList.toggle("on", +t.dataset.p === p));
    const calc = gazda.querySelector(".cb2__calc");
    if (calc) calc.innerHTML = `poziția = <span class="r">${i}</span> × ${n} + <span class="k">${j}</span> = <b>${p}</b>`;
  }
  gazda.querySelector(".cb2__g").addEventListener("click", e => { const b = e.target.closest("td button"); if (b) arata(+b.dataset.i, +b.dataset.j); });
  arata(ri, ci);
}
