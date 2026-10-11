-- ===========================================================================
-- 08. ORA CONDUSĂ DE PROFESOR
--
-- Un singur număr, ținut pe server: la ce slide e profesorul acum. Cât timp
-- ora e pornită, paginile studenților citesc numărul ăsta și se mută singure
-- acolo. Când ora se oprește, fiecare umblă din nou în ritmul lui.
--
-- Nu e supraveghere și nu blochează pe nimeni: studentul poate oricând să
-- iasă din ritm, iar pagina lui îi oferă butonul de întoarcere.
--
-- Se rulează o singură dată, după 07. Se poate rula din nou fără stricăciuni.
-- ===========================================================================

create table if not exists public.ritm (
  capitol        text primary key,          -- 'c1', 'c2', …
  slide_nr       int     not null default 1,
  total_nr       int,
  pornit         boolean not null default false,
  condus_de      uuid references auth.users(id) on delete set null,
  pornit_la      timestamptz,
  actualizat_la  timestamptz not null default now()
);

alter table public.ritm enable row level security;

-- Oricine e conectat poate citi: e doar un număr de slide, nu date personale.
drop policy if exists ritm_citire on public.ritm;
create policy ritm_citire on public.ritm
  for select to authenticated using (true);

-- Nimeni nu scrie direct în tabel. Scrisul trece prin pune_ritm(), care
-- verifică întâi că cel care cere chiar e profesor.

-- ------------------------------------------------------------ profesorul ---

create or replace function public.pune_ritm(
  p_capitol  text,
  p_slide_nr int     default null,
  p_total_nr int     default null,
  p_pornit   boolean default null
) returns jsonb
language plpgsql security definer set search_path = public as $$
declare r public.ritm;
begin
  if not public.sunt_profesor() then
    return jsonb_build_object('ok', false, 'mesaj', 'Numai profesorul poate conduce ora.');
  end if;
  if p_capitol is null or p_capitol = '' then
    return jsonb_build_object('ok', false, 'mesaj', 'Lipsește lecția.');
  end if;

  insert into public.ritm (capitol, slide_nr, total_nr, pornit, condus_de,
                           pornit_la, actualizat_la)
  values (p_capitol, coalesce(p_slide_nr, 1), p_total_nr,
          coalesce(p_pornit, true), auth.uid(),
          case when coalesce(p_pornit, true) then now() end, now())
  on conflict (capitol) do update set
    slide_nr      = coalesce(p_slide_nr, public.ritm.slide_nr),
    total_nr      = coalesce(p_total_nr, public.ritm.total_nr),
    pornit        = coalesce(p_pornit,   public.ritm.pornit),
    condus_de     = auth.uid(),
    -- pornit_la se reînnoiește doar la trecerea din oprit în pornit
    pornit_la     = case
                      when coalesce(p_pornit, public.ritm.pornit)
                           and not public.ritm.pornit then now()
                      when coalesce(p_pornit, public.ritm.pornit) then public.ritm.pornit_la
                      else null end,
    actualizat_la = now()
  returning * into r;

  return jsonb_build_object('ok', true, 'capitol', r.capitol,
                            'slide_nr', r.slide_nr, 'total_nr', r.total_nr,
                            'pornit', r.pornit, 'pornit_la', r.pornit_la);
end $$;

-- Oprirea e scrisă separat, ca să poată fi apăsată dintr-un singur buton.
create or replace function public.opreste_ritm(p_capitol text)
returns jsonb
language sql security definer set search_path = public as $$
  select public.pune_ritm(p_capitol, null, null, false);
$$;

-- ------------------------------------------------------------- studentul ---
-- Citirea merge și prin select direct, dar funcția întoarce exact ce-i trebuie
-- paginii, într-un singur rând, și spune și de cât timp n-a mai mișcat nimeni.

create or replace function public.citeste_ritm(p_capitol text)
returns jsonb
language sql security definer stable set search_path = public as $$
  select coalesce(
    (select jsonb_build_object(
       'pornit',   r.pornit,
       'slide_nr', r.slide_nr,
       'total_nr', r.total_nr,
       'vechime',  extract(epoch from (now() - r.actualizat_la))::int)
       from public.ritm r where r.capitol = p_capitol),
    jsonb_build_object('pornit', false));
$$;

-- --------------------------------------------------------------- curățare ---
-- O oră uitată pornită peste noapte nu trebuie să tragă pe nimeni a doua zi.
create or replace function public.curata_ritm()
returns int
language sql security definer set search_path = public as $$
  with s as (
    update public.ritm set pornit = false, pornit_la = null
     where pornit and actualizat_la < now() - interval '4 hours'
     returning 1)
  select count(*)::int from s;
$$;

grant execute on function public.pune_ritm(text, int, int, boolean) to authenticated;
grant execute on function public.opreste_ritm(text)                 to authenticated;
grant execute on function public.citeste_ritm(text)                 to authenticated;
