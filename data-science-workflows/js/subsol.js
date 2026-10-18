/* ===========================================================================
   Subsolul comun. <div id="subsol"></div> plus acest modul.

   Și aici se schimbă după rol: „Progresul meu" în subsolul fiecărei pagini,
   când tu ești cel care ține cursul, e aceeași greșeală ca pe pagina de
   acasă. Un singur produs per rol, inclusiv în locurile mici.

   Linkul către „Surse de date" a fost scos: pagina nu există în depozit, deci
   era un link mort în subsolul fiecărei pagini din sit. Se pune la loc în
   ziua în care există fișierul, nu înainte.
   =========================================================================== */

import { CURS, RADACINA } from "./curs.js?v=42";

deseneaza(false);

function deseneaza(profesor){
  const g = document.getElementById("subsol");
  if (!g) return;
  g.outerHTML = `
  <footer class="subsol" id="subsol"><div class="pagina subsol__in">
    <span>${CURS.institutie}</span>
    ${profesor
      ? `<a href="${RADACINA}/predau/">Predau</a>
         <a href="${RADACINA}/predau/sedinte/">Ședințele</a>`
      : (location.pathname.replace(/\/+$/, "/") === `${RADACINA}/cont/`
          ? ""                       /* ești deja acolo: linkul ar fi spre tine */
          : `<a href="${RADACINA}/cont/">Contul meu</a>`)}
    <a href="${RADACINA}/date-personale/">Date personale</a>
    <a href="${CURS.depozit}" target="_blank" rel="noopener">Depozit ↗</a>
    <span class="subsol__dr">${CURS.an}</span>
  </div></footer>`;
}

/* Rolul se află târziu, deci subsolul se desenează o dată fără el și se
   rescrie doar dacă e cazul. Pagina nu așteaptă după autentificare. */
try {
  const { profil } = await import(`${RADACINA}/js/auth.js?v=42`);
  const p = await profil();
  if (p.profesorReal) deseneaza(true);
} catch { /* fără cont, subsolul public e cel bun */ }
