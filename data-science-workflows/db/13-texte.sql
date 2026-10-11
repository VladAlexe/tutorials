-- ===========================================================================
-- 13. CE AU SCRIS CU MÂNA LOR
--
-- La cursul 1 studenții scriu ce așteaptă de la curs. La cursul 3, întrebarea
-- de cercetare a echipei. Vor mai fi și altele. Toate ajung în jurnal, sub
-- tipuri diferite, iar `sumar_asteptari` știa doar de primul.
--
-- Funcția de aici le scoate pe toate, filtrabile după lecție și după tip, ca
-- panoul să nu aibă nevoie de o funcție nouă la fiecare text pe care îl cer.
--
-- Se rulează o singură dată, după 12. Se poate rula din nou fără stricăciuni.
-- ===========================================================================

create or replace function public.sumar_scrise(
  p_capitol text default null,
  p_tip     text default null
)
returns table (tip text, matricol text, nume text, grupa text,
               text text, capitol text, creat_la timestamptz)
language sql security definer stable set search_path = public as $$
  select e.tip,
         coalesce(p.matricol, '—'),
         coalesce(s.nume, 'fără cont legat'),
         s.grupa,
         e.detalii->>'text',
         e.capitol,
         e.creat_la
    from public.evenimente e
    left join public.profiluri p on p.user_id = e.user_id
    left join public.studenti  s on s.matricol = p.matricol
   where public.sunt_profesor()
     and coalesce(btrim(e.detalii->>'text'), '') <> ''
     and (p_capitol is null or e.capitol = p_capitol)
     and (p_tip is null or e.tip = p_tip)
     and not exists (select 1 from public.profesori f where f.user_id = e.user_id)
   order by e.tip, e.creat_la desc;
$$;

-- Ce feluri de texte există, ca panoul să-și poată face singur filele.
create or replace function public.feluri_scrise(p_capitol text default null)
returns table (tip text, cate int)
language sql security definer stable set search_path = public as $$
  select e.tip, count(*)::int
    from public.evenimente e
   where public.sunt_profesor()
     and coalesce(btrim(e.detalii->>'text'), '') <> ''
     and (p_capitol is null or e.capitol = p_capitol)
     and not exists (select 1 from public.profesori f where f.user_id = e.user_id)
   group by e.tip
   order by 2 desc;
$$;

grant execute on function public.sumar_scrise(text, text) to authenticated;
grant execute on function public.feluri_scrise(text)       to authenticated;
