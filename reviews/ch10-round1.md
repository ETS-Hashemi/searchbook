# Review of Chapter 10 (Bounded-Suboptimal Search: ECBS) - round 1

Reviewer: independent domain expert (motion planning, MAPF, bounded-suboptimal search).
Material reviewed: `Overleaf/chapters/ch10-ecbs.tex` (1463 lines), `Overleaf/figures/ch10/{idea,focal-lowlevel,example-instance,example-trees,benchmark}.tex`,
`Overleaf/code/ch10_ecbs.py` (834 lines), `Overleaf/code/figures/gen_ch10_benchmark.py`,
`Overleaf/figures/data/ch10-benchmark.dat`, `Overleaf/appendices/solutions/ch10-solutions.tex`,
`Overleaf/appendices/glossary/ch10-terms.tex`, `Overleaf/references.bib`, `Overleaf/bib/ch10-extra.bib`,
against `STYLE_GUIDE.md` section 9 (A-H), `docs/specs/ch10.md` and `docs/core-idea.txt` (Week 5).

Checks actually run:

* `cd Overleaf && ./build.sh ch10-ecbs` - PDF produced, 48 pages of which the chapter proper is
  pp. 18-39 (**22 chapter pages**, inside the 24-page budget). No `!` errors originating in
  `ch10-ecbs.tex`; **no overfull boxes > 15 pt**; the only undefined references are `ch:chNN` of
  *other* chapters, which is expected in a single-chapter build. The non-zero exit status (12) comes
  from `build/only-ch10-ecbs.aux:102: File ended while scanning use of \@newl@bel`, i.e. from the
  `\@input` of a sibling chapter's `.aux`; `./build.sh ch09-cbs` fails identically, so this is a
  harness artefact and **not** chargeable to Chapter 10.
* `python3 code/ch10_ecbs.py` - self-test passes in 0.5 s ("45 random instances checked against CBS").
* Independent re-run of `worked_example()` and `low_level_example()` and of the benchmark `.dat`:
  **every number in Tables 10.2, 10.3, 10.4 and 10.6 and in Examples 10.1 and 10.2 is reproduced
  exactly** (CBS 12/7/13/136; ECBS 1.05 -> 12/7/13/136; 1.1 -> 13/4/7/61, LB 12; 1.2 -> 13/2/3/37,
  LB 11; 1.5 -> 13/1/1/20, LB 11; low level w=1 -> cost 3, 1 conflict, lb 3, 3 expansions;
  w=1.5 -> cost 4, 0 conflicts, lb 3, 4 expansions, goal selected at step 5).
* Benchmark parameters in the text (8x8, 10 % obstacles, 10 instances, 10 s and 50 000 CT
  expansions, w in {1.1, 1.5, 2.0}) match `gen_ch10_benchmark.py` exactly; all table entries match
  `figures/data/ch10-benchmark.dat`.
* Both `lstlisting` excerpts were diffed against `code/ch10_ecbs.py`: **verbatim, 0 deviations**
  (42 and 22 non-blank lines, both under the 45-line cap).
* All 13 citation keys resolve (12 in `references.bib`, `thayer2011bounded` in `bib/ch10-extra.bib`);
  I checked authors/venue/year/pages of each against my own knowledge of the literature and found
  no fabrication and no wrong detail.
* Spec "must cover" list: all 17 items present. Week-5 items of the training plan: all present.

## Verdict

**Minor revision.**

The mathematics is correct, the pseudocode matches Barer et al. (2014), the proofs are real proofs
(and the lower-bound bookkeeping - the part most chapters get wrong - is proved rather than asserted),
and every quoted number is reproduced by the committed code. The defects below are all local: three
sentences whose wording contradicts the chapter's own table/code, two rounded numbers, one
under-specified symbol, one figure legend, and one missing acronym expansion. None of them requires
rewriting a section.

## Required changes

