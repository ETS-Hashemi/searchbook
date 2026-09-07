"""Chapter 14 -- The Dynamic Window Approach (DWA).

A complete DWA controller for a velocity-controlled drone (holonomic, 2D or
3D, per-axis acceleration limits) plus the circular-arc rollout of the
original differential-drive formulation (Fox, Burgard and Thrun, 1997).

Contents
    Disc, Box, free_distance          obstacles and analytic ray casting
    DwaParams                         all parameters of the controller
    dynamic_window, window_candidates the velocity grid over the window
    admissible_speed, evaluate        braking test and the three-term score
    dwa_command                       one control step (arg max of G)
    rollout, rollout_free_distance    sampled straight-line rollouts
    diffdrive_rollout, ...            circular arcs for (v, omega)
    simulate                          closed-loop simulator with metrics
    worked_example, scenes            the instances used in the chapter

Coordinates: positions and velocities are NumPy arrays of length 2 or 3.
Distances in metres, speeds in m/s, accelerations in m/s^2, times in s.

Run:  python3 code/ch14_dwa.py     (self-test, takes about a second)
"""
from __future__ import annotations

import math
import time
from dataclasses import dataclass, field

import numpy as np


# ----------------------------------------------------------------------
# Obstacles and ray casting in the inflated configuration space
# ----------------------------------------------------------------------
@dataclass
class Disc:
    """A disc (2D) or ball (3D); `velocity` is set for moving obstacles."""
    centre: np.ndarray
    radius: float
    velocity: np.ndarray | None = None


@dataclass
class Box:
    """An axis-aligned box with corners lo <= hi (static)."""
    lo: np.ndarray
    hi: np.ndarray


def ray_disc(p, d, centre, radius):
    """Distance along the unit ray p + t*d to the disc surface, or inf."""
    m = p - centre
    b = float(np.dot(m, d))
    c = float(np.dot(m, m)) - radius * radius
    if c <= 0.0:
        return 0.0  # the ray starts inside the disc
    disc = b * b - c
    if b > 0.0 or disc < 0.0:
        return math.inf
    return -b - math.sqrt(disc)


def ray_box(p, d, lo, hi):
    """Slab test: distance along the unit ray to the box, or inf."""
    t0, t1 = 0.0, math.inf
    for k in range(len(p)):
        if abs(d[k]) < 1e-12:
            if p[k] < lo[k] or p[k] > hi[k]:
                return math.inf
            continue
        a = (lo[k] - p[k]) / d[k]
        b = (hi[k] - p[k]) / d[k]
        t0, t1 = max(t0, min(a, b)), min(t1, max(a, b))
        if t0 > t1:
            return math.inf
    return t0


def free_distance(p, d, obstacles, radius, d_max, v=None):
    """Free distance from p along the unit direction d, capped at d_max.

    Obstacles are inflated by the robot radius (boxes are inflated as
    boxes, a conservative approximation of the Minkowski sum).  If the
    robot velocity v is given, moving discs are handled in the relative
    frame: the collision time follows from the relative velocity v - u
    and the free distance is the robot's own travel until that time.
    """
    best = d_max
    for ob in obstacles:
        if isinstance(ob, Box):
            t = ray_box(p, d, ob.lo - radius, ob.hi + radius)
        elif v is None or ob.velocity is None:
            t = ray_disc(p, d, ob.centre, ob.radius + radius)
        else:
            rel = v - ob.velocity
            speed_rel = float(np.linalg.norm(rel))
            if speed_rel < 1e-9:
                continue
            t_rel = ray_disc(p, rel / speed_rel, ob.centre, ob.radius + radius)
            t = float(np.linalg.norm(v)) * t_rel / speed_rel
        best = min(best, t)
    return best


def clearance_at(p, obstacles, radius):
    """Signed distance from p to the nearest inflated obstacle surface."""
    best = math.inf
    for ob in obstacles:
        if isinstance(ob, Disc):
            best = min(best, float(np.linalg.norm(p - ob.centre)) - ob.radius - radius)
        else:
            gap = np.maximum(np.maximum(ob.lo - p, p - ob.hi), 0.0)
            best = min(best, float(np.linalg.norm(gap)) - radius)
    return best


