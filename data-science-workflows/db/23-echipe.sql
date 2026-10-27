-- ===========================================================================
-- 23. ECHIPELE DE PROIECT
--
-- Se rulează o dată, în Supabase (SQL Editor), după 22. E sigur de rulat din
-- nou: nu șterge nimic din ce există.
--
-- Cum funcționează:
--   1. La cursul 2 pornești alegerea pentru grupa activă (numărul de echipe
--      și limita, implicit 5 membri). Alegerea e DESCHISĂ: fiecare student
--      intră singur într-o echipă cu locuri libere și se poate muta.
--   2. O ÎNCHIZI când vrei. De atunci nimeni nu se mai mută singur.
--   3. Cine vine mai târziu (chiar și după cinci cursuri) CERE să intre
--      într-o echipă cu locuri libere; oricare membru al echipei, sau tu,
--      acceptă ori refuză.
--   4. Dacă toate echipele sunt pline, cel fără echipă deschide o echipă nouă,
--      iar următorii pot cere să intre în ea.
--
-- Ce vede fiecare (GDPR):
--   - fiecare student al grupei vede toate echipele grupei, cu numele
--     membrilor (doar numele, fără matricol și fără cont GitHub);
--   - membrii unei echipe văd numele celui care cere să intre la ei;
--   - profesorul vede tot: membrii, conturile GitHub, cererile, cine nu are
--     echipă.
-- Tabelele nu se citesc direct din browser (RLS fără politici); totul trece
-- prin funcțiile de mai jos, care întorc doar ce are voie fiecare să vadă.
-- ===========================================================================


-- 1. Tabelele -----------------------------------------------------------------

create table if not exists public.echipe_alegere (
  grupa_id       text primary key references public.grupe(id) on delete cascade,
  stare          text not null default 'deschisa' check (stare in ('deschisa', 'inchisa')),
  limita         int  not null default 5 check (limita between 2 and 10),
  actualizat_la  timestamptz not null default now()
);

create table if not exists public.echipe (
  id        bigint generated always as identity primary key,
  grupa_id  text not null references public.grupe(id) on delete cascade,
  nr        int  not null,
  creat_la  timestamptz not null default now(),
  unique (grupa_id, nr)
);

-- un student, cel mult o echipă: cheia primară e matricolul
create table if not exists public.echipe_membri (
  matricol   text primary key references public.studenti(matricol) on delete cascade,
  echipa_id  bigint not null references public.echipe(id) on delete cascade,
  intrat_la  timestamptz not null default now(),
  prin       text not null default 'alegere'
             check (prin in ('alegere', 'cerere', 'profesor', 'echipa_noua'))
);
create index if not exists echipe_membri_echipa_idx on public.echipe_membri (echipa_id);

create table if not exists public.echipe_cereri (
  id          bigint generated always as identity primary key,
  matricol    text not null references public.studenti(matricol) on delete cascade,
  echipa_id   bigint not null references public.echipe(id) on delete cascade,
  stare       text not null default 'in_asteptare'
              check (stare in ('in_asteptare', 'acceptata', 'refuzata', 'anulata')),
  creat_la    timestamptz not null default now(),
  raspuns_la  timestamptz,
  raspuns_de  text             -- matricolul membrului care a răspuns, sau 'profesor'
);
-- o singură cerere în așteptare pe student
create unique index if not exists echipe_cereri_una_idx
  on public.echipe_cereri (matricol) where stare = 'in_asteptare';

alter table public.echipe_alegere enable row level security;
alter table public.echipe         enable row level security;
alter table public.echipe_membri  enable row level security;
alter table public.echipe_cereri  enable row level security;
revoke all on public.echipe_alegere, public.echipe, public.echipe_membri, public.echipe_cereri
  from anon, authenticated;


-- 2. Cine sunt eu, ca student ----------------------------------------------------
--    Doar conturile legate de un nume din listă, fără invitați.

create or replace function public.ech_eu()
returns table (matricol text, grupa_id text, nume text)
language sql security definer stable set search_path = public as $$
  select s.matricol, s.grupa_id, s.nume
    from public.profiluri p
    join public.studenti s on s.matricol = p.matricol
   where p.user_id = auth.uid()
     and coalesce(s.invitat, false) = false
   limit 1;
