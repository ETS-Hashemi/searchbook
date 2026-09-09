# Review of Chapter 12 (Velocity Obstacles) - round 1

Reviewed artefacts: `Overleaf/chapters/ch12-velocity-obstacles.tex` (1489 lines),
`Overleaf/figures/ch12/{idea,geometry,truncated,feasible,example,oscillation,crossing,cone3d}.tex`,
`Overleaf/code/ch12_velocity_obstacles.py` (658 lines), `Overleaf/code/figures/gen_ch12_sim.py`,
`Overleaf/appendices/solutions/ch12-solutions.tex`, `Overleaf/appendices/glossary/ch12-terms.tex`,
`Overleaf/references.bib`, `Overleaf/frontmatter/notation.tex`, `docs/specs/ch12.md`,
`docs/core-idea.txt` (Week 6), `STYLE_GUIDE.md` section 9.

Build: `./build.sh ch12-velocity-obstacles` exits 0, no `!` errors, no citation warnings, no
undefined labels belonging to this chapter (the `??` are `ch:ch13`, `ch:ch14`, `ch:ch18`,
`ch:ch19`, `ch:ch20`, `ch:ch24`, i.e. other chapters, as expected in a single-chapter build).
The only overfull box (29.10 pt) is in the *List of Algorithms* and comes from an RRT caption of
another chapter, not from Chapter 12. Chapter body = PDF pages 21-42 = **22 pages**, inside the
24-page limit (but 7 pages above the spec's own 13-15 target; see Suggestions).

Code: `python3 code/ch12_velocity_obstacles.py` passes in 0.3 s. Every number in
Section 12.5, Table 12.1 (all 10 rows), Table 12.2 (all 7 x 8 cells), the oscillation narrative
(51 sign changes, min separation 1.002, 1 sign change with a single avoider) and the two
experiment paragraphs was reproduced by re-running the code and `code/figures/gen_ch12_sim.py`.
I also re-derived the geometry independently: `theta = arcsin(1/sqrt(50)) = 8.13 deg`, legs
`(0.8,-0.6)` / `(0.6,-0.8)`, `Delta/4 = 90.25 - 88.69 = 1.56`, `t_c = 4.5586 s`, exit at
`5.9386 s`, truncation disc `D((1,-0.1), 0.2)`, exact projection `v* = (1, 0.1)`,
`t* = 9.5/1.81 = 5.249 s` with closest distance `0.3716 m`, empty-set threshold
`v_max d/R = 10.6 m/s`, tangency distances `(d-R)/tau = 1.214` and `sqrt(d^2-R^2)/tau = 1.4`.
All correct.

## Verdict

**Minor revision.** The chapter is technically sound, complete against the spec and the Week-6
training plan, and unusually well instrumented: every quoted number is reproducible. Six local
defects must be fixed: two pseudocode/code mismatches at `tau = infinity`, one muddled step in
the proof of Proposition 12.6, one self-test timing/scope claim the code contradicts, one figure
caption whose time does not match the plotted data, one banned word, and the missing half of the
exercise solutions. Every one of them is a sentence- or line-level edit; nothing structural.

## Required changes

1. **`alg:ch12-ttc`, function `\VoInside`, line 558 (and the walkthrough at lines 574-577)
   - the membership test is wrong for `tau = infinity`.** (Category A.)
   The pseudocode returns `t <= tau`. When there is no collision `\VoTimeToCollision` returns
   `t = infinity`, and `infinity <= infinity` is *true*, so with `tau = infinity` the test
   declares **every** velocity dangerous - the exact opposite of the walkthrough's claim on
   line 576-577 ("with `tau = infinity` it tests membership in the untruncated `VO_{A|B}`").
   The Python is correct (`return tc < math.inf and tc <= tau`, listing `lst:ch12-ttc`), so the
   pseudocode and the listing currently disagree.
   *Fix:* change line 558 to `\KwRet{$t < \infty$ \textnormal{and} $t \le \ttc$}\;` and, in the
   walkthrough, add one clause noting that the `t < infinity` guard is what makes
   `tau = infinity` give the untruncated obstacle.

2. **`alg:ch12-choose`, line 591 (`\label{alg:ch12-choose:feasible}`) - same defect in the
   feasible-set line.** (Category A.)
   `F <- {v in S : t_min(v) > tau}` is empty when `tau = infinity`, so the algorithm would always
   fall through to the penalised fallback of line 595. The code guards this explicitly
   (`feasible = (tc > tau) | np.isinf(tc)`, listing `lst:ch12-choose`).
   *Fix:* write `$F \gets \set{\vel \in S : t_{\min}(\vel) > \ttc \ \text{or}\ t_{\min}(\vel) = \infty}$`
   and keep the sentence in the walkthrough that this is membership in the union of
   `\cref{eq:ch12-feasible}`.

3. **Proof of Proposition `thm:ch12-truncated` (shape of the truncated VO), lines 428-432 - the
   final step conflates the collision time `t` with the ray parameter.** (Category A.)
   "Along a fixed ray inside the cone, the times at which the point `t v` is inside the original
   disc form one interval `[t_c, t_2]`, so the union over `t <= tau` contains the ray's points
   beyond the first entry into the disc for `t = tau` and nothing before it" is not a proof: the
   set being described is a set of *velocities* on the ray, not of times, and the sentence never
   says which velocities.
   *Fix:* replace the sentence by the scaling identity, which is two lines and exact. From
   `\cref{eq:ch12-collision}`, for every `s > 0` and every relative velocity `v`,
   `t_c(s v) = t_c(v)/s`. Fix a unit direction `u` inside the cone. Then
   `t_c(s u) <= tau  <=>  s >= t_c(u)/tau`, so the truncated set meets the ray in the half-line
   `{s u : s >= t_c(u)/tau}`, whose endpoint `(t_c(u)/tau) u` is exactly the point at which the
   ray enters `D(p_rel/tau, R/tau)`. Hence the truncated obstacle is the part of the cone at or
   beyond that disc, and its boundary is the near arc of the disc together with the two legs
   beyond their tangency points with it.

4. **Section 12.9 ("Sampling versus solving exactly"), lines 1184-1186 - a run time and a scope
   claim that the code does not reproduce.** (Category A.)
   The text says "the whole self-test, including the experiments of `\cref{sec:ch12-experiment}`,
   runs in about 0.2 s". Running `python3 code/ch12_velocity_obstacles.py` prints
   `ch12 self-test passed (0.3 s)`, and `_self_test()` runs only `k in {1,4,8}` of the stream
   family and `n in {2,4,6}` of the circle family - the numbers of Table 12.2 and Figure 12.7
   (`n = 2..8`) are produced by `code/figures/gen_ch12_sim.py`.
   *Fix:* "which is why the self-test, including a sample of the experiments of
   `\cref{sec:ch12-experiment}`, runs in about `0.3 s`; the full sweep of
   `\cref{tab:ch12-crossing}` is produced by `code/figures/gen_ch12_sim.py`."

5. **Caption of `fig:ch12-example`, panel (b), lines 704-705 - the quoted interval does not match
   the plotted curve.** (Category D.)
   The caption says A "speeds up to 1.2 m/s between `t=1` and `t=3.6 s`". The plotted data
   (`figures/data/ch12-example-traj.dat`, column `avx`) hold `v_Ax = 1.2` from **`t = 0.9 s`** to
   `t = 3.6 s`; a reader who measures the figure will not find the stated start.
   *Fix:* "between `t=0.9` and `t=3.6\,\mathrm{s}`".

6. **Line 1180 - banned word.** (Category C.)
   "sampling is robust and *trivially* accepts other cost functions" violates the rule of
   `STYLE_GUIDE.md` section 3 ("Never write 'obviously', 'clearly', 'trivially' or 'it is easy to
   see'").
   *Fix:* "sampling is robust and accepts other cost functions and reachable sets without any
   change to the rule".

7. **`Overleaf/appendices/solutions/ch12-solutions.tex` - only 4 of the 8 exercises have a
   solution.** (Category E.)
   Present: `exr:ch12-tangent`, `exr:ch12-ttc`, `exr:ch12-empty`, `exr:ch12-coding`. Missing:
   `exr:ch12-halfangle`, `exr:ch12-truncation`, `exr:ch12-static`, `exr:ch12-3d` - i.e. exactly
   the numeric and geometric exercises a reader working alone cannot otherwise check. All four
   are short; the numbers are already established in the chapter:
   * `exr:ch12-halfangle`: `theta = arcsin(0.8/4) = 11.54 deg` (wedge `23.07 deg`); with `r_A`
     forgotten `arcsin(0.5/4) = 7.18 deg` (`14.36 deg`); with both forgotten `0 deg` (a ray).
     `theta = 30 deg` at `d = R/sin 30 = 1.6 m`; as `d -> R` the half-angle tends to `90 deg` and
     the cone becomes the whole half-plane of approaching velocities.
   * `exr:ch12-truncation`: use the identity `t_c(s v) = t_c(v)/s` of required change 3; closest
     point of the truncated obstacle to the apex `(d-R)/tau`, tangency points at
     `sqrt(d^2-R^2)/tau`; for `d = sqrt(50)`, `R = 1`, `tau = 5`: `1.214` and `1.4`, and the
     tangency point `(0,0.9)+1.4*(0.8,-0.6) = (1.12, 0.06)` is at distance exactly `0.2` from the
     truncation centre `(1,-0.1)`, as Figure 12.2(b) shows.
   * `exr:ch12-static`: (a) `v_B = 0` makes `\cref{eq:ch12-vo}` the identity; (b) the union of the
     cones of the points of a convex set is the wedge between its two extreme supporting tangent
     rays, since the cone of a set is the image of the set under the (convex-set-preserving)
     radial projection onto directions; (c) with the wall inflated by `r_A = 0.5` its face is at
     `1.5 m`, so the untruncated obstacle forbids every velocity with a positive normal component
     towards the wall, and with `tau = 4 s` only those whose normal component exceeds
     `1.5/4 = 0.375 m/s`.
   * `exr:ch12-3d`: the proof of `\cref{thm:ch12-cone}` verbatim with 3-vectors (only
     `d sin phi <= R` is used, and `phi` is the angle between two vectors in space); the tangency
     circle has centre at distance `(d^2-R^2)/d` from the apex along the axis and radius
     `R sqrt(d^2-R^2)/d`.
   *Fix:* add these four `\begin{solution}{...}` blocks.

## Suggestions

* **Length (22 pages against the spec's 13-15).** Nothing is padding in the harmful sense, but
  three passages are genuinely duplicated and could be trimmed by roughly a page and a half
  without losing content: (i) lines 375-381 work the `t_c = 4.559 s` computation in full, and
  Section 12.6 (lines 674-681) works it again - keep the full computation in the worked example
  and reduce lines 375-381 to the sentence about `Delta/4 = |v|^2 (R^2 - d^2 sin^2 phi)`;
  (ii) the RVO/HRVO/ORCA remedy is described twice, at lines 922-931 and again in the
  "Reciprocal variants" paragraph at lines 1042-1049 - keep the second and shorten the first to
  one forward-pointing sentence; (iii) the closing paragraph of Section 12.7.2 (lines 991-1008)
  restates Table 12.2 row by row and can be halved.
* **Line 727:** "by `t=5.5 s` the preferred velocity is feasible again" is true but loose - the
  data show `t_c(v^pref) = infinity` from `t = 5.1 s`. Use `5.1` for consistency with the exact
  times in the neighbouring sentences.
* **Point at the exact ch02 results, not the whole chapter.** Lines 179-181, 250-251, 341-343 and
  1017-1018 all say "of `\cref{ch:ch02}`". Chapter 2 has `\cref{thm:ch02-disc-minkowski}`
  (Minkowski sum of two discs), `\cref{thm:ch02-ray-circle}` (ray-circle intersection, with the
  tangent cone drawn in its figure and explicitly labelled "this cone is the velocity obstacle of
  Chapter 12") and `\cref{def:ch02-point-segment-distance}`. Citing them by label makes the
  chapter genuinely self-checking for a lone reader.
* **`closest_boundary_point` is called "the function" at lines 686, 1066-1067 and 1179**, but it
  is a method of the `VelocityObstacle` class (`code/ch12_velocity_obstacles.py`, line 194). Say
  "the method `VelocityObstacle.closest_boundary_point`" so a reader can find it.
* **Difficulty spread (E).** The eight exercises are graded 1,2,2,1,2,2,3,2 - only the coding
  exercise is a 3. Consider promoting `exr:ch12-3d` to `\difficulty{3}` (it asks for a proof plus
  a 3D sampler) or adding a 3-star pen-and-paper item, e.g. proving the non-linear velocity
  obstacle of Section 12.8 (the forbidden set is `union_{t<=tau} D((phat_B(t)-p_A)/t, R/t)`) and
  showing that it is no longer a cone.
* **`gen_ch12_sim.py` prints `min_sep` with three decimals**, so the claim "the recorded minimum
  is 1.0003" (line 993) cannot be checked from the script's own output. I verified it by calling
  `stream_metrics` directly (`1.00033` for `k = 2, 4, 8`); printing four decimals in the script
  would make the chapter self-verifying.
* **Figure 12.7 caption** says the stream keeps the distance "at exactly `R`". It is `1.0003`,
  i.e. just above `R`, which is what Corollary 12.12 promises; "at the guaranteed minimum `R`"
  would be more precise, since "exactly `R`" reads as touching.
* **Further reading** could add one sentence on the non-linear velocity obstacle (Large, Sekhavat,
  Shiller) that Section 12.8 introduces without a citation, and on the `k`-nearest-neighbour
  restriction mentioned in the complexity paragraph.

## What must be kept

The geometric spine of this chapter is excellent and should survive any revision untouched.
Theorem 12.1 and its proof (the `arcsin(R/d)` half-angle derived from the perpendicular distance
from the disc centre to the ray, with the `phi > pi/2` case handled explicitly) is the cleanest
statement of the collision cone I have read in a textbook, and Proposition 12.3 with the
observation that `Delta/4 = |v|^2 (R^2 - d^2 sin^2 phi)` makes the discriminant condition and the
cone condition the same fact - that identity is a real pedagogical find. The treatment of
truncation as the union of the scaled discs `D(p_rel/t, R/t)`, each inscribed in the cone, is the
right way to teach it and generalises immediately to the non-linear VO in Section 12.8; keep it.
Figure 12.2 (workspace next to velocity space, with the `3-4-5` tangent directions, the truncation
disc, the exact projection and the sampled choice all in one picture) is the figure this chapter
needed, and the eight figures are stylistically consistent and all referenced. The worked example
is exemplary: every one of the roughly forty numbers I checked - the trace table, the counts of
feasible samples falling `695 -> 122`, the path length `10.027`, the no-avoidance minimum `0.377`
at `t = 5.2 s` against the continuous `0.372` at `t* = 5.249 s` - comes out of the code exactly.
The "what is not guaranteed" list in Section 12.6.3, the oscillation section with its 51 sign
changes and the `n = 2..8` experiment that shows the guarantee dissolving as soon as both agents
avoid (a genuine, honest motivation for Chapter 13 rather than a hand-wave), the four pitfalls -
which are exactly the four the spec asks for and are each written from a symptom a reader will
actually observe - the drone box's sharp distinction between a non-cooperative intruder (full
responsibility, plain VO) and a swarm member (reciprocal), and the 3D section with the tangency
circle at `(d^2-R^2)/d` are all first-rate and must be kept.

## Response to review (round 1)

All seven required changes were applied. The chapter builds with status 0 and no
errors (`cd Overleaf && ./build.sh ch12-velocity-obstacles`), the self-test passes
(`ch12 self-test passed (0.3 s)`), and the three `.dat` files are byte-identical
after re-running `code/figures/gen_ch12_sim.py`.

### Required changes

1. **`\VoInside` returns `t <= tau` (A).** Fixed. The pseudocode line now reads
   `\KwRet{$t < \infty$ \textnormal{and} $t \le \ttc$}`, matching
   `lst:ch12-ttc`. The walkthrough gained a clause saying that the `t < infinity`
   guard is what makes the limit case work: without it the convention
   `inf <= inf` would report every collision-free velocity as dangerous, and it is
   precisely this guard that makes `tau = infinity` test membership in the
   untruncated `VO_{A|B}`.
2. **Feasible set in `alg:ch12-choose` (A).** Fixed. Line
   `alg:ch12-choose:feasible` now reads
   `F <- {v in S : t_min(v) > tau or t_min(v) = infinity}`, matching
   `feasible = (tc > tau) | np.isinf(tc)`. The walkthrough keeps the sentence that
   this is membership in the union of `eq:ch12-feasible`, with the added
   parenthesis that `t_min = infinity` (no collision at all) counts as safe.
3. **Proof of `thm:ch12-truncated` (A).** The final sentence was replaced by the
   scaling argument the reviewer proposed. The identity `t_c(s v) = t_c(v)/s` is
   now displayed and labelled `eq:ch12-scaling`; for a unit direction `u` inside
   the cone, `t_c(s u) <= tau` iff `s >= t_c(u)/tau`, so the truncated set meets
   the ray in the half-line `{s u : s >= t_c(u)/tau}` whose endpoint is exactly
   where the ray enters `D(p_rel/tau, R/tau)` (shown by rewriting the disc
   inequality as `|p_rel - (tau s) u| <= R`). The boundary claim now follows.
   `eq:ch12-scaling` is reused by the new solution to `exr:ch12-truncation`.
4. **Self-test timing and scope (A).** Rewritten exactly as suggested: "the
   self-test, including a sample of the experiments of `sec:ch12-experiment`, runs
   in about 0.3 s; the full sweep of `tab:ch12-crossing` is produced by
   `code/figures/gen_ch12_sim.py`." Verified: the script prints
   `ch12 self-test passed (0.3 s)`.
5. **Caption of `fig:ch12-example`, panel (b) (D).** Changed to "between
   $t=0.9$ and $t=3.6\,\mathrm{s}$", which is what column `avx` of
   `figures/data/ch12-example-traj.dat` holds.
6. **"trivially" (C).** Replaced by "sampling is robust and accepts other cost
   functions and reachable sets without any change to the rule".
7. **Missing solutions (E).** `appendices/solutions/ch12-solutions.tex` now holds
   all eight solutions, in exercise order. The four new blocks follow the
   reviewer's outlines: `exr:ch12-halfangle` (11.54 deg / 23.07 deg wedge; 7.18 deg
   / 14.36 deg with `r_A` forgotten; 0 deg with both forgotten; `d = 1.6` m for
   30 deg; `theta -> 90` deg as `d -> R`), `exr:ch12-truncation` (the scaling
   identity, `(d-R)/tau = 1.2142` and `sqrt(d^2-R^2)/tau = 1.4`, with both points
   checked to lie at distance exactly 0.2 from the truncation centre `(1,-0.1)`),
   `exr:ch12-static` (`v_B = 0` makes `eq:ch12-vo` the identity; the convexity
   argument for the wedge; wall face at 1.5 m, normal component 0 vs 0.375 m/s)
   and `exr:ch12-3d` (the proof of `thm:ch12-cone` with 3-vectors, tangency circle
   at `(d^2-R^2)/d` with radius `R sqrt(d^2-R^2)/d`, evaluated for the self-test
   geometry `(3,4,12)`). The file compiles with zero errors inside
   `appC-solutions` (the errors that build reports come from `ch05-solutions`,
   which is not this chapter's file).

### Suggestions adopted

* **Length.** Kept at 22 chapter pages (folios 115-136) despite the longer proof
  and the added further-reading sentences, by making the three trims the reviewer
  identified: the `t_c = 4.559` arithmetic is now worked once, in the worked
  example (Section 12.5 keeps the `Delta/4 = |v|^2 (R^2 - d^2 sin^2 phi)` identity
  and points forward); the RVO/HRVO/ORCA remedy is described once, in "Reciprocal
  variants", with the oscillation section pointing to it; and the closing
  paragraph of the crossing experiment was shortened.
* **`t = 5.5` -> `t = 5.1`.** Done; the `tc_pref` column of the trajectory data
  turns infinite at `t = 5.1` s.
* **Exact Chapter 2 pointers.** `\cref{ch:ch02}` replaced by
  `thm:ch02-disc-minkowski` (relative motion), `thm:ch02-tangents` (tangent
  points), `thm:ch02-ray-circle` (ray-circle intersection) and
  `thm:ch02-inflation` plus `def:ch02-point-segment-distance` (inflated
  obstacles). All four resolve in the build.
* **`closest_boundary_point`.** Now named as a method of `VelocityObstacle` at all
  three places.
* **Difficulty spread.** `exr:ch12-3d` promoted to `\difficulty{3} Proof`, giving
  1,2,2,1,2,2,3,3.
* **Four decimals.** `gen_ch12_sim.py` now prints `min_sep` with `%.4f`, so
  `stream k=2,4,8: VO sep 1.0003` can be read off its own output. The `.dat`
  files are unchanged.
* **Figure 12.7 caption.** "keeps the distance at the guaranteed minimum $R$
  ($1.0003$)".
* **Further reading.** Added the non-linear velocity obstacle of Large, Sekhavat,
  Shiller and Laugier (ICARCV 2002, new entry `large2002nonlinear` in
  `bib/ch12-extra.bib`) and a sentence on restricting the union to the `k` nearest
  neighbours.

### Not changed

Everything on the reviewer's "must be kept" list is untouched: `thm:ch12-cone`
and its proof, the `Delta/4` identity, the union-of-scaled-discs treatment of
truncation, all eight figures, the worked example and its trace table, the "what
is not guaranteed" list, the oscillation section, the `n = 2..8` experiment, the
four pitfalls, the drone box and the 3D section. No verified number was altered;
every number quoted in the text was re-checked against the code output.