# ----------------------------------------------------------------------
# The controller
# ----------------------------------------------------------------------
@dataclass
class DwaParams:
    """Parameters of the drone DWA (units: m, s)."""
    v_max: float = 2.0        # speed limit: V_s is the ball of radius v_max
    a_max: float = 2.0        # acceleration limit per axis (dynamic window)
    a_brake: float = 2.0      # braking deceleration (admissibility test)
    dt: float = 0.25          # control interval
    horizon: float = 1.0      # rollout horizon for trajectory prediction
    v_res: float = 0.25       # resolution of the velocity grid
    d_max: float = 3.0        # distances are capped here (sensor range)
    radius: float = 0.2       # drone radius (obstacle inflation)
    weights: tuple = (0.6, 0.2, 0.2)   # alpha, beta, gamma
    goal_tol: float = 0.2     # the goal counts as reached inside this radius
    brake_for_goal: bool = True   # also brake for the goal, not only for obstacles
    hysteresis: float = 0.0   # keep the old command unless the best beats it by this
    smooth: bool = False      # the sigma of Fox et al.: average G over neighbours


def dynamic_window(v_a, prm):
    """Bounds [lo, hi] of the velocities reachable within one interval."""
    lo = np.maximum(v_a - prm.a_max * prm.dt, -prm.v_max)
    hi = np.minimum(v_a + prm.a_max * prm.dt, prm.v_max)
    return lo, hi


def braking_candidate(v_a, prm):
    """The command 'keep the direction, brake with a_brake for one interval'.

    It always lies in the dynamic window (a_brake <= a_max) and is added
    to the candidate set so that a safe command is always available.
    """
    speed = float(np.linalg.norm(v_a))
    if speed <= prm.a_brake * prm.dt:
        return np.zeros_like(v_a)
    return v_a * (1.0 - prm.a_brake * prm.dt / speed)


def window_candidates(v_a, prm):
    """Velocity grid over the dynamic window, intersected with V_s, plus
    the braking candidate (appended if it is not a grid point already)."""
    lo, hi = dynamic_window(v_a, prm)
    n = int(round(prm.a_max * prm.dt / prm.v_res))
    axes = [v_a[k] + prm.v_res * np.arange(-n, n + 1) for k in range(len(v_a))]
    grid = np.array(np.meshgrid(*axes, indexing="ij")).reshape(len(v_a), -1).T
    inside = np.all((grid >= lo - 1e-9) & (grid <= hi + 1e-9), axis=1)
    grid = grid[inside]
    grid = grid[np.linalg.norm(grid, axis=1) <= prm.v_max + 1e-9]
    v_b = braking_candidate(v_a, prm)
    if not np.any(np.all(np.abs(grid - v_b) < 1e-9, axis=1)):
        grid = np.vstack([grid, v_b])
    return grid


def braking_distance(speed, a_brake, dt=0.0):
    """Distance travelled before standing still: the command is held for
    dt (dt = 0 gives the continuous formula v^2 / (2 a) of Fox et al.),
    then the robot decelerates with a_brake."""
    return speed * dt + speed * speed / (2.0 * a_brake)


def admissible_speed(dist, a_brake, dt=0.0):
    """Largest speed whose braking distance fits into dist (inverse of
    braking_distance): the positive root of v^2/(2a) + v dt = dist."""
    dist = max(dist, 0.0)
    return -a_brake * dt + math.sqrt(a_brake * a_brake * dt * dt + 2.0 * a_brake * dist)


def heading_term(p, v, target, prm):
    """1 - theta/pi, theta = angle between v and the target direction seen
    from the predicted position p + v*dt.  Zero for the zero velocity."""
    speed = float(np.linalg.norm(v))
    if speed < 1e-9:
        return 0.0
    to_target = target - (p + v * prm.dt)
    dist = float(np.linalg.norm(to_target))
    if dist < 1e-9:
        return 1.0
    cos = float(np.dot(v, to_target)) / (speed * dist)
    return 1.0 - math.acos(max(-1.0, min(1.0, cos))) / math.pi


