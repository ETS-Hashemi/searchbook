# Review of Chapter 10 (Bounded-Suboptimal Search: ECBS) - round 2

Reviewer: independent domain expert (motion planning, MAPF, bounded-suboptimal search).
Material reviewed: `Overleaf/chapters/ch10-ecbs.tex` (1482 lines),
`Overleaf/figures/ch10/{idea,focal-lowlevel,example-instance,example-trees,benchmark}.tex`,
`Overleaf/code/ch10_ecbs.py`, `Overleaf/figures/data/ch10-benchmark.dat`,
`Overleaf/appendices/solutions/ch10-solutions.tex`, `Overleaf/appendices/glossary/ch10-terms.tex`,
`Overleaf/references.bib`, `Overleaf/bib/ch10-extra.bib`, `Overleaf/frontmatter/notation.tex`,
`Overleaf/chapters/ch04-astar.tex` and `ch09-cbs.tex` (consistency), against
`STYLE_GUIDE.md` section 9 (A-H), `docs/specs/ch10.md` and `docs/core-idea.txt` (Week 5),
plus `reviews/ch10-round1.md` with the reviser's response.

Checks actually run in this round:

* `cd Overleaf && ./build.sh ch10-ecbs` - **exit status 0**, 43-page PDF, chapter proper on
  pp. 14-35 = **22 chapter pages**, inside the 24-page budget. No `!` errors; the only two
  overfull boxes are **3.54 pt and 1.48 pt** (paragraph "The root", lines 498-517), far below the
  15 pt threshold; the only undefined references are `ch:chNN` of *other* chapters, as expected in
  a single-chapter build. No `ch10` label, `\cref` or citation is undefined.
* `python3 code/ch10_ecbs.py` - self-test passes in 0.4 s, and the demo now prints the CBS trace
  **and** the ECBS traces for `w = 1.05, 1.1, 1.2`, so `tab:ch10-ecbs-trace` is reproducible by
  running the file (round-1 item 3).
* Independent re-run of `cbs()` and `ecbs()` on `worked_example()`: **Table 10.4 reproduces
  exactly** - CBS 12/7/13/LB 12/136; ECBS 1.05 -> 12/7/13/12/12.6/136; 1.1 -> 13/4/7/12/13.2/61;
  1.2 -> 13/2/3/11/13.2/37; 1.5 -> 13/1/1/11/16.5/20. The printed `w = 1.1` trace matches
  `tab:ch10-ecbs-trace` row for row, including the F/O flags (step 2 children `N_3` F and `N_4` F,
  step 3 children `N_5` O and `N_6` F), which is what round-1 item 1 turned on.
* Every number in `sec:ch10-motivation`, `sec:ch10-benchmark`, `sec:ch10-choosing-w`,
  `tab:ch10-benchmark` and the complexity subsection re-read off `figures/data/ch10-benchmark.dat`:
  23 ms and 7 % and 2/10 at k=16; 6/10, 1153.2 nodes, 1.9853 s, 5.7 nodes, 11.4 ms, 6.23 %,
  10.53 %, 15.87 %, 7.1 ms, 12.46 %, 7/10 and 4/10 at k=14/16; the 8/12/16-agent table rows;
  0.91 %-12.46 % and max 27.66 % for w=2; 8.2 > 6.9 CT nodes for w=1.1 at k=8. **All correct**,
  including the two numbers corrected in round 1 (items 4a, 4b).
