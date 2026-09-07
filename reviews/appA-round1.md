# Review of Appendix A (The Twelve-Week Study Plan) - round 1

Reviewed: `Overleaf/appendices/appA-study-plan.tex` (850 lines), figure
`Overleaf/figures/appA/timeline.tex`, against `STYLE_GUIDE.md` section 9 (A-H) and the
training plan `docs/core-idea.txt`. No spec file `docs/specs/appA.md` exists and the
appendix has no objectives box, so completeness was judged against the training plan and
the appendix's own opening promise ("maps every week to the chapters that teach it, and
adds study notes, a capstone description, a completion checklist and a traceability
table"). There is no `Overleaf/code/appA_*.py`, no `Overleaf/bib/appA-extra.bib` and no
`Overleaf/appendices/glossary/appA-terms.tex`; none is required by any spec, and the
appendix quotes no computed numbers, so step (3) of the review procedure (run the code and
check quoted numbers) does not apply. The one arithmetic claim in the text (`768` cells)
was checked by hand and is right; the one that is wrong (`eight` weeks) is item 1 below.

Build: `cd Overleaf && ./build.sh appA-study-plan` returns 0, no `!` errors, no undefined
citations, no undefined labels belonging to this appendix (the `??` in the PDF are all
`ch:chNN` references to chapters excluded from the single-chapter build, which
`STYLE_GUIDE.md` section 7 permits). Only two overfull boxes, both 0.71 pt in the
`longtable` header (lines 112 and 117), far below the 15 pt threshold.

Length: the appendix itself is PDF pages 22-35 = **14 pages**, inside the 20-page budget.
No cuts are required; there is no padding, and the ~2 pages the new figures below will add
still leave room.

Coverage against `docs/core-idea.txt` is complete and was checked item by item: goal,
target outcome, study load and suggested stack (section A.1); the twelve-week schedule
reproduced verbatim with an added *Read* column (Table A.1); all 27 algorithms of families
A-F with the plan's exact priority tags, including the qualified ones ("Essential for your
planned research", "Awareness to High", "Essential for formation-preserving work")
(Table A.5); the four capstone layers in the plan's words (Table A.2); the five decision
steps (section A.5.2); the five experiment factors and all ten metrics (Table A.3 and the
*Metrics* paragraph); the ten checklist statements (Table A.4); the twelve-item reading
order (Table A.6); and all seven "where research still exists" bullets (the *After Week 12*
paragraph). Nothing from the plan is missing.

## Verdict

**Minor revision.** The appendix is accurate, complete against the training plan, well
written and compiles cleanly. Three factual sentences are wrong or imprecise (items 1-3),
the figure count is 1 where the rubric asks for 4 (item 4), two tables float out of their
sections (item 5) and the book's objectives/summary boxes are missing (item 6). Every fix
is confined to this appendix and to `Overleaf/figures/appA/`; none touches the substance
of the plan.

## Required changes

1. **`sec:appA-timeline`, line 206-207, and the caption of `fig:appA-timeline`, lines
   219-221 - the count of "learn deeply" weeks is wrong.** The text says "eight of the
   twelve weeks go to the three ``learn deeply'' families" and the caption repeats
   "Families A--C ... take eight of the twelve weeks". Both the schedule (Table A.1) and
   the figure itself give family A weeks 1-2, family B weeks 3-5, family C weeks 6-7, i.e.
   2 + 3 + 2 = **seven** weeks; the bars in `Overleaf/figures/appA/timeline.tex` span
   x = 0.06-1.94, 2.06-4.94 and 5.06-6.94, which is 2, 3 and 2 week columns. Fix: write
   "seven of the twelve weeks -- more than half --" in the text and "take seven of the
   twelve weeks" in the caption. (Category A)

2. **`sec:appA-week03`, line 309 (and the *Traps* sentence, lines 322-323) - "edge or
   swap" conflates two conflict types that the book defines separately.** The Focus lists
   "the conflict types (vertex, edge or swap, following, cycle)", but
   `def:ch07-conflicts` in `Overleaf/chapters/ch07-mapf-problem.tex` (following Stern
   et al. 2019) defines *five* types, in which an **edge conflict** is two agents
   traversing the same edge *in the same direction*
   ($\pi_i[t]=\pi_j[t]=u$, $\pi_i[t+1]=\pi_j[t+1]=v$) and a **swapping conflict** is the
   two agents exchanging vertices ($\pi_i[t]=\pi_j[t+1]=u$, $\pi_i[t+1]=\pi_j[t]=v$).
   Merging them will make a reader's Week-3 conflict checker miss the same-direction case,
   which the Week-4 CBS high level then inherits. Fix: write "(vertex, edge, swapping,
   following, cycle)" and add the half-sentence "an edge conflict is the same edge in the
   same direction, a swap is the two agents exchanging ends"; in *Traps*, state the swap
   test as "agent $i$ moves $u \to v$ while agent $j$ moves $v \to u$ over the same step
   $t \to t+1$" instead of "compares $(u,v)$ at $t$ with $(v,u)$ at $t$". (Category A;
   also F, consistency with `ch:ch07`)

