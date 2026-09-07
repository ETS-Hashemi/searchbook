# Review of Chapter 4 (A* Search) - round 2

Reviewed artefacts: `Overleaf/chapters/ch04-astar.tex` (1608 lines), `Overleaf/figures/ch04/*.tex`
(7 files), `Overleaf/code/ch04_astar.py` (622 lines), `Overleaf/code/figures/gen_ch04_expansions.py`
and `gen_ch04_grids.py`, `Overleaf/figures/data/ch04-expansions.dat`,
`Overleaf/appendices/solutions/ch04-solutions.tex`, `Overleaf/appendices/glossary/ch04-terms.tex`,
`Overleaf/bib/ch04-extra.bib`, `Overleaf/references.bib`, `Overleaf/frontmatter/notation.tex` and
`Overleaf/chapters/ch02-toolbox.tex` (Section 2.x on time), against `STYLE_GUIDE.md` Section 9 (A-H),
`docs/specs/ch04.md` and Week 1 of `docs/core-idea.txt`.

**Build.** `cd Overleaf && ./build.sh ch04-astar` -> status 0. No `!` errors, **no overfull or underfull
boxes at all**, no undefined citations, and the only undefined references are cross-chapter ones
(`ch:ch02`, `ch:ch03`, `ch:ch05`, ..., plus `def:ch02-grid` and `exr:ch03-coding`), which is expected in
a single-chapter build. All three dangling `sec:ch04-*` references of round 1 are gone. Output: 45-page
PDF; the chapter itself is PDF pages 12-35, i.e. **exactly 24 typeset pages** - at the ceiling, not over
it. Listings keep their Python indentation in the PDF (checked with `pdftotext -layout`).

**Code.** `python3 code/ch04_astar.py` -> `ch04_astar: all self-tests passed` (exit 0, a few seconds).
`python3 code/figures/gen_ch04_grids.py` and `gen_ch04_expansions.py` regenerate
`figures/ch04/example.tex`, `figures/ch04/tiebreak.tex` and `figures/data/ch04-expansions.dat`
**byte-identically** to the committed files.

**Numbers.** I re-derived every quantity quoted in the new sections with an independent driver script.
Confirmed: 6 of 40 Manhattan-on-8-connected instances suboptimal; mini example 3 expansions / cost 2
unconstrained and 4 expansions / cost 3 constrained; edge-constraint variant cost 4 in 5 expansions with
path `(0,1),(0,1),(0,1),(1,1),(2,1)`; goal-blocked variant cost 6 with the path printed in the pitfall
box; `H = 1`, `D = 3`, `T_max = 5` on the mini example; corridor path of cost 5 and the provable failure
in **six** expansions; `default_horizon` = 8 and `H = 4` for agent 2 of the corridor (as claimed in the
solution to `exr:ch04-horizon`(c)); all ten rows of `tab:ch04-trace` including the Open column; the
terminal Open set `{(0,5),(1,5),(2,5),(3,0)}`; 39 vs 400 on the empty 20x20 grid; the experiment
paragraph and `fig:ch04-expansions` caption against row `n=100` of the `.dat` file (7451.8/7513.3,
756.2, 3323.6, 371.8, 271.3, ratios 1.0694/1.1197/1.0451/1.0582, all below the stated 1.13). I also
checked the ten solutions in `appendices/solutions/ch04-solutions.tex` against the code: the 4x4
Manhattan-trap instance really returns cost 6 against the optimum 4+sqrt(2)=5.414, and the three
space-time variants of `exr:ch04-spacetime` really give (5, 4, 3) expansions and costs (4, 3, 2).
**Exactly two quantitative claims in the chapter do not reproduce** - see required changes 1 and 2.

**Citations.** All 11 keys used (`hart1968formal`, `hart1972correction`, `dechter1985generalized`,
`pearl1984heuristics`, `russell2020aima`, `pohl1970heuristic`, `silver2005cooperative`, `stern2019mapf`,
`harabor2011jps`, `phillips2011sipp`, `likhachev2003ara`) exist in `references.bib`; the eight keys the
spec mandates are all cited. I can vouch for the bibliographic details of every one of them (venue,
volume, pages, year); nothing is fabricated, and no entry was added to `bib/ch04-extra.bib`.

