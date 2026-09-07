# Review of Chapter 7 (The Multi-Agent Path Finding Problem) - round 1

Reviewed artefacts: `Overleaf/chapters/ch07-mapf-problem.tex` (1297 lines),
`Overleaf/figures/ch07/*.tex` (8 figures), `Overleaf/code/ch07_mapf.py` (683 lines) and
`Overleaf/code/figures/gen_ch07_conflict_growth.py`, `Overleaf/figures/data/ch07-conflict-growth.dat`,
`Overleaf/appendices/solutions/ch07-solutions.tex`, `Overleaf/appendices/glossary/ch07-terms.tex`,
`Overleaf/bib/ch07-extra.bib`, against `STYLE_GUIDE.md` §9, `docs/specs/ch07.md` and
`docs/core-idea.txt` (Week 3).

Build: `./build.sh ch07-mapf-problem` exits 0, no `!` errors, **no overfull boxes > 15 pt**, no
undefined citations, and the only undefined references are cross-chapter ones (`ch:ch04`,
`ch:ch09`, ... ) which are expected in a single-chapter build.
Code: `python3 code/ch07_mapf.py` passes its self-test in 0.87 s. Every number quoted in the
chapter is reproduced: naive plan costs 3/3/1, `SoC = 7`, `MS = 3`, the three conflicts in the
order printed in §1.5; the conflict-free plan costs 5/3/4, `SoC = 12`, `MS = 5`, both confirmed
optimal by `optimal_soc_bruteforce`/`optimal_makespan_bruteforce`; the disagreement example
`SoC(Y) = 10, MS(Y) = 5`, `SoC(X) = 11, MS(X) = 4`, optimum `10` and `4`, and
`optimal_soc_bruteforce(inst_o, max_makespan=4) == 11` (which is what licenses "no solution
attains both"); the motivation numbers 95 %, 5 %, 3.5, 0/60, 97 conflicts and 72 pairs all match
`figures/data/ch07-conflict-growth.dat`. Bibliography: all 20 keys resolve, and I could verify
authors/venue/year/pages of every one of them; nothing looks fabricated.
Length: the chapter body is pages 13-32 of the single-chapter PDF, i.e. **20 pages** (front
matter and back matter excluded) against a spec target of 13-15 and a style-guide range of 12-18.

## Verdict

**Minor revision.** The chapter is technically strong, complete against the spec and the Week-3
plan, and unusually well verified by its code. Every defect I found is local: one genuine
internal contradiction in the conflict taxonomy (m = 2 cycles), two over-strong physical claims,
one false statement about the worked-example graph, a wrong glossary definition, an unexpanded
acronym, a duplicated bib entry, and about two pages of prose that repeats a table. None of them
touches the structure of the chapter.

## Required changes

1. **A cycle conflict with `m = 2` is a swapping conflict, so the chapter both forbids and allows
   it.** *Location:* `def:ch07-conflicts` item (e), lines 213-218; `prop:ch07-hierarchy` (b)/(c),
   lines 229-233; the paragraph "What this book forbids", lines 249-259; `tab:ch07-conflict-summary`
   row `cycle`, line 278; the caption of `fig:ch07-conflict-types`, line 113; the summary bullet,
   line 1159; and `appendices/glossary/ch07-terms.tex`, entry *Cycle conflict*. *Problem:* (e)
   admits `m >= 2`, and Prop. (b) states that a swapping conflict *is* a cycle conflict with
   `m = 2`; but the caption, the paragraph, the table and the summary all say classical MAPF
   "allows cycle conflicts" while forbidding swaps. As written, the same event is both allowed and
   forbidden, and the solution to `exr:ch07-classify`(b) repeats the ambiguity. *Fix:* define the
   cycle conflict for `m >= 3`; keep Prop. (b) but phrase it as "the degenerate case `m = 2` of the
   rotation pattern is exactly the swapping conflict, which is why the cycle conflict is defined
   for `m >= 3`"; write "allows (d) and (e)" as "allows (d), and (e) for `m >= 3`"; make the table
   row read `cycle (m >= 3)`; adjust the summary bullet and the glossary entry the same way.
   *Category:* A.
2. **`prop:ch07-hierarchy`(c) needs the distinctness of the cycle's vertices as a hypothesis.**
   *Location:* `def:ch07-conflicts`(e), line 213; proof of `prop:ch07-hierarchy`, lines 236-242.
   *Problem:* the proof asserts "the `m` vertices of the cycle are distinct", but the definition
   does not require it. Without distinctness the claim "contains no vertex conflict" is false: with
   `pi_1[t] = pi_3[t] = u`, `pi_2[t] = v`, the rotation gives `pi_2[t+1] = pi_3[t+1] = u`, a vertex
   conflict. *Fix:* add "on `m` pairwise distinct vertices `pi_{i_1}[t], ..., pi_{i_m}[t]`" to
   definition (e) (and say in one clause that a repeated vertex is already a vertex conflict), then
   the proof reads as written. *Category:* A.
3. **"One full edge behind at every instant" and "a rotation keeps the same distance" are false in
   continuous time.** *Location:* lines 254-259 ("Following is allowed because synchronous
   unit-speed motion keeps the follower one full edge behind the leader at every instant ... a
   rotation on a fully occupied cycle keeps the same distance"). *Problem:* the chapter's own
   `exr:ch07-separation` (line 1271), its solution in `appendices/solutions/ch07-solutions.tex` and
   §1.10 prove the opposite: a following move *around a corner* brings the two agents to
   `l/sqrt(2)` between integer times, and a rotation on a cycle is built from exactly those corner
   moves, so it does not keep the distance either. *Fix:* replace by "keeps the follower one full
   edge behind the leader **at every integer time**; between integer times two agents in distinct
   cells stay at least `l/sqrt(2)` apart, which is attained when the follower turns a corner
   (`\cref{exr:ch07-separation}`)", and change "a rotation on a fully occupied cycle keeps the same
   distance" to "a rotation on a fully occupied cycle has the same geometry and the same bound, so
   cycle conflicts are allowed too". *Category:* A.
4. **"(1,3) is a dead end" is false for the worked-example graph.** *Location:* §1.5, paragraph
   "A conflict-free plan", line 587. *Problem:* only `(1,0)` and `(1,2)` are blocked
   (`worked_example()` in `code/ch07_mapf.py`), so `(1,3)` is adjacent to `(0,3)` **and** to
   `(2,3)`; it is not a dead end. The argument for "the price is unavoidable" therefore does not
   read as stated. *Fix:* "... and an agent that ducks into `(1,3)` can return to the top row only
   through `(0,3)`, which `a_1` occupies from `t = 3` on, or by the detour through row 2 and the
   pocket `(1,1)`; so the pocket `(1,1)` must be used, and `a_3` has to clear it first."
   *Category:* A.
5. **Wrong definition of the plan horizon in the glossary.** *Location:*
   `appendices/glossary/ch07-terms.tex`, entry *Horizon of a plan*: "The largest path cost
   `T = max_i T_i` in a plan". *Problem:* `T_i` is the last index of the stored path, not the path
   cost; the two differ whenever a path carries trailing waits (e.g. `pi_1` of `exr:ch07-costs` has
   `T_1 = 5` and cost 3). The chapter (`def:ch07-plan`) and the code (`horizon()`, "largest time
   index that any path mentions explicitly") both use the index. *Fix:* "The largest time index
   `T = max_i T_i` that any path of the plan mentions explicitly; no vertex or swapping conflict
   can first appear after it." *Category:* A.
6. **CBS, ECBS and ICTS are never expanded in this chapter.** *Location:* first uses at line 337
   (`\cbs`), line 631 (`\ecbs`), line 774 (ICTS); also ILP at line 794. *Problem:* STYLE_GUIDE §3
   requires every acronym to be defined at first use *in every chapter*; a reader who starts Part
   III here meets "CBS" with no expansion. *Fix:* line 337 -> "of conflict-based search
   (\cbs, \cref{ch:ch09})"; line 631 -> "the yardstick of enhanced CBS (\ecbs, \cref{ch:ch10})";
   line 774 -> "the increasing cost tree search (ICTS)"; line 794 -> "a SAT or integer-linear-
   programming (ILP) solver". *Category:* F.
7. **Duplicate bib entry `sharon2013icts`.** *Location:* `Overleaf/bib/ch07-extra.bib` lines 9-16;
   the identical entry already exists in `Overleaf/bib/ch09-extra.bib` lines 2-9. *Problem:* when
   the editor concatenates the per-chapter extra files into `references.bib` this is a duplicate
   key and BibTeX/biber will warn or silently drop one. *Fix:* delete the entry from
   `bib/ch07-extra.bib` and note in the hand-in report that ch07 cites `sharon2013icts`, which
   ch09 supplies. *Category:* H.
8. **Trim about two pages of prose that repeats a table (the chapter is 20 pages against a
   12-18 page rule and a 13-15 page spec target).** *Location:* §1.7 paragraphs "What the families
   do" (lines 768-789) and "Reductions and learning" (lines 790-804); §1.10 paragraph "Why
   classical MAPF remains the right abstraction" (lines 1114-1132); §1.8 paragraph "A caveat"
   (lines 893-903). *Problem:* `tab:ch07-solver-families` already gives family, guarantee,
   representatives with chapter pointers and use case, and `fig:ch07-solver-families` gives the
   same five families a second time; the two prose paragraphs then restate all of it. The "right
   abstraction" paragraph repeats the roadmap of §1.1 and the `dronebox` that follows it, and the
   "caveat" paragraph repeats the first half of §1.10. *Fix:* keep the table and cut
   `fig:ch07-solver-families` (7 figures remain, well above the minimum of 4), or keep the figure
   and reduce the two §1.7 paragraphs to the one sentence per family that the table does not
   carry (what each family *searches*); compress "Why classical MAPF remains the right
   abstraction" to 4-5 sentences (combinatorial core is the NP-hard part; the discrete plan fixes
   the order of visits, which MAPF-POST and the local layers preserve; the guarantees are proved
   at the discrete level and survive if cell side and time step fit the vehicle model); shorten
   "A caveat" to two sentences. Target: <= 18 pages. Do not cut the definitions, the worked
   example, the benchmark formats or the map-family table. *Category:* G.

## Suggestions

* `exr:ch07-objectives`(c): the hint names the uniqueness of the shortest paths of `a_1` and
  `a_2`, but the argument that `MS = 4` forces two delays also needs `a_3`'s shortest path to be
  unique. Write "the shortest paths of all three agents are unique".
* `exr:ch07-horizon`(a): for a legal plan the hypothesis is vacuous - at every `t >= T` all agents
  sit on their pairwise distinct goals, so no conflict of either kind exists after `T`. Restate as
  "show that for any padded plan (whose paths need not end at distinct goals) a vertex or swapping
  conflict at some `t > T` implies a vertex conflict at `T`, and then show that for a legal plan no
  conflict occurs at any `t >= T` at all" - the second half is the fact the walkthrough uses.
* `exr:ch07-coding` carries four substantial parts, one of which - (d) - is the whole Week-3
  milestone. Split it into two exercises ((a)-(c) as a detector/validator exercise, (d) as the
  prioritized-planning exercise); 9 exercises is still inside the 6-10 range.
* Solutions exist for 4 of the 8 exercises, which matches ch01/ch02/ch03/ch05. If room allows, the
  three that a lone reader is most likely to get wrong are `exr:ch07-objectives`(b),
  `exr:ch07-horizon`(b) and `exr:ch07-corridor`(a) - the order-invariance argument on a path graph
  is the kind of proof a beginner cannot start.
* `lst:ch07-files`: in real `.scen` files the ninth field is a floating-point *octile* distance
  (e.g. `4.82843`), not the 4-connected integer used in the listing. Half a sentence after "treat
  as informative only" would prevent a parser that assumes `int`.
* `tab:ch07-solver-families`, reduction-based row: `felner2017search` is a survey; the canonical
  SAT-encoding reference is Surynek's own SAT work. Either cite `surynek2010optimization` there
  too or say "surveyed in \cite{felner2017search}".
* `thm:ch07-nphard` could note in one clause that hardness persists on 4-connected grid graphs
  (Banfi, Basilico and Amigoni, IEEE RA-L 2017) - only if you can verify the entry yourself; do not
  add it otherwise.
* `thm:ch07-bounds` labels a `proposition` environment while `prop:ch07-hierarchy` and
  `prop:ch07-detection` use the `prop:` prefix. Rename to `prop:ch07-bounds` (4 `\cref` uses) or
  promote it to a theorem.
* `def:ch07-instance` calls `<G, s, g>` a triple and then lists `k` as a fourth component. Say
  "consists of an undirected graph `G`, `k` agents, and maps `s, g`", or make `k` implicit in the
  domain of `s`.
* When `frontmatter/notation.tex` is filled in (Phase 1), it should carry this chapter's symbols:
  `pi_i`, `pi_i[t]`, `Pi`, `T_i`, `T`, `k`, `cost(pi_i)`, `SoC`, `MS`.

## What must be kept

The worked example is the best part of the chapter and must survive revision untouched: the
4x4 instance with the two blocked cells, the two-part position table with the grey stay-at-target
padding, the by-hand run of `alg:ch07-pairwise` that produces exactly the three conflicts in the
order the code prints them, the space-time figure that shows the same three paths as nodes and
crossing edges, and the fact that *every* number - including the optimality of `SoC = 12` and
`MS = 5` - is asserted in `_self_test()`. `ex:ch07-disagree` is equally good, and the assertion
`optimal_soc_bruteforce(inst_o, max_makespan=4) == 11` is exactly the right way to back the claim
that no plan attains both optima; keep it. Keep `fig:ch07-conflict-growth` and its generator:
opening a problem chapter with measured evidence that independent planning collapses at about
twelve agents is far more convincing than an assertion. Keep `prop:ch07-hierarchy` - deriving
*which* conflict types imply which is the right way to justify forbidding only two of the five -
and keep the three `pitfall` boxes, especially the stay-at-target one, together with the
discussion in §1.9 of why the implementation finishes the time step to get deterministic
tie-breaking. Keep §1.8 in full: the `.map`/`.scen` walkthrough, the `x`/`y` versus `(r, c)`
warning and the map-family table are practical knowledge that no other textbook writes down. And
keep `exr:ch07-separation` with its `l/sqrt(2)` solution - it is the bridge from the discrete
model to the drone hardware and it is derived, not asserted.

## Response to review (round 1)

All eight required changes were applied. The chapter builds with status 0, no
errors and no overfull boxes above 15 pt; `code/ch07_mapf.py` still passes its
self-test (the code was not modified, so `figures/data/ch07-conflict-growth.dat`
did not need regenerating) and every number quoted in the text still matches the
code output (naive plan 3/3/1 with SoC 7 and MS 3, solution 5/3/4 with SoC 12 and
MS 5, and 10/4/11 in `ex:ch07-disagree`).

**A1 — cycle conflict allowed and forbidden at the same time.**
`def:ch07-conflicts`(e) is now stated for $m \ge 3$. `prop:ch07-hierarchy`(b)
reads "the degenerate case $m = 2$ of the rotation pattern of
\cref{def:ch07-conflicts}(e) is exactly the swapping conflict, which is why the
cycle conflict is defined for $m \ge 3$"; (c) now applies to every cycle conflict
and no longer needs the "$m \ge 3$" qualifier. The caption of
`fig:ch07-conflict-types` reads "allows (d), and (e) for $m \ge 3$", the table
row is "cycle ($m \ge 3$)", the summary bullet names the rotation of $m \ge 3$
agents and calls $m = 2$ the forbidden swap, and the glossary entry *Cycle
conflict* says the same. The solution to `exr:ch07-classify`(b) was rewritten the
same way ("the degenerate case $m = 2$ of the rotation pattern, which is why
cycle conflicts are defined for $m \ge 3$").

**A2 — distinctness in item (e).** Item (e) now requires the agents to "stand on
$m$ pairwise distinct vertices $\pi_{i_1}[t], \dots, \pi_{i_m}[t]$", with the
clause "Distinctness costs nothing: two of these vertices that coincide are
already a vertex conflict at time $t$". The proof of (c) now cites the definition
for distinctness and otherwise reads as before.

**A3 — separation between integer times.** The paragraph now reads "keeps the
follower one full edge behind the leader at every integer time; between integer
times two agents in distinct cells stay at least $\ell/\sqrt{2}$ apart on a
lattice of cell side $\ell$, a bound attained exactly when the follower turns a
corner (\cref{exr:ch07-separation})", and the cycle sentence is "a rotation on a
fully occupied cycle has the same geometry and the same bound, so cycle conflicts
are allowed too". The "Why" column of `tab:ch07-conflict-summary` was corrected
in the same way ("one edge apart at every integer time"), and the glossary entry
*Following conflict* now says "at every integer time".

**A4 — the false dead end at (1,3).** Replaced with the reviewer's wording: "an
agent that ducks into $(1,3)$ can return to the top row only through $(0,3)$,
which $a_1$ occupies from $t = 3$ on, or by the detour through row 2 and the
pocket $(1,1)$; so the pocket $(1,1)$ must be used, and $a_3$ has to clear it
first". The rest of the worked example is untouched.

**A5 — glossary entry *Horizon of a plan*.** Now: "The largest time index
$T=\max_i T_i$ that any path of the plan mentions explicitly; no vertex or
swapping conflict can first appear after it."

**F6 — acronyms.** First uses are now "conflict-based search (\cbs,
\cref{ch:ch09})", "enhanced CBS (\ecbs, \cref{ch:ch10})", "the increasing cost
tree search (ICTS)" and "a SAT or integer-linear-programming (ILP) solver".

**H7 — duplicate BibTeX key.** `sharon2013icts` was deleted from
`bib/ch07-extra.bib` and replaced by a comment. **Note for the editor: ch07 cites
`sharon2013icts` (table of solver families and the ICTS sentence); the entry is
supplied by `bib/ch09-extra.bib`.**

**G8 — length.** `fig:ch07-solver-families` was cut (the table carries family,
guarantee, representatives and use case) and the two Section 1.7 paragraphs were
merged into one, "What the families search", which keeps only what the table does
not carry: what each family searches, plus the ICTS and ILP expansions. "Why
classical MAPF remains the right abstraction" is now four sentences and "A
caveat" two. Beyond the reviewer's list, the Python transcription of
`alg:ch07-hashed` was deleted (it duplicated the pseudocode; the two paragraphs
about deterministic tie-breaking and the swap test were kept and now refer to
`first_conflict_hashed` in the code file), `sum_of_costs`/`makespan` were dropped
from `lst:ch07-costs`, and roughly forty sentences were tightened throughout
(roadmap, walkthrough, NP-hardness proof idea, feasibility sketch, three
dimensions, kinematics, dronebox, summary bullets). The definitions, the worked
example, the benchmark section, the map-family table, the three pitfall boxes,
`prop:ch07-hierarchy`, `fig:ch07-conflict-growth` and `exr:ch07-separation` were
all preserved.

Result: the chapter body went from 20 pages (PDF 13–32 in the round-1 build) to
**19 pages** (PDF 13–31), not 18. The remaining page is not prose: the last page
carries only about 1700 characters, and a further round of sentence-level
tightening (about 1000 characters) moved the last page by only 150 characters,
because the chapter is float-bound, not text-bound — 6 figures, 3 tables, 2
algorithms, 2 listings and 7 boxes occupy roughly 4.2 of the 19 pages. Reaching
18 would require deleting two more floats, and the only unprotected candidates
left are `fig:ch07-lattice` (the 3D flight lattice, the drone section's only
figure) and `lst:ch07-costs` (the stay-at-target `position`/`path_cost` code that
the pitfall box and the glossary refer to). Both were tried and then restored:
each on its own does not save a page, and cutting both to gain one page seemed a
worse chapter than being one page over. Float placement was also loosened from
`[tb]` to `[!htb]` to pack the pages tighter, which did not change the count.

**Suggestions.** Applied: `exr:ch07-objectives`(c) now says "the shortest paths of
all three agents are unique"; `exr:ch07-horizon`(a) is restated in the two steps
the reviewer describes (padded plans, then legal plans); `exr:ch07-coding` was
split into a detector/validator exercise and a new prioritized-planning exercise
`exr:ch07-prioritized` (nine exercises now, and the dronebox cites both);
solutions were added for `exr:ch07-objectives`(b), `exr:ch07-horizon`(b) and
`exr:ch07-corridor`(a) (seven of nine exercises now have solutions); the ninth
`.scen` field is now described as a floating-point octile distance ("4.82843
rather than the 4-connected integer of \cref{lst:ch07-files}, so parse it as a
float or skip it"); the reduction-based row cites
`surynek2010optimization`, "surveyed in \cite{felner2017search}";
`thm:ch07-bounds` was renamed `prop:ch07-bounds` (five uses updated);
`def:ch07-instance` no longer calls a four-component object a triple ("is written
$\langle G, s, g\rangle$ and consists of an undirected graph $G$, a number $k$ of
agents, and two maps"). Not applied: the Banfi, Basilico and Amigoni citation for
hardness on 4-connected grids (the entry could not be verified from here, and the
reviewer asked for it only if verifiable); and the notation table, which lives in
`frontmatter/notation.tex` and is outside this chapter's files — the symbols
$\pi_i$, $\pi_i[t]$, $\Pi$, $T_i$, $T$, $k$, $\cost(\pi_i)$, SoC and MS should be
added there in Phase 1.
