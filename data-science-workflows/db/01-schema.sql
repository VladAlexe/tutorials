-- ============================================================================
--  Fluxuri de lucru pentru stiinta datelor
--  01. Schema
--
--  Se ruleaza o singura data, in SQL Editor din panoul Supabase.
--  Ruleaza-l intreg, de sus in jos. Daca dai de o eroare, opreste-te si
--  spune-mi care este; nu continua cu fisierul urmator.
-- ============================================================================

-- ----------------------------------------------------------------------------
--  Lista oficiala de studenti. O incarci tu, din lista de la secretariat.
--  Studentii NU citesc niciodata acest tabel: altfel ar vedea matricolele
--  colegilor si le-ar putea revendica. Verificarea se face printr-o functie,
--  mai jos.
-- ----------------------------------------------------------------------------
create table if not exists public.studenti (
  matricol    text primary key,
  nume        text not null,
  an          int,
  grupa       text,
  creat_la    timestamptz not null default now()
);

-- ----------------------------------------------------------------------------
--  Legatura dintre contul de autentificare si matricol.
--  Un cont are cel mult un matricol; un matricol are cel mult un cont.
-- ----------------------------------------------------------------------------
create table if not exists public.profiluri (
  user_id        uuid primary key references auth.users(id) on delete cascade,
  matricol       text unique not null references public.studenti(matricol),
  email          text,
  github_login   text,
  revendicat_la  timestamptz not null default now()
);

-- ----------------------------------------------------------------------------
--  Cine e profesor. Te adaugi manual, o singura data, dupa ce te
--  autentifici prima data (instructiunile sunt in db/README.md).
-- ----------------------------------------------------------------------------
create table if not exists public.profesori (
  user_id   uuid primary key references auth.users(id) on delete cascade,
  adaugat_la timestamptz not null default now()
);

-- ----------------------------------------------------------------------------
--  Raspunsurile la verificari.
--  intrebare_id are forma "2.3-v1", asa cum e in fisierele de continut.
-- ----------------------------------------------------------------------------
create table if not exists public.raspunsuri (
  id            bigint generated always as identity primary key,
  user_id       uuid not null references auth.users(id) on delete cascade,
  intrebare_id  text not null,
  capitol       text,
  raspuns       int,
  corect        boolean,
  creat_la      timestamptz not null default now()
);

create index if not exists raspunsuri_user_idx on public.raspunsuri (user_id);
create index if not exists raspunsuri_intrebare_idx on public.raspunsuri (intrebare_id);

-- ----------------------------------------------------------------------------
--  Rulari de cod din exercitiile din pagina.
-- ----------------------------------------------------------------------------
create table if not exists public.rulari_cod (
  id            bigint generated always as identity primary key,
  user_id       uuid not null references auth.users(id) on delete cascade,
  exercitiu_id  text not null,
  cod           text,
  trecut        boolean,
  creat_la      timestamptz not null default now()
);

create index if not exists rulari_user_idx on public.rulari_cod (user_id);

-- ----------------------------------------------------------------------------
--  Progresul prin secțiuni. Un rand per student si secțiune.
-- ----------------------------------------------------------------------------
create table if not exists public.progres (
  user_id       uuid not null references auth.users(id) on delete cascade,
  sectiune_id   text not null,
  prima_data    timestamptz not null default now(),
  ultima_data   timestamptz not null default now(),
  primary key (user_id, sectiune_id)
);

-- ----------------------------------------------------------------------------
--  Prezenta. Se marcheaza prin scanarea codului QR de la curs.
-- ----------------------------------------------------------------------------
create table if not exists public.prezente (
  user_id     uuid not null references auth.users(id) on delete cascade,
  curs        text not null,
  marcat_la   timestamptz not null default now(),
  primary key (user_id, curs)
);

-- ----------------------------------------------------------------------------
--  Jetoane pentru codul QR de prezenta. Scurte, cu expirare.
-- ----------------------------------------------------------------------------
create table if not exists public.jetoane_prezenta (
  jeton       text primary key,
  curs        text not null,
  expira_la   timestamptz not null,
  creat_la    timestamptz not null default now()
);


-- ============================================================================
--  Activam Row Level Security pe toate tabelele, chiar aici, la creare.
--
--  Din acest moment tabelele sunt INCHISE: nimeni nu citeste si nu scrie
--  nimic prin cheia publica. Permisiunile, adica cine are voie la ce, se
--  adauga in fisierul urmator, 02-politici.sql.
--
--  Ordinea e intentionata: intai inchidem, apoi deschidem exact cat trebuie.
--  Asa, daca ceva se opreste la jumatate, datele raman inaccesibile, nu
--  expuse. Tu, din editorul de SQL, rulezi ca administrator si treci peste
--  aceste reguli, deci poti incarca listele normal.
-- ============================================================================

alter table public.studenti          enable row level security;
alter table public.profiluri         enable row level security;
alter table public.profesori         enable row level security;
alter table public.raspunsuri        enable row level security;
alter table public.rulari_cod        enable row level security;
alter table public.progres           enable row level security;
alter table public.prezente          enable row level security;
alter table public.jetoane_prezenta  enable row level security;


-- ============================================================================
--  FUNCTII
-- ============================================================================

