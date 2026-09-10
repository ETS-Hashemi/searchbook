# Coverage audit: `docs/core-idea.txt` (training plan) vs. the book

**Audited:** `Overleaf/chapters/ch01`–`ch25`, `Overleaf/appendices/appA-study-plan.tex`,
`Overleaf/appendices/appC-solutions.tex` + `appendices/solutions/*`, `Overleaf/code/*.py`.
**Section, table, figure, algorithm and exercise numbers** are the real numbers from the full
build (`Overleaf/build-full/**/*.aux`), not guesses.
**Read-only audit:** no file other than this one was modified.

A note on counts before the tables. The plan has **six algorithm groups (A–F) with 27
algorithm rows**, a **twelve-week schedule**, a **four-layer capstone with five decision
steps**, **five experiment factors** and **ten metrics**, and a **ten-item completion
checklist** — all as briefed. Section 5 of the plan, however, lists **seven** research
directions, not six; `ch01` §1.5 says so explicitly ("The plan names seven such
directions"), and §4 of this report covers all seven.

---

## 1. The 27 algorithms

| # | Algorithm | Plan priority | Chapter / section | Covered |
|---|---|---|---|---|
| **A** | *Single-agent graph search — learn deeply* | | | |
| A1 | Dijkstra | High | Ch. 3: §3.4 (Alg. 3.1), §3.5 worked example, §3.6 properties, §3.7 variants (§3.7.2 backward/true-distance, Alg. 3.2) | fully |
| A2 | A\* | Essential | Ch. 4: §4.4 (Alg. 4.1), §4.5, §4.6.1–4.6.4 optimality/consistency, §4.7 variants, **§4.8 space-time A\*** (Alg. 4.2) | fully |
| A3 | D\* Lite | Essential | Ch. 5: §5.6 (§5.6.1 reversal, §5.6.2 $k_m$, §5.6.3 Alg. 5.2), §5.7 worked example, §5.8 properties, §5.8.1 experiment (Fig. 5.5) | fully |
| A4 | Lifelong Planning A\* (LPA\*) | Medium | Ch. 5: §5.4 (Alg. 5.1), §5.5 worked example (Tab. 5.1–5.2) | fully |
| A5 | Anytime Repairing A\* (ARA\*) | Medium | Ch. 6: §6.4 (Alg. 6.1–6.2), §6.5, §6.6 bounds, §6.7 $\varepsilon$-schedule + §6.7.1 experiment, §6.8.1 Anytime D\* | fully |
| **B** | *Multi-agent path finding — learn deeply* | | | |
| B1 | Prioritized Planning | High | Ch. 8: §8.4 (Alg. 8.1–8.2), §8.5, §8.6 incompleteness/well-formedness, §8.7 (HCA\*, WHCA\* Alg. 8.3, ordering, PBS) | fully |
| B2 | Conflict-Based Search (CBS) | Essential | Ch. 9: §9.4 (Alg. 9.1–9.2), §9.5 (Tab. 9.1), §9.6 optimality, §9.7 cardinal/bypass/MA-CBS/symmetry + §9.7.6 experiment | fully |
| B3 | Enhanced CBS (ECBS) | Essential | Ch. 10: §10.4 (Alg. 10.1–10.2), §10.5, §10.6 $w$-suboptimality, §10.7.3 benchmark (Tab. 10.5), §10.7.4 EECBS | fully |
| B4 | M\* | Medium | Ch. 11: §11.4.2 (Alg. 11.2) + §11.4.1 OD/ID (Alg. 11.1), §11.5 worked example, §11.6 (Thms. 11.9–11.11) | fully |
| B5 | Push-and-Swap / Push-and-Rotate | Awareness | Ch. 11 §11.7: §11.7.2 primitives (Fig. 11.6), §11.7.3 Push-and-Swap (Alg. 11.3) + Push-and-Rotate completeness (Thm. 11.12), §11.7.4 quality | **partially** — Push-and-Swap has pseudocode *and* a reference implementation (`push_and_swap()` in `code/ch11_mstar.py`); Push-and-Rotate has neither: the `Rotate` primitive is prose + Fig. 11.6(c) only, and `code/ch11_mstar.py` contains no `rotate`. Adequate for "Awareness", short of it for a reader who wants to run it. |
| **C** | *Local/reactive collision avoidance — learn deeply* | | | |
| C1 | Velocity Obstacles (VO) | Essential | Ch. 12: §12.3.2 cone, §12.3.3 Def. 12.4 VO, §12.3.4 TTC, §12.3.5 truncated VO, §12.4 (Alg. 12.1–12.3), §12.5, §12.6, §12.7 oscillation + §12.7.2 experiment (Tab. 12.2, Fig. 12.7), §12.9 3D | fully |
| C2 | Reciprocal Velocity Obstacles (RVO) | High | Ch. 13: §13.3.2 the dance, §13.3.3 RVO (Thm. 13.4, the apex), and RVO as a row of Tab. 13.2 | fully |
| C3 | ORCA | Essential | Ch. 13: §13.4 construction (Alg. 13.1), §13.4.1 non-cooperative share, §13.4.2 3D, §13.5 LP (Alg. 13.2–13.3), §13.6–13.7 examples, §13.8 guarantees | fully |
| C4 | Dynamic Window Approach (DWA) | High | Ch. 14: §14.3 (velocity space, three restrictions, objective), §14.4 (Alg. 14.1–14.2), §14.5, §14.6, §14.7 tuning | fully |
| C5 | Artificial Potential Fields (APF) | High | Ch. 15: §15.3–15.4 (Alg. 15.1–15.2), §15.5, §15.6, §15.7 failure modes (§15.7.1–15.7.5), §15.8 remedies + §15.8.1 basin experiment, §15.9 swarms | fully |
| **D** | *Sampling-based motion planning — know well* | | | |
| D1 | RRT | High | Ch. 16: §16.3.2 primitives, §16.4 (Alg. 16.1), §16.5, §16.6 completeness, §16.7 (RRT-Connect Alg. 16.2, kinodynamic Alg. 16.3, shortcut Alg. 16.4, 3D), §16.9 grid-vs-sampling | fully |
| D2 | RRT\* | High | Ch. 17: §17.4 (Alg. 17.1–17.2, radius, $k$-nearest, hand iteration), §17.5, §17.6 asymptotic optimality | fully |
| D3 | Informed RRT\* | Medium | Ch. 17 §17.7: §17.7.1 informed set, §17.7.2 ellipsoid sampling (Alg. 17.3), §17.7.3 what it buys (Fig. 17.7) | fully |
| **E** | *Prediction and tracking — know well* | | | |
| E1 | Kalman Filter | Essential | Ch. 18: §18.3–18.4 (Alg. 18.1–18.2), §18.5, §18.6, §18.7 tuning/gating, §18.8 uncertainty propagation, §18.9 experiment (Fig. 18.8) | fully |
| E2 | Extended Kalman Filter (EKF) | High | Ch. 19 §19.4 (Alg. 19.1), §19.4.2 Jacobians, §19.4.3 worked step, §19.4.4 failure | fully |
| E3 | Unscented Kalman Filter (UKF) | Medium | Ch. 19 §19.5 (Alg. 19.2), §19.5.1 unscented transform, §19.5.3–19.5.4 (Tab. 19.2–19.3) | fully |
| E4 | Particle Filter | Medium | Ch. 19 §19.6 (Alg. 19.3–19.4), §19.6.2 ESS/resampling, §19.6.4 occlusion example | fully |
| E5 | LSTM trajectory prediction | Essential *(for the planned research)* | Ch. 20 §20.5 (§20.5.1 cell, §20.5.2 seq2seq Alg. 20.2, §20.5.3 Social LSTM), Alg. 20.3 training, §20.8 worked example (Tab. 20.2–20.3), code `ch20_prediction.py` (+ `_torch`) | fully |
| E6 | Transformer trajectory prediction | Awareness **to High** | Ch. 20 §20.6 (Def. 20.5 attention, Eqs. 20.15–20.17, Fig. 20.6), Tab. 20.4 method comparison; exercises 20.5, 20.6; `scaled_dot_product_attention` / `multi_head_attention` / `toy_agent_attention` in `code/ch20_prediction.py` | **partially** — covered at the "Awareness" end only. There is no transformer *predictor* (no algorithm block matching Alg. 20.2, no end-to-end model, no row in the empirical comparison Tab. 20.2/20.3, no coding exercise). The plan's "to High" end is not reachable from the book alone. |
| **F** | *Optimization and control — learn enough to integrate* | | | |
| F1 | Model Predictive Control (MPC) | Essential | Ch. 21: §21.3 (model, OCP, §21.3.3 swarm constraints), §21.4 (condensed QP, solver Alg. 21.1, loop Alg. 21.2), §21.5, §21.6 stability/feasibility, §21.7.1–21.7.3 tuning/chance constraints/experiment | fully |
| F2 | Mixed-Integer Linear Programming (MILP) | Medium | Ch. 22: §22.3 LP/integer, §22.4 big-$M$/separation/full problem, §22.5 branch-and-bound (Alg. 22.1), §22.6, §22.7, §22.8.1 MAPF as an ILP, §22.9 cost of exactness | fully |
| F3 | Consensus / formation control | Essential *(for formation-preserving work)* | Ch. 23: §23.3 (Laplacian, Def. 23.6 formation error Eq. 23.4), §23.4 (Alg. 23.1–23.2), §23.5, §23.6 convergence, §23.7.1 rigidity, §23.7.2 flocking, §23.7.3 communication range; MPC form in Ch. 21 §21.3.3 | fully |

**Score: 25 of 27 rows fully covered; 2 partially** (B5 Push-and-Rotate, E6 Transformer) — both
at priorities ("Awareness", "Awareness to High") where the shortfall is defensible but should be
stated, since Appendix A's traceability table (Tab. A.5) shows both as plain chapter hits with no
depth caveat.

---

## 2. The twelve weeks

For every week: the plan's *Learn* bullets → where taught; the plan's *Coding exercise* → the
exercise that is it; the *Milestone* → where the reader can check the claim against a printed
number, figure or theorem. Appendix A's own per-week "Done when" paragraph (§A.4.1–A.4.12) is a
second, always-present verification anchor and is listed once per row as "A.4.$n$".

| Wk | Learn → where | Coding exercise → label (number) | Milestone → verify at |
|---|---|---|---|
| 1 | Graph search → §3.4, §4.4; admissible/consistent heuristics → §4.3.2, §4.6.2–4.6.3; space-time representation → §2.3 (Defs. 2.10–2.12), §4.8 | `exr:ch04-coding` (**Ex. 4.8**) — "the Week 1 coding exercise"; first half `exr:ch03-coding` (**Ex. 3.7**) | §4.6.1–4.6.4 (optimality theorem + "what goes wrong without the conditions"); A.4.1 "Done when"; self-check Q1 (§A.6) |
| 2 | Incremental search → §5.3–5.4; what changes when obstacles appear after planning → §5.6, §5.7, §5.8 | `exr:ch05-coding` (**Ex. 5.7**); optional `exr:ch06-coding` (**Ex. 6.6**) | §5.8.1 experiment, Fig. 5.5 (expansions/time vs. fresh A\*); Ex. 5.7(a) cost-equality test; A.4.2; self-check Q2 |
| 3 | Vertex/edge/swap conflicts → §7.3.2 (Def. 7.4); time-indexed paths → §7.3.1, §2.3; sum-of-costs & makespan → §7.3.3 (Defs. 2.17–2.18) | `exr:ch08-coding` (**Ex. 8.8**) — the full planner; **also** `exr:ch07-prioritized` (**Ex. 7.9**), which claims the same slot (see §6b, inconsistency I-3); detector in `exr:ch07-coding` (**Ex. 7.8**) | §7.4 (Alg. 7.1–7.2 + walkthrough); Ex. 7.4 planted-conflict cases; §8.6, Fig. 8.6 (orders that fail vs. succeed); A.4.3; self-check Q3 |
| 4 | Constraint tree → §9.3, §9.4; high level → §9.4.1; low-level A\* → §9.4.2; branching on conflicts → §9.4, §9.6 | `exr:ch09-coding` (**Ex. 9.9**); optional extension `exr:ch09-icbs-coding` (Ex. 9.10) | §9.5 worked example (Tab. 9.1 CT trace) to match your log against; §9.6 optimality; Ex. 9.2 hand-drawn CT; A.4.4; self-check Q4 |
| 5 | Bounded suboptimality → §10.3, §10.6.3; focal search → §10.4.1–10.4.3; performance/optimality trade-off → §10.7.1, §10.7.3 | `exr:ch10-coding` (**Ex. 10.7**) | §10.7.3 benchmark, Tab. 10.5 / Fig. 10.5 (cost vs. runtime as $w$ varies); Ex. 10.7(c); A.4.5; self-check Q5 |
| 6 | Collision cones → §12.3.2; relative velocity → §12.3.1, §13.3.1; reciprocal avoidance → §13.3.3 (RVO), §13.4 (ORCA) | `exr:ch13-coding` (**Ex. 13.9**) — the three-way comparison; first half `exr:ch12-coding` (**Ex. 12.7**) | **Tab. 13.2** (none / VO / RVO / ORCA on the circle: colliding pairs, $d_{\min}$, arrival, reversals) and Fig. 13.6; Tab. 12.2 / Fig. 12.7 for none-vs-VO; A.4.6; self-check Q6 |
| 7 | Short-horizon control → §14.3, §14.4; local minima → §15.7.1; oscillation → §12.7, §15.7.3, §14.7; robot dynamics → §14.3.2, §2.6 | `exr:ch14-coding` (**Ex. 14.8**) **or** `exr:ch15-coding` (**Ex. 15.9**) — the plan says "DWA or APF" | §14.6.2 "DWA is a local method" (Fig. 14.5 U-trap), §15.7.1–15.7.5 failure modes, §15.8.1 basin experiment (Fig. 15.8), Tab. 14.5 tuning table; A.4.7 |
| 8 | Sampling/steering/collision checks → §16.3.2, §16.8.1; path quality in continuous space → §16.6.2, §17.6.2, §17.7 | `exr:ch16-coding` (**Ex. 16.8**) and `exr:ch17-coding` (**Ex. 17.7**) — both self-describe as "the Week 8 coding exercise" (see I-4) | §16.9 "Grid search or sampling?" (Tab. 16.5), Tab. 17.2 convergence, Tab. 17.3 RRT\*/A\* comparison, Fig. 17.7; A.4.8 |
| 9 | Kalman/EKF tracking → §18.4, §19.4; state estimation → §18.3–18.5; uncertainty → §18.6, §18.7, §18.8 | `exr:ch18-coding` (**Ex. 18.8**); `exr:ch19-coding` (**Ex. 19.8**) if the intruder turns | §18.9 experiment (Fig. 18.8: filtered vs. raw RMSE; Tab. 18.2 tuning), §19.5.4 / Tab. 19.2 RMSE across EKF/UKF/PF; A.4.9; self-check Q7 (first half) |
| 10 | Constant-velocity baselines → §20.4 (Alg. 20.1); LSTM prediction → §20.5; horizon and uncertainty → §20.3 (Def. 20.2 ADE/FDE, Eq. 20.1), §20.7 | `exr:ch20-coding` (**Ex. 20.9**) | §20.8 worked example: **Tab. 20.2** (per-method ADE/FDE) and **Tab. 20.3** (per-horizon + calibration), Fig. 20.9; §20.9 "when the baseline is optimal"; A.4.10; self-check Q7 (second half) |
| 11 | Receding-horizon optimization → §21.3.2, §21.4; hard/soft constraints → §21.3.3, §21.6.2; formation error → §23.3 (Def. 23.6, Eq. 23.4); communication radius → §23.7.3, §21.3.3 | `exr:ch21-coding` (**Ex. 21.9**) and `exr:ch23-coding` (**Ex. 23.8**); `exr:ch22-coding` (Ex. 22.8) optional | §21.7.3 hard-vs-soft experiment (Tab. 21.4, Fig. 21.6: violations and slack logged), §23.6.4 + Tab. 23.3 (formation error vs. the exponential bound), §23.7.3 connectivity; A.4.11 |
| 12 | Global MAPF + reactive avoidance + prediction + replanning → Ch. 24 §§24.3–24.9; experiments → Ch. 25 §§25.3–25.6 | `exr:ch24-coding` (**Ex. 24.8**) and `exr:ch25-coding` (**Ex. 25.7**) | §24.10 worked scenario (Ex. 24.4, Tab. 24.4 executive trace, Figs. 24.4–24.6), §25.7 mini-study (Ex. 25.10, Tab. 25.4 results + Tab. 25.5 paired tests), §25.8 reproducibility checklist (Tab. 25.7); A.4.12; self-check Q8 |

Every week's *Learn* bullet has a home, and every week has a real, labelled coding exercise. The
only structural slippage is *whose* exercise a week is: see inconsistencies I-3 and I-4.

---

## 3. Capstone

### 3.1 The five decision-logic steps → Ch. 24

| Step (plan wording) | Where in Ch. 24 |
|---|---|
| 1. Follow the nominal CBS/ECBS path while no predicted conflict is inside the safety horizon | §24.4 state **Nominal** (Fig. 24.2 state machine, Tab. 24.2 transitions), Alg. 24.1 line 22 (`alg:ch24-loop:nominal`); the trigger itself is §24.5: **Def. 24.2** ("predicted conflict inside the safety horizon"), **Alg. 24.2** (`InsideHorizon`), Fig. 24.3; nominal path from Layer 1 (Tab. 24.1) and Prop. **24.5**/**24.6** |
| 2. If an unknown moving object creates a near-term risk, invoke ORCA/DWA for a local action | §24.4 state **Avoiding**, Alg. 24.1 lines 4 and 15 (`:enter`, `:avoid`); the layer itself is Tab. 24.1 row 3 → Ch. 13 §13.4/§13.5 (ORCA) or Ch. 14 §14.4 (DWA); guarantee Prop. **24.7**; DWA substitution worked in Ex. 24.7 |
| 3. After the conflict clears, reconnect to the nominal path at a safe future waypoint | **§24.6** "Reconnecting to the nominal path": **Def. 24.3** (admissible reconnection), **Alg. 24.3** (`Reconnect` + `SegmentFree`), hysteresis parameter $n_{\text{clear}}$ (Tab. 24.3); transition row Avoiding→Reconnecting in Tab. 24.2 |
| 4. If reconnection is impossible, too costly, or violates formation/communication constraints, run D\* Lite/A\* from the current state | **§24.7** "Replanning and the conflict re-check", paragraphs "The replanning trigger" and "What the replanner searches"; **Alg. 24.4** lines 2–8 (`:start`, `:res`, `:layers`, `:search`, `:install`); the constraint half of the trigger is §24.8 paragraph "In the replanning trigger and the re-check" (Eq. 24.6 formation, Eq. 24.7 communication); bounds $d_{\max}$, $t_{\text{avoid}}$, $T_{\text{replan}}$ in Tab. 24.3 |
| 5. Re-check inter-agent conflicts after any significant replan | §24.7 paragraph "Why a re-check is needed"; **Alg. 24.4** lines 9–13 (`:detect` via the Ch. 7 detector, `:cbs` local CBS, `:escalate`); **Fig. 24.6** draws the re-check of the worked run; guarantee Prop. **24.8**; also fires on a delayed reconnection, Alg. 24.1 line 14 (`:shift`) |

The five steps are also previewed in Ch. 1 §1.3.2 and restated in Appendix A §A.5.2 with Fig. A.4.
Cross-cutting support: shared world model **Def. 24.1** (§24.3), uncertainty→radius §24.9
(Eqs. 24.8–24.9), surviving guarantees §24.11 (Tab. 24.5), implementation §24.12 (Lst. 24.1 rates,
Lst. 24.2 executive), reference code `code/ch24_hybrid.py`.

### 3.2 The five experiment factors → Ch. 25

| Plan factor / levels | Where defined |
|---|---|
| Controlled drones: 2, 4, 8, more | §25.4.1, **Tab. 25.2** row 1 (base level **4**); scaling evidence Ch. 9 §9.7.6 / Fig. 9.6 and Ch. 10 §10.7.3; runner `run_study(cells,…)` in `code/ch25_evaluation.py` |
| Unknown external drones: 0, 1, 2, multiple crossing | §25.4.1, Tab. 25.2 row 2; trajectory families in §25.5.3 ("Intruder trajectory families and difficulty", Fig. 25.2: straight / turning / evasive) |
| Prediction quality: perfect, noisy, constant-velocity, learned | §25.4.1, Tab. 25.2 row 3 (starred, "deserves a small full factorial"); the four levels are implemented in `predict_intruders(..., prediction=...)` in `code/ch25_evaluation.py` — but see gap **G-1** for the "learned" level |
| Avoidance strategy: local-only, replan-only, hybrid | §25.4.1 Tab. 25.2 row 4 and **§25.4.2 Tab. 25.3 baselines** (plus a "no avoidance" sanity baseline and a MILP oracle); the switch is Ch. 24 §24.4 with Fig. A.4's two dashed cuts |
| Constraints: no formation vs. formation-preserving; no comm. radius vs. bounded range | §25.4.1 Tab. 25.2 row 5; enforcement in Ch. 21 §21.3.3 / Ch. 23 §23.7.3; *during avoidance* in Ch. 24 §24.8 (Eqs. 24.6–24.7) — but see gap **G-2** |

Design method: full factorial vs. one-factor-at-a-time and the interaction pair, §25.4.1;
paired design §25.5.4; statistics §25.6; worked instance §25.7 (Ex. 25.10).

### 3.3 The ten metrics → Ch. 25 §25.3 (and Ch. 23 for formation error)

| Metric | Definition | In the summary table | Reported in the mini-study |
|---|---|---|---|
| Collision rate | **Def. 25.2**, Eq. 25.1 ($\hat p_{\text{coll}}$, Wilson interval) | Tab. 25.1 row 1 | Tab. 25.4 col. 3 |
| Minimum separation | Def. 25.2, Eq. 25.2 ($d_{\min}$, split dd/di, near-miss rate); segment-based minimum from Ch. 2 §2.7 (Def. 2.19, Def. 2.30) | Tab. 25.1 row 2 | Tab. 25.4 col. 4; Tab. 25.5 |
| Path length | **Def. 25.3** ($L_i$, ratio $\rho_i$, $\rho_L$) | Tab. 25.1 row 3 | Tab. 25.4 col. 5 |
| Travel time | Def. 25.3, Eq. 25.3 ($T_i$, tolerance $\varepsilon_g$); Ch. 2 Def. 2.16 | Tab. 25.1 row 4 | via makespan / sum of costs |
| Makespan | Def. 25.3, Eq. 25.4; Ch. 7 §7.3.3, Ch. 2 Def. 2.17 | Tab. 25.1 row 5 | Tab. 25.4 col. 6 |
| Sum of costs | Def. 25.3, Eq. 25.4; Ch. 7 §7.3.3, Ch. 2 Def. 2.18 | Tab. 25.1 row 6 | Tab. 25.4 col. 7 |
| Replanning count | **Def. 25.4** ($n_{\text{rp}}$ = entries into Replanning, $n_{\text{av}}$ alongside) — ties directly to Ch. 24 §24.4 | Tab. 25.1 row 7 | Tab. 25.4 col. 8; Tab. 25.5 |
| Computation time | Def. 25.4 ($c_i(t)$, $\bar c$, $c_{99}$, deadline misses, $C_{\text{tot}}$) | Tab. 25.1 row 8 | Tab. 25.4 cols. 9–10; Fig. 25.4a cactus |
| Formation error | **Def. 25.5**, Eq. 25.5 ($e_F(t)$, $\bar e_F$, $e_F^{\max}$) — *defined in* **Ch. 23 §23.3, Def. 23.6, Eq. 23.4** (centred variant Eq. 23.5); convergence bound §23.6.4 / Tab. 23.3 | Tab. 25.1 row 9 | Tab. 25.4 col. 11; Tab. 25.5 |
| Communication violations | Def. 25.5, Eq. 25.6 ($n_{\text{cv}}$, kept edges **and** $\lambda_2(\mathbf L(t))=0$); range constraint Ch. 23 §23.7.3 | Tab. 25.1 row 10 | Tab. 25.4 col. 12 |

All ten are defined, grouped into four families (safety / efficiency / effort / constraints),
given units, estimators and a "sensitive to" column (Tab. 25.1), and actually printed by
`compute_metrics()` in `code/ch25_evaluation.py`.

---

## 4. The research directions (seven, not six)

The plan's §5 lists seven bullets (Ch. 1 §1.5 confirms: "The plan names seven such directions").
All seven have a dedicated, named paragraph in **Ch. 24 §24.13 "Research directions"**, each with a
formulation *and* an evaluation protocol, and all seven are previewed as a description list in
**Ch. 1 §1.5** and restated in Appendix A's "After Week 12" paragraph.

| # | Plan direction | Ch. 24 §24.13 paragraph | Also discussed |
|---|---|---|---|
| 1 | Unknown, non-cooperative drones with uncertain motion | "Non-cooperative, uncertain intruders" (reachable-set tube, manoeuvre-mode mixture) | §1.5 bullet 1; Ch. 13 §13.4.1 full responsibility; Ch. 19 §19.8; Ch. 20 §20.7 |
| 2 | Combining CBS-style coordination with real-time local avoidance without destroying global guarantees | "Coordinating CBS with real-time local avoidance…" (robust MAPF, tubes and time windows) | §1.5 bullet 2; §24.11 Tab. 24.5 (what survives) |
| 3 | Formation preservation and communication-range constraints during avoidance and replanning | "Formation and communication constraints during avoidance and replanning" (prioritised slacks, formation-level replan) | §1.5 bullet 3; §24.8; Ch. 21 §21.3.3; Ch. 23 §23.7.3 |
| 4 | Prediction-aware constraints that carry uncertainty | "Prediction-aware constraints with uncertainty" (risk allocation, calibration, particle tests) | §1.5 bullet 4; §24.9; Ch. 21 §21.7.2 chance constraints; Ch. 20 §20.7 |
| 5 | Deciding automatically when local avoidance suffices vs. a global replan | "Deciding automatically between local and global" (cost model over continue/reconnect/replan, regret vs. an oracle) | §1.5 bullet 5 ("Step 3 versus step 4"); §24.4 thresholds Tab. 24.3 |
| 6 | Reducing computation for larger swarms in dynamic 3D | "Computation for larger swarms in dynamic 3D environments" (ECBS + ID, windowed replanning, incremental search, lattices/sampling) | §1.5 bullet 6; Ch. 10 §10.7.4; Ch. 11 §11.4.1 |
| 7 | Benchmarks comparing local-only, replan-only and hybrid | "Benchmarks comparing local-only, replan-only and hybrid" | §1.5 bullet 7; **Ch. 25** §25.4.2 (Tab. 25.3), §25.5, §25.7, §25.8 |

---

## 5. The ten-item completion checklist

Appendix A **§A.6, Tab. A.4** repeats the ten statements and names chapters. Verified against the
chapters:

| # | Checklist item | Appendix A says | Actually taught at | OK? |
|---|---|---|---|---|
| 1 | Implement and explain A\* and space-time A\* | Ch. 4; reservation tables in Ch. 8 | §4.4, §4.6, **§4.8** (Alg. 4.2); reservation table §8.4 (Alg. 8.2) | yes |
| 2 | Explain the CBS constraint tree; implement vertex and edge constraints | Ch. 9; conflict types in Ch. 7 | §9.3–9.4 (Alg. 9.1–9.2), §9.5; Def. 7.4 (§7.3.2) | yes |
| 3 | Understand the speed/optimality trade-off in ECBS | Ch. 10 | §10.6.3 ($w$-suboptimality), §10.7.1, §10.7.3 Tab. 10.5 | yes |
| 4 | Explain VO/RVO/ORCA using relative position and velocity | Ch. 12, Ch. 13 | §12.3.1–12.3.5; §13.3.1, §13.3.3, §13.4 | yes |
| 5 | Track an unknown drone from noisy observations | Ch. 18, Ch. 19 | §18.4–18.9; §19.4–19.6 | yes |
| 6 | Compare a simple prediction baseline with LSTM prediction | Ch. 20 | §20.4 (Alg. 20.1) vs. §20.5 (Alg. 20.2), measured in §20.8 Tab. 20.2–20.3 | yes |
| 7 | Trigger local avoidance from a time-to-collision / safety-horizon rule | time to collision in Ch. 12; the trigger in Ch. 24 | §12.3.4 (Alg. 12.1); §24.5 Def. 24.2 + Alg. 24.2 | yes |
| 8 | Reconnect to the global route or trigger D\* Lite/A\* replanning | Ch. 5; reconnection in Ch. 24 | §5.6 (Alg. 5.2); §24.6 Def. 24.3 + Alg. 24.3; replan §24.7 Alg. 24.4 | yes |
| 9 | Enforce formation and/or communication-range constraints | Ch. 21, Ch. 23; during avoidance in Ch. 24 | §21.3.3, §21.6.2; §23.4.4, §23.7.3; §24.8 (Eqs. 24.6–24.7) | yes |
| 10 | Evaluate the hybrid system with reproducible metrics and controlled scenarios | Ch. 25 | §25.3 (Defs. 25.1–25.5), §25.4, §25.5, §25.6, §25.7, §25.8 Tab. 25.7 | yes |

All ten checklist items are taught where Appendix A says they are. The checklist is additionally
operationalised as an eight-question self-check (§A.6) tied to the weeks.

---

## 6a. GAPS, with a concrete proposed fix

Ordered by how much a reader working the plan would feel them.

**G-1 — The "learned prediction" level of the experiment matrix is a hook, not a working level.**
`predict_intruders()` in `code/ch25_evaluation.py` handles `"perfect"`, `"cv"` and `"noisy"`
end-to-end, but the `"learned"` branch is `pred[j] = predictor(hist)` with a *user-supplied*
callable and no adapter to the Ch. 20 model. So the plan's third factor cannot be run out of the
box, and §25.7's mini-study fixes prediction at `"noisy"`. *Fix:* in **Ch. 25 §25.11
(Implementation notes)** add a ~1-page subsection "Plugging in the Week-10 predictor" with a
10–15 line adapter that wraps `ch20_prediction.predict_seq2seq` (history length, frame
conversion, `(H+1, 2)` output shape) plus a one-line note in §25.4.1 under Tab. 25.2, and a
part (d) on **Ex. 25.7** asking for one cell of the prediction-quality factor with the learned
level. ~1 page of text + ~30 lines of code.

**G-2 — The "formation-preserving" level of the constraints factor is measured but never
enforced in the Ch. 25 runner.** `compute_metrics()` computes $e_F$ over *all pairs* against the
nominal geometry; there is no formation-preserving *strategy* in `ch25_evaluation.py`, and §25.7
runs "no formation requirement" only. Ch. 24 §24.8 defines the enforcement (Eq. 24.7) and the
Ch. 24 scenario exercises it (drone C is a follower of A, Ex. 24.4; Ex. 24.6 works the formation trigger), so the two chapters are out of step.
*Fix:* in **Ch. 25 §25.4.1**, add two paragraphs after Tab. 25.2 stating that the
formation-preserving level is the Eq. 24.6 term of Ch. 24 §24.8 switched on, with the formation
graph $E_F$ taken from the scenario; and in **§25.11** add the `edges`/`k_F` arguments to the
runner. Roughly 3/4 page + a code note. (Alternative, cheaper: state explicitly in §25.4.1 that
the toy runner leaves this level to the reader, and add it as part (e) of Ex. 25.7.)

**G-3 — Fourteen of the twenty-five chapter coding exercises — including both Week-12 capstone
exercises — have no entry in Appendix C.** Solutions exist for the coding exercises of
Ch. 1, 2, 4, 5, 6, 12, 18, 19, 21, 22, 23; they are missing for **Ch. 3, 7 (both), 8, 9, 10, 11,
13, 14, 15, 16, 17, 20, 24, 25**. Since Appendix A makes the coding exercise the *deliverable* of
every week, a self-study reader has no check for Weeks 3, 4, 5, 6 (the ORCA half), 7, 8, 10 and 12.
*Fix:* add a short hint block (10–20 lines each: expected shape of the answer, the number to
reproduce from the chapter's worked example, the two commonest bugs) to
`appendices/solutions/ch{03,07,08,09,10,11,13,14,15,16,17,20,24,25}-solutions.tex`. About 4–5
pages total; the numbers already exist in the chapters' worked-example tables.

**G-4 — Push-and-Rotate has no pseudocode and no reference implementation.** §11.7.2 describes the
`Rotate` primitive in prose with Fig. 11.6(c), and Thm. 11.12 states completeness, but
`code/ch11_mstar.py` implements `push_and_swap()` only. A reader who wants to *see* the
completeness claim exercised cannot. *Fix:* either (a) add a 12-line `Algorithm 11.4
(Push-and-Rotate, conceptual)` next to Alg. 11.3 in **§11.7.3**, showing the subproblem
decomposition and where `Rotate` is called — about 1/2 page; or (b) add one sentence to §11.7.3
and to Tab. A.5's Push-and-Swap row saying the rotation is presented at awareness depth only.
Option (b) is ~2 lines and is enough for an "Awareness" priority.

**G-5 — The Transformer is covered at awareness depth only, although the plan tags it
"Awareness to High".** §20.6 gives attention, multi-head attention and positional encodings with
code building blocks, but there is no transformer *predictor* and no row for it in the empirical
comparison (Tab. 20.2/20.3), so the "High" end of the tag has no path. *Fix:* add a subsection
**§20.6.4 "A transformer predictor end to end"** (~1.5 pages): encoder stack over the observed
window, a decoder that emits $H$ displacements, the exact parameter count, and a row in
Tab. 20.2/20.3 produced by extending `ch20_prediction.py` (the attention primitives already
exist) — plus a part (d) on **Ex. 20.9** comparing it with the LSTM at the same horizons. If that
is too much, add one sentence at the start of §20.6 saying the chapter treats the transformer at
awareness depth and pointing to `rudenko2020human` / `vaswani2017attention` for the rest (~2 lines).

**G-6 — MILP is in the algorithm list but nowhere in the plan's twelve-week *Learn* columns; the
book quietly attaches it to Week 11 without saying it is an addition.** Tab. A.1's Week-11 "Read"
column shows "(Ch. 22)" and Tab. A.5 gives MILP "Wk 11", but the plan's own Week-11 *Learn* cell
(reproduced verbatim in Tab. A.1) never mentions MILP. A reader comparing the two columns sees an
unexplained chapter. *Fix:* one sentence in **§A.4.11** ("Ch. 22 is the book's addition to the
plan's Week 11: the plan asks for MILP at Medium priority but gives it no week, so it is read here
as background for the cost of exactness"). ~2 lines.

**G-7 — Ch. 4 is the only chapter with no numbered `\section{Summary}`.** Its summary content
exists as a bare `summary` environment (`ch04-astar.tex:1459–1490`) between §4.10 and §4.11, so
A\* — the single most important chapter of the plan — has no "4.11 Summary" in the table of
contents while every other chapter has one. *Fix:* add `\section{Summary}\label{sec:ch04-summary}`
immediately before line 1459 of `Overleaf/chapters/ch04-astar.tex`. ~1 line. (Renumbers §4.11
Exercises to §4.12; no cross-reference breaks, since Exercises is referenced by label.)

**G-8 — No exercise-level traceability anywhere.** Appendix A never cites a single exercise label
(zero occurrences of `exr:` in `appA-study-plan.tex`); it identifies each week's deliverable by the
phrase "the exercise marked *Coding* at the end of that chapter". Ten chapters have **two**
Coding-marked exercises (Ch. 5, 7, 9, 10, 13, 15, 16, 18, 19, 20), and in Ch. 20 the *last*
Coding-marked exercise is `exr:ch20-calibration` (Ex. 20.10), not the week's exercise
`exr:ch20-coding` (Ex. 20.9). *Fix:* add one narrow column, "Exercise", to **Tab. A.1** carrying
the actual `\cref{exr:chNN-coding}` for each week (and both labels for Weeks 1, 3, 6, 8, 11), and
delete the "marked *Coding* at the end of that chapter" sentence from §A.1. ~1/4 page; the table
is a `longtable` and already has room if `Read` and `Learn` each lose 0.3 cm.

---

## 6b. Factual inconsistencies between Appendix A and the chapters

None of these is a broken cross-reference: the full build (`build-full/main.log`) reports **no
undefined or multiply-defined references**, so every `\cref` in Appendix A resolves. The problems
below are semantic — a statement in Appendix A that the chapter it points at contradicts.

**I-1 — The experiment-matrix cell count disagrees: Appendix A says 768, Ch. 25 says 576.**
§A.5.3 (`sec:appA-experiments`): *"the five factors — four swarm sizes, four intruder counts, four
prediction qualities, three avoidance strategies and four constraint settings … have
$4\times4\times4\times3\times4 = 768$ cells"*. Ch. 25 §25.4.1 and the caption of **Tab. 25.2**:
*"that is $3\times4\times4\times3\times4 = 576$ cells and, with 20 seeds per cell, 11 520 runs"*,
because Tab. 25.2 reads the swarm size as three levels, "2, **4**, 8 (more if computationally
feasible)". Both texts justify their own count, but they contradict each other on the same object
and a reader who quotes one will be corrected by the other. *Fix:* make Appendix A follow
Tab. 25.2 (3 levels for the swarm size → 576) and keep its explanatory sentence as a footnote, or
add "(Ch. 25 counts the swarm size as three levels and so reports 576; the difference is only
whether 'and more if computationally feasible' is a level)".

**I-2 — Appendix A's description of $\mathrm{VO}^{\tau}_{A|B}$ is backwards with respect to
Ch. 12 and Ch. 13.** §A.4.6 (Week 6 "Focus"): *"The velocity obstacle (VO) $\mathrm{VO}^{\tau}_{A|B}$
is the set of velocities of $A$ that, if $B$ held its current velocity, would bring the two discs
into contact within the horizon $\tau$; subtracting $\mathbf v_B$ gives the relative-velocity form
— the truncated cone of Ch. 12 — which is the form ORCA reasons in."* Both halves are wrong:
- In **Ch. 13 Def. 13.1 / Eq. (13.3)** the *un-argumented* symbol $\mathrm{VO}^{\tau}_{A|B}$ is
  *already* the relative-velocity set (apex at the origin); the absolute set is the translate
  $\mathbf v_B + \mathrm{VO}^{\tau}_{A|B}$, and Ch. 13 says so explicitly two lines later. You do
  not subtract $\mathbf v_B$ from it.
- In **Ch. 12 Def. 12.7 / Eq. (12.10)** the truncated cone is written *with* the argument,
  $\mathrm{VO}^{\tau}_{A|B}(\mathbf v_B) = \{\mathbf v_A : t_c(\mathbf v_A-\mathbf v_B)\le\tau\}$,
  i.e. Ch. 12's truncated cone is the **absolute** form; its relative form is
  $\mathrm{VO}^{\tau}_{A|B}(\mathbf v_B)-\mathbf v_B$ (Prop. 12.8, Eq. 12.11).
So Appendix A attributes the absolute set to the bare symbol and the relative set to Ch. 12 —
exactly the opposite of both chapters. *Fix:* rewrite the sentence as "$\mathrm{VO}^{\tau}_{A|B}$
(Ch. 13, Def. 13.1) is the set of *relative* velocities that lead to contact within $\tau$; adding
$\mathbf v_B$ gives the absolute set, which Ch. 12 writes $\mathrm{VO}^{\tau}_{A|B}(\mathbf v_B)$.
ORCA reasons in the relative form."

**I-3 — Two different exercises each call themselves "the Week 3 coding exercise", and they
overlap.** `exr:ch07-prioritized` (**Ex. 7.9**) opens *"The coding exercise of Week 3
(Appendix A): write a first prioritized planner for two to five agents…"*; `exr:ch08-coding`
(**Ex. 8.8**) opens *"This is the Week 3 exercise of the study plan (Appendix A). … implement a
reservation table … Cooperative A\* … the priority loop"*. Both build prioritized planning for
2–5 agents with deliberate conflict cases (the plan's Week-3 wording). Appendix A §A.4.3 papers
over it with the plural ("the coding exercises of Ch. 7, Ch. 8") but never says which is *the*
deliverable, and §A.1's rule ("the exercise marked *Coding* at the end of that chapter") does not
disambiguate Ch. 7, which has two. *Fix:* reword Ex. 7.9's opening to "a warm-up for the Week-3
exercise; Ch. 8 develops it properly" (it already ends with that parenthetical), and name
Ex. 8.8 as the week's deliverable in §A.4.3.

**I-4 — Weeks 8's two exercises both claim the whole week, unlike the halved Weeks 1 and 6.**
`exr:ch16-coding` (**Ex. 16.8**) says *"The coding exercise of Week 8"* and `exr:ch17-coding`
(**Ex. 17.7**) says *"This is the Week 8 coding exercise of the study plan"*. Compare the
consistent pattern used elsewhere: Ex. 3.7 ("the *first half* of the Week 1 exercise; Ch. 4
completes it") / Ex. 4.8 ("continues Ex. 3.7"), and Ex. 12.7 ("the *first half* of the coding
exercise of Week 6") / Ex. 13.9. Appendix A §A.4.8 asks for both, so the work is right, but the
labelling is inconsistent with the book's own convention. *Fix:* change Ex. 16.8's opening to
"the first half of the Week 8 coding exercise; Ch. 17 completes it", matching Ex. 3.7 and Ex. 12.7.

**I-5 — Appendix A's Week-5 build prescribes a set of $w$ values the Ch. 10 exercise does not
use.** §A.4.5 ("Build"): *"benchmark both for $w \in \{1.0, 1.1, 1.5, 2.0\}$"*, and §A.3 offers as
a compression *"Week 5 (benchmark two values of $w$ instead of **four**)"*. But **Ex. 10.7**, which
§A.4.5 itself names as the deliverable ("The coding exercise of Ch. 10"), asks for
$w\in\{1.1, 1.5, 2\}$ in part (a) — three values, without $w=1.0$ — and
$w\in\{1, 1.02, 1.05, 1.1, 1.2, 1.5, 2, 3\}$ in part (b) — eight. Neither is four. *Fix:* change
§A.4.5 to "$w \in \{1.1, 1.5, 2\}$ with $w=1$ (plain CBS) as the reference, as Ex. 10.7(a) asks",
and §A.3 to "benchmark two values of $w$ instead of three".

**I-6 — Tab. A.2 (the four layers) omits Ch. 19 from the prediction layer while Tab. A.4 (the
checklist) requires it.** Tab. A.2 row 2 gives the prediction layer as "Ch. 18, Ch. 20"; Tab. A.4
row 5 ("track an unknown drone from noisy observations") gives "Ch. 18, Ch. 19"; and Ch. 24's own
Tab. 24.1 row 2 gives the layer as "KF, EKF/UKF/PF, LSTM (Ch. 18, Ch. 19, Ch. 20)". Week 9
(§A.4.9) also reads Ch. 19. *Fix:* add Ch. 19 to Tab. A.2's row 2 so the three tables agree.

**I-7 (minor, Ch. 1 rather than Appendix A, but on the same traceability chain) — Ch. 1 §1.4
claims Ch. 7 "teaches no algorithm of its own."** The sentence after Tab. 1.4 reads: *"Two chapters
do not appear in the table because they teach no algorithm of their own. Ch. 2 is the toolbox …
Ch. 7 defines the multi-agent path finding problem…"* But Ch. 7 §7.4 is titled "The algorithm:
conflict detection" and contains **Alg. 7.1** (pairwise detection) and **Alg. 7.2** (hashed
detection), which Ch. 9 and Ch. 24 §24.7 both reuse by reference. *Fix:* change the sentence to
"…because they teach no algorithm of the plan's list", ~1 word.

### Checked and found correct

For completeness, the following Appendix A claims were verified and hold: every chapter/week pair
in **Tab. A.5** (all 27 rows) matches where the algorithm is actually taught; the **Tab. A.6**
reading order reproduces the plan's twelve items in order with the right chapters (item 10 →
Ch. 2, 16, 17); the Fig. A.2 caption's arrow counts ("four arrows leave Week 1 and two leave
Week 3") match `figures/appA/week-dependencies.tex` exactly; §A.3's "seven of the twelve weeks
(2, 3 and 2)" matches the schedule; the claim that "every chapter ships a Python file
`code/chNN_*.py`" holds for all 25 chapters; and every one of the ten checklist rows in Tab. A.4
points at a chapter that does teach the item (§6 above).
