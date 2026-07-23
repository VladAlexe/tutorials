const V = new URL(import.meta.url).searchParams.get("v") || "1";
const [
  { renderQuiz, renderVote },
  { renderNetwork, renderInteractive },
  {
    markSlidePosition,
    getSlidePosition,
    getProgress,
    getVote,
    markLessonStarted,
    markLessonCompleted,
    resetLessonProgress
  }
] = await Promise.all([
  import(`./quiz.js?v=${V}`),
  import(`./visualizations.js?v=${V}`),
  import(`./progress.js?v=${V}`)
]);

function makeSlideElement() {
  const el = document.createElement("section");
  el.className = "slide";
  el.hidden = true;
  el.tabIndex = -1;
  el.setAttribute("aria-hidden", "true");
  el.setAttribute("aria-roledescription", "diapozitiv");
  return el;
}

// --- placeholder substitution --------------------------------------------
// {{path.into.stats}}          -> resolved value (Romanian number formatting)
// {{name:topDegree}}           -> stats.topByDegree[0].name
// {{id:topTime}}               -> stats.topByWeighted[0].id
// {{value:topSpread}}          -> stats.spreadRanking.champions[0].value
// {{friendshipParadox.pctBelow}} -> stats.friendshipParadox.pctBelow
// Numbers formatted with Romanian comma decimal, 1 decimal (integers kept as-is).

const NAME_SHORTCUTS = {
  topDegree:   "topByDegree",
  topTime:     "topByWeighted",
  topSpread:   "spreadRanking.champions",
  seedFirst:   "majorityIllusion.seedNames",
  // Canonical role names, pinned by Phase 1 analysis (build_network.py ROLE_IDS).
  // Both bare and -ul suffix forms resolve so authors do not have to remember which.
  vedeta:      "sliceMetrics.characters.vedeta",
  campion:     "sliceMetrics.characters.campion",
  campionul:   "sliceMetrics.characters.campion",
  surpriza:    "sliceMetrics.characters.surpriza",
  puntea:      "sliceMetrics.characters.puntea",
  dependent:   "sliceMetrics.characters.dependent",
  dependentul: "sliceMetrics.characters.dependent",
  izolat:      "sliceMetrics.characters.izolat",
  izolatul:    "sliceMetrics.characters.izolat",
  // Legacy heuristic keys kept for backward-compat.
  discretul:   "sliceMetrics.characters.surpriza"
};


function formatValue(v) {
  if (typeof v === "number") {
    if (Number.isInteger(v)) return String(v);
    return v.toFixed(1).replace(".", ",");
  }
  return String(v);
}

function walkPath(obj, parts) {
  let val = obj;
  for (const p of parts) {
    if (val == null) return null;
    if (Array.isArray(val)) {
      const idx = Number(p);
      val = Number.isFinite(idx) ? val[idx] : val[p];
    } else {
      val = val[p];
    }
  }
  return val;
}

const FIELD_ALIASES = {
  degree:          "popularity",
  contacte:        "popularity",
  outClass:        "outClassContacts",
  contacteInAfara: "outClassContacts",
  raza:            "reach",
  rankReach:       "rankReach"
};

function resolveExpr(stats, expr) {
  if (!stats) return null;
  const trimmed = expr.trim();
  if (trimmed.includes(":")) {
    const [field, key] = trimmed.split(":").map((s) => s.trim());
    const actualField = FIELD_ALIASES[field] || field;
    const path = NAME_SHORTCUTS[key];
    if (!path) return null;
    const target = walkPath(stats, path.split("."));
    if (Array.isArray(target) && target[0] != null) {
      const first = target[0];
      return typeof first === "object" ? first[actualField] : first;
    }
    if (target && typeof target === "object") {
      return target[actualField];
    }
    return null;
  }
  const parts = trimmed.split(".");
  if (parts[0] === "stats") parts.shift();
  return walkPath(stats, parts);
}

function substituteText(text, stats) {
  if (typeof text !== "string" || !stats) return text;
  return text.replace(/\{\{([^}]+)\}\}/g, (m, expr) => {
    const v = resolveExpr(stats, expr);
    if (v == null) return m;
    return formatValue(v);
  });
}

const SUBST_FIELDS = [
  "title", "intro", "content", "description", "caption",
  "successText", "hint", "question", "explanation", "buttonLabel",
  "xLabel", "yLabel", "note", "citation",
  // mode-specific text fields the modes render themselves
  "textBefore", "textAfter", "task", "label"
];

