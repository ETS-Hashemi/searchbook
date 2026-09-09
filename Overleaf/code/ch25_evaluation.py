"""Evaluation toolkit for the hybrid planner (Chapter 25).

The file has five parts.

1. Metrics.  The ten metrics of the chapter, each computed from an
   execution log (arrays of positions, computation times and events):
   collision rate, minimum separation, path length, travel time, makespan,
   sum of costs, replanning count, computation time, formation error and
   communication violations.
2. Scenarios.  A seeded generator: k controlled drones with crossing
   straight-line missions, a nominal plan that resolves their conflicts
   by departure delays (a prioritised-planning stand-in for CBS), and m
   non-cooperative intruders from three trajectory families (straight
   crossing, turning, evasive) aimed at a drone at a chosen crossing angle.
3. A toy simulator with pluggable strategies: "none", "local" (a sampled
   velocity-obstacle avoider with horizon TAU_H, the stand-in for ORCA/DWA),
   "replan" (a detour planner with wait actions, the stand-in for D* Lite /
   space-time A*) and "hybrid" (local first, replanning when the deviation
   or the time in Avoiding grows or reconnection fails), driven by the
   Nominal / Avoiding / Reconnecting / Replanning state machine of
   Chapter 24.  Intruders are predicted perfectly, by constant velocity from
   the true state, or by a constant-velocity Kalman filter on noisy
   measurements with an uncertainty-inflated safety radius.
4. A paired runner: every strategy sees exactly the same scenarios (same
   seed, same intruder trajectories, same measurement noise).
5. Statistics: t intervals, bootstrap intervals, Wilson intervals for
   rates, medians with IQR, paired comparisons (mean difference with its
   interval, Cohen's d_z, Wilcoxon signed-rank and sign tests) and Holm's
   correction.

Self-test:  python3 ch25_evaluation.py      (runs the mini-study of the
chapter, checks the metrics on hand-built logs, determinism and pairing).
"""
import hashlib
import math
import time

import numpy as np

# ----------------------------------------------------------------------
# Constants of the toy world
# ----------------------------------------------------------------------
DT = 0.1             # simulation step (s)
R_DRONE = 0.3        # radius of a controlled drone (m)
R_INTRUDER = 0.3     # radius of an intruder (m)
R_SAFE = 1.0         # safety radius kept by the avoidance layers (m)
R_PLAN = 1.5         # separation enforced by the nominal plan (m)
V_MAX = 2.0          # speed limit (m/s)
V_NOM = 1.5          # nominal cruise speed (m/s)
TAU_H = 3.0          # safety horizon (s)
T_MAX = 40.0         # mission time cap (s)
GOAL_TOL = 0.3       # arrival tolerance (m)
LOOKAHEAD = 0.5      # tracking look-ahead (s)
SIGMA_MEAS = 0.3     # measurement noise of the intruder position (m)
SIGMA_ACC = 1.0      # process-noise acceleration of the intruder filter
KAPPA = 1.0          # inflation factor of the safety radius (sigma units)
INFL_MAX = 1.5       # cap on the inflation (m)
R_COMM = 10.0        # communication range of the study (m)
DEV_MAX = 3.0        # hybrid: deviation that triggers a replan (m)
AVOID_MAX = 4.0      # hybrid: time in Avoiding that triggers a replan (s)
REPLAN_GAP = 1.0     # minimum time between two replans (s)
RECONNECT_LEAD = 2.0  # lead of the reconnection waypoint (s)
N_MAX = int(round(T_MAX / DT))
H = int(round(TAU_H / DT))
HS = np.arange(H + 1) * DT
FAMILIES = ("straight", "turning", "evasive")
STRATEGIES = ("none", "local", "replan", "hybrid")
MODES = {"Nominal": 0, "Avoiding": 1, "Reconnecting": 2, "Replanning": 3}


# ----------------------------------------------------------------------
# Geometry helpers
# ----------------------------------------------------------------------
def rot(u, ang):
    """Rotate the 2-vector u by ang radians."""
    c, s = math.cos(ang), math.sin(ang)
    return np.array([c * u[0] - s * u[1], s * u[0] + c * u[1]])


def clamp_speed(v, vmax=V_MAX):
    n = float(np.hypot(v[0], v[1]))
    return v if n <= vmax else v * (vmax / n)


def segment_min_dist(a0, a1, b0, b1):
    """Minimum distance between two points that move linearly from a0 to
    a1 and from b0 to b1 during one step (closest approach of Chapter 2).
    Broadcasts over leading dimensions."""
    r0 = a0 - b0
    w = (a1 - b1) - r0
    ww = np.sum(w * w, axis=-1)
    s = np.where(ww > 1e-12, -np.sum(r0 * w, axis=-1) / np.maximum(ww, 1e-12), 0.0)
    s = np.clip(s, 0.0, 1.0)
    return np.linalg.norm(r0 + s[..., None] * w, axis=-1)


class Reference:
    """Piecewise-linear time-parameterised path through knots (t_k, p_k)."""

    def __init__(self, times, points):
        self.t = np.asarray(times, float)
        self.p = np.asarray(points, float)

    def at(self, t):
        t = np.atleast_1d(np.asarray(t, float))
        x = np.interp(t, self.t, self.p[:, 0])
        y = np.interp(t, self.t, self.p[:, 1])
        return np.stack([x, y], axis=-1)

    def length(self):
        return float(np.sum(np.linalg.norm(np.diff(self.p, axis=0), axis=1)))


# ----------------------------------------------------------------------
# Part 1: metrics on an execution log
# ----------------------------------------------------------------------
def pair_min_distances(P, Q=None):
    """Per-pair minimum distance over a run.  P has shape (T+1, k, 2) and
    Q shape (T+1, m, 2).  Returns dd (k x k, inf on the diagonal) and
    di (k x m).  Motion between samples is taken as linear."""
    k = P.shape[1]
    m = 0 if Q is None else Q.shape[1]
    dd = np.full((k, k), np.inf)
    di = np.full((k, m), np.inf)

    def track_min(A, B):
        if A.shape[0] == 1:
            return float(np.linalg.norm(A[0] - B[0]))
        return float(np.min(segment_min_dist(A[:-1], A[1:], B[:-1], B[1:])))

    for i in range(k):
        for j in range(i + 1, k):
            dd[i, j] = dd[j, i] = track_min(P[:, i], P[:, j])
        for j in range(m):
            di[i, j] = track_min(P[:, i], Q[:, j])
    return dd, di


