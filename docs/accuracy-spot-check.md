# Accuracy spot-check (second, independent reviewer)

Scope: every theorem, lemma, proposition and corollary of the book (144 statements)
plus the 8 comparison/complexity tables collected in the mechanical extract, checked
for (1) truth of the statement, (2) validity of the proof, (3) complexity claims,
(4) correct hypotheses on the named classical results. Definitions were opened in the
chapter sources wherever the statement depends on them (`def:ch02-closest-approach`,
`def:ch04-admissible/consistent`, `def:ch07-conflicts`, `def:ch10-focal`,
`eq:ch12-quadratic`, `eq:ch14-vadm`, `eq:ch17-radius`, `def:ch18-model`,
`def:ch23-laplacian`, `tab:ch14-parameters`). Read-only: no file under `Overleaf/`
was modified.

## Findings

| # | file:line | item | severity | what is wrong | proposed fix |
|---|-----------|------|----------|---------------|--------------|
| 1 | ch23-consensus-formation.tex:159 | `prop:ch23-laplacian` (v) | error | "if $G$ is not complete then $\lambda_2\le d_{\min}$" is false for **weighted** graphs, which `def:ch23-laplacian` explicitly admits ("weighted graphs use $w_{ij}>0$") and whose degrees are $d_i=\sum_j w_{ij}$. Counterexample: the path $1-2-3$ with $w_{12}=1$, $w_{23}=100$ is not complete, has $d_{\min}=1$ and $\lambda_2=1.4962$ (verified numerically). Fiedler's bound $\lambda_2\le\kappa_v(G)\le d_{\min}$ is a statement about unweighted graphs. Parts (i)-(iv) are fine for weights. | Replace (v) by: "if all weights are $1$ and $G$ is not complete, then $\lambda_2 \le d_{\min}$; the complete graph $K_n$ has $\lambda_2 = n$." (and keep the Fiedler citation in the proof, which is already restricted to that case) |
| 2 | ch18-kalman-filter.tex:748, :795, :839 | `thm:ch18-optimal`, `thm:ch18-best-gain`, `thm:ch18-steady` | imprecise | All three use $\Kgain=\mat{P}^-\mat{H}\T\mat{S}\inv$ with $\mat{S}=\mat{H}\mat{P}^-\mat{H}\T+\mat{R}$, i.e. they need $\mat{S}$ invertible, but `def:ch18-model` (line 145) puts **no** condition on $\mat{R}$ (or $\mat{P}_0$). The appendix corollary they rest on, `thm:appB-linear-update`, does require $\mat{P}\succ\mat{0}$ and $\mat{R}\succ\mat{0}$, and the proof of `thm:ch18-best-gain` silently invokes "$\mat{S}\succ\mat{0}$ when $\mat{R}\succ\mat{0}$". The DARE convergence theorem quoted in `thm:ch18-steady` also needs $\mat{R}\succ\mat{0}$ next to observability and $\mat{Q}\succ\mat{0}$. | In `def:ch18-model` add after the noise covariances: "with $\mat{R}\succ\mat{0}$, so that the innovation covariance $\mat{S}_k=\mat{H}\mat{P}^-_k\mat{H}\T+\mat{R}$ is invertible at every step"; in `thm:ch18-steady` state the hypotheses as "$(\mat{F},\mat{H})$ observable, $\mat{Q}\succ\mat{0}$ and $\mat{R}\succ\mat{0}$". |
| 3 | ch23-consensus-formation.tex:842 | `prop:ch23-leader`, proof | minor | The quadratic form is written $\vect{x}\T\mat{M}\vect{x}=\sum_{\{i,j\}\in E}(x_i-x_j)^2+k_l\sum_i x_i^2$, dropping the weights that `prop:ch23-laplacian`(ii) carries. Harmless for the unweighted radius graph, inconsistent with the stated generality. | `\sum_{\set{i,j}\in E} w_{ij}(x_i-x_j)^2 + k_l\sum_{i:\,b_i=1} x_i^2` (the conclusion $\mat{M}\succ\mat{0}$ is unaffected, since $w_{ij}>0$) |
| 4 | ch23-consensus-formation.tex:891 | `thm:ch23-formation`, sandwich `eq:ch23-sandwich` | minor | The step $\sum_{\{i,j\}\in E}(y_i-y_j)^2=\vect{\delta}\T\mat{L}\vect{\delta}$ and the edge error $e_F$ built from it hold only with unit weights; with weights the identity carries a $w_{ij}$ and the sandwich constants change. | Add "with unit weights on the formation graph" to the hypothesis of `thm:ch23-formation`, or write the sum as $\sum w_{ij}(\cdot)^2$ in the proof and in the definition of $e_F$. |
| 5 | ch09-cbs.tex:535-537 | `thm:ch09-split`, proof | minor | "If $c=\langle a_i,a_j,u,v,t\rangle$ is an edge conflict, the children forbid $a_i$ to move $u\to v$ and $a_j$ to move $v\to u$ ... because that is an edge conflict" reads as false against `def:ch07-conflicts`(b) (same-direction traversal); it is correct only under the local renaming announced in ch09:149-154 (CBS's "edge conflict" = ch07's swapping conflict). The lemma is 380 lines after that renaming. | "...forbid $a_i$ to move $u\to v$ and $a_j$ to move $v\to u$ at time $t$. A solution cannot make both moves, because together they are a swapping conflict (the \emph{edge conflict} of \cref{sec:ch09-conflicts})." |
| 6 | ch14-dwa.tex:799 (last sentence) | `thm:ch14-incomplete` | minor | "With $(\alpha,\beta,\gamma)=(0.2,0.6,0.2)$ and the parameters of `tab:ch14-parameters` the pocket may be $1.65$ m in radius": the weight triple is a *permutation* of the table's own default $(0.6,0.2,0.2)$, and with the table's weights the construction is vacuous ($\beta<\alpha$ makes the radius negative). The number itself is right: $d_{\max}\bigl(1-(\alpha+\gamma v_1/v_{\max})/\beta\bigr)=3(1-0.4512)=1.65$ m with $v_1=\sqrt2 a_{\max}\dt=0.707$. | "With the clearance-dominated weights $(\alpha,\beta,\gamma)=(0.2,0.6,0.2)$ — not the defaults of \cref{tab:ch14-parameters} — and the remaining parameters of \cref{tab:ch14-parameters}, the pocket may be $1.65$ m in radius." |

