# TODO — Multi-Agent Path Planning and Drone Collision Avoidance (textbook)

Source of requirements: `core idea/core.docx` (extracted to `docs/core-idea.txt`).
Deliverable: a complete textbook as an Overleaf project in `Overleaf/`, plus a zip package
and a compiled PDF.

## How the loop works

1. Pick the first unticked task (top to bottom) whose prerequisites are ticked.
2. Do it. Verify it (compile / run / read). Tick it `[x]` and add a short note.
3. Wait 30 seconds, then start the next iteration.
4. Review/revise tasks repeat per chapter until the reviewer's verdict is **Accept**
   (see the review log at the bottom). A chapter cannot be marked "final" before that.
5. Commit and push after every phase; merge into `main` (single-branch policy).

Legend: `[ ]` open · `[x]` done · `[~]` in progress · `[-]` dropped (with reason)

---

## Phase 0 — Requirements, planning, infrastructure

- [x] 0.1 Extract the training plan from `core.docx` (algorithms, priorities, weekly schedule, capstone, checklist) → `docs/core-idea.txt`
- [x] 0.2 Install the toolchain (TeX Live with TikZ/pgfplots/biber/latexmk; NumPy, SciPy, NetworkX, Matplotlib)
- [x] 0.3 Define audience, voice, learning outcomes and the promise to the reader (`STYLE_GUIDE.md` §1)
- [x] 0.4 Design the table of contents: 8 parts, 25 chapters, 3 appendices, glossary, bibliography, index (`Overleaf/main.tex`)
- [x] 0.5 Create the Overleaf project skeleton (`main.tex`, `searchbook.sty`, folders, `build.sh`, `latexmkrc`, `README.md`)
- [x] 0.6 Write the style guide and chapter template (`STYLE_GUIDE.md`, `docs/chapter-template.tex`)
- [x] 0.7 Define the notation macros and colour/TikZ style system (`searchbook.sty`)
- [x] 0.8 Seed the bibliography with canonical, verified references (`references.bib`)
- [x] 0.9 Verify the skeleton compiles end to end (pdflatex + biber + makeindex) with placeholder chapters — 45 pages, 0 errors; style test (`docs/style-test.tex`) exercises every environment
- [x] 0.10 Commit and push the skeleton; merge into `main` — commit 54a705f + follow-up

## Phase 1 — Front matter

(1.2–1.4 depend on the chapter drafts of Phase 2 and are done after them.)

- [x] 1.1 Title page and copyright/colophon page (`frontmatter/titlepage.tex`, `copyright.tex`; final polish in 7.5)
- [~] 1.2 Preface: who the book is for, prerequisites, how to read it, how it maps to the 12-week plan, conventions (boxes, difficulty stars, priorities), how to run the code — drafted (`frontmatter/preface.tex`, 3 pages, compiles); final check after the chapters are reviewed
- [x] 1.3 Notation and symbols table (complete, consistent with all chapters) — written (4 pages, 102 symbols in 7 groups, compiles); cross-chapter inconsistencies filed in docs/consistency-issues.md for 6.2
- [ ] 1.4 List of algorithms (auto-generated; check titles)

## Phase 2 — Chapter drafts

Each chapter: outline → draft following the template → figures (≥4, TikZ) → worked example with trace table → pseudocode → verified Python → pitfalls → drone-system box → summary → exercises → compile check.

### Part I — Foundations
- [x] 2.01 Ch 1 Planning for Drone Swarms (problem, the four-layer hybrid architecture preview, roadmap, established vs open research) — written and compiled; reviewed and revised (see review log)
- [x] 2.02 Ch 2 The Toolbox (graphs and grids, configuration space, time-indexed paths, kinematics, uncertainty, complexity, priority queues) — done: 23 pages, compiles, self-test passes (7 figures, 7 tables, 10 exercises, solutions, glossary); over the length target, cut candidates noted for review

### Part II — Single-Agent Graph Search
- [x] 2.03 Ch 3 Dijkstra's Algorithm — written and compiled; reviewed and revised (see review log)
- [x] 2.04 Ch 4 A* Search (admissible/consistent heuristics, optimality proof, weighted A*, space-time A*) — written and compiled; reviewed and revised (see review log)
- [x] 2.05 Ch 5 Incremental Search: LPA* and D* Lite — written and compiled; reviewed and revised (see review log)
- [~] 2.06 Ch 6 Anytime Search: ARA* (and Anytime D* pointer) — [~] author running (relaunched after container restart); text 4 lines so far, 0 figure files, code present

