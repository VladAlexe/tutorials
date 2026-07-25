/* wb.js — ajutoare comune pentru forma răspunsului Băncii Mondiale, construite
   din eșantionul local wb-data.json. Folosit de constructor, paginare și
   json_tabel. Nu face niciun apel de rețea. */

import { esc } from "./date.js";

/** Rândurile de date pentru țările și anii aleși (include valorile null). */
export function construiesteRanduri(data, tari, indicator, aniAlesi) {
  const indNume = (data.indicatori.find((i) => i.cod === indicator) || {}).nume || indicator;
  const rows = [];
  tari.forEach((cod) => {
    const tara = data.tari.find((t) => t.cod === cod);
    if (!tara) return;
    aniAlesi.forEach((an) => {
      const v = (data.valori[`${cod}|${indicator}`] || {})[an];
      rows.push({
        indicator: { id: indicator, value: indNume },
        country: { id: tara.cod.toUpperCase(), value: tara.nume },
        countryiso3code: tara.iso3,
        date: an,
        value: v === undefined ? null : v,
        unit: "",
        obs_status: "",
        decimal: 0
      });
    });
  });
  return rows;
}

/** Împachetează rândurile în răspunsul cu două elemente: [paginare, date]. */
export function raspuns(rows, page, perPage) {
  const total = rows.length;
  const pages = Math.max(1, Math.ceil(total / perPage));
  const p = Math.min(Math.max(1, page), pages);
  const start = (p - 1) * perPage;
  const felie = rows.slice(start, start + perPage);
  return [{ page: p, pages, per_page: perPage, total }, felie];
}

/** Lista anilor din interval [de, la], crescător, ca text. */
export function intervalAni(toti, de, la) {
  const a = Math.min(+de, +la), b = Math.max(+de, +la);
  return toti.filter((an) => +an >= a && +an <= b);
}

/** Segmentele adresei, colorate și etichetate. Pentru `format` json/absent. */
export function segmenteUrl(baza, tari, indicator, de, la, perPage, jsonFormat) {
  const host = baza.replace(/^https?:\/\//, "").split("/")[0];
  const segmente = [
    { t: "proto", text: "https", nume: "Protocol", rol: "HTTP securizat." },
    { t: "sep", text: "://" },
    { t: "host", text: host, nume: "Gazdă", rol: "Serverul API al Băncii Mondiale." },
    { t: "path", text: "/v2", nume: "Versiune", rol: "Versiunea 2 a API-ului. Contează: o versiune nouă poate schimba forma răspunsului." },
    { t: "path", text: `/country/${tari.join(";")}`, nume: "Țări", rol: "Una sau mai multe țări, separate prin punct și virgulă." },
    { t: "path", text: `/indicator/${indicator}`, nume: "Indicator", rol: "Codul indicatorului cerut." },
    { t: "sep", text: "?" }
  ];
  const q = [];
  if (jsonFormat) q.push({ t: "query", text: "format=json", nume: "format", rol: "Cere JSON. FĂRĂ el, răspunsul vine în XML — implicit." });
  const deLa = (+de === +la) ? `${de}` : `${Math.min(+de, +la)}:${Math.max(+de, +la)}`;
  q.push({ t: "query", text: `date=${deLa}`, nume: "date", rol: "Anul sau intervalul de ani." });
  q.push({ t: "query", text: `per_page=${perPage}`, nume: "per_page", rol: "Câte rezultate pe pagină. Implicit 50 la acest API." });
  q.forEach((seg, i) => {
    if (i > 0) segmente.push({ t: "sep", text: "&" });
    segmente.push(seg);
  });
  return segmente;
}

export function urlText(segmente) {
  return segmente.map((s) => s.text).join("");
}

/* ---------- colorare JSON ---------- */
export function coloreazaJson(v, indent = 0) {
  const pad = "  ".repeat(indent);
  if (v === null) return `<span class="jb">null</span>`;
  if (typeof v === "number") return `<span class="jn">${v}</span>`;
  if (typeof v === "boolean") return `<span class="jb">${v}</span>`;
  if (typeof v === "string") return `<span class="js">"${esc(v)}"</span>`;
  if (Array.isArray(v)) {
    if (v.length === 0) return `<span class="jp">[]</span>`;
    const inner = v.map((x) => `${pad}  ${coloreazaJson(x, indent + 1)}`).join(`<span class="jp">,</span>\n`);
    return `<span class="jp">[</span>\n${inner}\n${pad}<span class="jp">]</span>`;
  }
  const keys = Object.keys(v);
  if (keys.length === 0) return `<span class="jp">{}</span>`;
  const inner = keys.map((k) =>
    `${pad}  <span class="jk">"${esc(k)}"</span><span class="jp">: </span>${coloreazaJson(v[k], indent + 1)}`
  ).join(`<span class="jp">,</span>\n`);
  return `<span class="jp">{</span>\n${inner}\n${pad}<span class="jp">}</span>`;
}

/* ---------- forma XML (implicită fără format=json) ---------- */
export function formaXml(resp) {
  const [pag, date] = resp;
  const rows = (date || []).map((r) => `  <wb:data>
    <wb:indicator id="${esc(r.indicator.id)}">${esc(r.indicator.value)}</wb:indicator>
    <wb:country id="${esc(r.country.id)}">${esc(r.country.value)}</wb:country>
    <wb:countryiso3code>${esc(r.countryiso3code)}</wb:countryiso3code>
    <wb:date>${esc(r.date)}</wb:date>
    <wb:value>${r.value === null ? "" : r.value}</wb:value>
  </wb:data>`).join("\n");
  return `<span class="c">&lt;?xml version="1.0" encoding="utf-8"?&gt;</span>
&lt;wb:data page="${pag.page}" pages="${pag.pages}" per_page="${pag.per_page}" total="${pag.total}"&gt;
${rows}
&lt;/wb:data&gt;`;
}
