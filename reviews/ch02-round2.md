# Review of Chapter 2 (The Toolbox) - round 2

Reviewed artefacts: `Overleaf/chapters/ch02-toolbox.tex` (799 lines), the seven figure files in
`Overleaf/figures/ch02/`, `Overleaf/code/ch02_toolbox.py`,
`Overleaf/appendices/solutions/ch02-solutions.tex`,
`Overleaf/appendices/glossary/ch02-terms.tex` and `Overleaf/frontmatter/notation.tex`,
against `STYLE_GUIDE.md` §9, `docs/specs/ch02.md` and `docs/core-idea.txt`.

Build: `cd Overleaf && ./build.sh ch02-toolbox` -> status 0; no `!` errors; no multiply-defined
labels; no undefined reference or citation belonging to this chapter (every `??` in the PDF is a
forward reference to a chapter absent from a single-chapter build, which the guide allows); the
only `Overfull \hbox` above 15 pt (29.10 pt, log line 1946, source line 39) is still in the
front-matter *List of Algorithms*, not in this chapter.
Code: `python3 code/ch02_toolbox.py` -> `ch02_toolbox self-test passed`, exit 0.

Numbers re-checked against the run and by hand: `(3.0, 2.0)`, `(3, 3)`, makespan 3, SoC 6,
`sep 1.0`, `sep_cont 0.70710678`, `tca (3.0, 1.41421356)`, `ttc_r075 2.646446609`,
`ttc_r050 None`, `ellipse (1.6733, 0.4472, 33.690)`, `stretch2 1.0824`, `stretch3 1.1281`,
`stretch2_straight 1.41421`, `stretch3_straight 1.73205`. I re-derived the two stretch factors
analytically: for `G8`, `max_theta (cos t + (sqrt2-1) sin t) = sqrt(4-2 sqrt2) = 1.082392`,
attained at `t = 22.5 deg` exactly as the text claims; for the 26-lattice,
`sqrt(1 + (sqrt2-1)^2 + (sqrt3-sqrt2)^2) = 1.128093`. The inflation counts 5 / 9 / 21 follow from
the thresholds 0.5, 0.707, 1.5, 1.581, 2.121, and the 16 further cells of Figure 2.2(c) at
`r = 1.5` are correct and are now asserted in the self-test (line 540). Edge counts 17 / 29,
the tangent points `(3, ∓sqrt3)` with `l = sqrt12`, `theta = 30 deg`, the ellipse eigenvalues
2.8 / 0.2 with `e1 ∝ (3,2)` and `arctan(2/3) = 33.69 deg`, the 2D masses 39.3 / 86.5 / 98.9 %
and the 3D masses 19.9 / 73.9 %, and the double-integrator story (2 s / 5 s / 7 s / 10 m) are all
correct. Listing 2.1 is verbatim from the code file. All eleven cited keys resolve in
`references.bib`; nothing is fabricated. 67 `\index` entries, 7 figures, 6 tables, 28 numbered
definitions, 5 pitfall boxes, 10 exercises.

**Round-1 items verified as resolved:** #1 (cost vs. arrival time — Definition 2.10 now makes
trailing waits at the goal free and a new paragraph after Definition 2.16 states
`cost(pi) = T(pi)` and ties it to `stern2019mapf`, `ch:ch07` and the notation table); #3 (the
proof of Proposition 2.24 now closes with `= v^2/(2 a_max)`); #4 (Figure 2.5 panel (a) now
labels `d_1` and `d_2`, and the caption reserves `d = ||p - c||` for panel (b)); #5(a)-(e) (all
five prescribed cuts were made: Listing 2.2 is gone with no dangling `\Cref`, the "two variants"
discussion is two sentences, "Why dictionaries are enough" is two sentences, the motivation
paragraph is merged, the quadrotor caveats are trimmed). Every round-1 suggestion that the
response claims was applied is in fact applied. Item #2 was applied but its fix introduced a new
collision; see required change 2 below.

## Verdict

**Minor revision.**

The chapter is complete against every "must cover" item of `docs/specs/ch02.md` and every figure,
table, box and code artefact the spec asks for; the mathematics is right and the companion code
reproduces every quoted number. Three required changes remain, all local: one sentence in
Definition 2.15 that is false for exactly the paths the sentence before it puts in scope, one
symbol (`H`) that now means two different things inside the chapter and contradicts the notation
table, and a broken label in the solutions file that silently defeats the round-1 fix it was
supposed to deliver. None of them touches the structure of the chapter.

## Required changes

