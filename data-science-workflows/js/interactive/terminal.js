/* terminal.js — terminal simulat pentru mediul virtual. Recunoaște crearea
   mediului, activarea, instalarea, listarea, dezactivarea, plus `ajutor` și
   `curata`. Respectă ORDINEA: instalarea fără mediu activ avertizează că
   pachetul ajunge în Python-ul global; activarea fără mediu creat dă eroare.
   Lista de sarcini de deasupra se bifează pe măsură ce comenzile reușesc.
   Numele dosarului și etichetele sarcinilor vin din `parametri`. */

export default function terminal(gazda, parametri = {}) {
  const dosar = parametri.dosar || "proiect-dsw";
  const sarcini = parametri.sarcini || [];
  const P = `C:\\${dosar}`;      // calea afișată în prompt

  let activ = false;
  let instalate = [];
  const facute = new Set();
  let linii = [
    "Windows PowerShell",
    "Copyright (c) Microsoft Corporation",
    "",
    `PS ${P}> _`
  ];

  function render() {
    gazda.querySelector("#trm").innerHTML = linii.map((l) =>
      l.startsWith("!") ? `<div class="er">${l.slice(1)}</div>` : `<div>${l}</div>`).join("");
    const trm = gazda.querySelector("#trm");
    trm.scrollTop = trm.scrollHeight;
    gazda.querySelectorAll(".tchip").forEach((c, i) => c.classList.toggle("done", facute.has(i)));
    gazda.querySelector("#prompt").textContent = (activ ? "(venv) " : "") + `PS ${P}>`;
  }

  function spune(cmd, iesire) {
    linii.splice(linii.length - 1, 1);   // scoate cursorul „_”
    linii.push(`<span class="pr">${activ ? "(venv) " : ""}PS ${P}&gt;</span> ${cmd}`);
    iesire.forEach((o) => linii.push(o));
    linii.push("");
    linii.push("_");
  }

  function ruleaza(brut) {
    const c = brut.trim();
    if (!c) return;

    if (/^python -m venv/.test(c)) {
      facute.add(0);
      spune(c, ["", "Se creează mediul virtual în .\\venv ...", "Gata."]);
    } else if (/activate$/.test(c) && !/deactivate/.test(c)) {
      if (!facute.has(0)) {
        spune(c, ["!Nu există folderul venv. Creează întâi mediul."]);
      } else {
        activ = true; facute.add(1); spune(c, [""]);
      }
    } else if (/^deactivate/.test(c)) {
      if (!activ) spune(c, ["!Niciun mediu activ."]);
      else { activ = false; facute.add(4); spune(c, [""]); }
    } else if (/^pip install/.test(c)) {
      if (!activ) {
        spune(c, ["!Atenție: instalezi în Python-ul global, nu în mediu.", "!Activează mediul întâi."]);
      } else {
        const p = c.replace(/^pip install\s*/, "").split(/\s+/).filter(Boolean);
        if (!p.length) {
          spune(c, ["!Specifică ce vrei să instalezi. Exemplu: pip install requests pandas"]);
        } else {
          instalate = [...new Set([...instalate, ...p])];
          facute.add(2);
          spune(c, ["", ...p.map((x) => `Collecting ${x}`), `Successfully installed ${p.join(" ")}`]);
        }
      }
    } else if (/^pip list/.test(c)) {
      if (!activ) {
        spune(c, ["!Listezi pachetele globale. Activează mediul."]);
      } else {
        facute.add(3);
        spune(c, ["", "Package    Version", "---------- -------",
          ...(instalate.length ? instalate.map((x) => `${x.padEnd(11)}(latest)`) : ["(niciun pachet încă)"])]);
      }
    } else if (/^(ajutor|help)$/.test(c)) {
      spune(c, ["", "Comenzi recunoscute:",
        "  python -m venv venv", "  venv\\Scripts\\activate", "  pip install requests pandas",
        "  pip list", "  deactivate", "  curata"]);
    } else if (/^(curata|clear|cls)$/.test(c)) {
      linii.length = 0; linii.push("_");
    } else {
      spune(c, [`!'${c.split(" ")[0]}' nu este recunoscut.  Scrie ajutor.`]);
    }
    render();
  }

  gazda.innerHTML = `
    <div class="trm__task">${sarcini.map((t) => `<span class="tchip">${t.eticheta}</span>`).join("")}</div>
    <div class="trm" id="trm" aria-live="polite"></div>
    <div class="trm__in">
      <span id="prompt">PS ${P}&gt;</span>
      <input id="tin" autocomplete="off" spellcheck="false" aria-label="Comandă în terminal">
    </div>`;

  const inp = gazda.querySelector("#tin");
  inp.addEventListener("keydown", (e) => {
    if (e.key === "Enter") { ruleaza(inp.value); inp.value = ""; }
  });
  render();
}
