/* ===========================================================================
   ORA CONDUSĂ

   Totul se întâmplă în pagina lecției. Profesorul apasă „Predă" în lista lui
   de lecții, ajunge aici, și de aici conduce: codul de intrare stă în bară,
   iar slide-ul lui e slide-ul tuturor. Nu are de umblat între ferestre.

   Studentul nu are de ce să se desprindă. Dacă vrea să citească în ritmul
   lui, deschide manualul în altă filă, unde nimic nu e obligatoriu.

   Se folosește doar din js/slide.js:

     const r = await porneste({ capitol, total, esteProfesor, mergiLa, unde,
                                manual, laStare });
     r?.publica(nr);        // profesorul, la fiecare schimbare de slide

   Fără cont, fără rețea sau fără tabelul `ritm`, modulul iese tăcut și lecția
   merge exact ca înainte.
   =========================================================================== */

import { RADACINA } from "./curs.js?v=30";

const PAS_STUDENT  = 3000;    /* cât de des întreabă studentul unde e profesorul */
const PAS_PROFESOR = 10000;   /* cât de des numără profesorul cine e în sală */

export async function porneste({ capitol, total, esteProfesor, mergiLa, unde,
                                 manual, laStare }){
  let A;
  try { A = await import(`${RADACINA}/js/auth.js?v=30`); }
  catch { return null; }

  let p = null;
  try { p = await A.profil(); } catch { return null; }
  if (!p?.autentificat) return null;

  const sb = A.sb;
  const bara = construieste();
  let ceas = null;

  /* ============================================================ PROFESOR === */
  if (esteProfesor){
    let pornit = false, inClasa = 0, jeton = null;

    const scrie = async (nr, pornitNou) => {
      try {
        const { data } = await sb.rpc("pune_ritm", {
          p_capitol: capitol, p_slide_nr: nr ?? null,
          p_total_nr: total, p_pornit: pornitNou ?? null });
        if (data && data.ok !== false) pornit = !!data.pornit;
        return data;
      } catch { return null; }
    };

    const iaJeton = async () => {
      try {
        const { data } = await sb.rpc("creeaza_jeton", { p_curs: capitol, p_minute: 110 });
        if (data?.ok) jeton = data.jeton;
      } catch { /* fără jeton, rămâne doar ritmul */ }
    };

    const numara = async () => {
      try {
        const { data } = await sb.rpc("live_acum", { p_minute: 3 });
        inClasa = (data || []).filter(x => x.capitol === capitol).length;
      } catch { inClasa = 0; }
      deseneaza();
    };

    /* ora poate fi deja pornită: de pe alt calculator, sau pentru că tocmai
       am apăsat „Predă" în lista de lecții și am ajuns aici */
    try {
      const { data } = await sb.rpc("citeste_ritm", { p_capitol: capitol });
      pornit = !!data?.pornit;
    } catch { /* fără tabel, butonul rămâne, dar nu face nimic */ }
    if (pornit) await iaJeton();

    function deseneaza(){
      bara.hidden = false;
      bara.className = "ritm ritm--prof" + (pornit ? " ritm--on" : "");
      bara.innerHTML = pornit ? `
        <span class="ritm__pct"></span>
        <button class="ritm__cod" type="button" title="Arată codul mare, de proiectat">
          <small>cod</small>${jeton || "…"}</button>
        <span class="ritm__d"><b>${inClasa}</b> în clasă · sunt pe slide-ul tău</span>
        <a class="ritm__b" href="${RADACINA}/predau/ora/">Panoul live</a>
        <button class="ritm__b ritm__b--stop" type="button" data-rol="stop">Oprește ora</button>`
      : `
        <span class="ritm__pct"></span>
        <span class="ritm__t">Nu predai acum</span>
        <span class="ritm__d">umbli prin lecție de unul singur</span>
        <button class="ritm__b" type="button" data-rol="start">Pornește ora</button>`;

      bara.querySelector('[data-rol="start"]')?.addEventListener("click", async () => {
        await scrie(unde(), true);
        await iaJeton();
        laStare?.(true);
        deseneaza();
        if (jeton) ecran();
        numara();
      });
      bara.querySelector('[data-rol="stop"]')?.addEventListener("click", async () => {
        await scrie(null, false);
        laStare?.(false);
        deseneaza();
      });
      bara.querySelector(".ritm__cod")?.addEventListener("click", ecran);
    }

    /** Codul, mare, de proiectat la începutul orei. Se închide cu Esc sau clic. */
    function ecran(){
      if (document.querySelector(".cod-mare")) return;
      /* două adrese: una scurtă, de citit de pe ecran și de tastat, și una
         lungă, cu jeton și cu lecția, pe care o duce codul QR */
      const scurta = `${location.host}${RADACINA}/intra`;
      const adresa = `${location.origin}${RADACINA}/intra/?j=${jeton}` +
                     `&spre=${encodeURIComponent(location.pathname)}`;
      const d = document.createElement("div");
      d.className = "cod-mare";
      d.innerHTML = `
        <button class="cod-mare__x" type="button" aria-label="Închide">×</button>
        <div class="cod-mare__in">
          <p class="cod-mare__et">Intră la oră</p>
          <p class="cod-mare__c">${jeton || "—"}</p>
          <p class="cod-mare__u">${scurta}</p>
          <div class="cod-mare__qr"></div>
          <p class="cod-mare__d">Scanați codul cu telefonul, sau deschideți
            adresa și tastați cele șase semne. Cine are cont intră cu GitHub;
            cine nu, doar cu numele lui. Prezența se marchează singură.</p>
        </div>`;
      document.body.appendChild(d);

      const inchide = () => d.remove();
      d.addEventListener("click", e => {
        if (e.target === d || e.target.closest(".cod-mare__x")) inchide();
      });
      document.addEventListener("keydown", function esc(e){
        if (e.key === "Escape"){ inchide(); document.removeEventListener("keydown", esc); }
      });

      import("https://cdn.jsdelivr.net/npm/qrcode@1.5.4/+esm")
        .then(QR => QR.default.toDataURL(adresa, { margin:1, width:420, errorCorrectionLevel:"M" }))
        .then(u => { const g = d.querySelector(".cod-mare__qr");
                     if (g) g.innerHTML = `<img src="${u}" alt="Cod QR pentru intrarea la oră">`; })
        .catch(() => { /* fără bibliotecă, codul scris mare e de ajuns */ });
    }

    deseneaza(); numara(); laStare?.(pornit);
    ceas = setInterval(() => { if (!document.hidden && pornit) numara(); }, PAS_PROFESOR);

    return {
      publica(nr){ if (pornit) scrie(nr); },
      opreste(){ clearInterval(ceas); }
    };
  }

  /* ============================================================= STUDENT === */
  /* Cât ține ora în mod live, pagina lui e pagina mea: nu are buton de
     desprindere, pentru că n-ar mai fi live. În ritm propriu merge singur,
     dar ce trimite se leagă tot de ședință, deci se vede în panou și se
     notează ca lucru făcut la clasă. */
  let eraViu = false, ultim = null, modAcum = null;

  const bate = async () => {
    let d = null;
    try { ({ data: d } = await sb.rpc("ora_acum", { p_capitol: capitol })); }
    catch { return; }
    const viu = !!d?.viu;

    /* tot ce se salvează de acum poartă id-ul ședinței, sau niciunul */
    import(`${RADACINA}/js/colectare.js?v=30`)
      .then(m => m.setSedinta(viu ? d.sedinta : null)).catch(() => {});

    if (viu !== eraViu || d?.mod !== modAcum){
      eraViu = viu; modAcum = d?.mod || null;
      laStare?.(viu, d?.mod || null);
    }
    if (!viu){ bara.hidden = true; ultim = null; return; }

    /* numai în live îl mut după mine; în ritm propriu umblă singur */
    if (d.mod === "live"){
      const nr = Math.max(1, d.slide_nr | 0);
      if (nr !== ultim){ ultim = nr; mergiLa(nr - 1); }
    }
    deseneazaStudent(d);
  };

  function deseneazaStudent(d){
    const live = d.mod === "live";
    bara.hidden = false;
    bara.className = "ritm ritm--on";
    bara.innerHTML = `
      <span class="ritm__pct"></span>
      <span class="ritm__t">${live ? "Ora e condusă" : "Ești la oră"}</span>
      <span class="ritm__d">${live
        ? `slide-ul ${d.slide_nr}, ca pe ecranul din față`
        : "mergi în ritmul tău; ce faci se vede la profesor"}</span>
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
  /* când banda apare, scena coboară cu înălțimea ei: altfel acoperă numărul
     slide-ului, care e exact lucrul după care se uită omul */
  new MutationObserver(() => document.body.classList.toggle("are-ritm", !d.hidden))
    .observe(d, { attributes:true, attributeFilter:["hidden"] });
  return d;
}
