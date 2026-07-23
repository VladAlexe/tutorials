// Pure-SVG chart variants. No external library for most; cytoscape is loaded
// on demand only for the measure-tabs "Pe hartă" layoutMode: "liber" view.

const _V = new URL(import.meta.url).searchParams.get("v") || "1";
let _cyLoaderPromise = null;
async function _loadCy() {
  if (!_cyLoaderPromise) {
    _cyLoaderPromise = import(`./visualizations.js?v=${_V}`).then((m) => m.loadCytoscape());
  }
  return _cyLoaderPromise;
}

// Cache for computed cose layouts, keyed by network path so we only run
// cose once per session across all three measure cards.
const _cosePositionsCache = new Map();
async function computeCosePositions(netPath) {
  if (_cosePositionsCache.has(netPath)) return _cosePositionsCache.get(netPath);
  const cytoscape = await _loadCy();
  const net = await loadJSON(netPath);
  const elements = [
    ...net.nodes.map((n) => ({ data: { id: String(n.id) } })),
    ...net.edges.filter((e) => (e.weight || 1) >= 4).map((e, i) => ({
      data: { id: `ce${i}`, source: String(e.source), target: String(e.target) }
    })),
  ];
  const container = document.createElement("div");
  container.style.cssText = "position:absolute;left:-99999px;top:-99999px;width:800px;height:800px;";
  document.body.appendChild(container);
  const cy = cytoscape({
    container,
    elements,
    style: [{ selector: "node", style: { "width": 8, "height": 8 } }],
    layout: { name: "cose", animate: false, padding: 40, idealEdgeLength: 60, nodeRepulsion: 4500, randomize: true },
  });
  // Layout runs synchronously with animate:false; positions are set on the
  // instance immediately after the layout returns.
  const positions = {};
  let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
  cy.nodes().forEach((n) => {
    const p = n.position();
    positions[n.id()] = { x: p.x, y: p.y };
    if (p.x < minX) minX = p.x; if (p.x > maxX) maxX = p.x;
    if (p.y < minY) minY = p.y; if (p.y > maxY) maxY = p.y;
  });
  // Normalize to [-1, 1] with a small margin.
  const spanX = (maxX - minX) || 1, spanY = (maxY - minY) || 1;
  const out = {};
  for (const [nid, p] of Object.entries(positions)) {
    out[nid] = {
      x: (((p.x - minX) / spanX) * 2 - 1) * 0.95,
      y: (((p.y - minY) / spanY) * 2 - 1) * 0.95,
    };
  }
  try { cy.destroy(); } catch {}
  container.remove();
  _cosePositionsCache.set(netPath, out);
  return out;
}

async function loadJSON(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`Nu am putut încărca ${path}`);
  return res.json();
}

async function getValues(block) {
  if (Array.isArray(block.values)) return block.values;
  if (block.source && block.field) {
    const data = await loadJSON(block.source);
    return data[block.field] || [];
  }
  return [];
}

async function getStats(block) {
  const src = block.statsSource || "data/highschool-stats.json";
  try { return await loadJSON(src); }
  catch { return null; }
}

function binValues(values, binWidth) {
  if (!values.length) return [];
  const minV = Math.min(...values);
  const maxV = Math.max(...values);
  const startBin = Math.floor(minV / binWidth) * binWidth;
  const nBins = Math.floor((maxV - startBin) / binWidth) + 1;
  const bins = new Array(nBins).fill(0);
  for (const v of values) {
    const idx = Math.floor((v - startBin) / binWidth);
    if (idx >= 0 && idx < nBins) bins[idx]++;
  }
  return bins.map((count, i) => ({
    lo: startBin + i * binWidth,
    hi: startBin + (i + 1) * binWidth - 1,
    count
  }));
}

const COL_BAR   = "#8b4a1e";
const COL_BAR_B = "#3d7a52";
const COL_BAR_C = "#a67433";
const COL_MUTED = "#8a7a68";
const COL_INK   = "#2a1f16";
const COL_INK_S = "#5a4a3a";
const COL_LINE  = "#d9cfc0";
const COL_MEAN  = "#8b4a1e";
const COL_MEDIAN = "#3d7a52";
const COL_BG    = "#faf7f2";

function esc(s) {
  return String(s).replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
}

function fmtNum(v) {
  if (typeof v !== "number") return String(v);
  if (Number.isInteger(v)) return String(v);
  return v.toFixed(1).replace(".", ",");
}

// ---- histogram (with optional slider) -----------------------------------
function histogramSVG(bins, binWidth, block) {
  if (!bins.length) return "";
  const W = 420, H = 220;
  const padL = 34, padR = 12, padT = 22, padB = 42;
  const chartW = W - padL - padR;
  const chartH = H - padT - padB;
  const maxC = Math.max(...bins.map((b) => b.count), 1);
  const barW = chartW / bins.length;

  const bars = bins.map((b, i) => {
    const x = padL + i * barW + 1;
    const h = (b.count / maxC) * chartH;
    const y = padT + chartH - h;
    const label = binWidth === 1 ? `${b.lo}` : `${b.lo}–${b.hi}`;
    return (
      `<rect x="${x.toFixed(1)}" y="${y.toFixed(1)}" ` +
      `width="${(barW - 2).toFixed(1)}" height="${h.toFixed(1)}" fill="${COL_BAR}" rx="1"/>` +
      `<text x="${(x + barW / 2 - 1).toFixed(1)}" y="${(y - 4).toFixed(1)}" ` +
      `text-anchor="middle" font-size="11" fill="${COL_INK_S}">${b.count}</text>` +
      `<text x="${(x + barW / 2 - 1).toFixed(1)}" y="${(H - padB + 14).toFixed(1)}" ` +
      `text-anchor="middle" font-size="10" fill="${COL_MUTED}">${label}</text>`
    );
  }).join("");

  const axisX =
    `<line x1="${padL}" y1="${padT + chartH}" x2="${W - padR}" y2="${padT + chartH}" ` +
    `stroke="${COL_MUTED}" stroke-width="0.5"/>`;
  const xLabel = block.xLabel
    ? `<text x="${W / 2}" y="${H - 6}" text-anchor="middle" font-size="11" fill="${COL_INK_S}">${esc(block.xLabel)}</text>`
    : "";
  const yLabel = block.yLabel
    ? `<text x="${padL - 24}" y="${padT + chartH / 2}" text-anchor="middle" ` +
      `transform="rotate(-90 ${padL - 24} ${padT + chartH / 2})" font-size="11" fill="${COL_INK_S}">` +
      `${esc(block.yLabel)}</text>`
    : "";

  return (
    `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" ` +
    `style="width:100%;height:auto;max-width:500px;display:block;margin:0 auto" ` +
    `role="img" aria-label="${esc(block.title || 'Histogramă')}">` +
    axisX + bars + xLabel + yLabel +
    `</svg>`
  );
}

function renderHistogram(container, block, values) {
  const chartHost = document.createElement("div");
  chartHost.className = "chart__svg-wrap";
  container.appendChild(chartHost);

  const noSlider = block.slider === false;
  const defaultBW = block.defaultBinWidth || 3;

  if (!noSlider) {
    const controls = document.createElement("div");
    controls.className = "chart__controls";
    controls.innerHTML =
      `<label class="chart__slider">Lățime interval ` +
      `<output>${defaultBW}</output>` +
      `<input type="range" min="1" max="7" value="${defaultBW}" step="1"/>` +
      `</label>` +
      `<div class="chart__meta">${values.length} elevi</div>`;
    container.appendChild(controls);

    const slider = controls.querySelector('input[type="range"]');
    const out = controls.querySelector("output");
    function draw() {
      const bw = parseInt(slider.value, 10);
      chartHost.innerHTML = histogramSVG(binValues(values, bw), bw, block);
    }
    slider.addEventListener("input", () => {
      out.textContent = slider.value;
      draw();
    });
    draw();
    return { setValues(v) { values = v; draw(); }, setBinWidth(bw) { slider.value = bw; out.textContent = bw; draw(); } };
  }
  const meta = document.createElement("div");
  meta.className = "chart__meta";
  meta.textContent = `${values.length} elevi · lățime interval ${defaultBW}`;
  container.appendChild(meta);
  const draw = () => { chartHost.innerHTML = histogramSVG(binValues(values, defaultBW), defaultBW, block); };
  draw();
  return {
    setValues(v) { values = v; meta.textContent = `${v.length} elevi · lățime interval ${defaultBW}`; draw(); }
  };
}

// ---- bars ---------------------------------------------------------------
function wrapLabel(text, maxChars) {
  const words = String(text).split(" ");
  const lines = [];
  let cur = "";
  for (const w of words) {
    if ((cur + " " + w).trim().length <= maxChars) cur = (cur + " " + w).trim();
    else { if (cur) lines.push(cur); cur = w; }
  }
  if (cur) lines.push(cur);
  return lines;
}

function barsSVG(block) {
  const bars = block.bars || [];
  if (!bars.length) return "";
  const W = 420, H = 260;
  const padL = 20, padR = 20, padT = 28, padB = 70;
  const chartW = W - padL - padR;
  const chartH = H - padT - padB;
  const maxV = Math.max(...bars.map((b) => b.value), 1);
  const gapRatio = 0.5;
  const barW = chartW / (bars.length + (bars.length - 1) * gapRatio);
  const gap = barW * gapRatio;

  const palette = [COL_BAR, COL_BAR_B];
  const svgBars = bars.map((b, i) => {
    const x = padL + i * (barW + gap);
    const h = (b.value / maxV) * chartH;
    const y = padT + chartH - h;
    const color = b.color || palette[i % palette.length];
    const lines = wrapLabel(b.label, 20);
    const labelParts = lines.map((l, li) => {
      const yy = padT + chartH + 18 + li * 14;
      return `<text x="${(x + barW / 2).toFixed(1)}" y="${yy}" text-anchor="middle" font-size="12" fill="${COL_INK_S}">${esc(l)}</text>`;
    }).join("");
    return (
      `<rect x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${barW.toFixed(1)}" height="${h.toFixed(1)}" fill="${color}" rx="3"/>` +
      `<text x="${(x + barW / 2).toFixed(1)}" y="${(y - 6).toFixed(1)}" text-anchor="middle" font-size="18" font-weight="500" fill="${COL_INK}">${fmtNum(b.value)}</text>` +
      labelParts
    );
  }).join("");

  return (
    `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" ` +
    `style="width:100%;height:auto;max-width:440px;display:block;margin:0 auto" ` +
    `role="img" aria-label="${esc(block.title || 'Grafic în bare')}">` +
    svgBars +
    `</svg>`
  );
}

function renderBars(container, block) {
  const wrap = document.createElement("div");
  wrap.className = "chart__svg-wrap";
  wrap.innerHTML = barsSVG(block);
  container.appendChild(wrap);
}

// Horizontal ranking bars: name + class on the left, colored bar per class,
// value at the bar's right edge. Sorted with the largest on top. Designed
// for the c-gradul, c-deschiderea and any other "top N" card.
const CLASS_PALETTE_ORDER = ["Bio A","Bio B","Bio C","Mate A","Mate B","Mate C","Chimie A","Chimie B","Inginerie"];
function colorForClass(cls) {
  const palette = ["#8b4a1e","#3d7a52","#2f6fa8","#a3341f","#7a5b8c","#b57140","#4c6b3a","#8e5a86","#6a9c8b"];
  const i = CLASS_PALETTE_ORDER.indexOf(cls);
  return palette[(i < 0 ? 0 : i) % palette.length];
}

function hbarsSVG(block) {
  const bars = block.bars || [];
  if (!bars.length) return "";
  // Compact rows so the 8-row card fits within a laptop viewport without
  // scrolling. Wider left padding accommodates "Nour-Eddine, Mate C" etc.
  const rowH = 22;
  const rowGap = 6;
  const padT = 6, padB = 6, padL = 172, padR = 52;
  const W = 520;
  const chartW = W - padL - padR;
  const H = padT + padB + bars.length * (rowH + rowGap) - rowGap;
  const maxV = Math.max(...bars.map((b) => b.value), 1);

  const rows = bars.map((b, i) => {
    const y = padT + i * (rowH + rowGap);
    const w = Math.max(2, (b.value / maxV) * chartW);
    const cls = b.class || "";
    const name = b.name || b.label || "";
    const color = b.color || colorForClass(cls);
    const nameLabel = `${esc(name)}${cls ? `, ${esc(cls)}` : ""}`;
    return (
      `<g class="hbar-row">` +
      `<text x="${padL - 8}" y="${(y + rowH / 2 + 4).toFixed(1)}" text-anchor="end" font-family="Georgia, serif" font-size="12" fill="${COL_INK}">${nameLabel}</text>` +
      `<rect x="${padL}" y="${y.toFixed(1)}" width="${w.toFixed(1)}" height="${rowH}" fill="${color}" rx="2"/>` +
      `<text x="${(padL + w + 6).toFixed(1)}" y="${(y + rowH / 2 + 4).toFixed(1)}" font-family="Georgia, serif" font-size="13" font-weight="500" fill="${COL_INK}">${fmtNum(b.value)}</text>` +
      `</g>`
    );
  }).join("");

  return (
    `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" ` +
    `style="width:100%;height:auto;max-width:560px;display:block;margin:0 auto" ` +
    `role="img" aria-label="${esc(block.title || "Clasament")}">` +
    rows +
    `</svg>`
  );
}

function renderHBars(container, block) {
  const wrap = document.createElement("div");
  wrap.className = "chart__svg-wrap chart__svg-wrap--hbars";
  wrap.innerHTML = hbarsSVG(block);
  container.appendChild(wrap);

  const legendClasses = Array.from(new Set((block.bars || []).map((b) => b.class).filter(Boolean)));
  if (legendClasses.length) {
    const legend = document.createElement("div");
    legend.className = "chart__legend";
    legend.innerHTML = legendClasses.map((cls) =>
      `<span class="chart__legend-chip"><span class="chart__legend-dot" style="background:${colorForClass(cls)}"></span>${esc(cls)}</span>`
    ).join("");
    container.appendChild(legend);
  }
}

// ---- dots (scattered points, seeded random y, tap to reveal name) -------
function seededRandom(seed) {
  let s = seed | 0;
  return function () {
    s = (s * 1664525 + 1013904223) | 0;
    return ((s >>> 0) & 0xffffff) / 0x1000000;
  };
}

async function renderDots(container, block, values, stats) {
  const nodes = (stats && stats.topByDegree) ? null : null;
  // We don't have node ids from stats.degrees. If stats has network reference, look elsewhere.
  const chartHost = document.createElement("div");
  chartHost.className = "chart__svg-wrap";
  container.appendChild(chartHost);

  const W = 480, H = 220;
  const padL = 34, padR = 12, padT = 16, padB = 34;
  const chartW = W - padL - padR;
  const chartH = H - padT - padB;
  const maxV = Math.max(...values, 1);
  const minV = Math.min(...values, 0);
  const rnd = seededRandom(42);

  const dots = values.map((v, i) => {
    const jitterY = rnd();
    const jitterX = rnd();
    const x = padL + jitterX * chartW;
    const y = padT + (1 - (v - minV) / Math.max(1, maxV - minV)) * chartH * 0.85 + jitterY * 12;
    return { x, y, v, i };
  });

  const axisX =
    `<line x1="${padL}" y1="${padT + chartH}" x2="${W - padR}" y2="${padT + chartH}" ` +
    `stroke="${COL_MUTED}" stroke-width="0.5"/>`;
  const yLabel = block.yLabel
    ? `<text x="${padL - 24}" y="${padT + chartH / 2}" text-anchor="middle" ` +
      `transform="rotate(-90 ${padL - 24} ${padT + chartH / 2})" font-size="11" fill="${COL_INK_S}">${esc(block.yLabel)}</text>`
    : "";
  const xLabel = block.xLabel
    ? `<text x="${W / 2}" y="${H - 6}" text-anchor="middle" font-size="11" fill="${COL_INK_S}">${esc(block.xLabel)}</text>`
    : "";
  const yGrid = [0, 5, 10, 15].map(gv => {
    const gy = padT + (1 - (gv - minV) / Math.max(1, maxV - minV)) * chartH * 0.85;
    return `<line x1="${padL}" y1="${gy.toFixed(1)}" x2="${W - padR}" y2="${gy.toFixed(1)}" stroke="${COL_LINE}" stroke-width="0.5"/>` +
           `<text x="${padL - 4}" y="${(gy + 3).toFixed(1)}" text-anchor="end" font-size="10" fill="${COL_MUTED}">${gv}</text>`;
  }).join("");

  const dotsMarkup = dots.map(d =>
    `<circle cx="${d.x.toFixed(1)}" cy="${d.y.toFixed(1)}" r="3.6" fill="${COL_BAR}" fill-opacity="0.65" data-i="${d.i}" data-v="${d.v}"><title>Grad ${d.v}</title></circle>`
  ).join("");

  chartHost.innerHTML =
    `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" ` +
    `style="width:100%;height:auto;max-width:520px;display:block;margin:0 auto" ` +
    `role="img" aria-label="${esc(block.title || 'Puncte împrăștiate')}">` +
    yGrid + axisX + dotsMarkup + xLabel + yLabel +
    `</svg>`;

  const meta = document.createElement("div");
  meta.className = "chart__meta";
  meta.textContent = `${values.length} elevi. Fiecare punct e un elev, gradul e sus.`;
  container.appendChild(meta);
}

