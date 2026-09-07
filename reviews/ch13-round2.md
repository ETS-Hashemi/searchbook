# Review of Chapter 13 (Reciprocal Avoidance: RVO and ORCA) - round 2

## Verdict

**Minor revision.**

Round 1 left ten required changes. I checked each one against the current source, the current
code output and the current PDF:

| # (round 1) | Topic | Status |
|---|---|---|
| 1 | `0.1512` named the wrong quantity | **resolved** - text now reads "$0.1512$ away from its preferred velocity (and $0.2350$ from the velocity it currently flies; the half-plane only required $\tfrac12\norm{\vect{u}} = 0.1260$ along $\vect{n}$)"; `worked_example()` prints `change_a = 0.2350`; `tab:ch13-example` has the new row |
| 2 | three angle statements in two conventions | **resolved in the three places named** (table row $-14.36^\circ = -\theta$, code prints `angle_new_rel = -14.3633`, text "at $-11.06^\circ$ from $\pos_{\mathrm{rel}}$ ($-3.93^\circ$ in the world frame)"); a fourth place in the same paragraph still mixes frames - see required change 3 |
| 3 | dense fallback "postpones the first collision" | **resolved** in `sec:ch13-dense`, in `sec:ch13-limits` ("returns the least-penetrating velocity, which does not exclude a collision") and in the glossary entry *Dense fallback* |
| 4 | 3D uniqueness justification | **resolved**; the reflection argument, the outside/inside distinction and the parallel case are all stated, and the sentence naming how `orca_half_space_3d` breaks the tie is there |
| 5 | ORCA "optimality proof" over-claim | **resolved**; *reciprocally maximal*, "they argue this geometrically", the fixed-split remark, and "with the maximality argument" in *Further reading* |
| 6 | proof of `thm:ch13-incomplete` and `exr:ch13-corridor`(b) | **resolved and correct.** I re-derived the geometry: for the wall discs ($\pos_{\mathrm{rel}} = (0,\pm1.25)$, $R = 1$, $\ttc_{\mathrm{obst}} = 2$) one gets $\ell = 0.75$, $\vect{d} = (0.8,\pm0.6)$, $\vect{u} = (-0.36,\pm0.48)$, $\vect{n} = (0.6,\mp0.8)$ and, with $\alpha = 1$, exactly $\abs{v_y} \le 0.75\,v_x$; in the head-on arc case $\vect{u} = (d/\ttc)\hat{\pos} - \vel_{\mathrm{rel}}$, $\vect{n} = -\hat{\pos}$ and the half-plane bounds the approach speed by $d/(2\ttc)$, giving $d_{k+1} = d_k(1-\dt/\ttc)$ |
| 7 | lateral-velocity range of the dance | **resolved**; `ch13-dance.dat` has $\min = -0.1823$, $\max = +0.0518$, the text says $[-0.18, +0.05]$ and keeps the 49 reversals |
| 8 | combined radius $r \to R$ | **NOT resolved.** The response claims "44 occurrences ... done throughout the chapter", but 14 occurrences of lower-case $r$ for the combined radius survive, including `eq:ch13-vo`, `eq:ch13-vo-tau`, `eq:ch13-halfangle`, `thm:ch13-cases` and the proof of `thm:ch13-convex`. See required change 1 |
| 9 | index heads | **resolved**; `time horizon!ORCA` and `time horizon!obstacles` |
| 10 | acronym VO | **resolved** in the objectives and in `sec:ch13-motivation` |

