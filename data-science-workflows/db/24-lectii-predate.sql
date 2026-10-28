-- ===========================================================================
-- 24. LECȚIILE PREDATE, VĂZUTE ȘI FĂRĂ CONT
--
-- Se rulează o dată, în Supabase (SQL Editor), după 23. E sigur de rulat din
-- nou.
--
-- Ce face: o lecție apare pe site (prima pagină, pagina cursului, slide-urile
-- și manualul) doar după ce a fost pornită o oră a ei. Studenții autentificați
-- citeau deja lista orelor; fără cont, tabelul `sedinte` nu se poate citi, deci
-- pagina nu putea ști ce s-a predat. Funcția de mai jos întoarce DOAR codurile
-- lecțiilor predate (c1, c2, ...), nimic altceva: nici grupa, nici codul orei,
-- nici datele.
--
-- O oră de test se arhivează din Predau, la Ședințele: lecția ei nu mai
-- apare ca predată.
-- ===========================================================================

create or replace function public.lectii_predate()
returns table (capitol text)
language sql security definer stable set search_path = public as $$
  select distinct s.capitol from public.sedinte s where s.arhivata_la is null;
$$;

revoke all on function public.lectii_predate() from public;
grant execute on function public.lectii_predate() to anon, authenticated;
