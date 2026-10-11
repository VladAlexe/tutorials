-- ===========================================================================
-- 09. NOTELE, STRÂNSE PE GRUPĂ
--
-- Un singur rând pe student, cu tot ce intră în notă: câte verificări a dat,
-- câte exerciții cu cod i-au mers, la câte ore a fost. Punctele în sine nu se
-- calculează aici: schema de notare stă în js/curs.js, într-un singur loc, și
-- pagina o aplică peste cifrele astea.
--
-- Apare și cine n-a intrat niciodată: un student care lipsește din listă e o
-- informație, nu un rând de șters.
--
-- Se rulează o singură dată, după 08. Se poate rula din nou fără stricăciuni.
-- ===========================================================================

create or replace function public.sumar_note()
returns table (
  matricol text, nume text, grupa text,
  are_cont boolean, invitat boolean,
  verif_date int, verif_corecte int,
  cod_trecut int, cod_incercat int,
  prezente int,
  ultima_data timestamptz
)
language sql security definer stable set search_path = public as $$
  with eu as (select 1 where public.sunt_profesor()),
  rs as (
    select p.matricol,
           count(*)::int                         as verif_date,
           count(*) filter (where r.corect)::int as verif_corecte
      from public.profiluri p
      join public.raspunsuri r on r.user_id = p.user_id
     group by p.matricol
  ),
  cd as (
    -- un exercițiu se pune la socoteală o singură dată, oricâte încercări
    select p.matricol,
           count(distinct c.exercitiu_id) filter (where c.trecut)::int as cod_trecut,
           count(distinct c.exercitiu_id)::int                         as cod_incercat
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
         (p.user_id is not null)        as are_cont,
         coalesce(s.invitat, false)     as invitat,
         coalesce(rs.verif_date, 0),
         coalesce(rs.verif_corecte, 0),
         coalesce(cd.cod_trecut, 0),
         coalesce(cd.cod_incercat, 0),
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

-- --------------------------------------------- prezența, pe toate orele ---
-- Cine a fost la care ședință, într-un singur tabel, ca să nu cer de opt ori.

create or replace function public.sumar_prezente_toate()
returns table (matricol text, nume text, grupa text, curs text, marcat_la timestamptz)
language sql security definer stable set search_path = public as $$
  select coalesce(p.matricol, '—'),
         coalesce(s.nume, 'fără cont legat'),
         s.grupa, z.curs, z.marcat_la
    from public.prezente z
    left join public.profiluri p on p.user_id = z.user_id
    left join public.studenti  s on s.matricol = p.matricol
   where public.sunt_profesor()
   order by z.marcat_la desc;
$$;

grant execute on function public.sumar_note()            to authenticated;
grant execute on function public.sumar_prezente_toate()  to authenticated;
