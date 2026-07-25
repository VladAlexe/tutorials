/* surse.js — catalog filtrabil de surse reale accesibile prin API: tip, dacă cere
   cheie, ce format întoarce, o legătură către documentația oficială și o linie
   despre ce întrebare sociologică ar putea susține. Filtrare după domeniu.
   Date din continut/date/surse.json. */

import { incarcaDate, esc } from "./date.js";

export default async function surse(gazda, parametri = {}) {
  const d = await incarcaDate(parametri.sursa || "surse.json");
  const S = d.surse;
  const domenii = ["Toate", ...Array.from(new Set(S.map((s) => s.domeniu)))];
  let filtru = "Toate";

  gazda.innerHTML = `
    <div class="filters" id="su-f"></div>
    <div class="cards" id="su-c"></div>`;

  const f = gazda.querySelector("#su-f");
  const c = gazda.querySelector("#su-c");

  f.innerHTML = domenii.map((dm, i) =>
    `<button class="fbtn ${i === 0 ? "on" : ""}" data-d="${esc(dm)}">${esc(dm)}</button>`).join("");

  function deseneaza() {
    const lista = filtru === "Toate" ? S : S.filter((s) => s.domeniu === filtru);
    c.innerHTML = lista.map((s) => `
      <div class="scard">
        <h5>${esc(s.nume)}</h5>
        <div class="scard__meta">
          <div><b>Tip:</b> ${esc(s.tip)}</div>
          <div><b>Format:</b> ${esc(s.format)}</div>
          <div><b>Cheie:</b> <span class="tag-key ${s.cheie ? "yes" : "no"}">${s.cheie ? "necesară" : "fără"}</span></div>
        </div>
        <p class="scard__q">${esc(s.intrebare)}</p>
        <a href="${esc(s.url)}" target="_blank" rel="noopener">Documentație ↗</a>
      </div>`).join("");
  }

  f.querySelectorAll(".fbtn").forEach((b) => b.addEventListener("click", () => {
    filtru = b.dataset.d;
    f.querySelectorAll(".fbtn").forEach((x) => x.classList.toggle("on", x === b));
    deseneaza();
  }));

  deseneaza();
}
