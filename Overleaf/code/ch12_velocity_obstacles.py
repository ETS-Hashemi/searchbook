"""Velocity obstacles (Chapter 12): collision cone, velocity obstacle,
time to collision, truncated VO, velocity selection by sampling, and a
small simulator that produces trajectories.

Conventions (Fiorini and Shiller 1998, as used in Chapter 12):

    p_rel = p_B - p_A      relative position of B as seen from A
    v_rel = v_A - v_B      relative velocity of A with respect to B
    R     = r_A + r_B      radius of the Minkowski disc

The discs A and B touch or overlap at time t >= 0 if and only if
|p_rel - t v_rel| <= R, i.e. if and only if the point t v_rel lies in the
disc D(p_rel, R).  The collision cone CC_{A|B} is the set of relative
velocities for which this happens for some t > 0, the velocity obstacle is
VO_{A|B} = v_B + CC_{A|B}, and the truncated VO^tau_{A|B} keeps only the
velocities that collide within the horizon tau.

The geometry helpers in section 1 are copied from code/ch02_toolbox.py so
that this file is self-contained (the book's rule: copy, do not import).

Run:   python3 code/ch12_velocity_obstacles.py
       (self-test with asserts, then the numbers of the worked example)
"""
import math
import time

import numpy as np


# ---------------------------------------------------------------------
# 1. Plane geometry (copied from code/ch02_toolbox.py)
# ---------------------------------------------------------------------
def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def scale(a, s):
    return (a[0] * s, a[1] * s)


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


def cross(a, b):
    """The 2D cross product a_x b_y - a_y b_x (signed area, left turn > 0)."""
    return a[0] * b[1] - a[1] * b[0]


def norm(a):
    return math.hypot(a[0], a[1])


def rotate(a, angle):
    """Rotate the vector a counter-clockwise by ``angle`` radians."""
    c, s = math.cos(angle), math.sin(angle)
    return (c * a[0] - s * a[1], s * a[0] + c * a[1])


def ray_circle_intersection(o, d, c, r):
    """Smallest t >= 0 with |o + t d - c| = r, or None if the ray misses
    the circle.  Returns 0.0 if o already lies inside the circle."""
    f = sub(o, c)
    a = dot(d, d)
    b = dot(f, d)
    k = dot(f, f) - r * r
    if k <= 0.0:
        return 0.0
    if a == 0.0:
        return None
    disc = b * b - a * k
    if disc < 0.0:
        return None
    t = (-b - math.sqrt(disc)) / a
    return t if t >= 0.0 else None


def minkowski_disc(c1, r1, c2, r2):
    """Minkowski sum of two discs: a disc of centre c1 + c2 and radius r1 + r2."""
    return add(c1, c2), r1 + r2


def tangent_points(p, c, r):
    """The two points where the tangent lines from p touch the circle
    (c, r), or None if p lies on or inside the circle."""
    u = sub(p, c)
    d = norm(u)
    if d <= r:
        return None
    u = scale(u, 1.0 / d)                 # unit vector from c towards p
    perp = (-u[1], u[0])                  # u rotated by +90 degrees
    cos_a = r / d                         # angle at the centre
    sin_a = math.sqrt(1.0 - cos_a * cos_a)
    t_left = add(c, scale(add(scale(u, cos_a), scale(perp, sin_a)), r))
    t_right = add(c, scale(add(scale(u, cos_a), scale(perp, -sin_a)), r))
    return t_left, t_right


# ---------------------------------------------------------------------
# 2. Time to collision and the membership test (any dimension)
# ---------------------------------------------------------------------
def time_to_collision(p_rel, v_rel, radius):
    """First time t >= 0 at which |p_rel - t v_rel| <= radius, or math.inf
    if the discs (spheres) never touch.  Works in 2D and in 3D."""
    p = np.asarray(p_rel, dtype=float)
    v = np.asarray(v_rel, dtype=float)
    pp, pv, vv = p @ p, p @ v, v @ v
    k = pp - radius * radius
    if k <= 0.0:
        return 0.0                        # already overlapping
    if vv == 0.0:
        return math.inf                   # no relative motion
    disc = pv * pv - vv * k               # discriminant / 4
    if disc < 0.0:
        return math.inf                   # the ray misses the disc
    t = (pv - math.sqrt(disc)) / vv       # smaller root = first contact
    return t if t >= 0.0 else math.inf    # the disc lies behind A


