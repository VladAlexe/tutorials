-- ===========================================================================
-- 11. DE UNDE VINE FIECARE RĂSPUNS, ȘI CINE NU E STUDENT
--
-- Două lucruri care lipseau și fără care panoul minte.
--
-- 1. Contextul. Un exercițiu făcut în oră, cu mine de față, nu e același lucru
--    cu unul făcut marți seara din manual. Amândouă contează, dar trebuie să
--    le pot deosebi. De acum fiecare răspuns și fiecare rulare de cod poartă
--    cu ea de unde vine:
--      'live'     — în oră, cât ora era condusă de mine
--      'lectie'   — pe pagina lecției, dar singur, fără oră pornită
--      'manual'   — în tutorial, oricând
--
-- 2. Profesorul nu e student. Contul meu apărea în „cine e în lecție acum" și
--    în prezențe, ceea ce umfla cifrele cu exact un om: eu.
--
-- Se rulează o singură dată, după 10. Se poate rula din nou fără stricăciuni.
-- ===========================================================================

alter table public.raspunsuri  add column if not exists context text;
alter table public.rulari_cod  add column if not exists context text;

create index if not exists raspunsuri_context_idx on public.raspunsuri (context);
create index if not exists rulari_context_idx     on public.rulari_cod (context);

-- ----------------------------------------------------------- cine e în sală
-- Fără mine. Un profesor care deschide lecția ca s-o proiecteze nu e un
-- student în plus.

drop function if exists public.live_acum(int);
create or replace function public.live_acum(p_minute int default 3)
returns table (
  matricol text, nume text, grupa text,
  capitol text, slide_nr int, total_nr int,
  de_cat_timp int, intrat_de int, invitat boolean
)
language sql security definer stable set search_path = public as $$
  select coalesce(p.matricol, '—')                       as matricol,
         coalesce(st.nume, u.email, 'fără cont legat')    as nume,
         st.grupa,
         s.capitol, s.slide_nr, s.total_nr,
         extract(epoch from (now() - s.vazut_la))::int    as de_cat_timp,
         extract(epoch from (now() - s.inceput))::int     as intrat_de,
         coalesce(st.invitat, false)                      as invitat
    from public.sesiuni s
    join auth.users u            on u.id = s.user_id
    left join public.profiluri p on p.user_id = s.user_id
    left join public.studenti st on st.matricol = p.matricol
   where public.sunt_profesor()
     and s.vazut_la > now() - make_interval(mins => greatest(p_minute, 1))
     and not exists (select 1 from public.profesori f where f.user_id = s.user_id)
   order by s.slide_nr nulls last, st.nume;
$$;

-- -------------------------------------------------------------- prezențele
drop function if exists public.sumar_prezenta(text);
create or replace function public.sumar_prezenta(p_curs text)
returns table (matricol text, nume text, grupa text, invitat boolean,
               marcat_la timestamptz)
language sql security definer stable set search_path = public as $$
  select coalesce(p.matricol, '—'),
         coalesce(s.nume, 'fără cont legat'),
         s.grupa,
         coalesce(s.invitat, false),
         z.marcat_la
    from public.prezente z
    left join public.profiluri p on p.user_id = z.user_id
    left join public.studenti  s on s.matricol = p.matricol
   where public.sunt_profesor() and z.curs = p_curs
     and not exists (select 1 from public.profesori f where f.user_id = z.user_id)
   order by z.marcat_la;
$$;

drop function if exists public.sumar_prezente_toate();
create or replace function public.sumar_prezente_toate()
returns table (matricol text, nume text, grupa text, curs text,
               marcat_la timestamptz)
language sql security definer stable set search_path = public as $$
  select coalesce(p.matricol, '—'),
         coalesce(s.nume, 'fără cont legat'),
         s.grupa, z.curs, z.marcat_la
    from public.prezente z
    left join public.profiluri p on p.user_id = z.user_id
    left join public.studenti  s on s.matricol = p.matricol
   where public.sunt_profesor()
     and not exists (select 1 from public.profesori f where f.user_id = z.user_id)
   order by z.marcat_la desc;
$$;

-- ------------------------------------------------------- codul, cu context
drop function if exists public.sumar_cod(text);
create or replace function public.sumar_cod(p_exercitiu text default null)
returns table (
  exercitiu_id text, matricol text, nume text, grupa text,
  cod text, trecut boolean, context text,
  creat_la timestamptz, incercari int
)
language sql security definer stable set search_path = public as $$
  with r as (
    select c.*, p.matricol,
           row_number() over (partition by c.user_id, c.exercitiu_id
                              order by c.creat_la desc) as rn,
           count(*)    over (partition by c.user_id, c.exercitiu_id) as incercari
      from public.rulari_cod c
      left join public.profiluri p on p.user_id = c.user_id
     where public.sunt_profesor()
       and (p_exercitiu is null or c.exercitiu_id = p_exercitiu)
       and not exists (select 1 from public.profesori f where f.user_id = c.user_id)
  )
  select r.exercitiu_id, coalesce(r.matricol, '—'),
         coalesce(s.nume, 'fără cont legat'), s.grupa,
         r.cod, r.trecut, coalesce(r.context, 'necunoscut'),
         r.creat_la, r.incercari::int
    from r left join public.studenti s on s.matricol = r.matricol
   where r.rn = 1
   order by r.exercitiu_id, s.nume;
