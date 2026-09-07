# Review of Chapter 1 (Planning for Drone Swarms) - round 1

Reviewed artefacts: `Overleaf/chapters/ch01-introduction.tex` (1079 lines),
`Overleaf/figures/ch01/{scenario,planned-vs-unexpected,architecture,decision,timescales,reading-paths}.tex`,
`Overleaf/code/ch01_scenario.py`, `Overleaf/code/figures/gen_ch01_scenario.py`,
`Overleaf/appendices/solutions/ch01-solutions.tex`, `Overleaf/appendices/glossary/ch01-terms.tex`,
`Overleaf/bib/ch01-extra.bib`, and the training plan `docs/core-idea.txt`.
There is no `docs/specs/ch01.md`, so completeness was checked against the chapter's own
objectives box and against the training plan (sections 1-5 of `core-idea.txt`).

Build: `cd Overleaf && ./build.sh ch01-introduction` returns status 0. No `!` errors, no
`Overfull`/`Underfull` boxes at all, no undefined citations, no multiply-defined labels, and no
undefined reference belonging to this chapter (the `??` in the log and the PDF are all
cross-chapter `\cref{ch:chNN}` targets, which is expected in a single-chapter build).
The chapter occupies printed pages 1-20 (PDF pages 12-30 of `build/only-ch01-introduction.pdf`),
i.e. 20 pages - inside the 20-page cap, above the style guide's 12-18 band.

Code: `python3 code/ch01_scenario.py` prints `self-test passed` in well under a second.
I re-derived every quoted number independently (see "What must be kept"); all of them match.
`python3 code/figures/gen_ch01_scenario.py` regenerates `figures/ch01/scenario.tex` byte-identically.

## Verdict

**Minor revision.** The technical substance is sound and unusually well verified: every number in
the worked example, the trace table, the exercises and the solutions is reproduced by
`code/ch01_scenario.py`, the map table agrees item by item with the training plan, and all 17
citation keys resolve to real entries in `references.bib`. One statement in the properties table
(completeness of CBS) contradicts what Chapter 9 proves and is wrong as written; the remaining
items are local fixes to acronyms, two dangling forward references, one figure, one caption and a
modest trim. No required change asks for new content or a restructuring.

## Required changes

1. **Table 1.3 `tab:ch01-properties`, row "Complete" (`chapters/ch01-introduction.tex` line 398), and
   `appendices/glossary/ch01-terms.tex` line 4.** *Category A (technical accuracy).*
   The informal definition given is the strong one - "if a solution exists, the algorithm finds one,
   **and if none exists it says so**" - and `\cbs` is then listed as having it. That is false for CBS
   as published, and it contradicts this book's own Chapter 9, which states the objective as "Prove
   that CBS is complete **on solvable instances**" (`ch09-cbs.tex` line 14) and carries an explicit
   `rem:ch09-unsolvable` saying "there is no explicit stopping rule for unsolvable instances"
   (line 328, line 621: "Sharon et al. state completeness for solvable instances only").
   *Fix:* split the definition into the weak and strong forms - "if a solution exists the algorithm
   finds one; in the strong form it also reports failure when none exists, which needs a finite
   search space or a separate feasibility test" - and change the CBS entry to
   `\cbs on solvable instances (\cref{ch:ch09}; see the remark there on unsolvable instances)`.
   Keep Dijkstra/`\astar` in the strong form (finite graph) and prioritized planning as *not*
   complete. Apply the same correction to the glossary line, which currently reads "finding a
   solution whenever one exists and reporting failure when none exists".

