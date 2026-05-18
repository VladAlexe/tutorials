"""
EchoChamber Studio — varianta MINIMĂ (comentată pentru predare)
===============================================================
Idee de bază a Gradio: o FUNCȚIE Python -> o interfață web.
Aici fiecare tab e un `gr.Interface` (Gradio face singur butonul + layout-ul),
iar tab-urile sunt puse împreună într-un `gr.Blocks` ca să aibă temă comună.

Reguli de produs:
  · provider + model = UN SINGUR dropdown (nu se pot nepotrivi)
  · rolurile agenților se citesc din assets/roles/roles.yaml (cale absolută)
  · dacă o știre e încărcată, ea e contextul; subiectul scris INTRĂ PESTE știre
    (ex: știre despre UE + subiect „Bolojan” -> Bolojan în contextul știrii)
  · fără știre -> se vorbește doar despre subiectul scris

Rulează:  python -m app.app      (sau:  python app/app.py)
"""

# ==================================================
# 1. IMPORTS & SETUP
# ==================================================
import os, sys, html
from pathlib import Path

import gradio as gr                 # interfața web
import yaml, requests               # yaml = rolurile; requests = descarcă știrea
from bs4 import BeautifulSoup       # extrage textul din pagina HTML a știrii
from dotenv import load_dotenv      # citește cheile API din .env
from openai import OpenAI           # client OpenAI-compatible (gemini/deepseek)

# Rădăcina proiectului = folderul părinte al lui app/. O calculăm o dată
# ca să putem găsi .env, roles.yaml etc. indiferent din ce folder rulăm.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))     # ca să putem importa pachetul core/
load_dotenv(PROJECT_ROOT / ".env")        # încarcă GEMINI_API_KEY etc.

# Backend-ul construit în cursuri (NU îl rescriem, doar îl chemăm):
from core.agent import generate_agent_response          # C6 — un agent RAG
from core.graph import run_thread, HANDLES              # C7 — dezbatere

# ==================================================
# 2. CONFIG — provideri, modele, roluri din YAML
# ==================================================
# Fiecare provider are un endpoint OpenAI-compatible diferit.
BASE_URLS = {"gemini": "https://generativelanguage.googleapis.com/v1beta/openai/",
             "openrouter": "https://openrouter.ai/api/v1",
             "deepseek": "https://api.deepseek.com/v1"}
# Cheile vin din .env (numele variabilei = PROVIDER în litere mari + _API_KEY).
KEYS = {p: os.getenv(f"{p.upper()}_API_KEY") for p in BASE_URLS}
MODELS = {"gemini": ["gemini-2.5-flash-lite", "gemini-2.5-flash"],
          "openrouter": ["openrouter/auto", "google/gemini-2.5-flash-lite"],
          "deepseek": ["deepseek-chat"]}
# Arătăm doar providerii care chiar au cheie în .env.
PROVIDERS = [p for p, k in KEYS.items() if k] or ["gemini"]
K = 5      # câte fragmente recuperează retrieverul (top-k din FAISS)

# TRUC: provider + model într-UN SINGUR dropdown -> imposibil să fie nepotrivite.
# Valoarea fiecărei opțiuni e "provider|model"; o despărțim în setup().
MODEL_CHOICES = [(f"{p} · {m}", f"{p}|{m}")
                 for p in PROVIDERS for m in MODELS.get(p, [])]
DEFAULT_MM = MODEL_CHOICES[0][1] if MODEL_CHOICES else "gemini|gemini-2.5-flash-lite"

# Rolurile agenților: din YAML, cu CALE ABSOLUTĂ -> merge oricum ai porni app-ul.
ROLES_PATH = PROJECT_ROOT / "assets" / "roles" / "roles.yaml"

def load_roles():
    """Citește roles.yaml. Acceptă atât {agents: {...}} cât și {...} direct."""
    if not ROLES_PATH.exists():
        print(f"[avertisment] nu găsesc {ROLES_PATH}")
        return {}
    data = yaml.safe_load(ROLES_PATH.read_text(encoding="utf-8")) or {}
    return data.get("agents", data)

ROLES = load_roles()
# AGENTS = listă de perechi (eticheta_afișată, slug) pentru dropdown-uri.
AGENTS = [(r.get("name", s), s) for s, r in ROLES.items()]
print(f"[roluri] {len(AGENTS)} agenți din YAML: {[s for _, s in AGENTS]}")

