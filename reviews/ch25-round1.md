# Review of Chapter 25 (Evaluating a Hybrid Planner) - round 1

Reviewed artefacts: `Overleaf/chapters/ch25-experiments.tex` (1501 lines), figures
`Overleaf/figures/ch25/{pipeline,intruders,boxplot,cactus,pareto,switches}.tex`, code
`Overleaf/code/ch25_evaluation.py` (956 lines) and `Overleaf/code/figures/gen_ch25_study.py`,
data `Overleaf/figures/data/ch25-study-*.dat`, solutions
`Overleaf/appendices/solutions/ch25-solutions.tex`, glossary `Overleaf/appendices/glossary.tex`,
bibliography `Overleaf/references.bib` and `Overleaf/bib/ch25-extra.bib`, against
`STYLE_GUIDE.md` section 9, `docs/specs/ch25.md` and `docs/core-idea.txt` (Week 12).

Build: `./build.sh ch25-experiments` returns 0, no `!` errors, no undefined reference or
citation belonging to this chapter (all `??` in the PDF are in the front matter and in the
preface, from chapters not built). The single overfull box > 15 pt is in the List of
Algorithms (an RRT entry from another chapter), not in this chapter. Chapter body =
PDF pages 27-49 = **23 pages**, inside the 24-page limit, so no cuts are required.

Code: `python3 code/ch25_evaluation.py` passes its self-test in 24 s (320-run mini-study
included). Re-running `code/figures/gen_ch25_study.py` reproduces
`ch25-study-box.dat` and `ch25-study-pareto.dat` byte for byte and every column of
`ch25-study-summary.dat` **except `comp_ms` and `comp_total_s`** (wall-clock timings). Every
non-timing number in Tables 25.3 and 25.4 and in section 25.7 was re-derived here and matches:
collision rates 0.85/0.75 and their Wilson limits [0.64,0.95]/[0.53,0.89]; medians and IQRs
1.10 (0.93-1.21), 1.65 (1.32-2.01), 1.12 (0.94-1.36), 1.02 (0.97-1.12), 1.73 (1.31-2.31),
1.04 (0.97-1.21); near-miss rates 0.40/0.45/0.45/0.45 and 0.10/0.15; every paired difference,
CI, `d_z` and better/worse/tie count, including the four `e_F` rows; the makespan intervals
[12.31,16.55] and [13.86,14.95]; seed 13 (turning, 465 Avoiding steps, `e_F^max` = 9.03 m,
33.7 s) and the hybrid's longest run 17.2 s; seed 8 of the four-drone cell (evasive,
`d_min` = 0.436 m for local and hybrid, 3.45 m for replan-only); the family breakdown 14/14,
14/14, 4/12; the correlation rho = 0.904 of the path ratios in the four-drone cell. The two
propositions were re-derived independently: `1 - 0.05^{1/20} = 0.1391`, Wilson`[0,0.1611]`,
`[0.0089,0.2361]`, `[0.6396,0.9476]`, and the paired-variance algebra of Proposition 25.1
is correct as stated. All sixteen citation keys resolve and all ten entries in
`bib/ch25-extra.bib` (Efron-Tibshirani 1993, Cohen 1988, Wilcoxon 1945 Biometrics Bulletin
1(6):80-83, Wilson 1927 JASA 22(158):209-212, Holm 1979 Scand. J. Statist. 6(2):65-70,
Hooker 1995 and Barr et al. 1995 J. Heuristics 1(1), Sturtevant 2012 IEEE TCIAIG 4(2):144-148,
Peng 2011 Science 334:1226-1227, McGeoch 2012 CUP) are bibliographically correct; nothing
looks fabricated. Index entries: 38 (>= 15). Figures: 6, all referenced. Exercises: 8, with
difficulties 1,2,2,2,1,2,3,3 and the Week-12 coding exercise present.

## Verdict

**Minor revision.** The chapter is complete against the specification and the training
plan, the mini-study is genuinely reproducible, and the prose is of publishable quality.
Six required changes remain; each is local (one statistical routine plus one table column,
and five sentences/captions). Nothing needs to be cut for length.

## Required changes

