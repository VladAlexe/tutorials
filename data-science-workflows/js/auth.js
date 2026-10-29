/* ===========================================================================
   Autentificare si profil

   Un singur loc din care se afla cine e conectat. Restul paginilor cer de
   aici, nu vorbesc direct cu Supabase.
   =========================================================================== */

import { createClient } from "./vendor/supabase-js-2.117.0.js";   /* găzduită aici: nicio cerere la un CDN străin */
import { SUPABASE_URL, SUPABASE_ANON, ADRESA_RETUR } from "./supabase-config.js?v=100";

/* --- sesiunea expirată ---------------------------------------------------
   Jetonul de acces (JWT) expiră după o oră și biblioteca îl reînnoiește
   singură. Dacă reînnoirea ratează (laptop adormit, ceasul calculatorului
   dat greșit), baza de date răspunde „JWT expired” la fiecare cerere și
   contul pare blocat. De aceea, la un astfel de răspuns: o reînnoire, apoi
   aceeași cerere încă o dată. Dacă nici reînnoirea nu merge, sesiunea se
   închide pe acest calculator, iar pagina cere din nou intrarea.
   ------------------------------------------------------------------------- */

const JWT_EXPIRAT = /jwt expired|PGRST303/i;

async function fetchCuReinnoire(intrare, init = {}) {
  const r = await fetch(intrare, init);
  if (r.status !== 401) return r;
  const adresa = String(intrare?.url ?? intrare);
  if (!adresa.includes("/rest/v1/")) return r;          /* doar baza de date, nu autentificarea */
  let corp = "";
  try { corp = await r.clone().text(); } catch {}
  if (!JWT_EXPIRAT.test(corp)) return r;
  const { data, error } = await sb.auth.refreshSession().catch(e => ({ error: e }));
  if (error || !data?.session) {
    profilCache = null;
    await sb.auth.signOut({ scope: "local" }).catch(() => {});
    return r;
  }
  const antete = new Headers(init.headers);
  antete.set("Authorization", `Bearer ${data.session.access_token}`);
  return fetch(intrare, { ...init, headers: antete });
}

export const sb = createClient(SUPABASE_URL, SUPABASE_ANON, {
  auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: true },
  global: { fetch: fetchCuReinnoire }
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
  /* dacă serverul nu confirmă ieșirea (sesiune deja expirată), se închide
     măcar sesiunea de pe acest calculator */
  const { error } = await sb.auth.signOut().catch(e => ({ error: e }));
  if (error) await sb.auth.signOut({ scope: "local" }).catch(() => {});
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

/* Modul „vezi ca student” a fost scos: făcea situl jumătate profesor,
   jumătate student, și părea că ai două conturi. Ce văd ei se vede dintr-o
   fereastră privată. Cheia veche se șterge, ca să nu rămână nimeni prins. */
try { localStorage.removeItem(CHEIE_MOD); } catch {}
export function modVizualizare() { return "profesor"; }

export function setModVizualizare(mod) {
  try {
    localStorage.removeItem(CHEIE_MOD);
  } catch {}
  profilCache = null;
}

/* --- profil -------------------------------------------------------------- */

let profilCache = null;

/** { autentificat, matricol, nume, grupa, github_login, profesor } */
export async function profil({ proaspat = false } = {}) {
  if (profilCache && !proaspat) return profilCache;
  /* Dacă autentificarea nu răspunde (rețea proastă, filă blocată), nu ținem
     pagina în loc la nesfârșit: după 8 secunde, eroare, pe care paginile o
     tratează ca „fără cont deocamdată”. */
  const termen = ms => new Promise((_, r) => setTimeout(() => r(new Error("Serviciul de autentificare nu răspunde.")), ms));
  const { data: { session } } = await Promise.race([sb.auth.getSession(), termen(8000)]);
  if (!session) {
    profilCache = { autentificat: false };
    return profilCache;
  }
  const { data, error } = await Promise.race([sb.rpc("profilul_meu"), termen(8000)]);
  /* „JWT expired” ajunge aici doar dacă reînnoirea a eșuat și sesiunea s-a
     închis: pagina arată din nou intrarea, nu o eroare fără ieșire */
  if (error && JWT_EXPIRAT.test(`${error.code} ${error.message}`)) {
    profilCache = { autentificat: false, expirat: true };
    return profilCache;
  }
  if (error) throw new Error(traduEroare(error.message));

  /* anonim = invitat; un cont GitHub fără nume legat are anonim false și matricol null */
  const p = { ...data, email: session.user.email, anonim: !!session.user.is_anonymous };
  p.profesorReal = !!p.profesor;
  if (p.profesorReal && modVizualizare() === "student") p.profesor = false;

  profilCache = p;
  return profilCache;
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
    return "Prea multe încercări. Încearcă din nou peste un minut.";
  if (t.includes("invalid") && t.includes("email"))
    return "Adresa de e-mail nu este validă.";
  if (t.includes("jwt expired"))
    return "Sesiunea a expirat. Ieși din cont și intră din nou.";
  if (t.includes("failed to fetch") || t.includes("network"))
    return "Serverul nu poate fi contactat. Verifică conexiunea la internet.";
  if (t.includes("not found") && t.includes("function"))
    return "Baza de date nu este configurată complet. Rulează fișierele din db/.";
  if (t.includes("anonymous") && t.includes("disabled"))
    return "Intrarea ca invitat nu este activată. În Supabase: Authentication, " +
           "Sign In / Providers, Anonymous sign-ins.";
  return m;
}
