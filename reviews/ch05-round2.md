# Review of Chapter 5 (Incremental Search: LPA* and D* Lite) - round 2

Reviewed artefacts: `Overleaf/chapters/ch05-lpastar-dstarlite.tex` (1478 lines),
`Overleaf/figures/ch05/{idea,consistency,lpastar-example,dstarlite-example,replanning-experiment,drone-replanning}.tex`,
`Overleaf/code/ch05_dstar_lite.py`, `Overleaf/code/figures/gen_ch05_examples.py`,
`Overleaf/code/figures/gen_ch05_replanning.py`, `Overleaf/figures/data/ch05-replanning.dat`,
`Overleaf/appendices/solutions/ch05-solutions.tex`, `Overleaf/appendices/glossary/ch05-terms.tex`,
`Overleaf/bib/ch05-extra.bib`, `Overleaf/references.bib`, `Overleaf/frontmatter/notation.tex`,
`Overleaf/searchbook.sty`, against `STYLE_GUIDE.md` §9 (A-H), `docs/specs/ch05.md`,
`docs/core-idea.txt` (Week 2), and `reviews/ch05-round1.md` including the reviser's response.

**Round-1 follow-up.** All nine required changes of round 1 are verified as resolved, and none of
them is re-raised below:

1. (A) The consistency inequality in the proof sketch of Thm 2.9 now reads
   `h(s_start,s') <= h(s_start,u) + c(u,s')` for the edge `(u,s')`, `u in Pred(s')`. I re-derived the
   chain: the key order gives `g(s')+h(s_start,s') >= g(u)+h(s_start,u)`, and the correctly oriented
   inequality turns this into `c(u,s')+g(s') >= g(u)`. **Correct.**
2. (A) §2.8.1 now says "nearly twice as fast ... at 7 of the 40 events ... the slower of the two (up to
   5.2 ms against 1.6 ms)". Re-checked against `figures/data/ch05-replanning.dat`: means 0.8224 ms vs
   1.4932 ms (ratio 1.82), exactly 7 events with `dsl_ms > astar_ms` (2, 4, 5, 13, 16, 26, 37), max
   5.187 vs 1.645. **Correct.**
3. (A) Field D*: "up to about 41% ... on a 4-connected grid and up to about 8% ... on an 8-connected
   one". `sqrt(2)=1.414` and `sqrt(4-2*sqrt(2))=1.0824`. **Correct.**
4. (A) The `k_2` claim in §2.4 is now split into the overconsistent and underconsistent cases.
   **Correct.**
5. (D) The caption of Fig. 2.1 now carries the "(52 expansions)" clause, and §2.2 mirrors it. I
   re-ran `idea_scenario(3)`: `n_init=52`, `n_rep=6`, `astar.expansions=26`, and the repair touches
   exactly 4 distinct cells. **Correct.**
6. (G) §2.7 now has the short running title; `pdftotext` shows the running head
   "2.7 A worked example: D* Lite repairs a plan" cleanly separated on book page 37. **Correct.**
7. (G) The docstring in `notify_changed_cells` now reads "(D* Lite main loop)"; I verified
   programmatically that all three listings are byte-exact substrings of `code/ch05_dstar_lite.py`
   (39, 41 and 16 lines, all under the 45-line cap). **Correct.**
8. (G) **Zero** overfull `\hbox`es of any size in the build log. **Correct.**
9. (F) The bridge paragraph to Chapter 4's notation is in §2.3. **Correct.**

**Build.** `cd Overleaf && ./build.sh ch05-lpastar-dstarlite` -> status 0; no `!` errors; no undefined
reference or citation belonging to this chapter (all `??` are cross-chapter, as expected in a
single-chapter build); no multiply-defined labels; no overfull boxes. 43-page PDF; the chapter is book
pages 27-49, i.e. **23 pages**, inside the 24-page cap (about 5 above the 16-18 page target of
`docs/specs/ch05.md`). The excess is content, not padding - two full worked examples with four trace
tables, two full pseudocode listings and three code listings - so **no cuts are required** (category G
would be the wrong tool here). Fixing change 1 below should give back most of one page.

