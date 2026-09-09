# Review of Chapter 23 (Consensus and Formation Control) - round 1

## Verdict

**Minor revision.**

This is a strong, technically careful chapter. I checked every definition, every
proposition and theorem statement, every proof, both algorithms, all four tables and all
seven figure captions against the canonical sources (Olfati-Saber & Murray 2004;
Olfati-Saber, Fax & Murray 2007; Ren & Beard 2005/2008; Olfati-Saber 2006; Oh, Park & Ahn
2015; Jadbabaie, Lin & Morse 2003; Fiedler 1973) and against the code. The build is clean
(status 0, no errors, no undefined ch23 labels or citations, the single overfull box is in
the front-matter List of Algorithms and not this chapter's). `python3 code/ch23_consensus.py`
passes its self-test in 3.2 s and reproduces Tables 23.1-23.3 digit for digit;
`python3 code/figures/gen_ch23_formation.py` reproduces every number quoted in the captions
of Figures 23.3, 23.4 and 23.7 (lambda_2 = 0.27/1.19, tau = 3.7/0.84 s, 1% after 6.3/1.9 s;
e_F = 1.72 -> 0.12 -> 0.0025 m and 1.00 m without feed-forward; peak e_F = 0.356 m at
t = 10.50 s, recovery at 13.64 s, min intruder distance 0.909 m, max edge 3.040 m, min edge
1.564 m, lambda_2 = 4, zero violations). I re-derived by hand: the spectrum {0,1,3,4} and
its eigenvectors, e_F(0) = 2.5 and e_c(0) = 1.794, the sandwich (23.19), mu_1 = 0.1783 and
M^-1 1 = (4, 16/3, 17/3, 20/3) giving the 4 m / 6.67 m lags and the residual e_F = 1.19 m,
zeta = (0.75, 1.01, 1.13), eps* = 0.4 with rho = 0.6, the Perron-matrix and Gershgorin
bounds, the triangle residual e_F = 1/3 in the solutions file, and the boids/flocking and
delay (tau < pi/(2 lambda_n)) results. All are correct.

Every "must cover" item of `docs/specs/ch23.md` is present, and all 21 citation keys resolve
to entries in `references.bib` / `bib/ch23-extra.bib` whose authors, venues, volumes and
page ranges I can vouch for. What blocks Accept is one factually wrong sentence in the
worked example, one broken index in a proof, three symbol collisions and one false
"if and only if" in an exercise (and in its solution). All six are local, one-paragraph
fixes; hence Minor, not Major.

Length: the chapter body occupies pages 199-221 of `build/only-ch23-consensus-formation.pdf`,
i.e. **23 pages**. That is inside the 24-page ceiling of this review, so no cut is
*required*, but it is well above the spec's 13-15 page target and the style guide's 12-18
band. Concrete, painless trims are listed under Suggestions; none of them touches required
content.

## Required changes

1. **Location:** `chapters/ch23-consensus-formation.tex`, lines 573-574, Example 23.1
   ("*Discrete time.*" paragraph), parenthesis "(drone~3, which sits at the average of its
   neighbours, does not move at all in the first step because $\eps \cdot 3 \cdot 0 = 0$)".
   **Problem:** This is false and contradicts Table 23.2 and the code. At $k=0$ drone 3 holds
   $z_3 = 7$ while its neighbours 1, 2, 4 hold $(10, 4, 1)$ with average $5$; row 3 of
   $\mat{L}\vect{z}(0)$ is $6$, not $0$, and the table shows drone 3 moving from $7.000$ to
   $5.500$ in the *first* step. It is from $k = 1$ onwards that drone 3 sits exactly on its
   neighbours' average, $(7.75 + 6.25 + 2.5)/3 = 5.5$, and then never moves again.
   **Fix:** Replace the parenthesis with, e.g., "(after the first step drone 3 lands exactly
   on the average of its three neighbours, $(7.75+6.25+2.5)/3 = 5.5$, so its update term is
   zero and it does not move again, while the others keep converging towards it)".
   **Category: A.**

