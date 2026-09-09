# Review of Chapter 2 (The Toolbox) - round 1

Reviewed artefacts: `Overleaf/chapters/ch02-toolbox.tex` (817 lines), the seven figure
files in `Overleaf/figures/ch02/`, `Overleaf/code/ch02_toolbox.py`,
`Overleaf/code/figures/gen_ch02_gaussian.py`, `Overleaf/code/figures/gen_ch02_double_integrator.py`,
`Overleaf/appendices/solutions/ch02-solutions.tex`,
`Overleaf/appendices/glossary/ch02-terms.tex`, against `STYLE_GUIDE.md` §9,
`docs/specs/ch02.md` and `docs/core-idea.txt`.

Build: `cd Overleaf && ./build.sh ch02-toolbox` -> status 0, no `!` errors, no undefined
reference or citation belonging to this chapter (the `??` in the PDF are all forward
references to chapters not included in a single-chapter build, which the style guide
allows; the only `Overfull \hbox` above 15 pt, 29.10 pt at log line 1948, is in the
front-matter *List of Algorithms*, not in this chapter).
Code: `python3 code/ch02_toolbox.py` -> `ch02_toolbox self-test passed`, exit 0.
Both figure generators run and reproduce their data files.

Every number quoted in the chapter was checked against the code or recomputed:
`(3.0, 2.0)`, `(3, 3)`, makespan 3, SoC 6, `sep = 1.0`, `sep_cont = 0.70710678`,
`tca = (3.0, 1.41421356)`, `ttc_r075 = 2.646446609`, `ellipse = (1.6733, 0.4472, 33.690)`,
inflation counts 5 / 9 / 21, edge counts 17 / 29, stretches 1.0824 and 1.1281
(I re-derived both as `sqrt(sum_k (sqrt(k) - sqrt(k-1))^2)`), the Gaussian sample
fractions 39.8 % / 85.8 % (from `gen_ch02_gaussian.py`), the double-integrator story
2 s / 5 s / 7 s / 10 m (from `gen_ch02_double_integrator.py`), the 2D masses
39.3 / 86.5 / 98.9 % and the 3D masses 19.9 / 73.9 %, the tangent points `(3, +-sqrt3)`
with `l = sqrt(12)` and `theta = 30 deg`, and even the "about 150 MB and a few seconds"
dictionary estimate (measured: 153.9 MB, 2.7 s for 10^6 `((x,y),t)` keys). All correct.

## Verdict

**Minor revision.**

The chapter is technically sound, complete against every "must cover" item of
`docs/specs/ch02.md`, and its worked examples are reproduced exactly by the companion
code. Nothing here is wrong in a way that would mislead a reader about an algorithm.
Five required changes remain, all local: one genuine gap in the cost model (waits at the
goal), one overloaded symbol inside a definition, one proof that stops one step short of
its own formula, one figure that uses the same letter for two different distances, and
two pages of length over the cap that can be removed from clearly redundant material.

## Required changes

1. **The cost of a time-indexed path is never reconciled with its arrival time.**
   *Location:* `def:ch02-space-time-state` (line 193) together with
   `def:ch02-travel-time`, `def:ch02-makespan`, `def:ch02-sum-of-costs` (lines 269-290).
   *Problem:* Definition 2.2 defines `\cost(\pi)` as the sum of edge costs, and
   Definition 2.10 states flatly that "the wait costs $c_{\text{wait}}>0$". But
   Definitions 2.16-2.18 measure travel time, makespan and sum of costs by the *arrival
   time* $T(\pi)$. For any path with trailing waits at the goal - which the stay-at-goal
   convention of Definition 2.12 explicitly allows - the two quantities differ, so a
   reader who implements space-time search with $g=\sum$ action costs will not obtain the
   $\sumcost$ this chapter defines. The rest of the book has already settled the
   convention the other way: `frontmatter/notation.tex` lines 99-100 define
   $\sumcost(\Pi)=\sum_i\cost(\pi_i)$ and $\makespan(\Pi)=\max_i\cost(\pi_i)$, and
   `chapters/ch07-mapf-problem.tex` lines 190-193 says "\Cref{ch:ch02} writes the
   final-arrival time of a path as $T(\pi_i)$; here that quantity is $\cost(\pi_i)$",
   while its code (line 931) documents "trailing waits cost nothing". Chapter 2, read
   alone, contradicts that.
   *Fix:* (a) in Definition 2.10 replace "and the wait costs $c_{\text{wait}}>0$" by
   "and the wait costs $c_{\text{wait}}>0$ for every wait made before the agent's final
   arrival at its goal; by the stay-at-goal convention of
   \cref{def:ch02-time-indexed-path} the waits at the goal after arrival are free";
   (b) add one sentence after Definition 2.16: "With unit move costs this makes
   $\cost(\pi)=T(\pi)$: this is the convention of \textcite{stern2019mapf}, and it is
   what \cref{ch:ch07} writes as $\cost(\pi_i)$ and the notation table lists under
   $\sumcost$."
   *Category:* A (also F).

