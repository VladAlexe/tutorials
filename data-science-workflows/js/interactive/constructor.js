/* constructor.js — construiește adresa Băncii Mondiale în timp real din controale,
   cu fiecare segment colorat și etichetat, și arată răspunsul corespunzător din
   eșantionul local. Scoți format=json → vezi XML. Fără apeluri de rețea. */

import { incarcaDate, esc } from "./date.js";
import * as WB from "./wb.js";

const OPT_TARI = [
  { val: "ro", nume: "România" },
  { val: "it", nume: "Italia" },
  { val: "es", nume: "Spania" },
  { val: "ro;it", nume: "România + Italia" },
  { val: "ro;it;es", nume: "Toate trei" }
];

export default async function constructor(gazda, parametri = {}) {
  const data = await incarcaDate(parametri.sursa || "wb-data.json");
  const ani = data.ani;

  const st = {
    tari: "ro",
    indicator: data.indicatori[0].cod,
    de: ani[0],
    la: ani[ani.length - 1],
    perPage: 5,
    json: true
  };

  gazda.innerHTML = `
    <div class="ctrl">
      <label>Țară / țări
        <select id="c-tari">${OPT_TARI.map((o) => `<option value="${o.val}">${o.nume}</option>`).join("")}</select>
      </label>
      <label>Indicator
        <select id="c-ind">${data.indicatori.map((i) => `<option value="${i.cod}">${esc(i.nume)}</option>`).join("")}</select>
      </label>
      <label>De la anul
        <select id="c-de">${ani.map((a) => `<option>${a}</option>`).join("")}</select>
      </label>
      <label>Până la anul
        <select id="c-la">${ani.map((a) => `<option ${a === st.la ? "selected" : ""}>${a}</option>`).join("")}</select>
      </label>
      <label>per_page
        <select id="c-pp"><option>5</option><option>50</option></select>
      </label>
      <label class="chk" style="flex-direction:row;align-self:center;margin-top:14px">
        <input type="checkbox" id="c-json" checked> format=json
      </label>
    </div>
    <div class="url" id="c-url" role="group" aria-label="Adresa construită"></div>
    <p class="c2__tag" id="c-hint" style="margin:-6px 0 12px"></p>
    <div class="resp" id="c-resp" aria-live="polite"></div>
    <p style="font-size:12px;color:var(--muted);margin:8px 0 0">Răspuns din eșantionul local — la tine, în editor, ar fi date reale.</p>`;

  const q = (id) => gazda.querySelector(id);
  const elUrl = q("#c-url"), elResp = q("#c-resp"), elHint = q("#c-hint");

  function citesteControale() {
    st.tari = q("#c-tari").value;
    st.indicator = q("#c-ind").value;
    st.de = q("#c-de").value;
    st.la = q("#c-la").value;
    st.perPage = +q("#c-pp").value;
    st.json = q("#c-json").checked;
  }

  function deseneaza() {
    const tari = st.tari.split(";");
    const seg = WB.segmenteUrl(data.baza, tari, st.indicator, st.de, st.la, st.perPage, st.json);
    elUrl.innerHTML = seg.map((s, i) => s.t === "sep"
      ? `<span class="u-sep">${esc(s.text)}</span>`
      : `<button type="button" class="useg u-${s.t}" data-i="${i}" title="${esc(s.nume)}">${esc(s.text)}</button>`).join("");
    elUrl.querySelectorAll(".useg").forEach((b) => b.addEventListener("click", () => {
      elUrl.querySelectorAll(".useg").forEach((x) => x.classList.remove("on"));
      b.classList.add("on");
      const s = seg[+b.dataset.i];
      elHint.innerHTML = `<b>${esc(s.nume)}</b> — ${esc(s.rol)}`;
    }));

    const aniAlesi = WB.intervalAni(ani, st.de, st.la);
    const rows = WB.construiesteRanduri(data, tari, st.indicator, aniAlesi);
    const resp = WB.raspuns(rows, 1, st.perPage);

    if (st.json) {
      elResp.innerHTML = WB.coloreazaJson(resp);
    } else {
      elResp.innerHTML = WB.formaXml(resp) +
        `\n\n<span class="c"># Fără format=json, API-ul întoarce XML — asta primești implicit.</span>`;
    }
  }

  gazda.querySelectorAll("select, input").forEach((c) =>
    c.addEventListener("change", () => { citesteControale(); deseneaza(); }));

  deseneaza();
}
