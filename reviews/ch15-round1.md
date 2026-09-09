# Review of Chapter 15 (Artificial Potential Fields) - round 1

Reviewed: `Overleaf/chapters/ch15-potential-fields.tex` (1346 lines), the nine figure
files in `Overleaf/figures/ch15/`, `Overleaf/code/ch15_potential_fields.py`,
`Overleaf/code/figures/gen_ch15_field.py`, `Overleaf/bib/ch15-extra.bib`,
`Overleaf/appendices/glossary/ch15-terms.tex`,
`Overleaf/appendices/solutions/ch15-solutions.tex`, against `STYLE_GUIDE.md` §9,
`docs/specs/ch15.md` and `docs/core-idea.txt` (Week 7).

Build: `./build.sh ch15-potential-fields` returns status 0. No `!` errors, no undefined
citations, no undefined reference belonging to this chapter (the 63 `??` are all
`ch:chNN` cross-chapter references, legitimate in a single-chapter build). One overfull
box (29.1 pt) and it is in the glossary appendix, not in this chapter. Chapter body =
20 PDF pages (pp. 136-155, PDF pages 21-40), i.e. at the review ceiling but above the
12-18 pages of STYLE_GUIDE §2 and well above the 11-13 pages of the spec; see
Suggestion 1 -- I do **not** require cuts, because everything present is required
content.

Code: `python3 code/ch15_potential_fields.py` passes in 4.5 s. I re-ran the chapter's
numbers independently. All of these reproduce exactly: the three probe points A/B/C and
their forces and potentials (Table 7.1), the trajectory (1099 steps, min clearance
0.519; hybrid 1171 steps, 0.695), the path length 8.957 vs 8.016 straight line, the
local-minimum root x* = 2.4872 and the 354 steps, the saddle eigenvalues 36.96 and
-2.64, the GNRON offset d = 0.568 and the 425 steps for n = 2, the corridor table
(all 10 rows, all stiffnesses, 0.161/0.410/0.342/0.498), the -6.01 minimum of F_x and
the root x = 3.163, the stop point (3.163, 4.005) after 446 steps, the basin counts
262/179/386/55, the trapped point (2.676, 4.1) with eigenvalues 9.87 and 24.89, the
1018 and 1428 mean step counts, the basin half-widths 1.44 and 1.08, the swarm
separations 1.044 and 0.000 and the 30 time units. One number does not reproduce
(Required change 1).

## Verdict

**Minor revision.** The mathematics of the chapter is, with the exceptions listed
below, correct and unusually well tied to code: I checked every formula (attractive,
conic, hybrid, FIRAS repulsion, the chain-rule derivation, the GNRON product rule,
eq. 7.8, eq. 7.11, eq. 7.12, eq. 7.13, the Rimon-Koditschek navigation function, the
Euler-characteristic argument) and all of them are right. Every "must cover" item of
`docs/specs/ch15.md` is present, all nine figures are referenced with captions that say
what to notice, there are 28 index entries, 8 exercises including the Week-7 coding
exercise and a derivation exercise, and every citation key resolves to a real,
correctly described reference. The required changes below are all local: one wrong
number, one wrong summary claim, one theorem hypothesis, two mis-stated justifications,
one missing trace table, two undefined symbols, one un-expanded acronym and one missing
citation.

## Required changes

1. **§7.8.1 `sec:ch15-basin`, sentence "the drones that do arrive need on average
   $2.48$ escapes and $1\,428$ steps".** *Problem (category A):* the code does not
   produce 2.48 for that population. `basin_experiment(escape=True)` gives a mean of
   **1.236** escapes over the 386 drones that reach the goal; 2.478 is the mean over all
   441 starts, which is what `gen_ch15_field.py` prints (`res["escapes"].mean()`), and
   it is inflated by the 55 drones that time out after up to 20 escapes. *Fix:* write
   "need on average $1.24$ escapes and $1\,428$ steps, against $1\,018$ for the plain
   runs (averaged over all $441$ starts the escape count is $2.48$, because the $55$
   drones that never arrive keep walking)". Verified: mean escapes over reached =
   1.236, over all starts = 2.478, mean steps over reached = 1428.3, plain = 1018.4.

