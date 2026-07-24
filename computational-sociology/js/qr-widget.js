// QR widget for the course page: renders a QR pointing to the fresh-start
// lesson URL, plus a "Mărește pentru proiector" overlay that fills the screen.
// Loads the encoder locally (js/vendor/qr.js). No CDN, no external service.

const V = new URL(import.meta.url).searchParams.get("v") || "1";

async function loadEncoder() {
  // Import as a script tag rather than an ES module — qr.js attaches window.QR.
  if (window.QR) return window.QR;
  await new Promise((resolve, reject) => {
    const s = document.createElement("script");
    s.src = `js/vendor/qr.js?v=${V}`;
    s.onload = resolve;
    s.onerror = () => reject(new Error("Nu am putut încărca js/vendor/qr.js"));
    document.head.appendChild(s);
  });
  return window.QR;
}

function buildLessonUrl() {
  // Absolute URL to lesson.html with fresh reset param, so every scan starts
  // with no persisted votes/quiz answers.
  return new URL("lesson.html?id=highschool&fresh=1", location.href).href;
}

function makeOverlay(url, svgLarge) {
  const wrap = document.createElement("div");
  wrap.className = "qr-overlay";
  wrap.setAttribute("role", "dialog");
  wrap.setAttribute("aria-modal", "true");
  wrap.setAttribute("aria-label", "Cod QR mărit pentru proiector");
  wrap.innerHTML =
    `<button type="button" class="qr-overlay__close" aria-label="Închide">×</button>` +
    `<div class="qr-overlay__inner">` +
      `<div class="qr-overlay__svg">${svgLarge}</div>` +
      `<div class="qr-overlay__url">${url}</div>` +
      `<div class="qr-overlay__hint">Apasă ESC sau clic oriunde pentru a închide.</div>` +
    `</div>`;
  function close() {
    wrap.remove();
    document.removeEventListener("keydown", onKey);
  }
  function onKey(e) { if (e.key === "Escape") close(); }
  wrap.addEventListener("click", close);
  document.addEventListener("keydown", onKey);
  return wrap;
}

export async function mountQr(hostId = "qr-host") {
  const host = document.getElementById(hostId);
  if (!host) return;
  const url = buildLessonUrl();
  try {
    const QR = await loadEncoder();
    const svgSmall = QR.svg(url, { size: 200, margin: 4 });
    const svgLarge = QR.svg(url, { size: 1200, margin: 4 });
    host.innerHTML =
      `<h2 class="qr__title">Intră de pe telefon</h2>` +
      `<div class="qr__grid">` +
        `<div class="qr__svg">${svgSmall}</div>` +
        `<div class="qr__body">` +
          `<p class="qr__hint">Scanează codul cu camera telefonului. Fiecare telefon deschide lecția curat, fără răspunsurile din sesiunea anterioară.</p>` +
          `<div class="qr__url">${url}</div>` +
          `<button type="button" class="btn btn--ghost qr__enlarge">Mărește pentru proiector</button>` +
        `</div>` +
      `</div>`;
    host.querySelector(".qr__enlarge").addEventListener("click", () => {
      document.body.appendChild(makeOverlay(url, svgLarge));
    });
  } catch (err) {
    host.innerHTML =
      `<h2 class="qr__title">Intră de pe telefon</h2>` +
      `<p class="qr__hint">Nu am putut genera codul QR. Adresa lecției:</p>` +
      `<div class="qr__url">${url}</div>`;
  }
}
