# Review of Chapter 24 (The Hybrid Collision-Avoidance Architecture) - round 2

## Verdict

**Minor revision.**

Round 1's eight required changes were addressed and I verified each one against the
current source, the current build and a fresh run of the code. Seven are fully resolved
(1, 2, 3, 4, 5, 6, 8); one, the notation rename of the waypoint index (round-1 item 7), is
resolved in the chapter, the glossary and the exercises but **not** in the solutions
appendix, where the old `$k$`, `$k_0$` and `$t_k$` survive in the solution to
`exr:ch24-offsets`. That is required change 4 below.

The chapter is otherwise in very good shape. It builds with status 0, no `!` errors, no
undefined labels or citations of its own (the `??` are cross-chapter, as expected in a
single-chapter build), and the only overfull box inside the chapter is 13.23 pt, below the
style guide's 15 pt bar. The chapter body is now **24 pages** (PDF pages 27-50 of
`build/only-ch24-hybrid-architecture.pdf`), exactly at the bar, down from 25; the four cuts
prescribed in round 1 were all made and no required content was lost, so I require **no
further cuts**. Six figures, five tables, four algorithms, two listings (both verbatim from
`code/ch24_hybrid.py` modulo de-indentation, 21 and 38 lines), five pitfall boxes, 19+
unique index entries, eight graded exercises including the Week-12 capstone, seven of eight
solutions, and all eleven citation keys required by `docs/specs/ch24.md` present in
`references.bib` (I checked `zhu2019chance` and `honig2018trajectory` in detail; both are
correct as to authors, title, venue, volume, pages and year). Every "must cover" item of the
spec and every element of the Week-12 capstone in `docs/core-idea.txt` is present.

I re-derived the numbers. `python3 code/ch24_hybrid.py` runs in 1.3 s and passes its
self-tests (201 cycles); `python3 code/figures/gen_ch24_scenario.py` regenerates the data
and the two generated TikZ files. The CBS plan (2 CT nodes, costs 13/9/13, $\sumcost=35$,
$\makespan=13$, B's wait at $(6,3)$ at $t=5,6$), the trigger at $t=3.5$ (sep 1.53, inflation
0.86, margin $-0.03$, estimate $(10.37,4.35)$, **velocity $(-0.61,0.04)$** - round-1 item 1
fixed), the eight reconnection candidates at $t=9.1$ (seven "too fast", $j=13,\Delta=1$
"segment blocked" - round-1 item 6 fixed), the two replans and their cell paths, the 72
blocked cells (70 predicted + 2 teammates), the minimum separations 1.20/1.98/2.25 and 0.80,
the drift 3.22, the formation peak 2.10 at $t=11$, the longest link 7.33 m, the two
infeasible ORCA cycles, the arrivals 10/18/20 and $\sumcost=48$ (a $37\,\%$ rise, 13 extra
steps split 7/5/1) are all reproduced exactly. `k_comm=1.0` is in `PARAMS` and
`preferred_velocity` implements `eq:ch24-comm` literally (round-1 item 3 fixed); the false
clause in the proof of Proposition 24.4 is gone and the replacement sentence is correct
(round-1 item 4 fixed); $a_{\max}=1$ is in Example 24.1 and in Table 24.4 (round-1 item 5
fixed). I also re-verified Proposition 24.2's proof line by line (the case analysis on the
integer cross product is complete and the $\ell/\sqrt2$ bound is tight) and the derivation
$\kappa_p=\sqrt{-2\ln(1-p)}$ with 2.4477 and 3.0349.

Four defects block acceptance. Two are accuracy defects a reader can hit with a calculator:
a process-noise intensity that is off by a factor of ten between Example 24.1 and the
variance arithmetic that follows it, and a horizon that the chapter's own inequality says is
0.1 s too short. The other two are a free symbol in pseudocode and the stale notation in the
solutions file. All four are local edits; nothing structural changes and no number in the
worked scenario needs to move.

## Required changes

