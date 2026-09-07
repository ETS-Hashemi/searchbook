# Review of Chapter 14 (The Dynamic Window Approach) - round 2

## Verdict

**Minor revision.**

All eight required changes of round 1 are resolved, and I checked each one against the
code rather than against the reviser's description:

1. `sec:ch14-tuning`, "Clearance dominates" (lines 916-929). Fixed and correct.
   `evaluate()` at `corridor_scene()` with $(0.2,0.6,0.2)$ prints $(0.5,0)$: $\dist=2.6536$,
   clearance $0.8845$, $G=0.78072$; $(0.25,\pm 0.5)$: clearance $1$, heading $0.6409$,
   $G=0.78408$. Margin $0.00336$ = "three thousandths"; $0.6\cdot0.1155=0.069$,
   $0.2\cdot0.0295=0.006$, $0.2\cdot0.3591=0.072$. Every digit reproduces.
2. `sec:ch14-properties`, lines 814-815. Fixed. The 300-step default U-trap run has
   $x_{\max}=4.7649$, $y\in[-1.3125,1.2639]$, so $0.0351$ m to the back wall and $0.0875$ m
   to the arms; 32 reversals of $\dot y$; after step 8 the trajectory never returns below
   $x=3.25$, so "without leaving the U" is right; length $80.5$ m.
3. `eq:ch14-Va` now carries $\abs{\omega}$ and the paragraph explains why. Applied.
   (One residual problem in the same formula survives; see required change 1.)
4. `alg:ch14-command` takes $\pos_g$ and tests $>\min(d,\norm{\pos_g-\pos})$ on
   line~9; the algorithm read literally now produces steps 11-13 of `tab:ch14-trace` and
   the braking command $(0.51,-0.13)$. Applied.
5. Proof of `thm:ch14-safety` now reads $d' \ge d - \norm{\vel}\dt \ge \norm{\vel}^2/(2a_b)$
   with the $d_{\max}$ remark. Applied.
6. Caption of `fig:ch14-experiment` rewritten; it now matches `experiment.tex`, which
   plots three curves in panel (a) and four in panel (b). Applied.
7. ORCA (line 30), MAPF (line 956), CBS/ECBS (lines 1222-1223) expanded. Applied.
8. "trivially" replaced. A grep for the banned words now finds one hit only, inside the
   verbatim listing (`# hysteresis: keep v_a unless clearly beaten`); see suggestions.

Verification of this round. `python3 code/ch14_dwa.py` exits 0 in 1.19 s with its asserts
passing; `python3 code/figures/gen_ch14_traj.py` regenerates the figures and `.dat` files
byte-identically (git reports no change under `Overleaf/figures/`). I re-checked all 13
rows of `tab:ch14-candidates`, all 13 rows of `tab:ch14-trace`, all 9 rows of
`tab:ch14-weights`, the final position $(4.816,0.030)$, length $4.977$ m, minimum clearance
$0.016$ m, the free distance $0.6084$ m (recomputed by hand: $1.2-\sqrt{0.35}$), the
admissible speeds $1.5595$ / $1.1377$ m/s, the braking sum $1.25$ m, the $0.062$ m of the
1 m wall test, the $17$/$16$ steps in 2D/3D, and the step-7 collision of the moving-obstacle
pitfall (I re-ran the static-view loop separately: it collides exactly at step 7). The
$1.65$ m pocket of `thm:ch14-incomplete` recomputes as
$3(1-(0.2+0.2\cdot 0.7071/2)/0.6)=1.6465$ m; the complexity counts $25/125/121/1331$ are
right; `thm:ch14-braking-lemma` (right Riemann sum of a non-increasing function) and the
induction of `thm:ch14-safety` are both correct as printed; `eq:ch14-arc` matches Fox,
Burgard and Thrun (1997). Every "must cover" item of `docs/specs/ch14.md` and every Week-7
item of `docs/core-idea.txt` and `appA` is present. All seven bib keys exist and their
authors, titles, venues, volumes, numbers and years are correct.

