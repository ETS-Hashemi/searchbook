# Review of Chapter 5 (Incremental Search: LPA* and D* Lite) - round 2

Reviewed artefacts: `Overleaf/chapters/ch05-lpastar-dstarlite.tex` (1503 lines),
`Overleaf/figures/ch05/{idea,consistency,lpastar-example,dstarlite-example,replanning-experiment,drone-replanning}.tex`,
`Overleaf/code/ch05_dstar_lite.py`, `Overleaf/code/figures/gen_ch05_examples.py`,
`Overleaf/code/figures/gen_ch05_replanning.py`, `Overleaf/figures/data/ch05-replanning.dat`,
`Overleaf/appendices/solutions/ch05-solutions.tex`, `Overleaf/appendices/glossary/ch05-terms.tex`,
`Overleaf/references.bib`, `Overleaf/bib/ch05-extra.bib`, `Overleaf/frontmatter/notation.tex`,
`Overleaf/chapters/ch04-astar.tex` (notation and tie-breaking), against `STYLE_GUIDE.md` section 9
(A-H), `docs/specs/ch05.md`, `docs/core-idea.txt` (Week 2), and `reviews/ch05-round1.md`
including the reviser's response.

Checks performed in this round.

* **Build.** `cd Overleaf && ./build.sh ch05-lpastar-dstarlite` exits 0. No `!` errors, no
  undefined reference or citation belonging to Chapter 5 (the only `??` are `ch:ch11`,
  `ch:ch13`, `ch:ch14`, `ch:ch19`, `ch:ch20`, `ch:ch21`, i.e. chapters not built in the
  single-chapter run). The one overfull box (29.1 pt) is a line of the global *List of
  Algorithms* belonging to Chapter 16, not to this chapter. **Length: PDF pages 21-44 of
  `build/only-ch05-lpastar-dstarlite.pdf`, i.e. 24 chapter pages**, exactly at the 24-page
  ceiling (the spec asks for 16-18; see required change 1 and the trim list in the
  Suggestions, which must be applied together so the fix does not push the chapter over).
* **Code.** `python3 code/ch05_dstar_lite.py` -> `self-test passed in 1.2 s`.
* **Numbers.** I re-ran `lpastar_example`, `dstar_lite_example`, `gen_ch05_examples.idea_scenario`
  and all ten seeds of `gen_ch05_replanning.run`, and compared every number in the text with the
  output. Tables 5.1, 5.2, 5.5 and 5.6 are byte-identical with the rows emitted by `latex_trace`
  (5 / 13 / 10 / 12 expansions, A* 7 and 12, `k(S)=[7;7]`, `k_m=2`, `g(3,3)=4`, 3 updated
  vertices, costs 4->6 and 7->7, `t=9`). The idea figure reproduces 52 / 26 / 6 with exactly four
  distinct expanded cells, the blocked cell among them. Every experiment number is reproduced:
  1285.1 / 278.6 / 1246.7 expansions and 32.3 / 1.26 ms at event 0, 1031 vs 14 165.8 expansions
  and 32.9 vs 59.7 ms over events 1-40 (ratios 13.7 and 1.82), cumulative 65.2 vs 61.0 ms,
  crossover in cumulative expansions at event 4, mean repair 0.822 vs 1.493 ms, 7 slower events
  with 5.187 vs 1.645 ms, 28.2 vs 4.2 us per expansion, 203 on-path events (mean 49.3, median 4,
  max 1704) and 197 off-path events (mean 1.5, 68 % zeros), factor 1285/279 = 4.61.
* **Canonical sources.** Both pseudocodes were compared line by line with Koenig, Likhachev and
  Furcy (AIJ 2004) and Koenig and Likhachev (AAAI 2002): key with `k_m`, the `k_old <
  CalculateKey(u)` reinsert test, `g(u) <- inf` with `Pred(u) u {u}`, `UpdateVertex` on the tail
  of a changed edge, `k_m += h(s_last,s_start)` once per batch before the edge updates, and
  `s_last <- s_start` in the same branch: all correct (but see required change 2 on how the
  version is described). I re-derived Proposition 5.4, both proof sketches, the key-order
  argument, the `O(|E|(Delta+log|V|))` bound, the `k_m` lower-bound argument and Table 5.4 by
  hand; all are correct. I also re-derived the seven-expansion counterexample in the solution of
  `exr:ch05-secondkey` step by step - it is right, including the six-expansion two-component run.