// ---- strip (ordered values, animated from scattered) -------------------
function renderStrip(container, block, values) {
  const chartHost = document.createElement("div");
  chartHost.className = "chart__svg-wrap";
  container.appendChild(chartHost);

  const W = 480, H = 220;
  const padL = 34, padR = 12, padT = 16, padB = 34;
  const chartW = W - padL - padR;
  const chartH = H - padT - padB;
  const sorted = [...values].sort((a, b) => a - b);
  const maxV = Math.max(...sorted, 1);
  const minV = Math.min(...sorted, 0);
  const yFor = (v) => padT + (1 - (v - minV) / Math.max(1, maxV - minV)) * chartH * 0.85;

  // Jitter uses same seed as the dots card, so animation appears to continue from #15.
  const rnd = seededRandom(42);
  const jitter = sorted.map((v) => ({ jx: rnd(), jy: rnd() }));
  const scatterX = jitter.map((j) => padL + j.jx * chartW);
  const scatterY = jitter.map((j, i) => yFor(sorted[i]) + j.jy * 12);
  const targetX  = sorted.map((_, i) => padL + (i / Math.max(1, sorted.length - 1)) * chartW);
  const targetY  = sorted.map((v) => yFor(v));

  const axisX =
    `<line x1="${padL}" y1="${padT + chartH}" x2="${W - padR}" y2="${padT + chartH}" ` +
    `stroke="${COL_MUTED}" stroke-width="0.5"/>`;
  const yGrid = [0, 5, 10, 15].map((gv) => {
    const gy = padT + (1 - (gv - minV) / Math.max(1, maxV - minV)) * chartH * 0.85;
    return `<line x1="${padL}" y1="${gy.toFixed(1)}" x2="${W - padR}" y2="${gy.toFixed(1)}" stroke="${COL_LINE}" stroke-width="0.5"/>` +
           `<text x="${padL - 4}" y="${(gy + 3).toFixed(1)}" text-anchor="end" font-size="10" fill="${COL_MUTED}">${gv}</text>`;
  }).join("");

  const dotsMarkup = sorted.map((v, i) => {
    const isTop = i === sorted.length - 1;
    return `<circle cx="${scatterX[i].toFixed(1)}" cy="${scatterY[i].toFixed(1)}" r="${isTop ? 5 : 3.4}" fill="${isTop ? COL_BAR_B : COL_BAR}" fill-opacity="${isTop ? 0.95 : 0.7}" data-i="${i}"><title>Grad ${v}</title></circle>`;
  }).join("");

  const topLabelEl = `<text data-role="top-label" x="${targetX[targetX.length-1].toFixed(1)}" y="${(targetY[targetY.length-1] - 10).toFixed(1)}" text-anchor="middle" font-size="12" fill="${COL_INK}" opacity="0">${esc(block.topLabel || "vârf")}</text>`;

  const xLabel = block.xLabel
    ? `<text x="${W / 2}" y="${H - 6}" text-anchor="middle" font-size="11" fill="${COL_INK_S}">${esc(block.xLabel)}</text>`
    : "";

  chartHost.innerHTML =
    `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" ` +
    `style="width:100%;height:auto;max-width:520px;display:block;margin:0 auto" ` +
    `role="img" aria-label="${esc(block.title || 'Valori ordonate')}">` +
    yGrid + axisX + dotsMarkup + topLabelEl + xLabel +
    `</svg>`;

  const circles = chartHost.querySelectorAll("circle");
  const topLabel = chartHost.querySelector('[data-role="top-label"]');
  const reduced = typeof window !== "undefined" && window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const DUR = reduced ? 0 : 900;
  const start = (typeof performance !== "undefined" && performance.now) ? performance.now() : Date.now();
  function frame() {
    const now = (typeof performance !== "undefined" && performance.now) ? performance.now() : Date.now();
    const t = DUR ? Math.min(1, (now - start) / DUR) : 1;
    const eased = t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
    circles.forEach((c, i) => {
      const x = scatterX[i] + (targetX[i] - scatterX[i]) * eased;
      const y = scatterY[i] + (targetY[i] - scatterY[i]) * eased;
      c.setAttribute("cx", x.toFixed(1));
      c.setAttribute("cy", y.toFixed(1));
    });
    if (topLabel) topLabel.setAttribute("opacity", eased.toFixed(2));
    if (t < 1) requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);

  const meta = document.createElement("div");
  meta.className = "chart__meta";
  meta.textContent = `${values.length} elevi ordonați crescător.`;
  container.appendChild(meta);
}

// ---- freq: table + bars for class composition ---------------------------
function statsBucket(block, stats) {
  return block.dataset && stats?.[block.dataset] ? stats[block.dataset] : stats;
}

async function loadNodesForLink(block) {
  const path = block.linkNetworkData || "data/highschool-network.json";
  try {
    const d = await loadJSON(path);
    const nodes = d.nodes || [];
    const edges = d.edges || [];
    const deg = new Map();
    for (const e of edges) {
      if ((e.weight || 0) < 4) continue;
      deg.set(e.source, (deg.get(e.source) || 0) + 1);
      deg.set(e.target, (deg.get(e.target) || 0) + 1);
    }
    for (const n of nodes) {
      if (n.degree == null) n.degree = deg.get(n.id) || 0;
    }
    return nodes;
  } catch { return []; }
}

function renderFreq(container, block, stats) {
  const src = statsBucket(block, stats);
  const cf = src?.classFreq || {};
  const classNames = stats?.classNames || {};
  const friendly = (k) => classNames[k] || k;
  const rowsRaw = Object.entries(cf).filter(([k]) => k !== "globalBetweenPct");
  const total = rowsRaw.reduce((s, [, v]) => s + (v.n || 0), 0);
  const totalF = rowsRaw.reduce((s, [, v]) => s + (v.nF || 0), 0);
  const totalM = rowsRaw.reduce((s, [, v]) => s + (v.nM || 0), 0);
  const totalUnk = rowsRaw.reduce((s, [, v]) => s + (v.nUnk || 0), 0);

  // Toggle so only one view is visible at a time. Tabel = counts, Grafic = bars.
  const toggle = document.createElement("div");
  toggle.className = "chart__toggle";
  const btnTable = document.createElement("button");
  btnTable.type = "button";
  btnTable.className = "chart__toggle__btn is-active";
  btnTable.textContent = "Tabel";
  const btnBars = document.createElement("button");
  btnBars.type = "button";
  btnBars.className = "chart__toggle__btn";
  btnBars.textContent = "Grafic";
  toggle.appendChild(btnTable);
  toggle.appendChild(btnBars);
  container.appendChild(toggle);

  const tableWrap = document.createElement("div");
  tableWrap.className = "chart__freq-view";
  const table = document.createElement("table");
  table.className = "chart__freq";
  const header = `<tr><th></th><th>elevi</th><th>fete</th><th>băieți</th><th>?</th></tr>`;
  const body = rowsRaw.map(([k, v]) =>
    `<tr data-raw="${esc(k)}"><th>${esc(friendly(k))}</th><td>${v.n}</td><td>${v.nF}</td><td>${v.nM}</td><td>${v.nUnk || 0}</td></tr>`
  ).join("");
  table.innerHTML = header + body +
    `<tr class="chart__freq__total"><th>total</th><td>${total}</td><td>${totalF}</td><td>${totalM}</td><td>${totalUnk}</td></tr>`;
  tableWrap.appendChild(table);
  const note = document.createElement("p");
  note.className = "chart__note";
  note.textContent = "Sexul nu e cunoscut pentru câțiva elevi; îi trecem în ultima coloană.";
  tableWrap.appendChild(note);
  container.appendChild(tableWrap);

  // 100% stacked horizontal bars, sorted by %F desc
  const sorted = [...rowsRaw]
    .map(([k, v]) => {
      const known = (v.nF || 0) + (v.nM || 0);
      const pctF = v.n ? 100 * (v.nF || 0) / v.n : 0;
      const pctM = v.n ? 100 * (v.nM || 0) / v.n : 0;
      const pctU = v.n ? 100 * (v.nUnk || 0) / v.n : 0;
      return { label: k, n: v.n, nF: v.nF || 0, nM: v.nM || 0, nUnk: v.nUnk || 0, pctF, pctM, pctU };
    })
    .sort((a, b) => b.pctF - a.pctF);

  const nRows = sorted.length;
  const W = 480, H = 40 + nRows * 34;
  const padL = 70, padR = 40, padT = 20, padB = 32;
  const chartW = W - padL - padR;
  const rowH = 24;

  const svgRows = sorted.map((v, i) => {
    const y = padT + i * (rowH + 6);
    const wF = (v.pctF / 100) * chartW;
    const wM = (v.pctM / 100) * chartW;
    const wU = (v.pctU / 100) * chartW;
    const showFText = wF > 42;
    const showMText = wM > 42;
    return (
      `<g class="freq-bar" data-class="${esc(v.label)}" style="cursor:pointer">` +
      `<rect x="${padL - 60}" y="${y - 2}" width="${(chartW + 70).toFixed(1)}" height="${(rowH + 4).toFixed(1)}" fill="transparent"/>` +
      `<text x="${padL - 6}" y="${(y + rowH / 2 + 4).toFixed(1)}" text-anchor="end" font-size="12" fill="${COL_INK}" font-family="Georgia, serif">${esc(friendly(v.label))}</text>` +
      `<rect x="${padL}" y="${y.toFixed(1)}" width="${wF.toFixed(1)}" height="${rowH}" fill="${COL_BAR_B}"/>` +
      `<rect x="${(padL + wF).toFixed(1)}" y="${y.toFixed(1)}" width="${wM.toFixed(1)}" height="${rowH}" fill="${COL_BAR}"/>` +
      `<rect x="${(padL + wF + wM).toFixed(1)}" y="${y.toFixed(1)}" width="${wU.toFixed(1)}" height="${rowH}" fill="${COL_MUTED}"/>` +
      (showFText ? `<text x="${(padL + wF / 2).toFixed(1)}" y="${(y + rowH / 2 + 4).toFixed(1)}" text-anchor="middle" font-size="11" fill="${COL_BG}">${Math.round(v.pctF)}%</text>` : "") +
      (showMText ? `<text x="${(padL + wF + wM / 2).toFixed(1)}" y="${(y + rowH / 2 + 4).toFixed(1)}" text-anchor="middle" font-size="11" fill="${COL_BG}">${Math.round(v.pctM)}%</text>` : "") +
      `<text x="${(padL + chartW + 4).toFixed(1)}" y="${(y + rowH / 2 + 4).toFixed(1)}" font-size="11" fill="${COL_MUTED}">${v.n}</text>` +
      `</g>`
    );
  }).join("");

  const legend =
    `<g transform="translate(${padL}, ${H - 10})">` +
    `<rect x="0" y="-10" width="10" height="10" fill="${COL_BAR_B}"/>` +
    `<text x="14" y="-1" font-size="11" fill="${COL_INK_S}">fete</text>` +
    `<rect x="60" y="-10" width="10" height="10" fill="${COL_BAR}"/>` +
    `<text x="74" y="-1" font-size="11" fill="${COL_INK_S}">băieți</text>` +
    `<rect x="132" y="-10" width="10" height="10" fill="${COL_MUTED}"/>` +
    `<text x="146" y="-1" font-size="11" fill="${COL_INK_S}">necunoscut</text>` +
    `</g>`;

  const barsWrap = document.createElement("div");
  barsWrap.className = "chart__freq-view";
  barsWrap.hidden = true;
  const svg = document.createElement("div");
  svg.className = "chart__svg-wrap chart__svg-wrap--freq";
  svg.innerHTML =
    `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" ` +
    `style="width:100%;height:auto;max-width:520px;display:block;margin:0 auto" ` +
    `role="img" aria-label="Compoziția claselor sortate după procent fete">` +
    svgRows + legend +
    `</svg>`;
  barsWrap.appendChild(svg);
  container.appendChild(barsWrap);

  function showView(which) {
    const isTable = which === "table";
    tableWrap.hidden = !isTable;
    barsWrap.hidden = isTable;
    btnTable.classList.toggle("is-active", isTable);
    btnBars.classList.toggle("is-active", !isTable);
  }
  btnTable.addEventListener("click", () => showView("table"));
  btnBars.addEventListener("click", () => showView("bars"));

  if (block.linkNetwork) {
    const rowsHost = document.createElement("div");
    rowsHost.className = "chart__link-target";
    rowsHost.textContent = "Atinge un rând din tabel sau o bară pentru lista de nume și procentele.";
    container.appendChild(rowsHost);
    let nodesCache = null;
    async function ensureNodes() { if (!nodesCache) nodesCache = await loadNodesForLink(block); return nodesCache; }
    async function showClass(clsRaw) {
      const info = sorted.find((r) => r.label === clsRaw);
      const ns = await ensureNodes();
      // network nodes may carry the class code under either group or clasa;
      // compare on raw code so friendly-label rewrites do not break the lookup.
      const matching = ns.filter((n) => (n.group || n.clasa) === clsRaw);
      const pctLine = info ? ` · ${Math.round(info.pctF)}% fete, ${Math.round(info.pctM)}% băieți${info.nUnk ? `, ${Math.round(info.pctU)}% ?` : ""}` : "";
      const names = matching
        .map((n) => ({ n, deg: n.degree ?? n.pop ?? 0 }))
        .sort((a, b) => (b.deg || 0) - (a.deg || 0))
        .map(({ n, deg }) => deg ? `${esc(n.name || n.id)} (${deg})` : esc(n.name || n.id))
        .join(", ");
      rowsHost.innerHTML = `<strong>${esc(friendly(clsRaw))}</strong> (${matching.length} elevi${pctLine}): ` + names;
    }
    const tableRows = container.querySelectorAll(".chart__freq tr");
    tableRows.forEach((tr, idx) => {
      if (idx === 0 || tr.classList.contains("chart__freq__total")) return;
      const raw = tr.dataset.raw;
      if (!raw) return;
      tr.classList.add("chart__freq__tappable");
      tr.addEventListener("click", () => showClass(raw));
    });
    svg.querySelectorAll(".freq-bar").forEach((g) => {
      g.addEventListener("click", () => showClass(g.dataset.class));
    });
  }
}

// ---- grouped-strip: mean bars per class + individual points overlay -----
function renderGroupedStrip(container, block, stats) {
  const src = statsBucket(block, stats);
  const cmd = src?.classMeanDegree || {};
  const rows = Object.entries(cmd);
  if (!rows.length) { container.textContent = "Fără date."; return; }

  const W = 480, H = 260;
  const padL = 26, padR = 12, padT = 24, padB = 46;
  const chartW = W - padL - padR;
  const chartH = H - padT - padB;
  const maxV = Math.max(...rows.flatMap(([, v]) => [v.mean, ...(v.degrees || [0])]), 1);

  const groupW = chartW / rows.length;
  const barW = groupW * 0.55;

  const parts = rows.map(([label, v], gi) => {
    const cx = padL + gi * groupW + groupW / 2;
    const barX = cx - barW / 2;
    const meanH = (v.mean / maxV) * chartH;
    const meanY = padT + chartH - meanH;

    const rndY = seededRandom(gi + 7);
    const rndX = seededRandom(gi + 11);
    const dots = (v.degrees || []).map((d) => {
      const dx = cx + (rndX() - 0.5) * (barW - 8);
      const dh = (d / maxV) * chartH;
      const dy = padT + chartH - dh + (rndY() - 0.5) * 4;
      return `<circle cx="${dx.toFixed(1)}" cy="${dy.toFixed(1)}" r="3" fill="${COL_INK}" fill-opacity="0.35"/>`;
    }).join("");

    return (
      `<rect x="${barX.toFixed(1)}" y="${meanY.toFixed(1)}" width="${barW.toFixed(1)}" height="${meanH.toFixed(1)}" fill="${COL_BAR}" fill-opacity="0.30" rx="3"/>` +
      dots +
      `<line x1="${(barX - 6).toFixed(1)}" y1="${meanY.toFixed(1)}" x2="${(barX + barW + 6).toFixed(1)}" y2="${meanY.toFixed(1)}" stroke="${COL_MEAN}" stroke-width="2"/>` +
      `<text x="${cx.toFixed(1)}" y="${(meanY - 8).toFixed(1)}" text-anchor="middle" font-size="13" font-weight="500" fill="${COL_INK}">${fmtNum(v.mean)}</text>` +
      `<text x="${cx.toFixed(1)}" y="${(padT + chartH + 18).toFixed(1)}" text-anchor="middle" font-size="12" fill="${COL_INK_S}">${esc(label)}</text>` +
      `<text x="${cx.toFixed(1)}" y="${(padT + chartH + 32).toFixed(1)}" text-anchor="middle" font-size="10" fill="${COL_MUTED}">${(v.degrees||[]).length} elevi</text>`
    );
  }).join("");

  const svg = document.createElement("div");
  svg.className = "chart__svg-wrap";
  svg.innerHTML =
    `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" ` +
    `style="width:100%;height:auto;max-width:520px;display:block;margin:0 auto" ` +
    `role="img" aria-label="Grade medii pe clase">` +
    parts +
    `</svg>`;
  container.appendChild(svg);

  const meta = document.createElement("div");
  meta.className = "chart__meta";
  meta.textContent = "Bara: media pe clasă. Punctele: fiecare elev.";
  container.appendChild(meta);
}

