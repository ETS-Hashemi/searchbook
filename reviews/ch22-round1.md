# Review of Chapter 22 (Mixed-Integer Linear Programming for Planning) - round 1

## Verdict

**Minor revision.**

The chapter is technically strong, complete against `docs/specs/ch22.md`, and unusually
honest: it not only builds the MILP but shows where the sampled model lies (the
minimum-time plan lets the two drones fly through each other), quantifies the price of
exactness with a committed, reproducible experiment, and states plainly when MILP is the
wrong tool. It builds cleanly (status 0, no errors, no undefined labels of its own, no
overfull box inside the chapter - the single overfull `\hbox` in the log, at log line
1959, is in the front-matter list of algorithms), the code runs and passes its self-test
in 47 s, all six figures and five tables are referenced, and every citation key resolves.

Eight required changes remain, all of them local edits (a value, an index set, a sentence,
a caption, one table column, a handful of measured seconds); none requires restructuring.
Three are genuine technical errors (items 1, 2, 3), one is a stale set of numbers that the
code does not reproduce (item 4), and the rest are clarity/figure/exercise items. Length is
20.0 pages of chapter body (PDF pages 179-198 of `build/only-ch22-milp.pdf`), i.e. at the
20-page ceiling but well above the 11-13 page target of the spec; because every section
maps to a "must cover" item I require **no** cuts and instead list trim candidates as
suggestions.

## Required changes

