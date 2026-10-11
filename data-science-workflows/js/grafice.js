/* ===========================================================================
   GRAFICE DIN DATELE CURSULUI

   Două componente, amândouă pe date reale din Social Connectedness Index,
   calculate din fișierele descărcate de pe HDX și salvate în /date/.

     <div class="ix" data-ix="matrice"> …  matricea 42 × 42 a județelor
     <div class="ix" data-ix="bare">    …  România către celelalte țări

   Reguli de culoare: o singură nuanță pentru mărime, șase trepte, alese
   separat pentru fiecare temă (vezi grafice.css). Culoarea nu poartă
   niciodată singură informația: fiecare celulă are balon la hover, fiecare
   grafic are legendă cu praguri, și fiecare are o variantă de tabel.
   =========================================================================== */

import { RADACINA } from "./curs.js?v=4";

const G = {};

/* --- unelte comune -------------------------------------------------------- */

const nf = new Intl.NumberFormat("ro-RO");
const scurt = v => v >= 1e6 ? (v / 1e6).toFixed(v >= 1e7 ? 0 : 1).replace(".", ",") + " mil."
             : v >= 1e3 ? Math.round(v / 1e3) + " mii"
             : String(v);

/** Pragurile sunt scrise de mână, nu calculate: sunt numere pe care le poate
    citi un om, iar distribuția reală le acoperă uniform (q25 74k, q50 103k,
    q75 182k, q90 454k, q95 747k). */
const PRAGURI = [50e3, 100e3, 200e3, 500e3, 1e6];
const banda = v => { let i = 0; while (i < PRAGURI.length && v >= PRAGURI[i]) i++; return i + 1; };
const PRAG_ET = ["50", "100", "200", "500", "1 000"];

function cadru(gazda, { titlu, sub, unelte = "" }){
  gazda.innerHTML = `<div class="gf">
    <div class="gf__cap"><span class="gf__t">${titlu}</span>
      <span class="gf__unelte">${unelte}</span></div>
    ${sub ? `<p class="gf__sub">${sub}</p>` : ""}
    <div class="gf__corp"></div>
    <div class="gf__balon" role="status"></div>
  </div>`;
  return {
    corp: gazda.querySelector(".gf__corp"),
    balon: gazda.querySelector(".gf__balon"),
    gf: gazda.querySelector(".gf")
  };
}

function legenda(){
  return `<div class="gf__leg">
    <div class="gf__scara">
      <span class="gf__scara-et">conectivitate, mii</span>
      <div class="gf__trepte" role="img" aria-label="Scară de la sub 50 de mii la peste un milion">
        ${[1,2,3,4,5,6].map(i => `<span style="background:var(--sci-${i})"></span>`).join("")}
      </div>
      <div class="gf__praguri">
        ${PRAG_ET.map(e => `<span>${e}</span>`).join("")}<span>+</span>
      </div>
    </div>
    <span class="gf__lalt"><i></i>același județ, scos din scară</span>
  </div>`;
}

/** Balonul urmărește cursorul, dar rămâne în interiorul graficului. */
function leagaBalon(zona, balon){
  return {
    arata(ev, html){
      balon.innerHTML = html;
      balon.classList.add("viu");
      const z = zona.getBoundingClientRect();
      const b = balon.getBoundingClientRect();
      let x = ev.clientX - z.left + 14;
      let y = ev.clientY - z.top - b.height - 10;
      if (x + b.width > z.width) x = ev.clientX - z.left - b.width - 14;
      if (y < 0) y = ev.clientY - z.top + 18;
      balon.style.left = Math.max(0, x) + "px";
      balon.style.top = y + "px";
    },
    ascunde(){ balon.classList.remove("viu"); }
  };
}

async function adu(cale){
  const r = await fetch(`${RADACINA}/date/${cale}`, { cache:"force-cache" });
  if (!r.ok) throw new Error(`nu pot citi ${cale} (${r.status})`);
  return r.json();
}