Checked: 144 statements, 8 tables; errors: 1, imprecise: 1, minor: 4.

## What was verified positively (so the above is a short list on purpose)

Spot-checks that came out **correct**, including every numeric constant found in a
statement or table:

* Named results with their hypotheses: A\* optimality with an admissible $\hcost$ and
  re-opening (`thm:ch04-optimal`; `eq:ch04-admissible` does include $0\le\hcost$, so
  $\hcost(\gamma)=0$ as the proof needs), consistency $\Rightarrow$ one expansion per
  node and non-decreasing $\fcost$ (`thm:ch04-consistent`), $w\,C^*$ for weighted A\*
  and for focal search (`thm:ch04-weighted`, `thm:ch10-focal` with
  $\Focal=\{f\le w f_{\min}\}$), Dijkstra with $c\ge0$ and the *single* use of
  non-negativity flagged in step (iii) (`thm:ch03-invariant`), CBS optimality and
  completeness on solvable instances, ECBS $\mathrm{LB}\le C^*$, ORCA's reciprocal
  guarantee (the sign bookkeeping of `thm:ch13-pairwise` and the convexity of
  $\VO^\ttc$ both check out), RRT probabilistic completeness (the $\nu=\min(\eta/3,
  \delta_c/4,r_{\mathrm{goal}})$ bookkeeping is tight), RRT\* asymptotic optimality
  with $\gamma^*_{\rrtstar}=2(1+1/d)^{1/d}(\mu(\Xfree)/\zeta_d)^{1/d}$ (matches
  Karaman-Frazzoli; the worked values $12.05$, $13.66$, $12.2$, $15.0$ and the OMPL
  comparison $1.73\sqrt{\mu/\pi}$ vs $2.45\sqrt{\mu/\pi}$, "about 30 % below", all
  reproduce), Kalman MMSE/BLUE algebra (`eq:ch18-best-gain` expands correctly),
  average consensus and its $e^{-\lambda_2 t}$ rate, $h<2/\lambda_n$ and
  $h<1/d_{\max}$, big-M exactness, branch-and-bound correctness and Jeroslow's
  $2^{(n-1)/2}$, MPC recursive feasibility with the two terminal ingredients,
  exact-penalty KKT with $w_1\ge\max_k\lambda^*_k$.
* Complexity claims: Dijkstra $\bigO{(\abs{V}+\abs{E})\log\abs{V}}$ with lazy deletion
  and $\le\abs{E}+1$ pushes/pops (plus the Fibonacci-heap and dense-graph remarks,
  and Bellman-Ford $\bigO{\abs{V}\abs{E}}$), conflict detection $\bigO{k^2T}$ /
  $\bigO{kT}$ expected, prioritized planning $\bigO{b\abs{V}T_{\max}\log(\abs{V}
  T_{\max})}$, ORCA LP $\bigO{m^2}$ worst case and $\bigO{m}$ expected with the
  backward-analysis $2/i$ argument, D\* Lite "at most two expansions per vertex",
  attention $\Theta(nd^2)+\Theta(n^2d)$ and $\Theta(N^2T^2d+NTd^2)$, systematic
  resampling $\bigO{N}$ with $\E[N_i]=N\omega^{(i)}$.
