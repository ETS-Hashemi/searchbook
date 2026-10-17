# Lessons from producing a 737-page textbook with agents

Read this when something goes wrong, and once before starting.

## Agents and limits

* **Rate limits kill batches.** Session limits (5-hour) and weekly limits on the strongest
  model stopped every agent at once, several times. Symptoms: all agents fail with 429 or
  stop producing transcript lines. Response: stop launching, wait for the reset time shown
  in the error, then launch a *fresh* workflow scoped to the unfinished items. Resuming a
  workflow run (`resumeFromRunId`) re-ran reviews that had already finished because the
  prompts no longer matched the cache; it cost a whole batch.
* **Container restarts kill agents silently.** Ten authors died with nothing on disk
  because they had planned first and written last. Since then: "write the chapter text
  FIRST, in at most three large writes", a tool-call budget per role, and an autosave
  loop (`scripts/autosave.sh`, started with `setsid nohup`) that commits and pushes
  every 10 minutes. A killed agent then leaves a draft that a finisher completes.
* **Check that agents are alive by their transcripts' modification times**, not by
  waiting. An agent that has not written for 10 minutes is dead or stuck; message it to
  wrap up and report, then launch a finisher if needed.
* **Model split.** Authors on the strongest model (accuracy originates there); reviewers
  and revisers on a cheaper model when quota matters; the accuracy spot-check on the
  strongest model. Tell the user which model does what; they watch their quota.
* **Budgets that worked:** author ≈ 60 tool calls, reviewer ≈ 40, reviser ≈ 50, copyeditor
  ≈ 180 for a whole-book item list; chapters 16–24 pages; ≤ 2 review rounds (+1 after
  Major). Without budgets agents re-read large files repeatedly and render page images
  for no reason.
* **Two agents must never own the same file.** Partition by chapter id, including
  figures/chNN, code/chNN_*, solutions, glossary terms, extra bib files.

## The user's experience

* They see the repository, not the chat. Commit after every step; keep `TODO.md` and its
  loop log current; a day without commits looks like a day without work.
* Answer "how long is left" with a phase list and an estimate; answer "what did you do
  today" from the loop log.
* When they ask for more depth ("give the essential chapters more space"), raise the
  length band in the style guide and tell authors; do not silently cap.
* Warn them, once and clearly, about secrets they push into the repository (an API key in a
  helper script) and about anything only they can do (delete a remote branch the session
  cannot, rotate keys, get a human expert review, decide the license).

## LaTeX

* `tcolorbox` titles with commas break unless written `title={#1}`.
* Theorem-like environments sharing one counter need `aliascnt` so `\cref` names them
  correctly ("Theorem 4.3", not "Definition 4.3").
* Running heads: `\renewcommand{\chaptermark}[1]{\markboth{\@chapapp\ \thechapter.\ #1}{}}`
  inside `\makeatletter`, so appendices read "Appendix A" not "Chapter A".
* `\SetKwFunction` names, `\newcommand` names and labels must be unique across the book;
  prefix them with the chapter topic. Line labels inside algorithms: `alg:chNN-name:step`.
* `\index{}` arguments must sit on one source line.
* pdfLaTeX main memory: thin scatter data to ≤ 1500 points; the full build used 94 % of it.
* `latexmk -g` forces a rebuild; stale logs otherwise hide errors. Single-chapter builds
  via `\includeonly` legitimately report undefined references to other chapters.
* A missing `lmodern.sty` means the Debian package `lmodern`, not `fonts-lmodern`.
* Overleaf: 20 s (free) / 240 s (premium) compile timeout → figure cache (see
  `book-level-passes.md` §8) and `\includeonly` for one chapter at a time.

## Content integrity

* Never fabricate references. Verify every bibliography entry by web search (title, authors,
  venue, year); 4 of 162 needed correction in the drone book and none was invented, because
  authors were told to cite only what they were certain of and to put uncertain additions in
  a per-chapter extra bib file that the audit checks.
* Every number in prose comes from code that runs; reviewers recompute.
* Decide the spelling convention at the start. Converting 2,500 words later worked but
  needed a script with protected macro names, labels, cite keys and paths, and a
  follow-up check for renamed `\SetKwFunction` names and citation keys.
* A review loop catches most errors but not all: the independent accuracy spot-check of
  every theorem found a false proposition and a missing hypothesis after two review rounds.
* A human expert must read the book before publication; say so in the delivery message.

## Git

* One branch (`main`), commit after every step, `git push -u origin main`.
* A crashed `git add` can leave `.git/index.lock`; remove it when no git process runs.
* `pkill -f autosave.sh` in the foreground can kill your own shell; match the exact command
  (`pgrep -f "^bash .*autosave.sh"`).
* The session may not be able to delete remote branches (proxy); tell the user to do it in
  the GitHub UI.
