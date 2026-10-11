/* ===========================================================================
   Autentificare si profil

   Un singur loc din care se afla cine e conectat. Restul paginilor cer de
   aici, nu vorbesc direct cu Supabase.
   =========================================================================== */

import { createClient } from "https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.117.0/+esm";
import { SUPABASE_URL, SUPABASE_ANON, ADRESA_RETUR } from "./supabase-config.js?v=5";

export const sb = createClient(SUPABASE_URL, SUPABASE_ANON, {
  auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: true }
});

/* --- diagnostic ----------------------------------------------------------
   Ce a venit inapoi in adresa dupa autentificare. Il citim INAINTE ca
   biblioteca sa curete adresa, ca sa putem spune ce s-a intamplat cand ceva
   nu merge. Nu pastram valorile jetoanelor, doar numele parametrilor.
   ------------------------------------------------------------------------- */

export const intoarcere = (() => {
  const h = new URLSearchParams(location.hash.replace(/^#/, ""));
  const q = new URLSearchParams(location.search);
  const chei = [...new Set([...h.keys(), ...q.keys()])];
  return {
    chei,
    areJeton: h.has("access_token") || q.has("code"),
    eroare: h.get("error") || q.get("error") || null,
    descriere: h.get("error_description") || q.get("error_description") || null
  };
})();

/* --- intrare ------------------------------------------------------------- */

export async function intraCuEmail(email) {
  const { error } = await sb.auth.signInWithOtp({
    email: email.trim(),
    options: { emailRedirectTo: ADRESA_RETUR }
  });
  if (error) throw new Error(traduEroare(error.message));
  return true;
}

export async function intraCuGithub() {
  const { error } = await sb.auth.signInWithOAuth({
    provider: "github",
    options: { redirectTo: ADRESA_RETUR }
  });
  if (error) throw new Error(traduEroare(error.message));
}

export async function iesi() {
  await sb.auth.signOut();
  profilCache = null;
}

/* --- intrare ca invitat --------------------------------------------------
   Pentru teste, pentru cineva care intra prin QR la oră, sau pentru un
   student care încă nu are cont de GitHub. Creează un cont anonim real în
   Supabase, deci progresul lui se salvează și se vede în panoul de clasă,
   dar nu are email și nu e legat de un număr matricol din listă.

   Cere ca „Anonymous sign-ins” să fie pornit în Supabase:
     Authentication → Sign In / Providers → Anonymous sign-ins
   ------------------------------------------------------------------------- */

export async function intraCaInvitat(nume) {
  const { error } = await sb.auth.signInAnonymously();
  if (error) throw new Error(traduEroare(error.message));
  const { data, error: e2 } = await sb.rpc("intra_ca_invitat", {
    p_nume: (nume || "").trim() || null
  });
  if (e2) throw new Error(traduEroare(e2.message));
  profilCache = null;
  return data;   // { ok, matricol, nume }
}

/** Invitat = cont anonim, fără email, cu matricol care începe cu G-. */
export const esteInvitat = p => !!(p && p.matricol && String(p.matricol).startsWith("G-"));

/* --- mod de vizualizare --------------------------------------------------
   Un profesor poate alege sa vada site-ul ca un student. Alegerea se
   pastreaza pentru tot site-ul, pe toate paginile, pana o schimba inapoi.

   ATENTIE: e o simulare a interfetei, nu a drepturilor. Baza de date stie in
   continuare ca esti profesor. Deci intrebarea "poate un student sa vada
   raspunsurile altuia" NU se testeaza asa; aceea se testeaza doar cu un cont
   care chiar e de student.
   ------------------------------------------------------------------------- */

const CHEIE_MOD = "dsw.mod";

export function modVizualizare() {
  try { return localStorage.getItem(CHEIE_MOD) === "student" ? "student" : "profesor"; }
  catch { return "profesor"; }
}

export function setModVizualizare(mod) {
  try {
    if (mod === "student") localStorage.setItem(CHEIE_MOD, "student");
    else localStorage.removeItem(CHEIE_MOD);
  } catch {}
  profilCache = null;
}

/* --- profil -------------------------------------------------------------- */

let profilCache = null;

/** { autentificat, matricol, nume, grupa, github_login, profesor } */
export async function profil({ proaspat = false } = {}) {
  if (profilCache && !proaspat) return profilCache;
  const { data: { session } } = await sb.auth.getSession();
  if (!session) {
    profilCache = { autentificat: false };
    return profilCache;
  }
  const { data, error } = await sb.rpc("profilul_meu");
  if (error) throw new Error(traduEroare(error.message));

  const p = { ...data, email: session.user.email };
  p.profesorReal = !!p.profesor;
  if (p.profesorReal && modVizualizare() === "student") p.profesor = false;

  profilCache = p;
  return profilCache;
}

export async function revendicaMatricol(matricol) {
  const { data, error } = await sb.rpc("revendica_matricol", { p_matricol: matricol });
  if (error) throw new Error(traduEroare(error.message));
  profilCache = null;
  return data;   // { ok, mesaj, nume }
}

export async function marcheazaPrezenta(jeton) {
  const { data, error } = await sb.rpc("marcheaza_prezenta", { p_jeton: jeton });
  if (error) throw new Error(traduEroare(error.message));
  return data;
}

/** Anunta pagina cand se schimba starea de autentificare. */
export function laSchimbare(cb) {
  sb.auth.onAuthStateChange(() => { profilCache = null; cb(); });
}

/* --- mesaje de eroare in romana ------------------------------------------ */

function traduEroare(m = "") {
  const t = m.toLowerCase();
  if (t.includes("rate limit") || t.includes("too many"))
    return "Prea multe incercari. Mai asteapta un minut.";
  if (t.includes("invalid") && t.includes("email"))
    return "Adresa de e-mail nu pare valida.";
  if (t.includes("failed to fetch") || t.includes("network"))
    return "Nu pot ajunge la server. Verifica legatura la internet.";
  if (t.includes("not found") && t.includes("function"))
    return "Baza de date nu e configurata complet. Ruleaza fisierele din db/.";
  if (t.includes("anonymous") && t.includes("disabled"))
    return "Intrarea ca invitat nu e pornita. In Supabase: Authentication, " +
           "Sign In / Providers, Anonymous sign-ins.";
  return m;
}
