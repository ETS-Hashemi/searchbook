# Review of Chapter 8 (Prioritized Planning and Space-Time A*) - round 1

Reviewed artefacts: `Overleaf/chapters/ch08-prioritized-planning.tex` (1193 lines),
`Overleaf/figures/ch08/{idea,example,spacetime,counterexamples,window,orders}.tex`,
`Overleaf/figures/data/ch08-orders.dat`, `Overleaf/code/ch08_prioritized.py` (612 lines),
`Overleaf/code/figures/gen_ch08_orders.py`, `Overleaf/appendices/solutions/ch08-solutions.tex`,
`Overleaf/appendices/glossary/ch08-terms.tex`, `Overleaf/references.bib`,
`Overleaf/bib/ch08-extra.bib`, against `STYLE_GUIDE.md` §9, `docs/specs/ch08.md` and
`docs/core-idea.txt`.

Build: `./build.sh ch08-prioritized-planning` returns status 0, no `!` errors, no undefined
reference or citation belonging to this chapter (the two `??` on PDF pages 20 and 36 are
`\cref{ch:ch24}`, legitimately absent from a single-chapter build). The single overfull box
reported (29.1 pt, "Rapidly-exploring random tree with goal bias") comes from the shared
list-of-algorithms file, not from this chapter. Chapter body: PDF pages 20-38, i.e. **19
printed pages** - inside the 20-page ceiling, so no cuts are required.

