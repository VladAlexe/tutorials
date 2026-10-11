-- ===========================================================================
-- 12. CONTUL MEU DE PROFESOR
--
-- Un singur profesor: eu. Dreptul nu se cere din site, pentru că atunci l-ar
-- putea cere oricine. Se dă o dată, de aici, din SQL Editor.
--
-- Nu trebuie să modifici nimic în fișierul ăsta. Rulezi interogările pe rând,
-- de sus în jos, și te uiți ce scrie după fiecare.
-- ===========================================================================


-- ---------------------------------------------------------------------------
-- PASUL 1. Intră o dată pe site cu contul de GitHub pe care îl vrei profesor.
--          Dacă pagina îți cere numărul matricol, NU i-l da: închide-o și
--          vino aici. (Un cont cu matricol e un cont de student.)
-- ---------------------------------------------------------------------------


-- ---------------------------------------------------------------------------
-- PASUL 2. Fă-mă profesor. Rulează interogarea asta aşa cum e.
--
--          Caută contul după adresa de email cu care ai intrat, sau după
--          numele de utilizator GitHub. Dacă ai intrat cu altă adresă, nu
--          strică nimic: pur şi simplu nu va găsi nimic, şi treci la pasul 3.
-- ---------------------------------------------------------------------------

insert into public.profesori (user_id)
select u.id
  from auth.users u
 where u.email is not null
   and (lower(u.email) in ('alexe.vld@gmail.com')
        or lower(u.raw_user_meta_data->>'user_name') in ('vladalexe'))
on conflict (user_id) do nothing;


-- ---------------------------------------------------------------------------
-- PASUL 3. Verifică cine e profesor acum.
--
--          Dacă aici apare contul tău, eşti gata: ieşi şi intri din nou pe
--          site şi ajungi la „Lecţiile mele". Dacă tabelul e gol, treci la
--          pasul 4.
-- ---------------------------------------------------------------------------

select u.email,
       u.raw_user_meta_data->>'user_name' as github,
       pf.adaugat_la
  from public.profesori pf
  join auth.users u on u.id = pf.user_id
 order by pf.adaugat_la;


-- ---------------------------------------------------------------------------
-- PASUL 4. Numai dacă pasul 3 a ieşit gol.
--
--          Face profesor ultimul cont adevărat care a intrat pe site, adică
--          al tău, dacă tocmai ai intrat la pasul 1. Conturile de invitat
--          sunt sărite.
--
--          Rulează, apoi rulează din nou pasul 3 ca să confirmi.
-- ---------------------------------------------------------------------------

insert into public.profesori (user_id)
select u.id
  from auth.users u
 where u.email is not null          -- conturile de invitat n-au email
   and not exists (select 1 from public.profesori)   -- numai dacă nu e deja cineva
 order by u.created_at desc
 limit 1
on conflict (user_id) do nothing;


-- ---------------------------------------------------------------------------
-- DACĂ AI FĂCUT PROFESOR CONTUL GREȘIT
--
-- Interogarea asta lasă profesor doar contul tău de GitHub şi scoate orice
-- altceva a intrat din greşeală. Rulează, apoi pasul 3.
-- ---------------------------------------------------------------------------

-- delete from public.profesori pf
--  using auth.users u
--  where u.id = pf.user_id
--    and lower(u.raw_user_meta_data->>'user_name') is distinct from 'vladalexe';
--
-- (Rândurile de mai sus încep cu „--", adică sunt oprite. Ca să le foloseşti,
--  le selectezi cu mouse-ul, ştergi cele două liniuţe de la începutul fiecărui
--  rând, şi apeşi Run. Am lăsat-o oprită înadins: e singura din fişier care
--  şterge ceva.)


-- ---------------------------------------------------------------------------
-- CONTUL DE TEST
--
-- Nu-l face profesor niciodată. Rostul lui e să-ţi arate ce vede un student.
-- Conturile de invitat se curăţă singure:
-- ---------------------------------------------------------------------------

select public.sterge_invitatii(24);   -- şterge invitaţii mai vechi de 24 de ore