function substituteBlock(block, stats) {
  if (!stats) return block;
  const clone = { ...block };
  for (const key of SUBST_FIELDS) {
    if (typeof clone[key] === "string") {
      clone[key] = substituteText(clone[key], stats);
    }
  }
  if (Array.isArray(clone.options)) {
    clone.options = clone.options.map((o) =>
      typeof o === "string" ? substituteText(o, stats) : o
    );
  }
  if (Array.isArray(clone.bars)) {
    clone.bars = clone.bars.map((b) => {
      if (b && typeof b === "object" && typeof b.label === "string") {
        return { ...b, label: substituteText(b.label, stats) };
      }
      return b;
    });
  }
  if (clone.preview && typeof clone.preview === "object") {
    const p = { ...clone.preview };
    if (typeof p.legend === "string") p.legend = substituteText(p.legend, stats);
    if (typeof p.caption === "string") p.caption = substituteText(p.caption, stats);
    clone.preview = p;
  }
  if (clone.notification && typeof clone.notification === "object") {
    const n = { ...clone.notification };
    for (const k of ["meta1", "body", "meta2"]) {
      if (typeof n[k] === "string") n[k] = substituteText(n[k], stats);
    }
    clone.notification = n;
  }
  if (Array.isArray(clone.questions)) {
    clone.questions = clone.questions.map((q) => {
      if (!q || typeof q !== "object") return q;
      const cq = { ...q };
      for (const k of ["question", "explanation"]) {
        if (typeof cq[k] === "string") cq[k] = substituteText(cq[k], stats);
      }
      if (Array.isArray(cq.options)) cq.options = cq.options.map((o) => typeof o === "string" ? substituteText(o, stats) : o);
      return cq;
    });
  }
  if (clone.reveal && typeof clone.reveal === "object") {
    const r = { ...clone.reveal };
    if (typeof r.text === "string") r.text = substituteText(r.text, stats);
    if (Array.isArray(r.bars)) {
      r.bars = r.bars.map((b) => (b && typeof b === "object" && typeof b.label === "string")
        ? { ...b, label: substituteText(b.label, stats) } : b);
    }
    if (r.messagesByOption && typeof r.messagesByOption === "object") {
      const mm = {};
      for (const [k, v] of Object.entries(r.messagesByOption)) {
        mm[k] = typeof v === "string" ? substituteText(v, stats) : v;
      }
      r.messagesByOption = mm;
    }
    clone.reveal = r;
  }
  // story-network mode carries per-step text and buttonLabel that only the mode
  // renderer sees; substitute them at author time so placeholders never leak.
  if (Array.isArray(clone.story)) {
    clone.story = clone.story.map((step) => {
      if (!step || typeof step !== "object") return step;
      const s = { ...step };
      if (typeof s.text === "string") s.text = substituteText(s.text, stats);
      if (typeof s.buttonLabel === "string") s.buttonLabel = substituteText(s.buttonLabel, stats);
      return s;
    });
  }
  // Every other array of objects with a text/label field: presets, states,
  // series (chart), highlight arrays that carry copy.
  if (Array.isArray(clone.presets)) {
    clone.presets = clone.presets.map((p) => {
      if (!p || typeof p !== "object") return p;
      const c = { ...p };
      if (typeof c.label === "string") c.label = substituteText(c.label, stats);
      return c;
    });
  }
  if (Array.isArray(clone.states)) {
    clone.states = clone.states.map((s) => {
      if (!s || typeof s !== "object") return s;
      const c = { ...s };
      if (typeof c.label === "string") c.label = substituteText(c.label, stats);
      return c;
    });
  }
  if (Array.isArray(clone.series)) {
    clone.series = clone.series.map((s) => {
      if (!s || typeof s !== "object") return s;
      const c = { ...s };
      if (typeof c.title === "string") c.title = substituteText(c.title, stats);
      return c;
    });
  }
  if (Array.isArray(clone.slots)) {
    // slots are role keys, not text; leave alone.
  }
  return clone;
}

