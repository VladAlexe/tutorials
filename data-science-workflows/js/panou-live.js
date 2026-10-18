/* ===========================================================================
   PANOUL VIU, O SINGURĂ DATĂ

   Până acum panoul exista o dată, la `/predau/ora/`, ca pagină separată cu bara
   ei de butoane. Asta era problema: aceeași oră avea două volane, unul în
   lecție și unul în panou, și nu știai la care să te uiți.

   Acum panoul e desenat de aici, și apare în două locuri, cu același cod:

     sertar        peste treimea de jos a lecției, la tasta V, FĂRĂ NUME
     al doilea ecran  la /predau/ora/, ca oglindă fără butoane, CU NUME

   Diferența nu e de spațiu, e de public. Sertarul se deschide peste lecție,
   adică peste exact ce e pe proiector: acolo numele studenților ar fi citite
   de toată sala. În sertar vezi câți, nu cine. Cine anume vezi pe al doilea
   ecran, care e laptopul tău și nu se proiectează.

   Modulul își aduce stilul singur, cu clase `pv-`, ca să nu depindă de
   css/predau.css. Lecția nu încarcă foaia de predare și nici nu trebuie.

   Nu are niciun buton care schimbă ora. Panoul doar se uită.
   =========================================================================== */

import { STARI, ORDINEA } from "./ora.js?v=48";

/* --- stilul --------------------------------------------------------------- */

const CSS = `
.pv{display:grid;grid-template-columns:214px minmax(0,1fr);gap:26px;align-items:start}
@media (max-width:820px){ .pv{grid-template-columns:minmax(0,1fr);gap:18px} }
.pv__st{min-width:0}
.pv__dr{min-width:0}
.pv__n{font-family:var(--mono);font-size:10.5px;letter-spacing:.12em;
  text-transform:uppercase;color:var(--text-3);margin:0 0 6px}
.pv__q{font-family:var(--sans);font-size:16.5px;font-weight:600;letter-spacing:-.015em;
  color:var(--text);margin:0 0 14px;line-height:1.35}

.pv-inel{display:block;margin:0 auto 12px}
.pv-inel .num{font-family:var(--sans);font-size:30px;font-weight:600;
  letter-spacing:-.02em}
.pv-inel .sub{font-family:var(--mono);font-size:8.5px;letter-spacing:.09em;
  fill:var(--text-3);text-transform:uppercase}
.pv-gol{font-family:var(--sans);font-size:13px;color:var(--text-3);
  text-align:center;padding:26px 10px;line-height:1.5}

.pv-nr{list-style:none;padding:0;margin:0;max-width:none;font-family:var(--sans);font-size:13px}
.pv-nr li{display:flex;align-items:center;gap:9px;padding:5px 2px;margin:0;
  border-bottom:1px solid var(--linie)}
.pv-nr li::before{content:none}
.pv-nr li:last-child{border-bottom:0}
.pv-nr span{color:var(--text-2)}
.pv-nr b{margin-left:auto;font-family:var(--mono);font-size:13px;font-weight:500;
  color:var(--text);font-variant-numeric:tabular-nums}

.pv-g{display:inline-flex;align-items:center;justify-content:center;
  width:17px;height:17px;border-radius:50%;font-size:10px;line-height:1;flex:none}
.pv-g--ok{background:var(--ok);color:var(--panza)}
.pv-g--nu{background:var(--nu);color:var(--panza)}
.pv-g--gol{border:1.5px solid var(--linie-2);color:var(--text-3)}
.pv-g--nim{border:1.5px dotted var(--linie-2);color:transparent}

.pv-tb{width:100%;border-collapse:collapse;font-family:var(--sans);font-size:13px}
.pv-tb th{text-align:left;font-family:var(--mono);font-size:9.5px;font-weight:500;
  letter-spacing:.11em;text-transform:uppercase;color:var(--text-3);
  padding:0 10px 7px 0;border-bottom:1px solid var(--linie)}
.pv-tb td{padding:7px 10px 7px 0;border-bottom:1px solid var(--linie);
  color:var(--text);vertical-align:middle}
.pv-tb tr:last-child td{border-bottom:0}
.pv-tb tr.plecat td{opacity:.52}
.pv-tb__ales{font-family:var(--mono);font-size:11.5px;color:var(--text-2);
  max-width:30ch;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.pv-tb__ales em{font-style:italic;color:var(--text-3)}
.pv-tb__q{color:var(--text-3)}
.pv-tb__tot{display:flex;align-items:center;gap:8px;justify-content:flex-end}
.pv-bm{display:inline-block;width:50px;height:4px;border-radius:99px;
  background:var(--panza-2);overflow:hidden}
.pv-bm i{display:block;height:100%;background:var(--accent);border-radius:99px}
.pv-rap{font-family:var(--mono);font-size:10.5px;color:var(--text-3);
  font-variant-numeric:tabular-nums}
.pv-sort{font-family:var(--mono);font-size:10.5px;color:var(--text-3);margin:10px 0 0}
.pv-sort button{font:inherit;color:var(--text-3);background:none;border:0;
  cursor:pointer;padding:0 2px;text-decoration:underline dotted}
.pv-sort button:hover,.pv-sort button.on{color:var(--text)}
.pv-dist{display:flex;flex-direction:column;gap:8px;margin:0 0 20px}
.pv-dist__r{display:grid;grid-template-columns:minmax(0,1.3fr) minmax(0,2fr) 34px;gap:12px;align-items:center}
.pv-dist__t{font-family:var(--sans);font-size:15px;color:var(--text)}
.pv-dist__b{height:14px;border-radius:99px;background:var(--panza-2);overflow:hidden}
.pv-dist__b i{display:block;height:100%;background:var(--accent);border-radius:99px;transition:width .4s}
.pv-dist__r:nth-child(2) .pv-dist__b i{background:var(--ambra)}
.pv-dist__r:nth-child(3) .pv-dist__b i{background:var(--roza)}
.pv-dist__r:nth-child(4) .pv-dist__b i{background:var(--salvie)}
.pv-dist__r b{font-family:var(--mono);font-size:16px;font-weight:500;text-align:right}
.pv-mare{font-family:var(--sans);font-size:22px;color:var(--text-2);margin:6px 0 0}
.pv-mare b{font-size:40px;color:var(--text);font-weight:600}
.pv--anonim .pv-inel{margin-left:0}
`;

