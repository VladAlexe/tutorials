/* ===========================================================================
   Analiza exploratorie: componentele interactive ale lecției 6.

   Fiecare componentă predă un concept prin manipulare directă (glisoare,
   puncte trase, simulări, exerciții cu răspuns), numai pe datele cursului:
   perechile de regiuni cu SCI și tabelul regiunilor, primite din pagină.
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



/* --- datele SCI, primite din pagină -------------------------------------- */
const REG = d => (d.regiuni || []).map(r => { const o = { cod: r[0], tara: r[1], nume: r[2] };
  (d.var_reg || []).forEach((v, i) => o[v] = r[3 + i]); return o; });
const ET = { populatie: "populația", pib_locuitor: "PIB pe locuitor", studii_superioare: "studii superioare (%)", somaj: "șomaj (%)",
  varsta_medie: "vârsta medie", densitate: "densitatea (loc./km²)", deschidere: "deschiderea spre străinătate", est: "est (km)" };
const panou = t => `<p class="ed-not">${t}</p>`;
/* codul Python care produce vederea curentă, sub grafic */
const scrieCod = (el, t) => { const p = el.querySelector(".ed-cod"); if (p) p.textContent = t; };
const COL6 = `cols = ["populatie", "pib_locuitor", "studii_superioare", "somaj", "varsta_medie", "densitate"]`;
/* poziția pointerului în coordonatele SVG ale primului <svg> din element */
const laPointer = (el, cb) => { const s = el.querySelector("svg.ed-svg"); if (!s) return;
  s.addEventListener("pointermove", e => cb(punct(s, e), e)); s.addEventListener("pointerleave", () => cb(null)); };


/* =========================================================================
   1. Unitatea de analiză și tipurile coloanelor din tabelul perechilor
   ========================================================================= */
E.edTipuri = (gazda, d) => {
  const R = d.tip || [], pr = d.same / d.n;
  const C = [
    { n: "regiune_1", v: R.map(r => r.r1), t: "identificator", op: "nu se rezumă; leagă tabelul perechilor de tabelul regiunilor" },
    { n: "tara_1", v: R.map(r => r.t1), t: "categorică nominală", op: "frecvențe" },
    { n: "distanta_km", v: R.map(r => nr(r.d)), t: "numerică", op: "medie, mediană, histogramă" },
    { n: "interval_km", v: R.map(r => r.i), t: "categorică ordinală (intervale construite din distanță)", op: "frecvențe, în ordinea intervalelor" },
    { n: "aceeasi_tara", v: R.map(r => r.same ? "True" : "False"), t: "binară (adevărat / fals)", op: `proporția: ${f(100 * pr, 1)}% din cele ${nr(d.n)} de perechi` },
    { n: "sci", v: R.map(r => nr(r.sci)), t: "numerică, cu valori de la 1 la peste 4 milioane", op: "mediana; histograma pe scară logaritmică" },
  ];
  let k = 5;
  const el = bloc(gazda, `<div class="ed-tip"><table><thead><tr>${C.map((c, i) => `<th><button data-i="${i}">${c.n}</button></th>`).join("")}</tr></thead>
    <tbody>${R.map((_, r) => `<tr>${C.map(c => `<td>${c.v[r]}</td>`).join("")}</tr>`).join("")}</tbody></table>
    <div class="ed-tip__p"></div></div>`);
  const arata = () => {
    el.querySelectorAll("th button").forEach((b, i) => b.classList.toggle("on", i === k));
    el.querySelectorAll("tr").forEach(tr => [...tr.children].forEach((td, i) => td.classList.toggle("ales", i === k)));
    const c = C[k];
    el.querySelector(".ed-tip__p").innerHTML = `<b>${c.n}</b><span><i>tipul</i>${c.t}</span><span><i>se rezumă cu</i>${c.op}</span>`;
  };
  el.querySelectorAll("th button").forEach(b => b.addEventListener("click", () => { k = +b.dataset.i; arata(); }));
  arata();
};


/* =========================================================================
   2. Lipsurile: harta lipsurilor și simularea celor trei mecanisme
   ========================================================================= */
E.edLipsuri = (gazda, d) => {
  const R = REG(d), V = ["populatie", "pib_locuitor", "studii_superioare", "somaj", "varsta_medie", "densitate"];
  let mod = "harta", ord = "tara", ales = "pib_locuitor", mec = "mcar";
  const el = bloc(gazda, `<div class="ed-ctl">${butoane("m", [["harta", "harta lipsurilor"], ["sim", "simularea mecanismelor"]], mod)}
    <span class="ed-h1">${butoane("o", [["tara", "ordonate după țară"], ["rand", "în ordine întâmplătoare"]], ord)}</span>
    <span class="ed-h2">${butoane("k", [["mcar", "complet aleator"], ["mar", "după țară"], ["mnar", "după valoarea însăși"]], mec)}${glisor("p", "proporția lipsă", 0, .6, .05, .3)}</span></div><div class="ed-g"></div><pre class="ed-cod"></pre><div class="ed-o"></div>`);
  const ip = el.querySelector('input[data-n="p"]');
  const W = 900;
  const harta = () => {
    const x0 = 150, x1 = W - 10, rh = 20, H = V.length * rh + 34;
    let L = [...R];
    if (ord === "tara") L.sort((a, b) => a.tara.localeCompare(b.tara) || a.cod.localeCompare(b.cod));
    else { const r = rng(4); L = L.map(x => [r(), x]).sort((a, b) => a[0] - b[0]).map(x => x[1]); }
    const w = (x1 - x0) / L.length; let s = "";
    V.forEach((v, j) => { const y = 6 + j * rh;
      s += `<text class="ed-tx ed-lv${v === ales ? " on" : ""}" data-v="${v}" x="${x0 - 8}" y="${y + 13}" text-anchor="end">${ET[v]}</text>`;
      L.forEach((r, i) => s += `<rect x="${x0 + i * w}" y="${y}" width="${w + .3}" height="${rh - 4}" class="${r[v] == null ? "ed-gol" : "ed-plin"}"/>`); });
    if (ord === "tara"){ let i0 = 0;
      L.forEach((r, i) => { if (i === L.length - 1 || L[i + 1].tara !== r.tara){ const n = i - i0 + 1;
        if (n >= 8) s += `<text class="ed-tx ed-tx--mic" x="${x0 + (i0 + n / 2) * w}" y="${6 + V.length * rh + 12}" text-anchor="middle">${r.tara}</text>`;
        s += `<line class="ed-sep" x1="${x0 + (i + 1) * w}" x2="${x0 + (i + 1) * w}" y1="4" y2="${4 + V.length * rh}"/>`; i0 = i + 1; } }); }
    el.querySelector(".ed-g").innerHTML = svg(W, H, s);
    scrieCod(el, `${COL6}\nregiuni[cols].isna().sum()                          # câte lipsesc, pe coloane\nsns.heatmap(regiuni.sort_values("tara")[cols].isna().T, cbar=False)   # harta lipsurilor`);
    el.querySelectorAll(".ed-lv").forEach(t => t.addEventListener("click", () => { ales = t.dataset.v; harta(); }));
    const lipsa = R.filter(r => r[ales] == null), pe = {};
    lipsa.forEach(r => pe[r.tara] = (pe[r.tara] || 0) + 1);
    const tari = Object.entries(pe).sort((a, b) => b[1] - a[1]);
    const intregi = tari.filter(([t, n]) => n === R.filter(r => r.tara === t).length).map(e => e[0]);
    const v2 = ales === "varsta_medie" ? "pib_locuitor" : "varsta_medie";
    const toate = R.filter(r => r[v2] != null).map(r => r[v2]), complete = R.filter(r => r[v2] != null && r[ales] != null).map(r => r[v2]);
    el.querySelector(".ed-o").innerHTML = cifre([[ET[ales], `${lipsa.length} din ${R.length} lipsă`, "ed-c-sus"],
      ["țări întregi lipsă", intregi.join(", ") || "niciuna"],
      [`mediana ${ET[v2]}: toate regiunile / doar cele cu ${ET[ales]}`, `${fmt(mediana(toate))} / ${fmt(mediana(complete))}`]])
      + panou("Clic pe numele unei variabile. Ultima cifră arată cum se schimbă eșantionul când se păstrează doar cazurile complete.");
  };
  const fmt = v => v > 1000 ? nr(v) : f(v, 1);
  const sim = () => {
    const P = R.filter(r => r.pib_locuitor != null), p = +ip.value, rr = rng(9), n = P.length, m = Math.round(p * n);
    ip.nextElementSibling.textContent = `${Math.round(p * 100)}%`;
    let lipsa = new Set();
    if (mec === "mcar"){ P.map(r => [rr(), r]).sort((a, b) => a[0] - b[0]).slice(0, m).forEach(x => lipsa.add(x[1])); }
    else if (mec === "mar"){ const T = [...new Set(P.map(r => r.tara))].map(t => [rr(), t]).sort((a, b) => a[0] - b[0]).map(x => x[1]);
      for (const t of T){ if (lipsa.size >= m) break; P.filter(r => r.tara === t).forEach(r => lipsa.add(r)); } }
    else { P.map(r => [Math.log10(r.pib_locuitor) + .25 * normal(rr)(), r]).sort((a, b) => b[0] - a[0]).slice(0, m).forEach(x => lipsa.add(x[1])); }
    scrieCod(el, `regiuni["pib_locuitor"].median()                           # mediana adevărată\nregiuni["pib_locuitor"].sample(frac=${f(1 - p, 2).replace(",", ".")}).median()   # după o lipsă complet aleatoare`);
    const tot = P.map(r => Math.log10(r.pib_locuitor)), obs = P.filter(r => !lipsa.has(r)).map(r => Math.log10(r.pib_locuitor));
    const x0 = 50, x1 = W - 16, y0 = 14, y1 = 180, lo = Math.min(...tot), hi = Math.max(...tot), b = 28;
    const nt = histograma(tot, b, lo, hi + 1e-9), no = histograma(obs, b, lo, hi + 1e-9), sx = sc(lo, hi, x0, x1), sy = sc(0, Math.max(...nt) * 1.1, y1, y0), w = (x1 - x0) / b;
    let s = axe({ x0, x1, y0, y1, sx, sy, dx: [lo, hi], dy: [0, Math.max(...nt) * 1.1], fx: u => nr(10 ** u), ex: "PIB pe locuitor (scară log)", ey: "regiuni" });
    nt.forEach((c, i) => s += `<rect class="ed-lipsa" x="${x0 + i * w + .5}" y="${sy(c)}" width="${w - 1}" height="${y1 - sy(c)}"/>`);
    no.forEach((c, i) => s += `<rect class="ed-bar" x="${x0 + i * w + .5}" y="${sy(c)}" width="${w - 1}" height="${y1 - sy(c)}"/>`);
    const mt = mediana(tot), mo = obs.length ? mediana(obs) : mt;
    s += `<g class="ed-m1"><line x1="${sx(mo)}" x2="${sx(mo)}" y1="${y0}" y2="${y1}"/><text x="${sx(mo) + 5}" y="${y0 + 10}">mediana observată</text></g>`
      + `<g class="ed-m3"><line x1="${sx(mt)}" x2="${sx(mt)}" y1="${y0 + 16}" y2="${y1}"/><text x="${sx(mt) + 5}" y="${y0 + 26}">mediana adevărată</text></g>`;
    el.querySelector(".ed-g").innerHTML = svg(W, 220, s);
    const dif = 10 ** mo / 10 ** mt - 1;
    el.querySelector(".ed-o").innerHTML = cifre([["regiuni rămase", `${obs.length} din ${n}`], ["mediana adevărată", nr(10 ** mt), "ed-c-m3"], ["mediana observată", nr(10 ** mo), "ed-c-m1"],
      ["abaterea", `${dif >= 0 ? "+" : "−"}${f(Math.abs(dif) * 100, 1)}%`, Math.abs(dif) > .05 ? "ed-c-sus" : "ed-c-adev"]])
      + panou(mec === "mcar" ? "Complet aleator: rămâne un eșantion mai mic din aceeași distribuție. Abaterea e mică și fără direcție."
        : mec === "mar" ? "După țară: dispar țări întregi. Abaterea depinde de țările pierdute; în interiorul țărilor rămase, distribuția e intactă, deci se poate corecta pe țări."
        : "După valoare: lipsesc mai ales regiunile bogate. Abaterea are direcție și crește cu proporția; datele rămase nu arată că ceva lipsește.");
  };
  const deseneaza = () => { el.querySelector(".ed-h1").style.display = mod === "harta" ? "" : "none"; el.querySelector(".ed-h2").style.display = mod === "sim" ? "" : "none";
    (mod === "harta" ? harta : sim)(); };
  leaga(el, "m", v => { mod = v; deseneaza(); });
  leaga(el, "o", v => { ord = v; deseneaza(); });
  leaga(el, "k", v => { mec = v; deseneaza(); });
  ip.addEventListener("input", deseneaza);
  deseneaza();
};


/* =========================================================================
   3. Extremele: citite una câte una, apoi fără artefact
   ========================================================================= */
E.edExtreme = (gazda, d) => {
  let cap = "sus", fara = false;
  const el = bloc(gazda, `<div class="ed-ctl">${butoane("c", [["sus", "cele mai mari valori SCI"], ["jos", "cele mai mici valori SCI"]], cap)}<button class="ed-b ed-fs">exclude Svalbard</button></div><div class="ed-ex"></div><div class="ed-o"></div>`);
  const deseneaza = () => {
    const L = d[cap + (fara ? "2" : "")] || [], sv = p => p.r1 === "NO0B" || p.r2 === "NO0B", pop = v => v ? nr(v) : "—";
    el.querySelector(".ed-ex").innerHTML = `<table><thead><tr><th>regiunea 1</th><th>populația</th><th>regiunea 2</th><th>populația</th><th>distanța</th><th>SCI</th></tr></thead><tbody>`
      + L.map(p => `<tr class="${sv(p) ? "ed-r-sus" : ""}"><td>${p.n1}</td><td>${pop(p.p1)}</td><td>${p.n2}</td><td>${pop(p.p2)}</td><td>${nr(p.d)} km</td><td><b>${nr(p.sci)}</b></td></tr>`).join("") + "</tbody></table>";
    const [m1, m2] = d.medie_sci || [0, 0], [q1, q2] = d.mediana_sci || [0, 0];
    el.querySelector(".ed-o").innerHTML = cifre([["perechi cu Svalbard în tabel", `${L.filter(sv).length} din ${L.length}`, fara ? "" : "ed-c-sus"],
      ["media SCI", nr(fara ? m2 : m1)], ["mediana SCI", nr(fara ? q2 : q1)]])
      + panou(fara ? (cap === "sus" ? "Fără Svalbard, extremele sunt regiuni vecine din aceeași țară: valori plauzibile." : "Fără Svalbard, minimele sunt perechi foarte îndepărtate (teritoriile franceze de peste mări, estul Turciei): valori plauzibile.")
        : "Rândurile evidențiate conțin Svalbard (NO0B); „—” marchează o populație lipsă în tabelul regiunilor.");
  };
  leaga(el, "c", k => { cap = k; deseneaza(); });
  el.querySelector(".ed-fs").addEventListener("click", e => { fara = !fara; e.target.classList.toggle("on", fara); deseneaza(); });
  deseneaza();
};


/* =========================================================================
   4. Media și mediana: ce se întâmplă când apar câteva valori foarte mari
   ========================================================================= */