**Code.** `python3 code/ch05_dstar_lite.py` -> `self-test passed in 0.8 s` (exit 0). I re-ran
`lpastar_example()`, `dstar_lite_example()` and `idea_scenario(3)`, and recomputed the aggregate
statistics from the committed `.dat`. Every number quoted in the chapter reproduces:

* LPA*: first search 5 expansions / cost 4; repair 13 expansions / cost 6; A* from scratch 7
  expansions. Every row of Tables 2.1 and 2.2 is byte-identical to the LaTeX the code emits, and the
  five `UpdateVertex` events after the change match the "The change" paragraph.
* D* Lite: initial search 10 expansions, `k(S)=[7;7]`, cost 7; move/no-change rows; repair with
  `k_m=2`, 3 updated vertices, 12 expansions, `g(2,3)=7`; A* from `(2,3)` also 12; goal at `t=9`;
  `reinserted without expansion: []`, which is exactly the "the reinsert check therefore never fires"
  sentence. Every row of Tables 2.5 and 2.6 matches.
* Experiment: 1285.1/278.6/1246.7 expansions and 32.3/1.26/4.75 ms at event 0 (factor 4.61 ->
  "4.6"); sums over events 1-40 of 1031.0 and 14165.8 expansions (ratio 13.7 -> "about 14") and
  32.90 ms vs 59.73 ms (ratio 1.82 -> "about 1.8", "33 ms"/"60 ms"); cumulative time 65.2 ms vs
  61.0 ms; cumulative expansions cross over exactly at event 4; per-expansion cost
  65.211 ms / 2316.1 = 28.2 us against 60.991 ms / 14444.4 = 4.22 us; `onpath` sums to 20.3, i.e.
  203 on-path and 197 off-path events. All as printed.

**Pseudocode.** Algorithm 2.1 still matches LPA* (Koenig, Likhachev & Furcy, AIJ 2004, Fig. 1) line for
line, and Algorithm 2.2 matches the final version of D* Lite (Koenig & Likhachev, AAAI 2002, Fig. 3)
line for line: `s_last` initialised before `Initialize`, `k_m <- 0`, keys
`[min(g,rhs)+h(s_start,s)+k_m ; min(g,rhs)]`, loop condition
`TopKey() < CalculateKey(s_start) or rhs(s_start) != g(s_start)`, the `k_old < CalculateKey(u)`
reinsert branch, `Pred(u) u {u}` on underconsistency, `UpdateVertex` on the *tail* of a changed edge,
and the once-per-batch `k_m += h(s_last, s_start)`. The heuristic assumptions stated in §2.6.1
(nonnegative, `h(s_start,s_start)=0`, consistency w.r.t. the start, plus the triangle inequality for
`k_m`) are exactly what the proofs use, and admissibility follows from them by induction, so the
assumption set is both sufficient and honest.

**Bibliography.** All ten keys resolve (`references.bib`, `bib/ch05-extra.bib`) and I can vouch for
every one: Koenig & Likhachev AAAI 2002 pp. 476-483; Koenig, Likhachev & Furcy AIJ 155(1-2):93-146,
2004; Koenig & Likhachev T-RO 21(3):354-363, 2005; Stentz ICRA 1994 pp. 3310-3317; Stentz IJCAI 1995;
Sun, Yeoh & Koenig AAMAS 2010; Ferguson & Stentz JFR 23(2):79-101, 2006; Likhachev, Ferguson, Gordon,
Stentz & Thrun ICAPS 2005 pp. 262-271; plus Russell & Norvig and LaValle. Nothing fabricated.

