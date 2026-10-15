-- ===========================================================================
-- 15. PANOUL LIVE ȘI ECRANUL DE INTRARE
--
-- Fișierul 14 a adus obiectele: grupa și ședința. Aici sunt funcțiile pe care
-- le cheamă cele două ecrane noi.
--
-- Pentru panou, totul se învârte în jurul unei singure întrebări, pusă în timp
-- ce stai în fața clasei: pot merge mai departe? De aceea `panou_slide` nu
-- întoarce „progresul general", ci starea pe sarcinile de pe slide-ul care e
-- chiar acum pe proiector, un rând per student, cu ce a ales. Un apel, nu
-- unul per student și nu unul per sarcină.
--
-- Pentru intrare, `lista_grupei` dă numele celor din grupă, fără matricol, ca
-- studentul să se recunoască dintr-un tap. Matricolul nu iese din server.
--
-- Se rulează o singură dată, după 14. Se poate rula din nou fără stricăciuni.
-- ===========================================================================


-- ===========================================================================
-- 0. PGCRYPTO
--
-- `digest()` vine din pgcrypto, iar în Supabase pgcrypto stă în schema
-- `extensions`, nu în `public`. O funcție scrisă cu `set search_path = public`
-- pur și simplu nu-l vede, și creșterea ei eșuează cu
--     ERROR: function digest(text, unknown) does not exist
--
-- De aceea funcțiile care îl folosesc au `search_path = public, extensions`,
-- iar extensia se declară aici, înainte de ele: o funcție `language sql` se
-- verifică la creare, nu la prima chemare.
-- ===========================================================================

create schema if not exists extensions;
create extension if not exists pgcrypto with schema extensions;


-- ===========================================================================
-- A. PANOUL, PE SLIDE-UL CURENT
-- ===========================================================================

-- Un rând per student înscris în grupa ședinței, plus invitații care au
-- lucrat în ea. Cine n-a atins nimic apare oricum, cu starea `nefacut`:
-- absența lui din tabel ar fi exact informația pe care o pierzi.

create or replace function public.panou_slide(
  p_sedinta  uuid,
  p_sarcini  text[] default '{}'
)
returns table (
  matricol   text,
  nume       text,
  stare      text,     -- trecut | trimis_gresit | trimis_gol | nefacut
  ales       int,      -- indicele variantei alese, pentru verificări
  cand       timestamptz,
  facute     int,      -- sarcini trecute în toată ședința
  trimise    int,      -- sarcini atinse în toată ședința
  vazut_la   timestamptz
)
language sql security definer stable set search_path = public as $$
  with s as (
    select * from public.sedinte where id = p_sedinta
  ),
  -- cine ar trebui să fie în sală
  inscrisi as (
    select st.matricol, st.nume, p.user_id
      from public.studenti st
      left join public.profiluri p on p.matricol = st.matricol
     where st.grupa_id is not distinct from (select grupa_id from s)
       and coalesce(st.invitat, false) = false
  ),
  -- plus cine a lucrat efectiv în ședință, chiar dacă nu e în grupă
  veniti as (
    select distinct i.user_id from public.incercari i where i.sedinta_id = p_sedinta
  ),
  oameni as (
    select coalesce(i.matricol, p2.matricol, '—') as matricol,
           coalesce(i.nume, st2.nume, 'fără cont legat') as nume,
           coalesce(i.user_id, v.user_id) as user_id
      from inscrisi i
      full outer join veniti v on v.user_id = i.user_id
      left join public.profiluri p2 on p2.user_id = v.user_id
      left join public.studenti  st2 on st2.matricol = p2.matricol
  ),
  -- starea pe sarcinile slide-ului curent
  pe_slide as (
    select i.user_id,
           bool_or(i.corect)      as vreun_corect,
           bool_or(not i.gol)     as vreo_completare,
           count(*)               as cate,
           min(i.creat_la)        as cand
      from public.incercari i
     where i.sedinta_id = p_sedinta
       and i.sarcina_id = any(p_sarcini)
     group by i.user_id
  ),
  -- ce a ales: ultimul răspuns la o verificare de pe slide-ul curent
  alegerea as (
    select distinct on (r.user_id) r.user_id, r.raspuns
      from public.raspunsuri r
     where r.sedinta_id = p_sedinta
       and r.intrebare_id = any(p_sarcini)
     order by r.user_id, r.creat_la desc
  ),
  -- cât a făcut din toată ora
  toata_ora as (
    select i.user_id,
           count(distinct i.sarcina_id) filter (where i.corect) as facute,
           count(distinct i.sarcina_id)                          as trimise
      from public.incercari i
     where i.sedinta_id = p_sedinta
     group by i.user_id
  ),
  -- ultima bătaie de inimă, ca să se vadă cine s-a desprins
  vii as (
    select se.user_id, max(se.vazut_la) as vazut_la
      from public.sesiuni se group by se.user_id
  )
  select o.matricol, o.nume,
         case when p.vreun_corect       then 'trecut'
              when p.vreo_completare    then 'trimis_gresit'
              when p.cate is not null   then 'trimis_gol'
              else                           'nefacut' end,
         a.raspuns,
         p.cand,
         coalesce(t.facute, 0)::int,
         coalesce(t.trimise, 0)::int,
         v.vazut_la
    from oameni o
    left join pe_slide  p on p.user_id = o.user_id
    left join alegerea  a on a.user_id = o.user_id
    left join toata_ora t on t.user_id = o.user_id
    left join vii       v on v.user_id = o.user_id
   where public.sunt_profesor()
   order by o.nume;
