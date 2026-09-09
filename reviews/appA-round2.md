# Review of Appendix A (The Twelve-Week Study Plan) - round 2

Reviewed: `Overleaf/appendices/appA-study-plan.tex` (959 lines), its four figure files in
`Overleaf/figures/appA/` (`timeline.tex`, `week-dependencies.tex`, `architecture.tex`,
`decision-logic.tex`), against `STYLE_GUIDE.md` section 9 (A-H) and the training plan
`docs/core-idea.txt`. There is still no `docs/specs/appA.md`, so completeness was judged
against the training plan and the appendix's own `objectives` box (added in round 1). There
is no `Overleaf/code/appA_*.py` and no `Overleaf/bib/appA-extra.bib`; the appendix is a plan
and quotes no computed numbers, so step (3) of the procedure does not apply. The two
arithmetic claims in the text were recomputed by hand: `12 x 6` to `12 x 8` = 72-96 hours
(correct) and `4 x 4 x 4 x 3 x 4 = 768` cells (correct).

**Build.** `cd Overleaf && ./build.sh appA-study-plan` returns 0. No `!` errors, no
undefined citations, no multiply-defined labels. The only undefined references are
`ch:chNN`, `ch:appB` and `ch:appC`, i.e. chapters excluded from the single-chapter build,
which `STYLE_GUIDE.md` section 7 permits. Two overfull boxes, both 0.70782 pt in the
`longtable` header of Table A.1 (log lines 2149, 2154), far below the 15 pt threshold.

**Length.** The appendix runs PDF pages 19-36 of `build/only-appA-study-plan.pdf` (printed
pages 73-90) = **18 pages**, inside the 20-page budget. There is no padding; **no cuts are
required** (category G), and the two figure fixes below do not add a page.

**Round-1 items: all six verified resolved.**

1. *Week count.* Text (line 223) now reads "seven of the twelve weeks -- more than half"
   and the caption "take seven of the twelve weeks (2, 3 and 2)". I re-derived the split
   from Table A.1 and from the bar coordinates in `timeline.tex` (0.06-1.94, 2.06-4.94,
   5.06-6.94 = 2 + 3 + 2 = 7). Correct. The rendered figure puts every bar over the right
   week columns (checked at 110 dpi).
2. *Edge vs swapping conflict.* Week 3 Focus now lists "(vertex, edge, swapping, following,
   cycle)" with the distinguishing half-sentence, and the Traps sentence states the swap as
   "agent $i$ moving $u \to v$ while agent $j$ moves $v \to u$ over the same step
   $t \to t+1$". This matches `def:ch07-conflicts` (`ch07-mapf-problem.tex` lines 198-207)
   and Stern et al. 2019. Correct.
3. *"First six items" sentence* (lines 890-894) rewritten exactly as required. Correct.
4. *Four figures.* Three new TikZ figures exist, one per file, all using the shared styles
   and colours (`sbboxgray`, `sbflow`, `sbannot`, `sbLight*`, all confirmed present in
   `searchbook.sty`), all `\cref`-referenced, all captioned with what to notice. Resolved -
   with two content defects in the new figures, items 2 and 3 below.
5. *Float placement.* Rebuilt and checked page by page: Table A.4 now sits on the same page
   as the A.6 paragraph that introduces it (PDF p.34), Table A.6 with the A.8 text
   (PDF p.36), and no page carries two adjacent section headings with neither table.
   Resolved. One residual drift is noted under Suggestions.
6. *Objectives and summary boxes.* Both present and well made (objectives: 5 outcomes;
   `summary[Appendix summary]`: 5 bullets). Correct.

**Coverage against `docs/core-idea.txt` (category B): complete.** Re-checked item by item:
goal, target outcome, study load, suggested stack (A.1); the twelve-week schedule in the
plan's words plus a *Read* column (Table A.1); all 27 algorithms of families A-F with the
plan's exact priority tags including the qualified ones (Table A.5); the four capstone
layers (Table A.2); the five decision steps (A.5.2); the five experiment factors and all ten
metrics (Table A.3 and the *Metrics* paragraph); the ten checklist statements (Table A.4);
the twelve-item reading order (Table A.6); all seven "where research still exists" bullets
(*After Week 12*). Nothing from the plan is missing.

