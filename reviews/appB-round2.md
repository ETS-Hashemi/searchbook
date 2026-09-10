# Review of Appendix B (Mathematical Refresher) - round 2

Reviewed: `Overleaf/appendices/appB-math-refresher.tex` (1184 lines), its five figure files in
`Overleaf/figures/appB/` (`convexity.tex`, `gaussian-conditioning.tex`, `gradient-descent.tex`,
`laplacian.tex`, `lp-geometry.tex`), the number/data generator
`Overleaf/code/figures/gen_appB_numbers.py`, and the glossary file
`Overleaf/appendices/glossary/appB-terms.tex` (12 items, all merged into
`Overleaf/appendices/glossary.tex` with `\cref{ch:appB}` back-pointers), against
`STYLE_GUIDE.md` section 9 (A-H), the spec `docs/specs/appB.md`, the training plan
`docs/core-idea.txt` and `reviews/appB-round1.md` with the reviser's response.

**Round-1 required changes: all five verified resolved, and resolved correctly.**

1. *(A) Non-degeneracy in `thm:appB-conditioning`.* Done. Line 524 now reads "jointly Gaussian
   with a non-singular covariance" and `eq:appB-joint` carries `\mat{\Sigma} \succ \mat{0}`
   (line 529); the false sentence is replaced by the correct one at lines 501-507. I also
   checked the consequential edit the reviser volunteered: `thm:appB-linear-update` now
   assumes `P > 0` and `R > 0` (line 562), and the parenthetical justification is right - the
   joint covariance of `(x, z)` is `M diag(P, R) M^T` with `M = [[I,0],[H,I]]` invertible,
   hence PD, so the corollary's appeal to the conditioning theorem is now legitimate.
2. *(A) `thm:appB-local-global`.* Done, in the stronger form: line 734 restricts the
   zero-gradient characterisation to `C = R^n` and adds the variational inequality
   `grad f(x*)^T (x - x*) >= 0` for a general convex `C`; the proof at line 737 proves both
   directions and states the `f(x) = x` on `[0,1]` counterexample.
3. *(A) `thm:appB-vertex`.* Done, in the reviewer's trichotomy form (line 814). The statement
   is now correct and matches `\textcite[Chapter~13]{nocedal2006numerical}`.
4. *(D) `tab:appB-gaussian` unreferenced.* Done: lines 577-578 introduce it, and the PDF now
   has all three tables referenced from the text.
5. *(H) Sarkka locator.* Done: line 514 is a bare `\cite{sarkka2013bayesian}`.

The seven adopted suggestions (first-order strong convexity in `thm:appB-gd`, the `x != c`
proviso on `grad ||x - c||`, the `A`/`L` disambiguation opening B.5, "`thm:appB-affine` with
`A = L`, `b = mu`", degenerate pivots and Bland's rule, "for bounded integer variables" in
branch and bound, the trailing space) are all in place and all correct as written.

**Build (G).** `./build.sh appB-math-refresher` exits 0, no `!` errors, **no undefined
citations**. The only overfull box in the whole run (29.10 pt, log line 1946) is in the
front-matter *List of Algorithms* (an RRT caption belonging to another chapter) - pre-existing,
not this appendix. The undefined references (`ch:ch11`, `ch:ch13`, `ch:ch14`) are cross-chapter
and permitted in a single-chapter build by `STYLE_GUIDE.md` section 7; all three target files
exist in `Overleaf/chapters/`. (The chapter *numbers* printed for the refs that do resolve -
"Chapter 6" for `ch:ch12`, "Chapters 10, 13 and 15" for `ch:ch18,ch:ch21,ch:ch23` - come from
stale shared `build/chapters/*.aux` files, not from this appendix; they will be right in the
full-book build.)

**Length (G).** PDF pages 29-48, i.e. **20 appendix pages** of a 51-page single-chapter PDF
(28 pages of front matter, then Bibliography and Index). That is exactly the ceiling the review
brief allows and 5 pages over the spec's 12-15. I re-read the whole appendix looking for
padding and found none: every subsection answers a "must cover" bullet of the spec, no example
is duplicated, no result is restated. **No cuts are required.**

