# Review of Chapter 6 (Anytime Search: ARA*) - round 1

Reviewed artefacts: `Overleaf/chapters/ch06-arastar.tex` (1353 lines);
`Overleaf/figures/ch06/{idea,incons,example,anytime,deadline}.tex`;
`Overleaf/code/ch06_arastar.py` and `Overleaf/code/figures/{gen_ch06_anytime.py,gen_ch06_example.py}`;
`Overleaf/figures/data/ch06-anytime.dat`; `Overleaf/appendices/solutions/ch06-solutions.tex`;
`Overleaf/appendices/glossary/ch06-terms.tex`; `Overleaf/references.bib` and
`Overleaf/bib/ch06-extra.bib`; against `STYLE_GUIDE.md` §9 (A-H), `docs/specs/ch06.md`
and `docs/core-idea.txt` (Week 2, optional second half).

Checks performed: `./build.sh ch06-arastar` -> status 0, no `!` errors, no undefined
reference or citation belonging to this chapter (the only `??` are `ch:ch11/13/14/17/18/19/20/21/24/25`,
which is expected in a single-chapter build), and the only overfull box of the run
(29.1 pt) is in the book-wide list of algorithms and comes from a Chapter 16 caption,
not from this chapter. `python3 code/ch06_arastar.py` passes in 0.33 s.
`python3 code/figures/gen_ch06_anytime.py` reproduces `ch06-anytime.dat` byte-identically.
I re-ran the worked example, dumped the full expansion trace, re-derived the octile
values by hand, hand-executed the two exercise graphs, and re-checked every proof line
against Likhachev, Gordon and Thrun (NIPS 2003) and Likhachev et al. (AIJ 172(14), 2008).

## Verdict

**Minor revision.** The technical core is unusually solid: the pseudocode is the
canonical ARA*, the suboptimality theorem and the certificate proposition are correctly
stated *and* correctly proved (including the INCONS case that most treatments skip), and
every number in the worked example, the trace table, the experiment table, both
experiment figures and the deadline figure is reproduced exactly by the committed code.
All required changes below are local edits: three misstated sentences (two of them
cross-chapter claims about weighted A*), one vacuous verification claim, one notation
clash with the front matter, and about two pages of duplication to compress.

## Required changes

1. **§6.2.2 `sec:ch06-restart`, lines 107-108 - the weighted-A* bound needs consistency, not admissibility.**
   *Problem:* "The price is bounded: with an admissible heuristic the returned path costs
   at most $w \cdot C^*$." In this chapter weighted A* *is* `ImprovePath`, which never
   re-opens a closed state, and for that variant admissibility alone does **not** give the
   bound. `chapters/ch04-astar.tex` line 793 states `thm:ch04-weighted` for weighted A*
   *with re-opening*, and lines 812-818 of the same chapter say explicitly that the bound
   survives without re-opening only when $\hcost$ is consistent. Theorem `thm:ch06-bound`
   of this chapter needs consistency in Case 2, and `exr:ch06-proof`(c) exhibits an
   admissible-but-inconsistent instance where the bound fails. As written the sentence
   contradicts both chapters.
   *Fix:* replace with "The price is bounded: when $\hcost$ is consistent the returned path
   costs at most $w\,C^*$ even though closed states are never re-opened, which is the case
   \cref{thm:ch06-bound} proves below; with a merely admissible $\hcost$ the bound needs
   re-opening (\cref{thm:ch04-weighted}), and \cref{exr:ch06-proof} shows what breaks."
   *Category:* A.

