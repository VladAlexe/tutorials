-- ===========================================================================
-- 18. CATALOGUL
--
-- Se rulează o dată, în Supabase (SQL Editor), după 17.
--
-- Ce adaugă:
--   note_manuale   notele pe care le pui tu: tema 1, tema 2, tema 3, proiectul
--   pune_nota      scrie (sau șterge, cu null) o notă; doar profesorul
--   catalog        un rând pe student, cu tot ce intră în notă
--   note_mele      studentul își vede notele puse de tine
--
-- Activitatea la seminar NU se calculează aici: regula stă în js/curs.js
-- (NOTARE), ca studentul și profesorul să vadă exact aceeași cifră. Funcția
-- dă doar materia primă: ce sarcini a rezolvat fiecare, și dacă la oră sau
-- acasă.
-- ===========================================================================

create table if not exists public.note_manuale (
  matricol      text not null references public.studenti(matricol) on delete cascade,
  cheie         text not null check (cheie in ('tema1','tema2','tema3','proiect')),
  puncte        numeric(4,2) not null check (puncte >= 0),
  actualizat_la timestamptz not null default now(),
  primary key (matricol, cheie)
);
alter table public.note_manuale enable row level security;
-- nimeni nu citește tabelul direct: doar prin funcțiile de mai jos
revoke all on public.note_manuale from anon, authenticated;


create or replace function public.pune_nota(p_matricol text, p_cheie text, p_puncte numeric)
returns jsonb
language plpgsql security definer set search_path = public as $$
begin
  if not public.sunt_profesor() then
    return jsonb_build_object('ok', false, 'mesaj', 'Numai profesorul poate face asta.');
  end if;
  if p_puncte is null then
    delete from public.note_manuale where matricol = p_matricol and cheie = p_cheie;
  else
    insert into public.note_manuale (matricol, cheie, puncte)
    values (p_matricol, p_cheie, p_puncte)
    on conflict (matricol, cheie)
      do update set puncte = excluded.puncte, actualizat_la = now();
  end if;
  return jsonb_build_object('ok', true);
end $$;


-- Un rând pe student din listă (și pe invitații care au lucrat).
--   prezente  lecțiile la care a fost prezent, din orele nearhivate
--   sarcini   [[sarcina, la_ora], ...]: fiecare sarcină rezolvată corect,
--             o singură dată, cu la_ora = true dacă a rezolvat-o într-o oră
--   note      {"tema1": 0.8, "proiect": 4.5, ...}
create or replace function public.catalog()
returns table (matricol text, nume text, grupa text, are_cont boolean, invitat boolean,
               prezente text[], sarcini jsonb, note jsonb, ultima timestamptz)
language sql security definer stable set search_path = public as $$
  with eu as (select 1 where public.sunt_profesor()),
  pz as (
    select p.matricol, array_agg(distinct z.curs order by z.curs) as prezente
      from public.prezente z
      join public.profiluri p on p.user_id = z.user_id
      left join public.sedinte s on s.id = z.sedinta_id
     where s.id is null or s.arhivata_la is null
     group by p.matricol
  ),
  rez as (
    select p.matricol, i.sarcina_id,
           bool_or(i.sedinta_id is not null and coalesce(s.arhivata_la is null, true)) as la_ora,
           max(i.creat_la) as cand
      from public.incercari i
      join public.profiluri p on p.user_id = i.user_id
      left join public.sedinte s on s.id = i.sedinta_id
     where i.corect
     group by p.matricol, i.sarcina_id
  ),
  sar as (
    select matricol, jsonb_agg(jsonb_build_array(sarcina_id, la_ora)) as sarcini,
           max(cand) as ultima
      from rez group by matricol
  ),
  nt as (
    select matricol, jsonb_object_agg(cheie, puncte) as note
      from public.note_manuale group by matricol
  )
  select s.matricol, s.nume, s.grupa,
         exists (select 1 from public.profiluri p where p.matricol = s.matricol),
         coalesce(s.invitat, false),
         coalesce(pz.prezente, '{}'),
         coalesce(sar.sarcini, '[]'::jsonb),
         coalesce(nt.note, '{}'::jsonb),
         sar.ultima
    from eu, public.studenti s
    left join pz  on pz.matricol  = s.matricol
    left join sar on sar.matricol = s.matricol
    left join nt  on nt.matricol  = s.matricol
   where coalesce(s.invitat, false) = false
      or sar.matricol is not null
   order by coalesce(s.invitat, false), s.nume;
$$;


create or replace function public.note_mele()
returns jsonb
language sql security definer stable set search_path = public as $$
  select coalesce(jsonb_object_agg(n.cheie, n.puncte), '{}'::jsonb)
    from public.note_manuale n
    join public.profiluri p on p.matricol = n.matricol
   where p.user_id = auth.uid();
$$;

grant execute on function public.pune_nota(text, text, numeric) to authenticated;
grant execute on function public.catalog()  to authenticated;
grant execute on function public.note_mele() to authenticated;
