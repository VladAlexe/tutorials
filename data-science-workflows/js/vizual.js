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
    const m = await import("/data-science-workflows/js/colectare.js?v=15");
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
          <div class="flx__s" data-i="${i}">
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
      <div class="flx__i"><h5>${esc(d.titlu || "Apasă pe o stație")}</h5>
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
    stare.textContent = d.dus || "cererea pleacă";
    arata(0); sine[0].classList.add("atins");

    ceas = setInterval(() => {
      if (!inapoi){
        if (i >= S.length - 1){
          inapoi = true;
          stare.textContent = d.intors || "răspunsul se întoarce";
          return;
        }
        legi[i].classList.add("dus");
        i++; sine[i].classList.add("atins"); arata(i);
      } else {
        if (i <= 0){
          clearInterval(ceas);
          stare.textContent = d.gata || "gata, ai răspunsul";
          return;
        }
        i--; legi[i].classList.add("intors"); arata(i);
      }
    }, 820);
  };

  arata(0);
};


/* ===========================================================================
   2. CRONOLOGIE — o axă cu ani

   Lista de ani dintr-un tabel nu spune nimic despre ritm. O axă spune: se
   vede că între 1991 și 2000 s-a încercat de patru ori, și că de atunci s-a
   mai schimbat de două ori.
   =========================================================================== */

V.cronologie = (gazda, d) => {
  const P = (d.puncte || []).slice().sort((a, b) => a.an - b.an);
  if (!P.length) return;
  const a0 = P[0].an, a1 = P[P.length - 1].an, lat = Math.max(1, a1 - a0);
  /* nu de la 0 la 100: primul și ultimul punct ar fi tăiate pe jumătate de
     marginea casetei, iar anul lor n-ar mai încăpea întreg */
  const MARG = 7;
  const poz = p => MARG + ((p.an - a0) / lat) * (100 - 2 * MARG);

  gazda.innerHTML = `
    ${d.sarcina ? `<p class="ix__sarcina">${d.sarcina}</p>` : ""}
    <div class="crn">
      <div class="crn__axa">
        <span class="crn__linie"></span>
        ${P.map((p, i) => `
          <button class="crn__p ${i % 2 ? "jos" : "sus"}" data-i="${i}" type="button"
                  style="left:${poz(p)}%">
            <span class="crn__an">${p.an}</span>
            <span class="crn__nod"></span>
            <span class="crn__nume">${esc(p.nume)}</span>
          </button>`).join("")}
      </div>
      <div class="crn__i"><h5>${esc(d.titlu || "Apasă pe oricare")}</h5>
        <p>${d.intro || ""}</p></div>
    </div>`;

  const info = gazda.querySelector(".crn__i");
  gazda.addEventListener("click", e => {
    const b = e.target.closest(".crn__p");
    if (!b) return;
    gazda.querySelectorAll(".crn__p").forEach(x => x.classList.remove("on"));
    b.classList.add("on");
    const p = P[+b.dataset.i];
    info.innerHTML = `<h5>${p.an} · ${esc(p.nume)}${
      p.et ? ` <small>${esc(p.et)}</small>` : ""}</h5><p>${p.text || ""}</p>`;
  });
};


/* ===========================================================================
   3. RĂSPUNS — ce întoarce serverul

   Codurile de stare se învață prost dintr-un tabel și bine dintr-o cerere
   care eșuează sub ochii tăi. Alegi o situație, apeși trimite, vezi codul.
   =========================================================================== */

