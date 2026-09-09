# Review of Chapter 1 (Planning for Drone Swarms) - round 2

Reviewed artefacts: `Overleaf/chapters/ch01-introduction.tex` (1070 lines),
`Overleaf/figures/ch01/{scenario,planned-vs-unexpected,architecture,decision,timescales,reading-paths}.tex`,
`Overleaf/code/ch01_scenario.py` and `Overleaf/code/figures/gen_ch01_scenario.py`,
`Overleaf/appendices/solutions/ch01-solutions.tex`, `Overleaf/appendices/glossary/ch01-terms.tex`
(and the merged `Overleaf/appendices/glossary.tex`), `Overleaf/bib/ch01-extra.bib`,
`Overleaf/references.bib`, `Overleaf/frontmatter/{notation,preface}.tex`, `docs/chapter-template.tex`,
and, for consistency, `Overleaf/chapters/{ch02-toolbox,ch04-astar,ch07-mapf-problem,ch09-cbs,
ch12-velocity-obstacles,ch24-hybrid-architecture}.tex`.
There is still no `docs/specs/ch01.md`, so completeness was checked against the chapter's own
objectives box and against the training plan `docs/core-idea.txt` (sections 1-6).

**Build.** `cd Overleaf && ./build.sh ch01-introduction` (from a clean
`build/only-ch01-introduction.aux`) returns status 0. No `!` errors, no undefined citation, no
multiply-defined label, and no undefined reference that belongs to this chapter: every `??` in
the log and the PDF is a cross-chapter `ch:chNN` / `ch:appX` / `def:ch12-ttc`, expected in a
single-chapter build (the *wrong* chapter numbers that do print, e.g. "Chapter 6" for
`\cref{ch:ch12}`, come from stale `build/chapters/*.aux` files of an earlier partial build, not
from this chapter). Two overfull boxes remain, 2.64 pt and 2.26 pt, both far under the 15 pt
threshold, plus two underfull boxes in a caption and in the listing. The chapter occupies
printed pages 2-20 (PDF pages 20-38 of `build/only-ch01-introduction.pdf`), i.e. **19 printed
pages**, inside the 20-page cap; nothing in it is padding, so no cut is required.

**Code.** `python3 code/ch01_scenario.py` prints `self-test passed` in 0.14 s and reproduces
every number the chapter quotes. I re-derived the whole numeric spine independently of the
chapter's text (details under "What must be kept"), including the two results the default run
does not print: the wait-step minima of `exr:ch01-trace`(d) and the conflict fractions of
`exr:ch01-coding`(c). Everything matches to the printed precision, the misrounding of round 1
included, which is now fixed.

**Round-1 items.** All four required changes of `reviews/ch01-round1.md` are genuinely resolved
and are not re-raised:
1. The universal safety claim in `sec:ch01-two-kinds` (lines 139-145) now carries the
   reachability qualification and the reason nobody flies that way, with the forward pointer to
   the truncated velocity obstacle of \cref{ch:ch12}.
2. `appendices/solutions/ch01-solutions.tex`, `exr:ch01-coding`(c) now reads
   $0.215 / 0.595 / 0.995$ ($199$ of $200$). I re-ran the experiment
   (`generate(12,8,k,0.15,seed)`, `seed in range(200)`) and got exactly 43, 119 and 199 out of
   200.
3. The $\ttc$ / $t_c$ clash with \cref{ch:ch12} is gone: `sec:ch01-decision` defines the time to
   collision as $t_c$, the risk condition is $t_c<\ttc_{\mathrm{safe}}$, and the cross-reference
   now points at `def:ch12-ttc`, which does exist (`ch12-velocity-obstacles.tex:321`) and does
   define $t_c$. This also agrees with row 128 of `frontmatter/notation.tex` and with `def:ch24-inside`.
4. The `Conventions` paragraph that repeated the preface is deleted; the surviving opening
   paragraph of `sec:ch01-conventions` says only what the preface does not (the fixed section
   sequence) and hands the rest to the preface.

Two new items remain, both local, both consistency defects that a lone reader will trip over
because they concern claims and symbols that point *out* of this chapter.

## Verdict

**Minor revision.**