# STARE PARTAJATĂ între tab-uri. În varianta cu gr.Blocks am folosi gr.State;
# aici, pentru cod minim, folosim două dicționare la nivel de modul.
CFG = {"provider": PROVIDERS[0], "model": MODELS[PROVIDERS[0]][0], "temp": 0.3}
ART = {"text": "", "title": ""}     # textul complet al știrii + titlul

# ==================================================
# 3. APELURI LLM / BACKEND  (core.agent, core.graph)
# ==================================================
def ask_llm(prompt, temperature=None):
    """Apel LLM direct (folosit la Chat și Rezumat). Întoarce text sau eroare."""
    if not prompt.strip():
        return "Scrie mai întâi ceva."
    try:
        c = OpenAI(api_key=KEYS[CFG["provider"]], base_url=BASE_URLS[CFG["provider"]])
        r = c.chat.completions.create(
            model=CFG["model"],
            messages=[{"role": "user", "content": prompt}],
            temperature=float(CFG["temp"] if temperature is None else temperature))
        return r.choices[0].message.content.strip()
    except Exception as e:
        return f"[Eroare: {type(e).__name__} - {e}]"

def _agent(slug, stimulus):
    """Un agent RAG (din C6). roles_path = cale absolută -> rolul din YAML
    e găsit sigur. Backend-ul face retrieval + prompt + LLM; noi doar îl chemăm."""
    return generate_agent_response(
        agent_slug=slug, stimulus=stimulus, provider=CFG["provider"],
        model=CFG["model"], k=K, temperature=float(CFG["temp"]),
        roles_path=str(ROLES_PATH)).get("response", "")

def _subject(typed):
    """Ce primește un agent ca STIMULUS — regula cerută:

      știre + subiect -> vorbim despre SUBIECT, dar ÎN CONTEXTUL știrii
      doar știre      -> vorbim despre știre
      doar subiect    -> vorbim doar despre subiect

    Notă: stimulul e și interogarea FAISS, deci îl ținem scurt și focusat
    (subiectul primul, apoi un fragment de știre, nu tot articolul)."""
    typed = (typed or "").strip()
    news = ART["text"].strip()
    if news and typed:                       # subiectul intră PESTE știre
        return f"{typed}\n\n[În contextul acestei știri:]\n{news[:600]}"
    if news:                                 # doar știre
        return news[:700]
    return typed                             # doar subiect

