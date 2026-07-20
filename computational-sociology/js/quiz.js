import { markQuizAnswered, getProgress } from "./progress.js";

export function renderQuiz(container, block, options = {}) {
  const state = { selected: null, verified: false };
  const priorAnswer = getProgress().quizzes?.[block.id];
  const onAnswered = typeof options.onAnswered === "function" ? options.onAnswered : null;

  container.classList.add("quiz");
  container.setAttribute("role", "group");
  container.setAttribute("aria-labelledby", `${block.id}-q`);

  const question = document.createElement("p");
  question.className = "quiz__question";
  question.id = `${block.id}-q`;
  question.textContent = block.question;
  container.appendChild(question);

  const list = document.createElement("ul");
  list.className = "quiz__options";
  container.appendChild(list);

  const optionEls = [];
  block.options.forEach((opt, idx) => {
    const li = document.createElement("li");
    const label = document.createElement("label");
    label.className = "quiz__option";
    label.tabIndex = 0;

    const input = document.createElement("input");
    input.type = "radio";
    input.name = `quiz-${block.id}`;
    input.value = String(idx);
    input.setAttribute("aria-describedby", `${block.id}-q`);

    const text = document.createElement("span");
    text.textContent = opt;

    label.appendChild(input);
    label.appendChild(text);
    li.appendChild(label);
    list.appendChild(li);
    optionEls.push({ label, input, idx });

    input.addEventListener("change", () => selectOption(idx));
    label.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        input.checked = true;
        selectOption(idx);
      }
    });
  });

  const actions = document.createElement("div");
  actions.className = "btn-row";
  actions.style.marginTop = "var(--sp-4)";

  const verifyBtn = document.createElement("button");
  verifyBtn.type = "button";
  verifyBtn.className = "btn btn--primary";
  verifyBtn.textContent = "Verifică";
  verifyBtn.disabled = true;
  verifyBtn.addEventListener("click", verify);

  const retryBtn = document.createElement("button");
  retryBtn.type = "button";
  retryBtn.className = "btn btn--ghost";
  retryBtn.textContent = "Încearcă din nou";
  retryBtn.hidden = true;
  retryBtn.addEventListener("click", reset);

  actions.appendChild(verifyBtn);
  actions.appendChild(retryBtn);
  container.appendChild(actions);

  const feedback = document.createElement("div");
  feedback.className = "quiz__feedback";
  feedback.hidden = true;
  feedback.setAttribute("role", "status");
  container.appendChild(feedback);

  const explanation = document.createElement("p");
  explanation.className = "quiz__explanation";
  explanation.hidden = true;
  if (block.explanation) explanation.textContent = block.explanation;
  container.appendChild(explanation);

  if (priorAnswer && typeof priorAnswer.selectedIndex === "number") {
    const el = optionEls[priorAnswer.selectedIndex];
    if (el) {
      el.input.checked = true;
      selectOption(priorAnswer.selectedIndex);
      verify();
    }
  }

  function selectOption(idx) {
    if (state.verified) return;
    state.selected = idx;
    for (const o of optionEls) {
      o.label.classList.toggle("quiz__option--selected", o.idx === idx);
    }
    verifyBtn.disabled = false;
  }

  function verify() {
    if (state.selected === null) return;
    state.verified = true;
    const correct = state.selected === block.correctIndex;
    for (const o of optionEls) {
      o.input.disabled = true;
      o.label.classList.remove("quiz__option--selected");
      if (o.idx === block.correctIndex) {
        o.label.classList.add("quiz__option--correct");
      } else if (o.idx === state.selected && !correct) {
        o.label.classList.add("quiz__option--incorrect");
      }
    }
    feedback.hidden = false;
    feedback.textContent = correct ? "Corect." : "Nu chiar. Vezi explicația.";
    feedback.className = "quiz__feedback " + (correct
      ? "quiz__feedback--correct"
      : "quiz__feedback--incorrect");
    if (block.explanation) explanation.hidden = false;
    verifyBtn.hidden = true;
    retryBtn.hidden = false;
    markQuizAnswered(block.id, { correct, selectedIndex: state.selected });
    if (onAnswered) onAnswered({ correct, selectedIndex: state.selected });
  }

  function reset() {
    state.selected = null;
    state.verified = false;
    for (const o of optionEls) {
      o.input.disabled = false;
      o.input.checked = false;
      o.label.classList.remove(
        "quiz__option--selected",
        "quiz__option--correct",
        "quiz__option--incorrect"
      );
    }
    feedback.hidden = true;
    explanation.hidden = true;
    verifyBtn.hidden = false;
    verifyBtn.disabled = true;
    retryBtn.hidden = true;
  }
}