$$;

-- ------------------------------------------- fiecare răspuns, cu de-unde-vine
-- Pentru grila „cine ce a făcut și unde": un rând per student și sarcină.

create or replace function public.sumar_sarcini(p_capitol text default null)
returns table (
  matricol text, nume text, grupa text,
  sarcina text, fel text, reusit boolean, context text, creat_la timestamptz
)
language sql security definer stable set search_path = public as $$
  with eu as (select 1 where public.sunt_profesor()),
  v as (
    select distinct on (r.user_id, r.intrebare_id)
           r.user_id, r.intrebare_id as sarcina, 'verificare'::text as fel,
           r.corect as reusit, coalesce(r.context,'necunoscut') as context, r.creat_la
      from public.raspunsuri r
     where (p_capitol is null or r.capitol = p_capitol)
     order by r.user_id, r.intrebare_id, r.corect desc, r.creat_la
  ),
  c as (
    select distinct on (k.user_id, k.exercitiu_id)
           k.user_id, k.exercitiu_id as sarcina, 'cod'::text as fel,
           k.trecut as reusit, coalesce(k.context,'necunoscut') as context, k.creat_la
      from public.rulari_cod k
     where (p_capitol is null or k.exercitiu_id like p_capitol || '-%')
     order by k.user_id, k.exercitiu_id, k.trecut desc, k.creat_la
  ),
  t as (select * from v union all select * from c)
  select coalesce(p.matricol, '—'), coalesce(s.nume, 'fără cont legat'), s.grupa,
         t.sarcina, t.fel, t.reusit, t.context, t.creat_la
    from eu, t
    left join public.profiluri p on p.user_id = t.user_id
    left join public.studenti  s on s.matricol = p.matricol
   where not exists (select 1 from public.profesori f where f.user_id = t.user_id)
   order by s.nume nulls last, t.sarcina;
$$;

-- ----------------------------------------------- notele, cu live și cu după
drop function if exists public.sumar_note();
create or replace function public.sumar_note()
returns table (
  matricol text, nume text, grupa text,
  are_cont boolean, invitat boolean,
  verif_date int, verif_corecte int,
  cod_trecut int, cod_incercat int,
  facute_live int, facute_singur int,
  prezente int,
  ultima_data timestamptz
)
language sql security definer stable set search_path = public as $$
  with eu as (select 1 where public.sunt_profesor()),
  rs as (
    select p.matricol,
           count(distinct r.intrebare_id)::int                      as verif_date,
           count(distinct r.intrebare_id) filter (where r.corect)::int as verif_corecte,
           count(distinct r.intrebare_id) filter (where r.context = 'live')::int  as v_live,
           count(distinct r.intrebare_id) filter (where r.context is distinct from 'live')::int as v_singur
      from public.profiluri p
      join public.raspunsuri r on r.user_id = p.user_id
     group by p.matricol
  ),
  cd as (
    select p.matricol,
           count(distinct c.exercitiu_id) filter (where c.trecut)::int as cod_trecut,
           count(distinct c.exercitiu_id)::int                         as cod_incercat,
           count(distinct c.exercitiu_id) filter (where c.trecut and c.context = 'live')::int as c_live,
           count(distinct c.exercitiu_id) filter (where c.trecut and c.context is distinct from 'live')::int as c_singur
      from public.profiluri p
      join public.rulari_cod c on c.user_id = p.user_id
     group by p.matricol
  ),
  pz as (
    select p.matricol, count(*)::int as prezente
      from public.profiluri p
      join public.prezente z on z.user_id = p.user_id
     group by p.matricol
  ),
  ul as (
    select p.matricol, max(g.ultima_data) as ultima_data
      from public.profiluri p
      join public.progres g on g.user_id = p.user_id
     group by p.matricol
  )
  select s.matricol, s.nume, s.grupa,
         (p.user_id is not null), coalesce(s.invitat, false),
         coalesce(rs.verif_date, 0), coalesce(rs.verif_corecte, 0),
         coalesce(cd.cod_trecut, 0), coalesce(cd.cod_incercat, 0),
         coalesce(rs.v_live, 0)   + coalesce(cd.c_live, 0),
         coalesce(rs.v_singur, 0) + coalesce(cd.c_singur, 0),
         coalesce(pz.prezente, 0),
         ul.ultima_data
    from eu, public.studenti s
    left join public.profiluri p on p.matricol = s.matricol
    left join rs on rs.matricol = s.matricol
    left join cd on cd.matricol = s.matricol
    left join pz on pz.matricol = s.matricol
    left join ul on ul.matricol = s.matricol
   order by s.grupa nulls last, s.nume;
$$;

grant execute on function public.sumar_sarcini(text) to authenticated;