* Numbers: covariance-ellipse masses $39.3/86.5/98.9\,\%$; the 8-connected grid
  detour $\sqrt{4-2\sqrt2}=1.082$ ("up to 8 %"); CV noise amplification
  $1.25/0.65/0.23$ m; the rule of three ($-\ln 0.05=2.996$); the DWA numbers
  $1.56$/$1.14$ m/s at $0.608$ m and the discrete braking distance $1.25$ m;
  the ch08 counterexample costs $6+5=11$ and $8+7=15$ (both plans replayed by hand,
  no vertex/swap conflict); the coordinated-turn Jacobian, entry by entry,
  including the $\omega\to0$ limits; the $\ell/\sqrt2$ separation bound of
  `thm:ch24-separation` and the configuration that attains it; the ECBS/CBS
  constraint-counting bound $\Delta=k(\abs{V}+2\abs{E})(C^*+2)$.
* `tab:ch25-paired`: all sixteen exact **sign-test** $p$-values are consistent with
  the reported smaller/larger/equal counts (e.g. 5/9/6 gives $2\Prob(X\ge9\mid n{=}14)
  =0.424$; 0/7/13 gives $2/2^7=0.016$; 17/3/0 gives $0.003$), and all sixteen
  $d_z$ values are consistent with the reported mean and 95 % $t$ interval at
  $N=20$ ($d_z = \bar D/\mathrm{sd}$, half-width $=2.093\,\mathrm{sd}/\sqrt{20}$).
  The Wilcoxon $p$-values were not recomputed.
* Sign conventions that could easily have been wrong but are internally consistent:
  $\pos_{\mathrm{rel}}=\pos_B-\pos_A$, $\vel_{\mathrm{rel}}=\vel_A-\vel_B$ and
  $D(t)=\norm{\pos_{\mathrm{rel}}-t\vel_{\mathrm{rel}}}$ (hence $t^*=+\pos\cdot\vel/
  \norm{\vel}^2$); $\Delta/4$ as defined in `eq:ch12-quadratic`; the ORCA leg
  directions and outward normals of `thm:ch13-cases` (they agree with the RVO2
  formulas, and $\vect{n}=(-d_{L,y},d_{L,x})$ / $(d_{R,y},-d_{R,x})$ are indeed the
  outward normals); the ch04/ch10 horizons $H+1+D$ and $\lfloor w(H+1+D)\rfloor$
  (the ch04 $D$ is defined on the grid with parked cells as walls, which is what the
  proof needs, and ECBS has no parked cells, so its $D=\max_v\hcost(v)$ is right).

## Ten items a human should still verify

1. `prop:ch23-laplacian`(v) — finding 1 above; decide whether the chapter's Laplacian
   is weighted or not, and make (ii), (v), `prop:ch23-leader` and `thm:ch23-formation`
   agree on that.
2. `thm:ch18-optimal` / `thm:ch18-steady` — finding 2; where to put $\mat{R}\succ\mat0$
   (definition vs. each theorem), and whether $\mat{P}_0\succeq\mat0$ suffices for the
   induction as stated.
3. `thm:ch11-optimal`, Step 3 (M\*) — the only proof in the book whose termination
   argument I could not close by reading alone: "the set $A$ is replaced by a strictly
   smaller one at most $k$ times and otherwise the first conflict comes one step
   closer" deserves a careful re-reading against Wagner-Choset.
4. `thm:ch05-correct` and `thm:ch05-expansions` (D\* Lite) — proof sketches; in
   particular invariant (ii) (stored key $\le$ current key via $k_m$) and the claim
   that the first call reproduces A\* on the reversed graph *with the stated
   tie-breaking*.
5. `thm:ch13-cases` — the arc/leg case split, the $\dt$-based overlap fallback, and
   the exercise reference for "the foot of the perpendicular lies beyond the tangent
   point"; best checked against `code/ch13_*.py` rather than by hand.
6. `thm:ch13-incomplete` — the geometric claims imported from exercises (the corridor
   factor $0.75$, and that "backing into the bay is further from $\vel^{\mathrm{pref}}$
   than slowing down"); the $d_{k+1}=d_k(1-\dt/\ttc)$ recursion itself checks out.
7. `thm:ch08-incomplete` / `thm:ch08-suboptimal` — the "brute force confirms 11/15 is
   optimal" claims depend on `code/ch08_prioritized.py`; I verified the exhibited
   plans are valid and have those costs, not that no cheaper plan exists.
8. `thm:ch07-feasible` — the MAPF $\leftrightarrow$ pebble-motion equivalence
   (serialization of a parallel step, rotation on a fully occupied cycle) and the
   $\bigO{\abs{V}^3}$ move bound as attributed to Kornhauser et al.
9. `thm:ch14-incomplete` — finding 6; also whether $v_1=\sqrt{\dim}\,a_{\max}\dt$ is
   the intended largest window speed in 3D ($\dim=3$ changes $1.65$ m).
10. `tab:ch25-paired` — the Wilcoxon signed-rank $p$-values (only the sign-test ones
    and the $d_z$/CI consistency were recomputed here), and the reading direction of
    $\rho_L$: the caption says "smaller is better" for it, so the positive
    hybrid-minus-local-only differences say the hybrid is *worse* on that metric,
    which should be what the surrounding text claims.
