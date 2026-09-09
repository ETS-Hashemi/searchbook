# Review of Chapter 6 (Anytime Search: ARA*) - round 2

Reviewed artefacts: `Overleaf/chapters/ch06-arastar.tex` (1361 lines);
`Overleaf/figures/ch06/{idea,incons,example,anytime,deadline}.tex`;
`Overleaf/code/ch06_arastar.py`, `Overleaf/code/figures/{gen_ch06_anytime.py,gen_ch06_example.py}`,
`Overleaf/figures/data/ch06-anytime.dat`; `Overleaf/appendices/solutions/ch06-solutions.tex`;
`Overleaf/appendices/glossary/ch06-terms.tex`; `Overleaf/references.bib`,
`Overleaf/bib/ch06-extra.bib`; `Overleaf/frontmatter/notation.tex`;
`Overleaf/chapters/ch04-astar.tex` (§4.9) and `Overleaf/appendices/appA-study-plan.tex`
for the cross-chapter claims; against `STYLE_GUIDE.md` §9 (A-H), `docs/specs/ch06.md`
and `docs/core-idea.txt`.

Checks performed in this round.
`./build.sh ch06-arastar` -> status 0, no `!` errors; the only undefined references are
`ch:ch11/13/14/19/20/21` (other chapters, expected in a single-chapter build); the only
overfull box of the whole run (29.10 pt, log line 1946) is inside `only-ch06-arastar.loa`
and comes from the Chapter 16 algorithm caption "Rapidly-exploring random tree with goal
bias", not from this chapter. `python3 code/ch06_arastar.py` passes in 0.28 s and prints
`self-test passed: 202 published paths on 55 grids checked against optimal A*`.
`python3 code/figures/gen_ch06_anytime.py` and `gen_ch06_example.py` both reproduce their
committed outputs (`ch06-anytime.dat`, `figures/ch06/example.tex`) byte-identically.
I dumped the algorithm's own expansion trace and compared it row by row with
`tab:ch06-trace` (32 rows, all columns), re-ran the example under the schedules
`(3,2,1)`, `(3,1)` and the adaptive `(3,1.45,1)`, recomputed `weighted_astar` at
w = 1, 2, 3 and `astar_reference`, hand-executed both exercise graphs
(`exr:ch06-proof`(c) and `exr:ch06-incons`, including the "INCONS discarded" variant),
re-derived the octile values and the deadline-figure geometry, and re-checked every proof
line against Likhachev, Gordon and Thrun (NIPS 2003) and Likhachev et al. (AIJ 172(14),
2008).

Round-1 items: **all six were addressed**, and five of them correctly and completely.
(1) The weighted-A\* bound sentence in §6.2.2 now says the bound holds without re-opening
for a *consistent* heuristic and cites `thm:ch06-bound`, `thm:ch04-weighted` and
`exr:ch06-proof` - correct and consistent with `ch04-astar.tex` line 793 ff.
(2) The Chapter 4 numbers are now 3 324 -> 271 (8-connected, 6 %) and 756 -> 372
(4-connected, 12 %); I verified all six numbers against `ch04-astar.tex` lines 828-841,
including the pairing of the percentages with the connectivities.
(3) The self-test description now matches the code (80 grids at density 0.25, half
4-connected, checks on the 55 solvable ones, "nothing published" on the other 25).
(4) The weighted-A\* assertion is no longer advertised as an independent check; the text
states the "one-element schedule" relation instead.
(5) The $\eps$ convention is settled inside `def:ch06-key` by the permitted second
alternative.
(6) Length: the four passages were compressed, but the body is still 20 pages
(pp. 111-130 of `build/only-ch06-arastar.pdf`). I re-read those passages: the remaining
excess is content, not padding, so I do **not** require further cuts (see Suggestions for
the one genuinely content-free trim I found).

## Verdict