V.raspuns = (gazda, d) => {
  gazda.closest(".ix")?.classList.add("exc");
  const C = d.cazuri || [];
  const incercate = new Set();
  let ales = 0;

  gazda.innerHTML = `
    ${d.sarcina ? `<p class="ix__sarcina">${d.sarcina}</p>` : ""}
    <div class="rsp">
      <div class="rsp__cazuri">${C.map((c, i) =>
        `<button class="rsp__c ${i ? "" : "on"}" data-i="${i}" type="button">${esc(c.et)}</button>`).join("")}</div>
      <div class="rsp__bara">
        <span class="rsp__met">GET</span>
        <code class="rsp__url">${esc(C[0]?.url || "")}</code>
        <button class="btn btn--mic btn--tare" data-rol="trimite" type="button">Trimite</button>
      </div>
      <div class="rsp__out" hidden>
        <div class="rsp__cod"><b></b><span></span></div>
        <pre class="rsp__corp"></pre>
        <p class="rsp__ce"></p>
      </div>
      <p class="rsp__nr"></p>
      <p class="ex__stare"></p>
    </div>`;

  const url  = gazda.querySelector(".rsp__url");
  const out  = gazda.querySelector(".rsp__out");
  const cod  = gazda.querySelector(".rsp__cod");
  const corp = gazda.querySelector(".rsp__corp");
  const ce   = gazda.querySelector(".rsp__ce");
  const nr   = gazda.querySelector(".rsp__nr");
  const st   = gazda.querySelector(".ex__stare");

  const numara = () => {
    nr.textContent = `${incercate.size} din ${C.length} încercate`;
    nr.classList.toggle("gata", incercate.size >= C.length);
  };

  gazda.addEventListener("click", e => {
    const b = e.target.closest(".rsp__c");
    if (!b) return;
    gazda.querySelectorAll(".rsp__c").forEach(x => x.classList.toggle("on", x === b));
    ales = +b.dataset.i;
    url.textContent = C[ales].url || "";
    out.hidden = true;
  });

  gazda.querySelector('[data-rol="trimite"]').onclick = async () => {
    const c = C[ales];
    out.hidden = false;
    const fel = c.cod < 300 ? "ok" : c.cod < 500 ? "tu" : "ei";
    cod.className = "rsp__cod rsp__cod--" + fel;
    cod.querySelector("b").textContent = c.cod;
    cod.querySelector("span").textContent = c.nume || "";
    corp.textContent = c.corp || "";
    ce.innerHTML = c.ce || "";
    incercate.add(ales);
    numara();
    if (incercate.size >= C.length){
      const salvat = await poarta(gazda, d.id, [...incercate].join(","));
      st.textContent = "Le-ai încercat pe toate.";
      st.classList.add("vazut");
    }
  };

  numara();
};


/* ===========================================================================
   4. ZONE — cele trei zone ale lui Git

   Modelul mental fără de care comenzile lui Git se învață pe de rost. Aici nu
   se citește, se mută: apeși comanda și vezi unde ajung fișierele.
   =========================================================================== */

V.zone = (gazda, d) => {
  gazda.closest(".ix")?.classList.add("exc");
  const ZONE = [
    { t: "Dosarul de lucru", d: "aici editezi" },
    { t: "Pregătire", d: "ce intră în commit" },
    { t: "Istoric local", d: "commit-urile tale" },
    { t: "GitHub", d: "copia de pe internet" },
  ];
  const COM = [
    { c: "git status", z: null, d: "nu mută nimic; spune unde ești" },
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
      msg.textContent = `${c.c}: n-are ce muta. În „${ZONE[c.z - 1].t}” nu e nimic.`;
      return;
    }
    muta.forEach(f => f.z = c.z);
    msg.textContent = `${c.c}: ${muta.length} ${muta.length === 1 ? "fișier" : "fișiere"} → ${ZONE[c.z].t}.`;
    deseneaza();

    if (F.every(f => f.z === 3)){
      msg.textContent = "Toate au ajuns pe GitHub. Ăsta e drumul, de fiecare dată.";
      await poarta(gazda, d.id, jurnal.join(" → "));
      st.textContent = "Rezolvare înregistrată.";
      st.classList.add("vazut");
    }
  });

  deseneaza();
};


/* ===========================================================================
   5. RAMURI — graful care crește sub ochii tăi

   O ramură e greu de explicat în cuvinte și evidentă într-un desen. Aici se
   desenează pe măsură ce apeși.
   =========================================================================== */