2. **Location:** line 785, proof sketch of Theorem 23.2 (`thm:ch23-discrete`):
   "$\vect{\delta}_k = \mat{P}^k\vect{\delta}_0$ expands in the modes $k \ge 2$ with the
   factors $\mu_k^k$".
   **Problem:** the letter $k$ denotes the time step and the mode index in the same sentence,
   so "$\mu_k^k$" is not a well-formed expression; a reader cannot tell which $k$ is which.
   (The solution in `appendices/solutions/ch23-solutions.tex` gets this right by using $m$.)
   **Fix:** rewrite the sentence with a separate time index, e.g. "$\vect{\delta}_m =
   \mat{P}^m\vect{\delta}_0 = \sum_{k\ge2} c_k\,\mu_k^m\,\vect{v}_k$, so mode $k$ is damped
   by $\mu_k^m$ at step $m$". Keep $\rho^k$ in (23.17) or switch it to $\rho^m$ as well, but
   be consistent inside the theorem and its proof.
   **Category: A.**

3. **Location:** `\mat{B}` is defined twice with different meanings - line 367
   ("$\mat{B} = \diag(b_1,\dots,b_n)$", the pinning matrix, used in (23.11), Prop. 23.3 and
   Ex. 23.7b) and line 1150 in Section 23.7.3 *What to monitor*
   ("$\mat{B} = s\mat{I} - \mat{L} - \frac{s}{n}\vect{1}\vect{1}\T$", the power-iteration
   matrix).
   **Problem:** two incompatible definitions of the same symbol in one chapter; the style
   guide forbids competing notation. (The power-iteration matrix itself is correct: its
   eigenvalues are $0$ on $\vect{1}$ and $s-\lambda_k$ on $\vect{v}_k$, so the dominant one
   is $s-\lambda_2$.)
   **Fix:** rename the power-iteration matrix, e.g. $\mat{W} = s\mat{I} - \mat{L} -
   \frac{s}{n}\vect{1}\vect{1}\T$, and adjust the sentence "whose largest eigenvalue is
   $s - \lambda_2$" accordingly.
   **Category: F.**

4. **Location:** line 1030, Section 23.7.2 (flocking): the smoothed norm
   "$\norm{\vect{z}}_\sigma = (\sqrt{1 + \eps\norm{\vect{z}}^2} - 1)/\eps$".
   **Problem:** `\eps` is fixed by (23.9) and by `frontmatter/notation.tex` (line 219) as the
   *step size of discrete consensus* for this chapter; reusing it for Olfati-Saber's
   sigma-norm parameter inside the same chapter collides with the notation table.
   **Fix:** write the sigma-norm with a different parameter, e.g.
   "$\norm{\vect{z}}_\sigma = (\sqrt{1 + \sigma\norm{\vect{z}}^2} - 1)/\sigma$ with a small
   $\sigma > 0$" (and note in one clause that Olfati-Saber calls this parameter
   $\varepsilon$).
   **Category: F.**

