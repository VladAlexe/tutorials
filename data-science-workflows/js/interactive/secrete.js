/* secrete.js — același colector în două variante: cu cheia în cod și cu cheia în
   .env. Un comutator arată ce vede depozitul public. Al doilea arată istoricul
   Git, unde cheia rămâne vizibilă într-un commit vechi chiar după ce o ștergi.
   Date din continut/date/secrete.json. */

import { incarcaDate, esc } from "./date.js";

export default async function secrete(gazda, parametri = {}) {
  const d = await incarcaDate(parametri.sursa || "secrete.json");
  const V = d.variante;
  let activ = 0;
  let istoricDeschis = false;

  gazda.innerHTML = `
    <div class="toggles" id="s-var"></div>
    <div id="s-files"></div>
    <div class="c2__info" id="s-repo" style="margin-top:12px"></div>
    <div class="toggles" style="margin-top:16px">
      <button class="fbtn" id="s-hist" aria-expanded="false">Arată istoricul Git</button>
    </div>
    <div id="s-histbox"></div>`;

  const varBar = gazda.querySelector("#s-var");
  const files = gazda.querySelector("#s-files");
  const repo = gazda.querySelector("#s-repo");
  const histBox = gazda.querySelector("#s-histbox");

  varBar.innerHTML = V.map((v, i) =>
    `<button class="fbtn ${i === 0 ? "on" : ""}" data-i="${i}">${esc(v.eticheta)}</button>`).join("");

  function deseneaza() {
    const v = V[activ];
    files.innerHTML = v.fisiere.map((f) =>
      `<p class="c2__tag" style="margin:12px 0 5px">${esc(f.nume)}</p>
       <div class="resp" style="max-height:none">${esc(f.cod)}</div>`).join("");
    repo.innerHTML = `<h4>Ce vede depozitul public</h4><p>${esc(v.depozit)}</p>`;
  }

  varBar.querySelectorAll(".fbtn").forEach((b) => b.addEventListener("click", () => {
    activ = +b.dataset.i;
    varBar.querySelectorAll(".fbtn").forEach((x) => x.classList.toggle("on", x === b));
    deseneaza();
  }));

  gazda.querySelector("#s-hist").addEventListener("click", (e) => {
    istoricDeschis = !istoricDeschis;
    e.currentTarget.classList.toggle("on", istoricDeschis);
    e.currentTarget.setAttribute("aria-expanded", String(istoricDeschis));
    if (!istoricDeschis) { histBox.innerHTML = ""; return; }
    histBox.innerHTML = `
      <div class="resp" style="max-height:none">${d.istoric.map((c) =>
        `<span class="c">commit ${esc(c.hash)}</span>  ${esc(c.mesaj)}\n  ${c.expune
          ? `<span class="jn">API_KEY = "sk-live-8f3a2b9c4d7e"</span>   &lt;-- cheia e ÎNCĂ aici`
          : `<span class="js">(cod curat)</span>   ${esc(c.detaliu)}`}`).join("\n\n")}</div>
      <div class="trap"><b>ATENȚIE</b>Al doilea commit a scos cheia din fișier, dar primul commit o are încă în istoric. Ștergerea din cod nu ajunge — cheia trebuie <b style="font-family:var(--sans)">regenerată</b>.</div>`;
  });

  deseneaza();
}
