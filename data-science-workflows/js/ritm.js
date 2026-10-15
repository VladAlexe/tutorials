/* ===========================================================================
   ORA, ÎN PAGINA LECȚIEI

   O singură bandă, jos, și un singur adevăr: ȘEDINȚA.

   Până acum mergeau două sisteme în paralel, și de acolo venea tot haosul:
   bara asta își făcea un cod propriu în `jetoane_prezenta` și publica slide-ul
   în tabelul `ritm`, în timp ce ecranul de intrare și panoul citeau din
   `sedinte`. Ieșeau două coduri diferite pentru aceeași oră, studenți care
   intrau pe un cod care nu ducea nicăieri, și nimeni care se mișca după
   nimeni. Acum totul trece prin `sedinte`, și nicăieri altundeva.

   Profesorul:  un buton, „Pornește ora". Apoi codul, câți sunt, și modul.
   Studentul:   citește ședința deschisă și, în mod live, stă pe slide-ul tău.

   Se folosește doar din js/slide.js:

     const r = await porneste({ capitol, total, esteProfesor, mergiLa, unde,
                                manual, laStare });
     r?.publica(nr);        // profesorul, la fiecare schimbare de slide

   Fără cont, fără rețea, sau fără tabelele din db/14, modulul iese tăcut și
   lecția merge exact ca înainte.
   =========================================================================== */

import { RADACINA } from "./curs.js?v=34";

const PAS_STUDENT  = 3000;    /* cât de des întreabă studentul unde e profesorul */
const PAS_PROFESOR = 8000;    /* cât de des numără profesorul cine e în sală */

