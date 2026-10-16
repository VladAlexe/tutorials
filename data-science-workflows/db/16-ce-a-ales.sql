-- ===========================================================================
-- 16. CE A ALES, LA CARE ÎNTREBARE
--
-- Un fișier mic, cu o singură reparație.
--
-- Pe un slide cu DOUĂ verificări, panoul arăta un rând imposibil: „a ales
-- meniul" și „greșit", în același timp, când meniul e tocmai răspunsul bun.
-- (Cursul 2, slide 4, care are c2-v2 și c2-v3.)
--
-- Cauza: `panou_slide` întorcea indicele ultimului răspuns de pe slide, fără
-- să spună LA CARE întrebare, iar panoul citea eticheta din variantele primei
-- întrebări. Studentul răspunsese la a doua, indicele 2, iar panoul îl căuta
-- în lista primei, unde 2 înseamnă „meniul".
--
-- Reparația e o coloană: `ales_la`, id-ul întrebării. Panoul caută varianta în
-- întrebarea aceea, nu în prima de pe slide.
--
-- Nimic altceva nu se schimbă. Se poate rula oricând, și situl merge și fără
-- ea: dacă `ales_la` lipsește, panoul scrie verdictul (corect / greșit), care
-- e întotdeauna adevărat, și arată eticheta doar când slide-ul are o singură
-- întrebare, unde confuzia nu e posibilă.
-- ===========================================================================

-- Întâi drop: Postgres refuză `create or replace` când se schimbă lista de
-- coloane întoarse („cannot change return type of existing function").
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
    select se.user_id, max(se.vazut_la) as vazut_la
      from public.sesiuni se group by se.user_id
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

revoke all on function public.panou_slide(uuid, text[]) from public;
grant execute on function public.panou_slide(uuid, text[]) to authenticated;
