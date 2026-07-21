const V = new URL(import.meta.url).searchParams.get("v") || "1";
const { markCodeExecuted } = await import(`./progress.js?v=${V}`);

let worker = null;
let workerReady = false;
let workerLoading = false;
const listeners = new Set();
const statusSubscribers = new Set();

function supportsWorker() {
  return typeof Worker !== "undefined";
}

function notifyStatus(state, detail) {
  for (const fn of statusSubscribers) {
    try { fn(state, detail); } catch { /* ignore */ }
  }
}

export function subscribeStatus(fn) {
  statusSubscribers.add(fn);
  if (workerReady) fn("ready");
  else if (workerLoading) fn("loading");
  else fn("idle");
  return () => statusSubscribers.delete(fn);
}

function ensureWorker() {
  if (worker) return worker;
  worker = new Worker("workers/pyodide-worker.js");
  worker.addEventListener("message", (e) => {
    const msg = e.data || {};
    if (msg.type === "ready") {
      workerReady = true;
      workerLoading = false;
      notifyStatus("ready");
    } else if (msg.type === "loading") {
      workerLoading = true;
      notifyStatus("loading", msg.detail);
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

function runInWorker(code, context) {
  return new Promise((resolve) => {
    listeners.add(resolve);
    worker.postMessage({ type: "run", code, context: context || null });
  });
}

async function ensureReady() {
  if (workerReady) return true;
  if (!workerLoading) {
    ensureWorker();
    notifyStatus("loading");
    worker.postMessage({ type: "init" });
  }
  return new Promise((resolve) => {
    const iv = setInterval(() => {
      if (workerReady) { clearInterval(iv); resolve(true); }
    }, 100);
    setTimeout(() => { clearInterval(iv); resolve(workerReady); }, 60000);
  });
}

// Preload Pyodide on lesson entry (fire-and-forget).
export function preloadPyodide() {
  if (!supportsWorker()) return;
  if (workerReady || workerLoading) return;
  ensureWorker();
  notifyStatus("loading");
  worker.postMessage({ type: "init" });
}

// Classic code runner (simple demo lesson — pre-existing usage)
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
    warn.textContent = "Acest browser nu poate rula Pyodide (Web Worker indisponibil).";
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
  container.appendChild(output);

  function setStatus(s) {
    if (s === "loading") status.textContent = "Se încarcă Pyodide…";
    else if (s === "ready") status.textContent = "Python gata.";
    else if (s === "running") status.textContent = "Rulează…";
    else status.textContent = "Python gata.";
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
        parts.push(typeof result.value === "object" ? JSON.stringify(result.value) : String(result.value));
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

/**
 * Interactive Python cell wired to a visualization above.
 * The block:
 *   { id, initial: "PRAG = 3\n...", contextProvider: async () => ({pairs: [...]}), onResult(value) }
 * The Python code returns a value (list/dict) that JS receives.
 */
export function renderCodeInteractive(container, block, { getContext, onResult }) {
  container.classList.add("code-runner");

  const header = document.createElement("div");
  header.className = "code-runner__header";
  header.innerHTML =
    `<span>${block.headerLabel || "Cod Python"}</span>` +
    `<span>Python · Pyodide</span>`;
  container.appendChild(header);

  const editor = document.createElement("textarea");
  editor.className = "code-runner__editor";
  editor.spellcheck = false;
  editor.setAttribute("aria-label", "Editor de cod Python");
  editor.rows = Math.max(2, (block.initial || "").split("\n").length + 1);
  editor.value = block.initial || "";
  container.appendChild(editor);

  const actions = document.createElement("div");
  actions.className = "code-runner__actions";
  container.appendChild(actions);

  if (!supportsWorker()) {
    const warn = document.createElement("div");
    warn.className = "code-runner__unsupported";
    warn.textContent = "Acest browser nu poate rula Pyodide (Web Worker indisponibil).";
    container.appendChild(warn);
    return { destroy() {} };
  }

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
  status.textContent = "Se pregătește Python…";

  actions.appendChild(runBtn);
  actions.appendChild(resetBtn);
  actions.appendChild(status);

  const unsub = subscribeStatus((s) => {
    if (s === "loading") status.textContent = "Se încarcă Pyodide…";
    else if (s === "ready") status.textContent = "Python gata.";
    else if (s === "running") status.textContent = "Rulează…";
    else status.textContent = "Python gata.";
  });

  // Try to trigger preload silently
  preloadPyodide();

  runBtn.addEventListener("click", async () => {
    runBtn.disabled = true;
    status.textContent = "Se pregătește Pyodide…";
    const ok = await ensureReady();
    if (!ok) {
      status.textContent = "Nu am putut încărca Pyodide.";
      runBtn.disabled = false;
      return;
    }
    status.textContent = "Rulează…";
    const ctx = getContext ? await getContext() : null;
    const result = await runInWorker(editor.value, ctx);
    if (result.ok) {
      markCodeExecuted(block.id);
      status.textContent = "Rulat.";
      if (typeof onResult === "function") {
        try { onResult(result.value); } catch (e) { console.error(e); }
      }
    } else {
      status.textContent = "Eroare Python.";
      const err = document.createElement("div");
      err.className = "code-runner__output code-runner__output--error";
      err.textContent = (result.stdout ? result.stdout + "\n" : "") + (result.error || "Eroare necunoscută.");
      // Replace previous err if any
      const old = container.querySelector(".code-runner__output--error");
      if (old) old.remove();
      container.appendChild(err);
    }
    runBtn.disabled = false;
  });

  resetBtn.addEventListener("click", () => {
    editor.value = block.initial || "";
    const err = container.querySelector(".code-runner__output--error");
    if (err) err.remove();
  });

  return {
    destroy() { try { unsub(); } catch { /* ignore */ } }
  };
}
