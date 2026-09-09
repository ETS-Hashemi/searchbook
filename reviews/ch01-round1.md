# Review of Chapter 1 (Planning for Drone Swarms) - round 1

Reviewed artefacts: `Overleaf/chapters/ch01-introduction.tex` (1073 lines),
`Overleaf/figures/ch01/{scenario,planned-vs-unexpected,architecture,decision,timescales,reading-paths}.tex`,
`Overleaf/code/ch01_scenario.py` and `Overleaf/code/figures/gen_ch01_scenario.py`,
`Overleaf/appendices/solutions/ch01-solutions.tex`, `Overleaf/appendices/glossary/ch01-terms.tex`,
`Overleaf/bib/ch01-extra.bib`, `Overleaf/references.bib`, `Overleaf/frontmatter/{notation,preface}.tex`,
and, for consistency, `Overleaf/chapters/{ch02-toolbox,ch04-astar,ch07-mapf-problem,ch12-velocity-obstacles,ch13-rvo-orca}.tex`.
There is no `docs/specs/ch01.md`, so completeness was checked against the chapter's own
objectives box and against the training plan `docs/core-idea.txt` (sections 1-6).

**Build.** `cd Overleaf && ./build.sh ch01-introduction` returns status 0. No `!` errors, no
undefined citation, no multiply-defined label, and no undefined reference belonging to this
chapter (every `??` in the log and the PDF is a cross-chapter `\cref{ch:chNN}`, expected in a
single-chapter build; the numbers that *do* print for other chapters, e.g. "Chapters 5 to 6"
for `\ref{ch:ch12}`-`\ref{ch:ch15}`, come from stale per-chapter `.aux` files of an earlier
partial build - I checked `build/chapters/*.aux` and this is a build artefact, not a chapter
defect). Two overfull boxes, 11.10 pt (`figures/ch01/timescales.tex`) and 1.15 pt
(`reading-paths.tex`), both under the 15 pt threshold, plus one underfull box in the listing
caption. The chapter occupies printed pages 2-20 (PDF pages 18-36), i.e. **19 printed pages**,
inside the 20-page cap and one page above the style guide's 12-18 band.

**Code.** `python3 code/ch01_scenario.py` prints `self-test passed` in well under a second and
reproduces every quoted number. I re-derived the whole numeric spine independently (see
"What must be kept") and also re-ran the two results the default run does not print: the
conflict fractions of `exr:ch01-coding`(c) and the wait-step minima of `exr:ch01-trace`(d).
One of the six re-derived solution numbers is misrounded; everything else is exact.

## Verdict

**Minor revision.**

The chapter is accurate, complete against the training plan, and unusually well verified: every
number in the example, the trace table, the exercises and the solutions is produced by the
chapter's Python file; the map table reproduces the plan's six groups, 27 entries and priority
tags item by item; all 17 citation keys resolve to genuine, correctly detailed entries. Four
required changes remain, all local and all one-paragraph or smaller: one over-strong safety
claim, one misrounded number in the solutions, one notation clash with Chapter 12 that makes a
cross-reference point at the wrong object, and one paragraph that repeats the preface. Nothing
needs to be re-written or restructured, and no required change is in categories B-E.

## Required changes

1. **`chapters/ch01-introduction.tex`, section `sec:ch01-two-kinds`, lines 141-142.**
   *Category A (technical accuracy).*
   **Problem.** The text asserts flatly that "no algorithm can guarantee safety against an
   object whose motion is unknown". As a universal claim this is false, and a reader who knows
   the reachability / inevitable-collision-state literature will notice: if the intruder's
   speed (and, if you like, acceleration) is bounded, one *can* plan against its reachable set
   and guarantee safety - the reason nobody flies that way is conservatism, not impossibility.
   The book is careful everywhere else, and this sentence is the chapter's justification for
   the whole reactive layer, so it should not overstate.
   **Fix.** Add the qualifying clause, e.g.: "...and no algorithm can guarantee safety against
   an object whose motion is completely unknown; one can only do so by bounding its speed and
   planning against everywhere it could reach, which at a few seconds of horizon blocks so much
   of the airspace that the swarm cannot fly (\cref{ch:ch12} truncates the velocity obstacle
   for exactly this reason)."

