# Review of Chapter 24 (The Hybrid Collision-Avoidance Architecture) - round 1

## Verdict

**Minor revision.**

This is a strong capstone chapter. It covers every "must cover" item of `docs/specs/ch24.md`
and every element of the Week-12 capstone in `docs/core-idea.txt` (four layers, the five-step
decision logic, the experiment matrix, all seven research directions, all four spec pitfalls).
It builds with status 0, no `!` errors, no undefined labels or citations of its own, six
figures, five tables, four algorithms, two listings, five pitfall boxes, 19 unique index
entries, eight graded exercises including the Week-12 coding capstone, and all eleven
citation keys required by the spec exist in `Overleaf/references.bib`. The code
`Overleaf/code/ch24_hybrid.py` runs in 1.3 s, its self-tests pass, and almost every number
quoted in the chapter is reproduced by it (I re-ran the simulation and re-derived the
trigger profile, the minimum separations, the formation error, the link length, the blocked-cell
counts, the reconnection candidate list and the cost figures).

Four accuracy defects block acceptance, but each is a local edit: one quoted number the code
does not produce, one growth law that the numbers in the same sentence contradict, one
dimensionally inconsistent equation, and one false statement about what the code does. There
is also a book-wide notation collision on `$k$`, one missing parameter, and one page of
excess length. Nothing structural needs to change.

## Required changes

1. **Table 24.3 (`tab:ch24-trace`), row `t = 3.5`, section `sec:ch24-scenario` - the estimated
   intruder velocity is not what the code produces (category A).**
   The row reads "Estimate $(10.37, 4.35)$, velocity $(-0.55, 0.00)$; truth $(10.40, 4.30)$,
   $(-0.60, 0)$." The estimated position and both truth values are correct, but the estimated
   velocity at the trigger is $\hat{\vel} = (-0.614, 0.042)$ m/s; $(-0.552, -0.003)$ is the
   tracker's velocity at the *end* of the run ($t = 20.1$ s, after the intruder has left the
   sensor range). The root cause is in
   `Overleaf/code/figures/gen_ch24_scenario.py` (the print block after `write_dat("ch24-horizon.dat", ...)`):
   it prints `sim.tracker.velocity`, i.e. the final filter state, next to `hist[ib]["est"]`,
   which is the estimate stored at the trigger cycle.
   *Fix:* record the estimated velocity per cycle in `HybridSimulation.step`
   (add `est_v=self.tracker.velocity.copy()` to the history entry), print `hist[ib]["est_v"]`
   in the generator, and change the table to "velocity $(-0.61, 0.04)$". Do not change the
   truth values.

2. **Section `sec:ch24-uncertainty`, paragraph "How fast the inflation grows" - the stated
   growth law contradicts the numbers in the same sentence (category A).**
   The text says "the extrapolated position variance grows with the cube of the look-ahead,
   so $\sigma(h)$ grows like $s^{3/2}$: the tracker of the scenario reports
   $\sigma = 0.06, 0.14, 0.24, 0.35$ m at $s = 0,1,2,3$ s." Those numbers grow with exponent
   $\approx 0.86$ between $s = 1$ and $s = 3$ ($0.353/0.137 = 2.58$, whereas $s^{3/2}$ would
   give $3^{1.5} = 5.20$). At the trigger the filter's covariance is
   $\sigma_p^2 = 0.0041$, $\sigma_{pv} = 0.0035$, $\sigma_v^2 = 0.0060$, so the extrapolated
   position variance
   $\sigma^2(s) = \sigma_p^2 + 2s\,\sigma_{pv} + s^2\sigma_v^2 + \tfrac13 q_{\mathrm{eff}} s^3$
   is $0.0041, 0.0188, 0.0557, 0.1245$ at $s = 0,1,2,3$; the velocity-uncertainty term
   $s^2\sigma_v^2$ contributes $0.054$ of the $0.124$ at $s = 3$ and the cubic term only
   $0.045$. The cubic law is the asymptotic behaviour of the process-noise term alone, not of
   this tracker at this horizon.
   *Fix:* replace the first clause with the full extrapolation, e.g. "the extrapolated
   position variance is
   $\sigma_p^2 + 2s\,\sigma_{pv} + s^2\sigma_v^2 + \tfrac13 q s^3$: the velocity-uncertainty
   term $s^2\sigma_v^2$ dominates at the look-aheads that matter here, so the inflation grows
   almost linearly, and the cubic process-noise term only takes over once the velocity is well
   estimated and the horizon is long." Keep the quoted $\sigma$ values and the conclusion that
   the inflation ($0.86$ m) exceeds $R_{\mathrm{safe}}$.

