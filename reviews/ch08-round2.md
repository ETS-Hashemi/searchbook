# Review of Chapter 8 (Prioritized Planning and Space-Time A*) - round 2

Reviewed artefacts: `Overleaf/chapters/ch08-prioritized-planning.tex` (1220 lines),
`Overleaf/figures/ch08/{idea,example,spacetime,counterexamples,window,orders}.tex`,
`Overleaf/figures/data/ch08-orders.dat`, `Overleaf/code/ch08_prioritized.py`,
`Overleaf/code/figures/gen_ch08_orders.py`,
`Overleaf/appendices/solutions/ch08-solutions.tex`,
`Overleaf/appendices/glossary/ch08-terms.tex`, `Overleaf/references.bib`,
`Overleaf/bib/ch08-extra.bib`, against `STYLE_GUIDE.md` section 9, `docs/specs/ch08.md`,
`docs/core-idea.txt`, and `reviews/ch08-round1.md` with the reviser's response appended.

**Build.** `cd Overleaf && ./build.sh ch08-prioritized-planning` returns status 0. No `!`
errors. The only overfull box above 15 pt in the whole log (29.10 pt, "Rapidly-exploring
random tree with goal bias", line 39) comes from the shared list-of-algorithms file, not
from this chapter. All undefined references in the log (`ch:ch11`, `ch:ch13`, `ch:ch14`,
`ch:ch19`, `ch:ch20`, `ch:ch21`) are on front-matter page i and belong to the preface;
`pdftotext` finds no `??` anywhere in the chapter body, so every label, citation and
`\cref` of Chapter 8 resolves, including `\cref{thm:ch04-surely}`, `\cref{ch:ch24}` and
`\cref{ch:appA}`. Chapter body: PDF pages 22-41 of a 49-page single-chapter build, i.e.
**20 printed pages** - above the 13-15 of the spec but at the ceiling this review applies.
I found no padding, so no cut is required (category G); see the suggestions if a page must
be found later.

**Code.** `python3 code/ch08_prioritized.py` passes in 14.3 s on this machine. Everything
seeded reproduces exactly: the six-order table `tab:ch08-orders` (16/16/16/fail/21/fail
with `optimal_soc == 16`), the machine-generated trace `tab:ch08-trace` (I re-derived all
seven expansions, the tie-breaking and the three blocked successors of step 3 by hand and
they agree line for line), the pocket-corridor optimum 11, the bypass corridor (best order
16, optimum 15), the HCA* expansion counts 32 509 vs 11 034 on 20 grids of 20x20 with 30 %
obstacles and 8 agents, the `whca_star(inst, window=6, step=3)` costs 6/6/4, and every
number of the ordering experiment, which I recomputed from `figures/data/ch08-orders.dat`
(random fails 19/240, mcf 15/240, lpf 1/240, restarts 1/240; at k=32 soc 1.163 / 1.201 /
1.207 / 1.124; 13 % and 23 % failure for a single random order at k=32 and k=28; lpf and
mcf within one point for k >= 24). Two claims do **not** reproduce: the WHCA* exercise
(required change 2) and, in a weaker sense, the wall-clock benchmark (see suggestions).
I also re-derived both counterexample plans, the incompleteness argument and the
well-formedness proof by hand; that is where required change 1 comes from.

**Round-1 items.** All eight required changes of round 1 are present and correct in the
current text: the "agent 1 before agent 3" characterisation (line 411), the restricted
dominance statement with `\cref{thm:ch04-surely}` (lines 673-679), the timed benchmark and
both call sites (lines 585-590, 1063-1066), the rewritten WHCA* "First, ..." paragraph
(lines 738-744), the corrected "as if no other agent existed" sentence (lines 723-725), the
`fig:ch08-orders` caption and the most-constrained-first paragraph (lines 785-800), the
`\pi_i[t]` notation (no `\pi(\cdot)` form is left anywhere in the chapter or the solutions),
and the `\cbs`/`\ecbs` expansion at first use (line 48). None of them is re-raised. Required
change 3 below is new: it is the consequence of the reviser's *deviation* from round-1 item 4,
which was based on a measurement I cannot reproduce.

## Verdict

**Minor revision.** The chapter is technically strong, complete against every "must cover"
item of `docs/specs/ch08.md` and against Week 3 of the training plan, well written, and its
numbers are machine-checked. But two substantive things are wrong and both were verified by
running the chapter's own code: the definition of a well-formed instance is missing the
distinctness hypothesis, which makes the chapter's main theorem false as stated (I give a
three-cell counterexample that the code confirms), and part (b) of `exr:ch08-whca` together
with its published solution asserts an outcome that `whca_star` does not produce. Four
smaller items complete the list. Every required change is a local edit; nothing structural
needs to move.

