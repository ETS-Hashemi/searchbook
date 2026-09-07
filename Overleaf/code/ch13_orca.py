"""Chapter 13 -- Reciprocal Avoidance: RVO and ORCA.

Velocity obstacles (VO), reciprocal velocity obstacles (RVO) and optimal
reciprocal collision avoidance (ORCA) for discs that move in the plane.

* ``orca_half_plane(agent, other, tau, dt, reciprocal)`` builds the ORCA
  half-plane of one agent with respect to one neighbour, with the full
  case analysis of the closest point on the truncated velocity obstacle
  (truncating disc, left leg, right leg, already overlapping) and either
  half (reciprocal) or full (non-cooperative neighbour) responsibility.
* ``orca_velocity`` chooses the velocity closest to the preferred one in
  the intersection of all half-planes and the speed disc with the
  incremental two-dimensional linear program of RVO2, and falls back to
  the dense formulation (minimise the largest penetration) when the
  intersection is empty.
* ``simulate`` runs an n-agent scenario with no avoidance, sampled VO,
  sampled RVO or ORCA.  ``circle_scenario`` and ``dance_scenario`` are
  the instances used in the chapter; ``worked_example`` prints every
  number of the worked example.

The geometry helpers are copied from ch02_toolbox.py so that this file
stands alone.  Positions and velocities are plain tuples of floats; NumPy
is used for the sampled VO/RVO choice and for the simulation records.

Run the self-test with

    python3 ch13_orca.py
"""
from __future__ import annotations

import math
import time
from typing import NamedTuple

import numpy as np

EPS = 1e-9


# ---------------------------------------------------------------------
# 1. Geometry helpers (copied from ch02_toolbox.py)
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


def unit(a):
    """a / |a|, or (0, 0) for the zero vector."""
    n = norm(a)
    return (a[0] / n, a[1] / n) if n > 0.0 else (0.0, 0.0)


def clip_norm(vec, limit):
    """Scale ``vec`` down so that its Euclidean norm is at most ``limit``."""
    n = norm(vec)
    return vec if n <= limit else scale(vec, limit / n)


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


def time_to_collision(p_a, v_a, r_a, p_b, v_b, r_b):
    """First time t >= 0 at which two constant-velocity discs touch, or
    None.  This is a ray-circle test in the relative frame."""
    return ray_circle_intersection(sub(p_b, p_a), sub(v_b, v_a),
                                   (0.0, 0.0), r_a + r_b)


# ---------------------------------------------------------------------
# 2. Agents and half-planes
# ---------------------------------------------------------------------
class Agent:
    """A disc of radius ``radius`` at ``position`` moving with ``velocity``.

    ``goal`` and ``speed`` define the preferred velocity (towards the goal
    at the nominal speed, slowing down in the last time step); ``v_max``
    bounds the speed the agent may choose.
    """

    def __init__(self, position, velocity=(0.0, 0.0), radius=0.5,
                 v_max=1.5, goal=None, speed=1.0):
        self.position = tuple(float(x) for x in position)
        self.velocity = tuple(float(x) for x in velocity)
        self.radius = float(radius)
        self.v_max = float(v_max)
        self.goal = None if goal is None else tuple(float(x) for x in goal)
        self.speed = float(speed)
        self.v_pref = self.velocity


class HalfPlane:
    """The closed half-plane {v : (v - point) . normal >= 0}.

    ``normal`` is a unit vector pointing into the feasible side.  Its
    ``direction`` (the normal rotated by -90 degrees) runs along the
    boundary with the feasible side on the left, the convention of RVO2.
    """

    __slots__ = ("point", "normal")

    def __init__(self, point, normal):
        self.point = tuple(point)
        self.normal = tuple(normal)

    @property
    def direction(self):
        return (self.normal[1], -self.normal[0])

    def violation(self, v):
        """How far v lies on the wrong side (<= 0 means feasible)."""
        return -dot(sub(v, self.point), self.normal)

    def contains(self, v, tol=1e-9):
        return self.violation(v) <= tol


class OrcaLine(NamedTuple):
    """Result of ``orca_half_plane``: the half-plane (normal n, point) and
    the vector u and the boundary case that produced it."""
    normal: tuple
    point: tuple
    u: tuple
    case: str

    def half_plane(self):
        return HalfPlane(self.point, self.normal)


