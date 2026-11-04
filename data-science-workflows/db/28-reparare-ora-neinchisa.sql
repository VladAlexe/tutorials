-- ===========================================================================
-- 28. Ora rămasă deschisă: prezențele și punctajele unei lecții
--
-- Se rulează în Supabase (SQL Editor), după 27, când o oră n-a fost închisă la
-- timp. Lecția se alege într-un singur loc: 'c3' din blocul `lectia` de mai
-- jos (pentru C2: 'c2'). E sigur de rulat din nou: nu dublează nimic.
--
-- Pașii, toți într-o tranzacție:
--   0. Verificarea de dinainte (doar citește): orele lecției și câte răspunsuri
--      au rămas fără oră.
--   1. Ora rămasă deschisă se închide, ca la închiderea automată.
--   2. Răspunsurile date ÎN TIMPUL orei, dar înregistrate fără oră (de exemplu,
--      studentul nu intrase cu codul), se leagă de ora grupei lui. Așa contează
--      ca răspunsuri la oră: punctaj întreg, nu jumătate.
--   3. Prezența se recalculează din răspunsuri: cine a răspuns la oră e prezent.
--   4. Lecția 3, ultimele două sarcini:
--      - verificarea depozitului: punctaj întreg pentru TOȚI cei prezenți la
--        oră, cum s-a anunțat la curs. Cine a rezolvat-o păstrează rezolvarea
--        lui (legată de oră); celorlalți li se adaugă un rând marcat
--        „acordat de profesor”, ca să se vadă că nu e o rezolvare;
--      - întrebarea echipei: doar cei prezenți care au trimis textul, chiar
--        dacă l-au trimis după oră. Cine nu l-a trimis nu primește nimic.
--
-- În rest nu se inventează niciun răspuns: se schimbă doar legătura cu ora.
-- ===========================================================================

-- 0. Verificarea de dinainte: rulează doar blocul acesta, întâi, și uită-te la cifre.
with lectia as (select 'c3'::text as cap)
select s.capitol, s.titlu, s.deschisa_la, s.inchisa_la, s.arhivata_la,
       (select count(distinct i.user_id) from public.incercari i where i.sedinta_id = s.id) as au_raspuns_la_ora,
       (select count(*) from public.prezente z where z.sedinta_id = s.id)                   as prezenti
  from public.sedinte s, lectia
 where s.capitol = lectia.cap
 order by s.deschisa_la;

with lectia as (select 'c3'::text as cap)
select count(*) as raspunsuri_fara_ora, count(distinct i.user_id) as studenti
  from public.incercari i, lectia
 where i.sarcina_id like lectia.cap || '-%' and i.sedinta_id is null;


begin;

-- 1. orele uitate deschise (peste 3 ore) se închid și primesc prezența
select public.inchide_orele_uitate();

-- 2. răspunsurile din timpul orei, legate de ora grupei
with lectia as (select 'c3'::text as cap),
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

with lectia as (select 'c3'::text as cap),
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
with lectia as (select 'c3'::text as cap)
insert into public.prezente (user_id, curs, sedinta_id, marcat_la)
select i.user_id, s.capitol, s.id, min(i.creat_la)
  from public.sedinte s
  join public.incercari i on i.sedinta_id = s.id
  join lectia on s.capitol = lectia.cap
 where s.inchisa_la is not null
 group by i.user_id, s.capitol, s.id
on conflict do nothing;

-- 4a. lecția 3: rezolvările trimise după oră, de cei prezenți, se leagă de oră
update public.rulari_cod rc
   set sedinta_id = z.sedinta_id
  from public.prezente z
  join public.sedinte s on s.id = z.sedinta_id
 where s.capitol = 'c3' and s.arhivata_la is null
   and rc.user_id = z.user_id
   and rc.sedinta_id is null
   and rc.trecut
   and rc.exercitiu_id in ('c3-dovada-depozit', 'c3-intrebare');

-- 4b. verificarea depozitului: punctaj întreg pentru toți cei prezenți la C3
--     care nu au deja o rezolvare la oră
insert into public.rulari_cod (user_id, exercitiu_id, cod, trecut, sedinta_id, creat_la)
select z.user_id, 'c3-dovada-depozit', 'acordat de profesor', true, z.sedinta_id, s.deschisa_la + interval '1 hour'
  from public.prezente z
  join public.sedinte s on s.id = z.sedinta_id
 where s.capitol = 'c3' and s.arhivata_la is null
   and not exists (select 1 from public.rulari_cod rc
                    where rc.user_id = z.user_id
                      and rc.exercitiu_id = 'c3-dovada-depozit'
                      and rc.sedinta_id is not null
                      and rc.trecut);

commit;


-- Verificarea de după: pe fiecare oră a lecției, câți au răspuns, câți sunt
-- prezenți (trebuie egale) și câți au trimis ultimele două sarcini.
with lectia as (select 'c3'::text as cap)
select s.titlu, s.deschisa_la::date as ziua, s.inchisa_la,
       (select count(distinct i.user_id) from public.incercari i where i.sedinta_id = s.id) as au_raspuns,
       (select count(*) from public.prezente z where z.sedinta_id = s.id)                   as prezenti,
       (select count(distinct rc.user_id) from public.rulari_cod rc
         where rc.sedinta_id = s.id and rc.trecut and rc.exercitiu_id = 'c3-dovada-depozit') as depozit_verificat,
       (select count(distinct rc.user_id) from public.rulari_cod rc
         where rc.sedinta_id = s.id and rc.trecut and rc.exercitiu_id = 'c3-intrebare')      as intrebare_scrisa
  from public.sedinte s, lectia
 where s.capitol = lectia.cap
 order by s.deschisa_la;


-- ---------------------------------------------------------------------------
-- Ca să nu se mai întâmple: închiderea automată, la fiecare jumătate de oră.
-- Opțional. Cere extensia pg_cron (Database → Extensions → pg_cron → Enable).
-- Apoi rulează, o singură dată, rândul de mai jos (fără cele două liniuțe):
--
-- select cron.schedule('inchide-orele-uitate', '*/30 * * * *', $$select public.inchide_orele_uitate()$$);
--
-- O oră uitată deschisă se închide singură la 3 ore de la pornire, iar
-- prezențele apar fără nicio intervenție.
-- ---------------------------------------------------------------------------