@dataclass
class Candidate:
    v: np.ndarray
    dist: float          # free distance along the rollout (capped at d_max)
    admissible: bool
    heading: float
    clearance: float
    velocity: float
    score: float


def evaluate(p, v_a, obstacles, target, prm, goal=None):
    """Score every candidate of the window; returns a list of Candidate."""
    alpha, beta, gamma = prm.weights
    out = []
    for v in window_candidates(v_a, prm):
        speed = float(np.linalg.norm(v))
        if speed < 1e-9:
            dist = prm.d_max          # standing still never hits a static obstacle
        else:
            dist = free_distance(p, v / speed, obstacles, prm.radius, prm.d_max, v)
        adm = speed <= admissible_speed(dist, prm.a_brake, prm.dt) + 1e-9
        if prm.brake_for_goal and goal is not None:
            d_goal = float(np.linalg.norm(goal - p))
            adm = adm and speed <= admissible_speed(d_goal, prm.a_brake, prm.dt) + 1e-9
        h = heading_term(p, v, target, prm)
        c = min(dist, prm.d_max) / prm.d_max
        s = speed / prm.v_max
        g = alpha * h + beta * c + gamma * s if adm else 0.0
        out.append(Candidate(v, dist, adm, h, c, s, g))
    if prm.smooth:
        _smooth_scores(out, prm)
    return out


def _smooth_scores(cands, prm):
    """The sigma of Fox et al.: replace G by its mean over the grid
    neighbours (inadmissible neighbours count as zero)."""
    vs = np.array([c.v for c in cands])
    raw = np.array([c.score for c in cands])
    for i, c in enumerate(cands):
        near = np.all(np.abs(vs - vs[i]) <= prm.v_res + 1e-9, axis=1)
        c.score = float(raw[near].mean()) if c.admissible else 0.0


def dwa_command(p, v_a, obstacles, target, prm, goal=None):
    """One DWA step: the admissible window velocity with the largest G.

    Returns (v_best, candidates).  If no candidate is admissible (which
    cannot happen with static obstacles, see Theorem 14.x) the braking
    candidate is returned (emergency braking).  With hysteresis the
    current velocity v_a is kept unless the best candidate beats its
    score by more than prm.hysteresis.
    """
    cands = evaluate(p, v_a, obstacles, target, prm, goal)
    adm = [c for c in cands if c.admissible]
    if not adm:
        return braking_candidate(v_a, prm), cands
    best = max(adm, key=lambda c: c.score)
    if prm.hysteresis > 0.0:
        for c in adm:
            if np.allclose(c.v, v_a) and c.score >= best.score - prm.hysteresis:
                return c.v, cands
    return best.v, cands


# ----------------------------------------------------------------------
# Rollouts: straight segments (drone) and circular arcs (differential drive)
# ----------------------------------------------------------------------
def rollout(p, v, horizon, n=10):
    """Predicted positions p + v*t for t = 0, T/n, ..., T (a straight line)."""
    ts = np.linspace(0.0, horizon, n + 1)
    return p[None, :] + ts[:, None] * v[None, :]


def rollout_free_distance(p, v, obstacles, radius, d_max, ds=0.02):
    """Free distance measured by stepping along the rollout in steps of ds.

    This is the generic 'simulate and check' version of free_distance: it
    is slower but works for any motion model and any obstacle shape.
    """
    speed = float(np.linalg.norm(v))
    if speed < 1e-9:
        return d_max
    d = v / speed
    s = 0.0
    while s < d_max:
        if clearance_at(p + s * d, obstacles, radius) <= 0.0:
            return s
        s += ds
    return d_max


def diffdrive_rollout(pose, v, omega, horizon, n=20):
    """Arc of a differential-drive robot: rows (x, y, theta) for t in [0, T].

    With omega = 0 the arc degenerates to a straight segment; otherwise the
    robot moves on a circle of radius v / omega.
    """
    x, y, th = pose
    ts = np.linspace(0.0, horizon, n + 1)
    if abs(omega) < 1e-9:
        xs = x + v * ts * math.cos(th)
        ys = y + v * ts * math.sin(th)
        ths = np.full_like(ts, th)
    else:
        r = v / omega
        ths = th + omega * ts
        xs = x + r * (np.sin(ths) - math.sin(th))
        ys = y - r * (np.cos(ths) - math.cos(th))
    return np.column_stack([xs, ys, ths])


