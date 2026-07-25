/* paginare.js — un cursor pentru per_page. Se vede numărul de pagini necesare și,
   mai important, CE date lipsesc din tabel dacă citești doar prima pagină:
   rândurile absente sunt arătate, nu doar numărate. Eșantion local wb-data.json. */

import { incarcaDate, esc } from "./date.js";
import * as WB from "./wb.js";

export default async function paginare(gazda, parametri = {}) {
  const data = await incarcaDate(parametri.sursa || "wb-data.json");
  const toateTarile = data.tari.map((t) => t.cod);

  const st = { indicator: data.indicatori[0].cod, perPage: 5 };

  function randuri() {
    return WB.construiesteRanduri(data, toateTarile, st.indicator, data.ani);
  }
  const total = randuri().length;

  gazda.innerHTML = `
    <div class="ctrl">
      <label>Indicator
        <select id="pg-ind">${data.indicatori.map((i) => `<option value="${i.cod}">${esc(i.nume)}</option>`).join("")}</select>
      </label>
      <label>per_page: <span id="pg-val" style="font-family:var(--mono);color:var(--ink)">5</span>
        <input type="range" id="pg-pp" min="2" max="${total}" value="5" step="1">
      </label>
    </div>
    <p id="pg-sum" style="font-family:var(--sans);font-size:13.5px;margin:0 0 12px"></p>
    <div class="dt-wrap"><table class="dt" id="pg-tab"></table></div>
    <p style="font-size:12.5px;color:var(--muted);margin:10px 0 0">
      Rândurile roșii <b style="color:var(--no)">lipsesc din tabelul tău</b> dacă te oprești la prima pagină.</p>`;

  const elVal = gazda.querySelector("#pg-val");
  const elSum = gazda.querySelector("#pg-sum");
  const elTab = gazda.querySelector("#pg-tab");

  function deseneaza() {
    const rows = randuri();
    const pages = Math.max(1, Math.ceil(rows.length / st.perPage));
    const vizibile = st.perPage;
    const lipsa = Math.max(0, rows.length - vizibile);
    elVal.textContent = st.perPage;
    elSum.innerHTML = `Total: <b>${rows.length}</b> rânduri · pe prima pagină: <b>${Math.min(vizibile, rows.length)}</b> · ` +
      `pagini necesare: <b>${pages}</b> · lipsă dacă citești doar pagina 1: <b style="color:var(--no)">${lipsa}</b>`;
    elTab.innerHTML =
      `<thead><tr><th>#</th><th>Țară</th><th>An</th><th>Valoare</th></tr></thead><tbody>${
        rows.map((r, i) => `<tr class="${i >= vizibile ? "miss" : ""}">
          <td>${i + 1}</td><td>${esc(r.country.value)}</td><td>${esc(r.date)}</td>
          <td>${r.value === null ? "null" : r.value}</td></tr>`).join("")}</tbody>`;
  }

  gazda.querySelector("#pg-ind").addEventListener("change", (e) => { st.indicator = e.target.value; deseneaza(); });
  gazda.querySelector("#pg-pp").addEventListener("input", (e) => { st.perPage = +e.target.value; deseneaza(); });

  deseneaza();
}
