/* json_tabel.js — JSON în stânga, tabel în dreapta. Apeși pe o celulă și se
   evidențiază de unde a venit. Un comutator arată aceeași operație pe JSON-stat,
   unde corespondența nu mai e directă. Date din continut/date/json-tabel.json. */

import { incarcaDate, esc } from "./date.js";

export default async function jsonTabel(gazda, parametri = {}) {
  const d = await incarcaDate(parametri.sursa || "json-tabel.json");
  const M = d.moduri;
  let activ = 0;

  gazda.innerHTML = `
    <div class="toggles" id="jt-mod"></div>
    <div class="jt">
      <div>
        <p class="c2__tag" style="margin:0 0 6px">Răspunsul</p>
        <div class="resp" id="jt-json" style="max-height:340px"></div>
      </div>
      <div>
        <p class="c2__tag" style="margin:0 0 6px">Tabelul</p>
        <div class="dt-wrap"><table class="dt" id="jt-tab"></table></div>
      </div>
    </div>
    <p class="c2__tag" id="jt-nota" style="margin:14px 0 0;color:var(--muted);font-weight:500;font-size:13.5px;line-height:1.6"></p>`;

  const mod = gazda.querySelector("#jt-mod");
  const elJson = gazda.querySelector("#jt-json");
  const elTab = gazda.querySelector("#jt-tab");
  const elNota = gazda.querySelector("#jt-nota");

  mod.innerHTML = M.map((m, i) =>
    `<button class="fbtn ${i === 0 ? "on" : ""}" data-i="${i}">${esc(m.eticheta)}</button>`).join("");

  function deseneaza() {
    const m = M[activ];
    elJson.innerHTML = m.linii.map((l) =>
      `<span class="jline"${l.id ? ` id="jl-${l.id}"` : ""}>${esc(l.t)}</span>`).join("");
    elTab.innerHTML =
      `<thead><tr>${m.antet.map((h) => `<th>${esc(h)}</th>`).join("")}</tr></thead>` +
      `<tbody>${m.randuri.map((r) => `<tr>${r.map((c) =>
        `<td class="jt-cell" data-src="${(c.src || []).join(",")}" tabindex="0" role="button">${esc(c.text)}</td>`).join("")}</tr>`).join("")}</tbody>`;
    elNota.textContent = m.nota;

    const celule = elTab.querySelectorAll(".jt-cell");
    function aprinde(cell) {
      elJson.querySelectorAll(".jline.hot").forEach((x) => x.classList.remove("hot"));
      celule.forEach((x) => x.classList.remove("hot"));
      cell.classList.add("hot");
      (cell.dataset.src ? cell.dataset.src.split(",").filter(Boolean) : []).forEach((id) => {
        const t = elJson.querySelector(`#jl-${CSS.escape(id)}`);
        if (t) t.classList.add("hot");
      });
    }
    celule.forEach((cell) => {
      cell.addEventListener("click", () => aprinde(cell));
      cell.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); aprinde(cell); } });
    });
  }

  mod.querySelectorAll(".fbtn").forEach((b) => b.addEventListener("click", () => {
    activ = +b.dataset.i;
    mod.querySelectorAll(".fbtn").forEach((x) => x.classList.toggle("on", x === b));
    deseneaza();
  }));

  deseneaza();
}
