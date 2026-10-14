-- ===========================================================================
-- 14. GRUPE ȘI ȘEDINȚE
--
-- Până acum situl nu avea cum să spună „ora de marți, 14 octombrie, grupa 1,
-- lecția 3". Avea un singur steag `ritm.pornit` per lecție, iar prezența era
-- cheie (user_id, curs), adică o singură prezență per student per curs,
-- vreodată. Cu asta nu se putea ține aceeași lecție de două ori, nici anul
-- viitor, și nu se putea închide nimic, pentru că nu era nimic de închis.
--
-- Fișierul ăsta adaugă două obiecte, grupa și ședința, și o singură coloană
-- (`sedinta_id`) pe ce există deja. Atât. Din ele ies: marcarea zilei,
-- închiderea orei, statisticile pe acea zi, ștergerea unui log, exportul,
-- prezența din activitate, și regula de notare cu reluare.
--
-- Se rulează o singură dată, după 13. Se poate rula din nou fără stricăciuni.
--
-- ATENȚIE: ultima secțiune, „E. Curățenia", schimbă cheia tabelului `prezente`
-- și șterge prezențele vechi. E separată tocmai ca s-o rulezi conștient, după
-- ce te-ai uitat ce e în ea. Până atunci, restul merge și fără.
-- ===========================================================================


-- ===========================================================================
-- A. GRUPA
-- ===========================================================================

-- Grupa era o coloană de text pe student, scrisă de mână. Devine un rând,
-- ca să aibă ziua și ora ei, ca ședința să se poată deschide dintr-un clic,
-- și ca anul viitor să fie altă grupă, nu aceiași studenți suprascriși.

create table if not exists public.grupe (
  id         text primary key,                    -- 'g1'
  curs       text not null default 'dsw',
  nume       text not null,                       -- 'Grupa 1'
  an         text not null,                       -- '2026'
  zi         text,                                -- 'marți'
  ora        text,                                -- '10:00'
  activa     boolean not null default true,
  creat_la   timestamptz not null default now()
);

alter table public.grupe enable row level security;

-- Studentul capătă o legătură adevărată. Coloana veche `grupa` rămâne pe loc:
-- nu stric nimic acum, iar când totul citește din `grupa_id` o putem scoate.
alter table public.studenti
  add column if not exists grupa_id text references public.grupe(id);

create index if not exists studenti_grupa_idx on public.studenti (grupa_id);

-- Oricine e conectat poate citi grupele: sunt nume de grupe, nu date personale,
-- și ecranul de intrare are nevoie de ele înainte să știe cine e omul.
drop policy if exists grupe_citire on public.grupe;
create policy grupe_citire on public.grupe
  for select to authenticated using (true);

-- Scrisul trece prin funcție, ca peste tot.
create or replace function public.pune_grupa(
  p_id   text,
  p_nume text,
  p_an   text default '2026',
  p_zi   text default null,
  p_ora  text default null,
  p_curs text default 'dsw'
) returns jsonb
language plpgsql security definer set search_path = public as $$
begin
  if not public.sunt_profesor() then
    return jsonb_build_object('ok', false, 'mesaj', 'Numai profesorul poate face asta.');
  end if;

  insert into public.grupe (id, curs, nume, an, zi, ora)
  values (p_id, p_curs, p_nume, p_an, p_zi, p_ora)
  on conflict (id) do update
    set nume = excluded.nume, an = excluded.an,
        zi   = excluded.zi,   ora = excluded.ora, curs = excluded.curs;

  return jsonb_build_object('ok', true, 'id', p_id);
end $$;


-- ===========================================================================
-- B. ȘEDINȚA
-- ===========================================================================

create table if not exists public.sedinte (
  id            uuid primary key default gen_random_uuid(),
  capitol       text not null,                    -- 'c3'
  grupa_id      text references public.grupe(id), -- null = toate grupele
  titlu         text,                             -- 'Cursul 3, grupa 1'
  mod           text not null default 'live'
                check (mod in ('live', 'propriu')),
  cod           text,                             -- 'K7MQ2X', doar cât e deschisă
  slide_nr      int  not null default 1,
  total_nr      int,
  deschisa_la   timestamptz not null default now(),
  inchisa_la    timestamptz,                      -- null = în desfășurare
  arhivata_la   timestamptz,                      -- null = în listă
  note          text,                             -- ce ai scris tu despre ora asta
  deschisa_de   uuid references auth.users(id) on delete set null
);

