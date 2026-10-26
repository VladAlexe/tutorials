/* Pagina Exploratorului: harta legăturilor sociale pe tot ecranul.
   Toată logica stă în harta-sci.js, aceeași cu cea din slide-uri. */

import { monteaza } from "./harta-sci.js?v=69";

monteaza(document.getElementById("explorator"), {
  niveluri: ["judete", "regiuni", "tari"],
  nivel: "regiuni", masura: "sci", ales: "RO11",
  adresa: true,
  titlu: "Cu cine e legat un loc?",
  sub: "Alege un loc pe hartă. Celelalte se colorează după cât de legate sunt de el.",
  povesti: [
    { t: "Ghicitoarea: România", nivel: "tari", masura: "migr", ales: "RO",
      text: "Italia are cei mai mulți cetățeni români din Europa (1,07 milioane), înaintea Germaniei și a Spaniei. Comută pe Legături: în SCI, Italia e abia pe locul 6." },
    { t: "Modelul: România", nivel: "tari", masura: "model", ales: "RO",
      text: "Modelul din lecția 7 ține cont de distanță, migrație și graniță. Italia iese sub așteptare, Austria și Ungaria peste. Pentru Ungaria, explicația probabilă e minoritatea maghiară, nu migrația." },
    { t: "România și Germania", nivel: "regiuni", masura: "com", ales: "RO11",
      text: "Algoritmul de comunități pune toate cele 8 regiuni ale României în același grup cu Germania. În rețeaua migrației, România stă lângă Italia și Spania." },
    { t: "Polonezii din Irlanda", nivel: "regiuni", masura: "com", ales: "PL91",
      text: "Polonia, Irlanda, Islanda și Lituania formează o singură comunitate: urma emigrației poloneze de după 2004." },
    { t: "Harghita și Covasna", nivel: "judete", masura: "sci", ales: "RO124",
      text: "Cea mai puternică legătură dintre două județe românești. În afara țării, Harghita e legată de Ungaria și, surprinzător, de cantonul elvețian Thurgau." },
    { t: "Dolj și Huelva", nivel: "judete", masura: "sci", ales: "RO411",
      text: "Printre cei mai legați parteneri externi ai Doljului e Huelva, în sudul Spaniei: regiunea căpșunilor, unde lucrează sezonier mulți olteni." },
  ],
});
