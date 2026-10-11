/* ===========================================================================
   Structura cursului, intr-un singur loc.
   Paginile, antetul si fluxul citesc de aici.
   =========================================================================== */

export const RADACINA = "/data-science-workflows";

export const CURS = {
  titlu: "Fluxuri de lucru pentru știința datelor",
  scurt: "Fluxuri de lucru",
  institutie: "Analiza Datelor Complexe · Sociologie · UBB",
  an: "2026",
  depozit: "https://github.com/VladAlexe/tutorials"
};

/* Opt lectii. `stare` e "gata" sau "schita".
   `notebook` e legatura catre caietul de lucru, pe GitHub. */
export const LECTII = [
  { nr:1, cheie:"c1-introducere-si-mediu",
    titlu:"Introducere și mediul de lucru",
    scurt:"Introducere",
    rezumat:"Ce este un flux de lucru pentru date, cum arată proiectul semestrului, și cum îți pregătești mediul.",
    stare:"gata",
    notebook:"https://github.com/VladAlexe/tutorials/blob/main/data-science-workflows/caiete/c1_mediu.ipynb" },

  { nr:2, cheie:"c2-colectarea-prin-api",
    titlu:"Colectarea datelor prin API",
    scurt:"API",
    rezumat:"Ce este un API, cum se citește o documentație, și cum aduci primele date reale în proiect.",
    stare:"schita",
    notebook:"https://github.com/VladAlexe/tutorials/blob/main/data-science-workflows/caiete/c2_api.ipynb" },

  { nr:3, cheie:"c3-versionare-git",
    titlu:"Versionare cu Git",
    scurt:"Git",
    rezumat:"De ce versionăm, cum lucrează o echipă pe același proiect, și ce nu se urcă niciodată.",
    stare:"schita",
    notebook:null },

  { nr:4, cheie:"c4-curatarea-datelor",
    titlu:"Curățarea datelor",
    scurt:"Curățare",
    rezumat:"Lipsuri, duplicate, unități care nu se potrivesc. Etapa cea mai lungă și cea care decide tot.",
    stare:"schita",
    notebook:"https://github.com/VladAlexe/tutorials/blob/main/data-science-workflows/caiete/c4_curatare.ipynb" },

  { nr:5, cheie:"c5-agregare-si-baze-de-date",
    titlu:"Agregare și baze de date",
    scurt:"Agregare",
    rezumat:"Îmbinarea surselor, unitatea de analiză, și de ce un tabel mare are nevoie de o bază de date.",
    stare:"schita",
    notebook:"https://github.com/VladAlexe/tutorials/blob/main/data-science-workflows/caiete/c5_agregare.ipynb" },

  { nr:6, cheie:"c6-analiza-exploratorie",
    titlu:"Analiza exploratorie",
    scurt:"Explorare",
    rezumat:"Privitul datelor înainte de a le modela: distribuții, relații, și grafice care induc în eroare.",
    stare:"schita",
    notebook:"https://github.com/VladAlexe/tutorials/blob/main/data-science-workflows/caiete/c6_eda.ipynb" },

  { nr:7, cheie:"c7-variabile-si-model",
    titlu:"Variabile derivate și model",
    scurt:"Model",
    rezumat:"De la descriere la explicație: variabile construite de tine și un model pe care îl poți apăra.",
    stare:"schita",
    notebook:"https://github.com/VladAlexe/tutorials/blob/main/data-science-workflows/caiete/c7_model.ipynb" },

  { nr:8, cheie:"c8-raportare",
    titlu:"Raportare și proiect final",
    scurt:"Raport",
    rezumat:"Rezultatul devine util abia când altcineva îl poate citi, reproduce și critica.",
    stare:"schita",
    notebook:null }
];

export const dupaCheie = c => LECTII.find(l => l.cheie === c) || null;
