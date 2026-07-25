/* zone.js — trei coloane (dosar de lucru, zonă de pregătire, depozit) cu fișiere
   care se mută între ele. Un fișier modificat DUPĂ adăugare apare în două zone
   deodată — confuzia clasică, arătată vizual. Stare proprie, fără rețea. */

import { esc } from "./date.js";

export default function zone(gazda, parametri = {}) {
  const nume = parametri.fisiere || ["colector.py", "README.md"];
  // stare per fișier: tracked, staged, workMod
  const F = {};
  nume.forEach((n) => F[n] = { tracked: false, staged: false, workMod: false });

  function inWork(f) { return !f.tracked && !f.staged || f.workMod; }   // untracked, sau modificat după add/commit
  function inRepo(f) { return f.tracked; }

  function actiuni(n) {
    const f = F[n];
    const a = [];
    if ((!f.tracked && !f.staged) || (f.tracked && f.workMod)) a.push({ t: "git add", fn: () => { f.staged = true; f.workMod = false; } });
    if (f.staged || f.tracked) a.push({ t: "edit", fn: () => { f.workMod = true; } });
    if (f.staged) a.push({ t: "restore --staged", fn: () => { f.staged = false; if (f.tracked) f.workMod = true; } });
    if (f.tracked && f.workMod) a.push({ t: "restore", fn: () => { f.workMod = false; } });
    return a;
  }

  function render() {
    const work = Object.entries(F).filter(([, f]) => (!f.tracked && !f.staged) || f.workMod);
    const stage = Object.entries(F).filter(([, f]) => f.staged);
    const repo = Object.entries(F).filter(([, f]) => f.tracked);
    const dup = (n) => F[n].staged && F[n].workMod;

    gazda.querySelector("#z-cols").innerHTML = `
      <div class="zcol work"><h5>Dosar de lucru</h5><small>unde editezi</small>
        ${work.map(([n]) => `<span class="zfile ${dup(n) ? "dup" : ""}">${esc(n)}</span>`).join("") || '<span style="color:var(--muted);font-size:12px">gol</span>'}</div>
      <div class="zcol stage"><h5>Zonă de pregătire</h5><small>ce intră în commit</small>
        ${stage.map(([n]) => `<span class="zfile ${dup(n) ? "dup" : ""}">${esc(n)}</span>`).join("") || '<span style="color:var(--muted);font-size:12px">gol</span>'}</div>
      <div class="zcol repo"><h5>Depozit</h5><small>înregistrat definitiv</small>
        ${repo.map(([n]) => `<span class="zfile">${esc(n)}</span>`).join("") || '<span style="color:var(--muted);font-size:12px">gol</span>'}</div>`;

    gazda.querySelector("#z-ctrl").innerHTML = nume.map((n) => `
      <div style="margin:0 0 8px">
        <span style="font-family:var(--mono);font-size:12px;font-weight:600">${esc(n)}</span>
        ${actiuni(n).map((a, i) => `<button class="fbtn" data-n="${esc(n)}" data-i="${i}" style="margin-left:6px">${a.t}</button>`).join("")}
      </div>`).join("") +
      `<button class="btn" id="z-commit" style="margin-top:6px">git commit -m "…"</button>
       <p class="srt__fb" id="z-fb" style="min-height:20px"></p>`;

    gazda.querySelectorAll("#z-ctrl .fbtn").forEach((b) => b.addEventListener("click", () => {
      const n = b.dataset.n, a = actiuni(n)[+b.dataset.i];
      a.fn(); render();
      if (F[n].staged && F[n].workMod)
        gazda.querySelector("#z-fb").innerHTML = `<b>Vezi?</b> ${esc(n)} apare în ambele zone: versiunea pregătită e cea de la add, dar ai modificat fișierul din nou. La commit se înregistrează doar ce era pregătit.`;
    }));
    gazda.querySelector("#z-commit").addEventListener("click", () => {
      const st = Object.values(F).filter((f) => f.staged);
      if (!st.length) { gazda.querySelector("#z-fb").textContent = "Nimic în zona de pregătire — nu ai ce înregistra."; return; }
      st.forEach((f) => { f.tracked = true; f.staged = false; });
      render();
      gazda.querySelector("#z-fb").textContent = "Commit făcut. Ce era pregătit a ajuns în depozit; modificările nepregătite au rămas în dosarul de lucru.";
    });
  }

  gazda.innerHTML = `<div class="zones" id="z-cols"></div><div id="z-ctrl"></div>`;
  render();
}