alter table public.sedinte enable row level security;

create index if not exists sedinte_capitol_idx on public.sedinte (capitol, deschisa_la desc);
create index if not exists sedinte_grupa_idx   on public.sedinte (grupa_id, deschisa_la desc);

-- Codul e unic doar printre ședințele deschise. După închidere poate reveni.
create unique index if not exists sedinte_cod_viu
  on public.sedinte (cod) where inchisa_la is null and cod is not null;

-- Studenții citesc ședințele: au nevoie de slide_nr și de mod ca să știe dacă
-- sunt ținuți în ritmul tău sau merg singuri. Nu e nimic personal în tabel.
drop policy if exists sedinte_citire on public.sedinte;
create policy sedinte_citire on public.sedinte
  for select to authenticated using (true);


-- --------------------------------------------------- legătura cu restul ---
-- `null` înseamnă „a lucrat singur, în afara orei". Asta înlocuiește coloana
-- `context` cu ceva verificabil: nu mai e o etichetă pe care o scrie clientul,
-- e o legătură.

alter table public.raspunsuri  add column if not exists sedinta_id uuid references public.sedinte(id) on delete cascade;
alter table public.rulari_cod  add column if not exists sedinta_id uuid references public.sedinte(id) on delete cascade;
alter table public.evenimente  add column if not exists sedinta_id uuid references public.sedinte(id) on delete cascade;
alter table public.prezente    add column if not exists sedinta_id uuid references public.sedinte(id) on delete cascade;

create index if not exists raspunsuri_sedinta_idx on public.raspunsuri (sedinta_id);
create index if not exists rulari_sedinta_idx     on public.rulari_cod (sedinta_id);
create index if not exists evenimente_sedinta_idx on public.evenimente (sedinta_id);
create index if not exists prezente_sedinta_idx   on public.prezente (sedinta_id);


-- ===========================================================================
-- C. DESCHIDEREA ȘI ÎNCHIDEREA
-- ===========================================================================

-- Codul: șase semne din alfabetul fără O/0 și I/1/L, ca să nu se citească
-- greșit de pe proiector. Același alfabet ca la `creeaza_jeton`, din 07.
create or replace function public.cod_sedinta() returns text
language plpgsql set search_path = public as $$
declare v text := '';
begin
  while length(v) < 6 loop
    v := v || substr('ABCDEFGHJKMNPQRSTUVWXYZ23456789',
                     1 + floor(random() * 31)::int, 1);
  end loop;
  return v;
end $$;

create or replace function public.deschide_sedinta(
  p_capitol  text,
  p_grupa_id text default null,
  p_mod      text default 'live',
  p_titlu    text default null,
  p_total_nr int  default null
) returns jsonb
language plpgsql security definer set search_path = public as $$
declare
  v_id    uuid;
  v_cod   text;
  v_titlu text;
  v_vechi public.sedinte;
begin
  if not public.sunt_profesor() then
    return jsonb_build_object('ok', false, 'mesaj', 'Numai profesorul poate face asta.');
  end if;

  -- Dacă există deja una deschisă pentru aceeași lecție și grupă, o dau pe
  -- aceea. Altfel, o reîncărcare a paginii ar porni a doua ședință goală.
  select * into v_vechi from public.sedinte
   where capitol = p_capitol
     and grupa_id is not distinct from p_grupa_id
     and inchisa_la is null
   order by deschisa_la desc limit 1;

  if v_vechi.id is not null then
    return jsonb_build_object('ok', true, 'id', v_vechi.id, 'cod', v_vechi.cod,
                              'mod', v_vechi.mod, 'noua', false);
  end if;

  v_titlu := coalesce(p_titlu,
    'Cursul ' || replace(p_capitol, 'c', '') ||
    coalesce(', ' || (select lower(nume) from public.grupe where id = p_grupa_id), ''));

  -- cod nefolosit printre ședințele deschise
  loop
    v_cod := public.cod_sedinta();
    exit when not exists (select 1 from public.sedinte
                           where cod = v_cod and inchisa_la is null);
  end loop;

  insert into public.sedinte (capitol, grupa_id, titlu, mod, cod, total_nr, deschisa_de)
  values (p_capitol, p_grupa_id, v_titlu,
          case when p_mod in ('live','propriu') then p_mod else 'live' end,
          v_cod, p_total_nr, auth.uid())
  returning id into v_id;

  return jsonb_build_object('ok', true, 'id', v_id, 'cod', v_cod,
                            'titlu', v_titlu, 'noua', true);
