# Review of Chapter 17 (RRT* and Informed RRT*) - round 1

Reviewed: `Overleaf/chapters/ch17-rrt-star.tex` (1403 lines), figures
`Overleaf/figures/ch17/{near,choose-parent,rewire,radius,snapshots,ball-covering,ellipses,ellipse-transform,convergence}.tex`,
code `Overleaf/code/ch17_rrt_star.py` and `Overleaf/code/figures/gen_ch17_convergence.py`,
`Overleaf/appendices/solutions/ch17-solutions.tex`, `Overleaf/appendices/glossary/ch17-terms.tex`,
`Overleaf/bib/ch17-extra.bib`, against `STYLE_GUIDE.md` section 9, `docs/specs/ch17.md` and
`docs/core-idea.txt` (Week 8).

Build: `./build.sh ch17-rrt-star` returns status 0, no `!` errors, no undefined citations, no
undefined ch17 labels (only `ch:ch13`, `ch:ch14`, `ch:ch20`, `ch:ch21` `??` from chapters not in
the partial build, which is allowed), **no overfull or underfull boxes at all**. Chapter length:
PDF pages 24-43 = **20 pages** (front matter is pages 1-23), at the top of the budget and above
the spec target of 13-15.

Code: `python3 code/ch17_rrt_star.py` passes its self-test in 6.7 s;
`python3 code/figures/gen_ch17_convergence.py` reproduces the `.dat` file and the two generated
TikZ figures. I re-ran both and checked every number quoted in the chapter against their output.
Almost all of them match exactly (12.048/12.05, the whole hand-example trace, 351/204/21.003,
19.726, 18.212, 17.711, 17.452, 17.324, 0.946, 0.788, 25.721, 17.33+-0.08, 23.51+-1.67,
18.291/17.234, 7997 checks, 23.6 mean |Near|, k_n=33 and 17.437 vs 17.452, 21.57/18.10,
16.71+-1.23/14.09+-0.12, 8486 vs 7399, median 252, 24.3/19.1/14.2/14.0, 45.5 %/10.2 %, 13.65,
12.2, 15.0). Two quoted claims do **not** survive the check (items 1 and 2 below).

## Verdict

**Minor revision.** The mathematics of the chapter is sound: the radius condition, the
neighbour-count computation, the five-step ball-covering proof (including the origin of the
constant `2(1+1/d)^{1/d}`), the informed-set geometry, the sampling transformation and the SVD
rotation are all correct, and the code reproduces the tables and figures. But there are three
statements that are false as written (a convergence claim the code contradicts, a geometric claim
about the informed set that the chapter's own exercise solution contradicts, and a
misattribution of the RRT* radius constant), plus a small number of local notation and
reproducibility defects. Every required change is a sentence-level or caption-level edit; none
requires re-running an experiment or restructuring a section.

## Required changes

1. **A - Technical accuracy (a number the code does not reproduce).**
   *Location:* `sec:ch17-example`, line 609: "\rrtstar reaches that quality at about $2\,500$
   iterations and keeps going".
   *Problem:* "that quality" is the string-pulled grid-A* cost 17.23. With the run of
   `ex:ch17-map` (seed 1, `eta=1`, `gamma=13.3`) the best cost is **17.401 at 2 000-3 000
   iterations** (Table `tab:ch17-convergence` itself gives 17.452 at 2 000 and 17.324 at 3 000,
   and `c_best` is non-increasing by `prop:ch17-invariant`(iii)), so it cannot be at or below
   17.23 at 2 500. Running the same call with `max_iters=12000` gives the first `c_best <= 17.234`
   at **iteration 4 301** (and `c_best = 17.201` only at iteration 5 224).
   *Fix:* replace the clause with the true numbers, e.g. "\rrtstar is still at $17.40$ after
   $2\,500$ iterations and at $17.32$ after $3\,000$; with the same seed it matches the
   string-pulled grid path ($17.23$) at about $4\,300$ iterations and keeps improving, which no
   grid refinement can do." (Reproduce with
   `rrt_star(worked_example_world(), (1,1), (9,9), eta=1.0, gamma=13.3, seed=1, max_iters=12000)`.)

