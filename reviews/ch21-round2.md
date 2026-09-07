# Review of Chapter 21 (Model Predictive Control) - round 2

Reviewed: `Overleaf/chapters/ch21-mpc.tex` (1466 lines), figures `Overleaf/figures/ch21/{idea,halfplane,example,tuning,chance,experiment}.tex`,
code `Overleaf/code/ch21_mpc.py` (688 lines) and `Overleaf/code/figures/gen_ch21_mpc.py`,
`Overleaf/appendices/solutions/ch21-solutions.tex`, `Overleaf/appendices/glossary/ch21-terms.tex`,
against `STYLE_GUIDE.md` section 9 (A-H), `docs/specs/ch21.md` and `docs/core-idea.txt` (Week 11, line 87).

**Build.** `cd Overleaf && ./build.sh ch21-mpc` returns status 0. No `!` errors. No undefined label or citation
belonging to this chapter (the `??` in the PDF are cross-chapter references and front-matter references, expected in a
single-chapter build). One overfull box, `0.25 pt` at lines 340-348 - far below the 15 pt threshold.
**Length.** Chapter body runs from PDF page 17 (chapter opening) to page 39 (last exercise) = **23 pages**, inside the
24-page ceiling. Nothing required by the spec is padding, so no cuts are demanded (see S5 for the only compressible half-page).