1. **Location:** `sec:ch10-example`, paragraph "\ecbs with $w = 1.1$" (two sentences: "*Steps~2
   and~3 expand $N_2$ and $N_3$ ... because they are the only nodes in the band*" and "*Compare the
   two traces: \ecbs performs the same first three expansions as \cbs, since with a bound of $11$ the
   band contains exactly the nodes of cost $11$*").
   **Problem:** both claims are false and contradict `tab:ch10-ecbs-trace` on the same page and the
   trace printed by the code. With $\mathrm{LB}=11$ and $w=1.1$ the band is $\cost \le 12.1$, so it
   also contains the cost-12 node $N_4$ - which Table 10.3 itself marks "F" at step 2. At step 3
   \Focal is $\{N_3, N_4\}$, not $\{N_3\}$. The reason $N_3$ is expanded before $N_4$ is the
   tie-break (equal $h_c = 1$, then smaller cost), not band membership.
   **Fix:** replace with, e.g.: "Steps 2 and 3 expand $N_2$ and $N_3$: the band $\cost \le 12.1$
   admits $N_2$, then $N_3$ and $N_4$, all with $h_c = 1$, and the tie-break on cost picks the
   cost-11 node each time." And: "\ecbs performs the same first three expansions as \cbs because,
   while $\mathrm{LB} = 11$, every node inside the band still has a conflict and the tie-break on
   cost selects the cheapest one - exactly what \cbs does - and it then stops the moment the bound
   allows it."
   **Category:** A.

2. **Location:** `sec:ch10-focal-alg`, last sentence ("*with a consistent $\hcost$,
   $\fcost_{\min}$ never decreases, because expanding a node generates only successors with a larger
   or equal $\fcost$, **and the node with the smallest $\fcost$ always lies inside the band, so once
   it is expanded the minimum can only rise**.*").
   **Problem:** the italicised second half is a non sequitur and is the wrong reason. Focal search
   generally does *not* expand the node attaining $\fcost_{\min}$, so "once it is expanded" never
   has to happen; and the conclusion does not follow from band membership. The claim itself is true,
   but only because of the first half, which must also cover re-openings. This matters: the whole
   two-heap implementation of `sec:ch10-two-heaps` (and the listing, which only ever raises `f_min`)
   is correct *only* because of this monotonicity.
   **Fix:** "with a consistent $\hcost$, $\fcost_{\min}$ never decreases: whichever node $n$ is
   expanded, every successor $n'$ it pushes - including a re-opened one - satisfies
   $\fcost(n') = \gcost(n) + c(n,n') + \hcost(n') \ge \gcost(n) + \hcost(n) = \fcost(n) \ge
   \fcost_{\min}$, so no node with an $\fcost$ below the current minimum is ever added to \Open."
   **Category:** A.

3. **Location:** `sec:ch10-implementation`, paragraph "The self-test", last sentence ("*It then
   prints the traces of \cref{tab:ch10-cbs-trace,tab:ch10-ecbs-trace}.*").
   **Problem:** the program does not do this. Running `python3 code/ch10_ecbs.py` prints the CBS
   trace, an **ECBS($w=1.05$)** trace and an **ECBS($w=1.2$)** trace; the $w=1.1$ trace of
   Table 10.3 is never printed (it is only asserted: `mid.ct_expanded == 4`,
   `mid.ct_generated == 7`). A reader who runs the file to check Table 10.3 will not find it.
   **Fix:** either (preferred) change the demo block at the end of `ch10_ecbs.py` so that it prints
   the traces for $w = 1.05$, $1.1$ and $1.2$ (one extra `ecbs(inst, w=1.1, keep_trace=True)` print),
   or reword the sentence to "It then prints the trace of \cref{tab:ch10-cbs-trace} and the traces of
   \ecbs for $w = 1.05$, $1.1$ and $1.2$; the $w = 1.1$ one is \cref{tab:ch10-ecbs-trace}."
   **Category:** A.

4. **Location:** (a) `sec:ch10-motivation`, "*\ecbs with $w = 1.5$ solves all ten in about $25$
   milliseconds each*"; (b) `sec:ch10-choosing-w`, "*the plans of \ecbs with $w = 2$ are on average
   $1$--$13\,\%$ more expensive than optimal*".
   **Problem:** neither endpoint is what the code produces. (a) `ch10-benchmark.dat`, $k=16$,
   `e15_time_solved = 0.0231` s, i.e. **23 ms** (and `tab:ch10-benchmark` already says "23 ms", so
   the chapter contradicts itself). (b) the per-$k$ means of `e20_ratio` run from 1.0091 to 1.1246,
   i.e. **0.9 % to 12.5 %**, not "1-13 %".
   **Fix:** write "about $23$ milliseconds each" and "on average $1$--$12.5\,\%$ more expensive than
   optimal" (the "never more than $28\,\%$" is right: `e20_ratio_max` peaks at 1.2766).
   **Category:** A.

5. **Location:** `sec:ch10-lowlevel`, sentence defining the horizon ("*$T_{\max} = \lfloor w\,(H + 1
   + D)\rfloor$, where $H$ is the latest constrained time and $D$ the largest grid distance to the
   goal*"), and line 3 of `alg:ch10-lowlevel`.
   **Problem:** two symbols are used without being pinned down, and the worked example silently
   depends on the missing conventions. $H$ is undefined when $\mathcal{C}_i = \emptyset$ (the root),
   and $D$ is ambiguous ("largest distance" over what set?). The reader cannot reproduce
   `sec:ch10-example`'s "*its horizon $\lfloor 1.5 \cdot 5 \rfloor = 7$*" without knowing that
   $H = -1$ for an unconstrained agent and that $D = \max_{v \text{ free}} \hcost(v) = 5$ for
   $a_3$'s goal $(1,3)$.
   **Fix:** state it once, in the prose and in the pseudocode line: "$H$ is the largest time
   occurring in a constraint of $\mathcal{C}_i$, or $-1$ if $\mathcal{C}_i = \emptyset$, and
   $D = \max_{v} \hcost(v)$ over the free cells", and in `sec:ch10-example` add the parenthesis
   "(no constraints, so $H = -1$ and $T_{\max} = \lfloor w D\rfloor$)".
   **Category:** C.

6. **Location:** `figures/ch10/example-trees.tex`, panel (b): the legend line "*dashed: in \Open,
   never in \Focal*" and the `waiting` style applied to node $N_5$.
   **Problem:** it contradicts `sec:ch10-example`, which says "*Now $N_1$ and $N_5$ enter \Focal,
   both with $h_c = 0$, and step~4 expands the older one*". $N_5$ *does* enter \Focal once
   $\mathrm{LB}$ rises to 12; the flag recorded by the code is only "not in \Focal *at generation
   time*". A student comparing figure and text will conclude one of them is wrong. The legend also
   never explains the plain (undashed, unfilled) style used for $N_4$ and $N_6$.
   **Fix:** change the legend to three lines that match the text: "filled: expanded (order in
   orange); plain: generated, in \Focal, not expanded; dashed: generated outside \Focal (admitted
   only when $\mathrm{LB}$ rises); green: returned solution", and keep $N_5$ dashed. Also adjust the
   closing annotation of the panel, which currently only mentions $N_1$, to say "$N_1$ and $N_5$ are
   admitted when $\mathrm{LB}$ rises to 12; $N_1$ is the older and is expanded".
   **Category:** D.

7. **Location:** `sec:ch10-problem`, first sentence ("*We use the MAPF notation of \cref{ch:ch07}*")
   - first occurrence of "MAPF" in the chapter.
   **Problem:** the acronym is never expanded anywhere in Chapter 10; `STYLE_GUIDE.md` section 3
   requires every acronym to be defined at first use *in every chapter*. (CBS, ECBS, CT, EES, EECBS,
   GCBS and BCBS are all handled correctly - only MAPF is missing.)
   **Fix:** "We use the multi-agent path finding (MAPF) notation of \cref{ch:ch07}."
   **Category:** F.

## Suggestions

* `sec:ch10-benchmark`: "*ten instances for each number of agents $k$ from $2$ to $16$*" - the script
  uses `AGENTS = (2, 4, 6, 8, 10, 12, 14, 16)`. Write "for each even $k$ from 2 to 16" so a reader
  reproducing the curve gets the same 8 points.
* Proof of `thm:ch10-focal`: the step $\gcost(\gamma') = \fcost(\gamma')$ silently uses
  $\hcost(\gamma') = 0$. One parenthesis ("admissibility and $\hcost \ge 0$ give
  $\hcost(\gamma') = 0$") would remove the only unexplained step in an otherwise very clean proof.
* `sec:ch10-choosing-w`: "*Runtime drops steeply between $w = 1$ and $w \approx 1.2$ and flattens
  afterwards*" is a plausible rule of thumb but the benchmark only samples $w \in \{1.1, 1.5, 2\}$.
  Either hedge ("the benchmark samples only three factors; \cref{exr:ch10-coding}(b) asks you to
  locate the knee") or add a $w$-sweep column to the data file.
* `sec:ch10-eecbs`: the selection rule is given as "does the node with the fewest conflicts in \Focal
  have $\cost \le w\,\mathrm{LB}$?". Li et al. phrase the test with the inadmissible estimate,
  $\hat{\fcost}(N) \le w\,\mathrm{LB}$. The two coincide on conflict-free nodes, so the guarantee
  you state is untouched, but a half-sentence ("Li et al.\ test $\hat{\fcost}(N)$; for a
  conflict-free node $\hat{\fcost}(N) = \cost(N)$") would keep the sketch faithful to the source.
* Notation table: `frontmatter/notation.tex` has a row for $\gcost/\hcost/\fcost$ but none for
  \Focal, $\hcost_{\Focal}$, $\mathrm{LB}$, $\mathrm{LB}_i(N)$ or $w$, all of which this chapter
  makes book-level notation. This needs an editor edit outside the chapter; flagging it here as the
  style guide (section 7) prescribes rather than as a required change.
* Length: 22 chapter pages against a spec target of 13-15. I found **no padding worth cutting** -
  every section is a "must cover" item and the prose is dense. If the editor insists on shrinking,
  the only candidates are the four-bullet list "Practical details" (the floating-point bullet
  duplicates `exr:ch10-lowlevel-threshold`(b) and its solution) and the two-sentence "Other
  relatives" subsection, which could be folded into the summary. Both are worth about a third of a
  page each; I do not recommend either.
* `appendices/solutions/ch10-solutions.tex` covers 4 of the 8 exercises, which matches the
  convention of ch07-ch11, so no change is required. If solutions are ever extended,
  `exr:ch10-node-bound` deserves one: the intended answer ($N_7$, $\mathrm{LB} = 15 = \cost$, so
  $\cost \le 1.2\,\mathrm{LB}(N_7)$ admits it although $15/12 = 1.25 > 1.2$) is the sharpest
  illustration of the third pitfall and I verified it holds in the committed tree.

## What must be kept

The chapter's central asset is that the *bookkeeping is proved, not asserted*. Most treatments of
ECBS state the $w$-suboptimality theorem and wave at the lower bounds; here `thm:ch10-invariant`,
`thm:ch10-lowlevel-lb`, `thm:ch10-consistent` and `thm:ch10-ecbs` form a genuine chain - an
optimal-path node is always open, therefore the low level's $\fcost_{\min}$ bounds the constrained
optimum, therefore a consistent CT node's $\mathrm{LB}$ bounds $C^*$, therefore the band is honest -
and the paragraph after the theorem that says which piece of code each step justifies is exactly the
kind of writing a student reading alone needs. Keep it verbatim. Keep the "two rulers" paragraph
(the $\cost(N_{\min}) \le w\,\mathrm{LB}$ argument that \Focal is never empty), which is the detail
that makes the algorithm implementable and is missing from the original paper's exposition. Keep the
worked example in its entirety: one instance, five factors of $w$, a CBS tree and an ECBS tree drawn
side by side, and the honest observation that ECBS returns the cost-13 plan although a cost-12 plan
was inside the band - that single sentence teaches more about bounded suboptimality than the theorem
does. Keep the low-level example with its $w = 4/3$ threshold and its floating-point exercise. Keep
all three pitfall boxes; the third one ($w$ per agent versus $w$ on the sum, with the concrete
counter-node $N_7$) is the mistake practitioners actually make. Keep the benchmark section and its
`.dat`-driven figure: the dashed "proven bound" curves next to the true ratio curves are the visual
statement of the Week-5 milestone. And keep the code as it stands - it is honest, fast, verbatim in
the listings, and every number in the chapter comes out of it.

## Response to review (round 1)

All seven required changes are applied. Nothing the reviewer asked to keep was touched:
`thm:ch10-invariant` / `thm:ch10-lowlevel-lb` / `thm:ch10-consistent` / `thm:ch10-ecbs` and the
paragraph that maps each step of the chain onto the code, the "two rulers" paragraph, the whole
worked example (including the cost-13-inside-a-band-that-held-12 observation), the low-level
example with its $w = 4/3$ threshold, all three pitfall boxes, and the benchmark section with its
`.dat`-driven figure stand verbatim. The chapter is still 22 pages.

### Required changes

1. **`sec:ch10-example`, "ECBS with $w = 1.1$" (category A).** Fixed as prescribed. The two false
   claims are replaced by "Steps 2 and 3 expand $N_2$ and $N_3$: the band $\cost \le 12.1$ admits
   $N_2$, then $N_3$ and $N_4$, all with $h_c = 1$, and the tie-break on cost picks the cost-11 node
   each time." and "\ecbs performs the same first three expansions as \cbs because, while
   $\mathrm{LB} = 11$, every node inside the band still has a conflict and the tie-break on cost
   selects the cheapest one, exactly what \cbs does; and it then stops the moment the bound allows
   it." Verified against the newly printed $w = 1.1$ trace: at step 2 the children are $N_3$
   (11/11/1, FOCAL) and $N_4$ (12/12/1, FOCAL), so FOCAL at step 3 is $\{N_3, N_4\}$, and the focal
   heap key in `ecbs()` is `(conflicts, cost, id)`, i.e. $h_c$ then cost then age.

2. **`sec:ch10-focal-alg`, $f_{\min}$ monotonicity (category A).** Rewritten as prescribed, as a
   displayed chain: "with a consistent $h$, $f_{\min}$ never decreases. Whichever node $n$ is
   expanded, every successor $n'$ it pushes, including a re-opened one, satisfies
   $f(n') = g(n) + c(n,n') + h(n') \ge g(n) + h(n) = f(n) \ge f_{\min}$, so no node with an $f$ below
   the current minimum is ever added to OPEN, and the minimum over OPEN can only rise." The band /
   "once it is expanded" non sequitur is gone, and the argument now covers re-openings, which is what
   `sec:ch10-two-heaps` and `lst:ch10-lowlevel` rely on.

3. **`sec:ch10-implementation`, "The self-test" (category A).** Both halves of the reviewer's option
   were taken. `code/ch10_ecbs.py` demo block now loops `for w in (1.05, 1.1, 1.2)`, so the $w = 1.1$
   trace of `tab:ch10-ecbs-trace` is printed; it reproduces the table row for row
   ($N_0, N_2, N_3, N_1$; children $N_1$ O, $N_2$ F, $N_3$ F, $N_4$ F, $N_5$ O, $N_6$ F; 4 expanded,
   7 generated). The sentence now reads "It then prints the trace of `tab:ch10-cbs-trace` and the
   traces of \ecbs for $w = 1.05$, $1.1$ and $1.2$; the $w = 1.1$ one is `tab:ch10-ecbs-trace`."

4. **Two numbers contradicting the data file (category A).** `sec:ch10-motivation` now says "about
   $23$ milliseconds each" (`e15_time_solved` at $k = 16$ is 0.0231 s, matching `tab:ch10-benchmark`),
   and `sec:ch10-choosing-w` now says "$1$--$12.5\,\%$ more expensive than optimal". I kept the
   reviewer's wording "$1$" for the low end although the smallest per-$k$ mean is 1.0091; it rounds
   to 1 %. "never more than $28\,\%$" is unchanged (max 1.2766). The companion sentence in
   `sec:ch10-benchmark` ("$7$ milliseconds ... $12.5\,\%$" at $k = 14$) was already right.

5. **$H$ and $D$ pinned down (category C).** The prose of `sec:ch10-lowlevel` now reads
   "$T_{\max} = \lfloor w(H + 1 + D)\rfloor$, where $H$ is the largest time occurring in a constraint
   of $\mathcal{C}_i$, or $-1$ if $\mathcal{C}_i$ is empty, and $D = \max_v h(v)$ over the free cells
   $v$", and line 3 of `alg:ch10-lowlevel` sets $H$ and $D$ explicitly before $T_{\max}$. Both match
   `focal_space_time_astar`: `last_t = max((c.t for c in constraints), default=-1)` and
   `max(h.values())` over `inst.distances_to(goal)`. `sec:ch10-example` now carries the parenthesis
   "(no constraints, so $H = -1$ and $T_{\max} = \lfloor w D \rfloor$ with $D = 5$)", which makes
   $\lfloor 1.5 \cdot 5 \rfloor = 7$ reproducible.

6. **`figures/ch10/example-trees.tex`, panel (b) legend (category D).** Legend replaced by "filled:
   expanded (order in orange) / plain: generated, in FOCAL, not expanded / dashed: generated outside
   FOCAL (admitted only when LB rises) / green: returned solution"; $N_5$ stays dashed. The closing
   annotation now reads "$N_1$ and $N_5$ are admitted when LB rises to 12 after step 3
   ($1.1 \cdot 12 = 13.2$); $N_1$ is the older and is expanded." The legend was set in `\scriptsize`
   so the two extra lines do not widen the panel; no overfull box results. For consistency I also
   extended the last clause of the figure caption from "it is expanded at once because it has no
   conflicts" to "admits it together with $N_5$, and of the two conflict-free nodes the older one,
   $N_1$, is expanded."

7. **MAPF expanded at first use (category F).** `sec:ch10-problem` now opens "We use the multi-agent
   path finding (MAPF)\index{MAPF} notation of \cref{ch:ch07}."

### Suggestions

* **Even $k$ in the benchmark.** Applied: "ten instances for each even number of agents $k$ from $2$
  to $16$".
* **$h(\gamma') = 0$ in the proof of `thm:ch10-focal`.** Applied: "Since $\gamma'$ is a goal,
  admissibility and $h \ge 0$ give $h(\gamma') = 0$, and since $\gamma'$ was chosen from FOCAL, ...".
* **Hedging the knee of the runtime curve.** Applied: the claim is now stated as what the three
  sampled $w$ values show, with "Where exactly the knee lies is instance-dependent;
  `exr:ch10-coding`(b) asks you to locate it by sweeping $w$ on your own instances." No $w$-sweep was
  added to the data file, to keep the benchmark script and `ch10-benchmark.dat` as they are.
* **EECBS selection rule.** Applied: a parenthesis after the first test, "(Li et al. state the test
  on the estimate, $\hat f(N) \le w\,\mathrm{LB}$; the two agree on the conflict-free nodes that can
  be returned, where $\hat f(N) = \cost(N)$.)"
* **`frontmatter/notation.tex` rows for FOCAL, $h_{\mathrm{FOCAL}}$, LB, $\mathrm{LB}_i(N)$, $w$.**
  Not done: out of scope for a chapter reviser (the finisher brief forbids editing files outside the
  chapter's own set). Reported to the editor as a needed edit.
* **Length, solutions coverage.** No change, per the reviewer's own recommendation.
* **`build.sh` exit 12.** Not reproduced: `cd Overleaf && ./build.sh ch10-ecbs` now exits 0 with no
  `!` errors, no undefined `ch10` references or citations, and no overfull box above 15 pt
  (`build/only-ch10-ecbs.pdf`, 43 pages; the chapter itself is pp. 13-34, 22 pages).

### Verification

* `python3 code/ch10_ecbs.py` -> "ch10_ecbs self-test passed in 0.4 s (45 random instances checked
  against CBS)". The only code change is the demo loop, so no assertion or number moved.
* `figures/data/ch10-benchmark.dat` was not regenerated: the benchmark script is untouched and every
  number now quoted in the text is read off the committed file (23 ms, 7 %, 7 ms, 12.5 %, 28 %,
  2-3 %, 1153 expansions, 6/10 and 2/10 at $k = 14, 16$).