3. **Equation `eq:ch24-comm` in `sec:ch24-constraints` - dimensionally inconsistent (category A).**
   The communication term adds
   $\frac{\pos_j - \pos_i}{\norm{\pos_j - \pos_i}}\bigl(\norm{\pos_j - \pos_i} - \ell_{\mathrm{act}}\bigr)$,
   a *length*, to a velocity. The neighbouring `eq:ch24-formation` correctly carries the gain
   $k_F$ (units s$^{-1}$, `k_form=0.5` in `PARAMS`). `preferred_velocity` in
   `Overleaf/code/ch24_hybrid.py` implements the same expression with an implicit unit gain.
   *Fix:* introduce a gain $k_C$ with units s$^{-1}$,
   $\vel^{\mathrm{pref}}_i \gets \vel^{\mathrm{pref}}_i + k_C\,\frac{\pos_j - \pos_i}{\norm{\pos_j - \pos_i}}\bigl(\norm{\pos_j - \pos_i} - \ell_{\mathrm{act}}\bigr)$,
   add the row "$k_C$ | $1$ | gain of the soft range term of `eq:ch24-comm`" to
   Table 24.4 (`tab:ch24-parameters`), and name the constant explicitly in the code
   (`k_comm=1.0` in `PARAMS`, used in `preferred_velocity`).

4. **Proof of Proposition 24.4 (`thm:ch24-replan`), `sec:ch24-guarantees` - a false statement
   about the code (category A).**
   The proof sketch ends "...and it is run once more after the repair in the code."
   `HybridSimulation.recheck` in `Overleaf/code/ch24_hybrid.py` calls `first_conflict` exactly
   once, *before* the local CBS, and never again after the repaired pair is installed; the only
   post-repair detector calls in the file are in the self-tests.
   *Fix:* delete the clause - the argument is already complete without it, because the local
   CBS is run with $R'$ (every non-pair path) as low-level constraints, so a conflict with a
   third drone is impossible by construction - or add the second call at the end of `recheck`
   (`entry["after_conflict"] = first_conflict(...)` plus an `assert`) and keep the sentence.

5. **Example 24.1 (`ex:ch24-scenario`) and `sec:ch24-horizon` - $a_{\max}$ is used but never
   given (category C).**
   Section `sec:ch24-horizon` concludes "In the scenario $v_{\max}/a_{\max} = 1.5$ s", and
   `eq:ch24-tauh` and Exercise 24.1 depend on $a_{\max}$, but the example box states only
   $v_{\mathrm{cruise}} = 1$ m/s and $v_{\max} = 1.5$ m/s and Table 24.4 has no such row, so a
   reader cannot reproduce the $1.5$ s. The value in `PARAMS` is `a_max=1.0`.
   *Fix:* add "$a_{\max} = 1$ m/s$^2$" to Example 24.1, and add the row
   "$v_{\mathrm{cruise}}$; $v_{\max}$; $a_{\max}$ | $1$; $1.5$; $1$ | cruise and maximum speed,
   acceleration limit" to Table 24.4.

6. **Section `sec:ch24-reconnect`, paragraph beginning "When is a reconnection 'too costly'..." -
   contradicts the trace table and the code (category A).**
   The text says the reconnection of drone A at $t = 9.1$ s is impossible because "every
   segment back to it crosses the predicted tube". Instrumenting `HybridSimulation.reconnect`
   shows that of the eight candidates, seven are rejected on
   line~\ref{alg:ch24-reconnect:fast} for requiring $4.61, 2.68, 2.09, 1.81$ m/s ($\Delta = 0$,
   $k = 10 \ldots 13$) and $2.18, 1.76, 1.56$ m/s ($\Delta = 1$, $k = 10, 11, 12$), all above
   $v_{\max} = 1.5$ m/s, and only $k = 13$ with $\Delta = 1$ reaches the segment test and is
   blocked by the tube. Table 24.3 states this correctly, so the two passages disagree.
   *Fix:* rewrite as "...as for drone A at $t = 9.1$ s, where seven of the eight candidates
   would need more than $v_{\max}$ and the only slow enough one, $k = 13$ with $\Delta = 1$,
   crosses the predicted tube."

