# Review of Chapter 2 (The Toolbox) - round 1

## Verdict

**Minor revision.**

This is a strong foundations chapter. It is complete against every "must cover" item of
`docs/specs/ch02.md`, every formula I recomputed is right, the build is clean (status 0,
no `!` errors, no overfull box above 15 pt, no undefined label or citation belonging to
this chapter), and **every number quoted in the text is reproduced by the code**:
`python3 code/ch02_toolbox.py` prints `length (3.0, 2.0)`, `time (3, 3)`, `makespan 3`,
`soc 6`, `sep 1.0`, `sep_cont 0.7071`, `tca (3.0, 1.4142)`, `ttc_r075 2.6464`,
`ellipse (1.6733, 0.4472, 33.69)` and the self-test passes; `gen_ch02_gaussian.py` prints
`inside 1-sigma: 39.8%` / `inside 2-sigma: 85.8%`; `gen_ch02_double_integrator.py` prints
`v_max reached at t = 2.0 s`, `braking starts at t = 5.0 s`, `stopped at t = 7.0 s, x = 10.0000 m`.
I independently re-derived the 4-/8-/6-/26-connected stretch factors
(1.414, 1.082, 1.732, 1.128 - Cauchy-Schwarz on $w_k=\sqrt{k}-\sqrt{k-1}$), the inflation
counts 5/9/21, the edge counts 17/29, the eigen-decomposition of $\Sigma$, the
$1-e^{-k^2/2}$ mass values (39.3/86.5/98.9 % in 2D, 19.9/73.9 % in 3D), the closest-approach
numbers ($t^\*=3$, $d_{\min}=\sqrt2$, $t_c=2.6464$), the tangent geometry for
$p=(0,0),c=(4,0),r=2$, and the closest-approach column of Table 2.4 (1.000 / 0.707 / 1.000).
All ten bibliography keys exist and all ten entries are real and correctly described.

What blocks acceptance is a short list of *local* defects: one over-claim about
priority-queue variants, one pseudocode line that dereferences a deleted key, one wrong
area formula in an exercise, a sign convention in Figure 2.5(b) that contradicts
Equation (2.16), two smaller figure/caption mismatches, one uncited attribution, and a
length overrun of three pages that can be removed by deleting genuinely duplicated
material. None of them requires restructuring the chapter.

**Length.** The chapter occupies printed pages 21-43 of `build/only-ch02-toolbox.pdf`
(PDF pages 13-35) = **23 pages**, i.e. 3 over the 20-page cap and 5 over the spec's
14-18 target. Item 10 below names concrete cuts; all of them are duplication, not content.

## Required changes

1. **Section 2.9, paragraph after Algorithm 2.1 (`ch02-toolbox.tex` line 682): "All three
   do the same thing" is false.** *(Category A)*
   The text says: "Two equivalent variants appear in the literature: some codes compare
   the popped key with the vertex's current $\gcost$ instead of a separate dictionary, and
   some skip a popped vertex if it is already in the closed set. All three do the same
   thing". The first two variants are equivalent to the book's, but the closed-set variant
   is not: the book's `LazyPop` *deletes* `best[item]` when the item is popped, so a later
   push with a strictly better key re-opens the node, whereas the closed-set variant
   refuses to. With an admissible but *inconsistent* heuristic that difference changes the
   answer (the closed-set variant can return a suboptimal path unless nodes are reopened) -
   exactly the issue \cref{ch:ch04} discusses.
   **Fix:** replace the last clause with something like: "The first two are equivalent to
   the version above. The closed-set variant differs: because a popped item is removed from
   $\mathit{best}$, \cref{alg:ch02-lazypq} re-opens a node when a strictly better key
   arrives later, while a closed set never does. The two agree whenever the heuristic is
   consistent (\cref{ch:ch04}); with an inconsistent heuristic the closed-set variant must
   reopen nodes explicitly to stay optimal."

