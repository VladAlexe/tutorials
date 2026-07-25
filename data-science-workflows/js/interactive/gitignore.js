/* gitignore.js — un arbore de fișiere realist și un editor de tipare. Scrii un
   tipar și vezi imediat ce fișiere devin ignorate și care rămân. Cazul-capcană:
   un fișier deja urmărit NU dispare doar pentru că îl adaugi în .gitignore.
   Date din continut/date/gitignore.json. */

import { incarcaDate, esc } from "./date.js";

function bazename(cale) {
  return cale.replace(/\/$/, "").split("/").filter(Boolean).pop();
}

function seLoveste(tipar, cale) {
  if (tipar.endsWith("/")) {
    const dir = tipar.slice(0, -1);
    return cale === tipar || cale.startsWith(tipar) || cale.split("/").includes(dir);
  }
  if (tipar.startsWith("*.")) return bazename(cale).endsWith(tipar.slice(1));
  return bazename(cale) === tipar || cale === tipar;
}

function ignorat(tipare, cale) {
  return tipare
    .split("\n").map((l) => l.trim())
    .filter((l) => l && !l.startsWith("#"))
    .some((t) => seLoveste(t, cale));
}

export default async function gitignore(gazda, parametri = {}) {
  const d = await incarcaDate(parametri.sursa || "gitignore.json");

  gazda.innerHTML = `
    <div class="gi">
      <div>
        <p class="c2__tag" style="margin:0 0 6px">.gitignore</p>
        <textarea id="gi-pat" spellcheck="false" style="width:100%;height:190px;font-family:var(--mono);
          font-size:12.5px;padding:12px;border:1.5px solid var(--rule-strong);border-radius:6px;
          background:var(--panel);color:#DADAD6;resize:vertical">${esc(d.tipareInitiale || "")}</textarea>
      </div>
      <div>
        <p class="c2__tag" style="margin:0 0 6px">Fișierele proiectului</p>
        <div class="gitree" id="gi-tree"></div>
        <p class="srt__fb" id="gi-fb" style="min-height:20px;font-size:13px"></p>
      </div>
    </div>`;

  const pat = gazda.querySelector("#gi-pat");
  const tree = gazda.querySelector("#gi-tree");
  const fb = gazda.querySelector("#gi-fb");

  function deseneaza() {
    let capcana = false;
    tree.innerHTML = d.fisiere.map((f) => {
      const m = ignorat(pat.value, f.cale);
      let cls = "";
      if (m && f.tracked) { cls = "trap"; capcana = true; }
      else if (m) cls = "ign";
      return `<span class="gifile ${cls}">${esc(f.cale)}</span>`;
    }).join("");
    fb.innerHTML = capcana
      ? `<b style="color:var(--no)">Capcană:</b> un tipar se potrivește cu un fișier <b>deja urmărit</b> (.env a fost comis înainte). Adăugarea în .gitignore nu îl scoate din trecut — trebuie <code>git rm --cached</code>, iar dacă era un secret, regenerat.`
      : "Fișierele tăiate sunt ignorate: Git nu le va mai urmări.";
  }

  pat.addEventListener("input", deseneaza);
  deseneaza();
}
