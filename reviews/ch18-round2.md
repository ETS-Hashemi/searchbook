# Review of Chapter 18 (The Kalman Filter) - round 2

Reviewed artefacts: `Overleaf/chapters/ch18-kalman-filter.tex` (1672 lines), the eight figure
files in `Overleaf/figures/ch18/`, `Overleaf/code/ch18_kalman.py`,
`Overleaf/code/figures/gen_ch18_tracking.py`,
`Overleaf/appendices/solutions/ch18-solutions.tex`,
`Overleaf/appendices/glossary/ch18-terms.tex`, `Overleaf/references.bib`,
`Overleaf/bib/ch18-extra.bib`, `Overleaf/frontmatter/notation.tex`, `docs/specs/ch18.md`,
`docs/core-idea.txt`, `STYLE_GUIDE.md` section 9, and `reviews/ch18-round1.md` with the
reviser's response.

Build: `cd Overleaf && ./build.sh ch18-kalman-filter` exits 0; no `!` error; no undefined
label, reference or citation belonging to this chapter (all `??` in the PDF are cross-chapter
refs, expected in a single-chapter build). The only overfull box above 15 pt (29.10 pt) is in
the front-matter list of algorithms and belongs to another chapter; the worst box inside the
chapter is 9.92 pt. `python3 code/ch18_kalman.py` prints `self-test passed in 2.97 s`;
`python3 code/figures/gen_ch18_tracking.py` regenerates all ten `.dat` files with no diff
(`git status` shows no ch18 data file modified).

Verification of round-1 items: **all six required changes are correctly resolved.** (1) The
NIS sentence in `sec:ch18-example` now reads "far below the expected $m=2$" with
$\Prob(\chi^2_{10}\le2.15)\approx0.005$ - I recomputed `chi2.cdf(2.152,10)=0.004963`, and the
five NIS values printed by `worked_example()` are 0.309, 0.273, 0.632, 0.662, 0.276 (mean
0.4304). (2) Experiment B now states the asymmetry the code produces (optimum 0.469 m at
$q=0.178$; 0.477 at 0.1, 0.503 at 1, 0.541 at 0.032), and the caption of
`fig:ch18-experiment` was corrected to match. (3) The prediction pitfall now quotes
$2\sigma=0.8$ m and 2.9 m, matching `gen_ch18_tracking.py` (0.393 and 1.456 m at one sigma)
and the caption's $0.79\times0.46$ m. (4) The complexity sentence now separates the short form
($\bigO{n^2m+m^3}$) from the Joseph form ($\bigO{n^3}$) of line `alg:ch18-kf:cov` and gives
"about two thousand floating-point operations"; my own count for $n=6,m=3$ is ~1400
multiplications, ~2800 flops, so the order of magnitude is right. (5) `sec:ch18-motivation`
now reads "The velocity obstacle of \cref{ch:ch12}, used by the local avoidance layer of
\cref{ch:ch13}". (6) DWA and RMSE are expanded at first use. None of these is re-raised.

Independent re-verification this round: every number in `tab:ch18-trace`, `tab:ch18-tuning`,
`tab:ch18-chi2`, the eight figure captions, `sec:ch18-experiment` and `sec:ch18-prediction` is
reproduced by the two scripts (I re-ran both and matched line by line: 1.175/0.524 m and
16.787/0.787 m/s in the motivation, N=198 with band [1.72, 2.28], mean NIS 2.208, per-horizon
sigmas 0.393/0.230, 0.842/0.635, 1.456/1.213, 2.188/1.912, the 17-point $q$ grid, and the
experiment-C row 1.243/1.889/0.921/3.60/0.25/0.26 etc.). I recomputed by hand or with a short
script: the step-1 hand computation ($a^-=2.0333$, $b^-=1.05$, $c^-=1.1$, $S=2.2833$,
$k_p=0.8905$, $k_v=0.4599$), the CV process-noise integral, the CA entries
$q\dt^5/20,\ q\dt^4/8,\ q\dt^3/6,\ q\dt^3/3,\ q\dt^2/2,\ q\dt$, the $F(\dt)^j=F(j\dt)$ and
$\mat{Q}$ semigroup identities, the DARE of `eq:ch18-riccati`, the two-point-initialisation
covariance and its $V\to\infty$ derivation in the solutions, the observability ranks (1, 3, 2)
and the CA determinant $\dt^3$, all 15 chi-square quantiles in `tab:ch18-chi2`, the NIS band
$m\pm1.96\sqrt{2m/N}$, $1-e^{-2}=86.47\%$ and $\sqrt{5.99}=2.447$, and the
$\alpha=k_p$, $\beta=k_v\dt$ identification of the alpha-beta filter. **Everything is
correct.** The listing is verbatim from `code/ch18_kalman.py` (28 lines), the five
`\SetKwFunction` macros are unique across the book, there are no duplicate labels, 31 index
entries (>= 15), 8 figures all `\cref`-referenced, 3 tables, 2 algorithms, 4 pitfall boxes, 9
exercises graded 1/1/2/2/2/2/3/3/3 including the Week-9 coding exercise, and the solutions
appendix now answers 8 of the 9. All seven citation keys resolve
(`kalman1960new`, `welch1995introduction`, `thrun2005probabilistic`,
`barshalom2001estimation`, `sarkka2013bayesian` in `references.bib`; `rauch1965maximum`,
`maybeck1979stochastic` in `bib/ch18-extra.bib`) and all seven are real references whose
authors, titles, venues and years I can vouch for. Every "must cover" item of `docs/specs/ch18.md`
and every Week-9 item of the training plan is present.

