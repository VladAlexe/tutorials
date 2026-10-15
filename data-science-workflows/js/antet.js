/* ===========================================================================
   Antetul comun: marca, firimituri, comutator de tema, starea contului.

   Se include o singura data pe pagina:
     <div id="antet" data-aici="Titlul paginii"></div>
     <script type="module" src="/data-science-workflows/js/antet.js?v=26"></script>

   Daca pagina e o lectie, pune si data-lectie="c2-colectarea-prin-api" si
   antetul deseneaza sub el banda cu fluxul.
   =========================================================================== */

import { CURS, LECTII, RADACINA, dupaCheie } from "./curs.js?v=26";

const SVG = {
  soare: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"><circle cx="12" cy="12" r="4.2"/><path d="M12 2.6v2.1M12 19.3v2.1M4.2 4.2l1.5 1.5M18.3 18.3l1.5 1.5M2.6 12h2.1M19.3 12h2.1M4.2 19.8l1.5-1.5M18.3 5.7l1.5-1.5"/></svg>',
  luna:  '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M20.5 14.2A8.6 8.6 0 1 1 9.8 3.5a6.9 6.9 0 0 0 10.7 10.7z"/></svg>',
  clasa: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"><path d="M3 20V9M9 20V4M15 20v-8M21 20v-5"/></svg>',
  ochi:  '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12z"/><circle cx="12" cy="12" r="2.8"/></svg>',
  marca: '<svg width="21" height="21" viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="5" cy="6" r="2.3" stroke="currentColor" stroke-width="1.7"/><circle cx="5" cy="18" r="2.3" stroke="currentColor" stroke-width="1.7"/><circle cx="19" cy="12" r="2.3" stroke="currentColor" stroke-width="1.7"/><path d="M7.2 7.1 16.8 11M7.2 16.9 16.8 13" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></svg>'
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

  gazda.outerHTML = `
    <header class="antet ${crom ? "antet--crom" : ""}">
      <div class="${crom ? "" : "pagina"} antet__in">
        <a class="antet__marca" href="${RADACINA}/" aria-label="${CURS.titlu}">
          ${SVG.marca}<span class="antet__nume">${CURS.scurt}</span>
        </a>
        ${predau ? `
        <nav class="predau-nav" aria-label="Predare">
          ${[["", "Azi"], ["ora/", "Ora"], ["sedinte/", "Ședințele"]].map(([u, t]) => {
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

function banda(lectie){
  return `<div class="flux flux--banda"><div class="pagina"><div class="flux__sina">
    ${LECTII.map(l => {
      const stare = l.nr < lectie.nr ? "gata" : l.nr === lectie.nr ? "acum" : "viitor";
      return `<a class="etapa ${stare}" href="${RADACINA}/${l.cheie}/"
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
    const { profil } = await import(`${RADACINA}/js/auth.js?v=26`);
    const p = await profil();
    if (!p.autentificat) {
      zona.innerHTML = `<a class="btn-intra" href="${RADACINA}/cont/">Intră în cont</a>`;
      return;
    }
    /* în produsul de predare, antetul nu mai vinde nimic: numele, și ieșirea */
    if (predau){
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