1. **`sec:ch24-uncertainty` (line 835) together with Example 24.1 (`ex:ch24-scenario`,
   line 870) - the process-noise intensity is inconsistent by a factor of ten, so the
   variances quoted in the text cannot be reproduced from the parameters the chapter gives
   (category A).**
   Example 24.1 says the intruder is "tracked by the constant-velocity Kalman filter of
   `\cref{ch:ch18}` with process-noise intensity $q = 0.05$".
   `Overleaf/chapters/ch18-*.tex` (eq. at line 270) defines that model as
   $\mat{Q}=q\begin{psmallmatrix}\Delta t^3/3 & \Delta t^2/2\\ \Delta t^2/2 & \Delta t\end{psmallmatrix}$
   with $q$ the white-noise-acceleration *intensity* (spectral density). But
   `Overleaf/code/ch24_hybrid.py` (lines 337-339) builds
   `Q = q * [[d4,0,d3,0],[0,d4,0,d3],[d3,0,d2,0],[0,d3,0,d2]]` with
   `d2, d3, d4 = dt**2, dt**3/2, dt**4/4`, which is the *discrete* white-noise-acceleration
   (piecewise-constant-acceleration) model with acceleration variance $\sigma_a^2 = q$, not
   ch18's model. Its equivalent continuous intensity is $\sigma_a^2\,\Delta t = 0.005$.
   Consequently the sentence at line 835 - "the extrapolated position variance is
   $\sigma_p^2 + 2s\,\sigma_{pv} + s^2\sigma_v^2 + \tfrac13 q s^3$ ... a variance of
   $0.004, 0.019, 0.056, 0.124$ m$^2$ at $s = 0,1,2,3$ s, of which $0.054$ ... is the
   velocity term and $0.045$ the cubic one" - only works with $q = 0.005$: the quoted cubic
   term is $\tfrac13 (0.005)(27) = 0.045$. A reader who takes the $q = 0.05$ of Example 24.1
   gets $0.45$ m$^2$ for the cubic term and a total of $0.53$ m$^2$ at $s = 3$ s instead of
   $0.124$, hence $\sigma(3) = 0.73$ m instead of $0.35$ m and an inflation of $1.79$ m
   instead of $0.86$ m - which would also destroy the trigger arithmetic of
   `sec:ch24-horizon` and `fig:ch24-horizon`.
   *Fix* (keeps every number in the chapter unchanged): (a) in Example 24.1 write "tracked
   by the constant-velocity Kalman filter of `\cref{ch:ch18}`, in its discrete
   white-noise-acceleration form with acceleration variance $\sigma_a^2 = 0.05$\,m$^2$/s$^4$
   per axis, equivalent to a continuous intensity $q = \sigma_a^2\,\dt = 0.005$\,m$^2$/s$^3$";
   (b) in `sec:ch24-uncertainty` name the constant used in the cubic term, e.g. "...
   $+\tfrac13 q s^3$, with $q = 0.005$\,m$^2$/s$^3$ for the tracker of Example 24.1"; (c) fix
   the docstring of `IntruderTracker` in `code/ch24_hybrid.py` (line 330), which says
   "white-noise-acceleration process noise of intensity q" while the matrix below it is the
   discrete form - say "with acceleration variance q per axis (discrete white-noise
   acceleration; equivalent continuous intensity q*dt)". Do **not** change the code's `Q`:
   that would move every number in the worked scenario.

2. **`sec:ch24-horizon`, line 469 - the scenario's horizon does not satisfy the second
   condition of `eq:ch24-tauh` in the form the chapter itself calls binding (category A).**
   The text reads "In the scenario $v_{\max}/a_{\max} = 1.5$\,s, $\ttc = 3$\,s and
   $\kappa_p\sigma(3\,\mathrm{s}) = 0.86$\,m, so $\tau_h = 3$\,s satisfies the first two
   conditions". The second condition is `eq:ch24-tauh`, which has two forms:
   $\tau_h \ge \dt + v_{\max}/a_{\max} = 0.1 + 1.5 = 1.6$\,s (stop) and
   $\tau_h \ge \dt + 2v_{\max}/a_{\max} = 0.1 + 3.0 = 3.1$\,s (reversal). With $\tau_h = 3$\,s
   the reversal form fails by $0.1$\,s. The book treats the reversal form as a genuine
   constraint elsewhere: `exr:ch24-horizon`(a) asks for it explicitly, and the solution to
   `exr:ch24-dwa` says "with a double integrator ... the reversal form of `\cref{eq:ch24-tauh}`
   becomes the binding constraint on $\tau_h$".
   *Fix:* replace "satisfies the first two conditions" with a sentence that says which form is
   met, e.g. "so $\tau_h = 3$\,s clears the hand-over condition and the stop form of
   `\cref{eq:ch24-tauh}` ($1.6$\,s) with room to spare, and falls $0.1$\,s short of the
   reversal form ($3.1$\,s); the single-integrator drones of the scenario are never asked to
   reverse, but a double-integrator drone would need $\tau_h \ge 3.1$\,s
   (`\cref{exr:ch24-dwa}`)". (Raising $\tau_h$ to $3.1$ instead would change the run and is
   not recommended.)

