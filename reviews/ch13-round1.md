# Review of Chapter 13 (Reciprocal Avoidance: RVO and ORCA) - round 1

## Verdict

**Minor revision.**

This is a strong, technically careful chapter. I checked every definition, lemma, theorem,
proof, pseudocode line and complexity claim against the canonical sources (Fiorini & Shiller
1998; van den Berg, Lin & Manocha, ICRA 2008; van den Berg, Guy, Lin & Manocha, ISRR 2011;
Snape et al., T-RO 2011; Alonso-Mora et al., DARS/STAR 83; Seidel 1991; de Berg et al. ch. 4)
and against the RVO2 reference implementation (`Agent::computeNewVelocity`,
`linearProgram1/2/3`). The case analysis of `\cref{thm:ch13-cases}`, `\cref{alg:ch13-halfplane}`,
`\cref{alg:ch13-lp}` and `\cref{alg:ch13-dense}` agree with RVO2 line for line, including the
arc test `w.p < 0 and (w.p)^2 > r^2|w|^2`, the leg directions, the normal orientations, the
chord discriminant `b^2 + v_max^2 - |q_i|^2`, and the `den/num` clipping rule. The proofs of
`\cref{thm:ch13-convex}` (convexity of `VO^tau` via `1/t = lambda/t_1 + (1-lambda)/t_2`),
`\cref{thm:ch13-pairwise}` (adding the two half-plane inequalities) and `\cref{thm:ch13-lp}`
(backwards analysis, 2/i) are correct. I re-derived the whole worked example by hand
(`theta = 14.3633 deg`, `d_R = (0.9920,-0.1260)`, `q = (1.9682,-0.2500)`, `u = (-0.0318,-0.2500)`,
`n = (-0.1260,-0.9920)`, violation `0.1512`, `v_A^new = (1.1809,-0.1500)`) and everything matches
both the table and the code.

Build: status 12 only because of the expected cross-chapter `??` in a single-chapter build;
no `!` errors, no overfull box above 15 pt, no undefined label or citation belonging to this
chapter. `python3 code/ch13_orca.py` passes its self-test in 2.1 s and
`python3 code/figures/gen_ch13_circle.py` reproduces every number of
`\cref{tab:ch13-circle}` and of `\cref{fig:ch13-dance}` exactly. Both listings are verbatim
excerpts of the source (only the docstrings are dropped, as the captions say). Every "must
cover" item of `docs/specs/ch13.md` and every Week-6 item of the training plan is present.
Six figures, all referenced, all TikZ/pgfplots with the shared styles; 24 index entries; ten
exercises with a 1/1/2/2/2/2/2/2/3/3 spread including the Week-6 coding exercise; all nine
cited keys exist and their bibliographic details are correct.

The chapter body is pages 37-60 of the single-chapter PDF, i.e. **24 pages** - at the ceiling
of what I was asked to allow, and above the spec's target of 15-17. I do **not** require cuts:
almost all of it is content the spec demands. Concrete trims are listed under Suggestions.

All required changes below are local (one sentence, one proof paragraph, one symbol, one index
key); none of them touches the structure, the algorithms or the experiments. Hence *Minor
revision* rather than *Accept*: items 1-7 are category A (a number the code does not
reproduce, two over-claims, one false lemma-level justification, one loose proof).

## Required changes

1. **Location:** `\cref{sec:ch13-example}`, paragraph *The program*, line 913-914 ("Each agent
   has changed its velocity by $0.1512$\,m/s").
   **Problem:** Wrong quantity. `0.1512` is the distance from A's *preferred* velocity
   $(1.2,0)$ to the chosen velocity, i.e. the violation of the half-plane by
   $\vel_A^{\mathrm{pref}}$. The change of A's *velocity*, from $\vel_A = (1,0)$ to
   $(1.1809,-0.1500)$, is $0.2350$\,m/s (verified with the code). As written, the sentence also
   contradicts the half-plane statement two paragraphs earlier, which says that A must move its
   velocity by at least $\tfrac12\norm{\vect{u}} = 0.1260$ *in the direction $\vect{n}$*.
   **Fix:** Replace by "Each agent ends up $0.1512$\,m/s away from its preferred velocity (and
   $0.2350$\,m/s away from the velocity it currently flies; the half-plane only required
   $\tfrac12\norm{\vect{u}} = 0.1260$\,m/s along $\vect{n}$)". Add
   `norm(sub(v_a, a.velocity))` to the dictionary printed by `worked_example()` so that this
   number, too, comes from the code.
   **Category:** A.

