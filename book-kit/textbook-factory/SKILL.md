---
name: textbook-factory
description: End-to-end production of a complete, publication-grade textbook (LaTeX/Overleaf project, PDF, runnable code, figures, exercises, glossary, index, bibliography) from a subject brief, using parallel author agents and a peer-review/revision loop until every chapter is accepted. Use this skill whenever the user wants to write, generate, draft, assemble or finish a textbook, a book of algorithms, lecture notes, a course reader, a monograph or a long technical manual from an outline, a training plan, a syllabus or a Word file; also when they ask to "continue the book", "review the chapters", "build the Overleaf package" or "run the chapter loop". Do not use for a single article, a slide deck or a short report.
---

# Textbook factory

This skill turns a subject brief into a finished textbook the way the 737-page
*Multi-Agent Path Planning and Drone Collision Avoidance* was produced: a LaTeX
project that compiles on Overleaf, every algorithm or method with pseudocode, a
worked example, properties, runnable code and exercises, every chapter reviewed by
an independent reviewer agent and revised until accepted, then book-level audits,
copyediting, packaging. Everything below is what made that work; the reasons are
given so you can adapt them to a different subject without losing the guarantees.

## What you produce

| Deliverable | Where |
|---|---|
| Overleaf project (compiles with pdfLaTeX + Biber + MakeIndex) | `Overleaf/` with `main.tex` at its root |
| Compiled book and Overleaf zip | `Overleaf/<short>.pdf`, `Overleaf/<short>-overleaf.zip` |
| Runnable reference code with self-tests | `Overleaf/code/chNN_*.py`, `Overleaf/code/run_all.py` |
| TODO with every task ticked and a loop log | `TODO.md` |
| Style guide, specs, briefs, reviews, audits | `STYLE_GUIDE.md`, `docs/specs/`, `docs/*.md`, `reviews/` |

## Prerequisites

* A git repository to work in, one branch (`main`), commit rights.
* TeX Live with TikZ/pgfplots/biber/latexmk (`apt-get install texlive-full lmodern` or
  equivalent), Python 3.10+ with NumPy (SciPy if the subject needs it), `pdftotext`, `pdftoppm`.
