/* ===========================================================================
   Comutatorul de vizualizare

   Se include in ORICE pagina a cursului, cu o singura linie:
       <script type="module" src="/data-science-workflows/js/bara-mod.js"></script>

   Nu face nimic pentru studenti: bara apare doar daca esti profesor.
   Alegerea e valabila pe tot site-ul, nu doar pe pagina curenta.
   =========================================================================== */

import { profil, modVizualizare, setModVizualizare } from "./auth.js?v=31";

const CSS = `
.bara-mod{position:fixed;right:16px;bottom:16px;z-index:9999;display:flex;align-items:center;
  gap:10px;padding:8px 10px 8px 14px;border-radius:30px;
  font-family:'IBM Plex Sans',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
  font-size:12.5px;font-weight:600;box-shadow:0 3px 14px rgba(0,0,0,.18);
  background:#23231A;color:#E9E7E0;border:1.5px solid #23231A}
.bara-mod--student{background:#5E7A6C;border-color:#4C6558}
.bara-mod__et{opacity:.65;font-weight:500}
.bara-mod__val{letter-spacing:.02em}
.bara-mod__b{font:inherit;font-size:11.5px;font-weight:700;letter-spacing:.04em;
  padding:5px 11px;border-radius:20px;cursor:pointer;transition:.15s;
  background:rgba(255,255,255,.14);color:inherit;border:0}
.bara-mod__b:hover{background:rgba(255,255,255,.26)}
.bara-mod__b:focus-visible{outline:2px solid #fff;outline-offset:2px}
@media(max-width:560px){.bara-mod{right:10px;bottom:10px;font-size:11.5px;padding:7px 9px 7px 12px}}
`;

async function porneste() {
  let p;
  try { p = await profil(); } catch { return; }
  if (!p.autentificat || !p.profesorReal) return;   // studentii nu vad nimic

  const stil = document.createElement("style");
  stil.textContent = CSS;
  document.head.appendChild(stil);

  const student = modVizualizare() === "student";
  const bara = document.createElement("div");
  bara.className = "bara-mod" + (student ? " bara-mod--student" : "");
  bara.setAttribute("role", "status");
  bara.innerHTML = `
    <span class="bara-mod__et">Vezi ca</span>
    <span class="bara-mod__val">${student ? "student" : "profesor"}</span>
    <button class="bara-mod__b" type="button">${student ? "ieși" : "treci la student"}</button>`;

  bara.querySelector("button").addEventListener("click", () => {
    setModVizualizare(student ? "profesor" : "student");
    location.reload();
  });

  document.body.appendChild(bara);
}

if (document.readyState === "loading")
  document.addEventListener("DOMContentLoaded", porneste);
else porneste();
