# Review of Chapter 4 (A* Search) - round 2

Reviewed artefacts: `Overleaf/chapters/ch04-astar.tex` (1634 lines), the seven figure files
`Overleaf/figures/ch04/{idea,heuristics,example,inadmissible,tiebreak,expansions,spacetime}.tex`,
`Overleaf/code/ch04_astar.py` (622 lines) and `Overleaf/code/figures/gen_ch04_expansions.py`,
the data file `Overleaf/figures/data/ch04-expansions.dat`,
`Overleaf/appendices/solutions/ch04-solutions.tex`, `Overleaf/appendices/glossary/ch04-terms.tex`,
`Overleaf/bib/ch04-extra.bib` and `Overleaf/references.bib`, against `STYLE_GUIDE.md` section 9,
`docs/specs/ch04.md` and Week 1 of `docs/core-idea.txt`. Round 1 is `reviews/ch04-round1.md`;
all three of its required changes and all six of its suggestions were verified as applied
(details below), and none of them is re-raised here.

**Build.** `cd Overleaf && ./build.sh ch04-astar` produces `build/only-ch04-astar.pdf`
(54 pages) with **no `!` errors** and exactly one overfull box above 15 pt (29.10 pt, from the
*List of Algorithms* entry of the RRT chapter, line 38 of the front matter, not from Chapter 4).
The script exits with status 12 rather than 0; the cause is latexmk's
"Latex failed to resolve 39 reference(s)", and all 39 are cross-chapter references produced by the
front matter and other chapters in an `\includeonly` build. Only two of them belong to Chapter 4
(`ch:ch13` and `ch:ch14`, line 1430, in the drone box), and section 7 of the style guide explicitly
permits references to other chapters to be unresolved in a single-chapter build. Nothing in
Chapter 4 needs to change for this; I record it so the next builder is not alarmed by the
difference from round 1.

**Chapter length.** The chapter occupies pp. 21-44 of the single-chapter PDF, i.e. **24 pages**
(front matter and back matter excluded) - unchanged from round 1, exactly at the cap. I require
no cuts: every section is a "must cover" item of `docs/specs/ch04.md`, and I found no repetition,
no redundant example and no padded prose.

**Code.** `python3 code/ch04_astar.py` prints `ch04_astar: all self-tests passed` (exit 0,
under one second). Both listings (`lst:ch04-astar`, `lst:ch04-spacetime`) are byte-for-byte
verbatim excerpts of the file (checked mechanically; 35 and 22 lines, both under the 45-line cap).

**Independent recomputation.** I re-derived the chapter's numbers with my own A* and space-time A*
written from the pseudocode alone (not by importing the chapter code), and everything matches:
cost 13 with 21 expansions; the ten rows of `tab:ch04-trace` including the `Open` column; the
expansion order `(3,4),(3,3),(3,2),(0,4),(3,1),(3,5)`; the goal generated at step 20 and popped at
step 21; the four cells left in `Open` (`(0,5),(1,5),(2,5)` at `f = 13`, `(3,0)` at `f = 15`);
Dijkstra 26 expansions with `set(dijkstra) - set(astar) = {(0,5),(1,5),(2,5),(3,0),(4,0)}` and
`set(astar) - set(dijkstra) = {}` (the caption fixed in round 1 is correct, including
"leaves in Open or never generates": `(4,0)` is indeed never generated); 24 expansions with
small-`g` ties; `9 + 2*sqrt(2) = 11.828` with 24 expansions on the 8-connected grid; 39 versus 400
expansions on the empty 20x20 grid, both at cost 38; "6 of 40" suboptimal Manhattan runs (I re-ran
the loop with the seed of the self-test); the space-time counts 3 / 4 / 5 / 6 expansions and the
costs 2 / 3 / 4 / 6 with the exact paths printed in the text; the corridor path
`(3,0),(2,0),(2,1),(2,0),(1,0),(0,0)` of cost 5 and the six-expansion failure from `(4,0)`;
`H = 4`, `D = 3`, `T_max = 8` for the corridor and `H = 1`, `D = 3`, `T_max = 5` for the mini
example; and, in the solutions, `h*(1,4) = 8`, `h*(3,1) = 5`, the exercise-4.9 variants
(cost 4 / 5 expansions, cost 3 / 4 expansions, cost 2 / 3 expansions) and the ring counterexample
(raw eccentricity 6, naive horizon 7, true arrival 10, `D = 10` with the parked cell as a wall).
`figures/data/ch04-expansions.dat` at `n = 100` reproduces the prose exactly (free 7513.3,
Dijkstra 7451.8, A*-Manhattan 756.2, A*-octile 3323.6, wA*(2) 371.8 / 271.3, ratios
1.0694 / 1.1197 / 1.0451 / 1.0582, all below 1.13).

