# Review of Chapter 1 (Planning for Drone Swarms) - round 2

Reviewed artefacts: `Overleaf/chapters/ch01-introduction.tex` (1074 lines),
`Overleaf/figures/ch01/{scenario,planned-vs-unexpected,architecture,decision,timescales,reading-paths}.tex`,
`Overleaf/code/ch01_scenario.py`, `Overleaf/code/figures/gen_ch01_scenario.py`,
`Overleaf/appendices/solutions/ch01-solutions.tex`, `Overleaf/appendices/glossary/ch01-terms.tex`,
`Overleaf/bib/ch01-extra.bib`, `Overleaf/references.bib`, `Overleaf/frontmatter/notation.tex`,
and, for consistency, `Overleaf/chapters/{ch02-toolbox,ch07-mapf-problem,ch09-cbs,ch12-velocity-obstacles,ch13-rvo-orca}.tex`.
There is still no `docs/specs/ch01.md`, so completeness was checked against the chapter's own
objectives box and against the training plan `docs/core-idea.txt` (sections 1-6).

Build: `cd Overleaf && ./build.sh ch01-introduction` returns status 0. No `!` errors, no
`Overfull`/`Underfull` boxes at all, no undefined citations, no multiply-defined labels, and no
undefined reference belonging to this chapter. The chapter occupies printed pages 2-20
(PDF pages 11-29 of `build/only-ch01-introduction.pdf`), i.e. **19 printed pages**, inside the
20-page cap that this round applies (one page shorter than round 1).

Code: `python3 code/ch01_scenario.py` prints `self-test passed` in under a second and reproduces
every quoted number. I independently re-ran the two derived results that the default run does not
print: the conflict fractions of the solution to `exr:ch01-coding`(c) came out
0.215 / 0.595 / 0.995 for k = 2 / 4 / 8, and the wait-step minima of the solution to
`exr:ch01-trace`(d) came out 0.7169 (t=7) / 0.9767 (t=7) / 1.0555 (t=8). Both match the printed
values. I also re-derived by hand the speed 0.66030, the t=6 separation 0.3821, the closest
approach t\* = 6.1168 with distance 0.3342, the sums of costs 25 and 26, both makespans (10 with C
waiting, 11 with A waiting), and the three horizon positions (3.44, 2.18) / (2.90, 1.80) /
(0.74, 0.28) with distances 0.6826 / 0.6708 / 0.3256. All correct.

## Verdict

**Accept.**

All eight required changes of round 1 were applied and applied correctly; I verified each one
against the source, the figure files, the solutions file, the glossary and the rebuilt PDF (see
"Verification of round 1" below). No required change remains in categories A-E: the technical
content is accurate, every number in the chapter, in the trace table, in the exercises and in the
solutions is reproduced by the code, all 17 citation keys resolve to genuine and correctly
detailed entries, the chapter covers every item of the training plan, and the six figures, five
tables, eight exercises and 50 index entries all meet the rubric. One cosmetic consistency item
(category F) remains from round 1's acronym sweep; it is listed below and does not block
acceptance.

### Verification of round 1

1. **(A) Completeness of CBS overstated.** Fixed. `tab:ch01-properties`, "Complete" row (line 393)
   now separates the weak and strong forms and reads "\cbs on solvable instances (\cref{ch:ch09};
   see the remark there on unsolvable instances)". This agrees with `ch09-cbs.tex` line 14 and
   `rem:ch09-unsolvable` (line 627). The glossary line
   (`appendices/glossary/ch01-terms.tex` line 4) was corrected to match. Dijkstra/`\astar` stay in
   the strong form, `\rrt` probabilistic, prioritized planning *not* complete - all correct.
2. **(F) Acronyms.** Fixed except for one residue (required change 1 below). Checked in *rendered
   page order*, not only source order: RRT/RRT\*/MPC/MILP page 15, MAPF / CBS / ORCA page 16,
   ECBS / ARA\* / LPA\* / DWA in Table 1.3 on page 17 (i.e. before Figure 1.3 on page 18 uses
   ORCA and DWA), VO / RVO / APF / EKF / UKF / M\* in Table 1.4, QP on page 27. All correct.
3. **(F) Dangling forward references.** Fixed. The Python-stack sentence now ends at "how a path
   is represented" plus the `to_json`/`from_json` clause (lines 901-904), and `exr:ch01-coding`(d)
   no longer promises a `\cref{ch:ch25}` reader (lines 1069-1071). I confirmed that what remains
   does exist: `ch02-toolbox.tex` covers graph storage (line 50), paths/plans/trajectories,
   makespan and sum of costs (line 12), the time-expanded graph (`def:ch02-time-expanded-graph`)
   and Minkowski inflation (line 145).
4. **(F) PyTorch.** Fixed (line 893).
5. **(D) Intruder inside a blocked cell.** Fixed. `figures/ch01/planned-vs-unexpected.tex` now has
   `\gridobstacle{0}{0}\gridobstacle{0}{4}` in both scopes (lines 7 and 24); the intruder starts in
   the free cell (4,4). The reviser additionally extended the dotted prediction from (2.6,2.6) to
   (2.0,2.0); that was not asked for but it is an improvement, because the line now really does
   cross A's row y = 2.5 (at x = 2.5, i.e. t = 3.17), which is what the caption claims.
