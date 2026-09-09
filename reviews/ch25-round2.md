# Review of Chapter 25 (Evaluating a Hybrid Planner) - round 2

Reviewed artefacts: `Overleaf/chapters/ch25-experiments.tex` (1536 lines), the six figure
files `Overleaf/figures/ch25/{pipeline,intruders,boxplot,cactus,pareto,switches}.tex`, the
code `Overleaf/code/ch25_evaluation.py` (1003 lines) and `Overleaf/code/figures/gen_ch25_study.py`,
the data `Overleaf/figures/data/ch25-study-{runs,summary,box,cactus,pareto}.dat`, the
solutions `Overleaf/appendices/solutions/ch25-solutions.tex`, `Overleaf/appendices/glossary.tex`,
`Overleaf/references.bib` and `Overleaf/bib/ch25-extra.bib`, against `STYLE_GUIDE.md`
section 9, `docs/specs/ch25.md` and `docs/core-idea.txt` (Week 12, "Experiments to run",
"Metrics", the completion checklist).

**Build.** `./build.sh ch25-experiments` produces the PDF with **no `!` errors, no undefined
citation, and no undefined reference belonging to this chapter**; the only overfull box
over 15 pt (29.1 pt) is in the List of Algorithms and comes from an RRT entry of another
chapter. The build script returns 12; the cause is visible in
`build/only-ch25-experiments.latexmk.log` ("Latex failed to resolve 40 reference(s)"), and
all 40 are cross-chapter (`ch:ch11`, `ch:ch13`, `ch:ch14`, `ch:ch19`, `ch:ch20`, `ch:ch21`)
in the front matter and preface plus four in the chapter body (`ch:ch20` three times,
`ch:ch21` once), which section 7 of the style guide explicitly allows in a single-chapter
build. So the non-zero status is not a defect of this chapter (it is not the
"shared-build-directory race" the round-1 response diagnosed, but the conclusion is the
same: nothing to fix here). Chapter body = PDF pages 27-50 = **24 pages**, at the limit and
inside it; nothing in the chapter is padding, so **no cuts are required**.

**Code.** `python3 code/ch25_evaluation.py` passes its self-test (320-run mini-study,
26.1 s here). Every non-timing number of Tables 12.3/25.3 and 12.4/25.4 was reproduced from
that run: the four cell blocks of the results table (13.38/25.24, 13.23/48.05, 1.030-1.081,
1.10/1.65/1.12, 1.02/1.73/1.04, 4.15/7.45/0.85/1.50, 0.029-1.477, 3.5/1.6, collision rates
0.85/0.75/0.05 and their Wilson limits) and all sixteen paired rows including the eight
`p_W` and eight `p_sign` values (0.0419, 0.0085, 0.0156, 0.0781, 0.0001, 0.0001, 0.0245,
0.0001; 0.4524, 0.0064, 0.0003, 0.0001, <0.0001, <0.0001, 0.1140, 0.0001, and the sign-test
column 0.424/0.180/0.016/0.453/0.0001/0.0001/0.057/0.0001, 0.115/0.012/0.003/0.003/
<0.0001/<0.0001/0.263/0.003). The family breakdown 14/14, 14/14, 4/12 is printed by the
self-test as required in round 1. Both propositions were re-derived independently
($1-0.05^{1/20}=0.13911$; Wilson $[0,0.1611]$, $[0.0089,0.2361]$, $[0.6396,0.9476]$;
Wilson at $N=10$: $0.2775$ and $1-0.05^{1/10}=0.2589$), as were the answers of
Exercises 25.4(a) ($N_u=200$), 25.4(c) ($2\cdot 6196/2^{20}=0.01182$), 25.5 ($N=597.6\to598$,
$4\times20=80$, $20(0.026/0.005)^2=541$) and 25.6 (30.8/9.0 ms, PAR-2 30.8/47.2, 87.2 ms
under a 200 ms cap). The exact signed-rank implementation is correct: doubled average ranks,
$\prod_i (1+x^{r_i})$ by DP, two-sided $p = 2\min(P(W^+\le w), P(W^+\ge w))$, normal
approximation with continuity and tie correction above $n=20$.