Code: `python3 code/ch08_prioritized.py` passes in 1.3 s. Every number in the worked
example, the trace table, the order table, both counterexamples, the HCA* expansion
comparison, the ordering experiment and the WHCA* run was checked against the program's
output or against `figures/data/ch08-orders.dat`, and all of them reproduce **except the
wall-clock claim in item 3 below**. I also re-derived the two counterexample plans and the
well-formedness proof by hand, and re-ran the WHCA* oscillation experiment of
`exr:ch08-whca`(b): its claims ("`None` for `w <= 5`, a validator-rejected plan for
`w >= 6`", and the hint "order (2,1) gives 8 and 15") are all correct.

## Verdict

**Minor revision.** The mathematics is sound, the chapter covers every "must cover" item of
`docs/specs/ch08.md` and the Week-3 items of the training plan, the code runs and reproduces
its numbers, and the figures are genuinely informative. But there is one factually false
sentence about the worked example, one over-stated dominance theorem that contradicts
Chapter 4, one performance number the code does not reproduce, one text/code contradiction
in the WHCA* section, one wrong statement about what the heuristic ignores, one caption
contradicted by its own data file, and a systematic notation clash with the notation table.
All of them are local edits.

## Required changes

1. **§8.5 "All six orders", lines 414-416 (`\Cref{tab:ch08-orders}` paragraph).**
   *Problem (A - technical accuracy).* "Whenever agent~3 is planned last or second, the plan
   costs $16$" is false. Order $(2,3,1)$ plans agent 3 **second** and fails - as the very
   table two lines below says, and as `all_orders(worked_example())` confirms. The correct
   characterisation is "agent 1 before agent 3": the three orders $(1,2,3)$, $(1,3,2)$,
   $(2,1,3)$ cost 16; $(3,1,2)$ costs 21; $(2,3,1)$ and $(3,2,1)$ fail.
   *Fix.* Replace the clause by: "Whenever agent~1 is planned before agent~3 - the orders
   $(1,2,3)$, $(1,3,2)$ and $(2,1,3)$ - the plan costs $16$, which is also the optimal sum of
   costs of the instance (the self-test asserts `optimal_soc(inst) == 16`)."

2. **§8.6.1 (`sec:ch08-hca`), lines 660-662.**
   *Problem (A - technical accuracy; also F - consistency with `ch04`).* "the space-time
   search with $\hcost^*$ expands no more states than with the Manhattan distance" is stated
   as a consequence of the dominance result, and it is too strong twice over. (i) The
   dominance theorem only covers states with $\fcost < C^*$; states with $\fcost = C^*$
   depend on tie-breaking. Chapter 4 states this carefully (`thm:ch04-surely` plus lines
   744-762: "leaves the nodes with $\fcost = C^*$ to the tie-breaking"), so Chapter 8
   contradicts Chapter 4. (ii) The theorem applies to *one* search against a *fixed*
   reservation table. The quoted 32 509 vs 11 034 is the total over 8 agents x 20 instances
   of a prioritized run in which the two heuristics give the early agents different (equally
   short) paths and therefore give the later agents *different sub-problems* - the chapter
   itself says so four lines later. The self-test's `assert exp_t <= exp_m` is an empirical
   check, not a theorem.
   *Fix.* Rewrite as: "The true distance is consistent and dominates the Manhattan distance,
   so for a single agent against a fixed table every state with $\fcost < C^*$ that the
   search with $\hcost^*$ expands is also expanded with the Manhattan distance
   (\cref{thm:ch04-surely}); states with $\fcost = C^*$ are left to the tie-breaking rule.
   Across a whole prioritized run the guarantee is weaker still, because the two heuristics
   send the early agents along different shortest paths and hence give the later agents
   different sub-problems. Empirically the gain is large: on twenty random ..."

3. **§8.4 "Complexity", lines 576-579, and the `dronebox` of §8.9, lines 1036-1039.**
   *Problem (A - a number the code does not reproduce).* "Forty agents on a $100 \times 100$
   grid with $20\,\%$ obstacles take about a second in plain \python with the code of this
   chapter" (repeated in the drone box as "they finish in about a second in plain \python").
   The self-test never measures this. Running
   `prioritized_planning(random_instance(100, 100, 40, rng, 0.2), order_longest_first(...),
   heuristic="true")` on eight seeded instances gives 1.05, 1.68, 2.13, 2.28, 2.56, 3.05,
   3.31, 3.71 s - median 2.6 s, i.e. 2.5x the quoted figure, and the spread is a factor of
   3.5.
   *Fix.* Add a timed benchmark to `_self_test()` (three 100x100 / 40-agent instances with a
   fixed seed, printing the median), and quote what it prints, with the machine caveat the
   book uses elsewhere: "about two to three seconds in plain \python on a laptop". Change
   both places, or drop the wall clock in the drone box and say "forty searches instead of
   one joint search" there.

4. **§8.6.2 (`sec:ch08-whca`), lines 722-725 ("Three details ... First, ...").**
   *Problem (A - text contradicts the code it describes).* "the goal-stay check of
   \cref{alg:ch08-ca} only looks at entries inside the window, so an agent that is parked on
   somebody's goal blocks it only for the next $w$ steps". The implementation does the
   opposite: `ReservationTable.last_reserved` returns `INF` as soon as the parked cell's
   arrival time falls inside the window, and `space_time_astar` then returns `None`
   immediately (`if t_goal == INF ... return None`). The agent therefore cannot plan at all
   in that round and falls back to "stay put" - it is *not* free to arrive after the window.
   This is exactly the mechanism `exr:ch08-whca`(b) asks the reader to find, so the sentence
   also mis-leads the exercise.
   *Fix.* Replace by: "First, the table of line~\ref{alg:ch08-whca:table} is relative to the
   current round: time $0$ is now, and entries beyond $t = w$ are invisible. A cell that a
   higher-priority agent has *parked* on inside the window is the exception: the goal-stay
   check then reports $t_g = \infty$, the search fails at once, and the agent takes the
   stay-put branch of line~\ref{alg:ch08-whca:search} - which is where the plans of
   \cref{exr:ch08-whca} lose their guarantee." (Alternatively change `last_reserved` to
   return `window - 1` instead of `INF` in that case and re-run the self-test, but then the
   claims of `exr:ch08-whca`(b) must be re-measured.)

