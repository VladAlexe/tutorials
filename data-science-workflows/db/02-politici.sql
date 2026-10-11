-- ============================================================================
--  02. Politici de acces (Row Level Security)
--
--  Aceasta e partea care garanteaza ca un student vede numai datele lui.
--  Garantia vine de la baza de date, nu de la codul paginii: chiar daca
--  cineva deschide consola si scrie interogari de mana, nu primeste nimic
--  ce nu e al lui.
--
--  Se ruleaza dupa 01-schema.sql.
--
--  Liniile "enable row level security" de mai jos sunt deja rulate in
--  01-schema.sql. Le repetam aici ca fisierul sa fie valid si de unul singur;
--  a doua rulare nu schimba nimic.
-- ============================================================================

alter table public.studenti          enable row level security;
alter table public.profiluri         enable row level security;
alter table public.profesori         enable row level security;
alter table public.raspunsuri        enable row level security;
alter table public.rulari_cod        enable row level security;
alter table public.progres           enable row level security;
alter table public.prezente          enable row level security;
alter table public.jetoane_prezenta  enable row level security;

-- ----------------------------------------------------------------------------
--  studenti: lista oficiala. Numai profesorul.
--  Studentii ajung la numele lor prin functia profilul_meu().
-- ----------------------------------------------------------------------------
drop policy if exists studenti_prof on public.studenti;
create policy studenti_prof on public.studenti
  for all to authenticated
  using (public.sunt_profesor())
  with check (public.sunt_profesor());

-- ----------------------------------------------------------------------------
--  profiluri: fiecare isi vede randul lui. Profesorul le vede pe toate.
--  Scrierea se face numai prin revendica_matricol(), deci nu dam insert.
-- ----------------------------------------------------------------------------
drop policy if exists profiluri_citire on public.profiluri;
create policy profiluri_citire on public.profiluri
  for select to authenticated
  using (user_id = auth.uid() or public.sunt_profesor());

drop policy if exists profiluri_github on public.profiluri;
create policy profiluri_github on public.profiluri
  for update to authenticated
  using (user_id = auth.uid())
  with check (user_id = auth.uid());

-- ----------------------------------------------------------------------------
--  profesori: nimeni nu citeste direct. Se adauga din panoul Supabase.
-- ----------------------------------------------------------------------------
drop policy if exists profesori_prof on public.profesori;
create policy profesori_prof on public.profesori
  for select to authenticated
  using (public.sunt_profesor());

-- ----------------------------------------------------------------------------
--  raspunsuri: scrii numai pentru tine, citesti numai ale tale.
--  Profesorul citeste tot. Nimeni nu modifica un raspuns dat.
-- ----------------------------------------------------------------------------
drop policy if exists raspunsuri_scriere on public.raspunsuri;
create policy raspunsuri_scriere on public.raspunsuri
  for insert to authenticated
  with check (user_id = auth.uid());

drop policy if exists raspunsuri_citire on public.raspunsuri;
create policy raspunsuri_citire on public.raspunsuri
  for select to authenticated
  using (user_id = auth.uid() or public.sunt_profesor());

-- ----------------------------------------------------------------------------
--  rulari_cod: la fel.
-- ----------------------------------------------------------------------------
drop policy if exists rulari_scriere on public.rulari_cod;
create policy rulari_scriere on public.rulari_cod
  for insert to authenticated
  with check (user_id = auth.uid());

drop policy if exists rulari_citire on public.rulari_cod;
create policy rulari_citire on public.rulari_cod
  for select to authenticated
  using (user_id = auth.uid() or public.sunt_profesor());

-- ----------------------------------------------------------------------------
--  progres: aici se si actualizeaza, deci dam si update.
-- ----------------------------------------------------------------------------
drop policy if exists progres_scriere on public.progres;
create policy progres_scriere on public.progres
  for insert to authenticated
  with check (user_id = auth.uid());

drop policy if exists progres_actualizare on public.progres;
create policy progres_actualizare on public.progres
  for update to authenticated
  using (user_id = auth.uid())
  with check (user_id = auth.uid());

drop policy if exists progres_citire on public.progres;
create policy progres_citire on public.progres
  for select to authenticated
  using (user_id = auth.uid() or public.sunt_profesor());

-- ----------------------------------------------------------------------------
--  prezente: se scriu numai prin marcheaza_prezenta(), deci doar citire.
-- ----------------------------------------------------------------------------
drop policy if exists prezente_citire on public.prezente;
create policy prezente_citire on public.prezente
  for select to authenticated
  using (user_id = auth.uid() or public.sunt_profesor());

-- ----------------------------------------------------------------------------
--  jetoane_prezenta: numai profesorul le creeaza si le vede.
--  Studentul nu citeste tabelul, doar apeleaza functia cu jetonul din QR.
-- ----------------------------------------------------------------------------
drop policy if exists jetoane_prof on public.jetoane_prezenta;
create policy jetoane_prof on public.jetoane_prezenta
  for all to authenticated
  using (public.sunt_profesor())
  with check (public.sunt_profesor());
