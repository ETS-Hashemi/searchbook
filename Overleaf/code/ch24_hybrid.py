"""Chapter 24 -- The Hybrid Collision-Avoidance Architecture.

An integrated simulation of the four-layer architecture on a hybrid
grid/continuous world, combining simplified copies of the modules of the
earlier chapters so that this file stands alone:

* global layer  : space-time A* and conflict-based search (ch04, ch09),
                  conflict detection over padded paths (ch07);
* prediction    : a constant-velocity Kalman filter for the intruder with
                  covariance propagation over a horizon (ch18, ch20);
* local safety  : ORCA half-planes and the incremental linear program
                  (ch13), reciprocal for teammates, full responsibility for
                  the intruder, whose radius is inflated by the prediction
                  uncertainty;
* replanning    : space-time A* from the current cell over the time-indexed
                  grid with the predicted intruder cells blocked and the
                  teammates' paths reserved.  A D* Lite repair (ch05) would
                  reuse the previous search; a fresh A* replan is used here
                  because it is simpler and the instances are small.  The
                  interface (current cell, reservation, blocked cells per
                  time layer) is the same for both;
* decision logic: the per-drone state machine Nominal / Avoiding /
                  Reconnecting / Replanning with the safety-horizon
                  trigger, the reconnection search, the replanning trigger
                  and the conflict re-check with a local CBS repair.

Units: cells are 1 m squares, the grid time step is 1 s (cruise speed
1 m/s), the control cycle is DT = 0.1 s.  Cell (x, y) has its centre at
(x + 0.5, y + 0.5).  A time-indexed path is a list of cells; path[j] is the
cell occupied at absolute time t0 + j, and the drone parks at path[-1].

Run the self-test with
    python3 ch24_hybrid.py
"""
from __future__ import annotations

import heapq
import itertools
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Set, Tuple

import numpy as np

Cell = Tuple[int, int]
INF = float("inf")
EPS = 1e-9
DT = 0.1                      # control cycle of the local layer, s

# ---------------------------------------------------------------------
# 1. The world model: grid, obstacles, conversions
# ---------------------------------------------------------------------


class Grid:
    """A 4-connected grid of unit cells with a set of blocked cells."""

    def __init__(self, cols: int, rows: int, obstacles: Sequence[Cell] = ()):
        self.cols, self.rows = cols, rows
        self.obstacles: Set[Cell] = set(obstacles)

    def free(self, c: Cell) -> bool:
        x, y = c
        return 0 <= x < self.cols and 0 <= y < self.rows and c not in self.obstacles

    def neighbours(self, c: Cell) -> List[Cell]:
        x, y = c
        return [n for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))
                if self.free(n)]

    def distances(self, goal: Cell) -> Dict[Cell, int]:
        """True static distances to ``goal`` by breadth-first search."""
        dist = {goal: 0}
        queue = [goal]
        for c in queue:
            for n in self.neighbours(c):
                if n not in dist:
                    dist[n] = dist[c] + 1
                    queue.append(n)
        return dist

    def clearance(self, p) -> float:
        """Distance from the point p to the nearest obstacle cell or border."""
        best = min(p[0], p[1], self.cols - p[0], self.rows - p[1])
        for (x, y) in self.obstacles:
            dx = max(x - p[0], 0.0, p[0] - (x + 1))
            dy = max(y - p[1], 0.0, p[1] - (y + 1))
            best = min(best, math.hypot(dx, dy))
        return best


def centre(c: Cell):
    """Continuous position of the centre of a cell (grid -> world)."""
    return np.array([c[0] + 0.5, c[1] + 0.5])


def nearest_cell(p) -> Cell:
    """Cell that contains the point p (world -> grid)."""
    return (int(math.floor(p[0])), int(math.floor(p[1])))


def path_position(path: Sequence[Cell], t0: float, t: float):
    """Reference position of a time-indexed path at continuous time t:
    linear interpolation between the cells of steps floor and ceil."""
    s = t - t0
    if s <= 0:
        return centre(path[0])
    j = int(math.floor(s))
    if j >= len(path) - 1:
        return centre(path[-1])
    a, b = centre(path[j]), centre(path[j + 1])
    return a + (s - j) * (b - a)


# ---------------------------------------------------------------------
# 2. Global layer: reservations, space-time A*, conflicts, CBS
# ---------------------------------------------------------------------


class Reservation:
    """Vertex/edge constraints, parked agents and time-layered blocked cells.

    ``vertex`` holds (cell, t), ``edge`` holds (u, v, t) forbidding the move
    u -> v between t and t+1, ``parked`` maps a cell to the time from which
    it is occupied for ever, and ``layers`` maps a time to the set of cells
    blocked at that time (the predicted intruder cells)."""

    def __init__(self):
        self.vertex: Set[Tuple[Cell, int]] = set()
        self.edge: Set[Tuple[Cell, Cell, int]] = set()
        self.parked: Dict[Cell, int] = {}
        self.layers: Dict[int, Set[Cell]] = {}

    def add_path(self, path: Sequence[Cell], t0: int) -> None:
        """Reserve a whole path (vertices, reverse edges, parked goal)."""
        for j, v in enumerate(path):
            self.vertex.add((v, t0 + j))
        for j in range(len(path) - 1):
            if path[j] != path[j + 1]:
                self.edge.add((path[j + 1], path[j], t0 + j))
        self.parked[path[-1]] = t0 + len(path) - 1

    def block(self, cell: Cell, t: int) -> None:
        self.layers.setdefault(t, set()).add(cell)

    def vertex_blocked(self, v: Cell, t: int) -> bool:
        return ((v, t) in self.vertex or t >= self.parked.get(v, INF)
                or v in self.layers.get(t, ()))

    def edge_blocked(self, u: Cell, v: Cell, t: int) -> bool:
        return (u, v, t) in self.edge

    def last_time(self, v: Cell) -> float:
        """Largest time at which v is blocked (-1 never, inf if parked on)."""
        if v in self.parked:
            return INF
        times = [t for (u, t) in self.vertex if u == v]
        times += [t for t, cells in self.layers.items() if v in cells]
        return max(times, default=-1)

    def horizon(self) -> int:
        times = [t for (_, t) in self.vertex] + [t + 1 for (_, _, t) in self.edge]
        times += list(self.parked.values()) + list(self.layers)
        return max(times, default=-1)


@dataclass(frozen=True)
class Constraints:
    """CBS constraints of one agent: vertex <v, t> and edge <u, v, t>."""
    vertex: frozenset = frozenset()
    edge: frozenset = frozenset()

    def add_vertex(self, v: Cell, t: int) -> "Constraints":
        return Constraints(self.vertex | {(v, t)}, self.edge)

    def add_edge(self, u: Cell, v: Cell, t: int) -> "Constraints":
        return Constraints(self.vertex, self.edge | {(u, v, t)})

    def last_time(self) -> int:
        times = [t for _, t in self.vertex] + [t + 1 for _, _, t in self.edge]
        return max(times, default=-1)


