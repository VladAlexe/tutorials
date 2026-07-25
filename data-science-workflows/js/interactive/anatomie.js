/* anatomie.js — o adresă lungă, segmentată și colorată. Apeși pe un segment și
   afli ce e, ce rol are și dacă e obligatoriu. Un exemplu generic și unul real.
   Date din continut/date/anatomie.json. */

import { incarcaDate, esc } from "./date.js";

const CLASA = { proto: "u-proto", host: "u-host", port: "u-port", path: "u-path", query: "u-query", frag: "u-frag" };

export default async function anatomie(gazda, parametri = {}) {
  const d = await incarcaDate(parametri.sursa || "anatomie.json");
  const adrese = d.adrese;
  let activ = 0;

  gazda.innerHTML = `
    <div class="filters" id="pick"></div>
    <div class="url" id="url" role="group" aria-label="Segmentele adresei"></div>
    <div class="c2__info" id="ai" role="region" aria-live="polite">
      <h4>Structura unei adrese</h4>
      <p>Apasă pe un segment colorat ca să afli ce e și dacă e obligatoriu.</p>
    </div>`;

  const pick = gazda.querySelector("#pick");
  const url = gazda.querySelector("#url");
  const info = gazda.querySelector("#ai");

  pick.innerHTML = adrese.map((a, i) =>
    `<button class="fbtn ${i === 0 ? "on" : ""}" data-i="${i}">${esc(a.eticheta)}</button>`).join("");

  function deseneaza() {
    const segmente = adrese[activ].segmente;
    url.innerHTML = segmente.map((s, i) => {
      if (s.t === "sep") return `<span class="u-sep">${esc(s.text)}</span>`;
      return `<button type="button" class="useg ${CLASA[s.t]}" data-i="${i}">${esc(s.text)}</button>`;
    }).join("");

    url.querySelectorAll(".useg").forEach((b) => b.addEventListener("click", () => {
      url.querySelectorAll(".useg").forEach((x) => x.classList.remove("on"));
      b.classList.add("on");
      const s = segmente[+b.dataset.i];
      info.innerHTML =
        `<h4>${esc(s.nume)}</h4>` +
        `<p>${esc(s.rol)}</p>` +
        `<p class="c2__tag">${s.oblig ? "Obligatoriu" : "Opțional"}</p>`;
    }));
  }

  pick.querySelectorAll(".fbtn").forEach((b) => b.addEventListener("click", () => {
    activ = +b.dataset.i;
    pick.querySelectorAll(".fbtn").forEach((x) => x.classList.toggle("on", x === b));
    deseneaza();
  }));

  deseneaza();
}