end $$;


-- Mutarea prin slide-uri, și schimbarea modului în timpul orei.
create or replace function public.pune_sedinta(
  p_id       uuid,
  p_slide_nr int  default null,
  p_mod      text default null,
  p_note     text default null
) returns jsonb
language plpgsql security definer set search_path = public as $$
declare s public.sedinte;
begin
  if not public.sunt_profesor() then
    return jsonb_build_object('ok', false, 'mesaj', 'Numai profesorul poate face asta.');
  end if;

  update public.sedinte
     set slide_nr = coalesce(p_slide_nr, slide_nr),
         mod      = coalesce(nullif(p_mod, ''), mod),
         note     = coalesce(p_note, note)
   where id = p_id and inchisa_la is null
  returning * into s;

  if s.id is null then
    return jsonb_build_object('ok', false, 'mesaj', 'Ședința nu există sau e deja închisă.');
  end if;
  return jsonb_build_object('ok', true, 'slide_nr', s.slide_nr, 'mod', s.mod);
end $$;


-- --------------------------------------------------------- închiderea ----
-- Prezența se calculează aici, din activitate, nu din scanare: e prezent cine
-- a trimis cel puțin o sarcină în ședință. Pragul e *o trimitere*, nu *o
-- trimitere corectă* — cine a încercat și a greșit a fost acolo. Altfel
-- prezența ar măsura performanța, ceea ce nu vrem.

create or replace function public.inchide_sedinta(p_id uuid)
returns jsonb
language plpgsql security definer set search_path = public as $$
declare s public.sedinte; v_prez int;
begin
  if not public.sunt_profesor() then
    return jsonb_build_object('ok', false, 'mesaj', 'Numai profesorul poate face asta.');
  end if;

  select * into s from public.sedinte where id = p_id;
  if s.id is null then
    return jsonb_build_object('ok', false, 'mesaj', 'Ședința nu există.');
  end if;

  insert into public.prezente (user_id, curs, sedinta_id, marcat_la)
  select i.user_id, s.capitol, s.id, min(i.creat_la)
    from public.incercari i
   where i.sedinta_id = s.id
   group by i.user_id
  on conflict do nothing;

  get diagnostics v_prez = row_count;

  update public.sedinte
     set inchisa_la = now(), cod = null       -- codul moare odată cu ora
   where id = p_id;

  return jsonb_build_object('ok', true, 'prezenti', v_prez);
end $$;


-- Prezența calculată automat se poate răsturna cu un clic: uneori moare
-- bateria, pică Wi-Fi-ul, iar regula n-are cum să știe. Rămâne urma în jurnal.
create or replace function public.pune_prezenta(
  p_sedinta uuid, p_matricol text, p_prezent boolean
) returns jsonb
language plpgsql security definer set search_path = public as $$
declare v_user uuid; v_capitol text;
begin
  if not public.sunt_profesor() then
    return jsonb_build_object('ok', false, 'mesaj', 'Numai profesorul poate face asta.');
  end if;

  select user_id into v_user from public.profiluri where matricol = p_matricol;
  if v_user is null then
    return jsonb_build_object('ok', false, 'mesaj', 'Matricolul nu are cont legat.');
  end if;
  select capitol into v_capitol from public.sedinte where id = p_sedinta;

  if p_prezent then
    insert into public.prezente (user_id, curs, sedinta_id)
    values (v_user, v_capitol, p_sedinta) on conflict do nothing;
  else
    delete from public.prezente where user_id = v_user and sedinta_id = p_sedinta;
  end if;

  insert into public.evenimente (user_id, tip, capitol, sedinta_id, detalii)
  values (auth.uid(), 'prezenta_manuala', v_capitol, p_sedinta,
          jsonb_build_object('matricol', p_matricol, 'prezent', p_prezent));

  return jsonb_build_object('ok', true);
