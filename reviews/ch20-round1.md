# Review of Chapter 20 (Trajectory Prediction) - round 1

Reviewed artefacts: `Overleaf/chapters/ch20-trajectory-prediction.tex` (1571 lines),
`Overleaf/figures/ch20/*.tex` (10 files), `Overleaf/code/ch20_prediction.py`,
`Overleaf/code/ch20_prediction_torch.py`, `Overleaf/code/figures/gen_ch20_results.py`,
`Overleaf/appendices/solutions/ch20-solutions.tex`,
`Overleaf/appendices/glossary/ch20-terms.tex`, `Overleaf/bib/ch20-extra.bib`,
`Overleaf/references.bib`, against `STYLE_GUIDE.md` §9 (A-H), `docs/specs/ch20.md` and
`docs/core-idea.txt` (Week 10).

Build: `./build.sh ch20-trajectory-prediction` exits 0, no `!` errors, **no overfull boxes
over 15 pt**, no undefined labels or citations belonging to this chapter (the `??` are
`ch:ch06`, `ch:ch12`, `ch:ch15`-`ch:ch18`, `ch:ch23`-`ch:ch25`, `ch:appB`, all
single-chapter-build artefacts). The log shows a `Runaway argument? ... File ended while
scanning use of \@writefile` on `build/chapters/ch10-ecbs.aux`; that is a stale aux file
from another chapter's build in the shared `build/` directory, not a ch20 defect - remove
`build/` and rebuild to confirm.

Code: `python3 code/ch20_prediction.py` passes its self-test in 1.4 s and finishes the
experiment in 37 s; `python3 code/figures/gen_ch20_results.py` regenerates all twelve
`figures/data/ch20-*.dat` files. **Every number quoted in the chapter reproduces exactly**
- both results tables, all per-subset ADE/FDE, `minADE_20 = 0.695`/`minFDE_20 = 1.415`,
the miss rates, the calibration fractions `0.850/0.807/0.787` and `0.762/0.632/0.544`, the
LSTM-TF "best epoch 3 of 13", the ~10 s training time, the hand-traced LSTM cell (all 13
entries of Table 7.1), the worked-example errors `1.34/3.35/5.40`, `1.41/3.47/5.55`,
`0.70/1.82/2.64`, the ellipse semi-axes `0.84`/`0.51` (= 2.448 x sigma 0.344/0.210), the
baselines-figure numbers (turn rate 0.166 rad/s, speed 2.93 m/s, CA 3.97 m vs tuned CV
1.48 m, naive k=1 at 0.78 m) and the attention weights (0.483, 0.003, 0.000). I also
re-derived Propositions 20.1, 20.2, the conditional-mean theorem, the carousel and the
complexity claims by hand; the algebra is right (see "What must be kept").

Length: the chapter body occupies printed pages 95-118 of
`build/only-ch20-trajectory-prediction.pdf`, i.e. **24 pages** - at the 24-page cap, but
6 pages above the spec's 16-18 target. I do **not** require cuts: nothing is missing and
almost nothing is padding. Concrete optional trims are listed under Suggestions, and you
will need one or two of them if you act on required change 7.

Counts: 8 figures (>= 4), 3 algorithms, 3 tables, 2 listings, 4 pitfall boxes, 41 unique
index entries (>= 15), 10 exercises graded 1/1/1/2/2/2/2/2/3/3, 18 distinct citations, all
resolving in `references.bib` or `bib/ch20-extra.bib`. Every "must cover" item of
`docs/specs/ch20.md` is present except the exact formula for the collision metric
(required change 5); all ten mandated citation keys are used; the Week-10 coding exercise
(`exr:ch20-coding`) and the attention-complexity derivation (`exr:ch20-attention-complexity`)
are both there.

## Verdict

**Minor revision.** The technical core is sound and the experiment is honest and fully
reproducible, but there are four local accuracy defects (a scaling law that contradicts the
chapter's own proposition, an unsupported "triples" claim, a circular pooling equation, an
RMS-versus-mean comparison), one missing formula the spec demands, two figure problems
(a self-contradicting caption and two finished figures that are never included), two symbol
clashes, and two citation misattributions. Every one of them is a local edit; none touches
the structure, the derivations or the results.

## Required changes

