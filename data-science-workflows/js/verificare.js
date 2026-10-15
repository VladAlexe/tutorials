/* ===========================================================================
   VERIFICĂRILE DIN LECȚIE

   Marcaj în pagină, fără JavaScript scris de mână:

   <div class="verif" data-id="c1-v1" data-corect="1">
     <p class="verif__q">Întrebarea?</p>
     <button>Varianta A</button>
     <button>Varianta B</button>
     <p class="verif__ex">Explicația, afișată după răspuns.</p>
   </div>

   data-corect e indexul variantei corecte, de la 0.

   Pornește în două timpi, și asta e important la clasă: întâi restaurează din
   browser, imediat, fără rețea; apoi, în fundal, aduce din baza de date ce s-a
   răspuns de pe alt calculator. Dacă rețeaua e lentă, lecția nu așteaptă.

   Pune clasa .raspuns pe element și trimite evenimentul „verif:raspuns",
   de care se folosește rulatorul de slide-uri ca să deschidă poarta.
   =========================================================================== */

import { salveazaRaspuns, raspunsuriDate } from "./colectare.js?v=34";

const CSS = `
.verif{background:var(--panza);border:1px solid var(--linie);border-radius:11px;
  padding:19px 21px;margin:26px 0;max-width:66ch}
.verif__et{font-family:var(--mono);font-size:10px;font-weight:500;letter-spacing:.14em;
  text-transform:uppercase;color:var(--text-3);margin-bottom:9px;display:flex;
  align-items:center;gap:7px}
.verif__et::before{content:'';width:5px;height:5px;border-radius:50%;background:var(--accent)}
.verif.raspuns .verif__et::before{background:var(--ok)}
.verif__q{font-family:var(--sans);font-weight:500;font-size:16.5px;line-height:1.42;
  margin:0 0 15px;max-width:none}
.verif__opt{display:block;width:100%;text-align:left;font-family:var(--serif);
  font-size:16px;line-height:1.45;padding:11px 15px;margin-bottom:8px;border-radius:8px;
  border:1px solid var(--linie-2);background:var(--fundal);transition:.13s}
.verif__opt:hover:not(:disabled){border-color:var(--accent);background:var(--accent-slab)}
.verif__opt:disabled{cursor:default}
.verif__opt.bun{border-color:var(--ok);background:var(--ok-slab)}
.verif__opt.rau{border-color:var(--nu);background:var(--nu-slab)}
.verif__ex{display:none;margin:14px 0 0;padding:14px 16px;background:var(--panza-2);
  border-radius:8px;font-size:15.5px;line-height:1.56;max-width:none}
.verif__ex.vazut{display:block}
.verif__stare{font-family:var(--mono);font-size:10.5px;color:var(--text-3);margin-top:11px;
  display:none;max-width:none}
.verif__stare.vazut{display:block}
`;

const cheieLocal = capitol => `dsw.raspunsuri.${capitol}`;

function citesteLocal(capitol){
  try { return JSON.parse(localStorage.getItem(cheieLocal(capitol)) || "{}"); }
  catch { return {}; }
}
function scrieLocal(capitol, id, raspuns){
  try {
    const x = citesteLocal(capitol);
    x[id] = raspuns;
    localStorage.setItem(cheieLocal(capitol), JSON.stringify(x));
  } catch { /* fără memorie locală, verificarea merge la fel */ }
}

export function porneste(capitol){
  const toate = [...document.querySelectorAll(".verif")];
  if (!toate.length) return;

  const stil = document.createElement("style");
  stil.textContent = CSS;
  document.head.appendChild(stil);

  const local = citesteLocal(capitol);
  const comenzi = new Map();   /* id -> funcția care afișează un răspuns */

  for (const v of toate){
    const id      = v.dataset.id;
    const corect  = parseInt(v.dataset.corect, 10);
    const q       = v.querySelector(".verif__q");
    const ex      = v.querySelector(".verif__ex");
    const optiuni = [...v.querySelectorAll("button")];

    if (q && !v.querySelector(".verif__et")){
      const et = document.createElement("span");
      et.className = "verif__et";
      et.textContent = "Verificare";
      v.insertBefore(et, q);
    }
    optiuni.forEach((b, i) => { b.className = "verif__opt"; b.dataset.i = i; });

    const stare = document.createElement("p");
    stare.className = "verif__stare";
    v.appendChild(stare);

    const arata = (ales, nota) => {
      if (v.classList.contains("raspuns")) return;
      optiuni.forEach(b => {
        b.disabled = true;
        const i = +b.dataset.i;
        if (i === corect) b.classList.add("bun");
        else if (i === ales) b.classList.add("rau");
      });
      ex?.classList.add("vazut");
      v.classList.add("raspuns");
      if (nota){ stare.textContent = nota; stare.classList.add("vazut"); }
      document.dispatchEvent(new CustomEvent("verif:raspuns", {
        detail:{ id, capitol, raspuns:ales, corect:(ales === corect) }
      }));
    };
    comenzi.set(id, arata);

    optiuni.forEach(b => b.addEventListener("click", async () => {
      const ales = +b.dataset.i;
      scrieLocal(capitol, id, ales);
      arata(ales, null);
      const ok = await salveazaRaspuns({
        intrebareId:id, capitol, raspuns:ales, corect:(ales === corect)
      });
      stare.textContent = ok ? "Răspuns înregistrat."
                             : "Nu e înregistrat: nu ești autentificat.";
      stare.classList.add("vazut");
    }));

    /* timpul 1: ce s-a răspuns pe calculatorul ăsta, fără să aștepte nimic */
    if (id in local) arata(local[id], null);
  }

  /* timpul 2: ce s-a răspuns de pe alt calculator, când ajunge răspunsul */
  raspunsuriDate(capitol).then(dinBaza => {
    dinBaza.forEach((r, id) => {
      const f = comenzi.get(id);
      if (!f) return;
      scrieLocal(capitol, id, r.raspuns);
      f(r.raspuns, "Răspuns înregistrat.");
    });
  }).catch(() => { /* fără baza de date, rămâne ce e în browser */ });
}
