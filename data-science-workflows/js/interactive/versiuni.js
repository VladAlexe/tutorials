/* versiuni.js — două panouri paralele: un dosar cu fișiere numite manual și un
   istoric Git al aceluiași proiect. Pui aceeași întrebare amândurora și vezi că
   unul răspunde, celălalt nu. Date din continut/date/versiuni.json. */

import { incarcaDate, esc } from "./date.js";

export default async function versiuni(gazda, parametri = {}) {
  const d = await incarcaDate(parametri.sursa || "versiuni.json");

  gazda.innerHTML = `
    <div class="filters" id="v-q"></div>
    <div class="vs2">
      <div class="vs2__p folder">
        <h5>Dosar cu fișiere numite manual</h5>
        <div style="font-family:var(--mono);font-size:11.5px;color:var(--muted);line-height:1.9;margin:0 0 10px">
          ${d.folderFisiere.map((f) => esc(f)).join("<br>")}
        </div>
        <div class="vs2__ans no" id="v-folder">—</div>
      </div>
      <div class="vs2__p git">
        <h5>Istoric Git al aceluiași proiect</h5>
        <div style="font-family:var(--mono);font-size:11.5px;color:var(--muted);line-height:1.9;margin:0 0 10px">
          $ git log --oneline<br>a3f1c9 curăț coloana ani<br>7b20e4 adaug colectorul<br>1d4e8a primul commit
        </div>
        <div class="vs2__ans" id="v-git">—</div>
      </div>
    </div>`;

  const q = gazda.querySelector("#v-q");
  const fol = gazda.querySelector("#v-folder");
  const git = gazda.querySelector("#v-git");
  q.innerHTML = d.intrebari.map((it, i) => `<button class="fbtn ${i === 0 ? "" : ""}" data-i="${i}">${esc(it.q)}</button>`).join("");
  q.querySelectorAll(".fbtn").forEach((b) => b.addEventListener("click", () => {
    q.querySelectorAll(".fbtn").forEach((x) => x.classList.toggle("on", x === b));
    const it = d.intrebari[+b.dataset.i];
    fol.textContent = it.folder;
    git.textContent = it.git;
  }));
}