* **Bibliography.** All ten keys resolve; authors, venue, volume and pages of
  `koenig2002dstarlite` (AAAI 2002, 476-483), `koenig2004lpa` (AIJ 155(1-2):93-146),
  `koenig2005fast` (T-RO 21(3):354-363), `stentz1994optimal` (ICRA 1994, 3310-3317),
  `stentz1995focussed` (IJCAI 1995, 1652-1659), `likhachev2005anytime` (ICAPS 2005, 262-271),
  `ferguson2006field` (JFR 23(2):79-101) and `sun2010moving` (AAMAS 2010) are all ones I can
  vouch for. No fabricated reference. 24 distinct `\index` entries, well above the minimum.
* **Spec and Week-2 plan.** Every "must cover" item of `docs/specs/ch05.md` is present
  (wasted-work figure, g/rhs and the three consistency states, two-component key, LPA*
  pseudocode + worked example + trace, reversed search, numeric `k_m` illustration, full D* Lite
  pseudocode, three-panel worked example, properties with assumptions, generated 50x50
  experiment, four implementation notes, five pitfalls, four variants, drone box, 8 exercises
  with the Week-2 coding exercise, a hand trace and the `k_m` proof).

**Round-1 follow-up: all six required changes of round 1 are resolved, and none is re-raised.**

1. (A) `sec:ch05-properties` now reads `O(|E|(\Delta+\log|V|))` with the 4-connected
   specialisation and the sentence explaining the extra factor `Delta`. Correct.
2. (A) `def:ch05-problem` now carries the labelled **moving-start** clause and the road-map
   sentence with `\cref` to the four sections. Correct.
3. (A) The LPA* walkthrough now says "may be expanded a second time later ... if the loop ever
   reaches its new, larger key", with the pointer to step 10 of `tab:ch05-dstarlite-repair`.
   I re-checked that step: `(1,3)` is retracted and never re-expanded. Correct.
4. (D) `figures/ch05/drone-replanning.tex`: tube base at `y=1.2`, intruder at `(9.5,1.5)`, arrow
   from `(9.5,1.5)`. I traced the blue route cell by cell - `(8,2),(8,1),(8,0),(9,0),(10,0),
   (10,1),(10,2),...` - none of them is hatched and none is inside the polygon; the caption
   sentence about slipping below the region is there. Correct.
5. (D) `figures/ch05/idea.tex` line 99 now draws `\draw[sbOrange,line width=1.2pt] (6,6)
   rectangle ++(1,1);` after the obstacle fill, and the generator asserts the blocked cell is one
   of the expansions (it is). Caption extended. Correct.
6. (E) `appendices/solutions/ch05-solutions.tex` now has eight solution blocks for eight
   exercises, including `exr:ch05-threshold`. Correct.

The applied suggestions (strict key order in `def:ch05-key`, the machine-dependence sentence in
`sec:ch05-experiment`, the corrected "either makes it consistent or ..." in `sec:ch05-intuition`,
the `Memory` paragraph, the shortened `tab:ch05-km` caption) are all in place.

## Verdict

**Minor revision.** The chapter is technically correct, complete against the spec and the Week-2
plan, and every number in it is reproduced by the committed code. There is no remaining defect in
categories A-E. Two required changes remain, both local: a float pile-up that prints both
pseudocodes five to six pages after the walkthroughs that dissect them line by line, and one
sentence that mis-describes which version of D* Lite is printed.

## Required changes