$$;

create or replace function public.ech_ocupate(p_echipa bigint)
returns int
language sql security definer stable set search_path = public as $$
  select count(*)::int from public.echipe_membri where echipa_id = p_echipa;
$$;


-- 3. Ce vede studentul -----------------------------------------------------------

create or replace function public.echipele_mele()
returns jsonb
language plpgsql security definer stable set search_path = public as $$
declare
  v_eu      record;
  v_cfg     record;
  v_echipa  bigint;
  v_rez     jsonb;
begin
  if auth.uid() is null then
    return jsonb_build_object('ok', false, 'motiv', 'fara_cont');
  end if;
  select * into v_eu from public.ech_eu();
  if v_eu.matricol is null then
    return jsonb_build_object('ok', false, 'motiv', 'fara_nume');
  end if;
  if v_eu.grupa_id is null then
    return jsonb_build_object('ok', false, 'motiv', 'fara_grupa');
  end if;

  select * into v_cfg from public.echipe_alegere where grupa_id = v_eu.grupa_id;
  if v_cfg.grupa_id is null then
    return jsonb_build_object('ok', true, 'stare', 'nepornita', 'nume', v_eu.nume);
  end if;

  select echipa_id into v_echipa from public.echipe_membri where matricol = v_eu.matricol;

  select jsonb_build_object(
    'ok', true,
    'stare', v_cfg.stare,
    'limita', v_cfg.limita,
    'nume', v_eu.nume,

    -- echipa mea, cu numele colegilor
    'echipa', (
      select jsonb_build_object(
        'id', e.id, 'nr', e.nr,
        'membri', coalesce((
          select jsonb_agg(jsonb_build_object('nume', s.nume, 'eu', s.matricol = v_eu.matricol)
                           order by m.intrat_la)
            from public.echipe_membri m
            join public.studenti s on s.matricol = m.matricol
           where m.echipa_id = e.id), '[]'::jsonb))
        from public.echipe e where e.id = v_echipa),

    -- toate echipele grupei, cu numele membrilor: echipele sunt publice în
    -- interiorul grupei, ca fiecare să știe cine lucrează cu cine.
    'echipe', coalesce((
      select jsonb_agg(jsonb_build_object(
               'id', e.id, 'nr', e.nr,
               'ocupate', public.ech_ocupate(e.id),
               'plina', public.ech_ocupate(e.id) >= v_cfg.limita,
               'a_mea', e.id is not distinct from v_echipa,
               'membri', coalesce((
                   select jsonb_agg(s.nume order by m.intrat_la)
                     from public.echipe_membri m join public.studenti s on s.matricol = m.matricol
                    where m.echipa_id = e.id), '[]'::jsonb))
             order by e.nr)
        from public.echipe e where e.grupa_id = v_eu.grupa_id), '[]'::jsonb),

    'toate_pline', not exists (
      select 1 from public.echipe e
       where e.grupa_id = v_eu.grupa_id and public.ech_ocupate(e.id) < v_cfg.limita),

    -- cererea mea, dacă aștept răspuns
    'cerere', (
      select jsonb_build_object('id', c.id, 'nr', e.nr, 'creat_la', c.creat_la)
        from public.echipe_cereri c join public.echipe e on e.id = c.echipa_id
       where c.matricol = v_eu.matricol and c.stare = 'in_asteptare'),

    -- ultima cerere refuzată, ca studentul să știe de ce nu a intrat
    'refuzata', (
      select jsonb_build_object('nr', e.nr, 'la', c.raspuns_la)
        from public.echipe_cereri c join public.echipe e on e.id = c.echipa_id
       where c.matricol = v_eu.matricol and c.stare = 'refuzata' and v_echipa is null
         and not exists (select 1 from public.echipe_cereri c2
                          where c2.matricol = v_eu.matricol and c2.creat_la > c.creat_la)
       order by c.raspuns_la desc limit 1),

    -- cererile primite de echipa mea
    'cereri_primite', coalesce((
      select jsonb_agg(jsonb_build_object('id', c.id, 'nume', s.nume, 'creat_la', c.creat_la)
                       order by c.creat_la)
        from public.echipe_cereri c join public.studenti s on s.matricol = c.matricol
       where c.echipa_id = v_echipa and c.stare = 'in_asteptare'), '[]'::jsonb)
  ) into v_rez;

  return v_rez;
