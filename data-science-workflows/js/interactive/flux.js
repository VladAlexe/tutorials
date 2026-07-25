/* flux.js — cele opt etape ale fluxului de lucru plus baza de date (depozit).
   Datele (etapele) vin din `parametri.etape`; componenta nu știe conținutul. */

export default function flux(gazda, parametri = {}) {
  const etape = parametri.etape || [];

  gazda.innerHTML = `
    <div class="wf">
      <div class="wf__stages" role="tablist" aria-label="Etapele fluxului de lucru">
        ${etape.map((s, i) => `
          <button class="stage ${s.depozit ? "stage--db" : ""}" role="tab"
                  aria-selected="false" data-i="${i}">
            <i>${s.depozit ? "▣" : String(i + 1).padStart(2, "0")}</i>${s.nume}
          </button>`).join("")}
      </div>
      <div class="wf__info" id="wfi" role="region" aria-live="polite">
        <h4>Fluxul complet</h4>
        <p>Opt etape și un depozit. Apasă pe oricare ca să vezi ce se întâmplă acolo.</p>
      </div>
    </div>`;

  const info = gazda.querySelector("#wfi");
  const butoane = gazda.querySelectorAll(".stage");

  butoane.forEach((b) => {
    b.addEventListener("click", () => {
      butoane.forEach((x) => {
        x.classList.remove("is-on");
        x.setAttribute("aria-selected", "false");
      });
      b.classList.add("is-on");
      b.setAttribute("aria-selected", "true");
      const s = etape[+b.dataset.i];
      info.innerHTML =
        `<h4>${s.nume}</h4><p>${s.descriere}</p>` +
        `<p class="wf__ch">Capitolul ${s.capitol}</p>`;
    });
  });
}
