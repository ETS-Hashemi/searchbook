# Review of Chapter 16 (Rapidly-Exploring Random Trees) - round 2

Reviewed artefacts: `Overleaf/chapters/ch16-rrt.tex` (1354 lines), the eight figure files
`Overleaf/figures/ch16/{voronoi,primitives,tree-snapshots,jagged,connect,iterations,shortcut,scene3d}.tex`,
`Overleaf/code/ch16_rrt.py` (646 lines) and `Overleaf/code/figures/gen_ch16_tree.py`,
`Overleaf/figures/data/ch16-iterations.dat`, `Overleaf/appendices/solutions/ch16-solutions.tex`,
`Overleaf/appendices/glossary/ch16-terms.tex`, `Overleaf/bib/ch16-extra.bib`,
`Overleaf/frontmatter/notation.tex`, against `STYLE_GUIDE.md` section 9 (A-H),
`docs/specs/ch16.md`, `docs/core-idea.txt` (Week 8) and the round-1 review with the
reviser's response.

**Build.** `cd Overleaf && ./build.sh ch16-rrt` exits 0. No `!` errors, **zero overfull
boxes** (`grep -c Overfull build/only-ch16-rrt.log` = 0), and the only undefined references
are `ch:ch11`, `ch:ch13`, `ch:ch14`, all belonging to other chapters. Chapter body =
printed pages 159-179, i.e. **21 pages**.

**Code.** `python3 code/ch16_rrt.py` passes in 3.2 s; `python3 code/figures/gen_ch16_tree.py`
regenerates all eight figures and the `.dat` file. I re-ran both and checked every number in
the chapter against their output (worked example 402/245/50/23.847/3965; snapshots
{50:17, 200:103, 1000:673}; entry vertex (9.140, 8.603) at distance 0.4213; Voronoi
20.6/59.3/0.7/6.7 %; the four rows of Table 8.3 518/537/352/24.31+-2.00,
425/453/275/23.87+-1.84, 745/783/245/23.61+-1.86, 178/192/101/23.69+-1.98; jagged seed 14
28.35 at iteration 746; connect seed 1 164 with 68+29 and 25.11; shortcut
23.85 -> 19.91 (23) -> 18.39 (7); 3D 321/158/24.48/20.40/15.59; kinodynamic 680/512/41
steps/0.54; nearest-neighbour 0.039/0.294/2.838 ms). I also re-derived the ratios
(23.847/16.720 = 1.426, 23.847/17.198 = 1.387, 18.39/17.198 = 1.069, 425/178 = 2.39,
275/101 = 2.72, 20.55/17.198 = 1.195), re-checked both theorem proofs line by line,
re-checked the tight margin sqrt(r^2 + delta^2/4) of Exercise 16.3(b), and verified all six
rows of the grid-size table (3^d - 1 = 8/26/728; 4e6 x 20^3 = 3.2e10; 5e8 x 100^3 = 5e14)
and the two exercise-1 arithmetic answers (1.536e8 cells, 5.5e12 states, 0.56 MB).

**Round-1 items.** All seven required changes of round 1 were addressed. Items 1, 2, 3, 5
and 6 are fully and correctly resolved (the 34 rejections, the forty *directions* through a
point inside the thin wall plus the forty crossings now in `_self_test`, both reference
lengths computed and printed by the self-test with the two baselines named in the text, the
three pseudocode defects in `alg:ch16-kino`, and the finite-length hypothesis with the
compactness note in the proof). Item 4 is resolved except for one leftover number (required
change 1 below). Item 7 is only partly resolved (required change 5 below).

## Verdict

**Minor revision.** The mathematics is correct, completeness against the specification and
the Week-8 plan is total, the build is clean, and essentially every number is now produced
by committed code. Five local fixes remain: two numbers that the code does not reproduce,
one exercise whose general claim is false as stated, one summary bullet that contradicts the
correction made in round 1, and the residual four-page forward reference to Table 8.3.

## Required changes

1. **Location:** `chapters/ch16-rrt.tex` line 1043, section 16.8.3
   (`sec:ch16-parameters`): "The self-test runs in a few seconds (it prints its own runtime,
   four to five here)".
   **Problem:** the committed self-test prints `self-test passed in 3.2 s` on this machine,
   not four to five seconds. This is the one number in the chapter that the code does not
   reproduce; round 1 required exactly this sentence to be made truthful and the replacement
   is still machine-specific in a way the run contradicts.
   **Fix:** drop the parenthetical range or widen it to cover the observed value, e.g.
   "The self-test runs in a few seconds -- it prints its own runtime, three to five seconds
   on the machines used for this book -- and re-checks in one place ...".
   **Category:** A.

