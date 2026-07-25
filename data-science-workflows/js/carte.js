/* carte.js — încărcare, rutare cu ancoră (#/cap-1/1.3), randarea secțiunii și
   a cuprinsului lateral. Cuprinsul se desenează NUMAI din manifest; fișierul
   fiecărui capitol se încarcă la cerere, când intri în el. */

import { randeazaBlocuri } from "./blocuri.js";
import * as progres from "./progres.js";

const BAZA = "continut";
let manifest = null;
let plat = [];                 // listă plată de secțiuni (din manifest, ușoară)
const cacheCapitole = new Map();  // fisier -> conținut complet încărcat

/* ---------- încărcare ---------- */

async function incarcaManifest() {
  const r = await fetch(`${BAZA}/carte.json`);
  if (!r.ok) throw new Error("Nu am putut încărca manifestul cărții.");
  return r.json();
}

async function incarcaCapitol(fisier) {
  if (cacheCapitole.has(fisier)) return cacheCapitole.get(fisier);
  const r = await fetch(`${BAZA}/${fisier}`);
  if (!r.ok) throw new Error(`Nu am putut încărca „${fisier}”.`);
  const date = await r.json();
  cacheCapitole.set(fisier, date);
  return date;
}

/** Listă plată a secțiunilor, doar din manifest (pentru cuprins, prev/next). */
function construiestePlat() {
  plat = [];
  manifest.capitole.forEach((cap) => {
    cap.sectiuni.forEach((s) => {
      plat.push({
        capNumar: cap.numar,
        capTitlu: cap.titlu,
        capFisier: cap.fisier,
        parte: cap.parte,
        secId: s.id,
        secTitlu: s.titlu,
        secStare: s.stare
      });
    });
  });
}

/* ---------- rutare ---------- */

function parseazaHash() {
  const m = /^#\/cap-(\d+)\/([\d.]+)$/.exec(location.hash);
  if (!m) return null;
  return { capNumar: +m[1], secId: m[2] };
}

function ancora(capNumar, secId) {
  return `#/cap-${capNumar}/${secId}`;
}

function naviga(capNumar, secId) {
  const nou = ancora(capNumar, secId);
  if (location.hash === nou) render();      // aceeași ancoră: re-randăm manual
  else location.hash = nou;                 // altfel, hashchange declanșează render
}

/* ---------- cuprinsul lateral (din manifest) ---------- */

function cuprins(curentCap, curentSec) {
  const stare = progres.getStare();
  const vizitate = stare.vizitate || {};
  const gazda = document.getElementById("toc");
  let html = "";
  let ultimaParte = "";

  manifest.capitole.forEach((cap) => {
    if (cap.parte !== ultimaParte) {
      html += `<div class="part">${cap.parte}</div>`;
      ultimaParte = cap.parte;
    }
    const deschis = cap.numar === curentCap;
    const totVazut = cap.sectiuni.every((s) => vizitate[s.id]);
    const eticheta = cap.numar === 0 ? "·" : cap.numar;

    html += `
      <div class="ch ${deschis ? "is-open" : ""} ${totVazut ? "is-done" : ""}">
        <div class="ch__line"></div>
        <button class="ch__btn" data-cap="${cap.numar}" data-sec="${cap.sectiuni[0].id}">
          <span class="dot">${eticheta}</span>
          <span class="ch__name">${cap.titlu}</span>
        </button>
        <div class="secs">
          ${cap.sectiuni.map((s) => `
            <button class="sec ${s.stare === "schita" ? "soon" : ""}
                    ${deschis && s.id === curentSec ? "is-current" : ""}
                    ${vizitate[s.id] ? "is-seen" : ""}"
                    data-cap="${cap.numar}" data-sec="${s.id}">
              ${cap.numar === 0 ? "" : s.id + " &nbsp;"}${s.titlu}
            </button>`).join("")}
        </div>
      </div>`;
  });

  gazda.innerHTML = html;
  gazda.querySelectorAll(".ch__btn, .sec").forEach((b) => {
    b.addEventListener("click", () => {
      naviga(+b.dataset.cap, b.dataset.sec);
      document.body.classList.remove("menu");
    });
  });
}

function actualizeazaProgres() {
  const p = progres.getProcentGeneral();
  document.getElementById("progbar").style.width = p + "%";
  document.getElementById("progpct").textContent = p + "%";
}

/* ---------- navigarea de jos (prev / next) ---------- */

function navigareJos(pozitie) {
  const p = plat[pozitie - 1];
  const n = plat[pozitie + 1];
  const nav = document.createElement("div");
  nav.className = "nav";
  nav.innerHTML = `
    ${p ? `<a class="nav__b" href="${ancora(p.capNumar, p.secId)}"><small>ÎNAPOI</small>${p.secTitlu}</a>` : "<span></span>"}
    ${n ? `<a class="nav__b nav__b--next" href="${ancora(n.capNumar, n.secId)}"><small>CONTINUĂ</small>${n.secTitlu}</a>` : "<span></span>"}`;
  return nav;
}