def space_time_astar(grid: Grid, start: Cell, goal: Cell, t0: int = 0,
                     cons: Constraints = Constraints(),
                     res: Optional[Reservation] = None,
                     dist: Optional[Dict[Cell, int]] = None) -> Optional[List[Cell]]:
    """Space-time A* (ch04) from (start, t0): states (v, t), unit-cost moves
    and waits, CBS constraints ``cons``, a reservation ``res`` of the other
    agents and of the predicted intruder cells, the goal-stay test and the
    horizon T_max = H + 1 + D.  Returns path[j] = cell at time t0 + j."""
    dist = dist if dist is not None else grid.distances(goal)
    if start not in dist:
        return None
    goal_block = max((t for v, t in cons.vertex if v == goal), default=-1)
    if res is not None:
        goal_block = max(goal_block, res.last_time(goal))
    if goal_block == INF:
        return None
    last = max(cons.last_time(), res.horizon() if res is not None else -1, t0)
    horizon = last + 1 + max(dist.values())
    counter = itertools.count()
    parent: Dict[Tuple[Cell, int], Tuple[Cell, int]] = {}
    heap = [(dist[start], -t0, next(counter), (start, t0))]
    closed = set()
    while heap:
        _, _, _, state = heapq.heappop(heap)
        if state in closed:
            continue
        closed.add(state)
        v, t = state
        if v == goal and t > goal_block:
            path = [v]
            while state in parent:
                state = parent[state]
                path.append(state[0])
            return path[::-1]
        if t >= horizon:
            continue
        for w in grid.neighbours(v) + [v]:
            nxt = (w, t + 1)
            if nxt in closed or nxt in cons.vertex or (v, w, t) in cons.edge:
                continue
            if res is not None and (res.vertex_blocked(w, t + 1)
                                    or res.edge_blocked(v, w, t)):
                continue
            if nxt not in parent:                 # g = t + 1: first is best
                parent[nxt] = state
                heapq.heappush(heap, (t + 1 + dist[w], -(t + 1), next(counter), nxt))
    return None


@dataclass(frozen=True)
class Conflict:
    """A vertex conflict <i, j, v, t> (u is None) or a swap <i, j, u, v, t>."""
    i: int
    j: int
    u: Optional[Cell]
    v: Cell
    t: int

    def __str__(self) -> str:
        if self.u is None:
            return "<%s,%s,%s,%d>" % (self.i, self.j, self.v, self.t)
        return "<%s,%s,%s->%s,%d>" % (self.i, self.j, self.u, self.v, self.t)


def cell_at(path: Sequence[Cell], t0: int, t: int) -> Cell:
    """Cell of a path at absolute time t, padded at both ends (ch07)."""
    return path[max(0, min(t - t0, len(path) - 1))]


def first_conflict(paths: Sequence[Sequence[Cell]], starts: Sequence[int],
                   ids: Sequence = None, t_from: int = 0) -> Optional[Conflict]:
    """Earliest vertex or swapping conflict among time-indexed paths whose
    first cells are at the absolute times ``starts`` (conflict detection of
    ch07 over the padded paths, from time t_from to the common horizon)."""
    ids = list(range(len(paths))) if ids is None else list(ids)
    horizon = max(s + len(p) for s, p in zip(starts, paths))
    for t in range(t_from, horizon + 1):
        for a in range(len(paths)):
            for b in range(a + 1, len(paths)):
                va, vb = cell_at(paths[a], starts[a], t), cell_at(paths[b], starts[b], t)
                if va == vb:
                    return Conflict(ids[a], ids[b], None, va, t)
                if t + 1 <= horizon:
                    wa = cell_at(paths[a], starts[a], t + 1)
                    wb = cell_at(paths[b], starts[b], t + 1)
                    if va == wb and vb == wa and va != wa:
                        return Conflict(ids[a], ids[b], va, wa, t)
    return None


@dataclass
class CTNode:
    cons: Tuple[Constraints, ...]
    paths: List[List[Cell]]
    cost: int
    n: int = 0


def cbs(grid: Grid, starts: Sequence[Cell], goals: Sequence[Cell], t0: int = 0,
        res: Optional[Reservation] = None, node_limit: int = 5000):
    """Conflict-based search (ch09) for agents starting at time t0, with an
    optional reservation of outside agents.  Returns (paths, expansions)."""
    dists = [grid.distances(g) for g in goals]
    k = len(starts)
    ids = itertools.count()
    paths = [space_time_astar(grid, s, g, t0, Constraints(), res, d)
             for s, g, d in zip(starts, goals, dists)]
    if any(p is None for p in paths):
        return None, 0
    root = CTNode(tuple(Constraints() for _ in range(k)), paths,
                  sum(len(p) - 1 for p in paths), next(ids))
    heap = [(root.cost, root.n, root)]
    expanded = 0
    while heap and expanded < node_limit:
        _, _, node = heapq.heappop(heap)
        expanded += 1
        conflict = first_conflict(node.paths, [t0] * k)
        if conflict is None:
            return node.paths, expanded
        for agent in (conflict.i, conflict.j):
            if conflict.u is None:
                extra = node.cons[agent].add_vertex(conflict.v, conflict.t)
            else:                                  # the swap seen from ``agent``
                u, v = (conflict.u, conflict.v) if agent == conflict.i else (conflict.v, conflict.u)
                extra = node.cons[agent].add_edge(u, v, conflict.t)
            path = space_time_astar(grid, starts[agent], goals[agent], t0, extra,
                                    res, dists[agent])
            if path is None:
                continue
            cons = list(node.cons)
            cons[agent] = extra
            new_paths = list(node.paths)
            new_paths[agent] = path
            child = CTNode(tuple(cons), new_paths, sum(len(p) - 1 for p in new_paths),
                           next(ids))
            heapq.heappush(heap, (child.cost, child.n, child))
    return None, expanded


# ---------------------------------------------------------------------
# 3. Prediction layer: constant-velocity Kalman filter (ch18, ch20)
# ---------------------------------------------------------------------