def in_velocity_obstacle(p_rel, v_rel, radius, tau=math.inf):
    """True iff the relative velocity v_rel leads to a collision within the
    horizon tau (tau = inf gives the untruncated velocity obstacle)."""
    tc = time_to_collision(p_rel, v_rel, radius)
    return tc < math.inf and tc <= tau


def cone_half_angle(distance, radius):
    """Half-angle of the collision cone, asin(R / |p_rel|) (2D and 3D)."""
    if distance <= radius:
        return math.pi / 2.0
    return math.asin(radius / distance)


def ttc_batch(p_rel, v_rels, radius):
    """Vectorised time_to_collision: v_rels has shape (m, dim)."""
    p = np.asarray(p_rel, dtype=float)
    v = np.asarray(v_rels, dtype=float)
    pp = p @ p
    pv = v @ p
    vv = np.einsum("ij,ij->i", v, v)
    k = pp - radius * radius
    if k <= 0.0:
        return np.zeros(len(v))
    disc = pv * pv - vv * k
    out = np.full(len(v), np.inf)
    ok = (disc >= 0.0) & (vv > 0.0)
    t = (pv[ok] - np.sqrt(disc[ok])) / vv[ok]
    t[t < 0.0] = np.inf
    out[ok] = t
    return out


# ---------------------------------------------------------------------
# 3. The velocity obstacle as a geometric object (2D)
# ---------------------------------------------------------------------
class VelocityObstacle:
    """VO^tau_{A|B}: apex v_B, axis towards p_rel, half-angle asin(R/d),
    truncated by the disc D(v_B + p_rel/tau, R/tau) when tau < inf."""

    def __init__(self, p_a, r_a, p_b, v_b, r_b, tau=math.inf):
        self.apex = (float(v_b[0]), float(v_b[1]))
        self.p_rel = sub(p_b, p_a)
        self.radius = r_a + r_b
        self.tau = tau
        self.distance = norm(self.p_rel)
        self.half_angle = cone_half_angle(self.distance, self.radius)
        if self.distance > 0.0:
            self.axis = scale(self.p_rel, 1.0 / self.distance)
        else:
            self.axis = (1.0, 0.0)
        self.left = rotate(self.axis, self.half_angle)     # ccw tangent ray
        self.right = rotate(self.axis, -self.half_angle)   # cw tangent ray

    def contains(self, v):
        """Membership of an absolute velocity v of A."""
        return in_velocity_obstacle(self.p_rel, sub(v, self.apex),
                                    self.radius, self.tau)

    def time_to_collision(self, v):
        return time_to_collision(self.p_rel, sub(v, self.apex), self.radius)

    def truncation_disc(self):
        """Centre and radius of the disc that cuts the apex off (absolute
        velocities); None for the untruncated cone."""
        if math.isinf(self.tau):
            return None
        return add(self.apex, scale(self.p_rel, 1.0 / self.tau)), \
            self.radius / self.tau

    def closest_boundary_point(self, v):
        """Exact projection of an absolute velocity v onto the boundary of
        the (truncated) VO; returns v itself if v is not inside."""
        if not self.contains(v):
            return v
        w = sub(v, self.apex)
        cands = []
        # the two tangent rays, beyond their tangency points
        s_min = 0.0
        if not math.isinf(self.tau):
            c = scale(self.p_rel, 1.0 / self.tau)
            s_min = dot(c, self.left)          # tangency parameter, same
            # for both rays by symmetry
        for e in (self.left, self.right):
            s = max(dot(w, e), s_min)
            cands.append(scale(e, s))
        # the near arc of the truncation disc, between the tangency points
        if not math.isinf(self.tau):
            rho = self.radius / self.tau
            n_left = rotate(self.left, math.pi / 2)
            n_right = rotate(self.right, -math.pi / 2)
            ang_l = math.atan2(n_left[1], n_left[0])
            ang_r = math.atan2(n_right[1], n_right[0])
            wc = sub(w, c)
            if norm(wc) > 0.0:
                ang = math.atan2(wc[1], wc[0])
                span = (ang_r - ang_l) % (2 * math.pi)
                if (ang - ang_l) % (2 * math.pi) <= span:
                    cands.append(add(c, scale(wc, rho / norm(wc))))
        best = min(cands, key=lambda q: norm(sub(q, w)))
        return add(self.apex, best)


