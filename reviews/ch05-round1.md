# Review of Chapter 5 (Incremental Search: LPA* and D* Lite) - round 1

Reviewed artefacts: `Overleaf/chapters/ch05-lpastar-dstarlite.tex` (1443 lines),
`Overleaf/figures/ch05/{idea,consistency,lpastar-example,dstarlite-example,replanning-experiment,drone-replanning}.tex`,
`Overleaf/code/ch05_dstar_lite.py`, `Overleaf/code/figures/gen_ch05_examples.py`,
`Overleaf/code/figures/gen_ch05_replanning.py`, `Overleaf/figures/data/ch05-replanning.dat`,
`Overleaf/appendices/solutions/ch05-solutions.tex`, `Overleaf/appendices/glossary/ch05-terms.tex`,
`Overleaf/bib/ch05-extra.bib`, `Overleaf/references.bib`, `Overleaf/frontmatter/notation.tex`,
`Overleaf/chapters/ch02-toolbox.tex`, `Overleaf/chapters/ch04-astar.tex`,
against `STYLE_GUIDE.md` §9 (A-H), `docs/specs/ch05.md` and `docs/core-idea.txt` (Week 2).

**Build.** `cd Overleaf && ./build.sh ch05-lpastar-dstarlite` -> status 0, no `!` errors, no undefined
references or citations belonging to this chapter (the `??` in the PDF are all cross-chapter refs, as
expected in a single-chapter build). Two overfull `\hbox`es above the 15 pt threshold, both from figure
files (see change 8). Output: 45-page PDF; the chapter itself is book pages 13-35, i.e. **23 pages** -
inside the 24-page cap, about 5 pages above the 16-18 page target of `docs/specs/ch05.md`. No cuts are
*required*: the excess is content, not padding (two full worked examples with four trace tables and
three code listings). Trimming ideas are in Suggestions.

**Code.** `python3 code/ch05_dstar_lite.py` -> `self-test passed in 0.8 s` (exit 0). I re-ran
`lpastar_example()`, `dstar_lite_example()`, `idea_scenario(3)` and a copy of
`gen_ch05_replanning.py` redirected to a scratch file, and compared every number in the text against
the output. **All expansion counts, keys, rhs-values and trace rows reproduce exactly**: LPA* first
search 5 expansions / cost 4; repair 13 expansions, cost 6, A* from scratch 7 expansions; every row of
Tables 2.1 and 2.2 is byte-identical to the LaTeX the code emits; D* Lite initial search 10 expansions,
k(S)=[7;7], cost 7; repair 12 expansions with k_m=2, 3 updated vertices, no reinsert firing, A* from
(2,3) also 12; goal at t=9; Figure 2.1's "26 expansions" and "6 expansions" (over 4 distinct cells);
and the experiment section's 1285/279/1247 expansions, factor 4.6, 14 166 vs 1 031, ratio ~14,
crossover at event 4, 203 on-path events (mean 49.3, median 4, max 1704), 197 off-path events (mean
1.5, zero in 68 %), 28 us vs 4.1 us per expansion. The regenerated `.dat` matches the committed one in
every expansion column exactly. **One quoted claim is contradicted by that same data** (change 2).

**Pseudocode.** Algorithm 2.1 matches LPA* (Koenig, Likhachev & Furcy, AIJ 2004, Fig. 1) line for line,
and Algorithm 2.2 matches the final version of D* Lite (Koenig & Likhachev, AAAI 2002, Fig. 3) line for
line, including `s_last`, the `k_old < CalculateKey(u)` reinsert test, `Pred(u) ∪ {u}` on
underconsistency, `UpdateVertex` on the *tail* of a changed edge, and the once-per-batch
`k_m += h(s_last, s_start)`. Keys, the loop condition and the argmin step all agree with the spec.

## Verdict

**Minor revision.** Four required changes are in category A (one invalid step in a proof sketch, one
number/claim the code contradicts, one wrong quantitative claim about grid path quality, one
over-general tie-breaking claim), one in D and four in F/G. Every one of them is local: a sentence, a
caption, a `\section` optional argument, or a `scale=` value. Nothing in the chapter's structure,
algorithms, examples, experiment or exercises needs rework.

## Required changes