class IntruderTracker:
    """Kalman filter with the constant-velocity model x = (px, py, vx, vy),
    white-noise-acceleration process noise of intensity q and position
    measurements of noise sigma_z; ``predict_horizon`` propagates the mean
    and the covariance over a horizon without measurements."""

    def __init__(self, dt: float, q: float, sigma_z: float):
        self.dt, self.q, self.sigma_z = dt, q, sigma_z
        self.F = np.array([[1, 0, dt, 0], [0, 1, 0, dt], [0, 0, 1, 0], [0, 0, 0, 1.0]])
        d2, d3, d4 = dt ** 2, dt ** 3 / 2, dt ** 4 / 4
        self.Q = q * np.array([[d4, 0, d3, 0], [0, d4, 0, d3],
                               [d3, 0, d2, 0], [0, d3, 0, d2]])
        self.H = np.array([[1, 0, 0, 0], [0, 1, 0, 0.0]])
        self.R = sigma_z ** 2 * np.eye(2)
        self.x: Optional[np.ndarray] = None
        self.P: Optional[np.ndarray] = None
        self.n_updates = 0

    def update(self, z) -> None:
        z = np.asarray(z, dtype=float)
        if self.x is None:                       # initialise from the first fix
            self.x = np.array([z[0], z[1], 0.0, 0.0])
            self.P = np.diag([self.sigma_z ** 2, self.sigma_z ** 2, 1.0, 1.0])
            self.n_updates = 1
            return
        x, P = self.F @ self.x, self.F @ self.P @ self.F.T + self.Q      # predict
        S = self.H @ P @ self.H.T + self.R
        K = P @ self.H.T @ np.linalg.inv(S)                              # gain
        self.x = x + K @ (z - self.H @ x)
        self.P = (np.eye(4) - K @ self.H) @ P
        self.n_updates += 1

    @property
    def position(self):
        return self.x[:2].copy()

    @property
    def velocity(self):
        return self.x[2:].copy()

    def predict_horizon(self, n_steps: int):
        """Means and position covariances at 0, dt, ..., n_steps*dt ahead."""
        means, covs = [self.x[:2].copy()], [self.P[:2, :2].copy()]
        x, P = self.x.copy(), self.P.copy()
        for _ in range(n_steps):
            x, P = self.F @ x, self.F @ P @ self.F.T + self.Q
            means.append(x[:2].copy())
            covs.append(P[:2, :2].copy())
        return means, covs


def sigma_max(cov) -> float:
    """Largest standard deviation of a 2x2 covariance: sqrt(lambda_max)."""
    return math.sqrt(max(np.linalg.eigvalsh(cov)))


# ---------------------------------------------------------------------
# 4. Local safety layer: ORCA (copied from ch13_orca.py, condensed)
# ---------------------------------------------------------------------


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


def _cross(a, b):
    return a[0] * b[1] - a[1] * b[0]


class HalfPlane:
    """The closed half-plane {v : (v - point) . normal >= 0}."""

    def __init__(self, point, normal):
        self.point, self.normal = (float(point[0]), float(point[1])), (float(normal[0]), float(normal[1]))

    @property
    def direction(self):
        return (self.normal[1], -self.normal[0])

    def violation(self, v):
        return -_dot((v[0] - self.point[0], v[1] - self.point[1]), self.normal)


def vo_closest_boundary_point(p, v_rel, r, tau, dt):
    """Smallest change u from v_rel to the boundary of VO^tau and the
    outward normal n at that point (ch13, all four cases)."""
    dist2, r2 = _dot(p, p), r * r
    if dist2 > r2:
        c = (p[0] / tau, p[1] / tau)
        rho = r / tau
        w = (v_rel[0] - c[0], v_rel[1] - c[1])
        w2, wp = _dot(w, w), _dot(w, p)
        if wp < 0.0 and wp * wp > r2 * w2:                # truncating disc
            w_len = math.sqrt(w2)
            n = (w[0] / w_len, w[1] / w_len)
            return (n[0] * (rho - w_len), n[1] * (rho - w_len)), n
        leg = math.sqrt(dist2 - r2)
        if _cross(p, w) > 0.0:                            # left leg
            d = ((p[0] * leg - p[1] * r) / dist2, (p[0] * r + p[1] * leg) / dist2)
            n = (-d[1], d[0])
        else:                                             # right leg
            d = ((p[0] * leg + p[1] * r) / dist2, (-p[0] * r + p[1] * leg) / dist2)
            n = (d[1], -d[0])
        s = _dot(v_rel, d)
        return (d[0] * s - v_rel[0], d[1] * s - v_rel[1]), n
    c = (p[0] / dt, p[1] / dt)                            # already overlapping
    rho = r / dt
    w = (v_rel[0] - c[0], v_rel[1] - c[1])
    w_len = math.hypot(*w)
    if w_len > EPS:
        n = (w[0] / w_len, w[1] / w_len)
    elif dist2 > 0.0:
        d = math.sqrt(dist2)
        n = (-p[0] / d, -p[1] / d)
    else:
        n = (1.0, 0.0)
    return (n[0] * (rho - w_len), n[1] * (rho - w_len)), n


def orca_half_plane(p_a, v_a, r_a, p_b, v_b, r_b, tau, dt=DT, share=0.5) -> HalfPlane:
    """ORCA half-plane of agent A induced by B: share 1/2 for a reciprocal
    teammate, 1 (full responsibility) for a non-cooperative intruder."""
    p = (p_b[0] - p_a[0], p_b[1] - p_a[1])
    v_rel = (v_a[0] - v_b[0], v_a[1] - v_b[1])
    u, n = vo_closest_boundary_point(p, v_rel, r_a + r_b, tau, dt)
    return HalfPlane((v_a[0] + share * u[0], v_a[1] + share * u[1]), n)


def _lp_on_line(lines, i, v_max, v_opt, direction_opt):
    line = lines[i]
    d, q = line.direction, line.point
    b = _dot(q, d)
    disc = b * b + v_max * v_max - _dot(q, q)
    if disc < 0.0:
        return None
    root = math.sqrt(disc)
    t_left, t_right = -b - root, -b + root
    for j in range(i):
        dj = lines[j].direction
        den = _cross(d, dj)
        num = _cross(dj, (q[0] - lines[j].point[0], q[1] - lines[j].point[1]))
        if abs(den) <= EPS:
            if num < 0.0:
                return None
            continue
        t = num / den
        if den >= 0.0:
            t_right = min(t_right, t)
        else:
            t_left = max(t_left, t)
        if t_left > t_right:
            return None
    if direction_opt:
        t = t_right if _dot(v_opt, d) > 0.0 else t_left
    else:
        t = min(max(_dot(d, (v_opt[0] - q[0], v_opt[1] - q[1])), t_left), t_right)
    return (q[0] + d[0] * t, q[1] + d[1] * t)


