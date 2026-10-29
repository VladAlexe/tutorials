/* ===========================================================================
   ECHIPELE DE PROIECT (db/23-echipe.sql)

   Trei locuri, același modul:
     echipeStudent(gazda)              contul studentului și slide-ul din C2
     echipeProfesor(gazda, { grupa })  pagina „Predau”, fila Echipele
     echipeSlideProfesor(gazda)        slide-ul din C2, pe proiector
     amEchipa()                        antetul: are studentul ceva de făcut?

   Fiecare echipă are o culoare din paletă, după numărul ei, și o păstrează
   peste tot. Echipa e un cartonaș pe care apeși: cinci locuri, care se umplu
   cu inițialele celor care intră, și numele lor dedesubt, mic.

   Ce vede fiecare:
     - studentul vede toate echipele grupei, cu numele membrilor;
     - pe proiector apar toate echipele, câte un pătrat cu numele întregi;
     - profesorul vede totul în pagina lui.

   Pagina se reîmprospătează singură la câteva secunde, cât e vizibilă.
   =========================================================================== */

import { RADACINA } from "./curs.js?v=95";

const esc = s => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/"/g, "&quot;");
const PAS = 3500;

/* culoarea echipei: aceeași ordine peste tot, din paletă */
const CULORI = ["accent", "ambra", "roza", "ardezie", "ceas", "text"];
const culoare = nr => `var(--${CULORI[(nr - 1) % CULORI.length]})`;
const initiale = n => String(n || "?").trim().split(/\s+/).slice(0, 2).map(x => x[0] || "").join("").toUpperCase();

let A = null;
async function auth(){ if (!A) A = await import(`${RADACINA}/js/auth.js?v=95`); return A; }
async function rpc(f, args){
  const { sb } = await auth();
  const r = await sb.rpc(f, args);
  if (r.error){
    const m = r.error.message || "";
    if (/function .* does not exist|could not find the function/i.test(m))
      throw new Error("Baza de date nu are încă echipele: rulează db/23-echipe.sql în Supabase.");
    throw new Error(m);
  }
  return r.data;
}

/* reîmprospătare cât timp gazda e în pagină și fila e vizibilă */
function ceas(gazda, f){
  const t = setInterval(() => {
    if (!gazda.isConnected){ clearInterval(t); return; }
    const a = document.activeElement;
    if (!document.hidden && !(a && gazda.contains(a) && a.tagName === "SELECT")) f();
  }, PAS);
  return () => clearInterval(t);
}

/* numele văzute data trecută, ca doar cele noi să apară animat */
function memorie(){
  let vechi = null;
  return lista => {
    const noi = new Set(vechi ? lista.filter(x => !vechi.has(x)) : []);
    vechi = new Set(lista);
    return noi;
  };
}

/* --------------------------------------------------------------- cartonașul --
   e: { id, nr, membri: [nume] | null, ocupate }. Cu `actiune`, tot cartonașul e
   un buton (de aceea înăuntru sunt doar elemente inline). Culoarea se adună pe
   măsură ce echipa se umple; echipa completă e plină de culoare. */
function cartonas(e, lim, o = {}){
  const membri = e.membri || null;
  const n = membri ? membri.length : (e.ocupate || 0);
  const plina = n >= lim;
  const tenta = 4 + Math.round(14 * Math.min(n, lim) / lim);
  if (o.sloturi) return patrat(e, lim, o, membri, n, plina, tenta);
  const locuri = Array.from({ length: Math.max(lim, n) }, (_, i) => {
    if (i >= n) return "<i></i>";
    const nume = membri && membri[i];
    return `<i class="da${nume && o.noi?.has(nume) ? " nou" : ""}">${nume ? esc(initiale(nume)) : ""}</i>`;
  }).join("");
  const nume = membri && membri.length && o.nume !== false
    ? `<span class="echp__nume">${membri.map(x =>
        `<span class="${o.noi?.has(x) ? "nou" : ""}" title="${esc(x)}">${esc(x)}${o.eu === x ? " <em>tu</em>" : ""}</span>`).join("")}</span>`
    : "";
  const et = plina ? "Completă" : (o.eticheta || "");
  const buton = !!o.actiune && !plina;
  const tag = buton ? "button" : "div";
  const atr = buton
    ? `type="button" data-act="${o.actiune}" data-id="${e.id}" aria-label="${esc(`${o.eticheta}: Echipa ${e.nr}, ${n} din ${lim} locuri ocupate`)}"`
    : "";
  return `<${tag} class="echp__c${plina ? " plina" : ""}${o.a_mea ? " a-mea" : ""}${o.mic ? " mic" : ""}${buton ? " act" : ""}"
      style="--ec:${culoare(e.nr)};--tenta:${tenta}%;--i:${e.nr - 1}" ${atr}>
    <span class="echp__cap"><b>Echipa ${e.nr}</b><small>${n}/${lim}</small></span>
    <span class="echp__loc">${locuri}</span>${nume}${et ? `<span class="echp__et">${et}</span>` : ""}
  </${tag}>`;
}