7. **Book-wide notation collision on $k$ (category F).**
   `Overleaf/frontmatter/notation.tex` (line 95) fixes $k$ as the number of agents, and
   Proposition 24.1 uses it that way ($\Pi = (\pi_1, \dots, \pi_k)$), as does the complexity
   statement "$\bigO{n\,k}$ distance computations" in `sec:ch24-reconnect`. The same symbol is
   used for the reconnection *waypoint index* in Definition 24.3, Algorithm 24.3,
   Algorithm 24.1 (line~\ref{alg:ch24-loop:reconnect} and the shift on
   line~\ref{alg:ch24-loop:shift}), Table 24.2, Table 24.3, `sec:ch24-scenario` and
   Exercises 24.3 and 24.4 - in the same section as the agent-count use.
   *Fix:* rename the waypoint index to $j$ (already the path index in Definition 24.1,
   $\pi_i[j]$) everywhere it means a waypoint, rename the sample counter inside
   `\HybridSegment` from $j$ to $u$, and leave $K$ (the look-ahead) and $k$ (the number of
   agents) as they are. Update the glossary entry "Reconnection" in
   `Overleaf/appendices/glossary.tex` and the solutions in
   `Overleaf/appendices/solutions/ch24-solutions.tex` to match.

8. **Length: the chapter body is 25 pages against the 24-page bar (spec target 16-18)
   (category G).**
   In `build/only-ch24-hybrid-architecture.pdf` the chapter runs pages 27-51; page 52 is the
   bibliography. All of the technical content is required by the spec, so cut only the
   following repetitions, which together recover about one page:
   (a) `sec:ch24-motivation`, the final paragraph "The chapter is organised as follows...
   the capstone build of Week 12" (11 lines) restates the table of contents; reduce to one
   sentence naming `sec:ch24-scenario` and `sec:ch24-guarantees`.
   (b) `sec:ch24-horizon`, "Choosing the horizon", from "A last condition ties the horizon to
   the sensor" to "...would have triggered with about $1.8$ s to spare" (12 lines): keep the
   detection-range formula and the "$8$ m needed against a $6$ m sensor" fact, and drop the
   shared-track arithmetic, which is exactly what Exercise 24.1(b) asks the reader to do.
   (c) `sec:ch24-scenario`, "What the run shows": the minimum separations
   $1.20 / 1.98 / 2.25$ m are already in the caption of `fig:ch24-timeline` and the
   $\sumcost = 48$, $\makespan = 20$ figures are already in the last row of Table 24.3; keep
   only the teammate separation, the two infeasible cycles, the price of safety and the
   forward pointer to `ch:ch25`.
   (d) `sec:ch24-intuition`, first paragraph: the four sentences that re-describe each layer's
   inputs, outputs and rate duplicate Table 24.1 and `fig:ch24-architecture`; keep the "four
   people with different time budgets" analogy and one clause per layer.

## Suggestions

* `sec:ch24-scenario`, "What the run shows": "almost all of it A's detour along row 6" is an
  overstatement - A contributes $7$ of the $13$ extra steps ($13 \to 20$), C contributes $5$
  ($13 \to 18$) and B one ($9 \to 10$). Write "over half of it A's detour along row 6, the
  rest C's descent to row 1 and B's extra wait".
* `Overleaf/appendices/solutions/ch24-solutions.tex` has solutions for only three of the eight
  exercises (`exr:ch24-horizon`, `exr:ch24-reconnect-bound`, `exr:ch24-offsets`). Adding at
  least short hints for `exr:ch24-particles`, `exr:ch24-states`, `exr:ch24-formation` and
  `exr:ch24-dwa` would bring the chapter in line with ch21 (8 of 10). The three that exist are
  excellent and are consistent with the chapter.