**Round-1 items.** All six required changes of round 1 are resolved: (1) exact Wilcoxon in
`wilcoxon_signed_rank()` with the promised `p` column and the rewritten list item 3 and
caption; (2) the "printed by the self-test" sentence in `ex:ch25-study` now names the three
sources, and the `__main__` block really does print `ef_mean` and the family breakdown;
(3) the caption disclaimer for $\bar c$, "about 20 s on the author's machine" and the
ordering-first rewrite of "Effort and constraints"; (4) "about 14 % (`thm:ch25-three`; the
Wilson interval gives 16 %)"; (5) "1 of 20 runs, for 69 steps" / "for 32 steps"; (6) the new
`p_sign` column plus the reworded Exercise 25.4(c) and its matching solution. Six of the
seven suggestions were adopted as described. None of these is re-raised below.

**Other checks.** Index entries 38 (>= 15); figures 6, all referenced, `fig:ch25-plots`
now referenced too, all using the shared `sb*` styles; tables 7; one algorithm with a
line-by-line walkthrough; five pitfall boxes; exercises 8 with difficulties 1,2,2,2,1,2,3,3
and the Week-12 coding exercise present, six of them with solutions; all 16 citation keys
resolve (10 in `bib/ch25-extra.bib`, 6 in `references.bib`), and the ten extra entries
(Efron-Tibshirani 1993; Cohen 1988 2nd ed.; Wilcoxon 1945 *Biometrics Bulletin* 1(6):80-83;
Wilson 1927 *JASA* 22(158):209-212; Holm 1979 *Scand. J. Statist.* 6(2):65-70; Hooker 1995
and Barr et al. 1995 *J. Heuristics* 1(1):33-42 and 9-32; Sturtevant 2012 *IEEE TCIAIG*
4(2):144-148; Peng 2011 *Science* 334(6060):1226-1227; McGeoch 2012 CUP) are
bibliographically correct; none looks fabricated. Every "must cover" item of
`docs/specs/ch25.md` is present, and the notation ($\makespan$, $\sumcost$, $\dt$, $\ttc$,
$\tau_h$, $\lambda_2$, $\pos_i$) agrees with `frontmatter/notation.tex` and with
`ch24-hybrid-architecture.tex` (which fixes $\tau_h = \ttc = 3$ s).

## Verdict

**Minor revision.** The chapter is complete, accurate and reproducible, and the round-1
changes were all made correctly. Five required changes remain, and every one of them is
local: one table column plus three sentences, two lines of statistics code, two lines of a
listing and one caption clause. Nothing needs to be cut for length.

## Required changes

1. **`tab:ch25-results` $\bar c$ column (lines 844-859, ninth data column), the
   "Effort and constraints" paragraph (lines 949-953) and the implementation note at
   line 1294 - against the committed `figures/data/ch25-study-summary.dat`.**
   *Problem:* the printed $\bar c$ values are from a different run of the study than the
   data files that ship with the book and that `fig:ch25-cactus` plots. The committed
   `ch25-study-summary.dat` gives `comp_ms` = 0.0743-0.0752 ($k=2$, $m=0$), 0.0820 (none),
   0.1631 (local), 0.0964 (replan), 0.1597 (hybrid) for $k=2, m=1$; 0.0814-0.0830
   ($k=4$, $m=0$), 0.0837 (none), **0.2106** (local), 0.0972 (replan), **0.2113** (hybrid)
   for $k=4, m=1$, against the table's 0.077 / 0.079, 0.166, 0.095, 0.156 / 0.077 / 0.082,
   **0.167**, 0.094, **0.168**. The four-drone reactive entries are therefore 26 % below the
   shipped data (my own run reproduces the shipped data: 0.219 and 0.222 ms), and
   `ch25-study-cactus.dat`, from which the cactus panel is drawn, spans 20-209 ms, i.e. the
   same second machine. Two captions each say "one machine" while describing two. The prose
   at lines 951-953 ("those steps are $0.16$--$0.17$~ms, $0.09$~ms and $0.08$~ms") has the
   same problem, and line 1294 ("$320$ runs in about $21$~s") is an unqualified wall-clock
   number that does not reproduce (24.6 s here) in the one place where `ex:ch25-study`
   (line 815) already says "on the author's machine".
   *Fix:* make table, figure, prose and `.dat` come from one run. Cheapest: rerun
   `code/figures/gen_ch25_study.py` and copy the regenerated `comp_ms` column into the
   $\bar c$ column of `tab:ch25-results` (0.075, 0.082, 0.163, 0.096, 0.160, 0.082, 0.084,
   0.211, 0.097, 0.211 for the ten rows as ordered above); rewrite lines 951-953 as "on the
   machine that produced the table those steps are $0.16$~ms with two drones and $0.21$~ms
   with four, against $0.10$~ms for a replanning step and $0.08$~ms for prediction and
   tracking alone; on yours all three will move together" (the ordering and the "about
   twice" ratio both survive); and at line 1294 write "about $25$~s on that machine".
   *Category:* A.

