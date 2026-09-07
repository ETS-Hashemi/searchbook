# Review of Chapter 11 (M*, Push-and-Swap, Push-and-Rotate) - round 2

Reviewed against `STYLE_GUIDE.md` section 9 (categories A-H), `docs/specs/ch11.md`,
`docs/core-idea.txt`, the round-1 review with the reviser's response
(`reviews/ch11-round1.md`), the six figure files in `Overleaf/figures/ch11/`, the code
`Overleaf/code/ch11_mstar.py` with its three generators in `Overleaf/code/figures/`, the data
files `Overleaf/figures/data/ch11-expansions.dat` and `ch11-state-space.dat`, and the appendix
files `Overleaf/appendices/solutions/ch11-solutions.tex`,
`Overleaf/appendices/glossary/ch11-terms.tex` and `Overleaf/appendices/appA-study-plan.tex`.

**Round-1 items.** All eight required changes of round 1 were verified individually and all
eight are correctly resolved; none is re-raised below. Specifically: (1) the "612 candidates"
sentence now gives the right reason and the right average; (2) `thm:ch11-linear` now says
$T$ expansions and the proof ends with "$v_f$ is never expanded" (I re-ran the corridor check:
`expansions == 5` for a makespan-5 policy path); (3) the cost convention is now restricted to
the joint-\astar/\mstar plans and carries the 26-vs-27 counterexample (code: `active_cost` 26,
`sum_of_costs` 27); (4) Step 2 of `thm:ch11-optimal` now opens with the contradiction
hypothesis, which repairs the argument (with the hypothesis, "every node generated with
$f \le C^*$ is expanded" is a correct consequence of popping the smallest key); (5)
`alg:ch11-pas` binds $b$ to "the agent occupying the next vertex of $p$" and the resolve line
matches; (6) exercise 11.2 and its solution now match the code exactly on the substance
(expansion 5, the $b \to d$ move, $C(v_s) = \set{1,2,3}$ at expansion 6, failure after 12
expansions / 84 candidates - all re-derived here, see required change 2 for the one residual
slip); (7) exercise 11.6(c) now asks for "exactly three time steps" with a correct pairing;
(8) the Week-5 sentence of exercise 11.7 agrees with `appA-study-plan.tex`.

**Build.** `./build.sh ch11-mstar-push-and-swap` produces
`build/only-ch11-mstar-push-and-swap.pdf` (44 pages) with no `!` errors, no undefined
reference or citation belonging to this chapter, and three overfull hboxes of 8.08 pt,
6.85 pt and 1.63 pt (all below the 15 pt threshold). The script exits with status 12 because
latexmk treats the 41 unresolved *cross-chapter* references (`ch:ch07`, `ch:ch08`, `ch:ch10`,
`ch:ch12`, `ch:ch18`, `ch:ch24`, `ch:appA`, ...) as an error in a clean tree; this is an
artefact of the `\includeonly` build in a tree without the other chapters' `.aux` files, not a
defect of the chapter, and needs no action from the reviser.

**Code.** `python3 code/ch11_mstar.py` runs in a few seconds and every `assert` passes:
worked example M\* 31/127 cost 15, joint \astar 24/612, OD 100/292, ID 27/162 with groups
`[[2],[0,1]]`; swap example 14 moves, makespan 14, sum of costs 27; push example 8 moves. I
re-derived independently: the trace rows 1-8 and 24-31 of `tab:ch11-trace` (config, $C$,
$\gcost$, $\hcost$, new successors), the 55/19 configuration counts, every entry of
`tab:ch11-sizes` ($54^k$, $54^{\underline{k}}$, $5^k$, $400^k$), every number quoted from
`ch11-expansions.dat` (medians 140/77 000, OD below 360, means 132 000 / 1 100 / 14 000 /
42 000, 63.7 -> 29.6, 2.8 and 3.8, common sets 30/30/30/29/27, OD median ratio 216 and mean
ratio 119), and the claims of `fig:ch11-joint-graph` (12 states, 18 joint moves, 3 swap edges,
optimal cost 7). `lst:ch11-core` is 45 lines and every line is verbatim from
`code/ch11_mstar.py`. All 16 citation keys resolve to entries in `references.bib`,
`bib/ch07-extra.bib` or `bib/ch11-extra.bib`, and the details of the five anchor entries
(Wagner & Choset IROS 2011 pp. 3260-3267; AIJ 219:1-24; Luna & Bekris IJCAI 2011 pp. 294-300;
de Wilde et al. JAIR 51:443-492; Standley AAAI 2010 pp. 173-178) are correct.

**Length.** The chapter occupies printed pages 36-56, i.e. 21 pages, one over the 20-page
ceiling of the brief; page 56 carries five lines of exercise text. See required change 3.

## Verdict

**Minor revision.** The chapter is technically accurate, complete against the spec and the
training plan, and every number in it is reproduced by the code. Three defects remain, and all
three are local: two sentences in the first two sections, one clause in one solution, and about
fifteen lines of duplicated prose to trim. Nothing has to be restructured, re-derived or
re-computed.

## Required changes

1. **Location:** `\section{Why this matters for a drone swarm}` (`sec:ch11-motivation`), tex
   lines 53-57, "Push-and-Swap and Push-and-Rotate never search the joint space: they move the
   agents one at a time with a handful of \emph{primitives} and find a plan, in polynomial
   time, whenever one exists and at least two cells are empty"; and
   `\section{The idea in plain words}` (`sec:ch11-intuition`), tex lines 123-125, "These rules
   never look at the cost of the plan; their value is that they always terminate and find a
   plan whenever one exists on a graph with two empty vertices."
   **Problem:** both sentences assert completeness for Push-and-Swap, which the chapter itself
   withdraws eight pages later: \cref{sec:ch11-constructive} says Luna and Bekris only *state*
   that guarantee and that "de Wilde, ter Mors and Witteveen later found instances in this
   class on which the published algorithm fails", and `thm:ch11-par` and the summary bullet
   correctly give the guarantee to Push-and-Rotate alone. As written the reader of the first
   two pages is told something that the rest of the chapter contradicts, and the training
   plan's "good conceptual contrast to CBS" is exactly the point where such a claim must be
   exact.
   **Fix:** (i) in `sec:ch11-motivation`: "... they move the agents one at a time with a
   handful of \emph{primitives} and run in polynomial time; Push-and-Rotate finds a plan
   whenever one exists and at least two cells are empty (\cref{sec:ch11-constructive} says what
   the original Push-and-Swap missed)."; (ii) in `sec:ch11-intuition`: "... their value is that
   they always terminate, and that Push-and-Rotate finds a plan whenever one exists on a graph
   with two empty vertices."
   **Category:** A (also C).

2. **Location:** `Overleaf/appendices/solutions/ch11-solutions.tex`,
   `\begin{solution}{exr:ch11-collision-sets}`, the sentence "The three legal ones enter \Open
   with $\gcost = 2$ and $\fcost = 5$ for $(a, b, d)$ and $(b, c, d)$ ... and $\fcost = 6$ for
   the joint wait."
   **Problem:** contradicted by the chapter's own code. The joint wait *is* the start
   configuration $(a, c, d)$, whose $\gcost$ is already $0$, so the relaxation
   (line~\ref{alg:ch11-mstar:relax}) fails and nothing is queued for it; only two successors
   enter \Open. Running the chapter code on this instance
   (`Graph.from_edges([("a","b"),("b","c"),("b","d")])`, starts `a,c,d`, goals `c,a,d`,
   `mstar(inst, trace=True)`) gives exactly two recorded successors at the second expansion,
   not three, and no node of the run ever has $\fcost = 6$. Everything else in the rewritten
   solution checks out against the trace.
   **Fix:** replace the sentence by "Two of them enter \Open with $\gcost = 2$ and
   $\fcost = 5$: $(a, b, d)$ and $(b, c, d)$ (one agent moves, the other waits away from its
   goal, agent~3 rests at its goal for free). The joint wait leads back to the start itself,
   whose $\gcost$ is already $0$, so it is generated but never queued - a useful reminder that
   a limited neighbour is not automatically a new node."
   **Category:** A (also E).

3. **Location:** whole chapter; concretely `\subsection{Feasibility is not optimality}`
   (`sec:ch11-quality`), tex lines 970-974, and the paragraph *Phase 3: the patch*
   (`sec:ch11-example`), tex lines 553-562.
   **Problem:** the chapter is 21 printed pages (36-56) against the 20-page ceiling, and page
   56 holds only five lines. The overflow is covered several times over by duplicated prose:
   (i) the closing sentence of `sec:ch11-quality` ("What the methods buy with this is speed on
   instances that are hopeless for optimal solvers: hundreds of agents on a graph with only a
   few free vertices, where \cbs would face an astronomical constraint tree and \mstar a
   collision set containing everyone.") repeats the "typical use" column of
   `tab:ch11-comparison` ("dense, puzzle-like instances; any feasible plan") and the dronebox
   sentence about the dense hangar; (ii) the middle of *Phase 3* ("Each is expanded with an
   empty collision set first; its policy successor is a swap or a vertex collision, so the node
   is re-opened and expanded again with $C = \set{1,2}$ (steps~5--8)" and "At $\fcost = 14$ the
   search tries the bay at the wrong time and lets drone~2 wander into the passage $(4,2)$;
   nothing there is cheaper than 15") repeats rows 5-8 and the 9--24 summary row of
   `tab:ch11-trace` almost word for word.
   **Fix:** delete (i) entirely and reduce (ii) to its two load-bearing sentences (what an
   $\fcost = 13$ node means, and "Twelve of the 31 expansions are such second expansions; other
   nodes inherit $\set{1,2}$ from a policy successor that already carries it"), then re-run
   `./build.sh` and confirm the chapter ends on page 55. Do **not** buy the space anywhere
   else: no content required by `docs/specs/ch11.md` may be cut, and the passages named on the
   "must be kept" list below are off limits.
   **Category:** G.

## Suggestions

* `alg:ch11-pas`: the outer loop is `\ForEach{agent $a$ in a fixed order}` while
  line~`alg:ch11-pas:resolve` says "schedule it to be solved again" and the prose calls it a
  queue. One word fixes the mismatch: "\ForEach{agent $a$ taken from a queue $Q$, initially all
  agents in a fixed order}" (and "append it to $Q$" in the resolve line).
* `thm:ch11-par` and `def:ch11-cost`, `def:ch11-joint`, `def:ch11-limited`,
  `thm:ch11-heuristic` are never `\cref`-ed. The Push-and-Rotate theorem in particular deserves
  a pointer from the "Complete?" discussion above `tab:ch11-comparison` ("Push-and-Rotate also
  terminates ... (\cref{thm:ch11-par})").
* Caption of `fig:ch11-push-swap`(a): "c moves first, then b, then a walks through" is the
  figure's numbering, but `PushSwapState.push` in the chapter code lets $a$ take its free step
  $v_0 \to v_1$ *before* the chain shift (`st3.moves[1:3]` is the shift). Either say "the two
  blockers shift, and $a$ walks through: six moves in all" or add "the code lets $a$ take its
  free steps first".
* The solutions file covers four of the eight exercises, which matches the rest of the book
  (ch01-ch10 have 0-4). If one more is added, `exr:ch11-reexpansion` is the one a lone reader
  is most likely to get wrong, because part (a) needs the distinction between a collision among
  a node's own successors and a set handed up by line~`alg:ch11-mstar:bpchild`.
* `sec:ch11-experiment`: consider naming the cap ("1.5 million successor candidates") in the
  caption of `fig:ch11-expansions` as well, since the survivorship sentence in the text refers
  to it and the figure is read on its own.

## What must be kept

Everything the round-1 review protected has survived and must continue to: the three-drone
aisle instance of `ex:ch11-aisles` with its four-phase narrative, `tab:ch11-trace`,
`fig:ch11-search-graph` and the "four searches compared" paragraph, all of which I reproduced
number for number from `ch11_mstar.py` (31/127, 24/612, 100/292, 27/162, cost 15, makespan 7,
55 configurations touched, 19 with $C = \set{1,2}$, 12 second expansions); the distinction
between vertex collisions (a property of the configuration) and swap collisions (a property of
the move) together with its pitfall box, still the clearest statement of that point I know in
print; `thm:ch11-terminates` and the three-step structure of the optimality sketch, which is
now correct as well as readable; the independence-detection proposition with its restriction
argument; the honest treatment of Luna and Bekris's claim and de Wilde et al.'s
counterexamples; `sec:ch11-quality` with its 27-versus-14 comparison; and
`tab:ch11-comparison`, which remains the single most useful page of the MAPF part of the book.
Two further things earned their place in this round: `fig:ch11-joint-graph` (12 states, 18
joint moves, three deleted swap edges, optimal cost 7 - all verified independently here), and
the sober `sec:ch11-experiment` discussion of medians against means, including the survivorship
warning added in round 1, which teaches a reader more about benchmarking than most chapters of
this kind manage. The bibliography again needs no work.

## Response to review (round 2)

All three required changes were applied; the two suggestions that cost nothing and the two that
cost a line were applied as well. Every number quoted in the chapter and in the solutions was
re-checked against `code/ch11_mstar.py`, whose self-test still passes unchanged
(`31/127`, `24/612`, `100/292`, `27/162`, cost 15, makespan 7; swap example 14 moves,
makespan 14, sum of costs 27, optimum 7/14).

**Required 1 (A) - the completeness claim on the opening two pages.** Applied exactly as
prescribed. `sec:ch11-motivation` now reads "... they move the agents one at a time with a
handful of *primitives* and run in polynomial time; Push-and-Rotate finds a plan whenever one
exists and at least two cells are empty (\cref{sec:ch11-constructive} says what the original
Push-and-Swap missed)", and `sec:ch11-intuition` "... their value is that they always
terminate, and that Push-and-Rotate finds a plan whenever one exists on a graph with two empty
vertices". The chapter now attributes the guarantee to Push-and-Rotate alone in all four places
(motivation, intuition, `thm:ch11-par`, summary bullet, `tab:ch11-comparison`).

**Required 2 (A) - the phantom third successor in the collision-set solution.** Confirmed
against the code before editing: `mstar(inst, trace=True)` on `Graph.from_edges([("a","b"),
("b","c"),("b","d")])` with starts `a,c,d` and goals `c,a,d` records exactly two successors at
expansion 2, `(a,b,d)` and `(b,c,d)`, both with g = 2 and f = 5; the run's f values are
{4, 5, 8}, so no node ever has f = 6. The sentence was replaced by the one you proposed
(two successors enter Open; the joint wait is the start itself, whose g is already 0, so it is
generated but never queued). The rest of that solution - expansion 5, the `b -> d` move,
C(v_s) = {1,2,3} at expansion 6, failure after 12 expansions and 84 candidates - was re-derived
from the same run and left as it stands.

**Required 3 (G) - one page over the ceiling.** Both named duplications were removed: the
closing "what the methods buy with this is speed ..." sentence of `sec:ch11-quality` is gone
entirely, and *Phase 3* is reduced to the two load-bearing sentences (with "such second
expansions" rephrased to "second expansions, of a node whose collision set grew after it had
already been expanded", because the code shows that 5 of the 12 got their set handed up from a
child rather than from their own policy successor - 7 of 12 own-successor, 5 of 12 via
line `alg:ch11-mstar:bpchild`). That alone did not clear the page, so the space was bought from
further duplication and from wording only, never from content: the "scales with" sentence above
`tab:ch11-comparison` (a verbatim repeat of the table caption), the two pointers in *Relatives*
that Further reading already carries (Standley 2011, BIBOX - both citations survive in Further
reading), the drone box's independence-detection recipe (already the ID section and a summary
bullet) and its Week-5 sentence (already in the motivation and in the coding exercise), and
tighter wording in the coding exercise, the last exercise and Further reading. In addition, and
with no loss of content, `fig:ch11-search-graph` was tightened vertically (y = 1cm -> 0.86cm),
`fig:ch11-example` scaled 0.82 -> 0.77 and `fig:ch11-joint-graph` regenerated with a slightly
smaller lattice (STEP 1.55 -> 1.44; it still prints 12 states, 18 joint moves, 3 deleted swap
edges, optimal cost 7), and the floats were given `[!tb]`/`[!htb]` so that LaTeX may pack two
of them on a page. Nothing on the "must be kept" list was touched: `ex:ch11-aisles` and its
four phases, `tab:ch11-trace`, `fig:ch11-search-graph`, the "four searches compared" paragraph,
the vertex/swap distinction and its pitfall box, `thm:ch11-terminates` and the optimality
sketch, the ID proposition, the Luna-Bekris/de Wilde treatment, `sec:ch11-quality`'s 27-vs-14
comparison, `tab:ch11-comparison`, `fig:ch11-joint-graph` and `sec:ch11-experiment` are all
intact.

**Suggestions.** `alg:ch11-pas` now reads "\ForEach{agent $a$ taken from a queue $Q$, initially
all agents in a fixed order}" with "append it to $Q$" at line `alg:ch11-pas:resolve`.
`def:ch11-joint`, `def:ch11-cost` and `thm:ch11-heuristic` are now `\cref`-ed from the preamble
of `sec:ch11-properties`, `def:ch11-limited` from the implementation notes, and `thm:ch11-par`
from the "Complete?" discussion above `tab:ch11-comparison`. The caption of
`fig:ch11-push-swap`(a) now says "the two blockers shift and $a$ walks through", which no
longer contradicts `PushSwapState.push`. The caption of `fig:ch11-expansions` names the cap of
1.5 million successor candidates (the value of `CAP` in `gen_ch11_expansions.py`). A fifth
solution was added for `exr:ch11-reexpansion`, with the 7/5 split of the twelve second
expansions and the two expansions of the start (steps 1 and 4) taken from the trace.

**Build note.** Confirmed. `./build.sh ch11-mstar-push-and-swap` exits 12 on the *first* run in
a tree whose `build/` holds no other chapter's `.aux`: latexmk stops after one pdflatex pass
because the pass returns 1 on unresolved cross-chapter references. Running it a second time
converges and exits 0, with no `!` errors, no undefined citation and no undefined reference of
this chapter (only `ch:chNN`/`ch:appX`, as expected under `\includeonly`).

**Page count, measured.** The shared `Overleaf/build/` directory is written by several chapter
builds at once here, and its `.aux` state changes the float packing of this chapter by up to
half a page from run to run, so the count was settled with a private output directory
(`latexmk -pdf -outdir=<tmp> -jobname=iso-ch11` on `\includeonly{chapters/ch11-mstar-push-and-swap}`,
two passes, exit 0). In that deterministic build the chapter is **20 printed pages** and its last
page is full - the exercises end at the bottom of it, with no five-line tail. Getting the last
three lines back needed a little more than the two prescribed deletions, all of it wording:
the coding exercise, `exr:ch11-reexpansion`, `exr:ch11-swap-count`, `exr:ch11-id-groups` and
`exr:ch11-unsolvable` were tightened without dropping a single part of any of them, and Further
reading lost six words while keeping every citation. All eight exercises, all their parts, and
every element the specification asks for are still there.