### Part III — Multi-Agent Path Finding
- [x] 2.07 Ch 7 The MAPF Problem (conflict types, objectives, complexity, benchmarks) — written and compiled; reviewed and revised (see review log)
- [~] 2.08 Ch 8 Prioritized Planning and Space-Time A* (reservation tables, Cooperative A*, incompleteness) — drafted on Fable (19 pp, compiles, code + self-test); Opus review in progress
- [x] 2.09 Ch 9 Conflict-Based Search (constraint tree, high/low level, optimality, ICBS improvements) — written and compiled; reviewed and revised (see review log)
- [x] 2.10 Ch 10 Bounded-Suboptimal Search: ECBS (focal search, bounds, benchmarks vs CBS) — written and compiled; reviewed and revised (see review log)
- [x] 2.11 Ch 11 M*, Push-and-Swap, Push-and-Rotate — written and compiled; reviewed and revised (see review log)

### Part IV — Local and Reactive Collision Avoidance
- [~] 2.12 Ch 12 Velocity Obstacles (collision cone, relative velocity, time-to-collision, truncation) — drafted on Fable (22 pp, compiles); Opus review in progress
- [x] 2.13 Ch 13 RVO and ORCA (reciprocity, half-planes, linear program, 3D extension) — written and compiled; reviewed and revised (see review log)
- [x] 2.14 Ch 14 Dynamic Window Approach (dynamic window, objective, admissible velocities) — written and compiled; reviewed and revised (see review log)
- [ ] 2.15 Ch 15 Artificial Potential Fields (attractive/repulsive, local minima, oscillation, remedies)

### Part V — Sampling-Based Motion Planning
- [~] 2.16 Ch 16 RRT (sampling, nearest, steer, collision checking, RRT-Connect) — drafted on Fable (20 pp, 1337 lines, compiles); Opus review in progress
- [ ] 2.17 Ch 17 RRT* and Informed RRT* (rewiring, asymptotic optimality, informed ellipsoid sampling)

### Part VI — Tracking and Prediction
- [ ] 2.18 Ch 18 The Kalman Filter (linear-Gaussian model, predict/update, tuning, constant-velocity tracking)
- [x] 2.19 Ch 19 EKF, UKF and Particle Filters — written and compiled; reviewed and revised (see review log)
- [x] 2.20 Ch 20 Trajectory Prediction (constant-velocity baselines, LSTM, Transformers, ADE/FDE, uncertainty) — written and compiled; reviewed and revised (see review log)

### Part VII — Optimization and Control
- [x] 2.21 Ch 21 Model Predictive Control (receding horizon, constraints, QP formulation, collision constraints) — written and compiled; reviewed and revised (see review log)
- [~] 2.22 Ch 22 MILP for Planning (big-M obstacle avoidance, scheduling, when it is too expensive) — drafted on Fable (20 pp, compiles); Opus review in progress
- [~] 2.23 Ch 23 Consensus and Formation Control (graph Laplacian, consensus protocol, formation error, communication radius) — drafted on Fable (23 pp, compiles); Opus review in progress

### Part VIII — Putting It Together
- [ ] 2.24 Ch 24 The Hybrid Collision-Avoidance Architecture (layers, decision logic, safety horizon, reconnection, replanning triggers)
- [ ] 2.25 Ch 25 Evaluating a Hybrid Planner (experiment matrix, metrics, benchmarks, reproducibility, reporting)

## Phase 3 — Reference code and figure generators

- [ ] 3.1 Python reference implementations for every algorithm family (`Overleaf/code/`), each with a passing self-test
- [ ] 3.2 Figure/data generators (`Overleaf/code/figures/`) reproducible from fixed seeds; outputs committed
- [ ] 3.3 A single script `Overleaf/code/run_all.py` that runs all self-tests
- [ ] 3.4 Every listing in the book is an excerpt of a file that runs

## Phase 4 — Back matter

- [x] 4.1 Appendix A: the twelve-week study plan (week → chapters → coding exercise → milestone → completion checklist) — written; reviewed and revised (see review log)
- [ ] 4.2 Appendix B: mathematical refresher (linear algebra, probability, calculus for kinematics, convex optimization, LP/QP/MILP basics)
- [ ] 4.3 Appendix C: hints and solutions to selected exercises (≥2 per chapter)
- [ ] 4.4 Glossary (every bold term of the book)
- [ ] 4.5 Index (≥15 entries per chapter; check for duplicates and synonyms)
- [x] 4.6 Bibliography audit: every citation resolves; every entry is a real, correctly described publication — audited by web search: 162 entries, 158 verified, 4 corrected (author order, 2 truncated titles, 1 entry type), 17 missing page ranges added; none fabricated (docs/bib-audit.md)

