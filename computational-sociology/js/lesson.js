import { markLessonStarted, markLessonCompleted } from "./progress.js";
import { renderQuiz } from "./quiz.js";
import { renderCodeRunner } from "./code-runner.js";
import { renderNetwork } from "./visualizations.js";

function getLessonId() {
  const params = new URLSearchParams(location.search);
  return params.get("id") || "demo";
}

async function loadLesson(id) {
  const res = await fetch(`lessons/${id}.json`);
  if (!res.ok) throw new Error(`Nu am putut încărca lecția „${id}”.`);
  return res.json();
}

function renderText(block) {
  const el = document.createElement("div");
  el.className = "block block--text";
  const p = document.createElement("p");
  p.innerHTML = block.content;
  el.appendChild(p);
  return el;
}

function renderCallout(block) {
  const el = document.createElement("aside");
  el.className = "callout";
  if (block.title) {
    const h = document.createElement("h3");
    h.className = "callout__title";
    h.textContent = block.title;
    el.appendChild(h);
  }
  const p = document.createElement("p");
  p.innerHTML = block.content;
  p.style.margin = "0";
  el.appendChild(p);
  return el;
}

function renderImage(block) {
  const fig = document.createElement("figure");
  fig.className = "figure";
  const img = document.createElement("img");
  img.src = block.src;
  img.alt = block.alt || "";
  img.loading = "lazy";
  fig.appendChild(img);
  if (block.caption) {
    const cap = document.createElement("figcaption");
    cap.className = "figure__caption";
    cap.textContent = block.caption;
    fig.appendChild(cap);
  }
  return fig;
}

function renderVideo(block) {
  const el = document.createElement("div");
  el.className = "video-placeholder";
  el.innerHTML = `<strong>${block.title || "Video"}</strong><br>${block.note || "Videoclip nu este încă disponibil."}`;
  return el;
}

function renderConclusion(block) {
  const el = document.createElement("section");
  el.className = "conclusion";
  if (block.title) {
    const h = document.createElement("h2");
    h.textContent = block.title;
    el.appendChild(h);
  }
  const p = document.createElement("p");
  p.innerHTML = block.content;
  el.appendChild(p);
  return el;
}

function renderBlock(block) {
  switch (block.type) {
    case "text":         return renderText(block);
    case "callout":      return renderCallout(block);
    case "image":        return renderImage(block);
    case "video":        return renderVideo(block);
    case "quiz": {
      const el = document.createElement("div");
      renderQuiz(el, block);
      return el;
    }
    case "code": {
      const el = document.createElement("div");
      renderCodeRunner(el, block);
      return el;
    }
    case "visualization": {
      const el = document.createElement("div");
      if (block.title) {
        const h = document.createElement("h3");
        h.textContent = block.title;
        el.appendChild(h);
      }
      if (block.description) {
        const p = document.createElement("p");
        p.className = "section-list__desc";
        p.textContent = block.description;
        el.appendChild(p);
      }
      const viz = document.createElement("div");
      el.appendChild(viz);
      if (block.kind === "network") renderNetwork(viz, block);
      return el;
    }
    case "conclusion":   return renderConclusion(block);
    default: {
      const el = document.createElement("p");
      el.textContent = `Bloc necunoscut: ${block.type}`;
      return el;
    }
  }
}

async function init() {
  const id = getLessonId();
  try {
    const lesson = await loadLesson(id);
    markLessonStarted(id);

    document.title = `${lesson.title} — Sociologie computațională`;
    document.getElementById("lesson-title").textContent = lesson.title;
    document.getElementById("crumb-lesson").textContent = lesson.title;
    if (lesson.lede) {
      document.getElementById("lesson-lede").textContent = lesson.lede;
    } else {
      document.getElementById("lesson-lede").remove();
    }

    const root = document.getElementById("lesson-blocks");
    root.innerHTML = "";
    for (const block of lesson.blocks) {
      root.appendChild(renderBlock(block));
    }

    const prevLink = document.getElementById("prev-link");
    const nextLink = document.getElementById("next-link");
    if (lesson.prev) {
      prevLink.href = `lesson.html?id=${encodeURIComponent(lesson.prev)}`;
    } else {
      prevLink.href = "index.html";
    }
    if (lesson.next) {
      nextLink.href = `lesson.html?id=${encodeURIComponent(lesson.next)}`;
      nextLink.querySelector(".lesson-nav__label").nextSibling.textContent =
        " Următoarea lecție";
    } else {
      nextLink.href = "index.html";
      nextLink.classList.add("btn--primary");
      nextLink.innerHTML = `<span class="lesson-nav__label">Următor</span> Înapoi la curs`;
      nextLink.addEventListener("click", () => markLessonCompleted(id));
    }
  } catch (err) {
    console.error(err);
    document.getElementById("lesson-blocks").innerHTML =
      `<p>${err.message}</p>`;
  }
}

init();
