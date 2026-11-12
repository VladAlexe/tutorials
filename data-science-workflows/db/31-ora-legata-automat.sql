-- ===========================================================================
-- 31. Răspunsurile din timpul orei se leagă singure de oră
--
-- Se rulează în Supabase (SQL Editor). E sigur de rulat din nou: nu dublează
-- nimic și nu inventează răspunsuri.
--
-- Problema, la fiecare lecție (C2, C3, C4, C5): o parte din răspunsurile date
-- în timpul orei se salvau fără oră (sedinta_id gol). Pagina studentului
-- leagă răspunsul de oră doar dacă a aflat, la timp, că ora e deschisă (din
-- ora_acum). Cine a deschis lecția înainte de pornirea orei, cine a răspuns
-- înainte de prima verificare a paginii sau cine a lucrat din manual salva
-- „fără oră”. Asemenea răspunsuri nu dau prezență, iar în catalog contează
-- ca făcute acasă (jumătate) sau deloc. Până acum s-au reparat de mână, după
-- fiecare lecție (28, 30).
--
-- Reparația de aici are două părți:
--   B. Pe viitor, baza leagă singură răspunsul de oră, în momentul salvării:
--      dacă răspunsul vine fără oră, dar grupa studentului are o oră deschisă
--      la lecția aceea, primește ora. Nu mai depinde de pagina studentului.
--   C. Pentru trecut, aceeași regulă ca în 28 și 30, pentru TOATE lecțiile
--      deodată: răspunsurile date în intervalul unei ore, de un student din
--      grupa ei, se leagă de ora aceea; apoi se scrie prezența.
--
-- Ordinea:
--   A. doar citește: ce lipsește acum, pe lecții (rezultatul se păstrează);
--   B. o singură dată: funcțiile și declanșatoarele;
--   C. tranzacția: reparația trecutului;
--   D. doar citește: verificarea (rândurile „fără oră” din timpul orelor = 0).
-- ===========================================================================


-- A. Ce lipsește acum ------------------------------------------------------

-- A1. Prezența imediată (29) este instalată? Trebuie să apară două rânduri.
--     Dacă nu apare niciunul, partea B de mai jos o instalează.
select tgname, tgrelid::regclass as tabelul
  from pg_trigger
 where tgname in ('prezenta_din_raspuns', 'prezenta_din_cod');

-- A2. Orele fiecărei lecții: câți au răspuns la oră și câți sunt prezenți.
select s.capitol, s.titlu, s.deschisa_la::date as ziua, s.inchisa_la is null as inca_deschisa,
       (select count(distinct i.user_id) from public.incercari i where i.sedinta_id = s.id) as au_raspuns_la_ora,
       (select count(*) from public.prezente z where z.sedinta_id = s.id)                   as prezenti
  from public.sedinte s
 where s.arhivata_la is null
 order by s.deschisa_la;

-- A3. Răspunsurile date ÎN TIMPUL unei ore a grupei, dar salvate fără oră.
--     Acestea sunt cele care lipsesc din catalog.
with ora as (
  select s.id, s.capitol, s.grupa_id, s.deschisa_la,
         coalesce(s.inchisa_la, s.deschisa_la + interval '3 hours') as gata
    from public.sedinte s
   where s.arhivata_la is null
),
cine as (
  select p.user_id, st.grupa_id
    from public.profiluri p
    left join public.studenti st on st.matricol = p.matricol
)
select o.capitol, count(*) as raspunsuri_fara_ora, count(distinct i.user_id) as studenti
  from public.incercari i
  join cine c on c.user_id = i.user_id
  join ora o on split_part(i.sarcina_id, '-', 1) = o.capitol
            and (o.grupa_id is null or o.grupa_id = c.grupa_id)
            and i.creat_la between o.deschisa_la and o.gata
 where i.sedinta_id is null
 group by o.capitol
 order by o.capitol;


-- B. Pe viitor: legarea automată (o singură dată) ---------------------------

-- B1. Înainte de salvare: un răspuns fără oră primește ora deschisă a grupei,
--     la lecția lui. Lecția se citește din id: 'c5-...' -> 'c5'.
create or replace function public.leaga_de_ora()
returns trigger
language plpgsql security definer set search_path = public as $$
declare
  cap text := split_part(coalesce(to_jsonb(new) ->> 'intrebare_id', to_jsonb(new) ->> 'exercitiu_id'), '-', 1);
begin
  if new.sedinta_id is null then
    select s.id into new.sedinta_id
      from public.sedinte s
      join public.profiluri p on p.user_id = new.user_id
      left join public.studenti st on st.matricol = p.matricol
     where s.capitol = cap
       and s.arhivata_la is null
       and s.inchisa_la is null
       and s.deschisa_la <= now()
       and s.deschisa_la > now() - interval '3 hours'
       and (s.grupa_id is null or s.grupa_id = st.grupa_id)
     order by s.deschisa_la desc
     limit 1;
  end if;
  return new;
end $$;

drop trigger if exists leaga_raspuns_de_ora on public.raspunsuri;
create trigger leaga_raspuns_de_ora
  before insert on public.raspunsuri
  for each row execute function public.leaga_de_ora();

drop trigger if exists leaga_cod_de_ora on public.rulari_cod;
create trigger leaga_cod_de_ora
  before insert on public.rulari_cod
  for each row execute function public.leaga_de_ora();

