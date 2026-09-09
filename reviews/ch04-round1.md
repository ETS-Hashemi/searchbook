# Review of Chapter 4 (A* Search) - round 1

Reviewed artefacts: `Overleaf/chapters/ch04-astar.tex` (1625 lines), figures
`Overleaf/figures/ch04/{idea,heuristics,example,inadmissible,tiebreak,expansions,spacetime}.tex`,
code `Overleaf/code/ch04_astar.py` and `Overleaf/code/figures/{gen_ch04_expansions.py,gen_ch04_grids.py}`,
data `Overleaf/figures/data/ch04-expansions.dat`, `Overleaf/appendices/solutions/ch04-solutions.tex`,
`Overleaf/appendices/glossary/ch04-terms.tex`, `Overleaf/bib/ch04-extra.bib`, `Overleaf/references.bib`,
against `STYLE_GUIDE.md` section 9, `docs/specs/ch04.md` and `docs/core-idea.txt` (Week 1).

Build: `./build.sh ch04-astar` exits 0, no `!` errors, no undefined reference or citation belonging
to this chapter, one overfull box (29.1 pt) that comes from the *List of Algorithms* entry for the
RRT chapter, not from Chapter 4. The chapter itself occupies pp. 18-41 of `build/only-ch04-astar.pdf`,
i.e. **24 pages** - exactly at the cap.

Code: `python3 code/ch04_astar.py` prints `ch04_astar: all self-tests passed` (exit 0).
Re-running `gen_ch04_grids.py` reproduces the committed `example.tex` and `tiebreak.tex` byte for byte.

Independent recomputation confirmed every number quoted in the text: cost 13 / 21 expansions /
26 (Dijkstra) / 24 (small-`g` ties) / `9+2*sqrt2 = 11.828` with 24 expansions on the 8-connected
version; the ten rows of Table 4.2 including the `Open` column; the expansion order
`(3,4),(3,3),(3,2),(0,4),(3,1),(3,5)`; the goal being *generated* at step 20 and *popped* at step 21;
the four cells left in `Open` with `f = 13,13,13` and `(3,0)` at `f = 15`; 39 vs 400 expansions in
Figure 4.5; "6 of 40" suboptimal Manhattan runs in the pitfall box; the space-time counts
3 / 4 / 5 / 6 expansions and costs 2 / 3 / 4 / 6; the corridor path of cost 5, the six-expansion
failure, `H = 4`, `D = 3`, `T_max = 8`, and `H = 1`, `D = 3`, `T_max = 5` for the mini example.
All of `ch04-expansions.dat` at `n = 100` matches the prose: free 7513.3, Dijkstra 7451.8,
A*(Manhattan) 756.2, A*(octile) 3323.6, wA*(w=2) 371.8 / 271.3, ratios 1.0694 / 1.1197 / 1.0451 /
1.0582 (max ratio over all sizes 1.1197 < 1.13). The numbers in `appendices/solutions/ch04-solutions.tex`
also check out (h*(1,4)=8, h*(3,1)=5; the 4x4 Manhattan trap returns 6 against the optimum
4+sqrt2 = 5.414; the space-time variants give 5, 4 and 3 expansions; the ring counterexample gives
true arrival 10 against the naive horizon 7).

## Verdict

**Minor revision.**

Chapter 4 is, technically, the strongest chapter I have reviewed in this book so far. Every
definition, theorem, proof, complexity claim and pseudocode line I checked against
Hart-Nilsson-Raphael, Pearl, Dechter-Pearl, Pohl, Likhachev et al., Silver and Stern et al. is
correct, correctly hedged and correctly attributed; every "must cover" item of `docs/specs/ch04.md`
is present; every number in the prose is reproduced by the code. Two localised statements are
nevertheless wrong or under-qualified, and one style-guide item (acronym expansion) is missed. All
three fixes are one- or two-line edits; none touches the structure, the proofs or the code.

## Required changes

1. **`fig:ch04-example` caption, lines 399-400 (`chapters/ch04-astar.tex`): the claim about what
   Dijkstra additionally expands is factually wrong.** The caption ends "(b) Dijkstra's algorithm
   ($\hcost = 0$) expands 26 cells, including the whole south-west corner." A* *already* expands the
   whole south-west corner: its expansion list contains `(0,0),(1,0),(1,1),(1,2),(0,1),(0,2),(1,3),
   (0,3),(1,4)`. The five cells Dijkstra expands that A* does not are `(0,5),(1,5),(2,5)` - the
   *top* row, i.e. the north-west, since `(0,0)` is the bottom-left corner per `def:ch02-grid` - and
   `(3,0),(4,0)` on the bottom row east of the first wall. (Verified: `set(dijkstra) - set(astar) =
   {(0,5),(1,5),(2,5),(3,0),(4,0)}`; `set(astar) - set(dijkstra)` is empty.) Concrete fix: replace
   the final clause by "(b) Dijkstra's algorithm ($\hcost = 0$) expands 26 cells, five more than
   \astar: the top-row cells $(0,5)$, $(1,5)$, $(2,5)$ and the bottom-row cells $(3,0)$, $(4,0)$,
   which \astar either leaves in \Open or never generates." *Category A (and D).*

