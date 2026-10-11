# Lista de bifat, in ordine

Proiectul: `ybvtxenerriwstiktebe`
Panou: https://supabase.com/dashboard/project/ybvtxenerriwstiktebe

---

- [ ] **1. Ruleaza SQL**, in SQL Editor, in ordinea asta, fiecare separat:
      - `01-schema.sql` → trebuie `Success`
      - `02-politici.sql` → trebuie `Success`
      - `04-studenti-test.sql` → trebuie sa afiseze doua randuri, A cu 12 si B cu 12

- [ ] **1b. Restul fisierelor SQL**, tot in SQL Editor, tot in ordine:
      - `05-sesiuni-si-reset.sql` → sesiunile live si butonul de reset
      - `06-invitati-si-asteptari.sql` → intrarea ca invitat si asteptarile lor
      - `07-prezenta.sql` → codul QR de prezenta
      - `08-ritm.sql` → **ora condusa**: toti sar pe slide-ul meu
      - `09-note.sql` → tabelul cu notele grupei
      - `10-profesori.sql` → pot face profesor si un al doilea cont
      - `11-context.sql` → de unde vine fiecare raspuns (in ora / singur /
        din manual), si scoaterea contului meu din statisticile clasei

      Fiecare trebuie sa dea `Success`. Se pot rula din nou oricand, nu strica
      nimic.

      Pentru intrarea ca invitat mai e un buton de pornit, nu din SQL:
      **Authentication** → **Sign In / Providers** → **Anonymous sign-ins**.

- [ ] **2. Ia cheia publica**: butonul verde **Connect**, sus de tot, tabul
      **App Frameworks**. Acolo apare si adresa, si cheia publica.
      Alternativ: **Settings** → **API Keys**.

      Cheia noua incepe cu `sb_publishable_`. Daca proiectul are si cheia veche,
      aceea se cheama `anon public` si incepe cu `eyJ`. Oricare merge.

      O pui in `js/supabase-config.js`, in locul lui `PUNE-AICI-CHEIA-PUBLICA`.
      Adresa proiectului e deja completata.

- [ ] **3. Adrese de retur**: Authentication → URL Configuration
      - Site URL: `https://courses.vladalexe.com`
      - Redirect URLs, pe rinduri separate:
        - `https://courses.vladalexe.com/data-science-workflows/cont/`
        - `http://localhost:*`

- [ ] **4. Verifica e-mailul**: Authentication → Providers → Email trebuie pornit.

- [ ] **5. Intra tu pe site**, pe `/data-science-workflows/cont/`, cu adresa ta.
      **Nu introduce niciun matricol.** Doar te autentifici.

- [ ] **6. Fa-te profesor**, in SQL Editor:
      ```sql
      insert into public.profesori (user_id)
      select id from auth.users where email = 'adresa@ta.ro';
      ```
      Verificare: `select * from public.profesori;` trebuie sa aiba un rand.

      **Un cont separat, numai de profesor** (recomandat: asa poti sa-ti incerci
      site-ul cu un cont de student fara sa-ti pierzi panoul): intra o data pe
      site cu celalalt cont, apoi, din `/profesor/`, sectiunea *Conturile de
      profesor*, scrie-i adresa si apasa *Fa-l profesor*. Contul de profesor nu
      are nevoie de numar matricol si nu apare in lista studentilor.

- [ ] **7. Proba finala.** Fereastra privata, `/data-science-workflows/cont/`,
      intri cu alta adresa, introduci `900001`.
      Pagina trebuie sa scrie **Bun venit, Andreea**.

- [ ] **8. Verifica in baza**: Table Editor → `profiluri` → un rand, cu `900001`.

---

## Daca ceva nu merge

Spune-mi exact la ce pas si ce scrie pe ecran. Erorile de SQL sunt
informative; cele din pagina apar in caseta roșie sau in consola browserului
(F12, tabul Console).

## Cand vine lista reala

```sql
delete from public.studenti where matricol like '9%';
```

Apoi incarci lista adevarata prin Table Editor → `studenti` → Insert →
Import data from CSV. Fisierul completat **nu se pune in repo**.