**Technical audit.** I checked every definition, lemma, theorem, proof, formula, pseudocode line
and complexity claim against Hart-Nilsson-Raphael 1968/1972, Pearl 1984, Dechter-Pearl 1985,
Pohl 1970, Likhachev-Gordon-Thrun 2003, Martelli 1977, Silver 2005 and Stern et al. 2019, and
found no error. Specifically: `thm:ch04-invariant` (the minimal-index argument, including the
"never stale, never popped" step), `thm:ch04-optimal`, `thm:ch04-consistent` (i) and (ii),
`thm:ch04-surely`, `thm:ch04-dominance` with its `f = C*` caveat and its correctly narrowed
statement of what Dechter and Pearl proved, `thm:ch04-weighted`, `thm:ch04-metric`,
`thm:ch04-static` and `thm:ch04-horizon` (I checked the `H = -1` and `v = gamma` edge cases of the
last one separately) are all correct as stated. The claim that the four grid distances are norms
holds for the octile distance too: `max + (sqrt2-1)min = (sqrt2-1)*l1 + (2-sqrt2)*l_inf`, a
positive combination of two norms. Table 4.1 is correct row by row, including
octile > Euclidean > Chebyshev on 8-connected grids.

**Citations.** Every key resolves (`hart1968formal`, `hart1972correction`, `dechter1985generalized`,
`pearl1984heuristics`, `russell2020aima`, `pohl1970heuristic`, `silver2005cooperative`,
`stern2019mapf`, `likhachev2003ara`, `harabor2011jps`, `phillips2011sipp` in `references.bib`,
`martelli1977complexity` in `bib/ch04-extra.bib`). I can vouch for the authors, title, venue,
volume, pages and year of all twelve, including the Martelli entry added in round 1
(*Artificial Intelligence* 8(1):1-13, 1977). No fabricated reference. All eight keys demanded by
the spec are cited.

**Completeness.** Every "must cover" item of `docs/specs/ch04.md` is present, and the Week 1 items
of the training plan (graph search, admissible/consistent heuristics, space-time representation,
grid A*, time as a state variable, visualising open/closed sets) are all covered. 37 index entries
(>= 15), 7 figures (>= 4, all `\cref`-referenced, consistent `sb...` styles, captions that say what
to notice), 3 tables, 2 algorithms, 2 listings, 3 pitfall boxes (>= 2), 10 exercises graded
1,1,2,2,2,2,2,3,3,3 with the Week-1 coding exercise as `exr:ch04-coding`, and a solution for each.

**Round-1 items, verified resolved.** (1) The `fig:ch04-example` caption now names the five extra
Dijkstra cells, and my independent recomputation confirms the new wording in full. (2) The
`keyidea` box now carries the re-opening proviso and points at
`line~\ref{alg:ch04-astar:reopen}`, matching `thm:ch04-optimal`, the summary and the
`reopen=False -> cost 5` assertion. (3) ECBS, ORCA and DWA are expanded at first use. The six
suggestions were also applied (cross-reference to `sec:ch04-experiment`, the `closed`-set clause in
the `lst:ch04-spacetime` caption, the Martelli sentence, the 4-connected octile table cell, the
`h*` codomain, and the removal of the `(1-eps)h*` aside).

## Verdict

**Minor revision.**

This is an unusually strong chapter and it survived my independent audit intact: no wrong formula,
no broken proof, no unproved theorem, no number that the code fails to reproduce, no missing
spec item. Three small things are left. One is a statement about the code that is not true as
written (required change 1); the other two are consistency items that the style guide asks for and
that round 1 established the precedent for. All three are one- to four-line edits and none touches
the structure, the proofs, the figures or the algorithms.