2. **Acronyms are used before (or without) their expansion, throughout.** *Category F (consistency
   with the style guide, section 3: "Define each acronym at first use in every chapter").*
   Never expanded anywhere in the chapter: **ORCA** (optimal reciprocal collision avoidance;
   first use line 302), **ECBS** (Enhanced CBS; first use in Table 1.3, line 400), **LSTM** (long
   short-term memory; line 457), **RRT/RRT\*** (rapidly-exploring random tree; line 302),
   **LPA\*** (Lifelong Planning A\*; line 640), **ARA\*** (Anytime Repairing A\*; line 641),
   **M\*** (line 647), **QP** (line 901). Expanded, but only *after* the acronym has been used:
   **MAPF** (first use Table 1.5 line 816 and Figure 1.6; expansion only at lines 680/782),
   **MPC**, **MILP**, **VO**, **RVO**, **DWA** (all first used at lines 302 / 403, expanded later
   in Table 1.4).
   *Fix:* expand at first use. Concretely: line 302 -> "`\rrt` (rapidly-exploring random tree),
   `\rrtstar`, model predictive control (MPC), mixed-integer linear programming (MILP) and the
   velocity-space methods"; put the expansion in the "Algorithm" column of Table 1.4 for
   `\lpastar`, `\arastar`, `\orca`, `\ecbs`, `\mstar` and LSTM; write "multi-agent path finding
   (MAPF)" at line 262 or 613 so the acronym is defined before Table 1.5 and Figure 1.6 use it;
   spell out "quadratic program (QP)" at line 901.

3. **Two forward references promise material that the target chapters do not contain.**
   *Category F.*
   (a) Line 909-911 (§1.6.1, "The Python stack"): "`\Cref{ch:ch02}` describes the small conventions
   that the book's code shares: how a grid is stored, how a path is represented, **how a scenario is
   written to a file**." `chapters/ch02-toolbox.tex` has no scenario-file or JSON material (zero hits
   for "json" and for "scenario").
   (b) Exercise `exr:ch01-coding` (d), line 1076-1077: "`\cref{ch:ch25}` will read such files when it
   builds an experiment matrix." `chapters/ch25-experiments.tex` contains zero occurrences of
   "scenario" and no JSON reader.
   *Fix:* delete both clauses, or repoint them at material that exists: in (a) end the sentence at
   "how a path is represented", and add "the JSON layout used by `to_json`/`from_json` in
   `code/ch01_scenario.py` is the one the later experiment code reuses"; in (d) replace the
   `\cref{ch:ch25}` promise with "keep the layout of `to_json`, so that the same files can drive a
   later experiment matrix".

4. **§1.6.1 "The Python stack" (line 900-902) understates the dependencies.** *Category F.*
   "The book's reference implementations use only Python 3.10 or newer and NumPy (SciPy for the QP
   and MILP solvers of `\cref{ch:ch21,ch:ch22}`)" is contradicted by
   `code/ch20_prediction_torch.py` and `lst:ch20-torch` (`ch20-trajectory-prediction.tex`
   lines 1336-1366), which import PyTorch. Objective 6 promises the reader can "set up the Python
   stack that its code uses", so the omission has a practical cost.
   *Fix:* add ", plus an optional PyTorch version of the predictor in `\cref{ch:ch20}`, which the
   self-tests never run".

5. **`figures/ch01/planned-vs-unexpected.tex`, panel (b): the intruder starts inside a blocked
   cell.** *Category D (figures).*
   Both panels place `\gridobstacle{4}{4}` (line 7 and line 27 of the figure file), and panel (b)
   puts the intruder node and the start of its dotted prediction at `(4.4,4.4)`, which is inside
   cell (4,4). The same figure uses blocked cells as impassable walls for drone A, so a reader
   reasonably asks why the intruder may sit in one.
   *Fix:* move the obstacle out of the top-right corner in both panels - replace
   `\gridobstacle{4}{4}` by `\gridobstacle{0}{4}` in each scope. That cell is on neither A's route
   (row y=2) nor C's route (column x=2), and the intruder's line (4.4,4.4) -> (2.6,2.6) then passes
   only through free cells (4,4), (3,3), (2,2), so nothing else in the figure changes.