3. **`alg:ch24-reconnect`, function `\HybridSegment`, lines 537-538 - a free symbol $t$ in
   pseudocode (category C).**
   `\HybridSegment` is declared with the arguments $(\pos, t_a, \vect{w}, t_b,
   \text{prediction}, \text{teammates})$, but line~`alg:ch24-reconnect:pred` evaluates the
   prediction at "$h = (t' - t)/\dt$" and line~`alg:ch24-reconnect:mate` at
   "$\tilde{\pos}_m(t' - t)$", using a $t$ that is not an argument of the function. A reader
   implementing the algorithm from the pseudocode has no definition for it (the single call
   site passes $t_a = t$, which is where the code gets it from).
   *Fix:* replace both occurrences of $t$ inside `\HybridSegment` by $t_a$, i.e.
   "$h = (t' - t_a)/\dt$" and "$\tilde{\pos}_m(t' - t_a)$"; nothing else changes because
   `\HybridReconnect` calls it with $t_a = t$.

4. **`Overleaf/appendices/solutions/ch24-solutions.tex`, solution to `exr:ch24-offsets`
   (line 12) - the round-1 rename of the waypoint index was not carried into the solutions
   (category F).**
   The chapter, `Overleaf/appendices/glossary/ch24-terms.tex`, `Overleaf/appendices/glossary.tex`,
   Tables 24.2 and 24.3 and the exercises now all use $j$ for the waypoint index, $j_0$ for
   the first index not yet passed and $t_j$ for the arrival time (and the solution to
   `exr:ch24-reconnect-bound` was updated). The solution to `exr:ch24-offsets` still reads
   "Start times are read on line~... ($k_0$ from $t/\Delta T - t_0^i$) and in the arrival time
   $t_k = (t_0^i + k + \Delta)\Delta T$; written on line~... ($t_0^i \gets t_0^i + k + \Delta$)",
   which collides with $k$ = number of agents in
   `Overleaf/frontmatter/notation.tex` (line 95) and contradicts the algorithm the reader is
   being pointed at.
   *Fix:* in that one sentence replace $k_0 \to j_0$, $t_k \to t_j$ and both occurrences of
   $k$ in "$t_0^i + k + \Delta$" by $j$. (Optional, cosmetic: the label
   `alg:ch24-reconnect:k0` could be renamed `alg:ch24-reconnect:j0` in the chapter and in the
   two solutions that `\ref` it; label names are not printed, so this is not required.)

## Suggestions

* `figures/ch24/architecture.tex` still produces the same 13.22856 pt overfull hbox as in
  round 1 (log line 2169), although the round-1 response reported it cleared. It is below the
  15 pt bar, so it is optional, but the fix is small: reduce `layer/.style` from
  `minimum width=4.1cm,text width=3.9cm` to about `3.9cm/3.7cm`, or shift the right-hand
  column from $x = 9.4$ to $x = 9.2$.
* `code/figures/gen_ch24_scenario.py` prints "72 blocked cells, 9 in layer 10" while
  `sec:ch24-uncertainty` says "70 predicted cells over five layers, seven of them in the
  first, plus the two teammates' current cells". Both are right (9 = 7 + 2), but a reader who
  re-runs the generator will think the chapter is wrong. Print the split explicitly, e.g.
  "72 blocked cells = 70 predicted (7, 10, 13, 16, 24 in layers 10-14) + 2 teammate cells".
