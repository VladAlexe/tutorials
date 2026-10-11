/* Subsolul comun. <div id="subsol"></div> plus acest modul. */
import { CURS, RADACINA } from "./curs.js?v=11";

const g = document.getElementById("subsol");
if (g) g.outerHTML = `
  <footer class="subsol"><div class="pagina subsol__in">
    <span>${CURS.institutie}</span>
    <a href="${RADACINA}/cont/" id="subsol-cont">Contul meu</a>
    <a href="${RADACINA}/surse-de-date.html">Surse de date</a>
    <a href="${RADACINA}/date-personale/">Date personale</a>
    <a href="${CURS.depozit}" target="_blank" rel="noopener">Depozit</a>
    <span class="subsol__dr">${CURS.an}</span>
  </div></footer>`;

/* Profesorul n-are „contul meu": are panoul. Întrebăm abia după ce s-a
   desenat subsolul, ca pagina să nu aştepte după autentificare. */
import(`${RADACINA}/js/auth.js?v=11`)
  .then(m => m.profil())
  .then(p => {
    if (!p?.profesor) return;
    const a = document.getElementById("subsol-cont");
    if (a){ a.href = `${RADACINA}/panou/`; a.textContent = "Panoul meu"; }
  })
  .catch(() => { /* fără cont, rămâne cum e */ });
