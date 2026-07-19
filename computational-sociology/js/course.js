import { getProgress } from "./progress.js";

async function loadCourse() {
  const res = await fetch("data/course.json");
  if (!res.ok) throw new Error("Nu am putut încărca cursul.");
  return res.json();
}

function renderSections(list, course, progress) {
  list.innerHTML = "";
  for (const s of course.sections) {
    const li = document.createElement("li");
    li.className = "section-list__item";

    const num = document.createElement("span");
    num.className = "section-list__num";
    num.textContent = String(s.number).padStart(2, "0");

    const body = document.createElement("div");
    body.className = "section-list__body";

    const titleWrap = document.createElement("div");
    if (s.lesson) {
      const a = document.createElement("a");
      a.href = `lesson.html?id=${encodeURIComponent(s.lesson)}`;
      a.className = "section-list__title";
      a.textContent = s.title;
      titleWrap.appendChild(a);
    } else {
      const span = document.createElement("span");
      span.className = "section-list__title";
      span.textContent = s.title;
      titleWrap.appendChild(span);
    }
    body.appendChild(titleWrap);

    const desc = document.createElement("p");
    desc.className = "section-list__desc";
    desc.textContent = s.description;
    body.appendChild(desc);

    const state = document.createElement("span");
    state.className = "section-list__state";
    const lessonState = s.lesson ? progress.lessons[s.lesson] : null;
    if (lessonState?.completed) {
      state.textContent = "Finalizată";
      state.classList.add("section-list__state--done");
    } else if (lessonState?.started) {
      state.textContent = "În curs";
    } else if (s.status === "planned") {
      state.textContent = "În pregătire";
    } else {
      state.textContent = "Disponibilă";
    }

    li.appendChild(num);
    li.appendChild(body);
    li.appendChild(state);
    list.appendChild(li);
  }
}

async function init() {
  try {
    const course = await loadCourse();
    document.getElementById("course-title").textContent = "Cuprinsul cursului";
    document.getElementById("course-subtitle").textContent = course.title;
    const progress = getProgress();
    renderSections(document.getElementById("section-list"), course, progress);
  } catch (err) {
    console.error(err);
    document.getElementById("section-list").innerHTML =
      `<li class="section-list__item">Eroare: ${err.message}</li>`;
  }
}

init();
