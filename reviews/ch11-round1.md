# Review of Chapter 11 (M*, Push-and-Swap, Push-and-Rotate) - round 1

Reviewed against `STYLE_GUIDE.md` section 9 (categories A-H), `docs/specs/ch11.md`,
`docs/core-idea.txt`, the six figure files in `Overleaf/figures/ch11/`, the code
`Overleaf/code/ch11_mstar.py` and its figure generators, and the appendix files
`Overleaf/appendices/solutions/ch11-solutions.tex`, `Overleaf/appendices/glossary/ch11-terms.tex`,
`Overleaf/appendices/appA-study-plan.tex`.

Build: `./build.sh ch11-mstar-push-and-swap` -> status 0, no `!` errors, no undefined
reference or citation of this chapter (only forward references `ch:ch12`, `ch:ch18`,
`ch:ch24` are `??`, which is expected in a single-chapter build), three overfull hboxes of
8.08 pt, 6.85 pt and 1.63 pt (all below the 15 pt threshold).
Code: `python3 code/ch11_mstar.py` runs in a few seconds and all `assert`s pass.
Length: the chapter occupies printed pages 48-67, i.e. exactly 20 pages, at the ceiling
given in the review brief and above the 12-14 pages of the spec; the excess is content the
spec demands, so no cut is *required* (see Suggestions for optional trims).

## Verdict

**Minor revision.** The chapter is technically strong, complete against the spec and the
training plan, and its worked example is fully reproduced by the code. Eight defects must be
fixed, but every one of them is local: six are single sentences or single pseudocode lines in
the chapter, two are an exercise statement plus the corresponding paragraph of the solutions
file. Nothing has to be restructured or re-derived.

## Required changes

1. **Location:** `\section{A worked example}`, paragraph *The four searches compared*
   (tex line ~672), sentence "plain joint \astar expands 24 nodes but examines $612$
   successor candidates, because every expansion enumerates $5^3 = 125$ joint moves".
   **Problem:** the stated reason is wrong and contradicts the number in front of it:
   $612/24 = 25.5$ candidates per expansion, not 125. `joint_astar` counts every element of
   `itertools.product(*[agent_moves(...)])`, and on this narrow map almost every cell has one
   to three neighbours ($(0,1)$ has one, $(3,1)$ has two), so $5^3$ is the obstacle-free
   maximum, never the actual count here.
   **Fix:** replace by "because every expansion enumerates the whole Cartesian product of the
   agents' move lists - up to $5^3 = 125$ joint moves, and $612/24 \approx 26$ on average on
   this narrow map, where most cells have only one or two neighbours".
   **Category:** A.

2. **Location:** `\begin{corollary}[No collisions, no search]`, `\label{thm:ch11-linear}`
   (tex line ~795): "the number of expansions is the makespan of the individual paths plus
   one".
   **Problem:** off by one against the algorithm and the code. `MStar` returns at
   line~`alg:ch11-mstar:goal` when $v_f$ is *popped*; $v_f$ is never expanded and is not
   counted. Verified with the chapter's own code: two agents on an obstacle-free
   $6 \times 2$ corridor, collision-free policy paths of makespan 5, gives
   `m.expansions == 5`, not 6. (The worked example is consistent with this: 31 expansions and
   "$v_f$ is popped next".)
   **Fix:** state "\mstar expands exactly the $T$ non-goal nodes of that path, one successor
   each, and then pops $v_f$ and returns: $T$ expansions, where $T$ is the makespan of the
   individual paths, whatever $k$ is", and adjust the proof's last sentence accordingly
   ("the goal is popped with $\gcost = \hcost(v_s)$ after $T$ expansions").
   **Category:** A.

3. **Location:** `\section{Problem statement and notation}`, paragraph after
   `\begin{definition}[Cost of a joint move]` (`def:ch11-cost`, tex line ~180): "It agrees
   with the sum of costs of \cref{ch:ch07} on every plan in which no agent leaves its goal
   after arriving, which includes every plan of this chapter".
   **Problem:** the second half is false, and the counterexample is in this chapter. The
   push-and-swap plan of \cref{sec:ch11-quality} displaces agent $a$ after it has reached
   $c_1$ (path `c0 c0 c1 c1 c2 c2 c3 s s s c3 c3 c2 c2 c1`); its cost under
   \cref{eq:ch11-cost} is 26 while the sum of costs quoted in the text is 27
   (`active_cost` = 26, `sum_of_costs` = 27 in `ch11_mstar.py`).
   **Fix:** "... which includes every plan returned by joint \astar and \mstar in this
   chapter; the push-and-swap plan of \cref{sec:ch11-quality}, in which an agent is displaced
   from its goal, costs 26 under \cref{eq:ch11-cost} against a sum of costs of 27."
   **Category:** A.

