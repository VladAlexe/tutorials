-- ===========================================================================
-- 30. Prezențele și punctajele lecției 4 (ora rămasă deschisă)
--
-- Se rulează în Supabase (SQL Editor). Aceiași pași ca 28, pentru 'c4', fără
-- sarcinile speciale de la C3 (acolo s-a promis punctaj întreg la verificarea
-- depozitului; la C4 nu). E sigur de rulat din nou: nu dublează nimic.
--
-- Ordinea:
--   A. blocul „Este instalată prezența imediată?” (doar citește);
--   B. blocul 0 (doar citește): orele C4 și răspunsurile rămase fără oră;
--   C. tranzacția (begin ... commit): pașii 1-3;
--   D. verificarea de după;
--   E. dacă la A nu apare niciun rând: rulează o dată 29-prezenta-imediata.sql,
--      ca la C5 prezența să se scrie singură.
-- ===========================================================================

-- A. Este instalată prezența imediată (29)? Trebuie să apară două rânduri.
select tgname, tgrelid::regclass as tabelul
  from pg_trigger
 where tgname in ('prezenta_din_raspuns', 'prezenta_din_cod');

-- 0. Verificarea de dinainte: rulează doar blocul acesta, întâi, și uită-te la cifre.
with lectia as (select 'c4'::text as cap)
select s.capitol, s.titlu, s.deschisa_la, s.inchisa_la, s.arhivata_la,
       (select count(distinct i.user_id) from public.incercari i where i.sedinta_id = s.id) as au_raspuns_la_ora,
       (select count(*) from public.prezente z where z.sedinta_id = s.id)                   as prezenti
  from public.sedinte s, lectia
 where s.capitol = lectia.cap
 order by s.deschisa_la;

with lectia as (select 'c4'::text as cap)
select count(*) as raspunsuri_fara_ora, count(distinct i.user_id) as studenti
  from public.incercari i, lectia
 where i.sarcina_id like lectia.cap || '-%' and i.sedinta_id is null;


begin;

-- 1. orele uitate deschise (peste 3 ore) se închid și primesc prezența
select public.inchide_orele_uitate();

-- 2. răspunsurile din timpul orei, legate de ora grupei
with lectia as (select 'c4'::text as cap),
ora as (
  select s.id, s.grupa_id, s.deschisa_la,
         coalesce(s.inchisa_la, s.deschisa_la + interval '3 hours') as gata
    from public.sedinte s, lectia
   where s.capitol = lectia.cap and s.arhivata_la is null
),
cine as (
  select p.user_id, st.grupa_id
    from public.profiluri p
    left join public.studenti st on st.matricol = p.matricol
)
update public.raspunsuri r
   set sedinta_id = o.id
  from ora o, cine c, lectia
 where r.sedinta_id is null
   and r.intrebare_id like lectia.cap || '-%'
   and c.user_id = r.user_id
   and (o.grupa_id is null or o.grupa_id = c.grupa_id)
   and r.creat_la between o.deschisa_la and o.gata;

with lectia as (select 'c4'::text as cap),
ora as (
  select s.id, s.grupa_id, s.deschisa_la,
         coalesce(s.inchisa_la, s.deschisa_la + interval '3 hours') as gata
    from public.sedinte s, lectia
   where s.capitol = lectia.cap and s.arhivata_la is null
),
cine as (
  select p.user_id, st.grupa_id
    from public.profiluri p
    left join public.studenti st on st.matricol = p.matricol
)
update public.rulari_cod rc
   set sedinta_id = o.id
  from ora o, cine c, lectia
 where rc.sedinta_id is null
   and rc.exercitiu_id like lectia.cap || '-%'
   and c.user_id = rc.user_id
   and (o.grupa_id is null or o.grupa_id = c.grupa_id)
   and rc.creat_la between o.deschisa_la and o.gata;

-- 3. prezența, din răspunsuri, pentru orele închise ale lecției
with lectia as (select 'c4'::text as cap)
insert into public.prezente (user_id, curs, sedinta_id, marcat_la)
select i.user_id, s.capitol, s.id, min(i.creat_la)
  from public.sedinte s
  join public.incercari i on i.sedinta_id = s.id
  join lectia on s.capitol = lectia.cap
 where s.inchisa_la is not null
 group by i.user_id, s.capitol, s.id
on conflict do nothing;

commit;


-- D. Verificarea de după: pe fiecare oră C4, câți au răspuns și câți sunt
--    prezenți (trebuie egale), plus câte răspunsuri au rămas fără oră.
with lectia as (select 'c4'::text as cap)
select s.titlu, s.deschisa_la::date as ziua, s.inchisa_la,
       (select count(distinct i.user_id) from public.incercari i where i.sedinta_id = s.id) as au_raspuns,
       (select count(*) from public.prezente z where z.sedinta_id = s.id)                   as prezenti
  from public.sedinte s, lectia
 where s.capitol = lectia.cap
 order by s.deschisa_la;

with lectia as (select 'c4'::text as cap)
select count(*) as raspunsuri_ramase_fara_ora, count(distinct i.user_id) as studenti
  from public.incercari i, lectia
 where i.sarcina_id like lectia.cap || '-%' and i.sedinta_id is null;
