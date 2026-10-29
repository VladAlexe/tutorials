/* ===========================================================================
   Harta legăturilor sociale

   O componentă, folosită în două locuri: pagina Exploratorului și slide-urile
   lecțiilor (prin ix("harta", ...)). Alegi un loc, iar celelalte se colorează
   după SCI-ul cu el, raportat la mediana partenerilor lui. Pentru țări, și
   migrația (Eurostat) și reziduul modelului din lecția 7; pentru regiuni,
   și comunitățile din lecția 6.

   Trei niveluri: județe (NUTS3), regiuni (NUTS2), țări. Datele vin gata
   pregătite din notebook-urile cursului; la județe, SCI-ul fiecărui județ
   stă în fișierul lui și se încarcă doar când e ales.

   Harta e SVG simplu: contururile sunt deja proiectate (EPSG:3035, în km).
   =========================================================================== */

const DATE = "/data-science-workflows/date/";
const V = "?v=92";
const NS = "http://www.w3.org/2000/svg";

/* Categorii, nu trepte: aceleași culori ca harta comunităților din C6. */
const COMUNITATI = ["#1f77b4", "#aec7e8", "#ff7f0e", "#ffbb78", "#2ca02c", "#98df8a", "#d62728",
  "#ff9896", "#9467bd", "#c5b0d5", "#8c564b", "#c49c94", "#e377c2", "#f7b6d2", "#7570b3", "#e7298a",
  "#66a61e", "#e6ab02"];

const NIVELURI = { judete: "Județe", regiuni: "Regiuni", tari: "Țări" };
const MASURI = {
  judete: [["sci", "Legături"]],
  regiuni: [["sci", "Legături"], ["com", "Comunități"]],
  tari: [["sci", "Legături"], ["migr", "Migranți"], ["model", "Față de model"]],
};
/* paleta e în explorator.css: nouă trepte pentru mărime, șapte divergente */
const SECV = [1, 2, 3, 4, 5, 6, 7, 8, 9].map(k => `var(--hs-${k})`);
const DIVERG = [1, 2, 3, 4, 5, 6, 7].map(k => `var(--hsd-${k})`);
const PRAG = {
  sci:   { v: [0.25, 0.5, 1, 2, 4, 8, 20, 50], et: ["¼×", "½×", "1×", "2×", "4×", "8×", "20×", "50×"] },
  migr:  { v: [500, 2000, 5000, 20000, 50000, 100000, 300000, 700000],
           et: ["", "2 mii", "", "20 mii", "", "100 mii", "", "700 mii"] },
  model: { v: [0.4, 0.6, 0.85, 1.18, 1.67, 2.5], et: ["0,4×", "0,6×", "0,85×", "1,2×", "1,7×", "2,5×"] },
};
const FARA = "var(--crom-2)";

const fmt = (x, z = 0) => x.toLocaleString("ro-RO", { maximumFractionDigits: z, minimumFractionDigits: z });
const treapta = (x, praguri) => { let k = 0; while (k < praguri.length && x >= praguri[k]) k++; return k; };

/* datele comune, încărcate o singură dată pe pagină */
let baza = null, judete = null;
const sci3 = new Map();
const json = async (f) => (await fetch(DATE + f + V)).json();
const incarcaBaza = () => baza || (baza = json("explorator.json"));
const incarcaJudete = () => judete || (judete = json("harta/judete.json"));
async function randJudet(cod){
  if (!sci3.has(cod)) sci3.set(cod, json(`harta/sci3/${cod}.json`));
  return sci3.get(cod);
}

