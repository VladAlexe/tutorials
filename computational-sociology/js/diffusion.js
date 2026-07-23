const V = new URL(import.meta.url).searchParams.get("v") || "1";
const { loadCytoscape, GROUP_PALETTE, narrowCyOpts } = await import(`./visualizations.js?v=${V}`);

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
        "width": 9,
        "height": 9,
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
        "width": 0.8,
        "opacity": 0.35,
        "curve-style": "bezier"
      }
    },
    { selector: "node.knows", style: { "opacity": 1, "width": 11, "height": 11 } },
    {
      selector: "node.source",
      style: {
        "border-color": "#2a1f16",
        "border-width": 2,
        "width": 20,
        "height": 20,
        "label": "data(label)",
        "font-family": "Georgia, serif",
        "font-size": 11,
        "color": "#2a1f16",
        "text-background-color": "#faf7f2",
        "text-background-opacity": 0.9,
        "text-background-padding": 3,
        "text-valign": "bottom",
        "text-margin-y": 4
      }
    },
    {
      selector: "node.top",
      style: {
        "opacity": 1,
        "border-color": "#2a1f16",
        "border-width": 2,
        "width": 22,
        "height": 22,
        "label": "data(label)",
        "font-family": "Georgia, serif",
        "font-size": 11,
        "color": "#2a1f16",
        "text-background-color": "#faf7f2",
        "text-background-opacity": 0.9,
        "text-background-padding": 3,
        "text-valign": "bottom",
        "text-margin-y": 4
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

async function renderDuel(container, block) {
  container.classList.add("viz");
  container.innerHTML = "";
  let cytoscape, data, statsData;
  try {
    [cytoscape, data] = await Promise.all([loadCytoscape(), loadJSON(block.data || "data/highschool-network.json")]);
    try { statsData = await (await fetch(block.statsSource || "data/highschool-stats.json")).json(); } catch { statsData = null; }
  } catch (err) { return errorHandle(container, err.message); }

  const trio = statsData?.sliceMetrics?.trioMission || {};
  const classNames = statsData?.classNames || {};
  const pasi = block.pasi || statsData?.sliceMetrics?.diffusionModel?.pasi || 4;
  const maxT = block.maxTransmiteri || statsData?.sliceMetrics?.diffusionModel?.maxTransmiteri || 4;

  const nodes = data.nodes.map((n) => ({ id: String(n.id), name: n.name != null ? String(n.name) : null, group: n.group || "" }));
  const edges = data.edges.map((e, i) => ({ id: `e${i}`, source: String(e.source), target: String(e.target), weight: e.weight || 1 }));

  const groups = [...new Set(nodes.map((n) => n.group).filter(Boolean))];
  const classPalette = new Map();
  groups.forEach((g, i) => classPalette.set(g, GROUP_PALETTE[i % GROUP_PALETTE.length]));

  // Build weighted-top adjacency for bounded diffusion (MIN_WEIGHT = 4).
  const MIN_W = 4;
  const adjWeighted = new Map();
  for (const n of nodes) adjWeighted.set(n.id, []);
  for (const e of edges) {
    if ((e.weight || 0) < MIN_W) continue;
    adjWeighted.get(e.source).push({ to: e.target, w: e.weight });
    adjWeighted.get(e.target).push({ to: e.source, w: e.weight });
  }
  const adjTop = new Map();
  for (const [nid, arr] of adjWeighted) {
    arr.sort((a, b) => b.w - a.w || (a.to < b.to ? -1 : 1));
    adjTop.set(nid, arr.slice(0, maxT).map((x) => x.to));
  }

  // Which trio slots to render (new keys vedeta/campion/surpriza; sandu/emil/doina kept as legacy aliases)
  const legacyAlias = { sandu: "vedeta", emil: "campion", doina: "surpriza" };
  const slots = (block.slots || ["vedeta", "campion", "surpriza"])
    .map((k) => trio[k] || trio[legacyAlias[k]])
    .filter(Boolean);
  if (!slots.length) { container.innerHTML = "<div class=\"diff-hint\">Nu am date pentru trio.</div>"; return { refit() {}, destroy() {} }; }

  const grid = document.createElement("div");
  grid.className = "duel";
  container.appendChild(grid);

  const controls = document.createElement("div");
  controls.className = "diffusion-controls";
  controls.innerHTML =
    `<div class="diff-row diff-buttons">` +
      `<button type="button" class="btn btn--primary" data-act="run">Rulează toate trei</button>` +
      `<button type="button" class="btn btn--ghost" data-act="step">Pas cu pas</button>` +
      `<button type="button" class="btn btn--ghost" data-act="reset">Resetează</button>` +
    `</div>` +
    `<div class="diff-hint" data-role="hint">Uită-te la cifrele lor înainte de a porni valurile, apoi ghicește cine câștigă.</div>`;
  container.appendChild(controls);

  const cyInstances = [];
  const knowsPer = [];
  const stepPer = [];
  const countersPer = [];

  for (const p of slots) {
    const cell = document.createElement("div");
    cell.className = "duel__cell";

    const cap = document.createElement("div");
    cap.className = "duel__cap";
    cap.innerHTML = `<strong>${p.name}</strong> <span class="duel__cap-sub">${p.classFriendly}</span>`;
    cell.appendChild(cap);

    const stats = document.createElement("div");
    stats.className = "duel__stats";
    stats.innerHTML =
      `<span><strong>${p.popularity}</strong> contacte</span>` +
      `<span><strong>${p.groups}</strong> ${p.groups === 1 ? "grup" : "grupuri"}</span>` +
      `<span class="duel__reach">rază: <strong data-role="reach">?</strong></span>`;
    cell.appendChild(stats);

    const stage = document.createElement("div");
    stage.className = "duel__stage";
    cell.appendChild(stage);
    grid.appendChild(cell);

    const elements = [
      ...nodes.map((n) => ({ data: { id: n.id, label: n.name, name: n.name, group: n.group, color: classPalette.get(n.group) || GROUP_PALETTE[0] } })),
      ...edges.map((e) => ({ data: { id: `${p.id}-${e.id}`, source: e.source, target: e.target } }))
    ];
    const cy = cytoscape({
      ...narrowCyOpts(),
      container: stage,
      elements,
      style: [
        { selector: "node", style: { "background-color": "#d9cfc0", "width": 6, "height": 6, "opacity": 0.35 } },
        { selector: "node.knows", style: { "background-color": "data(color)", "opacity": 1, "width": 10, "height": 10 } },
        { selector: "node.source", style: { "background-color": "#2a1f16", "border-color": "#2a1f16", "border-width": 2, "width": 15, "height": 15, "opacity": 1, "label": "data(label)", "font-size": 9, "text-valign": "bottom", "text-margin-y": 3, "color": "#2a1f16", "text-background-color": "#faf7f2", "text-background-opacity": 0.9 } },
        { selector: "edge", style: { "line-color": "#d9cfc0", "opacity": 0.25, "width": 0.6, "curve-style": "bezier" } }
      ],
      layout: { name: "cose", animate: false, padding: 10, idealEdgeLength: 32, nodeRepulsion: 2600 },
      minZoom: 0.3, maxZoom: 2, wheelSensitivity: 0.2
    });
    cy.style().update();
    cyInstances.push(cy);
    knowsPer.push(null);
    stepPer.push(0);
    countersPer.push(cell.querySelector('[data-role="reach"]'));

    // Highlight the source now
    const src = cy.getElementById(String(p.id));
    if (src && src.length) src.addClass("source");
  }

  function computeKnows(sourceId) {
    const known = new Map();
    known.set(String(sourceId), 0);
    let frontier = [String(sourceId)];
    for (let s = 0; s < pasi && frontier.length; s++) {
      const next = [];
      for (const x of frontier) {
        for (const y of adjTop.get(x) || []) {
          if (!known.has(y)) { known.set(y, s + 1); next.push(y); }
        }
      }
      frontier = next;
    }
    return known;
  }

  function drawUpToStep(idx, upTo) {
    const cy = cyInstances[idx];
    const knows = knowsPer[idx];
    if (!cy || !knows) return;
    cy.nodes().forEach((n) => {
      const at = knows.get(n.id());
      if (at !== undefined && at <= upTo) n.addClass("knows");
      else n.removeClass("knows");
    });
    // Update counter
    let c = 0;
    for (const s of knows.values()) if (s <= upTo) c++;
    if (countersPer[idx]) countersPer[idx].textContent = String(c);
  }

  let currentStep = 0;
  const maxSteps = pasi;

  function ensureSimulated() {
    slots.forEach((p, i) => {
      if (!knowsPer[i]) knowsPer[i] = computeKnows(p.id);
    });
  }

  function resetAll() {
    currentStep = 0;
    cyInstances.forEach((cy) => cy.nodes().removeClass("knows"));
    slots.forEach((p, i) => {
      const cy = cyInstances[i];
      const src = cy.getElementById(String(p.id));
      if (src && src.length) src.addClass("source");
      if (countersPer[i]) countersPer[i].textContent = "?";
    });
  }

  let animTimer = null;
  function stopAnim() { if (animTimer) { clearInterval(animTimer); animTimer = null; } }

  controls.querySelector('[data-act="run"]').addEventListener("click", () => {
    stopAnim();
    ensureSimulated();
    currentStep = 0;
    slots.forEach((_, i) => drawUpToStep(i, 0));
    animTimer = setInterval(() => {
      currentStep++;
      slots.forEach((_, i) => drawUpToStep(i, currentStep));
      if (currentStep >= maxSteps) stopAnim();
    }, 700);
  });
  controls.querySelector('[data-act="step"]').addEventListener("click", () => {
    stopAnim();
    ensureSimulated();
    if (currentStep >= maxSteps) return;
    currentStep++;
    slots.forEach((_, i) => drawUpToStep(i, currentStep));
  });
  controls.querySelector('[data-act="reset"]').addEventListener("click", () => {
    stopAnim();
    resetAll();
  });

  function refit() { cyInstances.forEach((cy) => { try { cy.resize(); cy.fit(undefined, 12); } catch {} }); }
  const onWin = () => refit();
  window.addEventListener("resize", onWin);
  const ro = new ResizeObserver(refit);
  ro.observe(grid);
  requestAnimationFrame(refit);

  return {
    refit,
    destroy() {
      stopAnim();
      window.removeEventListener("resize", onWin);
      ro.disconnect();
      cyInstances.forEach((cy) => { try { cy.destroy(); } catch {} });
    }
  };
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
      ...narrowCyOpts(),
      container: stage,
      elements,
      style: [
        { selector: "node", style: { "background-color": "data(color)", "width": 8, "height": 8, "opacity": 0.4 } },
        { selector: "node.focus", style: { "width": 13, "height": 13, "border-width": 1, "border-color": "#2a1f16", "opacity": 1, "label": "data(label)", "font-size": 9, "text-valign": "bottom", "text-margin-y": 4, "color": "#2a1f16", "text-background-color": "#faf7f2", "text-background-opacity": 0.9 } },
        { selector: "edge", style: { "line-color": "#b57140", "opacity": 0.35, "width": 1, "curve-style": "bezier" } }
      ],
      layout: { name: "cose", animate: false, padding: 10, idealEdgeLength: 32, nodeRepulsion: 2800 },
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

async function renderMirror(container, block) {
  container.classList.add("viz");
  container.innerHTML = "";
  let cytoscape, data, statsData;
  try {
    [cytoscape, data] = await Promise.all([loadCytoscape(), loadJSON(block.data || "data/highschool-network.json")]);
    try { statsData = await (await fetch(block.statsSource || "data/highschool-stats.json")).json(); } catch { statsData = null; }
  } catch (err) { return errorHandle(container, err.message); }

  const nodes = data.nodes.map((n) => ({ id: String(n.id), name: n.name != null ? String(n.name) : null, group: n.group || "" }));
  const edges = data.edges.map((e, i) => ({ id: `e${i}`, source: String(e.source), target: String(e.target) }));
  const commById = statsData?.sliceMetrics?.communities?.byId || {};

  const groups = [...new Set(nodes.map((n) => n.group).filter(Boolean))];
  const classPalette = new Map(); groups.forEach((g, i) => classPalette.set(g, GROUP_PALETTE[i % GROUP_PALETTE.length]));

  function colorFor(nid, scheme, groupOf) {
    if (scheme === "class") return classPalette.get(groupOf) || GROUP_PALETTE[0];
    if (scheme === "community") {
      const c = commById[nid];
      return c == null ? "#8a7a68" : GROUP_PALETTE[c % GROUP_PALETTE.length];
    }
    return "#8a7a68";
  }

  const grid = document.createElement("div");
  grid.className = "mirror";
  container.appendChild(grid);

  const toggle = document.createElement("div");
  toggle.className = "mirror__toggle";
  toggle.innerHTML =
    `<button type="button" class="btn btn--primary" data-side="left">${block.left?.title || "Stânga"}</button>` +
    `<button type="button" class="btn btn--ghost" data-side="right">${block.right?.title || "Dreapta"}</button>`;
  grid.appendChild(toggle);

  const cyInstances = [];
  const sides = ["left", "right"];
  sides.forEach((side, si) => {
    const spec = block[side] || {};
    const cell = document.createElement("div");
    cell.className = `mirror__cell mirror__cell--${side}`;
    const cap = document.createElement("div");
    cap.className = "mirror__cap";
    cap.textContent = spec.title || side;
    cell.appendChild(cap);
    const stage = document.createElement("div");
    stage.className = "mirror__stage";
    cell.appendChild(stage);
    grid.appendChild(cell);

    const scheme = spec.colorBy || "class";
    const elements = [
      ...nodes.map((n) => ({ data: { id: n.id, name: n.name, group: n.group, color: colorFor(n.id, scheme, n.group), label: n.name } })),
      ...edges.map((e) => ({ data: { id: `${side}-${e.id}`, source: e.source, target: e.target } })),
    ];
    const cy = cytoscape({
      ...narrowCyOpts(),
      container: stage,
      elements,
      style: [
        { selector: "node", style: { "background-color": "data(color)", "width": 10, "height": 10, "opacity": 0.85 } },
        { selector: "edge", style: { "line-color": "#b57140", "opacity": 0.4, "width": 1, "curve-style": "bezier" } },
      ],
      layout: { name: "cose", animate: false, padding: 12, idealEdgeLength: 40, nodeRepulsion: 3000 },
      minZoom: 0.3, maxZoom: 2, wheelSensitivity: 0.2,
    });
    cy.style().update();
    cyInstances.push(cy);
  });

  function showSide(which) {
    grid.classList.remove("mirror--left", "mirror--right");
    grid.classList.add(`mirror--${which}`);
    toggle.querySelectorAll("[data-side]").forEach((b) => {
      b.classList.remove("btn--primary"); b.classList.add("btn--ghost");
      if (b.dataset.side === which) { b.classList.remove("btn--ghost"); b.classList.add("btn--primary"); }
    });
    setTimeout(() => cyInstances.forEach((cy) => { try { cy.resize(); cy.fit(undefined, 12); } catch {} }), 50);
  }
  toggle.querySelectorAll("[data-side]").forEach((b) => b.addEventListener("click", () => showSide(b.dataset.side)));
  showSide("left");

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
    },
  };
}

export async function renderDiffusion(container, block, options = {}) {
  const mode = block.mode;

  if (mode === "compare-three") {
    return await renderCompareThree(container, block);
  }
  if (mode === "mirror") {
    return await renderMirror(container, block);
  }
  if (mode === "duel") {
    return await renderDuel(container, block);
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
    ...narrowCyOpts(),
    container: stage,
    elements,
    style: makeStyle(),
    layout: {
      name: "cose",
      animate: false,
      padding: 20,
      idealEdgeLength: 50,
      nodeRepulsion: 4500
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

    function activate(metric, btn) {
      controls.querySelectorAll("[data-metric]").forEach((b) => b.classList.remove("btn--primary", "diff-btn--active"));
      controls.querySelectorAll("[data-metric]").forEach((b) => b.classList.add("btn--ghost"));
      if (btn) { btn.classList.remove("btn--ghost"); btn.classList.add("btn--primary", "diff-btn--active"); }
      cy.nodes().removeClass("top");
      const res = computeTop(metric);
      if (res && res.id) {
        const n = cy.getElementById(res.id);
        if (n && n.length) n.addClass("top");
        const who = nameById.get(res.id) || `Elev ${res.id}`;
        valueEl.textContent = `${who}: ${res.label}`;
      }
    }
    controls.querySelectorAll("[data-metric]").forEach((btn) => {
      btn.addEventListener("click", () => activate(btn.dataset.metric, btn));
    });
    // Activate first metric on load, so the user sees a highlight immediately.
    requestAnimationFrame(() => {
      const first = controls.querySelector('[data-metric="degree"]');
      if (first) activate("degree", first);
    });
  }

  else if (mode === "temporal") {
    // hourly cursor + network redraw from highschool-hours.json
    // Make nodes fully opaque and normally sized (matches other cards).
    cy.nodes().addClass("knows");
    cy.nodes().forEach((n) => {
      n.style("opacity", 1);
      n.style("width", 10);
      n.style("height", 10);
    });

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
      cy.edges().style("line-color", "#b57140");
      cy.edges().style("opacity", 0.4);
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
    // Probabilistic SIR calibrated on this network (Sandu source, 200 runs):
    //   pT = 0.10, pS = 0.42 -> mean 50, min 1, max 155.
    //   ~20% of runs die out under 10, tail out to ~150. Shape is right-skewed
    //   with a heavy small-outcome mode, which is the pedagogical point.
    const P_T = block.pTransmit ?? 0.10;
    const P_S = block.pStop ?? 0.42;
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
      `<div class="diff-hint">Aceleași noduri, alt criteriu de colorare. Priveşte contactele și vezi cum se aleg vecinii, sau nu.</div>`;
  }

  else if (mode === "recolor") {
    cy.nodes().addClass("knows");
    const schemes = block.schemes || ["class", "community", "component", "degree"];
    let statsData = null;
    try { statsData = await (await fetch(block.statsSource || "data/highschool-stats.json")).json(); } catch {}
    const commById = statsData?.sliceMetrics?.communities?.byId || {};
    const mismatchedIds = new Set((statsData?.sliceMetrics?.communities?.mismatched || []).map((m) => String(m.id)));

    const adjMap = new Map();
    for (const n of nodes) adjMap.set(n.id, new Set());
    for (const e of edges) { adjMap.get(e.source).add(e.target); adjMap.get(e.target).add(e.source); }
    const compById = {};
    let cid = 0;
    const seen = new Set();
    for (const n of nodes) {
      if (seen.has(n.id)) continue;
      const stk = [n.id];
      while (stk.length) {
        const x = stk.pop();
        if (seen.has(x)) continue;
        seen.add(x);
        compById[x] = cid;
        for (const y of adjMap.get(x) || []) if (!seen.has(y)) stk.push(y);
      }
      cid++;
    }

    const degById = {};
    cy.nodes().forEach((n) => { degById[n.id()] = n.connectedEdges().length; });
    const maxDeg = Math.max(...Object.values(degById), 1);

    const PALETTE = GROUP_PALETTE.slice();
    const groupBy = new Map(nodes.map((n) => [n.id, n.group]));

    // Component sizes + biggest-component id, for the component scheme.
    const compSizes = new Map();
    for (const nid of Object.keys(compById)) {
      const c = compById[nid];
      compSizes.set(c, (compSizes.get(c) || 0) + 1);
    }
    let bigCompId = null, bigCompSize = -1;
    for (const [c, sz] of compSizes) {
      if (sz > bigCompSize) { bigCompSize = sz; bigCompId = c; }
    }
    // Unreached ids come from stats, so both marginal cases (small-comp + unreached-inside-big-comp) collapse to one visual class.
    const unreachedSet = new Set((statsData?.sliceMetrics?.unreachableIds || []).map(String));

    function colorFor(nid, scheme) {
      if (scheme === "class") {
        const g = groupBy.get(nid);
        const i = groups.indexOf(g);
        return PALETTE[i % PALETTE.length];
      }
      if (scheme === "community") {
        const c = commById[nid];
        if (c == null) return "#8a7a68";
        return PALETTE[c % PALETTE.length];
      }
      if (scheme === "component") {
        // Almost the whole school is one component, so painting by component id
        // just floods everything with one hue. Instead: paint the big component
        // in a light neutral, and highlight the marginal students (unreached by
        // the bounded diffusion, or sitting in a tiny detached component) in
        // an accent color so the exception reads.
        const compId = compById[nid];
        const isBig = compId === bigCompId;
        const isUnreachedFlag = unreachedSet.has(String(nid));
        if (isBig && !isUnreachedFlag) return "#efe6d6"; // light beige (in the big component, reachable)
        return "#c96d3f"; // warm accent for the margin (either small comp or unreached)
      }
      if (scheme === "degree") {
        const t = degById[nid] / maxDeg;
        const R = Math.round(217 * (1 - t) + 139 * t);
        const G = Math.round(207 * (1 - t) + 74  * t);
        const B = Math.round(192 * (1 - t) + 30  * t);
        return `rgb(${R},${G},${B})`;
      }
      if (scheme === "openness") {
        const opById = statsData?.sliceMetrics?.openness || {};
        const maxOp = Math.max(...Object.values(opById).map((v) => Number(v) || 0), 1);
        const t = (Number(opById[String(nid)]) || 0) / maxOp;
        // Sequential warm palette: light beige → deep brown
        const R = Math.round(242 * (1 - t) + 74  * t);
        const G = Math.round(237 * (1 - t) + 46  * t);
        const B = Math.round(229 * (1 - t) + 24  * t);
        return `rgb(${R},${G},${B})`;
      }
      if (scheme === "mismatch") {
        return mismatchedIds.has(String(nid)) ? "#a3341f" : "#d9cfc0";
      }
      return "#8a7a68";
    }

    function applyScheme(scheme) {
      const opById = statsData?.sliceMetrics?.openness || {};
      const opVals = Object.values(opById).map((v) => Number(v) || 0);
      const maxOp = Math.max(...opVals, 1);
      // Top 10% openness threshold (for border-emphasis on openness scheme)
      const opSorted = opVals.slice().sort((a, b) => b - a);
      const top10Op = opSorted[Math.max(0, Math.floor(opVals.length * 0.1) - 1)] || 0;
      // For degree: same idea
      const degVals = Object.values(degById);
      const degSorted = degVals.slice().sort((a, b) => b - a);
      const top10Deg = degSorted[Math.max(0, Math.floor(degVals.length * 0.1) - 1)] || 0;

      cy.nodes().forEach((n) => {
        const nid = n.id();
        n.style("transition-property", "background-color, width, height, border-width");
        n.style("transition-duration", 400);
        n.style("background-color", colorFor(nid, scheme));
        if (scheme === "mismatch" && mismatchedIds.has(nid)) {
          n.style("width", 20); n.style("height", 20); n.style("border-width", 2); n.style("opacity", 1);
        } else if (scheme === "mismatch") {
          n.style("width", 10); n.style("height", 10); n.style("border-width", 1); n.style("opacity", 0.35);
        } else if (scheme === "openness") {
          const v = Number(opById[nid]) || 0;
          const size = 8 + (v / maxOp) * 10; // 8..18
          n.style("width", size); n.style("height", size);
          n.style("border-width", v >= top10Op ? 2 : 1);
          n.style("border-color", v >= top10Op ? "#2a1f16" : "#5a4a3a");
          n.style("opacity", 1);
        } else if (scheme === "degree") {
          const v = degById[nid] || 0;
          const size = 8 + (v / maxDeg) * 10;
          n.style("width", size); n.style("height", size);
          n.style("border-width", v >= top10Deg ? 2 : 1);
          n.style("border-color", v >= top10Deg ? "#2a1f16" : "#5a4a3a");
          n.style("opacity", 1);
        } else if (scheme === "component") {
          const compId = compById[nid];
          const isMargin = compId !== bigCompId || unreachedSet.has(String(nid));
          if (isMargin) {
            n.style("width", 15); n.style("height", 15);
            n.style("border-width", 2); n.style("border-color", "#5a2a10");
          } else {
            n.style("width", 8); n.style("height", 8);
            n.style("border-width", 1); n.style("border-color", "#c9beac");
          }
          n.style("opacity", 1);
        } else {
          n.style("width", 9); n.style("height", 9); n.style("border-width", 1);
          n.style("border-color", "#5a4a3a"); n.style("opacity", 1);
        }
      });

      // Update legend to gradient bar when using sequential scheme
      if (scheme === "openness" || scheme === "degree") {
        legend.innerHTML =
          `<div class="viz__gradient" style="background: linear-gradient(to right, ` +
          (scheme === "openness"
            ? "rgb(242,237,229), rgb(74,46,24)"
            : "rgb(217,207,192), rgb(139,74,30)") + `);">` +
          `<span class="viz__gradient-label viz__gradient-label--left">${scheme === "openness" ? "un grup" : "puțin"}</span>` +
          `<span class="viz__gradient-label viz__gradient-label--right">${scheme === "openness" ? maxOp + " grupuri" : maxDeg + " contacte"}</span>` +
          `</div>`;
      } else {
        // Restore group legend
        legend.innerHTML = "";
        for (const g of groups) {
          const chip = document.createElement("span");
          chip.className = "viz__legend-chip";
          const dot = document.createElement("span");
          dot.className = "viz__legend-dot";
          dot.style.background = colorMap.get(g);
          chip.appendChild(dot);
          const label = document.createElement("span");
          const friendly = statsData?.classNames?.[g] || g;
          label.textContent = friendly;
          chip.appendChild(label);
          legend.appendChild(chip);
        }
      }
    }

    const labels = {
      class: "Clasa", community: "Comunitatea", component: "Componenta",
      degree: "Popularitatea", openness: "Deschiderea",
      mismatch: "Arată nepotrivirile"
    };
    const marginCount = (() => {
      let m = 0;
      for (const nid of Object.keys(compById)) {
        if (compById[nid] !== bigCompId || unreachedSet.has(nid)) m++;
      }
      return m;
    })();

    const explains = {
      class:     "Culoarea = clasa administrativă. Așa vede orarul.",
      community: "Culoarea = comunitatea detectată de algoritm (label propagation, seed 42). Aproape identică cu clasele; unde nu, avem personaje.",
      component: `O componentă mare cu ${bigCompSize} elevi, plus ${marginCount} la margine (evidențiați cu contur), la care difuzia nu ajunge.`,
      degree:    "Culoarea = popularitatea (gradul). Cu cât mai închis, cu atât mai popular.",
      openness:  "Culoarea = deschiderea. Cu cât mai închis (albastru), cu atât mai multe grupuri diferite atinge cu vecinii lui.",
      mismatch:  "Roșu = elevii puși de algoritm în altă comunitate decât clasa lor. Sunt puțini, dar prin ei trece rețeaua dincolo de granițe."
    };

    controls.innerHTML =
      `<div class="diff-row diff-buttons">` +
      schemes.map((s) => `<button type="button" class="btn btn--ghost recolor-btn" data-scheme="${s}">${labels[s] || s}</button>`).join("") +
      `</div>` +
      `<div class="diff-hint" data-role="explain"></div>` +
      `<div class="diff-count" data-role="info">Atinge un nod pentru numele lui.</div>`;

    const explainEl = controls.querySelector('[data-role="explain"]');
    const infoEl = controls.querySelector('[data-role="info"]');
    function activate(scheme, btn) {
      controls.querySelectorAll("[data-scheme]").forEach((b) => { b.classList.remove("btn--primary"); b.classList.add("btn--ghost"); });
      if (btn) { btn.classList.remove("btn--ghost"); btn.classList.add("btn--primary"); }
      applyScheme(scheme);
      explainEl.textContent = explains[scheme] || "";
    }
    controls.querySelectorAll("[data-scheme]").forEach((btn) => btn.addEventListener("click", () => activate(btn.dataset.scheme, btn)));
    cy.on("tap", "node", (e) => {
      const nid = e.target.id();
      const n = nodes.find((nn) => nn.id === nid);
      const deg = e.target.connectedEdges().length;
      const parts = [n?.name || `Elev ${nid}`];
      if (n?.group) {
        const friendly = statsData?.classNames?.[n.group] || n.group;
        parts.push(`clasa ${friendly}`);
      }
      parts.push(`${deg} contacte`);
      infoEl.textContent = parts.join(" · ");
    });
    requestAnimationFrame(() => {
      const first = controls.querySelector("[data-scheme]");
      if (first) activate(first.dataset.scheme, first);
    });
  }

  else if (mode === "coverage") {
    cy.nodes().addClass("knows");
    const seedNames = block.seedNames || [];
    const nameToId = new Map(nodes.map((n) => [n.name, n.id]));
    const seedIds = seedNames.map((nm) => nameToId.get(nm)).filter(Boolean);
    const SEED_COLORS = ["#8b4a1e", "#3d7a52", "#2f6fa8", "#a3341f"];

    const adjMap = new Map();
    for (const n of nodes) adjMap.set(n.id, new Set());
    for (const e of edges) { adjMap.get(e.source).add(e.target); adjMap.get(e.target).add(e.source); }
    const egos = seedIds.map((sid) => new Set([sid, ...(adjMap.get(sid) || [])]));

    const joint = new Set();
    for (const s of egos) for (const x of s) joint.add(x);
    const sumInd = egos.reduce((s, e) => s + e.size, 0);
    const overlap = sumInd - joint.size;

    cy.nodes().forEach((n) => {
      const nid = n.id();
      const owners = egos.map((e, i) => e.has(nid) ? i : -1).filter((x) => x >= 0);
      if (!owners.length) { n.style("opacity", 0.15); return; }
      if (owners.length === 1) {
        n.style("background-color", SEED_COLORS[owners[0] % SEED_COLORS.length]);
        n.style("opacity", 0.7);
      } else {
        n.style("background-color", "#2a1f16");
        n.style("opacity", 1);
      }
      if (seedIds.includes(nid)) { n.addClass("source"); }
    });

    const seedNamesFmt = seedIds.map((sid, i) => `<span style="color:${SEED_COLORS[i % SEED_COLORS.length]}">${nameById.get(sid) || sid}</span>`).join(", ");
    controls.innerHTML =
      `<div class="diff-hint">Cercuri de acoperire pentru: ${seedNamesFmt}. Nodurile <strong>închise</strong> sunt acoperite de mai mulți.</div>` +
      `<div class="diff-count">Împreună: <strong>${joint.size}</strong>. Suma separată: ${sumInd}. Suprapunere: ${overlap}.</div>`;
  }

  else if (mode === "greedy-anim") {
    cy.nodes().addClass("knows");
    const steps = block.steps || 3;

    let statsDataG = null;
    try { statsDataG = await (await fetch(block.statsSource || "data/highschool-stats.json")).json(); } catch {}
    const PASI = block.pasi || statsDataG?.sliceMetrics?.diffusionModel?.pasi || 4;
    const MAX_T = block.maxTransmiteri || statsDataG?.sliceMetrics?.diffusionModel?.maxTransmiteri || 4;
    const MIN_W = 4;

    // Bounded reach: weight-filtered top-K adjacency, PASI rounds.
    const adjTopG = new Map();
    {
      const tmp = new Map();
      for (const n of nodes) tmp.set(n.id, []);
      for (const e of edges) {
        if ((e.weight || 0) < MIN_W) continue;
        tmp.get(e.source).push({ to: e.target, w: e.weight });
        tmp.get(e.target).push({ to: e.source, w: e.weight });
      }
      for (const [nid, arr] of tmp) {
        arr.sort((a, b) => b.w - a.w || (a.to < b.to ? -1 : 1));
        adjTopG.set(nid, arr.slice(0, MAX_T).map((x) => x.to));
      }
    }
    function reachBounded(seeds) {
      const known = new Set(seeds.map(String));
      let frontier = seeds.map(String);
      for (let s = 0; s < PASI && frontier.length; s++) {
        const next = [];
        for (const x of frontier) {
          for (const y of adjTopG.get(x) || []) {
            if (!known.has(y)) { known.add(y); next.push(y); }
          }
        }
        frontier = next;
      }
      return known;
    }
    const reachSet = new Map(nodes.map((n) => [String(n.id), reachBounded([n.id])]));

    let picks = [];
    let covered = new Set();

    controls.innerHTML =
      `<div class="diff-count" data-role="status">Alegere lacomă: pas 0 din ${steps}.</div>` +
      `<div class="diff-row diff-buttons">` +
        `<button type="button" class="btn btn--primary" data-act="step">Pas următor</button>` +
        `<button type="button" class="btn btn--ghost" data-act="reset">Resetează</button>` +
      `</div>` +
      `<div class="diff-hint" data-role="pick"></div>`;

    const statusEl = controls.querySelector('[data-role="status"]');
    const pickEl = controls.querySelector('[data-role="pick"]');

    function paint() {
      cy.nodes().forEach((n) => {
        const nid = n.id();
        n.removeClass("source");
        if (picks.includes(nid)) { n.addClass("source"); n.style("opacity", 1); }
        else if (covered.has(nid)) n.style("opacity", 0.35);
        else n.style("opacity", 1);
      });
    }

    function doStep() {
      if (picks.length >= steps) return;
      let bestId = null, bestAdd = -1;
      for (const n of nodes) {
        const nid = String(n.id);
        if (picks.includes(nid)) continue;
        // Recompute with cumulative team so overlap counts properly.
        const cumulative = reachBounded([...picks, n.id].map(Number));
        const add = cumulative.size - covered.size;
        if (add > bestAdd || (add === bestAdd && (bestId === null || nid < bestId))) {
          bestAdd = add;
          bestId = nid;
        }
      }
      if (bestId === null) return;
      const teamReach = reachBounded([...picks, bestId].map(Number));
      const gained = new Set([...teamReach].filter((x) => !covered.has(x)));
      picks.push(bestId);
      covered = teamReach;
      cy.nodes().forEach((n) => {
        if (gained.has(n.id())) { n.style("opacity", 1); n.style("background-color", "#3d7a52"); }
      });
      setTimeout(() => paint(), 800);
      const nm = nameById.get(bestId);
      pickEl.textContent = `Pas ${picks.length}: ${nm} adaugă ${bestAdd} persoane noi. Acoperire totală: ${covered.size} din ${nodes.length}.`;
      statusEl.textContent = `Alegere lacomă: pas ${picks.length} din ${steps}.`;
    }
    function doReset() {
      picks = []; covered = new Set();
      cy.nodes().forEach((n) => { n.removeClass("source"); n.style("opacity", 1); });
      cy.nodes().forEach((n) => {
        const gc = colorMap.get(n.data("group")) || GROUP_PALETTE[0];
        n.style("background-color", gc);
      });
      statusEl.textContent = `Alegere lacomă: pas 0 din ${steps}.`;
      pickEl.textContent = "";
    }
    controls.querySelector('[data-act="step"]').addEventListener("click", doStep);
    controls.querySelector('[data-act="reset"]').addEventListener("click", doReset);
  }

  else if (mode === "characters") {
    cy.nodes().addClass("knows");
    let statsData = null;
    try { statsData = await (await fetch(block.statsSource || "data/highschool-stats.json")).json(); } catch {}
    const chars = statsData?.sliceMetrics?.characters || {};
    const roles = [
      { key: "star", label: "Vedeta", numLabel: "contacte", numField: "popularity" },
      { key: "bridge", label: "Puntea", numLabel: "grupuri diferite", numField: "openness" },
      { key: "discreet", label: "Discretul", numLabel: "grupuri (doar câteva contacte)", numField: "openness" },
      { key: "isolated", label: "Izolatul", numLabel: "contact", numField: "popularity" }
    ];
    const chipsHtml = roles.map((r) => {
      const c = chars[r.key];
      if (!c) return "";
      return `<button type="button" class="char-chip" data-role="${r.key}" data-id="${c.id}">` +
        `<div class="char-chip__role">${r.label}</div>` +
        `<div class="char-chip__name">${c.name}</div>` +
        `<div class="char-chip__stat"><strong>${c[r.numField]}</strong> ${r.numLabel}</div>` +
        `</button>`;
    }).join("");
    controls.innerHTML =
      `<div class="char-chips">${chipsHtml}</div>` +
      `<div class="diff-hint" data-role="info">Atinge un personaj pentru a-l vedea pe hartă cu vecinii lui.</div>`;
    const infoEl = controls.querySelector('[data-role="info"]');
    function highlight(nid) {
      cy.nodes().removeClass("top source knows");
      const focal = cy.getElementById(String(nid));
      if (focal && focal.length) {
        focal.closedNeighborhood().addClass("knows");
        focal.addClass("top");
      }
    }
    controls.querySelectorAll(".char-chip").forEach((btn) => {
      btn.addEventListener("click", () => {
        const roleKey = btn.dataset.role;
        const c = chars[roleKey];
        if (!c) return;
        controls.querySelectorAll(".char-chip").forEach((b) => b.classList.remove("char-chip--active"));
        btn.classList.add("char-chip--active");
        highlight(c.id);
        infoEl.textContent = `${c.name} din ${c.class}: ${c.popularity} contacte, în ${c.openness} grupuri diferite. Uită-te unde e situat în rețea.`;
      });
    });
    requestAnimationFrame(() => {
      const first = controls.querySelector(".char-chip");
      if (first) first.click();
    });
  }

  else if (mode === "mission") {
    cy.nodes().addClass("knows");
    const teamSize = block.teamSize || 3;
    const presets = block.presets || [];
    const nameToId = new Map(nodes.map((n) => [n.name, n.id]));

    // Bounded diffusion matching build_network.py:
    //  - only edges with weight >= MIN_W count
    //  - each carrier transmits to at most MAX_T strongest contacts
    //  - BFS bounded to PASI rounds
    let statsDataM = null;
    try { statsDataM = await (await fetch(block.statsSource || "data/highschool-stats.json")).json(); } catch {}
    const PASI = block.pasi || statsDataM?.sliceMetrics?.diffusionModel?.pasi || 4;
    const MAX_T = block.maxTransmiteri || statsDataM?.sliceMetrics?.diffusionModel?.maxTransmiteri || 4;
    const MIN_W = 4;

    const adjTop = new Map();
    {
      const tmp = new Map();
      for (const n of nodes) tmp.set(n.id, []);
      for (const e of edges) {
        if ((e.weight || 0) < MIN_W) continue;
        tmp.get(e.source).push({ to: e.target, w: e.weight });
        tmp.get(e.target).push({ to: e.source, w: e.weight });
      }
      for (const [nid, arr] of tmp) {
        arr.sort((a, b) => b.w - a.w || (a.to < b.to ? -1 : 1));
        adjTop.set(nid, arr.slice(0, MAX_T).map((x) => x.to));
      }
    }
    // Full unbounded adjacency for the animation only (so the wave still spreads visually)
    const adjMap = new Map();
    for (const n of nodes) adjMap.set(n.id, new Set());
    for (const e of edges) { adjMap.get(e.source).add(e.target); adjMap.get(e.target).add(e.source); }

    function coverage(seedIds) {
      const known = new Set(seedIds.map(String));
      let frontier = seedIds.map(String);
      for (let s = 0; s < PASI && frontier.length; s++) {
        const next = [];
        for (const x of frontier) {
          for (const y of adjTop.get(x) || []) {
            if (!known.has(y)) { known.add(y); next.push(y); }
          }
        }
        frontier = next;
      }
      return known;
    }

    const team = [];
    const history = [];

    controls.innerHTML =
      `<div class="diff-count" data-role="status">Alege ${teamSize} elevi. Zvonul pornește de la ei simultan.</div>` +
      `<div class="diff-hint" data-role="preview">Atinge un nod pentru a-l adăuga în echipă.</div>` +
      `<div class="diff-row diff-buttons">` +
        `<button type="button" class="btn btn--primary" data-act="send" disabled>Trimite</button>` +
        `<button type="button" class="btn btn--ghost" data-act="reset">Resetează echipa</button>` +
      `</div>` +
      (presets.length ? `<div class="diff-row diff-buttons mission-presets">` +
        `<span class="mission-presets__label">Strategii predefinite:</span>` +
        presets.map((p, i) => `<button type="button" class="btn btn--ghost" data-preset="${i}">${p.label}</button>`).join("") +
        `</div>` : "") +
      `<div class="diff-hint" data-role="history"></div>`;

    const statusEl = controls.querySelector('[data-role="status"]');
    const previewEl = controls.querySelector('[data-role="preview"]');
    const historyEl = controls.querySelector('[data-role="history"]');
    const sendBtn = controls.querySelector('[data-act="send"]');

    function paint() {
      cy.nodes().removeClass("source");
      cy.nodes().forEach((n) => {
        if (team.includes(n.id())) n.addClass("source");
      });
      const cov = team.length ? coverage(team).size : 0;
      statusEl.textContent = team.length
        ? `Echipa: ${team.length}/${teamSize}. Acoperire actuală: ${cov} din ${nodes.length}.`
        : `Alege ${teamSize} elevi. Zvonul pornește de la ei simultan.`;
      sendBtn.disabled = team.length !== teamSize;
    }

    cy.on("tap", "node", (e) => {
      const nid = e.target.id();
      const pos = team.indexOf(nid);
      if (pos >= 0) team.splice(pos, 1);
      else if (team.length < teamSize) team.push(nid);
      paint();
    });
    cy.on("mouseover", "node", (e) => {
      const nid = e.target.id();
      if (team.includes(nid) || team.length >= teamSize) return;
      const hyp = coverage([...team, nid]).size;
      previewEl.textContent = `Cu ${nameById.get(nid) || nid} în plus, echipa ar atinge ${hyp} elevi.`;
    });
    cy.on("mouseout", "node", () => { if (team.length < teamSize) previewEl.textContent = "Atinge un nod pentru a-l adăuga în echipă."; });

    function animateSpread(ids, cb) {
      cy.nodes().removeClass("knows");
      for (const x of ids) cy.getElementById(String(x)).addClass("knows");
      const covered = new Set(ids.map(String));
      let frontier = ids.map(String);
      let step = 0;
      const iv = setInterval(() => {
        const next = [];
        for (const x of frontier) for (const y of adjTop.get(x) || []) if (!covered.has(y)) { covered.add(y); next.push(y); }
        for (const y of next) cy.getElementById(String(y)).addClass("knows");
        frontier = next;
        step++;
        if (!next.length || step >= PASI) { clearInterval(iv); cb(covered); }
      }, 350);
    }

    function renderHistory() {
      if (!history.length) { historyEl.innerHTML = ""; return; }
      historyEl.innerHTML = "<strong>Istoric:</strong><br>" + history.map((h, i) =>
        `${i + 1}. ${h.team.join(", ")} → <strong>${h.coverage}</strong>`
      ).join("<br>");
    }

    sendBtn.addEventListener("click", () => {
      const seeds = [...team];
      sendBtn.disabled = true;
      statusEl.textContent = "Se transmite…";
      previewEl.textContent = "";
      animateSpread(seeds, (covered) => {
        const names = seeds.map((s) => nameById.get(s) || s);
        history.push({ team: names, coverage: covered.size });
        renderHistory();
        statusEl.textContent = `Rezultat: ${names.join(", ")} → ${covered.size} din ${nodes.length}.`;
        team.length = 0;
        setTimeout(() => { cy.nodes().addClass("knows"); paint(); }, 1400);
      });
    });
    controls.querySelector('[data-act="reset"]').addEventListener("click", () => { team.length = 0; paint(); });
    controls.querySelectorAll("[data-preset]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const p = presets[parseInt(btn.dataset.preset, 10)];
        if (!p) return;
        team.length = 0;
        if (p.random === true) {
          // Pick teamSize distinct random elevs
          const pool = nodes.map((n) => n.id);
          for (let i = pool.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [pool[i], pool[j]] = [pool[j], pool[i]];
          }
          for (const nid of pool.slice(0, teamSize)) team.push(nid);
        } else if (Array.isArray(p.names)) {
          for (const nm of p.names) { const nid = nameToId.get(nm); if (nid && team.length < teamSize) team.push(nid); }
        }
        paint();
      });
    });
    paint();
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

  else if (mode === "class-lens") {
    // Show one class in isolation, three named characters emphasized; button
    // reveals the rest of the school with the same three staying prominent.
    let statsData = null;
    try { statsData = await (await fetch(block.statsSource || "data/highschool-stats.json")).json(); } catch {}
    const focusClass = block.focusClass;
    const highlightNames = block.highlight || [];
    const nameToNode = new Map(nodes.map((n) => [n.name, n]));
    const highlightIds = new Set(
      highlightNames.map((nm) => nameToNode.get(nm)?.id).filter(Boolean)
    );
    let expanded = false;

    function apply() {
      cy.nodes().forEach((n) => {
        const nid = n.id();
        const grp = n.data("group");
        const isHighlight = highlightIds.has(nid);
        const inFocus = grp === focusClass;
        if (expanded) {
          n.style("display", "element");
          if (isHighlight) {
            n.style("opacity", 1); n.style("width", 18); n.style("height", 18);
            n.style("border-width", 2); n.style("border-color", "#2a1f16");
          } else {
            n.style("opacity", 0.45); n.style("width", 8); n.style("height", 8);
            n.style("border-width", 1);
          }
        } else {
          if (inFocus) {
            n.style("display", "element");
            if (isHighlight) {
              n.style("opacity", 1); n.style("width", 20); n.style("height", 20);
              n.style("border-width", 2); n.style("border-color", "#2a1f16");
            } else {
              n.style("opacity", 0.9); n.style("width", 12); n.style("height", 12);
              n.style("border-width", 1);
            }
          } else {
            n.style("display", "none");
          }
        }
      });
      cy.edges().forEach((e) => {
        const sId = e.source().id(), tId = e.target().id();
        const sVis = cy.getElementById(sId).style("display") !== "none";
        const tVis = cy.getElementById(tId).style("display") !== "none";
        e.style("display", sVis && tVis ? "element" : "none");
        e.style("opacity", 0.35);
      });
      setTimeout(() => { try { cy.resize(); cy.fit(cy.nodes(":visible"), 30); } catch {} }, 60);
    }

    const beforeText = block.textBefore || "";
    const afterText  = block.textAfter  || "";
    const buttonLabel = block.buttonLabel || "Arată restul școlii";

    controls.innerHTML =
      `<div class="diff-hint" data-role="text">${beforeText}</div>` +
      `<div class="diff-row diff-buttons">` +
        `<button type="button" class="btn btn--primary" data-act="expand">${buttonLabel}</button>` +
      `</div>`;
    const textEl = controls.querySelector('[data-role="text"]');
    controls.querySelector('[data-act="expand"]').addEventListener("click", () => {
      if (expanded) return;
      expanded = true;
      apply();
      textEl.innerHTML = afterText;
    });

    apply();
  }

  else if (mode === "story-network") {
    // Progressive ego-network reveal for C10-C12.
    // block.focus (name), block.focus2 (optional), block.story = [ {visible?, buttonLabel?, add?, action?, text?} ]
    let statsData = null;
    try { statsData = await (await fetch(block.statsSource || "data/highschool-stats.json")).json(); } catch {}
    const classNames = statsData?.classNames || {};
    const nameToNode = new Map(nodes.map((n) => [n.name, n]));
    const focusName = block.focus;
    const focus2Name = block.focus2 || null;
    const focusNode = nameToNode.get(focusName);
    const focus2Node = focus2Name ? nameToNode.get(focus2Name) : null;

    if (!focusNode) {
      controls.innerHTML = `<div class="diff-hint">Nu găsesc personajul „${focusName}".</div>`;
    } else {
      const adjSet = new Map();
      for (const n of nodes) adjSet.set(n.id, new Set());
      for (const e of edges) { adjSet.get(e.source)?.add(e.target); adjSet.get(e.target)?.add(e.source); }

      function idsFor(what) {
        if (what === "focus") return [focusNode.id];
        if (what === "neighbors") return [...(adjSet.get(focusNode.id) || [])];
        if (what === "class") return nodes.filter((n) => n.group === focusNode.group).map((n) => n.id);
        if (what === "focus2") return focus2Node ? [focus2Node.id] : [];
        if (what === "focus2:neighbors") return focus2Node ? [...(adjSet.get(focus2Node.id) || [])] : [];
        if (what === "focus2:class") return focus2Node ? nodes.filter((n) => n.group === focus2Node.group).map((n) => n.id) : [];
        return [];
      }

      const story = Array.isArray(block.story) ? block.story : [];
      let stepIndex = 0;
      const visible = new Set();

      // Bootstrap initial visible set
      const initial = story[0]?.visible || ["focus"];
      for (const w of initial) for (const id of idsFor(w)) visible.add(id);

      // Layout on FULL graph so positions are stable; hide the rest via display.
      // Colors default to class palette.
      cy.nodes().forEach((n) => {
        const nid = n.id();
        if (visible.has(nid)) {
          n.style("display", "element");
          n.style("opacity", 1);
        } else {
          n.style("display", "none");
        }
      });
      cy.edges().forEach((e) => {
        const s = e.source().id(), t = e.target().id();
        if (visible.has(s) && visible.has(t)) e.style("display", "element");
        else e.style("display", "none");
      });

      function refitStage() {
        try { cy.resize(); cy.fit(cy.nodes(":visible"), 40); } catch {}
      }

      function highlightFocus() {
        cy.nodes().removeClass("top source");
        const f = cy.getElementById(focusNode.id);
        if (f && f.length) f.addClass("source");
        if (focus2Node && visible.has(focus2Node.id)) {
          const f2 = cy.getElementById(focus2Node.id);
          if (f2 && f2.length) f2.addClass("top");
        }
      }

      function applyVisibility() {
        cy.nodes().forEach((n) => {
          const nid = n.id();
          if (visible.has(nid)) {
            n.style("display", "element");
            n.style("opacity", 1);
          } else {
            n.style("display", "none");
          }
        });
        cy.edges().forEach((e) => {
          const s = e.source().id(), t = e.target().id();
          if (visible.has(s) && visible.has(t)) e.style("display", "element");
          else e.style("display", "none");
        });
        highlightFocus();
        setTimeout(refitStage, 60);
      }

      function renderControls() {
        const step = story[stepIndex] || {};
        const next = story[stepIndex + 1];
        const focusClassFriendly = classNames[focusNode.group] || focusNode.group;
        const focus2ClassFriendly = focus2Node ? (classNames[focus2Node.group] || focus2Node.group) : "";
        let text = step.text || "";
        text = text
          .replace(/\{\{focus\}\}/g, focusName)
          .replace(/\{\{focusClass\}\}/g, focusClassFriendly)
          .replace(/\{\{focus2\}\}/g, focus2Name || "")
          .replace(/\{\{focus2Class\}\}/g, focus2ClassFriendly);

        let html = "";
        if (text) html += `<div class="diff-hint" data-role="text">${text}</div>`;
        if (next && next.buttonLabel) {
          html += `<div class="diff-row diff-buttons"><button type="button" class="btn btn--primary" data-act="next">${next.buttonLabel}</button></div>`;
        }
        controls.innerHTML = html;
        const btn = controls.querySelector('[data-act="next"]');
        if (btn) btn.addEventListener("click", () => {
          stepIndex++;
          const s = story[stepIndex];
          if (s.add) for (const id of idsFor(s.add)) visible.add(id);
          applyVisibility();
          renderControls();
        });
      }

      highlightFocus();
      renderControls();
      setTimeout(refitStage, 120);
    }
  }

  else if (mode === "try-break") {
    // Removal experiment for C13. Two submodes: people, edges.
    let statsData = null;
    try { statsData = await (await fetch(block.statsSource || "data/highschool-stats.json")).json(); } catch {}
    const classNames = statsData?.classNames || {};
    const sm = statsData?.sliceMetrics || {};
    const cutVertices = sm.cutVertices || [];
    const nCutVertices = sm.nCutVertices || cutVertices.length;
    const bridgeEdges = sm.bridgeEdges || [];
    const top5Removal = sm.top5Removal || { top5: [] };
    const brokenPair = sm.brokenPair || null;

    const cutMap = new Map();
    for (const cv of cutVertices) cutMap.set(String(cv.id), cv);

    const nameToNode = new Map(nodes.map((n) => [n.name, n]));

    let subMode = "people";
    const removedNodes = new Set();
    const removedEdges = new Set();

    // Identify Luca-Kira edge id for edges mode highlight
    let starBridgeEdgeId = null;
    if (brokenPair && brokenPair.personA && brokenPair.personB) {
      const pa = nameToNode.get(brokenPair.personA.name);
      const pb = nameToNode.get(brokenPair.personB.name);
      if (pa && pb) {
        cy.edges().forEach((e) => {
          const s = e.source().id(), t = e.target().id();
          if ((s === pa.id && t === pb.id) || (s === pb.id && t === pa.id)) starBridgeEdgeId = e.id();
        });
      }
    }
    // Identify all thin (1-2 edge) class-pair edge ids
    const thinBridgeEdgeIds = new Set();
    const classPairMatrix = sm.classPairMatrix || [];
    for (const cp of classPairMatrix) {
      if (cp.edgeCount <= 2) {
        for (const ce of cp.edges || []) {
          const aId = String(ce.a?.id), bId = String(ce.b?.id);
          cy.edges().forEach((e) => {
            const s = e.source().id(), t = e.target().id();
            if ((s === aId && t === bId) || (s === bId && t === aId)) thinBridgeEdgeIds.add(e.id());
          });
        }
      }
    }

    function resetAllVisuals() {
      removedNodes.clear();
      removedEdges.clear();
      cy.nodes().forEach((n) => {
        n.style("opacity", 1);
        n.style("width", 9); n.style("height", 9);
        n.style("border-width", 1);
        n.style("border-color", "#5a4a3a");
        n.style("background-color", n.data("color") || "#8a7a68");
      });
      cy.edges().forEach((e) => {
        e.style("opacity", 0.35);
        e.style("width", 0.8);
        e.style("line-color", "#d9cfc0");
      });
      applyEdgeHighlightIfEdgesMode();
    }

    function applyEdgeHighlightIfEdgesMode() {
      if (subMode !== "edges") return;
      cy.edges().forEach((e) => {
        if (thinBridgeEdgeIds.has(e.id())) {
          e.style("line-color", "#c96d3f");
          e.style("width", 2.4);
          e.style("opacity", 0.85);
        }
        if (e.id() === starBridgeEdgeId) {
          e.style("line-color", "#8b4a1e");
          e.style("width", 4);
          e.style("opacity", 1);
        }
      });
    }

    function removeNodeVisual(nid) {
      const id = String(nid);
      if (removedNodes.has(id)) return;
      removedNodes.add(id);
      const cn = cy.getElementById(id);
      if (cn && cn.length) {
        cn.style("opacity", 0.12);
        cn.style("background-color", "#a3341f");
        cn.style("border-width", 0);
      }
      cy.edges().forEach((e) => {
        if (e.source().id() === id || e.target().id() === id) e.style("opacity", 0.04);
      });
      // Highlight detached
      const cv = cutMap.get(id);
      if (cv && Array.isArray(cv.detached)) {
        for (const det of cv.detached) {
          const dn = cy.getElementById(String(det.id));
          if (dn && dn.length) {
            dn.style("border-color", "#a3341f");
            dn.style("border-width", 3);
            dn.style("width", 14); dn.style("height", 14);
          }
        }
      }
    }

    function textForRemovals() {
      const infoEl = controls.querySelector('[data-role="info"]');
      if (!infoEl) return;
      if (removedNodes.size === 0) {
        infoEl.textContent = "Atinge un elev pentru a-l scoate din rețea.";
        return;
      }
      // Special cased narrations
      const removedNames = [...removedNodes].map((id) => nameById.get(id) || `Elev ${id}`);
      // Vedeta solo (max popularity)
      const vedeta = sm.characters?.vedeta;
      if (removedNodes.size === 1 && vedeta && removedNodes.has(String(vedeta.id))) {
        const remaining = nodes.length - 1;
        infoEl.innerHTML = `Cel mai popular elev din școală a dispărut. Rămâne o singură bucată, cu <strong>${remaining}</strong> elevi. Nimeni nu s-a desprins.`;
        return;
      }
      // Dependentul (id 276) - detaches the most
      const dependent = sm.characters?.dependent;
      if (removedNodes.size === 1 && dependent && removedNodes.has(String(dependent.id))) {
        const dependentCut = cutVertices.find((c) => c.id === dependent.id);
        if (dependentCut) {
          const detNames = (dependentCut.detached || []).map((d) => d.name).join(", ");
          const pronoun = dependent.sex === "F" ? "Ea" : "El";
          const article = dependent.sex === "F" ? "-o" : "-l";
          infoEl.innerHTML = `Aici se întâmplă ceva. Fără <strong>${dependent.name}</strong>, ${dependentCut.detachedCount} elevi rămân complet rupți de restul școlii: ${detNames}. ${pronoun} era singurul lor drum.`;
          return;
        }
      }
      // Top 5
      const top5Ids = new Set((top5Removal.top5 || []).map((t) => String(t.id)));
      if (removedNodes.size === 5 && [...top5Ids].every((id) => removedNodes.has(id))) {
        const largest = top5Removal.largestAfter || 294;
        infoEl.innerHTML = `Cinci dintre cei mai conectați oameni, scoși deodată. Rămân <strong>${largest}</strong> de elevi, într-o singură bucată. Zero desprinși. Rețeaua nici nu a clipit.`;
        return;
      }
      // Generic: gather detached from cut vertices among removed
      const detachedSet = new Set();
      for (const rid of removedNodes) {
        const cv = cutMap.get(rid);
        if (cv) for (const d of cv.detached || []) detachedSet.add(d.name);
      }
      if (detachedSet.size > 0) {
        infoEl.innerHTML = `Elevi scoși: ${removedNames.join(", ")}. Desprinși de rețea: <strong>${detachedSet.size}</strong> (${[...detachedSet].join(", ")}).`;
      } else {
        infoEl.innerHTML = `Elevi scoși: ${removedNames.join(", ")}. Rețeaua rămâne o singură bucată. Nimeni nu s-a desprins.`;
      }
    }

    function removeEdgeVisual(edgeId) {
      if (removedEdges.has(edgeId)) return;
      removedEdges.add(edgeId);
      const e = cy.getElementById(edgeId);
      if (e && e.length) {
        e.style("opacity", 0.05);
        e.style("width", 0.5);
      }
      // If it's the star bridge (Luca-Kira), show a specific reveal
      const infoEl = controls.querySelector('[data-role="info"]');
      if (edgeId === starBridgeEdgeId && brokenPair && infoEl) {
        infoEl.innerHTML =
          `Nici măcar asta nu rupe școala. Fără prietenia dintre <strong>${brokenPair.personA.name}</strong> și <strong>${brokenPair.personB.name}</strong>, ` +
          `${brokenPair.classAFriendly} și ${brokenPair.classBFriendly} rămân legate, doar că drumul se lungește, ` +
          `de la <strong>${brokenPair.distanceBefore}</strong> la <strong>${brokenPair.distanceAfter}</strong> pași, prin ocol. ` +
          `Rețeaua are aproape peste tot mai multe drumuri între oricare doi oameni. ` +
          `Nu o rupi nici scoțând cei mai populari cinci elevi, nici tăind singurul fir dintre două clase. ` +
          `<strong>Atunci unde e fragilă?</strong>`;
        return;
      }
      if (thinBridgeEdgeIds.has(edgeId) && infoEl) {
        // Find which class pair this edge belonged to
        const sSrc = e.source().id(), sTgt = e.target().id();
        for (const cp of classPairMatrix) {
          if (cp.edgeCount > 2) continue;
          for (const ce of cp.edges || []) {
            const aId = String(ce.a?.id), bId = String(ce.b?.id);
            if ((aId === sSrc && bId === sTgt) || (aId === sTgt && bId === sSrc)) {
              const fA = classNames[cp.classA] || cp.classA;
              const fB = classNames[cp.classB] || cp.classB;
              infoEl.innerHTML = `Legătura ${ce.a.name} - ${ce.b.name} a dispărut. Între ${fA} și ${fB} rămân doar ${cp.edgeCount - 1} legături directe.`;
              return;
            }
          }
        }
      }
      if (infoEl) infoEl.textContent = "Legătura a dispărut. Rețeaua caută alt drum.";
    }

    function switchSubMode(newMode) {
      subMode = newMode;
      resetAllVisuals();
      applyEdgeHighlightIfEdgesMode();
      const modeButtons = controls.querySelectorAll("[data-mode]");
      modeButtons.forEach((b) => {
        if (b.dataset.mode === newMode) { b.classList.add("btn--primary"); b.classList.remove("btn--ghost"); }
        else { b.classList.remove("btn--primary"); b.classList.add("btn--ghost"); }
      });
      const quickRow = controls.querySelector('[data-role="quick"]');
      if (quickRow) quickRow.style.display = (newMode === "people") ? "" : "none";
      const infoEl = controls.querySelector('[data-role="info"]');
      if (infoEl) {
        if (newMode === "edges" && brokenPair) {
          infoEl.innerHTML =
            `Uită-te la relații. Clasa ${brokenPair.classAFriendly} și clasa ${brokenPair.classBFriendly} sunt două lumi care nu se ating aproape deloc. ` +
            `Între ele există o singură legătură directă: ${brokenPair.personA.name} și ${brokenPair.personB.name}. O prietenie. ` +
            `Atinge muchia colorată puternic pentru a o tăia.`;
        } else {
          infoEl.textContent = "Atinge un elev pentru a-l scoate din rețea.";
        }
      }
    }

    // Build UI
    controls.innerHTML =
      `<div class="diff-row diff-buttons try-break__modes">` +
        `<button type="button" class="btn btn--primary" data-mode="people">Oameni</button>` +
        `<button type="button" class="btn btn--ghost" data-mode="edges">Legături</button>` +
      `</div>` +
      `<div class="diff-row diff-buttons try-break__quick" data-role="quick">` +
        (sm.characters?.vedeta
          ? `<button type="button" class="btn btn--ghost" data-quick="vedeta">Scoate${sm.characters.vedeta.sex === "F" ? "-o pe " : "-l pe "}${sm.characters.vedeta.name}</button>`
          : "") +
        `<button type="button" class="btn btn--ghost" data-quick="top5">Scoate cei mai populari 5</button>` +
        (sm.characters?.dependent
          ? `<button type="button" class="btn btn--ghost" data-quick="dependent">Scoate${sm.characters.dependent.sex === "F" ? "-o pe " : "-l pe "}${sm.characters.dependent.name}</button>`
          : "") +
        `<button type="button" class="btn btn--ghost" data-quick="reset">Adu-i înapoi</button>` +
      `</div>` +
      `<div class="diff-hint" data-role="info">Atinge un elev pentru a-l scoate din rețea.</div>` +
      `<div class="diff-hint diff-hint--muted"><strong>${nCutVertices}</strong> elevi obișnuiți sunt singura legătură a cuiva cu restul școlii. Fragilitatea nu e la centru — e la periferie.</div>`;

    controls.querySelectorAll("[data-mode]").forEach((btn) => {
      btn.addEventListener("click", () => switchSubMode(btn.dataset.mode));
    });

    controls.querySelectorAll("[data-quick]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const q = btn.dataset.quick;
        if (q === "reset") { resetAllVisuals(); textForRemovals(); return; }
        if (subMode !== "people") return;
        if (q === "vedeta") {
          const v = sm.characters?.vedeta;
          if (v) removeNodeVisual(String(v.id));
        }
        if (q === "dependent") {
          const d = sm.characters?.dependent;
          if (d) removeNodeVisual(String(d.id));
        }
        if (q === "top5") {
          for (const t of (top5Removal.top5 || [])) removeNodeVisual(String(t.id));
        }
        textForRemovals();
      });
    });

    cy.on("tap", "node", (e) => {
      if (subMode !== "people") return;
      removeNodeVisual(e.target.id());
      textForRemovals();
    });
    cy.on("tap", "edge", (e) => {
      if (subMode !== "edges") return;
      removeEdgeVisual(e.target.id());
    });

    resetAllVisuals();
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
