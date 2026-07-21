const V = new URL(import.meta.url).searchParams.get("v") || "1";
const { loadCytoscape, GROUP_PALETTE } = await import(`./visualizations.js?v=${V}`);

// Shared state so successive slides can use the same source/threshold.
const shared = {
  sourceId: null,
  threshold: 3,
  networkKey: null,
  network: null
};

export function setShared(partial) {
  if (!partial) return;
  if (partial.sourceId !== undefined) shared.sourceId = partial.sourceId;
  if (partial.threshold !== undefined) shared.threshold = partial.threshold;
}

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
      style: {
        "border-color": "#2a1f16",
        "border-width": 3,
        "width": 28,
        "height": 28,
        "label": "data(label)",
        "font-family": "Georgia, serif",
        "font-size": 13,
        "color": "#2a1f16",
        "text-background-color": "#faf7f2",
        "text-background-opacity": 0.9,
        "text-background-padding": 3,
        "text-valign": "bottom",
        "text-margin-y": 6
      }
    },
    {
      selector: "node.top",
      style: {
        "opacity": 1,
        "border-color": "#2a1f16",
        "border-width": 3,
        "width": 30,
        "height": 30,
        "label": "data(label)",
        "font-family": "Georgia, serif",
        "font-size": 13,
        "color": "#2a1f16",
        "text-background-color": "#faf7f2",
        "text-background-opacity": 0.9,
        "text-background-padding": 3,
        "text-valign": "bottom",
        "text-margin-y": 6
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

async function renderCompareThree(container, block) {
  container.classList.add("viz");
  container.innerHTML = "";
  let cytoscape, data;
  try {
    [cytoscape, data] = await Promise.all([
      loadCytoscape(),
      loadJSON(block.data || "data/highschool-three-networks.json")
    ]);
  } catch (err) { return errorHandle(container, err.message); }

  const sources = block.sources || [
    { key: "sensor",     title: "Senzori (proximitate fizică)" },
    { key: "diaries",    title: "Chestionar (jurnal declarat)" },
    { key: "friendship", title: "Prietenie declarată" }
  ];
  const nodes = data.nodes.map((n) => ({
    id: String(n.id), name: n.name != null ? String(n.name) : null, group: n.group || ""
  }));
  const nameById = new Map(nodes.map((n) => [n.id, n.name || `Elev ${n.id}`]));

  // pick 8 focus students who appear in all sources (highest degree overall)
  const inAll = new Set(nodes.map((n) => n.id));
  const degOverall = new Map();
  for (const src of sources) {
    for (const e of (data[src.key] || [])) {
      degOverall.set(String(e.source), (degOverall.get(String(e.source)) || 0) + 1);
      degOverall.set(String(e.target), (degOverall.get(String(e.target)) || 0) + 1);
    }
  }
  const focus = new Set([...inAll].sort((a, b) => (degOverall.get(b) || 0) - (degOverall.get(a) || 0)).slice(0, 8));

  const grid = document.createElement("div");
  grid.className = "compare-three";
  container.appendChild(grid);

  const groups = [...new Set(nodes.map((n) => n.group).filter(Boolean))];
  const colorMap = new Map();
  groups.forEach((g, i) => colorMap.set(g, GROUP_PALETTE[i % GROUP_PALETTE.length]));
  const cyInstances = [];

  for (const src of sources) {
    const cell = document.createElement("div");
    cell.className = "compare-three__cell";
    const cap = document.createElement("div");
    cap.className = "compare-three__cap";
    cap.textContent = src.title;
    cell.appendChild(cap);
    const stage = document.createElement("div");
    stage.className = "compare-three__stage";
    cell.appendChild(stage);
    const foot = document.createElement("div");
    foot.className = "compare-three__foot";
    cell.appendChild(foot);
    grid.appendChild(cell);

    const edges = (data[src.key] || []).map((e, i) => ({ id: `${src.key}-e${i}`, source: String(e.source), target: String(e.target) }));
    const elements = [
      ...nodes.map((n) => ({ data: { id: n.id, label: n.name, name: n.name, color: colorMap.get(n.group) || GROUP_PALETTE[0] }, classes: focus.has(n.id) ? "focus" : "" })),
      ...edges.map((e) => ({ data: { id: e.id, source: e.source, target: e.target } }))
    ];
    const cy = cytoscape({
      container: stage,
      elements,
      style: [
        { selector: "node", style: { "background-color": "data(color)", "width": 10, "height": 10, "opacity": 0.4 } },
        { selector: "node.focus", style: { "width": 16, "height": 16, "border-width": 1, "border-color": "#2a1f16", "opacity": 1, "label": "data(label)", "font-size": 9, "text-valign": "bottom", "text-margin-y": 4, "color": "#2a1f16", "text-background-color": "#faf7f2", "text-background-opacity": 0.9 } },
        { selector: "edge", style: { "line-color": "#b57140", "opacity": 0.35, "width": 1, "curve-style": "bezier" } }
      ],
      layout: { name: "cose", animate: false, padding: 12, idealEdgeLength: 40, nodeRepulsion: 3000 },
      minZoom: 0.3, maxZoom: 2, wheelSensitivity: 0.2
    });
    cy.style().update();
    foot.textContent = `${edges.length} legături`;
    cyInstances.push(cy);
  }

  function refit() { cyInstances.forEach((cy) => { try { cy.resize(); cy.fit(undefined, 12); } catch {} }); }
  const onWin = () => refit();
  window.addEventListener("resize", onWin);
  const ro = new ResizeObserver(refit);
  ro.observe(grid);
  requestAnimationFrame(refit);

  return {
    refit,
    destroy() {
      window.removeEventListener("resize", onWin);
      ro.disconnect();
      cyInstances.forEach((cy) => { try { cy.destroy(); } catch {} });
    }
  };
}

export async function renderDiffusion(container, block, options = {}) {
  const mode = block.mode;

  if (mode === "compare-three") {
    return await renderCompareThree(container, block);
  }

  let cytoscape, data;
  try {
    [cytoscape, data] = await Promise.all([loadCytoscape(), getData(block)]);
  } catch (err) {
    return errorHandle(container, err.message);
  }

  const nodes = data.nodes.map((n) => {
    const name = n.name != null ? String(n.name) : null;
    return {
      id: String(n.id),
      name,
      label: name || (n.label != null ? String(n.label) : String(n.id)),
      group: n.group != null ? String(n.group) : ""
    };
  });
  const nameById = new Map(nodes.map((n) => [n.id, n.name || `Elev ${n.id}`]));
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
      data: { id: n.id, label: n.label, name: n.name, group: n.group, color: colorMap.get(n.group) || GROUP_PALETTE[0] }
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
          const who = nameById.get(res.id) || `Elev ${res.id}`;
          valueEl.textContent = `${who}: ${res.label}`;
        }
      });
    });
  }

  else if (mode === "temporal") {
    // hourly cursor + network redraw from highschool-hours.json
    let hours;
    try {
      const r = await fetch(block.hoursSource || "data/highschool-hours.json");
      hours = await r.json();
    } catch (err) { return errorHandle(container, err.message); }

    const first = hours.hours[0] || { edges: [] };
    function drawEdges(edgeList) {
      cy.edges().remove();
      const toAdd = edgeList.map((e, i) => ({
        data: { id: `h${i}`, source: String(e.source), target: String(e.target), weight: e.weight, w: 1.5 + Math.min(4, e.weight * 0.2) }
      }));
      cy.add(toAdd);
    }
    drawEdges(first.edges);

    const hrLabel = (h) => `${8 + h}:00`;
    controls.innerHTML =
      `<div class="diff-row">` +
        `<label class="diff-slider">Ora <output>${hrLabel(0)}</output>` +
        `<input type="range" min="0" max="${hours.hours.length - 1}" value="0" step="1"/></label>` +
        `<div class="diff-count">${first.edges.length} legături active</div>` +
      `</div>` +
      `<div class="diff-hint">În ore de curs contactele se restrâng; în pauze explodează.</div>`;

    const slider = controls.querySelector('input[type="range"]');
    const out    = controls.querySelector("output");
    const countEl = controls.querySelector(".diff-count");
    slider.addEventListener("input", () => {
      const idx = parseInt(slider.value, 10);
      const snap = hours.hours[idx] || { edges: [] };
      out.textContent = hrLabel(idx);
      drawEdges(snap.edges);
      countEl.textContent = `${snap.edges.length} legături active`;
      refit();
    });
  }

  else if (mode === "sir") {
    // probabilistic SIR: pT=0.10, pS=0.20 calibrated for bimodal outcomes.
    const P_T = block.pTransmit ?? 0.10;
    const P_S = block.pStop ?? 0.20;
    const sourceId = shared.sourceId && nodes.some((n) => n.id === shared.sourceId)
      ? shared.sourceId
      : (nodes.find((n) => n.name === "Octav")?.id || nodes[0].id);
    shared.sourceId = sourceId;

    const adj = new Map();
    for (const n of nodes) adj.set(n.id, []);
    for (const e of edges) {
      adj.get(e.source)?.push(e.target);
      adj.get(e.target)?.push(e.source);
    }

    function runSIR() {
      const state = new Map();
      for (const n of nodes) state.set(n.id, "S");
      state.set(sourceId, "I");
      const history = [];
      let step = 0;
      while (step < 100) {
        const carriers = [];
        for (const [id, s] of state) if (s === "I") carriers.push(id);
        if (!carriers.length) break;
        const newI = [];
        for (const c of carriers) {
          for (const nb of adj.get(c) || []) {
            if (state.get(nb) === "S" && Math.random() < P_T) newI.push(nb);
          }
        }
        for (const nb of newI) state.set(nb, "I");
        for (const c of carriers) if (Math.random() < P_S) state.set(c, "R");
        step++;
        history.push({ knows: [...state].filter(([, s]) => s !== "S").map(([id]) => id) });
      }
      let known = 0;
      for (const s of state.values()) if (s !== "S") known++;
      return { finalKnow: known, history, state };
    }

    controls.innerHTML =
      `<div class="diff-row diff-buttons">` +
        `<button type="button" class="btn btn--primary" data-act="once">Rulează o dată</button>` +
        `<button type="button" class="btn btn--ghost" data-act="hundred">Rulează de 100 de ori</button>` +
      `</div>` +
      `<div class="diff-count" data-role="last">Sursă: ${nameById.get(sourceId) || sourceId}. Fiecare rulare are alt viitor.</div>` +
      `<div class="diff-hint">p transmitere ${P_T} · p stingere ${P_S}. Sursa: ${nameById.get(sourceId) || sourceId}.</div>` +
      `<svg class="diff-outcome" width="100%" height="120" aria-hidden="true" viewBox="0 0 480 120" preserveAspectRatio="none" style="background:var(--color-surface-alt);border-radius:var(--radius-sm);margin-top:var(--sp-2);display:none"></svg>`;

    const lastEl = controls.querySelector('[data-role="last"]');
    const outcomeSvg = controls.querySelector(".diff-outcome");

    async function animateRun(res) {
      clearAnim();
      cy.nodes().removeClass("knows source");
      const src = cy.getElementById(sourceId);
      if (src && src.length) src.addClass("source");
      let step = 0;
      const maxStep = res.history.length;
      animTimer = setInterval(() => {
        const snap = res.history[step];
        if (!snap) { clearAnim(); return; }
        cy.nodes().removeClass("knows");
        for (const id of snap.knows) {
          const n = cy.getElementById(id);
          if (n && n.length) n.addClass("knows");
        }
        step++;
        if (step >= maxStep) { clearAnim(); lastEl.textContent = `Acoperire finală: ${res.finalKnow} din ${total}.`; }
      }, 350);
    }

    controls.querySelector('[data-act="once"]').addEventListener("click", () => {
      const res = runSIR();
      animateRun(res);
    });

    controls.querySelector('[data-act="hundred"]').addEventListener("click", () => {
      const outcomes = [];
      for (let i = 0; i < 100; i++) outcomes.push(runSIR().finalKnow);
      const bw = 5;
      const bins = new Array(Math.ceil(total / bw)).fill(0);
      for (const v of outcomes) {
        const idx = Math.min(bins.length - 1, Math.floor(v / bw));
        bins[idx]++;
      }
      const W = 480, H = 120, pad = 6;
      const chartW = W - pad * 2;
      const maxC = Math.max(...bins, 1);
      const barW = chartW / bins.length;
      const bars = bins.map((c, i) => {
        const x = pad + i * barW;
        const h = (c / maxC) * (H - 24);
        const y = H - 4 - h;
        return `<rect x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${(barW - 1).toFixed(1)}" height="${h.toFixed(1)}" fill="#8b4a1e"/>` +
               `<text x="${(x + barW/2).toFixed(1)}" y="${H - 1}" text-anchor="middle" font-size="9" fill="#8a7a68">${i * bw}</text>`;
      }).join("");
      outcomeSvg.innerHTML = `<text x="6" y="12" font-size="10" fill="#5a4a3a">100 rulări · acoperire finală</text>` + bars;
      outcomeSvg.style.display = "block";
      const mean = outcomes.reduce((a, b) => a + b, 0) / outcomes.length;
      const died = outcomes.filter((v) => v < 5).length;
      lastEl.textContent = `Din 100 rulări: medie ${mean.toFixed(1)} · ${died} rulări au murit sub 5 elevi.`;
    });
  }

  else if (mode === "game") {
    // 3 attempts: user taps a source, deterministic BFS scores, then heatmap of top spreads
    let attempts = 0;
    const maxAttempts = block.attempts || 3;
    const bestPossible = block.bestPossible || (function () {
      let bp = 0;
      for (const n of nodes) {
        const k = simulate(nodes, edges, n.id, shared.threshold || 3);
        if (k.size > bp) bp = k.size;
      }
      return bp;
    })();

    cy.nodes().addClass("knows");
    controls.innerHTML =
      `<div class="diff-hint" data-role="status">Atinge un elev pe rețea — pornim zvonul de acolo.</div>` +
      `<div class="diff-count" data-role="scores"></div>` +
      `<div class="diff-row diff-buttons" data-role="final" hidden>` +
        `<button type="button" class="btn btn--primary" data-act="reveal">Clasamentul complet</button>` +
      `</div>`;

    const statusEl = controls.querySelector('[data-role="status"]');
    const scoresEl = controls.querySelector('[data-role="scores"]');
    const finalBar = controls.querySelector('[data-role="final"]');
    const scores = [];

    cy.on("tap", "node", (e) => {
      if (attempts >= maxAttempts) return;
      const id = e.target.id();
      const k = simulate(nodes, edges, id, shared.threshold || 3);
      attempts++;
      scores.push({ id, size: k.size });
      cy.nodes().removeClass("source top");
      e.target.addClass("source");
      cy.nodes().forEach((n) => { n.removeClass("knows"); if (k.has(n.id())) n.addClass("knows"); });
      statusEl.textContent = `Încercarea ${attempts}/${maxAttempts}: ${nameById.get(id) || id} atinge ${k.size} din ${total}. Recordul posibil: ${bestPossible}.`;
      scoresEl.textContent = scores.map((s, i) => `#${i+1}: ${s.size}`).join(" · ");
      if (attempts >= maxAttempts) {
        finalBar.hidden = false;
        statusEl.textContent += " Ai epuizat încercările.";
      }
    });

    controls.querySelector('[data-act="reveal"]').addEventListener("click", () => {
      // heatmap: color nodes by their spread rank
      const rankings = nodes.map((n) => ({ id: n.id, size: simulate(nodes, edges, n.id, shared.threshold || 3).size }));
      const maxSize = Math.max(...rankings.map((r) => r.size), 1);
      cy.nodes().removeClass("source top knows");
      rankings.forEach((r) => {
        const n = cy.getElementById(r.id);
        if (!n || !n.length) return;
        const t = r.size / maxSize;
        // heatmap color: from muted grey (low) to strong brown (high)
        const R = Math.round(217 * (1 - t) + 139 * t);
        const G = Math.round(207 * (1 - t) + 74  * t);
        const B = Math.round(192 * (1 - t) + 30  * t);
        n.style("background-color", `rgb(${R},${G},${B})`);
        n.style("opacity", 0.4 + 0.6 * t);
      });
      statusEl.textContent = "Culoarea = câți atinge fiecare elev, pornind de acolo.";
    });
  }

  else if (mode === "majority") {
    // interactive majority illusion: user picks how many seeds, sees pct exposed
    const nodesSortedByDegree = [...nodes].sort((a, b) => {
      const da = (edges.filter((e) => e.source === a.id || e.target === a.id)).length;
      const db = (edges.filter((e) => e.source === b.id || e.target === b.id)).length;
      return db - da;
    });
    const adjSet = new Map();
    for (const n of nodes) adjSet.set(n.id, new Set());
    for (const e of edges) { adjSet.get(e.source).add(e.target); adjSet.get(e.target).add(e.source); }

    function seedFor(k) { return new Set(nodesSortedByDegree.slice(0, k).map((n) => n.id)); }
    function computePct(k) {
      const seed = seedFor(k);
      let withNb = 0, exposed = 0;
      for (const n of nodes) {
        const nbs = adjSet.get(n.id);
        if (!nbs.size) continue;
        withNb++;
        let seen = 0;
        for (const x of nbs) if (seed.has(x)) seen++;
        if (seen / nbs.size >= 0.5) exposed++;
      }
      return { withNb, exposed, seed };
    }

    function paint(k, showExposed) {
      const { seed } = computePct(k);
      cy.nodes().removeClass("source top knows");
      cy.nodes().forEach((n) => {
        if (seed.has(n.id())) n.addClass("source");
        else n.addClass("knows");
      });
      if (showExposed) {
        // dim non-exposed nodes further
        cy.nodes().forEach((n) => {
          if (seed.has(n.id())) return;
          const nbs = adjSet.get(n.id());
          if (!nbs || !nbs.size) return;
          let seen = 0;
          for (const x of nbs) if (seed.has(x)) seen++;
          if (seen / nbs.size >= 0.5) n.style("border-color", "#2a1f16").style("border-width", 2);
        });
      }
    }

    const initialK = 4;
    controls.innerHTML =
      `<div class="diff-row">` +
        `<label class="diff-slider">Câți elevi „știu" <output>${initialK}</output>` +
        `<input type="range" min="1" max="20" value="${initialK}" step="1"/></label>` +
      `</div>` +
      `<div class="diff-count" data-role="pct">–</div>` +
      `<div class="diff-hint" data-role="tap">Atinge orice alt elev: vezi câți dintre vecinii lui sunt „informați".</div>`;

    const slider = controls.querySelector('input[type="range"]');
    const out    = controls.querySelector("output");
    const pctEl  = controls.querySelector('[data-role="pct"]');
    const tapEl  = controls.querySelector('[data-role="tap"]');

    function update(k) {
      const { withNb, exposed, seed } = computePct(k);
      const pct = withNb ? (100 * exposed / withNb).toFixed(0) : "0";
      pctEl.textContent = `${pct}% dintre elevi văd majoritatea prietenilor „știind" (deși doar ${k} din ${total} știu de fapt).`;
      paint(k, true);
      return { pct, seed };
    }
    slider.addEventListener("input", () => {
      out.textContent = slider.value;
      update(parseInt(slider.value, 10));
    });
    update(initialK);

    cy.on("tap", "node", (e) => {
      const k = parseInt(slider.value, 10);
      const seed = seedFor(k);
      const nid = e.target.id();
      if (seed.has(nid)) { tapEl.textContent = `${nameById.get(nid)} e chiar unul dintre cei informați.`; return; }
      const nbs = adjSet.get(nid);
      if (!nbs || !nbs.size) { tapEl.textContent = `${nameById.get(nid)} nu are vecini în felie.`; return; }
      let seen = 0;
      for (const x of nbs) if (seed.has(x)) seen++;
      tapEl.textContent = `${nameById.get(nid)}: ${seen} din ${nbs.size} vecini știu zvonul (${(100 * seen / nbs.size).toFixed(0)}%).`;
    });
  }

  else if (mode === "path") {
    // pick 2 nodes → shortest path
    let pickA = null, pickB = null;
    const adjMap = new Map();
    for (const n of nodes) adjMap.set(n.id, []);
    for (const e of edges) { adjMap.get(e.source).push(e.target); adjMap.get(e.target).push(e.source); }

    function bfs(src, dst) {
      const prev = new Map(); prev.set(src, null);
      const q = [src];
      while (q.length) {
        const x = q.shift();
        if (x === dst) break;
        for (const nb of adjMap.get(x) || []) {
          if (!prev.has(nb)) { prev.set(nb, x); q.push(nb); }
        }
      }
      if (!prev.has(dst)) return null;
      const path = [dst];
      while (prev.get(path[0]) != null) path.unshift(prev.get(path[0]));
      return path;
    }

    controls.innerHTML =
      `<div class="diff-hint" data-role="hint">Atinge doi elevi — trasez cel mai scurt drum între ei.</div>` +
      `<div class="diff-count" data-role="len"></div>` +
      `<div class="diff-row diff-buttons"><button type="button" class="btn btn--ghost" data-act="reset">Alegere nouă</button></div>`;

    const hintEl = controls.querySelector('[data-role="hint"]');
    const lenEl  = controls.querySelector('[data-role="len"]');
    function clearAll() {
      cy.nodes().removeClass("source top knows");
      cy.edges().removeClass("neighbor-edge");
      pickA = null; pickB = null;
      hintEl.textContent = "Atinge doi elevi — trasez cel mai scurt drum între ei.";
      lenEl.textContent = "";
    }

    cy.on("tap", "node", (e) => {
      const id = e.target.id();
      if (!pickA) {
        pickA = id;
        e.target.addClass("source");
        hintEl.textContent = `Ai ales pe ${nameById.get(id) || id}. Alege al doilea.`;
      } else if (!pickB && id !== pickA) {
        pickB = id;
        e.target.addClass("source");
        const path = bfs(pickA, pickB);
        if (!path) {
          hintEl.textContent = "Nu există drum între cei doi elevi (componente separate).";
          return;
        }
        for (const nid of path) cy.getElementById(nid).addClass("knows");
        // highlight edges on path
        for (let i = 0; i < path.length - 1; i++) {
          const es = cy.edges(`[source="${path[i]}"][target="${path[i+1]}"], [source="${path[i+1]}"][target="${path[i]}"]`);
          es.addClass("neighbor-edge");
        }
        lenEl.textContent = `Drum de lungime ${path.length - 1} pași: ${path.map((id) => nameById.get(id) || id).join(" → ")}.`;
      }
    });
    controls.querySelector('[data-act="reset"]').addEventListener("click", clearAll);
  }

  else if (mode === "photo-film") {
    // hidden source, show final state; user taps guess; button reveals film + verdict
    const hiddenSourceId = block.hiddenSourceId
      || (nodes.find((n) => n.name === "Denis")?.id
        || nodes.find((n) => n.name === "Bianca")?.id
        || nodes[0].id);
    const threshold = shared.threshold || 3;
    const knowsAt = simulate(nodes, edges, hiddenSourceId, threshold);
    drawUpToStep(knowsAt, maxStepOf(knowsAt));

    let guessId = null;
    controls.innerHTML =
      `<div class="diff-hint" data-role="hint">Iată rezultatul final. Atinge nodul pe care îl bănuiești sursă.</div>` +
      `<div class="diff-count" data-role="guess"></div>` +
      `<div class="diff-row diff-buttons">` +
        `<button type="button" class="btn btn--primary" data-act="film" disabled>Derulează filmul</button>` +
      `</div>` +
      `<svg class="diff-curve" width="100%" height="50" aria-hidden="true"></svg>` +
      `<div class="diff-hint" data-role="verdict"></div>`;

    const hintEl = controls.querySelector('[data-role="hint"]');
    const guessEl = controls.querySelector('[data-role="guess"]');
    const filmBtn = controls.querySelector('[data-act="film"]');
    const curveEl = controls.querySelector(".diff-curve");
    const verdictEl = controls.querySelector('[data-role="verdict"]');

    cy.on("tap", "node", (e) => {
      const id = e.target.id();
      if (!knowsAt.has(id)) {
        guessEl.textContent = `${nameById.get(id) || id} nu apare în starea finală — nu are cum să fi fost sursa.`;
        return;
      }
      guessId = id;
      cy.nodes().removeClass("source top");
      e.target.addClass("top");
      guessEl.textContent = `Bănuit: ${nameById.get(id) || id}.`;
      filmBtn.disabled = false;
    });

    filmBtn.addEventListener("click", () => {
      const maxStep = maxStepOf(knowsAt);
      clearAnim();
      cy.nodes().removeClass("knows source top");
      let step = 0;
      drawUpToStep(knowsAt, 0);
      drawCurve(curveEl, stepsSeries(knowsAt, 0), knowsAt.size);
      animTimer = setInterval(() => {
        step++;
        drawUpToStep(knowsAt, step);
        drawCurve(curveEl, stepsSeries(knowsAt, step), knowsAt.size);
        if (step >= maxStep) {
          clearAnim();
          const src = cy.getElementById(hiddenSourceId);
          if (src && src.length) src.addClass("source");
          const correct = guessId === hiddenSourceId;
          verdictEl.textContent = correct
            ? `Ai nimerit. Sursa a fost ${nameById.get(hiddenSourceId) || hiddenSourceId}.`
            : `Nu era ${nameById.get(guessId) || guessId} — sursa a fost ${nameById.get(hiddenSourceId) || hiddenSourceId}. Din fotografie nu poți fi sigur.`;
        }
      }, 400);
    });
  }

  else if (mode === "recolor-sex") {
    // recolor nodes by sex
    cy.nodes().addClass("knows");
    const sexMap = new Map();
    for (const n of data.nodes) sexMap.set(String(n.id), n.sex || "Unknown");
    const palette = { F: "#3d7a52", M: "#8b4a1e", Unknown: "#8a7a68" };
    cy.nodes().forEach((n) => {
      const s = sexMap.get(n.id()) || "Unknown";
      n.style("background-color", palette[s] || palette.Unknown);
    });
    legend.innerHTML =
      `<span class="viz__legend-chip"><span class="viz__legend-dot" style="background:${palette.F}"></span>fete</span>` +
      `<span class="viz__legend-chip"><span class="viz__legend-dot" style="background:${palette.M}"></span>băieți</span>` +
      `<span class="viz__legend-chip"><span class="viz__legend-dot" style="background:${palette.Unknown}"></span>necunoscut</span>`;

    controls.innerHTML =
      `<div class="diff-hint">Aceleași noduri, alt criteriu de colorare. Priveşte contactele și vezi cum se aleg vecinii — sau nu.</div>`;
  }

  else if (mode === "highlight") {
    cy.nodes().addClass("knows");
    const metric = block.metric || "degree";

    function topByMetric(m) {
      if (m === "degree") {
        let bestId = null, bv = -1, ranked = [];
        cy.nodes().forEach((n) => {
          const d = n.connectedEdges().length;
          ranked.push({ id: n.id(), v: d });
          if (d > bv) { bv = d; bestId = n.id(); }
        });
        ranked.sort((a, b) => b.v - a.v);
        return { id: bestId, value: bv, label: `${bv} contacte`, runners: ranked.slice(1, 3) };
      }
      if (m === "wdegree") {
        let bestId = null, bv = -1, ranked = [];
        cy.nodes().forEach((n) => {
          let s = 0;
          n.connectedEdges().forEach((e) => { s += e.data("weight") || 0; });
          ranked.push({ id: n.id(), v: s });
          if (s > bv) { bv = s; bestId = n.id(); }
        });
        ranked.sort((a, b) => b.v - a.v);
        return { id: bestId, value: bv, label: `${bv} întâlniri (sumă ponderi)`, runners: ranked.slice(1, 3) };
      }
      if (m === "between") {
        const bc = cy.elements().betweennessCentrality({ directed: false });
        let bestId = null, bv = -1, ranked = [];
        cy.nodes().forEach((n) => {
          const v = bc.betweenness(n);
          ranked.push({ id: n.id(), v });
          if (v > bv) { bv = v; bestId = n.id(); }
        });
        ranked.sort((a, b) => b.v - a.v);
        return { id: bestId, value: Math.round(bv), label: `intermediere ${Math.round(bv)}`, runners: ranked.slice(1, 3) };
      }
      if (m === "spread") {
        let bestId = null, bv = -1, ranked = [];
        for (const n of nodes) {
          const k = simulate(nodes, edges, n.id, shared.threshold);
          ranked.push({ id: n.id, v: k.size });
          if (k.size > bv) { bv = k.size; bestId = n.id; }
        }
        ranked.sort((a, b) => b.v - a.v);
        return { id: bestId, value: bv, label: `ajunge la ${bv} elevi`, runners: ranked.slice(1, 3) };
      }
      return null;
    }

    const res = topByMetric(metric);
    if (res && res.id) {
      const n = cy.getElementById(res.id);
      if (n && n.length) n.addClass("top");
      const who = nameById.get(res.id) || `Elev ${res.id}`;
      const runnersText = (res.runners || [])
        .map((r) => nameById.get(r.id) || `Elev ${r.id}`)
        .join(", ");
      controls.innerHTML =
        `<div class="diff-hint"><strong>${who}</strong> — ${res.label}</div>` +
        (runnersText
          ? `<div class="diff-hint">Urmează: ${runnersText}.</div>`
          : "");
    } else {
      controls.innerHTML = `<div class="diff-hint">Nu am putut calcula.</div>`;
    }
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