V.ramuri = (gazda, d) => {
  gazda.closest(".ix")?.classList.add("exc");
  let main = 2, ram = 0, peRamura = false, unit = 0, nodRam = null;
  /* main: câte commit-uri pe main; ram: câte pe ramură; unit: s-a îmbinat */

  gazda.innerHTML = `
    ${d.sarcina ? `<p class="ix__sarcina">${d.sarcina}</p>` : ""}
    <div class="rm">
      <div class="rm__desen"></div>
      <div class="rm__com">
        <button class="zn__cb" data-a="commit" type="button">commit</button>
        <button class="zn__cb" data-a="ramura" type="button">git switch -c curatare</button>
        <button class="zn__cb" data-a="main" type="button">git switch main</button>
        <button class="zn__cb" data-a="merge" type="button">git merge curatare</button>
        <button class="zn__cb zn__cb--rau" data-a="reset" type="button">de la capăt</button>
      </div>
      <p class="rm__unde"></p>
      <p class="ex__stare"></p>
    </div>`;

  const desen = gazda.querySelector(".rm__desen");
  const unde  = gazda.querySelector(".rm__unde");
  const st    = gazda.querySelector(".ex__stare");

  function deseneaza(){
    const PAS = 54, R = 9, SUS = 34, JOS = 84;
    const n = main + (ram ? ram : 0) + (unit ? 1 : 0);
    const lat = Math.max(420, (main + ram + 2) * PAS);
    let p = [], linii = [];

    for (let i = 0; i < main; i++) p.push({ x: (i + 1) * PAS, y: JOS, t: "main" });
    for (let i = 1; i < main; i++)
      linii.push(`M${i * PAS} ${JOS} H${(i + 1) * PAS}`);

    const bif = nodRam === null ? null : nodRam;
    for (let i = 0; i < ram; i++){
      const x = (bif + i + 1) * PAS;
      p.push({ x, y: SUS, t: "ramura" });
      if (i === 0) linii.push(`M${bif * PAS} ${JOS} C${bif * PAS + 22} ${JOS} ${x - 22} ${SUS} ${x} ${SUS}`);
      else linii.push(`M${x - PAS} ${SUS} H${x}`);
    }
    if (unit){
      const x = (main) * PAS;
      p.push({ x, y: JOS, t: "unit" });
      linii.push(`M${(main - 1) * PAS} ${JOS} H${x}`);
      linii.push(`M${(bif + ram) * PAS} ${SUS} C${(bif + ram) * PAS + 22} ${SUS} ${x - 22} ${JOS} ${x} ${JOS}`);
    }

    desen.innerHTML = `
      <svg viewBox="0 0 ${lat} 120" width="100%" height="120" role="img"
           aria-label="graful ramurilor">
        <text x="6" y="${JOS + 4}" class="rm__et">main</text>
        ${ram ? `<text x="6" y="${SUS + 4}" class="rm__et rm__et--r">curatare</text>` : ""}
        ${linii.map(dd => `<path d="${dd}" class="rm__l"/>`).join("")}
        ${p.map(q => `<circle cx="${q.x}" cy="${q.y}" r="${R}" class="rm__n rm__n--${q.t}"/>`).join("")}
      </svg>`;
    unde.textContent = peRamura ? "ești pe ramura curatare" : "ești pe main";
  }

  gazda.addEventListener("click", async e => {
    const b = e.target.closest("[data-a]");
    if (!b) return;
    const a = b.dataset.a;
    if (a === "reset"){ main = 2; ram = 0; peRamura = false; unit = 0; nodRam = null; deseneaza(); return; }
    if (a === "commit"){
      if (peRamura) ram++; else main++;
    }
    if (a === "ramura"){
      if (unit){ return; }
      peRamura = true; if (nodRam === null) nodRam = main;
    }
    if (a === "main") peRamura = false;
    if (a === "merge"){
      if (!ram || peRamura){
        unde.textContent = ram ? "întâi git switch main" : "n-ai ce îmbina: ramura e goală";
        return;
      }
      unit = 1; main++;
      await poarta(gazda, d.id, `main:${main} ramura:${ram}`);
      st.textContent = "Ai dus o ramură până la capăt.";
      st.classList.add("vazut");
    }
    deseneaza();
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
        <button class="zn__cb" data-k="meu" type="button">păstrez ce am eu</button>
        <button class="zn__cb" data-k="lor" type="button">păstrez ce vine</button>
        <button class="zn__cb" data-k="ambele" type="button">le păstrez pe amândouă</button>
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
      ? "<b>Așa e.</b> Marcajele au dispărut, fișierul rulează din nou."
      : `<b>Merge, dar nu e ce trebuia.</b> ${d.deCe || ""}`;
    ex.classList.add("vazut");
    ex.innerHTML = d.explicatie || "";
    btV.disabled = true;
    gazda.querySelectorAll("[data-k]").forEach(x => x.disabled = true);
    await poarta(gazda, d.id, ales);
    st.textContent = "Rezolvare înregistrată.";
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
        ${X.map(x => `<span class="prg__p" data-v="${x.v}"
            style="left:${poz(x.v)}%" title="${esc(x.t)}: ${x.v}"></span>`).join("")}
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
          <button class="zn__cb" data-r="scot" type="button">Sunt greșeli, le scot</button>
          <button class="zn__cb" data-r="pastrez" type="button">Nu sunt greșeli, le păstrez</button>
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
      `<b>${peste.length}</b> din ${X.length} sunt peste el`;
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
      ? `<b>Da.</b> ${d.laBine || ""}`
      : `<b>Nu încă.</b> ${d.laRau || ""}`;
    out.classList.add("vazut");
    await poarta(gazda, d.id, `k=${k} raspuns=${raspuns}`);
    st.textContent = "Rezolvare înregistrată.";
    st.classList.add("vazut");
  });

  deseneaza();
};


export default V;
