# Review of Chapter 17 (RRT* and Informed RRT*) - round 2

Reviewed: `Overleaf/chapters/ch17-rrt-star.tex` (1428 lines), the nine figure files in
`Overleaf/figures/ch17/`, `Overleaf/code/ch17_rrt_star.py` (773 lines),
`Overleaf/code/figures/gen_ch17_convergence.py`,
`Overleaf/appendices/solutions/ch17-solutions.tex`,
`Overleaf/appendices/glossary/ch17-terms.tex`, `Overleaf/bib/ch17-extra.bib`, against
`STYLE_GUIDE.md` section 9, `docs/specs/ch17.md` and `docs/core-idea.txt` (Week 8), and
against `reviews/ch17-round1.md` with the reviser's response.

**Build.** `cd Overleaf && ./build.sh ch17-rrt-star` returns status 0. No `!` errors, **no
overfull or underfull boxes at all** (`grep -c Overfull` on the log returns 0), no undefined
citations, no undefined ch17 labels. The only `??` in the chapter body are `ch:ch13`,
`ch:ch14` (line 1260, the drone box) and, in the front matter, `ch:ch11`, `ch:ch20`,
`ch:ch21`; all of these are chapters outside the single-chapter build, which is allowed. I
verified that every cross-chapter pointer names the right chapter (ch09 = CBS, ch10 = ECBS,
ch13 = RVO/ORCA, ch14 = DWA, ch05 = LPA*/D* Lite, ch04 = A*, ch16 = RRT) - with the one
exception in required change 2.

**Length.** The chapter body is PDF pages 25-45 of `build/only-ch17-rrt-star.pdf` (printed
pages 180-200) = **21 pages**, one over the 20-page ceiling; page 45 carries only nine lines
of the last exercise.

**Code.** `python3 code/ch17_rrt_star.py` passes its self-test in 4.8 s; the assertions cover
exactly what `docs/specs/ch17.md` asks for (paths collision-free, `costs_consistent()`,
`c_best` monotone, `C` orthogonal with `det = 1` and `C e_1 = a_1`, informed samples inside
the hyperspheroid, final cost within 5 % of both the grid reference and the visibility
optimum). `python3 code/figures/gen_ch17_convergence.py` reruns in ~4 min and leaves
`figures/data/ch17-convergence.dat`, `figures/ch17/snapshots.tex` and
`figures/ch17/ellipses.tex` byte-identical (`git status --porcelain` is empty).

**Round-1 items: all nine verified as resolved, and re-checked numerically.**

1. (17.40 / 17.32 / iteration 4 301 / 17.05) - confirmed by re-running
   `rrt_star(worked_example_world(), (1,1), (9,9), eta=1.0, gamma=13.3, seed=1,
   max_iters=12000)`: `c_best` = 17.4006 at 2 500, 17.3236 at 3 000, first value `<= 17.234`
   at iteration **4 301** (17.2096), 17.0484 at 12 000. Exactly the text.
2. (informed set does not contain the whole map at the optimum) - confirmed by Monte Carlo
   with 4x10^6 points on `[0,10]^2`: 100.00 % inside at `c_best` = 21.003 and 18.11,
   **99.47 %** at 17.324, **98.73 %** at 16.909; `InformedSampler.measure` gives areas
   291.90 and 166.89. The text's 99.5 %, 98.7 %, 292 and 167 are right, and the "8 of 2 657
   informed draws" is printed by the self-test.
3. (attribution of the radius constant) - `rem:ch17-fineprint` is now correct:
   `eq:ch17-radius` is what Karaman and Frazzoli prove for RRG *and* RRT*, and
   `(2(1+1/d) mu/zeta_d)^{1/d}` is what Gammell et al. and OMPL use. The 2D figures check
   out: 2(1.5)^{1/2} = 2.449 against (3)^{1/2} = 1.732, i.e. 29.3 % below, "about 30 %".
   The Solovey et al. sentence is right too: their radius uses the exponent 1/(d+1), which
   for a base below 1 shrinks more slowly, as the text says.
4. (the wide field is located) - `[-10,20]^2` now appears in `sec:ch17-informed-set` with
   `wide_example_world()`, in both figure captions and in `exr:ch17-fraction`(a). The 46 % /
   10 % of the text and the 45.6 % / 25.7 % / 10.1 % of the solution are correct (the whole
   ellipse fits inside the field at `c_best` = 24.3, so the area ratio is exact), and the
   generator prints 45.5 % and 10.2 %.
5. (`c_min` overloaded) - fixed: `alg:ch17-helpers` uses `x_par`/`c_par`, the walkthrough
   follows, and `code/ch17_rrt_star.py` uses `i_par`/`c_par`. `c_min` now means only the
   start-goal distance.