**Round-1 items.** All 13 required changes of round 1 are genuinely resolved. I re-verified each: the
space-time section (1) is present and is the strongest new material; implementation notes with two
verbatim listings (2); three pitfall boxes (3); the `dronebox` with the three roles and the Week-1
pointer (4); summary box and further-reading paragraph (5); ten graded exercises plus a full solutions
file (6); no undefined `sec:ch04-*` references (7); `figures/ch04/spacetime.tex` is included and cref-ed
(8); `silver2005cooperative` and `stern2019mapf` cited (9); the "three wasted expansions (3,3),(3,2),(3,1)"
correction in caption *and* body (10); the corollary cross-reference now attributes each clause to the
right result (11); "conflict-based search (CBS)" and "multi-agent path finding (MAPF)" expanded at first
use (12); the octile annotation in `heuristics.tex` now reads "3 diagonal + 2 straight moves" (13).
Seven of the eight suggestions were applied as described. **Nothing from round 1 is re-raised below.**

## Verdict

**Minor revision.**

The chapter is now complete against `docs/specs/ch04.md` - I checked every "must cover" item and found
none missing - and against Week 1 of the training plan (graph search; admissible/consistent heuristics;
space-time representation; the coding exercise "implement grid A*, add time as a state variable,
visualise open/closed sets" is `exr:ch04-coding`; the milestone "explain exactly why A* returns an
optimal path" is `thm:ch04-optimal` with its hypotheses spelled out). The theory is correct: I checked
`thm:ch04-invariant`, `thm:ch04-optimal`, `thm:ch04-consistent`, `thm:ch04-surely`,
`thm:ch04-dominance`, `thm:ch04-weighted`, `thm:ch04-metric` and `thm:ch04-static` line by line against
Hart-Nilsson-Raphael, Pearl and Russell-Norvig and found no error. Four issues remain, all local: one
hypothesis in `thm:ch04-horizon` that does not match the code it claims to describe (and is unsound as
written), one row of the space-time trace table that the code does not reproduce, one self-contradictory
sentence in the worked example, and one definition that does not say what the text later claims it says.
Adding two consistency items (F) and one repetition (G) gives seven required changes, every one of them
a one- or two-sentence edit. None is a category-B gap, so the chapter is one short pass from Accept.

**Length.** 24 pages, exactly at the ceiling, against a 16-18 page target in the spec. I looked hard for
padding and found only one clear instance (required change 7, a sentence duplicated verbatim between the
running text and a pitfall box). **Nothing else should be cut**: every remaining section is required
content, and the two candidates the reviser proposed for cutting in the round-1 response
(`lst:ch04-spacetime` and the second half of `ex:ch04-corridor`) are both load-bearing - the listing is
what makes the goal-stay test and the constraint filter concrete, and the corridor example is the only
place where reservation tables, reversed-edge constraints, parked goals and the incompleteness of
prioritized planning are shown working together. Keep them.

## Required changes

1. **`thm:ch04-horizon`: the definition of `H` does not match `default_horizon()`, and as written the
   proof step it supports is false.**
   *Location:* Section `sec:ch04-horizon`, lines 1000-1003 ("Write $H$ for the largest time step that
   appears in any constraint ($H = -1$ if there is none)"), the proof at lines 1019-1021, and the claim
   at line 1033 ("\Cref{eq:ch04-horizon} is what \code{default\_horizon()} returns").
   *Problem:* `ReservationTable.horizon()` (`code/ch04_astar.py` lines 303-308) returns the maximum over
   (i) the times `t` of vertex constraints, (ii) `t+1` for edge constraints, **and (iii) the times at
   which agents park on their goals** (`list(self.parked.values())`). The chapter's `H` omits (iii).
   That omission is not cosmetic: the reservation table of Section `sec:ch04-spacetime` blocks a parked
   goal "for every $t \ge T$", so "the largest time step that appears in any constraint" is either
   infinite or, on the intended reading, silently drops the parking times - and then the proof's step
   "from time $H+1$ on the only forbidden cells are the parked ones, which are forbidden for ever" is
   wrong. An agent that parks at $t = 9$ leaves its cell free at $t \le 8$, so the suffix of $\pi$ from
   $H+1$ need not avoid it, $\gamma$ need not be reachable in the reduced grid, and $T_{\max}$ can be
   too small. The solutions file already follows the code rather than the chapter: the solution to
   `exr:ch04-horizon`(d) states "$H = 0$" for an instance whose only obstruction is an agent parked from
   $t = 0$, where the chapter's definition gives $H = -1$.
   *Fix:* replace the sentence at lines 1000-1003 by: "Write $H$ for the last time step at which the
   table blocks anything: the largest $t$ of a vertex constraint, the largest $t+1$ of an edge
   constraint, and the time from which each parked agent occupies its cell ($H = -1$ if the table is
   empty). This is what \code{ReservationTable.horizon()} computes." Then add one clause to the proof
   after "the only forbidden cells are the parked ones": "every parked agent has arrived by time $H$, so
   from $H+1$ on those cells are blocked for ever." No number in the chapter changes ($H = 1$ on the mini
   example, $H = 4$ for agent 2 of the corridor, both re-verified).
   *Category:* A (also F: text/code mismatch).

2. **`tab:ch04-spacetime`, row 3: the Open column is wrong; the code produces ten entries, not seven.**
   *Location:* line 1187 (`3 & $((1,1),2)$ & 2 & 1 & 3 & $((2,1),3){:}3$, $((1,1),3){:}4$, and the six
   entries of step~2 that are still open`).
   *Problem:* `space_time_astar(grid, s, z, cons, record_open=True)` gives, after step 3, Open =
   `((0,0),1):4, ((0,0),2):5, ((0,1),2):4, ((0,1),3):5, ((0,2),1):4, ((0,2),2):5, ((1,0),3):5,
   ((1,1),3):4, ((1,2),3):5, ((2,1),3):3`. Two errors: three states pushed by the expansion of
   $((1,1),2)$ are missing (`((0,1),3):5`, `((1,0),3):5`, `((1,2),3):5` - the moves back to $(0,1)$ and
   sideways to $(1,0)$ and $(1,2)$), and only **five** of the six entries of step 2 are still open, since
   $((1,1),2)$ is the entry that step 3 popped. A reader doing `exr:ch04-spacetime`(c), which explicitly
   asks to compare expansion counts with this table, will hit the discrepancy.
   *Fix:* row 3, last column -> `$((2,1),3){:}3$, $((1,1),3){:}4$, $((0,1),3){:}5$, $((1,0),3){:}5$,
   $((1,2),3){:}5$, and the five entries of step~2 that are still open`.
   *Category:* A (also D).

3. **Worked example: a self-contradictory sentence about $(3,1)$ and $(0,4)$, and a wrong claim about
   when the frontier reaches $\fcost = 13$.**
   *Location:* lines 417-420, "The cell $(3, 1)$ is reached one pop after $(0, 4)$, because both carry
   $\fcost = 13$ and $11$ respectively; the expansion order is $\dots$. Only after these does the
   frontier reach $\fcost = 13$, and the search crosses the top row $\dots$".
   *Problem:* "both carry $\fcost = 13$ and $11$ respectively" contradicts itself. The values are
   $\fcost(0,4) = 4 + 7 = 11$ and $\fcost(3,1) = 10 + 3 = 13$ (verified). And "only after these does the
   frontier reach $\fcost = 13$" is false, because $(3,1)$, which is inside the listed sequence, is
   itself expanded at $\fcost = 13$.
   *Fix:* "The cell $(0,4)$ carries $\fcost = 11$ and $(3,1)$ carries $\fcost = 13$, so $(0,4)$ is popped
   first and $(3,1)$ one pop later; the expansion order is $\dots, (3,4), (3,3), (3,2), (0,4), (3,1),
   (3,5), \dots$. From $(3,1)$ on the frontier is at $\fcost = 13$: the search crosses the top row
   $(3,5), (4,5), (5,5)$ and descends to the goal, which is popped at step~21 with $\gcost = 13$."
   *Category:* A (the two $\fcost$ values as written are wrong), also C.

4. **`def:ch04-constraints` does not cover the agent's occupancy after arrival, but Section
   `sec:ch04-goalstay` claims it does.**
   *Location:* definition at lines 919-930; the claim at lines 973-975 ("the returned path $\pi$ can be
   extended by waiting at $\gamma$ for ever without violating a constraint, which is what
   \cref{def:ch04-constraints} demands of a MAPF solution").
   *Problem:* the definition only quantifies over $0 \le t \le T$, so nothing in it demands anything
   about $t > T$; the whole point of `def:ch04-goalstay` therefore rests on a condition the referenced
   definition never states. Chapter 2 has the missing piece (`def:ch02-time-indexed-path`, stay-at-goal
   convention) and the chapter never uses it.
   *Fix:* append one sentence to `def:ch04-constraints`: "By the stay-at-goal convention of
   \cref{def:ch02-time-indexed-path} the agent still occupies $\gamma$ at every $t > T$, so a path that
   respects the constraints must also avoid $\langle a, \gamma, t\rangle$ for every $t > T$." The
   sentence at lines 973-975 then says exactly what it claims.
   *Category:* C (also A: a definition that does not support the property proved from it).

5. **Section `sec:ch04-spacetime` re-defines Chapter 2's space-time state, wait action and
   time-expanded graph without referring to them, and indexes the concept under a second key.**
   *Location:* `def:ch04-spacetime`, lines 881-890 (including `\index{state!space-time}` and
   `\index{time-expanded graph}` and `\index{wait action}`); Section `sec:ch04-goalstay`, lines 957-977.
   *Problem:* `chapters/ch02-toolbox.tex` already defines "Space-time state, move and wait actions"
   (`def:ch02-space-time-state`, line 191), "Time-expanded graph"
   (`def:ch02-time-expanded-graph`, line 198) and the stay-at-goal convention
   (`def:ch02-time-indexed-path`, line 212), with index entries `\index{space-time state}`,
   `\index{time-expanded graph}` and `\index{wait action}`. Chapter 4 restates all three from scratch
   and uses `\index{state!space-time}`, so the same concept produces two unrelated entries in the book
   index (STYLE_GUIDE Sections 3 and 9F).
   *Fix:* open `def:ch04-spacetime` with "Recall the space-time state and the time-expanded graph of
   \cref{def:ch02-space-time-state,def:ch02-time-expanded-graph}; here every action, move or wait, costs
   one time step, so ..."; change `\index{state!space-time}` to `\index{space-time state}`; and in
   Section `sec:ch04-goalstay` name the convention it uses: "by the stay-at-goal convention of
   \cref{def:ch02-time-indexed-path}".
   *Category:* F.

6. **The MAPF paragraph never points to the chapter that formalises MAPF.**
   *Location:* lines 866-877 ("the standard formulation is the one of Stern et al.~\cite{stern2019mapf}
   ... \Cref{ch:ch08,ch:ch09,ch:ch10} build three planners on top of that formulation").
   *Problem:* `ch:ch07` ("The Multi-Agent Path Finding Problem") is the chapter that defines the MAPF
   problem, conflicts and constraints; Chapter 2 already forwards the reader there. Chapter 4 introduces
   the formulation and the constraint notation without a single reference to it, so a reader who wants
   the full problem statement is sent to the planner chapters instead.
   *Fix:* "...the standard formulation is the one of Stern et al.~\cite{stern2019mapf}, stated in full in
   \cref{ch:ch07}: ..." and change the following sentence to
   "\Cref{ch:ch08,ch:ch09,ch:ch10} build three planners on top of it."
   *Category:* F.

7. **The "6 of 40 instances" experiment is stated twice, almost word for word.**
   *Location:* lines 258-261 (running text after `thm:ch04-metric`) and lines 288-291 (inside the
   `pitfall` box "The Manhattan distance on an 8-connected grid").
   *Problem:* the two sentences differ only in "returns a path longer than optimal" vs "returns a
   strictly longer path"; the chapter is exactly at the 24-page ceiling, and this is the one piece of
   genuine repetition in it.
   *Fix:* delete the second half of the sentence at lines 258-261, i.e. end that paragraph at
   "\Cref{tab:ch04-heuristics} summarises the result. The Manhattan distance is the classic example of a
   heuristic that is perfect for one grid and wrong for another." and let the pitfall box (which is two
   paragraphs later and quotes the same run) carry the experiment.
   *Category:* G.

## Suggestions

* `thm:ch04-static` ("The static heuristic is consistent") is never `\cref`-ed. The natural place is the
  sentence after it at lines 1083-1086 ("The consistency of $\hcost$ means the search inherits
  \cref{thm:ch04-consistent}") - write "By \cref{thm:ch04-static} the search inherits ...".
* In `thm:ch04-horizon`, `D` is "the largest number of moves from any cell to $\gamma$" - strictly, from
  any cell *from which $\gamma$ is reachable* in the reduced grid; that is what
  `max(reach.values())` in `default_horizon()` computes. One parenthesis would close the gap.
* `alg:ch04-astar`'s `\KwIn` lists a goal test, but the signature `\AstarSearch{$G$, $s$, $\hcost$, $w$}`
  does not carry it (nor the costs `c`). Either add them to the signature or drop them from `\KwIn`.
* The complexity subsection cites Pearl for the $\hcost^* - \hcost = \bigO{\log \hcost^*}$ condition but
  does not name the contrast case. Half a sentence - "a heuristic with constant relative error, e.g.
  $\hcost = (1-\varepsilon)\hcost^*$, still gives exponentially many expansions" - would make the point
  land, and it is exactly the result that motivates weighted \astar two sections later.
* `ex:ch04-corridor` says "which alone takes 3 steps"; the self-test asserts that number
  (`space_time_astar(grid,(3,0),(0,0)).cost == 3.0`), so consider adding "(the self-test checks this)"
  for symmetry with the rest of the chapter, where every number is attributed.
* The corridor failure "in finite time, six expansions" would be even more convincing with the horizon
  that makes it finite: $H = 4$, $D = 3$, $T_{\max} = 8$ (both verified). One clause.
* `fig:ch04-spacetime` draws only the middle row of the grid. A one-line note in the caption saying that
  the states of the other two rows exist but are never expanded would stop a careful reader from
  wondering where $((0,0),1)$ and $((0,2),1)$ of `tab:ch04-spacetime` live.

## What must be kept

The proof architecture is the best thing in this chapter and must survive untouched. `thm:ch04-invariant`
is stated once, in a form that is deliberately about an arbitrary node rather than the goal, and then
carries the optimality theorem, the no-re-expansion theorem *and* the weighted-A* bound; I checked every
step, including the delicate case analysis on the first index whose node has not yet been expanded with
its optimal $\gcost$, the treatment of re-opening inside the invariant, and the observation that the
invariant never touches the heuristic and therefore transfers verbatim to the key $\gcost + w\hcost$.
That is a cleaner and more honest treatment than the three-separate-proofs version found in most
textbooks. `thm:ch04-consistent`, `thm:ch04-surely` and `thm:ch04-dominance` are correctly stated and
correctly proved, with the tie-breaking caveat on $\fcost = C^*$ made explicit where most authors leave
it implicit, and the Dechter-Pearl optimality claim is now correctly fenced by naming the class it holds
over. `thm:ch04-metric` remains exactly the right lemma: it makes all four grid heuristics fall out of
one inequality per move type, and `tab:ch04-heuristics` with the Manhattan-on-8-connected trap - backed
by a reproducible experiment and a pitfall box - is the clearest short treatment of that trap I have
read.

The new space-time section is a genuine asset and should be preserved essentially as it is. It gets the
things that are usually got wrong right: the goal-stay test as a per-goal quantity $t_\gamma$ rather
than a global horizon (with the pitfall box explaining what the global variant costs), the reversed-edge
reservation that prevents swaps, the parked goal, the static-distance heuristic with the argument for
why it is worth computing there and not for a single query, and a real completeness/termination
proposition instead of an arbitrary cut-off. `ex:ch04-corridor` earns its space: it is the only place in
Part II where a reservation table, a forced detour into a passing bay and the incompleteness of
prioritized planning are demonstrated on one instance whose every number the self-test asserts.

Keep the worked example and its trace table exactly as they are (apart from change 3): all ten rows,
including the Open column and the re-relaxation of $(0,2)$ in step 5, reproduce from the code, and the
instance is chosen so that the search genuinely walks into a dead end that the Manhattan distance cannot
see. Keep the tie-breaking subsection with the 39-versus-400 experiment, the random-grid experiment and
`figures/ch04/expansions.tex`, the six implementation paragraphs (the `round(f, 9)` / `EPS` discussion is
the kind of detail that saves a reader a lost weekend), all three pitfall boxes, the ten exercises with
their difficulty spread, and the solutions file - I checked its numbers against the code and every one of
them holds, including the 4x4 Manhattan-trap instance and the ring-map counterexample for the horizon.
Finally, keep `code/ch04_astar.py` unchanged: it is complete, fast, and its self-test asserts the
chapter's numbers rather than merely running.

## Response to review (round 2)

All seven required changes are applied; the numbers were re-verified by running
`code/ch04_astar.py` before and after. Build status 0, no errors, no undefined
ch04 references, no overfull box above 15 pt; chapter body unchanged at 24 pages.
`python3 code/ch04_astar.py` prints `ch04_astar: all self-tests passed`. The code
was not touched, so no `.dat` file needed regenerating.

**Required 1 — the definition of `H` in `sec:ch04-horizon` (category A). Done.**
The definition now reads: "Write `H` for the last time step at which the table
blocks anything: the largest `t` of a vertex constraint, the largest `t+1` of an
edge constraint, and the time from which each parked agent occupies its cell
(`H = -1` if the table is empty). This is what `ReservationTable.horizon()`
computes." The proof of `thm:ch04-horizon` gained the missing clause: "the only
forbidden cells are the parked ones; every parked agent has arrived by time `H`,
so from `H+1` on those cells are blocked for ever." The claim at the end of the
subsection that `eq:ch04-horizon` is what `default_horizon()` returns is now
true as written and was left alone. Re-verified against the code: mini example
`H = 1`, `D = 3`, `T_max = 5`; corridor agent 2 `H = 4`, `D = 3`, `T_max = 8`.
The solutions file is now consistent with the chapter, including
`exr:ch04-horizon(d)` (`H = 0` for the agent parked from `t = 0`) and
`exr:ch04-spacetime(d)` (`H = 2`). While rewriting the sentence I also folded in
suggestion 2: `D` is now defined "among the cells from which `gamma` is
reachable at all", which is what `max(reach.values())` computes.

**Required 2 — row 3 of `tab:ch04-spacetime` (category A). Done.**
Re-ran `space_time_astar(grid, s, z, cons, record_open=True)`; the Open snapshot
after step 3 has exactly the ten entries the reviewer lists. Row 3's last column
now reads `((2,1),3):3, ((1,1),3):4, ((0,1),3):5, ((1,0),3):5, ((1,2),3):5, and
the five entries of step 2 that are still open`. The other three rows reproduce
unchanged from the code and were not touched.

**Required 3 — the `f` values in `sec:ch04-example` (category A). Done.**
Re-ran the worked example: `f(0,4) = 4 + 7 = 11` at expansion 14 and
`f(3,1) = 10 + 3 = 13` at expansion 15, with the goal popped at step 21 with
`g = 13`. The self-contradictory sentence was replaced by the reviewer's text
verbatim.

**Required 4 — `def:ch04-constraints` says nothing about `t > T` (category C). Done.**
Appended to the definition: "By the stay-at-goal convention of
`def:ch02-time-indexed-path` the agent still occupies `gamma = pi_T` at every
`t > T`, so a path that respects the constraints must also avoid
`<a, gamma, t>` for every `t > T`." The goal-stay argument in
`sec:ch04-goalstay` now rests on something the referenced definition states.

**Required 5 — duplicated Chapter 2 concepts and a split index entry (category F). Done.**
`def:ch04-spacetime` now opens with "Recall the space-time state and the
time-expanded graph of `\cref{def:ch02-space-time-state,def:ch02-time-expanded-graph}`;
here every action, move or wait, costs one time step, so time and cost
coincide."; `\index{state!space-time}` became `\index{space-time state}`, which
merges with the Chapter 2 entry; and `sec:ch04-goalstay` now names the
convention ("by the stay-at-goal convention of
`\cref{def:ch02-time-indexed-path}`"). Both Chapter 2 references resolve in the
build.

**Required 6 — missing forward reference to `ch:ch07` (category F). Done.**
The opening paragraph of `sec:ch04-spacetime` now reads "the standard
formulation is the one of Stern et al. [stern2019mapf], stated in full in
`\cref{ch:ch07}`: ..." and the next sentence is "`\Cref{ch:ch08,ch:ch09,ch:ch10}`
build three planners on top of it."

**Required 7 — the "6 of 40 instances" experiment stated twice (category G). Done.**
The running-text copy after `thm:ch04-metric` is gone; that paragraph now ends
"...perfect for one grid and wrong for another." The pitfall box two paragraphs
later carries the experiment, and "6 of 40" now occurs exactly once in the
chapter.

**Suggestions.** All seven applied, each in one clause. (1) The sentence after
`thm:ch04-static` now reads "By `\cref{thm:ch04-static}` the search inherits
`\cref{thm:ch04-consistent}`", so the proposition is cited. (2) Folded into
required change 1 above. (3) `alg:ch04-astar`'s signature is now
`AStar(G, s, isGoal, h, w)`, matching its `\KwIn` (the costs `c` stay inside
`G`, as `\KwIn` already says). (4) The complexity paragraph now names the
contrast case: "a heuristic with `h = (1-eps) h*` still gives exponentially many
expansions --- which is why `\cref{sec:ch04-variants}` buys speed by giving up
optimality rather than by sharpening `h`." (5) `ex:ch04-corridor` says agent 2's
trip "on the empty corridor takes 3 steps" and the example now closes with
"Every number in this example is asserted by the self-test of
`ch04_astar.py`." (6) The corridor failure now carries its horizon: "six
expansions, thanks to `\cref{thm:ch04-horizon}`: here `H = 4` and `D = 3`, so
`T_max = 8`" --- both re-verified against `default_horizon()`. (7)
`fig:ch04-spacetime`'s caption gained "The states of the top and bottom rows,
such as `((0,0),1)` and `((0,2),1)` in `\cref{tab:ch04-spacetime}`, exist too but
are never expanded, so the drawing omits them."

**What was kept.** Untouched: the whole proof architecture
(`thm:ch04-invariant` stated once for an arbitrary node and carrying
optimality, no-re-expansion and the weighted-A* bound; `thm:ch04-consistent`,
`thm:ch04-surely`, `thm:ch04-dominance`, `thm:ch04-metric`), `tab:ch04-heuristics`
and its pitfall box, the worked example and all ten rows of `tab:ch04-trace`
including the re-relaxation of `(0,2)` in step 5, the tie-breaking 39-versus-400
and random-grid experiments and `figures/ch04/expansions.tex`, the six
implementation paragraphs, all three pitfall boxes, `ex:ch04-corridor`,
`lst:ch04-spacetime`, the ten exercises, the solutions and glossary files, and
`code/ch04_astar.py`. No required content was removed to save space; the only
deletion is the duplicated sentence required change 7 asks for.
