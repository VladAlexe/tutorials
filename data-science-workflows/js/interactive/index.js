/* index.js — registrul de componente interactive: nume -> funcție.
   Randorul de blocuri nu cunoaște componentele; le cere doar după nume.
   Ca să adaugi o componentă nouă: scrie-o în acest folder, exportând o funcție
   `(gazda, parametri)`, importă-o aici și adaug-o în obiectul REGISTRU. */

import flux from "./flux.js";
import tipuri from "./tipuri.js";
import json from "./json.js";
import terminal from "./terminal.js";

export const REGISTRU = {
  flux,
  tipuri,
  json,
  terminal
};

/** Întoarce funcția componentei sau null dacă numele nu e înregistrat. */
export function componenta(nume) {
  return REGISTRU[nume] || null;
}
