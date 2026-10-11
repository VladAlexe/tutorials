# Configurare, pas cu pas

Se face o singura data, in jur de douazeci de minute. Fiecare pas se verifica
inainte de urmatorul: daca unul nu merge, oprește-te si spune-mi care.

---

## 1. Creeaza proiectul Supabase

Pe supabase.com, cont nou sau existent, apoi **New project**.

- Nume: `dsw-2026`
- Regiune: Frankfurt sau Londra, cele mai apropiate
- Parola bazei de date: genereaza una si **salveaza-o** in managerul tau de parole

Planul gratuit permite doua proiecte active. Daca ai deja doua, suspenda unul
vechi sau foloseste alta organizatie.

## 2. Ruleaza fisierele SQL

In panou, meniul din stanga, **SQL Editor**, apoi **New query**.

Lipeste intreg `01-schema.sql`, apasa **Run**. Trebuie sa scrie `Success`.
Apoi acelasi lucru cu `02-politici.sql`.

Verificare: in **Table Editor** trebuie sa vezi opt tabele, toate goale.

## 3. Ia cheile

**Project Settings**, apoi **API**. Ai nevoie de doua valori:

- **Project URL**, de forma `https://xxxxxxxx.supabase.co`
- **anon public** key, un sir lung

Le pui in `js/supabase-config.js`.

Cheia `anon` **este facuta sa fie publica**. Ajunge in pagina si o vede oricine,
si asa trebuie. Ea nu da acces la nimic: accesul e decis de politicile din pasul 2.
Cheia care nu se publica niciodata e `service_role`, pe care noi nu o folosim deloc.

## 4. Porneste autentificarea

**Authentication**, apoi **Providers**.

**Email**: e pornit din start. Verifica sa fie bifat *Enable email provider*.
Daca vrei intrare fara parola, lasa *Confirm email* pornit; linkul trimis
functioneaza ca autentificare.

**GitHub**: il pornesti cand ajungem la cursul despre Git. Ai nevoie de o
aplicatie OAuth pe GitHub, iar Supabase iti arata exact ce adresa de retur sa
pui. Nu e nevoie acum.

## 5. Spune-i unde sa se intoarca

**Authentication**, apoi **URL Configuration**.

- **Site URL**: `https://courses.vladalexe.com`
- **Redirect URLs**, adauga pe rinduri separate:
  - `https://courses.vladalexe.com/data-science-workflows/cont/`
  - `http://localhost:*` (ca sa poti testa local)

Fara pasul acesta, linkul din e-mail te duce intr-un loc greșit.

## 6. Incarca lista de studenti

> **Atentie.** Tot ce e in acest repo e servit public, la adresa fiecarui fisier.
> O lista cu nume si matricole reale, pusa aici, ar putea fi descarcata de oricine.
> Fisierul `03-lista-studenti.csv` e trecut in `.gitignore` tocmai de aceea.
>
> Lucreaza pe o copie **in afara repo-ului**, de exemplu pe desktop, si incarca-o
> direct in Supabase. In repo rimane doar antetul, ca sablon.

Formatul, cu prima linie exact cum e:

```
matricol,nume,an,grupa
123456,Popescu Ion,1,A
123457,Ionescu Maria,1,A
```

Apoi: **Table Editor**, tabelul `studenti`, butonul **Insert**, apoi
**Import data from CSV**.

Matricolele se scriu exact cum apar in lista de la secretariat. Functia de
inregistrare le compara cu majuscule si fara spatii la capete, deci nu conteaza
cum le tasteaza studentul.

## 7. Fa-te profesor

Intai te autentifici tu pe site, cu e-mailul tau, pe pagina `/cont/`.
Nu introduce niciun matricol.

Apoi, in **SQL Editor**:

```sql
insert into public.profesori (user_id)
select id from auth.users where email = 'adresa@ta.ro';
```

Verificare, in SQL Editor:

```sql
select public.sunt_profesor();
```

Trebuie sa intoarca `true`. Daca intoarce `false`, inseamna ca rulezi
interogarea ca administrator al bazei, nu ca utilizator; verifica in schimb
direct tabelul:

```sql
select * from public.profesori;
```

## 8. Verifica lanțul complet

Deschide `/data-science-workflows/cont/` intr-o fereastra privata, ca sa nu
folosesti sesiunea ta de profesor.

- intri cu o adresa de e-mail
- primesti linkul si te intorci pe pagina
- introduci un matricol de test, pus de tine in lista
- pagina trebuie sa afiseze numele din lista

Apoi, in **Table Editor**, tabelul `profiluri`: trebuie sa vezi un rand, cu
matricolul si adresa.

Daca ai ajuns aici, baza, autentificarea si politicile functioneaza. De aici
incolo, restul e repetitie.

---

## Ce NU se pune niciodata in acest repo

Cheia `service_role`. Parola bazei de date. Orice jeton de acces GitHub.
Lista reala de studenti, cu nume si matricole.

Tot ce e in acest repo e servit public, la adresa fiecarui fisier. Verifica
oricand: deschide `courses.vladalexe.com/` plus calea fisierului.
