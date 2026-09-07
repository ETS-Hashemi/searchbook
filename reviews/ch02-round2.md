# Review of Chapter 2 (The Toolbox) - round 2

## Verdict

**Minor revision.**

All ten required changes of round 1 were applied, and I verified each one in the source, in
the figure files, in the rendered PDF and in the code:

1. the "All three do the same thing" over-claim is gone and the closed-set variant is now
   distinguished from `\cref{alg:ch02-lazypq}` (but see required change 1 below: the
   replacement sentence introduced a new, smaller contradiction);
2. `LazyPop` now tests `item ∈ best \KwAnd best[item] = key`, matching
   `self._best.get(item) == key`, and the "(or the item has already been popped)"
   parenthetical is gone;
3. Exercise 2.3 now compares against the rounded-square area $1+4r+\pi r^2$;
4. `figures/ch02/segment-circle.tex` now labels the upper point `T1` as $\vect{t}_{-}$ and
   the lower point `T2` as $\vect{t}_{+}$, which is what Equation (2.16), Definition 2.22
   and `tangent_points` produce ($\vect{u}=(-1,0)$, $\vect{u}^{\perp}=(0,-1)$,
   $\vect{t}_{+}=(3,-\sqrt3)$);
5. the pseudocode signature is `\ToolboxLazyPush{$\key$, item}`, matching
   `def push(self, key, item)`;
6. the solution to `exr:ch02-closest-approach` now differentiates $D(t)^2$;
7. the annotation in `time-expanded.tex` points at `B2` and reads "state $(b,2)$";
8. the $r$ arrow in `minkowski-inflation.tex` runs `(2.5,3.0) -- (2.5,4.5)`, i.e. from the
   top edge of the obstacle square to the centre of the outermost blocked cell;
9. `lozanoperez1983spatial` exists in `bib/ch02-extra.bib`, is cited in Section 2.3 and
   named in the further-reading paragraph (the entry is real and correct: IEEE Trans.
   Computers C-32(2), 108-120, 1983);
10. all seven prescribed cuts were made (Listing 2.3 gone, Listing 2.2 reduced to
    `tangent_points`, one of the three closing remarks gone, Section 2.10 compressed,
    "Why dictionaries are enough" cut to two sentences, `tab:ch02-roadmap` gone, the opening
    paragraph split).

I re-verified the technical content independently: the four stretch factors
($\sqrt2$, $\sqrt{1+(\sqrt2-1)^2}=1.0824$, $\sqrt3$, $\sqrt{1+(\sqrt2-1)^2+(\sqrt3-\sqrt2)^2}=1.1281$),
the inflation counts 5/9/21 and the thresholds $0.5,\sqrt{0.5},1.5,\sqrt{2.5},1.5\sqrt2$,
the sixteen orange cells of Figure 2.2(c) against the $r=1.5$ rule with the two-cell
obstacle, the 17/29 edge counts, the time-expanded edge count $T(\abs{V}+2\abs{E})$,
Example 2.20 and every entry of Table 2.3 (including the closest-approach column
$1.000/0.707/1.000$, which I recomputed by hand), the exact discrete double integrator and
the $2/5/7$~s, $2/8/10$~m milestones of Figure 2.4, the ray-circle roots, the tangent
geometry $(3,\mp\sqrt3)$, $\ell=2\sqrt3$, $\theta=30^\circ$, the closest-approach formulas
and $t^*=3$, $d_{\min}=\sqrt2$, $t_c=2.6464$, the eigen-decomposition
$\lambda=2.8/0.2$, $\vect{e}_1\propto(3,2)$, $33.69^\circ$, and the $1-e^{-k^2/2}$ masses
(39.3/86.5/98.9 % in 2D, 19.9/73.9 % in 3D). The proof of the stopping distance, of the
inflation proposition, of the disc Minkowski sum, of the tangent triangle, of the
Lagrange-identity step and of the $\chi^2_2$ mass are all correct. Every proposition has a
proof; nothing is asserted as a theorem without one.