* Subagents (Claude Code's Agent and Workflow tools) for parallel work. Without them, see
  "Working without subagents" at the end.

## The workflow, phase by phase

Read `references/process.md` once at the start; it is the detailed playbook with
checklists. The short form:

0. **Requirements and infrastructure (do this yourself, not with agents).** Extract the
   brief (Word file, syllabus, outline, plan) into `docs/requirements.md`: topics, their
   priority, the order, the exercises or milestones the reader must reach. Decide audience,
   voice, spelling convention (American or British, decided now, never later), code
   language, chapter length bands. Write `book.json` and run
   `python3 scripts/new_book.py book.json <target-dir>` to scaffold the project
   (LaTeX skeleton, style file, build/package scripts, agents, TODO, briefs). Fill the
   domain parts of `STYLE_GUIDE.md` (canonical sources table, notation macros in
   `Overleaf/textbook.sty`). Build the empty skeleton; it must compile with zero errors
   before any chapter is written. Commit.
1. **Specifications.** One `docs/specs/<id>.md` per chapter (format in
   `references/spec-template.md`): must-cover list, code file and its self-test, figures,
   citations, target length. Specs are what makes 25 parallel authors produce one book.
   Write them yourself or with one agent per part, then read every one.
2. **Chapter drafts.** Launch the chapter loop (`scripts/chapter-loop.js` through the
   Workflow tool, or one `chapter-author` agent per chapter through the Agent tool) in
   batches of 6–8 chapters. Authors write text first, then code, then figures; every
   number in a worked example comes from the code; the chapter must compile alone.
3. **Review and revision loop.** For each chapter: `chapter-reviewer` (rubric A–H in
   `references/review-rubric.md`) → `chapter-reviser` applies every required change and
   appends a response → re-review. Stop at Accept, or after round 2 unless the verdict is
   still Major revision (then one more round). The loop script does this automatically.
4. **Back matter and front matter.** Notation table, glossary (assembled by script from
   per-chapter term files), solutions appendix, study plan or course map, preface,
   title/copyright/about-the-author pages, index audit, bibliography audit (verify every
   entry by web search; never keep an entry you cannot verify).
5. **Book-level passes** (`references/book-level-passes.md`): coverage audit against the
   requirements, consistency pass (notation, terminology, cross-references), book-level
   review by one reviewer agent, accuracy spot-check of every theorem and comparison table by
   a second reviewer, fix passes on disjoint file sets, the mechanical pass (spelling script,
   index line joins, starred paragraphs, short captions), overfull boxes.
6. **Final build, QA, packaging.** `package.sh` renders the figure cache, builds, writes the
   PDF and the Overleaf zip; `scripts/qa.sh` checks errors, undefined references, overfull
   boxes, TOC, index, bibliography, `??` in the text, figures and exercises per chapter.
   Unzip the package into an empty directory and compile one chapter from it.
7. **Deliver.** Commit and push `main`; send the PDF and the zip; tick the last TODO items;
   tell the user what only they can do (delete stale branches, rotate any keys found in the
   repo, read the book themselves, get a human expert review before publishing).

## The loop rules (these are the contract with the user)

* `TODO.md` lists every task; pick the first unticked task whose prerequisites are ticked,
  do it, verify it (compile, run, read), tick it with a note, append a row to the loop log,
  commit and push, wait 30 seconds, repeat. The user watches the repository, not the chat:
  progress that is not committed does not exist for them.
* A chapter is final only when a reviewer's verdict is Accept or its last review's required
  changes have all been applied and answered in the review file.
* Never fabricate a reference, a number, or a result. Numbers come from code; references are
  verified; theorems have proofs or citations.
* Accuracy outranks length. Cuts remove repetition, never required content.

## Roles, models and budgets

Five agent definitions are installed by the scaffolder into `.claude/agents/`:
`chapter-author`, `chapter-reviewer`, `chapter-reviser`, `book-copyeditor`,
`accuracy-checker` (`references/agents.md` explains each). Use the strongest model you
have for authors and for the accuracy checker: those are where wrong statements originate
or get caught. Reviewers and revisers can run on a cheaper model when quota is tight; it
worked, but the accuracy spot-check still found one false theorem that two review rounds had
missed, so do not skip that check.

Give every agent a tool-call budget (author ≈ 60, reviewer ≈ 40, reviser ≈ 50, finisher
≈ 60) and tell it to write the text first in at most three large writes: agents die
(rate limits, container restarts), and a half-written chapter on disk is recoverable, a plan
in an agent's head is not. Run an autosave loop (`scripts/autosave.sh`) that commits and
pushes every 10 minutes for the same reason.

When agents fail with rate-limit errors, stop launching, wait for the reset, then launch a
fresh workflow scoped exactly to what is unfinished. Do not resume the old workflow run:
resuming re-ran finished reviews and wasted a whole batch.

## Checks you run yourself after every batch

* `cd Overleaf && ./build.sh <stem>` for a changed chapter; `./build.sh` for the book.
* `python3 code/run_all.py` after any code change.
* `python3 scripts/check_book.py` (labels referenced, citation keys defined, macro names
  consistent) and `scripts/qa.sh` after a full build.
* Are the agents alive? Look at the modification times of their transcripts, not at
  silence; a stalled agent gets a message asking it to wrap up and report.

## When to read which reference

| Situation | Read |
|---|---|
| Starting a book, or lost in the phases | `references/process.md` |
| Filling the style guide, writing specs | `assets/STYLE_GUIDE.md.template` (what the scaffolder installs), `references/spec-template.md` |
| Launching authors or finishers | `docs/writer-brief.md` and `docs/finisher-brief.md` in the project (from `assets/*.template`), `references/agents.md` |
| Launching reviewers | `references/review-rubric.md` |
| Everything after the chapters are accepted | `references/book-level-passes.md` |
| Something went wrong (limits, restarts, memory, Overleaf timeouts, spelling, git) | `references/lessons.md` |

## Working without subagents (claude.ai or a plain session)

The phases are the same; you play each role yourself, one chapter at a time: write the
chapter following `references/writer-brief.md`, then review it in a fresh context against
the rubric (write the review file), then revise. Keep the TODO and the review files exactly
as the loop would, so the work can be continued by a session that does have subagents.
Expect roughly one chapter per long session.
