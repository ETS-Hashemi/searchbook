# Review of Chapter 15 (Artificial Potential Fields) - round 2

Reviewed: `Overleaf/chapters/ch15-potential-fields.tex` (1427 lines), the nine figure
files in `Overleaf/figures/ch15/`, `Overleaf/code/ch15_potential_fields.py` (576 lines),
`Overleaf/code/figures/gen_ch15_field.py`, `Overleaf/bib/ch15-extra.bib`,
`Overleaf/appendices/glossary/ch15-terms.tex`,
`Overleaf/appendices/solutions/ch15-solutions.tex`, against `STYLE_GUIDE.md` §9,
`docs/specs/ch15.md` and `docs/core-idea.txt` (Week 7), plus the round-1 review and the
reviser's response appended to it.

**Round-1 items.** All ten required changes of round 1 are resolved, and resolved
correctly. I re-verified each: (1) the escape means now read `1.24` per arriving drone
with the `2.48` all-starts figure in parentheses, and both are printed by the self-test;
(2) the summary bullet now separates oscillation (`\dt\lambda_{\max} > 1`) from
divergence; (3) Theorem 7.3(iii) carries both bounds, and I re-derived the hybrid one,
`d \le U_0/(k_{att}d^*) + d^*/2`, which is right; (4) §7.7.4 now gives the algebra
`F_x(4) = 8 - 4 = 4 > 0` instead of appealing to Theorem 7.3, and the `(4,4)` run (599
steps, clearance 0.300) is asserted by the self-test; the "first root at 3.163, second
near 3.91" is exactly what I get by bisection (3.1634 and 3.9128); (5) §7.7.2 states the
chatter amplitude and Exercise 7.4(b) now prescribes `goal_tol=1e-3`, which the self-test
runs (n = 1 stuck after 695 steps, n = 2 reached in 509); (6) the basin text and caption
now say "a separate single-drone run ... with its own random stream"; (7) `tab:ch15-trace`
is present, `booktabs`, `\small`, caption above, referenced with `\cref`, and every one of
its seven rows matches the self-test output character for character; (8) `N_i` and
`\alpha` are defined before `eq:ch15-alignment`; (9) `borenstein1991vfh` exists, is cited
at the VFH mention and in further reading, and the bibliographic details are correct;
(10) DWA is expanded in §7.1. None of these is re-raised below.

**Build.** `./build.sh ch15-potential-fields` returns status 0. No `!` errors. The only
undefined references are `ch:ch11`, `ch:ch13`, `ch:ch14`, `ch:ch21` — cross-chapter, and
legitimate in a single-chapter build. Exactly one overfull box in the whole document
(29.10 pt) and it is the RRT entry of the glossary appendix, not this chapter.
Chapter body = PDF pages 24-44, i.e. **21 pages** (one more than round 1, the trace table).

**Code.** `python3 code/ch15_potential_fields.py` passes in 3.3 s. I re-checked the
numbers of the text independently, including those the self-test does not print: path
length 8.9574 against a straight line of 8.0156 (11.75 %, "about 12 %"); the saddle
Hessian eigenvalues at `(2.4872, 4)` (−2.65, 36.97 by central differences); the basin
minimum eigenvalues at `(2.676, 4.1)` (9.87, 24.89, exact); the waypoint run (1188 steps,
both legs "reached"); the swarm run (`dt = 0.02`, 1500 steps = 30 time units, every drone
within 0.3 of its goal, min separation 1.044 against 0.000). I also recomputed
`eq:ch15-gapforce` on a 40 001-point grid: minimum −6.0128 ("−6.01"), roots 3.1634 and
3.9128. `eq:ch15-stiffness` I re-derived by hand and evaluated for all five widths
(667.7, 204.1, 81.0, 38.0, 11.7) — all five table entries are right. Two numeric claims
in the text do **not** hold up (Required changes 1 and 2).

## Verdict