2. **§6.2.2, lines 108-110 - the quoted Chapter 4 speed-up is wrong for the 4-connected grid.**
   *Problem:* "On the random grids of \cref{ch:ch04}, $w = 2$ cut the effort by a factor of
   about ten while lengthening the paths by $6$--$12\,\%$." Chapter 4
   (`sec:ch04-experiment`, lines 828-838) reports A* at 756 expansions (4-connected) and
   3324 (8-connected), and weighted A* with $w=2$ at 372 and 271: factors of 2.0 and 12.3.
   "About ten" holds only for the 8-connected grid; the reader who checks Chapter 4 finds a
   factor of two.
   *Fix:* "On the random grids of \cref{ch:ch04}, $w = 2$ cut the effort from $3\,324$ to
   $271$ expansions on the 8-connected grid and from $756$ to $372$ on the 4-connected one,
   while lengthening the paths by $6$ and $12\,\%$ respectively."
   *Category:* A.

3. **§6.9 `sec:ch06-implementation`, line 1073 - the self-test description does not match what the code prints.**
   *Problem:* "The self-test runs \arastar with the schedule $3, 2, 1.5, 1$ on 80 random
   $24 \times 18$ grids, half of them 4-connected". Running the file prints
   `self-test passed: 202 published paths on 55 grids checked against optimal A*`: the loop
   (`for k in range(80)`, `code/ch06_arastar.py` line 375) draws 80 instances at obstacle
   density 0.25, of which 55 are solvable and carry the path/bound checks; on the other 25 it
   only asserts that nothing is published. A reader running the code sees "55", not "80".
   *Fix:* "...on 80 random $24 \times 18$ grids with a quarter of the cells blocked, half of
   them 4-connected; on the 55 solvable ones it checks against an independent \astar that ...,
   and on the rest that nothing is published."
   *Category:* A.

4. **§6.9, line 1077 - "the first iteration coincides with weighted \astar" is verified by construction, not by a test.**
   *Problem:* the sentence lists this among the properties the self-test "checks", but
   `weighted_astar()` (`code/ch06_arastar.py` lines 269-275) is literally
   `next(iter(ARAStar(grid, start, goal, schedule=(eps,)).run()), None)`, so the assertion
   `wa.cost == sols[0].cost and wa.expansions == sols[0].expansions` (line 411-412) cannot
   fail and verifies nothing. The same routine supplies the "restarted weighted \astar"
   baseline of \cref{tab:ch06-experiment} and \cref{fig:ch06-anytime}; that is a fair
   baseline (identical tie-breaking, no re-expansions), but the chapter must not present it
   as an independent check.
   *Fix:* either (preferred, one line) state the relation instead of the check:
   "weighted \astar is \arastar with a one-element schedule --- that is exactly how
   \code{weighted\_astar()} is implemented, so the first iteration and the restarts of
   \cref{sec:ch06-experiment} use the same code path and the same tie-breaking as \arastar
   itself"; or write an independent weighted-A* loop (own heap, key $\gcost + w\,\hcost$, no
   re-opening) and keep the assertion.
   *Category:* A.

5. **Notation clash with `Overleaf/frontmatter/notation.tex` line 82.**
   *Problem:* the notation table reads "$\eps$ & inflation factor of \arastar; $w=1+\eps$ in
   $\astar_\eps$ & \cref{ch:ch06}". Chapter 6 uses $\eps$ as the multiplier itself
   (\cref{def:ch06-key}, bound $\eps\,C^*$) and never mentions the $1+\eps$ convention, so
   the table sends the reader of this chapter to a second, unexplained convention and
   mis-attributes it to \arastar.
   *Fix:* either shorten the notation line to "$\eps$ & inflation factor of \arastar, key
   $\gcost+\eps\hcost$, bound $\eps\,C^*$ & \cref{ch:ch06}" and move the $\astar_\eps$
   remark to the focal-search row of \cref{ch:ch10}; or, if the front matter must stay,
   add one sentence after \cref{def:ch06-key}: "Pearl and Kim's $\astar_\eps$
   \cite{pearl1982studies} writes the slack as $\eps$, so that its bound reads $1+\eps$;
   here $\eps$ is the multiplier itself." Do one of the two, not both.
   *Category:* F.

