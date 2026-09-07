# Review of Chapter 3 (Dijkstra's Algorithm) - round 1

## Verdict

**Minor revision.**

This is a strong, careful chapter. It covers every "must cover" item of `docs/specs/ch03.md`
and the Dijkstra half of Week 1 of the training plan, its mathematics is correct, and - unusually
- *every* number quoted in the text is reproduced by `code/ch03_dijkstra.py`. What I verified:

* **Build.** `./build.sh ch03-dijkstra` failed in the shared `Overleaf/build/` directory, but the
  failure is *not* this chapter's: pdflatex aborted on a half-written `build/chapters/ch20-trajectory-prediction.aux`
  (`ch20-...aux:37: Undefined control sequence. l.37 \newlabe`) left behind by a concurrent build,
  which stopped latexmk after one pass and left every `\cref` as `??`. Re-running the identical
  build into a private output directory gives **status 0, no `!` errors, no undefined ch03 label
  or citation, no overfull box wider than 15 pt**. Nothing to fix in the chapter here (see
  Suggestion 8).
* **Length.** Chapter body = **19 pages** (pp. 45-61 of the book build; pp. 12-30 of the
  single-chapter PDF). Inside the 20-page ceiling, but above the style guide's 12-18 and the
  spec's 12-14; the only genuine repetition is named in Required change 4.