# ---------------------------------------------------------------------
# 3. Velocity obstacles: membership and the closest boundary point
# ---------------------------------------------------------------------
def in_velocity_obstacle(p, v_rel, r, tau=math.inf):
    """True if the relative velocity v_rel lies inside VO^tau: two discs
    with relative position p and combined radius r would touch before
    time tau.  Velocities on the boundary count as outside."""
    t = ray_circle_intersection((0.0, 0.0), v_rel, p, r)
    return t is not None and t < tau


def vo_closest_boundary_point(p, v_rel, r, tau, dt):
    """Closest point of the boundary of the truncated velocity obstacle
    VO^tau (relative position p, combined radius r) to the relative
    velocity v_rel.

    Returns (u, n, case): u is the vector from v_rel to the closest
    boundary point q = v_rel + u, n is the outward unit normal of VO^tau
    at q, and case names the part of the boundary that was hit: "disc"
    (the truncating disc of centre p / tau and radius r / tau), "left
    leg", "right leg", or "overlap" (the discs already intersect; the
    disc of one time step dt is used instead so that the agents separate).
    """
    dist2 = dot(p, p)
    r2 = r * r
    if dist2 > r2:
        c = scale(p, 1.0 / tau)              # centre of the truncating disc
        rho = r / tau                        # its radius
        w = sub(v_rel, c)                    # from that centre to v_rel
        w2 = dot(w, w)
        wp = dot(w, p)
        if wp < 0.0 and wp * wp > r2 * w2:
            # angle(w, -p) < arccos(r / |p|): the closest point is on the arc
            w_len = math.sqrt(w2)
            n = scale(w, 1.0 / w_len)
            return scale(n, rho - w_len), n, "disc"
        leg = math.sqrt(dist2 - r2)          # length of a tangent from 0
        if cross(p, w) > 0.0:
            d = ((p[0] * leg - p[1] * r) / dist2,
                 (p[0] * r + p[1] * leg) / dist2)   # unit vector, left leg
            n = (-d[1], d[0])                        # outward: d rotated +90
            case = "left leg"
        else:
            d = ((p[0] * leg + p[1] * r) / dist2,
                 (-p[0] * r + p[1] * leg) / dist2)  # unit vector, right leg
            n = (d[1], -d[0])                        # outward: d rotated -90
            case = "right leg"
        q = scale(d, dot(v_rel, d))              # projection onto the leg
        return sub(q, v_rel), n, case
    # the discs already overlap: leave the disc of centre p/dt, radius r/dt
    c = scale(p, 1.0 / dt)
    rho = r / dt
    w = sub(v_rel, c)
    w_len = norm(w)
    if w_len > EPS:
        n = scale(w, 1.0 / w_len)
    elif dist2 > 0.0:
        n = unit(scale(p, -1.0))
    else:
        n = (1.0, 0.0)
    return scale(n, rho - w_len), n, "overlap"


def orca_half_plane(agent, other, tau, dt=0.1, reciprocal=True):
    """The ORCA half-plane of ``agent`` induced by ``other`` for the
    horizon tau.  With ``reciprocal`` both agents take half of the
    avoiding change u (the other is assumed to run ORCA too); without it
    ``agent`` takes all of u (a non-cooperative intruder, a static
    obstacle).

    Returns an OrcaLine (normal n, point, u, case); the half-plane is
    {v : (v - point) . n >= 0} with point = v_agent + u/2 or v_agent + u.
    """
    p = sub(other.position, agent.position)
    v_rel = sub(agent.velocity, other.velocity)
    r = agent.radius + other.radius
    u, n, case = vo_closest_boundary_point(p, v_rel, r, tau, dt)
    share = 0.5 if reciprocal else 1.0
    return OrcaLine(n, add(agent.velocity, scale(u, share)), u, case)