end $$;


-- 4. Ce face studentul -----------------------------------------------------------

-- alegerea liberă, cât timp e deschisă
create or replace function public.alege_echipa(p_echipa bigint)
returns jsonb
language plpgsql security definer set search_path = public as $$
declare v_eu record; v_cfg record; v_e record;
begin
  select * into v_eu from public.ech_eu();
  if v_eu.matricol is null then return jsonb_build_object('ok', false, 'mesaj', 'Contul nu este legat de un nume din lista grupei.'); end if;
  select * into v_cfg from public.echipe_alegere where grupa_id = v_eu.grupa_id;
  if v_cfg.grupa_id is null then return jsonb_build_object('ok', false, 'mesaj', 'Alegerea echipelor nu a început.'); end if;
  if v_cfg.stare <> 'deschisa' then return jsonb_build_object('ok', false, 'mesaj', 'Alegerea este închisă: trimite o cerere echipei.'); end if;

  select * into v_e from public.echipe where id = p_echipa and grupa_id = v_eu.grupa_id for update;
  if v_e.id is null then return jsonb_build_object('ok', false, 'mesaj', 'Echipa nu există.'); end if;

  if (select count(*) from public.echipe_membri where echipa_id = v_e.id and matricol <> v_eu.matricol) >= v_cfg.limita then
    return jsonb_build_object('ok', false, 'mesaj', 'Echipa este completă.');
  end if;

  insert into public.echipe_membri (matricol, echipa_id, prin)
  values (v_eu.matricol, v_e.id, 'alegere')
  on conflict (matricol) do update set echipa_id = excluded.echipa_id, intrat_la = now(), prin = 'alegere';

  update public.echipe_cereri set stare = 'anulata', raspuns_la = now()
   where matricol = v_eu.matricol and stare = 'in_asteptare';
  return jsonb_build_object('ok', true);
end $$;

-- ieșirea din echipă, cât timp alegerea e deschisă
create or replace function public.paraseste_echipa()
returns jsonb
language plpgsql security definer set search_path = public as $$
declare v_eu record; v_cfg record;
begin
  select * into v_eu from public.ech_eu();
  if v_eu.matricol is null then return jsonb_build_object('ok', false, 'mesaj', 'Contul nu este legat de un nume din lista grupei.'); end if;
  select * into v_cfg from public.echipe_alegere where grupa_id = v_eu.grupa_id;
  if v_cfg.stare is distinct from 'deschisa' then
    return jsonb_build_object('ok', false, 'mesaj', 'Echipele sunt închise; pentru o schimbare, scrie profesorului.');
  end if;
  delete from public.echipe_membri where matricol = v_eu.matricol;
  return jsonb_build_object('ok', true);
end $$;

-- cererea de intrare, după închidere
create or replace function public.cere_echipa(p_echipa bigint)
returns jsonb
language plpgsql security definer set search_path = public as $$
declare v_eu record; v_cfg record; v_e record;
begin
  select * into v_eu from public.ech_eu();
  if v_eu.matricol is null then return jsonb_build_object('ok', false, 'mesaj', 'Contul nu este legat de un nume din lista grupei.'); end if;
  select * into v_cfg from public.echipe_alegere where grupa_id = v_eu.grupa_id;
  if v_cfg.grupa_id is null then return jsonb_build_object('ok', false, 'mesaj', 'Alegerea echipelor nu a început.'); end if;
  if v_cfg.stare = 'deschisa' then return public.alege_echipa(p_echipa); end if;
  if exists (select 1 from public.echipe_membri where matricol = v_eu.matricol) then
    return jsonb_build_object('ok', false, 'mesaj', 'Faci deja parte dintr-o echipă.');
  end if;
  select * into v_e from public.echipe where id = p_echipa and grupa_id = v_eu.grupa_id;
  if v_e.id is null then return jsonb_build_object('ok', false, 'mesaj', 'Echipa nu există.'); end if;
  if public.ech_ocupate(v_e.id) >= v_cfg.limita then
    return jsonb_build_object('ok', false, 'mesaj', 'Echipa este completă.');
  end if;

  update public.echipe_cereri set stare = 'anulata', raspuns_la = now()
   where matricol = v_eu.matricol and stare = 'in_asteptare';
  insert into public.echipe_cereri (matricol, echipa_id) values (v_eu.matricol, v_e.id);
  return jsonb_build_object('ok', true);