$$;


-- Ce ședință e deschisă acum. Panoul o cere la deschidere, ca să nu-l pun pe
-- profesor să aleagă dintr-o listă ce e oricum evident: ora care e în curs.
create or replace function public.sedinta_deschisa(p_capitol text default null)
returns table (id uuid, capitol text, titlu text, grupa_id text, grupa text,
               mod text, cod text, slide_nr int, total_nr int,
               deschisa_la timestamptz, minute int, in_clasa int)
language sql security definer stable set search_path = public as $$
  select s.id, s.capitol, s.titlu, s.grupa_id,
         (select nume from public.grupe where id = s.grupa_id),
         s.mod, s.cod, s.slide_nr, s.total_nr, s.deschisa_la,
         round(extract(epoch from now() - s.deschisa_la) / 60)::int,
         (select count(distinct i.user_id)::int from public.incercari i
           where i.sedinta_id = s.id)
    from public.sedinte s
   where public.sunt_profesor()
     and s.inchisa_la is null
     and s.arhivata_la is null
     and (p_capitol is null or s.capitol = p_capitol)
   order by s.deschisa_la desc
   limit 1;
$$;


-- ===========================================================================
-- B. ECRANUL DE INTRARE
-- ===========================================================================

-- Lista grupei, după codul de pe proiector. Întoarce NUMELE, nu matricolele:
-- studentul se recunoaște dintr-un tap, iar numărul matricol nu are de ce să
-- plece de pe server. Marcăm cine e deja luat, ca să nu intre doi pe același
-- nume, dar îl lăsăm vizibil, ca omul adevărat să-și găsească rândul.
--
-- Funcția e `security definer` și o poate chema oricine e autentificat: ca să
-- vezi lista trebuie să ai codul orei, care e scurt, expiră, și stă pe
-- proiector, în sală.

create or replace function public.lista_grupei(p_cod text)
returns table (cheie text, nume text, luat boolean)
language sql security definer stable
  set search_path = public, extensions as $$
  with s as (
    select * from public.sedinte
     where upper(btrim(cod)) = upper(btrim(p_cod))
       and inchisa_la is null
     limit 1
  )
  select encode(extensions.digest(st.matricol || 'dsw', 'sha256'), 'hex'),
         st.nume,
         (p.user_id is not null)
    from public.studenti st
    left join public.profiluri p on p.matricol = st.matricol
   where auth.uid() is not null
     and st.grupa_id is not distinct from (select grupa_id from s)
     and coalesce(st.invitat, false) = false
     and exists (select 1 from s)
   order by st.nume;
$$;