**Minor revision.** The chapter is technically strong and the round-1 revision was done
honestly and completely. Every definition, every derivation (chain rule for the FIRAS
force, the GNRON product rule, `eq:ch15-axis`, `eq:ch15-gapforce`, `eq:ch15-stiffness`),
both theorem statements and all four proofs, the Rimon-Koditschek navigation function
`eq:ch15-navfun`, the Euler-characteristic count in Remark 7.9 and the complexity claim
are correct as written; I checked each against the canonical sources and, where a number
was involved, against a script. Every "must cover" item of `docs/specs/ch15.md` is
present, the nine figures are all referenced with captions that say what to notice, there
are 30 index entries, 9 exercises with a 2/5/2 difficulty spread including the Week-7
coding exercise and a derivation exercise, and all twelve citation keys resolve to real
references whose authors, titles, venues, volumes, pages and years I can vouch for. The
five required changes are all local: one false equivalence, one number quoted for the
wrong geometry, one dead cross-reference used twice in proofs, one solution sketch that
no longer answers its exercise, and one caption that is off by one step.

## Required changes

1. **§7.3 `sec:ch15-problem`, the paragraph after `def:ch15-attractive`: "Clipping the
   quadratic force at a speed $v_{\max}$, as the controller of \cref{sec:ch15-algorithm}
   does, is the same as the hybrid potential with $d^* = v_{\max}/k_{\mathrm{att}}$, so
   the examples of this chapter use the quadratic bowl ...".**
   *Problem (category A):* the equivalence holds for the attractive force alone, but the
   controller clips the **total** force (line~\ref{alg:ch15-descend:clip}), i.e. after the
   vector sum with the repulsions, whereas the hybrid potential caps the attraction
   **before** the sum. Near an obstacle the two therefore give different fields and
   different trajectories, and the sentence — which is the stated justification for the
   chapter's whole parameter choice — is false where the chapter needs it most.
   Verified: from $(0, 4.5)$ in the scene of `ex:ch15-disc`, `ApfParams()` (quadratic +
   clip at $v_{\max}=1$) reaches the goal in **1099** steps with clearance **0.519** and a
   path of 8.957, while `replace(prm, d_star=1.0)` — the supposedly identical hybrid with
   $d^* = v_{\max}/k_{\mathrm{att}} = 1$ — takes **1474** steps with clearance **0.840**
   and a path of 9.254.
   *Fix:* qualify the claim and name the exception, e.g. "Away from obstacles, clipping
   the quadratic force at $v_{\max}$ gives the same command as the hybrid potential with
   $d^* = v_{\max}/k_{\mathrm{att}}$ (\cref{exr:ch15-conic}); inside an influence region
   the two differ, because the controller clips the *sum* while the hybrid caps the
   attraction before the repulsion is added — from $(0,4.5)$ the clipped quadratic field
   keeps a clearance of $0.519$ and the hybrid one with $d^*=1$ a clearance of $0.840$.
   The examples of this chapter use the quadratic bowl with $k_{\mathrm{att}} = 1$ and
   $v_{\max} = 1$." Exercise 7.2(b) itself is fine as stated (it speaks of the attractive
   force only) and needs no change.

2. **§7.7.1 `sec:ch15-localmin`, last sentence: "although a free path over or under the
   disc exists and is only $12\,\%$ longer than the straight line".**
   *Problem (category A):* $12\,\%$ is the excess of the trajectory of §7.5, which starts
   at $(0, 4.5)$ and is measured against its own straight line of $8.016$. In §7.7.1 the
   start is $(0, 4)$ and the straight line is $8$; there the **shortest** free path (two
   tangents plus the arc, $2\sqrt{15} + \arccos$-arc) is $8.2513$, i.e. only $3.1\,\%$
   longer, and even a path that keeps the controller's own clearance of $0.519$ is
   $8.584$, i.e. $7.3\,\%$. The number is quoted for the wrong geometry and understates
   the point the sentence is making.
   *Fix:* write "although a free path over or under the disc exists: the shortest one is
   $8.25$ units against the straight-line $8$, only $3\,\%$ longer, and even one that
   keeps the clearance $0.519$ of \cref{fig:ch15-field} costs $7\,\%$." (Keep the $12\,\%$
   in §7.5, where it is correct for the run from $(0, 4.5)$.)

