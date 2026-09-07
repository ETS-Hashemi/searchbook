# Review of Chapter 9 (Conflict-Based Search) - round 1

Reviewed artefacts: `Overleaf/chapters/ch09-cbs.tex` (1315 lines), figures
`Overleaf/figures/ch09/{idea,example,tree,mdd,symmetry,scaling}.tex`,
`Overleaf/figures/data/ch09-scaling.dat`, `Overleaf/code/ch09_cbs.py` (616 lines),
`Overleaf/code/figures/gen_ch09_scaling.py`,
`Overleaf/appendices/solutions/ch09-solutions.tex`,
`Overleaf/appendices/glossary/ch09-terms.tex`, `Overleaf/references.bib`,
`Overleaf/bib/ch09-extra.bib`, against `STYLE_GUIDE.md` section 9, `docs/specs/ch09.md`
and `docs/core-idea.txt` (Week 4).

Build: `./build.sh ch09-cbs` exits 0, no `!` errors, no undefined label or citation that
belongs to this chapter (all `??` are cross-chapter references, which is expected in a
single-chapter build). Two overfull boxes (8.18 pt, 17.35 pt). Chapter length: PDF pages
15-34 of the single-chapter build = **20 pages** of chapter body, i.e. inside the 24-page
limit; no cuts are required and none are requested below.

Code: `python3 code/ch09_cbs.py` passes all asserts in 2.3 s. Every number of the worked
example (root costs 4/2/4 = 10, `N1`..`N6` costs, 4 expanded / 7 generated CT nodes, 9
low-level calls, optimum 12 confirmed against the joint-space solver), the rectangle-symmetry
figures (5 x 10 shortest paths, 15 expanded nodes) and every number quoted from
`ch09-scaling.dat` (success 0.92/0.75/0.58, means 55/241/622, maxima 441/1061/2398, ICBS
15/49/92 and 66/199/308, means 1.3/4.0/7.8 at k = 2/4/6) reproduce exactly. Two quoted
numbers do **not** reproduce; see required changes 1 and 2.

## Verdict

**Minor revision.** The mathematics is sound: both lemmas, the invariant, the optimality
theorem and the completeness theorem are correctly stated and correctly proved (I checked
the depth bound `Delta = k(|V| + 2|E|)(C*+2)` and the "at least one agent has not yet
arrived" step in detail), the pseudocode of both levels matches Sharon et al. (2015), the
worked example is exactly what the code produces, and every "must cover" item of
`docs/specs/ch09.md` and every Week-4 item of the training plan is present. What blocks an
Accept is a small set of *local* defects: two numbers in the text that the shipped code does
not produce, three sentences that state something factually wrong (a reversed
follower/leader, MA-CBS with B = 0, the admissibility argument for h_CG), a definition that
contradicts Chapter 7, one misleading figure caption, one overfull box and two terminology
slips. Every fix is a sentence, a number or a figure scale; nothing has to be restructured.

## Required changes

1. **`sec:ch09-complexity`, lines 668-673 ("The self-test contains a 4 x 3 maze ...").**
   Category **A**. The text claims "CBS had expanded 60,000 constraint-tree nodes after 13 s
   without finding a conflict-free node". The shipped self-test
   (`code/ch09_cbs.py:541-549`, `_test_coupled_instance`) runs `cbs(..., node_limit=2000)`
   and asserts `res.stats.expanded == 2000`; it prints
   `coupled maze: joint-space optimum 24 in 0.012 s; CBS: no answer after 2000 CT nodes
   (0.31 s)`. The numbers 60,000 and 13 s are not reproducible from anything in the
   repository, so the chapter violates the rule that quoted numbers come from running the
   code. Fix: change the sentence to the numbers the self-test prints, e.g. "... optimal sum
   of costs is 24: Dijkstra on the joint state space finds it in 0.01 s, while CBS was still
   without a conflict-free node after the 2,000 constraint-tree nodes (0.3 s) that the
   self-test allows it". (If you prefer to keep a bigger number, add the larger run to
   `gen_ch09_scaling.py` and record it in a `.dat` file - do not put it only in the
   self-test, which must stay under 10 s per the style guide.) Also update the stale comment
   in `code/ch09_cbs.py:468-469` ("CBS expands tens of thousands of CT nodes"), which is what
   the text appears to have been written from.

