// ===========================================================================
// Edge Function Supabase: sincronizeaza-github
//
// Butonul „Sincronizează GitHub” din Predau → Echipele o cheamă pentru o grupă.
// Pentru fiecare echipă cu membri:
//   1. creează repo-ul privat echipa-N în organizație, din șablon, dacă lipsește;
//   2. trimite invitație (drept de scriere) fiecărui membru cu cont GitHub legat;
//   3. scoate accesul celor care nu mai sunt în echipă (colaboratori și invitații).
// Se poate apăsa oricând: ce e deja făcut nu se refaci.
//
// Siguranță:
//   - tokenul GitHub stă doar în secretele Supabase (GITHUB_TOKEN), niciodată aici;
//   - lista echipelor se ia cu public.echipe_toate, cu jetonul celui care apasă,
//     deci funcția lucrează doar pentru profesor (sunt_profesor() în SQL);
//   - nu atinge pe nimeni cu rol de admin pe repo (profesorul).
// Instalare: db/26-sincronizare-github.md
// ===========================================================================

import { createClient } from "npm:@supabase/supabase-js@2";

const ORG = "dsw-ubb-2026";
const SABLON = "proiect-template";

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

const raspuns = (o: unknown) =>
  new Response(JSON.stringify(o), { headers: { ...CORS, "Content-Type": "application/json" } });

const pauza = (ms: number) => new Promise((r) => setTimeout(r, ms));

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: CORS });

  try {
    const TOKEN = Deno.env.get("GITHUB_TOKEN");
    if (!TOKEN) return raspuns({ ok: false, mesaj: "Lipsește secretul GITHUB_TOKEN în Supabase." });

    const gh = (cale: string, metoda = "GET", corp?: unknown) =>
      fetch(`https://api.github.com${cale}`, {
        method: metoda,
        headers: {
          Authorization: `Bearer ${TOKEN}`,
          Accept: "application/vnd.github+json",
          "X-GitHub-Api-Version": "2022-11-28",
          "User-Agent": "dsw-sincronizare",
        },
        body: corp ? JSON.stringify(corp) : undefined,
      });

    // echipele grupei, cerute cu jetonul profesorului
    const { grupa } = await req.json();
    const sb = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_ANON_KEY")!, {
      global: { headers: { Authorization: req.headers.get("Authorization") ?? "" } },
    });
    const { data: d, error } = await sb.rpc("echipe_toate", { p_grupa: grupa });
    if (error) return raspuns({ ok: false, mesaj: error.message });
    if (!d?.ok) return raspuns({ ok: false, mesaj: d?.mesaj || "Numai profesorul poate face asta." });

    const rezultat = [];
    for (const e of d.echipe) {
      if (!e.membri.length) continue;
      const repo = `echipa-${e.nr}`;
      const r = { repo, creat: false, invitati: [] as string[], scosi: [] as string[], fara_cont: [] as string[], eroare: "" };
      rezultat.push(r);

      // 1. repo-ul, din șablon, dacă nu există
      if ((await gh(`/repos/${ORG}/${repo}`)).status === 404) {
        const g = await gh(`/repos/${ORG}/${SABLON}/generate`, "POST", { owner: ORG, name: repo, private: true });
        if (!g.ok) { r.eroare = `repo-ul nu a putut fi creat (${g.status})`; continue; }
        r.creat = true;
        for (let i = 0; i < 10 && (await gh(`/repos/${ORG}/${repo}`)).status !== 200; i++) await pauza(1000);
      }

      // cine trebuie să aibă acces (conturile GitHub ale membrilor)
      const doriti = new Map<string, string>();
      for (const m of e.membri) {
        if (m.github) doriti.set(String(m.github).toLowerCase(), m.github);
        else r.fara_cont.push(m.nume);
      }

      // cine are acces acum: colaboratori direcți și invitații în așteptare
      const colab = await (await gh(`/repos/${ORG}/${repo}/collaborators?affiliation=direct&per_page=100`)).json();
      const invit = await (await gh(`/repos/${ORG}/${repo}/invitations?per_page=100`)).json();
      const auAcces = new Set<string>([
        ...(Array.isArray(colab) ? colab.map((c: any) => c.login.toLowerCase()) : []),
        ...(Array.isArray(invit) ? invit.map((i: any) => i.invitee?.login?.toLowerCase()).filter(Boolean) : []),
      ]);

      // 2. invitații pentru cei noi
      for (const [mic, login] of doriti) {
        if (auAcces.has(mic)) continue;
        const p = await gh(`/repos/${ORG}/${repo}/collaborators/${login}`, "PUT", { permission: "push" });
        if (p.ok) r.invitati.push(login);
        else r.eroare = `${login}: invitația nu a mers (${p.status})`;
      }

      // 3. accesul celor care nu mai sunt în echipă (fără admini)
      if (Array.isArray(colab)) for (const c of colab) {
        if (c.role_name === "admin" || doriti.has(c.login.toLowerCase())) continue;
        if ((await gh(`/repos/${ORG}/${repo}/collaborators/${c.login}`, "DELETE")).ok) r.scosi.push(c.login);
      }
      if (Array.isArray(invit)) for (const i of invit) {
        const login = i.invitee?.login;
        if (!login || doriti.has(login.toLowerCase())) continue;
        if ((await gh(`/repos/${ORG}/${repo}/invitations/${i.id}`, "DELETE")).ok) r.scosi.push(login);
      }
    }

    return raspuns({ ok: true, echipe: rezultat });
  } catch (err) {
    return raspuns({ ok: false, mesaj: String((err as Error)?.message || err) });
  }
});
