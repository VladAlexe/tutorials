/* ===========================================================================
   Colectarea raspunsurilor

   Se ocupa de trei lucruri: marcheaza secțiunea ca parcursa, salveaza
   raspunsul la o verificare, salveaza o rulare de cod.

   Daca studentul nu e autentificat, nu salveaza nimic si nu se plange:
   lectia functioneaza la fel si fara cont. Nimic nu blocheaza cititul.
   =========================================================================== */

import { sb, profil } from "./auth.js?v=3";

let gata = null;

async function pregatit(){
  if (gata !== null) return gata;
  try {
    const p = await profil();
    gata = !!(p.autentificat && p.matricol);
  } catch { gata = false; }
  return gata;
}

export async function marcheazaSectiune(sectiuneId){
  if (!await pregatit()) return;
  const { data:{ user } } = await sb.auth.getUser();
  if (!user) return;
  await sb.from("progres").upsert(
    { user_id:user.id, sectiune_id:sectiuneId, ultima_data:new Date().toISOString() },
    { onConflict:"user_id,sectiune_id" }
  );
}

export async function salveazaRaspuns({ intrebareId, capitol, raspuns, corect }){
  if (!await pregatit()) return false;
  const { data:{ user } } = await sb.auth.getUser();
  if (!user) return false;
  const { error } = await sb.from("raspunsuri").insert({
    user_id:user.id, intrebare_id:intrebareId, capitol, raspuns, corect
  });
  return !error;
}

export async function salveazaCod({ exercitiuId, cod, trecut }){
  if (!await pregatit()) return false;
  const { data:{ user } } = await sb.auth.getUser();
  if (!user) return false;
  const { error } = await sb.from("rulari_cod").insert({
    user_id:user.id, exercitiu_id:exercitiuId, cod:(cod||"").slice(0,4000), trecut
  });
  return !error;
}

/** Raspunsurile deja date la aceasta lectie, ca sa nu reintrebam. */
export async function raspunsuriDate(capitol){
  if (!await pregatit()) return new Map();
  const { data } = await sb.from("raspunsuri")
    .select("intrebare_id, raspuns, corect").eq("capitol", capitol);
  return new Map((data||[]).map(r => [r.intrebare_id, r]));
}
