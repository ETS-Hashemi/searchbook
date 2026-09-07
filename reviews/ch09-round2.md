# Review of Chapter 9 (Conflict-Based Search) - round 2

Reviewed artefacts: `Overleaf/chapters/ch09-cbs.tex` (1346 lines), figures
`Overleaf/figures/ch09/{idea,example,tree,mdd,symmetry,scaling}.tex`,
`Overleaf/figures/data/ch09-scaling.dat`, `Overleaf/code/ch09_cbs.py` (616 lines),
`Overleaf/code/figures/gen_ch09_scaling.py`,
`Overleaf/appendices/solutions/ch09-solutions.tex`,
`Overleaf/appendices/glossary/ch09-terms.tex`, `Overleaf/references.bib`,
`Overleaf/bib/ch09-extra.bib`, against `STYLE_GUIDE.md` section 9, `docs/specs/ch09.md`
and `docs/core-idea.txt` (Week 4), plus `reviews/ch09-round1.md` with the reviser's
response.

**Build.** `cd Overleaf && ./build.sh ch09-cbs` exits 0; `build/only-ch09-cbs.pdf`,
42 pages; no `!` errors; **no overfull box of any size** (both round-1 boxes are gone);
the only undefined references are cross-chapter (`ch:ch06`, `ch:ch08`, `ch:ch10`-`ch:ch25`,
`ch:appB`, `ch:appC`), which a single-chapter build is allowed to leave as `??`. No label,
citation, algorithm-line reference or `\cref` of this chapter is undefined. Float placement
is now good: every algorithm, table, figure and listing sits on the page of its first
reference or the next one.

**Length.** Chapter body = PDF pages 14-34 = **21 pages**, inside the 24-page limit.
No cuts are required and none are requested below.

**Code.** `python3 code/ch09_cbs.py` passes every assert in 2.5 s. I re-checked every
number the chapter quotes against the run and against `figures/data/ch09-scaling.dat`:
root costs 4/2/4 = 10; `N_1`..`N_6` costs 11/11/12/12/12/12 with 1/4/0/0/5/2 conflicts;
4 expanded, 7 generated, 9 low-level calls, optimum 12 (certified against
`joint_optimal_cost`); rectangle symmetry 5 x 10 paths and 15 expanded CT nodes;
coupled maze optimum 24, 0.012 s joint-space, 2000 CT nodes in 0.33 s;
1.3/4.0/7.8 at k = 2/4/6; 92/75/58 % and 55/241/622 and 441/1061/2398 for plain CBS;
15/114/92 and 66/771/308 and 100/92/75 % for ICBS; 23,600 against 17,700 low-level
expansions at k = 12; 616 lines of which 112 are `_test_*`. **All reproduce.** I also
recomputed by hand: the CBSH walk-through (`h_CG(N_0)=1`, keys 11/12/12/12, three
expansions instead of four), the shortest-path counts C(5,1)=5 and C(5,2)=10 of
`exr:ch09-rectangle`, the four conflicts of `N_2`, the three-node tree of
`exr:ch09-handtree`, the `exr:ch09-goalstay` instance (first conflict
`<a_1,a_2,(4,1),5>`), the horizon bound `T_max = H+1+D`, the depth bound
`Delta = k(|V|+2|E|)(C*+2)`, and the admissibility argument for `h_CG`. All correct.

**Round-1 items.** All eleven required changes of round 1 were applied and applied
*correctly* - I verified each one against the source, the code output and, for item 6,
against `def:ch07-conflicts` and `prop:ch07-hierarchy`(a) in
`chapters/ch07-mapf-problem.tex`. In particular the `h_CG` admissibility argument now
actually proves admissibility (the "agents whose cost rises" set really is a vertex cover,
and each of its members really pays at least one unit, because a cardinal split raises the
constrained agent's own path cost), the leader/follower sentence in `sec:ch09-example` is
now right, and the ICBS low-level-expansion sentence has the right unit. Nine of the ten
suggestions were taken as well. None of the round-1 items is re-raised.

## Verdict

**Minor revision.** The chapter itself is, as far as I can check it, technically clean:
definitions, both lemmas, the invariant, the optimality and completeness theorems and their
proofs, both pseudocodes, the complexity discussion, the worked example, the experiment and
every quoted number are correct and reproducible. What blocks an Accept is one factual error
that survives in the chapter's *glossary* file - the very error that required change 4 of
round 1 removed from the chapter body, so the book would now contradict itself between
Chapter 9 and Appendix B - plus one terminology slip in the same file. Both fixes are a
single sentence each; nothing in the chapter has to be restructured.

## Required changes

1. **`Overleaf/appendices/glossary/ch09-terms.tex`, entry "Meta-agent CBS (MA-CBS)"
   (last clause).** Category **A**. The entry says MA-CBS interpolates "between \cbs
   ($B = \infty$) and joint-space \astar ($B = 0$)". This is the claim that round-1
   required change 4 corrected in `sec:ch09-macbs`: with $B = 0$ MA-CBS merges *a pair* at
   its first conflict, so agents that never conflict are never merged and the algorithm is
   Standley's independence detection with a joint-space search per interacting group, not one
   joint search over all $k$ agents. As it stands, the glossary of Appendix B contradicts
   \cref{sec:ch09-macbs} of the same book. Fix: replace the clause by
   "interpolating between plain \cbs ($B = \infty$) and Standley's independence detection
   ($B = 0$), in which every pair is merged at its first conflict, so each group of
   interacting agents is solved by a joint-space \astar while agents that never conflict are
   still planned alone." (Same wording as the chapter, so the two agree verbatim.)

2. **`Overleaf/appendices/glossary/ch09-terms.tex`, entry name "Goal-occupied-later test"
   (last entry).** Category **F** (cosmetic). Round-1 required change 10 standardised the
   chapter on **goal-stay test** (the name used by `ch08` line 280, by the Chapter 4 glossary
   entry "Space-time A*" and by the Chapter 8 glossary entry "Cooperative A*"), keeping
   "goal-occupied-later test" only as a parenthetical at `ch09-cbs.tex` line 224. The
   glossary entry still carries the non-standard name as its head word, so the assembled
   glossary will list the concept twice under two names. Fix: rename the entry to
   `\item[Goal-stay test (goal-occupied-later test)]` and leave the definition as it is.
   While there, change the module docstring of `Overleaf/code/ch09_cbs.py` line 11
   ("with the goal-occupied-later test and a finite horizon") to "with the goal-stay test and
   a finite horizon", so the file agrees with the in-code comment on the goal test and with
   the listing caption of `lst:ch09-lowlevel`.

## Suggestions

* `sec:ch09-macbs`, "counts, for every pair of agents, the conflicts split between them
  *along the current branch*". Sharon et al.\ (AIJ 2015, Section 5) maintain a conflict
  matrix `CM[i][j]` that is incremented whenever a conflict between the pair is found, and I
  read that counter as global over the whole CT search rather than per branch. Please check
  the paper and either drop "along the current branch" or say "in the search so far (some
  implementations count only along the current branch)".