/* ---------- randarea unei secțiuni ---------- */

async function render() {
  let ruta = parseazaHash();
  if (!ruta) ruta = { capNumar: 0, secId: plat[0].secId };  // fără ancoră -> introducere

  const pozitie = plat.findIndex((x) => x.capNumar === ruta.capNumar && x.secId === ruta.secId);
  if (pozitie === -1) { naviga(0, plat[0].secId); return; }

  const meta = plat[pozitie];
  const main = document.getElementById("main");

  let capitol;
  try {
    capitol = await incarcaCapitol(meta.capFisier);
  } catch (err) {
    console.error(err);
    main.innerHTML = `<p>${err.message}</p>`;
    return;
  }
  const sectiune = capitol.sectiuni.find((s) => s.id === meta.secId);
  if (!sectiune) { main.innerHTML = `<p>Secțiunea „${meta.secId}” nu a fost găsită.</p>`; return; }

  // Firimitura din bara de sus
  document.getElementById("crumb").textContent =
    meta.capNumar === 0 ? meta.capTitlu : `${meta.capNumar}. ${meta.capTitlu}`;
  document.title = `${sectiune.titlu} — ${manifest.titlu}`;

  // Corpul secțiunii
  main.innerHTML = "";
  const eyebrow = document.createElement("p");
  eyebrow.className = "eyebrow";
  eyebrow.textContent = meta.capNumar === 0
    ? "INTRODUCERE"
    : `CAPITOLUL ${meta.capNumar} · SECȚIUNEA ${sectiune.id}`;
  main.appendChild(eyebrow);

  const h1 = document.createElement("h1");
  h1.textContent = sectiune.titlu;
  h1.tabIndex = -1;
  main.appendChild(h1);

  if (sectiune.rezumat) {
    const deck = document.createElement("p");
    deck.className = "deck";
    deck.textContent = sectiune.rezumat;
    main.appendChild(deck);
  }

  const areBlocuri = Array.isArray(sectiune.blocuri) && sectiune.blocuri.length > 0;
  if (sectiune.stare === "schita" && !areBlocuri) {
    const box = document.createElement("div");
    box.className = "soonbox";
    box.innerHTML = `<b>Secțiune în lucru</b>Structura e fixată, conținutul se scrie după ce alegem sursele de date.`;
    main.appendChild(box);
  } else {
    randeazaBlocuri(main, sectiune.blocuri, sectiune.id);
  }

  main.appendChild(navigareJos(pozitie));

  // Progres + cuprins + focus
  progres.marcheazaVizitata(sectiune.id);
  cuprins(meta.capNumar, meta.secId);
  actualizeazaProgres();
  window.scrollTo({ top: 0, behavior: "instant" });
  h1.focus({ preventScroll: true });
}

/* ---------- pornire ---------- */

async function porneste() {
  manifest = await incarcaManifest();
  construiestePlat();

  // Total = secțiunile numărate (capitolele 1–8), fără introducere.
  const total = plat.filter((x) => x.capNumar >= 1).length;
  progres.init({ total });

  // Antetul cuprinsului din manifest
  document.getElementById("spine-title").textContent = manifest.titlu;
  if (manifest.sigla) {
    document.getElementById("mark-t").textContent = manifest.sigla.text || "";
    document.getElementById("mark-s").textContent = manifest.sigla.subtext || "";
  }

  // Interfața se reîmprospătează când se schimbă progresul (ex. din altă filă)
  progres.onSchimbare(() => actualizeazaProgres());

  // Rutare
  window.addEventListener("hashchange", render);

  // Meniu mobil
  document.getElementById("burger").addEventListener("click",
    () => document.body.classList.toggle("menu"));
  document.getElementById("scrim").addEventListener("click",
    () => document.body.classList.remove("menu"));

  // Săgeți pe calculator
  document.addEventListener("keydown", (e) => {
    if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") return;
    const ruta = parseazaHash() || { capNumar: 0, secId: plat[0].secId };
    const poz = plat.findIndex((x) => x.capNumar === ruta.capNumar && x.secId === ruta.secId);
    if (e.key === "ArrowRight" && plat[poz + 1]) naviga(plat[poz + 1].capNumar, plat[poz + 1].secId);
    if (e.key === "ArrowLeft" && plat[poz - 1]) naviga(plat[poz - 1].capNumar, plat[poz - 1].secId);
  });

  render();
}

porneste().catch((err) => {
  console.error(err);
  document.getElementById("main").innerHTML = `<p>${err.message}</p>`;
});