**Code.** `python3 code/ch21_mpc.py` runs in 2.5 s and the self-test passes. I re-ran the soft-weight sweep
independently (`w_lin=w_quad in {1,10,100}`) and reproduced RMS `0.1263 / 0.2073 / 0.2081` and minimum separations
`0.7775 / 0.9982 / 1.0000`, i.e. the `0.126 m`, `0.998 m`, `0.777 m` and `0.22 m` of Section 21.7.1.
Every number I could check reproduces: Table 21.3 row by row (2.477/0.861/-0.416/2.257/0.023/16.2 at t = 2.5 s, etc.),
RMS `0.208` and max error `0.532`, min separation `1.000` at `t = 4.2` s, guess separation `0.908` at `t = 2.1` s,
min/max speed `0.763 / 1.277`, `max |y| = 0.395`, lag `0.532`, warm/cold ADMM iterations `25.5/280` vs `46.6/420`
(quoted as 26 and 47), solve time `mean 1.32 ms / max 9.21 ms` (quoted as "about 1.3 ms ... under 10 ms ... hardware
dependent"), largest multiplier `18.70`, chance-constrained separation `1.143 m`, tuning minima
`vx5/vx10/vx20 = 0.2199/0.5634/0.7557`, and every entry of Table 21.4 against `figures/data/ch21-experiment.dat`.
Both listings are verbatim copies of `ch21_mpc.py` (lines 187 and 330). All ten `\cite` keys exist
(`references.bib` for seven, `bib/ch21-extra.bib` for `kerrigan2000soft`, `boyd2011admm`, `stellato2020osqp`) and
every one of them is a real publication whose authors, venue, volume and pages I can vouch for.

**Independent technical re-derivation.** Prop. 21.2 (Cauchy-Schwarz), Prop. 21.3 (apothem `e cos(pi/M)`, loss
`7.6 %` at M = 8 and `1.9 %` at M = 16), the condensed cost `eq:ch21-condensed-cost` and its `H`/`f`, every block of
`eq:ch21-qp-constraints` including the bounds `b_k` and `c_{k,m}`, the DARE and the rearrangement
`(A-BK)'P(A-BK)-P = -(Q+K'RK)`, Prop. 21.4 (exact penalty, KKT with `mu_k = w_1 - lambda_k*`), the chance-constraint
inversion `mu >= r + kappa_delta sigma` with `kappa = 1.28/1.64/2.33`, the inflation `0.500 m` at k = 15, and the
complexity claims of Section 21.6.3 (`O(N^3 n^3)` build, `O((nN)^2 + m nN)` per iteration, `O((nN)^3)` refactorisation,
banded `O(N)` sparse form) are all correct as printed. The ADMM pseudocode is a faithful transcription of the OSQP
iteration and of `solve_qp`, including the primal-infeasibility certificate.

**Round-1 items: all nine verified as resolved.** (1) `thm:ch21-stability` now stipulates the k = 0 stage sum and the
proof's bookkeeping matches. (2) Sizes and timings agree with the code and name the timed (hard) program. (3) The
sentence after `eq:ch21-qp-constraints` and the caption of Table 21.1 now say the keep-in rows are hard in the code and
that the last column is a recommendation. (4) `a_max/sqrt(n)`. (5) Solution to `exr:ch21-slack` says "about 19 ... 18.7
... 16.2", and `worked_example()` prints `largest multiplier over the run: 18.70`. (6) Table 21.3 caption fixed.
(7) `Pi_{[l,u]}`, `dy^+`, `dy^-` all defined. (8) `simulate` really has a `wind` argument (line 441) and the exercise
spells out the open-loop change. (9) ORCA, CBS and ECBS expanded at first use. Suggestions S1-S8 of round 1 were also
acted on. None of these is re-raised.

## Verdict

**Minor revision.** Three local defects remain, all one-line edits: one wrong index range in the chapter's central
definition (A), one symbol used for two different quantities inside a single subsection (C), and one symbol collision
between two sections (F). Nothing else in A-E is open; B, D, E and H are clean.

## Required changes

1. **`def:ch21-ocp` / `eq:ch21-ocp`, Section 21.3.2 (line 176), the second constraint line.**
   *Problem (A).* The line reads
   `\abs{u_{k,i}}\le a_{\max},\quad \abs{v_{k,i}}\le v_{\max},\quad \pos_k\in\mathcal{X},\qquad k=1,\dots,N`,
   i.e. a single index range `k = 1,...,N` for all three. The decision variables are `u_0,...,u_{N-1}`
   (as the objective's own `\sum_{k=0}^{N-1}\ctrl_k\T\mat{R}\ctrl_k` and the dynamics line `k=0,\dots,N-1` state), so
   as written the input bound is imposed on a non-existent `u_N` and **not** on `u_0`, the input the controller
   actually applies. This contradicts `eq:ch21-qp-constraints`, whose first block is the identity on the whole of
   `\mat{U}` with bounds `\pm a_{\max}\vect{1}` (30 rows for N = 15, as Section 21.4.2 counts), and it contradicts the
   code, whose self-test asserts `np.abs(rec["u"]) <= mpc.a_max` at every step. It is the chapter's central
   definition, so the off-by-one must not stand.
   *Fix.* Split the line into two:
   `& \abs{u_{k,i}}\le a_{\max},\qquad k=0,\dots,N-1,\\`
   `& \abs{v_{k,i}}\le v_{\max},\quad \pos_k\in\mathcal{X},\qquad k=1,\dots,N,\\`
   (One extra line in the `aligned`; nothing else in the chapter changes.)

2. **Section 21.4.3, the walkthrough paragraph after \cref{alg:ch21-admm} (lines 520-545), together with the `\KwIn`
   line of `alg:ch21-admm` (line 496).**
   *Problem (C).* `\sigma` denotes two different quantities within one subsection. In the algorithm's input list it is
   the ADMM regularisation (`regularisation $\sigma$`, and it appears as `\sigma\vect{z}` on
   line~`alg:ch21-admm:linsys` and in `\mat{K}\gets\mat{H}+\sigma\mat{I}+\rho\mat{G}\T\mat{G}`). Fifteen lines later
   the same letter is the residual scale: "the code tests them every ten iterations against the mixed tolerance
   $\eps_{\mathrm{abs}}+\eps_{\mathrm{rel}}\sigma$, where $\sigma$ is the largest of the terms that make up the
   residual being tested". A reader alone cannot tell that these are unrelated, and the code calls them `sigma`
   versus `s_prim`/`s_dual` (visible in `lst:ch21-admm`, which is printed two pages later).
   *Fix.* Rename the scale to match the listing: "... against the mixed tolerances
   $\eps_{\mathrm{abs}}+\eps_{\mathrm{rel}}s_{\mathrm{prim}}$ and
   $\eps_{\mathrm{abs}}+\eps_{\mathrm{rel}}s_{\mathrm{dual}}$, where
   $s_{\mathrm{prim}}=\max(\norm{\mat{G}\vect{z}}_\infty,\norm{\vect{w}}_\infty)$ and
   $s_{\mathrm{dual}}=\max(\norm{\mat{H}\vect{z}}_\infty,\norm{\vect{f}}_\infty,\norm{\mat{G}\T\vect{y}}_\infty)$
   (\code{s\_prim} and \code{s\_dual} in \cref{lst:ch21-admm})". Leave `\sigma` to the regularisation only.

3. **`alg:ch21-admm` line~`alg:ch21-admm:factor` and its walkthrough ("a linear system with the fixed matrix
   $\mat{K}$", line ~527) versus `eq:ch21-riccati` and Section 21.6.1.**
   *Problem (F, cosmetic but a genuine collision).* `\mat{K}` is the ADMM system matrix
   `\mat{H}+\sigma\mat{I}+\rho\mat{G}\T\mat{G}` in Section 21.4.3 and the LQR feedback gain
   `(\mat{R}+\mat{B}\T\mat{P}\mat{B})\inv\mat{B}\T\mat{P}\mat{A}` in `eq:ch21-riccati`, in
   `\kappa_f(\state)=-\mat{K}\state`, in "invariant set of $\mat{A}-\mat{B}\mat{K}$", and in the solution to
   `exr:ch21-feasibility`. The style guide forbids competing notation; the LQR `K` is standard and must stay.
   *Fix.* Rename the ADMM matrix to `\mat{M}` in line~`alg:ch21-admm:factor`, line~`alg:ch21-admm:linsys`
   (`\mat{M}\inv(\dots)`), line~`alg:ch21-admm:rho` ("refactorise $\mat{M}$") and in the two walkthrough sentences,
   and add the half-clause "(\code{Kinv} in \cref{lst:ch21-admm} is $\mat{M}\inv$)" so the pseudocode and the listing
   still line up without touching the code.

## Suggestions

* **S1.** Section 21.6.2: "This result, due to \textcite{kerrigan2000soft}". Exact penalty functions predate that
  paper by decades (Pietrzykowski 1969; Han & Mangasarian 1979). Write "the MPC form of this classical exact-penalty
  result is due to \textcite{kerrigan2000soft}" - one word, and it protects the chapter from a specialist reader.
* **S2.** `exr:ch21-chance` tells the reader to run `MPC(delta=$\delta$)` with `\Sigma_k=\Sigma_0+(k\dt)^2\Sigma_v`,
  but the covariance growth is supplied through `simulate(..., cov_growth=(Sigma0, Sigma_v))`. Name that argument the
  way Exercise 21.1 now names `wind=`, so the exercise is runnable without reading `simulate`'s body.
* **S3.** `exr:ch21-horizon` says "the stopping distance of \cref{ch:ch02}"; point at the proposition itself,
  `\cref{thm:ch02-stopping-distance}`, which is the exact result the exercise needs.
* **S4.** Table 21.2, row "Horizon $N$": "the QP grows quadratically" is loose next to Section 21.6.3. Write "the dense
  condensed Hessian grows quadratically with $N$ and a refactorisation cubically".
* **S5.** The only compressible half-page: items 1 and 2 of Section 21.6.3 ("The half-plane is an approximation",
  "Moving obstacles break the shifted-candidate argument") restate Pitfall 1 and Pitfall 2 of Section 21.8. If a page
  must be recovered to approach the spec's 15-17 target, cut those two items to one sentence each with
  `\cref` to the pitfalls; keep items 3 and 4, which have no counterpart elsewhere.
* **S6.** Section 21.3.1: the per-axis box `|u_{k,i}| <= a_max` is a *relaxation* of the disc (it admits
  `||a|| <= sqrt(n) a_max`), which the text only hints at through "if you need the disc or ball exactly". Half a
  sentence saying so, and noting that the worked example therefore declares `a_max = 2` m/s^2 *per axis*, closes the
  loop for a careful reader.
* **S7.** `_self_test` asserts `elapsed < 60.0` while the style guide budgets 10 s and the actual run is 2.5 s.
  Tighten the assert to 10 s so a future performance regression is caught.
* **S8.** The solutions file now covers 7 of 10 exercises, which is good. The three still uncovered are 21.1, 21.9
  (the Week-11 coding exercise) and 21.10; a five-line sketch for 21.9 - which quantities to log (formation error per
  step, count of steps with `dist > R_comm`, slack sums) and what the reactive baseline should look like - would help
  the lone reader most, because that exercise is the week's milestone.

## What must be kept

This is an exemplary control chapter for this audience, and the round-1 fixes did not cost it anything. Keep the
headlight metaphor and `fig:ch21-idea`, which land the receding-horizon principle in half a page; keep the derivation
of the condensed form and the block-by-block reading of `\mat{G}`, `\vect{l}`, `\vect{u}` after
`eq:ch21-qp-constraints`, which is exactly what a student needs to implement it, together with the new clause that
says which rows the shipped code softens. Keep both propositions and their proofs (the Cauchy-Schwarz half-plane and
the apothem argument), the exact-penalty proposition tied to *measured* multipliers (14-19, hence `w_1 = 50`), and the
honest stability section with its corrected k = 0 bookkeeping and its explicit statement that the guarantee is nominal.
Keep the worked example untouched: every entry of Table 21.3, the 1.000 m minimum separation at t = 4.2 s, the
0.908 m linearisation-point separation, the 26/47 warm/cold iteration counts and the 1.143 m chance-constrained
separation are machine-produced and I reproduced them. Keep the late-detection experiment with Table 21.4 and
`fig:ch21-experiment` - the result that the soft controller beats the hard one on *both* separation and tracking is
the intellectual pay-off of the chapter and the clearest possible argument for the Week-11 milestone. Keep the ADMM
pseudocode and the two verbatim listings, the chance-constraint section, the four pitfalls, the tuning table with its
units paragraph, the drone box, the six figures, the 32 index entries, and the ten well-graded exercises including the
leader-follower coding exercise that the code's `Follower` and `simulate(..., followers=...)` genuinely support.

## Response to review (round 2)

All three required changes are applied, plus seven of the eight suggestions.
Build: `./build.sh ch21-mpc` -> status 0, no errors, no overfull boxes above 15 pt,
no undefined labels of this chapter (only cross-chapter `ch:chNN` / `thm:ch02-*`
references, expected in a single-chapter build). Self-test: passes in 2.6 s.
Chapter length unchanged at 23 pages (the additions below are offset by S5).

### Required changes

1. **Off-by-one in the index ranges of `eq:ch21-ocp` (category A).** Applied exactly as
   prescribed. The single constraint line is now two lines inside the `aligned` block:
   `\abs{u_{k,i}}\le a_{\max},\qquad k=0,\dots,N-1,` and
   `\abs{v_{k,i}}\le v_{\max},\quad \pos_k\in\mathcal{X},\qquad k=1,\dots,N,`.
   The input box is now imposed on `u_0,...,u_{N-1}`, which agrees with the objective, with
   the dynamics line, with the first block of `eq:ch21-qp-constraints` (the identity on the
   whole of `U`, 30 rows for `N=15`) and with the assertion `np.abs(rec["u"]) <= mpc.a_max`
   in `code/ch21_mpc.py`. Nothing else changed.

2. **`\sigma` overloaded in Section 21.4.3 (category C).** The residual scale is renamed to
   match the listing. The walkthrough now reads "... against the mixed tolerances
   `eps_abs + eps_rel s_prim` and `eps_abs + eps_rel s_dual`, where
   `s_prim = max(||Gz||_inf, ||w||_inf)` and
   `s_dual = max(||Hz||_inf, ||f||_inf, ||G'y||_inf)` are the largest of the terms that make
   up the residual being tested (`s_prim` and `s_dual` in `\cref{lst:ch21-admm}`)", followed
   by an explicit sentence that `\sigma` stays with the regularisation of
   line~`alg:ch21-admm:factor`. `\sigma` now has exactly one meaning in the subsection.

3. **`\mat{K}` collision between the ADMM system matrix and the LQR gain (category F).**
   The ADMM matrix is renamed `\mat{M}` in `alg:ch21-admm:factor`, in
   `alg:ch21-admm:linsys` (`\mat{M}\inv(...)`), in `alg:ch21-admm:rho`
   ("refactorise `\mat{M}`"), in the walkthrough sentence, and in Section 21.6.4
   ("one product with `\mat{M}\inv`"), which was a fifth occurrence the review did not list.
   The walkthrough now spells out `\mat{M}=\mat{H}+\sigma\mat{I}+\rho\mat{G}\T\mat{G}`, adds
   the requested clause "(`Kinv` in `\cref{lst:ch21-admm}` is `\mat{M}\inv`)", and states
   that `\mat{K}` is reserved for the LQR gain of `eq:ch21-riccati`. The Python is untouched,
   so the listing still matches the file verbatim.

### Suggestions

* **S1 (applied).** Section 21.6.2 now reads "The MPC form of this classical exact-penalty
  result (exact penalties themselves go back to the nonlinear-programming literature of the
  nineteen sixties and seventies) is due to \textcite{kerrigan2000soft}". No new bib entry
  was added, since the style guide forbids citing works I cannot verify in
  `references.bib`.
* **S2 (applied).** `exr:ch21-chance` now names the argument:
  "... which you pass to the simulator as `simulate(..., cov_growth=(Sigma_0, Sigma_v))`".
* **S3 (applied).** `exr:ch21-horizon` now points at `\cref{thm:ch02-stopping-distance}`
  instead of `\cref{ch:ch02}`.
* **S4 (applied).** The "Horizon N" row of Table 21.2 now reads "the dense condensed Hessian
  grows quadratically with N and a refactorisation cubically".
* **S5 (applied).** Items 1 and 2 of Section 21.6.3 are cut to one sentence each, each with a
  `\cref{sec:ch21-implementation}` and the title of the pitfall that develops it. Items 3 and
  4 (solver tolerance, nominal stability) are untouched, as asked. This exactly pays for the
  text added by the required changes and S6, so the chapter stays at 23 pages.
* **S6 (applied).** Section 21.3.1 now says the per-axis box is a relaxation that admits
  `||a|| <= sqrt(n) a_max` along a diagonal, that `a_max` must therefore be declared per axis,
  and that the worked example accordingly takes `a_max = 2 m/s^2` per axis.
* **S7 (applied).** `assert elapsed < 60.0` is now `assert elapsed < 10.0` in
  `_self_test`; the run takes 2.6 s, so the margin is still ample and a regression is caught.
* **S8 (applied).** A solution sketch for `exr:ch21-coding` (Exercise 21.9, the Week-11
  milestone) is added to `appendices/solutions/ch21-solutions.tex`: how the follower's two
  extra row blocks are built from the leader's plan, what to log per step (formation error
  with mean/max/count above `e_max`, distance to the leader and the count of steps above
  `R_comm` -- both already recorded as `rec["form_err"]` and `rec["dist"]` -- and the slack
  sums in the soft version), what the reactive baseline is, and what the comparison should
  show. Solutions now cover 8 of 10 exercises; 21.1 and 21.10 remain open by design.

### Not changed

No numbers moved: the code changed only in the timing assertion, so no `.dat` file needed
regeneration and every quoted figure (minimum separation 1.000 m at t = 4.2 s, linearisation
point 0.908 m, largest multiplier 18.70, 26/47 warm/cold ADMM iterations, chance-constrained
1.143 m, Table 21.3, Table 21.4) is unchanged and still reproduced by
`python3 code/ch21_mpc.py`. Everything on the reviewer's keep list is intact.