Build: `./build.sh ch13-rvo-orca` exits 0, no `!` error, no overfull box at all, no
multiply-defined label, no undefined citation, and no undefined label belonging to this
chapter (the 33 `??` are the expected cross-chapter ones: `ch:ch12`, `ch:ch15`, `ch:ch16`,
`ch:ch18`, `ch:ch20`, `ch:ch23`, `ch:ch24`, `ch:appA`). `python3 code/ch13_orca.py` passes
its self-test in 2.1 s; `python3 code/figures/gen_ch13_circle.py` rewrites every
`figures/data/ch13-*.dat` byte-identically (`git status` shows no change), so every generated
number in `tab:ch13-circle`, `fig:ch13-dance` and `fig:ch13-circle` is reproduced. Both
listings are verbatim excerpts of `code/ch13_orca.py` (39 and 23 lines, both under the 45-line
cap). I re-derived the whole worked example independently ($\norm{\pos_{\mathrm{rel}}} =
4.0311$, $\theta = 14.3633^\circ$, $\vect{w} = (1,-0.125)$, $\vect{w}\cdot\pos_{\mathrm{rel}} =
3.9375$, $\pos_{\mathrm{rel}}\times\vect{w} = -1$, $\ell = 3.9051$, $\vect{d}_{\mathrm{R}} =
(0.99203,-0.12600)$, $\vect{q} = (1.96825,-0.24996)$, $\vect{u} = (-0.03175,-0.25)$,
$\norm{\vect{u}} = 0.25201$, $\vect{n} = (-0.12600,-0.99203)$, violation $0.15120$,
$\vel_A^{\mathrm{new}} = (1.18095,-0.15)$, change $0.23504$, full-responsibility point
$(0.96825,-0.25)$, violation $0.27720$, $\vel_A^{\mathrm{new}} = (1.16507,-0.275)$, collision
at $t = 1.567$ s) and every entry of `tab:ch13-example` is right. I also re-derived
`fig:ch13-rvo` ($\vel' = (0.7661,0.6428)$, $\vel_A^{\mathrm{new}} = (0.8830,0.3214)$, exactly
on the RVO leg) and `fig:ch13-lp` (the three lines carry the normals and points quoted in
`exr:ch13-lp-by-hand`, and the projection of $(1.2,0.3)$ onto $H_1$ is $(1.1096,-0.1427)$,
which satisfies $H_2$, $H_3$ and the disc, as the caption says). The case analysis, the two
algorithms and the dense fallback still agree with RVO2 (`computeNewVelocity`,
`linearProgram1/2/3`) line for line, including the arc test, the leg formulas, the normal
orientations, the chord discriminant, the `den`/`num` clipping rule and the bisector
construction.

Length: the chapter body is pages 17-40 of the 48-page single-chapter PDF, i.e. **24 pages**,
unchanged and at the ceiling I was given. As in round 1 I require **no cuts**: the material is
what the spec demands.

The four required changes below are all local (a mechanical symbol substitution, six lines of
`print` keys, two sentences, three acronyms). Nothing in the structure, the mathematics, the
algorithms or the experiments needs to move. Because one of them is in category C (a symbol
that the chapter never defines appears in its central definition) and one in category A (the
chapter claims a provenance for seven numbers that the code does not in fact provide), the
verdict is *Minor revision* rather than *Accept*.

## Required changes