// ---- stacked: intern/extern % per clasa ---------------------------------
function renderStacked(container, block, stats) {
  const src = statsBucket(block, stats);
  const ccs = src?.classContactSplit || {};
  const rows = Object.entries(ccs).filter(([k]) => k !== "globalBetweenPct");
  if (!rows.length) { container.textContent = "Fără date."; return; }

  const W = 480, H = 200;
  const padL = 60, padR = 20, padT = 20, padB = 40;
  const chartW = W - padL - padR;
  const chartH = H - padT - padB;
  const rowH = chartH / rows.length;

  const svgRows = rows.map(([label, v], i) => {
    const y = padT + i * rowH + rowH * 0.15;
    const h = rowH * 0.6;
    const wInternal = (v.internalPct / 100) * chartW;
    const wExternal = (v.externalPct / 100) * chartW;
    return (
      `<g class="stacked-row" data-class="${esc(label)}" style="cursor:pointer">` +
      `<rect x="${padL - 40}" y="${y.toFixed(1)}" width="${(chartW + 40).toFixed(1)}" height="${h.toFixed(1)}" fill="transparent"/>` +
      `<text x="${padL - 6}" y="${(y + h / 2 + 4).toFixed(1)}" text-anchor="end" font-size="12" fill="${COL_INK_S}">${esc(label)}</text>` +
      `<rect x="${padL}" y="${y.toFixed(1)}" width="${wInternal.toFixed(1)}" height="${h.toFixed(1)}" fill="${COL_BAR}" rx="2"/>` +
      `<rect x="${(padL + wInternal).toFixed(1)}" y="${y.toFixed(1)}" width="${wExternal.toFixed(1)}" height="${h.toFixed(1)}" fill="${COL_BAR_C}" rx="2"/>` +
      `<text x="${(padL + wInternal / 2).toFixed(1)}" y="${(y + h / 2 + 4).toFixed(1)}" text-anchor="middle" font-size="11" fill="${COL_BG}">${fmtNum(v.internalPct)}%</text>` +
      `<text x="${(padL + wInternal + wExternal / 2).toFixed(1)}" y="${(y + h / 2 + 4).toFixed(1)}" text-anchor="middle" font-size="11" fill="${COL_INK}">${fmtNum(v.externalPct)}%</text>` +
      `</g>`
    );
  }).join("");

  const legend =
    `<g transform="translate(${padL}, ${H - 14})">` +
    `<rect x="0" y="-10" width="10" height="10" fill="${COL_BAR}"/>` +
    `<text x="14" y="-1" font-size="11" fill="${COL_INK_S}">intern (aceeași clasă)</text>` +
    `<rect x="180" y="-10" width="10" height="10" fill="${COL_BAR_C}"/>` +
    `<text x="194" y="-1" font-size="11" fill="${COL_INK_S}">extern (altă clasă)</text>` +
    `</g>`;

  const svg = document.createElement("div");
  svg.className = "chart__svg-wrap";
  svg.innerHTML =
    `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" ` +
    `style="width:100%;height:auto;max-width:520px;display:block;margin:0 auto" ` +
    `role="img" aria-label="Timp de contact pe clase">` +
    svgRows + legend +
    `</svg>`;
  container.appendChild(svg);

  if (block.linkNetwork) {
    const rowsHost = document.createElement("div");
    rowsHost.className = "chart__link-target";
    rowsHost.textContent = "Atinge o bară pentru numele elevilor din acea clasă.";
    container.appendChild(rowsHost);
    let nodesCache = null;
    async function ensureNodes() { if (!nodesCache) nodesCache = await loadNodesForLink(block); return nodesCache; }
    svg.querySelectorAll(".stacked-row").forEach((g) => {
      g.addEventListener("click", async () => {
        const cls = g.dataset.class;
        const ns = await ensureNodes();
        const matching = ns.filter((n) => (n.group || n.clasa) === cls);
        rowsHost.innerHTML = `<strong>${esc(cls)}</strong> (${matching.length} elevi): ` +
          matching.map((n) => esc(n.name || n.id)).join(", ");
      });
    });
  }
}

// ---- states: dots with commanded arrangements (scatter, sorted, grouped)
async function renderStates(container, block, values, stats) {
  const chartHost = document.createElement("div");
  chartHost.className = "chart__svg-wrap";
  container.appendChild(chartHost);

  const W = 480, H = 220;
  const padL = 34, padR = 12, padT = 16, padB = 34;
  const chartW = W - padL - padR;
  const chartH = H - padT - padB;
  const maxV = Math.max(...values, 1);
  const minV = Math.min(...values, 0);
  const rnd = seededRandom(42);
  const jitter = values.map(() => ({ jx: rnd(), jy: rnd() }));

  // Precompute positions for each state
  function scatterPos(i, v) {
    return {
      x: padL + jitter[i].jx * chartW,
      y: padT + (1 - (v - minV) / Math.max(1, maxV - minV)) * chartH * 0.85 + jitter[i].jy * 12,
    };
  }
  function sortedPos(i, v, sortedIdx) {
    return {
      x: padL + (sortedIdx / Math.max(1, values.length - 1)) * chartW,
      y: padT + (1 - (v - minV) / Math.max(1, maxV - minV)) * chartH * 0.85,
    };
  }
  // Groups: derive from block.groupField pointing into stats, e.g. sliceMetrics.communities.byId
  const groups = block.groupField
    ? (function () {
        const g = block.groupField.split(".").reduce((o, k) => (o ? o[k] : null), stats) || {};
        return values.map((_, i) => g[String(block.nodeIds ? block.nodeIds[i] : i)] ?? 0);
      })()
    : values.map(() => 0);

  const groupCounts = {};
  groups.forEach((g) => { groupCounts[g] = (groupCounts[g] || 0) + 1; });
  const groupOrder = Object.keys(groupCounts).sort();
  const groupCumPos = {};
  let acc = 0;
  const gap = 8;
  const groupBoxes = {};
  const totalGaps = (groupOrder.length - 1) * gap;
  const availW = chartW - totalGaps;
  for (const g of groupOrder) {
    const w = availW * (groupCounts[g] / values.length);
    groupBoxes[g] = { start: acc, width: w };
    acc += w + gap;
  }
  const groupIndexIn = {};
  groups.forEach((g, i) => {
    groupIndexIn[i] = (groupIndexIn[g + "_c"] = (groupIndexIn[g + "_c"] || 0));
    groupIndexIn[g + "_c"]++;
  });
  function groupedPos(i, v) {
    const g = groups[i];
    const box = groupBoxes[g] || { start: 0, width: chartW };
    const idxInGroup = groupIndexIn[i] || 0;
    const denom = Math.max(1, groupCounts[g] - 1);
    return {
      x: padL + box.start + (denom ? (idxInGroup / denom) * box.width : box.width / 2),
      y: padT + (1 - (v - minV) / Math.max(1, maxV - minV)) * chartH * 0.85,
    };
  }

  const sortedIdx = [...values.map((v, i) => i)].sort((a, b) => values[a] - values[b]);
  const rankOf = new Array(values.length);
  sortedIdx.forEach((origIdx, rank) => { rankOf[origIdx] = rank; });

  const states = block.states || [
    { label: "Împrăștiat", key: "scatter" },
    { label: "Ordonat", key: "sorted" },
    { label: "Grupat", key: "grouped" },
  ];

  const axisX = `<line x1="${padL}" y1="${padT + chartH}" x2="${W - padR}" y2="${padT + chartH}" stroke="${COL_MUTED}" stroke-width="0.5"/>`;

  // Precompute bin layout so we can add a count label per column. Declared
  // BEFORE the dot markup so both the histogram state and the count labels
  // read from the same source of truth.
  const BW = block.binWidth || 3;
  const startBin = Math.floor(minV / BW) * BW;
  const maxHi = Math.max(...values);
  const nBins = Math.floor((maxHi - startBin) / BW) + 1;
  const binPx = chartW / nBins;
  const DOT_SIZE = 7;
  const binCounts = new Array(nBins).fill(0);
  for (const v of values) {
    const idx = Math.floor((v - startBin) / BW);
    if (idx >= 0 && idx < nBins) binCounts[idx]++;
  }

  const initialPos = values.map((v, i) => scatterPos(i, v));
  const dots = initialPos.map((p, i) =>
    `<circle cx="${p.x.toFixed(1)}" cy="${p.y.toFixed(1)}" r="3.5" fill="${COL_BAR}" fill-opacity="0.7"><title>${values[i]}</title></circle>`
  ).join("");

  // Count labels — one per bin, hidden except when the histogram state is
  // active. Position them above the tallest possible column so they clear
  // the dots regardless of animation.
  const countLabels = binCounts.map((c, i) => {
    const x = padL + i * binPx + binPx / 2;
    const y = padT + chartH - c * DOT_SIZE - 6;
    return `<text class="states-count" data-bin="${i}" x="${x.toFixed(1)}" y="${y.toFixed(1)}" text-anchor="middle" font-size="12" font-weight="500" fill="${COL_INK}" opacity="0">${c}</text>`;
  }).join("");

  chartHost.innerHTML =
    `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto;max-width:520px;display:block;margin:0 auto">` +
    axisX + dots + countLabels + `</svg>`;

  const circles = chartHost.querySelectorAll("circle");
  const countTexts = chartHost.querySelectorAll(".states-count");
  let currentPos = initialPos;

  function setCountsVisible(visible) {
    countTexts.forEach((t) => {
      t.setAttribute("opacity", visible ? "1" : "0");
    });
  }

  function histogramPos(i, v) {
    const binIdx = Math.floor((v - startBin) / BW);
    const x = padL + binIdx * binPx + binPx / 2;
    let rank = 0;
    for (let j = 0; j < i; j++) {
      if (Math.floor((values[j] - startBin) / BW) === binIdx) rank++;
    }
    return { x, y: padT + chartH - (rank + 1) * DOT_SIZE };
  }

  function positionsFor(key) {
    if (key === "sorted") return values.map((v, i) => sortedPos(i, v, rankOf[i]));
    if (key === "grouped") return values.map((v, i) => groupedPos(i, v));
    if (key === "histogram") return values.map((v, i) => histogramPos(i, v));
    return values.map((v, i) => scatterPos(i, v));
  }

  function transitionTo(target, dur = 800) {
    const start = performance.now();
    const startPos = currentPos.map((p) => ({ x: p.x, y: p.y }));
    function frame() {
      const t = Math.min(1, (performance.now() - start) / dur);
      const eased = t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
      circles.forEach((c, i) => {
        const x = startPos[i].x + (target[i].x - startPos[i].x) * eased;
        const y = startPos[i].y + (target[i].y - startPos[i].y) * eased;
        c.setAttribute("cx", x.toFixed(1));
        c.setAttribute("cy", y.toFixed(1));
      });
      if (t < 1) requestAnimationFrame(frame);
      else currentPos = target;
    }
    requestAnimationFrame(frame);
  }

  const controls = document.createElement("div");
  controls.className = "chart__controls chart__states-controls";
  controls.innerHTML = states.map((s, i) => `<button type="button" class="btn ${i === 0 ? "btn--primary" : "btn--ghost"}" data-state="${s.key}">${s.label}</button>`).join("");
  container.appendChild(controls);
  controls.querySelectorAll("[data-state]").forEach((btn) => {
    btn.addEventListener("click", () => {
      controls.querySelectorAll("[data-state]").forEach((b) => { b.classList.remove("btn--primary"); b.classList.add("btn--ghost"); });
      btn.classList.remove("btn--ghost"); btn.classList.add("btn--primary");
      const key = btn.dataset.state;
      transitionTo(positionsFor(key));
      // Counts appear only in the histogram state, matching the verb "numără".
      setCountsVisible(key === "histogram");
    });
  });
}

// ---- sex-composition: 100% stacked bars F/M per class -------------------
function renderSexComposition(container, block, stats) {
  const src = statsBucket(block, stats);
  const csx = src?.classSexComposition || {};
  const rows = Object.entries(csx);
  if (!rows.length) { container.textContent = "Fără date de compoziție pe sex."; return; }

  const W = 480, H = Math.max(200, 40 + rows.length * 30);
  const padL = 60, padR = 40, padT = 20, padB = 40;
  const chartW = W - padL - padR;
  const chartH = H - padT - padB;
  const rowH = chartH / rows.length;

  const svgRows = rows.map(([label, v], i) => {
    const y = padT + i * rowH + rowH * 0.15;
    const h = rowH * 0.6;
    const wF = (v.pctF / 100) * chartW;
    const wM = (v.pctM / 100) * chartW;
    return (
      `<text x="${padL - 6}" y="${(y + h / 2 + 4).toFixed(1)}" text-anchor="end" font-size="11" fill="${COL_INK_S}">${esc(label)}</text>` +
      `<rect x="${padL}" y="${y.toFixed(1)}" width="${wF.toFixed(1)}" height="${h.toFixed(1)}" fill="${COL_BAR_B}" rx="2"/>` +
      `<rect x="${(padL + wF).toFixed(1)}" y="${y.toFixed(1)}" width="${wM.toFixed(1)}" height="${h.toFixed(1)}" fill="${COL_BAR}" rx="2"/>` +
      `<text x="${(padL + wF / 2).toFixed(1)}" y="${(y + h / 2 + 4).toFixed(1)}" text-anchor="middle" font-size="10" fill="${COL_BG}">${Math.round(v.pctF)}%</text>` +
      `<text x="${(padL + wF + wM / 2).toFixed(1)}" y="${(y + h / 2 + 4).toFixed(1)}" text-anchor="middle" font-size="10" fill="${COL_BG}">${Math.round(v.pctM)}%</text>` +
      `<text x="${(padL + chartW + 4).toFixed(1)}" y="${(y + h / 2 + 4).toFixed(1)}" font-size="10" fill="${COL_MUTED}">${v.n}</text>`
    );
  }).join("");

  const legend =
    `<g transform="translate(${padL}, ${H - 14})">` +
    `<rect x="0" y="-10" width="10" height="10" fill="${COL_BAR_B}"/>` +
    `<text x="14" y="-1" font-size="11" fill="${COL_INK_S}">fete</text>` +
    `<rect x="80" y="-10" width="10" height="10" fill="${COL_BAR}"/>` +
    `<text x="94" y="-1" font-size="11" fill="${COL_INK_S}">băieți</text>` +
    `</g>`;

  const svg = document.createElement("div");
  svg.className = "chart__svg-wrap";
  svg.innerHTML =
    `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" ` +
    `style="width:100%;height:auto;max-width:520px;display:block;margin:0 auto" ` +
    `role="img" aria-label="Compoziția pe sex a claselor">` +
    svgRows + legend +
    `</svg>`;
  container.appendChild(svg);
}

// ---- meanmedian: histogram + mean/median lines + cursor -----------------
function meanOf(arr) { return arr.reduce((a, b) => a + b, 0) / (arr.length || 1); }
function medianOf(arr) {
  const s = [...arr].sort((a, b) => a - b);
  const n = s.length;
  if (!n) return 0;
  return n % 2 ? s[(n - 1) / 2] : (s[n / 2 - 1] + s[n / 2]) / 2;
}

function meanmedianChartHTML(baseValues, extras, block) {
  const values = [...baseValues, ...extras];
  const binWidth = block.defaultBinWidth || 3;
  const bins = binValues(values, binWidth);
  if (!bins.length) return { svg: "", mean: 0, median: 0 };

  const W = 480, H = 240;
  const padL = 40, padR = 12, padT = 22, padB = 42;
  const chartW = W - padL - padR;
  const chartH = H - padT - padB;
  const maxC = Math.max(...bins.map((b) => b.count), 1);
  const barW = chartW / bins.length;
  const minLo = bins[0].lo;
  const maxHi = bins[bins.length - 1].hi;
  const xForValue = (v) => padL + ((v - minLo) / Math.max(1, maxHi + 1 - minLo)) * chartW;

  const bars = bins.map((b, i) => {
    const x = padL + i * barW + 1;
    const h = (b.count / maxC) * chartH;
    const y = padT + chartH - h;
    return `<rect x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${(barW - 2).toFixed(1)}" height="${h.toFixed(1)}" fill="${COL_BAR}" fill-opacity="0.85" rx="1"/>`;
  }).join("");

  const mean = meanOf(values);
  const median = medianOf(values);
  const xMean = xForValue(mean);
  const xMedian = xForValue(median);

  const meanLine =
    `<line x1="${xMean.toFixed(1)}" y1="${padT - 2}" x2="${xMean.toFixed(1)}" y2="${(padT + chartH).toFixed(1)}" stroke="${COL_MEAN}" stroke-width="2"/>` +
    `<text x="${xMean.toFixed(1)}" y="${(padT - 6).toFixed(1)}" text-anchor="middle" font-size="12" fill="${COL_MEAN}">medie ${fmtNum(Math.round(mean * 10) / 10)}</text>`;
  const medianLine =
    `<line x1="${xMedian.toFixed(1)}" y1="${padT - 2}" x2="${xMedian.toFixed(1)}" y2="${(padT + chartH).toFixed(1)}" stroke="${COL_MEDIAN}" stroke-width="2" stroke-dasharray="4 3"/>` +
    `<text x="${xMedian.toFixed(1)}" y="${(padT + chartH + 24).toFixed(1)}" text-anchor="middle" font-size="12" fill="${COL_MEDIAN}">median ${fmtNum(Math.round(median * 10) / 10)}</text>`;

  const axisX =
    `<line x1="${padL}" y1="${padT + chartH}" x2="${W - padR}" y2="${padT + chartH}" stroke="${COL_MUTED}" stroke-width="0.5"/>`;
  const ticks = [];
  const step = Math.max(1, Math.ceil((maxHi + 1 - minLo) / 10));
  for (let v = minLo; v <= maxHi + 1; v += step) {
    const tx = xForValue(v);
    ticks.push(`<text x="${tx.toFixed(1)}" y="${(padT + chartH + 14).toFixed(1)}" text-anchor="middle" font-size="10" fill="${COL_MUTED}">${v}</text>`);
  }

  return {
    svg:
      `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" ` +
      `style="width:100%;height:auto;max-width:520px;display:block;margin:0 auto" ` +
      `role="img" aria-label="Media și medianul">` +
      axisX + bars + ticks.join("") + meanLine + medianLine +
      `</svg>`,
    mean, median
  };
}

function renderMeanMedian(container, block, values) {
  const chartHost = document.createElement("div");
  chartHost.className = "chart__svg-wrap";
  container.appendChild(chartHost);

  const controls = document.createElement("div");
  controls.className = "chart__controls";
  controls.innerHTML =
    `<label class="chart__slider">Adaugă un elev cu gradul <output>0</output>` +
    `<input type="range" min="0" max="200" value="0" step="1"/></label>` +
    `<div class="chart__meta">media <span data-role="mean">–</span> · median <span data-role="median">–</span></div>`;
  container.appendChild(controls);

  const slider = controls.querySelector('input[type="range"]');
  const out = controls.querySelector("output");
  const meanEl = controls.querySelector('[data-role="mean"]');
  const medEl  = controls.querySelector('[data-role="median"]');

  function draw() {
    const extras = parseInt(slider.value, 10) > 0 ? [parseInt(slider.value, 10)] : [];
    const res = meanmedianChartHTML(values, extras, block);
    chartHost.innerHTML = res.svg;
    meanEl.textContent = fmtNum(Math.round(res.mean * 10) / 10);
    medEl.textContent  = fmtNum(Math.round(res.median * 10) / 10);
  }
  slider.addEventListener("input", () => {
    out.textContent = slider.value;
    draw();
  });
  draw();
}

