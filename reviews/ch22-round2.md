# Review of Chapter 22 (Mixed-Integer Linear Programming for Planning) - round 2

## Verdict

**Minor revision.**

All eight required changes of round 1 were resolved, and resolved correctly. I re-checked
each one against the source, the code and the PDF:

1. *Symmetry-breaking binary* (`sec:ch22-implementation`, lines 1161-1172): the second
   reading was taken; $c^{12}_{k,1}=1$ is now correctly described as switching *off* the
   row "drone 1 at least $d_{\min}$ to the right of drone 2", the opposite value $0$ is
   correctly described as enforcing $x^1_k - x^2_k \ge d_{\min}$, and solution (d) matches.
2. *Sum of costs of the MAPF ILP* (line ~925): the objective is now
   $\sum_i\sum_{e \ne ((g_i,t)\to(g_i,t+1))} f^i_e$, which is exactly $\sum_i t_i$; the
   closing sentence about the old index set is correct.
3. *Interior-point methods* (line 79): "converge to a point of the optimal face, from which
   a crossover step recovers a vertex" - correct, and now consistent with `sec:ch22-lp`.
4. *Solve times*: re-measured, with a footnote naming machine, Python, SciPy and HiGHS.
   On the review machine the run gives 1.25 / 0.095 / 0.31 s against the quoted
   1.8 / 0.14 / 0.53 s - the same ratios, within the factor of two the footnote declares -
   and every reproducible quantity matches exactly (366 / 1 / 1 nodes; 344, 298, 368
   variables; 388, 388, 486 rows; 144, 144, 168 binaries; $J_{\text{fuel}} = 12.0202$;
   $9.0160$; $0.8889+0.8889$; $16.0$; 4103 nodes and $12.0383$ at $\dt = 0.25$;
   $16.7778$ and 48 nodes for the safe instance; $0.0606$ m for the block-only inflation;
   $0.1455$ m and $0.8556$ m between samples; $10.7713/12.0202/12.5616/12.5616$ for the
   four $d_{\min}$; the seven-node tree, the root bound 4 and the 256-LP brute force).
   `tab:ch22-steps` agrees row by row with the self-test printout.
5. *`tab:ch22-binaries` caption*: the promised leaves column is gone; the table's own
   numbers are all correct ($4N(mn_O+\binom{m}{2})$).
6. *Maximisation in `fig:ch22-relaxation`*: stated in the paragraph and in the caption;
   I re-solved the LP ($10$ at $(2.5,3.75)$) and the IP ($9$ at $(3,3)$) and both are right.
7. *Boundary degrees*: the solution of `exr:ch22-mapfilp` now has $4992$ edges per layer,
   $6.0\cdot10^6$ binaries and $1.2\cdot10^5$ anti-swap rows - all correct.
8. *`exr:ch22-coding`(a)*: the time limit, the status/gap instruction and the reference
   numbers are in place.

I also re-derived the rest of the technical content and found it sound: the tight $M$ of
`eq:ch22-tightM` and `prop:ch22-bigm` with its proof; the separation constants
$M_x = 11$, $M_y = 9$ m; `eq:ch22-time` (Richards-How arrival encoding); the node bound
$2^{|I|+1}-1$ and the three-part proof of `thm:ch22-bnb`; the Jeroslow family and the
$\sum_j z_j \le (n-1)/2$ cut in `prop:ch22-complexity`; all three parts of
`prop:ch22-intersample`; the flow, capacity and anti-swap rows of `eq:ch22-mapf-ilp` and
the $m\,T\sum_v(\deg v+1)$ count; the variable and row accounting of `ex:ch22-two`
(344/388, 298/388, 368/486, all confirmed by the code); and every number of
`sec:ch22-cost` against `figures/data/ch22-scaling.dat` (1.25/3.08/12.56 s, 35.6 %,
8.85 %, 55.4 %, 81.1 %, two nodes, 2016 binaries, 3192 variables).

Build: `./build.sh ch22-milp` status 0, no errors, no undefined label or citation of this
chapter (the `ch:ch11`, `ch:ch13`, `ch:ch14` warnings come from the front matter and from
the cross-chapter `\cref` of line 35, which is expected in a single-chapter build), and
the only overfull box in the log is the pre-existing one in the front-matter list of
algorithms. `python3 code/ch22_milp.py` passes in 29.9 s, exit 0. Six figures, six tables,
three listings, one algorithm, all referenced; 36 index entries; 13 glossary terms; all
twelve citation keys resolve in `references.bib`/`bib/ch22-extra.bib` and all twelve
entries look genuine to me.