let pus = false;
/** Pune stilul în pagină o singură dată, oriunde ar fi desenat panoul. */
export function stil(){
  if (pus) return;
  pus = true;
  const s = document.createElement("style");
  s.textContent = CSS;
  document.head.appendChild(s);
}

/* --- ceasul ---------------------------------------------------------------
   Numără în sus de când a apărut slide-ul, nu de la începutul orei. Ăla e
   numărul după care decizi dacă mergi mai departe. Verde până la prag,
   chihlimbar după. Nu e numărătoare inversă și nu dă pe nimeni afară.

   Chihlimbarul e un jeton separat, nu `--nu`. Cărămiziul înseamnă „greșit" în
   tot situl; un ceas de aceeași culoare s-ar citi de la distanță, cu coada
   ochiului, ca un verdict. */

export const PRAG = 120;   /* secunde */

export function ceasText(secunde){
  const s = Math.max(0, Math.floor(secunde));
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
}

export function ceasHTML(secunde, prag = PRAG){
  const tarziu = secunde >= prag;
  return `<span class="ceas${tarziu ? " ceas--tarziu" : ""}"
    title="de când e slide-ul pe ecran">${ceasText(secunde)}</span>`;
}

/* --- cifrele --------------------------------------------------------------- */

/** Câți sunt în fiecare stare, pe slide-ul de acum. */
export function numara(randuri){
  const c = {};
  ORDINEA.forEach(k => c[k] = 0);
  (randuri || []).forEach(x => { if (c[x.stare] != null) c[x.stare]++; });
  return c;
}

/* --- inelul ---------------------------------------------------------------
   Patru segmente pe același cerc, în ordinea stărilor. Numărul din mijloc e
   cel care contează: câți au trimis ceva, din câți sunt. */

