/* harta_doc.js — documentația reprodusă schematic, cu zone marcate. Apeși pe o
   zonă și afli ce cauți acolo. O sarcină mică: găsește parametrul care limitează
   numărul de rezultate. Date din continut/date/harta-doc.json. */

import { incarcaDate, esc } from "./date.js";

export default async function hartaDoc(gazda, parametri = {}) {
  const d = await incarcaDate(parametri.sursa || "harta-doc.json");
  const Z = d.zone;
  const sarcina = d.sarcina;

  gazda.innerHTML = `
    <div class="c2">
      <div class="doczones" id="hz" role="list" aria-label="Zonele documentației"></div>
      <div class="c2__info" id="hi" role="region" aria-live="polite">
        <h4>${esc(d.titlu)}</h4>
        <p>Apasă pe o zonă ca să afli ce găsești acolo.</p>
      </div>
    </div>
    <div style="margin-top:18px;padding-top:16px;border-top:1px solid var(--rule)">
      <p style="font-family:var(--sans);font-weight:600;font-size:14px;margin:0 0 10px">Sarcină: ${esc(sarcina.intrebare)}</p>
      <div class="filters" id="ht"></div>
      <p class="srt__fb" id="hf" role="status" aria-live="polite" style="min-height:24px"></p>
    </div>`;

  const zone = gazda.querySelector("#hz");
  const info = gazda.querySelector("#hi");
  zone.innerHTML = Z.map((z, i) =>
    `<button class="dzone" data-i="${i}" role="listitem"><b>${esc(z.eticheta)}</b><span>${esc(z.unde)}</span></button>`).join("");
  zone.querySelectorAll(".dzone").forEach((b) => b.addEventListener("click", () => {
    zone.querySelectorAll(".dzone").forEach((x) => x.classList.remove("on"));
    b.classList.add("on");
    const z = Z[+b.dataset.i];
    info.innerHTML = `<h4>${esc(z.eticheta)}</h4><p class="c2__eg">${esc(z.unde)}</p><p>${esc(z.explicatie)}</p>`;
  }));

  const task = gazda.querySelector("#ht");
  const fb = gazda.querySelector("#hf");
  task.innerHTML = sarcina.optiuni.map((o) => `<button class="fbtn" data-o="${esc(o)}">${esc(o)}</button>`).join("");
  task.querySelectorAll(".fbtn").forEach((b) => b.addEventListener("click", () => {
    const bun = b.dataset.o === sarcina.corect;
    task.querySelectorAll(".fbtn").forEach((x) => {
      x.disabled = true;
      if (x.dataset.o === sarcina.corect) x.classList.add("on");
    });
    fb.innerHTML = `<b>${bun ? "Corect." : "Nu."}</b> ${esc(sarcina.explicatie)}`;
  }));
}