5. **§8.6.2, lines 683-685.**
   *Problem (A/C - wrong statement).* "beyond it, the agents are ignored and the search
   follows the true-distance heuristic alone, which means it computes the rest of the path as
   if the map were empty". The true-distance heuristic is computed *on the map with its
   obstacles* (`bfs_distances`); what is ignored beyond the window is the other agents, not
   the walls.
   *Fix.* "... which means it completes the path as if no other agent existed (the static
   obstacles are still respected, because $\hcost^*$ is the distance on the real map)."

6. **Caption of `fig:ch08-orders` (lines 784-790) and the paragraph at lines 765-779.**
   *Problem (D - caption contradicted by the data it plots; one of four curves never
   discussed).* The caption says "Longest path first ... produces the most expensive plans",
   but in `figures/data/ch08-orders.dat` most-constrained-first is the most expensive rule at
   $k = 32$ (`soc_mcf` $=1.207$ against `soc_lpf` $=1.201$). Separately, the paragraph gives
   numbers for the random order, longest-path-first and restarts but never mentions
   most-constrained-first, although it is one of the three rules just introduced and one of
   the four curves in both panels; the reader cannot tell what the orange curve is for.
   *Fix.* (a) Caption: "Longest path first almost never fails; it and most constrained first
   produce the most expensive plans (within one point of each other for $k \ge 24$); five
   random restarts give the cheapest plans and fail once in 240 instances." (b) Add one
   sentence to the paragraph: "Most constrained first is a disappointment here: it fails in
   15 of the 240 instances, almost exactly as often as a single random order (19), and at
   $k = 32$ its plans are the most expensive of all four rules, $21\,\%$ above the bound.
   Counting conflicts between independent paths says little about who will be trapped."

7. **Whole chapter: $\pi_i(t)$ vs $\pi_i[t]$.**
   *Problem (F - competing notation).* `frontmatter/notation.tex` line 96 defines
   "$\pi_i$, $\pi_i[t]$ - path of $a_i$ and the vertex it occupies at step $t$", and
   `ch07-mapf-problem.tex` (19 occurrences) and `ch09-cbs.tex` (6) use the square brackets.
   Chapter 8 writes $\pi_i(t)$ everywhere: §8.3 (lines 145-155), `def:ch08-reservation`
   (168-171), §8.5 (line 339), the proof of `thm:ch08-sound` (469-473), the proof of
   `thm:ch08-incomplete` (511-512).
   *Fix.* Replace $\pi_i(t)$ / $\pi_j(t)$ / $\pi(t)$ by $\pi_i[t]$ / $\pi_j[t]$ / $\pi[t]$
   throughout the chapter (including $\pi_i[0] = s_i$, $\pi_i[T_i] = g_i$ and
   $(\pi[t], \pi[t+1])$ in `def:ch08-reservation`).

8. **§8.1, line 48 (`\cbs` / `\ecbs` first use).**
   *Problem (F - acronym not defined at first use in this chapter, required by
   `STYLE_GUIDE.md` §3).* "the global layer is \cbs or \ecbs" is the first appearance of both
   acronyms; the expansion "conflict-based search" only shows up at line 801, 750 lines
   later.
   *Fix.* Write "the global layer is conflict-based search (\cbs, \cref{ch:ch09}) or its
   bounded-suboptimal variant \ecbs (\cref{ch:ch10})".

## Suggestions

* `appendices/solutions/ch08-solutions.tex` holds solutions for only 3 of the 8 exercises
  (`exr:ch08-table`, `exr:ch08-pocket`, `exr:ch08-wellformed`). For a reader working alone,
  `exr:ch08-following`(b) (six orders under disappear-at-target - the answer is that all six
  succeed at the lower bound 14) and `exr:ch08-whca` (whose part (b) is a specific,
  verifiable claim) would repay a solution each.
* Add a row to `frontmatter/notation.tex` next to the existing $\sigma$ row:
  `$R=(R_V,R_E)$ & reservation table: (vertex, time) and (move, time) entries, plus parked
  goals & \cref{ch:ch08}`. Chapter 4 (line 971 of ch07 too) already refers to "the
  reservation tables of \cref{ch:ch08}", so the symbol deserves a table entry.
