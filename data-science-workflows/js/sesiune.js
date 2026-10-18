/* ===========================================================================
   SESIUNEA DE LUCRU

   Spune bazei de date, din 20 în 20 de secunde, că studentul e încă în lecție
   și pe ce slide se află. De aici se alimentează panoul de clasă.

   Trei lucruri de care depinde să fie util la oră:

   1. Nu blochează nimic. Dacă nu există cont, dacă Supabase nu răspunde, dacă
      rețeaua pică, lecția merge mai departe neschimbată și nu apare nicio
      eroare pe ecranul studentului.

   2. Se oprește când fila nu e vizibilă, ca să nu arate 25 de studenți
      „în lecție" când de fapt și-au lăsat laptopul deschis la altceva.

   3. Jurnalul e separat de bătaia de inimă. Sesiunea se rescrie mereu, deci
      arată doar prezentul; evenimentele se adaugă și rămân, deci reconstituie
      ora și după ce toată lumea a închis laptopul.
   =========================================================================== */

const RITM = 20000;        /* bătaia de inimă */
const RITM_LENT = 60000;   /* când fila e în fundal, dar încă deschisă */

let sb = null, pornit = false, idSesiune = null, ceas = null;
let curent = { capitol:null, slide:null, slide_nr:null, total_nr:null };

async function conecteaza(){
  if (sb) return sb;
  try {
    const m = await import("./auth.js?v=39");
    const p = await m.profil();
    if (!p.autentificat) return null;
    sb = m.sb;
    return sb;
  } catch { return null; }
}

async function bate(){
  const c = await conecteaza();
  if (!c) return;
  try {
    const { data, error } = await c.rpc("bate", {
      p_sesiune: idSesiune,
      p_capitol: curent.capitol,
      p_slide: curent.slide,
      p_slide_nr: curent.slide_nr,
      p_total_nr: curent.total_nr
    });
    if (!error && data) idSesiune = data;
  } catch { /* fără rețea, sesiunea pur și simplu nu se mai vede ca activă */ }
}

function programeaza(){
  clearTimeout(ceas);
  const t = document.visibilityState === "visible" ? RITM : RITM_LENT;
  ceas = setTimeout(async () => { if (pornit){ await bate(); programeaza(); } }, t);
}

/** Pornește urmărirea sesiunii pentru o lecție. Se cheamă o dată. */
export function porneste({ capitol, total }){
  if (pornit) return;
  pornit = true;
  curent.capitol = capitol;
  curent.total_nr = total ?? null;

  bate();
  programeaza();

  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible") bate();
    programeaza();
  });

  /* la închiderea filei, o ultimă bătaie, trimisă în fundal */
  addEventListener("pagehide", () => { pornit = false; clearTimeout(ceas); }, { once:true });
}

/** Studentul a ajuns pe alt slide. Scrie și în sesiune, și în jurnal. */
export function laSlide({ slide, nr, total }){
  curent.slide = slide;
  curent.slide_nr = nr ?? null;
  if (total) curent.total_nr = total;
  bate();
  jurnal("slide", { slide, nr });
}

/** Un eveniment care merită păstrat. Nu se șterge la resetarea progresului. */
export async function jurnal(tip, detalii = {}){
  const c = await conecteaza();
  if (!c) return;
  try {
    const { data:{ user } } = await c.auth.getUser();
    if (!user) return;
    await c.from("evenimente").insert({
      user_id: user.id,
      sesiune: idSesiune,
      tip,
      capitol: curent.capitol,
      slide: curent.slide,
      slide_nr: curent.slide_nr,
      detalii
    });
  } catch { /* jurnalul e util, nu indispensabil */ }
}
