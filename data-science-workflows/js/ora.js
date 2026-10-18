/* ===========================================================================
   ORA, CA OBIECT

   Un singur loc din care se vorbește cu ședințele. Paginile de predare și
   pagina lecției cer de aici, nu scriu RPC-uri de mână.

   O ședință e o oră anume: lecția, grupa, ziua, modul, ora de început și cea
   de sfârșit. Tot ce fac studenții în timpul ei se leagă de ea, iar din asta
   ies prezența, raportul, exportul și ștergerea.

   Dacă baza nu are încă tabelele din db/14 și db/15, funcțiile de aici
   întorc null sau o listă goală. Nimic nu aruncă și nicio pagină nu se rupe:
   doar nu se vede nimic, ceea ce e adevărul.
   =========================================================================== */

import { sb } from "./auth.js?v=46";
import { RADACINA } from "./curs.js?v=46";

/* Ultima eroare de la bază, ca paginile să poată spune ADEVĂRUL.

   Fără ea, o funcție care lipsește din bază arăta pe ecran ca „codul nu e
   bun". Omul schimbă codul de trei ori, se enervează, și de fapt problema era
   că n-a rulat un fișier SQL. Un mesaj greșit costă mai mult decât niciunul. */
let eroare = null;
export function ultimaEroare(){ return eroare; }

/** Adevărat dacă baza nu are încă funcțiile din db/14 și db/15. */
export function lipsesteBaza(){
  const m = (eroare || "").toLowerCase();
  return m.includes("could not find the function")
      || m.includes("schema cache")
      || m.includes("does not exist")
      || m.includes("pgrst202");
}

/** Cheamă o funcție din bază și întoarce null în loc să arunce. */
async function cheama(nume, argumente = {}) {
  try {
    const { data, error } = await sb.rpc(nume, argumente);
    if (error) { eroare = error.message; console.warn(`[ora] ${nume}:`, error.message); return null; }
    eroare = null;
    return data;
  } catch (e) { eroare = e.message; console.warn(`[ora] ${nume}:`, e.message); return null; }
}

/* --- grupe ---------------------------------------------------------------- */

export async function grupe() {
  try {
    const { data } = await sb.from("grupe").select("*").order("nume");
    return data || [];
  } catch { return []; }
}

export const puneGrupa = (id, nume, an, zi, ora) =>
  cheama("pune_grupa", { p_id:id, p_nume:nume, p_an:an, p_zi:zi, p_ora:ora });

/* --- ședința, la profesor ------------------------------------------------- */

/** O oră deschisă de mai mult de 3 ore e o oră uitată: se închide singură.
    Aceeași regulă stă și în bază (db/17); aici e pentru cine n-a rulat-o. */
export const ORE_MAX = 3;
export function prea_veche(s) {
  if (!s) return false;
  const min = Number.isFinite(s.minute) ? s.minute
    : s.deschisa_la ? (Date.now() - new Date(s.deschisa_la)) / 60000 : 0;
  return min > ORE_MAX * 60;
}

/** Ora deschisă acum, sau null. */
export async function deschisa(capitol = null) {
  const r = await cheama("sedinta_deschisa", { p_capitol: capitol });
  return (r && r[0]) || null;
}

/** Deschide ora. Grupa se alege singură: dacă ai una, e aia; dacă n-ai
    niciuna, se face „Grupa 1" pe loc.

    Înainte, lipsa grupei oprea pornirea orei și te trimitea la un formular cu
    trei câmpuri — adică stăteai în fața clasei și completai un formular. Grupa
    e o etichetă pentru statistici; se poate redenumi oricând, pe urmă. */
export async function deschide(capitol, grupaId = null, mod = "live", total = null) {
  if (!grupaId) {
    const gr = await grupe();
    if (gr.length === 1) grupaId = gr[0].id;
    else if (!gr.length) {
      const f = await cheama("pune_grupa", { p_id:"g1", p_nume:"Grupa 1",
        p_an:String(new Date().getFullYear()), p_zi:null, p_ora:null });
      if (f?.ok) grupaId = "g1";
    }
  }
  return cheama("deschide_sedinta", { p_capitol:capitol, p_grupa_id:grupaId,
                                      p_mod:mod, p_total_nr:total });
}

export const pune = (id, { slide = null, mod = null, note = null } = {}) =>
  cheama("pune_sedinta", { p_id:id, p_slide_nr:slide, p_mod:mod, p_note:note });