## Required changes

1. **`chapters/ch04-astar.tex` line 1242 (`ex:ch04-corridor`) and line 1216
   (`sec:ch04-spacetime`, the "two variations" paragraph); `code/ch04_astar.py`, `_self_test()`,
   lines 560-600: the chapter claims a test coverage that the self-test does not have.**
   Line 1242 says "Every number in this example is asserted by the self-test of
   `ch04_astar.py`", but of Example 4.21 the self-test asserts only `p2`, its length 5 and
   `path is None` for the start `(4,0)`; the **six expansions**, and `H = 4`, `D = 3`,
   `T_max = 8`, are never asserted (`default_horizon()` and `ReservationTable.horizon()` are not
   called anywhere in `_self_test()`). Likewise line 1216 says the two mini-example variations are
   "both in the self-test" and then quotes "cost 4 after **five expansions**", while the test
   asserts only `res.cost == 4.0` (line 565). The numbers themselves are right - I reproduced
   6, 5, `H = 4` and `T_max = 8` both with the chapter's own code and with an independent
   re-implementation - so this is a coverage claim, not a wrong number, but as written it is false.
   Concrete fix (preferred): extend the self-test, after line 565 and after the corridor block,
   with
   ```python
   assert res.num_expansions == 5                     # edge-constraint variant
   ...
   fail = space_time_astar(grid, (4, 0), (0, 0), table)
   assert fail.path is None and fail.num_expansions == 6
   assert table.horizon() == 4                        # H
   assert default_horizon(grid, (0, 0), table, 4) == 8 # T_max = H + 1 + D
   ```
   (all four hold; I ran them). If the code must stay untouched instead, replace "asserted by" with
   "produced by" on line 1242 and drop "both in the self-test" on line 1216. *Category A.*

2. **`chapters/ch04-astar.tex` lines 44-46 (`sec:ch04-motivation`): LPA\* and ARA\* are used
   without being expanded at first use in this chapter.** Section 3 of `STYLE_GUIDE.md` requires
   every acronym to be defined at first use *in every chapter*; round 1 applied exactly this rule to
   ECBS, ORCA and DWA. `\lpastar` and `\arastar` expand to the bare strings `LPA*` and `ARA*`
   (`searchbook.sty` lines 296-297), and their first occurrence in this chapter is line 45-46,
   with no expansion; `\cref{ch:ch05}` and `\cref{ch:ch06}` do expand them in their own chapters.
   Concrete fix: write "the incremental planners of \cref{ch:ch05} (lifelong planning \astar,
   \lpastar, and \dstarlite) and the anytime planner of \cref{ch:ch06} (anytime repairing \astar,
   \arastar)". *Category F.*

3. **`chapters/ch04-astar.tex` line 1017 (`sec:ch04-horizon`): the symbol $H$ collides with the
   book's notation and with the word "horizon" used three lines later.** In
   `\cref{def:ch02-time-indexed-path}` the letter $H$ is the *horizon of a stored time-indexed
   path* ("the last index $H$ is the horizon of the stored list"), and the notation table
   (`frontmatter/notation.tex`, line 75) reserves $T$ for the planning horizon. Here $H$ is the
   last blocked time of the reservation table, while the *search* horizon is $T_{\max}$ - and the
   method that returns $H$ is called `ReservationTable.horizon()`. A reader coming from
   \cref{ch:ch02}, or a reader of \cref{ch:ch08,ch:ch09} who cites `thm:ch04-horizon`, will trip on
   this. Concrete fix: after "Write $H$ for the last time step at which the table blocks anything:"
   add the parenthesis "(the letter $H$ is the horizon of a stored path in
   \cref{def:ch02-time-indexed-path}; here it is a property of the constraint table, and the horizon
   of the *search* is $T_{\max}$)". No renaming of $H$ is needed, so the code, the solutions and
   `eq:ch04-horizon` stay as they are. *Category F.*

## Suggestions