/* ==========================================================================
   1. Matricea județelor
   ========================================================================== */

G.matrice = async (gazda) => {
  const d = await adu("sci-ro-nuts3.json");
  const { judete, sigle, matrice: M } = d;
  const n = judete.length;

  const u = cadru(gazda, {
    titlu: "Conectivitate între județe",
    sub: `Fiecare pătrat e o pereche de județe: cât de probabil e ca un om din
      județul de pe rând și unul din județul de pe coloană să fie prieteni pe
      Facebook. ${n} × ${n} = ${nf.format(n * n)} de pătrate, adică exact atâtea
      rânduri are tabelul de la care pornim. Treci cu mouse-ul peste oricare,
      sau apasă pe un județ ca să-i vezi tot rândul.`,
    unelte: `<button class="gf__bt on" data-vedere="harta" type="button">hartă</button>
             <button class="gf__bt" data-vedere="tabel" type="button">tabel</button>`
  });

  /* --- geometria: o singură unitate de desen, scalată prin viewBox --------- */
  const C = 13, G0 = 26, L = G0 + n * C;

  let html = `<div class="v-harta">${legenda()}<svg class="mtx" viewBox="0 0 ${L + 2} ${L + 2}"
      role="img" aria-label="Matrice de conectivitate între cele ${n} de județe">`;

  /* umbre de rând și de coloană, aprinse la hover */
  html += `<rect class="umbra" id="um-r" x="0" y="0" width="${L}" height="${C}"></rect>
           <rect class="umbra" id="um-c" x="0" y="0" width="${C}" height="${L}"></rect>`;

  for (let i = 0; i < n; i++){
    html += `<text class="et er" data-i="${i}" x="${G0 - 4}" y="${G0 + i * C + C / 2 + 2.6}"
               text-anchor="end">${sigle[i]}</text>`;
    html += `<text class="et ec" data-i="${i}" x="${G0 + i * C + C / 2}" y="${G0 - 5}"
               text-anchor="start" transform="rotate(-90 ${G0 + i * C + C / 2} ${G0 - 5})">${sigle[i]}</text>`;
  }
  for (let i = 0; i < n; i++){
    for (let j = 0; j < n; j++){
      const v = M[i][j];
      const cls = i === j ? "eu" : "b" + banda(v);
      html += `<rect class="c ${cls}" x="${G0 + j * C}" y="${G0 + i * C}"
                 width="${C}" height="${C}" data-i="${i}" data-j="${j}"></rect>`;
    }
  }
  html += `</svg><div class="mtx__det"></div>
    <p class="gf__sursa">Date: Data for Good at Meta, Social Connectedness Index,
    instantaneu ianuarie 2026, nivel NUTS 3. Diagonala, adică legăturile din
    interiorul aceluiași județ, e scoasă din scară: mediana ei e de 238 de ori
    mai mare decât mediana restului, și ar face toate celelalte pătrate să
    arate la fel.</p></div>`;

  /* --- varianta de tabel, fără culoare ------------------------------------ */
  const perechi = [];
  for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++)
    perechi.push({ a:judete[i], b:judete[j], v:M[i][j] });
  perechi.sort((x, y) => y.v - x.v);

  html += `<div class="v-tabel" hidden><div class="gf__sul"><table class="gf__tab">
      <thead><tr><th>#</th><th>Pereche</th><th>Conectivitate</th></tr></thead>
      <tbody>${perechi.slice(0, 40).map((p, k) => `<tr>
        <td class="n">${k + 1}</td><td>${p.a} – ${p.b}</td>
        <td class="n">${nf.format(p.v)}</td></tr>`).join("")}</tbody></table></div>
    <p class="gf__sursa">Primele 40 dintre cele ${nf.format(perechi.length)} de perechi
    distincte de județe. Același tabel pe care îl obții cu un sort în pandas.</p></div>`;

  u.corp.innerHTML = html;

  /* cele două vederi stau amândouă în pagină; comutatorul doar le ascunde */
  const vHarta = u.corp.querySelector(".v-harta");
  const vTabel = u.corp.querySelector(".v-tabel");
  u.gf.querySelectorAll("[data-vedere]").forEach(b => b.onclick = () => {
    u.gf.querySelectorAll("[data-vedere]").forEach(x => x.classList.toggle("on", x === b));
    const t = b.dataset.vedere === "tabel";
    vTabel.hidden = !t; vHarta.hidden = t;
  });

  const svg  = u.corp.querySelector(".mtx");
  const det  = u.corp.querySelector(".mtx__det");
  const umR  = u.corp.querySelector("#um-r");
  const umC  = u.corp.querySelector("#um-c");
  const bal  = leagaBalon(u.gf, u.gf.querySelector(".gf__balon"));
  const etR  = [...svg.querySelectorAll(".er")];
  const etC  = [...svg.querySelectorAll(".ec")];

  const aprinde = (i, j) => {
    umR.setAttribute("y", G0 + i * C); umR.classList.add("viu");
    umC.setAttribute("x", G0 + j * C); umC.classList.add("viu");
    etR.forEach((e, k) => e.classList.toggle("viu", k === i));
    etC.forEach((e, k) => e.classList.toggle("viu", k === j));
  };
  const stinge = () => {
    umR.classList.remove("viu"); umC.classList.remove("viu");
    etR.forEach(e => e.classList.remove("viu"));
    etC.forEach(e => e.classList.remove("viu"));
  };

  svg.addEventListener("mousemove", ev => {
    const r = ev.target.closest("rect.c");
    if (!r){ bal.ascunde(); stinge(); return; }
    const i = +r.dataset.i, j = +r.dataset.j, v = M[i][j];
    aprinde(i, j);
    bal.arata(ev, i === j
      ? `în interiorul județului ${judete[i]}<b>${nf.format(v)}</b>`
      : `${judete[i]} → ${judete[j]}<b>${nf.format(v)}</b>`);
  });
  svg.addEventListener("mouseleave", () => { bal.ascunde(); stinge(); });
  svg.addEventListener("click", ev => {
    const r = ev.target.closest("rect.c");
    const e = ev.target.closest("text.et");
    if (r) detaliu(+r.dataset.i, true);
    else if (e) detaliu(+e.dataset.i, true);
  });

  /** Un rând din matrice e o privire monadică asupra unui județ: cu cine e
      legat și cu cine nu. Exact pasul pe care îl fac studenții la lecția 6. */
  function detaliu(i, sari){
    const r = judete.map((nume, j) => ({ nume, v: M[i][j], j }))
                    .filter(x => x.j !== i)
                    .sort((a, b) => b.v - a.v);
    const sus = r.slice(0, 8), jos = r.slice(-3);
    const max = sus[0].v;
    const rand = x => `<div class="brr__r">
        <span class="brr__n">${x.nume}</span>
        <span class="brr__p"><i style="width:${(x.v / max * 100).toFixed(1)}%"></i></span>
        <span class="brr__v">${nf.format(x.v)}</span></div>`;
    det.innerHTML = `
      <p class="mtx__dt">${judete[i]}: cu cine e legat</p>
      <p class="mtx__dd">Rândul lui ${judete[i]} din matrice, ordonat. În interiorul
      județului: <b style="font-family:var(--mono);font-weight:500">${nf.format(M[i][i])}</b>,
      de ${Math.round(M[i][i] / sus[0].v)} de ori mai mult decât cu primul vecin.</p>
      <div class="brr">
        ${sus.map(rand).join("")}
        <div class="brr__r" style="opacity:.5"><span class="brr__n"></span>
          <span class="brr__p" style="display:grid;place-items:center">
            <span style="font-family:var(--mono);font-size:10px;color:var(--text-3)">
              ${r.length - 11} de județe la mijloc</span></span><span></span></div>
        ${jos.map(rand).join("")}
      </div>`;
    if (sari) det.scrollIntoView({ block:"nearest", behavior:"smooth" });
  }

  /* o deschidere implicită, ca panoul să nu fie gol la prima vedere */
  detaliu(judete.indexOf("Cluj") >= 0 ? judete.indexOf("Cluj") : 0);
};