2. **`appendices/solutions/ch01-solutions.tex`, solution to `exr:ch01-coding`, part (c).**
   *Category A (numbers must be reproduced by the code).*
   **Problem.** The solution reports "about $0.22$ for $k=2$, $0.60$ for $k=4$ and $0.99$ for
   $k=8$". Running the book's own generator
   (`ch01_scenario.generate(12, 8, k, 0.15, seed)` for `seed` in `range(200)`, then
   `plan_independently` and `find_conflicts`) gives **0.215, 0.595 and 0.995**. The first two
   round correctly; the third does not - 0.995 is 199 scenarios out of 200 and rounds to 1.00,
   not 0.99. A reader who follows the instruction and re-runs the experiment gets a number that
   disagrees with the printed one in the last digit.
   **Fix.** Replace the three values by the exact ones: "about $0.215$ for $k=2$, $0.595$ for
   $k=4$ and $0.995$ for $k=8$ (199 scenarios out of 200)". Keep the following sentence about
   tie-breaking unchanged.

3. **`chapters/ch01-introduction.tex`, section `sec:ch01-decision`, lines 484-490 (definition of
   $\ttc$ and the sentence "\Cref{ch:ch12} computes $\ttc$ from relative position and
   velocity").** *Category F (consistency with the notation and the later chapters).*
   **Problem.** Chapter 1 uses $\ttc$ (i.e. $\tau$) for the *time to collision* and
   $\ttc_{\mathrm{safe}}$ for the safety horizon. Chapter 12 does the opposite: `def:ch12-ttc`
   (line 322) defines the time to collision as $t_c(\vel_{\mathrm{rel}})$ and reserves $\ttc$
   for the *truncation horizon* of a velocity obstacle, $\VO^{\ttc}_{A|B}$ (line 397); Chapter
   13 continues with $\ttc$ as the horizon in $\ORCA^{\ttc}_{A|B}$; and
   `frontmatter/notation.tex` row 129 has to paper over the clash with "horizon of the reactive
   layer; a time to collision in \cref{ch:ch01}". The consequence is a cross-reference that is
   simply wrong: Chapter 12 does *not* compute $\ttc$ from relative position and velocity, it
   computes $t_c$, and a reader who follows the pointer finds the symbol meaning something
   else.
   **Fix.** In `sec:ch01-decision` rename the time to collision to $t_c$ in its three
   occurrences - the defining sentence ("The \textbf{time to collision} $t_c$ of a drone with a
   predicted object is ..."), the risk condition ("$t_c<\ttc_{\mathrm{safe}}$"), and the last
   sentence, which should read "\Cref{ch:ch12} computes $t_c$ from relative position and
   velocity (\cref{def:ch12-ttc}) and uses $\ttc$ for the horizon over which a velocity obstacle
   is truncated." Keep $\ttc_{\mathrm{safe}}$ for the safety horizon: with $t_c$ freed, $\tau$
   then means a *horizon* in Chapters 1, 12 and 13 alike, and `exr:ch01-timescales` needs no
   change. Editor's note (outside this chapter): row 129 of `frontmatter/notation.tex` can then
   be shortened to "$\ttc$ & horizon of the reactive layer & \cref{ch:ch12}".

4. **`chapters/ch01-introduction.tex`, section `sec:ch01-conventions`, lines 824-841 (the
   opening paragraph and the "Conventions" paragraph).** *Category G (padding; the chapter is
   19 pages, above the 12-18 band).*
   **Problem.** These two paragraphs repeat the Preface almost item for item.
   `frontmatter/preface.tex` lines 106-122 already state: every chapter opens with a learning
   objectives box and closes with a summary box and exercises; the five kinds of coloured box
   and their colours; that definitions, examples and theorems share one counter per chapter;
   that exercises are marked with one to three stars and what each star means; that hints and
   solutions for a selection are in `\cref{ch:appC}`; and that algorithms carry a `\priority`
   tag. Preface lines 95-105 additionally give the plan's fast reading path, which `sec:ch01-howto`
   and the top row of `fig:ch01-reading-paths` give again. This is the only clear padding in the
   chapter and it costs roughly two thirds of a page.
   **Fix.** Delete the "Conventions" paragraph (lines 832-841) and shorten the opening
   paragraph (824-830) to the one thing the preface does not say - that every algorithm chapter
   has the same *fixed sequence of sections* (why it matters, the idea in plain words, problem
   statement, pseudocode with walkthrough, worked example with figure and trace table,
   properties with proofs, variants, implementation notes with a listing, the drone box,
   summary, further reading, exercises), so that the reader can find the optimality proof or the
   pitfalls of any algorithm without searching - and add one clause "the conventions of the
   book, including the coloured boxes and the difficulty stars, are described in the preface".
   Keep the "Code files" and "The Python stack" paragraphs untouched: they are chapter-specific
   and carry required content.

## Suggestions

* **Bridge cells and metres.** `sec:ch01-example` works entirely in grid cells ("0.38 cells")
  while `sec:ch01-timescales` and `exr:ch01-timescales` work entirely in SI units (5 m/s, 2 m,
  20 ms), and nothing connects them; a lone reader cannot tell whether 0.38 cells is alarming.
  One sentence in `ex:ch01-scenario` would fix it: "If a cell is 2 m wide, the intruder passes
  0.76 m from the centre of $B$'s cell - well inside the 2 m separation used in
  \cref{sec:ch01-timescales}."
* **Solutions for the numeric exercise.** `\cref{ch:appC}` covers `exr:ch01-classify`,
  `exr:ch01-deadlock`, `exr:ch01-trace`, `exr:ch01-horizon` and `exr:ch01-coding` but not
  `exr:ch01-timescales`, which is the one purely numeric exercise a reader alone cannot check.
  Adding it costs four lines: (a) 0.1 m, 2.5 m, 15 m; (b) $\ttc_{\mathrm{safe}} = 10\times20$ ms
  $=0.2$ s, and with a closing speed of $5+3=8$ m/s the risk is detected at
  $2 + 8\cdot 0.2 = 3.6$ m; (c) at 30 s a constant-velocity prediction is worthless and almost
  every distant object would trigger avoidance.
* **Summary bullet, `sec:ch01-summary`.** "twenty-seven algorithms in six groups" counts table
  *rows*; the row "Push-and-Swap, Push-and-Rotate" names two algorithms. Write "twenty-seven
  entries" or split the row.
* **`fig:ch01-reading-paths`.** Both the caption and `sec:ch01-howto` say the first six items of
  the top row are the highest priority, but nothing in the drawing marks them. A brace or a
  shaded band over nodes `f0`-`f5` would make the figure carry that statement itself.
* **`tab:ch01-properties`, "Real-time" row.** "such methods do not search for a route" is a
  little loose - DWA does search, over a discretised set of velocities (as the same cell then
  says). Consider "they search over a bounded set of velocities rather than over routes".
* **`sec:ch01-layers`, layer 1.** CBS is called "optimal" without naming the objective, while
  `tab:ch01-properties` correctly says "for the sum of costs". Add the three words here too.
* **Book-level, not this chapter.** `appendices/glossary.tex` is still the Phase-7 placeholder
  and does not `\input` `appendices/glossary/ch01-terms.tex`, so this chapter's 16 glossary
  entries are currently orphaned. Worth noting in the book-level task list.
* **Cosmetic LaTeX.** The 11.10 pt overfull box comes from the long band label "sensing,
  tracking and prediction update (Kalman filter, LSTM)" in `figures/ch01/timescales.tex`;
  breaking it over two lines would clear it. Both boxes are under the 15 pt threshold, so this
  is optional.

## What must be kept

The numeric spine of this chapter is exemplary and must survive any revision. I re-derived every
quoted value independently of the chapter's code: the intruder speed
$\lVert(-0.54,-0.38)\rVert = 0.66030$; the $t=6$ position $(7.76,5.22)$ and separation
$0.38210$ from the centre of $B$'s cell; the continuous closest approach at
$t^{*}=15.39/2.5160=6.11685$ with distance $0.33413$; the sums of costs 25 and 26 and both
makespans (10 when $C$ waits, 11 when $A$ waits); the horizon positions $(3.44,2.18)$,
$(2.90,1.80)$, $(0.74,0.28)$ at distances 0.6826, 0.6708 and 0.3256; the wait-step minima
0.7169 ($t=7$), 0.9767 ($t=7$) and 1.0555 ($t=8$), hence three wait steps; and the conflict
fractions 0.215 / 0.595 / 0.995. Every one matches (only the last is misrounded in the
solutions, item 2). Table 1.1 was spot-checked cell by cell and is exact to two decimals. The
listing `lst:ch01-conflicts` is a verbatim `diff`-checked excerpt of `code/ch01_scenario.py`,
and the default horizon claim in `exr:ch01-horizon` ("makespan plus one, $t=11$") matches the
code exactly.

The citations are clean: all 17 keys resolve in `references.bib`, `bib/ch01-extra.bib` is empty,
and I checked every entry's authors, venue, volume, pages and year against my own knowledge -
Dijkstra 1959 (Numer. Math. 1:269-271), Hart-Nilsson-Raphael 1968 (IEEE T-SSC 4(2):100-107),
Kalman 1960 (J. Basic Eng. 82(1):35-45), Fox-Burgard-Thrun 1997 (IEEE RAM 4(1):23-33),
Fiorini-Shiller 1998 (IJRR 17(7):760-772), LaValle 1998 (TR 98-11), Koenig-Likhachev 2002 (AAAI
476-483), van den Berg et al. 2011 (ISRR, STAR 70:3-19), Sharon et al. 2015 (AIJ 219:40-66),
Stern et al. 2019 (SoCS 151-158), Hochreiter-Schmidhuber 1997, Vaswani et al. 2017,
Hagberg et al. 2008, Panerati et al. 2021 (IROS 7512-7519), plus the three textbooks. Nothing is
fabricated, and the history box's dates (1959, 1960, 1968, 1997, 1998, 2002, 2011, 2012/2015,
1997, 2017) are all right.

Completeness against the training plan is total and should not be trimmed. `tab:ch01-map`
reproduces groups A-F, all 27 entries and every priority tag exactly as the plan states them
(including "Awareness--High" for the Transformer); `tab:ch01-weeks` reproduces all twelve weeks
with the right chapters; `sec:ch01-research` reproduces all seven research directions and the
ten metrics; the reading order, the capstone's four layers and its five-step decision logic all
match. All six chapter objectives are met.

Pedagogically, the strongest parts are the two-kinds-of-trouble framing (Definitions 1.1 and
1.2 with `fig:ch01-planned-vs-unexpected` showing them side by side), the key-idea box that
states the thesis of the book in one sentence, the architecture figure with every interface
labelled by what it carries, the five-step decision loop with its two "keep going" back-edges,
and the logarithmic time-scale figure with its "distance flown meanwhile" row - which turns an
abstract layering argument into a physical one. The two pitfall boxes are both worth their
space, especially "Numbers on a logarithmic axis are not measurements", which is exactly the
kind of honesty a lone reader needs. Keep the trace table and the `dronebox` of interfaces
verbatim; later chapters depend on them.

Finally, the mechanics: six figures (style guide asks four), all `\cref`-referenced, all built
from the shared `sb*` styles with a consistent colour code for the four layers and a legend;
five tables in `booktabs`; 54 index entries (minimum 15); eight exercises spread
1/1/2/2/2/2/1/3 with a genuine difficulty-3 coding task whose self-test criteria are spelled
out; a build with no errors and no undefined chapter-local reference. The week-1 coding
exercise of the plan ("implement grid A*, add time as a state variable") correctly lives in
Chapter 4, not here - Chapter 1 is parenthetical in week 1 and its own generator exercise is
the right assignment for an introduction.

## Response to review (round 1)

All four required changes are applied, together with six of the eight suggestions. Nothing
listed under "What must be kept" was touched: the numeric spine, the trace table, the map and
week tables, the research directions, the `dronebox`, the citations and the figure set are
unchanged except where a required change or an accepted suggestion demanded it. The chapter
still builds with status 0 and no errors, `python3 code/ch01_scenario.py` still prints
`self-test passed`, and the chapter still occupies 19 printed pages.

### Required changes

1. **Over-strong safety claim (`sec:ch01-two-kinds`).** Applied. The sentence now reads
   "...and no algorithm can guarantee safety against an object whose motion is *completely
   unknown*; one can only do so by bounding its speed and planning against everywhere it could
   reach, which at a horizon of a few seconds blocks so much of the airspace that the swarm
   cannot fly (`\cref{ch:ch12}` truncates the velocity obstacle for exactly this reason)."
   The reachability escape hatch and the reason nobody uses it are both named, and the
   forward pointer to the truncated velocity obstacle is in place.

2. **Misrounded conflict fractions (`appendices/solutions/ch01-solutions.tex`,
   `exr:ch01-coding`(c)).** Applied. I re-ran the experiment before editing
   (`generate(12, 8, k, 0.15, seed)` for `seed in range(200)`, then `plan_independently` and
   `find_conflicts`) and reproduced the reviewer's counts exactly: 43/200, 119/200, 199/200.
   The text now reads "about $0.215$ for $k=2$, $0.595$ for $k=4$ and $0.995$ for $k=8$
   ($199$ scenarios out of $200$)". The following sentence about tie-breaking is untouched.

3. **Notation clash with Chapter 12 (`sec:ch01-decision`).** Applied exactly as specified. The
   time to collision is now $t_c$ in all three places - the defining sentence, the risk
   condition $t_c<\ttc_{\mathrm{safe}}$, and the cross-reference, which now reads
   "\Cref{ch:ch12} computes $t_c$ from relative position and velocity (\cref{def:ch12-ttc}) and
   uses $\ttc$ for the horizon over which a velocity obstacle is truncated."
   $\ttc_{\mathrm{safe}}$ is kept for the safety horizon, so $\tau$ now means a horizon in
   Chapters 1, 12 and 13 alike and `exr:ch01-timescales` needed no change. `\ttc` survives in
   this chapter only in $\ttc_{\mathrm{safe}}$ (lines in `sec:ch01-decision` and
   `exr:ch01-timescales`) and in the new clause naming the truncation horizon. The editor's
   note about row 129 of `frontmatter/notation.tex` is **not** acted on here: front matter is
   outside this chapter's file set, so it is left for the book-level pass.
   `\cref{def:ch12-ttc}` prints `??` in a single-chapter build like every other cross-chapter
   reference; it resolves in the full book (the label is at `ch12-velocity-obstacles.tex:321`).

4. **Padding that repeats the preface (`sec:ch01-conventions`).** Applied. The
   `\paragraph{Conventions.}` paragraph is deleted in full. The opening paragraph is rewritten
   around the one thing the preface does not say - the *fixed sequence of sections* of every
   algorithm chapter - and ends with the clause "The conventions of the book, including the
   coloured boxes and the difficulty stars of the exercises, are described in the preface."
   The "Code files" and "The Python stack" paragraphs are untouched.
   Note on length: the chapter is still 19 printed pages. The deletion frees about two thirds
   of a page, but required change 1 and the accepted suggestions add back a comparable amount,
   and the last chapter page is full, so no page is saved. No required or kept content was
   trimmed to chase the 12-18 band.

### Suggestions

* **Bridge cells and metres.** Applied. `ex:ch01-scenario` now adds: "If a cell is $2$~m wide,
  the intruder passes $0.76$~m from the centre of $B$'s cell---well inside the $2$~m separation
  used in \cref{sec:ch01-timescales}."
* **Solution for `exr:ch01-timescales`.** Applied. A new `solution` block gives (a) 0.1 m,
  2.5 m, 15 m; (b) $\ttc_{\mathrm{safe}}=10\times20\ \mathrm{ms}=0.2$ s, closing speed
  $5+3=8$ m/s, risk declared at $2+8\times0.2=3.6$ m; (c) why a 30 s horizon is useless with a
  constant-velocity prediction. It is inserted in exercise order, before `exr:ch01-coding`.
* **Summary bullet.** Applied: "twenty-seven **entries** in six groups".
* **`fig:ch01-reading-paths`.** Applied. A dashed purple band is drawn behind nodes `f0`-`f5`
  and the row label now reads "Fast path: the training plan's reading order (shaded: the six
  highest-priority chapters)", so the drawing carries the statement itself. Checked in the
  rendered PDF (page 33 of the single-chapter build): the band clears node `f6` and the row
  below it.
