/* coduri.js — trimiți cereri corecte și greșite către ambele API-uri și vezi
   codul de stare, antetul și corpul. Cazul 200-înșelător de la Banca Mondială e
   marcat vizual ca fiind capcana. Răspunsuri salvate în continut/date/coduri.json. */

import { incarcaDate, esc } from "./date.js";

const CLASA_HTTP = { ok: "http--ok", warn: "http--warn", err: "http--err" };

export default async function coduri(gazda, parametri = {}) {
  const d = await incarcaDate(parametri.sursa || "coduri.json");
  const S = d.scenarii;

  gazda.innerHTML = `
    <div class="filters" id="k-list"></div>
    <div id="k-out" aria-live="polite"></div>`;

  const list = gazda.querySelector("#k-list");
  const out = gazda.querySelector("#k-out");

  list.innerHTML = S.map((s, i) =>
    `<button class="fbtn ${i === 0 ? "on" : ""}" data-i="${i}">${esc(s.api)}: ${esc(s.eticheta)}</button>`).join("");

  function arata(i) {
    const s = S[i];
    const clasa = CLASA_HTTP[s.clasa] || "http--warn";
    out.innerHTML = `
      <p style="font-family:var(--mono);font-size:12.5px;color:var(--muted);margin:4px 0 10px">${esc(s.cerere)}</p>
      <p><span class="http ${clasa}">${esc(s.status)}</span></p>
      <div class="resp" style="max-height:240px">${s.antet.map((h) => `<span class="c">${esc(h)}</span>`).join("\n")}\n\n${esc(s.corp)}</div>
      ${s.capcana
        ? `<div class="trap"><b>CAPCANĂ</b>Cod 200, dar corpul e o eroare. La Banca Mondială, codul de stare nu e suficient — uită-te întotdeauna și în corp. ${esc(s.urmator)}</div>`
        : `<p style="font-size:13.5px;color:var(--muted);margin:10px 0 0"><b style="font-family:var(--sans);color:var(--ink)">Ce faci mai departe:</b> ${esc(s.urmator)}</p>`}`;
  }

  list.querySelectorAll(".fbtn").forEach((b) => b.addEventListener("click", () => {
    list.querySelectorAll(".fbtn").forEach((x) => x.classList.toggle("on", x === b));
    arata(+b.dataset.i);
  }));

  arata(0);
}