* `code/ch24_hybrid.py` still logs reconnection attempts as `k=5 delay=1` (the "Reconnection
  attempts" block). Round 1's rename reached the transition string ("at waypoint %d") but not
  this one; `j=5` would match the chapter.
* `exr:ch24-horizon`(b) asks for a detection range but gives only $v_{\max} = 2$\,m/s, while
  the formula in `sec:ch24-horizon` uses $v_{\mathrm{cruise}}$. The solution silently
  substitutes $v_{\max}$ and then mentions $v_{\mathrm{cruise}} = 1.5$ in a parenthesis. Add
  "$v_{\mathrm{cruise}} = 1.5$\,m/s" to the exercise statement so the reader can apply the
  chapter's formula as written.
* `def:ch24-inside` and `alg:ch24-trigger` allow the trigger to fire at $h = 0$, i.e. with
  the drone already inside the inflated margin. One clause in the paragraph after the
  definition saying what the executive does then (it enters Avoiding with $t_c = 0$ and the
  ORCA half-plane is built at $h_c = 0$, so the manoeuvre is the most aggressive one
  available) would close the last gap in the trigger's specification.
* Table 24.1 gives the prediction layer's rate as "every control cycle, 10 Hz", but the code
  drives it from `RateSchedule` with a separate `period_prediction`. Naming that parameter in
  Table 24.4 would make `lst:ch24-rates` self-explanatory.
* Table 24.5 pairs each claim with a ch25 metric; a pointer to the specific row of ch25's
  experiment matrix (prediction quality, intruder behaviour, ...) would make the audit trail
  complete.

## What must be kept

Everything praised in round 1 survives the revision and should not be touched again: the
four-layer diagram with real rates and Table 24.1 as an interface contract; `sec:ch24-world`,
the piece most integration papers omit, with the start-time bookkeeping that the
"Reservations without their time offsets" pitfall then dramatises; the state machine,
Algorithm 24.1 and its *bounded* exit from Avoiding by drift **and** time, with the three
commentary points after it; Definition 24.2 with `eq:ch24-margin` and the new sentence that
$t_c$ is a time to loss of margin rather than to impact; the $\kappa_p = \sqrt{-2\ln(1-p)}$
derivation with 2.45/3.03 and the comparison against the one-dimensional 1.64 of the
linearised chance constraint; Proposition 24.2 and its proof, which is correct, complete and
tight, and is the missing link between grid MAPF and physical drones; the worked scenario
intact - the trace table, `fig:ch24-recheck` and drone C's delayed reconnection creating
$\langle B, C, (6,2), 7\rangle$ remain the best argument in the book for why a re-check is not
optional, and every number in them is reproduced by the code; the honest "What is not
guaranteed" list with Table 24.5; the five pitfall boxes; the research-directions section,
each paragraph with a formulation *and* an evaluation; and Exercise 24.8 as a genuine
Week-12 capstone.

Four round-2 improvements are worth calling out and keeping as they are. The rewritten
"How fast the inflation grows" paragraph is now the correct extrapolation
$\sigma_p^2 + 2s\sigma_{pv} + s^2\sigma_v^2 + \tfrac13 q s^3$ with the velocity term
identified as the dominant one at these look-aheads - only the value of $q$ needs naming
(required change 1); the gain $k_C$ now makes `eq:ch24-comm` dimensionally sound and matches
`preferred_velocity` term for term; the proof of Proposition 24.4 now closes on the right
argument ("every non-pair path is reserved in $R'$") instead of a false claim about the code;
and the solutions appendix has grown from three to seven of the eight exercises, with the new
hints for `exr:ch24-particles`, `exr:ch24-states`, `exr:ch24-formation` and `exr:ch24-dwa`
being substantive and consistent with the chapter - the bimodal-prediction discussion in
`exr:ch24-particles` and the leader-avoids rule in `exr:ch24-formation`(c) are genuinely
instructive.

## Response to review (round 2)

All four required changes are applied; the build is status 0 with no errors, the
self-test of `code/ch24_hybrid.py` passes (201 cycles), and every number quoted in
the chapter is unchanged.

**Required change 1 (category A) — process-noise intensity inconsistent by a factor of ten.**
Applied exactly as prescribed; no number and no line of the code's `Q` was touched.
(a) `chapters/ch24-hybrid-architecture.tex`, Example 24.1 (`ex:ch24-scenario`) now reads
"tracked by the constant-velocity Kalman filter of \cref{ch:ch18}, in its discrete
white-noise-acceleration form with acceleration variance $\sigma_a^2 = 0.05$ m$^2$/s$^4$
per axis, equivalent to a continuous intensity $q = \sigma_a^2\,\dt = 0.005$ m$^2$/s$^3$
at the $10$ Hz observation rate."
(b) In `sec:ch24-uncertainty` the extrapolation now names the constant: "... $+\tfrac13 q s^3$
in the filter's position, cross and velocity variances, with $q = 0.005$ m$^2$/s$^3$ for the
tracker of \cref{ex:ch24-scenario}". The arithmetic of the paragraph is now reproducible:
$\tfrac13(0.005)(27) = 0.045$, total $0.0041 + 0.021 + 0.054 + 0.045 = 0.124$ m$^2$ at
$s = 3$ s, hence $\sigma(3) = 0.35$ m and the inflation $0.86$ m used by `sec:ch24-horizon`
and `fig:ch24-horizon`.
(c) The docstring of `IntruderTracker` (`code/ch24_hybrid.py`, line 328) now says the process
noise comes from the *discrete* white-noise-acceleration model with acceleration variance `q`
per axis, whose equivalent continuous intensity is `q*dt` — the value the $\tfrac13 q s^3$
growth law of the chapter uses. `Q` itself is unchanged, so no simulated number moved.

**Required change 2 (category A) — the horizon and the reversal form of `eq:ch24-tauh`.**
`sec:ch24-horizon` (formerly "satisfies the first two conditions") now reads: "so $\tau_h = 3$ s
clears the hand-over condition and the stop form of \cref{eq:ch24-tauh} ($1.6$ s) with room to
spare, and falls $0.1$ s short of the reversal form ($3.1$ s); the single-integrator drones of
the scenario are never asked to reverse, but a double-integrator drone would need
$\tau_h \ge 3.1$ s (\cref{exr:ch24-dwa}). The inflation is still below the lane spacing of $2$ m."
$\tau_h$ was **not** raised, so the whole run is unchanged.

**Required change 3 (category C) — free symbol $t$ in `\HybridSegment`.**
Both occurrences inside the function now use its own argument $t_a$:
line `alg:ch24-reconnect:pred` tests $h = (t' - t_a)/\dt$ and line `alg:ch24-reconnect:mate`
tests $\tilde{\pos}_m(t' - t_a)$. The single call site passes $t_a = t$, so nothing else changes.

**Required change 4 (category F) — the waypoint index in the solution to `exr:ch24-offsets`.**
That sentence now reads $j_0$ (from $t/\Delta T - t_0^i$), the arrival time $t_j = (t_0^i + j + \Delta)\Delta T$
and $t_0^i \gets t_0^i + j + \Delta$, consistent with the chapter, the glossary and the other
solutions. The optional part was taken too: the label `alg:ch24-reconnect:k0` is renamed
`alg:ch24-reconnect:j0` in the chapter and in the solution that `\ref`s it (no other file refers to it).

### Suggestions

* **architecture figure overfull hbox — fixed.** The offender was not the layer width but the
  single-line label "observations $\meas_k$ of the intruder" on the world-model arrow, which
  reached $x = 13.5$ cm. It is now broken over two lines; the picture measures $421.6$ pt against
  a text width of $443.9$ pt (was $460.7$ pt), and the $13.22856$ pt overfull box is gone from the
  log. Layer widths and column positions are unchanged, so the diagram is exactly as praised.
  The only overfull box left in the build ($29.1$ pt, "Rapidly-exploring random tree with goal
  bias") is a list-of-algorithms entry of ch16 in the shared front matter, not a ch24 file.
* **`gen_ch24_scenario.py` cell split — done.** It now prints
  `72 blocked cells = 70 predicted (7, 10, 13, 16, 24 in layers 10-14) + 2 teammate cells`,
  matching "70 predicted cells over five layers, seven of them in the first, plus the two
  teammates' current cells".
* **`k=5 delay=1` in the reconnection log — done.** The log key and the printed label are now
  `j` (`t=  4.9  C at (5.46, 2.39): j=5 delay=1 (ok)`); the two self-test assertions were updated
  with it and still pass.
* **`exr:ch24-horizon`(b) — done.** The statement now gives $v_{\mathrm{cruise}} = 1.5$ m/s, and the
  solution applies the chapter's formula as written: $(1.5+3)(2+20\cdot0.05)+1+0.5 = 15$ m, with the
  $16.5$ m variant for a drone already at $v_{\max}$ given as the second case.
* **Trigger at $h = 0$ — done.** A clause after `def:ch24-inside` now states what the executive does
  when $t_c = 0$: it enters Avoiding with $t_c = 0$ and builds the ORCA half-plane at $h_c = 0$, from
  the current relative position — the most aggressive manoeuvre available, a recovery rather than a
  prevention — and stays in Avoiding until the margin is positive for $n_{\mathrm{clear}}$ cycles.
* **`period_prediction` — done.** `tab:ch24-parameters` has a new row naming the parameter, its value
  $0.1$ s and the fact that it equals $\dt$ here, which is why the layer table reads "every control cycle".
* **ch25 experiment-matrix row pointers (Table 24.5)** — not done. It requires editing against another
  chapter's table numbering, which is outside this chapter's files and would break if ch25's matrix is
  still being revised.

Nothing on the "must be kept" list was touched: the four-layer diagram and its rates, `sec:ch24-world`,
the state machine and Algorithm 24.1, Definition 24.2, the $\kappa_p$ derivation, Proposition 24.2 and
its proof, the worked scenario with its trace table, `fig:ch24-recheck` and drone C's delayed
reconnection, the "What is not guaranteed" list, the five pitfall boxes, the research directions,
Exercise 24.8, the rewritten inflation-growth paragraph (only $q$ is now named), the gain $k_C$, the
proof of Proposition 24.4 and the seven solutions.