**Spec coverage.** Every "must cover" item of `docs/specs/ch05.md` is present, including the numeric
`k_m` illustration (Table 2.4), the three-panel D* Lite figure, the generated 50x50 experiment, all
five named pitfalls, all four named variants, the drone box with the predicted-intruder-region-as-cost-change
paragraph, and 8 exercises with the Week-2 coding exercise, the hand trace and the `k_m` proof.

## Verdict

**Minor revision.** There are no outstanding problems in categories A, B, D, E or H. Two required
changes remain, both in category G (float placement), and both are local one-line edits to placement
specifiers plus one `\FloatBarrier`. They are not cosmetic, however: as the chapter currently prints,
the D* Lite pseudocode and the two D* Lite trace tables sit *after the exercises*, eleven pages away
from the text that walks through them line by line, which materially damages the chapter for the
reader who is working alone (category C is affected as a consequence). Everything else - the
mathematics, the proofs, the code, the numbers, the figures, the exercises and the citations - is in
publishable shape.

## Required changes

1. **`ch05-lpastar-dstarlite.tex` line 677 (`\begin{algorithm}[htb]`, `alg:ch05-dstarlite`) -
   Algorithm 2.2, the central pseudocode of the chapter, is printed on book page 48, after all eight
   exercises, while §2.6.3 walks through it on book pages 36-37.**
   The float is a full text column tall (40 numbered lines plus `\KwIn`/`\KwOut` and caption), so
   `h` fails at its point of insertion and `t`/`b` can never accept it (it exceeds
   `\topfraction * \textheight`); with no `p` in the specifier LaTeX defers it to the chapter-final
   `\clearpage`. The consequence in the printed PDF: the "Walkthrough" paragraph on page 36 refers to
   "line 8", "line 10", "line 14", "line 15", "line 18", "lines 20-24", and the paragraph on page 37
   to "line 28", "line 30", "line 31", "line 33", "line 35", "line 39", "line 40"; §2.7 (page 37)
   refers to "line 28" and "lines 35-40"; §2.10 (page 44) to "line 30"; and Exercises 2.4 and 2.5
   (page 47) to "line 35" - all of an algorithm the reader has not yet seen. Listing 2.3's caption
   ("lines 35-40 of Main") is likewise unresolvable at the point it is read.
   *Fix:* change line 677 to `\begin{algorithm}[p]` (equivalently `[!htbp]`, which also lifts the
   fraction limits), so that the algorithm is set on a float page inside §2.6. Rebuild and confirm
   with `pdftotext build/only-ch05-lpastar-dstarlite.pdf -` that "Algorithm 2.2. D* Lite, final
   version" now appears *before* the "2.7 A worked example" heading. (Category **G**, with a
   knock-on effect on **C**.)

2. **`ch05-lpastar-dstarlite.tex` lines 805 and 825 (`\begin{table}[tb]`, `tab:ch05-dstarlite-trace`
   and `tab:ch05-dstarlite-repair`) - Tables 2.5 and 2.6 are printed on book page 49, after the
   exercises, while §2.7 discusses them on book pages 37-38.**
   They are held on the deferred-float list behind Algorithm 2.2 (LaTeX defers the remainder of the
   list once a float in it cannot be placed) and are then flushed only at the chapter-final
   `\clearpage`. The reader of §2.7 is told "Table 2.5 lists the events" and "Table 2.6 traces the
   repair" and must jump eleven pages forward for both; the worked example is unreadable as printed.
   *Fix:* after applying change 1, also give both tables `[htbp]` instead of `[tb]`, and insert
   `\FloatBarrier` on its own line immediately before `\section{Properties: correctness, optimality,
   complexity}` (line 902) - `placeins` is already loaded by `searchbook.sty` (line 70), so no
   package change is needed. Rebuild and confirm that Tables 2.5 and 2.6 both appear between the
   "2.7 A worked example" heading and the "2.8 Properties" heading, and that no new overfull box or
   float warning appears. (Category **G**, with a knock-on effect on **C**.)

## Suggestions

