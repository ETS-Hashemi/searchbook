# Review of Chapter 10 (Bounded-Suboptimal Search: ECBS) - round 1

Reviewed artefacts: `Overleaf/chapters/ch10-ecbs.tex` (1491 lines), figures
`Overleaf/figures/ch10/{idea,focal-lowlevel,example-instance,example-trees,benchmark}.tex`,
data `Overleaf/figures/data/ch10-benchmark.dat`, generator
`Overleaf/code/figures/gen_ch10_benchmark.py`, code `Overleaf/code/ch10_ecbs.py`,
`Overleaf/appendices/solutions/ch10-solutions.tex`,
`Overleaf/appendices/glossary/ch10-terms.tex`, against `STYLE_GUIDE.md` section 9,
`docs/specs/ch10.md` and `docs/core-idea.txt` (Week 5).

Build: `./build.sh ch10-ecbs` exits 0, no `!` errors, no undefined label or citation
belonging to this chapter (the `??` in the text are all cross-chapter refs to ch05,
ch06, ch11, ch13, ch14, ch18, ch20, ch24, which is expected in a single-chapter build),
two overfull hboxes of 3.5 pt and 1.5 pt (both below the 15 pt threshold).
Length: pages 20-42 of `build/only-ch10-ecbs.pdf` are the chapter, i.e. **23 pages**,
inside the 24-page ceiling (above the 13-15 pages of the spec; see Suggestions).

