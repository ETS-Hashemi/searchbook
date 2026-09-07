# Review of Chapter 19 (Nonlinear Filtering: EKF, UKF and Particle Filters) - round 2

## Verdict

**Minor revision.**

**Round-1 items: all eight are resolved, and resolved correctly.** I checked each one in
the current source and in the rebuilt PDF and I do not re-raise any of them.

1. `sec:ch19-ukf-compare`, third of the "four things to notice", now reads "the poor start
   is survived by *both Gaussian filters* in every run ... and one of its hundred runs never
   recovers", which agrees with the `0/0/1` of `tab:ch19-rmse`. Fixed.
2. The systematic-resampling variance claim is gone. The new sentence (O(N) time, counts by
   `thm:ch19-systematic`, variance far below multinomial's in practice, no general
   guarantee, order-dependent, contrasted with stratified resampling) is correct, and
   `douc2005comparison` (Douc, Cappe and Moulines, ISPA 2005) is a real paper with correct
   authors, title, venue and year. The multinomial parenthesis (`O(N log N)` with one binary
   search per draw, `O(N)` with sorted uniforms) is also correct. Fixed.
3. `figures/ch19/particles.tex`: legend moved below the axis, `axis equal image` dropped,
   `height=6.5cm`, `xmin/xmax = -40/40`. In the rebuilt PDF (Figure 3.5, page 31) all three
   clouds, the obstacle rectangle, its label, the three crosses and the purple UKF square
   are visible and unoccluded. Fixed.
4. `figures/ch19/linearisation.tex`: `xmin=-70, xmax=70, ymin=55, ymax=118`, `height=6.5cm`,
   legends below in two columns, the 4.4 m offset annotated with dotted guides and a red
   double arrow, and the caption now states the transform's parameters and warns that the
   axes are not to the same scale. All three ellipses and the arc tips fit. Fixed.
5. Timings: absolute numbers appear once, in `sec:ch19-properties`, with the caveat "on the
   machine used for `\cref{tab:ch19-rmse}`"; the other two places give ratios. Fixed (see
   Suggestions for a small robustness point).
6. `figures/ch19/compare.tex`: right-panel legend below the axis in four columns, turn
   labels moved to the top with white backgrounds, `ymax=8`; left-panel legend in the
   south-west corner, clear of the sensor marker and its label. The reviser's deviation
   (south-west rather than south-east) is right: the south-east corner carries the track.
   Fixed.
7. `\section[Properties and cost]{...}` and three further short marks; no running-head
   collision anywhere in the rebuilt PDF. Fixed.
8. `lst:ch19-pf`: every source line now fits the column, no `breaklines` wrap, Python
   indentation intact throughout (checked on pages 34-35). Fixed.

**Verification done this round.** Build: `./build.sh ch19-nonlinear-filters` returns status
0, no `!` errors, no overfull box wider than 15 pt (three remain at 13.4, 7.8 and 4.8 pt),
no undefined label or citation belonging to this chapter (only `ch:ch20` and `ch:appA`,
outside the single-chapter build). All 14 citation keys resolve, in `references.bib` or
`bib/ch19-extra.bib`, and I can vouch for every one of them: Kalman-family and PF sources
(Thrun/Burgard/Fox 2005; Julier & Uhlmann SPIE 3068:182-193, 1997 and Proc. IEEE
92(3):401-422, 2004; Wan & van der Merwe AS-SPCC 2000:153-158; Gordon/Salmond/Smith IEE
Proc. F 140(2):107-113, 1993; Arulampalam et al. IEEE TSP 50(2):174-188, 2002;
Kitagawa JCGS 5(1):1-25, 1996; Crisan & Doucet IEEE TSP 50(3):736-746, 2002; Doucet/de
Freitas/Gordon, Springer 2001; Blom & Bar-Shalom IEEE TAC 33(8):780-783, 1988; Arasaratnam
& Haykin IEEE TAC 54(6):1254-1269, 2009; Bar-Shalom/Li/Kirubarajan 2001; Sarkka 2013;
Douc/Cappe/Moulines ISPA 2005) are all real and correctly described. 52 index entries,
5 figures, 3 tables, 4 algorithms, 1 listing, 2 pitfall boxes, 8 exercises with all 8
solved in `appendices/solutions/ch19-solutions.tex`, 15 glossary terms in
`appendices/glossary/ch19-terms.tex`.