* §2.8, proof sketch of Thm 2.9: the sentence "The consistency condition of \cref{sec:ch05-dstarlite}"
  points at §2.6, but the condition is stated in §2.6.1. Change the reference to
  `\cref{sec:ch05-reverse}`.
* §2.5, "The change" paragraph: "two underconsistent cells, eight queued cells" reads as if the queue
  held eight entries; the code shows ten (the two underconsistent cells *plus* eight overconsistent
  ones). Write "two underconsistent cells, eight further queued cells".
* §2.8, second remark: "its only cost is at most one extra pop-and-reinsert per queue entry that was
  inserted before a move" is exact only within a single call of `ComputeShortestPath` (where `k_m` is
  constant); across several calls an entry can be reinserted once per `k_m` increase. Add "within one
  call".
* Table 2.4: the final row prints "v (no `k_m`) | u | u" under three columns whose headings are
  "stored key", "now, no `k_m`", "now, `k_m=2`". Relabelling the first of these cells (for example
  "v, from the stored keys") would make the point land without re-reading the caption.
* `frontmatter/notation.tex` is still a 13-line stub and does not list `\rhs`, `k_m`, `\Pred`,
  `\Succ` or `\dist`. This is a Phase-1 file, not the chapter's, so it is not a required change here;
  keep carrying the five symbols in the hand-in report until the notation table is written.
* `appendices/solutions/ch05-solutions.tex` now covers 6 of the 8 exercises, and the four long ones
  are excellent. The two coding exercises (2.6, 2.7) have nothing; two sentences of expected outcome
  for 2.6 ("the two path costs must agree on every run; off-path obstacles should cost D* Lite zero
  expansions in most events; the first search will be several times more expensive than A*") would
  let a lone reader know whether their implementation is right.
* §2.9, "D* Lite ... is provably at least as efficient in expansions" than D*: this is a real result
  but the reader cannot tell which paper proves it. Either name the theorem in
  \cite{koenig2002dstarlite} or soften to "expands no more vertices than D* in the experiments of
  \cite{koenig2005fast}".
* Figure 2.4's middle panel is described as showing "orange cells ... UpdateVertex made
  inconsistent", while the text says three vertices changed (two became inconsistent, one left the
  queue). One clause in the caption - "the third changed vertex, the gap cell (3,4), simply leaves
  the queue" - would close the small gap between figure and text.

## What must be kept

The chapter is in excellent shape and the round-1 revision was carried out with unusual care - the
reviser even corrected one of my own numbers ("nearly twice as fast", not "three times") from the
data, and pushed the overfull-box fix past the value I suggested when it turned out to be the legend
and not the axis width that was too wide. Keep the two-halves structure (LPA* with a fixed start
first, then the mirror-image D* Lite plus `k_m`); it is the right pedagogical order and Table 2.3, the
LPA*/D* Lite mirror table, remains the single most useful page in the chapter for someone about to
implement this. Keep both pseudocode listings exactly as they are: they are faithful to the canonical
sources line for line, including every edge case the style guide singles out. Keep the whole `k_m`
treatment - the triangle-inequality argument, Table 2.4's numeric counterexample, the lower-bound and
reinsert invariant, Exercise 2.4 and its written solution; it is the clearest short account of the key
modifier I have read, and the solution's explanation of why `k_m` must be *accumulated* rather than
recomputed from the original start (because the direct heuristic distance can shrink when the robot
turns back) is better than the original papers'. Above all, keep the intellectual honesty: the chapter
tells the reader that the LPA* repair costs 13 expansions against A*'s 7 on the toy grid, that the
first D* Lite search is 4.6x more expensive than a well-tuned A*, that cumulative wall-clock time has
still not recovered after 40 events, and that 7 of those 40 repairs were slower than starting over -
and then explains exactly why (the second key component forces the whole f-band). Every one of those
numbers is machine-generated and reproduces exactly. The five pitfall boxes are all real and all
distinct, the exercise set is well graded and genuinely solvable from the chapter, and the six written
solutions are worth more than most textbooks' answer keys.
