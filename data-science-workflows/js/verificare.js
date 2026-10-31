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

   FIECARE DESCHIDERE A LECȚIEI E O ÎNCERCARE NOUĂ. Pagina pornește curată.

   Înainte restaura răspunsurile, din browser și din bază, și asta strica exact
   lucrul pentru care există ora: veneau la clasă, vedeau deja bifat de acasă,
   iar întrebarea live nu mai măsura nimic. Acum nu se restaurează nimic.

   Istoricul nu se pierde: fiecare răspuns e un rând nou în `raspunsuri`, și
   din el se face nota (în oră întreg, acasă jumătate, se ia cel mai bun).
   Singurul lucru care rămâne pe ecran e o linie cenușie la întrebările la care
   a mai răspuns altă dată, fără să spună ce a ales sau dacă a nimerit.

   Pune clasa .raspuns pe element și trimite evenimentul „verif:raspuns",
   de care se folosește rulatorul de slide-uri ca să deschidă poarta.
   =========================================================================== */

import { salveazaRaspuns, aMaiRaspuns, deCeNu } from "./colectare.js?v=103";

const CSS = `
.verif{background:var(--panza);border:1px solid var(--linie);border-radius:11px;
  padding:19px 21px;margin:26px 0;max-width:66ch}
.verif__et{font-family:var(--sans);font-size:var(--t1);font-weight:500;color:var(--text-3);margin-bottom:9px;display:flex;
  align-items:center;gap:7px}
.verif__et::before{content:'';width:5px;height:5px;border-radius:50%;background:var(--accent)}
.verif.raspuns .verif__et::before{background:var(--ok)}
.verif__q{font-family:var(--sans);font-weight:500;font-size:var(--t4);line-height:1.42;
  margin:0 0 15px;max-width:none}
.verif__opt{display:block;width:100%;text-align:left;font-family:var(--serif);
  font-size:var(--t4);line-height:1.45;padding:11px 15px;margin-bottom:8px;border-radius:8px;
  border:1px solid var(--linie-2);background:var(--fundal);transition:.13s}
.verif__opt:hover:not(:disabled){border-color:var(--accent);background:var(--accent-slab)}
.verif__opt:disabled{cursor:default}
.verif__opt.bun{border-color:var(--ok);background:var(--ok-slab)}
.verif__opt.rau{border-color:var(--nu);background:var(--nu-slab)}
.verif__ex{display:none;margin:14px 0 0;padding:14px 16px;background:var(--panza-2);
  border-radius:8px;font-size:var(--t3);line-height:1.56;max-width:none}
.verif__ex.vazut{display:block}
.verif__stare{font-family:var(--sans);font-size:var(--t1);color:var(--text-3);margin-top:11px;
  display:none;max-width:none}
.verif__stare.vazut{display:block}
`;

export function porneste(capitol){
  const toate = [...document.querySelectorAll(".verif")];
  if (!toate.length) return;

  const stil = document.createElement("style");
  stil.textContent = CSS;
  document.head.appendChild(stil);

  const comenzi = new Map();   /* id -> funcția care arată o linie de stare */

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
    optiuni.forEach(b => b.addEventListener("click", async () => {
      const ales = +b.dataset.i;
      arata(ales, null);
      const ok = await salveazaRaspuns({
        intrebareId:id, capitol, raspuns:ales, corect:(ales === corect)
      });
      stare.textContent = ok ? "Răspuns înregistrat."
                             : `Răspunsul nu a fost înregistrat: ${deCeNu()}.`;
      stare.classList.add("vazut");
    }));

    /* Nimic restaurat: întrebarea pornește deschisă, de fiecare dată.
       Singurul lucru pe care îl poate afla din fundal e că a mai trecut pe
       aici, fără ce a ales și fără verdict. */
    comenzi.set(id, () => {
      if (v.classList.contains("raspuns")) return;
      stare.textContent = "Ai mai răspuns la această întrebare într-o sesiune anterioară.";
      stare.classList.add("vazut");
    });
  }

  /* în fundal: la care întrebări a mai răspuns cândva. Doar atât, fără ce a
     ales și fără verdict. Dacă a răspuns deja acum, nu suprascriem. */
  aMaiRaspuns(capitol).then(vazute => {
    vazute.forEach(id => comenzi.get(id)?.());
  }).catch(() => { /* fără bază, întrebarea arată pur și simplu curată */ });
}
