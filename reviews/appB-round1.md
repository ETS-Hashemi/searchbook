# Review of Appendix B (Mathematical Refresher) - round 1

Reviewed: `Overleaf/appendices/appB-math-refresher.tex` (1168 lines), its five figure files in
`Overleaf/figures/appB/` (`convexity.tex`, `gaussian-conditioning.tex`, `gradient-descent.tex`,
`laplacian.tex`, `lp-geometry.tex`), the number/data generator
`Overleaf/code/figures/gen_appB_numbers.py`, and the glossary file
`Overleaf/appendices/glossary/appB-terms.tex` (12 items, all merged into
`Overleaf/appendices/glossary.tex`), against `STYLE_GUIDE.md` section 9 (A-H), the spec
`docs/specs/appB.md` and the training plan `docs/core-idea.txt`.

Build: `./build.sh appB-math-refresher` exits 0, no `!` errors, **no undefined citations**, and
the only overfull box in the whole run (29.10 pt, log line 1947) is in the front-matter *List of
Algorithms* (the RRT caption of another chapter), **not** in this appendix - do not chase it. The
undefined references reported (`ch:ch11`, `ch:ch13`, `ch:ch14`, `ch:ch19`, `ch:ch20`, `ch:ch21`,
`ch:ch24`) are cross-chapter references, which `STYLE_GUIDE.md` section 7 permits in a
single-chapter build; every `ch:chNN` target used by the appendix exists in `Overleaf/chapters/`,
so they will resolve in the full book. Length: PDF pages 28-47, i.e. **20 appendix pages** (the
first 27 pages are front matter). That is at the ceiling the review brief allows and 5 pages over
the spec's 12-15, but I found no padding worth removing: every subsection is a "must cover" item
of the spec and the prose is dense. **No cuts are required.**

Code check: `python3 code/figures/gen_appB_numbers.py` runs in 0.04 s, all its `assert`s pass, and
it reproduces **every** number quoted in the text. I checked all of them against the output and,
independently, by hand: eigenvalues 2.8/0.2, eigenvector `(3,2)/sqrt(13)`, 33.69 deg, semi-axes
1.673/0.447, Cholesky `[[1.4142,0],[0.8485,0.5292]]`, `Sigma^-1` entries, Schur complement 0.56,
`A^T A = [[3,3],[3,5]]`, `A^T b = (3.0,4.9)`, `(p0,v) = (0.05,0.95)`, residuals `(0.05,-0.10,0.05)`
with squared norm 0.015, `H` at `(3,4)`, `h = (5,0.9273)`, linear prediction `(4.9000,0.8873)` vs
exact `(4.9041,0.8865)`, `||delta|| = 0.2236`, double integrator 0.205 m / 2.1 m/s, conditional
`N(3.2,0.56)` and `rho = 0.85`, Monte Carlo `0.8695 +- 0.0034` against `1-e^-2 = 0.8647`, the six
chi-square gates (3.841/6.635, 5.991/9.210, 7.815/11.345), Bayes 1/3, LP vertices `0/8/9/6` with
multipliers `(1.5,0.5)` and the relaxed optimum 10.5 at `(4.5,0.5)`, all five branch-and-bound
nodes (21, 20.67, 18, 19, 20) with the integer optimum `(4,0)`, the three gradient-descent runs
(`x_20 = (3.226, ~0)`, `f = 5.20`; `(0.170, 0.023)`, `f = 0.017`; `x_2 = 13.5`, `f = 905`), and the
Laplacian spectrum `(0,1,3,4)`, Fiedler vector `(-2,0,1,1)` and `(0,0,3,3)` after the cut. Nothing
in category A failed here.

Completeness (B): every numbered item of the spec's six sections is present, including the proof
of the Gaussian conditioning formula, the LP standard form, big-M, branch and bound, the Laplacian
spectrum with the `lambda_2 > 0` iff connected argument, and the `heapq`/`dict` note. The six
mandated citation keys plus `wolsey1998integer`, `doucet2001sequential`, `barshalom2001estimation`
and `fiedler1973algebraic` all resolve (the last four live in `references.bib`,
`bib/ch19-extra.bib`, `bib/ch22-extra.bib` and `bib/ch23-extra.bib`); I can vouch for all ten as
real works with correct authors, titles, venues and years. Index entries: 56, with subentries,
correctly bracketed by `\index{mathematical refresher|(}` / `|)`.

