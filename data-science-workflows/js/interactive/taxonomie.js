/* taxonomie.js — harta familiilor de API. Apeși pe o familie și vezi definiția,
   un exemplu real și când o întâlnești. Filtrul marchează ce apare în cercetarea
   socială. Date din continut/date/taxonomie.json. */

import { incarcaDate, esc } from "./date.js";

export default async function taxonomie(gazda, parametri = {}) {
  const d = await incarcaDate(parametri.sursa || "taxonomie.json");
  const grupuri = d.grupuri;
  // index plat pentru selecție
  const plat = [];
  grupuri.forEach((g) => g.membri.forEach((m) => plat.push(m)));
  let doarSocial = false;

  gazda.innerHTML = `
    <div class="filters">
      <button class="fbtn" id="flt" aria-pressed="false">Doar cele din cercetarea socială</button>
    </div>
    <div class="c2">
      <div class="c2__nodes" id="grid" style="flex-direction:column;gap:14px"></div>
      <div class="c2__info" id="ti" role="region" aria-live="polite">
        <h4>Patru familii</h4>
        <p>API-urile se clasifică pe mai multe axe deodată. Apasă pe oricare tip ca să vezi ce e și când îl întâlnești.</p>
      </div>
    </div>`;

  const grid = gazda.querySelector("#grid");
  const info = gazda.querySelector("#ti");

  function deseneaza() {
    grid.innerHTML = grupuri.map((g) => `
      <div>
        <div class="c2__tag" style="margin-bottom:6px">${esc(g.nume)}</div>
        <div style="display:flex;flex-wrap:wrap;gap:7px">
          ${g.membri.map((m) => {
            const idx = plat.indexOf(m);
            const estompat = doarSocial && !m.social;
            return `<button class="stage ${m.social ? "" : ""}" data-i="${idx}"
                      style="${estompat ? "opacity:.32" : ""}${m.social && doarSocial ? "border-color:var(--olive);background:rgba(110,115,88,.12)" : ""}">
                      ${esc(m.nume)}</button>`;
          }).join("")}
        </div>
      </div>`).join("");

    grid.querySelectorAll(".stage").forEach((b) => b.addEventListener("click", () => {
      grid.querySelectorAll(".stage").forEach((x) => x.classList.remove("is-on"));
      b.classList.add("is-on");
      const m = plat[+b.dataset.i];
      info.innerHTML =
        `<h4>${esc(m.nume)}</h4>` +
        `<p>${esc(m.definitie)}</p>` +
        `<p class="c2__tag">Exemplu</p><p class="c2__eg">${esc(m.exemplu)}</p>` +
        `<p class="c2__tag">Când o întâlnești</p><p>${esc(m.cand)}</p>` +
        `<p style="font-size:12px;color:var(--muted)">${m.social ? "Apare în cercetarea socială." : "Rar în cercetarea socială."}</p>`;
    }));
  }

  gazda.querySelector("#flt").addEventListener("click", (e) => {
    doarSocial = !doarSocial;
    e.currentTarget.classList.toggle("on", doarSocial);
    e.currentTarget.setAttribute("aria-pressed", String(doarSocial));
    deseneaza();
  });

  deseneaza();
}