1. **`sec:ch22-implementation`, paragraph "Symmetry", line 1119 - the symmetry-breaking
   binary has the wrong value.** The text says: "fix the side for one pair
   (`$c^{12}_{k,1} = 1$` for all $k$, say, when you know drone~1 should stay on one side)".
   By the chapter's own convention (\cref{eq:ch22-sep} and \cref{sec:ch22-bigm}: "$b_j = 1$
   relaxes the inequality ... it is switched *off*"), $c^{12}_{k,1}=1$ *switches off*
   $x^1_k - x^2_k \ge d_{\min}$, i.e. it forbids that direction from being the separating
   one; it does not fix a side. **Fix:** either write $c^{12}_{k,1} = 0$ for all $k$ and
   say what it enforces ("drone 1 stays at least $d_{\min}$ to the right of drone 2 at
   every step, which is legitimate only when you know an optimal plan of that shape
   exists"), or keep the value 1 and reword to "forbid one of the four disjuncts for one
   pair, which removes the mirror-image subtree". Make the wording of the solution of
   \cref{exr:ch22-coding}(d) (`appendices/solutions/ch22-solutions.tex`, line 69, fixes
   `model.cpair((0,1),k,0)` to $1$ and calls it "forbids drone 1 to the right of drone 2")
   consistent with whichever reading you choose. *Category A.*

2. **`sec:ch22-mapf-ilp`, line 897 - the sum-of-costs objective of the MAPF ILP is off by
   one per agent.** The text writes the objective as
   $\sum_i \sum_{e \notin \delta^-(g_i,\cdot)} f^i_e$ and claims it "agrees with the
   definition of \cref{ch:ch07}". Since $\delta^-(g_i,\cdot)$ contains *every* edge
   entering the goal, the agent's final arrival move is excluded as well, so the sum is
   $\sum_i (t_i - 1) = \mathrm{SOC} - m$, not the sum of costs. **Fix:** exclude only the
   goal wait edges, i.e. write
   $\sum_i \sum_{e \ne ((g_i,t)\to(g_i,t+1))} f^i_e$ ("all edges of agent $i$ except the
   self-loops at its own goal"), and keep the existing proviso that no agent leaves its
   goal again; alternatively keep the current index set and state that it differs from the
   sum of costs by the constant $m$, which does not change the optimiser. *Category A.*

3. **`sec:ch22-intuition`, line 79 - interior-point methods do not converge to a vertex.**
   "interior-point methods travel through the inside and converge to the same vertex" is
   wrong (and contradicts the chapter's own correct sentence at line ~176, "follow a path
   through the interior of $P$ towards the optimal face"): an interior-point method
   converges to a point in the relative interior of the optimal face - the analytic centre
   - and a vertex is produced only by a crossover step; the optimum need not be unique.
   **Fix:** "interior-point methods travel through the inside and converge to a point of
   the optimal face, from which a crossover step recovers a vertex when one is wanted."
   *Category A.*

4. **`tab:ch22-sizes` (lines 649-657), `sec:ch22-example` line 633, `sec:ch22-implementation`
   line 1130, and `appendices/solutions/ch22-solutions.tex` line 26 - the solve times are
   not reproduced by the code.** Running `python3 code/ch22_milp.py` on the review machine
   gives, against the values printed in the chapter: fuel **1.96 s** (text and table say
   1.2 s), peak **0.145 s** (table 0.09), time **0.481 s** (table 0.28), $\dt = 0.25$ run
   **22.1 s** (text "about 14 s"), safe-margin instance **2.96 s** (solution "about 1.3 s").
   Every *node count* matches exactly (366, 1, 1, 4103, 48), so only the wall-clock numbers
   are stale; note also that `figures/data/ch22-scaling.dat` reports 1.234 s for the
   comparable two-drone crossing instance, so the chapter's 1.2 s and the committed data
   were plausibly measured on a faster machine than the one that must reproduce them.
   **Fix:** re-run `code/ch22_milp.py` and `code/figures/gen_ch22_scaling.py` on one
   machine, quote those times, and replace the caption sentence "Times vary by a few
   tenths of a second between runs" by a footnote naming the hardware and the HiGHS version
   ("measured with SciPy x.y / HiGHS 1.x on one core of ..."); or, if you prefer numbers
   that never rot, drop the absolute seconds from the running text and keep only the node
   counts plus a relative statement ("about twenty times the fuel instance"). *Category A.*

5. **`tab:ch22-binaries`, caption line 372 - the caption describes a column that is not in
   the table.** "...and the number of leaves $2^{\text{binaries}}$ that a search without
   bounding would have to visit" - the table has only $m$, $\binom{m}{2}$ and the binary
   counts for $N = 10, 20, 50$. **Fix:** either add the promised column (for $N = 10$:
   $2^{120} \approx 10^{36}$, $2^{240}\approx 10^{72}$, $2^{600}\approx 10^{180}$, ... - one
   order-of-magnitude column is enough and makes the point), or delete the clause from the
   caption and leave the observation in the body paragraph, which already says "every
   binary can in principle double the size of the search tree". *Category D.*

6. **`sec:ch22-intuition` (lines 88-104) and `fig:ch22-relaxation` - the concept figure
   silently switches to a maximisation.** \cref{def:ch22-lp} and \cref{alg:ch22-bnb} are
   minimisations, but the figure, its caption ("value $10$ ... an upper bound on it") and
   \cref{exr:ch22-lp} maximise $x + 2y$. The body text says only "its value is a bound on
   the integer optimum", which a reader following the minimisation convention will read as
   a lower bound; the figure then shows an upper bound. **Fix:** say it once in the
   paragraph and once in the caption, e.g. "This example *maximises* $x + 2y$ (equivalently
   minimises $-x-2y$), so the relaxation gives an upper bound; for the minimisation of
   \cref{def:ch22-lp} the relaxation value is a lower bound." *Category C.*

7. **`appendices/solutions/ch22-solutions.tex`, solution of `exr:ch22-mapfilp`, line 49 -
   "every state has five outgoing edges" is false on the boundary of the grid.** On a
   $32\times32$ 4-connected grid a corner cell has 3 outgoing edges and an edge cell 4, so
   $\sum_v(\deg v + 1) = 1024 + 2\cdot(2\cdot32\cdot31) = 4992$, not $5\cdot1024 = 5120$.
   **Fix:** "interior states have five outgoing edges; counting the boundary,
   $\sum_v(\deg v + 1) = 4992$, so $20 \cdot 60 \cdot 4992 \approx 6.0\cdot10^6$ binaries",
   and give the anti-swap row count as $1984 \cdot 60 \approx 1.2\cdot10^5$ (there are
   $2\cdot32\cdot31 = 1984$ undirected grid edges). The chapter's own "about six million"
   (line ~915) is then exact rather than approximate. *Category A.*

8. **`exr:ch22-coding` (part (a)) and its solution - the exercise can run for a minute with
   no stated target and no time limit.** Verified on the review machine: the courtyard
   instance (3 drones, block $[4,6]\times[2,6]$, $N = 12$, fuel) is *solvable to proven
   optimality* - status 0, $J_{\mathrm{fuel}} = 21.19$~m/s, 288 binaries, 9755 nodes - but
   it takes 45 s, and part (a) also asks for the minimum-time variant, which is untested.
   A reader working alone has no way to know whether a long run means a mistake.
   **Fix:** in part (a) instruct "solve with `solve_instance(inst, time_limit=120)` and
   report `sol.status` and `sol.gap` if the limit strikes", and add the reference numbers
   to the solution ("the fuel optimum is $21.19$~m/s with 288 binaries and about ten
   thousand nodes; the run takes tens of seconds"), so the answer is checkable.
   *Category E.*

## Suggestions

* **Length (20.0 pages against the spec's 11-13).** No cut is required, but if you want
  the chapter shorter, the padding is here, in this order: (i) the paragraph after
  \cref{tab:ch22-verdict} ("\cref{tab:ch22-verdict} states the verdict ... fifty drones ten
  times a second") repeats the table it follows *and* the closing of
  \cref{sec:ch22-motivation} - two sentences suffice; (ii) the "Two lessons of the example"
  paragraph after \cref{ex:ch22-tiny} repeats the weak-relaxation argument of
  \cref{sec:ch22-bigm} and pre-announces the symmetry discussion of
  \cref{sec:ch22-implementation}; (iii) the narrative of \cref{sec:ch22-cost} restates
  numbers that \cref{fig:ch22-scaling} already shows - keep the one-drone/two-drone/three-drone
  sentence and the "what the solver fights" sentence, drop the rest.
* `sec:ch22-lp`, line 174: "an LP with $10^5$ variables is solved in well under a second"
  is optimistic for a general sparse LP; the sentence two lines earlier ("hundreds of
  thousands of variables in seconds") is the safer claim - keep only that one.
* `sec:ch22-example`: the worked example has a size table but no per-step trace table,
  while the trace table (\cref{tab:ch22-trace}) belongs to the *tiny* example. The
  self-test already prints $k$, $\pos^A_k$, $\pos^B_k$, $\norm{\cdot}_\infty$ for the
  twelve steps; turning that into a small `booktabs` table would satisfy the template's
  "worked example: figure + trace table" literally and would let the reader check the
  active separation at $k=6$.
* `figures/ch22/scaling.tex`, line 19: the right axis is labelled "MIP gap after 30 s"
  although the $m = 1$ and $m = 2$ runs finished before the limit (their gap is 0 because
  they were solved, not because 30 s were enough). "final MIP gap [%]" matches the caption.
* `figures/ch22/timeexpanded.tex`: the anti-swap annotation is written with fixed agent
  indices, $f^1_{(b,1)\to(d,2)} + f^2_{(d,1)\to(b,2)} \le 1$, while
  \cref{eq:ch22-mapf-swap} sums over all agents in both directions. Write $\sum_i$ or add
  "for the two agents shown".
* `eq:ch22-sep` uses a single $M$ in all four rows, and the paragraph after it then gives
  two different tight values ($x$-rows and $y$-rows). Writing $M_x$, $M_y$ in the equation
  removes the overload, as \cref{eq:ch22-tightM} does for the obstacle rows.
* `alg:ch22-bnb`, the line after `SolveRelaxation`: "\If{$Q$ is infeasible}" should read
  "if the relaxation is infeasible" - that is what the solver reports, and the implication
  (relaxation infeasible $\Rightarrow$ node infeasible) is exactly the argument the proof
  of \cref{thm:ch22-bnb} uses.
* `thm:ch22-complexity` labels a `proposition` with the `thm:` prefix while
  `prop:ch22-bigm` and `prop:ch22-intersample` use `prop:`; rename to
  `prop:ch22-complexity` (two references, lines ~800 and in the summary). *Category F,
  cosmetic.*
* `tab:ch22-sizes`, "Optimum" column: the min-time row shows the arrival times
  ($4.5 + 4.5$ s) while the code's printed objective is $9.016$ (arrival plus the $10^{-3}$
  fuel tie-breaker). A footnote saying so would prevent a reader from thinking the code
  disagrees.
* `sec:ch22-implementation`: it would be worth naming the SciPy fields the text refers to
  (`res.mip_gap`, `res.mip_node_count`), since the surrounding prose promises "the node
  count and the gap".
* `sec:ch22-example`: giving the four tight $M$ values of this instance in one clause would
  connect the worked example to \cref{exr:ch22-tightm}, which asks for exactly them.

## What must be kept

The spine of this chapter is excellent and should survive revision untouched. Keep the
big-$M$ derivation with \cref{prop:ch22-bigm} and its proof, and the explicit tight
constants of \cref{eq:ch22-tightM} - it is rare to see a textbook derive $M$ instead of
writing $10^6$, and the "hurts twice" argument (weak relaxation *and* an integrality
tolerance that buys a metre of penetration) is the best short explanation of the issue I
have read at this level. Keep \cref{ex:ch22-tiny} exactly as it is: seven nodes, one LP
each, reproduced by the book's own textbook branch-and-bound and cross-checked against a
256-LP brute force, with the tree figure and \cref{tab:ch22-trace} agreeing line by line
with the code's printout. Keep \cref{prop:ch22-intersample} with its proof and, above all,
the honesty around it: the minimum-time plan whose sampled separation is $1.25$~m and whose
continuous separation is $0$, the $0.146$~m corner cut of the minimum-fuel plan, and the
demonstration that inflating the block alone still leaves $0.06$~m - this is the
pedagogical high point of the chapter and it is fully backed by `continuous_check`. Keep
\cref{sec:ch22-cost} with its generated, committed data and \cref{tab:ch22-verdict}: an
honest scaling experiment that admits the method fails from three drones on is worth more
than any amount of advocacy. Keep the MAPF-ILP section and its comparison with CBS
("\cbs works on the conflicts, the ILP works on the volume"), the three pitfall boxes, the
exact variable-and-row accounting of \cref{ex:ch22-two} (which lets a reader rebuild the
model from scratch), the 33 index entries, the 13 glossary terms and the four worked
solutions.
