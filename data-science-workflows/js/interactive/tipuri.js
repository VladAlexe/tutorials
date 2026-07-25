/* tipuri.js — exercițiu „Recunoaște tipul”. Opt valori, una pe rând, opt tipuri
   de ales, feedback imediat, bară de progres, scor final și reluare.
   Valorile și opțiunile vin din `parametri`. */

function esc(s) {
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

export default function tipuri(gazda, parametri = {}) {
  const valori = parametri.valori || [];
  const optiuni = parametri.optiuni || [];
  const n = valori.length;

  let i = 0, corecte = 0;
  const raspunsuri = [];

  function deseneaza() {
    // Ecranul de final
    if (i >= n) {
      const totBun = corecte === n;
      gazda.innerHTML = `
        <div class="srt__bar">${raspunsuri.map((a) => `<span class="${a ? "ok" : "no"}"></span>`).join("")}</div>
        <div class="srt__val">${corecte} / ${n}</div>
        <p class="srt__fb">${totBun
          ? "<b>Tot corect.</b> Distincția dintre <code>'2024'</code> și <code>2024</code> e cea care produce cele mai multe erori tăcute la citirea fișierelor."
          : "<b>Reia.</b> Cazurile ratate merită privite încă o dată — se întorc la curățarea datelor."}</p>
        <button class="btn btn--ghost" id="iar">Încă o dată</button>`;
      gazda.querySelector("#iar").addEventListener("click", () => {
        i = 0; corecte = 0; raspunsuri.length = 0; deseneaza();
      });
      return;
    }

    const q = valori[i];
    gazda.innerHTML = `
      <div class="srt__bar">${valori.map((_, k) =>
        `<span class="${raspunsuri[k] === undefined ? "" : (raspunsuri[k] ? "ok" : "no")}"></span>`).join("")}</div>
      <div class="srt__val">${esc(q.valoare)}</div>
      <div class="srt__opts">${optiuni.map((o) =>
        `<button class="srt__opt" data-o="${esc(o)}">${esc(o)}</button>`).join("")}</div>
      <p class="srt__fb" role="status" aria-live="polite"></p>`;

    gazda.querySelectorAll(".srt__opt").forEach((b) => {
      b.addEventListener("click", () => {
        const bun = b.dataset.o === q.tip;
        gazda.querySelectorAll(".srt__opt").forEach((x) => {
          x.disabled = true;
          if (x.dataset.o === q.tip) x.classList.add("ok");
          else if (x === b) x.classList.add("no");
        });
        raspunsuri[i] = bun;
        if (bun) corecte++;
        gazda.querySelector(".srt__fb").innerHTML = `<b>${bun ? "Corect." : "Nu."}</b> ${q.explicatie}`;
        setTimeout(() => { i++; deseneaza(); }, bun ? 1250 : 2400);
      });
    });
  }

  deseneaza();
}