def lp_incremental(lines, v_max, v_opt, direction_opt=False):
    """Incremental 2D linear program of RVO2 (ch13): the point of the
    intersection of the half-planes and the speed disc closest to v_opt."""
    if direction_opt:
        v = (v_opt[0] * v_max, v_opt[1] * v_max)
    elif _dot(v_opt, v_opt) > v_max * v_max:
        s = v_max / math.hypot(*v_opt)
        v = (v_opt[0] * s, v_opt[1] * s)
    else:
        v = (float(v_opt[0]), float(v_opt[1]))
    for i, line in enumerate(lines):
        if line.violation(v) > 0.0:
            new_v = _lp_on_line(lines, i, v_max, v_opt, direction_opt)
            if new_v is None:
                return v, i
            v = new_v
    return v, len(lines)


def lp_dense(lines, begin, v_max, v):
    """Dense fallback: minimise the largest penetration (RVO2 linearProgram3)."""
    depth = 0.0
    for i in range(begin, len(lines)):
        if lines[i].violation(v) <= depth:
            continue
        proj = []
        for j in range(i):
            li, lj = lines[i], lines[j]
            den = _cross(li.direction, lj.direction)
            if abs(den) <= EPS:
                if _dot(li.direction, lj.direction) > 0.0:
                    continue
                point = ((li.point[0] + lj.point[0]) / 2, (li.point[1] + lj.point[1]) / 2)
            else:
                t = _cross(lj.direction, (li.point[0] - lj.point[0], li.point[1] - lj.point[1])) / den
                point = (li.point[0] + li.direction[0] * t, li.point[1] + li.direction[1] * t)
            dd = (lj.direction[0] - li.direction[0], lj.direction[1] - li.direction[1])
            nn = math.hypot(*dd)
            dd = (dd[0] / nn, dd[1] / nn)
            proj.append(HalfPlane(point, (-dd[1], dd[0])))
        cand, k = lp_incremental(proj, v_max, lines[i].normal, True)
        if k == len(proj):
            v = cand
        depth = lines[i].violation(v)
    return v


def orca_velocity(lines, v_pref, v_max):
    """Velocity closest to v_pref inside all half-planes; (v, feasible)."""
    v, k = lp_incremental(lines, v_max, v_pref)
    if k < len(lines):
        return lp_dense(lines, k, v_max, v), False
    return v, True


# ---------------------------------------------------------------------
# 5. Parameters of the architecture and of the worked scenario
# ---------------------------------------------------------------------

PARAMS = dict(
    v_cruise=1.0, v_max=1.5, a_max=1.0,     # drone limits, m/s and m/s^2
    r_drone=0.3, r_intruder=0.3, margin=0.1,  # radii and safety margin, m
    tau_h=3.0,                # safety horizon, s (= ORCA tau)
    kappa=2.45,               # inflation: sqrt(-2 ln 0.05), the 95 % disc in 2D
    t_pred=5.0,               # prediction horizon of the tracker, s
    sense_range=6.0,          # detection range for the intruder, m
    n_warm=10,                # filter updates before its prediction is trusted
    n_clear=5,                # cycles without predicted conflict before Reconnecting
    k_look=6,                 # waypoints searched forward by Reconnect
    delay_max=1,              # largest admissible delay (time shift), steps
    drift_max=3.5,            # largest tolerated drift from the plan, m
    t_avoid_max=8.0,          # longest stay in Avoiding, s
    r_comm=8.5,               # communication range, m
    ell_act=7.5,              # link length at which the communication pull acts, m
    k_form=0.5,               # formation correction gain, 1/s
    k_comm=1.0,               # gain of the soft communication-range term, 1/s
    period_prediction=0.1,    # rate of the prediction layer, s (control cycle: DT)
    replan_period=1.0,        # a drone replans at most once per this many seconds
    sigma_z=0.15, q_kf=0.05,  # measurement noise (m) and process noise of the KF
    seed=24,
)


def worked_scenario():
    """The instance of the worked scenario: a 14 x 9 grid, three swarm
    drones and one intruder flying head-on along the lane of drone A."""
    grid = Grid(14, 9, obstacles=[(3, 6), (4, 6), (7, 5), (8, 5), (9, 1), (10, 1), (3, 0), (10, 7)])
    starts = [(0, 4), (6, 8), (0, 2)]
    goals = [(13, 4), (6, 0), (13, 2)]
    names = ["A", "B", "C"]
    intruder = dict(p0=np.array([12.5, 4.3]), v=np.array([-0.6, 0.0]))
    formation = {("A", "C"): np.array([0.0, -2.0])}   # desired p_C - p_A
    return grid, starts, goals, names, intruder, formation


# ---------------------------------------------------------------------
# 6. The per-drone decision logic
# ---------------------------------------------------------------------

NOMINAL, AVOIDING, RECONNECTING, REPLANNING = "Nominal", "Avoiding", "Reconnecting", "Replanning"


@dataclass
class Drone:
    name: str
    goal: Cell
    pos: np.ndarray
    vel: np.ndarray = field(default_factory=lambda: np.zeros(2))
    path: List[Cell] = field(default_factory=list)   # current time-indexed plan
    t0: int = 0                                      # absolute time of path[0]
    state: str = NOMINAL
    target: Optional[np.ndarray] = None              # reconnection waypoint
    target_time: float = 0.0
    target_index: int = 0
    t_state: float = 0.0                             # time of the last transition
    clear_count: int = 0
    replans: int = 0
    reconnections: int = 0
    t_last_replan: float = -INF

    def plan_position(self, t: float):
        return path_position(self.path, self.t0, t)

    def arrived(self, t: float) -> bool:
        return (t >= self.t0 + len(self.path) - 1
                and np.linalg.norm(self.pos - centre(self.goal)) < 0.15)


