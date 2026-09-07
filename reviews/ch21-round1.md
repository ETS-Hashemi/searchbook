# Review of Chapter 21 (Model Predictive Control) - round 1

Reviewed: `Overleaf/chapters/ch21-mpc.tex` (1431 lines), figures `Overleaf/figures/ch21/{idea,halfplane,example,tuning,chance,experiment}.tex`,
code `Overleaf/code/ch21_mpc.py` and `Overleaf/code/figures/gen_ch21_mpc.py`,
`Overleaf/appendices/solutions/ch21-solutions.tex`, `Overleaf/appendices/glossary/ch21-terms.tex`,
against `STYLE_GUIDE.md` section 9 (A-H), `docs/specs/ch21.md` and `docs/core-idea.txt` (Week 11).

Build: `./build.sh ch21-mpc` returns status 0, no `!` errors, no undefined labels or citations belonging to this chapter
(the `??` are cross-chapter references, expected in a single-chapter build), no overfull boxes above 15 pt.
Chapter body runs from PDF page 18 (chapter opening) to page 39 (last exercise) = **22 pages**, inside the 24-page ceiling
(above the spec's 15-17 target; see suggestion S3, no cuts are required).
Code: `python3 code/ch21_mpc.py` runs in 3.0 s, self-test passes. I re-ran `tuning_runs()` and `horizon_experiment()`
without touching the repository: `figures/data/ch21-experiment.dat` and `ch21-tuning.dat` reproduce exactly.
Every number in Table 21.3 (trace), Section 21.7.1 (tuning) and Table 21.4 (experiment) matches the code, and
Proposition 21.2 (half-plane), Proposition 21.3 (inscribed polygon), Proposition 21.4 (exact penalty), the DARE/LQR
rearrangement and the chance-constraint derivation are all correct as stated. Two independent hand checks passed
(intruder crossing time 3.75 s at x = 4.5 m; guess separation 0.908 m at t = 2.1 s).

## Verdict

**Minor revision.** The chapter is technically strong, complete against the spec, and its numbers are reproducible.
Every required change below is local: a sentence, a number, a caption, or one added clause. None of them touches the
structure, the algorithm, the code or the figures.

## Required changes

1. **Section 21.6.1 "Terminal cost, terminal set and stability", Theorem 21.5 and `eq:ch21-lyapunov` (lines 725-775).**
   *Problem (A).* `eq:ch21-ocp` (line ~196) defines the cost with the state sum starting at $k=1$:
   $J=\sum_{k=1}^{N-1}(\cdot)\T\mat{Q}(\cdot)+\sum_{k=0}^{N-1}\ctrl_k\T\mat{R}\ctrl_k+(\cdot)\T\mat{P}(\cdot)$.
   Line 729 then defines $V_N(\state)$ as "the optimal cost of `eq:ch21-ocp`", so $V_N$ omits the $k=0$ state term.
   With that cost the shifted-candidate computation of the proof gives
   $V_N(\state_{t+1})\le V_N(\state_t)-\state_{t+1}\T\mat{Q}\state_{t+1}-\ctrl_0^{*\mathsf{T}}\mat{R}\ctrl_0^{*}$,
   **not** $V_N(\state_{t+1})\le V_N(\state_t)-\ell(\state_t,\ctrl_0^{*})$ as printed; the sketch's bookkeeping
   ("the old optimal cost minus the first stage") silently assumes the state sum starts at $k=0$. As written the
   theorem statement and its proof do not match the chapter's own cost.
   *Fix.* Add one sentence after "Write $V_N(\state)$ for the optimal cost of \cref{eq:ch21-ocp} ...":
   "For this section we let the stage sum start at $k=0$, i.e.\ $J=\sum_{k=0}^{N-1}\ell(\state_k,\ctrl_k)+V_f(\state_N)$;
   because $\state_0$ is fixed data, the extra term $\state_0\T\mat{Q}\state_0$ is a constant and the minimiser of
   \cref{eq:ch21-ocp} is unchanged." (Equivalently, restate `eq:ch21-lyapunov` with $-\state_{t+1}\T\mat{Q}\state_{t+1}-\ctrl_0^{*\mathsf{T}}\mat{R}\ctrl_0^{*}$
   on the right-hand side.) Everything else in the proof then goes through verbatim.

2. **Section 21.8 "Solve time" (lines 1127-1131), consistent with Section 21.4.2 (lines 454-457).**
   *Problem (A).* The text says "With $30$ inputs, $15$ slacks and $90$ rows, one step of the planar example takes about
   $1.3$~ms on average and under $10$~ms at worst". The measured run is the **hard** worked example, and
   `ch21_mpc.py` prints `solve time per step: mean 1.41 ms, max 11.03 ms (30 vars, 75 rows)`. Both the problem size and
   the two timings quoted disagree with the code (the 90-row/15-slack count in Section 21.4.2 is correct, but it is the
   *soft* program, which is not the one timed).
   *Fix.* Rewrite as: "With $30$ inputs and $75$ rows (the hard program of \cref{ex:ch21-crossing}; $45$ variables and
   $90$ rows with slacks), one step takes about $1.4$~ms on average and about $11$~ms at worst in NumPy on a laptop, an
   order of magnitude below a $\dt$ of $0.1$~s"; or state the timings as "a few milliseconds, hardware dependent" and
   keep the row counts exact. Same for the sentence at line 456 if you want one consistent figure quoted twice.

