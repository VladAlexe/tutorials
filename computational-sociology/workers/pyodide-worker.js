// Pyodide worker — runs Python off the main thread.
// Loads Pyodide from the official CDN on first `init` or `run` message.

const PYODIDE_VERSION = "0.26.2";
const PYODIDE_URL = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/pyodide.js`;

let pyodide = null;
let loading = null;

async function ensurePyodide() {
  if (pyodide) return pyodide;
  if (loading) return loading;
  loading = (async () => {
    self.postMessage({ type: "loading", detail: "importing" });
    importScripts(PYODIDE_URL);
    self.postMessage({ type: "loading", detail: "downloading" });
    pyodide = await self.loadPyodide({
      indexURL: `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`
    });
    self.postMessage({ type: "ready" });
    return pyodide;
  })();
  try {
    return await loading;
  } catch (err) {
    loading = null;
    self.postMessage({ type: "error", error: `Nu am putut încărca Pyodide: ${err.message || err}` });
    throw err;
  }
}

function toJs(value) {
  if (value === undefined || value === null) return "";
  if (typeof value?.toJs === "function") {
    try { return value.toJs({ create_proxies: false, dict_converter: Object.fromEntries }); }
    catch { /* fall through */ }
  }
  return value;
}

async function runCode(code, context) {
  const py = await ensurePyodide();

  let stdout = "";
  py.setStdout({ batched: (s) => { stdout += s + "\n"; } });
  py.setStderr({ batched: (s) => { stdout += s + "\n"; } });

  try {
    if (context && typeof context === "object") {
      for (const [k, v] of Object.entries(context)) {
        py.globals.set(k, py.toPy(v));
      }
    }
    const result = await py.runPythonAsync(code);
    const jsValue = toJs(result);
    let payload;
    if (typeof jsValue === "object" && jsValue !== null) {
      payload = jsValue;
    } else if (jsValue === undefined || jsValue === null || jsValue === "") {
      payload = "";
    } else {
      payload = jsValue;
    }
    self.postMessage({ type: "result", value: payload, stdout });
  } catch (err) {
    self.postMessage({
      type: "error",
      error: err.message || String(err),
      stdout
    });
  }
}

self.addEventListener("message", (e) => {
  const msg = e.data || {};
  if (msg.type === "init") {
    ensurePyodide().catch(() => { /* error already posted */ });
  } else if (msg.type === "run") {
    runCode(String(msg.code || ""), msg.context || null);
  }
});
