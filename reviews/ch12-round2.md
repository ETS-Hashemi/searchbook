# Review of Chapter 12 (Velocity Obstacles) - round 2

Reviewed artefacts: `Overleaf/chapters/ch12-velocity-obstacles.tex` (1513 lines),
`Overleaf/figures/ch12/{idea,geometry,truncated,feasible,example,oscillation,crossing,cone3d}.tex`,
`Overleaf/code/ch12_velocity_obstacles.py` (658 lines), `Overleaf/code/figures/gen_ch12_sim.py`,
`Overleaf/figures/data/ch12-{example-traj,oscillation,crossing}.dat`,
`Overleaf/appendices/solutions/ch12-solutions.tex` (107 lines),
`Overleaf/appendices/glossary/ch12-terms.tex`, `Overleaf/references.bib`,
`Overleaf/bib/ch12-extra.bib`, `Overleaf/frontmatter/notation.tex`, `Overleaf/searchbook.sty`,
`docs/specs/ch12.md`, `docs/core-idea.txt` (Week 6), `STYLE_GUIDE.md` section 9,
and `reviews/ch12-round1.md` including the reviser's response.

**Build.** `cd Overleaf && ./build.sh ch12-velocity-obstacles` exits 0. No `!` errors, no
citation warnings, no undefined label belonging to Chapter 12 (all `??` resolve to
`ch:ch11`, `ch:ch13`, `ch:ch14`, `ch:ch18`, `ch:ch19`, `ch:ch20`, `ch:ch21`, `ch:ch24`, i.e.
other chapters, as expected in a single-chapter build). The single overfull box (29.10 pt,
log line 1947) is in the *List of Algorithms* and comes from another chapter's caption.
Chapter body = PDF folios 115-136 = **22 pages**, inside the 24-page limit.

**Code.** `python3 code/ch12_velocity_obstacles.py` prints `ch12 self-test passed (0.3 s)`;
`python3 code/figures/gen_ch12_sim.py` regenerates the three `.dat` files unchanged. I
re-derived independently and confirmed: `theta = arcsin(1/sqrt50) = 8.130 deg`, legs
`(0.8,-0.6)`/`(0.6,-0.8)` with tangent points `(5.6,-4.2)`/`(4.2,-5.6)` at distance `7`,
`Delta/4 = 90.25-88.69 = 1.56`, roots `4.5586` and `5.9386`, exact projection `v* = (1,0.1)`
with `t_c = 5` exactly, `t* = 9.5/1.81 = 5.2486` with miss distance `0.37167`, threshold
`v_max d/R = 10.6`, `(d-R)/tau = 1.2142`, `sqrt(d^2-R^2)/tau = 1.4`, the `n=1` discriminant
of `(1.2,-0.9)` at `t=1 s` (`-0.117 < 0`), and every cell of Tables 12.1 and 12.2. From the
plot data I confirmed the two numbers the reviser changed in round 1: `avx = 1.2` holds
exactly on `t in [0.9, 3.6]` (caption of `fig:ch12-example`(b)) and the northward component
first appears at `t = 3.7 s` with `v_A = (1.046, 0.0915)`.

**Round-1 items.** All seven required changes of round 1 are correctly resolved and are not
re-raised: `\VoInside` now returns `t < infinity and t <= tau` (line 568) matching
`lst:ch12-ttc`; `alg:ch12-choose:feasible` now reads
`{v in S : t_min(v) > tau or t_min(v) = infinity}` matching `feasible = (tc > tau) | isinf(tc)`;
the proof of `thm:ch12-truncated` now uses the scaling identity `eq:ch12-scaling`
(`t_c(sv) = t_c(v)/s`) and the argument is correct and complete; the self-test timing/scope
sentence matches the code; the `fig:ch12-example`(b) interval is `0.9`-`3.6 s`; "trivially" is
gone; and all eight solutions are present in `appendices/solutions/ch12-solutions.tex`
(I checked each one numerically - `11.54/23.07 deg`, `7.18/14.36 deg`, `d = 1.6 m`;
`1.2142` and `1.4` with both points at distance exactly `0.2` from `(1,-0.1)`;
`9t^2-36t+33.75=0`, roots `1.5`/`2.5`, `t* = 2`, distance `2`; `0.375 m/s`;
tangency circle at `168/13 = 12.923` with radius `sqrt(168)/13 = 0.997` - all correct).

## Verdict

**Minor revision.** The chapter is technically sound, complete against the spec and Week 6 of
the training plan, and every quoted number is reproduced by the code. Three defects remain,
all sentence-level: one statement in the worked example that is wrong by a factor of two
under the chapter's own convention, one use of the term "relative velocity" with the opposite
sign to `\cref{def:ch12-relative}`, and four acronyms used before being defined. Nothing
structural; no proof, formula, figure or table needs to change.