## Phase 5 — Peer review and revision (per chapter, repeated until Accept)

Round k for chapter N: reviewer report → required changes applied → compile → re-review.

- [x] 5.01 Ch 1 — review/revise until Accept — Accept (round 2)
- [~] 5.02 Ch 2 — review/revise until Accept — two Opus rounds done, remaining minor items applied; final confirmation pass pending
- [~] 5.03 Ch 3 — review/revise until Accept — two Opus rounds done, remaining minor items applied; final confirmation pass pending
- [~] 5.04 Ch 4 — review/revise until Accept — two Opus rounds done, remaining minor items applied; final confirmation pass pending
- [~] 5.05 Ch 5 — review/revise until Accept — two Opus rounds done, remaining minor items applied; final confirmation pass pending
- [ ] 5.06 Ch 6 — review/revise until Accept
- [~] 5.07 Ch 7 — review/revise until Accept — two Opus rounds done, remaining minor items applied; final confirmation pass pending
- [ ] 5.08 Ch 8 — review/revise until Accept
- [~] 5.09 Ch 9 — review/revise until Accept — two Opus rounds done, remaining minor items applied; final confirmation pass pending
- [~] 5.10 Ch 10 — review/revise until Accept — two Opus rounds done, remaining minor items applied; final confirmation pass pending
- [~] 5.11 Ch 11 — review/revise until Accept — two Opus rounds done, remaining minor items applied; final confirmation pass pending
- [ ] 5.12 Ch 12 — review/revise until Accept
- [~] 5.13 Ch 13 — review/revise until Accept — two Opus rounds done, remaining minor items applied; final confirmation pass pending
- [~] 5.14 Ch 14 — review/revise until Accept — two Opus rounds done, remaining minor items applied; final confirmation pass pending
- [ ] 5.15 Ch 15 — review/revise until Accept
- [ ] 5.16 Ch 16 — review/revise until Accept
- [ ] 5.17 Ch 17 — review/revise until Accept
- [ ] 5.18 Ch 18 — review/revise until Accept
- [~] 5.19 Ch 19 — review/revise until Accept — two Opus rounds done, remaining minor items applied; final confirmation pass pending
- [~] 5.20 Ch 20 — review/revise until Accept — two Opus rounds done, remaining minor items applied; final confirmation pass pending
- [~] 5.21 Ch 21 — review/revise until Accept — two Opus rounds done, remaining minor items applied; final confirmation pass pending
- [ ] 5.22 Ch 22 — review/revise until Accept
- [ ] 5.23 Ch 23 — review/revise until Accept
- [ ] 5.24 Ch 24 — review/revise until Accept
- [ ] 5.25 Ch 25 — review/revise until Accept
- [~] 5.26 Front matter and appendices — review/revise until Accept — two Opus rounds done, remaining minor items applied; final confirmation pass pending

## Phase 6 — Book-level review (whole manuscript)

- [ ] 6.1 Structural review: order of chapters, prerequisites satisfied, redundancy removed, forward/backward references correct
- [ ] 6.2 Consistency review: notation, terminology, algorithm names, agent colours in figures, box usage
- [ ] 6.3 Coverage audit against the training plan: every algorithm, every weekly "Learn" item, every capstone element, every checklist item is taught somewhere (traceability table in Appendix A)
- [ ] 6.4 Accuracy spot-check of all theorems, formulas and complexity tables by a second reviewer
- [ ] 6.5 Readability pass: sentence length, jargon defined, transitions, chapter openings/closings
- [ ] 6.6 Apply book-level revisions and re-review until Accept

## Phase 7 — Copyediting and typesetting

- [ ] 7.1 Spelling and grammar pass (American English), consistent hyphenation and capitalisation of algorithm names
- [ ] 7.2 Typesetting: overfull/underfull boxes, widows/orphans, float placement, figure sizes, table widths, listing lengths
- [ ] 7.3 Captions, labels and cross-references: no `??`, every float referenced
- [ ] 7.4 Hyperlinks, bookmarks and PDF metadata (title, author, subject)
- [ ] 7.5 Front matter finalised (TOC depth, list of algorithms, preface date)

## Phase 8 — Final build, packaging, delivery