2. **Location:** `appendices/solutions/ch16-solutions.tex`, solution to
   `exr:ch16-trace`, lines 40 and 44: "$x_{\mathrm{new}}=x_6+0.5\,(0.9504,0.3112)=(3.335,3.076)$"
   and "$x_{\mathrm{new}}=(3.145,3.331)$ ... Both lines match the trace printed by
   `ch16_rrt.py`."
   **Problem:** the code does not print those values. Instrumenting
   `rrt(worked_example_world(), (1,1), (9,9), eta=0.5, p_goal=0.05, r_goal=0.5, seed=1,
   trace=...)` gives iteration 11 -> `(3.3321, 3.0727)` and iteration 12 ->
   `(3.1427, 3.3272)`. The solution's numbers are right *given the two-decimal vertex
   coordinates of Table 8.2*, but the sentence claims agreement with the program at three
   decimals, and a reader who runs the code will see a mismatch in the third decimal.
   **Fix:** keep the derivation and replace the last claim by, e.g., "Computed from the
   two-decimal coordinates of \cref{tab:ch16-trace}; the trace printed by
   \code{ch16\_rrt.py}, which carries the full precision of $x_6$, gives $(3.332,3.073)$
   and $(3.143,3.327)$ -- the same conclusion, the difference being the rounding of the
   tabulated vertex."
   **Category:** A.

3. **Location:** `chapters/ch16-rrt.tex` lines 1308-1313, `exr:ch16-voronoi`: "Then show in
   general that for a tree that is a single straight chain of $k+1$ vertices spaced $\eta$
   apart in a large map, the tip is chosen with probability close to $1/2$ ...".
   **Problem:** the claim is false as stated, and it contradicts the chapter. For a chain
   whose root sits near a corner -- exactly the situation of section 16.5, where the text
   correctly says "its tip owns almost the whole map" -- the tip's Voronoi region is the
   half-plane beyond the tip, which is nearly the whole map, so its probability is close to
   1, not 1/2. The stated result needs the chain to be *centred* in the map: this hypothesis
   is silently added in the solution ("in the middle of a square of side $L\gg k\eta$"),
   which the exercise text does not give the student. As written the exercise cannot be
   solved.
   **Fix:** restate as "... for a tree that is a single straight chain of $k+1$ vertices
   spaced $\eta$ apart, centred in a large square map of side $L$ with $L\gg k\eta$, each of
   the two tips is chosen with probability close to $1/2$ and every interior vertex with
   probability at most $\eta/L$", and add one clause pointing out that with the root at a
   corner, as in \cref{ex:ch16-map}, the single tip takes almost all of the probability
   instead. Adjust the first sentence of the solution to match.
   **Category:** E.

4. **Location:** `chapters/ch16-rrt.tex` lines 1208-1211, third bullet of the `summary` box:
   "a vertex is extended with probability equal to the relative volume of its Voronoi
   region".
   **Problem:** this is the imprecise formulation that round 1 asked to be corrected. It was
   corrected in section 16.2 and in the `keyidea` box (both now say *selected*, with the
   extension conditional on the collision check), but not in the summary, which is the
   sentence a reader is most likely to memorise. It is also flatly contradicted by the same
   chapter's worked example, where 34 of the first 50 selections are rejected.
   **Fix:** "a vertex is *selected* with probability equal to the relative volume of its
   Voronoi region, and extended when the step is collision-free, so the tree is pulled into
   the largest unexplored regions." Align `appendices/glossary/ch16-terms.tex` line 5 the
   same way ("selected for extension ... and extended when the step is free").
   **Category:** C.

5. **Location:** `chapters/ch16-rrt.tex` line 538 (section 16.6.2) and the table block at
   lines 696-714 (`tab:ch16-connect`); float placement in section 16.7 generally.
   **Problem:** round-1 item 7 is only partly resolved. In the current build
   `tab:ch16-connect` is first cited on printed page 166 ("with the mean and spread of
   \cref{tab:ch16-connect}") and typeset on page 170 -- a four-page forward jump across a
   section boundary, worse than any of the three floats round 1 complained about.
   (`alg:ch16-connect` p.167 -> 169, `alg:ch16-kino` p.168 -> 170, `alg:ch16-shortcut`
   p.169 -> 171, `fig:ch16-iterations` p.167 -> 169; only `fig:ch16-scene3d` p.171 -> 172
   now satisfies the "same page or the page after" rule.)
   **Fix:** (a) remove the long-range forward reference: on line 538 replace "with the mean
   and spread of \cref{tab:ch16-connect}" by the two numbers themselves, "with mean $23.87$
   and standard deviation $1.84$" -- this is more useful to the reader at that point and
   leaves \cref{tab:ch16-connect} with its first citation inside section 16.7.1, where it
   belongs; (b) change the table's placement from `[tb]` to `[!t]` so it can take the top of
   page 168 or 169 instead of queueing behind the two algorithms. The remaining two-page lags
   of `alg:ch16-connect`, `alg:ch16-kino` and `alg:ch16-shortcut` are accepted as physical
   float congestion (eight floats over four pages of section 16.7) and need no further work,
   provided (a) and (b) are done and the rebuilt PDF is checked.
   **Category:** G.

## Suggestions

* **Length (21 pages against a 20-page cap, spec target 13-15).** No cuts are *required*:
  the twenty-first page is the price of round 1's own required additions (both baselines,
  the finite-length note, the named Karaman-Frazzoli assumptions, the two `\KwIn` entries,
  the smoothing sentences), and nothing on those pages is padding of the kind that must go.
  If the editor still wants the page back, the four genuinely duplicated passages are:
  (i) section 16.6.2 lines 533-540, which quotes four separate ratios (43 %, 65 %, 70 %, the
  20.55-28.35 range) plus "not one run comes within 15 %" for a single point -- two of them
  suffice; (ii) the pitfall *Testing the vertices but not the segments* (lines 1073-1085),
  which re-tells the thickness-0.02, delta-0.05, forty-tests story already told in section
  16.3 lines 265-272 -- one of the two can just point at the other; (iii) section 16.8.3
  lines 1032-1039 ("Two of them are most often mishandled. The *seed*: ... The *budget*: ..."),
  which restates the last two rows of \cref{tab:ch16-parameters} in prose; (iv) the first two
  sentences of the "Voronoi bias, quantified" paragraph (lines 336-341), which repeat section
  16.2 in words before \cref{eq:ch16-voronoi} says it in symbols. Together about 18 lines.