end $$;

create or replace function public.anuleaza_cererea()
returns jsonb
language plpgsql security definer set search_path = public as $$
declare v_eu record;
begin
  select * into v_eu from public.ech_eu();
  if v_eu.matricol is null then return jsonb_build_object('ok', false); end if;
  update public.echipe_cereri set stare = 'anulata', raspuns_la = now()
   where matricol = v_eu.matricol and stare = 'in_asteptare';
  return jsonb_build_object('ok', true);
end $$;

-- răspunsul unui membru al echipei (sau al profesorului) la o cerere
create or replace function public.raspunde_cererii(p_cerere bigint, p_accept boolean)
returns jsonb
language plpgsql security definer set search_path = public as $$
declare v_eu record; v_c record; v_cfg record; v_prof boolean := public.sunt_profesor(); v_de text;
begin
  select * into v_c from public.echipe_cereri where id = p_cerere and stare = 'in_asteptare' for update;
  if v_c.id is null then return jsonb_build_object('ok', false, 'mesaj', 'Cererea nu mai este în așteptare.'); end if;

  if v_prof then
    v_de := 'profesor';
  else
    select * into v_eu from public.ech_eu();
    if v_eu.matricol is null or not exists (
         select 1 from public.echipe_membri where matricol = v_eu.matricol and echipa_id = v_c.echipa_id) then
      return jsonb_build_object('ok', false, 'mesaj', 'Numai membrii echipei pot răspunde.');
    end if;
    v_de := v_eu.matricol;
  end if;

  if not p_accept then
    update public.echipe_cereri set stare = 'refuzata', raspuns_la = now(), raspuns_de = v_de where id = v_c.id;
    return jsonb_build_object('ok', true);
  end if;

  perform 1 from public.echipe where id = v_c.echipa_id for update;
  select a.* into v_cfg from public.echipe_alegere a join public.echipe e on e.grupa_id = a.grupa_id where e.id = v_c.echipa_id;
  if public.ech_ocupate(v_c.echipa_id) >= coalesce(v_cfg.limita, 5) and not v_prof then
    return jsonb_build_object('ok', false, 'mesaj', 'Echipa este deja completă.');
  end if;
  if exists (select 1 from public.echipe_membri where matricol = v_c.matricol) then
    update public.echipe_cereri set stare = 'anulata', raspuns_la = now(), raspuns_de = v_de where id = v_c.id;
    return jsonb_build_object('ok', false, 'mesaj', 'Studentul a intrat între timp în altă echipă.');
  end if;

  insert into public.echipe_membri (matricol, echipa_id, prin) values (v_c.matricol, v_c.echipa_id, 'cerere');
  update public.echipe_cereri set stare = 'acceptata', raspuns_la = now(), raspuns_de = v_de where id = v_c.id;
  return jsonb_build_object('ok', true);
end $$;

-- echipă nouă: doar când toate echipele grupei sunt complete
create or replace function public.echipa_noua()
returns jsonb
language plpgsql security definer set search_path = public as $$
declare v_eu record; v_cfg record; v_id bigint;
begin
  select * into v_eu from public.ech_eu();
  if v_eu.matricol is null then return jsonb_build_object('ok', false, 'mesaj', 'Contul nu este legat de un nume din lista grupei.'); end if;
  select * into v_cfg from public.echipe_alegere where grupa_id = v_eu.grupa_id for update;
  if v_cfg.grupa_id is null then return jsonb_build_object('ok', false, 'mesaj', 'Alegerea echipelor nu a început.'); end if;
  if exists (select 1 from public.echipe_membri where matricol = v_eu.matricol) then
    return jsonb_build_object('ok', false, 'mesaj', 'Faci deja parte dintr-o echipă.');
  end if;
  if exists (select 1 from public.echipe e where e.grupa_id = v_eu.grupa_id
                and public.ech_ocupate(e.id) < v_cfg.limita) then
    return jsonb_build_object('ok', false, 'mesaj', 'Există încă echipe cu locuri libere.');
  end if;

  insert into public.echipe (grupa_id, nr)
  values (v_eu.grupa_id, coalesce((select max(nr) from public.echipe where grupa_id = v_eu.grupa_id), 0) + 1)
  returning id into v_id;
  insert into public.echipe_membri (matricol, echipa_id, prin) values (v_eu.matricol, v_id, 'echipa_noua');
  update public.echipe_cereri set stare = 'anulata', raspuns_la = now()
   where matricol = v_eu.matricol and stare = 'in_asteptare';
  return jsonb_build_object('ok', true);
