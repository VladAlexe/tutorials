// Pure-SVG histogram + bars. No external library, no cytoscape.

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
const COL_MUTED = "#8a7a68";
const COL_INK   = "#2a1f16";
const COL_INK_S = "#5a4a3a";
const COL_BG    = "#faf7f2";

function esc(s) {
  return String(s).replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
}

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

  const controls = document.createElement("div");
  controls.className = "chart__controls";
  const defaultBW = block.defaultBinWidth || 3;
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
    const bins = binValues(values, bw);
    chartHost.innerHTML = histogramSVG(bins, bw, block);
  }
  slider.addEventListener("input", () => {
    out.textContent = slider.value;
    draw();
  });
  draw();
}

function wrapLabel(text, maxChars) {
  const words = String(text).split(" ");
  const lines = [];
  let cur = "";
  for (const w of words) {
    if ((cur + " " + w).trim().length <= maxChars) {
      cur = (cur + " " + w).trim();
    } else {
      if (cur) lines.push(cur);
      cur = w;
    }
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
      `<text x="${(x + barW / 2).toFixed(1)}" y="${(y - 6).toFixed(1)}" text-anchor="middle" font-size="18" font-weight="500" fill="${COL_INK}">${b.value}</text>` +
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

export async function renderChart(container, block) {
  container.classList.add("chart");
  container.innerHTML = "";

  try {
    if (block.variant === "histogram") {
      const values = await getValues(block);
      if (!values.length) {
        container.textContent = "Fără date pentru histogramă.";
        return { refit() {}, destroy() {} };
      }
      renderHistogram(container, block, values);
    } else if (block.variant === "bars") {
      renderBars(container, block);
    } else {
      container.textContent = `Grafic necunoscut: ${block.variant}`;
    }
  } catch (err) {
    container.textContent = `Eroare grafic: ${err.message}`;
  }

  return { refit() {}, destroy() {} };
}