**Code (A).** `python3 code/figures/gen_appB_numbers.py` runs in 0.02 s, every `assert` passes,
and it reproduces every number quoted in the text. I re-checked all of them against the run and
independently by hand: 2.8/0.2, `(3,2)/sqrt(13)`, 33.69 deg, 1.673/0.447, the Cholesky factor,
`Sigma^-1`, Schur complement 0.56, `A^T A`, `A^T b`, `(0.05, 0.95)`, residuals and 0.015, `H`
at `(3,4)`, `h = (5, 0.9273)`, `(4.9000, 0.8873)` vs `(4.9041, 0.8865)`, 0.205 m / 2.1 m/s,
`N(3.2, 0.56)`, `rho = 0.85`, `0.8695 +- 0.0034` vs `1 - e^-2 = 0.8647`, the six chi-square
gates, Bayes 1/3, LP vertices 0/8/9/6, multipliers `(1.5, 0.5)`, 10.5 at `(4.5, 0.5)`, the five
branch-and-bound nodes 21 / 20.67 / 18 / 19 / 20 with optimum `(4,0)`, the three gradient-descent
runs, and the Laplacian spectrum `(0,1,3,4)`, Fiedler vector `(-2,0,1,1)` and `(0,0,3,3)` after
the cut. Nothing in that list failed.

**Completeness (B).** Every numbered item of all six spec sections is present, including the
proof of the conditioning formula, LP standard form, big-M, branch and bound, the Laplacian
`lambda_2 > 0` argument and the `heapq`/`dict` note. Five figures (spec asks >= 4), three tables
(spec asks >= 3), 56 index entries with subentries, correctly bracketed by
`\index{mathematical refresher|(}` / `|)`. All ten citation keys resolve
(`references.bib`, `bib/ch19-extra.bib`, `bib/ch22-extra.bib`, `bib/ch23-extra.bib`); I can
vouch for all ten as real works with correct authors, titles, venues and years, and I checked
every locator this round - Boyd & Vandenberghe Appendix A (A.5.2 symmetric eigenvalue
decomposition), Appendix C (C.3.2 Cholesky), Sections 3.1, 4.2, Chapters 5 and 9;
Nocedal & Wright Chapters 3, 12, 13 and 17; CLRS Chapters 6 and 11. All are correct.

**Exercises (E).** As in round 1, I do *not* raise the absence of an exercise set: the spec for
this appendix prescribes sections, figures, tables, glossary and summary and says "No
code/solutions", `appC-solutions.tex` has no Appendix B block by design, and Appendix A set the
precedent. See Suggestion 1.

## Verdict

**Minor revision.** Two required changes, each a local edit of one clause or one sentence: one
false geometric claim about the feasible set of a mixed-integer program (A), and a
sign-convention contradiction between two passages of text and the LP figure they point at (C),
which was introduced by the round-1 fix to required change 2. Everything else in A-E is sound:
the mathematics is correct throughout, every proof I checked line by line holds, and every
quoted number is reproduced by the script.

## Required changes

1. **`sec:appB-milp`, lines 877-879 - "the feasible set is a scatter of points" is false for a
   *mixed*-integer program.** *Problem:* the sentence "A **mixed-integer linear program**
   (MILP) is an LP in which some variables are restricted to integers... The integrality
   constraint destroys convexity: the feasible set is a scatter of points, not a polyhedron"
   describes a pure integer program. When continuous variables remain - which is exactly the
   case in `\cref{ch:ch22}`, where the drone positions are continuous and only the big-M
   disjunction indicators are binary - the feasible set is a *union of polyhedra*, one full
   slice for each assignment of the integer variables, not a set of isolated points. A reader
   who takes the sentence at face value will expect `\cref{ch:ch22}` to discretise position.
   *Fix:* replace the clause with, e.g., "the feasible set is a union of polyhedral slices, one
   for every assignment of the integer variables - a scatter of isolated points only when
   *every* variable is integer - and in either case not convex". *Category:* A.

