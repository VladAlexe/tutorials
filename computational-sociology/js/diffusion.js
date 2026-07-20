const V = new URL(import.meta.url).searchParams.get("v") || "1";
const { loadCytoscape, GROUP_PALETTE } = await import(`./visualizations.js?v=${V}`);

// Shared state so successive slides can use the same source/threshold.
const shared = {
  sourceId: null,
  threshold: 20,
  networkKey: null,
  network: null
};

async function loadJSON(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`Nu am putut încărca ${path}`);
  return res.json();
}

/**
 * Deterministic BFS-like diffusion with a contact-strength threshold.
 * Returns Map<nodeId, step> where step is when the node learned (0 = source).
 */
export function simulate(nodes, edges, sourceId, threshold) {
  const adj = new Map();
  for (const n of nodes) adj.set(String(n.id), []);
  for (const e of edges) {
    if ((e.weight ?? 0) >= threshold) {
      adj.get(String(e.source))?.push(String(e.target));
      adj.get(String(e.target))?.push(String(e.source));
    }
  }
  const knowsAt = new Map();
  const src = String(sourceId);
  if (!adj.has(src)) return knowsAt;
  knowsAt.set(src, 0);
  let frontier = [src];
  let step = 0;
  while (frontier.length && step < 100) {
    step++;
    const next = [];
    for (const id of frontier) {
      for (const nb of adj.get(id) || []) {
        if (!knowsAt.has(nb)) {
          knowsAt.set(nb, step);
          next.push(nb);
        }
      }
    }
    frontier = next;
  }
  return knowsAt;
}

function drawCurve(svg, series, maxY) {
  const w = svg.clientWidth || 240;
  const h = svg.clientHeight || 50;
  if (!series.length) { svg.innerHTML = ""; return; }
  const my = maxY || Math.max(...series, 1);
  const pts = series
    .map((y, i) => {
      const x = series.length === 1 ? w / 2 : (i / (series.length - 1)) * w;
      const yy = h - (y / my) * (h - 4) - 2;
      return `${x.toFixed(1)},${yy.toFixed(1)}`;
    })
    .join(" ");
  svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
  svg.setAttribute("preserveAspectRatio", "none");
  svg.innerHTML =
    `<polyline points="${pts}" fill="none" stroke="#8b4a1e" stroke-width="2"/>`;
}

async function getData(block) {
  if (shared.networkKey === block.data && shared.network) return shared.network;
  const d = await loadJSON(block.data);
  shared.network = d;
  shared.networkKey = block.data;
  return d;
}

function buildLegend(el, groups, colorMap) {
  const visible = groups.filter((g) => g && g !== "exemplu");
  if (visible.length < 2) { el.remove(); return; }
  el.innerHTML = "";
  for (const g of visible) {
    const chip = document.createElement("span");
    chip.className = "viz__legend-chip";
    const dot = document.createElement("span");
    dot.className = "viz__legend-dot";
    dot.style.background = colorMap.get(g);
    chip.appendChild(dot);
    chip.appendChild(document.createTextNode(g));
    el.appendChild(chip);
  }
}

function makeStyle() {
  return [
    {
      selector: "node",
      style: {
        "background-color": "data(color)",
        "opacity": 0.15,
        "width": 20,
        "height": 20,
        "border-width": 1,
        "border-color": "#5a4a3a",
        "transition-property": "opacity, width, height, border-width, border-color",
        "transition-duration": 220
      }
    },
    {
      selector: "edge",
      style: {
        "line-color": "#d9cfc0",
        "width": 1.2,
        "opacity": 0.4,
        "curve-style": "bezier"
      }
    },
    { selector: "node.knows", style: { "opacity": 1, "width": 22, "height": 22 } },
    {
      selector: "node.source",
      style: { "border-color": "#2a1f16", "border-width": 3, "width": 28, "height": 28 }
    },
    {
      selector: "node.top",
      style: {
        "opacity": 1,
        "border-color": "#2a1f16",
        "border-width": 3,
        "width": 30,
        "height": 30
      }
    }
  ];
}

function errorHandle(container, message) {
  container.innerHTML = "";
  const errEl = document.createElement("div");
  errEl.className = "code-runner__unsupported";
  errEl.textContent = message;
  container.appendChild(errEl);
  return { refit() {}, destroy() {} };
}

