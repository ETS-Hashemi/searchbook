# Review of Chapter 20 (Trajectory Prediction) - round 2

Reviewed artefacts: `Overleaf/chapters/ch20-trajectory-prediction.tex` (1626 lines),
the ten figure files in `Overleaf/figures/ch20/`, `Overleaf/code/ch20_prediction.py`
(1007 lines), `Overleaf/code/ch20_prediction_torch.py`,
`Overleaf/code/figures/gen_ch20_results.py`, the twelve `figures/data/ch20-*.dat`,
`Overleaf/appendices/solutions/ch20-solutions.tex`,
`Overleaf/appendices/glossary/ch20-terms.tex`, `Overleaf/bib/ch20-extra.bib` and
`Overleaf/references.bib`, against `STYLE_GUIDE.md` §9 (A-H), `docs/specs/ch20.md`
and Week 10 of `docs/core-idea.txt`. Round-1 review and the reviser's response were
read first; each of the twelve round-1 required changes was checked in the source.

**Round-1 items.** All twelve are applied. I verified in the source: the CV noise
sentence now reads $\sigma\sqrt2/(k\dt)$ times $h\dt$ with the remark that $\dt$
cancels (1); the CA sentence now states the stencil norms $6$ against $2$ and the
$4.7\times$ RMS factor, which I recomputed - with $u=h/k=4$ the CA stencil is
$(15,-24,10)$, $\lVert\cdot\rVert^2 = 901$ against $41$ for CV, $\sqrt{901/41} = 4.69$
(2); `eq:ch20-pooling` is now $\mat{S}_{i,t}[m,n,:]=\sum_j \mathbb{1}[\cdot]\vect{h}_{j,t-1}$
with the "previous step" sentence, and the middle panel of `social-pooling.tex` matches
(3); the RMS-to-mean conversion $\sqrt\pi/2\cdot1.25 = 1.11$ against the measured
$1.125$ is correct (4); `eq:ch20-collision-rate` is present with the
predicted-vs-true / predicted-vs-predicted sentence (5); `\PredKF` is now
`KalmanExtrapolate(z, H, F, Q)` and $\mat{H},\mat{R}$ are named in line 11 only (6);
$n_h$ is used for heads in `eq:ch20-multihead`, `thm:ch20-complexity`(ii), its proof,
`exr:ch20-attention-complexity` **and** in `ch20-solutions.tex` (7); the
`fig:ch20-results` caption was rewritten (8 - but see required changes 1 and 2);
`ch20/integration` and `ch20/training` are both included and compile (9); the
one-seed sentence and the three-seed request in `exr:ch20-coding`(a) are in place (10);
Schöller is credited with the constant-velocity finding and Rudenko with the context
(11); the "state of the art" sentence no longer cites the survey (12).

**Build.** `./build.sh ch20-trajectory-prediction` writes a complete 48-page PDF, no
overfull box above 15 pt, and the only undefined references are cross-chapter
(`ch:ch18`, `ch:ch24`, `ch:appA`, `ch:ch12`, `ch:ch25` - chapters excluded from a
single-chapter build). The script reports status 12 because of two *other* chapters'
`.aux` files: `build/chapters/ch11-mstar-push-and-swap.aux` line 133/134 (the caption
of `fig:ch11-expansions`, with `M\textsuperscript {*}\xspace` and a `` ``all $k$ agents'' ``
quotation inside `\@writefile`/`\@newl@bel`) and `build/chapters/ch02-toolbox.aux`
(a runaway `{sec: `) trigger `File ended while scanning use of \@writefile`. Nothing in
ch20 causes it and no ch20 label is lost (`def:ch02-covariance-ellipse`,
`def:ch02-minkowski-sum`, `def:ch02-double-integrator` all resolve). Report it to the
book editor with ch11/ch02, do not chase it here.

