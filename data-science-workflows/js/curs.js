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
   tabelul meu.

   Numarul NU se scrie din cap: e cel din date/harta-cN.json, pe care il
   tipareste generatorul la fiecare rulare ("lectia N trebuie sa aiba
   sarcini:X"). Daca cele doua nu se potrivesc, studentul vede "18 din 17
   sarcini" si ia punctajul maxim pe o lectie nefacuta. */
export const LECTII = [
  { nr:1, cheie:"c1-introducere-si-mediu",
    titlu:"Introducere și configurare",
    scurt:"Introducere",
    rezumat:"Proiectul, pașii unui proiect de analiză de date, mediul de lucru virtual, tipurile de date și formatul JSON.",
    stare:"gata", sarcini:19,
    notebook:"https://github.com/VladAlexe/tutorials/blob/main/data-science-workflows/caiete/c1_mediu.ipynb" },

  { nr:2, cheie:"c2-colectarea-prin-api",
    titlu:"Colectarea datelor prin API",
    scurt:"API",
    rezumat:"Ce este un API, cum se citește o documentație, și cum aduci primele date reale în proiect.",
    stare:"gata", sarcini:18,
    notebook:"https://github.com/VladAlexe/tutorials/blob/main/data-science-workflows/caiete/c2_api.ipynb" },

  { nr:3, cheie:"c3-versionare-git",
    titlu:"Versionare cu Git",
    scurt:"Git",
    rezumat:"De ce versionăm, cum lucrează o echipă pe același proiect, și ce nu se urcă niciodată.",
    stare:"gata", sarcini:21,
    notebook:null },

  { nr:4, cheie:"c4-curatarea-datelor",
    titlu:"Curățarea datelor",
    scurt:"Curățare",
    rezumat:"Lipsuri, duplicate, unități care nu se potrivesc. Etapa cea mai lungă și cea care decide tot.",
    stare:"gata", sarcini:21,
    notebook:"https://github.com/VladAlexe/tutorials/blob/main/data-science-workflows/caiete/c4_curatare.ipynb" },

  { nr:5, cheie:"c5-agregare-si-baze-de-date",
    titlu:"Agregare și baze de date",
    scurt:"Agregare",
    rezumat:"Îmbinarea surselor, unitatea de analiză, și de ce un tabel mare are nevoie de o bază de date.",
    stare:"gata", sarcini:22,
    notebook:"https://github.com/VladAlexe/tutorials/blob/main/data-science-workflows/caiete/c5_agregare.ipynb" },

  { nr:6, cheie:"c6-analiza-exploratorie",
    titlu:"Analiza exploratorie",
    scurt:"Explorare",
    rezumat:"Privitul datelor înainte de a le modela: distribuții, relații, și grafice care induc în eroare.",
    stare:"gata", sarcini:7,
    notebook:"https://github.com/VladAlexe/tutorials/blob/main/data-science-workflows/caiete/c6_eda.ipynb" },

  { nr:7, cheie:"c7-variabile-si-model",
    titlu:"Variabile derivate și model",
    scurt:"Model",
    rezumat:"De la descriere la explicație: variabile construite de tine și un model pe care îl poți apăra.",
    stare:"gata", sarcini:8,
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

   Unsprezece puncte, din patru surse. Scris aici o singură dată: contul
   studentului, pagina cursului și catalogul citesc de aici, ca să nu existe
   două variante care se bat cap în cap.

   Două dintre ele le pun eu de mână (temele și proiectul), una o calculează
   situl din ce s-a lucrat la seminar, una se primește.

   Activitatea, în detaliu, pentru că e singura care se calculează:

     pe seminar   2 p ÷ 7 seminare = 0,2857
     pe quiz      0,2857 ÷ câte quiz-uri are seminarul
     la oră       întreg
     acasă        jumătate
     se ia cel mai bun dintre cele două

   De aici iese regula pe care o spui o dată la început de semestru și nu o
   mai explici: ORA LIVE VALOREAZĂ DE DOUĂ ORI CÂT ACEEAȘI LECȚIE FĂCUTĂ
   ACASĂ. Și, important pentru tine: numărul de quiz-uri dintr-un seminar NU
   schimbă cât valorează seminarul. Zece sau patru, tot 0,2857. Deci tai din
   ele pentru atenția lor, nu pentru notă.
   =========================================================================== */

export const NOTARE = {
  total: 11,
  activitate: { puncte: 2, seminare: 7, acasa: 0.5 },
  componente: [
    { cheie:"teme", nume:"Teme", puncte:3,
      scurt:"trei teme, predate pe Teams",
      d:"Trei teme de seminar, pe care le încarci în Teams. N-au legătură cu " +
        "lecțiile de pe sit: le citesc și le notez eu." },

    { cheie:"seminar", nume:"Activitate la seminar", puncte:2,
      scurt:"quiz-urile din lecții",
      d:"Se adună din quiz-urile din lecții. La oră valorează întreg, acasă " +
        "jumătate, și se ia cel mai bun dintre cele două. Fiecare seminar " +
        "valorează la fel, indiferent câte quiz-uri are." },

    { cheie:"proiect", nume:"Proiect", puncte:5,
      scurt:"depozitul de echipă și raportul final",
      d:"Proiectul de echipă, cu tot cu depozitul pe GitHub: datele colectate, " +
        "curățarea, analiza și raportul. Se notează drumul care se vede în " +
        "depozit, nu spectaculozitatea rezultatului. Nota e pe om." },

    { cheie:"oficiu", nume:"Din oficiu", puncte:1,
      scurt:"se primește",
      d:"Un punct pe care îl ai de la început. Nu trebuie făcut nimic pentru el." }
  ]
};

export const punctaj = cheie => NOTARE.componente.find(c => c.cheie === cheie)?.puncte || 0;
