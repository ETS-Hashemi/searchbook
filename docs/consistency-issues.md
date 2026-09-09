# Cross-chapter notation inconsistencies (input to Phase 6.2)

Found by the notation-table author (2026-09-09) after Chapters 1-5, 7-14, 19-22 were written.
Decisions marked DECIDED are to be applied by the consistency-fix agent; the others need a
judgement at fix time.

## Same thing, different symbol
1. Goal vertex: ch02/ch07/ch08 use g / g_i; ch04, ch09, ch10, ch11 use gamma / gamma_i; ch03 uses t;
   ch05 uses s_start, s_goal. DECIDED: start s (s_i), goal gamma (gamma_i) everywhere; ch05 may keep
   s_start/s_goal inside the D* Lite pseudocode because it mirrors the original paper, with one
   sentence saying so. Fix ch02, ch03, ch07, ch08.
2. Shortest-path distance: \dist(u,v) in ch02/ch05/ch07 vs delta(s,v) in ch03 (44 occurrences).
   DECIDED: \dist everywhere; ch03 may mention that CLRS writes delta.
3. Arrival time: ch02 writes T(pi); ch07 writes \cost(pi_i) and uses T_i for the last stored index.
   DECIDED: \cost(pi) = arrival time (stay-at-target), T = plan/planning horizon; fix ch02.
4. Free space: ch02 defines \Cfree/\Cobs; ch16 uses \Xfree/\Xobs and plain x for states.
   DECIDED: keep both with the meaning C = configuration space (Parts I-IV), X = state space of
   sampling-based planning (Part V), stated in the notation table; ch16 should use bold \state.

## Same symbol, different thing
5. Q, R: noise covariances (Part VI) vs cost weights (Part VII); ch20 also uses Q/K/V for attention.
   Handled by the notation-table note and ch21's warning; add one sentence in ch20.
6. tau: ch01 uses tau for time-to-collision and tau_safe for the horizon; ch02/ch12/ch13 use t_c for
   time-to-collision and tau for the horizon; ch07 uses tau as a dummy time variable; ch16 for a path.
   DECIDED: t_c = time to collision, tau = horizon (ORCA/safety); fix ch01; rename the dummy in ch07
   and the path in ch16 (use sigma or pi).
7. w: suboptimality factor (ch04, ch10), edge weight (ch03), particle weight and process noise in the
   same equation (ch19 eq. around line 834), ADMM auxiliary (ch21), ORCA case analysis (ch13).
   DECIDED: fix the ch19 clash (process noise \vect{w}_k vs particle weights w^{(i)} -> use
   \omega^{(i)} for particle weights); others are local and documented.
8. eps: ARA* inflation (ch05/ch06), A*_eps (ch10), tolerance (ch13, ch21, ch22), Gaussian noise
   (ch20), consensus step size (ch23). DECIDED: ch23 step size -> use h or alpha_c, since ch23 also
   uses L and lambda; the rest stay (documented).
9. P: estimate covariance (ch19), terminal weight (ch21), iteration matrix (ch23 solutions), LP
   polyhedron (ch22). Local; add a note in ch21 (P_f for the terminal weight preferred).
10. H (measurement matrix vs QP Hessian), S (innovation covariance vs prediction matrices), L
    (Cholesky factor vs Laplacian), A/B (plant vs adjacency/pinning). Local; ch23 should write the
    adjacency matrix as \mat{W} or \mathcal{A} to avoid the plant matrix A of ch02/ch21.
11. u: control input (ch02, ch21), ORCA velocity change (ch13), QP upper bound in alg:ch21-admm.
    DECIDED: fix the ch21-internal clash (upper bound -> \bar{\vect{z}} or u_max).
12. T: planning horizon (ch02), plan horizon (ch07), RRT tree (ch16). DECIDED: tree -> \mathcal{T}.
13. d_ij: scalar separation (ch02) vs bold formation offset (ch21, ch23). Acceptable (bold vs scalar);
    mention in the notation table (done).
14. alpha/beta/gamma (DWA weights, UKF parameters, ADMM), sigma (priority permutation, DWA smoothing,
    std. dev., ADMM), N (CT node, particle count, MPC horizon), \mathcal{C} (C-space vs constraint
    set), L (path length vs Laplacian). Local; document in chapter openings where two meet.

## Minor
- ch12 line ~455 writes \epsilon where the book macro is \eps.
