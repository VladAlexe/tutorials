/* ==========================================================================
   progres.js — SINGURUL loc din care se citește și se scrie progresul.
   Restul codului nu atinge niciodată localStorage direct (verificabil printr-o
   căutare după „localStorage” în tot folderul js/ — trebuie să apară doar aici).

   Interfața stabilă, gândită ca peste ea să se poată pune mai târziu un cont și
   o bază de date fără a schimba restul aplicației:

     init(config)                         pregătește stratul; config.total = nr. de secțiuni numărate
     getStare()                           întoarce o copie a stării curente
     marcheazaVizitata(idSectiune)
     salveazaRaspuns(idSectiune, idIntrebare, raspuns, corect)
     getProcentGeneral()                  0–100, pe secțiunile numărate
     onSchimbare(callback)                se notifică interfața la fiecare scriere

   `reset()` este un utilitar de întreținere (golire completă), nu face parte din
   interfața stabilă; e păstrat aici tocmai ca ștergerea să se facă dintr-un
   singur loc.

   Pentru trecerea la cont + server, vezi secțiunea din README.md.
   ========================================================================== */

const CHEIE = "dswProgress";
const VERSIUNE = 1;

const GOL = {
  versiune: VERSIUNE,
  vizitate: {},     // { "1.1": { la } }
  raspunsuri: {},   // { "1.1": { "v0": { raspuns, corect, la } } }
  total: 56
};

let stare = structuredClone(GOL);
const ascultatori = new Set();

function citeste() {
  try {
    const brut = localStorage.getItem(CHEIE);
    if (!brut) return structuredClone(GOL);
    const parsat = JSON.parse(brut);
    // Migrare simplă între versiuni: pornim de la gol și suprascriem cu ce știm.
    if (parsat.versiune !== VERSIUNE) {
      return { ...structuredClone(GOL), ...parsat, versiune: VERSIUNE };
    }
    return { ...structuredClone(GOL), ...parsat };
  } catch {
    return structuredClone(GOL);
  }
}

function scrie() {
  try {
    localStorage.setItem(CHEIE, JSON.stringify(stare));
  } catch {
    /* stocarea poate fi dezactivată — ignorăm în mod tăcut */
  }
  for (const cb of ascultatori) {
    try { cb(getStare()); } catch { /* un ascultător care cade nu blochează restul */ }
  }
}

/** Pregătește stratul. `config.total` = numărul de secțiuni numărate (fără intro). */
export function init(config = {}) {
  stare = citeste();
  if (typeof config.total === "number" && config.total > 0) {
    stare.total = config.total;
  }
  return getStare();
}

/** Copie a stării curente (nu se modifică din afară). */
export function getStare() {
  return structuredClone(stare);
}

/** Marchează o secțiune ca vizitată. Idempotent. */
export function marcheazaVizitata(idSectiune) {
  if (!idSectiune) return;
  if (!stare.vizitate[idSectiune]) {
    stare.vizitate[idSectiune] = { la: Date.now() };
    scrie();
  }
}

/** Salvează răspunsul la o verificare. */
export function salveazaRaspuns(idSectiune, idIntrebare, raspuns, corect) {
  if (!idSectiune || !idIntrebare) return;
  stare.raspunsuri[idSectiune] = stare.raspunsuri[idSectiune] || {};
  stare.raspunsuri[idSectiune][idIntrebare] = {
    raspuns,
    corect: !!corect,
    la: Date.now()
  };
  scrie();
}

/**
 * Procent general, 0–100. Numărătorul sunt secțiunile numărate vizitate.
 * Convenție: secțiunile de introducere au id-ul „0.x” și NU se numără; ele nu
 * intră nici în numitor (config.total = numărul secțiunilor 1.x–8.x).
 */
export function getProcentGeneral() {
  const total = stare.total || 56;
  const numarate = Object.keys(stare.vizitate).filter((id) => !id.startsWith("0."));
  return Math.round((numarate.length / total) * 100);
}

/** Înregistrează un ascultător notificat la fiecare scriere. Întoarce dezabonarea. */
export function onSchimbare(callback) {
  if (typeof callback !== "function") return () => {};
  ascultatori.add(callback);
  return () => ascultatori.delete(callback);
}

/** Utilitar de întreținere: golește complet progresul (o singură cheie). */
export function reset() {
  try { localStorage.removeItem(CHEIE); } catch { /* ignorăm */ }
  stare = structuredClone(GOL);
  scrie();
}
