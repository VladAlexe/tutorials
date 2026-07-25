/* json.js — arbore pliabil peste un răspuns real de API, cu evidențiere pe
   tipuri. La alegerea unui rând se afișează tipul, calea de acces și o explicație.
   Datele exemplu vin din `parametri.date`; explicațiile de tip sunt generice. */

const DESCRIERI = {
  "tablou": "Listă ordonată. Accesezi elementele după poziție, începând de la 0.",
  "obiect": "Perechi cheie–valoare. În Python devine dicționar; accesezi după cheie.",
  "text": "Șir de caractere. Chiar dacă arată ca un an, rămâne text până îl converteșt tu.",
  "număr": "Valoare numerică. Poate fi întreg sau cu zecimale.",
  "null": "Valoarea lipsește explicit. În pandas devine NaN, nu zero.",
  "boolean": "Adevărat sau fals."
};

function esc(s) {
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;");
}

function tipul(v) {
  if (v === null) return "null";
  if (Array.isArray(v)) return "tablou";
  if (typeof v === "object") return "obiect";
  if (typeof v === "number") return "număr";
  if (typeof v === "boolean") return "boolean";
  return "text";
}

export default function jsonTree(gazda, parametri = {}) {
  const date = parametri.date ?? [];
  const radacina = parametri.eticheta_radacina || "raspuns";
  const randuri = [];

  function parcurge(v, cheie, adancime, cale) {
    const ind = "  ".repeat(adancime);
    const k = cheie !== null
      ? `<span class="jk">"${esc(cheie)}"</span><span class="jp">: </span>` : "";

    if (Array.isArray(v)) {
      randuri.push({ selectabil: true, cale, kind: "tablou", n: v.length,
        html: `${ind}<span class="jtog">▾</span>${k}<span class="jp">[</span>` });
      v.forEach((x, i) => parcurge(x, null, adancime + 1, `${cale}[${i}]`));
      randuri.push({ selectabil: false, html: `${ind}   <span class="jp">]</span>` });
    } else if (v && typeof v === "object") {
      randuri.push({ selectabil: true, cale, kind: "obiect", n: Object.keys(v).length,
        html: `${ind}<span class="jtog">▾</span>${k}<span class="jp">{</span>` });
      Object.entries(v).forEach(([kk, vv]) => parcurge(vv, kk, adancime + 1, `${cale}["${kk}"]`));
      randuri.push({ selectabil: false, html: `${ind}   <span class="jp">}</span>` });
    } else {
      const kind = tipul(v);
      const disp = v === null ? `<span class="jb">null</span>`
        : typeof v === "string" ? `<span class="js">"${esc(v)}"</span>`
        : `<span class="jn">${esc(v)}</span>`;
      randuri.push({ selectabil: true, cale, kind, html: `${ind}   ${k}${disp}` });
    }
  }
  parcurge(date, null, 0, radacina);

  gazda.innerHTML = `
    <div class="jsn">${randuri.map((r, i) => r.selectabil
      ? `<button type="button" class="jrow" data-r="${i}">${r.html}</button>`
      : `<span class="jrow static">${r.html}</span>`).join("")}</div>
    <p class="jsn__out" id="jout" role="status" aria-live="polite">Apasă pe orice rând din arbore.</p>`;

  const out = gazda.querySelector("#jout");
  gazda.querySelectorAll("button.jrow").forEach((rw) => {
    rw.addEventListener("click", () => {
      const r = randuri[+rw.dataset.r];
      gazda.querySelectorAll(".jrow").forEach((x) => x.classList.remove("sel"));
      rw.classList.add("sel");
      const extra = r.n !== undefined
        ? ` cu ${r.n} ${r.kind === "tablou" ? "elemente" : "chei"}` : "";
      out.innerHTML =
        `<span class="pill">${r.kind.toUpperCase()}</span><b>${esc(r.cale)}</b>${extra}<br>${DESCRIERI[r.kind]}`;
    });
  });
}
