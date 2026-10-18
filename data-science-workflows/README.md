# Fluxuri de lucru pentru știința datelor

Curs de masterat (UBB · ADC). Sit static: HTML, CSS și JavaScript simplu, cu
Supabase pentru conturi și ore, servit de Cloudflare.

## Cum e organizat

```
index.html                 pagina cursului: lecțiile, una sub alta
cN-.../index.html          pagina unei lecții (generată, vezi mai jos)
cN-.../lectie/             slide-urile lecției (generate)
cN-.../tutorial/           manualul lecției (generat)
cont/                      intrarea în cont și contul studentului
intra/                     intrarea la oră, cu codul de pe ecran
predau/                    doar profesorul: catalogul, lecțiile, orele
explorator/                harta SCI
date-personale/            ce se salvează
css/  js/  img/  date/     stiluri, cod, logo, date pentru componente
db/                        SQL de rulat în Supabase, în ordine
_build/                    generatoarele
```

## Predarea, într-un singur loc

- Pe pagina lecției, profesorul are în plus butonul **Predă**: pornește ora și
  deschide lecția. Codul apare mare, de proiectat.
- În lecție, bara orei are patru lucruri: codul (un clic îl face mare, cu QR și
  link), câți sunt, **Arată clasei** (răspunsurile agregate, fără nume, pentru
  proiector), **Rezultate** (cu nume, într-o fereastră peste lecție: slide-ul de pe ecran și toată ora) și **Încheie ora**, singurul
  loc din care se oprește.
- O oră uitată deschisă se închide singură după 3 ore (`db/17-inchidere-automata.sql`).
- O singură oră, condusă dintr-o singură filă. Dacă ieși din ea, butonul **Înapoi la oră**
  din antet te duce înapoi (profesor sau student). După 3 ore ora se închide singură.
- `db/19-viteza.sql` face panoul orei rapid și cu 30 de studenți.
- Catalogul (prezență, activitate, teme, proiect, total) cere `db/18-catalog.sql`.
  Temele și proiectul se scriu direct în catalog; studentul le vede în contul lui.
- Studentul vede doar lecțiile predate grupei. **Începe lecția** pornește mereu de
  la primul slide.

## Cum se construiește

```
python3 _build/c1.py ... c7.py      # slide-urile și manualul fiecărei lecții
python3 _build/intrari.py           # paginile lecțiilor, din _build/intrari.json
python3 _build/versiune.py          # ULTIMUL: ridică ?v=N peste tot
```

Local: `python -m http.server 8000` din folderul `tutorials/`, apoi
<http://localhost:8000/data-science-workflows/>.