**Citations (category H): clean.** All 15 keys (`alahi2016social`, `fiorini1998motion`,
`fox1997dwa`, `hagberg2008networkx`, `hart1968formal`, `karaman2011sampling`,
`koenig2002dstarlite`, `lavalle1998rrt`, `lavalle2006planning`, `panerati2021learning`,
`rawlings2017mpc`, `rudenko2020human`, `sharon2015cbs`, `stern2019mapf`,
`vandenberg2011orca`) resolve in `Overleaf/references.bib`; every one is the canonical
source that `STYLE_GUIDE.md` section 8 names for its topic, and each is correctly paired
with its reading-order item. No fabricated reference. **Index (category F):** 30 distinct
entries with proper subentries and a `study plan|(`...`|)` range - well above the minimum
of 15.

## Verdict

**Minor revision.** The appendix is complete against the training plan, honest, unusually
well written, and it compiles clean at 18 pages. Every required change below is local: one
sentence in Week 6, two edits inside the new figure files, one sentence in A.3 plus the
matching summary bullet, an extension of the self-check, and four cosmetic LaTeX items.
None of them touches the substance of the plan or the week-note structure.

## Required changes

1. **`sec:appA-week06`, Week 6 *Focus*, lines 422-426 - the definition of the velocity
   obstacle is stated on the wrong velocity space and contradicts the book's own
   `ch:ch12`.** The appendix says "The velocity obstacle (VO) is the set of *relative*
   velocities that reach the disc within the horizon $\ttc$".
   `chapters/ch12-velocity-obstacles.tex` line 397 defines
   $\VO^{\ttc}_{A|B}(\vel_B) = \set{\vel_A : t_c(\vel_A - \vel_B) \le \ttc}$, i.e. a set of
   $A$'s *own* velocities, and derives the relative form separately as
   $\VO^{\ttc}_{A|B}(\vel_B) - \vel_B = \bigcup_{0 < t \le \ttc} \disc{\pos_{\mathrm{rel}}/t}{R/t}$
   (line 407-408); Fiorini and Shiller 1998 use the same absolute-velocity convention (van
   den Berg et al. 2011 use the relative one, which is why the two conventions must be named
   rather than merged). A reader who takes the appendix's sentence into the Week-6 exercise
   will test candidate velocities against a set that is offset by $\vel_B$. Fix: replace the
   sentence with "The velocity obstacle $\VO^{\ttc}_{A|B}$ is the set of velocities of $A$
   that, if $B$ held its current velocity, would bring the two discs into contact within the
   horizon $\ttc$; subtracting $\vel_B$ gives the relative-velocity form -- the truncated
   cone of \cref{ch:ch12} -- which is the form \orca reasons in." (Category A; also F,
   consistency with `ch:ch12`.)

2. **`Overleaf/figures/appA/week-dependencies.tex` and the caption of
   `fig:appA-week-dependencies` (lines 265-276) - Week 2 is drawn as a dead end, and Week 6
   does not feed the capstone, although the text asserts both.** In the figure, `w2`
   (D\* Lite repair) has exactly one incident edge, the incoming `(w1.north) to[out=70,in=180]
   (w2.west)`; nothing leaves it. But `tab:appA-layers` says Layer 4, the replanning layer,
   *is* \dstarlite/\astar, built in "Weeks 1--2" and used by the Week-12 capstone, and Week
   12's *Build* says "the four layers you already own". Likewise Week 6's *Exercises* says
   "Keep the simulator; Week 7 **and the capstone** reuse it", yet the only edges out of `w6`
   go to `w7` and `w10`, while the caption claims "Only the reuse that the week notes assert
   is drawn". Fix: add two `dep` edges into the capstone box - one from `w2` (e.g.
   `\draw[dep] (w2.east) -- (11.6,6.9) -- (11.6,2.4) -- (11.6,2.7);` routed clear of the
   existing top rail at $y=8.1$) and one from `w6` (e.g. `\draw[dep] (w6.east) -- (2.2,2.4)
   -- (2.2,3.2) -- (9.3,3.2) -- (9.45,2.6);` or any route that does not cross a node). Leave
   the caption's counts as they are: four arrows still leave Week 1 and two leave Week 3.
   (Category D; also F.)

