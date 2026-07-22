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
    return d.nodes || [];
  } catch { return []; }
}

function renderFreq(container, block, stats) {
  const src = statsBucket(block, stats);
  const cf = src?.classFreq || {};
  const rows = Object.entries(cf).filter(([k]) => k !== "globalBetweenPct");
  const total = rows.reduce((s, [, v]) => s + (v.n || 0), 0);

  const table = document.createElement("table");
  table.className = "chart__freq";
  const header = `<tr><th></th><th>elevi</th><th>fete</th><th>băieți</th></tr>`;
  const body = rows.map(([k, v]) =>
    `<tr><th>${esc(k)}</th><td>${v.n}</td><td>${v.nF}</td><td>${v.nM}</td></tr>`
  ).join("");
  table.innerHTML = header + body + `<tr class="chart__freq__total"><th>total</th><td>${total}</td><td>${rows.reduce((s, [, v]) => s + v.nF, 0)}</td><td>${rows.reduce((s, [, v]) => s + v.nM, 0)}</td></tr>`;
  container.appendChild(table);

  const maxV = Math.max(...rows.flatMap(([, v]) => [v.nF, v.nM]), 1);
  const W = 420, H = 160;
  const padL = 60, padR = 12, padT = 12, padB = 30;
  const chartW = W - padL - padR;
  const chartH = H - padT - padB;
  const rowH = chartH / rows.length;
  const barGap = 4;
  const svgRows = rows.map(([k, v], i) => {
    const y0 = padT + i * rowH + 4;
    const halfH = (rowH - 8 - barGap) / 2;
    const wF = (v.nF / maxV) * chartW;
    const wM = (v.nM / maxV) * chartW;
    return (
      `<text x="${padL - 6}" y="${(y0 + halfH).toFixed(1)}" text-anchor="end" font-size="11" fill="${COL_INK_S}">${esc(k)}</text>` +
      `<rect x="${padL}" y="${y0.toFixed(1)}" width="${wF.toFixed(1)}" height="${halfH.toFixed(1)}" fill="${COL_BAR_B}" rx="2"/>` +
      `<text x="${(padL + wF + 4).toFixed(1)}" y="${(y0 + halfH - 1).toFixed(1)}" font-size="11" fill="${COL_INK}">${v.nF}F</text>` +
      `<rect x="${padL}" y="${(y0 + halfH + barGap).toFixed(1)}" width="${wM.toFixed(1)}" height="${halfH.toFixed(1)}" fill="${COL_BAR}" rx="2"/>` +
      `<text x="${(padL + wM + 4).toFixed(1)}" y="${(y0 + halfH + barGap + halfH - 1).toFixed(1)}" font-size="11" fill="${COL_INK}">${v.nM}M</text>`
    );
  }).join("");

  const svg = document.createElement("div");
  svg.className = "chart__svg-wrap";
  const barRects = rows.map(([k], i) => `data-class="${esc(k)}"`).join("|"); // marker for tap
  svg.innerHTML =
    `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" ` +
    `style="width:100%;height:auto;max-width:520px;display:block;margin:0 auto" ` +
    `role="img" aria-label="Compoziția claselor">` +
    svgRows +
    `</svg>`;
  container.appendChild(svg);

  if (block.linkNetwork) {
    const rowsHost = document.createElement("div");
    rowsHost.className = "chart__link-target";
    rowsHost.textContent = "Atinge un rând din tabel pentru lista de nume.";
    container.appendChild(rowsHost);
    const tableRows = container.querySelectorAll(".chart__freq tr");
    // Bind class name from the row header if present
    let nodesCache = null;
    async function ensureNodes() { if (!nodesCache) nodesCache = await loadNodesForLink(block); return nodesCache; }
    tableRows.forEach((tr, idx) => {
      const th = tr.querySelector("th");
      if (!th || idx === 0 || tr.classList.contains("chart__freq__total")) return;
      tr.classList.add("chart__freq__tappable");
      tr.addEventListener("click", async () => {
        const cls = th.textContent.trim();
        const ns = await ensureNodes();
        const matching = ns.filter((n) => (n.group || n.clasa) === cls);
        rowsHost.innerHTML = `<strong>${esc(cls)}</strong> (${matching.length}): ` +
          matching.map((n) => esc(n.name || n.id)).join(", ");
      });
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
