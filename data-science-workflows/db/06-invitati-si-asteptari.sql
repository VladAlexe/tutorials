-- ===========================================================================
-- 06. INTRARE CA INVITAT, AȘTEPTĂRI, ȘI CODUL SCRIS DE STUDENȚI
--
-- Se rulează o singură dată, după 05. Se poate rula din nou fără stricăciuni.
--
-- ATENȚIE, un pas în interfața Supabase înainte de a rula:
--   Authentication → Sign In / Providers → Anonymous sign-ins → ON
-- Fără el, intrarea ca invitat dă eroarea „Anonymous sign-ins are disabled".
-- ===========================================================================

-- ------------------------------------------------------------- invitații --
-- Un invitat e un student ca oricare altul, doar că matricolul lui începe cu
-- „G-" și nu vine din lista oficială. Apare în panou ca toți ceilalți, se
-- șterge ușor, și nu amestecă statistica: grupa lui e „invitat".

alter table public.studenti
  add column if not exists invitat boolean not null default false;

create or replace function public.intra_ca_invitat(p_nume text default null)
returns jsonb
language plpgsql security definer set search_path = public as $$
declare
  v_user uuid := auth.uid();
  v_mat  text;
  v_nume text;
  v_vechi text;
begin
  if v_user is null then
    return jsonb_build_object('ok', false, 'mesaj', 'Nu ești autentificat.');
  end if;

  -- dacă utilizatorul are deja un profil, nu îi mai facem altul
  select matricol into v_vechi from public.profiluri where user_id = v_user;
  if v_vechi is not null then
    return jsonb_build_object('ok', true, 'matricol', v_vechi, 'deja', true);
  end if;

  v_nume := nullif(btrim(coalesce(p_nume, '')), '');
  if v_nume is null then v_nume := 'Invitat'; end if;
  v_nume := left(v_nume, 60);

  -- matricol scurt și lizibil, din primele caractere ale id-ului
  v_mat := 'G-' || upper(substr(replace(v_user::text, '-', ''), 1, 6));

  insert into public.studenti (matricol, nume, grupa, invitat)
  values (v_mat, v_nume, 'invitat', true)
  on conflict (matricol) do update set nume = excluded.nume;

  insert into public.profiluri (user_id, matricol, email)
  values (v_user, v_mat, null)
  on conflict (user_id) do nothing;

  insert into public.evenimente (user_id, tip, detalii)
  values (v_user, 'invitat', jsonb_build_object('nume', v_nume));

  return jsonb_build_object('ok', true, 'matricol', v_mat, 'nume', v_nume);
end $$;

-- Ștergerea invitaților, ca să nu se adune de la o grupă la alta.
create or replace function public.sterge_invitatii(p_ore int default 24)
returns int
language plpgsql security definer set search_path = public as $$
declare v int;
begin
  if not public.sunt_profesor() then return 0; end if;
  delete from public.studenti s
   where s.invitat
     and not exists (
       select 1 from public.profiluri p
        join public.sesiuni se on se.user_id = p.user_id
       where p.matricol = s.matricol
         and se.vazut_la > now() - make_interval(hours => greatest(p_ore, 1)));
  get diagnostics v = row_count;
  return v;
end $$;

-- ------------------------------------------------------------- așteptări --
-- Text liber, scris de student la începutul cursului. Se ține în jurnal, ca
-- orice altceva, dar are nevoie de o funcție proprie ca să îl pot citi grupat.

create or replace function public.sumar_asteptari(p_capitol text default 'c1')
returns table (matricol text, nume text, grupa text, text text, creat_la timestamptz)
language sql security definer stable set search_path = public as $$
  select coalesce(p.matricol, '—'),
         coalesce(s.nume, 'fără cont legat'),
         s.grupa,
         e.detalii->>'text',
         e.creat_la
    from public.evenimente e
    left join public.profiluri p on p.user_id = e.user_id
    left join public.studenti s  on s.matricol = p.matricol
   where public.sunt_profesor()
     and e.tip = 'asteptari'
     and (p_capitol is null or e.capitol = p_capitol)
     and coalesce(btrim(e.detalii->>'text'), '') <> ''
   order by e.creat_la desc;
$$;

-- --------------------------------------------------- codul scris de ei ----
-- Ce au trimis la exercițiile cu cod. Ultima rezolvare per student și
-- exercițiu, ca să nu se umple ecranul cu încercări.

create or replace function public.sumar_cod(p_exercitiu text default null)
returns table (
  exercitiu_id text, matricol text, nume text, grupa text,
  cod text, trecut boolean, creat_la timestamptz, incercari int
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
  )
  select r.exercitiu_id, coalesce(r.matricol, '—'),
         coalesce(s.nume, 'fără cont legat'), s.grupa,
         r.cod, r.trecut, r.creat_la, r.incercari::int
    from r left join public.studenti s on s.matricol = r.matricol
   where r.rn = 1
   order by r.exercitiu_id, s.nume;
$$;

-- --------------------------------------- autoevaluarea, strânsă pe grupă ---
-- Ce a bifat fiecare la „ce știi deja", ca să văd profilul grupei dintr-o
-- privire, nu citind 25 de jurnale.

create or replace function public.sumar_autoevaluare(p_capitol text default 'c1')
returns table (tema text, nivel int, cati int)
language sql security definer stable set search_path = public as $$
  select k.key, (k.value)::text::int, count(*)::int
    from public.evenimente e
    cross join lateral jsonb_each(e.detalii) as k(key, value)
   where public.sunt_profesor()
     and e.tip = 'autoevaluare'
     and (p_capitol is null or e.capitol = p_capitol)
     and jsonb_typeof(k.value) = 'number'
   group by k.key, (k.value)::text::int
   order by k.key, 2;
$$;
