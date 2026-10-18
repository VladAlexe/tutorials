/* ===========================================================================
   ORA, ÎN PAGINA LECȚIEI

   O regulă ține tot restul: CONDUCI DIN LECȚIE, ÎNTOTDEAUNA.

   Lecția e ce proiectezi, deci acolo stai oricum. Tot ce-ți trebuie în timpul
   orei intră în banda de jos: codul, câți sunt, cine a răspuns, ceasul. Panoul
   cu nume se deschide peste treimea de jos, la tasta V, sau pe al doilea ecran.

   Înainte erau douăsprezece butoane pe trei suprafețe, iar aceeași oră avea
   două volane, unul aici și unul în panou. De acolo venea senzația de
   complicat, nu din numărul lor. Acum rămân patru, într-un singur loc, și
   niciodată toate patru deodată.

   Nu mai există mod „ritm propriu". Cât ora e deschisă, ei sunt pe slide-ul
   tău; când o închizi, lecția rămâne deschisă pentru acasă. Butonul de
   comutare a existat o vreme, nu-i aducea curat înapoi, și folosea la un
   singur moment din oră. Un buton care te minte o dată pe oră e mai rău decât
   niciunul.

   Taste:  → ←  slide   ·   V  cifrele   ·   C  codul mare   ·   F  prezentare

   Panoul nu e pe „P" pentru că js/slide.js folosește deja p și n pentru slide-ul
   precedent și următor, și apăsarea lui ar sări înapoi în lecție în loc să
   deschidă panoul. V vine de la „vezi cine a răspuns".

   Se folosește doar din js/slide.js:

     const r = await porneste({ capitol, total, esteProfesor, mergiLa, unde,
                                manual, laStare });
     r?.publica(nr);        // profesorul, la fiecare schimbare de slide

   Fără cont, fără rețea, sau fără tabelele din db/14, modulul iese tăcut și
   lecția merge exact ca înainte.
   =========================================================================== */

import { RADACINA } from "./curs.js?v=39";

const PAS_STUDENT   = 3000;   /* cât de des întreabă studentul unde ești */
const PAS_PROFESOR  = 8000;   /* cât de des numără profesorul sala */
const PAS_INTREBARE = 4000;   /* mai des, cât timp e o întrebare pe ecran */

