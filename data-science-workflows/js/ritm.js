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

import { RADACINA } from "./curs.js?v=45";

const PAS_STUDENT   = 3000;   /* cât de des întreabă studentul unde ești */
const PAS_PROFESOR  = 8000;   /* cât de des numără profesorul sala */
const PAS_INTREBARE = 4000;   /* mai des, cât timp e o întrebare pe ecran */

export async function porneste({ capitol, total, esteProfesor, mergiLa, unde,
                                 manual, laStare }){
  let A, O, P;
  try {
    A = await import(`${RADACINA}/js/auth.js?v=45`);
    O = await import(`${RADACINA}/js/ora.js?v=45`);
    P = await import(`${RADACINA}/js/panou-live.js?v=45`);
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
    /* o oră uitată deschisă se închide singură după 3 ore */
    if (S && O.prea_veche(S)){ await O.inchide(S.id); S = null; }
    /* ora se pornește dintr-un singur loc: butonul „Predă” de pe pagina
       lecției, care aduce aici ?preda=1. Adresa se curăță imediat, ca un
       refresh să nu pornească încă o oră. */
    const cerePredare = new URLSearchParams(location.search).has("preda");
    if (cerePredare){
      const u = new URL(location.href); u.searchParams.delete("preda");
      history.replaceState(null, "", u.pathname + u.search + u.hash);
    }
    let randuri = [], sertarDeschis = false;

    const slideAcum = () => Math.max(1, (unde?.() | 0) || 1);

    /** Câți sunt, și cine ce a trimis pe slide-ul de pe ecran. */
    async function numara(){
      const proaspat = await O.deschisa(capitol);
      if (!proaspat){ S = null; randuri = []; deseneaza(); laStare?.(false, null); return; }
      if (O.prea_veche(proaspat)){ await opresteOra(); return; }
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

      /* fără oră pornită, bara nu există: profesorul răsfoiește lecția ca
         oricine. Ora se pornește de pe pagina lecției, cu „Predă”. */
      if (!S){ bara.hidden = true; bara.innerHTML = ""; return; }

      const sarcini = sarciniDe(slideAcum());
      const cate = P.numara(randuri);
      const trimis = randuri.length - cate.nefacut;

      /* Patru lucruri, mereu în aceeași ordine: codul (un clic îl face mare,
         cu QR și link), câți sunt, ce le arăți, încheierea. „Arată clasei”
         apare doar pe slide-urile cu întrebare; „Rezultate” e un link
         obișnuit, spre pagina cu nume, de deschis în altă filă. */
      if (!sarcini.length && sertarDeschis){ sertarDeschis = false; inchideSertar(); }
      /* „în clasă” = cine e acum pe pagina lecției (o bătaie în ultimele 90 de
         secunde), nu cine e înscris în grupă. Profesorul nu se numără. */
      const acum = Date.now();
      const vii = randuri.filter(x => x.vazut_la && acum - new Date(x.vazut_la) < 90000);
      const inClasa = vii.length;
      bara.innerHTML = `
        <span class="ritm__pct"></span>
        <button class="ritm__cod" type="button" data-rol="cod"
                title="Codul mare, cu QR și linkul de intrare">${S.cod || "…"}</button>
        <span class="ritm__d"><b>${inClasa}</b> în clasă</span>
        ${sarcini.length ? `
          <span class="ritm__stari" title="pe slide-ul de pe ecran: corect, greșit, gol, n-a trimis">
            ${P.ceasHTML(secunde())}
            ${["trecut","trimis_gresit","trimis_gol","nefacut"].map(k =>
              `<span class="ritm__g ritm__g--${k}">${
                { trecut:"✓", trimis_gresit:"✕", trimis_gol:"◉", nefacut:"○" }[k]
              }<b>${k === "nefacut" ? Math.max(0, inClasa - (cate.trecut + cate.trimis_gresit + cate.trimis_gol)) : cate[k]}</b></span>`).join("")}
          </span>` : `<span class="ritm__stari">${P.ceasHTML(secunde())}</span>`}
        <span class="ritm__sp"></span>
        ${sarcini.length ? `<button class="ritm__b${sertarDeschis ? " ritm__b--on" : ""}" type="button"
            data-rol="panou" title="Răspunsurile clasei, fără nume, pentru proiector">${
            sertarDeschis ? "Ascunde răspunsurile" : "Arată clasei"}</button>` : ""}
        <a class="ritm__b" href="${RADACINA}/predau/ora/" target="_blank" rel="noopener"
           title="Cine ce a răspuns, cu nume. Doar pentru tine.">Rezultate ↗</a>
        <button class="ritm__b ritm__b--stop" type="button" data-rol="stop">Încheie ora</button>`;
      lega();
      if (sertarDeschis) deseneazaSertar();
    }

    function lega(){
      bara.querySelector('[data-rol="stop"]') ?.addEventListener("click", opresteOra);
      bara.querySelector('[data-rol="link"]') ?.addEventListener("click", copiaza);
      bara.querySelector('[data-rol="cod"]')  ?.addEventListener("click", ecran);
      bara.querySelector('[data-rol="panou"]')?.addEventListener("click", comutaPanoul);
    }

    async function porneste(){
      /* Grupa se alege singură, în js/ora.js. Aici ești în fața clasei: un
         buton, și ora e pornită. */
      /* o singură oră pornită odată: dacă a rămas deschisă alta (altă
         lecție), se încheie înainte să pornească asta */
      const alta = await O.deschisa();
      if (alta && alta.capitol !== capitol) await O.inchide(alta.id);
      const r = await O.deschide(capitol, null, "live", total);
      if (!r?.ok){
        alert(r?.mesaj || (O.lipsesteBaza()
          ? "Baza nu e pregătită: rulează db/14 și db/15 în Supabase."
          : "N-am putut porni ora."));
        return;
      }
      S = await O.deschisa(capitol);
      if (S) await O.pune(S.id, { slide: slideAcum() });
      dinCand = Date.now();
      laStare?.(true, S?.mod || "live");
      document.dispatchEvent(new Event("dsw:ora"));
      deseneaza();
      ecran();
      numara();
    }

    async function opresteOra(){
      if (!S) return;
      const id = S.id;
      await O.inchide(id);
      S = null; sertarDeschis = false; inchideSertar();
      laStare?.(false, null);
      document.dispatchEvent(new Event("dsw:ora"));
      deseneaza();
      /* ce urmează după oră: raportul ei, la un clic */
      bara.hidden = false;
      bara.className = "ritm ritm--prof";
      bara.innerHTML = `<span class="ritm__pct"></span>
        <span class="ritm__t">Ora s-a încheiat</span>
        <span class="ritm__sp"></span>
        <a class="ritm__b ritm__b--tare" href="${RADACINA}/predau/?raport=${id}">Raportul orei</a>
        <button class="ritm__b" type="button" data-rol="gata">Închide</button>`;
      bara.querySelector('[data-rol="gata"]').onclick = () => { bara.hidden = true; };
      setTimeout(() => { if (!S) bara.hidden = true; }, 20000);
    }

    /* Linkul de intrare, copiat în clipboard. Cineva ajunge la minutul 20 și
       codul mare nu mai e pe ecran: i-l trimiți pe chat și intră. */
    async function copiaza(e){
      const b = e.target.closest('[data-rol="link"]') || e.currentTarget;
      const adresa = `${location.origin}${RADACINA}/intra/?c=${S.cod}`;
      try {
        await navigator.clipboard.writeText(adresa);
        b.textContent = "copiat ✓";
      } catch {
        b.textContent = adresa;        /* fără clipboard, îl arăt ca să-l iei cu mâna */
        getSelection()?.selectAllChildren(b);
      }
      setTimeout(() => { if (b.isConnected) b.textContent = "Copiază linkul"; }, 2400);
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
        /* proiectat: doar cine e acum în clasă, ca „din câți” să fie sala */
        slide: slideDe(nr), sarcini: sarciniDe(nr),
        randuri: randuri.filter(x => x.stare !== "nefacut" ||
                   (x.vazut_la && Date.now() - new Date(x.vazut_la) < 90000)),
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
            adresa și tastați cele șase semne.</p>
          <button class="ritm__b cod-mare__copiaza" type="button" data-rol="link">Copiază linkul</button>
        </div>`;
      document.body.appendChild(d);
      d.addEventListener("click", e => {
        if (e.target.closest('[data-rol="link"]')){ copiaza(e); return; }
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
    else if (cerePredare) porneste();

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
    import(`${RADACINA}/js/colectare.js?v=45`)
      .then(m => m.setSedinta(viu ? d.sedinta : null)).catch(() => {});

    const tocmaiS_aIncheiat = eraViu && !viu;
    if (viu !== eraViu){ eraViu = viu; laStare?.(viu, viu ? "live" : null); }
    if (!viu){
      ultim = null;
      if (tocmaiS_aIncheiat){
        /* nu dispare pe tăcute: îi spun ce s-a întâmplat și ce rămâne */
        bara.hidden = false; bara.className = "ritm";
        bara.innerHTML = `<span class="ritm__pct"></span>
          <span class="ritm__t">Ora s-a încheiat</span>
          <span class="ritm__d">lecția rămâne a ta: o poți parcurge oricând, în ritmul tău</span>`;
        setTimeout(() => { if (!eraViu) bara.hidden = true; }, 12000);
      } else if (!bara.innerHTML.includes("s-a încheiat")) bara.hidden = true;
      return;
    }

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
