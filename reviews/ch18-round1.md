# Review of Chapter 18 (The Kalman Filter) - round 1

Reviewed artefacts: `Overleaf/chapters/ch18-kalman-filter.tex` (1650 lines), the eight figure
files in `Overleaf/figures/ch18/`, `Overleaf/code/ch18_kalman.py` (574 lines),
`Overleaf/code/figures/gen_ch18_tracking.py` (261 lines),
`Overleaf/appendices/solutions/ch18-solutions.tex`, `Overleaf/appendices/glossary/ch18-terms.tex`,
`Overleaf/bib/ch18-extra.bib`, `Overleaf/frontmatter/notation.tex`, `docs/specs/ch18.md`,
`docs/core-idea.txt`, `STYLE_GUIDE.md` section 9.

Build: `./build.sh ch18-kalman-filter` returns status 0, no `!` errors, no undefined label,
reference or citation belonging to this chapter (all `??` are cross-chapter refs, expected in a
single-chapter build). No overfull box of this chapter exceeds 15 pt (worst inside the chapter:
9.92 pt at lines 1000-1004, the NEES list item; two 5.40 pt boxes belong to figure floats).
`python3 code/ch18_kalman.py` passes its self-test in 3.17 s;
`python3 code/figures/gen_ch18_tracking.py` regenerates all six `.dat` files.
Chapter length: pages 25-48 of `build/only-ch18-kalman-filter.pdf` = **24 pages**, i.e. at the
budget ceiling (spec target 15-17, style guide 12-18) - see Suggestions; I do **not** require cuts,
because essentially every section maps onto a "must cover" item of `docs/specs/ch18.md`.

## Verdict

**Minor revision.**

This is a strong, technically sound chapter. I verified every formula against the canonical
sources (Kalman 1960; Bar-Shalom, Li & Kirubarajan 2001; Thrun, Burgard & Fox 2005 ch. 3; Welch &
Bishop TR 95-041; Sarkka 2013) and recomputed the worked example, the chi-square table, the
process-noise integrals for the CV and CA models, the observability ranks, the NIS band and the
$1-e^{-2}$ ellipse probability: all correct. Every number in the worked-example trace table, in
`tab:ch18-tuning`, in the figure captions and in the experiment section is reproduced exactly by
the two scripts. All seven citation keys resolve (five in `references.bib`, `rauch1965maximum` and
`maybeck1979stochastic` in `bib/ch18-extra.bib`) and all seven references are real and correctly
described. Every "must cover" item of the spec and the Week-9 items of the training plan are
present.

What blocks acceptance is a small set of *local* factual slips: two statistical/numerical claims
that the code does not support (items 1 and 2), one figure of merit quoted at the wrong sigma
level (item 3), and a complexity claim that contradicts the algorithm the chapter itself
prescribes (item 4), plus two consistency items (5 and 6). Each is a one- to three-sentence edit;
none touches the structure, the derivations or the code.

## Required changes

