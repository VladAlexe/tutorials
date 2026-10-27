/* ===========================================================================
   RULATORUL DE SLIDE-URI

   Ia secțiunile <section class="sld"> din pagină și le transformă într-o
   lecție navigabilă: cuprins în stânga, un slide pe ecran, bară de stare jos.

   Trei lucruri pentru care a fost făcut:

   1. Toți în același loc, în același timp. Fiecare slide are un număr și o
      adresă proprie (…/lectie/#7), deci „mergeți la slide-ul 7" chiar
      funcționează: tastezi 7, sau apeși Ctrl+K și cauți.

   2. Nu treci peste verificări. Dacă un slide are o verificare la care nu ai
      răspuns, butonul „Înainte" e închis. Nu se verifică dacă ai răspuns
      corect, doar dacă ai răspuns: scopul e să te oprești și să te gândești,
      nu să ghicești.

   3. Se ține minte. Progresul se scrie local imediat și în baza de date dacă
      ai cont, ca să îl vezi în pagina de progres și ca eu să văd unde s-a
      oprit grupa.

   Pornire, din pagina lecției:

     import { porneste } from "../js/slide.js?v=83";
     porneste({ capitol:"c1", lectie:"c1-introducere-si-mediu" });
   =========================================================================== */

import { CURS, LECTII, RADACINA, dupaCheie } from "./curs.js?v=83";

const SVG = {
  gata:  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12.5l5 5L20 6.5"/></svg>',
  lacat: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"><rect x="4.5" y="10.5" width="15" height="10" rx="2"/><path d="M8 10.5V7.8a4 4 0 0 1 8 0v2.7"/></svg>',
  intreb:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"><circle cx="12" cy="12" r="8.5"/><path d="M9.6 9.3a2.5 2.5 0 1 1 3.4 2.3c-.7.3-1 .8-1 1.6v.3"/><path d="M12 17h.01"/></svg>',
  stanga:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 5.5 8 12l6.5 6.5"/></svg>',
  dreapta:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.5 5.5 16 12l-6.5 6.5"/></svg>',
  lista: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h10"/></svg>',
  caut:  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="10.8" cy="10.8" r="6.3"/><path d="M15.5 15.5 20 20"/></svg>',
  caiet: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h11l5 5v11H4z"/><path d="M15 4v5h5"/></svg>',
  acasa: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 10.5 12 4l8 6.5V20H4z"/></svg>',
  carte: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v15H6.5A2.5 2.5 0 0 0 4 20.5z"/><path d="M8 7.5h8M8 11h6"/></svg>',
  grafic:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M4 20V9M10 20V4M16 20v-7M22 20H2"/></svg>'
};

/* ------------------------------------------------------------------ pornire */

