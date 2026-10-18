-- ===========================================================================
-- 17. Ora uitată deschisă se închide singură, după 3 ore.
--
-- Se rulează o dată, în Supabase (SQL Editor), după 14 și 15.
--
-- Cum: (1) o funcție care închide orele mai vechi de 3 ore, cu ora de
-- închidere pusă la deschidere + 3 ore (nu „acum”, ca durata din statistici
-- să rămână cinstită); (2) funcțiile care caută „ora deschisă” nu mai văd o
-- oră mai veche de 3 ore, chiar dacă încă nu a închis-o nimeni; (3) la
-- pornirea unei ore noi se face curățenia.
-- ===========================================================================

create or replace function public.inchide_orele_uitate()
returns int
language plpgsql security definer set search_path = public as $$
declare n int;
begin
  -- prezența se ia din activitate, ca la închiderea obișnuită (inchide_sedinta)
  insert into public.prezente (user_id, curs, sedinta_id, marcat_la)
  select i.user_id, s.capitol, s.id, min(i.creat_la)
    from public.sedinte s
    join public.incercari i on i.sedinta_id = s.id
   where s.inchisa_la is null
     and s.deschisa_la < now() - interval '3 hours'
   group by i.user_id, s.capitol, s.id
  on conflict do nothing;

  update public.sedinte
     set inchisa_la = deschisa_la + interval '3 hours'
   where inchisa_la is null
     and deschisa_la < now() - interval '3 hours';
  get diagnostics n = row_count;
  return n;
end $$;

grant execute on function public.inchide_orele_uitate() to authenticated;

-- curățenia de acum, pentru ce a rămas deschis până azi
select public.inchide_orele_uitate();

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

  -- orele uitate deschise se închid înainte de orice
  perform public.inchide_orele_uitate();

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
     and s.deschisa_la > now() - interval '3 hours'
     and (p_capitol is null or s.capitol = p_capitol)
   order by s.deschisa_la desc
   limit 1;
$$;

create or replace function public.lista_grupei(p_cod text)
returns table (cheie text, nume text, luat boolean)
language sql security definer stable
  set search_path = public, extensions as $$
  with s as (
    select * from public.sedinte
     where upper(btrim(cod)) = upper(btrim(p_cod))
       and inchisa_la is null
       and deschisa_la > now() - interval '3 hours'
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
     and deschisa_la > now() - interval '3 hours'
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

create or replace function public.sedinta_dupa_cod(p_cod text)
returns jsonb
language plpgsql security definer stable set search_path = public as $$
declare v_sed public.sedinte; v_mat text; v_nume text; v_inchisa boolean;
begin
  /* Caut întâi fără filtru de „deschisă", ca să pot spune care din două e:
     un cod inventat și o oră care tocmai s-a închis cer de la om lucruri
     diferite. „Codul nu e bun sau ora s-a închis" nu ajută pe nimeni. */
  select * into v_sed from public.sedinte
   where upper(btrim(cod)) = upper(btrim(p_cod))
   order by deschisa_la desc limit 1;

  if v_sed.id is null then
    return jsonb_build_object('ok', false, 'cod_gresit', true,
      'mesaj', 'Codul ăsta nu există. Verifică semnele de pe ecran.');
  end if;

  v_inchisa := v_sed.inchisa_la is not null
               or v_sed.deschisa_la < now() - interval '3 hours';
  if v_inchisa then
    return jsonb_build_object('ok', false, 'inchisa', true,
      'mesaj', 'Ora s-a închis. Poți intra în lecție, dar nu mai contează ca prezență.',
      'capitol', v_sed.capitol);
  end if;

  select p.matricol, st.nume into v_mat, v_nume
    from public.profiluri p
    left join public.studenti st on st.matricol = p.matricol
   where p.user_id = auth.uid();

  return jsonb_build_object('ok', true, 'sedinta', v_sed.id,
    'capitol', v_sed.capitol, 'titlu', v_sed.titlu, 'mod', v_sed.mod,
    'slide_nr', v_sed.slide_nr, 'grupa_id', v_sed.grupa_id,
    /* profesorul care scanează propriul cod nu e un student fără nume:
       nu are ce căuta în lista grupei */
    'profesor', public.sunt_profesor(),
    'cunoscut', (v_mat is not null and v_mat not like 'G-%'),
    'nume', v_nume);
end $$;

create or replace function public.ora_acum(p_capitol text)
returns jsonb
language sql security definer stable set search_path = public as $$
  select coalesce(
    (select jsonb_build_object('viu', true, 'sedinta', s.id, 'mod', s.mod,
                               'slide_nr', s.slide_nr, 'titlu', s.titlu)
       from public.sedinte s
      where s.capitol = p_capitol and s.inchisa_la is null
        and s.deschisa_la > now() - interval '3 hours'
      order by s.deschisa_la desc limit 1),
    jsonb_build_object('viu', false));
$$;

-- Opțional, dacă ai pg_cron pornit în Supabase (Database > Extensions):
-- select cron.schedule('dsw-ore-uitate', '*/15 * * * *',
--                      $$select public.inchide_orele_uitate()$$);