/* pe slide: un pătrat pentru fiecare echipă, cu un rând pentru fiecare loc. Pe
   rând stă numele întreg al celui care a intrat, ca să se citească din sală;
   locurile goale rămân linii punctate. Înăuntru doar elemente inline, pentru
   că pătratul poate fi buton. */
function patrat(e, lim, o, membri, n, plina, tenta){
  const randuri = Array.from({ length: Math.max(lim, n) }, (_, i) => {
    const nume = membri && membri[i];
    if (i >= n) return `<span class="echp__sl echp__sl--liber"><i>${i + 1}</i><span>loc liber</span></span>`;
    return `<span class="echp__sl${nume && o.noi?.has(nume) ? " nou" : ""}"><i>${i + 1}</i><span title="${esc(nume || "")}">${nume ? esc(nume) : "ocupat"}${o.eu && o.eu === nume ? " <em>tu</em>" : ""}</span></span>`;
  }).join("");
  const buton = !!o.actiune && !plina;
  const tag = buton ? "button" : "div";
  const atr = buton
    ? `type="button" data-act="${o.actiune}" data-id="${e.id}" aria-label="${esc(`${o.eticheta}: Echipa ${e.nr}, ${n} din ${lim} locuri ocupate`)}"`
    : "";
  const et = plina ? "Completă" : (o.eticheta || "");
  return `<${tag} class="echp__c echp__c--sl${plina ? " plina" : ""}${o.a_mea ? " a-mea" : ""}${buton ? " act" : ""}"
      style="--ec:${culoare(e.nr)};--tenta:${tenta}%;--i:${e.nr - 1}" ${atr}>
    <span class="echp__cap"><b>Echipa ${e.nr}</b><small>${n}/${lim}</small></span>
    <span class="echp__sls">${randuri}</span>${et && buton ? `<span class="echp__et">${et}</span>` : ""}
  </${tag}>`;
}

/* banda grupei: câte un segment pentru fiecare student cu echipă, în culoarea
   echipei, pe fondul celor încă fără echipă */
function banda(echipe, total){
  if (!total) return "";
  return `<span class="echp__banda" aria-hidden="true">${echipe.map(e => {
    const n = e.membri ? e.membri.length : e.ocupate;
    return n ? `<i style="--ec:${culoare(e.nr)};flex-grow:${n}"></i>` : "";
  }).join("")}<i class="rest" style="flex-grow:${Math.max(0, total - echipe.reduce((s, e) => s + (e.membri ? e.membri.length : e.ocupate), 0))}"></i></span>`;
}

/* rescrie gazda doar dacă s-a schimbat ceva: fără pâlpâit și fără focus pierdut */
function pune(gazda, h){
  if (gazda._h === h) return false;
  gazda.innerHTML = h; gazda._h = h;
  return true;
}

/* ============================================================== STUDENTUL === */