Length: the chapter occupies pages 25-49 of `build/only-ch18-kalman-filter.pdf`, i.e.
**25 pages** (spec target 15-17, style guide 12-18, review ceiling 24). This is one page above
the ceiling and is the only substantive point left, together with one garbled sentence.

## Verdict

**Minor revision.**

There is no remaining error of category A-B: no wrong formula, no unproved theorem, no number
the code fails to reproduce, no missing "must cover" item. Both required changes are local -
one sentence to rewrite (C) and about thirty lines of prose that restate captions, algorithm
comments and the trace table to delete (G). Nothing in the derivations, the code, the figures
or the exercises needs to be touched.

## Required changes

1. **Location:** `sec:ch18-models`, lines 331-333 ("Second, the off-diagonal term couples
   position and velocity ... a diagonal $\mat{Q}$ is a **common shortcut** and a mild error,
   $\mat{Q}=q\,\mat{I}$ regardless of $\dt$ a **common shortcut** and a serious one").
   **Problem (category C).** The phrase "a common shortcut and" appears twice in one sentence
   and the second clause has no verb, so the sentence reads as an editing artefact and the
   reader has to parse it twice to see that two *different* shortcuts of two *different*
   severities are being contrasted. This is the sentence that sets up the chapter's most
   emphasised pitfall (a $\mat{Q}$ that does not scale with $\dt$), so it must be unambiguous.
   **Fix.** Replace with, for example: "... moves both in the same direction. Dropping the
   off-diagonal term is a common shortcut and a mild error; using $\mat{Q}=q\,\mat{I}$
   regardless of $\dt$ is just as common and much worse (\cref{sec:ch18-implementation})."

2. **Location:** whole chapter; concretely lines 618-631, 737-741, 946-949, 1072-1076 and
   1294-1297.
   **Problem (category G).** The chapter is 25 typeset pages (pages 25-49 of the
   single-chapter PDF), one page over the 24-page ceiling and eight over the spec's 15-17.
   I confirm the round-1 finding that no section can be dropped without losing a "must cover"
   item, and I am *not* asking for content to be removed. What is left is prose that repeats
   information the reader already has on the same page, roughly one page of it:
   * lines 618-631: the walkthrough of `alg:ch18-track` restates, sentence by sentence, the
     end-of-line comments of the algorithm itself and the four subsections
     (`sec:ch18-gating`, `sec:ch18-missing`, `sec:ch18-init`, `sec:ch18-prediction`) that
     follow it. Keep the first sentence and the drop rule; delete the retelling of
     lines `init`, `predict`, `miss`, `nis`, `gate` and `deliver` (about 9 lines saved).
   * lines 946-949: "shows a drone that flies straight at $3$~m/s, turns by $90^\circ$ in four
     seconds and flies straight again, tracked from the same measurements
     ($\sigma_p=1$~m at $10$~Hz) with three values of $q$. The intermediate value is best
     overall and nearly as good as the small one on the straight legs" repeats the caption of
     `fig:ch18-tuning` and the header of `tab:ch18-tuning`. Start the paragraph at "The small
     value pays for its smoothness in the turn ..." and keep the $56\%$ / "doubles" numbers
     (about 4 lines saved).
   * lines 737-741: "after five position measurements it is $(1.135,0.630)$~m/s against the
     true $(1,0.5)$, an error of $0.18$~m/s inside the reported standard deviation
     $\sqrt{0.138}=0.37$~m/s, and the final position error $(0.32,0.23)$~m is inside
     $\sqrt{0.171}=0.41$~m as well" re-reads four numbers out of the last row of
     `tab:ch18-trace`. One clause ("the velocity estimate recovers from its wrong start, and
     both final errors fall inside the standard deviations the filter reports") does the same
     work (about 3 lines saved).
   * lines 1072-1076: "wide where the prediction is uncertain, narrow where it is precise, and
     growing after missed measurements, so that a track that has not seen its target for a
     while accepts measurements from a larger region" repeats `def:ch18-gate` and the caption
     of `fig:ch18-gating`; keep the price/benefit sentence (about 3 lines saved).
   * lines 1294-1297: the four extra grid points ($0.691$ m at $q=0.01$, $0.773$ m at $q=100$
     and the three velocity figures) are all readable off the right panel of
     `fig:ch18-experiment`; keep the raw-RMSE comparison and the asymmetry sentence, drop the
     enumeration (about 4 lines saved).
   **Fix.** Apply those five trims (or equivalent ones of your choosing that remove pure
   repetition), rebuild, and check that the chapter ends on page 48 or earlier, i.e. at most
   24 pages. Do **not** drop any figure, table, box, definition, proof, pitfall, exercise or
   spec item to make room; if the trims fall short of a page, say so in the response rather
   than cutting content.

## Suggestions

* **`fig:ch18-gating` (D).** Round 1 asked for the two normalised distances of $\meas^{(3)}$
  to be visible; the reviser declined in order not to disturb the geometry, which is fair.
  A cheap compromise that does not move anything: print the two numbers as a small annotation
  next to the crossing measurement ("$d^2=0.883\gamma$ to A, $0.898\gamma$ to B"), so the
  reader can see *why* the measurement is ambiguous instead of taking it on trust.
* **`sec:ch18-prediction`, pitfall box (C).** "$\mat{P}_k$ ... converges to a small steady
  value and never grows, however long you track" is contradicted three pages earlier by
  `sec:ch18-missing`, where $\mat{P}_k$ grows during predict-only steps. Add three words:
  "never grows *while measurements keep arriving*".
* **`sec:ch18-variants`, "Constant gain" (C).** "the same steady-state accuracy, but no
  transient and no covariance output" can be read as praise ("no transient" sounds good).
  Write "but no transient *phase of large gains*, so it converges slowly from a poor start,
  and no covariance output for the safety layer".
* **`alg:ch18-track`, line `alg:ch18-track:nis` (G).** The line computes $\vect{y}$ and
  $\mat{S}$, and `\KalmanUpdate` on line `alg:ch18-track:update` computes them again. A
  `\tcp*{reuse in \KalmanUpdate}` (as the implementation does) prevents a reader from
  concluding that the gate doubles the cost of an update.
* **Solutions (E).** 8 of 9 exercises are now covered; `exr:ch18-tuning` is the only one
  without even a hint, and it is the exercise that most needs one (part (c) asks the reader to
  compare CV and CA on the turning data). Two lines - where the minimum moves on a manoeuvring
  target, and that the CA model wins in the turn and loses on the straight legs - would close
  the set.
* **Notation table (F, front matter, not this chapter's file).** `frontmatter/notation.tex`
  attributes $\vect{w}_k,\vect{v}_k$ (line 159) and $\vect{y}_k,\mat{S}_k$ (line 160) to
  `\cref{ch:ch19}`, although both pairs are defined here in `eq:ch18-motion`,
  `eq:ch18-measurement`, `eq:ch18-innovation` and `eq:ch18-S`. Worth listing in the final
  report so the front-matter owner changes those two rows to `\cref{ch:ch18}`.
* **`thm:ch18-best-gain` (A, cosmetic).** The statement now carries the induction that closes
  the one-update-to-whole-recursion gap, which is what round 1 asked for; it currently uses
  two colons in one sentence. Splitting it into two sentences would make the induction easier
  to find.

## What must be kept

Everything round 1 listed under "must be kept" is intact and must stay: the two-Gaussian-facts
derivation strategy (predict = fact (i), update = fact (ii) on the joint `eq:ch18-joint`, the
same expansion re-used for the Joseph form and for `thm:ch18-best-gain`); the per-axis
reduction `eq:ch18-example-recursion` that makes the hand computation, the trace table and
`exr:ch18-hand` possible; the $k_v=b^-/S$ thread from `eq:ch18-predict-cv` through
`eq:ch18-gain-cv` to `sec:ch18-init` and the finite-differences pitfall; the whole
tuning-and-diagnostics apparatus (NIS band, whiteness, the demonstration in `tab:ch18-tuning`
that $q=100$ passes NIS and fails whiteness, and the closing observation of experiment B that
the NIS rule lands within a factor of two of the RMSE optimum); all four pitfall boxes; the
$\mat{F}/\mat{H}$ versus $\mat{A}/\mat{C}$ notebox, now including the $\vect{v}_k$ versus
$\vel$ warning; `sec:ch18-prediction` and `fig:ch18-prediction` with the $1-e^{-2}=86.5\%$
correction and $\kappa=\sqrt{5.99}$; and the code contract, which is the strongest in the book
so far.

Three things added or repaired in round 1 deserve to be protected explicitly, because they are
what a reader learning this material alone will most easily get wrong elsewhere: the corrected
NIS discussion of the worked example, which now teaches that five steps out of a pessimistic
$\mat{P}_0$ are *not* a consistency test; the asymmetric reading of the RMSE-versus-$q$ curve
in experiment B, with its explicit contrast to the turning target of `fig:ch18-tuning`; and the
single $2\sigma$ convention shared by the prediction pitfall, the paragraph before it and the
caption of `fig:ch18-prediction`. Also keep the two new solutions (`exr:ch18-scales`,
`exr:ch18-observability`) and the two coding hints - the $m=4$ NIS band with $\gamma=13.28$ and
the swap-rate hint - which are exactly the numbers a reader needs to know whether their own
implementation is working.

## Response to review (round 2)

Build after the revision: `cd Overleaf && ./build.sh ch18-kalman-filter` exits **0**, no `!`
error, no undefined label/reference/citation belonging to this chapter (the remaining `??` are
cross-chapter refs, expected in a single-chapter build). The worst overfull box inside the
chapter is unchanged at 9.92 pt; the only box above 15 pt (29.10 pt) is the front-matter list
of algorithms and belongs to another chapter. `python3 code/ch18_kalman.py` prints
`self-test passed in 3.26 s`. No code was touched, so no `.dat` file needed regenerating and
every number quoted in the chapter still comes from the two scripts.

**The chapter now occupies pages 25-48 of `build/only-ch18-kalman-filter.pdf`: 24 pages,
at the ceiling.**

### Required change 1 (C) --- the garbled $\mat{Q}$ sentence in `sec:ch18-models`

Applied, in the form the review proposed. The passage now reads: "... an unknown acceleration
moves both in the same direction. Dropping the off-diagonal term is a common shortcut and a
mild error; using $\mat{Q}=q\,\mat{I}$ regardless of $\dt$ is just as common and much worse
(\cref{sec:ch18-implementation})." Two shortcuts, two verbs, two severities, one forward
reference to the pitfall box.

### Required change 2 (G) --- one page of repeated prose

All five trims were applied as specified, and no figure, table, box, definition, proof,
pitfall, exercise or spec item was dropped.

* **`alg:ch18-track` walkthrough.** Reduced to the first sentence and the drop rule; the
  retelling of lines `init`, `predict`, `miss`, `nis`, `gate` and `deliver` is gone. The first
  sentence now points at the four subsections that fill those lines in
  (`\cref{sec:ch18-gating,sec:ch18-missing,sec:ch18-init,sec:ch18-prediction}`) instead of
  paraphrasing them.
* **Tuning paragraph.** Now starts "In \cref{fig:ch18-tuning} the small value pays for its
  smoothness in the turn ..."; the retelling of the caption and of the table header is gone,
  the $56\%$ and "doubles" numbers are kept.
* **Worked example.** The four-number recap is replaced by "The velocity estimate recovers
  from its wrong start, and both final errors fall inside the standard deviations the filter
  reports." The following sentence on $d^2_k$ and the whole corrected NIS discussion are
  untouched.
* **Gate paragraph.** The sentence restating `def:ch18-gate` and the caption of
  `fig:ch18-gating` is gone; the price/benefit sentence and the self-test outlier sentence are
  kept.
* **Experiment B.** The enumeration of grid points is gone. Kept: the optimum
  ($0.469$ m at $q=0.178$), the $0.477$/$0.503$/$0.541$ readings that carry the "under-sizing
  is punished sooner" asymmetry, the raw-RMSE comparison ("the position RMSE stays below the
  raw $1.126$~m over the whole grid"), the explanation of the velocity asymmetry --- now
  stated correctly as running *the other way* from the position asymmetry --- the contrast
  with the turning target of `fig:ch18-tuning`, and the NIS-rule closing observation.

Those five trims alone left the chapter at 25 pages with eleven lines spilling onto page 49,
so two further pieces of pure repetition were removed, in the spirit of the "or equivalent
ones of your choosing" clause:

* The third paragraph of `sec:ch18-motivation` was an almost verbatim preview of the drone box
  of `sec:ch18-drone` (same layers, same chapters, same Week-9 milestone sentence). It is now
  one sentence: the filter is the core of the prediction layer and the Week-9 topic, and
  `\cref{sec:ch18-drone}` sets out the interface. The DWA expansion that lived in the deleted
  sentence was moved to the drone box, which is now the first use of the abbreviation, so the
  round-1 "expand DWA at first use" item is preserved.
* The half-sentence of `sec:ch18-implementation` describing `KalmanFilter` as "a class that
  holds the model and the belief, with `predict` and `update` methods" duplicated the caption
  of `lst:ch18-core` directly above it. The rest of that paragraph, including the full
  self-test contract, is untouched.

### Suggestions

* **`fig:ch18-gating`.** Adopted. A two-line annotation `$d^2=0.883\gamma$ to A /
  $0.899\gamma$ to B` now sits just below $\meas^{(3)}$, on a light background, in the gap
  outside both ellipses; no marker, gate or arrow moved. The two values are the exact
  normalised distances of the drawn geometry (I recomputed them from the ellipse centres,
  rotations and semi-axes: $0.8830$ and $0.8992$; the review's $0.898$ for B is $0.899$ to
  three decimals). The page was rendered to check the annotation does not collide with
  anything.
* **Prediction pitfall.** Adopted: "$\mat{P}_k$ ... *while measurements keep arriving* it
  converges to a small steady value and never grows, however long you track", which removes
  the contradiction with `sec:ch18-missing`.
* **"Constant gain" variant.** Adopted verbatim: "but no transient phase of large gains, so it
  converges slowly from a poor start, and no covariance output for the safety layer".
* **`alg:ch18-track:nis`.** Adopted: the line now carries `\tcp*{reused in \KalmanUpdate}`.
  It does not overflow the algorithm box (the worst overfull in the chapter is unchanged).
* **Solutions.** Adopted: `exr:ch18-tuning` now has a hint covering where the minimum moves on
  a manoeuvring target, the reversed asymmetry of the curve, what the diagnostics select, and
  the CA-versus-CV trade (CA wins in the turn, loses on the straight legs, which is the
  argument for the IMM estimator). All 9 exercises are now answered or hinted. Verified by
  building `appC-solutions`: the new solution typesets with no error.
* **`thm:ch18-best-gain`.** Adopted: the two-colon sentence is split, so the induction now
  starts its own sentence ("The statement extends from one update to the whole recursion by
  induction over $k$, since ...").
* **Notation table (front matter, not this chapter's file).** Not actioned, as instructed:
  `frontmatter/notation.tex` lines 159-160 attribute $\vect{w}_k,\vect{v}_k$ and
  $\vect{y}_k,\mat{S}_k$ to `\cref{ch:ch19}`, although all four are defined in this chapter
  (`eq:ch18-motion`, `eq:ch18-measurement`, `eq:ch18-innovation`, `eq:ch18-S`). **The
  front-matter owner should change those two rows to `\cref{ch:ch18}`.** This is repeated in
  the final report.

### What was kept

Nothing on the "must be kept" list was touched. Specifically still present and unchanged: the
corrected NIS discussion of the worked example; the asymmetric reading of the RMSE-versus-$q$
curve of experiment B with its contrast to the turning target; the single $2\sigma$ convention
across the prediction pitfall, the paragraph before it and the caption of
`fig:ch18-prediction`; the split complexity claim after `alg:ch18-kf`; the
`ch:ch12`/`ch:ch13` velocity-obstacle attribution; the RMSE expansion at first use (and DWA,
now expanded at its new first use); the two-Gaussian-facts derivation strategy;
`eq:ch18-example-recursion` and the trace table; the $k_v=b^-/S$ thread; the whole
tuning-and-diagnostics apparatus; all four pitfall boxes; the $\mat{F}/\mat{H}$ notebox;
`sec:ch18-prediction` with $1-e^{-2}=86.5\%$ and $\kappa=\sqrt{5.99}$; the two round-1
solutions and the two coding hints; and the code contract. Figure, table, algorithm, listing,
pitfall, definition and exercise counts are unchanged (8/3/2/1/4/.../9), and all eight figures
are still `\cref`-referenced.