# ---------------------------------------------------------------------
# 4. The linear program over half-planes
# ---------------------------------------------------------------------
def _lp_on_line(lines, i, v_max, v_opt, direction_opt):
    """Best point on the boundary line of lines[i] that satisfies
    lines[0..i-1] and the speed disc (RVO2 linearProgram1); None if the
    line carries no such point."""
    line = lines[i]
    d = line.direction
    q = line.point
    b = dot(q, d)
    disc = b * b + v_max * v_max - dot(q, q)
    if disc < 0.0:
        return None                          # the line misses the disc
    root = math.sqrt(disc)
    t_left, t_right = -b - root, -b + root   # the chord inside the disc
    for j in range(i):
        dj = lines[j].direction
        den = cross(d, dj)
        num = cross(dj, sub(q, lines[j].point))
        if abs(den) <= EPS:                  # parallel boundaries
            if num < 0.0:
                return None                  # line j excludes all of line i
            continue
        t = num / den
        if den >= 0.0:
            t_right = min(t_right, t)        # line j cuts the chord on the right
        else:
            t_left = max(t_left, t)          # ... on the left
        if t_left > t_right:
            return None
    if direction_opt:                        # go as far as possible along v_opt
        t = t_right if dot(v_opt, d) > 0.0 else t_left
    else:                                    # closest point to v_opt
        t = min(max(dot(d, sub(v_opt, q)), t_left), t_right)
    return add(q, scale(d, t))


def lp_incremental(lines, v_max, v_opt, direction_opt=False):
    """Incremental two-dimensional linear program (RVO2 linearProgram2).

    Finds the point of the intersection of the half-planes ``lines`` and
    the disc |v| <= v_max that is closest to v_opt (or, with
    ``direction_opt``, furthest along the unit direction v_opt).  Returns
    (v, k): k == len(lines) on success; otherwise lines[k] cannot be
    satisfied together with lines[0..k-1], and v solves lines[0..k-1].
    """
    if direction_opt:
        v = scale(v_opt, v_max)
    elif dot(v_opt, v_opt) > v_max * v_max:
        v = scale(v_opt, v_max / norm(v_opt))
    else:
        v = v_opt
    for i, line in enumerate(lines):
        if line.violation(v) > 0.0:
            new_v = _lp_on_line(lines, i, v_max, v_opt, direction_opt)
            if new_v is None:
                return v, i
            v = new_v
    return v, len(lines)


def lp_dense(lines, n_hard, begin, v_max, v):
    """Dense fallback (RVO2 linearProgram3): the half-planes cannot all be
    satisfied, so return the velocity that minimises the largest
    penetration of lines[begin..]; the first n_hard lines (static
    obstacles) stay hard.  ``v`` solves lines[0..begin-1]."""
    depth = 0.0
    for i in range(begin, len(lines)):
        if lines[i].violation(v) <= depth:
            continue                         # no deeper than the others
        # "line j penetrates no deeper than line i" is the half-plane on the
        # feasible side of the bisector of lines i and j
        proj = list(lines[:n_hard])
        for j in range(n_hard, i):
            li, lj = lines[i], lines[j]
            den = cross(li.direction, lj.direction)
            if abs(den) <= EPS:
                if dot(li.direction, lj.direction) > 0.0:
                    continue                 # same direction: nothing to add
                point = scale(add(li.point, lj.point), 0.5)
            else:
                t = cross(lj.direction, sub(li.point, lj.point)) / den
                point = add(li.point, scale(li.direction, t))
            direction = unit(sub(lj.direction, li.direction))
            proj.append(HalfPlane(point, (-direction[1], direction[0])))
        candidate, k = lp_incremental(proj, v_max, lines[i].normal, True)
        if k == len(proj):
            v = candidate
        depth = lines[i].violation(v)
    return v


def orca_velocity(lines, v_pref, v_max, n_hard=0):
    """Velocity closest to v_pref in the intersection of all ORCA
    half-planes and the disc |v| <= v_max.  Returns (v, feasible); when
    the intersection is empty, v is the dense-fallback velocity."""
    v, k = lp_incremental(lines, v_max, v_pref)
    if k < len(lines):
        return lp_dense(lines, n_hard, k, v_max, v), False
    return v, True


# ---------------------------------------------------------------------
# 5. Sampled VO and RVO velocity choice (for the comparison)
# ---------------------------------------------------------------------
def velocity_samples(v_max, rings=10, directions=72):
    """Polar grid of candidate velocities inside the speed disc."""
    pts = [(0.0, 0.0)]
    for k in range(1, rings + 1):
        s = v_max * k / rings
        for m in range(directions):
            a = 2.0 * math.pi * m / directions
            pts.append((s * math.cos(a), s * math.sin(a)))
    return np.array(pts)


