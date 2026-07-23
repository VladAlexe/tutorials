const V = new URL(import.meta.url).searchParams.get("v") || "1";
const { markQuizAnswered, clearQuiz, getProgress, markVote, getVote } = await import(`./progress.js?v=${V}`);

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
  retryBtn.className = "btn btn--ghost btn--sm";
  retryBtn.textContent = "Răspunde din nou";
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
    // Clear the persisted answer as well, so a page refresh does not
    // auto-restore the previous answer and re-verify it.
    clearQuiz(block.id);
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

/**
 * Vote block: question, big options, reveal after choice with message + optional bars.
 * block: { id, question, options[], reveal: { text, bars, messagesByOption } }
 */
export function renderVote(container, block, options = {}) {
  const onAnswered = typeof options.onAnswered === "function" ? options.onAnswered : null;
  const prior = getVote(block.id);

  container.classList.add("vote");

  const q = document.createElement("p");
  q.className = "vote__question";
  q.textContent = block.question;
  container.appendChild(q);

  const optWrap = document.createElement("div");
  optWrap.className = "vote__options";
  container.appendChild(optWrap);

  const revealWrap = document.createElement("div");
  revealWrap.className = "vote__reveal";
  revealWrap.hidden = true;
  container.appendChild(revealWrap);

  const optBtns = [];
  (block.options || []).forEach((opt, idx) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "btn btn--ghost vote__option";
    btn.textContent = opt;
    btn.addEventListener("click", () => pick(idx));
    optWrap.appendChild(btn);
    optBtns.push(btn);
  });

  async function pick(idx) {
    for (const b of optBtns) {
      b.disabled = true;
      b.classList.toggle("vote__option--picked", optBtns.indexOf(b) === idx);
    }
    markVote(block.id, { selectedIndex: idx });
    // Fire onAnswered FIRST so gating unblocks even if reveal render fails
    if (onAnswered) onAnswered({ selectedIndex: idx });
    try { await showReveal(idx); } catch (e) { console.error("vote reveal error", e); }
  }

  async function showReveal(idx) {
    revealWrap.hidden = false;
    revealWrap.innerHTML = "";
    const reveal = block.reveal || {};
    const msg = reveal.messagesByOption && reveal.messagesByOption[String(idx)];
    if (msg) {
      const p = document.createElement("p");
      p.className = "vote__reveal-msg";
      p.innerHTML = msg;
      revealWrap.appendChild(p);
    }
    if (reveal.text) {
      const p = document.createElement("p");
      p.className = "vote__reveal-text";
      p.innerHTML = reveal.text;
      revealWrap.appendChild(p);
    }
    if (Array.isArray(reveal.bars) && reveal.bars.length) {
      const chartWrap = document.createElement("div");
      chartWrap.className = "chart";
      const { renderChart } = await import(`./charts.js?v=${V}`);
      await renderChart(chartWrap, { variant: "bars", bars: reveal.bars });
      revealWrap.appendChild(chartWrap);
    }
  }

  if (prior && typeof prior.selectedIndex === "number") {
    for (const b of optBtns) {
      b.disabled = true;
      b.classList.toggle("vote__option--picked", optBtns.indexOf(b) === prior.selectedIndex);
    }
    showReveal(prior.selectedIndex);
    if (onAnswered) onAnswered({ selectedIndex: prior.selectedIndex });
  }
}