def collision_summary(P, Q=None, r_drone=R_DRONE, r_intruder=R_INTRUDER):
    """Collision indicator and count, and the minimum separations."""
    dd, di = pair_min_distances(P, Q)
    k = P.shape[1]
    iu = np.triu_indices(k, 1)
    n_dd = int(np.sum(dd[iu] < 2 * r_drone)) if k > 1 else 0
    n_di = int(np.sum(di < r_drone + r_intruder)) if di.size else 0
    return {
        "collision": int(n_dd + n_di > 0),
        "n_collisions": n_dd + n_di,
        "dmin_dd": float(np.min(dd[iu])) if k > 1 else float("nan"),
        "dmin_di": float(np.min(di)) if di.size else float("nan"),
    }


def path_lengths(P):
    """Flown length of every drone (m), shape (k,)."""
    if P.shape[0] < 2:
        return np.zeros(P.shape[1])
    return np.sum(np.linalg.norm(np.diff(P, axis=0), axis=2), axis=0)


def travel_times(P, goals, dt=DT, tol=GOAL_TOL):
    """First time after which each drone stays within tol of its goal;
    inf if it is not there at the end of the log."""
    away = np.linalg.norm(P - np.asarray(goals)[None], axis=2) > tol
    out = []
    for i in range(P.shape[1]):
        idx = np.nonzero(away[:, i])[0]
        if away[-1, i]:
            out.append(float("inf"))
        elif idx.size == 0:
            out.append(0.0)
        else:
            out.append(float((idx[-1] + 1) * dt))
    return np.array(out)


def makespan(travel):
    return float(np.max(travel))


def sum_of_costs(travel):
    return float(np.sum(travel))


def replanning_count(replans):
    return int(np.sum(replans))


def computation_time(C, dt=DT):
    """C holds the computation time (s) of every decision, shape (T+1, k)."""
    flat = np.asarray(C, float).ravel()
    return {
        "comp_mean_ms": float(np.mean(flat)) * 1000.0,
        "comp_p99_ms": float(np.percentile(flat, 99)) * 1000.0,
        "comp_max_ms": float(np.max(flat)) * 1000.0,
        "comp_total_s": float(np.sum(flat)),
        "deadline_misses": int(np.sum(flat > dt)),
    }


def formation_error(P, D, edges):
    """e_F(t) of Chapter 23: RMS violation of the desired displacements
    D[t, i, j] over the edges (i, j) of the formation graph; shape (T+1,)."""
    sq = np.stack([np.sum(((P[:, j] - P[:, i]) - D[:, i, j]) ** 2, axis=1)
                   for (i, j) in edges])
    return np.sqrt(np.mean(sq, axis=0))


def algebraic_connectivity(positions, r_comm):
    """lambda_2 of the Laplacian of the radius graph (inf for one node)."""
    k = positions.shape[0]
    if k < 2:
        return float("inf")
    d = np.linalg.norm(positions[:, None] - positions[None], axis=2)
    A = (d <= r_comm).astype(float)
    np.fill_diagonal(A, 0.0)
    L = np.diag(A.sum(axis=1)) - A
    return float(np.linalg.eigvalsh(L)[1])


def communication_violations(P, r_comm, edges_keep=()):
    """Number of steps at which a kept edge is longer than r_comm or the
    radius graph is disconnected (lambda_2 = 0)."""
    n = 0
    for t in range(P.shape[0]):
        bad = algebraic_connectivity(P[t], r_comm) < 1e-9
        for (i, j) in edges_keep:
            bad = bad or np.linalg.norm(P[t, i] - P[t, j]) > r_comm
        n += int(bad)
    return n


# ----------------------------------------------------------------------
# Part 2: scenarios
# ----------------------------------------------------------------------
class Scenario:
    """Everything a run needs, fixed by the seed: starts, goals, the
    nominal plan, the intruder trajectories and the measurement noise."""

    def __init__(self, seed, k, m, starts, goals, refs, Q, noise, families, meta):
        self.seed, self.k, self.m = seed, k, m
        self.starts, self.goals, self.refs = starts, goals, refs
        self.Q, self.noise, self.families, self.meta = Q, noise, families, meta

    def signature(self):
        h = hashlib.sha1()
        for a in (self.starts, self.goals, self.Q, self.noise):
            h.update(np.ascontiguousarray(a).tobytes())
        h.update(",".join(self.families).encode())
        return h.hexdigest()


def plan_nominal(starts, goals, r_plan=R_PLAN):
    """Straight-line missions at V_NOM; each drone in priority order takes
    the smallest departure delay (multiples of 0.5 s) that keeps it at
    least r_plan from every higher-priority drone at all sampled times."""
    ts = np.arange(N_MAX + 1) * DT
    refs, tracks = [], []
    for i in range(len(starts)):
        length = float(np.linalg.norm(goals[i] - starts[i]))
        dur = length / V_NOM
        delay = 0.0
        while True:
            ref = Reference([0.0, delay, delay + dur], [starts[i], starts[i], goals[i]])
            pos = ref.at(ts)
            ok = all(np.min(np.linalg.norm(pos - tr, axis=1)) >= r_plan for tr in tracks)
            if ok or delay >= 15.0:
                break
            delay += 0.5
        refs.append(ref)
        tracks.append(pos)
    return refs


def intruder_trajectory(p_x, t_x, heading, speed, fam, omega, t_e, d_e):
    """Closed-form trajectory that passes p_x at time t_x with the given
    heading (unit vector) and speed; sampled at every step."""
    ts = np.arange(N_MAX + 1) * DT
    phi_x = math.atan2(heading[1], heading[0])
    if fam == "turning":
        phi = phi_x + omega * (ts - t_x)
        x = p_x[0] + speed / omega * (np.sin(phi) - math.sin(phi_x))
        y = p_x[1] - speed / omega * (np.cos(phi) - math.cos(phi_x))
        return np.stack([x, y], axis=1)
    Q = p_x[None] + speed * (ts - t_x)[:, None] * heading[None]
    if fam == "evasive":
        q_e = p_x + speed * (t_e - t_x) * heading
        h2 = rot(heading, d_e)
        late = ts > t_e
        Q[late] = q_e[None] + speed * (ts[late] - t_e)[:, None] * h2[None]
    return Q