`python3 code/ch19_nonlinear_filters.py` passes all self-tests in 0.2 s. I re-ran all three
figure generators. Every number quoted in the chapter is reproduced:
`ex:ch19-ekf`/`tab:ch19-ekf-trace` (F entries -0.9851/1.4888/0.991/-0.1489/-9.8507/-4.8881,
prediction (-109.851, -5.489), `h` = (109.99, -3.0917), naive innovation 6.2117, wrapped
-0.0715, `H` = (-0.9988, -0.0499; 0.00045, -0.00908), `S` = diag(9.28, 0.0016),
K11 = -0.569, K22 = -47.05, K31 = 0.16, K42 = 2.56, update (-110.941, -2.134, 10.190,
-3.0313, 0.2787), all ten standard deviations, and the UKF row (-110.834, -2.176, 10.214,
-3.0284, 0.2784) with its sigma-point images (-108.238, -9.602) and (-109.526, -1.082),
average x = -108.882, prediction shift 0.21 m against the second-order estimate 0.197 m);
`sec:ch19-ekf-failure` (MC mean (-0.16, 95.58), exact 95.60, EKF (0, 100), UT (0, 95.60),
sigma along y 5.00 / 7.65 / 10.12, coverage 74.6 % / 91.6 % / nominal 86.5 %);
`tab:ch19-rmse` (all 4 x 8 entries, exactly); the caption of `fig:ch19-compare`
(3.61 / 2.80 / 2.89 / 2.76); and `ex:ch19-occlusion` (68.3 %, 27.8 %, UKF mean
(-3.0, 61.4), `N_eff` 17 at k = 20 and 432 at k = 21, 99.9 %, 13 resamplings in 29 steps).
I re-derived the coordinated-turn Jacobian and its six `omega -> 0` limits, the
range-bearing Jacobian, the wrap map at both end points, the scaled-UT weights, the proofs
of `thm:ch19-ekf-order`, `thm:ch19-ut` and `thm:ch19-systematic`, and the hand computation
of `exr:ch19-ess`(d) (u = 0.1 gives counts 3, 0, 1, 0, consistent with
`thm:ch19-systematic`). All correct.

**What blocks Accept** is one sentence that the chapter's own data contradict, plus the
concept figure `fig:ch19-idea`, which is the one figure round 1 did not examine closely: it
has three text collisions and, more seriously, it does not show the bias its caption tells
the reader to look at. All four required changes are local; none touches the structure, the
mathematics or the code.

**Length.** The chapter body is pages 17-37 of `build/only-ch19-nonlinear-filters.pdf`,
i.e. **21 pages**, one above the brief's ceiling and four above the spec's 15-17. Most of
the overrun is required content (three filters, three worked examples, three pseudocodes,
five figures) and part of it was created by required changes 3 and 4 of round 1, which
enlarged two figures - I am not asking for any of that back. Required change 4 below names
the only passages that are genuine repetition (prose reciting numbers that stand two inches
above in a table); removing them costs no content and should bring the chapter to 20 pages.

## Required changes

