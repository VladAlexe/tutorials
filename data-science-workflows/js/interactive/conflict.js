/* conflict.js — un conflict real într-un fișier: vezi ambele versiuni, alegi sau
   editezi, obții fișierul rezolvat. Al doilea scenariu, la fel de important: două
   modificări care NU produc conflict, ca să se vadă că Git nu e capricios.
   Date din continut/date/conflict.json. */

import { incarcaDate, esc } from "./date.js";

export default async function conflict(gazda, parametri = {}) {
  const d = await incarcaDate(parametri.sursa || "conflict.json");
  let activ = 0;

  gazda.innerHTML = `
    <div class="toggles" id="cf-mod"></div>
    <div id="cf-body"></div>`;

  const mod = gazda.querySelector("#cf-mod");
  const body = gazda.querySelector("#cf-body");
  mod.innerHTML = d.scenarii.map((s, i) => `<button class="fbtn ${i === 0 ? "on" : ""}" data-i="${i}">${esc(s.titlu)}</button>`).join("");

  function conflictView(s) {
    body.innerHTML = `
      <p style="font-family:var(--mono);font-size:12px;color:var(--muted);margin:0 0 8px">${esc(s.fisier)} — conflict</p>
      <div class="cf-file">${esc(s.sus)}
<span class="cf-mark">&lt;&lt;&lt;&lt;&lt;&lt;&lt; HEAD (al tău)</span>
<span class="cf-ours">${esc(s.ours)}</span><span class="cf-mark">=======</span>
<span class="cf-theirs">${esc(s.theirs)}</span><span class="cf-mark">&gt;&gt;&gt;&gt;&gt;&gt;&gt; feature (al colegului)</span>
${esc(s.jos)}</div>
      <p style="font-size:14px;color:var(--muted);margin:0 0 10px">${esc(s.explicatie)}</p>
      <div class="filters">
        <button class="fbtn" data-r="ours">Păstrează versiunea ta</button>
        <button class="fbtn" data-r="theirs">Păstrează versiunea lui</button>
        <button class="fbtn" data-r="combin">Combină manual</button>
      </div>
      <div id="cf-out"></div>`;
    body.querySelectorAll("[data-r]").forEach((b) => b.addEventListener("click", () => {
      body.querySelectorAll("[data-r]").forEach((x) => x.classList.toggle("on", x === b));
      const val = b.dataset.r === "ours" ? s.ours : b.dataset.r === "theirs" ? s.theirs : s.combinat;
      const rezolvat = [s.sus, val, s.jos].join("\n");
      body.querySelector("#cf-out").innerHTML = `
        <p class="c2__tag" style="margin:12px 0 5px">Fișier rezolvat</p>
        <div class="cf-file">${esc(rezolvat)}</div>
        <p style="font-size:13.5px;color:var(--muted)">Marcajele au dispărut. Acum îl consemnezi:
        <code>git add ${esc(s.fisier)}</code> apoi <code>git commit</code>.</p>`;
    }));
  }

  function noConflictView(s) {
    body.innerHTML = `
      <p style="font-size:14px;color:var(--muted);margin:0 0 12px">${esc(s.explicatie)}</p>
      <p class="c2__tag" style="margin:0 0 5px">${esc(s.fisier)} — îmbinat automat, fără intervenția ta</p>
      <div class="cf-file">${esc(s.rezolvat)}</div>`;
  }

  function arata() {
    const s = d.scenarii[activ];
    if (s.conflict) conflictView(s); else noConflictView(s);
  }

  mod.querySelectorAll(".fbtn").forEach((b) => b.addEventListener("click", () => {
    activ = +b.dataset.i;
    mod.querySelectorAll(".fbtn").forEach((x) => x.classList.toggle("on", x === b));
    arata();
  }));
  arata();
}