1. **Wrong scaling law, contradicts Proposition `thm:ch20-cv-noise`.**
   *Location:* §`sec:ch20-baselines`, paragraph "Constant velocity (CV)", line 268.
   *Problem:* "each measurement error of standard deviation $\sigma$ enters the velocity
   divided by $\dt$, and the position error at horizon $h$ grows like $h\sigma/\dt$". The
   $\dt$ cancels: the velocity error has standard deviation $\sigma\sqrt2/(k\dt)$ per axis
   and is multiplied by the look-ahead $h\dt$, so the position error grows like $h\sigma/k$.
   As written the expression has units of m/s and disagrees with the chapter's own
   `thm:ch20-cv-noise`, which gives $\E[e_h^2]=2\sigma^2[(1+h/k)^2+(h/k)^2]$ - no $\dt$
   anywhere.
   *Fix:* replace by "the velocity estimate inherits an error of standard deviation
   $\sigma\sqrt{2}/(k\dt)$ per axis, which the look-ahead $h\dt$ turns into a position error
   growing like $h\sigma/k$ - the step $\dt$ cancels (\cref{thm:ch20-cv-noise})".
   *Category:* A.

2. **Unsupported quantitative claim about constant acceleration.**
   *Location:* §`sec:ch20-baselines`, paragraph "Constant acceleration (CA)", line 283:
   "The second finite difference also triples the noise amplification."
   *Problem:* the factor is not 3. The CA prediction is the fixed combination
   $\hat{\pos}_{T+h}=c_0\meas_T+c_1\meas_{T-k}+c_2\meas_{T-2k}$ with $u=h/k$,
   $c_0=1+u+\tfrac12(u+u^2)$, $c_1=-(2u+u^2)$, $c_2=\tfrac12(u+u^2)$. At the chapter's own
   operating point ($h=12$, $k=3$, $u=4$) this is $(15,-24,10)$, so
   $\E[e_{12}^2]=2\sigma^2\cdot901$ against $2\sigma^2\cdot41$ for CV at the same $k$: an
   RMS factor of **4.7**, not 3. (The only quantity that triples is the squared norm of the
   difference stencil, $\lVert(1,-2,1)\rVert^2=6$ against $\lVert(1,-1)\rVert^2=2$.)
   *Fix:* state precisely what triples - "the second difference has stencil $(1,-2,1)$
   whose squared norm $6$ is three times the first difference's $2$, so the acceleration
   estimate is three times as noisy in variance; extrapolated to $h=12$ with $k=3$ this
   becomes an RMS position error $4.7$ times the CV one, which is why CA loses on straight
   flight in \cref{tab:ch20-results}" - or delete the sentence and keep only the measured
   comparison ($0.830$ m against $0.335$ m).
   *Category:* A.

3. **The social-pooling equation is circular as written.**
   *Location:* §`sec:ch20-social`, `eq:ch20-pooling`, line 616, and the caption/labels of
   `fig:ch20-social-pooling`.
   *Problem:* $\mat{H}_i[m,n,:]=\sum_{j\ne i}\mathbb{1}[\cdot]\vect{h}_j$ carries no time
   index, so the pooled input to agent $i$'s cell at step $t$ appears to depend on the
   neighbours' hidden states at step $t$, which are themselves being computed. Alahi et al.
   pool the neighbours' **previous** hidden states $\vect{h}^{j}_{t-1}$.
   *Fix:* write $\mat{S}_{i,t}[m,n,:]=\sum_{j\ne i}\mathbb{1}\bigl[\pos_{j,t-1}-\pos_{i,t-1}
   \in \text{cell}(m,n)\bigr]\,\vect{h}_{j,t-1}$ (see also required change 6 on the symbol
   $\mat{H}$), and add one sentence: "the states of the previous step are pooled, so every
   agent's cell can be stepped once per time step in any order." Update the figure's middle
   panel formula to match.
   *Category:* A.

4. **RMS prediction compared against a measured mean.**
   *Location:* §`sec:ch20-example`, paragraph "Straight flight: constant velocity wins",
   lines 970-973.
   *Problem:* "\cref{thm:ch20-cv-noise} predicts a root-mean-square final error of $1.25$~m,
   close to the measured $1.125$~m" - the table entry $1.125$ is a *mean* FDE, not an RMS,
   so the two quantities are not comparable. For an isotropic 2-D Gaussian error the mean
   norm is $\sqrt{\pi}/2$ times the RMS, i.e. $0.886\times1.251=1.11$ m.
   *Fix:* "\cref{thm:ch20-cv-noise} predicts a root-mean-square final error of $1.25$~m and
   hence a mean error of $\sqrt{\pi}/2\cdot 1.25 = 1.11$~m, against the measured $1.125$~m."
   *Category:* A.