2. **Proof of `thm:appB-local-global` (line 737, last sentence) and `sec:appB-lp`
   (lines 806-810) - both send the reader to `\cref{fig:appB-lp}` with the opposite sign
   convention to the one the figure and `ex:appB-lp` use.** *Problem:* `def:appB-lp` is a
   *minimisation*, so the text correctly says "`-c` lies in the cone of the normals of the
   active constraints" (line 737) and "sliding a level line in the direction `-c` as far as `P`
   allows ends at a vertex" (line 809). But `ex:appB-lp` and `fig:appB-lp` are a
   *maximisation* of `2z_1 + 3z_2`: the figure draws `c = (2,3)` (not `-c`) inside the cone of
   `(1,1)` and `(1,3)`, its caption (line 838) says "Sliding a level line in the direction of
   `c` until it is about to leave `P`", and line 832 says "`c` lies in the cone spanned by the
   two active normals". A reader who follows either pointer sees the arrow pointing the
   opposite way from what the sentence just claimed. (This mismatch is new; it entered with the
   round-1 fix to item 2, whose suggested wording assumed the figure showed `-c`.) *Fix:* name
   the convention at both pointers. At line 737 write "...`\Cref{fig:appB-lp}` draws the
   constrained condition for a linear programme; that example *maximises*, so the arrow shown
   inside the cone of the active normals is `+c`, which is the same statement with the sign of
   the objective flipped." At lines 806-810 write "...sliding a level line in the direction
   `-c` as far as `P` allows ends at a vertex, or along a whole edge when the level lines are
   parallel to it (`\cref{fig:appB-lp}` maximises, so there the level line slides in the
   direction `+c`)." Leave the figure, its caption and `ex:appB-lp` exactly as they are - they
   are correct and mutually consistent. *Category:* C (with a knock-on effect in D).

## Suggestions

1. *Optional self-checks (repeat of round 1, still declined and still optional).* The spec asks
   for no exercises and the appendix is already at the 20-page ceiling, so this stays a
   suggestion: four or five one-line self-checks with answers inline (verify
   `eq:appB-block-inverse` by multiplication; derive `(P^-1 + H^T R^-1 H)^-1` from
   `thm:appB-woodbury`; compute the 99 % gate for `n = 4`; find the Fiedler vector of a
   5-cycle) would cost half a page and give the solitary reader something to do.
2. `ex:appB-jacobian`, line 404: "the linear prediction `h + H delta = (4.9000, 0.8873)`
   differs from the exact value `(4.9041, 0.8865)` by `(0.0041, -0.0008)`". Taken literally
   the difference is `(-0.0041, +0.0008)`; the printed pair is *exact minus linear*, which is
   what the script labels "linearisation error". Write "the exact value exceeds it by
   `(0.0041, -0.0008)`" or simply "differs from it in the fourth decimal".
3. `def:appB-bigO`, line 1077: the constants are quantified once, in the `O` clause, and then
   reused for `Omega` and `Theta`. `Theta` needs two constants. Write "...if there are
   constants `c_1, c_2 > 0` and `n_0` with `c_1 g(n) <= f(n) <= c_2 g(n)` for all `n >= n_0`",
   as `\cite[Chapter~3]{cormen2009clrs}` does.
4. Eigenvalue ordering flips between sections: `thm:appB-spectral` numbers
   `lambda_1 >= ... >= lambda_n` (so `lambda_2 = 0.2` is the *smallest* in `ex:appB-eigen`)
   while `thm:appB-laplacian` numbers `lambda_1 <= ... <= lambda_n` (so `lambda_2` is the
   algebraic connectivity). Both are the standard convention in their own field and both are
   stated locally, but since the appendix invites the reader to jump straight into a section,
   add half a sentence to B.5: "note that Laplacian eigenvalues are numbered in *increasing*
   order here, the reverse of `\cref{thm:appB-spectral}`".
