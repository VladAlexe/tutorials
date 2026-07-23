// Pure-SVG chart variants. No external library.

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

  const initialPos = values.map((v, i) => scatterPos(i, v));
  const dots = initialPos.map((p, i) =>
    `<circle cx="${p.x.toFixed(1)}" cy="${p.y.toFixed(1)}" r="3.5" fill="${COL_BAR}" fill-opacity="0.7"><title>${values[i]}</title></circle>`
  ).join("");

  chartHost.innerHTML =
    `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto;max-width:520px;display:block;margin:0 auto">` +
    axisX + dots + `</svg>`;

  const circles = chartHost.querySelectorAll("circle");
  let currentPos = initialPos;

  function histogramPos(i, v) {
    const bw = block.binWidth || 3;
    const startBin = Math.floor(minV / bw) * bw;
    const maxHi = Math.max(...values);
    const nBins = Math.floor((maxHi - startBin) / bw) + 1;
    const binPx = chartW / nBins;
    const binIdx = Math.floor((v - startBin) / bw);
    const x = padL + binIdx * binPx + binPx / 2;
    let rank = 0;
    for (let j = 0; j < i; j++) {
      if (Math.floor((values[j] - startBin) / bw) === binIdx) rank++;
    }
    const dotSize = 7;
    return { x, y: padT + chartH - (rank + 1) * dotSize };
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
      transitionTo(positionsFor(btn.dataset.state));
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