2. **Algorithm 2.1, `LazyPop`, the test after the pop (`ch02-toolbox.tex` line 673):
   undefined dictionary lookup.** *(Category A)*
   The line reads `\If{$\mathit{best}[\text{item}]=\key$}`, but the branch above deletes
   `best[item]` when an item is popped, so for a stale entry of an already-popped item
   `best[item]` does not exist and the pseudocode is undefined. (The Python is correct:
   `self._best.get(item) == key`.) The surrounding prose even concedes the case ("or the
   item has already been popped") instead of fixing the line.
   **Fix:** change the condition to
   `\If{$\text{item}\in\mathit{best}$ \KwAnd $\mathit{best}[\text{item}]=\key$}` and drop
   the parenthetical "(or the item has already been popped)" from the following paragraph.

3. **Exercise 2.3 (`exr:ch02-inflation`, `ch02-toolbox.tex` line 861): wrong area formula.**
   *(Category A, also E)*
   "Compare the blocked area with the area $\pi(r+\tfrac12)^2$ of the exact Minkowski sum
   of a square and a disc for large $r$." $\pi(r+\tfrac12)^2$ is the area of a *disc* of
   radius $r+\tfrac12$. The Minkowski sum of the unit square with a disc of radius $r$ is
   the rounded square of area $1+4r+\pi r^2$ (square + four $1\times r$ rectangles + four
   quarter-discs). The two differ by $\pi r-4r+\pi/4-1\approx-0.86r-0.21$, so a student who
   follows the exercise will conclude the sampled inflation is wrong when it is not.
   **Fix:** replace the clause with "Compare the blocked-cell count with the area
   $1+4r+\pi r^2$ of the exact Minkowski sum of the unit square with the disc of radius
   $r$, and check that the ratio tends to $1$."

4. **Figure 2.5(b) (`figures/ch02/segment-circle.tex`, nodes `T1`/`T2`): the $t_+$ and
   $t_-$ labels are swapped relative to Equation (2.16).** *(Category A, also D)*
   With $p=(0,0)$, $c=(4,0)$, $r=2$: $\vect{u}=(\vect{p}-\vect{c})/d=(-1,0)$ and, by
   Definition 2.22, $\vect{u}^{\perp}=(-u_y,u_x)=(0,-1)$. Equation (2.16) then gives
   $\vect{t}_{+}=\vect{c}+r(\cos\alpha\,\vect{u}+\sin\alpha\,\vect{u}^{\perp})
   =(3,-\sqrt3)$, i.e. the *lower* tangent point - which is also what `tangent_points`
   returns first (`_self_test` asserts `t1 = (3, -sqrt 3)`). The figure labels
   `T1 = (3, 1.732)` (upper) as $\vect{t}_{+}$ and `T2 = (3,-1.732)` as $\vect{t}_{-}$.
   Since this cone is reused as the velocity obstacle and the ORCA half-plane orientation
   in \cref{ch:ch12,ch:ch13}, the sign convention must be consistent.
   **Fix:** in `figures/ch02/segment-circle.tex`, swap the two labels, so that
   `T1` (upper) is $\vect{t}_{-}$ and `T2` (lower) is $\vect{t}_{+}$; leave the
   right-angle pic and the $\alpha$/$\theta$ arcs where they are.

5. **Algorithm 2.1 vs Listing 2.3: the argument order of the push operation differs.**
   *(Category F)*
   The pseudocode declares `\ToolboxLazyPush{item, key}` (and the prose says
   "\cref{alg:ch02-lazypq} states the two operations and \cref{lst:ch02-lazypq} shows the
   toolbox class"), while the code is `def push(self, key, item)`. A reader mapping one
   onto the other stumbles.
   **Fix:** change the pseudocode signature to `\ToolboxLazyPush{$\key$, item}` and the
   text of the two lines accordingly (`push $(\key,c,\text{item})$` is already in that
   order).

6. **`appendices/solutions/ch02-solutions.tex`, solution to `exr:ch02-closest-approach`:
   $D(t)$ is redefined as the squared distance.** *(Category F, also A)*
   The solution opens "the squared distance is $D(t)=\norm{\pos+t\vel}^2=\dots$, a parabola
   in $t$ with $D'(t)=\dots$", but Definition 2.30 in the chapter defines
   $D(t)=\norm{\pos+t\,\vel}$ (the distance, not its square), and Proposition 2.31's proof
   correctly writes $D(t)^2$. As written the solution contradicts the definition it is
   solving against.
   **Fix:** write $D(t)^2=\pos\cdot\pos+2t\,\pos\cdot\vel+t^2\,\vel\cdot\vel$ and
   differentiate $D(t)^2$: $\tfrac{d}{dt}D(t)^2=2\,\pos\cdot\vel+2t\,\vel\cdot\vel$,
   vanishing at $t^\*$.

7. **Figure 2.3 (`figures/ch02/time-expanded.tex`): the only state label points at a node
   that is not on the highlighted path.** *(Category D)*
   The annotation `state $(a,2)$` has an arrow to node `A2`, while the caption says "The
   highlighted time-indexed path waits at $a$ for one step and then moves to $b$, ending in
   the state $(b,2)$." The reader's eye follows the arrow to the wrong node.
   **Fix:** move the annotation to `B2` and label it `state $(b,2)$` (e.g.
   `\node[sbannot] at (6.4,1.2) {state $(b,2)$}; \draw[sbannot,->,black!50] (6.1,1.35) -- (B2.east);`),
   or keep `(a,2)` and add a second, highlighted label on `B2`.

8. **Figure 2.2(c) (`figures/ch02/minkowski-inflation.tex`, the orange $r$ arrow): $r$ is
   drawn from the obstacle-cell centre, but the rule measures it from the obstacle
   square.** *(Category D)*
   The arrow runs `(2.5,2.5) -- (2.5,4.0)`, i.e. length $1.5$ starting at the *centre* of
   obstacle cell $(2,2)$. Section 2.3 and `Grid.inflate` block a cell "if its centre lies
   within $r$ of some obstacle *square*"; that is why cell $(2,4)$ (centre $y=4.5$) is
   blocked at $r=1.5$ while $(0,1)$ (distance $1.58$) is not. As drawn, the figure invites
   the centre-to-centre reading and contradicts the counts of Exercise 2.3.
   **Fix:** draw the arrow from the top edge of the obstacle square to the centre of the
   outermost blocked cell, `(2.5,3.0) -- (2.5,4.5)`, and keep the label $r$ beside it.

9. **Section 2.3, line 146: the configuration-space idea is attributed to Lozano-Perez
   without a citation.** *(Category H)*
   "The classical remedy, due to Lozano-P\'erez and presented in every planning textbook
   \cite{lavalle2006planning,choset2005principles}" cites only the two textbooks; the style
   guide requires the original paper as well.
   **Fix:** add to `Overleaf/bib/ch02-extra.bib` (under the ch02 comment):
   `@article{lozanoperez1983spatial, author = {Lozano-P{\'e}rez, Tom{\'a}s}, title = {Spatial Planning: A Configuration Space Approach}, journal = {IEEE Transactions on Computers}, volume = {C-32}, number = {2}, pages = {108--120}, year = {1983}}`
   and cite it: `\cite{lozanoperez1983spatial,lavalle2006planning,choset2005principles}`.
   Add it to the further-reading paragraph too.

10. **Length: 23 printed pages against a 20-page cap (spec target 14-18).** *(Category G)*
    Every cut below removes material that is stated twice; no "must cover" item is touched.
    Together they recover roughly three pages.
    a. **Delete Listing 2.3 (`lst:ch02-lazypq`, 35 lines).** It is a line-for-line
       transcription of Algorithm 2.1, which the chapter has just walked through. Replace
       with one sentence: "The class `LazyPQ` in `code/ch02_toolbox.py` implements
       \cref{alg:ch02-lazypq} on `heapq` and additionally counts pushes and stale pops."
       Remove `\cref{lst:ch02-lazypq}` from the sentence at line 725. (~0.8 page)
    b. **Shorten Listing 2.2 to `tangent_points` only.** `time_of_closest_approach` is a
       transcription of Equation (2.14) and `time_to_collision` is the "one-line call to
       `ray_circle_intersection`" the very next paragraph describes in words. (~0.5 page)
    c. **Delete the first of the "Three remarks close the toolkit" (line 538)**, from
       "First, the time to collision is a ray--circle intersection..." to "...the velocity
       obstacle of \cref{ch:ch12}." Proposition 2.27, the proof of Proposition 2.31 and the
       caption of Figure 2.5 already make this identification three times. Keep remarks two
       (the horizon $\ttc$) and three (3D). (~0.25 page)
    d. **Compress the four bullets of Section 2.10 to two sentences.** Bullet 4's ASCII-map
       convention repeats Section 2.2 line 96 verbatim in substance ("`.` for free, `#` for
       blocked, top row first"), and bullets 1-3 restate the study-plan/appendix material.
       (~0.4 page)
    e. **Cut the paragraph "Why dictionaries are enough" (line 692) to two sentences** -
       keep the $10^6$-states / ~150 MB estimate and "no chapter uses a specialised closed
       set"; drop the encode-as-integer / compiled-language advice, which returns in
       \cref{ch:ch25}. (~0.2 page)
    f. **Cut Table 2.1 (`tab:ch02-roadmap`) or its third column.** The dronebox of
       Section 2.11 already maps every tool of this chapter onto a layer and a chapter, with
       cross-references; the roadmap table repeats that mapping on the first page.
       Cutting the table and keeping one sentence ("each section names the chapters that
       use it again") is the cleaner cut. (~0.5 page)
    g. **Split and trim the opening paragraph of Section 2.1 (line 23).** It is a single
       20-line paragraph that enumerates the whole chapter and then Section 2.1's second
       paragraph plus Table 2.1 enumerate it again; this also violates the style guide's
       "one idea per paragraph". Cut it to three short paragraphs (map and size; time and
       cost; motion, geometry, uncertainty, computation). (~0.3 page)

## Suggestions

* Exercise difficulty is bunched: seven of ten are `\difficulty{2}`. Exercise 2.5 (build a
  three-agent instance *and* prove no plan is optimal for both objectives - the model
  solution runs to fifteen lines) is a genuine `\difficulty{3}`; Exercise 2.4's
  one-to-one-correspondence claim is nearer 3 than 2. Promoting one of them and adding a
  one-star drill on makespan/sum-of-costs arithmetic would give a better spread.
* `appendices/solutions/ch02-solutions.tex` has four solutions for ten exercises (the same
  ratio as ch01/ch03/ch05, so this is not a required change). Exercises 2.1, 2.3, 2.6 and
  2.8 all have short, checkable answers (17/29 edges; 5/9/21 cells, the count
  changing at $r=0.5$, $\sqrt{0.5}$, $1.5$, $\sqrt{2.5}\approx1.581$ and $1.5\sqrt2\approx2.121$; 20 braking steps, 2.0 m exact vs 2.1 m
  forward-Euler; $(3,\mp\sqrt3)$, $\ell=2\sqrt3$, $\theta=30^\circ$). Two-line hints would
  help the solo reader a lot.
* Section 2.9, line 632: "a NumPy operation on a whole array costs about the same per
  element but with a hundredfold smaller constant" reads as self-contradictory. Say
  "NumPy does the same work per element roughly a hundred times faster, because the loop
  runs in C".
* Proposition 2.9: add "closed" to the hypothesis on $\mathcal{O}$. With a non-closed
  obstacle region the equivalence "$\pos\in\Cfree$ iff $\dist(\pos,\mathcal{O})>r$" fails
  on the boundary (the infimum need not be attained).
* `\dist` is used for three different things (graph distance in Definition 2.3, point-to-set
  distance in Definition 2.11, point-to-segment distance in Definition 2.23). One sentence
  in Definition 2.11 saying that $\dist$ also denotes Euclidean distance to a set would
  save the reader a double-take.
* `code/ch02_toolbox.py`, `tangent_points`: `t_left` is the point *below* the axis in the
  worked configuration (it is Equation (2.16)'s $\vect{t}_+$). Rename `t_left`/`t_right` to
  `t_plus`/`t_minus` so the code, the proposition and the figure use one convention (this
  is the same convention issue as required change 4).
* Figure 2.1(b) caption: "the move into the obstacle and the two diagonals that would pass
  its corners are forbidden by the corner-cutting rule" - the straight move is forbidden
  because the cell is blocked, not by the corner-cutting rule. Reword to "the move into the
  obstacle is forbidden because the cell is blocked; the two diagonals past its corners are
  forbidden by the corner-cutting rule."
* Definition 2.10 introduces $c_{\text{wait}}$ but never constrains it. Add "with
  $c_{\text{wait}}>0$" (or note that a zero-cost wait makes the search non-terminating on an
  unbounded horizon).
* For the editor, not this chapter: `frontmatter/notation.tex` is still the two-row
  placeholder, so notation consistency could only be checked against `searchbook.sty` and
  \cref{ch:ch04}. Chapter 2 is the natural source for the notation table -
  $\pos,\vel,\acc,\state,\meas,\Cfree,\Cobs,\makespan,\sumcost,\dt,\ttc,\dist,\cost$ are all
  defined here; consider harvesting it when Phase 1 completes. Also note that `\ttc` renders
  as $\tau$ but is used as the *horizon*, while the *time to collision* is $t_c$; a
  `\horizon` macro would remove the clash.

## What must be kept

The geometry section (2.7) is the best thing in the chapter and must survive intact: five
primitives, each with a correct statement *and* a real proof (the Lagrange-identity step in
Proposition 2.31 and the right-triangle argument in Proposition 2.29 are exactly right), all
of them framed in the relative frame that \cref{ch:ch12,ch:ch13} will inherit. Keep
Proposition 2.9 with its proof and the disc-to-point argument, the bounding-sphere
paragraph, and the margin pitfall - that is the cleanest statement of "why we may plan for a
point" I have read in a textbook of this level. Keep Example 2.20 with Table 2.4 and the
pitfall "A conflict-free plan is not automatically collision-free": showing that two agents
that never share a cell still pass within $\sqrt{0.5}$ of each other, and pinning the safe
radius at $0.3$ vs $0.4$ cells, is the single most valuable page of the chapter and it is
verified by `min_separation_continuous`. Keep the exact discrete double-integrator matrices
with the explicit "the model is exact, not an approximation" remark, the forward-Euler
contrast, and the "Clipping breaks linearity" pitfall - together with the trapezoid trick in
`double_integrator_step` they pre-empt a bug almost every student writes. Keep the whole
lazy-deletion treatment (subject only to the two local fixes above): it is the idiom the
entire book runs on and it is explained better here than in most references. Keep the
68-95 pitfall and Proposition 2.36's $1-e^{-k^2/2}$ mass formula with the 2D and 3D numbers.
Keep all seven figures - they use the shared styles, they are geometrically correct (I
checked the intersection points $x=2\pm\sqrt{0.75}$ in 2.5(a), the contact point
$(1.354,-0.646)$ in 2.6, the semi-axis arrows in 2.7 and the sixteen inflated cells in
2.2(c) against the $r=1.5$ rule), and two of them are generated from seeded data. Keep
Tables 2.2 and 2.3: the lattice-stretch column is a non-obvious result computed by the
code, and the path / time-indexed path / plan / trajectory table is the vocabulary the rest
of the book depends on. Finally, keep the discipline that produced this draft - every
quoted number traced to a runnable script, 66 index entries, ten verified citations, and a
clean build.