export async function echipeStudent(gazda, { slide = false } = {}){
  gazda.classList.add("echp");
  if (slide) gazda.classList.add("echp--slide");
  let ocupat = false, msg = "", prima = true;
  const noi = memorie();

  async function actiune(f, args){
    if (ocupat) return;
    ocupat = true; msg = "";
    try {
      const r = await rpc(f, args);
      if (r && r.ok === false) msg = r.mesaj || "Acțiunea nu a reușit.";
    } catch (e){ msg = e.message; }
    finally { ocupat = false; await deseneaza(); }
  }

  async function deseneaza(){
    let d;
    try { d = await rpc("echipele_mele"); }
    catch (e){ pune(gazda, `<p class="echp__gol">${esc(e.message)}</p>`); return; }
    if (!d) d = { ok: false, motiv: "fara_cont" };

    if (!d.ok){
      const t = {
        fara_cont: `Echipa se alege din <a class="leg" href="${RADACINA}/cont/">cont</a>, după autentificarea cu GitHub.`,
        fara_nume: "Echipa se alege după ce contul este asociat numelui tău din lista grupei, la prima oră.",
        fara_grupa: "Numele tău nu este încă asociat unei grupe. Scrie profesorului."
      }[d.motiv] || "Alegerea echipei nu este disponibilă pentru acest cont.";
      pune(gazda, `<p class="echp__gol">${t}</p>`);
      return;
    }
    if (d.stare === "nepornita"){
      pune(gazda, `<p class="echp__gol">Echipele de proiect nu sunt încă deschise.</p>`);
      return;
    }

    const lim = d.limita, deschisa = d.stare === "deschisa";
    const E = d.echipe || [];
    const intra = prima ? " intra" : "";
    let h = "";

    if (d.echipa){
      /* ai echipă: a ta sus, celelalte dedesubt, toate cu numele */
      const mea = d.echipa;
      const nou = noi(mea.membri.map(m => m.nume));
      const eu = mea.membri.find(m => m.eu)?.nume;
      h += `<div class="echp__a-mea${intra}">${cartonas({ ...mea, membri: mea.membri.map(m => m.nume) }, lim, { a_mea: true, noi: nou, eu })}
        <div class="echp__lat">
          <p class="echp__lead">Ești în <b style="color:${culoare(mea.nr)}">Echipa ${mea.nr}</b>.</p>
          ${(d.cereri_primite || []).length ? `<div class="echp__cereri">${d.cereri_primite.map(c => `<div class="echp__cerere">
              <span><b>${esc(c.nume)}</b> cere să intre în echipă.</span>
              <button class="btn btn--mic btn--tare" type="button" data-r="${c.id}" data-a="1">Acceptă</button>
              <button class="btn btn--mic" type="button" data-r="${c.id}" data-a="0">Refuză</button></div>`).join("")}
            <p class="echp__info">Răspunde oricare membru al echipei.</p></div>` : ""}
          ${deschisa ? `<p class="echp__info">Alegerea este încă deschisă. Te poți muta într-o echipă cu locuri libere.</p>`
                     : `<p class="echp__info">Echipele sunt închise. Pentru o schimbare, scrie profesorului.</p>`}
        </div></div>`;
      if (deschisa){
        const alte = E.filter(e => !e.a_mea);
        h += `<p class="echp__et2">Celelalte echipe</p>
          <div class="echp__grila echp__grila--mic${intra}">${alte.map(e => cartonas(e, lim, { actiune: "muta", eticheta: "Mută-mă aici", mic: true })).join("")}</div>
          <button class="btn btn--mic echp__iesi" type="button" data-iesi="1">Ies din echipă</button>`;
      }
    } else {
      /* fără echipă: vezi toate echipele, cu numele, și alegi */
      const nou = noi(E.flatMap(e => e.membri || []));
      if (deschisa){
        h += `<p class="echp__lead">Apasă pe echipa în care vrei să intri. Te poți muta până când profesorul închide alegerea.</p>`;
      } else if (d.cerere){
        h += `<div class="echp__cererea" style="--ec:${culoare(d.cerere.nr)}"><p class="echp__lead">Ai cerut să intri în <b>Echipa ${d.cerere.nr}</b>.
          Un membru al echipei acceptă sau refuză cererea.</p>
          <button class="btn btn--mic" type="button" data-anuleaza="1">Anulează cererea</button></div>`;
      } else {
        h += `<p class="echp__lead">Alegerea liberă s-a încheiat. Apasă pe o echipă cu locuri libere pentru a cere să intri; un membru al echipei acceptă cererea.</p>`;
        if (d.refuzata) h += `<p class="echp__info">Cererea pentru Echipa ${d.refuzata.nr} a fost refuzată. Poți cere altei echipe.</p>`;
      }
      const act = d.cerere ? null : (deschisa ? "intra" : "cere");
      h += `<div class="echp__grila${slide ? " echp__grila--sl" : ""}${intra}">${E.map(e => cartonas(e, lim, {
               actiune: act, noi: nou, a_mea: d.cerere && d.cerere.nr === e.nr, sloturi: slide,
               eticheta: d.cerere ? (d.cerere.nr === e.nr ? "Cerere trimisă" : "") : deschisa ? "Intru aici" : "Cer să intru" })).join("")}</div>`;
      if (d.toate_pline && !d.cerere){
        h += `<div class="echp__noua"><p>Toate echipele sunt complete.</p>
          <button class="btn btn--mic btn--tare" type="button" data-noua="1">Deschid o echipă nouă</button></div>`;
      }
    }
    if (msg) h += `<p class="echp__msg">${esc(msg)}</p>`;
    if (!slide) h += `<p class="echp__gdpr">Echipele și numele membrilor sunt vizibile pentru studenții grupei. Numărul matricol și contul GitHub nu apar.</p>`;
    prima = false;
    if (!pune(gazda, h)) return;

    gazda.querySelectorAll("[data-act]").forEach(b => b.onclick = () => {
      const id = +b.dataset.id;
      actiune(b.dataset.act === "cere" ? "cere_echipa" : "alege_echipa", { p_echipa: id });
    });
    gazda.querySelectorAll("[data-r]").forEach(b => b.onclick = () =>
      actiune("raspunde_cererii", { p_cerere: +b.dataset.r, p_accept: b.dataset.a === "1" }));
    gazda.querySelector("[data-iesi]")?.addEventListener("click", () => actiune("paraseste_echipa", {}));
    gazda.querySelector("[data-anuleaza]")?.addEventListener("click", () => actiune("anuleaza_cererea", {}));
    gazda.querySelector("[data-noua]")?.addEventListener("click", () => actiune("echipa_noua", {}));
  }

  await deseneaza();
  ceas(gazda, deseneaza);
}

