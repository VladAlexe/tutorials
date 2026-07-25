/* ramuri.js — graf de commituri (SVG) care se construiește pe măsură ce dai
   comenzi. Se vede punctul de ramificare, commiturile pe fiecare ramură și unde
   te afli (HEAD). Comanda și efectul, deodată. Fără biblioteci, fără rețea. */

const LANE = { main: 0, feature: 1 };
const COL = { 0: "#8D9472", 1: "#8FA9C4" };

export default function ramuri(gazda, parametri = {}) {
  let ord = 0;
  const hexId = () => Math.random().toString(16).slice(2, 8);
  const first = { id: hexId(), lane: 0, order: ord++, parents: [], branch: "main" };
  const commits = [first];
  const branches = { main: first };
  let head = "main";
  let jurnal = ['comit inițial pe main'];

  const tip = () => branches[head];
  const x = (o) => 46 + o * 74;
  const y = (l) => 44 + l * 66;

  function svg() {
    const maxO = Math.max(...commits.map((c) => c.order));
    const W = Math.max(360, x(maxO) + 90), H = y(1) + 40;
    let lines = "", nodes = "";
    commits.forEach((c) => {
      c.parents.forEach((p) => {
        lines += `<path d="M ${x(p.order)} ${y(p.lane)} L ${x(c.order)} ${y(c.lane)}" stroke="#5C6165" stroke-width="2.5" fill="none"/>`;
      });
    });
    commits.forEach((c) => {
      const isTip = (branches.main === c || (branches.feature && branches.feature === c));
      const isHead = tip() === c;
      nodes += `<circle cx="${x(c.order)}" cy="${y(c.lane)}" r="12" fill="${COL[c.lane]}" stroke="${isHead ? "#E8E8E4" : "#16181A"}" stroke-width="${isHead ? 3.5 : 1.5}"/>`;
      nodes += `<text x="${x(c.order)}" y="${y(c.lane) + 4}" text-anchor="middle" font-size="9" fill="#15170F">${c.id.slice(0, 4)}</text>`;
      if (isTip) {
        const bname = branches.main === c ? "main" : "feature";
        nodes += `<text x="${x(c.order)}" y="${y(c.lane) - 20}" text-anchor="middle" font-size="10" fill="#DADAD6" font-weight="700">${bname}${isHead ? " ←HEAD" : ""}</text>`;
      }
    });
    return `<svg class="gg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" role="img" aria-label="Graf de commituri">${lines}${nodes}</svg>`;
  }

  function actualizeaza() {
    gazda.querySelector("#r-graf").innerHTML = svg();
    gazda.querySelector("#r-graf").scrollLeft = 9999;
    gazda.querySelector("#r-jurnal").innerHTML = jurnal.map((l) => `<div><span class="pr">$</span> ${l}</div>`).join("");
    const has = !!branches.feature;
    gazda.querySelector("#b-crea").disabled = has;
    gazda.querySelector("#b-feat").disabled = !has || head === "feature";
    gazda.querySelector("#b-main").disabled = head === "main";
    gazda.querySelector("#b-merge").disabled = !has || head !== "main" || branches.main === branches.feature;
  }

  gazda.innerHTML = `
    <div class="gg-wrap" id="r-graf"></div>
    <div class="filters">
      <button class="fbtn" id="b-commit">git commit</button>
      <button class="fbtn" id="b-crea">git switch -c feature</button>
      <button class="fbtn" id="b-feat">git switch feature</button>
      <button class="fbtn" id="b-main">git switch main</button>
      <button class="fbtn" id="b-merge">git merge feature</button>
      <button class="btn btn--ghost" id="b-reset">reset</button>
    </div>
    <div class="resp" id="r-jurnal" style="max-height:120px;font-size:12px"></div>`;

  const on = (id, fn) => gazda.querySelector(id).addEventListener("click", fn);

  on("#b-commit", () => {
    const c = { id: hexId(), lane: LANE[head], order: ord++, parents: [tip()], branch: head };
    commits.push(c); branches[head] = c; jurnal.push(`git commit  (pe ${head})`); actualizeaza();
  });
  on("#b-crea", () => {
    branches.feature = branches.main; head = "feature";
    jurnal.push("git switch -c feature  → ramură nouă din main"); actualizeaza();
  });
  on("#b-feat", () => { head = "feature"; jurnal.push("git switch feature"); actualizeaza(); });
  on("#b-main", () => { head = "main"; jurnal.push("git switch main"); actualizeaza(); });
  on("#b-merge", () => {
    const c = { id: hexId(), lane: 0, order: ord++, parents: [branches.main, branches.feature], branch: "main" };
    commits.push(c); branches.main = c;
    jurnal.push("git merge feature  → commit de îmbinare pe main"); actualizeaza();
  });
  on("#b-reset", () => {
    ord = 0; const f = { id: hexId(), lane: 0, order: ord++, parents: [], branch: "main" };
    commits.length = 0; commits.push(f); branches.main = f; delete branches.feature; head = "main";
    jurnal = ["comit inițial pe main"]; actualizeaza();
  });

  actualizeaza();
}