* Solution-appendix claims re-verified by running the code:
  `3 * (4/3) == 4.0` in Python (as `exr:ch10-lowlevel-threshold`(b)'s solution states), and part (c)
  reproduces exactly - with B waiting twice at (1,1), `w = 1.5` returns the cost-3 path, 1 conflict,
  bound 3, 4 expansions; `w = 2` returns `(1,0),(1,0),(1,0),(1,1),(1,2),(1,3)`, cost 5, 0 conflicts,
  bound 3.
* All 13 citation keys resolve (12 in `references.bib`, `thayer2011bounded` in `bib/ch10-extra.bib`)
  and I re-checked authors/venue/year/pages of each against the literature: Barer et al. SoCS 2014
  pp. 19-27; Pearl & Kim PAMI-4(4):392-399 1982; Li/Ruml/Koenig AAAI 2021 pp. 12353-12362;
  Thayer & Ruml IJCAI 2011; Felner et al. ICAPS 2018 pp. 83-87; Li et al. AAAI 2019 pp. 6087-6095;
  Boyarski et al. IJCAI 2015 pp. 740-746; Pohl AIJ 1(3-4):193-204 1970; Pearl 1984. **No fabricated
  or wrong entry.**
* Round-1 items **1-7 are all resolved, and resolved correctly**; I re-derived the FOCAL membership
  at each step of the `w = 1.1` trace (item 1), checked the new `f_min` monotonicity chain against
  consistency (item 2), diffed the `T_max`/`H`/`D` wording against `focal_space_time_astar` and
  against `thm:ch04-horizon` (item 5), and read the new legend and closing annotation of
  `example-trees.tex` panel (b) against the printed trace (item 6). None of them is re-raised.
* Spec `docs/specs/ch10.md`: all 17 "must cover" items present. Week-5 items of the training plan:
  all present. 5 figures, 5 tables, 8 exercises (difficulties 1,1,2,2,2,3,3,3), 3 pitfall boxes,
  22 index entries, `keyidea`/`objectives`/`summary`/`dronebox` all present, both listings verbatim
  from `ch10_ecbs.py` and under 45 lines.

## Verdict

**Minor revision.**

The chapter is in very good shape. The algorithm matches Barer et al. (2014) line for line, the
lower-bound bookkeeping is proved rather than asserted, every number in the text is reproduced by
the committed code, and the seven round-1 defects were fixed properly and without collateral damage.
Two items remain, both strictly local: one sentence in `sec:ch10-properties` that states an
assumption about the low-level horizon which is *false as written* (the proofs themselves are
correct and need only the weaker, true statement), and the time labels of agent B in
`figures/ch10/focal-lowlevel.tex`, which sit on cell boundaries instead of in cells while agent A's
sit in cells, with no caption sentence saying what the numbers mean.

## Required changes

1. **Location:** `sec:ch10-properties`, subsection "\ecbs is $w$-suboptimal", the sentence
   immediately before `thm:ch10-consistent`: "*We assume that the low-level horizon $T_{\max}$ is
   large enough to contain $\pi_i^*$ under the constraints of every consistent node; the horizon
   $T_{\max} = \lfloor w\,(H+1+D)\rfloor \ge H+1+D$ of \cref{alg:ch10-lowlevel} guarantees this, by
   the argument of \cref{ch:ch04}.*"
   **Problem:** the assumption is stated about the wrong object and is false as written.
   $\pi_i^*$ is agent $a_i$'s path in a fixed optimal *joint* solution; its length is bounded by
   $C^*$, not by $H + 1 + D$, because $\pi_i^*$ may contain long waits that let other agents pass.
   A concrete case: at the root $H = -1$, so $T_{\max} = \lfloor wD \rfloor$, while an optimal joint
   solution can easily give one agent a path of cost $> wD$. And `\cref{ch:ch04}`
   (`thm:ch04-horizon`) does not prove what the sentence claims it proves: it proves that *some*
   constraint-respecting path arrives by $H + 1 + D$, not that $\pi_i^*$ does. The two proofs that
   use this sentence do not actually need it - `thm:ch10-ecbs` only ever uses
   $C_i^*(\mathcal{C}) \le \cost(\pi_i^*)$, and `thm:ch10-lowlevel-lb` only needs the *constrained
   optimum* to be attained inside the horizon - so the fix is a restatement, not a repair.
   **Fix:** replace the sentence with, e.g.: "Two horizon facts are used below. By
   \cref{thm:ch04-horizon}, if any path respecting $\mathcal{C}_i$ exists then one exists that
   arrives no later than $H + 1 + D \le \lfloor w\,(H+1+D)\rfloor = T_{\max}$. Hence (i) the
   low-level call of a consistent node never fails, and (ii) the constrained optimum
   $C_i^*(\mathcal{C}_i)$ is attained within the horizon, so \cref{thm:ch10-lowlevel-lb} applies.
   Note that $\pi_i^*$ itself may be longer than $T_{\max}$, because it may wait for other agents;
   we never need the low level to find $\pi_i^*$, only to bound $C_i^*(\mathcal{C}) \le
   \cost(\pi_i^*)$." Then, in the proof of `thm:ch10-consistent`, replace "*$\pi_a^*$ respects
   $N'.\mathcal{C}_a$ and lies within the horizon, so a path exists*" by "*$\pi_a^*$ respects
   $N'.\mathcal{C}_a$, so a path exists, and by (i) one exists within the horizon*".
   **Category:** A.

2. **Location:** `figures/ch10/focal-lowlevel.tex`, the two `tB` labels
   (`\node[tB] at (1.78,2.0) {1};` and `\node[tB] at (1.78,1.0) {2};`) and the caption of
   `fig:ch10-focal-lowlevel` in `sec:ch10-lowlevel`.
   **Problem:** with the figure's own convention (cell $(r,c)$ has centre $(c+0.5,\,2.5-r)$), the
   row centres are $y = 2.5, 1.5, 0.5$, so the labels at $y = 2.0$ and $y = 1.0$ sit exactly on the
   grid lines *between* B's cells, i.e. offset along B's direction of travel, whereas agent A's
   labels are offset perpendicular to A's travel and stay horizontally aligned with the cells. The
   companion figure `example-instance.tex` uses the perpendicular-offset convention throughout.
   Since the whole point of `ex:ch10-lowlevel` is that **B is at $(1,1)$ at $t=1$**, a "1" drawn on
   the boundary between $(0,1)$ and $(1,1)$ makes the reader guess; and unlike
   `fig:ch10-example-instance`, this caption never says what the small numbers mean.
   **Fix:** move the two labels onto the cells - `\node[tB] at (1.78,1.5) {1};` and
   `\node[tB] at (1.78,0.5) {2};` (B is at $(1,1)$ at $t = 1$ and at $(2,1)$ at $t = 2$) - and add
   the convention to the caption, e.g. after the first sentence: "Small numbers give the time at
   which a cell is reached; B is at $(1,1)$ at $t = 1$ and parks at $(2,1)$ from $t = 2$."
   **Category:** D.

## Suggestions

* `sec:ch10-highlevel`, walkthrough, after the discussion of line~\ref{alg:ch10-ecbs:lb}:
  "*Barer et al.\ use the returned value alone; ... Either way, $\mathrm{LB}(N')$ can be larger than
  $\cost$ of the parent and, unlike the cost, it never decreases along a branch.*" The
  monotonicity along a branch follows immediately from the `max`, but *not* from Barer's variant:
  the $\fcost_{\min}$ a child's low level returns is only a lower bound on a *larger* constrained
  optimum and can be smaller than the parent's returned value, since the child's search may pop a
  goal from \Focal earlier. Nothing in the chapter's proofs depends on it, so this is only a
  wording matter: write "With the maximum of line~\ref{alg:ch10-ecbs:lb}, $\mathrm{LB}(N')$ never
  decreases along a branch, unlike the cost."
* `sec:ch10-lowlevel`, walkthrough: "*The duplicate test that ends in line~\ref{...:dup}*" and, in
  `sec:ch10-implementation`, "*The test before line~\ref{...:dup}*" both point at the same line from
  two different directions. Say "the duplicate test at line~\ref{alg:ch10-lowlevel:dup}" in both
  places.
* Chapter preamble: `\SetKwFunction{EcbsFocalSearch}{FocalSearch}` is declared and never used (only
  `EcbsLowLevel` and `EcbsHighLevel` appear in the two algorithms). Delete the declaration
  (category G, cosmetic).
* `exr:ch10-focal-by-hand`(d) says "*the other nodes being unchanged*"; the intended reading -
  confirmed by the solution, which puts $(16,0)$ in \Focal - includes the two successors generated
  in part (b). Write "the nodes of (a) and (b) otherwise unchanged" so the reader assembles the same
  \Open.
* `tab:ch10-variants`, GCBS row: the "High level: \Open by" cell is "--". A word ("single queue")
  reads better than a dash in a column whose other entries are quantities.
* `frontmatter/notation.tex` still has no rows for \Focal, $\hcost_{\Focal}$, $\mathrm{LB}$,
  $\mathrm{LB}_i(N)$ and $w$, all of which this chapter promotes to book-level notation. This is an
  editor edit outside the chapter's file set (the reviser correctly reported it rather than making
  it in round 1); flagging it again so it is not lost.