6. **Length: the chapter body is 20 pages (pp. 19-38 of `build/only-ch06-arastar.pdf`).**
   *Problem:* STYLE_GUIDE §2 allows 12-18 pages and `docs/specs/ch06.md` targets 11-13. The
   excess is not missing-content overrun but four identifiable duplications; no required
   content need be dropped.
   *Fix (about two pages, all compressions):*
   (a) lines 427-452, "First iteration, $\eps=3$": the paragraph re-narrates \cref{tab:ch06-trace}
   step by step. Keep the three turning points (the greedy dive to $(4,2)$; the wall and the
   fall-back to keys around 17; step 12 and the \textsc{Incons} event) and the certificate
   computation; delete the retelling of steps 13-17, which the table already gives row by row.
   (b) lines 831-857, "Five observations": items 1 and 3 restate columns of
   \cref{tab:ch06-experiment}. Merge them into one sentence and keep items 2, 4 and 5, which
   add reasoning the table cannot carry.
   (c) lines 860-899: the prose of §6.7.2 and \cref{tab:ch06-schedule} make the same five
   points in the same order ($\eps_1$ large, $\eps_1=2$-$3$, one jump, small decrement,
   adaptive rule). Keep the table and reduce the prose to what the table cannot say (why a
   greedy dead end costs more than it saves, and where the adaptive rule comes from).
   (d) lines 1143-1160, "Three practical rules": "Fly the first path" and "Read the
   certificate, not $\eps$" repeat summary bullets 4 and 6; compress to two sentences and
   keep "Search backward when the start moves", which is the only one that is new.
   *Category:* G.

## Suggestions

* `appendices/solutions/ch06-solutions.tex` answers 4 of the 7 exercises
  (`bound`, `proof`, `incons`, `coding`). Add short solutions for `exr:ch06-trace`,
  `exr:ch06-schedule` and `exr:ch06-deadline`; the numbers exist already (e.g. the adaptive
  rule of `exr:ch06-schedule`(d) yields the schedule $3 \to 1.45 \to 1$ with 17, 13 and 2
  expansions, $\eps' = 1.65, 1.16, 1.00$ - I verified this by running `ARAStar` with that
  schedule).
* §6.7.2, lines 876-884 already gives the complete answer to `exr:ch06-schedule`(d)
  (13 expansions, certificate 1.16, then two expansions). Move those numbers to the solution
  and let the section state only the rule, or reword the exercise to ask for a different
  $\Delta$.
* §6.5, line 540: "Plain \astar with the same tie-breaking needs 22 expansions". A reader who
  runs `astar_reference()` gets 25 (that routine uses its own tie-breaking); name the call
  that gives 22, e.g. "(`weighted_astar(grid, s, gamma, 1.0)` in the code)".
* Caption of \cref{fig:ch06-incons}: "cost $1 + 2\sqrt{2} = 3.83$" and "cost 3" are
  $\gcost$-values measured from $s$, not the cost of the two-move segment from $(1,3)$.
  Write "$\gcost = 1 + 2\sqrt{2} = 3.83$" and "$\gcost = 3$" to avoid the ambiguity.
* Proof of `thm:ch06-pointer`: the acyclicity argument is compressed to one clause. Spell it
  out: consider the moment the closing pointer of a hypothetical cycle was set; the
  relaxation is strict there, while telescoping $\gcost(\mathrm{parent}) + c \le \gcost$
  around the cycle forces every inequality to be tight - a contradiction.
* `def:ch06-certificate`: add one clause noting that $\gamma$ is never expanded, so
  $\gcost(\gamma) < \infty$ implies $\gamma \in \Open$ and hence $L \le \gcost(\gamma) < \infty$
  and $\eps' \ge 1$; the "$L = \infty$" branch can only coincide with the failure exit
  (line~\ref{alg:ch06-main:fail}). This is what `_bound()` guards with `max(1.0, ...)`.
* STYLE_GUIDE §3 asks for every acronym to be expanded at first use in each chapter; §6.1
  uses CBS, ECBS, ORCA and DWA unexpanded (ARA* and AD* are correctly introduced).