1. **Definition 2.15 claims `L(pi) = cost(pi)` for paths that contain waits; the chapter's own
   worked example contradicts it.**
   *Location:* `def:ch02-path-length`, line 264 (`Overleaf/chapters/ch02-toolbox.tex`), the two
   sentences "Waiting adds nothing to the length. On a grid with the costs of
   \cref{def:ch02-grid}, $L(\pi)=\cost(\pi)$."
   *Problem:* the first sentence brings time-indexed paths with wait actions into scope; the
   second then asserts an identity that holds only for wait-free paths. In `ex:ch02-costs`
   (line 303) the path `pi_B = ((1,2),(1,2),(1,1),(1,0))` has `L(pi_B) = 2` while its cost is
   `1 + 1 + 1 = 3` (one wait at unit `c_wait` plus two moves), which is also `T(pi_B) = 3`. A
   reader who trusts Definition 2.15 and then computes the sum of costs from path *lengths* gets
   5 instead of 6 for the very plan traced in Table 2.3.
   *Fix:* replace the second sentence by "On a grid with the costs of \cref{def:ch02-grid} a path
   that contains no wait has $L(\pi)=\cost(\pi)$; a time-indexed path with $w$ waits before its
   arrival has $\cost(\pi)=L(\pi)+w\,c_{\text{wait}}$, so for unit costs
   $\cost(\pi)=T(\pi)$ while $L(\pi)$ counts only the distance flown (in \cref{ex:ch02-costs},
   $L(\pi_B)=2$ but $\cost(\pi_B)=T(\pi_B)=3$)."
   *Category:* A.