1. **Location:** `\cref{sec:ch13-vo}` and later - `chapters/ch13-rvo-orca.tex` lines 153, 168
   (`eq:ch13-vo`), 175 and 176 (`eq:ch13-vo-tau`), 185, 189 (`eq:ch13-halfangle`), 193, 195,
   201, 308, 461 and 484 (`\cref{thm:ch13-cases}`), 502 (its proof sketch), 1044 (proof of
   `\cref{thm:ch13-convex}`); also `appendices/solutions/ch13-solutions.tex` lines 4 and 16.
   **Problem:** Round-1 item 8 is not finished. `\cref{eq:ch13-relative}` now defines the
   **combined radius** $R = r_A + r_B$ and states that $R$ "is the same symbol that
   \cref{ch:ch12} uses", but fourteen occurrences still print lower-case $r$ for that same
   quantity, and the chapter never defines a bare $r$ (only $r_A$, $r_B$ and $R$). The PDF
   therefore shows, four lines apart, "$\norm{\pos_{\mathrm{rel}} - t\vel_{\mathrm{rel}}} < R$"
   and "$\VO_{A|B} = \set{\vel : \exists t > 0,\ t\vel \in D(\pos_{\mathrm{rel}}, r)}$", and
   the half-angle as $\theta = \arcsin(r/\norm{\pos_{\mathrm{rel}}})$ while
   `tab:ch13-example`, `\cref{alg:ch13-halfplane}` and
   `\cref{fig:ch13-orca-construction}` all use $R$. The three central set definitions of the
   chapter are thus written with an undefined symbol, and `eq:ch13-vo-tau` again fails to line
   up with `eq:ch12-union` of the preceding chapter, which is what the round-1 item was about.
   **Fix:** Complete the substitution: `{r}` $\to$ `{R}` in the seven `\disc{\pos_{\mathrm{rel}}}{r}`,
   `{r/t}` $\to$ `{R/t}`, `{r/2t}` $\to$ `{R/2t}`, `{r/\ttc}` $\to$ `{R/\ttc}`,
   `{r/\dt}` $\to$ `{R/\dt}` (two places), and
   `\arcsin\frac{r}{\norm{\pos_{\mathrm{rel}}}}` $\to$ `\arcsin\frac{R}{\norm{\pos_{\mathrm{rel}}}}`
   in `eq:ch13-halfangle`, plus the same two substitutions in the solutions file. Leave the
   code keyword `r` in `\cref{lst:ch13-cases,lst:ch13-lp}` as it is, but add half a sentence
   to the paragraph that introduces the listings: "the code writes the combined radius `r`
   where the text writes $R$". Verify with
   `grep -n '}{r}\|{r/\|frac{r}' chapters/ch13-rvo-orca.tex appendices/solutions/ch13-solutions.tex`,
   which must return nothing.
   **Category:** C (and F).