* §6.7.2 could add one clause: if the schedule does not reach $\eps = 1$, the last path
  carries only its certificate $\eps'$, which is often already 1 in practice
  (\cref{tab:ch06-experiment}).
* §6.8.2 is a good short comparison. If (and only if) the bibliographic details can be
  vouched for, one clause on ANA* (which removes the schedule entirely) would round it off;
  do not add an entry otherwise.

## What must be kept

The worked example is the best I have seen in this book so far, and it must survive intact:
I dumped the algorithm's own trace and every one of the 32 rows of `tab:ch06-trace` matches
- the $\gcost$, $\hcost$ and $\fcost_\eps$ columns, the "successors improved" column
including the `I` marker in step 12, and the "$\min_{\Open}\fcost_\eps$ after the step"
column, which is the column that makes the termination test legible. The published costs
12.24 / 11.41 / 10.24, the expansion counts 17 / 4 / 11, the list sizes 8 / 10 / 9, the
lower bounds 7.41 / 8.00 / 10.24 and the certificates 1.65 / 1.53 / 1.00 in
`tab:ch06-iterations` are exactly what `ch06_arastar.py` prints, and the "the pointer path
(11.41) is cheaper than $\gcost(\gamma)$ (12.24)" effect in iteration 2 is both real and
one of the most instructive details of the chapter. The experiment is equally clean: a
fresh run of `gen_ch06_anytime.py` reproduces `tab:ch06-experiment` to the last digit
(215/0/0/1/83/435/480/328 expansions, certificate 1.412 at $\eps=3$, totals 1541 against
3963 and 1177), and the block lengths of `fig:ch06-deadline` are consistent with its stated
scale of 1 cm = 400 expansions.

Keep the proofs as they stand. The three-case induction of `thm:ch06-bound` (consistent /
in \Open / in \textsc{Incons}), with the explicit base case "for the first expansion
\textsc{Incons} is empty", is the correct and complete argument, and the remark that
consistency is used in Case 2 only, for the uninflated heuristic, is exactly the right
pointer for the reader. `thm:ch06-certificate`'s two-case proof (first inconsistent state on
an optimal path lies in $\Open \cup \textsc{Incons}$) is what makes the certificate
trustworthy, and `thm:ch06-properties`(iv) - the zero-work iteration - is the insight that
the experiment then confirms. Keep `def:ch06-inconsistent` together with the paragraph that
separates "inconsistent state" from "consistent heuristic"; that confusion is a real trap and
few texts address it. Keep all three pitfalls and, above all, the two exercise graphs: I ran
both by hand and they work as advertised - `exr:ch06-proof`(c) really returns
$\gcost(\gamma) = 5 > C^* = 4$ with the false certificate $\eps' = 1$, and
`exr:ch06-incons` really produces both INCONS failure modes at once (a cost-5.5 path
certified as optimal, and a final iteration that never reaches $C^* = 5$). Keep the AD*
subsection, whose key rule (inflate the keys of overconsistent states only, leave
underconsistent keys exact, search backward from the goal) is stated correctly, and keep the
drone framing of §6.10 - "read the certificate, not $\eps$" is the sentence an engineer will
remember.

## Response to review (round 1)

All six required changes were applied. Build status 0, no errors, no undefined
citations; `python3 Overleaf/code/ch06_arastar.py` still prints
`self-test passed: 202 published paths on 55 grids ...`. The code was not
changed, so no `.dat` file needed regenerating.

**Required change 1 (§6.2.2, the weighted-A\* bound).** Replaced the false
"with an admissible heuristic ..." sentence by the reviewer's wording: the
bound holds without re-opening when *h* is consistent (`\cref{thm:ch06-bound}`),
needs re-opening for a merely admissible *h* (`\cref{thm:ch04-weighted}`), and
`\cref{exr:ch06-proof}` shows what breaks. The chapter no longer contradicts
ch04 or its own Theorem.

