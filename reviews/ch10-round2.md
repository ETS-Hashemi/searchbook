# Review of Chapter 10 (Bounded-Suboptimal Search: ECBS) - round 2

Reviewed artefacts: `Overleaf/chapters/ch10-ecbs.tex` (1511 lines), the five figure
files `Overleaf/figures/ch10/{idea,focal-lowlevel,example-instance,example-trees,benchmark}.tex`,
the data file `Overleaf/figures/data/ch10-benchmark.dat` and its generator
`Overleaf/code/figures/gen_ch10_benchmark.py`, the implementation
`Overleaf/code/ch10_ecbs.py`, `Overleaf/appendices/solutions/ch10-solutions.tex`,
`Overleaf/appendices/glossary/ch10-terms.tex`, `Overleaf/frontmatter/notation.tex`,
`Overleaf/references.bib` and `Overleaf/bib/ch10-extra.bib`, against
`STYLE_GUIDE.md` section 9 (A-H), `docs/specs/ch10.md` and `docs/core-idea.txt`
(Week 5), plus the round-1 review and the reviser's response.

**Build.** `cd Overleaf && ./build.sh ch10-ecbs` exits 0. No `!` errors. No undefined
label or citation belonging to this chapter; every `??` in the chapter body is a
cross-chapter reference (ch11, ch13, ch14, ch18, ch20, ch21, ch24), which is expected
in a single-chapter build. Overfull boxes inside the chapter: 3.54 pt and 1.48 pt
(lines 505-526), both far below the 15 pt threshold; the one 29.10 pt box the log
reports is line 39 of the book-wide List of Algorithms (an RRT entry), not chapter
text. Length: the chapter is pages 22-44 of `build/only-ch10-ecbs.pdf`, i.e.
**23 pages**, inside the 24-page ceiling.