2. **Section 25.7, "Efficiency", line 934: "Makespans differ by less than a second on
   average."** *Problem:* the chapter's own `tab:ch25-results` contradicts this in the
   four-drone cell, where the mean makespans are 13.4 s (local-only) and 14.7 s
   (replan-only), a difference of 1.3 s. The statement is true only of the hybrid's paired
   differences against each baseline ($-0.03$, $+0.76$, $-0.35$, $-0.51$ s from
   `paired_table`).
   *Fix:* replace by "The mean makespans of the three avoidance strategies lie within
   $1.3$~s of each other (local-only $13.4$~s against replan-only $14.7$~s with four
   drones), and the hybrid is within $0.8$~s of either baseline in every cell."
   *Category:* A.

3. **`code/ch25_evaluation.py`, `paired_compare()` (lines 774-788) and
   `wilcoxon_signed_rank()` (lines 713-761), exercised by the paired loop of the
   `__main__` block (lines 990-996).** *Problem:* when a metric is undefined for a cell the
   metric functions return `nan` (as `sec:ch25-implementation` says they should), but
   `paired_compare()` does not drop them: `nan != 0` keeps them in the signed-rank sample,
   `w_plus` comes out 0 and the exact branch returns $p = 2/2^{20} = 1.9\cdot10^{-6}$,
   printed as `p_wilcoxon 0.0000`, with `d_z +inf` and counts `0/0/0`, for the four
   `dmin_di` comparisons of the $m=0$ cells; two NumPy `RuntimeWarning`s
   ("Mean of empty slice", "invalid value encountered in scalar divide") are printed as
   well. A chapter whose subject is statistical hygiene must not have its own self-test
   print a highly significant $p$ for a comparison with no data.
   *Fix:* in `paired_compare()`, after `d = np.asarray(a, float) - np.asarray(b, float)`,
   add `d = d[np.isfinite(d)]` and return `{"n": 0, "mean_diff": nan, ..., "p_wilcoxon": 1.0,
   "p_sign": 1.0}` when `d.size == 0` (guard `dz` the same way); optionally skip the $m=0$
   cells for `dmin_di` in the printing loop so the self-test output shows the four real
   rows. Keep `lst:ch25-paired` in step with the edited function (see change 4).
   *Category:* A.

4. **`lst:ch25-paired`, lines 1283-1284.** *Problem:* the listing is not verbatim from the
   file, contrary to section 6 of the style guide (and to the round-1 response, which said
   it was): the chapter prints
   `w = wilcoxon_signed_rank(d)      # exact null distribution for n <= 20` and
   `out["p_wilcoxon"], out["p_exact"] = w["p"], w["exact"]`, whereas
   `code/ch25_evaluation.py` has `w = wilcoxon_signed_rank(d)` with no comment followed by
   two separate assignments. The other two listings are verbatim (`lst:ch25-simulator` is
   declared a sketch).
   *Fix:* put the comment and the merged assignment into `paired_compare()` in the `.py`
   file (both are valid Python and keep the excerpt short), or restore the file's four-line
   form in the listing. Whichever is chosen, re-check the excerpt after change 3.
   *Category:* G.