* `fig:ch08-counterexamples`, panel (a): agent 1 carries time labels 1..5 but not the
  arrival "6", so the caption's cost $6+5=11$ cannot be read off the picture. Add the label.
* `alg:ch08-pp`: `\KwIn` lists the flag *revised*, but the `\Fn{\PpPlan{...}}` signature does
  not; likewise `\hcost` is in the `\KwIn` of `alg:ch08-ca` but not in `\PpStar{...}`. Make
  the signatures match the input lists.
* Proof of `thm:ch08-wellformed` cites `thm:ch08-sound` for *completeness* of
  `alg:ch08-ca`, but that proposition is stated as soundness and per-agent optimality. Add
  "and it returns a path whenever an unblocked one with arrival time at most $T_{\max}$
  exists" to the second claim of `thm:ch08-sound`.
* `thm:ch08-wellformed`, the "goal test passes" step: the chain $t_g \le T^*_j < T^*_j + L_i$
  silently assumes $L_i \ge 1$. Add "(if $s_i = g_i$ then $L_i = 0$ and $t_g = -1$, because no
  earlier agent may enter $s_i$)" or assume $s_i \ne g_i$ in the theorem.
* §8.3, after `def:ch08-order`: note that the revised rule needs $g_i \notin
  \set{s_{\sigma(j+1)}, \dots}$, which holds automatically on well-formed instances
  (endpoints are distinct) but can make the search fail on arbitrary instances where one
  agent's goal is another's start.
* §8.5, line 374: "Steps~4 and~5 pop the two remaining states with $\fcost = 3$ and find them
  blocked as well" - they are only partly blocked (step 4 still generates the wait at
  $(1,3)$, step 5 generates two successors), as `tab:ch08-trace` shows. Say "and find their
  moves towards the goal blocked as well".
* The class is `ReservationTable.static_time()` here and `ReservationTable.horizon()` in the
  Chapter 4 code. One sentence in §8.8 ("what \cref{ch:ch04} calls `horizon()`") would help a
  reader moving between the two files.
* Length: 19 printed pages against the 13-15 of `docs/specs/ch08.md`. Nothing here is
  padding, so no cut is required; if a page must be found later, §8.6.5 "Beyond grids" and
  the second half of the drone box compress most easily.

## What must be kept

The worked example is the best thing in the chapter and must survive intact: one $3 \times 7$
map carries the reservation table (`tab:ch08-table`), a genuine machine-generated search
trace (`tab:ch08-trace`, verbatim from the `trace` list of `space_time_astar`), the
space-time picture of the same search (`fig:ch08-spacetime` - the three forbidden successors
at $t=2$ drawn in red are exactly the "V, V, E" of the trace), and the full six-order table
with a brute-force optimum. The two counterexamples are minimal, correct and hand-checkable,
and the decision to give each of them its own panel plus the optimal plan in panel (c) is
right. The completeness proof for well-formed instances is a real proof, not a sketch: the
wait-then-go witness, the three separated claims, and the remark that isolates *the single
place* where the revised rule is used are exactly what a graduate student needs, and the
corollary and its honest "the bound is loose" remark should stay. Keep the three pitfall
boxes - "checking the edge in the wrong direction" is the bug every first implementation
has - and keep the "collapsing time instead of a horizon" note with `lst:ch08-search`, which
is a genuinely useful implementation idea that most treatments omit. The bibliography is
clean: all eleven keys resolve, and authors, venues, volumes and pages of Silver 2005 (AIIDE
117-122), Erdmann and Lozano-Perez 1987 (Algorithmica 2, 477-521), Cap et al. 2015 (T-ASE
12(3), 835-849), Bennewitz et al. 2002 (RAS 41(2-3), 89-99), van den Berg and Overmars 2005
(IROS 430-435), Ma et al. 2019 (AAAI 7643-7650), Ma et al. 2017 (AAMAS 837-845), Phillips and
Likhachev 2011 (ICRA 5628-5635), Hoenig et al. 2016 (ICAPS 477-485) and Stern et al. 2019
(SoCS 151-158) are all correct - nothing is fabricated.