* Length: 22 chapter pages against a spec target of 13-15 but inside the 24-page budget. As in round
  1, I find **no padding worth cutting**: every section corresponds to a "must cover" item and the
  prose is dense. Completeness and accuracy outrank the page target here; I explicitly do **not**
  request cuts (category G).
* `appendices/solutions/ch10-solutions.tex` covers 4 of 8 exercises, in line with the neighbouring
  chapters (ch09: 3/10, ch11: 5/8). No change required. If ever extended, `exr:ch10-node-bound`
  deserves one; I re-verified the intended answer ($N_7$: $\cost = 15$, $\mathrm{LB}(N_7) = 15$,
  $h_c = 0$, so the node-local test $15 \le 1.2 \cdot 15$ admits it although $15/12 = 1.25 > 1.2$).

## What must be kept

Everything the round-1 review asked to keep is still there, untouched, and still the best part of
the chapter: the proof chain `thm:ch10-invariant` -> `thm:ch10-lowlevel-lb` -> `thm:ch10-consistent`
-> `thm:ch10-ecbs`, together with the paragraph after the theorem that maps each step of the chain
onto a specific piece of bookkeeping in the code - most treatments of ECBS state the theorem and
wave at the lower bounds; this one proves them. Keep the "two rulers" paragraph, whose
$\cost(N_{\min}) \le w\,\mathrm{LB}(N_{\min}) = w\,\mathrm{LB}$ argument shows \Focal is never
empty and is missing from the original paper. Keep the worked example in full: one instance, five
values of $w$, CBS and ECBS trees side by side, and the honest sentence that ECBS returns the
cost-13 plan although a cost-12 plan was inside the band - that observation teaches more about
bounded suboptimality than the theorem does. Keep the root paragraph's explanation of *why* the
$w = 1.2$ low level misses the conflict-free cost-6 path (the duplicate rule at
line~\ref{alg:ch10-lowlevel:dup}); I re-derived it and it is exactly right - every conflict-free
cost-6 path for $a_3$ must use state $(2,1)$ at $t = 3$, and the first arrival there comes through
the swapping move from $(2,0)$. Keep the low-level example with its $w = 4/3$ threshold and the
floating-point exercise and its solution (I confirmed `3 * (4/3) == 4.0` and both $w = 1.5$ and
$w = 2$ runs of part (c)). Keep all three pitfall boxes, especially the third one with its concrete
counter-node $N_7$. Keep the two-heaps subsection, including the sentence that reading
$\fcost_{\min}$ *before* popping from \Focal is what makes `thm:ch10-lowlevel-lb` hold - that single
line is the difference between a correct and a silently broken implementation. Keep the benchmark
section, its `.dat`-driven figure with the dashed proven-bound curves, and `tab:ch10-benchmark`:
together they are the Week-5 milestone made visible. And keep the code as it stands - fast, honest,
verbatim in the listings, and the source of every number in the chapter.