2. **Location:** `\cref{ex:ch13-two-agents}`, line 868 ("Every number below is printed by
   \code{worked\_example()} in \code{ch13\_orca.py}"), and `worked_example()` in
   `code/ch13_orca.py` (lines 617-664).
   **Problem:** Seven of the quantities in `\cref{tab:ch13-example}` are *not* printed by the
   function: $\norm{\pos_{\mathrm{rel}}} = 4.0311$, $\vect{w} = (1,-0.125)$,
   $\vect{w}\cdot\pos_{\mathrm{rel}} = 3.9375$, $\pos_{\mathrm{rel}}\times\vect{w} = -1$,
   $\ell = 3.9051$, $\vect{d}_{\mathrm{R}} = (0.9920,-0.1260)$ and $\norm{\vect{u}} = 0.2520$.
   Running the file prints only `tau, p, r, phi, theta, centre, rho, v_rel, case, q, u, n,
   point_a, point_b, n_b, v_new_a, v_new_b, feasible, change_a, angle_new_rel, point_full,
   v_new_full, angle_full_rel, violation_pref, violation_pref_full`. The seven values are all
   correct - I re-derived each of them by hand - but the sentence asserts a provenance the
   code does not deliver, and the style guide (Sections 3 and 6) asks the numbers of a worked
   example to come from running the code. This is the same defect that was fixed for
   `change_a` in round 1, left in the six neighbouring rows.
   **Fix:** In `worked_example()`, add the seven keys to the dictionary it builds and prints,
   next to the existing ones - `norm_p = norm(p)`, `w = sub(v_rel, centre)`,
   `w_dot_p = dot(w, p)`, `cross_p_w = cross(p, w)`, `ell = math.sqrt(dot(p, p) - r * r)`,
   `d_leg` (the leg direction, available from `vo_closest_boundary_point`, or recomputed with
   the same formula) and `u_norm = norm(u)` - and assert two of them in `_self_test()` in the
   style of the existing checks (`abs(res["u_norm"] - 0.2520) < 1e-4`,
   `abs(res["ell"] - 3.9051) < 1e-4`). Then the sentence at line 868 becomes true as written.
   **Category:** A.

3. **Location:** `\cref{sec:ch13-example}`, the *Step 1* / *Step 2* paragraph, lines 909-918.
   **Problem:** Three consecutive sentences use two angle frames without saying which is
   which. "the legs point at $21.49^\circ$ (left) and $-7.24^\circ$ (right)" is the world
   frame; the next sentence says "Directions in this example are measured from the axis of the
   cone" and concludes "so that the legs are at $\pm\theta$", i.e. $\pm 14.36^\circ$; the next
   sentence says "$\vel_{\mathrm{rel}} = (2,0)$ points at $0^\circ$, between the legs", which
   is the world frame again ($\angle(\vel_{\mathrm{rel}},\pos_{\mathrm{rel}}) = -7.13^\circ$
   in the frame just defined). A reader who takes the declared convention at face value reads
   that the legs are simultaneously at $21.49^\circ/-7.24^\circ$ and at $\pm14.36^\circ$. This
   is the fourth instance of the problem round-1 item 2 identified; the three instances the
   review named were fixed, this one was not.
   **Fix:** Label the frame in each sentence. For example: "... the cone half-angle is
   $\theta = \arcsin(1/4.0311) = 14.36^\circ$, so in the world frame the legs point at
   $21.49^\circ$ (left) and $-7.24^\circ$ (right). From here on, directions are measured from
   the axis of the cone: for $\vel \ne \vect{0}$ write
   $\angle(\vel,\pos_{\mathrm{rel}}) = \mathrm{atan2}(v_y,v_x) - \varphi$ ... so that the legs
   are at $\pm\theta$ ... \emph{Step 2.} $\vel_{\mathrm{rel}} = (2,0)$ points along the
   $x$-axis, that is $\angle(\vel_{\mathrm{rel}},\pos_{\mathrm{rel}}) = -7.13^\circ$, between
   the legs, and ...".
   **Category:** C.

4. **Location:** `\cref{sec:ch13-motivation}` line 27 (`\cbs`), the `dronebox` lines 1429
   (`\cbs or \ecbs`) and 1446 (`\dstarlite or \astar`).
   **Problem:** Style guide Section 3 requires every acronym to be defined at first use *in
   every chapter*, and names CBS explicitly. This chapter introduces VO, RVO and ORCA
   correctly but uses CBS and ECBS unexpanded, in the very first paragraph and in the drone
   box. `ch12-velocity-obstacles` does not mention CBS, so a reader arriving here from
   Part IV has not met the expansion recently.
   **Fix:** Line 27: "nominal paths planned by conflict-based search (\cbs, \cref{ch:ch09})".
   Line 1429: "from the global planner (conflict-based search \cbs, or its bounded-suboptimal
   variant \ecbs, \cref{ch:ch09,ch:ch10})". Line 1446 needs no change (\dstarlite and \astar
   are typeset names, not acronyms).
   **Category:** F.

## Suggestions

* **Length (G).** Still 24 pages against a spec target of 15-17. I require no cuts, and I
  repeat only the cheapest of last round's candidates, in case the book-level page budget
  bites later: the first half of `\cref{sec:ch13-intuition}` (the corridor anecdote) duplicates
  `sec:ch12-oscillation` and `\cref{fig:ch13-idea}`, and the first paragraph of
  `\cref{sec:ch13-limits}` restates the three pitfall boxes. Together they are about
  three quarters of a page.