end $$;


-- ===========================================================================
-- D. CELE PATRU STĂRI, ȘI NOTAREA CU RELUARE
-- ===========================================================================

-- Verificările și exercițiile cu cod stau în două tabele, dar din punctul de
-- vedere al notei sunt același lucru: o sarcină trimisă. Vederea de mai jos le
-- pune cap la cap, și scoate cele patru stări din coloanele care există deja.
-- Nu e nevoie de nicio coloană nouă: „gol" înseamnă că n-a scris nimic.

create or replace view public.incercari as
  select r.user_id,
         r.intrebare_id                     as sarcina_id,
         'verificare'::text                 as fel,
         r.capitol,
         r.sedinta_id,
         r.creat_la,
         (r.raspuns is null)                as gol,
         coalesce(r.corect, false)          as corect
    from public.raspunsuri r
  union all
  select c.user_id,
         c.exercitiu_id,
         'cod',
         null::text,
         c.sedinta_id,
         c.creat_la,
         (coalesce(btrim(c.cod), '') = ''),
         coalesce(c.trecut, false)
    from public.rulari_cod c;

-- ATENȚIE, și e un pas pe care e ușor să-l uiți: o vedere rulează, implicit,
-- cu drepturile celui care a creat-o, nu ale celui care o interoghează. Fără
-- rândul de mai jos, `incercari` ar ocoli RLS-ul tabelelor de dedesubt, iar
-- orice student conectat ar putea citi răspunsurile întregii grupe printr-un
-- singur select. Verificat: fără el se văd toate rândurile, cu el doar ale tale.
alter view public.incercari set (security_invoker = true);

-- Funcțiile de mai jos sunt `security definer`, deci ele continuă să vadă tot,
-- după ce verifică `sunt_profesor()`. Vederea rămâne îngustă pentru studenți.
revoke all on public.incercari from anon;


-- Starea unei sarcini pentru un student, într-o ședință anume. Asta e ce vezi
-- tu în panou pe slide-ul curent:
--
--   trecut         a completat corect
--   trimis_gresit  a completat, dar greșit
--   trimis_gol     a apăsat Verifică fără să completeze
--   nefacut        nu a atins sarcina  (nu apare aici: lipsa rândului ESTE starea)

create or replace function public.stare_sarcina(
  p_sedinta uuid, p_sarcina text
) returns table (user_id uuid, stare text, cand timestamptz)
language sql security definer stable set search_path = public as $$
  select i.user_id,
         case when bool_or(i.corect)              then 'trecut'
              when bool_or(not i.gol)             then 'trimis_gresit'
              else                                     'trimis_gol' end,
         min(i.creat_la)
    from public.incercari i
   where public.sunt_profesor()
     and i.sedinta_id = p_sedinta
     and i.sarcina_id = p_sarcina
   group by i.user_id;
$$;


-- --------------------------------------------------------------- nota ----
-- Regula, în cuvinte: nota la o sarcină e cel mai bun dintre punctul luat în
-- ședință și jumătate din PRIMA completare din afara ei.
--
--   în ședință, corect          -> 1
--   acasă, prima completare bună -> 0,5
--   nota                         -> cel mai mare dintre cele două
--
-- Două lucruri care contează și nu se văd din formulă:
--
-- 1. Numai PRIMA completare din afara ședinței se notează. Restul sunt
--    exerciții, oricâte. Altfel s-ar încerca până nimerește.
-- 2. Trimiterile goale nu sunt completări. La schimbarea slide-ului, în live,
--    ce e în lucru se trimite automat, așa cum e; dacă acel „gol" ar îngheța
--    nota, regula de auto-trimitere ar pedepsi exact studentul mai lent, care
--    știa. Se înregistrează, se vede în panou, dar nu intră la notă.

create or replace function public.nota_sarcini(p_user uuid default null)
returns table (user_id uuid, sarcina_id text, fel text,
               in_sedinta boolean, acasa boolean, punct numeric)
