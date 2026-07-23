const STORAGE_KEY = "computationalSociologyProgress";

const EMPTY = {
  version: 1,
  lessons: {},
  quizzes: {},
  code: {},
  slides: {}
};

function safeGet() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return structuredClone(EMPTY);
    const parsed = JSON.parse(raw);
    return { ...structuredClone(EMPTY), ...parsed };
  } catch {
    return structuredClone(EMPTY);
  }
}

function safeSet(state) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch {
    /* storage may be disabled — silently ignore in prototype */
  }
}

export function getProgress() {
  return safeGet();
}

export function markLessonStarted(lessonId) {
  const s = safeGet();
  s.lessons[lessonId] = s.lessons[lessonId] || { started: false, completed: false };
  s.lessons[lessonId].started = true;
  safeSet(s);
}

export function markLessonCompleted(lessonId) {
  const s = safeGet();
  s.lessons[lessonId] = s.lessons[lessonId] || { started: false, completed: false };
  s.lessons[lessonId].started = true;
  s.lessons[lessonId].completed = true;
  safeSet(s);
}

export function markQuizAnswered(quizId, { correct, selectedIndex }) {
  const s = safeGet();
  s.quizzes[quizId] = {
    correct: !!correct,
    selectedIndex: selectedIndex,
    at: Date.now()
  };
  safeSet(s);
}

export function clearQuiz(quizId) {
  const s = safeGet();
  if (s.quizzes && s.quizzes[quizId]) {
    delete s.quizzes[quizId];
    safeSet(s);
  }
}

export function markVote(voteId, { selectedIndex }) {
  const s = safeGet();
  s.votes = s.votes || {};
  s.votes[voteId] = { selectedIndex, at: Date.now() };
  safeSet(s);
}

export function getVote(voteId) {
  return safeGet().votes?.[voteId] || null;
}

export function markCodeExecuted(codeId) {
  const s = safeGet();
  s.code[codeId] = { executed: true, at: Date.now() };
  safeSet(s);
}

export function markSlidePosition(lessonId, index) {
  const s = safeGet();
  s.slides[lessonId] = { index: Math.max(0, index | 0), at: Date.now() };
  safeSet(s);
}

export function getSlidePosition(lessonId) {
  return safeGet().slides?.[lessonId]?.index ?? 0;
}

export function resetProgress() {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch { /* ignore */ }
}

export function resetLessonProgress(lessonId, quizIds = []) {
  const s = safeGet();
  delete s.slides[lessonId];
  if (s.lessons[lessonId]) {
    s.lessons[lessonId] = { started: false, completed: false };
  }
  for (const qid of quizIds) {
    delete s.quizzes[qid];
  }
  safeSet(s);
}

export function summarize(course) {
  const s = safeGet();
  const total = course?.sections?.length ?? 0;
  const completed = Object.values(s.lessons).filter((l) => l.completed).length;
  const started = Object.values(s.lessons).filter((l) => l.started && !l.completed).length;
  return { total, completed, started, ratio: total ? completed / total : 0 };
}