E.edRezistenta = (gazda, d) => {
  const B = (d.sci || []).filter((_, i) => i % 50 === 25), TOP = (d.sus || []).map(p => p.sci);
  const W = 900, x0 = 20, x1 = W - 20;
  const el = bloc(gazda, `<div class="ed-ctl">${glisor("k", "perechi cu valori foarte mari adăugate", 0, TOP.length, 1, 0)}</div><div class="ed-g"></div><pre class="ed-cod"></pre><div class="ed-o"></div>`);
  const ik = el.querySelector("input");
  const deseneaza = () => {
    const k = +ik.value; ik.nextElementSibling.textContent = `${k} din ${TOP.length}`;
    const v = [...B, ...TOP.slice(0, k)], L = sc(0, 6.8, x0, x1), sx = x => L(Math.log10(Math.max(1, x)));
    const M = [["media", medie(v), "ed-m1"], ["mediana", mediana(v), "ed-m3"]];
    scrieCod(el, `perechi["sci"].mean(), perechi["sci"].median()      # media și mediana\nperechi["sci"].std(), stats.iqr(perechi["sci"])     # abaterea standard și IQR`);
    let s = axe({ x0, x1, y0: 10, y1: 120, sx: L, sy: v => v, dx: [0, 6.8], nx: 7, fx: u => nr(10 ** u), ex: "SCI (axa pe scară logaritmică)" });
    const st = {}; v.forEach((x, i) => { const b = Math.round(sx(x) / 7); st[b] = (st[b] || 0) + 1;
      s += `<circle class="${i >= B.length ? "ed-sus" : "ed-p"}" cx="${b * 7}" cy="${116 - Math.min(st[b], 11) * 9}" r="4"/>`; });
    M.forEach(([e, m, cl], j) => s += `<g class="${cl}"><line x1="${sx(m)}" x2="${sx(m)}" y1="${8 + j * 16}" y2="120"/><text x="${sx(m) + 5}" y="${18 + j * 16}">${e}</text></g>`);
    el.querySelector(".ed-g").innerHTML = svg(W, 165, s);
    el.querySelector(".ed-o").innerHTML = cifre([["media", nr(M[0][1]), "ed-c-m1"], ["mediana", nr(M[1][1]), "ed-c-m3"],
      ["abaterea standard", nr(abatere(v))], ["IQR", nr(cuantila(v, .75) - cuantila(v, .25))]])
      + panou(`${B.length} perechi obișnuite (puncte verzi). Glisorul adaugă, una câte una, perechile cu cele mai mari valori SCI (portocaliu).`);
  };
  ik.addEventListener("input", deseneaza);
  deseneaza();
};


/* =========================================================================
   5. Distribuția: cinci grafice, cu citirea valorilor sub pointer
   ========================================================================= */
const variabila = (d, k) => {
  const R = REG(d);
  if (k === "sci") return [(d.sci || []).filter(x => x > 0).map(x => Math.log10(x)), "log10(SCI)"];
  if (k === "dist") return [(d.perechi || []).slice(0, 3000).map(p => 10 ** p[0]), "distanța, km"];
  if (k === "pop") return [R.filter(r => r.populatie > 0).map(r => Math.log10(r.populatie)), "log10(populația)"];
  return [R.map(r => r[k]).filter(x => x != null), ET[k]];
};
E.edDistributie = (gazda, d) => {
  let set = "sci", fel = "hist";
  const el = bloc(gazda, `<div class="ed-ctl">${butoane("s", [["sci", "SCI (log)"], ["dist", "distanța"], ["pib_locuitor", "PIB/loc."], ["varsta_medie", "vârsta medie"]], set)}${butoane("f", [["hist", "histogramă"], ["dens", "densitate"], ["ecdf", "ECDF"], ["box", "boxplot"], ["viol", "violin și puncte"]], fel)}</div>
    <div class="ed-ctl ed-gls">${glisor("b", "bare", 3, 60, 1, 14)}${glisor("o", "începutul barelor", 0, 1, .05, 0)}${glisor("h", "netezirea", .02, .4, .01, .08)}</div><div class="ed-g"></div><pre class="ed-cod"></pre><div class="ed-o"></div>`);
  const [ib, io, ih] = ["b", "o", "h"].map(n => el.querySelector(`input[data-n="${n}"]`));
  const W = 900, H = 220, x0 = 50, x1 = W - 16, y0 = 18, y1 = H - 40;
  const kde = (v, lo, hi, h) => { const bw = h * (hi - lo), n = 160, rez = [];
    for (let i = 0; i <= n; i++){ const x = lo + (hi - lo) * i / n; let s = 0;
      for (const u of v) s += Math.exp(-.5 * ((x - u) / bw) ** 2); rez.push([x, s / (v.length * bw * 2.5066)]); } return rez; };
  const deseneaza = () => {
    const [v, ex] = variabila(d, set); if (!v.length) return;
    const [df, col, lg] = { sci: ["perechi", "sci", 1], dist: ["perechi", "distanta_km", 0], pib_locuitor: ["regiuni", "pib_locuitor", 0], varsta_medie: ["regiuni", "varsta_medie", 0] }[set], Lg = lg ? ", log_scale=True" : "";
    scrieCod(el, { hist: `sns.histplot(${df}, x="${col}"${Lg}, bins=${ib.value})          # bins = numărul barelor`,
      dens: `sns.kdeplot(${df}, x="${col}"${Lg}, bw_adjust=0.5)    # bw_adjust: cât de netedă e curba`,
      ecdf: `sns.ecdfplot(${df}, x="${col}"${Lg})                  # proporția valorilor ≤ x`,
      box: `sns.boxplot(${df}, x="${col}"${Lg})`,
      viol: `sns.violinplot(${df}, x="${col}"${Lg}, inner="point")  # inner="point": și observațiile` }[fel]);
    const o = sortat(v), lo = o[0], hi = o[o.length - 1], fx = u => Math.abs(hi) > 1000 ? nr(u) : f(u, Math.abs(hi - lo) < 20 ? 1 : 0);
    const sx = sc(lo, hi, x0, x1), inv = X => lo + (X - x0) / (x1 - x0) * (hi - lo);
    el.querySelectorAll(".ed-gl").forEach(g => g.style.display =
      (g.querySelector("input").dataset.n === "h" ? ["dens", "viol"].includes(fel) : fel === "hist") ? "" : "none");
    let s = "", bare = null;
    if (fel === "hist"){
      const b = +ib.value, w = (hi - lo) / b, st = lo - w * +io.value, n = histograma(v, b + 1, st, st + w * (b + 1));
      const sy = sc(0, Math.max(...n) * 1.1, y1, y0); bare = { st, w, n };
      s += axe({ x0, x1, y0, y1, sx, sy, dx: [lo, hi], dy: [0, Math.max(...n) * 1.1], ex, ey: "câte valori", fx });
      n.forEach((c, i) => { const a = sx(Math.max(lo, st + i * w)), bb = sx(Math.min(hi, st + (i + 1) * w));
        if (bb > a) s += `<rect class="ed-bar" x="${a + .5}" y="${sy(c)}" width="${Math.max(0, bb - a - 1)}" height="${y1 - sy(c)}"/>`; });
      ib.nextElementSibling.textContent = b; io.nextElementSibling.textContent = f(+io.value, 2);
    } else if (fel === "dens"){
      const k = kde(v, lo, hi, +ih.value), mx = Math.max(...k.map(p => p[1])), sy = sc(0, mx * 1.1, y1, y0);
      s += axe({ x0, x1, y0, y1, sx, sy, dx: [lo, hi], ex, fx });
      s += `<path class="ed-arie" d="M${sx(lo)},${y1} ${k.map(p => `L${sx(p[0])},${sy(p[1])}`).join(" ")} L${sx(hi)},${y1}Z"/>`;
      v.slice(0, 600).forEach(u => s += `<line class="ed-rug" x1="${sx(u)}" x2="${sx(u)}" y1="${y1}" y2="${y1 - 7}"/>`);
      ih.nextElementSibling.textContent = f(+ih.value, 2);
    } else if (fel === "ecdf"){
      const sy = sc(0, 1, y1, y0);
      s += axe({ x0, x1, y0, y1, sx, sy, dx: [lo, hi], dy: [0, 1], ex, ey: "proporția valorilor ≤ x", fy: u => f(u, 2), fx });
      s += `<polyline class="ed-linie" points="${o.map((u, i) => `${sx(u)},${sy(i / o.length)} ${sx(u)},${sy((i + 1) / o.length)}`).join(" ")}"/>`;
      [.25, .5, .75].forEach(q => { const u = cuantila(o, q, true);
        s += `<line class="ed-l-obs" x1="${x0}" x2="${sx(u)}" y1="${sy(q)}" y2="${sy(q)}"/><line class="ed-l-obs" x1="${sx(u)}" x2="${sx(u)}" y1="${sy(q)}" y2="${y1}"/>`; });
    } else {
      const q1 = cuantila(o, .25, true), q2 = cuantila(o, .5, true), q3 = cuantila(o, .75, true), iq = q3 - q1;
      const lw = o.find(u => u >= q1 - 1.5 * iq), uw = [...o].reverse().find(u => u <= q3 + 1.5 * iq), yc = (y0 + y1) / 2;
      s += axe({ x0, x1, y0, y1, sx, sy: v => v, dx: [lo, hi], ex, fx });
      if (fel === "viol"){
        const k = kde(v, lo, hi, +ih.value), mx = Math.max(...k.map(p => p[1])), hh = sc(0, mx, 0, (y1 - y0) / 2 - 6);
        s += `<path class="ed-arie" d="M${k.map(p => `${sx(p[0])},${yc - hh(p[1])}`).join(" L")} L${[...k].reverse().map(p => `${sx(p[0])},${yc + hh(p[1])}`).join(" L")}Z"/>`;
        const rr = rng(2); v.slice(0, 800).forEach(u => s += `<circle class="ed-p ed-mic" cx="${sx(u)}" cy="${yc + (rr() - .5) * 40}" r="2"/>`);
        ih.nextElementSibling.textContent = f(+ih.value, 2);
      } else {
        s += `<line class="ed-mus" x1="${sx(lw)}" x2="${sx(q1)}" y1="${yc}" y2="${yc}"/><line class="ed-mus" x1="${sx(q3)}" x2="${sx(uw)}" y1="${yc}" y2="${yc}"/>`
          + `<rect class="ed-cutie" x="${sx(q1)}" y="${yc - 34}" width="${sx(q3) - sx(q1)}" height="68"/><line class="ed-med" x1="${sx(q2)}" x2="${sx(q2)}" y1="${yc - 34}" y2="${yc + 34}"/>`;
        o.filter(u => u < lw || u > uw).forEach(u => s += `<circle class="ed-sus" cx="${sx(u)}" cy="${yc}" r="3"/>`);
      }
    }
    s += `<line class="ed-cursor" x1="0" x2="0" y1="${y0}" y2="${y1}" style="display:none"/>`;
    el.querySelector(".ed-g").innerHTML = svg(W, H, s);
    const baza = panou(fel === "ecdf" ? "Liniile punctate marchează cuartilele. Pointerul pe grafic afișează proporția valorilor de sub fiecare prag."
      : fel === "hist" ? "Numărul și originea claselor schimbă forma aparentă, deși datele sunt aceleași. Pointerul pe grafic afișează clasa și frecvența ei."
      : fel === "box" ? "Cutia: între prima și a treia cuartilă; linia: mediana; mustățile: până la 1,5 × IQR; punctele: valorile din afara lor."
      : "O lățime de bandă mică arată zgomot; una mare ascunde forma.");
    el.querySelector(".ed-o").innerHTML = baza;
    const cur = el.querySelector(".ed-cursor");
    laPointer(el, p => {
      if (!p || p.x < x0 || p.x > x1){ cur.style.display = "none"; el.querySelector(".ed-o").innerHTML = baza; return; }
      const u = inv(p.x), sub = o.filter(z => z <= u).length; cur.style.display = ""; cur.setAttribute("x1", p.x); cur.setAttribute("x2", p.x);
      let t = [["valoarea", set === "sci" ? `${fx(u)} (SCI ≈ ${nr(10 ** u)})` : fx(u)], ["valori ≤ prag", `${nr(sub)} din ${nr(o.length)} (${f(100 * sub / o.length, 1)}%)`]];
      if (bare){ const i = Math.floor((u - bare.st) / bare.w); if (i >= 0 && i < bare.n.length) t.push(["bara", `${fx(bare.st + i * bare.w)} - ${fx(bare.st + (i + 1) * bare.w)}: ${bare.n[i]} valori`]); }
      el.querySelector(".ed-o").innerHTML = cifre(t);
    });
  };
  leaga(el, "s", k => { set = k; deseneaza(); });
  leaga(el, "f", k => { fel = k; deseneaza(); });
  [ib, io, ih].forEach(i => i.addEventListener("input", deseneaza));
  deseneaza();
};


/* =========================================================================
   6. Transformarea logaritmică: x, √x, log x
   ========================================================================= */
E.edReexprimare = (gazda, d) => {
  const R = REG(d);
  const SET = { sci: [(d.sci || []).filter(x => x > 0), "SCI"], pop: [R.map(r => r.populatie).filter(x => x > 0), "populația regiunii"],
    dens: [R.map(r => r.densitate).filter(x => x > 0), "densitatea"], pib: [R.map(r => r.pib_locuitor).filter(x => x > 0), "PIB pe locuitor"] };
  const TR = { x: [v => v, y => y, "valorile inițiale"], r: [Math.sqrt, y => y * y, "rădăcina pătrată"], l: [Math.log10, y => 10 ** y, "logaritmul în baza 10"] };
  let set = "sci", tr = "x";
  const el = bloc(gazda, `<div class="ed-ctl">${butoane("s", [["sci", "SCI"], ["pop", "populația"], ["dens", "densitatea"], ["pib", "PIB/loc."]], set)}${butoane("t", [["x", "x"], ["r", "√x"], ["l", "log10 x"]], tr)}</div><div class="ed-g"></div><pre class="ed-cod"></pre><div class="ed-o"></div>`);
  const W = 900, H = 200, x0 = 40, x1 = W - 16, y0 = 16, y1 = H - 40;
  const deseneaza = () => {
    const [fn, inv, et] = TR[tr], v = SET[set][0].map(fn);
    const [df, col] = { sci: ["perechi", "sci"], pop: ["regiuni", "populatie"], dens: ["regiuni", "densitate"], pib: ["regiuni", "pib_locuitor"] }[set];
    const ex2 = { x: `${df}["${col}"]`, r: `np.sqrt(${df}["${col}"])`, l: `np.log10(${df}["${col}"])` }[tr];
    scrieCod(el, `sns.histplot(x=${ex2})\n${ex2}.skew()        # asimetria`);
    const lo = Math.min(...v), hi = Math.max(...v), n = histograma(v, 32, lo, hi), sx = sc(lo, hi, x0, x1), sy = sc(0, Math.max(...n) * 1.1, y1, y0);
    const fm = u => tr === "l" ? `${f(u, 1)} (${nr(10 ** u)})` : nr(u);
    let s = axe({ x0, x1, y0, y1, sx, sy, dx: [lo, hi], ex: `${SET[set][1]}: ${et}`, fx: fm });
    const w = (x1 - x0) / 32; n.forEach((c, i) => s += `<rect class="ed-bar" x="${x0 + i * w + .5}" y="${sy(c)}" width="${Math.max(0, w - 1)}" height="${y1 - sy(c)}"/>`);
    const m = medie(v), q = mediana(v);
    s += `<g class="ed-m1"><line x1="${sx(m)}" x2="${sx(m)}" y1="${y0}" y2="${y1}"/><text x="${sx(m) + 5}" y="${y0 + 10}">media</text></g>`
      + `<g class="ed-m3"><line x1="${sx(q)}" x2="${sx(q)}" y1="${y0 + 18}" y2="${y1}"/><text x="${sx(q) + 5}" y="${y0 + 28}">mediana</text></g>`;
    el.querySelector(".ed-g").innerHTML = svg(W, H, s);
    const a = asimetrie(v);
    el.querySelector(".ed-o").innerHTML = cifre([["asimetria", f(a, 2), Math.abs(a) < .4 ? "ed-c-adev" : ""],
      ["", Math.abs(a) < .4 ? "aproape simetrică: media ≈ mediana" : a > 0 ? "coadă lungă spre dreapta: media > mediana" : "coadă spre stânga: transformarea e prea puternică"]])
      + panou(tr === "l" ? "Pe axă, fiecare valoare log10 are în paranteză valoarea inițială: 3 înseamnă 1.000, 6 înseamnă 1.000.000." : "Asimetria 0 înseamnă o distribuție simetrică; cu cât e mai mare, cu atât coada spre dreapta e mai lungă.");
  };
  leaga(el, "s", k => { set = k; deseneaza(); });
  leaga(el, "t", k => { tr = k; deseneaza(); });
  deseneaza();
};