3. **Section 21.4.2, `eq:ch21-qp-constraints` (line 431), and Table 21.1 / Section 21.3.3(4) / Pitfall 2 / summary / drone box.**
   *Problem (A).* In the displayed $\mat{G}$ the keep-in block is $(\mat{N}^{c}\mat{S}_u^{p}\ \ \mat{0})$ - no slack
   column - so formation and communication constraints are **hard** in the QP the chapter writes down, in
   `alg:ch21-loop` line `alg:ch21-loop:keepin`, and in the shipped code (`MPC.step` attaches slacks to the avoidance
   rows only; `n_slack = n_avoid if self.soft else 0`). But Table 21.1 classifies Formation and Communication as
   "soft", Section 21.3.3(4) says "avoidance, formation and communication constraints are soft", Pitfall 2 says "make
   every constraint that depends on another agent soft with an exact penalty, and log the slacks", the summary bullet
   repeats it, and the drone box promises slack values for the formation constraint. A reader who implements the
   displayed QP gets the opposite of what the table recommends.
   *Fix.* Add two sentences after `eq:ch21-qp-constraints`: "Written this way the keep-in rows are hard, which is what
   the book's code does: softening them is the same construction as for avoidance (append a $-\mat{I}$ slack column and
   a non-negativity block, and add $w_1s+w_2s^2$ to the cost), and \cref{exr:ch21-coding} asks you to do it." Add a
   footnote or a caption clause to Table 21.1 saying that the hard/soft column is the *recommendation*, and that
   `ch21_mpc.py` implements soft avoidance rows and hard keep-in rows.

4. **Section 21.3.1 "The drone model", line 159.**
   *Problem (A).* "if you need the disc exactly, use a box of half-width $a_{\max}/\sqrt{2}$ (which lies inside the
   disc)" is stated for a model that has just been introduced for $n\in\set{2,3}$; in three dimensions the inscribed
   box has half-width $a_{\max}/\sqrt{3}$.
   *Fix.* Replace $a_{\max}/\sqrt{2}$ by $a_{\max}/\sqrt{n}$ (and likewise for the velocity box if you spell it out).

5. **`Overleaf/appendices/solutions/ch21-solutions.tex`, solution to `exr:ch21-slack` (line 12).**
   *Problem (A).* "In the worked example the largest multiplier is about $16$" contradicts the chapter (Section 21.5,
   "the multipliers stay between $14$ and $19$"; Section 21.6.2, "never exceed $19$") and the code, which reports a
   maximum multiplier of $18.70$ over the run (Table 21.3 shows only the half-second samples, whose maximum is 16.23).
   *Fix.* Change "about $16$" to "about $19$ (the largest multiplier over the run is $18.7$; the sampled trace of
   \cref{tab:ch21-trace} shows $16.2$)".

6. **Table 21.3 caption (`tab:ch21-trace`, lines 647-649).**
   *Problem (D).* The caption says "every half second", but the table lists $t=2.0,\dots,5.0$ in half-second steps and
   then jumps to $6.0$ and $7.0$, and it starts at $t=2.0$, not $t=0$.
   *Fix.* "Trace of \cref{alg:ch21-loop} on \cref{ex:ch21-crossing}: every half second from $t=2$~s to $t=5$~s, then
   every second (the first two seconds are identical to $t=2.0$, all inputs zero)."

7. **Algorithm 21.1 (`alg:ch21-admm`, lines 490, 494) and Algorithm 21.2 (`alg:ch21-loop`, fallback line).**
   *Problem (C).* $\Pi_{[\vect{l},\vect{u}]}$ is used three times and never defined, and the infeasibility certificate
   in the paragraph after the algorithm uses $\delta\vect{y}^{+}$ and $\delta\vect{y}^{-}$ without saying they are the
   positive and negative parts. For a reader working alone these are the only unexplained symbols in the chapter.
   *Fix.* In the sentence introducing the algorithm add: "$\Pi_{[\vect{l},\vect{u}]}(\vect{a})$ is the componentwise
   projection onto the box, i.e.\ $\min(\max(\vect{a},\vect{l}),\vect{u})$", and in the certificate sentence add
   "where $\delta\vect{y}^{+}=\max(\delta\vect{y},0)$ and $\delta\vect{y}^{-}=\min(\delta\vect{y},0)$".

8. **Exercise 21.1 (`exr:ch21-receding`).**
   *Problem (E).* The exercise asks the reader to "run the code with all $N$ inputs of one plan applied in open loop
   while a constant wind adds $0.3$~m/s$^2$ to the plant". `simulate()` has no disturbance argument and no open-loop
   mode (signature: `simulate(mpc, x0, ref, intruder=None, T=8.0, r_safe=1.0, followers=(), cov_growth=None)`), so as
   written the exercise cannot be run; the reader has to guess that the code must be modified.
   *Fix.* Say so explicitly: "(add a constant vector to the plant update inside `simulate`, two lines, and apply
   `U[k]` instead of re-solving for the open-loop run)".