5. **Location:** the first-order gain `$k$`: line 320 ("A gain $k > 0$ in front of the sum"),
   line 327 ("$\eps = k\,\dt$"), Algorithm 23.1 `\KwIn` (line 437, "gains $k$, $k_l$"),
   line 464 ("$\eps = k\dt$ ... $k\dt < 1/d_{\max}$"), Corollary 23.1 (line 724, "With a gain
   $k$ ... the rate is $k\lambda_2$"), the caption of Table 23.3 (line 644) and of Figure 23.4
   (line 873), the implementation note (line 1167) and Exercise 23.7b (line 1526).
   **Problem:** `frontmatter/notation.tex` (line 25) reserves $k$ as the *time index*, and this
   chapter itself uses $k$ as the discrete time index in (23.8) and (23.17) and as the mode
   index in the proofs of Theorems 23.1-23.2 and Prop. 23.5. The formula "$\eps = k\,\dt$"
   printed one line above "$\vect{x}_{k+1} = (\mat{I}-\eps\mat{L})\vect{x}_k$" is genuinely
   ambiguous. Neither the consensus gain nor the pinning gain $k_l$ appears in the ch23 block
   of the notation table, although $k_p$, $k_v$, $k_d$ do.
   **Fix:** rename the first-order gain to $k_c$ (consensus gain) everywhere listed above,
   including Algorithm 23.1 lines 5, `\KwIn`, and the code caption of Listing 23.2 (the code
   keyword `gain=` need not change), and add one row to the "Networks and consensus" block of
   `frontmatter/notation.tex`:
   `$k_c$, $k_l$ & consensus gain of the first-order protocol; pinning gain of the leader &
   \cref{ch:ch23}\\`. (Report the notation-table edit in the revision note; it is a
   front-matter file, not `searchbook.sty`.)
   **Category: F.**

6. **Location:** Exercise 23.5(a) (`exr:ch23-inconsistent`, lines 1490-1491) and the matching
   sentence in `appendices/solutions/ch23-solutions.tex`, solution to `exr:ch23-inconsistent`,
   part (a): "show that the centroid is stationary **if and only if** $\vect{d}_{ji} =
   -\vect{d}_{ij}$ on every edge".
   **Problem:** the "only if" direction is false. Summing (23.12) gives
   $\frac{d}{dt}\sum_i \pos_i = -\sum_i\sum_{j\in N_i}\vect{d}_{ij}$, so the centroid is
   stationary exactly when that *total* sum vanishes; edgewise antisymmetry is sufficient but
   not necessary. Counterexample on the path $1-2-3$: $\vect{d}_{12} = \vect{d}_{21} = (1,0)$
   and $\vect{d}_{23} = \vect{d}_{32} = (-1,0)$ sum to zero, the centroid does not move, yet
   no edge is antisymmetric. A student who tries to prove the stated equivalence will fail.
   **Fix:** restate as "(a) Sum \cref{eq:ch23-formation} over all drones and show that the
   centroid moves with the constant velocity $-\frac1n\sum_i\sum_{j\in N_i}\vect{d}_{ij}$;
   conclude that it is stationary whenever $\vect{d}_{ji} = -\vect{d}_{ij}$ on every edge, and
   give an example that is not antisymmetric on any edge and still leaves the centroid fixed."
   Make the same correction in the solutions file ("The second vanishes if and only if ..." ->
   "The second vanishes whenever $\vect{d}_{ji} = -\vect{d}_{ij}$ on every edge; in general
   the centroid moves with the constant velocity ...").
   **Category: E** (and A for the solution).

## Suggestions

* **Length (23 pages against a 13-15 page spec).** Four cuts, none of which removes required
  content, recover roughly 1.5 pages:
  (i) the section-by-section roadmap at the end of Section 23.1 (lines 50-62) repeats the
  table of contents; two sentences suffice;
  (ii) the `historynote` (lines 1068-1080) and the *Further reading* paragraph (lines
  1412-1430) name the same six papers (Vicsek, Jadbabaie, Olfati-Saber x2, Ren & Beard,
  Tanner, Fiedler) - keep the narrative in the history note and trim *Further reading* to the
  sources it alone introduces (Ren-Beard-Atkins, Mesbahi & Egerstedt, Bullo et al., Oh et al.,
  Anderson, Krick, Ji, Zavlanos, Yang, Xiao & Boyd);
  (iii) the "Asynchronous updates and packet loss" paragraph (lines 1187-1200) restates the
  delay bound $\pi/(2\lambda_n)$ and the switching-union condition already proved in
  Section 23.6.3; compress to four lines that only add what is new (stale neighbour states,
  asymmetric loss breaking the exact average);
  (iv) Table 23.2 can drop rows $k = 3, 4$ of the diverging run - two rows already show the
  sign flip.
* **Equation (23.21), flocking.** The navigation feedback is written as
  `- \underbrace{c_1(\pos_i-\pos_\gamma) - c_2(\vel_i-\vel_\gamma)}`. The typeset formula is
  correct, but the *braced group* is $c_1(\cdot) - c_2(\cdot)$ preceded by a minus, which
  reads as $-c_1(\cdot) + c_2(\cdot)$ (anti-damping). Move both signs inside the brace:
  `+ \underbrace{\bigl(-c_1(\pos_i-\pos_\gamma) - c_2(\vel_i-\vel_\gamma)\bigr)}_{\text{navigation feedback}}`.
* **Solutions coverage.** Only 4 of the 8 exercises have entries in
  `appendices/solutions/ch23-solutions.tex` (ch21, ch20 and ch13 carry 7-8 of 10). Two gaps
  matter because the main text delegates a claim to them: Exercise 23.2(c) is the only
  justification given for $e_F^2 = \frac{2n}{n-1}e_c^2$ (line 283), and Exercise 23.6(b) is
  the only justification for the inscribed-polygon relaxation $\vect{n}_q\T(\pos_i-\pos_j)
  \le R_{\mathrm{comm}}\cos(\pi/Q)$ (line 1098). Both are short; adding them (and one for the
  directed-graph Exercise 23.4) would close the loop. Note for the writer: for $Q=8$ the
  inner polygon gives away $1-\cos(\pi/8) = 7.6\%$ of the range in the normal directions.
* **Figure 23.7 caption.** The top panel plots a second curve labelled "distance to intruder
  /10" in the legend, but the caption never says the intruder distance is scaled by ten. Add
  a clause: "the intruder distance is drawn divided by ten so that both curves fit one axis".
* **Disconnected-graph pitfall (line 759).** "the disagreement norm stays at $10$ for ever"
  is loose: $\norm{\vect{\delta}(0)} = \sqrt{110} = 10.49$ and it *decays to* 10 and stops
  there. Write "settles at 10 instead of decaying to zero".
* **Figure 23.1 caption (line 88).** "their sum (orange) points from $\vect{x}_i$ towards
  $\abs{N_i}$ times the neighbours' average" - the sum equals $\abs{N_i}$ times *the vector
  from $\vect{x}_i$ to the neighbours' average*; the current phrasing names a point that does
  not exist. Suggested: "their sum (orange) is $\abs{N_i}$ times the vector from
  $\vect{x}_i$ to the neighbours' average, so ...".
* **Kronecker order (line 368).** $\vect{e} = \vect{x} - \vect{r}\otimes\vect{1}$ should be
  $\vect{1}\otimes\vect{r}$ to match the stacking used in Prop. 23.3
  ($-\mat{M}\inv\vect{1}\otimes\dot{\vect{r}}$) and in Exercise 23.7(b). One-symbol fix.
* Consider one sentence in Section 23.4.5 noting that the absolute damping $-k_d(\vel_i -
  \dot{\vect{r}})$ requires every follower to know $\dot{\vect{r}}$ (forwarded through the
  graph, as stated for the first-order case on line 469) - otherwise a reader may think it is
  purely local.

## What must be kept

The architecture of the chapter is exactly right and should not be disturbed: the single
idea - "everything here is consensus on a shifted state" - is announced in the `keyidea` box,
made precise by $\vect{y}_i = \pos_i - \vect{o}_i$ in Definition 23.3, and then reused to
derive formation control, leader-following and the second-order controller without a single
new proof. That is the best pedagogical decision in the chapter. Keep Proposition 23.1 with
its five short, complete proofs (including the Gershgorin and Fiedler steps), Theorem 23.1's
eigen-decomposition proof and Corollary 23.1's tightness remark, and Theorem 23.3 with the
$e_c$/$e_F$ sandwich (23.19) - the sandwich is what makes the chapter's error metric
theoretically meaningful and it is checked numerically in the worked example ($e_c \le e_F
\le 2e_c$). Keep Example 23.1 in full: one graph carrying the Laplacian, the spectrum, the
Fiedler vector, the continuous run, both discrete runs (converging and diverging) and the
formation run is an unusually economical worked example, and every number in it is produced
by `worked_example()`. Keep all four pitfall boxes, especially "An unstable step size looks
like a bug in the messages" with the exact 4-cycle boundary case, and "Avoidance breaks the
formation, and must be allowed to", which is the correct engineering judgement and connects
directly to `\cref{ch:ch24}` and `\cref{ch:ch25}`. Keep the algorithms written from one
drone's point of view with the broadcast line, the seven figures (all referenced, all in the
shared `sb*` styles, three of them generated with a committed script), Table 23.4 of the
three formation-control families, the 36 index entries, and the complete, accurate
bibliography.