2. **`summary` box, third bullet: "oscillation when $\dt\,\lambda_{\max} \ge 2$".**
   *Problem (category A):* this contradicts Proposition 7.7 and §7.7.3. By Prop. 7.7 the
   error alternates in sign (that *is* the oscillation) already for
   $1 < \dt\,\lambda_i < 2$, and $\dt\,\lambda_{\max} \ge 2$ is *divergence*, not
   oscillation; the chapter's own Table 7.2 has a run that oscillates at
   $\dt\,\lambda_y = 4.05$ and one that crashes at $8.1$, and §7.7.3 states the
   distinction correctly ("$0.81 < 1$ decays monotonically, $4.05 > 2$ diverges").
   *Fix:* replace by "oscillation once $\dt\,\lambda_{\max} > 1$ and divergence once
   $\dt\,\lambda_{\max} \ge 2$, with a stiffness growing like the inverse fourth power
   of a passage width".

3. **Theorem 7.3 `thm:ch15-descent`, part (iii) and the corresponding proof step.**
   *Problem (category A):* the bound "$\pos(t)$ stays within $\sqrt{2U_0/k_{\mathrm{att}}}$
   of the goal" and its proof step $\tfrac12 k_{\mathrm{att}}\norm{\pos-\pos_{\mathrm{g}}}^2
   \le U$ are valid only for the *quadratic* attraction. For the hybrid attraction of
   \cref{eq:ch15-hybrid}, which the chapter itself runs in §7.5, one has
   $U_{\mathrm{att}} = k_{\mathrm{att}} d^* d - \tfrac12 k_{\mathrm{att}}(d^*)^2 <
   \tfrac12 k_{\mathrm{att}} d^2$ for $d > d^*$, and the claim is false already at
   $t = 0$: with $k_{\mathrm{att}} = 1$, $d^* = 2$, no obstacles and a start at distance
   $10$, $U_0 = 18$ but $\sqrt{2U_0/k_{\mathrm{att}}} = 6 < 10$. *Fix:* either add
   "with the quadratic attractive potential \cref{eq:ch15-uatt}" to the hypothesis of
   the theorem, or state both bounds: $d \le \sqrt{2U_0/k_{\mathrm{att}}}$ (quadratic)
   and $d \le U_0/(k_{\mathrm{att}} d^*) + d^*/2$ (hybrid, for $d > d^*$). Parts (i)
   and (ii) are correct for both and need no change.

4. **§7.7.4 `sec:ch15-nopassage`, second sentence: "by \cref{thm:ch15-descent} a drone
   inside it would be carried through by the attraction".** *Problem (category A):*
   Theorem 7.3 guarantees only monotone descent, safety and convergence to *some*
   critical point; it cannot rule out a critical point inside the passage and therefore
   does not support "carried through". *Fix:* give the actual reason, which is one line
   of \cref{eq:ch15-gapforce}: on the axis at $x = 4$ the factor $4 - x$ kills the
   horizontal repulsion, so $F_x(4) = 8 - 4 = 4 > 0$ and the force inside the gap points
   at the goal. You may quote the verified run: started at $(4, 4)$, inside the gap, the
   controller reaches the goal in $599$ steps with a minimum clearance of $0.300$
   (`simulate((4,4), (8,4.2), corridor(0.6), ApfParams())`).

5. **§7.7.2 `sec:ch15-gnron` ("a conic pull that makes the drone chatter") together with
   Exercise 7.4(b).** *Problem (categories A and E):* the exercise tells the reader to
   "Run `gnron_case()` with $n = 1$, describe the motion near the goal", but at the
   chapter's default tolerance $\eps_{\mathrm{g}} = 0.05$ that run reports **reached**
   after 508 steps and the reader sees no chatter at all: the predicted chatter has the
   amplitude $\dt\,v_{\max} = 0.01$ and is swallowed by the tolerance. As written the
   exercise cannot be solved as instructed. *Fix:* in §7.7.2 add "the chatter has the
   amplitude $\dt\,v_{\max}$ and is hidden by the goal tolerance $\eps_{\mathrm{g}}$",
   and in Exercise 7.4(b) instruct the run with a tolerance below that amplitude, e.g.
   `simulate((8,6), (5.4,4), DISC, replace(prm, n_gnron=1, goal_tol=1e-3))`. Verified:
   with `goal_tol=1e-3` the $n = 1$ run is declared **stuck** after $695$ steps while
   oscillating at $d \approx 0.0023 \dots 0.0027$, whereas $n = 2$ reaches in $509$
   steps.