/* ============================================================== PROFESORUL === */

export async function echipeProfesor(gazda, { grupa, numeGrupa = "" } = {}){
  gazda.classList.add("echp", "echp--prof");
  if (!grupa){ pune(gazda, `<p class="echp__gol">Alege mai întâi o grupă.</p>`); return () => {}; }
  let ocupat = false, msg = "", d = null;
  const noi = memorie();

  async function actiune(f, args){
    if (ocupat) return;
    ocupat = true; msg = "";
    try {
      const r = await rpc(f, args);
      if (r && r.ok === false) msg = r.mesaj || "Acțiunea nu a reușit.";
    } catch (e){ msg = e.message; }
    finally { ocupat = false; await deseneaza(); }
  }

  async function deseneaza(){
    try { d = await rpc("echipe_toate", { p_grupa: grupa }); }
    catch (e){ pune(gazda, `<p class="echp__gol">${esc(e.message)}</p>`); return; }
    if (!d || !d.ok){ pune(gazda, `<p class="echp__gol">${esc(d?.mesaj || "Echipele nu pot fi citite.")}</p>`); return; }

    if (d.stare === "nepornita"){
      const sugerat = Math.max(1, Math.ceil((d.studenti || 0) / (d.limita || 5)));
      if (!pune(gazda, `<div class="echp__porneste">
        <p class="echp__lead">Alegerea echipelor nu a pornit pentru ${esc(numeGrupa || "această grupă")}: ${d.studenti} studenți în listă.</p>
        <label>Echipe <input type="number" min="1" max="40" value="${sugerat}" id="echp-n"></label>
        <label>Membri pe echipă <input type="number" min="2" max="10" value="${d.limita || 5}" id="echp-l"></label>
        <button class="btn btn--tare" type="button" id="echp-start">Pornește alegerea</button>
        <p class="echp__info">Studenții își aleg echipa din cont sau de pe slide-ul din cursul 2, cât timp alegerea este deschisă.</p>
        ${msg ? `<p class="echp__msg">${esc(msg)}</p>` : ""}</div>`)) return;
      gazda.querySelector("#echp-start").onclick = () => actiune("echipe_porneste", {
        p_grupa: grupa, p_numar: +gazda.querySelector("#echp-n").value || sugerat, p_limita: +gazda.querySelector("#echp-l").value || 5 });
      return;
    }

    const deschisa = d.stare === "deschisa", lim = d.limita;
    const nou = noi(d.echipe.flatMap(e => e.membri.map(m => m.nume)));
    const opt = sel => `<option value="">fără echipă</option>` +
      d.echipe.map(e => `<option value="${e.id}" ${e.id === sel ? "selected" : ""}>Echipa ${e.nr}</option>`).join("");
    const cuEchipa = d.echipe.reduce((s, e) => s + e.membri.length, 0);

    const h = `
      <div class="echp__bara">
        <span class="echp__stare ${deschisa ? "on" : ""}">${deschisa ? "Alegere deschisă" : "Alegere închisă"}</span>
        <span class="echp__info">${d.echipe.length} echipe · ${cuEchipa} din ${d.studenti} studenți au o echipă</span>
        <span class="sp"></span>
        <button class="btn btn--mic" type="button" id="echp-st">${deschisa ? "Închide alegerea" : "Redeschide alegerea"}</button>
        <button class="btn btn--mic" type="button" id="echp-add">Adaugă o echipă</button>
        <button class="btn btn--mic" type="button" id="echp-csv">Export CSV</button>
      </div>
      ${banda(d.echipe, d.studenti)}
      ${msg ? `<p class="echp__msg">${esc(msg)}</p>` : ""}
      ${d.cereri.length ? `<div class="echp__cereri"><p class="echp__et2">Cereri în așteptare</p>
        ${d.cereri.map(c => `<div class="echp__cerere" style="--ec:${culoare(c.nr)}"><span><b>${esc(c.nume)}</b> cere să intre în
          <b class="echp__ec">Echipa ${c.nr}</b>.</span>
          <button class="btn btn--mic btn--tare" type="button" data-r="${c.id}" data-a="1">Acceptă</button>
          <button class="btn btn--mic" type="button" data-r="${c.id}" data-a="0">Refuză</button></div>`).join("")}</div>` : ""}
      <div class="echp__grila echp__grila--prof">${d.echipe.map(e => {
        const n = e.membri.length;
        return `<div class="echp__c" style="--ec:${culoare(e.nr)};--tenta:${4 + Math.round(10 * Math.min(n, lim) / lim)}%">
          <span class="echp__cap"><b>Echipa ${e.nr}</b><small>${n}/${lim}</small></span>
          <span class="echp__loc">${Array.from({ length: Math.max(lim, n) }, (_, i) => i < n
            ? `<i class="da${nou.has(e.membri[i].nume) ? " nou" : ""}">${esc(initiale(e.membri[i].nume))}</i>` : "<i></i>").join("")}</span>
          ${n ? `<ul class="echp__lista">${e.membri.map(m => `<li><span title="${esc(m.nume)}">${esc(m.nume)}${m.github ? ` <small>@${esc(m.github)}</small>` : ""}</span>
            <select data-m="${esc(m.matricol)}" aria-label="Mută ${esc(m.nume)}">${opt(e.id)}</select></li>`).join("")}</ul>` : ""}
        </div>`; }).join("")}</div>
      ${d.fara_echipa.length ? `<div class="echp__fara"><p class="echp__et2">Fără echipă (${d.fara_echipa.length})</p>
        <ul class="echp__lista">${d.fara_echipa.map(s => `<li><span>${esc(s.nume)}${s.cont ? "" : ` <small>fără cont</small>`}</span>
          <select data-m="${esc(s.matricol)}" aria-label="Pune ${esc(s.nume)} într-o echipă">${opt(null)}</select></li>`).join("")}</ul></div>` : ""}`;
    if (!pune(gazda, h)) return;

    gazda.querySelector("#echp-st").onclick = () => actiune("echipe_stare", { p_grupa: grupa, p_stare: d.stare === "deschisa" ? "inchisa" : "deschisa" });
    gazda.querySelector("#echp-add").onclick = () => actiune("echipe_adauga", { p_grupa: grupa });
    gazda.querySelector("#echp-csv").onclick = () => csv(d);
    gazda.querySelectorAll("[data-r]").forEach(b => b.onclick = () =>
      actiune("raspunde_cererii", { p_cerere: +b.dataset.r, p_accept: b.dataset.a === "1" }));
    gazda.querySelectorAll("select[data-m]").forEach(s => s.onchange = () =>
      actiune("echipe_pune", { p_matricol: s.dataset.m, p_echipa: s.value ? +s.value : null }));
  }

  function csv(d){
    const r = [["echipa", "nume", "github"]];
    d.echipe.forEach(e => e.membri.forEach(m => r.push([`echipa-${e.nr}`, m.nume, m.github || ""])));
    const t = r.map(x => x.map(v => `"${String(v).replace(/"/g, '""')}"`).join(",")).join("\n");
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob(["﻿" + t], { type: "text/csv;charset=utf-8" }));
    a.download = `echipe-${grupa}.csv`;
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 2000);
  }

  await deseneaza();
  return ceas(gazda, deseneaza);
}

