-- ============================================================================
--  25. Numele din listă, la prima intrare cu GitHub, oriunde pe sit
--
--  Până acum numele se alegea doar din pagina de intrare la oră, cu codul
--  ședinței, și doar în primele 3 ore de la deschiderea ei. Cine intra cu
--  GitHub altfel (din antet, de acasă, după ce ora se închisese) rămânea cu un
--  cont nelegat de niciun nume, iar răspunsurile lui nu se salvau.
--
--  Acum alegerea nu mai ține de oră: la prima intrare cu GitHub, oricare ar fi
--  pagina, studentul își caută numele și îl alege. O singură dată.
--
--  Lista nu se trimite întreagă: numele apar doar după ce studentul scrie cel
--  puțin trei litere din numele lui, cel mult 10 rezultate. Altfel oricine își
--  face un cont GitHub ar vedea numele tuturor studenților.
--
--  Rulează-l întreg, după 24. E sigur de rulat de mai multe ori.
-- ============================================================================

-- 1. Litere fără diacritice: „Creţu” (cu sedilă), „Crețu” și „cretu” sunt la fel
create or replace function public.fara_diacritice(t text)
returns text
language sql immutable set search_path = public as $$
  select translate(lower(coalesce(t, '')),
                   'ăâîșşțţáàäéèëíïóöőúüű',
                   'aaisstt' || 'aaa' || 'eee' || 'ii' || 'ooo' || 'uuu');
$$;

-- 2. Căutarea numelui ------------------------------------------------------------
--    Doar pentru un cont GitHub încă nelegat. Fiecare cuvânt scris trebuie să
--    apară în nume, în orice ordine: „sebastian cretu” găsește „Creţu Sebastian”.
create or replace function public.cauta_numele(p_text text)
returns table (cheie text, nume text, grupa text)
language plpgsql security definer stable set search_path = public as $$
declare
  v_cuv text[];
begin
  if not public.e_cont_github() then return; end if;
  if exists (select 1 from public.profiluri p where p.user_id = auth.uid()) then return; end if;

  v_cuv := array_remove(regexp_split_to_array(public.fara_diacritice(btrim(coalesce(p_text, ''))), '[\s-]+'), '');
  if length(array_to_string(v_cuv, '')) < 3 then return; end if;

  return query
    select st.cheie::text, st.nume,
           coalesce((select g.nume from public.grupe g where g.id = st.grupa_id), st.grupa)
      from public.studenti st
     where coalesce(st.invitat, false) = false
       and coalesce((select g.activa from public.grupe g where g.id = st.grupa_id), true)
       and not exists (select 1 from public.profiluri p where p.matricol = st.matricol)
       and (select bool_and(strpos(public.fara_diacritice(st.nume), c) > 0) from unnest(v_cuv) c)
     order by st.nume
     limit 10;
end $$;

-- 3. Alegerea numelui ------------------------------------------------------------
create or replace function public.alege_numele(p_cheie text)
returns jsonb
language plpgsql security definer set search_path = public as $$
declare
  v_user uuid := auth.uid();
  v_mat  text;
  v_nume text;
begin
  if not public.e_cont_github() then
    return jsonb_build_object('ok', false,
      'mesaj', 'Numele din listă se alege doar cu un cont GitHub.');
  end if;

  if exists (select 1 from public.profiluri where user_id = v_user) then
    return jsonb_build_object('ok', false,
      'mesaj', 'Contul tău este deja asociat unui nume. Dacă nu este numele tău, spune-i profesorului.');
  end if;

  select st.matricol, st.nume into v_mat, v_nume
    from public.studenti st
   where coalesce(st.invitat, false) = false
     and st.cheie::text = p_cheie;
  if v_mat is null then
    return jsonb_build_object('ok', false, 'mesaj', 'Numele nu a fost găsit în listă.');
  end if;

  if exists (select 1 from public.profiluri where matricol = v_mat) then
    return jsonb_build_object('ok', false,
      'mesaj', 'Numele acesta a fost deja ales de alt cont. Spune-i profesorului.');
  end if;

  begin
    insert into public.profiluri (user_id, matricol, github_login)
    values (v_user, v_mat,
            (select raw_user_meta_data ->> 'user_name' from auth.users where id = v_user));
  exception when unique_violation then
    -- două conturi au apăsat același nume în aceeași secundă
    return jsonb_build_object('ok', false,
      'mesaj', 'Numele acesta a fost deja ales de alt cont. Spune-i profesorului.');
  end;

  insert into public.evenimente (user_id, tip, detalii)
  values (v_user, 'alegere_nume', '{}'::jsonb);

  return jsonb_build_object('ok', true, 'nume', v_nume);
end $$;

revoke execute on function public.cauta_numele(text) from public, anon;
revoke execute on function public.alege_numele(text) from public, anon;
grant  execute on function public.cauta_numele(text) to authenticated;
grant  execute on function public.alege_numele(text) to authenticated;