export async function porneste({ capitol, lectie }){
  const slides = [...document.querySelectorAll(".sld")];
  if (!slides.length) return;

  const info = dupaCheie(lectie) || { nr:"?", titlu:document.title, scurt:"" };
  const N = slides.length;

  /* fiecare slide are nevoie de un id si de un titlu scurt */
  slides.forEach((s, i) => {
    if (!s.id) s.id = "s" + (i + 1);
    s.dataset.i = i;
    if (!s.dataset.t) s.dataset.t = s.querySelector("h2")?.textContent?.trim() || s.id;
    /* numărul slide-ului, deasupra titlului: „slide-ul 7" trebuie să se vadă */
    const cap = document.createElement("div");
    cap.className = "sld__cap";
    cap.innerHTML = `<span class="sld__nr">${String(i + 1).padStart(2,"0")} / ${N}</span>
      <span class="sld__hr"></span>
      ${s.dataset.sci ? `<span class="sld__sci" title="Social Connectedness Index, Meta Data for Good, instantaneul din 25 ianuarie 2026"><b>SCI</b>date Meta, 2026</span>` : ""}
      ${s.dataset.grup ? `<span class="sld__nr">${s.dataset.grup}</span>` : ""}`;
    s.prepend(cap);
  });

  const stare = {
    i: 0,
    vizitate: new Set(),
    liber: false,          /* profesorul poate dezactiva porțile */
    tinut: false,          /* în mod live, slide-ul meu e slide-ul lui */
    profesor: false,
    live: false            /* ora e condusă chiar acum */
  };

  const CHEIE_LOCAL = `dsw.parcurs.${capitol}`;
  let ceasToast = null, ceasSalv = null;   /* declarate aici: se folosesc din mergi() */
  let ritm = null;                         /* ora condusă; se umple mai jos */

  /* O poartă e fie o verificare cu variante, fie un exercițiu cu cod. */
  const SEL_TOATE = ".verif, .ix.exc:not(.liber)";
  const SEL_GATA  = ".verif.raspuns, .ix.exc.gata:not(.liber)";
  citesteLocal();

  construiesteSchelet();
  const el = {
    sina:   document.querySelector(".rnr__sina"),
    lista:  document.querySelector(".sina__lista"),
    bara:   document.querySelector(".sina__bara i"),
    subT:   document.querySelector(".sina__sub-t"),
    poz:    document.querySelector(".stare__poz"),
    verif:  document.querySelector(".stare__verif"),
    bLiber: document.querySelector(".stare__liber"),
    scena:  document.querySelector(".rnr__scena"),
    plt:    document.querySelector(".plt"),
    pltIn:  document.querySelector(".plt input"),
    pltLista: document.querySelector(".plt__lista"),
    toast:  document.querySelector(".toast")
  };

  deseneazaSina();
  adaugaPasi();
  lega();

  /* ce slide cerea adresa, înainte ca porțile să-l mute altundeva */
  const cerutInitial = dinAdresa();
  mergi(cerutInitial, { tacut:true });
  harta();

  /* verificarile raspund asincron: cand una se completeaza, porțile se mută */
  ["verif:raspuns", "poarta:gata"].forEach(nume =>
    document.addEventListener(nume, ev => {
      reinnoieste(); salveaza();
      import(`${RADACINA}/js/sesiune.js?v=83`)
        .then(s => s.jurnal(nume === "poarta:gata" ? "cod" : "raspuns", ev.detail))
        .catch(() => {});
    }));

  /* până aflăm dacă ora e pornită, ce se salvează e lucru de unul singur */
  import(`${RADACINA}/js/colectare.js?v=83`)
    .then(m => m.setContext("lectie")).catch(() => {});

  /* urmărirea sesiunii: de aici știu, la oră, unde a ajuns fiecare */
  import(`${RADACINA}/js/sesiune.js?v=83`)
    .then(s => s.porneste({ capitol, total:N }))
    .catch(() => { /* fără cont, nu se urmărește nimic */ });

  /* profesorul navighează liber, ca să poată arăta orice slide la clasă */
  try {
    const { profil } = await import(`${RADACINA}/js/auth.js?v=83`);
    const p = await profil();
    stare.profesor = !!p.profesor;
    if (stare.profesor){
      stare.liber = true; el.bLiber.hidden = false; reinnoieste();
      /* adresa cu #10 a fost deja limitată de porți, înainte să se știe cine
         e; acum că se știe, mergem unde ceruse link-ul */
      if (cerutInitial !== stare.i) mergi(cerutInitial, { tacut:true });
    }
  } catch { /* fără cont, lecția merge la fel */ }

  /* ora condusă: profesorul publică slide-ul lui, studenții sar după el.
     Dacă modulul nu pornește (fără cont, fără rețea), lecția merge la fel. */
  try {
    const R = await import(`${RADACINA}/js/ritm.js?v=83`);
    ritm = await R.porneste({
      capitol, total:N,
      esteProfesor: stare.profesor,
      unde: () => stare.i + 1,
      /* la ritm nu se aplică porțile: dacă profesorul arată slide-ul 9,
         slide-ul 9 se vede, chiar dacă verificarea de la 4 n-a fost făcută */
      manual: `${RADACINA}/${lectie}/tutorial/`,
      mergiLa: k => { trimiteCeEInLucru(stare.i); mergi(k, { fortat:true }); },
      /* ce se salvează de acum înainte poartă eticheta potrivită: un
         exercițiu făcut în oră nu e același lucru cu unul făcut acasă */
      laStare: (viu) => {
        stare.live  = viu;
        /* ținut = ora e deschisă ȘI nu sunt eu cel care predă. Profesorul
           umblă liber, altfel n-ar putea arăta nimic. Nu mai există al doilea
           mod: cât ora e deschisă, ei sunt pe slide-ul lui. */
        stare.tinut = !!viu && !stare.profesor;
        if (viu && !stare.profesor) stare.liber = true;  /* porțile nu mai au rost: el conduce */
        import(`${RADACINA}/js/colectare.js?v=83`)
          .then(m => m.setContext(viu ? "live" : "lectie"))
          .catch(() => {});
        reinnoieste();
      }
    });
  } catch { /* fără ora condusă, lecția merge la fel */ }

  /* --------------------------------------------------------------- porțile */

  /** Câte porți are slide-ul i și câte sunt trecute. O poartă e fie o
      verificare cu variante, fie un exercițiu cu cod: amândouă opresc
      înaintarea până sunt făcute. */
  function porti(i){
    const s = slides[i];
    return { toate: s.querySelectorAll(SEL_TOATE).length,
             date:  s.querySelectorAll(SEL_GATA).length };
  }
  /** Slide-ul i e „rezolvat": nu are verificări, sau s-a răspuns la toate. */
  function rezolvat(i){ const g = porti(i); return g.date >= g.toate; }

  /** Primul slide care încă blochează. Dincolo de el nu se trece. */
  function blocaj(){
    if (stare.liber) return N;
    for (let i = 0; i < N; i++) if (!rezolvat(i)) return i;
    return N;
  }
  function permis(j){ return j <= blocaj(); }

  function totalVerif(){
    let t = 0, d = 0;
    for (let i = 0; i < N; i++){ const g = porti(i); t += g.toate; d += g.date; }
    return { t, d };
  }

  /* --------------------------------------------- ce rămâne în urmă, în oră

     Când profesorul trece mai departe, ce e în lucru pe slide-ul pe care îl
     părăsim se trimite automat, așa cum e. Dacă nu s-a completat nimic, se
     înregistrează ca „trimis gol": zero la notă, exact ca necompletat, dar
     pentru profesor diferența e tot. Un om care a trimis gol e blocat sau se
     grăbește; unul care n-a trimis deloc nu e acolo. Două conversații
     diferite, și le vede pe amândouă în panou.

     Se întâmplă doar în oră. Acasă, un exercițiu neatins rămâne neatins. */

  async function trimiteCeEInLucru(i){
    if (!stare.live || i == null || !slides[i]) return;
    let C;
    try { C = await import(`${RADACINA}/js/colectare.js?v=83`); } catch { return; }

    for (const v of slides[i].querySelectorAll(".verif:not(.raspuns)")){
      const id = v.dataset.id;
      if (id) C.salveazaRaspuns({ intrebareId:id, capitol, raspuns:null, corect:false });
    }
    for (const x of slides[i].querySelectorAll(".ix.exc:not(.gata):not(.liber)")){
      const j = x.querySelector('script[type="application/json"]');
      if (!j) continue;
      try {
        const d = JSON.parse(j.textContent);
        if (d?.id) C.salveazaCod({ exercitiuId:d.id, cod:"", trecut:false });
      } catch {}
    }
  }

  /* ------------------------------------------------------------- navigarea */

  function mergi(j, { tacut = false, fortat = false } = {}){
    j = Math.max(0, Math.min(N - 1, j | 0));

    /* în mod live, singurul care mută slide-ul e cel de la catedră. Nu e o
       poartă, e altceva: nu „n-ai terminat încă", ci „ne uităm toți la
       același lucru". De aceea mesajul e altul, și nu te duce înapoi. */
    if (!fortat && stare.tinut){
      spune("Ora este condusă de profesor, care schimbă slide-urile.");
      return;
    }

    if (!fortat && !permis(j)){
      const b = blocaj();
      spune(`Slide-ul ${j + 1} se deschide după sarcina de la slide-ul ${b + 1}.`);
      if (stare.i !== b) mergi(b);
      return;
    }

    slides.forEach((s, k) => s.classList.toggle("on", k === j));
    stare.i = j;
    stare.vizitate.add(j);

    el.scena.scrollTop = 0;
    if (!tacut) history.replaceState(null, "", `#${j + 1}`);
    else if (!location.hash) history.replaceState(null, "", `#${j + 1}`);

    reinnoieste();
    salveaza();
    if (!fortat) ritm?.publica(j + 1);   /* fortat = vin de la profesor, nu-i trimit înapoi */
    el.sina.classList.remove("deschisa");
  }

  function dinAdresa(){
    const h = (location.hash || "").replace(/^#\/?s?/, "");
    const n = parseInt(h, 10);
    if (Number.isFinite(n) && n >= 1 && n <= N) return n - 1;
    const prin = slides.findIndex(s => s.id === (location.hash || "").slice(1));
    if (prin >= 0) return prin;
    /* fără slide în adresă, lecția începe de la primul: nu se reia de unde
       ai rămas, se reîncepe de fiecare dată */
    return 0;
  }

  /** Cel mai departe slide atins (rămâne pentru porți). */
  function ultimulAtins(){
    let max = 0;
    stare.vizitate.forEach(k => { if (k > max) max = k; });
    return Math.min(max, blocaj());
  }

  /* ------------------------------------------------------------- desenarea */

  function construiesteSchelet(){
    const gazda = document.querySelector(".rnr");
    const sina = document.createElement("aside");
    sina.className = "rnr__sina";
    sina.innerHTML = `
      <div class="sina__cap">
        <span class="sina__et">Lecția ${info.nr}</span>
        <span class="sina__t">${info.titlu}</span>
        <div class="sina__sub">
          <span class="sina__bara"><i></i></span>
          <span class="sina__sub-t">0%</span>
        </div>
      </div>
      <nav class="sina__lista" aria-label="Cuprinsul lecției"></nav>
      <div class="sina__jos">
        <a class="sina__leg" href="${RADACINA}/${lectie}/tutorial/">${SVG.carte}<span>Manualul</span></a>
        <a class="sina__leg" href="${RADACINA}/${lectie}/">${SVG.acasa}<span>Pagina cursului</span></a>
        <a class="sina__leg" href="${RADACINA}/cont/">${SVG.grafic}<span>Contul meu</span></a>
        ${info.notebook ? `<a class="sina__leg" href="${info.notebook}" target="_blank"
            rel="noopener">${SVG.caiet}<span>Caietul lecției</span></a>` : ""}
      </div>`;
    gazda.prepend(sina);

    const bara = document.createElement("div");
    bara.className = "stare";
    bara.innerHTML = `
      <button class="stare__c sina-btn" type="button" aria-label="Cuprins">${SVG.lista}</button>
      <span class="stare__c stare__ascuns-mic">${CURS.scurt} · lecția ${info.nr}</span>
      <span class="stare__gol"></span>
      <span class="stare__c stare__verif"></span>
      <button class="stare__c stare__liber" type="button" hidden
              title="Profesor: dezactivează porțile">porți: închise</button>
      <span class="stare__c stare__poz"></span>
      <button class="stare__c" type="button" id="btn-plt">${SVG.caut}<span>salt la…</span></button>`;
    document.body.appendChild(bara);

    /* --- comanda de sus ---------------------------------------------------
       Un buton de slide următor care e mereu la vedere, ca să nu cauți
       tastatura în fața clasei, și care nu stă în drum: stă decolorat până
       pui mâna pe el. Lângă el, modul de prezentare.

       Jos nu se putea pune: acolo e banda orei, iar în mod prezentare
       cuprinsul dispare și n-ar mai rămâne niciun buton de mers înainte. */
    const sus = document.createElement("div");
    sus.className = "nav-sus";
    sus.innerHTML = `
      <button class="nav-sus__b" type="button" data-n="-1" aria-label="Slide-ul anterior">‹</button>
      <span class="nav-sus__n" aria-live="off"></span>
      <button class="nav-sus__b" type="button" data-n="1" aria-label="Slide-ul următor">›</button>
      <button class="nav-sus__b nav-sus__b--f" type="button" data-rol="prezint"
              title="Prezentare, fără cuprins și antet (F)" aria-label="Mod prezentare">⛶</button>`;
    document.body.appendChild(sus);
    sus.querySelectorAll("[data-n]").forEach(b =>
      b.addEventListener("click", () => mergi(stare.i + (+b.dataset.n))));
    sus.querySelector('[data-rol="prezint"]').addEventListener("click", prezint);

    /* --- modul prezentare -------------------------------------------------
       Ascunde tot ce nu e slide: antetul, cuprinsul, bara de jos. Cere și
       ecranul întreg de la browser, dar nu se supără dacă îl refuză: clasa
       de pe <body> face oricum treaba. */
    function prezint(){
      const acum = document.body.classList.toggle("prezint");
      try {
        if (acum && !document.fullscreenElement) document.documentElement.requestFullscreen?.();
        else if (!acum && document.fullscreenElement) document.exitFullscreen?.();
      } catch { /* fără ecran întreg, tot se vede doar slide-ul */ }
    }
    document.addEventListener("fullscreenchange", () => {
      if (!document.fullscreenElement) document.body.classList.remove("prezint");
    });

    const plt = document.createElement("div");
    plt.className = "plt";
    plt.hidden = true;
    plt.innerHTML = `
      <div class="plt__cutie" role="dialog" aria-label="Salt la slide">
        <div class="plt__cauta">${SVG.caut}
          <input type="text" placeholder="Numărul slide-ului sau un cuvânt din titlu…"
                 autocomplete="off" spellcheck="false"></div>
        <div class="plt__lista"></div>
        <div class="plt__jos">
          <span><kbd>↑</kbd><kbd>↓</kbd> selectare</span>
          <span><kbd>Enter</kbd> deschidere</span>
          <span><kbd>Esc</kbd> închidere</span>
          <span>în orice moment: tastează numărul slide-ului</span>
        </div>
      </div>`;
    document.body.appendChild(plt);

    const t = document.createElement("div");
    t.className = "toast";
    t.setAttribute("role", "status");
    document.body.appendChild(t);
  }

  function deseneazaSina(){
    let html = "", grup = null;
    slides.forEach((s, i) => {
      if (s.dataset.grup && s.dataset.grup !== grup){
        grup = s.dataset.grup;
        html += `<div class="sina__grup">${grup}</div>`;
      }
      html += `<button class="rnd" data-j="${i}" type="button">
          <span class="rnd__n">${i + 1}</span>
          <span class="rnd__t">${s.dataset.t}</span>
          <span class="rnd__s"></span>
        </button>`;
    });
    el.lista.innerHTML = html;
    el.lista.addEventListener("click", ev => {
      const r = ev.target.closest(".rnd");
      if (r) mergi(+r.dataset.j);
    });
  }

  /** Fiecare slide primește jos o pereche înapoi/înainte și, dacă are
      verificări, o casetă care spune de ce nu merge încă mai departe. */
  function adaugaPasi(){
    slides.forEach((s, i) => {
      const g = porti(i);
      if (g.toate){
        const p = document.createElement("div");
        p.className = "poarta";
        p.innerHTML = `
          <span class="poarta__ic">${SVG.lacat}</span>
          <div><p class="poarta__t"></p><p class="poarta__d"></p></div>`;
        s.appendChild(p);
      }
      const nav = document.createElement("div");
      nav.className = "pasi";
      nav.innerHTML = `
        <button class="pas pas--inapoi" type="button">${SVG.stanga}<span>Înapoi</span></button>
        <span class="pasi__gol"></span>
        <span class="pas__nota" hidden></span>
        <button class="pas pas--tare pas--inainte" type="button">
          <span>${i === N - 1 ? "Încheie lecția" : "Înainte"}</span>${SVG.dreapta}</button>`;
      s.appendChild(nav);
      nav.querySelector(".pas--inapoi").onclick = () => mergi(i - 1);
      nav.querySelector(".pas--inainte").onclick = () => {
        if (i === N - 1) location.href = `${RADACINA}/${lectie}/#gata`;
        else mergi(i + 1);
      };
    });
  }

  /** Reașază tot ce depinde de stare: cuprins, porți, bara de jos. */
  function reinnoieste(){
    const b = blocaj();

    [...el.lista.querySelectorAll(".rnd")].forEach(r => {
      const j = +r.dataset.j;
      const g = porti(j);
      r.classList.toggle("acum", j === stare.i);
      const fapt = stare.vizitate.has(j) && g.date >= g.toate;
      r.classList.toggle("gata", fapt);
      r.classList.toggle("blocat", !permis(j));
      const s = r.querySelector(".rnd__s");
      s.innerHTML = !permis(j) ? SVG.lacat
                  : fapt       ? SVG.gata
                  : g.toate && g.date < g.toate ? SVG.intreb : "";
    });

    slides.forEach((s, i) => {
      const g = porti(i);
      const p = s.querySelector(".poarta");
      if (p){
        const ok = g.date >= g.toate;
        p.classList.toggle("deschisa", ok);
        p.querySelector(".poarta__ic").innerHTML = ok ? SVG.gata : SVG.lacat;
        /* numim lucrul după ce e: verificare, exercițiu, sau amândouă */
        const nQ = s.querySelectorAll(".verif").length;
        const nC = s.querySelectorAll(".ix.exc:not(.liber)").length;
        const cuv = nQ && nC ? ["sarcinile de mai sus", "Sarcinile de mai sus sunt rezolvate."]
                  : nC       ? (nC > 1 ? ["exercițiile de mai sus", "Exercițiile sunt rezolvate."]
                                       : ["exercițiul de mai sus", "Exercițiul este rezolvat."])
                             : (nQ > 1 ? ["verificările de mai sus", "Verificările sunt completate."]
                                       : ["verificarea de mai sus", "Verificarea este completată."]);
        p.querySelector(".poarta__t").textContent = ok ? cuv[1] : `Completează ${cuv[0]}.`;
        p.querySelector(".poarta__d").textContent = ok
          ? "Poți trece la slide-ul următor. Rezolvarea rămâne înregistrată."
          : nC && !nQ
            ? "Apasă Rulează pentru verificare. Butonul Indiciu oferă o sugestie."
            : "Pentru a trece mai departe este suficient un răspuns, nu neapărat cel corect. Explicația apare după alegere.";
      }
      const inainte = s.querySelector(".pas--inainte");
      const inapoi  = s.querySelector(".pas--inapoi");
      const nota    = s.querySelector(".pas__nota");
      const poate = stare.liber || g.date >= g.toate;
      /* în mod live butoanele dispar cu totul, nu doar se sting: altfel
         jumătate din clasă le apasă la nesfârșit și crede că s-a stricat */
      inapoi.hidden  = stare.tinut;
      inainte.hidden = stare.tinut;
      inapoi.disabled = i === 0;
      inainte.disabled = !poate;
      nota.hidden = stare.tinut ? false : poate;
      if (stare.tinut) nota.textContent = "Ora este condusă de profesor, care schimbă slide-urile.";
      else if (!poate) nota.textContent = g.toate > 1
        ? "Sarcinile de mai sus deblochează slide-ul următor."
        : "Sarcina de mai sus deblochează slide-ul următor.";
    });

    const v = totalVerif();
    el.verif.innerHTML = v.t
      ? `<span class="stare__dot ${v.d >= v.t ? "ok" : "nu"}"></span>verificări ${v.d}/${v.t}`
      : "";
    el.poz.innerHTML = `slide <b>${stare.i + 1}</b>/${N}`;
    const nsus = document.querySelector(".nav-sus__n");
    if (nsus) nsus.textContent = `${stare.i + 1}/${N}`;
    const proc = Math.round((stare.vizitate.size / N) * 100);
    el.bara.style.width = proc + "%";
    el.subT.textContent = `${stare.vizitate.size}/${N} · ${proc}%`;
    el.bLiber.textContent = stare.liber ? "porți: deschise" : "porți: închise";
    el.bLiber.classList.toggle("stare--acc", stare.liber);
  }

  /* ---------------------------------------------------------------- paleta */

  function paleta(deschide){
    el.plt.hidden = !deschide;
    if (deschide){ el.pltIn.value = ""; filtreaza(""); el.pltIn.focus(); }
    else {
      /* fără asta, focusul rămâne în câmpul paletei și tastele de navigare
         nu mai funcționează: le ignorăm intenționat când cineva scrie */
      el.pltIn.blur();
      el.scena.focus({ preventScroll:true });
    }
  }

  let sel = 0;
  function filtreaza(q){
    q = q.trim().toLowerCase();
    const n = parseInt(q, 10);
    let r = slides.map((s, i) => ({ i, t: s.dataset.t }));
    if (q){
      r = Number.isFinite(n) && String(n) === q
        ? r.filter(x => String(x.i + 1).startsWith(q))
        : r.filter(x => x.t.toLowerCase().includes(q));
    }
    sel = 0;
    el.pltLista.innerHTML = r.length ? r.map((x, k) => {
      const g = porti(x.i);
      const et = !permis(x.i) ? "blocat" : g.toate ? "verificare" : "";
      return `<button class="plt__r ${k === 0 ? "sel" : ""}" data-j="${x.i}" type="button">
        <span class="n">${x.i + 1}</span><span class="t">${x.t}</span>
        <span class="g">${et}</span></button>`;
    }).join("") : `<div style="padding:14px;color:var(--text-3);font-family:var(--sans);
        font-size:var(--t2)">Niciun slide nu conține „${q}”.</div>`;
  }

  function alege(d){
    const r = [...el.pltLista.querySelectorAll(".plt__r")];
    if (!r.length) return;
    sel = (sel + d + r.length) % r.length;
    r.forEach((x, k) => x.classList.toggle("sel", k === sel));
    r[sel].scrollIntoView({ block:"nearest" });
  }

  /* -------------------------------------------------------------- legături */

  function lega(){
    document.querySelector("#btn-plt").onclick = () => paleta(true);
    document.querySelector(".sina-btn").onclick = () => el.sina.classList.toggle("deschisa");
    el.bLiber.onclick = () => {
      if (!stare.profesor) return;
      stare.liber = !stare.liber; reinnoieste();
      spune(stare.liber ? "Porțile sunt deschise doar pentru tine, pe acest calculator."
                        : "Porțile sunt închise, ca pentru studenți.");
    };

    el.plt.addEventListener("click", ev => {
      const r = ev.target.closest(".plt__r");
      if (r){ paleta(false); mergi(+r.dataset.j); return; }
      if (ev.target === el.plt) paleta(false);
    });
    el.pltIn.addEventListener("input", () => filtreaza(el.pltIn.value));
    el.pltIn.addEventListener("keydown", e => {
      if (e.key === "ArrowDown"){ e.preventDefault(); alege(1); }
      else if (e.key === "ArrowUp"){ e.preventDefault(); alege(-1); }
      else if (e.key === "Enter"){
        const r = el.pltLista.querySelector(".plt__r.sel");
        if (r){ paleta(false); mergi(+r.dataset.j); }
      } else if (e.key === "Escape") paleta(false);
    });

    let tampon = "", ceas = null;
    document.addEventListener("keydown", e => {
      if ((e.key === "k" || e.key === "K") && (e.metaKey || e.ctrlKey)){
        e.preventDefault(); paleta(true); return;
      }
      if (e.key === "Escape"){
        if (!el.plt.hidden) paleta(false);
        el.sina.classList.remove("deschisa");
        return;
      }
      if (!el.plt.hidden) return;
      /* nu furăm tastele când scrie cineva în terminal sau într-un câmp */
      const t = e.target;
      if (t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.isContentEditable)) return;
      if (e.metaKey || e.ctrlKey || e.altKey) return;

      if (e.key === "ArrowRight" || e.key === "PageDown" || e.key === "n"){
        e.preventDefault(); mergi(stare.i + 1);
      } else if (e.key === "ArrowLeft" || e.key === "PageUp" || e.key === "p"){
        e.preventDefault(); mergi(stare.i - 1);
      } else if (e.key === "f" || e.key === "F"){
        e.preventDefault();
        document.querySelector('[data-rol="prezint"]')?.click();
      } else if (e.key === "Home"){ e.preventDefault(); mergi(0); }
      else if (e.key === "End"){ e.preventDefault(); mergi(N - 1); }
      else if (/^[0-9]$/.test(e.key)){
        /* „mergeți la slide-ul 12": tastezi 1 apoi 2 */
        tampon += e.key;
        clearTimeout(ceas);
        const n = parseInt(tampon, 10);
        spune(`slide ${tampon}…`, 700);
        ceas = setTimeout(() => {
          if (n >= 1 && n <= N) mergi(n - 1);
          else spune(`Lecția are ${N} slide-uri.`);
          tampon = "";
        }, 620);
      }
    });

    window.addEventListener("hashchange", () => {
      const j = dinAdresa();
      if (j !== stare.i) mergi(j, { tacut:true });
    });
  }

  /* ---------------------------------------------------------- memorie, mesaje */

  function spune(text, ms = 2600){
    el.toast.textContent = text;
    el.toast.classList.add("vazut");
    clearTimeout(ceasToast);
    ceasToast = setTimeout(() => el.toast.classList.remove("vazut"), ms);
  }

  function citesteLocal(){
    try {
      const x = JSON.parse(localStorage.getItem(CHEIE_LOCAL) || "{}");
      (x.vizitate || []).forEach(k => stare.vizitate.add(k));
    } catch { /* fără memorie locală, lecția merge la fel */ }
  }

  function salveaza(){
    try {
      localStorage.setItem(CHEIE_LOCAL, JSON.stringify({
        vizitate:[...stare.vizitate], total:N, cand:Date.now()
      }));
    } catch {}
    clearTimeout(ceasSalv);
    ceasSalv = setTimeout(async () => {
      const id = slides[stare.i].id;
      try {
        const { marcheazaSectiune } = await import(`${RADACINA}/js/colectare.js?v=83`);
        await marcheazaSectiune(`${capitol}/${id}`);
      } catch {}
      try {
        const s = await import(`${RADACINA}/js/sesiune.js?v=83`);
        s.laSlide({ slide:id, nr:stare.i + 1, total:N });
      } catch {}
    }, 900);
  }

  /** Harta lecției, pentru pagina de progres: câte slide-uri are, cum se
      numesc, și ce verificări stau pe fiecare. Id-urile, nu doar numărul:
      altfel pagina de progres nu poate spune care verificare e făcută. */
  function harta(){
    try {
      localStorage.setItem(`dsw.harta.${capitol}`, JSON.stringify({
        total:N,
        titluri:slides.map(s => s.dataset.t),
        verif:slides.map(s => [
          ...[...s.querySelectorAll(".verif")].map(v => v.dataset.id),
          ...[...s.querySelectorAll(".ix.exc:not(.liber)")].map((_, k) => `${s.id}-cod${k + 1}`)
        ])
      }));
    } catch {}
  }
}
