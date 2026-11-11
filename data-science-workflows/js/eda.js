/* ===========================================================================
   Analiza exploratorie: componentele interactive ale lecției 6.

   Fiecare componentă predă un concept pe date mici și generale (simulate cu
   un generator cu sămânță fixă sau seturi clasice), iar unde are sens are și
   o filă „Pe datele noastre”, cu datele SCI primite din pagină.
   Desenul este SVG simplu (canvas doar unde sunt zeci de mii de puncte);
   culorile vin din variabilele temei, deci merg în ambele moduri.
   =========================================================================== */

const E = {};

/* --- statistici ----------------------------------------------------------- */
const rng = (s = 1) => () => { s |= 0; s = s + 0x6D2B79F5 | 0; let t = Math.imul(s ^ s >>> 15, 1 | s);
  t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
const normal = r => () => Math.sqrt(-2 * Math.log(r() || 1e-12)) * Math.cos(2 * Math.PI * r());
const medie = a => a.reduce((s, x) => s + x, 0) / a.length;
const sortat = a => [...a].sort((x, y) => x - y);
const cuantila = (a, q, gata) => { const s = gata ? a : sortat(a), i = (s.length - 1) * q, j = Math.floor(i);
  return s[j] + ((s[Math.min(j + 1, s.length - 1)] - s[j]) * (i - j) || 0); };
const mediana = a => cuantila(a, .5);
const abatere = a => { const m = medie(a); return Math.sqrt(a.reduce((s, x) => s + (x - m) ** 2, 0) / (a.length - 1)); };
const trunchiata = (a, p) => { const s = sortat(a), k = Math.floor(s.length * p); return medie(s.slice(k, s.length - k)); };
const mad = a => { const m = mediana(a); return mediana(a.map(x => Math.abs(x - m))); };
const pearson = (x, y) => { const mx = medie(x), my = medie(y); let a = 0, b = 0, c = 0;
  for (let i = 0; i < x.length; i++){ const u = x[i] - mx, v = y[i] - my; a += u * v; b += u * u; c += v * v; }
  return a / Math.sqrt(b * c); };
const ranguri = a => { const o = a.map((v, i) => [v, i]).sort((p, q) => p[0] - q[0]), r = new Array(a.length);
  for (let i = 0; i < o.length;){ let j = i; while (j + 1 < o.length && o[j + 1][0] === o[i][0]) j++;
    for (let k = i; k <= j; k++) r[o[k][1]] = (i + j) / 2 + 1; i = j + 1; } return r; };
const spearman = (x, y) => pearson(ranguri(x), ranguri(y));
const kendall = (x, y) => { let c = 0, d = 0, tx = 0, ty = 0;
  for (let i = 0; i < x.length; i++) for (let j = i + 1; j < x.length; j++){
    const a = Math.sign(x[i] - x[j]), b = Math.sign(y[i] - y[j]);
    if (a && b) (a === b ? c++ : d++); else if (a) ty++; else if (b) tx++; }
  return (c - d) / Math.sqrt((c + d + tx) * (c + d + ty)); };
const asimetrie = a => { const m = medie(a), s = abatere(a); return a.reduce((t, x) => t + ((x - m) / s) ** 3, 0) / a.length; };
const mcmmp = (x, y) => { const mx = medie(x), my = medie(y); let a = 0, b = 0;
  for (let i = 0; i < x.length; i++){ a += (x[i] - mx) * (y[i] - my); b += (x[i] - mx) ** 2; }
  const p = a / b; return [my - p * mx, p]; };

/* --- desen ---------------------------------------------------------------- */
const f = (v, d = 2) => (Math.abs(v) < 1e-9 ? 0 : v).toFixed(d).replace(".", ",").replace("-", "−");
const nr = v => Math.round(v).toLocaleString("ro-RO");
const sc = (d0, d1, r0, r1) => v => r0 + (v - d0) / ((d1 - d0) || 1) * (r1 - r0);
const repere = (a, b, n = 5) => { const p = Math.pow(10, Math.floor(Math.log10((b - a) / n || 1))),
  e = [1, 2, 2.5, 5, 10].map(k => k * p).find(k => (b - a) / k <= n) || p * 10, r = [];
  for (let v = Math.ceil(a / e) * e; v <= b + 1e-9; v += e) r.push(+v.toFixed(10)); return r; };
const svg = (w, h, corp, cls = "") => `<svg class="ed-svg ${cls}" viewBox="0 0 ${w} ${h}" preserveAspectRatio="xMidYMid meet">${corp}</svg>`;
/* axe simple: dreptunghiul [x0,x1]×[y0,y1], scalele sx, sy, domeniile */
function axe(o){
  const { x0, x1, y0, y1, sx, sy, dx, dy, ex = "", ey = "", fx = v => f(v, 0), fy = v => f(v, 0), nx = 5, ny = 4 } = o;
  let g = `<g class="ed-ax">`;
  if (dx) repere(dx[0], dx[1], nx).forEach(v => { const X = sx(v);
    g += `<line x1="${X}" x2="${X}" y1="${y1}" y2="${y1 + 4}"/><text x="${X}" y="${y1 + 16}" text-anchor="middle">${fx(v)}</text>`; });
  if (dy) repere(dy[0], dy[1], ny).forEach(v => { const Y = sy(v);
    g += `<line class="ed-grila" x1="${x0}" x2="${x1}" y1="${Y}" y2="${Y}"/><text x="${x0 - 6}" y="${Y + 4}" text-anchor="end">${fy(v)}</text>`; });
  g += `<line x1="${x0}" x2="${x1}" y1="${y1}" y2="${y1}"/>`;
  if (ex) g += `<text class="ed-et" x="${(x0 + x1) / 2}" y="${y1 + 32}" text-anchor="middle">${ex}</text>`;
  if (ey) g += `<text class="ed-et" x="${x0}" y="${y0 - 8}" text-anchor="start">${ey}</text>`;
  return g + "</g>";
}
const bloc = (gazda, html) => { gazda.innerHTML = `<div class="eda">${html}</div>`; return gazda.firstElementChild; };
const butoane = (nume, optiuni, activ) => `<div class="ed-bt" data-n="${nume}">${optiuni.map(([k, t]) =>
  `<button data-k="${k}" class="${k === activ ? "on" : ""}">${t}</button>`).join("")}</div>`;
const leaga = (el, nume, cb) => el.querySelectorAll(`.ed-bt[data-n="${nume}"] button`).forEach(b =>
  b.addEventListener("click", () => { b.parentElement.querySelectorAll("button").forEach(x => x.classList.toggle("on", x === b)); cb(b.dataset.k); }));
const glisor = (nume, et, min, max, pas, val) => `<label class="ed-gl"><span>${et}</span><input type="range" data-n="${nume}" min="${min}" max="${max}" step="${pas}" value="${val}"><output></output></label>`;
const cifre = perechi => `<div class="ed-cf">${perechi.map(([e, v, c]) => `<span class="${c || ""}"><i>${e}</i><b>${v}</b></span>`).join("")}</div>`;
const histograma = (v, b, lo, hi) => { const n = new Array(b).fill(0), w = (hi - lo) / b;
  v.forEach(x => { const k = Math.min(b - 1, Math.max(0, Math.floor((x - lo) / w))); if (x >= lo && x <= hi) n[k]++; }); return n; };
/* coordonatele SVG ale unui eveniment de pointer */
const punct = (s, e) => { const p = s.createSVGPoint(); p.x = e.clientX; p.y = e.clientY; return p.matrixTransform(s.getScreenCTM().inverse()); };


/* =========================================================================
   1. Tipurile de variabile
   ========================================================================= */
E.edTipuri = (gazda) => {
  const C = [
    { n: "vârsta", t: "numerică continuă", v: [34, 51, 27, 45, 62, 38], op: "medie, mediană, abatere standard, cuantile", g: "histogramă, boxplot, densitate" },
    { n: "copii", t: "numerică discretă", v: [2, 0, 1, 3, 1, 0], op: "medie, mediană, frecvența fiecărei valori", g: "bare pe valori" },
    { n: "venit", t: "numerică continuă, asimetrică", v: ["2.400", "9.800", "3.100", "41.000", "2.700", "5.200"], op: "mediană, cuantile; media e trasă de coadă", g: "histogramă pe scară logaritmică" },
    { n: "studii", t: "categorică ordinală", v: ["liceu", "master", "licență", "gimnaziu", "licență", "doctorat"], op: "frecvențe, mediană, ordinea; nu media", g: "bare în ordinea categoriilor" },
    { n: "județ", t: "categorică nominală", v: ["CJ", "B", "IS", "CJ", "TM", "B"], op: "frecvențe, moda; nu ordinea", g: "bare ordonate după frecvență" },
    { n: "a votat", t: "binară", v: ["da", "nu", "da", "da", "nu", "da"], op: "proporția", g: "o proporție, bare" },
  ];
  let k = 0;
  const el = bloc(gazda, `<div class="ed-tip"><table><thead><tr>${C.map((c, i) => `<th><button data-i="${i}">${c.n}</button></th>`).join("")}</tr></thead>
    <tbody>${[0, 1, 2, 3, 4, 5].map(r => `<tr>${C.map(c => `<td>${c.v[r]}</td>`).join("")}</tr>`).join("")}</tbody></table>
    <div class="ed-tip__p"></div></div>`);
  const arata = () => {
    el.querySelectorAll("th button").forEach((b, i) => b.classList.toggle("on", i === k));
    el.querySelectorAll("tr").forEach(tr => [...tr.children].forEach((td, i) => td.classList.toggle("ales", i === k)));
    const c = C[k];
    el.querySelector(".ed-tip__p").innerHTML = `<b>${c.n}</b><span><i>tipul</i>${c.t}</span><span><i>se rezumă cu</i>${c.op}</span><span><i>graficul</i>${c.g}</span>`;
  };
  el.querySelectorAll("th button").forEach(b => b.addEventListener("click", () => { k = +b.dataset.i; arata(); }));
  arata();
};


/* =========================================================================
   2. Mecanismele lipsurilor
   ========================================================================= */
E.edLipsuri = (gazda) => {
  const r = rng(7), z = normal(r), N = 220;
  const P = Array.from({ length: N }, () => { const v = 20 + r() * 50; return { v, y: 1800 + 75 * v + 900 * z() }; });
  const ADEV = medie(P.map(p => p.y));
  let mec = "mcar";
  const el = bloc(gazda, butoane("m", [["mcar", "complet aleatoare"], ["mar", "depind de vârstă"], ["mnar", "depind de venit"]], mec)
    + `<div class="ed-g"></div><div class="ed-o"></div>`);
  const W = 900, H = 230, x0 = 64, x1 = W - 16, y0 = 24, y1 = H - 40;
  const sx = sc(20, 70, x0, x1), sy = sc(2000, 9000, y1, y0);
  const deseneaza = () => {
    const rr = rng(11);
    P.forEach(p => {
      const pr = mec === "mcar" ? .35 : mec === "mar" ? 1 / (1 + Math.exp(-(p.v - 52) / 4)) : 1 / (1 + Math.exp(-(p.y - 6200) / 500));
      p.lipsa = rr() < pr; });
    const obs = P.filter(p => !p.lipsa).map(p => p.y);
    /* corecția pe vârstă: media pe grupe de vârstă, ponderată cu mărimea grupei */
    let cor = 0, tot = 0;
    for (let a = 20; a < 70; a += 10){
      const g = P.filter(p => p.v >= a && p.v < a + 10), o = g.filter(p => !p.lipsa);
      if (o.length){ cor += medie(o.map(p => p.y)) * g.length; tot += g.length; } }
    cor /= tot;
    let s = axe({ x0, x1, y0, y1, sx, sy, dx: [20, 70], dy: [2000, 9000], ex: "vârsta", ey: "venitul (lei)", fy: v => nr(v) });
    P.forEach(p => s += `<circle class="${p.lipsa ? "ed-lipsa" : "ed-p"}" cx="${sx(p.v)}" cy="${sy(p.y)}" r="4"/>`);
    [[ADEV, "ed-l-adev"], [medie(obs), "ed-l-obs"]].forEach(([m, c]) => s += `<line class="${c}" x1="${x0}" x2="${x1}" y1="${sy(m)}" y2="${sy(m)}"/>`);
    el.querySelector(".ed-g").innerHTML = svg(W, H, s);
    const dev = 100 * (medie(obs) / ADEV - 1), devc = 100 * (cor / ADEV - 1);
    el.querySelector(".ed-o").innerHTML = cifre([
      ["lipsesc", `${P.length - obs.length} din ${P.length}`],
      ["media adevărată", nr(ADEV), "ed-c-adev"],
      ["media cazurilor complete", `${nr(medie(obs))} (${dev >= 0 ? "+" : "−"}${f(Math.abs(dev), 1)}%)`, "ed-c-obs"],
      ["media corectată pe vârstă", `${nr(cor)} (${devc >= 0 ? "+" : "−"}${f(Math.abs(devc), 1)}%)`]]);
  };
  leaga(el, "m", k => { mec = k; deseneaza(); });
  deseneaza();
};


/* =========================================================================
   3. Numerele mici: graficul-pâlnie
   ========================================================================= */
E.edMici = (gazda) => {
  let samanta = 3;
  const p = .05, N = 300, W = 900, H = 230, x0 = 56, x1 = W - 16, y0 = 20, y1 = H - 42;
  const el = bloc(gazda, `<div class="ed-ctl"><button class="ed-b">o nouă extragere</button></div><div class="ed-g"></div><div class="ed-o"></div>`);
  const sx = sc(2, 5, x0, x1), sy = sc(0, .16, y1, y0);
  const deseneaza = () => {
    const r = rng(samanta), z = normal(r);
    const U = Array.from({ length: N }, () => { const n = Math.round(10 ** (2 + 3 * r()));
      const k = n < 400 ? Array.from({ length: n }, () => r() < p).filter(Boolean).length
        : Math.max(0, Math.round(n * p + z() * Math.sqrt(n * p * (1 - p))));
      return { n, rata: k / n }; });
    const ord = [...U].sort((a, b) => b.rata - a.rata), sus = new Set(ord.slice(0, 10)), jos = new Set(ord.slice(-10));
    let s = axe({ x0, x1, y0, y1, sx, sy, dx: [2, 5], dy: [0, .16], ex: "populația (scară logaritmică)", ey: "rata observată",
      fx: v => nr(10 ** v), fy: v => f(100 * v, 0) + "%" });
    [[2, "ed-pl2"], [3, "ed-pl3"]].forEach(([k, c]) => [1, -1].forEach(sg => {
      const d = []; for (let L = 2; L <= 5.001; L += .05){ const n = 10 ** L; d.push(`${sx(L)},${sy(Math.max(0, p + sg * k * Math.sqrt(p * (1 - p) / n)))}`); }
      s += `<polyline class="${c}" points="${d.join(" ")}"/>`; }));
    s += `<line class="ed-l-adev" x1="${x0}" x2="${x1}" y1="${sy(p)}" y2="${sy(p)}"/>`;
    U.forEach(u => s += `<circle class="${sus.has(u) ? "ed-sus" : jos.has(u) ? "ed-jos" : "ed-p ed-slab"}" cx="${sx(Math.log10(u.n))}" cy="${sy(Math.min(u.rata, .16))}" r="${sus.has(u) || jos.has(u) ? 5 : 3.5}"/>`);
    el.querySelector(".ed-g").innerHTML = svg(W, H, s);
    const mici = [...sus, ...jos].filter(u => u.n < 1000).length;
    el.querySelector(".ed-o").innerHTML = cifre([
      ["rata adevărată", "5% în toate unitățile", "ed-c-adev"],
      ["cele 10 rate cele mai mari", `${[...sus].filter(u => u.n < 1000).length} sub 1.000 de locuitori`, "ed-c-sus"],
      ["cele 10 cele mai mici", `${[...jos].filter(u => u.n < 1000).length} sub 1.000 de locuitori`, "ed-c-jos"],
      ["din 20 de extreme", `${mici} sunt unități mici`]]);
  };
  el.querySelector(".ed-b").addEventListener("click", () => { samanta++; deseneaza(); });
  deseneaza();
};


/* =========================================================================
   4. Locația, variabilitatea, rezistența
   ========================================================================= */
E.edRezistenta = (gazda) => {
  const r = rng(5), z = normal(r);
  const B = Array.from({ length: 40 }, () => 50 + 9 * z()).sort((a, b) => a - b);
  const W = 900, H = 210, x0 = 20, x1 = W - 20;
  const el = bloc(gazda, glisor("k", "valori contaminate", 0, 20, 1, 0) + `<div class="ed-g"></div><div class="ed-o"></div>`);
  const inp = el.querySelector("input"), out = el.querySelector("output");
  const deseneaza = () => {
    const k = +inp.value; out.textContent = `${k} din 40 (${k * 2.5}%)`;
    const v = B.map((x, i) => i >= 40 - k ? 260 + (i - (40 - k)) * 12 : x);
    const sx = sc(0, 520, x0, x1);
    const M = [["media", medie(v), "ed-m1"], ["media trunchiată 10%", trunchiata(v, .1), "ed-m2"], ["mediana", mediana(v), "ed-m3"]];
    let s = axe({ x0, x1, y0: 10, y1: 120, sx, sy: v => v, dx: [0, 520], nx: 10, ex: "valoarea" });
    const st = {}; v.forEach((x, i) => { const b = Math.round(x / 3); st[b] = (st[b] || 0) + 1;
      s += `<circle class="${i >= 40 - k ? "ed-sus" : "ed-p"}" cx="${sx(b * 3)}" cy="${116 - st[b] * 9}" r="4.2"/>`; });
    M.forEach(([e, m, c], j) => s += `<g class="${c}"><line x1="${sx(m)}" x2="${sx(m)}" y1="${8 + j * 15}" y2="120"/><text x="${sx(m) + 5}" y="${18 + j * 15}">${e}</text></g>`);
    el.querySelector(".ed-g").innerHTML = svg(W, 165, s);
    const q = cuantila(v, .75) - cuantila(v, .25);
    el.querySelector(".ed-o").innerHTML = cifre([
      ["media", f(M[0][1], 1), "ed-c-m1"], ["media trunchiată", f(M[1][1], 1), "ed-c-m2"], ["mediana", f(M[2][1], 1), "ed-c-m3"],
      ["abaterea standard", f(abatere(v), 1)], ["IQR", f(q, 1)], ["MAD", f(mad(v), 1)]]);
  };
  inp.addEventListener("input", deseneaza);
  deseneaza();
};


/* =========================================================================
   5. Distribuția: cinci grafice pentru aceleași date
   ========================================================================= */
E.edDistributie = (gazda, d) => {
  const r = rng(9), z = normal(r);
  const EX = Array.from({ length: 260 }, () => r() < .6 ? 30 + 5 * z() : 55 + 6 * z());
  const SCI = (d.sci || []).filter(x => x > 0).map(x => Math.log10(x));
  let set = "ex", fel = "hist";
  const el = bloc(gazda, `<div class="ed-ctl">${butoane("s", [["ex", "exemplul"], ["sci", "SCI (log10)"]], set)}${butoane("f", [["hist", "histogramă"], ["dens", "densitate"], ["ecdf", "ECDF"], ["box", "boxplot"], ["viol", "violin și puncte"]], fel)}</div>
    <div class="ed-ctl ed-gls">${glisor("b", "bare", 3, 60, 1, 14)}${glisor("o", "începutul barelor", 0, 1, .05, 0)}${glisor("h", "netezirea", .02, .4, .01, .08)}</div><div class="ed-g"></div>`);
  const [ib, io, ih] = ["b", "o", "h"].map(n => el.querySelector(`input[data-n="${n}"]`));
  const W = 900, H = 220, x0 = 50, x1 = W - 16, y0 = 18, y1 = H - 40;
  const kde = (v, lo, hi, h) => { const bw = h * (hi - lo), n = 160, rez = [];
    for (let i = 0; i <= n; i++){ const x = lo + (hi - lo) * i / n; let s = 0;
      for (const u of v) s += Math.exp(-.5 * ((x - u) / bw) ** 2); rez.push([x, s / (v.length * bw * 2.5066)]); } return rez; };
  const deseneaza = () => {
    const v = set === "ex" ? EX : SCI; if (!v.length) return;
    const lo = Math.floor(Math.min(...v)) - (set === "ex" ? 2 : 0), hi = Math.ceil(Math.max(...v)) + (set === "ex" ? 2 : 0);
    const sx = sc(lo, hi, x0, x1), ex = set === "ex" ? "valoarea" : "log10(SCI)";
    el.querySelectorAll(".ed-gl").forEach(g => g.style.display =
      (g.querySelector("input").dataset.n === "h" ? ["dens", "viol"].includes(fel) : fel === "hist") ? "" : "none");
    let s = "";
    if (fel === "hist"){
      const b = +ib.value, w = (hi - lo) / b, st = lo - w * +io.value, n = histograma(v, b + 1, st, st + w * (b + 1));
      const sy = sc(0, Math.max(...n) * 1.1, y1, y0);
      s += axe({ x0, x1, y0, y1, sx, sy, dx: [lo, hi], dy: [0, Math.max(...n) * 1.1], ex, ey: "câte valori" });
      n.forEach((c, i) => { const a = sx(Math.max(lo, st + i * w)), bb = sx(Math.min(hi, st + (i + 1) * w));
        if (bb > a) s += `<rect class="ed-bar" x="${a + .5}" y="${sy(c)}" width="${Math.max(0, bb - a - 1)}" height="${y1 - sy(c)}"/>`; });
      el.querySelector('label:has(input[data-n="b"]) output').textContent = b;
      el.querySelector('label:has(input[data-n="o"]) output').textContent = f(+io.value, 2);
    } else if (fel === "dens"){
      const k = kde(v, lo, hi, +ih.value), mx = Math.max(...k.map(p => p[1])), sy = sc(0, mx * 1.1, y1, y0);
      s += axe({ x0, x1, y0, y1, sx, sy, dx: [lo, hi], ex });
      s += `<path class="ed-arie" d="M${sx(lo)},${y1} ${k.map(p => `L${sx(p[0])},${sy(p[1])}`).join(" ")} L${sx(hi)},${y1}Z"/>`;
      v.forEach(u => s += `<line class="ed-rug" x1="${sx(u)}" x2="${sx(u)}" y1="${y1}" y2="${y1 - 7}"/>`);
      el.querySelector('label:has(input[data-n="h"]) output').textContent = f(+ih.value, 2);
    } else if (fel === "ecdf"){
      const o = sortat(v), sy = sc(0, 1, y1, y0);
      s += axe({ x0, x1, y0, y1, sx, sy, dx: [lo, hi], dy: [0, 1], ex, ey: "proporția valorilor ≤ x", fy: v => f(v, 1) });
      s += `<polyline class="ed-linie" points="${o.map((u, i) => `${sx(u)},${sy(i / o.length)} ${sx(u)},${sy((i + 1) / o.length)}`).join(" ")}"/>`;
      [.25, .5, .75].forEach(q => { const u = cuantila(o, q, true);
        s += `<line class="ed-l-obs" x1="${x0}" x2="${sx(u)}" y1="${sy(q)}" y2="${sy(q)}"/><line class="ed-l-obs" x1="${sx(u)}" x2="${sx(u)}" y1="${sy(q)}" y2="${y1}"/>`; });
    } else {
      const o = sortat(v), q1 = cuantila(o, .25, true), q2 = cuantila(o, .5, true), q3 = cuantila(o, .75, true), iq = q3 - q1;
      const lw = o.find(u => u >= q1 - 1.5 * iq), uw = [...o].reverse().find(u => u <= q3 + 1.5 * iq), yc = (y0 + y1) / 2;
      s += axe({ x0, x1, y0, y1, sx, sy: v => v, dx: [lo, hi], ex });
      if (fel === "viol"){
        const k = kde(v, lo, hi, +ih.value), mx = Math.max(...k.map(p => p[1])), hh = sc(0, mx, 0, (y1 - y0) / 2 - 6);
        s += `<path class="ed-arie" d="M${k.map(p => `${sx(p[0])},${yc - hh(p[1])}`).join(" L")} L${[...k].reverse().map(p => `${sx(p[0])},${yc + hh(p[1])}`).join(" L")}Z"/>`;
        const rr = rng(2); v.forEach(u => s += `<circle class="ed-p ed-mic" cx="${sx(u)}" cy="${yc + (rr() - .5) * 40}" r="2.2"/>`);
        el.querySelector('label:has(input[data-n="h"]) output').textContent = f(+ih.value, 2);
      } else {
        s += `<line class="ed-mus" x1="${sx(lw)}" x2="${sx(q1)}" y1="${yc}" y2="${yc}"/><line class="ed-mus" x1="${sx(q3)}" x2="${sx(uw)}" y1="${yc}" y2="${yc}"/>`
          + `<rect class="ed-cutie" x="${sx(q1)}" y="${yc - 34}" width="${sx(q3) - sx(q1)}" height="68"/><line class="ed-med" x1="${sx(q2)}" x2="${sx(q2)}" y1="${yc - 34}" y2="${yc + 34}"/>`;
        o.filter(u => u < lw || u > uw).forEach(u => s += `<circle class="ed-sus" cx="${sx(u)}" cy="${yc}" r="3"/>`);
      }
    }
    el.querySelector(".ed-g").innerHTML = svg(W, H, s);
  };
  leaga(el, "s", k => { set = k; deseneaza(); });
  leaga(el, "f", k => { fel = k; deseneaza(); });
  [ib, io, ih].forEach(i => i.addEventListener("input", deseneaza));
  deseneaza();
};


/* =========================================================================
   6. Reexprimarea: scara puterilor lui Tukey
   ========================================================================= */
E.edReexprimare = (gazda, d) => {
  const r = rng(4), z = normal(r);
  const EX = Array.from({ length: 300 }, () => Math.exp(8.2 + .75 * z()));
  const SCI = (d.sci || []).filter(x => x > 0);
  const PUT = [[1, "x"], [.5, "√x"], [0, "log x"], [-.5, "−1/√x"], [-1, "−1/x"]];
  let set = "ex";
  const el = bloc(gazda, `<div class="ed-ctl">${butoane("s", [["ex", "venituri simulate"], ["sci", "SCI"]], set)}${glisor("p", "puterea", 0, 4, 1, 0)}</div><div class="ed-g"></div><div class="ed-o"></div>`);
  const inp = el.querySelector("input"), out = el.querySelector("output");
  const W = 900, H = 215, x0 = 40, x1 = W - 16, y0 = 16, y1 = H - 40;
  const deseneaza = () => {
    const [p, et] = PUT[+inp.value]; out.textContent = et;
    const v = (set === "ex" ? EX : SCI).map(x => p === 0 ? Math.log10(x) : p > 0 ? x ** p : -(x ** p));
    const lo = Math.min(...v), hi = Math.max(...v), n = histograma(v, 32, lo, hi), sx = sc(lo, hi, x0, x1), sy = sc(0, Math.max(...n) * 1.1, y1, y0 + 30);
    let s = axe({ x0, x1, y0, y1, sx, sy, dx: [lo, hi], ex: et, fx: u => Math.abs(hi - lo) < 1 ? f(u, 3) : Math.abs(hi - lo) < 50 ? f(u, 1) : nr(u) });
    const w = (x1 - x0) / 32; n.forEach((c, i) => s += `<rect class="ed-bar" x="${x0 + i * w + .5}" y="${sy(c)}" width="${Math.max(0, w - 1)}" height="${y1 - sy(c)}"/>`);
    const o = sortat(v), q1 = cuantila(o, .25, true), q2 = cuantila(o, .5, true), q3 = cuantila(o, .75, true);
    s += `<rect class="ed-cutie" x="${sx(q1)}" y="${y0}" width="${sx(q3) - sx(q1)}" height="18"/><line class="ed-med" x1="${sx(q2)}" x2="${sx(q2)}" y1="${y0}" y2="${y0 + 18}"/>`
      + `<line class="ed-mus" x1="${sx(lo)}" x2="${sx(q1)}" y1="${y0 + 9}" y2="${y0 + 9}"/><line class="ed-mus" x1="${sx(q3)}" x2="${sx(hi)}" y1="${y0 + 9}" y2="${y0 + 9}"/>`;
    el.querySelector(".ed-g").innerHTML = svg(W, H, s);
    const a = asimetrie(v);
    el.querySelector(".ed-o").innerHTML = cifre([["transformarea", et], ["asimetria", f(a, 2), Math.abs(a) < .3 ? "ed-c-adev" : ""],
      ["media / mediana", f(medie(v) / mediana(v), 2)], ["", Math.abs(a) < .3 ? "aproape simetrică" : a > 0 ? "coadă spre dreapta" : "coadă spre stânga"]]);
  };
  leaga(el, "s", k => { set = k; deseneaza(); });
  inp.addEventListener("input", deseneaza);
  deseneaza();
};


/* =========================================================================
   7. Tabelul de contingență
   ========================================================================= */
E.edContingenta = (gazda, d) => {
  const SETURI = {
    ex: { r: ["urban", "rural"], c: ["fără liceu", "liceu", "superioare"], v: [[120, 300, 280], [260, 210, 70]], er: "localitatea", ec: "studiile" },
    sci: d.sci || null };
  let set = "ex", mod = "n", gr = "grup";
  const el = bloc(gazda, `<div class="ed-ctl">${d.sci ? butoane("s", [["ex", "exemplul"], ["sci", "SCI"]], set) : ""}${butoane("m", [["n", "numere"], ["r", "% pe rând"], ["c", "% pe coloană"]], mod)}${butoane("g", [["grup", "bare grupate"], ["stiv", "bare stivuite 100%"], ["moz", "mozaic"]], gr)}</div>
    <div class="ed-ct"><div class="ed-ct__t"></div><div class="ed-g"></div></div>`);
  const CUL = ["var(--sci-2)", "var(--sci-4)", "var(--sci-6)", "var(--ambra)"];
  const deseneaza = () => {
    const T = SETURI[set], R = T.v.map(x => x.reduce((a, b) => a + b, 0)), Cc = T.c.map((_, j) => T.v.reduce((a, x) => a + x[j], 0)), N = R.reduce((a, b) => a + b, 0);
    const val = (i, j) => mod === "n" ? T.v[i][j] : mod === "r" ? T.v[i][j] / R[i] : T.v[i][j] / Cc[j];
    const mx = Math.max(...T.v.flatMap((x, i) => x.map((_, j) => val(i, j))));
    el.querySelector(".ed-ct__t").innerHTML = `<table><thead><tr><th>${T.er} \\ ${T.ec}</th>${T.c.map(c => `<th>${c}</th>`).join("")}${mod === "r" ? "<th>total</th>" : ""}</tr></thead><tbody>`
      + T.r.map((rr, i) => `<tr><th>${rr}</th>${T.c.map((_, j) => { const u = val(i, j);
        return `<td style="--p:${(u / mx).toFixed(3)}">${mod === "n" ? nr(u) : f(100 * u, 0) + "%"}</td>`; }).join("")}${mod === "r" ? "<td>100%</td>" : ""}</tr>`).join("")
      + (mod === "c" ? `<tr><th>total</th>${T.c.map(() => "<td>100%</td>").join("")}</tr>` : "") + "</tbody></table>";
    const W = 400, H = 250, x0 = 60, x1 = W - 8, y0 = 10, y1 = H - 46; let s = "";
    if (gr === "grup"){
      const sy = sc(0, 1, y1, y0), bw = (x1 - x0) / T.r.length;
      T.r.forEach((rr, i) => { T.c.forEach((_, j) => { const p = T.v[i][j] / R[i], w = (bw - 16) / T.c.length;
        s += `<rect x="${x0 + i * bw + 8 + j * w}" y="${sy(p)}" width="${Math.max(0, w - 2)}" height="${y1 - sy(p)}" style="fill:${CUL[j]}"/>`; });
        s += `<text class="ed-tx${T.r.length > 3 ? " ed-tx--mic" : ""}" x="${x0 + i * bw + bw / 2}" y="${y1 + 16}" text-anchor="middle">${rr}</text>`; });
      s += `<text class="ed-tx" x="${x0 - 6}" y="${y0 + 8}" text-anchor="end">% pe rând</text><text class="ed-tx" x="${x0 - 6}" y="${y1}" text-anchor="end">0</text>`;
    } else {
      let xa = x0; T.r.forEach((rr, i) => { const w = gr === "moz" ? (x1 - x0) * R[i] / N : (x1 - x0) / T.r.length; let ya = y1;
        T.c.forEach((_, j) => { const h = (y1 - y0) * T.v[i][j] / R[i]; s += `<rect x="${xa + 1}" y="${ya - h}" width="${Math.max(0, w - 2)}" height="${h}" style="fill:${CUL[j]}"/>`; ya -= h; });
        s += `<text class="ed-tx${T.r.length > 3 ? " ed-tx--mic" : ""}" x="${xa + w / 2}" y="${y1 + 16}" text-anchor="middle">${w > 24 || T.r.length <= 3 ? rr : ""}</text>`; xa += w; });
    }
    s += T.c.map((c, j) => `<g transform="translate(${x0 + j * 110},${H - 6})"><rect y="-10" width="10" height="10" style="fill:${CUL[j]}"/><text class="ed-tx" x="14" y="-1">${c}</text></g>`).join("");
    el.querySelector(".ed-g").innerHTML = svg(W, H, s);
  };
  leaga(el, "s", k => { set = k; deseneaza(); });
  leaga(el, "m", k => { mod = k; deseneaza(); });
  leaga(el, "g", k => { gr = k; deseneaza(); });
  deseneaza();
};


/* =========================================================================
   8. Corelația: Pearson, Spearman, Kendall
   ========================================================================= */
E.edCorelatie = (gazda) => {
  const FORME = { lin: "liniară", mon: "curbă, dar monotonă", u: "în U", ext: "un punct extrem", zg: "fără relație" };
  const gen = k => { const r = rng(21), z = normal(r);
    return Array.from({ length: 40 }, (_, i) => { const x = r() * 10;
      if (k === "ext" && i === 0) return [9.8, 30];
      const y = k === "lin" ? 1 + .7 * x + 1.4 * z() : k === "mon" ? Math.exp(x / 2.2) / 6 + .3 * z()
        : k === "u" ? (x - 5) ** 2 / 3 + .8 * z() : k === "ext" ? 4 + .6 * z() : 4 + 1.6 * z();
      return [x, y]; }); };
  let forma = "lin", P = gen(forma), lo = 0, hi = 1, trag = -1;
  const el = bloc(gazda, `<div class="ed-ctl">${butoane("f", Object.entries(FORME), forma)}<span class="ed-not">punctele se pot trage cu mouse-ul</span></div><div class="ed-g"></div><div class="ed-o"></div>`);
  const W = 900, H = 220, x0 = 40, x1 = W - 16, y0 = 14, y1 = H - 30, sx = sc(0, 10, x0, x1);
  const cifreR = () => { const x = P.map(p => p[0]), y = P.map(p => p[1]);
    el.querySelector(".ed-o").innerHTML = cifre([["Pearson r", f(pearson(x, y)), "ed-c-m1"], ["Spearman ρ", f(spearman(x, y)), "ed-c-m2"], ["Kendall τ", f(kendall(x, y)), "ed-c-m3"]]); };
  const deseneaza = () => {
    const ys = P.map(p => p[1]); lo = Math.min(0, ...ys) - 1; hi = Math.max(...ys) + 1;
    const sy = sc(lo, hi, y1, y0);
    let s = axe({ x0, x1, y0, y1, sx, sy, dx: [0, 10], dy: [lo, hi] });
    const [a, b] = mcmmp(P.map(p => p[0]), ys);
    s += `<line class="ed-l-obs" x1="${sx(0)}" x2="${sx(10)}" y1="${sy(a)}" y2="${sy(a + 10 * b)}"/>`;
    P.forEach((p, i) => s += `<circle class="ed-p ed-trage" data-i="${i}" cx="${sx(p[0])}" cy="${sy(p[1])}" r="6"/>`);
    el.querySelector(".ed-g").innerHTML = svg(W, H, s);
    cifreR();
  };
  const g = el.querySelector(".ed-g");
  g.addEventListener("pointerdown", e => { const c = e.target.closest("circle.ed-trage"); if (!c) return; trag = +c.dataset.i; g.setPointerCapture(e.pointerId); e.preventDefault(); });
  g.addEventListener("pointermove", e => { if (trag < 0) return; const q = punct(g.querySelector("svg"), e);
    const X = Math.max(x0, Math.min(x1, q.x)), Y = Math.max(y0, Math.min(y1, q.y));
    P[trag] = [(X - x0) / (x1 - x0) * 10, lo + (y1 - Y) / (y1 - y0) * (hi - lo)];
    const c = g.querySelector(`circle[data-i="${trag}"]`); c.setAttribute("cx", X); c.setAttribute("cy", Y); cifreR(); });
  g.addEventListener("pointerup", () => { if (trag >= 0){ trag = -1; deseneaza(); } });
  leaga(el, "f", k => { forma = k; P = gen(k); deseneaza(); });
  deseneaza();
};


/* =========================================================================
   9. Aceleași statistici, alte grafice; prea multe puncte
   ========================================================================= */
const ANS = { x: [10, 8, 13, 9, 11, 14, 6, 4, 12, 7, 5], x4: [8, 8, 8, 8, 8, 8, 8, 19, 8, 8, 8],
  y: [[8.04, 6.95, 7.58, 8.81, 8.33, 9.96, 7.24, 4.26, 10.84, 4.82, 5.68], [9.14, 8.14, 8.74, 8.77, 9.26, 8.10, 6.13, 3.10, 9.13, 7.26, 4.74],
    [7.46, 6.77, 12.74, 7.11, 7.81, 8.84, 6.08, 5.39, 8.15, 6.42, 5.73], [6.58, 5.76, 7.71, 8.84, 8.47, 7.04, 5.25, 12.50, 5.56, 7.91, 6.89]] };
E.edAnscombe = (gazda) => {
  let fila = "ans", vedere = "pct";
  const el = bloc(gazda, `<div class="ed-ctl">${butoane("t", [["ans", "cvartetul lui Anscombe"], ["mult", "prea multe puncte"]], fila)}
    <span class="ed-mult">${glisor("n", "observații", 0, 3, 1, 0)}${butoane("v", [["pct", "puncte"], ["tr", "transparență"], ["2d", "histogramă 2D"], ["med", "mediane pe intervale"]], vedere)}</span></div><div class="ed-g"></div><div class="ed-o"></div>`);
  const inp = el.querySelector("input"), NS = [100, 2000, 10000, 50000];
  const r = rng(13), z = normal(r);
  const MARE = Array.from({ length: 50000 }, () => { const x = r() * 10; return [x, 6 - .45 * x + Math.abs(z()) * (.4 + .12 * x) * (r() < .1 ? 3 : 1)]; });
  const deseneaza = () => {
    el.querySelector(".ed-mult").style.display = fila === "mult" ? "" : "none";
    if (fila === "ans"){
      const W = 900, H = 230, w = 215; let s = "";
      ANS.y.forEach((y, k) => { const x = k === 3 ? ANS.x4 : ANS.x, X0 = k * (w + 10) + 26, X1 = X0 + w - 30, sx = sc(2, 20, X0, X1), sy = sc(2, 14, 200, 20);
        s += axe({ x0: X0, x1: X1, y0: 20, y1: 200, sx, sy, dx: [2, 20], dy: [2, 14], nx: 3, ny: 3 });
        const [a, b] = mcmmp(x, y); s += `<line class="ed-l-obs" x1="${sx(2)}" x2="${sx(20)}" y1="${sy(a + 2 * b)}" y2="${sy(a + 20 * b)}"/>`;
        x.forEach((u, i) => s += `<circle class="ed-p" cx="${sx(u)}" cy="${sy(y[i])}" r="4"/>`);
        s += `<text class="ed-tx ed-gros" x="${X0}" y="12">${["I", "II", "III", "IV"][k]}</text>`; });
      el.querySelector(".ed-g").innerHTML = svg(W, H, s);
      const y = ANS.y[0];
      el.querySelector(".ed-o").innerHTML = cifre([["media x", "9,0 în toate"], ["media y", "7,50 în toate"], ["varianța y", "4,12 în toate"],
        ["corelația", f(pearson(ANS.x, y)) + " în toate"], ["dreapta", "y = 3,00 + 0,50 x"]]);
      return;
    }
    const n = NS[+inp.value]; el.querySelector("output").textContent = nr(n);
    const D = MARE.slice(0, n), W = 900, H = 220, x0 = 40, x1 = W - 16, y0 = 12, y1 = H - 30, sx = sc(0, 10, x0, x1), sy = sc(0, 9, y1, y0);
    let s = axe({ x0, x1, y0, y1, sx, sy, dx: [0, 10], dy: [0, 9] });
    if (vedere === "2d"){
      const B = 40, M = 24, c = Array.from({ length: M }, () => new Array(B).fill(0));
      D.forEach(([x, y]) => { const i = Math.min(B - 1, Math.floor(x / 10 * B)), j = Math.min(M - 1, Math.max(0, Math.floor(y / 9 * M))); c[j][i]++; });
      const mx = Math.max(...c.flat()), w = (x1 - x0) / B, h = (y1 - y0) / M;
      c.forEach((rd, j) => rd.forEach((k, i) => { if (k) s += `<rect x="${x0 + i * w}" y="${y1 - (j + 1) * h}" width="${w}" height="${h}" style="fill:var(--accent);opacity:${(.12 + .88 * Math.sqrt(k / mx)).toFixed(2)}"/>`; }));
    } else if (vedere === "med"){
      const B = 10; let pts = [];
      for (let i = 0; i < B; i++){ const g = D.filter(p => p[0] >= i && p[0] < i + 1).map(p => p[1]); if (g.length)
        pts.push([i + .5, cuantila(g, .25), mediana(g), cuantila(g, .75)]); }
      pts.forEach(p => s += `<line class="ed-mus" x1="${sx(p[0])}" x2="${sx(p[0])}" y1="${sy(p[1])}" y2="${sy(p[3])}"/>`);
      s += `<polyline class="ed-linie" points="${pts.map(p => `${sx(p[0])},${sy(p[2])}`).join(" ")}"/>` + pts.map(p => `<circle class="ed-p" cx="${sx(p[0])}" cy="${sy(p[2])}" r="5"/>`).join("");
    }
    el.querySelector(".ed-g").innerHTML = svg(W, H, s) + (["pct", "tr"].includes(vedere) ? `<canvas class="ed-cv" width="${W * 2}" height="${H * 2}"></canvas>` : "");
    const cv = el.querySelector("canvas");
    if (cv){ const c = cv.getContext("2d"), col = getComputedStyle(el).getPropertyValue("--accent").trim() || "#1a7a66";
      c.scale(2, 2); c.fillStyle = col; c.globalAlpha = vedere === "tr" ? Math.max(.02, Math.min(.6, 60 / n)) : .9;
      D.forEach(([x, y]) => { c.beginPath(); c.arc(sx(x), sy(y), 2.4, 0, 6.3); c.fill(); }); }
    el.querySelector(".ed-o").innerHTML = cifre([["observații", nr(n)], ["", vedere === "pct" ? "punctele se acoperă: zona densă nu se vede"
      : vedere === "tr" ? "transparența arată densitatea, până la un punct" : vedere === "2d" ? "fiecare căsuță: câte observații cad în ea" : "mediana și quartilele pe intervale: forma relației și împrăștierea ei"]]);
  };
  leaga(el, "t", k => { fila = k; deseneaza(); });
  leaga(el, "v", k => { vedere = k; deseneaza(); });
  inp.addEventListener("input", deseneaza);
  deseneaza();
};


/* =========================================================================
   10. Lineup: graficul real ascuns între grafice permutate
   ========================================================================= */
E.edLineup = (gazda, d) => {
  const R = d.regiuni || [];
  const RUNDE = [
    { t: "exemplu: un tipar puternic", gen: s => { const r = rng(s), z = normal(r); return Array.from({ length: 50 }, () => { const x = z(); return [x, .5 * x + .85 * z()]; }); } },
    { t: "exemplu: un tipar slab", gen: s => { const r = rng(s), z = normal(r); return Array.from({ length: 50 }, () => { const x = z(); return [x, .12 * x + z()]; }); } },
    ...(R.length ? [
      { t: "SCI: deschiderea și longitudinea", sci: true, gen: () => R.map(q => [q[4], q[3]]), ex: "est →", ey: "deschiderea" },
      { t: "SCI: deschiderea și populația", sci: true, gen: () => R.map(q => [q[2], q[3]]), ex: "log populația", ey: "deschiderea" }] : [])];
  let k = 0, samanta = 1, real = 0, ales = -1;
  const el = bloc(gazda, `<div class="ed-ctl">${butoane("r", RUNDE.map((q, i) => [String(i), q.t]), "0")}<button class="ed-b">altă așezare</button></div><div class="ed-g ed-lu"></div><div class="ed-o"></div>`);
  const deseneaza = () => {
    let P = RUNDE[k].gen(samanta);
    if (RUNDE[k].sci){ const rx = ranguri(P.map(p => p[0])), ry = ranguri(P.map(p => p[1])); P = P.map((_, i) => [rx[i], ry[i]]); }   /* pe ranguri, ca punctele să nu se strângă */
    const y = P.map(p => p[1]), rr = rng(samanta * 7 + k);
    real = Math.floor(rr() * 8); ales = -1;
    const xs = P.map(p => p[0]), lo = Math.min(...xs), hi = Math.max(...xs), ylo = Math.min(...y), yhi = Math.max(...y);
    let html = "";
    for (let g = 0; g < 8; g++){
      let yy = y; if (g !== real){ yy = [...y]; for (let i = yy.length - 1; i > 0; i--){ const j = Math.floor(rr() * (i + 1)); [yy[i], yy[j]] = [yy[j], yy[i]]; } }
      const sx = sc(lo, hi, 8, 172), sy = sc(ylo, yhi, 112, 8);
      html += `<button class="ed-lu__p" data-g="${g}">${svg(180, 120, `<rect class="ed-cadru" x="1" y="1" width="178" height="118"/>`
        + xs.map((u, i) => `<circle class="ed-p ed-mic" cx="${sx(u)}" cy="${sy(yy[i])}" r="${RUNDE[k].sci ? 1.8 : 2.6}"/>`).join(""))}<i>${g + 1}</i></button>`;
    }
    el.querySelector(".ed-g").innerHTML = html;
    el.querySelector(".ed-o").innerHTML = `<p class="ed-not">Șapte grafice au valorile de pe axa verticală amestecate (permutate). Care este cel real?</p>`;
    el.querySelectorAll(".ed-lu__p").forEach(b => b.addEventListener("click", () => {
      if (ales >= 0) return; ales = +b.dataset.g;
      el.querySelectorAll(".ed-lu__p").forEach((x, i) => x.classList.add(i === real ? "real" : i === ales ? "gresit" : "stins"));
      const ok = ales === real, rho = spearman(xs, y);
      el.querySelector(".ed-o").innerHTML = cifre([["", ok ? "Corect: tiparul se deosebește de zgomot." : `Nu: cel real era ${real + 1}.`, ok ? "ed-c-adev" : "ed-c-sus"],
        ["ρ Spearman în graficul real", f(rho)], ["șansa de a ghici la întâmplare", "1 din 8"]]);
    }));
  };
  leaga(el, "r", v => { k = +v; samanta++; deseneaza(); });
  el.querySelector(".ed-b").addEventListener("click", () => { samanta++; deseneaza(); });
  deseneaza();
};


/* =========================================================================
   11. Categoric × numeric: ce ascunde bara cu media
   ========================================================================= */
E.edGrupuri = (gazda) => {
  const r = rng(17), z = normal(r);
  const G = [
    ["A: simetrică", Array.from({ length: 80 }, () => 50 + 8 * z())],
    ["B: două cocoașe", Array.from({ length: 80 }, () => r() < .5 ? 38 + 4 * z() : 62 + 4 * z())],
    ["C: asimetrică", Array.from({ length: 80 }, () => 38 + Math.exp(2.3 + .6 * z()))],
    ["D: 6 observații", Array.from({ length: 6 }, () => 50 + 14 * z())]];
  let v = "bare";
  const el = bloc(gazda, butoane("v", [["bare", "bare cu media"], ["box", "boxplot"], ["viol", "violin"], ["pct", "puncte"]], v) + `<div class="ed-g"></div>`);
  const W = 900, H = 220, x0 = 50, x1 = W - 10, y0 = 14, y1 = H - 34, sy = sc(0, 110, y1, y0), bw = (x1 - x0) / 4;
  const deseneaza = () => {
    let s = axe({ x0, x1, y0, y1, sx: x => x, sy, dy: [0, 110] });
    G.forEach(([et, a], i) => { const c = x0 + bw * i + bw / 2, rr = rng(i + 3);
      s += `<text class="ed-tx" x="${c}" y="${y1 + 18}" text-anchor="middle">${et}</text>`;
      if (v === "bare"){ const m = medie(a), e = abatere(a) / Math.sqrt(a.length);
        s += `<rect class="ed-bar" x="${c - 34}" y="${sy(m)}" width="68" height="${y1 - sy(m)}"/><line class="ed-mus" x1="${c}" x2="${c}" y1="${sy(m - 2 * e)}" y2="${sy(m + 2 * e)}"/>`; }
      else if (v === "pct") a.forEach(u => s += `<circle class="ed-p ed-mic" cx="${c + (rr() - .5) * 70}" cy="${sy(u)}" r="3"/>`);
      else if (v === "box"){ const o = sortat(a), q1 = cuantila(o, .25, true), q2 = cuantila(o, .5, true), q3 = cuantila(o, .75, true), iq = q3 - q1,
          lw = o.find(u => u >= q1 - 1.5 * iq), uw = [...o].reverse().find(u => u <= q3 + 1.5 * iq);
        s += `<line class="ed-mus" x1="${c}" x2="${c}" y1="${sy(lw)}" y2="${sy(uw)}"/><rect class="ed-cutie" x="${c - 34}" y="${sy(q3)}" width="68" height="${sy(q1) - sy(q3)}"/><line class="ed-med" x1="${c - 34}" x2="${c + 34}" y1="${sy(q2)}" y2="${sy(q2)}"/>`;
        o.filter(u => u < lw || u > uw).forEach(u => s += `<circle class="ed-sus" cx="${c}" cy="${sy(u)}" r="3"/>`); }
      else { const bwd = 5, pts = []; for (let y = 5; y <= 105; y += 2){ let t = 0; a.forEach(u => t += Math.exp(-.5 * ((y - u) / bwd) ** 2)); pts.push([y, t / a.length]); }
        const mx = Math.max(...pts.map(p => p[1])), hh = sc(0, mx, 0, 40);
        s += `<path class="ed-arie" d="M${pts.map(p => `${c - hh(p[1])},${sy(p[0])}`).join(" L")} L${[...pts].reverse().map(p => `${c + hh(p[1])},${sy(p[0])}`).join(" L")}Z"/>`; } });
    el.querySelector(".ed-g").innerHTML = svg(W, H, s);
  };
  leaga(el, "v", k => { v = k; deseneaza(); });
  deseneaza();
};


/* =========================================================================
   12. Paradoxul lui Simpson: admiterea la Berkeley, 1973
   ========================================================================= */
E.edSimpson = (gazda) => {
  const D = [["A", 825, 512, 108, 89], ["B", 560, 353, 25, 17], ["C", 325, 120, 593, 202], ["D", 417, 138, 375, 131], ["E", 191, 53, 393, 94], ["F", 373, 22, 341, 24]];
  let v = "tot";
  const el = bloc(gazda, butoane("v", [["tot", "toate departamentele"], ["dep", "pe departamente"], ["cer", "unde au candidat"]], v) + `<div class="ed-g"></div><div class="ed-o"></div>`);
  const W = 900, H = 220, x0 = 60, x1 = W - 20, y0 = 16, y1 = H - 34;
  const tb = D.reduce((a, d) => a + d[1], 0), ab = D.reduce((a, d) => a + d[2], 0), tf = D.reduce((a, d) => a + d[3], 0), af = D.reduce((a, d) => a + d[4], 0);
  const deseneaza = () => {
    let s = "";
    if (v === "tot"){
      const sy = sc(0, 1, y1, y0); s += axe({ x0, x1, y0, y1, sx: x => x, sy, dy: [0, 1], fy: u => f(100 * u, 0) + "%", ey: "admiși" });
      [["bărbați", ab / tb, "ed-bar"], ["femei", af / tf, "ed-bar2"]].forEach(([e, p, c], i) => { const x = x0 + 120 + i * 260;
        s += `<rect class="${c}" x="${x}" y="${sy(p)}" width="140" height="${y1 - sy(p)}"/><text class="ed-tx ed-gros" x="${x + 70}" y="${sy(p) - 6}" text-anchor="middle">${f(100 * p, 1)}%</text><text class="ed-tx" x="${x + 70}" y="${y1 + 18}" text-anchor="middle">${e}</text>`; });
    } else if (v === "dep"){
      const sx = sc(0, 5, x0 + 40, x1 - 40), sy = sc(0, 1, y1, y0), rz = n => 3 + Math.sqrt(n) / 3.2;
      s += axe({ x0, x1, y0, y1, sx: x => x, sy, dy: [0, 1], fy: u => f(100 * u, 0) + "%", ey: "admiși, pe departamente (cercul: câți au candidat)" });
      D.forEach(([dp, b, ba, fe, fa], i) => { const x = sx(i);
        s += `<line class="ed-mus" x1="${x}" x2="${x}" y1="${sy(ba / b)}" y2="${sy(fa / fe)}"/><circle class="ed-pb" cx="${x - 6}" cy="${sy(ba / b)}" r="${rz(b)}"/><circle class="ed-pf" cx="${x + 6}" cy="${sy(fa / fe)}" r="${rz(fe)}"/><text class="ed-tx" x="${x}" y="${y1 + 18}" text-anchor="middle">${dp}</text>`; });
    } else {
      const sx = sc(0, 1, x0, x1); s += `<text class="ed-tx" x="${x0}" y="${y0 + 4}">din toți candidații fiecărui gen, unde au candidat (departamentele, de la cel mai ușor la cel mai greu)</text>`;
      [["bărbați", 1, tb], ["femei", 3, tf]].forEach(([e, k, t], j) => { let xa = x0; const y = y0 + 30 + j * 80;
        s += `<text class="ed-tx" x="${x0 - 8}" y="${y + 30}" text-anchor="end">${e}</text>`;
        D.forEach((d, i) => { const w = (x1 - x0) * d[k] / t; s += `<rect x="${xa}" y="${y}" width="${Math.max(0, w - 1)}" height="50" style="fill:var(--sci-${i + 1})"/>`
          + (w > 26 ? `<text class="ed-tx ed-alb" x="${xa + w / 2}" y="${y + 30}" text-anchor="middle">${d[0]}</text>` : ""); xa += w; }); });
    }
    el.querySelector(".ed-g").innerHTML = svg(W, H, s);
    el.querySelector(".ed-o").innerHTML = cifre(v === "tot" ? [["bărbați", `${nr(ab)} din ${nr(tb)} admiși`], ["femei", `${nr(af)} din ${nr(tf)}`], ["", "pe total, femeile par dezavantajate"]]
      : v === "dep" ? [["", "în patru din șase departamente, femeile au rata mai mare", "ed-c-adev"], ["bărbați", "cercurile pline"], ["femei", "cercurile cu contur"]]
      : [["", "femeile au candidat mai ales la C-F, unde admiterea e grea; departamentul este variabila de confuzie"]]);
  };
  leaga(el, "v", k => { v = k; deseneaza(); });
  deseneaza();
};


/* =========================================================================
   13. Nivelul de analiză: între grupuri, în interiorul lor, total
   ========================================================================= */
E.edNivele = (gazda, d) => {
  const R = d.regiuni || [];
  let set = "ex", arata = { tot: true, intre: false, in: false }, sep = 1;
  const el = bloc(gazda, `<div class="ed-ctl">${R.length ? butoane("s", [["ex", "exemplul"], ["sci", "SCI: regiunile"]], set) : ""}
    <div class="ed-bt ed-multi">${[["tot", "total"], ["intre", "între grupuri"], ["in", "în interiorul grupurilor"]].map(([k, t]) => `<button data-k="${k}" class="${arata[k] ? "on" : ""}">${t}</button>`).join("")}</div>
    <span class="ed-sep">${glisor("sep", "distanța dintre grupuri", 0, 2, .1, 1)}</span></div><div class="ed-g"></div><div class="ed-o"></div>`);
  const CUL = i => `var(--cat-${i % 8 + 1})`;
  const date = () => {
    if (set === "sci"){ const T = {}; R.forEach(q => (T[q[1]] ||= []).push(q)); const mari = Object.entries(T).sort((a, b) => b[1].length - a[1].length).map(e => e[0]);
      return R.map(q => ({ x: q[2], y: q[3], g: mari.indexOf(q[1]), t: q[1] })); }
    const r = rng(8), z = normal(r);
    return Array.from({ length: 6 }, (_, g) => Array.from({ length: 25 }, () => { const u = z();
      return { x: g * 1.2 * sep + u, y: -g * 1.0 * sep + .8 * u + .5 * z(), g, t: "G" + (g + 1) }; })).flat(); };
  const W = 900, H = 230, x0 = 46, x1 = W - 16, y0 = 14, y1 = H - 34;
  const deseneaza = () => {
    el.querySelector(".ed-sep").style.display = set === "ex" ? "" : "none";
    const P = date(), xs = P.map(p => p.x), ys = P.map(p => p.y);
    const lo = Math.min(...xs), hi = Math.max(...xs), ylo = Math.min(...ys), yhi = Math.max(...ys), sx = sc(lo, hi, x0, x1), sy = sc(ylo, yhi, y1, y0);
    let s = axe({ x0, x1, y0, y1, sx, sy, dx: [lo, hi], dy: [ylo, yhi], fx: u => f(u, set === "sci" ? 1 : 0), fy: u => f(u, 1),
      ex: set === "sci" ? "log10(populația regiunii)" : "x", ey: set === "sci" ? "log10(deschiderea spre străinătate)" : "y" });
    const vizibil = g => g < 8;                                       /* pe SCI, doar cele 8 țări mari colorate */
    P.forEach(p => s += `<circle class="ed-mic" cx="${sx(p.x)}" cy="${sy(p.y)}" r="${set === "sci" ? 3 : 4}" style="fill:${vizibil(p.g) ? CUL(p.g) : "var(--text-3)"};opacity:${vizibil(p.g) ? .8 : .3}"/>`);
    const grupe = {}; P.forEach(p => (grupe[p.g] ||= []).push(p));
    const dreapta = (a, c, w) => { const [i, b] = mcmmp(a.map(p => p.x), a.map(p => p.y)), l = Math.min(...a.map(p => p.x)), h = Math.max(...a.map(p => p.x));
      return `<line class="${c}" x1="${sx(l)}" x2="${sx(h)}" y1="${sy(i + b * l)}" y2="${sy(i + b * h)}" ${w || ""}/>`; };
    if (arata.tot) s += dreapta(P, "ed-l-tot");
    if (arata.in) Object.entries(grupe).forEach(([g, a]) => { if (vizibil(+g) && a.length >= 5) s += dreapta(a, "ed-l-in", `style="stroke:${CUL(+g)}"`); });
    const centru = a => ({ x: mediana(a.map(p => p.x)), y: mediana(a.map(p => p.y)) });
    if (arata.intre){ const C = Object.values(grupe).map(centru);
      C.forEach(c => s += `<rect class="ed-centru" x="${sx(c.x) - 6}" y="${sy(c.y) - 6}" width="12" height="12"/>`); s += dreapta(C, "ed-l-intre"); }
    el.querySelector(".ed-g").innerHTML = svg(W, H, s);
    const tot = spearman(xs, ys), med = Object.values(grupe).map(centru),
      intre = spearman(med.map(c => c.x), med.map(c => c.y)), inn = mediana(Object.values(grupe).filter(a => a.length >= 5).map(a => spearman(a.map(p => p.x), a.map(p => p.y))));
    el.querySelector(".ed-o").innerHTML = cifre([["ρ total", f(tot), "ed-c-m1"], ["ρ între grupuri", f(intre), "ed-c-m2"], ["ρ în interiorul grupurilor (mediana)", f(inn), "ed-c-m3"],
      ...(set === "sci" ? [["", "toate țările în calcul; cele 8 cu cele mai multe regiuni, colorate"]] : [])]);
  };
  leaga(el, "s", k => { set = k; deseneaza(); });
  el.querySelectorAll(".ed-multi button").forEach(b => b.addEventListener("click", () => { arata[b.dataset.k] = !arata[b.dataset.k]; b.classList.toggle("on", arata[b.dataset.k]); deseneaza(); }));
  const i = el.querySelector("input"); i.addEventListener("input", () => { sep = +i.value; el.querySelector("output").textContent = f(sep, 1); deseneaza(); });
  el.querySelector("output").textContent = "1,0";
  deseneaza();
};


/* =========================================================================
   14. Multe variabile: matricea de grafice și matricea de corelație
   ========================================================================= */
E.edMultivar = (gazda, d) => {
  const r = rng(31), z = normal(r), V = ["venit", "studii", "vârsta", "copii"];
  const P = Array.from({ length: 150 }, () => { const g = Math.floor(r() * 3), st = 10 + 3 * z() + 2 * g, v = 1500 + 260 * st + 600 * z(),
    a = 45 + 12 * z(), c = Math.max(0, 3.2 - .08 * st + .02 * (a - 45) + .9 * z()); return [v, st, a, c, g]; });
  let set = "ex", cul = false, sel = [0, 1];
  const el = bloc(gazda, `<div class="ed-ctl">${d.cor ? butoane("s", [["ex", "exemplul"], ["sci", "SCI: indicatorii regiunilor"]], set) : ""}<button class="ed-b ed-cul">culoare după grup</button><span class="ed-not">clic pe o căsuță</span></div><div class="ed-mv"><div class="ed-g"></div><div class="ed-h"></div></div>`);
  const deseneaza = () => {
    const sci = set === "sci", nume = sci ? d.cor.var.map(v => ({ pib_locuitor: "PIB/loc.", studii_superioare: "studii", somaj: "șomaj", varsta_medie: "vârsta", densitate: "densitate", retele_sociale: "rețele" }[v] || v)) : V;
    const M = sci ? d.cor.v : V.map((_, i) => V.map((_, j) => spearman(P.map(p => p[i]), P.map(p => p[j]))));
    el.querySelector(".ed-cul").style.display = sci ? "none" : "";
    /* matricea de grafice, doar pe exemplu (pe SCI avem doar coeficienții) */
    if (!sci){
      const k = 4, w = 92, s0 = 30; let s = "";
      for (let i = 0; i < k; i++) for (let j = 0; j < k; j++){
        const X0 = s0 + j * w, Y0 = i * w, xs = P.map(p => p[j]), ys = P.map(p => p[i]), sx = sc(Math.min(...xs), Math.max(...xs), X0 + 4, X0 + w - 6), sy = sc(Math.min(...ys), Math.max(...ys), Y0 + w - 6, Y0 + 4);
        const on = (sel[0] === i && sel[1] === j) || (sel[0] === j && sel[1] === i);
        s += `<rect class="ed-cadru ${on ? "on" : ""}" data-i="${i}" data-j="${j}" x="${X0}" y="${Y0}" width="${Math.max(0, w - 2)}" height="${w - 2}"/>`;
        if (i === j){ const n = histograma(xs, 10, Math.min(...xs), Math.max(...xs) + 1e-9), m = Math.max(...n);
          n.forEach((c, b) => s += `<rect class="ed-bar" x="${X0 + 4 + b * 8.2}" y="${Y0 + w - 6 - c / m * 70}" width="7" height="${c / m * 70}"/>`); }
        else P.forEach(p => s += `<circle cx="${sx(p[j])}" cy="${sy(p[i])}" r="1.6" style="fill:${cul ? `var(--cat-${p[4] + 1})` : "var(--accent)"};opacity:.6;pointer-events:none"/>`);
      }
      V.forEach((v, i) => s += `<text class="ed-tx" x="${s0 - 4}" y="${i * w + w / 2}" text-anchor="end">${v}</text>`);
      el.querySelector(".ed-g").innerHTML = svg(30 + 4 * 92, 4 * 92 + 4, s, "ed-pp");
    } else el.querySelector(".ed-g").innerHTML = "";
    const n = nume.length, w = sci ? 56 : 62;
    let h = `<div class="ed-hm" style="--n:${n};--w:${w}px"><span></span>${nume.map(v => `<b>${v}</b>`).join("")}`;
    M.forEach((rd, i) => { h += `<b class="ed-hm__r">${nume[i]}</b>` + rd.map((v, j) => { const on = (sel[0] === i && sel[1] === j) || (sel[0] === j && sel[1] === i);
      return `<i data-i="${i}" data-j="${j}" class="${on ? "on" : ""}" style="background:${v >= 0 ? `color-mix(in srgb,var(--hsd-7) ${Math.abs(v) * 90}%,var(--panza))` : `color-mix(in srgb,var(--hsd-1) ${Math.abs(v) * 90}%,var(--panza))`}">${i === j ? "" : f(v, 1)}</i>`; }).join(""); });
    el.querySelector(".ed-h").innerHTML = h + "</div>";
    el.querySelectorAll("[data-i]").forEach(c => c.addEventListener("click", () => { sel = [+c.dataset.i, +c.dataset.j]; deseneaza(); }));
  };
  leaga(el, "s", k => { set = k; sel = [0, 1]; deseneaza(); });
  el.querySelector(".ed-cul").addEventListener("click", e => { cul = !cul; e.target.classList.toggle("on", cul); deseneaza(); });
  deseneaza();
};


/* =========================================================================
   15. Tipar și reziduu
   ========================================================================= */
E.edReziduu = (gazda, d) => {
  const r = rng(12), z = normal(r);
  const EX = Array.from({ length: 70 }, () => { const x = r() * 10, g = r() < .3 ? 1 : 0; return [x, 2 + .7 * x + .09 * (x - 5) ** 2 + 1.8 * g + .5 * z(), g]; });
  const SCI = (d.perechi || []).map(p => [p[0], p[1], p[2]]);
  let set = "ex", a = 2, b = .8;
  const el = bloc(gazda, `<div class="ed-ctl">${SCI.length ? butoane("s", [["ex", "exemplul"], ["sci", "SCI: distanța"]], set) : ""}${glisor("b", "panta", -2, 2, .02, .8)}${glisor("a", "nivelul", -2, 8, .05, 2)}<button class="ed-b">cele mai mici pătrate</button></div><div class="ed-g"></div><div class="ed-o"></div>`);
  const [ib, ia] = ["b", "a"].map(n => el.querySelector(`input[data-n="${n}"]`));
  const W = 900, x0 = 50, x1 = W - 16;
  const deseneaza = () => {
    const P = set === "ex" ? EX : SCI, xs = P.map(p => p[0]), ys = P.map(p => p[1]);
    const lo = Math.min(...xs), hi = Math.max(...xs), ylo = Math.min(...ys), yhi = Math.max(...ys), sx = sc(lo, hi, x0, x1), sy = sc(ylo, yhi, 168, 14);
    const res = P.map(p => p[1] - (a + b * p[0])), rm = Math.max(...res.map(Math.abs)) || 1, sr = sc(-rm, rm, 290, 206);
    const ex = set === "ex" ? "x" : "log10(distanța, km)", ey = set === "ex" ? "y" : "log10(SCI)";
    let s = axe({ x0, x1, y0: 14, y1: 168, sx, sy, dx: [lo, hi], dy: [ylo, yhi], fx: u => f(u, 1), fy: u => f(u, 1), ey });
    P.forEach(p => s += `<circle class="${p[2] ? "ed-sus" : "ed-p"} ed-mic" cx="${sx(p[0])}" cy="${sy(p[1])}" r="${set === "ex" ? 4 : 2}"/>`);
    s += `<line class="ed-l-tot" x1="${sx(lo)}" x2="${sx(hi)}" y1="${sy(a + b * lo)}" y2="${sy(a + b * hi)}"/>`;
    s += axe({ x0, x1, y0: 206, y1: 290, sx, sy: sr, dx: [lo, hi], dy: [-rm, rm], ny: 2, fx: u => f(u, 1), fy: u => f(u, 1), ex, ey: "reziduul = y − dreapta" });
    s += `<line class="ed-l-adev" x1="${x0}" x2="${x1}" y1="${sr(0)}" y2="${sr(0)}"/>`;
    P.forEach((p, i) => s += `<circle class="${p[2] ? "ed-sus" : "ed-p"} ed-mic" cx="${sx(p[0])}" cy="${sr(res[i])}" r="${set === "ex" ? 3.5 : 1.8}"/>`);
    el.querySelector(".ed-g").innerHTML = svg(W, 330, s);
    const ssr = res.reduce((t, e) => t + e * e, 0), r0 = res.filter((_, i) => !P[i][2]), r1 = res.filter((_, i) => P[i][2]);
    el.querySelector(".ed-o").innerHTML = cifre([["suma pătratelor reziduurilor", f(ssr, 1)],
      [set === "ex" ? "reziduul median, grupul obișnuit" : "reziduul median, țări diferite", f(mediana(r0), 2)],
      [set === "ex" ? "reziduul median, grupul marcat" : "reziduul median, aceeași țară", f(r1.length ? mediana(r1) : 0, 2), "ed-c-sus"]]);
    ib.nextElementSibling.textContent = f(b, 2); ia.nextElementSibling.textContent = f(a, 2);
  };
  const potriveste = () => { const P = set === "ex" ? EX : SCI; [a, b] = mcmmp(P.map(p => p[0]), P.map(p => p[1])); ib.value = b; ia.value = a; deseneaza(); };
  leaga(el, "s", k => { set = k; if (k === "sci"){ ib.min = -3; ib.max = 1; ia.min = 0; ia.max = 10; } else { ib.min = -2; ib.max = 2; ia.min = -2; ia.max = 8; }
    potriveste(); });
  ib.addEventListener("input", () => { b = +ib.value; deseneaza(); });
  ia.addEventListener("input", () => { a = +ia.value; deseneaza(); });
  el.querySelector(".ed-b").addEventListener("click", potriveste);
  deseneaza();
};


/* =========================================================================
   16. Grădina potecilor: cea mai mare corelație în zgomot
   ========================================================================= */
E.edPoteci = (gazda) => {
  let samanta = 1;
  const el = bloc(gazda, `<div class="ed-ctl">${glisor("k", "variabile cercetate", 2, 40, 1, 10)}<button class="ed-b">alt eșantion de zgomot</button></div><div class="ed-po"><div class="ed-g"></div><div class="ed-g2"></div></div><div class="ed-o"></div>`);
  const inp = el.querySelector("input");
  const deseneaza = () => {
    const k = +inp.value, n = 30, r = rng(samanta), z = normal(r);
    el.querySelector("output").textContent = k;
    const X = Array.from({ length: k }, () => Array.from({ length: n }, z));
    let max = 0, pi = 0, pj = 1; const toate = [];
    for (let i = 0; i < k; i++) for (let j = i + 1; j < k; j++){ const c = pearson(X[i], X[j]); toate.push(c); if (Math.abs(c) > Math.abs(max)){ max = c; pi = i; pj = j; } }
    const W = 380, H = 230, x0 = 30, x1 = W - 10, y0 = 14, y1 = H - 34, sx = sc(-.8, .8, x0, x1), nb = histograma(toate, 32, -.8, .8), sy = sc(0, Math.max(...nb) * 1.1, y1, y0);
    let s = axe({ x0, x1, y0, y1, sx, sy, dx: [-.8, .8], fx: u => f(u, 1), ex: `r, în cele ${nr(toate.length)} perechi` });
    const w = (x1 - x0) / 32; nb.forEach((c, i) => s += `<rect class="${Math.abs(-.8 + (i + .5) * .05) > .36 ? "ed-bar2" : "ed-bar"}" x="${x0 + i * w + .5}" y="${sy(c)}" width="${Math.max(0, w - 1)}" height="${y1 - sy(c)}"/>`);
    el.querySelector(".ed-g").innerHTML = svg(W, H, s);
    const a = X[pi], b = X[pj], sx2 = sc(-3, 3, 30, 370), sy2 = sc(-3, 3, 196, 14);
    let t = axe({ x0: 30, x1: 370, y0: 14, y1: 196, sx: sx2, sy: sy2, dx: [-3, 3], dy: [-3, 3], ex: `variabila ${pi + 1} și variabila ${pj + 1}` });
    const [c0, c1] = mcmmp(a, b); t += `<line class="ed-l-obs" x1="${sx2(-3)}" x2="${sx2(3)}" y1="${sy2(c0 - 3 * c1)}" y2="${sy2(c0 + 3 * c1)}"/>`;
    a.forEach((u, i) => t += `<circle class="ed-p" cx="${sx2(u)}" cy="${sy2(b[i])}" r="4"/>`);
    el.querySelector(".ed-g2").innerHTML = svg(380, 230, t);
    const peste = toate.filter(c => Math.abs(c) > .36).length;
    el.querySelector(".ed-o").innerHTML = cifre([["perechi încercate", nr(toate.length)], ["cea mai mare |r|", f(Math.abs(max)), "ed-c-sus"],
      ["perechi „semnificative” (|r| > 0,36, p < 0,05)", `${peste}, deși totul e zgomot`]]);
  };
  inp.addEventListener("input", deseneaza);
  el.querySelector(".ed-b").addEventListener("click", () => { samanta++; deseneaza(); });
  deseneaza();
};


/* =========================================================================
   17. Tipurile de grafice (după Wilke)
   ========================================================================= */
E.edTipGrafice = (gazda) => {
  const T = {
    cant: ["Cantități", "o valoare pe categorie", [["bare", "barplot, countplot"], ["puncte (dot plot)", "pointplot"], ["heatmap", "heatmap"]]],
    dist: ["Distribuții", "cum se repartizează o variabilă numerică", [["histogramă", "histplot"], ["densitate", "kdeplot"], ["ECDF", "ecdfplot"], ["boxplot", "boxplot"], ["violin", "violinplot"], ["puncte cu zgomot", "stripplot"]]],
    prop: ["Proporții", "părți dintr-un întreg", [["bare stivuite 100%", "crosstab(normalize=)"], ["bare alăturate", "barplot(hue=)"], ["mozaic", "statsmodels mosaic"], ["plăcintă (doar 2-3 părți)", "plt.pie"]]],
    rel: ["Relații x-y", "două sau mai multe variabile numerice", [["dispersie (scatter)", "scatterplot"], ["histogramă 2D, hexbin", "histplot(x=, y=)"], ["tendință netezită", "regplot(lowess=True)"], ["matricea de grafice", "pairplot"], ["matricea de corelație", "heatmap(df.corr())"], ["linie în timp", "lineplot"]]],
    geo: ["Date spațiale", "valori pe teritorii", [["hartă coropletă", "geopandas plot(column=)"], ["simboluri proporționale", "plot(markersize=)"], ["cartogramă", "pachete dedicate"]]],
    inc: ["Incertitudine", "cât de sigură e o estimare", [["bare de eroare", "pointplot(errorbar=)"], ["benzi de încredere", "lineplot(errorbar=)"], ["eșantioane bootstrap", "errorbar=('ci', 95)"]]] };
  let k = "dist";
  const el = bloc(gazda, butoane("t", Object.entries(T).map(([c, v]) => [c, v[0]]), k) + `<div class="ed-tg"></div>`);
  const deseneaza = () => { const [n, d, L] = T[k];
    el.querySelector(".ed-tg").innerHTML = `<p class="ed-not">${n}: ${d}</p><div class="ed-tg__l">${L.map(([g, c]) => `<div><b>${g}</b><code>${c}</code></div>`).join("")}</div>`; };
  leaga(el, "t", v => { k = v; deseneaza(); });
  deseneaza();
};

export default E;