# ---------------------------------------------------------------------
# 4. Agents, velocity selection by sampling, simulation
# ---------------------------------------------------------------------
class Agent:
    """A disc-shaped agent moving towards a goal at a nominal speed."""

    def __init__(self, position, goal, radius=0.5, speed=1.0, v_max=1.5,
                 avoiding=True, velocity=None):
        self.position = (float(position[0]), float(position[1]))
        self.goal = (float(goal[0]), float(goal[1]))
        self.radius = float(radius)
        self.speed = float(speed)
        self.v_max = float(v_max)
        self.avoiding = avoiding
        self.velocity = (0.0, 0.0) if velocity is None else tuple(velocity)
        self.done = False

    def preferred_velocity(self, dt):
        """Towards the goal at the nominal speed, slowing down so as not to
        overshoot within one step; zero once the goal is reached."""
        to_goal = sub(self.goal, self.position)
        d = norm(to_goal)
        if d < 1e-9:
            return (0.0, 0.0)
        s = min(self.speed, d / dt)
        return scale(to_goal, s / d)


def velocity_samples(v_max, rings=10, directions=72):
    """Candidate velocities: the origin plus ``rings`` concentric rings of
    ``directions`` equally spaced directions, up to the speed v_max."""
    speeds = v_max * np.arange(1, rings + 1) / rings
    angles = 2.0 * np.pi * np.arange(directions) / directions
    ring = np.stack([np.cos(angles), np.sin(angles)], axis=1)
    pts = [np.zeros((1, 2))] + [s * ring for s in speeds]
    return np.vstack(pts)


def choose_velocity(agent, others, tau, dt, samples=None, penalty=1.0):
    """Sampled velocity-obstacle selection for ``agent`` (Algorithm 12.2).

    Every candidate is tested against the truncated VO of every other
    agent (others keep their current velocities).  Among the candidates
    that are outside all VO^tau, the one closest to the preferred velocity
    wins; if there is none, the penalised cost |v - v_pref| + penalty/t_c
    picks the least dangerous candidate.  Returns (velocity, info)."""
    v_pref = agent.preferred_velocity(dt)
    if samples is None:
        samples = velocity_samples(agent.v_max)
    cand = np.vstack([samples, np.asarray([v_pref])])
    tc = np.full(len(cand), np.inf)
    for other in others:
        if other is agent:
            continue
        p_rel = sub(other.position, agent.position)
        v_rel = cand - np.asarray(other.velocity, dtype=float)
        radius = agent.radius + other.radius
        if norm(p_rel) <= radius:            # already overlapping: forbid
            tc_j = np.where(v_rel @ np.asarray(p_rel) > 0.0, 0.0, np.inf)
        else:                                # every closing velocity
            tc_j = ttc_batch(p_rel, v_rel, radius)
        tc = np.minimum(tc, tc_j)
    dist = np.linalg.norm(cand - np.asarray(v_pref), axis=1)
    feasible = (tc > tau) | np.isinf(tc)
    if feasible.any():
        idx = int(np.argmin(np.where(feasible, dist, np.inf)))
    else:
        idx = int(np.argmin(dist + penalty / np.maximum(tc, 1e-9)))
    info = {"v_pref": v_pref, "tc_pref": float(tc[-1]),
            "n_feasible": int(feasible.sum()), "tc": float(tc[idx]),
            "feasible": bool(feasible[idx]), "dist": float(dist[idx])}
    return (float(cand[idx, 0]), float(cand[idx, 1])), info