1. **`code/ch25_evaluation.py`, `wilcoxon_signed_rank()` (lines 710-730) and the `p` column
   of `tab:ch25-paired` (lines 844-868), plus section 25.6 list item 3 (lines 655-660).**
   *Problem:* the p-values printed as the last column of Table 25.4 come from a **normal
   approximation** to the signed-rank statistic, with no continuity correction and no tie
   correction of `sigma`, applied to samples as small as n = 7 non-zero differences (the
   `d_min` rows drop 13 ties). They are wrong by up to a factor of eight in the tail, and
   neither the chapter nor the caption says the test is approximate - a textbook that
   teaches statistical hygiene must not print an approximate p as if it were the test.
   *Fix:* compute the exact null distribution for `n <= 20` (a DP over the achievable rank
   sums, `poly = poly * (1 + x^{r_i})`, is ten lines and microseconds) and fall back to the
   normal approximation only above that; note the switch in the docstring and in list item 3
   ("for the small n of a seed study, use the exact distribution; the normal approximation
   needs n >~ 25"). Then replace the `p` column of Table 25.4 with the exact values
   (hybrid minus local-only, cells k=2/k=4): rho_L 0.042/0.009; d_min 0.016/0.078;
   n_rp 0.0001/0.0001; e_F 0.025/0.0001. Hybrid minus replan-only: rho_L 0.452/0.006;
   d_min 0.0003/0.0001; n_rp <0.0001/<0.0001; e_F 0.114/0.0001. Note that the `d_min`,
   k = 4 row moves from 0.063 to 0.078 and the `n_rp` rows from 0.001 to 0.0001, so the
   sentence "the paired differences ... with intervals far from zero" (line 896) still holds.
   *Category:* A.

2. **`ex:ch25-study`, line 800: "every number below is printed by the self-test of the
   file".** *Problem:* the claim does not hold. `python3 code/ch25_evaluation.py` prints the
   per-cell summary and the paired rows for `path_ratio`, `dmin_di`, `makespan` and
   `replans` only; the four `e_F` rows of Table 25.4, the intruder-family breakdown
   (14/14, 14/14, 4/12) and the LaTeX rows of Table 25.3 are printed by
   `code/figures/gen_ch25_study.py`, and the per-seed facts of section 25.7 (seed 13's 465
   Avoiding steps and 9 m peak, seed 8's 0.436 m, the single 69-step communication
   violation, rho = 0.90) are recoverable only from `figures/data/ch25-study-runs.dat`.
   *Fix:* replace the sentence by "every number below is produced by the code: the summary
   rows and the paired comparisons by `code/figures/gen_ch25_study.py` (whose output is the
   LaTeX of Tables 25.3 and 25.4), the metric definitions and the determinism of the runner
   by the self-test of `ch25_evaluation.py`, and the per-seed facts of the discussion by the
   raw rows in `figures/data/ch25-study-runs.dat`" - or, better, move the `ef_mean` paired
   loop and the family breakdown into the `__main__` block of `ch25_evaluation.py` so that
   the self-test really does print them. *Category:* A.

3. **`tab:ch25-results` caption (lines 805-812), line 797 ("The 320 runs take 21 s") and the
   "Effort and constraints" paragraph (lines 918-921).** *Problem:* the `bar c` column and
   the two wall-clock statements are the only numbers in the chapter that a reader cannot
   reproduce: on a second machine the same code and seeds give 0.085 ms (none), 0.101 ms
   (replan), 0.175-0.219 ms (local and hybrid) and 23-24 s for the study, i.e. the
   four-drone reactive entries printed as 0.167/0.168 come out 30 % higher, while every
   other column of `ch25-study-summary.dat` reproduces bit for bit. As written, a reader who
   re-runs the code concludes that the table is stale. *Fix:* add one sentence to the caption
   of Table 25.3 - "the `bar c` column is wall-clock time on one machine (see the pitfall on
   page ...); it is the only column that will differ when you re-run the study, and only its
   ordering is meaningful" - write "about 20 s on the author's machine" at line 797, and in
   the "Effort and constraints" paragraph state the ordering and the ratio ("a reactive step
   costs about twice a replanning step and twice a pure prediction step") before the absolute
   milliseconds. *Category:* A.

4. **Pitfall "Collision rate without minimum separation", lines 277-278.** *Problem:* "A
   collision rate of 0/20 says that the true rate is below about 16 % (`\cref{thm:ch25-three}`)"
   attributes the number to the wrong result: Proposition 25.2 (rule of three) gives
   `1 - 0.05^{1/20} = 0.139`, i.e. about 14 %; 16 % is the Wilson upper limit of
   `eq:ch25-wilson`, as the chapter itself says correctly on line 585. *Fix:* write "below
   about 14 % (`\cref{thm:ch25-three}`; the Wilson interval of `\cref{eq:ch25-wilson}` gives
   16 %)". *Category:* A.

5. **Section 25.7, "Effort and constraints", lines 924-928.** *Problem:* "the means of 3.5
   and 1.6 steps each come from a single run: a mean of a quantity that is zero in 19 of 20
   runs should be reported as '1 of 20 runs, for 69 steps' instead" gives one step count for
   two different runs. The code shows one replan-only run with **69** violating steps
   (3.45 x 20 = 69) and one hybrid run with **32** (1.6 x 20 = 32). *Fix:* "... should be
   reported as '1 of 20 runs, for 69 steps' for replan-only and '1 of 20 runs, for 32 steps'
   for the hybrid instead". *Category:* A.

6. **`exr:ch25-pairing` part (c), lines 1438-1440, and its solution in
   `appendices/solutions/ch25-solutions.tex` (block `exr:ch25-pairing`).** *Problem:* part (c)
   asks the reader to compute the two-sided sign-test p-value for 16 of 20 and "compare with
   `\cref{tab:ch25-paired}`", and the solution asserts that the resulting 0.0118 "is the
   0.012 printed for rho_L of hybrid against replan-only with four drones". Table 25.4 prints
   no sign-test p: that row shows 0.008, the Wilcoxon value (0.0064 once change 1 is applied).
   The exercise is therefore not solvable against the chapter as printed, and the solution
   points at a number the reader cannot find. *Fix:* add a `p_sign` column to Table 25.4 (the
   code already returns it: 0.012 for that row), or - cheaper - reword (c) as "compute the
   two-sided sign-test p-value exactly and explain why it is larger than the Wilcoxon
   p-value that `\cref{tab:ch25-paired}` reports for the same row", and adjust the solution to
   name 0.0118 against the table's Wilcoxon value and to say that the sign test discards the
   sizes of the differences. *Category:* E.

## Suggestions

* `fig:ch25-plots`, the outer float that carries the cactus and Pareto subfigures, is never
  referenced (only its two subfigures are). Add one `\cref{fig:ch25-plots}` in section 25.6
  or drop the outer label.
* `figures/ch25/cactus.tex` fixes `xmin=15, xmax=210`, which are the author's machine's
  milliseconds; a reader who regenerates `ch25-study-cactus.dat` on faster or slower hardware
  gets curves partly off the axis. Either delete the two limits and use
  `enlargelimits=0.05`, or plot the effort normalised by the no-avoidance median, which also
  makes the plot machine-independent and reinforces the chapter's own advice.
* Line 792: "97 candidate velocities". `safe_velocity()` evaluates 98 - the 97 of `_CAND`
  (the zero velocity plus 4 speeds x 24 headings) and the preferred velocity appended to
  them. Write "97 sampled velocities plus the preferred one".
* The closest-approach formula on lines 125-129 divides by `||w||^2`; add the degenerate case
  in half a sentence ("if `w = 0` the two agents move identically over the interval and the
  minimum is `||r_0||`"). Exercise 25.2 actually hits this case on the drone-drone pair, and
  the code handles it, so the reader should not have to guess.
* Only four of the eight exercises have solutions (25.2-25.5). This matches chapters 22-24,
  but `exr:ch25-matrix` and `exr:ch25-cactus` have crisp answers that a self-study reader
  cannot check: 576 x 3 = 1728 full-factorial cells and 14 + 3 - 1 = 16 one-factor-at-a-time
  cells for 25.1; success rates 10/10 and 8/10, means over finished runs 30.8 ms and 9.0 ms,
  PAR-2 scores 30.8 ms and 47.2 ms for 25.6 (and, for part (d), a 200 ms cap changes only B's
  PAR-2, to 87.2 ms if the two runs still fail, which is the point of the question).
* Table 25.2 folds two binary constraint choices into one four-level factor, and the
  strategy factor is counted as three levels with "none" outside the design; both are what
  make `3 x 4 x 4 x 3 x 4 = 576`. One clause in the caption saying so would stop a reader
  from arriving at 4 x 4 x 4 x 4 x 2.
* If space is ever needed elsewhere in the book, `tab:ch25-template` overlaps
  `tab:ch25-metrics` in its middle rows and could lose two lines; this is not a length
  problem in this chapter, which is inside its budget.

## What must be kept

The chapter is the strongest kind of methodology chapter: it teaches by doing, and almost
everything it claims can be re-run. Keep the four-family taxonomy of the ten metrics and
`tab:ch25-metrics` with its "sensitive to" column - that column is the most useful single
page in the chapter. Keep Proposition 25.1 with its proof and the rho = 0.90 illustration,
and Proposition 25.2 used immediately to defuse "0/20 collisions"; both are exactly the
right level of formality for a methodology chapter. Keep the aimed-intruder generator with
its three families and the honest observation that the evasive family often misses. Keep the
mini-study in full, and above all its six-point cautious interpretation - the admissions
that the hybrid does *not* improve `d_min` over local-only because its local phase *is*
local-only, that replan-only's separation advantage comes from a 2 m parameter rather than a
principle, and that none of the numbers transfers to a physics simulator - which is a model
of how to report one's own results. Keep all five pitfall boxes, the reproducibility habits
and the results-table template, the checklist-restated-as-questions table, the simulator
interface sketch with the "three things change" paragraph, and the exercise set, in
particular the hand-computable log of Exercise 25.2 (which the self-test asserts) and the
flawed-table critique of Exercise 25.3.

## Response to review (round 1)

All six required changes are applied, plus six of the seven suggestions. The chapter
builds with status 0, no errors, no undefined in-chapter references and no overfull box
over 15 pt; `python3 code/ch25_evaluation.py` passes its self-test (320-run mini-study,
21.7 s here) and `code/figures/gen_ch25_study.py` still reproduces every `.dat` column
except the wall-clock ones. Nothing from the "what must be kept" list was removed.

**Required 1 - approximate Wilcoxon p-values.** `wilcoxon_signed_rank()` in
`code/ch25_evaluation.py` now enumerates the exact null distribution for
`n <= EXACT_MAX_N = 20`: the ranks are doubled so that average ranks stay integral, and
the coefficients of `prod_i (1 + x^{r_i})` are accumulated by the ten-line DP the review
describes; the two-sided p is `2 min(P(W+ <= w), P(W+ >= w))`. Above n = 20 the normal
approximation takes over, now *with* a continuity correction and with sigma corrected for
ties. The docstring says all of this, the returned dict carries an `exact` flag, and
`_selftest_statistics()` asserts three new cases (six positive differences give exactly
2/2^6 = 0.03125; a tied sample gives W+ = 7.0 through half-integer ranks; n = 25 falls
through to the approximation). The `p` column of Table 25.4 was replaced with the exact
values, which reproduce the reviewer's list exactly: hybrid minus local-only 0.042/0.009,
0.016/0.078, 0.0001/0.0001, 0.025/0.0001; hybrid minus replan-only 0.452/0.006,
0.0003/0.0001, <0.0001/<0.0001, 0.114/0.0001. Section 25.6 item 3 now tells the reader to
compute both p-values from the exact distribution, states that the normal approximation
needs N of about 25 and is wrong by a factor of several in the tail below that, and names
the generating polynomial and the function. The caption of Table 25.4 says both p-values
are exact and why that matters (7 non-zero differences in the d_min rows against
local-only). The prose at line 896 was checked and still holds.

**Required 2 - "printed by the self-test".** Both halves of the fix were done. The
`__main__` block of `ch25_evaluation.py` now includes `ef_mean` in the paired loop (so the
four e_F rows of Table 25.4 are printed by the self-test), prints the p-values with four
decimals, and prints the intruder-family breakdown (14/14, 14/14, 4/12). The sentence in
`ex:ch25-study` was replaced by one naming all three sources: the summary rows and paired
comparisons (as LaTeX) from `gen_ch25_study.py`, the metric definitions and the
determinism of the runner from the self-test of `ch25_evaluation.py` (which also prints
the per-cell summary, the paired rows and the family breakdown), and the per-seed facts
from `ch25-study-runs.dat`.

**Required 3 - machine-dependent numbers.** The caption of Table 25.3 now ends: "The
`bar c` column is wall-clock time on one machine; it is the only column that will differ
when you re-run the study, and only its ordering is meaningful." Line 797 reads "about
20 s on the author's machine". The "Effort and constraints" paragraph now gives the
ordering and the ratio first (a reactive step costs about twice a replanning step and
about twice a pure prediction-and-tracking step, because the velocity sampling runs at
every Avoiding step), then the absolute 0.16-0.17 / 0.09 / 0.08 ms with "on yours all
three will move together". The `.dat` files were regenerated to confirm that only the
timing columns move, and then restored to the author's machine's version so that the
printed table, the prose and the cactus figure stay consistent with each other.

**Required 4 - rule of three vs Wilson.** The pitfall now reads "below about 14 %
(\cref{thm:ch25-three}; the Wilson interval of \cref{eq:ch25-wilson} gives 16 %)".

**Required 5 - two different runs.** Now "should be reported as '1 of 20 runs, for 69
steps' for replan-only and '1 of 20 runs, for 32 steps' for the hybrid instead".

**Required 6 - Exercise 25.4(c).** The first (better) option was taken: Table 25.4 has a
new `p_sign` column, filled from `paired_compare`'s exact sign test (0.424, 0.180, 0.016,
0.453, 0.0001, 0.0001, 0.057, 0.0001; 0.115, 0.012, 0.003, 0.003, <0.0001, <0.0001, 0.263,
0.003), and the caption announces both tests. Part (c) now asks the reader to compute the
exact sign-test p, find the row of the table it belongs to, and explain why that row's
Wilcoxon p is smaller. The solution names the 0.012 in the `p_sign` column of the
rho_L / hybrid-minus-replan / k = 4 row (16 / 4 / 0), contrasts it with the Wilcoxon 0.006,
and explains that the sign test discards the sizes: the four scenarios the hybrid lost it
lost by 0.022 on average against the 0.042 of the sixteen it won. The table survives the
extra column with no overfull box.

**Suggestions.** Adopted: (i) `\cref{fig:ch25-plots}` is now used at the end of the Pareto
paragraph; (ii) `figures/ch25/cactus.tex` drops `xmin/xmax` for `enlargelimits=0.05`, and
the N = 80 line is drawn relative to the axis (with `\addlegendimage`) so it follows the
data on any machine - the current data span 20-209 ms and still fill the axis; (iii) "97
sampled velocities plus the preferred one"; (iv) the degenerate case w = 0 of the
closest-approach formula is stated in half a sentence, with a pointer to
\cref{exr:ch25-metrics-log}, which hits it; (v) solutions were added for
`exr:ch25-matrix` (design, plus 576 x 3 = 1728 full-factorial cells and 14 + 3 - 1 = 16
one-factor-at-a-time cells) and `exr:ch25-cactus` (10/10 and 8/10, 30.8 ms and 9.0 ms,
PAR-2 30.8 and 47.2 ms, and 87.2 ms for B under a 200 ms cap), so six of the eight
exercises now have solutions; (vi) the caption of Table 25.2 explains that the count
3 x 4 x 4 x 3 x 4 = 576 reads the two binary constraint choices as one four-level factor
and keeps "no avoidance" outside the design. Not adopted: trimming `tab:ch25-template`,
since the chapter is inside its page budget and the review asks for the template to be
kept.

**Side effect.** The listing `lst:ch25-paired` was updated in the two lines where
`paired_compare()` changed, so the printed code still matches the file. The chapter body
grew from 23 to 24 PDF pages, which is the budget.