3. **`sec:appA-reading`, lines 804-806 - "the layers of the capstone" overstates what the
   first six reading items cover.** The six items are A*, D* Lite, CBS, the MAPF overview,
   VO and ORCA: they are the global planner, the local safety layer and the replanning
   layer, but *not* the prediction layer, whose sources appear only at item 12 (Rudenko
   et al., Alahi et al.) and, for the Kalman filter, nowhere in the plan's reading list.
   Fix: "they are three of the four capstone layers -- the global planner (item 3), the
   local safety layer (items 5-6) and the replanning layer (items 1-2) -- plus the MAPF
   definitions (item 4) that make the conflict re-check precise; the prediction layer's
   sources come later, at item 12." (Category A)

4. **Whole appendix - only one figure where the rubric requires at least four.**
   `fig:appA-timeline` is the only figure; sections A.5 (the capstone) and A.4 (the week
   notes) are the parts of the appendix a reader most needs a picture of, and the appendix
   has 6 pages of budget left. Add at least three TikZ figures, one per file in
   `Overleaf/figures/appA/` (shared styles `sbbox`, `sbflow`, `sbannot`, `sbnode`,
   `sbedge`, colours `sbBlue/sbOrange/sbGreen/sbPurple/sbRed/sbGray`), each referenced
   with `\cref` and captioned with what to notice:
   * `figures/appA/architecture.tex` - the four capstone layers as blocks with the data
     flow and the interfaces of the "Keep the layers separable" notebox on the arrows
     (instance -> time-indexed paths; observations -> predicted trajectory + covariance;
     states + predictions -> velocity; start state -> path). Reference it from
     `sec:appA-layers` next to Table A.2; caption should point out that layer 4 is the
     only one that writes back to the global plan.
   * `figures/appA/decision-logic.tex` - a flowchart of the five steps of
     `sec:appA-logic` with the three triggers named in the text (time to collision below
     threshold, reconnection cost above bound, violated formation/communication
     constraint), and the two switches that make the "avoidance strategy" axis
     (local-only disables layer 4, replan-only disables layer 3).
   * `figures/appA/week-dependencies.tex` - a small DAG of which week's artifact feeds
     which, exactly as the prose already asserts: Week 1 space-time A* -> Weeks 3, 4, 12;
     Week 3 conflict checker -> Weeks 4, 12; Week 6 simulator -> Weeks 7, 10; Week 8 3D
     field -> Week 12; Week 9 filter -> Weeks 10, 12. Reference it from the `pitfall`
     "Moving on with a red test", whose argument it makes visible.
   (Category D)

5. **`tab:appA-checklist` (line 697) and `tab:appA-reading` (line 814) float out of their
   sections.** In the built PDF, section A.6 and its one paragraph are on page 32 but
   Table A.4 lands on page 34, and section A.8's text is on page 33 while Table A.6 lands
   on page 35; the result is a page on which the headings "A.6 Completion checklist" and
   "A.7 Traceability" sit next to each other with neither table. The cause is the
   `longtable` A.5 in between, which is not a float. `searchbook.sty` already loads both
   `float` and `placeins`, so fix either by `\begin{table}[H]` for these two tables or by
   putting `\FloatBarrier` at the end of sections A.6 and A.8; then rebuild and confirm
   each table sits in its own section. (Category G)

6. **No `objectives` box at the start and no `summary` box at the end.** `STYLE_GUIDE.md`
   section 2 (items 2 and 12) makes both mandatory, every chapter of the book has them,
   and both environments exist in `searchbook.sty` (`objectives`, and `summary` with an
   optional title). Fix: after the opening paragraph (line 15) add an `objectives` box
   with 4-6 outcomes, e.g. "choose a twelve-week route through this book and a weekly
   rhythm that fits 6-8 hours", "say for each week what to build and how to tell it
   works", "state the four layers of the capstone and the decision logic that switches
   between them", "design the capstone's experiment matrix and name the metrics it must
   report", "check the book's coverage of the training plan in either direction with the
   traceability table"; and before the *After Week 12* paragraph (line 839) add
   `\begin{summary}[Appendix summary]` with bullets for the three-ability core idea, the
   6-8 h/week rhythm and the milestone rule, the parts that may be compressed (Weeks 7, 8
   and the MILP part of 11) and the ones that may not (1, 4, 6, 9, 12), the four layers,
   and the ten checklist statements as the exit test. (Category F)

