/* ===========================================================================
   Subsolul comun. <div id="subsol"></div> plus acest modul.

   Și aici se schimbă după rol: „Progresul meu" în subsolul fiecărei pagini,
   când tu ești cel care ține cursul, e aceeași greșeală ca pe pagina de
   acasă. Un singur produs per rol, inclusiv în locurile mici.

   Linkul către „Surse de date" a fost scos: pagina nu există în depozit, deci
   era un link mort în subsolul fiecărei pagini din sit. Se pune la loc în
   ziua în care există fișierul, nu înainte.
   =========================================================================== */

import { CURS, RADACINA } from "./curs.js?v=73";

deseneaza();

/* Subsolul e același pentru toți: contul și predarea stau în antet, într-un
   singur loc, nu repetate jos. */
function deseneaza(){
  const g = document.getElementById("subsol");
  if (!g) return;
  g.outerHTML = `
  <footer class="subsol" id="subsol"><div class="pagina subsol__in">
    <span>${CURS.institutie}</span>
    <a href="${RADACINA}/">Cursul</a>
    <a href="${RADACINA}/date-personale/">Protecția datelor</a>
    <a href="${CURS.depozit}" target="_blank" rel="noopener">Depozit ↗</a>
    <span class="subsol__dr">${CURS.an}</span>
  </div></footer>`;
}