6. (`n` versus the iteration count) - fixed: `def:ch17-tree` reserves `n` for `|V|` and
   counts iterations with `i`; `def:ch17-ao` and `thm:ch17-ao` use `Y_i` and
   `P(lim_{i->inf} Y_i = c*) = 1`.
7. (three optima for one map) - fixed: `ex:ch17-map` states the inflation
   (`delta/2 = 0.025` plus 0.005) and reconciles 16.909 with ch16's 16.72 and 17.20; line 33
   reads "about 16.9 (ch16)".
8. (acronyms) - CBS, ECBS and DWA are now expanded at first use (see the suggestion about
   ORCA below).
9. (length cuts) - all three prescribed cuts are in place: the two intuition bullets are one
   sentence each, only the second `penrose2003random` remark survives, and the middle
   re-derivation of `zeta_d gamma^d log n / mu` is reduced to "the count of the third bullet
   above would lose its `log n`".

**Independent technical re-check (all correct).** `gamma* = 2(1.5)^{1/2}(76/pi)^{1/2} =
12.046` -> 12.05; `2(4/3)^{1/3}(1000/zeta_3)^{1/3} = 13.657` -> 13.66; the cap stops at
n = 1 264; r_n = 0.9457 at n = 1 438 and 0.7878 at n = 2 193 (table: 0.946, 0.788);
`zeta_d gamma^d log n / mu` at n = 10^4 gives 67; `k_n = ceil(1.1 e (1+1/d) log 1438) = 33`;
the ball-covering bookkeeping (`q_n = r_n/(2+theta)`, spacing `theta q_n`, two points in
consecutive balls at most `(2+theta) q_n = r_n` apart, `M_n ~ (n/log n)^{1/d}`,
`a = zeta_d gamma^d/((2+theta)^d mu)`, `sum_n M_n n^{-a} < inf` iff `a > 1+1/d` iff
`gamma > (2+theta)(1+1/d)^{1/d}(mu/zeta_d)^{1/d}`) is exactly right, and so is the
no-cycle argument of `prop:ch17-invariant`(i). The 3D informed-set numbers check out:
with `c_min = 15.588` (start `(0.5,0.5,0.5)`, goal `(9.5,9.5,9.5)` in `scene_3d()`) the
ellipsoid volumes are 3 767, 2 217, 409 and 108.5 at `c_best` = 23.45, 21.07, 17.0, 16.0,
and Monte Carlo over `[0,10]^3` gives 100 %, 98.4 %, **38.69 %** and **10.88 %** of the box
inside the informed set, matching the solution's 38.7 % / 2.6 draws and 9.2 draws.
Both listings are verbatim copies of `code/ch17_rrt_star.py` (checked programmatically);
`lst:ch17-core` is 38 lines, under the 45-line cap. All ten citation keys resolve, and I can
vouch for every one of them (Karaman & Frazzoli IJRR 30(7):846-894 2011; Gammell et al. IROS
2014 pp. 2997-3004; BIT* ICRA 2015 pp. 3067-3074; Informed sampling T-RO 34(4) 2018; Janson
et al. IJRR 34(7) 2015; Solovey et al. ICRA 2020; Karaman et al. ICRA 2011; Penrose, OUP
2003; LaValle 2006 and TR 98-11). Every "must cover" item of `docs/specs/ch17.md` is
present, including all four named pitfalls, the comparison table, the Week-8 coding exercise
and the ellipsoid-derivation exercise; 29 unique index entries; 7 figures, all referenced,
all in the shared TikZ styles; 8 exercises graded 1,1,2,2,2,2,3,3.

## Verdict

**Minor revision.** The chapter is technically sound and every number in it is reproduced by
its own code; all nine round-1 items are genuinely fixed and I re-verified each one
numerically. Three items remain, and all three are local: one sentence that overstates what
informed sampling does to the tree, one cross-reference that points at a chapter which does
not contain the fact being cited, and one page over the length ceiling with two concretely
nameable duplications. No re-run, no restructuring and no new experiment is needed.

## Required changes

