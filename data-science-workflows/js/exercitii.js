/* ===========================================================================
   EXERCIȚII CU COD

   Două feluri, amândouă fără Python în browser: se verifică forma a ceea ce
   scrii, nu rezultatul rulării. E o alegere, nu o scurtătură. Un interpretor
   în pagină ar însemna câteva megaocteți descărcați la începutul orei, pe
   același wifi, de 25 de oameni deodată. Rularea adevărată se face în caiet,
   la ei în VS Code, unde și trebuie să se întâmple.

     <div class="ix" data-ix="cod">      completezi golurile dintr-un cod
     <div class="ix" data-ix="ordine">   pui liniile în ordinea corectă

   Amândouă contează ca poartă: nu treci la slide-ul următor până nu le faci,
   exact ca la verificări. Se salvează prin salveazaCod, deci apar la mine în
   panou ca activitate.
   =========================================================================== */

import { salveazaCod } from "./colectare.js?v=4";

const E = {};

const SVG_SUS = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19V6M6 11.5 12 5.5l6 6"/></svg>';
const SVG_JOS = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5v13M6 12.5l6 6 6-6"/></svg>';

const esc = s => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

/** Colorare minimală: suficient cât să semene cu un editor, fără bibliotecă. */
function coloreaza(s){
  return esc(s)
    .replace(/(#[^\n]*)/g, '<span class="c">$1</span>')
    .replace(/('[^']*'|&quot;[^&]*&quot;|"[^"]*")/g, '<span class="s">$1</span>')
    .replace(/\b(import|from|as|def|return|if|else|elif|for|in|while|with|open|print|None|True|False|not|and|or)\b/g,
             '<span class="k">$1</span>')
    .replace(/\b(\d+\.?\d*)\b/g, '<span class="n">$1</span>');
}

/** Normalizare înainte de comparație: spațiile și ghilimelele nu contează. */
const normal = s => String(s).trim()
  .replace(/\s+/g, " ")
  .replace(/[“”„]/g, '"')
  .replace(/[‘’]/g, "'");

/** Marchează exercițiul ca poartă trecută și anunță rulatorul de slide-uri. */
function gata(gazda, id){
  const ix = gazda.closest(".ix") || gazda;
  ix.classList.add("gata");
  document.dispatchEvent(new CustomEvent("poarta:gata", { detail:{ id } }));
}

function cadruJos(){
  return `<div class="ex__jos">
      <button class="btn btn--mic btn--tare" data-rol="verifica" type="button">Verifică</button>
      <button class="btn btn--mic" data-rol="din-nou" type="button" hidden>Încearcă din nou</button>
      <span class="ex__raspuns"></span>
    </div>
    <p class="ex__ex"></p>
    <p class="ex__stare"></p>`;
}

/* ==========================================================================
   1. Completează golurile
   ========================================================================== */

E.cod = (gazda, d) => {
  const id = d.id || "cod";
  gazda.closest(".ix")?.classList.add("exc");

  /* `cod` e un bloc de text cu {{1}}, {{2}} … în locurile de completat */
  const linii = d.cod.replace(/\t/g, "    ").split("\n");
  const corp = linii.map(l => {
    let h = coloreaza(l);
    h = h.replace(/\{\{(\w+)\}\}/g, (_, k) => {
      const g = d.goluri[k] || {};
      const lat = Math.max(5, (g.ok?.[0] || "").length + 2);
      return `<input class="gol" data-k="${k}" size="${lat}" spellcheck="false"
                autocapitalize="off" autocomplete="off"
                placeholder="${esc(g.ajutor || "…")}" aria-label="Golul ${k}">`;
    });
    return h || "&nbsp;";
  }).join("\n");

  gazda.innerHTML = `
    ${d.sarcina ? `<p class="ex__sarcina">${d.sarcina}</p>` : ""}
    <div class="ed">
      <div class="ed__bara"><span class="ed__pct"><i></i><i></i><i></i></span>
        <span class="ed__nume">${esc(d.fisier || "exercitiu.py")}</span></div>
      <div class="ed__corp">
        <div class="ed__nr">${linii.map((_, i) => `<span>${i + 1}</span>`).join("")}</div>
        <div class="ed__cod">${corp}</div>
      </div>
    </div>
    ${cadruJos()}`;

  const goluri = [...gazda.querySelectorAll(".gol")];
  const btV = gazda.querySelector('[data-rol="verifica"]');
  const btN = gazda.querySelector('[data-rol="din-nou"]');
  const out = gazda.querySelector(".ex__raspuns");
  const ex  = gazda.querySelector(".ex__ex");
  const st  = gazda.querySelector(".ex__stare");

  goluri.forEach(g => g.addEventListener("keydown", e => {
    if (e.key === "Enter"){ e.preventDefault(); btV.click(); }
  }));

  btV.onclick = async () => {
    let bune = 0;
    goluri.forEach(g => {
      const asteptat = (d.goluri[g.dataset.k]?.ok || []).map(normal);
      const ok = asteptat.includes(normal(g.value));
      g.classList.toggle("bun", ok);
      g.classList.toggle("rau", !ok);
      if (ok) bune++;
    });
    const tot = bune === goluri.length;
    out.innerHTML = tot
      ? `<b>Corect.</b> ${d.laBine || ""}`
      : `<b>${bune} din ${goluri.length}.</b> ${d.laRau || "Golurile roșii nu sunt încă bune."}`;
    btN.hidden = tot;
    if (tot){
      btV.disabled = true;
      goluri.forEach(g => g.disabled = true);
      ex.classList.add("vazut");
      ex.innerHTML = d.explicatie || "";
      gata(gazda, id);
      const salvat = await salveazaCod({
        exercitiuId: id,
        cod: goluri.map(g => `${g.dataset.k}=${g.value}`).join(" | "),
        trecut: true
      });
      st.textContent = salvat ? "Rezolvare înregistrată."
                              : "Nu e înregistrată: nu ești autentificat.";
      st.classList.add("vazut");
    }
  };
  btN.onclick = () => {
    goluri.forEach(g => { g.classList.remove("bun", "rau"); });
    out.textContent = ""; btN.hidden = true;
    goluri[0]?.focus();
  };
};

/* ==========================================================================
   2. Pune liniile în ordine
   ========================================================================== */

E.ordine = (gazda, d) => {
  const id = d.id || "ordine";
  gazda.closest(".ix")?.classList.add("exc");

  /* amestecăm, dar niciodată în ordinea corectă din prima */
  const n = d.linii.length;
  let ordine = d.linii.map((_, i) => i);
  do { ordine = amesteca(ordine); } while (ordine.every((v, i) => v === i) && n > 1);

  gazda.innerHTML = `
    ${d.sarcina ? `<p class="ex__sarcina">${d.sarcina}</p>` : ""}
    <div class="ord"></div>
    ${cadruJos()}`;

  const lista = gazda.querySelector(".ord");
  const btV = gazda.querySelector('[data-rol="verifica"]');
  const btN = gazda.querySelector('[data-rol="din-nou"]');
  const out = gazda.querySelector(".ex__raspuns");
  const ex  = gazda.querySelector(".ex__ex");
  const st  = gazda.querySelector(".ex__stare");

  function deseneaza(){
    lista.innerHTML = ordine.map((k, poz) => `
      <div class="ord__r" data-poz="${poz}">
        <span class="ord__p">${poz + 1}</span>
        <span class="ord__t">${coloreaza(d.linii[k])}</span>
        <span class="ord__b">
          <button type="button" data-m="-1" ${poz === 0 ? "disabled" : ""}
            aria-label="Mută mai sus">${SVG_SUS}</button>
          <button type="button" data-m="1" ${poz === n - 1 ? "disabled" : ""}
            aria-label="Mută mai jos">${SVG_JOS}</button>
        </span>
      </div>`).join("");
  }
  deseneaza();

  lista.addEventListener("click", e => {
    const b = e.target.closest("button[data-m]");
    if (!b) return;
    const poz = +b.closest(".ord__r").dataset.poz;
    const la = poz + (+b.dataset.m);
    if (la < 0 || la >= n) return;
    [ordine[poz], ordine[la]] = [ordine[la], ordine[poz]];
    deseneaza();
    out.textContent = "";
  });

  btV.onclick = async () => {
    const randuri = [...lista.querySelectorAll(".ord__r")];
    let bune = 0;
    ordine.forEach((k, poz) => {
      const ok = k === poz;
      randuri[poz].classList.toggle("bun", ok);
      randuri[poz].classList.toggle("rau", !ok);
      if (ok) bune++;
    });
    const tot = bune === n;
    out.innerHTML = tot
      ? `<b>Corect.</b> ${d.laBine || ""}`
      : `<b>${bune} din ${n} pe locul lor.</b> ${d.laRau || "Mută-le pe celelalte."}`;
    btN.hidden = tot;
    if (tot){
      btV.disabled = true;
      lista.querySelectorAll("button").forEach(b => b.disabled = true);
      ex.classList.add("vazut");
      ex.innerHTML = d.explicatie || "";
      gata(gazda, id);
      const salvat = await salveazaCod({
        exercitiuId: id, cod: ordine.join(","), trecut: true
      });
      st.textContent = salvat ? "Rezolvare înregistrată."
                              : "Nu e înregistrată: nu ești autentificat.";
      st.classList.add("vazut");
    }
  };
  btN.onclick = () => {
    lista.querySelectorAll(".ord__r").forEach(r => r.classList.remove("bun", "rau"));
    out.textContent = ""; btN.hidden = true;
  };
};

function amesteca(a){
  const b = a.slice();
  for (let i = b.length - 1; i > 0; i--){
    const j = Math.floor(Math.random() * (i + 1));
    [b[i], b[j]] = [b[j], b[i]];
  }
  return b;
}

export default E;
