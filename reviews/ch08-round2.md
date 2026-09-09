# Review of Chapter 8 (Prioritized Planning and Space-Time A*) - round 2

Reviewed artefacts: `Overleaf/chapters/ch08-prioritized-planning.tex` (1220 lines),
`Overleaf/figures/ch08/{idea,example,spacetime,counterexamples,window,orders}.tex`,
`Overleaf/figures/data/ch08-orders.dat`, `Overleaf/code/ch08_prioritized.py`,
`Overleaf/code/figures/gen_ch08_orders.py`, `Overleaf/appendices/solutions/ch08-solutions.tex`,
`Overleaf/appendices/glossary/ch08-terms.tex`, `Overleaf/references.bib`,
`Overleaf/bib/ch08-extra.bib`, against `STYLE_GUIDE.md` section 9, `docs/specs/ch08.md`,
`docs/core-idea.txt`, and `reviews/ch08-round1.md` with the reviser's response.

**Build.** `./build.sh ch08-prioritized-planning` returns status 0. No `!` errors. The only
overfull box in the whole log (29.10 pt, "Rapidly-exploring random tree with goal bias",
lines 39--39) is in the shared list-of-algorithms, not in this chapter. All undefined
references reported (`ch:ch11`, `ch:ch13`, `ch:ch14`, `ch:ch19`, `ch:ch20`, `ch:ch21`) are on
front-matter page i and belong to the preface, not to Chapter 8; every label, citation and
`\cref` of this chapter resolves, including `\cref{thm:ch04-surely}`, `\cref{ch:ch24}` and
`\cref{ch:appA}`. Chapter body: PDF pages 22--41, i.e. **20 printed pages**, at the ceiling
but not over it. Nothing in the chapter is padding, so no cuts are required (category G).

