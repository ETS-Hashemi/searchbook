# Review of Chapter 4 (A* Search) - round 1

Reviewed artefacts: `Overleaf/chapters/ch04-astar.tex` (809 lines), `Overleaf/figures/ch04/*.tex`,
`Overleaf/code/ch04_astar.py`, `Overleaf/code/figures/gen_ch04_expansions.py`,
`Overleaf/figures/data/ch04-expansions.dat`, `Overleaf/appendices/solutions/ch04-solutions.tex`,
`Overleaf/appendices/glossary/ch04-terms.tex`, `Overleaf/bib/ch04-extra.bib`, `Overleaf/references.bib`,
against `STYLE_GUIDE.md` §9 (A-H), `docs/specs/ch04.md` and `docs/core-idea.txt` (Week 1).

Build: `cd Overleaf && ./build.sh ch04-astar` initially returned status 12. The cause is **not** this
chapter: a truncated leftover `build/chapters/ch10-ecbs.aux` from an earlier single-chapter build made
pdflatex abort with "Runaway argument? {\contentsline {subsection}{\numberline {1.8.2}Tie-breaking}".
After `rm build/chapters/ch10-ecbs.aux` the build is clean: status 0, no `!` errors, **no overfull boxes
at all**, no undefined citations, and only three undefined references, all of them pointing at sections
that do not exist (see change 7). Output: 32-page PDF; the chapter itself is book pages 3-14, i.e.
**12 pages** - well inside the 24-page cap and about 5 pages *below* the 16-18 page target of the spec.

Code: `python3 code/ch04_astar.py` -> `ch04_astar: all self-tests passed` (exit 0, < 5 s).
I re-derived every number quoted in the chapter with an independent script driving `astar()` directly.
**All of them are correct**: 21 expansions and cost 13 for A*/Manhattan on the 6x6 instance; 26 for
Dijkstra; 24 for smaller-g tie-breaking; 24 expansions and cost 9+2*sqrt(2)=11.82843 for octile on the
8-connected version; the ten rows of Table 1.2 (nodes, g, h, f and the Open column) match the code
exactly; the terminal Open set is {(0,5),(1,5),(2,5)} at f=13 plus (3,0) at f=15; the empty 20x20 grid
gives 39 vs 400 expansions at cost 38; the inconsistent-graph f-sequence is 0,3,4,2,4 with cost 4 (5
without re-opening); the "6 of 40 instances" figure for Manhattan on 8-connected grids reproduces; and
every number in §1.7.3 matches row `n=100` of `figures/data/ch04-expansions.dat`
(7451.8/7513.3, 756.2, 3323.6, 371.8, 271.3, ratios 1.1197, 1.0582, 1.0694, 1.0451; caption bound 1.13 holds).
All nine cited keys exist in `references.bib` and their bibliographic details are correct as far as I can
vouch for them; nothing is fabricated.

## Verdict

**Major revision.**

The material that is present is of high quality and is technically sound - I found only two small factual
errors in roughly 800 lines. The problem is that the chapter file **stops in mid-chapter**. It ends after
§1.7.4 "Other relatives" with no space-time A* section, no implementation notes, no Python listing, no
pitfall boxes, no drone box, no summary, no further-reading paragraph and no exercises. Roughly 40 % of
the required content - including the single largest "must cover" item of the specification and the Week-1
milestone item "space-time representation" - is absent, the glossary file already defines six terms the
chapter never introduces, the solutions file is empty, and a finished TikZ figure for the missing section
is sitting unused in `figures/ch04/`. This is squarely category B, so Accept and Minor revision are both
out of reach.

**No cuts are required (category G).** The chapter is 12 pages against a 24-page ceiling; there is no
padding to remove. Completing the missing sections should bring it to roughly 20-22 pages, still inside
the ceiling. Do not shorten anything listed under "What must be kept".

## Required changes