**Code.** `python3 code/ch02_toolbox.py` passes its self-test and prints
`length (3.0, 2.0)`, `time (3, 3)`, `makespan 3`, `soc 6`, `sep 1.0`,
`sep_cont 0.7071067811865476`, `tca (3.0, 1.4142135623730951)`, `ttc_r075 2.646446609406726`,
`ttc_r050 None`, `ellipse (1.6733200530681511, 0.44721359549995787, 33.69006752597979)`;
`gen_ch02_double_integrator.py` prints `v_max reached at t = 2.0 s, x = 2.000 m`,
`braking starts at t = 5.0 s, x = 8.000 m, stopping distance = 2.000 m`,
`stopped at t = 7.0 s, x = 10.0000 m`; `gen_ch02_gaussian.py` prints
`eigenvalues: 2.800, 0.200; semi-axes: 1.673, 0.447; angle: 33.69 deg`,
`inside 1-sigma: 39.8%`, `inside 2-sigma: 85.8%`. **Every number quoted in the chapter, in
the captions and in the solutions is reproduced by the code.**

**Build.** `./build.sh ch02-toolbox` -> status 0, no `!` errors, **zero** overfull boxes of
any size, no undefined reference or citation belonging to Chapter 2 (the remaining warnings
are all `ch:chNN` of chapters not included in the single-chapter build). All eleven citation
keys resolve, and all eleven entries are real and correctly described. 66 unique index
entries, 15 glossary terms in `appendices/glossary/ch02-terms.tex`, 8 of 10 exercises have
solutions in `appendices/solutions/ch02-solutions.tex` (the two without are the
diagonal-cost thought experiment and the coding exercise).

**Completeness.** All nine "must cover" groups of `docs/specs/ch02.md` are present, together
with all six prescribed figures (plus a seventh, the closest-approach figure), 6 tables
(spec: >=3), 7 figures (spec: >=5), 10 exercises (spec: 8-10) with the spread 1,1,2,3,3,2,2,2,2,3,
the coding exercise, the objectives box, one keyidea box, five pitfall boxes, the dronebox
naming the four layers of `\cref{ch:ch24}` and Week 1 of `\cref{ch:appA}`, the summary and
the further-reading paragraph. Week 1 of the training plan (space-time representation, the
foundations for admissible/consistent heuristics) is served.

**Length.** The chapter occupies printed pages 21-42 of `build/only-ch02-toolbox.pdf`
(PDF pages 12-33) = **22 pages**, 2 over the 20-page cap and 4 over the spec's 14-18 target.
I looked for the two pages and did not find them: after the round-1 cuts, the material I can
still identify as duplication is worth about half a page in total (listed under Suggestions),
and everything larger is either a must-cover item of the spec or on the round-1 "must be
kept" list. In a chapter with 7 figures, 6 tables, an algorithm and 2 listings, removing body
text tightens pages rather than eliminating them - the reviser measured this (23 -> 22 for
78 deleted lines plus ~250 words) and my own reading agrees. **I therefore do not require
cuts**: per the review brief, completeness and accuracy outrank length, and the remaining
excess is content, not padding.

What blocks acceptance is a short list of three local defects: one contradictory sentence
introduced by the round-1 fix, one self-contradicting model solution, and one stale
proposition number in a code docstring.

## Required changes

1. **Section 2.9 (`sec:ch02-computation`), `ch02-toolbox.tex` line 666, printed page 38:
   "The first two are equivalent to the version above" contradicts the sentence that
   follows.** *(Category A, also C)*
   The passage now reads: "*Two* variants appear in the literature: some codes compare the
   popped key with the vertex's current $\gcost$ instead of a separate dictionary, and some
   skip a popped vertex if it is already in the closed set. **The first two** are equivalent
   to the version above. **The closed-set variant differs**: ...". Only two variants are
   introduced, and the second of them is the closed-set variant, so "the first two" asserts
   that the closed-set variant is equivalent and then immediately denies it. (The round-1
   fix text was written for the older sentence, which counted three things: the book's
   version plus two variants.)
   **Fix:** replace "The first two are equivalent to the version above." with "The first of
   these is equivalent to the version above." Leave the rest of the paragraph unchanged; it
   is correct as it stands.