1. **Location:** `sec:ch19-pf-example`, the last long paragraph
   (`ch19-nonlinear-filters.tex` around line 985): "The filter resamples in $13$ of the $29$
   steps, and after each one the curve in the right panel restarts near $N$: the sawtooth is
   the signature of a healthy filter."
   **Problem:** the claim "the curve in the right panel restarts near $N$" is contradicted
   by the chapter's own figure and by its generator. `python3 code/figures/gen_ch19_particles.py`
   prints the plotted sequence; the value at the step *after* each of the 13 resamplings is
   592, 934, 865, 772, 514, 2000, 1906, 432, 1033, 1653, 1424, 964, 1465 out of $N = 2\,000$
   - eight of the thirteen below $0.55N$, and the one value that does reach $N$ (2000) is the
   first step of the measurement-free band, not a recovery. The right panel of
   `fig:ch19-particles` shows exactly that: outside the measurement-free band the green
   curve oscillates between about $0.2$ and $0.8$ and never returns to $1$. The reason is stated correctly elsewhere in the
   chapter but not joined up here: `alg:ch19-pf` computes $N_{\mathrm{eff}}$ on
   line~\ref{alg:ch19-pf:ess}, *before* resampling, so the plotted point at step $k+1$
   already includes the re-concentration caused by the next measurement. A reader who
   believes the sentence will read the figure as showing a sick filter.
   **Fix:** replace the clause, e.g.: "The filter resamples in $13$ of the $29$ steps.
   Resampling resets the weights to $1/N$, but the very next measurement immediately
   re-concentrates them, and $N_{\mathrm{eff}}$ is plotted *before* resampling
   (line~\ref{alg:ch19-pf:ess}), so the curve climbs back only to between $0.2N$ and $0.8N$:
   that sawtooth between the threshold and a partial recovery is the signature of a healthy
   filter with informative measurements. A curve pinned near $N$, as in the measurement-free
   band, means the data are telling the filter nothing; one pinned near $1$ means a lost
   track." Then check the wording of the second pitfall box, which already says the same
   thing correctly, so that the two agree.
   **Category:** A (also C).

2. **Location:** `figures/ch19/idea.tex`, the column heading at `(7.0,1.0)`, the blue label
   at `(7,0.78)` and the row labels at `(-2.9,0)`; rendered as Figure 3.1 on page 18 of the
   PDF.
   **Problem:** three text collisions, all visible at normal reading size.
   (i) The two-line heading "output: true distribution of $f(\state)$ / and each filter's
   approximation" and the blue node "tangent image of the mean" (anchored `south` at
   $y = 0.78$, so its text occupies $y \approx 0.78$ to $0.95$) are printed on top of each
   other; both are illegible in the overlap.
   (ii) The row labels are set `anchor=west` at $x = -2.9$ while the input ellipse spans
   $x \in [-1.2, 1.2]$; at `\footnotesize` "(b) UKF: sigma points" is about $3.0$ cm wide,
   so it runs across the ellipse and prints through the left sigma point at $(-1.2, 0)$.
   "(a) EKF: linearise" and "(c) PF: samples" likewise end inside their ellipses (the latter
   over the sample cloud).
   (iii) The red "true mean" node, anchored `north` at $(7.35, 0.25)$, crosses the lower arc
   of the blue EKF ellipse.
   **Fix:** raise the heading to `at (7.0,1.45)`; move the row labels to
   `\node[sbannot,text=black,anchor=east] at (-1.45,0) {\lab};` so they end clear of the
   ellipses; move the "true mean" label to `anchor=north east` at `(6.6,0.05)` (or put it to
   the right of the banana with a short leader). Verify in the rebuilt PDF that no two
   pieces of text touch.
   **Category:** D.

3. **Location:** `figures/ch19/idea.tex`, row (a) (the EKF mean at `(7,0.4)`, the red cross
   drawn between `(6.9,0.27)` and `(7.1,0.47)`) and row (b) (the fitted ellipse centred at
   `(7,0.27)`); Figure 3.1, page 18.
   **Problem:** the figure does not show what its caption tells the reader to notice. The
   caption says "(a) ... the ellipse sits on the image of the mean, **not on the mean of the
   banana**" and "(b) ... the fitted mean lies inside the banana", but the blue EKF mean is
   at $y = 0.40$ and the centre of the red cross at $y = 0.37$ - $0.3$ mm apart, so the two
   markers are one blob in print, and the orange UKF centre is a further $1$ mm away. The
   entire teaching point of the chapter's concept figure, the EKF's outward bias and the
   UT's correction of it, is invisible. (The cross is also in the wrong place
   geometrically: the centroid of the drawn arc - radii $2.65$ to $3.35$ about $(7,-2.6)$,
   angles $60$ to $120$ degrees - is at $y = -2.6 + 3.014 \cdot (3/\pi) = 0.28$, not $0.37$.)
   **Fix:** widen the arc so the bias is visible, and put the three markers where they
   belong. Concretely: change both `arc (60:120:...)` / `arc (120:60:...)` pairs to
   `arc (50:130:...)` / `arc (130:50:...)`; change the map exponent from `20*\u` to `28*\u`
   in the two `\foreach` loops of rows (b) and (c) so the images still fill the arc; then
   place the true-mean cross at $(7, 0.18)$ (the centroid of the widened arc), leave the
   blue EKF mean and its ellipse at $(7, 0.40)$ on the apex, and lower the orange fitted
   ellipse and its centre to $(7, 0.22)$. Add the offset explicitly in row (a), e.g.
   `\draw[<->,sbRed!80!black] (8.05,0.40) -- node[right,sbannot,fill=white,inner sep=1pt]{bias} (8.05,0.18);`
   with dotted guides from the two markers, as `fig:ch19-linearisation` already does. Any
   equivalent change is fine provided the rebuilt PDF shows the blue mean clearly above the
   red cross, the orange mean between them, and the row-(c) banana clear of the row above.
   **Category:** D (also C).