async function loadStats(source) {
  if (!source) return null;
  try {
    const res = await fetch(source);
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

// Paradox block: 4-state guided card.
//  1) vote (required to unlock navigation)
//  2) reveal — real numbers from the school + tailored feedback
//  3) mechanism — a 10-spoke star network that makes the sampling bias obvious
//  4) application — Christakis-Fowler and acquaintance immunization
// Progression is by button; each next stage stays visible when the next one
// opens, so the card reads as a stacked narrative when scrolled back.
async function renderParadox(container, block, stats, opts) {
  const progressMod = await import(`./progress.js?v=${V}`);
  const { markVote } = progressMod;

  const p = stats?.sliceMetrics?.friendshipParadox || stats?.friendshipParadox || {};
  const meanDeg = p.meanDegree ?? 6;
  const meanFriendDeg = p.meanFriendDegree ?? 7.6;
  const pctBelow = p.pctBelow ?? 70;

  // Stage 1: vote
  const voteWrap = document.createElement("div");
  voteWrap.className = "paradox__vote vote";
  const q = document.createElement("p");
  q.className = "vote__question";
  q.textContent = block.question || "";
  voteWrap.appendChild(q);
  const optWrap = document.createElement("div");
  optWrap.className = "vote__options";
  voteWrap.appendChild(optWrap);

  const optBtns = [];
  (block.options || []).forEach((label, idx) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "btn btn--ghost vote__option";
    btn.textContent = label;
    btn.addEventListener("click", () => pick(idx));
    optWrap.appendChild(btn);
    optBtns.push(btn);
  });
  container.appendChild(voteWrap);

  // Stage 2 host, hidden initially
  const revealEl = document.createElement("div");
  revealEl.className = "paradox__reveal";
  revealEl.hidden = true;
  container.appendChild(revealEl);

  const mechEl = document.createElement("div");
  mechEl.className = "paradox__mechanism";
  mechEl.hidden = true;
  container.appendChild(mechEl);

  const appEl = document.createElement("div");
  appEl.className = "paradox__application";
  appEl.hidden = true;
  container.appendChild(appEl);

  function tailoredMsg(idx) {
    // Order: [0]="mai mulți", [1]="cam la fel", [2]="mai puțini"
    if (idx === 0) return "Ai votat împotriva intuiției comune, și ai avut dreptate. Dar probabil nu din motivul corect.";
    return "Ai votat ca majoritatea. Și, ca majoritatea, datele te contrazic.";
  }

  function fmtNumberRo(v) { return String(v).replace(".", ","); }

  function starSvg(centerCount = 10) {
    const W = 320, H = 220;
    const cx = W / 2, cyC = H / 2;
    const r = 82;
    const parts = [];
    // spokes
    for (let i = 0; i < centerCount; i++) {
      const angle = (i / centerCount) * 2 * Math.PI - Math.PI / 2;
      const px = cx + Math.cos(angle) * r;
      const py = cyC + Math.sin(angle) * r;
      parts.push(`<line x1="${cx}" y1="${cyC}" x2="${px.toFixed(1)}" y2="${py.toFixed(1)}" stroke="#8a7154" stroke-width="1.2" opacity="0.55"/>`);
    }
    // peripherals
    for (let i = 0; i < centerCount; i++) {
      const angle = (i / centerCount) * 2 * Math.PI - Math.PI / 2;
      const px = cx + Math.cos(angle) * r;
      const py = cyC + Math.sin(angle) * r;
      parts.push(`<circle cx="${px.toFixed(1)}" cy="${py.toFixed(1)}" r="9" fill="#3d7a52" stroke="#2a1f16" stroke-width="0.8"/>`);
      parts.push(`<text x="${px.toFixed(1)}" y="${(py + 3).toFixed(1)}" text-anchor="middle" font-size="9" fill="#faf7f2" font-family="Georgia, serif">1</text>`);
    }
    // center
    parts.push(`<circle cx="${cx}" cy="${cyC}" r="15" fill="#8b4a1e" stroke="#2a1f16" stroke-width="1"/>`);
    parts.push(`<text x="${cx}" y="${(cyC + 4).toFixed(1)}" text-anchor="middle" font-size="12" fill="#faf7f2" font-weight="500" font-family="Georgia, serif">10</text>`);
    return `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto;max-width:340px;display:block;margin:0 auto" role="img" aria-label="Rețea în stea: un nod central cu grad 10, zece noduri de margine cu grad 1">${parts.join("")}</svg>`;
  }

  function barsSvg() {
    const W = 440, H = 100;
    const padL = 44, padR = 60, padT = 8, padB = 8;
    const chartW = W - padL - padR;
    const rowH = 26, rowGap = 12;
    const maxV = Math.max(meanFriendDeg, meanDeg) * 1.15;
    function row(label, val, y, color) {
      const w = (val / maxV) * chartW;
      return `<text x="${padL - 6}" y="${(y + rowH / 2 + 4).toFixed(1)}" text-anchor="end" font-family="Georgia, serif" font-size="12" fill="#2a1f16">${label}</text>` +
             `<rect x="${padL}" y="${y.toFixed(1)}" width="${w.toFixed(1)}" height="${rowH}" fill="${color}" rx="2"/>` +
             `<text x="${(padL + w + 6).toFixed(1)}" y="${(y + rowH / 2 + 4).toFixed(1)}" font-family="Georgia, serif" font-size="13" font-weight="500" fill="#2a1f16">${fmtNumberRo(val)}</text>`;
    }
    const svg = `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto;max-width:520px;display:block;margin:0 auto">` +
      row("un elev", meanDeg, padT, "#8b4a1e") +
      row("prietenii lui", meanFriendDeg, padT + rowH + rowGap, "#3d7a52") +
      `</svg>`;
    return svg;
  }

  function openReveal(idx) {
    revealEl.hidden = false;
    revealEl.innerHTML =
      `<p class="paradox__msg">${tailoredMsg(idx)}</p>` +
      `<div class="paradox__bars">${barsSvg()}</div>` +
      `<p class="paradox__stat">În școala noastră, un elev are în medie <strong>${fmtNumberRo(meanDeg)}</strong> contacte. Prietenii unui elev au în medie <strong>${fmtNumberRo(meanFriendDeg)}</strong>.</p>` +
      `<p class="paradox__punch"><strong>${pctBelow}%</strong> dintre elevi au prietenii mai populari decât ei înșiși.</p>` +
      `<p class="paradox__note">Nu e o coincidență a acestei școli. Se întâmplă în aproape orice rețea socială, și are un nume: paradoxul prieteniei, descris de Scott Feld în 1991.</p>` +
      `<button type="button" class="btn btn--primary" data-next="mech">De ce se întâmplă?</button>`;
    revealEl.querySelector('[data-next="mech"]').addEventListener("click", openMech);
  }

  function openMech() {
    mechEl.hidden = false;
    mechEl.innerHTML =
      `<h3 class="paradox__section-title">Cazul extrem</h3>` +
      `<div class="paradox__star">${starSvg(10)}</div>` +
      `<p>Un elev are zece prieteni. Ceilalți zece au fiecare un singur prieten: pe el.</p>` +
      `<p>Întreabă pe fiecare câți prieteni are: zece oameni răspund <strong>unu</strong>, iar unul răspunde <strong>zece</strong>. Media e puțin peste unu.</p>` +
      `<p>Acum întreabă pe fiecare câți prieteni are prietenul lui. Cei zece răspund toți <strong>zece</strong>, pentru că toți au același prieten popular. Doar el răspunde unu.</p>` +
      `<p>Deci aproape toată lumea are un prieten mai popular decât ea, iar asta nu spune nimic despre ei. Spune ceva despre <strong>cum am numărat</strong>.</p>` +
      `<p>Motivul: cine are mulți prieteni apare în listele multor oameni. Cine are puțini apare aproape în nicio listă. Când te uiți la prietenii oamenilor, îi vezi disproporționat pe cei populari. Nu e psihologie, e <strong>eșantionare</strong>.</p>` +
      `<button type="button" class="btn btn--primary" data-next="app">La ce folosește?</button>`;
    mechEl.querySelector('[data-next="app"]').addEventListener("click", openApp);
    mechEl.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function openApp() {
    appEl.hidden = false;
    appEl.innerHTML =
      `<h3 class="paradox__section-title">La ce folosește</h3>` +
      `<p>Paradoxul nu e doar o ciudățenie. E o unealtă.</p>` +
      `<p>În 2010, <strong>Christakis și Fowler</strong> au urmărit o epidemie de gripă într-un campus universitar. Au format două grupuri: elevi aleși la întâmplare, și prieteni ai unor elevi aleși la întâmplare. Grupul de prieteni s-a îmbolnăvit cu aproape două săptămâni mai devreme, pentru că, prin paradox, ei erau mai bine plasați în rețea. Un sistem de avertizare timpurie, construit fără să știi rețeaua.</p>` +
      `<p>Și e chiar răspunsul la problema noastră, într-o formă practică.</p>` +
      `<p>Toată misiunea a presupus că știm întreaga rețea: cine cu cine, cât timp, totul. În realitate nu ai datele astea aproape niciodată.</p>` +
      `<p>Dar poți face altceva: alegi oameni la întâmplare și îi rogi să numească un prieten. Prin paradox, prietenii numiți sunt sistematic mai bine plasați decât cei aleși la întâmplare. Fără niciun calcul, fără nicio hartă, obții oameni mai buni decât hazardul.</p>` +
      `<p>Strategia se numește <strong>imunizare prin cunoștințe</strong> (<em>acquaintance immunization</em>) și e folosită în sănătate publică, unde nimeni nu are harta contactelor unui oraș.</p>` +
      `<h3 class="paradox__section-title">Și acum uită-te ce s-a întâmplat de fapt</h3>` +
      `<p>Percepția ta despre cine e popular e deformată de propria ta poziție în rețea. Nu vezi școala, vezi bucata din ea la care ești legat, iar acea bucată e părtinitoare spre cei bine conectați.</p>` +
      `<p>Orice feed face exact același lucru. Nu ești tu mai puțin interesant decât ceilalți. Vezi o <strong>selecție deformată</strong>.</p>`;
    appEl.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  async function pick(idx) {
    optBtns.forEach((b, i) => {
      b.disabled = true;
      b.classList.toggle("vote__option--picked", i === idx);
    });
    markVote(block.id, { selectedIndex: idx });
    if (opts.onAnswered) opts.onAnswered({ selectedIndex: idx });
    openReveal(idx);
  }
}

// (renderParadoxSubnet removed — the 4-state paradox card uses a scripted
// star SVG instead of the tap-the-six-nodes subnet from the earlier version.)

function addTitle(el, text, small) {
  const h = document.createElement(small ? "h2" : "h1");
  h.className = "slide__title" + (small ? " slide__title--sm" : "");
  h.textContent = text;
  el.appendChild(h);
}

function addBody(el, html) {
  const wrap = document.createElement("div");
  wrap.className = "slide__body";
  const p = document.createElement("p");
  p.innerHTML = html;
  wrap.appendChild(p);
  el.appendChild(wrap);
}

function addIntro(el, text) {
  const wrap = document.createElement("div");
  wrap.className = "slide__intro";
  wrap.innerHTML = text;
  el.appendChild(wrap);
}

function addNotification(el, n) {
  const panel = document.createElement("div");
  panel.className = "notification-panel";
  if (n.meta1) {
    const m1 = document.createElement("div");
    m1.className = "notification-panel__meta";
    m1.textContent = n.meta1;
    panel.appendChild(m1);
  }
  if (n.body) {
    const b = document.createElement("div");
    b.className = "notification-panel__body";
    b.textContent = n.body;
    panel.appendChild(b);
  }
  if (n.meta2) {
    const m2 = document.createElement("div");
    m2.className = "notification-panel__meta notification-panel__meta--end";
    m2.textContent = n.meta2;
    panel.appendChild(m2);
  }
  el.appendChild(panel);
}

function addCitation(el, citation) {
  const p = document.createElement("p");
  p.className = "slide__citation";
  p.innerHTML = citation;
  el.appendChild(p);
}

function addCaption(el, text) {
  const c = document.createElement("p");
  c.className = "slide__caption";
  // Author-provided copy may include inline emphasis (<strong>, <em>).
  // JSON is authored, not user input, so innerHTML is safe here.
  c.innerHTML = text;
  el.appendChild(c);
}

function addPreview(el, preview) {
  const pre = document.createElement("pre");
  pre.className = "data-preview";
  pre.textContent = Array.isArray(preview.lines) ? preview.lines.join("\n") : String(preview);
  el.appendChild(pre);
  if (preview.legend) {
    const l = document.createElement("div");
    l.className = "data-preview__legend";
    l.textContent = preview.legend;
    el.appendChild(l);
  }
  if (preview.caption) {
    const cap = document.createElement("p");
    cap.className = "data-preview__caption";
    cap.textContent = preview.caption;
    el.appendChild(cap);
  }
}

async function wireCodePrag(vizWrap, codeWrap, block, slideState, V) {
  const [pairsRes, statsRes, vizMod, codeMod] = await Promise.all([
    fetch("data/highschool-pairs.json"),
    fetch("data/highschool-stats.json"),
    import(`./visualizations.js?v=${V}`),
    import(`./code-runner.js?v=${V}`)
  ]);
  const pairsData = await pairsRes.json();
  const stats     = await statsRes.json();
  const minPrag   = (stats.edgeCountByThreshold?.["1"] || 0) > 800 ? 2 : 1;

  let currentViz = null;
  async function renderNet(edges, countEl) {
    if (currentViz && typeof currentViz.destroy === "function") {
      try { currentViz.destroy(); } catch { /* ignore */ }
    }
    vizWrap.innerHTML = "";
    currentViz = await vizMod.renderNetwork(vizWrap, {
      title: block.title,
      inlineData: { nodes: pairsData.nodes, edges }
    });
    if (countEl) countEl.textContent = `${edges.length} muchii`;
  }
  const initialPrag = 3;
  const initialEdges = pairsData.pairs.filter((p) => p.weight >= initialPrag);
  await renderNet(initialEdges);

  const meta = document.createElement("div");
  meta.className = "code-runner__result";
  meta.textContent = `La PRAG = ${initialPrag}: ${initialEdges.length} legături rămase din întreaga zi.`;
  codeWrap.appendChild(meta);

  if (minPrag > 1) {
    const warn = document.createElement("p");
    warn.className = "code-runner__warn";
    warn.textContent = "La prag 1 rețeaua depășește limita de desenare pe telefon; folosim prag minim 2.";
    codeWrap.appendChild(warn);
  }

  codeMod.renderCodeInteractive(codeWrap, block, {
    getContext: async () => ({ pairs: pairsData.pairs, prag_minim: minPrag }),
    onResult: async (val) => {
      const edges = val && Array.isArray(val.edges) ? val.edges : [];
      const prag = val?.prag ?? "?";
      await renderNet(edges);
      meta.textContent = `La PRAG = ${prag}: ${edges.length} legături rămase din întreaga zi.`;
    }
  });
  slideState.viz = { refit: () => currentViz && currentViz.refit && currentViz.refit() };
}

async function wireCodeDiffuz(vizWrap, codeWrap, block, slideState, V) {
  const [netRes, statsRes, diffMod, codeMod] = await Promise.all([
    fetch("data/highschool-network.json"),
    fetch("data/highschool-stats.json"),
    import(`./diffusion.js?v=${V}`),
    import(`./code-runner.js?v=${V}`)
  ]);
  const network = await netRes.json();
  const stats   = await statsRes.json();
  const topName = stats.topByDegree?.[0]?.name || "Octav";
  const nameToId = new Map(network.nodes.map((n) => [n.name, String(n.id)]));

  const stageWrap = document.createElement("div");
  vizWrap.appendChild(stageWrap);

  let currentViz = null;
  async function renderRun(sourceId, threshold) {
    if (currentViz && typeof currentViz.destroy === "function") {
      try { currentViz.destroy(); } catch {}
    }
    stageWrap.innerHTML = "";
    diffMod.setShared({ sourceId: String(sourceId), threshold });
    currentViz = await diffMod.renderDiffusion(stageWrap, {
      mode: "replay-order",
      data: "data/highschool-network.json"
    });
  }

  const meta = document.createElement("div");
  meta.className = "code-runner__result";
  const { simulate: sim0 } = diffMod;
  const nodesLite = network.nodes.map((n) => ({ id: String(n.id), name: n.name }));
  const edgesLite = network.edges.map((e) => ({ source: String(e.source), target: String(e.target), weight: e.weight }));
  const k0 = sim0(nodesLite, edgesLite, String(nameToId.get(topName)), 3);
  const maxStep0 = Math.max(0, ...k0.values());
  meta.textContent = `Pornind de la ${topName}, zvonul a ajuns la ${k0.size} din ${network.nodes.length} de elevi în ${maxStep0} pași.`;
  codeWrap.appendChild(meta);

  // initial render
  await renderRun(nameToId.get(topName), 3);

  codeMod.renderCodeInteractive(codeWrap, block, {
    getContext: async () => ({
      nodes: nodesLite,
      edges: edgesLite
    }),
    onResult: async (val) => {
      const srcName = val?.source_name || topName;
      const srcId   = nameToId.get(srcName) || nameToId.get(topName);
      const thr     = val?.threshold ?? 3;
      await renderRun(srcId, thr);
      const { simulate } = diffMod;
      const k = simulate(nodesLite, edgesLite, String(srcId), thr);
      const maxStep = Math.max(0, ...k.values());
      meta.textContent = `Pornind de la ${srcName}, zvonul a ajuns la ${k.size} din ${network.nodes.length} de elevi în ${maxStep} pași.`;
    }
  });
  slideState.viz = { refit: () => currentViz && currentViz.refit && currentViz.refit() };
}

function countBins(values, bw) {
  if (!values.length || !bw) return 0;
  const mn = Math.min(...values), mx = Math.max(...values);
  return Math.floor((mx - Math.floor(mn / bw) * bw) / bw) + 1;
}

async function wireCodeBins(vizWrap, codeWrap, block, slideState, V) {
  const [statsRes, chartMod, codeMod] = await Promise.all([
    fetch("data/highschool-stats.json"),
    import(`./charts.js?v=${V}`),
    import(`./code-runner.js?v=${V}`)
  ]);
  const stats = await statsRes.json();
  const degrees = stats.degrees || [];

  const chartHost = document.createElement("div");
  chartHost.className = "chart";
  vizWrap.appendChild(chartHost);
  let api = await chartMod.renderChart(chartHost, {
    variant: "histogram",
    values: degrees,
    xLabel: block.xLabel || "contacte",
    yLabel: block.yLabel || "elevi",
    defaultBinWidth: 3,
    slider: false
  });

  const meta = document.createElement("div");
  meta.className = "code-runner__result";
  meta.textContent = `La lățime 3: histograma se împarte în ${countBins(degrees, 3)} intervale.`;
  codeWrap.appendChild(meta);

  codeMod.renderCodeInteractive(codeWrap, block, {
    getContext: async () => ({ degrees }),
    onResult: async (val) => {
      const bw = val && (val.binWidth || val.latime) ? (val.binWidth || val.latime) : 3;
      chartHost.innerHTML = "";
      api = await chartMod.renderChart(chartHost, {
        variant: "histogram",
        values: degrees,
        xLabel: block.xLabel || "contacte",
        yLabel: block.yLabel || "elevi",
        defaultBinWidth: bw,
        slider: false
      });
      meta.textContent = `La lățime ${bw}: histograma se împarte în ${countBins(degrees, bw)} intervale.`;
    }
  });
  slideState.viz = { refit: () => {} };
}

function fillSlide(slideState, callbacks) {
  if (slideState.fillPromise) return slideState.fillPromise;
  const onAnswered = callbacks.onAnswered;
  const onAdvance = callbacks.onAdvance;
  const stats = callbacks.stats;
  slideState.fillPromise = (async () => {
    const b = slideState.block;
    const el = slideState.el;

    try {
    switch (b.type) {
      case "chapter-intro": {
        const wrap = document.createElement("div");
        wrap.className = "chapter-intro";
        const num = document.createElement("div");
        num.className = "chapter-intro__num";
        num.textContent = `Capitolul ${b.chapter.n} din ${b.chapterTotal}`;
        const title = document.createElement("h1");
        title.className = "chapter-intro__title";
        title.textContent = b.chapter.title;
        const hint = document.createElement("p");
        hint.className = "chapter-intro__hint";
        hint.textContent = "Apasă Continuă ca să intri.";
        wrap.appendChild(num);
        wrap.appendChild(title);
        wrap.appendChild(hint);
        el.appendChild(wrap);
        break;
      }
      case "text": {
        if (b.title) addTitle(el, b.title);
        if (b.notification) addNotification(el, b.notification);
        if (b.content) addBody(el, b.content);
        if (b.preview) addPreview(el, b.preview);
        if (b.citation) addCitation(el, b.citation);
        break;
      }
      case "callout": {
        const c = document.createElement("aside");
        c.className = "callout";
        if (b.title) {
          const h = document.createElement("h2");
          h.className = "callout__title";
          h.textContent = b.title;
          c.appendChild(h);
        }
        const p = document.createElement("p");
        p.innerHTML = b.content;
        p.style.margin = "0";
        c.appendChild(p);
        el.appendChild(c);
        break;
      }
      case "image": {
        const fig = document.createElement("figure");
        fig.className = "figure";
        const img = document.createElement("img");
        img.src = b.src;
        img.alt = b.alt || "";
        img.loading = "lazy";
        fig.appendChild(img);
        if (b.caption) {
          const cap = document.createElement("figcaption");
          cap.className = "figure__caption";
          cap.textContent = b.caption;
          fig.appendChild(cap);
        }
        el.appendChild(fig);
        break;
      }
      case "video": {
        const v = document.createElement("div");
        v.className = "video-placeholder";
        v.innerHTML = `<strong>${b.title || "Video"}</strong><br>${b.note || ""}`;
        el.appendChild(v);
        break;
      }
      case "quiz": {
        if (b.title) addTitle(el, b.title, true);
        if (b.intro) addIntro(el, b.intro);
        const wrap = document.createElement("div");
        renderQuiz(wrap, b, { onAnswered: () => onAnswered(slideState) });
        el.appendChild(wrap);
        if (b.caption) addCaption(el, b.caption);
        break;
      }
      case "vote": {
        if (b.title) addTitle(el, b.title, true);
        if (b.intro) addIntro(el, b.intro);
        const wrap = document.createElement("div");
        renderVote(wrap, b, { onAnswered: () => onAnswered(slideState) });
        el.appendChild(wrap);
        if (b.caption) addCaption(el, b.caption);
        break;
      }
      case "paradox": {
        if (b.title) addTitle(el, b.title, true);
        if (b.intro) addIntro(el, b.intro);
        const wrap = document.createElement("div");
        wrap.className = "paradox";
        el.appendChild(wrap);
        await renderParadox(wrap, b, stats, {
          onAnswered: () => onAnswered(slideState)
        });
        if (b.caption) addCaption(el, b.caption);
        break;
      }
      case "quizset": {
        if (b.title) addTitle(el, b.title, true);
        if (b.intro) addIntro(el, b.intro);
        const wrap = document.createElement("div");
        wrap.className = "quizset";
        el.appendChild(wrap);
        const questions = b.questions || [];
        const total = questions.length;
        let answered = 0;
        questions.forEach((q, i) => {
          const holder = document.createElement("div");
          holder.className = "quizset__q";
          const num = document.createElement("div");
          num.className = "quizset__num";
          num.textContent = `Întrebarea ${i + 1} din ${total}`;
          holder.appendChild(num);
          wrap.appendChild(holder);
          const sub = { ...q, id: `${b.id}-${i}` };
          renderQuiz(holder, sub, {
            onAnswered: () => {
              answered++;
              if (answered >= total) onAnswered(slideState);
            }
          });
        });
        if (b.caption) addCaption(el, b.caption);
        break;
      }
      case "code": {
        if (b.title) addTitle(el, b.title, true);
        if (b.intro) addIntro(el, b.intro);
        const vizWrap = document.createElement("div");
        vizWrap.className = "code-viz";
        el.appendChild(vizWrap);
        const codeWrap = document.createElement("div");
        el.appendChild(codeWrap);
        if (b.instance === "prag") {
          await wireCodePrag(vizWrap, codeWrap, b, slideState, V);
        } else if (b.instance === "bins") {
          await wireCodeBins(vizWrap, codeWrap, b, slideState, V);
        } else if (b.instance === "diffuz") {
          await wireCodeDiffuz(vizWrap, codeWrap, b, slideState, V);
        } else {
          const { renderCodeRunner } = await import(`./code-runner.js?v=${V}`);
          renderCodeRunner(codeWrap, b);
        }
        if (b.caption) addCaption(el, b.caption);
        break;
      }
      case "visualization": {
        if (b.title) addTitle(el, b.title, true);
        if (b.description) addIntro(el, b.description);
        const vizWrap = document.createElement("div");
        el.appendChild(vizWrap);
        if (b.kind === "network") {
          slideState.viz = await renderNetwork(vizWrap, b);
        }
        if (b.caption) addCaption(el, b.caption);
        break;
      }
      case "interactive": {
        if (b.title) addTitle(el, b.title, true);
        if (b.intro) addIntro(el, b.intro);
        const vizWrap = document.createElement("div");
        el.appendChild(vizWrap);
        slideState.viz = await renderInteractive(vizWrap, b);
        break;
      }
      case "diffusion": {
        if (b.title) addTitle(el, b.title, true);
        if (b.intro) addIntro(el, b.intro);
        const vizWrap = document.createElement("div");
        el.appendChild(vizWrap);
        const { renderDiffusion } = await import(`./diffusion.js?v=${V}`);
        slideState.viz = await renderDiffusion(vizWrap, b, {
          onAdvance: onAdvance
        });
        if (b.caption) addCaption(el, b.caption);
        break;
      }
      case "chart": {
        if (b.title) addTitle(el, b.title, true);
        if (b.intro) addIntro(el, b.intro);
        const chartWrap = document.createElement("div");
        el.appendChild(chartWrap);
        const { renderChart } = await import(`./charts.js?v=${V}`);
        slideState.viz = await renderChart(chartWrap, b);
        if (b.caption) addCaption(el, b.caption);
        break;
      }
      case "conclusion": {
        if (b.title) addTitle(el, b.title);
        if (b.content) addBody(el, b.content);
        break;
      }
      default: {
        const p = document.createElement("p");
        p.textContent = `Bloc necunoscut: ${b.type}`;
        el.appendChild(p);
      }
    }
    } catch (err) {
      // A single broken card must not lock the whole lesson. Show the error
      // inline and keep advancement enabled so the reader can move past it.
      const warn = document.createElement("div");
      warn.className = "slide__error";
      warn.style.cssText = "background:#f7ede1;border:1px solid #c96d3f;border-radius:6px;padding:12px;margin-top:12px;font-size:0.9rem;color:#5a2a10;";
      warn.textContent = `Cardul „${b.id || b.type}" nu s-a randat corect (${err && err.message ? err.message : err}). Poți continua.`;
      el.appendChild(warn);
      slideState.canAdvance = true;
    }
  })();
  return slideState.fillPromise;
}

export async function renderSlides(root, lesson) {
  markLessonStarted(lesson.id);
  root.innerHTML = "";
  root.classList.add("slides-root");

  const statsSource = lesson.statsSource || "data/highschool-stats.json";
  const stats = await loadStats(statsSource);

  const chapters = Array.isArray(lesson.chapters) ? lesson.chapters : [];

  const rawBlocks = lesson.blocks || [];
  // Inject chapter-intro cards at every chapter startIdx.
  const mergedBlocks = [];
  const nChapters = chapters.length;
  let curChapter = null;
  for (let i = 0; i < rawBlocks.length; i++) {
    const ch = chapters.find((c) => c.startIdx === i);
    if (ch) {
      curChapter = ch;
      mergedBlocks.push({
        type: "chapter-intro",
        id: `chapter-intro-${ch.n}`,
        chapter: ch,
        chapterTotal: nChapters,
        _chapter: ch
      });
    }
    // Blocks marked enabled: false stay in the file (so authors can flip them
    // back on without editing structure) but do not enter the reader's flow.
    if (rawBlocks[i].enabled === false) continue;
    mergedBlocks.push({ ...rawBlocks[i], _chapter: curChapter });
  }

  const blocks = mergedBlocks.length ? mergedBlocks : rawBlocks;
  const total = blocks.length;

  function chapterForBlock(b) { return b?._chapter || null; }

  const progressState = getProgress();
  const slideState = blocks.map((b) => {
    const gatingType = b.type === "quiz" || b.type === "vote" || b.type === "quizset" || b.type === "paradox";
    const s = {
      block: substituteBlock(b, stats),
      el: makeSlideElement(),
      fillPromise: null,
      viz: null,
      canAdvance: !gatingType
    };
    if (b.type === "quiz" && progressState.quizzes?.[b.id]) s.canAdvance = true;
    if (b.type === "vote" && progressState.votes?.[b.id]) s.canAdvance = true;
    if (b.type === "paradox" && progressState.votes?.[b.id]) s.canAdvance = true;
    if (b.type === "quizset" && Array.isArray(b.questions)) {
      const allAnswered = b.questions.every((_, i) => progressState.quizzes?.[`${b.id}-${i}`]);
      if (allAnswered && b.questions.length) s.canAdvance = true;
    }
    return s;
  });

  const header = document.createElement("div");
  header.className = "slides-header";
  const chapterEl = document.createElement("div");
  chapterEl.className = "slides-chapter";
  chapterEl.setAttribute("aria-live", "polite");
  const bar = document.createElement("div");
  bar.className = "slides-progress-bar";
  bar.setAttribute("role", "presentation");
  const fill = document.createElement("div");
  fill.className = "slides-progress-fill";
  bar.appendChild(fill);
  const count = document.createElement("div");
  count.className = "slides-count";
  count.setAttribute("aria-live", "polite");
  const row = document.createElement("div");
  row.className = "slides-header__row";
  row.appendChild(bar);
  row.appendChild(count);
  header.appendChild(chapterEl);
  header.appendChild(row);
  root.appendChild(header);

  const stage = document.createElement("div");
  stage.className = "slides-stage";
  stage.setAttribute("aria-live", "polite");
  root.appendChild(stage);
  slideState.forEach((s) => stage.appendChild(s.el));

  const nav = document.createElement("div");
  nav.className = "slides-nav";
  const backBtn = document.createElement("button");
  backBtn.type = "button";
  backBtn.className = "btn btn--ghost slides-back";
  backBtn.textContent = "Înapoi";
  const nextBtn = document.createElement("button");
  nextBtn.type = "button";
  nextBtn.className = "btn btn--primary slides-next";
  nextBtn.textContent = "Continuă";
  nav.appendChild(backBtn);
  nav.appendChild(nextBtn);
  root.appendChild(nav);

  let current = 0;
  const saved = getSlidePosition(lesson.id);
  const hasSaved = Number.isInteger(saved) && saved > 0 && saved < total;

  function onQuizAnswered(s) {
    s.canAdvance = true;
    updateNav();
  }

  function collectQuizIds() {
    const ids = [];
    for (const b of blocks) {
      if (b.type === "quiz" && b.id) ids.push(b.id);
      if (b.type === "quizset" && b.id && Array.isArray(b.questions)) {
        b.questions.forEach((_, i) => ids.push(`${b.id}-${i}`));
      }
    }
    return ids;
  }

  function doRestart() {
    resetLessonProgress(lesson.id, collectQuizIds());
    slideState.forEach((s) => {
      if (s.viz && typeof s.viz.destroy === "function") {
        try { s.viz.destroy(); } catch { /* ignore */ }
      }
      s.fillPromise = null;
      s.viz = null;
      s.el.innerHTML = "";
      if (s.block.type === "quiz" || s.block.type === "vote" || s.block.type === "quizset" || s.block.type === "paradox") s.canAdvance = false;
    });
  }

  function showResumeBanner(atIndex) {
    const banner = document.createElement("section");
    banner.className = "slide slides-resume";
    banner.tabIndex = -1;
    banner.setAttribute("aria-live", "polite");
    banner.innerHTML =
      `<h1 class="slide__title">Reia lecția?</h1>` +
      `<p class="slide__intro">Ai lăsat lecția la slide-ul ${atIndex + 1} din ${total}. ` +
      `Vrei să continui de acolo sau să începi din nou?</p>` +
      `<div class="btn-row">` +
      `<button type="button" class="btn btn--primary" data-resume="continue">Continuă</button>` +
      `<button type="button" class="btn btn--ghost" data-resume="restart">Începe din nou</button>` +
      `</div>`;
    stage.prepend(banner);
    slideState.forEach((s) => { s.el.hidden = true; });
    backBtn.hidden = true;
    nextBtn.hidden = true;
    fill.style.width = "0%";
    count.textContent = "";

    banner.querySelector('[data-resume="continue"]').addEventListener("click", () => {
      banner.remove();
      nextBtn.hidden = false;
      show(atIndex);
    });
    banner.querySelector('[data-resume="restart"]').addEventListener("click", () => {
      banner.remove();
      nextBtn.hidden = false;
      doRestart();
      show(0);
    });
    banner.focus({ preventScroll: true });
  }

  function updateNav() {
    const pct = Math.round(((current + 1) / total) * 100);
    fill.style.width = `${pct}%`;
    count.textContent = `${current + 1} / ${total}`;
    backBtn.hidden = current === 0;
    const isLast = current === total - 1;
    nextBtn.textContent = isLast ? "Înapoi la curs" : "Continuă";
    const cur = slideState[current];
    nextBtn.disabled = !isLast && !cur.canAdvance;
    const curBlock = slideState[current]?.block;
    const ch = chapterForBlock(curBlock);
    if (ch) {
      const prevBlock = current > 0 ? slideState[current - 1]?.block : null;
      const prevCh = chapterForBlock(prevBlock);
      const isNew = !prevCh || prevCh.n !== ch.n;
      chapterEl.textContent = `Capitolul ${ch.n} · ${ch.title}`;
      chapterEl.classList.toggle("slides-chapter--pulse", isNew && current > 0);
    } else {
      chapterEl.textContent = "";
    }
  }

  async function show(idx) {
    idx = Math.max(0, Math.min(total - 1, idx));
    slideState.forEach((s, i) => {
      const active = i === idx;
      s.el.hidden = !active;
      s.el.setAttribute("aria-hidden", active ? "false" : "true");
    });
    current = idx;
    updateNav();
    markSlidePosition(lesson.id, idx);
    window.scrollTo({ top: 0, behavior: "auto" });
    slideState[idx].el.focus({ preventScroll: true });

    await fillSlide(slideState[idx], { onAnswered: onQuizAnswered, onAdvance: goNext, stats });

    if (current !== idx) return;
    // If the block finished (or errored inline) canAdvance may have flipped;
    // refresh the Continuă button so the reader is not stuck on a broken card.
    updateNav();

    // Post-render safety net: check for two dev-blocking mistakes.
    requestAnimationFrame(() => {
      if (current !== idx) return;
      const domText = slideState[idx].el.innerText || "";
      // 1. Unresolved placeholders {{...}} still in text.
      const leaked = domText.match(/\{\{[^}]+\}\}/g);
      if (leaked && leaked.length) {
        const warn = document.createElement("div");
        warn.style.cssText = "background:#c96d3f;color:#fff;padding:8px 12px;margin:12px 0;border-radius:6px;font-size:0.85rem;font-family:monospace;";
        warn.textContent = `Placeholder-e nerezolvate în „${slideState[idx].block.id || "?"}": ${leaked.join(", ")}`;
        slideState[idx].el.insertBefore(warn, slideState[idx].el.firstChild);
        console.warn("Unresolved placeholders on", slideState[idx].block.id, leaked);
      }
      // 2. Author HTML tags rendered as text (indicates textContent was used
      //    where innerHTML should be). Look for literal <strong>, </strong>,
      //    <em>, </em> etc. in innerText.
      const rawTags = domText.match(/<\/?(strong|em|b|i|u|br|p)>/gi);
      if (rawTags && rawTags.length) {
        const warn2 = document.createElement("div");
        warn2.style.cssText = "background:#5a2a10;color:#fff;padding:8px 12px;margin:12px 0;border-radius:6px;font-size:0.85rem;font-family:monospace;";
        warn2.textContent = `Marcaje HTML afișate ca text în „${slideState[idx].block.id || "?"}": ${[...new Set(rawTags)].join(", ")}`;
        slideState[idx].el.insertBefore(warn2, slideState[idx].el.firstChild);
        console.warn("Raw HTML tags on", slideState[idx].block.id, rawTags);
      }
    });
    const viz = slideState[idx].viz;
    if (viz && typeof viz.refit === "function") {
      requestAnimationFrame(() => {
        if (current === idx) viz.refit();
      });
    }
  }

  function goNext() {
    if (current === total - 1) {
      markLessonCompleted(lesson.id);
      location.href = "index.html";
      return;
    }
    if (!slideState[current].canAdvance) return;
    show(current + 1);
  }

  backBtn.addEventListener("click", () => show(current - 1));
  nextBtn.addEventListener("click", goNext);

  root.addEventListener("keydown", (e) => {
    const t = e.target;
    if (t && (t.tagName === "TEXTAREA" || t.tagName === "INPUT")) return;
    if (e.key === "ArrowRight") {
      e.preventDefault();
      if (current < total - 1 && slideState[current].canAdvance) show(current + 1);
      else if (current === total - 1) goNext();
    } else if (e.key === "ArrowLeft") {
      e.preventDefault();
      if (current > 0) show(current - 1);
    } else if (e.key === "Enter") {
      if (t && (t.tagName === "BUTTON" || t.tagName === "A" || t.tagName === "LABEL")) return;
      e.preventDefault();
      goNext();
    }
  });

  if (hasSaved) {
    showResumeBanner(saved);
  } else {
    show(0);
  }
}
