/* ===========================================================================
   ALEGEREA NUMELUI, LA PRIMA INTRARE CU GITHUB

   Oriunde ar intra studentul cu GitHub (codul orei, antetul, de acasă), până
   își alege numele din listă contul lui nu este legat de nimeni și
   răspunsurile nu se salvează. Pasul se face o singură dată și nu ține de
   oră: îl folosesc și pagina de intrare la oră, și pagina contului.

   Lista nu vine întreagă: numele apar după trei litere scrise (db/25), ca
   numele colegilor să nu le vadă oricine își face un cont GitHub.
   =========================================================================== */

import * as O from "./ora.js?v=105";

const RAD = "/data-science-workflows";
const esc = s => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/"/g, "&quot;");

/** Trebuie ales numele? Cont GitHub (nu invitat), nu profesor, fără nume legat. */
export const trebuieAles = p => !!(p?.autentificat && !p.anonim && !p.profesorReal && !p.matricol);

/* --- informarea GDPR ------------------------------------------------------
   Nu e consimțământ (temeiul e interesul legitim), ci dovada că studentul a
   primit informarea. Se cere o dată pe cont, și din nou când se schimbă
   versiunea politicii (O.INFORMARE). */

export function informare({ gazda, cap, mesaj, dupa }){
  cap("Protecția datelor",
      "Situl înregistrează activitatea la curs. Citește politica de confidențialitate și confirmă luarea la cunoștință.");
  gazda.innerHTML = `
    <div class="cutie">
      <ul class="inf">
        <li>Operator: Vlad Alexe, titularul cursului.</li>
        <li>Se prelucrează numele, contul GitHub, răspunsurile, prezența și notele, pentru organizarea și evaluarea cursului.</li>
        <li>Datele tale sunt accesibile doar ție și titularului. Datele se șterg cel târziu la 31 martie 2027.</li>
        <li>Ai dreptul de acces, rectificare, ștergere, restricționare, portabilitate și opoziție.</li>
      </ul>
      <p class="mic"><a href="${RAD}/date-personale/" target="_blank" rel="noopener">Citește politica de confidențialitate completă ↗</a></p>
      <label class="bifa"><input type="checkbox" id="inf-ok">
        <span>Am citit și am luat la cunoștință Politica de confidențialitate (versiunea ${O.INFORMARE}).</span></label>
      <button class="btn btn--tare" id="bt-inf" type="button" disabled>Confirm și continui</button>
      <p class="mic">Confirmarea nu este un consimțământ. Se păstrează data și versiunea, ca dovadă a informării.</p>
    </div>`;
  const b = gazda.querySelector("#bt-inf");
  gazda.querySelector("#inf-ok").onchange = e => { b.disabled = !e.target.checked; };
  b.onclick = async () => {
    b.disabled = true; b.textContent = "Se salvează…";
    const r = await O.confirmaInformarea();
    if (!r?.ok){ b.disabled = false; b.textContent = "Confirm și continui";
                 mesaj(r?.mesaj || "Nu s-a putut salva confirmarea.", "rau"); return; }
    mesaj("");
    dupa();
  };
}

/* --- căutarea și alegerea -------------------------------------------------
   gazda: unde se desenează; cap(titlu, sub): titlul paginii; mesaj(text, fel);
   dupa(nume): după alegere; faraNume(): „numele meu nu apare în listă”. */

export async function alegeNumele(o){
  if (await O.informareConfirmata() === false){ informare({ ...o, dupa: () => cautare(o) }); return; }
  cautare(o);
}

function cautare({ gazda, cap, mesaj, dupa, faraNume }){
  cap("Alege-ți numele",
      "Scrie numele tău și apasă-l în listă. Pasul se face o singură dată: din acel moment, răspunsurile se salvează în contul tău.");
  gazda.innerHTML = `
    <div class="cutie">
      <label for="an-cauta">Numele tău</label>
      <input class="cauta" id="an-cauta" type="search" autocomplete="off" spellcheck="false"
             placeholder="de exemplu, numele de familie">
      <div class="lista" id="an-lista"></div>
      <p class="mic" id="an-stare" aria-live="polite">Numele apar după primele trei litere.</p>
      <button class="btn btn--tare" id="an-ok" type="button" disabled>Confirm selecția</button>
      <p class="mic"><a href="#" id="an-nu">Numele meu nu apare în listă</a></p>
    </div>`;

  const $ = s => gazda.querySelector(s);
  const camp = $("#an-cauta"), lista = $("#an-lista"), stare = $("#an-stare"), ok = $("#an-ok");
  let ales = null, cerere = 0, t = null;
  camp.focus();

  async function cauta(){
    const text = camp.value.trim();
    const nr = ++cerere;
    ales = null; ok.disabled = true;
    if (text.replace(/[\s-]/g, "").length < 3){
      lista.innerHTML = ""; stare.textContent = "Numele apar după primele trei litere."; return;
    }
    stare.textContent = "Se caută…";
    const r = await O.cautaNumele(text);
    if (nr !== cerere) return;                      /* a scris între timp: contează ultima căutare */
    if (r === null){
      lista.innerHTML = "";
      stare.textContent = O.lipsesteBaza()
        ? "Căutarea nu există încă în baza de date: rulează db/25-alegere-nume.sql în Supabase."
        : "Căutarea nu a reușit. Verifică conexiunea și încearcă din nou.";
      return;
    }
    lista.innerHTML = r.map(x => `
      <button class="nume" type="button" data-k="${esc(x.cheie)}">${esc(x.nume)}${x.grupa ? `<small>${esc(x.grupa)}</small>` : ""}</button>`).join("");
    stare.textContent = !r.length ? "Niciun nume găsit. Verifică scrierea sau scrie doar numele de familie."
                      : r.length >= 10 ? "Primele 10 rezultate: scrie mai mult din nume."
                      : "Apasă pe numele tău, apoi confirmă.";
  }

  camp.addEventListener("input", () => { clearTimeout(t); t = setTimeout(cauta, 250); });
  lista.addEventListener("click", e => {
    const b = e.target.closest(".nume"); if (!b) return;
    lista.querySelectorAll(".nume").forEach(x => x.classList.remove("on"));
    b.classList.add("on"); ales = b.dataset.k; ok.disabled = false;
  });
  ok.onclick = async () => {
    if (!ales) return;
    ok.disabled = true; ok.textContent = "Se salvează…";
    const r = await O.alegeNumele(ales);
    if (!r?.ok){
      ok.disabled = false; ok.textContent = "Confirm selecția";
      mesaj(r?.mesaj || (O.lipsesteBaza()
        ? "Alegerea nu există încă în baza de date: rulează db/25-alegere-nume.sql în Supabase."
        : "Alegerea nu a reușit. Încearcă din nou."), "rau");
      return;
    }
    mesaj("");
    dupa(r.nume);
  };
  $("#an-nu").onclick = e => { e.preventDefault(); mesaj(""); faraNume(); };
}