1. **Location:** `sec:ch05-lpastar` / `sec:ch05-dstarlite`; the float environments at
   lines 289 (`\begin{algorithm}[htb]`, `alg:ch05-lpastar`), 442, 496, 576, 647
   (`\begin{table}[tb]`), 686 (`\begin{algorithm}[!htbp]`, `alg:ch05-dstarlite`) and 815, 835
   (`\begin{table}[htbp]`).
   **Problem:** the floats of Sections 5.4-5.7 pile up and are printed far behind the text that
   uses them. In the current PDF, Section 5.4 and its line-by-line walkthrough are on PDF pages
   25-26 (printed 91-92) but **Algorithm 5.1 is typeset on PDF page 31 (printed 97)**; the
   walkthrough tells the reader "line 6 ... line 9 ... lines 10-11 ... line 13 ... line 20" for a
   listing that is six pages further on, inside the D* Lite worked example. The same happens to
   the main algorithm: the pseudocode walkthrough of Section 5.6.3 is on PDF pages 28-29
   (printed 94-95), **Algorithm 5.2 is typeset on PDF page 33 (printed 99)**, i.e. after the
   worked example that traces it. Table 5.1 (discussed p. 26) lands on p. 31, Table 5.2
   (p. 26-27) on p. 32, Table 5.3 (p. 27) on p. 32, Table 5.4 (p. 28) on p. 32, Tables 5.5 and
   5.6 (p. 29-30) on p. 34; PDF pages 31-34 are four consecutive pages of floats. For a reader
   working alone this is the single biggest obstacle in the chapter.
   **Fix:** the chapter already loads `placeins` (it uses `\FloatBarrier` at line 912). Add three
   more barriers and pin the two algorithms to the top of a page:
   (a) change line 289 to `\begin{algorithm}[!t]` and line 686 to `\begin{algorithm}[!t]`;
   (b) insert `\FloatBarrier` immediately before `\section{A worked example: \lpastar repairs a
   path}` (line 405), before `\section{The algorithm: \dstarlite}` (line 532), and before
   `\section[A worked example: \dstarlite repairs a plan]{...}` (line 787).
   After that, Algorithm 5.1 must appear inside Section 5.4, Tables 5.1-5.2 inside Section 5.5,
   and Algorithm 5.2 with Tables 5.3-5.4 no later than the end of Section 5.6. Re-run
   `./build.sh ch05-lpastar-dstarlite` and check the new page map. Barriers cost white space, so
   apply the three trims of Suggestions 4-6 in the same pass and confirm the chapter still ends
   within 24 pages; if one page is still missing, move `tab:ch05-directions` (the mirror table,
   line 576) to the end of Section 5.6.1 with `[!b]`, or shorten Listing 5.1 as proposed.
   **Category:** G (float placement), with a direct effect on C.

2. **Location:** `sec:ch05-dstarlite-pseudocode`, first sentence: "\Cref{alg:ch05-dstarlite} is
   the final, optimised version of \dstarlite as published by Koenig and Likhachev
   \cite{koenig2002dstarlite}."
   **Problem:** the algorithm printed is the paper's *final version* (the one that introduces
   `k_m`), not its *optimised version*. The optimised variant in the same paper differs in
   exactly the place the chapter later reasons about: it maintains `rhs` incrementally in the
   overconsistent branch (`rhs(s) <- min(rhs(s), c(s,u)+g(u))` for each predecessor), recomputes
   the full minimum in the underconsistent branch only for predecessors whose `rhs` was derived
   from the retracted `g`-value, and updates a queue entry in place instead of Remove+Insert. A
   reader who follows the sentence to the paper's optimised figure will find pseudocode that does
   not match Algorithm 5.2 line by line, and will also conclude that the published algorithm
   carries the factor `Delta` that `sec:ch05-properties` attributes to "recomputing an rhs-value
   as a minimum over all successors" - which is precisely what the optimised version avoids in
   the common case.
   **Fix:** replace the phrase "the final, optimised version" by "the final version (the one with
   the key modifier)" and add one sentence at the end of that paragraph, e.g.: "The paper also
   gives an optimised variant that computes the same values with the same expansions but
   maintains $\rhs$ incrementally instead of recomputing the minimum over all successors on every
   \DslUpdateVertex; it removes the factor $\Delta$ of \cref{sec:ch05-properties} from the
   overconsistent case and is what a production implementation should use." (Optionally add the
   same one-clause remark to the complexity paragraph in `sec:ch05-properties`.)
   **Category:** H (attribution to the cited source), with an A-flavoured consequence for the
   complexity discussion.

## Suggestions

1. **`fig:ch05-dstarlite-example` shows only `g`-values.** `dsl_labels` in
   `code/figures/gen_ch05_examples.py` prints `g` alone, while `fig:ch05-lpastar-example` prints
   `g/rhs`. In the middle panel the two orange cells `(3,3)` and `(2,3)` therefore carry the
   numbers 4 and 5 with no visible reason for being inconsistent, although the whole chapter
   turns on the gap between `g` and `rhs`. Printing `g/rhs` for at least the three changed cells
   (or for all cells of the middle panel) would make the panel self-explanatory and the two
   worked-example figures consistent with each other.