3. **`Overleaf/figures/appA/decision-logic.tex` and the caption of
   `fig:appA-decision-logic` (lines 684-694) - the "replan-only" cut leaves the strategy it
   names undefined.** The dashed red cut at `(-1.05,4.15) -- (1.05,3.85)` severs the *only*
   outgoing "yes" edge of the first diamond, so with layer 3 switched off a detected risk
   leads nowhere and the chart says nothing about what the replan-only strategy does. The
   caption nevertheless calls the two cuts "the avoidance strategy axis of the experiment
   matrix". Fix: draw a dotted bypass from the "yes" branch of `d1` straight to `s4`, e.g.
   `\draw[sbflow,dotted,draw=sbRed,rounded corners=4pt] (0.55,4.0) -- (-3.4,4.0) -- (-3.4,-3.1) -- (s4.west);`
   labelled "replan-only", and add one clause to the caption: "in replan-only the yes branch
   goes straight to step~4 (dotted), in local-only step~4 is never reached and the drone
   stays on the local layer until it can reconnect." (Category D.)

4. **`sec:appA-timeline`, lines 224-226, and the matching summary bullet, line 936 -
   Week 7 is named as the first place to save time although it is the lightest week and its
   *Build* is already the compressed version.** The text says "the places to compress are
   Week~7 (do DWA \emph{or} APF, not both)", but `docs/core-idea.txt` itself specifies
   "Implement DWA **or** APF", Week 7's *Build* (line 456) already reads "One of the two",
   and Week 7 is now the only `\difficulty{1}` week in the appendix - so the advice asks the
   reader to do what the plan already asks, and points at the week with the least to save.
   Fix (either one, and mirror it in the summary bullet): (a) drop Week 7 from the list and
   replace it with a real saving that the week notes support - "Week~5 (benchmark two values
   of $w$ instead of four)" - keeping Week 8 and the MILP part of Week 11; or (b) restore
   Week 7's *Build* to "both DWA and APF" with `\difficulty{2}`, which makes "do one of them"
   a genuine compression again and keeps the load scale running from 1 to 3 only if another
   week is rated 1. Option (a) is the smaller edit. (Category C; also F.)