1. **`ch05-lpastar-dstarlite.tex` line 944, proof sketch of Theorem 2.9 (`thm:ch05-expansions`) - the
   consistency inequality is written the wrong way round, so the "hence" does not follow.**
   The text has
   `$\hcost(s_{\mathrm{start}},u) \le \hcost(s_{\mathrm{start}},s') + c(u,s')$ for the edge $(u,s')$`.
   For the edge `(u,s')` with `u ∈ Pred(s')`, the chapter's own consistency condition
   (§2.6.1, line 539) gives the *opposite* orientation, and that is the one the argument needs:
   from `g(s') + h(s_start,s') ≥ g(u) + h(s_start,u)` one gets `g(s') ≥ g(u) + h(s_start,u) - h(s_start,s')`,
   and only `h(s_start,s') ≤ h(s_start,u) + c(u,s')` turns this into `c(u,s') + g(s') ≥ g(u)`.
   As printed, the inequality bounds `h(s_start,u) - h(s_start,s')` from *above* by `c(u,s')`, which
   yields nothing.
   *Fix:* replace line 944 by
   `$\hcost(s_{\mathrm{start}},s') \le \hcost(s_{\mathrm{start}},u) + c(u,s')$ for the`
   and keep the rest of the sentence unchanged (the following clause `hence $c(u,s')+\gcost(s')\ge\gcost(u)$`
   then follows immediately). Optionally add half a sentence saying that this is
   \cref{sec:ch05-reverse}'s condition applied to the edge $(u,s')$, $u\in\Pred(s')$. (Category **A**)

2. **`ch05-lpastar-dstarlite.tex` lines 1022-1023, §2.8.1 - "although it is faster at every single one
   of them" is false in the chapter's own data.**
   In `figures/data/ch05-replanning.dat` the mean D* Lite time exceeds the mean A* time at 7 of the 40
   events: event 2 (1.37 vs 1.25 ms), 4 (2.21 vs 1.47), 5 (4.92 vs 1.52), 13 (5.19 vs 1.65), 16 (1.67
   vs 1.66), 26 (2.66 vs 1.65) and 37 (2.34 vs 1.25). The claim also contradicts the sentence four
   lines later that "the largest single repair expanded 1 704 vertices, several times the cost of an
   A* search".
   *Fix:* replace "although it is faster at every single one of them ($0.8$~ms against $1.5$~ms on
   average)" with something like "although its repairs are on average three times faster than a fresh
   \astar ($0.8$~ms against $1.5$~ms); at $7$ of the $40$ events, where the obstacle closed a corridor,
   the repair was nevertheless the slower of the two (up to $5.2$~ms against $1.6$~ms)". Keep the
   averages - they are correct. (Category **A**)

3. **`ch05-lpastar-dstarlite.tex` lines 1057-1059, §2.9 "Field D*" - the 8 % figure is attributed to
   4-connected grids as well, which is wrong by a factor of five.**
   The ~8 % bound (max ratio `sqrt(4-2*sqrt(2)) ≈ 1.082` between octile and Euclidean distance) holds
   for **8**-connected grids. On a 4-connected grid the worst case is `sqrt(2) ≈ 1.41`, i.e. up to
   about 41 % longer.
   *Fix:* rewrite as "Paths on a grid are restricted to a few headings: up to about $41\%$ longer than
   the true shortest path on a 4-connected grid and up to about $8\%$ longer on an 8-connected one."
   (Category **A**)

4. **`ch05-lpastar-dstarlite.tex` lines 362-363, §2.4 "Why the two-component key works" - the claim
   `$k_2(u) < k_2(w)$ whenever $k_1(u)=k_1(w)$` is stated in general but only holds when `w` is
   overconsistent.**
   With `u` underconsistent, `k2(u) = g(u)`; but `k2(w) = min(g(w), rhs(w))`, and if `w` is itself
   underconsistent then `k2(w) = g(w)`, which can be smaller than `g(u)` (e.g. `g(w)=1`,
   `rhs(w)=g(u)+c(u,w)=6`, `g(u)=5`). The sentence as printed asserts a false inequality.
   *Fix:* qualify it, e.g. "If $w$ is overconsistent, then $k_2(w)=\rhs(w)=\gcost(u)+c(u,w) > \gcost(u)
   = k_2(u)$ because $c(u,w)>0$, so $u$ comes first among the ties and the stale value is withdrawn
   before $w$ is recomputed; if $w$ is itself underconsistent it is retracted in the same way before it
   can be expanded with a stale value." (Category **A**)