2. **Priority-queue cost in `sec:ch05-implementation`.** "the heap holds at most one live entry
   per vertex, and all operations stay $\bigO{\log|U|}$ amortised" understates the heap: with
   lazy deletion the *stale* entries are only discarded when they surface at the top, so the heap
   can hold many entries per vertex and its size is bounded by the number of insertions since the
   last purge, not by `|U|`. Suggest "all operations stay $\bigO{\log m}$ amortised, where `m` is
   the number of entries currently in the heap; stale entries are only discarded when they reach
   the top, so on a long mission it is worth rebuilding the heap from `key_of` occasionally" -
   and one clause in the `Memory` paragraph that the queue, unlike the two arrays, is not
   `O(|V|)`.
3. **Notation table.** `frontmatter/notation.tex` line 84 advertises `\key(s)` for this chapter,
   while the chapter writes `k(s)`, `k_1`, `k_2`. Round 1 raised this and the reviser deferred it
   to the consistency pass, which is reasonable; a one-clause in-chapter remedy is available in
   the meantime: in `def:ch05-key` write "the **key** (written $\key(s)$ in the notation table)".
   Still flag `s_start`, `s_goal`, `s_last` for the front-matter pass.
4. **Trim (needed if change 1 costs a page): Listing 5.1.** `lst:ch05-queue` (lines 1178-1218) is
   40 lines for a standard lazy-deletion heap and repeats its own six-line docstring in the prose
   above it. Dropping the docstring, `__contains__` and `__len__` saves about a third of a page
   without losing anything the text needs.
5. **Trim: the duplicated ratio in `sec:ch05-experiment`.** "in wall-clock time the ratio was
   only about $1.8$ ($60$~ms against $33$~ms)" and "its repairs are on average nearly twice as
   fast as a fresh \astar ($0.8$~ms against $1.5$~ms)" are the same measurement (1.82) stated
   twice, three sentences apart. Keep the second (it carries the per-event meaning) and shorten
   the first to the totals.
6. **Trim: the last paragraph of `sec:ch05-lpastar-example`** ("The path is read off at the end
   ... the tie-break selects this one") repeats the extraction rule already stated in
   `thm:ch05-consistent-correct` and shown in the right panel of the figure; two sentences suffice.
7. **A second difficulty-1 exercise.** Round 1's proposal was rightly rejected as a lookup. A
   conceptual on-ramp that is not a lookup: "In \cref{ex:ch05-dstarlite} the robot walks from
   $(0,3)$ to $(2,3)$ and $k_m$ stays $0$. Explain why no key in $U$ has to be touched during
   those two steps, and why line~\ref{alg:ch05-dstarlite:km} then adds $2$ in one lump instead of
   $1+1$." (Answer: keys are only ever compared inside `ComputeShortestPath`, which is not called
   while nothing changes; `s_last` remembers the position at which the stored keys were valid.)
8. **Pitfall "Wrong heuristic direction".** "The search then still terminates and often still
   finds a path" understates the damage; say explicitly that the path it returns may be *longer
   than the shortest one*, because the loop test is no longer backed by a lower bound.
9. **`sec:ch05-km`, last sentence of the paragraph before Table 5.4.** "adding the same constant
   to all new keys changes no comparison among them" is loose: it is the comparison among
   *current* keys that is unaffected, while stored keys become lower bounds - which the next
   sentence already says. Consider "adding the same constant to every key computed from now on
   leaves every comparison among current keys unchanged".

## What must be kept

Keep the chapter's honesty about its own algorithm; it is still its best feature and it is rare.
The LPA* worked example ends with the repair costing **13** expansions against A*'s **7** and
then explains exactly why (two retractions plus the band effect of the second key component);
`sec:ch05-experiment` reports that in wall-clock time the incremental planner has *not* repaid
its first search after 40 events (65 ms against 61 ms) and that 7 of the 40 repairs were slower
than a fresh A*. Keep the dotted third curve of `fig:ch05-experiment` (A* with D* Lite's own
tie-breaking), which turns an unexplained factor of 4.6 into an explained one, and the
"Replanning can be slower than A*" pitfall that draws the moral.