5. **`tab:ch25-results` caption, lines 826-839.** *Problem:* the caption does not say over
   which runs the means are taken, and the answer contradicts the rule the chapter itself
   states in `sec:ch25-statistics` ("averages every finished-run metric ... over the
   successful runs only"): `summarise()` averages `path_ratio`, `makespan`, `soc`,
   `replans`, `ef_mean` and `comm_viol` over **all** 20 runs of a row, so the
   no-avoidance rows report $\rho_L = 0.999$ and a makespan of 13.4 s over the 17 (resp. 15)
   runs that ended in a collision as well.
   *Fix:* add one clause to the caption: "Means are over all $20$ runs of a row, collisions
   included: in the toy a collision does not stop a run and every drone reaches its goal, so
   there is nothing to censor; the rule of \cref{sec:ch25-statistics} to average over
   successful runs only applies as soon as a run can fail to finish." *Category:* C.

## Suggestions

* `sec:ch25-implementation` speaks of "the six pitfalls of this chapter" and lists six, but
  there are five pitfall boxes (means-without-spread and hidden-failures share one).
  Either split that box or write "the six pitfalls collected in the five boxes above".
* Table 25.3 would carry its own message better with a $c_{99}$ column next to $\bar c$:
  `def:ch25-effort` introduces the 99th percentile as "the deadline behaviour",
  `tab:ch25-template` demands it, and `summarise()` already computes `comp_max_ms`; the
  reader never sees one in a real table.
* Exercise 25.7(a) asks for $k=8$ and $m=2$, which the mini-study never exercises. One
  sentence with the expected cost ("$3\times3\times3\times4\times20$ runs is roughly ten
  times the mini-study, a few minutes") would tell a self-study reader whether to start it.
* The prose at line 815 says the study takes "about 20 s" and line 1294 "about 21 s" for the
  same 320 runs; after change 1 make the two agree.
* `figures/data/ch25-study-runs.dat` is named in `ex:ch25-study` as the source of the
  per-seed facts. A one-line header comment in it naming the generating script and the git
  commit (as `sec:ch25-reproducibility` item 4 tells the reader to do) would make the
  chapter practise its own habit.
* Solutions still exist for six of the eight exercises; a two-line answer sketch for
  `exr:ch25-simulator` (what tracking lag does to $d_{\min}$, and that the margin needed is
  roughly the lag times the closing speed) would close the set for a reader working alone.

## What must be kept

Everything the round-1 review asked to keep is still here and still deserves it: the
four-family taxonomy of the ten metrics and the "sensitive to" column of
`tab:ch25-metrics`, Proposition 25.1 with its proof and the $\rho = 0.90$ illustration,
Proposition 25.2 used immediately to defuse "0/20 collisions", the aimed-intruder generator
with its three families and the honest admission that the evasive family often misses, the
whole mini-study and above all its six-point cautious interpretation, the five pitfall
boxes, the reproducibility habits, the results-table template, the checklist-as-questions
table, the simulator interface sketch with its "three things change" paragraph, and the
exercise set, in particular the hand-computable log of Exercise 25.2 and the flawed-table
critique of Exercise 25.3. Add to that list the work done in this round: the exact
signed-rank test with its generating-polynomial DP and its `exact` flag is now the
statistically correct thing to teach, and the two-column presentation of $p_W$ next to
$p_{\mathrm{sign}}$ in `tab:ch25-paired` - with Exercise 25.4(c) asking the reader to
compute one of them and explain why the other is smaller - is a better piece of teaching
than either column alone. Keep the caption sentence that marks $\bar c$ as the only
machine-dependent column; it is exactly the right kind of warning, and change 1 only asks
that the column it warns about be the one the shipped data produce.

## Response to review (round 2)

All five required changes are applied. Everything the "What must be kept" paragraph names is
untouched: the metric taxonomy and `tab:ch25-metrics`, both propositions with their proofs and
illustrations, the aimed-intruder generator with its three families, the mini-study and its
six-point cautious interpretation, the five pitfall boxes, the reproducibility habits and the
results-table template, the checklist-as-questions table, the simulator sketch, the exercise
set, the exact signed-rank test with its DP and `exact` flag, and the $p_W$/$p_{\mathrm{sign}}$
pair in `tab:ch25-paired` (all sixteen paired rows reproduce unchanged, verified against the
self-test output). The caption sentence that marks the timing column as the only
machine-dependent one is kept and now also covers $c_{99}$.

**1. One run behind table, figure, prose and `.dat` (A).** Done, by making the chapter follow
the shipped data rather than by regenerating it: regenerating on this machine would have
produced a third set of timings (my run gives 0.222 and 0.228 ms for the four-drone reactive
cells) and would have desynchronised `ch25-study-cactus.dat` from the reviewer's reference
numbers, so the committed `.dat` files are left exactly as they are and the chapter was moved
onto them. The $\bar c$ column of `tab:ch25-results` is now 0.075, 0.082, 0.163, 0.096, 0.160,
0.082, 0.084, 0.211, 0.097, 0.211 (the ten rows in table order), which is the per-cell mean of
`comp_mean_ms` in `figures/data/ch25-study-runs.dat` rounded to three decimals, and agrees with
`ch25-study-summary.dat` row by row. The prose of "Effort and constraints" now reads "on the
machine that produced the table those steps are $0.16$~ms with two drones and $0.21$~ms with
four, against $0.10$~ms for a replanning step and $0.08$~ms for prediction and tracking alone;
on yours all three will move together"; the preceding ordering sentence and its "about twice"
are unchanged and still hold (0.16/0.10 = 1.6, 0.21/0.10 = 2.2, 0.16/0.08 = 2.0). The
implementation note now says "$320$ runs in about $25$~s on that machine" and `ex:ch25-study`
"about $25$~s on the author's machine", so the two agree (suggestion 4); 25 s is also what this
machine reports (`mini-study: 320 runs in 25.2 s`). One further number was stale for the same
reason: the "comparing computation times across machines" pitfall said "a decision that takes
$0.17$~ms"; it now says $0.16$~ms, which is a number the table contains.

**2. The makespan claim (A).** "Makespans differ by less than a second on average." is replaced
by the reviewer's sentence: "The mean makespans of the three avoidance strategies lie within
$1.3$~s of each other (local-only $13.4$~s against replan-only $14.7$~s with four drones), and
the hybrid is within $0.8$~s of either baseline in every cell." (Paired differences $-0.03$,
$+0.76$, $-0.35$, $-0.51$ s, from the self-test.)

**3. `paired_compare()` and undefined metrics (A).** `paired_compare()` now does
`d = d[np.isfinite(d)]` immediately after forming the differences and returns
`{"n": 0, "mean_diff": nan, ..., "p_wilcoxon": 1.0, "p_exact": True, "p_sign": 1.0}` when
nothing is left, so `mean_ci()`, `d_z` and both tests are only ever reached with a non-empty
sample; the docstring says why. The `__main__` printing loop skips comparisons with `n == 0`,
so the self-test now prints the four real `dmin_di` rows and no `p_wilcoxon 0.0000` with
`d_z +inf` and `0/0/0` counts, and the two NumPy `RuntimeWarning`s are gone (`grep -ci warning`
on the output: 0). All other printed rows are bit-for-bit what they were. The reason for the
drop is also stated in the chapter, in the paragraph that introduces `lst:ch25-paired`.

**4. `lst:ch25-paired` verbatim (G).** The listing body is now copied out of
`code/ch25_evaluation.py` programmatically, so it is verbatim by construction, and it includes
the change-3 edit; the comment `# exact null distribution for n <= 20` and the merged
`out["p_wilcoxon"], out["p_exact"] = w["p"], w["exact"]` were moved into the `.py` file as the
reviewer's first option suggests. The excerpt is 42 lines, still under the 45-line limit.

**5. Over which runs the means are taken (C).** The reviewer's clause is added verbatim to the
`tab:ch25-results` caption, after "so one row serves".

**Suggestions.** Adopted: (a) "the six pitfalls collected in the five boxes above"; (b) the
$c_{99}$ column, which was possible without a rerun because `ch25-study-runs.dat` carries
`comp_p99_ms` per run from the same study - the values 0.16, 0.15, 0.48, 0.81, 0.54, 0.16,
0.17, 0.97, 0.62, 1.02 ms are the per-cell means of that column, the caption names the
estimator, and three sentences in "Effort and constraints" draw the moral (replan-only is the
cheapest on average but its tail is as large as the reactive strategies', because a replan is
rare and expensive; a deadline is missed by the tail, not by the mean); the table needed
`\tabcolsep` 3pt -> 2pt to stay inside the text block; (c) the cost of Exercise 25.7(a)
($27$ cells, $2160$ runs, roughly ten times the mini-study, a few minutes); (d) the two
wall-clock statements now agree at 25 s; (e) `ch25-study-runs.dat` has a leading `#` provenance
line naming the generating script, the code file and the study configuration, and `write_dat()`
grew an optional `note=` argument that `gen_ch25_study.py` passes for that file only (the
pgfplots-read files keep a bare header row); the git commit is *not* written into it, because
this brief forbids running git and the repository autosaves, so any hash recorded here would be
wrong within the minute - the line ends by telling the reader to add it; (f) a solution sketch
for `exr:ch25-simulator` was added, so all eight exercises now have solutions.

**Checks.** `python3 code/ch25_evaluation.py`: self-test passes in 26.4 s, no warnings, all
sixteen paired rows and the per-cell summary unchanged and equal to the shipped `.dat`
(non-timing columns reproduce exactly). `./build.sh ch25-experiments`: no `!` errors, no
undefined reference or citation belonging to this chapter, chapter body pages 27-50 = 24 pages
as before, and the only overfull box above 15 pt is the 29.1 pt List-of-Algorithms entry of
another chapter; the table's own 13.6 pt overfull box, created by the new column, is gone. The
script exits 12 for the reason diagnosed in this review: 40 unresolved cross-chapter references
(`ch:ch11`, `ch:ch13`, `ch:ch14`, `ch:ch19`, `ch:ch20`, `ch:ch21`), which section 7 of the style
guide allows in a single-chapter build.
