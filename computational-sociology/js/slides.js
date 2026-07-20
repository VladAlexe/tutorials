import { renderQuiz } from "./quiz.js";
import { renderNetwork } from "./visualizations.js";
import {
  markSlidePosition,
  getSlidePosition,
  getProgress,
  markLessonStarted,
  markLessonCompleted
} from "./progress.js";

function buildSlide(block, slideState) {
  const el = document.createElement("section");
  el.className = "slide";
  el.hidden = true;
  el.tabIndex = -1;
  el.setAttribute("aria-hidden", "true");
  el.setAttribute("aria-roledescription", "diapozitiv");
  slideState.el = el;
  return el;
}

function fillSlide(slideState, onAnswered) {
  if (slideState.filled) return;
  slideState.filled = true;
  const b = slideState.block;
  const el = slideState.el;

  switch (b.type) {
    case "text": {
      if (b.title) {
        const h = document.createElement("h1");
        h.className = "slide__title";
        h.textContent = b.title;
        el.appendChild(h);
      }
      const body = document.createElement("div");
      body.className = "slide__body";
      const p = document.createElement("p");
      p.innerHTML = b.content;
      body.appendChild(p);
      el.appendChild(body);
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
      const wrap = document.createElement("div");
      renderQuiz(wrap, b, {
        onAnswered: () => onAnswered(slideState)
      });
      el.appendChild(wrap);
      break;
    }
    case "visualization": {
      if (b.title) {
        const h = document.createElement("h2");
        h.className = "slide__title slide__title--sm";
        h.textContent = b.title;
        el.appendChild(h);
      }
      const vizWrap = document.createElement("div");
      el.appendChild(vizWrap);
      if (b.description) {
        const cap = document.createElement("p");
        cap.className = "slide__caption";
        cap.textContent = b.description;
        el.appendChild(cap);
      }
      if (b.kind === "network") {
        renderNetwork(vizWrap, b);
      }
      break;
    }
    case "conclusion": {
      if (b.title) {
        const h = document.createElement("h1");
        h.className = "slide__title";
        h.textContent = b.title;
        el.appendChild(h);
      }
      const body = document.createElement("div");
      body.className = "slide__body";
      const p = document.createElement("p");
      p.innerHTML = b.content;
      body.appendChild(p);
      el.appendChild(body);
      break;
    }
    default: {
      const p = document.createElement("p");
      p.textContent = `Bloc necunoscut: ${b.type}`;
      el.appendChild(p);
    }
  }
}

export function renderSlides(root, lesson) {
  markLessonStarted(lesson.id);
  root.innerHTML = "";
  root.classList.add("slides-root");

  const blocks = lesson.blocks || [];
  const total = blocks.length;

  const progressState = getProgress();
  const slideState = blocks.map((b) => {
    const s = { block: b, el: null, filled: false, canAdvance: b.type !== "quiz" };
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

  slideState.forEach((s) => stage.appendChild(buildSlide(s.block, s)));

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
  if (Number.isInteger(saved) && saved >= 0 && saved < total) current = saved;

  function onQuizAnswered(s) {
    s.canAdvance = true;
    updateNav();
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

  function show(idx) {
    idx = Math.max(0, Math.min(total - 1, idx));
    slideState.forEach((s, i) => {
      const active = i === idx;
      s.el.hidden = !active;
      s.el.setAttribute("aria-hidden", active ? "false" : "true");
    });
    current = idx;
    fillSlide(slideState[idx], onQuizAnswered);
    updateNav();
    markSlidePosition(lesson.id, idx);
    window.scrollTo({ top: 0, behavior: "auto" });
    slideState[idx].el.focus({ preventScroll: true });
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

  show(current);
}