4. **Location:** proof of `\begin{theorem}[\mstar is complete and optimal]`
   (`thm:ch11-optimal`), *Step 2: everything cheap is expanded* (tex line ~825).
   **Problem:** the claim "A node generated with $\fcost \le C^*$ is expanded before the run
   ends" is false for a successful run: when $v_f$ is popped with $\fcost = C^*$, other nodes
   with $\fcost = C^*$ may still be in \Open. The justification that follows ("if that cost
   were larger than $C^*$, or the run ended in failure ...") is valid only under the
   contradiction hypothesis introduced later, in Step 3, so as written the proof asserts more
   than it proves.
   **Fix:** move the hypothesis in front of Step 2, e.g. begin Step 2 with "Assume, for the
   contradiction of Step 3, that the run either fails or returns a cost larger than $C^*$.
   Then every generated node with $\fcost \le C^*$ is expanded before the run ends, because
   the goal is popped only with $\fcost$ equal to the returned cost, so every such node is
   popped first." Nothing else in the proof changes.
   **Category:** A.

5. **Location:** `\begin{algorithm}` `Push-and-Swap (conceptual)` (`alg:ch11-pas`), the line
   "$b \gets$ the locked agent on the next vertex of $p$" (tex line ~886).
   **Problem:** contradicts the text of \cref{sec:ch11-constructive} one page earlier ("The
   push fails when the blocking agent is locked **or when no empty vertex can be reached
   without crossing $p$**"): in the second case the blocker is not locked, so the pseudocode
   has no agent to bind $b$ to and the algorithm falls through. Luna and Bekris invoke `swap`
   on whichever agent occupies the next vertex of $p$ after a failed push.
   **Fix:** change the line to "$b \gets$ the agent occupying the next vertex of $p$" and the
   resolve line~`alg:ch11-pas:resolve` to "if $b \in U$, remove it from $U$ and schedule it to
   be solved again".
   **Category:** A.

6. **Location:** `\begin{exercise}` `\label{exr:ch11-collision-sets}` (Exercise 11.2, tex
   line ~1206) and the matching solution in
   `Overleaf/appendices/solutions/ch11-solutions.tex` (`\begin{solution}{exr:ch11-collision-sets}`,
   last three sentences).
   **Problem:** the question "Which agent never enters a collision set, and why not ...?" and
   the solution's answer "Agent 3 never enters a collision set" are both false. Running the
   chapter's own code on that instance (`Graph.from_edges([("a","b"),("b","c"),("b","d")])`,
   starts `a, c, d`, goals `c, a, d`) gives collision sets $\{1,2\}$, $\{2,3\}$, $\{1,3\}$ and
   $\{1,2,3\}$; the start ends with $C = \set{1,2,3}$, and the run reports failure after 12
   expansions and 84 generated candidates. As soon as agent 2 is in a collision set it
   branches into the occupied vertex $d$, which is a vertex collision of agents 2 and 3 and is
   backpropagated. The solution's own justification is self-contradictory ("a vertex collision
   that adds only agents 2 and 3 ... where it is never tried").
   **Fix:** (i) replace the question by "At which expansion does agent 3 first enter a
   collision set, and which move puts it there? What is the collision set of the start when
   the search stops?"; (ii) rewrite the last third of the solution: agent 3 enters a collision
   set as soon as agent 2, already coupled, is allowed to try the move into $d$; the start
   ends with $C = \set{1,2,3}$; \mstar returns failure after 12 expansions / 84 generated
   candidates, guaranteed to terminate by \cref{thm:ch11-terminates}. Keep the first two
   thirds (policies, the first three expansions, the four limited neighbours, the
   unsolvability argument) - they are correct and were checked against the code.
   **Category:** A (also E).

7. **Location:** `\begin{exercise}` `\label{exr:ch11-swap-count}` part (c) (Exercise 11.6,
   tex line ~1257) and the matching paragraph of `ch11-solutions.tex`
   (`\begin{solution}{exr:ch11-swap-count}`, part (c)).
   **Problem:** "Show that the six exchange moves of \cref{fig:ch11-push-swap}(b) cannot be
   parallelised into fewer than four time steps without a conflict" is false under this
   chapter's own convention that following an agent into the cell it is leaving is allowed
   (\cref{sec:ch11-problem}). The six moves of the figure - $a\!:\!v\to n_1$, $b\!:\!u\to v$,
   $b\!:\!v\to n_2$, $a\!:\!n_1\to v$, $a\!:\!v\to u$, $b\!:\!n_2\to v$ - pair up into three
   time steps $\{1,2\}$, $\{3,4\}$, $\{5,6\}$, each pair being a following move on a
   different edge; three is optimal because each agent makes three moves and an agent moves
   at most once per time step. The solution's "chain of length four" argument is therefore
   wrong as well.
   **Fix:** ask for "exactly three time steps" and give the pairing above; replace the
   solution's dependency-chain sentence by "each of the three pairs is a following move
   (one agent enters the vertex the other leaves in the same step), and no fewer than three
   steps are possible because each of the two agents has to make three moves". Leave the
   multipush claim ("$d$ time steps") unchanged - it is correct.
   **Category:** A (also E).

8. **Location:** `\begin{exercise}` `\label{exr:ch11-coding}` (Exercise 11.7), first sentence:
   "This is the coding exercise of this chapter in the study plan (\cref{ch:appA}, Week~5)."
   **Problem:** contradicts `Overleaf/appendices/appA-study-plan.tex`, Week 5 (line ~379):
   "**Exercises.** The coding exercise of \cref{ch:ch10}. Read \cref{ch:ch11} to know how
   \mstar and Push-and-Swap differ from \cbs; the plan asks for awareness, not an
   implementation." The training plan's Week-5 coding exercise is the ECBS benchmark of
   \cref{ch:ch10}, not this one.
   **Fix:** "This is the coding exercise of this chapter. The study plan
   (\cref{ch:appA}, Week~5) asks only for awareness of \mstar and Push-and-Swap, so treat it
   as the optional extension of the Week-5 work." (The exercise content itself is exactly what
   `docs/specs/ch11.md` asks for and must stay.)
   **Category:** F (also B).