-- B2. După salvare: prezența se scrie imediat (aceeași funcție ca în 29).
create or replace function public.prezenta_din_raspuns()
returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if new.sedinta_id is not null then
    insert into public.prezente (user_id, curs, sedinta_id, marcat_la)
    select new.user_id, s.capitol, s.id, coalesce(new.creat_la, now())
      from public.sedinte s
     where s.id = new.sedinta_id
       and s.arhivata_la is null
    on conflict do nothing;
  end if;
  return new;
end $$;

drop trigger if exists prezenta_din_raspuns on public.raspunsuri;
create trigger prezenta_din_raspuns
  after insert or update of sedinta_id on public.raspunsuri
  for each row execute function public.prezenta_din_raspuns();

drop trigger if exists prezenta_din_cod on public.rulari_cod;
create trigger prezenta_din_cod
  after insert or update of sedinta_id on public.rulari_cod
  for each row execute function public.prezenta_din_raspuns();


-- C. Pentru trecut: toate lecțiile deodată ----------------------------------

begin;

-- C1. orele uitate deschise (peste 3 ore) se închid
select public.inchide_orele_uitate();

-- C2. verificările date în timpul orei grupei, legate de ora aceea
with ora as (
  select s.id, s.capitol, s.grupa_id, s.deschisa_la,
         coalesce(s.inchisa_la, s.deschisa_la + interval '3 hours') as gata
    from public.sedinte s
   where s.arhivata_la is null
),
cine as (
  select p.user_id, st.grupa_id
    from public.profiluri p
    left join public.studenti st on st.matricol = p.matricol
)
update public.raspunsuri r
   set sedinta_id = o.id
  from ora o, cine c
 where r.sedinta_id is null
   and split_part(r.intrebare_id, '-', 1) = o.capitol
   and c.user_id = r.user_id
   and (o.grupa_id is null or o.grupa_id = c.grupa_id)
   and r.creat_la between o.deschisa_la and o.gata;

-- C3. la fel, rulările de cod
with ora as (
  select s.id, s.capitol, s.grupa_id, s.deschisa_la,
         coalesce(s.inchisa_la, s.deschisa_la + interval '3 hours') as gata
    from public.sedinte s
   where s.arhivata_la is null
),
cine as (
  select p.user_id, st.grupa_id
    from public.profiluri p
    left join public.studenti st on st.matricol = p.matricol
)
update public.rulari_cod rc
   set sedinta_id = o.id
  from ora o, cine c
 where rc.sedinta_id is null
   and split_part(rc.exercitiu_id, '-', 1) = o.capitol
   and c.user_id = rc.user_id
   and (o.grupa_id is null or o.grupa_id = c.grupa_id)
   and rc.creat_la between o.deschisa_la and o.gata;

-- C4. prezența, din răspunsurile legate de ore
insert into public.prezente (user_id, curs, sedinta_id, marcat_la)
select i.user_id, s.capitol, s.id, min(i.creat_la)
  from public.sedinte s
  join public.incercari i on i.sedinta_id = s.id
 where s.arhivata_la is null
 group by i.user_id, s.capitol, s.id
on conflict do nothing;

commit;


-- D. Verificarea ------------------------------------------------------------

-- D1. Declanșatoarele: trebuie să apară patru rânduri.
select tgname, tgrelid::regclass as tabelul
  from pg_trigger
 where tgname in ('leaga_raspuns_de_ora', 'leaga_cod_de_ora', 'prezenta_din_raspuns', 'prezenta_din_cod')
 order by tgname;

-- D2. Pe fiecare oră: câți au răspuns și câți sunt prezenți (trebuie egale).
select s.capitol, s.titlu, s.deschisa_la::date as ziua,
       (select count(distinct i.user_id) from public.incercari i where i.sedinta_id = s.id) as au_raspuns_la_ora,
       (select count(*) from public.prezente z where z.sedinta_id = s.id)                   as prezenti
  from public.sedinte s
 where s.arhivata_la is null
 order by s.deschisa_la;

-- D3. Răspunsuri din timpul orelor rămase fără oră: trebuie să nu apară niciun rând.
with ora as (
  select s.id, s.capitol, s.grupa_id, s.deschisa_la,
         coalesce(s.inchisa_la, s.deschisa_la + interval '3 hours') as gata
    from public.sedinte s
   where s.arhivata_la is null
),
cine as (
  select p.user_id, st.grupa_id
    from public.profiluri p
    left join public.studenti st on st.matricol = p.matricol
)
select o.capitol, count(*) as raspunsuri_fara_ora
  from public.incercari i
  join cine c on c.user_id = i.user_id
  join ora o on split_part(i.sarcina_id, '-', 1) = o.capitol
            and (o.grupa_id is null or o.grupa_id = c.grupa_id)
            and i.creat_la between o.deschisa_la and o.gata
 where i.sedinta_id is null
 group by o.capitol;

-- D4. Studenții care au lucrat la C5, cu sau fără oră (ce ar trebui să vezi în catalog).
select coalesce(st.nume, p.matricol, i.user_id::text) as studentul,
       count(*) filter (where i.sedinta_id is not null) as la_ora,
       count(*) filter (where i.sedinta_id is null)     as acasa
  from public.incercari i
  left join public.profiluri p on p.user_id = i.user_id
  left join public.studenti st on st.matricol = p.matricol
 where i.sarcina_id like 'c5-%'
 group by 1
 order by 1;
