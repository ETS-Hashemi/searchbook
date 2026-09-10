# Review of Chapter 23 (Consensus and Formation Control) - round 2

## Verdict

**Minor revision.**

**Round-1 items: all six are resolved, correctly, and none is re-raised below.**
I checked each one against the current source:

1. *Example 23.1, "Discrete time." parenthesis* (line 574). Now reads "(after the first
   step drone~3 lands exactly on the average of its three neighbours,
   $(7.75+6.25+2.5)/3 = 5.5$, so its update term is zero and it never moves again ...)".
   This agrees with Table 23.2 (drone 3: $7.000 \to 5.500 \to 5.500 \to \dots$) and with
   row 3 of $\mat{L}\vect{z}(0) = 6$. **Fixed.**
2. *$\mu_k^k$ in the proof of Theorem 23.2* (lines 780-790). The theorem statement,
   \cref{eq:ch23-discreterate} and the proof now use $m$ for the time step and $k$ for the
   mode: $\vect{\delta}_m = \mat{P}^m\vect{\delta}_0 = \sum_{k\ge2}c_k\mu_k^m\vect{v}_k$,
   $\norm{\vect{\delta}_m} \le \rho^m\norm{\vect{\delta}_0}$. Consistent with
   `appendices/solutions/ch23-solutions.tex`. **Fixed.**
3. *Two meanings of $\mat{B}$*. The power-iteration matrix is now
   $\mat{W} = s\mat{I} - \mat{L} - \frac{s}{n}\vect{1}\vect{1}\T$ with the explicit
   parenthesis "(a different matrix from the pinning matrix $\mat{B}$ of
   \cref{eq:ch23-pinned})". I re-checked the spectrum: $\mat{W}\vect{1} = \vect{0}$ and
   $\mat{W}\vect{v}_k = (s-\lambda_k)\vect{v}_k$, so with $s = 2d_{\max} \ge \lambda_n$ the
   largest eigenvalue is indeed $s-\lambda_2$. **Fixed.**
4. *$\eps$ in the sigma-norm* (line 1030). Now $\norm{\vect{z}}_\sigma =
   (\sqrt{1+\sigma\norm{\vect{z}}^2}-1)/\sigma$ with the clause naming Olfati-Saber's
   $\epsilon$. **Fixed.**
5. *First-order gain renamed $k_c$*. Renamed at every site (protocol, $\eps = k_c\dt$,
   `\KwIn` and line 5 of Algorithm 23.1, the walkthrough, Corollary 23.1, the captions of
   Table 23.3 and Figure 23.4, the implementation notes, Exercise 23.7b and its solution),
   with the added sentence "The letter $k$ is reserved for the time step and the mode
   index" and an index entry. The notation row is present:
   `frontmatter/notation.tex:223` reads `$k_c$, $k_l$ & consensus gain of the first-order
   protocol; pinning gain of the leader & \cref{ch:ch23}\\`. **Fixed.**
6. *Exercise 23.5(a) "if and only if"*. The exercise now asks for the centroid velocity
   $-\frac1n\sum_i\sum_{j\in N_i}\vect{d}_{ij}$, states antisymmetry as sufficient, and
   asks for a non-antisymmetric counterexample; the solution gives the path $1-2-3$
   counterexample and says explicitly "sufficient but not necessary". **Fixed.**

**Build.** `./build.sh ch23-consensus-formation` returns status 0, no `!` errors, no
undefined ch23 references or citations (the `??` for `ch:ch11`, `ch:ch13`, `ch:ch14` are
other chapters in a single-chapter build, as the style guide allows), and the single
overfull box in the log (29.1 pt, "Rapidly-exploring random tree with goal bias") is in the
front-matter List of Algorithms, not in this chapter.