4. **Location:** `sec:ch19-ukf-compare`, the "Four things to notice" paragraph
   (around lines 764-790); `sec:ch19-ukf-example`, its last four sentences (around lines
   745-760); `sec:ch19-variants`, the "Better particle filters" paragraph (around line 1195).
   **Problem:** the chapter is 21 pages (PDF pages 17-37), one over the brief's ceiling, and
   these three passages are prose that recites numbers already printed in an adjacent table,
   which the style guide asks you to put in tables rather than sentences (Section 3, "use
   tables for comparisons"). "Four things to notice" repeats eight of the twelve mean-RMSE
   figures of `tab:ch19-rmse` and both median figures; the second half of
   `sec:ch19-ukf-example` repeats four standard deviations and two state components that are
   rows of `tab:ch19-ekf-trace` two inches above; the variants paragraph re-introduces the
   auxiliary and regularised filters that `sec:ch19-resampling` has already named.
   **Fix:** keep every *reason* and cut only the duplicated figures. (i) In "Four things to
   notice", drop the parenthesised pairs and keep the percentages and the explanations:
   "in the baseline scenario the EKF and the UKF are indistinguishable: at ranges of
   45-160 m ...", "with $8^\circ$ of bearing noise the UKF's RMSE is $10\,\%$ below the
   EKF's, and on the close pass, where $\mathbf{H}$ changes fastest, $12\,\%$ below" (about
   6 lines). (ii) In `sec:ch19-ukf-example`, delete "The covariance also changes shape
   slightly ($\sigma_x = 2.355$ against $2.306$, $\sigma_y = 2.810$ against $2.854$)" and
   compress "The update redraws eleven points ... and the gain from the cross-covariance"
   to one clause, keeping the sigma-point straddling argument and the second-order check,
   which are the best teaching in the chapter (about 5 lines). (iii) In the variants
   paragraph, delete the auxiliary and regularised filters, keeping Rao-Blackwellisation
   and the three-dimensional state (about 3 lines). Re-run the build and report the page
   count; do not remove anything else to reach 20 pages.
   **Category:** G.

## Suggestions

* `sec:ch19-properties`, "Cost per step": on this machine
  `code/figures/gen_ch19_compare.py` prints `EKF 0.275, UKF 0.481, PF 1.229` ms, against the
  chapter's $0.26 / 0.46 / 1.2$ ms. The ratios ($1 : 1.75 : 4.47$) match "roughly
  $1 : 1.8 : 4.5$" exactly, and the text already says absolute times move with the machine,
  so nothing is wrong - but one significant figure ("about $0.3$, $0.5$ and $1.2\,\mathrm{ms}$")
  would survive any machine and would stop a reader from testing a number that cannot be
  reproduced.
* `figures/ch19/particles.tex`, left panel: the "no measurements" node sits *above* the grey
  band it labels (at $y \approx 76$, the band is $y \in [35,75]$) and runs flush to the right
  axis edge. Move it inside the band, e.g. `at (axis cs:0,44)` with `fill=white, inner sep=1pt`,
  or give it a short leader to the band.