class Trace:
    """Positions (T+1, n, 2), velocities (T, n, 2), times (T+1,)."""

    def __init__(self, positions, velocities, times, infos):
        self.positions = positions
        self.velocities = velocities
        self.times = times
        self.infos = infos

    def separations(self):
        """Smallest centre distance over all pairs, per time step."""
        p = self.positions
        n = p.shape[1]
        if n < 2:
            return np.full(len(p), np.inf)
        best = np.full(len(p), np.inf)
        for i in range(n):
            for j in range(i + 1, n):
                best = np.minimum(best, np.linalg.norm(p[:, i] - p[:, j], axis=1))
        return best

    def min_separation(self):
        return float(self.separations().min())

    def path_lengths(self):
        steps = np.linalg.norm(np.diff(self.positions, axis=0), axis=2)
        return steps.sum(axis=0)


def simulate(agents, dt=0.1, steps=200, tau=5.0, samples=None,
             goal_tolerance=0.05, record_info=False):
    """Synchronous simulation (Algorithm 12.3).  In every step each
    avoiding agent chooses a velocity outside the truncated VOs induced by
    the others' *current* velocities; non-avoiding agents follow their
    preferred velocity.  Then all agents move for dt.  Stops early when
    every agent has reached its goal."""
    if samples is None:
        samples = velocity_samples(max(a.v_max for a in agents))
    positions = [np.array([a.position for a in agents])]
    velocities, infos, times = [], [], [0.0]
    for a in agents:
        a.done = norm(sub(a.goal, a.position)) <= goal_tolerance
    for k in range(steps):
        new_v, step_info = [], []
        for a in agents:
            if a.done:
                v, info = (0.0, 0.0), None
            elif a.avoiding:
                v, info = choose_velocity(a, agents, tau, dt, samples)
            else:
                v, info = a.preferred_velocity(dt), None
            new_v.append(v)
            step_info.append(info)
        for a, v in zip(agents, new_v):
            a.velocity = v
            a.position = add(a.position, scale(v, dt))
            if norm(sub(a.goal, a.position)) <= goal_tolerance:
                a.done = True
        velocities.append(np.array(new_v))
        positions.append(np.array([a.position for a in agents]))
        times.append((k + 1) * dt)
        if record_info:
            infos.append(step_info)
        if all(a.done for a in agents):
            break
    return Trace(np.array(positions), np.array(velocities), np.array(times),
                 infos)


# ---------------------------------------------------------------------
# 5. Scenarios
# ---------------------------------------------------------------------
def crossing_scenario(speed_b=0.9, avoid_a=True, avoid_b=False):
    """The worked example: A flies east from (-5, 0), B flies north from
    (0, -5) at speed_b; B does not avoid (a non-cooperative intruder)."""
    a = Agent((-5.0, 0.0), (5.0, 0.0), radius=0.5, speed=1.0, v_max=1.5,
              avoiding=avoid_a, velocity=(1.0, 0.0))
    b = Agent((0.0, -5.0), (0.0, 5.0), radius=0.5, speed=speed_b, v_max=1.5,
              avoiding=avoid_b, velocity=(0.0, speed_b))
    return [a, b]


def head_on_scenario(offset=0.2, avoiding=True):
    """Two agents swapping places head-on; B is offset laterally.  With
    both avoiding this produces the oscillation of Section 12.7."""
    a = Agent((-5.0, 0.0), (5.0, 0.0), avoiding=avoiding, velocity=(1.0, 0.0))
    b = Agent((5.0, offset), (-5.0, offset), avoiding=avoiding,
              velocity=(-1.0, 0.0))
    return [a, b]


def circle_scenario(n, radius=6.0, seed=12, perturbation=0.05, avoiding=True):
    """n agents evenly spaced on a circle, each heading for the antipodal
    point: every pair is on a crossing course through the centre.  A small
    fixed-seed perturbation of the start positions breaks the symmetry."""
    rng = np.random.default_rng(seed)
    agents = []
    for i in range(n):
        ang = 2.0 * math.pi * i / n
        start = (radius * math.cos(ang), radius * math.sin(ang))
        start = add(start, tuple(perturbation * rng.standard_normal(2)))
        goal = (-radius * math.cos(ang), -radius * math.sin(ang))
        agents.append(Agent(start, goal, avoiding=avoiding))
    for a in agents:
        a.velocity = a.preferred_velocity(0.1)
    return agents


