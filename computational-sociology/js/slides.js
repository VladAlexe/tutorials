const V = new URL(import.meta.url).searchParams.get("v") || "1";
const [
  { renderQuiz },
  { renderNetwork, renderInteractive },
  {
    markSlidePosition,
    getSlidePosition,
    getProgress,
    markLessonStarted,
    markLessonCompleted,
    resetLessonProgress
  }
] = await Promise.all([
  import(`./quiz.js?v=${V}`),
  import(`./visualizations.js?v=${V}`),
  import(`./progress.js?v=${V}`)
]);

function makeSlideElement() {
  const el = document.createElement("section");
  el.className = "slide";
  el.hidden = true;
  el.tabIndex = -1;
  el.setAttribute("aria-hidden", "true");
  el.setAttribute("aria-roledescription", "diapozitiv");
  return el;
}

function addTitle(el, text, small) {
  const h = document.createElement(small ? "h2" : "h1");
  h.className = "slide__title" + (small ? " slide__title--sm" : "");
  h.textContent = text;
  el.appendChild(h);
}

function addBody(el, html) {
  const wrap = document.createElement("div");
  wrap.className = "slide__body";
  const p = document.createElement("p");
  p.innerHTML = html;
  wrap.appendChild(p);
  el.appendChild(wrap);
}

function addIntro(el, text) {
  const p = document.createElement("p");
  p.className = "slide__intro";
  p.textContent = text;
  el.appendChild(p);
}

function fillSlide(slideState, onAnswered) {
  if (slideState.fillPromise) return slideState.fillPromise;
  slideState.fillPromise = (async () => {
    const b = slideState.block;
    const el = slideState.el;

    switch (b.type) {
      case "text": {
        if (b.title) addTitle(el, b.title);
        if (b.content) addBody(el, b.content);
        break;
      }
      case "callout": {
        const c = document.createElement("aside");
        c.className = "callout";
        if (b.title) {
          const h = document.createElement("h2");
          h.className = "callout__title";
          h.textContent = b.title;
          c.appendChild(h);
        }
        const p = document.createElement("p");
        p.innerHTML = b.content;
        p.style.margin = "0";
        c.appendChild(p);
        el.appendChild(c);
        break;
      }
      case "image": {
        const fig = document.createElement("figure");
        fig.className = "figure";
        const img = document.createElement("img");
        img.src = b.src;
        img.alt = b.alt || "";
        img.loading = "lazy";
        fig.appendChild(img);
        if (b.caption) {
          const cap = document.createElement("figcaption");
          cap.className = "figure__caption";
          cap.textContent = b.caption;
          fig.appendChild(cap);
        }
        el.appendChild(fig);
        break;
      }
      case "video": {
        const v = document.createElement("div");
        v.className = "video-placeholder";
        v.innerHTML = `<strong>${b.title || "Video"}</strong><br>${b.note || ""}`;
        el.appendChild(v);
        break;
      }
      case "quiz": {
        if (b.title) addTitle(el, b.title, true);
        const wrap = document.createElement("div");
        renderQuiz(wrap, b, { onAnswered: () => onAnswered(slideState) });
        el.appendChild(wrap);
        break;
      }
      case "visualization": {
        if (b.title) addTitle(el, b.title, true);
        if (b.description) addIntro(el, b.description);
        const vizWrap = document.createElement("div");
        el.appendChild(vizWrap);
        if (b.kind === "network") {
          slideState.viz = await renderNetwork(vizWrap, b);
        }
        break;
      }
      case "interactive": {
        if (b.title) addTitle(el, b.title, true);
        if (b.intro) addIntro(el, b.intro);
        const vizWrap = document.createElement("div");
        el.appendChild(vizWrap);
        slideState.viz = await renderInteractive(vizWrap, b);
        break;
      }
      case "conclusion": {
        if (b.title) addTitle(el, b.title);
        if (b.content) addBody(el, b.content);
        break;
      }
      default: {
        const p = document.createElement("p");
        p.textContent = `Bloc necunoscut: ${b.type}`;
        el.appendChild(p);
      }
    }
  })();
  return slideState.fillPromise;
}

