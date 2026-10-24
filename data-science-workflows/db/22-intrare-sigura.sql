-- ============================================================================
--  22. Intrare sigură: numele din listă, legat de GitHub
--
--  Studentul nu-și vede și nu-și scrie niciodată numărul matricol. La prima
--  oră scanează codul, intră cu GitHub și își apasă numele din lista grupei.
--  De atunci contul lui GitHub e legat de rândul lui din listă.
--
--  Ce repară fișierul ăsta:
--    1. Lista trimitea spre browser sha256(matricol || 'dsw'). Matricolele au
--       șase cifre, deci amprenta se putea sparge în câteva secunde: oricine
--       avea codul orei afla matricolele colegilor. Acum fiecare student are
--       o cheie aleatoare, care nu spune nimic despre matricol.
--    2. Un cont anonim (invitat) putea să-și aleagă numele cuiva din listă.
--       Acum alegerea cere un cont GitHub.
--    3. Un cont deja legat de un nume putea fi mutat pe alt nume. Acum nu.
--    4. Un student putea să-și modifice direct rândul din `profiluri`,
--       inclusiv matricolul. Acum scrierea se face doar prin funcții.
--    5. revendica_matricol() spunea „nu există” sau „e luat”, deci putea fi
--       folosită ca să ghicești matricole. Nu se mai poate apela.
--    6. Numele deja alese nu mai apar în listă deloc.
--    7. Profesorul vede contul GitHub legat și poate dezlega o alegere greșită.
--
--  Rulează-l întreg, după 21. E sigur de rulat de mai multe ori.
-- ============================================================================

-- 1. Cheia aleatoare a fiecărui student ---------------------------------------
alter table public.studenti
  add column if not exists cheie uuid not null default gen_random_uuid();
create unique index if not exists studenti_cheie_idx on public.studenti (cheie);

-- 2. Cine poate alege un nume: un cont adevărat, nu unul anonim ---------------
create or replace function public.e_cont_github()
returns boolean
language sql stable set search_path = public as $$
  select auth.uid() is not null
     and coalesce((auth.jwt() ->> 'is_anonymous')::boolean, false) = false;
$$;

-- 3. Lista grupei: doar numele încă nealese, cu cheia aleatoare ----------------
--    Aceeași formă ca înainte (cheie, nume, luat), ca pagina să nu se strice.
create or replace function public.lista_grupei(p_cod text)
returns table (cheie text, nume text, luat boolean)
language sql security definer stable set search_path = public as $$
  with s as (
    select * from public.sedinte
     where upper(btrim(cod)) = upper(btrim(p_cod))
       and inchisa_la is null
       and deschisa_la > now() - interval '3 hours'
     limit 1
  )
  select st.cheie::text, st.nume, false
    from public.studenti st
   where public.e_cont_github()
     and exists (select 1 from s)
     and st.grupa_id is not distinct from (select grupa_id from s)
     and coalesce(st.invitat, false) = false
     and not exists (select 1 from public.profiluri p where p.matricol = st.matricol)
   order by st.nume;
$$;

-- 4. Intrarea cu numele ales -------------------------------------------------
create or replace function public.intra_in_sedinta(p_cod text, p_cheie text)
returns jsonb
language plpgsql security definer set search_path = public as $$
declare
  v_user  uuid := auth.uid();
  v_sed   public.sedinte;
  v_mat   text;
  v_nume  text;
  v_alt   uuid;
  v_deja  text;
begin
  if v_user is null then
    return jsonb_build_object('ok', false, 'mesaj', 'Nu ești autentificat.');
  end if;
  if not public.e_cont_github() then
    return jsonb_build_object('ok', false,
      'mesaj', 'Ca să-ți alegi numele din listă, intră cu GitHub.');
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
     and coalesce(st.invitat, false) = false
     and st.cheie::text = p_cheie;
  if v_mat is null then
    return jsonb_build_object('ok', false, 'mesaj', 'Nu te găsesc în lista grupei.');
  end if;

  -- contul ăsta e deja legat de un nume?
  select matricol into v_deja from public.profiluri where user_id = v_user;
  if v_deja is not null and v_deja <> v_mat then
    return jsonb_build_object('ok', false,
      'mesaj', 'Contul tău GitHub e deja legat de alt nume. Spune-i profesorului.');
  end if;

  -- numele ăsta e deja ales de alt cont?
  select user_id into v_alt from public.profiluri where matricol = v_mat;
  if v_alt is not null and v_alt <> v_user then
    return jsonb_build_object('ok', false,
      'mesaj', 'Cineva a ales deja numele ăsta. Spune-i profesorului.');
  end if;

  if v_deja is null then
    insert into public.profiluri (user_id, matricol, github_login)
    values (v_user, v_mat,
            (select raw_user_meta_data ->> 'user_name' from auth.users where id = v_user));
  end if;

  insert into public.evenimente (user_id, tip, capitol, sedinta_id, detalii)
  values (v_user, 'intrare_sedinta', v_sed.capitol, v_sed.id, '{}'::jsonb);

  return jsonb_build_object('ok', true, 'nume', v_nume,
                            'sedinta', v_sed.id, 'capitol', v_sed.capitol,
                            'titlu', v_sed.titlu, 'mod', v_sed.mod,
                            'slide_nr', v_sed.slide_nr);
end $$;

-- 5. Profilul se scrie doar prin funcții -------------------------------------
drop policy if exists profiluri_github on public.profiluri;
revoke insert, update, delete on public.profiluri from anon, authenticated;

-- 6. Vechea revendicare după matricol nu se mai poate apela -------------------
revoke execute on function public.revendica_matricol(text) from public, anon, authenticated;

-- 7. Profesorul: ce cont e legat de un student, și dezlegarea ----------------
create or replace function public.contul_studentului(p_matricol text)
returns jsonb
language sql security definer stable set search_path = public as $$
  select case when not public.sunt_profesor() then null else
    (select jsonb_build_object('github_login', p.github_login, 'legat_la', p.revendicat_la)
       from public.profiluri p where p.matricol = p_matricol)
  end;
$$;

create or replace function public.dezleaga_student(p_matricol text)
returns jsonb
language plpgsql security definer set search_path = public as $$
begin
  if not public.sunt_profesor() then
    return jsonb_build_object('ok', false, 'mesaj', 'Doar profesorul.');
  end if;
  delete from public.profiluri where matricol = p_matricol and matricol not like 'G-%';
  return jsonb_build_object('ok', true);
end $$;

grant execute on function public.e_cont_github()               to authenticated;
grant execute on function public.lista_grupei(text)            to authenticated;
grant execute on function public.intra_in_sedinta(text, text)  to authenticated;
grant execute on function public.contul_studentului(text)      to authenticated;
grant execute on function public.dezleaga_student(text)        to authenticated;

-- ----------------------------------------------------------------------------
--  La sfârșitul anului (după contestații), ștergerea datelor cursului.
--  NU rula acum. Notele oficiale rămân în catalogul facultății, nu aici.
--
--  delete from public.incercari;   delete from public.raspunsuri;
--  delete from public.rulari_cod;  delete from public.progres;
--  delete from public.evenimente;  delete from public.prezente;
--  delete from public.observatii;  delete from public.note_manuale;
--  delete from public.profiluri;   delete from public.studenti;
--  delete from auth.users where id not in (select user_id from public.profesori);
-- ----------------------------------------------------------------------------