1. **A - Technical accuracy: "the tree grows only inside the current ellipsoid" is false.**
   *Location:* `sec:ch17-informed`, line 950 (the paragraph introducing
   `alg:ch17-informed`): "from the first solution on, the tree grows only inside the current
   ellipsoid, which shrinks whenever \textsc{Rewire} improves the goal's branch."
   *Problem:* only the *samples* are drawn from the informed set. A new vertex is
   `x_new = Steer(x_nearest, x_rand)`, a point on the segment from `x_nearest` towards the
   sample; `x_nearest` is very often a vertex the tree acquired *before* the first solution
   and therefore outside the current ellipsoid, so `x_new` can be outside it too. The
   chapter's own code agrees with me and not with this sentence: `InformedSampler.sample`
   returns samples, and the self-test asserts the hyperspheroid membership of *samples*
   (`assert np.all(dsum <= c_best + 1e-9)`), never of vertices. A reader who takes the
   sentence literally will write an assertion over `tree.V` that fails.
   *Fix:* replace the clause by, e.g., "from the first solution on every sample is drawn
   inside the current ellipsoid, so the tree grows towards it - a new vertex can still land
   just outside, because $\Steer$ starts from a vertex that may predate the solution - and
   the ellipsoid shrinks whenever \textsc{Rewire} improves the goal's branch."
   *Category:* A.

2. **F - A cross-reference to a fact that `ch:ch02` does not contain.**
   *Location:* `sec:ch17-sampling`, line 915, first bullet: "the normalised Gaussian is
   uniform on the sphere (\cref{ch:ch02})".
   *Problem:* `chapters/ch02-toolbox.tex` defines the multivariate Gaussian
   $\Normal(\vect{\mu},\mat{\Sigma})$ and the $k\sigma$ covariance ellipse, but nowhere
   states or proves that $\vect{u}/\norm{\vect{u}}$ with $\vect{u}\sim\Normal(\vect{0},\mat{I})$
   is uniform on the unit sphere (a search of that file for "sphere", "isotropic" and
   "rotation" finds only the bounding-sphere drone model and the covariance ellipse). The
   lone reader follows the pointer and finds nothing. The fact *is* proved in this chapter,
   in the solution to `exr:ch17-ellipsoid`(c).
   *Fix:* replace "(\cref{ch:ch02})" by the one-clause reason plus the internal pointer:
   "(the standard Gaussian density depends on $\vect{u}$ only through $\norm{\vect{u}}$ and
   is therefore rotation-invariant; \cref{exr:ch17-ellipsoid}(c))".
   *Category:* F.

3. **G - Length: 21 pages against the 20-page ceiling; two named duplications carry it over.**
   *Location and concrete cuts* (about 15 lines, no required content lost; page 45 currently
   holds only nine lines, so this is enough):
   (a) `sec:ch17-informed-results`, lines 995-999 ("On the small map (a) the three planners
   find their first solution at the same iteration, median $252$ ... $2.5\,\%$ above the
   optimum") repeats numbers the reader already has: `17.33\pm0.08` and `23.51\pm1.67` are
   given in `sec:ch17-example` lines 605-608, "$2.5\%$ above the optimum" at line 603, and
   "on the small map \rrtstar and \irrtstar coincide" a third time in the caption of
   `fig:ch17-convergence` (line 1022). *Fix:* compress to one sentence, e.g. "On the small
   map (a) the informed set is essentially the whole map (\cref{sec:ch17-informed-set}), so
   \rrtstar and \irrtstar coincide, both reaching the $17.33\pm0.08$ of
   \cref{sec:ch17-example} while \rrt stays at $23.51\pm1.67$." Keep the wide-field
   sentences that follow, including the segment-check comparison and the
   `gammell2014informed` radius remark - those are new information.
   (b) "Any upper bound on $\mu(\Xfree)$, such as $\mu(\mathcal{X})$, is safe because a
   larger $\gamma$ still satisfies the condition" is stated four times: line 401 (fifth
   bullet of `sec:ch17-radius`), lines 695-697 (fourth bullet after `thm:ch17-ao`), line
   1010 (`sec:ch17-informed-results`) and line 1144 ("Choosing $\gamma_{\rrtstar}$").
   *Fix:* keep line 401 in full; reduce the other three to back-references, e.g. "which is
   usually unknown; any upper bound is safe (\cref{sec:ch17-radius})" at line 696, "keeping
   $\mu(\Xfree)$ is admissible (\cref{sec:ch17-radius}) and those extra checks are what it
   costs" at line 1010, and drop "the safe upper bound of \cref{sec:ch17-radius}" to just
   "(\cref{sec:ch17-radius})" at line 1144.
   *Category:* G. Do **not** buy pages anywhere else: the proof, the radius dissection, the
   informed-set derivation, the four pitfalls and the tables are all required content and
   are at the right length.

## Suggestions

* Drone box, line ~1236: `\orca` is still the bare acronym on its first (and only) use in
  this chapter, while CBS, ECBS and DWA are now expanded. Write "optimal reciprocal
  collision avoidance (\orca) or the dynamic window approach, DWA". (Round 1 dictated the
  wording that left it out, so this is a leftover of that fix, not a new defect.)