There is no required change in categories A-E. The technical content is correct as far as I can
check it: the two definitions match \textcite{stern2019mapf} and \cref{ch:ch07}; the property
descriptions (completeness, strong completeness, probabilistic completeness, optimality,
asymptotic optimality, bounded suboptimality, anytime, incremental, real-time) are each stated
with the qualification that makes them true; the history dates (1959, 1960, 1968, 1997, 1998,
2002, 2011, 2012/2015, 1997, 2017) are all right; every one of the 27 map entries carries the
priority the plan gives it; and every number in the example, the trace table, the exercises and
the solutions is reproduced by `code/ch01_scenario.py`. The two required changes below are one
sentence and one symbol respectively.

## Required changes

1. **`chapters/ch01-introduction.tex`, `sec:ch01-map`, line 613: "Every chapter repeats the
   priority tag of its algorithm at the start".** *Category F (consistency with the other
   chapters).*
   **Problem.** This is not true of the book as it stands, and it is a promise the reader will
   act on. `\priority` occurs in exactly three chapter files besides this one - `ch05` (2),
   `ch11` (2) and `ch13` (2) - and in none of them at the start of the chapter. The chapters of
   the algorithms the plan calls *Essential* do not carry the tag at all: `ch04` (\astar),
   `ch09` (\cbs), `ch10` (\ecbs), `ch12` (VO), `ch18` (Kalman), `ch20` (LSTM), `ch21` (MPC) and
   `ch23` (consensus) contain no `\priority` command. `docs/chapter-template.tex` does not ask
   for one either, and the preface (line 119) makes only the weaker claim that a priority "is
   shown as a tag such as `\priority{Essential}`". A reader who opens \cref{ch:ch04} looking for
   the tag this sentence promises finds nothing.
   **Fix (inside this chapter's file set).** Replace the clause with one that describes what the
   book actually does, e.g.: "The priority tags of the plan are collected here, in
   \cref{tab:ch01-map}, and the twelve-week schedule of \cref{sec:ch01-howto} tells you when to
   read each chapter." *Editor's alternative, outside this chapter:* if the intended convention
   is that every algorithm chapter opens with its tag, keep the sentence and add the missing
   `\priority{...}` line to the 21 chapters that lack it as a book-level task; the sentence must
   not stay as it is while the chapters are silent.

2. **`chapters/ch01-introduction.tex`, `sec:ch01-decision`, lines 492 and 494, and
   `exr:ch01-timescales`, line 1041 (plus `appendices/solutions/ch01-solutions.tex`, line 88):
   the safety horizon $\ttc_{\mathrm{safe}}$.** *Category F (notation consistency; the same class
   of defect as round-1 item 3, in the other direction).*
   **Problem.** \Cref{ch:ch24}, which this section explicitly forwards to ("\cref{ch:ch24} gives
   the full treatment, with the state machine, the triggers, the constraints"), calls the same
   quantity $\tau_h$: `def:ch24-inside` (line 392) defines "inside the safety horizon $\tau_h$"
   and the parameter table at line 355 lists "$\tau_h$ = 3 = safety horizon = \orca horizon
   $\ttc$". Chapter 24 never writes $\ttc_{\mathrm{safe}}$ and Chapter 1 never writes $\tau_h$,
   so the book now has two symbols for one defined term, and `frontmatter/notation.tex` has a
   row for neither (it has $\ttc$ = "horizon of the reactive layer" and $t_c$, but no safety
   horizon). The chapter's own $t_c$ was aligned with Chapters 12 and 24 in round 1; the second
   half of the same definition was not.
   **Fix.** Rename the safety horizon to $\tau_h$ in its four occurrences - the defining sentence
   (line 492), the risk condition $t_c<\tau_h$ (line 494), `exr:ch01-timescales`(b) (line 1041)
   and the solution to `exr:ch01-timescales`(b) (`ch01-solutions.tex`, line 88, "$\tau_h =
   10\times 20$ ms $= 0.2$ s") - and add half a clause after the definition so the reader can
   follow the pointer: "\cref{ch:ch24} writes this horizon $\tau_h$ as well, and takes it equal
   to the \orca horizon $\ttc$ of \cref{ch:ch13}." Nothing else in the chapter uses
   $\ttc_{\mathrm{safe}}$, so this is a four-line edit. *Editor's note (outside this chapter):*
   add the row "$\tau_h$ & safety horizon of the hybrid architecture & \cref{ch:ch01}" to
   `frontmatter/notation.tex`, and shorten row 129 to "$\ttc$ & horizon of the reactive layer &
   \cref{ch:ch12}" - its trailing clause "a time to collision in \cref{ch:ch01}" has been stale
   since round 1. (If the editor rules the other way and prefers $\ttc_{\mathrm{safe}}$
   book-wide, the equivalent fix is in \cref{ch:ch24}; what must not survive is two symbols for
   one term.)

## Suggestions

* **`sec:ch01-two-kinds`, roadmap sentence, lines 154-160.** \Cref{ch:ch05} is placed in two
  different families in one sentence ("Chapters 3 to 11 build the global planner" and
  "Chapters 5, 16, 17 and 21 to 23 provide the replanning"), and \cref{ch:ch06} (\arastar) is
  swept into the global planner without being named anywhere. Writing "Chapters 3, 4 and 6 to 11
  build the global planner" removes the double assignment at no cost.
* **Same sentence, LaTeX.** The chapter ranges use bare `\ref{ch:ch03}` etc. with the word
  "Chapters" typed by hand; `\crefrange{ch:ch03}{ch:ch11}` produces the same text, keeps the
  hyperlink and matches the style guide's rule that cross-chapter references use `\cref`.
  Cosmetic (category G).
* **`lst:ch01-conflicts`.** The listing splices two regions of `code/ch01_scenario.py` that are
  not adjacent in the file - the `Conflict` dataclass and `cell_centre` sit between them - and
  it uses the names `Cell` and `Conflict` without showing them. Every line is verbatim, so this
  is not an accuracy problem, but half a clause in the caption ("the `Conflict` dataclass
  between the two functions is omitted") would stop a reader from copying the excerpt and
  getting a `NameError`.
* **`exr:ch01-properties`.** This is the only exercise with a large mechanical answer (ten
  algorithms times six properties) and it has no entry in \cref{ch:appC}; a reader alone cannot
  check the ten hardest cells (weighted \astar is bounded suboptimal *and* complete; \dstarlite
  is incremental *and* optimal; \orca is real-time and none of the others). Four lines in
  `ch01-solutions.tex` would close the last gap in the appendix, which now covers six of the
  eight exercises.
* **`fig:ch01-scenario`.** The red dashed circle that marks the encounter has radius 0.62 cells
  while the caption quotes the encounter distance as 0.38 cells; a reader may take the circle for
  the distance. Either say in the caption that the circle marks the cell of $B$ at $t=6$, or draw
  the 0.38 gap as a short segment between $(7.5,5.5)$ and $(7.76,5.22)$.
* **Objectives box, last bullet ("set up the Python stack that its code uses").** The chapter
  names the stack but never says how to install it; one line
  (`python3 -m pip install numpy networkx matplotlib`) in the "The Python stack" paragraph would
  make the objective literally achievable.
* **Resolved since round 1, for the record.** The orphaned glossary is fixed: all sixteen ch01
  terms are now in the merged `appendices/glossary.tex` (Hybrid architecture line 139, Intruder
  159, Planned conflict 223, Safety horizon 269, Unexpected obstacle 324, ...), and
  `appendices/appC-solutions.tex` inputs `ch01-solutions.tex`. If required change 2 is applied,
  the "Safety horizon" glossary entry needs no symbol change (it names no symbol).

## What must be kept

The numeric spine is exact and must survive any revision; I re-derived it independently and then
re-ran the code. The scenario: 14 blocked cells; $A$'s 10-step path, $B$'s 9, $C$'s 6, sum of
costs 25, makespan 10, and the single vertex conflict $A$/$C$ at $(3,3)$, $t=4$ (no swap, as the
solution says); the intruder speed $\lVert(-0.54,-0.38)\rVert = 0.66030$; the $t=6$ position
$(7.76,5.22)$ at $0.38210$ from the centre of $B$'s cell; every one of the 88 numbers of
\cref{tab:ch01-trace} to two decimals; the continuous closest approach
$t^{*}=15.39/2.5160=6.11685$ at distance $0.33413$; the horizon positions $(3.44,2.18)$,
$(2.90,1.80)$, $(0.74,0.28)$ at $0.6826$, $0.6708$ and $0.3256$ cells from the parked drones;
the wait-step minima $0.7169$ ($t=7$), $0.9767$ ($t=7$) and $1.0555$ ($t=8$), hence three wait
steps; and the conflict fractions $43/200$, $119/200$, $199/200$. The "makespan plus one,
$t=11$" of `exr:ch01-horizon` matches `intruder_encounters` exactly (`horizon = max(len(p)) + 1
= 12`, so $t \le 11$), and `lst:ch01-conflicts` is verbatim from the file.

Completeness against the training plan is total and must not be trimmed. `tab:ch01-map`
reproduces groups A-F with all 27 entries, each with the plan's own priority (including
"Awareness--High" for the Transformer and "High" for Dijkstra) and the right chapter;
`tab:ch01-weeks` reproduces all twelve weeks with the right chapters and the right build target;
`sec:ch01-research` reproduces all seven research directions and the ten metrics; the capstone's
four layers, its five-step decision logic and the plan's reading order are all faithful. All six
objectives of the box are met by the text. The correct decision of round 1 to leave the week-1
coding exercise (grid \astar with time as a state variable) in \cref{ch:ch04} still holds:
the plan lists this chapter parenthetically in week 1, and `exr:ch01-coding` is the right
assignment for an introduction.

The citations are clean. All 17 keys used in the chapter resolve in `references.bib`
(`bib/ch01-extra.bib` is empty apart from its comment), and I checked each entry against my own
knowledge of the literature: Dijkstra 1959, Kalman 1960, Hart-Nilsson-Raphael 1968,
Fox-Burgard-Thrun 1997, Hochreiter-Schmidhuber 1997, Fiorini-Shiller 1998, LaValle 1998,
Koenig-Likhachev 2002, van den Berg et al. 2011, Sharon et al. 2015, Stern et al. 2019,
Vaswani et al. 2017, Hagberg et al. 2008, Panerati et al. 2021, plus LaValle 2006,
Russell-Norvig 2020 and Thrun-Burgard-Fox 2005. Nothing is fabricated and no detail is wrong.

Pedagogically, the parts that carry the chapter must stay as they are: the two-kinds-of-trouble
framing with Definitions 1.1 and 1.2 and `fig:ch01-planned-vs-unexpected` side by side; the
key-idea box that states the thesis of the book in one sentence; `ex:ch01-scenario` with its
trace table and the new cells-to-metres bridge; the architecture figure with every interface
labelled by what it carries, and the matching `dronebox`, which later chapters depend on; the
five-step decision loop with its two "keep going" back-edges; the logarithmic time-scale figure
with the "distance flown meanwhile" row (5 mm / 5 cm / 0.5 m / 5 m / 50 m / 500 m at 5 m/s -
all correct) and the honest pitfall box that forbids reading it as a measurement; the second
pitfall "An intruder is not a wall"; the history note; and the shaded six-chapter band added to
`fig:ch01-reading-paths` in round 1, which now makes the figure carry its own claim.

The mechanics are in order: six figures, all `\cref`-referenced, all built from the shared `sb*`
styles with one colour per architecture layer and a legend; five tables in `booktabs`
(`tab:ch01-map` as a `longtable` with proper continuation headers); 54 index entries against a
minimum of 15; eight exercises graded 1/1/2/2/2/2/1/3 with a genuine difficulty-3 coding task
whose acceptance tests are spelled out; six of the eight with solutions in \cref{ch:appC}; no
banned word ("obviously", "clearly", "trivially", "it is easy to see") anywhere in the chapter or
its solutions; ASCII-only, standard-library-only Python that runs in 0.14 s; and a build with no
errors, no chapter-local undefined reference and no overfull box above 3 pt.

## Response to review (round 2)

### Required change 1 (F) --- the false claim about priority tags (sec:ch01-map, line 613)

Applied, with the reviewer's first option. The sentence now reads:

> \Cref{tab:ch01-map} lists every algorithm of the plan with its role in one line, its
> priority and the chapter that teaches it. The priority tags of the plan are collected
> here, in \cref{tab:ch01-map}, and the twelve-week schedule of \cref{sec:ch01-howto}
> tells you when to read each chapter.

The chapter no longer promises a per-chapter tag that 21 of the algorithm chapters do
not carry. The four `\priority{...}` tags in the paragraph above stay: they define the
four levels of the plan, which is what the table's Priority column uses. The editor's
alternative (adding `\priority{...}` to the 21 silent chapters) is a book-level task and
is outside this chapter's file set.

### Required change 2 (F) --- two symbols for the safety horizon

Applied, four occurrences renamed to $\tau_h$, plus the half clause the reviewer asked
for:

* `chapters/ch01-introduction.tex:494` --- definition: "The **safety horizon** $\tau_h$
  is a look-ahead time chosen by the designer...".
* `chapters/ch01-introduction.tex:496` --- risk condition "$t_c<\tau_h$".
* `chapters/ch01-introduction.tex:498-500` --- added: "\Cref{ch:ch24} writes this horizon
  $\tau_h$ as well, and takes it equal to the \orca horizon $\ttc$ of \cref{ch:ch13}."
* `chapters/ch01-introduction.tex:1048` --- exr:ch01-timescales(b).
* `appendices/solutions/ch01-solutions.tex:106` --- solution to exr:ch01-timescales(b),
  now "$\tau_h = 10\times20$ ms $= 0.2$ s".

`\ttc_{\mathrm{safe}}` no longer occurs anywhere in the chapter's files; the book now
uses one symbol, $\tau_h$, for the term, matching def:ch24-inside and the parameter table
of \cref{ch:ch24}. The two notation-table rows the reviewer asks for
(`$\tau_h$` added, row 129 shortened) are in `frontmatter/notation.tex`, which this
chapter's author may not edit; **left for the editor**, exactly as the review's editor's
note describes.

### Suggestions

* **Roadmap sentence (sec:ch01-two-kinds).** Rewritten. Chapter 5 is no longer in two
  families and Chapter 6 is named: "The global planner is built by \cref{ch:ch03,ch:ch04}
  and \crefrange{ch:ch06}{ch:ch11}, ... \Crefrange{ch:ch12}{ch:ch15} build the local
  layer. \Crefrange{ch:ch18}{ch:ch20} build the tracking and prediction ...
  \Cref{ch:ch05,ch:ch16,ch:ch17} and \crefrange{ch:ch21}{ch:ch23} provide the
  replanning...". The bare `\ref` + hand-typed "Chapters" is gone, so the whole sentence
  is now `\cref`/`\crefrange` as the style guide asks (cosmetic point applied at the same
  time).
* **lst:ch01-conflicts caption.** Extended: the caption now says the two functions are not
  adjacent in the file, that the `Conflict` record type and the helper `cell_centre` sit
  between them and are omitted, that `Cell` is a type alias defined earlier, and that the
  reader should copy from the file rather than from the page. (The reviewer's list is
  corrected on one point: `Cell` is defined at line 31 of `code/ch01_scenario.py`, well
  before `position_on_path`, not between the two functions.)
* **exr:ch01-properties solution.** Added to `appendices/solutions/ch01-solutions.tex`,
  in exercise order (after exr:ch01-classify). It gives all ten rows, including the hard
  cells the reviewer named (weighted \astar bounded suboptimal and complete, \dstarlite
  incremental *and* optimal, \orca the only real-time entry, prioritized planning with
  none of the six), and answers the second half of the exercise: optimal and real-time
  never co-occur, structurally, because bounding the work per cycle bounds what can be
  examined. Appendix C now carries seven of the eight exercises.
* **fig:ch01-scenario caption.** The caption no longer labels the encounter "(dashed
  circle)" next to the $0.38$ figure; it now says that the red dashed circle marks the
  cell $B$ occupies at $t=6$, where the encounter happens, and that its radius is not the
  $0.38$-cell gap. The figure itself is unchanged (the circle is centred on $(7.5,5.5)$,
  the centre of $B$'s cell at $t=6$).
* **Objectives box / Python stack.** One line added to the "The Python stack" paragraph:
  "One line installs everything the exercises need: `python3 -m pip install numpy networkx
  matplotlib`."
* The round-1 book-level note (glossary merge, Appendix C input) needed no action; noted
  as resolved.

### Verification

* Nothing in the "must keep" list was touched: the scenario code, all figures, the five
  tables (27 map entries, twelve weeks, the trace table), the research directions and
  metrics, the citations, the boxes, the exercises and their grades are unchanged. No
  content was removed; the chapter grew by six lines.
* `python3 code/ch01_scenario.py` --- self-test passes in 0.15 s; the printed numbers
  (10/9/6 steps, vertex conflict A/C at $(3,3)$ at $t=4$, speed 0.66, $0.38$ at $t=6$) are
  unchanged, so every number quoted in the text still matches the code. The code was not
  edited, so no `.dat` file needed regeneration.
* Build: status **0**, no errors, no overfull boxes above 15 pt, chapter 19 pages. The
  build had to be run with a private `-outdir` because several other chapters were being
  rebuilt into the shared `Overleaf/build/` directory at the same time; that concurrency
  truncates `build/chapters/chNN.aux` for ch05, ch15, ch18 and ch24 and makes
  `./build.sh ch01-introduction` report "File ended while scanning use of \@newl@b" for
  *those* files. Those errors are not in ch01; with an isolated output directory and the
  same sources the build is clean (only `def:ch12-ttc` and the `ch:chNN` labels are
  undefined, as expected in a single-chapter build). `appendices/solutions/ch01-solutions.tex`
  was compiled inside Appendix C as well and produced no errors.