**Code.** `python3 code/ch23_consensus.py` passes in 2.9 s. `worked_example()` reproduces
Tables 23.1, 23.2 and 23.3 digit for digit ($e_F(0)=2.5000$, $e_c(0)=1.7941$, centroid
shift $(0.625,0.125)$, both discrete runs, the spectrum $\{0,1,3,4\}$).
`python3 code/figures/gen_ch23_formation.py` reproduces every number in the captions of
Figures 23.3, 23.4 and 23.7 ($\lambda_2 = 0.2679/1.1864$, $\tau = 3.73/0.84$ s, 1 % after
6.28/1.88 s; $e_F = 1.720 \to 0.124 \to 0.0025$ m and $1.003$ m without feed-forward; peak
$e_F = 0.356$ m at $t = 10.50$ s, recovery at $13.64$ s, closest approach $0.909$ m, max
edge $3.040$ m, min edge $1.564$ m, $\lambda_2 = 4$, zero violations, band $[6.86,11.68]$ s)
and rewrites the four committed `.dat` files byte-identically (`git status` clean).

**Independent re-derivations.** I re-checked by hand or with a short script: the spectrum
$\{0,1,3,4\}$ and its eigenvectors; $\lambda_2 = 2(1-\cos(\pi/6)) = 0.268$ for the path;
$\lambda_n \le 2d_{\max}$ and the $4$-cycle boundary case $\eps = 0.5 \Rightarrow \mu = -1$;
$\eps^\ast = 0.4$ with $\rho = 0.6$ against $\rho = 2/3$ at $\eps = 1/3$;
$\mu_1(\mat{L}+\mat{B}) = 0.17834$ so $1/\mu_1 = 5.61$ s; $\mat{M}\inv\vect{1} =
(4, 16/3, 17/3, 20/3)$ giving the 4 m / 6.67 m lags and the residual $e_F = 1.190$ m;
the sandwich $e_c \le e_F \le 2e_c$ at $n = \abs{E} = 4$; $\zeta = (0.75, 1.010, 1.125)$;
the inscribed-polygon loss $1-\cos(\pi/8) = 7.6\,\%$; the non-closing-triangle residual
$e_F = 1/3$; the derivative of the range barrier; the directed three-drone cases (a), (b)
and (c) of Exercise 23.4 including $x_3(t) = x_1(0) + (x_3(0)-x_1(0))e^{-t} +
(x_2(0)-x_1(0))te^{-t}$; and the complement shortcut $\{0,2,4,4\}$ in the solution to
Exercise 23.1. All are correct. All 21 citation keys resolve, and every bibliography entry
printed in the PDF (Anderson 2008, Bullo 2009, Fiedler 1973, Jadbabaie 2003, Ji 2007,
Khatib 1986, Krick 2009, Mesbahi 2010, Oh 2015, Olfati-Saber 2004/2006/2007, Ren
2005/2007/2008, Reynolds 1987, Tanner 2007, Vicsek 1995, Xiao 2004, Yang 2010, Zavlanos
2011) has authors, venue, volume, year and page range that I can vouch for.

**Completeness.** Every "must cover" item of `docs/specs/ch23.md` is present, and the
Week 11 items of `docs/core-idea.txt` (formation error, communication radius, constraints
enforced rather than repaired) are covered, with the plan's coding exercise as
\cref{exr:ch23-coding}.

**What blocks Accept** are two new findings, both in category A and both one-line edits: a
modal equation stated for a range of indices in which it is false, and an algorithm input
list that does not supply a symbol the algorithm's own line uses. Because both are strictly
local, the verdict is Minor, not Major.

**Length.** The chapter body is PDF pages 27-49 of `build/only-ch23-consensus-formation.pdf`
(printed 318-340), i.e. **23 pages**, inside the 24-page ceiling of this review. It is still
above the spec's 13-15 page target, but every page carries a "must cover" item; I require no
cuts. Two optional trims are listed under Suggestions.

## Required changes

