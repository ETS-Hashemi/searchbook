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
- [ ] 1.3 Notation and symbols table (complete, consistent with all chapters)
- [ ] 1.4 List of algorithms (auto-generated; check titles)

## Phase 2 — Chapter drafts

Each chapter: outline → draft following the template → figures (≥4, TikZ) → worked example with trace table → pseudocode → verified Python → pitfalls → drone-system box → summary → exercises → compile check.

### Part I — Foundations
- [~] 2.01 Ch 1 Planning for Drone Swarms (problem, the four-layer hybrid architecture preview, roadmap, established vs open research) — drafted, compiles (Ch 1, ~20 pp, 6 figures, code + self-test)
- [x] 2.02 Ch 2 The Toolbox (graphs and grids, configuration space, time-indexed paths, kinematics, uncertainty, complexity, priority queues) — done: 23 pages, compiles, self-test passes (7 figures, 7 tables, 10 exercises, solutions, glossary); over the length target, cut candidates noted for review

### Part II — Single-Agent Graph Search
- [~] 2.03 Ch 3 Dijkstra's Algorithm — drafted, compiles (Ch 3, 6 figures, code + self-test); awaiting finisher pass
- [~] 2.04 Ch 4 A* Search (admissible/consistent heuristics, optimality proof, weighted A*, space-time A*) — drafted, compiles (Ch 4, 7 figures); space-time A* section and experiment figure to verify
- [~] 2.05 Ch 5 Incremental Search: LPA* and D* Lite — drafted, compiles (Ch 5, 6 figures, D* Lite + LPA*); finisher pass pending
- [~] 2.06 Ch 6 Anytime Search: ARA* (and Anytime D* pointer) — [~] author running (relaunched after container restart); text 4 lines so far, 0 figure files, code present

### Part III — Multi-Agent Path Finding
- [~] 2.07 Ch 7 The MAPF Problem (conflict types, objectives, complexity, benchmarks) — [~] author running (relaunched after container restart); text 4 lines so far, 8 figure files, code present
- [~] 2.08 Ch 8 Prioritized Planning and Space-Time A* (reservation tables, Cooperative A*, incompleteness) — partial draft (282 lines, ends mid-chapter); needs completion
- [ ] 2.09 Ch 9 Conflict-Based Search (constraint tree, high/low level, optimality, ICBS improvements)
- [ ] 2.10 Ch 10 Bounded-Suboptimal Search: ECBS (focal search, bounds, benchmarks vs CBS)
- [ ] 2.11 Ch 11 M*, Push-and-Swap, Push-and-Rotate

### Part IV — Local and Reactive Collision Avoidance
- [ ] 2.12 Ch 12 Velocity Obstacles (collision cone, relative velocity, time-to-collision, truncation)
- [ ] 2.13 Ch 13 RVO and ORCA (reciprocity, half-planes, linear program, 3D extension)
- [ ] 2.14 Ch 14 Dynamic Window Approach (dynamic window, objective, admissible velocities)
- [ ] 2.15 Ch 15 Artificial Potential Fields (attractive/repulsive, local minima, oscillation, remedies)

### Part V — Sampling-Based Motion Planning
- [ ] 2.16 Ch 16 RRT (sampling, nearest, steer, collision checking, RRT-Connect)
- [ ] 2.17 Ch 17 RRT* and Informed RRT* (rewiring, asymptotic optimality, informed ellipsoid sampling)

### Part VI — Tracking and Prediction
- [ ] 2.18 Ch 18 The Kalman Filter (linear-Gaussian model, predict/update, tuning, constant-velocity tracking)
- [ ] 2.19 Ch 19 EKF, UKF and Particle Filters
- [ ] 2.20 Ch 20 Trajectory Prediction (constant-velocity baselines, LSTM, Transformers, ADE/FDE, uncertainty)

### Part VII — Optimization and Control
- [ ] 2.21 Ch 21 Model Predictive Control (receding horizon, constraints, QP formulation, collision constraints)
- [ ] 2.22 Ch 22 MILP for Planning (big-M obstacle avoidance, scheduling, when it is too expensive)
- [ ] 2.23 Ch 23 Consensus and Formation Control (graph Laplacian, consensus protocol, formation error, communication radius)