2. **Location:** `\cref{tab:ch13-example}` line 882 ("$-14.36^\circ = -\theta$"), text line 915,
   text line 924 ("at $-3.93^\circ$"), and `worked_example()` in `code/ch13_orca.py`
   (key `angle_new_rel`).
   **Problem:** Two different angle conventions in three adjacent places, and a sign the code
   does not print. The code computes `ang_new = phi - degrees(atan2(new_rel))` and prints
   `angle_new_rel = 14.3633` (positive); the table and the text print $-14.36^\circ$. Both
   describe the same geometry, but the reader cannot tell which sign convention is meant, and
   the self-test asserts `abs(angle_new_rel - theta) < 1e-6`, i.e. the unsigned version. Two
   lines further, "$(2.1809,-0.1500)$, at $-3.93^\circ$" is a *world-frame* angle
   (`atan2(-0.15, 2.1809) = -3.934 deg`), not an angle measured from $\pos_{\mathrm{rel}}$; the
   corresponding quantity in that convention is $-11.06^\circ$ (as the solution of
   `exr:ch13-shares` correctly says).
   **Fix:** Define the signed angle once in `\cref{sec:ch13-example}`, e.g.
   "$\angle(\vel,\pos_{\mathrm{rel}}) = \operatorname{atan2}(\vel) - \varphi$, positive
   counter-clockwise", use it in the table row and in both sentences, and change
   `worked_example()` to print that signed quantity (`ang_new = degrees(atan2(new_rel[1],
   new_rel[0])) - phi`, with the self-test asserting `abs(ang_new + theta) < 1e-6`). Then write
   "at $-11.06^\circ$ from $\pos_{\mathrm{rel}}$ ($-3.93^\circ$ in the world frame), inside the
   cone of half-angle $14.36^\circ$".
   **Category:** A.