1. **Location:** `chapters/ch23-consensus-formation.tex`, Proposition 23.5
   (`prop:ch23-second`), \cref{eq:ch23-modes2} at lines 934-938 and the sentence at
   lines 941-945.
   **Problem:** the modal equation
   $\ddot{q}_k + (k_v\lambda_k + k_d)\dot{q}_k + k_p\lambda_k q_k = 0$ is asserted "for
   $k = 1, \dots, n$", but for $k = 1$ it is false whenever $\dot{\vect{r}} \ne \vect{0}$,
   and it then contradicts the proposition's own last sentence. In the shifted variables
   $\vect{y}_i = \pos_i - \vect{o}_i$, \cref{eq:ch23-second} without pinning gives
   $\ddot{\vect{y}} = -k_p\mat{L}\vect{y} - k_v\mat{L}\dot{\vect{y}} - k_d\dot{\vect{y}}
   + k_d\,\dot{\vect{r}}\vect{1}$; the forcing $k_d\dot{\vect{r}}\vect{1}$ lies entirely in
   the $\lambda_1 = 0$ mode, so that mode obeys $\ddot{q}_1 + k_d\dot{q}_1 =
   k_d\sqrt{n}\,\dot{r}$, not the homogeneous equation. Read literally, (23.20) with
   $k = 1$ says $\dot{q}_1 \to 0$, i.e. the centroid comes to rest, whereas the next
   sentence correctly says "its velocity decays to $\dot{\vect{r}}$ if $k_d > 0$". In the
   same sentence, "with $k_v = k_d = 0$ every mode oscillates for ever at the angular
   frequency $\sqrt{k_p\lambda_k}$" is also false for $k = 1$: $\lambda_1 = 0$ gives
   frequency zero, i.e. a constant-velocity drift of the centroid, not an oscillation.
   **Fix:** (i) restrict the displayed equation to the disagreement modes, "$k = 2, \dots,
   n$"; (ii) add one sentence after it: "The centroid mode $k = 1$ ($\lambda_1 = 0$,
   $\vect{v}_1 = \vect{1}/\sqrt{n}$) obeys $\ddot{q}_1 + k_d\dot{q}_1 =
   k_d\sqrt{n}\,\dot{r}$, so the centroid velocity converges to $\dot{\vect{r}}$ when
   $k_d > 0$ and is conserved when $k_d = 0$."; (iii) change "every mode oscillates for
   ever" to "every mode with $\lambda_k > 0$ oscillates for ever"; (iv) add the omitted
   forcing term to the two places where the shifted dynamics are displayed, the proof
   sketch at line 947 and the sentence at lines 502-504, writing
   $\ddot{\vect{y}} = -k_p\mat{L}\vect{y} - (k_v\mat{L}+k_d\mat{I})\dot{\vect{y}}
   + k_d\dot{\vect{r}}\vect{1}$ (or state once that $\dot{\vect{r}}$ is taken constant and
   absorbed by working in the frame moving with the reference).
   **Category: A.**

2. **Location:** `chapters/ch23-consensus-formation.tex`, the `\KwIn` of Algorithm 23.1
   (line 433) together with line~\ref{alg:ch23-formation:ff} (line 444), and the `\KwIn` of
   Algorithm 23.2 (line 511) together with its first body line (line 514).
   **Problem:** both input lists give the reference velocity only to the pinned drone -
   "if drone $i$ is pinned ($b_i = 1$), the reference $\vect{r}$ and its velocity
   $\dot{\vect{r}}$" and "reference $\vect{r}$, $\dot{\vect{r}}$ if pinned" - but both
   algorithms use $\dot{\vect{r}}$ unconditionally on *every* drone: line 8 of
   Algorithm 23.1 is $\vel_i \gets \vel_i + \dot{\vect{r}} + \vel_i^{\mathrm{extra}}$ and
   line 1 of Algorithm 23.2 is $\ctrl_i \gets -k_d(\vel_i - \dot{\vect{r}})$. A reader
   implementing Algorithm 23.1 from the box alone has no value of $\dot{\vect{r}}$ on a
   follower. The prose already says the right thing twice (line 375, "the followers can
   receive from it through the graph"; line 471, "is forwarded to the followers"; line 500
   for the second-order case), and the Python agrees (`formation_velocity` adds `ref_vel`
   to all rows), so only the two input declarations are wrong.
   **Fix:** in the `\KwIn` of Algorithm 23.1 replace the clause by "the reference velocity
   $\dot{\vect{r}}$, forwarded from the leader through the graph to every drone (use
   $\vect{0}$ if unknown); if drone $i$ is pinned ($b_i = 1$), also the reference
   $\vect{r}$"; make the same change in the `\KwIn` of Algorithm 23.2 ("$\dot{\vect{r}}$
   on every drone, $\vect{r}$ if pinned").
   **Category: A.**

