-- ===========================================================================
-- 05. SESIUNI, JURNAL DE EVENIMENTE ȘI RESETARE
--
-- Se rulează o singură dată, în SQL Editor, după 01, 02 și 03.
-- Se poate rula din nou fără stricăciuni: totul e „if not exists" sau
-- „create or replace".
--
-- Ce adaugă:
--   sesiuni      cine e acum în lecție și pe ce slide  (se rescrie mereu)
--   evenimente   jurnalul complet, nu se șterge        (supraviețuiește oricărui restart)
--
-- Principiul e același ca până acum: studentul nu citește niciodată direct
-- tabelele celorlalți. Tot ce vede profesorul trece prin funcții cu
-- „security definer", care verifică întâi că e profesor.
-- ===========================================================================

-- ---------------------------------------------------------------- tabele ---

create table if not exists public.sesiuni (
  id         uuid primary key default gen_random_uuid(),
  user_id    uuid not null references auth.users(id) on delete cascade,
  capitol    text,
  slide      text,
  slide_nr   int,
  total_nr   int,
  inceput    timestamptz not null default now(),
  vazut_la   timestamptz not null default now()
);
alter table public.sesiuni enable row level security;

create index if not exists sesiuni_vazut_idx  on public.sesiuni (vazut_la desc);
create index if not exists sesiuni_user_idx   on public.sesiuni (user_id);

-- Jurnalul. Aici nu se șterge nimic la resetarea progresului: resetarea
-- repune studentul la început, dar urma a ceea ce s-a întâmplat rămâne.
create table if not exists public.evenimente (
  id        bigint generated always as identity primary key,
  user_id   uuid not null references auth.users(id) on delete cascade,
  sesiune   uuid,
  tip       text not null,     -- intrare | slide | raspuns | cod | reset | iesire
  capitol   text,
  slide     text,
  slide_nr  int,
  detalii   jsonb,
  creat_la  timestamptz not null default now()
);
alter table public.evenimente enable row level security;

create index if not exists evenimente_creat_idx   on public.evenimente (creat_la desc);
create index if not exists evenimente_capitol_idx on public.evenimente (capitol, creat_la desc);
create index if not exists evenimente_user_idx    on public.evenimente (user_id, creat_la desc);

-- --------------------------------------------------------------- politici --

drop policy if exists "sesiuni: vezi ale tale" on public.sesiuni;
create policy "sesiuni: vezi ale tale" on public.sesiuni
  for select using (user_id = auth.uid() or public.sunt_profesor());

drop policy if exists "sesiuni: scrii ale tale" on public.sesiuni;
create policy "sesiuni: scrii ale tale" on public.sesiuni
  for insert with check (user_id = auth.uid());

drop policy if exists "sesiuni: actualizezi ale tale" on public.sesiuni;
create policy "sesiuni: actualizezi ale tale" on public.sesiuni
  for update using (user_id = auth.uid()) with check (user_id = auth.uid());

drop policy if exists "evenimente: vezi ale tale" on public.evenimente;
create policy "evenimente: vezi ale tale" on public.evenimente
  for select using (user_id = auth.uid() or public.sunt_profesor());

drop policy if exists "evenimente: scrii ale tale" on public.evenimente;
create policy "evenimente: scrii ale tale" on public.evenimente
  for insert with check (user_id = auth.uid());

-- Fără politică de delete: jurnalul nu se șterge din browser, de nimeni.

-- ------------------------------------------------------- bătaia de inimă ---
-- Pagina lecției o cheamă la intrare și apoi din 20 în 20 de secunde.
-- Întoarce id-ul sesiunii, pe care pagina îl ține până la reîncărcare.