6. **Figure 1.6 caption (lines 768-771) does not describe the figure it labels.** *Category D.*
   The caption says "The top row is the reading order of the training plan", but the plan's
   reading order (`docs/core-idea.txt`, section 4) has twelve items while the top row of
   `figures/ch01/reading-paths.tex` has thirteen nodes: it appends `24/hybrid`, which the plan does
   not list, and it silently renders the plan's item 10, "Planning reference" - which line 784 of
   the chapter correctly says is "not a chapter but a book to keep at hand" - as chapter 2.
   *Fix:* drop the `24/hybrid/sbboxgray` entry from the first `\foreach` list in
   `figures/ch01/reading-paths.tex`; or keep it and amend the caption to "the plan's twelve items,
   with its 'planning reference' shown as the book's own toolbox chapter, followed by the capstone".

7. **`appendices/solutions/ch01-solutions.tex`, solution to `exr:ch01-classify`, item (h):
   self-reference.** *Category F.*
   It reads "one of the research directions of `\cref{ch:ch01}`", which renders in Appendix C as
   "Chapter 1" and points the reader at the whole chapter.
   *Fix:* replace with `\cref{sec:ch01-research}`.

8. **Length: trim about 1.5 pages of repetition (currently 20 printed pages; guide asks 12-18).**
   *Category G.* Three passages say twice what the chapter has already said once; no required
   content is involved.
   (a) §1.2, Table 1.2 `tab:ch01-contrasts` (lines 265-285) versus the eight `\paragraph`
   explanations that follow (lines 287-378): the table's two columns and the paragraphs carry the
   same content (compare the "Global / local" row with the "Global and local planning" paragraph,
   and the "Deliberative / reactive" row with its paragraph). Keep the table as the scannable
   summary and cut "Planning and control", "Deliberative and reactive" and "Centralized and
   decentralized" to two or three sentences each, keeping only what the table does not say (the MPC
   remark, the R&N citation, the CBS-needs-all-routes remark).
   (b) Summary box, bullet 4 (lines 929-933) re-lists all eight contrast pairs and all six
   properties, reproducing objectives bullet 3 (lines 21-25) nearly word for word. Replace with one
   sentence pointing at Tables 1.2 and 1.3.
   (c) §1.6, "The fast path" and "The builder's path" (lines 775-795) enumerate in prose exactly the
   chapter sequences already drawn in the two rows of Figure 1.6. Delete the two enumerations and
   keep the two remarks that the figure cannot carry: read `\cref{ch:ch07}` before `\cref{ch:ch09}`,
   and what the plan's "planning reference" means.

## Suggestions

* Objectives bullet 2 (line 18): "Tell a *planned conflict* ... from an *unexpected obstacle*" is
  grammatical but reads as a garden path. "Distinguish a planned conflict ... from an unexpected
  obstacle" is plainer and matches the style guide's "short sentences, plain American English".
* `exr:ch01-properties` (line 991): "which two properties never appear together in your table, and
  why is that not a coincidence?" has several correct answers (real-time and optimal; real-time and
  complete; optimal and bounded suboptimal). For a reader working alone, rephrase as "name a pair of
  properties that never appear together in your table and explain why the conflict is structural".
* Line 321: the chapter calls the construction the "space-time graph"; `ch02-toolbox.tex` names it
  the **time-expanded graph** (`def:ch02-space-time-state` and line 216). Use Chapter 2's term, or
  give both once.
* `exr:ch01-timescales` (b) (line 1048-1052) needs the 20 ms control cycle from part (a); restate it
  in (b) so the part is self-contained. (The intended answer works out cleanly: closing speed
  8 m/s, ten cycles = 0.2 s, so `\ttc_{\mathrm{safe}} \ge 0.2` s and the risk is detected at
  2 + 8 * 0.2 = 3.6 m.)
* `frontmatter/notation.tex` is still a placeholder with two rows. Chapter 1 is the first user of
  `\Cspace`, `\Cfree`, `\Cobs`, `\ttc`, `\pos`, `\vel`, `G=(V,E)`, `\pi`, `k` and `w`; ask the
  front-matter phase to add them so §1.2 does not introduce notation the table never confirms.
  Nothing needs to change in the chapter itself.
* Table 1.3, "Bounded suboptimal" row (line 400): "w=1.5 is often orders of magnitude faster" is an
  unsourced quantitative claim in an introduction. Point it at the ECBS benchmark of
  `\cref{ch:ch10}`, where the book measures it.