export async function renderDiffusion(container, block, options = {}) {
  const mode = block.mode;

  let cytoscape, data;
  try {
    [cytoscape, data] = await Promise.all([loadCytoscape(), getData(block)]);
  } catch (err) {
    return errorHandle(container, err.message);
  }

  const nodes = data.nodes.map((n) => ({
    id: String(n.id),
    label: n.label != null ? String(n.label) : String(n.id),
    group: n.group != null ? String(n.group) : ""
  }));
  const edges = data.edges.map((e, i) => ({
    id: `e${i}`,
    source: String(e.source),
    target: String(e.target),
    weight: typeof e.weight === "number" ? e.weight : 1
  }));

  const groups = [...new Set(nodes.map((n) => n.group).filter(Boolean))];
  const colorMap = new Map();
  groups.forEach((g, i) => colorMap.set(g, GROUP_PALETTE[i % GROUP_PALETTE.length]));

  container.classList.add("viz");
  container.innerHTML = "";

  const stage = document.createElement("div");
  stage.className = "viz__stage";
  stage.tabIndex = 0;
  container.appendChild(stage);

  const legend = document.createElement("div");
  legend.className = "viz__legend";
  container.appendChild(legend);
  buildLegend(legend, groups, colorMap);

  const controls = document.createElement("div");
  controls.className = "diffusion-controls";
  container.appendChild(controls);

  const elements = [
    ...nodes.map((n) => ({
      data: { id: n.id, label: n.label, group: n.group, color: colorMap.get(n.group) || GROUP_PALETTE[0] }
    })),
    ...edges.map((e) => ({
      data: { id: e.id, source: e.source, target: e.target, weight: e.weight }
    }))
  ];

  const cy = cytoscape({
    container: stage,
    elements,
    style: makeStyle(),
    layout: {
      name: "cose",
      animate: false,
      padding: 24,
      idealEdgeLength: 60,
      nodeRepulsion: 5000
    },
    minZoom: 0.3,
    maxZoom: 2.5,
    wheelSensitivity: 0.2
  });
  cy.style().update();

  const refit = () => {
    try { cy.resize(); cy.fit(undefined, 30); } catch { /* ignore */ }
  };
  const onWin = () => refit();
  window.addEventListener("resize", onWin);
  const ro = new ResizeObserver(refit);
  ro.observe(stage);
  requestAnimationFrame(refit);

  let animTimer = null;
  const clearAnim = () => { if (animTimer) { clearInterval(animTimer); animTimer = null; } };

  const total = nodes.length;

  function drawUpToStep(knowsAt, upTo) {
    cy.nodes().forEach((n) => {
      const at = knowsAt.get(n.id());
      if (at !== undefined && at <= upTo) n.addClass("knows");
      else n.removeClass("knows");
    });
  }

  function stepsSeries(knowsAt, upTo) {
    const series = [];
    for (let i = 0; i <= upTo; i++) {
      let c = 0;
      for (const s of knowsAt.values()) if (s <= i) c++;
      series.push(c);
    }
    return series;
  }

  function maxStepOf(knowsAt) {
    let m = 0;
    for (const s of knowsAt.values()) if (s > m) m = s;
    return m;
  }

  if (mode === "explore") {
    controls.innerHTML =
      `<div class="diff-row">` +
        `<label class="diff-slider">Prag contact <output>${shared.threshold}</output>` +
        `<input type="range" min="5" max="80" value="${shared.threshold}" step="5"/></label>` +
        `<div class="diff-count">0 / ${total} știu</div>` +
      `</div>` +
      `<div class="diff-row diff-buttons">` +
        `<button type="button" class="btn btn--primary" data-act="play">Reia pas cu pas</button>` +
        `<button type="button" class="btn btn--ghost" data-act="final">Doar starea finală</button>` +
        `<button type="button" class="btn btn--ghost" data-act="random">Sursă aleatoare, ascunsă</button>` +
        `<button type="button" class="btn btn--ghost" data-act="reset">Resetează</button>` +
      `</div>` +
      `<svg class="diff-curve" width="100%" height="50" aria-hidden="true"></svg>` +
      `<div class="diff-hint" data-role="hint">Atinge un nod pentru a alege sursa.</div>`;

    const slider = controls.querySelector('input[type="range"]');
    const out = controls.querySelector("output");
    const countEl = controls.querySelector(".diff-count");
    const curveEl = controls.querySelector(".diff-curve");
    const hintEl = controls.querySelector('[data-role="hint"]');

    let source = shared.sourceId && nodes.some((n) => n.id === shared.sourceId) ? shared.sourceId : null;
    let sourceHidden = false;
    let knowsAt = new Map();

    function setCount(c) { countEl.textContent = `${c} / ${total} știu`; }
    function highlightSource(show) {
      cy.nodes().removeClass("source");
      if (show && source) {
        const n = cy.getElementById(source);
        if (n && n.length) n.addClass("source");
      }
    }
    function refreshSim() {
      if (!source) return;
      knowsAt = simulate(nodes, edges, source, shared.threshold);
    }

    slider.addEventListener("input", () => {
      shared.threshold = parseInt(slider.value, 10);
      out.textContent = shared.threshold;
      clearAnim();
      cy.nodes().removeClass("knows");
      setCount(0);
      curveEl.innerHTML = "";
      refreshSim();
      if (!sourceHidden) highlightSource(true);
    });

    cy.on("tap", "node", (e) => {
      source = e.target.id();
      shared.sourceId = source;
      sourceHidden = false;
      hintEl.textContent = `Sursă aleasă: elev ${source}. Apasă „Reia pas cu pas”.`;
      highlightSource(true);
      refreshSim();
    });

    controls.querySelector('[data-act="random"]').addEventListener("click", () => {
      const r = nodes[Math.floor(Math.random() * nodes.length)];
      source = r.id;
      shared.sourceId = source;
      sourceHidden = true;
      hintEl.textContent = "Sursă aleatoare aleasă. E ascunsă — poți ghici cine e după difuzie.";
      cy.nodes().removeClass("source");
      refreshSim();
    });

    controls.querySelector('[data-act="play"]').addEventListener("click", () => {
      if (!source) { hintEl.textContent = "Alege o sursă mai întâi."; return; }
      refreshSim();
      const maxStep = maxStepOf(knowsAt);
      clearAnim();
      cy.nodes().removeClass("knows");
      let step = 0;
      drawUpToStep(knowsAt, step);
      setCount(1);
      drawCurve(curveEl, stepsSeries(knowsAt, step), total);
      animTimer = setInterval(() => {
        step++;
        drawUpToStep(knowsAt, step);
        let c = 0;
        for (const s of knowsAt.values()) if (s <= step) c++;
        setCount(c);
        drawCurve(curveEl, stepsSeries(knowsAt, step), total);
        if (step >= maxStep) {
          clearAnim();
          if (!sourceHidden) highlightSource(true);
        }
      }, 500);
    });

    controls.querySelector('[data-act="final"]').addEventListener("click", () => {
      if (!source) { hintEl.textContent = "Alege o sursă mai întâi."; return; }
      clearAnim();
      refreshSim();
      const maxStep = maxStepOf(knowsAt);
      drawUpToStep(knowsAt, maxStep);
      setCount(knowsAt.size);
      drawCurve(curveEl, stepsSeries(knowsAt, maxStep), total);
      if (!sourceHidden) highlightSource(true);
    });

    controls.querySelector('[data-act="reset"]').addEventListener("click", () => {
      clearAnim();
      cy.nodes().removeClass("knows source");
      setCount(0);
      curveEl.innerHTML = "";
      hintEl.textContent = "Atinge un nod pentru a alege sursa.";
      source = null;
      shared.sourceId = null;
      refit();
    });

    if (source) highlightSource(true);
  }

  else if (mode === "final-only") {
    let source = shared.sourceId && nodes.some((n) => n.id === shared.sourceId)
      ? shared.sourceId
      : nodes[Math.floor(Math.random() * nodes.length)].id;
    shared.sourceId = source;
    const knowsAt = simulate(nodes, edges, source, shared.threshold);
    drawUpToStep(knowsAt, maxStepOf(knowsAt));

    controls.innerHTML =
      `<div class="diff-row">` +
        `<div class="diff-count">${knowsAt.size} / ${total} știu zvonul</div>` +
      `</div>` +
      `<div class="diff-row diff-buttons">` +
        `<button type="button" class="btn btn--primary" data-act="reveal">Dezvăluie ordinea</button>` +
      `</div>` +
      `<div class="diff-hint">Sursa nu este marcată. Poți ghici doar uitându-te?</div>`;

    controls.querySelector('[data-act="reveal"]').addEventListener("click", () => {
      if (typeof options.onAdvance === "function") options.onAdvance();
    });
  }

  else if (mode === "replay-order") {
    let source = shared.sourceId && nodes.some((n) => n.id === shared.sourceId)
      ? shared.sourceId
      : nodes[Math.floor(Math.random() * nodes.length)].id;
    shared.sourceId = source;
    const knowsAt = simulate(nodes, edges, source, shared.threshold);
    const maxStep = maxStepOf(knowsAt);

    controls.innerHTML =
      `<div class="diff-row">` +
        `<div class="diff-count">0 / ${knowsAt.size} știu</div>` +
      `</div>` +
      `<div class="diff-row diff-buttons">` +
        `<button type="button" class="btn btn--ghost" data-act="replay">Reia din nou</button>` +
      `</div>` +
      `<svg class="diff-curve" width="100%" height="50" aria-hidden="true"></svg>` +
      `<div class="diff-hint">Primul care se aprinde este sursa.</div>`;

    const countEl = controls.querySelector(".diff-count");
    const curveEl = controls.querySelector(".diff-curve");

    function play() {
      clearAnim();
      cy.nodes().removeClass("knows source");
      curveEl.innerHTML = "";
      countEl.textContent = `0 / ${knowsAt.size} știu`;
      let step = 0;
      drawUpToStep(knowsAt, 0);
      countEl.textContent = `1 / ${knowsAt.size} știu`;
      drawCurve(curveEl, stepsSeries(knowsAt, 0), knowsAt.size);
      animTimer = setInterval(() => {
        step++;
        drawUpToStep(knowsAt, step);
        let c = 0;
        for (const s of knowsAt.values()) if (s <= step) c++;
        countEl.textContent = `${c} / ${knowsAt.size} știu`;
        drawCurve(curveEl, stepsSeries(knowsAt, step), knowsAt.size);
        if (step >= maxStep) {
          clearAnim();
          const n = cy.getElementById(String(source));
          if (n && n.length) n.addClass("source");
        }
      }, 500);
    }

    controls.querySelector('[data-act="replay"]').addEventListener("click", play);
    setTimeout(play, 500);
  }

  else if (mode === "investigation") {
    cy.nodes().addClass("knows");

    controls.innerHTML =
      `<div class="diff-row diff-buttons">` +
        `<button type="button" class="btn btn--ghost" data-metric="degree">Cele mai multe contacte</button>` +
        `<button type="button" class="btn btn--ghost" data-metric="wdegree">Cel mai mult timp petrecut</button>` +
        `<button type="button" class="btn btn--ghost" data-metric="between">Punte între clase</button>` +
        `<button type="button" class="btn btn--ghost" data-metric="spread">Cel mai bun răspânditor</button>` +
      `</div>` +
      `<div class="diff-hint" data-role="value">Apasă o măsură pentru a evidenția nodul de top.</div>`;

    const valueEl = controls.querySelector('[data-role="value"]');

    function computeTop(metric) {
      if (metric === "degree") {
        let bestId = null, bv = -1;
        cy.nodes().forEach((n) => {
          const d = n.connectedEdges().length;
          if (d > bv) { bv = d; bestId = n.id(); }
        });
        return { id: bestId, label: `${bv} contacte` };
      }
      if (metric === "wdegree") {
        let bestId = null, bv = -1;
        cy.nodes().forEach((n) => {
          let s = 0;
          n.connectedEdges().forEach((e) => { s += e.data("weight") || 0; });
          if (s > bv) { bv = s; bestId = n.id(); }
        });
        return { id: bestId, label: `${bv} întâlniri (suma ponderilor)` };
      }
      if (metric === "between") {
        const bc = cy.elements().betweennessCentrality({ directed: false });
        let bestId = null, bv = -1;
        cy.nodes().forEach((n) => {
          const v = bc.betweenness(n);
          if (v > bv) { bv = v; bestId = n.id(); }
        });
        return { id: bestId, label: `centralitate de intermediere ${Math.round(bv)}` };
      }
      if (metric === "spread") {
        let bestId = null, bv = -1;
        for (const n of nodes) {
          const k = simulate(nodes, edges, n.id, shared.threshold);
          if (k.size > bv) { bv = k.size; bestId = n.id; }
        }
        return { id: bestId, label: `ajunge la ${bv} elevi la prag ${shared.threshold}` };
      }
      return null;
    }

    controls.querySelectorAll("[data-metric]").forEach((btn) => {
      btn.addEventListener("click", () => {
        cy.nodes().removeClass("top");
        const res = computeTop(btn.dataset.metric);
        if (res && res.id) {
          const n = cy.getElementById(res.id);
          if (n && n.length) n.addClass("top");
          valueEl.textContent = `Elev ${res.id}: ${res.label}`;
        }
      });
    });
  }

  return {
    refit,
    destroy() {
      clearAnim();
      window.removeEventListener("resize", onWin);
      ro.disconnect();
      try { cy.destroy(); } catch { /* ignore */ }
    }
  };
}
