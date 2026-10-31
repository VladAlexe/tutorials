-- ===========================================================================
-- 27. Reparația prezențelor
--
-- Se rulează o dată, în Supabase (SQL Editor), după 26. Comportamentul orei
-- nu se schimbă: prezența se calculează tot la închiderea orei, din
-- răspunsurile date în timpul ei. Fișierul repară două lucruri:
--
--   1. Cheia tabelului `prezente` era (user_id, curs): un student putea fi
--      prezent o singură dată pe lecție, deci a doua oră din aceeași lecție
--      (de exemplu C1 predată de două ori) rămânea fără prezențe. Cheia devine
--      (user_id, sedinta_id): o prezență pe oră. Este secțiunea F din 14,
--      care nu fusese rulată. Se șterg doar prezențele vechi fără oră
--      (codurile QR de dinainte de ședințe); catalogul nu le afișa oricum.
--   2. Orele rămase deschise peste 3 ore se închid acum (ca și cum s-ar fi
--      închis singure), iar prezența se recalculează pentru toate orele
--      închise, din răspunsurile deja date. Nu se pierde nimic: cine a
--      răspuns la oră apare prezent.
--
-- Atenție: recalcularea pune la loc și o prezență scoasă de mână dintr-un
-- raport, dacă studentul a răspuns la acea oră.
-- ===========================================================================

begin;

-- 1. cheia nouă: o prezență pe oră
delete from public.prezente where sedinta_id is null;
alter table public.prezente drop constraint if exists prezente_pkey;
alter table public.prezente alter column sedinta_id set not null;
alter table public.prezente add primary key (user_id, sedinta_id);

-- 2. orele uitate deschise se închid (și primesc prezența)
select public.inchide_orele_uitate();

-- 3. prezența pentru toate orele închise, din răspunsuri
insert into public.prezente (user_id, curs, sedinta_id, marcat_la)
select i.user_id, s.capitol, s.id, min(i.creat_la)
  from public.sedinte s
  join public.incercari i on i.sedinta_id = s.id
 where s.inchisa_la is not null
 group by i.user_id, s.capitol, s.id
on conflict do nothing;

commit;

-- Verificare: pe fiecare oră, câți au răspuns și câți sunt prezenți (trebuie egale)
select s.capitol, s.deschisa_la::date as ziua,
       (select count(distinct i.user_id) from public.incercari i where i.sedinta_id = s.id) as au_raspuns,
       (select count(*) from public.prezente z where z.sedinta_id = s.id) as prezenti
  from public.sedinte s
 order by s.deschisa_la;
