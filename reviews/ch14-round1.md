# Review of Chapter 14 (The Dynamic Window Approach) - round 1

## Verdict

**Minor revision.**

This is a strong, technically careful chapter. The build is clean (`./build.sh ch14-dwa`,
exit 0, no `!` errors, no overfull boxes above 15 pt, no undefined labels or citations
belonging to this chapter; the `??` in the PDF are all in the shared front matter).
`python3 code/ch14_dwa.py` and `python3 code/figures/gen_ch14_traj.py` both run in about
1.3 s, and I checked every quoted number against their output: all 13 rows of
`tab:ch14-candidates`, all 13 rows of `tab:ch14-trace`, all 9 rows of `tab:ch14-weights`,
the final position `(4.82, 0.03)`, path length `4.98` m, minimum clearance `1.6` cm, the
free distance `0.608` m, the admissible speeds `1.56`/`1.14` m/s, the braking sequence
`0.5+0.375+0.25+0.125 = 1.25` m, the collision "in step 7" of the moving-obstacle test,
the `17`/`16` steps in 2D/3D, and the `35.9` m of the hysteresis run quoted in the
solutions file - all reproduce exactly. Theorem 14.1 and its lemma are correct as proved
(I recomputed the algebra), Proposition 14.2's pocket radius of 1.65 m is right, the
complexity counts (25/125/121/1331) are right, and the arc equations match Fox, Burgard
and Thrun (1997). Every "must cover" item of `docs/specs/ch14.md` and every Week-7 item of
the training plan is present. Length is 20 PDF pages (pp. 15-34 of the single-chapter
build) - at the ceiling, above the spec's 12-14 target, but the material is required
content rather than padding, so I ask for trims only as suggestions.

Eight required changes remain, all local: three claims the code does not support, one gap
between the pseudocode and the code that produced the trace table, one definition that is
false as printed, one loose clause in an otherwise correct proof, one self-contradicting
caption, plus acronyms and one banned word. None of them requires restructuring.

## Required changes

1. **Location:** `sec:ch14-tuning`, paragraph "Clearance dominates", line 902
   ("Every candidate that enters the $2$~m wide corridor has a clearance of at most $0.33$
   against $1$ in the open").
   **Problem:** the code does not produce this number, and the mechanism described is not
   the one that operates. At the start of the corridor run (`corridor_scene()`,
   $\pos=(0,0)$, $\vel_a=\vect{0}$, weights $(0.2,0.6,0.2)$) the straight candidate
   $(0.5,0)$ has $\dist = 2.65$ m, i.e. clearance $0.885$, not $\le 0.33$; the deepest
   forward candidate reaches $0.317$ only three steps later, once the drone has already
   turned away. The real reason for the detour is a 0.003 margin, not a 3:1 gap.
   **Fix:** replace the sentence with the numbers `evaluate()` prints for step 1, e.g.:
   "From the start the straight command $(0.5,0)$ sees the wall and the pillar ahead
   ($\dist = 2.65$ m, clearance $0.885$) and scores $0.2 + 0.531 + 0.05 = 0.781$, while
   $(0.25,\pm 0.5)$, which turn out of the corridor mouth into the open, see nothing within
   $d_{\max}$ (clearance $1$) and score $0.784$ despite a heading of only $0.641$: $\beta$
   gains $0.6\cdot 0.115 = 0.069$ and $\gamma$ another $0.006$ against the
   $0.2\cdot 0.359 = 0.072$ that $\alpha$ loses. The margin is three thousandths, and it is
   enough to turn the drone away." Keep the rest of the paragraph (it is correct: 21 steps,
   8.7 m, 47 % longer, goal reached from below).
   **Category:** A.

2. **Location:** `sec:ch14-properties`, subsection "DWA is a local method", lines 799-801
   ("it covers $80$~m without leaving the U, passing within $4$~cm of the arms").
   **Problem:** the 4 cm is the minimum clearance against the *back wall*, not the arms. In
   the 300-step default run the trajectory spans $x \in [0, 4.76]$ and
   $y \in [-1.31, 1.26]$; with the wall face at $x = 5.0$ and the drone radius $0.2$ the
   gap to the back wall is $5.0 - 4.76 - 0.2 = 0.04$ m, while the closest approach to the
   arms (faces at $y = \pm 1.6$) is $1.6 - 1.31 - 0.2 = 0.09$ m.
   **Fix:** "...it covers $80$~m without leaving the U, braking to within $4$~cm of the
   back wall and turning $9$~cm short of the arms."
   **Category:** A.