def ttc_batch(p, v_rels, r):
    """Time to collision for many relative velocities at once (vectorised
    ray-circle test): inf where the discs never touch, 0 if they overlap."""
    p = np.asarray(p, dtype=float)
    k = float(p @ p - r * r)
    out = np.full(len(v_rels), np.inf)
    if k <= 0.0:
        out[:] = 0.0
        return out
    a = np.einsum("ij,ij->i", v_rels, v_rels)
    b = -(v_rels @ p)
    disc = b * b - a * k
    ok = (disc >= 0.0) & (a > 0.0)
    t = np.full(len(v_rels), np.inf)
    t[ok] = (-b[ok] - np.sqrt(disc[ok])) / a[ok]
    hit = ok & (t >= 0.0)
    out[hit] = t[hit]
    return out


def choose_sampled(agent, others, tau, reciprocal=False, samples=None):
    """Velocity choice of the sampled VO (reciprocal=False) or RVO
    (reciprocal=True) method: among the candidates the one closest to
    v_pref whose (reciprocal) relative velocity stays outside every
    truncated VO; if there is none, the candidate with the latest first
    collision (ties towards v_pref)."""
    if samples is None:
        samples = velocity_samples(agent.v_max)
    cand = np.vstack([samples, [agent.v_pref], [agent.velocity]])
    cand = cand[np.hypot(cand[:, 0], cand[:, 1]) <= agent.v_max + 1e-12]
    v_a = np.asarray(agent.velocity)
    feasible = np.ones(len(cand), dtype=bool)
    first = np.full(len(cand), np.inf)
    for other in others:
        p = sub(other.position, agent.position)
        r = agent.radius + other.radius
        v_b = np.asarray(other.velocity)
        if reciprocal:
            v_rel = 2.0 * cand - v_a - v_b   # RVO: average of v and v_A vs v_B
        else:
            v_rel = cand - v_b               # VO: v vs v_B
        t = ttc_batch(p, v_rel, r)
        feasible &= t >= tau
        first = np.minimum(first, t)
    dist = np.hypot(cand[:, 0] - agent.v_pref[0], cand[:, 1] - agent.v_pref[1])
    if feasible.any():
        idx = np.flatnonzero(feasible)
        best = idx[np.argmin(dist[idx])]
    else:
        best = np.lexsort((dist, -first))[0]
    return (float(cand[best, 0]), float(cand[best, 1]))


# ---------------------------------------------------------------------
# 6. Simulation
# ---------------------------------------------------------------------
def preferred_velocity(agent, dt):
    """Towards the goal at the nominal speed, slowing down so that the
    goal is reached and not overshot in the last time step."""
    if agent.goal is None:
        return agent.velocity
    to_goal = sub(agent.goal, agent.position)
    d = norm(to_goal)
    if d < EPS:
        return (0.0, 0.0)
    return scale(to_goal, min(agent.speed, d / dt) / d)


def simulate(agents, mode, tau=5.0, dt=0.1, steps=300, perturbation=None,
             goal_tol=0.1):
    """Run the scenario with mode in {"none", "vo", "rvo", "orca"}.

    All agents choose their new velocity from the same snapshot of the
    others (simultaneous updates), then move for one time step.
    ``perturbation`` (n x 2) is added to every preferred velocity to break
    exact symmetry.  Returns a dictionary with the position and velocity
    records (steps+1, n, 2), the minimum centre distance over time, the
    number of time steps and pairs with overlapping discs, the number of
    steps in which the ORCA program was infeasible, and arrival times.
    """
    n = len(agents)
    pos = np.zeros((steps + 1, n, 2))
    vel = np.zeros((steps + 1, n, 2))
    pos[0] = [a.position for a in agents]
    vel[0] = [a.velocity for a in agents]
    samples = None
    if mode in ("vo", "rvo"):
        samples = velocity_samples(max(a.v_max for a in agents))
    infeasible = 0
    arrival = np.full(n, np.nan)
    for k in range(steps):
        new_v = []
        for i, a in enumerate(agents):
            v_pref = preferred_velocity(a, dt)
            if perturbation is not None:
                v_pref = add(v_pref, tuple(perturbation[i]))
            a.v_pref = clip_norm(v_pref, a.v_max)
            others = [b for j, b in enumerate(agents) if j != i]
            if mode == "none":
                v = a.v_pref
            elif mode in ("vo", "rvo"):
                v = choose_sampled(a, others, tau, mode == "rvo", samples)
            elif mode == "orca":
                lines = [orca_half_plane(a, b, tau, dt).half_plane()
                         for b in others]
                v, ok = orca_velocity(lines, a.v_pref, a.v_max)
                infeasible += 0 if ok else 1
            else:
                raise ValueError("unknown mode " + str(mode))
            new_v.append(v)
        for i, (a, v) in enumerate(zip(agents, new_v)):
            a.velocity = v
            a.position = add(a.position, scale(v, dt))
            pos[k + 1, i] = a.position
            vel[k + 1, i] = v
            if (math.isnan(arrival[i]) and a.goal is not None
                    and norm(sub(a.position, a.goal)) <= goal_tol):
                arrival[i] = (k + 1) * dt
    radii = np.array([a.radius for a in agents])
    diff = pos[:, :, None, :] - pos[:, None, :, :]
    dist = np.hypot(diff[..., 0], diff[..., 1])
    iu = np.triu_indices(n, 1)
    pair_dist = dist[:, iu[0], iu[1]]
    threshold = radii[iu[0]] + radii[iu[1]]
    overlap = pair_dist < threshold - 1e-9
    return {"positions": pos, "velocities": vel, "dt": dt,
            "min_separation": pair_dist.min(axis=1),
            "collision_steps": int(overlap.any(axis=1).sum()),
            "collision_pairs": int(overlap.any(axis=0).sum()),
            "infeasible_steps": infeasible, "arrival": arrival}