create or replace function public.bate(
  p_sesiune  uuid default null,
  p_capitol  text default null,
  p_slide    text default null,
  p_slide_nr int  default null,
  p_total_nr int  default null
) returns uuid
language plpgsql security definer set search_path = public as $$
declare v_id uuid;
begin
  if auth.uid() is null then return null; end if;

  if p_sesiune is not null then
    update public.sesiuni
       set capitol = coalesce(p_capitol, capitol),
           slide = coalesce(p_slide, slide),
           slide_nr = coalesce(p_slide_nr, slide_nr),
           total_nr = coalesce(p_total_nr, total_nr),
           vazut_la = now()
     where id = p_sesiune and user_id = auth.uid()
     returning id into v_id;
    if v_id is not null then return v_id; end if;
  end if;

  insert into public.sesiuni (user_id, capitol, slide, slide_nr, total_nr)
  values (auth.uid(), p_capitol, p_slide, p_slide_nr, p_total_nr)
  returning id into v_id;
  return v_id;
end $$;

-- ------------------------------------------------------- vederea live -----
-- Cine e în lecție chiar acum. Numai profesorul.

create or replace function public.live_acum(p_minute int default 3)
returns table (
  matricol text, nume text, grupa text,
  capitol text, slide_nr int, total_nr int,
  de_cat_timp int, intrat_de int
)
language sql security definer stable set search_path = public as $$
  select coalesce(p.matricol, '—')            as matricol,
         coalesce(st.nume, u.email, 'fără cont legat') as nume,
         st.grupa,
         s.capitol, s.slide_nr, s.total_nr,
         extract(epoch from (now() - s.vazut_la))::int as de_cat_timp,
         extract(epoch from (now() - s.inceput))::int  as intrat_de
    from public.sesiuni s
    join auth.users u            on u.id = s.user_id
    left join public.profiluri p on p.user_id = s.user_id
    left join public.studenti st on st.matricol = p.matricol
   where public.sunt_profesor()
     and s.vazut_la > now() - make_interval(mins => greatest(p_minute, 1))
   order by s.slide_nr desc nulls last, st.nume;
$$;

-- -------------------------------------------- distribuția răspunsurilor ---
-- Pentru fiecare întrebare, câți au ales fiecare variantă. Exact ce îți
-- trebuie ca să vezi la clasă unde s-a împiedicat grupa.

create or replace function public.sumar_raspunsuri(p_capitol text default null)
returns table (intrebare_id text, raspuns int, cati int, corect boolean)
language sql security definer stable set search_path = public as $$
  select r.intrebare_id, r.raspuns, count(*)::int, bool_or(r.corect)
    from public.raspunsuri r
   where public.sunt_profesor()
     and (p_capitol is null or r.capitol = p_capitol)
   group by r.intrebare_id, r.raspuns
   order by r.intrebare_id, r.raspuns;
$$;

-- ------------------------------------------------- unde a ajuns fiecare ---
-- Toți studenții din listă, inclusiv cei care nu au intrat niciodată.

create or replace function public.sumar_progres(p_capitol text default null)
returns table (
  matricol text, nume text, grupa text, are_cont boolean,
  slide_max int, slide_vazute int,
  verif_date int, verif_corecte int,
  ultima_data timestamptz
)
language sql security definer stable set search_path = public as $$
  with eu as (select 1 where public.sunt_profesor()),
  pr as (
    select p.matricol,
           max(nullif(split_part(g.sectiune_id, '/s', 2), '')::int) as slide_max,
           count(*) filter (where g.sectiune_id like '%/s%')        as slide_vazute,
           max(g.ultima_data)                                       as ultima_data
      from public.profiluri p
      join public.progres g on g.user_id = p.user_id
     where p_capitol is null or g.sectiune_id like p_capitol || '/%'
     group by p.matricol
  ),
  rs as (
    select p.matricol,
           count(*)::int                             as verif_date,
           count(*) filter (where r.corect)::int     as verif_corecte
      from public.profiluri p
      join public.raspunsuri r on r.user_id = p.user_id
     where p_capitol is null or r.capitol = p_capitol
     group by p.matricol
  )
  select s.matricol, s.nume, s.grupa,
         (p.user_id is not null)                as are_cont,
         coalesce(pr.slide_max, 0)              as slide_max,
         coalesce(pr.slide_vazute, 0)::int      as slide_vazute,
         coalesce(rs.verif_date, 0)             as verif_date,
         coalesce(rs.verif_corecte, 0)          as verif_corecte,
         pr.ultima_data
    from eu, public.studenti s
    left join public.profiluri p on p.matricol = s.matricol
    left join pr on pr.matricol = s.matricol
    left join rs on rs.matricol = s.matricol
   order by s.grupa nulls last, s.nume;