export function renderSlides(root, lesson) {
  markLessonStarted(lesson.id);
  root.innerHTML = "";
  root.classList.add("slides-root");

  const blocks = lesson.blocks || [];
  const total = blocks.length;

  const progressState = getProgress();
  const slideState = blocks.map((b) => {
    const s = {
      block: b,
      el: makeSlideElement(),
      fillPromise: null,
      viz: null,
      canAdvance: b.type !== "quiz"
    };
    if (b.type === "quiz" && progressState.quizzes?.[b.id]) {
      s.canAdvance = true;
    }
    return s;
  });

  const header = document.createElement("div");
  header.className = "slides-header";
  const bar = document.createElement("div");
  bar.className = "slides-progress-bar";
  bar.setAttribute("role", "presentation");
  const fill = document.createElement("div");
  fill.className = "slides-progress-fill";
  bar.appendChild(fill);
  const count = document.createElement("div");
  count.className = "slides-count";
  count.setAttribute("aria-live", "polite");
  header.appendChild(bar);
  header.appendChild(count);
  root.appendChild(header);

  const stage = document.createElement("div");
  stage.className = "slides-stage";
  stage.setAttribute("aria-live", "polite");
  root.appendChild(stage);
  slideState.forEach((s) => stage.appendChild(s.el));

  const nav = document.createElement("div");
  nav.className = "slides-nav";
  const backBtn = document.createElement("button");
  backBtn.type = "button";
  backBtn.className = "btn btn--ghost slides-back";
  backBtn.textContent = "Înapoi";
  const nextBtn = document.createElement("button");
  nextBtn.type = "button";
  nextBtn.className = "btn btn--primary slides-next";
  nextBtn.textContent = "Continuă";
  nav.appendChild(backBtn);
  nav.appendChild(nextBtn);
  root.appendChild(nav);

  let current = 0;
  const saved = getSlidePosition(lesson.id);
  const hasSaved = Number.isInteger(saved) && saved > 0 && saved < total;

  function onQuizAnswered(s) {
    s.canAdvance = true;
    updateNav();
  }

  function collectQuizIds() {
    return blocks.filter((b) => b.type === "quiz" && b.id).map((b) => b.id);
  }

  function doRestart() {
    resetLessonProgress(lesson.id, collectQuizIds());
    slideState.forEach((s) => {
      if (s.viz && typeof s.viz.destroy === "function") {
        try { s.viz.destroy(); } catch { /* ignore */ }
      }
      s.fillPromise = null;
      s.viz = null;
      s.el.innerHTML = "";
      if (s.block.type === "quiz") s.canAdvance = false;
    });
  }

  function showResumeBanner(atIndex) {
    const banner = document.createElement("section");
    banner.className = "slide slides-resume";
    banner.tabIndex = -1;
    banner.setAttribute("aria-live", "polite");
    banner.innerHTML =
      `<h1 class="slide__title">Reia lecția?</h1>` +
      `<p class="slide__intro">Ai lăsat lecția la slide-ul ${atIndex + 1} din ${total}. ` +
      `Vrei să continui de acolo sau să începi din nou?</p>` +
      `<div class="btn-row">` +
      `<button type="button" class="btn btn--primary" data-resume="continue">Continuă</button>` +
      `<button type="button" class="btn btn--ghost" data-resume="restart">Începe din nou</button>` +
      `</div>`;
    stage.prepend(banner);
    slideState.forEach((s) => { s.el.hidden = true; });
    backBtn.hidden = true;
    nextBtn.hidden = true;
    fill.style.width = "0%";
    count.textContent = "";

    banner.querySelector('[data-resume="continue"]').addEventListener("click", () => {
      banner.remove();
      nextBtn.hidden = false;
      show(atIndex);
    });
    banner.querySelector('[data-resume="restart"]').addEventListener("click", () => {
      banner.remove();
      nextBtn.hidden = false;
      doRestart();
      show(0);
    });
    banner.focus({ preventScroll: true });
  }

  function updateNav() {
    const pct = Math.round(((current + 1) / total) * 100);
    fill.style.width = `${pct}%`;
    count.textContent = `${current + 1} / ${total}`;
    backBtn.hidden = current === 0;
    const isLast = current === total - 1;
    nextBtn.textContent = isLast ? "Înapoi la curs" : "Continuă";
    const cur = slideState[current];
    nextBtn.disabled = !isLast && !cur.canAdvance;
  }

  async function show(idx) {
    idx = Math.max(0, Math.min(total - 1, idx));
    slideState.forEach((s, i) => {
      const active = i === idx;
      s.el.hidden = !active;
      s.el.setAttribute("aria-hidden", active ? "false" : "true");
    });
    current = idx;
    updateNav();
    markSlidePosition(lesson.id, idx);
    window.scrollTo({ top: 0, behavior: "auto" });
    slideState[idx].el.focus({ preventScroll: true });

    await fillSlide(slideState[idx], onQuizAnswered);

    if (current !== idx) return;
    const viz = slideState[idx].viz;
    if (viz && typeof viz.refit === "function") {
      requestAnimationFrame(() => {
        if (current === idx) viz.refit();
      });
    }
  }

  function goNext() {
    if (current === total - 1) {
      markLessonCompleted(lesson.id);
      location.href = "index.html";
      return;
    }
    if (!slideState[current].canAdvance) return;
    show(current + 1);
  }

  backBtn.addEventListener("click", () => show(current - 1));
  nextBtn.addEventListener("click", goNext);

  root.addEventListener("keydown", (e) => {
    const t = e.target;
    if (t && (t.tagName === "TEXTAREA" || t.tagName === "INPUT")) return;
    if (e.key === "ArrowRight") {
      e.preventDefault();
      if (current < total - 1 && slideState[current].canAdvance) show(current + 1);
      else if (current === total - 1) goNext();
    } else if (e.key === "ArrowLeft") {
      e.preventDefault();
      if (current > 0) show(current - 1);
    } else if (e.key === "Enter") {
      if (t && (t.tagName === "BUTTON" || t.tagName === "A" || t.tagName === "LABEL")) return;
      e.preventDefault();
      goNext();
    }
  });

  if (hasSaved) {
    showResumeBanner(saved);
  } else {
    show(0);
  }
}