* The objectives box promises "the four integration pitfalls" but the chapter has five pitfall
  boxes (the extra one is "A trigger without hysteresis chatters"). Say "five", or label the
  hysteresis box as belonging to the trigger rather than to the integration.
* Only one citation appears outside the Further-reading paragraph (`\textcite{zhu2019chance}`).
  Consider citing `vandenberg2011orca` at Proposition 24.3, `sharon2015cbs`/`barer2014ecbs` at
  Proposition 24.1, `koenig2002dstarlite` in `sec:ch24-replan` where the key modifier $k_m$ is
  invoked, `stern2019mapf` at Definition 24.1 and `honig2018trajectory` at `eq:ch24-reference`.
* `def:ch24-inside` calls $t_c$ the "predicted time to collision", but it is the first
  look-ahead at which the *inflated* margin goes negative, which is strictly earlier than any
  collision. One sentence saying so ("$t_c$ is a time to loss of margin, not a time to
  impact") would prevent a misreading when $t_c$ is passed to the ORCA half-plane.
* Proposition 24.3 should name two more ORCA assumptions from ch13: the chosen velocity is held
  constant over $\ttc$, and the drones are velocity-controlled (single integrators), which the
  worked scenario satisfies but a real quadrotor does not.
* `sec:ch24-uncertainty` says the replan of A "blocks $72$ cells over five layers, nine of them
  in the first". This is reproducible only if the reader knows that the count from
  `HybridSimulation.replan` mixes the $70$ intruder cells (7, 10, 13, 16, 24 at grid times
  10-14) with the two teammate cells blocked at $t_{\mathrm{start}}$. Either say "$70$
  predicted cells over five layers, seven in the first, plus the two teammates' current cells"
  or have `gen_ch24_scenario.py` print the split.
* `figures/ch24/architecture.tex` produces a 13.2 pt overfull hbox (below the 15 pt bar in the
  style guide, so optional): shortening the labels "re-check conflicts and constraints; local
  CBS on the affected subset" and "nominal time-indexed paths $\pi_1,\dots,\pi_k$" would clear it.
* Table 24.1 would be easier to use if the "Guarantee" column also pointed at the proposition
  in `sec:ch24-guarantees` that carries the claim into the composed system.

## What must be kept

The architecture is taught the way a research student needs it: `fig:ch24-architecture` and
Table 24.1 give the four layers with real inputs, outputs and rates; `sec:ch24-world` is the
piece most integration papers omit and this chapter gets right, including the start-time
bookkeeping that the "Reservations without their time offsets" pitfall then dramatises. The
state machine, Algorithm 24.1 and its bounded exit from Avoiding (drift *and* time) are exactly
the right level of detail, and the three commentary points after the algorithm are worth more
than a page of prose. Definition 24.2 with `eq:ch24-margin`, and the derivation of
$\kappa_p = \sqrt{-2\ln(1-p)}$ with $\kappa_{0.95} = 2.45$, $\kappa_{0.99} = 3.03$ and the
comparison with the one-dimensional $1.64$ of the linearised chance constraint, are correct and
unusually careful. Proposition 24.2 and its proof are the highlight: the
$\ell/\sqrt{2}$ separation bound is correct, the case analysis on the integer cross product is
complete, the bound is genuinely tight (the $\vect{\Delta}_0 = (1,0)$, $\vect{\Delta}_1 = (0,1)$
witness), and it is the missing link between grid MAPF and physical drones that most texts skip.
Keep the worked scenario intact - the trace table, `fig:ch24-recheck` and the delayed
reconnection of drone C that creates the conflict $\langle B, C, (6,2), 7\rangle$ are the best
argument in the book for why a re-check is not optional, and every one of those numbers is
reproduced by `ch24_hybrid.py`. Keep the honest "What is not guaranteed" list and
Table 24.5 pairing each claim with its assumption and the ch25 metric that measures the gap;
keep the five pitfall boxes, the research-directions section (each with a formulation *and* an
evaluation), and Exercise 24.8, which is a genuine Week-12 capstone rather than a homework
problem.
