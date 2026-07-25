/* blocuri.js — un renderer per tip de bloc. Randorul NU cunoaște componentele
   interactive: le cere registrului după nume (bloc.componenta). Astfel se poate
   adăuga o componentă nouă fără să atingi acest fișier.

   Tipuri de bloc: text, lista, nota, cod, tabel, verificare, interactiv, in_lucru.
*/

import { componenta } from "./interactive/index.js";
import * as progres from "./progres.js";

function el(tag, clasa, html) {
  const e = document.createElement(tag);
  if (clasa) e.className = clasa;
  if (html != null) e.innerHTML = html;
  return e;
}

/* ---------- randere simple ---------- */

function text(b) {
  return el("p", null, b.continut);
}

function lista(b) {
  const ul = el("ul");
  (b.elemente || []).forEach((x) => ul.appendChild(el("li", null, x)));
  return ul;
}

function nota(b) {
  const d = el("div", "note");
  d.appendChild(el("b", null, b.eticheta || ""));
  d.appendChild(el("p", null, b.continut));
  return d;
}

function cod(b) {
  const d = el("div", "codeblk", b.continut);
  if (b.limbaj) d.dataset.limbaj = b.limbaj;
  return d;
}

function tabel(b) {
  const t = el("table", "tbl");
  const thead = el("thead");
  const trh = el("tr");
  (b.antet || []).forEach((h) => trh.appendChild(el("th", null, h)));
  thead.appendChild(trh);
  const tbody = el("tbody");
  (b.randuri || []).forEach((r) => {
    const tr = el("tr");
    r.forEach((c) => tr.appendChild(el("td", null, c)));
    tbody.appendChild(tr);
  });
  t.appendChild(thead);
  t.appendChild(tbody);
  return t;
}

function inLucru(b) {
  const d = el("div", "soonbox");
  d.appendChild(el("b", null, "În lucru"));
  d.appendChild(document.createTextNode(b.continut || ""));
  return d;
}

/* ---------- verificare (quiz) ---------- */

function aplicaRaspuns(box, corect, ales) {
  const optiuni = box.querySelectorAll(".qz__o");
  optiuni.forEach((x) => {
    x.disabled = true;
    const xi = +x.dataset.i;
    if (xi === corect) x.classList.add("ok");
    else if (xi === ales) x.classList.add("no");
  });
  const ex = box.querySelector(".qz__ex");
  ex.classList.add("show");
}

function verificare(b, idSectiune, indice) {
  const idIntrebare = `v${indice}`;
  const box = el("div", "ix");
  box.innerHTML = `
    <div class="ix__head"><span class="ix__kind">VERIFICARE</span></div>
    <div class="ix__body">
      <p class="qz__q">${b.intrebare}</p>
      <div class="qz__opts">
        ${(b.optiuni || []).map((o, i) => `<button class="qz__o" data-i="${i}">${o}</button>`).join("")}
      </div>
      <div class="qz__ex"><b>EXPLICAȚIE</b><span>${b.explicatie || ""}</span></div>
    </div>`;

  const optiuni = box.querySelectorAll(".qz__o");
  optiuni.forEach((o) => o.addEventListener("click", () => {
    const ales = +o.dataset.i;
    const corect = ales === b.corect;
    aplicaRaspuns(box, b.corect, ales);
    progres.salveazaRaspuns(idSectiune, idIntrebare, ales, corect);
  }));

  // Restaurează un răspuns dat anterior (persistă între reîncărcări).
  const salvat = progres.getStare().raspunsuri?.[idSectiune]?.[idIntrebare];
  if (salvat && typeof salvat.raspuns === "number") {
    aplicaRaspuns(box, b.corect, salvat.raspuns);
  }
  return box;
}

/* ---------- interactiv ---------- */

function interactiv(b) {
  const box = el("div", "ix");
  box.innerHTML = `
    <div class="ix__head">
      <span class="ix__kind">${(b.kind || "INTERACTIV").toUpperCase()}</span>
      <span class="ix__title">${b.titlu || ""}</span>
    </div>
    <div class="ix__body">
      ${b.sarcina ? `<p class="ix__task">${b.sarcina}</p>` : ""}
      <div class="ix__mount"></div>
    </div>`;
  const gazda = box.querySelector(".ix__mount");
  const fn = componenta(b.componenta);
  if (fn) {
    try {
      fn(gazda, b.parametri || {});
    } catch (err) {
      console.error(`Componenta „${b.componenta}” a eșuat:`, err);
      gazda.innerHTML = `<p class="ix__task">Componenta „${b.componenta}” nu a putut fi încărcată.</p>`;
    }
  } else {
    gazda.innerHTML = `<p class="ix__task">Componentă necunoscută: „${b.componenta}”.</p>`;
  }
  return box;
}

/* ---------- dispecer ---------- */

export function randeazaBloc(bloc, idSectiune, indice) {
  switch (bloc.tip) {
    case "text":       return text(bloc);
    case "lista":      return lista(bloc);
    case "nota":       return nota(bloc);
    case "cod":        return cod(bloc);
    case "tabel":      return tabel(bloc);
    case "verificare": return verificare(bloc, idSectiune, indice);
    case "interactiv": return interactiv(bloc);
    case "in_lucru":   return inLucru(bloc);
    default:           return el("p", null, `Bloc necunoscut: ${bloc.tip}`);
  }
}

export function randeazaBlocuri(container, blocuri, idSectiune) {
  (blocuri || []).forEach((bloc, i) => {
    container.appendChild(randeazaBloc(bloc, idSectiune, i));
  });
}