3. **Location:** `def:ch14-admissible` / `eq:ch14-Va`, line 261
   ($\omega \le \sqrt{2\,\dist(v,\omega)\,\dot\omega_b}$).
   **Problem:** as printed the rotational condition is vacuous for left turns: every
   $\omega < 0$ satisfies it whatever the free distance, so $V_a$ as defined contains
   arbitrarily fast negative rotations next to an obstacle. (The original paper writes it
   the same way; a textbook that promises exact definitions should not inherit the slip.)
   **Fix:** write $\abs{\omega} \le \sqrt{2\,\dist(v,\omega)\,\dot\omega_b}$ in
   `eq:ch14-Va` and add half a sentence to the "Where the square root comes from"
   paragraph: "the sign of $\omega$ does not matter, which is why the bars are needed;
   Fox et al.\ omit them." Nothing else in the chapter changes ($v \ge 0$ for the
   differential drive, and the drone form already uses $\norm{\vel}$).
   **Category:** A.

4. **Location:** `alg:ch14-command` line~\ref{alg:ch14-command:admissible} (file line 470),
   its walkthrough (lines 509-512) and `tab:ch14-trace`.
   **Problem:** the pseudocode brakes only for obstacles, but steps 11-13 of the trace
   table are produced by the code's goal braking (`brake_for_goal=True`, `evaluate()`:
   `limit = min(limit, admissible_speed(d_goal, a_b, delay))`). A reader who implements
   Algorithm 4.1 literally keeps $(1.75,-0.25)$ in step 11, arrives inside the goal
   tolerance in 12 steps, and cannot reproduce the last three rows of the table or the
   quoted $(0.51,-0.13)$ braking command. The walkthrough mentions the rule in prose, but
   the algorithm the reader implements must produce the numbers the chapter prints.
   **Fix:** add $\pos_g$ to the `\KwIn` of `\DwaCommand` and change the test to
   $\norm{\vel}\dt + \norm{\vel}^2/(2a_b) > \min\bigl(d,\ \norm{\pos_g - \pos}\bigr)$ with
   the end-of-line comment "brake for the goal as for a wall"; keep the clearance term at
   $d$ (this is exactly what the code does, since `admissible_speed` is monotone in its
   distance argument). Then shorten the sentence in lines 509-512 to a pointer to that
   line.
   **Category:** A.

