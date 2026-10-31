# 26. Repo-urile echipelor pe GitHub, dintr-un buton

Butonul **Sincronizează GitHub** din **Predau → Echipele** face, pentru grupa aleasă:

- câte un repo privat `echipa-N` în organizația `dsw-ubb-2026`, din șablonul `proiect-template`;
- invitație (drept de scriere) pentru fiecare membru cu cont GitHub legat pe site;
- scoate accesul celor care nu mai sunt în echipă.

Se apasă după ce se formează echipele și ori de câte ori intră sau iese cineva. Ce e deja făcut nu se refaci.

Butonul cheamă o funcție de pe serverul Supabase (Edge Function). Tokenul GitHub stă doar acolo, ca secret: nu apare în cod, în repo sau în pagină.

## Instalare, o singură dată

### 1. Tokenul GitHub

1. GitHub → poza ta → **Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token**.
2. **Resource owner:** `dsw-ubb-2026`. **Expiration:** până după sfârșitul semestrului.
3. **Repository access:** All repositories.
4. **Permissions → Repository permissions:** `Administration` = Read and write, `Contents` = Read-only (`Metadata` se pune singur).
5. **Generate token** și copiază-l (se vede o singură dată).

Dacă organizația cere aprobarea tokenurilor, aprob-o din **dsw-ubb-2026 → Settings → Personal access tokens → Pending requests**.

### 2. Funcția în Supabase

1. Supabase, proiectul `dsw-2026` → **Edge Functions → Deploy a new function → Via Editor**.
2. Nume: `sincronizeaza-github` (exact așa).
3. Înlocuiește tot codul din editor cu `db/functii/sincronizeaza-github/index.ts` și apasă **Deploy**.
4. Lasă **Verify JWT** pornit.

### 3. Secretul

**Edge Functions → Secrets → Add new secret**: nume `GITHUB_TOKEN`, valoare tokenul de la pasul 1. Salvează.

`SUPABASE_URL` și `SUPABASE_ANON_KEY` le pune Supabase singur.

## Verificare

În **Predau → Echipele** apasă **Sincronizează GitHub**. Sub butoane apare, pe echipe: repo creat, cine a primit invitație, cine a fost scos, cine nu are cont GitHub legat. Pe GitHub, în `dsw-ubb-2026`, apar repo-urile `echipa-N`.

Studenții primesc invitația pe email și în notificările GitHub și trebuie să o accepte (expiră după 7 zile; dacă expiră, butonul o retrimite).

## Ce nu face

- Nu șterge repo-uri: o echipă rămasă goală își păstrează repo-ul.
- Nu atinge pe nimeni cu rol de admin (tu, ca owner al organizației).
- Repo-urile se numesc după numărul echipei; dacă vei avea mai multe grupe în aceeași organizație, numele trebuie diferențiate pe grupe.
