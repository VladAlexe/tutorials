/* ===========================================================================
   Antetul comun: marca, firimituri, comutator de tema, starea contului.

   Se include o singura data pe pagina:
     <div id="antet" data-aici="Titlul paginii"></div>
     <script type="module" src="/data-science-workflows/js/antet.js?v=41"></script>

   Daca pagina e o lectie, pune si data-lectie="c2-colectarea-prin-api" si
   antetul deseneaza sub el banda cu fluxul.
   =========================================================================== */

import { CURS, LECTII, RADACINA, dupaCheie } from "./curs.js?v=41";

const SVG = {
  soare: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"><circle cx="12" cy="12" r="4.2"/><path d="M12 2.6v2.1M12 19.3v2.1M4.2 4.2l1.5 1.5M18.3 18.3l1.5 1.5M2.6 12h2.1M19.3 12h2.1M4.2 19.8l1.5-1.5M18.3 5.7l1.5-1.5"/></svg>',
  luna:  '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M20.5 14.2A8.6 8.6 0 1 1 9.8 3.5a6.9 6.9 0 0 0 10.7 10.7z"/></svg>',
  clasa: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"><path d="M3 20V9M9 20V4M15 20v-8M21 20v-5"/></svg>',
  ochi:  '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12z"/><circle cx="12" cy="12" r="2.8"/></svg>',
  /* marca DSW: fluxul intră, trece prin două noduri și se ramifică.
     Liniile iau culoarea textului (merg în ambele teme), nodurile paleta. */
  marca: '<svg class="marca" width="26" height="26" viewBox="0 0 64 64" fill="none" aria-hidden="true"><g stroke="currentColor" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"><path d="M5 9H24Q30 9 30 15V49Q30 55 24 55H15Q10 55 10 60"/><path d="M18.5 3.5 24 9l-5.5 5.5"/><path d="M35 22h5l8.5-9"/><path d="M35 42h6l7.5-7M41 42l7.5 7"/><circle cx="30" cy="22" r="5" fill="var(--accent)"/><circle cx="30" cy="42" r="5" fill="var(--ceas)"/><circle cx="52" cy="10" r="4" fill="var(--panza)"/><circle cx="52" cy="32" r="4" fill="var(--panza)"/><circle cx="52" cy="52" r="4" fill="var(--panza)"/></g></svg>'
};

const gazda = document.getElementById("antet");
if (gazda) construieste(gazda);

function construieste(gazda){
  const aici    = gazda.dataset.aici || "";
  const cheie   = gazda.dataset.lectie || null;
  const lectie  = cheie ? dupaCheie(cheie) : null;
  /* data-crom: antetul unei pagini-aplicație, lipit de barele din jur,
     fără coloana centrată a paginilor de citit */
  const crom    = gazda.hasAttribute("data-crom");
  /* data-predau: antetul produsului de predare. Alt antet, nu același cu un
     buton în plus: aici nu există „contul meu", „progresul meu", „lecțiile
     mele". Aici predai, nu parcurgi. */
  const predau  = gazda.hasAttribute("data-predau");

  if (!document.querySelector('link[rel="icon"]')){
    const ic = document.createElement("link");
    ic.rel = "icon"; ic.type = "image/svg+xml"; ic.href = `${RADACINA}/img/dsw.svg`;
    document.head.appendChild(ic);
  }
  gazda.outerHTML = `
    <header class="antet ${crom ? "antet--crom" : ""}">
      <div class="${crom ? "" : "pagina"} antet__in">
        <a class="antet__marca" href="${RADACINA}/" aria-label="${CURS.titlu}">
          ${SVG.marca}<span class="antet__nume">${CURS.scurt}</span>
        </a>
        ${predau ? `
        <nav class="predau-nav" aria-label="Predare">
          ${[["", "Lecțiile"], ["ora/", "Ora"], ["sedinte/", "Ședințele"],
             ["semestru/", "Semestrul"]].map(([u, t]) => {
            const h = `${RADACINA}/predau/${u}`;
            const acum = location.pathname.replace(/\/+$/, "/") === h.replace(/\/+$/, "/");
            return `<a href="${h}" class="${acum ? "on" : ""}"
                       ${acum ? 'aria-current="page"' : ""}>${t}</a>`;
          }).join("")}
        </nav>` : `
        <nav class="firimituri" aria-label="Unde ești">
          ${aici ? `<span class="sep">/</span><span class="aici">${aici}</span>` : ""}
        </nav>`}
        <div class="antet__dr">
          <button class="icon-btn" id="btn-tema" type="button"
                  aria-label="Schimbă tema"></button>
          <span id="zona-cont"></span>
        </div>
      </div>
    </header>
    ${lectie ? banda(lectie) : ""}`;

  /* tema */
  const bt = document.getElementById("btn-tema");
  const pictTema = () => { bt.innerHTML = window.dswTema.curenta() === "intunecat" ? SVG.soare : SVG.luna; };
  pictTema();
  bt.addEventListener("click", () => { window.dswTema.comuta(); pictTema(); });

  cont(predau);
}