* `\eps` carries three different meanings in the chapter and is defined nowhere: the numerical
  tolerance in `\cref{alg:ch13-lp}` (`$\abs{\mathit{den}} \le \eps$`), the perturbation in the
  second pitfall box (`$\vel_{\mathrm{rel}} + \vect{u} \pm \eps\vect{n}$`) and the tracking-error
  bound of Alonso-Mora et al. in `\cref{sec:ch13-variants}`. One parenthesis ("$\eps$ is a small
  numerical tolerance") at the first use, and a different letter for the tracking bound, would
  remove the collision.
* `ch12-velocity-obstacles` marks the defining occurrence of each of its index heads with
  `|textbf` (`\index{velocity obstacle|textbf}`, `\index{collision cone|textbf}`). Chapter 13
  uses none, so in the merged index the ORCA entries have no bold page number. Adding it to the
  four defining occurrences (`reciprocal velocity obstacle`, `ORCA!half-plane`,
  `ORCA!full responsibility`, `linear program!incremental`) would match.
* `figures/ch13/orca-construction.tex`, header comment line 2, still says "`r = 1`"; the drawn
  label is already `$R/\ttc$`. Cosmetic, but it is the one place a future editor would look.
* `appendices/solutions/ch13-solutions.tex` now covers six of ten exercises. The two remaining
  gaps that a lone reader is most likely to hit are `exr:ch13-by-hand` (the mirrored worked
  example - three lines would do, since the answer is the sign flip of `tab:ch13-example`) and
  `exr:ch13-corridor`(a), whose $0.75$ the chapter's own proof now cites.
* The spec asks for "the reciprocal dance among three" agents. The chapter argues the
  three-agent failure of RVO in prose (agent $C$ absorbing $B$'s whole reaction) and shows the
  side-switching numerically for two near-symmetric agents. I accept this as covered, as round 1
  did; a third trace in `\cref{fig:ch13-dance}` would still be the single best half-page
  addition if the page budget ever allows.
* `frontmatter/notation.tex` is still the two-row placeholder. When it is filled, this chapter's
  symbols ($\pos_{\mathrm{rel}}$, $\vel_{\mathrm{rel}}$, $R$, $\ttc$, $\vect{u}$, $\vect{n}$,
  $\vel^{\mathrm{pref}}$, $v_{\max}$, $\VO$, $\RVO$, $\ORCA$, $\alpha$) belong in it. Front-matter
  task, not this chapter's.

## What must be kept

Everything the round-1 review praised survived the revision intact, and the revision itself
improved the two places where the chapter had been weakest. The four-step derivation with one
panel of `\cref{fig:ch13-orca-construction}` per step, worked entirely in the relative frame
and translated into $A$'s velocity space only at Step 4, remains the clearest exposition of
ORCA I know outside the original paper. `\cref{thm:ch13-cases}` and
`\cref{alg:ch13-halfplane}` are faithful to RVO2 down to the sign conventions - the
trigonometry-free arc test, the leg formulas as rotations by $\pm\theta$, and the outward
normal being $+90^\circ$ on the left leg and $-90^\circ$ on the right - and the pitfall box
about the normal orientation earns its space. The proof of `\cref{thm:ch13-convex}` via
$1/t = \lambda/t_1 + (1-\lambda)/t_2$ is elegant and correct, and it is what makes the two-line
proof of `\cref{thm:ch13-pairwise}` honest. Carrying the responsibility as one parameter
$\alpha$ with the guarantee holding exactly when $\alpha_A + \alpha_B = 1$ unifies the
reciprocal, non-cooperative and priority cases through the algorithm, the worked example, the
pitfall box, the drone box and `\cref{exr:ch13-shares}`, and is exactly what `\cref{ch:ch24}`
needs. The rewritten proof of `\cref{thm:ch13-incomplete}` is now genuinely a proof: the
$\abs{v_y} \le 0.75\,v_x$ wall bound and the geometric decay $d_{k+1} = d_k(1-\dt/\ttc)$ both
check out exactly, and the matching `\cref{exr:ch13-corridor}` is one of the best exercises in
the book so far. `\cref{sec:ch13-limits}` is the honest section most textbooks omit. Finally,
the code and the generated data remain a model of what the style guide asks for: the self-test
covers all four geometric cases, the optimality of the LP solution against a brute-force grid,
the minimax property of the dense fallback, the doubling of the shift in the non-reciprocal
branch and the rotation covariance of the 3D half-space, `gen_ch13_circle.py` reproduces every
number of `\cref{tab:ch13-circle}` and of `\cref{fig:ch13-dance}` byte-identically, and both
scripts together run in under four seconds.