function inel(cate, trimis, total){
  const R = 52, C = 2 * Math.PI * R;
  let unghi = -90;
  const culori = { trecut:"var(--ok)", trimis_gresit:"var(--nu)",
                   trimis_gol:"var(--linie-2)", nefacut:"var(--linie)" };
  const arce = ORDINEA.map(k => {
    const n = cate[k];
    if (!n || !total) return "";
    const lung = C * n / total;
    const s = `<circle cx="66" cy="66" r="${R}" fill="none" stroke="${culori[k]}"
      stroke-width="13" stroke-dasharray="${Math.max(0, lung - 2)} ${C - lung + 2}"
      transform="rotate(${unghi} 66 66)"></circle>`;
    unghi += 360 * n / total;
    return s;
  }).join("");

  return `
    <svg class="pv-inel" width="132" height="132" viewBox="0 0 132 132" role="img"
         aria-label="${trimis} din ${total} au trimis">
      <circle cx="66" cy="66" r="${R}" fill="none" stroke="var(--linie)" stroke-width="13"/>
      ${arce}
      <text class="num" x="66" y="64" text-anchor="middle" dominant-baseline="middle"
            fill="var(--text)">${trimis}</text>
      <text class="sub" x="66" y="86" text-anchor="middle">din ${total}</text>
    </svg>
    <ul class="pv-nr">
      ${ORDINEA.map(k => `<li>
        <span class="pv-g pv-g--${STARI[k].clasa.replace("g--","")}">${STARI[k].glif}</span>
        <span>${STARI[k].nume}</span><b>${cate[k]}</b></li>`).join("")}
    </ul>`;
}

/* --- ce a ales -------------------------------------------------------------
   Coloana asta e motivul pentru care panoul există. Fără ea ai o listă de
   bife și n-ai ști de unde să începi discuția.

   Aici era o greșeală care se vedea doar când un slide avea DOUĂ verificări:
   indicele răspunsului venea de la o întrebare, iar eticheta era citită din
   variantele celeilalte. Pe slide-ul 4 din cursul 2 ieșea „a ales meniul" și
   „greșit" în același rând, ceea ce e imposibil, meniul fiind răspunsul bun.

   Acum rândul spune și la CE întrebare a răspuns (`ales_la`), iar varianta se
   caută în întrebarea aceea. Dacă baza e mai veche și nu trimite `ales_la`,
   eticheta se afișează doar când slide-ul are o singură întrebare; altfel se
   scrie verdictul, care e întotdeauna adevărat. */

function ales(x, intrebari){
  if (x.stare === "nefacut")    return "—";
  if (x.stare === "trimis_gol") return "<em>trimis fără răspuns</em>";

  const verdict = x.stare === "trecut" ? "<em>corect</em>" : "<em>greșit</em>";
  if (x.ales == null) return verdict;

  const q = x.ales_la ? intrebari.find(i => i.id === x.ales_la)
          : (intrebari.length === 1 ? intrebari[0] : null);
  const eticheta = q?.optiuni?.[x.ales];
  if (!eticheta) return verdict;

  /* când slide-ul are mai multe întrebări, spune și la care a răspuns */
  return intrebari.length > 1 && q.scurt
    ? `<span class="pv-tb__q">${q.scurt}:</span> ${eticheta}`
    : eticheta;
}

/* --- tabelul --------------------------------------------------------------- */

const RANG = { trimis_gol:0, trimis_gresit:1, nefacut:2, trecut:3 };

function tabel(randuri, intrebari, sortare, totalSarcini){
  if (!randuri.length) return `
    <div class="pv-gol">Încă n-a intrat nimeni.<br>
      Arată codul pe proiector; cum intră primul, apare aici.</div>`;

  const r = [...randuri];
  if (sortare === "slide")    r.sort((a,b) => RANG[a.stare] - RANG[b.stare] ||
                                              a.nume.localeCompare(b.nume, "ro"));
  else if (sortare === "tot") r.sort((a,b) => a.facute - b.facute ||
                                              a.nume.localeCompare(b.nume, "ro"));
  else                        r.sort((a,b) => a.nume.localeCompare(b.nume, "ro"));

  const max = Math.max(1, totalSarcini || 1, ...r.map(x => x.facute || 0));

  return `<table class="pv-tb">
    <thead><tr>
      <th>Student</th><th>Acest slide</th><th>Ce a ales</th>
      <th style="text-align:right">Toată ora</th>
    </tr></thead>
    <tbody>${r.map(x => {
      const st = STARI[x.stare] || STARI.nefacut;
      const plecat = x.vazut_la && (Date.now() - new Date(x.vazut_la)) > 120000;
      return `<tr class="${plecat ? "plecat" : ""}">
        <td>${x.nume}</td>
        <td><span class="pv-g pv-g--${st.clasa.replace("g--","")}"
              title="${st.nume}">${st.glif}</span></td>
        <td class="pv-tb__ales">${ales(x, intrebari)}</td>
        <td><span class="pv-tb__tot">
          <span class="pv-bm"><i style="width:${Math.round(100 * (x.facute||0) / max)}%"></i></span>
          <span class="pv-rap">${x.facute || 0}/${totalSarcini || max}</span></span></td>
      </tr>`;
    }).join("")}</tbody></table>
    <p class="pv-sort">sortează după:
      ${[["slide","slide"],["nume","nume"],["tot","cât a făcut"]].map(([k,t]) =>
        `<button type="button" data-sort="${k}" class="${sortare===k?"on":""}">${t}</button>`
      ).join(" · ")}</p>`;
}

