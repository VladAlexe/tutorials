-- ===========================================================================
-- 20. GRUPELE, NOTA TRANSPARENTĂ ȘI CURĂȚENIA
--
-- Se rulează o dată, în Supabase (SQL Editor), după 19. Înlocuiește funcția
-- `catalog` din 18 (aceeași idee, date mai curate).
--
-- 1. catalog          un rând pe student, cu grupa lui. Pentru fiecare
--                     întrebare: primul răspuns la oră, primul acasă, și câte
--                     încercări a avut în total. Restul încercărilor nu mai
--                     contează (regula din js/curs.js, „două șanse”).
--                     Orele arhivate (de test) nu intră nicăieri.
-- 2. ore_lista        orele, cu grupa fiecăreia, ca panoul să le filtreze
-- 3. trimise_in_sedinta  ce a trimis fiecare la un exercițiu, DOAR în ora dată
-- 4. sterge_sedinta   șterge de tot o oră, cu tot ce s-a lucrat în ea
-- 5. sterge_invitati  șterge toți invitații, cu tot ce au lucrat
-- ===========================================================================

drop function if exists public.catalog();
create function public.catalog()
returns table (matricol text, nume text, grupa_id text, grupa text,
               are_cont boolean, invitat boolean,
               prezente text[], rezolvari jsonb, note jsonb, ultima timestamptz)
language sql security definer stable set search_path = public as $$
  with eu as (select 1 where public.sunt_profesor()),
  pz as (
    select p.matricol, array_agg(distinct z.curs order by z.curs) as prezente
      from public.prezente z
      join public.profiluri p on p.user_id = z.user_id
      join public.sedinte s on s.id = z.sedinta_id
     where s.arhivata_la is null
     group by p.matricol
  ),
  inc as (
    select p.matricol, i.sarcina_id, i.corect, i.gol, i.creat_la,
           (i.sedinta_id is not null) as la_ora
      from public.incercari i
      join public.profiluri p on p.user_id = i.user_id
      left join public.sedinte s on s.id = i.sedinta_id
     where i.sedinta_id is null or s.arhivata_la is null
  ),
  prime as (
    select matricol, sarcina_id,
           (array_agg(corect order by creat_la) filter (where la_ora and not gol))[1]     as la_ora_ok,
           (array_agg(corect order by creat_la) filter (where not la_ora and not gol))[1] as acasa_ok,
           count(*)::int as n,
           max(creat_la) as ultima
      from inc
     group by matricol, sarcina_id
  ),
  rez as (
    select matricol, jsonb_agg(jsonb_build_array(sarcina_id, la_ora_ok, acasa_ok, n)) as rezolvari,
           max(ultima) as ultima
      from prime group by matricol
  ),
  nt as (
    select n.matricol, jsonb_object_agg(n.cheie, n.puncte) as note
      from public.note_manuale n group by n.matricol
  )
  select s.matricol, s.nume, s.grupa_id,
         coalesce((select g.nume from public.grupe g where g.id = s.grupa_id), s.grupa),
         exists (select 1 from public.profiluri p where p.matricol = s.matricol),
         coalesce(s.invitat, false) or s.matricol like 'G-%',
         coalesce(pz.prezente, '{}'),
         coalesce(rez.rezolvari, '[]'::jsonb),
         coalesce(nt.note, '{}'::jsonb),
         rez.ultima
    from eu, public.studenti s
    left join pz  on pz.matricol  = s.matricol
    left join rez on rez.matricol = s.matricol
    left join nt  on nt.matricol  = s.matricol
   order by s.nume;
$$;


create or replace function public.ore_lista(p_arhivate boolean default false)
returns table (id uuid, titlu text, capitol text, grupa_id text, grupa text,
               deschisa_la timestamptz, inchisa_la timestamptz,
               minute int, prezenti int, zile_ramase int)
language sql security definer stable set search_path = public as $$
  select s.id, s.titlu, s.capitol, s.grupa_id,
         (select nume from public.grupe where id = s.grupa_id),
         s.deschisa_la, s.inchisa_la,
         round(extract(epoch from coalesce(s.inchisa_la, now()) - s.deschisa_la)/60)::int,
         (select count(*)::int from public.prezente where sedinta_id = s.id),
         case when s.arhivata_la is null then null
              else greatest(0, 30 - extract(day from now() - s.arhivata_la)::int) end
    from public.sedinte s
   where public.sunt_profesor()
     and (s.arhivata_la is not null) = p_arhivate
   order by s.deschisa_la desc;
$$;


-- Ce a trimis fiecare la exercițiile date, în ora asta și numai în ea:
-- ultimul răspuns ne-gol, pe om și pe exercițiu.
create or replace function public.trimise_in_sedinta(p_sedinta uuid, p_sarcini text[])
returns table (matricol text, nume text, sarcina text, cod text, trecut boolean, creat_la timestamptz)
language sql security definer stable set search_path = public as $$
  select distinct on (c.user_id, c.exercitiu_id)
         coalesce(p.matricol, '—'), coalesce(st.nume, 'fără cont legat'),
         c.exercitiu_id, c.cod, coalesce(c.trecut, false), c.creat_la
    from public.rulari_cod c
    left join public.profiluri p on p.user_id = c.user_id
    left join public.studenti st on st.matricol = p.matricol
   where public.sunt_profesor()
     and c.sedinta_id = p_sedinta
     and c.exercitiu_id = any(p_sarcini)
     and coalesce(btrim(c.cod), '') <> ''
   order by c.user_id, c.exercitiu_id, c.creat_la desc;
$$;


-- Ștergerea definitivă a unei ore. Cascada ia cu ea răspunsurile, codul,
-- prezențele și evenimentele legate de ora aceea. Ce au lucrat acasă rămâne.
create or replace function public.sterge_sedinta(p_id uuid)
returns jsonb
language plpgsql security definer set search_path = public as $$
begin
  if not public.sunt_profesor() then
    return jsonb_build_object('ok', false, 'mesaj', 'Numai profesorul poate face asta.');
  end if;
  delete from public.sedinte where id = p_id;
  return jsonb_build_object('ok', true);
end $$;


-- Toți invitații, cu tot ce au lucrat. Conturile lor de invitat se șterg, iar
-- cascada din auth.users ia cu ea răspunsurile, codul, prezențele, jurnalul.
create or replace function public.sterge_invitati()
returns jsonb
language plpgsql security definer set search_path = public, auth as $$
declare n int;
begin
  if not public.sunt_profesor() then
    return jsonb_build_object('ok', false, 'mesaj', 'Numai profesorul poate face asta.');
  end if;
  delete from auth.users u
   using public.profiluri p
   where p.user_id = u.id
     and p.matricol in (select matricol from public.studenti
                         where coalesce(invitat, false) or matricol like 'G-%')
     and not exists (select 1 from public.profesori f where f.user_id = u.id);
  get diagnostics n = row_count;
  delete from public.note_manuale where matricol like 'G-%'
     or matricol in (select matricol from public.studenti where coalesce(invitat, false));
  delete from public.studenti s
   where (coalesce(s.invitat, false) or s.matricol like 'G-%')
     and not exists (select 1 from public.profiluri p where p.matricol = s.matricol);
  return jsonb_build_object('ok', true, 'conturi', n);
end $$;

grant execute on function public.catalog()                         to authenticated;
grant execute on function public.ore_lista(boolean)                to authenticated;
grant execute on function public.trimise_in_sedinta(uuid, text[])  to authenticated;
grant execute on function public.sterge_sedinta(uuid)              to authenticated;
grant execute on function public.sterge_invitati()                 to authenticated;