/* =========================================================================
   7. Tabelul de contingență: distanța × aceeași țară; calculul procentelor arătat
   ========================================================================= */
E.edContingenta = (gazda, d) => {
  const T = d.sci;
  let mod = "n", gr = "hm", cel = [0, 0];
  const el = bloc(gazda, `<div class="ed-ctl">${butoane("m", [["n", "numere"], ["r", "% pe rând"], ["c", "% pe coloană"]], mod)}${butoane("g", [["hm", "matrice colorată"], ["stiv", "bare stivuite 100%"], ["grup", "bare grupate"], ["moz", "mozaic"]], gr)}</div>
    <div class="ed-ct"><div class="ed-ct__t"></div><div><div class="ed-g"></div><p class="ed-leg2"></p></div></div><pre class="ed-cod"></pre><div class="ed-o"></div>`);
  const CUL = ["var(--sci-2)", "var(--sci-5)"];
  const deseneaza = () => {
    const R = T.v.map(x => x.reduce((a, b) => a + b, 0)), Cc = T.c.map((_, j) => T.v.reduce((a, x) => a + x[j], 0)), N = R.reduce((a, b) => a + b, 0);
    const val = (i, j) => mod === "n" ? T.v[i][j] : mod === "r" ? T.v[i][j] / R[i] : T.v[i][j] / Cc[j];
    const fv = u => mod === "n" ? nr(u) : f(100 * u, u < .1 ? 1 : 0) + "%";
    const mx = Math.max(...T.v.flatMap((x, i) => x.map((_, j) => val(i, j))));
    const [ci, cj] = cel;
    /* celulele care intră la numitor: rândul (pe rând) sau coloana (pe coloană) */
    const inNumitor = (i, j) => (mod === "r" && i === ci) || (mod === "c" && j === cj);
    el.querySelector(".ed-ct__t").innerHTML = `<table><thead><tr><th>${T.er}</th>${T.c.map(c => `<th>${c}</th>`).join("")}${mod === "n" ? "<th>total</th>" : ""}</tr></thead><tbody>`
      + T.r.map((rr, i) => `<tr><th>${rr}</th>${T.c.map((_, j) => { const u = val(i, j);
        return `<td data-i="${i}" data-j="${j}" class="${ci === i && cj === j ? "on" : ""}${inNumitor(i, j) ? " numitor" : ""}" style="--p:${(u / mx).toFixed(3)}">${fv(u)}</td>`; }).join("")}`
        + (mod === "n" ? `<td class="tot">${nr(R[i])}</td>` : "") + `</tr>`).join("")
      + (mod === "n" ? `<tr><th>total</th>${Cc.map(c => `<td class="tot">${nr(c)}</td>`).join("")}<td class="tot">${nr(N)}</td></tr>` : "") + "</tbody></table>";
    const W = 420, H = 250, x0 = 56, x1 = W - 8, y0 = 10, y1 = H - 46; let s = "", leg = "";
    if (gr === "hm"){
      const cw = (x1 - x0) / T.c.length, rh = (y1 - y0) / T.r.length;
      T.r.forEach((rr, i) => { s += `<text class="ed-tx ed-tx--mic" x="${x0 - 6}" y="${y0 + i * rh + rh / 2 + 4}" text-anchor="end">${rr}</text>`;
        T.c.forEach((_, j) => { const u = val(i, j);
          s += `<rect x="${x0 + j * cw + 1}" y="${y0 + i * rh + 1}" width="${cw - 2}" height="${rh - 2}" style="fill:var(--accent);opacity:${(.08 + .92 * u / mx).toFixed(2)}"/>`
            + `<text class="ed-tx" x="${x0 + j * cw + cw / 2}" y="${y0 + i * rh + rh / 2 + 4}" text-anchor="middle"${u / mx > .55 ? ' style="fill:#fff"' : ""}>${fv(u)}</text>`; }); });
      T.c.forEach((c, j) => s += `<text class="ed-tx ed-tx--mic" x="${x0 + j * cw + cw / 2}" y="${y1 + 16}" text-anchor="middle">${c}</text>`);
      leg = "Același tabel, cu culoarea după valoare: cu cât e mai închisă, cu atât valoarea e mai mare.";
    } else if (gr === "grup"){
      const sy = sc(0, mod === "n" ? mx : 1, y1, y0), bw = (x1 - x0) / T.r.length;
      T.r.forEach((rr, i) => { T.c.forEach((_, j) => { const p = val(i, j), w = (bw - 12) / T.c.length;
        s += `<rect x="${x0 + i * bw + 6 + j * w}" y="${sy(p)}" width="${Math.max(0, w - 2)}" height="${y1 - sy(p)}" style="fill:${CUL[j]}"/>`; });
        s += `<text class="ed-tx ed-tx--mic" x="${x0 + i * bw + bw / 2}" y="${y1 + 16}" text-anchor="middle">${rr}</text>`; });
      s += `<text class="ed-tx" x="${x0 - 4}" y="${y0 + 8}" text-anchor="end">${mod === "n" ? nr(mx) : "100%"}</text><text class="ed-tx" x="${x0 - 4}" y="${y1}" text-anchor="end">0</text>`;
      leg = mod === "n" ? "Două bare pe interval, înălțimea = numărul de perechi. Perechile din țări diferite sunt de 18 ori mai multe, deci barele „aceeași țară” abia se văd: de aceea se trece la procente."
        : "Două bare pe interval, înălțimea = procentul din tabel.";
    } else {
      let xa = x0; T.r.forEach((rr, i) => { const w = gr === "moz" ? (x1 - x0) * R[i] / N : (x1 - x0) / T.r.length; let ya = y1;
        T.c.forEach((_, j) => { const h = (y1 - y0) * T.v[i][j] / R[i]; s += `<rect x="${xa + 1}" y="${ya - h}" width="${Math.max(0, w - 2)}" height="${h}" style="fill:${CUL[j]}"/>`; ya -= h; });
        s += `<text class="ed-tx ed-tx--mic" x="${xa + w / 2}" y="${y1 + 16}" text-anchor="middle">${w > 30 ? rr : ""}</text>`; xa += w; });
      leg = gr === "stiv" ? "O bară pe interval de distanță, înaltă cât 100% din perechile lui; partea de jos, mai deschisă = procentul perechilor din aceeași țară (procentele pe rând)."
        : "Ca barele stivuite, dar lățimea fiecărei bare = câte perechi are intervalul. Intervalele scurte au puține perechi, deci barele lor sunt înguste.";
    }
    if (gr !== "hm") s += T.c.map((c, j) => `<g transform="translate(${x0 + j * 130},${H - 6})"><rect y="-10" width="10" height="10" style="fill:${CUL[j]}"/><text class="ed-tx" x="14" y="-1">${c}</text></g>`).join("");
    el.querySelector(".ed-g").innerHTML = svg(W, H, s);
    el.querySelector(".ed-leg2").textContent = leg;
    const norm = { n: "", r: ', normalize="index"', c: ', normalize="columns"' }[mod];
    scrieCod(el, { hm: `tabel = pd.crosstab(perechi["interval_km"], perechi["aceeasi_tara"]${norm})\nsns.heatmap(tabel, annot=True)`,
      grup: `pd.crosstab(perechi["interval_km"], perechi["aceeasi_tara"]${norm})\nsns.countplot(perechi, x="interval_km", hue="aceeasi_tara")`,
      stiv: `tabel = pd.crosstab(perechi["interval_km"], perechi["aceeasi_tara"], normalize="index")\ntabel.plot(kind="bar", stacked=True)`,
      moz: `from statsmodels.graphics.mosaicplot import mosaic\nmosaic(perechi, ["interval_km", "aceeasi_tara"])` }[gr]);
    const v = T.v[ci][cj], rr = T.r[ci], cc = T.c[cj];
    el.querySelector(".ed-o").innerHTML =
        `<p class="ed-calc${mod === "r" ? " on" : ""}"><b>pe rând</b> ${nr(v)} ÷ ${nr(R[ci])} = <b>${f(100 * v / R[ci], 1)}%</b> · dintre cele ${nr(R[ci])} de perechi aflate la ${rr} km, ${nr(v)} sunt „${cc}”</p>`
      + `<p class="ed-calc${mod === "c" ? " on" : ""}"><b>pe coloană</b> ${nr(v)} ÷ ${nr(Cc[cj])} = <b>${f(100 * v / Cc[cj], 1)}%</b> · dintre cele ${nr(Cc[cj])} de perechi „${cc}”, ${nr(v)} sunt la ${rr} km</p>`;
    el.querySelectorAll("td[data-i]").forEach(t => t.addEventListener("click", () => { cel = [+t.dataset.i, +t.dataset.j]; deseneaza(); }));
  };
  leaga(el, "m", k => { mod = k; deseneaza(); });
  leaga(el, "g", k => { gr = k; deseneaza(); });
  deseneaza();
};


/* =========================================================================
   8. Corelația: puncte care se pot trage; Pearson față de Spearman și Kendall
   ========================================================================= */
E.edCorelatie = (gazda, d) => {
  const R = REG(d), P = (d.perechi || []).slice(0, 300);
  const SET = {
    pib: { t: "PIB/loc. și studiile", ...pereche(R, "pib_locuitor", "studii_superioare") },
    dens: { t: "densitatea și PIB/loc.", ...pereche(R, "densitate", "pib_locuitor") },
    vrs: { t: "vârsta medie și șomajul", ...pereche(R, "varsta_medie", "somaj") },
    dist: { t: "distanța și SCI (300 de perechi)", x: P.map(p => 10 ** p[0]), y: P.map(p => 10 ** p[1]), ex: "distanța, km", ey: "SCI" } };
  function pereche(R, a, b){ const L = R.filter(r => r[a] > 0 && r[b] > 0); return { x: L.map(r => r[a]), y: L.map(r => r[b]), ex: ET[a], ey: ET[b] }; }
  let set = "pib", lg = false, X = [], Y = [], dom = null, trag = -1;
  const el = bloc(gazda, `<div class="ed-ctl">${butoane("s", Object.entries(SET).map(([k, v]) => [k, v.t]), set)}<button class="ed-b ed-lg">scară logaritmică</button><button class="ed-b ed-rs">datele inițiale</button></div><div class="ed-g"></div><pre class="ed-cod"></pre><div class="ed-o"></div>`);
  const W = 900, H = 220, x0 = 60, x1 = W - 16, y0 = 18, y1 = H - 36;
  const init = () => { X = [...SET[set].x]; Y = [...SET[set].y]; dom = null; };
  const tx = u => lg ? Math.log10(u) : u, itx = u => lg ? 10 ** u : u;
  const deseneaza = () => {
    const S = SET[set], x = X.map(tx), y = Y.map(tx);
    const [df, cx, cy] = { pib: ["regiuni", "pib_locuitor", "studii_superioare"], dens: ["regiuni", "densitate", "pib_locuitor"], vrs: ["regiuni", "varsta_medie", "somaj"], dist: ["perechi", "distanta_km", "sci"] }[set];
    scrieCod(el, `sns.scatterplot(${df}, x="${cx}", y="${cy}")${lg ? '\nplt.xscale("log"); plt.yscale("log")' : ""}\n`
      + `${df}["${cx}"].corr(${df}["${cy}"], method="spearman")   # "pearson" sau "kendall"`
      + (lg ? `\nnp.log10(${df}["${cx}"]).corr(np.log10(${df}["${cy}"]))   # Pearson pe log` : ""));
    if (!dom){ const a = Math.min(...x), b = Math.max(...x), c = Math.min(...y), e = Math.max(...y), mx = (b - a) * .25, my = (e - c) * .25; dom = [a, b + mx, c, e + my]; }
    const [lo, hi, ylo, yhi] = dom, sx = sc(lo, hi, x0, x1), sy = sc(ylo, yhi, y1, y0);
    const fm = b => u => lg ? f(u, 1) : Math.abs(b) > 1000 ? nr(u) : f(u, 0);
    let s = axe({ x0, x1, y0, y1, sx, sy, dx: [lo, hi], dy: [ylo, yhi], ex: (lg ? "log10 " : "") + S.ex, ey: (lg ? "log10 " : "") + S.ey, fx: fm(hi), fy: fm(yhi) });
    const [a, b] = mcmmp(x, y); s += `<line class="ed-l-obs" x1="${sx(lo)}" x2="${sx(hi)}" y1="${sy(a + b * lo)}" y2="${sy(a + b * hi)}"/>`;
    x.forEach((u, i) => s += `<circle class="ed-p ed-trage" data-i="${i}" cx="${sx(u)}" cy="${sy(y[i])}" r="3.5"/>`);
    el.querySelector(".ed-g").innerHTML = svg(W, H, s);
    const sv = el.querySelector("svg"), dr = sv.querySelector(".ed-l-obs");
    const cifreCor = () => { const x = X.map(tx), y = Y.map(tx), r0 = SET[set], [a, b] = mcmmp(x, y);
      dr.setAttribute("y1", sy(a + b * lo)); dr.setAttribute("y2", sy(a + b * hi));
      el.querySelector(".ed-o").innerHTML = cifre([["Pearson r", f(pearson(x, y)), "ed-c-m1"], ["Spearman ρ", f(spearman(x, y)), "ed-c-m2"], ["Kendall τ", f(kendall(x, y)), "ed-c-m3"],
        ["datele inițiale (r / ρ)", `${f(pearson(r0.x.map(tx), r0.y.map(tx)))} / ${f(spearman(r0.x, r0.y))}`], ["observații", nr(x.length)]])
        + panou("La mutarea unui punct departe de nor, Pearson se schimbă mult, iar Spearman și Kendall puțin: ultimii doi depind doar de ordinea valorilor."); };
    sv.addEventListener("pointerdown", e => { const c = e.target.closest(".ed-trage"); if (!c) return; trag = +c.dataset.i; c.classList.add("on"); sv.setPointerCapture(e.pointerId); e.preventDefault(); });
    sv.addEventListener("pointermove", e => { if (trag < 0) return; const p = punct(sv, e), c = sv.querySelector(`.ed-trage[data-i="${trag}"]`);
      const X1 = Math.max(x0, Math.min(x1, p.x)), Y1 = Math.max(y0, Math.min(y1, p.y));
      c.setAttribute("cx", X1); c.setAttribute("cy", Y1);
      X[trag] = Math.max(1e-6, itx(lo + (X1 - x0) / (x1 - x0) * (hi - lo))); Y[trag] = Math.max(1e-6, itx(ylo + (y1 - Y1) / (y1 - y0) * (yhi - ylo))); cifreCor(); });
    const gata = () => { if (trag < 0) return; sv.querySelector(`.ed-trage[data-i="${trag}"]`)?.classList.remove("on"); trag = -1; };
    sv.addEventListener("pointerup", gata); sv.addEventListener("pointercancel", gata);
    cifreCor();
  };
  leaga(el, "s", k => { set = k; init(); deseneaza(); });
  el.querySelector(".ed-lg").addEventListener("click", e => { lg = !lg; e.target.classList.toggle("on", lg); dom = null; deseneaza(); });
  el.querySelector(".ed-rs").addEventListener("click", () => { init(); deseneaza(); });
  init(); deseneaza();
};


