# Review of Chapter 12 (Velocity Obstacles) - round 3

Reviewed artefacts: `Overleaf/chapters/ch12-velocity-obstacles.tex` (1520 lines),
`Overleaf/figures/ch12/{idea,geometry,truncated,feasible,example,oscillation,crossing,cone3d}.tex`,
`Overleaf/code/ch12_velocity_obstacles.py` (658 lines), `Overleaf/code/figures/gen_ch12_sim.py`,
`Overleaf/figures/data/ch12-{example-traj,oscillation,crossing}.dat`,
`Overleaf/appendices/solutions/ch12-solutions.tex`, `Overleaf/appendices/glossary/ch12-terms.tex`,
`Overleaf/references.bib`, `Overleaf/bib/ch12-extra.bib`, `Overleaf/frontmatter/notation.tex`,
`docs/specs/ch12.md`, `docs/core-idea.txt` (Week 6), `STYLE_GUIDE.md` section 9,
and `reviews/ch12-round2.md` including the reviser's response.

**Build.** `cd Overleaf && ./build.sh ch12-velocity-obstacles` exits 0. No `!` errors, no
citation warnings, no undefined label belonging to Chapter 12 (the remaining `??` are
`ch:ch11`, `ch:ch13`, `ch:ch14`, `ch:ch19`, `ch:ch20`, `ch:ch21`, i.e. other chapters, as
expected in a single-chapter build). The one overfull box (29.10 pt) is in
`build/only-ch12-velocity-obstacles.loa`, from the *List of Algorithms* caption
"Rapidly-exploring random tree with goal bias" - another chapter's. Chapter body = PDF
folios 115-136 = **22 pages**, inside the 24-page limit.

**Code.** `python3 code/ch12_velocity_obstacles.py` prints `ch12 self-test passed (0.2 s)`.
`python3 code/figures/gen_ch12_sim.py` regenerates all three `.dat` files byte-identically
(`git status` clean afterwards). I re-derived and re-checked independently: `theta =
arcsin(1/sqrt50) = 8.130 deg`, leg directions `(0.8,-0.6)`/`(0.6,-0.8)` with tangency at
`(5.6,-4.2)`/`(4.2,-5.6)` (both at distance `1` from `(5,-5)` and perpendicular to their
legs), `Delta/4 = 90.25-88.69 = 1.56`, roots `4.5586`/`5.9387`, `v* = (1,0.1)` with
`t_c = 5.0000` exactly and `|dv| = 0.1`, sampled `v' = (0.8966,0.0784)` = speed `0.9` at
`5 deg` with `|dv| = 0.1298`, `t_c = 5.027`, `695` of `722` feasible, `t* = 9.5/1.81 =
5.2486` with miss distance `0.3717`, path `10.0270`, no-avoidance minimum `0.3774` at
`t = 5.2`, `d = 1.0012` at `t = 5.0` (half-angle `87.2 deg`), the `n=1` discriminant of
`(1.2,-0.9)` at `t = 1 s` (`-0.11 < 0`), the threshold `v_max d/R = 10.6`, `(d-R)/tau =
1.2142` and `sqrt(d^2-R^2)/tau = 1.4` (both points at distance exactly `0.2` from
`(1,-0.1)`), the 3D tangency circle at `168/13 = 12.923` of radius `sqrt(168)/13 = 0.997`,
`n(n-1)m = 40432` for `n=8`, `721 = 1 + 10*72` samples, and **every cell** of
`tab:ch12-trace` and `tab:ch12-crossing` against the code's stdout and the `.dat` files
(`1.0003` stream minimum, `11.3`-`11.5 s` arrival, `1.4`-`2.3 %` stream ratio,
`0.914` at `n=6`, `14.2 %` maximum circle ratio, `pairs<R` and `empty` columns). Both
listings are verbatim substrings of the `.py` file (23 and 34 lines, under the 45-line cap).

**Round-2 items.** All three required changes of round 2 are correctly resolved and are not
re-raised. (1) The worked-example sentence now reads "the half-angle is almost $90^\circ$
($d = 1.0012\,\mathrm{m} \approx R$), so the wedge is nearly a half-plane"; `1.0012` is the
code's own `min separation` and `sep_vo` value, and `arcsin(1/1.0012) = 87.2 deg`, so the
factor-of-two error is gone and the number is the right one. (2) `sec:ch12-intuition` now
says "drifts at the rate $\vel_B - \vel_A$, the negative of the relative velocity of
\cref{def:ch12-relative}", consistent with the definition, the notation table and the
glossary. (3) CBS, ECBS, RVO and ORCA are all expanded at first use. The six accepted
suggestions are also in place and correct: the `proof` environment on `thm:ch12-cone3d`, the
merged implementation paragraph, the `1.4`-`2.3 %` caption, the `3`-`4`-`5` leg-direction
wording, the interval-wise justification in the proof of `cor:ch12-intruder`, and the four
exact Chapter-2 labels (`thm:ch02-disc-minkowski`, `def:ch02-single-integrator`,
`def:ch02-point-segment-distance`) - all of which resolve in the build.

