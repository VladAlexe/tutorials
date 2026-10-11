# Lista de bifat, in ordine

Proiectul: `ybvtxenerriwstiktebe`
Panou: https://supabase.com/dashboard/project/ybvtxenerriwstiktebe

---

- [ ] **1. Ruleaza SQL**, in SQL Editor, in ordinea asta, fiecare separat:
      - `01-schema.sql` → trebuie `Success`
      - `02-politici.sql` → trebuie `Success`
      - `04-studenti-test.sql` → trebuie sa afiseze doua randuri, A cu 12 si B cu 12

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
