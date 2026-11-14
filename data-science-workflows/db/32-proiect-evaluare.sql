-- ===========================================================================
-- 32. EVALUAREA PROIECTULUI
--
-- Se rulează o dată, în Supabase (SQL Editor), după 23 (echipele).
--
-- Ce adaugă:
--   proiect_criterii   punctajele pe criterii, pe student (ciorna, în timpul
--                      prezentării); criteriile echipei se scriu la toți membrii
--   proiect_obs        observațiile pe echipă
--   pune_criteriu      scrie (sau șterge, cu null) un criteriu pentru unul sau
--                      mai mulți studenți; doar profesorul
--   pune_obs_proiect   scrie observațiile unei echipe; doar profesorul
--   proiect_evaluare   tot ce s-a notat pentru o grupă
--
-- Nota finală la proiect NU se scrie aici: o scrie butonul „Actualizează nota”
-- din pagina Predau, prin pune_nota(..., 'proiect', ...) din 18.
-- ===========================================================================

create table if not exists public.proiect_criterii (
  matricol      text not null references public.studenti(matricol) on delete cascade,
  criteriu      text not null check (criteriu in ('analiza','depozit','prezentare','pas','contributie')),
  puncte        numeric(3,2) not null check (puncte >= 0 and puncte <= 1),
  actualizat_la timestamptz not null default now(),
  primary key (matricol, criteriu)
);

create table if not exists public.proiect_obs (
  echipa_id     bigint primary key references public.echipe(id) on delete cascade,
  text          text not null default '',
  actualizat_la timestamptz not null default now()
);

alter table public.proiect_criterii enable row level security;
alter table public.proiect_obs enable row level security;
revoke all on public.proiect_criterii from anon, authenticated;
revoke all on public.proiect_obs from anon, authenticated;


create or replace function public.pune_criteriu(p_matricole text[], p_criteriu text, p_puncte numeric)
returns jsonb
language plpgsql security definer set search_path = public as $$
begin
  if not public.sunt_profesor() then
    return jsonb_build_object('ok', false, 'mesaj', 'Numai profesorul poate face asta.');
  end if;
  if p_puncte is null then
    delete from public.proiect_criterii where matricol = any(p_matricole) and criteriu = p_criteriu;
  else
    insert into public.proiect_criterii (matricol, criteriu, puncte)
    select m, p_criteriu, p_puncte from unnest(p_matricole) as m
    on conflict (matricol, criteriu)
      do update set puncte = excluded.puncte, actualizat_la = now();
  end if;
  return jsonb_build_object('ok', true);
end $$;


create or replace function public.pune_obs_proiect(p_echipa bigint, p_text text)
returns jsonb
language plpgsql security definer set search_path = public as $$
begin
  if not public.sunt_profesor() then
    return jsonb_build_object('ok', false, 'mesaj', 'Numai profesorul poate face asta.');
  end if;
  insert into public.proiect_obs (echipa_id, text) values (p_echipa, coalesce(p_text, ''))
  on conflict (echipa_id) do update set text = excluded.text, actualizat_la = now();
  return jsonb_build_object('ok', true);
end $$;


-- {"criterii": {"<matricol>": {"analiza": 1, ...}}, "obs": {"<echipa_id>": "..."}}
create or replace function public.proiect_evaluare(p_grupa text)
returns jsonb
language plpgsql security definer stable set search_path = public as $$
begin
  if not public.sunt_profesor() then
    return jsonb_build_object('ok', false, 'mesaj', 'Numai profesorul poate face asta.');
  end if;
  return jsonb_build_object(
    'ok', true,
    'criterii', coalesce((
      select jsonb_object_agg(x.matricol, x.c) from (
        select c.matricol, jsonb_object_agg(c.criteriu, c.puncte) as c
          from public.proiect_criterii c
          join public.studenti s on s.matricol = c.matricol
         where s.grupa_id = p_grupa
         group by c.matricol) x), '{}'::jsonb),
    'obs', coalesce((
      select jsonb_object_agg(o.echipa_id::text, o.text)
        from public.proiect_obs o
        join public.echipe e on e.id = o.echipa_id
       where e.grupa_id = p_grupa), '{}'::jsonb)
  );
end $$;


grant execute on function public.pune_criteriu(text[], text, numeric) to authenticated;
grant execute on function public.pune_obs_proiect(bigint, text) to authenticated;
grant execute on function public.proiect_evaluare(text) to authenticated;

-- Verificare: trebuie să apară cele trei funcții.
select proname from pg_proc
 where proname in ('pune_criteriu', 'pune_obs_proiect', 'proiect_evaluare')
 order by proname;