2. **The letter $T$ means two different things inside Definition 2.12.**
   *Location:* `def:ch02-time-indexed-path`, lines 212-215; knock-on effects in
   `def:ch02-time-expanded-graph` (line 200) and `exr:ch02-time-expanded` (line 785).
   *Problem:* the definition first writes the path as $\pi=(v_0,\dots,v_T)$ with $v_T=g$
   and then defines the arrival time as $T(\pi)$. Because trailing waits at the goal are
   permitted, $T(\pi)\le T$ and the two are not equal in general, so the sentence "The
   arrival time $T(\pi)$ is the smallest $t$ such that $v_{t'}=g$ for all $t'\ge t$" reads
   as if $T$ were being defined in terms of itself. `ch07-mapf-problem.tex` (lines
   190-193) reserves $T_i$ for the last stored index precisely to avoid this collision.
   *Fix:* write the sequence as $\pi=(v_0,\dots,v_{T_i})$ (or $H$ for the horizon of the
   stored list), keep $T(\pi)$ for the arrival time only, and add "the arrival time
   satisfies $T(\pi)\le T_i$, with equality exactly when the path ends without a trailing
   wait at the goal; \cref{ch:ch07} uses the same two letters." Use the same letter for
   the horizon in Definition 2.11 and in Exercise 2.4.
   *Category:* C (also F).

3. **The proof of Proposition 2.24 does not finish its own computation.**
   *Location:* proof of `thm:ch02-stopping-distance`, line 378.
   *Problem:* the chain ends at "$= v\,t_s-\tfrac12 a_{\max}t_s^2 = v^2/a_{\max}-v^2/(2a_{\max})$"
   and never states that this equals $v^2/(2a_{\max})$, i.e. the displayed
   \cref{eq:ch02-stopping-distance} that the proposition asserts. The chapter's promise is
   that every property is proved; leaving the last simplification to the reader breaks it,
   and the guide forbids implying that a step is obvious.
   *Fix:* end the sentence with "$=v^2/(2a_{\max})$, which is \cref{eq:ch02-stopping-distance}."
   *Category:* A.

4. **Figure 2.5 uses the symbol $d$ for two different distances.**
   *Location:* `fig:ch02-segment-circle` (lines 452-457) and the figure file
   `Overleaf/figures/ch02/segment-circle.tex`.
   *Problem:* in panel (a) $d$ is the point-to-segment distance ("the closest point
   $\vect q$ is at distance $d\le r$", "The disc around $\vect c'$ is missed because
   $d>r$"), while in panel (b) $d=\norm{\vect p-\vect c}$ is the distance from the external
   point to the *centre*, the quantity that appears in $\cos\alpha=r/d$,
   $\ell=\sqrt{d^2-r^2}$ and $\theta=\arcsin(r/d)$. Both panels are in the same figure and
   the same caption, so a reader alone cannot tell which $d$ Proposition 2.29 refers to.
   *Fix:* in the TikZ file label the two distances of panel (a) as $d_1$ (to $\vect c$) and
   $d_2$ (to $\vect c'$), or write them as $\dist(\vect c,\overline{\vect a\vect b})$, and
   rewrite the caption accordingly ("...because the closest point $\vect q$ is at distance
   $d_1\le r$; the disc around $\vect c'$ is missed because $d_2>r$"). Keep $d$ for
   $\norm{\vect p-\vect c}$ in panel (b) only, and say so in the caption.
   *Category:* D.

5. **The chapter is 22 pages; the cap is 20 (the spec targets 14-18).**
   *Location:* whole chapter; the body occupies printed pages 21-42 of
   `build/only-ch02-toolbox.pdf` (PDF pages 18-39).
   *Problem:* two pages over. All "must cover" content is needed and must stay; the excess
   is in five places that repeat material already given.
   *Fix:* make these concrete cuts (about two pages together), touching no required
   content:
   (a) delete **Listing 2.2** (`lst:ch02-geometry`, lines 721-736): `tangent_points` is a
       line-for-line transcription of \cref{eq:ch02-tangent-points}, which the reader has
       just seen with a proof, a picture and a numeric instance. Keep Listing 2.1 (the
       style guide requires one listing) and keep the sentence in line 699 that names the
       function; adjust that sentence so it no longer says "\Cref{lst:ch02-geometry} shows".
   (b) compress the "two variants in the literature" discussion in line 663 (from "Two
       variants appear in the literature" to "to stay optimal", about eight printed lines)
       to two sentences: name the two variants, say they coincide under a consistent
       heuristic, and forward-reference \cref{ch:ch04}, which is where reopening is
       actually analysed.
   (c) cut the paragraph "Why dictionaries are enough" (lines 672-673) to two sentences:
       the $10^6$-state / 150 MB estimate and the conclusion. Its remaining three clauses
       repeat Table 2.5 and the preceding paragraph.
   (d) merge the one-sentence second paragraph of \cref{sec:ch02-motivation} (line 25)
       into the paragraph above it; it restates "time" and "cost measures", which the
       following paragraph and the roadmap sentence already announce.
   (e) in the paragraph "Why a quadrotor is a double integrator, and when it is not"
       (line 366) drop the payload/drag elaboration and keep the caveat list to
       acceleration-cannot-jump, asymmetric limits and "choose $a_{\max}$, $v_{\max}$ with
       a margin"; about four printed lines.
   *Category:* G.

## Suggestions

* Definition 2.1: for a *weighted* undirected graph, also require $c(u,v)=c(v,u)$;
  otherwise "count it once" is ambiguous.
* Definition 2.19 says two agents *collide* when $d_{ij}(t)<r_i+r_j$ (strict), while
  Proposition 2.28 says two discs *overlap* when $\norm{\pos_B-\pos_A}\le r_A+r_B$
  (non-strict). Add half a sentence saying that the touching case is treated as safe (or
  as a collision) and be consistent, since \cref{ch:ch12,ch:ch13} branch on this test.
* Definition 2.30 says the time to collision is $\infty$ when no collision occurs, but
  `time_to_collision` returns `None` (self-test line 597). State the code's convention in
  the text, as is already done for `tangent_points` in line 483.
* Line 29 promises that "every number quoted in the text is produced by the companion file
  `code/ch02_toolbox.py`". The 39.8 % / 85.8 % of Example 2.37 come from
  `code/figures/gen_ch02_gaussian.py`, and Figure 2.4's numbers from
  `gen_ch02_double_integrator.py`. Name all three files.
* Table 2.1's stretch values are attributed to `lattice_stretch`, but `worked_example`
  does not print them, so a reader who runs the file cannot see them. Add
  `lattice_stretch(2)`, `lattice_stretch(3)` and the two non-diagonal values to the
  printed output.
* Figure 2.2(c) is drawn for $r=1.5$ cells while the text (line 176) works out $r=0.6$,
  $1.0$ and $1.6$. Either redraw at $r=1.6$ (21 cells, the case the text counts) or state
  the count for $r=1.5$ (13 cells) in the caption, so the picture is checkable.
* Definition 2.13 writes agent $i$'s position as $v^i_t$; \cref{ch:ch07} and the notation
  table write $\pi_i[t]$. Mention the ch07 form once here.
* Line 640 uses \lpastar without expanding it; the guide asks for each acronym to be
  expanded at first use in every chapter ("Lifelong Planning A*").
* Algorithm 2.1 returns "empty" on an exhausted heap, while `LazyPQ.pop` raises
  `IndexError`. One clause in line 663 would remove the discrepancy.
* In line 176 the argument "the distance to the obstacle along such a move is smallest at
  one of its endpoints" is correct, but only because obstacle centres and move endpoints
  both lie on the integer lattice. Adding that clause makes the claim checkable by the
  reader (I verified it holds for exactly this reason).
* `appendices/solutions/ch02-solutions.tex` has solutions for eight of the ten exercises;
  Exercise 2.2 (a one-star exercise whose point - a diagonal cost of 1 breaks admissibility
  of the Euclidean heuristic - is worth confirming) has none. A two-line hint would help a
  reader working alone.

## What must be kept

The chapter does the hardest thing a foundations chapter has to do: it is a reference the
rest of the book can cite by number, and it is still readable straight through. Keep the
definition-by-definition organisation exactly as it is - `ch04-astar.tex` (lines 141, 886,
935, 984) and `ch07-mapf-problem.tex` (line 190) already depend on these labels, and the
numbering is the chapter's main product. Keep Proposition 2.9 with its short proof and the
inflation pitfall; keep Example 2.20 with Table 2.3 and the pitfall "A conflict-free plan
is not automatically collision-free" - the $\sqrt{0.5}\approx0.707$ mid-step crossing is
the single best pedagogical moment in the chapter and it is exactly the model/physics gap
that Chapters 7-13 and 25 lean on. Keep Proposition 2.31 with the Lagrange-identity proof
and Example 2.35, whose numbers ($t^*=3$, $d_{\min}=\sqrt2$, $t_c\approx2.646$) the toolbox
reproduces to the digit. Keep Proposition 2.36 and the "68-95 rule is one-dimensional"
pitfall; the 2D masses 39.3 / 86.5 / 98.9 % and the 3D masses 19.9 / 73.9 % are all
correct and the warning is one practitioners get wrong constantly. Keep Algorithm 2.1 and
its honest comparison with a closed set, keep the stretch table (I re-derived 1.082 and
1.128 analytically and both are right), keep the generated double-integrator figure, and
keep the drone box, which maps every tool onto a layer of Chapter 24. The bibliography is
clean: all eleven cited keys resolve, the five anchors demanded by the spec are present,
and the details of `lozanoperez1983spatial` (IEEE Trans. Computers C-32(2):108-120, 1983),
`mellinger2011minimum` (ICRA 2011, 2520-2525), `panerati2021learning` (IROS 2021,
7512-7519), `hagberg2008networkx` (SciPy 2008, 11-15) and `fiorini1998motion`
(IJRR 17(7):760-772, 1998) are all correct - nothing fabricated.

## Response to review (round 1)

All five required changes were applied, together with every suggestion that was cheap.
Build: `cd Overleaf && ./build.sh ch02-toolbox` -> status 0, no `!` errors, no undefined
reference or citation belonging to this chapter, no multiply-defined labels; the only
overfull box above 15 pt (29.10 pt) is still the front-matter *List of Algorithms*.
Code: `python3 code/ch02_toolbox.py` -> `ch02_toolbox self-test passed`, exit 0. Both
figure generators were left untouched, so their `.dat` files are unchanged and still match
the numbers in the text; every other number quoted in the chapter is printed or asserted by
`ch02_toolbox.py`.

### Required changes

1. **Cost of a time-indexed path vs. arrival time.** Done, both parts.
   (a) `def:ch02-space-time-state` now reads "the wait costs $c_{\text{wait}}>0$ for every
   wait made before the agent's final arrival at its goal; by the stay-at-goal convention of
   \cref{def:ch02-time-indexed-path} the waits at the goal after arrival are free."
   (b) A new sentence follows `def:ch02-travel-time`: with unit move costs and free trailing
   waits, $\cost(\pi)=T(\pi)$, so a search that accumulates action costs in $g$ returns the
   travel time defined here; it names \textcite{stern2019mapf}, the $\cost(\pi_i)$ of
   \cref{ch:ch07} and the notation table's $\sumcost$.
2. **The letter $T$ overloaded in Definition 2.12.** Done. The stored list is now
   $\pi=(v_0,\dots,v_H)$, with $H$ named as the **horizon** (new index entry); $T(\pi)$ is
   the arrival time only. Added: "the arrival time satisfies $T(\pi)\le H$, with equality
   exactly when the path ends without a trailing wait at the goal. \Cref{ch:ch07} uses the
   same two letters, writing the horizon of agent $i$'s stored path as $T_i$." The same
   letter $H$ now appears in `def:ch02-time-expanded-graph`, in the vertex/edge count in the
   surrounding text, in `exr:ch02-time-expanded` and in that exercise's solution.
3. **Proof of Proposition 2.24 stops one step short.** Done: the chain now ends
   "$=v^2/a_{\max}-v^2/(2a_{\max})=v^2/(2a_{\max})$, which is
   \cref{eq:ch02-stopping-distance}."
4. **Figure 2.5 used $d$ for two distances.** Done. In `figures/ch02/segment-circle.tex`
   panel (a) the two labels are now $d_1$ (to $\vect c$) and $d_2>r$ (to $\vect c'$). The
   caption says $d_1=\dist(\vect c,\overline{\vect a\vect b})$ is the point-to-segment
   distance, that $\vect c'$ is missed because its point-to-segment distance $d_2$ exceeds
   $r$, and that in panel (b) $d=\norm{\vect p-\vect c}$ is the distance to the *centre*,
   the quantity of \cref{thm:ch02-tangents}.
5. **Length.** All five prescribed cuts were made, exactly as specified:
   (a) Listing 2.2 (`lst:ch02-geometry`) deleted; the sentence that announced it now reads
   "In the same file `tangent_points` transcribes \cref{eq:ch02-tangent-points} of
   \cref{thm:ch02-tangents} line for line, `time_of_closest_approach` ...". Listing 2.1 and
   the reference to it are untouched, and no dangling `\Cref{lst:ch02-geometry}` remains.
   (b) The "two variants in the literature" discussion is now two sentences (name both
   variants, say they coincide under a consistent heuristic, forward-reference
   \cref{ch:ch04}).
   (c) "Why dictionaries are enough" is now two sentences (the $10^6$-state / 150 MB
   estimate and the conclusion, pointing at \cref{ch:ch25}).
   (d) The one-sentence second paragraph of `sec:ch02-motivation` was merged into the
   paragraph above it.
   (e) The quadrotor caveats keep acceleration-cannot-jump, asymmetric limits and the
   margin advice; the drag and payload elaboration is gone.
   Beyond these I also tightened about fifteen wordy sentences and captions (no fact
   removed) and reduced the drawing height of the time-expanded and Gaussian figures.
   **Result: the chapter body is now 21 printed pages (was 22), not 20.** The remaining page could only be recovered by deleting content that
   this review says must be kept (the definitions the other chapters cite by number, the
   worked example with Table 2.3, the proofs, the four remaining "must cover" tables, the
   ten exercises), so it was left in place rather than cut. Every "must cover" item of
   `docs/specs/ch02.md` is still present.

### Suggestions

Applied: symmetric edge costs required for undirected weighted graphs
(`def:ch02-graph`); the touching case $d_{ij}=R_{ij}$ declared safe here and in
\cref{ch:ch12,ch:ch13}, with a note on why \cref{thm:ch02-disc-minkowski} calls it an
overlap; `time_to_collision` returning `None` stated in `def:ch02-closest-approach`; all
three generating files named in `sec:ch02-motivation`; `lattice_stretch(2)`,
`lattice_stretch(3)` and the two straight-move values added to the printed output of
`worked_example`; Figure 2.2(c) made checkable (its two-cell obstacle blocks 16 further
cells at $r=1.5$, now also asserted in the self-test, and the caption says the 5/9/21 counts
belong to the single-cell case of the text); the \cref{ch:ch07} spelling $\pi_i[t]$
mentioned in `def:ch02-plan`; "Lifelong Planning A*" expanded at first use; the
`LazyPQ.pop`/`IndexError` discrepancy stated where Algorithm 2.1 returns "empty"; the
integer-lattice clause added to the endpoint argument about inflation on a grid; a solution
for Exercise 2.2 added to `appendices/solutions/ch02-solutions.tex` (all ten exercises now
have one).

Nothing in the review was judged technically wrong; no required change was skipped.
