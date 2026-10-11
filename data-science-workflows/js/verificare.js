/* ===========================================================================
   Verificarile din lectie

   Marcaj in pagina, fara JavaScript scris de mana:

   <div class="verif" data-id="1.4-v1" data-corect="1">
     <p class="verif__q">Întrebarea?</p>
     <button>Varianta A</button>
     <button>Varianta B</button>
     <p class="verif__ex">Explicația, afișată după răspuns.</p>
   </div>

   data-corect e indexul variantei corecte, de la 0.
   Raspunsul se salveaza daca studentul e autentificat; altfel doar se afiseaza.
   =========================================================================== */

import { salveazaRaspuns, raspunsuriDate } from "./colectare.js?v=1";

const CSS = `
.verif{background:var(--panza);border:1px solid var(--linie);border-radius:11px;
  padding:20px 22px;margin:0 0 26px;max-width:var(--citit)}
.verif__et{font-family:var(--mono);font-size:10.5px;font-weight:500;letter-spacing:.12em;
  text-transform:uppercase;color:var(--text-3);margin-bottom:9px;display:block}
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
.verif__stare{font-family:var(--mono);font-size:11px;color:var(--text-3);margin-top:11px;
  display:none}
.verif__stare.vazut{display:block}
`;

export async function porneste(capitol){
  const toate = [...document.querySelectorAll(".verif")];
  if (!toate.length) return;

  const stil = document.createElement("style");
  stil.textContent = CSS;
  document.head.appendChild(stil);

  const deja = await raspunsuriDate(capitol);

  for (const v of toate){
    const id = v.dataset.id;
    const corect = parseInt(v.dataset.corect, 10);
    const q = v.querySelector(".verif__q");
    const ex = v.querySelector(".verif__ex");
    const optiuni = [...v.querySelectorAll("button")];

    if (q && !v.querySelector(".verif__et")) {
      const et = document.createElement("span");
      et.className = "verif__et";
      et.textContent = "Verificare";
      v.insertBefore(et, q);
    }
    optiuni.forEach((b, i) => { b.className = "verif__opt"; b.dataset.i = i; });

    const stare = document.createElement("p");
    stare.className = "verif__stare";
    v.appendChild(stare);

    const arata = (ales, salvat) => {
      optiuni.forEach(b => {
        b.disabled = true;
        const i = +b.dataset.i;
        if (i === corect) b.classList.add("bun");
        else if (i === ales) b.classList.add("rau");
      });
      ex?.classList.add("vazut");
      if (salvat !== null) {
        stare.textContent = salvat ? "Răspuns înregistrat." : "Nu e înregistrat: nu ești autentificat.";
        stare.classList.add("vazut");
      }
    };

    if (deja.has(id)) { arata(deja.get(id).raspuns, null); continue; }

    optiuni.forEach(b => b.addEventListener("click", async () => {
      const ales = +b.dataset.i;
      arata(ales, false);
      const ok = await salveazaRaspuns({
        intrebareId:id, capitol, raspuns:ales, corect:(ales === corect)
      });
      stare.textContent = ok ? "Răspuns înregistrat." : "Nu e înregistrat: nu ești autentificat.";
    }));
  }
}