1. **Location:** `sec:ch18-example`, paragraph after `tab:ch18-trace` ("And the last column lists
   $d^2_k=\dots$"), line ~700: *"the five values average $0.43$, unremarkable for five samples"*.
   **Problem (category A).** This is statistically false and the chapter's own data show it. The
   five NIS values are $0.309, 0.273, 0.632, 0.662, 0.276$, summing to $2.152$; for a correctly
   tuned filter their sum is $\chi^2_{10}$, and $\Prob(\chi^2_{10}\le 2.152)=0.005$. A mean NIS of
   $0.43$ against an expectation of $2$ is therefore *remarkable*, not unremarkable; it happens
   because the example deliberately starts from $\mat{P}_0=\mat{I}$, which is far larger than the
   actual initial error, so $\mat{S}_k$ overstates the innovation spread throughout the transient.
   Leaving the sentence as it stands teaches the reader the wrong calibration for the test that
   `sec:ch18-diagnostics` then asks them to apply.
   **Fix.** Replace the clause with something like: "the five values average $0.43$, far below the
   expected $m=2$ -- for a correctly initialised filter a sum this small would have probability
   $\Prob(\chi^2_{10}\le2.15)\approx0.005$. The cause is the deliberately pessimistic
   $\mat{P}_0=\mat{I}$: while the filter is still shedding that excess covariance, $\mat{S}_k$ is
   larger than the innovations warrant. This is why the NIS test of \cref{sec:ch18-diagnostics} is
   run over long records and after the transient, not over five steps."

2. **Location:** `sec:ch18-experiment`, experiment B paragraph, line ~1300: *"it is $0.477$~m at
   $q=0.1$ and $0.503$~m at $q=1$, so a factor of five either way costs less than $8\%$"*.
   **Problem (category A).** The conclusion is not what the code produces. The optimum is
   $0.469$~m at $q=0.178$; the two quoted points are a factor $1.8$ *below* and $5.6$ *above* it
   ($+1.7\%$ and $+7.2\%$). A genuine factor of five below the optimum is $q\approx0.036$, where
   the printed grid gives $0.541$~m at $q=0.032$, i.e. $+15.4\%$ -- roughly twice the claimed
   bound. Measured from the true $q=0.2$ instead of the optimum the statement is still wrong
   ($q=0.04$ costs about $11\%$).
   **Fix.** State the asymmetry the data show: "so a factor of two below or five above the optimum
   costs less than $8\%$, while a factor of five below already costs $15\%$ ($0.541$~m at
   $q=0.032$): under-sizing $q$ is punished sooner than over-sizing it on this straight-flying
   target." (Note this is the opposite asymmetry from the turning target of `fig:ch18-tuning`,
   which the following sentences already discuss, so the contrast is worth one clause.)

3. **Location:** `sec:ch18-prediction`, `pitfall` box "Confusing the estimation covariance with the
   prediction covariance", line ~1240: *"inflates the radius by the current $2\sigma$ of $0.4$~m
   when the collision is two seconds away and the honest figure is $1.5$~m"*.
   **Problem (category A).** The two numbers are quoted at different sigma levels, and one of them
   is mislabelled. `gen_ch18_tracking.py` gives, for experiment A at $t=10$~s,
   $\sigma_x=0.393$~m now and $\sigma_x=1.456$~m at a $2$~s horizon, so $0.4$ and $1.5$ are the
   *one*-sigma figures; the $2\sigma$ figures are $0.79$~m and $2.9$~m. As written the box
   understates the honest inflation by a factor of two, in the very box that warns against
   over-confidence, and it contradicts the caption of `fig:ch18-prediction`, which reports $2\sigma$
   semi-axes of $0.79\times0.46$~m.
   **Fix.** Use one convention consistently: "...inflates the radius by the current $2\sigma$ of
   $0.8$~m when the collision is two seconds away and the honest figure is $2.9$~m..." (or keep
   $0.4$/$1.5$ and write $\sigma$ instead of $2\sigma$).

4. **Location:** `sec:ch18-pseudocode`, last paragraph after `alg:ch18-kf`, line ~600: *"A predict
   step costs $\bigO{n^3}$ and an update $\bigO{n^2m+m^3}$; for the CV model in 3D, $n=6$ and
   $m=3$, a few hundred floating-point operations"*.
   **Problem (category A).** (i) The $\bigO{n^2m+m^3}$ bound holds for the short-form update
   $\mat{P}=\mat{P}^--\Kgain(\mat{H}\mat{P}^-)$, but line~\ref{alg:ch18-kf:cov} of the very
   algorithm being annotated prescribes the Joseph form, which multiplies the $n\times n$ matrix
   $(\mat{I}-\Kgain\mat{H})$ by $\mat{P}^-$ and again by $(\mat{I}-\Kgain\mat{H})\T$ and therefore
   costs $\bigO{n^3}$. (ii) The flop count is off by about an order of magnitude: for $n=6$, $m=3$
   the predict step alone needs $\approx 2n^3=432$ multiplications and the Joseph update
   $\approx 700$, i.e. about $1100$ multiplications and some $2200$ flops per cycle.
   **Fix.** "A predict step costs $\bigO{n^3}$; an update costs $\bigO{n^2m+m^3}$ in the short form
   and $\bigO{n^3}$ in the Joseph form of line~\ref{alg:ch18-kf:cov}. For the CV model in 3D,
   $n=6$ and $m=3$, that is about two thousand floating-point operations per cycle, so a filter
   runs at kilohertz rates on a flight computer."