// ---- outcome-histogram (SIR outcomes) -----------------------------------
export function renderOutcomeHistogram(container, outcomes, block) {
  container.innerHTML = "";
  const bins = binValues(outcomes, block.binWidth || 10);
  container.innerHTML = histogramSVG(bins, block.binWidth || 10, block);
}

// ---- triple-histogram: three mini-histograms compared -------------------
function walkStatsPath(stats, path) {
  const parts = path.split(".");
  let cur = stats;
  for (const p of parts) {
    if (cur == null) return null;
    if (Array.isArray(cur)) { const i = Number(p); cur = Number.isFinite(i) ? cur[i] : cur[p]; }
    else cur = cur[p];
  }
  return cur;
}

function miniHistogramSVG(values, binWidth, title) {
  if (!values || !values.length) return `<div class="triple__cell"><div class="triple__title">${esc(title)}</div><div class="triple__empty">Fără date</div></div>`;
  const bins = binValues(values, binWidth);
  const W = 260, H = 160;
  const padL = 22, padR = 8, padT = 20, padB = 26;
  const chartW = W - padL - padR;
  const chartH = H - padT - padB;
  const maxC = Math.max(...bins.map((b) => b.count), 1);
  const barW = chartW / bins.length;
  const mn = values.reduce((a, b) => a + b, 0) / values.length;
  const sorted = [...values].sort((a, b) => a - b);
  const md = sorted.length % 2 ? sorted[(sorted.length - 1) / 2] : (sorted[sorted.length / 2 - 1] + sorted[sorted.length / 2]) / 2;
  const minLo = bins[0].lo;
  const maxHi = bins[bins.length - 1].hi;
  const xFor = (v) => padL + ((v - minLo) / Math.max(1, maxHi + 1 - minLo)) * chartW;

  const bars = bins.map((b, i) => {
    const x = padL + i * barW + 0.5;
    const h = (b.count / maxC) * chartH;
    const y = padT + chartH - h;
    return `<rect x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${(barW - 1).toFixed(1)}" height="${h.toFixed(1)}" fill="${COL_BAR}" fill-opacity="0.9"/>`;
  }).join("");
  const meanLine =
    `<line x1="${xFor(mn).toFixed(1)}" y1="${padT - 2}" x2="${xFor(mn).toFixed(1)}" y2="${padT + chartH}" stroke="${COL_MEAN}" stroke-width="2"/>` +
    `<text x="${xFor(mn).toFixed(1)}" y="${(padT - 6).toFixed(1)}" text-anchor="middle" font-size="10" fill="${COL_MEAN}">medie ${fmtNum(Math.round(mn * 10) / 10)}</text>`;
  const medianLine =
    `<line x1="${xFor(md).toFixed(1)}" y1="${padT - 2}" x2="${xFor(md).toFixed(1)}" y2="${padT + chartH}" stroke="${COL_MEDIAN}" stroke-width="2" stroke-dasharray="4 3"/>` +
    `<text x="${xFor(md).toFixed(1)}" y="${(padT + chartH + 16).toFixed(1)}" text-anchor="middle" font-size="10" fill="${COL_MEDIAN}">median ${fmtNum(Math.round(md * 10) / 10)}</text>`;

  return `<div class="triple__cell">` +
    `<div class="triple__title">${esc(title)}</div>` +
    `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto;display:block">` +
    bars + meanLine + medianLine +
    `</svg>` +
    `<div class="triple__meta">${values.length} valori</div>` +
    `</div>`;
}

async function renderTripleHistogram(container, block, stats) {
  const series = block.series || [];
  const grid = document.createElement("div");
  grid.className = "triple-histogram";
  grid.innerHTML = series.map((s) => {
    const values = Array.isArray(s.values) ? s.values : (s.path ? walkStatsPath(stats, s.path) : []) || [];
    return miniHistogramSVG(values, s.binWidth || 3, s.title || "");
  }).join("");
  container.appendChild(grid);
}

// ---- public entry --------------------------------------------------------
function renderScatter(container, block, stats) {
  const sm = stats?.sliceMetrics || {};
  const scatter = sm.scatterData || [];
  const trio = sm.trioMission || {};
  const corr = sm.correlations || {};
  if (!scatter.length) { container.textContent = "Fără date pentru scatter."; return; }

  let axisMode = "popularity"; // popularity | groups | reach2

  const wrap = document.createElement("div");
  wrap.className = "chart__wrap chart__wrap--scatter";
  container.appendChild(wrap);

  const controls = document.createElement("div");
  controls.className = "chart__controls";
  controls.innerHTML =
    `<div class="diff-row diff-buttons">` +
      `<button type="button" class="btn btn--primary" data-axis="popularity">Popularitate</button>` +
      `<button type="button" class="btn btn--ghost" data-axis="groups">Deschidere</button>` +
      `<button type="button" class="btn btn--ghost" data-axis="reach2">Rază la 2 pași</button>` +
    `</div>` +
    `<div class="chart__meta chart__meta--corr" data-role="corr"></div>`;
  wrap.appendChild(controls);

  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("class", "chart__svg chart__svg--scatter");
  svg.setAttribute("viewBox", "0 0 640 380");
  svg.setAttribute("preserveAspectRatio", "xMidYMid meet");
  wrap.appendChild(svg);

  const trioIds = new Set([trio.sandu?.id, trio.emil?.id, trio.doina?.id].filter(Boolean).map(Number));
  const trioLabel = new Map();
  if (trio.sandu) trioLabel.set(Number(trio.sandu.id), trio.sandu.name);
  if (trio.emil) trioLabel.set(Number(trio.emil.id), trio.emil.name);
  if (trio.doina) trioLabel.set(Number(trio.doina.id), trio.doina.name);

  function draw() {
    svg.innerHTML = "";
    const W = 640, H = 380;
    const M = { top: 20, right: 20, bottom: 50, left: 55 };
    const iw = W - M.left - M.right;
    const ih = H - M.top - M.bottom;

    const xField = axisMode;
    const xLabel =
      axisMode === "popularity" ? "Popularitate (contacte)" :
      axisMode === "groups"     ? "Deschidere (grupuri)" :
                                  "Rază la 2 pași";
    const yLabel = "Rază la 4 pași";
    const corrKey =
      axisMode === "popularity" ? "popularityReach" :
      axisMode === "groups"     ? "groupsReach" :
                                  "reach2Reach";
    const rVal = corr[corrKey];

    const corrEl = controls.querySelector('[data-role="corr"]');
    if (corrEl) corrEl.innerHTML = `Corelație cu raza: <strong>${(rVal ?? 0).toFixed(2)}</strong>`;

    const xMax = Math.max(...scatter.map((p) => p[xField]), 1);
    const yMax = Math.max(...scatter.map((p) => p.reach), 1);
    const xScale = (v) => M.left + (v / xMax) * iw;
    const yScale = (v) => M.top + ih - (v / yMax) * ih;

    // Axes
    const axG = document.createElementNS("http://www.w3.org/2000/svg", "g");
    axG.setAttribute("stroke", "#8a7a68"); axG.setAttribute("stroke-width", "1");
    const xAxis = document.createElementNS("http://www.w3.org/2000/svg", "line");
    xAxis.setAttribute("x1", M.left); xAxis.setAttribute("y1", M.top + ih);
    xAxis.setAttribute("x2", M.left + iw); xAxis.setAttribute("y2", M.top + ih);
    axG.appendChild(xAxis);
    const yAxis = document.createElementNS("http://www.w3.org/2000/svg", "line");
    yAxis.setAttribute("x1", M.left); yAxis.setAttribute("y1", M.top);
    yAxis.setAttribute("x2", M.left); yAxis.setAttribute("y2", M.top + ih);
    axG.appendChild(yAxis);
    svg.appendChild(axG);

    // Grid + ticks
    const gridG = document.createElementNS("http://www.w3.org/2000/svg", "g");
    for (let i = 0; i <= 5; i++) {
      const y = M.top + ih - (i / 5) * ih;
      const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
      line.setAttribute("x1", M.left); line.setAttribute("y1", y);
      line.setAttribute("x2", M.left + iw); line.setAttribute("y2", y);
      line.setAttribute("stroke", "#e5dccc"); line.setAttribute("stroke-width", "0.5");
      gridG.appendChild(line);
      const lbl = document.createElementNS("http://www.w3.org/2000/svg", "text");
      lbl.setAttribute("x", M.left - 8); lbl.setAttribute("y", y + 3);
      lbl.setAttribute("text-anchor", "end"); lbl.setAttribute("font-size", "10");
      lbl.setAttribute("fill", "#5a4a3a");
      lbl.textContent = String(Math.round((i / 5) * yMax));
      gridG.appendChild(lbl);
    }
    for (let i = 0; i <= 5; i++) {
      const x = M.left + (i / 5) * iw;
      const lbl = document.createElementNS("http://www.w3.org/2000/svg", "text");
      lbl.setAttribute("x", x); lbl.setAttribute("y", M.top + ih + 15);
      lbl.setAttribute("text-anchor", "middle"); lbl.setAttribute("font-size", "10");
      lbl.setAttribute("fill", "#5a4a3a");
      lbl.textContent = String(Math.round((i / 5) * xMax));
      gridG.appendChild(lbl);
    }
    svg.appendChild(gridG);

    // Axis labels
    const xTitle = document.createElementNS("http://www.w3.org/2000/svg", "text");
    xTitle.setAttribute("x", M.left + iw / 2); xTitle.setAttribute("y", M.top + ih + 38);
    xTitle.setAttribute("text-anchor", "middle"); xTitle.setAttribute("font-size", "11");
    xTitle.setAttribute("fill", "#2a1f16"); xTitle.textContent = xLabel;
    svg.appendChild(xTitle);
    const yTitle = document.createElementNS("http://www.w3.org/2000/svg", "text");
    yTitle.setAttribute("x", -M.top - ih / 2); yTitle.setAttribute("y", 15);
    yTitle.setAttribute("text-anchor", "middle"); yTitle.setAttribute("font-size", "11");
    yTitle.setAttribute("fill", "#2a1f16"); yTitle.setAttribute("transform", "rotate(-90)");
    yTitle.textContent = yLabel;
    svg.appendChild(yTitle);

    // Points
    const dotsG = document.createElementNS("http://www.w3.org/2000/svg", "g");
    for (const p of scatter) {
      if (trioIds.has(Number(p.id))) continue;
      const c = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      const jx = xScale(p[xField]) + (Math.random() - 0.5) * 6;
      c.setAttribute("cx", jx.toFixed(1));
      c.setAttribute("cy", yScale(p.reach).toFixed(1));
      c.setAttribute("r", "2.5");
      c.setAttribute("fill", "#8b4a1e");
      c.setAttribute("opacity", "0.42");
      dotsG.appendChild(c);
    }
    svg.appendChild(dotsG);

    // Trio markers on top
    const trioG = document.createElementNS("http://www.w3.org/2000/svg", "g");
    const trioColors = { "Sandu": "#2a1f16", "Emil": "#a3341f", "Doina": "#1e5a4a" };
    for (const p of scatter) {
      const id = Number(p.id);
      if (!trioIds.has(id)) continue;
      const label = trioLabel.get(id);
      const color = trioColors[label] || "#2a1f16";
      const c = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      const cx = xScale(p[xField]); const cy = yScale(p.reach);
      c.setAttribute("cx", cx); c.setAttribute("cy", cy);
      c.setAttribute("r", "6");
      c.setAttribute("fill", color); c.setAttribute("stroke", "#faf7f2");
      c.setAttribute("stroke-width", "2");
      trioG.appendChild(c);
      const t = document.createElementNS("http://www.w3.org/2000/svg", "text");
      t.setAttribute("x", cx + 9); t.setAttribute("y", cy + 4);
      t.setAttribute("font-size", "12"); t.setAttribute("font-weight", "600");
      t.setAttribute("fill", color); t.textContent = label;
      trioG.appendChild(t);
    }
    svg.appendChild(trioG);
  }

  controls.querySelectorAll("[data-axis]").forEach((btn) => {
    btn.addEventListener("click", () => {
      axisMode = btn.dataset.axis;
      controls.querySelectorAll("[data-axis]").forEach((b) => {
        if (b.dataset.axis === axisMode) { b.classList.add("btn--primary"); b.classList.remove("btn--ghost"); }
        else { b.classList.remove("btn--primary"); b.classList.add("btn--ghost"); }
      });
      draw();
    });
  });

  draw();
}

// Ego-net comparison. Each tab: one focus student. Small SVG shows focus at
// center, 1-hop contacts in one color, 2-hop friends-of-friends in another.
// Under each: "la 1 pas: X, la 2 pași: Y". Used by c-prietenii-prietenilor
// (3 tabs) and c14-yann-izolat (2 tabs).
async function renderFriendsTabs(container, block, stats) {
  const netPath = block.data || block.linkNetworkData || "data/highschool-network.json";
  let net;
  try { net = await loadJSON(netPath); } catch { container.textContent = "Nu am putut încărca rețeaua."; return; }
  const sm = stats?.sliceMetrics || {};
  const chars = sm.characters || {};
  const nameToNode = new Map();
  const idToNode = new Map();
  for (const n of net.nodes) {
    idToNode.set(String(n.id), n);
    if (n.name) nameToNode.set(n.name, n);
  }

  const adj = new Map();
  for (const n of net.nodes) adj.set(String(n.id), new Set());
  for (const e of net.edges) {
    adj.get(String(e.source))?.add(String(e.target));
    adj.get(String(e.target))?.add(String(e.source));
  }

  // Resolve focuses: list of {roleKey?, name?, id?, label?}
  const focuses = (block.focuses || []).map((f) => {
    let node = null;
    if (f.roleKey && chars[f.roleKey]) node = idToNode.get(String(chars[f.roleKey].id));
    else if (f.name) node = nameToNode.get(f.name);
    else if (f.id) node = idToNode.get(String(f.id));
    if (!node) return null;
    return {
      id: String(node.id),
      name: node.name || `Elev ${node.id}`,
      classFriendly: (stats?.classNames || {})[node.group] || node.group,
      label: f.label || node.name,
    };
  }).filter(Boolean);
  if (!focuses.length) { container.textContent = "Fișe indisponibile."; return; }

  const tabsWrap = document.createElement("div");
  tabsWrap.className = "friends-tabs__tabs";
  container.appendChild(tabsWrap);
  const stage = document.createElement("div");
  stage.className = "friends-tabs__stage";
  container.appendChild(stage);
  const stat = document.createElement("div");
  stat.className = "friends-tabs__stat";
  container.appendChild(stat);

  const S = 340;

  function drawFor(f) {
    const oneHop = adj.get(f.id) || new Set();
    const twoHop = new Set();
    for (const y of oneHop) for (const z of adj.get(y) || []) if (z !== f.id && !oneHop.has(z)) twoHop.add(z);

    // Positions: focus at center; 1-hop on a small ring; 2-hop grouped
    // around their 1-hop parent, on an outer ring.
    const pos = new Map();
    pos.set(f.id, { x: S / 2, y: S / 2 });
    const oneArr = [...oneHop];
    const R1 = S * 0.20;
    oneArr.forEach((id, i) => {
      const a = (i / Math.max(1, oneArr.length)) * 2 * Math.PI - Math.PI / 2;
      pos.set(id, { x: S / 2 + Math.cos(a) * R1, y: S / 2 + Math.sin(a) * R1 });
    });
    // For each 2-hop node, pick its "parent" (a 1-hop neighbor) and place near.
    const R2 = S * 0.42;
    const parentOf = new Map();
    for (const t of twoHop) {
      // pick any 1-hop neighbor of t
      let p = null;
      for (const y of adj.get(t) || []) if (oneHop.has(y)) { p = y; break; }
      parentOf.set(t, p);
    }
    // Group 2-hop by parent and lay them out around parent's angle.
    const byParent = new Map();
    for (const [t, p] of parentOf) {
      if (p == null) continue;
      if (!byParent.has(p)) byParent.set(p, []);
      byParent.get(p).push(t);
    }
    for (const [p, kids] of byParent) {
      const parentIdx = oneArr.indexOf(p);
      const parentAngle = (parentIdx / Math.max(1, oneArr.length)) * 2 * Math.PI - Math.PI / 2;
      kids.forEach((t, i) => {
        const spread = Math.min(1.2, 0.15 + kids.length * 0.05);
        const localA = parentAngle + (i - (kids.length - 1) / 2) * spread / Math.max(1, kids.length);
        pos.set(t, { x: S / 2 + Math.cos(localA) * R2, y: S / 2 + Math.sin(localA) * R2 });
      });
    }
    // 2-hop with no 1-hop parent (rare) go on the outer ring uniformly.
    const orphan = [...twoHop].filter((t) => !pos.has(t));
    orphan.forEach((t, i) => {
      const a = (i / Math.max(1, orphan.length)) * 2 * Math.PI;
      pos.set(t, { x: S / 2 + Math.cos(a) * R2, y: S / 2 + Math.sin(a) * R2 });
    });

    // Edges: focus-to-1hop, 1hop-to-2hop.
    const edges = [];
    for (const id of oneHop) {
      edges.push({ a: f.id, b: id });
      for (const t of adj.get(id) || []) {
        if (twoHop.has(t)) edges.push({ a: id, b: t });
      }
    }
    const edgesSvg = edges.map((e) => {
      const pa = pos.get(e.a), pb = pos.get(e.b);
      if (!pa || !pb) return "";
      return `<line x1="${pa.x.toFixed(1)}" y1="${pa.y.toFixed(1)}" x2="${pb.x.toFixed(1)}" y2="${pb.y.toFixed(1)}" stroke="#8a7154" stroke-width="0.8" opacity="0.4"/>`;
    }).join("");

    const twoDots = [...twoHop].map((id) => {
      const p = pos.get(id); if (!p) return "";
      return `<circle cx="${p.x.toFixed(1)}" cy="${p.y.toFixed(1)}" r="4" fill="#3d7a52" opacity="0.9"/>`;
    }).join("");
    const oneDots = [...oneHop].map((id) => {
      const p = pos.get(id); if (!p) return "";
      return `<circle cx="${p.x.toFixed(1)}" cy="${p.y.toFixed(1)}" r="5" fill="#8b4a1e"/>`;
    }).join("");
    const focusDot = `<circle cx="${(S/2).toFixed(1)}" cy="${(S/2).toFixed(1)}" r="8" fill="#2a1f16"/>`;

    stage.innerHTML =
      `<svg viewBox="0 0 ${S} ${S}" xmlns="http://www.w3.org/2000/svg" ` +
      `style="width:100%;height:auto;max-width:${S+20}px;display:block;margin:0 auto" ` +
      `role="img" aria-label="Ego-rețeaua lui ${esc(f.name)}">` +
      edgesSvg + twoDots + oneDots + focusDot +
      `</svg>` +
      `<div class="friends-tabs__legend">` +
        `<span><span class="friends-tabs__dot" style="background:#2a1f16"></span>${esc(f.name)}, ${esc(f.classFriendly)}</span>` +
        `<span><span class="friends-tabs__dot" style="background:#8b4a1e"></span>contactele lui (${oneHop.size})</span>` +
        `<span><span class="friends-tabs__dot" style="background:#3d7a52"></span>contactele contactelor (${twoHop.size})</span>` +
      `</div>`;
    stat.innerHTML = `La 1 pas: <strong>${oneHop.size}</strong>. La 2 pași: <strong>${twoHop.size}</strong>.`;
  }

  focuses.forEach((f, i) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "friends-tabs__tab" + (i === 0 ? " is-active" : "");
    btn.textContent = f.label;
    btn.addEventListener("click", () => {
      tabsWrap.querySelectorAll(".friends-tabs__tab").forEach((b) => b.classList.remove("is-active"));
      btn.classList.add("is-active");
      drawFor(f);
    });
    tabsWrap.appendChild(btn);
  });
  drawFor(focuses[0]);
}

