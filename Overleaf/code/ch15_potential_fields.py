"""Artificial potential fields (APF) for a point drone in the plane.

Chapter 15 of "Multi-Agent Path Planning and Drone Collision Avoidance".

Contents
    ApfParams                gains and simulation settings
    Disc                     circular obstacle with a distance query rho, grad rho
    attractive_potential     1/2 k_att d^2, or conic (k_att d* d - 1/2 k_att d*^2)
    attractive_force         beyond the switch distance d* (hybrid potential)
    repulsive_potential      Khatib's 1/2 k_rep (1/rho - 1/rho0)^2 for rho <= rho0,
    repulsive_force          optionally multiplied by d^n (Ge & Cui's GNRON fix)
    total_potential, total_force, clip_speed, min_clearance
    simulate_many            vectorised gradient-descent controller with a
                             velocity limit, local-minimum detection and an
                             optional random-walk escape
    simulate                 the same for one start; returns the path
    follow_waypoints         APF as the local layer under a global plan
    simulate_swarm           several drones with inter-agent repulsion
    stiffness                largest eigenvalue of the Hessian of U at a point
    lateral_reversals        oscillation metric (sign changes of the lateral step)
    worked_example, local_minimum_case, gnron_case, corridor_case,
    basin_experiment         the scenes used in the chapter

Positions are NumPy arrays of shape (2,) or (N, 2); every force and potential
function broadcasts over the leading axis.  Run the file for the self-test.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, replace

import numpy as np

EPS = 1e-12


@dataclass
class ApfParams:
    """Gains of the potentials and settings of the discrete-time controller."""
    k_att: float = 1.0        # attractive gain
    k_rep: float = 1.0        # repulsive gain
    rho0: float = 2.0         # influence distance of an obstacle
    d_star: float | None = None  # None: quadratic everywhere; else conic beyond d*
    n_gnron: int = 0          # 0: Khatib's repulsion; n >= 1: multiplied by d^n
    v_max: float = 1.0        # speed limit of the commanded velocity
    dt: float = 0.01          # control period
    goal_tol: float = 0.05    # distance at which the goal counts as reached
    max_steps: int = 4000     # simulation horizon
    stuck_window: int = 100   # steps over which progress is measured
    stuck_tol: float = 1e-3   # less displacement than this = local minimum


@dataclass
class Disc:
    """A circular obstacle; the drone is a point (obstacles are inflated)."""
    center: tuple
    radius: float

    def distance(self, p):
        """Return rho(p) = distance to the boundary (shape (...,1)) and
        grad rho (shape (...,2)), the unit vector away from the centre."""
        diff = np.asarray(p, float) - np.asarray(self.center, float)
        r = np.linalg.norm(diff, axis=-1, keepdims=True)
        return r - self.radius, diff / np.maximum(r, EPS)


def _goal_offset(p, goal):
    diff = np.asarray(p, float) - np.asarray(goal, float)
    return diff, np.linalg.norm(diff, axis=-1, keepdims=True)


# ---------------------------------------------------------------- potentials
def attractive_potential(p, goal, prm):
    """U_att: quadratic bowl, conic beyond d* if prm.d_star is set."""
    _, d = _goal_offset(p, goal)
    quad = 0.5 * prm.k_att * d ** 2
    if prm.d_star is None:
        return quad[..., 0]
    conic = prm.k_att * prm.d_star * d - 0.5 * prm.k_att * prm.d_star ** 2
    return np.where(d <= prm.d_star, quad, conic)[..., 0]


def attractive_force(p, goal, prm):
    """F_att = -grad U_att: -k_att (p - goal), of constant size beyond d*."""
    diff, d = _goal_offset(p, goal)
    if prm.d_star is None:
        return -prm.k_att * diff
    scale = np.where(d <= prm.d_star, 1.0, prm.d_star / np.maximum(d, EPS))
    return -prm.k_att * scale * diff


def repulsive_potential(p, goal, obstacles, prm):
    """U_rep = sum_i 1/2 k_rep (1/rho_i - 1/rho0)^2 [rho_i <= rho0] * d^n."""
    _, d = _goal_offset(p, goal)
    u = np.zeros(d.shape[:-1])
    for obs in obstacles:
        rho, _ = obs.distance(p)
        rho_c = np.maximum(rho, EPS)
        term = 0.5 * prm.k_rep * (1.0 / rho_c - 1.0 / prm.rho0) ** 2
        if prm.n_gnron > 0:
            term = term * d ** prm.n_gnron
        u = u + np.where(rho < prm.rho0, term, 0.0)[..., 0]
    return u


def repulsive_force(p, goal, obstacles, prm):
    """F_rep = -grad U_rep, summed over the obstacles within rho0.

    Plain (n = 0):  k_rep (1/rho - 1/rho0) / rho^2 * grad rho.
    GNRON (n >= 1): the same times d^n, minus
                    (n/2) k_rep (1/rho - 1/rho0)^2 d^(n-1) * grad d,
    where d = ||p - goal|| and grad d = (p - goal)/d points away from the goal.
    """
    diff, d = _goal_offset(p, goal)
    n = prm.n_gnron
    f = np.zeros_like(diff)
    for obs in obstacles:
        rho, grad_rho = obs.distance(p)
        rho_c = np.maximum(rho, EPS)
        gap = 1.0 / rho_c - 1.0 / prm.rho0
        term = prm.k_rep * gap / rho_c ** 2 * grad_rho
        if n > 0:
            grad_d = diff / np.maximum(d, EPS)
            term = term * d ** n - 0.5 * n * prm.k_rep * gap ** 2 * d ** (n - 1) * grad_d
        f = f + np.where(rho < prm.rho0, term, 0.0)
    return f


def total_potential(p, goal, obstacles, prm):
    return attractive_potential(p, goal, prm) + repulsive_potential(p, goal, obstacles, prm)


def total_force(p, goal, obstacles, prm):
    return attractive_force(p, goal, prm) + repulsive_force(p, goal, obstacles, prm)


def clip_speed(v, v_max):
    """Scale v down to length v_max where it is longer (direction is kept)."""
    s = np.linalg.norm(v, axis=-1, keepdims=True)
    return np.where(s > v_max, v * (v_max / np.maximum(s, EPS)), v)


def min_clearance(p, obstacles):
    """Smallest rho over the obstacles, shape (...,); +inf without obstacles."""
    p = np.asarray(p, float)
    best = np.full(p.shape[:-1], np.inf)
    for obs in obstacles:
        best = np.minimum(best, obs.distance(p)[0][..., 0])
    return best


def numerical_force(p, goal, obstacles, prm, h=1e-6):
    """-grad U by central differences; used to check the analytic forces."""
    p = np.asarray(p, float)
    f = np.zeros(2)
    for i in range(2):
        e = np.zeros(2)
        e[i] = h
        f[i] = -(total_potential(p + e, goal, obstacles, prm)
                 - total_potential(p - e, goal, obstacles, prm)) / (2 * h)
    return f


def stiffness(p, goal, obstacles, prm, h=1e-5):
    """Largest eigenvalue of the Hessian of U at p (from the analytic force).

    With the explicit update p <- p + dt F the motion near a minimum is
    stable only if dt * stiffness < 2 and free of overshoot if < 1.
    """
    p = np.asarray(p, float)
    hess = np.zeros((2, 2))
    for i in range(2):
        e = np.zeros(2)
        e[i] = h
        hess[:, i] = -(total_force(p + e, goal, obstacles, prm)
                       - total_force(p - e, goal, obstacles, prm)) / (2 * h)
    hess = 0.5 * (hess + hess.T)
    return float(np.linalg.eigvalsh(hess)[-1])


# ---------------------------------------------------------------- controller
def simulate_many(starts, goal, obstacles, prm, escape=False, rng=None,
                  max_escapes=20, keep_history=True):
    """Gradient-descent controller run from every row of `starts` at once.

    Each drone repeats: stop if within goal_tol of the goal; compute the force;
    clip it to v_max; move by dt * v.  A drone that moved less than stuck_tol
    during the last stuck_window steps is declared stuck (local minimum).
    With escape=True a stuck drone instead makes a straight random move of
    random length (0.5 .. 2 units) at full speed, aborted if it would come
    closer than 0.1 to an obstacle, and then resumes the descent.

    Returns a dict with status (N,) in {reached, stuck, collision, timeout},
    final (N,2), steps (N,), escapes (N,) and history (T,N,2) or None.
    """
    starts = np.atleast_2d(np.asarray(starts, float))
    goal = np.asarray(goal, float)
    n = len(starts)
    rng = np.random.default_rng(0) if rng is None else rng
    p = starts.copy()
    status = np.array(["timeout"] * n, dtype=object)
    active = np.ones(n, bool)
    steps = np.zeros(n, int)
    escapes = np.zeros(n, int)
    esc_left = np.zeros(n, int)
    esc_dir = np.zeros((n, 2))
    hist = [p.copy()]
    w = prm.stuck_window
    for k in range(prm.max_steps):
        reached = active & (np.linalg.norm(p - goal, axis=1) <= prm.goal_tol)
        status[reached] = "reached"
        hit = active & ~reached & (min_clearance(p, obstacles) <= 0.0)
        status[hit] = "collision"
        active &= ~(reached | hit)
        if k >= w:
            moved = np.linalg.norm(p - hist[k - w], axis=1)
            stuck = active & (esc_left == 0) & (moved < prm.stuck_tol)
            if escape:
                kick = stuck & (escapes < max_escapes)
                ang = rng.uniform(0.0, 2.0 * np.pi, n)
                length = rng.uniform(0.5, 2.0, n)
                esc_dir[kick] = np.stack([np.cos(ang), np.sin(ang)], axis=1)[kick]
                esc_left[kick] = np.ceil(length[kick] / (prm.v_max * prm.dt)).astype(int)
                escapes[kick] += 1
                stuck &= ~kick
            status[stuck] = "stuck"
            active &= ~stuck
        if not active.any():
            break
        v = clip_speed(total_force(p, goal, obstacles, prm), prm.v_max)
        kicking = active & (esc_left > 0)
        v[kicking] = prm.v_max * esc_dir[kicking]
        p_new = p + prm.dt * v
        if kicking.any():
            too_close = kicking & (min_clearance(p_new, obstacles) < 0.1)
            p_new[too_close] = p[too_close]
            esc_left[too_close] = 0
            esc_left[kicking & ~too_close] -= 1
        p = np.where(active[:, None], p_new, p)
        steps[active] += 1
        hist.append(p.copy())
    return dict(status=status, final=p, steps=steps, escapes=escapes,
                history=np.array(hist) if keep_history else None)


def simulate(start, goal, obstacles, prm, escape=False, rng=None):
    """Run the controller from one start; returns path (T,2), status, steps."""
    res = simulate_many(np.asarray([start], float), goal, obstacles, prm,
                        escape=escape, rng=rng)
    path = res["history"][: res["steps"][0] + 1, 0]
    return dict(path=path, status=str(res["status"][0]), steps=int(res["steps"][0]),
                escapes=int(res["escapes"][0]), final=path[-1],
                min_clearance=float(min_clearance(path, obstacles).min()))


def follow_waypoints(start, waypoints, obstacles, prm, wp_tol=0.3):
    """APF as a local layer: descend towards each waypoint of a global path in
    turn (the last one with the normal goal tolerance).  Returns the joined
    path and the list of per-leg statuses."""
    pieces, statuses, p = [], [], np.asarray(start, float)
    for i, wp in enumerate(waypoints):
        leg = replace(prm, goal_tol=prm.goal_tol if i == len(waypoints) - 1 else wp_tol)
        res = simulate(p, wp, obstacles, leg)
        pieces.append(res["path"] if not pieces else res["path"][1:])
        statuses.append(res["status"])
        p = res["final"]
        if res["status"] != "reached":
            break
    return dict(path=np.vstack(pieces), statuses=statuses)


def simulate_swarm(starts, goals, obstacles, prm, k_agent=1.0, rho_agent=1.5,
                   r_agent=0.25, k_spring=0.0, d_spring=0.0, steps=1500):
    """Several drones, each attracted by its own goal and repelled by the
    obstacles and by every other drone (pairwise Khatib term with the
    clearance rho_ij = ||p_i - p_j|| - 2 r_agent).  With k_spring > 0 every
    pair is also joined by a spring of rest length d_spring (formation keeping).
    Returns history (T,N,2) and the smallest pairwise distance ever observed."""
    p = np.asarray(starts, float).copy()
    goals = np.asarray(goals, float)
    n = len(p)
    hist = [p.copy()]
    min_sep = np.inf
    eye = np.eye(n, dtype=bool)
    for _ in range(steps):
        f = np.stack([total_force(p[i], goals[i], obstacles, prm) for i in range(n)])
        diff = p[:, None, :] - p[None, :, :]                 # (N,N,2), i minus j
        dist = np.linalg.norm(diff, axis=-1)                 # (N,N)
        min_sep = min(min_sep, dist[~eye].min())
        unit = diff / np.maximum(dist, EPS)[..., None]
        rho = np.maximum(dist - 2.0 * r_agent, EPS)
        gain = k_agent * (1.0 / rho - 1.0 / rho_agent) / rho ** 2
        gain = np.where((rho < rho_agent) & ~eye, gain, 0.0)
        f += (gain[..., None] * unit).sum(axis=1)
        if k_spring > 0.0:
            pull = np.where(eye, 0.0, -k_spring * (dist - d_spring))
            f += (pull[..., None] * unit).sum(axis=1)
        p = p + prm.dt * clip_speed(f, prm.v_max)
        hist.append(p.copy())
    return dict(history=np.array(hist), min_separation=float(min_sep))


def lateral_reversals(path, x_range=(-np.inf, np.inf)):
    """Number of sign changes of the y-step along the path (x within x_range)."""
    path = np.asarray(path, float)
    dy = np.diff(path[:, 1])
    inside = (path[:-1, 0] >= x_range[0]) & (path[:-1, 0] <= x_range[1])
    s = np.sign(dy[inside & (np.abs(dy) > 1e-9)])
    return int(np.sum(s[1:] * s[:-1] < 0))


# ---------------------------------------------------------------- the scenes
GOAL = np.array([8.0, 4.0])
DISC = [Disc((4.0, 4.0), 1.0)]
POINTS = {"A": (0.5, 4.0), "B": (2.5, 4.0), "C": (3.0, 5.3)}


TRACE_STEPS = (0, 100, 200, 300, 500, 800, 1099)


def trace_rows(path, goal, obstacles, prm, steps=TRACE_STEPS):
    """Trace of a run: step k, position, clearance, force, clipped velocity and
    distance to the goal at the selected steps (the trace table of the text)."""
    out = []
    for k in steps:
        if k >= len(path):
            break
        q = np.asarray(path[k], float)
        f = total_force(q, goal, obstacles, prm)
        out.append(dict(k=k, p=q, rho=float(min_clearance(q, obstacles)), f=f,
                        f_norm=float(np.linalg.norm(f)), v=clip_speed(f, prm.v_max),
                        d=float(np.linalg.norm(q - goal))))
    return out


def worked_example(prm=None):
    """One obstacle, three probe points, and a trajectory from (0, 4.5)."""
    prm = ApfParams() if prm is None else prm
    rows = {}
    for name, q in POINTS.items():
        q = np.asarray(q, float)
        fa = attractive_force(q, GOAL, prm)
        fr = repulsive_force(q, GOAL, DISC, prm)
        rows[name] = dict(p=q, rho=float(DISC[0].distance(q)[0][0]), f_att=fa, f_rep=fr,
                          f=fa + fr, u=float(total_potential(q, GOAL, DISC, prm)))
    traj = simulate((0.0, 4.5), GOAL, DISC, prm)
    traj["trace"] = trace_rows(traj["path"], GOAL, DISC, prm)
    return rows, traj


def local_minimum_case(prm=None):
    """Obstacle exactly between start (0,4) and goal (8,4): forces cancel."""
    prm = ApfParams() if prm is None else prm
    res = simulate((0.0, 4.0), GOAL, DISC, prm)

    def fx(x):  # x-component of the force on the axis y = 4
        return float(total_force(np.array([x, 4.0]), GOAL, DISC, prm)[0])

    lo, hi = 1.5, 2.9                     # fx(lo) > 0 (towards goal), fx(hi) < 0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if fx(mid) > 0 else (lo, mid)
    fix = follow_waypoints((0.0, 4.0), [(3.0, 6.5), GOAL], DISC, prm)
    return dict(result=res, equilibrium_x=0.5 * (lo + hi), waypoint=fix)


def gnron_case(prm=None, goal=(5.4, 4.0), start=(8.0, 6.0)):
    """Goal 0.4 from the obstacle boundary: plain APF stops short, n = 2 arrives."""
    prm = ApfParams() if prm is None else prm
    plain = simulate(start, goal, DISC, prm)
    fixed = simulate(start, goal, DISC, replace(prm, n_gnron=2))
    return dict(plain=plain, fixed=fixed,
                d_plain=float(np.linalg.norm(plain["final"] - goal)),
                d_fixed=float(np.linalg.norm(fixed["final"] - goal)))


def corridor(gap, radius=1.0):
    """Two discs whose boundaries leave a vertical passage of width `gap`."""
    return [Disc((4.0, 4.0 - radius - gap / 2), radius), Disc((4.0, 4.0 + radius + gap / 2), radius)]


CORRIDOR_GOAL = np.array([8.0, 4.2])   # slightly off the axis, as in any real scene


def corridor_case(gap, dt, prm=None, v_max=1.0, start=(0.0, 4.3)):
    """Cross the passage from an off-axis start.  Reports the status, the
    number of lateral reversals and the largest lateral excursion inside the
    passage (3 < x < 5), and the stiffness of U at the passage midpoint."""
    prm = ApfParams() if prm is None else prm
    prm = replace(prm, dt=dt, v_max=v_max, stuck_window=max(10, int(round(1.0 / dt))))
    obs = corridor(gap)
    res = simulate(start, CORRIDOR_GOAL, obs, prm)
    path = res["path"]
    inside = path[(path[:, 0] > 3.0) & (path[:, 0] < 5.0)]
    amp = float(np.abs(inside[:, 1] - 4.0).max()) if len(inside) else float("nan")
    return dict(result=res, reversals=lateral_reversals(path, (3.0, 5.0)), amplitude=amp,
                stiffness=stiffness((4.0, 4.0), CORRIDOR_GOAL, obs, prm))


BASIN_OBS = [Disc((4.0, 3.2), 1.0), Disc((4.0, 5.0), 1.0)]
BASIN_GOAL = np.array([8.0, 4.1])


def basin_starts(nx=21, ny=21):
    xs, ys = np.linspace(0.0, 2.0, nx), np.linspace(0.5, 7.7, ny)
    return np.array([(x, y) for y in ys for x in xs])


def basin_experiment(escape=False, prm=None, seed=15):
    """441 starts in front of two overlapping discs (one peanut-shaped obstacle)."""
    prm = ApfParams() if prm is None else prm
    return simulate_many(basin_starts(), BASIN_GOAL, BASIN_OBS, prm, escape=escape,
                         rng=np.random.default_rng(seed))


# ---------------------------------------------------------------- self-test
def _self_test():
    t0 = time.time()
    prm = ApfParams()
    rng = np.random.default_rng(1)

    # 1. analytic forces equal -grad U (plain, GNRON n=1,2, hybrid attractive)
    scene = [Disc((4.0, 4.0), 1.0), Disc((6.0, 6.5), 0.7)]
    for variant in (prm, replace(prm, n_gnron=1), replace(prm, n_gnron=2),
                    replace(prm, d_star=2.0), replace(prm, d_star=1.0, n_gnron=2)):
        for _ in range(40):
            q = rng.uniform(0.0, 9.0, 2)
            if min_clearance(q, scene) < 0.05 or np.linalg.norm(q - GOAL) < 0.05:
                continue
            fa, fn = total_force(q, GOAL, scene, variant), numerical_force(q, GOAL, scene, variant)
            assert np.allclose(fa, fn, rtol=1e-5, atol=1e-5), (variant, q, fa, fn)
    # hybrid attractive force is continuous at d*, conic beyond it
    hyb = replace(prm, d_star=2.0)
    for q in ((6.0, 4.0), (10.0, 4.0), (8.0, 9.0)):
        f = attractive_force(np.array(q), GOAL, hyb)
        assert abs(np.linalg.norm(f) - 2.0) < 1e-9, f
    assert abs(attractive_potential(np.array([6.0, 4.0]), GOAL, hyb) - 2.0) < 1e-12
    assert abs(attractive_potential(np.array([10.0, 4.0]), GOAL, hyb) - 2.0) < 1e-12

    # 2. worked example: hand-computed values at A and B
    rows, traj = worked_example(prm)
    assert np.allclose(rows["A"]["f_att"], [7.5, 0.0]) and np.allclose(rows["A"]["f_rep"], [0.0, 0.0])
    assert np.allclose(rows["B"]["f_att"], [5.5, 0.0]) and np.allclose(rows["B"]["f_rep"], [-6.0, 0.0])
    assert np.allclose(rows["B"]["f"], [-0.5, 0.0])
    assert rows["C"]["f"][1] > 0.0 and rows["C"]["f"][0] > 0.0   # deflected upwards
    assert traj["status"] == "reached" and traj["min_clearance"] > 0.2, traj["status"]
    # the hybrid attraction (conic beyond d* = 2) keeps a larger clearance
    hyb_run = simulate((0.0, 4.5), GOAL, DISC, replace(prm, d_star=2.0))
    assert hyb_run["status"] == "reached" and hyb_run["min_clearance"] > traj["min_clearance"]
    # the speed limit binds while the drone is far from the goal and releases near it
    trace = traj["trace"]
    assert abs(np.linalg.norm(trace[0]["v"]) - prm.v_max) < 1e-9, trace[0]["v"]
    assert trace[-1]["f_norm"] < prm.v_max and trace[-1]["d"] <= prm.goal_tol

    # 3. local minimum on the axis is detected, at the root of F_x = 0
    lm = local_minimum_case(prm)
    assert lm["result"]["status"] == "stuck", lm["result"]["status"]
    assert abs(lm["result"]["final"][0] - lm["equilibrium_x"]) < 0.02
    assert abs(lm["result"]["final"][1] - 4.0) < 1e-6
    assert lm["waypoint"]["statuses"] == ["reached", "reached"]

    # 4. GNRON: plain repulsion stops short of a goal near an obstacle, n=2 arrives
    g = gnron_case(prm)
    assert g["plain"]["status"] == "stuck" and g["d_plain"] > 0.3, (g["plain"]["status"], g["d_plain"])
    assert g["fixed"]["status"] == "reached" and g["d_fixed"] <= prm.goal_tol
    # with n = 2 the goal is the global minimum of U and a stationary point
    fixed = replace(prm, n_gnron=2)
    goal = np.array([5.4, 4.0])
    assert np.allclose(total_force(goal, goal, DISC, fixed), 0.0)
    assert abs(total_potential(goal, goal, DISC, fixed)) < 1e-12
    assert np.all(total_potential(rng.uniform(0, 9, (200, 2)), goal, DISC, fixed) >= 0.0)

    # 4b. below the chatter amplitude dt*v_max the n = 1 correction never settles
    tight = replace(prm, goal_tol=1e-3)
    chat = simulate((8.0, 6.0), goal, DISC, replace(tight, n_gnron=1))
    fine = simulate((8.0, 6.0), goal, DISC, replace(tight, n_gnron=2))
    assert chat["status"] == "stuck" and fine["status"] == "reached", chat["status"]
    chat_d = np.linalg.norm(chat["path"][-100:] - goal, axis=1)
    assert chat_d.max() < prm.goal_tol and chat_d.max() < 2.0 * prm.dt * prm.v_max, chat_d.max()

    # 4c. inside the blocked gap of section "no passage" the force points at the goal
    gap_in = simulate((4.0, 4.0), CORRIDOR_GOAL, corridor(0.6), prm)
    assert gap_in["status"] == "reached" and gap_in["min_clearance"] > 0.29
    assert total_force(np.array([4.0, 4.0]), CORRIDOR_GOAL, corridor(0.6), prm)[0] > 0.0

    # 5. corridor: dt*stiffness < 2 crosses smoothly; beyond it the explicit
    #    update zigzags (no speed limit) or, with a larger dt, hits the wall
    smooth = corridor_case(1.0, 0.01, prm)
    zig = corridor_case(1.0, 0.05, prm, v_max=np.inf)
    crash = corridor_case(1.0, 0.10, prm, v_max=np.inf)
    assert smooth["result"]["status"] == "reached" and smooth["reversals"] <= 2, smooth["reversals"]
    assert zig["result"]["status"] == "reached" and zig["reversals"] >= smooth["reversals"] + 5
    assert zig["amplitude"] > 2.0 * smooth["amplitude"], (zig["amplitude"], smooth["amplitude"])
    assert crash["result"]["status"] == "collision", crash["result"]["status"]
    assert 0.01 * smooth["stiffness"] < 2.0 < 0.05 * zig["stiffness"]

    # 6. no passage: the 0.6-wide gap is free, but the drone stops in front of it
    block = corridor_case(0.6, 0.01, prm)
    assert block["result"]["status"] == "stuck" and block["result"]["final"][0] < 4.0
    axis = np.array([(x, 4.0) for x in np.linspace(3.0, 5.0, 41)])
    assert min_clearance(axis, corridor(0.6)).min() > 0.29

    # 7. basin experiment: some starts are trapped; random-walk escapes free them
    plain = basin_experiment(escape=False, prm=prm)
    walk = basin_experiment(escape=True, prm=prm)
    share_plain = np.mean(plain["status"] == "reached")
    share_walk = np.mean(walk["status"] == "reached")
    assert 0.3 < share_plain < 0.95 and share_walk > share_plain + 0.2, (share_plain, share_walk)
    assert not np.any(plain["status"] == "collision") and not np.any(walk["status"] == "collision")

    # 8. explicit Euler on the quadratic bowl: k dt < 1 monotone, 1 < k dt < 2 alternating
    free = replace(prm, v_max=1e9, max_steps=60, stuck_window=10 ** 6)
    for dt, alternating in ((0.5, False), (1.5, True)):
        path = simulate((1.0, 0.0), (0.0, 0.0), [], replace(free, dt=dt))["path"]
        x = path[:, 0]
        assert np.all(np.abs(x[1:]) < np.abs(x[:-1]) + 1e-12)
        assert (np.any(x[1:] < 0) == alternating)

    # 9. swarm: six drones swapping places through the centre of a circle
    ang = np.linspace(0.0, 2 * np.pi, 6, endpoint=False)
    ring = np.stack([3 * np.cos(ang), 3 * np.sin(ang)], axis=1)
    with_rep = simulate_swarm(ring, -ring, [], replace(prm, dt=0.02), k_agent=1.0)
    without = simulate_swarm(ring, -ring, [], replace(prm, dt=0.02), k_agent=0.0)
    assert with_rep["min_separation"] > 0.5 > without["min_separation"], (
        with_rep["min_separation"], without["min_separation"])
    end = with_rep["history"][-1]
    assert np.all(np.linalg.norm(end + ring, axis=1) < 0.3)

    print("self-test passed in %.1f s" % (time.time() - t0))
    print("worked example (k_att=1, k_rep=1, rho0=2, goal (8,4), disc (4,4) r=1):")
    for name, r in rows.items():
        print("  %s p=%s rho=%.3f F_att=%s F_rep=%s F=%s |F|=%.3f U=%.3f" % (
            name, r["p"], r["rho"], np.round(r["f_att"], 3), np.round(r["f_rep"], 3),
            np.round(r["f"], 3), np.linalg.norm(r["f"]), r["u"]))
    print("  trace of the run from (0,4.5): k, p, rho, F, |F|, clipped v, d")
    for r in traj["trace"]:
        print("   %4d (%.3f,%.3f) %.3f (%.3f,%.3f) %.3f (%.3f,%.3f) %.3f" % (
            r["k"], r["p"][0], r["p"][1], r["rho"], r["f"][0], r["f"][1], r["f_norm"],
            r["v"][0], r["v"][1], r["d"]))
    print("  trajectory from (0,4.5): %s after %d steps, min clearance %.3f" % (
        traj["status"], traj["steps"], traj["min_clearance"]))
    print("  the same with the hybrid attraction d*=2: %s after %d steps, min clearance %.3f" % (
        hyb_run["status"], hyb_run["steps"], hyb_run["min_clearance"]))
    print("local minimum: stuck at x=%.4f after %d steps; root of F_x=0 at x=%.4f" % (
        lm["result"]["final"][0], lm["result"]["steps"], lm["equilibrium_x"]))
    print("GNRON: plain stops %.3f from the goal (%s, %d steps); n=2 %s in %d steps" % (
        g["d_plain"], g["plain"]["status"], g["plain"]["steps"], g["fixed"]["status"], g["fixed"]["steps"]))
    print("GNRON with goal_tol=1e-3: n=1 %s after %d steps (chatter <= %.4f); n=2 %s in %d steps" % (
        chat["status"], chat["steps"], chat_d.max(), fine["status"], fine["steps"]))
    print("started inside the 0.6 gap at (4,4): %s after %d steps, min clearance %.3f" % (
        gap_in["status"], gap_in["steps"], gap_in["min_clearance"]))
    print("corridor (v_max=1) gap/dt/status/steps/reversals/amplitude/stiffness/dt*stiffness:")
    for gap in (0.6, 0.8, 1.0, 1.2, 1.6):
        for dt in (0.01, 0.05):
            c = corridor_case(gap, dt, prm)
            print("  %.1f %.2f %-9s %5d %4d %.3f %8.1f %6.2f" % (
                gap, dt, c["result"]["status"], c["result"]["steps"], c["reversals"],
                c["amplitude"], c["stiffness"], dt * c["stiffness"]))
    for name, c in (("smooth dt=0.01 v_max=1", smooth), ("zigzag dt=0.05 no limit", zig),
                    ("crash dt=0.10 no limit", crash)):
        print("  %s: %s after %d steps, %d reversals, amplitude %.3f, min clearance %.3f" % (
            name, c["result"]["status"], c["result"]["steps"], c["reversals"], c["amplitude"],
            c["result"]["min_clearance"]))
    print("basin: plain %.1f%% reached, %.1f%% stuck; with random walk %.1f%% reached" % (
        100 * share_plain, 100 * np.mean(plain["status"] == "stuck"), 100 * share_walk))
    ok, ok_plain = walk["status"] == "reached", plain["status"] == "reached"
    print("  escapes: %.3f per drone that arrives, %.3f averaged over all %d starts;"
          " steps %.1f with escapes against %.1f plain" % (
              walk["escapes"][ok].mean(), walk["escapes"].mean(), len(ok),
              walk["steps"][ok].mean(), plain["steps"][ok_plain].mean()))
    print("swarm min separation: with repulsion %.3f, without %.3f" % (
        with_rep["min_separation"], without["min_separation"]))


if __name__ == "__main__":
    _self_test()