* Spelling is mixed British/American (centre, manoeuvre, optimise, discretise, colour, organise,
  labelled) against the guide's "Plain American English". The whole book is inconsistent this way
  (ch02 and ch13 are worse), so this belongs to the book-wide copyedit rather than to this chapter
  alone - but it is worth recording here.
* The training plan's "Experiments to run" list (metrics: collision rate, minimum separation, path
  length, travel time, makespan, sum of costs, replanning count, computation time, formation error,
  communication violations) is the only part of the plan that §1.4-§1.5 do not preview. One sentence
  in the `dronebox` or at the end of §1.5 naming those metrics and pointing at `\cref{ch:ch25}`
  would close the loop with objective 5.
* Only 4 of the 8 exercises have entries in `appendices/solutions/ch01-solutions.tex`. Adding a short
  answer for `exr:ch01-horizon` would help a lone reader; the numbers are
  t=14: (3.44, 2.18), 0.68 cells from parked C at (3,1); t=15: (2.90, 1.80), 0.67 cells;
  t=19: (0.74, 0.28), 0.33 cells from parked A at (0,0) - i.e. the default horizon of makespan+1
  misses two encounters with drones that are sitting on their goals.

## What must be kept

The worked example is the best-verified piece of writing I have reviewed in this book, and none of
it should be touched. I recomputed independently, from the two paths and the intruder's linear
motion, the speed (0.6603 -> 0.66), all 33 distances of Table 1.1 (every entry matches to the
printed two decimals, including the 0.38 minimum at t=6), the sum of costs 25 and makespan 10, the
rise to 26 after one wait step, the closest-approach time t\*=6.117 with minimum distance 0.334 in
`exr:ch01-trace`(c), the wait-step distances 0.717/0.977/1.055 in the solution to (d), and the
conflict fractions 0.215/0.595/0.995 quoted in the solution to `exr:ch01-coding`(c) - all reproduced
exactly by `code/ch01_scenario.py`, and `gen_ch01_scenario.py` regenerates `figures/ch01/scenario.tex`
byte for byte. Keep the scenario, its seed, Table 1.1, the listing (verbatim from the file) and all
four exercises built on it.

Keep the planned-conflict / unexpected-obstacle framing (Definitions 1.1 and 1.2 with the paired
Figure 1.2): it is the spine of the whole book, it is stated precisely, and the "fact versus
prediction" paragraph after Table 1.1 plus the "An intruder is not a wall" pitfall are exactly the
right lesson at exactly the right moment. Keep Table 1.4: all 27 algorithms, their one-line roles,
their priorities and their chapter assignments agree item by item with the training plan, including
the two hedged tags ("Awareness--High" for Transformers, and the two "essential for your research"
notes). Keep the four-layer preview with its interface `dronebox`, the five-step decision logic and
Figure 1.5 together with the "Numbers on a logarithmic axis are not measurements" pitfall - that
pitfall is the most honest paragraph in the chapter. Keep §1.5 on established results versus open
questions, which mirrors the plan's seven research directions faithfully and sets the reader's
expectations correctly. Finally, keep the mechanical hygiene: a clean build with no overfull boxes,
53 index entries with proper subentries, six well-styled TikZ figures all referenced with `\cref`
and all captioned with what to notice, and 17 citations that every resolve to genuine entries in
`references.bib` (Dijkstra 1959, Kalman 1960, Hart-Nilsson-Raphael 1968, Fox 1997, Hochreiter 1997,
Fiorini-Shiller 1998, LaValle 1998/2006, Koenig-Likhachev 2002, Thrun 2005, van den Berg 2011,
Sharon 2015, Vaswani 2017, Stern 2019, Russell-Norvig 2020, Hagberg 2008, Panerati 2021), with the
history note's dates all correct.

## Response to review (round 1)

All eight required changes are applied, plus six of the nine suggestions. Build status 0,
no `!` errors, no overfull boxes over 15 pt; `python3 code/ch01_scenario.py` still prints
`self-test passed` and the same numbers (speed 0.66, closest approach 0.38 at t=6, sum of
costs 25, makespan 10). The code was not modified, so `figures/ch01/scenario.tex` is
unchanged and no `.dat` file needed regenerating.