## Required changes

1. **`sec:ch12-example`, line 785 (PDF p.125, paragraph "Two details of the trace deserve
   attention") - "the wedge is almost $90^\circ$ wide" is wrong by a factor of two.**
   (Category A.)
   The chapter's own convention is that a wedge of half-angle `theta` is `2*theta` *wide*
   (`exr:ch12-halfangle` asks for "the width of the wedge in degrees" and its solution gives
   "$\theta=11.54^\circ$, a wedge $23.07^\circ$ wide"). At `t = 5.0 s` the trace gives
   `p_A = (0.637, 0.273)` and `B` at `(0,-0.5)`, so `p_rel = (-0.637,-0.773)`,
   `d = 1.00165` and `theta = arcsin(R/d) = 86.7^\circ`: the wedge is `173^\circ` wide,
   i.e. almost a half-plane - which is exactly the point the sentence is trying to make
   (that `122` of `722` samples nevertheless survive).
   *Fix:* replace "the wedge is almost $90^\circ$ wide ($d \approx R$)" by
   "the half-angle is almost $90^\circ$ ($d = 1.0017 \approx R$), so the wedge is nearly a
   half-plane".

2. **`sec:ch12-intuition`, line 84 - "relative velocity" is used with the sign opposite to
   `\cref{def:ch12-relative}`.** (Category C.)
   The sentence reads "drone $B$ is an object at the relative position $\pos_B - \pos_A$ that
   drifts with the relative velocity $\vel_B - \vel_A$". The statement is physically correct,
   but two pages later `\cref{def:ch12-relative}` and the notation table
   (`frontmatter/notation.tex`, line 128) fix `\vel_{\mathrm{rel}} = \vel_A - \vel_B` as *the*
   relative velocity, and the rest of the chapter (and the glossary entry "Relative velocity")
   uses only that sign. A reader working alone who flips back will read the two as
   contradictory.
   *Fix:* write "...that drifts at the rate $\vel_B - \vel_A$, the negative of the relative
   velocity of \cref{def:ch12-relative}". (The next sentence, which switches to
   $\vel_A - \vel_B$, then needs no change.)

3. **Acronyms used before being defined: `\cbs` (line 30), `\ecbs` (line 54), RVO and `\orca`
   (lines 59-60).** (Category F, cosmetic.)
   `STYLE_GUIDE.md` section 3 requires each acronym to be defined at first use *in every
   chapter*. Chapter 12 never expands RVO or ORCA, although it is the chapter that introduces
   the VO family and hands the reciprocal cases to `\cref{ch:ch13}`; the other chapters do
   expand it (`ch02` line 341, `ch14` line 30: "optimal reciprocal collision avoidance
   (\orca)").
   *Fix:* line 30, "its conflict-based-search (\cbs) route"; line 54, "(\cbs or \ecbs,
   enhanced \cbs, \cref{ch:ch09,ch:ch10})"; lines 59-60, "The reciprocal variants of
   \cref{ch:ch13} --- reciprocal velocity obstacles (RVO) and optimal reciprocal collision
   avoidance (\orca) --- are what the swarm members use among themselves".

## Suggestions

* **`thm:ch12-cone3d` has its proof in running prose rather than in a `proof` environment.**
  The sketch ("the proof is the one of `\cref{thm:ch12-cone}` and `\cref{thm:ch12-truncated}`
  read with 3-vectors; the only new fact is that the set of directions at angle `<= theta`
  from a fixed axis in `R^3` is a circular cone") is complete enough and the details are
  `exr:ch12-3d` with a full solution, so this is not a defect; but wrapping those two
  sentences in `\begin{proof}[Proof sketch] ... \end{proof}` would make it visibly a proof and
  match the presentation of the other four results in the chapter.
* **Duplication between "Exact selection" (`sec:ch12-variants`, lines 1075-1086) and
  "Sampling versus solving exactly" (`sec:ch12-implementation`, lines 1187-1201).** Both say
  that with a single obstacle `VelocityObstacle.closest_boundary_point` is cheaper and better,
  that with several obstacles the projection onto one wedge can land in another, and that
  \orca solves this with one half-plane per obstacle. The chapter is inside the 24-page limit,
  so no cut is required, but merging these two paragraphs (keeping the geometric statement in
  `sec:ch12-variants` and the practical advice in `sec:ch12-implementation`) would recover
  about half a page towards the spec's 13-15 page target.
* **Caption of `fig:ch12-crossing`(b)** says the price of avoidance is "$1$--$2\,\%$ in the
  stream", while the body text and `tab:ch12-crossing` give `1.4`-`2.3 %` (max `1.023` at
  `n=8`). Use `1$--$2.5\,\%` or repeat `1.4$--$2.3\,\%` so the caption and the table agree.