Keep `tab:ch05-directions`, the nine-row LPA*/D* Lite mirror table that makes `exr:ch05-directions`
work; the "Why the two-component key works" argument (`k_2(w)=g(u)+c(u,w)>g(u)=k_2(u)`), the
cleanest short justification of the second key component I know; the numeric `k_m` table with its
companion proof exercise `exr:ch05-kmproof`; and all five pitfalls, in particular "Blocking a cell
changes all of its edges, in both directions", which diagnoses both halves of the mistake and
explains why the bug stays hidden until the obstacle disappears again. Keep the trace tables
exactly as they are - they are emitted verbatim by `latex_trace` in `code/ch05_dstar_lite.py`, so
they cannot drift from the code - and keep the self-test that checks D* Lite against A* after
every change, including the assertion that the first search expands exactly as many vertices as
A* with the same tie-breaking.

Keep the solutions file as written. The solution of `exr:ch05-secondkey` is a fully worked
four-vertex counterexample in which `k_1`-only comparison expands one vertex three times and can
even terminate with the wrong cost; I re-derived all seven expansions and they are correct. Keep
the `exr:ch05-threshold` solution's insistence that the crossover in time comes long before the
crossover in expansions. Finally keep the drone box's precise reading of "edge costs change" as
the rasterised, inflated prediction tube, and `exr:ch05-intruder`, which is the bridge from this
chapter to `ch:ch20` and `ch:ch24`.

## Response to review (round 2)

Both required changes are applied, together with all nine suggestions. Nothing the
"What must be kept" list names was removed: the 13-against-7 expansion count and its
two-retraction/band explanation, the 65~ms-against-61~ms honesty of
`sec:ch05-experiment` with its 7-of-40 slower repairs, the dotted third curve of
`fig:ch05-experiment`, all five pitfalls, `tab:ch05-directions`, the two-component-key
argument, the numeric $k_m$ table, the code-generated trace tables, the self-test and the
solutions file are all untouched except where a change below says otherwise.

### Required change 1 - float placement (category G)

Applied exactly as specified, plus the three trims of Suggestions 4-6 in the same pass.

* `\begin{algorithm}[htb]` (Algorithm 5.1) and `\begin{algorithm}[!htbp]` (Algorithm 5.2)
  are now `\begin{algorithm}[!t]`.
* `\FloatBarrier` inserted immediately before `\section{A worked example: \lpastar repairs
  a path}`, before `\section{The algorithm: \dstarlite}` and before the sectioning command
  of `sec:ch05-dstarlite-example`. (`placeins` is loaded by `searchbook.sty`, line 70.)

New page map of `build/only-ch05-lpastar-dstarlite.pdf` (PDF page numbers; the chapter
still occupies pages 21-44, i.e. **24 pages**, exactly as before):

| Float | was on | is now on | its section |
|---|---|---|---|
| Algorithm 5.1 | 31 | **26** | 5.4 (pp. 25-26) |
| Table 5.1, Table 5.2 | 31, 32 | **28** | 5.5 (pp. 27-28) |
| Table 5.3 (`tab:ch05-directions`) | 32 | **29** | 5.6.1 |
| Table 5.4 (`tab:ch05-km`) | 32 | **30** | 5.6.2 (discussed on the same page) |
| Algorithm 5.2 | 33 | **32** | 5.6.3 (walkthrough on p. 31) |
| Tables 5.5, 5.6 | 34, 34 | **33, 34** | 5.7 |

Every float now prints inside the section that discusses it, and the block of four
consecutive float-only pages (old 31-34) is gone. The line-by-line walkthrough of
Algorithm 5.1 and the listing itself are on facing pages, as are the D* Lite walkthrough
(p. 31) and Algorithm 5.2 (p. 32). Because the barriers were paid for by the three trims,
`tab:ch05-directions` did not have to be moved and Listing 5.1 did not have to be cut
further than Suggestion 4 asks.

### Required change 2 - which version of D* Lite is printed (category H)

`sec:ch05-dstarlite-pseudocode` now opens with "\Cref{alg:ch05-dstarlite} is the final
version of \dstarlite (the one with the key modifier) as published by Koenig and
Likhachev", and the paragraph ends with a new sentence that describes the optimised
variant precisely as the review does: same values and same expansions, but $\rhs$
maintained incrementally ($\rhs(s)\gets\min(\rhs(s),c(s,u)+\gcost(u))$ per predecessor in
the overconsistent branch), the full minimum recomputed in the underconsistent branch only
for predecessors whose $\rhs$ came from the retracted $\gcost$-value, and queue entries
updated in place instead of Remove+Insert; it notes that this removes the factor $\Delta$
of `sec:ch05-properties` in the overconsistent case and is what a production implementation
should use, and says why the plain version is the one printed. The optional one-clause
remark was added to the complexity paragraph of `sec:ch05-properties` as well, so the
$\Delta$ discussion no longer reads as a property of the published algorithm.