6. **§7.8.1 `sec:ch15-basin`, "\Cref{fig:ch15-basin}b shows one of them, from $(0,4.1)$
   on the axis: eight random walks, $3\,810$ steps", and the caption of
   \cref{fig:ch15-basin}(b).** *Problem (category A/C):* $(0, 4.1)$ is not "one of them":
   in the batch run that produced the 386/55 split, that start **times out** at 4000
   steps after 10 escapes. The 8-walk, 3810-step trajectory comes from the separate
   single-drone run in `gen_ch15_field.py`
   (`simulate(starts[pick], BASIN_GOAL, BASIN_OBS, prm, escape=True, rng=default_rng(15))`),
   which draws a different random stream. *Fix:* replace "shows one of them" by "shows a
   separate single-drone run from the trapped start $(0,4.1)$, with its own random
   stream", and say in the caption that the escape trajectory is a single-drone run;
   optionally add "in the batch run the same start is still walking when the horizon
   expires -- the outcome of a random escape is a random variable".

7. **`objectives` box, second bullet ("trace the discrete-time controller with a velocity
   limit") vs §7.5 `sec:ch15-example`.** *Problem (categories C and D):* the chapter never
   traces the controller. §7.5 has only the three-probe-point force table (Table 7.1),
   which the spec asks for, but STYLE_GUIDE §2 item 7 requires a *trace table* of the
   worked example, and the objective promises one. *Fix:* add a second small table to
   §7.5 (caption above, `booktabs`, `\small`, label `tab:ch15-trace`, referenced from the
   text) with 6-8 rows of the run from $(0, 4.5)$ -- suggested columns
   $k$, $\pos_k$, $\rho$, $\vect{F}(\pos_k)$, $\norm{\vect{F}}$, the clipped $\vel$, and
   $\norm{\pos_k - \pos_{\mathrm{g}}}$ -- printed by `worked_example()` at, say,
   $k = 0, 100, 200, 300, 500, 800, 1099$, so that the reader sees the clip binding early
   and releasing near the goal.

8. **\cref{eq:ch15-alignment} (§7.9), "$\vel_i \gets \vel_i + \alpha \sum_{j \in N_i}
   (\vel_j - \vel_i)$".** *Problem (category C):* $N_i$ and $\alpha$ are used without
   being defined; STYLE_GUIDE §3 requires every symbol to be defined before use, and the
   reader needs $\alpha$'s admissible range to connect the update to \cref{ch:ch23}.
   *Fix:* immediately before the equation write "let $N_i = \set{j \ne i \colon
   \norm{\pos_i - \pos_j} \le \rho_{\mathrm{a}}}$ be the neighbours of drone $i$ and
   $\alpha > 0$ the alignment gain, small enough that $\alpha\,\lvert N_i\rvert < 1$".

9. **§7.7.5 `sec:ch15-koren`, "replaced them with the vector field histogram".**
   *Problem (category H):* a named method with no citation; STYLE_GUIDE §3 requires the
   original source. *Fix:* cite Borenstein and Koren, "The Vector Field Histogram -- Fast
   Obstacle Avoidance for Mobile Robots", *IEEE Transactions on Robotics and Automation*
   7(3):278-288, 1991, added to `Overleaf/bib/ch15-extra.bib` as
   `borenstein1991vfh`, and mention it again in the further-reading paragraph.

10. **`summary` box, fifth bullet, "while \orca and DWA take the safety layer" (and
    §7.1, §7.11).** *Problem (category F):* "DWA" is never expanded in this chapter --
    the text always writes "the dynamic window approach" -- and STYLE_GUIDE §3 requires
    each acronym to be defined at first use *in every chapter*. *Fix:* at its first
    occurrence in §7.1 write "the dynamic window approach (DWA) of \cref{ch:ch14}".

## Suggestions