def make_scenario(seed, k, m, family="mixed", angle_deg=None, spread=8.0, arena=20.0):
    """Seeded scenario: k drones on crossing missions, m aimed intruders."""
    rng = np.random.default_rng(seed)
    ys = arena / 2 + (np.linspace(-spread / 2, spread / 2, k) if k > 1 else np.zeros(1))
    starts = np.stack([np.full(k, 2.0), ys + rng.uniform(-0.3, 0.3, k)], axis=1)
    perm = np.arange(k)
    while k > 1 and np.all(perm == np.arange(k)):
        perm = rng.permutation(k)
    goals = np.stack([np.full(k, arena - 2.0), ys[perm] + rng.uniform(-0.3, 0.3, k)], axis=1)
    refs = plan_nominal(starts, goals)
    Q = np.zeros((N_MAX + 1, m, 2))
    families, meta = [], []
    targets = rng.permutation(k)
    for j in range(m):
        fam = family if family != "mixed" else FAMILIES[(seed + j) % 3]
        i = int(targets[j % k])
        ref = refs[i]
        delay, dur = ref.t[1], ref.t[2] - ref.t[1]
        t_x = float(delay + rng.uniform(0.35, 0.65) * dur)
        p_x = ref.at(t_x)[0]
        u = goals[i] - starts[i]
        u = u / np.linalg.norm(u)
        theta = math.radians(angle_deg if angle_deg is not None else rng.uniform(45.0, 135.0))
        side = float(rng.choice([-1.0, 1.0]))
        heading = rot(u, side * theta)
        speed = float(rng.uniform(1.0, 2.0))
        omega = math.radians(rng.uniform(5.0, 15.0)) * float(rng.choice([-1.0, 1.0]))
        t_e = t_x - float(rng.uniform(1.0, 2.5))
        d_e = math.radians(rng.uniform(30.0, 70.0)) * float(rng.choice([-1.0, 1.0]))
        Q[:, j] = intruder_trajectory(p_x, t_x, heading, speed, fam, omega, t_e, d_e)
        families.append(fam)
        meta.append({"target": i, "t_x": t_x, "angle_deg": math.degrees(theta),
                     "speed": speed, "family": fam})
    noise = rng.normal(0.0, SIGMA_MEAS, size=(N_MAX + 1, m, 2))
    return Scenario(seed, k, m, starts, goals, refs, Q, noise, families, meta)


# ----------------------------------------------------------------------
# Part 3: prediction and the toy simulator
# ----------------------------------------------------------------------
class IntruderKF:
    """Constant-velocity Kalman filter (Chapter 18) on noisy positions."""

    def __init__(self, z0, dt=DT):
        self.x = np.array([z0[0], z0[1], 0.0, 0.0])
        self.P = np.diag([SIGMA_MEAS ** 2, SIGMA_MEAS ** 2, 1.0, 1.0])
        self.F = np.array([[1, 0, dt, 0], [0, 1, 0, dt], [0, 0, 1, 0], [0, 0, 0, 1]], float)
        g = np.array([[dt * dt / 2, 0], [0, dt * dt / 2], [dt, 0], [0, dt]])
        self.Qn = SIGMA_ACC ** 2 * g @ g.T
        self.Hm = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], float)
        self.R = SIGMA_MEAS ** 2 * np.eye(2)

    def step(self, z):
        x = self.F @ self.x
        P = self.F @ self.P @ self.F.T + self.Qn
        S = self.Hm @ P @ self.Hm.T + self.R
        K = P @ self.Hm.T @ np.linalg.inv(S)
        self.x = x + K @ (z - self.Hm @ x)
        self.P = (np.eye(4) - K @ self.Hm) @ P

    def estimate(self):
        sp = math.sqrt((self.P[0, 0] + self.P[1, 1]) / 2)
        sv = math.sqrt((self.P[2, 2] + self.P[3, 3]) / 2)
        return self.x[:2].copy(), self.x[2:].copy(), sp, sv


def predict_intruders(sc, n, prediction, kfs, predictor=None):
    """Predicted intruder positions at steps n..n+H, shape (m, H+1, 2),
    and the inflation of the safety radius, shape (m, H+1)."""
    pred = np.zeros((sc.m, H + 1, 2))
    infl = np.zeros((sc.m, H + 1))
    for j in range(sc.m):
        if prediction == "perfect":
            idx = np.minimum(n + np.arange(H + 1), N_MAX)
            pred[j] = sc.Q[idx, j]
        elif prediction == "cv":
            n0 = max(n, 1)
            v = (sc.Q[n0, j] - sc.Q[n0 - 1, j]) / DT
            pred[j] = sc.Q[n, j][None] + HS[:, None] * v[None]
        elif prediction == "noisy":
            kf = kfs[j]
            kf.step(sc.Q[n, j] + sc.noise[n, j])
            q, v, sp, sv = kf.estimate()
            pred[j] = q[None] + HS[:, None] * v[None]
            infl[j] = np.minimum(KAPPA * np.sqrt(sp ** 2 + (HS * sv) ** 2), INFL_MAX)
        elif prediction == "learned":
            hist = sc.Q[max(0, n - 20):n + 1, j] + sc.noise[max(0, n - 20):n + 1, j]
            pred[j] = predictor(hist)  # user-supplied model returning (H+1, 2)
        else:
            raise ValueError(prediction)
    return pred, infl


def track_velocity(p, ref, t):
    target = ref.at(t + LOOKAHEAD)[0]
    return clamp_speed((target - p) / LOOKAHEAD)


def trajectory_margin(traj, obs, rad):
    """Smallest (distance - radius) between a trajectory (…, H+1, 2) and
    the predicted obstacles obs (n_obs, H+1, 2) with radii rad (n_obs, H+1)."""
    d = np.linalg.norm(traj[..., None, :, :] - obs, axis=-1)   # (…, n_obs, H+1)
    return np.min(d - rad, axis=(-2, -1))