2. **`keyidea` box, lines 109-114: the optimality statement omits the re-opening condition that the
   chapter itself later shows to be necessary.** The box reads "If $\hcost$ never overestimates the
   remaining cost, the first goal that \astar expands is reached by an optimal path." For the
   graph-search algorithm the reader is about to meet, that is false without
   line~\ref{alg:ch04-astar:reopen}: the chapter's own four-node example in
   *"Admissible but inconsistent heuristics"* (sec:ch04-properties) returns cost 5 instead of 4 when
   re-opening is switched off, and `ch04_astar.py` asserts exactly that
   (`res.cost == 5.0  # suboptimal`). `thm:ch04-optimal` and the summary box both state the
   condition; only the key-idea box drops it. Concrete fix: "... the first goal that \astar
   \emph{pops} is reached by an optimal path, provided a closed node may be re-opened when a cheaper
   path to it turns up (\cref{alg:ch04-astar}, line~\ref{alg:ch04-astar:reopen})." *Category A.*

3. **Line 36 and line 1421: acronyms used without expansion at first use in this chapter.**
   `STYLE_GUIDE.md` section 3 requires every acronym to be defined at first use *in every chapter*.
   The chapter expands MAPF and CBS but not ECBS (line 36, "its bounded-suboptimal variant \ecbs")
   nor ORCA and DWA (line 1421, "\orca, \cref{ch:ch13}; DWA, \cref{ch:ch14}"). Concrete fix: write
   "its bounded-suboptimal variant, enhanced \cbs (\ecbs)" at line 36, and "optimal reciprocal
   collision avoidance (\orca), \cref{ch:ch13}; the dynamic window approach (DWA), \cref{ch:ch14}"
   at line 1421. *Category F (cosmetic).*

## Suggestions

* **Length.** The chapter is exactly at the 24-page cap and six pages above the 16-18 pages that
  `docs/specs/ch04.md` targets. I do **not** require cuts - everything present is required content
  or earns its place - but if room is ever needed, the two most compressible spots are
  (a) `ex:ch04-corridor` (the passing-bay example, ~2/3 page), whose reservation-table and
  prioritized-planning-incompleteness lesson is re-taught in `ch:ch08`, and which could shrink to
  four or five lines plus the two paths; and (b) the last five sentences of the Pearl paragraph in
  *Complexity*, which could lose the `(1-epsilon)h*` aside without losing the point.
* **Line 26-27 (motivation).** "in the experiment of \cref{sec:ch04-variants}" points at the whole
  *Variants* section; `\cref{sec:ch04-experiment}` is the subsection that actually contains the
  numbers and is a friendlier pointer for a reader who jumps.
* **`lst:ch04-spacetime`.** The listing maintains a `closed` set that `alg:ch04-spacetime` does not
  mention (the pseudocode says `Gen` "plays the role of both \Open and \Closed"). One clause in the
  listing caption - "the `closed` set is kept only for the traces and figures; correctness needs
  only `parent`" - would remove the apparent mismatch.
* **Complexity subsection.** One sentence on the admissible-but-inconsistent worst case (a node can
  be re-expanded exponentially often; Martelli 1977, and Pearl ch. 3) would round out the picture and
  motivate `thm:ch04-consistent`(i) even more sharply. Only add the reference if you can vouch for it.
* **`tab:ch04-heuristics`.** For symmetry with the other rows, the octile entry in the 4-connected
  column could add "not exact" beside "consistent (below Manhattan)".
* **`def:ch04-problem`.** The codomain is given as $\hcost\colon V \to \R_{\ge 0}$ while
  $\hcost^*(n) = \infty$ is allowed two lines later; writing $\R_{\ge 0}\cup\{\infty\}$ for $\hcost^*$
  (or saying $\hcost$ is finite by fiat) removes a small inconsistency.

## What must be kept

Almost everything. The proof architecture is the best part of the chapter: a single invariant
(`thm:ch04-invariant`, "an optimal-path node is always open") that is proved once and then reused
verbatim for optimality with an admissible heuristic, for no-re-expansion with a consistent one, and
for the weighted-A* bound - including the explicit remark that the lemma never touches the heuristic,
which is exactly why it survives the change of key. Keep it. Keep `thm:ch04-surely` and the honest
"may or may not expand nodes with $f = C^*$" caveat, and keep the matching caveat in
`thm:ch04-dominance`; most textbooks get that wrong. Keep the careful statement of what Dechter and
Pearl actually proved, and the sentence that says what it does *not* claim. Keep the entire
space-time section: `def:ch04-goalstay`, the pitfall about the too-strong `t >= H` goal test, and
`thm:ch04-horizon` with its `T_max = H + 1 + D` bound and proof are a genuinely useful, correct and
rarely-written-down treatment that `ch:ch08`-`ch:ch10` can now simply cite. Keep the floating-point
paragraph (`round(f, 9)`, `EPS`) - it is the reason the tie-breaking experiment is reproducible at
all. Keep the three pitfall boxes, the `(f, -g, counter)` discussion, the seven figures (the
`fig:ch04-idea` disc-versus-ellipse pairing and the `fig:ch04-spacetime` time-layer drawing are both
excellent), the ten well-graded exercises, and above all the discipline of having `ch04_astar.py`
assert every number that appears in the prose and in the solutions.
