/* sincronizare.js — două panouri, local și la distanță, cu istoricele lor.
   Rulezi push / pull / fetch și vezi ce se mută și ce nu. Scenariul cel mai
   instructiv: altcineva a împins între timp, iar push-ul tău e respins. Fără rețea. */

import { esc } from "./date.js";

export default function sincronizare(gazda, parametri = {}) {
  const hexId = () => Math.random().toString(16).slice(2, 8);
  const base = [{ id: hexId(), msg: "primul commit" }];
  const localAhead = [];
  const remoteAhead = [];
  let fetched = false;
  let n = 1;

  if (parametri.seedRemoteAhead) remoteAhead.push({ id: hexId(), msg: "colegul a adăugat curățarea" });

  function nod(c, cls) { return `<div class="snode ${cls}">${c.id.slice(0, 6)}  ${esc(c.msg)}</div>`; }

  function render() {
    gazda.querySelector("#sy-local").innerHTML =
      base.map((c) => nod(c, "")).join("") + localAhead.map((c) => nod(c, "ahead")).join("");
    gazda.querySelector("#sy-remote").innerHTML =
      base.map((c) => nod(c, "")).join("") + remoteAhead.map((c) => nod(c, "ahead")).join("");
    gazda.querySelector("#sy-fb").innerHTML = mesaj;
  }

  let mesaj = 'Local ești cu <b>' + localAhead.length + '</b> commituri înainte. Apasă o comandă.';

  function push() {
    if (remoteAhead.length) {
      mesaj = `<b style="color:var(--no)">! [rejected] push respins.</b> Depozitul la distanță are commituri pe care tu nu le ai (colegul a împins între timp). Git cere „fetch first”. Fă <code>git pull</code> întâi.`;
    } else if (!localAhead.length) {
      mesaj = "Nimic de împins — local și la distanță sunt la fel.";
    } else {
      const k = localAhead.length;
      while (localAhead.length) base.push(localAhead.shift());
      mesaj = `<b>push reușit.</b> ${k} commit(uri) au urcat. Acum ambele istorice sunt la fel.`;
    }
    render();
  }
  function fetchR() {
    fetched = true;
    mesaj = remoteAhead.length
      ? `<b>fetch.</b> Ai adus referințele colegului: cele ${remoteAhead.length} commituri sunt acum <em>cunoscute</em>, dar NU au fost îmbinate în ce lucrezi. Diferența dintre fetch și pull.`
      : "<b>fetch.</b> Nimic nou la distanță.";
    render();
  }
  function pull() {
    if (!remoteAhead.length) { mesaj = "<b>pull.</b> Ești deja la zi — nimic de adus."; render(); return; }
    const k = remoteAhead.length;
    while (remoteAhead.length) base.push(remoteAhead.shift());
    fetched = false;
    mesaj = `<b>pull.</b> Am adus și am îmbinat ${k} commit(uri) ale colegului. Acum poți face push fără să fii respins.`;
    render();
  }

  gazda.innerHTML = `
    <div class="sync">
      <div class="sync__p"><h5>Local (laptopul tău)</h5><div id="sy-local"></div></div>
      <div class="sync__arrow">push →<br>← pull / fetch</div>
      <div class="sync__p"><h5>La distanță (GitHub)</h5><div id="sy-remote"></div></div>
    </div>
    <div class="filters">
      <button class="fbtn" id="sy-commit">commit local</button>
      <button class="fbtn" id="sy-coleg">colegul împinge</button>
      <button class="fbtn" id="sy-push">git push</button>
      <button class="fbtn" id="sy-fetch">git fetch</button>
      <button class="fbtn" id="sy-pull">git pull</button>
    </div>
    <p class="srt__fb" id="sy-fb" style="min-height:40px"></p>`;

  gazda.querySelector("#sy-commit").addEventListener("click", () => { localAhead.push({ id: hexId(), msg: "muncă locală " + n++ }); mesaj = "Ai un commit local nou, netrimis încă."; render(); });
  gazda.querySelector("#sy-coleg").addEventListener("click", () => { remoteAhead.push({ id: hexId(), msg: "commit de la coleg" }); mesaj = "Colegul a împins un commit la distanță. Tu încă nu-l ai."; render(); });
  gazda.querySelector("#sy-push").addEventListener("click", push);
  gazda.querySelector("#sy-fetch").addEventListener("click", fetchR);
  gazda.querySelector("#sy-pull").addEventListener("click", pull);

  render();
}