**Code.** `python3 code/ch08_prioritized.py` passes, in 19.0 s. Every number quoted in the
chapter was re-checked against the program or against `figures/data/ch08-orders.dat` and
reproduces: the six-order table (16/16/16/fail/21/fail), the machine-generated trace of
`tab:ch08-trace`, `optimal_soc == 16`, the pocket corridor (optimum 11), the bypass corridor
(best order 16, optimum 15), the HCA* expansion counts (32 509 vs 11 034), the ordering
experiment (failures 19/15/1/1 out of 240; `soc` at `k = 32` equal to 1.163/1.201/1.207/1.124;
random order failing 13 % at `k = 32` and 23 % at `k = 28`; lpf and mcf within one point for
`k >= 24`), the WHCA* run on the worked example (`window=6, step=3` -> costs 6, 6, 4), and the
new timing benchmark (2.2, 4.2, 7.6 s, median 4.2 s, matching "about 2, 4 and 7 seconds, a
median of roughly 4"). I also re-derived both counterexample plans and the well-formedness
proof by hand.

**Round-1 items.** Required changes 1, 2, 5, 6, 7 and 8 of round 1 are correctly resolved
(the "agent 1 before agent 3" characterisation, the restricted HCA* dominance statement with
`thm:ch04-surely`, the "as if no other agent existed" sentence, the `fig:ch08-orders` caption
plus the most-constrained-first paragraph, `\pi_i[t]` everywhere - no `\pi_i(...)` is left in
the chapter or the solutions - and the `\cbs`/`\ecbs` expansion at first use). Required
change 3 is resolved as far as the quoted numbers go, but the fix pushed the self-test over
the 10 s budget (item 5 below). Required change 4 is resolved in its wording, but the
reviser's stated reason for the one deviation is factually wrong, and that same wrong
measurement was propagated into `exr:ch08-whca`(b) and its new solution (items 1 and 4 below).
None of the round-1 items that were resolved correctly are re-raised here.

## Verdict

**Minor revision.** The mathematics, the pseudocode, the complexity bound, the worked example
and the ordering experiment are all sound and reproduce, the chapter covers every "must
cover" item of `docs/specs/ch08.md` and every Week-3 item of the training plan, and the
figures, index (26 entries), exercises (8, graded 1-1-2-2-2-2-2-3, Week-3 coding exercise
present) and bibliography (11 keys, all resolving, all correct) are in good shape. Three
things must still be fixed: one exercise (and its solution) states a result about
`whca_star` that the code contradicts, `def:ch08-wellformed` is missing the distinctness
hypothesis that its own theorem, its own remark and the code all rely on, and one line of the
completeness proof is stated for the wrong range of $t$. All required changes are local
edits of at most a few lines each.

## Required changes

1. **`exr:ch08-whca`(b) (chapter lines ~1206-1213) and the solution for `exr:ch08-whca`(b) in
   `Overleaf/appendices/solutions/ch08-solutions.tex`.**
   *Problem (A - a claim the code does not reproduce).* The exercise asserts "Run
   `whca_star` with $\delta = 1$ and windows $w = 2, \dots, 12$. For every one of them the
   rounds never end and the function returns `None`, even when $w$ is larger than the whole
   corridor", and the solution repeats it ("`whca_star` therefore reaches `max_rounds` and
   returns `None` for every $w = 2, \dots, 12$"). This is false. On exactly the instance the
   exercise describes - `grid = ['#.#######', '.........']`, agent 1 from $(1,0)$ to $(1,8)$,
   agent 2 from $(1,8)$ to $(1,0)$, i.e. corridor $(1,0), \dots, (1,8)$ with the single pocket
   $(0,1)$ - `whca_star(inst, window=w, step=1)` gives

   | $w$ | result | validator |
   |---|---|---|
   | 2, 3, 4, 5 | `None` | -- |
   | 6 | costs $[10, 9]$ | `vertex conflict agents 0,1 at (1, 4) t=5` |
   | 7, 8 | costs $[9, 10]$ | `vertex conflict agents 0,1 at (1, 5) t=5` |
   | 9, 10, 11, 12 | costs $[11, 12]$ | `vertex conflict agents 0,1 at (1, 5) t=7` |

   For $w = 8$ the executed plan is
   $\pi_1 = (1,0),(1,1),(1,2),(1,3),(1,4),(1,5),(1,5),(1,6),(1,7),(1,8),(1,8)$ and
   $\pi_2 = (1,8),(1,7),(1,6),(1,6),(1,5),(1,5),(1,4),(1,3),(1,2),(1,1),(1,0)$: the agents
   walk through each other on $(1,5)$. Instrumenting `space_time_astar` inside `whca_star`
   shows it returning `None` three times in that run (goals $(1,0)$, $(1,0)$, $(1,8)$), so the
   stay-put branch does fire. It fires because the agent planned first reserves a straight
   path along the whole corridor and parks on the far end, which is the only place the agent
   planned second could retreat to; with $w \le 5$ that parked entry falls outside the window
   and the second agent can still retreat, which is why the small windows livelock instead.
   The round-1 review had this right; the "correction" applied in round 1 was based on a
   mis-measurement.
   *Fix.* Restore the correct claim in (b): "For $w \le 5$ the rounds never end and the
   function returns `None`. For $w \ge 6$ it returns an executed plan that `validate`
   rejects - with $w = 8$ both agents stand on $(1,5)$ at $t = 5$. Explain why a larger window
   makes matters worse rather than better: which agent sees the other one at all in a given
   round, what does the agent planned second do when every cell in front of it is reserved and
   its only retreat is parked on, and which line of `whca_star` throws the guarantee away."
   Rewrite solution (b) to match: the first planner never sees the other agent; the second
   planner's search fails outright once the first planner's parked goal is inside the window;
   the stay-put fallback of line~\ref{alg:ch08-whca:search} is then executed, and the next
   round marches the other agent into the stationary one. Keep (a) and (c) as they are - both
   are correct ($w = 2$ really does oscillate with no failed search, and
   `prioritized_planning` with order $(2,1)$ and the full horizon really does return costs
   $15$ and $8$).

2. **`def:ch08-wellformed` (section 8.3), and the remark after `def:ch08-order`.**
   *Problem (A - a theorem hypothesis that is used but never stated).* The definition says only
   that each agent has a path visiting no endpoint of $P$ other than its own two. It never
   requires the $2k$ endpoints to be distinct. But that distinctness is used three times:
   the remark after `def:ch08-order` asserts "the well-formed instances of
   `def:ch08-wellformed`, whose endpoints are all distinct"; the proof of
   `thm:ch08-wellformed` uses "$s_i$ is not parked on because goals are distinct from starts";
   and `is_well_formed` in `code/ch08_prioritized.py` tests
   `len(set(endpoints)) != 2 * inst.k` and returns `False`. Without the hypothesis
   `thm:ch08-wellformed` is false: on the path graph $a - b - c$ (grid `['...']`) with agent 1
   from $a$ to $b$ and agent 2 from $b$ to $c$, both agents have endpoint-free paths, so the
   instance satisfies `def:ch08-wellformed` as written, yet
   `prioritized_planning(inst, [0,1], "true", revised=True)` returns `None`, because the
   revised rule turns agent 1's own goal $b = s_2$ into a static obstacle - while the plan
   $\pi_1 = (a,b)$, $\pi_2 = (b,c)$ is valid.
   *Fix.* Add the missing condition to `def:ch08-wellformed`, e.g. after "Let
   $P = \set{s_1, \dots, s_k, g_1, \dots, g_k}$": "with all $2k$ endpoints distinct,
   $\abs{P} = 2k$" - this is Čáp et al.'s assumption - and add half a sentence saying that in
   particular no agent's goal is another agent's start, which is what makes the remark after
   `def:ch08-order` and the "waiting is unblocked" step of `thm:ch08-wellformed` legitimate.

3. **Proof of `thm:ch08-wellformed`, the paragraph "*Going is unblocked*".**
   *Problem (A - an incorrect step in a proof).* "After time $T^*_j$ every earlier agent is
   parked on its own goal, so $R$ contains no timed vertex entry and no move entry with
   $t \ge T^*_j$" is false at $t = T^*_j$ itself: the agent whose arrival time equals $T^*_j$
   contributes the timed vertex entry $(g_{\sigma(m)}, T^*_j)$ to $R_V$. (Move entries are
   fine: the last move of that agent is recorded at $t = T^*_j - 1$.)
   *Fix.* Change the range and add the one clause that closes the gap: "... so $R$ contains no
   move entry with $t \ge T^*_j$ and no timed vertex entry with $t > T^*_j$; the single timed
   entry at $t = T^*_j$ is the goal of the last agent to arrive, which $P_i$ avoids, and the
   wait-then-go path is still sitting at $s_i$ at that moment. The only blocked cells from
   $T^*_j$ on are therefore the goals $g_{\sigma(m)}$, $m < j$, which $P_i$ avoids by
   construction."

4. **Section 8.6.2 (`sec:ch08-whca`), the sentence ending "... which is one of the two ways in
   which a windowed plan loses its guarantee."**
   *Problem (C - a forward reference replaced by an unexplained count).* "the two ways" are
   never enumerated anywhere in the chapter, so the reader cannot check the statement, and the
   pointer to the exercise that demonstrates the mechanism was removed. The reason given in
   round 1 for removing it ("the stay-put branch never fires" on that instance) is wrong; see
   item 1.
   *Fix.* Restore the link and name both failure modes explicitly, e.g.: "..., and the agent
   takes the stay-put branch of line~\ref{alg:ch08-whca:search}. This is where a windowed plan
   loses its guarantee, and it is exactly what happens in \cref{exr:ch08-whca}: a stationary
   agent is no longer in the table that the others planned against, so the executed plan can
   contain a real conflict. The second failure mode is milder - the loop need not terminate at
   all, as the third point below explains."

5. **`Overleaf/code/ch08_prioritized.py`, `_self_test()` step 7 (the 100x100 benchmark), and
   the sentence quoting it in section 8.4 ("Complexity").**
   *Problem (G - violates `STYLE_GUIDE.md` section 6: the self-test must run "in under 10
   seconds").* The self-test now takes 19.0 s, of which about 14 s is the three-instance
   timing benchmark added in round 1 (2.2 + 4.2 + 7.6 s).
   *Fix.* Keep the benchmark but take it out of the default run: guard it with a command-line
   switch (`if "--bench" in sys.argv:` around step 7, printing the three times and the median
   as now) so that plain `python3 code/ch08_prioritized.py` finishes in about 5 s, and change
   the sentence in section 8.4 to name the command, e.g. "... a median of roughly $4$ seconds
   on the laptop used for this book (run `python3 code/ch08_prioritized.py --bench` to
   reproduce the measurement); the spread comes from the instances, not from the machine, and
   your own times will differ." Do not change the quoted numbers - they are correct.

## Suggestions

* Section 8.5, `ex:ch08-three`: "The instance is not well-formed: every path of agent~3 ends on
  the bottom corridor, which agent~1 cannot avoid" states the violation from the wrong side.
  It is agent 1 that has no endpoint-free path: the bottom route passes $g_3 = (2,3)$ and every
  route to the top corridor passes $s_2 = (0,0)$, $s_3 = (0,3)$ or $g_2 = (0,6)$. Say that
  instead; it also prepares `exr:ch08-wellformed`.
* Section 8.6.1 writes $\hcost^*(v) = \dist_G(v, g)$. The notation table (line 74 of
  `frontmatter/notation.tex`) and `ch07-mapf-problem.tex` use $\dist(u,v)$ without the
  subscript. Drop the $G$ for consistency.
* Section 8.6.3: "A single random order fails in $13\,\%$ of the instances with $32$ agents and
  in $23\,\%$ of those with $28$" invites the question why more agents fail less often. One
  clause ("the difference is inside the noise of thirty instances per $k$") removes it.
* `appendices/solutions/ch08-solutions.tex` now covers 5 of the 8 exercises. `exr:ch08-hca`(c)
  (is the parked-cell heuristic still admissible? - the answer, that it overestimates as soon as
  a parked agent blocks the only short route, is a genuine trap) would repay a solution.
* The notation-table row for $R = (R_V, R_E)$ suggested in round 1 is still missing; the
  reviser correctly left `frontmatter/notation.tex` alone, so this is one for the front-matter
  owner: `$R=(R_V,R_E)$ & reservation table: (vertex, time) and (move, time) entries, plus
  parked goals & \cref{ch:ch08}`.
* Length: 20 printed pages against the 13-15 of `docs/specs/ch08.md`. Nothing is padding and no
  cut is required. If a page has to be found at book level, section 8.6.5 "Beyond grids" and
  the second half of the drone box (which repeats the `\cbs`/`\ecbs` argument of section 8.1)
  compress most easily.

## What must be kept

The worked example remains the best thing in the chapter and must survive intact: one
$3 \times 7$ map carries the reservation table (`tab:ch08-table`), a genuinely
machine-generated search trace (`tab:ch08-trace`, verbatim from the `trace` list of
`space_time_astar`, and reproducing exactly - including the "V, V, E" blocked column), the
space-time picture of that same search (`fig:ch08-spacetime`), and the complete six-order table
with a brute-force optimum. The two counterexamples are minimal, correct and hand-checkable,
and panel (c) with the optimal plan is the right editorial decision; I re-derived both plans
($6+5=11$ and $8+7=15$) and they are exactly as drawn. The completeness proof for well-formed
instances is a real proof with a named witness (wait-then-go), three separated claims, an
honest remark isolating the single place where the revised rule is used, and a corollary that
admits its own looseness - keep all of it. The HCA* passage as rewritten in round 1 is now a
model of how to state a dominance result honestly (single agent, fixed table, $\fcost < C^*$,
tie-breaking, and an explicit switch to "empirically" for the whole-run measurement) and should
not be softened further. Keep the three pitfall boxes - "checking the edge in the wrong
direction" is the bug every first implementation has - and keep the "collapsing time instead of
a horizon" note attached to `lst:ch08-search`, which most treatments omit. The PBS section is
accurate about what priorities can and cannot express. The bibliography is clean: all eleven
keys resolve and the details of Silver 2005 (AIIDE 117-122), Erdmann and Lozano-Perez 1987
(Algorithmica 2, 477-521), Cap et al. 2015 (T-ASE 12(3), 835-849), van den Berg and Overmars
2005 (IROS 430-435), Bennewitz et al. 2002 (RAS 41(2-3)), Ma et al. 2019 (AAAI 7643-7650), Ma
et al. 2017 (AAMAS 837-845), Phillips and Likhachev 2011 (ICRA 5628-5635), Hoenig et al. 2016
(ICAPS 477-485), Stern et al. 2019 (SoCS 151-158) and LaValle 2006 are all correct - nothing is
fabricated.