## Suggestions

* **Discrete time index.** \Cref{eq:ch23-discrete}, Table 23.2 and the third summary bullet
  index discrete time by $k$, while Theorem 23.2 and its proof index it by $m$ (correctly,
  since $k$ is the mode there). Add half a clause to the theorem statement - "the iteration
  $\vect{x}_{m+1} = (\mat{I}-\eps\mat{L})\vect{x}_m$ of \cref{eq:ch23-discrete}, whose time
  step is written $m$ here because $k$ indexes the modes in the proof" - so the reader is
  not left wondering whether two different iterations are meant.
* **Exercise 23.2(b) duplicates a worked pitfall.** The pitfall "A disconnected graph agrees
  in clusters" (lines 752-762) already gives the same graph, the same initial states
  $(1,3,10,14)$, the same limit $(2,2,12,12)$ and the same disagreement norm 10 that
  Exercise 23.2(b) asks the student to predict, and the solution repeats them a third time.
  Either change the numbers in the exercise, or turn it into "how large must
  $R_{\mathrm{comm}}$ be before the four drones agree globally, and what is $\lambda_2$
  then?".
* **Kronecker parse in Proposition 23.3.** $-\mat{M}\inv\vect{1}\otimes\dot{\vect{r}}$
  (twice, statement and proof) is easier to read as
  $-(\mat{M}\inv\vect{1})\otimes\dot{\vect{r}}$; and the solution to Exercise 23.7(b) writes
  the same forcing as $\dot{\vect{r}}\vect{1}$ instead of $\vect{1}\otimes\dot{\vect{r}}$.
  Unify on the $\otimes$ form.
* **Undefined symbol $\ttc$** (line 1069, "collision-free for the horizon $\ttc$"). It is a
  book-wide macro but is used here without a gloss; write "for the ORCA horizon $\ttc$ of
  \cref{ch:ch13}".