## Required changes

1. **`def:ch08-wellformed`, lines 204-213 (and the sentence at line 200).**
   *Problem (A - technical accuracy: the main theorem is false as stated).* The definition
   says only that $P = \set{s_1,\dots,s_k,g_1,\dots,g_k}$ is "the set of all endpoints" and
   that each agent has a path avoiding the endpoints other than its own. It never requires
   the $2k$ endpoints to be **distinct**, yet line 200 asserts that well-formed instances
   have "endpoints ... all distinct", the proof of `thm:ch08-wellformed` uses it (line 613:
   "$s_i$ is not parked on because goals are distinct from starts"), and
   `code/ch08_prioritized.py` enforces it (`is_well_formed` starts with
   `if len(set(endpoints)) != 2 * inst.k: return False`). Without it the theorem is false.
   Counterexample, checked with the chapter's own code: the $1 \times 3$ grid
   $(0,0)-(0,1)-(0,2)$, agent 1 from $(0,1)$ to $(0,2)$, agent 2 from $(0,0)$ to $(0,1)$.
   Every agent has a path that visits no endpoint but its own two, so the instance is
   well-formed under `def:ch08-wellformed` as written; but
   `prioritized_planning(inst, [1, 0], revised=True)` returns `None`, because under the
   revised rule agent 2 must avoid $s_1 = (0,1)$, which is its own goal. So
   `thm:ch08-wellformed` ("returns a valid plan for *every* priority order") fails on an
   instance its own hypothesis admits.
   *Fix.* Make distinctness part of the definition, as Čáp et al. do: replace the first
   sentence by "Let $P = \set{s_1, \dots, s_k, g_1, \dots, g_k}$ be the set of all
   **endpoints**, and assume they are pairwise distinct, $\abs{P} = 2k$." Then add one
   sentence after the definition: "Distinctness is not a technicality: if some $g_j$ were
   the start $s_i$ of another agent, the revised rule would turn $g_j$ into a static
   obstacle for agent $j$ and its search would fail at once, as noted after
   `def:ch08-order`. The function `is_well_formed` of `code/ch08_prioritized.py` tests
   distinctness first, then runs the $k$ breadth-first searches." Finally, in
   `appendices/solutions/ch08-solutions.tex`, solution `exr:ch08-wellformed`(a), add the
   distinctness test to the algorithm and its cost: "First check in $\bigO{k}$ that the
   $2k$ endpoints are distinct; then, for each agent $i$, ..."

2. **`exr:ch08-whca`(b), lines 1193-1200, and the corresponding paragraph (b) of
   `appendices/solutions/ch08-solutions.tex`.**
   *Problem (A - a claim the code does not reproduce).* The exercise states: "Run
   `whca_star` with $\delta = 1$ and windows $w = 2, \dots, 12$. For every one of them the
   rounds never end and the function returns `None`, even when $w$ is larger than the whole
   corridor", and the solution repeats it ("`whca_star` therefore reaches `max_rounds` and
   returns `None` for every $w = 2, \dots, 12$"). On the instance the exercise describes -
   `Instance(["@.@@@@@@@", "........."], [(1,0),(1,8)], [(1,8),(1,0)])`, i.e. the nine-cell
   corridor $(1,0)\dots(1,8)$ whose only pocket is $(0,1)$ - `whca_star(inst, window=w,
   step=1)` returns `None` only for $w = 2, 3, 4, 5$. For $w = 6, 7, 8$ it returns an
   executed plan of costs $[10, 10]$ and for $w = 9, \dots, 12$ one of costs $[12, 12]$, and
   `validate` rejects each of them (for $w = 6$: `vertex conflict agents 0,1 at (1,4) t=5`).
   Both agents need at least 15 and 8 steps in any valid plan, so these are plans in which
   the agents walk through each other. The mechanism, obtained by instrumenting
   `space_time_astar` inside `whca_star`, is exactly the stay-put branch: in the round in
   which agent 1 stands at $(1,3)$ and agent 2 at $(1,4)$ and agent 1 plans first, agent 1
   reserves the straight path $(1,3)@0,\dots,(1,8)@5$ and parks $(1,8)$ from $t = 5$;
   agent 2 is then chased backwards down the corridor - each reserved move forbids the
   turn-around by the swap test and each reserved vertex forbids the wait - until it is
   cornered at $(1,8)@4$, where waiting hits the parked goal and turning back hits the
   reserved move $((1,7),(1,8),4)$. Its search returns `None`, it stays put, and agent 1
   walks into it. For $w \le 5$ the parked entry at $t = 5$ falls outside the window, the
   cornered agent escapes beyond the window, and the oscillation of part (a) runs for ever.
   *Fix.* Replace part (b) by: "(b) Run `whca_star` with $\delta = 1$ and windows
   $w = 2, \dots, 12$ and check every returned plan with `validate`. For $w \le 5$ the
   rounds never end and the function returns `None`. For $w \ge 6$ it returns an executed
   plan that the validator rejects: the two agents pass through each other. Explain both
   outcomes. Which of the two agents sees the other one at all in a given round? What
   happens to the agent that is planned second when every cell in front of it is reserved,
   and which branch of `alg:ch08-whca` does it then take?" Rewrite solution (b) around the
   mechanism above (chased backwards, cornered at the dead end by the parked goal and the
   reserved move, `space_time_astar` returns `None`, stay-put branch, collision), and keep
   the existing correct observation that enlarging $w$ does not help because only the first
   $\delta = 1$ step of the retreat is ever executed.

