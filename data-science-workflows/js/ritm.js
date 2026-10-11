/* ===========================================================================
   ORA CONDUSĂ

   La curs, toată lumea trebuie să fie pe același slide. Altfel „uitați-vă la
   slide-ul 9" înseamnă treizeci de oameni care caută slide-ul 9.

   Cât timp profesorul conduce ora, pagina studentului se mută singură după
   el. Nimeni nu e însă blocat: există oricând butonul „mă uit singur", iar
   după el butonul de întoarcere în ritm.

   Se folosește doar din js/slide.js:

     const r = await porneste({ capitol, total, esteProfesor, mergiLa, unde });
     r?.publica(nr);        // profesorul, la fiecare schimbare de slide

   Fără cont, fără rețea sau fără tabelul `ritm` în baza de date, modulul
   iese tăcut și lecția merge exact ca înainte.
   =========================================================================== */

import { RADACINA } from "./curs.js?v=7";

const PAS_STUDENT  = 3000;    /* cât de des întreabă studentul unde e profesorul */
const PAS_PROFESOR = 12000;   /* cât de des numără profesorul cine e în sală */

export async function porneste({ capitol, total, esteProfesor, mergiLa, unde,
                                 manual, laStare }){
  let A;
  try { A = await import(`${RADACINA}/js/auth.js?v=7`); }
  catch { return null; }

  let p = null;
  try { p = await A.profil(); } catch { return null; }
  if (!p?.autentificat) return null;

  const sb = A.sb;
  const bara = construieste();
  let ceas = null;

  /* ------------------------------------------------------------ profesor --- */
  if (esteProfesor){
    let pornit = false, inSala = 0;

    const scrie = async (nr, pornitNou) => {
      try {
        const { data } = await sb.rpc("pune_ritm", {
          p_capitol: capitol, p_slide_nr: nr ?? null,
          p_total_nr: total, p_pornit: pornitNou ?? null });
        if (data && data.ok !== false) pornit = !!data.pornit;
        return data;
      } catch { return null; }
    };

    /* dacă ora era deja pornită de pe alt calculator, o luăm de acolo */
    try {
      const { data } = await sb.rpc("citeste_ritm", { p_capitol: capitol });
      pornit = !!data?.pornit;
    } catch { /* fără tabel, butonul rămâne, dar nu face nimic */ }

    const numara = async () => {
      try {
        const { data } = await sb.rpc("live_acum", { p_minute: 3 });
        inSala = (data || []).filter(x => x.capitol === capitol).length;
      } catch { inSala = 0; }
      deseneaza();
    };

    function deseneaza(){
      bara.hidden = false;
      bara.className = "ritm ritm--prof" + (pornit ? " ritm--on" : "");
      bara.innerHTML = `
        <span class="ritm__pct"></span>
        <span class="ritm__t">${pornit ? "Conduci ora" : "Ora nu e condusă"}</span>
        <span class="ritm__d">${pornit
          ? `toți sar pe slide-ul tău · ${inSala} ${inSala === 1 ? "om" : "oameni"} în lecție`
          : "fiecare umblă în ritmul lui"}</span>
        <button class="ritm__b" type="button">${pornit ? "Oprește" : "Condu ora"}</button>`;
      bara.querySelector(".ritm__b").onclick = async () => {
        const d = await scrie(unde(), !pornit);
        if (d && d.ok === false){ bara.querySelector(".ritm__d").textContent = d.mesaj; return; }
        deseneaza(); laStare?.(pornit);
      };
    }

    deseneaza(); numara(); laStare?.(pornit);
    ceas = setInterval(() => { if (!document.hidden && pornit) numara(); }, PAS_PROFESOR);

    return {
      publica(nr){ if (pornit) scrie(nr); },
      opreste(){ clearInterval(ceas); }
    };
  }

  /* ------------------------------------------------------------- student --- */
  /* Nu există buton de desprindere: cât ține ora, pagina lui e pagina mea.
     Ce poate face e să deschidă manualul în altă filă și să citească în
     paralel; acolo nimic nu e obligatoriu și poate relua oricând. */
  let eraPornit = false, ultim = null;

  const bate = async () => {
    let d = null;
    try { ({ data: d } = await sb.rpc("citeste_ritm", { p_capitol: capitol })); }
    catch { return; }
    const acum = !!d?.pornit;

    if (acum !== eraPornit){ eraPornit = acum; laStare?.(acum); }
    if (!acum){ bara.hidden = true; ultim = null; return; }

    const nr = Math.max(1, d.slide_nr | 0);
    if (nr !== ultim){ ultim = nr; mergiLa(nr - 1); }
    deseneaza(nr);
  };

  function deseneaza(nr){
    bara.hidden = false;
    bara.className = "ritm ritm--on";
    bara.innerHTML = `
      <span class="ritm__pct"></span>
      <span class="ritm__t">Ora e condusă</span>
      <span class="ritm__d">slide-ul ${nr}, ca pe ecranul din față</span>
      ${manual ? `<a class="ritm__b" href="${manual}" target="_blank"
                     rel="noopener">Deschide manualul</a>` : ""}`;
  }

  bate();
  ceas = setInterval(() => { if (!document.hidden) bate(); }, PAS_STUDENT);
  document.addEventListener("visibilitychange", () => { if (!document.hidden) bate(); });

  return { publica(){}, opreste(){ clearInterval(ceas); } };
}

function construieste(){
  const d = document.createElement("div");
  d.className = "ritm";
  d.hidden = true;
  document.body.appendChild(d);
  /* cand banda apare, scena coboara cu inaltimea ei: altfel acopera numarul
     slide-ului, care e exact lucrul dupa care se uita omul */
  new MutationObserver(() => document.body.classList.toggle("are-ritm", !d.hidden))
    .observe(d, { attributes:true, attributeFilter:["hidden"] });
  return d;
}