1. **The whole space-time A* section is missing.**
   *Location:* `chapters/ch04-astar.tex`, after line 809 (end of §`sec:ch04-variants`); promised by the
   roadmap at lines 56-57 and by objective 4 at line 14.
   *Problem:* `docs/specs/ch04.md` asks for a "FULL SECTION on space-time A*", and Week 1 of
   `docs/core-idea.txt` lists "space-time representation" as a learning item and "add time as a state
   variable" as the coding exercise. Nothing of it is in the chapter. This is also the section that
   `ch:ch08` and `ch:ch09` are told to rely on, and `appendices/glossary/ch04-terms.tex` already ships
   definitions for *Space-time A\**, *Vertex constraint*, *Edge constraint*, *Reservation table*,
   *Goal-stay time* and *Time horizon* - six glossary entries that currently point at text that does not
   exist.
   *Fix:* add `\section{Space-time \astar}\label{sec:ch04-spacetime}` covering, in this order:
   (a) the state $(v,t)$ and the time-expanded graph, with the wait action of cost 1 and the observation
   that the graph is a DAG in $t$; (b) `definition` environments for a vertex constraint
   $\langle a,v,t\rangle$ and an edge constraint $\langle a,u,v,t\rangle$ in the notation of
   Stern et al. \cite{stern2019mapf}, plus the reservation table of Silver \cite{silver2005cooperative};
   (c) goal handling - the agent parks at the goal, so a state $(\gamma,t)$ is a goal only if
   $t > t_\gamma$, the last time the goal is constrained (the code's `last_blocked_time`); (d) the time
   horizon $T_{\max}=H+1+D$ used by `default_horizon()` in the code, with the argument why it preserves
   completeness and guarantees termination; (e) the heuristic: the static distance table from a backward
   BFS/Dijkstra (`static_distances`), which is consistent on the space-time graph and is re-used across
   every constrained re-run - this closes the loop with §1.3.2 line 274-278; (f) an `algorithm2e`
   pseudocode block `\label{alg:ch04-spacetime}` using the already-declared `\SetKwFunction{AstarSpaceTime}`
   macro (line 6), which is currently declared but never used; (g) the worked mini-example that is already
   implemented and asserted in the code (`spacetime_example()`: 3x3 empty grid, $s=(0,1)$, $\gamma=(2,1)$,
   vertex constraint $((1,1),1)$; unconstrained cost 2 with 3 expansions, constrained cost 3 with 4
   expansions and the path $(0,1),(0,1),(1,1),(2,1)$, i.e. one forced wait), and ideally the corridor /
   passing-bay example of self-test 8. Quote only numbers taken from the self-test.
   *Category:* B (also A: the objectives box promises material the chapter does not deliver).

2. **No implementation-notes section and no Python listing.**
   *Location:* referenced as `\cref{sec:ch04-implementation}` at lines 58 and 703-704, does not exist.
   *Problem:* STYLE_GUIDE §2 item 10 and §6 require an implementation section with a `lstlisting`
   excerpt of at most 45 lines copied verbatim from `code/ch04_astar.py`. The chapter contains no
   `lstlisting` at all, and §1.7.1 line 703 already forward-references the counter in the priority
   tuple to a section that is not there.
   *Fix:* add `\section{Implementation notes}\label{sec:ch04-implementation}` with a listing of the main
   loop of `astar()` (lines 137-170 of `code/ch04_astar.py` fit in 34 lines) labelled
   `lst:ch04-astar` and `\cref`-ed from the text, plus the points the spec names: hashing of grid and
   space-time states, the priority tuple $(f,-g,\text{counter})$ and why the counter stops Python from
   comparing tuples of coordinates, parent dictionaries and path reconstruction, lazy deletion versus
   decrease-key, and memory. Mention the `round(f, 9)` / `EPS` guard the code uses so that
   $\sqrt2$ arithmetic does not break tie-breaking or the relaxation test.
   *Category:* B, G.

3. **No `pitfall` boxes.**
   *Location:* nowhere in the chapter; STYLE_GUIDE §2 item 10 requires at least two.
   *Problem:* the chapter has the raw material for them in the running text but no boxes.
   *Fix:* add at least two `\begin{pitfall}...\end{pitfall}` boxes, e.g. (i) "Manhattan on an
   8-connected grid" - it overestimates the diagonal, A* then returns longer paths silently and the code
   reproduces this on 6 of 40 random instances; (ii) "Testing the goal at generation time" - returns the
   first path found, not the cheapest, and breaks the proof of `thm:ch04-optimal`; (iii) in the new
   space-time section, "forgetting that the goal must stay free after arrival", which turns a solvable
   MAPF sub-problem into a spurious failure.
   *Category:* B, C.

4. **No "Where this fits in the drone system" section / `dronebox`.**
   *Location:* referenced as `\cref{sec:ch04-drone}` at line 59, does not exist.
   *Problem:* STYLE_GUIDE §2 item 11 requires this section with a `dronebox` referencing `\cref{ch:ch24}`
   and the study-plan week in `\cref{ch:appA}`; the spec asks specifically for "low-level planner inside
   CBS/ECBS, replanner fallback, reference for D* Lite".
   *Fix:* add `\section{Where this fits in the drone system}\label{sec:ch04-drone}` with a `dronebox`
   naming the three roles: the constrained low-level search called once per constraint-tree node in
   `\cref{ch:ch09,ch:ch10}`, the replanning-layer fallback of `\cref{ch:ch24}` when a local ORCA/DWA
   manoeuvre cannot rejoin the nominal route, and the pointer to `\cref{ch:ch05}` for repairing rather
   than restarting. Reference Week 1 of `\cref{ch:appA}`.
   *Category:* B.

5. **No `summary` box and no further-reading paragraph.**
   *Location:* end of chapter (after the new §space-time / implementation / drone sections).
   *Problem:* STYLE_GUIDE §2 item 12 requires both.
   *Fix:* add `\begin{summary}` with bullets (f = g + h; admissible vs consistent; the two optimality
   theorems and what each assumes; grid heuristics per connectivity; tie-breaking; the $w\,C^*$ bound;
   the space-time state and constraints) and a *Further reading* paragraph citing
   `hart1968formal`, `hart1972correction`, `pearl1984heuristics`, `dechter1985generalized`,
   `russell2020aima`, `pohl1970heuristic`, `silver2005cooperative`, `stern2019mapf`,
   `harabor2011jps`, `phillips2011sipp`.
   *Category:* B, H.

6. **No exercises, and the solutions file is empty.**
   *Location:* end of `chapters/ch04-astar.tex`; `appendices/solutions/ch04-solutions.tex` contains only
   a comment line.
   *Problem:* STYLE_GUIDE §2 item 13 and rubric E require 6-10 graded exercises including the study-plan
   week's coding exercise. There are none, so a self-study reader has nothing to practise on and
   Appendix C has nothing to show.
   *Fix:* add `\section{Exercises}` with 8-10 `\begin{exercise}[\difficulty{n}]` items following the
   format of `chapters/ch03-dijkstra.tex` lines 1007-1090, labelled `exr:ch04-...`, with a difficulty
   spread (roughly 2 at level 1, 4 at level 2, 2-3 at level 3) and the spec's named items:
   (a) hand-trace two more expansions of `ex:ch04-grid` and give the Open set; (b) prove that the octile
   distance is consistent on an 8-connected grid with the corner-cutting rule of `\cref{def:ch02-grid}`;
   (c) prove the $w\,C^*$ bound of `thm:ch04-weighted` again for the variant that never re-opens, assuming
   $\hcost$ consistent; (d) show $\max(\hcost_1,\hcost_2)$ is admissible/consistent when both are, and
   relate it to `thm:ch04-dominance`; (e) design admissible heuristics for the 6-, 18- and 26-connected 3D
   lattices of `\cref{ch:ch02}`; (f) construct a grid on which Manhattan on an 8-connected map returns a
   strictly longer path; (g) **the Week-1 coding exercise, marked `\difficulty{3} Coding`: implement grid
   A*, add time as a state variable, and visualise the open and closed sets** - phrase it against the API
   of `code/ch04_astar.py`; (h) a space-time exercise: add one vertex and one edge constraint by hand and
   predict the wait, then check it with `space_time_astar`. Populate
   `appendices/solutions/ch04-solutions.tex` with a hint or full solution per exercise.
   *Category:* E.

7. **Three dangling cross-references print as `??` in the PDF.**
   *Location:* lines 56, 58, 59 (`sec:ch04-spacetime`, `sec:ch04-implementation`, `sec:ch04-drone`);
   confirmed in `build/only-ch04-astar.log` and visible in the PDF text of book page 6 ("it becomes the
   heuristic of choice in space-time (??)"), see also lines 277 and 703-704.
   *Problem:* undefined references belonging to this chapter; STYLE_GUIDE §7 forbids them.
   *Fix:* they disappear once changes 1, 2 and 4 add the labelled sections. Re-run
   `./build.sh ch04-astar` and confirm the log has no `Reference \`sec:ch04-...' undefined`.
   *Category:* G.

8. **`figures/ch04/spacetime.tex` exists but is never included.**
   *Location:* `Overleaf/figures/ch04/spacetime.tex` (51 lines, finished: 3x3 grid with the hatched
   forbidden cell plus the time-expanded middle row for t = 0..3 with wait and move edges).
   *Problem:* an orphan figure file; the spec explicitly asks for a "worked mini-example with one vertex
   constraint forcing a wait (figure with time layers)".
   *Fix:* include it inside the new §space-time with
   `\begin{figure}[tb]\centering\inputfigure{ch04/spacetime}\caption{...}\label{fig:ch04-spacetime}\end{figure}`
   and `\cref` it from the text. Write a caption that says what to notice, in the style of the existing
   captions: the horizontal edges are waits, the diagonal edges are moves, the hatched state $((1,1),1)$
   is removed by the vertex constraint, and the cheapest remaining path costs 3 instead of 2.
   *Category:* D, B.

9. **Two mandated citations are missing.**
   *Location:* whole chapter; `docs/specs/ch04.md` lists the required keys.
   *Problem:* `silver2005cooperative` (cooperative pathfinding / reservation tables) and
   `stern2019mapf` (the vertex/edge-constraint terminology) are never cited, because the section that
   would cite them is missing. Both keys already exist in `references.bib` and are correct.
   *Fix:* cite them where introduced in the new §space-time and again in *Further reading*.
   *Category:* H.

10. **Factual error: "four wasted expansions" in the worked example; $(3,4)$ lies on the returned path.**
    *Location:* caption of `fig:ch04-example`, line 373-374 ("note the four wasted expansions in the
    column $x = 3$"), and body text lines 388-390 ("dives down the column $x = 3$ to $(3, 2)$ ... the four
    cells $(3, 4), (3, 3), (3, 2), (3, 1)$ are a dead end").
    *Problem:* the path returned by the code is
    $(0,0),(1,0),(1,1),(1,2),(1,3),(1,4),(2,4),(3,4),(3,5),(4,5),(5,5),(5,4),(5,3),(5,2)$, so $(3,4)$ is on
    the optimal path and is not a wasted expansion and not part of the dead end. The wasted cells are the
    three cells $(3,3),(3,2),(3,1)$. The same sentence also says the search "dives down the column $x=3$
    to $(3,2)$", but the expansion order produced by the code is
    $\dots,(3,4),(3,3),(3,2),(0,4),(3,1),(3,5),\dots$: it goes one cell further, to $(3,1)$, after
    $(0,4)$ is taken off the queue.
    *Fix:* in the caption write "note the three wasted expansions $(3,3),(3,2),(3,1)$ below the junction at
    $(3,4)$, where the heuristic cannot see the wall at $x = 4$"; in the body write "dives down the column
    $x = 3$ as far as $(3,1)$, where the second wall stops it: the three cells $(3,3),(3,2),(3,1)$ are a
    dead end that the Manhattan distance cannot foresee" (and keep the following clause about $(0,4)$,
    which is correct: $(0,4)$ is expanded between $(3,2)$ and $(3,1)$).
    *Category:* A (also D, since the caption is wrong).

11. **Mis-attributed cross-reference after the corollary.**
    *Location:* lines 584-587: "\Cref{thm:ch04-surely} is the reason why the closed set can be a plain
    'expanded' flag when $\hcost$ is consistent, why the trace in \cref{tab:ch04-trace} shows
    non-decreasing $\fcost$, and why the $\fcost$ values in \cref{fig:ch04-example} never exceed 13."
    *Problem:* only the third clause follows from `thm:ch04-surely`. The plain expanded-flag argument is
    `thm:ch04-consistent`(i) and the non-decreasing trace is `thm:ch04-consistent`(ii). As written the
    reader is sent to the wrong result twice.
    *Fix:* "\Cref{thm:ch04-consistent}(i) is the reason why the closed set can be a plain 'expanded' flag
    when $\hcost$ is consistent and part~(ii) why the trace in \cref{tab:ch04-trace} shows non-decreasing
    $\fcost$; \cref{thm:ch04-surely} is why the $\fcost$ values in \cref{fig:ch04-example} never exceed 13."
    *Category:* C.

12. **Acronyms CBS and ECBS are used without being defined in this chapter.**
    *Location:* line 35 ("The global planner ... is \cbs or \ecbs"); `\cbs` expands to the bare string
    "CBS" (`searchbook.sty` line 302).
    *Problem:* STYLE_GUIDE §3 requires every acronym to be expanded at first use *in every chapter*.
    *Fix:* write "is conflict-based search (\cbs) or its bounded-suboptimal variant \ecbs
    (\cref{ch:ch09,ch:ch10})". Do the same for MAPF when the new space-time section introduces it.
    *Category:* F.

13. **Wrong count in the annotation of `figures/ch04/heuristics.tex`.**
    *Location:* `Overleaf/figures/ch04/heuristics.tex`, last node: "(4 moves of cost 1 or $\sqrt{2}$ are
    drawn)".
    *Problem:* the octile polyline drawn there covers three diagonal moves and two straight ones, i.e.
    five moves, not four; and the sentence is ambiguous about which of the four drawn curves it refers to.
    *Fix:* replace by "(the blue octile path is 3 diagonal + 2 straight moves)" or drop the line - the
    chapter text at lines 210-214 already explains the construction.
    *Category:* D.

## Suggestions

* `fig:ch04-idea` (right panel) draws an obstacle inside the ellipse, but the caption claims that "the
  nodes with $\fcost \le C^*$ lie inside an ellipse with foci $s$ and $\gamma$". That is exact only in an
  obstacle-free space, where $\gcost^*$ is the straight-line distance. Add "in an obstacle-free plane" to
  the caption, or drop the small obstacle from the right panel.
* Line 380: "Steps 1-4 walk up the column $x = 1$" - step 1 expands the start $(0,0)$, which is in column
  $x=0$. Say "Steps 2-4".
* §1.3.2 discusses 8-connected grids without recalling the corner-cutting rule of `\cref{def:ch02-grid}`,
  which `grid_successors()` in the code does enforce. One sentence with a `\cref` would keep chapter and
  code visibly aligned and is worth having before the space-time section reuses the successor function.
* The proof sketch of `thm:ch04-dominance` ends with "no admissible algorithm can do better than \astar
  with a consistent heuristic". Dechter and Pearl's optimality result holds over a specific class
  (admissible algorithms that are equally informed and search the same graph) and is about the surely
  expanded set. Add half a sentence naming the class, otherwise the claim reads stronger than it is.
* `thm:ch04-weighted` remark (lines 758-761): the ARA* result that the $w\,C^*$ bound survives without
  re-opening assumes a *consistent* $\hcost$. Say so explicitly.
* The complexity subsection gives the graph-search bounds but never says that on an implicit graph A* is
  exponential in the solution depth unless the heuristic error grows slower than the true cost
  (Pearl 1984, ch. 6). Two sentences would round the section off and cost almost nothing.
* `astar_grid()` in `code/ch04_astar.py` does not forward `record_open`, so trace tables must be produced
  by calling `astar()` directly (as `gen_ch04_grids.py` does). Adding the keyword would make the exercise
  "visualise the open and closed sets" easier for the reader.
* Build hygiene, not a chapter defect: `./build.sh ch04-astar` aborts with status 12 while the stale
  `build/chapters/ch10-ecbs.aux` from another chapter's build is present. Delete it (or clean `build/`)
  before re-checking, otherwise the reviser will chase a phantom error in Chapter 4.

## What must be kept

The theory in this chapter is genuinely well built and should survive revision essentially untouched.
The single invariant `thm:ch04-invariant` ("an optimal-path node is always open") is stated once and then
carries the optimality theorem, the no-re-expansion theorem and the weighted-A* bound; that is a cleaner
architecture than the usual three separate proofs, and every step of it - including the treatment of
re-opening inside the invariant and the $\hcost(\gamma')=0$ step - is correct. `thm:ch04-consistent`,
`thm:ch04-surely` and `thm:ch04-dominance` are correctly stated and correctly proved, the
consistency-implies-admissibility lemma comes with a genuine counterexample that is reused later in the
chapter and in the code, and `thm:ch04-metric` is exactly the right lemma to make the four grid
heuristics fall out in one line. Keep `tab:ch04-heuristics` and the paragraph that derives it: the
per-connectivity admissibility statement, backed by the "6 of 40 instances" experiment, is the clearest
short treatment of that trap I have read.

Keep the worked example as it stands (apart from change 10). It is the strongest part of the chapter:
a small instance chosen so that the search really does walk into a dead end, a trace table whose ten rows
- including the Open column and the re-relaxation of $(0,2)$ in step 5 - I reproduced exactly from the
code, and a comparison against Dijkstra and against the opposite tie-breaking rule on the same instance.
Keep the tie-breaking subsection with the 39-versus-400 experiment; keep §1.7.3 and
`figures/ch04/expansions.tex` - every number in that paragraph and its caption checks out against
`figures/data/ch04-expansions.dat`. Keep `code/ch04_astar.py` as it is: it is complete (including the
space-time search, reservation table, horizon and MAPF-style constraint filtering the chapter has yet to
describe), its self-test asserts the chapter's numbers rather than merely running, and it passes.
Finally, keep the voice - patient, second person, intuition before formalism - and the honest
"what goes wrong without the conditions" subsection, which is exactly what a reader working alone needs.
