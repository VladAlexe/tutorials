-- ===========================================================================
-- 21. OBSERVAȚIILE TALE DESPRE STUDENȚI
--
-- Se rulează o dată, în Supabase (SQL Editor), după 20.
--
-- Un câmp de text pe student, doar pentru tine: ce ai observat la clasă,
-- ce trebuie urmărit, cu ce a avut probleme. Studentul nu îl vede.
-- ===========================================================================

create table if not exists public.observatii (
  matricol      text primary key references public.studenti(matricol) on delete cascade,
  text          text not null,
  actualizat_la timestamptz not null default now()
);
alter table public.observatii enable row level security;
revoke all on public.observatii from anon, authenticated;

create or replace function public.pune_observatie(p_matricol text, p_text text)
returns jsonb
language plpgsql security definer set search_path = public as $$
begin
  if not public.sunt_profesor() then
    return jsonb_build_object('ok', false, 'mesaj', 'Numai profesorul poate face asta.');
  end if;
  if coalesce(btrim(p_text), '') = '' then
    delete from public.observatii where matricol = p_matricol;
  else
    insert into public.observatii (matricol, text) values (p_matricol, left(p_text, 4000))
    on conflict (matricol) do update set text = excluded.text, actualizat_la = now();
  end if;
  return jsonb_build_object('ok', true);
end $$;

create or replace function public.observatii()
returns table (matricol text, text text, actualizat_la timestamptz)
language sql security definer stable set search_path = public as $$
  select o.matricol, o.text, o.actualizat_la from public.observatii o where public.sunt_profesor();
$$;

grant execute on function public.pune_observatie(text, text) to authenticated;
grant execute on function public.observatii() to authenticated;