/* ==========================================================================
   2. România către celelalte țări
   ========================================================================== */

G.bare = async (gazda, date) => {
  const d = await adu("sci-ro-tari.json");
  const cate = date.cate || 20;
  const t = d.tari.slice(0, cate);
  const max = t[0].sci;

  const u = cadru(gazda, {
    titlu: "România, către celelalte țări",
    sub: `Primele ${cate} de țări după conectivitate socială cu România. Indicele e
      normalizat prin populațiile celor două țări, deci răspunde la întrebarea
      „cât de probabil e ca doi oameni să fie prieteni", nu la „câți români
      trăiesc acolo". Cele două ordini nu coincid, și aici e toată lecția.`,
    unelte: `<button class="gf__bt on" data-vedere="bare" type="button">bare</button>
             <button class="gf__bt" data-vedere="tabel" type="button">tabel</button>`
  });

  const bare = `<div class="brr">
      ${t.map(x => `<div class="brr__r">
        <span class="brr__n" title="${x.nume}">${x.nume}</span>
        <span class="brr__p"><i style="width:${(x.sci / max * 100).toFixed(1)}%"></i></span>
        <span class="brr__v">${nf.format(x.sci)}</span></div>`).join("")}
    </div>
    <div class="gf__reper"><b>${scurt(d.ro_ro)}</b>
      <span>Conectivitatea României cu ea însăși, pe aceeași scară.
      De ${Math.round(d.ro_ro / t[0].sci)} de ori mai mare decât cu
      ${t[0].nume}, prima din clasament. Dacă ar intra în grafic, toate barele
      de mai sus s-ar lipi de zero. Asta e prima problemă practică a
      indicatorului, și motivul pentru care la lecția 6 lucrăm pe scară
      logaritmică.</span></div>
    <p class="gf__sursa">Date: Data for Good at Meta, Social Connectedness Index,
    instantaneu ianuarie 2026, nivel de țară. ${d.tari.length} de parteneri în total.</p>`;

  const tabel = `<div class="gf__sul"><table class="gf__tab">
      <thead><tr><th>#</th><th>Țară</th><th>Cod</th><th>Conectivitate</th></tr></thead>
      <tbody>${d.tari.slice(0, 60).map((x, k) => `<tr>
        <td class="n">${k + 1}</td><td>${x.nume}</td><td class="n">${x.cod}</td>
        <td class="n">${nf.format(x.sci)}</td></tr>`).join("")}</tbody></table></div>
    <p class="gf__sursa">Primele 60 din ${d.tari.length}.</p>`;

  u.corp.innerHTML = bare;
  u.gf.querySelectorAll("[data-vedere]").forEach(b => b.onclick = () => {
    u.gf.querySelectorAll("[data-vedere]").forEach(x => x.classList.toggle("on", x === b));
    u.corp.innerHTML = b.dataset.vedere === "tabel" ? tabel : bare;
  });
};