export async function porneste({ capitol, total, esteProfesor, mergiLa, unde,
                                 manual, laStare }){
  let A, O;
  try {
    A = await import(`${RADACINA}/js/auth.js?v=34`);
    O = await import(`${RADACINA}/js/ora.js?v=34`);
  } catch { return null; }

  let p = null;
  try { p = await A.profil(); } catch { return null; }
  if (!p?.autentificat) return null;

  const bara = construieste();
  let ceas = null;

  /* ============================================================ PROFESOR === */
  if (esteProfesor){
    let S = await O.deschisa(capitol);     /* ședința deschisă, dacă există */
    let inClasa = S?.in_clasa || 0;

    const numara = async () => {
      const proaspat = await O.deschisa(capitol);
      if (proaspat){ S = { ...S, ...proaspat }; inClasa = proaspat.in_clasa || 0; }
      else { S = null; inClasa = 0; }
      deseneaza();
    };

    function deseneaza(){
      bara.hidden = false;
      bara.className = "ritm ritm--prof" + (S ? " ritm--on" : "");
      bara.innerHTML = S ? `
        <span class="ritm__pct"></span>
        <button class="ritm__cod" type="button" title="Arată codul mare, de proiectat">
          <small>cod</small>${S.cod || "…"}</button>
        <span class="ritm__d"><b>${inClasa}</b> în clasă ·
          ${S.mod === "live" ? "sunt pe slide-ul tău" : "merg în ritmul lor"}</span>
        <button class="ritm__b" type="button" data-rol="mod">${
          S.mod === "live" ? "Lasă-i singuri" : "Ține-i cu mine"}</button>
        <a class="ritm__b" href="${RADACINA}/predau/ora/">Panoul live</a>
        <button class="ritm__b ritm__b--stop" type="button" data-rol="stop">Oprește ora</button>`
      : `
        <span class="ritm__pct"></span>
        <span class="ritm__t">Nu predai acum</span>
        <span class="ritm__d">umbli prin lecție de unul singur</span>
        <button class="ritm__b" type="button" data-rol="start">Pornește ora</button>`;

      bara.querySelector('[data-rol="start"]')?.addEventListener("click", async e => {
        const b = e.currentTarget; b.disabled = true; b.textContent = "Se pornește…";
        /* Grupa se alege singură, în js/ora.js. Aici ești în fața clasei: un
           buton, și ora e pornită. */
        const r = await O.deschide(capitol, null, "live", total);
        if (!r?.ok){
          b.disabled = false; b.textContent = "Pornește ora";
          alert(r?.mesaj || (O.lipsesteBaza()
            ? "Baza nu e pregătită: rulează db/14 și db/15 în Supabase."
            : "N-am putut porni ora."));
          return;
        }
        S = await O.deschisa(capitol);
        if (S) await O.pune(S.id, { slide: unde() });
        laStare?.(true, S?.mod || "live");
        deseneaza();
        ecran();
        numara();
      });

      bara.querySelector('[data-rol="stop"]')?.addEventListener("click", async () => {
        if (!S) return;
        await O.inchide(S.id);
        S = null; laStare?.(false, null); deseneaza();
      });

      bara.querySelector('[data-rol="mod"]')?.addEventListener("click", async () => {
        if (!S) return;
        const nou = S.mod === "live" ? "propriu" : "live";
        const r = await O.pune(S.id, { mod: nou });
        if (r?.ok){ S.mod = r.mod; laStare?.(true, S.mod); deseneaza(); }
      });

      bara.querySelector(".ritm__cod")?.addEventListener("click", ecran);
    }

    /** Codul, mare, de proiectat la începutul orei. Se închide cu Esc sau clic. */
    function ecran(){
      if (!S?.cod || document.querySelector(".cod-mare")) return;
      const scurta = `${location.host}${RADACINA}/intra`;
      const adresa = `${location.origin}${RADACINA}/intra/?c=${S.cod}`;
      const d = document.createElement("div");
      d.className = "cod-mare";
      d.innerHTML = `
        <button class="cod-mare__x" type="button" aria-label="Închide">×</button>
        <div class="cod-mare__in">
          <p class="cod-mare__et">${S.titlu || "Intră la oră"}</p>
          <p class="cod-mare__c">${S.cod}</p>
          <p class="cod-mare__u">${scurta}</p>
          <div class="cod-mare__qr"></div>
          <p class="cod-mare__d">Scanați codul cu telefonul, sau deschideți
            adresa și tastați cele șase semne. Codul știe lecția și grupa;
            voi spuneți doar cine sunteți.</p>
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
        .then(Q => Q.default.toDataURL(adresa, { margin:1, width:420, errorCorrectionLevel:"M" }))
        .then(u => { const g = d.querySelector(".cod-mare__qr");
                     if (g) g.innerHTML = `<img src="${u}" alt="Cod QR pentru intrarea la oră">`; })
        .catch(() => { /* fără bibliotecă, codul scris mare e de ajuns */ });
    }

    deseneaza();
    if (S) laStare?.(true, S.mod);
    ceas = setInterval(() => { if (!document.hidden && S) numara(); }, PAS_PROFESOR);

    return {
      publica(nr){ if (S) O.pune(S.id, { slide: nr }); },
      opreste(){ clearInterval(ceas); }
    };
  }

  /* ============================================================= STUDENT === */
  /* Cât ține ora în mod live, pagina lui e pagina mea: nu are buton de
     desprindere, pentru că n-ar mai fi live. În ritm propriu merge singur,
     dar ce trimite se leagă tot de ședință. */
  let eraViu = false, ultim = null, modAcum = null;

  const bate = async () => {
    const d = await O.acum(capitol);
    if (!d) return;
    const viu = !!d.viu;

    /* tot ce se salvează de acum poartă id-ul ședinței, sau niciunul */
    import(`${RADACINA}/js/colectare.js?v=34`)
      .then(m => m.setSedinta(viu ? d.sedinta : null)).catch(() => {});

    if (viu !== eraViu || d.mod !== modAcum){
      eraViu = viu; modAcum = d.mod || null;
      laStare?.(viu, d.mod || null);
    }
    if (!viu){ bara.hidden = true; ultim = null; return; }

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