## Suggestions

* `\section{The algorithms}`, end of the operator-decomposition paragraph: "OD examines about
  $200$ times fewer successor candidates than plain joint \astar with six agents" is the
  *median* ratio ($76\,928 / 356 \approx 216$); the ratio of the means is $119$. Add the word
  "median" so the reader can find the number in `figures/data/ch11-expansions.dat`.
* `\subsection{Effort on random maps}` and the caption of `fig:ch11-expansions`: the caption
  says "30 instances per $k$", but the statistics are over the instances solved by all four
  methods (column `all`: 30, 30, 30, 29, 27). Worth one clause, and worth one more sentence
  noting the survivorship effect it creates - joint \astar's *mean* expansions fall from 63.7
  at $k=5$ to 29.6 at $k=6$ only because the hardest instances drop out of the common set.
* Proof of `thm:ch11-optimal`, Step 3: "Collision sets can shrink at most $k$ times along this
  process" reads as a contradiction of `def:ch11-limited` ("only ever growing"). Reword to
  "the set $A$ used in the argument is replaced by a strictly smaller one at most $k$ times".
* Caption of `tab:ch11-trace`: "\code{mstar(inst, trace=True)} prints all 31" - the function
  records them in `result.info["trace"]`; say "records all 31" (Exercise 11.5 already tells
  the reader to print them).
* \cbs is spelled out at first use in this chapter, \ecbs is not; add "enhanced \cbs (\ecbs)"
  at its first occurrence in \cref{sec:ch11-motivation}, as required by section 3 of the style
  guide.
* Push-and-Swap termination (\cref{sec:ch11-constructive}, paragraph before
  `alg:ch11-pas`): "so the current agent arrives after finitely many primitives and the loop
  terminates" argues only about the inner loop; the resolve step unlocks solved agents and can
  re-enter the outer loop. One clause ("the outer loop needs the more involved argument of
  \cite{luna2011push}, corrected in \cite{dewilde2014push}") would keep the chapter's otherwise
  scrupulous honesty about this algorithm.
* Length (category G, optional): the chapter is exactly 20 printed pages against a spec target
  of 12-14. If space is needed at book level, the three cheapest cuts that lose no content are
  (i) folding the prose of \cref{sec:ch11-experiment} into the caption of
  `fig:ch11-expansions` (about 10 lines), (ii) dropping `limited_neighbours` from
  `lst:ch11-core` (it restates \cref{eq:ch11-limited}; the listing is at the 45-line limit) and
  (iii) shortening "Phase 3: the patch", whose content is already in rows 9-24 of
  `tab:ch11-trace`. None of these is required.

## What must be kept

The worked example is the best part of the chapter and must survive revision untouched in
substance: the three-drone aisle instance, the four-phase narrative, `tab:ch11-trace`,
`fig:ch11-search-graph` and the "four searches compared" comparison are all reproduced
number-for-number by `ch11_mstar.py` (31/127, 24/612, 100/292, 27/162, cost 15, makespan 7,
55 configurations touched, 19 with $C=\set{1,2}$, 12 second expansions - I re-ran the
self-test and re-derived the joint-graph figure's 12 states, 18 joint moves and cost-7 optimal
plan independently). Keep the distinction between vertex collisions (a property of the
configuration) and swap collisions (a property of the move), together with the pitfall box
that explains it - this is the subtlest implementation point of M* and it is stated more
clearly here than in most published descriptions. Keep `thm:ch11-terminates` and the
three-step structure of the optimality sketch, the ID optimality proposition with its
restriction argument, the honest treatment of Luna and Bekris's completeness claim and de
Wilde et al.'s counterexamples, the "feasibility is not optimality" section with its 27-vs-14
number, and `tab:ch11-comparison`, which is the single most useful page in the MAPF part of
the book. All 16 citations resolve to real, correctly described entries in `references.bib`,
`bib/ch07-extra.bib` and `bib/ch11-extra.bib`; the bibliography needs no work.