5. **`ch05-lpastar-dstarlite.tex` lines 85-89, caption of `fig:ch05-idea` - the headline comparison
   "26 expansions vs 6 expansions" omits the initial search and therefore overstates the case.**
   `gen_ch05_examples.py` reports that the 6-expansion repair follows an initial D* Lite search of
   **52** expansions on the same map, whereas the A* panel is a single 26-expansion search. The chapter
   is scrupulously honest about this later (§2.8, §2.8.1, the last pitfall), but the reader's first
   figure currently reads as an unqualified 4x win.
   *Fix:* add one clause to the caption, e.g. "D* Lite is repairing a search it had already run from
   the drone's original start ($52$ expansions); \cref{sec:ch05-experiment} accounts for that first
   search." Optionally mirror it in the text at lines 78-81. (Category **D**)

6. **`ch05-lpastar-dstarlite.tex` line 759 - the running head of §2.7 collides with the chapter title.**
   On PDF page 21 `pdftotext -layout` shows `Chapter 2. Incremental Search: LPA* and2.7` /
   `D*ALite` / `worked example: the robot moves and an obstacle appears`: the two heads overlap, unlike
   on every other page.
   *Fix:* give the section a short running title:
   `\section[A worked example: \dstarlite repairs a plan]{A worked example: the robot moves and an obstacle appears}`.
   This also shortens the over-long ToC line. (Category **G**)

7. **`ch05-lpastar-dstarlite.tex` line 1208 vs line 1210 - the caption of Listing 2.3 and the docstring
   inside it name different line numbers for the same code.**
   The caption resolves to "lines 35-40 of Main" (via `\ref{alg:ch05-dstarlite:km}`--`\ref{alg:ch05-dstarlite:replan}`),
   while the first line of the quoted docstring says `"""Lines 28'-35': process cells whose blocked
   status flipped.` (the numbering of the original AAAI paper). A reader who follows the caption will
   look for lines that do not exist in Algorithm 2.2.
   *Fix:* change the docstring in `code/ch05_dstar_lite.py` (`notify_changed_cells`, ~line 305) to
   `"""Process cells whose blocked status flipped (Alg. D* Lite, main loop).` and re-copy the listing
   verbatim, so that code and caption agree. (Category **G**)

8. **`figures/ch05/consistency.tex` line 2 and `figures/ch05/replanning-experiment.tex` lines 4/16 -
   two overfull `\hbox`es above the 15 pt threshold of `STYLE_GUIDE.md` §7.**
   Log: `Overfull \hbox (22.95328pt too wide)` right after `consistency.tex` is read, and
   `Overfull \hbox (34.55225pt too wide)` right after the pgfplots figure.
   *Fix:* in `consistency.tex` change `[scale=1, ...]` to `[scale=0.92, ...]`; in
   `replanning-experiment.tex` change both `width=0.5\textwidth` to `width=0.46\textwidth` and
   `xshift=1.6cm` to `xshift=1.1cm`. Re-build and confirm both warnings are gone. (Category **G**)

9. **`ch05-lpastar-dstarlite.tex` §2.3, lines 127-133 - no bridge from Chapter 4's notation to this
   chapter's.**
   Chapter 4 (`def:ch04-problem`) writes the start node `s`, the goal `\gamma`, and uses
   `\gcost^*(n)`/`\hcost^*(n)` for true distances; Chapter 5 introduces `s_{\mathrm{start}}`,
   `s_{\mathrm{goal}}` and `\dist(u,v)` without a word. A reader working alone will wonder whether
   `\gcost` here is the same object as `\gcost` there (it is not: here it is a *stored* value that may
   lag). `\rhs`, `k_m`, `\Pred`, `\Succ` and `\dist` are also absent from
   `frontmatter/notation.tex` (currently a placeholder).
   *Fix:* add one sentence after line 133, e.g. "In the notation of \cref{ch:ch04}, $s_{\mathrm{start}}$
   is the start node $s$, $s_{\mathrm{goal}}$ the goal $\gamma$, and $\dist(s_{\mathrm{start}},n)$ the
   true distance $\gcost^*(n)$; unlike in \cref{ch:ch04}, $\gcost(s)$ here is a value stored from an
   earlier search and may be stale." Also list `\rhs`, `k_m`, `\Pred`, `\Succ`, `\dist` in your final
   report as notation-table additions for Phase 1. (Category **F**)

## Suggestions

* §2.8 line 956: "Two remarks put the bound in perspective" is followed by *First*, *Second* and
  *Third*. Say "Three remarks", or fold the third into the second.
* §2.8 heading promises "complexity" but no time bound is stated. One sentence would close it: within a
  call, at most `2|V|` expansions, each doing `O(deg(u))` `UpdateVertex` calls of `O(deg + log|U|)`, so
  `O((|V|+|E|) log|V|)` worst case per call - the same as a fresh A*, with the constant paid only where
  values actually changed.