5. **Collision-based metric stated without a formula, which the spec requires.**
   *Location:* §`sec:ch20-problem`, line 197 ("**Collision-based metrics** count the fraction
   of predicted trajectories ...").
   *Problem:* `docs/specs/ch20.md` requires "the METRICS with exact formulas: ADE ..., FDE,
   minADE_k/minFDE_k ..., and collision-based metrics". ADE, FDE, minADE/minFDE and the miss
   rate are all displayed; the collision metric is only prose, so the reader cannot implement
   it unambiguously (over which pairs? any step or the last? predicted-vs-true or
   predicted-vs-predicted?).
   *Fix:* add one displayed equation after that sentence, e.g.
   $\mathrm{CR}_{d_{\min}}=\frac{1}{|\mathcal{D}|}\sum_{n\in\mathcal{D}}\mathbb{1}\bigl[\exists
   h\le T_{\mathrm{pred}},\ \exists j\ne i:\ \lVert\hat{\pos}^{\,i}_{T+h}-\pos^{\,j}_{T+h}\rVert
   < d_{\min}\bigr]$, label it `eq:ch20-collision-rate`, and say in half a sentence that the
   predicted-versus-*true* variant measures the predictor while the predicted-versus-predicted
   variant measures a joint sampler's self-consistency.
   *Category:* B.

6. **Symbol clash: $H$ means three different things.**
   *Location:* `alg:ch20-baselines` line 236 (`\KwIn{... horizon $H$, ... filter matrices
   $\mat{F}, \mat{Q}, \mat{H}, \mat{R}$}`) and line 247 (`\PredKF{$\meas$, $H$, $\mat{F}$,
   $\mat{Q}$, $\mat{H}$, $\mat{R}$}`); `eq:ch20-pooling` line 616 ($\mat{H}_i$, the pooling
   tensor); the horizon $H$ throughout `alg:ch20-seq2seq`, `alg:ch20-train` and
   `thm:ch20-cv-error`.
   *Problem:* in a single `\KwIn` line "horizon $H$" and "filter matrices ... $\mat{H}$"
   sit next to each other, and the same letter carries a third meaning in the Social-LSTM
   section. In the compiled PDF the reader sees `KalmanExtrapolate(z, H, F, Q, H, R)`.
   *Fix:* (a) drop $\mat{H}$ and $\mat{R}$ from the `\KwIn` list and the `\PredKF` signature
   and write in line 11 of the algorithm "one predict and one update step of the
   constant-velocity Kalman filter of \cref{ch:ch18} with $\mat{F}$, $\mat{Q}$ of
   \cref{eq:ch20-q}, $\mat{H}=(\mat{I}\;\mat{0})$ and $\mat{R}=\sigma^2\mat{I}$";
   (b) rename the pooling tensor to $\mat{S}_i$ (not $\mat{P}$, which is the filter
   covariance) in `eq:ch20-pooling`, the surrounding prose, `fig:ch20-social-pooling` and
   `exr:ch20-calibration`(c).
   *Category:* F.

7. **Symbol clash: $M$ means three different things, twice inside one proposition.**
   *Location:* `def:ch20-lstm` ($M$ = LSTM input size), `eq:ch20-multihead` line 685 and
   `thm:ch20-complexity`(ii) ($M$ = number of heads), §`sec:ch20-multimodal` "Ensembles"
   line 824 ($M$ = number of ensemble members).
   *Problem:* `thm:ch20-complexity` states "(i) One LSTM step with $M$ inputs and $D$ hidden
   units ..." and "(ii) ... multi-head attention with $M$ heads of dimension $d/M$" - the
   same letter, two meanings, one statement. The solutions file already works around this by
   silently introducing $M_{\mathrm{in}}$
   (`appendices/solutions/ch20-solutions.tex`, `exr:ch20-attention-complexity`).
   *Fix:* keep $M$ for the LSTM input size; use $n_h$ for the number of heads in
   `eq:ch20-multihead`, `thm:ch20-complexity`(ii), the "What Transformers buy" paragraph and
   `exr:ch20-attention-complexity`; write "training five copies" (or $M_{\mathrm{ens}}$) in
   the Ensembles paragraph. Update `appendices/solutions/ch20-solutions.tex` to use $M$
   instead of $M_{\mathrm{in}}$ once the clash is gone.
   *Category:* F.

8. **`fig:ch20-results` caption contradicts itself and the data.**
   *Location:* caption of `fig:ch20-results`, line 951.
   *Problem:* "The learned predictors are below every baseline from the first step on, ...
   and the network trained on absolute coordinates is worse than constant velocity."
   LSTM-abs *is* a learned predictor and is plotted in the left panel; at $h=1$ it has
   $\mathrm{ADE}_1=0.175$ m against $0.123$ m for the tuned CV and $0.120$ m for the KF
   (`figures/data/ch20-results.dat`, columns `ade_abs`, `ade_cv`, `ade_kf`).
   *Fix:* "LSTM-NLL and LSTM-MSE are below every baseline from the first step on and the gap
   widens with $h$, while the same network trained on absolute coordinates is above every
   baseline at every horizon."
   *Category:* D.

9. **Two finished figures are never included in the chapter.**
   *Location:* `Overleaf/figures/ch20/integration.tex` and `Overleaf/figures/ch20/training.tex`;
   `code/figures/gen_ch20_results.py` writes `figures/data/ch20-training-nll.dat` and
   `ch20-training-tf.dat` that nothing consumes. Only 8 of the 10 figure files are
   `\inputfigure`d (lines 86, 316, 360, 462, 634, 754, 949, 1029).
   *Problem:* §4 of the style guide requires every figure to be tested by compiling the
   chapter; these two are never compiled, and both carry content the chapter currently
   asserts only in prose. `training.tex` is exactly the evidence for the exposure-bias claim
   ("LSTM-TF reaches a training loss far below the free-running model's, but its
   free-running validation ADE is best at epoch 3 and then drifts upwards", lines 985-990),
   and §`sec:ch20-drone` - the "where this fits" section - has **no figure at all**, which
   `integration.tex` (ORCA inflated disc / D* Lite cost region / MPC margin) supplies.
   *Fix:* include `ch20/integration` in §`sec:ch20-drone` right after `eq:ch20-inflated`,
   with a caption saying what to notice (the same ellipse sequence read three ways: a radius,
   a set of cells, a per-step margin); include `ch20/training` in the "Horizons, pitfalls and
   calibration" paragraph, with a caption naming the crossing point where teacher forcing's
   training loss keeps falling while its free-running validation ADE rises. If you would
   rather not spend the pages, delete the unused `.tex` file **and** the code in
   `gen_ch20_results.py` that writes its `.dat` files, so no untested figure remains in the
   repository. Do not leave them as they are.
   *Category:* D (with G for the dead data files).

10. **The chapter's own protocol rule 5 is not honoured by its own experiment.**
    *Location:* §`sec:ch20-problem` rule 5 ("repeat over seeds and report the spread") versus
    §`sec:ch20-example` and `tab:ch20-results`/`tab:ch20-horizon`.
    *Problem:* all reported numbers come from one seed, and the chapter never says so, right
    after telling the reader that reporting a single run is not honest. A reader following
    the text cannot tell whether the 0.821 vs 1.141 gap is bigger than the seed noise.
    *Fix:* one sentence in the paragraph that introduces the learned predictors: "All numbers
    below come from the one fixed seed of \cref{ex:ch20-dataset}; \cref{exr:ch20-coding} asks
    you to repeat the training over seeds and report the spread, which rule~5 of
    \cref{sec:ch20-problem} demands of any published comparison." Alternatively run three
    seeds and add a $\pm$ to the LSTM rows of `tab:ch20-horizon`.
    *Category:* C.

11. **Misattributed finding: the constant-velocity result is Schöller et al.'s, not the survey's.**
    *Location:* §`sec:ch20-motivation`, lines 41-46.
    *Problem:* "a large survey of motion prediction~\cite{rudenko2020human} and a widely
    discussed follow-up study~\cite{schoeller2020constant} found that a carefully tuned
    constant-velocity model matches or beats many published neural predictors on the standard
    pedestrian benchmarks". Rudenko et al. (IJRR 2020) is a taxonomy and does not run that
    comparison; the finding is Schöller et al. (RA-L 2020) alone. The two are contemporaries,
    so "follow-up" is also wrong.
    *Fix:* "a widely discussed study~\cite{schoeller2020constant} found that a carefully tuned
    constant-velocity model matches or beats many published neural predictors on the standard
    pedestrian benchmarks, and the survey of Rudenko et al.~\cite{rudenko2020human} places
    that result in the context of the field."
    *Category:* H.

12. **The survey is cited for work published after it.**
    *Location:* §`sec:ch20-transformer`, paragraph "Attention across agents", line 736.
    *Problem:* "the joint agent-time attention of the Transformers surveyed
    in~\cite{rudenko2020human} are the state of the art". Rudenko et al. was submitted in
    2019 and published in 2020; joint agent-time attention predictors post-date it, so the
    survey does not survey them.
    *Fix:* either reword without the citation - "and joint attention over agents *and* time
    steps, the natural generalisation of both, is the current state of the art for
    interaction-aware prediction" - or cite a paper that actually does it. Yuan, Weng, Ou and
    Kitani, "AgentFormer: Agent-Aware Transformers for Socio-Temporal Multi-Agent
    Forecasting", ICCV 2021, is the canonical choice; add it to `bib/ch20-extra.bib` **only**
    after verifying authors, title, venue and year, per §3 of the style guide.
    *Category:* H.

## Suggestions

* **Length.** The body is exactly at the 24-page cap and 6 pages above the spec's 16-18.
  If required change 9 pushes you over, these four cuts recover about a page and a half
  without losing content: (a) the paragraph "What Transformers buy and what they cost"
  repeats the complexity figures already in `thm:ch20-complexity` and column "Compute" of
  `tab:ch20-methods` - keep the data/compute/engineering triad in three sentences;
  (b) the closing paragraph of §`sec:ch20-example` ("The milestone of Week~10 asks
  whether ...") is a near-verbatim duplicate of the last bullet of the `summary` box - cut
  it and let the summary carry it; (c) the pitfall "A poorly tuned baseline, and an ADE
  without a horizon" restates the CV paragraph of §`sec:ch20-baselines` and rules 3 and 5 of
  the protocol - compress to four lines; (d) the "Rolling the decoder out" paragraph and the
  LSTM-TF discussion in §`sec:ch20-example` both explain exposure bias from scratch - the
  second can point back to the first.
* Point at the definitions rather than whole chapters: `\cref{def:ch02-covariance-ellipse}`
  in `eq:ch20-ellipse` (it defines exactly the $k\sigma$ ellipse you use),
  `\cref{def:ch02-minkowski-sum}` in `eq:ch20-inflated`, and
  `\cref{def:ch02-double-integrator}` where "the drone model of \cref{ch:ch02}" is mentioned
  in §`sec:ch20-variants`.
* `thm:ch20-conditional-mean`: "and by nothing else" should be "and, up to modification on a
  set of measure zero, by nothing else" - the proof already says "almost surely".
* §`sec:ch20-baselines`, Kalman paragraph: the step from `thm:ch20-conditional-mean` to "its
  mean is the minimum-mean-square-error predictor" needs the extra fact that the Kalman mean
  *is* the conditional mean under the linear-Gaussian model. Half a sentence (or a pointer to
  the corresponding result in `ch:ch18` once that chapter exists) closes the gap.
* `tab:ch20-results` bolds LSTM-abs in the "evasive, hidden" column, so the model the text
  calls a pitfall appears to win a column. Add a note to the caption that the four predictors
  are within noise of each other on those 60 trajectories, or leave that column unbolded.
* `ch:ch18` is still a placeholder file, so `alg:ch20-baselines` line 11 and the dronebox
  "Receives" paragraph cannot yet be checked for notation agreement ($\state$, $\meas$,
  $\mat{F}$, $\mat{Q}$, $\mat{P}$, `eq:ch20-q`). Re-check when ch18 lands; the same applies
  to the placeholder `frontmatter/notation.tex`, which does not yet list $\pos$, $\vel$,
  $\acc$, $\meas$, $\state$ or $\dt$.
* `exr:ch20-metrics-hand`, `exr:ch20-cell-hand`, `exr:ch20-pe`, `exr:ch20-protocol`,
  `exr:ch20-coding` and `exr:ch20-calibration` have no entries in
  `appendices/solutions/ch20-solutions.tex` (4 of 10, which matches ch13/ch19/ch21). At least
  `exr:ch20-metrics-hand` deserves one: it is the exercise that fixes the ADE/FDE/minADE
  definitions, and its answer is four lines.
* `\index{Kalman filter!extrapolation}` and `\index{Kalman extrapolation}` are two entries
  for one concept; keep the subentry form and drop the flat one.

## What must be kept

The experiment is the best thing in the chapter and must survive revision untouched in
substance. It is genuinely honest: it keeps the untuned CV row next to the tuned one, splits
the test set into straight / turn / visible-manoeuvre / hidden-manoeuvre, reports the two
deliberate failure models (LSTM-abs, LSTM-TF) as first-class rows rather than as anecdotes,
adds a calibration column that shows the learned model's own uncertainty to be badly
over-confident (54 % coverage where 95 % is claimed), and states flatly that constant
velocity wins on straight flight and that nothing beats anything on manoeuvres that have not
started. That is exactly the Week-10 milestone - "you can quantify whether learning actually
improves prediction" - answered with numbers and with its limits. I re-ran both scripts and
checked every quoted figure: they all reproduce, including the hand-traced LSTM cell of
`ex:ch20-cell`/`tab:ch20-cell` and the worked-example errors and ellipse semi-axes of
`fig:ch20-example`. Do not weaken this by dropping rows or subsets to save space.

The mathematics is correct where it matters and should be kept as it stands (modulo the four
local repairs above): `thm:ch20-cv-error` (including the $\tfrac12\lVert\acc\rVert\dt^2
(H+1)(2H+1)/6$ ADE and the $v\omega$ centripetal remark), `thm:ch20-cv-noise` with its
verified $1.25$/$0.65$/$0.23$ m table, the constant-acceleration midpoint correction
$\hat{\vel}=\vel_1+\tfrac12\hat{\acc}k\dt$ in `alg:ch20-baselines` (a detail most texts get
wrong), the conditional-mean theorem with its clean bias-variance proof and the mode-averaging
corollary that motivates the whole multimodality section, `thm:ch20-carousel` with its
honest caveat that the indirect paths through $\vect{h}_{t-1}$ are *not* protected, and all
three parts of `thm:ch20-complexity`. `eq:ch20-ellipse` ($k_{0.95}=2.448$) and
`eq:ch20-inflated` are right, and the chance-constraint argument in the dronebox does
correctly bound the per-step collision probability by $\delta$.

Keep the hand-set attention map in §`sec:ch20-transformer`: with
$\vect{k}_j=(\vect{x}_j,\lVert\vect{x}_j\rVert^2,1)$ and
$\vect{q}_i=(\vect{x}_i,-\tfrac12,-\tfrac12\lVert\vect{x}_i\rVert^2)\sqrt{d_k}/\ell^2$ the
scaled dot product really is $-\lVert\vect{x}_i-\vect{x}_j\rVert^2/(2\ell^2)$ - I verified
the algebra - so `fig:ch20-attention` shows a real attention pattern with reproducible
numbers and no training at all. That is a rare and very good pedagogical device.

Keep also: the five-rule evaluation protocol (it is the most useful page in the chapter for
a student about to publish a comparison); the agent-centred frame `eq:ch20-frame` together
with the residual-over-constant-velocity read-out on line
`alg:ch20-seq2seq:readout`, and the observation that an untrained network then *is* the CV
model; the three decoder modes in one algorithm; the four pitfall boxes, each of which is
backed by a measured number rather than by an assertion; `tab:ch20-methods` as a decision
table; the ten exercises with their 3/5/2 difficulty spread and the four carefully worked
solutions (I checked the arithmetic in all four - `0.04h^2`, $S=k(k+1)(k+2)/12=42$, the
$1.33$ line-fit factor, $NT>192$ and $16\pi(1-\pi)$ are all correct); and the citation set -
all 18 keys resolve, the LSTM/forget-gate/BPTT attributions are split correctly between
Hochreiter & Schmidhuber 1997, Gers et al. 2000 and Werbos 1990, and I could vouch for the
authors, venue and year of every entry.