* **Code.** `python3 code/ch03_dijkstra.py` -> `all self-tests passed (0.04 s)`. I re-ran the
  chapter's claims independently: trace table (12 pops / 7 settles / 5 stale / max heap size 4),
  `dist['F'] == 12` at the early exit vs. the true 11, distances `A0 B2 C3 D5 E8 G10 F11`, path
  `A,B,C,D,E,G,F`, the negative example (Dijkstra 2, Bellman-Ford 1, `delta(S,A)=0`), the grid run
  (23 free cells, 19 expansions, 0 stale, `g(T)=8`, open tentative values 9/9/10 for (2,3)/(3,2)/(3,3),
  (3,4) never discovered, `h*(3,3)=2` vs. 4 for a forward run from `T`, and exactly the nine path
  cells with `g+h*=8`), and the 8-connected variant of Exercise 3.5 (`delta(S,T)=6+sqrt2 = 7.4142`,
  24 pops, 5 stale - so the exercise's premise holds). Every figure number in
  `figures/data/ch03-expansions.dat` matches the text (7437.7 -> "7,438", 7498.5 -> "7,499",
  7436.6 -> "7,437", 165.489 -> "165.5", 85.252 -> "85.3", 3020.4 -> "3,020" = 41 % of 7437.7),
  and the generator really uses 10 seeded instances at 25 % density, 8-connected, source top-left.
* **Citations.** All seven keys resolve (`dijkstra1959note`, `cormen2009clrs`, `russell2020aima`,
  `hart1968formal`, `pearl1984heuristics` in `references.bib`; `fredman1987fibonacci`,
  `felner2011position` in `bib/ch03-extra.bib`) and I can vouch for the details of all seven
  (Dijkstra, Numer. Math. 1:269-271, 1959; CLRS 3rd ed.; AIMA 4th ed.; Hart-Nilsson-Raphael,
  IEEE TSSC 4(2):100-107, 1968; Pearl 1984; Fredman & Tarjan, JACM 34(3):596-615, 1987;
  Felner, SoCS 2011). No fabricated reference.
* **Counts.** 6 figures (all `\cref`-referenced, generated ones committed with their generators),
  2 tables, 2 algorithms, 2 listings (30 and 27 lines, both byte-for-byte identical to the
  source file), 3 pitfall boxes, 40 index entries, 8 exercises graded 1,1,2,2,2,2,3,3 with the
  Week-1 coding exercise present, glossary (`appendices/glossary/ch03-terms.tex`) and four
  solutions (`appendices/solutions/ch03-solutions.tex`, whose numbers I re-derived and confirmed).

The four required changes below are all local: two are one-to-three-line repairs of formal
statements (A), one is a cross-reference to material that does not exist in Chapter 2 (F), and one
is a concrete de-duplication (G). Nothing in B, C, D, E is missing.

## Required changes

1. **Corollary 3.8 (`cor:ch03-ucs`), proof, `chapters/ch03-dijkstra.tex` lines 490-503.**
   *Problem (category A).* The corollary asserts two things, and the proof proves only the first:
   "The second claim and the remaining details are `\cref{exr:ch03-monotone}`" hands the proof of
   "it settles every vertex with `\delta(s,v)<\delta(s,t)`" to Exercise 3.3, which has no solution
   in `appendices/solutions/ch03-solutions.tex`. A numbered result must carry its own proof or a
   citation; and this claim is used later (Section 3.6, "Expansions in practice", and the reading
   of `\cref{fig:ch03-expansions}`).
   *Fix.* Add three lines to the proof before the deferral, e.g.: "For the second claim, suppose
   `\delta(s,v)<\delta(s,t)` and `v` is not settled at the moment `t` is popped. Take a shortest
   path from `s` to `v` and let `y` be its first unsettled vertex (it exists, since `s` is settled);
   as in step (ii) of the proof of `\cref{thm:ch03-invariant}` the heap holds the entry
   `(\delta(s,y),y)` with `\delta(s,y)\le\delta(s,v)<\delta(s,t)=\gcost(t)`, contradicting that
   `(\gcost(t),t)` was the minimum." Keep Exercise 3.3 as practice, but reduce its deferral to the
   tie-case and the zero-cost part ("which vertices with `\delta(s,v)=\delta(s,t)` are settled
   depends only on tie-breaking").

2. **Theorem 3.11 (`thm:ch03-true-distance`), item 1 "Exactness", lines 709-712.**
   *Problem (category A).* The equivalence "a vertex `v` lies on some shortest path from `s` to `t`
   if and only if `\delta(s,v)+\hcost^*(v)=\delta(s,t)`" is false when `t` is not reachable from `s`:
   then `\delta(s,t)=\infty` and every `v` with `\delta(s,v)=\infty` satisfies the equation
   (`\infty=\infty`) although no `s`-`t` path exists at all. The proof of the converse silently
   assumes the two halves are finite paths.
   *Fix.* State the hypothesis: "Assume `\delta(s,t)<\infty`. Then a vertex `v` lies on some shortest
   path from `s` to `t` if and only if `\delta(s,v)+\hcost^*(v)=\delta(s,t)` (both terms are then
   finite)." Add "both summands are finite, since their sum is" to the converse direction of the
   proof of (1).

3. **Section 3.3 (`sec:ch03-problem`), last paragraph, lines 176-178:** "The open vertices form the
   priority queue `\Open` and the settled vertices the set `\Closed`, exactly as in the best-first
   skeleton of `\cref{ch:ch02}`."
   *Problem (category F).* Chapter 2 contains no "best-first skeleton": the string "best-first" does
   not occur in `chapters/ch02-toolbox.tex`, and that chapter never uses `\Open` or `\Closed`
   (0 occurrences of either macro). A reader sent back to Chapter 2 for the skeleton will not find
   it, and the two chapters then look inconsistent.
   *Fix.* Introduce the two sets here and point at what Chapter 2 actually supplies: "...form the
   priority queue `\Open` and the settled vertices the set `\Closed`. Both are new here; from
   `\cref{ch:ch02}` we reuse only the implicit successor interface `\Succ` and the lazy-deletion
   queue `\code{LazyPQ}` (`\cref{alg:ch02-lazypq}`, `\cref{lst:ch02-lazypq}`)." Make the same repair
   in Section 3.4 ("This is the lazy deletion idiom of `\cref{ch:ch02}`" -> add
   `\cref{alg:ch02-lazypq}`) and in the "Costs and parents"/"The heap" paragraphs of Section 3.8,
   which already refer to `\code{LazyPQ}` correctly.

4. **`dronebox`, Section 3.9 (lines 955-975) against Section 3.1 (lines 41-56).**
   *Problem (category G).* The drone box restates, almost verbatim, the two roles already developed
   in the motivation: "As the *baseline planner* it routes a single drone across a static occupancy
   grid ... the experiments of `\cref{ch:ch25}` report path lengths relative to it. As the
   *heuristic factory* it runs backwards from every drone's goal once ..." duplicates items 1 and 2
   of the numbered list in Section 3.1 ("*It is the baseline planner.* ... the optimum comes from
   this chapter." / "*It is the heuristic factory.* ..."), and Summary bullet 5 states the same
   again. This is the one place where the chapter's 19 pages are padding rather than content.
   *Fix.* Cut the two restatements from the drone box (about a third of a page) and keep only what
   is new there: the placement in the global planning layer of `\cref{ch:ch24}`, the cross-reference
   back to `\cref{sec:ch03-motivation}` for the two roles, what the algorithm does *not* do (no other
   drones, no intruders), the `\dstarlite` link, and the Week-1 pointer to `\cref{ch:appA}`. Do not
   touch Section 3.1, the proofs, the examples or the exercises: with this cut the chapter lands at
   about 18 pages, inside the style guide's range.

## Suggestions

1. *Spec-named pitfalls.* The spec asks for pitfalls on "decrease-key vs lazy insertion" and "float
   equality". Both topics are covered, but only inside ordinary paragraphs ("The heap",
   "Floating-point costs", Section 3.8). Promoting the float-equality paragraph to a fourth
   `pitfall` box would cost two lines and match the spec's wording; the decrease-key warning can
   stay where it is.
2. *Multi-source example, line 646.* "Started from all obstacle cells of a grid with unit costs, the
   run labels every free cell with its distance to the nearest obstacle" is at odds with Chapter 2's
   grid graph, whose vertices are the **free** cells only (`chapters/ch02-toolbox.tex`, line 100).
   Either say "on the grid graph that keeps blocked cells as vertices" or start the wave from the
   free cells that touch an obstacle, with key 0.
3. *Bidirectional stopping rule, Section 3.7.3 (lines 765-780).* The sketch ("a path cheaper than
   `\mu` would have to pass through a vertex still open on the forward side and later through one
   still open on the backward side") skips the case in which the forward-open vertex comes *after*
   the backward-open vertex on the path - exactly the case that the clause "including edges to
   vertices that either side has settled" rules out (that edge would already have been scanned and
   would have set `\mu` to the path's cost). One sentence naming this case would make the sketch
   honest and would tell the reader of Exercise 3.8(b) what the crux is.
4. *Degenerate side in `\cref{eq:ch03-bidir-stop}`.* Say that an empty `\Open` counts as
   `\min=\infty`, so the rule also terminates the search correctly when one side exhausts its
   component.
5. *Definition 3.1 vs. Example 3.9.* Definition 3.1 fixes `c:E\to\R_{\ge0}`, so the negative-edge
   graph is formally not a graph of this chapter. Half a sentence in Example 3.9 ("for this example
   only we drop the non-negativity requirement of `\cref{def:ch03-graph}`") removes the friction.
6. *Solutions coverage.* Four of eight exercises have solutions, which is the book's norm, but the
   two exercises that carry proofs used in the running text (Exercise 3.3 for Corollary 3.8, once
   Required change 1 is made only partly, and Exercise 3.8(b) for the bidirectional rule) are among
   the unsolved ones. Consider swapping `exr:ch03-grid8`'s or `exr:ch03-early`'s slot for a short
   hint on `exr:ch03-monotone`.
7. *"It is the oldest algorithm in this book" (line 39).* Breadth-first search, which Section 3.7.4
   presents, is older (Moore 1959, and Zuse 1945). "It is the oldest of the shortest-path algorithms
   in this book" is safe.
8. *Build hygiene (not a chapter defect).* `build.sh` writes into the shared `Overleaf/build/`
   directory, so a build started by another chapter's author can leave a truncated
   `build/chapters/chNN-*.aux` that makes an unrelated single-chapter build fail with unresolved
   `\cref`s. If the reviser sees `??` everywhere, delete the foreign `.aux` files (or build with a
   private `-outdir`) before concluding anything about this chapter.
9. *Notation table (book-level).* `frontmatter/notation.tex` is still the placeholder with two rows.
   Chapter 3 is the first heavy user of `\delta(u,v)`, `c(u,v)`, `\Succ`, `\Open`, `\Closed` and
   `\hcost^*`; list them in the final notation table so the chapter's promise "define every symbol"
   is kept book-wide.
10. *Trace table.* Adding a "settled so far" column to `\cref{tab:ch03-trace}` (or a marginal note
    of the running expansion count) would let a reader check the "twelve pops, seven settles, five
    stale" arithmetic of the "Counting" paragraph at a glance. Optional; the table is already good.

## What must be kept

The wave metaphor is the best thing in the chapter: it is introduced once (the stone in the pond),
made literal by the generated `\cref{fig:ch03-wavefront}` (bands `\lfloor\gcost\rfloor`, the wave
bending around the block and re-centring on the gap behind the wall), and then used consistently as
the explanatory device for the settling order, the early exit, the area argument for bidirectional
search and the expansions plot. Keep it, and keep all six figures - they are stylistically uniform,
generated from the same code as the text, and their captions really do say what to notice.

Keep the proof architecture. Lemma 3.6 -> Theorem 3.7 -> Corollary 3.8 -> Theorem 3.10 is exactly
the right decomposition, the sentence "*This is the only place where `c\ge0` is used*" in step (iii)
is worth its weight in gold, and Example 3.9 then walks the reader through the *same* step failing
on a concrete negative edge (`2\le0`) instead of merely asserting that negative costs break the
algorithm. Keep the pitfall on testing the goal at discovery time (with the `F`: 13 -> 12 -> 11
evidence) and the constant-shift trap; both are the bugs graduate students actually write.

Keep Section 3.7.2 in full. Theorem 3.11 - exactness, consistency, and *admissibility in space-time
under arbitrary constraints* - is the hinge between this chapter and Chapters 4, 8, 9 and the
`\hcost^*` panel of `\cref{fig:ch03-backward-heuristic}` (the green `g+h^*=8` cells being exactly the
optimal path) is the clearest possible preparation for A*. The directed-grid detail (entering a slow
cell costs 3, leaving it costs 1, so `GridGraph.reversed()` is not the same as searching from `T`)
is a genuinely instructive subtlety that most treatments get wrong or omit.

Finally, keep the discipline of the worked examples and the code. The trace table with the heap
after every pop, the stale entries shown as first-class citizens, the settling order of the grid run
printed cell by cell, the `dat`-backed expansions figure, the verbatim listings and the self-test
that checks the chapter's numbers against brute force and against a Bellman-Ford reference are what
make this chapter trustworthy. The exercise set (difficulties 1,1,2,2,2,2,3,3, ending in the Week-1
coding exercise that Chapter 4 continues) is well graded and solvable from the chapter alone.