class HybridSimulation:
    """The integrated simulation: one control loop per drone per cycle."""

    def __init__(self, params=None, scenario=None):
        self.p = dict(PARAMS)
        if params:
            self.p.update(params)
        grid, starts, goals, names, intr, formation = scenario or worked_scenario()
        self.grid, self.names, self.formation = grid, names, formation
        self.rng = np.random.default_rng(self.p["seed"])
        self.R_safe = self.p["r_drone"] + self.p["r_intruder"] + self.p["margin"]
        self.R_mate = 2 * self.p["r_drone"] + self.p["margin"]
        # global layer: nominal plan by CBS
        paths, self.cbs_expansions = cbs(grid, starts, goals)
        assert paths is not None, "CBS found no nominal plan"
        self.nominal = [list(p) for p in paths]
        self.drones = [Drone(n, g, centre(s), path=list(p))
                       for n, s, g, p in zip(names, starts, goals, paths)]
        # intruder: true motion and tracker
        self.intr_p0, self.intr_v = intr["p0"].astype(float), intr["v"].astype(float)
        self.tracker = IntruderTracker(DT, self.p["q_kf"], self.p["sigma_z"])
        self.detected_at: Optional[float] = None
        self.t = 0.0
        self.log: List[Tuple[float, str, str, str, str]] = []
        self.d_min_intruder, self.d_min_mates = INF, INF
        self.history: List[dict] = []
        self.recheck_log: List[dict] = []
        self.reconnect_log: List[dict] = []
        self.trigger_profiles: List[dict] = []
        self.replan_log: List[dict] = []
        self.orca_infeasible = 0
        self.clock = RateSchedule({"control": DT, "prediction": self.p["period_prediction"]})
        self.pred = None

    # -- world -----------------------------------------------------------
    def intruder_true(self, t: Optional[float] = None):
        t = self.t if t is None else t
        return self.intr_p0 + self.intr_v * t

    def others(self, d: Drone) -> List[Drone]:
        return [o for o in self.drones if o is not d]

    # -- prediction and trigger --------------------------------------------
    def prediction(self):
        """Predicted intruder means/covariances at multiples of DT, or None."""
        if self.tracker.x is None or self.tracker.n_updates < self.p["n_warm"]:
            return None                          # the filter has not converged yet
        n = int(round(self.p["t_pred"] / DT))
        return self.tracker.predict_horizon(n)

    def intended_positions(self, d: Drone, times):
        """Where the drone intends to be at the given future times if it
        heads for its next waypoint and then follows its plan at cruise
        speed (the intended motion used by the trigger and by Reconnect)."""
        poly = [d.pos.copy()]
        if d.state == RECONNECTING and d.target is not None:
            poly.append(d.target.copy())
            k = d.target_index + 1
        else:
            k = max(0, int(math.ceil(self.t - d.t0 + 1e-9)))
        poly.extend(centre(c) for c in d.path[k:])
        seg = [(poly[i], poly[i + 1], float(np.linalg.norm(poly[i + 1] - poly[i])))
               for i in range(len(poly) - 1)]
        out = []
        for s in times:
            dist = self.p["v_cruise"] * s
            pt = poly[-1]
            for a, b, L in seg:
                if dist <= L:
                    pt = a + (b - a) * (dist / L if L > 0 else 0.0)
                    break
                dist -= L
            out.append(pt)
        return out

    def conflict_profile(self, d: Drone, pred):
        """Over the safety horizon: the look-ahead times s, the predicted
        separation sep(s) and the uncertainty inflation kappa*sigma(s)."""
        means, covs = pred
        n = min(int(round(self.p["tau_h"] / DT)), len(means) - 1)
        times = [i * DT for i in range(n + 1)]
        own = self.intended_positions(d, times)
        sep = [float(np.linalg.norm(own[i] - means[i])) for i in range(n + 1)]
        infl = [self.p["kappa"] * sigma_max(covs[i]) for i in range(n + 1)]
        return times, sep, infl, own

    def predicted_conflict(self, d: Drone, pred):
        """(inside, t_c, worst margin): the safety-horizon test of the
        chapter.  A conflict is inside the horizon when the predicted
        separation minus the uncertainty inflation drops below R_safe
        within tau_h seconds; t_c is the first such look-ahead time."""
        if pred is None:
            return False, None, INF
        times, sep, infl, _ = self.conflict_profile(d, pred)
        margin = [sep[i] - infl[i] - self.R_safe for i in range(len(times))]
        worst = min(margin)
        t_c = next((times[i] for i in range(len(times)) if margin[i] < 0), None)
        return t_c is not None, t_c, worst

    # -- local layer ---------------------------------------------------------
    def preferred_velocity(self, d: Drone, with_formation: bool):
        """Towards the next waypoint at cruise speed, with the formation and
        communication corrections when they are not relaxed."""
        if d.state == RECONNECTING and d.target is not None:
            remaining = max(d.target_time - self.t, DT)
            v = (d.target - d.pos) / remaining
        else:
            look = self.t + 0.5
            ref = d.plan_position(look)
            v = (ref - d.pos) / 0.5
            if np.linalg.norm(v) > self.p["v_cruise"] and self.t < d.t0 + len(d.path) - 1:
                v = v / np.linalg.norm(v) * self.p["v_cruise"]
        if with_formation:
            for (a, b), off in self.formation.items():
                if d.name == b:
                    leader = next(o for o in self.drones if o.name == a)
                    v = v + self.p["k_form"] * ((leader.pos + off) - d.pos)
        # communication: pull towards the nearest teammate if the link stretches
        mates = self.others(d)
        if mates:
            nearest = min(mates, key=lambda o: np.linalg.norm(o.pos - d.pos))
            gap = np.linalg.norm(nearest.pos - d.pos)
            if gap > self.p["ell_act"]:
                v = v + (self.p["k_comm"] * (gap - self.p["ell_act"])
                         * (nearest.pos - d.pos) / gap)
        n = np.linalg.norm(v)
        if n > self.p["v_max"]:
            v = v / n * self.p["v_max"]
        return v

    def local_layer(self, d: Drone, v_pref, pred, t_c, with_intruder: bool):
        """The local safety layer: ORCA half-planes of the teammates (always,
        reciprocal; inactive while everybody follows a conflict-free plan),
        of the nearby obstacle cells (closest points, full responsibility)
        and, when the drone is Avoiding, of the intruder with full
        responsibility and the radius inflated at the predicted conflict
        time.  Returns (velocity, feasible)."""
        tau = self.p["tau_h"]
        r_own = self.p["r_drone"] + self.p["margin"] / 2
        lines = []
        for o in self.others(d):
            if np.linalg.norm(o.pos - d.pos) < 2 * tau * self.p["v_max"]:
                lines.append(orca_half_plane(d.pos, d.vel, r_own, o.pos, o.vel, r_own, tau, share=0.5))
        for (x, y) in self.grid.obstacles:
            q = np.array([min(max(d.pos[0], x), x + 1.0), min(max(d.pos[1], y), y + 1.0)])
            if np.linalg.norm(q - d.pos) < 2.0:
                lines.append(orca_half_plane(d.pos, d.vel, r_own, q, np.zeros(2), 0.0, tau, share=1.0))
        if with_intruder and pred is not None:
            means, covs = pred
            i = min(int(round((t_c if t_c is not None else tau) / DT)), len(covs) - 1)
            r_b = self.p["r_intruder"] + self.p["margin"] + self.p["kappa"] * sigma_max(covs[i])
            lines.append(orca_half_plane(d.pos, d.vel, self.p["r_drone"], self.tracker.position,
                                         self.tracker.velocity, r_b, tau, share=1.0))
        v, feasible = orca_velocity(lines, tuple(v_pref), self.p["v_max"])
        if not feasible:
            self.orca_infeasible += 1
        return np.array(v), feasible

    # -- reconnection ------------------------------------------------------
    def segment_free(self, p, t_a, w, t_b, pred, d: Drone) -> bool:
        """Straight flight from p at t_a to w at t_b: clear of obstacles, of
        the inflated prediction and of the teammates' intended positions."""
        n = max(2, int(math.ceil((t_b - t_a) / DT)))
        mates = [(o, self.intended_positions(o, [t_a - self.t + (t_b - t_a) * i / n
                                                 for i in range(n + 1)]))
                 for o in self.others(d)]
        for i in range(n + 1):
            s = i / n
            q = p + (w - p) * s
            t = t_a + (t_b - t_a) * s
            if self.grid.clearance(q) < self.p["r_drone"]:
                return False
            if pred is not None:
                means, covs = pred
                j = min(int(round((t - self.t) / DT)), len(means) - 1)
                if (np.linalg.norm(q - means[j]) - self.p["kappa"] * sigma_max(covs[j])
                        < self.R_safe):
                    return False
            for o, pts in mates:
                if np.linalg.norm(q - pts[i]) < self.R_mate:
                    return False
        return True

    def reconnect(self, d: Drone, pred):
        """Search forward along the nominal path for a waypoint that can be
        reached by a collision-free straight flight, with a delay of at
        most delay_max steps.  Returns (k, delay, reason, candidates tried)."""
        k0 = max(0, int(math.ceil(self.t - d.t0 + 1e-9)))
        last = len(d.path) - 1
        tried = []
        for delay in range(self.p["delay_max"] + 1):
            for k in range(k0, min(k0 + self.p["k_look"], last) + 1):
                t_b = d.t0 + k + delay                # arrive at waypoint k, delayed
                w = centre(d.path[k])
                need = float(np.linalg.norm(w - d.pos))
                if t_b - self.t < DT or need / (t_b - self.t) > self.p["v_max"]:
                    tried.append((k, delay, "too fast"))
                    continue
                if self.segment_free(d.pos, self.t, w, t_b, pred, d):
                    tried.append((k, delay, "ok"))
                    return k, delay, "ok", tried
                tried.append((k, delay, "segment blocked"))
        return None, None, (tried[-1][2] if tried else "no waypoint ahead"), tried

    # -- replanning and the conflict re-check ------------------------------
    def reservation_of_others(self, d: Drone, pred, t_start: int) -> Reservation:
        res = Reservation()
        for o in self.others(d):
            res.add_path(o.path, o.t0)
        if pred is not None:                       # predicted intruder cells
            means, covs = pred
            for j in range(0, len(means), int(round(1.0 / DT))):
                t = self.t + j * DT
                layer = int(round(t))
                if layer < t_start:
                    continue
                r = self.R_safe + self.p["kappa"] * sigma_max(covs[j]) + 0.5
                cx, cy = means[j]
                for x in range(int(cx - r) - 1, int(cx + r) + 2):
                    for y in range(int(cy - r) - 1, int(cy + r) + 2):
                        if np.linalg.norm(np.array([x + 0.5, y + 0.5]) - means[j]) < r:
                            res.block((x, y), layer)
        return res

    def replan(self, d: Drone, pred) -> bool:
        """Space-time A* from the current cell at the next grid time with the
        teammates reserved and the predicted intruder cells blocked."""
        t_start = int(math.ceil(self.t + 0.5))
        c0 = nearest_cell(d.pos)
        if not self.grid.free(c0):
            c0 = min(self.grid.neighbours(c0) or [c0],
                     key=lambda c: np.linalg.norm(centre(c) - d.pos))
        res = self.reservation_of_others(d, pred, t_start)
        for o in self.others(d):                   # keep clear of where they are now
            res.block(nearest_cell(o.pos), t_start)
        path = space_time_astar(self.grid, c0, d.goal, t_start, Constraints(), res)
        if path is None:
            return False
        d.path, d.t0 = [c0] + path, t_start - 1
        d.target, d.target_time, d.target_index = centre(c0), float(t_start), 0
        d.replans += 1
        self.last_replan = dict(t=self.t, drone=d.name, t_start=t_start, c0=c0,
                                path=list(d.path), blocked=sum(len(v) for v in res.layers.values()),
                                layers={t: sorted(c) for t, c in res.layers.items()})
        self.replan_log.append(self.last_replan)
        return True

    def recheck(self, changed: Drone) -> dict:
        """Conflict re-check: detect conflicts between the changed plan and
        the current plans of the other drones; if one appears, repair the
        affected subset with a local CBS from their next grid cells."""
        t_from = int(math.floor(self.t))
        paths = [o.path for o in self.drones]
        starts = [o.t0 for o in self.drones]
        conflict = first_conflict(paths, starts, self.names, t_from)
        entry = dict(t=self.t, drone=changed.name, conflict=str(conflict) if conflict else None,
                     repaired=None, before=[(o.name, list(o.path), o.t0) for o in self.drones])
        if conflict is not None:
            subset = [o for o in self.drones if o.name in (conflict.i, conflict.j)]
            t_start = int(math.ceil(self.t + 0.5))
            entry["subset"], entry["t_start"] = [o.name for o in subset], t_start
            res = Reservation()
            for o in self.drones:
                if o not in subset:
                    res.add_path(o.path, o.t0)
            cells = [cell_at(o.path, o.t0, t_start) for o in subset]
            new_paths, _ = cbs(self.grid, cells, [o.goal for o in subset], t_start, res)
            entry["repaired"] = new_paths is not None
            if new_paths is not None:
                for o, p in zip(subset, new_paths):
                    o.path, o.t0 = p, t_start
                    o.target, o.target_time, o.target_index = centre(p[0]), float(t_start), 0
                    if o.state == NOMINAL:
                        self.transition(o, RECONNECTING, "repaired by local CBS")
        entry["after"] = [(o.name, list(o.path), o.t0) for o in self.drones]
        self.recheck_log.append(entry)
        return entry

    # -- the state machine ---------------------------------------------------
    def transition(self, d: Drone, new: str, reason: str) -> None:
        self.log.append((round(self.t, 2), d.name, d.state, new, reason))
        if new == AVOIDING and self.pred is not None:   # keep the trigger's evidence
            times, sep, infl, own = self.conflict_profile(d, self.pred)
            self.trigger_profiles.append(dict(t=self.t, drone=d.name, times=times, sep=sep,
                                              infl=infl, own=own, means=self.pred[0][:len(times)]))
        d.state, d.t_state, d.clear_count = new, self.t, 0
        if new == NOMINAL:
            d.target = None

    def decide(self, d: Drone, pred) -> np.ndarray:
        """One pass of the per-drone control loop; returns the velocity."""
        p = self.p
        inside, t_c, _ = self.predicted_conflict(d, pred)
        if d.state == NOMINAL and inside:
            self.transition(d, AVOIDING, "predicted conflict at t_c=%.1f s" % t_c)
        if d.state == AVOIDING:
            drift = float(np.linalg.norm(d.pos - d.plan_position(self.t)))
            too_long = self.t - d.t_state > p["t_avoid_max"]
            d.clear_count = 0 if inside else d.clear_count + 1
            if drift > p["drift_max"] or too_long:
                self.transition(d, REPLANNING, "drift %.2f m or time" % drift)
            elif d.clear_count >= p["n_clear"]:
                self.transition(d, RECONNECTING, "conflict cleared")
                reason = self.try_reconnect(d, pred)
                if reason != "ok":
                    self.transition(d, REPLANNING, "reconnection failed: " + reason)
            else:
                v_pref = self.preferred_velocity(d, with_formation=False)
                return self.local_layer(d, v_pref, pred, t_c, with_intruder=True)[0]
        if d.state == REPLANNING:
            due = self.t - d.t_last_replan >= p["replan_period"]
            if due and self.replan(d, pred):
                d.t_last_replan = self.t
                self.recheck(d)
                self.transition(d, RECONNECTING, "new path from the current cell")
                inside, t_c, _ = self.predicted_conflict(d, pred)
            else:                                  # no path yet: hover, retry
                return self.local_layer(d, np.zeros(2), pred, t_c, True)[0]
        if d.state == RECONNECTING:
            if inside:
                self.transition(d, AVOIDING, "conflict again, t_c=%.1f s" % t_c)
                v_pref = self.preferred_velocity(d, with_formation=False)
                return self.local_layer(d, v_pref, pred, t_c, with_intruder=True)[0]
            if self.t >= d.target_time - DT / 2:
                self.transition(d, NOMINAL, "back on the plan at waypoint %d" % d.target_index)
        v_pref = self.preferred_velocity(d, with_formation=True)
        return self.local_layer(d, v_pref, pred, t_c, with_intruder=False)[0]

    def try_reconnect(self, d: Drone, pred) -> str:
        """Run the reconnection search and install its result: the target
        waypoint and, for a delayed reconnection, the shifted plan and the
        conflict re-check.  Returns "ok" or the reason of the failure."""
        k, delay, reason, tried = self.reconnect(d, pred)
        self.reconnect_log.append(dict(t=self.t, drone=d.name, k=k, delay=delay,
                                       reason=reason, pos=d.pos.copy(), tried=tried))
        if k is None:
            return reason
        d.target, d.target_index = centre(d.path[k]), k
        d.target_time = float(d.t0 + k + delay)
        d.reconnections += 1
        if delay > 0:                              # shift the remainder of the plan
            d.path, d.t0 = d.path[k:], d.t0 + k + delay
            d.target_index = 0
            self.recheck(d)
        return "ok"

    # -- one control cycle -----------------------------------------------------
    def step(self) -> None:
        """One control cycle: prediction layer at its own rate, then one
        decision per drone from a common snapshot, then the motion."""
        p_true = self.intruder_true()
        if self.clock.due("prediction", self.t):
            if self.detected_at is None and any(
                    np.linalg.norm(p_true - d.pos) <= self.p["sense_range"] for d in self.drones):
                self.detected_at = self.t
            if self.detected_at is not None:          # observe, filter, predict
                z = p_true + self.rng.normal(0.0, self.p["sigma_z"], 2)
                self.tracker.update(z)
            self.pred = self.prediction()
        pred = self.pred
        profiles = {d.name: (self.conflict_profile(d, pred) if pred is not None else None)
                    for d in self.drones}
        # decisions from one snapshot of the teammates' states
        commands = [self.decide(d, pred) for d in self.drones]
        for d, v in zip(self.drones, commands):
            d.vel = v
        # record
        snap = dict(t=self.t, pos=[d.pos.copy() for d in self.drones],
                    state=[d.state for d in self.drones], intruder=p_true.copy(),
                    est=(self.tracker.position if self.tracker.x is not None else None),
                    est_v=(self.tracker.velocity if self.tracker.x is not None else None),
                    est_P=(self.tracker.P.copy() if self.tracker.x is not None else None),
                    pred=pred, e_form=self.formation_error(), connected=self.connected(),
                    sep=[float(np.linalg.norm(d.pos - p_true)) for d in self.drones],
                    drift=[float(np.linalg.norm(d.pos - d.plan_position(self.t))) for d in self.drones],
                    profiles=profiles, paths=[(list(d.path), d.t0) for d in self.drones])
        self.history.append(snap)
        for d in self.drones:
            self.d_min_intruder = min(self.d_min_intruder, float(np.linalg.norm(d.pos - p_true)))
            for o in self.others(d):
                self.d_min_mates = min(self.d_min_mates, float(np.linalg.norm(d.pos - o.pos)))
        # integrate
        for d in self.drones:
            d.pos = d.pos + d.vel * DT
        self.t = round(self.t + DT, 6)

    def formation_error(self) -> float:
        errs = []
        for (a, b), off in self.formation.items():
            pa = next(o for o in self.drones if o.name == a).pos
            pb = next(o for o in self.drones if o.name == b).pos
            errs.append(np.linalg.norm((pb - pa) - off) ** 2)
        return math.sqrt(sum(errs) / len(errs)) if errs else 0.0

    def connected(self) -> bool:
        n = len(self.drones)
        seen, stack = {0}, [0]
        while stack:
            i = stack.pop()
            for j in range(n):
                if j not in seen and np.linalg.norm(self.drones[i].pos - self.drones[j].pos) <= self.p["r_comm"]:
                    seen.add(j)
                    stack.append(j)
        return len(seen) == n

    def run(self, t_end: float = 30.0) -> None:
        while self.t < t_end and not all(d.arrived(self.t) for d in self.drones):
            self.step()