* `sec:ch09-example`, "Depth one": "$a_2$ now moves up into $(2,2)$ at $t=1$ while $a_3$
  moves down into $(2,1)$". Both agents *arrive* at $t = 2$; the move starts at $t = 1$,
  which is why the conflict carries index 1. "between $t = 1$ and $t = 2$, $a_2$ moves up
  into $(2,2)$ while $a_3$ moves down into $(2,1)$" removes the ambiguity for a reader who
  is learning the edge-conflict indexing convention.
* `appendices/solutions/ch09-solutions.tex`, solution to `exr:ch09-handtree`. The exercise
  asks two questions and the solution answers only the first; the comparison with the joint
  state space is missing. Two sentences would close it, e.g. "The joint-space search must
  consider the reachable joint states of the two agents on the seven free cells - up to
  $7 \times 6 = 42$ position pairs per time step, of which A* expands a few dozen - against
  three CT nodes and four low-level searches here."
* `sec:ch09-experiment`, "(Its mean at $k = 10$ is larger than at $k = 12$ because it
  finishes one crowded instance that plain \cbs abandons ...)". The parenthesis explains a
  *between-solver* effect, but the anomaly it introduces is *within* ICBS across $k$. One
  extra clause fixes it: "... because at $k = 10$ it still solves an instance that needs 771
  nodes, whereas at $k = 12$ the three hardest instances time out and drop out of the mean
  altogether."
* `def:ch09-ctnode`: "Every non-goal node has two children". The algorithm discards a child
  whose low level fails (line~\ref{alg:ch09-cbs:replan}), so "at most two children, one per
  constraint of the split; a child whose low-level problem is infeasible does not exist"
  would match `alg:ch09-cbs` exactly.
* `def:ch09-constraint`, `def:ch09-lowlevel` and `def:ch09-cardinal` are never `\cref`ed.
  Consider referring to `def:ch09-cardinal` from `tab:ch09-conflict-types` and to
  `def:ch09-lowlevel` from `alg:ch09-lowlevel`'s walkthrough, so the numbered definitions
  earn their labels.
* Still open from round 1 and still outside this chapter's remit:
  `frontmatter/notation.tex` is the Phase-1 placeholder and should gain this chapter's
  symbols ($\pi_i$, $\gamma_i$, `SoC`, $C^*$, $\langle a_i,v,t\rangle$, $N.\mathcal{C}$,
  $N.\cost$), and `searchbook.sty` should gain a third path style so
  `figures/ch09/example.tex` need not improvise `draw=sbGreen,line width=1.6pt`. Keep both
  on the book-level list.

## What must be kept

Everything the round-1 review asked to keep survived, and the round-1 repairs made the
chapter stronger rather than patchier. Keep the proof section exactly as it is: the
decomposition into "a split loses no solution" / "a node's cost is a lower bound" / "the
invariant of the high level", the honest completeness proof that really bounds the number of
nodes of cost at most $C^*$ (via the time index of any constraint that can appear on a
branch), and `rem:ch09-unsolvable`, which admits that CBS does not terminate on unsolvable
instances. Keep the worked example in full - three agents, `fig:ch09-example` with its new
per-panel timing annotations, `fig:ch09-tree`, `tab:ch09-ct` and `tab:ch09-timeline` are a
model of how to show a search tree, and the four lessons after it are precisely the four
things students get wrong. Keep the now-correct `h_CG` argument and the CBSH walk-through on
the worked example: it is rare for a textbook to show a high-level heuristic *changing the
expansion order on an instance the reader already knows*. Keep the corridor-versus-open-room
analysis with the 15-node rectangle measurement and the coupled maze - this is the most
honest account of where CBS loses to joint-space search that I have seen at this level - and
keep all three pitfall boxes, the $T_{\max} = H+1+D$ horizon, the goal-stay treatment in both
the low level and the validator, and the `sec:ch09-variants` sequence cardinal -> bypass ->
MA-CBS -> CBSH -> symmetry, which ends on the one principle worth memorising: any pair of
constraint sets such that every solution satisfies at least one of them is a legal split.
Keep the code, its certification against a joint-space optimum on 65 random instances, and
the generated scaling experiment with its caveat paragraph: together they are exactly the
Week-4 milestone.
