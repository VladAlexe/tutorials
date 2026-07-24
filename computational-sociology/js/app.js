const V = new URL(import.meta.url).searchParams.get("v") || "1";
const { getProgress, resetProgress, summarize } = await import(`./progress.js?v=${V}`);

async function loadCourse() {
  const res = await fetch("data/course.json");
  if (!res.ok) throw new Error("Nu am putut încărca cursul.");
  return res.json();
}

function renderWhatYouWillDo(list, items) {
  list.innerHTML = "";
  for (const item of items) {
    const li = document.createElement("li");
    li.textContent = item;
    list.appendChild(li);
  }
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

function renderProgress(course) {
  const progress = getProgress();
  const s = summarize(course);
  document.getElementById("progress-count").textContent =
    `${s.completed} / ${s.total} lecții`;
  document.getElementById("progress-fill").style.width = `${Math.round(s.ratio * 100)}%`;
  const summaryEl = document.getElementById("progress-summary");
  if (s.completed === 0 && s.started === 0) {
    summaryEl.textContent = "Nu ai început încă. Când începi o lecție, o vom marca aici.";
  } else if (s.completed >= s.total) {
    summaryEl.textContent = "Ai parcurs toate secțiunile disponibile în prototip.";
  } else {
    summaryEl.textContent = `${s.completed} finalizate, ${s.started} în curs.`;
  }
  return progress;
}

async function init() {
  try {
    const course = await loadCourse();

    document.getElementById("course-title").textContent = course.title;
    document.getElementById("course-subtitle").textContent = course.subtitle;
    document.getElementById("course-description").textContent = course.description;

    const meta = document.getElementById("course-meta");
    meta.innerHTML =
      `<span><strong>Public:</strong> ${course.audience}</span>` +
      `<span><strong>Durată:</strong> ${course.duration}</span>`;

    renderWhatYouWillDo(document.getElementById("what-list"), course.whatYouWillDo);
    const progress = renderProgress(course);
    renderSections(document.getElementById("section-list"), course, progress);

    document.getElementById("progress-reset").addEventListener("click", () => {
      const ok = confirm("Sigur vrei să resetezi progresul demonstrativ?");
      if (!ok) return;
      resetProgress();
      const p = renderProgress(course);
      renderSections(document.getElementById("section-list"), course, p);
    });

    const first = course.sections.find((s) => s.lesson);
    if (first) {
      document.getElementById("start-btn").href =
        `lesson.html?id=${encodeURIComponent(first.lesson)}`;
    }

    // QR widget: points at the lesson with fresh=1 so each phone starts clean.
    try {
      const { mountQr } = await import(`./qr-widget.js?v=${V}`);
      mountQr("qr-host");
    } catch (e) { /* non-fatal — QR is optional */ }
  } catch (err) {
    console.error(err);
    document.getElementById("section-list").innerHTML =
      `<li class="section-list__item">Nu am putut încărca cursul: ${err.message}</li>`;
  }
}

init();
