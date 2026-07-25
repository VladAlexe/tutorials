/* cod_parametri.js — bloc de cod Python în care se schimbă câteva valori din
   controale, cu ieșirea care se actualizează. Codul rămâne lizibil, nu devine
   formular. Valorile ies din eșantionul local wb-data.json. */

import { incarcaDate, esc } from "./date.js";

export default async function codParametri(gazda, parametri = {}) {
  const data = await incarcaDate(parametri.sursa || "wb-data.json");
  const ani = data.ani;

  const st = { tara: "ro", indicator: data.indicatori[0].cod, an: ani[ani.length - 1] };

  gazda.innerHTML = `
    <div class="ctrl">
      <label>tara
        <select id="p-tara">${data.tari.map((t) => `<option value="${t.cod}">${t.cod}</option>`).join("")}</select>
      </label>
      <label>indicator
        <select id="p-ind">${data.indicatori.map((i) => `<option value="${i.cod}">${i.cod}</option>`).join("")}</select>
      </label>
      <label>an
        <select id="p-an">${ani.map((a) => `<option ${a === st.an ? "selected" : ""}>${a}</option>`).join("")}</select>
      </label>
    </div>
    <div class="resp" id="p-cod" style="max-height:none"></div>
    <p class="c2__tag" style="margin:12px 0 4px">Ieșire</p>
    <div class="resp" id="p-out" style="max-height:none"></div>`;

  const elCod = gazda.querySelector("#p-cod");
  const elOut = gazda.querySelector("#p-out");

  function valoare() {
    const v = (data.valori[`${st.tara}|${st.indicator}`] || {})[st.an];
    return v === undefined || v === null ? "None" : String(v);
  }

  function deseneaza() {
    const V = (s) => `<span class="js">"${esc(s)}"</span>`;
    elCod.innerHTML =
`<span class="c">import requests</span>

<span class="jk">def</span> adu(tara, indicator, an):
    url = <span class="js">f"https://api.worldbank.org/v2/country/{tara}/indicator/{indicator}"</span>
    r = requests.get(url, params={<span class="js">"date"</span>: an, <span class="js">"format"</span>: <span class="js">"json"</span>}, timeout=<span class="jn">30</span>)
    r.raise_for_status()
    date = r.json()[<span class="jn">1</span>]            <span class="c"># al doilea element = datele</span>
    <span class="jk">return</span> date[<span class="jn">0</span>][<span class="js">"value"</span>] <span class="jk">if</span> date <span class="jk">else</span> <span class="jb">None</span>

print(adu(${V(st.tara)}, ${V(st.indicator)}, ${V(st.an)}))`;
    const val = valoare();
    elOut.innerHTML = val === "None"
      ? `<span class="jb">None</span>   <span class="c"># valoare lipsă pentru această combinație</span>`
      : `<span class="jn">${esc(val)}</span>`;
  }

  gazda.querySelector("#p-tara").addEventListener("change", (e) => { st.tara = e.target.value; deseneaza(); });
  gazda.querySelector("#p-ind").addEventListener("change", (e) => { st.indicator = e.target.value; deseneaza(); });
  gazda.querySelector("#p-an").addEventListener("change", (e) => { st.an = e.target.value; deseneaza(); });

  deseneaza();
}
