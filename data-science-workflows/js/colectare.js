/* ===========================================================================
   COLECTAREA RĂSPUNSURILOR

   Se ocupă de trei lucruri: marchează slide-ul ca parcurs, salvează răspunsul
   la o verificare, salvează o rulare de cod.

   Două reguli de care depinde tot restul:

   1. Dacă studentul nu e autentificat, nu salvează nimic și nu se plânge.
      Lecția funcționează la fel și fără cont.

   2. Autentificarea se încarcă leneș, cu import dinamic. auth.js aduce
      biblioteca Supabase de pe un CDN; dacă rețeaua aceea e lentă sau blocată,
      un import static ar dărâma și verificările și rulatorul de slide-uri.
      Așa, lecția rămâne întreagă și doar salvarea lipsește.
   =========================================================================== */

let modul = null;   /* null = neîncercat, false = indisponibil, altfel modulul */
let gata  = null;   /* null = neștiut, true/false = poate salva sau nu */

/* De unde vine ce se salvează. Pagina o spune, o dată, cu setContext():
     'live'    — în oră, cât ora e condusă de profesor
     'lectie'  — pe pagina lecției, dar singur
     'manual'  — în tutorial, oricând
   Fără ea, rândul rămâne cu null și apare la profesor ca „necunoscut".
   Nu e un amănunt: un exercițiu făcut în oră și unul făcut marți seara spun
   lucruri diferite, iar panoul trebuie să le poată deosebi. */
let contextul = null;
export function setContext(c){ contextul = c || null; }
export function context(){ return contextul; }

/* De care oră ține ce se salvează. Pagina lecției o află din `ora_acum` și o
   pune aici. `null` înseamnă „a lucrat singur, în afara orei", și din diferența
   asta ies și prezența, și regula de notare: în ședință punct întreg, singur
   acasă jumătate, la prima completare. Nu e o etichetă scrisă de client, ca
   `context`, e o legătură adevărată către un rând din `sedinte`. */
let sedinta = null;
export function setSedinta(id){ sedinta = id || null; }
export function sedintaAcum(){ return sedinta; }

async function autentificare(){
  if (modul !== null) return modul;
  try { modul = await import("./auth.js?v=83"); }
  catch { modul = false; }
  return modul;
}

async function pregatit(){
  if (gata !== null) return gata;
  const a = await autentificare();
  if (!a){ gata = false; return gata; }
  try {
    const p = await a.profil();
    gata = !!(p.autentificat && p.matricol);
  } catch { gata = false; }
  return gata;
}

/** Utilizatorul curent, sau null. */
async function cine(){
  if (!await pregatit()) return null;
  const a = await autentificare();
  const { data:{ user } } = await a.sb.auth.getUser();
  return user ? { user, sb:a.sb } : null;
}

export async function marcheazaSectiune(sectiuneId){
  const c = await cine();
  if (!c) return false;
  const { error } = await c.sb.from("progres").upsert(
    { user_id:c.user.id, sectiune_id:sectiuneId, ultima_data:new Date().toISOString() },
    { onConflict:"user_id,sectiune_id" }
  );
  return !error;
}

export async function salveazaRaspuns({ intrebareId, capitol, raspuns, corect }){
  const c = await cine();
  if (!c) return false;
  const { error } = await c.sb.from("raspunsuri").insert({
    user_id:c.user.id, intrebare_id:intrebareId, capitol, raspuns, corect,
    context: contextul, sedinta_id: sedinta
  });
  return !error;
}

export async function salveazaCod({ exercitiuId, cod, trecut }){
  if (globalThis.dswFaraPoarta?.has(exercitiuId)) return false;   /* de încercat, nu sarcină */
  const c = await cine();
  if (!c) return false;
  const { error } = await c.sb.from("rulari_cod").insert({
    user_id:c.user.id, exercitiu_id:exercitiuId, cod:(cod||"").slice(0,4000), trecut,
    context: contextul, sedinta_id: sedinta
  });
  return !error;
}

/** Răspunsurile deja date la această lecție, ca să nu reîntrebăm. */
/** La care întrebări din lecție a mai răspuns cândva. Doar id-urile.

    Înainte exista `raspunsuriDate`, care aducea și ce a ales, și dacă a
    nimerit, ca să le pună înapoi pe ecran. Asta strica ora: veneau la clasă și
    vedeau deja bifat de acasă. Acum fiecare deschidere a lecției e o încercare
    nouă, iar din bază se află doar că a mai trecut pe aici. */
export async function aMaiRaspuns(capitol){
  const c = await cine();
  if (!c) return new Set();
  const { data } = await c.sb.from("raspunsuri")
    .select("intrebare_id").eq("capitol", capitol);
  return new Set((data||[]).map(r => r.intrebare_id));
}