# ---------------------------------------------------------------------
# 7. Rates: which module runs in which control cycle
# ---------------------------------------------------------------------
#
#   module (layer)      interface                        rate
#   global planner (1)  cbs(grid, starts, goals)         once, before take-off
#   tracker (2)         update(z); predict_horizon(n)    period_prediction
#   local layer (3)     local_layer(d, v_pref, pred)     every cycle DT
#   replanner (4)       replan(d, pred); recheck(d)      on demand, >= replan_period
#   executive           decide(d, pred) -> velocity      every cycle DT


class RateSchedule:
    """A module with period T runs in the first cycle at or after its due
    time; the executive asks ``due(name, t)`` once per cycle."""

    def __init__(self, periods: Dict[str, float]):
        self.periods = dict(periods)
        self.next_due = {name: 0.0 for name in periods}

    def due(self, name: str, t: float) -> bool:
        if t + EPS < self.next_due[name]:
            return False
        self.next_due[name] = t + self.periods[name]
        return True


# ---------------------------------------------------------------------
# 8. A second example: two drones replan in the same cycle
# ---------------------------------------------------------------------


def simultaneous_replan_example():
    """Two drones that replan in the same cycle, each against the other's
    old reservation, and the re-check that repairs the result with a local
    CBS (partial replanning).  Returns a dict with the numbers."""
    grid = Grid(7, 5)
    old = {"A": ([(0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2)], 0),
           "B": ([(3, 4), (3, 3), (3, 2), (3, 1), (3, 0)], 0)}
    # both were pushed off their plans; both replan at t_start = 3 from new cells
    res_for_a = Reservation()
    res_for_a.add_path(*old["B"])
    res_for_b = Reservation()
    res_for_b.add_path(*old["A"])
    new_a = space_time_astar(grid, (1, 3), (6, 2), 3, Constraints(), res_for_a)
    new_b = space_time_astar(grid, (2, 4), (3, 0), 3, Constraints(), res_for_b)
    conflict = first_conflict([new_a, new_b], [3, 3], ["A", "B"], 3)
    repaired, expanded = cbs(grid, [(1, 3), (2, 4)], [(6, 2), (3, 0)], 3)
    return dict(new_a=new_a, new_b=new_b, conflict=conflict, repaired=repaired,
                expanded=expanded,
                after=first_conflict(repaired, [3, 3], ["A", "B"], 3) if repaired else None)


