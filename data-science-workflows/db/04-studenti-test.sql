-- ============================================================================
--  04. Studenti ficitivi, pentru testare
--
--  Matricolele incep cu 9, ca sa se poata sterge toate deodata cand vine
--  lista reala:
--
--      delete from public.studenti where matricol like '9%';
--
--  Stergerea unui student sterge in cascada si profilul legat de el, deci
--  conturile de test se desprind singure.
-- ============================================================================

insert into public.studenti (matricol, nume, an, grupa) values
  ('900001', 'Andreea Pavel',        1, 'A'),
  ('900002', 'Mihai Costache',       1, 'A'),
  ('900003', 'Ioana Barbu',          1, 'A'),
  ('900004', 'Radu Nistor',          1, 'A'),
  ('900005', 'Elena Dragomir',       1, 'A'),
  ('900006', 'Tudor Apostol',        1, 'A'),
  ('900007', 'Carmen Lupu',          1, 'A'),
  ('900008', 'Alexandru Teodorescu', 1, 'A'),
  ('900009', 'Diana Oprea',          1, 'A'),
  ('900010', 'Vlad Munteanu',        1, 'A'),
  ('900011', 'Raluca Stanciu',       1, 'A'),
  ('900012', 'Cristian Baciu',       1, 'A'),
  ('900013', 'Simona Ardelean',      1, 'B'),
  ('900014', 'George Petrescu',      1, 'B'),
  ('900015', 'Bianca Olaru',         1, 'B'),
  ('900016', 'Stefan Vasilescu',     1, 'B'),
  ('900017', 'Alina Chirila',        1, 'B'),
  ('900018', 'Bogdan Serban',        1, 'B'),
  ('900019', 'Larisa Toma',          1, 'B'),
  ('900020', 'Paul Iordache',        1, 'B'),
  ('900021', 'Monica Grigore',       1, 'B'),
  ('900022', 'Victor Alexandrescu',  1, 'B'),
  ('900023', 'Daria Sandu',          1, 'B'),
  ('900024', 'Emil Ciobanu',         1, 'B'),
  ('900099', 'Cont de test',         1, 'A')
on conflict (matricol) do nothing;

-- ----------------------------------------------------------------------------
--  900099 e contul tau de test.
--
--  Dupa ce te faci profesor, revendici matricolul acesta cu acelasi cont de
--  GitHub. Vei fi si profesor, si student: vezi panoul cu toata grupa, dar si
--  pagina personala a unui student, cu propriile tale raspunsuri. Util cand
--  verifici cum arata lucrurile din partea lor.
--
--  Cand vine lista reala, se sterge odata cu restul: toate incep cu 9.
-- ----------------------------------------------------------------------------

-- verificare
select grupa, count(*) as studenti
from public.studenti
where matricol like '9%'
group by grupa
order by grupa;