- [ ] 8.1 Full clean build with zero errors; record page count and remaining warnings
- [ ] 8.2 Produce `Overleaf/searchbook.pdf`
- [ ] 8.3 Produce the Overleaf package `Overleaf/searchbook-overleaf.zip` (main.tex at the root of the zip) and test that it unzips into a compilable project
- [ ] 8.4 Update `README.md` (repo root and `Overleaf/`) with upload/compile instructions
- [ ] 8.5 Final QA of the PDF: open, check TOC, every chapter has figures/tables/examples/exercises, index and bibliography present
- [ ] 8.6 Commit, push, merge into `main`, remove the working branch (single-branch policy)

---

## Loop log (one line per iteration; each iteration starts 30 s after the previous one finished)

| # | Time (UTC) | Task | Result |
|---|---|---|---|
| 1 | 02:40 | 0.1–0.8 requirements, toolchain, TOC, skeleton, style guide, macros, bibliography | done |
| 2 | 03:00 | 0.9 skeleton compile + style test | 45 pages, 0 errors; every environment renders |
| 3 | 03:05 | 0.10 commit/push skeleton | 54a705f, d6483fc |
| 4 | 03:06 | 2.01–2.08 launch authors for Chapters 1–8 (batch 1 of 4) | lost in container restart at ~03:40 (code/figures survived and were committed) |
| 5 | 03:08 | 4.1, 4.2 launch authors for Appendices A and B | Appendix A draft survived (238 lines); B lost |
| 6 | 03:12 | 1.2 preface | drafted, compiles (3 pages) |
| 7 | 03:15 | 4.6 bibliography audit attempt via Semantic Scholar | egress blocked; web search works and will be used in Phase 4 |
| 8 | 03:45 | relaunch 2.01–2.08, 4.1, 4.2 with "text first" order; autosave to main every 5 min | running |
| 9 | 03:50 | single-branch policy: merged into main, local branch removed | remote branch deletion refused by proxy; delete in GitHub UI |
| 10 | 04:00–12:50 | usage limit hit; all authors stopped (drafts of Ch 1–5, 8 and App. A survived via autosave) | paused until reset |
| 13 | 13:20–13:40 | finishers for Ch 3, 4, 5, 8 and author for Ch 7 all terminated (4x HTTP 500, 1x out of usage credits) | no file damage; drafts intact |
| 14 | 13:50 | fixed two build blockers myself: tcolorbox titles containing commas (global, `searchbook.sty`) and the missing `figures/ch08/idea.tex` | full book compiles: 168 pp, 0 errors |
| 15 | 13:55 | 8.2/8.3 produced `Overleaf/searchbook.pdf` and `Overleaf/searchbook-overleaf.zip` (202 files) from the current state | delivered |
| 24 | 13:00-17:40 | first wave: authors finished Ch 7, 9, 11, 13, 19, 20, 21 (20-24 pp each, all compile); then the session limit hit again (reset 17:40 UTC) before any review completed | 17 drafted files |
| 26 | 09-08 | review loops finished for Ch 1-5, 7, 9-11, 13, 14, 19-21 and App. A (Ch 1 Accept; 14 others: two Opus rounds, minor items applied). All 12 remaining authors (Ch 6, 8, 12, 15-18, 22-25, App. B) stopped by the WEEKLY Fable limit | 15 reviewed |
| 28 | 09-09 08:55 | workflows resumed (cached reviews replay; 12 authors to run). In parallel on Opus: 4.6 bibliography audit via web search (docs/bib-audit.md) and 1.3 notation table (frontmatter/notation.tex) | running |
| 27 | 09-09 08:50 | full build currently fails on partial figures left by interrupted authors (ch12, ch22); resuming the workflows so those authors finish their chapters | resuming |
| 25 | 19:15 | workflows resumed from their run IDs: the seven finished authors replay from cache; Opus reviews of Ch 7, 9, 11, 13, 19, 20, 21 and the review-only passes start; remaining authors (Ch 6, 8, 12, 14-18, 22-25, App B) follow | running |
| 23 | 12:46 | session limit reset; three workflows relaunched from docs/workflows/batches/w1-3.json (Fable authors, Opus reviewers, Essential chapters 16-24 pp) | running |
| 22 | 02:45 | all three workflows failed at launch: session limit (resets 06:00 UTC) - no chapter work possible until then. User: Essential chapters get more space (16-22 pp, up to 24); completeness never sacrificed to length. Script and batch files (docs/workflows/batches/w1-3.json) updated; automatic resume scheduled for 06:07 UTC | paused |
| 21 | 02:35 | user: keep Fable for writing (accuracy), be efficient. Relaunched 3 workflows with docs/workflows/chapter-loop.js: authors on Fable, reviewers/revisers on Opus, 12-16 page cap, max 2 rounds (+1 after Major). W1: Ch 11, 13-18; W2: Ch 19-25, App B; W3: Ch 9, 7, 12, 8, 6 + review-only Ch 1-5, 10, App A | running |
| 20 | 02:27 | user: 35% of weekly Fable limit used in a day. All Fable workflows stopped. New cost-reduced loop (docs/workflows/chapter-loop.js): every agent on Opus, chapters capped at 12-16 pages, at most 2 review rounds (3rd only after a Major verdict) | Ch 10 done; Ch 11, 19, 20 drafted (to be completed on Opus) |
| 18 | 02:15 | status check: Ch 10, 11, 19, 20 being written by the workflows (1.5-2k lines each, in compile-fix); the five standalone authors for Ch 6, 7, 8, 9, 12 died silently at 01:11 with no text | user chose model split: Fable authors, Opus reviews/revisions |
| 19 | 02:16 | workflow scripts patched (review/revise -> Opus); journals monitored to stop/resume each workflow right after its current authors finish; third workflow prepared for Ch 6, 7, 8, 9, 12 | in progress |
| 16 | 14:05 | model switched to Fable 5.1; ultracode on. Specs for Ch 9-25 written (docs/specs/). Authors launched for Ch 6, 7, 8, 9, 12 | running |
| 17 | 14:20 | two Workflows launched: write -> review -> revise -> re-review (max 4 rounds, stop at Accept) for Ch 10, 11, 13-18 and Ch 19-25 + App. B; reviews saved to reviews/ | running |
| 12 | 13:15 | 2.02 Chapter 2 finished; global cleveref fix (aliascnt) in searchbook.sty | Ch 2: 23 pp, 0 errors |
| 11 | 12:55 | specs saved to docs/specs/; finishers launched for Ch 2, 3, 4, 5, 8 (5 in parallel to stay under the limit) | running |