* **`tab:ch01-properties`, "Real-time" row.** Applied: "such methods search over a bounded set
  of velocities rather than over routes, which is why they can run at tens of hertz".
* **`sec:ch01-layers`, layer 1.** Applied: conflict-based search "is optimal **for the sum of
  costs**".
* **Cosmetic LaTeX (`figures/ch01/timescales.tex`).** Applied. The long green-band label is
  broken over two lines, which clears the 11.10 pt overfull box; the two remaining overfull
  boxes in the chapter are 2.64 pt and 2.26 pt. While checking the rendered figure I also found
  that the blue band's label "global swarm planning (CBS, ECBS): seconds" was anchored *inside*
  its own rectangle, so the box border cut through the word "planning"; the label is now
  anchored above the band, matching the other three.
* **Book-level: `appendices/glossary.tex` placeholder.** Not acted on. It is outside this
  chapter's file set (the brief forbids editing files other than the chapter's own), so the
  orphaned `ch01-terms.tex` remains a book-level task.

### Verification after revision

* `cd Overleaf && ./build.sh ch01-introduction` - status 0, no `!` errors, no undefined
  citation, no multiply-defined label; every undefined reference is a cross-chapter
  `ch:chNN`/`ch:appX`/`def:ch12-ttc`. No overfull box above 15 pt.