3. **`sec:ch08-whca`, line 743.**
   *Problem (C - a dangling promise to the reader, introduced by the round-1 deviation).*
   The sentence ends "... the agent takes the stay-put branch of
   line~\ref{alg:ch08-whca:search}, which is one of the two ways in which a windowed plan
   loses its guarantee." The chapter never says what the second way is, so "one of the two
   ways" leaves the reader hanging. The reviser weakened round 1's wording (which pointed
   at `exr:ch08-whca`) because the stay-put branch appeared never to fire there; as
   required change 2 shows, it does fire there, for every $w \ge 6$.
   *Fix.* End the sentence: "... the agent takes the stay-put branch of
   line~\ref{alg:ch08-whca:search} and moves without any guarantee at all - this is how the
   windowed plans of \cref{exr:ch08-whca} come to contain a collision. The other way is the
   window itself: beyond $t = w$ the table is empty, so a plan that looks safe now can be
   invalidated by the next round."

4. **Proof of `thm:ch08-wellformed`, "Going is unblocked", lines 617-620.**
   *Problem (A - a false intermediate claim in the proof of the main theorem).* "After time
   $T^*_j$ every earlier agent is parked on its own goal, so $R$ contains no timed vertex
   entry and no move entry with $t \ge T^*_j$." $R_V$ *does* contain a timed vertex entry at
   $t = T^*_j$: the arrival of the agent whose arrival time defines $T^*_j$ is reserved as
   $(g_{\sigma(m)}, T^*_j)$. The bound is correct for move entries ($t \le T^*_j - 1$) but
   off by one for vertex entries. The conclusion is unaffected, because the wait-then-go
   path is still at $s_i$ at time $T^*_j$ and $s_i$ is never reserved, but a careful reader
   stumbles here.
   *Fix.* "After time $T^*_j$ every earlier agent is parked on its own goal, so $R$ contains
   no timed vertex entry with $t > T^*_j$ and no move entry with $t \ge T^*_j$; the wait-then-go
   path is still at $s_i$ at time $T^*_j$, which no earlier agent ever reserved. The only
   blocked cells at times $t > T^*_j$ are the goals $g_{\sigma(m)}$, $m < j$, which $P_i$
   avoids by construction."