3. **Proof of `thm:ch15-descent` ("LaSalle's invariance principle (\cref{ch:appB})") and
   proof of `thm:ch15-stability` ("Lyapunov's indirect method, \cref{ch:appB}").**
   *Problem (categories F and H):* `Overleaf/appendices/appB-math-refresher.tex` contains
   neither result — its sections are vectors and matrices, calculus for motion,
   probability and Gaussians, optimization (including a *Gradient descent* subsection),
   graphs and the Laplacian, complexity and data structures; `grep -i "lasalle\|lyapunov"`
   returns nothing. Both proofs therefore send the reader to an appendix that does not
   contain the theorem they rest on, and a reader working alone has no way to close the
   gap. The reference resolves at build time, so nothing flags it.
   *Fix:* replace both `\cref{ch:appB}` pointers by a citation to a standard text —
   Khalil, *Nonlinear Systems*, 3rd ed., Prentice Hall, 2002 (LaSalle's invariance
   principle and the linearisation/indirect method are both there), added to
   `Overleaf/bib/ch15-extra.bib` as `khalil2002nonlinear` and named once in further
   reading. Do not cite theorem numbers. If you prefer to keep the appendix pointer, keep
   `\cref{ch:appB}` only for the eigenvalue facts of §B.1.3 that the proof of
   `thm:ch15-stability` also uses, and state LaSalle in one sentence inline ("a bounded
   trajectory of a gradient flow on a compact positively invariant set converges to the
   set where $\nabla U = \vect{0}$"), with the citation.

4. **`Overleaf/appendices/solutions/ch15-solutions.tex`, `\begin{solution}{exr:ch15-gnron}`,
   the sentences on $n = 1$.** *Problem (category E):* Exercise 7.4(b) was rewritten in
   round 1 and now instructs the reader to run
   `simulate((8,6), (5.4,4), DISC, replace(prm, n_gnron=1, goal_tol=1e-3))` and to "say
   what each run reports". The solution still describes the old run: "the drone reaches
   the goal from every side along a straight final approach and would chatter around it
   without a goal tolerance". With the tolerance the exercise now prescribes, the run is
   declared **stuck after 695 steps** with a chatter of at most $0.0074$, so the solution
   contradicts the outcome the reader will see and never answers the question asked.
   *Fix:* replace those two sentences by: "For $n = 1$ the goal is still the global
   minimum, but the force does not vanish there: the drone chatters across the goal with
   an amplitude of one step, $\dt\,v_{\max} = 0.01$. With the chapter's tolerance
   $\eps_{\mathrm{g}} = 0.05$ the chatter is inside the tolerance and the run reports
   *reached* after 508 steps; with `goal_tol=1e-3` the same run reports *stuck* after 695
   steps, the chatter staying below $0.0074$. With $n = 2$ the force does vanish at the
   goal and the run reports *reached* after 509 steps at either tolerance."

5. **Caption of `fig:ch15-oscillation`: "with $\dt = 0.10$ and no limit (red) the second
   step inside the passage overshoots the axis by more than the half-width and the drone
   crashes".** *Problem (category D):* off by one. In
   `figures/data/ch15-osc-crash.dat` the drone first enters the gap ($|x - 4| < 1$) at the
   sample $x = 3.1466$, $e = 0.182$; the next steps have $e = -0.0685$ (first), $e =
   +0.1497$ (second) and $e = -0.8014$ (third), and only the third exceeds the half-width
   $0.5$ — that is the collision, at step 8 of 8, inside the lower disc.
   *Fix:* "with $\dt = 0.10$ and no limit (red) the lateral error doubles at every step
   and the third step inside the passage overshoots the axis by $0.80$, more than the
   half-width $0.5$, so the drone ends inside the lower disc after $8$ steps."

## Suggestions

1. **`eq:ch15-gapforce` has no domain clause.** `eq:ch15-axis` is introduced "for
   $1 \le x < 3$, inside the influence region"; `eq:ch15-gapforce` is not, yet the text
   says it is "plotted in \cref{fig:ch15-nopassage}b" and the plotted data
   (`ch15-nopassage-profile.dat`) comes from `total_force`, which masks the repulsion at
   $\rho > \rho_0$. Written without the mask the formula turns the repulsion into a small
   attraction outside the influence region (at $x = 0$ it gives $8.035$ instead of $8$).
   Add "for $\rho \le \rho_0$, and $F_x = 8 - x$ beyond" after the equation. Nothing in
   the chapter's conclusions changes; all the points it is used at ($x = 4$, $x = 3.163$,
   $x = 3.91$) lie inside the influence region.
2. **Summary bullet 3 versus Proposition 7.10.** The bullet says "divergence once
   $\dt\,\lambda_{\max} \ge 2$" while the proposition (correctly, after round 1) says
   unstable for $> 2$ and "decides nothing" at $= 2$. Change the bullet's $\ge$ to $>$.