def predicted_conflict(p, v, obs, rad):
    traj = p[None] + HS[:, None] * v[None]
    return bool(trajectory_margin(traj, obs, rad) < 0.0)


_ANG = np.radians(np.arange(0, 360, 15))
_CAND = np.concatenate([np.zeros((1, 2))] + [
    s * np.stack([np.cos(_ANG), np.sin(_ANG)], axis=1) for s in (0.5, 1.0, 1.5, 2.0)])


def safe_velocity(p, v_pref, obs, rad):
    """Sampled velocity-obstacle choice: among the candidate velocities whose
    constant-velocity trajectory keeps the inflated safety radius from every
    predicted obstacle over the horizon, take the one closest to v_pref;
    if none is safe, take the one with the largest margin."""
    cand = np.vstack([_CAND, v_pref[None]])
    traj = p[None, None] + HS[None, :, None] * cand[:, None, :]      # (C, H+1, 2)
    margin = trajectory_margin(traj, obs, rad)                       # (C,)
    feasible = margin >= 0.0
    if np.any(feasible):
        dev = np.linalg.norm(cand - v_pref[None], axis=1)
        dev[~feasible] = np.inf
        return cand[int(np.argmin(dev))].copy()
    return cand[int(np.argmax(margin))].copy()


def leg_is_safe(p, w, obs, rad):
    """Is the straight leg from p towards w at V_NOM free of predicted
    conflicts within the horizon?"""
    d = w - p
    length = float(np.linalg.norm(d))
    frac = np.minimum(1.0, HS * V_NOM / max(length, 1e-9))
    traj = p[None] + frac[:, None] * d[None]
    return bool(trajectory_margin(traj, obs, rad) >= 0.0)


def replan(p, t, goal, obs, rad):
    """Detour planner (stand-in for space-time A* / D* Lite): candidate
    routes are the direct leg and legs through a waypoint offset sideways
    from the point of closest predicted approach, each optionally preceded
    by a wait; the cheapest route whose predicted margin is non-negative
    over the horizon wins, otherwise the one with the largest margin."""
    d = goal - p
    length = float(np.linalg.norm(d))
    if length < 1e-6:
        return Reference([t, t + 1.0], [p, p])
    u = d / length
    nrm = np.array([-u[1], u[0]])
    frac = np.minimum(1.0, HS * V_NOM / length)
    direct = p[None] + frac[:, None] * d[None]
    dist = np.linalg.norm(direct[:, None, :] - obs.transpose(1, 0, 2), axis=2) - rad.T
    h_star = int(np.argmin(np.min(dist, axis=1)))
    c = direct[h_star]
    best, best_cost, best_margin = None, math.inf, -math.inf
    for wait in (0.0, 1.0, 2.0):
        for s in (0.0, 2.0, -2.0, 3.5, -3.5, 5.0, -5.0):
            pts = [p, p] + ([c + s * nrm] if s != 0.0 else []) + [goal]
            times = [t, t + wait]
            for a, b in zip(pts[1:-1], pts[2:]):
                times.append(times[-1] + float(np.linalg.norm(b - a)) / V_NOM)
            ref = Reference(times, pts)
            margin = float(trajectory_margin(ref.at(t + HS), obs, rad))
            cost = times[-1] - t
            if margin >= 0.0 and cost < best_cost:
                best, best_cost = ref, cost
            if best is None and margin > best_margin:
                best_margin, fallback = margin, ref
    return best if best is not None else fallback


class RunLog:
    """Execution log of one run (positions, modes, computation, events)."""

    def __init__(self, sc, P, Q, modes, C, replans, avoid_steps):
        self.scenario = sc
        self.P, self.Q, self.modes, self.C = P, Q, modes, C
        self.replans, self.avoid_steps = replans, avoid_steps
        self.dt = DT
        ts = np.arange(P.shape[0]) * DT
        self.P_nom = np.stack([r.at(ts) for r in sc.refs], axis=1)   # (T+1, k, 2)
        self.nominal_lengths = np.array([r.length() for r in sc.refs])


def run_episode(sc, strategy, prediction="noisy", predictor=None):
    """Simulate one scenario under one strategy and return its log."""
    if strategy not in STRATEGIES:
        raise ValueError(strategy)
    k, m = sc.k, sc.m
    p = sc.starts.copy()
    v = np.zeros((k, 2))
    refs = [Reference(r.t, r.p) for r in sc.refs]
    mode = ["Nominal"] * k
    t_avoid = np.zeros(k)
    t_replan = np.full(k, -math.inf)
    replans = np.zeros(k, int)
    avoid_steps = np.zeros(k, int)
    kfs = [IntruderKF(sc.Q[0, j] + sc.noise[0, j]) for j in range(m)]
    P, Qlog, modes, C = [], [], [], []
    settled = 0
    for n in range(N_MAX + 1):
        t = n * DT
        pred, infl = predict_intruders(sc, n, prediction, kfs, predictor)
        P.append(p.copy())
        Qlog.append(sc.Q[n].copy())
        modes.append([MODES[x] for x in mode])
        c_row = np.zeros(k)
        v_new = np.zeros((k, 2))
        for i in range(k):
            t0 = time.perf_counter()
            others = np.delete(np.arange(k), i)
            obs = np.concatenate([p[others][:, None, :] + HS[None, :, None] * v[others][:, None, :], pred])
            rad = np.concatenate([np.full((k - 1, H + 1), R_SAFE), R_SAFE + infl])
            v_pref = track_velocity(p[i], refs[i], t)
            conflict = predicted_conflict(p[i], v_pref, obs, rad)
            new_mode, cmd = "Nominal", v_pref
            if strategy == "local":
                if conflict:
                    new_mode, cmd = "Avoiding", safe_velocity(p[i], v_pref, obs, rad)
            elif strategy == "replan":
                if conflict and t - t_replan[i] >= REPLAN_GAP:
                    refs[i] = replan(p[i], t, sc.goals[i], obs, rad)
                    replans[i] += 1
                    t_replan[i] = t
                    new_mode, cmd = "Replanning", track_velocity(p[i], refs[i], t)
            elif strategy == "hybrid":
                if conflict:
                    if mode[i] != "Avoiding":
                        t_avoid[i] = t
                    dev = float(np.linalg.norm(p[i] - refs[i].at(t)[0]))
                    if (dev > DEV_MAX or t - t_avoid[i] > AVOID_MAX) and t - t_replan[i] >= REPLAN_GAP:
                        refs[i] = replan(p[i], t, sc.goals[i], obs, rad)
                        replans[i] += 1
                        t_replan[i] = t
                        new_mode, cmd = "Replanning", track_velocity(p[i], refs[i], t)
                    else:
                        new_mode, cmd = "Avoiding", safe_velocity(p[i], v_pref, obs, rad)
                elif mode[i] in ("Avoiding", "Reconnecting"):
                    if leg_is_safe(p[i], refs[i].at(t + RECONNECT_LEAD)[0], obs, rad):
                        new_mode, cmd = "Nominal", v_pref
                    elif t - t_replan[i] >= REPLAN_GAP:
                        refs[i] = replan(p[i], t, sc.goals[i], obs, rad)
                        replans[i] += 1
                        t_replan[i] = t
                        new_mode, cmd = "Replanning", track_velocity(p[i], refs[i], t)
                    else:
                        new_mode, cmd = "Reconnecting", safe_velocity(p[i], v_pref, obs, rad)
            c_row[i] = time.perf_counter() - t0
            avoid_steps[i] += int(new_mode in ("Avoiding", "Reconnecting"))
            mode[i] = new_mode
            v_new[i] = clamp_speed(cmd)
        C.append(c_row)
        v = v_new
        p = p + v * DT
        at_goal = np.all(np.linalg.norm(p - sc.goals, axis=1) <= GOAL_TOL)
        settled = settled + 1 if at_goal and all(x == "Nominal" for x in mode) else 0
        if settled >= 10:
            P.append(p.copy())
            Qlog.append(sc.Q[min(n + 1, N_MAX)].copy())
            modes.append([MODES[x] for x in mode])
            C.append(np.zeros(k))
            break
    return RunLog(sc, np.array(P), np.array(Qlog), np.array(modes), np.array(C), replans, avoid_steps)