**Minor revision.** Everything that carries the chapter - pseudocode, three proofs, the
certificate, the worked example, the experiment, the code and the solutions - is correct,
and I could not break any of it. Every number I could reach is reproduced by the committed
code: 17/4/11 expansions, costs 12.243/11.414/10.243, $L = 7.414/8.000/10.243$,
certificates 1.651/1.530/1.000, list sizes 8/10/9, the 22 and 20 expansions of the
`weighted_astar` restarts, the 25 of `astar_reference`, the 15 expansions of the "3, 1"
schedule in the third pitfall, the adaptive schedule $3 \to 1.45 \to 1$ with 17/13/2
expansions, and all 40 numbers of `tab:ch06-experiment` and the two figures built from it.
Three required changes remain, all of them single-sentence edits: one wrong justification
for the adaptive schedule (which the chapter's own tables contradict twice), one rounding
that clashes with the same figure quoted two pages earlier, and one unexpanded acronym.

## Required changes

1. **§6.7.2 "Choosing the schedule", lines 879-882, and the last row of
   `tab:ch06-schedule`, line 903 - the justification of the adaptive rule is false, and
   the chapter's own numbers are the counter-example.**
   *Problem:* the text reads "an inflation factor above $\eps'_k$, which has already been
   achieved, cannot improve the published guarantee, so the next iteration may start at
   $\eps_{k+1} = \max(1, \eps'_k - \Delta)$", and the table row repeats it as "skips
   factors that cannot improve the guarantee". The published guarantee of this chapter is
   $\eps' = \min(\eps, \gcost(\gamma)/L)$, and it *can* improve under an inflation factor
   above $\eps'_k$, because $\gcost(\gamma)$ falls and $L$ rises. Two counter-examples are
   printed in the chapter itself: in `tab:ch06-iterations` iteration 2 runs at $\eps = 2 >
   \eps'_1 = 1.65$ and improves the certificate to $1.53$; in `tab:ch06-experiment`
   iteration 5 runs at $\eps = 1.5 > \eps'_4 = 1.412$ and improves it to $1.378$. (I
   re-ran both.) What is actually true is that $\eps_{k+1}$ is the *worst case* the next
   iteration promises, so a value at or above $\eps'_k$ promises nothing the incumbent does
   not already deliver - and a value equal to $\eps_k$ provably does no work at all
   (`thm:ch06-properties`(iv)).
   *Fix:* replace the clause by, e.g., "the inflation $\eps_{k+1}$ is only the worst case
   that the next iteration promises, so a value at or above the $\eps'_k$ already certified
   promises nothing the published path does not already deliver, and $\eps_{k+1} = \eps_k$
   provably buys nothing (\cref{thm:ch06-properties}(iv)). Starting the next iteration at
   $\eps_{k+1} = \max(1, \eps'_k - \Delta)$ therefore skips the factors whose promise is
   already kept and forces every iteration to aim at a strictly better bound. A larger
   $\eps$ may still improve the certificate in practice - the $\eps = 2$ iteration of
   \cref{ex:ch06-grid} does, from $1.65$ to $1.53$ - so the rule trades such cheap
   improvements for a faster approach to optimality." Change the table cell to "skips the
   factors whose promise the incumbent already keeps".
   *Category:* A.

2. **Pitfall "Decreasing $\eps$ too fast", line 1129 - "one within $1\,\%$" is not what the
   table says.**
   *Problem:* "in \cref{tab:ch06-experiment} a path within $7\,\%$ of optimal was available
   for $83$ more expansions and one within $1\,\%$ for $518$ more". The table gives
   $1.0698$ (6.98 %, so "within 7 %" is right) and $1.0105$ after $83 + 435 = 518$ further
   expansions - that is 1.05 %, not within 1 %. Observation 4 of §6.7.1 states the same
   figure correctly as "within $1.1\,\%$", so the chapter contradicts itself two pages
   apart.
   *Fix:* write "one within $1.1\,\%$ for $518$ more".
   *Category:* A.

3. **§6.3, line 218 - LPA\* is used without being expanded.**
   *Problem:* "The word \emph{inconsistent} is used here in the sense of \lpastar and
   \dstarlite (\cref{ch:ch05})" is the only occurrence of `\lpastar` in the chapter, and
   `\lpastar` typesets as "LPA*". STYLE_GUIDE §3 requires every acronym to be expanded at
   first use *in every chapter*; round 1 had the same problem with CBS, ECBS, ORCA and DWA,
   which were fixed, and this one was missed.
   *Fix:* "in the sense of Lifelong Planning \astar (\lpastar) and \dstarlite
   (\cref{ch:ch05})".
   *Category:* F (cosmetic).

## Suggestions

* **Proof of `thm:ch06-certificate`, line 711.** The first branch, "If every state of $P$
  is consistent", cannot occur: `def:ch06-certificate` has just established that $\gamma$
  is never expanded, so $\gamma$ is inconsistent whenever $\gcost(\gamma) < \infty$. The
  proof is still correct, because the second branch covers $u = \gamma$ and yields
  $\gcost(\gamma) = C^*$ and $L \le C^*$ together, but a careful reader will stop at the
  contradiction. Recommended rewrite: "Let $u$ be the first inconsistent state on $P$; it
  exists, because $\gamma$ is never expanded. Telescoping (ii) over the consistent states
  before $u$ gives $\gcost(u) = \gcost^*(u)$, and (iii) puts $u \in \Open \cup
  \textsc{Incons}$. If $u = \gamma$ then $\gcost(\gamma) = C^*$; in either case $L \le
  \gcost(u) + \hcost(u) \le C^*$."
* **`lst:ch06-improve`, the eleven-line `if self.trace is not None:` block.** This is
  instrumentation, not the algorithm, and it is the only content-free passage I could find
  in the chapter. Replacing it with `# (trace bookkeeping for tab:ch06-trace omitted)`
  shortens the listing by about ten lines - roughly a quarter of a page, the only
  cut I would make on length grounds. The chapter is 20 pages against the style guide's
  12-18 and the spec's 11-13, but everything else in it is required content
  (worked example, proofs, pitfalls, exercises), and content outranks length.
* **§6.5, third iteration, lines 537-540.** "the cells that the greedy first iteration
  skipped, $(1,2)$, $(2,4)$, $(2,1)$, $(1,4)$ and $(1,1)$ ... are expanded first" - the
  trace has $(4,4)$ at step 3 between them (it was expanded in iteration 1 and improved in
  iteration 2, so it is not one of the skipped cells). Write "are five of the first six
  expansions" to keep the sentence exactly true against `tab:ch06-trace`.
* **Caption of `fig:ch06-deadline`, line 1179.** It explains that the $\eps = 2.5$ and
  $2$ blocks have zero length, but not that the $\eps = 1.75$ block is a single expansion
  and therefore invisible too; a reader who counts the five labels against eight iterations
  is left one short. Add "and $\eps = 1.75$ is a single expansion wide".
* **`exr:ch06-proof`(c).** The solution notes that the pointer path happens to cost $4$
  while $\gcost(\gamma) = 5$. Add half a sentence to the exercise itself ("note which of
  the two quantities the certificate is about") so that a student who publishes an optimal
  path is not confused about having found the counter-example.
* **`references.bib`, `likhachev2003ara`.** The booktitle reads "Advances in Neural
  Information Processing Systems (NeurIPS)" for a 2003 volume, which was NIPS at the time.
  Purely cosmetic, and the file is shared, so change it only in a book-wide bibliography
  pass.
* §6.8.2 remains a good short comparison. As in round 1: an ANA\* clause would round it
  off, but only if the bibliographic details can be vouched for - do not add an entry
  otherwise. The reviser was right to decline.

## What must be kept

The worked example and its trace survive a second, independent verification: I dumped
`ARAStar(..., trace=True)` and every one of the 32 rows of `tab:ch06-trace` matches the
algorithm's own record - the $\gcost$, $\hcost$ and $\fcost_\eps$ columns, the "successors
improved" column with the `I` marker at step 12, and the "$\min_{\Open}\fcost_\eps$ after
the step" column that makes the termination test legible. `tab:ch06-iterations` is exact
(17/4/11 expansions, 12.24/11.41/10.24 published, $L = 7.41/8.00/10.24$, $\eps' =
1.65/1.53/1.00$, list sizes 8/10/9, $\textsc{Incons} = \{(3,3)\}$), and so are the
comparison numbers around it: `weighted_astar` at $w=1$ and $w=2$ really needs 22 and 20
expansions, `astar_reference` really needs 25, and $17+20+22=59$ really is what restarting
would cost. The "the pointer path (11.41) is cheaper than $\gcost(\gamma)$ (12.24)" effect
of iteration 2 is the most instructive detail in the chapter; keep it, keep
`thm:ch06-pointer` with its now fully spelled-out acyclicity argument, and keep the
sentence in `def:ch06-certificate` that $\gamma$ is never expanded, which is what makes
$\eps' \ge 1$ and the failure exit fit together.

Keep the proofs exactly as they stand (subject only to the cosmetic rewrite suggested
above). The three-case induction of `thm:ch06-bound` - consistent / in \Open / in
\textsc{Incons}, with the base case "for the first expansion \textsc{Incons} is empty" - is
the correct and complete argument, and I re-checked every inequality in Cases 1-3,
including the use of $\eps \ge 1$ and $c \ge 0$ in Case 1 and the exact place where
consistency of the *uninflated* heuristic enters in Case 2. `thm:ch06-properties`(ii)'s
completeness argument (the "first state with $\gcost = \infty$ on a cheapest path" with the
\Open-empty case) and (iv)'s zero-work iteration are both right, and (iv) is the insight
the experiment then confirms.

The experiment is fully reproducible: a fresh run of `gen_ch06_anytime.py` rewrites
`ch06-anytime.dat` byte-identically, and every entry of `tab:ch06-experiment`
(215/0/0/1/83/435/480/328 expansions; totals 215/215/215/216/298/733/1213/1541 against
215/439/683/980/1326/1916/2791/3963; certificate 1.412 at $\eps = 3$; 1 177 for one \astar,
hence the 1.3 and 3.4 factors and the 18 % first-path figure) follows from it, as do the
block geometries of `fig:ch06-deadline` (1 cm = 400 expansions, checked to three decimals).

Keep all three pitfalls, and above all the two exercise graphs, which I ran by hand again:
`exr:ch06-proof`(c) really returns $\gcost(\gamma) = 5 > C^* = 4$ with $L = 2$ and
$\eps' = 1$, and `exr:ch06-incons` really produces both INCONS failure modes on one graph -
4 expansions with $\eps = 3$ giving the pointer path of cost 7 against $\gcost(\gamma) = 8$,
$L = 3$, $\eps' = 2.67$; then 3 expansions at $\eps = 1$ reaching $C^* = 5$; and, with
\textsc{Incons} discarded, a single expansion that publishes the cost-5.5 decoy certified
as optimal. Keep `def:ch06-inconsistent` with the paragraph separating "inconsistent state"
from "consistent heuristic", the AD\* subsection (inflated keys for overconsistent states
only, exact keys for underconsistent ones, backward search - all stated correctly), and the
drone framing of §6.10; "read the certificate, not $\eps$" is the sentence an engineer will
remember. Finally, keep the solutions appendix as it now stands: all seven exercises are
answered, and I recomputed the ones that carry numbers - the per-100-expansion improvement
rates of `exr:ch06-schedule`(a), the 800- and 1 000-expansion snapshots, and the adaptive
schedule $3 \to 1.45 \to 1$ with 17, 13 and 2 expansions and $\eps' = 1.65, 1.16, 1.00$ -
and every one of them is right.
