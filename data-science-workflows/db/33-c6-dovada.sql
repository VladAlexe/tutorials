-- ===========================================================================
-- 33. Lecția 6: ultima sarcină („Verificarea în caiet”, c6-dovada)
--
-- Se rulează în Supabase (SQL Editor). Toți cei prezenți la ora C6 primesc
-- sarcina c6-dovada ca rezolvată la oră. E sigur de rulat din nou: nu dublează
-- nimic (sare peste cei care o au deja rezolvată la oră).
--
-- De ce creat_la = începutul orei: activitatea ia PRIMUL răspuns de la oră
-- (js/curs.js). Rândul pus aici trebuie să fie primul, altfel o încercare
-- greșită de mai devreme ar rămâne cea care contează.
--
-- Ordinea: A (doar citește), apoi B (tranzacția), apoi C (verificarea).
-- ===========================================================================

-- A. Înainte: pe fiecare oră C6, câți sunt prezenți și câți au deja sarcina
select s.titlu, s.deschisa_la::date as ziua,
       (select count(*) from public.prezente z where z.sedinta_id = s.id) as prezenti,
       (select count(distinct rc.user_id) from public.rulari_cod rc
         where rc.sedinta_id = s.id and rc.trecut and rc.exercitiu_id = 'c6-dovada') as au_dovada
  from public.sedinte s
 where s.capitol = 'c6' and s.arhivata_la is null
 order by s.deschisa_la;


-- B. Punctaj întreg la c6-dovada pentru toți cei prezenți la C6
begin;

insert into public.rulari_cod (user_id, exercitiu_id, cod, trecut, sedinta_id, creat_la)
select z.user_id, 'c6-dovada', 'acordat de profesor', true, z.sedinta_id, s.deschisa_la
  from public.prezente z
  join public.sedinte s on s.id = z.sedinta_id
 where s.capitol = 'c6' and s.arhivata_la is null
   and not exists (select 1 from public.rulari_cod rc
                    where rc.user_id = z.user_id
                      and rc.exercitiu_id = 'c6-dovada'
                      and rc.sedinta_id is not null
                      and rc.trecut
                      and rc.creat_la <= s.deschisa_la);

commit;


-- C. După: „au_dovada” trebuie să fie egal cu „prezenti”
select s.titlu, s.deschisa_la::date as ziua,
       (select count(*) from public.prezente z where z.sedinta_id = s.id) as prezenti,
       (select count(distinct rc.user_id) from public.rulari_cod rc
         where rc.sedinta_id = s.id and rc.trecut and rc.exercitiu_id = 'c6-dovada') as au_dovada
  from public.sedinte s
 where s.capitol = 'c6' and s.arhivata_la is null
 order by s.deschisa_la;