/* --- vederea întreagă ------------------------------------------------------ */

/**
 * @param slide        rândul din hartă pentru slide-ul de pe ecran, sau null
 * @param sarcini      sarcinile slide-ului, din hartă
 * @param randuri      rândurile de la `panou_slide`
 * @param sortare      "slide" | "nume" | "tot"
 * @param secunde      de câte secunde e slide-ul pe ecran, sau null
 * @param totalSarcini câte sarcini are lecția, pentru coloana „toată ora"
 */
/**
 * @param nume  true pe al doilea ecran (tabelul cu cine ce a ales), false în
 *              sertar, care se deschide peste proiector și n-are voie cu nume.
 */
export function randeaza({ slide, sarcini = [], randuri = [], sortare = "slide",
                           secunde = null, totalSarcini = null, nume = true }){
  const intrebari = sarcini.filter(x => x.fel === "verificare" && x.q);
  const cate = numara(randuri);
  const total = randuri.length;
  const trimis = total - cate.nefacut;

  /* Fără nume: ce vede clasa pe proiector. Doar cifre agregate: câți au
     trimis și, la fiecare întrebare, câți au ales fiecare variantă. Niciun
     text pentru profesor, nimic despre cine. */
  if (!nume){
    const dist = intrebari.filter(q => Array.isArray(q.optiuni)).map(q => {
      const n = q.optiuni.map(() => 0);
      randuri.forEach(x => {
        if (x.ales == null) return;
        const aici = x.ales_la ? x.ales_la === q.id : intrebari.length === 1;
        if (aici && n[x.ales] != null) n[x.ales]++;
      });
      return { q, n };
    });
    return `<div class="pv pv--anonim">
      <div class="pv__st">${inel(cate, trimis, total)}</div>
      <div class="pv__dr">${dist.length ? dist.map(({ q, n }) => {
        const tot = n.reduce((a, b) => a + b, 0);
        return `<p class="pv__q">${q.q}</p>
          <div class="pv-dist">${q.optiuni.map((o, k) => `
            <div class="pv-dist__r"><span class="pv-dist__t">${o}</span>
              <span class="pv-dist__b"><i style="width:${tot ? Math.round(100 * n[k] / tot) : 0}%"></i></span>
              <b>${n[k]}</b></div>`).join("")}</div>`;
      }).join("") : `<p class="pv__q">${slide?.titlu || ""}</p>
          <p class="pv-mare"><b>${trimis}</b> din ${total} au trimis</p>`}</div>
    </div>`;
  }

  return `<div class="pv">
    <div class="pv__st">
      <p class="pv__n">slide-ul de pe ecran${secunde != null ? " · " + ceasText(secunde) : ""}</p>
      <p class="pv__q">${slide?.titlu || "—"}</p>
      ${sarcini.length
        ? inel(cate, trimis, total)
        : `<div class="pv-gol">Slide-ul ăsta n-are nimic de trimis.<br>
             Doar îl arăți și vorbești.</div>`}
    </div>
    <div class="pv__dr">
      ${intrebari.length === 1
        ? `<p class="pv__n">întrebarea de pe ecran</p><p class="pv__q">${intrebari[0].q}</p>`
        : intrebari.length > 1
          ? `<p class="pv__n">${intrebari.length} întrebări pe slide</p>
             <p class="pv__q">${intrebari.map(i => i.q).join(" &nbsp;·&nbsp; ")}</p>`
          : ""}
      ${tabel(randuri, intrebari, sortare, totalSarcini)}
    </div>
  </div>`;
}

/** Leagă butoanele de sortare dintr-o vedere deja desenată. */
export function legaSortarea(gazda, laSchimbare){
  gazda.querySelectorAll("[data-sort]").forEach(b =>
    b.addEventListener("click", () => laSchimbare(b.dataset.sort)));
}