3. **Length (category G, not required).** 21 PDF pages against `STYLE_GUIDE` §2's 12-18
   and the spec's 11-13. As in round 1 I find no padding whose removal would not cost
   required content: the spec asks for nine figures, four failure modes each with its own
   run, figure and formula, four remedies, the swarm section and the basin experiment.
   About half a page can still be recovered without loss: (a) the paragraph after
   `tab:ch15-trace` re-narrates rows the caption already reads (keep the clip-release and
   the $\ln(1.007/0.05)$ sentences, drop the $k = 300$ sentence, which duplicates the row);
   (b) the $w = 1.6$ rows of `tab:ch15-corridor` add nothing beyond $w = 1.2$; (c) §7.8.1's
   "In the batch run that start is still walking when the horizon expires" repeats the last
   sentence of the `fig:ch15-basin` caption verbatim — keep it in one place.
4. **`\rho_{ij}`.** The notation table (`frontmatter/notation.tex`, line 151) already uses
   $\rho_{ij}$ for a Gaussian correlation in `ch:ch02`, and `eq:ch15-interagent` uses it
   for an inter-agent clearance. Both are listed against their chapters, so this is
   legal, but a one-clause reminder at `eq:ch15-interagent` ("$\rho_{ij}$ here is a
   clearance, not the correlation of \cref{ch:ch02}") would save a reader a double take.
5. **§7.9, the swarm run.** The text gives $k_{\mathrm{a}} = 1$, $\rho_{\mathrm{a}} = 1.5$
   and $r = 0.25$ but not the control period; the self-test uses $\dt = 0.02$ for 1500
   steps, which is where "30 time units" comes from. Add "$\dt = 0.02$" so the reader can
   reproduce the 1.044.
6. **Solutions coverage.** Six of the nine exercises now have sketches — better than the
   book's average. Exercise 7.7 (`exr:ch15-smoothness`), being new and one-star, would
   benefit from three lines: the force is $C^0$ but not $C^1$ at $\rho = \rho_0$ because
   the second derivative jumps from $k_{\mathrm{rep}}/\rho_0^4$ to $0$ (stated just after
   `thm:ch15-continuity`), so a finite-difference stiffness estimate straddling the
   boundary averages two different curvatures.
7. **`fig:ch15-oscillation` legend** writes "$\dt = 0.01$ s" while the body never attaches
   a unit to $\dt$. Drop the "s" or introduce the unit once in §7.4.

## What must be kept

The failure-mode section remains the best thing in the chapter and must survive intact:
four failure modes, each with a runnable case, its own figure and — the part that lifts
this above every textbook treatment I know — its own *formula*. `eq:ch15-axis` with its
bisected root, `eq:ch15-gapforce` with the two repulsions adding in front of a free gap
and its two roots, and the lateral stiffness `eq:ch15-stiffness` tied through Proposition
7.10 to the three runs of `fig:ch15-oscillation` and the ten rows of `tab:ch15-corridor`
turn "potential fields have problems" into arithmetic the reader can redo; I redid all of
it and it is right. Keep Theorem 7.3 with its explicit clearance bound $\rho_{\min}$ and
its now two-branch bound (iii); keep Remark 7.9, whose Euler-characteristic count is what
makes the navigation-function paragraph mean something instead of sounding like better
tuning. Keep the new `tab:ch15-trace` and the paragraph that reads it: the clip binding in
every row but the last, and the exponential tail predicted to 0.01 time units, are exactly
the two things a reader needs to see once. Keep the honest Koren-Borenstein subsection and
its separation of structural failures from implementation-dependent ones. Keep the basin
experiment, the sentence that the failures are properties of *regions* of the start space
rather than of the scene, and the round-1 correction that an escape outcome is a random
variable and not a property of the start — that paragraph now teaches experimental
honesty as well as potential fields. Keep the waypoint/local-layer framing, the drone
box's frank explanation of why the safety layer is ORCA/DWA, and the code as it is:
vectorised over drones, self-testing in 3.3 s, analytic forces checked against central
differences, and reproducing every quoted number to the last digit. Keep all nine figures
and their captions, which tell the reader what to notice rather than what is drawn.

## Response to review (round 2)

All five required changes are applied; the chapter builds with status 0, no errors and no
undefined citations, the self-test of `code/ch15_potential_fields.py` passes unchanged
(3.3 s), and the chapter is 21 PDF pages. No `.dat` file was regenerated because the code
was not touched.

**A (§7.3, the clipping equivalence).** Applied. The sentence after
`def:ch15-attractive` now reads: away from obstacles the clip at $v_{\max}$ gives the same
command as the hybrid with $d^* = v_{\max}/k_{\mathrm{att}}$ (`exr:ch15-conic`); inside an
influence region the two differ, because the controller clips the *sum* while the hybrid
caps the attraction before the repulsion is added -- from $(0,4.5)$ in `ex:ch15-disc` the
clipped field keeps a clearance of $0.519$, the hybrid one with $d^* = 1$ a clearance of
$0.840$. Both numbers re-verified against the code (1099 steps / 0.5186 and 1474 /
0.8405). Exercise 7.2(b) left as it was.

**A (§7.7.1, the 12 %).** Applied. The sentence now reads: "a free path over or under the
disc exists: the shortest one, two tangents and an arc, is 8.25 units against the
straight-line 8, only 3 % longer, and even one that keeps the clearance 0.519 of
`fig:ch15-field` costs 7 %." Recomputed independently: $2\sqrt{15} + \arccos$-arc
$= 8.2513$ (3.1 %) and, with the offset radius $1.519$, $8.5844$ (7.3 %). The 12 % in §7.5
is unchanged, where it is correct for the run from $(0,4.5)$.

**F (LaSalle / Lyapunov pointing at `ch:appB`).** Applied, first option. Both
`\cref{ch:appB}` pointers in the proofs of `thm:ch15-descent` and `thm:ch15-stability` are
replaced by `\cite{khalil2002nonlinear}`; `khalil2002nonlinear` (Khalil, *Nonlinear
Systems*, 3rd ed., Prentice Hall, 2002) was added to `bib/ch15-extra.bib` and named once in
further reading. No theorem numbers are cited. `references.bib` was not touched.

**E (solution of `exr:ch15-gnron`).** Applied, with one number corrected. The two stale
sentences are replaced by the chatter/tolerance explanation the exercise now asks for:
chatter amplitude one step, $\dt\,v_{\max} = 0.01$; reached after 508 steps at
$\eps_{\mathrm{g}} = 0.05$; stuck after 695 steps with `goal_tol=1e-3`, the distance to the
goal alternating between 0.0027 and 0.0074. **Deviation:** the review's suggested wording
says $n = 2$ "reports reached after 509 steps at either tolerance"; the run reports 509
steps only at `goal_tol=1e-3` and 425 steps at $\eps_{\mathrm{g}} = 0.05$ (the code's own
self-test prints both), so the solution states the two figures separately.

**D (caption of `fig:ch15-oscillation`, off by one).** Applied. The caption now reads:
"the lateral error changes sign and grows at every step inside the passage, and the third
step there overshoots the axis by 0.80, more than the half-width 0.5, so the drone ends
inside the lower disc after 8 steps." **Deviation:** the suggested "doubles at every step"
is not what `ch15-osc-crash.dat` shows (the lateral error goes $0.182 \to -0.0685 \to
0.1497 \to -0.8014$, i.e. it shrinks once, then grows by 2.2 and 5.4), so the caption says
"changes sign and grows at every step inside the passage" instead; the corrected step index,
the 0.80 overshoot and the 8 steps are exactly as required.

**Suggestions.** 1 (domain clause on `eq:ch15-gapforce`), 2 ($\ge 2 \to > 2$ in summary
bullet 3), 3a/3b/3c (the $k = 300$ sentence after `tab:ch15-trace`, the $w = 1.6$ rows of
`tab:ch15-corridor` and the sentence duplicated between §7.8.1 and the `fig:ch15-basin`
caption -- the round-1 correction about the random escape stays in the body paragraph), 4
($\rho_{ij}$ reminder at `eq:ch15-interagent`), 5 ($\dt = 0.02$ in §7.9), 6 (a solution
sketch for `exr:ch15-smoothness`) and 7 (the "s" dropped from the `fig:ch15-oscillation`
legend) are all applied. On 3 (length): the trims plus some tightening of the new material
and of the coding exercise's wording hold the chapter at 21 pages with every required
addition in place; nothing the "what must be kept" list names was removed.