def diffdrive_window(v, omega, dv_max, dw_max, dt, v_max, w_max):
    """The dynamic window [v -/+ dv dt] x [omega -/+ dw dt] of Fox et al."""
    return ((max(v - dv_max * dt, 0.0), min(v + dv_max * dt, v_max)),
            (max(omega - dw_max * dt, -w_max), min(omega + dw_max * dt, w_max)))


def diffdrive_free_distance(pose, v, omega, obstacles, radius, d_max, ds=0.02):
    """Distance travelled on the arc of (v, omega) before the first contact."""
    if v < 1e-9:
        return d_max
    n = int(math.ceil(d_max / ds))
    arc = diffdrive_rollout(pose, v, omega, d_max / v, n)
    for k in range(n + 1):
        if clearance_at(arc[k, :2], obstacles, radius) <= 0.0:
            return k * ds
    return d_max


# ----------------------------------------------------------------------
# Closed-loop simulation
# ----------------------------------------------------------------------
def lookahead_point(p, waypoints, lookahead):
    """Point on the polyline `waypoints` at arc length `lookahead` beyond
    the point of the polyline closest to p (a 'carrot' for the heading)."""
    best_d, best_i, best_t = math.inf, 0, 0.0
    for i in range(len(waypoints) - 1):
        a, b = waypoints[i], waypoints[i + 1]
        seg = b - a
        length2 = float(np.dot(seg, seg))
        t = 0.0 if length2 < 1e-12 else min(1.0, max(0.0, float(np.dot(p - a, seg)) / length2))
        d = float(np.linalg.norm(a + t * seg - p))
        if d < best_d:
            best_d, best_i, best_t = d, i, t
    remaining = lookahead
    a = waypoints[best_i] + best_t * (waypoints[best_i + 1] - waypoints[best_i])
    for i in range(best_i, len(waypoints) - 1):
        b = waypoints[i + 1]
        seg_len = float(np.linalg.norm(b - a))
        if seg_len >= remaining:
            return a + (b - a) * (remaining / seg_len)
        remaining -= seg_len
        a = b
    return waypoints[-1]


def simulate(p0, v0, goal, obstacles, prm, max_steps=200, waypoints=None,
             lookahead=1.0):
    """Run DWA in closed loop until the goal is reached, a collision occurs
    or max_steps elapse.  Moving discs advance by their velocity each step.

    Returns a dict with the trajectory (positions), the commands, and the
    metrics used in the chapter: reached, collided, steps, path_length,
    min_clearance, mean_speed.
    """
    p, v = np.array(p0, dtype=float), np.array(v0, dtype=float)
    goal = np.array(goal, dtype=float)
    traj, cmds = [p.copy()], []
    reached = collided = False
    min_clear = clearance_at(p, obstacles, prm.radius)
    for _ in range(max_steps):
        target = goal if waypoints is None else lookahead_point(p, waypoints, lookahead)
        v, _ = dwa_command(p, v, obstacles, target, prm, goal)
        p = p + v * prm.dt
        for ob in obstacles:
            if isinstance(ob, Disc) and ob.velocity is not None:
                ob.centre = ob.centre + ob.velocity * prm.dt
        traj.append(p.copy())
        cmds.append(v.copy())
        min_clear = min(min_clear, clearance_at(p, obstacles, prm.radius))
        if min_clear <= 0.0:
            collided = True
            break
        if float(np.linalg.norm(p - goal)) <= prm.goal_tol:
            reached = True
            break
    traj = np.array(traj)
    steps = len(cmds)
    length = float(np.sum(np.linalg.norm(np.diff(traj, axis=0), axis=1)))
    return dict(traj=traj, cmds=np.array(cmds) if cmds else np.zeros((0, len(p))),
                reached=reached, collided=collided, steps=steps,
                path_length=length, min_clearance=min_clear,
                mean_speed=length / (steps * prm.dt) if steps else 0.0)