**Code.** `python3 code/ch20_prediction.py`: self-test passes in 1.5 s, experiment
finishes in 30.8 s, exit 0. **Every number in the two result tables reproduces
exactly**, as do `minADE_20 = 0.695`/`minFDE_20 = 1.415`, all eight miss rates, the
calibration triples `0.850/0.807/0.787` and `0.762/0.632/0.544`, LSTM-TF's "best epoch
3 of 13" and val ADE `0.99`, the training times ("about ten seconds": 3.3-9.9 s), the
$\approx 9000$ weights ($2\times(128\times34+128)+132 = 9092$), the subset sizes
$317/236/187/60$, and the derived percentages ($88\%$, $25\%$, $28\%$, $0.32$ m). I
recomputed the whole of `tab:ch20-cell` from the weights of `ex:ch20-cell`
independently: all 22 numbers agree to four decimals. From the `.dat` files I
re-derived the worked-example errors ($1.337/3.353/5.399$ CV, $1.414/3.469/5.551$ KF,
$0.704/1.824/2.636$ LSTM), the $h=12$ ellipse semi-axes ($0.841$, $0.514$), the
attention row of drone A ($0.514$ self, $0.483$ B, $0.0035$ C, $0.000$ D) and the
baselines-figure final errors ($3.97$ m CA, $1.479$ m tuned CV, $0.784$ m naive CV):
all match the text. Both listings are verbatim copies of the source files.

**Counts.** 10 figures (all `\inputfigure`d and all `\cref`ed), 3 algorithms, 4 tables,
2 listings, 4 pitfall boxes, 40 unique index entries, 10 exercises graded
1/1/2/2/2/2/2/1/3/3, 5 worked solutions, 15 glossary terms, 18 citations - every key
resolves and I can vouch for the authors, title, venue and year of all of them
(Gers 2000 *Neural Computation* 12(10):2451-2471; Werbos 1990 *Proc. IEEE*
78(10):1550-1560; Schöller 2020 RA-L 5(2):1696-1703; Giuliari ICPR 2021:10335-10342;
Zhu & Alonso-Mora RA-L 2019 4(2):776-783 are all correct as entered). Every "must
cover" item of `docs/specs/ch20.md` is present, all ten mandated citation keys are
used, and the Week-10 coding exercise plus the attention-complexity derivation are
both there.

**Length.** The chapter body occupies PDF pages 18-42 of
`build/only-ch20-trajectory-prediction.pdf`, i.e. **25 pages**, one over the 24-page
cap (the reviser's own "open point"). Required change 5 names the padding to cut; it
touches no content.

## Verdict

**Minor revision.** The chapter is in very good shape: the mathematics, the
experiment, the code and the citations all check out, and the round-1 repairs were
made properly. Six things are left, and every one of them is a local edit. Three are
statements about the experiment that the chapter's own data contradict (all three in
the `fig:ch20-results` caption, two of them introduced or left standing by the round-1
caption rewrite), one is a figure that mixes the validation and test splits in a single
panel, one is notation, and one is the last page of padding.

## Required changes