def path_lengths(result):
    """Length of the polyline travelled by every agent."""
    steps = np.diff(result["positions"], axis=0)
    return np.hypot(steps[..., 0], steps[..., 1]).sum(axis=0)


def velocity_variation(result, i):
    """Sum of |v(k+1) - v(k)| for agent i: how much the velocity changes."""
    dv = np.diff(result["velocities"][:, i, :], axis=0)
    return float(np.hypot(dv[:, 0], dv[:, 1]).sum())


def reversals(result, i):
    """Number of time steps at which the velocity change of agent i turns
    against the previous change (a zig-zag indicator)."""
    dv = np.diff(result["velocities"][:, i, :], axis=0)
    turn = np.einsum("ij,ij->i", dv[1:], dv[:-1])
    return int((turn < -1e-12).sum())


def circle_scenario(n=8, radius=10.0, agent_radius=0.5, speed=1.0,
                    v_max=1.5):
    """n agents evenly spaced on a circle; each goal is the antipode."""
    agents = []
    for i in range(n):
        a = 2.0 * math.pi * i / n
        p = (radius * math.cos(a), radius * math.sin(a))
        agents.append(Agent(p, (0.0, 0.0), agent_radius, v_max,
                            goal=(-p[0], -p[1]), speed=speed))
    return agents


def circle_perturbation(n=8, seed=13, magnitude=0.02):
    """Fixed small offsets of the preferred velocities (one per agent)
    that break the exact symmetry of the circle scenario."""
    rng = np.random.default_rng(seed)
    ang = rng.uniform(0.0, 2.0 * math.pi, n)
    return magnitude * np.stack([np.cos(ang), np.sin(ang)], axis=1)


def dance_scenario(offset=0.1, agent_radius=0.5, speed=1.0, v_max=1.5):
    """Two agents that swap places head-on, offset laterally by a little so
    that their choices are not perfectly symmetric."""
    a = Agent((-5.0, 0.0), (speed, 0.0), agent_radius, v_max,
              goal=(5.0, 0.0), speed=speed)
    b = Agent((5.0, offset), (-speed, 0.0), agent_radius, v_max,
              goal=(-5.0, offset), speed=speed)
    return [a, b]