# ----------------------------------------------------------------------
# Instances used in the chapter
# ----------------------------------------------------------------------
def worked_example():
    """The instance of the worked example: a drone at the origin flying at
    (1, 0) m/s towards the goal (5, 0) with a disc obstacle ahead."""
    prm = DwaParams()
    p = np.array([0.0, 0.0])
    v_a = np.array([1.0, 0.0])
    goal = np.array([5.0, 0.0])
    obstacles = [Disc(np.array([1.2, -0.1]), 0.4)]
    return p, v_a, goal, obstacles, prm


def corridor_scene():
    """A 4 m corridor of half-width 1 m with a pillar in it."""
    obstacles = [Box(np.array([1.0, 1.0]), np.array([5.0, 1.4])),
                 Box(np.array([1.0, -1.4]), np.array([5.0, -1.0])),
                 Disc(np.array([3.0, 0.2]), 0.2)]
    return np.array([0.0, 0.0]), np.array([0.0, 0.0]), np.array([6.0, 0.0]), obstacles


def utrap_scene():
    """A U-shaped obstacle opening towards the drone; the goal is behind it."""
    obstacles = [Box(np.array([5.0, -2.0]), np.array([5.4, 2.0])),
                 Box(np.array([3.0, 1.6]), np.array([5.4, 2.0])),
                 Box(np.array([3.0, -2.0]), np.array([5.4, -1.6]))]
    return np.array([0.0, 0.0]), np.array([0.0, 0.0]), np.array([7.0, 0.0]), obstacles


UTRAP_WAYPOINTS = np.array([[0.0, 0.0], [2.0, 2.8], [6.4, 2.8], [7.0, 0.0]])

WEIGHT_SETTINGS = {
    "heading": (0.8, 0.1, 0.1),
    "clearance": (0.2, 0.6, 0.2),
    "velocity": (0.2, 0.2, 0.6),
}


def moving_obstacle_scene():
    """An intruder crossing the drone's path from the left at 1.5 m/s."""
    obstacles = [Disc(np.array([3.5, 3.0]), 0.3, np.array([0.0, -1.5]))]
    return np.array([0.0, 0.0]), np.array([1.0, 0.0]), np.array([7.0, 0.0]), obstacles


# ----------------------------------------------------------------------
# Self-test
# ----------------------------------------------------------------------
def _check_window_and_admissibility(p, v_a, v, obstacles, prm):
    lo, hi = dynamic_window(v_a, prm)
    assert np.all(v >= lo - 1e-9) and np.all(v <= hi + 1e-9), "command outside the window"
    assert np.linalg.norm(v) <= prm.v_max + 1e-9, "command faster than v_max"
    speed = float(np.linalg.norm(v))
    if speed > 1e-9:
        dist = free_distance(p, v / speed, obstacles, prm.radius, prm.d_max, v)
        assert speed <= admissible_speed(dist, prm.a_brake, prm.dt) + 1e-9, "command not admissible"