# ---------------------------------------------------------------------
# 9. Worked example and self-test
# ---------------------------------------------------------------------


def worked_example(verbose: bool = True) -> HybridSimulation:
    sim = HybridSimulation()
    sim.run()
    if verbose:
        print("Nominal plan (CBS, %d CT nodes expanded):" % sim.cbs_expansions)
        for n, p in zip(sim.names, sim.nominal):
            print("  %s: cost %2d  %s" % (n, len(p) - 1, p))
        soc = sum(len(p) - 1 for p in sim.nominal)
        print("  sum of costs %d, makespan %d" % (soc, max(len(p) - 1 for p in sim.nominal)))
        print("Intruder detected at t = %.1f s" % sim.detected_at)
        print("Transitions:")
        for t, n, a, b, r in sim.log:
            print("  t=%5.1f  %s: %-12s -> %-12s (%s)" % (t, n, a, b, r))
        print("Reconnection attempts:")
        for e in sim.reconnect_log:
            print("  t=%5.1f  %s at (%.2f, %.2f): k=%s delay=%s (%s)" % (e["t"], e["drone"], e["pos"][0], e["pos"][1], e["k"], e["delay"], e["reason"]))
        print("Re-checks:")
        for e in sim.recheck_log:
            print("  t=%5.1f  %s: conflict=%s repaired=%s" % (e["t"], e["drone"], e["conflict"], e["repaired"]))
        for lr in sim.replan_log:
            print("Replan of %s at t=%.1f from %s at t_start=%d, %d blocked cells:\n  %s"
                  % (lr["drone"], lr["t"], lr["c0"], lr["t_start"], lr["blocked"], lr["path"]))
        print("Minimum separation: intruder %.2f m, teammates %.2f m (R_safe = %.2f, R_mate = %.2f)"
              % (sim.d_min_intruder, sim.d_min_mates, sim.R_safe, sim.R_mate))
        print("Formation error: max %.2f m, final %.2f m; communication connected always: %s"
              % (max(h["e_form"] for h in sim.history), sim.history[-1]["e_form"],
                 all(h["connected"] for h in sim.history)))
        print("Arrival times: %s" % ", ".join("%s %.1f" % (d.name, d.t0 + len(d.path) - 1) for d in sim.drones))
        print("Replans %s, reconnections %s, ORCA infeasible cycles %d, end t=%.1f"
              % ([d.replans for d in sim.drones], [d.reconnections for d in sim.drones],
                 sim.orca_infeasible, sim.t))
        ex = simultaneous_replan_example()
        print("Simultaneous replans: A %s\n                      B %s\n  conflict %s, local CBS (%d nodes) -> %s, conflict after: %s"
              % (ex["new_a"], ex["new_b"], ex["conflict"], ex["expanded"], ex["repaired"], ex["after"]))
    return sim


