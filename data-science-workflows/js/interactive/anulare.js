/* anulare.js — arbore de decizie. Răspunzi la două-trei întrebări despre ce ai
   făcut și primești comanda potrivită, cu explicația și cu ce se pierde.
   Un traseu, nu un tabel. Date din continut/date/anulare.json. */

import { incarcaDate, esc } from "./date.js";

export default async function anulare(gazda, parametri = {}) {
  const d = await incarcaDate(parametri.sursa || "anulare.json");
  const drum = [];

  function arata(cheie) {
    const nod = d.noduri[cheie];
    if (nod.rezultat) {
      gazda.innerHTML = `
        <div class="tree__res">
          <div style="font-family:var(--mono);font-size:15px;color:var(--ok);font-weight:600">${esc(nod.comanda)}</div>
          <b>CE FACE</b>${esc(nod.explicatie)}
          <b>CE PIERZI</b>${esc(nod.pierde)}
        </div>
        <button class="btn btn--ghost" id="a-reia" style="margin-top:14px">De la început</button>`;
      gazda.querySelector("#a-reia").addEventListener("click", () => { drum.length = 0; arata(d.start); });
      return;
    }
    gazda.innerHTML = `
      <p class="tree__q">${esc(nod.intrebare)}</p>
      <div class="filters">${nod.optiuni.map((o, i) => `<button class="fbtn" data-i="${i}">${esc(o.text)}</button>`).join("")}</div>
      ${drum.length ? '<button class="btn btn--ghost" id="a-inapoi" style="margin-top:12px">Înapoi</button>' : ""}`;
    gazda.querySelectorAll(".fbtn").forEach((b) => b.addEventListener("click", () => {
      drum.push(cheie); arata(nod.optiuni[+b.dataset.i].next);
    }));
    const inapoi = gazda.querySelector("#a-inapoi");
    if (inapoi) inapoi.addEventListener("click", () => arata(drum.pop()));
  }

  arata(d.start);
}
