-- ===========================================================================
-- 07. PREZENȚA PRIN CODUL QR
--
-- Tabelele există din 01-schema.sql (prezente, jetoane_prezenta) și funcția
-- marcheaza_prezenta() la fel. Lipseau două lucruri: o cale prin care
-- profesorul să facă un jeton, și una prin care să vadă cine a scanat.
--
-- Se rulează o singură dată, după 06. Se poate rula din nou fără stricăciuni.
-- ===========================================================================

-- --------------------------------------------------- jetonul de la oră ----
-- Scurt, ca să încapă lizibil într-un cod QR, și cu viață scurtă, ca să nu
-- poată fi trimis pe grup de cineva care a plecat acasă.

create or replace function public.creeaza_jeton(
  p_curs   text,
  p_minute int default 90
) returns jsonb
language plpgsql security definer set search_path = public as $$
declare
  v_jeton text;
  v_expira timestamptz;
begin
  if not public.sunt_profesor() then
    return jsonb_build_object('ok', false, 'mesaj', 'Numai profesorul poate face asta.');
  end if;

  -- dacă există deja unul valabil pentru cursul ăsta, îl dăm pe acela:
  -- altfel, la fiecare reîncărcare a panoului s-ar schimba codul de pe ecran
  select jeton, expira_la into v_jeton, v_expira
    from public.jetoane_prezenta
   where curs = p_curs and expira_la > now() + interval '2 minutes'
   order by expira_la desc limit 1;

  if v_jeton is not null then
    return jsonb_build_object('ok', true, 'jeton', v_jeton,
                              'expira_la', v_expira, 'nou', false);
  end if;

  -- șase caractere, fără cele care se confundă între ele la citit: 0/O, 1/I/L
  v_jeton := '';
  while length(v_jeton) < 6 loop
    v_jeton := v_jeton || substr('ABCDEFGHJKMNPQRSTUVWXYZ23456789',
                                 1 + floor(random() * 31)::int, 1);
  end loop;
  v_expira := now() + make_interval(mins => greatest(p_minute, 5));

  insert into public.jetoane_prezenta (jeton, curs, expira_la)
  values (v_jeton, p_curs, v_expira);

  return jsonb_build_object('ok', true, 'jeton', v_jeton,
                            'expira_la', v_expira, 'nou', true);
end $$;

-- ------------------------------------------------------- cine e prezent ---

create or replace function public.sumar_prezenta(p_curs text)
returns table (matricol text, nume text, grupa text, invitat boolean,
               marcat_la timestamptz)
language sql security definer stable set search_path = public as $$
  select coalesce(p.matricol, '—'),
         coalesce(s.nume, 'fără cont legat'),
         s.grupa,
         coalesce(s.invitat, false),
         z.marcat_la
    from public.prezente z
    left join public.profiluri p on p.user_id = z.user_id
    left join public.studenti  s on s.matricol = p.matricol
   where public.sunt_profesor() and z.curs = p_curs
   order by z.marcat_la;
$$;

-- Ștergerea prezenței unui student, dacă a scanat din greșeală alt curs.
create or replace function public.sterge_prezenta(p_matricol text, p_curs text)
returns jsonb
language plpgsql security definer set search_path = public as $$
declare v_user uuid; v int;
begin
  if not public.sunt_profesor() then
    return jsonb_build_object('ok', false, 'mesaj', 'Numai profesorul poate face asta.');
  end if;
  select user_id into v_user from public.profiluri where matricol = p_matricol;
  if v_user is null then
    return jsonb_build_object('ok', false, 'mesaj', 'Matricolul nu are cont legat.');
  end if;
  delete from public.prezente where user_id = v_user and curs = p_curs;
  get diagnostics v = row_count;
  return jsonb_build_object('ok', true, 'sterse', v);
end $$;