def _self_test():
    t0 = time.time()
    rng = np.random.default_rng(14)

    # 1. Ray casting agrees with the sampled rollout on random disc scenes;
    #    with boxes the ray cast is conservative (inflated corners).
    for _ in range(50):
        obstacles = [Disc(rng.uniform(-3, 3, 2), rng.uniform(0.2, 0.8)) for _ in range(3)]
        p = rng.uniform(-3, 3, 2)
        if clearance_at(p, obstacles, 0.2) <= 0.0:
            continue
        v = rng.uniform(-1, 1, 2)
        d_ray = free_distance(p, v / np.linalg.norm(v), obstacles, 0.2, 4.0)
        d_roll = rollout_free_distance(p, v, obstacles, 0.2, 4.0, ds=0.005)
        assert abs(d_ray - d_roll) <= 0.011, (d_ray, d_roll)
        obstacles.append(Box(np.array([1.0, 1.0]), np.array([2.0, 2.5])))
        if clearance_at(p, obstacles, 0.2) <= 0.0:
            continue
        d_ray = free_distance(p, v / np.linalg.norm(v), obstacles, 0.2, 4.0)
        d_roll = rollout_free_distance(p, v, obstacles, 0.2, 4.0, ds=0.005)
        assert d_ray <= d_roll + 0.011, (d_ray, d_roll)

    # 2. The worked example: the chosen command, the window, admissibility.
    p, v_a, goal, obstacles, prm = worked_example()
    v, cands = dwa_command(p, v_a, obstacles, goal, prm, goal)
    _check_window_and_admissibility(p, v_a, v, obstacles, prm)
    assert len(cands) == 25 and sum(c.admissible for c in cands) == 16
    assert np.allclose(v, [1.0, 0.5]), v
    straight = free_distance(p, np.array([1.0, 0.0]), obstacles, prm.radius, prm.d_max)
    assert abs(straight - (1.2 - math.sqrt(0.6 ** 2 - 0.1 ** 2))) < 1e-9
    assert abs(admissible_speed(straight, prm.a_brake) - 2.0 * math.sqrt(straight)) < 1e-12
    v_disc = admissible_speed(straight, prm.a_brake, prm.dt)
    assert abs(braking_distance(v_disc, prm.a_brake, prm.dt) - straight) < 1e-9
    assert 1.0 <= v_disc < 1.25, v_disc    # (1, 0) admissible, (1.25, 0) not
    # the closed loop from the worked example passes the obstacle and arrives
    run = simulate(p, v_a, goal, obstacles, prm, max_steps=60)
    assert run["reached"] and not run["collided"], run["steps"]
    assert run["steps"] == 13, run["steps"]
    print("worked example: chosen command", v, "reached goal after",
          run["steps"], "steps, min clearance %.3f m" % run["min_clearance"])

    # 3. Every command of every closed-loop run lies in the window and is
    #    admissible (checked inside the loop of several scenes).
    for scene in (corridor_scene, utrap_scene):
        p, v0, goal, obstacles = scene()
        prm = DwaParams()
        p, v = p.copy(), v0.copy()
        for _ in range(120):
            v_new, _ = dwa_command(p, v, obstacles, goal, prm, goal)
            _check_window_and_admissibility(p, v, v_new, obstacles, prm)
            p, v = p + v_new * prm.dt, v_new
            if np.linalg.norm(p - goal) <= prm.goal_tol:
                break

    # 4. Open field: the goal is reached without collision, in 2D and 3D.
    for dim in (2, 3):
        prm = DwaParams()
        goal = np.array([6.0, 1.0, -1.0][:dim])
        obstacles = [Disc(np.array([3.0, 0.6, -0.4][:dim]), 0.5)]
        run = simulate(np.zeros(dim), np.zeros(dim), goal, obstacles, prm, max_steps=100)
        assert run["reached"] and not run["collided"], (dim, run["steps"])
        assert run["min_clearance"] > 0.0
        print("open field %dD: reached in %d steps, length %.2f m, min clearance %.2f m"
              % (dim, run["steps"], run["path_length"], run["min_clearance"]))

    # 5. Corridor: reached with the default weights; U-trap: reproducibly NOT
    #    reached (the documented failure), no collision, drone stuck inside
    #    the U (300 steps = 75 s of oscillation between the arms).
    p, v0, goal, obstacles = corridor_scene()
    run = simulate(p, v0, goal, obstacles, DwaParams(), max_steps=200)
    assert run["reached"] and not run["collided"], run["steps"]
    print("corridor: reached in %d steps, min clearance %.2f m" % (run["steps"], run["min_clearance"]))
    p, v0, goal, obstacles = utrap_scene()
    run = simulate(p, v0, goal, obstacles, DwaParams(), max_steps=300)
    assert not run["reached"] and not run["collided"], "the U-trap should trap the drone"
    end = run["traj"][-1]
    assert 3.0 <= end[0] <= 5.0 and abs(end[1]) <= 1.6, end
    print("U-trap: NOT reached (expected), final position (%.2f, %.2f), final speed %.2f m/s"
          % (end[0], end[1], np.linalg.norm(run["cmds"][-1])))
    # remedy: the heading term follows a global path around the U
    p, v0, goal, obstacles = utrap_scene()
    run = simulate(p, v0, goal, obstacles, DwaParams(), max_steps=300,
                   waypoints=UTRAP_WAYPOINTS, lookahead=1.0)
    assert run["reached"] and not run["collided"], run["steps"]
    print("U-trap with global path: reached in %d steps, length %.2f m"
          % (run["steps"], run["path_length"]))

    # 6. Differential drive: the arc of (v, omega) has radius v/omega and its
    #    end point matches the closed form; omega = 0 is a straight segment.
    arc = diffdrive_rollout((0.0, 0.0, 0.0), 1.0, 0.5, 2.0, n=40)
    r = 1.0 / 0.5
    assert np.allclose(arc[-1], [r * math.sin(1.0), r * (1 - math.cos(1.0)), 1.0])
    assert np.allclose(np.hypot(arc[:, 0], arc[:, 1] - r), r)
    seg = diffdrive_rollout((1.0, 2.0, math.pi / 2), 1.0, 0.0, 2.0)
    assert np.allclose(seg[-1], [1.0, 4.0, math.pi / 2])
    obstacles = [Disc(np.array([2.0, 0.0]), 0.3)]
    d_arc = diffdrive_free_distance((0.0, 0.0, 0.0), 1.0, 0.0, obstacles, 0.2, 4.0, ds=0.005)
    assert abs(d_arc - 1.5) <= 0.011, d_arc
    lo, hi = diffdrive_window(0.5, 0.0, 0.5, 1.0, 0.25, 1.0, 2.0)
    assert lo == (0.375, 0.625) and hi == (-0.25, 0.25)

    # 7. Moving obstacle: treating the intruder as static during the
    #    rollout ends in a collision; the relative-velocity rollout does not.
    p, v0, goal, obstacles = moving_obstacle_scene()
    static_view = [Disc(obstacles[0].centre.copy(), obstacles[0].radius)]
    # A static "view" is refreshed every step but never predicts the motion.
    prm = DwaParams()
    pos, vel = p.copy(), v0.copy()
    collided_static = False
    for _ in range(80):
        static_view[0].centre = obstacles[0].centre.copy()
        vel, _ = dwa_command(pos, vel, static_view, goal, prm, goal)
        pos = pos + vel * prm.dt
        obstacles[0].centre = obstacles[0].centre + obstacles[0].velocity * prm.dt
        if clearance_at(pos, obstacles, prm.radius) <= 0.0:
            collided_static = True
            break
        if np.linalg.norm(pos - goal) <= prm.goal_tol:
            break
    assert collided_static, "the static view should collide with the intruder"
    p, v0, goal, obstacles = moving_obstacle_scene()
    run = simulate(p, v0, goal, obstacles, DwaParams(), max_steps=80)
    assert run["reached"] and not run["collided"], (run["reached"], run["collided"])
    print("moving obstacle: static view collides, relative-velocity rollout reaches "
          "the goal in %d steps (min clearance %.2f m)" % (run["steps"], run["min_clearance"]))

    # 8. Hysteresis and smoothing keep the command in the window and admissible.
    p, v_a, goal, obstacles, prm = worked_example()
    for prm2 in (DwaParams(hysteresis=0.05), DwaParams(smooth=True)):
        v, _ = dwa_command(p, v_a, obstacles, goal, prm2, goal)
        _check_window_and_admissibility(p, v_a, v, obstacles, prm2)

    print("ch14_dwa.py: all self-tests passed in %.2f s" % (time.time() - t0))


def print_candidate_table(cands):
    """Print the candidates of the worked example as rows: vx vy dist adm h c s G."""
    for c in sorted(cands, key=lambda c: (-c.v[0], -c.v[1])):
        print("%5.2f %5.2f  dist=%5.3f  adm=%d  h=%.3f  c=%.3f  s=%.3f  G=%.3f"
              % (c.v[0], c.v[1], c.dist, c.admissible, c.heading, c.clearance,
                 c.velocity, c.score))


if __name__ == "__main__":
    _self_test()
    p, v_a, goal, obstacles, prm = worked_example()
    _, cands = dwa_command(p, v_a, obstacles, goal, prm, goal)
    print_candidate_table(cands)
