-- ===========================================================================
-- 10. CONTUL DE PROFESOR, SEPARAT DE CEL DE STUDENT
--
-- Dreptul de profesor stă într-un singur loc: un rând în `profesori`, legat de
-- un cont. Nu e un rol pe care-l poate cere cineva; se dă din altă parte.
--
-- Fișierul ăsta adaugă doar atât: un profesor poate face profesor un alt cont,
-- după adresa de email cu care acel cont a intrat. Așa pot avea un cont numai
-- pentru predat, fără număr matricol și fără progres de student, și pot să-mi
-- încerc site-ul cu un cont obișnuit fără să-mi pierd drepturile.
--
-- Nu se poate scoate ultimul profesor: altfel panoul rămâne fără stăpân și
-- singura cale înapoi e prin Supabase.
--
-- Se rulează o singură dată, după 09. Se poate rula din nou fără stricăciuni.
-- ===========================================================================

-- ---------------------------------------------------------- cine e profesor
create or replace function public.profesorii()
returns table (user_id uuid, email text, de_cand timestamptz, sunt_eu boolean)
language sql security definer stable set search_path = public as $$
  select pf.user_id, u.email::text, pf.adaugat_la, (pf.user_id = auth.uid())
    from public.profesori pf
    join auth.users u on u.id = pf.user_id
   where public.sunt_profesor()
   order by pf.adaugat_la;
$$;

-- ------------------------------------------------------ dă dreptul altcuiva
-- Contul trebuie să fi intrat măcar o dată pe site: altfel nu există încă în
-- auth.users și n-am ce lega.

create or replace function public.fa_profesor(p_email text)
returns jsonb
language plpgsql security definer set search_path = public as $$
declare v_user uuid; v_email text;
begin
  if not public.sunt_profesor() then
    return jsonb_build_object('ok', false, 'mesaj', 'Numai un profesor poate face asta.');
  end if;

  v_email := lower(btrim(coalesce(p_email, '')));
  if v_email = '' then
    return jsonb_build_object('ok', false, 'mesaj', 'Scrie adresa de email a contului.');
  end if;

  select id, email::text into v_user, v_email
    from auth.users where lower(email) = v_email limit 1;

  if v_user is null then
    return jsonb_build_object('ok', false, 'mesaj',
      'Nu există niciun cont cu adresa asta. Intră o dată cu el pe site, apoi revino.');
  end if;

  insert into public.profesori (user_id) values (v_user)
  on conflict (user_id) do nothing;

  return jsonb_build_object('ok', true, 'email', v_email,
                            'mesaj', 'Contul ' || v_email || ' e acum profesor.');
end $$;

-- ------------------------------------------------------------ ia dreptul
create or replace function public.scoate_profesor(p_email text)
returns jsonb
language plpgsql security definer set search_path = public as $$
declare v_user uuid; v_cati int;
begin
  if not public.sunt_profesor() then
    return jsonb_build_object('ok', false, 'mesaj', 'Numai un profesor poate face asta.');
  end if;

  select id into v_user from auth.users
   where lower(email) = lower(btrim(coalesce(p_email, ''))) limit 1;
  if v_user is null then
    return jsonb_build_object('ok', false, 'mesaj', 'Nu există cont cu adresa asta.');
  end if;

  select count(*) into v_cati from public.profesori;
  if v_cati <= 1 then
    return jsonb_build_object('ok', false, 'mesaj',
      'E ultimul profesor. Dacă îl scoți, panoul rămâne fără nimeni.');
  end if;

  delete from public.profesori where user_id = v_user;
  return jsonb_build_object('ok', true, 'mesaj', 'Gata, contul nu mai e profesor.');
end $$;

grant execute on function public.profesorii()           to authenticated;
grant execute on function public.fa_profesor(text)      to authenticated;
grant execute on function public.scoate_profesor(text)  to authenticated;