* **Line 410 (`sec:ch04-example`).** "steps~2--4 then walk up the column $x = 1$: every cell there
  has $\fcost = 7$" reads as a claim about the whole column, but $(1,3)$ and $(1,4)$ have
  $\fcost = 9$ and $11$. Write "the three cells expanded there have $\fcost = 7$".
* **Line 1131 (`alg:ch04-spacetime`).** `\ForEach{$v' \in \{v\} \cup \Succ(v)$}` uses $\Succ$ as a
  set of vertices, while `def:ch04-problem` defines it as a set of pairs $(n', c(n,n'))$. Write
  $\{v\} \cup \{v' : (v', c) \in \Succ(v)\}$, or add "on the unit-cost grid we write $\Succ(v)$ for
  the cells alone" to the walkthrough.
* **`alg:ch04-spacetime` line~\ref{alg:ch04-spacetime:hopeless} and `space_time_astar()`.** Neither
  tests whether the *start* state $(s,0)$ is itself forbidden. The realistic case is a previously
  planned agent whose goal is this agent's start and which parks there from $t = 0$; the search
  would then return a path whose first state violates the table. One extra clause
  ("or $(s,0) \in R$") on the hopeless-case line, or one sentence saying that the caller guarantees
  a free start, would close it.
* **Line 731 (`sec:ch04-dominance`).** "The theorem also shows why the maximum of several admissible
  heuristics is admissible and never worse than any of them" - the theorem gives the second half
  only; admissibility of the maximum is `exr:ch04-max`(a). Reword to "...why the maximum of several
  admissible heuristics (`\cref{exr:ch04-max}`) is never worse than any of them".
* **Line 683 (`sec:ch04-properties`, Complexity).** I can vouch for the Pearl book and for the
  $\hcost^* - \hcost = \bigO{\log \hcost^*}$ result, but not for the chapter locator "ch.~6".
  Please confirm it against a copy, or cite the book without the chapter.
* **Length.** At 24 pages the chapter is at the cap. Nothing here is padding, so I require no cuts;
  if room is ever needed for the book as a whole, the most compressible spot remains
  `ex:ch04-corridor` (about two thirds of a page), whose prioritized-planning lesson is re-taught
  in `\cref{ch:ch08}` - but it is referenced by `exr:ch04-coding`(c) and `exr:ch04-horizon`(c), so
  cutting it costs more than it saves.
* **Build.** Consider noting in the repository (not in the chapter) that `build.sh` inherits
  latexmk's exit code 12 whenever any cross-chapter reference is unresolved, which is the normal
  state of every single-chapter build.

## What must be kept

Keep the proof architecture. One invariant - `thm:ch04-invariant`, "an optimal-path node is always
open" - is proved once and then carries optimality with an admissible heuristic, no re-expansion
with a consistent one, and the weighted-A* bound, with the explicit remark that the lemma never
touches the heuristic. I checked the minimal-index argument line by line, including the step that
the entry carrying $\gcost^*(n_i)$ can be neither stale nor already popped; it is correct and it is
better than the version in most textbooks. Keep `thm:ch04-surely` with its honest "may or may not
expand nodes with $\fcost = C^*$", the matching caveat in `thm:ch04-dominance`, and the precise
statement of what Dechter and Pearl proved together with the sentence saying what it does *not*
claim. Keep the whole space-time section: `def:ch04-goalstay`, the pitfall about the too-strong
$t \ge H$ goal test, and `thm:ch04-horizon` with its $T_{\max} = H + 1 + D$ bound and proof, which
is correct in the edge cases I probed and which `\cref{ch:ch08,ch:ch09,ch:ch10}` can now simply
cite. Keep the static-distance heuristic argument of `sec:ch04-static` - "one backward search per
agent instead of thousands" is the single most useful implementation insight in the chapter. Keep
the floating-point paragraph (`round(f, 9)`, `EPS`), the `(f, -g, counter)` discussion and the
reason the counter exists, the three pitfall boxes, all seven figures (the disc-versus-ellipse
pairing of `fig:ch04-idea` and the time-layer drawing of `fig:ch04-spacetime` are exemplary), the
ten well-graded exercises with their unusually complete solutions, and the discipline of deriving
every quoted number from `ch04_astar.py` - required change 1 asks only that the last three numbers
be brought inside the same net.