/* Banda de sub antet, pe pagina unei lecții. Studentul vede în ea doar
   lecțiile ținute, ca să nu i se arate drumul până la capăt din prima zi.
   Se desenează întâi întreagă, pentru că pagina nu așteaptă după rețea, și se
   taie pe urmă dacă e cazul. */
async function taieBanda(profesor){
  const g = document.querySelector(".flux__sina");
  if (!g || profesor) return;
  try {
    const O = await import(`${RADACINA}/js/ora.js?v=41`);
    const p = await O.predate();
    if (!p) return;
    g.querySelectorAll("[data-c]").forEach(a => {
      if (!p.has(a.dataset.c)) a.remove();
    });
    /* dacă n-a mai rămas nimic, banda goală arată ca un sit stricat: o scot */
    if (!g.querySelector(".etapa")) g.closest(".flux")?.remove();
  } catch { /* fără bază, banda rămâne întreagă */ }
}

function banda(lectie){
  return `<div class="flux flux--banda"><div class="pagina"><div class="flux__sina">
    ${LECTII.map(l => {
      const stare = l.nr < lectie.nr ? "gata" : l.nr === lectie.nr ? "acum" : "viitor";
      return `<a class="etapa ${stare}" href="${RADACINA}/${l.cheie}/" data-c="c${l.nr}"
                 ${stare === "acum" ? 'aria-current="page"' : ""}>
                <span class="etapa__nod">${l.nr}</span>
                <span class="etapa__et">${l.scurt}</span></a>`;
    }).join("")}
  </div></div></div>`;
}

/* --- starea contului ------------------------------------------------------
   Se incarca lenes: pagina nu asteapta dupa ea. Daca autentificarea nu e
   configurata, nu apare nimic si pagina ramane intacta.
   ------------------------------------------------------------------------- */

async function cont(predau){
  const zona = document.getElementById("zona-cont");
  if (!zona) return;
  try {
    const { profil } = await import(`${RADACINA}/js/auth.js?v=41`);
    const p = await profil();
    if (p.autentificat) taieBanda(p.profesorReal);
    if (!p.autentificat) {
      zona.innerHTML = `<a class="btn-intra" href="${RADACINA}/cont/">Intră în cont</a>`;
      return;
    }
    /* în produsul de predare, antetul nu mai vinde nimic: numele, și ieșirea */
    if (predau){
      /* Dacă ai rămas cu „vezi ca student" pornit de la o verificare de acum
         două săptămâni, intrarea în /predau/ îl stinge. Altfel situl te ține
         jumătate profesor, jumătate student, și pare că ai două conturi. */
      try {
        const { modVizualizare, setModVizualizare } = await import(`${RADACINA}/js/auth.js?v=41`);
        if (modVizualizare() === "student") setModVizualizare("profesor");
      } catch {}
      zona.innerHTML = `<span class="pred-cine">${p.nume || p.email || ""}</span>
        <a class="icon-btn" href="${RADACINA}/" title="Pagina cursului, cum o văd ei"
           aria-label="Pagina cursului">${SVG.ochi}</a>`;
      return;
    }
    /* profesorul are casa lui; studentul nu afla ca exista */
    const clasa = p.profesor
      ? `<a class="btn-intra" href="${RADACINA}/predau/" title="Produsul de predare">Predau</a>`
      : "";
    const nume = p.nume || p.email || "Contul meu";
    const ini = nume.trim().split(/\s+/).slice(0,2).map(x=>x[0]||"").join("").toUpperCase() || "?";
    const acasa = p.profesor ? `${RADACINA}/predau/` : `${RADACINA}/cont/`;
    zona.innerHTML = clasa +
      `<a class="cont-chip" href="${acasa}" title="${nume}">
         <span class="cont-chip__cerc">${ini}</span>
         <span>${nume.split(/\s+/)[0]}</span>
       </a>`;
  } catch {
    zona.innerHTML = `<a class="btn-intra" href="${RADACINA}/cont/">Intră în cont</a>`;
  }
}