* `thm:ch17-ao`, line ~666: "let the samples be uniform on $\mathcal{X}$" sits slightly
  awkwardly next to "let $x_{\mathrm{goal}}$ enter the tree through the goal bias", since
  the sampler is a mixture until the goal is a vertex. Half a clause fixes it: "let the
  samples be uniform on $\mathcal{X}$ apart from the goal-biased draws, which stop once
  $x_{\mathrm{goal}}\in V$".
* `sec:ch17-informed-set`, the $\hat f$ analogy: "the informed set is the region
  $\fcost\le C^*$ that \astar with a consistent heuristic never leaves" - \astar *generates*
  nodes with $\fcost>C^*$; it never *expands* one. "never expands outside" is the exact
  claim and costs one word.
* Solution to `exr:ch17-fraction`(b): parts (a) and (c) are fully checkable, but for
  $c_{\mathrm{best}}=23.45$ and $21.07$ the answer only says "(nearly) the whole box". The
  exact clipped fractions are $100\,\%$ and $98.4\,\%$ (Monte Carlo, $2\times10^6$ points in
  $[0,10]^3$), i.e. $1.00$ and $1.02$ draws per accepted sample; one clause makes the whole
  part verifiable.
* `ex:ch17-gamma` quotes $\gamma^*=12.05$ from the exact $\mu(\Xfree)=76$, while
  `gen_ch17_convergence.py` prints `gamma* = 12.04` from its Monte-Carlo estimate
  $\hat\mu=75.9$. A parenthesis ("the code's Monte-Carlo estimate $\hat\mu=75.9$ gives
  $12.04$") would stop a reader who runs the script from thinking one of the two is wrong.
* `tab:ch17-comparison`: the PRM row reads "no ($k$ fixed)" while PRM\textsuperscript{*}
  appears two rows below; writing the first row as "PRM ($k$ fixed)" makes the contrast
  visible at a glance.
* Still open from round 1 and deliberately deferred by the reviser (correctly, since
  `frontmatter/notation.tex` is outside the chapter's scope): the notation table has a row
  for `\rrt` but none for this chapter's symbols. Please carry
  $r_n$, $\gamma_{\rrtstar}$, $c_{\mathrm{best}}$, $c_{\min}$, $\zeta_d$ and $\Near$ into
  the book-level pass so it is not lost. Note also that `notation.tex` line 72 reserves
  $\gamma$ for the goal vertex "from \cref{ch:ch04} on", while this chapter uses a bare
  $\gamma$ for the radius constant throughout; the subscripted $\gamma_{\rrtstar}$ is
  unambiguous, but the book-level pass should decide whether to say so in the table.

## What must be kept

Everything on the round-1 keep list survived the revision intact, and it should survive this
one too. Keep the three-panel `fig:ch17-primitives` with the hand-computed numbers and the
before/after trace `tab:ch17-hand`: \textsc{Near}, a blocked cheapest parent, a real rewire
and a propagated cost in a single page, every entry out of `tiny_example()`. Keep the
symbol-by-symbol dissection of `eq:ch17-radius` and the "why the radius must shrink, and
shrink slowly" paragraph, together with the $k$-nearest subsection and
$k_{\mathrm{RRG}}>e(1+1/d)$ - this remains the clearest textbook-level account of that
formula I know. Keep the five-step ball-covering proof with the explicit origin of the
constant $2(1+1/d)^{1/d}$, the Borel-Cantelli step and `fig:ch17-ball-covering`, the bullet
list of what the theorem does *not* say, and the now-correct `rem:ch17-fineprint`, which is
better than round 1: it names the proved constant, the smaller constant that OMPL and
Gammell et al. actually ship, and the Solovey et al. gap with the $1/(d+1)$ exponent, all in
one honest paragraph. Keep the informed-set section end to end - the conjugate-diameter
derivation, the constant-Jacobian uniformity argument, the SVD rotation with
$\det\mat{U}\det\mat{V}$, `fig:ch17-ellipse-transform`, and the volume argument for *when*
informed sampling pays, now with the corrected 99.5 % / 98.7 % containment story that
explains why panel (a) of `fig:ch17-convergence` shows two coincident curves. Keep the four
pitfalls, `tab:ch17-comparison`, the anytime/seeding/re-check structure of the drone box,
the eight exercises with their five worked solutions, and above all the discipline that
every number in the prose, the tables, the captions and the generated figures comes out of
`code/ch17_rrt_star.py` and `code/figures/gen_ch17_convergence.py`. I re-ran both from
scratch and, this round, **every single quoted number matches** - including the four new
ones introduced by the round-1 fixes.