-- Cheia de mai sus nu e matricolul, e o amprentă a lui. Studentul trimite
-- înapoi amprenta, serverul găsește rândul. Așa numărul matricol nu ajunge
-- niciodată în pagină, nici măcar ascuns în marcaj.

create or replace function public.intra_in_sedinta(p_cod text, p_cheie text)
returns jsonb
language plpgsql security definer
  set search_path = public, extensions as $$
declare
  v_user uuid := auth.uid();
  v_sed  public.sedinte;
  v_mat  text;
  v_nume text;
  v_alt  uuid;
begin
  if v_user is null then
    return jsonb_build_object('ok', false, 'mesaj', 'Nu ești autentificat.');
  end if;

  select * into v_sed from public.sedinte
   where upper(btrim(cod)) = upper(btrim(p_cod)) and inchisa_la is null
   limit 1;
  if v_sed.id is null then
    return jsonb_build_object('ok', false, 'mesaj', 'Codul nu e bun sau ora s-a închis.');
  end if;

  select st.matricol, st.nume into v_mat, v_nume
    from public.studenti st
   where st.grupa_id is not distinct from v_sed.grupa_id
     and encode(extensions.digest(st.matricol || 'dsw', 'sha256'), 'hex') = p_cheie;

  if v_mat is null then
    return jsonb_build_object('ok', false, 'mesaj', 'Nu te găsesc în lista grupei.');
  end if;

  select user_id into v_alt from public.profiluri where matricol = v_mat;
  if v_alt is not null and v_alt <> v_user then
    return jsonb_build_object('ok', false,
      'mesaj', 'Cineva a intrat deja cu numele ăsta. Spune-i profesorului.');
  end if;

  insert into public.profiluri (user_id, matricol)
  values (v_user, v_mat)
  on conflict (user_id) do update set matricol = excluded.matricol;

  insert into public.evenimente (user_id, tip, capitol, sedinta_id, detalii)
  values (v_user, 'intrare_sedinta', v_sed.capitol, v_sed.id,
          jsonb_build_object('matricol', v_mat));

  return jsonb_build_object('ok', true, 'nume', v_nume,
                            'sedinta', v_sed.id, 'capitol', v_sed.capitol,
                            'titlu', v_sed.titlu, 'mod', v_sed.mod,
                            'slide_nr', v_sed.slide_nr);
end $$;


-- Studentul deja cunoscut: scanează codul și intră direct, fără listă.
create or replace function public.sedinta_dupa_cod(p_cod text)
returns jsonb
language plpgsql security definer stable set search_path = public as $$
declare v_sed public.sedinte; v_mat text; v_nume text;
begin
  select * into v_sed from public.sedinte
   where upper(btrim(cod)) = upper(btrim(p_cod)) and inchisa_la is null limit 1;
  if v_sed.id is null then
    return jsonb_build_object('ok', false, 'mesaj', 'Codul nu e bun sau ora s-a închis.');
  end if;

  select p.matricol, st.nume into v_mat, v_nume
    from public.profiluri p
    left join public.studenti st on st.matricol = p.matricol
   where p.user_id = auth.uid();

  return jsonb_build_object('ok', true, 'sedinta', v_sed.id,
    'capitol', v_sed.capitol, 'titlu', v_sed.titlu, 'mod', v_sed.mod,
    'slide_nr', v_sed.slide_nr, 'grupa_id', v_sed.grupa_id,
    'cunoscut', (v_mat is not null and v_mat not like 'G-%'),
    'nume', v_nume);
end $$;


-- Ce trebuie să știe pagina lecției, la student: e ora pornită, în ce mod,
-- la ce slide, și de ce ședință să lege ce trimite. O singură cerere, la
-- fiecare bătaie, deci cât mai ieftină cu putință.
create or replace function public.ora_acum(p_capitol text)
returns jsonb
language sql security definer stable set search_path = public as $$
  select coalesce(
    (select jsonb_build_object('viu', true, 'sedinta', s.id, 'mod', s.mod,
                               'slide_nr', s.slide_nr, 'titlu', s.titlu)
       from public.sedinte s
      where s.capitol = p_capitol and s.inchisa_la is null
      order by s.deschisa_la desc limit 1),
    jsonb_build_object('viu', false));
$$;