## Response to review (round 2)

All changes were made in the chapter's own file set
(`chapters/ch10-ecbs.tex`, `figures/ch10/focal-lowlevel.tex`); nothing else was touched.
Build: `./build.sh ch10-ecbs` exits **0**, no `!` errors, the only overfull boxes are the same
two of 3.54 pt and 1.48 pt in the "The root" paragraph, and the only undefined references are
`ch:chNN` of other chapters. `python3 code/ch10_ecbs.py` still prints
"self-test passed in 0.4 s (45 random instances checked against CBS)"; the code was not modified,
so `figures/data/ch10-benchmark.dat` is unchanged and every number in the text still matches it.

### Required changes

1. **`sec:ch10-properties`, the horizon assumption before `thm:ch10-consistent` (category A) - fixed
   as prescribed.** The reviewer is right: $\pi_i^*$ is a path of a fixed optimal *joint* solution
   and can be longer than $T_{\max} = \lfloor w\,(H+1+D)\rfloor$ (at the root $H = -1$, so
   $T_{\max} = \lfloor wD \rfloor$, while $\pi_i^*$ may wait for other agents), and
   `thm:ch04-horizon` only asserts that *some* constraint-respecting path arrives by $H+1+D$.
   The false sentence was replaced by the "two horizon facts" paragraph: `thm:ch04-horizon` gives
   $H + 1 + D \le \lfloor w\,(H+1+D)\rfloor = T_{\max}$, hence (i) the low-level call of a
   consistent node never fails and (ii) the constrained optimum $C_i^*(\mathcal{C}_i)$ is attained
   inside the horizon, so `thm:ch10-lowlevel-lb` applies; and the paragraph now says explicitly
   that $\pi_i^*$ itself may exceed $T_{\max}$ and that only
   $C_i^*(\mathcal{C}) \le \cost(\pi_i^*)$ is ever needed. In the proof of `thm:ch10-consistent`,
   "$\pi_a^*$ respects $N'.\mathcal{C}_a$ and lies within the horizon, so a path exists" is now
   "$\pi_a^*$ respects $N'.\mathcal{C}_a$, so a path exists, and by~(i) one exists within the
   horizon". I checked the statement of `thm:ch04-horizon` in `ch04-astar.tex` (line 1005) against
   the new wording; the cross-reference resolves in the build. No other proof text changed, so the
   chain `thm:ch10-invariant` -> `thm:ch10-lowlevel-lb` -> `thm:ch10-consistent` ->
   `thm:ch10-ecbs` and the bookkeeping paragraph after it are untouched.
