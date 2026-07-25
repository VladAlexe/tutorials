/* terminal_git.js — simulator de terminal Git cu STARE REALĂ: fișiere, zone,
   commituri, ramuri, depozit la distanță. Recunoaște comenzile predate la curs,
   răspunde ca Git-ul adevărat, inclusiv la erori și la comenzi în ordine greșită.
   Se refolosește în mai multe secțiuni, cu liste de sarcini diferite (parametri).
   Nu face niciun apel de rețea. Comandă de ajutor în română: `ajutor`. */

export default function terminalGit(gazda, parametri = {}) {
  const dosar = parametri.dosar || "proiect-echipa";
  const P = `~/${dosar}`;
  const sarcini = parametri.sarcini || [];
  const scenariu = parametri.scenariu || null;   // ex. "push-auth"

  // ---- stare ----
  const S = {
    init: false,
    cfg: { name: null, email: null },
    files: {},        // nume -> {exists, tracked, staged, stagedKind, workMod}
    commits: [],      // {id, msg, parent, branch}
    branches: {},     // nume -> id-ul commitului de vârf (sau null)
    head: null,
    remote: null,
    pushed: {}         // ramura -> id
  };
  (parametri.fisiere || []).forEach((n) =>
    S.files[n] = { exists: true, tracked: false, staged: false, stagedKind: null, workMod: false });

  const atins = new Set();
  let linii = [];
  const hexId = () => Math.random().toString(16).slice(2, 9);

  // Pornire dintr-un depozit gata pregătit (pentru secțiunile despre ramuri și push).
  if (parametri.preInit) {
    S.init = true; S.head = "main";
    S.cfg = { name: parametri.nume || "Student", email: parametri.email || "student@example.com" };
    const id0 = hexId();
    S.commits.push({ id: id0, msg: "primul commit", parent: null, branch: "main" });
    S.branches = { main: id0 };
    Object.values(S.files).forEach((f) => { f.tracked = true; });
    atins.add("init"); atins.add("commit"); atins.add("config");
  }
  if (parametri.remote) S.remote = parametri.remote;

  // ---- ajutoare de stare ----
  const stagedFiles = () => Object.entries(S.files).filter(([, f]) => f.staged);
  const notStaged = () => Object.entries(S.files).filter(([, f]) => f.tracked && f.workMod);
  const untracked = () => Object.entries(S.files).filter(([, f]) => f.exists && !f.tracked && !f.staged);
  const tipId = () => S.branches[S.head];
  const commitById = (id) => S.commits.find((c) => c.id === id || c.id.startsWith(id));
  const ancestry = (id) => { const out = []; let c = commitById(id); while (c) { out.push(c); c = c.parent ? commitById(c.parent) : null; } return out; };

  // ---- ieșire ----
  const out = (arr) => arr.forEach((l) => linii.push(l));
  const err = (l) => linii.push("!" + l);

  function statusText() {
    const L = [`On branch ${S.head}`];
    const st = stagedFiles(), ns = notStaged(), ut = untracked();
    if (S.commits.length === 0 && S.branches[S.head] == null) L.push("No commits yet");
    if (st.length) {
      L.push("", "Changes to be committed:");
      st.forEach(([n, f]) => L.push(`  <span class=\"js\">${f.stagedKind === 'add' ? 'new file:' : f.stagedKind === 'del' ? 'deleted:' : 'modified:'}   ${n}</span>`));
    }
    if (ns.length) {
      L.push("", "Changes not staged for commit:");
      ns.forEach(([n]) => L.push(`  <span class=\"er\">modified:   ${n}</span>`));
    }
    if (ut.length) {
      L.push("", "Untracked files:");
      ut.forEach(([n]) => L.push(`  <span class=\"er\">${n}</span>`));
    }
    if (!st.length && !ns.length && !ut.length) L.push("", "nothing to commit, working tree clean");
    return L;
  }

  // ---- dispecer ----
  function ruleaza(raw) {
    const c = raw.trim();
    if (!c) return;
    linii.push(`<span class="pr">${prompt()}</span> ${c}`);

    if (/^(ajutor|help)$/.test(c)) return ajutor();
    if (/^(curata|clear|cls)$/.test(c)) { linii = []; return; }
    if (/^nou\s+(\S+)/.test(c)) { const n = RegExp.$1; S.files[n] = { exists: true, tracked: false, staged: false, stagedKind: null, workMod: false }; out([`am creat fișierul ${n}`]); return; }
    if (/^edit\s+(\S+)/.test(c)) { return editeaza(RegExp.$1); }
    if (!/^git\b/.test(c)) { err(`'${c.split(' ')[0]}' nu este recunoscut. Scrie ajutor.`); return; }

    const g = c.replace(/^git\s+/, "");

    // comenzi care merg fără depozit
    if (/^config\s+--global\s+user\.(name|email)\s+(.+)/.test(g)) { const k = RegExp.$1, v = RegExp.$2.replace(/^["']|["']$/g, ""); S.cfg[k === "name" ? "name" : "email"] = v; atins.add("config"); return; }
    if (/^config\s+user\.(name|email)\s+(.+)/.test(g)) { const k = RegExp.$1, v = RegExp.$2.replace(/^["']|["']$/g, ""); S.cfg[k === "name" ? "name" : "email"] = v; atins.add("config"); return; }
    if (/^config\s+user\.(name|email)\s*$/.test(g)) { const k = RegExp.$1; out([S.cfg[k === "name" ? "name" : "email"] || ""]); return; }
    if (/^init\b/.test(g)) { if (S.init) { out(["Reinitialized existing Git repository in ./.git/"]); return; } S.init = true; S.head = "main"; S.branches = { main: null }; atins.add("init"); out([`Initialized empty Git repository in ${P}/.git/`]); return; }
    if (/^clone\s+(\S+)/.test(g)) { S.init = true; S.head = "main"; S.branches = { main: null }; S.remote = RegExp.$1; atins.add("clone"); out([`Cloning into '${dosar}'...`, "done."]); return; }

    if (!S.init) { err("fatal: not a git repository (or any of the parent directories): .git"); return; }

    if (/^status\b/.test(g)) { atins.add("status"); out(statusText()); return; }
    if (/^add\s+(.+)/.test(g)) { return adauga(RegExp.$1.trim()); }
    if (/^rm\s+--cached\s+(\S+)/.test(g)) { return rmCached(RegExp.$1); }
    if (/^restore\s+--staged\s+(\S+)/.test(g)) { return restoreStaged(RegExp.$1); }
    if (/^restore\s+(\S+)/.test(g)) { return restore(RegExp.$1); }
    if (/^commit\b/.test(g)) { return commit(g); }
    if (/^log\b/.test(g)) { return log(g); }
    if (/^show\s+(\S+)/.test(g)) { return show(RegExp.$1); }
    if (/^branch\s+-D\s+(\S+)/.test(g)) { return delBranch(RegExp.$1, true); }
    if (/^branch\s+-d\s+(\S+)/.test(g)) { return delBranch(RegExp.$1, false); }
    if (/^branch\s*$/.test(g)) { return listBranches(); }
    if (/^switch\s+-c\s+(\S+)/.test(g)) { return switchC(RegExp.$1); }
    if (/^switch\s+(\S+)/.test(g)) { return switchTo(RegExp.$1); }
    if (/^merge\s+(\S+)/.test(g)) { return merge(RegExp.$1); }
    if (/^remote\s+add\s+origin\s+(\S+)/.test(g)) { S.remote = RegExp.$1; atins.add("remote"); return; }
    if (/^remote(\s+-v)?\s*$/.test(g)) { out(S.remote ? [`origin  ${S.remote} (fetch)`, `origin  ${S.remote} (push)`] : []); return; }
    if (/^push\b/.test(g)) { return push(g); }
    if (/^pull\b/.test(g)) { if (!S.remote) { err("fatal: No configured push destination."); return; } out(["Already up to date."]); atins.add("pull"); return; }
    if (/^fetch\b/.test(g)) { if (!S.remote) { err("fatal: No remote repository specified."); return; } out(["Fetching origin"]); atins.add("fetch"); return; }

    err(`git: '${g.split(' ')[0]}' is not a git command. See 'git --help'.`);
  }

  function editeaza(n) {
    const f = S.files[n];
    if (!f || !f.exists) { err(`fișierul ${n} nu există. Creează-l cu: nou ${n}`); return; }
    if (f.tracked || f.staged) f.workMod = true;   // dacă e urmărit sau pregătit, apare o modificare nouă
    out([`am modificat fișierul ${n}`]);
  }

  function adauga(arg) {
    const tinte = arg === "." ? Object.keys(S.files).filter((n) => S.files[n].exists) : [arg];
    let n = 0;
    tinte.forEach((name) => {
      const f = S.files[name];
      if (!f || !f.exists) { err(`fatal: pathspec '${name}' did not match any files`); return; }
      if (!f.tracked && !f.staged) { f.staged = true; f.stagedKind = "add"; f.workMod = false; n++; }
      else if (f.tracked && f.workMod) { f.staged = true; f.stagedKind = "mod"; f.workMod = false; n++; }
      else if (f.staged && f.workMod) { f.workMod = false; n++; }
    });
    if (n) atins.add("add");
  }

  function rmCached(n) {
    const f = S.files[n];
    if (!f) { err(`fatal: pathspec '${n}' did not match any files`); return; }
    f.tracked = false; f.staged = false; f.stagedKind = null;
    out([`rm '${n}'`]);
  }

  function restore(n) {
    const f = S.files[n];
    if (!f || !f.tracked) { err(`error: pathspec '${n}' did not match any file(s) known to git`); return; }
    f.workMod = false;
    atins.add("restore");
  }

  function restoreStaged(n) {
    const f = S.files[n];
    if (!f || !f.staged) { err(`error: pathspec '${n}' did not match any staged file`); return; }
    if (f.stagedKind === "add") { f.staged = false; f.stagedKind = null; }  // redevine untracked
    else { f.staged = false; f.stagedKind = null; f.workMod = true; }        // modificarea revine în working
    atins.add("restore-staged");
  }

  function commit(g) {
    const m = /-m\s+"([^"]*)"|-m\s+'([^']*)'/.exec(g);
    if (!m) { err("aborting commit due to empty commit message. Folosește: git commit -m \"mesaj\""); return; }
    const msg = m[1] ?? m[2] ?? "";
    if (!S.cfg.name || !S.cfg.email) {
      err("*** Please tell me who you are.");
      err('  git config --global user.email "adresa@exemplu.com"');
      err('  git config --global user.name "Numele Tău"');
      return;
    }
    const st = stagedFiles();
    if (!st.length) { out(["On branch " + S.head, "nothing to commit, working tree clean"]); return; }
    st.forEach(([, f]) => {
      if (f.stagedKind === "del") { /* delete */ }
      else { f.tracked = true; }
      f.staged = false; f.stagedKind = null;
    });
    const id = hexId();
    const commit = { id, msg, parent: S.branches[S.head], branch: S.head };
    S.commits.push(commit);
    S.branches[S.head] = id;
    atins.add("commit");
    out([`[${S.head} ${id.slice(0, 7)}] ${msg}`, ` ${st.length} file(s) changed`]);
  }

  function log(g) {
    const tip = tipId();
    if (!tip) { err(`fatal: your current branch '${S.head}' does not have any commits yet`); return; }
    const list = ancestry(tip);
    if (/--oneline/.test(g)) { out(list.map((c) => `<span class="js">${c.id.slice(0, 7)}</span> ${c.msg}${c.id === tip ? '  <span class="c">(HEAD -> ' + S.head + ')</span>' : ''}`)); }
    else { list.forEach((c) => out([`<span class="js">commit ${c.id}</span>${c.id === tip ? '  (HEAD -> ' + S.head + ')' : ''}`, `Author: ${S.cfg.name || '?'} <${S.cfg.email || '?'}>`, "", `    ${c.msg}`, ""])); }
    atins.add("log");
  }

  function show(id) {
    const c = commitById(id);
    if (!c) { err(`fatal: bad revision '${id}'`); return; }
    out([`<span class="js">commit ${c.id}</span>`, `Author: ${S.cfg.name || '?'} <${S.cfg.email || '?'}>`, "", `    ${c.msg}`]);
  }

  function listBranches() {
    Object.keys(S.branches).forEach((b) => out([`${b === S.head ? "* <span class=\"js\">" + b + "</span>" : "  " + b}`]));
    atins.add("branch");
  }

  function switchC(b) {
    if (S.branches[b] !== undefined) { err(`fatal: a branch named '${b}' already exists`); return; }
    S.branches[b] = S.branches[S.head]; S.head = b; atins.add("switch");
    out([`Switched to a new branch '${b}'`]);
  }

  function switchTo(b) {
    if (S.branches[b] === undefined) { err(`fatal: invalid reference: ${b}`); return; }
    S.head = b; atins.add("switch");
    out([`Switched to branch '${b}'`]);
  }

  function delBranch(b, force) {
    if (b === S.head) { err(`error: cannot delete branch '${b}' checked out at '${P}'`); return; }
    if (S.branches[b] === undefined) { err(`error: branch '${b}' not found.`); return; }
    if (!force && S.branches[b] && S.branches[b] !== S.branches[S.head]) {
      err(`error: the branch '${b}' is not fully merged.`);
      err(`Dacă ești sigur, forțează cu: git branch -D ${b}`);
      return;
    }
    delete S.branches[b];
    out([`Deleted branch ${b}.`]);
  }

  function merge(b) {
    if (S.branches[b] === undefined) { err(`merge: ${b} - not something we can merge`); return; }
    const other = S.branches[b], mine = S.branches[S.head];
    if (other === mine) { out(["Already up to date."]); return; }
    // fast-forward simplu dacă ramura mea nu are commituri proprii după punctul de plecare
    S.branches[S.head] = other;   // aducem vârful
    atins.add("merge");
    out([`Updating ${(mine || '').slice(0, 7)}..${(other || '').slice(0, 7)}`, "Fast-forward"]);
  }

  function push(g) {
    if (!S.remote) { err("fatal: No configured push destination. Rulează întâi: git remote add origin <URL>"); return; }
    if (!tipId()) { err("error: src refspec main does not match any (niciun commit de trimis)"); return; }
    if (scenariu === "push-auth") {
      err("remote: Support for password authentication was removed.");
      err("remote: Please use a personal access token instead.");
      err("fatal: Authentication failed for '" + S.remote + "'");
      return;
    }
    if (scenariu === "push-reject") {
      err("! [rejected]        main -> main (fetch first)");
      err("error: failed to push some refs. Rulează întâi: git pull");
      return;
    }
    S.pushed[S.head] = tipId(); atins.add("push");
    out([`To ${S.remote}`, ` * [new branch]      ${S.head} -> ${S.head}`, `branch '${S.head}' set up to track 'origin/${S.head}'.`]);
  }

  function ajutor() {
    out(["Comenzi recunoscute (scrie-le ca la Git):",
      "  git init · git status · git add . · git commit -m \"mesaj\"",
      "  git log --oneline · git show <id> · git restore [--staged] <fisier>",
      "  git branch · git switch -c <ramura> · git switch <ramura> · git merge <ramura>",
      "  git remote add origin <URL> · git push -u origin main · git pull · git fetch",
      "  git config --global user.name \"...\" · git config --global user.email \"...\"",
      "Ajutoare de simulare:  nou <fisier> · edit <fisier> · curata"]);
  }

  // ---- randare ----
  const prompt = () => (S.head && S.init ? `${P} (${S.head})` : P) + " $";

  function render() {
    gazda.querySelector("#tg").innerHTML = linii.map((l) =>
      l.startsWith("!") ? `<div class="er">${l.slice(1)}</div>` : `<div>${l}</div>`).join("");
    const t = gazda.querySelector("#tg"); t.scrollTop = t.scrollHeight;
    gazda.querySelectorAll(".tchip").forEach((ch) => ch.classList.toggle("done", atins.has(ch.dataset.k)));
    gazda.querySelector("#tgp").textContent = prompt();
  }

  gazda.innerHTML = `
    ${sarcini.length ? `<div class="trm__task">${sarcini.map((s) => `<span class="tchip" data-k="${s.cheie}">${s.eticheta}</span>`).join("")}</div>` : ""}
    <div class="trm" id="tg" aria-live="polite"></div>
    <div class="trm__in"><span id="tgp">${P} $</span>
      <input id="tgi" autocomplete="off" spellcheck="false" aria-label="Comandă Git"></div>`;

  const inp = gazda.querySelector("#tgi");
  inp.addEventListener("keydown", (e) => { if (e.key === "Enter") { ruleaza(inp.value); inp.value = ""; render(); } });
  render();
}