**Code.** `python3 code/ch10_ecbs.py` passes in 0.5 s ("45 random instances checked
against CBS"). I re-derived the quoted numbers independently rather than trusting
round 1:

* `tab:ch10-example-compare` - CBS 12/7/13/12/136; `w=1.05` 12/7/13/12/136;
  `w=1.1` 13/4/7/12/61; `w=1.2` 13/2/3/11/37; `w=1.5` 13/1/1/11/20. All reproduced by
  `cbs(worked_example())` and `ecbs(worked_example(), w)`.
* The `w = 1.5` root detour `(3,0),(2,0),(1,0),(0,0),(0,1),(0,2),(1,2),(1,3)` of cost 7
  and the root cost $2+4+7=13$: reproduced. $D = 5$ and
  $T_{\max} = \lfloor 1.5\cdot 5\rfloor = 7$ check out on the $4\times4$ grid with
  $(3,2)$ blocked.
* `tab:ch10-cbs-trace` and `tab:ch10-ecbs-trace`: every node id, cost, $\mathrm{LB}$,
  per-agent bound vector, $h_c$ and F/O flag matches the trace printed by the
  self-test.
* `ex:ch10-lowlevel`: `w=1.5` gives cost 4, no conflict, bound 3, goal selected in
  step 5 after 4 expansions; `w=1` gives cost 3, one conflict, bound 3, after 3
  expansions. The threshold $w = 4/3$ is right (the wait state has $\fcost=4$,
  $\fcost_{\min}=3$).
* Every cell of `tab:ch10-benchmark` and every number of the benchmark prose,
  `sec:ch10-motivation` (2/10, 23 ms, 7 %), `sec:ch10-choosing-w` (1-12.5 %, 28 %,
  within 3 %) and the complexity subsection (1 150 -> under six) matches
  `ch10-benchmark.dat`. The generator's column semantics agree with the table caption
  (means over solved instances; ratios over instances solved by both the solver and
  CBS).
* I re-checked the two claims that are asserted rather than printed. By exhaustive
  enumeration there are exactly **four** conflict-free cost-6 paths for $a_3$ at the
  root and **all four** pass through $(2,1)$ at $t=3$, so the sentence in
  `sec:ch10-example` is correct. `3 * (4/3)` really is `4.0` in Python, as
  `exr:ch10-lowlevel-threshold`(b) and its solution claim. The exercise's part (c)
  numbers are also correct: with $w=1.5$ the low level returns the cost-3 path with one
  conflict, bound 3, after four expansions; with $w=2$ it returns
  $(1,0),(1,0),(1,0),(1,1),(1,2),(1,3)$ of cost 5, no conflict, bound 3.

Both listings are byte-for-byte identical with `code/ch10_ecbs.py` (42 and 23 lines,
under the 45-line limit).

**Round-1 items.** 1 (root paragraph contradicting the section), 2 (the horizon $H$ of
`thm:ch04-horizon` vs the $H$ of `alg:ch10-lowlevel`), 3 (`\cost(\Pi)`/`\cost(N)` ->
`\sumcost(\Pi)`/`N.\cost`) and 5 (the 28 % attributed to the figure) are **resolved
correctly**; I re-read each and re-checked the affected numbers. Item 2's inserted
argument is sound: with $H$ the largest time in any constraint, every vertex constraint
is inert from $H+1$ on and every edge constraint forbids only a departure at some
$t \le H$, so from $H+1$ the agent moves freely and reaches its goal by $H+1+D$; no
cell is blocked by another agent at the low level, so the parked-agent part of ch04's
$H$ is not needed. Item 4 (a row for $\mathrm{lb}_i / \mathrm{LB}(N) / \mathrm{LB}$ in
`frontmatter/notation.tex`) was **not applied**, correctly so: that is a shared
front-matter file and STYLE_GUIDE section 7 tells chapter revisers to report such
additions instead of making them. It is carried forward below as an editor task, not
as a required change against the chapter.

**Theory.** I checked `thm:ch10-invariant`, `thm:ch10-focal`, `thm:ch10-lowlevel-lb`,
`thm:ch10-consistent`, `thm:ch10-ecbs` and `thm:ch10-terminates` line by line against
Pearl and Kim (1982) and Barer et al. (2014), including the points a compressed proof
usually gets wrong: that `thm:ch10-invariant` is choice-rule free and therefore usable
by focal search; that it still applies to a low level that never re-opens, because with
unit costs every generated space-time state already carries its optimal $\gcost$; that
$\fcost_{\min}$ is read *before* the pop, which is what makes
$\fcost_{\min}\le t\le w\fcost_{\min}$ true; that all ancestors of a $\Pi^*$-consistent
node are themselves consistent, which is what licenses the "maximum over ancestor
bounds" step; that $\max(N.\mathrm{lb}_a,\fcost_{\min})$ preserves both
$\mathrm{LB}_i(N)\le\cost(\pi_i^*)$ and $\cost(\pi_a)\le w\,\mathrm{lb}_a$; and that
the termination sketch's "every constraint has $t \le w\,C^*$" follows because a
conflict cannot occur after the makespan and the makespan is at most the sum of costs.
The monotonicity argument for $\fcost_{\min}$ under a consistent $\hcost$ is correct as
written. The $w_H w_L$ guarantee for BCBS, the EES selection rule and the description
of EECBS's online-learned $\hat{\fcost}$ match Thayer and Ruml (2011) and Li, Ruml and
Koenig (2021). I found no incorrect formula, no unproved theorem and no complexity
claim that does not hold.

**Coverage.** Every "must cover" item of `docs/specs/ch10.md` is present: why optimal
CBS does not scale and what the bound buys (10.1); FOCAL search in general with the
theorem and its proof (`def:ch10-focal`, `thm:ch10-focal`); focal search at the low
level with $h_{\Focal}=h_c$ and at the high level with
$\mathrm{LB}=\min_{N\in\Open}\mathrm{LB}(N)$; the lower-bound bookkeeping
(`def:ch10-lb`, line `alg:ch10-ecbs:lb`, `thm:ch10-lowlevel-lb`); full pseudocode for
both levels; a worked example contrasting CBS and ECBS on one instance in the figure
family of ch09, with cost / CT nodes / bound in a table; `thm:ch10-ecbs` with proof;
choosing $w$; the generated benchmark figure and the speed-quality table for
$w\in\{1.1,1.5,2\}$; EECBS in one section; implementation notes (two heaps, refilling
FOCAL when $\fcost_{\min}$ rises, tie-breaking); all three required pitfalls; the drone
box; and eight exercises including the Week-5 coding exercise and a proof exercise on
the bound. Week 5 of the training plan is fully served, milestone included.

**Presentation.** 5 figures (concept, low-level example, worked-example instance,
constraint trees, generated benchmark), all referenced with `\cref`, captions that say
what to notice, consistent `searchbook.sty` styles; 5 tables in `booktabs`; 2
`algorithm2e` algorithms with unique `Ecbs*` macro names; 2 listings; 26 index entries
(including subentries); 13 citations, all resolving (12 in `references.bib`,
`thayer2011bounded` in `bib/ch10-extra.bib`). I can vouch for the bibliographic details
of all 13: Barer et al., SoCS 5(1) 2014, 19-27; Pearl and Kim, IEEE TPAMI 4(4) 1982,
392-399; Li, Ruml and Koenig, AAAI 2021, 12353-12362; Thayer and Ruml, IJCAI 2011;
Felner et al., ICAPS 2018, 83-87; Li et al., AAAI 2019, 6087-6095; Pohl, AIJ 1(3-4)
1970, 193-204; the rest are the book's standard entries. Notation follows
`frontmatter/notation.tex` (`\sumcost`, `N.\cost`, `\Focal`, `\fcost_{\min}`, $h_c$)
and ch07/ch09 usage. No forbidden hedge words. Exercise difficulties 1,1,2,2,2,3,3,3;
five of the eight have worked solutions in the appendix, and all five are correct (I
checked `exr:ch10-focal-by-hand`, `exr:ch10-lowlevel-threshold` and
`exr:ch10-node-bound` against the code and by hand).

## Verdict

**Accept.**

No required changes remain in categories A-E, and nothing in F-H beyond one shared-file
addition that the chapter's reviser is not permitted to make and has already handed to
the editor. The chapter is technically correct, complete against the spec and the Week-5
plan, reproducible to the digit, and it builds cleanly.

## Required changes

None.

(The four round-1 items that were inside the chapter's remit are resolved and are not
re-raised. The fifth, item 4 of round 1, is an editor task on a shared file and is
restated under Suggestions so it is not lost.)

## Suggestions

None of the following blocks acceptance; take them or leave them.

1. **Editor task, carried over from round 1 (category F, shared file).** Add one row to
   the MAPF block of `Overleaf/frontmatter/notation.tex`, which lists `\Focal`,
   $\fcost_{\min}$ and $h_c$ but not the symbol the whole correctness argument turns on:

       $\mathrm{lb}_i$, $\mathrm{LB}(N)$, $\mathrm{LB}$ & per-agent lower bound, their sum in a CT node, and its minimum over \Open & \cref{ch:ch10}\\

   The chapter itself introduces all three before first use (`def:ch10-lb`, the `\KwOut`
   line of `alg:ch10-lowlevel`) and the glossary carries them, so a reader is never left
   with an undefined symbol; this is purely a front-matter consistency item.
2. **Section 10.4.1, the $w=1$ degeneration sentence.** "breaking ties towards the
   smaller $\fcost$ and then the larger $\gcost$, so that with $w = 1$ it degenerates to
   \astar with the tie-breaking of \cref{ch:ch04}" omits that $\hcost_{\Focal}$ is still
   the *first* key inside the band. Section 10.8.2 states it precisely ("the key reduces
   to conflicts, depth, age"), and `exr:ch10-w-one` asks for "CBS with conflict-based
   tie-breaking", so the two places read slightly differently. Adding three words -
   "\astar with $\hcost_{\Focal}$ and then the tie-breaking of \cref{ch:ch04}" - would
   align them.
3. **Summary, fifth bullet.** "where \cbs fails within ten seconds" is stronger than the
   data (\cbs solves 2 of 10 at $k=16$). The motivation and the benchmark caption both
   give the 2/10; one parenthesis here would make the summary as careful as the body.
4. **Optional trims, if the book-level editor needs the page.** The chapter is 23 pages
   against the spec's 13-15, and I do **not** require cuts, because none of the excess is
   filler in the sense of adding no information. If space must be found, the three
   cheapest places are still the ones named in round 1: (a) the re-quoted percentages in
   Section 10.7.1 that Section 10.7.3 gives again fifteen lines later (keep the three
   rules of thumb and the $\cost/\mathrm{LB}$ diagnostic); (b) the last three sentences
   of "Other values of $w$", which walk `tab:ch10-example-compare` row by row; (c) the
   overlap between the first bullets of Section 10.8.4 and Section 10.8.1. Together
   about 1.5 pages. Completeness outranks length here.
5. **A solution for `exr:ch10-lower-bound`.** It is the one conceptual exercise whose
   answer ("a larger $w$ stops the low level earlier, so $\fcost_{\min}$ has had less
   time to rise; it is still a lower bound because $\fcost_{\min}\le C_i^*$ at every
   moment") a reader working alone might get half right. Six of eight would be a
   generous ratio; five of eight is already in line with ch08/ch09.

## What must be kept

Everything the round-1 review asked to keep survived the revision, and the revision
improved two of those threads rather than disturbing them. Keep, in particular:

* **The lower-bound thread.** `def:ch10-lb`, line `alg:ch10-ecbs:lb`, the "two rulers"
  paragraph (now with the inheritance clause that makes the invariant airtight),
  `thm:ch10-lowlevel-lb`, the second and third pitfall boxes, `exr:ch10-node-bound` and
  its new solution form one coherent argument for the piece of ECBS that most treatments
  skip. The explicit remark that Barer et al. use the returned $\fcost_{\min}$ alone and
  that the `max` is a safe tightening is exactly the kind of scholarship this book should
  show.
* **`thm:ch10-invariant` stated as a choice-rule-free lemma**, so that one invariant
  serves A*, focal search and the low-level bound, and the sentence that closes the
  proof of `thm:ch10-focal`: "the ruler must be honest, the choice inside the band is
  free."
* **The worked example, unchanged.** Running CBS and ECBS on the same $4\times4$
  instance, showing that CBS finds the returned-later solution $N_1$ in step 1 and still
  expands six more nodes, then walking $w$ through 1.05 / 1.1 / 1.2 / 1.5 until the root
  itself changes, is the single best argument for bounded suboptimality in the book - and
  every number is produced by the self-test. Keep the honest admission that ECBS returns
  the cost-13 plan although a cost-12 plan lies inside the band, and the explanation via
  the duplicate rule at line `alg:ch10-lowlevel:dup`.
* **The horizon paragraph in Section 10.6.3 as repaired.** It is now the only treatment
  I know of that states why the ECBS low level may use a smaller $H$ than the generic
  space-time bound, and facts (i) and (ii) genuinely carry `thm:ch10-consistent` and
  `thm:ch10-ecbs`.
* **The benchmark and its `.dat`-driven figure**, including the new 9/10, 9/10, 6/10,
  2/10 success labels on the CBS curve and the caption sentence that tells the reader to
  read the flattening at $k=16$ as failure and not as speed. The table, the figure and
  the prose agree to the digit.
* **The implementation section**: two heaps with lazy purge, the band-widening scan and
  its cost argument, the tie-breaking subsection, and both verbatim listings. The
  insistence that $\fcost_{\min}$ be read before the pop is the detail that decides
  whether an implementation is correct.
* **The drone box**, especially the separation of the bound from safety ("A nominal path
  that is 10 % longer than optimal costs flight time and battery, but it is neither more
  nor less safe") and the observation that mission knowledge belongs in
  $\hcost_{\Focal}$, where it cannot damage the guarantee.
* **The EECBS section with its honesty parenthetical**, now saying that substituting
  $N.\cost$ for $\hat{\fcost}(N)$ in the first EES test changes which nodes are expanded
  and not only which may be returned, so a solver built from that paragraph is a close
  relative of EECBS and not EECBS itself.
