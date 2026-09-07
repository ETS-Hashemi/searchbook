# Review of Chapter 7 (The Multi-Agent Path Finding Problem) - round 2

Reviewed artefacts: `Overleaf/chapters/ch07-mapf-problem.tex` (1234 lines, down from 1297),
`Overleaf/figures/ch07/*.tex` (7 used + 1 now unused), `Overleaf/code/ch07_mapf.py` (683 lines),
`Overleaf/figures/data/ch07-conflict-growth.dat`, `Overleaf/appendices/solutions/ch07-solutions.tex`,
`Overleaf/appendices/glossary/ch07-terms.tex`, `Overleaf/bib/ch07-extra.bib`, against
`STYLE_GUIDE.md` §9, `docs/specs/ch07.md`, `docs/core-idea.txt` (Week 3) and the round-1 review
with the reviser's response.

**Build.** `./build.sh ch07-mapf-problem` exits 0; no `!` errors; no undefined citations; the only
undefined references are cross-chapter (`ch:ch08`, `ch:ch11`, `ch:ch24`, `ch:ch25`, ...), expected
in a single-chapter build. One overfull box, 14.64 pt at lines 271-282
(`tab:ch07-conflict-summary`), i.e. below the 15 pt threshold.
**Code.** `python3 code/ch07_mapf.py` passes its self-test in 0.84 s and prints exactly the numbers
the chapter quotes: naive plan 3/3/1 with `SoC = 7`, `MS = 3` and the three conflicts in the order
of §3.5 (`vertex 0,2 @ t=1`, `swap 0,1 between t=1 and t=2`, `vertex 1,2 @ t=2`); solution 5/3/4
with `SoC = 12`, `MS = 5`, both asserted optimal by the brute-force searches; `ex:ch07-disagree`
gives 10/5 and 11/4 with the optima 10 and 4 and `optimal_soc_bruteforce(inst_o, max_makespan=4)
== 11`. The motivation numbers all match `ch07-conflict-growth.dat` (k=2: 0.950; k=8: 0.050 and
3.500; k=12: 0.000; k=40: 96.883 conflicts, 71.967 pairs). `lst:ch07-costs` is verbatim from the
file. The five cases of `exr:ch07-conflict-cases` and the answers of `exr:ch07-classify`,
`exr:ch07-costs` and `exr:ch07-corridor` are all asserted in `_self_test()`.
**Bibliography.** All 20 keys resolve (16 in `references.bib`, 3 in `bib/ch07-extra.bib`,
`sharon2013icts` in `bib/ch09-extra.bib`); I could verify authors, title, venue, year and pages of
every one of them and none looks fabricated.
**Length.** The chapter body is pages 15-33 of the single-chapter PDF, i.e. **19 pages** (front and
back matter excluded), one page shorter than in round 1 and inside the 20-page ceiling for this
round. I require **no further cuts**; see "What must be kept".

**Round-1 items.** All eight required changes are genuinely fixed, and I re-checked each:
(1) `def:ch07-conflicts`(e) is now stated for $m \ge 3$, and the proposition, the figure caption,
`tab:ch07-conflict-summary` ("cycle ($m \ge 3$)"), the summary bullet, the glossary entry and the
solution to `exr:ch07-classify`(b) all agree; (2) item (e) now requires $m$ pairwise distinct
vertices and says why that costs nothing; (3) the separation claims now read "at every integer
time" with the $\ell/\sqrt2$ bound between integer times, in the paragraph, the table and the
glossary - and they agree with the independent computation in `ch02` line 303 ($\sqrt{0.5}\approx
0.707$); (4) the false "dead end at (1,3)" is replaced by the correct argument; (5) the glossary
entry *Horizon of a plan* now matches `horizon()` in the code; (6) CBS, ECBS, ICTS and ILP are
expanded; (7) the duplicate `sharon2013icts` is gone from `bib/ch07-extra.bib`; (8) the chapter
lost a figure and about a page of repeated prose. None of these is re-raised below.

## Verdict

**Minor revision.** The chapter is accurate, complete against the spec and Week 3 of the training
plan, unusually well verified by its code, and it now reads cleanly. Four defects remain and all
four are local: one step of one proof is skipped in a way that a careful reader will notice, two
notation collisions with `ch02`/`ch08`/`ch09`, and one citation that attributes a SAT encoding to a
hardness paper. No structural change is needed and nothing needs to be cut.

## Required changes