5. Symbol overloading, same spirit as the `A`/`L` note the reviser added to B.5: `\vect{z}` is
   the decision variable of the LP/QP/MILP in B.4 while `\meas` (also a bold `z`) is the
   measurement vector in B.3. One clause at the start of B.4 ("in this section `z` is the vector
   of decision variables, not the measurement of `\cref{sec:appB-probability}`") removes the
   collision without renaming anything.
6. `thm:appB-vertex`, line 814: "Every LP `\cref{eq:appB-lp}` either is infeasible" renders as
   "Every LP Equation (B.31) either is infeasible", which reads awkwardly. Write "Every LP of
   the form `\cref{eq:appB-lp}`".
7. Summary bullet 6, line 1165: "gradient descent converges for `alpha < 2/lambda_max`" is the
   quadratic case; in general the condition is `alpha < 2/L` with `L` the Lipschitz constant of
   the gradient. Write "`alpha < 2/L` (that is `2/lambda_max` for a quadratic)".
8. `def:appB-lp`, line 801: `b` is the right-hand-side *vector* of `eq:appB-lp` and a *scalar*
   two lines later ("writing `a^T z = b` as two inequalities"). Use `beta`, as
   `eq:appB-bigM` already does.
9. `fig:appB-gd`: the pgfplots axis is 0.88\textwidth by 4 cm over ranges 11.4 by 5, so the
   level ellipses are drawn at roughly 7:1 rather than the true 10:1 (`sqrt(lambda_max/lambda_min)`
   is 3.16 in each semi-axis). Nothing is wrong, but raising `height` to about 5 cm would make
   the "narrow valley" of the caption look as narrow as the text says it is.

## What must be kept

This remains the strongest kind of refresher: exact, short, and always pointed at the chapter
that needs the result. Keep the four-move `keyidea` framing and the "read a section when a
chapter sends you here" opening, which make the appendix usable as a lookup table instead of a
course. Keep every proof - the block-factorisation proof of `thm:appB-block`, the
completing-the-square proof of `thm:appB-conditioning` (the cleanest route to the Kalman update
in the book), the derivation of Woodbury by inverting one bordered matrix two ways, the polar
integral in `thm:appB-chi2`, and the Laplacian null-space argument in `thm:appB-laplacian`(iii).
Keep in particular the three fixes made in round 1 in the exact form they now have: the
`Sigma > 0` hypothesis and its `P > 0`, `R > 0` knock-on in `thm:appB-linear-update`, the
two-case first-order condition in `thm:appB-local-global` with its `[0,1]` counterexample, and
the trichotomy in `thm:appB-vertex` - all three are now stated the way a careful text should
state them. Keep the worked examples exactly as they are: one covariance `[[2,1.2],[1.2,1]]`
carries the eigen-decomposition, the Schur complement, the Cholesky factor, the conditioning
example and the Monte Carlo check, and it matches the covariance-ellipse example of
`\cref{ch:ch02}` number for number; keep `gen_appB_numbers.py`, whose asserts make that reuse
verifiable, and keep the branch-and-bound-by-hand example with its five nodes and its explicit
remark that rounding the relaxation gives an infeasible or a suboptimal point. Keep all five
figures: the conditioning figure has correctly scaled densities (peak ratio 1.89, exactly the
ratio of the true densities) and a slice tangent to the 1-sigma ellipse; the LP figure draws the
objective gradient inside the cone of the two active normals; the gradient-descent figure plots
true level sets from generated data. Keep the three pitfalls - "do not form the inverse", "check
every Jacobian numerically" and "heap entries must be comparable" - and the
`heapq`/`dict`/lazy-deletion paragraph, which is the exact idiom the search chapters use.

## Response to review (round 2)

Both required changes are applied, plus seven of the nine suggestions. Nothing on the
"what must be kept" list was touched: all proofs, all five figures, all worked examples,
the three round-1 fixes, the three pitfalls, the `heapq`/`dict` paragraph, the four-move
`keyidea` framing and the opening are exactly as they were.

### Required changes

1. **`sec:appB-milp` - "a scatter of points" is false for a mixed-integer program.**
   Applied, in the reviewer's wording. The clause now reads: "The integrality constraint
   destroys convexity: the feasible set is a union of polyhedral slices, one for every
   assignment of the integer variables---a scatter of isolated points only when
   *every* variable is integer---and convex in neither case. The problem is NP-hard in
   general." (Only the trailing "and in either case not convex" was turned into "and convex
   in neither case. The problem is NP-hard in general." so that the sentence does not end
   with two coordinated clauses of opposite polarity.) The rest of the paragraph - LP
   relaxation, the bound direction, branch and bound - is unchanged.