$$;

-- ----------------------------------------------------------- resetarea ----
-- Studentul își poate reseta propriul progres, la o lecție sau la tot.
-- Răspunsurile și progresul dispar; jurnalul rămâne, cu o intrare „reset".

create or replace function public.reset_progresul_meu(p_capitol text default null)
returns jsonb
language plpgsql security definer set search_path = public as $$
declare v_prog int; v_rasp int; v_cod int;
begin
  if auth.uid() is null then
    return jsonb_build_object('ok', false, 'mesaj', 'Nu ești autentificat.');
  end if;

  delete from public.progres
   where user_id = auth.uid()
     and (p_capitol is null or sectiune_id = p_capitol or sectiune_id like p_capitol || '/%');
  get diagnostics v_prog = row_count;

  delete from public.raspunsuri
   where user_id = auth.uid() and (p_capitol is null or capitol = p_capitol);
  get diagnostics v_rasp = row_count;

  delete from public.rulari_cod
   where user_id = auth.uid()
     and (p_capitol is null or exercitiu_id like p_capitol || '-%');
  get diagnostics v_cod = row_count;

  insert into public.evenimente (user_id, tip, capitol, detalii)
  values (auth.uid(), 'reset', p_capitol,
          jsonb_build_object('progres', v_prog, 'raspunsuri', v_rasp, 'cod', v_cod));

  return jsonb_build_object('ok', true, 'progres', v_prog,
                            'raspunsuri', v_rasp, 'cod', v_cod);
end $$;

-- Profesorul poate reseta un student anume, după numărul matricol.

create or replace function public.reset_student(
  p_matricol text, p_capitol text default null
) returns jsonb
language plpgsql security definer set search_path = public as $$
declare v_user uuid; v_prog int; v_rasp int;
begin
  if not public.sunt_profesor() then
    return jsonb_build_object('ok', false, 'mesaj', 'Numai profesorul poate face asta.');
  end if;

  select user_id into v_user from public.profiluri where matricol = p_matricol;
  if v_user is null then
    return jsonb_build_object('ok', false,
      'mesaj', 'Matricolul ' || p_matricol || ' nu are cont legat.');
  end if;

  delete from public.progres
   where user_id = v_user
     and (p_capitol is null or sectiune_id = p_capitol or sectiune_id like p_capitol || '/%');
  get diagnostics v_prog = row_count;

  delete from public.raspunsuri
   where user_id = v_user and (p_capitol is null or capitol = p_capitol);
  get diagnostics v_rasp = row_count;

  insert into public.evenimente (user_id, tip, capitol, detalii)
  values (v_user, 'reset', p_capitol,
          jsonb_build_object('de_catre', 'profesor', 'progres', v_prog, 'raspunsuri', v_rasp));

  return jsonb_build_object('ok', true, 'matricol', p_matricol,
                            'progres', v_prog, 'raspunsuri', v_rasp);
end $$;

-- ------------------------------------------------------------ curățenie ---
-- Sesiuni vechi, ca tabelul să nu crească la nesfârșit. Nu atinge jurnalul.

create or replace function public.curata_sesiuni(p_zile int default 2)
returns int
language plpgsql security definer set search_path = public as $$
declare v int;
begin
  if not public.sunt_profesor() then return 0; end if;
  delete from public.sesiuni where vazut_la < now() - make_interval(days => greatest(p_zile, 1));
  get diagnostics v = row_count;
  return v;
end $$;