### Suggestions

1. **`fig:ch05-dstarlite-example` shows only g-values.** `dsl_labels` in
   `code/figures/gen_ch05_examples.py` now follows the same rule as `lpa_labels`: a cell
   is labelled `g` when it is locally consistent and `g/rhs` when it is not, and is left
   blank only when both values are $\infty$. The middle panel now shows $4/\infty$ at
   $(3,3)$ and $\infty/8$ at $(2,3)$ (the retracted cell and the cell that lost its
   successor), so the orange colouring has a visible reason. Figure regenerated; the
   caption now says "written $\gcost/\rhs$ for the cells where the two disagree, as in
   \cref{fig:ch05-lpastar-example}".
2. **Heap complexity.** The priority-queue paragraph of `sec:ch05-implementation` now says
   that stale entries are only discarded when they surface, that the heap therefore grows
   with the number of insertions rather than with $|U|$, that every operation costs
   $\bigO{\log m}$ with $m$ the current heap size, and that the heap should be rebuilt from
   `key_of` when $m$ grows past a few times $|U|$. The Memory paragraph gained a clause
   saying the queue, unlike the two arrays, is not $\bigO{|V|}$.
3. **`\key` in the notation table.** `def:ch05-key` now reads "The **key** (written
   $\key(s)$ in the notation table) of a vertex $s$". `s_start`, `s_goal`, `s_last` remain
   flagged for the front-matter consistency pass; the front matter was not edited.
4. **Trim Listing 5.1.** The six-line docstring and `__len__` are gone (the class in
   `code/ch05_dstar_lite.py` keeps both; the listing is an excerpt). `__contains__` was
   kept, with a one-line comment, because the pseudocode tests $u \in U$ explicitly and
   dropping it would leave that line of Algorithm 5.1 unimplemented in print.
5. **Trim the duplicated ratio.** The first mention is now totals only ("the same repairs
   took 60 ms and 33 ms of wall-clock time, a much smaller gap"); the per-event sentence
   with 0.8 ms against 1.5 ms is unchanged.
6. **Trim the last paragraph of `sec:ch05-lpastar-example`.** Reduced to two sentences that
   point at `thm:ch05-consistent-correct` instead of restating the extraction rule.
7. **A second difficulty-1 exercise.** Added as `exr:ch05-nomove`, with the review's
   wording, immediately after `exr:ch05-states`, plus a worked solution in
   `appendices/solutions/ch05-solutions.tex` (keys are only compared inside
   `ComputeShortestPath`, which is not called while nothing changes; `s_last` records the
   position at which the stored keys were computed, so the increment is one lump).
8. **Pitfall "Wrong heuristic direction".** Now states that the returned path may be
   *longer than the shortest one*, and why: the loop test compares `TopKey` with
   $k(s_{\mathrm{start}})$, and that comparison only proves nothing cheaper is left while
   $k_1$ is a lower bound.
9. **`sec:ch05-km` wording.** Now "adding the same constant to every key computed from now
   on leaves every comparison among current keys unchanged".

### Verification

* `python3 code/ch05_dstar_lite.py` -> "self-test passed" (D* Lite against A* after every
  change, including the equal-expansion assertion for the first search).
* `python3 code/figures/gen_ch05_examples.py` regenerates all three example figures;
  `figures/data/ch05-replanning.dat` is unchanged because `gen_ch05_replanning.py` was not
  touched, so every number quoted in `sec:ch05-experiment` still matches the code.
* `./build.sh ch05-lpastar-dstarlite`: no LaTeX errors, no new overfull boxes; the only
  remaining warnings are the expected undefined references to other chapters in a
  single-chapter build. Note that latexmk can exit non-zero on this machine when another
  session rebuilds a different chapter at the same time: `\includeonly` re-reads the other
  chapters' `.aux` files, their part-page numbers then change between passes, and latexmk
  reports "needed too many passes". The chapter's own aux entries are stable across passes.