**Bibliography.** I can now vouch for all six keys: Fiorini & Shiller, IJRR 17(7):760-772,
1998; van den Berg, Lin & Manocha, ICRA 2008, 1928-1935; van den Berg, Guy, Lin & Manocha,
*Reciprocal n-Body Collision Avoidance*, ISRR, STAR 70:3-19, 2011; Snape, van den Berg, Guy
& Manocha, T-RO 27(4):696-706, 2011; Choset et al., MIT Press 2005; and
`large2002nonlinear` (Large, Sekhavat, Shiller & Laugier, *Using Non-Linear Velocity
Obstacles to Plan Motions in a Dynamic Environment*, ICARCV 2002) - the title wording
queried in round 2 is the correct one, and the entry carries no page numbers. Nothing is
fabricated.

## Verdict

**Minor revision.** The chapter is technically accurate, complete against every "must cover"
item of `docs/specs/ch12.md` and against Week 6 of the training plan, and every number in the
worked example, the two tables, the eight figure captions and the eight solutions is
reproduced by the code. Two defects remain, both in the same paragraph of
`sec:ch12-oscillation` and both purely local: the head-on scenario is described with the
wrong goals, and the amplitude of the oscillating command is quoted as a symmetric
`+-0.2` that the data do not show. No proof, formula, algorithm, table, figure or exercise
needs to change.

## Required changes

1. **`sec:ch12-oscillation`, first sentence (line 916, PDF p.128) - the head-on scenario is
   described with the wrong goals.** (Category A.)
   The text says "Let two identical agents fly head-on towards *each other's start
   positions*, $A$ from $(-5,0)$ and $B$ from $(5, 0.2)$". The code that produced
   `fig:ch12-oscillation` does something else: `head_on_scenario` in
   `code/ch12_velocity_obstacles.py` (lines 383-389) is
   `Agent((-5.0, 0.0), (5.0, 0.0), ...)` and `Agent((5.0, offset), (-5.0, offset), ...)`, so
   each agent flies to the point opposite *its own* start, along a line parallel to the
   other's; the `0.2` offset is in the starts *and* the goals. The difference is not
   cosmetic: with the goals as the text states them, both preferred velocities acquire a
   lateral component of `0.02` towards the other's line, and a reader reproducing the
   experiment gets a different picture and a different sign-change count. It also makes the
   later sentences "so $A$ returns to $(1,0)$, and $B$, by symmetry, returns to $(-1,0)$"
   exactly true only under the code's version (at $t=0$ the preferred velocities are
   $(1,0)$ and $(-1,0)$ to machine precision).
   *Fix:* replace the clause by "Let two identical agents fly head-on along parallel lines
   offset laterally by $0.2$ --- $A$ from $(-5,0)$ to $(5,0)$ and $B$ from $(5,0.2)$ to
   $(-5,0.2)$ --- both at speed $1$ with $R = 1$, and let \emph{both} apply
   \cref{alg:ch12-choose} at every step."

2. **`sec:ch12-oscillation`, same paragraph (line 928, PDF p.128) - "the velocity command
   chatters between roughly $\pm0.2$ and $0$ at every step" is not what the data show.**
   (Category A: a number the code does not reproduce.)
   In `figures/data/ch12-oscillation.dat` the lateral velocity `avy` of $A$ takes exactly two
   kinds of value in alternation: about $-0.1823$ (with a single peak of $-0.2329$) and a
   small *positive* value that starts at $+0.0018$ and grows to at most $+0.0832$ as $A$
   drifts below its line. `gen_ch12_sim.py` prints `max |v_Ay| 0.233`. The command therefore
   never approaches $+0.2$; it alternates between a sizeable sidestep and (essentially) the
   preferred velocity. The `51` sign changes are real, but they are crossings between
   $-0.18$ and a value just above zero, not swings of amplitude $\pm0.2$.
   *Fix:* replace the clause by "the command alternates at every step between a sidestep of
   about $-0.18\,\mathrm{m/s}$ (peak $0.23$) and a lateral component just above zero, so it
   crosses zero at almost every decision". If a symmetric picture is wanted, say instead
   "the lateral command jumps between $-0.18\,\mathrm{m/s}$ and $\approx 0$ at every step".

## Suggestions

* **`sec:ch12-implementation`, "runs in about $0.3\,\mathrm{s}$".** The self-test prints
  `0.2 s` on this machine (and in round 2). Wall-clock is machine-dependent, so nothing is
  wrong, but "runs in a fraction of a second" or "in well under a second" (the phrase already
  used two paragraphs earlier) would not need re-checking on every future build.
* **Caption of `fig:ch12-oscillation`, "Two agents swap places head-on with a lateral offset
  of $0.2$".** Once required change 1 is applied, "swap places" is slightly off - they swap
  $x$-positions but keep their own $y$ lines. "Two agents pass each other head-on along lines
  offset by $0.2$" matches the scenario and the fixed body text.