Build. `./build.sh ch14-dwa` returns status 12, but the failure is the shared-`build/`
race the round-1 note already described (`build/only-ch14-dwa.aux:25: File ended while
scanning use of \@newl@bel`); building the identical source with
`latexmk -g -pdf -outdir=<private> -jobname=rv14` returns status 0, no `!` errors, no
overfull box above 15 pt, and no undefined reference or citation belonging to this chapter
(the `??` are `ch:chNN`/`ch:appX` from the single-chapter build). I do not count this
against the chapter.

Length. The chapter itself is pages 14-33 of the single-chapter PDF, i.e. **20 pages**,
against 12-18 in STYLE_GUIDE section 2 and 12-14 in the spec. I looked hard for padding and
found under one page of it; the rest is required content and must stay. Required change 3
names the two pure repetitions and nothing else.

Three required changes remain, all local: one formula that is dimensionally wrong as
printed (inherited from the original paper, but this chapter has already committed to
repairing that formula), one line reference that points one line past its target, and the
length trim. Nothing needs restructuring.

## Required changes

1. **Location:** `def:ch14-admissible` / `eq:ch14-Va` (lines 258-262) and the paragraph
   "Where the square root comes from", lines 279-283 ("The condition on $\omega$ in
   \cref{eq:ch14-Va} is the same argument applied to the rotation, so that the robot can
   also stop turning.").
   **Problem:** the second condition, $\abs{\omega} \le \sqrt{2\,\dist(v,\omega)\,\dot\omega_b}$,
   is not dimensionally consistent and is therefore not "the same argument applied to the
   rotation". $\dist(v,\omega)$ is a length in metres (\cref{eq:ch14-dist}) and
   $\dot\omega_b$ is in rad/s$^2$, so the right-hand side has units
   $\sqrt{\mathrm{m}\cdot\mathrm{rad}}/\mathrm{s}$, not rad/s; with the chapter's own
   numbers ($\dist = 0.608$ m, $\dot\omega_b = 2$) it returns the bare number $1.56$, which
   is not an angular rate. The braking argument applied to the rotation gives
   $\omega^2 \le 2\,\Delta\theta\,\dot\omega_b$, where $\Delta\theta$ is the *heading change*
   still available before the obstacle, $\Delta\theta(v,\omega) = \abs{\omega}\dist(v,\omega)/v$
   along the arc. Fox et al.\ substitute the translational $\dist$ for $\Delta\theta$; the
   chapter repairs their missing absolute value one sentence earlier and promises exact
   definitions, so it cannot present this substitution as the same derivation. A reader who
   checks units (the chapter trains them to, see `pitfall` "Scoring in different units")
   will stop here.
   **Fix:** keep Fox et al.'s form for fidelity but label it as what it is. Replace lines
   279-283 with, for example: "The condition on $\omega$ is the braking argument applied to
   the rotation: the turn must be stoppable within the heading change still available before
   the obstacle, $\omega^2 \le 2\,\Delta\theta(v,\omega)\,\dot\omega_b$ with
   $\Delta\theta(v,\omega) = \abs{\omega}\,\dist(v,\omega)/v$. Fox et al.\ write the
   translational free distance $\dist(v,\omega)$ in place of $\Delta\theta$, as
   \cref{eq:ch14-Va} does; the two sides then do not carry the same units, and the condition
   is a heuristic cap on $\omega$ rather than a braking guarantee. The sign of $\omega$ does
   not matter -- a fast left turn is as hard to stop as a fast right turn -- which is why
   \cref{eq:ch14-Va} needs the bars; Fox et al.\ omit them, and without them every
   $\omega < 0$ passes whatever the free distance. The drone form of
   \cref{def:ch14-admissible}, which is what \cref{alg:ch14-command} and all the code use,
   has only the translational test, so nothing else in the chapter depends on this."
   Alternatively print $\abs{\omega} \le \sqrt{2\,\Delta\theta(v,\omega)\,\dot\omega_b}$ in
   `eq:ch14-Va` and note in one clause that Fox et al.\ write $\dist$ there. Either way, add
   half a sentence to the glossary entry *Admissible velocity*
   (`appendices/glossary/ch14-terms.tex`, line 3), which currently states only the
   translational form and is unaffected.
   **Category:** A.

2. **Location:** walkthrough of \cref{alg:ch14-command}, lines 520-521
   ("Line~\ref{alg:ch14-command:admissible} is the discrete admissibility test
   \cref{eq:ch14-vadm}"); the label sits on line 481 of the source.
   **Problem:** `\label{alg:ch14-command:admissible}` is attached to the `\KwContinue`
   inside the `\If`, so it resolves to algorithm line **9**, which in the printed algorithm
   reads `continue`. The test itself is on line **8**. The chapter therefore tells the
   reader that "Line 9 is the discrete admissibility test", pointing at a bare `continue`.
   Every other line reference in this chapter (lines 2, 3, 4, 7, 10, 12 of Algorithm 1.1 and
   4, 5, 8, 9 of Algorithm 1.2) is exact, so this one reads as an error.
   **Fix:** move the label onto the test line, e.g. write the branch as
   `\lIf{$\norm{\vel}\dt + \norm{\vel}^2/(2a_b) > \min(d,\ \norm{\pos_g - \pos})$}{\KwContinue}\label{alg:ch14-command:admissible}`
   (one line, comment `\tcp*{brake for the goal as for a wall}` kept), which also saves a
   line; or keep the two-line form and reword the walkthrough as "Line~8 is the discrete
   admissibility test \cref{eq:ch14-vadm} and line~9 discards the candidate".
   **Category:** G.

3. **Location:** `lst:ch14-window` (lines 1076-1110) and the duplicated sentence at lines
   509-510 and 1053-1054.
   **Problem:** the chapter is 20 PDF pages against the 12-18 of STYLE_GUIDE section 2 and
   the 12-14 of the spec. Almost all of the excess is required content and must not be cut,
   but two items are pure repetition. (i) `lst:ch14-window` prints `dynamic_window()`
   (5 lines) and `braking_candidate()` (11 lines), which restate \cref{eq:ch14-Vd} and
   line~4 of \cref{alg:ch14-command} with nothing added; the listing's actual subject is
   `window_candidates()`. (ii) "The grid is centred on $\vel_a$, so ``keep the current
   velocity'' is always a candidate" (lines 509-510) is repeated almost verbatim as "The
   grid is centred on $\vel_a$ on purpose, so that ``keep the current velocity'' is always a
   candidate" (lines 1053-1054).
   **Fix:** (i) cut `dynamic_window()` and `braking_candidate()` from the listing, keep
   `window_candidates()`, and change the caption to "The candidate grid over the dynamic
   window (from \code{code/ch14\_dwa.py}); the helpers \code{dynamic\_window()} and
   \code{braking\_candidate()} implement \cref{eq:ch14-Vd} and
   line~\ref{alg:ch14-command:brake} directly." Then adjust the sentence at line 1112 to
   name only line~\ref{alg:ch14-command:grid}, and the "line 12" pointer at line 1119 to the
   new numbering of `lst:ch14-dist` (unchanged, it refers to the other listing). (ii) delete
   the sentence at lines 1053-1054. Do **not** cut anything else for length: the trace
   table, the discrete-time refinement, the two proofs, the four pitfalls and the tuning
   experiment are all required content.
   **Category:** G.

## Suggestions

* `figures/ch14/space-window.tex`: the black dot marking $(\omega_a, v_a)$ sits at
  $(0.1,0.6)$, which is also in the red-cross (inadmissible) list. The figure therefore
  shows the robot currently flying an inadmissible command, the one state
  \cref{thm:ch14-safety} says cannot arise with static obstacles. Either move the dot to an
  admissible cell (e.g. $(0.2,0.5)$, keeping the window centred by shifting the rectangle),
  or add one clause to the caption: "here the previous command has just become inadmissible
  because a new obstacle came into range".
* Line 805-807 ("With a dominant heading term the drone never rests, since some moving
  candidate always beats $\beta$"): "always" is stronger than the argument supports - it
  needs an admissible non-zero candidate with
  $\alpha\,\mathrm{heading} + \gamma\,\mathrm{velocity} \ge \beta(1-\mathrm{clearance})$,
  which a tight pocket can deny. Write "usually" and state that condition in the same
  sentence.
* Line 770-771 ("Fox et al.\ test $v$ and $\omega$ separately, which is simpler and
  conservative"): "conservative" is an unproved comparison with the joint arc-braking
  condition. "simpler, and in the cases that matter more restrictive" would be safe.
* Proof of `thm:ch14-safety`: since required change 4 of round 1 put
  $\min(d, \norm{\pos_g-\pos})$ into line~8 of the algorithm, add one clause showing the
  goal term obeys the same recursion - $\norm{\pos_g - \pos'} \ge \norm{\pos_g-\pos} -
  \norm{\vel}\dt$, so the braking candidate passes the stricter test too. Without it the
  reader has to check that (ii) still matches the test the printed algorithm performs, and
  the claim on line 517 ("it is also the command returned when nothing else is admissible,
  which with static obstacles cannot happen") rests on the same step.
* `def:ch14-admissible` defines "admissible" by the continuous \cref{eq:ch14-Va}, while
  \cref{alg:ch14-command}, `thm:ch14-safety`, the tables and the code all use
  \cref{eq:ch14-vadm}. The switch is announced in prose but the term ends up with two
  meanings. Consider adding \cref{eq:ch14-vadm} to `def:ch14-admissible` as its second
  displayed line, or promoting the discrete refinement to its own numbered definition.
* `eq:ch14-clearance` writes $\min(\dist(\vel), d_{\max})/d_{\max}$, but
  \cref{eq:ch14-dist} already caps $\dist$ at $d_{\max}$; the $\min$ is redundant in the
  definition (it is needed in the code, which is fine).
* Line 926 ("$47\,\%$ longer than the direct route"): $8.7/5.9 = 1.475$, so the comparison
  is with the $5.9$ m default run, not with the straight line ($6$ m, $45\,\%$). Say "than
  the $5.9$~m of the default run".
* `tab:ch14-trace` steps 6-10 are five rows with the same $\vel_a$, the same command and
  terms that differ in the third decimal. Collapsing them into one row "6-10 ... (five
  identical steps)" would save a third of a page without losing anything; I leave this to
  the author because round 1 asked for the full trace to be kept.
* `code/ch14_dwa.py`, `dwa_command()`: the comment `# hysteresis: keep v_a unless clearly
  beaten` contains one of the words STYLE_GUIDE section 1 forbids, and it is printed
  verbatim in `lst:ch14-dist`. Change it in the `.py` (e.g. "unless the best candidate wins
  by more than the margin") and re-copy the listing.
* American spelling. STYLE_GUIDE section 1 asks for plain American English; this chapter has
  33 British forms (`normalised`, `normalisation`, `discretised`, `centred`, `behaviour`,
  `colours`, `metre`, `summarises`, `optimisation`), the most of any chapter in the book -
  ch21, ch20 and ch19 have 28, 22 and 18, most others 0-5. This is a book-wide copyedit
  item, not a defect of this chapter alone, but ch14 is where it is worst.
* `frontmatter/notation.tex` is still a 13-line placeholder; when it is filled, hand it this
  chapter's symbols: $\vel_a$, $V_s/V_a/V_d/V_r$, $\dist$, $d_{\max}$, $a_b$, $\dot v_b$,
  $\dot\omega_b$, $\Delta v$, $v_{\mathrm{adm}}$, $\dim$.
* `bib/ch14-extra.bib`: `ogren2005convergent` is missing its page range (188-195); add it or
  leave it out per the guide. All other bibliographic details of the seven keys used here are
  correct as printed. I could not open the 1997 magazine article, but $\alpha = 2.0$,
  $\beta = 0.2$, $\gamma = 0.2$ (line 941) is the weighting the paper reports for RHINO and
  matches the value quoted throughout the literature; I see no reason to change it.
* `appendices/solutions/ch14-solutions.tex` carries 5 of the 8 exercises. `exr:ch14-arcs`
  (the arc derivation) and `exr:ch14-units` (part (c), the $\lambda$ scaling argument) are
  the two a lone reader will most want next.

## What must be kept

The spine of this chapter is now unusually strong and none of it should be touched. The
discrete-time refinement of the braking test (`eq:ch14-braking-discrete`, `eq:ch14-vadm`)
with the 1 m wall counter-example remains the best treatment of that point I have seen in a
textbook: it names a bug most DWA implementations contain, proves the fix in
`thm:ch14-braking-lemma` and `thm:ch14-safety` (the Riemann-sum bound and the
$\norm{\vel}^2/(2a_b) - a_b\dt^2/2 \le d'$ induction are both correct and elegant), and flies
both versions in the self-test. `thm:ch14-incomplete` is the right way to state
incompleteness: a checkable condition, an explicit $1.65$ m pocket, and the honest remark
that a dominant heading term converts the local minimum into oscillation. The worked example
is exemplary and every digit of it reproduces - 25 candidates, the admissibility arithmetic
done by hand, 13 scored rows, a 13-step trace, and the observation that "the clearance term,
not the heading term, chose the side". The repaired tuning paragraph is now better than what
it replaced: it shows a three-thousandth margin deciding a whole trajectory, which is exactly
the lesson about weight tuning. Keep the generated corridor/U-trap experiment and
`tab:ch14-weights`, the DWA/ORCA/APF comparison table, all four pitfall boxes (the
moving-obstacle one with its verified step-7 collision earns its space), the
relative-velocity repair, `fig:ch14-utrap` with the global path drawn around it, the drone
box, and the coding exercise, whose four failure cases and paired remedies are precisely the
Week-7 milestone.

## Response to review (round 2)

All three required changes are applied. The chapter builds with status 0, no `!` errors and
no overfull boxes above 15 pt; `python3 code/ch14_dwa.py` passes its self-test (exit 0). No
code logic changed, so no `.dat` file needed regenerating and every number quoted in the text
still comes from the same run.

### Required change 1 (A) — the rotational admissibility condition

Rewritten in the paragraph *Where the square root comes from* (`chapters/ch14-dwa.tex`).
The text now says that the braking argument applied to the rotation gives
$\omega^2 \le 2\,\Delta\theta(v,\omega)\,\dot\omega_b$ with
$\Delta\theta(v,\omega)=\lvert\omega\rvert\,\dist(v,\omega)/v$, the heading change still
available before the obstacle; that Fox et al. write the translational $\dist$ in place of
$\Delta\theta$, as `eq:ch14-Va` does; that the two sides then do not carry the same units
($\sqrt{\mathrm{m\cdot rad}}/\mathrm{s}$ against rad/s); and that the condition is therefore a
heuristic cap on $\omega$, not a braking guarantee. The sentence on the missing absolute value
is kept, and a closing clause states that the drone form of `def:ch14-admissible` — the one
`alg:ch14-command` and all the code use — has only the translational test, so nothing else in
the chapter depends on this. `eq:ch14-Va` itself is unchanged, keeping Fox et al.'s form for
fidelity. Half a sentence was added to the *Admissible velocity* entry of
`appendices/glossary/ch14-terms.tex` saying the same thing.

### Required change 2 (G) — `\label{alg:ch14-command:admissible}` pointed at a bare `continue`

The branch is now the one-line form
`\lIf{...}{\KwContinue\tcp*[f]{brake for the goal as for a wall}\label{alg:ch14-command:admissible}}`,
following the convention of ch04. The label resolves to algorithm line 8, which is the test
itself (verified in `build/chapters/ch14-dwa.aux`: `alg:ch14-command:admissible}{{8}`), and the
algorithm is one line shorter (12 lines instead of 13). The end-of-line comment is set with
`\tcp*[f]` so that `\lIf` does not emit an extra empty numbered line.

### Required change 3 (G) — repetition

(i) `lst:ch14-window` now prints only `window_candidates()`; `dynamic_window()` and
`braking_candidate()` are cut and the caption reads "The candidate grid over the dynamic window
(from code/ch14_dwa.py); the helpers dynamic_window() and braking_candidate() implement
Equation (3.7) and line 4 directly." The following sentence now names only
`line~\ref{alg:ch14-command:grid}`. (ii) The duplicated sentence in *Resolution of the velocity
grid* ("The grid is centred on $\vel_a$ on purpose...") is deleted; the copy in the walkthrough
of `alg:ch14-command` is kept. Nothing else was cut: the trace table, the discrete-time
refinement, both proofs, the four pitfalls and the tuning experiment are untouched.

### Suggestions adopted

* `fig:ch14-spaces` caption (c) now ends "here the previous command $(\omega_a, v_a)$ itself
  carries a cross, because a new obstacle has just come into range and made it inadmissible",
  which is the cheap half of the alternative; the figure file is unchanged.
* "the drone never rests, since some moving candidate always beats $\beta$" is now "usually does
  not rest, because some admissible non-zero candidate then satisfies
  $\alpha\,\mathrm{heading}+\gamma\,\mathrm{velocity} > \beta(1-\mathrm{clearance})$ ... a tight
  pocket can still deny it".
* "simpler and conservative" is now "simpler and, in the cases that matter, more restrictive".
* The proof of `thm:ch14-safety` gains the goal-term recursion
  $\lVert\pos_g-\pos'\rVert \ge \lVert\pos_g-\pos\rVert-\lVert\vel\rVert\dt$, so the induction is
  carried out for $\tilde d=\min(d,\lVert\pos_g-\pos\rVert)$, the quantity line 8 actually tests.
* `def:ch14-admissible` now says in its last sentence that the test is sharpened to
  `eq:ch14-vadm` below and that the discrete form is the one the algorithm, the theorem, the
  tables and the code use.
* `eq:ch14-clearance`: a clause notes that the `min` is redundant there because `eq:ch14-dist`
  already caps $\dist$ at $d_{\max}$, and that the code keeps it as a guard.
* "47 % longer than the direct route" is now "47 % longer than the 5.9 m of the default run".
* `code/ch14_dwa.py`: the comment `# hysteresis: keep v_a unless clearly beaten` (forbidden word)
  is now `# keep v_a unless beaten by the margin`; `lst:ch14-dist` was re-copied to match.
* `bib/ch14-extra.bib`: `ogren2005convergent` now carries `pages = {188--195}`.
* American spelling: 33 British forms replaced (normalis*, discretised, centred, behaviour(s),
  colours, metre(s)/centimetre(s), summarises, optimisation, neighbour(s)); "optimistic" was left
  alone. `grep` for the British forms now returns nothing in the chapter, glossary, solutions and
  figure files.
* `appendices/solutions/ch14-solutions.tex`: solutions added for `exr:ch14-arcs` (the arc
  derivation, the circle of radius $v/\omega$, the pose $(1.683, 0.919, 1)$ after 2 s, and why the
  predicted pose matters for a differential drive but hardly for a drone) and for
  `exr:ch14-units` (all three parts; (a) and (b) computed from `evaluate()` on
  `ex:ch14-approach`: $(1.00, 0.50)$ wins with 1.330 in metres and with 82.87 in centimetres,
  where the heading term is 0.6 % of the score). Seven of the eight exercises now have solutions;
  only the Week-7 coding exercise is left open.

### Suggestions not adopted

* `tab:ch14-trace` rows 6–10 were **not** collapsed: round 1 asked for the full trace and the
  reviewer marked this optional.
* `frontmatter/notation.tex` is outside this chapter's file set (the brief forbids editing it).
  Its symbols for ch14 are, for the editor: $\vel_a$, $V_s/V_a/V_d/V_r$, $\dist$, $d_{\max}$,
  $a_b$, $\dot v_b$, $\dot\omega_b$, $\Delta v$, $v_{\mathrm{adm}}$, $\dim$.

### Length

The chapter is 21 PDF pages of body (pp. 15–35 of the single-chapter build) against the 12–18 of
STYLE_GUIDE section 2. The two repetitions the review named are gone (about 19 lines); the
required rewrite of the rotational condition and the proof clause added about 25 lines back.
Nothing else was cut, on the review's explicit instruction that the remaining excess is required
content.