* **`sec:ch12-example`, "the tangent points ... form $3$--$4$--$5$ triangles"** is loose: the
  triangle `0`, `t`, `p_rel` has legs `1` and `7`. What is `3-4-5` is the *direction* of each
  leg, `(0.8,-0.6)` and `(0.6,-0.8)`. Say "the leg directions are the `3`-`4`-`5` unit vectors
  $(0.8,-0.6)$ and $(0.6,-0.8)$".
* **Proof of `cor:ch12-intruder`** applies `\cref{thm:ch12-safety}`, whose hypothesis is that
  *both* agents hold their velocities on the whole of `[0,\ttc]`, while `A` in fact changes
  its velocity at `\dt`. The conclusion is still correct because the centre distance on
  `[0,\dt]` depends only on the velocities held there; one half-sentence ("the distance on
  $[k\dt,(k+1)\dt]$ depends only on the velocities held during that interval") would close the
  gap for a careful reader.
* **Proof of `thm:ch12-cone`, line 239** still points at `\cref{ch:ch02}` in general
  ("Chapter 2, distance from a point to a segment") where the neighbouring references were
  upgraded to exact labels in round 1; `\cref{def:ch02-point-segment-distance}` is the result
  meant. Lines 90, 148 and 481 are the same case (Minkowski sum, point-mass model, `v_max`).
* **`bib/ch12-extra.bib`, `large2002nonlinear`.** I can vouch for the existence of the
  non-linear velocity obstacle work of Large, Sekhavat, Shiller and Laugier around 2002 and
  the ICARCV venue is plausible, but I cannot verify the exact title wording or the page
  numbers from here. Since the entry carries no pages, it is safe as it stands; if the editor
  can check one thing, check that the title is "Using Non-Linear Velocity Obstacles to Plan
  Motions in a Dynamic Environment" rather than the IROS 2002 variant "Towards Real-Time
  Global Motion Planning in a Dynamic Environment Using the NLVO Concept".
* **`figures/data/ch12-example-traj.dat`** stores `tc_pref = 99.0` where the time to collision
  is infinite. The text and the trace table (which come from the code, not the file) say
  `\infty`, so nothing is wrong, but a reader who opens the `.dat` will wonder; a comment line
  in `gen_ch12_sim.py` saying that `99` is the plotting cap would prevent the question.

## What must be kept

The geometric spine of this chapter is the best I have read on velocity obstacles and must
survive untouched. `thm:ch12-cone` and its proof (the `arcsin(R/d)` half-angle obtained from
the perpendicular distance from the disc centre to the ray, with the `varphi > pi/2` case
handled explicitly), the observation that `Delta/4 = |v|^2 (R^2 - d^2 sin^2 varphi)` makes the
discriminant condition and the cone condition the same fact, and the treatment of truncation
as the union of the inscribed scaled discs `D(p_rel/t, R/t)` - which generalises immediately
to the non-linear velocity obstacle and to 3D - are a genuine pedagogical find. The rewritten
proof of `thm:ch12-truncated` is now exactly right: the scaling identity `eq:ch12-scaling` is
stated, used to locate the endpoint of each ray, and reused by the solution to
`exr:ch12-truncation`; do not touch it. `fig:ch12-geometry` (workspace beside velocity space,
with the `3-4-5` legs, the truncation disc, the exact projection and the sampled choice in one
picture) is the figure this chapter needed, and all eight figures are stylistically consistent,
all referenced, and all captioned with what to notice. The worked example is exemplary: every
number in `tab:ch12-trace`, the fall of the feasible count `695 -> 122`, the path length
`10.027`, the no-avoidance minimum `0.377` at `t = 5.2 s` against the continuous `0.372` at
`t* = 5.249 s`, and the `t_c = 0.013 s` of the preferred velocity at `t = 5.0 s` all come
straight out of the code. Keep the "what is not guaranteed" list in `sec:ch12-properties`,
the oscillation section with its `51` sign changes against `1`, and the `n = 2..8` experiment
that shows the `cor:ch12-intruder` guarantee holding exactly (`1.0003`) against
non-cooperative intruders and dissolving (`0.914` at `n = 6`) as soon as everybody avoids -
that is an honest, quantitative motivation for `\cref{ch:ch13}` rather than a hand-wave. The
four pitfalls are precisely the four the spec asks for and are each written from a symptom the
reader will actually observe; the drone box's distinction between a non-cooperative intruder
(full responsibility, plain VO) and a swarm member (reciprocal) is sharp and correct; and the
3D section, with the tangency circle at `(d^2-R^2)/d` of radius `R sqrt(d^2-R^2)/d` and the
`(3,4,12)` self-test, earns its page.