2. **Sign convention at the two pointers to `fig:appB-lp`.** Applied at both places; the
   figure, its caption and `ex:appB-lp` were not touched.
   * Proof of `thm:appB-local-global`: "...`\Cref{fig:appB-lp}` draws the constrained
     condition for a linear programme: at the optimal vertex `-c` lies in the cone of the
     normals of the active constraints, so no feasible direction decreases the objective.
     That example *maximises*, so the arrow shown inside the cone of the active normals is
     `+c`, which is the same statement with the sign of the objective flipped."
   * `sec:appB-lp`: "...ends at a vertex, or along a whole edge when the level lines are
     parallel to it (`\cref{fig:appB-lp}` maximises, so there the level line slides in the
     direction `+c`)."

### Suggestions

1. *Self-checks.* Declined again, for the reason the reviewer gives: the spec says
   "No code/solutions" and the appendix is at the page ceiling.
2. *`ex:appB-jacobian` sign of the linearisation error.* Applied: "the linear prediction is
   `h + H delta = (4.9000, 0.8873)`, and the exact value `(4.9041, 0.8865)` exceeds it by
   `(0.0041, -0.0008)`". The numbers are untouched and still match the script.
3. *`def:appB-bigO`.* Applied: `Omega` now quantifies its own `c > 0`, `n_0`, and `Theta` is
   stated with `c_1, c_2 > 0` and `n_0` such that `c_1 g(n) <= f(n) <= c_2 g(n)`, as in CLRS.
4. *Eigenvalue ordering.* Applied: the disambiguation paragraph opening B.5 now ends
   "...and Laplacian eigenvalues are numbered in *increasing* order, the reverse of
   `\cref{thm:appB-spectral}`".
5. *`z` overloading.* Applied: B.4 now opens with "Throughout this section `z` is the vector
   of decision variables of a mathematical programme, not the measurement vector of
   `\cref{sec:appB-probability}`, which is written with the same bold letter." (Phrased
   without printing `\meas`, since it expands to the same glyph.)
6. *`thm:appB-vertex`.* Applied: "Every LP of the form `\cref{eq:appB-lp}`...".
7. *Summary bullet 6.* Applied: "gradient descent converges for `alpha < 2/L` with `L` the
   Lipschitz constant of the gradient (that is `2/lambda_max` for a quadratic)".
8. *Scalar `b` in `def:appB-lp`.* Applied: the scalar is now `beta`, matching `eq:appB-bigM`.
9. *`fig:appB-gd` aspect ratio.* Applied: `height` raised from 4.0 cm to 5.0 cm, which brings
   the drawn ellipses close to the true 10:1 ratio. Checked that this costs no page: the
   appendix body ends on the same folio with 4.0 cm and with 5.0 cm.

### Verification

* `./build.sh appB-math-refresher` exits **0**, no `!` errors, no undefined citations, no
  undefined reference inside the appendix. The single overfull box in the run (29.10 pt) is
  the pre-existing front-matter *List of Algorithms* entry belonging to another chapter.
  (One intermediate run reported status 12 from a truncated shared `build/*.aux`; deleting
  that stale file and rebuilding gives 0.)
* `python3 code/figures/gen_appB_numbers.py` runs in 0.02 s with every `assert` passing, and
  `figures/data/appB-gradient-descent.dat` was regenerated. No number in the text changed;
  the only numeric passage edited (suggestion 2) keeps the same four values and only says
  which of the two the difference points from.
* Length unchanged: no text was removed, and the additions come to about five printed lines.