export async function monteaza(gazda, opt = {}){
  const niveluri = opt.niveluri || ["judete", "regiuni", "tari"];
  const povesti = opt.povesti || [];
  /* o lecție poate arăta doar măsurile pe care le-a predat deja */
  const masuri = n => MASURI[n].filter(([m]) => !opt.masuri || opt.masuri.includes(m));
  let st = { nivel: opt.nivel || niveluri[0], masura: opt.masura || "sci", ales: opt.ales || "RO113", poveste: null };

  gazda.classList.add("hs");
  if (opt.slide) gazda.classList.add("hs--slide");
  gazda.innerHTML = `
    <div class="hs__harta">
      <svg role="img" aria-label="Harta Europei"></svg>
      <div class="hs__zoom">
        <button type="button" data-z="1.4" aria-label="Apropie">+</button>
        <button type="button" data-z="0.71" aria-label="Depărtează">−</button>
        <button type="button" data-z="0" aria-label="Toată harta">⟲</button>
        <button type="button" data-rol="linii" class="on" aria-label="Arată legăturile ca linii" title="Linii spre partenerii cu cele mai puternice legături">⌒</button>
        <button type="button" data-rol="mare" aria-label="Deschide harta mare" title="Harta pe tot ecranul (Esc pentru închidere)">⤢</button>
      </div>
      <div class="hs__balon" hidden></div>
      <p class="hs__incarc">Se încarcă harta…</p>
    </div>
    <aside class="hs__panou">
      ${opt.titlu ? `<h1 class="hs__titlu">${opt.titlu}</h1>` : ""}
      ${opt.sub ? `<p class="hs__sub">${opt.sub}</p>` : ""}
      <div class="hs__grup">
        ${niveluri.length > 1 ? `<div class="hs__seg" data-rol="nivel">${niveluri.map(n =>
          `<button type="button" data-v="${n}">${NIVELURI[n]}</button>`).join("")}</div>` : ""}
        <div class="hs__seg" data-rol="masura"></div>
      </div>
      ${povesti.length ? `<div class="hs__grup">
        <span class="hs__et">Cazuri din date</span>
        <div class="hs__povesti">${povesti.map((p, i) => `<button type="button" data-i="${i}">${p.t}</button>`).join("")}</div>
        <p class="hs__poveste" hidden></p></div>` : ""}
      <label class="hs__cauta"><span class="hs__et">Caută un loc</span>
        <input type="search" list="hs-l-${Math.random().toString(36).slice(2, 8)}" placeholder="Cluj, Napoli, Bavaria…" autocomplete="off">
        <datalist></datalist></label>
      <div class="hs__ales">
        <span class="hs__et" data-rol="ales-et"></span>
        <div class="hs__nume"></div>
        <div class="hs__meta"></div>
      </div>
      <div data-rol="legenda"></div>
      <div class="hs__grup"><ul class="hs__lista"></ul></div>
      <p class="hs__note"></p>
    </aside>`;
  const $ = (s) => gazda.querySelector(s);
  const svg = $("svg");
  const cautare = $(".hs__cauta input"), dl = $(".hs__cauta datalist");
  dl.id = cautare.getAttribute("list");
  let linii = !opt.faraLinii, centre = [];

  const B = await incarcaBaza();
  let J = null;
  const cutie = B.cutie.slice();
  let vb = cutie.slice();
  let rand = null;   // SCI-ul locului ales cu toate celelalte, la nivelul curent

  /* --- starea în adresă, doar pe pagina Exploratorului ---------------- */
  if (opt.adresa){
    const [nivel, masura, ales] = location.hash.slice(1).split("-");
    if (niveluri.includes(nivel) && MASURI[nivel].some(([m]) => m === masura)) st = { nivel, masura, ales, poveste: null };
  }
  const scrieAdresa = () => { if (opt.adresa) history.replaceState(null, "", `#${st.nivel}-${st.masura}-${st.ales}`); };

  /* --- datele nivelului curent ---------------------------------------- */
  const locuri = () => st.nivel === "judete" ? J.judete : st.nivel === "regiuni" ? B.regiuni : B.tari;
  const numeTara = (cod) => (B.tari.find(t => t.cod === cod) || { nume: cod }).nume;
  const loc = (cod) => locuri().find(l => l.cod === cod);
  const tara = (l) => st.nivel === "tari" ? l.cod : l.tara;

  async function incarcaRand(){
    const L = locuri(), i = L.findIndex(l => l.cod === st.ales);
    if (st.nivel === "judete") rand = await randJudet(st.ales);
    else rand = (st.nivel === "regiuni" ? B.sci_regiuni : B.sci_tari)[i];
  }
  function rapoarte(){
    const i = locuri().findIndex(l => l.cod === st.ales);
    const v = rand.filter((x, j) => j !== i && x > 0).sort((a, b) => a - b);
    const med = v[Math.floor(v.length / 2)];
    return rand.map((x, j) => (j === i || !x) ? null : x / med);
  }
  const rezidual = (cod) => { const k = [st.ales, cod].sort().join("-"); return k in B.model ? B.model[k] : null; };
  const migranti = (cod) => {
    if (!B.raportoare.includes(cod)) return undefined;
    return (B.migratie[st.ales] || {})[cod];
  };

  /* --- desenul ---------------------------------------------------------- */
  async function deseneaza(){
    if (st.nivel === "judete" && !J) J = await incarcaJudete();
    if (!loc(st.ales)){
      const dorita = st.taraDorita || "RO";
      st.ales = (locuri().find(l => tara(l) === dorita && l.d) || locuri().find(l => l.d)).cod;
    }
    svg.innerHTML = "";
    vb = cutie.slice();
    svg.setAttribute("viewBox", vb.join(" "));
    if (st.nivel !== "tari"){
      const cuDate = new Set(locuri().map(l => l.tara));
      for (const t of B.tari) if (!cuDate.has(t.cod) && t.d) svg.appendChild(cale(t.d, "fundal"));
    }
    locuri().forEach((l, i) => { if (l.d){ const p = cale(l.d, "zona"); p.dataset.i = i; svg.appendChild(p); } });
    /* centrul fiecărui loc, pentru liniile spre parteneri */
    /* din coordonatele conturului, nu din getBBox: harta poate fi încă ascunsă (alt slide) */
    centre = locuri().map(l => {
      if (!l.d) return null;
      const n = l.d.match(/-?\d+(?:\.\d+)?/g).map(Number);
      let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity;
      for (let k = 0; k + 1 < n.length; k += 2){ const x = n[k], y = n[k + 1];
        if (x < x0) x0 = x; if (x > x1) x1 = x; if (y < y0) y0 = y; if (y > y1) y1 = y; }
      return [(x0 + x1) / 2, (y0 + y1) / 2];
    });
    const g = document.createElementNS(NS, "g"); g.setAttribute("class", "arce"); svg.appendChild(g);
    dl.innerHTML = locuri().filter(l => l.d).map(l => `<option value="${l.nume}">${st.nivel === "tari" ? "" : numeTara(l.tara)}</option>`).join("");
    await actualizeaza();
  }
  function cale(d, cls){
    const p = document.createElementNS(NS, "path");
    p.setAttribute("d", d); p.setAttribute("class", cls);
    return p;
  }

  function culori(){
    const L = locuri();
    if (st.masura === "com") return L.map(l => COMUNITATI[l.com % COMUNITATI.length]);
    if (st.masura === "sci") return rapoarte().map(r => r === null ? FARA : SECV[treapta(r, PRAG.sci.v)]);
    if (st.masura === "migr") return L.map(l => { const m = migranti(l.cod);
      return m === undefined ? FARA : SECV[treapta(m, PRAG.migr.v)]; });
    return L.map(l => { const r = rezidual(l.cod); return r === null ? FARA : DIVERG[treapta(Math.exp(r), PRAG.model.v)]; });
  }

  async function actualizeaza(){
    await incarcaRand();
    const L = locuri(), c = culori();
    for (const p of svg.querySelectorAll(".zona")){
      const i = +p.dataset.i, e = L[i].cod === st.ales;
      p.style.fill = e && st.masura !== "com" ? "var(--panza)" : c[i];
      p.classList.toggle("ales", e);
      if (e) svg.insertBefore(p, svg.querySelector(".arce"));
    }
    arce();
    panou();
    scrieAdresa();
  }

  /* --- liniile spre cei mai legați parteneri ------------------------------
     Arce, nu drumuri: unesc centrele. Grosimea crește cu legătura. */
  function arce(){
    const g = svg.querySelector(".arce"); if (!g) return;
    g.innerHTML = "";
    if (!linii || st.masura === "com") return;
    const L = locuri(), i0 = L.findIndex(l => l.cod === st.ales), c0 = centre[i0];
    if (!c0) return;
    let top;
    /* la județe și regiuni, vecinii din aceeași țară ar fi doar un ghem în jurul locului ales:
       liniile merg spre partenerii din alte țări, adică spre diaspora */
    const taraAles = tara(L[i0]);
    if (st.masura === "sci") top = rapoarte().map((r, j) => [r, j])
      .filter(([r, j]) => r !== null && centre[j] && (st.nivel === "tari" || L[j].tara !== taraAles))
      .sort((a, b) => b[0] - a[0]).slice(0, 8);
    else if (st.masura === "migr") top = L.map((l, j) => [migranti(l.cod), j]).filter(([v, j]) => v && centre[j]).sort((a, b) => b[0] - a[0]).slice(0, 8);
    else top = L.map((l, j) => [rezidual(l.cod), j]).filter(([r, j]) => r !== null && centre[j]).sort((a, b) => b[0] - a[0]).slice(0, 6);
    if (!top.length) return;
    const max = top[0][0], min = top[top.length - 1][0];
    top.forEach(([v, j], k) => {
      const [x1, y1] = centre[j], [x0, y0] = c0, dx = x1 - x0, dy = y1 - y0, d = Math.hypot(dx, dy) || 1;
      const cx = (x0 + x1) / 2 - dy * 0.22, cy = (y0 + y1) / 2 + dx * 0.22;
      const p = document.createElementNS(NS, "path");
      p.setAttribute("d", `M${x0},${y0} Q${cx},${cy} ${x1},${y1}`);
      const t = max === min ? 1 : (v - min) / (max - min);
      p.setAttribute("class", "arc"); p.setAttribute("pathLength", "1");
      p.style.strokeWidth = (0.7 + 1.8 * t) * (vb[2] / 2600) + "";
      p.style.animationDelay = (k * 60) + "ms";
      p.dataset.i = j;
      g.appendChild(p);
      const pt = document.createElementNS(NS, "circle");
      pt.setAttribute("cx", x1); pt.setAttribute("cy", y1); pt.setAttribute("r", (1.4 + 1.4 * t) * (vb[2] / 2600));
      pt.setAttribute("class", "arc__cap"); pt.style.animationDelay = (k * 60 + 300) + "ms";
      g.appendChild(pt);
    });
  }

  /* --- panoul ----------------------------------------------------------- */
  function panou(){
    gazda.querySelectorAll('[data-rol="nivel"] button').forEach(b => b.classList.toggle("on", b.dataset.v === st.nivel));
    const seg = $('[data-rol="masura"]');
    const ms = masuri(st.nivel);
    seg.hidden = ms.length < 2;
    seg.innerHTML = ms.map(([v, t]) => `<button type="button" data-v="${v}" class="${v === st.masura ? "on" : ""}">${t}</button>`).join("");
    gazda.querySelectorAll(".hs__povesti button").forEach(b => b.classList.toggle("on", +b.dataset.i === st.poveste));
    const pv = $(".hs__poveste");
    if (pv){ pv.hidden = st.poveste === null; if (st.poveste !== null) pv.textContent = povesti[st.poveste].text; }

    const l = loc(st.ales);
    $('[data-rol="ales-et"]').textContent = { judete: "Județul ales", regiuni: "Regiunea aleasă", tari: "Țara aleasă" }[st.nivel];
    $(".hs__nume").textContent = l.nume;
    $(".hs__meta").textContent = st.nivel === "tari" ? l.cod : `${l.cod} · ${numeTara(l.tara)}`;
    legenda();
    lista();
    $(".hs__note").textContent = (st.nivel === "tari"
      ? "Pentru migrație raportează doar 24 de țări; lipsesc, între altele, Polonia, Danemarca, Grecia, Croația, Cipru, Malta, Elveția, Regatul Unit și cele mai multe țări din afara UE. "
      : "Regiunile ultraperiferice (Canare, Azore, Madeira, teritoriile franceze de peste mări) sunt incluse în date, dar nu sunt afișate pe hartă. ")
      + B.surse;
  }

  function legenda(){
    const scara = (et, trepte, praguri, fara) => `
      <div class="gf__leg"><div class="gf__scara">
        <span class="gf__scara-et">${et}</span>
        <div class="gf__trepte">${trepte.map((c, k) => `<span data-k="${k}" style="background:${c}" title="Treci cu mouse-ul pentru a evidenția doar locurile din această treaptă"></span>`).join("")}</div>
        <div class="gf__praguri">${praguri.map(p => `<span>${p}</span>`).join("")}<span></span></div>
      </div></div><div class="hs__fara"><i></i>${fara}</div>`;
    $('[data-rol="legenda"]').innerHTML =
      st.masura === "sci" ? scara("Probabilitatea de prietenie, față de mediana partenerilor", SECV, PRAG.sci.et, "fără date")
      : st.masura === "migr" ? scara("Cetățeni ai țării alese care trăiesc acolo", SECV, PRAG.migr.et, "țara nu raportează cetățeniile")
      : st.masura === "model" ? scara("SCI observat, raportat la valoarea prezisă de model", DIVERG, PRAG.model.et, "perechea nu este în model (lipsesc datele de migrație)")
      : `<div class="hs__fara">Fiecare culoare reprezintă un grup de regiuni mai legate între ele decât cu restul. Culorile sunt doar etichete.</div>`;
  }

  function lista(){
    const L = locuri(), taraAles = tara(loc(st.ales));
    let h = [], nr = 0;
    const sep = (t) => { h.push(`<li class="sep">${t}</li>`); nr = 0; };
    /* fiecare rând are bara lui: lista se citește ca un grafic, nu ca un tabel */
    const rnd = (j, val, w) => h.push(`<li data-cod="${L[j].cod}"${w != null ? ` class="cu-bara" style="--w:${Math.max(3, Math.round(w * 100))}%"` : ""}><span class="nr">${++nr}</span><span>${L[j].nume}</span><span class="val">${val}</span></li>`);
    const ori = (r) => `${fmt(r, r < 10 ? 1 : 0)}×`;

    if (st.masura === "sci"){
      const R = rapoarte().map((r, j) => [r, j]).filter(([r]) => r !== null).sort((a, b) => b[0] - a[0]);
      if (st.nivel === "tari"){ sep("Partenerii cei mai legați"); const mx = R[0]?.[0] || 1; R.slice(0, 8).forEach(([r, j]) => rnd(j, ori(r), r / mx)); }
      else {
        sep("Cei mai legați, în aceeași țară");
        R.filter(([, j]) => L[j].tara === taraAles).slice(0, 3).forEach(([r, j]) => rnd(j, ori(r)));
        sep("Cei mai legați, din alte țări");
        R.filter(([, j]) => L[j].tara !== taraAles).slice(0, 5).forEach(([r, j]) => rnd(j, ori(r)));
      }
    } else if (st.masura === "migr"){
      sep("Țările cu cei mai mulți cetățeni ai țării alese");
      const R = L.map((l, j) => [migranti(l.cod), j]).filter(([v]) => v).sort((a, b) => b[0] - a[0]).slice(0, 8);
      const mx = R[0]?.[0] || 1; R.forEach(([v, j]) => rnd(j, fmt(v), v / mx));
      if (!R.length) sep("nu există date pentru această cetățenie");
    } else if (st.masura === "model"){
      const R = L.map((l, j) => [rezidual(l.cod), j]).filter(([r]) => r !== null).sort((a, b) => b[0] - a[0]);
      if (!R.length) sep("țara aleasă nu este în model");
      else {
        sep("Mai legate decât prezice modelul"); R.slice(0, 4).forEach(([r, j]) => rnd(j, `${fmt(Math.exp(r), 2)}×`));
        sep("Mai puțin legate"); R.slice(-4).reverse().forEach(([r, j]) => rnd(j, `${fmt(Math.exp(r), 2)}×`));
      }
    } else {
      sep("În aceeași comunitate");
      const com = loc(st.ales).com, numar = {};
      for (const l of L) if (l.com === com) numar[l.tara] = (numar[l.tara] || 0) + 1;
      Object.entries(numar).sort((a, b) => b[1] - a[1]).forEach(([t, n]) =>
        h.push(`<li data-cod="${L.find(l => l.tara === t).cod}"><span class="nr">${++nr}</span><span>${numeTara(t)}</span><span class="val">${n} ${n === 1 ? "regiune" : "regiuni"}</span></li>`));
    }
    $(".hs__lista").innerHTML = h.join("");
  }

  function alege(cod){ st.ales = cod; st.poveste = null; actualizeaza(); }

  /* treapta de sub mouse, în legendă: aprinde doar locurile din ea */
  gazda.addEventListener("pointerover", (e) => {
    const t = e.target.closest(".gf__trepte span[data-k]"); if (!t) return;
    const c = culori(), cul = (st.masura === "model" ? DIVERG : SECV)[+t.dataset.k];
    for (const p of svg.querySelectorAll(".zona")) p.classList.toggle("stins", c[+p.dataset.i] !== cul);
  });
  gazda.addEventListener("pointerout", (e) => {
    if (e.target.closest(".gf__trepte span[data-k]")) svg.querySelectorAll(".zona.stins").forEach(p => p.classList.remove("stins"));
  });
  /* căutarea: după nume, la nivelul curent */
  cautare.addEventListener("change", () => {
    const q = cautare.value.trim().toLowerCase(); if (!q) return;
    const fara = t => t.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
    const l = locuri().find(x => x.d && fara(x.nume) === fara(q)) || locuri().find(x => x.d && fara(x.nume).includes(fara(q)));
    if (l){ alege(l.cod); cautare.value = ""; cautare.blur(); }
  });
  /* harta mare: peste toată pagina, Esc o închide */
  function mare(da){
    gazda.classList.toggle("hs--mare", da);
    document.documentElement.classList.toggle("hs-deschis", da);
    const b = $('[data-rol="mare"]'); b.textContent = da ? "✕" : "⤢"; b.setAttribute("aria-label", da ? "Închide harta mare" : "Deschide harta mare");
    vb = cutie.slice(); pune(); arce();
  }
  document.addEventListener("keydown", (e) => { if (e.key === "Escape" && gazda.classList.contains("hs--mare")) mare(false); });

  /* --- evenimente ------------------------------------------------------- */
  gazda.addEventListener("click", (e) => {
    const b = e.target.closest("button");
    if (b && b.closest('[data-rol="nivel"]') && b.dataset.v !== st.nivel){
      const t = tara(loc(st.ales));
      st.nivel = b.dataset.v; st.masura = "sci"; st.poveste = null;
      st.ales = null; st.taraDorita = t;
      deseneaza();
    } else if (b && b.closest('[data-rol="masura"]')){
      st.masura = b.dataset.v; st.poveste = null; actualizeaza();
    } else if (b && b.closest(".hs__povesti")){
      const p = povesti[b.dataset.i], schimba = p.nivel !== st.nivel;
      st = { nivel: p.nivel, masura: p.masura, ales: p.ales, poveste: +b.dataset.i };
      schimba ? deseneaza() : actualizeaza();
    }
    const li = e.target.closest(".hs__lista li[data-cod]");
    if (li) alege(li.dataset.cod);
  });
  svg.addEventListener("click", (e) => {
    const i = e.target.dataset && e.target.dataset.i;
    if (i !== undefined && svg.dataset.trasa !== "1") alege(locuri()[i].cod);
  });
  svg.addEventListener("pointermove", (e) => balon(e));
  svg.addEventListener("pointerleave", () => { $(".hs__balon").hidden = true; });

  function balon(e){
    const b = $(".hs__balon"), i = e.target.dataset && e.target.dataset.i;
    if (i === undefined || !rand){ b.hidden = true; return; }
    const l = locuri()[i];
    let val;
    if (l.cod === st.ales) val = "locul ales";
    else if (st.masura === "sci"){ const r = rapoarte()[i]; val = r === null ? "fără date" : `${fmt(r, r < 10 ? 1 : 0)}× mediana`; }
    else if (st.masura === "migr"){ const m = migranti(l.cod); val = !B.raportoare.includes(l.cod) ? "nu raportează" : m === undefined ? "fără date" : `${fmt(m)} cetățeni`; }
    else if (st.masura === "model"){ const r = rezidual(l.cod); val = r === null ? "nu este în model" : `${fmt(Math.exp(r), 2)}× valoarea prezisă`; }
    else val = `comunitatea ${l.com}`;
    b.innerHTML = `<b>${l.nume}</b><span>${st.nivel === "tari" ? "" : numeTara(l.tara) + " · "}${val}</span>`;
    const z = b.parentNode.getBoundingClientRect();
    b.style.left = Math.min(e.clientX - z.left + 14, z.width - 250) + "px";
    b.style.top = Math.min(e.clientY - z.top + 14, z.height - 60) + "px";
    b.hidden = false;
  }

  /* apropiere cu rotița și tragere cu mouse-ul */
  const pune = () => svg.setAttribute("viewBox", vb.join(" "));
  const punct = (e) => {
    const r = svg.getBoundingClientRect(), s = Math.max(vb[2] / r.width, vb[3] / r.height);
    return [vb[0] + vb[2] / 2 + (e.clientX - r.left - r.width / 2) * s, vb[1] + vb[3] / 2 + (e.clientY - r.top - r.height / 2) * s, s];
  };
  const scala = (f, cx, cy) => {
    const w = Math.min(cutie[2], Math.max(200, vb[2] / f)), k = w / vb[2];
    vb = [cx - (cx - vb[0]) * k, cy - (cy - vb[1]) * k, w, vb[3] * k]; pune();
    clearTimeout(scala.t); scala.t = setTimeout(arce, 120);
  };
  svg.addEventListener("wheel", (e) => { e.preventDefault(); const [x, y] = punct(e); scala(e.deltaY < 0 ? 1.25 : 0.8, x, y); }, { passive: false });
  let start = null;
  svg.addEventListener("pointerdown", (e) => { start = [e.clientX, e.clientY, vb[0], vb[1]]; svg.dataset.trasa = "0"; });
  svg.addEventListener("pointermove", (e) => {
    if (!start) return;
    const [, , s] = punct(e), dx = e.clientX - start[0], dy = e.clientY - start[1];
    if (Math.abs(dx) + Math.abs(dy) > 4){ svg.dataset.trasa = "1"; svg.classList.add("trage"); }
    vb[0] = start[2] - dx * s; vb[1] = start[3] - dy * s; pune();
  });
  const opreste = () => { start = null; svg.classList.remove("trage"); setTimeout(() => { svg.dataset.trasa = "0"; }, 0); };
  svg.addEventListener("pointerup", opreste);
  svg.addEventListener("pointerleave", opreste);
  $(".hs__zoom").addEventListener("click", (e) => {
    const r = e.target.closest("button")?.dataset.rol;
    if (r === "mare") return mare(!gazda.classList.contains("hs--mare"));
    if (r === "linii"){ linii = !linii; e.target.classList.toggle("on", linii); return arce(); }
    const z = e.target.dataset.z; if (z === undefined) return;
    if (+z === 0){ vb = cutie.slice(); pune(); } else scala(+z, vb[0] + vb[2] / 2, vb[1] + vb[3] / 2);
  });

  await deseneaza();
  $(".hs__incarc").remove();
}

/* În lecții: ix("harta", titlu, {nivel, masura, ales, niveluri, povesti}) */
export default { harta: (gazda, date) => monteaza(gazda, { ...date, slide: true }) };