/* =========================================================================
   9. Prea multe puncte: suprapunere, transparență, histogramă 2D, mediane
   ========================================================================= */
E.edMulte = (gazda, d) => {
  const P = d.perechi || [];
  let vedere = "pct";
  const NS = [300, 1000, 3000, P.length];
  const el = bloc(gazda, `<div class="ed-ctl">${glisor("n", "perechi desenate", 0, 3, 1, 3)}${butoane("v", [["pct", "puncte"], ["tr", "transparență"], ["2d", "histogramă 2D"], ["med", "mediane pe intervale"]], vedere)}
    ${glisor("a", "opacitatea", .01, .5, .01, .04)}${glisor("b", "căsuțe pe axa x", 10, 80, 5, 45)}</div><div class="ed-g"></div><pre class="ed-cod"></pre><div class="ed-o"></div>`);
  const [inp, ia, ibn] = ["n", "a", "b"].map(n => el.querySelector(`input[data-n="${n}"]`));
  const deseneaza = () => {
    const n = NS[+inp.value]; inp.nextElementSibling.textContent = nr(n); ia.nextElementSibling.textContent = f(+ia.value, 2); ibn.nextElementSibling.textContent = ibn.value;
    ia.closest(".ed-gl").style.display = vedere === "tr" ? "" : "none"; ibn.closest(".ed-gl").style.display = vedere === "2d" ? "" : "none";
    scrieCod(el, { pct: `sns.scatterplot(perechi, x="distanta_km", y="sci")\nplt.xscale("log"); plt.yscale("log")`,
      tr: `sns.scatterplot(perechi, x="distanta_km", y="sci", alpha=${(+ia.value).toFixed(2)})   # alpha = opacitatea\nplt.xscale("log"); plt.yscale("log")`,
      "2d": `sns.histplot(perechi, x="distanta_km", y="sci", log_scale=True, bins=${ibn.value})`,
      med: `perechi.groupby("interval_km", observed=True)["sci"].quantile([0.25, 0.5, 0.75]).unstack()` }[vedere]);
    const D = P.slice(0, n), W = 900, H = 230, x0 = 46, x1 = W - 16, y0 = 12, y1 = H - 34;
    const sx = sc(1, 4, x0, x1), sy = sc(0, 6.6, y1, y0);
    let s = axe({ x0, x1, y0, y1, sx, sy, dx: [1, 4], dy: [0, 6.6], ex: "distanța, km (log10)", ey: "SCI (log10)", fx: u => nr(10 ** u), fy: u => f(u, 0) });
    if (vedere === "2d"){
      const B = +ibn.value, M = Math.round(B * .58), c = Array.from({ length: M }, () => new Array(B).fill(0));
      D.forEach(([x, y]) => { const i = Math.min(B - 1, Math.max(0, Math.floor((x - 1) / 3 * B))), j = Math.min(M - 1, Math.max(0, Math.floor(y / 6.6 * M))); c[j][i]++; });
      const mx = Math.max(...c.flat()), w = (x1 - x0) / B, h = (y1 - y0) / M;
      c.forEach((rd, j) => rd.forEach((k, i) => { if (k) s += `<rect x="${x0 + i * w}" y="${y1 - (j + 1) * h}" width="${w}" height="${h}" style="fill:var(--accent);opacity:${(.12 + .88 * Math.sqrt(k / mx)).toFixed(2)}"/>`; }));
    } else if (vedere === "med"){
      const pts = []; for (let a = 1; a < 4; a += .25){ const g = D.filter(p => p[0] >= a && p[0] < a + .25).map(p => p[1]); if (g.length > 4) pts.push([a + .125, cuantila(g, .25), mediana(g), cuantila(g, .75), g.length]); }
      pts.forEach(p => s += `<line class="ed-mus" x1="${sx(p[0])}" x2="${sx(p[0])}" y1="${sy(p[1])}" y2="${sy(p[3])}"/>`);
      s += `<polyline class="ed-linie" points="${pts.map(p => `${sx(p[0])},${sy(p[2])}`).join(" ")}"/>` + pts.map(p => `<circle class="ed-p" cx="${sx(p[0])}" cy="${sy(p[2])}" r="5"/><text class="ed-tx ed-tx--mic" x="${sx(p[0])}" y="${y0 + 8}" text-anchor="middle">${nr(p[4])}</text>`).join("");
    }
    el.querySelector(".ed-g").innerHTML = svg(W, H, s) + (["pct", "tr"].includes(vedere) ? `<canvas class="ed-cv" width="${W * 2}" height="${H * 2}"></canvas>` : "");
    const cv = el.querySelector("canvas");
    if (cv){ const c = cv.getContext("2d"), col = getComputedStyle(el).getPropertyValue("--accent").trim() || "#1a7a66";
      c.scale(2, 2); c.fillStyle = col; c.globalAlpha = vedere === "tr" ? +ia.value : .9;
      D.forEach(([x, y]) => { c.beginPath(); c.arc(sx(x), sy(y), 2.2, 0, 6.3); c.fill(); }); }
    el.querySelector(".ed-o").innerHTML = panou(vedere === "pct" ? "Punctele se suprapun: zona cu cele mai multe perechi nu se distinge."
      : vedere === "tr" ? "Opacitatea potrivită depinde de numărul de puncte: cu mai multe puncte, opacitatea trebuie redusă."
      : vedere === "2d" ? "Fiecare căsuță e colorată după numărul de perechi. Căsuțele prea mici arată zgomot, cele prea mari ascund forma."
      : "Mediana și cuartilele pe intervale de distanță, cu numărul de perechi deasupra: forma relației și împrăștierea ei.");
  };
  leaga(el, "v", k => { vedere = k; deseneaza(); });
  [inp, ia, ibn].forEach(i => i.addEventListener("input", deseneaza));
  deseneaza();
};


/* =========================================================================
   10. Tipar real sau întâmplare: amestecarea (testul de permutare)
   ========================================================================= */
E.edLineup = (gazda, d) => {
  const R = REG(d).filter(r => r.populatie > 0);
  const RUNDE = [
    { t: "PIB/loc. și studiile", x: "pib_locuitor", y: "studii_superioare" },
    { t: "vârsta medie și studiile", x: "varsta_medie", y: "studii_superioare" },
    { t: "PIB/loc. și vârsta medie", x: "pib_locuitor", y: "varsta_medie" }];
  let k = 0, A = [], arat = null, samanta = 1 + Math.floor(Math.random() * 1000);
  const el = bloc(gazda, `<div class="ed-ctl">${butoane("r", RUNDE.map((q, i) => [String(i), q.t]), "0")}
    <button class="ed-b ed-1">amestecă o dată</button><button class="ed-b ed-200">amestecă de 200 de ori</button><button class="ed-b ed-0">de la zero</button></div>
    <div class="ed-g"></div><pre class="ed-cod"></pre><div class="ed-o"></div>`);
  const W = 900, H = 230;
  const amesteca = a => { const r = rng(samanta++), b = [...a]; for (let i = b.length - 1; i > 0; i--){ const j = Math.floor(r() * (i + 1)); [b[i], b[j]] = [b[j], b[i]]; } return b; };
  const date = () => { const q = RUNDE[k], P = R.filter(r => r[q.x] != null && r[q.y] != null); return [q, P.map(r => r[q.x]), P.map(r => r[q.y])]; };
  const deseneaza = () => {
    const [q, xs, ys] = date(), real = spearman(xs, ys), yy = arat || ys;
    scrieCod(el, `reala = regiuni["${q.x}"].corr(regiuni["${q.y}"], method="spearman")\n`
      + `amestecat = pd.Series(rng.permutation(regiuni["${q.y}"].values), index=regiuni.index)   # aceleași valori, alte regiuni\n`
      + `regiuni["${q.x}"].corr(amestecat, method="spearman")       # corelația după amestecare`);
    /* stânga: punctele, reale sau amestecate */
    const a0 = 50, a1 = 360, b0 = 24, b1 = H - 34;
    const sx = sc(Math.min(...xs), Math.max(...xs), a0, a1), sy = sc(Math.min(...ys), Math.max(...ys), b1, b0);
    let s = axe({ x0: a0, x1: a1, y0: b0, y1: b1, sx, sy, dx: [Math.min(...xs), Math.max(...xs)], dy: [Math.min(...ys), Math.max(...ys)], nx: 4, ny: 4,
      fx: u => u > 1000 ? nr(u) : f(u, 0), fy: u => f(u, 0), ex: ET[q.x], ey: ET[q.y] });
    xs.forEach((u, i) => s += `<circle class="${arat ? "ed-sus" : "ed-p"} ed-mic" cx="${sx(u)}" cy="${sy(yy[i])}" r="2.2"/>`);
    s += `<text class="ed-tx ed-gros" x="${a1}" y="12" text-anchor="end">${arat ? `amestecat: ρ = ${f(spearman(xs, yy))}` : `datele reale: ρ = ${f(real)}`}</text>`;
    /* dreapta: corelațiile din amestecări, față de cea reală */
    const c0 = 430, c1 = W - 16, sh = sc(-.7, .7, c0, c1), B = 28, n = histograma(A, B, -.7, .7), mx = Math.max(4, ...n), syh = sc(0, mx * 1.1, b1, b0), w = (c1 - c0) / B;
    s += axe({ x0: c0, x1: c1, y0: b0, y1: b1, sx: sh, sy: syh, dx: [-.7, .7], nx: 7, fx: u => f(u, 1), ex: "ρ: corelația datelor amestecate (bare) și a celor reale (linia)", ey: "câte amestecări" });
    n.forEach((c, i) => { if (c) s += `<rect class="ed-bar2" x="${c0 + i * w + .5}" y="${syh(c)}" width="${w - 1}" height="${b1 - syh(c)}"/>`; });
    s += `<g class="ed-m1"><line x1="${sh(real)}" x2="${sh(real)}" y1="${b0}" y2="${b1}"/><text x="${sh(real) + (real > .4 ? -6 : 6)}" y="${b0 + 10}" text-anchor="${real > .4 ? "end" : "start"}">reală: ${f(real)}</text></g>`;
    el.querySelector(".ed-g").innerHTML = svg(W, H, s);
    const K = A.filter(a => Math.abs(a) >= Math.abs(real)).length;
    el.querySelector(".ed-o").innerHTML = !A.length
      ? panou("Stânga: datele reale, câte un punct pe regiune. „Amestecă o dată” mută valorile de pe axa verticală la întâmplare între regiuni: valorile rămân aceleași, legătura dispare. Corelația fiecărei amestecări se adaugă în dreapta.")
      : cifre([["amestecări", nr(A.length)], [`cu |ρ| cel puțin ${f(Math.abs(real))}`, `${K} din ${A.length}`, K / A.length < .05 ? "ed-c-adev" : "ed-c-sus"],
          ["", A.length < 50 ? "mai multe amestecări, pentru o concluzie" : K / A.length < .05
            ? "corelația reală nu apare din întâmplare: relația este reală"
            : "corelații la fel de mari apar des și din întâmplare: relația poate fi doar întâmplare"]]);
  };
  el.querySelector(".ed-1").addEventListener("click", () => { const [, xs, ys] = date(); arat = amesteca(ys); A.push(spearman(xs, arat)); deseneaza(); });
  el.querySelector(".ed-200").addEventListener("click", () => { const [, xs, ys] = date(); const rx = ranguri(xs);
    for (let i = 0; i < 200; i++){ arat = amesteca(ys); A.push(pearson(rx, ranguri(arat))); } deseneaza(); });
  el.querySelector(".ed-0").addEventListener("click", () => { A = []; arat = null; deseneaza(); });
  leaga(el, "r", v => { k = +v; A = []; arat = null; deseneaza(); });
  deseneaza();
};


/* =========================================================================
   11. Granița, la aceeași distanță: o comparație corectă
   ========================================================================= */
E.edGrupuri = (gazda, d) => {
  const P = d.perechi || [];
  const D = [null, 50, 100, 200, 300, 500, 800, 1200];
  const el = bloc(gazda, `<div class="ed-ctl">${glisor("d", "compară perechile aflate la", 0, D.length - 1, 1, 0)}</div><div class="ed-g"></div><pre class="ed-cod"></pre><div class="ed-o"></div>`);
  const inp = el.querySelector("input");
  const med = (a) => a.length ? 10 ** mediana(a) : null;
  const toateRap = med(P.filter(p => p[2]).map(p => p[1])) / med(P.filter(p => !p[2]).map(p => p[1]));
  const W = 900, H = 240, a0 = 56, a1 = 560, b0 = 14, b1 = H - 36;
  const deseneaza = () => {
    const c = D[+inp.value], lo = c ? Math.log10(c / 1.3) : -1, hi = c ? Math.log10(c * 1.3) : 9;
    inp.nextElementSibling.textContent = c ? `aproximativ ${nr(c)} km (${nr(Math.round(c / 1.3))}-${nr(Math.round(c * 1.3))})` : "toate distanțele";
    const In = P.filter(p => p[0] >= lo && p[0] < hi), da = In.filter(p => p[2]).map(p => p[1]), nu = In.filter(p => !p[2]).map(p => p[1]);
    scrieCod(el, c ? `la_fel = perechi[perechi["distanta_km"].between(${Math.round(c / 1.3)}, ${Math.round(c * 1.3)})]     # doar perechile aflate la ~${c} km\nla_fel.groupby("aceeasi_tara")["sci"].median()`
      : `perechi.groupby("aceeasi_tara")["sci"].median()          # toate perechile, la orice distanță`);
    /* stânga: toate perechile; banda arată ce se compară */
    const sx = sc(1, 4, a0, a1), sy = sc(0, 6.6, b1, b0);
    let s = axe({ x0: a0, x1: a1, y0: b0, y1: b1, sx, sy, dx: [1, 4], dy: [0, 6.6], fx: u => nr(10 ** u), fy: u => nr(10 ** u), ex: "distanța, km", ey: "SCI" });
    if (c) s += `<rect x="${sx(lo)}" y="${b0}" width="${sx(hi) - sx(lo)}" height="${b1 - b0}" style="fill:var(--ambra);opacity:.12"/>`;
    P.slice(0, 4000).forEach(p => { const inb = !c || (p[0] >= lo && p[0] < hi);
      s += `<circle cx="${sx(p[0])}" cy="${sy(p[1])}" r="${p[2] ? 2.4 : 1.6}" class="${p[2] ? "ed-sus" : "ed-p"}" style="opacity:${inb ? (p[2] ? .9 : .35) : .07}"/>`; });
    s += `<g transform="translate(${a1 - 190},${b0 + 6})"><circle r="4" class="ed-sus"/><text class="ed-tx" x="8" y="4">aceeași țară</text><circle cx="100" r="4" class="ed-p"/><text class="ed-tx" x="108" y="4">țări diferite</text></g>`;
    /* dreapta: mediana fiecărui grup și raportul */
    const md = med(da), mn = med(nu), x0 = 620, x1 = W - 20, M = Math.max(md || 0, mn || 0) || 1, bx = sc(0, M, x0, x1);
    s += `<text class="ed-tx ed-gros" x="${x0}" y="${b0 + 10}">mediana SCI ${c ? `la ~${nr(c)} km` : "pe toate perechile"}</text>`;
    [["aceeași țară", md, da.length, "ed-bar2"], ["țări diferite", mn, nu.length, "ed-bar"]].forEach(([e, v, n, cl], i) => { const y = b0 + 34 + i * 60;
      s += `<text class="ed-tx" x="${x0}" y="${y}">${e} (${nr(n)} perechi)</text>`
        + (v && n >= 5 ? `<rect class="${cl}" x="${x0}" y="${y + 6}" width="${Math.max(2, bx(v) - x0)}" height="22"/><text class="ed-tx ed-gros" x="${Math.min(x1 - 4, bx(v) + 6)}" y="${y + 22}" text-anchor="${bx(v) > x1 - 60 ? "end" : "start"}"${bx(v) > x1 - 60 ? ' style="fill:#fff"' : ""}>${nr(v)}</text>` : `<text class="ed-tx" x="${x0}" y="${y + 22}">prea puține perechi</text>`); });
    const rap = md && mn && da.length >= 5 && nu.length >= 5 ? md / mn : null;
    s += `<text class="ed-tx ed-gros" x="${x0}" y="${b0 + 172}" style="font-size:18px">${rap ? `de ${f(rap, 0)} ori mai mare` : ""}</text>`;
    el.querySelector(".ed-g").innerHTML = svg(W, H, s);
    el.querySelector(".ed-o").innerHTML = cifre([["toate perechile", `aceeași țară: de ${f(toateRap, 0)} ori mai mare`], ...(c && rap ? [[`doar la ~${nr(c)} km`, `de ${f(rap, 0)} ori mai mare`, "ed-c-sus"]] : [])])
      + panou(c ? "Comparăm doar perechi aflate la aproximativ aceeași distanță (banda colorată). Diferența care rămâne nu mai poate veni din distanță."
        : "Punctele portocalii (aceeași țară) stau aproape toate în stânga, la distanțe mici, unde SCI e mare oricum. Glisorul alege o distanță: se compară doar perechile aflate acolo.");
  };
  inp.addEventListener("input", deseneaza);
  deseneaza();
};


