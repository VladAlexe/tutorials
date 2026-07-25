/* index.js — registrul de componente interactive: nume -> funcție.
   Randorul de blocuri nu cunoaște componentele; le cere doar după nume.
   Ca să adaugi o componentă nouă: scrie-o în acest folder, exportând o funcție
   `(gazda, parametri)`, importă-o aici și adaug-o în obiectul REGISTRU. */

/* Capitolul 1 */
import flux from "./flux.js";
import tipuri from "./tipuri.js";
import json from "./json.js";
import terminal from "./terminal.js";

/* Capitolul 2 */
import restaurant from "./restaurant.js";
import taxonomie from "./taxonomie.js";
import surse from "./surse.js";
import anatomie from "./anatomie.js";
import constructor from "./constructor.js";
import coduri from "./coduri.js";
import harta_doc from "./harta_doc.js";
import secrete from "./secrete.js";
import cod_parametri from "./cod_parametri.js";
import paginare from "./paginare.js";
import json_tabel from "./json_tabel.js";

/* Capitolul 3 */
import versiuni from "./versiuni.js";
import terminal_git from "./terminal_git.js";
import zone from "./zone.js";
import anulare from "./anulare.js";
import ramuri from "./ramuri.js";
import conflict from "./conflict.js";
import sincronizare from "./sincronizare.js";
import gitignore from "./gitignore.js";

export const REGISTRU = {
  flux,
  tipuri,
  json,
  terminal,
  restaurant,
  taxonomie,
  surse,
  anatomie,
  constructor,
  coduri,
  harta_doc,
  secrete,
  cod_parametri,
  paginare,
  json_tabel,
  versiuni,
  terminal_git,
  zone,
  anulare,
  ramuri,
  conflict,
  sincronizare,
  gitignore
};

/** Întoarce funcția componentei sau null dacă numele nu e înregistrat. */
export function componenta(nume) {
  return REGISTRU[nume] || null;
}
