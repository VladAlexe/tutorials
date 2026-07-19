import { markCodeExecuted } from "./progress.js";

let worker = null;
let workerReady = false;
let workerLoading = false;
const listeners = new Set();

function supportsWorker() {
  return typeof Worker !== "undefined";
}

function ensureWorker(onStatus) {
  if (worker) return worker;
  worker = new Worker("workers/pyodide-worker.js");
  worker.addEventListener("message", (e) => {
    const msg = e.data || {};
    if (msg.type === "ready") {
      workerReady = true;
      workerLoading = false;
      onStatus && onStatus("ready");
    } else if (msg.type === "loading") {
      workerLoading = true;
      onStatus && onStatus("loading", msg.detail);
    } else if (msg.type === "result") {
      for (const l of listeners) l({ ok: true, value: msg.value, stdout: msg.stdout });
      listeners.clear();
    } else if (msg.type === "error") {
      for (const l of listeners) l({ ok: false, error: msg.error, stdout: msg.stdout });
      listeners.clear();
    }
  });
  worker.addEventListener("error", (e) => {
    for (const l of listeners) l({ ok: false, error: e.message || "Eroare în worker." });
    listeners.clear();
  });
  return worker;
}

function runInWorker(code) {
  return new Promise((resolve) => {
    listeners.add(resolve);
    worker.postMessage({ type: "run", code });
  });
}

export function renderCodeRunner(container, block) {
  container.classList.add("code-runner");

  const header = document.createElement("div");
  header.className = "code-runner__header";
  header.innerHTML = `<span>${block.title || "Exercițiu Python"}</span><span>Python · Pyodide</span>`;
  container.appendChild(header);

  if (block.description) {
    const desc = document.createElement("p");
    desc.style.margin = "0";
    desc.style.padding = "var(--sp-3) var(--sp-4) 0";
    desc.style.fontSize = "var(--fs-sm)";
    desc.style.color = "var(--color-ink-soft)";
    desc.textContent = block.description;
    container.appendChild(desc);
  }

  const editor = document.createElement("textarea");
  editor.className = "code-runner__editor";
  editor.spellcheck = false;
  editor.setAttribute("aria-label", "Editor de cod Python");
  editor.rows = Math.max(3, block.initial.split("\n").length + 1);
  editor.value = block.initial || "";
  container.appendChild(editor);

  const actions = document.createElement("div");
  actions.className = "code-runner__actions";
  container.appendChild(actions);

  if (!supportsWorker()) {
    const warn = document.createElement("div");
    warn.className = "code-runner__unsupported";
    warn.textContent =
      "Acest browser nu poate rula Pyodide (Web Worker indisponibil).";
    container.appendChild(warn);
    return;
  }

  const loadBtn = document.createElement("button");
  loadBtn.type = "button";
  loadBtn.className = "btn btn--ghost";
  loadBtn.textContent = "Încarcă Python";

  const runBtn = document.createElement("button");
  runBtn.type = "button";
  runBtn.className = "btn btn--primary";
  runBtn.textContent = "Rulează";

  const resetBtn = document.createElement("button");
  resetBtn.type = "button";
  resetBtn.className = "btn btn--ghost";
  resetBtn.textContent = "Resetează";

  const status = document.createElement("span");
  status.className = "code-runner__status";
  status.textContent = "Python nu este încărcat.";

  actions.appendChild(loadBtn);
  actions.appendChild(runBtn);
  actions.appendChild(resetBtn);
  actions.appendChild(status);

  const output = document.createElement("div");
  output.className = "code-runner__output";
  output.setAttribute("aria-live", "polite");
  output.textContent = "";
  container.appendChild(output);

  function setStatus(s, detail) {
    if (s === "loading") status.textContent = "Se încarcă Pyodide…";
    else if (s === "ready") status.textContent = "Python gata.";
    else if (s === "running") status.textContent = "Rulează…";
    else if (s === "idle") status.textContent = "Python gata.";
    else status.textContent = s;
  }

  async function ensureReady() {
    if (workerReady) return true;
    if (!workerLoading) {
      ensureWorker(setStatus);
      setStatus("loading");
      worker.postMessage({ type: "init" });
    }
    return new Promise((resolve) => {
      const iv = setInterval(() => {
        if (workerReady) { clearInterval(iv); resolve(true); }
      }, 100);
      setTimeout(() => { clearInterval(iv); resolve(workerReady); }, 60000);
    });
  }

  loadBtn.addEventListener("click", async () => {
    loadBtn.disabled = true;
    await ensureReady();
    loadBtn.disabled = false;
    loadBtn.textContent = workerReady ? "Reîncarcă Python" : "Încarcă Python";
  });

  runBtn.addEventListener("click", async () => {
    runBtn.disabled = true;
    output.className = "code-runner__output";
    output.textContent = "";
    const ok = await ensureReady();
    if (!ok) {
      output.className = "code-runner__output code-runner__output--error";
      output.textContent = "Nu am putut încărca Pyodide.";
      runBtn.disabled = false;
      return;
    }
    setStatus("running");
    const result = await runInWorker(editor.value);
    if (result.ok) {
      const parts = [];
      if (result.stdout) parts.push(result.stdout.trimEnd());
      if (result.value !== undefined && result.value !== null && result.value !== "") {
        parts.push(String(result.value));
      }
      output.textContent = parts.join("\n") || "(fără output)";
      markCodeExecuted(block.id);
    } else {
      output.className = "code-runner__output code-runner__output--error";
      output.textContent = (result.stdout ? result.stdout + "\n" : "") + (result.error || "Eroare necunoscută.");
    }
    setStatus("idle");
    runBtn.disabled = false;
  });

  resetBtn.addEventListener("click", () => {
    editor.value = block.initial || "";
    output.textContent = "";
    output.className = "code-runner__output";
  });
}