* Same panel: the green $k = 20$ cloud is the smallest of the three and is partly covered by
  the black true-position cross. Draw the crosses before the clouds, or use `mark size=4pt`
  with a white outline, so the cloud is not hidden by its own annotation.
* `figures/ch19/linearisation.tex`, panel (a): the arrow head of the `4.4 m` double arrow
  clips the leading digit of the label. Move the label out one more unit
  (`at (axis cs:27,97.8)`), or set `inner sep=2pt`.
* `lst:ch19-pf` breaks across the page boundary in the middle of `update` (lines 1-30 on
  page 34, 31-34 on page 35). Either split it into two listings ("systematic resampling" and
  "the update"), which would also let each get its own caption, or move it before the
  "Vectorising" paragraph so it starts at the top of a page.
* Exercise difficulty is 1, 2, 1, 2, 2, 2, 3, 3. One more `\difficulty{1}` - for instance
  "read `tab:ch19-comparison` and say which filter you would put on a $50\,\mathrm{g}$
  microcontroller tracking one intruder at $300\,\mathrm{m}$, and why" - would flatten the
  entry step for a reader working alone.
* `frontmatter/notation.tex` is still a two-row placeholder, so this chapter still cannot be
  checked against it, and `ch18-kalman-filter.tex` still owes the symbols that
  `sec:ch19-problem` says it keeps. Hand the same list on again: `x`, `z`, `x_hat_k^-`,
  `P_k^-`, `y_k`, `S_k`, `K_k`, `F_k`, `H_k`, `Q_k`, `R_k`, `N_eff`, `X_i`, `W^(m)`,
  `W^(c)`, `lambda`, `alpha`, `beta`, `kappa`, `wrap`, and the wrapped-difference operator
  `\ominus`. This is not this chapter's file and is not a required change here.
* `sec:ch19-pf-example` says the remaining $4\,\%$ of particles at $k = 15$ are "still level
  with the building in $x$ but north or south of it". That is the only claim in the example
  the generator does not print; two extra lines in `occlusion_example()` counting them would
  make the whole example machine-checkable.

## What must be kept