/* =================================================== PROFESORUL, PE SLIDE === */
/* Pe proiector: cartonașele echipelor, cu numele care apar pe măsură ce
   intră studenții; plus pornirea, închiderea și redeschiderea alegerii. */

export async function echipeSlideProfesor(gazda){
  gazda.classList.add("echp", "echp--slide");
  const O = await import(`${RADACINA}/js/ora.js?v=95`);
  const S = await O.deschisa().catch(() => null);
  let grupa = S?.grupa_id || null;
  if (!grupa){
    const gr = (await O.grupe()).filter(g => g.activa !== false);
    grupa = gr[0]?.id || null;
  }
  if (!grupa){ pune(gazda, `<p class="echp__gol">Nu există nicio grupă activă.</p>`); return; }
  const noi = memorie();
  let msg = "", prima = true;

  async function actiune(f, args){
    msg = "";
    try {
      const r = await rpc(f, args);
      if (r && r.ok === false) msg = r.mesaj || "Acțiunea nu a reușit.";
    } catch (e){ msg = e.message; }
    await deseneaza();
  }

  async function deseneaza(){
    let d;
    try { d = await rpc("echipe_toate", { p_grupa: grupa }); }
    catch (e){ pune(gazda, `<p class="echp__gol">${esc(e.message)}</p>`); return; }
    if (!d || !d.ok){ pune(gazda, `<p class="echp__gol">${esc(d?.mesaj || "Echipele nu pot fi citite.")}</p>`); return; }
    const m = msg ? `<p class="echp__msg">${esc(msg)}</p>` : "";
    if (d.stare === "nepornita"){
      const n = Math.max(1, Math.ceil((d.studenti || 0) / (d.limita || 5)));
      if (!pune(gazda, `<p class="echp__lead">${d.studenti} studenți: ${n} echipe de cel mult ${d.limita} membri.</p>
        <button class="btn btn--tare" type="button" id="echp-start">Pornește alegerea echipelor</button>${m}`)) return;
      gazda.querySelector("#echp-start").onclick = () =>
        actiune("echipe_porneste", { p_grupa: grupa, p_numar: n, p_limita: d.limita || 5 });
      return;
    }
    const deschisa = d.stare === "deschisa";
    const E = d.echipe.map(e => ({ id: e.id, nr: e.nr, ocupate: e.membri.length,
                                   membri: e.membri.map(x => x.nume) }));
    const nou = noi(E.flatMap(e => e.membri || []));
    const ocupate = E.reduce((s, e) => s + e.ocupate, 0);
    const h = `<div class="echp__grila echp__grila--sl${prima ? " intra" : ""}">${E.map(e => cartonas(e, d.limita, { noi: nou, sloturi: true })).join("")}</div>
      <div class="echp__bara">
        <span class="echp__stare ${deschisa ? "on" : ""}">${deschisa ? "Alegere deschisă" : "Alegere închisă"}</span>
        <span class="echp__info">${ocupate} din ${d.studenti} studenți au o echipă</span>
        ${banda(E, d.studenti)}
        <button class="btn btn--mic" type="button" id="echp-st">${deschisa ? "Închide alegerea" : "Redeschide alegerea"}</button>
      </div>${m}`;
    prima = false;
    if (!pune(gazda, h)) return;
    gazda.querySelector("#echp-st").onclick = () =>
      actiune("echipe_stare", { p_grupa: grupa, p_stare: deschisa ? "inchisa" : "deschisa" });
  }
  await deseneaza();
  ceas(gazda, deseneaza);
}

/* ================================================================ ANTETUL === */

export async function amEchipa(){
  try { return await rpc("am_echipa"); } catch { return null; }
}
