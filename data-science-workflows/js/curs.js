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
   `notebook` e legatura catre caietul de lucru, pe GitHub.
   `sarcini` e cate porti are lectia: verificarile cu variante plus exercitiile
   cu cod. Din numarul asta ies punctele de la teme, si pentru student si in
   tabelul meu, deci se tine la zi cand se schimba continutul lectiei. */
export const LECTII = [
  { nr:1, cheie:"c1-introducere-si-mediu",
    titlu:"Introducere și configurare",
    scurt:"Introducere",
    rezumat:"Proiectul, pașii unui proiect de analiză de date, mediul de lucru virtual, tipurile de date și formatul JSON.",
    stare:"gata", sarcini:17,
    notebook:"https://github.com/VladAlexe/tutorials/blob/main/data-science-workflows/caiete/c1_mediu.ipynb" },

  { nr:2, cheie:"c2-colectarea-prin-api",
    titlu:"Colectarea datelor prin API",
    scurt:"API",
    rezumat:"Ce este un API, cum arată o cerere, codurile de răspuns, requests, și primele date reale în proiect.",
    stare:"gata", sarcini:18,
    notebook:"https://github.com/VladAlexe/tutorials/blob/main/data-science-workflows/caiete/c2_api.ipynb" },

  { nr:3, cheie:"c3-versionare-git",
    titlu:"Versionare cu Git",
    scurt:"Git",
    rezumat:"De ce versionăm, cum lucrează o echipă pe același proiect, ce nu se urcă niciodată, și cum se încadrează teoretic un proiect.",
    stare:"gata", sarcini:23,
    notebook:"https://github.com/VladAlexe/tutorials/blob/main/data-science-workflows/caiete/c3_git.ipynb" },

  { nr:4, cheie:"c4-curatarea-datelor",
    titlu:"Curățarea datelor",
    scurt:"Curățare",
    rezumat:"Git în practică, apoi etapa care mănâncă 60% din timp: profilare, standardizare, duplicate, lipsuri, valori extreme, validare.",
    stare:"gata", sarcini:22,
    notebook:"https://github.com/VladAlexe/tutorials/blob/main/data-science-workflows/caiete/c4_curatare.ipynb" },

  { nr:5, cheie:"c5-agregare-si-baze-de-date",
    titlu:"Agregare și baze de date",
    scurt:"Agregare",
    rezumat:"Îmbinarea surselor, unitatea de analiză, și de ce un tabel mare are nevoie de o bază de date.",
    stare:"schita", sarcini:null,
    notebook:"https://github.com/VladAlexe/tutorials/blob/main/data-science-workflows/caiete/c5_agregare.ipynb" },

  { nr:6, cheie:"c6-analiza-exploratorie",
    titlu:"Analiza exploratorie",
    scurt:"Explorare",
    rezumat:"Privitul datelor înainte de a le modela: distribuții, relații, și grafice care induc în eroare.",
    stare:"schita", sarcini:null,
    notebook:"https://github.com/VladAlexe/tutorials/blob/main/data-science-workflows/caiete/c6_eda.ipynb" },

  { nr:7, cheie:"c7-variabile-si-model",
    titlu:"Variabile derivate și model",
    scurt:"Model",
    rezumat:"De la descriere la explicație: variabile construite de tine și un model pe care îl poți apăra.",
    stare:"schita", sarcini:null,
    notebook:"https://github.com/VladAlexe/tutorials/blob/main/data-science-workflows/caiete/c7_model.ipynb" },

  { nr:8, cheie:"c8-raportare",
    titlu:"Raportare și proiect final",
    scurt:"Raport",
    rezumat:"Rezultatul devine util abia când altcineva îl poate citi, reproduce și critica.",
    stare:"schita", sarcini:null,
    notebook:null }
];

export const dupaCheie = c => LECTII.find(l => l.cheie === c) || null;

/* ===========================================================================
   NOTAREA

   Zece puncte, din trei surse. Scris aici o singura data: contul studentului,
   pagina cursului si panoul profesorului citesc de aici, ca sa nu existe doua
   variante care se bat cap in cap.
   =========================================================================== */

export const NOTARE = {
  total: 10,
  componente: [
    { cheie:"teme", nume:"Teme", puncte:3,
      scurt:"verificările și exercițiile din lecții",
      d:"Se adună din ce faci în lecții: verificările cu variante și exercițiile cu cod. " +
        "Contează că le-ai făcut, nu că le-ai nimerit din prima — poți relua orice slide " +
        "până iese." },

    { cheie:"proiect", nume:"Proiect", puncte:5,
      scurt:"depozitul de echipă și raportul final",
      d:"Proiectul de echipă, cu tot cu depozitul pe GitHub: datele colectate, curățarea, " +
        "analiza și raportul. Se notează drumul care se vede în depozit, nu spectaculozitatea " +
        "rezultatului." },

    { cheie:"seminar", nume:"Seminar și prezență", puncte:2,
      scurt:"prezența la ore și lucrul la seminar",
      d:"Prezența se marchează la începutul orei, scanând codul de pe ecran. Punctajul " +
        "crește cu fiecare ședință la care ai fost și ai lucrat." }
  ]
};

export const punctaj = cheie => NOTARE.componente.find(c => c.cheie === cheie)?.puncte || 0;