* `python3 code/ch01_scenario.py` - `self-test passed`; the printed scenario still matches the
  chapter (speed 0.66 cells/step, $t=6$ encounter at 0.38 cells, vertex conflict $A$/$C$ at
  $(3,3)$, $t=4$).
* No Python file was changed, so no `.dat` file and no generated figure needed regenerating
  (`code/figures/gen_ch01_scenario.py` writes `figures/ch01/scenario.tex`, which is unchanged
  and still consistent with the code).
* Every number quoted in the chapter, the trace table, the exercises and the solutions was
  re-checked against the code; the only number that changed is the one required change 2 asked
  for, and it is now the exact value the generator produces.
* Build note (pre-existing, book-level, not a chapter defect): a *second* `./build.sh
  ch01-introduction` run over an existing `build/only-ch01-introduction.aux` intermittently
  reports status 12 with "File ended while scanning use of `\@newl@b`" at a varying line of that
  `.aux`, while still writing a correct PDF. Deleting `build/only-ch01-introduction.aux` before
  the run always gives status 0. The same message appears in the stored build logs of
  ch02, ch04, ch08, ch10, ch11, ch15, ch18 and ch21, so it is a property of the build
  directory, not of this chapter. The final build for this revision was made from a clean
  `.aux` and is status 0 with no errors.