2. **`H` now denotes both the grid height and the time horizon, and neither matches the notation
   table.**
   *Location:* horizon: `def:ch02-time-expanded-graph` (line 198), `def:ch02-time-indexed-path`
   (line 212), the vertex/edge counts in line 208, `exr:ch02-time-expanded` (line 768) and its
   solution in `appendices/solutions/ch02-solutions.tex`; grid height: `def:ch02-grid` (line 82,
   "width $W$ and height $H$"), `def:ch02-lattice` (line 119, "$W\times H\times D$"),
   `ex:ch02-costs` (line 303, "$W=4$ and $H=3$"), `exr:ch02-adjacency` (line 753, "$W\times H$
   grid"); third spelling: `def:ch02-big-o` (line 613) still says "the horizon $T$";
   `Overleaf/frontmatter/notation.tex` line 75 declares "$(v,t)$, $T$ ... planning horizon &
   \cref{ch:ch02}".
   *Problem:* round 1 asked for the `T`/`T(pi)` clash to be removed and it was, but the
   replacement letter was already in use: in `ex:ch02-costs` the reader meets "$H=3$" meaning a
   grid of three rows two pages after "horizon $H$" meant a number of time layers, and Exercise
   2.4 uses `H` for the horizon while Exercise 2.1 uses it for the height. Definition 2.38 and
   the notation table — which names Chapter 2 as the defining chapter for this symbol — still use
   `T`. The guide (§3) forbids competing notation and requires the notation table to be honoured.
   *Fix:* pick one free symbol for the time horizon and use it everywhere. Concretely, write
   `$\Tmax$` (i.e. `T_{\max}`): in Definition 2.11 ("with horizon $T_{\max}$ ... vertex set
   $V\times\set{0,\dots,T_{\max}}$ ... for every $t<T_{\max}$"), in Definition 2.12
   ("$\pi=(v_0,\dots,v_{T_{\max}})$ ... the last index $T_{\max}$ is the horizon ... occupies $g$
   at every time $t>T_{\max}$ ... $T(\pi)\le T_{\max}$"), in line 208 ("$\abs{V}(T_{\max}+1)$
   vertices and $T_{\max}(\abs{V}+2\abs{E})$ edges"), in Exercise 2.4 and in that exercise's
   solution; change Definition 2.38 to "the horizon $T_{\max}$"; leave `H` as the grid height
   only; keep `T(\pi)` as the arrival time. Adjust the closing sentence of Definition 2.12 to
   "\Cref{ch:ch07} writes the horizon of agent $i$'s stored path as $T_i$ and the plan horizon as
   $T=\max_i T_i$." Update `Overleaf/frontmatter/notation.tex` line 75 to read "$(v,t)$,
   $T_{\max}$ & space-time state (vertex $v$ at step $t$); planning horizon & \cref{ch:ch02}".
   While editing Definition 2.13 (line 222), replace "when $t$ exceeds the length of $\pi_i$" by
   "when $t$ exceeds the horizon of $\pi_i$", because *length* is `L(pi)` from Definition 2.15.
   *Category:* F (with C).

3. **The solution to Exercise 2.2 points at a label that does not exist, so the round-1 fix does
   not reach the book.**
   *Location:* `Overleaf/appendices/solutions/ch02-solutions.tex`, line 3:
   `\begin{solution}{exr:ch02-diagonal}`; the exercise carries `\label{exr:ch02-diagonal-cost}`
   (`chapters/ch02-toolbox.tex` line 757).
   *Problem:* the `solution` environment expands to `Exercise~\ref{#1}`
   (`searchbook.sty` line 289), so in the assembled book this solution is headed "Exercise ??"
   and LaTeX reports an undefined reference for `exr:ch02-diagonal`. The single-chapter build
   hides the fault because Appendix C is not included.
   *Fix:* change the argument to `exr:ch02-diagonal-cost`.
   *Category:* G.

## Suggestions

* **Length.** The chapter body is printed pages 21–42 of `build/only-ch02-toolbox.pdf`
  (PDF pages 20–41), i.e. **22 pages**, not the 21 claimed in the round-1 response — the same
  count as before the cuts, because the space freed by Listing 2.2 was absorbed by float
  re-placement. I am *not* requiring further cuts: every remaining page is a "must cover" item of
  the spec, and accuracy and completeness outrank length. If you want the last two pages back
  without losing content, the only material that is genuinely repeated is: (a) the second half of
  the paragraph at line 697 ("Figures whose content is computed ... for the TikZ figure to read"),
  which restates line 27; (b) the first clause of line 522 ("A horizon $\ttc$ turns ... clamps
  $t^*$ to $[0,\ttc]$"), which restates the last sentence of Definition 2.30; (c) the one-line
  paragraph at line 251; (d) the restatement of 39.3 % / 86.5 % in the "68–95 rule" pitfall, which
  is their third appearance — about half a page in total. The rest would have to come from
  shrinking figures (Figure 2.5 and Figure 2.7 are the two largest) or from `[htbp]` placement.
* Example 2.20 (line 303) says the radius-0.4 agents "touch"; by Definition 2.19 they *collide*,
  since `0.707 < 0.8` strictly. Say "collide (their separation drops below the collision
  distance)" here and in the pitfall at line 323, so the strict test of Definition 2.19 stays
  visible.
* Proposition 2.36 (line 575) gives the major-axis angle as `atan2(e_{1,y}, e_{1,x})`, which is
  defined only up to 180 degrees because an eigenvector has no canonical sign. Add "with
  $\vect e_1$ normalised so that $e_{1,x}\ge0$", which is what `covariance_ellipse` does
  (`code/ch02_toolbox.py` lines 381–383).
* The proof of Proposition 2.28 (line 464) divides by `r_1 + r_2`. Add "assume $r_1+r_2>0$; if
  both radii vanish the claim is trivial".
* Definition 2.26 (line 424) opens with "Let $\vect a\neq\vect b$" and closes with "When
  $\vect a=\vect b$ we set $s=0$". Drop the `\neq` from the opening and keep the degenerate case
  in the body.
* Exercise 2.10 (the week's coding exercise) has no solution entry; the other nine do. Chapter 4
  gives all ten, including its coding exercise. Three lines of checkpoints would help a reader
  alone: the expected 3D closest-approach value for a hand-picked pair, the 6- vs 26-connected
  path costs on an empty lattice, and the invariant `stale pops < pushes` that part (c) asks
  about.
* Table 2.1's caption credits `lattice_stretch`; the four printed values now appear in
  `worked_example` output (`stretch2`, `stretch3`, `stretch2_straight`, `stretch3_straight`), so
  the caption could say "printed by `worked_example`" and make the check a one-liner for the
  reader.

## What must be kept

The chapter does the hardest job a foundations chapter has: it is a numbered reference the rest of
the book cites, and it still reads straight through. Keep the definition-by-definition
organisation and every label exactly as it is — `ch04-astar.tex` and `ch07-mapf-problem.tex`
already depend on them, and the numbering is the chapter's main product. Keep Proposition 2.9 with
its short proof and the inflation pitfall; keep Example 2.20 with Table 2.3 and the pitfall "A
conflict-free plan is not automatically collision-free" — the `sqrt(0.5) = 0.707` mid-step
crossing is the single best pedagogical moment in the book's first part and it is exactly the
model/physics gap that Chapters 7–13 and 25 lean on. Keep the new paragraph after Definition 2.16
that reconciles `cost(pi)` with `T(pi)`: it is the sentence that makes Chapter 7 readable. Keep
Proposition 2.31 with its Lagrange-identity proof and Example 2.32, whose numbers (`t* = 3`,
`d_min = sqrt2`, `t_c = 2.646`) the toolbox reproduces to the digit; keep Proposition 2.36 and the
"68–95 rule is one-dimensional" pitfall — the 2D masses 39.3 / 86.5 / 98.9 % and the 3D masses
19.9 / 73.9 % are all correct and this is a warning practitioners get wrong constantly. Keep
Algorithm 2.1 with its honest comparison against a closed set and the `IndexError` note; keep
Table 2.1 (I re-derived 1.082 at 22.5 degrees and 1.128 analytically, both right); keep the
generated double-integrator figure and the corrected Figure 2.5; keep the drone box, which maps
every tool onto a layer of Chapter 24. The bibliography is clean: all eleven cited keys resolve,
the five anchors demanded by the spec are present, and nothing is fabricated.
