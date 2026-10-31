/* Pagina Exploratorului: harta legăturilor sociale pe tot ecranul.
   Toată logica stă în harta-sci.js, aceeași cu cea din slide-uri. */

import { monteaza } from "./harta-sci.js?v=103";

monteaza(document.getElementById("explorator"), {
  niveluri: ["judete", "regiuni", "tari"],
  nivel: "regiuni", masura: "sci", ales: "RO11",
  adresa: true,
  titlu: "Legăturile sociale ale unui loc",
  sub: "Alege un loc pe hartă. Celelalte sunt colorate după intensitatea legăturii cu acesta.",
  povesti: [
    { t: "Migrația: România", nivel: "tari", masura: "migr", ales: "RO",
      text: "Italia are cei mai mulți cetățeni români dintre țările europene (1,07 milioane), înaintea Germaniei și a Spaniei. După măsura Legături (SCI), Italia se află abia pe locul 6." },
    { t: "Modelul: România", nivel: "tari", masura: "model", ales: "RO",
      text: "Modelul din lecția 7 include distanța, migrația și granița comună. Italia are valori sub cele prezise de model, Austria și Ungaria peste. Pentru Ungaria, explicația probabilă este minoritatea maghiară, nu migrația." },
    { t: "România și Germania", nivel: "regiuni", masura: "com", ales: "RO11",
      text: "Algoritmul de detectare a comunităților plasează toate cele 8 regiuni ale României în același grup cu Germania. În rețeaua migrației, România apare alături de Italia și Spania." },
    { t: "Polonezii din Irlanda", nivel: "regiuni", masura: "com", ales: "PL91",
      text: "Polonia, Irlanda, Islanda și Lituania formează o singură comunitate, ceea ce reflectă emigrația poloneză de după 2004." },
    { t: "Harghita și Covasna", nivel: "judete", masura: "sci", ales: "RO124",
      text: "Cea mai puternică legătură dintre două județe românești. În afara țării, Harghita este legată de Ungaria și, mai neașteptat, de cantonul elvețian Thurgau." },
    { t: "Dolj și Huelva", nivel: "judete", masura: "sci", ales: "RO411",
      text: "Printre partenerii externi cu cele mai puternice legături cu Doljul se află Huelva, în sudul Spaniei, o regiune de cultivare a căpșunilor unde lucrează sezonier mulți muncitori din Oltenia." },
  ],
});