---

## Review log

| Chapter | Round | Verdict | Required changes (summary) | Status |
|---|---|---|---|---|
| Ch 1 | 1-2 | Minor revision (8) -> Accept (1 cosmetic) | see reviews/ch01-round1.md, ch01-round2.md | ACCEPT |
| Ch 2 | 1-2 | Minor revision (10) -> Minor revision (3), applied | see reviews/ch02-round1.md, ch02-round2.md | minor items applied, unreviewed |
| Ch 3 | 1-2 | Minor revision (4) -> Minor revision (2), applied | see reviews/ch03-round1.md, ch03-round2.md | minor items applied, unreviewed |
| Ch 4 | 1-2 | Major revision (13) -> Minor revision (7), applied | see reviews/ch04-round1.md, ch04-round2.md | minor items applied, unreviewed |
| Ch 5 | 1-2 | Minor revision (9) -> Minor revision (2), applied | see reviews/ch05-round1.md, ch05-round2.md | minor items applied, unreviewed |
| Ch 7 | 1-2 | Minor revision (8) -> Minor revision (4), applied | see reviews/ch07-round1.md, ch07-round2.md | minor items applied, unreviewed |
| Ch 9 | 1-2 | Minor revision (11) -> Minor revision (2), applied | see reviews/ch09-round1.md, ch09-round2.md | minor items applied, unreviewed |
| Ch 10 | 1-2 | Minor revision (7) -> Minor revision (2), applied | see reviews/ch10-round1.md, ch10-round2.md | minor items applied, unreviewed |
| Ch 11 | 1-2 | Minor revision (8) -> Minor revision (3), applied | see reviews/ch11-round1.md, ch11-round2.md | minor items applied, unreviewed |
| Ch 13 | 1-2 | Minor revision (10) -> Minor revision (4), applied | see reviews/ch13-round1.md, ch13-round2.md | minor items applied, unreviewed |
| Ch 14 | 1-2 | Minor revision (8) -> Minor revision (3), applied | see reviews/ch14-round1.md, ch14-round2.md | minor items applied, unreviewed |
| Ch 19 | 1-2 | Minor revision (8) -> Minor revision (4), applied | see reviews/ch19-round1.md, ch19-round2.md | minor items applied, unreviewed |
| Ch 20 | 1-2 | Minor revision (12) -> Minor revision (6), applied | see reviews/ch20-round1.md, ch20-round2.md | minor items applied, unreviewed |
| Ch 21 | 1-2 | Minor revision (9) -> Minor revision (3), applied | see reviews/ch21-round1.md, ch21-round2.md | minor items applied, unreviewed |
| App. A | 1-2 | Minor revision (6) -> Minor revision (9), applied | see reviews/appA-round1.md, appA-round2.md | minor items applied, unreviewed |
