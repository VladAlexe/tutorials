-- ===========================================================================
-- 29. Prezența se scrie imediat, nu la închiderea orei
--
-- Se rulează o dată, în Supabase (SQL Editor), după 28. E sigur de rulat din
-- nou.
--
-- Până acum, prezența se calcula doar când ora se închidea (de mână, sau
-- automat la pornirea orei următoare). O oră uitată deschisă lăsa toată grupa
-- fără prezență până la reparație, ca la C2 și C3.
--
-- Acum, primul răspuns dat într-o oră (o verificare sau un exercițiu, cu
-- sedinta_id) scrie pe loc prezența la acea oră. Regula rămâne aceeași: e
-- prezent cine a răspuns la oră. Nu e nevoie de cron și nici de închiderea
-- orei; închiderea rămâne doar pentru cod și pentru durata orei.
--
-- Orele arhivate (de test) nu dau prezență: catalogul și contul le ignoră
-- oricum, iar aici nici nu se mai scriu.
-- ===========================================================================

create or replace function public.prezenta_din_raspuns()
returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if new.sedinta_id is not null then
    insert into public.prezente (user_id, curs, sedinta_id, marcat_la)
    select new.user_id, s.capitol, s.id, coalesce(new.creat_la, now())
      from public.sedinte s
     where s.id = new.sedinta_id
       and s.arhivata_la is null
    on conflict do nothing;
  end if;
  return new;
end $$;

drop trigger if exists prezenta_din_raspuns on public.raspunsuri;
create trigger prezenta_din_raspuns
  after insert or update of sedinta_id on public.raspunsuri
  for each row execute function public.prezenta_din_raspuns();

drop trigger if exists prezenta_din_cod on public.rulari_cod;
create trigger prezenta_din_cod
  after insert or update of sedinta_id on public.rulari_cod
  for each row execute function public.prezenta_din_raspuns();

-- prezențele care lipsesc deja, pentru orele deschise sau închise, nearhivate
insert into public.prezente (user_id, curs, sedinta_id, marcat_la)
select i.user_id, s.capitol, s.id, min(i.creat_la)
  from public.sedinte s
  join public.incercari i on i.sedinta_id = s.id
 where s.arhivata_la is null
 group by i.user_id, s.capitol, s.id
on conflict do nothing;

-- Verificare: pe fiecare oră, câți au răspuns și câți sunt prezenți (trebuie egale)
select s.capitol, s.titlu, s.deschisa_la::date as ziua, s.inchisa_la is null as inca_deschisa,
       (select count(distinct i.user_id) from public.incercari i where i.sedinta_id = s.id) as au_raspuns,
       (select count(*) from public.prezente z where z.sedinta_id = s.id)                   as prezenti
  from public.sedinte s
 where s.arhivata_la is null
 order by s.deschisa_la;