3. **Location:** `\cref{sec:ch13-dense}`, lines 772-776 ("Pushing a half-plane inward by the
   same amount $\delta$ for all agents is equivalent to shrinking the horizon for all of them
   at once, so the velocity found is the one that postpones the first collision as long as
   possible"), and the identical claim in `appendices/glossary/ch13-terms.tex`, entry
   *Dense fallback*, line 10.
   **Problem:** Both halves of the claim are false in general and are not in the source. A
   uniform translation of the half-planes is *not* a change of $\ttc$: in the leg case
   $\vect{u}$ and $\vect{n}$ are completely independent of $\ttc$ (they are the perpendicular to
   a leg, and the legs do not depend on the horizon), so shrinking $\ttc$ does not move the
   half-plane at all until the closest point jumps onto the arc, where the dependence is
   non-linear in $1/\ttc$ and differs from pair to pair. Consequently "the velocity that
   postpones the first collision as long as possible" (a max-min-time-to-collision statement)
   does not follow from minimising the maximum penetration. Van den Berg et al. only claim the
   latter ("the safest possible velocity ... minimises the maximum penetration depth into the
   ORCA half-planes").
   **Fix:** Delete the clause "is equivalent to shrinking the horizon for all of them at once,
   so the velocity found is the one that postpones the first collision as long as possible" and
   replace by: "Relaxing every agent half-plane by the same $\delta$ and taking the smallest
   $\delta$ for which a velocity survives is exactly \cref{eq:ch13-dense}; van den Berg et al.\
   call the result the safest possible velocity, the one that penetrates the half-planes least.
   It is a heuristic: it minimises a penetration, not the time to the first
   collision~\cite{vandenberg2011orca}." Change the glossary entry to "... which penetrates the
   half-planes least" and drop "postpones the first collision as long as possible".
   **Category:** A.

4. **Location:** `\cref{sec:ch13-3d}`, lines 636-642 ("reflecting through that plane leaves the
   body unchanged, and the closest point of a convex body is unique").
   **Problem:** The justification is wrong as stated, and the construction is undefined in one
   case. Uniqueness of the nearest point holds for the projection of a point onto a convex
   *set* when the point is *outside* it; the nearest point of the *boundary* of a convex body
   seen from *inside* need not be unique. The counter-example is exactly the case the reader
   will hit: if $\vel_{\mathrm{rel}}$ lies on the axis inside the truncated cone, an entire
   circle of points of the lateral surface is nearest (this is the three-dimensional version of
   the two-dimensional tie between the two legs, which the chapter breaks by the sign of
   $\pos_{\mathrm{rel}} \times \vect{w}$). In that same case the "plane spanned by
   $\pos_{\mathrm{rel}}$ and $\vel_{\mathrm{rel}}$" does not exist, because the two vectors are
   parallel.
   **Fix:** Replace the parenthesis by: "(the truncated cone is invariant under reflection in
   any plane containing $\pos_{\mathrm{rel}}$, so the set of nearest boundary points is
   invariant too; when $\vel_{\mathrm{rel}}$ is outside, the nearest point of a convex set is
   unique and therefore lies in the plane of $\pos_{\mathrm{rel}}$ and $\vel_{\mathrm{rel}}$,
   and when it is inside, at least one nearest point lies in that plane and the construction
   may take it. If $\vel_{\mathrm{rel}}$ is parallel to $\pos_{\mathrm{rel}}$ every plane
   through the axis gives an equally good $\vect{u}$; `orca_half_space_3d` picks one, exactly
   as the two-dimensional code breaks the leg tie by a sign.)" State in one clause how the code
   makes that choice, so that the reader can match text and implementation.
   **Category:** A.

5. **Location:** `\cref{sec:ch13-orca}`, Step 4 paragraph, lines 545-549 ("in the sense that for
   every radius the permitted fraction of the disc around $\vel_A$ ... is as large as possible;
   van den Berg et al.\ prove this"), and *Further reading*, line 1462 ("\orca, with the
   optimality proof").
   **Problem:** A named optimality property is attributed to the source as a proved theorem,
   but the formalisation given here ("for every radius the permitted fraction of the disc") is
   not the source's, and the source does not prove it. Van den Berg et al.\ define the pair of
   half-planes to be *reciprocally maximal* - among the pairs of half-planes that are
   collision-avoiding and symmetric in the two agents, no other pair contains more velocities
   close to the optimisation velocities - and support it with a short geometric argument, not a
   proof. Either the chapter proves what it states, or it must report the source correctly.
   **Fix:** Replace the clause by: "It is called *optimal* because the pair
   $(\ORCA^{\ttc}_{A|B}, \ORCA^{\ttc}_{B|A})$ is what van den Berg et al.\ call *reciprocally
   maximal*: among all pairs of half-planes that are safe in the sense of
   \cref{thm:ch13-pairwise} and treat the two agents symmetrically, no other pair permits more
   velocities near the optimisation velocities; they argue this geometrically and note that the
   equal split can be replaced by any fixed split that sums to one~\cite{vandenberg2011orca}."
   In *Further reading*, replace "with the optimality proof" by "with the maximality argument".
   **Category:** A.

6. **Location:** proof of `\cref{thm:ch13-incomplete}`, lines 1146-1156, and the parallel
   wording in `\cref{exr:ch13-corridor}`(b), lines 1570-1573.
   **Problem:** Two loose steps in what is presented as a proof. (i) "The wall half-planes
   forbid any lateral velocity ... so the only permitted velocities lie along the corridor" is
   too strong: with the geometry of `\cref{exr:ch13-corridor}` the two wall discs give
   $\abs{v_y} \le 0.75\,v_x$ (I checked: $\pos_{\mathrm{rel}} = (0,\pm1.25)$, $r = 1$,
   $\ttc_{\mathrm{obst}} = 2$, $\vect{d} = (0.8,\pm0.6)$, $\vect{u} = (-0.36,\pm0.48)$,
   $\vect{n} = (0.6,\mp0.8)$), so lateral motion is permitted in proportion to the forward
   speed and only disappears as the agent slows down. (ii) "the programs return velocities of
   decreasing speed and finally $\vect{0}$ for both: ... The state repeats forever" is not
   reached in finite time. In the head-on configuration the arc case gives
   $\vect{u} = ((\norm{\pos_{\mathrm{rel}}}-r)/\ttc)\,\hat{\pos}$ and
   $\vect{n} = -\hat{\pos}$, so each agent may close the gap at
   $(\norm{\pos_{\mathrm{rel}}}-r)/(2\ttc)$ at most; with $d_k = \norm{\pos_{\mathrm{rel}}}-r$
   this gives $d_{k+1} = d_k(1-\dt/\ttc)$, a geometric decay to zero, never an exact fixed
   point.
   **Fix:** Rewrite the last third of the proof as: "The wall half-planes bound the lateral
   velocity by a fixed multiple of the forward velocity, so a lateral escape is available only
   while the agent still moves forward. As the two agents approach, the arc case of
   `\cref{thm:ch13-cases}` gives $\vect{u} = ((\norm{\pos_{\mathrm{rel}}}-r)/\ttc)\hat{\pos}$
   and $\vect{n} = -\hat{\pos}$, so each may close the gap at most at
   $(\norm{\pos_{\mathrm{rel}}}-r)/(2\ttc)$: the gap obeys $d_{k+1} = d_k(1-\dt/\ttc)$ and both
   speeds decay geometrically to zero. Backing into the bay is further from
   $\vel^{\mathrm{pref}}$ than slowing down and no half-plane ever asks for it, so neither
   agent ever reaches its goal, although a collision-free joint plan exists." Change
   `\cref{exr:ch13-corridor}`(b) to ask the student to derive $d_{k+1} = d_k(1-\dt/\ttc)$ and to
   conclude that the configuration converges to a stalled state rather than "is a fixed point".
   **Category:** A.

7. **Location:** `\cref{sec:ch13-dance}`, line 248-250 ("the lateral velocity of agent A under
   the velocity obstacle rule alternates between $0$ and about $-0.2$\,m/s for the whole
   approach").
   **Problem:** The generated data say something slightly different. In
   `figures/data/ch13-dance.dat` the column `vo_vy` alternates between $0$ and $-0.078$ for the
   first four steps, then between about $+0.05$ (52 of the 101 samples) and $-0.09$ or $-0.18$;
   its range is $[-0.182, +0.052]$. The upper level of the oscillation is not $0$.
   **Fix:** "the lateral velocity of agent A under the velocity obstacle rule jumps back and
   forth between about $+0.05$ and $-0.18$\,m/s for the whole approach (range
   $[-0.18, +0.05]$\,m/s)"; keep the "49 reversals in 100 steps", which the code reproduces
   exactly.
   **Category:** A.

8. **Location:** `\cref{sec:ch13-vo}`, `\cref{eq:ch13-relative}`, line 143 ($r = r_A + r_B$) and
   every later use of $r$ for the combined radius.
   **Problem:** Notation clash with the immediately preceding chapter. `ch12-velocity-obstacles`
   defines "The **combined radius** is $R = r_A + r_B$" and uses $R$ throughout (its
   `\cref{eq:ch12-union}` is $\bigcup \disc{\pos_{\mathrm{rel}}/t}{R/t}$, its pseudocode takes
   `combined radius $R$`). Chapter 13 writes the same quantity as $r$ while also using $r_A$ and
   $r_B$, so the two chapters print two different symbols for one concept two pages apart, and
   the reader who compares `\cref{eq:ch13-vo-tau}` with `eq:ch12-union` sees $r/t$ against
   $R/t$.
   **Fix:** Either rename to $R$ throughout the chapter (mechanical: $r \to R$ in
   `\cref{eq:ch13-relative}`, `\cref{def:ch13-vo}`, `\cref{thm:ch13-cases}`, the algorithms,
   the table and the figure captions; the code keyword `r` may stay), or - minimally - add one
   sentence after `\cref{eq:ch13-relative}`: "\Cref{ch:ch12} writes the combined radius $R$;
   this chapter uses $r$, keeping $r_A$ and $r_B$ for the individual radii." The first option is
   preferable.
   **Category:** F.

9. **Location:** line 394, `\index{time horizon $\tau$}`.
   **Problem:** Creates a second, differently spelled index head ("time horizon $\tau$") beside
   the one chapter 12 already uses (`\index{time horizon!velocity obstacle}`), so the two
   chapters' entries do not merge, and a math symbol appears as an index head.
   **Fix:** `\index{time horizon!ORCA}` (and, where it occurs, `\index{time horizon!obstacles}`
   for $\ttc_{\mathrm{obst}}$ in `\cref{sec:ch13-implementation}`).
   **Category:** F.

10. **Location:** objectives box line 19, and the first use in the running text
    (`\cref{sec:ch13-motivation}`, "Velocity obstacles (\cref{ch:ch12}) give such a rule").
    **Problem:** The abbreviation "VO" is used in the objectives, in
    `\cref{fig:ch13-dance}`, `\cref{tab:ch13-circle}`, `\cref{fig:ch13-circle}` and the summary
    without ever being introduced in this chapter; the style guide requires every acronym to be
    defined at first use in every chapter (RVO and \orca are correctly introduced).
    **Fix:** In `\cref{sec:ch13-motivation}` write "Velocity obstacles (VO, \cref{ch:ch12})
    give such a rule"; that one insertion covers all later uses.
    **Category:** F.

## Suggestions

* **Length (G).** 24 pages against a spec target of 15-17. None of it is wrong, but about two
  pages are re-tellings. Concrete candidates: (a) the reciprocal dance is told five times -
  `\cref{sec:ch13-motivation}` paragraph 2, `\cref{sec:ch13-intuition}` paragraph 1,
  `\cref{fig:ch13-idea}` (five rows), `\cref{thm:ch13-dance}` and the paragraph after it; the
  corridor anecdote and the first half of `\cref{sec:ch13-intuition}` can go, since
  `sec:ch12-oscillation` already tells the story and `\cref{fig:ch13-idea}` shows it;
  (b) the first paragraph of `\cref{sec:ch13-limits}` repeats the three pitfall boxes (radius
  margin, $\ttc$ versus $\dt$, tracking delay) - reduce it to a list of the assumptions of
  `\cref{thm:ch13-nbody}` with pointers; (c) `\cref{lst:ch13-cases}` may drop its last twelve
  lines (the overlap branch), which `\cref{thm:ch13-cases}` and
  line~\ref{alg:ch13-halfplane:overlap} of `\cref{alg:ch13-halfplane}` already give.
* Line 199: "enters $\disc{\pos_{\mathrm{rel}}}{r}$ at a time smaller than $\ttc$" should read
  "at a time at most $\ttc$", to agree with $t \in (0,\ttc]$ in `\cref{eq:ch13-vo-tau}`.
* `\cref{sec:ch13-limits}` never says that the overlap branch of `\cref{thm:ch13-cases}` carries
  no $\ttc$-guarantee: `\cref{thm:ch13-pairwise}` assumes $\norm{\pos_{\mathrm{rel}}} > r$, and
  once the discs overlap the construction only promises separation after one $\dt$. One
  sentence would close the gap between the lemma and the theorem.
* `\cref{eq:ch13-dense}` is called "a linear program in three variables $(v_x,v_y,\delta)$";
  strictly it is an LP in those three variables *plus* the speed disc, i.e. the same
  half-plane-and-disc structure as `\cref{alg:ch13-lp}`. Say so, since
  `\cref{alg:ch13-dense}` in fact calls the two-dimensional machinery with the disc.
* `\cref{fig:ch13-circle}`: the caption describes three trace panels but the lower panel plots
  four curves; add "the lower panel also shows sampled RVO" so that the reader looking for RVO
  in the traces knows it is deliberately omitted there.
* `appendices/solutions/ch13-solutions.tex` covers four of the ten exercises. The two that a
  lone reader is most likely to get stuck on are `exr:ch13-lp-by-hand` (the order-dependence of
  the incremental LP) and `exr:ch13-infeasible` (the bisector half-planes); a short hint for
  each would pay for itself.
* `frontmatter/notation.tex` is still a placeholder. When it is filled, this chapter's symbols
  ($\pos_{\mathrm{rel}}$, $\vel_{\mathrm{rel}}$, $\ttc$, $\vect{u}$, $\vect{n}$,
  $\vel^{\mathrm{pref}}$, $v_{\max}$, $\VO$, $\RVO$, $\ORCA$, the share $\alpha$) should go in;
  they are the ones a reader most often looks up. (Front-matter task, not the chapter author's.)
* The spec asks for "the reciprocal dance among three" agents; the chapter argues the
  three-agent failure of RVO in prose and demonstrates the side-switching numerically with a
  two-agent instance. A third trace in `\cref{fig:ch13-dance}` (three RVO agents, one of them
  taking none of the responsibility for the pair) would make the argument visible at no cost in
  new code - `simulate` already supports it.

## What must be kept

The mathematical core of this chapter is in excellent shape and should not be touched. The
four-step derivation with one panel of `\cref{fig:ch13-orca-construction}` per step is the
clearest presentation of ORCA I have read outside the original paper, and the decision to work
in the relative frame and only translate into A's velocity space at Step 4 is exactly right.
`\cref{thm:ch13-cases}` and `\cref{alg:ch13-halfplane}` are faithful to RVO2 down to the
sign conventions, including the two subtleties that implementations get wrong (the arc test
written without trigonometry, and the outward normal being $+90^\circ$ on the left leg and
$-90^\circ$ on the right), and the pitfall box about the normal orientation is worth its space.
The proof of `\cref{thm:ch13-convex}` via $1/t = \lambda/t_1 + (1-\lambda)/t_2$ is elegant and
correct, and it is what makes the two-line proof of `\cref{thm:ch13-pairwise}` honest rather
than hand-waved. Treating the responsibility as one parameter $\alpha$, with the guarantee
holding exactly when $\alpha_A + \alpha_B = 1$, unifies the reciprocal, the non-cooperative and
the priority cases, is carried consistently through the algorithm, the worked example, the
pitfall box, the drone box and `\cref{exr:ch13-shares}`, and is precisely what
`\cref{ch:ch24}` will need. `\cref{sec:ch13-limits}` is the kind of honest section textbooks
usually omit. Finally, the code and the generated data are a model of what the style guide
asks for: `worked_example()` prints every number of `\cref{tab:ch13-example}`,
`gen_ch13_circle.py` prints every number of `\cref{tab:ch13-circle}` and of the dance figure,
the self-test checks all four geometric cases, the optimality of the LP solution against a
brute-force grid, the minimax property of the dense fallback, the doubling of the shift in the
non-reciprocal branch and the rotation covariance of the 3D half-space - and it all runs in
2.1 s.

## Response to review (round 1)

All ten required changes are applied. Build: `./build.sh ch13-rvo-orca` ends with no
`!` error, no overfull box above 15 pt, no undefined label or citation belonging to this
chapter, and no multiply-defined label; the exit status is 12 for exactly the reason the
review names, the 40 cross-chapter `??` of a single-chapter build (`ch:ch24`, `ch:ch12`,
`ch:appA`, ...). The body is still 24 pages (pp. 58-81 of the current single-chapter PDF).
`python3 code/ch13_orca.py` passes its self-test in 2.2 s and
`python3 code/figures/gen_ch13_circle.py` rewrites `figures/data/ch13-dance.dat` and
`ch13-circle-*.dat` byte-identically, so every generated number is unchanged.

1. **Worked example, "the program" paragraph (0.1512 named the wrong quantity).** Rewritten
   as required: "Each agent ends up $0.1512$ m/s away from its preferred velocity (and
   $0.2350$ m/s away from the velocity it currently flies; the half-plane only required
   $\tfrac12\norm{\vect{u}} = 0.1260$ m/s along $\vect{n}$)". `worked_example()` now prints
   `change_a = norm(sub(v_a, a.velocity)) = 0.2350`, the self-test asserts it (and the
   $0.1512$ violation), and `tab:ch13-example` gained a row
   $\norm{\vel_A^{\mathrm{new}} - \vel_A} = 0.2350$ so the number in the text is in the table
   and in the code output.

2. **Three angle statements in two conventions.** The signed angle is now defined once, in
   `sec:ch13-example` Step 1: $\angle(\vel,\pos_{\mathrm{rel}}) = \mathrm{atan2}(v_y,v_x) -
   \varphi$, positive counter-clockwise, legs at $\pm\theta$. The table row is now
   "$\angle(\vel_{\mathrm{rel}}^{\mathrm{new}}, \pos_{\mathrm{rel}})$, $-14.36^\circ =
   -\theta$", the first sentence uses the same symbol, and the second reads "at
   $-11.06^\circ$ from $\pos_{\mathrm{rel}}$ ($-3.93^\circ$ in the world frame), inside the
   cone of half-angle $14.36^\circ$". `worked_example()` now computes
   `ang_new = degrees(atan2(new_rel[1], new_rel[0])) - phi` (and the same for
   `angle_full_rel`), printing $-14.3633$; the self-test asserts
   `abs(ang_new + theta) < 1e-6`. The solution of `exr:ch13-shares` was aligned with the same
   notation.

3. **Dense fallback: the "shrinking the horizon"/"postpones the first collision" claim.**
   Deleted and replaced by the wording asked for: relaxing every agent half-plane by the same
   $\delta$ and taking the smallest feasible $\delta$ is exactly `eq:ch13-dense`; van den Berg
   et al. call the result the *safest possible velocity*, the one that penetrates the
   half-planes least [vandenberg2011orca]; "It is a heuristic: it minimises a penetration, not
   the time to the first collision." The glossary entry *Dense fallback* now says "which
   penetrates the half-planes least" and carries the same caveat. The same over-claim in
   `sec:ch13-limits` ("postpones the first collision without excluding it") became "returns
   the least-penetrating velocity, which does not exclude a collision".

4. **3D justification.** The parenthesis is replaced by the argument supplied: invariance of
   the truncated cone under reflection in any plane containing $\pos_{\mathrm{rel}}$,
   uniqueness only for $\vel_{\mathrm{rel}}$ *outside* the convex body, "at least one nearest
   point lies in that plane" when it is inside, and the parallel case in which every plane
   through the axis gives an equally good $\vect{u}$, the code picking one as the 2D code
   breaks the leg tie by a sign. The following sentence states how the code chooses: it spans
   the plane by the unit vector along $\pos_{\mathrm{rel}}$ and the unit vector along the
   component of $\vel_{\mathrm{rel}}$ perpendicular to it, "or, when that component vanishes,
   along a fixed helper axis" (`orca_half_space_3d`, lines 281-290).

5. **Optimality over-claim (Step 4) and Further reading.** The clause is replaced by the
   reciprocal-maximality formulation given in the review, with a forward `\cref` to
   `thm:ch13-pairwise` ("safe in the sense of Theorem 13.10"), "they argue this geometrically",
   the fixed-split remark, and a new index entry `ORCA!reciprocal maximality`. Further reading
   now reads "with the maximality argument".

6. **Proof of `thm:ch13-incomplete` and `exr:ch13-corridor`(b).** The last third of the proof
   is rewritten: the wall half-planes bound the lateral velocity by a fixed multiple of the
   forward velocity (the exercise computes $0.75$), the head-on arc case gives
   $\vect{u} = (d/\ttc)\hat{\pos} - \vel_{\mathrm{rel}}$ and $\vect{n} = -\hat{\pos}$ with
   $d = \norm{\pos_{\mathrm{rel}}} - R$, so each agent may approach at no more than
   $d/(2\ttc)$ whatever its current speed, the gap obeys $d_{k+1} = d_k(1 - \dt/\ttc)$ and both
   speeds decay geometrically to zero; backing into the bay is never asked for, so no agent
   reaches its goal although a collision-free joint plan exists. (The general $\vect{u}$ is
   written with the $-\vel_{\mathrm{rel}}$ term; at a hover it is the review's
   $((\norm{\pos_{\mathrm{rel}}}-R)/\ttc)\hat{\pos}$, and the bound $d/(2\ttc)$ is the same.)
   Exercise (b) now asks for that bound, the derivation of $d_{k+1} = d_k(1-\dt/\ttc)$ and the
   conclusion that the configuration *converges to* a stalled state; (a) asks for the bound of
   $\abs{v_y}$ by a fixed multiple of $v_x$ instead of a bare threshold.

7. **`sec:ch13-dance` lateral-velocity range.** Now "jumps back and forth between about
   $+0.05$ and $-0.18$ m/s for the whole approach (range $[-0.18, +0.05]$ m/s)", with the
   49 reversals in 100 steps kept; both match `figures/data/ch13-dance.dat` (min $-0.1823$,
   max $+0.0518$) as regenerated.

8. **Combined radius $r$ -> $R$.** Done throughout the chapter (44 occurrences: the display
   `eq:ch13-relative`, `def:ch13-vo`, `thm:ch13-cases` and its proof, `alg:ch13-halfplane`,
   the 3D section, `tab:ch13-example`, the theorem statements, the exercises), plus the
   glossary entry, the solution of `exr:ch13-arc-case` and the label $R/\ttc$ in
   `figures/ch13/orca-construction.tex`. `r_A`, `r_B` and the code keyword `r` in the two
   listings are untouched, as the review allows. The sentence after `eq:ch13-relative` now
   bolds **combined radius**, adds `\index{combined radius}` (the same index head as
   `ch:ch12`) and says it is the symbol `ch:ch12` uses.

9. **Index heads.** `\index{time horizon $\tau$}` is now `\index{time horizon!ORCA}`, and
   `\index{time horizon!obstacles}` was added where $\ttc_{\mathrm{obst}}$ is introduced in
   `sec:ch13-implementation`.

10. **The acronym VO.** `sec:ch13-motivation` now reads "Velocity obstacles (VO,
    \cref{ch:ch12}) give such a rule"; since the objectives box precedes it, that item was
    also changed to "the velocity obstacle (VO) rule", so the acronym is defined at its true
    first use.

**Suggestions.** Applied: "at a time at most $\ttc$" in `sec:ch13-vo`; a sentence in
`sec:ch13-limits` saying that `thm:ch13-pairwise` assumes $\norm{\pos_{\mathrm{rel}}} > R$ and
that the overlap branch carries no $\ttc$-guarantee, only separation after one $\dt$;
`eq:ch13-dense` is now called "a linear program in the three variables $(v_x,v_y,\delta)$
together with the speed disc, the same half-plane-and-disc structure as `alg:ch13-lp`"; the
`fig:ch13-circle` caption now says the lower panel shows all four methods, RVO included;
solutions were added for `exr:ch13-lp-by-hand` (order-dependence, the boundary-line argument,
the disc clamp) and `exr:ch13-infeasible` (equalised violations, the bisector half-planes, the
independence of $\vel^{\mathrm{pref}}$), so six of ten exercises now have solutions.
Not applied: the length trims (the review requires no cuts and the material is spec content;
the chapter stays at 24 pages), the third RVO trace in `fig:ch13-dance` (it needs a new
three-agent run in `gen_ch13_circle.py` and a fourth curve in a figure the review asks to
keep; the panel already carries a fourth curve, the unequal-share RVO run), and the
front-matter notation table, which is not this chapter's file.