def compute_metrics(log, r_comm=R_COMM, edges_keep=()):
    """All ten metrics of one run as a flat dictionary."""
    P, Q, sc = log.P, log.Q, log.scenario
    k = P.shape[1]
    out = collision_summary(P, Q if sc.m else None)
    lengths = path_lengths(P)
    travel = travel_times(P, sc.goals, log.dt)
    censored = np.minimum(travel, T_MAX)
    edges = [(i, j) for i in range(k) for j in range(i + 1, k)]
    D = log.P_nom[:, None, :, :] - log.P_nom[:, :, None, :]     # D[t,i,j] = nom_j - nom_i
    ef = formation_error(P, D, edges) if edges else np.zeros(P.shape[0])
    out.update({
        "near_miss": int(min(out["dmin_dd"] if k > 1 else np.inf,
                             out["dmin_di"] if sc.m else np.inf) < R_SAFE),
        "path_total": float(np.sum(lengths)),
        "path_ratio": float(np.mean(lengths / log.nominal_lengths)),
        "travel_mean": float(np.mean(censored)),
        "makespan": float(np.max(censored)),
        "soc": float(np.sum(censored)),
        "success": int(np.all(np.isfinite(travel)) and out["collision"] == 0),
        "replans": replanning_count(log.replans),
        "avoid_steps": int(np.sum(log.avoid_steps)),
        "ef_mean": float(np.mean(ef)),
        "ef_max": float(np.max(ef)),
        "comm_viol": communication_violations(P, r_comm, edges_keep),
        "steps": int(P.shape[0]),
    })
    out.update(computation_time(log.C, log.dt))
    return out


# ----------------------------------------------------------------------
# Part 4: the paired runner
# ----------------------------------------------------------------------
METRIC_COLUMNS = ("collision", "n_collisions", "near_miss", "dmin_dd", "dmin_di",
                  "path_total", "path_ratio", "travel_mean", "makespan", "soc",
                  "success", "replans", "avoid_steps", "comp_mean_ms", "comp_p99_ms",
                  "comp_max_ms", "comp_total_s", "deadline_misses", "ef_mean",
                  "ef_max", "comm_viol", "steps")


def run_study(cells, strategies, seeds, prediction="noisy", family="mixed", **kw):
    """Paired design: for every cell (k, m) and seed one scenario is built
    and every strategy runs on it.  Returns one row (dict) per run."""
    rows = []
    for (k, m) in cells:
        for seed in seeds:
            sc = make_scenario(seed, k, m, family=family, **kw)
            sig = sc.signature()
            for strat in strategies:
                log = run_episode(sc, strat, prediction)
                row = {"k": k, "m": m, "seed": seed, "strategy": strat,
                       "family": sc.families[0] if sc.m else "-", "signature": sig}
                row.update(compute_metrics(log))
                rows.append(row)
    return rows


def write_dat(path, rows, columns):
    """Whitespace-separated table with a header row (ASCII only)."""
    with open(path, "w") as f:
        f.write(" ".join(columns) + "\n")
        for r in rows:
            f.write(" ".join(_fmt(r[c]) for c in columns) + "\n")


def _fmt(x):
    if isinstance(x, (bool, np.bool_)):
        return str(int(x))
    if isinstance(x, (int, np.integer)):
        return str(int(x))
    if isinstance(x, float):
        if not np.isfinite(x):
            return "nan"
        return "%.4f" % x
    return str(x)


# ----------------------------------------------------------------------
# Part 5: statistics
# ----------------------------------------------------------------------
_T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365,
         8: 2.306, 9: 2.262, 10: 2.228, 11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145,
         15: 2.131, 16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086, 21: 2.080,
         22: 2.074, 23: 2.069, 24: 2.064, 25: 2.060, 26: 2.056, 27: 2.052, 28: 2.048,
         29: 2.045, 30: 2.042, 40: 2.021, 60: 2.000, 120: 1.980}