language sql security definer stable set search_path = public as $$
  with eu as (
    select coalesce(p_user, auth.uid()) as u
  ),
  -- numai profesorul poate cere notele altcuiva
  permis as (
    select (select u from eu) as u
     where (select u from eu) = auth.uid() or public.sunt_profesor()
  ),
  i as (
    select * from public.incercari
     where user_id = (select u from permis)
  ),
  in_sed as (          -- a luat-o la oră?
    select sarcina_id, fel, bool_or(corect) as bun
      from i where sedinta_id is not null
     group by sarcina_id, fel
  ),
  afara as (           -- prima completare din afara orei, oricare ar fi ea
    select distinct on (sarcina_id, fel) sarcina_id, fel, corect as bun
      from i where sedinta_id is null and not gol
     order by sarcina_id, fel, creat_la
  )
  select (select u from permis),
         coalesce(s.sarcina_id, a.sarcina_id),
         coalesce(s.fel, a.fel),
         coalesce(s.bun, false),
         coalesce(a.bun, false),
         greatest(case when coalesce(s.bun, false) then 1.0 else 0 end,
                  case when coalesce(a.bun, false) then 0.5 else 0 end)::numeric
    from in_sed s
    full outer join afara a on a.sarcina_id = s.sarcina_id and a.fel = s.fel;
$$;


-- ===========================================================================
-- E. RAPORTUL, ARHIVA, EXPORTUL
-- ===========================================================================

create or replace function public.raport_sedinta(p_id uuid)
returns jsonb
language plpgsql security definer stable set search_path = public as $$
declare s public.sedinte; v jsonb;
begin
  if not public.sunt_profesor() then
    return jsonb_build_object('ok', false, 'mesaj', 'Numai profesorul poate face asta.');
  end if;
  select * into s from public.sedinte where id = p_id;
  if s.id is null then
    return jsonb_build_object('ok', false, 'mesaj', 'Ședința nu există.');
  end if;

  select jsonb_build_object(
    'ok', true,
    'id', s.id, 'titlu', s.titlu, 'capitol', s.capitol, 'mod', s.mod,
    'grupa', (select nume from public.grupe where id = s.grupa_id),
    'deschisa_la', s.deschisa_la, 'inchisa_la', s.inchisa_la,
    'minute', round(extract(epoch from
        coalesce(s.inchisa_la, now()) - s.deschisa_la) / 60)::int,
    'inscrisi', (select count(*) from public.studenti
                  where grupa_id is not distinct from s.grupa_id),
    'prezenti', (select count(*) from public.prezente where sedinta_id = s.id),
    'intrati',  (select count(distinct user_id) from public.incercari
                  where sedinta_id = s.id),
    'sarcini_atinse', (select count(distinct sarcina_id) from public.incercari
                        where sedinta_id = s.id),
    'impotmolire', (
      select jsonb_build_object('sarcina', x.sarcina_id,
                                'trecuti', x.trecuti, 'din', x.toti)
        from (select i.sarcina_id,
                     count(distinct i.user_id) filter (where i.corect) as trecuti,
                     count(distinct i.user_id)                          as toti
                from public.incercari i
               where i.sedinta_id = s.id
               group by i.sarcina_id
               having count(distinct i.user_id) > 2
               order by (count(distinct i.user_id) filter (where i.corect))::numeric
                        / nullif(count(distinct i.user_id), 0)
               limit 1) x),
    'texte', (select count(*) from public.evenimente
               where sedinta_id = s.id and tip in ('asteptari', 'text'))
  ) into v;
  return v;
end $$;


-- Un rând per student, pentru tabelul din raport și pentru export.
create or replace function public.sumar_sedinta(p_id uuid)
returns table (matricol text, nume text, prezent boolean,
               trimise int, trecute int, goale int, prima timestamptz)
language sql security definer stable set search_path = public as $$
  select coalesce(p.matricol, '—'),
         coalesce(st.nume, 'fără cont legat'),
         exists (select 1 from public.prezente z
                  where z.sedinta_id = p_id and z.user_id = i.user_id),
         count(distinct i.sarcina_id)::int,
         count(distinct i.sarcina_id) filter (where i.corect)::int,
         count(distinct i.sarcina_id) filter (where i.gol)::int,
         min(i.creat_la)
    from public.incercari i
    left join public.profiluri p on p.user_id = i.user_id
    left join public.studenti st on st.matricol = p.matricol
   where public.sunt_profesor() and i.sedinta_id = p_id
   group by p.matricol, st.nume, i.user_id
   order by 2;