Code: `python3 code/ch10_ecbs.py` passes in 0.3 s ("45 random instances checked
against CBS"). I re-ran the worked example and the low-level example independently.
**Every number quoted in the chapter is reproduced by the code**, specifically
`tab:ch10-example-compare` (CBS 12/7/13/12/136; w=1.05 12/7/13/12/136;
w=1.1 13/4/7/12/61; w=1.2 13/2/3/11/37; w=1.5 13/1/1/11/20), both trace tables
(node ids, costs, LBs, h_c, F/O flags all match the printed traces), the
`w = 1.5` root detour `(3,0),(2,0),(1,0),(0,0),(0,1),(0,2),(1,2),(1,3)` of cost 7,
Example 10.1 (cost 4 / bound 3 / 5th selection for `w = 1.5`; cost 3 / one conflict /
3 expansions for `w = 1`), and every entry of `tab:ch10-benchmark` and of the
benchmark prose against `ch10-benchmark.dat`. I also verified by exhaustive
enumeration the non-obvious claim on p. 509-518 that all four conflict-free cost-6
paths of `a_3` pass through the state `(2,1)` at `t = 3`, and I checked the
solutions of `exr:ch10-lowlevel-threshold`(c) (`w=1.5`: cost 3, one conflict,
bound 3, four expansions; `w=2`: waits twice, cost 5, no conflict, bound 3) against
`focal_space_time_astar`. All correct.

Theory: I checked `thm:ch10-invariant`, `thm:ch10-focal`, `thm:ch10-lowlevel-lb`,
`thm:ch10-consistent`, `thm:ch10-ecbs` and `thm:ch10-terminates` line by line against
Pearl & Kim (1982) and Barer et al. (2014). The proofs are sound; the statement that
weighted A* is a special case of focal search (Section 10.6.1) is correct
(`f(n*) <= g(n*) + w h(n*) <= g(n_min) + w h(n_min) <= w f_min`), the `w_H w_L`
guarantee for BCBS matches Barer et al., and the EES selection rule matches
Thayer & Ruml (2011). Two defects remain, both local.

## Verdict

**Minor revision.** Two required changes in category A, both repairable by editing a
single sentence, plus three consistency/notation items in F. Nothing in B, C, D or E
is missing: the chapter covers every "must cover" item of `docs/specs/ch10.md` and
every Week-5 item of the training plan, it has 5 figures, 5 tables, 2 algorithms,
2 listings, 3 pitfall boxes, a drone box, 8 exercises with difficulties 1,1,2,2,2,3,3,3
including the Week-5 coding exercise and a proof exercise on the bound, 25+ index
entries, and 13 citations that all resolve (12 in `references.bib`, `thayer2011bounded`
in `bib/ch10-extra.bib`; authors, titles, venues and years of all of them are correct
as far as I can vouch).

## Required changes

1. **Section 10.5 (`sec:ch10-example`), line 508-509, "The root" paragraph:
   a statement that the chapter itself contradicts.**
   The text reads "The root therefore has $\cost = 11$, per-agent bounds $(2, 4, 5)$,
   $\mathrm{LB} = 11$ and $h_c = 1$, for \cbs ($w = 1$) and for \ecbs with every $w$
   we try." This is false for two of the five runs that the section actually reports.
   For `w = 1.5` (and `w = 2`) the low level of `a_3` already returns the
   conflict-free detour of cost 7 at the root, so the root has cost 13, bounds
   $(2,4,5)$, $\mathrm{LB} = 11$ and $h_c = 0$ - which is exactly what the "Other
   values of $w$" paragraph says twenty lines later and what
   `tab:ch10-example-compare` records (1 CT node expanded, 1 generated). Verified
   with `ecbs(worked_example(), 1.5)`.
   *Fix:* replace "and for \ecbs with every $w$ we try" by "and for \ecbs with
   $w \le 1.2$; for $w = 1.5$ the root itself already changes, as the last paragraph
   of this section shows". Category **A**.

2. **Algorithm 10.1 line 2 (`alg:ch10-lowlevel`, file line 309) together with
   Section 10.6.3, line 770-774: the horizon argument is cited from a proposition
   whose $H$ is defined differently, so the completeness step is not established for
   edge constraints.**
   Algorithm 10.1 sets "$H \gets$ largest $t$ in a constraint of $\mathcal{C}_i$"
   (and `focal_space_time_astar` does the same: `last_t = max(c.t for c in
   constraints)`). `thm:ch04-horizon` in `chapters/ch04-astar.tex` (lines 1010-1016)
   defines $H$ as "the largest $t$ of a vertex constraint, **the largest $t+1$ of an
   edge constraint**, and the time from which each parked agent occupies its cell".
   When the latest constraint in $\mathcal{C}_i$ is an edge constraint
   $\langle i,u,v,t\rangle$, the chapter's $H$ is one smaller than ch04's, so the
   sentence "By \cref{thm:ch04-horizon}, if any path respecting $\mathcal{C}_i$ exists
   at all then one exists that arrives no later than $H + 1 + D$" does not follow from
   the cited proposition. Facts (i) and (ii) derived from it carry
   `thm:ch10-lowlevel-lb`, `thm:ch10-consistent` and hence `thm:ch10-ecbs`, so the
   gap is load-bearing. (The chapter's tighter $H$ *is* in fact sufficient in this
   setting, because no low-level cell is blocked by a parked agent; the argument is
   just not given.)
   *Fix (preferred, changes no number and no code):* after the `thm:ch04-horizon`
   citation on line 770 insert one sentence, e.g. "The $H$ of \cref{ch:ch04} also
   counts the arrival times of parked agents and uses $t+1$ for an edge constraint;
   here no cell is blocked by another agent, and an edge constraint
   $\langle i,u,v,t\rangle$ only restricts a move that departs at time $t$, so from
   time $H+1$ on the agent moves freely and the proof of \cref{thm:ch04-horizon}
   gives arrival by $H+1+D$ with the $H$ of \cref{alg:ch10-lowlevel}."
   *Alternative:* redefine $H$ in Algorithm 10.1 line 2 and in
   `focal_space_time_astar` as "$t$ for a vertex constraint, $t+1$ for an edge
   constraint"; this only enlarges $T_{\max}$, but then re-run the code and re-check
   `tab:ch10-example-compare` and the benchmark, because expansion counts may move.
   Category **A**.

3. **Whole chapter: sum-of-costs notation competes with `ch07`/`ch09`.**
   Chapter 10 writes `\cost(\Pi)` for the sum of costs (line 165 and 3 more places)
   and `\cost(N)` for a CT node's cost (23 places). Chapter 7 and Chapter 9 use the
   macro `\sumcost(\Pi)` (the one listed in `frontmatter/notation.tex`, 6 uses in
   ch09) and write a node's cost as `N.\cost` (21 uses in ch09, and the notation
   table's MAPF block explicitly lists "$N.\mathcal{C}$, $N.\pi$, $N.\cost$").
   Chapter 10 uses zero `\sumcost`. This is exactly the "competing notation" that
   STYLE_GUIDE section 3 forbids, and it is jarring one chapter after CBS.
   *Fix:* replace `\cost(\Pi)` by `\sumcost(\Pi)` and `\cost(N)` by `N.\cost`
   throughout the chapter (including the two tables, the two algorithms, the summary
   box, the pitfall boxes and `appendices/glossary/ch10-terms.tex`), keeping
   `\cost(\pi_i)` for a single path. Category **F**.

4. **`frontmatter/notation.tex`, MAPF block: the chapter's central new symbol is not
   in the notation table.**
   `\Focal`, `$\fcost_{\min}$`, `$w$` and `$h_c$` are listed (lines 81, 82, 107), but
   $\mathrm{LB}$, $\mathrm{LB}_i(N)$ and $\mathrm{LB}(N)$ - used about forty times and
   the object the whole correctness argument turns on - are not.
   *Fix:* add one row to the MAPF block of `frontmatter/notation.tex`, e.g.
   `$\mathrm{lb}_i$, $\mathrm{LB}(N)$, $\mathrm{LB}$ & per-agent lower bound, their
   sum in a CT node, and its minimum over \Open & \cref{ch:ch10}\\`.
   Category **F**.

5. **Section 10.7.1 (`sec:ch10-choosing-w`), line 899-901: a number attributed to a
   figure that does not show it.**
   "in \cref{fig:ch10-benchmark} the plans of \ecbs with $w = 2$ are on average
   $1$--$12.5\,\%$ more expensive than optimal and never more than $28\,\%$". The
   averages are in the figure (`e20_ratio`, 1.0091 to 1.1246, so the range is right),
   but the worst case comes from `e20_ratio_max` in `ch10-benchmark.dat` (1.2766 at
   $k = 10$), which is plotted nowhere and tabulated nowhere.
   *Fix:* either change the attribution to "in the benchmark of
   \cref{sec:ch10-benchmark} ... and, over all instances of the run, never more than
   $28\,\%$", or add a `cost/C^*` worst-case column to `tab:ch10-benchmark`.
   Category **F**.

## Suggestions

* Section 10.5, "The two rulers": the invariant $\cost(\pi_a) \le w\,\mathrm{lb}_a$
  for *every* agent of *every* node is asserted in a walkthrough paragraph and then
  used inside the proof of `thm:ch10-terminates` ("because the node attaining
  $\mathrm{LB}$ lies in the band (\cref{sec:ch10-highlevel})"). One extra clause
  would make it airtight: the pair (path, bound) is inherited unchanged by the
  agents that are not replanned, and for the replanned agent
  $\cost(\pi) \le w\,\fcost_{\min} \le w\,\max(\mathrm{lb}^{\text{parent}},
  \fcost_{\min})$, so the max of line `alg:ch10-ecbs:lb` preserves it. Consider
  promoting it to a short lemma in Section 10.6, since two proofs depend on it.
* Section 10.9 (EECBS), "Explicit estimation": the parenthetical honestly flags that
  Li et al. test $\hat{\fcost}(N) \le w\,\mathrm{LB}$ while the text tests
  $\cost(N)$. Worth adding half a sentence that the substitution changes *which
  nodes are expanded* (not only what may be returned), so a reader who implements
  from this paragraph does not think they have implemented EECBS.
* Section 10.1: "its plans are on average $7\,\%$ more expensive than the optimum"
  at $k = 16$ is an average over the two instances that CBS solved. The caption of
  `tab:ch10-benchmark` says so, the motivation does not. Add "(over the two
  instances CBS could solve)" or use the $k = 12$ figure, which rests on nine.
* Section 10.7.1 "with $w = 1.1$ the plans are within $2$--$3\,\%$ of optimal" -
  `e11_ratio` runs from 1.0148 to 1.0282, so "within $3\,\%$" is the accurate phrasing.
* Length (23 pages against the spec's 13-15). Nothing here is padding in the sense
  that it could be cut without losing content, but three places are mildly
  redundant and would give back about 1.5 pages if the chapter has to shrink:
  (a) Section 10.7.1 restates benchmark numbers that Section 10.7.3 gives again
  15 lines later - keep the three rules of thumb and the $\cost/\mathrm{LB}$
  diagnostic, drop the re-quoted percentages; (b) the last five sentences of the
  "Other values of $w$" paragraph in Section 10.5 repeat
  `tab:ch10-example-compare` row by row; (c) the first two bullets of Section 10.8.4
  "Practical details" overlap Section 10.8.1. I do **not** require these cuts: the
  chapter is inside the 24-page limit and completeness outranks length.
* `exr:ch10-node-bound` is referenced twice from the body (Section 10.6.3 and the
  third pitfall) and is the sharpest exercise in the chapter, but it has no entry in
  `appendices/solutions/ch10-solutions.tex`. Four of eight is in line with ch08/ch09,
  yet this one would repay a solution (the answer is $N_7$: cost 15,
  $\mathrm{LB}(N_7) = 15$, $15 \le 1.2 \cdot 15$, ratio $15/12 = 1.25 > 1.2$).
* `fig:ch10-benchmark`, left panel: the caption says runs that time out count as
  10 s, which makes the CBS and ECBS(1.1) curves lower bounds. Consider adding a
  second y-axis or a small success-rate annotation on the plot itself, so the reader
  who only looks at the figure does not read the flattening of the CBS curve at
  $k = 16$ as CBS getting relatively better.

## What must be kept

The chapter is, technically, the strongest kind of textbook writing: it earns every
claim. The separation of the two duties of the two heuristics ("the ruler must be
honest, the choice inside the band is free") is the clearest statement of focal
search I have read at this level, and the decision to prove `thm:ch10-invariant` as a
choice-rule-free lemma - so that the same invariant serves A*, focal search and the
low-level bound - is exactly right pedagogically and mathematically. The
lower-bound bookkeeping is treated as the heart of the algorithm rather than an
implementation detail: `def:ch10-lb`, line `alg:ch10-ecbs:lb`, the "two rulers"
paragraph, `thm:ch10-lowlevel-lb`, the third pitfall box and
`exr:ch10-node-bound` form a single coherent thread that is the one thing most
treatments of ECBS get wrong or skip. Keep all of it, including the explicit remark
that Barer et al. use the returned $\fcost_{\min}$ alone and that the `max` is a safe
tightening.

Keep the worked example exactly as it is. Running CBS and ECBS on *the same* 4x4
instance, showing that CBS finds the returned-later solution $N_1$ in step 1 and
still has to expand six more nodes, and then walking $w$ through
1.05 / 1.1 / 1.2 / 1.5 so that the reader sees the tree collapse from 7 expansions to
1 and the root itself change - with every one of those numbers produced by
`ch10_ecbs.py` and printed by its self-test - is the best argument for bounded
suboptimality the book can make. The honest admission that ECBS returns the cost-13
plan although a cost-12 plan lies inside the band, and the explanation via the
duplicate rule at line `alg:ch10-lowlevel:dup`, is the kind of detail that stops a
student from believing that the focal heuristic is a guarantee.

Keep the benchmark and the `.dat`-driven figure: it is fully reproducible, its
numbers match the table and the prose to the digit, and it supports the Week-5
milestone directly. Keep the three pitfall boxes, which name the three real ECBS
bugs. Keep the drone box's distinction between the bound and safety ("A nominal path
that is 10 % longer than optimal costs flight time and battery, but it is neither
more nor less safe") and the observation that mission knowledge belongs in
$\hcost_{\Focal}$ where it cannot damage the guarantee - that is the sentence that
connects this chapter to Chapters 20 and 24. Keep the two heaps / lazy purge /
band-widening implementation section and both listings; they are verbatim from the
running file and answer the question every implementer asks.