1. **`fig:ch20-results` caption overstates the gain on visible manoeuvres as "half";
   the summary repeats it.**
   *Location:* caption of `fig:ch20-results`, line 980-981 ("on turns and on visible
   evasive manoeuvres the LSTM halves the error"); `summary` box, line 1491 ("by half
   on turns and visible manoeuvres").
   *Problem:* on the *turn* subset the reduction really is a half ($1.125 \to 0.549$~m,
   $-51\%$), but on the *visible evasive* subset it is a third ($2.351 \to 1.585$~m,
   $-33\%$). The body text (line 1013) states the visible-manoeuvre numbers correctly,
   so the caption and the summary are the only places where the number is wrong.
   *Fix:* caption: "on turns the LSTM halves the error and on visible evasive
   manoeuvres it removes a third of it"; summary bullet: "beats the tuned baselines by
   $28\,\%$ overall, halves the error on turns and removes a third of it on visible
   manoeuvres".
   *Category:* A.

2. **`fig:ch20-results` caption: "On straight flight CV wins at every horizon" is
   false for $h \le 7$, and the right panel shows the crossing.**
   *Location:* caption of `fig:ch20-results`, line 979-980; supporting text
   §`sec:ch20-example`, paragraph "Straight flight: constant velocity wins"
   (line 986 ff.); `keyidea` box, line 121-128 ("nothing beats it on straight flight").
   *Problem:* in `figures/data/ch20-results.dat` the straight-subset columns are
   $\mathrm{ADE}_h$: CV(tuned) $0.0991, 0.1194, 0.1403, 0.1614, 0.1828, 0.2043, 0.2260$
   and LSTM-NLL $0.0769, 0.0904, 0.1072, 0.1273, 0.1513, 0.1797, 0.2124$ for
   $h = 1,\dots,7$ - the LSTM is *ahead* by up to $22\,\%$ over the first $1.4$~s and
   only loses from $h = 8$ on ($0.2476$ against $0.2490$), ending $0.09$~m behind at
   $h = 12$. The two green curves in the right panel visibly cross at $h \approx 7.5$,
   so a reader who looks at the figure is told the opposite of what the figure shows.
   *Fix:* caption: "On straight flight the two curves cross at $h \approx 8$: the LSTM
   is marginally ahead over the first $1.4$~s and the tuned CV wins from there on,
   ending $0.09$~m ahead at $2.4$~s." Add half a sentence to the "Straight flight"
   paragraph after the first sentence: "the advantage is a long-horizon one - up to
   $h = 7$ the two are within $2$~cm of each other and the LSTM is slightly ahead."
   In the `keyidea` box write "nothing beats it on straight flight at the long
   horizons that set the safety margin".
   *Category:* A.

3. **`fig:ch20-results` caption: "the same network trained on absolute coordinates is
   above every baseline at every horizon" fails at the last step.**
   *Location:* caption of `fig:ch20-results`, line 977-979.
   *Problem:* at $h = 12$, `ade_abs` $= 1.3149$ is *below* `ade_ca` $= 1.3216$ (both in
   `figures/data/ch20-results.dat`); the LSTM-abs and CA curves cross between $h = 11$
   and $h = 12$, exactly at the right-hand edge of the left panel. LSTM-abs is above
   CV($k{=}1$), CV(tuned) and KF at every horizon, so only the "every baseline" is
   wrong.
   *Fix:* "while the same network trained on absolute coordinates stays above both
   constant-velocity baselines and the Kalman filter at every horizon (and above
   constant acceleration until the last step)".
   *Category:* D.

4. **`fig:ch20-training` compares a validation curve with a test-set constant, in the
   chapter that teaches the split protocol.**
   *Location:* `Overleaf/figures/ch20/training.tex`, lines 27-29 (`\addplot[sbBlue,
   thick,dashed,domain=0:41,samples=2] {1.141};` with the legend entry "CV (tuned) on
   the test split"), and the caption of `fig:ch20-training`, line 1054-1055 ("The
   dashed line is the tuned CV baseline").
   *Problem:* the right panel's $y$-axis is the *validation* ADE, epoch by epoch,
   while the dashed reference is the tuned CV's $\mathrm{ADE}_{12}$ on the *test*
   split ($1.141$ from `tab:ch20-results`). Rule 4 of the chapter's own protocol tells
   the reader never to let the test set into model selection, and this panel invites
   exactly the forbidden reading ("the LSTM passes CV at epoch $n$"). The value is also
   hard-coded in the figure, so it will silently go stale if the experiment is rerun.
   *Fix:* have `code/figures/gen_ch20_results.py` write the tuned CV's ADE on the
   **validation** split as an extra column (or a one-row `ch20-training-cv.dat`), plot
   that with `\addplot table[...]`, and set the legend entry to "CV (tuned),
   validation". Update the caption to "The dashed line is the tuned CV baseline on the
   same validation split." If you prefer to keep the test number, say so in the caption
   and add "shown only for scale; nothing in this figure is selected with it".
   *Category:* D (with G for the hard-coded constant).

5. **One page over the cap; cut the repetition, not the content.**
   *Location:* whole chapter (PDF pages 18-42 = 25 pages against the 24-page cap).
   *Problem:* the body is one printed page too long. It is not over-long because
   anything is missing-in-reverse: four passages repeat material that is said properly
   elsewhere.
   *Fix:* make these four cuts, which together recover about one page and remove no
   result, proof, figure, table or exercise.
   (a) §`sec:ch20-intuition`, lines 98-120: the three paragraphs "First, the past
   constrains the future / Second, the past reveals the manoeuvre / Third, the future
   is uncertain" restate §`sec:ch20-motivation` lines 36-52 and are restated again by
   the `keyidea` box that immediately follows (lines 121-128). Compress to one
   paragraph of five or six lines that names the three facts and points at
   `fig:ch20-idea`; keep the box unchanged.
   (b) §`sec:ch20-motivation`, lines 65-76: the section-by-section roadmap duplicates
   the table of contents of the chapter. Keep two sentences (the experiment in
   §`sec:ch20-example` and the properties in §`sec:ch20-properties` are worth
   announcing), drop the rest.
   (c) §`sec:ch20-example`, paragraph "Horizons, pitfalls and calibration": the
   sentence on LSTM-abs ("LSTM-abs is worse than the tuned CV on every subset ... and
   it does not") repeats the pitfall box *Predicting in absolute coordinates* almost
   word for word, including the $1.315$ against $1.141$ and the $1600$ examples. Cut it
   from the paragraph and let the pitfall box carry it (add "see the pitfall box on
   p.~\pageref{...}" if you want the pointer).
   (d) `dronebox`, paragraph "Study plan" (lines 1475-1479): the Week-10 task and
   milestone are already stated in §`sec:ch20-motivation` lines 54-58 and in the last
   summary bullet. Keep the first clause ("Week~10 of \cref{ch:appA}") and the
   research-direction sentence, drop the restatement of the exercise and the milestone.
   *Category:* G.

6. **$k$ denotes the decoder step in one algorithm and the velocity window in the
   one before it, while the chapter defines $h$ as the horizon step.**
   *Location:* `alg:ch20-seq2seq`, lines 501-506 (`\For{$k = 1, \dots, H$}`,
   $\vect{\mu}_k$, $\log\vect{\sigma}_k$, $\vect{y}_k$, $\vect{\sigma}_k$) and the
   paragraph "Rolling the decoder out", lines 539-544 ("the decoder's input at step
   $k$", $\vect{\mu}_{k-1}$, $\vect{y}_{k-1}$); against `def:ch20-problem`
   ("the integer $h \in \{1,\dots,T_{\mathrm{pred}}\}$ is the **horizon step**") and
   `alg:ch20-baselines`, where $k$ is the velocity window and the loop index is $h$.
   *Problem:* two facing algorithms use $k$ for two different things, and the second
   uses it for the quantity the chapter has just named $h$; $\vect{\sigma}_k$ in
   `alg:ch20-seq2seq` and $\vect{\sigma}_h$ in `eq:ch20-nll` are the same object under
   two names. This is the same class of defect as round-1 items 6 and 7.
   *Fix:* rename the decoder index to $h$ throughout `alg:ch20-seq2seq` (loop,
   $\vect{\mu}_h$, $\vect{\sigma}_h$, $\vect{y}_h$, the `\KwOut` line) and in the
   "Rolling the decoder out" paragraph ($\vect{\mu}_{h-1}$, $\vect{y}_{h-1}$). Nothing
   else in that algorithm uses $k$, so the edit is mechanical.
   *Category:* F.

## Suggestions

* §`sec:ch20-transformer`: $\mat{Q}$ is the query matrix in `def:ch20-attention` and
  the process-noise covariance in `eq:ch20-q`. Both are standard in their own fields
  and they are far apart, so I would not rename either - but one parenthesis in
  `def:ch20-attention` ("$\mat{Q}$ here is the query matrix, not the process noise of
  \cref{eq:ch20-q}") costs a line and removes the double take.
* Similarly $d_h$ (inflated radius, `eq:ch20-inflated`), $d_k$/$d_v$ (attention
  dimensions) and $d_{\min}$ (`eq:ch20-collision-rate`) are three different $d$'s with
  index-like subscripts; consider $d^{\mathrm{safe}}_h$ for the radius.
* §`sec:ch20-example`, hidden-manoeuvre paragraph: "every predictor scores
  $1.6$-$1.8$~m and nothing can do better" is a shade stronger than the data
  ($1.598$ against $1.696$ for the tuned CV at $h=12$, and the LSTM is $6$-$26\,\%$
  ahead at *every* horizon on that subset). "No predictor is ahead by more than the
  noise of $60$ trajectories" would be exact, and it is what `tab:ch20-results`'s
  caption already says.
* §`sec:ch20-baselines`, CA paragraph: the $4.7\times$ factor is CA($k{=}3$) against
  CV($k{=}3$) at the final step, while the measured pair quoted next to it
  ($0.830$ against $0.335$) is an ADE against the *tuned* CV($k{=}2$). One clause -
  "at the same window $k = 3$ and at $h = 12$" - stops a careful reader from trying to
  reconcile $4.7$ with $2.5$. (The predicted mean FDE at $k=3$, $1.88$~m, in fact
  matches the measured $1.869$~m almost exactly; that would be an even better sentence.)
* Solutions exist for 5 of 10 exercises. `exr:ch20-pe` (the $\mat{M}_\delta$ rotation)
  and `exr:ch20-protocol` (the six protocol violations) would each take four lines and
  are the two a lone reader is most likely to get half-right.
* `frontmatter/notation.tex` is still a 13-line placeholder, so $\pos$, $\vel$, $\acc$,
  $\meas$, $\state$, $\dt$ cannot be checked against the book table; `ch:ch18` is still
  absent, so `alg:ch20-baselines` line 11 and the dronebox "Receives" paragraph cannot
  be checked for agreement with the tracker's notation. Re-check both when they land.
* If required change 5 leaves you short, `tab:ch20-methods` can move from
  `\footnotesize` to a two-column layout without losing a row, and
  `fig:ch20-seq2seq`+`fig:ch20-lstm-cell` can share a page.

## What must be kept

The experiment remains the best thing in the chapter and must survive untouched in
substance. I re-ran both scripts from scratch: every quoted number reproduces, and the
reporting is genuinely honest - the untuned CV row stands next to the tuned one, the
test set is split into straight / turn / visible / hidden, the two deliberate failure
models (LSTM-abs, LSTM-TF) are first-class rows rather than anecdotes, the calibration
column exposes the learned model's over-confidence ($54\,\%$ coverage where $95\,\%$ is
claimed), and the chapter says plainly that constant velocity wins on straight flight
at the long horizons and that nothing beats anything on manoeuvres that have not
started. That is the Week-10 milestone answered with numbers *and* with its limits. Do
not drop rows, subsets or the calibration column to save space.

The mathematics is correct and should stand as written: `thm:ch20-cv-error` with its
$\tfrac12\lVert\acc\rVert\dt^2(H+1)(2H+1)/6$ ADE and the $v\omega$ centripetal remark;
`thm:ch20-cv-noise` (I re-derived the $1.25/0.65/0.23$~m table); the midpoint
correction $\hat{\vel}=\vel_1+\tfrac12\hat{\acc}k\dt$ in `alg:ch20-baselines`, which
most texts get wrong; `thm:ch20-conditional-mean` with its bias-variance proof and the
mode-averaging corollary; `thm:ch20-carousel` with its honest caveat about the indirect
paths; all three parts of `thm:ch20-complexity`; `eq:ch20-ellipse` with
$k_{0.95}=2.448$; and the chance-constraint argument in the dronebox, which does
correctly bound the per-step collision probability by $\delta$ (a collision needs
$\lVert X-\hat\pos\rVert \ge k_p\sqrt{\lambda_{\max}}$, i.e. the true position outside
the $p$-ellipse).

Keep the hand-set attention map of §`sec:ch20-transformer`: with
$\vect{k}_j=(\vect{x}_j,\lVert\vect{x}_j\rVert^2,1)$ and
$\vect{q}_i=(\vect{x}_i,-\tfrac12,-\tfrac12\lVert\vect{x}_i\rVert^2)\sqrt{d_k}/\ell^2$
the scaled dot product is exactly $-\lVert\vect{x}_i-\vect{x}_j\rVert^2/(2\ell^2)$, and
the weights in `figures/data/ch20-attention.dat` are a real attention pattern with
reproducible numbers and no training. Keep the hand-traced LSTM step
(`ex:ch20-cell`/`tab:ch20-cell`) - I recomputed all 22 entries independently and they
are right to four decimals. Keep the five-rule evaluation protocol, the agent-centred
frame `eq:ch20-frame` with the residual-over-constant-velocity read-out (and the remark
that an untrained network then *is* the CV model), the three decoder modes in one
algorithm, the four pitfall boxes (each backed by a measured number), `tab:ch20-methods`
as a decision table, the two new figures added in round 1 - `fig:ch20-integration`
("one prediction, three consumers") and `fig:ch20-training` (exposure bias, measured) -
the ten exercises with their 3/5/2 difficulty spread, and the citation set, which is
complete, correctly attributed (LSTM / forget gate / BPTT split between Hochreiter &
Schmidhuber, Gers et al. and Werbos; the constant-velocity finding to Schöller et al.)
and free of anything I cannot vouch for.