def t_quantile_975(df):
    """Upper 2.5% quantile of Student's t (table, linear between rows)."""
    keys = sorted(_T975)
    if df <= keys[0]:
        return _T975[keys[0]]
    if df >= keys[-1]:
        return 1.960
    lo = max(x for x in keys if x <= df)
    hi = min(x for x in keys if x >= df)
    if lo == hi:
        return _T975[lo]
    w = (df - lo) / (hi - lo)
    return _T975[lo] + w * (_T975[hi] - _T975[lo])


def mean_ci(x):
    """Mean, 95% t interval and standard deviation of a sample."""
    x = np.asarray(x, float)
    n = x.size
    mu = float(np.mean(x))
    if n < 2:
        return {"mean": mu, "lo": mu, "hi": mu, "sd": 0.0, "n": n}
    sd = float(np.std(x, ddof=1))
    half = t_quantile_975(n - 1) * sd / math.sqrt(n)
    return {"mean": mu, "lo": mu - half, "hi": mu + half, "sd": sd, "n": n}


def median_iqr(x):
    x = np.asarray(x, float)
    q1, med, q3 = np.percentile(x, [25, 50, 75])
    return {"median": float(med), "q1": float(q1), "q3": float(q3),
            "p5": float(np.percentile(x, 5)), "min": float(np.min(x)), "n": x.size}


def wilson(successes, n, z=1.96):
    """Wilson score interval for a proportion."""
    if n == 0:
        return {"p": float("nan"), "lo": float("nan"), "hi": float("nan"), "n": 0}
    p = successes / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return {"p": p, "lo": max(0.0, centre - half), "hi": min(1.0, centre + half), "n": n}


def bootstrap_ci(x, stat=np.mean, n_boot=2000, seed=0):
    """Percentile bootstrap interval of a statistic."""
    x = np.asarray(x, float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, x.size, size=(n_boot, x.size))
    boots = np.array([stat(x[row]) for row in idx])
    return {"stat": float(stat(x)), "lo": float(np.percentile(boots, 2.5)),
            "hi": float(np.percentile(boots, 97.5))}


EXACT_MAX_N = 20   # exact signed-rank null distribution up to this many non-zero differences


def _normal_sf(z):
    return 0.5 * math.erfc(z / math.sqrt(2.0))


def wilcoxon_signed_rank(d):
    """Two-sided Wilcoxon signed-rank test (zero differences dropped,
    average ranks for ties).

    For n <= 20 the null distribution is enumerated exactly: conditional on
    the observed ranks r_i (doubled, so that average ranks stay integral),
    every sign pattern is equally likely, and the generating polynomial
    prod_i (1 + x^{r_i}) counts the sign patterns by rank sum.  Above n = 20
    the count (2^n) grows faster than it is worth and the normal
    approximation takes over, with a continuity correction and with sigma
    corrected for ties.  The approximation needs n of about 25 or more; on
    the n <= 20 of a seed study it can be wrong by a factor of several in
    the tail, which is why the exact branch exists.
    """
    d = np.asarray(d, float)
    d = d[d != 0]
    n = d.size
    if n == 0:
        return {"W": 0.0, "p": 1.0, "n": 0, "exact": True}
    a = np.abs(d)
    order = np.argsort(a)
    ranks = np.empty(n)
    ranks[order] = np.arange(1, n + 1)
    for val in np.unique(a):
        same = a == val
        ranks[same] = np.mean(ranks[same])
    w_plus = float(np.sum(ranks[d > 0]))
    if n <= EXACT_MAX_N:
        # doubled ranks keep half-integer average ranks in integer arithmetic
        r2 = np.rint(2 * ranks).astype(int)
        counts = np.zeros(int(r2.sum()) + 1)
        counts[0] = 1.0
        for r in r2:                       # poly = poly * (1 + x^r)
            counts[r:] += counts[:counts.size - r].copy()
        total = counts.sum()               # = 2^n
        w2 = int(round(2 * w_plus))
        lower = counts[:w2 + 1].sum() / total
        upper = counts[w2:].sum() / total
        return {"W": w_plus, "p": min(1.0, 2 * min(lower, upper)), "n": n, "exact": True}
    mu = n * (n + 1) / 4.0
    ties = 0.0
    for val in np.unique(a):
        t = int(np.sum(a == val))
        ties += t ** 3 - t
    var = n * (n + 1) * (2 * n + 1) / 24.0 - ties / 48.0
    sigma = math.sqrt(var)
    z = (abs(w_plus - mu) - 0.5) / sigma if sigma > 0 else 0.0
    return {"W": w_plus, "p": min(1.0, 2 * _normal_sf(max(z, 0.0))), "n": n, "exact": False}


def sign_test(d):
    """Exact two-sided sign test (zero differences dropped)."""
    d = np.asarray(d, float)
    d = d[d != 0]
    n, pos = d.size, int(np.sum(d > 0))
    if n == 0:
        return {"pos": 0, "neg": 0, "p": 1.0}
    cdf = sum(math.comb(n, i) for i in range(0, min(pos, n - pos) + 1)) / 2 ** n
    return {"pos": pos, "neg": n - pos, "p": min(1.0, 2 * cdf)}


def paired_compare(a, b):
    """Paired comparison of metric a against metric b (same scenarios):
    mean difference with its t interval, Cohen's d_z, Wilcoxon and sign tests."""
    d = np.asarray(a, float) - np.asarray(b, float)
    ci = mean_ci(d)
    dz = ci["mean"] / ci["sd"] if ci["sd"] > 0 else float("inf") if ci["mean"] != 0 else 0.0
    out = {"mean_diff": ci["mean"], "lo": ci["lo"], "hi": ci["hi"], "d_z": dz,
           "n": d.size, "better": int(np.sum(d < 0)), "worse": int(np.sum(d > 0)),
           "tie": int(np.sum(d == 0))}
    w = wilcoxon_signed_rank(d)
    out["p_wilcoxon"] = w["p"]
    out["p_exact"] = w["exact"]
    out["p_sign"] = sign_test(d)["p"]
    return out


def holm(pvalues):
    """Holm's step-down adjusted p-values."""
    p = np.asarray(pvalues, float)
    m = p.size
    order = np.argsort(p)
    adj = np.empty(m)
    running = 0.0
    for rank, idx in enumerate(order):
        running = max(running, (m - rank) * p[idx])
        adj[idx] = min(1.0, running)
    return adj