// Three-in-one view: multiple isolated ego-nets in the same SVG so the visual
// makes the point that they are separate islands. Used for the "trei izolați"
// card in Ch3 (Yann + Iban + Cécile) — three degree-1 students the model
// never reaches, from three different classes.
async function renderUnreachedMulti(container, block, stats) {
  const netPath = block.data || "data/highschool-network.json";
  let net;
  try { net = await loadJSON(netPath); } catch { container.textContent = "Nu am putut încărca rețeaua."; return; }
  const nameToNode = new Map();
  const idToNode = new Map();
  for (const n of net.nodes) {
    idToNode.set(String(n.id), n);
    if (n.name) nameToNode.set(n.name, n);
  }
  const adj = new Map();
  for (const n of net.nodes) adj.set(String(n.id), new Set());
  for (const e of net.edges) {
    adj.get(String(e.source))?.add(String(e.target));
    adj.get(String(e.target))?.add(String(e.source));
  }
  const classNames = stats?.classNames || {};

  const focuses = (block.focuses || []).map((f) => {
    let node = null;
    if (f.name) node = nameToNode.get(f.name);
    else if (f.id) node = idToNode.get(String(f.id));
    if (!node) return null;
    return {
      id: String(node.id),
      name: node.name,
      classFriendly: classNames[node.group] || node.group,
    };
  }).filter(Boolean);
  if (!focuses.length) { container.textContent = "Nu am găsit elevii ceruți."; return; }

  const W = 640, H = 360;
  const cluster = focuses.map((f, i) => {
    const angle = (i / focuses.length) * 2 * Math.PI - Math.PI / 2;
    return {
      focus: f,
      cx: W / 2 + Math.cos(angle) * W * 0.28,
      cy: H / 2 + Math.sin(angle) * H * 0.28,
    };
  });

  const parts = [];
  for (const c of cluster) {
    const f = c.focus;
    const oneHop = [...(adj.get(f.id) || [])];
    const twoHop = new Set();
    for (const y of oneHop) for (const z of adj.get(y) || []) if (z !== f.id && !oneHop.includes(z)) twoHop.add(z);

    const R1 = 32;
    const R2 = 62;

    const pos = new Map();
    pos.set(f.id, { x: c.cx, y: c.cy });
    oneHop.forEach((id, i) => {
      const a = (i / Math.max(1, oneHop.length)) * 2 * Math.PI - Math.PI / 2;
      pos.set(id, { x: c.cx + Math.cos(a) * R1, y: c.cy + Math.sin(a) * R1 });
    });
    const twoArr = [...twoHop];
    const parentOf = new Map();
    for (const t of twoArr) {
      let p = null;
      for (const y of adj.get(t) || []) if (oneHop.includes(y)) { p = y; break; }
      parentOf.set(t, p);
    }
    const byParent = new Map();
    for (const [t, p] of parentOf) {
      if (p == null) continue;
      if (!byParent.has(p)) byParent.set(p, []);
      byParent.get(p).push(t);
    }
    for (const [p, kids] of byParent) {
      const parentIdx = oneHop.indexOf(p);
      const parentAngle = (parentIdx / Math.max(1, oneHop.length)) * 2 * Math.PI - Math.PI / 2;
      kids.forEach((t, i) => {
        const spread = Math.min(1.0, 0.2 + kids.length * 0.06);
        const localA = parentAngle + (i - (kids.length - 1) / 2) * spread / Math.max(1, kids.length);
        pos.set(t, { x: c.cx + Math.cos(localA) * R2, y: c.cy + Math.sin(localA) * R2 });
      });
    }
    const orphans = twoArr.filter((t) => !pos.has(t));
    orphans.forEach((t, i) => {
      const a = (i / Math.max(1, orphans.length)) * 2 * Math.PI;
      pos.set(t, { x: c.cx + Math.cos(a) * R2, y: c.cy + Math.sin(a) * R2 });
    });

    // Edges within this cluster
    for (const id of oneHop) {
      const pa = pos.get(f.id), pb = pos.get(id);
      if (pa && pb) parts.push(`<line x1="${pa.x.toFixed(1)}" y1="${pa.y.toFixed(1)}" x2="${pb.x.toFixed(1)}" y2="${pb.y.toFixed(1)}" stroke="#8a7154" stroke-width="0.8" opacity="0.45"/>`);
      for (const t of adj.get(id) || []) {
        if (twoHop.has(t)) {
          const pc = pos.get(t);
          if (pb && pc) parts.push(`<line x1="${pb.x.toFixed(1)}" y1="${pb.y.toFixed(1)}" x2="${pc.x.toFixed(1)}" y2="${pc.y.toFixed(1)}" stroke="#8a7154" stroke-width="0.8" opacity="0.45"/>`);
        }
      }
    }
    // 2-hop dots
    for (const t of twoArr) {
      const p = pos.get(t); if (!p) continue;
      parts.push(`<circle cx="${p.x.toFixed(1)}" cy="${p.y.toFixed(1)}" r="3.5" fill="#3d7a52" opacity="0.85"/>`);
    }
    // 1-hop dots
    for (const id of oneHop) {
      const p = pos.get(id); if (!p) continue;
      parts.push(`<circle cx="${p.x.toFixed(1)}" cy="${p.y.toFixed(1)}" r="4.5" fill="#8b4a1e"/>`);
    }
    // Focus dot + label
    parts.push(`<circle cx="${c.cx.toFixed(1)}" cy="${c.cy.toFixed(1)}" r="8" fill="#2a1f16"/>`);
    const labelY = c.cy + R2 + 18;
    parts.push(`<text x="${c.cx.toFixed(1)}" y="${labelY.toFixed(1)}" text-anchor="middle" font-family="Georgia, serif" font-size="14" fill="#2a1f16"><tspan font-weight="500">${esc(f.name)}</tspan>, ${esc(f.classFriendly)}</text>`);
  }

  const svg = document.createElement("div");
  svg.className = "chart__svg-wrap";
  svg.innerHTML =
    `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" ` +
    `style="width:100%;height:auto;max-width:700px;display:block;margin:0 auto" ` +
    `role="img" aria-label="Trei elevi izolați cu vecinătatea lor la doi pași">` +
    parts.join("") + `</svg>`;
  container.appendChild(svg);

  const legend = document.createElement("div");
  legend.className = "friends-tabs__legend";
  legend.innerHTML =
    `<span><span class="friends-tabs__dot" style="background:#2a1f16"></span>elev neatins</span>` +
    `<span><span class="friends-tabs__dot" style="background:#8b4a1e"></span>singurul lui contact</span>` +
    `<span><span class="friends-tabs__dot" style="background:#3d7a52"></span>contactele acelui contact</span>`;
  container.appendChild(legend);
}