Six required changes remain, and every one of them is a local edit: one notation collision,
one qualitative claim the chapter's own experiment contradicts, two solution-appendix
items, one trim, one acronym. None touches the structure or the results.

Length: the chapter body is PDF pages 27-47 of `build/only-ch22-milp.pdf`, i.e. **21
pages**, one over the 20-page ceiling (and above both the spec's 11-13 and the style
guide's 12-18). Almost all of that is required content; item 5 names the repetition that
is not, and nothing else is to be cut.

## Required changes

1. **`sec:ch22-formulation`, `eq:ch22-time` and the paragraph around it (lines 462-475) -
   the arrival binary $y^i_k$ is the same symbol as the $y$-coordinate $y^i_k$ used
   110 lines earlier.** `eq:ch22-sep-sides` (line 348) and `eq:ch22-sep` (lines 361-362)
   write the separation rows as $y^i_k - y^j_k \ge d_{\min}$, where $y^i_k$ is drone $i$'s
   $y$-position at step $k$; `eq:ch22-time` then declares "$y^i_k \in \set{0,1}$ marks the
   arrival step of drone $i$". Both meanings live inside the *same* model: the minimum-time
   MILP contains the separation rows and the arrival binaries at once, and a reader who
   builds it from the text cannot tell $y^i_k$ from $y^i_k$. The style guide forbids
   competing notation for one symbol. **Fix:** rename the arrival binary to $w^i_k$ in
   `eq:ch22-time` (all four occurrences: the objective $\sum_i\sum_k k\,\dt\,w^i_k$, the
   choice row $\sum_k w^i_k = 1$, the switch $1-\sum_{k'\le k} w^i_{k'}$) and in the two
   sentences that surround it (lines 464 and 473), and add a half-clause saying that the
   code's accessor for it is `MilpModel.y(i, k)` - or rename that method to `w` as well,
   which is a two-line change in `code/ch22_milp.py` (definition at line 145 and its use in
   `_arrival_rows`/`arrival_times`). Nothing else in the chapter uses the symbol.
   *Category C.*

2. **`sec:ch22-separation`, the paragraph after `tab:ch22-binaries` (line ~394) - the
   scaling sentence contradicts the chapter's own measurement.** The text reads "Two drones
   and twenty steps are a routine problem, ten drones and fifty steps are a hard one, and
   twenty drones are beyond reach without further structure", and the next sentence claims
   the table "is the quantitative reason for the verdict of `sec:ch22-cost`". But
   `fig:ch22-scaling` and `figures/data/ch22-scaling.dat` show that **three** drones already
   hit the 30 s limit at every horizon (gaps 8.9 %, 33.8 %, 46.6 %, 55.4 %), and that even
   two drones need 12.6 s at $N = 20$ and are unsolved at $N = 24$. Ten drones are not "a
   hard one", they are hopeless. **Fix:** replace the sentence by one that matches the
   experiment, e.g. "Two drones and twenty steps are a problem of seconds; three
   interacting drones are already at the edge of what thirty seconds can prove optimal
   (\cref{sec:ch22-cost}); ten drones and fifty steps are out of reach without further
   structure." *Category C.*

3. **`appendices/solutions/ch22-solutions.tex` - only four of the eight exercises have a
   solution.** Chapters 18-25 supply 7-9 solutions each (ch23, ch24, ch25: 7 of 8); this
   chapter supplies solutions for `exr:ch22-lp`, `exr:ch22-margin`, `exr:ch22-mapfilp` and
   `exr:ch22-coding` only, so `exr:ch22-tightm`, `exr:ch22-separation`, `exr:ch22-time` and
   `exr:ch22-schedule` leave a reader working alone with no way to check the answer.
   **Fix:** add at least three of the four missing solutions (all four is better), in the
   same short style. The results are:
   * `exr:ch22-tightm`: $M_1 = X_{\max}-x_{\min} = 6$, $M_2 = x_{\max}-X_{\min} = 6$,
     $M_3 = Y_{\max}-y_{\min} = 6.5$, $M_4 = y_{\max}-Y_{\min} = 5.5$ m;
     $M_x = d_{\min}+(X_{\max}-X_{\min}) = 11$ m, $M_y = d_{\min}+(Y_{\max}-Y_{\min}) = 9$ m.
     With $M_1 = 3 < 6$ the legal position $(9, 6.5)$, which is above the block, becomes
     infeasible: it needs $b_{k,4} = 0$, hence $b_{k,1} = 1$, hence $x_k \le x_{\min}+M_1 = 7$,
     which $x_k = 9$ violates. With $M_1 = 0$ the first row is $x_k \le x_{\min}$ whatever
     $b_{k,1}$ is, so the drone is pinned to the left of the block at every step and the
     model is over-constrained (here: infeasible, since both goals lie at $x = 9$).
   * `exr:ch22-separation`: the proof is `prop:ch22-bigm` applied to the square of side
     $2d_{\min}$ centred on drone $j$, with $M_x, M_y$ as above; a convex polygon with $r$
     edges needs $r$ binaries and $\sum_j b_j \le r-1$ (write each edge as
     $\vect{a}_j\T\pos_k \ge c_j - M_j b_j$ with $M_j$ the largest violation of that edge
     inside $W$); a 3-D box needs six binaries and $\sum_j b_j \le 5$. Four drones, two
     hexagons, $N = 20$: $6\cdot4\cdot2\cdot20 = 960$ obstacle binaries plus
     $4\binom{4}{2}\cdot20 = 480$ separation binaries, $1440$ in all.
   * `exr:ch22-time`: from $\sum_{k'\le k} w^i_{k'} = 1$ for every $k \ge k_a$ the
     right-hand side is $0$, so $\abs{p^i_{k,d}-p^i_{\mathrm{g},d}} \le 0$ at every sampled
     instant from the arrival step on; before it the term is $M_{\mathrm{g}}$ and the row is
     vacuous. Two plans with the same arrival time but different fuel: reach the goal with
     one hard accelerate-decelerate pair, or wander first and arrive at the same step - the
     arrival objective cannot separate them, which is what the $10^{-3}J_{\mathrm{fuel}}$
     tie-breaker is for. Time window: $\sum_{k\dt \in [t^i_a, t^i_b]} w^i_k = 1$;
     no two drones in the same step: $\sum_i w^i_k \le 1$ for every $k$.
   * `exr:ch22-schedule`: $z_{i,p,q} \in \set{0,1}$, $\sum_{p,q} z_{i,p,q} = 1$ (each drone
     lands once, the *choice* gadget), $\sum_i z_{i,p,q} \le 1$ (one landing per pad and
     slot, the *at most one* gadget), $z_{i,p,q} + z_{i',p,q'} \le 1$ for $\abs{q-q'} < 2$
     (two slots apart on one pad), $z_{i,p,q} = 0$ whenever $30q > T_i$ (deadline), and
     $\min \sum_{i,p,q} 30q\,z_{i,p,q}$ (or the waiting time measured from each drone's
     arrival). For $m = 6$, two pads and eight slots: $6\cdot2\cdot8 = 96$ binaries, $6$
     assignment rows, $16$ pad-slot rows and the pairwise separation rows.
   *Category E.*

4. **`appendices/solutions/ch22-solutions.tex`, solution of `exr:ch22-coding`(a) - the
   `Instance(...)` call cannot produce the second of the two runs the exercise asks for.**
   The exercise says "solve it with the fuel and the time objective", but the constructor
   given in the hint omits the `objective` field, and the chapter never states how the
   objective is chosen in code (`lst:ch22-use` only shows `example_instance("fuel")`).
   **Fix:** append `objective="fuel"` to the constructor in the hint and add "and the same
   instance with `objective="time"` for the second run"; and add the field to the sentence
   in `sec:ch22-implementation` that lists the class, e.g. "...and `Instance` carries the
   geometry, the horizon, the limits and the field `objective` (`"fuel"`, `"peak"` or
   `"time"`)". *Category E.*

5. **Length: the chapter body is 21 pages, one over the ceiling; cut the repeated
   passages named here and nothing else.** The excess is content, not padding, except in
   four places where the same numbers or the same argument appear twice:
   (a) the pitfall *Safe at the samples, unsafe in between* (lines ~1218-1226) restates the
   $0.25$ m margin, the $t = 2 \dots 2.5$ s swap and the $0.15$ m corner cut that
   `sec:ch22-example` has just given - replace those two sentences by "Both plans of
   \cref{ex:ch22-two} violate the continuous constraint although every sampled constraint
   holds";
   (b) the pitfall *A huge $M$* (lines ~1208-1216) repeats the "hurts twice" paragraph of
   `sec:ch22-bigm` sentence for sentence - keep the two imperatives ("Compute $M$ from the
   workspace... verify the returned plan") and one clause of justification, and point at
   `sec:ch22-bigm` for the rest;
   (c) the paragraph after `tab:ch22-verdict` (lines ~1063-1068) closes with "replan fifty
   drones ten times a second", which is verbatim the closing of `sec:ch22-motivation` - cut
   it to the one sentence that is new ("MILP is not a competitor of the planners of
   Parts III and IV but their judge");
   (d) `tab:ch22-steps` has thirteen rows of which six ($k = 1,2,3,9,10,11$) carry nothing
   the reader needs - keep $k = 0, 4, 5, 6, 7, 8, 12$ and say in the caption that the
   self-test prints all of them.
   Do **not** cut the variable-and-row accounting, `ex:ch22-tiny`, `prop:ch22-intersample`,
   `sec:ch22-cost` or any of the three pitfalls themselves. If the chapter still runs a few
   lines past twenty pages after these four cuts, leave it there. *Category G.*

6. **Acronyms not expanded at first use in this chapter (`sec:ch22-motivation` line 30,
   `sec:ch22-mapf-ilp` line 900).** The style guide requires every acronym to be defined at
   first use *in every chapter*; `\cbs` appears in line 30 as bare "CBS" and MAPF appears
   in the objectives box and in line 900 without expansion. **Fix:** write "\cbs
   (conflict-based search, \cref{ch:ch09})" at the first occurrence and "The multi-agent
   path finding (MAPF) problem of \cref{ch:ch07}" at line 900. *Category F, cosmetic.*

## Suggestions

* `thm:ch22-bnb` assumes implicitly that the relaxations are bounded; with an unbounded
  relaxation `SolveRelaxation` returns no optimal point and the "integral" branch of the
  proof has nothing to talk about. One clause in the hypothesis ("whose LP relaxations are
  bounded and solved exactly") closes the gap, and a half-sentence noting that the model of
  `def:ch22-problem` is bounded because every variable has finite bounds would connect it
  to the chapter.
* `sec:ch22-implementation` names the index function `\code{cpair(pair, k, q)}` while the
  code's parameter is `j` (`code/ch22_milp.py` line 141); the same paragraph writes
  `b(i, o, k, j)`, which does match. Use `j` in both.
* `figures/ch22/timeexpanded.tex`, the capacity annotation writes
  $\sum_i f^i_{(b,1)} \le 1$, but $f$ is indexed by edges, not by states. Write
  $\sum_i \sum_{e \in \delta^-(b,1)} f^i_e \le 1$ to match `eq:ch22-mapf-cap`.
* `sec:ch22-example`: "and \cref{tab:ch22-steps} is the resulting pair of trajectories"
  reads oddly - a table is not a trajectory. "and \cref{tab:ch22-steps} lists the resulting
  pair of trajectories step by step".
* `figures/data/ch22-scaling-horizon.dat` is committed but no figure or table reads it. If
  it is dead, delete it; if it backs a sentence of `sec:ch22-cost`, say which one.
* `sec:ch22-mapf-ilp`: "Yu and LaValle report optimal solutions for a hundred or more
  robots on grids of a few hundred cells" would be safer with the qualifier that this uses
  their split heuristics rather than the plain flow ILP.
* `tab:ch22-gadgets` says the gadgets are "linear in the continuous variables $x, u$" while
  $\vect{z}$ is the LP variable vector of `def:ch22-lp` and $x$ is a position coordinate
  everywhere else in the chapter. Naming the generic continuous variable $\vect{z}$ in that
  caption would remove the third meaning of $x$.
* `sec:ch22-cost` quotes "$2\,000$ binaries and $3\,000$ variables" for $m = 6$, $N = 24$;
  the data file has $2016$ and $3192$. Rounding is fine, but "about $2\,000$ binaries among
  $3\,200$ variables" is closer and costs nothing.

## What must be kept

Everything round 1 asked to keep survived, and it should stay. The big-$M$ derivation with
`prop:ch22-bigm`, its proof and the explicit tight constants of `eq:ch22-tightM` remain the
best short treatment of $M$ I have seen at this level, and the "hurts twice" argument -
weak relaxation *and* an integrality tolerance that buys a metre of penetration - is still
the passage I would quote to a student. `ex:ch22-tiny` is exemplary: seven nodes, one LP
each, a tree figure, a trace table and a 256-LP brute force, all three reproduced exactly
by the self-test, and the new `tab:ch22-steps` now does the same job for the two-drone
instance. Keep `prop:ch22-intersample` with its proof and the honesty around it: the
minimum-time plan whose sampled separation is $1.25$ m and whose continuous separation is
$0$, the $0.146$ m corner cut, and the demonstration that inflating the block alone still
leaves $0.06$ m. Keep `sec:ch22-cost` with its committed, regenerated data and
`tab:ch22-verdict` - an experiment that admits the method fails from three drones on is
worth more than any advocacy - and keep the footnote that names machine, Python, SciPy and
HiGHS, which is the right way to quote a wall clock in a textbook. Keep the MAPF-ILP
section with its corrected sum-of-costs objective and the "\cbs works on the conflicts, the
ILP works on the volume" comparison, the three pitfall boxes, the variable-and-row
accounting of `ex:ch22-two`, the exact tight $M$ values now quoted in the worked example,
the drone box that positions MILP as the judge rather than a competitor of the hybrid
planner, and the 36 index entries and 13 glossary terms.

## Response to review (round 2)

All six required changes are applied, plus seven of the eight suggestions. The build is
status 0 with no errors and no undefined reference or citation of this chapter (the
remaining warnings are the front-matter cross-chapter ones of a single-chapter build), the
only overfull box in the log is the pre-existing front-matter one, and
`python3 code/ch22_milp.py` still passes (exit 0, 29.6 s) with every quoted number
unchanged.

**Required changes**

1. *Arrival binary vs. y-coordinate* (`eq:ch22-time`). The arrival binary is now $w^i_k$ in
   all four places of `eq:ch22-time` (objective, choice row, switch, and the sum inside the
   switch) and in the two surrounding sentences, so $y$ is again only a coordinate. I took
   the second option offered for the code: `MilpModel.y(i, k)` is renamed to
   `MilpModel.w(i, k)` in `code/ch22_milp.py` (definition, `y_off` -> `w_off`, the objective
   row, `_arrival_rows` and `arrival_times`), and a half-clause in the text says why the
   letter changed ("the letter $w$ keeps the arrival binary apart from the $y$-coordinate of
   `eq:ch22-sep`"). The self-test was re-run after the rename and passes.
2. *Claim contradicted by the experiment* (paragraph after `tab:ch22-binaries`). Replaced by
   "Two drones and twenty steps are a problem of seconds; three interacting drones are
   already past what thirty seconds can prove optimal (`sec:ch22-cost`); ten drones and
   fifty steps are out of reach without further structure." I used "past" rather than "at
   the edge of" because `figures/data/ch22-scaling.dat` shows three drones hitting the limit
   at *every* horizon.
3. *Missing solutions*. All four are added, so the file now has 8 of 8:
   `exr:ch22-tightm` ($M_1 = 6$, $M_2 = 6$, $M_3 = 6.5$, $M_4 = 5.5$ m, $M_x = 11$,
   $M_y = 9$ m; the legal point $(9,6.5)$ cut off when $M_1 = 3$; the strip $x \le 4$ when
   $M_1 = 0$ - stated as infeasible here because drone A must reach $x = 9$ and drone B
   starts there, not "both goals are at $x = 9$", which the instance does not have);
   `exr:ch22-separation` (both directions of the equivalence, the $r$-binary polygon with
   $\sum b \le r-1$, the 6-binary 3-D box, and $960 + 480 = 1440$ binaries);
   `exr:ch22-time` (the switch is $|p - p_g| \le 0$ from the arrival step on and vacuous
   before it, the accelerate-decelerate versus wander pair for the tie-breaker plus why the
   multiplier must stay small, the window row and $\sum_i w^i_k \le 1$);
   `exr:ch22-schedule` (objective and four constraint families, 96 binaries, 6 assignment
   rows, 16 pad-slot rows and 14 consecutive-slot rows in the aggregated form, with the
   pairwise variant and its 420 rows named as the weaker alternative).
4. *`exr:ch22-coding`(a) hint*. The hint now ends with `objective="fuel"` and "repeat the
   run with `objective="time"`", and `sec:ch22-implementation` gained the sentence "The
   dataclass `Instance` carries the geometry, the horizon, the limits and the field
   `objective` (`"fuel"`, `"peak"` or `"time"`)". The hint's geometry moved from one long
   inline `\code{...}` into math, and the paragraph is wrapped in `sloppypar`, because the
   fragment overran the margin twice; the solutions file now compiles with no overfull box
   (`./build.sh --standalone appendices/solutions/ch22-solutions.tex`, 3 pages).
5. *Length*. (a) The inter-sample pitfall now reads "Both plans of `ex:ch22-two` violate the
   continuous constraint although every sampled constraint holds". (b) The big-$M$ pitfall
   keeps the two imperatives and one clause ("costs twice, once in the relaxation and once
   in the tolerances"), pointing at `sec:ch22-bigm`. (c) The paragraph after
   `tab:ch22-verdict` is one sentence and no longer repeats the closing of
   `sec:ch22-motivation`. (d) `tab:ch22-steps` keeps $k = 0, 4, 5, 6, 7, 8, 12$ and its
   caption says the self-test lists all thirteen steps and that the omitted rows continue
   the pattern. Nothing else was cut. The body is still 21 pages: the four cuts bought about
   two thirds of a page, and the required additions of items 1, 4 and 6 and the two accepted
   suggestions put roughly the same amount back, so the chapter ends about half a page into
   its twenty-first page - the "few lines past twenty" the review allows.
6. *Acronyms*. `\cbs (conflict-based search, \cref{ch:ch09})` at its first occurrence in
   `sec:ch22-motivation`, and "The multi-agent path finding (MAPF) problem of
   \cref{ch:ch07}" at the head of `sec:ch22-mapf-ilp`. MAPF also occurs earlier, in the
   objectives box, so that bullet now carries the expansion too; the body expansion is kept
   as asked, for a reader who skips the box.

**Suggestions**

* `thm:ch22-bnb` now assumes LP relaxations that are "bounded and solved exactly", and the
  paragraph after the proof notes that `def:ch22-problem` qualifies because every variable
  has finite bounds. Applied.
* `cpair(pair, k, q)` -> `cpair(pair, k, j)` in `sec:ch22-implementation`, matching the code.
  Applied.
* `figures/ch22/timeexpanded.tex` capacity annotation is now
  $\sum_i \sum_{e \in \delta^-(b,1)} f^i_e \le 1$. Applied.
* "`tab:ch22-steps` lists the resulting pair of trajectories step by step". Applied.
* `figures/data/ch22-scaling-horizon.dat` was dead (only the generator wrote it, no figure
  read it); the file and the block of `code/figures/gen_ch22_scaling.py` that wrote it are
  gone. `ch22-scaling.dat` is untouched, so no re-measurement was needed.
* The Yu and LaValle sentence now says "using the splitting heuristics of their paper rather
  than the plain flow ILP". Applied.
* "about $2\,000$ binaries among $3\,200$ variables" in `sec:ch22-cost`. Applied.
* `tab:ch22-gadgets`: the caption no longer names $x, u$ - it says the gadgets are linear in
  the variables of `def:ch22-lp`, of which $b$ and $z_j$ are binary - and the either-or row
  is written $f(\vect{z}) \le Mb$, $g(\vect{z}) \le M(1-b)$. I did not rename the gadget
  binaries $z_j$ to something else: the paragraph before the table introduces them as the
  integer components $z_j$ of $\vect{z}$ from `def:ch22-milp`, so $z_j$ is not a competing
  meaning, and only the caption's $x$ was.

Everything the review asked to keep is untouched: the big-$M$ derivation, `prop:ch22-bigm`
and `eq:ch22-tightM`, the "hurts twice" paragraph of `sec:ch22-bigm` (only its pitfall-box
copy was shortened), `ex:ch22-tiny` with `tab:ch22-trace`, `fig:ch22-bnb` and the 256-LP
cross-check, `prop:ch22-intersample` with its proof and the honest numbers around it,
`sec:ch22-cost` with its data, `tab:ch22-verdict` and the hardware footnote, the MAPF-ILP
section with the CBS comparison, the three pitfall boxes, the variable-and-row accounting of
`ex:ch22-two`, the drone box, and the index and glossary entries.