2. **`figures/ch10/focal-lowlevel.tex` time labels and caption (category D) - fixed.** Both `tB`
   labels moved from the grid lines onto the cells: `(1.78,2.0)` -> `(1.86,1.5)` (B at $(1,1)$ at
   $t=1$) and `(1.78,1.0)` -> `(1.86,0.5)` (B parked at $(2,1)$ from $t=2$). I used $x = 1.86$
   rather than the suggested $1.78$: at $1.78$ the "2" is printed on the dashed goal circle of B,
   whose radius is 8 pt about $(1.5,0.5)$; $1.86$ clears the circle and the cross marker while
   staying inside column 1 and keeping the offset perpendicular to B's travel, as in
   `example-instance.tex`, and the `tB` style now carries `fill=white,inner sep=0.5pt` so the "2"
   is not crossed by the dashed goal circle of B (the same masking convention as the annotation
   nodes of `figures/ch09/tree.tex`). Verified on the rendered page at 400 dpi. The caption now states the convention
   after the first sentence: "Small numbers give the time at which a cell is reached; B is at
   $(1,1)$ at $t = 1$ and parks at $(2,1)$ from $t = 2$."

### Suggestions

* LB monotonicity: rewritten as suggested - "With the maximum of line~\ref{alg:ch10-ecbs:lb},
  $\mathrm{LB}(N')$ can be larger than $\cost$ of the parent and, unlike the cost, it never
  decreases along a branch." The claim is now attached to the `max`, not to Barer's variant.
* Duplicate test: both places now read "the duplicate test at
  line~\ref{alg:ch10-lowlevel:dup}" (`sec:ch10-lowlevel` walkthrough and `sec:ch10-implementation`).
* `\SetKwFunction{EcbsFocalSearch}{FocalSearch}` deleted from the chapter preamble (unused).
* `exr:ch10-focal-by-hand`(d): "the other nodes being unchanged" -> "the nodes of (a) and (b)
  otherwise unchanged", which is the reading the solution assumes.
* `tab:ch10-variants`, GCBS row: "--" -> "single queue" in the "High level: \Open by" column.
* `frontmatter/notation.tex`: **not done, out of the chapter's file set** (the finisher brief
  forbids editing front matter). Reported again for the editor: rows are still needed for \Focal,
  $\hcost_{\Focal}$, $\mathrm{LB}$, $\mathrm{LB}_i(N)$ and $w$.
* Length: no cuts, as the reviewer explicitly did not request them. The chapter is now 23 pages
  (PDF pp. 15-37 of the single-chapter build; it grew by the one added paragraph), still inside
  the 24-page budget.
* Solutions appendix left at 4 of 8 exercises, as the reviewer said no change is required.

### What was kept

Untouched: the four-step proof chain and the bookkeeping paragraph after `thm:ch10-ecbs`, the "two
rulers" paragraph, the whole worked example (one instance, five values of $w$, both trees, and the
sentence about the cost-13 plan returned while a cost-12 plan was in the band), the root
paragraph's duplicate-rule explanation, the low-level example with the $w = 4/3$ threshold and its
floating-point exercise and solution, all three pitfall boxes, the two-heaps subsection with the
sentence about reading $\fcost_{\min}$ before popping from \Focal, the benchmark section with its
`.dat`-driven figure and `tab:ch10-benchmark`, and `code/ch10_ecbs.py` exactly as it stands.
