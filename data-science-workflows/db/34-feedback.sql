-- ===========================================================================
-- 34. Feedback-ul pentru curs (lecția 8, sarcina c8-feedback)
--
-- Se rulează în Supabase (SQL Editor), o singură dată. E sigur de rulat din
-- nou: nu șterge nimic.
--
-- Răspunsurile sunt anonime. Se țin în două tabele care nu se pot lega:
--   feedback_trimis  cine a completat (pentru punctaj și ca să nu trimită de
--                    două ori), fără conținut;
--   feedback_curs    ce a răspuns, fără cont, cu cheie aleatoare (uuid, nu un
--                    număr crescător) și doar cu ziua, fără oră.
-- Punctajul vine, ca la celelalte sarcini, din rulari_cod (c8-feedback), unde
-- ajunge doar cuvântul „trimis”.
--
-- Ordinea: A (tabelele și funcția), apoi B (verificarea).
-- C are interogările pentru rezultate, de rulat după oră.
-- ===========================================================================

-- A. Tabelele și funcția prin care se trimite
create table if not exists public.feedback_trimis (
  user_id  uuid not null references auth.users(id) on delete cascade,
  capitol  text not null,
  primary key (user_id, capitol)
);

create table if not exists public.feedback_curs (
  id          uuid primary key default gen_random_uuid(),
  capitol     text not null,
  ziua        date not null default current_date,
  raspunsuri  jsonb not null
);

-- Fără politici: din browser nu se citește și nu se scrie direct nimic.
-- Singura cale de scriere este funcția de mai jos; citirea, din SQL Editor.
alter table public.feedback_trimis enable row level security;
alter table public.feedback_curs   enable row level security;

create or replace function public.feedback_trimite(p_capitol text, p_raspunsuri jsonb)
returns jsonb
language plpgsql security definer set search_path = public as $$
begin
  if auth.uid() is null then
    return jsonb_build_object('ok', false, 'mesaj', 'Feedback-ul se trimite din cont.');
  end if;
  if not exists (select 1 from public.profiluri where user_id = auth.uid()) then
    return jsonb_build_object('ok', false, 'mesaj', 'Contul nu are încă un nume din listă.');
  end if;
  if length(p_raspunsuri::text) > 6000 then
    return jsonb_build_object('ok', false, 'mesaj', 'Răspunsul este prea lung.');
  end if;
  if exists (select 1 from public.feedback_trimis where user_id = auth.uid() and capitol = p_capitol) then
    return jsonb_build_object('ok', true, 'deja', true);
  end if;

  insert into public.feedback_trimis (user_id, capitol) values (auth.uid(), p_capitol);
  insert into public.feedback_curs (capitol, raspunsuri) values (p_capitol, p_raspunsuri);
  return jsonb_build_object('ok', true, 'deja', false);
end $$;

revoke all on function public.feedback_trimite(text, jsonb) from public, anon;
grant execute on function public.feedback_trimite(text, jsonb) to authenticated;


-- B. Verificarea: două tabele, o funcție, RLS pornit
select c.relname as tabelul, c.relrowsecurity as rls
  from pg_class c join pg_namespace n on n.oid = c.relnamespace
 where n.nspname = 'public' and c.relname in ('feedback_trimis', 'feedback_curs');
select proname from pg_proc where proname = 'feedback_trimite';


-- C. Rezultatele (după oră)

-- C1. Câți au completat
select count(*) as au_completat from public.feedback_trimis where capitol = 'c8';

-- C2. Scala: media și distribuția pe fiecare afirmație (1 = deloc, 5 = întru totul)
select k.cheie as afirmatia,
       round(avg((f.raspunsuri->>k.cheie)::int), 2) as media,
       count(*) filter (where (f.raspunsuri->>k.cheie)::int <= 2) as dezacord_1_2,
       count(*) filter (where (f.raspunsuri->>k.cheie)::int = 3)  as neutru_3,
       count(*) filter (where (f.raspunsuri->>k.cheie)::int >= 4) as acord_4_5
  from public.feedback_curs f
 cross join lateral jsonb_object_keys(f.raspunsuri) as k(cheie)
 where f.capitol = 'c8' and k.cheie ~ '^[abc][0-9]_'
 group by k.cheie
 order by k.cheie;

-- C3. Ritmul și lecția care ar fi avut nevoie de mai mult timp
select raspunsuri->>'ritm' as ritmul, count(*) from public.feedback_curs
 where capitol = 'c8' group by 1 order by 2 desc;
select raspunsuri->>'lectia' as lectia, count(*) from public.feedback_curs
 where capitol = 'c8' group by 1 order by 2 desc;

-- C4. Răspunsurile deschise
select raspunsuri->>'in_plus' as ce_ar_fi_trebuit_in_plus,
       raspunsuri->>'greu'    as cel_mai_greu
  from public.feedback_curs
 where capitol = 'c8'
 order by random();