/* =========================================================================
   13. Multe variabile: matricea de grafice și matricea de corelație
   ========================================================================= */
E.edMultivar = (gazda, d) => {
  const V = ["pib_locuitor", "studii_superioare", "somaj", "varsta_medie", "densitate"], SC = { pib_locuitor: "PIB/loc.", studii_superioare: "studii", somaj: "șomaj", varsta_medie: "vârsta", densitate: "densitate" };
  const R0 = REG(d).filter(r => V.every(v => r[v] != null && r[v] > 0));
  let sel = [0, 4], met = "s", lg = true;
  const el = bloc(gazda, `<div class="ed-ctl">${butoane("m", [["s", "Spearman"], ["p", "Pearson"]], met)}<button class="ed-b ed-lg on">densitatea pe scara log</button></div><div class="ed-mv"><div class="ed-g"></div><div class="ed-h"></div></div><pre class="ed-cod"></pre><div class="ed-o"></div>`);
  const deseneaza = () => {
    scrieCod(el, `date = regiuni[["pib_locuitor", "studii_superioare", "somaj", "varsta_medie", "densitate"]]${lg ? '.assign(densitate=np.log10(regiuni["densitate"]))' : ""}\n`
      + `sns.pairplot(date); sns.heatmap(date.corr(method="${met === "s" ? "spearman" : "pearson"}"), annot=True, cmap="RdBu_r", vmin=-1, vmax=1)`);
    const R = R0.map(r => V.map(v => v === "densitate" && lg ? Math.log10(r[v]) : r[v])), co = met === "s" ? spearman : pearson;
    const M = V.map((_, i) => V.map((_, j) => co(R.map(r => r[i]), R.map(r => r[j]))));
    const k = V.length, w = 74, s0 = 56; let s = "";
    for (let i = 0; i < k; i++) for (let j = 0; j < k; j++){
      const X0 = s0 + j * w, Y0 = i * w, xs = R.map(r => r[j]), ys = R.map(r => r[i]), sx = sc(Math.min(...xs), Math.max(...xs), X0 + 4, X0 + w - 6), sy = sc(Math.min(...ys), Math.max(...ys), Y0 + w - 6, Y0 + 4);
      const on = (sel[0] === i && sel[1] === j) || (sel[0] === j && sel[1] === i);
      s += `<rect class="ed-cadru ${on ? "on" : ""}" data-i="${i}" data-j="${j}" x="${X0}" y="${Y0}" width="${w - 2}" height="${w - 2}"/>`;
      if (i === j){ const n = histograma(xs, 10, Math.min(...xs), Math.max(...xs) + 1e-9), m = Math.max(...n);
        n.forEach((c, b) => s += `<rect class="ed-bar" x="${X0 + 4 + b * 6.4}" y="${Y0 + w - 6 - c / m * 56}" width="5.4" height="${c / m * 56}"/>`); }
      else R.forEach(r => s += `<circle cx="${sx(r[j])}" cy="${sy(r[i])}" r="1.3" style="fill:var(--accent);opacity:.55;pointer-events:none"/>`);
    }
    V.forEach((v, i) => s += `<text class="ed-tx ed-tx--mic" x="${s0 - 4}" y="${i * w + w / 2}" text-anchor="end">${SC[v]}${v === "densitate" && lg ? " (log)" : ""}</text>`);
    el.querySelector(".ed-g").innerHTML = svg(s0 + k * w, k * w + 4, s, "ed-pp");
    let h = `<div class="ed-hm" style="--n:${k};--w:52px"><span></span>${V.map(v => `<b>${SC[v]}</b>`).join("")}`;
    M.forEach((rd, i) => { h += `<b class="ed-hm__r">${SC[V[i]]}</b>` + rd.map((v, j) => { const on = (sel[0] === i && sel[1] === j) || (sel[0] === j && sel[1] === i);
      return `<i data-i="${i}" data-j="${j}" class="${on ? "on" : ""}" style="background:${v >= 0 ? `color-mix(in srgb,var(--hsd-7) ${Math.abs(v) * 90}%,var(--panza))` : `color-mix(in srgb,var(--hsd-1) ${Math.abs(v) * 90}%,var(--panza))`}">${i === j ? "" : f(v, 1)}</i>`; }).join(""); });
    el.querySelector(".ed-h").innerHTML = h + "</div>";
    el.querySelectorAll("[data-i]").forEach(c => c.addEventListener("click", () => { sel = [+c.dataset.i, +c.dataset.j]; deseneaza(); }));
    const [a, b] = sel, alt = (met === "s" ? pearson : spearman)(R.map(r => r[a]), R.map(r => r[b]));
    el.querySelector(".ed-o").innerHTML = cifre([[`${SC[V[a]]} și ${SC[V[b]]}`, a === b ? "aceeași variabilă" : `${met === "s" ? "ρ" : "r"} = ${f(M[a][b])}`], [met === "s" ? "Pearson, pentru comparație" : "Spearman, pentru comparație", a === b ? "" : f(alt)], ["regiuni cu toate valorile", nr(R.length)]])
      + panou("Clic pe o căsuță, în oricare dintre matrice. Cu Pearson, scala densității schimbă coeficienții; cu Spearman, nu.");
  };
  leaga(el, "m", k => { met = k; deseneaza(); });
  el.querySelector(".ed-lg").addEventListener("click", e => { lg = !lg; e.target.classList.toggle("on", lg); deseneaza(); });
  deseneaza();
};


/* =========================================================================
   14. Tipar și reziduu: dreapta potrivită de mână (pentru C7; nu apare în C6)
   ========================================================================= */
E.edReziduu = (gazda, d) => {
  const P = (d.perechi || []).slice(0, 1500);
  const [A0, B0] = mcmmp(P.map(p => p[0]), P.map(p => p[1]));
  const SSmin = P.reduce((t, p) => t + (p[1] - A0 - B0 * p[0]) ** 2, 0);
  let a = d.a0 ?? 6, b = d.b0 ?? -1, seg = false;
  const DY = d.dy || [0, 6.6], ET2 = d.et || ["țări diferite", "aceeași țară (portocaliu)"];
  const el = bloc(gazda, `<div class="ed-ctl">${glisor("b", "panta", -3, 1, .02, b)}${glisor("a", "constanta (intercept)", 2, 10, .05, a)}<button class="ed-b ed-mp">cele mai mici pătrate</button><button class="ed-b ed-sg">reziduurile, ca segmente</button></div><div class="ed-g"></div><pre class="ed-cod"></pre><div class="ed-o"></div>`);
  const [ib, ia] = ["b", "a"].map(n => el.querySelector(`input[data-n="${n}"]`));
  const W = 900, x0 = 56, x1 = W - 16;
  const deseneaza = () => {
    const xs = P.map(p => p[0]), lo = Math.min(...xs), hi = Math.max(...xs), sx = sc(lo, hi, x0, x1), sy = sc(DY[0], DY[1], 168, 14);
    scrieCod(el, d.cod || `x, y = np.log10(perechi["distanta_km"]), np.log10(perechi["sci"])\npanta, nivel = np.polyfit(x, y, 1)              # cele mai mici pătrate\nperechi["reziduu"] = y - (nivel + panta * x)`);
    const res = P.map(p => p[1] - (a + b * p[0])), rm = d.rm || 3, sr = sc(-rm, rm, 290, 206);
    let s = axe({ x0, x1, y0: 14, y1: 168, sx, sy, dx: [lo, hi], dy: DY, fx: u => nr(10 ** u), fy: u => f(u, 0), ey: "SCI (log10)" });
    if (seg) P.slice(0, 200).forEach(p => s += `<line class="ed-l-obs" x1="${sx(p[0])}" x2="${sx(p[0])}" y1="${sy(p[1])}" y2="${sy(a + b * p[0])}"/>`);
    P.forEach(p => s += `<circle class="${p[2] ? "ed-sus" : "ed-p"} ed-mic" cx="${sx(p[0])}" cy="${sy(p[1])}" r="2"/>`);
    s += `<line class="ed-l-tot" x1="${sx(lo)}" x2="${sx(hi)}" y1="${sy(a + b * lo)}" y2="${sy(a + b * hi)}"/>`;
    s += axe({ x0, x1, y0: 206, y1: 290, sx, sy: sr, dx: [lo, hi], dy: [-rm, rm], ny: 2, fx: u => nr(10 ** u), fy: u => f(u, 0), ex: "distanța, km (scară log)", ey: "reziduul = SCI − dreapta (log10)" });
    s += `<line class="ed-l-adev" x1="${x0}" x2="${x1}" y1="${sr(0)}" y2="${sr(0)}"/>`;
    P.forEach((p, i) => s += `<circle class="${p[2] ? "ed-sus" : "ed-p"} ed-mic" cx="${sx(p[0])}" cy="${sr(Math.max(-rm, Math.min(rm, res[i])))}" r="1.8"/>`);
    el.querySelector(".ed-g").innerHTML = svg(W, 330, s);
    const r0 = res.filter((_, i) => !P[i][2]), r1 = res.filter((_, i) => P[i][2]), ss = res.reduce((t, e) => t + e * e, 0);
    el.querySelector(".ed-o").innerHTML = cifre([["suma pătratelor reziduurilor", f(ss, 0)], ["față de minimul posibil", `+${f(100 * (ss / SSmin - 1), 1)}%`, ss / SSmin < 1.005 ? "ed-c-adev" : ""],
      ["reziduul median, " + ET2[0], f(mediana(r0), 2)], ["reziduul median, " + ET2[1], f(mediana(r1), 2), "ed-c-sus"], ...(d.r2 ? [["R²", f(1 - ss / P.reduce((t, p, _, A) => t + (p[1] - medie(A.map(q => q[1]))) ** 2, 0), 2), "ed-c-m1"]] : [])])
      + panou("Panta și constanta se ajustează până când suma pătratelor nu mai scade; rezultatul se compară apoi cu metoda celor mai mici pătrate.");
    ib.nextElementSibling.textContent = f(b, 2); ia.nextElementSibling.textContent = f(a, 2);
  };
  ib.addEventListener("input", () => { b = +ib.value; deseneaza(); });
  ia.addEventListener("input", () => { a = +ia.value; deseneaza(); });
  el.querySelector(".ed-mp").addEventListener("click", () => { a = A0; b = B0; ib.value = b; ia.value = a; deseneaza(); });
  el.querySelector(".ed-sg").addEventListener("click", e => { seg = !seg; e.target.classList.toggle("on", seg); deseneaza(); });
  deseneaza();
};


/* =========================================================================
   16. Tipurile de grafice (după Wilke)
   ========================================================================= */
E.edTipGrafice = (gazda) => {
  const T = {
    cant: ["Cantități", "o valoare pe categorie", [["bare", "barplot, countplot"], ["puncte (dot plot)", "pointplot"], ["heatmap", "heatmap"]]],
    dist: ["Distribuții", "cum se repartizează o variabilă numerică", [["histogramă", "histplot"], ["densitate", "kdeplot"], ["ECDF", "ecdfplot"], ["boxplot", "boxplot"], ["violin", "violinplot"], ["puncte cu zgomot", "stripplot"]]],
    prop: ["Proporții", "părți dintr-un întreg", [["bare stivuite 100%", "crosstab(normalize=)"], ["bare alăturate", "barplot(hue=)"], ["mozaic", "statsmodels mosaic"], ["plăcintă (doar 2-3 părți)", "plt.pie"]]],
    rel: ["Relații x-y", "două sau mai multe variabile numerice", [["dispersie (scatter)", "scatterplot"], ["histogramă 2D, hexbin", "histplot(x=, y=)"], ["tendință netezită", "regplot(lowess=True)"], ["matricea de grafice", "pairplot"], ["matricea de corelație", "heatmap(df.corr())"], ["linie în timp", "lineplot"]]],
    geo: ["Date spațiale", "valori pe teritorii", [["hartă coropletă", "geopandas plot(column=)"], ["hartă pe categorii (comunități)", "plot(column=, categorical=True)"], ["linii între locuri (legături)", "ax.plot([x1, x2], [y1, y2])"], ["simboluri proporționale", "plot(markersize=)"]]],
    inc: ["Incertitudine", "cât de sigură e o estimare", [["bare de eroare", "pointplot(errorbar=)"], ["benzi de încredere", "lineplot(errorbar=)"], ["eșantioane bootstrap", "errorbar=('ci', 95)"]]] };
  let k = "dist";
  const el = bloc(gazda, butoane("t", Object.entries(T).map(([c, v]) => [c, v[0]]), k) + `<div class="ed-tg"></div>`);
  const deseneaza = () => { const [n, d, L] = T[k];
    el.querySelector(".ed-tg").innerHTML = `<p class="ed-not">${n}: ${d}</p><div class="ed-tg__l">${L.map(([g, c]) => `<div><b>${g}</b><code>${c}</code></div>`).join("")}</div>`; };
  leaga(el, "t", v => { k = v; deseneaza(); });
  deseneaza();
};