end $$;

-- pentru antet: are nevoie studentul să facă ceva?
create or replace function public.am_echipa()
returns jsonb
language sql security definer stable set search_path = public as $$
  with eu as (select * from public.ech_eu()),
       cfg as (select a.* from public.echipe_alegere a join eu on a.grupa_id = eu.grupa_id),
       m as (select m.* from public.echipe_membri m join eu on m.matricol = eu.matricol)
  select case when not exists (select 1 from cfg) then jsonb_build_object('stare', 'nepornita')
    else jsonb_build_object(
      'stare', (select stare from cfg),
      'are', exists (select 1 from m),
      'cereri_primite', (select count(*) from public.echipe_cereri c
                          where c.stare = 'in_asteptare' and c.echipa_id = (select echipa_id from m)))
  end;
$$;


-- 5. Ce face profesorul ----------------------------------------------------------

-- pornește alegerea pentru o grupă: creează echipele lipsă, o deschide
create or replace function public.echipe_porneste(p_grupa text, p_numar int, p_limita int default 5)
returns jsonb
language plpgsql security definer set search_path = public as $$
declare i int;
begin
  if not public.sunt_profesor() then return jsonb_build_object('ok', false, 'mesaj', 'Numai profesorul poate face asta.'); end if;
  if p_numar is null or p_numar < 1 or p_numar > 40 then return jsonb_build_object('ok', false, 'mesaj', 'Număr de echipe nevalid.'); end if;
  insert into public.echipe_alegere (grupa_id, stare, limita) values (p_grupa, 'deschisa', p_limita)
  on conflict (grupa_id) do update set stare = 'deschisa', limita = excluded.limita, actualizat_la = now();
  for i in 1 .. p_numar loop
    insert into public.echipe (grupa_id, nr) values (p_grupa, i) on conflict (grupa_id, nr) do nothing;
  end loop;
  return jsonb_build_object('ok', true);
end $$;

create or replace function public.echipe_stare(p_grupa text, p_stare text)
returns jsonb
language plpgsql security definer set search_path = public as $$
begin
  if not public.sunt_profesor() then return jsonb_build_object('ok', false, 'mesaj', 'Numai profesorul poate face asta.'); end if;
  if p_stare not in ('deschisa', 'inchisa') then return jsonb_build_object('ok', false); end if;
  update public.echipe_alegere set stare = p_stare, actualizat_la = now() where grupa_id = p_grupa;
  return jsonb_build_object('ok', found);
end $$;

create or replace function public.echipe_adauga(p_grupa text)
returns jsonb
language plpgsql security definer set search_path = public as $$
begin
  if not public.sunt_profesor() then return jsonb_build_object('ok', false, 'mesaj', 'Numai profesorul poate face asta.'); end if;
  insert into public.echipe (grupa_id, nr)
  values (p_grupa, coalesce((select max(nr) from public.echipe where grupa_id = p_grupa), 0) + 1);
  return jsonb_build_object('ok', true);
end $$;

-- mută sau scoate un student (p_echipa null = fără echipă); limita nu se aplică
create or replace function public.echipe_pune(p_matricol text, p_echipa bigint)
returns jsonb
language plpgsql security definer set search_path = public as $$
begin
  if not public.sunt_profesor() then return jsonb_build_object('ok', false, 'mesaj', 'Numai profesorul poate face asta.'); end if;
  if p_echipa is null then
    delete from public.echipe_membri where matricol = p_matricol;
  else
    insert into public.echipe_membri (matricol, echipa_id, prin) values (p_matricol, p_echipa, 'profesor')
    on conflict (matricol) do update set echipa_id = excluded.echipa_id, intrat_la = now(), prin = 'profesor';
    update public.echipe_cereri set stare = 'anulata', raspuns_la = now(), raspuns_de = 'profesor'
     where matricol = p_matricol and stare = 'in_asteptare';
  end if;
  return jsonb_build_object('ok', true);