def _self_test() -> None:
    sim = worked_example(verbose=False)
    # 1. the nominal plan is conflict-free and reaches the goals
    assert first_conflict(sim.nominal, [0] * 3) is None
    assert all(p[-1] == d.goal for p, d in zip(sim.nominal, sim.drones))
    # 2. the intruder is detected and triggers Avoiding
    assert sim.detected_at is not None
    assert any(b == AVOIDING for (_, _, _, b, _) in sim.log)
    # 3. the minimum separation stays above the safety radius
    assert sim.d_min_intruder >= sim.p["r_drone"] + sim.p["r_intruder"], sim.d_min_intruder
    assert sim.d_min_mates >= 2 * sim.p["r_drone"], sim.d_min_mates
    # 4. after the intruder has passed, every drone is back on a plan that is
    #    conflict-free against the others and reaches the goal
    assert all(d.state == NOMINAL for d in sim.drones)
    assert first_conflict([d.path for d in sim.drones], [d.t0 for d in sim.drones],
                          t_from=int(math.floor(sim.t))) is None
    assert all(d.arrived(sim.t) for d in sim.drones), [d.pos for d in sim.drones]
    assert sim.t < 25.0, sim.t
    # 4b. the re-check inside the scenario found and repaired a conflict
    assert any(e["repaired"] for e in sim.recheck_log)
    # 4c. one reconnection succeeded and one failed before a replan
    assert any(e["k"] is not None for e in sim.reconnect_log)
    assert any(e["k"] is None for e in sim.reconnect_log)
    # 5. the re-check repairs a pair of simultaneous replans
    ex = simultaneous_replan_example()
    assert ex["conflict"] is not None and ex["repaired"] is not None and ex["after"] is None
    # 6. the Kalman prediction inflation grows with the horizon
    means, covs = sim.tracker.predict_horizon(30)
    assert sigma_max(covs[-1]) > sigma_max(covs[0])
    # 7. the rate schedule runs a 0.3 s module in every third 0.1 s cycle
    clock = RateSchedule({"slow": 0.3})
    assert sum(clock.due("slow", round(i * DT, 6)) for i in range(30)) == 10
    print("ch24_hybrid.py: all self-tests passed (%d cycles simulated)" % len(sim.history))


if __name__ == "__main__":
    import time
    start = time.perf_counter()
    worked_example(verbose=True)
    _self_test()
    print("elapsed %.1f s" % (time.perf_counter() - start))