/* =========================================================================
   C7. Variabile derivate și model: componentele lecției 7
   Datele: d.tari = [tara_1, tara_2, sci, migranti, la_mie, distanta_km, granita, reziduu]
   ========================================================================= */
const TARI = d => (d.tari || []).map(r => ({ p: r[0] + "–" + r[1], sci: r[2], migr: r[3], rata: r[4], dist: r[5], gr: r[6], rez: r[7] }));
const L10 = Math.log10;

/* Un nor de puncte cu dreapta celor mai mici pătrate; x și y aleși prin butoane. */
E.edModelVar = (gazda, d) => {
  const T = TARI(d), mod = d.mod || "constr";
  const V = mod === "constr"
    ? { migr: { t: "numărul de migranți", x: r => L10(r.migr), y: r => L10(r.sci), ex: "migranți (scară log)", ey: "SCI (scară log)", lx: true, ly: true,
                cod: `m = smf.ols("log_sci ~ log_migranti", data=date).fit()\nm.rsquared` },
        rata: { t: "migranți la 1.000 de locuitori", x: r => L10(r.rata), y: r => L10(r.sci), ex: "migranți la mie (scară log)", ey: "SCI (scară log)", lx: true, ly: true,
                cod: `date["la_mie"] = 1000 * date["migranti"] / (date["tara_1"].map(pop) + date["tara_2"].map(pop))\nm = smf.ols("log_sci ~ log_la_mie", data=date).fit()\nm.rsquared` } }
    : { brut: { t: "valorile brute", x: r => r.dist, y: r => r.sci, ex: "distanța, km", ey: "SCI", lx: false, ly: false,
                cod: `sns.regplot(date, x="distanta_km", y="sci")\ndate["sci"].skew()` },
        log: { t: "logaritmul ambelor", x: r => L10(r.dist), y: r => L10(r.sci), ex: "distanța, km (scară log)", ey: "SCI (scară log)", lx: true, ly: true,
                cod: `date["log_sci"] = np.log10(date["sci"])\ndate["log_distanta"] = np.log10(date["distanta_km"])\nsns.regplot(date, x="log_distanta", y="log_sci")` } };
  let k = Object.keys(V)[0];
  const el = bloc(gazda, `<div class="ed-ctl">${butoane("v", Object.entries(V).map(([c, v]) => [c, v.t]), k)}</div><div class="ed-g"></div><pre class="ed-cod"></pre><div class="ed-o"></div>`);
  const W = 900, H = 250, x0 = 62, x1 = W - 16, y0 = 20, y1 = H - 40;
  const deseneaza = () => {
    const v = V[k], x = T.map(v.x), y = T.map(v.y);
    const lo = Math.min(...x), hi = Math.max(...x), ylo = Math.min(...y), yhi = Math.max(...y);
    const sx = sc(lo, hi, x0, x1), sy = sc(ylo, yhi, y1, y0), [a, b] = mcmmp(x, y), r = pearson(x, y);
    const fx = v.lx ? u => nr(10 ** u) : u => nr(u), fy = v.ly ? u => nr(10 ** u) : u => nr(u);
    let s = axe({ x0, x1, y0, y1, sx, sy, dx: [lo, hi], dy: [ylo, yhi], ex: v.ex, ey: v.ey, fx, fy });
    T.forEach((t, i) => s += `<circle class="${t.p.includes("RO") ? "ed-sus" : "ed-p"}" cx="${sx(x[i])}" cy="${sy(y[i])}" r="3.4"><title>${t.p}</title></circle>`);
    s += `<line class="ed-l-tot" x1="${sx(lo)}" x2="${sx(hi)}" y1="${sy(a + b * lo)}" y2="${sy(a + b * hi)}"/>`;
    el.querySelector(".ed-g").innerHTML = svg(W, H, s);
    scrieCod(el, v.cod);
    el.querySelector(".ed-o").innerHTML = cifre([["Pearson r", f(r), "ed-c-m1"], ["R² = r²", f(r * r), "ed-c-adev"], ["asimetria lui y", f(asimetrie(y))], ["perechi de țări", nr(x.length)]])
      + panou("Portocaliu: perechile cu România. Trecerea cu mouse-ul peste un punct arată perechea.");
  };
  leaga(el, "v", c => { k = c; deseneaza(); });
  deseneaza();
};

/* Scorul z: trei variabile pe scări diferite, apoi pe aceeași scară. */
E.edScalare = (gazda, d) => {
  const T = TARI(d);
  const V = [["log SCI", T.map(r => L10(r.sci))], ["log distanța", T.map(r => L10(r.dist))], ["log migranți la mie", T.map(r => L10(r.rata))]];
  const Z = V.map(([, a]) => { const m = medie(a), s = abatere(a); return a.map(x => (x - m) / s); });
  const z = a => { const m = medie(a), s = abatere(a); return a.map(x => (x - m) / s); };
  const ALESE = (d.alese || []).filter(p => T.some(t => t.p === p));
  let mod = d.mod0 || "brut", ales = ALESE[0] || null;
  const el = bloc(gazda, `<div class="ed-ctl">${butoane("m", [["brut", "valorile (log)"], ["z", "scorul z"]], mod)}${ALESE.length ? butoane("p", ALESE.map(p => [p, p]), ales) : ""}</div><div class="ed-g"></div><pre class="ed-cod"></pre><div class="ed-o"></div>`);
  const W = 900, x0 = 170, x1 = W - 20, rand = 62, H = 30 + rand * V.length + 30;
  const deseneaza = () => {
    const D = V.map(([n, a]) => [n, mod === "z" ? z(a) : a]), tot = D.flatMap(v => v[1]);
    const lo = Math.min(...tot), hi = Math.max(...tot), sx = sc(lo, hi, x0, x1);
    let s = axe({ x0, x1, y0: 10, y1: 20 + rand * V.length, sx, sy: v => v, dx: [lo, hi], ex: mod === "z" ? "abateri standard față de medie" : "valoarea, pe scara log10", fx: u => f(u, 1) });
    D.forEach(([n, a], j) => { const Y = 22 + rand * j + rand / 2, m = medie(a), sd = abatere(a);
      s += `<text class="ed-tx" x="${x0 - 12}" y="${Y + 4}" text-anchor="end">${n}</text>`;
      s += `<rect class="ed-cutie2" x="${sx(m - sd)}" y="${Y - 14}" width="${sx(m + sd) - sx(m - sd)}" height="28"/>`;
      a.forEach((x, i) => s += `<circle class="ed-p ed-mic" cx="${sx(x)}" cy="${Y + ((i * 37) % 21) - 10}" r="2.2"/>`);
      s += `<line class="ed-l-tot" x1="${sx(m)}" x2="${sx(m)}" y1="${Y - 18}" y2="${Y + 18}"/>`;
      const i = T.findIndex(t => t.p === ales);
      if (i >= 0){ const X = sx(a[i]), zz = Z[j][i];
        s += `<circle class="ed-pf" cx="${X}" cy="${Y}" r="7"/>`;
        s += `<text class="ed-gros" x="${X}" y="${Y - 22}" text-anchor="middle">${mod === "z" ? "z = " + (zz >= 0 ? "+" : "") + f(zz, 1) : f(a[i], 2)}</text>`; } });
    el.querySelector(".ed-g").innerHTML = svg(W, H, s);
    scrieCod(el, mod === "z" ? `def scor_z(x):\n    return (x - x.mean()) / x.std()\n\ndate["z_log_distanta"] = scor_z(date["log_distanta"])` : `date[["log_sci", "log_distanta", "log_la_mie"]].describe()`);
    const i = T.findIndex(t => t.p === ales), t = T[i];
    const semn = zz => (zz >= 0 ? "+" : "") + f(zz, 1);
    const cuvant = zz => Math.abs(zz) < 0.5 ? "obișnuită" : Math.abs(zz) < 1.5 ? (zz > 0 ? "peste medie" : "sub medie") : (zz > 0 ? "neobișnuit de mare" : "neobișnuit de mică");
    const pereche = i < 0 ? "" : `<p class="ed-rand"><b>${ales}</b>: ${nr(t.dist)} km, ${f(t.rata, 1)} migranți la mie. `
      + `Distanța are z = ${semn(Z[1][i])}: ${cuvant(Z[1][i])}. Rata migranților are z = ${semn(Z[2][i])}: ${cuvant(Z[2][i])}. `
      + `Pe scara inițială, kilometrii și migranții la mie nu se pot compara; în abateri standard, da.</p>`;
    el.querySelector(".ed-o").innerHTML = pereche + cifre(D.map(([n, a], j) => [n, `medie ${f(medie(a), 2)} · a.s. ${f(abatere(a), 2)} · asim. ${f(asimetrie(V[j][1]), 2)}`]))
      + panou("Linia: media; banda: o abatere standard în jurul ei; cercul: perechea aleasă. Scorul z mută și întinde fiecare variabilă, dar forma (asimetria) rămâne aceeași.");
  };
  leaga(el, "m", c => { mod = c; deseneaza(); });
  leaga(el, "p", c => { ales = c; deseneaza(); });
  deseneaza();
};

/* Cum construiește modelul predicția pentru o pereche: constanta, apoi
   contribuția fiecărui predictor, apoi comparația cu SCI-ul observat. */
E.edPredictie = (gazda, d) => {
  const T = TARI(d), M = d.modele, ALESE = (d.alese || []).filter(p => T.some(t => t.p === p));
  let ales = ALESE[0], mk = M.length - 1;
  const el = bloc(gazda, `<div class="ed-ctl">${butoane("p", ALESE.map(p => [p, p]), ales)}${butoane("m", M.map((m, k) => [String(k), m.nume]), String(mk))}</div><div class="ed-g"></div><pre class="ed-cod"></pre><div class="ed-o"></div>`);
  const W = 900, x0 = 330, x1 = W - 30, rand = 34, lo = 3, hi = 7;
  const sx = sc(lo, hi, x0, x1);
  const deseneaza = () => {
    const t = T.find(x => x.p === ales), b = M[mk].coef;
    const pasi = [["constanta", null, b.Intercept, "pornirea dreptei"]];
    pasi.push(["distanța", `${nr(t.dist)} km`, b.log_distanta * L10(t.dist), `${f(b.log_distanta, 2)} × log ${nr(t.dist)}`]);
    if (b.log_la_mie != null) pasi.push(["rata migranților", `${f(t.rata, 1)} la mie`, b.log_la_mie * L10(t.rata), `${f(b.log_la_mie, 2)} × log ${f(t.rata, 1)}`]);
    if (b.granita != null) pasi.push(["granița", t.gr ? "vecine" : "nevecine", b.granita * t.gr, `${f(b.granita, 2)} × ${t.gr}`]);
    let s = "", cum = lo, y = 6;
    repere(lo, hi, 4).forEach(v => s += `<line class="ed-grila" x1="${sx(v)}" x2="${sx(v)}" y1="0" y2="${rand * (pasi.length + 2) + 4}" stroke="var(--linie)"/><text class="ed-tx ed-tx--mic" x="${sx(v)}" y="${rand * (pasi.length + 2) + 18}" text-anchor="middle">SCI ${nr(10 ** v)}</text>`);
    pasi.forEach(([n, val, c, cal], j) => {
      const a = j === 0 ? lo : cum, z = j === 0 ? c : cum + c;
      s += `<text class="ed-tx" x="${x0 - 12}" y="${y + 21}" text-anchor="end"><tspan class="ed-gros">${n}</tspan>${val ? "  " + val : ""}</text>`;
      s += `<rect class="${j === 0 ? "ed-cutie" : c >= 0 ? "ed-bar" : "ed-bar2"}" x="${sx(Math.min(a, z))}" y="${y + 6}" width="${Math.max(2, Math.abs(sx(z) - sx(a)))}" height="22"/>`;
      s += `<text class="ed-tx ed-tx--mic" x="${sx(Math.max(a, z)) + 6}" y="${y + 21}">${j === 0 ? f(c, 2) : (c >= 0 ? "+" : "") + f(c, 2) + "  (" + cal + ")"}</text>`;
      cum = z; y += rand; });
    const obs = L10(t.sci), rez = obs - cum;
    s += `<text class="ed-tx" x="${x0 - 12}" y="${y + 21}" text-anchor="end"><tspan class="ed-gros">prezis</tspan>  SCI ${nr(10 ** cum)}</text>`;
    s += `<line class="ed-l-tot" x1="${sx(cum)}" x2="${sx(cum)}" y1="${y + 2}" y2="${y + 32}"/>`;
    y += rand;
    s += `<text class="ed-tx" x="${x0 - 12}" y="${y + 21}" text-anchor="end"><tspan class="ed-gros">observat</tspan>  SCI ${nr(t.sci)}</text>`;
    s += `<line class="ed-l-adev" x1="${sx(cum)}" x2="${sx(obs)}" y1="${y + 17}" y2="${y + 17}"/><circle class="ed-pf" cx="${sx(obs)}" cy="${y + 17}" r="7"/>`;
    s += `<text class="ed-gros" x="${Math.max(sx(cum), sx(obs)) + 14}" y="${y + 22}">reziduu: × ${f(10 ** rez, 2)}</text>`;
    el.querySelector(".ed-g").innerHTML = svg(W, rand * (pasi.length + 2) + 24, s);
    scrieCod(el, `rand = date[date["pereche"] == "${ales.replace("–", "-")}"]
${M[mk].var}.predict(rand)       # log SCI prezis: ${f(cum, 2)}
np.log10(rand["sci"])     # observat: ${f(obs, 2)}`);
    el.querySelector(".ed-o").innerHTML = panou(`Modelul nu știe nimic despre ${ales}: vede doar ${pasi.length - 1 === 1 ? "distanța" : "distanța, rata migranților și granița"}. `
      + `Predicția este suma barelor, pe scara log SCI. Perechea este ${10 ** rez >= 1 ? "de " + f(10 ** rez, 1) + " ori mai legată" : "de " + f(1 / 10 ** rez, 1) + " ori mai puțin legată"} decât prezice modelul: acesta este reziduul.`);
  };
  leaga(el, "p", c => { ales = c; deseneaza(); });
  leaga(el, "m", c => { mk = +c; deseneaza(); });
  deseneaza();
};

/* Rețeaua țărilor după model: o legătură între două țări dacă perechea e mult
   peste (sau sub) ce prezice M3. Nodurile stau pe hartă; trecerea cu mouse-ul
   peste o țară îi arată partenerii. */