Note on exercises: the spec for this appendix prescribes sections, figures, tables, glossary and
summary and says "No code/solutions"; it does not ask for an exercise set, `appC-solutions.tex`
has no Appendix B block, and the round-2 review of Appendix A explicitly declined to require
chapter-style exercises in an appendix. I therefore do **not** raise the missing exercise section
as a required change under E; see Suggestion 1.

## Verdict

**Minor revision.** Five required changes, each a local edit of one sentence or one clause: three
statements in category A that are wrong or missing a hypothesis as written (all with concrete
counterexamples below), one unreferenced table (D), and one misplaced citation locator (H). The
mathematics elsewhere - and it is a lot of mathematics - is correct, and every quoted number is
reproduced by the script.

## Required changes

1. **`thm:appB-conditioning` (Theorem B.20, line 514, and the sentence at lines 498-499) -
   missing non-degeneracy hypothesis and a false blanket claim.** *Problem:* the theorem is stated
   for any jointly Gaussian `(x_a, x_b)` but its statement uses `Sigma_bb^{-1}` and its proof
   divides densities, so it needs a non-singular covariance; and the preceding sentence, "A
   singular `Sigma >= 0` has no density, but the two theorems that follow still hold for it", is
   false for the conditional half, since `Sigma_bb^{-1}` need not exist (take `x_b` deterministic:
   `Sigma_bb = 0`). *Fix:* add "`with Sigma > 0`" to the hypothesis of the theorem (in
   `eq:appB-joint`), and replace the sentence at lines 498-499 with, e.g., "A singular
   `Sigma >= 0` has no density; `\cref{thm:appB-affine}` still holds for it, because a degenerate
   Gaussian is defined by its mean and covariance through its characteristic function, while the
   conditioning formula of `\cref{thm:appB-conditioning}` needs `Sigma_bb > 0` (or the
   Moore-Penrose pseudo-inverse `Sigma_bb^+` in place of `Sigma_bb^{-1}`)." Nothing downstream
   changes: `thm:appB-linear-update` already has `S = H P H^T + R > 0` whenever `R > 0`.
   *Category:* A.

2. **`thm:appB-local-global` (Proposition B.25, line 723), second sentence - false on a proper
   convex subset.** *Problem:* "If `f` is differentiable on `R^n`, `x*` is a global minimiser iff
   `grad f(x*) = 0`" is stated inside a proposition whose `f` lives on an arbitrary convex set
   `C`. Counterexample: `f(x) = x` on `C = [0,1]` is convex and differentiable, `x* = 0` is the
   global minimiser, and `grad f(0) = 1 != 0`. *Fix:* restrict the claim to the unconstrained
   case - "If moreover `C = R^n` and `f` is differentiable, then `x*` is a global minimiser iff
   `grad f(x*) = 0`" - and, if you want the constrained statement too, add the one-line
   first-order condition "on a general convex `C`, `x*` is optimal iff
   `grad f(x*)^T (x - x*) >= 0` for all `x in C` \cite[Section~4.2]{boyd2004convex}", which is
   also the geometry `\cref{fig:appB-lp}` shows for an LP. *Category:* A.

3. **`thm:appB-vertex` (Theorem B.28, line 803) - the "Otherwise" clause is false.** *Problem:*
   the sentence "Otherwise the LP is infeasible (`P = empty`) or unbounded" negates the
   *conjunction* "has an optimal solution **and** `P` has at least one vertex", so it asserts that
   an LP over a vertex-free polyhedron is infeasible or unbounded. Counterexample:
   `min z_1` subject to `-z_1 <= 0` in `R^2`; `P = {z_1 >= 0}` contains a line and therefore has
   no vertex, yet the optimum 0 is attained on a whole edge-free face. *Fix:* separate the
   trichotomy from the vertex statement, e.g. "Every LP either is infeasible (`P = empty`), or is
   unbounded (`c^T z -> -infinity` on `P`), or attains its optimum. In the last case, if `P` has
   at least one vertex - which holds in particular for the standard form with `z >= 0` - then some
   vertex of `P` is optimal." The citation `\textcite[Chapter~13]{nocedal2006numerical}` supports
   exactly this form. *Category:* A.