// Measure card with two tabs: Clasament (horizontal bars, primii 8) + Pe
// hartă (network view highlighting the measure's champion in a way specific
// to that measure). Used by c-gradul, c-deschiderea, c-intermedierea.
// Data comes from build precomputes: coverageMaps._positions (shared radial
// layout by class) and coverageMaps._measureMaps.{degree|openness|betweenness}.
async function renderMeasureTabs(container, block, stats) {
  const measure = block.measure || "degree";  // "degree" | "openness" | "betweenness"
  const cm = stats?.sliceMetrics?.mission?.coverageMaps || {};
  // Per-card layout: "liber" runs cose live (same as the school-map "Liber"
  // mode); "class" uses the precomputed class-clustered ring positions.
  // Defaults: grad + intermediere on liber, deschidere on class (the point
  // of deschidere is exactly to see contacts jump between class clumps).
  const defaultLayout = measure === "openness" ? "class" : "liber";
  const layoutMode = block.layoutMode || defaultLayout;

  let positions;
  if (layoutMode === "liber") {
    const netPath = block.data || "data/highschool-network.json";
    const cose = await computeCosePositions(netPath);
    const meta = cm._positions || {};
    positions = {};
    for (const [nid, p] of Object.entries(cose)) {
      const m = meta[nid] || {};
      positions[nid] = { x: p.x, y: p.y, class: m.class, classFriendly: m.classFriendly };
    }
  } else {
    positions = cm._positions || {};
  }
  const mm = cm._measureMaps || {};
  const forMeasure = mm[measure] || null;
  const positionsList = Object.entries(positions);
  const total = mm.total || stats?.total || 299;

  const tabsWrap = document.createElement("div");
  tabsWrap.className = "measure-tabs__tabs";
  container.appendChild(tabsWrap);

  const barsPane = document.createElement("div");
  barsPane.className = "measure-tabs__pane";
  const mapPane = document.createElement("div");
  mapPane.className = "measure-tabs__pane";
  mapPane.hidden = true;
  container.appendChild(barsPane);
  container.appendChild(mapPane);

  // -- Clasament (uses existing hbarsSVG with the block's bars)
  const barsHost = document.createElement("div");
  barsHost.className = "chart__svg-wrap chart__svg-wrap--hbars";
  barsHost.innerHTML = hbarsSVG(block);
  barsPane.appendChild(barsHost);
  const legendClasses = Array.from(new Set((block.bars || []).map((b) => b.class).filter(Boolean)));
  if (legendClasses.length) {
    const legend = document.createElement("div");
    legend.className = "chart__legend";
    legend.innerHTML = legendClasses.map((cls) =>
      `<span class="chart__legend-chip"><span class="chart__legend-dot" style="background:${colorForClass(cls)}"></span>${esc(cls)}</span>`
    ).join("");
    barsPane.appendChild(legend);
  }

  // -- Pe hartă: measure-specific visualization
  // Keep the map roughly the same footprint as the Clasament bars so switching
  // tabs does not send the card jumping in height (users perceived this as
  // "atlas mode" — a jarring layout shift).
  const S = 380;
  function projX(px) { return ((px + 1) / 2) * (S - 40) + 20; }
  function projY(py) { return ((py + 1) / 2) * (S - 40) + 20; }
  function posOf(id) {
    const p = positions[String(id)];
    if (!p) return null;
    return { x: projX(p.x), y: projY(p.y), classFriendly: p.classFriendly };
  }

  function baseDotsSvg(highlightSet) {
    // On the free (cose) layout the pale backdrop of 280 non-highlighted dots
    // reads as noise around the champion's small ego-network. Suppress it and
    // leave the map with just the champion + his contacts + edges.
    if (layoutMode === "liber") return "";
    return positionsList.map(([nid, p]) => {
      const x = projX(p.x), y = projY(p.y);
      const on = highlightSet && highlightSet.has(String(nid));
      if (on) return "";
      return `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="2.2" fill="#c9beac"/>`;
    }).join("");
  }

  // Small class-label overlay so students can name each clump. Draws one
  // label per class at the mean position of its members, then clamped to
  // the SVG margins so nothing crops.
  function classLabelsSvg() {
    const byClass = new Map();
    for (const [nid, p] of Object.entries(positions)) {
      if (!p.classFriendly) continue;
      if (!byClass.has(p.classFriendly)) byClass.set(p.classFriendly, []);
      byClass.get(p.classFriendly).push(p);
    }
    const parts = [];
    const margin = 14;
    for (const [cls, arr] of byClass) {
      const cx = arr.reduce((s, q) => s + q.x, 0) / arr.length;
      const cy = arr.reduce((s, q) => s + q.y, 0) / arr.length;
      const px = projX(cx), py = projY(cy);
      const cx2c = (S / 2) - px;
      const cy2c = (S / 2) - py;
      const mag = Math.sqrt(cx2c * cx2c + cy2c * cy2c) || 1;
      const off = 14;  // smaller push so the label stays close to its clump
      let lx = px - (cx2c / mag) * off;
      let ly = py - (cy2c / mag) * off;
      lx = Math.max(margin, Math.min(S - margin, lx));
      ly = Math.max(margin, Math.min(S - margin, ly));
      parts.push(`<text x="${lx.toFixed(1)}" y="${ly.toFixed(1)}" text-anchor="middle" font-family="Georgia, serif" font-size="10" fill="#5c5346">${esc(cls)}</text>`);
    }
    return parts.join("");
  }

  function baseEdgesSvg() { return ""; /* class-cluster layout: no backdrop */ }

  const mapControls = document.createElement("div");
  mapControls.className = "measure-tabs__map-controls";
  const mapHost = document.createElement("div");
  mapHost.className = "chart__svg-wrap";
  const mapCaption = document.createElement("div");
  mapCaption.className = "measure-tabs__map-caption";
  mapPane.appendChild(mapControls);
  mapPane.appendChild(mapHost);
  mapPane.appendChild(mapCaption);

  let mapBuilt = false;
  function buildMap() {
    if (mapBuilt) return;
    mapBuilt = true;
    if (measure === "degree") buildDegreeMap();
    else if (measure === "openness") buildOpennessMap();
    else if (measure === "betweenness") buildBetweennessMap();
    else { mapHost.textContent = "Măsură necunoscută."; }
  }

  function drawChampionMap(champ, opts) {
    // champ: {id, name, classFriendly, contactIds, classDistribution}
    // opts: {edgeColor, contactFillFn(nid)->color, showLegend: bool, subtitle: string}
    const champPos = posOf(champ.id);
    if (!champPos) { mapHost.textContent = "Nu am poziția campionului."; return; }
    const contactSet = new Set(champ.contactIds.map(String));
    const hi = new Set([String(champ.id), ...contactSet]);

    const edges = champ.contactIds.map((cid) => {
      const p = posOf(cid); if (!p) return "";
      return `<line x1="${champPos.x.toFixed(1)}" y1="${champPos.y.toFixed(1)}" x2="${p.x.toFixed(1)}" y2="${p.y.toFixed(1)}" stroke="${opts.edgeColor}" stroke-width="1.4" opacity="0.7"/>`;
    }).join("");
    const contactDots = champ.contactIds.map((cid) => {
      const p = posOf(cid); if (!p) return "";
      const fill = opts.contactFillFn ? opts.contactFillFn(cid) : "#8b4a1e";
      return `<circle cx="${p.x.toFixed(1)}" cy="${p.y.toFixed(1)}" r="5" fill="${fill}" stroke="#3a2a1a" stroke-width="0.6"/>`;
    }).join("");
    const champDot = `<circle cx="${champPos.x.toFixed(1)}" cy="${champPos.y.toFixed(1)}" r="10" fill="#2a1f16" stroke="#000" stroke-width="1"/>`;
    const label = `<text x="${champPos.x.toFixed(1)}" y="${(champPos.y + 22).toFixed(1)}" text-anchor="middle" font-family="Georgia, serif" font-size="13" fill="#2a1f16"><tspan font-weight="500">${esc(champ.name)}</tspan>, ${esc(champ.classFriendly)}</text>`;

    mapHost.innerHTML =
      `<svg viewBox="0 0 ${S} ${S}" xmlns="http://www.w3.org/2000/svg" ` +
      `style="width:100%;height:auto;max-width:420px;display:block;margin:0 auto" ` +
      `role="img" aria-label="Harta măsurii pentru ${esc(champ.name)}">` +
      baseDotsSvg(hi) + (layoutMode === "class" ? classLabelsSvg() : "") + edges + contactDots + champDot + label +
      `</svg>`;
    mapCaption.innerHTML = opts.subtitle || "";
  }

  function buildDegreeMap() {
    const champ = forMeasure?.champion;
    if (!champ) { mapHost.textContent = "Fără date pentru harta gradului."; return; }
    drawChampionMap(champ, {
      edgeColor: "#8b4a1e",
      contactFillFn: () => "#8b4a1e",
      subtitle: `<strong>${champ.degree}</strong> muchii pleacă din el. Atât înseamnă gradul.`,
    });
  }

  function buildOpennessMap() {
    const champ = forMeasure?.champion;
    const contrast = forMeasure?.contrast;
    if (!champ) { mapHost.textContent = "Fără date."; return; }

    function drawOne(who) {
      const contactFillFn = (cid) => {
        const p = positions[String(cid)];
        if (!p) return "#8b4a1e";
        return colorForClass(p.classFriendly);
      };
      let subtitle;
      if (who.id === champ.id) {
        subtitle = `La <strong>${who.name}</strong>, contactele vin din <strong>${who.classDistribution.length}</strong> clase diferite. Culorile arată din care.`;
      } else {
        subtitle = `La <strong>${who.name}</strong>, contactele au aproape toate aceeași culoare: sunt din <strong>${who.classDistribution[0].classFriendly}</strong>, clasa lui.`;
      }
      drawChampionMap(who, { edgeColor: "#8a7154", contactFillFn, subtitle });
    }
    drawOne(champ);

    mapControls.innerHTML =
      `<button type="button" class="btn btn--primary" data-who="champion">${champ.name} (${champ.classFriendly})</button>` +
      (contrast ? `<button type="button" class="btn btn--ghost" data-who="contrast">${contrast.name} (${contrast.classFriendly})</button>` : "");
    mapControls.querySelectorAll("[data-who]").forEach((btn) => {
      btn.addEventListener("click", () => {
        mapControls.querySelectorAll("[data-who]").forEach((b) => { b.classList.remove("btn--primary"); b.classList.add("btn--ghost"); });
        btn.classList.remove("btn--ghost"); btn.classList.add("btn--primary");
        drawOne(btn.dataset.who === "contrast" ? contrast : champ);
      });
    });
  }

  function buildBetweennessMap() {
    const champ = forMeasure?.champion;
    const paths = forMeasure?.paths || [];
    if (!champ || !paths.length) { mapHost.textContent = "Fără date."; return; }
    const champPos = posOf(champ.id);
    if (!champPos) { mapHost.textContent = "Nu am poziția campionului."; return; }

    let shown = 0;
    const PALETTE = ["#a3341f", "#3d7a52", "#2f6fa8", "#7a5b8c", "#b57140"];

    function draw() {
      const activePaths = paths.slice(0, shown);
      const highlightIds = new Set([String(champ.id)]);
      activePaths.forEach((pth) => pth.pathIds.forEach((x) => highlightIds.add(String(x))));

      // Draw paths as colored polylines.
      const pathSvgs = activePaths.map((pth, i) => {
        const pts = pth.pathIds.map((id) => posOf(id)).filter(Boolean);
        const poly = pts.map((p) => `${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(" ");
        const color = PALETTE[i % PALETTE.length];
        return `<polyline points="${poly}" fill="none" stroke="${color}" stroke-width="2.2" opacity="0.85"/>`;
      }).join("");

      // Endpoint dots for each shown path (colored by path color).
      const endDots = activePaths.flatMap((pth, i) => {
        const s = posOf(pth.sourceId), t = posOf(pth.targetId);
        const color = PALETTE[i % PALETTE.length];
        const svg = [];
        if (s) svg.push(`<circle cx="${s.x.toFixed(1)}" cy="${s.y.toFixed(1)}" r="4.5" fill="${color}" stroke="#3a2a1a" stroke-width="0.7"/>`);
        if (t) svg.push(`<circle cx="${t.x.toFixed(1)}" cy="${t.y.toFixed(1)}" r="4.5" fill="${color}" stroke="#3a2a1a" stroke-width="0.7"/>`);
        return svg;
      }).join("");

      const champDot = `<circle cx="${champPos.x.toFixed(1)}" cy="${champPos.y.toFixed(1)}" r="11" fill="#2a1f16" stroke="#000" stroke-width="1.2"/>`;
      const champLabel = `<text x="${champPos.x.toFixed(1)}" y="${(champPos.y + 24).toFixed(1)}" text-anchor="middle" font-family="Georgia, serif" font-size="13" fill="#2a1f16"><tspan font-weight="500">${esc(champ.name)}</tspan>, ${esc(champ.classFriendly)}</text>`;

      mapHost.innerHTML =
        `<svg viewBox="0 0 ${S} ${S}" xmlns="http://www.w3.org/2000/svg" ` +
        `style="width:100%;height:auto;max-width:420px;display:block;margin:0 auto" ` +
        `role="img" aria-label="Drumuri prin ${esc(champ.name)}">` +
        baseDotsSvg(highlightIds) + (layoutMode === "class" ? classLabelsSvg() : "") + pathSvgs + endDots + champDot + champLabel +
        `</svg>`;

      if (shown === 0) {
        mapCaption.textContent = "Apasă butonul ca să vezi un drum care trece prin ea.";
      } else {
        mapCaption.innerHTML =
          `<strong>${shown}</strong> ${shown === 1 ? "drum arătat" : "drumuri arătate"}. Toate trec prin <strong>${champ.name}</strong>.<br>` +
          `<span class="measure-tabs__paths-list">` +
          activePaths.map((pth, i) => `<span style="color:${PALETTE[i % PALETTE.length]}">${esc(pth.sourceName)} (${esc(pth.sourceClass)}) → ${esc(pth.targetName)} (${esc(pth.targetClass)})</span>`).join(" · ") +
          `</span>`;
      }
      addBtn.disabled = shown >= paths.length;
    }

    const addBtn = document.createElement("button");
    addBtn.type = "button";
    addBtn.className = "btn btn--primary";
    addBtn.textContent = "Arată încă un drum";
    const resetBtn = document.createElement("button");
    resetBtn.type = "button";
    resetBtn.className = "btn btn--ghost";
    resetBtn.textContent = "Începe de la zero";
    mapControls.appendChild(addBtn);
    mapControls.appendChild(resetBtn);

    addBtn.addEventListener("click", () => { if (shown < paths.length) { shown++; draw(); } });
    resetBtn.addEventListener("click", () => { shown = 0; draw(); });
    draw();
  }

  // -- Wire tabs
  const btnBars = document.createElement("button");
  btnBars.type = "button";
  btnBars.className = "measure-tabs__tab is-active";
  btnBars.textContent = "Clasament";
  const btnMap = document.createElement("button");
  btnMap.type = "button";
  btnMap.className = "measure-tabs__tab";
  btnMap.textContent = "Pe hartă";
  tabsWrap.appendChild(btnBars);
  tabsWrap.appendChild(btnMap);
  btnBars.addEventListener("click", () => {
    btnBars.classList.add("is-active"); btnMap.classList.remove("is-active");
    barsPane.hidden = false; mapPane.hidden = true;
  });
  btnMap.addEventListener("click", () => {
    btnMap.classList.add("is-active"); btnBars.classList.remove("is-active");
    barsPane.hidden = true; mapPane.hidden = false;
    buildMap();
  });
}

// Two-curve robustness chart: X = number removed, Y = size of largest remaining
// component. Random curve (averaged over trials) sits above; targeted curve
// (highest-degree first) plunges. Reads sliceMetrics.mission.coverageMaps._robustness
// which the build precomputes. Below the curves, buttons for the specific
// scenarios (Antoine, top 5, all cut vertices) place a marker at the correct
// x-value on both curves and show the observed component sizes for that case.
function renderRobustness(container, block, stats) {
  const cm = stats?.sliceMetrics?.mission?.coverageMaps || {};
  const rob = cm._robustness || null;
  if (!rob) { container.textContent = "Fără date pentru robustețe."; return; }
  const rand = rob.randomCurve || [];
  const targ = rob.targetedCurve || [];
  const total = rob.total || stats?.total || Math.max(...rand, ...targ);
  const maxRemoved = rob.maxRemoved || (rand.length - 1);

  const W = 620, H = 320;
  const M = { top: 24, right: 24, bottom: 42, left: 46 };
  const iw = W - M.left - M.right;
  const ih = H - M.top - M.bottom;

  const xScale = (k) => M.left + (k / maxRemoved) * iw;
  const yScale = (v) => M.top + (1 - v / total) * ih;

  function polyPoints(curve) {
    return curve.map((v, i) => `${xScale(i).toFixed(1)},${yScale(v).toFixed(1)}`).join(" ");
  }

  const xTicks = [0, 25, 50, 75, 100];
  const yTicks = [0, 75, 150, 225, 299];
  const grid = [];
  yTicks.forEach((v) => {
    const y = yScale(v).toFixed(1);
    grid.push(`<line x1="${M.left}" y1="${y}" x2="${W - M.right}" y2="${y}" stroke="${COL_LINE}" stroke-width="0.6"/>`);
    grid.push(`<text x="${M.left - 6}" y="${(parseFloat(y) + 4).toFixed(1)}" text-anchor="end" font-size="11" fill="${COL_MUTED}">${v}</text>`);
  });
  xTicks.forEach((k) => {
    const x = xScale(k).toFixed(1);
    grid.push(`<line x1="${x}" y1="${M.top}" x2="${x}" y2="${H - M.bottom}" stroke="${COL_LINE}" stroke-width="0.4" opacity="0.6"/>`);
    grid.push(`<text x="${x}" y="${(H - M.bottom + 16).toFixed(1)}" text-anchor="middle" font-size="11" fill="${COL_MUTED}">${k}</text>`);
  });

  const wrap = document.createElement("div");
  wrap.className = "chart__svg-wrap";
  container.appendChild(wrap);

  const legend = document.createElement("div");
  legend.className = "chart__legend";
  legend.innerHTML =
    `<span class="chart__legend-chip"><span class="chart__legend-dot" style="background:#3d7a52"></span>la întâmplare (medie peste ${rob.trials || 30} rulări)</span>` +
    `<span class="chart__legend-chip"><span class="chart__legend-dot" style="background:#a3341f"></span>țintit (cel mai popular rămas)</span>`;
  container.appendChild(legend);

  // Scenario buttons below: use the precomputed tryBreak scenarios so a click
  // places a marker at exactly the k that scenario removes.
  const scenarios = (stats?.sliceMetrics?.tryBreak?.scenarios || []).map((s) => {
    const k = (s.removedIds || []).length;
    return {
      key: s.key,
      k,
      label: s.label,
      biggestExact: s.biggestSize,
    };
  }).filter((s) => s.k > 0 && s.k <= maxRemoved);

  let markerK = null;
  let markerBiggest = null;

  function markerSvg() {
    if (markerK === null) return "";
    const x = xScale(markerK);
    const parts = [];
    // Vertical guide
    parts.push(`<line x1="${x.toFixed(1)}" y1="${M.top}" x2="${x.toFixed(1)}" y2="${H - M.bottom}" stroke="#2a1f16" stroke-width="1" stroke-dasharray="4 3"/>`);
    // Point on random curve
    if (rand[markerK] !== undefined) {
      const yr = yScale(rand[markerK]);
      parts.push(`<circle cx="${x.toFixed(1)}" cy="${yr.toFixed(1)}" r="5" fill="#3d7a52" stroke="#2a1f16" stroke-width="1"/>`);
    }
    // Point on targeted curve
    if (targ[markerK] !== undefined) {
      const yt = yScale(targ[markerK]);
      parts.push(`<circle cx="${x.toFixed(1)}" cy="${yt.toFixed(1)}" r="5" fill="#a3341f" stroke="#2a1f16" stroke-width="1"/>`);
    }
    // Point at scenario exact (if provided, differs from targeted curve when
    // the removed set is NOT the top-k-degree set)
    if (markerBiggest !== null) {
      const yb = yScale(markerBiggest);
      parts.push(`<circle cx="${x.toFixed(1)}" cy="${yb.toFixed(1)}" r="6" fill="none" stroke="#2a1f16" stroke-width="2"/>`);
    }
    return parts.join("");
  }

  function drawChart() {
    wrap.innerHTML =
      `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" ` +
      `style="width:100%;height:auto;max-width:680px;display:block;margin:0 auto" ` +
      `role="img" aria-label="Curbe de robustețe">` +
      grid.join("") +
      `<polyline points="${polyPoints(rand)}" fill="none" stroke="#3d7a52" stroke-width="2.5"/>` +
      `<polyline points="${polyPoints(targ)}" fill="none" stroke="#a3341f" stroke-width="2.5"/>` +
      markerSvg() +
      `<text x="${(M.left + iw / 2).toFixed(1)}" y="${(H - 6).toFixed(1)}" text-anchor="middle" font-size="12" fill="${COL_INK_S}">elevi scoși</text>` +
      `<text x="${(M.left - 34).toFixed(1)}" y="${(M.top + ih / 2).toFixed(1)}" text-anchor="middle" font-size="12" fill="${COL_INK_S}" transform="rotate(-90 ${(M.left - 34).toFixed(1)} ${(M.top + ih / 2).toFixed(1)})">cea mai mare bucată rămasă</text>` +
      `</svg>`;
  }

  const scenarioBar = document.createElement("div");
  scenarioBar.className = "measure-tabs__map-controls";
  scenarioBar.innerHTML = scenarios.map((s) =>
    `<button type="button" class="btn btn--ghost" data-scen-k="${s.k}" data-scen-b="${s.biggestExact}" data-scen-key="${s.key}">${esc(s.label)}</button>`
  ).join("") + (scenarios.length ? `<button type="button" class="btn btn--ghost" data-scen-k="clear">Curăță</button>` : "");
  container.appendChild(scenarioBar);

  const scenarioNote = document.createElement("div");
  scenarioNote.className = "measure-tabs__map-caption";
  container.appendChild(scenarioNote);

  scenarioBar.querySelectorAll("[data-scen-k]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const raw = btn.dataset.scenK;
      if (raw === "clear") { markerK = null; markerBiggest = null; drawChart(); scenarioNote.innerHTML = ""; return; }
      const k = parseInt(raw, 10);
      markerK = k;
      markerBiggest = parseInt(btn.dataset.scenB, 10);
      drawChart();
      scenarioNote.innerHTML =
        `Cu <strong>${k}</strong> ${k === 1 ? "elev scos" : "elevi scoși"} așa cum arată butonul, ` +
        `cea mai mare bucată rămâne cu <strong>${markerBiggest}</strong> elevi. ` +
        `Pe curba țintită la același k: <strong>${targ[k] ?? "?"}</strong>. ` +
        `Pe curba la întâmplare la același k: <strong>${rand[k] ?? "?"}</strong>.`;
    });
  });

  drawChart();
}

// Two-panel strategy duel: two maps side by side so comparison is visual, not
// memorized. Each class is a COMPACT clump of dots (not a ring), so the
// covered-vs-not proportion reads at a glance. Below each map, per-side buttons
// to swap which strategy is shown. Under the two, a highlight of which classes
// differ most between the two picks.
const CLASS_ORDER_LAYOUT = ["Bio A","Bio B","Bio C","Mate A","Mate B","Mate C","Chimie A","Chimie B","Inginerie"];
function renderStrategyDuel(container, block, stats) {
  const cm = stats?.sliceMetrics?.mission?.coverageMaps || {};
  const total = cm._total || stats?.total || 299;
  const classNames = stats?.classNames || {};
  // We do not use _positions (rings) any more — build compact clumps per class.
  const strategyList = block.strategies || ["greedy", "top3reach", "top3pop", "knownTeam", "top3betw"];
  const labels = {
    knownTeam: "Cei trei pe care îi știi",
    top3pop:   "Cei mai populari trei",
    top3open:  "Cei mai deschiși trei",
    top3reach: "Cei mai buni răspânditori",
    top3betw:  "Cei mai centrali trei",
    greedy:    "Alegerea lacomă",
  };

  // Bucket every node by its class.
  const byClass = new Map();
  for (const cls of CLASS_ORDER_LAYOUT) byClass.set(cls, []);
  const strategyById = {};  // node id -> class
  const anyStrat = strategyList.find((k) => cm[k]);
  if (!anyStrat) { container.textContent = "Fără date."; return; }
  // Pull the class of every node from _positions (which has classFriendly).
  const positions = cm._positions || {};
  for (const [nid, p] of Object.entries(positions)) {
    const cls = p.classFriendly;
    if (!byClass.has(cls)) byClass.set(cls, []);
    byClass.get(cls).push(String(nid));
    strategyById[String(nid)] = cls;
  }

  const wrap = document.createElement("div");
  wrap.className = "strategy-duel";
  container.appendChild(wrap);

  const compareLine = document.createElement("div");
  compareLine.className = "strategy-duel__compare";
  container.appendChild(compareLine);

  const sides = [
    { key: "left",  initial: strategyList[0] || "greedy" },
    { key: "right", initial: strategyList[1] || "top3reach" },
  ];
  const sideState = {};

  function renderSide(sideKey) {
    const state = sideState[sideKey];
    const data = cm[state.strategy];
    if (!data) { state.mapHost.textContent = "Fără date."; return; }
    const covered = new Set((data.coveredIds || []).map(String));
    const seeds = new Set((data.seedIds || []).map(String));

    // Layout: 9 classes in a 3x3 grid. Each cell has a compact clump of dots
    // arranged in a rough disk via a spiral packing — small deterministic.
    const CELL = 96;         // per-class cell size (px)
    const COLS = 3;
    const ROWS = 3;
    const S_W = COLS * CELL;
    const S_H = ROWS * CELL + 28;  // room for class labels
    const CLUMP_R = 32;      // disk radius inside each cell
    const NODE_R = 5;

    // Deterministic disk-packing: use golden-angle spiral for tight fill.
    function clumpPositions(n) {
      const gold = Math.PI * (3 - Math.sqrt(5));
      const pts = [];
      for (let i = 0; i < n; i++) {
        // sunflower / Vogel spiral for tight disk packing
        const r = CLUMP_R * Math.sqrt((i + 0.5) / n);
        const a = i * gold;
        pts.push({ x: Math.cos(a) * r, y: Math.sin(a) * r });
      }
      return pts;
    }

    const parts = [];
    CLASS_ORDER_LAYOUT.forEach((cls, idx) => {
      const col = idx % COLS;
      const row = Math.floor(idx / COLS);
      const cx = col * CELL + CELL / 2;
      const cy = row * CELL + CELL / 2 - 6;
      const members = byClass.get(cls) || [];
      const nCov = members.filter((m) => covered.has(m)).length;
      const nTot = members.length;
      const pcts = clumpPositions(nTot);
      const memPos = members.map((_, i) => ({ x: cx + pcts[i].x, y: cy + pcts[i].y, id: members[i] }));
      // Order: uncovered first (so covered draw on top), then covered, then seeds
      const drawOrder = [];
      memPos.forEach((p) => {
        if (seeds.has(p.id)) drawOrder.push({ ...p, kind: "seed" });
        else if (covered.has(p.id)) drawOrder.push({ ...p, kind: "cov" });
        else drawOrder.push({ ...p, kind: "miss" });
      });
      drawOrder.sort((a, b) => {
        // draw missed first, then covered, then seeds
        const order = { miss: 0, cov: 1, seed: 2 };
        return order[a.kind] - order[b.kind];
      });
      for (const p of drawOrder) {
        if (p.kind === "seed") parts.push(`<circle cx="${p.x.toFixed(1)}" cy="${p.y.toFixed(1)}" r="${NODE_R + 2}" fill="#2a1f16" stroke="#000" stroke-width="0.8"/>`);
        else if (p.kind === "cov") parts.push(`<circle cx="${p.x.toFixed(1)}" cy="${p.y.toFixed(1)}" r="${NODE_R}" fill="#8b4a1e"/>`);
        else parts.push(`<circle cx="${p.x.toFixed(1)}" cy="${p.y.toFixed(1)}" r="${NODE_R - 1.5}" fill="#e5dccb"/>`);
      }
      // Class label below the clump
      parts.push(`<text x="${cx.toFixed(1)}" y="${(cy + CLUMP_R + 12).toFixed(1)}" text-anchor="middle" font-family="Georgia, serif" font-size="10" fill="#5c5346"><tspan font-weight="500">${esc(cls)}</tspan>, ${nCov} din ${nTot}</text>`);
    });

    state.mapHost.innerHTML =
      `<svg viewBox="0 0 ${S_W} ${S_H}" xmlns="http://www.w3.org/2000/svg" ` +
      `style="width:100%;height:auto;max-width:340px;display:block;margin:0 auto" ` +
      `role="img" aria-label="Harta pentru ${esc(labels[state.strategy] || state.strategy)}">` +
      parts.join("") +
      `</svg>`;
    state.captionEl.innerHTML =
      `<strong>${esc(labels[state.strategy] || state.strategy)}</strong><br>` +
      `${esc((data.seedNames || []).join(", "))} — <strong>${covered.size}</strong> din ${total}`;
    state.buttonBar.querySelectorAll("[data-strat]").forEach((b) => {
      const on = b.dataset.strat === state.strategy;
      b.classList.toggle("btn--primary", on);
      b.classList.toggle("btn--ghost", !on);
    });
    updateCompare();
  }

  function updateCompare() {
    // Both sides must be initialised. First-time renderSide runs for "left"
    // before the "right" panel exists in the DOM loop, so guard against that.
    if (!sideState.left || !sideState.right) return;
    const left = cm[sideState.left.strategy];
    const right = cm[sideState.right.strategy];
    if (!left || !right) return;
    const leftCov = new Set((left.coveredIds || []).map(String));
    const rightCov = new Set((right.coveredIds || []).map(String));
    const diffs = [];
    for (const cls of CLASS_ORDER_LAYOUT) {
      const members = byClass.get(cls) || [];
      const l = members.filter((m) => leftCov.has(m)).length;
      const r = members.filter((m) => rightCov.has(m)).length;
      diffs.push({ cls, l, r, tot: members.length, delta: Math.abs(l - r) });
    }
    diffs.sort((a, b) => b.delta - a.delta);
    const top = diffs.slice(0, 2).filter((d) => d.delta >= 3);
    const leftName = labels[sideState.left.strategy] || sideState.left.strategy;
    const rightName = labels[sideState.right.strategy] || sideState.right.strategy;
    let msg = `<strong>${leftName}</strong> acoperă <strong>${leftCov.size}</strong>. <strong>${rightName}</strong>, <strong>${rightCov.size}</strong>.`;
    if (top.length) {
      const parts = top.map((d) => {
        const side = d.l > d.r ? leftName : rightName;
        const other = d.l > d.r ? rightName : leftName;
        return `${d.cls} apare la <strong>${side}</strong> (${Math.max(d.l, d.r)} din ${d.tot}) dar aproape lipsește la ${other} (${Math.min(d.l, d.r)}).`;
      });
      msg += " " + parts.join(" ");
    }
    compareLine.innerHTML = msg;
  }

  sides.forEach((side) => {
    const panel = document.createElement("div");
    panel.className = "strategy-duel__panel";
    const buttonBar = document.createElement("div");
    buttonBar.className = "strategy-duel__buttons";
    buttonBar.innerHTML = strategyList.map((k) =>
      `<button type="button" class="btn btn--ghost" data-strat="${esc(k)}">${esc(labels[k] || k)}</button>`
    ).join("");
    const mapHost = document.createElement("div");
    mapHost.className = "chart__svg-wrap";
    const captionEl = document.createElement("div");
    captionEl.className = "strategy-duel__caption";
    panel.appendChild(buttonBar);
    panel.appendChild(mapHost);
    panel.appendChild(captionEl);
    wrap.appendChild(panel);

    sideState[side.key] = { strategy: side.initial, buttonBar, mapHost, captionEl };
    buttonBar.querySelectorAll("[data-strat]").forEach((b) => {
      b.addEventListener("click", () => {
        sideState[side.key].strategy = b.dataset.strat;
        renderSide(side.key);
      });
    });
    renderSide(side.key);
  });
}

// Two panels, same class-clustered layout. Each panel highlights TWO people's
// individual reach zones plus their overlap. Purpose: show the difference
// between champions who cover the same area (Chloé + Gabin, both Bio C) and
// champions who cover disjoint areas (Chloé + Rémi, different classes).
// Reads individualReach for the seed IDs from build precompute.
function renderOverlapDuel(container, block, stats) {
  const cm = stats?.sliceMetrics?.mission?.coverageMaps || {};
  const positions = cm._positions || {};
  const positionsList = Object.entries(positions);
  const ir = cm._individualReach || {};
  const pairs = block.pairs || [
    { a: 778, b: 939, aName: "Chloé", bName: "Gabin" },
    { a: 778, b: 1218, aName: "Chloé", bName: "Rémi" },
  ];

  const grid = document.createElement("div");
  grid.className = "overlap-duel";
  container.appendChild(grid);

  const S = 360;
  const projX = (px) => ((px + 1) / 2) * (S - 30) + 15;
  const projY = (py) => ((py + 1) / 2) * (S - 30) + 15;

  pairs.forEach((pair) => {
    const setA = new Set((ir[String(pair.a)]?.coveredIds || []).map(String));
    const setB = new Set((ir[String(pair.b)]?.coveredIds || []).map(String));
    const both = new Set([...setA].filter((x) => setB.has(x)));
    const onlyA = new Set([...setA].filter((x) => !setB.has(x)));
    const onlyB = new Set([...setB].filter((x) => !setA.has(x)));
    const aId = String(pair.a);
    const bId = String(pair.b);
    const aName = pair.aName || ir[aId]?.name || "?";
    const bName = pair.bName || ir[bId]?.name || "?";

    const COLOR_A = "#8b4a1e";      // warm brown = A only
    const COLOR_B = "#2f6fa8";      // cool blue = B only
    const COLOR_BOTH = "#2a1f16";   // dark ink = overlap (both)
    const COLOR_MISS = "#e5dccb";   // pale = neither

    // Render base pale dots + colored dots on top. Draw missed first, then
    // A-only, then B-only, then both (largest r).
    const misses = [];
    const aOnly = [];
    const bOnly = [];
    const overlaps = [];
    positionsList.forEach(([nid, p]) => {
      const x = projX(p.x), y = projY(p.y);
      if (both.has(nid)) overlaps.push([x, y]);
      else if (onlyA.has(nid)) aOnly.push([x, y]);
      else if (onlyB.has(nid)) bOnly.push([x, y]);
      else misses.push([x, y]);
    });

    const dot = (pts, r, color, extra = "") =>
      pts.map(([x, y]) => `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${r}" fill="${color}"${extra}/>`).join("");

    // Seed markers (larger, black outline) at the two chosen people
    const pa = positions[aId]; const pb = positions[bId];
    const seedSvg = [pa, pb].filter(Boolean).map((p, i) => {
      const cx = projX(p.x), cy = projY(p.y);
      const color = i === 0 ? COLOR_A : COLOR_B;
      return `<circle cx="${cx.toFixed(1)}" cy="${cy.toFixed(1)}" r="8" fill="${color}" stroke="#000" stroke-width="1.4"/>`;
    }).join("");

    const svg =
      `<svg viewBox="0 0 ${S} ${S}" xmlns="http://www.w3.org/2000/svg" ` +
      `style="width:100%;height:auto;max-width:400px;display:block;margin:0 auto" ` +
      `role="img" aria-label="Zonele atinse de ${esc(aName)} și ${esc(bName)}">` +
      dot(misses, 2.4, COLOR_MISS) +
      dot(aOnly, 3.6, COLOR_A) +
      dot(bOnly, 3.6, COLOR_B) +
      dot(overlaps, 4.2, COLOR_BOTH) +
      seedSvg +
      `</svg>`;

    const cell = document.createElement("div");
    cell.className = "overlap-duel__cell";
    cell.innerHTML =
      `<div class="overlap-duel__title"><strong>${esc(aName)}</strong> și <strong>${esc(bName)}</strong></div>` +
      svg +
      `<div class="overlap-duel__legend">` +
        `<span><span class="overlap-duel__dot" style="background:${COLOR_A}"></span>${esc(aName)}: <strong>${setA.size}</strong></span>` +
        `<span><span class="overlap-duel__dot" style="background:${COLOR_B}"></span>${esc(bName)}: <strong>${setB.size}</strong></span>` +
        `<span><span class="overlap-duel__dot" style="background:${COLOR_BOTH}"></span>în comun: <strong>${both.size}</strong></span>` +
      `</div>`;
    grid.appendChild(cell);
  });
}

// Legacy single-map compare (kept for backward compat but not used by m5 now).
function renderStrategyCompare(container, block, stats) {
  const cm = stats?.sliceMetrics?.mission?.coverageMaps || {};
  const total = cm._total || stats?.total || 299;
  const positions = cm._positions || {};
  const strategies = block.strategies || ["knownTeam", "top3reach", "top3pop", "greedy"];
  const labels = {
    knownTeam: "Cei trei pe care îi știi",
    top3pop:   "Cei mai populari trei",
    top3open:  "Cei mai deschiși trei",
    top3reach: "Cei mai buni răspânditori",
    top3betw:  "Cei mai centrali trei",
    greedy:    "Alegerea lacomă",
  };
  const nodesArr = Object.entries(positions);

  const btnBar = document.createElement("div");
  btnBar.className = "measure-tabs__map-controls";
  container.appendChild(btnBar);

  const stage = document.createElement("div");
  stage.className = "chart__svg-wrap";
  container.appendChild(stage);

  const captionBox = document.createElement("div");
  captionBox.className = "measure-tabs__map-caption";
  container.appendChild(captionBox);

  const S = 340;
  function draw(key) {
    const data = cm[key];
    if (!data) { stage.textContent = "Fără date."; return; }
    const covered = new Set((data.coveredIds || []).map(String));
    const seedSet = new Set((data.seedIds || []).map(String));
    const dots = nodesArr.map(([nid, p]) => {
      const x = ((p.x + 1) / 2) * (S - 20) + 10;
      const y = ((p.y + 1) / 2) * (S - 20) + 10;
      const isSeed = seedSet.has(nid);
      const isCovered = covered.has(nid);
      let r, fill, stroke, sw;
      if (isSeed) { r = 5.5; fill = "#2a1f16"; stroke = "#2a1f16"; sw = 1; }
      else if (isCovered) { r = 3.2; fill = "#8b4a1e"; stroke = "none"; sw = 0; }
      else { r = 2.4; fill = "#e5dccb"; stroke = "none"; sw = 0; }
      return `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${r}" fill="${fill}"${stroke !== "none" ? ` stroke="${stroke}" stroke-width="${sw}"` : ""}/>`;
    }).join("");
    stage.innerHTML =
      `<svg viewBox="0 0 ${S} ${S}" xmlns="http://www.w3.org/2000/svg" ` +
      `style="width:100%;height:auto;max-width:400px;display:block;margin:0 auto" ` +
      `role="img" aria-label="Hartă de acoperire, ${esc(labels[key] || key)}">` +
      dots + `</svg>`;
    captionBox.innerHTML =
      `<strong>${esc(labels[key] || key)}</strong>: ${esc((data.seedNames || []).join(", "))} — <strong>${covered.size}</strong> din ${total}`;
  }

  btnBar.innerHTML = strategies.map((key, i) =>
    `<button type="button" class="btn ${i === 0 ? "btn--primary" : "btn--ghost"}" data-strategy="${esc(key)}">${esc(labels[key] || key)}</button>`
  ).join("");
  btnBar.querySelectorAll("[data-strategy]").forEach((btn) => {
    btn.addEventListener("click", () => {
      btnBar.querySelectorAll("[data-strategy]").forEach((b) => { b.classList.remove("btn--primary"); b.classList.add("btn--ghost"); });
      btn.classList.remove("btn--ghost"); btn.classList.add("btn--primary");
      draw(btn.dataset.strategy);
    });
  });
  draw(strategies[0]);
}

function renderStrategyMaps(container, block, stats) {
  const cm = stats?.sliceMetrics?.mission?.coverageMaps || {};
  const total = cm._total || stats?.total || 299;
  const positions = cm._positions || {};
  const strategies = block.strategies || ["knownTeam", "top3pop", "greedy", "top3open"];
  const labels = {
    knownTeam: "Cei trei pe care îi știi",
    top3pop:   "Cei mai populari trei",
    top3open:  "Cei mai deschiși trei",
    greedy:    "Alegerea lacomă",
  };

  const nodesArr = Object.entries(positions);

  const grid = document.createElement("div");
  grid.className = "coverage-maps";
  container.appendChild(grid);

  for (const key of strategies) {
    const data = cm[key];
    if (!data) continue;
    const covered = new Set((data.coveredIds || []).map(String));
    const seedSet = new Set((data.seedIds || []).map(String));
    const cell = document.createElement("div");
    cell.className = "coverage-maps__cell";
    const S = 220;
    const dots = nodesArr.map(([nid, p]) => {
      const x = ((p.x + 1) / 2) * (S - 20) + 10;
      const y = ((p.y + 1) / 2) * (S - 20) + 10;
      const isSeed = seedSet.has(nid);
      const isCovered = covered.has(nid);
      let r, fill, stroke, sw;
      if (isSeed) { r = 4.5; fill = "#2a1f16"; stroke = "#2a1f16"; sw = 1; }
      else if (isCovered) { r = 2.8; fill = "#8b4a1e"; stroke = "none"; sw = 0; }
      else { r = 2.2; fill = "#e5dccb"; stroke = "none"; sw = 0; }
      return `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${r}" fill="${fill}"${stroke !== "none" ? ` stroke="${stroke}" stroke-width="${sw}"` : ""}/>`;
    }).join("");
    cell.innerHTML =
      `<div class="coverage-maps__cap">${esc(labels[key] || key)}</div>` +
      `<svg viewBox="0 0 ${S} ${S}" xmlns="http://www.w3.org/2000/svg" ` +
      `style="width:100%;height:auto;max-width:240px;display:block;margin:0 auto" ` +
      `role="img" aria-label="Hartă de acoperire pentru ${esc(labels[key] || key)}">` +
      dots + `</svg>` +
      `<div class="coverage-maps__stat"><strong>${covered.size}</strong> din ${total}</div>` +
      (data.seedNames && data.seedNames.length ? `<div class="coverage-maps__seeds">${data.seedNames.map(esc).join(", ")}</div>` : "");
    grid.appendChild(cell);
  }
}

function renderStrategies(container, block, stats) {
  const sm = stats?.sliceMetrics || {};
  const mission = sm.mission || {};
  const total = stats?.total || 299;
  const plafon = mission.plafon || sm.plafon || 290;
  const strats = sm.strategies || {};

  // Recover userSeed coverage if present via progress; for now, allow block.userScore
  const rows = [
    { key: "top3pop",  label: "Cei mai populari trei", value: mission.top3PopularCoverage ?? 0, seeds: mission.top3PopularNames || [] },
    { key: "top3open", label: "Cei mai deschiși trei", value: mission.top3OpenCoverage ?? 0, seeds: mission.top3OpenNames || [] },
    { key: "oneEach",  label: "Câte unul din trei comunități", value: strats.oneEachComm?.coverage ?? 0, seeds: (strats.oneEachComm?.seeds || []).map((s) => s.name || s) },
    { key: "greedy",   label: "Alegerea lacomă", value: mission.greedyCoverage ?? 0, seeds: mission.greedyNames || [] },
    { key: "random",   label: "La întâmplare (30 rulări)", value: mission.randomMean ?? 0, minV: mission.randomMin, maxV: mission.randomMax, isRandom: true },
  ];
  if (typeof block.userScore === "number") {
    rows.push({ key: "user", label: "Alegerea ta", value: block.userScore, seeds: block.userSeeds || [], isUser: true });
  }

  const wrap = document.createElement("div");
  wrap.className = "chart__wrap chart__wrap--strategies";
  container.appendChild(wrap);

  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("class", "chart__svg chart__svg--strategies");
  svg.setAttribute("viewBox", "0 0 720 320");
  svg.setAttribute("preserveAspectRatio", "xMidYMid meet");
  wrap.appendChild(svg);

  const W = 720, H = 320;
  const M = { top: 20, right: 30, bottom: 40, left: 200 };
  const iw = W - M.left - M.right;
  const ih = H - M.top - M.bottom;
  const xMax = Math.max(plafon, total, ...rows.map((r) => r.maxV || r.value));

  const xScale = (v) => M.left + (v / xMax) * iw;

  // Plafon line
  const plafG = document.createElementNS("http://www.w3.org/2000/svg", "g");
  const plafX = xScale(plafon);
  const plafLine = document.createElementNS("http://www.w3.org/2000/svg", "line");
  plafLine.setAttribute("x1", plafX); plafLine.setAttribute("y1", M.top - 4);
  plafLine.setAttribute("x2", plafX); plafLine.setAttribute("y2", M.top + ih + 4);
  plafLine.setAttribute("stroke", "#2a1f16"); plafLine.setAttribute("stroke-width", "1");
  plafLine.setAttribute("stroke-dasharray", "4 3");
  plafG.appendChild(plafLine);
  const plafLbl = document.createElementNS("http://www.w3.org/2000/svg", "text");
  // Place the label INSIDE the chart area, to the LEFT of the plafon line,
  // right-aligned so "plafon 290" never clips the right edge of the viewBox.
  plafLbl.setAttribute("x", plafX - 4); plafLbl.setAttribute("y", M.top + 8);
  plafLbl.setAttribute("text-anchor", "end");
  plafLbl.setAttribute("font-size", "10"); plafLbl.setAttribute("fill", "#2a1f16");
  plafLbl.textContent = `plafon ${plafon}`;
  plafG.appendChild(plafLbl);
  svg.appendChild(plafG);

  // Bars
  const barH = Math.min(28, (ih - 8) / rows.length - 6);
  rows.forEach((r, i) => {
    const y = M.top + i * (barH + 8) + 2;
    // Label
    const lbl = document.createElementNS("http://www.w3.org/2000/svg", "text");
    lbl.setAttribute("x", M.left - 8); lbl.setAttribute("y", y + barH / 2 + 4);
    lbl.setAttribute("text-anchor", "end"); lbl.setAttribute("font-size", "11");
    lbl.setAttribute("fill", "#2a1f16"); lbl.textContent = r.label;
    svg.appendChild(lbl);

    if (r.isRandom) {
      // Whisker: from min to max, box for range
      const xMin = xScale(r.minV || 0); const xMean = xScale(r.value); const xMx = xScale(r.maxV || 0);
      const midY = y + barH / 2;
      const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
      line.setAttribute("x1", xMin); line.setAttribute("y1", midY);
      line.setAttribute("x2", xMx);  line.setAttribute("y2", midY);
      line.setAttribute("stroke", "#8a7a68"); line.setAttribute("stroke-width", "2");
      svg.appendChild(line);
      // caps
      for (const xx of [xMin, xMx]) {
        const cap = document.createElementNS("http://www.w3.org/2000/svg", "line");
        cap.setAttribute("x1", xx); cap.setAttribute("y1", midY - 6);
        cap.setAttribute("x2", xx); cap.setAttribute("y2", midY + 6);
        cap.setAttribute("stroke", "#8a7a68"); cap.setAttribute("stroke-width", "2");
        svg.appendChild(cap);
      }
      const meanDot = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      meanDot.setAttribute("cx", xMean); meanDot.setAttribute("cy", midY);
      meanDot.setAttribute("r", "5"); meanDot.setAttribute("fill", "#5a4a3a");
      svg.appendChild(meanDot);
      const valLbl = document.createElementNS("http://www.w3.org/2000/svg", "text");
      valLbl.setAttribute("x", xMx + 6); valLbl.setAttribute("y", midY + 4);
      valLbl.setAttribute("font-size", "11"); valLbl.setAttribute("fill", "#2a1f16");
      valLbl.textContent = `medie ${Math.round(r.value)}, min ${r.minV}, max ${r.maxV}`;
      svg.appendChild(valLbl);
    } else {
      const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
      rect.setAttribute("x", M.left); rect.setAttribute("y", y);
      rect.setAttribute("width", Math.max(0, xScale(r.value) - M.left));
      rect.setAttribute("height", barH);
      const isGreedy = r.key === "greedy";
      const isUser = r.isUser;
      rect.setAttribute("fill", isGreedy ? "#5a4a3a" : (isUser ? "#a3341f" : "#8b4a1e"));
      rect.setAttribute("opacity", "0.85");
      svg.appendChild(rect);
      const valLbl = document.createElementNS("http://www.w3.org/2000/svg", "text");
      valLbl.setAttribute("x", xScale(r.value) + 6); valLbl.setAttribute("y", y + barH / 2 + 4);
      valLbl.setAttribute("font-size", "11"); valLbl.setAttribute("fill", "#2a1f16");
      valLbl.textContent = String(r.value);
      svg.appendChild(valLbl);
    }
  });

  // x-axis ticks at bottom
  const axG = document.createElementNS("http://www.w3.org/2000/svg", "g");
  const axLine = document.createElementNS("http://www.w3.org/2000/svg", "line");
  axLine.setAttribute("x1", M.left); axLine.setAttribute("y1", M.top + ih);
  axLine.setAttribute("x2", M.left + iw); axLine.setAttribute("y2", M.top + ih);
  axLine.setAttribute("stroke", "#8a7a68"); axLine.setAttribute("stroke-width", "0.7");
  axG.appendChild(axLine);
  for (let i = 0; i <= 5; i++) {
    const v = Math.round((i / 5) * xMax);
    const x = xScale(v);
    const t = document.createElementNS("http://www.w3.org/2000/svg", "text");
    t.setAttribute("x", x); t.setAttribute("y", M.top + ih + 15);
    t.setAttribute("text-anchor", "middle"); t.setAttribute("font-size", "10");
    t.setAttribute("fill", "#5a4a3a"); t.textContent = String(v);
    axG.appendChild(t);
  }
  svg.appendChild(axG);
}

function renderRanking(container, block, stats) {
  const sm = stats?.sliceMetrics || {};
  const scatter = sm.scatterData || [];
  const characters = sm.characters || {};
  const corr = sm.correlations || {};
  if (!scatter.length) { container.textContent = "Fără date pentru clasament."; return; }

  const HIGHLIGHTS = [
    { key: "vedeta",   role: characters.vedeta,   color: "#2a1f16" },
    { key: "puntea",   role: characters.puntea,   color: "#3d7a52" },
    { key: "campion",  role: characters.campion,  color: "#a3341f" },
    { key: "surpriza", role: characters.surpriza, color: "#8b4a1e" },
  ].filter((h) => h.role);
  const highlightIds = new Map(HIGHLIGHTS.map((h) => [Number(h.role.id), h]));

  const AXES = {
    popularity: { label: "Popularitate", corr: corr.popularityReach || 0, field: "popularity", intro: "Liniile se încrucișează în toate direcțiile. Elevi din vârful popularității cad la mijloc, iar elevi de jos urcă în vârf." },
    groups:     { label: "Deschidere",   corr: corr.groupsReach     || 0, field: "groups",     intro: "Puțin mai bine, dar tot haos." },
    reach2:     { label: "Rază la 2 pași", corr: corr.reach2Reach   || 0, field: "reach2",     intro: "Acum liniile sunt aproape paralele. Măsura prezice." }
  };

  let axisMode = "popularity";

  const wrap = document.createElement("div");
  wrap.className = "chart__wrap chart__wrap--ranking";
  container.appendChild(wrap);

  const legend = document.createElement("div");
  legend.className = "chart__meta chart__meta--legend";
  legend.textContent = "Fiecare linie e un elev. În stânga, poziția lui după măsura aleasă. În dreapta, poziția lui după câți oameni află de la el. Dacă măsura prezice bine, liniile sunt paralele.";
  wrap.appendChild(legend);

  const controls = document.createElement("div");
  controls.className = "chart__controls";
  controls.innerHTML =
    `<div class="diff-row diff-buttons">` +
      `<button type="button" class="btn btn--primary" data-axis="popularity">Popularitate</button>` +
      `<button type="button" class="btn btn--ghost" data-axis="groups">Deschidere</button>` +
      `<button type="button" class="btn btn--ghost" data-axis="reach2">Rază la 2 pași</button>` +
    `</div>` +
    `<div class="chart__meta chart__meta--corr" data-role="corr"></div>` +
    `<div class="chart__meta" data-role="hint"></div>`;
  wrap.appendChild(controls);

  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("class", "chart__svg--ranking");
  // Height reduced from 640 to 460 so the chart hugs its content; viewBox width
  // narrowed to make label margins predictable.
  svg.setAttribute("viewBox", "0 0 640 460");
  svg.setAttribute("preserveAspectRatio", "xMidYMid meet");
  wrap.appendChild(svg);

  function draw() {
    svg.innerHTML = "";
    const W = 640, H = 460;
    const M = { top: 30, right: 130, bottom: 15, left: 130 };
    const colX_left = M.left;
    const colX_right = W - M.right;
    const y0 = M.top, y1 = H - M.bottom;
    const cur = AXES[axisMode];

    const leftOrder = [...scatter].sort((a, b) =>
      (b[cur.field] || 0) - (a[cur.field] || 0) || a.name.localeCompare(b.name));
    const leftIdxOf = new Map();
    leftOrder.forEach((p, i) => leftIdxOf.set(Number(p.id), i));

    const rightOrder = [...scatter].sort((a, b) =>
      (b.reach || 0) - (a.reach || 0) || a.name.localeCompare(b.name));
    const rightIdxOf = new Map();
    rightOrder.forEach((p, i) => rightIdxOf.set(Number(p.id), i));

    const N = scatter.length;
    const yFor = (idx) => y0 + (idx / (N - 1)) * (y1 - y0);

    // Column titles
    const t1 = document.createElementNS("http://www.w3.org/2000/svg", "text");
    t1.setAttribute("x", colX_left); t1.setAttribute("y", 18);
    t1.setAttribute("text-anchor", "middle"); t1.setAttribute("font-size", "13");
    t1.setAttribute("font-weight", "600"); t1.setAttribute("fill", "#2a1f16");
    t1.textContent = cur.label;
    svg.appendChild(t1);
    const t2 = document.createElementNS("http://www.w3.org/2000/svg", "text");
    t2.setAttribute("x", colX_right); t2.setAttribute("y", 18);
    t2.setAttribute("text-anchor", "middle"); t2.setAttribute("font-size", "13");
    t2.setAttribute("font-weight", "600"); t2.setAttribute("fill", "#2a1f16");
    t2.textContent = "Rază";
    svg.appendChild(t2);

    // Anonymous lines: thin, slightly darker + slightly wider for visibility.
    const lineG = document.createElementNS("http://www.w3.org/2000/svg", "g");
    for (const p of scatter) {
      const id = Number(p.id);
      if (highlightIds.has(id)) continue;
      const l = document.createElementNS("http://www.w3.org/2000/svg", "line");
      l.setAttribute("x1", colX_left);  l.setAttribute("y1", yFor(leftIdxOf.get(id)));
      l.setAttribute("x2", colX_right); l.setAttribute("y2", yFor(rightIdxOf.get(id)));
      l.setAttribute("stroke", "#5a4a3a"); l.setAttribute("stroke-width", "0.7");
      l.setAttribute("opacity", "0.15");
      lineG.appendChild(l);
    }
    svg.appendChild(lineG);

    // Highlighted characters, with label anti-collision: compute label Y
    // positions per side, force at least 16px vertical spacing.
    const highG = document.createElementNS("http://www.w3.org/2000/svg", "g");
    const withY = HIGHLIGHTS.map((h) => {
      const id = Number(h.role.id);
      return { h, y_l: yFor(leftIdxOf.get(id)), y_r: yFor(rightIdxOf.get(id)) };
    });
    // Draw lines first (using raw Y)
    for (const { h, y_l, y_r } of withY) {
      const l = document.createElementNS("http://www.w3.org/2000/svg", "line");
      l.setAttribute("x1", colX_left);  l.setAttribute("y1", y_l);
      l.setAttribute("x2", colX_right); l.setAttribute("y2", y_r);
      l.setAttribute("stroke", h.color); l.setAttribute("stroke-width", "2.5");
      l.setAttribute("opacity", "0.9");
      highG.appendChild(l);
    }
    // Compute label positions to avoid overlap on each side.
    function spread(items, key) {
      const MIN = 16;
      const sorted = items.slice().sort((a, b) => a[key] - b[key]);
      for (let i = 1; i < sorted.length; i++) {
        const diff = sorted[i][key] - sorted[i - 1][key];
        if (diff < MIN) sorted[i][key] = sorted[i - 1][key] + MIN;
      }
      // Also clip to [y0, y1]
      for (const it of sorted) {
        if (it[key] < y0 + 4) it[key] = y0 + 4;
        if (it[key] > y1 - 4) it[key] = y1 - 4;
      }
      return sorted;
    }
    const withLabelY = withY.map((it) => ({ ...it, lbl_l: it.y_l, lbl_r: it.y_r }));
    spread(withLabelY, "lbl_l");
    spread(withLabelY, "lbl_r");

    for (const it of withLabelY) {
      const { h, lbl_l, lbl_r } = it;
      const tL = document.createElementNS("http://www.w3.org/2000/svg", "text");
      tL.setAttribute("x", colX_left - 10); tL.setAttribute("y", lbl_l + 4);
      tL.setAttribute("text-anchor", "end"); tL.setAttribute("font-size", "12");
      tL.setAttribute("font-weight", "600"); tL.setAttribute("fill", h.color);
      tL.textContent = h.role.name;
      highG.appendChild(tL);
      const tR = document.createElementNS("http://www.w3.org/2000/svg", "text");
      tR.setAttribute("x", colX_right + 10); tR.setAttribute("y", lbl_r + 4);
      tR.setAttribute("text-anchor", "start"); tR.setAttribute("font-size", "12");
      tR.setAttribute("font-weight", "600"); tR.setAttribute("fill", h.color);
      tR.textContent = h.role.name;
      highG.appendChild(tR);
    }
    svg.appendChild(highG);

    const corrEl = controls.querySelector('[data-role="corr"]');
    if (corrEl) corrEl.innerHTML = `Corelație <strong>${cur.label.toLowerCase()}</strong> vs rază: <strong>${(cur.corr).toFixed(2)}</strong>`;
    const hintEl = controls.querySelector('[data-role="hint"]');
    if (hintEl) hintEl.textContent = cur.intro;
  }

  controls.querySelectorAll("[data-axis]").forEach((btn) => {
    btn.addEventListener("click", () => {
      axisMode = btn.dataset.axis;
      controls.querySelectorAll("[data-axis]").forEach((b) => {
        if (b.dataset.axis === axisMode) { b.classList.add("btn--primary"); b.classList.remove("btn--ghost"); }
        else { b.classList.remove("btn--primary"); b.classList.add("btn--ghost"); }
      });
      draw();
    });
  });

  draw();
}

export async function renderChart(container, block) {
  container.classList.add("chart");
  container.innerHTML = "";

  try {
    if (block.variant === "histogram") {
      const values = await getValues(block);
      if (!values.length) { container.textContent = "Fără date pentru histogramă."; return { refit(){}, destroy(){} }; }
      const api = renderHistogram(container, block, values);
      return { refit() {}, destroy() {}, ...api };
    }
    if (block.variant === "bars") {
      renderBars(container, block);
      return { refit() {}, destroy() {} };
    }
    if (block.variant === "hbars") {
      renderHBars(container, block);
      return { refit() {}, destroy() {} };
    }
    if (block.variant === "dots") {
      const values = await getValues(block);
      const stats = await getStats(block);
      await renderDots(container, block, values, stats);
      return { refit() {}, destroy() {} };
    }
    if (block.variant === "strip") {
      const values = await getValues(block);
      renderStrip(container, block, values);
      return { refit() {}, destroy() {} };
    }
    if (block.variant === "freq") {
      const stats = await getStats(block);
      renderFreq(container, block, stats);
      return { refit() {}, destroy() {} };
    }
    if (block.variant === "grouped-strip") {
      const stats = await getStats(block);
      renderGroupedStrip(container, block, stats);
      return { refit() {}, destroy() {} };
    }
    if (block.variant === "stacked") {
      const stats = await getStats(block);
      renderStacked(container, block, stats);
      return { refit() {}, destroy() {} };
    }
    if (block.variant === "meanmedian") {
      const values = await getValues(block);
      renderMeanMedian(container, block, values);
      return { refit() {}, destroy() {} };
    }
    if (block.variant === "states") {
      const values = await getValues(block);
      const stats = await getStats(block);
      await renderStates(container, block, values, stats);
      return { refit() {}, destroy() {} };
    }
    if (block.variant === "triple-histogram") {
      const stats = await getStats(block);
      await renderTripleHistogram(container, block, stats);
      return { refit() {}, destroy() {} };
    }
    if (block.variant === "sex-composition") {
      const stats = await getStats(block);
      renderSexComposition(container, block, stats);
      return { refit() {}, destroy() {} };
    }
    if (block.variant === "scatter") {
      const stats = await getStats(block);
      renderScatter(container, block, stats);
      return { refit() {}, destroy() {} };
    }
    if (block.variant === "strategy-maps") {
      const stats = await getStats(block);
      renderStrategyMaps(container, block, stats);
      return { refit() {}, destroy() {} };
    }
    if (block.variant === "friends-tabs") {
      const stats = await getStats(block);
      await renderFriendsTabs(container, block, stats);
      return { refit() {}, destroy() {} };
    }
    if (block.variant === "unreached-multi") {
      const stats = await getStats(block);
      await renderUnreachedMulti(container, block, stats);
      return { refit() {}, destroy() {} };
    }
    if (block.variant === "measure-tabs") {
      const stats = await getStats(block);
      await renderMeasureTabs(container, block, stats);
      return { refit() {}, destroy() {} };
    }
    if (block.variant === "robustness") {
      const stats = await getStats(block);
      renderRobustness(container, block, stats);
      return { refit() {}, destroy() {} };
    }
    if (block.variant === "strategy-compare") {
      const stats = await getStats(block);
      renderStrategyCompare(container, block, stats);
      return { refit() {}, destroy() {} };
    }
    if (block.variant === "strategy-duel") {
      const stats = await getStats(block);
      renderStrategyDuel(container, block, stats);
      return { refit() {}, destroy() {} };
    }
    if (block.variant === "overlap-duel") {
      const stats = await getStats(block);
      renderOverlapDuel(container, block, stats);
      return { refit() {}, destroy() {} };
    }
    if (block.variant === "strategies") {
      const stats = await getStats(block);
      renderStrategies(container, block, stats);
      return { refit() {}, destroy() {} };
    }
    if (block.variant === "ranking") {
      const stats = await getStats(block);
      renderRanking(container, block, stats);
      return { refit() {}, destroy() {} };
    }
    if (block.variant === "outcome-histogram") {
      const hint = document.createElement("div");
      hint.className = "chart__meta";
      hint.textContent = 'Va fi populat la „Rulează de 100 de ori" din difuzia SIR.';
      container.appendChild(hint);
      return { refit() {}, destroy() {} };
    }
    container.textContent = `Grafic necunoscut: ${block.variant}`;
  } catch (err) {
    container.textContent = `Eroare grafic: ${err.message}`;
  }
  return { refit() {}, destroy() {} };
}
