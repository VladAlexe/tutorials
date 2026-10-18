-- ===========================================================================
-- 19. VITEZA, PENTRU O SALĂ PLINĂ
--
-- Se rulează o dată, în Supabase (SQL Editor), după 18.
--
-- Panoul profesorului cere, la fiecare câteva secunde, starea sălii
-- (panou_slide). Până acum, pentru „cine mai e pe pagină”, funcția citea
-- întreg tabelul de sesiuni al semestrului, care crește cu fiecare vizită.
-- Cu 30 de studenți și câteva săptămâni de curs, asta devine partea lentă.
-- Acum se uită doar la oamenii din sala de azi și doar la ultimele minute.
--
-- Plus două indexuri pentru întrebările care se pun cel mai des.
-- ===========================================================================

drop function if exists public.panou_slide(uuid, text[]);

create function public.panou_slide(
  p_sedinta  uuid,
  p_sarcini  text[] default '{}'
)
returns table (
  matricol   text,
  nume       text,
  stare      text,     -- trecut | trimis_gresit | trimis_gol | nefacut
  ales       int,      -- indicele variantei alese, pentru verificări
  ales_la    text,     -- LA CARE întrebare; fără asta, indicele minte
  cand       timestamptz,
  facute     int,      -- sarcini trecute în toată ședința
  trimise    int,      -- sarcini atinse în toată ședința
  vazut_la   timestamptz
)
language sql security definer stable set search_path = public as $$
  with s as (
    select * from public.sedinte where id = p_sedinta
  ),
  inscrisi as (
    select st.matricol, st.nume, p.user_id
      from public.studenti st
      left join public.profiluri p on p.matricol = st.matricol
     where st.grupa_id is not distinct from (select grupa_id from s)
       and coalesce(st.invitat, false) = false
  ),
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
  -- ce a ales, și la ce. `intrebare_id` e singura adăugire din fișierul ăsta.
  alegerea as (
    select distinct on (r.user_id) r.user_id, r.raspuns, r.intrebare_id
      from public.raspunsuri r
     where r.sedinta_id = p_sedinta
       and r.intrebare_id = any(p_sarcini)
     order by r.user_id, r.creat_la desc
  ),
  toata_ora as (
    select i.user_id,
           count(distinct i.sarcina_id) filter (where i.corect) as facute,
           count(distinct i.sarcina_id)                          as trimise
      from public.incercari i
     where i.sedinta_id = p_sedinta
     group by i.user_id
  ),
  vii as (
    -- doar oamenii din sala asta și doar ultimele minute: altfel tabelul de
    -- sesiuni, care crește tot semestrul, se citea întreg la fiecare 4 secunde
    select se.user_id, max(se.vazut_la) as vazut_la
      from public.sesiuni se
     where se.user_id in (select user_id from oameni where user_id is not null)
       and se.vazut_la > now() - interval '30 minutes'
     group by se.user_id
  )
  select o.matricol, o.nume,
         case when p.vreun_corect       then 'trecut'
              when p.vreo_completare    then 'trimis_gresit'
              when p.cate is not null   then 'trimis_gol'
              else                           'nefacut' end,
         a.raspuns,
         a.intrebare_id,
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

grant execute on function public.panou_slide(uuid, text[]) to authenticated;

create index if not exists sesiuni_user_vazut_idx on public.sesiuni (user_id, vazut_la desc);
create index if not exists sedinte_deschise_idx  on public.sedinte (capitol) where inchisa_la is null;
create index if not exists raspunsuri_sedinta_idx on public.raspunsuri (sedinta_id, intrebare_id);
create index if not exists rulari_sedinta_idx     on public.rulari_cod (sedinta_id, exercitiu_id);