# ---------------------------------------------------------------------
# 7. The worked example of the chapter
# ---------------------------------------------------------------------
def worked_example(verbose=True):
    """Two agents; every number of the chapter's worked example."""
    tau = 4.0
    a = Agent((0.0, 0.0), (1.0, 0.0), 0.5, 1.5)
    b = Agent((4.0, 0.5), (-1.0, 0.0), 0.5, 1.5)
    a.v_pref, b.v_pref = (1.2, 0.0), (-1.2, 0.0)
    p = sub(b.position, a.position)
    r = a.radius + b.radius
    v_rel = sub(a.velocity, b.velocity)
    line_a = orca_half_plane(a, b, tau)
    line_b = orca_half_plane(b, a, tau)
    line_full = orca_half_plane(a, b, tau, reciprocal=False)
    v_a, ok_a = orca_velocity([line_a.half_plane()], a.v_pref, a.v_max)
    v_b, ok_b = orca_velocity([line_b.half_plane()], b.v_pref, b.v_max)
    v_full, _ = orca_velocity([line_full.half_plane()], a.v_pref, a.v_max)
    theta = math.degrees(math.asin(r / norm(p)))
    phi = math.degrees(math.atan2(p[1], p[0]))
    q = add(v_rel, line_a.u)
    new_rel = sub(v_a, v_b)
    ang_new = phi - math.degrees(math.atan2(new_rel[1], new_rel[0]))
    full_rel = sub(v_full, b.velocity)
    ang_full = phi - math.degrees(math.atan2(full_rel[1], full_rel[0]))
    out = {"tau": tau, "p": p, "r": r, "phi": phi, "theta": theta,
           "centre": scale(p, 1.0 / tau), "rho": r / tau,
           "v_rel": v_rel, "case": line_a.case, "q": q, "u": line_a.u,
           "n": line_a.normal, "point_a": line_a.point,
           "point_b": line_b.point, "n_b": line_b.normal,
           "v_new_a": v_a, "v_new_b": v_b, "feasible": ok_a and ok_b,
           "angle_new_rel": ang_new,
           "point_full": line_full.point, "v_new_full": v_full,
           "angle_full_rel": ang_full,
           "violation_pref": line_a.half_plane().violation(a.v_pref),
           "violation_pref_full": line_full.half_plane().violation(a.v_pref)}
    if verbose:
        f = "{:>16s} = {}"
        for key, val in out.items():
            if isinstance(val, tuple):
                val = "(" + ", ".join("{:.4f}".format(x) for x in val) + ")"
            elif isinstance(val, float):
                val = "{:.4f}".format(val)
            print(f.format(key, val))
    return out


# ---------------------------------------------------------------------
# 8. Self-test
# ---------------------------------------------------------------------
def _close(a, b, tol=1e-7):
    return all(abs(x - y) <= tol for x, y in zip(a, b))


def _check_boundary(p, v_rel, r, tau, dt=0.1):
    """q = v_rel + u lies on the boundary of VO^tau and n points outward."""
    u, n, case = vo_closest_boundary_point(p, v_rel, r, tau, dt)
    assert abs(norm(n) - 1.0) < 1e-9
    assert abs(cross(u, n)) < 1e-9, "u must be parallel to n"
    q = add(v_rel, u)
    horizon = tau if case != "overlap" else dt
    if case != "overlap":
        inside = in_velocity_obstacle(p, sub(q, scale(n, 1e-4)), r, horizon)
        outside = in_velocity_obstacle(p, add(q, scale(n, 1e-4)), r, horizon)
        assert inside and not outside, (case, inside, outside)
    else:
        t = ray_circle_intersection((0.0, 0.0), q, p, r)
        assert t == 0.0  # still overlapping at t = 0, separated after dt
        d_after = norm(sub(p, scale(add(q, scale(n, 1e-4)), dt)))
        assert d_after > r
    return case