* `eq:ch16-voronoi` and `def:ch16-primitives` carry labels that are never referenced, as do
  the line labels `alg:ch16-rrt:fail` and `alg:ch16-shortcut:draw`. Either `\cref` them or
  drop the labels.
* Section 16.6.1, first paragraph: "A planner is probabilistically complete if, whenever a
  solution exists, ...". The glossary and \cref{thm:ch16-complete} both (correctly) require a
  solution with positive clearance. Add "with positive clearance" here too, or one sentence
  saying that the guarantee is for robustly feasible queries.
* Section 16.6.1, bullet *The role of $\eta$*: "A larger $\eta$ does not hurt" is true of the
  bound but reads as a general claim, and \cref{tab:ch16-parameters} says the opposite for
  cluttered maps. Write "does not hurt this bound".
* Section 16.7.1: the committed `ch16-iterations.dat` shows RRT-Connect solving all 100 seeds
  by iteration 375, so "solves every instance within $500$ iterations" can be sharpened to
  375 at no cost.
* Notation: `frontmatter/notation.tex` line 138 now has a ch16 row, but it lists only
  $T=(V,E)$ and $\eta$, while line 136 assigns $\rho,\rho_0$ to clearance and influence
  distance in \cref{ch:ch15} and \cref{eq:ch16-metric} reuses $\rho$ for the weighted state
  metric. Ask the editor to extend the ch16 row with $\delta$, $p_{\mathrm{goal}}$,
  $r_{\mathrm{goal}}$ and $\rho$ (state-space metric), or rename the metric $d_{w}$ inside
  this chapter, which is a two-line change the chapter can make on its own.
* The `dronebox` uses \cbs, \ecbs and \dstarlite without expanding them; the guide asks each
  acronym to be expanded at first use *in every chapter*. One parenthetical
  ("conflict-based search") would fix it.
* Solutions now cover 6 of 8 exercises. `exr:ch16-goalbias` would benefit from a two-sentence
  expected-shape answer (U-shaped curve, minimum near 0.05-0.1, and the fact that moving the
  goal to $(9,1)$ shifts the optimum upwards because only one wall blocks the straight line).

## What must be kept

The proof of \cref{thm:ch16-complete} remains the best thing in the chapter and is now
airtight: the ball chain with $\nu=\min(\eta/3,\delta_c/4,r_{\mathrm{goal}})$, the
three-term triangle inequality that forces \textsc{Steer} to return the sample exactly, the
convexity argument that puts the whole segment inside the clearance tube, the domination by a
sum of geometrics, Markov, and now the compactness note that makes the finite-length
hypothesis free. Keep it, and keep the three bullets after it ($\eta$, the goal bias, the
$(1/w)^{d}$ narrow-passage law) - they are exactly what a lone reader needs. Keep
\cref{thm:ch16-resolution} and the $r+\delta/2$ inflation, which is carried consistently into
`segment_free`, into \cref{fig:ch16-primitives}, into the pitfalls and into Exercise 16.3(b),
whose sharper margin $\sqrt{r^{2}+\delta^{2}/4}$ I re-verified as the tight one. Keep the
reproducibility that this revision has now completed: every figure and every quoted number is
regenerated by committed code, including the two reference lengths (16.720 by the exact
corners $(3,6),(5,6),(6,4),(8,4)$ and 17.198 with clearance 0.075), the forty-direction and
forty-crossing thin-wall test that now really tests what the text says it tests, the
nearest-neighbour timings, and the 100-seed table. Keep the honest result that
$p_{\mathrm{goal}}=0.5$ is worse than no bias at all, with its matching pitfall box; keep
\cref{tab:ch16-gridsizes} and \cref{tab:ch16-comparison}, which between them answer the
Week-8 milestone; keep the "only the bounds change" 3D section, the kinodynamic section with
its corrected pseudocode, and the `dronebox` on splicing a local \rrt into a global grid plan.