def stream_scenario(k, avoid_a=True):
    """One VO agent A flying east from (-6, 0) to (6, 0) at speed 1 across
    k non-cooperative intruders.  Intruder i crosses A's nominal path at
    x_i = -3.5 + i flying north at speed s_i in {0.8, 1.1, 1.4}, and starts
    at (x_i, -s_i (x_i + 6)) so that it would hit A exactly when A is there
    (A reaches x_i at time x_i + 6)."""
    a = Agent((-6.0, 0.0), (6.0, 0.0), avoiding=avoid_a, velocity=(1.0, 0.0))
    agents = [a]
    for i in range(k):
        x = -3.5 + i
        s_i = (0.8, 1.1, 1.4)[i % 3]
        agents.append(Agent((x, -s_i * (x + 6.0)), (x, 10.0), speed=s_i,
                            avoiding=False, velocity=(0.0, s_i)))
    return agents


def stream_metrics(k, avoid_a=True, steps=400, tau=5.0, dt=0.1):
    """Minimum separation between A and any intruder, A's path-length
    ratio and A's travel time in the stream scenario."""
    agents = stream_scenario(k, avoid_a=avoid_a)
    trace = simulate(agents, dt=dt, steps=steps, tau=tau, record_info=True)
    p = trace.positions
    sep = np.full(len(p), np.inf)
    for j in range(1, k + 1):
        sep = np.minimum(sep, np.linalg.norm(p[:, 0] - p[:, j], axis=1))
    reached = [i for i, q in enumerate(p[:, 0]) if norm(sub(q, agents[0].goal)) <= 0.05]
    t_goal = trace.times[reached[0]] if reached else float("inf")
    infeasible = sum(1 for step in trace.infos if step[0] is not None
                     and step[0]["n_feasible"] == 0)
    return {"min_sep": float(sep.min()), "t_min_sep": float(trace.times[int(np.argmin(sep))]),
            "path_ratio": float(trace.path_lengths()[0] / 12.0),
            "time": float(t_goal), "infeasible": infeasible, "trace": trace}


def crossing_metrics(n, avoiding, steps=400, tau=5.0, dt=0.1, **kw):
    """Minimum separation, mean path-length ratio, number of colliding
    pairs and completion time for the circle scenario."""
    agents = circle_scenario(n, avoiding=avoiding, **kw)
    straight = np.array([norm(sub(a.goal, a.position)) for a in agents])
    trace = simulate(agents, dt=dt, steps=steps, tau=tau)
    seps = trace.separations()
    p = trace.positions
    collisions = 0
    for i in range(n):
        for j in range(i + 1, n):
            d = np.linalg.norm(p[:, i] - p[:, j], axis=1)
            collisions += int(d.min() < agents[i].radius + agents[j].radius)
    return {"min_sep": float(seps.min()),
            "path_ratio": float((trace.path_lengths() / straight).mean()),
            "collisions": collisions,
            "time": float(trace.times[-1]),
            "finished": all(a.done for a in agents)}