5. **Location:** `sec:ch18-motivation`, first paragraph, line ~31: *"The local avoidance layer of
   \cref{ch:ch13} needs the intruder's \emph{velocity} to build a velocity obstacle"*.
   **Problem (category F).** The velocity obstacle is defined in \cref{ch:ch12}
   (`ch12-velocity-obstacles.tex`); \cref{ch:ch13} is RVO/ORCA. The chapter itself points to
   \cref{ch:ch12} for "the velocity-obstacle construction" in `exr:ch18-coding`, so the two
   references disagree.
   **Fix.** Write "\cref{ch:ch12,ch:ch13}" (or "the velocity obstacle of \cref{ch:ch12}, used by
   the local avoidance layer of \cref{ch:ch13}").

6. **Location:** first uses of two acronyms: **DWA** in `sec:ch18-motivation`, third paragraph
   ("(\orca or DWA, \cref{ch:ch13,ch:ch14})", line ~55) and **RMSE** in the header of
   `tab:ch18-tuning` and its caption (`sec:ch18-qr`, line ~960).
   **Problem (category F).** STYLE_GUIDE section 3 requires every acronym to be defined at first
   use *in every chapter*. "root mean square" appears in `sec:ch18-motivation` but never as the
   expansion of RMSE, and DWA is never expanded here.
   **Fix.** "(\orca or the dynamic window approach, DWA, \cref{ch:ch13,ch:ch14})" and, at the first
   occurrence of the abbreviation, "root-mean-square error (RMSE)" -- e.g. in
   `sec:ch18-motivation`: "from $1.18$~m to $0.52$~m (root-mean-square error, RMSE)".

## Suggestions

* **Length (category G, not required).** At 24 pages the chapter is at the ceiling and above the
  spec's 15-17. I found no section that could be dropped without losing a "must cover" item, but
  roughly half a page of genuine duplication could go: (a) the RMSE figures $1.18\to0.52$~m and
  $16.8\to0.79$~m are given in `sec:ch18-motivation` and repeated verbatim in
  `sec:ch18-experiment` -- the second occurrence can be a cross-reference; (b) the four
  per-horizon standard deviations in the paragraph after `fig:ch18-prediction` repeat the caption
  of that figure -- keep one of the two; (c) the last two sentences of `sec:ch18-gain`
  ("One feature of the matrix gain has no scalar analogue ...") overlap the closing sentences of
  `sec:ch18-predict` about the position-velocity coupling.
* **Lemma `thm:ch18-gaussian-facts`, fact (i).** It is applied in `sec:ch18-update` to the stacked
  vector $(\state_k,\meas_k)$, whose additive noise $(\vect{0},\vect{v}_k)$ has a *singular*
  covariance. Add "($\mat{Q}$ may be singular)" to the statement so the step is airtight for a
  reader checking it line by line.
* **`thm:ch18-best-gain`, closing sentence.** The proposition proves optimality over gains of one
  update; the sentence "the recursion is the best linear unbiased estimator for any noise with the
  given second moments" extends this to the whole recursion. One clause ("by induction over $k$,
  since the prediction of the next step is a linear function of the previous estimate") would close
  the gap; the citation to `kalman1960new` that follows is otherwise carrying the claim alone.
* **`sec:ch18-properties`, "Complexity and memory".** "it is the batch least-squares fit to all
  measurements so far, reorganised so that each measurement is absorbed once and forgotten" is a
  nice remark but is asserted; add a pointer (Sarkka 2013, ch. 4, or the information form of
  `sec:ch18-variants`, where the equivalence is visible).
* **`fig:ch18-gating`.** Measurement $\meas^{(3)}$ falls inside both gates at normalised distances
  $0.883\gamma$ (track A) and $0.898\gamma$ (track B) -- correct as annotated, but the reader
  cannot see the difference. Either move $\meas^{(3)}$ a little towards A or annotate the two
  $d^2$ values in the figure.
* **Solutions coverage.** `appendices/solutions/ch18-solutions.tex` answers 4 of the 9 exercises
  (`hand`, `gain`, `q`, `init`). Appendix C is explicitly "selected exercises", so this is legal,
  but `exr:ch18-observability` and `exr:ch18-scales` are both cheap to answer and would help a
  reader working alone; ch04 supplies all ten. A two-line hint for each of the two coding exercises
  (expected swap rate, expected NIS with $m=4$) would also be welcome.
* **Notation collision.** $\vect{v}_k$ (measurement noise) and $\vel=\vect{v}$ (velocity) are both
  bold $v$ and both appear on the same page (e.g. `def:ch18-cv` and `eq:ch18-measurement`). The
  front-matter table sanctions both, but one sentence in the existing `notebox` ("$\vect{v}_k$ with
  a time index is the measurement noise; $\vel$ without one is the velocity block of the state")
  would remove a real stumbling block.
* **`sec:ch18-gating`.** The text motivates the gate with "an outlier $40$~m from the predicted
  position" and then reports the self-test's "$50$-metre outlier". Using the same number in both
  places costs nothing and reads better.

## What must be kept

The derivation strategy is the best thing here and should not be touched: two clearly stated
Gaussian facts, predict as fact (i), update as fact (ii) applied to the joint distribution
`eq:ch18-joint`, and then the same expansion re-used to prove the Joseph form, to prove that the
Kalman gain is the best gain (`thm:ch18-best-gain`), and to explain what goes wrong for a
suboptimal gain. That economy is exactly what a graduate student reading alone needs, and it is
rare in textbook treatments of this material.

Keep the per-axis reduction of the worked example (`eq:ch18-example-recursion`): decoupling the 4D
filter into two identical 2D recursions is what makes the by-hand step-1 computation, the trace
table and `exr:ch18-hand` possible, and every digit of it is reproduced by `worked_example()`.
Keep the interpretation of $k_v=b^-/S$ as the mechanism by which a position-only sensor produces a
velocity estimate, and its link back to the $\dt^2c$ coupling created in `eq:ch18-predict-cv` --
this is the chapter's central pedagogical thread and it pays off again in `sec:ch18-init` and in
the "finite differences as velocity measurements" pitfall.

Keep the whole tuning-and-diagnostics apparatus: the NIS band, the whiteness test, the worked
demonstration in `tab:ch18-tuning` that $q=100$ passes NIS and fails whiteness, and the closing
observation in experiment B that choosing $q$ where the mean NIS equals $m$ lands within a factor
of two of the RMSE optimum without ever seeing the truth. Keep all four pitfall boxes and the
`notebox` on $\mat{F}/\mat{H}$ versus $\mat{A}/\mat{C}$; keep `sec:ch18-prediction` and
`fig:ch18-prediction` intact, including the $1-e^{-2}=86.5\%$ correction and $\kappa=\sqrt{5.99}$,
which is precisely the interface \cref{ch:ch24} and \cref{ch:ch13} need. Finally, keep the code
contract: `ch18_kalman.py` and `gen_ch18_tracking.py` back every quoted number, the self-test
checks the process-noise integrals, the $\mat{Q}(j\dt)$ semigroup identity, the Joseph-versus-short
form definiteness counterexample, gating, misses, observability, NEES over 300 Monte-Carlo runs and
the worked example to four decimals. That is the standard the rest of the book should meet.