* **Self-test comment out of step with its assertion.** In `code/ch23_consensus.py`, block 7
  is commented "Inconsistent displacement vectors (d_ji != -d_ij) make the centroid drift
  instead of settling", but the only assertion is that `displacement_targets(O)` *is*
  antisymmetric. Either retitle the block ("displacements derived from offsets are
  antisymmetric by construction") or add the three-line drift test that the comment promises
  (integrate the protocol with a deliberately non-antisymmetric $\vect{d}$ and check the
  centroid velocity against $-\frac1n\sum_i\sum_j\vect{d}_{ij}$).
* **Solutions coverage.** Seven of the eight exercises now have solutions, which is in line
  with the rest of the book. Exercise 23.8 is the coding exercise; three lines of expected
  output in `appendices/solutions/ch23-solutions.tex` (spectrum $\{0,1,3,4\}$; final square
  $\vect{o}_i + (0.625, 0.125)$; peak $e_F = 0.36$ m at $t = 10.5$ s, back below $0.05$ m at
  $t = 13.6$ s; $\lambda_2 = 4$ at $R_{\mathrm{comm}} = 3.2$ m and $\lambda_2 = 2$ at
  $2.5$ m) would let a lone reader check part (c) without reading the reference
  implementation.
* **Optional trims (no required content).** If a page is wanted: (i) rows $k = 3, 4$ of the
  diverging half of Table 23.2 (the sign flip is already visible at $k = 1, 2$; the reviser
  kept them in round 1, which is defensible); (ii) the first paragraph of the `dronebox`
  ("From the global planner") repeats the opening scenario of \cref{sec:ch23-motivation}
  almost sentence for sentence - three lines instead of eight would be enough, since the
  new information is only that $\vect{r}, \dot{\vect{r}}$ come from the CBS/MPC path.

## What must be kept

The chapter's organising idea is still its best asset and must not be disturbed: everything
is consensus on a shifted state, announced in the `keyidea` box, made precise by
$\vect{y}_i = \pos_i - \vect{o}_i$ in \cref{def:ch23-formation}, and then reused to derive
formation control, leader-following and the second-order controller without a single new
proof. Keep Proposition 23.1 with its five short complete proofs (Gershgorin and Fiedler
included), Theorem 23.1's eigen-decomposition proof, Corollary 23.1's tightness remark, and
Theorem 23.3 with the $e_c$/$e_F$ sandwich (23.19), which is what makes the chapter's error
metric theoretically meaningful and is confirmed numerically in the worked example. Keep
Example 23.1 whole: one graph carrying the Laplacian, the spectrum, the Fiedler vector, the
continuous run, both discrete runs and the formation run is an unusually economical worked
example, and every number in it comes from `worked_example()`. Keep the four pitfall boxes,
especially "An unstable step size looks like a bug in the messages" with the exact $4$-cycle
boundary case, and "Avoidance breaks the formation, and must be allowed to", which is the
right engineering judgement and connects directly to \cref{ch:ch24} and \cref{ch:ch25}. Keep
the algorithms written from one drone's point of view with the broadcast line, the seven
figures (all referenced, consistent `sb*`/pgfplots styles, three generated by a committed
script), Table 23.4 of the three formation-control families, the connectivity-maintenance
section with both the hard-constraint and the barrier route and the $\mat{W}$
power-iteration monitor, the 37 index entries, the glossary entries, and above all the
`_self_test()` of `code/ch23_consensus.py`, which pins every quoted number in the chapter,
the captions, the exercises and the solutions (including $\mu_1 = 0.178$, the lag vector
$(4, 16/3, 17/3, 20/3)$, $e_F = 1.19$ m, the spectrum $\{0,2,4,4\}$ of Exercise 23.1 and the
$e_F = 1/3$ of the non-closing triangle) - that test is the reason this review could verify
the chapter so quickly, and it should be treated as part of the chapter.

## Response to review (round 2)

Both required changes are applied, plus five of the six cheap suggestions. The
build is status 0 with no errors, `code/ch23_consensus.py` self-tests pass
(now including the new numbers), and `code/figures/gen_ch23_formation.py` was
re-run so the three `.dat` files are current.

### Required change A1 — the modal equation (23.20) and the missing forcing term

* **(i)** `eq:ch23-modes2` is now stated for the disagreement modes only,
  `k = 2, ..., n`, and the sentence introducing it says "decouple into the
  disagreement modes".
* **(ii)** The sentence the reviewer asked for follows the display:
  "The centroid mode k = 1 (lambda_1 = 0, v_1 = 1/sqrt(n)) carries the whole
  forcing and obeys qddot_1 + k_d qdot_1 = k_d sqrt(n) rdot instead, where rdot
  is the component of the reference velocity in the coordinate considered, so
  the centroid velocity converges to rdot when k_d > 0 and is conserved when
  k_d = 0." The old (correct but now redundant) last sentence of the
  proposition was folded into this one, so the statement says it once.
* **(iii)** "every mode oscillates for ever" is now "every mode with
  lambda_k > 0 oscillates for ever ..., while the centroid keeps whatever
  velocity it started with".
* **(iv)** Both displays of the shifted dynamics now carry the forcing:
  the proof sketch reads `yddot = -k_p L y - (k_v L + k_d I) ydot + k_d 1 (x) rdot`
  and continues "the forcing is a multiple of 1 = sqrt(n) v_1, so it appears in
  the mode k = 1 alone and every mode k >= 2 is homogeneous"; the prose display
  in Section 6.4.4 (former lines 502-504) was corrected in the same way, with
  "with rdot constant" stated there, and a following clause explaining that the
  forcing moves the centroid and leaves the shape alone. The proposition now
  also assumes a constant rdot explicitly.

### Required change A2 — rdot in the input lists of both algorithms

* Algorithm 23.1 `\KwIn` now reads "... the reference velocity rdot, forwarded
  from the leader through the graph to every drone (use 0 if unknown); if drone
  i is pinned (b_i = 1), also the reference r; ...".
* Algorithm 23.2 `\KwIn` now reads "... the reference velocity rdot on every
  drone (use 0 if unknown), the reference r if pinned".
* The one place in the chapter that still implied the opposite — the dronebox
  sentence "One drone is pinned to it; the others need nothing but their
  neighbours' positions and offsets" — now says that rdot is forwarded through
  the graph to the others as well.

### Suggestions

* **Discrete time index (applied).** Theorem 23.2 now reads "the iteration
  x_{m+1} = (I - eps L) x_m of (6.8), whose time step is written m here because
  k indexes the modes in the proof, conserves the average ...".
* **Exercise 23.2(b) (applied, rewritten).** It no longer repeats the pitfall's
  prediction. It now gives the four positions on a line and asks how large
  R_comm must be before the drones agree globally, and for lambda_2 and the
  time constant there and at R_comm = 10 m. The solution answers R_comm >= 9 m
  (the gap between the inner pair), the path graph with lambda_2 = 2 - sqrt(2)
  = 0.586 and 1/lambda_2 = 1.71 s, and at 10 m the spectrum {0, 2, 4, 4} with
  lambda_2 = 2. Both numbers are now pinned by new assertions in
  `_self_test()` (block 4), including that R_comm = 8.9 m is still
  disconnected.
* **Kronecker parse (applied).** Proposition 23.3 (statement and proof) now
  writes `-(M^{-1} 1) (x) rdot`, Exercise 23.7(b) writes
  `-v ((k_c L + k_l B)^{-1} 1) (x) e`, and the solution to 23.7(b) uses
  `1 (x) rdot` for the forcing instead of `rdot 1`.
* **tau_ORCA (applied).** The flocking section now says "collision-free for the
  ORCA horizon tau of Chapter 13".
* **Self-test block 7 (applied, drift test added).** The block is retitled and
  now integrates the protocol on a path of three drones with a deliberately
  non-antisymmetric d (both ends of every edge asking for the same offset) and
  checks that the centroid velocity equals -(1/n) sum_i sum_j d_ij =
  (-4/3, 0) m/s and that the swarm really drifts away, exactly what the comment
  promises. The antisymmetry assertion for `displacement_targets` is kept.
* **Solutions coverage (applied).** `ch23-solutions.tex` now has a solution for
  the coding exercise 23.8 giving the expected output of every part: the
  spectrum {0, 1, 3, 4}; the final square at o_i + (0.625, 0.125) m and
  e_F(0) = 2.500 m below 1% after 4.1 s; e_F(20 s) = 0.0025 m with feed-forward
  against 1.00 m without; and for the avoidance run the intruder inside 2 m
  from t = 6.9 s to t = 11.7 s, the peak e_F = 0.36 m at t = 10.5 s, back below
  0.05 m at t = 13.6 s, closest approach 0.91 m, longest edge 3.04 m, no
  communication violation and lambda_2 = 4 throughout; at R_comm = 2.5 m the
  4-cycle with spectrum {0, 2, 2, 4}. Every one of these numbers is printed by
  `worked_example()` or by `gen_ch23_formation.py`, which were re-run to check
  them.
* **Optional trims (partly applied).** The dronebox's first paragraph was
  shortened by two lines while fixing the rdot sentence above. The rows k = 3, 4
  of the diverging half of Table 23.2 were kept: they are the rows that show the
  divergence growing rather than merely starting, and the chapter is not short
  of space in a way that would justify losing them.

Nothing on the "must keep" list was touched: Proposition 23.1 and its five
proofs, Theorem 23.1, Corollary 23.1, Theorem 23.3 with the e_c/e_F sandwich,
Example 23.1 in full, the four pitfall boxes, the seven figures, Table 23.4,
the connectivity-maintenance section, the index and glossary entries and the
self-test are all unchanged except where a required change or an applied
suggestion demanded it.