# ---------------------------------------------------------------------
# 6. Worked example and self-test
# ---------------------------------------------------------------------
def worked_example(verbose=True, tau=5.0, dt=0.1):
    """All numbers quoted in Section 12.5 of the chapter."""
    out = {}
    a, b = crossing_scenario()
    vo = VelocityObstacle(a.position, a.radius, b.position, b.velocity,
                          b.radius, tau=tau)
    deg = 180.0 / math.pi
    v_pref = a.preferred_velocity(dt)
    v_rel = sub(v_pref, b.velocity)
    tc_pref = vo.time_to_collision(v_pref)
    exact = vo.closest_boundary_point(v_pref)
    samples = velocity_samples(a.v_max)
    v_chosen, info = choose_velocity(a, [a, b], tau, dt, samples)
    out.update(p_rel=vo.p_rel, distance=vo.distance, radius=vo.radius,
               half_angle_deg=vo.half_angle * deg, left=vo.left,
               right=vo.right, apex=vo.apex, v_rel=v_rel, tc_pref=tc_pref,
               disc=vo.truncation_disc(), exact=exact,
               tc_exact=vo.time_to_collision(exact), chosen=v_chosen,
               info=info)
    # no avoidance: closest approach
    trace0 = simulate(crossing_scenario(avoid_a=False), dt=dt, steps=200, tau=tau)
    out["none_min_sep"] = trace0.min_separation()
    out["none_time"] = float(trace0.times[int(np.argmin(trace0.separations()))])
    # with VO for A only
    agents = crossing_scenario()
    trace = simulate(agents, dt=dt, steps=200, tau=tau, record_info=True)
    seps = trace.separations()
    out["vo_min_sep"] = float(seps.min())
    out["vo_time_min_sep"] = float(trace.times[int(np.argmin(seps))])
    out["vo_path_a"] = float(trace.path_lengths()[0])
    out["vo_path_b"] = float(trace.path_lengths()[1])
    out["vo_finish"] = float(trace.times[-1])
    out["trace"] = trace
    if verbose:
        print("Worked example: A (-5,0)->(5,0) at 1.0, B (0,-5)->(0,5) at 0.9,"
              " r = 0.5 each, tau = %.1f, dt = %.1f" % (tau, dt))
        print("  p_rel = (%.1f, %.1f), d = %.4f, R = %.1f, half-angle = %.3f deg"
              % (vo.p_rel[0], vo.p_rel[1], vo.distance, vo.radius,
                 vo.half_angle * deg))
        print("  axis angle = %.2f deg, tangent rays at %.2f deg and %.2f deg"
              % (math.atan2(vo.axis[1], vo.axis[0]) * deg,
                 math.atan2(vo.left[1], vo.left[0]) * deg,
                 math.atan2(vo.right[1], vo.right[0]) * deg))
        print("  left ray dir = (%.4f, %.4f), right ray dir = (%.4f, %.4f)"
              % (vo.left + vo.right))
        print("  apex v_B = (%.1f, %.1f); v_pref = (%.1f, %.1f); v_rel = (%.1f, %.1f)"
              % (vo.apex + v_pref + v_rel))
        print("  quadratic: %.4f t^2 - %.4f t + %.4f = 0 -> t_c(v_pref) = %.4f s"
              % (dot(v_rel, v_rel), 2 * dot(vo.p_rel, v_rel),
                 dot(vo.p_rel, vo.p_rel) - vo.radius ** 2, tc_pref))
        c, rho = vo.truncation_disc()
        print("  truncation disc: centre (%.4f, %.4f), radius %.4f; v_pref in VO^tau: %s"
              % (c[0], c[1], rho, vo.contains(v_pref)))
        print("  exact closest boundary point = (%.4f, %.4f), |dv| = %.4f, t_c = %.4f"
              % (exact[0], exact[1], norm(sub(exact, v_pref)),
                 vo.time_to_collision(exact)))
        print("  sampled choice = (%.4f, %.4f), |dv| = %.4f, t_c = %.4f, "
              "feasible candidates = %d of %d"
              % (v_chosen[0], v_chosen[1], info["dist"], info["tc"],
                 info["n_feasible"], len(samples) + 1))
        print("  no avoidance: min separation %.4f at t = %.1f s"
              % (out["none_min_sep"], out["none_time"]))
        print("  VO (A only): min separation %.4f at t = %.1f s; path A %.4f, "
              "path B %.4f; finished at t = %.1f s"
              % (out["vo_min_sep"], out["vo_time_min_sep"], out["vo_path_a"],
                 out["vo_path_b"], out["vo_finish"]))
        print("  trace (t, p_A, v_rel(pref), t_c(pref), feasible, chosen v_A, t_c(chosen)):")
        for k in (0, 1, 2, 5, 10, 20, 30, 40, 45, 50, 60):
            if k >= len(trace.infos):
                break
            inf_a = trace.infos[k][0]
            if inf_a is None:
                break
            pa = trace.positions[k, 0]
            vb = trace.velocities[k, 1]
            vr = sub(inf_a["v_pref"], tuple(vb))
            va = trace.velocities[k, 0]
            print("   %4.1f  (%6.3f, %6.3f)  (%6.3f, %6.3f)  %7.3f  %4d  (%6.3f, %6.3f)  %7.3f"
                  % (trace.times[k], pa[0], pa[1], vr[0], vr[1], inf_a["tc_pref"],
                     inf_a["n_feasible"], va[0], va[1], inf_a["tc"]))
    return out


