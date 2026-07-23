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
  vedeta:      "sliceMetrics.characters.vedeta",
  campion:     "sliceMetrics.characters.campion",
  surpriza:    "sliceMetrics.characters.surpriza",
  puntea:      "sliceMetrics.characters.puntea",
  dependent:   "sliceMetrics.characters.dependent",
  izolat:      "sliceMetrics.characters.izolat",
  // Legacy heuristic keys kept for backward-compat.
  discretul:   "sliceMetrics.characters.surpriza",
  izolatul:    "sliceMetrics.characters.izolat"
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

const FIELD_ALIASES = { degree: "popularity" };

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
  "xLabel", "yLabel", "note", "citation"
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

// Paradox block: vote + interactive 6-node subnet + whole-school numbers
async function renderParadox(container, block, stats, opts) {
  const progressMod = await import(`./progress.js?v=${V}`);
  const { getVote, markVote } = progressMod;
  const prior = getVote(block.id);

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

  const revealEl = document.createElement("div");
  revealEl.className = "paradox__reveal";
  revealEl.hidden = true;
  container.appendChild(revealEl);

  async function pick(idx) {
    optBtns.forEach((b, i) => {
      b.disabled = true;
      b.classList.toggle("vote__option--picked", i === idx);
    });
    markVote(block.id, { selectedIndex: idx });
    if (opts.onAnswered) opts.onAnswered({ selectedIndex: idx });
    await showReveal();
  }

  async function showReveal() {
    revealEl.hidden = false;
    revealEl.innerHTML = "";
    const subnet = stats?.sliceMetrics?.friendshipParadox?.subnet;
    if (subnet && Array.isArray(subnet.nodes)) {
      const subnetHost = document.createElement("div");
      subnetHost.className = "paradox__subnet";
      revealEl.appendChild(subnetHost);
      renderParadoxSubnet(subnetHost, subnet);
    }
    const p = stats?.sliceMetrics?.friendshipParadox || stats?.friendshipParadox;
    if (p) {
      const nums = document.createElement("div");
      nums.className = "paradox__numbers";
      nums.innerHTML =
        `<p>Pe toată școala: un elev are în medie <strong>${p.meanDegree}</strong> prieteni.</p>` +
        `<p>Prietenii lui au în medie <strong>${p.meanFriendDegree}</strong>.</p>` +
        `<p><strong>${p.pctBelow}%</strong> dintre elevi sunt sub media prietenilor lor.</p>`;
      revealEl.appendChild(nums);
    }
  }

  if (prior && typeof prior.selectedIndex === "number") {
    optBtns.forEach((b, i) => {
      b.disabled = true;
      b.classList.toggle("vote__option--picked", i === prior.selectedIndex);
    });
    await showReveal();
    if (opts.onAnswered) opts.onAnswered({ selectedIndex: prior.selectedIndex });
  }
}

function renderParadoxSubnet(container, subnet) {
  const nodes = subnet.nodes || [];
  const edges = subnet.edges || [];
  const N = nodes.length;
  const W = 480, H = 260;
  const cx = W / 2, cyC = H / 2 - 10;
  const r = 90;

  const positions = {};
  nodes.forEach((n, i) => {
    const angle = (i / Math.max(1, N)) * 2 * Math.PI - Math.PI / 2;
    positions[n.id] = { x: cx + r * Math.cos(angle), y: cyC + r * Math.sin(angle) };
  });

  const edgeSvg = edges.map((e) => {
    const p1 = positions[e.source];
    const p2 = positions[e.target];
    if (!p1 || !p2) return "";
    return `<line x1="${p1.x.toFixed(1)}" y1="${p1.y.toFixed(1)}" x2="${p2.x.toFixed(1)}" y2="${p2.y.toFixed(1)}" stroke="#b57140" stroke-width="1.5" opacity="0.5"/>`;
  }).join("");

  const nodeSvg = nodes.map((n) => {
    const p = positions[n.id];
    const color = n.belowMean ? "#a3341f" : "#3d7a52";
    return `<g class="paradox-node" data-id="${n.id}" style="cursor:pointer">` +
      `<circle cx="${p.x.toFixed(1)}" cy="${p.y.toFixed(1)}" r="20" fill="${color}" fill-opacity="0.8"/>` +
      `<text x="${p.x.toFixed(1)}" y="${(p.y + 4).toFixed(1)}" text-anchor="middle" font-size="11" fill="white" font-family="Georgia, serif">${n.name}</text>` +
      `</g>`;
  }).join("");

  container.innerHTML =
    `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto;max-width:520px;display:block;margin:0 auto">` +
    edgeSvg + nodeSvg +
    `</svg>`;

  const hint = document.createElement("p");
  hint.className = "paradox__hint";
  hint.textContent = "Atinge pe rând fiecare din cei 6. Numărăm împreună.";
  container.appendChild(hint);

  const tracker = document.createElement("p");
  tracker.className = "paradox__tracker";
  tracker.textContent = `Numărate: 0/${N}. Sub media prietenilor: 0/${N}.`;
  container.appendChild(tracker);

  const counted = new Set();
  container.querySelectorAll(".paradox-node").forEach((g) => {
    g.addEventListener("click", () => {
      const id = parseInt(g.dataset.id, 10);
      const n = nodes.find((x) => x.id === id);
      if (!n) return;
      counted.add(id);
      const belowSoFar = [...counted].filter((cId) => nodes.find((x) => x.id === cId)?.belowMean).length;
      const friendList = (n.friendDegrees || []).join(", ");
      hint.textContent = `${n.name} are ${n.degree} prieteni; prietenii au ${friendList}, deci în medie ${n.friendMean}. ${n.name} e ${n.belowMean ? "sub" : "peste"} această medie.`;
      tracker.textContent = `Numărate: ${counted.size}/${N}. Sub media prietenilor: ${belowSoFar}/${counted.size}.`;
      const c = g.querySelector("circle");
      if (c) { c.setAttribute("stroke", "#2a1f16"); c.setAttribute("stroke-width", "2"); }
    });
  });
}

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
  c.textContent = text;
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
        if (b.caption) {
          const c = document.createElement("p");
          c.className = "slide__caption";
          c.textContent = b.caption;
          el.appendChild(c);
        }
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
        if (b.caption) {
          const c = document.createElement("p");
          c.className = "slide__caption";
          c.textContent = b.caption;
          el.appendChild(c);
        }
        break;
      }
      case "chart": {
        if (b.title) addTitle(el, b.title, true);
        if (b.intro) addIntro(el, b.intro);
        const chartWrap = document.createElement("div");
        el.appendChild(chartWrap);
        const { renderChart } = await import(`./charts.js?v=${V}`);
        slideState.viz = await renderChart(chartWrap, b);
        if (b.caption) {
          const c = document.createElement("p");
          c.className = "slide__caption";
          c.textContent = b.caption;
          el.appendChild(c);
        }
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
      const chapterOfN = rawBlocks
        .slice(i, i + 30) // rough limit
        .filter((_, j) => {
          const nextCh = chapters.find((c) => c.startIdx === i + j && c !== ch);
          return !nextCh || i + j < (nextCh?.startIdx ?? Infinity);
        }).length;
      mergedBlocks.push({
        type: "chapter-intro",
        id: `chapter-intro-${ch.n}`,
        chapter: ch,
        chapterTotal: nChapters,
        _chapter: ch
      });
    }
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