4. **`tab:appB-gaussian` (Table B.2, lines 587-604) is never referenced from the text.**
   *Problem:* `STYLE_GUIDE.md` section 3 requires every table to be referenced with `\cref`; a
   grep of the file finds `tab:appB-gaussian` only in its own `\label`. The reader meets a
   floating table on PDF page 37 with nothing pointing at it, while `tab:appB-identities` and
   `tab:appB-heap` are both introduced properly. *Fix:* add one sentence at the end of the
   paragraph that closes at line 568 (after "...the precisions of prior and measurement simply
   add."), for instance: "`\Cref{tab:appB-gaussian}` collects these identities in the form in
   which `\cref{ch:ch18,ch:ch19}` use them." *Category:* D.

5. **Citation locator in the proof of `thm:appB-affine` (line 506):
   `\cite[Chapter~4]{sarkka2013bayesian}`.** *Problem:* the sentence it supports is about the
   degenerate/characteristic-function cases of affine maps of Gaussians. In Sarkka's *Bayesian
   Filtering and Smoothing* (CUP 2013), Chapter 4 is "Bayesian filtering equations and exact
   solutions"; the Gaussian-distribution lemmas (joint, marginal, conditional, affine maps) are in
   the book's appendix on the properties of the Gaussian distribution. I cannot vouch for the
   chapter locator as given. *Fix:* drop the locator (`\cite{sarkka2013bayesian}`) as
   `STYLE_GUIDE.md` section 3 prescribes when a page or chapter number is not certain, or point to
   the Gaussian-distribution lemmas in that book's appendix once verified against a copy.
   *Category:* H.

## Suggestions

1. *Optional self-check items.* The spec does not ask for exercises and Appendix A set the
   precedent of not having them, but four or five one-line self-checks with answers given inline
   (verify `M^-1` in `eq:appB-block-inverse` by multiplication; derive the information form
   `(P^-1 + H^T R^-1 H)^-1` from `thm:appB-woodbury`; compute the 99 % gate for `n = 4`; find the
   Fiedler vector of a 5-cycle) would cost half a page and give the solitary reader something to
   do. If they are added, put the answers in the appendix itself, not in `appC-solutions.tex`,
   since the spec excludes solutions.
2. `thm:appB-gd` (Proposition B.31, line 923) assumes only differentiability but then writes
   strong convexity as `grad^2 f >= mu I`, which needs twice differentiability. Use the
   first-order form `f(y) >= f(x) + grad f(x)^T (y - x) + (mu/2)||y - x||^2`, or add "twice
   continuously differentiable" to the hypothesis.
3. `eq:appB-derivs` (line 363): `grad ||x - c|| = (x - c)/||x - c||` holds only for `x != c`. Add
   the proviso; it matters because the repulsive potential of `\cref{ch:ch15}` is evaluated at the
   obstacle boundary.
4. Symbol overloading. `\mat{L}` is the Cholesky factor in B.1/B.3 and the graph Laplacian in B.5;
   `\mat{A}` is a generic matrix, the double-integrator transition matrix in `eq:appB-AB` and the
   adjacency matrix in `def:appB-laplacian`. Both are consistent with
   `frontmatter/notation.tex`, so do not rename; add half a sentence at the start of B.5 ("in this
   section `A` is the adjacency matrix and `L` the Laplacian, not the Cholesky factor of B.1").
5. Line 662: "(`\cref{thm:appB-affine}` in reverse)" - drawing `x = mu + L xi` is a *direct*
   application of the affine theorem, not its reverse. Say "by `\cref{thm:appB-affine}` with
   `A = L`, `b = mu`".
6. Line 807: "the simplex method walks from vertex to adjacent vertex, improving the objective at
   every step" - degenerate pivots do not improve it. Write "never worsening the objective, and
   improving it away from degenerate pivots (an anti-cycling rule guarantees termination)".
7. Line 877: branch and bound terminates for bounded integer variables; add "with bounded integer
   variables" (or "over a bounded feasible region"), which is the case in `\cref{ch:ch22}`.
8. If the appendix must be pulled back towards the spec's 12-15 pages, the only text I would
   consider optional is the ADMM half-sentence at line 856, the free-variable-splitting detail in
   `def:appB-lp` and the last two sentences of the paragraph at lines 947-955. That saves well
   under a page and costs useful pointers; I recommend leaving all of it and letting the editors
   accept 20 pages for a reference appendix.
9. Line 1051 ends the shortest-path paragraph with a trailing space before the section break;
   harmless, but remove it while you are in the file.

## What must be kept

This is the strongest kind of refresher: exact, short, and always pointed at the chapter that
needs the result. Keep the four-move `keyidea` framing and the "read a section when a chapter
sends you here" opening - it makes the appendix usable as a lookup table instead of a course. Keep
every proof: the block-factorisation proof of `thm:appB-block` and the completing-the-square proof
of `thm:appB-conditioning` are the cleanest route to the Kalman update in the book, and deriving
Woodbury by inverting one bordered matrix two ways is elegant and correct. Keep the worked
examples exactly as they are - one covariance `[[2,1.2],[1.2,1]]` is reused for the
eigen-decomposition, the Schur complement, the Cholesky factor, the conditioning example and the
Monte Carlo check, and it matches the covariance-ellipse example of `\cref{ch:ch02}` number for
number - and keep `gen_appB_numbers.py`, whose asserts make that reuse verifiable. Keep the
branch-and-bound-by-hand example with its five nodes and its explicit remark that rounding the
relaxation gives an infeasible or suboptimal point, the three-step-size gradient-descent example
that pins down `alpha < 2/lambda_max`, and the four-drone Laplacian example with its Fiedler
vector and its post-cut spectrum. Keep all five figures: the conditioning figure has correctly
scaled densities (peak ratio 1.89, exactly the ratio of the true densities), the LP figure draws
the objective gradient inside the cone of the two active normals, and the gradient-descent figure
plots true level sets from generated data. Keep the three pitfalls - "do not form the inverse",
"check every Jacobian numerically" and "heap entries must be comparable" - which are the three
mistakes that actually cost readers days, and keep the `heapq`/`dict`/lazy-deletion paragraph,
which is the exact idiom the search chapters use.

## Response to review (round 1)

All five required changes are applied, plus six of the cheap suggestions. Only
`Overleaf/appendices/appB-math-refresher.tex` was touched; no numbers, figures, code or
`.dat` files changed, and nothing the reviewer asked to keep was removed. The build is
status 0 with no `!` errors and no undefined citations; the only overfull box (29.10 pt,
front-matter *List of Algorithms*) is the pre-existing one the review told me not to chase.
`python3 code/figures/gen_appB_numbers.py` still passes every assert in 0.03 s and
reproduces the `figures/data/appB-gradient-descent.dat` file byte for byte. The appendix
still occupies PDF pages 28-47 (20 pages), unchanged.

### Required changes

1. **`thm:appB-conditioning` non-degeneracy (A).** *Done.* The hypothesis of
   \cref{thm:appB-conditioning} now reads "jointly Gaussian with a non-singular
   covariance", and `eq:appB-joint` carries the condition explicitly:
   `\qquad \mat{\Sigma}_{ba} = \mat{\Sigma}_{ab}\T,\quad \mat{\Sigma} \succ \mat{0}.`
   (no overfull box). The false sentence before \cref{thm:appB-affine} is replaced by the
   reviewer's wording: "A singular $\Sigma \succeq 0$ has no density;
   \cref{thm:appB-affine} still holds for it, because a degenerate Gaussian is defined by
   its mean and covariance through its characteristic function, while the conditioning
   formula of \cref{thm:appB-conditioning} needs $\Sigma_{bb} \succ 0$ (or the
   Moore--Penrose pseudo-inverse $\Sigma_{bb}^{+}$ in place of $\Sigma_{bb}^{-1}$)."
   One consequential edit the review did not list: `thm:appB-linear-update`, which applies
   the conditioning theorem, now states `P > 0` and `R > 0` in its hypothesis (the joint
   covariance of $(x, z)$ is then $M\,\mathrm{diag}(P, R)\,M^\mathsf{T}$ with
   $M = [[I, 0],[H, I]]$ invertible, hence non-singular, so the corollary still follows).
   Nothing else downstream changed.

2. **`thm:appB-local-global` second sentence (A).** *Done, with the optional constrained
   condition.* The statement now reads "If moreover $\mathcal{C} = \R^n$ and $f$ is
   differentiable, then $x^*$ is a global minimiser iff $\nabla f(x^*) = 0$; on a general
   convex $\mathcal{C}$ the first-order condition is instead
   $\nabla f(x^*)\T(x - x^*) \ge 0$ for all $x \in \mathcal{C}$." The proof was extended
   accordingly (sufficiency from the tangent-plane inequality, necessity by moving along
   the segment towards $x$, cited to \cite[Section~4.2]{boyd2004convex}), it now says
   "an *unconstrained* minimiser has zero gradient", it states the reviewer's
   counterexample ($f(x) = x$ on $[0,1]$, $x^* = 0$, $\nabla f(x^*) = 1$), and it points at
   \cref{fig:appB-lp} as the picture of the constrained condition ($-c$ inside the cone of
   the active normals).

3. **`thm:appB-vertex` "Otherwise" clause (A).** *Done, in the reviewer's form.* The
   theorem now reads: "Every LP \cref{eq:appB-lp} either is infeasible ($P = \emptyset$),
   or is unbounded ($c\T z \to -\infty$ on $P$), or attains its optimum. In the last case,
   if $P$ has at least one vertex---which holds in particular for the standard form with
   $z \ge 0$---then some vertex of $P$ is optimal." The
   \textcite[Chapter~13]{nocedal2006numerical} pointer is unchanged.

4. **`tab:appB-gaussian` unreferenced (D).** *Done.* The paragraph that ends "...the
   precisions of prior and measurement simply add." now continues: "\Cref{tab:appB-gaussian}
   collects these identities in the form in which \cref{ch:ch18,ch:ch19} use them."

5. **Citation locator in the proof of `thm:appB-affine` (H).** *Done.*
   `\cite[Chapter~4]{sarkka2013bayesian}` is now `\cite{sarkka2013bayesian}`; I did not have
   a copy at hand to verify the appendix locator, so the locator is dropped as
   `STYLE_GUIDE.md` section 3 prescribes.

### Suggestions

* **Strong convexity in `thm:appB-gd`.** *Adopted:* the hypothesis is now the first-order
  form $f(y) \ge f(x) + \nabla f(x)\T(y - x) + (\mu/2)\norm{y - x}^2$, with
  "(equivalently $\nabla^2 f \succeq \mu I$ when $f$ is twice differentiable)".
* **`eq:appB-derivs` proviso.** *Adopted:* "The fourth expression holds only for
  $x \ne c$, because $\norm{x - c}$ is not differentiable at its own centre", and the
  sentence on the repulsive potential of \cref{ch:ch15} now ends "---a formula that the
  code must guard at zero clearance, where the gradient is undefined."
* **Symbol overloading.** *Adopted, without renaming:* B.5 opens with "Throughout this
  section $A$ is the adjacency matrix and $L$ the Laplacian of a graph, not the generic
  matrix of \cref{sec:appB-linalg} or the Cholesky factor of \cref{thm:appB-psd-tests}."
* **"\cref{thm:appB-affine} in reverse".** *Adopted:* now "(\cref{thm:appB-affine} with
  $A = L$ and $b = \mu$)".
* **Simplex and degenerate pivots.** *Adopted:* "never worsening the objective and
  improving it away from degenerate pivots, until no neighbour is better, which by
  convexity is a global optimum (an anti-cycling rule such as Bland's guarantees
  termination)".
* **Branch-and-bound termination.** *Adopted:* "The method terminates, for bounded integer
  variables, because every branch cuts away a slice...".
* **Trailing space at line 1051.** *Adopted:* removed.
* **Self-check items.** *Not adopted.* The spec says "No code/solutions" and does not ask
  for exercises, Appendix A set the precedent, and the appendix is already 5 pages over the
  spec's 12-15; adding half a page of exercises would push it further without a required
  need. The review does not list this as required.
* **Length trim (ADMM half-sentence, free-variable splitting, closing sentences of the
  gradient-descent paragraph).** *Not adopted*, as the reviewer recommends keeping all of
  it; the required changes added roughly fifteen lines and the appendix still ends on the
  same PDF page as before.

### Note on the build

While these edits were made, other agents were rebuilding `ch18` and `ch22`, which
truncates the shared `build/chapters/*.aux` files that `build.sh` `\@input`s; a build run
during that window reports `File ended while scanning use of \@newl@bel` for
`chapters/ch18-kalman-filter.aux`. The final run against complete `.aux` files exits 0 with
no errors, as recorded above.