### Part VIII — Putting It Together
- [ ] 2.24 Ch 24 The Hybrid Collision-Avoidance Architecture (layers, decision logic, safety horizon, reconnection, replanning triggers)
- [ ] 2.25 Ch 25 Evaluating a Hybrid Planner (experiment matrix, metrics, benchmarks, reproducibility, reporting)

## Phase 3 — Reference code and figure generators

- [ ] 3.1 Python reference implementations for every algorithm family (`Overleaf/code/`), each with a passing self-test
- [ ] 3.2 Figure/data generators (`Overleaf/code/figures/`) reproducible from fixed seeds; outputs committed
- [ ] 3.3 A single script `Overleaf/code/run_all.py` that runs all self-tests
- [ ] 3.4 Every listing in the book is an excerpt of a file that runs

## Phase 4 — Back matter

- [~] 4.1 Appendix A: the twelve-week study plan (week → chapters → coding exercise → milestone → completion checklist) — drafted, compiles (Appendix A, 850 lines)
- [ ] 4.2 Appendix B: mathematical refresher (linear algebra, probability, calculus for kinematics, convex optimization, LP/QP/MILP basics)
- [ ] 4.3 Appendix C: hints and solutions to selected exercises (≥2 per chapter)
- [ ] 4.4 Glossary (every bold term of the book)
- [ ] 4.5 Index (≥15 entries per chapter; check for duplicates and synonyms)
- [ ] 4.6 Bibliography audit: every citation resolves; every entry is a real, correctly described publication

## Phase 5 — Peer review and revision (per chapter, repeated until Accept)

Round k for chapter N: reviewer report → required changes applied → compile → re-review.

- [ ] 5.01 Ch 1 — review/revise until Accept
- [ ] 5.02 Ch 2 — review/revise until Accept
- [ ] 5.03 Ch 3 — review/revise until Accept
- [ ] 5.04 Ch 4 — review/revise until Accept
- [ ] 5.05 Ch 5 — review/revise until Accept
- [ ] 5.06 Ch 6 — review/revise until Accept
- [ ] 5.07 Ch 7 — review/revise until Accept
- [ ] 5.08 Ch 8 — review/revise until Accept
- [ ] 5.09 Ch 9 — review/revise until Accept
- [ ] 5.10 Ch 10 — review/revise until Accept
- [ ] 5.11 Ch 11 — review/revise until Accept
- [ ] 5.12 Ch 12 — review/revise until Accept
- [ ] 5.13 Ch 13 — review/revise until Accept
- [ ] 5.14 Ch 14 — review/revise until Accept
- [ ] 5.15 Ch 15 — review/revise until Accept
- [ ] 5.16 Ch 16 — review/revise until Accept
- [ ] 5.17 Ch 17 — review/revise until Accept
- [ ] 5.18 Ch 18 — review/revise until Accept
- [ ] 5.19 Ch 19 — review/revise until Accept
- [ ] 5.20 Ch 20 — review/revise until Accept
- [ ] 5.21 Ch 21 — review/revise until Accept
- [ ] 5.22 Ch 22 — review/revise until Accept
- [ ] 5.23 Ch 23 — review/revise until Accept
- [ ] 5.24 Ch 24 — review/revise until Accept
- [ ] 5.25 Ch 25 — review/revise until Accept
- [ ] 5.26 Front matter and appendices — review/revise until Accept

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
| 12 | 13:15 | 2.02 Chapter 2 finished; global cleveref fix (aliascnt) in searchbook.sty | Ch 2: 23 pp, 0 errors |
| 11 | 12:55 | specs saved to docs/specs/; finishers launched for Ch 2, 3, 4, 5, 8 (5 in parallel to stay under the limit) | running |

---

## Review log

| Chapter | Round | Verdict | Required changes (summary) | Status |
|---|---|---|---|---|
| — | — | — | — | — |
