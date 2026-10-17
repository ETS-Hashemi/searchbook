# Chapter specification format

One file per chapter: `docs/specs/<id>.md`, 150–400 words, dense. Authors treat every
"must cover" item as mandatory; reviewers check against it. Write it so that a competent
author who has never seen the book produces the right chapter.

```
# Chapter N — <Title> (priority <Essential|Important|Optional>; <schedule slot, e.g. Week 3>)
File Overleaf/chapters/chNN-<slug>.tex, label ch:chNN. <Template: algorithm | concept | system | evaluation>. Target <pages> pages.
Must cover: <semicolon-separated list of definitions, results (with "proof" where a proof is required), algorithms (with pseudocode), worked example (what instance, what figure, what trace table), generated experiment figure (what is compared), variants, implementation notes, pitfalls, the application box content, exercises incl. the brief's coding exercise, cross-references to other chapters by ch: label>.
Code: Overleaf/code/chNN_<slug>.py: <functions and what the self-test must check, incl. "reproduces the worked-example numbers">. Generators: Overleaf/code/figures/gen_chNN_<slug>.py -> figures/data/chNN-<slug>.dat.
Cite: <bib keys that exist in references.bib, or the exact references to add>.
Do not cover: <what belongs to other chapters>.
```

## Example (from the drone book, Chapter 4)

```
# Chapter 4 — A* Search (priority Essential; Week 1)
File Overleaf/chapters/ch04-astar.tex, label ch:ch04. Algorithm template. Target 16–18 pages.
Must cover: best-first search with f=g+h; exact definitions of admissible and consistent heuristics; lemma consistency ⇒ admissibility (proof); theorem: A* with admissible h returns an optimal solution when nodes may be re-opened (proof); theorem: with consistent h no re-expansion is needed and f along expansions is non-decreasing (proof); inadmissible-heuristic counterexample figure; pseudocode (graph search, closed set, lazy PQ); worked example on a 6x6 grid with obstacles: figure of open/closed cells and final path, trace table of the first 8–10 expansions with g,h,f; grid heuristics Manhattan, octile, Euclidean, Chebyshev with a table of admissibility/consistency per connectivity; dominance (statement + proof sketch); tie-breaking; weighted A* with w-suboptimality bound (proof); generated experiment figure: expansions of Dijkstra vs A* variants on random grids; full section on space-time A*: state (v,t), wait action, vertex/edge constraints, goal handling, reservation tables, pseudocode, mini-example with one constraint forcing a wait; implementation notes; pitfalls; application box; 8–10 exercises incl. the Week-1 coding exercise.
Code: Overleaf/code/ch04_astar.py: astar for graphs and grids, heuristics, weighted A*, space_time_astar(...) with constraints; self-test vs an internal Dijkstra, constrained search waits when required, reproduces worked-example numbers. Script Overleaf/code/figures/gen_ch04_expansions.py -> .dat.
Cite: hart1968formal, pearl1984heuristics, russell2020aima, pohl1970heuristic, silver2005cooperative.
```

## Templates by chapter kind

* **Algorithm chapter** (the default): motivation → idea → problem statement and notation →
  the algorithm (pseudocode, walkthrough) → worked example (figure, trace table) →
  properties (theorems with proofs) → variants → implementation notes and listing →
  pitfalls → application box → summary → further reading → exercises.
* **Concept/toolbox chapter:** definitions and facts the later chapters rely on, each with
  a small example and a pointer to where it is used; fewer theorems, more tables.
* **System chapter** (how the pieces fit): architecture figure, interfaces between
  components, decision logic as pseudocode or a state machine, what guarantees survive the
  combination, research directions.
* **Evaluation chapter:** experiment matrix, metric definitions with formulas, scenario
  generation, statistics (confidence intervals, paired tests), reporting, reproducibility,
  a complete mini-study run by the code.