-- ----------------------------------------------------------------------------
--  sunt_profesor(): folosita de politicile de acces.
--  security definer, ca sa poata citi tabelul profesori chiar daca
--  politicile nu dau acces direct la el.
-- ----------------------------------------------------------------------------
create or replace function public.sunt_profesor()
returns boolean
language sql
security definer
stable
set search_path = public
as $$
  select exists (select 1 from public.profesori where user_id = auth.uid());
$$;

-- ----------------------------------------------------------------------------
--  revendica_matricol(): singura cale prin care un student se leaga de un
--  matricol. Verifica totul si nu dezvaluie nimic despre lista.
--
--  Intoarce un obiect JSON cu { ok, mesaj, nume }.
-- ----------------------------------------------------------------------------
create or replace function public.revendica_matricol(p_matricol text)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_user   uuid := auth.uid();
  v_mat    text := upper(trim(p_matricol));
  v_nume   text;
  v_deja   text;
begin
  if v_user is null then
    return jsonb_build_object('ok', false, 'mesaj', 'Nu esti autentificat.');
  end if;

  if v_mat is null or v_mat = '' then
    return jsonb_build_object('ok', false, 'mesaj', 'Introdu numarul matricol.');
  end if;

  -- acest cont a revendicat deja un matricol?
  select matricol into v_deja from public.profiluri where user_id = v_user;
  if v_deja is not null then
    if v_deja = v_mat then
      select nume into v_nume from public.studenti where matricol = v_mat;
      return jsonb_build_object('ok', true, 'mesaj', 'Deja inregistrat.', 'nume', v_nume);
    end if;
    return jsonb_build_object('ok', false,
      'mesaj', 'Contul acesta e deja legat de alt numar matricol. Scrie-mi ca sa il schimb.');
  end if;

  -- matricolul exista pe lista?
  select nume into v_nume from public.studenti where matricol = v_mat;
  if v_nume is null then
    return jsonb_build_object('ok', false,
      'mesaj', 'Numarul acesta nu apare pe lista cursului. Verifica cifrele sau scrie-mi.');
  end if;

  -- a fost revendicat de altcineva?
  if exists (select 1 from public.profiluri where matricol = v_mat) then
    return jsonb_build_object('ok', false,
      'mesaj', 'Numarul acesta a fost deja revendicat de alt cont. Scrie-mi.');
  end if;

  insert into public.profiluri (user_id, matricol, email, github_login)
  values (
    v_user,
    v_mat,
    (select email from auth.users where id = v_user),
    (select raw_user_meta_data->>'user_name' from auth.users where id = v_user)
  );

  return jsonb_build_object('ok', true, 'mesaj', 'Inregistrat.', 'nume', v_nume);
end;
$$;

-- ----------------------------------------------------------------------------
--  profilul_meu(): ce vede studentul despre el insusi.
--  Nu expune nimic despre altcineva.
-- ----------------------------------------------------------------------------
create or replace function public.profilul_meu()
returns jsonb
language sql
security definer
stable
set search_path = public
as $$
  select case
    when auth.uid() is null then jsonb_build_object('autentificat', false)
    else coalesce(
      (select jsonb_build_object(
          'autentificat', true,
          'matricol', p.matricol,
          'nume', s.nume,
          'grupa', s.grupa,
          'github_login', p.github_login,
          'profesor', public.sunt_profesor()
        )
       from public.profiluri p
       join public.studenti s on s.matricol = p.matricol
       where p.user_id = auth.uid()),
      jsonb_build_object(
        'autentificat', true,
        'matricol', null,
        'profesor', public.sunt_profesor())
    )
  end;
$$;

-- ----------------------------------------------------------------------------
--  marcheaza_prezenta(): scanarea codului QR.
-- ----------------------------------------------------------------------------
create or replace function public.marcheaza_prezenta(p_jeton text)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_user uuid := auth.uid();
  v_curs text;
begin
  if v_user is null then
    return jsonb_build_object('ok', false, 'mesaj', 'Nu esti autentificat.');
  end if;

  if not exists (select 1 from public.profiluri where user_id = v_user) then
    return jsonb_build_object('ok', false, 'mesaj', 'Inregistreaza-te mai intai cu numarul matricol.');
  end if;

  select curs into v_curs
  from public.jetoane_prezenta
  where jeton = p_jeton and expira_la > now();

  if v_curs is null then
    return jsonb_build_object('ok', false, 'mesaj', 'Codul nu mai e valabil.');
  end if;

  insert into public.prezente (user_id, curs)
  values (v_user, v_curs)
  on conflict (user_id, curs) do nothing;

  return jsonb_build_object('ok', true, 'mesaj', 'Prezenta inregistrata.', 'curs', v_curs);
end;
$$;

-- drepturi de apel pentru utilizatorii autentificati
revoke all on function public.revendica_matricol(text) from public, anon;
revoke all on function public.marcheaza_prezenta(text) from public, anon;
grant execute on function public.revendica_matricol(text) to authenticated;
grant execute on function public.marcheaza_prezenta(text) to authenticated;
grant execute on function public.profilul_meu() to authenticated, anon;
grant execute on function public.sunt_profesor() to authenticated;