2. **`appendices/solutions/ch02-solutions.tex`, solution to `exr:ch02-adjacency`: the
   neighbour list of cell $(2,1)$ states four diagonals and then withdraws two of them.**
   *(Category E, also C)*
   The sentence reads: "Cell $(2,1)$ has $(1,1)$ blocked, so its neighbours are $(3,1)$,
   $(2,0)$, $(2,2)$ at cost $1$ and $(1,0)$, $(3,0)$, $(1,2)$, $(3,2)$ at cost $\sqrt2$ (the
   diagonals to $(1,0)$ and $(1,2)$ pass between $(1,1)$ and a free cell, and the
   corner-cutting rule of \cref{def:ch02-grid} forbids them, so only $(3,0)$ and $(3,2)$
   remain)." A student checking an answer reads the list before the parenthesis and
   concludes that $(1,0)$ and $(1,2)$ are neighbours. The correct answer - the one asserted
   by the self-test, `sorted(nb) == [(2, 0), (2, 2), (3, 0), (3, 1), (3, 2)]` - is five
   neighbours.
   **Fix:** state it once, positively, e.g.: "Cell $(2,1)$ has the blocked cell $(1,1)$ as
   its left neighbour, so the straight moves lead to $(3,1)$, $(2,0)$ and $(2,2)$ at cost
   $1$. Of the four diagonals, those to $(1,0)$ and $(1,2)$ pass between $(1,1)$ and a free
   cell and are forbidden by the corner-cutting rule of \cref{def:ch02-grid}; only $(3,0)$
   and $(3,2)$ remain, at cost $\sqrt2$. Cell $(2,1)$ therefore has five neighbours."

3. **`code/ch02_toolbox.py`, `tangent_points` docstring (line ~283): wrong proposition
   number.** *(Category F, cosmetic)*
   The docstring says "Returns `(t_plus, t_minus)` in the sign convention of **Proposition
   2.32**". In the built chapter the tangent-line result is **Proposition 2.29**
   (2.32 is *Example* 2.32, the crossing-drones example).
   **Fix:** write "in the sign convention of Equation (2.16) (Proposition 2.29 of
   Chapter 2)", or drop the number and say "in the sign convention of the chapter's
   tangent-line proposition: `t_plus` uses $+\sin\alpha$ along `u` rotated by $+90$
   degrees". Referring to the equation rather than the proposition number makes the
   docstring immune to renumbering.

## Suggestions

* **Definition 2.8 (`def:ch02-minkowski-sum`).** The identity
  $A\oplus\disc{\vect{0}}{r}=\set{\vect{x} : \dist(\vect{x},A)\le r}$ holds for a *closed*
  $A$; for a non-closed $A$ the infimum need not be attained and the right-hand side is
  strictly larger on the boundary. Proposition 2.9 already assumes $\mathcal{O}$ closed
  (round-1 suggestion, applied); add the same word here, e.g. "\textbf{Inflating} a closed
  set $A$ by the radius $r$ ...".