5. **Location:** proof of `thm:ch14-safety`, line 734 ("the free distance along it is now
   $d' = d - \norm{\vel}\dt$").
   **Problem:** with $\dist$ capped at $d_{\max}$ by `eq:ch14-dist` this is an equality
   only when the cap is inactive; if $d = d_{\max}$ the new free distance may again be
   $d_{\max}$. The proof needs the inequality, not the equality, so as written it is a gap
   in an otherwise correct argument.
   **Fix:** "because the obstacles have not moved and the new ray is a sub-ray of the old
   one, the free distance along it satisfies $d' \ge d - \norm{\vel}\dt \ge
   \norm{\vel}^2/(2a_b)$ (the cap $d_{\max}$ can only raise it)". The remainder of the
   proof is unchanged.
   **Category:** A.

6. **Location:** caption of `fig:ch14-experiment`, lines 854-861.
   **Problem:** the caption contradicts itself - "(a) All three settings pass the pillar in
   the corridor, but the clearance-dominant drone refuses the corridor altogether and flies
   around the outside of the lower wall"; the clearance run never passes the pillar. It
   also says "three weight settings" while panel (b) plots four curves (the fourth,
   dash-dotted green, is the default weights with the global path), and the reader is not
   told that panel (a) has no legend of its own.
   **Fix:** "(a) The heading- and velocity-dominant runs thread the corridor and pass the
   pillar; the clearance-dominant run refuses the corridor mouth and flies around the
   outside of the lower wall. (b) ... The fourth curve (dash-dotted green) is the default
   weights with the heading term aimed at a lookahead point on the global path; it is the
   only run that reaches the goal. Panel (a) uses the same colours and line styles as the
   legend of (b)."
   **Category:** D.

7. **Location:** line 31 (`\orca`, first use), line 933 ("the nominal MAPF path"), line
   1199 (`\cbs or \ecbs` in the `dronebox`).
   **Problem:** STYLE_GUIDE section 3 requires every acronym to be expanded at its first
   use *in every chapter*; ORCA, MAPF, CBS and ECBS appear here unexpanded.
   **Fix:** line 31 "optimal reciprocal collision avoidance (\orca)"; line 933
   "the nominal multi-agent path finding (MAPF) path"; line 1199 "conflict-based search
   (\cbs) or its bounded-suboptimal variant \ecbs".
   **Category:** F.

8. **Location:** proof of `thm:ch14-safety`, line 736 ("or $0$, in which case it is
   trivially admissible").
   **Problem:** "trivially" is on the list of words the style guide forbids (section 1,
   Voice).
   **Fix:** "(or $0$; the zero command has $\dist(\vect{0}) = d_{\max}$ and is admissible)".
   **Category:** C.

## Suggestions

* `fig:ch14-example` caption: the scene panel draws 14 dots (the start plus the 13
  step end-points), so "the 13 positions" is off by one - say "the start and the 13
  step end-points". In panel (b) the caption names the crosses, the square and the star
  but not the blue dots; add "the dots the 16 admissible grid points".
* `figures/ch14/space-admissible.tex`: the label "$v > \sqrt{2\,\dist\,\dot v_b}$: cannot
  stop" sits at $(-0.55, 0.22)$, i.e. *below* the boundary curve and inside the admissible
  region. Move it into the hatched bite or attach a short leader line.
* Proof of `thm:ch14-incomplete`: the bound gives score $\le \beta$; say "strictly within
  $d_{\max}(1 - (\alpha + \gamma v_1/v_{\max})/\beta)$" so that the inequality is strict.
* `def:ch14-search-set`: define $\dim$ (2 or 3, the dimension of the velocity space) where
  it first appears, and note that $(2n+1)^{\dim}$ is an upper bound because the ball $V_s$
  clips the corners.
* Line 6 declares `\SetKwFunction{DwaCandidates}{WindowCandidates}`, which is never used;
  either drop it or use it on line~\ref{alg:ch14-command:grid} instead of the prose
  description of the grid.
* Length (currently 20 pages against the spec's 12-14). Three painless trims, in order of
  yield: (i) collapse steps 5-10 of `tab:ch14-trace`, which repeat the same command
  $(1.75,-0.25)$, into a single row "5-10 ... (six identical steps)"; (ii) the 1 m
  wall/2 m/s example is told three times (the "discrete-time refinement" paragraph,
  `exr:ch14-braking`, and the listing walkthrough) - keep the derivation and the exercise,
  cut the third telling; (iii) the four paragraphs of `sec:ch14-tuning` restate rows of
  `tab:ch14-weights`; two sentences each would do.
* "Fox et al.\ report $\alpha = 2.0$, $\beta = 0.2$, $\gamma = 0.2$" (line ~925): please
  re-check these against the experiments section of the 1997 magazine article before
  print, and if the values come from a later restatement, cite that source instead. All
  seven bib keys used here (`fox1997dwa`, `brock1999global`, `ogren2005convergent`,
  `choset2005principles`, `siciliano2016handbook`, `khatib1986realtime`,
  `vandenberg2011orca`) exist and their authors, titles, venues and years are correct;
  `ogren2005convergent` is missing its page range (188-195), which may be added or left
  out per the guide.
* A one-sentence remark that the per-axis box window is optimistic by a factor
  $\sqrt{\dim}$ for a vehicle with an isotropic limit $\norm{\vect{a}} \le a_{\max}$ would
  sharpen `def:ch14-window`; `exr:ch14-safety`(a) already leads there.
* `frontmatter/notation.tex` is still a placeholder; when it is filled, hand it this
  chapter's symbols ($\vel_a$, $V_s/V_a/V_d/V_r$, $\dist$, $d_{\max}$, $a_b$, $\Delta v$).
* The solutions appendix carries 4 of the 8 exercises, which matches ch12 and ch13
  practice; if one more is added, `exr:ch14-safety` is the one a lone reader will most
  want. Consider promoting it to `\difficulty{3}` as well - the chapter currently has a
  single level-3 item.

## What must be kept

The spine of this chapter is excellent and should survive revision untouched. The
discrete-time refinement of the braking test (`eq:ch14-braking-discrete`,
`eq:ch14-vadm`) with the 1 m wall counter-example is the best treatment of that point I
have seen in a textbook: it names a real bug that most DWA implementations contain, proves
the fix in `thm:ch14-braking-lemma`/`thm:ch14-safety` (the Riemann-sum argument and the
$\norm{\vel}^2/(2a_b) - a_b\dt^2/2 \le d'$ induction are both correct and elegant), and
backs it with a self-test that flies both versions. Proposition 14.2 is the right way to
state incompleteness - a checkable condition, an explicit pocket radius, and the honest
remark that a dominant heading term converts the local minimum into oscillation. The
worked example is exemplary: 25 candidates, the admissibility arithmetic done by hand,
13 rows of scores and a 13-step trace, every digit of which the code reproduces, and the
observation that "the clearance term, not the heading term, chose the side". Keep the
generated corridor/U-trap experiment and `tab:ch14-weights`, the DWA/ORCA/APF comparison
table, all four pitfall boxes (the moving-obstacle one with its step-7 collision is worth
its space), the relative-velocity repair for moving obstacles, the U-trap figure with the
global path drawn around it, and the coding exercise, whose four failure cases and paired
remedies are exactly the Week-7 milestone.

## Response to review (round 1)

All eight required changes are applied. The spine the review asked to keep is untouched:
`eq:ch14-braking-discrete`/`eq:ch14-vadm` with the 1 m wall counter-example,
`thm:ch14-braking-lemma`/`thm:ch14-safety`, `thm:ch14-incomplete` with its 1.65 m pocket,
the 25-candidate worked example with its 13 score rows and 13-step trace, the generated
corridor/U-trap experiment and `tab:ch14-weights`, the DWA/ORCA/APF table, all four
pitfall boxes, the relative-velocity repair, the U-trap figure and the coding exercise.

### Required changes

1. **`sec:ch14-tuning`, "Clearance dominates" (was line 902).** Done. The
   "clearance of at most $0.33$" sentence is gone; the paragraph now carries the step-1
   numbers printed by `evaluate()` at `corridor_scene()` with $(0.2,0.6,0.2)$: the
   straight command $(0.5,0)$ with $\dist = 2.65$ m, clearance $0.885$ and score
   $0.2+0.531+0.05 = 0.781$, against $(0.25,\pm 0.5)$ with clearance $1$, heading $0.641$
   and score $0.784$; $\beta$ gains $0.6\cdot 0.115 = 0.069$ and $\gamma$ $0.006$ against
   the $0.2\cdot 0.359 = 0.072$ that $\alpha$ loses, a margin of three thousandths. I
   re-ran `evaluate()` and confirmed every digit (0.7807 vs 0.7841). The rest of the
   paragraph (21 steps, 8.7 m, 47 % longer, goal reached from below) is unchanged and
   still matches `gen_ch14_traj.py` (`corridor & clearance & reached & 21 & 8.7`).

2. **`sec:ch14-properties`, "DWA is a local method" (was lines 799-801).** Done, with the
   reviewer's wording: "braking to within $4$~cm of the back wall and turning $9$~cm short
   of the arms". Recomputed from the 300-step default run:
   $x_{\max} = 4.7649$, $y \in [-1.3125, 1.2639]$, so $5.0-4.7649-0.2 = 0.035$ m to the
   back wall and $1.6-1.3125-0.2 = 0.088$ m to the arms; path length 80.5 m.

3. **`def:ch14-admissible` / `eq:ch14-Va`.** Done. The rotational condition is now
   $\abs{\omega} \le \sqrt{2\,\dist(v,\omega)\,\dot\omega_b}$, and the "Where the square
   root comes from" paragraph says that the sign of $\omega$ does not matter, that this is
   why the bars are needed, and that Fox et al. omit them (so that without them every
   $\omega < 0$ passes whatever the free distance). Nothing else changed.

4. **`alg:ch14-command` line `alg:ch14-command:admissible`, walkthrough, `tab:ch14-trace`.**
   Done. `\DwaCommand` now takes $\pos_g$ in `\KwIn` and in its signature (and the call in
   `alg:ch14-loop` passes it), and the admissibility test reads
   $\norm{\vel}\dt + \norm{\vel}^2/(2a_b) > \min(d, \norm{\pos_g - \pos})$ with the
   end-of-line comment "brake for the goal as for a wall". This is exactly the code, since
   `admissible_speed` is increasing in its distance argument, so
   $\min(\text{limit}(d), \text{limit}(d_g)) = \text{limit}(\min(d, d_g))$; the clearance
   term still uses $d$. The walkthrough is now one sentence pointing at that line.
   Algorithm 4.1 read literally now reproduces steps 11-13 of `tab:ch14-trace` and the
   braking command $(0.51,-0.13)$.

5. **Proof of `thm:ch14-safety` (was line 734).** Done, verbatim as asked: "because the
   obstacles have not moved and the new ray is a sub-ray of the old one, the free distance
   along it satisfies $d' \ge d - \norm{\vel}\dt \ge \norm{\vel}^2/(2a_b)$ (the cap
   $d_{\max}$ can only raise it)". The rest of the proof is unchanged.

6. **Caption of `fig:ch14-experiment`.** Rewritten as asked: panel (a) now says the
   heading- and velocity-dominant runs thread the corridor and pass the pillar while the
   clearance-dominant run refuses the corridor mouth; the fourth (dash-dotted green) curve
   is named as the default weights with the heading term on a global-path lookahead point
   and as the only run that reaches the goal; and the caption states that panel (a) uses
   the colours and line styles of the legend of (b). ("three weight settings" is gone.)

7. **Acronyms (lines 31, 933, 1199).** Done: "optimal reciprocal collision avoidance
   (\orca)" at first use; "the nominal multi-agent path finding (MAPF) path"; and in the
   drone box "from the global layer---conflict-based search (\cbs) or its
   bounded-suboptimal variant \ecbs---".

8. **"trivially" in the proof of `thm:ch14-safety`.** Replaced by "(or $0$; the zero
   command has $\dist(\vect{0}) = d_{\max}$ and is admissible)". A grep for
   *obviously / clearly / trivial / easy to see* now finds only one hit, inside the
   verbatim Python listing (`# hysteresis: keep v_a unless clearly beaten`), which is a
   source comment copied from `ch14_dwa.py`; I left it so the listing stays verbatim.

### Suggestions

Applied: the `fig:ch14-example` caption now says "the 14 blue dots are the start and the
13 step end-points" and names the dots in panel (b) as "the 16 admissible grid points, the
crosses the 9 inadmissible ones" (25 candidates, 16 admissible, verified by
`evaluate()`); `figures/ch14/space-admissible.tex` keeps the label outside but now draws a
leader line from it into the hatched bite; `thm:ch14-incomplete` says "meets an obstacle
strictly within"; `def:ch14-search-set` defines $\dim$ and says $(2n+1)^{\dim}$ is an
upper bound because the ball $V_s$ clips the corners; the unused
`\SetKwFunction{DwaCandidates}{WindowCandidates}` is deleted; `def:ch14-window` gains a
sentence that the per-axis box is optimistic by $\sqrt{\dim}$ under an isotropic limit,
pointing at `exr:ch14-safety`; `exr:ch14-safety` is promoted to `\difficulty{3}` and a
solution for it is added to `appendices/solutions/ch14-solutions.tex` (5 of 8 exercises
now have solutions), including the concrete moving-obstacle counter-example for part (b)
(free distance $0.175 < 0.1875$ m at $u = 0.3$ m/s).

Not applied, with reasons: the length trims were left alone. Collapsing steps 5-10 of
`tab:ch14-trace` conflicts with the "what must be kept" paragraph ("13 rows of scores and
a 13-step trace whose every digit the code reproduces"), and the brief forbids removing
required content to save space; the two remaining mentions of the 1 m wall outside
`sec:ch14-restrictions` (lines ~1117 and ~1170) are one-clause pointers, not retellings;
and required change 1 lengthens the tuning section rather than shortening it. The chapter
is still 20 PDF pages. The Fox et al. weights $(2.0, 0.2, 0.2)$ are left as printed
pending a copy of the 1997 magazine article; `references.bib` and
`frontmatter/notation.tex` are outside this chapter's file set.

### Verification

`cd Overleaf && ./build.sh ch14-dwa`: status 0, no `!` errors, no overfull boxes above
15 pt, no undefined references or citations belonging to this chapter (the remaining
`??` are `ch:chNN`/`ch:appX` from the single-chapter build). `python3 code/ch14_dwa.py`
exits 0 with its asserts passing; `python3 code/figures/gen_ch14_traj.py` regenerates
`figures/ch14/experiment.tex`, the example figures and the `figures/data/ch14-*.dat`
files unchanged (the Python was not modified). Every number quoted in the revised text
was re-read from that output.

(Note for the next round: `Overleaf/build/` is shared by all chapter builds, so a
concurrent build of another chapter can truncate its `.aux` while this chapter's run reads
it, which shows up as `build/only-ch14-dwa.aux:NN: File ended while scanning use of
\@newl@bel` and exit status 12. Re-running `./build.sh ch14-dwa`, or building into a
private `-outdir`, gives status 0; the failure never involves a ch14 file.)
