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
  varsta_medie: "vârsta medie", densitate: "densitatea (loc./km²)", retele_sociale: "rețele sociale (%)", deschidere: "deschiderea spre străinătate", est: "est (km)" };
const panou = t => `<p class="ed-not">${t}</p>`;
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
  const R = REG(d), V = ["populatie", "pib_locuitor", "studii_superioare", "somaj", "varsta_medie", "densitate", "retele_sociale"];
  let mod = "harta", ord = "tara", ales = "retele_sociale", mec = "mcar";
  const el = bloc(gazda, `<div class="ed-ctl">${butoane("m", [["harta", "harta lipsurilor"], ["sim", "simularea mecanismelor"]], mod)}
    <span class="ed-h1">${butoane("o", [["tara", "ordonate după țară"], ["rand", "în ordine întâmplătoare"]], ord)}</span>
    <span class="ed-h2">${butoane("k", [["mcar", "complet aleator"], ["mar", "după țară"], ["mnar", "după valoarea însăși"]], mec)}${glisor("p", "proporția lipsă", 0, .6, .05, .3)}</span></div><div class="ed-g"></div><div class="ed-o"></div>`);
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
  const el = bloc(gazda, `<div class="ed-ctl">${glisor("k", "perechi cu valori foarte mari adăugate", 0, TOP.length, 1, 0)}</div><div class="ed-g"></div><div class="ed-o"></div>`);
  const ik = el.querySelector("input");
  const deseneaza = () => {
    const k = +ik.value; ik.nextElementSibling.textContent = `${k} din ${TOP.length}`;
    const v = [...B, ...TOP.slice(0, k)], L = sc(0, 6.8, x0, x1), sx = x => L(Math.log10(Math.max(1, x)));
    const M = [["media", medie(v), "ed-m1"], ["mediana", mediana(v), "ed-m3"]];
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
    <div class="ed-ctl ed-gls">${glisor("b", "bare", 3, 60, 1, 14)}${glisor("o", "începutul barelor", 0, 1, .05, 0)}${glisor("h", "netezirea", .02, .4, .01, .08)}</div><div class="ed-g"></div><div class="ed-o"></div>`);
  const [ib, io, ih] = ["b", "o", "h"].map(n => el.querySelector(`input[data-n="${n}"]`));
  const W = 900, H = 220, x0 = 50, x1 = W - 16, y0 = 18, y1 = H - 40;
  const kde = (v, lo, hi, h) => { const bw = h * (hi - lo), n = 160, rez = [];
    for (let i = 0; i <= n; i++){ const x = lo + (hi - lo) * i / n; let s = 0;
      for (const u of v) s += Math.exp(-.5 * ((x - u) / bw) ** 2); rez.push([x, s / (v.length * bw * 2.5066)]); } return rez; };
  const deseneaza = () => {
    const [v, ex] = variabila(d, set); if (!v.length) return;
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
      let t = [["valoarea", fx(u)], ["valori ≤ prag", `${nr(sub)} din ${nr(o.length)} (${f(100 * sub / o.length, 1)}%)`]];
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
  const el = bloc(gazda, `<div class="ed-ctl">${butoane("s", [["sci", "SCI"], ["pop", "populația"], ["dens", "densitatea"], ["pib", "PIB/loc."]], set)}${butoane("t", [["x", "x"], ["r", "√x"], ["l", "log10 x"]], tr)}</div><div class="ed-g"></div><div class="ed-o"></div>`);
  const W = 900, H = 200, x0 = 40, x1 = W - 16, y0 = 16, y1 = H - 40;
  const deseneaza = () => {
    const [fn, inv, et] = TR[tr], v = SET[set][0].map(fn);
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
   7. Tabelul de contingență: distanța × aceeași țară; citirea unei celule
   ========================================================================= */
E.edContingenta = (gazda, d) => {
  const T = d.sci;
  let mod = "n", gr = "grup", cel = [1, 0];
  const el = bloc(gazda, `<div class="ed-ctl">${butoane("m", [["n", "numere"], ["r", "% pe rând"], ["c", "% pe coloană"]], mod)}${butoane("g", [["grup", "bare grupate"], ["stiv", "bare stivuite 100%"], ["moz", "mozaic"]], gr)}</div>
    <div class="ed-ct"><div class="ed-ct__t"></div><div class="ed-g"></div></div><div class="ed-o"></div>`);
  const CUL = ["var(--sci-2)", "var(--sci-5)"];
  const deseneaza = () => {
    const R = T.v.map(x => x.reduce((a, b) => a + b, 0)), Cc = T.c.map((_, j) => T.v.reduce((a, x) => a + x[j], 0)), N = R.reduce((a, b) => a + b, 0);
    const val = (i, j) => mod === "n" ? T.v[i][j] : mod === "r" ? T.v[i][j] / R[i] : T.v[i][j] / Cc[j];
    const mx = Math.max(...T.v.flatMap((x, i) => x.map((_, j) => val(i, j))));
    el.querySelector(".ed-ct__t").innerHTML = `<table><thead><tr><th>${T.er}</th>${T.c.map(c => `<th>${c}</th>`).join("")}</tr></thead><tbody>`
      + T.r.map((rr, i) => `<tr><th>${rr}</th>${T.c.map((_, j) => { const u = val(i, j);
        return `<td data-i="${i}" data-j="${j}" class="${cel[0] === i && cel[1] === j ? "on" : ""}" style="--p:${(u / mx).toFixed(3)}">${mod === "n" ? nr(u) : f(100 * u, u < .1 ? 1 : 0) + "%"}</td>`; }).join("")}</tr>`).join("")
      + (mod === "n" ? `<tr><th>total</th>${Cc.map(c => `<td>${nr(c)}</td>`).join("")}</tr>` : "") + "</tbody></table>";
    const W = 420, H = 250, x0 = 56, x1 = W - 8, y0 = 10, y1 = H - 46; let s = "";
    if (gr === "grup"){
      const sy = sc(0, mod === "n" ? mx : 1, y1, y0), bw = (x1 - x0) / T.r.length;
      T.r.forEach((rr, i) => { T.c.forEach((_, j) => { const p = val(i, j), w = (bw - 12) / T.c.length;
        s += `<rect x="${x0 + i * bw + 6 + j * w}" y="${sy(p)}" width="${Math.max(0, w - 2)}" height="${y1 - sy(p)}" style="fill:${CUL[j]}"/>`; });
        s += `<text class="ed-tx ed-tx--mic" x="${x0 + i * bw + bw / 2}" y="${y1 + 16}" text-anchor="middle">${rr}</text>`; });
      s += `<text class="ed-tx" x="${x0 - 4}" y="${y0 + 8}" text-anchor="end">${mod === "n" ? nr(mx) : "100%"}</text><text class="ed-tx" x="${x0 - 4}" y="${y1}" text-anchor="end">0</text>`;
    } else {
      let xa = x0; T.r.forEach((rr, i) => { const w = gr === "moz" ? (x1 - x0) * R[i] / N : (x1 - x0) / T.r.length; let ya = y1;
        T.c.forEach((_, j) => { const h = (y1 - y0) * T.v[i][j] / R[i]; s += `<rect x="${xa + 1}" y="${ya - h}" width="${Math.max(0, w - 2)}" height="${h}" style="fill:${CUL[j]}"/>`; ya -= h; });
        s += `<text class="ed-tx ed-tx--mic" x="${xa + w / 2}" y="${y1 + 16}" text-anchor="middle">${w > 30 ? rr : ""}</text>`; xa += w; });
    }
    s += T.c.map((c, j) => `<g transform="translate(${x0 + j * 130},${H - 6})"><rect y="-10" width="10" height="10" style="fill:${CUL[j]}"/><text class="ed-tx" x="14" y="-1">${c}</text></g>`).join("");
    el.querySelector(".ed-g").innerHTML = svg(W, H, s);
    const [i, j] = cel, pr = T.v[i][j] / R[i], pc = T.v[i][j] / Cc[j];
    el.querySelector(".ed-o").innerHTML = cifre([["celula", `${T.r[i]} km × ${T.c[j]}: ${nr(T.v[i][j])} perechi`],
      ["pe rând", `${f(100 * pr, 1)}% din perechile aflate la ${T.r[i]} km sunt „${T.c[j]}”`, mod === "r" ? "ed-c-m1" : ""],
      ["pe coloană", `${f(100 * pc, 1)}% din perechile „${T.c[j]}” sunt la ${T.r[i]} km`, mod === "c" ? "ed-c-m1" : ""]])
      + panou("Clic pe o celulă: aceeași celulă, citită pe rând și pe coloană, răspunde la două întrebări diferite.");
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
  const el = bloc(gazda, `<div class="ed-ctl">${butoane("s", Object.entries(SET).map(([k, v]) => [k, v.t]), set)}<button class="ed-b ed-lg">scară logaritmică</button><button class="ed-b ed-rs">datele inițiale</button></div><div class="ed-g"></div><div class="ed-o"></div>`);
  const W = 900, H = 220, x0 = 60, x1 = W - 16, y0 = 18, y1 = H - 36;
  const init = () => { X = [...SET[set].x]; Y = [...SET[set].y]; dom = null; };
  const tx = u => lg ? Math.log10(u) : u, itx = u => lg ? 10 ** u : u;
  const deseneaza = () => {
    const S = SET[set], x = X.map(tx), y = Y.map(tx);
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
    ${glisor("a", "opacitatea", .01, .5, .01, .04)}${glisor("b", "căsuțe pe axa x", 10, 80, 5, 45)}</div><div class="ed-g"></div><div class="ed-o"></div>`);
  const [inp, ia, ibn] = ["n", "a", "b"].map(n => el.querySelector(`input[data-n="${n}"]`));
  const deseneaza = () => {
    const n = NS[+inp.value]; inp.nextElementSibling.textContent = nr(n); ia.nextElementSibling.textContent = f(+ia.value, 2); ibn.nextElementSibling.textContent = ibn.value;
    ia.closest(".ed-gl").style.display = vedere === "tr" ? "" : "none"; ibn.closest(".ed-gl").style.display = vedere === "2d" ? "" : "none";
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
   10. Lineup: graficul real ascuns între grafice permutate
   ========================================================================= */
E.edLineup = (gazda, d) => {
  const R = REG(d).filter(r => r.populatie > 0);
  const per = (a, b) => R.filter(r => r[a] != null && r[b] != null).map(r => [r[a], r[b]]);
  const RUNDE = [
    { t: "PIB/loc. și studiile", gen: () => per("pib_locuitor", "studii_superioare") },
    { t: "deschiderea și longitudinea", gen: () => per("est", "deschidere") },
    { t: "deschiderea și populația", gen: () => per("populatie", "deschidere") }];
  let k = 0, samanta = 1, real = 0, ales = -1, ok = 0, tot = 0;
  const el = bloc(gazda, `<div class="ed-ctl">${butoane("r", RUNDE.map((q, i) => [String(i), q.t]), "0")}<button class="ed-b">altă așezare</button></div><div class="ed-g ed-lu"></div><div class="ed-o"></div>`);
  const deseneaza = () => {
    let P = RUNDE[k].gen(); const rx = ranguri(P.map(p => p[0])), ry = ranguri(P.map(p => p[1]));
    P = P.map((_, i) => [rx[i], ry[i]]);
    const xs = P.map(p => p[0]), y = P.map(p => p[1]), rr = rng(samanta * 7 + k), n = xs.length;
    real = Math.floor(rr() * 8); ales = -1;
    let html = "";
    for (let g = 0; g < 8; g++){
      let yy = y; if (g !== real){ yy = [...y]; for (let i = yy.length - 1; i > 0; i--){ const j = Math.floor(rr() * (i + 1)); [yy[i], yy[j]] = [yy[j], yy[i]]; } }
      const sx = sc(1, n, 8, 172), sy = sc(1, n, 112, 8);
      html += `<button class="ed-lu__p" data-g="${g}">${svg(180, 120, `<rect class="ed-cadru" x="1" y="1" width="178" height="118"/>`
        + xs.map((u, i) => `<circle class="ed-p ed-mic" cx="${sx(u)}" cy="${sy(yy[i])}" r="1.8"/>`).join(""))}<i>${g + 1}</i></button>`;
    }
    el.querySelector(".ed-g").innerHTML = html;
    el.querySelector(".ed-o").innerHTML = cifre([["identificări corecte", `${ok} din ${tot}`]]) + panou("Fiecare punct este o regiune, pe ranguri. În șapte grafice, valorile de pe axa verticală au fost permutate între regiuni. Care este graficul real?");
    el.querySelectorAll(".ed-lu__p").forEach(b => b.addEventListener("click", () => {
      if (ales >= 0) return; ales = +b.dataset.g; tot++; if (ales === real) ok++;
      el.querySelectorAll(".ed-lu__p").forEach((x, i) => x.classList.add(i === real ? "real" : i === ales ? "gresit" : "stins"));
      el.querySelector(".ed-o").innerHTML = cifre([["", ales === real ? "Identificat: tiparul se deosebește de permutări." : `Graficul real era ${real + 1}.`, ales === real ? "ed-c-adev" : "ed-c-sus"],
        ["ρ Spearman în graficul real", f(spearman(xs, y))], ["probabilitatea unei alegeri la întâmplare", "1 din 8"], ["identificări corecte", `${ok} din ${tot}`]]);
    }));
  };
  leaga(el, "r", v => { k = +v; samanta++; deseneaza(); });
  el.querySelector(".ed-b").addEventListener("click", () => { samanta++; deseneaza(); });
  deseneaza();
};


/* =========================================================================
   11. Categoric × numeric: SCI pe intervale de distanță; variabila de confuzie
   ========================================================================= */
E.edGrupuri = (gazda, d) => {
  const LIM = [0, 2, 2.398, 2.699, 3, 3.301, 9], ETI = ["0-100", "100-250", "250-500", "500-1000", "1000-2000", "2000+"];
  const P = (d.perechi || []).slice(0, 4000);
  let v = "bare", hue = false;
  const el = bloc(gazda, `<div class="ed-ctl">${butoane("v", [["bare", "bare cu media"], ["box", "boxplot"], ["viol", "violin"], ["pct", "puncte"]], v)}<button class="ed-b ed-hue">separat: aceeași țară / țări diferite</button><button class="ed-b ed-tot">fără intervale</button></div><div class="ed-g"></div><div class="ed-o"></div>`);
  let fara = false;
  const W = 900, H = 230, x0 = 64, x1 = W - 10, y0 = 14, y1 = H - 46;
  const deseneaza = () => {
    const IN = fara ? [[0, 9]] : ETI.map((_, i) => [LIM[i], LIM[i + 1]]), ET2 = fara ? ["toate distanțele"] : ETI.map(e => e + " km"), bw = (x1 - x0) / IN.length;
    const log = v !== "bare", sy = log ? sc(0, 6.6, y1, y0) : sc(0, 400000, y1, y0);
    let s = axe({ x0, x1, y0, y1, sx: x => x, sy, dy: log ? [0, 6.6] : [0, 400000], fy: u => log ? f(u, 0) : nr(u), ey: log ? "SCI (log10)" : "SCI, media (scară obișnuită)" });
    const med = {};
    IN.forEach(([a0, a1], i) => {
      const G = hue ? [[0, -bw / 4], [1, bw / 4]] : [[null, 0]];
      s += `<text class="ed-tx" x="${x0 + bw * i + bw / 2}" y="${y1 + 16}" text-anchor="middle">${ET2[i]}</text>`;
      G.forEach(([gr, dx]) => { const a = P.filter(p => p[0] >= a0 && p[0] < a1 && (gr === null || p[2] === gr)).map(p => log ? p[1] : 10 ** p[1]);
        if (!a.length) return; const c = x0 + bw * i + bw / 2 + dx, w = Math.min(hue ? bw / 2.6 : bw / 1.8, 120), cls = gr === 1 ? "ed-bar2" : "ed-bar", rr = rng(i + 3);
        med[`${i}-${gr}`] = mediana(a.map(u => log ? u : Math.log10(u)));
        s += `<text class="ed-tx ed-tx--mic" x="${c}" y="${y1 + 30}" text-anchor="middle">n = ${nr(a.length)}</text>`;
        if (v === "bare"){ const m = medie(a), e = abatere(a) / Math.sqrt(a.length);
          s += `<rect class="${cls}" x="${c - w / 2}" y="${sy(Math.min(m, 400000))}" width="${w}" height="${y1 - sy(Math.min(m, 400000))}"/><line class="ed-mus" x1="${c}" x2="${c}" y1="${sy(Math.max(0, m - 2 * e))}" y2="${sy(Math.min(400000, m + 2 * e))}"/>`; }
        else if (v === "pct") a.slice(0, 500).forEach(u => s += `<circle class="${gr === 1 ? "ed-sus" : "ed-p"} ed-mic" cx="${c + (rr() - .5) * w}" cy="${sy(u)}" r="2"/>`);
        else if (v === "box"){ const o = sortat(a), q1 = cuantila(o, .25, true), q2 = cuantila(o, .5, true), q3 = cuantila(o, .75, true), iq = q3 - q1,
            lw = o.find(u => u >= q1 - 1.5 * iq), uw = [...o].reverse().find(u => u <= q3 + 1.5 * iq);
          s += `<line class="ed-mus" x1="${c}" x2="${c}" y1="${sy(lw)}" y2="${sy(uw)}"/><rect class="ed-cutie${gr === 1 ? " ed-cutie2" : ""}" x="${c - w / 2}" y="${sy(q3)}" width="${w}" height="${sy(q1) - sy(q3)}"/><line class="ed-med" x1="${c - w / 2}" x2="${c + w / 2}" y1="${sy(q2)}" y2="${sy(q2)}"/>`; }
        else { const pts = []; for (let y = 0; y <= 6.6; y += .15){ let t = 0; a.forEach(u => t += Math.exp(-.5 * ((y - u) / .25) ** 2)); pts.push([y, t / a.length]); }
          const mx = Math.max(...pts.map(p => p[1])), hh = sc(0, mx, 0, w / 2);
          s += `<path class="ed-arie${gr === 1 ? " ed-arie2" : ""}" d="M${pts.map(p => `${c - hh(p[1])},${sy(p[0])}`).join(" L")} L${[...pts].reverse().map(p => `${c + hh(p[1])},${sy(p[0])}`).join(" L")}Z"/>`; } });
    });
    el.querySelector(".ed-g").innerHTML = svg(W, H, s);
    const rap = IN.map((_, i) => med[`${i}-1`] != null && med[`${i}-0`] != null ? 10 ** (med[`${i}-1`] - med[`${i}-0`]) : null).filter(x => x);
    el.querySelector(".ed-o").innerHTML = (hue ? cifre([[fara ? "raportul medianelor, aceeași țară / țări diferite, pe toate perechile" : "raportul medianelor, aceeași țară / țări diferite, pe intervale",
        rap.map(x => f(x, 0) + "×").join("  ·  "), "ed-c-sus"]]) : "")
      + panou(v === "bare" ? "Media pe scara obișnuită este dominată de câteva perechi foarte legate; barele nu descriu perechea tipică, iar erorile sunt mari."
        : hue && fara ? "Fără intervale, comparația amestecă efectul graniței cu al distanței: perechile din aceeași țară sunt și mult mai apropiate."
        : hue ? "Verde: țări diferite; portocaliu: aceeași țară. Comparația pe intervale ține distanța aproximativ constantă."
        : "Pe scara log: mediana, împrăștierea și forma fiecărui grup, cu numărul de perechi.");
  };
  leaga(el, "v", k => { v = k; deseneaza(); });
  el.querySelector(".ed-hue").addEventListener("click", e => { hue = !hue; e.target.classList.toggle("on", hue); deseneaza(); });
  el.querySelector(".ed-tot").addEventListener("click", e => { fara = !fara; e.target.classList.toggle("on", fara); deseneaza(); });
  deseneaza();
};


/* =========================================================================
   13. Multe variabile: matricea de grafice și matricea de corelație
   ========================================================================= */
E.edMultivar = (gazda, d) => {
  const V = ["pib_locuitor", "studii_superioare", "somaj", "varsta_medie", "densitate"], SC = { pib_locuitor: "PIB/loc.", studii_superioare: "studii", somaj: "șomaj", varsta_medie: "vârsta", densitate: "densitate" };
  const R0 = REG(d).filter(r => V.every(v => r[v] != null && r[v] > 0));
  let sel = [0, 4], met = "s", lg = true;
  const el = bloc(gazda, `<div class="ed-ctl">${butoane("m", [["s", "Spearman"], ["p", "Pearson"]], met)}<button class="ed-b ed-lg on">densitatea pe scara log</button></div><div class="ed-mv"><div class="ed-g"></div><div class="ed-h"></div></div><div class="ed-o"></div>`);
  const deseneaza = () => {
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
   14. Tipar și reziduu: dreapta potrivită de mână, apoi prin cele mai mici pătrate
   ========================================================================= */
E.edReziduu = (gazda, d) => {
  const P = (d.perechi || []).slice(0, 1500);
  const [A0, B0] = mcmmp(P.map(p => p[0]), P.map(p => p[1]));
  const SSmin = P.reduce((t, p) => t + (p[1] - A0 - B0 * p[0]) ** 2, 0);
  let a = 6, b = -1, seg = false;
  const el = bloc(gazda, `<div class="ed-ctl">${glisor("b", "panta", -3, 1, .02, b)}${glisor("a", "nivelul", 2, 10, .05, a)}<button class="ed-b ed-mp">cele mai mici pătrate</button><button class="ed-b ed-sg">reziduurile, ca segmente</button></div><div class="ed-g"></div><div class="ed-o"></div>`);
  const [ib, ia] = ["b", "a"].map(n => el.querySelector(`input[data-n="${n}"]`));
  const W = 900, x0 = 56, x1 = W - 16;
  const deseneaza = () => {
    const xs = P.map(p => p[0]), lo = Math.min(...xs), hi = Math.max(...xs), sx = sc(lo, hi, x0, x1), sy = sc(0, 6.6, 168, 14);
    const res = P.map(p => p[1] - (a + b * p[0])), rm = 3, sr = sc(-rm, rm, 290, 206);
    let s = axe({ x0, x1, y0: 14, y1: 168, sx, sy, dx: [lo, hi], dy: [0, 6.6], fx: u => nr(10 ** u), fy: u => f(u, 0), ey: "SCI (log10)" });
    if (seg) P.slice(0, 200).forEach(p => s += `<line class="ed-l-obs" x1="${sx(p[0])}" x2="${sx(p[0])}" y1="${sy(p[1])}" y2="${sy(a + b * p[0])}"/>`);
    P.forEach(p => s += `<circle class="${p[2] ? "ed-sus" : "ed-p"} ed-mic" cx="${sx(p[0])}" cy="${sy(p[1])}" r="2"/>`);
    s += `<line class="ed-l-tot" x1="${sx(lo)}" x2="${sx(hi)}" y1="${sy(a + b * lo)}" y2="${sy(a + b * hi)}"/>`;
    s += axe({ x0, x1, y0: 206, y1: 290, sx, sy: sr, dx: [lo, hi], dy: [-rm, rm], ny: 2, fx: u => nr(10 ** u), fy: u => f(u, 0), ex: "distanța, km (scară log)", ey: "reziduul = SCI − dreapta (log10)" });
    s += `<line class="ed-l-adev" x1="${x0}" x2="${x1}" y1="${sr(0)}" y2="${sr(0)}"/>`;
    P.forEach((p, i) => s += `<circle class="${p[2] ? "ed-sus" : "ed-p"} ed-mic" cx="${sx(p[0])}" cy="${sr(Math.max(-rm, Math.min(rm, res[i])))}" r="1.8"/>`);
    el.querySelector(".ed-g").innerHTML = svg(W, 330, s);
    const r0 = res.filter((_, i) => !P[i][2]), r1 = res.filter((_, i) => P[i][2]), ss = res.reduce((t, e) => t + e * e, 0);
    el.querySelector(".ed-o").innerHTML = cifre([["suma pătratelor reziduurilor", f(ss, 0)], ["față de minimul posibil", `+${f(100 * (ss / SSmin - 1), 1)}%`, ss / SSmin < 1.005 ? "ed-c-adev" : ""],
      ["reziduul median, țări diferite", f(mediana(r0), 2)], ["reziduul median, aceeași țară (portocaliu)", f(mediana(r1), 2), "ed-c-sus"]])
      + panou("Panta și nivelul se ajustează până când suma pătratelor nu mai scade; rezultatul se compară apoi cu metoda celor mai mici pătrate.");
    ib.nextElementSibling.textContent = f(b, 2); ia.nextElementSibling.textContent = f(a, 2);
  };
  ib.addEventListener("input", () => { b = +ib.value; deseneaza(); });
  ia.addEventListener("input", () => { a = +ia.value; deseneaza(); });
  el.querySelector(".ed-mp").addEventListener("click", () => { a = A0; b = B0; ib.value = b; ia.value = a; deseneaza(); });
  el.querySelector(".ed-sg").addEventListener("click", e => { seg = !seg; e.target.classList.toggle("on", seg); deseneaza(); });
  deseneaza();
};


/* =========================================================================
   15. Multe încercări: variabile aleatoare lângă indicatorii reali
   ========================================================================= */
E.edPoteci = (gazda, d) => {
  const R = REG(d).filter(r => r.deschidere != null && r.cod !== "NO0B");
  const REAL = ["pib_locuitor", "studii_superioare", "somaj", "densitate", "varsta_medie"];
  const PRAG = 1.96 / Math.sqrt(R.length - 1);
  let samanta = 1;
  const el = bloc(gazda, `<div class="ed-ctl">${glisor("k", "variabile aleatoare încercate", 0, 60, 1, 20)}<button class="ed-b">alte numere aleatoare</button></div><div class="ed-g"></div><div class="ed-o"></div>`);
  const inp = el.querySelector("input"), ry = ranguri(R.map(q => q.deschidere));
  const realC = REAL.map(v => { const a = R.filter(q => q[v] != null); return { n: ET[v], c: spearman(a.map(q => q[v]), a.map(q => q.deschidere)), real: true }; });
  const deseneaza = () => {
    const k = +inp.value, z = normal(rng(samanta)), W = 900; el.querySelector("output").textContent = k;
    const A = []; for (let i = 0; i < k; i++) A.push({ n: `aleatoare ${i + 1}`, c: pearson(ranguri(R.map(() => z())), ry), real: false });
    const L = [...realC, ...A.sort((p, q) => Math.abs(q.c) - Math.abs(p.c)).slice(0, 6)];
    const H = 150, x0 = 200, x1 = W - 60, sx = sc(0, .6, x0, x1), rh = (H - 10) / L.length;
    let s = "";
    L.forEach((q, i) => { const yy = 4 + i * rh, a = Math.abs(q.c);
      s += `<text class="ed-tx${q.real ? " ed-gros" : ""}" x="${x0 - 8}" y="${yy + rh * .7}" text-anchor="end">${q.n}</text><rect class="${q.real ? "ed-bar" : "ed-bar2"}" x="${x0}" y="${yy + 2}" width="${Math.max(1, sx(Math.min(.6, a)) - x0)}" height="${rh - 5}"/><text class="ed-tx" x="${sx(Math.min(.6, a)) + 6}" y="${yy + rh * .7}">${f(a)}</text>`; });
    s += `<line class="ed-l-obs" x1="${sx(PRAG)}" x2="${sx(PRAG)}" y1="0" y2="${H}"/><text class="ed-tx ed-tx--mic" x="${sx(PRAG) + 4}" y="${H - 2}">pragul de 5%</text>`;
    el.querySelector(".ed-g").innerHTML = svg(W, H, s);
    const peste = A.filter(q => Math.abs(q.c) > PRAG).length;
    el.querySelector(".ed-o").innerHTML = cifre([["variabile aleatoare peste prag", `${peste} din ${k}`, peste ? "ed-c-sus" : ""], ["cea mai mare corelație a unei variabile aleatoare", f(Math.max(0, ...A.map(q => Math.abs(q.c))))]])
      + panou("Corelația (în valoare absolută) cu deschiderea regiunilor. Verde: indicatorii reali; portocaliu: cele mai mari 6 dintre variabilele aleatoare.");
  };
  inp.addEventListener("input", deseneaza);
  el.querySelector(".ed-b").addEventListener("click", () => { samanta++; deseneaza(); });
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
