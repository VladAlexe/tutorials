/* ===========================================================================
   Configurare Supabase
   Proiect: dsw-2026  (ybvtxenerriwstiktebe), West Europe, Londra

   Cheia de mai jos ESTE publica, prin proiectare. Ajunge in pagina si o vede
   oricine, si asa trebuie: accesul la date nu e decis de ea, ci de politicile
   din baza de date (db/02-politici.sql).

   NU se pune aici niciodata: cheia secreta (sb_secret_... sau service_role)
   si parola bazei de date. Tot ce e in acest repo e servit public.
   =========================================================================== */

export const SUPABASE_URL = "https://ybvtxenerriwstiktebe.supabase.co";

/* De completat. In panou: Settings, apoi API Keys.
   Cauta cheia publica: incepe cu "sb_publishable_".
   Daca proiectul are inca si cheia veche, aceea se numeste "anon public"
   si e un sir lung care incepe cu "eyJ". Oricare dintre ele merge. */
export const SUPABASE_ANON = "PUNE-AICI-CHEIA-PUBLICA";

/* Adresa la care se intoarce studentul dupa ce apasa linkul din e-mail.
   Trebuie trecuta si in Authentication, URL Configuration, Redirect URLs. */
export const ADRESA_RETUR = window.location.origin + "/data-science-workflows/cont/";

/* Intrarea cu e-mail e ascunsa pana cand configurezi un serviciu de trimitere
   (de exemplu Resend) in Authentication, Emails, SMTP Settings.
   Serviciul inclus in Supabase trimite doar 2 mesaje pe ora si numai catre
   membrii echipei proiectului, deci nu ajunge la studenti.
   Pune true dupa ce ai configurat SMTP. */
export const PERMITE_EMAIL = false;