6. **(D) Figure 1.6 caption.** Fixed by the second of the two offered options: the caption
   (lines 766-770) now says "its twelve items, with the plan's 'planning reference' shown as the
   book's own toolbox chapter, followed by the capstone", which is exactly the 13 nodes of the top
   row, and the first six nodes (4, 5, 9, 7, 12, 13) are the plan's first six items.
7. **(F) Self-reference in the solutions.** Fixed: `\cref{sec:ch01-research}`
   (`appendices/solutions/ch01-solutions.tex` line 19).
8. **(G) Length.** Fixed as far as it should be. The three named cuts were made and nothing else
   was removed; 20 printed pages became 19. I re-read §1.2, the summary box and §1.6 looking for
   further padding and found none: the eight contrast paragraphs are now two to three sentences
   each and each carries something the table does not, summary bullet 4 is one sentence, and §1.6
   no longer duplicates Figure 1.6. Table 1.4 (27 rows, ~2.5 pages) is required content and must
   not be cut.

## Required changes

1. **`chapters/ch01-introduction.tex` line 447, `\paragraph{2. Prediction layer (Kalman filter,
   LSTM).}` (printed page 9), together with `figures/ch01/architecture.tex` line 8.**
   *Category F (consistency with the style guide, §3: "Define each acronym at first use in every
   chapter"). Cosmetic.*
   **Problem.** LSTM is the one acronym that round 1's sweep did not reach. Its first appearance in
   the rendered chapter is the box "Kalman filter / LSTM" of Figure 1.3 and the paragraph heading
   on the same page; the expansion "a long short-term memory (LSTM) network" only follows four
   lines later at line 453. Everywhere else in the chapter the expansion now precedes the acronym.
   **Fix.** Move the expansion into §1.2, which is printed a page earlier, and drop the second one.
   In the "Tracking and prediction" paragraph (lines 370-372) end the sentence about prediction
   with "...over a horizon of a few seconds and reports the growing uncertainty along the way,
   either by extrapolation or with a learned model such as a long short-term memory (LSTM) network
   (\cref{ch:ch20})"; then line 453 becomes "...either by extrapolating at constant velocity or
   with an LSTM network (\cref{ch:ch20})". (A one-word alternative, if §1.2 is not to be touched,
   is to write the heading as "2. Prediction layer (Kalman filter, long short-term memory network)."
   and leave line 453 as it stands.)

## Suggestions

* `figures/ch01/planned-vs-unexpected.tex`, panel (b), lines 38-40: the three time labels are
  placed inconsistently relative to the discs they name. "t=1" (anchor west at (3.05,3.95)) sits
  above-left of its disc at (3.8,3.8); "t=2" (anchor west at (2.7,3.2)) starts inside its own disc,
  which spans x from 2.76 to 3.64 at that height; "t=3" (anchor east at (1.95,2.1)) sits about 0.6
  units down-left of its disc at (2.6,2.6), right at the end of the dotted line. Nothing is wrong
  logically - there are exactly three discs and the caption names them in order - but a reader
  scanning the picture can attach "t=3" to the end of the line rather than to the third disc. Put
  each label just outside its own disc on the same side, e.g. `anchor=west` at (3.05,3.95),
  (2.42,3.36) and (1.82,2.76) respectively (up-left of each disc), and shift them out of the disc
  interiors.
* Same figure and caption (line 128-131): the dotted prediction is drawn one step past the last
  disc, to the t = 4 position (2.0,2.0), while the caption says "we predict where it will be at
  t = 1, 2, 3". One extra half-sentence - "the dotted line continues past the last disc to show
  where the crossing happens" - would remove the small mismatch, or draw a fourth (fainter) disc.
* Line 190: "\Cref{tab:ch01-trace} lists the whole time line." The table stops at t = 10, and
  `exr:ch01-horizon` is built on exactly the point that the interesting encounters happen *after*
  the makespan. "lists the time line of the plan" would be more accurate and would not undercut
  the exercise.
* `appendices/solutions/ch01-solutions.tex` line 96: the code gives 0.995 for k = 8, which the
  solution prints as "about 0.99". That is a truncation, not a rounding. Write "about 0.99-1.00"
  or "practically every scenario"; the 0.22 and 0.60 for k = 2 and 4 are correct as printed.
* Spelling is still mixed British/American against the guide's "Plain American English": 26
  occurrences in this chapter, namely *centre* (5), *centres*, *manoeuvre* (4), *metres* (3),
  *organise* (2), *neighbours* (2), *neighbour*, *recognise*, *optimisation*, *Optimises*,
  *modelled*, *linearisation*, *labelled*, *discretise*, *Colours*. As in round 1, this belongs to
  the book-wide copyedit rather than to this chapter alone, but it is worth recording that it is
  still open.