def _close(a, b, tol=1e-9):
    return abs(a - b) <= tol


def _self_test():
    t0 = time.time()
    R = 1.0
    p_rel = (5.0, -5.0)
    # (1) head-on relative velocity is inside the VO, a perpendicular one is not
    assert in_velocity_obstacle(p_rel, (1.0, -1.0), R)
    assert not in_velocity_obstacle(p_rel, (1.0, 1.0), R)
    assert not in_velocity_obstacle(p_rel, (-1.0, 1.0), R)   # moving away
    # (2) closed-form time to collision when heading straight at the disc
    tc = time_to_collision((10.0, 0.0), (2.0, 0.0), R)
    assert _close(tc, (10.0 - R) / 2.0)
    tc = time_to_collision(p_rel, (1.0, -1.0), R)
    assert _close(tc, 5.0 - 1.0 / math.sqrt(2.0))
    # overlapping discs collide now; the toolbox routine agrees everywhere
    assert time_to_collision((0.5, 0.0), (1.0, 0.0), R) == 0.0
    rng = np.random.default_rng(3)
    for _ in range(500):
        p = tuple(rng.uniform(-5, 5, 2))
        va, vb = tuple(rng.uniform(-2, 2, 2)), tuple(rng.uniform(-2, 2, 2))
        mine = time_to_collision(p, sub(va, vb), R)
        ref = ray_circle_intersection(p, sub(vb, va), (0.0, 0.0), R)
        assert (ref is None and math.isinf(mine)) or _close(mine, ref, 1e-9)
    # (3) tangent half-angle and the 3-4-5 tangent directions
    vo = VelocityObstacle((-5.0, 0.0), 0.5, (0.0, -5.0), (0.0, 0.9), 0.5, tau=5.0)
    assert _close(vo.half_angle, math.asin(1.0 / math.sqrt(50.0)))
    assert _close(vo.left[0], 0.8) and _close(vo.left[1], -0.6)
    assert _close(vo.right[0], 0.6) and _close(vo.right[1], -0.8)
    # grazing: the relative velocity along a tangent ray touches at one time
    tl = tangent_points((0.0, 0.0), p_rel, R)
    assert tl is not None
    for tp in tl:
        d = scale(tp, 1.0 / norm(tp))
        assert _close(abs(cross(d, vo.left)) * abs(cross(d, vo.right)), 0.0, 1e-9)
    # inside just inside the cone, outside just outside
    eps = 1e-3
    assert in_velocity_obstacle(p_rel, rotate(vo.axis, vo.half_angle - eps), R)
    assert not in_velocity_obstacle(p_rel, rotate(vo.axis, vo.half_angle + eps), R)
    # (4) truncation: a collision after the horizon is not in VO^tau
    v_far = scale(vo.axis, 0.5)         # t_c = (sqrt(50) - 1) / 0.5 = 12.1 s
    assert in_velocity_obstacle(p_rel, v_far, R)
    assert not in_velocity_obstacle(p_rel, v_far, R, tau=5.0)
    assert in_velocity_obstacle(p_rel, v_far, R, tau=13.0)
    # the truncation disc is inscribed in the cone: its centre lies on the
    # axis and its distance to each tangent ray equals its radius
    c, rho = vo.truncation_disc()
    c_rel = sub(c, vo.apex)
    assert _close(abs(cross(c_rel, vo.left)), rho) and _close(abs(cross(c_rel, vo.right)), rho)
    # (5) the worked example: exact projection and sampled choice
    ex = worked_example(verbose=False)
    assert _close(ex["exact"][0], 1.0, 1e-9) and _close(ex["exact"][1], 0.1, 1e-9)
    assert _close(ex["tc_exact"], 5.0, 1e-9)
    assert ex["info"]["feasible"] and ex["info"]["tc"] > 5.0
    assert ex["info"]["dist"] <= 0.2       # sampled choice close to the optimum
    # a Minkowski sum of the two discs is the disc of the VO
    assert minkowski_disc((0.0, -5.0), 0.5, (0.0, 0.0), 0.5) == ((0.0, -5.0), 1.0)
    # (6) static obstacle: v_B = 0 makes VO = CC (apex at the origin)
    vo_static = VelocityObstacle((0.0, 0.0), 0.5, (3.0, 0.0), (0.0, 0.0), 0.5)
    assert vo_static.apex == (0.0, 0.0) and vo_static.contains((1.0, 0.0))
    assert not vo_static.contains((0.0, 1.0))
    # (7) 3D: same formula, same half-angle, right circular cone
    p3 = np.array([3.0, 4.0, 12.0])            # |p3| = 13
    theta = cone_half_angle(13.0, R)
    u = p3 / 13.0
    w = np.array([0.0, 0.0, 1.0])
    w = w - (w @ u) * u
    w = w / np.linalg.norm(w)
    inside = math.cos(theta - eps) * u + math.sin(theta - eps) * w
    outside = math.cos(theta + eps) * u + math.sin(theta + eps) * w
    assert in_velocity_obstacle(p3, inside, R)
    assert not in_velocity_obstacle(p3, outside, R)
    assert _close(time_to_collision(p3, 2.0 * u, R), (13.0 - R) / 2.0)
    # (8) simulation: VO keeps the minimum separation above r_A + r_B
    assert ex["none_min_sep"] < 1.0            # without avoidance they collide
    assert ex["vo_min_sep"] >= 1.0 - 1e-9      # with VO for A they never do
    assert ex["vo_path_a"] > 10.0              # the detour costs some length
    four = crossing_metrics(4, avoiding=True, steps=300)
    none4 = crossing_metrics(4, avoiding=False, steps=300)
    assert none4["collisions"] > 0 and none4["min_sep"] < 1.0
    assert four["collisions"] == 0 and four["min_sep"] >= 1.0 - 1e-9
    assert four["finished"]
    stream = stream_metrics(5)
    assert stream["min_sep"] >= 1.0 - 1e-9 and stream["time"] < 40.0
    assert stream_metrics(5, avoid_a=False)["min_sep"] < 1.0
    # (9) the oscillation scenario reverses the lateral velocity of A
    osc = simulate(head_on_scenario(), dt=0.1, steps=120, tau=5.0)
    vy = osc.velocities[:, 0, 1]
    flips = int((np.sign(vy[1:]) * np.sign(vy[:-1]) < 0).sum())
    assert flips >= 3 and osc.min_separation() >= 1.0 - 1e-9
    print("ch12 self-test passed (%.1f s)" % (time.time() - t0))


if __name__ == "__main__":
    _self_test()
    worked_example()
    for k in (1, 4, 8):
        m = stream_metrics(k)
        print("stream k=%d: VO min_sep %.3f at t=%.1f ratio %.3f time %.1f "
              "infeasible %d" % (k, m["min_sep"], m["t_min_sep"], m["path_ratio"],
                                 m["time"], m["infeasible"]))
    for n in (2, 4, 6):
        m_vo = crossing_metrics(n, avoiding=True)
        m_no = crossing_metrics(n, avoiding=False)
        print("circle n=%d: none min_sep %.3f ratio %.3f | VO min_sep %.3f "
              "ratio %.3f time %.1f" % (n, m_no["min_sep"], m_no["path_ratio"],
                                        m_vo["min_sep"], m_vo["path_ratio"],
                                        m_vo["time"]))
