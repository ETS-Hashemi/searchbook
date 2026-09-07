# Review of Chapter 19 (Nonlinear Filtering: EKF, UKF and Particle Filters) - round 1

## Verdict

**Minor revision.**

This is a strong, technically sound chapter. I checked every formula in it against the
canonical sources and by hand/by script: the coordinated-turn model
(`eq:ch19-ct`), its Jacobian (`eq:ch19-ct-jacobian`, all ten non-trivial entries and the
six `omega -> 0` limits), the range-bearing Jacobian (`eq:ch19-rb-jacobian`), the wrap map
(`eq:ch19-wrap`, including the `(-pi, pi]` end points), the EKF equations, the scaled
unscented transform (`eq:ch19-sigma`, `eq:ch19-ut`, `lambda = alpha^2 (n+kappa) - n`,
`W_0^(c) = lambda/(n+lambda) + 1 - alpha^2 + beta`), the UKF update with the
cross-covariance, SIR/bootstrap weighting, `N_eff`, and systematic resampling are all
correct. The proofs of `thm:ch19-ct-jacobian`, `thm:ch19-rb-jacobian`,
`thm:ch19-ekf-order`, `thm:ch19-ut` and `thm:ch19-systematic` are correct as written (I
re-derived the second-order UT argument and the interval-counting argument for systematic
resampling); `thm:ch19-pf-convergence` is correctly attributed to Crisan and Doucet with a
proof sketch and citation. Every number in `ex:ch19-ekf`, `tab:ch19-ekf-trace`,
`sec:ch19-ukf-example`, `sec:ch19-ekf-failure`, `tab:ch19-rmse`, `fig:ch19-compare`'s
caption and `ex:ch19-occlusion` is reproduced by `code/ch19_nonlinear_filters.py` or by
`code/figures/gen_ch19_*.py`, which I ran (all self-tests pass in 0.2 s; the three figure
generators reproduce 3.78/2.74/2.76/4.04, 10.11/6.88/6.21/7.62, 3.92/3.09/2.71/2.68,
3.89/3.10/2.90/5.74, the single-run 3.61/2.80/2.89/2.76, 74.6 %/91.6 %/86.5 %,
68.3 %/27.8 %, `N_eff` 17 at k=20 and 432 at k=21, 13 of 29 resamplings). The build is
clean: status 0, no errors, no overfull boxes, no undefined labels or citations belonging
to this chapter (only cross-chapter `??` to unwritten chapters), all 13 citation keys exist
and their bibliographic details are correct, 46 index entries, 8 exercises, 5 figures, 3
tables, 4 algorithms, 2 pitfalls, glossary and solutions files present. Every "must cover"
item of `docs/specs/ch19.md` is present.

What blocks Accept is a small set of local defects: one paragraph that contradicts itself,
one overstated variance claim about systematic resampling, three timing numbers the code
does not print, and - most visibly - two figures whose legends or axis limits hide exactly
what their captions tell the reader to look at. All fixes are local; none requires
rewriting or restructuring.

Length: the chapter body is pages 16-35 of the single-chapter PDF, i.e. **20 pages** - at
the limit, three above the spec's 15-17. I am **not** requiring cuts: the excess is
required content (three filters, three worked examples, three pseudocodes), not padding.
Optional trims are listed under Suggestions.

## Required changes

1. **Location:** `sec:ch19-ukf-compare`, the "Four things to notice" paragraph, third item
   (ch19-nonlinear-filters.tex around line 770).
   **Problem:** the sentence contradicts itself and `tab:ch19-rmse`. It says "the poor
   start is survived by every filter in every run" and then, in the same sentence, "one of
   its runs never recovers"; the table's `lost` column for that row is `0/0/1`.
   **Fix:** restrict the first clause to the Gaussian filters, e.g. "Third, the poor start
   is survived by both Gaussian filters in every run, because the range-bearing measurement
   pins the position at each step; the UKF recovers faster than the EKF (2.90 against
   3.10 m) and the particle filter more slowly (median 3.08), and one of its hundred runs
   never recovers: ...".
   **Category:** A (also C).