E.edRetea = (gazda, d) => {
  const N = d.noduri, P = d.perechi, PR = [1.5, 2, 3];
  let sens = "peste", ip = 0, focus = null;
  const el = bloc(gazda, `<div class="ed-ctl">${butoane("s", [["peste", "mai legate decât prezice M3"], ["sub", "mai puțin legate"]], sens)}${glisor("p", "pragul", 0, 2, 1, 0)}</div><div class="ed-g ed-rt"></div><pre class="ed-cod"></pre><div class="ed-o"></div>`);
  const ipr = el.querySelector('input[data-n="p"]');
  const [vx, vy, vw, vh] = d.cutie, poz = Object.fromEntries(N.map(n => [n.c, n])), u = vw / 100;
  const deseneaza = () => {
    const prag = PR[ip], E2 = P.filter(([a, b, r]) => sens === "peste" ? 10 ** r >= prag : 10 ** r <= 1 / prag);
    const grad = {}; E2.forEach(([a, b]) => { grad[a] = (grad[a] || 0) + 1; grad[b] = (grad[b] || 0) + 1; });
    let s = `<g class="ed-rt__harta">${d.contur.map(p => `<path d="${p}"/>`).join("")}</g>`;
    E2.forEach(([a, b, r]) => { const A = poz[a], B = poz[b]; if (!A || !B) return;
      const mx = (A.x + B.x) / 2 - (B.y - A.y) * 0.15, my = (A.y + B.y) / 2 + (B.x - A.x) * 0.15;
      const on = !focus || focus === a || focus === b;
      s += `<path class="ed-rt__l ${sens} ${on ? "" : "stins"}" d="M${A.x},${A.y} Q${mx},${my} ${B.x},${B.y}" style="stroke-width:${(u * (0.3 + Math.abs(r) * 1.4)).toFixed(1)}"><title>${a}–${b}: × ${f(10 ** r, 2)}</title></path>`; });
    N.forEach(n => { const g = grad[n.c] || 0, on = !focus || focus === n.c || E2.some(([a, b]) => (a === focus && b === n.c) || (b === focus && a === n.c));
      s += `<g class="ed-rt__n ${on ? "" : "stins"}" data-c="${n.c}"><circle cx="${n.x}" cy="${n.y}" r="${(u * (1.5 + g * 0.35)).toFixed(1)}" style="stroke-width:${(u * 0.18).toFixed(1)}"/><text x="${n.x}" y="${n.y + u * 0.6}" text-anchor="middle" style="font-size:${(u * 1.6).toFixed(1)}px">${n.c}</text></g>`; });
    el.querySelector(".ed-g").innerHTML = `<svg class="ed-svg ed-rt__svg" viewBox="${vx} ${vy} ${vw} ${vh}" preserveAspectRatio="xMidYMid meet">${s}</svg>`;
    el.querySelectorAll(".ed-rt__n").forEach(g => { g.addEventListener("pointerenter", () => { focus = g.dataset.c; deseneaza(); });
      g.addEventListener("pointerleave", () => { focus = null; deseneaza(); }); });
    ipr.nextElementSibling.textContent = `× ${f(prag, 1)}`;
    const top = [...E2].sort((x, y) => sens === "peste" ? y[2] - x[2] : x[2] - y[2]).slice(0, 5)
      .map(([a, b, r]) => `${a}–${b} (× ${f(10 ** r, 2)})`).join(", ");
    const inF = focus ? E2.filter(([a, b]) => a === focus || b === focus).map(([a, b, r]) => `${a === focus ? b : a} × ${f(10 ** r, 2)}`).join(", ") : "";
    el.querySelector(".ed-o").innerHTML = cifre([["legături", nr(E2.length)], ["țări cu cel puțin o legătură", nr(Object.keys(grad).length)]])
      + panou(focus ? `<b>${focus}</b>: ${inF || "nicio legătură la acest prag"}.` : `Cele mai ${sens === "peste" ? "puternice" : "slabe"}: ${top}. Cu mouse-ul pe o țară, partenerii ei.`);
    scrieCod(el, `date["reziduu_m3"] = m3.resid\n${sens === "peste" ? `legate = date[10 ** date["reziduu_m3"] >= ${String(prag)}]` : `legate = date[10 ** date["reziduu_m3"] <= 1 / ${String(prag)}]`}   # perechile ${sens} model\nR = nx.from_pandas_edgelist(legate, "tara_1", "tara_2")\ndict(R.degree())                      # câte legături are fiecare țară`);
  };
  leaga(el, "s", c => { sens = c; focus = null; deseneaza(); });
  ipr.addEventListener("input", () => { ip = +ipr.value; deseneaza(); });
  deseneaza();
};

/* Elasticitățile modelului M4: cu cât se schimbă SCI-ul prezis. */
E.edElasticitate = (gazda, d) => {
  const b = d.coef, F = [0.25, 0.5, 1, 2, 4];
  let fd = 2, fr = 2, gr = 0;
  const el = bloc(gazda, `<div class="ed-ctl">${glisor("d", "distanța ×", 0, 4, 1, 3)}${glisor("r", "rata migranților ×", 0, 4, 1, 3)}<button class="ed-b ed-gr">graniță comună</button></div><div class="ed-g"></div><pre class="ed-cod"></pre><div class="ed-o"></div>`);
  const [id, ir] = ["d", "r"].map(n => el.querySelector(`input[data-n="${n}"]`));
  const W = 900, H = 186, x0 = 270, x1 = W - 120, rand = 40;
  const fmt = v => (v >= 1 ? "+" : "−") + f(Math.abs(v - 1) * 100, 0) + "%";
  const deseneaza = () => {
    const md = fd ** b.log_distanta, mr = fr ** b.log_la_mie, mg = 10 ** (b.granita * gr), tot = md * mr * mg;
    const R = [[`distanța × ${f(fd, fd < 1 ? 2 : 0)}  (coef. ${f(b.log_distanta, 2)})`, md], [`rata migranților × ${f(fr, fr < 1 ? 2 : 0)}  (coef. ${f(b.log_la_mie, 2)})`, mr], [`granița: ${gr ? "comună" : "nu"}  (coef. ${f(b.granita, 2)})`, mg], ["împreună", tot]];
    const lim = Math.max(2, ...R.map(r => Math.max(r[1], 1 / r[1]))), sx = sc(-Math.log(lim), Math.log(lim), x0, x1);
    let s = `<line class="ed-l-adev" x1="${sx(0)}" x2="${sx(0)}" y1="8" y2="${H - 24}"/><text class="ed-tx" x="${sx(0)}" y="${H - 8}" text-anchor="middle">SCI neschimbat (× 1)</text>`;
    R.forEach(([n, v], j) => { const Y = 12 + rand * j, a = sx(0), c = sx(Math.log(v));
      s += `<text class="ed-tx" x="${x0 - 12}" y="${Y + 20}" text-anchor="end">${n}</text>`;
      s += `<rect class="${v >= 1 ? "ed-bar" : "ed-bar2"}" x="${Math.min(a, c)}" y="${Y + 6}" width="${Math.max(1, Math.abs(c - a))}" height="${j === 3 ? 24 : 20}"/>`;
      s += `<text class="ed-tx" x="${Math.max(a, c) + 8}" y="${Y + 21}">SCI × ${f(v, 2)} (${fmt(v)})</text>`; });
    el.querySelector(".ed-g").innerHTML = svg(W, H, s);
    scrieCod(el, `b = m4.params\n${f(fd, 2).replace(",", ".")} ** b["log_distanta"]     # ${f(md, 2)}\n${f(fr, 2).replace(",", ".")} ** b["log_la_mie"]       # ${f(mr, 2)}\n10 ** b["granita"]              # ${f(10 ** b.granita, 2)}`);
    el.querySelector(".ed-o").innerHTML = panou("Pe logaritmi, efectele se înmulțesc: distanța de două ori mai mare și rata de două ori mai mare dau împreună produsul celor două.");
    id.nextElementSibling.textContent = "× " + f(fd, fd < 1 ? 2 : 0); ir.nextElementSibling.textContent = "× " + f(fr, fr < 1 ? 2 : 0);
  };
  id.addEventListener("input", () => { fd = F[+id.value]; deseneaza(); });
  ir.addEventListener("input", () => { fr = F[+ir.value]; deseneaza(); });
  el.querySelector(".ed-gr").addEventListener("click", e => { gr = 1 - gr; e.target.classList.toggle("on", !!gr); deseneaza(); });
  deseneaza();
};

/* k-means pe două variabile ale regiunilor: cu sau fără scorul z, k ales. */
E.edKmeans = (gazda, d) => {
  const R = (d.reg || []).map(r => ({ cod: r[0], tara: r[1], nume: r[2], x: r[3], y: r[4] }));
  let k = 4, mod = "z";
  const el = bloc(gazda, `<div class="ed-ctl">${butoane("m", [["brut", "valorile inițiale"], ["z", "scorul z"]], mod)}${glisor("k", "grupe, k", 2, 6, 1, k)}</div><div class="ed-g"></div><pre class="ed-cod"></pre><div class="ed-o"></div>`);
  const ik = el.querySelector('input[data-n="k"]');
  const zs = a => { const m = medie(a), s = abatere(a); return a.map(v => (v - m) / s); };
  const kmeans = (P, k) => { let best = null; const r = rng(7);
    for (let t = 0; t < 12; t++){
      let C = [P[Math.floor(r() * P.length)]];
      while (C.length < k){ const D = P.map(p => Math.min(...C.map(c => (p[0] - c[0]) ** 2 + (p[1] - c[1]) ** 2))), S = D.reduce((a, b) => a + b, 0);
        let u = r() * S, i = 0; while (u > D[i] && i < D.length - 1){ u -= D[i]; i++; } C.push(P[i]); }
      let L = [];
      for (let it = 0; it < 100; it++){
        L = P.map(p => { let b = 0, bd = 1e99; C.forEach((c, j) => { const dd = (p[0] - c[0]) ** 2 + (p[1] - c[1]) ** 2; if (dd < bd){ bd = dd; b = j; } }); return b; });
        const C2 = C.map((c, j) => { const M = P.filter((_, i) => L[i] === j); return M.length ? [medie(M.map(m => m[0])), medie(M.map(m => m[1]))] : c; });
        const gata = C2.every((c, j) => c[0] === C[j][0] && c[1] === C[j][1]); C = C2; if (gata) break; }
      const inn = P.reduce((s, p, i) => s + (p[0] - C[L[i]][0]) ** 2 + (p[1] - C[L[i]][1]) ** 2, 0);
      if (!best || inn < best.inn) best = { inn, L, C }; }
    return best; };
  const W = 900, H = 228, x0 = 62, x1 = W - 16, y0 = 20, y1 = H - 40;
  const deseneaza = () => {
    const X = R.map(r => r.x), Y = R.map(r => r.y);
    const P = mod === "z" ? (() => { const a = zs(X), b = zs(Y); return a.map((v, i) => [v, b[i]]); })() : X.map((v, i) => [v, Y[i]]);
    const { L } = kmeans(P, k);
    const sx = sc(0, Math.max(...X) * 1.02, x0, x1), sy = sc(0, Math.max(...Y) * 1.05, y1, y0);
    let s = axe({ x0, x1, y0, y1, sx, sy, dx: [0, Math.max(...X) * 1.02], dy: [0, Math.max(...Y) * 1.05], ex: "PIB pe locuitor (euro)", ey: "studii superioare (%)", fx: u => nr(u), fy: u => f(u, 0) });
    R.forEach((r, i) => s += `<circle cx="${sx(r.x)}" cy="${sy(r.y)}" r="3.4" style="fill:var(--cat-${L[i] + 1});fill-opacity:.85"><title>${r.nume} (${r.tara})</title></circle>`);
    el.querySelector(".ed-g").innerHTML = svg(W, H, s);
    scrieCod(el, mod === "z"
      ? `z = (reg[indicatori] - reg[indicatori].mean()) / reg[indicatori].std()\ngrupare = KMeans(n_clusters=${k}, n_init=10, random_state=1).fit(z)\nreg["grupa"] = grupare.labels_`
      : `grupare = KMeans(n_clusters=${k}, n_init=10, random_state=1).fit(reg[indicatori])   # fără scorul z\nreg["grupa"] = grupare.labels_`);
    const G = [...Array(k).keys()].map(j => { const ix = L.map((l, i) => l === j ? i : -1).filter(i => i >= 0);
      return [`${j + 1}`, `${ix.length} reg. · ${nr(mediana(ix.map(i => X[i])))} € · ${f(mediana(ix.map(i => Y[i])), 0)}%`, ""]; });
    el.querySelector(".ed-o").innerHTML = cifre(G).replace(/<span class="">/g, (m => { let j = 0; return () => `<span class="ed-k" style="--kc:var(--cat-${++j})">`; })())
      + panou(mod === "z" ? "Cu scorul z, ambii indicatori cântăresc la fel: grupele se formează pe diagonală." : "Fără scorul z, PIB-ul (zeci de mii) domină distanța: grupele sunt felii verticale, după PIB.");
    ik.nextElementSibling.textContent = k;
  };
  leaga(el, "m", c => { mod = c; deseneaza(); });
  ik.addEventListener("input", () => { k = +ik.value; deseneaza(); });
  deseneaza();
};

/* Ieșirea lui summary(), cu explicația fiecărui câmp la clic. */
E.edSumar = (gazda, d) => {
  const X = d.expl || {};
  const linii = (d.linii || []).map(l => l.map(([t, k]) => k ? `<span class="ed-sm__k" data-k="${k}" tabindex="0">${t}</span>` : t).join("")).join("\n");
  const el = bloc(gazda, `<div class="ed-sm"><pre class="ed-sm__p">${linii}</pre><div class="ed-sm__x"></div></div>`);
  const arata = k => { const [t, v, x] = X[k];
    el.querySelectorAll(".ed-sm__k").forEach(s => s.classList.toggle("on", s.dataset.k === k));
    el.querySelector(".ed-sm__x").innerHTML = `<b>${t}</b><span class="ed-sm__v">${v}</span><p>${x}</p>`; };
  el.querySelectorAll(".ed-sm__k").forEach(s => { s.addEventListener("click", () => arata(s.dataset.k)); s.addEventListener("keydown", e => { if (e.key === "Enter") arata(s.dataset.k); }); });
  arata(d.prim || Object.keys(X)[0]);
};

/* Observat față de prezis, pentru M2, M3 și M4. Banda arată perechile prezise
   cu o eroare sub ×1,5; la schimbarea modelului, punctele se mută spre diagonală. */