* The band effect is explained four times (end of §2.5, §2.8 "Third", §2.8.1, and the last pitfall).
  Cutting the §2.5 occurrence to a forward reference would save ~a third of a page and remove the only
  real repetition in the chapter.
* Listing 2.1 (39 lines) is generic heap infrastructure. Keeping only `insert`, `remove`, `_purge` and
  `top_key` would save ~2/3 of a page without losing anything the text discusses.
* `figures/ch05/drone-replanning.tex` draws the intruder as a node containing `?` and the drone as a
  node containing `1`. Neither is explained in the caption; add "the `?` marks the non-cooperative
  intruder, `1` the drone under our control".
* §2.9 mentions "its Focussed variant" of D* without a citation. Stentz, *The Focussed D\* Algorithm
  for Real-Time Replanning*, IJCAI 1995, is the right entry if you want one; otherwise drop the clause.
* CBS, ECBS, ORCA and DWA appear expanded only as macros in the drone box; `STYLE_GUIDE.md` §3 asks for
  a definition at first use in *every* chapter. LPA* is likewise only expanded in §2.4, after four
  earlier uses - move "Lifelong Planning \astar" into the second paragraph of §2.1.
* `appendices/solutions/ch05-solutions.tex` covers 4 of the 8 exercises (the same ratio as ch03), and
  the four it covers are excellent. Exercises 2.5 (reversal) and 2.8 (intruder tube) would benefit most
  from a short hint, since both are conceptual and have no code to check against.
* Table 2.4's "stored key" column shows "[9;6] or [11;6]" for `v`, which is really two different
  scenarios in one cell. Splitting it into two rows, or adding a footnote, would make the point land
  faster.

## What must be kept

This is a strong, unusually well-verified chapter, and most of it should not be touched. The two-halves
structure - LPA* first with a fixed start, then the mirror-image D* Lite plus `k_m` - is exactly the
right pedagogical order, and Table 2.3 (the LPA*/D* Lite mirror table) is the single most useful page
in the chapter for a reader who has to implement this. Both pseudocode listings are faithful to the
canonical sources line for line, including the edge cases the style guide singles out (`Pred(u) ∪ {u}`
on underconsistency, `UpdateVertex` on the tail, once-per-batch `k_m`). Every number in both worked
examples, in Figure 2.1 and in the whole experiment section is machine-generated and reproduces
exactly - including the honest, and rare, admissions that the LPA* repair costs 13 expansions against
A*'s 7 on the toy grid, that the first D* Lite search is 4.6x more expensive than a well-tuned A*, and
that cumulative wall-clock time has not recovered after 40 events. That intellectual honesty, and the
explanation of *why* (the second key component forces the whole `f`-band), is the best thing in the
chapter; keep it verbatim. The five pitfall boxes are all real, all distinct, and all the mistakes
people actually make. The `k_m` treatment (triangle-inequality argument, Table 2.4's numeric
counterexample, the lower-bound/reinsert invariant, and Exercise 2.4 asking for the proof) is the
clearest short account of the key modifier I have read. The exercise set is well graded and genuinely
solvable from the chapter, the Week-2 coding exercise is present and complete with its 8-connectivity
part, and the four written solutions - especially the `k1`-only counterexample for Exercise 2.3 - are
worth more than most textbooks' answer keys.

---

## Response to review (round 1)

All nine required changes are applied. Chapter file: `Overleaf/chapters/ch05-lpastar-dstarlite.tex`;
code: `Overleaf/code/ch05_dstar_lite.py`; figures: `Overleaf/figures/ch05/`; solutions:
`Overleaf/appendices/solutions/ch05-solutions.tex`; bibliography: `Overleaf/bib/ch05-extra.bib`.

### Required changes