**Required change 2 (§6.2.2, the ch04 numbers).** Replaced "a factor of about
ten" by the figures of ch04 §4.9 (verified against `ch04-astar.tex`
lines 828-838): 3 324 -> 271 expansions on the 8-connected grid, 756 -> 372 on
the 4-connected one, paths 6 % and 12 % longer respectively.

**Required change 3 (§6.9, the self-test).** Reworded to what the code does:
80 random 24x18 grids with a quarter of the cells blocked, half of them
4-connected; the path/bound checks run on the 55 solvable ones, and on the
other 25 the test asserts that nothing is published; the worked example is
checked separately.

**Required change 4 (§6.9, the weighted-A\* assertion).** Took the preferred
one-line option: the text now states the relation instead of claiming a check
-- weighted A\* is ARA\* with a one-element schedule, which is exactly how
`weighted_astar()` is implemented, so the first iteration and the restarts of
§6.7.1 use the same code path and tie-breaking as ARA\* itself. The assertion
in the code was left in place (it is a cheap regression guard) but is no
longer advertised as evidence.

**Required change 5 (the eps convention).** Took the second of the two
alternatives, the one that stays inside this chapter's files: one sentence
after `def:ch06-key` says that Pearl and Kim's A\*_eps writes the slack as eps
so its bound reads 1+eps, while here eps is the multiplier itself and the
bound is eps*C\*. `frontmatter/notation.tex` was left untouched (it is not a
chapter file; the finisher brief forbids editing shared front matter). Only
one of the two fixes was applied, as instructed.

**Required change 6 (length).** All four passages were compressed as
directed: (a) the "First iteration" narration keeps the three turning points
and the certificate computation and drops the retelling of steps 13-17;
(b) observations 1 and 3 are merged into a single item, 2, 4 and 5 are kept;
(c) the prose of §6.7.2 is reduced to the three things `tab:ch06-schedule`
cannot say (and the give-away numbers of `exr:ch06-schedule`(d) were moved
into the solution, per the suggestion); (d) the two practical rules that
repeat summary bullets 4 and 6 are now two clauses, "Search backward when the
start moves" is kept in full. Net effect on the body: those four passages lost
about 40 % of their prose, but the corrections above (changes 1-5) and the
accepted suggestions add roughly as much text back, so the body is 20 pages
(pp. 21-40 of `build/only-ch06-arastar.pdf`) rather than 18. Getting to 18
would mean cutting the worked example, a proof, a pitfall or an exercise --
all of them on the reviewer's "must keep" list -- so the remaining excess was
left in place rather than paid for with content.

**Suggestions.** Adopted: solutions for `exr:ch06-trace`, `exr:ch06-schedule`
and `exr:ch06-deadline` were added to
`appendices/solutions/ch06-solutions.tex` (all numbers recomputed or taken
from `ch06_arastar.py`: keys 17.41/18.24/19.90/20.00/22.49 for eps=3 and the
eps=2 re-keying 11.83 < 12.24 < ... < 16.66; the adaptive schedule
3 -> 1.45 -> 1 with 17, 13 and 2 expansions and eps' = 1.65, 1.16, 1.00;
1 000 expansions per 50 ms cycle); the give-away in §6.7.2 was removed;
§6.5 now names the call that reproduces the 22 expansions
(`weighted_astar(grid, start, goal, 1.0)`) and says the reference A\* of the
self-test breaks ties differently and needs 25; the caption of
`fig:ch06-incons` now writes g = 1 + 2*sqrt2 = 3.83 and g = 3; the proof of
`thm:ch06-pointer` spells out the acyclicity argument (last pointer set,
strict relaxation, telescoping around the cycle); `def:ch06-certificate` gains
the clause that gamma is never expanded, so L <= g(gamma) < inf and eps' >= 1,
and L = inf can only coincide with the failure exit; CBS, ECBS, ORCA and DWA
are expanded at first use in §6.1; §6.7.2 gains the clause about a schedule
that stops before eps = 1. Not adopted: the ANA\* clause in §6.8.2, which
would need a new bibliography entry -- the suggestion made it conditional, and
no entry was added rather than risk an unverified reference.
