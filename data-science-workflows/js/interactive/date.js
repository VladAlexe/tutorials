/* date.js — încărcător pentru datele locale ale componentelor.
   Toate componentele capitolului 2 rulează pe fișiere din continut/date/.
   Nu există niciun apel către API-uri externe; singurul fetch este către
   fișierele proprii ale cursului, la fel ca încărcarea capitolelor.

   Calea se rezolvă relativ la pagina (carte.html), deci „continut/date/…”. */

const cache = new Map();

export async function incarcaDate(sursa) {
  if (!sursa) return null;
  if (cache.has(sursa)) return cache.get(sursa);
  const r = await fetch(`continut/date/${sursa}`);
  if (!r.ok) throw new Error(`Nu am putut încărca datele „${sursa}”.`);
  const d = await r.json();
  cache.set(sursa, d);
  return d;
}

/** Ajutor comun de escape pentru text pus în HTML. */
export function esc(s) {
  return String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