export default G;

/* ==========================================================================
   3. „Cluj sau București?"  — comparație în doi poli
   Aceeași întrebare ca harta Madrid–Barcelona de la Social Capital Lab, pe
   datele noastre: pentru fiecare județ, cu care dintre cei doi poli e mai
   legat, raportat la cât de legat e cu fiecare.
   ========================================================================== */

G.diverg = async (gazda, date) => {
  const d = await adu("sci-ro-nuts3.json");
  const { judete, matrice: M } = d;
  const A = date.a || "Cluj", B = date.b || "București";
  const ia = judete.indexOf(A), ib = judete.indexOf(B);
  if (ia < 0 || ib < 0) throw new Error(`nu găsesc ${A} sau ${B}`);

  const r = judete.map((nume, j) => ({ nume, j, va:M[ia][j], vb:M[ib][j] }))
                  .filter(x => x.j !== ia && x.j !== ib)
                  .map(x => ({ ...x, raport: x.va / x.vb }))
                  .sort((x, y) => y.raport - x.raport);
  const spreA = r.filter(x => x.raport > 1).length;
  const maxLog = Math.max(...r.map(x => Math.abs(Math.log2(x.raport))));

  const u = cadru(gazda, {
    titlu: `${A} sau ${B}?`,
    sub: `Pentru fiecare județ: cu care dintre cele două orașe are legături de
      prietenie mai probabile. Bara spre stânga înseamnă ${A}, spre dreapta
      ${B}. Lungimea arată de câte ori, nu cu cât.`,
    unelte: `<button class="gf__bt on" data-vedere="bare" type="button">grafic</button>
             <button class="gf__bt" data-vedere="tabel" type="button">tabel</button>`
  });

  const rand = x => {
    const spre = x.raport > 1 ? "a" : "b";
    const ori  = x.raport > 1 ? x.raport : 1 / x.raport;
    const lat  = Math.abs(Math.log2(x.raport)) / maxLog * 50;
    return `<div class="dv__r" title="${x.nume}: ${A} ${nf.format(x.va)}, ${B} ${nf.format(x.vb)}">
      <span class="dv__n">${x.nume}</span>
      <span class="dv__p">
        <i class="dv__${spre}" style="${spre === "a"
          ? `right:50%;width:${lat}%` : `left:50%;width:${lat}%`}"></i>
        <b class="dv__ax"></b>
      </span>
      <span class="dv__v">${ori.toFixed(1)}×</span></div>`;
  };

  const bare = `<div class="dv__cap">
      <span class="dv__et dv__et--a">mai legat de ${A}</span>
      <span class="dv__et dv__et--b">mai legat de ${B}</span></div>
    <div class="dv">${r.map(rand).join("")}</div>
    <div class="gf__reper"><b>${spreA} / ${r.length}</b>
      <span>Atâtea județe înclină spre ${A}. Nu e o hartă politică și nu e o
      hartă a distanțelor, deși seamănă cu amândouă. E doar cine pe cine
      cunoaște.</span></div>
    <p class="gf__sursa">Date: Data for Good at Meta, Social Connectedness Index,
    nivel NUTS 3. Întrebarea e luată de la Social Capital Lab, care a făcut
    aceeași comparație pentru Madrid și Barcelona, la nivelul întregii Europe.</p>`;

  const tabel = `<div class="gf__sul"><table class="gf__tab">
      <thead><tr><th>Județ</th><th>${A}</th><th>${B}</th><th>Înclină spre</th></tr></thead>
      <tbody>${r.map(x => `<tr><td>${x.nume}</td>
        <td class="n">${nf.format(x.va)}</td><td class="n">${nf.format(x.vb)}</td>
        <td class="n">${x.raport > 1 ? A : B} ${(x.raport > 1 ? x.raport : 1 / x.raport).toFixed(1)}×</td>
        </tr>`).join("")}</tbody></table></div>`;

  u.corp.innerHTML = `<div class="v-bare">${bare}</div><div class="v-tabel" hidden>${tabel}</div>`;
  const vb = u.corp.querySelector(".v-bare"), vt = u.corp.querySelector(".v-tabel");
  u.gf.querySelectorAll("[data-vedere]").forEach(b => b.onclick = () => {
    u.gf.querySelectorAll("[data-vedere]").forEach(x => x.classList.toggle("on", x === b));
    const t = b.dataset.vedere === "tabel";
    vt.hidden = !t; vb.hidden = t;
  });
};