5. **`code/ch08_prioritized.py`, `_self_test()` step 7 (the timing benchmark).**
   *Problem (G - violates `STYLE_GUIDE.md` section 6).* The self-test must run "in under 10
   seconds"; it now takes 14.3 s here and, by the reviser's own note, about 19 s on the
   machine used for writing, because step 7 plans three 100x100 instances with 40 agents.
   *Fix.* Keep the benchmark but make it cheap by default: run the three seeded instances
   only when the script is called with a `--bench` flag (`if "--bench" in sys.argv:`), and
   otherwise time a single seeded 100x100 / 40-agent instance and print it. Then adjust
   line 585-590 to say how the reader reproduces the figure ("run `python3
   code/ch08_prioritized.py --bench`"). The self-test must be back under 10 s.

6. **`sec:ch08-hca`, lines 674 and 676; `sec:ch08-implementation`, line 916.**
   *Problem (F - undefined symbol, `STYLE_GUIDE.md` section 3 requires every symbol to be
   defined before use).* $C^*$ appears three times in this chapter and is never introduced
   here; it is defined only in \cref{ch:ch04}.
   *Fix.* At its first use (line 674) write "every state with $\fcost < C^*$, where $C^*$ is
   the arrival time of the optimal unblocked path, that the search with $\hcost^*$ expands
   ...". No other change is needed; the two later uses are then clear.

## Suggestions

* **The wall clock (lines 585-590).** The text says the self-test "prints times of about
  $2$, $4$ and $7$ seconds, a median of roughly $4$ seconds". On this machine it prints
  `1.7, 3.2, 5.4 s (median 3.2 s)`. The machine caveat that follows ("your own times will
  differ") makes this honest, and round 1 already prescribed exactly this fix, so I do not
  re-raise it; but the chapter would age better with a relative statement: "a few seconds
  per instance, with a spread of a factor of three between instances of the same size - the
  self-test prints the three times and their median so that you can compare your own
  machine."
* **Solutions coverage.** `appendices/solutions/ch08-solutions.tex` now covers five of the
  eight exercises (`table`, `following`, `pocket`, `wellformed`, `whca`). The one still
  worth adding is `exr:ch08-hca`(c): "is the parked-agent heuristic still admissible?" has a
  non-obvious answer (it is not - a parked agent may sit on the goal-side of a corridor that
  the agent never has to enter, so the modified distance can exceed the true remaining cost
  of the unblocked optimum; it is exact when every parked cell is a permanent obstacle for
  the rest of the plan, e.g. when no higher-priority agent ever leaves its goal and no
  path through a parked cell is ever needed).
* **Difficulty spread (category E, not blocking).** Seven of the eight exercises are
  `\difficulty{1}` or `\difficulty{2}` and only the coding exercise is `\difficulty{3}`.
  `exr:ch08-whca` - three parts, a hand simulation, a code experiment and a design question
  - is a level-3 exercise; promoting it would give the spread 2/4/2 instead of 2/5/1.
* **Notation table.** The row for $R = (R_V, R_E)$ suggested in round 1 is still absent from
  `frontmatter/notation.tex`. The reviser correctly declined to edit a file outside the
  chapter's scope; the front-matter owner should add
  `$R=(R_V,R_E)$ & reservation table: (vertex, time) and (move, time) entries, plus parked
  goals & \cref{ch:ch08}`.
* **Length.** 20 printed pages against the 13-15 of `docs/specs/ch08.md`. Nothing is
  padding, so no cut is required. If a page has to be found at copy-edit time, the two
  places that compress without loss are `sec:ch08-beyond` (four sentences could become two,
  keeping SIPP and the kinematic-constraints pointer) and the second half of the `dronebox`,
  whose list of failure modes repeats `sec:ch08-properties` almost verbatim.
* **`thm:ch08-sound`.** The second claim is prefixed "if $\hcost$ is admissible", but
  completeness of `alg:ch08-ca` on the finite space-time graph does not need admissibility -
  only per-agent optimality does. Splitting the sentence would make the hypothesis land
  where it is used, which matters because `thm:ch08-wellformed` cites the completeness half.
* **`alg:ch08-whca`.** "execute the first $\delta$ steps of every $\rho_i$" is silent about
  a plan shorter than $\delta$; the code pads with the last cell (`moves += [path[-1]] * ...`).
  Half a sentence in the walkthrough would close the gap between pseudocode and listing.

## What must be kept

The worked example remains the best thing in the chapter and must survive intact: one
$3 \times 7$ map carries the reservation table (`tab:ch08-table`), a genuinely
machine-generated search trace (`tab:ch08-trace`, which I re-derived expansion by expansion
including the tie-breaking - it is exactly right), the space-time picture of the same search
(`fig:ch08-spacetime`, whose three red dashed successors at $t = 2$ are precisely the
"V, V, E" of the trace), and the six-order table with a brute-force optimum. The two
counterexamples are minimal, correct, hand-checkable and correctly identified as not
well-formed; giving each its own panel plus the optimal plan in panel (c) is the right
design. The completeness proof for well-formed instances is a real proof and not a sketch -
the wait-then-go witness, the three separated claims, the corollary and the honest "the
bound is loose" remark, and above all the remark that isolates the single place where the
revised rule is used, are exactly what a graduate student reading alone needs (required
change 4 is one symbol inside it, not a structural objection). Keep the three pitfall boxes,
especially "checking the edge in the wrong direction", which is the bug every first
implementation has; keep the "collapsing time instead of a horizon" note attached to
`lst:ch08-search`, a genuinely useful implementation idea that most treatments omit; and
keep the ordering experiment with its unflattering result for most-constrained-first, which
is far more instructive than a tidy one. The bibliography is clean: all eleven keys resolve
in `references.bib` / `bib/ch08-extra.bib`, and the details I can vouch for are correct -
Silver 2005 (AIIDE 117-122), Erdmann and Lozano-Pérez 1987 (Algorithmica 2, 477-521), van
den Berg and Overmars 2005 (IROS 430-435), Bennewitz, Burgard and Thrun 2002 (RAS 41(2-3),
89-99), Čáp et al. 2015 (T-ASE 12(3), 835-849), Ma et al. 2017 (AAMAS 837-845), Ma et al.
2019 (AAAI 7643-7650), Phillips and Likhachev 2011 (ICRA 5628-5635), Hönig et al. 2016
(ICAPS 477-485), Stern et al. 2019 (SoCS 151-158) and LaValle 2006. Nothing is fabricated.
The 25 index entries, the 14-entry glossary file and the six figures with informative
captions are all above the bar of the style guide.

---

## Response to review (round 2)

All six required changes were applied. The chapter builds with status 0 and no errors
(`cd Overleaf && ./build.sh ch08-prioritized-planning`, 20 printed pages, the only
overfull box is in the front-matter list of algorithms and belongs to another chapter),
the self-test of `Overleaf/code/ch08_prioritized.py` passes in 4.9 s, and
`Overleaf/appendices/solutions/ch08-solutions.tex` was compiled separately with
`./build.sh --standalone`. `figures/data/ch08-orders.dat` was regenerated and is
byte-identical, so no figure changed.

**1. Distinctness in `def:ch08-wellformed` (A).** Applied as prescribed. The first
sentence now reads "Let $P = \set{s_1, \dots, s_k, g_1, \dots, g_k}$ be the set of all
endpoints, and assume that they are pairwise distinct, $\abs{P} = 2k$." A paragraph
after the definition explains why this is not a technicality (a goal that is another
agent's start becomes a static obstacle for its own owner under the revised rule, so
the completeness theorem would be false), points back to `def:ch08-order`, and says
that `is_well_formed` tests distinctness first and then runs the $k$ breadth-first
searches. Solution `exr:ch08-wellformed`(a) now begins with the $\bigO{k}$ distinctness
test and notes that the searches dominate its cost. I re-ran the reviewer's
counterexample: the 1x3 instance satisfied the old definition, `is_well_formed` returns
`False` (it already required distinctness) and `prioritized_planning(inst, [1, 0],
revised=True)` returns `None` — the definition, not the code, was at fault.

**2. `exr:ch08-whca`(b) and its solution (A).** Verified with the chapter's code:
`whca_star(inst, window=w, step=1)` returns `None` for w = 2,...,5 and an executed plan
for w = 6,...,12 that `validate` rejects (w = 6: `vertex conflict agents 0,1 at (1, 4)
t=5`; w = 7,8: `(1,5)`, t = 5; w = 9,...,12: `(1,5)`, t = 7). Part (b) was replaced by
the wording the review prescribes (run with `validate`, explain both outcomes, name the
branch of `alg:ch08-whca`). Solution (b) was rewritten around the mechanism, which I
confirmed by instrumenting `space_time_astar` inside `whca_star`: in the round with
agent 1 at (1,3) and agent 2 at (1,4) and agent 1 planning first, agent 1 reserves
(1,3)@0 ... (1,8)@5 and parks (1,8) from t = 5; agent 2 is chased backwards to (1,8)@4,
where the wait hits the parked goal and the turn-around hits the reserved move
((1,7),(1,8),4); its search returns `None`, it takes the stay-put branch, and agent 1
walks into it. The boundary at w = 6 is `in_window`, which keeps an entry only if
t < w, so for w <= 5 the parked entry at t = 5 is invisible and the oscillation of part
(a) runs for ever; I verified both regimes by replaying the rounds. The existing correct
observation (only the first delta = 1 step of the retreat is executed, and the pocket
lies behind the meeting point) is kept as the closing paragraph.

**3. "one of the two ways" at line 743 (C).** The sentence now ends: the agent "takes
the stay-put branch of line~\ref{alg:ch08-whca:search}: it stays where it is with no
guarantee at all, and an agent planned earlier in the same round may be walking straight
into it. This is how the windowed plans of \cref{exr:ch08-whca} come to contain a
collision. The other way is the window itself: beyond $t = w$ the table is empty, so a
plan that looks safe now can be invalidated by the next round." I kept the reviewer's
content but said "it stays where it is" instead of "moves", because the branch makes the
agent stand still — the collision comes from the agent planned before it.

**4. "Going is unblocked" (A).** Replaced by the prescribed text: no timed vertex entry
with $t > T^*_j$ and no move entry with $t \ge T^*_j$; the wait-then-go path is still at
$s_i$ at time $T^*_j$, which no earlier agent ever reserved; the only blocked cells at
times $t > T^*_j$ are the earlier goals, which $P_i$ avoids.

**5. Self-test runtime (G).** Step 7 of `_self_test` now times a single seeded
100x100 / 40-agent instance (seed 2) and prints `... 3.2 s (run with --bench for three
instances and their median)`; `python3 code/ch08_prioritized.py --bench` still plans
seeds 1, 2, 3 and prints the three times and the median (`1.8, 3.3, 5.8 s (median
3.3 s)`). `import sys` was added. The default self-test is down from 14.6 s to 4.9 s;
`--bench` takes 14.8 s. The text at lines 585-590 now tells the reader how to reproduce
the figure and follows the reviewer's suggestion of a relative statement ("a few seconds
per instance, with a spread of about a factor of three between instances of the same
size"), so no absolute time is quoted any more. The flag is typeset as `-{}-bench` so
that the two hyphens do not become an en dash.

**6. $C^*$ undefined (F).** Defined at its first use in `sec:ch08-hca`: "so for a single
agent against a fixed table, writing $C^*$ for the arrival time of the optimal unblocked
path, every state with $\fcost < C^*$ ...". The same words as the prescribed fix, moved
in front of the clause so that the sentence does not break in the middle. The two later
uses are unchanged.

### Suggestions

* **Wall clock:** taken, as part of required change 5 (relative statement, self-test
  prints the times).
* **Solution for `exr:ch08-hca`:** added, covering all three parts. (a) and (b) are
  machine-checked: on the worked-example map the true distance to $g_1 = (2,6)$ equals
  the Manhattan distance at every free cell, so both heuristics expand the same 22
  states for agent 1 in the order (3,1,2) and return the same path of cost 10. (c) The
  parked-agent heuristic is not admissible; the instance given is the open 3x3 grid with
  agent 1 from (2,1) to (0,1) and agent 2 from (0,0) to (0,2): agent 2 crosses (0,1) at
  t = 1, one step before agent 1 parks there, and arrives at cost 2, while the modified
  heuristic reports 4. The condition for exactness is stated as "every parked cell is
  already parked on at the time of the state being evaluated", which is the precise form
  of the reviewer's "permanent obstacle for the rest of the plan".
* **Difficulty spread:** `exr:ch08-whca` promoted to `\difficulty{3}` and retitled
  "Oscillation and collision in WHCA*", giving the spread 2/4/2.
* **`thm:ch08-sound`:** split, so that completeness on the finite space-time graph stands
  without a hypothesis and admissibility is required only for per-agent optimality.
* **`alg:ch08-whca` and plans shorter than $\delta$:** half a sentence added to the
  walkthrough, quoting `moves += [path[-1]] * (step - len(moves))` from the listing.
* **Notation table:** still not done, and still outside this chapter's scope —
  `frontmatter/notation.tex` needs the row
  `$R=(R_V,R_E)$ & reservation table: (vertex, time) and (move, time) entries, plus
  parked goals & \cref{ch:ch08}`. Please hand this to the front-matter owner.
* **Length:** unchanged at 20 pages; the round-2 edits add about half a page and nothing
  was cut, as the brief forbids removing required content to save space. The two
  compressible places named by the reviewer (`sec:ch08-beyond`, the second half of the
  drone box) are left for copy-edit time.
