/* Subsolul comun. <div id="subsol"></div> plus acest modul. */
import { CURS, RADACINA } from "./curs.js?v=1";

const g = document.getElementById("subsol");
if (g) g.outerHTML = `
  <footer class="subsol"><div class="pagina subsol__in">
    <span>${CURS.institutie}</span>
    <a href="${RADACINA}/date-personale/">Date personale</a>
    <a href="${CURS.depozit}" target="_blank" rel="noopener">Depozit</a>
    <span class="subsol__dr">${CURS.an}</span>
  </div></footer>`;