* **`LazyPQ.push` docstring and the prose "re-opens a node when a strictly better key
  arrives later".** Because a popped item is deleted from `best`, *any* later push for that
  item is accepted, not only a strictly better one; the docstring "ignored unless `key`
  improves" is true only while the item is still queued. No search in this book pushes a
  worse key for a popped item, so nothing is broken - but half a sentence ("a key pushed
  after the item has been popped is always accepted; the searches of this book only push
  improved keys") would close the gap for a reader who reuses the class.
* **Length, optional trims (~0.5 page, no must-cover item touched).** If the editor wants to
  claw back space without cutting content: (a) the paragraph after Table 2.6
  (`ch02-toolbox.tex` line 700) repeats the table's Status column - "Every algorithm is
  implemented with \python and NumPy alone; SciPy appears only for the optimisation problems
  of Part~VII" - and can lose that clause; (b) the last two sentences of the pitfall "Floats
  and arrays as dictionary keys" repeat the "Hashing states" paragraph immediately above
  ("keep discrete states as tuples of integers" / "round it to a resolution first") and can
  be reduced to the `0.1 + 0.2 != 0.3` observation and the NumPy-arrays-are-unhashable
  remark; (c) Table 2.5 (`tab:ch02-operations`) can drop the rows "append, index, pop from
  the end", "sort" and "vector operation of length $n$", which a reader "comfortable with
  \python" already knows, keeping the four rows that the following two paragraphs actually
  use; (d) the sentence after Table 2.2 ("\Cref{tab:ch02-path-plan-trajectory} summarises the
  vocabulary ... the local layer edits that trajectory when an intruder appears") restates the
  table's "Produced by"/"Consumed by" columns and the drone box.
* **Exercise 2.3.** Section 2.3 already gives the counts 5, 9 and 21 *and* names the shapes
  ("a plus shape, a $3\times3$ block, and the block with a ring of $12$ further cells"), so
  "confirm the counts $5$, $9$ and $21$" asks the student to confirm what they have just
  read. Consider dropping the three numbers from the exercise (keep them in the solution) so
  that part of the exercise is a real computation.
* **`covariance_ellipse` (code, line ~386).** The comment `# in (-90, 90] degrees` sits on
  `angle = math.atan2(...)`, which returns radians; the degree conversion happens in the
  caller. Say "radians, equivalent to $(-90,90]$ degrees".
* **For the editor, not this chapter.** (i) `frontmatter/notation.tex` is still the two-row
  placeholder, so notation consistency could only be checked against `searchbook.sty` and
  the later chapters; Chapter 2 remains the natural source to harvest
  ($\pos,\vel,\acc,\state,\meas,\Cfree,\Cobs,\makespan,\sumcost,\dt,\ttc,\dist,\cost$ are all
  defined here). (ii) `\ttc` renders as $\tau$ but is used as the *horizon*, while the *time
  to collision* is $t_c$; a `\horizon` macro would remove the clash before
  \cref{ch:ch12,ch:ch13,ch:ch24} inherit it. (iii) In a single-chapter build,
  cross-chapter `\cref`s resolve against stale `build/chapters/*.aux` files rather than
  printing `??` - `\cref{ch:ch04}` renders as "Chapter 1" on page 38 - so cross-chapter
  *numbers* can only be checked in the full build. The keys themselves are all correct
  (ch03 Dijkstra, ch04 A*, ch05 D* Lite, ch07 MAPF, ch12 VO, ch13 ORCA, ch14 DWA, ch16/17
  RRT, ch18 Kalman, ch19 nonlinear filters, ch20 prediction, ch21 MPC, ch22 MILP, ch24
  hybrid, ch25 experiments - I checked every one against `main.tex`).

## What must be kept

Everything the round-1 review named must survive, and the round-2 draft has kept it: the
geometry section (2.7) with five primitives, each with a correct statement *and* a real
proof, all framed in the relative frame that \cref{ch:ch12,ch:ch13} inherit; Proposition 2.9
with its disc-to-point argument, the bounding-sphere paragraph and the margin pitfall - still
the cleanest statement of "why we may plan for a point" I have read at this level; Example
2.20 with Table 2.3 and the pitfall "A conflict-free plan is not automatically
collision-free", including the $0.3$-versus-$0.4$-cell radius threshold, which is the single
most valuable page of the chapter; the exact discrete double-integrator matrices with the
"the model is exact, not an approximation" remark, the forward-Euler contrast and the
"Clipping breaks linearity" pitfall, backed by the trapezoid trick in
`double_integrator_step`; the whole lazy-deletion treatment, which is the idiom the entire
book runs on; the 68-95 pitfall with Proposition 2.36 and its 2D/3D mass numbers; all seven
figures, whose geometry I re-checked point by point (the intersections $x=2\pm\sqrt{0.75}$ in
2.5(a), the corrected tangent labels in 2.5(b), the contact point $(1.354,-0.646)$ and the
$R=1.5$ circle in 2.6, the semi-axes $\sqrt{2.8}\,(0.832,0.555)$ and
$\sqrt{0.2}\,(-0.555,0.832)$ in 2.7, the sixteen inflated cells and the corrected $r$ arrow
in 2.2(c), the corrected state annotation in 2.3, the forbidden moves in 2.1(b)); Tables 2.1
and 2.2, whose lattice-stretch column and path/time-indexed-path/plan/trajectory vocabulary
the rest of the book depends on.

New in this round and worth keeping: the corrected Figure 2.1(b) caption, which now blames
the blocked cell and the corner-cutting rule separately; the $c_{\text{wait}}>0$ requirement
in Definition 2.10 with its one-line justification; the note in Definition 2.8 that $\dist$
also denotes point-to-set distance, with pointers to its other two uses; the
`t_plus`/`t_minus` renaming, which now gives code, proposition, figure and solution a single
sign convention; the promotion of Exercises 2.4 and 2.5 to three stars; and the four new
short solutions (2.1, 2.3, 2.6, 2.8), all of which I checked and all of which are correct -
in particular the 2.1 m forward-Euler figure and its
$\tfrac12\dt^2 a_{\max}$-per-step explanation, and the six-cell corridor of the makespan /
sum-of-costs solution, whose optimality argument (makespan 5 forces $\sumcost\ge12$;
$\sumcost=11$ forces makespan 6) I verified case by case.

Above all, keep the discipline that produced this draft: every quoted number traced to a
runnable script, a build with zero overfull boxes, 66 index entries, eleven verified
citations, and a solutions file that now covers eight of ten exercises.
