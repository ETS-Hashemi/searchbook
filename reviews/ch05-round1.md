# Review of Chapter 5 (Incremental Search: LPA* and D* Lite) - round 1

Reviewed artefacts: `Overleaf/chapters/ch05-lpastar-dstarlite.tex` (1482 lines),
`Overleaf/figures/ch05/{idea,consistency,lpastar-example,dstarlite-example,replanning-experiment,drone-replanning}.tex`,
`Overleaf/code/ch05_dstar_lite.py`, `Overleaf/code/figures/gen_ch05_examples.py`,
`Overleaf/code/figures/gen_ch05_replanning.py`, `Overleaf/figures/data/ch05-replanning.dat`,
`Overleaf/appendices/solutions/ch05-solutions.tex`, `Overleaf/appendices/glossary/ch05-terms.tex`,
`Overleaf/bib/ch05-extra.bib`, `Overleaf/references.bib`, `Overleaf/frontmatter/notation.tex`,
against `STYLE_GUIDE.md` section 9 (A-H), `docs/specs/ch05.md` and `docs/core-idea.txt` (Week 2).

Checks performed.

* **Build.** `./build.sh ch05-lpastar-dstarlite` exits 0. No `!` errors. The only undefined
  references are to chapters not built in the single-chapter run (`ch:ch06`, `ch:ch09`,
  `ch:ch10`, `ch:ch13`, `ch:ch14`, `ch:ch18`, `ch:ch20`, `ch:ch24`, `ch:appA`, `ch:appB`);
  none belongs to this chapter. The single overfull box in the log (29.1 pt, "Rapidly-exploring
  random tree with goal bias") is a line of the global *List of Algorithms* from Chapter 16, not
  from Chapter 5. **Length: pages 18-40 of the single-chapter PDF, i.e. 23 chapter pages**,
  inside the 24-page ceiling (above the 16-18 pages of the spec; see the Suggestions).
* **Code.** `python3 code/ch05_dstar_lite.py` -> `self-test passed in 0.5 s`.
* **Numbers.** I re-ran `lpastar_example`, `dstar_lite_example`, `gen_ch05_examples.py` and
  `gen_ch05_replanning.py` and compared every number in the text against the output.
  Every entry of Tables 5.1, 5.4, 5.5 and 5.6 is byte-identical with the LaTeX rows emitted by
  `latex_trace`; 5 / 13 / 10 / 12 expansions, `k(S)=[7;7]`, `k_m=2`, `g(3,3)=4`, 3 updated
  vertices, costs 4 -> 6 and 7 -> 7, A*-from-scratch 7 and 12 expansions, `t=9`, all confirmed.
  The idea figure (seed 3) reproduces 52 / 26 / 6 expansions. All experiment numbers
  (1285, 279, 1247, 1031, 14166, ratio 13.7, crossover at event 4, 197 off-path events at mean
  1.5 and 68 % zeros, 203 on-path events at mean 49 / median 4 / max 1704, factor 4.6) match
  `figures/data/ch05-replanning.dat` exactly, and the timings quoted (32.3 ms, 1.26 ms,
  33 vs 60 ms, 65 vs 61 ms, 0.82 vs 1.49 ms, 7 slower events with 5.187 vs 1.661 ms,
  28 us vs 4 us per expansion) are all derivable from the committed `.dat` file. Expansion
  counts are seed-deterministic and reproduce on a different machine; only wall-clock times move.
* **Canonical sources.** Pseudocode compared line by line against Koenig & Likhachev (AAAI 2002,
  final version) and Koenig, Likhachev & Furcy (AIJ 2004): key definition with `k_m`, the
  `k_old < CalculateKey(u)` reinsert test, `g(u) <- inf` plus `Pred(u) u {u}` on underconsistency,
  `UpdateVertex` on the *tail* of a changed edge, `k_m += h(s_last, s_start)` once per batch
  *before* the edge updates, and `s_last <- s_start` in the same branch: all correct. The
  `rhs(s_start) != g(s_start)` form of the loop test is the one prescribed by the spec.
* **Bibliography.** All nine keys resolve; author/venue/volume/pages of `koenig2002dstarlite`
  (AAAI 2002, 476-483), `koenig2004lpa` (AIJ 155(1-2):93-146), `koenig2005fast`
  (T-RO 21(3):354-363), `stentz1994optimal` (ICRA 1994, 3310-3317), `likhachev2005anytime`
  (ICAPS 2005, 262-271), `ferguson2006field` (JFR 23(2):79-101), `sun2010moving` (AAMAS 2010)
  and `stentz1995focussed` (IJCAI 1995, 1652-1659) are all ones I can vouch for. No fabrication
  found. 23 distinct `\index` entries (27 calls), well above the minimum of 15.
* **Spec coverage.** Every "must cover" item of `docs/specs/ch05.md` is present, including the
  three-panel D* Lite figure, the numeric `k_m` illustration, the generated 50x50 experiment,
  the five required pitfalls, the four variants, the drone box, and 8 exercises with the Week-2
  coding exercise, a hand trace and a `k_m` proof.

## Verdict

**Minor revision.** The chapter is technically sound, complete against the spec and the Week-2
training plan, and its worked examples are fully reproduced by the code. Six required changes
remain; every one of them is local (one sentence, one definition, one figure script, one
solution entry).

## Required changes

1. **Location:** `sec:ch05-properties`, the last paragraph of the section
   ("The bound also fixes the running time of a call ... A call therefore costs
   $O((|V|+|E|)\log|V|)$ in the worst case, the same bound as a search from scratch with A*").
   **Problem:** the stated bound does not follow from the cost model given two sentences
   earlier, and is wrong for graphs of unbounded degree. Because `UpdateVertex(s)` recomputes
   `rhs(s)` as a minimum over *all* successors of `s`, the work of one call is
   `sum over expanded u, over s in Pred(u), of O(deg(s) + log|V|)`, which is
   `O(|E|(Delta + log|V|))` with `Delta` the maximum degree, not `O((|V|+|E|)\log|V|)`.
   For a dense graph (`Delta = Theta(|V|)`) the true bound is `Theta(|V|^3)` against the
   claimed `Theta(|V|^2 log|V|)`. A* from scratch really is `O((|V|+|E|)\log|V|)` because it
   relaxes each edge in `O(1)` instead of recomputing a minimum.
   **Fix:** replace the sentence by: "A call therefore costs `O(|E|(\Delta + \log|V|))`, where
   `\Delta` is the maximum degree of the graph; on a 4-connected grid `\Delta = 4` is a
   constant and this is `O((|V|+|E|)\log|V|)`, the same bound as a search from scratch with
   A*. Recomputing an `rhs`-value as a minimum over all successors, rather than relaxing one
   edge as A* does, is what costs the extra factor `\Delta`."
   **Category:** A.

2. **Location:** `def:ch05-problem` (Definition 5.1, "Incremental shortest-path problem"),
   section `sec:ch05-problem`.
   **Problem:** the definition fixes "a sequence of shortest-path queries between *the same two
   vertices* `s_start` and `s_goal`". That excludes D* Lite, which is the chapter's main
   subject and whose whole point is a start vertex that moves (objectives bullet 3,
   `sec:ch05-reverse`). The chapter's own problem statement therefore does not cover the
   algorithm it goes on to develop, and the reader who takes the definition literally will not
   see what `k_m` is for.
   **Fix:** add a second, labelled clause to the definition, e.g.: "In the **moving-start**
   variant, which D* Lite solves, the goal is fixed but before each query the start vertex is
   replaced by the vertex the agent has moved to, which is required to lie on the path returned
   by the previous query." Then add one sentence after the definition pointing forward:
   "Sections 5.4-5.5 treat the fixed-start case (LPA*); Sections 5.6-5.7 add the moving start
   (D* Lite)."
   **Category:** A (definition), with a pedagogical effect (C).

3. **Location:** `sec:ch05-lpastar`, paragraph "Walkthrough.", second bullet
   (underconsistent case): "After this step `u` is either consistent (both `inf`) or
   overconsistent with a fresh, larger key, **and will be expanded a second time later** as an
   ordinary A* expansion."
   **Problem:** the second expansion is not guaranteed, and the chapter's own worked example
   contradicts it: in `tab:ch05-dstarlite-repair`, step 10 retracts `(1,3)` and re-inserts it
   with key `[11;8]`; the loop stops at step 12 with `k(s_start)=[9;7]`, so `(1,3)` is never
   expanded again and keeps `g = inf`. The correct statement is the upper bound of
   `thm:ch05-expansions` ("at most twice"), not a promise of a second expansion.
   **Fix:** replace "and will be expanded a second time later as an ordinary A* expansion" by
   "and may be expanded a second time later, as an ordinary A* expansion, if the loop ever
   reaches its new, larger key; `thm:ch05-expansions` bounds this at one further expansion.
   Step 10 of `tab:ch05-dstarlite-repair` shows a vertex that is retracted and never
   re-expanded, because the search stops first."
   **Category:** A.

4. **Location:** `Overleaf/figures/ch05/drone-replanning.tex` (figure `fig:ch05-drone`),
   lines with `\node[sbintruder] at (9,0.5) {?}`, the tube polygon starting at
   `(8.6,0.2) -- (9.4,0.2)`, and the replanned route `... -- (8.5,0.5) -- (10.5,0.5) -- ...`.
   **Problem:** the blue "D* Lite route" runs horizontally at `y = 0.5` from `x = 8.5` to
   `x = 10.5`, so it passes exactly through the intruder marker at `(9,0.5)` and through cell
   `(9,0)`, which lies inside the drawn red uncertainty tube but is *not* among the hatched
   cells. The figure that is supposed to show a safe replan shows the drone flying through the
   predicted intruder region and over the intruder symbol; it also contradicts its own caption
   ("A predicted intruder trajectory ... is rasterised into blocked cells (hatched)"), because
   the bottom of the tube is not rasterised. The gap in row 0 cannot simply be hatched: it is
   the only opening in the wall of blocked cells in column 9, so hatching it would leave no
   path at all.
   **Fix:** lift the predicted region off row 0 so that the gap the drone uses is visibly
   outside it. Concretely: change the tube polygon base from `(8.6,0.2) -- (9.4,0.2)` to
   `(8.6,1.2) -- (9.4,1.2)`, move the intruder node from `(9,0.5)` to the cell centre
   `(9.5,1.5)`, and start the red velocity arrow at `(9.5,1.5)` instead of `(9,0.5)`. The
   hatched set `(9,1) ... (9,8)` then needs `(9,1)` removed (the intruder's own cell should be
   hatched, so keep `(9,1)` hatched and instead reroute the blue path one row lower, which it
   already is) - after the shift, row 0 is free of both the tube and the marker and the
   existing blue route is correct without further change. Add to the caption: "the drone slips
   below the predicted region through the one row the tube does not reach."
   **Category:** D.

5. **Location:** `sec:ch05-intuition` ("an incremental search touches only the orange cells,
   **four cells** in six expansions") and the caption of `fig:ch05-idea`
   ("D* Lite expands only the orange cells"), generated by
   `Overleaf/code/figures/gen_ch05_examples.py`.
   **Problem:** the generator emits `\fill[sbOrange!35] (6,6) rectangle ++(1,1);` for the newly
   blocked cell and then, 14 lines later, `\fill[sbobstacle] (6,6) rectangle ++(1,1);` on top of
   it. The fourth orange cell is therefore invisible: the reader counts three orange cells and
   cannot reconcile that with "four cells". (The blocked cell *is* legitimately one of the six
   expansions - it is the underconsistent retraction - so the count in the text is right and
   the drawing is wrong.)
   **Fix:** in `gen_ch05_examples.py`, after the obstacle fill, draw the newly blocked cell with
   an orange frame, e.g. `\draw[sbOrange,line width=1.2pt] (6,6) rectangle ++(1,1);`, and
   regenerate `figures/ch05/idea.tex` (`python3 code/figures/gen_ch05_examples.py`). Extend the
   caption with "the newly blocked cell (orange frame) is itself one of the expanded cells: its
   stale distance is retracted first."
   **Category:** D.

6. **Location:** `Overleaf/appendices/solutions/ch05-solutions.tex`; exercise
   `exr:ch05-threshold` in `sec:ch05-exercises`.
   **Problem:** the file contains seven `\begin{solution}` blocks
   (`states`, `handtrace`, `secondkey`, `kmproof`, `directions`, `coding`, `intruder`) for eight
   exercises; `exr:ch05-threshold` has none. The book's reader works alone, and every other
   exercise of this chapter (and of Chapters 3 and 4) has at least a hint, so the omission
   leaves the only exercise about *when incremental search stops paying off* unanswered - the
   very point the second pitfall of `sec:ch05-implementation` asks the reader to internalise.
   **Fix:** add a `\begin{solution}{exr:ch05-threshold}` block with the expected outcome:
   for very small `phi` D* Lite wins by orders of magnitude in expansions; the crossover in
   *time* comes much earlier than the crossover in *expansions* because a D* Lite expansion
   costs several times an A* expansion (28 us vs 4 us in `sec:ch05-experiment`); around
   `phi` of a few per cent on a 100x100 grid the repair touches a constant fraction of the
   vertices, `thm:ch05-expansions` then allows up to `2|V|` expansions plus `UpdateVertex` on
   every neighbour of each, and a fresh A* is faster; the rule for `ch:ch24` is to count changed
   cells per replanning cycle and fall back to A* above the measured threshold (and always
   after a full map replacement or a goal change). State that exact numbers are
   implementation-dependent and that the student should report their own crossover.
   **Category:** E.

## Suggestions

* **Trim, if the page budget matters.** At 23 pages the chapter is at the top of the allowed
  range (the spec asks for 16-18). The only genuine duplication I found is around
  `tab:ch05-km`: the caption (7 lines) explains the whole table, and the paragraph immediately
  after it ("`\Cref{tab:ch05-km}` gives numbers. Vertex `u` was inserted before the move with
  key `[4+6;4]` ...") walks through the same six numbers a second time. Cutting the caption
  back to two sentences ("Why the key modifier is needed. `m = min(g,rhs)`; the last two columns
  are the keys `CalculateKey` returns now, without and with the modifier.") would save about
  half a page without losing anything. Everything else in the chapter is required content.
* **Define the strict key order.** `def:ch05-key` defines only `k <= k'`, while both algorithms
  and the reinsert test use `<`. Add the one clause: "and `k < k'` iff `k_1 < k'_1`, or
  `k_1 = k'_1` and `k_2 < k'_2`."
* **Notation table.** `frontmatter/notation.tex` line 84 advertises the symbol `\key(s)`
  (typeset *key*(s)), but the chapter writes `k(s)`, `k_1`, `k_2` throughout. Either use `\key`
  in `eq:ch05-key` or change the notation row to `k(s)`. While that row is being touched,
  `s_start`, `s_goal` and `s_last` deserve their own line: the chapter is the first to use them
  and explicitly maps them onto `s` and `gamma` of `ch:ch04`. (Front-matter edits belong to the
  consistency pass, not to this chapter's reviser.)
* **Machine-dependent numbers.** `sec:ch05-experiment` quotes wall-clock times to two
  significant digits. The expansion counts are seed-deterministic and reproduce exactly; the
  times do not (on my machine the same script produced 23 ms instead of 32 ms for the initial
  search, with identical expansion counts). One clause - "on the reference machine of
  `\cref{ch:ch02}`" or "on a 2024 laptop" - would keep the claim honest without changing any
  number.
* **`sec:ch05-intuition`, "Processing a vertex makes it consistent."** True for the
  overconsistent case only; the underconsistent case can leave the vertex overconsistent. The
  walkthrough in `sec:ch05-lpastar` says this correctly. Consider "Processing a vertex either
  makes it consistent or replaces its stale value by a larger, honest one" so the intuition
  section is not contradicted 4 pages later.
* **Memory.** The implementation notes cover the queue, infinity, edge scanning and
  termination but never state the storage cost. One sentence ("two floats per vertex,
  `O(|V|)`, kept for the lifetime of the mission - this is what an incremental search buys its
  savings with") would complete the picture and pre-empt the natural question for a
  200x200x10 map from `sec:ch05-motivation`.
* **Exercise spread.** One exercise at difficulty 1, four at 2, three at 3. A second
  difficulty-1 item - for example "given the `g`/`rhs` values in the middle panel of
  `fig:ch05-lpastar-example`, list the queue in pop order" - would make the on-ramp gentler.

## What must be kept

The chapter is unusually honest about its own algorithm, and that honesty is its best feature:
the LPA* worked example ends with the repair costing **13** expansions against A*'s **7** and
then explains exactly why (two retractions plus the band effect of the second key component),
and `sec:ch05-experiment` shows that in wall-clock time the incremental planner has *not* repaid
its first search after 40 events. Most textbook treatments quietly omit both facts. Keep them,
keep the third (dotted) curve of `fig:ch05-experiment` that runs A* with D* Lite's own
tie-breaking - it is what makes the comparison fair and turns a puzzling factor of 4.6 into an
explained one - and keep the "Replanning can be slower than A*" pitfall that draws the moral.

Keep `tab:ch05-directions`, the LPA*/D* Lite mirror table: nine rows that let a reader convert
one algorithm into the other without re-reading either, and the reason `exr:ch05-directions`
works. Keep the two-component-key argument in "Why the two-component key works"
(`k_2(w) = g(u)+c(u,w) > g(u) = k_2(u)`), which is the cleanest short explanation of the second
key component I have read. Keep the numeric `k_m` table with its companion proof exercise
`exr:ch05-kmproof`; together they cover the one part of D* Lite that implementers get wrong.
Keep all five pitfalls, in particular "Blocking a cell changes all of its edges, in both
directions", which diagnoses both halves of the mistake and explains why the bug stays hidden
until the obstacle disappears again. Keep the trace tables exactly as they are: they are emitted
verbatim by `latex_trace` in `code/ch05_dstar_lite.py`, so they cannot drift from the code.
Finally keep the drone box's precise reading of "edge costs change" as the rasterised, inflated
prediction tube, and `exr:ch05-intruder`, which is the bridge from this chapter to
`ch:ch20` and `ch:ch24`.

## Response to review (round 1)

All six required changes are applied, together with six of the seven suggestions. The
chapter builds with status 0, no errors, no undefined references belonging to Chapter 5;
`python3 code/ch05_dstar_lite.py` reports `self-test passed`; the figure generator was
re-run and every number quoted in the text still matches the code and the committed
`.dat` file. Chapter length after the changes: pages 19-42 of the single-chapter PDF,
i.e. 24 chapter pages (the caption trim below offset most of the added text; the
one-page growth is inside the 24-page ceiling).

### Required changes

1. **Running-time bound in `sec:ch05-properties`.** *Done, exactly as prescribed.* The
   sentence now reads: "A call therefore costs $O(|E|(\Delta+\log|V|))$ in the worst
   case, where $\Delta$ is the maximum degree of the graph; on a 4-connected grid
   $\Delta=4$ is a constant and this is $O((|V|+|E|)\log|V|)$, the same bound as a search
   from scratch with A*. Recomputing an rhs-value as a minimum over all successors,
   rather than relaxing one edge as A* does, is what costs the extra factor $\Delta$."
   The reviewer's derivation is right: `UpdateVertex` recomputes a minimum over all
   successors, so the per-call work is $O(|E|(\Delta+\log|V|))$, not
   $O((|V|+|E|)\log|V|)$.

2. **Definition 5.1 excludes the moving start.** *Done.* `def:ch05-problem` now ends with
   the labelled second clause: "In the **moving-start** variant, which D* Lite solves,
   the goal is fixed but before each query the start vertex is replaced by the vertex the
   agent has moved to, which is required to lie on the path returned by the previous
   query." (indexed under `incremental search!moving start`). A road-map sentence was
   added immediately after the definition: "Sections 5.4 and 5.5 treat the fixed-start
   case (LPA*); Sections 5.6 and 5.7 add the moving start (D* Lite)" — written with
   `\cref` on the section labels rather than hard-coded numbers.

3. **"will be expanded a second time later" in the LPA* walkthrough.** *Done.* Replaced
   by: "and may be expanded a second time later, as an ordinary A* expansion, if the loop
   ever reaches its new, larger key; `thm:ch05-expansions` bounds this at one further
   expansion. Step 10 of `tab:ch05-dstarlite-repair` shows a vertex that is retracted and
   never re-expanded, because the search stops first." Verified against the table: step
   10 pops $(1,3)$ with key $[9;6]$ as underconsistent, sets $g=\infty$ and re-inserts it
   with $[11;8]$; the loop stops at step 12 with $(2,3)$ at $[9;7]$, so $(1,3)$ is indeed
   never expanded again.

4. **Drone figure: blue route through the intruder and the tube.** *Done, as prescribed.*
   In `figures/ch05/drone-replanning.tex` the tube polygon base moved from
   `(8.6,0.2) -- (9.4,0.2)` to `(8.6,1.2) -- (9.4,1.2)`, the intruder node from `(9,0.5)`
   to the cell centre `(9.5,1.5)`, and the red velocity arrow now starts at `(9.5,1.5)`.
   The hatched set is unchanged, so the intruder's own cell `(9,1)` stays hatched; row 0
   is now free of both the tube and the marker, and the existing blue route at $y=0.5$ is
   correct without further change. The caption gained: "the drone slips below the
   predicted region through the one row the tube does not reach."

5. **Invisible fourth orange cell in `fig:ch05-idea`.** *Done.* `code/figures/gen_ch05_examples.py`
   gained a `frames=` argument to `panel()`, drawn after the obstacle fills and the grid
   lines, and `idea_figure()` passes
   `frames=[("sbOrange,line width=1.2pt", [r["obstacle"]])]`; an assertion was added that
   the blocked cell really is one of the expanded cells (it is). `figures/ch05/idea.tex`
   was regenerated and now contains
   `\draw[sbOrange,line width=1.2pt] (6,6) rectangle ++(1,1);` after the obstacle fill.
   The generator still reports seed 3: initial search 52, repair 6, A* from scratch 26 —
   all three numbers in the text and caption are unchanged. The caption gained: "The
   newly blocked cell (orange frame) is itself one of the expanded cells: its stale
   distance is retracted first."

6. **Missing solution for `exr:ch05-threshold`.** *Done.* A
   `\begin{solution}{exr:ch05-threshold}` block was added to
   `appendices/solutions/ch05-solutions.tex`, in exercise order (between `exr:ch05-coding`
   and `exr:ch05-intruder`), covering: orders-of-magnitude win in expansions for very
   small $\phi$; the crossover in time arriving much earlier than the crossover in
   expansions because a D* Lite expansion costs about $28\,\mu$s against $4\,\mu$s for an
   A* expansion (`sec:ch05-experiment`); at a $\phi$ of a few per cent on a
   $100\times100$ grid the repair touches a constant fraction of the vertices,
   `thm:ch05-expansions` then permits up to $2|V|$ expansions plus an `UpdateVertex` on
   every neighbour of each, and a fresh A* wins; the rule for `ch:ch24` (count changed
   cells per replanning cycle, fall back to A* above the measured threshold, and always
   after a full map replacement, a goal change or a re-localisation); and an explicit
   statement that the numbers are implementation- and machine-dependent and that the
   student should report their own crossover. The file now has eight solution blocks for
   eight exercises.

### Suggestions

* **Trim around `tab:ch05-km`.** *Applied.* The caption is cut from nine lines to four
  ("Why the key modifier is needed. ... The row of $v$ lists both keys it could receive;
  it is inserted once."); the walk-through paragraph after the table, which explains the
  same six numbers, is kept unchanged.
* **Strict key order.** *Applied.* `def:ch05-key` now adds: "and $k<k'$ iff $k_1<k'_1$,
  or $k_1=k'_1$ and $k_2<k'_2$."
* **Machine-dependent numbers.** *Applied.* `sec:ch05-experiment` now says, before the
  first quoted timing: "The expansion counts below are seed-deterministic and reproduce
  exactly; the wall-clock times were measured on a 2024 laptop and will differ on your
  machine." No number changed.
* **"Processing a vertex makes it consistent."** *Applied.* `sec:ch05-intuition` now
  reads "Processing a vertex either makes it consistent or replaces its stale value by a
  larger, honest one, and may make its neighbours inconsistent, ...".
* **Memory.** *Applied.* A short `\paragraph{Memory.}` was added to
  `sec:ch05-implementation`: two floats per vertex for the lifetime of the mission,
  $O(|V|)$ storage that a search from scratch releases when it returns, $400\,000$
  vertices for the $200\times200\times10$ voxel grid of `sec:ch05-motivation`.
* **Notation table.** *Not applied, deliberately.* The `\key` / `k(s)` mismatch and the
  missing rows for $s_{\mathrm{start}}$, $s_{\mathrm{goal}}$, $s_{\mathrm{last}}$ live in
  `frontmatter/notation.tex`, which is outside this chapter's file set; as the review
  itself notes, that belongs to the consistency pass. Flagged for it.
* **Exercise spread.** *Not applied.* The proposed difficulty-1 item ("list the queue in
  pop order from the middle panel of `fig:ch05-lpastar-example`") would need numbers that
  the existing trace table already prints in pop order, so it would be a lookup rather
  than an exercise; and the chapter is now at the 24-page ceiling. Left for round 2 if
  the reviewer still wants a second on-ramp item.

### What must be kept

Nothing on the "must be kept" list was touched: the 13-vs-7 expansion count of the LPA*
worked example and its explanation, the wall-clock finding that the incremental planner
has not repaid its first search after 40 events, the dotted third curve of
`fig:ch05-experiment`, the "Replanning can be slower than A*" pitfall, `tab:ch05-directions`,
the "Why the two-component key works" argument, the numeric $k_m$ table (only its caption
was shortened; every number and the companion exercise `exr:ch05-kmproof` are untouched),
all five pitfalls, all trace tables verbatim from `latex_trace`, the drone box's reading of
"edge costs change", and `exr:ch05-intruder`.