2. **`sec:ch09-experiment`, lines 941-945 ("it performs more low-level expansions per
   constraint-tree node (23,600 against 17,700 ...)").** Category **A**. The two numbers are
   the `icbs_lowexp` and `cbs_lowexp` columns of `figures/data/ch09-scaling.dat`
   (23576.7778 and 17724.1429), and by the definition in
   `code/figures/gen_ch09_scaling.py` (`lowexp.append(res.stats.low_level_expanded)`,
   averaged over solved instances) they are low-level state expansions **per solved
   instance**, not per constraint-tree node. Per CT node the figures are roughly 23,600/92 =
   256 for ICBS against 17,700/622 = 28 for plain CBS, so the sentence understates the
   effect by an order of magnitude and attaches the wrong unit. Fix: "... so it performs many
   more low-level expansions per constraint-tree node: at k = 12 a solved run costs 23,600
   low-level state expansions against 17,700 for plain CBS, although it expands only 92
   instead of 622 CT nodes; an MDD-based classifier avoids this."

3. **`sec:ch09-example`, lines 396-397 ("Agent a_3 follows one step behind a_1 from t = 2
   on").** Category **A**. In the root plan `a_1 = (0,1),(1,1),(2,1),(3,1),(4,1)` and
   `a_3 = (2,2),(2,1),(3,1),(4,1),(4,0)`, so at t = 2 `a_3` is at (3,1) and `a_1` at (2,1):
   `a_1` enters at t+1 the cell `a_3` occupied at t. The leader and the follower are
   interchanged; with the sentence as written the reader cannot understand why delaying
   `a_3` by one step in `N_2` makes it collide with `a_1` at three consecutive times. Fix:
   "(Agent `a_1` follows one step behind `a_3` from t = 2 on, but following is not a conflict
   in our model - this is why the one-step delay of `a_3` in `N_2` makes the two paths
   coincide.)"

4. **`sec:ch09-macbs`, lines 808-809 ("With B = 0 everything is merged at once and MA-CBS is
   joint-space A*").** Category **A**. With B = 0 MA-CBS merges *a pair* the first time it
   conflicts; agents that never conflict are never merged. Sharon et al. (2015) state that
   MA-CBS(0) is equivalent to Standley's independence detection with a joint-space search per
   conflicting group, which is not the same as one joint search over all k agents. Fix:
   "With B = 0 every pair is merged at its first conflict, so MA-CBS degenerates to
   Standley's independence detection: each group of interacting agents is solved by a
   joint-space A*, while independent agents are still planned alone. With B = infinity it is
   plain CBS."

5. **`sec:ch09-heuristics`, lines 827-828 ("A set of agents that covers every edge of the
   conflict graph must therefore pay at least its size").** Category **A** (the sentence is
   the only justification given for the admissibility of `eq:ch09-hcg`, and as written it
   does not establish it - an arbitrary vertex cover does not "pay" anything). Fix, keeping
   the same length: "Collect the agents whose cost is larger in a solution below N than in N.
   Because each cardinal conflict forces at least one of its two agents into that set, the
   set is a vertex cover of the conflict graph, so it contains at least
   `h_CG(N)` agents, each paying at least one extra unit. Hence every solution below N costs
   at least `N.cost + h_CG(N)`, and `h_CG` is admissible."

6. **`sec:ch09-problem`, line 148 ("an **edge conflict** (a swap) ...").** Category **F**
   (terminology contradicting an earlier chapter of the same book, while the paragraph
   explicitly claims to "use the MAPF model of `ch:ch07`"). `def:ch07-conflicts` follows
   Stern et al. and reserves *edge conflict* for two agents traversing the same edge in the
   *same* direction (`tab:ch07-conflict-summary`), and calls the head-on case a **swapping
   conflict**; `alg:ch07-pairwise` returns "swapping conflict". A reader who has just read
   Chapter 7 will read Chapter 9's definition as a different conflict type. Fix: keep the CBS
   name for the *constraint* but flag the clash once, e.g. "... and an **edge conflict**
   `<a_i, a_j, u, v, t>` if ...; this is the *swapping conflict* of `\cref{def:ch07-conflicts}`
   - the CBS literature calls it an edge conflict because the constraint that forbids it is an
   edge constraint. The same-direction edge conflict of `\cref{ch:ch07}` needs no separate test
   here: by `\cref{prop:ch07-hierarchy}`(a) it implies a vertex conflict." Add the same
   parenthetical to the summary bullet at line 1183.

7. **Caption of `fig:ch09-idea` (line ~99, "The high level expands the cheaper child
   first.").** Category **D**. This contradicts the point the chapter itself stresses twice
   (`sec:ch09-highlevel`: "there is no goal test at generation time"; `sec:ch09-example`: "a
   conflict-free node is not returned until it is the cheapest node in Open"), and in the
   worked example the node expanded after the root is *not* chosen by comparing the two
   children (they tie at 11 and the tie-break on conflicts decides). Fix: "... The high level
   then continues with the cheapest node of the whole queue, which may be either child or a
   node generated elsewhere in the tree."

8. **`figures/ch09/symmetry.tex`.** Category **G**. The figure produces
   `Overfull \hbox (17.34924pt too wide)` on page 50 of the build, above the 15 pt threshold
   of style guide section 7. The two scopes are 5 x 0.75 cm and 9 x 0.75 cm wide with
   `xshift=7.4cm`. Fix: set both `scale=0.7` and `xshift=6.9cm` (or wrap the picture in
   `\resizebox{\textwidth}{!}{...}`), then rebuild and confirm the box is gone. (The 8.18 pt
   overfull from `figures/ch09/mdd.tex` on page 49 is below the threshold; fixing it by
   reducing the right-hand scope's `xshift` from 6.9 cm to 6.5 cm is optional.)

9. **`sec:ch09-implementation`, "Duplicate nodes" paragraph, lines 1001-1005.** Category
   **H**. "Sharon et al. describe duplicate detection by hashing the constraint sets, and
   report that it rarely pays" attributes a specific empirical claim to
   `\cite{sharon2015cbs}` that I cannot verify from the cited paper, and the style guide
   forbids attributing details one is not certain of. Fix: either give the exact section of
   the AIJ paper, or drop the attribution: "Two branches can reach the same constraint sets
   ... Duplicate detection by hashing the constraint sets is easy to add, but such
   coincidences are uncommon; the implementation here does not detect duplicates, and the
   proofs of `\cref{sec:ch09-properties}` do not need it."

10. **Terminology "goal-occupied-later test"** (`eq:ch09-tgamma` at line 215,
    `alg:ch09-lowlevel` line ~332, listing caption line 1018, pitfall line 1128, summary line
    1186, exercise line 1298, index entry). Category **F**. Chapter 8 defines the same object
    as the **goal-stay time** `t_g` with `\index{goal-stay check}` (`ch08` lines 280, 345,
    718, 865) and the Chapter 4 glossary entry says "goal-stay test". Two names for one
    concept in consecutive chapters will confuse a reader working alone. Fix: use
    "goal-stay test" throughout Chapter 9 and change the index entry to
    `\index{goal-stay test}` (matching `\index{goal-stay check}` of Chapter 8), or, if you
    want to keep the more descriptive name, write once at line 215 "the **goal-stay test**
    (also called the goal-occupied-later test)" and index both.

11. **Acronyms ICBS (line 728) and CBSH (line 818).** Category **F**. Style guide section 3
    requires every acronym to be expanded at first use in every chapter; MAPF, CBS, CT, MDD
    and MA-CBS are expanded, these two are not. Fix: "Their algorithm, improved CBS (ICBS),
    therefore splits ..." and "... and run the high level as A* (the family is called CBSH,
    for CBS with heuristics)".

## Suggestions

* `sec:ch09-implementation`, line 957: "implements everything in this chapter in about 400
  lines" - the file is 616 lines. Say "in about 600 lines, of which some 150 are the
  self-tests".
* `code/figures/gen_ch09_scaling.py`: the docstring advertises an `S_conflicts` column that
  is never written, and the loop computes `conflicts` (with an extra `cbs(..., node_limit=1)`
  call per instance) and then discards it. Either write the column and use it in the text
  ("the number of root conflicts grows like ...") or delete the dead code and the docstring
  line.
* `sec:ch09-motivation`, line 44: "it continues with whichever alternative is cheaper" - a
  reader may take this for a greedy choice between the two children. "it keeps both
  alternatives and always continues with the cheapest world it has ever created" is one word
  longer and agrees with `sec:ch09-intuition`.
* `figures/ch09/example.tex`: the right-hand panel repeats the arrows of the left-hand panel
  exactly, so the difference between the root plan and `N_3` is carried entirely by the two
  "wait" labels; and those labels are `circle` nodes containing four characters of text,
  which TikZ blows up into large ellipses. Consider `rounded corners` rectangles, and add
  the arrival times along each route (as in `tab:ch09-timeline`) so the reader sees *when*,
  not only *where*.
* `exr:ch09-cardinal` asks the reader to classify the splits of `tab:ch09-ct`, but
  `sec:ch09-example` already answers this ("every conflict split here was cardinal"). Turn
  the first sentence into "verify, from the child costs in `\cref{tab:ch09-ct}`, that ...".
  For the `h_CG(N_2)` part, give the hint that `N_2` has four conflicts and that the reader
  may assume the three `a_1`-`a_3` conflicts are cardinal; otherwise the exercise silently
  requires six extra low-level searches by hand.
* `sec:ch09-cardinal`: the "cardinal iff both MDDs have a single cell at level t"
  equivalence is stated without a citation at the point of use; add `\cite{boyarski2015icbs}`
  to that sentence (the paper is cited two paragraphs earlier for a different claim).
* `sec:ch09-bypass`: "and has the minimum cost under it" deserves the half-sentence that
  makes it true - "because its cost equals `N.cost`, which is the minimum under
  `N.C_i`".
* `frontmatter/notation.tex` is still the Phase-1 placeholder; when it is filled in, this
  chapter's symbols (`pi_i`, `gamma_i`, `SoC`, `C*`, `<a_i, v, t>`, `N.C`, `N.cost`) should
  be added, and `example.tex` needs a third path style (it improvises
  `draw=sbGreen,line width=1.6pt` because `searchbook.sty` offers only `sbpath` and
  `sbpathalt`) - worth requesting `sbpathalt2`/`sbpathC` as a macro addition.
* Optional extra reading pointer: `\cref{sec:ch04-spacetime}` rather than the whole
  `\cref{ch:ch04}` wherever the low level is called "the space-time A* of Chapter 4"
  (lines 176, 344).

## What must be kept

The proof section is the best part of the chapter and must survive revision untouched: the
decomposition into "a split loses no solution" / "a node's cost is a lower bound" /
"the invariant of the high level" is exactly the right pedagogy, the proofs are complete
rather than gestured at, and the completeness proof does the thing most textbook treatments
skip - it actually bounds the number of nodes of cost at most `C*` by bounding the time
index of any constraint that can appear on a branch, and it states honestly (in
`rem:ch09-unsolvable`) that CBS does not terminate on unsolvable instances. Keep the worked
example in full: three agents is exactly the right size, it is reproduced line by line by
`ch09_cbs.py`, the four lessons after it (a resolution creates a new conflict, constraints
accumulate, a conflict-free node waits in Open, two optima exist) are the four things
students get wrong, and `fig:ch09-tree` plus `tab:ch09-ct` plus `tab:ch09-timeline` are a
model of how to show a search tree. Keep the corridor-versus-open-room analysis with the
15-node rectangle measurement and the coupled maze: the chapter is unusually honest about
where CBS loses to joint-space search. Keep all three pitfall boxes, the `T_max = H + 1 + D`
horizon (correctly derived and correctly implemented), the goal-stay treatment in both the
low level and the validator, and the `sec:ch09-variants` sequence cardinal ->
bypass -> MA-CBS -> CBSH -> symmetry, which ends on the one principle worth memorising:
any pair of constraint sets such that every solution satisfies at least one of them is a
legal split. The code, the certification against a joint-space optimum on 65 random
instances, and the generated scaling experiment are exactly what the Week-4 milestone asks
for.

## Response to review (round 1)

All eleven required changes were applied. Build: `cd Overleaf && ./build.sh ch09-cbs`
produces `build/only-ch09-cbs.pdf`, 41 pages, no `!` errors, no undefined
reference or citation that belongs to Chapter 9, and **no overfull hbox at all**
(previously 17.35 pt from `figures/ch09/symmetry.tex` and 8.18 pt from
`figures/ch09/mdd.tex`). `python3 code/ch09_cbs.py` passes in 2.3 s.
`code/figures/gen_ch09_scaling.py` was re-run and `figures/data/ch09-scaling.dat`
regenerated. (latexmk still exits 12 because 71 cross-chapter references are
unresolved in a single-chapter build; the style guide allows those `??`.)

### Required changes

1. **`sec:ch09-complexity`, coupled maze (A).** Done. The sentence now reads
   "...Dijkstra on the joint state space finds it in 0.01 s, while CBS was still
   without a conflict-free node after the 2,000 constraint-tree nodes (0.3 s) that
   the self-test allows it, because ...". These are exactly the numbers printed by
   `_test_coupled_instance` (`coupled maze: joint-space optimum 24 in 0.012 s;
   CBS: no answer after 2000 CT nodes (0.31 s)`). No larger run was added, so the
   self-test stays at 2.3 s. The stale comment at `code/ch09_cbs.py:466-469`
   ("CBS expands tens of thousands of CT nodes") was rewritten to match.

2. **`sec:ch09-experiment`, low-level expansions per CT node (A).** Done, with the
   reviewer's wording: "... so it performs many more low-level expansions per
   constraint-tree node: at k = 12 a solved run costs 23,600 low-level state
   expansions against 17,700 for plain CBS, although it expands only 92 instead of
   622 CT nodes; an MDD-based classifier avoids this."

3. **`sec:ch09-example`, leader and follower (A).** Done, and made explicit:
   "(Agent a_1 follows one step behind a_3 from t = 2 on -- at t = 2 it enters the
   cell (2,1) that a_3 left at t = 1 -- but following is not a conflict in our
   model; this is why the one-step delay of a_3 in N_2 makes the two paths
   coincide.)" Checked against the root paths printed by the code.

4. **`sec:ch09-macbs`, MA-CBS with B = 0 (A).** Done: "With B = 0 every pair is
   merged at its first conflict, so MA-CBS degenerates to Standley's independence
   detection~\cite{standley2010finding}: each group of interacting agents is solved
   by a joint-space A*, while agents that never conflict are still planned alone.
   With B = infinity it is plain CBS."

5. **`sec:ch09-heuristics`, admissibility of h_CG (A).** Done. `eq:ch09-hcg` now
   comes first ("Set h_CG(N) = ..."), followed by the reviewer's argument: collect
   the agents whose cost rises below N; each cardinal conflict forces one of its
   two endpoints into that set, so the set is a vertex cover and has at least
   h_CG(N) members, each paying at least one unit; hence every solution below N
   costs at least N.cost + h_CG(N).

6. **`sec:ch09-problem`, "edge conflict" vs. "swapping conflict" (F).** Done. After
   the definition on line ~148: "This is the swapping conflict of
   \cref{def:ch07-conflicts}; the CBS literature calls it an edge conflict because
   the constraint that forbids it is an edge constraint. The same-direction edge
   conflict of \cref{ch:ch07} needs no separate test here: by
   \cref{prop:ch07-hierarchy}(a) it implies a vertex conflict." (Verified that
   `prop:ch07-hierarchy`(a) is indeed the same-direction implication.) The summary
   bullet now reads "an edge conflict (the swapping conflict of
   \cref{def:ch07-conflicts}) is split into the two opposite edge constraints".

7. **Caption of `fig:ch09-idea` (D).** Done: the last sentence is now "The high
   level then continues with the cheapest node of the whole queue, which may be
   either child or a node generated elsewhere in the tree."

8. **`figures/ch09/symmetry.tex` overfull box (G).** Done: both scopes are
   `scale=0.7` and the second is `xshift=6.9cm`. The optional `mdd.tex` fix was
   applied too (inner `xshift` 6.9 cm -> 6.5 cm). The rebuilt log contains no
   overfull hbox of any size.

9. **`sec:ch09-implementation`, "Duplicate nodes" attribution (H).** Done, using
   the reviewer's replacement text; the attribution to Sharon et al. is gone.

10. **"goal-occupied-later test" vs. Chapter 8's "goal-stay test" (F).** Done, by
    both routes the reviewer offered. The term is now **goal-stay test** everywhere
    in Chapter 9 (definition site, `alg:ch09-lowlevel` walkthrough, listing caption,
    the in-listing comment, the pitfall box, the summary bullet and
    `exr:ch09-coding`), the definition site says "This is the goal-stay test of
    \cref{ch:ch08}, also called the goal-occupied-later test", and both spellings
    are indexed (`\index{goal-stay test}` and
    `\index{goal-occupied-later test}`). The comment in `code/ch09_cbs.py` was
    changed to `# goal-stay test` so the listing stays verbatim.

11. **ICBS and CBSH expanded at first use (F).** Done: "Their algorithm, improved
    CBS (ICBS)\index{ICBS}\index{CBS!improved}, therefore splits ..." and "... run
    the high level as A* (the family is called CBSH, for CBS with heuristics)".

### Suggestions

* **"about 400 lines".** Fixed to "about 600 lines, of which some 110 are the
  self-tests" (`code/ch09_cbs.py` is 616 lines; the `_test_*` block runs from
  line 505 to the end, 112 lines).
* **Dead `S_conflicts` code in `gen_ch09_scaling.py`.** Removed: the docstring
  line, the `all_conflicts` import, the `conflicts` list and the extra
  `cbs(..., node_limit=1)` call per instance. The written columns are unchanged.
* **`sec:ch09-motivation` line 44.** Rewritten to "It keeps both alternatives and
  always continues with the cheapest world it has ever created."
* **`figures/ch09/example.tex`.** The two wait markers are now rounded-corner
  rectangles reading "a_1 waits here, t = 1,2" and "a_2 waits here, t = 0,1"
  instead of `circle` nodes, and each panel carries the timing the reviewer asked
  for: which agent is in the crossing cell (2,1) at which time, and each agent's
  arrival time. The two panels are now distinguishable by their annotations
  (root: (2,1) at t = 1 by a_2 and a_3, at t = 2 by a_1, arrivals 4/2/4; N_3:
  t = 1 by a_3, t = 2 by a_2, t = 3 by a_1, arrivals 5/3/4). All numbers checked
  against the code's printed trace.
* **`exr:ch09-cardinal`.** Reworded to "Verify, from the child costs listed in
  \cref{tab:ch09-ct}, that every conflict split in \cref{ex:ch09-crossing} is
  cardinal", and the h_CG part now carries the hint that the three a_1--a_3
  conflicts of N_2 may be assumed cardinal.
* **`sec:ch09-cardinal`.** `\cite{boyarski2015icbs}` attached directly to the
  "cardinal iff both MDDs have a single cell at level t" equivalence.
* **`sec:ch09-bypass`.** The missing half-sentence added: "... and has the minimum
  cost under it, because cost(N'.pi_i) = cost(N.pi_i), which is the minimum under
  N.C_i".
* **`\cref{sec:ch04-spacetime}` instead of `\cref{ch:ch04}`.** Done at both places
  (the low-level introduction and the `alg:ch09-lowlevel` walkthrough); a pointer
  to `\cref{ch:ch08}` was added where the reservation-table analogy is drawn.
* **`frontmatter/notation.tex` and a third path style in `searchbook.sty`.** Not
  applied: both files are outside this chapter's remit. Requested additions are
  listed in the final report (`pi_i`, `gamma_i`, SoC, `C*`, `<a_i,v,t>`, `N.C`,
  `N.cost`; and an `sbpathalt2`/`sbpaththird` style so `example.tex` need not
  improvise `draw=sbGreen,line width=1.6pt`).

### One consequence to flag

Re-running `gen_ch09_scaling.py` changed one row of
`figures/data/ch09-scaling.dat`: the ICBS entry at k = 10 (success 0.83 -> 0.92,
mean nodes 48.8 -> 114.5, max 199 -> 771, low-level expansions 5,292 -> 22,468).
The cause is the 5 s wall-clock cap, which is the only non-deterministic element
of the experiment: on this machine ICBS now finishes one extra hard instance
inside the cap. Every other row is bit-identical. The text of
`sec:ch09-experiment` and the caption of `fig:ch09-scaling` were updated to the
new numbers ("15, 114 and 92", "66, 771 and 308", "92 % and 75 % for k = 10 and
12", "divide the node count by two to seven"), a sentence was added explaining
that a mean over solved instances only is not comparable when the two solvers
solve different sets, and the caveat paragraph now says that the 5 s cap makes the
success rates depend a little on the machine. The k = 12 figures quoted in
required change 2 (23,600 / 17,700 / 92 / 622) are unaffected.