1. **(A) Consistency inequality in the proof sketch of `thm:ch05-expansions`.** Accepted; the
   reviewer is right that the printed orientation does not support the deduction. The sentence
   now reads: "The consistency condition of \cref{sec:ch05-dstarlite}, applied to the edge
   $(u,s')$ with $u \in \Pred(s')$, reads $\hcost(s_{\mathrm{start}},s') \le
   \hcost(s_{\mathrm{start}},u) + c(u,s')$, hence $c(u,s') + \gcost(s') \ge \gcost(u)$".
   The chain now runs: key order gives $\gcost(s') \ge \gcost(u) + \hcost(s_\mathrm{start},u) -
   \hcost(s_\mathrm{start},s')$, and the (correctly oriented) consistency inequality turns that
   into $c(u,s') + \gcost(s') \ge \gcost(u)$. The cross-reference points at the section where
   the condition is stated, so the reader can check the orientation.

2. **(A) "faster at every single one of them" in Sec. 2.8.1.** Accepted, with one correction to
   the suggested wording. Replaced by: "although its repairs are on average nearly twice as fast
   as a fresh \astar ($0.8$~ms against $1.5$~ms); at $7$ of the $40$ events, those in which the
   obstacle forced a long detour, the repair was nevertheless the slower of the two (up to
   $5.2$~ms against $1.6$~ms)." The reviewer's draft said "three times faster", but
   $1.493/0.822 = 1.82$, so "nearly twice as fast" is what the data support; the two averages
   themselves are kept as they were. Re-verified against `figures/data/ch05-replanning.dat`:
   exactly 7 of the 40 events have `dsl_ms > astar_ms` (events 2, 4, 5, 13, 16, 26, 37), the
   largest being $5.187$~ms against $1.645$~ms. Those 7 events all have well above-median
   D* Lite expansion counts (42-174 against a median of 4), which is why the clause attributes
   them to a long detour rather than to a corridor specifically.

3. **(A) Field D* paragraph, 8% attributed to 4-connected grids.** Accepted verbatim: "Paths on
   a grid are restricted to a few headings: up to about $41\%$ longer than the true shortest
   path on a 4-connected grid and up to about $8\%$ longer on an 8-connected one."

4. **(A) The $k_2(u) < k_2(w)$ claim in Sec. 2.4.** Accepted; the reviewer's counterexample is
   correct. The sentence is now split into the two cases: if $w$ is overconsistent then
   $k_2(w) = \rhs(w) = \gcost(u)+c(u,w) > \gcost(u) = k_2(u)$ because $c(u,w)>0$, so $u$ comes
   first among the ties; if $w$ is itself underconsistent it is retracted in the same way before
   it can be expanded with a stale value.

5. **(D) Caption of `fig:ch05-idea`.** Accepted, and mirrored in the text as the reviewer
   suggested. The caption now ends "Note that \dstarlite is repairing a search it had already
   run from the drone's original start ($52$ expansions); \cref{sec:ch05-experiment} accounts
   for that first search." Sec. 2.2 gained the matching sentence. The number $52$ was re-checked
   by re-running `code/figures/gen_ch05_examples.py`, which prints "initial search 52, repair 6,
   A* from scratch 26" and regenerates the three example figures byte-identically.

6. **(G) Running head of Sec. 2.7.** Accepted verbatim:
   `\section[A worked example: \dstarlite repairs a plan]{A worked example: the robot moves and
   an obstacle appears}`. `pdftotext -layout` now shows the two heads separated on that page,
   and the ToC line is one line.

7. **(G) `lst:ch05-main` caption vs. the quoted docstring.** Accepted. The docstring in
   `code/ch05_dstar_lite.py` is now `"""Process cells whose blocked status flipped (D* Lite main
   loop).` and the listing was re-copied so that it is again byte-identical to the file. A check
   over all three listings confirms each is a verbatim substring of `ch05_dstar_lite.py`.
   (The AAAI line numbering `26'-27'` in the docstring of `move`, which no listing quotes, was
   left alone.)

8. **(G) Two overfull `\hbox`es.** Accepted and taken further, because the reviewer's numbers
   fixed only one of them. `figures/ch05/consistency.tex` is now `[scale=0.92, ...]`, which
   removes the $22.95$~pt box. For `figures/ch05/replanning-experiment.tex`, narrowing the axes
   to `0.46\textwidth` and `xshift=1.1cm` left a residual $15.47$~pt box, because the culprit is
   the three-column legend, whose width does not depend on the axis width. Both axes are now
   `width=0.45\textwidth` with `xshift=0.9cm`, and the legend is `font=\scriptsize` with
   `column sep=0.2cm` and anchored at `(1.14,-0.34)`. **The chapter build now reports zero
   overfull `\hbox`es of any size.**

9. **(F) Bridge from Chapter 4's notation.** Accepted, with one addition. A new paragraph after
   the notation list in Sec. 2.3 reads: "This is the notation of \cref{ch:ch04} in new clothes:
   $s_{\mathrm{start}}$ is the start node $s$ of \cref{def:ch04-problem}, $s_{\mathrm{goal}}$ is
   the goal $\gamma$, and $\dist(s_{\mathrm{start}},n)$ is the true distance written
   $\gcost^*(n)$ there. One symbol changes meaning, and it is the important one: in
   \cref{ch:ch04}, $\gcost(n)$ is the cost of the best path found *so far in the current
   search*, whereas here $\gcost(s)$ is a value stored from an *earlier* search that may be
   stale until the repair reaches it." The notation-table additions
   ($\rhs$, $k_m$, $\Pred$, $\Succ$, $\dist$) are listed in the final report;
   `frontmatter/notation.tex` is not this chapter's file and was not touched.

### Suggestions

Applied:

* "Two remarks" is now "Three remarks" in Sec. 2.8.
* A running-time paragraph was added after the remarks: at most $2|V|$ expansions per call, each
  calling `UpdateVertex` on $O(\deg u)$ vertices at a cost of the vertex degree plus
  $O(\log|U|)$, hence $O((|V|+|E|)\log|V|)$ per call, the same bound as a fresh \astar, with the
  constant paid only where stored values actually changed.
* `figures/ch05/drone-replanning` caption now explains the two glyphs: the "?" is the
  non-cooperative intruder, the "1" the drone under our control.
* Stentz's Focussed D* is now cited (`stentz1995focussed`, IJCAI 1995, added to
  `bib/ch05-extra.bib`, which is this chapter's bibliography file).
* CBS, ECBS, ORCA and DWA are expanded at first use in the drone box, and "Lifelong Planning
  \astar" was moved into Sec. 2.1 where \lpastar first appears.
* Table 2.4: the cell now reads `[9;6] / [11;6]` and the caption explains that $v$ has a single
  stored key in any given run, the two entries being the key it receives without and with the
  modifier.
* Short hints were written for the two conceptual exercises without code to check against,
  `exr:ch05-directions` (the reversal, including exactly which lines of `Main` exist only
  because the start moves) and `exr:ch05-intruder` (rasterising the tube, updating only the
  symmetric difference on the next prediction, what blocking the whole tube for the whole
  horizon costs, and why a moving goal breaks the backward search).
  `appendices/solutions/ch05-solutions.tex` now covers 6 of the 8 exercises.

Not applied, with reasons:

* **Trimming Listing 2.1 to four methods.** The listing is 39 lines, inside the style guide's
  45-line limit, and every listing in the chapter is currently a byte-exact substring of
  `ch05_dstar_lite.py`. Cutting `__init__`, `__contains__` and the class docstring, which is
  where the lazy-deletion invariant ("a heap entry is live only if its key equals
  `key_of[vertex]`") is actually stated, would cost the one thing the surrounding text discusses
  in exchange for two thirds of a page.
* **Reducing the band-effect explanation in Sec. 2.5 to a forward reference.** The four
  occurrences serve different purposes (a first observation on the toy trace, the theorem's
  third remark, the measured factor $4.6$, and the pitfall), and the reviewer's own "what must
  be kept" paragraph names this honesty as the best thing in the chapter. Left as it is rather
  than risk thinning it.

### Verification

* `cd Overleaf && ./build.sh ch05-lpastar-dstarlite`: no `!` errors from this chapter's files, no
  overfull `\hbox` of any size, and the only undefined references are the expected cross-chapter
  ones (`ch:ch01`-`ch:ch03`, `ch:ch06`-`ch:ch25`, `ch:appA`, `ch:appB`) plus zero undefined
  citations. Occasional `File ended while scanning use of \@writefile` messages naming
  `build/chapters/ch11-*.aux`, `ch19-*.aux` or `ch21-*.aux` come from other chapters' `.aux`
  files being rewritten concurrently in the shared `build/` directory; they disappear on a rerun
  and are not produced by this chapter's sources.
* `python3 code/ch05_dstar_lite.py`: self-test passes in 0.8 s.
* `python3 code/figures/gen_ch05_examples.py`: reproduces `idea.tex`, `lpastar-example.tex` and
  `dstarlite-example.tex` byte-identically and prints the $52/6/26$ expansion counts quoted in
  Sec. 2.2 and its figure caption.
* `python3 code/figures/gen_ch05_replanning.py` was re-run: every expansion column of
  `figures/data/ch05-replanning.dat` is byte-identical, and only the three wall-clock columns
  move with machine load, so the reviewer-verified `.dat` (the one all quoted timings were
  checked against) was restored rather than overwritten. Only a docstring changed in the Python
  file, so no numeric output could change.