2. **A - Technical accuracy (false geometric claim, contradicts the chapter's own solution).**
   *Location:* `sec:ch17-informed-set`, lines 846-849: "so the ellipse has area $292$: it contains
   the whole map, and still does at the optimum ($167$)".
   *Problem:* $\hat f$ is convex, so its maximum over $[0,10]^2$ is at a corner; the corners
   $(10,0)$ and $(0,10)$ have $\hat f = 2\sqrt{82} = 18.11$. The informed set therefore contains
   the whole map only while $c_{\mathrm{best}} \ge 18.11$; at the optimum $16.909$ it contains
   $98.7\,\%$ of the map, and at $c_{\mathrm{best}} = 17.32$ it contains $99.5\,\%$ (Monte Carlo,
   $4\times10^6$ points). The claim also directly contradicts the answer to
   `exr:ch17-fraction`(c) in `appendices/solutions/ch17-solutions.tex` ("Below
   $c_{\mathrm{best}}=18.11$ the corners drop out") and the code's own report that 8 of 2 657
   informed draws were rejected on this map.
   *Fix:* "so the ellipse has area $292$ and contains the whole map. It keeps containing it until
   $c_{\mathrm{best}}=18.11$ (\cref{exr:ch17-fraction}) and then loses only two thin corners:
   $99.5\,\%$ of the map is still inside at $c_{\mathrm{best}}=17.32$ (the code rejected $8$ of
   $2\,657$ informed draws), so uniform sampling of the map is essentially informed sampling
   there, which is why the two planners coincide in \cref{fig:ch17-convergence}(a)." Keep the
   area $167$ as the *area of the ellipse*, not as a claim of containment.

3. **A/H - Attribution of the radius constant.**
   *Location:* `rem:ch17-fineprint`, lines 769-773: "for \rrtstar, which keeps only a tree, their
   paper states the smaller constant $(2(1+1/d))^{1/d}(\mu(\Xfree)/\zeta_d)^{1/d}$, also found in
   library code. The condition of \cref{eq:ch17-radius} is the stricter of the two and therefore
   safe."
   *Problem:* Karaman and Frazzoli state the *same* threshold
   $2(1+1/d)^{1/d}(\mu(\Xfree)/\zeta_d)^{1/d}$ for RRG and for RRT* (IJRR 2011, the RRG theorem
   and the RRT* theorem); \cref{eq:ch17-radius} **is** their RRT* constant, not a stricter one
   introduced here. The smaller form $(2(1+1/d))^{1/d}(\mu(\Xfree)/\zeta_d)^{1/d}$ is the one used
   by Gammell et al. (Informed RRT*, where the radius is written
   $\bigl(2(1+1/d)\lambda(\Xfree)/\zeta_d\bigr)^{1/d}(\log q/q)^{1/d}$) and by OMPL's `RRTstar`
   (`rewireFactor * pow(2*(1+1/d)*(measure/unitBallMeasure), 1/d)`), and it is *smaller* than the
   proved threshold for every $d\ge2$ (in 2D: $1.73\sqrt{\mu/\pi}$ against $2.45\sqrt{\mu/\pi}$).
   *Fix:* rewrite as: "\cref{eq:ch17-radius} is the constant Karaman and Frazzoli prove, for RRG
   and for \rrtstar alike. Implementations use a smaller one:
   \textcite{gammell2014informed} and the OMPL library take
   $\gamma=(2(1+1/d)\mu(\Xfree)/\zeta_d)^{1/d}$, about $30\,\%$ below the proved threshold in 2D.
   It works well in practice but is not covered by the theorem, so \cref{eq:ch17-radius} is the
   safe choice." Verify the wording against the paper before committing it.

4. **C - Reproducibility: the "wide field" is never located.**
   *Location:* `sec:ch17-informed-set` line 849 ("In a $30\times30$ field with the same walls,
   start and goal"), the caption of `fig:ch17-ellipses` (line 861), the caption of
   `fig:ch17-convergence` (line 997) and `exr:ch17-fraction`(a) (line 1362).
   *Problem:* the field of `wide_example_world()` is $[-10,20]^2$, i.e. the *same* walls, start
   $(1,1)$ and goal $(9,9)$ sitting near the middle of a much larger box. The chapter never says
   this. A reader who assumes the natural $[0,30]^2$ gets completely different numbers: with
   $[0,30]^2$ the informed set at $c_{\mathrm{best}}=24.3$ covers $26.9\,\%$ of the field, not
   $46\,\%$ (a large part of the ellipse would stick out of the field), so
   `exr:ch17-fraction`(a) is not solvable as stated and the $46\,\%$ looks wrong.
   *Fix:* say it once, e.g. "In the field $[-10,20]^2$ with the same two walls, the same start and
   the same goal (\code{wide\_example\_world()}) the free space is nine times larger...", and add
   "$\mathcal{X}=[-10,20]^2$" to `exr:ch17-fraction`(a) as it is already given for the 3D scene in
   part (b). (With this stated, the $46\,\%$/$26\,\%$/$10\,\%$ numbers and the exercise solution
   are correct - I verified them by Monte Carlo.)

5. **C/F - The symbol $c_{\min}$ is used with two meanings.**
   *Location:* `def:ch17-problem` (line ~170, $c_{\min}=\norm{x_{\mathrm{goal}}-x_{\mathrm{init}}}$,
   used again in `eq:ch17-axes`, `eq:ch17-transform`, `alg:ch17-informed`) versus
   `alg:ch17-helpers` lines 333 and 337, where $c_{\min}$ is the running best cost-to-come inside
   \textsc{ChooseParent} (and `c_min` in `lst:ch17-core`).
   *Problem:* the same symbol denotes the straight-line start-goal distance and a local variable of
   a helper, in the same chapter and once in the same algorithm block; the style guide forbids
   competing notation. A reader tracing \textsc{ChooseParent} while holding the informed-set
   formulas in mind is needlessly confused.
   *Fix:* rename the local variable in `alg:ch17-helpers` to $c_{\mathrm{par}}$ (and $x_{\mathrm{par}}$
   for $x_{\min}$ if you want symmetry), update the walkthrough sentence in
   `sec:ch17-pseudocode` that points at line~\ref{alg:ch17-helpers:default}, and rename `c_min` to
   `c_par` in `code/ch17_rrt_star.py` and in the excerpt `lst:ch17-core` so the listing stays
   verbatim.

6. **C/F - The symbol $n$ is used both for $\abs{V}$ and for the iteration count.**
   *Location:* `def:ch17-tree` (line 202: "with $n=\abs{V}$ vertices ... The best cost after $n$
   iterations"), `def:ch17-ao` (line 234: "$Y_n$ ... after $n$ iterations"), `thm:ch17-ao`
   (line 668), against `def:ch17-near`/`eq:ch17-radius` and the first bullet of
   `sec:ch17-radius`, which insists that "$n=\abs{V}$ is the number of vertices *in the tree*, not
   the number of iterations".
   *Problem:* `def:ch17-tree` uses $n$ for both quantities in two consecutive sentences, and the
   chapter itself stresses that they differ (Table `tab:ch17-convergence`: 3 000 iterations,
   2 193 vertices).
   *Fix:* reserve $n$ for $\abs{V}$ throughout; write "the best cost after $i$ iterations" in
   `def:ch17-tree`, "$Y_i$ ... after $i$ iterations" in `def:ch17-ao` and
   "$\Prob(\lim_{i\to\infty}Y_i=c^*)=1$" in `def:ch17-ao` and `thm:ch17-ao` (or state once, in
   `def:ch17-tree`, that both indices tend to infinity together almost surely and that $n$ is used
   for both in limits).

7. **F - The optimum of the shared map disagrees with \cref{ch:ch16}.**
   *Location:* line 33 ("the shortest route has length $16.9$") and `ex:ch17-map` (lines ~575-585,
   "the optimum ... has length $c^*=16.909$").
   *Problem:* \cref{ch:ch16} reports, for the same map and the same collision checker, "the
   shortest path in $\Xfree$ ... has length $16.72$ (in the limit of zero clearance; with a
   clearance of $0.075$ it has length $17.20$)". The reader meets three different optima for one
   map with no explanation. The 16.909 of this chapter is the visibility-graph path around corners
   pushed out by `radius + delta/2 + 0.005 = 0.03`.
   *Fix:* in `ex:ch17-map` state the clearance explicitly ("the corners pushed out by the
   checker's inflation $\rho+\delta/2=0.025$ plus $0.005$, which gives $c^*=16.909$; \cref{ch:ch16}
   quotes $16.72$ for zero clearance and $17.20$ for a clearance of $0.075$"), and in line 33 write
   "$16.9$" as "about $16.9$ (\cref{ch:ch16})" or use the ch16 value there.

8. **F - Acronyms not expanded at first use in this chapter.**
   *Location:* line 57 and line 1223 (`\cbs`, `\ecbs`), line 1236 (`\orca or DWA`).
   *Problem:* the style guide requires each acronym to be defined at first use *in every chapter*;
   CBS, ECBS and DWA appear here without expansion (RRG, PRM*, FMT*, BIT* and SVD are correctly
   expanded).
   *Fix:* at line 57 write "conflict-based search (\cbs) or its bounded-suboptimal variant \ecbs
   (\cref{ch:ch09,ch:ch10})", and at line 1236 "\orca or the dynamic window approach (DWA)".

9. **G - Length: 20 pages against a 13-15 page target; cut the duplicated explanations.**
   *Location and concrete cuts* (about 3/4 to 1 page, none of it required content):
   (a) `sec:ch17-intuition`, the two bullets "Choose the parent"/"Rewire the neighbours"
   (lines ~93-105) restate almost word for word the paragraphs \textbf{ChooseParent} and
   \textbf{Rewire} of `sec:ch17-primitives` (lines ~283-305); shorten the bullets to one sentence
   each and let the formal paragraphs carry the detail.
   (b) The random-geometric-graph remark with `\cite{penrose2003random}` appears twice, at the end
   of `sec:ch17-intuition` (line ~110) and again at the end of "Why the radius must shrink"
   (lines ~455-460); keep the second, drop the first.
   (c) The expected-neighbour computation $\zeta_d\gamma^d\log n/\mu(\Xfree)$ is derived three
   times: third bullet of `sec:ch17-radius`, again in "Why the radius must shrink", and again in
   `sec:ch17-cost` ("By the computation in \cref{sec:ch17-radius}"); keep the bullet and the
   back-reference in `sec:ch17-cost`, and cut the re-derivation in the middle occurrence to its
   conclusion.

## Suggestions

* `sec:ch17-informed` / implementation notes: Gammell et al. also shrink the *connection radius*
  with the informed set, replacing $\mu(\Xfree)$ by the measure of
  $\mathcal{X}_{\hat f}\cap\Xfree$ in \cref{eq:ch17-radius}. One sentence would close the loop with
  the observation that \irrtstar pays $8\,486$ segment checks against $7\,399$ - with the updated
  measure the radius shrinks faster and part of that extra cost disappears. Using $\mu(\Xfree)$, as
  the chapter does, is safe (a larger $\gamma$ is always admissible), and saying so is worth a
  clause.
* `code/ch17_rrt_star.py` (and therefore `lst:ch17-core`): `dists` is bound only inside
  `if choose_parent and len(near):` but is read in the \textsc{Rewire} loop, so the call
  `rrt_star(..., choose_parent=False, rewire=True)` raises `NameError`. Move
  `dists = np.linalg.norm(tree.V[near] - x_new, axis=1)` just after `near` is computed.
* Pseudocode/code mismatch: `alg:ch17-rrtstar` line~\ref{alg:ch17-rrtstar:near} puts
  $x_{\mathrm{nearest}}$ into $X_{\mathrm{near}}$, so `alg:ch17-helpers`'s \textsc{Rewire} may
  rewire $x_{\mathrm{nearest}}$; the implementation iterates over `near` only and can miss it
  (possible when $r_n<\norm{x_{\mathrm{new}}-x_{\mathrm{nearest}}}$). Either add the index to
  `near` in the code, or say in the walkthrough that $x_{\mathrm{nearest}}$ is added for
  \textsc{ChooseParent} only.
* `sec:ch17-cost`: a kd-tree range query costs $\bigO{\log n + \abs{X_{\mathrm{near}}}}$, not
  $\bigO{\log n}$; the conclusion is unchanged because $\abs{X_{\mathrm{near}}}=\bigO{\log n}$ in
  expectation, but the reader who implements it should see the reporting term.
* `ex:ch17-gamma`: $2(4/3)^{1/3}(1000/\zeta_3)^{1/3}=13.656$, so "13.65" should be "13.66".
* Solution to `exr:ch17-fraction`(b): the 3D percentages are volume ratios
  $\mu(\text{ellipsoid})/\mu(\mathcal{X})$; at $c_{\mathrm{best}}=17.0$ the ellipsoid pokes out of
  $[0,10]^3$, so the fraction of the box actually inside the informed set is $38.7\,\%$
  ($2.6$ draws), not $41\,\%$ ($2.4$ draws). Either say "volume of the ellipsoid, as a fraction of
  the box" or give the clipped value.
* Only four of the eight exercises have entries in `appendices/solutions/ch17-solutions.tex`
  (the appendix is "selected exercises", and ch15/ch16/ch18 also give four, so this is within
  convention), but `exr:ch17-radius` is the one pure numeric drill of the chapter and a lone
  reader would benefit from a three-line answer ($n=1\,264$; $\abs{X_{\mathrm{near}}}\approx67$ at
  $n=10^4$; $\gamma^*=12.22$ and $13.66$; $n\approx9\,119$ for $\eta=1.5$, $\gamma=15$).
* `frontmatter/notation.tex` has a row for `\rrt` ($T=(V,E)$, $\eta$, `\Nearest`, `\Steer`) but
  none for this chapter's symbols; add $r_n$, $\gamma_{\rrtstar}$, $c_{\mathrm{best}}$,
  $c_{\min}$, $\zeta_d$, $\Near$ pointing at `\cref{ch:ch17}`.
* Caption of `fig:ch17-radius` explains the $\gamma=13.3$ curves and the dashed asymptote but
  never mentions the $\gamma=20$ curve that carries the "larger $\gamma$ buys more rewiring"
  point; name it.
* `tab:ch17-convergence`: the final row repeats "16.909" in both cost columns; a single
  `\multicolumn` entry would read better.
* `thm:ch17-ao` could state the two implicit assumptions ($\mu(\Xfree)>0$ and $\mathcal{X}$
  bounded, and that the goal point enters the tree through the goal bias) in half a line, since
  the chapter is otherwise scrupulous about assumptions.

## What must be kept

This is a strong chapter and most of it should not be touched. Keep the three-panel
`fig:ch17-primitives` with the hand-computed numbers and the before/after trace table
`tab:ch17-hand`: the reader sees \textsc{Near}, a blocked cheapest parent, a real rewire and a
propagated cost in one page, and every entry comes out of `tiny_example()`. Keep the symbol-by-symbol
dissection of `eq:ch17-radius` and the "why the radius must shrink, and shrink slowly" paragraph -
this is the best explanation of that formula I have read at textbook level, and the $k$-nearest
subsection with $k_{\mathrm{RRG}}>e(1+1/d)$ is exactly right. Keep the five-step ball-covering
proof: the $q_n=r_n/(2+\theta)$ bookkeeping, the union bound, the Borel-Cantelli step and the
explicit derivation of where the constant $2(1+1/d)^{1/d}$ comes from are correct and are the
right level of detail for a proof idea, and `fig:ch17-ball-covering` carries it. Keep the bullet
list of what the theorem does *not* say, and the honest `rem:ch17-fineprint` about the gap closed
by Solovey et al. Keep the informed-set section: the conjugate-diameter derivation from
$2\sqrt{b^2+c_{\min}^2/4}=c_{\mathrm{best}}$, the constant-Jacobian argument for uniformity, the
SVD rotation with $\det\mat{U}\det\mat{V}$, `fig:ch17-ellipse-transform` and the volume argument
for *when* informed sampling pays. Keep the four pitfalls (they are the four real bugs), the
comparison table `tab:ch17-comparison`, the anytime/seeding/re-check structure of the drone box,
and above all the discipline that every number in the text, the tables and the generated figures
is produced by `code/ch17_rrt_star.py` and `code/figures/gen_ch17_convergence.py` - I re-ran both
and, apart from item 1, they agree to the last digit.

---

## Response to review (round 1)

All nine required changes are applied; the chapter builds with status 0, no errors and no
overfull boxes above 15 pt, the self-test of `Overleaf/code/ch17_rrt_star.py` passes, and
`figures/data/ch17-convergence.dat` is byte-identical after re-running
`code/figures/gen_ch17_convergence.py` (the code edits are a rename and a hoisted
computation, so no number moved).

**Required change 1 (A) — the "2 500 iterations" claim, `sec:ch17-example`.** Replaced with
the measured numbers: "\rrtstar is still at $17.40$ after $2\,500$ iterations and at $17.32$
after $3\,000$; with the same seed it matches the string-pulled grid path ($17.23$) at
iteration $4\,301$ and keeps improving ($17.05$ at $12\,000$), which no grid refinement can
do." Verified with `rrt_star(worked_example_world(), (1,1), (9,9), eta=1.0, gamma=13.3,
seed=1, max_iters=12000)`: 17.401 at 2 500, 17.324 at 3 000, first $c_{\text{best}}\le17.234$
at iteration 4 301 (17.210), 17.048 at 12 000.

**Required change 2 (A) — the informed set does not contain the whole map at the optimum.**
Rewritten as suggested: the ellipse (area 292) contains the map, keeps containing it until
$c_{\text{best}}=18.11$ (cross-referenced to `exr:ch17-fraction`), then loses two thin
corners; 99.5 % of the map is inside at 17.32 (8 of 2 657 informed draws rejected) and 98.7 %
at the optimum, where the area is 167. Monte Carlo with $4\times10^6$ points confirms
100 % / 100 % / 99.47 % / 98.73 % at $c_{\text{best}}=21.003$, 18.11, 17.324, 16.909.

**Required change 3 (A) — misattribution in `rem:ch17-fineprint`.** Rewritten:
`eq:ch17-radius` is the constant Karaman and Frazzoli prove, for RRG and for \rrtstar alike;
the smaller $(2(1+1/d)\mu(\Xfree)/\zeta_d)^{1/d}$ is what Gammell et al. and OMPL use
($1.73\sqrt{\mu/\pi}$ against the proved $2.45\sqrt{\mu/\pi}$ in 2D, about 30 % below), works
in practice but is not covered by the theorem. The Solovey et al. sentence is unchanged.

**Required change 4 (C) — the extent of the wide field.** The field is now named as
$[-10,20]^2$ in `sec:ch17-informed-set` (with `wide_example_world()`), in the caption of
`fig:ch17-ellipses`, in the caption of `fig:ch17-convergence`(b) and in `exr:ch17-fraction`(a)
("$\mathcal{X}=[-10,20]^2$"), so the 46 %/26 %/10 % numbers are now reproducible.

**Required change 5 (C) — the two meanings of $c_{\min}$.** The \textsc{ChooseParent} locals
are now $x_{\mathrm{par}}$, $c_{\mathrm{par}}$ in `alg:ch17-helpers`, in the walkthrough
sentence, and as `i_par`, `c_par` in `code/ch17_rrt_star.py` (both `rrt_star` and
`tiny_example`) and hence in `lst:ch17-core`, which is still a verbatim copy of the file. A
comment in the code says why. $c_{\min}$ now only ever means the start–goal distance.

**Required change 6 (F) — $n$ versus the iteration count.** `def:ch17-tree` now says that $n$
is reserved for $\abs{V}$ and iterations are counted by $i$ (with $n<i$); the best cost is
"after $i$ iterations". `def:ch17-ao` and `thm:ch17-ao` use $Y_i$ and
$\Prob(\lim_{i\to\infty}Y_i=c^*)=1$.

**Required change 7 (F) — three optima for one map.** `ex:ch17-map` now states the clearance
("the wall corners pushed out by the checker's inflation ($\delta/2=0.025$ for a point robot)
plus a margin of $0.005$") and reconciles the values: ch16 quotes 16.72 at zero clearance and
17.20 at clearance 0.075. Line 33 now reads "length about $16.9$ (\cref{ch:ch16})".

**Required change 8 (F) — acronyms.** First use in the chapter is now "conflict-based search
(\cbs) or its bounded-suboptimal variant \ecbs"; the drone box says "\orca or the dynamic
window approach, DWA". (ORCA was left as the reviewer wrote it.)

**Required change 9 (G) — length.** All three prescribed cuts are made: (a) the two
`sec:ch17-intuition` bullets are one sentence each; (b) the first `penrose2003random` remark
is gone (the one in "Why the radius must shrink" is kept); (c) the middle re-derivation of
$\zeta_d\gamma^d\log n/\mu(\Xfree)$ is reduced to its conclusion ("the count of the third
bullet above would lose its $\log n$"), with the bullet and the `sec:ch17-cost`
back-reference kept. Four further trims: the duplicated "corner cuts need a sample in a small
region", the repeated "nine times larger" in `sec:ch17-informed-results`, the repeated
safe-upper-bound argument in "Choosing $\gamma$", and a tightened motivation paragraph and
roadmap. Nothing on the keep list was touched. The chapter is nevertheless 21 pages
(24–44 of the single-chapter build) rather than 19: required changes 1, 2, 3 and 7 and the
accepted suggestions add roughly as much text as the cuts remove. No required content was
removed to save space.

**Suggestions adopted.** Informed \rrtstar also shrinks the radius with the informed set
(one sentence, with why $\mu(\Xfree)$ is admissible and what the extra checks buy); the
`dists` NameError with `choose_parent=False, rewire=True` (the array is now computed right
after `near`, in the file and in `lst:ch17-core`); the pseudocode/code mismatch about
$x_{\mathrm{nearest}}\in X_{\mathrm{near}}$ (stated in the walkthrough); the kd-tree range
query $\bigO{\log n+\abs{X_{\mathrm{near}}}}$; 13.65 → 13.66 in `ex:ch17-gamma`; the 3D
percentages in the solution to `exr:ch17-fraction`(b) are now labelled as ellipsoid volumes,
with the clipped 38.7 % (2.6 draws) at $c_{\text{best}}=17.0$; a solution for
`exr:ch17-radius` (1 264 vertices; 67 neighbours at $n=10^4$; 12.22 and 13.66; 9 119);
the caption of `fig:ch17-radius` now names the $\gamma=20$ curve; the last row of
`tab:ch17-convergence` uses `\multicolumn`; `thm:ch17-ao` states the two implicit assumptions
($\mathcal{X}$ bounded with $\mu(\Xfree)>0$, goal enters through the bias).

**Suggestion not adopted.** The row for this chapter's symbols in `frontmatter/notation.tex`:
that file is outside this chapter's scope (the finisher brief forbids editing shared front
matter). It is left for the book-level pass, with the symbols to add being $r_n$,
$\gamma_{\rrtstar}$, $c_{\mathrm{best}}$, $c_{\min}$, $\zeta_d$ and \textsc{Near}.
