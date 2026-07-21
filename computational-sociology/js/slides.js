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
  seedFirst:   "majorityIllusion.seedNames"
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

function resolveExpr(stats, expr) {
  if (!stats) return null;
  const trimmed = expr.trim();
  if (trimmed.includes(":")) {
    const [field, key] = trimmed.split(":").map((s) => s.trim());
    const path = NAME_SHORTCUTS[key];
    if (!path) return null;
    const arr = walkPath(stats, path.split("."));
    if (Array.isArray(arr) && arr[0] != null) {
      const first = arr[0];
      return typeof first === "object" ? first[field] : first;
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
  meta.className = "chart__meta";
  meta.textContent = `${initialEdges.length} muchii · prag ${initialPrag}`;
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
      await renderNet(edges);
      meta.textContent = `${edges.length} muchii · prag ${val?.prag ?? "?"}`;
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
  meta.className = "chart__meta";
  meta.textContent = `Sursă implicită: ${topName}. Prag: 3.`;
  codeWrap.appendChild(meta);

  // initial render
  await renderRun(nameToId.get(topName), 3);

  codeMod.renderCodeInteractive(codeWrap, block, {
    getContext: async () => ({
      nodes: network.nodes.map((n) => ({ id: String(n.id), name: n.name })),
      edges: network.edges.map((e) => ({ source: String(e.source), target: String(e.target), weight: e.weight }))
    }),
    onResult: async (val) => {
      const srcName = val?.source_name || topName;
      const srcId   = nameToId.get(srcName) || nameToId.get(topName);
      const thr     = val?.threshold ?? 3;
      await renderRun(srcId, thr);
      const { simulate } = diffMod;
      const k = simulate(
        network.nodes.map((n) => ({ id: String(n.id), name: n.name })),
        network.edges.map((e) => ({ source: String(e.source), target: String(e.target), weight: e.weight })),
        String(srcId), thr
      );
      meta.textContent = `Sursă: ${srcName} · Prag: ${thr} · Acoperire: ${k.size} din ${network.nodes.length}.`;
    }
  });
  slideState.viz = { refit: () => currentViz && currentViz.refit && currentViz.refit() };
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
  meta.className = "chart__meta";
  meta.textContent = `lățime interval 3 (implicit)`;
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
      meta.textContent = `lățime interval ${bw}`;
    }
  });
  slideState.viz = { refit: () => {} };
}

function fillSlide(slideState, callbacks) {
  if (slideState.fillPromise) return slideState.fillPromise;
  const onAnswered = callbacks.onAnswered;
  const onAdvance = callbacks.onAdvance;
  slideState.fillPromise = (async () => {
    const b = slideState.block;
    const el = slideState.el;

    switch (b.type) {
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
  })();
  return slideState.fillPromise;
}

export async function renderSlides(root, lesson) {
  markLessonStarted(lesson.id);
  root.innerHTML = "";
  root.classList.add("slides-root");

  const statsSource = lesson.statsSource || "data/highschool-stats.json";
  const stats = await loadStats(statsSource);

  const blocks = lesson.blocks || [];
  const total = blocks.length;

  const progressState = getProgress();
  const slideState = blocks.map((b) => {
    const gatingType = b.type === "quiz" || b.type === "vote" || b.type === "quizset";
    const s = {
      block: substituteBlock(b, stats),
      el: makeSlideElement(),
      fillPromise: null,
      viz: null,
      canAdvance: !gatingType
    };
    if (b.type === "quiz" && progressState.quizzes?.[b.id]) s.canAdvance = true;
    if (b.type === "vote" && progressState.votes?.[b.id]) s.canAdvance = true;
    if (b.type === "quizset" && Array.isArray(b.questions)) {
      const allAnswered = b.questions.every((_, i) => progressState.quizzes?.[`${b.id}-${i}`]);
      if (allAnswered && b.questions.length) s.canAdvance = true;
    }
    return s;
  });

  const chapters = Array.isArray(lesson.chapters) ? lesson.chapters : [];
  function chapterForIdx(idx) {
    let cur = null;
    for (const c of chapters) {
      if (idx >= c.startIdx) cur = c;
    }
    return cur;
  }

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
      if (s.block.type === "quiz" || s.block.type === "vote" || s.block.type === "quizset") s.canAdvance = false;
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
    const ch = chapterForIdx(current);
    if (ch) {
      const prevIdx = current > 0 ? chapterForIdx(current - 1) : null;
      const isNew = !prevIdx || prevIdx.n !== ch.n;
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

    await fillSlide(slideState[idx], { onAnswered: onQuizAnswered, onAdvance: goNext });

    if (current !== idx) return;
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
