/* restaurant.js — analogia restaurantului: cinci elemente, fiecare cu
   corespondentul tehnic și o explicație. Date din continut/date/restaurant.json. */

import { incarcaDate, esc } from "./date.js";

export default async function restaurant(gazda, parametri = {}) {
  const d = await incarcaDate(parametri.sursa || "restaurant.json");
  const E = d.elemente;

  gazda.innerHTML = `
    <div class="rest">
      ${E.map((e, i) => `
        <button class="rest__node" data-i="${i}" aria-pressed="false">
          <div class="rest__ico" aria-hidden="true">${e.ico}</div>
          <div class="rest__n">${esc(e.nume)}</div>
        </button>
        ${i < E.length - 1 ? '<span class="rest__arrow" aria-hidden="true">→</span>' : ""}`).join("")}
    </div>
    <div class="c2__info" id="ri" role="region" aria-live="polite">
      <h4>Cinci elemente</h4>
      <p>Apasă pe fiecare ca să vezi ce reprezintă, tehnic, în lumea unui API.</p>
    </div>`;

  const info = gazda.querySelector("#ri");
  const noduri = gazda.querySelectorAll(".rest__node");
  noduri.forEach((b) => b.addEventListener("click", () => {
    noduri.forEach((x) => { x.classList.remove("on"); x.setAttribute("aria-pressed", "false"); });
    b.classList.add("on"); b.setAttribute("aria-pressed", "true");
    const e = E[+b.dataset.i];
    info.innerHTML =
      `<h4>${esc(e.nume)}</h4>` +
      `<p class="c2__tag">= ${esc(e.tehnic)}</p>` +
      `<p>${esc(e.explicatie)}</p>`;
  }));
}