def summarise(rows, keys=("k", "m", "strategy")):
    """Per-group summary: rates with Wilson intervals, means with t
    intervals, medians with IQR.  Returns {group: summary}."""
    groups = {}
    for r in rows:
        groups.setdefault(tuple(r[key] for key in keys), []).append(r)
    out = {}
    for g, rs in sorted(groups.items()):
        n = len(rs)
        s = {"n": n}
        for col in ("collision", "near_miss", "success"):
            s[col] = wilson(sum(r[col] for r in rs), n)
        for col in ("path_ratio", "makespan", "soc", "travel_mean", "replans",
                    "comp_mean_ms", "comp_total_s", "ef_mean", "ef_max", "comm_viol",
                    "avoid_steps"):
            s[col] = mean_ci([r[col] for r in rs])
        for col in ("dmin_dd", "dmin_di", "comp_max_ms"):
            vals = [r[col] for r in rs if np.isfinite(r[col])]
            s[col] = median_iqr(vals) if vals else None
        out[g] = s
    return out


def paired_table(rows, metric, strategy_a, strategy_b, keys=("k", "m")):
    """Paired comparison of strategy_a minus strategy_b per cell."""
    out = {}
    cells = sorted({tuple(r[key] for key in keys) for r in rows})
    for cell in cells:
        def pick(strat):
            sel = [r for r in rows if tuple(r[key] for key in keys) == cell and r["strategy"] == strat]
            return [r[metric] for r in sorted(sel, key=lambda r: r["seed"])]
        a, b = pick(strategy_a), pick(strategy_b)
        if a and b and len(a) == len(b):
            out[cell] = paired_compare(a, b)
    return out


# ----------------------------------------------------------------------
# The mini-study of the chapter
# ----------------------------------------------------------------------
STUDY_CELLS = ((2, 0), (2, 1), (4, 0), (4, 1))
STUDY_SEEDS = tuple(range(20))


def run_mini_study(seeds=STUDY_SEEDS, strategies=STRATEGIES, prediction="noisy"):
    return run_study(STUDY_CELLS, strategies, seeds, prediction=prediction, family="mixed")


def print_summary(summary):
    print("%-4s %-2s %-7s %5s %11s %9s %7s %7s %7s %6s %7s %7s %6s" % (
        "k", "m", "strat", "n", "coll[CI]", "dmin_di", "ratio", "mksp", "soc",
        "repl", "cmp_ms", "eF", "cviol"))
    for (k, m, strat), s in summary.items():
        c = s["collision"]
        dm = s["dmin_di"]
        print("%-4d %-2d %-7s %5d %4.2f[%.2f,%.2f] %9s %7.3f %7.2f %7.2f %6.2f %7.3f %7.3f %6.1f" % (
            k, m, strat, s["n"], c["p"], c["lo"], c["hi"],
            ("%.2f" % dm["median"]) if dm else "-", s["path_ratio"]["mean"],
            s["makespan"]["mean"], s["soc"]["mean"], s["replans"]["mean"],
            s["comp_mean_ms"]["mean"], s["ef_mean"]["mean"], s["comm_viol"]["mean"]))


# ----------------------------------------------------------------------
# Self-test
# ----------------------------------------------------------------------
def _selftest_metrics():
    P = np.array([[[0, 0], [0, 2]], [[1, 0], [0, 2]], [[2, 0], [1, 2]], [[3, 0], [1, 2]]], float)
    Q = np.array([[[2, 4]], [[2, 3]], [[2, 2]], [[2, 1]]], float)
    goals = np.array([[3, 0], [1, 2]], float)
    c = collision_summary(P, Q, r_drone=0.3, r_intruder=0.8)
    assert c["collision"] == 1 and c["n_collisions"] == 1
    assert abs(c["dmin_dd"] - 2.0) < 1e-9 and abs(c["dmin_di"] - 1.0) < 1e-9
    c2 = collision_summary(P, Q, r_drone=0.3, r_intruder=0.3)
    assert c2["collision"] == 0 and c2["n_collisions"] == 0
    dd, di = pair_min_distances(P, Q)
    assert abs(di[0, 0] - math.sqrt(2.0)) < 1e-9
    L = path_lengths(P)
    assert np.allclose(L, [3.0, 1.0])
    tt = travel_times(P, goals, dt=1.0, tol=0.3)
    assert np.allclose(tt, [3.0, 2.0])
    assert makespan(tt) == 3.0 and sum_of_costs(tt) == 5.0
    assert replanning_count(np.array([2, 1])) == 3
    C = np.array([[0.001, 0.002], [0.003, 0.004], [0.005, 0.006], [0.007, 0.008]])
    ct = computation_time(C, dt=1.0)
    assert abs(ct["comp_total_s"] - 0.036) < 1e-12 and abs(ct["comp_mean_ms"] - 4.5) < 1e-9
    assert abs(ct["comp_max_ms"] - 8.0) < 1e-9 and ct["deadline_misses"] == 0
    assert computation_time(C, dt=0.005)["deadline_misses"] == 3
    D = np.zeros((4, 2, 2, 2))
    D[:, 0, 1] = [0.0, 2.0]
    D[:, 1, 0] = [0.0, -2.0]
    ef = formation_error(P, D, [(0, 1)])
    assert np.allclose(ef, [0.0, 1.0, 1.0, 2.0])
    assert communication_violations(P, 2.5) == 1
    assert communication_violations(P, 2.2) == 3
    assert communication_violations(P, 2.5, edges_keep=[(0, 1)]) == 1
    assert algebraic_connectivity(P[0], 2.5) == 2.0 and algebraic_connectivity(P[3], 2.5) == 0.0
    # single drone, no intruder: metrics must not crash
    c3 = collision_summary(P[:, :1], None)
    assert c3["collision"] == 0 and math.isnan(c3["dmin_dd"]) and math.isnan(c3["dmin_di"])