5. **`sec:appA-checklist`, "A six-question self-check", lines 784-802 - the appendix's only
   assessment element is ungraded and tests only half the plan.** The six prompts come from
   Weeks 1, 2, 3, 4, 5 and 12; nothing tests Weeks 6-11, i.e. local avoidance, sampling-based
   planning, tracking, prediction and control - the entire second half of the plan and three
   of the ten checklist statements. They also carry no `\difficulty{}` grade, unlike every
   exercise in the book, so the rubric's "graded, appropriate range" is not met. I am *not*
   asking for chapter-style exercises here (they would duplicate the chapters' own, as round 1
   correctly argued). Fix: grade the existing six with `\difficulty{}` (items 1 and 3 are
   naturally `\difficulty{1}`, items 2, 4 and 5 `\difficulty{2}`, item 6 `\difficulty{3}`) and
   add two more drawn from the existing *Done when* lines so the count is eight and the
   coverage is complete: one from Week 6 ("draw the VO cone and the \orca half-plane for one
   crossing pair and say which velocities each of them forbids", `\difficulty{2}`) and one
   from Weeks 9-10 ("show the filtered estimate beating the raw measurements on one run, and
   the ADE/FDE table per horizon for constant velocity and the LSTM", `\difficulty{2}`).
   (Category E.)

6. **Lines 211, 262, 274 and 587 - `\cref{sec:appA-...}` prints "Appendix A.3" and
   "Appendix A.5" for *sections* of this appendix.** In the built PDF the four occurrences
   read "Build the capstone architecture (Appendix A.5)" (Table A.1, Week 12), "Appendix A.3
   names the parts that can be compressed" (the `pitfall`), "...which is why Appendix A.3
   refuses to let you compress them" (caption of Figure A.2) and "The architecture and
   decision logic of Appendix A.5" (Week 12 *Focus*). A.3 and A.5 are sections of Appendix A,
   not appendices, so the reader is sent looking for a document that does not exist. Fix: in
   these four places write `Section~\ref{sec:appA-capstone}` / `Section~\ref{sec:appA-timeline}`
   instead of `\cref{...}`. (A book-level alternative is a `\crefname`/`\crefalias` for
   sections after `\appendix` in `main.tex`; `STYLE_GUIDE.md` section 7 forbids editing
   `main.tex` from a chapter pass, so list it in the final report instead of applying it.)
   (Category G; also F.)

7. **`fig:appA-decision-logic` occupies a float page of its own, two pages after the text
   that introduces it.** §A.5.2 and its five enumerated steps are on PDF p.30 (printed 84);
   Figure A.4 lands alone on PDF p.32 (printed 86) with roughly 5 cm of white space above it,
   because the `tikzpicture` is about 13.2 cm tall ($y$ from $-4.9$ to $8.3$) plus a six-line
   caption, which no text page can take. Fix: compress the flowchart vertically so the float
   fits beside its text - set `y=0.8cm` in the `tikzpicture` options and pull the boxes to
   `s1` 6.2, `d1` 4.4, `s2` 2.7, `s3` 1.3, `d2` $-0.6$, `s4` $-2.5$, `s5` $-4.0$ (adjusting
   the three return rails and the two cuts to match), or split the two trigger annotations
   onto one line each. Rebuild and confirm the figure sits on the same page as, or the page
   after, §A.5.2. (Category G.)

8. **Bad hyphenation inside TikZ nodes in all three new figures.** Visible in the rendered
   PDF: "Sensor ob-servations" (`architecture.tex`, node `obs`); "1 Follow the nomi-nal
   CBS/ECBS path", "2 ORCA/DWA: lo-cal avoidance velocity", "formation or communi-cation
   constraint vio-lated" (`decision-logic.tex`); "W3 con-flict checker", "W6 2D avoid-ance
   simulator", "W10 predic-tion models", "W8 3D ob-stacle field" (`week-dependencies.tex`).
   Fix: add `\hyphenpenalty=10000\exhyphenpenalty=10000` to the `font=` key of the `wk`,
   `logicstep` and `src` styles, or widen each `text width` by 2-3 mm, or put an explicit
   `\\` at the intended break ("Sensor\\ observations of the intruder", "W3\\ conflict
   checker", ...). (Category G.)

9. **`sec:appA-checklist`, self-check item 3, line 794 - "(Weeks~3)" should be
   "(Week~3)".** Every other item in the list uses the singular. (Category G.)

## Suggestions

* **Objectives box, line 26-27** promises "say what **each** metric hides", but the *Metrics*
  paragraph (lines 746-749) discusses only two of the ten (collision rate, computation
  time). Either narrow the objective to "say what the headline metrics hide" or add one
  clause for a third (e.g. "sum of costs hides which agent paid the detour, which is what a
  per-agent cost table is for").
* **`tab:appA-layers` drifts one page from its reference.** §A.5.1's introducing sentence is
  on PDF p.29 and the table on p.31, with Figure A.3 in between. `searchbook.sty` loads
  `float`, so `\begin{table}[H]` for `tab:appA-layers` would pin it under the paragraph that
  introduces it. Cosmetic; harmless if left.
* **Acronyms used before they are expanded.** "the QP and MILP solvers of
  \cref{ch:ch21,ch:ch22}" (line 82) uses both abbreviations in §A.1; MILP is expanded only in
  Week 11 (line 563) and QP never (Week 11 spells out "quadratic program" without tying it to
  "QP"). ECBS is likewise used in §A.1 (line 44) without the expansion "Enhanced CBS", which
  appears only in Table A.5. Expanding all three at first use would satisfy
  `STYLE_GUIDE.md` section 3.
* **`fig:appA-architecture`:** the nominal plan reaches "Command executed this cycle" only
  through Layer 3, but step 1 of the decision logic is "follow the nominal path" with no
  local layer involved. Consider a thin direct edge from Layer 1 to the command box labelled
  "no risk: nominal waypoint", which would also make the "local-only / replan-only" switches
  of the notebox readable off this figure.
* **`tab:appA-layers`, Layer 4, Weeks column "1--2, 11".** The 11 is unexplained; a reader
  looking for the replanning layer in Week 11 will not find it. Either drop it or say why
  ("Week 11 adds the formation and communication constraints this layer must re-check").
* **A second `pitfall` box.** `STYLE_GUIDE.md` section 2 item 10 asks for at least two per
  chapter and the appendix has one ("Moving on with a red test"). The material for a second
  one already exists in the week notes - e.g. "Benchmarking on one instance", drawn from the
  Week-5 trap "concluding from one instance" and the Week-10 trap "tuning on the test set".
  Not required, because the twelve *Traps* paragraphs already do this work.
* **Week 6 *Done when*** asserts an experimental outcome ("VO avoids but oscillates or
  detours widely, \orca is smooth and collision-free at the same speeds"). It is the expected
  outcome, but phrasing it as "you should see" rather than as a pass criterion would keep a
  reader from doubting a correct implementation that behaves slightly differently at their
  speeds and radii.
* **For the book-level pass, not for this appendix.** (a) `chapters/ch04-astar.tex` now has
  `\begin{exercise}[\difficulty{3} Coding]` at line 1559, so round 1's concern about Week 1's
  deliverable is resolved. (b) Chapters 6, 15, 16, 17, 18, 23, 24 and 25 are still 4-line
  stubs with no `exercise` environments, so the appendix's instruction "the coding exercise
  of \cref{ch:chNN}" cannot yet be honoured for Weeks 2 (optional), 7, 8, 9, 11 (optional)
  and 12, and its descriptions of `ch:ch24` (state machine, safety horizon, reconnection) and
  `ch:ch25` (scenario generator, metric definitions) cannot be verified. Re-check these
  cross-references once those chapters exist. (c) `frontmatter/notation.tex` is 13 lines and
  lists neither $\ttc$ nor $\rhs$ nor $\Open$/$\Closed$, all of which this appendix uses
  through the `searchbook.sty` macros; the notation table needs them.

## What must be kept

The week-by-week structure - **Focus / Build / Done when / Traps / Exercises** - remains the
best thing in this appendix and must not be touched. Every *Traps* list is expert-grade and
each entry is correct: the $k_m$ key modifier when the start moves, the low level that
returns at the first pop of the goal and so ignores a later constraint on the goal cell, the
focal bound taken from the current node instead of the minimum over \Open, the lower bound
taken from the returned path cost instead of $\fcost_{\min}$, the octile and Euclidean
heuristics turning inadmissible under unit diagonal cost, the space-time search that never
terminates without a time bound, an arrived agent that must stay reserved at its goal, the
truncated cone that is a disc plus two tangent legs, $\mat{R}$ below the real noise, the
rewire that forgets the descendants' costs, leakage between training and test trajectories,
linearizing MPC around a stale trajectory. Each one saves a reader days. The *Done when*
lines are equally valuable because they are falsifiable tests, and "the path cost after every
repair equals a fresh \astar cost" is exactly the right correctness oracle for Week 2.

Keep the faithful reproduction of the plan: the schedule in the plan's own words with only a
*Read* column added, the traceability table covering all 27 algorithms with the priority tags
and their qualifications preserved, the checklist, the reading order with its primary sources,
and the "After Week 12" research directions. Keep the two new content figures for what they
do rather than how they are drawn - Figure A.3's insistence that every interface carries one
named object, and Figure A.2's demonstration of how far a red test travels - and keep the
timeline figure, whose bars, labels and week count I re-verified against Table A.1. Keep the
`pitfall` on carrying a red test forward and the `notebox` that tells the reader to use the
book's code as an oracle and not as a starting point. Keep the honesty of Week 10 ("the LSTM
did not beat constant velocity on this data" is a legitimate result), the warning that a zero
collision rate hides near misses and that a mean computation time hides the missed deadline,
the explicit derivation of the 768 cells, and the total study budget of 72-96 hours. The
objectives and summary boxes added in round 1 are well judged and should stay as they are.

## Response to review (round 2)

All nine required changes are applied. Build: `cd Overleaf && ./build.sh appA-study-plan`
returns status 0, no `!` errors, no undefined citations, no multiply-defined labels; the only
remaining overfull boxes are the two pre-existing 0.70782 pt ones in the Table A.1 longtable
header. The appendix now runs PDF pages 21-37 (17 pages) of
`build/only-appA-study-plan.pdf`. There is no `Overleaf/code/appA_*.py` and no `.dat` file
for this appendix, so steps (3) and the regeneration step do not apply; the two arithmetic
claims (72-96 hours, 768 cells) are unchanged and still correct.

**A. Week 6 Focus: the velocity obstacle was defined on the wrong velocity space.** Applied.
The sentence now reads: "The velocity obstacle (VO) $\VO^{\ttc}_{A|B}$ is the set of
velocities of $A$ that, if $B$ held its current velocity, would bring the two discs into
contact within the horizon $\ttc$; subtracting $\vel_B$ gives the relative-velocity form --
the truncated cone of \cref{ch:ch12} -- which is the form \orca reasons in." I kept the
parenthetical "(VO)" so that the acronym is still expanded at first use in the appendix
(STYLE_GUIDE section 3); nothing else in the reviewer's wording was changed.

**D. Week 2 is a dead end and Week 6 does not feed the capstone
(`figures/appA/week-dependencies.tex`).** Applied. Two `dep` edges were added into the
capstone box: `(w2.east) -- (10.9,6.9) -- (10.9,2.7)` and
`(w6.east) -- (2.2,2.4) -- (2.2,3.2) -- (9.3,3.2) -- (9.45,2.6)`. I used x = 10.9 for the
W2 rail rather than the suggested 11.6 because a descent at 11.6 would have crossed the
existing W1 rail where it drops at x = 11.2; for spacing, that W1 descent was moved from
x = 11.2 to x = 11.5, so the three arrowheads on the top of the capstone box now sit at
10.4, 10.9 and 11.5. The W6 route is the reviewer's, and crosses no node (it does cross the
W5 curve at a near-right angle, as the reviewer's own route does). The caption is unchanged,
so the counts "four arrows leave Week 1 and two leave Week 3" still hold: the new edges leave
Weeks 2 and 6. Verified in the rendered page.

**D. The replan-only cut leaves the strategy undefined
(`figures/appA/decision-logic.tex`).** Applied. A dotted red bypass now leaves the *yes*
branch of the first diamond above the cut and runs down the left-hand side into step 4:
`(0,3.06) -- (-2.7,3.06) -- (-2.7,-3.49) -- (s4.west)`, labelled "replan-only". I routed the
rail at x = -2.7 rather than the suggested -3.4 because x = -3.4 runs through the
`Trigger 2 / Trigger 3` annotation block (the `trig` nodes are `anchor=east` at x = -3.0 with
`text width=3.1cm`, so they occupy x in [-6.1,-3.0]). The caption gained the required clause:
"In replan-only the *yes* branch goes straight to step 4 (dotted); in local-only step 4 is
never reached and the drone stays on the local layer until it can reconnect."

**C. Week 7 named as the first place to save time.** Applied, option (a). The compression
list in section A.3 is now "Week 5 (benchmark two values of $w$ instead of four), Week 8 (use
a library for RRT*) and the MILP part of Week 11"; Week 7's Build and its
`\difficulty{1}` are untouched. The summary bullet mirrors it: "compress Week 5 (two values
of $w$ instead of four), Week 8 ... and the MILP part of Week 11". Week 5's Build does ask
for `w in {1.0, 1.1, 1.5, 2.0}`, so the saving is real, and Week 5 is not on the
"do not compress" list.

**E. The self-check was ungraded and covered only half the plan.** Applied. The paragraph is
now "An eight-question self-check". The six existing prompts carry `\difficulty{}` exactly as
prescribed (items 1 and 3 one star, items 2, 4, 5 two stars, the capstone item three stars),
and two prompts were added from existing "Done when" lines: item 6 (Week 6, two stars) draws
the VO cone and the ORCA half-plane for one crossing pair and says which velocities each
forbids; item 7 (Weeks 9-10, two stars) shows the filtered estimate beating the raw
measurements and the ADE/FDE table per horizon for constant velocity and the LSTM. No
chapter-style `exercise` environments were added; it is still a self-check.

**G. `\cref{sec:appA-...}` printed "Appendix A.3" / "Appendix A.5".** Applied in all four
places (Table A.1 Week 12, the pitfall on carrying a red test forward, the caption of
Figure A.2, and the Week-12 Focus): each now uses `Section~\ref{sec:appA-capstone}` or
`Section~\ref{sec:appA-timeline}`, and the PDF reads "Section A.5" and "Section A.3". The
book-level alternative is **not** applied and is listed here for the book editor: adding
`\crefalias{section}{appendixsection}` (or a `\crefname` switch) after `\appendix` in
`main.tex` would let `\cref` print "Section A.3" for sections of an appendix throughout the
book, after which these four `\ref`s could go back to `\cref`.

**G. Figure A.4 occupied a float page two pages after its text.** Applied. The flowchart was
compressed vertically (the diamonds went from `aspect=2.4` to `aspect=3`, and the boxes moved
to s1 5.60, d1 3.93, s2 1.76, s3 0.35, d2 -1.32, s4 -3.49, s5 -4.90, with the three return
rails now at y = 5.6 / 6.1 / 6.5 and the two cuts at y = 2.82/2.61 and -2.43/-2.64). I did
not use the literal coordinates in the fix: with `y=0.8cm` and s1 at 6.2, d1 at 4.4 the gap
between the bottom of box 1 and the top of the first diamond is about 1 mm, which is not
enough for the connecting arrow (the diamond's half-height is about 8.5 mm at this text
width). The chosen layout keeps every gap between 4.5 and 9.5 mm and is 1.8 cm shorter
overall (11.9 cm instead of 13.7 cm). The figure float is now `[tbh]`; section A.5.2 with its
five steps is on PDF p.32 and Figure A.4 sits at the top of p.33 with section A.5.3 under it,
with no white space anywhere. Requirement met ("the page after section A.5.2").

**G. Bad hyphenation inside TikZ nodes.** Applied.
`\hyphenpenalty=10000\exhyphenpenalty=10000` was added to the `font=` key (braced, so the
key parser keeps the `=` signs) of `wk` and `capbox` in `week-dependencies.tex`, `logicstep`,
`test`, `trig` and `cutlab` in `decision-logic.tex`, and `lay`, `src` and `ifc` in
`architecture.tex`. `pdftotext` of the rebuilt PDF no longer contains "ob-servations",
"nomi-nal", "lo-cal", "communi-cation", "vio-lated", "con-flict", "avoid-ance",
"predic-tion" or "ob-stacle"; no new overfull box appeared.

**G. "(Weeks~3)" in self-check item 3.** Applied; it reads "(Week~3)".

### Suggestions

Taken:

* The objectives box now promises "say what the headline metrics hide", matching the two
  metrics the Metrics paragraph actually dissects.
* `tab:appA-layers` is now `\begin{table}[H]`, so it sits directly under section A.5.1
  instead of drifting; and its Layer-4 Job cell explains the "11" in the Weeks column:
  "(Week 11 adds the formation and communication constraints this re-check must test.)"
* Acronyms expanded at first use: "bounded-suboptimal variant enhanced CBS (ECBS)" in
  section A.1, and "SciPy only for the quadratic program (QP) and mixed-integer linear
  program (MILP) solvers".
* A second `pitfall` box, "Benchmarking on one instance", was added after the Metrics
  paragraph, built from the Week-5 trap ("concluding from one instance") and the Week-10 trap
  ("tuning on the test set"). The appendix now meets STYLE_GUIDE section 2 item 10.
* Week 6's "Done when" no longer asserts an experimental outcome as a pass criterion: the
  falsifiable part (draw the cone and the half-plane, say what each forbids) leads, and the
  comparison is phrased as "you should see ...", with a sentence telling the reader to report
  separation numbers rather than doubt a correct implementation whose speeds and radii differ.

Not taken:

* The extra Layer 1 -> command edge in `fig:appA-architecture`. The only clear route is down
  the far left at about x = -4.7, which widens the picture past the text block (the `inst`
  node already reaches x = -4.2 and the right-hand interface label reaches x = 7.95). The
  point it would make -- that the nominal waypoint is the command when no risk is detected --
  is now carried by the dotted replan-only rail and the extended caption of Figure A.4.
* The book-level `\crefname`/`\crefalias` fix, per the reviewer's own instruction; listed
  above for the editor.

### For the book editor (outside this appendix)

* `main.tex`: a `\crefalias{section}{appendixsection}` after `\appendix` would fix
  "Appendix A.3" for `\cref` to sections of an appendix book-wide.
* Chapters 6, 15, 16, 17, 18, 23, 24 and 25 are still stubs with no `exercise`
  environments, so "the coding exercise of Chapter NN" cannot yet be honoured for Weeks 2,
  7, 8, 9, 11 and 12, and the Week-12 descriptions of `ch:ch24` and `ch:ch25` cannot be
  verified. Re-check once those chapters exist.
* `frontmatter/notation.tex` (13 lines) lists neither `\ttc` nor `\rhs` nor
  `\Open`/`\Closed`, all of which this appendix uses.