2. **Location:** `sec:ch19-resampling`, the sentence introducing systematic resampling
   (around line 863): "in `O(N)` time and with the smallest variance of the standard
   schemes."
   **Problem:** this is false as stated. Systematic resampling has no general
   variance-optimality guarantee; its result depends on the *order* of the particles, and
   there are weight configurations for which its variance exceeds that of multinomial
   resampling. The scheme with a proof that it never does worse than multinomial is
   *stratified* resampling.
   **Fix:** replace by, e.g., "... in `O(N)` time; its per-particle counts obey
   `\cref{thm:ch19-systematic}`, and in practice its variance is far below multinomial
   resampling's, although - unlike stratified resampling, which provably never does worse
   than multinomial - systematic resampling carries no such guarantee, and its result
   depends on the order of the particles." Add a citation only if you can verify it
   yourself (Douc, Cappe and Moulines, "Comparison of resampling schemes for particle
   filtering", ISPA 2005); otherwise state the fact without a new reference.
   **Category:** A.

3. **Location:** `figures/ch19/particles.tex`, the left (`name=map`) axis; rendered as
   Figure 3.5 on page 29 of `build/only-ch19-nonlinear-filters.pdf`.
   **Problem:** the six-entry legend box, anchored `north west` inside an axis that is only
   `0.43\textwidth` wide but 104 m tall with `axis equal image`, covers the whole region
   `y in [38, 100]` - that is, the building rectangle, the "no measurements" band, the
   k=15 (orange) and k=20 (green) particle clouds, the purple UKF-mean square and the
   "building" node. The one thing the figure exists to show - the cloud splitting into two
   lobes around the building while the UKF mean sits inside it - is invisible.
   **Fix:** move the legend out of the plotting area and give the panel room, e.g. replace
   the `legend style` with
   `legend style={font=\scriptsize, at={(0.5,-0.22)}, anchor=north, legend columns=3, draw=none}`,
   drop `axis equal image` in favour of `axis equal=false` with `height=6.5cm`, and tighten
   `xmin=-40, xmax=40`. Check in the rebuilt PDF that all three clouds, the obstacle
   rectangle, the "building" node and the purple square are visible and unoccluded.
   **Category:** D.

4. **Location:** `figures/ch19/linearisation.tex` (both `\nextgroupplot`s); rendered as
   Figure 3.3 on page 23.
   **Problem:** with `xmin=-45, xmax=45` the objects the caption points at are clipped and
   squashed. The sample cloud reaches `x = +-56 m` (radius 100 at `+-2 sigma_phi = +-0.6`
   rad) and the `2 sigma` ellipses reach `x = +-60` (EKF, `sigma_x = 30`) and `+-57` (MC,
   `sigma_x = 28.35`), so all three run off the left and right edges; with
   `axis equal image` over an x range of 90 m and a y range of 54 m the panels are so flat
   that the 4.4 m gap between the blue EKF mean and the red true-mean cross is about one
   millimetre, and the "banana" reads as a straight horizontal bar. The legends
   additionally sit on top of the sample cloud.
   **Fix:** set `xmin=-70, xmax=70, ymin=55, ymax=118` so that the full ellipses and the
   tips of the arc fit, increase `height` to about `6.5cm`, move the legends below the axes
   (`legend style={at={(0.5,-0.22)}, anchor=north}, legend columns=2`), and annotate the
   4.4 m offset explicitly, e.g.
   `\draw[<->,sbRed] (axis cs:6,95.6) -- node[right,sbannot]{$4.4$\,m} (axis cs:6,100);`
   **Category:** D.

5. **Location:** `sec:ch19-ukf-compare` last sentence ("Fourth, the cost: 0.27 ms per step
   for the EKF, 0.47 for the UKF and 1.2 ms ..."), the "Cost per step" paragraph of
   `sec:ch19-properties`, and the "Cost per step" row of `tab:ch19-comparison`.
   **Problem:** the chapter presents these as measured, but
   `python3 code/figures/gen_ch19_compare.py` prints
   `mean time per filter step (ms): EKF 0.258, UKF 0.458, PF 1.175`. 0.27 and 0.47 are not
   what the script produces (they round to 0.26 and 0.46), and the numbers appear three
   times.
   **Fix:** quote the printed values in all three places (`0.26`, `0.46`, `1.2` ms) and add
   "on the machine used for `\cref{tab:ch19-rmse}`" once, so that a reader whose timings
   differ is not misled; or state the ratios (`1x`, `1.8x`, `4.6x`) and give the absolute
   numbers only once.
   **Category:** A.

6. **Location:** `figures/ch19/compare.tex`, both `\nextgroupplot`s; rendered as Figure 3.4
   on page 26.
   **Problem:** in the left panel the `north west` legend covers the sensor marker
   (`\node[sbagentA] at (axis cs:0,0)`) and its "sensor" label, which the caption's story
   depends on; in the right panel the `north east` legend covers the peaks of the grey
   measurement-error curve, and the "left turn" / "right turn" annotations, drawn at 2 % of
   the axis height, are overprinted by the curves and are illegible.
   **Fix:** in the left panel move the legend to `at={(0.97,0.03)}, anchor=south east`
   (that corner is empty) or below the axis; in the right panel put the legend below the
   axis (`at={(0.5,-0.28)}, anchor=north, legend columns=4`) and move the two turn labels
   to the top of the axis with a white background
   (`node[sbannot, fill=white, inner sep=1pt, anchor=north west]` at
   `{rel axis cs:0,0.97}`-height) so that they sit above the data.
   **Category:** D.

7. **Location:** `\section{Properties: accuracy, convergence and cost}`
   (`sec:ch19-properties`, around line 991); visible on pages 29-30.
   **Problem:** the running head overlaps: the left mark "Chapter 3. Nonlinear Filtering:
   EKF, UKF and Particle Filters" and the right mark "3.7 Properties: accuracy,
   convergence and cost" collide and print on top of each other ("... Particle Filt3r7
   Properties: ..."). It will be worse in the full book, where the number is "19". No
   overfull box is reported, so the build log does not catch it.
   **Fix:** give the section a short mark:
   `\section[Properties and cost]{Properties: accuracy, convergence and cost}`. Check the
   other long heads in the rebuilt PDF (`\section[Where this fits]{Where this fits in the
   drone system}` is currently just short enough, but will not be after renumbering to 19).
   **Category:** G.

8. **Location:** `lst:ch19-pf` (`sec:ch19-implementation`) / `code/ch19_nonlinear_filters.py`,
   the `update` method; rendered on page 33.
   **Problem:** three source lines are too long for the text column, so `breaklines`
   wraps them to the *left margin* with no continuation indent: the comment "# optional
   jitter of / the copies" is split across two lines, and
   `self.X = self.X + self.rng.normal(size=self.X.shape) * / self.roughening` and
   `self.logw = np.full(self.n, -math.log(self.n))` lose their Python indentation. In a
   listing that teaches indentation-sensitive code this is misleading.
   **Fix:** shorten the three lines in `code/ch19_nonlinear_filters.py` to <= 78 characters
   (move the "optional jitter of the copies" comment onto its own line above the `if`; use
   a temporary, e.g. `jitter = self.rng.normal(size=self.X.shape) * self.roughening`), re-run
   the self-test, and re-copy the excerpt verbatim into the listing.
   **Category:** G.

## Suggestions

* `sec:ch19-ekf-failure`: "the exact mean is `100 e^{-0.3^2/2} = 95.6`, because the samples
  lie on an arc of radius 100" - the samples do not lie on an arc, `r` has `sigma_r = 5`.
  The formula comes from `E[sin phi] = e^{-sigma_phi^2/2}` for a Gaussian angle together
  with the independence of `r` and `phi`. Keep the arc as intuition but say so: "because
  `E[r sin phi] = E[r] E[sin phi]` and `E[sin phi] = e^{-sigma_phi^2/2}` for a Gaussian
  bearing - averaging points spread along an arc pulls the mean inside it".
* Same paragraph: the unscented transform's y-spread there is 10.1 m against the samples'
  7.7 m, i.e. the UT *over*-estimates the spread (which is why its ellipse holds 91.6 %
  rather than 86.5 %). One clause saying that the UT is conservative here, not exact, would
  stop a reader from concluding that 91.6 % is "better" than 86.5 %.
* Same paragraph, and `exr:ch19-banana`: the figure and the exercise use `n = 2, alpha = 1,
  kappa = 1` (`lambda = 1`, five points at `sqrt(3)` standard deviations), not the chapter's
  default `kappa = 0`. State the parameters once in the caption of
  `fig:ch19-linearisation` so the two agree visibly.
* `eq:ch19-ct-noise`: `G(x)` ignores the coupling of the turn acceleration `gamma` into
  `(x, y)`. Add "to first order in `Delta t`" after "so that", so the construction is not
  read as exact.
* `alg:ch19-resample`: add the rounding guard that the code has
  (`c_N <- 1` before the loop, `\tcp*{guard against rounding}`), otherwise the pseudocode
  can run `i` past `N` when the weights sum to `1 - eps`.
* `sec:ch19-pf-example`: 68.3 % + 27.8 % = 96.1 %; say in half a clause where the remaining
  4 % are (still level with the building, north or south of it), so the reader does not
  hunt for a third lobe.
* `code/figures/gen_ch19_particles.py`, the diagnostic print at the end ("UKF mean while
  hidden (k, x, y)") is off by one relative to `occlusion_example()`: it labels the
  `(-3.0, 61.4)` mean `k = 14` and the `(-15.1, 73.7)` mean `k = 19`, while
  `occlusion_example()` prints them as `k = 15` and `k = 20`. The figure data are correct
  (they come from `res["stages"]`); only the print is shifted. Fix the enumerate offset so
  a reader who runs the generator is not confused.
* Multinomial resampling is `O(N log N)` "with binary search"; it is `O(N)` with sorted
  uniforms. One parenthesis would make the comparison with systematic resampling exact.
* Exercise difficulty is bunched: 1, 2, 1, 2, 2, 2, 2, 3. Consider promoting
  `exr:ch19-occlusion` to `\difficulty{3}` (it asks for three code modifications and their
  explanation) or adding a `\difficulty{1}` reading-the-table question.
* Only 4 of the 8 exercises have entries in
  `appendices/solutions/ch19-solutions.tex` (which is already better than most chapters).
  Short hints for `exr:ch19-wrapping`, `exr:ch19-banana` and the two coding exercises would
  help a reader working alone - the numbers are already in the code.
* Optional trims if the editor wants the chapter back to 18 pages, all padding rather than
  content: (i) the second half of `sec:ch19-ukf-example` restates numbers already in
  `tab:ch19-ekf-trace` - the sigma-point straddling argument and the second-order check are
  worth keeping, the sentence-by-sentence recital of the update is not (~8 lines);
  (ii) the "Four things to notice" paragraph repeats every figure in `tab:ch19-rmse` -
  the percentages can go, the *reasons* must stay (~5 lines); (iii) the
  `\paragraph{Better particle filters, and three dimensions.}` list of variants could lose
  the auxiliary and regularised filters, which are already named in
  `sec:ch19-resampling` (~4 lines).
* `frontmatter/notation.tex` is still a placeholder with two rows, so I could not check
  this chapter against it. When it is written, it must contain `x`, `z`, `x_hat_k^-`,
  `P_k^-`, `y_k`, `S_k`, `K_k`, `F_k`, `H_k`, `Q_k`, `R_k`, `N_eff`, `X_i`, `W^(m)`,
  `W^(c)`, `lambda`, `alpha`, `beta`, `kappa`, `wrap`, and the `(-)` ("wrapped difference")
  operator, all of which this chapter uses. Similarly, `ch18-kalman-filter.tex` is still a
  stub, so the claim in `sec:ch19-problem` that "we keep the notation of `\cref{ch:ch18}`"
  is currently unverifiable - the ch18 author should be handed this chapter's symbol list
  (`x_hat_k^-`, `P_k^-`, `y_k`, `S_k`, `K_k`, Joseph form, white-noise-acceleration `Q`).

## What must be kept

The chapter is unusually careful where nonlinear filtering is usually sloppy, and that care
must survive revision. Keep the three-way structure - EKF, UKF, PF in increasing order of
generality and cost - and the single running scenario (turning intruder plus a
range-bearing sensor) that all three are applied to; running the *same* step through
`alg:ch19-ekf` and `alg:ch19-ukf` in `tab:ch19-ekf-trace`, then explaining the 0.21 m
difference by `1/2 P_psi_psi d^2 x'/d psi^2 = 0.197` m, is the best piece of teaching in the
chapter and is exactly right. Keep the honest empirical comparison in `tab:ch19-rmse`: four
scenarios, mean *and* median, a "lost" column, and the finding that the EKF is
indistinguishable from the UKF in the easy case and 10-12 % worse only when the belief
widens - textbooks routinely assert UKF superiority without this evidence. Keep the
treatment of angles: the explicit `wrap` map, the `(-)` operator, the wrapped sigma-point
mean, the circular mean of a particle cloud, and the pitfall computing what an unwrapped
6.2 rad innovation costs. Keep the log-weight/`N_eff`/sawtooth story and the occlusion
example with the map as a likelihood - the two-lobe cloud against a UKF mean sitting inside
a building is the clearest possible argument for particle filters and the right hand-off to
the prediction-aware constraints of Chapter 24. Keep the proofs as they stand
(`thm:ch19-ut`'s cancellation argument and `thm:ch19-systematic`'s interval-counting
argument are both correct and short), the `Q(x)`-at-the-right-point pitfall, the Joseph
form in `alg:ch19-ekf`, and the decision guide "which filter for which intruder model",
which is what a reader will actually come back to.

---

## Response to review (round 1)

All eight required changes are applied. Build: `cd Overleaf && ./build.sh ch19-nonlinear-filters`
returns **status 0**, no `!` errors, no overfull box wider than 15 pt (three remain at
13.4, 7.8 and 4.8 pt). `python3 code/ch19_nonlinear_filters.py` passes all self-tests in
0.2 s. `code/figures/gen_ch19_compare.py`, `gen_ch19_linearisation.py` and
`gen_ch19_particles.py` were re-run; no `.dat` file changed, because the only code edits
were cosmetic (line lengths) and a print-label offset.

### Required changes

1. **`sec:ch19-ukf-compare`, "Four things to notice", third item — self-contradiction.**
   Fixed as suggested. The clause now reads "the poor start is survived by *both Gaussian
   filters* in every run ... and one of its hundred runs never recovers", so it agrees with
   the `0/0/1` in `tab:ch19-rmse`. "hundred" is exact: `RUNS = 100` in
   `code/figures/gen_ch19_compare.py`.

2. **`sec:ch19-resampling` — the variance claim for systematic resampling.**
   Replaced with the reviewer's wording: O(N) time, counts obeying `thm:ch19-systematic`,
   variance far below multinomial's in practice, but no general guarantee and a dependence
   on particle order, contrasted with stratified resampling (now defined and indexed), which
   provably never does worse than multinomial. Douc, Cappé and Moulines, ISPA 2005, is cited;
   I am certain of authors, title, venue and year, so the entry was added to
   `Overleaf/bib/ch19-extra.bib` (`douc2005comparison`, no page numbers) rather than guessed
   at. The neighbouring multinomial sentence now also carries the parenthesis the suggestions
   asked for: O(N log N) with one binary search per draw, O(N) with sorted uniforms.

3. **`figures/ch19/particles.tex` — legend covering the whole map.**
   The legend is out of the plotting area, below the axis (`at={(0.5,-0.24)}, anchor=north,
   draw=none`). `axis equal image` is gone, `height=6.5cm`, `xmin=-40, xmax=40`, and the grey
   band and the "no measurements" node were moved to match the new x limits (the node now
   sits above the band, at `(39,76)`, in empty space). Two further occlusions the fix
   exposed were repaired: the white "building" label sat exactly on the purple UKF mean, so
   it moved to the bottom of the rectangle, and the UKF-mean square is now 3 pt with a white
   edge so that it reads against the dark obstacle fill. In the right panel `ymax` went to
   1.2 so the "no measurements" label is no longer clipped, and "threshold N/2" got a white
   background. **Verified in the rebuilt PDF:** all three clouds (blue k=7, the two-lobe
   orange k=15, green k=20), the obstacle rectangle, its label, the three true-position
   crosses and the purple square are visible and unoccluded.
   *Deviation:* `legend columns=2`, not 3 — six entries in three columns overflow a
   `0.40\textwidth` axis.

4. **`figures/ch19/linearisation.tex` — clipped, squashed panels and legends on the cloud.**
   `xmin=-70, xmax=70, ymin=55, ymax=118`, `height=6.5cm`, `axis equal image` dropped,
   legends below the axes in two columns. All three ellipses (EKF ±60, MC ±56.9, UT ±57.3)
   and the arc tips now fit. The 4.4 m offset is annotated explicitly, but drawn clear of the
   markers: two dotted guides run from the two means out to x = 24, where a red double arrow
   and a white-backed "4.4 m" label sit. Because the axes are no longer to the same scale,
   the caption now says so and says why. The caption also states the transform's parameters
   (n = 2, alpha = 1, beta = 2, kappa = 1, lambda = 1, points at sqrt(3) sd) and notes that
   the chapter's default elsewhere is kappa = 0 — the third suggestion.

5. **Timings quoted three times, not matching the script.**
   Taken the second of the two offered routes. Absolute numbers now appear **once**, in the
   "Cost per step" paragraph of `sec:ch19-properties`, as "about 0.26 ms (EKF), 0.46 ms (UKF)
   and 1.2 ms (particle filter, N = 2000) ... on the machine used for `tab:ch19-rmse`", with
   the explicit caveat that absolute times move with the machine and the ratios do not. The
   other two places give ratios only: "roughly 1.8 times an EKF step ... roughly 4.5 times"
   in `sec:ch19-ukf-compare`, and `1x / 1.8x / 4.5x` in the "Cost per step" row of
   `tab:ch19-comparison` (its caption changed to match). A fourth occurrence the review did
   not list, in the "Vectorising the particle filter" paragraph, now says "about a
   millisecond". On this machine the generator prints EKF 0.269, UKF 0.470, PF 1.208 ms and a
   twelve-repeat re-measurement gives 0.264 / 0.460 / 1.162 ms (ratios 1.74 and 4.40); the
   reviewer's machine printed 0.258 / 0.458 / 1.175 (1.78 and 4.55). Both round to
   0.26 / 0.46 / 1.2 ms and to "roughly 1 : 1.8 : 4.5", which is why the ratio form was
   chosen.

6. **`figures/ch19/compare.tex` — legends over the sensor and over the error peaks.**
   Right panel: legend moved below the axis (`at={(0.5,-0.26)}, anchor=north,
   legend columns=4`), and the two turn labels moved to the top of the axis
   (`rel axis cs:0,0.98`, `anchor=north west`) with a white background, so they sit above the
   curves; `ymax=8` keeps the grey curve's 7.05 m peak inside.
   *Deviation, left panel:* the review suggested `at={(0.97,0.03)}, anchor=south east`, but
   that corner is **not** empty — the true path starts at (120, -94) and climbs the right
   edge, so a south-east legend would sit on it. The only empty corner is the south-west one
   (no data point has y < -40 except at x ~ 120), and the legend went there. The sensor
   marker and its "sensor" label are now clear, which was the point of the item.

7. **Running-head collision (`sec:ch19-properties`).**
   `\section[Properties and cost]{Properties: accuracy, convergence and cost}`. The document
   is `oneside`, so `\leftmark` and `\rightmark` share one line on every page; I gave short
   marks to the three other heads that would be at risk after renumbering to 19 as well:
   `\section[Where this fits]{...}`, `\section[Why this matters]{...}` and
   `\section[Problem and notation]{...}`. The longest surviving pair is
   "Chapter NN. Nonlinear Filtering: EKF, UKF and Particle Filters" against
   "NN.5 The unscented Kalman filter", which leaves a clear gap in the rebuilt PDF; one extra
   digit in the chapter number does not close it. The chapter title itself was left long, so
   the table of contents keeps the full title.

8. **`lst:ch19-pf` wrapping and lost indentation.**
   `code/ch19_nonlinear_filters.py` edited: the "optional jitter of the copies" comment is
   now a line of its own above the `if`, the roughening update goes through a temporary
   (`jitter = self.rng.normal(size=self.X.shape)`), and the two long docstrings and the
   `isfinite` / `log-sum-exp` comments in the same excerpt were shortened. Every line of the
   excerpt is now at most 77 characters; the listing wraps at about 80. The listing in the
   chapter was re-extracted from the file programmatically, so it is verbatim. Self-test
   re-run and passing. Verified on the rendered page: no line wraps, all Python indentation
   intact.

### Suggestions

Applied: the real reason for the 95.6 m mean (independence plus
E[sin phi] = exp(-sigma_phi^2/2)), with the arc kept as intuition; the clause saying the UT
is conservative here, not exact, so 91.6 % is not "better" than 86.5 %; the transform's
parameters in the `fig:ch19-linearisation` caption; "to first order in Delta t" for
`eq:ch19-ct-noise`, with the coupling of gamma named; the rounding guard in
`alg:ch19-resample` (as `i < N` in the while test, which is the correct guard for the
incremental cumulative sum the pseudocode uses — "c_N <- 1" belongs to the code's
precomputed `cumsum`, not to that loop, so it is stated as a comment line instead); the
missing 4 % in `sec:ch19-pf-example`; the multinomial O(N) parenthesis; the enumerate offset
in `gen_ch19_particles.py` (the slice now starts at `k_last`, so the printed k values are
8...20 and agree with `occlusion_example()`); `exr:ch19-occlusion` promoted to
`\difficulty{3}`, so the spread is 1, 2, 1, 2, 2, 2, 3, 3; and hints/solutions added for the
four exercises that had none (`exr:ch19-wrapping`, `exr:ch19-banana`, `exr:ch19-occlusion`,
`exr:ch19-coding`) — the banana solution carries the hand computation and lands on 95.60 m
from both the exact formula and the five sigma points.

Not applied: the optional trims. They are explicitly optional, and two of the three touch
material the review's own "what must be kept" paragraph protects; the brief forbids removing
content to save space. The chapter body is 21 pages in the single-chapter build.

Passed on: the notation-table and ch18 item is not this chapter's file. Symbol list for
whoever owns those: x, z, x_hat_k^-, P_k^-, y_k, S_k, K_k, F_k, H_k, Q_k, R_k, N_eff,
X_i, W^(m), W^(c), lambda, alpha, beta, kappa, wrap, and the wrapped-difference operator.
