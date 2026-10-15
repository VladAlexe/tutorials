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
    const m = await import("/data-science-workflows/js/colectare.js?v=29");
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
        <span class="imb__pct imb__pct--ab"></span>cheie în amândouă
        <span class="imb__pct imb__pct--un"></span>cheie într-unul singur
      </p>
      <div class="imb__fel">
        ${FELURI.map(f => `<button class="imb__b" data-f="${f}" type="button">${
          f === "concat" ? "pd.concat" : `how=&quot;${NUME[f]}&quot;`}</button>`).join("")}
      </div>
      <div class="imb__jos"><p class="imb__gol">Apasă pe un fel de îmbinare.</p></div>
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
      st.textContent = "Le-ai văzut pe toate. Înregistrat.";
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
              <option value="">alege tipul…</option>
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
    out.innerHTML = tot ? `<b>Tot corect.</b> ${d.laBine || ""}`
                        : `<b>${bune} din ${C.length}.</b> ${d.laRau || ""}`;
    btN.hidden = tot;
    if (!tot) return;
    btV.disabled = true;
    de.innerHTML = C.map(c => `<p><code>${esc(c.nume)}</code>
      <b>${esc(c.ok)}</b> ${c.de_ce || ""}</p>`).join("");
    de.classList.add("vazut");
    await poarta(gazda, d.id || "coloane", sel.map(s => s.value).join(","));
    st.textContent = "Rezolvare înregistrată.";
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
    d.p0 || "Tot răspunsul, așa cum vine.",
    d.p1 || "Lista dinăuntru: asta devine tabel.",
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
          <p class="dsf__gol">Încă nimic.</p>
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
    bt.textContent = pas === 0 ? (d.buton || "Arată-mi lista")
                   : pas === 1 ? "Fă tabelul"
                   : "Încă o dată";
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
    <button class="drm__e drm__e--${banda}" data-i="${esc(x.n)}"
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

        <button class="drm__fin" data-i="${esc(FIN.n)}" type="button">${esc(FIN.n)}</button>

        <button class="drm__baza" data-i="${esc(BAZA.n)}" type="button">
          <span class="drm__bt">${esc(BAZA.n)}</span>
          <span class="drm__bd">nu e o etapă, e depozitul</span>
        </button>

        <div class="drm__rand drm__rand--jos">${JOS.map((x, i) => chev(x, i + 4, "b")).join("")}</div>
        <span class="drm__banda drm__banda--jos">${esc(d.bandaJos || "Ingineria modelelor")}</span>
      </div>

      <p class="drm__leg">
        <span class="drm__lp"></span>drumul înainte
        <span class="drm__lp drm__lp--p"></span>întoarcerile, la fel de normale
      </p>
      <div class="drm__i"><h5>${esc(d.titlu || "Apasă pe o etapă")}</h5>
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
    info.innerHTML = `<h5>${esc(x.n)}${x.unde ? ` <small>${esc(x.unde)}</small>` : ""}</h5>
      <p>${x.d || ""}</p>`;
  });
};


/* ===========================================================================
   13. SEMESTRU — cele unsprezece teme, așezate pe cele opt ședințe

   O grilă de cartonașe răspunde la „ce teme sunt” și deloc la „când”. Aici
   ședințele sunt o linie, iar temele atârnă de ședința în care se fac: se
   vede dintr-o privire că primul curs duce două teme, că Git-ul vine înaintea
   API-urilor, și unde e aglomerat semestrul.
   =========================================================================== */

V.semestru = (gazda, d) => {
  const T = d.teme || [];
  const N = d.sedinte || 8;
  const pe = k => T.filter(t => t.c === k);

  gazda.innerHTML = `
    ${d.sarcina ? `<p class="ix__sarcina">${d.sarcina}</p>` : ""}
    <div class="sem">
      <div class="sem__linie">
        ${Array.from({ length: N }, (_, i) => {
          const k = i + 1, lista = pe(k);
          return `
          <div class="sem__c ${lista.length ? "" : "sem__c--gol"}">
            <span class="sem__cap">
              <i class="sem__pct"></i>
              <b>C${k}</b>
            </span>
            <div class="sem__teme">
              ${lista.map(t => `
                <button class="sem__t" data-n="${esc(t.n)}" type="button">
                  <span class="sem__tn">${String(T.indexOf(t) + 1).padStart(2, "0")}</span>
                  <span class="sem__tt">${esc(t.n)}</span>
                </button>`).join("")}
            </div>
          </div>`;
        }).join("")}
      </div>
      <div class="sem__i"><h5>${esc(d.titlu || "Apasă pe o temă")}</h5>
        <p>${d.intro || ""}</p></div>
    </div>`;

  const info = gazda.querySelector(".sem__i");
  gazda.querySelector(".sem__linie").addEventListener("click", ev => {
    const b = ev.target.closest(".sem__t");
    if (!b) return;
    gazda.querySelectorAll(".sem__t").forEach(x => x.classList.remove("on"));
    b.classList.add("on");
    const t = T.find(x => x.n === b.dataset.n);
    if (!t) return;
    info.innerHTML = `<h5>${esc(t.n)} <small>cursul ${t.c}</small></h5>
      <p>${t.d || ""}</p>`;
  });
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
      <p class="ana__i">${d.intro || "Apasă pe o parte ca s-o vezi aprinsă."}</p>
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
      st.textContent = "Le-ai văzut. Înregistrat.";
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


export default V;