export const inchide  = id => cheama("inchide_sedinta", { p_id:id });
export const raport   = id => cheama("raport_sedinta", { p_id:id });
export const sumar    = id => cheama("sumar_sedinta", { p_id:id });
export const arhiveaza = (id, inapoi = false) =>
  cheama("arhiveaza_sedinta", { p_id:id, p_inapoi:inapoi });
export const lista = (arhivate = false, capitol = null) =>
  cheama("lista_sedinte", { p_arhivate:arhivate, p_capitol:capitol });
export const punePrezenta = (sedinta, matricol, prezent) =>
  cheama("pune_prezenta", { p_sedinta:sedinta, p_matricol:matricol, p_prezent:prezent });

/** Un rând per student, pentru sarcinile de pe slide-ul care e pe ecran. */
export const panou = (sedinta, sarcini) =>
  cheama("panou_slide", { p_sedinta:sedinta, p_sarcini:sarcini || [] });

/* --- intrarea, la student ------------------------------------------------- */

export const dupaCod     = cod => cheama("sedinta_dupa_cod", { p_cod:cod });
export const listaGrupei = cod => cheama("lista_grupei", { p_cod:cod });
export const intra       = (cod, cheie) =>
  cheama("intra_in_sedinta", { p_cod:cod, p_cheie:cheie });

/** Ce trebuie să știe pagina lecției: e ora pornită, în ce mod, la ce slide. */
export const acum = capitol => cheama("ora_acum", { p_capitol:capitol });

/* --- ce lecții se văd ------------------------------------------------------
   Studentul vede doar lecțiile pe care le-ai predat deja. Nu e o chestiune de
   secret, e una de ordine: cursul se desfășoară în timp, iar opt lecții puse
   toate deodată în față, dintre care trei sunt schelete, spun „ai rămas în
   urmă" cuiva care e exact la zi. */

/** Capitolele care au avut cel puțin o ședință, sau `null` dacă nu pot afla.

    `null` înseamnă „nu filtra". Dacă baza nu răspunde, sau cine se uită nu e
    autentificat, se vede tot cursul. O pagină goală din cauza rețelei ar fi
    mai rea decât o lecție văzută prea devreme. */
export async function predate() {
  try {
    /* doar orele adevărate: o oră de test o arhivezi din „Ședințele” și
       lecția nu mai apare ca predată */
    const { data, error } = await sb.from("sedinte").select("capitol").is("arhivata_la", null);
    if (error) return null;
    return new Set((data || []).map(r => r.capitol));
  } catch { return null; }
}

/** Lecțiile pe care are voie să le vadă cine se uită acum. Profesorul le vede
    pe toate; studentul, doar pe cele predate. */
export async function lectiiVizibile(lectii, profesor) {
  if (profesor) return lectii;
  const p = await predate();
  if (!p) return lectii;
  return lectii.filter(l => p.has("c" + l.nr));
}

/* --- harta slide-urilor --------------------------------------------------- */

const harti = new Map();

/** Ce sarcini stau pe fiecare slide, cu întrebarea și variantele ei. */
export async function harta(capitol) {
  if (harti.has(capitol)) return harti.get(capitol);
  try {
    const r = await fetch(`${RADACINA}/date/harta-${capitol}.json?v=46`);
    const h = r.ok ? await r.json() : null;
    harti.set(capitol, h);
    return h;
  } catch { harti.set(capitol, null); return null; }
}

/** Sarcinile de pe un slide anume (1-based), din hartă. */
export function sarciniDe(h, nr) {
  if (!h) return [];
  const s = (h.slide || []).find(x => x.nr === nr);
  return s ? s.sarcini : [];
}

/* --- cuvinte -------------------------------------------------------------- */

/** Cele patru stări, cu glif și nume. Forma poartă informația, culoarea doar
    o întărește: se citesc și pe un proiector decolorat, și alb-negru. */
export const STARI = {
  trecut:        { glif:"✓", nume:"corect",     clasa:"g--ok"  },
  trimis_gresit: { glif:"✕", nume:"greșit",     clasa:"g--nu"  },
  trimis_gol:    { glif:"◉", nume:"trimis gol", clasa:"g--gol" },
  nefacut:       { glif:"○", nume:"n-a trimis", clasa:"g--nim" }
};

export const ORDINEA = ["trecut", "trimis_gresit", "trimis_gol", "nefacut"];

/** „acum 3 minute", „acum o oră”. */
export function deCand(t) {
  if (!t) return "—";
  const m = Math.round((Date.now() - new Date(t).getTime()) / 60000);
  if (m < 1) return "acum";
  if (m < 60) return `acum ${m} min`;
  const h = Math.round(m / 60);
  return h === 1 ? "acum o oră" : `acum ${h} ore`;
}