# ==================================================
# 4. TAB „SETĂRI”  (alege model + opțional încarcă știrea)
# ==================================================
def setup(model_choice, temperature, url):
    """Salvează provider/model/temperatură în CFG și (opțional) încarcă o știre
    în ART. Tot ce ține de configurare stă aici, într-un singur loc."""
    provider, model = model_choice.split("|", 1)     # despărțim "provider|model"
    CFG.update(provider=provider, model=model, temp=temperature)
    url = (url or "").strip()
    if not url:
        ART.update(text="", title="")
        return (f"Setări salvate.\nProvider: {provider}  ·  Model: {model}\n"
                "Nicio știre încărcată — se folosește subiectul scris în tab.")
    try:
        # Descărcăm pagina și extragem titlul (h1) + paragrafele lungi din <article>.
        resp = requests.get(url, timeout=12, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        title = soup.find("h1").get_text(" ", strip=True) if soup.find("h1") else "Știre"
        body = "\n\n".join(p.get_text(" ", strip=True)
                           for p in (soup.find("article") or soup).find_all("p")
                           if len(p.get_text(" ", strip=True)) > 40)
        if not body:
            ART.update(text="", title="")
            return "Setări salvate. Nu am putut extrage textul știrii din pagină."
        ART.update(text=f"{title}\n\n{body[:4500]}", title=title)
        return (f"Setări salvate.  Provider: {provider}  ·  Model: {model}\n\n"
                f"ȘTIRE ACTIVĂ: {title}\n"
                "Subiectul scris în celelalte tab-uri va fi discutat ÎN "
                "CONTEXTUL acestei știri.\n\n"
                f"{body[:900]}...")
    except Exception as e:
        ART.update(text="", title="")
        return f"Setări salvate. Eroare la știre: {type(e).__name__} - {e}"

# ==================================================
# 5. ACȚIUNI TAB-URI  (fiecare funcție = un tab)
# ==================================================
def chat(prompt):
    """Chat. Dacă există o știre, întrebarea ta primește răspuns DIN ea."""
    prompt = (prompt or "").strip()
    if ART["text"]:
        q = prompt or "Despre ce este știrea? Rezumă pe scurt."
        return ask_llm("Răspunde la ÎNTREBARE folosind DOAR ȘTIREA de mai jos. Ai "
                       "deja textul - nu cere alt text. Dacă nu reiese, spune asta."
                       f"\n\nȘTIRE:\n{ART['text']}\n\nÎNTREBARE:\n{q}")
    return ask_llm(prompt) if prompt else "Scrie un prompt sau încarcă o știre."

def summary():
    """Rezumă știrea încărcată (nu ia niciun input — folosește ART)."""
    if not ART["text"]:
        return "Încarcă mai întâi o știre în tab-ul Setări."
    return ask_llm("Rezumă în 5 propoziții, fără a adăuga informații.\n\n"
                   + ART["text"], temperature=0.2)

def agent(text, slug):
    """Un agent comentează subiectul (peste știre, dacă e încărcată)."""
    s = _subject(text)
    if not slug:      return "Nu există agenți (verifică assets/roles/roles.yaml)."
    if not s.strip(): return "Încarcă o știre sau scrie un subiect."
    try:    return _agent(slug, s)
    except Exception as e: return f"[Eroare: {type(e).__name__} - {e}]"

def all_agents(text):
    """Același subiect, prin TOATE rolurile din YAML (loop peste ROLES)."""
    s = _subject(text)
    if not s.strip():
        return "Încarcă o știre sau scrie un subiect."
    if not ROLES:
        return "Nu există agenți (verifică assets/roles/roles.yaml)."
    out = []
    for slug, role in ROLES.items():
        try:    r = _agent(slug, s)
        except Exception as e: r = f"[Eroare: {type(e).__name__} - {e}]"
        out.append(f"### {role.get('name', slug)}\n\n{r}")
    return "\n\n---\n\n".join(out)          # markdown cu separatoare

def debate(subject, slugs, turns):
    """Dezbatere multi-agent (C7). run_thread orchestrează agenții pe rând."""
    s = _subject(subject)
    if not slugs or len(slugs) < 2:
        return "Selectează cel puțin doi agenți."
    if not s.strip():
        return "Încarcă o știre sau scrie un subiect."
    try:
        msgs = run_thread(stimulus=s, active_slugs=slugs, total_turns=int(turns),
                          provider=CFG["provider"], model=CFG["model"], k=K)
    except Exception as e:
        return f"[Eroare dezbatere: {type(e).__name__} - {e}]"
    # Construim cardurile vizual (HTML simplu, fără fișier CSS separat).
    cards = []
    for m in msgs:
        role = ROLES.get(m.get("slug", ""), {})
        cards.append(
            f"<div style='border:1px solid #4a4a55;border-left:3px solid "
            f"{role.get('color', '#e8833a')};border-radius:12px;padding:12px 14px;"
            f"margin:10px 0;background:rgba(255,255,255,.02)'>"
            f"<div style='font-size:12px;opacity:.65;margin-bottom:6px'>"
            f"{html.escape(str(m.get('agent','')))} &middot; intervenția "
            f"{m.get('turn','')}</div><div style='font-size:15px;line-height:1.6'>"
            f"{html.escape(str(m.get('text','')))}</div></div>")
    return "<h3>Dezbatere</h3>" + "\n".join(cards)

# ==================================================
# 6. UI — logo + 6 Interface-uri + temă (zero CSS custom)
# ==================================================
# Temă „cool” fără nicio linie de CSS: portocaliu + colțuri mari + font Inter.
THEME = gr.themes.Soft(
    primary_hue="orange",
    secondary_hue="amber",
    neutral_hue="slate",
    radius_size="lg",
    spacing_size="lg",
    font=[gr.themes.GoogleFont("Inter"), "system-ui", "sans-serif"],
    font_mono=[gr.themes.GoogleFont("JetBrains Mono"), "monospace"],
)

# LOGO al site-ului: un „mark” SVG (unde concentrice = ecou) + numele.
# E doar HTML inline, deci tot „zero CSS custom” (nu fișier .css separat).
LOGO = """
<div style="display:flex;align-items:center;gap:14px;padding:8px 0 4px">
  <svg width="46" height="46" viewBox="0 0 46 46" fill="none">
    <circle cx="15" cy="23" r="5.5" fill="#ea7a2a"/>
    <path d="M23 14 A 11 11 0 0 1 23 32" stroke="#ea7a2a" stroke-width="2.6"
          fill="none" opacity=".70"/>
    <path d="M29 9 A 18 18 0 0 1 29 37" stroke="#ea7a2a" stroke-width="2.6"
          fill="none" opacity=".45"/>
    <path d="M35 4 A 25 25 0 0 1 35 42" stroke="#ea7a2a" stroke-width="2.6"
          fill="none" opacity=".22"/>
  </svg>
  <div>
    <div style="font-size:25px;font-weight:800;letter-spacing:-.5px">
      EchoChamber <span style="color:#ea7a2a">Studio</span></div>
    <div style="font-size:13px;opacity:.6">simulare discursivă pe știri
      și texte politice</div>
  </div>
</div>
"""

# Fiecare tab = un gr.Interface(funcție, inputs, outputs). Gradio face restul.
tab_setup = gr.Interface(
    setup, title="Setări",
    description="Alege provider+model dintr-un singur loc și (opțional) încarcă "
                "o știre. Dacă o știre e încărcată, subiectul scris în celelalte "
                "tab-uri se discută ÎN CONTEXTUL ei.",
    inputs=[gr.Dropdown(MODEL_CHOICES, value=DEFAULT_MM, label="Provider · Model"),
            gr.Slider(0, 1, value=0.3, step=0.1, label="Temperatură"),
            gr.Textbox(label="URL știre (gol = fără știre)", lines=2)],
    outputs=gr.Textbox(label="Stare", lines=12),
    submit_btn="Salvează / Încarcă", flagging_mode="never")

tab_chat = gr.Interface(
    chat, title="Chat",
    description="Dacă o știre e încărcată, răspund la întrebarea ta despre ea. "
                "Altfel, chat normal.",
    inputs=gr.Textbox(label="Întrebare / prompt", lines=4),
    outputs=gr.Textbox(label="Răspuns", lines=14),
    examples=[["Despre ce este știrea?"], ["Ce miză politică are?"]],
    flagging_mode="never")

tab_sum = gr.Interface(
    lambda: summary(), title="Rezumat",          # lambda: funcție fără input
    description="Rezumatul știrii încărcate (din tab-ul Setări).",
    inputs=[], outputs=gr.Textbox(label="Rezumat", lines=12),
    submit_btn="Rezumă știrea", flagging_mode="never")

tab_agent = gr.Interface(
    agent, title="Agent",
    description="Un agent comentează subiectul. Dacă o "
                "știre e încărcată, comentează subiectul ÎN CONTEXTUL ei.",
    inputs=[gr.Textbox(label="Subiect (intră peste știre, dacă e încărcată)",
                       lines=4),
            gr.Dropdown(AGENTS, value=(AGENTS[0][1] if AGENTS else None),
                        label="Agent")],
    outputs=gr.Textbox(label="Comentariu", lines=14), flagging_mode="never")

tab_all = gr.Interface(
    all_agents, title="Toți agenții",
    description="Același subiect, prin toate vocile discursive"
                "(în contextul știrii, dacă e încărcată).",
    inputs=gr.Textbox(label="Subiect (intră peste știre, dacă e încărcată)",
                      lines=4),
    outputs=gr.Markdown(), flagging_mode="never")

tab_debate = gr.Interface(
    debate, title="Dezbatere",
    description="Agenții discută între ei pe marginea "
                "subiectului, în contextul știrii dacă e încărcată.",
    inputs=[gr.Textbox(label="Subiect (intră peste știre, dacă e încărcată)",
                       lines=3),
            gr.CheckboxGroup(AGENTS, value=[v for _, v in AGENTS], label="Agenți"),
            gr.Slider(2, 12, value=5, step=1, label="Număr intervenții")],
    outputs=gr.HTML(), flagging_mode="never")

# gr.TabbedInterface nu acceptă theme= pe toate versiunile, așa că facem ce
# face el intern: un gr.Blocks cu temă + gr.Tabs, în care randăm Interface-urile.
TABS = [("Setări", tab_setup), ("Chat", tab_chat), ("Rezumat", tab_sum),
        ("Agent", tab_agent), ("Toți agenții", tab_all), ("Dezbatere", tab_debate)]

with gr.Blocks(title="EchoChamber Studio", theme=THEME) as demo:
    gr.HTML(LOGO)                              # logo-ul sus, o singură dată
    with gr.Tabs():
        for _name, _iface in TABS:             # un Tab per Interface
            with gr.Tab(_name):
                _iface.render()                # randează Interface-ul în tab

# ==================================================
# 7. LAUNCH
# ==================================================
if __name__ == "__main__":
    port = os.getenv("GRADIO_SERVER_PORT")     # opțional, din .env
    demo.launch(server_name="127.0.0.1",
                server_port=int(port) if port else None,
                share=False, inbrowser=True)