def _self_test():
    t0 = time.time()
    # -- 1. the case analysis of the closest boundary point ---------------
    p, r, tau = (4.0, 0.5), 1.0, 4.0
    cases = {_check_boundary(p, (2.0, 0.0), r, tau),        # right leg
             _check_boundary(p, (1.5, 0.9), r, tau),        # left leg
             _check_boundary(p, (0.4, 0.05), r, tau),       # disc, outside
             _check_boundary(p, (1.0, 0.1), r, tau),        # disc, inside
             _check_boundary((0.6, 0.2), (0.3, 0.0), r, tau)}  # overlap
    assert cases == {"right leg", "left leg", "disc", "overlap"}, cases
    # -- 2. reciprocity: half vs full responsibility, symmetry -------------
    a = Agent((0.0, 0.0), (1.0, 0.0), 0.5, 1.5)
    b = Agent((4.0, 0.5), (-1.0, 0.0), 0.5, 1.5)
    half = orca_half_plane(a, b, tau)
    full = orca_half_plane(a, b, tau, reciprocal=False)
    assert _close(sub(full.point, a.velocity),
                  scale(sub(half.point, a.velocity), 2.0))
    assert _close(full.normal, half.normal) and _close(full.u, half.u)
    mirror = orca_half_plane(b, a, tau)
    assert _close(mirror.u, scale(half.u, -1.0))
    assert _close(mirror.normal, scale(half.normal, -1.0))
    # -- 3. the worked example --------------------------------------------
    ex = worked_example(verbose=False)
    assert ex["case"] == "right leg" and ex["feasible"]
    assert abs(ex["angle_new_rel"] - ex["theta"]) < 1e-6   # on the boundary
    assert abs(ex["angle_full_rel"] - ex["theta"]) < 1e-6
    assert half.half_plane().contains(ex["v_new_a"])
    # the new relative velocity lies on the boundary of VO^tau: the discs
    # graze at most, so the centre distance never drops below r
    d_min = min(norm(sub(add(b.position, scale(ex["v_new_b"], t)),
                         add(a.position, scale(ex["v_new_a"], t))))
                for t in np.linspace(0.0, 2.0 * tau, 4001))
    assert d_min >= a.radius + b.radius - 1e-6, d_min
    # -- 4. the linear program on random feasible instances ----------------
    rng = np.random.default_rng(13)
    grid = velocity_samples(1.5, rings=60, directions=360)
    for _ in range(200):
        v_max = 1.5
        v0 = rng.uniform(-1.0, 1.0, 2) * 0.7          # a feasible point
        lines = []
        for _k in range(rng.integers(1, 9)):
            ang = rng.uniform(0.0, 2.0 * math.pi)
            n = (math.cos(ang), math.sin(ang))
            s = rng.uniform(0.0, 1.0)
            lines.append(HalfPlane(sub(tuple(v0), scale(n, s)), n))
        v_pref = tuple(rng.uniform(-2.0, 2.0, 2))
        v, feasible = orca_velocity(lines, v_pref, v_max)
        assert feasible and norm(v) <= v_max + 1e-9
        assert all(line.contains(v, 1e-9) for line in lines)
        ok = np.ones(len(grid), dtype=bool)
        for line in lines:
            ok &= (grid - np.asarray(line.point)) @ np.asarray(line.normal) >= 0.0
        best_grid = np.hypot(grid[ok, 0] - v_pref[0], grid[ok, 1] - v_pref[1]).min()
        assert norm(sub(v, v_pref)) <= best_grid + 1e-9
    # -- 5. the dense fallback on infeasible instances ---------------------
    for _ in range(100):
        lines = []
        for _k in range(rng.integers(3, 8)):
            ang = rng.uniform(0.0, 2.0 * math.pi)
            n = (math.cos(ang), math.sin(ang))
            lines.append(HalfPlane(scale(n, rng.uniform(0.5, 2.5)), n))
        v_pref = tuple(rng.uniform(-1.0, 1.0, 2))
        v, feasible = orca_velocity(lines, v_pref, 1.5)
        if feasible:
            continue
        assert norm(v) <= 1.5 + 1e-9
        worst = max(line.violation(v) for line in lines)
        pen = np.zeros(len(grid))
        for line in lines:
            pen = np.maximum(pen, -((grid - np.asarray(line.point))
                                    @ np.asarray(line.normal)))
        assert worst <= pen.min() + 1e-6, (worst, pen.min())
    # -- 6. two agents: VO dances, RVO and ORCA do not ----------------------
    res = {m: simulate(dance_scenario(), m, tau=5.0, dt=0.1, steps=100)
           for m in ("vo", "rvo", "orca")}
    for m in res:
        assert res[m]["collision_steps"] == 0, m
    assert reversals(res["vo"], 0) >= 10 * max(1, reversals(res["rvo"], 0))
    assert velocity_variation(res["vo"], 0) > 5 * velocity_variation(res["rvo"], 0)
    assert velocity_variation(res["orca"], 0) < velocity_variation(res["vo"], 0)
    # -- 7. eight agents on a circle ----------------------------------------
    pert = circle_perturbation()
    none = simulate(circle_scenario(), "none", steps=300, perturbation=pert)
    orca = simulate(circle_scenario(), "orca", steps=300, perturbation=pert)
    assert none["collision_steps"] > 0
    assert orca["collision_steps"] == 0 and orca["infeasible_steps"] == 0
    assert orca["min_separation"].min() >= 1.0 - 1e-9
    assert np.all(np.isfinite(orca["arrival"]))
    print("self-test passed in {:.1f} s".format(time.time() - t0))


if __name__ == "__main__":
    worked_example(verbose=True)
    _self_test()