def _selftest_statistics():
    w = wilson(0, 20)
    assert w["lo"] == 0.0 and abs(w["hi"] - 0.1611) < 5e-4
    ci = mean_ci([1, 2, 3, 4, 5])
    assert abs(ci["mean"] - 3.0) < 1e-12 and abs(ci["hi"] - 4.963) < 2e-3
    a = np.array([1, 2, 3, 4, 5, 6, 7, 8], float)
    b = a - np.array([0.5, 1, 0.5, 1, 0.5, 1, 0.5, 1])
    pc = paired_compare(a, b)
    assert abs(pc["mean_diff"] - 0.75) < 1e-12 and pc["worse"] == 8 and pc["better"] == 0
    assert pc["p_sign"] < 0.01 and pc["p_wilcoxon"] < 0.02
    # the exact signed-rank distribution: six positive differences, W+ = 21 = max,
    # so p = 2 * 1/2^6 = 0.03125 exactly (the normal approximation would say 0.028)
    w6 = wilcoxon_signed_rank(np.array([1.0, 2, 3, 4, 5, 6]))
    assert w6["exact"] and abs(w6["p"] - 2 / 64) < 1e-12 and w6["W"] == 21.0
    # ties are handled by average (half-integer) ranks and still enumerated exactly
    w4 = wilcoxon_signed_rank(np.array([1.0, 1.0, -2.0, 3.0]))
    assert w4["exact"] and abs(w4["W"] - 7.0) < 1e-12
    assert not wilcoxon_signed_rank(np.arange(1.0, 26.0))["exact"]   # n = 25 > EXACT_MAX_N
    assert paired_compare(a, a)["mean_diff"] == 0.0 and paired_compare(a, a)["p_wilcoxon"] == 1.0
    bs = bootstrap_ci(a)
    assert bs["lo"] <= 4.5 <= bs["hi"]
    adj = holm([0.01, 0.04, 0.03])
    assert np.allclose(adj, [0.03, 0.06, 0.06])
    m = median_iqr([1, 2, 3, 4, 5])
    assert m["median"] == 3.0 and m["q1"] == 2.0 and m["q3"] == 4.0


def _selftest_simulator():
    # the nominal plan keeps R_PLAN between drones and the run is deterministic
    sc = make_scenario(3, 4, 1)
    P_nom = np.stack([r.at(np.arange(N_MAX + 1) * DT) for r in sc.refs], axis=1)
    dd, _ = pair_min_distances(P_nom)
    assert np.min(dd[np.triu_indices(4, 1)]) >= R_PLAN - 1e-9
    assert sc.signature() == make_scenario(3, 4, 1).signature()
    assert sc.signature() != make_scenario(4, 4, 1).signature()
    # intruder families pass through their aim point at t_x
    for fam in FAMILIES:
        s2 = make_scenario(7, 2, 1, family=fam)
        meta = s2.meta[0]
        n_x = int(round(meta["t_x"] / DT))
        aim = s2.refs[meta["target"]].at(meta["t_x"])[0]
        tol = 0.25 if fam != "evasive" else 6.0
        assert np.linalg.norm(s2.Q[n_x, 0] - aim) < tol, (fam, np.linalg.norm(s2.Q[n_x, 0] - aim))
    rows1 = run_study([(2, 1)], STRATEGIES, [0, 1], prediction="noisy")
    rows2 = run_study([(2, 1)], STRATEGIES, [0, 1], prediction="noisy")
    skip = {"comp_mean_ms", "comp_p99_ms", "comp_max_ms", "comp_total_s", "deadline_misses"}
    for r1, r2 in zip(rows1, rows2):
        for key in r1:
            if key not in skip:
                assert r1[key] == r2[key] or (isinstance(r1[key], float) and np.isnan(r1[key]) and np.isnan(r2[key])), key
    # the paired design: every strategy of a (cell, seed) sees the same scenario
    for seed in (0, 1):
        sigs = {r["signature"] for r in rows1 if r["seed"] == seed}
        assert len(sigs) == 1
    for pred in ("perfect", "cv"):
        log = run_episode(make_scenario(5, 2, 1), "hybrid", prediction=pred)
        assert log.P.shape[1] == 2 and log.P.shape[0] > 10


def _selftest_study():
    t0 = time.perf_counter()
    rows = run_mini_study()
    elapsed = time.perf_counter() - t0
    summary = summarise(rows)
    print_summary(summary)
    print("mini-study: %d runs in %.1f s" % (len(rows), elapsed))
    assert len(rows) == len(STUDY_CELLS) * len(STUDY_SEEDS) * len(STRATEGIES)
    # sanity checks of the mini-study
    assert summary[(2, 0, "none")]["collision"]["p"] == 0.0     # the plan is conflict-free
    assert summary[(4, 0, "none")]["collision"]["p"] == 0.0
    assert summary[(2, 1, "none")]["collision"]["p"] >= 0.5     # the intruders are aimed
    for k in (2, 4):
        assert summary[(k, 1, "hybrid")]["collision"]["p"] <= summary[(k, 1, "none")]["collision"]["p"]
        assert summary[(k, 1, "local")]["collision"]["p"] <= summary[(k, 1, "none")]["collision"]["p"]
    cmp = paired_table(rows, "path_ratio", "hybrid", "local")
    for cell, c in cmp.items():
        assert c["n"] == len(STUDY_SEEDS)
    return rows, summary


if __name__ == "__main__":
    t_start = time.perf_counter()
    _selftest_metrics()
    _selftest_statistics()
    _selftest_simulator()
    rows, summary = _selftest_study()
    for metric in ("path_ratio", "dmin_di", "makespan", "replans", "ef_mean"):
        for other in ("local", "replan"):
            for cell, c in paired_table(rows, metric, "hybrid", other).items():
                print("paired %-10s hybrid-%-6s cell %s: diff %+.3f [%+.3f, %+.3f] d_z %+.2f "
                      "better/worse/tie %d/%d/%d p_wilcoxon %.4f p_sign %.4f" % (
                          metric, other, cell, c["mean_diff"], c["lo"], c["hi"], c["d_z"],
                          c["better"], c["worse"], c["tie"], c["p_wilcoxon"], c["p_sign"]))
    fam = {}
    for r in rows:
        if r["m"] == 1 and r["strategy"] == "none":
            fam.setdefault(r["family"], []).append(r["collision"])
    print("collision rate of 'none' by intruder family:",
          {f: "%d/%d" % (sum(v), len(v)) for f, v in sorted(fam.items())})
    print("self-test passed in %.1f s" % (time.perf_counter() - t_start))