1. **`prop:ch07-hierarchy`(c): the proof of "a cycle conflict contains no swapping conflict" skips
   the non-consecutive pairs.** *Location:* proof of `prop:ch07-hierarchy`, line 241 ("A swap would
   require $\pi_{i_1}[t+1] = \pi_{i_2}[t]$ together with $\pi_{i_2}[t+1] = \pi_{i_1}[t]$, that is
   $i_3 = i_1$, which is impossible for $m \ge 3$"). *Problem:* the argument names the swapping
   pair $(i_1, i_2)$, i.e. it silently assumes that two agents that swap are *consecutive* in the
   rotation. That is exactly the step that needs proving, and a reader who tests $m = 3$ finds a
   reason to doubt it: for the pair $(i_1, i_3)$ the rotation already gives
   $\pi_{i_3}[t+1] = \pi_{i_1}[t]$, i.e. half of the swap condition holds, so the case does not look
   vacuous. *Fix:* replace the sentence by the two-line argument that covers every pair, for
   example: "Suppose $a_{i_a}$ and $a_{i_b}$ swap. Then $\pi_{i_a}[t+1] = \pi_{i_b}[t]$ and, since
   the $m$ vertices are distinct, $\pi_{i_a}[t+1] = \pi_{i_{a+1}}[t]$ forces $i_b = i_{a+1}$;
   symmetrically $\pi_{i_b}[t+1] = \pi_{i_a}[t]$ forces $i_a = i_{b+1}$ (indices modulo $m$).
   Together $a \equiv a + 2 \pmod m$, so $m = 2$, and no pair of a cycle with $m \ge 3$ swaps."
   *Category:* A.
2. **$T_i$ and $T = \max_i T_i$ mean something else in `ch02`, `ch08` and `ch09`, and the reader is
   not warned.** *Location:* `def:ch07-path` (lines 160-176) and `def:ch07-plan`, lines 181-184
   ("Its \textbf{horizon} is $T = \max_i T_i$"). *Problem:* `ch02` (`def:ch02-time-indexed-path`,
   line 214) calls the final-arrival time $T(\pi)$ and its summary bullet (line 756) writes
   "$\makespan=\max_i T_i$, $\sumcost=\sum_i T_i$"; `ch08` (lines 144-148) and `ch09` (lines
   142-147) both define "the cost of the path is its arrival time $T_i$" and
   "$\makespan = \max_i T_i$". In this chapter $T_i$ is the last index that the stored list
   mentions and $T = \max_i T_i$ is the horizon, which is $\ge$ the makespan and equal to it only
   when no path carries trailing waits. A reader arriving from `ch02` therefore reads
   `def:ch07-plan` as defining the makespan, and the whole point of the horizon argument in the
   walkthrough of `alg:ch07-pairwise` is lost. *Fix:* add one sentence to `def:ch07-plan` (or
   immediately after it), for example: "\Cref{ch:ch02} writes the final-arrival time as
   $T(\pi_i)$; here that quantity is $\cost(\pi_i)$, while $T_i$ is only the last index the list
   stores, so $T_i \ge \cost(\pi_i)$ and $T \ge \makespan(\Pi)$. The two coincide when no path ends
   with waits at its goal, which is how \cref{ch:ch08,ch:ch09} store paths." Note in the hand-in
   report that the editor should change `ch02`'s summary bullet to $\max_i T(\pi_i)$ /
   $\sum_i T(\pi_i)$. *Category:* F.
3. **`prop:ch07-bounds` invents $d(u,v)$ where the book has the `\dist` macro.** *Location:*
   `prop:ch07-bounds`, statement and proof, lines 610-624 (four occurrences: the definition of
   $d(u,v)$, the two bounds in `eq:ch07-bounds`, and "$\cost(\pi_i) \ge d(s_i, g_i)$"). *Problem:*
   `searchbook.sty` line 323 declares `\dist` and `ch02` uses `\dist(s,g)` seven times as *the*
   symbol for the shortest-path distance (`def` of distance, line 64); introducing a second symbol
   for the same quantity is the competing notation that STYLE_GUIDE §3 forbids. *Fix:* replace the
   four occurrences by `\dist(\cdot,\cdot)` and shorten the preamble to "Let $\dist(u,v)$ be the
   distance of \cref{ch:ch02} in $G$". *Category:* F.
4. **`tab:ch07-solver-families` cites a hardness paper as the SAT-encoding reference.**
   *Location:* line 743, reduction-based row: "SAT encodings \cite{surynek2010optimization},
   surveyed in \cite{felner2017search}". *Problem:* `surynek2010optimization` is the three-page
   AAAI 2010 note *An Optimization Variant of Multi-Robot Path Planning Is Intractable*
   (pp. 1261-1263), a complexity result; it contains no SAT encoding of MAPF. It is cited correctly
   in `thm:ch07-nphard`, but in this cell it credits the paper with a contribution it does not
   have. *Fix:* make the cell read "SAT encodings (surveyed in \cite{felner2017search}); integer
   programming \cite{yu2016optimal} (\cref{ch:ch22})" and delete
   `\cite{surynek2010optimization}` there. If you want a primary SAT reference, Surynek, Felner,
   Stern and Boyarski, *Efficient SAT Approach to Multi-Agent Path Finding Under the Sum of Costs
   Objective*, ECAI 2016, is the standard one - add it only if you can verify authors, venue and
   pages yourself (STYLE_GUIDE §3); otherwise leave the survey citation alone. *Category:* H.

## Suggestions

* `tab:ch07-solver-families` (line 740) prints "ICTS" one page before the paragraph that expands it
  (line 754). Write "increasing cost tree search (ICTS) \cite{sharon2013icts}" in the table cell and
  drop the expansion from the paragraph.
* Caption of `fig:ch07-example-instance` (line 468): "The crosses mark the three conflicts" - the
  figure draws two crosses, one on the cell $(0,1)$ (which carries both vertex conflicts) and one on
  the edge. Say so: "The cross on $(0,1)$ carries both vertex conflicts, the cross on the edge marks
  the swap."
* `figures/ch07/solver-families.tex` is no longer included anywhere (it was cut in round 1). Delete
  it, or say in the hand-in report that it is deliberately unused, so the editor does not chase a
  missing float.
* Line 1027: "Solving that network is a linear program". MAPF-POST decides the simple temporal
  network by shortest-path computations on its distance graph; "a shortest-path computation on the
  distance graph (a special linear program)" is both shorter and exact.
* Line 36: "The number of conflicts grows roughly like the number of pairs, $k(k-1)/2$". At $k=40$
  the data give 97 conflicts against 780 pairs, so write "grows roughly in proportion to the number
  of pairs" to prevent the sentence being read as an equality.
* Line 366: the parenthesis "(\cref{alg:ch07-pairwise} states the direct version)" is attached to
  "the re-check of the drone architecture", where it does not belong; start the next sentence with
  it.
* The 14.64 pt overfull box in `tab:ch07-conflict-summary` comes from the "Why" column; "one edge
  apart at integer times" instead of "one edge apart at every integer time" removes it.
* `frontmatter/notation.tex` is still the two-row placeholder. In Phase 1 it should carry this
  chapter's symbols $\pi_i$, $\pi_i[t]$, $\Pi$, $T_i$, $T$, $k$, $\cost(\pi_i)$, $\sumcost$,
  $\makespan$ - with the distinction of required change 2 spelled out once, for the whole book.
* Solutions now cover 7 of 9 exercises. The cheapest addition is `exr:ch07-corridor`(b)-(c): the
  self-test already asserts `optimal_makespan_bruteforce(pocket) == 5` and
  `optimal_soc_bruteforce(pocket) == 8` for the pocket corridor, so the answer is two lines.
* Editor note to repeat in the hand-in report: ch07 cites `sharon2013icts` (solver table and the
  ICTS sentence) and the entry is supplied by `bib/ch09-extra.bib`.

## What must be kept

Everything the round-1 review protected has survived and must continue to: the $4 \times 4$ worked
example with its two-part position table and grey stay-at-target padding, the by-hand run of
`alg:ch07-pairwise` that produces exactly the three conflicts the code prints, the space-time figure
of the same plan, `ex:ch07-disagree` with the `optimal_soc_bruteforce(inst_o, max_makespan=4) == 11`
assertion that licenses "no solution attains both", `fig:ch07-conflict-growth` and its generator,
`prop:ch07-hierarchy`, the three pitfall boxes, `exr:ch07-separation` with its derived
$\ell/\sqrt{2}$, and §3.8 in full ( `.map`/`.scen` walkthrough, the $x$/$y$ versus $(r,c)$ warning
and the map-family table). Two things earned their keep in this round as well: the pair
`alg:ch07-pairwise`/`alg:ch07-hashed` with `prop:ch07-detection` - the $\bigO{k^2T}$ and
$\bigO{kT}$ statements are right, the swap tuples in both algorithms are oriented correctly, and
the implementation note on deterministic tie-breaking explains the one place where the code
deliberately differs from the pseudocode - and the split of the coding exercise into
`exr:ch07-coding` and `exr:ch07-prioritized`, which is what makes the Week-3 milestone testable.
Finally, the length: at 19 pages the chapter is one page over the style-guide range and four over
the spec target, but every remaining page is definitions, the worked example, the benchmark section
or floats. Do not trim further; completeness here is worth more than the page.