export async function porneste({ capitol, total, esteProfesor, mergiLa, unde,
                                 manual, laStare }){
  let A, O, P;
  try {
    A = await import(`${RADACINA}/js/auth.js?v=39`);
    O = await import(`${RADACINA}/js/ora.js?v=39`);
    P = await import(`${RADACINA}/js/panou-live.js?v=39`);
  } catch { return null; }

  let p = null;
  try { p = await A.profil(); } catch { return null; }
  if (!p?.autentificat) return null;

  const bara = construieste();
  let ceas = null, ceasul = null;

  /* de când e slide-ul pe ecran; se pune la zero la fiecare schimbare */
  let dinCand = Date.now();
  const secunde = () => (Date.now() - dinCand) / 1000;

  const harta = await O.harta(capitol);
  const sarciniDe = nr => O.sarciniDe(harta, nr);
  const slideDe   = nr => (harta?.slide || []).find(x => x.nr === nr) || null;

  /* ============================================================ PROFESOR === */
  if (esteProfesor){
    P.stil();
    let S = await O.deschisa(capitol);
    let randuri = [], sertarDeschis = false;

    const slideAcum = () => Math.max(1, (unde?.() | 0) || 1);

    /** Câți sunt, și cine ce a trimis pe slide-ul de pe ecran. */
    async function numara(){
      const proaspat = await O.deschisa(capitol);
      if (!proaspat){ S = null; randuri = []; deseneaza(); return; }
      S = { ...S, ...proaspat };

      const sarcini = sarciniDe(slideAcum());
      randuri = sarcini.length
        ? (await O.panou(S.id, sarcini.map(x => x.id)) || [])
        : (await O.panou(S.id, []) || []);
      deseneaza();
    }

    /* --- banda ----------------------------------------------------------- */

    function deseneaza(){
      bara.hidden = false;
      bara.className = "ritm ritm--prof" + (S ? " ritm--on" : "");

      if (!S){
        bara.innerHTML = `
          <span class="ritm__pct"></span>
          <span class="ritm__t">Nu predai acum</span>
          <span class="ritm__d">umbli prin lecție de unul singur</span>
          <span class="ritm__sp"></span>
          <button class="ritm__b ritm__b--tare" type="button" data-rol="start">Pornește ora</button>`;
        lega();
        return;
      }

      const sarcini = sarciniDe(slideAcum());
      const cate = P.numara(randuri);
      const trimis = randuri.length - cate.nefacut;

      bara.innerHTML = `
        <span class="ritm__pct"></span>
        <button class="ritm__cod" type="button" data-rol="cod"
                title="Arată codul mare, de proiectat (C)">${S.cod || "…"}</button>
        ${sertarDeschis ? `
          <span class="ritm__stari">${P.ceasHTML(secunde())}</span>
          <span class="ritm__d"><b>${trimis}</b> din ${randuri.length} au trimis</span>
          <span class="ritm__sp"></span>
          <button class="ritm__b" type="button" data-rol="panou">Strânge cifrele</button>`
        : `
          ${sarcini.length ? `
            <span class="ritm__stari">
              ${P.ceasHTML(secunde())}
              ${["trecut","trimis_gresit","trimis_gol","nefacut"].map(k =>
                `<span class="ritm__g ritm__g--${k}">${
                  { trecut:"✓", trimis_gresit:"✕", trimis_gol:"◉", nefacut:"○" }[k]
                }<b>${cate[k]}</b></span>`).join("")}
            </span>`
          : `<span class="ritm__d"><b>${S.in_clasa || 0}</b> în clasă,
               pe slide-ul tău</span>`}
          <span class="ritm__sp"></span>
          <button class="ritm__b" type="button" data-rol="link"
                  title="Pentru cine ajunge mai târziu">copiază linkul</button>
          <button class="ritm__b" type="button" data-rol="panou"
                  title="Câți au răspuns, fără nume (V)">Cifrele</button>
          <a class="ritm__b" href="${RADACINA}/predau/ora/" target="_blank"
             rel="noopener" title="Panoul cu nume, pe al doilea ecran">al doilea ecran ↗</a>
          <button class="ritm__b ritm__b--stop" type="button" data-rol="stop">Închide ora</button>`}`;
      lega();
      if (sertarDeschis) deseneazaSertar();
    }

    function lega(){
      bara.querySelector('[data-rol="start"]')?.addEventListener("click", porneste);
      bara.querySelector('[data-rol="stop"]') ?.addEventListener("click", opresteOra);
      bara.querySelector('[data-rol="link"]') ?.addEventListener("click", copiaza);
      bara.querySelector('[data-rol="cod"]')  ?.addEventListener("click", ecran);
      bara.querySelector('[data-rol="panou"]')?.addEventListener("click", comutaPanoul);
    }

    async function porneste(e){
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
      if (S) await O.pune(S.id, { slide: slideAcum() });
      dinCand = Date.now();
      laStare?.(true, S?.mod || "live");
      deseneaza();
      ecran();
      numara();
    }

    async function opresteOra(){
      if (!S) return;
      await O.inchide(S.id);
      S = null; sertarDeschis = false; inchideSertar();
      laStare?.(false, null);
      deseneaza();
    }

    /* Linkul de intrare, copiat în clipboard. Cineva ajunge la minutul 20 și
       codul mare nu mai e pe ecran: i-l trimiți pe chat și intră. */
    async function copiaza(e){
      const b = e.currentTarget;
      const adresa = `${location.origin}${RADACINA}/intra/?c=${S.cod}`;
      try {
        await navigator.clipboard.writeText(adresa);
        b.textContent = "copiat ✓";
      } catch {
        b.textContent = adresa;        /* fără clipboard, îl arăt ca să-l iei cu mâna */
        getSelection()?.selectAllChildren(b);
      }
      setTimeout(() => { if (b.isConnected) b.textContent = "copiază linkul"; }, 2400);
    }

    /* --- sertarul, peste treimea de jos ---------------------------------- */

    let gazdaSertar = null;

    function comutaPanoul(){
      sertarDeschis = !sertarDeschis;
      if (!sertarDeschis) inchideSertar();
      deseneaza();
    }

    function inchideSertar(){
      gazdaSertar?.remove();
      gazdaSertar = null;
      document.body.classList.remove("are-sertar");
    }

    function deseneazaSertar(){
      if (!gazdaSertar){
        gazdaSertar = document.createElement("div");
        gazdaSertar.className = "sertar";
        document.body.appendChild(gazdaSertar);
        document.body.classList.add("are-sertar");
      }
      const nr = slideAcum();
      gazdaSertar.innerHTML = P.randeaza({
        slide: slideDe(nr), sarcini: sarciniDe(nr), randuri,
        secunde: secunde(), totalSarcini: harta?.sarcini || null,
        nume: false   /* se deschide peste proiector: cifre, nu nume */
      });
    }

    /* --- codul mare ------------------------------------------------------ */

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
      d.addEventListener("click", e => {
        if (e.target === d || e.target.closest(".cod-mare__x")) d.remove();
      });

      import("https://cdn.jsdelivr.net/npm/qrcode@1.5.4/+esm")
        .then(Q => Q.default.toDataURL(adresa, { margin:1, width:420, errorCorrectionLevel:"M" }))
        .then(u => { const g = d.querySelector(".cod-mare__qr");
                     if (g) g.innerHTML = `<img src="${u}" alt="Cod QR pentru intrarea la oră">`; })
        .catch(() => { /* fără bibliotecă, codul scris mare e de ajuns */ });
    }

    /* --- taste ------------------------------------------------------------ */

    document.addEventListener("keydown", e => {
      if (e.metaKey || e.ctrlKey || e.altKey) return;
      const t = e.target;
      if (t && (t.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName))) return;

      if (e.key === "Escape"){
        if (document.querySelector(".cod-mare")) document.querySelector(".cod-mare").remove();
        else if (sertarDeschis) comutaPanoul();
        return;
      }
      if (!S) return;
      const k = e.key.toLowerCase();
      if (k === "v"){ e.preventDefault(); comutaPanoul(); }
      if (k === "c"){ e.preventDefault(); ecran(); }
    });

    /* --- ceasuri ---------------------------------------------------------- */

    deseneaza();
    if (S) laStare?.(true, "live");

    /* ticăitul: o dată pe secundă, doar textul ceasului, fără să redesenez tot */
    ceasul = setInterval(() => {
      if (!S || document.hidden) return;
      const c = bara.querySelector(".ceas");
      if (!c) return;
      c.textContent = P.ceasText(secunde());
      c.classList.toggle("ceas--tarziu", secunde() >= P.PRAG);
      const cs = gazdaSertar?.querySelector(".pv__n");
      if (cs) cs.textContent = `slide-ul de pe ecran · ${P.ceasText(secunde())}`;
    }, 1000);

    let pas = PAS_PROFESOR;
    const bate = () => { if (!document.hidden && S) numara(); };
    ceas = setInterval(() => {
      const vrut = sarciniDe(slideAcum()).length ? PAS_INTREBARE : PAS_PROFESOR;
      if (vrut !== pas){ pas = vrut; clearInterval(ceas); ceas = setInterval(bate, pas); }
      bate();
    }, pas);
    if (S) numara();

    /* js/slide.js cheamă publica() la fiecare mișcare prin lecție, inclusiv
       când ajunge pe același slide. Ceasul se pune la zero doar când slide-ul
       chiar s-a schimbat, altfel n-ar trece niciodată de câteva secunde. */
    let publicat = null;

    return {
      publica(nr){
        if (nr === publicat) return;
        publicat = nr;
        dinCand = Date.now();               /* slide nou, ceas de la zero */
        if (!S) return;
        O.pune(S.id, { slide: nr });
        randuri = [];
        deseneaza();
        numara();
      },
      opreste(){ clearInterval(ceas); clearInterval(ceasul); }
    };
  }

  /* ============================================================= STUDENT === */
  /* Cât ora e deschisă, pagina lui e pagina mea. Atât. Nu mai există două
     moduri de urmat, deci nici stare de ținut minte, nici buton. Când ora se
     închide, banda dispare și lecția rămâne a lui, pentru acasă. */
  let eraViu = false, ultim = null;

  const bate = async () => {
    const d = await O.acum(capitol);
    if (!d) return;
    const viu = !!d.viu;

    /* tot ce se salvează de acum poartă id-ul ședinței, sau niciunul */
    import(`${RADACINA}/js/colectare.js?v=39`)
      .then(m => m.setSedinta(viu ? d.sedinta : null)).catch(() => {});

    if (viu !== eraViu){ eraViu = viu; laStare?.(viu, viu ? "live" : null); }
    if (!viu){ bara.hidden = true; ultim = null; return; }

    const nr = Math.max(1, d.slide_nr | 0);
    if (nr !== ultim){ ultim = nr; dinCand = Date.now(); mergiLa(nr - 1); }
    deseneazaStudent(d);
  };

  function deseneazaStudent(d){
    const areIntrebare = sarciniDe(Math.max(1, d.slide_nr | 0)).length > 0;
    bara.hidden = false;
    bara.className = "ritm ritm--on";
    bara.innerHTML = `
      <span class="ritm__pct"></span>
      <span class="ritm__t">Ești la oră</span>
      ${areIntrebare ? `<span class="ritm__stari">${P.ceasHTML(secunde())}</span>` : ""}
      <span class="ritm__d">slide-ul ${d.slide_nr}, ca pe ecranul din față</span>
      <span class="ritm__sp"></span>
      ${manual ? `<a class="ritm__b" href="${manual}" target="_blank"
                     rel="noopener">Deschide manualul</a>` : ""}`;
  }

  bate();
  ceas = setInterval(() => { if (!document.hidden) bate(); }, PAS_STUDENT);
  ceasul = setInterval(() => {
    if (document.hidden) return;
    const c = bara.querySelector(".ceas");
    if (!c) return;
    c.textContent = P.ceasText(secunde());
    c.classList.toggle("ceas--tarziu", secunde() >= P.PRAG);
  }, 1000);
  document.addEventListener("visibilitychange", () => { if (!document.hidden) bate(); });

  return { publica(){}, opreste(){ clearInterval(ceas); clearInterval(ceasul); } };
}

function construieste(){
  const d = document.createElement("div");
  d.className = "ritm";
  d.hidden = true;
  document.body.appendChild(d);
  /* când banda apare, scena se ridică cu înălțimea ei: altfel acoperă
     numărul slide-ului, care e exact lucrul după care se uită omul */
  new MutationObserver(() => document.body.classList.toggle("are-ritm", !d.hidden))
    .observe(d, { attributes:true, attributeFilter:["hidden"] });
  return d;
}