E.edObsPrez = (gazda, d) => {
  const P = d.op, MOD = [["M2", 2], ["M3", 3], ["M4", 4]], B = Math.log10(1.5);
  let mk = d.start || 0;
  const el = bloc(gazda, `<div class="ed-ctl">${butoane("m", MOD.map(([n], k) => [String(k), n]), String(mk))}</div><div class="ed-g ed-op"></div><pre class="ed-cod"></pre><div class="ed-o"></div>`);
  const W = 540, H = 440, x0 = 50, x1 = W - 14, y0 = 24, y1 = H - 44, lo = 2.8, hi = 6.2;
  const sx = sc(lo, hi, x0, x1), sy = sc(lo, hi, y1, y0), id = "op" + Math.random().toString(36).slice(2, 8);
  const ban = [[lo - 1, lo - 1 + B], [hi + 1, hi + 1 + B], [hi + 1, hi + 1 - B], [lo - 1, lo - 1 - B]].map(([a, b]) => `${sx(a)},${sy(b)}`).join(" ");
  let s = `<defs><clipPath id="${id}"><rect x="${x0}" y="${y0}" width="${x1 - x0}" height="${y1 - y0}"/></clipPath></defs>`;
  s += axe({ x0, x1, y0, y1, sx, sy, dx: [lo, hi], dy: [lo, hi], fx: v => f(v, 1), fy: v => f(v, 1), ex: "log SCI prezis de model", ey: "log SCI observat" });
  s += `<g clip-path="url(#${id})"><polygon class="ed-op__banda" points="${ban}"/><line class="ed-op__diag" x1="${sx(lo)}" y1="${sy(lo)}" x2="${sx(hi)}" y2="${sy(hi)}"/></g>`;
  s += `<text class="ed-tx ed-tx--mic" x="${sx(hi) - 4}" y="${sy(hi) + 34}" text-anchor="end">banda ×1,5</text>`;
  s += `<g class="ed-op__p">${P.map(p => `<circle r="4.2"><title></title></circle>`).join("")}</g><g class="ed-op__e"></g>`;
  el.querySelector(".ed-g").innerHTML = svg(W, H, s);
  const C = [...el.querySelectorAll(".ed-op__p circle")], ET = el.querySelector(".ed-op__e");
  const stat = k => { const o = P.map(p => p[1]), r = P.map(p => p[1] - p[k]), mo = medie(o);
    const ss = r.reduce((a, x) => a + x * x, 0), st = o.reduce((a, x) => a + (x - mo) ** 2, 0);
    return { r2: 1 - ss / st, ori: 10 ** abatere(r), banda: r.filter(x => Math.abs(x) < B).length / r.length, r }; };
  const S = MOD.map(([, k]) => stat(k));
  const TEXT = [
    "Distanța, rata migranților și granița. Norul de puncte e larg: multe perechi stau departe de diagonală.",
    "Plus efectele de țară: fiecare țară primește nivelul ei. Norul se strânge pe diagonală.",
    "Numărul de migranți în locul ratei și fostul stat comun. Aproape toate perechile intră în bandă; rămân departe câteva legături cu o poveste proprie."];
  const COD = [
    `formula_m2 = ("log_sci ~ log_distanta"\n              " + log_la_mie + granita")\nm2 = smf.ols(formula_m2, data=date).fit()\n\n# prezis (orizontal), observat (vertical)\nplt.scatter(m2.fittedvalues, date["log_sci"])\n10 ** m2.resid.std()     # × ${f(S[0].ori, 2)}`,
    `# formula lui M2, plus variabilele de țară\nm3 = smf.ols(formula_m2 + efecte,\n             data=date).fit()\n\nplt.scatter(m3.fittedvalues, date["log_sci"])\n10 ** m3.resid.std()     # × ${f(S[1].ori, 2)}`,
    `formula_m4 = ("log_sci ~ log_distanta"\n              " + log_migranti + granita"\n              " + stat_comun" + efecte)\nm4 = smf.ols(formula_m4, data=date).fit()\n\nplt.scatter(m4.fittedvalues, date["log_sci"])\n10 ** m4.resid.std()     # × ${f(S[2].ori, 2)}`];
  const deseneaza = () => {
    const k = MOD[mk][1], st = S[mk];
    C.forEach((c, i) => { const p = P[i], r = p[1] - p[k];
      c.style.transform = `translate(${sx(p[k]).toFixed(1)}px,${sy(p[1]).toFixed(1)}px)`;
      c.setAttribute("class", Math.abs(r) < B ? "" : r > 0 ? "peste" : "sub");
      c.firstChild.textContent = `${p[0]}: observat ${f(p[1], 2)}, prezis ${f(p[k], 2)}, × ${f(10 ** r, 2)}`; });
    const ord = P.map((p, i) => [i, p[1] - p[k]]).sort((a, b) => b[1] - a[1]), alese = [...ord.slice(0, 3), ...ord.slice(-2)];
    let ultim = { 1: -99, 0: -99 };
    ET.innerHTML = alese.map(([i, r]) => [i, r, sy(P[i][1])]).sort((a, b) => a[2] - b[2]).map(([i, r, Y]) => { const p = P[i], X = sx(p[k]), sus = r > 0 ? 1 : 0;
      if (Y - ultim[sus] < 20) Y = ultim[sus] + 20; ultim[sus] = Y;
      return `<text class="ed-op__et" x="${sus ? X - 9 : X + 9}" y="${Y + 4}" text-anchor="${sus ? "end" : "start"}">${p[0]} ×${f(10 ** r, 1)}</text>`; }).join("");
    ET.classList.remove("apare"); void ET.getBBox; requestAnimationFrame(() => ET.classList.add("apare"));
    el.querySelector(".ed-o").innerHTML = cifre([["R²", f(st.r2, 2)], ["greșește de obicei", "× " + f(st.ori, 2)], ["perechi în bandă", f(100 * st.banda, 0) + "%"]])
      + panou(TEXT[mk]);
    scrieCod(el, COD[mk]);
  };
  leaga(el, "m", c => { mk = +c; deseneaza(); });
  deseneaza();
};

/* Regresia QAP: coeficientul real față de 1.000 de coeficienți obținuți
   amestecând numele țărilor. */
E.edQAP = (gazda, d) => {
  const Q = d.qap, V = [["log_distanta", "distanța"], ["log_la_mie", "rata migranților"], ["granita", "granița"]], T = d.tari;
  let v = "log_la_mie", nr_am = 1;
  const el = bloc(gazda, `<div class="ed-ctl">${butoane("v", V, v)}<button class="ed-b" data-a="1">o amestecare</button></div><div class="ed-g"></div><p class="ed-rand ed-qap__am"></p><pre class="ed-cod"></pre><div class="ed-o"></div>`);
  const W = 620, H = 260, x0 = 30, x1 = W - 20, y0 = 30, y1 = H - 44;
  const amesteca = () => { const r = rng(nr_am++), a = [...T]; for (let i = a.length - 1; i > 0; i--){ const j = Math.floor(r() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; }
    const m = Object.fromEntries(T.map((t, i) => [t, a[i]])), ex = ["AT", "RO", "IT", "DE"].filter(t => T.includes(t));
    el.querySelector(".ed-qap__am").innerHTML = `O amestecare: ${ex.map(t => `${t} → <b>${m[t]}</b>`).join(", ")}, … Perechea AT–RO primește SCI-ul perechii <b>${[m.AT, m.RO].sort().join("–")}</b>; distanța, migrația și granița rămân ale perechii AT–RO.`; };
  const deseneaza = () => {
    const q = Q[v], n = q.h.length, w = (q.hi - q.lo) / n, sx = sc(q.lo, q.hi, x0, x1), mx = Math.max(...q.h), sy = sc(0, mx, y1, y0), R = Math.abs(q.real);
    let s = axe({ x0, x1, y0, y1, sx, sy, dx: [q.lo, q.hi], fx: v => f(v, 1), ex: "coeficientul în cele 1.000 de amestecări" });
    q.h.forEach((c, i) => { const a = q.lo + i * w, mij = a + w / 2;
      s += `<rect class="${Math.abs(mij) >= R ? "ed-bar2" : "ed-plin"}" x="${sx(a) + 0.5}" y="${sy(c)}" width="${Math.max(1, sx(a + w) - sx(a) - 1)}" height="${y1 - sy(c)}"/>`; });
    s += `<line class="ed-l-tot" x1="${sx(q.real)}" x2="${sx(q.real)}" y1="${y0 - 14}" y2="${y1}"/><text class="ed-gros" x="${sx(q.real) + (q.real > 0 ? -6 : 6)}" y="${y0 - 18}" text-anchor="${q.real > 0 ? "end" : "start"}">M2: ${f(q.real, 2)}</text>`;
    s += `<line class="ed-l-tot ed-qap__opus" x1="${sx(-q.real)}" x2="${sx(-q.real)}" y1="${y0}" y2="${y1}"/>`;
    el.querySelector(".ed-g").innerHTML = svg(W, H, s);
    const k = Math.round(q.p * 1000), trece = q.p < 0.05;
    el.querySelector(".ed-o").innerHTML = cifre([["coeficientul real", f(q.real, 2)], ["amestecări cel puțin la fel de departe de 0", nr(k) + " din 1.000"], ["p QAP", q.p < 0.001 ? "< 0,001" : f(q.p, 2)]])
      + panou(trece ? `Nicio amestecare nu dă un coeficient atât de mare: asocierea cu ${V.find(x => x[0] === v)[1]} nu ține de structura rețelei.`
        : `În ${f(100 * q.p, 0)}% dintre amestecări coeficientul iese cel puțin la fel de departe de 0 (barele portocalii): în rețea, efectul ${v === "granita" ? "graniței" : "distanței"} nu se deosebește de întâmplare.`);
    scrieCod(el, `real = abs(m2.params["${v}"])                   # coeficientul din M2: ${f(R, 2)}\namestecat = amestecati["${v}"].abs()           # cei 1.000 de coeficienți amestecați\n(amestecat >= real).mean()                     # p QAP: ${q.p < 0.001 ? "0,0" : f(q.p, 3)}`);
  };
  leaga(el, "v", c => { v = c; deseneaza(); });
  el.querySelector('[data-a="1"]').addEventListener("click", amesteca);
  amesteca(); deseneaza();
};

/* Comunitățile Louvain pe rețeaua regiunilor: pe SCI (C6) și peste model, cu
   rezoluția aleasă. Scheletul desenat: arborele legăturilor celor mai puternice,
   plus cele 4 legături cele mai puternice ale fiecărei regiuni. */
E.edComunitati = (gazda, d) => {
  const R = d.retea, N = R.noduri, NUME = d.nume || [], PAL = [...(d.culori || []), "#76b7b2", "#edc948", "#ff9da7", "#9c755f", "#bab0ac", "#86bcb6", "#d37295", "#a0cbe8", "#8cd17d", "#f1ce63", "#499894"];
  let mod = "model", rez = "1", focus = null;
  const ETR = { RO42: ["Vest", 16, 10, "start"], RO12: ["Centru", -16, -10, "end"], RO32: ["București", 16, 10, "start"] };
  const el = bloc(gazda, `<div class="ed-ctl">${butoane("r", [["brut", "rețeaua pe SCI (C6)"], ["model", "rețeaua peste model"]], mod)}<span class="ed-cm__z"><span>rezoluția</span>${butoane("z", [["0.75", "0,75"], ["1", "1"], ["1.25", "1,25"], ["1.5", "1,5"]], rez)}</span></div><div class="ed-g ed-cm"></div><div class="ed-cm__leg"></div><p class="ed-rand ed-cm__info">Mouse-ul pe o regiune: numele și comunitatea ei.</p><pre class="ed-cod"></pre><div class="ed-o"></div>`);
  const pad = 30, VW = 1000 + 2 * pad, VH = 880 + 2 * pad;
  let s = `<g class="ed-cm__m"></g><g class="ed-cm__n">${N.map(n => `<circle r="${n[2] === "RO" ? 11 : 7.5}" class="${n[2] === "RO" ? "ro" : ""}"><title>${n[1]} (${n[2]})</title></circle>`).join("")}</g><g class="ed-cm__e"></g>`;
  el.querySelector(".ed-g").innerHTML = `<svg class="ed-svg ed-cm__svg" viewBox="${-pad} ${-pad} ${VW} ${VH}" preserveAspectRatio="xMidYMid meet">${s}</svg>`;
  const C = [...el.querySelectorAll(".ed-cm__n circle")], G = el.querySelector(".ed-cm__m"), ET = el.querySelector(".ed-cm__e");
  const com = () => mod === "brut" ? R.brut.c : R.model.c[rez];
  const deseneaza = () => {
    const L = R[mod], c = com(), dx = (1000 - L.w) / 2, dy = (880 - L.h) / 2;
    G.innerHTML = L.m.map(([a, b]) => `<line x1="${L.p[a][0] + dx}" y1="${L.p[a][1] + dy}" x2="${L.p[b][0] + dx}" y2="${L.p[b][1] + dy}"/>`).join("");
    G.classList.remove("apare"); requestAnimationFrame(() => G.classList.add("apare"));
    C.forEach((el2, i) => { el2.style.transform = `translate(${L.p[i][0] + dx}px,${L.p[i][1] + dy}px)`; el2.style.fill = PAL[c[i] % PAL.length];
      el2.classList.toggle("stins", focus !== null && c[i] !== focus); el2.dataset.c = c[i]; el2.dataset.i = i; });
    // etichetele: regiunile României
    ET.innerHTML = N.map((n, i) => { const e = mod === "brut" ? (n[0] === "RO32" ? ["România", 16, 10, "start"] : null) : ETR[n[0]]; return e ? `<text x="${L.p[i][0] + dx + e[1]}" y="${L.p[i][1] + dy + e[2]}" text-anchor="${e[3]}">${e[0]}</text>` : ""; }).join("");
    ET.classList.remove("apare"); requestAnimationFrame(() => ET.classList.add("apare"));
    el.querySelector(".ed-cm__z").classList.toggle("stins", mod === "brut");
    const k = new Set(c).size, st = mod === "brut" ? null : d.stat[rez];
    el.querySelector(".ed-cm__leg").innerHTML = mod === "model" && rez === "1"
      ? NUME.map((t, j) => `<span data-c="${j}"><i style="background:${PAL[j]}"></i>${t}</span>`).join("")
      : `<span class="ed-cm__nr">${mod === "brut" ? "Culorile: cele " + k + " comunități pe SCI, aproape fiecare o țară." : "Culorile: cele " + k + " comunități la rezoluția " + rez.replace(".", ",") + "; o comunitate apropiată de una de la rezoluția 1 îi păstrează culoarea."}</span>`;
    el.querySelectorAll(".ed-cm__leg span[data-c]").forEach(sp => { sp.addEventListener("pointerenter", () => { focus = +sp.dataset.c; stinge(); }); sp.addEventListener("pointerleave", () => { focus = null; stinge(); }); });
    el.querySelector(".ed-o").innerHTML = cifre(mod === "brut"
      ? [["comunități", nr(d.brut_stat[0])], ["ARI cu țara", f(d.brut_stat[1], 2)]]
      : [["comunități", nr(st[0])], ["stabilitatea (ARI între rulări)", f(st[1], 2)], ["ARI cu țara", f(st[2], 2)]])
      + panou(mod === "brut" ? "Pe SCI, legăturile din interiorul țării sunt de zeci de ori mai puternice: rețeaua se strânge în ciorchini, aproape fiecare o țară (ARI cu țara 0,76)."
        : rez === "1" ? "Cinci comunități, cea mai stabilă împărțire. Regiunile României se despart: Vestul și Centrul merg cu spațiul dunărean, celelalte cu blocul latin (Italia, Spania)."
        : +rez < 1 ? "Rezoluție mică: comunități puține și mari. Stabilitatea scade față de rezoluția 1."
        : "Rezoluție mare: comunitățile se sparg și se apropie din nou de țări (ARI cu țara crește), iar stabilitatea scade.");
    scrieCod(el, mod === "brut"
      ? `# greutatea legăturii: SCI, ca în C6\nG_sci = nx.from_pandas_edgelist(\n    perechi, "regiune_1", "regiune_2",\n    edge_attr="sci")\ncomunitati_sci = louvain(G_sci, "sci")\nadjusted_rand_score(tara_regiunii,\n                    comunitati_sci)`
      : `# de câte ori peste modelul de bază\nperechi["peste_model"] = 10 ** m_regiuni.resid\nG_peste = nx.from_pandas_edgelist(\n    perechi, "regiune_1", "regiune_2",\n    edge_attr="peste_model")\ncomunitati = louvain(G_peste, "peste_model",\n                     rezolutie=${rez})`);
  };
  const numeCom = j => mod === "model" && rez === "1" && NUME[j] ? NUME[j] : `comunitatea ${j + 1}`;
  const INFO = el.querySelector(".ed-cm__info");
  const stinge = () => C.forEach(x => x.classList.toggle("stins", focus !== null && +x.dataset.c !== focus));
  C.forEach(x => { x.addEventListener("pointerenter", () => { focus = +x.dataset.c; stinge(); const n = N[+x.dataset.i];
      INFO.innerHTML = `<b>${n[1]}</b> (${n[2]}) · ${numeCom(focus)}`; });
    x.addEventListener("pointerleave", () => { focus = null; stinge(); }); });
  leaga(el, "r", c => { mod = c; focus = null; deseneaza(); });
  leaga(el, "z", c => { rez = c; if (mod === "brut"){ mod = "model"; el.querySelectorAll('.ed-bt[data-n="r"] button').forEach(b => b.classList.toggle("on", b.dataset.k === "model")); } focus = null; deseneaza(); });
  deseneaza();
};

export default E;