$$;


-- ------------------------------------------------------------- arhiva ----
-- Ștergerea nu e definitivă pe loc: ședința iese din listă imediat, dar stă
-- 30 de zile în arhivă, de unde se aduce înapoi cu un clic. Butonul pe care
-- îl apeși în grabă, la sfârșitul orei, e cel care NU distruge nimic.

create or replace function public.arhiveaza_sedinta(p_id uuid, p_inapoi boolean default false)
returns jsonb
language plpgsql security definer set search_path = public as $$
begin
  if not public.sunt_profesor() then
    return jsonb_build_object('ok', false, 'mesaj', 'Numai profesorul poate face asta.');
  end if;
  update public.sedinte
     set arhivata_la = case when p_inapoi then null else now() end
   where id = p_id;
  return jsonb_build_object('ok', true, 'arhivata', not p_inapoi);
end $$;


create or replace function public.goleste_arhiva(p_zile int default 30)
returns int
language plpgsql security definer set search_path = public as $$
declare v int;
begin
  if not public.sunt_profesor() then return 0; end if;
  delete from public.sedinte
   where arhivata_la is not null
     and arhivata_la < now() - make_interval(days => greatest(p_zile, 1));
  get diagnostics v = row_count;
  return v;   -- cascada ia cu ea răspunsurile, rulările și prezențele ședinței
end $$;


create or replace function public.lista_sedinte(
  p_arhivate boolean default false,
  p_capitol  text    default null
) returns table (id uuid, titlu text, capitol text, grupa text, mod text,
                 deschisa_la timestamptz, inchisa_la timestamptz,
                 minute int, prezenti int, zile_ramase int)
language sql security definer stable set search_path = public as $$
  select s.id, s.titlu, s.capitol,
         (select nume from public.grupe where id = s.grupa_id),
         s.mod, s.deschisa_la, s.inchisa_la,
         round(extract(epoch from coalesce(s.inchisa_la, now()) - s.deschisa_la)/60)::int,
         (select count(*)::int from public.prezente where sedinta_id = s.id),
         case when s.arhivata_la is null then null
              else greatest(0, 30 - extract(day from now() - s.arhivata_la)::int) end
    from public.sedinte s
   where public.sunt_profesor()
     and (s.arhivata_la is not null) = p_arhivate
     and (p_capitol is null or s.capitol = p_capitol)
   order by s.deschisa_la desc;
$$;


-- ===========================================================================
-- F. CURĂȚENIA  —  citește înainte de a rula
--
-- Blocul ăsta schimbă cheia tabelului `prezente`, din (user_id, curs) în
-- (user_id, sedinta_id). Fără el, un student tot nu poate fi prezent de două
-- ori la aceeași lecție, deci bug-ul rămâne.
--
-- Prețul: prezențele vechi nu au ședință, deci nu încap în cheia nouă și se
-- șterg. Dacă ai prezențe la care ții, scoate-le întâi:
--     select * from public.prezente;
--
-- Rulează-l separat, nu odată cu restul fișierului.
-- ===========================================================================

-- do $$
-- begin
--   delete from public.prezente where sedinta_id is null;
--   alter table public.prezente drop constraint if exists prezente_pkey;
--   alter table public.prezente alter column sedinta_id set not null;
--   alter table public.prezente add primary key (user_id, sedinta_id);
-- end $$;


-- ===========================================================================
-- G. DE UNDE ÎNCEPI
--
-- O grupă și prima ședință, ca să ai ce vedea în panou:
--
--   select public.pune_grupa('g1', 'Grupa 1', '2026', 'marți', '10:00');
--   update public.studenti set grupa_id = 'g1' where grupa = '1';
--   select public.deschide_sedinta('c1', 'g1', 'live');
--
-- Și, la sfârșit de oră:
--
--   select public.inchide_sedinta('<id-ul de mai sus>');
--   select public.raport_sedinta('<id>');
--   select * from public.sumar_sedinta('<id>');
-- ===========================================================================