* **`sec:ch12-implementation`, "Always add the preferred velocity and, to reduce chattering,
  the current velocity to the candidates".** The book's own `choose_velocity` adds only
  `v_pref` (line `cand = np.vstack([samples, np.asarray([v_pref])])`, quoted in
  `lst:ch12-choose`), so a reader may take this as a description of the code rather than as
  advice. Two extra words - "in your own implementation, always add ..." - remove the
  ambiguity.
* **Residual near-duplication.** "Exact selection" (`sec:ch12-variants`) and the pitfall
  *Discretisation of the velocity samples* both close with "prefer the exact projection when
  there is a single obstacle", and the horizon is discussed both at the end of
  `sec:ch12-truncated` and under "The horizon" in `sec:ch12-implementation`. At 22 pages the
  chapter is inside the limit, so no cut is required and none of this is padding of the kind
  that must go; but dropping the repeated closing clause of the pitfall would tighten it at
  no cost. Do **not** cut any of the derivations, the experiment or the 3D section to reach
  the spec's 13-15 page target - the content is all mandated by the spec.
* **`sec:ch12-example`, "the relative velocity $(1.2,-0.9)$ passes the disc on the far
  side".** "Far side" is ambiguous in velocity space. "passes the disc on the side away from
  $B$'s motion (in the workspace, $A$ crosses in front of $B$)" would tie the sign of the
  miss to the picture the reader has in `fig:ch12-example`(a).
* **`thm:ch12-empty`.** Worth one half-sentence noting that the hypothesis $s > v_{\max}$ is
  implied by the conclusion (since $d > R$ gives $v_{\max}d/R > v_{\max}$), so the
  proposition is really a threshold statement about $s$ alone; a careful reader currently
  pauses on the two speed conditions.
* **`exr:ch12-tangent`(b).** The step "$(\lambda-1)\vel_B$ is a difference of cone vectors
  for every $\lambda$, which fails for $\vel_B \ne \vect{0}$" in the solution is the one
  place in the solutions file where the argument is compressed to the point of being hard to
  follow. A one-line concrete counterexample (take $\vel$ on a boundary ray and
  $\lambda \to 0^+$, so $\lambda(\vel_B+\vel) \to \vect{0} \notin \VO$ whenever
  $-\vel_B \notin CC_{A|B}$) would make it self-contained.

## What must be kept

The geometric spine of this chapter remains the best treatment of velocity obstacles I have
read at textbook level, and it must survive untouched. `thm:ch12-cone` and its proof - the
`arcsin(R/d)` half-angle obtained from the perpendicular distance from the disc centre to the
*ray*, with the `varphi > pi/2` case handled explicitly rather than waved away - the
observation that `Delta/4 = |v|^2 (R^2 - d^2 sin^2 varphi)` makes the discriminant condition
and the cone condition literally the same fact, and the treatment of truncation as the union
of the inscribed scaled discs `D(p_rel/t, R/t)` (which then generalises for free to the
non-linear velocity obstacle and to 3D) are a genuine pedagogical find. The proof of
`thm:ch12-truncated` with the scaling identity `eq:ch12-scaling`, reused by the solution to
`exr:ch12-truncation`, is exactly right; do not touch it. `fig:ch12-geometry` - workspace
beside velocity space, with the `3`-`4`-`5` legs, the truncation disc, the exact projection
`v* = (1,0.1)` and the sampled choice in one picture - is the figure this chapter needed, and
all eight figures are stylistically consistent, all referenced, and all captioned with what to
notice. The worked example is exemplary: every number in `tab:ch12-trace`, the fall of the
feasible count `695 -> 122`, the path length `10.027`, and the `t_c = 0.013 s` of the
preferred velocity at `t = 5.0 s` come straight out of the code, and the two-detail paragraph
after the table (now with the correct half-angle) is the kind of commentary a reader working
alone needs. Keep the "what is not guaranteed" list in `sec:ch12-properties`, the oscillation
section with its `51` sign changes against `1`, and the `n = 2..8` experiment showing the
`cor:ch12-intruder` guarantee holding exactly (`1.0003`) against non-cooperative intruders and
dissolving (`0.914` at `n = 6`) as soon as everybody avoids - that is an honest, quantitative
motivation for `\cref{ch:ch13}` rather than a hand-wave. The four pitfalls are precisely the
four the spec asks for and are each written from a symptom the reader will actually observe;
the drone box's distinction between a non-cooperative intruder (full responsibility, plain VO)
and a swarm member (reciprocal) is sharp and correct; the 3D section, with the tangency circle
at `(d^2-R^2)/d` of radius `R sqrt(d^2-R^2)/d` and the `(3,4,12)` self-test, earns its page;
and the eight solutions in `appendices/solutions/ch12-solutions.tex` are complete, correct and
worth their length.