* `frontmatter/notation.tex` is still the two-row placeholder. Chapter 1 remains the first user of
  `\Cspace`, `\Cfree`, `\Cobs`, `\ttc`, `\pos`, `\vel`, `\pi`, $k$ and $w$; the front-matter phase
  still owes those rows. Nothing needs to change in the chapter.
* `chapters/ch24-hybrid-architecture.tex` and `chapters/ch25-experiments.tex` are still
  four-line placeholders. Chapter 1 makes four concrete promises about Chapter 25 (measuring
  computation time honestly, defining and measuring the ten metrics, building the local-only /
  replan-only / hybrid benchmark, and measuring the numbers behind Figure 1.5) and several about
  Chapter 24. They match those chapters' planned titles, so nothing is wrong today, but they should
  be re-checked in the book-level consistency pass once those chapters exist - this is exactly the
  failure mode that round 1's item 3 caught.
* Build hygiene, not a chapter defect: `build/chapters/*.aux` from earlier single-chapter builds
  survives, so in `build/only-ch01-introduction.pdf` some cross-chapter references render as a
  wrong number rather than `??` - `ch:ch04` shows as "Chapter 1" and `ch:ch07` as "Chapter 2"
  (`build/chapters/ch04-astar.aux`, `ch07-mapf-problem.aux`). Whoever reads a single-chapter PDF
  should clear `build/` first, or they will chase a reference bug that is not there. I verified
  every `\cref{ch:chNN}` in the source by hand and all of them point at the right chapter.
* Objective 6 promises the reader can "set up the Python stack that its code uses", and §1.6.1
  names the packages but gives no command. One line - `python3 -m pip install numpy scipy
  networkx matplotlib` - would close the objective for a reader working alone.

## What must be kept

Everything round 1 asked to keep survived intact, and the round-2 evidence is stronger, not weaker.

The worked example remains the best-verified writing in the book. Seed 1462, the three paths, the
33 distances of Table 1.1, the sum of costs 25 and makespan 10, the rise to 26 after one wait, the
speed 0.66 and the 0.38 minimum at t=6 are all reproduced exactly by `code/ch01_scenario.py`; the
four exercises built on the scenario and their solutions are reproduced too, including the numbers
that the default run does not print (0.215/0.595/0.995 and 0.7169/0.9767/1.0555, which I re-ran).
`gen_ch01_scenario.py` still regenerates `figures/ch01/scenario.tex` unchanged. Do not touch the
scenario, the seed, Table 1.1, the listing (both excerpts are byte-for-byte the file) or the four
exercises.

Keep the planned-conflict / unexpected-obstacle spine: Definitions 1.1 and 1.2, the paired
Figure 1.2, the "fact versus prediction" paragraph after Table 1.1, and the "An intruder is not a
wall" pitfall. Definition 1.4 (time-indexed path) is now demonstrably consistent with
`def:ch07-path` down to the `\set{v_t,v_{t+1}}\in E` notation and the stay-at-target convention,
and with `def:ch02-graph`; that agreement is worth protecting.

Keep the corrected "Complete" row of Table 1.3 - the weak/strong split with "CBS on solvable
instances" is now the most careful statement of completeness in the book, and Chapter 9 depends on
it. Keep Table 1.4: all 27 algorithms, roles, priorities and chapter assignments still agree item
by item with the training plan, including "Awareness--High" for Transformers and the two "essential
for your research" notes. Keep Table 1.5, whose twelve rows match the plan's schedule week by week,
and the "Parts II, III and V are global" claim, which I checked against `main.tex`.

Keep the four-layer preview with its interface `dronebox`, the five-step decision logic with
Figures 1.3 and 1.4, the time-scale figure with the "Numbers on a logarithmic axis are not
measurements" pitfall (still the most honest paragraph in the chapter, and its arithmetic - 10 cm,
2.5 m, 15 m, and the 5 mm / 5 cm / 0.5 m / 5 m / 50 m / 500 m row of Figure 1.5 - is exact), and
§1.5 with its seven research directions and the metric list that now closes the loop with
objective 5.

Finally keep the mechanical hygiene, which is now better than in round 1: build status 0 with no
overfull boxes, 19 printed pages, 50 index entries with proper subentries, six well-styled TikZ
figures all referenced with `\cref` and captioned with what to notice, five booktabs tables, two
pitfall boxes, eight exercises spread 3 x ★, 4 x ★★, 1 x ★★★ with the coding exercise present, and
17 citations that all resolve to genuine entries whose authors, venue and year I checked
(Dijkstra 1959, Kalman 1960, Hart-Nilsson-Raphael 1968, Fox 1997, Hochreiter-Schmidhuber 1997,
Fiorini-Shiller 1998, LaValle TR 98-11 1998, LaValle 2006, Koenig-Likhachev 2002, Thrun 2005,
Hagberg 2008 SciPy 11-15, van den Berg 2011 STAR 70:3-19, Sharon 2015 AIJ 219:40-66,
Vaswani 2017, Stern 2019 SoCS 151-158, Russell-Norvig 2020, Panerati 2021 IROS 7512-7519), with
every date in the history note correct.