9. **Whole chapter (first use of `\cbs`, `\ecbs`, `\orca`, lines 57, 41, 1148, ...).**
   *Problem (F, cosmetic).* Style guide section 3 requires every acronym to be defined at first use *in every chapter*.
   The macros print bare "CBS", "ECBS", "ORCA"; MPC, QP, ADMM, LQR and DARE are expanded properly, these three are not.
   *Fix.* At the first occurrence write "the conflict-based search (\cbs) path of \cref{ch:ch09}" and "optimal
   reciprocal collision avoidance (\orca, \cref{ch:ch13})", and expand \ecbs at its first use in the drone box.

## Suggestions

* **S1.** Section 21.5 quotes "$\pos_{15}$ ... is only $0.91$~m from the intruder's predicted position" - correct
  (I get $0.908$~m by hand), but the code prints the *solved* plan separation (`plan point sep=1.000`), not the guess.
  Print the linearisation-point separation in `worked_example()` so that this number is also machine-produced.
* **S2.** Section 21.7.1: "RMS error $0.227$~m against $0.208$~m for $N\ge10$" - the experiment gives $0.2074$-$0.2091$
  for $N\ge10$. Write "$\approx0.208$~m" or quote the range.
* **S3.** Length (22 pages against a 15-17 target). Nothing required is padding, but about a page of repetition can go:
  the late-detection result is told three times with the same numbers (Section 21.7.3, Pitfall "Hard constraints that
  become infeasible", Section 21.8 "When the solver fails") and the "$w_1=50$ reproduces the hard trajectory" story
  four times (end of Section 21.5, Section 21.6.2, Section 21.7.1, summary). Keep the full account in Sections 21.6.2
  and 21.7.3; reduce the two pitfall/implementation repetitions to a cross-reference.
* **S4.** `alg:ch21-admm` line `alg:ch21-admm:scale` says "unit norm"; the code equilibrates rows to unit *infinity*
  norm and tests the residuals every ten iterations against `eps_abs + eps_rel * scale`. One clause in the walkthrough
  would make pseudocode and code agree exactly (the rest of the algorithm matches `solve_qp` line for line, including
  the $\rho$ rebalancing every 30 iterations and the dual restart).
* **S5.** Section 21.4.3 calls the solver "thirty lines"; `solve_qp` is about 75 lines with scaling, restart and
  polishing (the ADMM iteration itself is the 22 lines of `lst:ch21-admm`). Say "whose iteration is twenty lines".
* **S6.** $\mat{X}$, $\mat{U}$, $\mat{S}_x\state_0$ are stacked *vectors* typeset with the matrix macro, and the
  geofence $\mathcal{X}$ sits two lines away from $\mat{X}$ in Section 21.3.2. Consider $\vect{X}$, $\vect{U}$, or a
  half-sentence warning.
* **S7.** `appendices/solutions/ch21-solutions.tex` covers 4 of the 10 exercises. Hints for 21.4 (units), 21.7
  (recursive feasibility with $c$ such that $\set{\state:\state\T\mat{P}\state\le c}$ respects the input box) and 21.8
  (chance constraint) would help a lone reader most.
* **S8.** Table 21.1 could name $M$ in the "polygon" cells (e.g. "polygon, $M=8$, \cref{thm:ch21-polygon}") so the
  $7.6\,\%$ loss quoted later is anchored in the table.

## What must be kept

The chapter is the best kind of control chapter for this audience: it earns every formula. The headlight metaphor and
`fig:ch21-idea` land the receding-horizon principle in half a page; the condensation to `eq:ch21-qp` is derived, not
asserted, and the block-by-block reading of $\mat{G}$, $\vect{l}$, $\vect{u}$ after `eq:ch21-qp-constraints` is exactly
what a student needs to implement it. The half-plane convexification with Proposition 21.2 and `fig:ch21-halfplane`,
and the inscribed-polygon proposition with its apothem argument, are correct, short and genuinely useful. The
hard/soft discussion is the intellectual centre of the chapter: the exact-penalty proposition is correctly stated and
proved, it is tied to *measured* multipliers (14-19, so $w_1=50$), and the late-detection experiment shows the soft
controller beating the hard one on both separation and tracking - keep that experiment, Table 21.4 and
`fig:ch21-experiment` untouched. The worked example is fully reproducible: every entry of Table 21.3, the minimum
separation of exactly 1.000 m at t = 4.2 s, the RMS error 0.208 m, the 26/47 warm/cold iteration counts and the
chance-constrained 1.143 m all come out of `ch21_mpc.py` as printed. The ADMM pseudocode is a faithful transcription of
the OSQP iteration and of the shipped solver, including row scaling, polishing and the primal-infeasibility
certificate. The chance-constraint section, the four pitfalls, the tuning table with its units paragraph, the drone box
and the ten well-graded exercises (including the Week-11 leader-follower coding exercise, which the code's `Follower`
actually supports) all stay as they are.