1. **Length (category G, not required).** The chapter body is 20 pages against
   STYLE_GUIDE's 12-18 and the spec's 11-13. I found no padding worth cutting on
   content grounds -- the spec demands nine figures' worth of material -- but about a
   page can be recovered without losing anything: (a) the claim "the stiffness grows
   like the inverse fourth power of the width" is made three times (end of §7.7.3, §7.7.5
   bullet 2, summary bullet 3) and the claim "the first-order controller never
   oscillates in continuous time" twice (end of §7.7.3 and §7.7.5 bullet 2) -- keep one
   of each; (b) the $w = 1.6$ rows of Table 7.2 add nothing beyond $w = 1.2$; (c) the
   last two sentences of the §7.5 paragraph on the hybrid run restate what Table 7.1's
   caption already says.
2. **Proposition 7.7.** The "if and only if" is indeterminate at
   $\dt\,\lambda_{\max} = 2$ exactly (the linearisation is marginally stable and
   Lyapunov's indirect method says nothing). Write "asymptotically stable if
   $\dt\,\lambda_{\max} < 2$ and unstable if $\dt\,\lambda_{\max} > 2$".
3. **§7.7.4.** "has its root at $x = 3.163$" -- $F_x$ has two roots on the axis in
   $(1,4)$: the stable one at $3.163$ where the drone stops and an unstable one near
   $x \approx 3.9$; write "its first root".
4. **Remark 7.6.** The Euler-characteristic count needs the potential to be a *Morse*
   function; add "Morse" to the hypothesis ("every smooth Morse potential that ...").
5. **Exercises.** Only one of the eight is `\difficulty{1}` and none is purely
   conceptual. Consider adding a one-star conceptual exercise, e.g. "explain why
   $\vect{F}$ is continuous but not $C^1$ across $\rho = \rho_0$, and why the stuck
   detector of line \ref{alg:ch15-descend:stuck} cannot distinguish a local minimum from
   a very flat region of $U$".
6. **Solutions.** `appendices/solutions/ch15-solutions.tex` covers 4 of the 8 exercises
   (7.1, 7.3, 7.4, 7.5). This matches the book's practice (ch12 and ch16 also have 4),
   but sketches for 7.2 (a two-line calculation) and 7.6 (the answer is
   $k_{\mathrm{att}}$ between $2.0$ and $2.5$: at $k_{\mathrm{att}} = 2$ the drone still
   stops at $x = 3.464$, at $2.5$ it crosses in 871 steps) would help a reader working
   alone.
7. **§7.7.2.** When introducing \cref{eq:ch15-gnron-u} it is worth saying that Ge and
   Cui recommend $n = 2$ for exactly the reason Proposition 7.4(c) gives, so the reader
   knows the chapter's default is the source's.

## What must be kept

The failure-mode section is the best thing in this chapter and must survive revision
intact: four failure modes, each with its own runnable case, its own figure and -- the
part that lifts this above every textbook treatment I know -- its own *formula*.
\cref{eq:ch15-axis} with its bisected root, \cref{eq:ch15-gapforce} with the two
repulsions adding in front of a free gap, and the lateral stiffness
\cref{eq:ch15-stiffness} tied through Proposition 7.7 to the three runs of
\cref{fig:ch15-oscillation} and the ten rows of \cref{tab:ch15-corridor} turn "potential
fields have problems" into arithmetic the reader can redo. Keep Theorem 7.3 with its
explicit clearance bound $\rho_{\min}$, and keep Remark 7.6: the topological lower bound
on the number of critical points is what makes the later navigation-function paragraph
mean something instead of sounding like a better tuning. Keep the honest Koren-Borenstein
subsection, and in particular its separation of structural failures from
implementation-dependent ones -- that is a genuinely useful piece of scholarship. Keep
the basin experiment and the sentence that the failures are properties of *regions* of
the start space, not of the scene, together with the instruction to sweep a grid of
starts; keep the waypoint/local-layer framing and the drone box's frank explanation of
why the safety layer is ORCA/DWA and what potential fields are still good for. Keep the
code as it is: vectorised over drones, self-testing in 4.5 s, with the analytic forces
checked against central differences, and reproducing the chapter's numbers to the last
digit. Keep all nine figures and their captions, which consistently tell the reader what
to notice rather than what is drawn.