### Required changes

1. **(A) Completeness overstated for CBS.** `chapters/ch01-introduction.tex`, "Complete"
   row of Table 1.3, now reads "if a solution exists, the algorithm finds one; in the
   *strong* form it also reports failure when none exists, which needs a finite search
   space or a separate feasibility test", with the probabilistic sentence kept. The
   examples column now reads "Dijkstra and A* in the strong form (Ch. 3, 4); CBS on
   solvable instances (Ch. 9; see the remark there on unsolvable instances); RRT,
   probabilistically (Ch. 16); prioritized planning is *not* complete (Ch. 8)". The
   glossary entry in `appendices/glossary/ch01-terms.tex` was rewritten to match
   ("...in the strong form the algorithm also reports failure when no solution exists,
   which needs a finite search space or a separate feasibility test"). The cross-reference
   to Chapter 9 is phrased in words rather than with `\ref{rem:ch09-unsolvable}`, so the
   single-chapter build stays clean and no other chapter's label is depended on.

2. **(F) Acronyms not expanded at first use.** Every acronym is now expanded at its first
   occurrence *in source order*: RRT (rapidly-exploring random tree), RRT*, model
   predictive control (MPC) and mixed-integer linear programming (MILP) in the
   "Discrete and continuous planning" paragraph; ORCA (optimal reciprocal collision
   avoidance) and CBS (in "conflict-based search (CBS)") in the rewritten
   "Centralized and decentralized" paragraph, which precedes Table 1.3; ECBS
   ("ECBS, Enhanced CBS"), ARA* ("Anytime Repairing A*"), LPA* ("Lifelong Planning A*")
   and DWA ("the dynamic window approach (DWA)") inside the rows of Table 1.3, which is
   where each of them is first used; LSTM ("a long short-term memory (LSTM) network") in
   the prediction-layer paragraph; M* as "M* (read *M-star*)" in Table 1.4, since M* is a
   proper name with no expansion; and "quadratic program (QP)" in the Python-stack
   paragraph. MAPF is now defined in the "Time-indexed paths" paragraph ("in the standard
   vocabulary of **multi-agent path finding** (MAPF)", with an index entry), well before
   Figure 1.6 and Table 1.5 use the acronym. VO and RVO were already expanded at first use
   in Table 1.4; the redundant second expansion of CBS in the global-planner paragraph was
   dropped.

3. **(F) Two forward references to material that does not exist.** The Python-stack
   sentence now ends "...how a grid is stored and how a path is represented. The JSON
   layout written by `to_json` and read by `from_json` in `code/ch01_scenario.py` is the
   one that the book's later experiment code reuses." Exercise 1.8(d) now reads
   "...write the scenario to a JSON file, keeping the layout of `to_json`, so that the
   same files can drive a later experiment matrix." Neither claim depends on Chapter 2 or
   Chapter 25 containing scenario or JSON material.

4. **(F) PyTorch omitted from the stack.** The sentence now reads "...NumPy (SciPy for the
   quadratic program (QP) and MILP solvers of Chapters 21 and 22, plus an optional PyTorch
   version of the predictor in Chapter 20, which the self-tests never run), so that you can
   read every line."

5. **(D) Intruder starting inside a wall.** `figures/ch01/planned-vs-unexpected.tex`:
   `\gridobstacle{4}{4}` replaced by `\gridobstacle{0}{4}` in both scopes. Cell (0,4) is on
   neither A's row (y=2) nor C's column (x=2), and the intruder's line (4.4,4.4) to
   (2.0,2.0) now crosses only free cells; nothing else in the figure changed.

6. **(D) Reading-path caption versus figure.** The second option of the fix was taken: the
   figure is unchanged and the caption now reads "The top row is the reading order of the
   training plan: its twelve items, with the plan's ``planning reference'' shown as the
   book's own toolbox chapter, followed by the capstone; the first six items are the
   highest priority." The prose in Section 1.6 says the same thing where it explains what
   the plan's "planning reference" is.

7. **(F) Wrong cross-reference in the solutions.** `appendices/solutions/ch01-solutions.tex`,
   solution to `exr:ch01-classify` item (h): `\cref{ch:ch01}` is now `\cref{sec:ch01-research}`.

8. **(G) Length and repetition.** All three cuts were made and nothing else was removed.
   (a) Table 1.2 is untouched; "Planning and control", "Deliberative and reactive" and
   "Centralized and decentralized" are now two sentences each, keeping the MPC remark, the
   Russell-Norvig citation and the CBS-needs-all-routes remark, and the bold terms with
   their index entries. "Global and local planning", which the review named as the other
   duplicate of a table row, was tightened to the two sentences the table does not carry
   ("a global planner knows the goal but not the surprise..." plus the chapter pointers).
   (b) Summary bullet 4 is now one sentence pointing at Tables 1.2 and 1.3. (c) The two
   chapter-number enumerations in Section 1.6 are gone; only the read-Chapter-7-before-9
   remark and the explanation of the plan's "planning reference" remain, both pointing at
   Figure 1.6. **Result: the chapter now prints 19 pages (PDF pages 12-30 of
   `build/only-ch01-introduction.pdf`), one page shorter than before.** It is still one page
   over the guide's 18. Closing that last page would mean cutting required content -- the
   review's own instruction was "cut nothing else" -- so it was left alone; every page is
   dense (37-53 lines, no float-induced gaps).

### Suggestions

* Objectives bullet 2 now reads "Distinguish a *planned conflict* ... from an *unexpected
  obstacle*". Applied.
* `exr:ch01-properties` now asks the reader to "name a pair of properties that never appear
  together in your table and explain why that conflict is structural rather than
  accidental". Applied.
* The "space-time graph" sentence now reads "turns this into the time-expanded graph, also
  called the space-time graph", so Chapter 2's term comes first. Applied.
* `exr:ch01-timescales` (b) now says "at least ten of the 20 ms control cycles of part (a)",
  making the part self-contained. Applied.
* Table 1.3, bounded-suboptimal row: the unsourced "w=1.5 is often orders of magnitude
  faster" is replaced by "a larger w buys speed, a trade-off measured for ECBS in
  Chapter 10". Applied.
* The training plan's metrics are now named at the end of Section 1.5 ("collision rate,
  minimum separation, path length, travel time, makespan, sum of costs, replanning count,
  computation time, formation error and communication violations---which Chapter 25 defines
  and measures"), closing the loop with objective 5. Applied.
* A solution for `exr:ch01-horizon` was added to `appendices/solutions/ch01-solutions.tex`.
  The three positions and distances were recomputed by hand from pos_0=(11.0,7.5),
  v=(-0.54,-0.38) and the goal-cell centres (3.5,1.5) and (0.5,0.5): (3.44,2.18) at 0.683
  cells from parked C at t=14, (2.90,1.80) at 0.671 cells at t=15, and (0.74,0.28) at 0.326
  cells from parked A at t=19, printed as 0.68, 0.67 and 0.33 -- the reviewer's numbers.
  Applied.
* `frontmatter/notation.tex` is outside this chapter's file set; the request for entries for
  Cspace, Cfree, Cobs, ttc, pos, vel, G=(V,E), pi, k and w is passed to the front-matter
  phase unchanged. Not applied here.
* British/American spelling belongs to the book-wide copyedit, as the review says. Not
  applied here.

### What was kept

The worked example is untouched: the scenario, seed 1462, Table 1.1, the verbatim listing,
the trace numbers and all four exercises built on them; the planned-conflict versus
unexpected-obstacle framing with Definitions 1.1 and 1.2, Figure 1.2 and the
"fact versus prediction" paragraph; Table 1.4 with all 27 algorithms, priorities and chapter
assignments; the four-layer preview, the interface dronebox, the five-step decision logic,
Figure 1.5 with its pitfall; Section 1.5 and its seven research directions; and all
citations, index entries and figures.