Everything round 1 protected has survived the revision and must survive this one. Keep the
three-way structure - EKF, UKF, PF in increasing order of generality and cost - and the
single running scenario (turning intruder plus range-bearing sensor) that all three are
applied to; running the *same* step through `alg:ch19-ekf` and `alg:ch19-ukf` in
`tab:ch19-ekf-trace` and then explaining the 0.21 m difference by
$\tfrac12 P_{\psi\psi}\,\partial^2 x'/\partial\psi^2 = 0.197$ m is the best piece of teaching
in the chapter and is exactly right. Keep the honest empirical comparison in
`tab:ch19-rmse`: four scenarios, mean *and* median, a "lost" column, and the finding that
the EKF is indistinguishable from the UKF in the easy case and only 10-12 % worse when the
belief widens - textbooks routinely assert UKF superiority without this evidence. Keep the
new, careful sentence on systematic resampling (order-dependent, no general variance
guarantee, contrasted with stratified) - it is more accurate than most research papers on
the subject. Keep the whole treatment of angles: the explicit `wrap` map, the `\ominus`
operator, the wrapped sigma-point mean, the circular mean of a particle cloud, and the
pitfall that prices an unwrapped 6.2 rad innovation at 290 m. Keep the log-weight /
`N_eff` / sawtooth story and the occlusion example with the map as a likelihood - the
two-lobe cloud against a UKF mean sitting inside a building is the clearest possible
argument for particle filters and the right hand-off to the prediction-aware constraints of
Chapter 24. Keep the proofs as they stand (`thm:ch19-ut`'s cancellation argument and
`thm:ch19-systematic`'s interval-counting argument are both correct and short), the honest
"the UT is conservative here, not exact" clause added in round 1, the `Q(x)`-at-the-right-point
pitfall, the Joseph form in `alg:ch19-ekf`, the enlarged `fig:ch19-linearisation` and
`fig:ch19-particles` with their legends outside the axes, and the decision guide "which
filter for which intruder model", which is what a reader will actually come back to.

## Response to review (round 2)

All four required changes are applied. Build: `./build.sh ch19-nonlinear-filters`
finishes with no `!` errors, no overfull box wider than 15 pt and no undefined
reference or citation belonging to this chapter (latexmk's exit code 12 is
raised only by the expected cross-chapter `ch:chNN` / `ch:appA` references of a
single-chapter build). `python3 code/ch19_nonlinear_filters.py` passes its
self-test; `gen_ch19_compare.py`, `gen_ch19_particles.py` and
`gen_ch19_linearisation.py` were re-run and every number quoted in the text
still matches their output.

### Required change 1 - the N_eff sawtooth sentence (sec:ch19-pf-example)

Accepted; the reviewer is right and the old clause was false. The sentence now
reads: the filter resamples in 13 of the 29 steps; resampling resets the weights
to 1/N, but the next measurement re-concentrates them at once and N_eff is
plotted *before* resampling (`line~\ref{alg:ch19-pf:ess}`), so the curve climbs
back only to between 0.2N and 0.8N; that partial recovery is the healthy
signature, a curve pinned near N (the measurement-free band) means uninformative
data and one pinned near 1 a lost track. This is exactly what the printed
sequence 592, 934, 865, 772, 514, 2000, 1906, 432, 1033, 1653, 1424, 964, 1465
out of N = 2000 shows. The second pitfall box already said the same thing and
was checked against the new wording; it agrees verbatim ("a curve that stays
near N means uninformative measurements, one that stays near 1 a lost track").

### Required change 2 - text collisions in figures/ch19/idea.tex

Accepted, with one deviation from the suggested coordinates.
(i) Both column headings were raised to y = 1.75 (not 1.45): at 1.45 the second
line of the right-hand heading still touched the blue "tangent image of the
mean" node, which was verified on a 150 dpi render of the rebuilt page.
(ii) The row labels are now `\node[sbannot,text=black,anchor=east] at (-1.45,0)`
exactly as prescribed, so all three end 0.25 cm clear of the input ellipses.
(iii) The red "true mean" node was moved out from under the blue EKF ellipse: it
now sits below the banana (`anchor=north` at (7,-0.26)) with a short dotted
leader up to the cross, which keeps it clear of every other piece of text and of
the ellipse arc. A render of the rebuilt page confirms no two pieces of text
touch.

### Required change 3 - the concept figure did not show its own teaching point

Accepted; implemented as an equivalent change rather than literally.
The arc was widened to `arc (45:135:...)` / `arc (135:45:...)` instead of
50:130, because the centroid of the 50:130 sector is at y = 0.175 and the
resulting 0.22 cm bias is at the edge of visibility in print; the 45:135 sector
has its centroid at y = 0.113, giving a 0.29 cm gap. The markers are now:
blue EKF mean and its ellipse on the apex at (7,0.40); red cross at the true
centroid (7,0.11); orange fitted mean at (7,0.20), with a red dotted
"true-mean level" at y = 0.11 drawn across row (b) so the reader can see the
UT's correction without a second cross blurring into the orange dot. The map
exponent in the two `\foreach` loops of rows (b) and (c) is `28*\u` as
requested. The offset is annotated in row (a) by dotted guides from both markers
and a `<->` arrow labelled *bias*, as in `fig:ch19-linearisation`. The caption
now names the red cross, the bias arrow and the dotted true-mean level. Checked
on the rendered page: the blue mean is clearly above the red cross, the orange
mean lies between them and on the true-mean level, and the row-(c) banana clears
row (b) by about 0.4 cm.

### Required change 4 - duplicated numbers, and the page count

Accepted in all three places; every reason was kept and only figures already
printed in an adjacent table were cut.
(i) "Four things to notice": the six parenthesised mean-RMSE pairs and the
median 3.08 are gone; the 10 % and 12 % comparisons, the range/noise
explanation, the "both Gaussian filters survive" reason and the cost ratios stay.
(ii) sec:ch19-ukf-example: the sentence on the two standard deviations is
deleted and the update sentence is compressed to one clause; the sigma-point
straddling argument, the 0.21 m difference and the (1/2) P_psipsi d^2x'/dpsi^2 =
0.197 m check are untouched.
(iii) sec:ch19-variants: the auxiliary and regularised filters are removed from
the "Better particle filters" paragraph (the regularised filter is still named
where it belongs, in sec:ch19-resampling); Rao-Blackwellisation and the
three-dimensional state stay.

**Page count: the chapter is still 21 PDF pages (opening page plus 20 pages of
running head; pages 17-37 of `build/only-ch19-nonlinear-filters.pdf`), not 20.**
The three cuts remove about eight typeset lines and the last page of the chapter
carries roughly 30 lines of exercises, so a further half page would have to go.
Per the instruction "do not remove anything else to reach 20 pages", nothing
else was cut. If one more page is wanted, the cheapest content-preserving option
is to shorten `tab:ch19-comparison` or to let `fig:ch19-particles` drop from
6.5 cm to 5.5 cm high; both would need a reviewer's sign-off, as the round-1
protections cover that figure.

### Suggestions

* **Cost per step** - now quoted to one significant figure: "about 0.3 ms (EKF),
  0.5 ms (UKF) and 1.2 ms (particle filter)". On this machine the generator
  prints 0.260 / 0.455 / 1.168 ms, ratios 1 : 1.75 : 4.49, so "roughly
  1 : 1.8 : 4.5" is unchanged.
* **"no measurements" node in `particles.tex`** - moved inside the grey band it
  labels. Placed at the band's bottom-left corner (`anchor=south west` at
  (-38,36)) with `fill=white`, rather than the suggested (0,44), because (0,44)
  sits in the middle of the k = 15 particle cloud and would have hidden about
  twenty particles.
* **The k = 20 cloud hidden by its own cross** - the `mark=x` plot of the true
  positions is now drawn before the three clouds, and the legend was reordered to
  match. The stray seventh legend entry (a bare `$k=15$` that pgfplots silently
  dropped) was folded into "UKF mean ($k=15$)".
* **The 4.4 m label in `linearisation.tex`** - moved to (27,97.8) and given
  `inner sep=2pt`; the arrow head no longer touches the leading digit.
* **`lst:ch19-pf` breaking across a page** - the listing was moved ahead of the
  "Vectorising the particle filter" paragraph. It now sits whole on one page
  (page 34), so no split into two listings was needed.
* **The unverified 4 % at k = 15** - `occlusion_example()` now counts these
  particles, and the count contradicted the chapter, so the text was corrected:
  3.9 % of the particles are level with the building in x, and 3.4 % of the
  cloud sits inside the footprint carrying weight zero, waiting for the next
  resampling. They are dead bookkeeping, not a third hypothesis and not a
  north/south lobe. The whole example is now machine-checkable.
* **One more difficulty-1 exercise** - not added. The chapter is already one page
  over the ceiling and adding an exercise (plus its solution) pushes the wrong
  way; this is the one suggestion left open, and it should be taken together with
  a decision on the page budget.
* **`frontmatter/notation.tex` and `ch18-kalman-filter.tex`** - out of scope for
  this file, as the review notes. The symbol list (x, z, xhat^-, P^-, y, S, K,
  F, H, Q, R, N_eff, X_i, W^(m), W^(c), lambda, alpha, beta, kappa, wrap and the
  wrapped-difference operator) is repeated here so it can be handed on.

### What round 1 and round 2 protected, and is unchanged

The three-way EKF/UKF/PF structure and the single running scenario; the shared
step through `alg:ch19-ekf` and `alg:ch19-ukf` in `tab:ch19-ekf-trace` with the
0.21 m difference explained by the second-order term; `tab:ch19-rmse` with four
scenarios, mean and median, the "lost" column and its finding; the systematic-
resampling sentence; the complete treatment of angles including the 290 m
pitfall; the log-weight / N_eff / sawtooth story and the occlusion example; both
proofs; the "conservative here, not exact" clause; the Q(x) pitfall; the Joseph
form; the enlarged `fig:ch19-linearisation` and `fig:ch19-particles` with legends
outside the axes; and the decision guide.