## Suggestions

* **The load scale has no light week.** Section A.4 describes the rating as running "from
  `\difficulty{1}` (light) to `\difficulty{3}` (heavy)" and advises "plan lighter weeks
  around heavier ones", but six weeks are rated 3 and none is rated 1. Either rate the two
  weeks the appendix itself says can be halved (Week 7, "do DWA *or* APF"; Week 5, "or
  reproduce an open implementation") as `\difficulty{1}`, or reword the scale as
  "moderate to heavy".
* **Exercises.** The rubric asks for 6-10 graded exercises. I do not require them here: the
  appendix is a plan, not a teaching chapter, its *Exercises* paragraph in each week already
  routes the reader to the graded, `Coding`-marked exercises of the chapters (the marker
  the appendix names does exist, e.g. `\begin{exercise}[\difficulty{3} Coding]` at
  `ch03-dijkstra.tex:1068`, `ch09-cbs.tex:1294`), and inventing appendix exercises would
  duplicate them. If the book-level pass wants an assessment element here, the cheapest
  honest one is a short "self-check" list of six prompts drawn from the *Done when* lines.
* **`tab:appA-layers`, layer 1** is tagged "Weeks 3--5" but its chapters are `ch:ch09` and
  `ch:ch10`, taught in weeks 4-5; week 3 builds prioritized planning and the conflict
  checker. Consider "4--5 (Week 3 builds the conflict checker it needs)".
* **`sec:appA-experiments`, line 649.** Spell out where 768 comes from - "four swarm sizes
  x four intruder counts x four prediction qualities x three strategies x four constraint
  settings" - and say that "and more if computationally feasible" is being counted as a
  fourth level, otherwise a reader who counts 2/4/8 gets 576.
* **Section A.1, *Study load*.** Give the total once (12 weeks x 6-8 h is roughly 75-95
  hours); readers budgeting the plan will want it.
* **Two small precision points in the week notes.** Week 1 *Done when*: "with the zero
  heuristic both searches expand the same nodes as Dijkstra" - add "up to tie-breaking".
  Week 5 *Done when*: "$w = 1$ reproducing CBS exactly" - true of the cost and the returned
  solution, not necessarily of the expansion order; "reproducing CBS's optimal cost" is
  safer. Week 1 *Focus*: Dijkstra's settled-node invariant holds "on graphs with
  non-negative edge costs" - the qualification is already in the algorithm map of
  `ch:ch01` and costs three words here.
* **For the book-level pass, not for this appendix:** `chapters/ch04-astar.tex` currently
  has no Exercises section, yet Week 1 says "the coding exercise of `\cref{ch:ch04}` is the
  deliverable"; and the appendix's descriptions of `ch:ch24` (state machine, safety
  horizon, reconnection) and `ch:ch25` (scenario generator, metric definitions) cannot be
  verified because those chapters are still stubs. Re-check these cross-references once
  those chapters are written.

## What must be kept

The week-by-week structure - **Focus / Build / Done when / Traps / Exercises** - is the
best thing in this appendix and should not be touched. The *Traps* lists are expert-grade
and specific in a way that only someone who has debugged these algorithms writes them: the
D* Lite key modifier `k_m` when the start moves, a low level that returns at the first pop
of the goal and so ignores a later constraint on the goal cell, the focal bound taken from
the current node instead of the minimum over Open, the truncated VO cone being a disc plus
two tangent legs, `R` below the real noise, leakage between training and test trajectories,
linearizing MPC around a stale trajectory. Each is correct and each saves a reader days.
The *Done when* lines are equally valuable because they are falsifiable tests rather than
feelings, and the equality "path cost after every repair equals a fresh A* cost" is exactly
the right correctness oracle for Week 2.

Keep the faithful reproduction of the plan: the schedule table in the plan's own words with
only a *Read* column added, the traceability table covering all 27 algorithms with the
plan's priority tags and its qualifications preserved, the checklist, the reading order and
the "After Week 12" research directions. Keep the `pitfall` on carrying a red test forward
and the `notebox` that tells the reader to use the book's code as an oracle and not as a
starting point - that single instruction is what makes the coding weeks worth anything.
Keep the honesty of Week 10 ("the LSTM did not beat constant velocity on this data" is a
legitimate result) and the warning that a zero collision rate hides near misses. Citations
are correct and verifiable (all 15 keys resolve in `references.bib`; Hagberg 2008,
Panerati 2021, Rudenko 2020, Rawlings-Mayne-Diehl 2017 and Koenig-Likhachev 2002 were
checked against their venues and page ranges), there are 29 index entries with proper
subentries and a `study plan|(`...`|)` range, and the appendix compiles clean at 14 pages.