end $$;

-- tot ce vede profesorul despre o grupă
create or replace function public.echipe_toate(p_grupa text)
returns jsonb
language plpgsql security definer stable set search_path = public as $$
declare v_cfg record;
begin
  if not public.sunt_profesor() then return jsonb_build_object('ok', false, 'mesaj', 'Numai profesorul poate face asta.'); end if;
  select * into v_cfg from public.echipe_alegere where grupa_id = p_grupa;
  return jsonb_build_object(
    'ok', true,
    'stare', coalesce(v_cfg.stare, 'nepornita'),
    'limita', coalesce(v_cfg.limita, 5),
    'studenti', (select count(*) from public.studenti where grupa_id = p_grupa and coalesce(invitat, false) = false),
    'echipe', coalesce((
      select jsonb_agg(jsonb_build_object(
               'id', e.id, 'nr', e.nr,
               'membri', coalesce((
                 select jsonb_agg(jsonb_build_object(
                          'matricol', s.matricol, 'nume', s.nume, 'github', p.github_login,
                          'prin', m.prin, 'intrat_la', m.intrat_la) order by m.intrat_la)
                   from public.echipe_membri m
                   join public.studenti s on s.matricol = m.matricol
                   left join public.profiluri p on p.matricol = m.matricol
                  where m.echipa_id = e.id), '[]'::jsonb))
             order by e.nr)
        from public.echipe e where e.grupa_id = p_grupa), '[]'::jsonb),
    'fara_echipa', coalesce((
      select jsonb_agg(jsonb_build_object('matricol', s.matricol, 'nume', s.nume,
                                          'cont', p.user_id is not null) order by s.nume)
        from public.studenti s
        left join public.profiluri p on p.matricol = s.matricol
       where s.grupa_id = p_grupa and coalesce(s.invitat, false) = false
         and not exists (select 1 from public.echipe_membri m where m.matricol = s.matricol)), '[]'::jsonb),
    'cereri', coalesce((
      select jsonb_agg(jsonb_build_object('id', c.id, 'nume', s.nume, 'nr', e.nr, 'creat_la', c.creat_la)
                       order by c.creat_la)
        from public.echipe_cereri c
        join public.echipe e on e.id = c.echipa_id
        join public.studenti s on s.matricol = c.matricol
       where e.grupa_id = p_grupa and c.stare = 'in_asteptare'), '[]'::jsonb)
  );
end $$;


-- 6. Drepturi ----------------------------------------------------------------------

revoke all on function public.ech_eu() from anon, public;
revoke all on function public.ech_ocupate(bigint) from anon, public;
grant execute on function public.echipele_mele()                     to authenticated;
grant execute on function public.alege_echipa(bigint)                to authenticated;
grant execute on function public.paraseste_echipa()                  to authenticated;
grant execute on function public.cere_echipa(bigint)                 to authenticated;
grant execute on function public.anuleaza_cererea()                  to authenticated;
grant execute on function public.raspunde_cererii(bigint, boolean)   to authenticated;
grant execute on function public.echipa_noua()                       to authenticated;
grant execute on function public.am_echipa()                         to authenticated;
grant execute on function public.echipe_porneste(text, int, int)     to authenticated;
grant execute on function public.echipe_stare(text, text)            to authenticated;
grant execute on function public.echipe_adauga(text)                 to authenticated;
grant execute on function public.echipe_pune(text, bigint)           to authenticated;
grant execute on function public.echipe_toate(text)                  to authenticated;


-- 7. Verificare: patru tabele noi, toate goale la început -----------------------
select 'echipe_alegere' as tabel, count(*) from public.echipe_alegere
union all select 'echipe', count(*) from public.echipe
union all select 'echipe_membri', count(*) from public.echipe_membri
union all select 'echipe_cereri', count(*) from public.echipe_cereri;
