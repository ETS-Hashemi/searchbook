"""Mixed-integer linear programming for multi-vehicle trajectory planning.

Chapter 22 of "Multi-Agent Path Planning and Drone Collision Avoidance".

The module builds, as sparse matrices, the MILP of Schouwenaars et al.
(2001) and Richards and How (2002): m planar double-integrator vehicles
fly from their starts to their goals within N steps of length dt, stay
outside axis-aligned rectangular obstacles and keep an infinity-norm
distance of at least d_min from each other at every sampled instant.
Obstacle avoidance and separation are "either-or" constraints written
with the big-M trick and binary variables.  Three objectives exist:

    fuel  minimize dt * sum_k ||u_k||_1   (one slack per input component)
    peak  minimize max_k ||u_k||_inf      (one slack per vehicle)
    time  minimize the arrival time       (arrival binaries, Richards & How)

The model is solved with scipy.optimize.milp (the HiGHS branch-and-cut
solver).  A small textbook branch-and-bound, whose LP relaxations are
solved by HiGHS, shows what the solver does and produces the trace of the
chapter's example; a brute-force enumeration certifies the optimum of a
tiny instance in the self-test.

Run:  python3 code/ch22_milp.py     (self-test, a few seconds)
"""
from __future__ import annotations

import heapq
import itertools
import time
from dataclasses import dataclass

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import coo_matrix


# ---------------------------------------------------------------------
# Problem data
# ---------------------------------------------------------------------
@dataclass
class Vehicle:
    """Start and goal position of one vehicle; it starts and ends at rest."""
    start: tuple
    goal: tuple


@dataclass
class Instance:
    """A multi-vehicle trajectory problem.

    obstacles: (xmin, xmax, ymin, ymax) rectangles, already inflated by the
        vehicle radius and the corner-cutting margin.
    workspace: the same tuple for the flight area; it bounds every position
        and yields the tight big-M values.
    """
    vehicles: list
    obstacles: list
    horizon: int
    dt: float
    a_max: float
    v_max: float
    d_min: float
    workspace: tuple
    objective: str = "fuel"      # "fuel", "peak" or "time"


def double_integrator(dt):
    """Discrete double integrator: x = (px, py, vx, vy), u = (ax, ay)."""
    A = np.eye(4)
    A[0, 2] = A[1, 3] = dt
    B = np.zeros((4, 2))
    B[0, 0] = B[1, 1] = 0.5 * dt * dt
    B[2, 0] = B[3, 1] = dt
    return A, B


# ---------------------------------------------------------------------
# The MILP
# ---------------------------------------------------------------------
class MilpModel:
    """Variables, bounds, objective and constraint rows of the MILP.

    The constraint rows are collected as (row, col, value) triples with a
    lower and an upper bound per row (lb = ub for an equality) and turned
    into one sparse matrix in solve().
    """

    def __init__(self, inst, big_m=None):
        self.inst = inst
        self.big_m = big_m            # None: tight, per-constraint values
        m, N = len(inst.vehicles), inst.horizon
        self.n_var = 0
        self.x_off = [self._alloc(4 * (N + 1)) for _ in range(m)]
        self.u_off = [self._alloc(2 * N) for _ in range(m)]
        n_slack = 1 if inst.objective == "peak" else 2 * N
        self.s_off = [self._alloc(n_slack) for _ in range(m)]
        self.b_off = {(i, o): self._alloc(4 * N)
                      for i in range(m) for o in range(len(inst.obstacles))}
        self.pairs = list(itertools.combinations(range(m), 2))
        self.c_off = {p: self._alloc(4 * N) for p in self.pairs}
        self.w_off = ([self._alloc(N) for _ in range(m)]
                      if inst.objective == "time" else [])
        self.rows, self.cols, self.vals = [], [], []
        self.row_lb, self.row_ub = [], []
        self.lb = np.full(self.n_var, -np.inf)
        self.ub = np.full(self.n_var, np.inf)
        self.integrality = np.zeros(self.n_var)
        self.c = np.zeros(self.n_var)
        self._bounds_and_objective()
        self._dynamics_rows()
        self._slack_rows()
        self._obstacle_rows()
        self._separation_rows()
        if inst.objective == "time":
            self._arrival_rows()
        self.n_cons = len(self.row_lb)
        self.n_bin = int(self.integrality.sum())

    # -- variable indices ------------------------------------------------
    def _alloc(self, n):
        first = self.n_var
        self.n_var += n
        return first

    def x(self, i, k, d):
        """State component d (0 px, 1 py, 2 vx, 3 vy) of vehicle i, step k."""
        return self.x_off[i] + 4 * k + d

    def u(self, i, k, d):
        return self.u_off[i] + 2 * k + d

    def s(self, i, k, d):
        if self.inst.objective == "peak":
            return self.s_off[i]
        return self.s_off[i] + 2 * k + d

    def b(self, i, o, k, j):
        """Obstacle binary j (0..3) of vehicle i, obstacle o, step k = 1..N."""
        return self.b_off[(i, o)] + 4 * (k - 1) + j

    def cpair(self, pair, k, j):
        """Separation binary j (0..3) of the pair at step k = 1..N."""
        return self.c_off[pair] + 4 * (k - 1) + j

    def w(self, i, k):
        """Arrival binary of vehicle i for step k = 1..N (objective time)."""
        return self.w_off[i] + (k - 1)

    # -- rows --------------------------------------------------------------
    def add_row(self, coeffs, lb, ub):
        """Append the row lb <= sum_j coeffs[j] * x_j <= ub."""
        r = len(self.row_lb)
        for j, v in coeffs.items():
            self.rows.append(r)
            self.cols.append(j)
            self.vals.append(float(v))
        self.row_lb.append(lb)
        self.row_ub.append(ub)

    def _bounds_and_objective(self):
        inst = self.inst
        m, N, ws = len(inst.vehicles), inst.horizon, inst.workspace
        for i in range(m):
            for k in range(N + 1):
                self.lb[self.x(i, k, 0)], self.ub[self.x(i, k, 0)] = ws[0], ws[1]
                self.lb[self.x(i, k, 1)], self.ub[self.x(i, k, 1)] = ws[2], ws[3]
                for d in (2, 3):
                    self.lb[self.x(i, k, d)] = -inst.v_max
                    self.ub[self.x(i, k, d)] = inst.v_max
            for k in range(N):
                for d in (0, 1):
                    self.lb[self.u(i, k, d)] = -inst.a_max
                    self.ub[self.u(i, k, d)] = inst.a_max
                    self.lb[self.s(i, k, d)] = 0.0
                    if inst.objective == "fuel":
                        self.c[self.s(i, k, d)] = inst.dt
                    elif inst.objective == "time":
                        self.c[self.s(i, k, d)] = 1e-3 * inst.dt   # tie-break
            if inst.objective == "peak":
                self.c[self.s(i, 0, 0)] = 1.0
            if inst.objective == "time":
                for k in range(1, N + 1):
                    self.c[self.w(i, k)] = k * inst.dt
        first_bin = min([self.b_off[key] for key in self.b_off]
                        + [self.c_off[p] for p in self.pairs]
                        + self.w_off + [self.n_var])
        self.lb[first_bin:] = 0.0
        self.ub[first_bin:] = 1.0
        self.integrality[first_bin:] = 1

    def _dynamics_rows(self):
        inst = self.inst
        A, B = double_integrator(inst.dt)
        for i, veh in enumerate(inst.vehicles):
            start = (veh.start[0], veh.start[1], 0.0, 0.0)
            goal = (veh.goal[0], veh.goal[1], 0.0, 0.0)
            for d in range(4):                       # initial state
                self.add_row({self.x(i, 0, d): 1.0}, start[d], start[d])
            for k in range(inst.horizon):            # x_{k+1} = A x_k + B u_k
                for r in range(4):
                    coeffs = {self.x(i, k + 1, r): 1.0}
                    for cc in range(4):
                        if A[r, cc] != 0.0:
                            coeffs[self.x(i, k, cc)] = -A[r, cc]
                    for cc in range(2):
                        if B[r, cc] != 0.0:
                            coeffs[self.u(i, k, cc)] = -B[r, cc]
                    self.add_row(coeffs, 0.0, 0.0)
            for d in range(4):                       # terminal state
                self.add_row({self.x(i, inst.horizon, d): 1.0}, goal[d], goal[d])

    def _slack_rows(self):
        """u <= s and -u <= s, so that s >= |u| (1-norm or inf-norm)."""
        inst = self.inst
        for i in range(len(inst.vehicles)):
            for k in range(inst.horizon):
                for d in (0, 1):
                    u, s = self.u(i, k, d), self.s(i, k, d)
                    self.add_row({u: 1.0, s: -1.0}, -np.inf, 0.0)
                    self.add_row({u: -1.0, s: -1.0}, -np.inf, 0.0)

    def _obstacle_rows(self):
        """Big-M disjunction: at every step at least one side constraint holds."""
        inst = self.inst
        ws = inst.workspace
        for o, (xmin, xmax, ymin, ymax) in enumerate(inst.obstacles):
            # tight M: the largest violation possible inside the workspace
            tight = (ws[1] - xmin, xmax - ws[0], ws[3] - ymin, ymax - ws[2])
            M = [self.big_m] * 4 if self.big_m is not None else list(tight)
            for i in range(len(inst.vehicles)):
                for k in range(1, inst.horizon + 1):
                    px, py = self.x(i, k, 0), self.x(i, k, 1)
                    b = [self.b(i, o, k, j) for j in range(4)]
                    self.add_row({px: 1.0, b[0]: -M[0]}, -np.inf, xmin)   # left
                    self.add_row({px: -1.0, b[1]: -M[1]}, -np.inf, -xmax)  # right
                    self.add_row({py: 1.0, b[2]: -M[2]}, -np.inf, ymin)   # below
                    self.add_row({py: -1.0, b[3]: -M[3]}, -np.inf, -ymax)  # above
                    self.add_row({bj: 1.0 for bj in b}, -np.inf, 3.0)

    def _separation_rows(self):
        """||p_i - p_j||_inf >= d_min via four binaries per pair and step."""
        inst = self.inst
        ws = inst.workspace
        Mx = inst.d_min + (ws[1] - ws[0])
        My = inst.d_min + (ws[3] - ws[2])
        if self.big_m is not None:
            Mx = My = self.big_m
        for pair in self.pairs:
            i, j = pair
            for k in range(1, inst.horizon + 1):
                c = [self.cpair(pair, k, q) for q in range(4)]
                for d, M, cs in ((0, Mx, c[:2]), (1, My, c[2:])):
                    pi, pj = self.x(i, k, d), self.x(j, k, d)
                    # p_i - p_j >= d_min - M c   or   p_j - p_i >= d_min - M c
                    self.add_row({pi: 1.0, pj: -1.0, cs[0]: M}, inst.d_min, np.inf)
                    self.add_row({pj: 1.0, pi: -1.0, cs[1]: M}, inst.d_min, np.inf)
                self.add_row({cq: 1.0 for cq in c}, -np.inf, 3.0)

    def _arrival_rows(self):
        """Minimum time: w_{i,k} = 1 marks the arrival step; then p stays at g."""
        inst = self.inst
        ws = inst.workspace
        Mg = max(ws[1] - ws[0], ws[3] - ws[2])
        for i, veh in enumerate(inst.vehicles):
            ws = {self.w(i, k): 1.0 for k in range(1, inst.horizon + 1)}
            self.add_row(ws, 1.0, 1.0)
            for k in range(1, inst.horizon + 1):
                arrived = {self.w(i, q): Mg for q in range(1, k + 1)}
                for d in (0, 1):
                    p = self.x(i, k, d)
                    row = dict(arrived)
                    row[p] = 1.0                 # p - g <= Mg (1 - sum y)
                    self.add_row(row, -np.inf, veh.goal[d] + Mg)
                    row = dict(arrived)
                    row[p] = -1.0                # g - p <= Mg (1 - sum y)
                    self.add_row(row, -np.inf, -veh.goal[d] + Mg)

    def groups(self):
        """The either-or groups: four binaries whose sum is at most 3."""
        inst = self.inst
        groups = [[self.b(i, o, k, j) for j in range(4)]
                  for (i, o) in self.b_off for k in range(1, inst.horizon + 1)]
        groups += [[self.cpair(p, k, j) for j in range(4)]
                   for p in self.pairs for k in range(1, inst.horizon + 1)]
        return groups

    # -- solving -----------------------------------------------------------
    def matrix(self):
        return coo_matrix((self.vals, (self.rows, self.cols)),
                          shape=(self.n_cons, self.n_var)).tocsr()

    def solve(self, time_limit=None, lb=None, ub=None, relax=False):
        """Solve with scipy.optimize.milp (HiGHS); relax=True drops integrality."""
        options = {"disp": False}
        if time_limit is not None:
            options["time_limit"] = time_limit
        constraints = LinearConstraint(self.matrix(), self.row_lb, self.row_ub)
        bounds = Bounds(self.lb if lb is None else lb,
                        self.ub if ub is None else ub)
        integrality = None if relax else self.integrality
        t0 = time.perf_counter()
        res = milp(self.c, integrality=integrality, bounds=bounds,
                   constraints=constraints, options=options)
        return self._unpack(res, time.perf_counter() - t0)

    def _unpack(self, res, elapsed):
        inst = self.inst
        m, N = len(inst.vehicles), inst.horizon
        sol = Solution(status=int(res.status), message=str(res.message),
                       objective=np.inf, positions=None, velocities=None,
                       inputs=None, x=None, solve_time=elapsed,
                       n_var=self.n_var, n_cons=self.n_cons, n_bin=self.n_bin,
                       nodes=int(getattr(res, "mip_node_count", 0) or 0),
                       gap=float(getattr(res, "mip_gap", 0.0) or 0.0))
        if res.x is None:
            return sol
        x = np.asarray(res.x)
        sol.x, sol.objective = x, float(res.fun)
        sol.positions = np.array([[[x[self.x(i, k, 0)], x[self.x(i, k, 1)]]
                                   for k in range(N + 1)] for i in range(m)])
        sol.velocities = np.array([[[x[self.x(i, k, 2)], x[self.x(i, k, 3)]]
                                    for k in range(N + 1)] for i in range(m)])
        sol.inputs = np.array([[[x[self.u(i, k, 0)], x[self.u(i, k, 1)]]
                                for k in range(N)] for i in range(m)])
        return sol


@dataclass
class Solution:
    status: int            # 0 optimal, 1 time limit (incumbent), 2 infeasible
    message: str
    objective: float
    positions: np.ndarray  # (m, N+1, 2)
    velocities: np.ndarray
    inputs: np.ndarray     # (m, N, 2)
    x: np.ndarray
    solve_time: float
    n_var: int
    n_cons: int
    n_bin: int
    nodes: int
    gap: float


# ---------------------------------------------------------------------
# Checking a solution
# ---------------------------------------------------------------------
def check_solution(inst, sol):
    """Largest violation of each constraint family at the sampled instants."""
    A, B = double_integrator(inst.dt)
    P, V, U = sol.positions, sol.velocities, sol.inputs
    m, N = len(inst.vehicles), inst.horizon
    dyn = obs = sep = bnd = term = 0.0
    for i in range(m):
        state = np.hstack([P[i], V[i]])
        for k in range(N):
            pred = A @ state[k] + B @ U[i, k]
            dyn = max(dyn, np.abs(pred - state[k + 1]).max())
        term = max(term, np.abs(P[i, N] - inst.vehicles[i].goal).max(),
                   np.abs(V[i, N]).max(), np.abs(P[i, 0] - inst.vehicles[i].start).max())
        bnd = max(bnd, np.abs(U[i]).max() - inst.a_max, np.abs(V[i]).max() - inst.v_max)
        for (xmin, xmax, ymin, ymax) in inst.obstacles:
            for k in range(1, N + 1):
                px, py = P[i, k]
                depth = min(px - xmin, xmax - px, py - ymin, ymax - py)
                obs = max(obs, depth)          # > 0 means inside
    for i, j in itertools.combinations(range(m), 2):
        for k in range(1, N + 1):
            gap = np.abs(P[i, k] - P[j, k]).max()
            sep = max(sep, inst.d_min - gap)
    return {"dynamics": dyn, "obstacle": obs, "separation": sep,
            "bounds": bnd, "terminal": term}


def continuous_check(inst, sol, substeps=20):
    """Worst obstacle penetration and smallest separation BETWEEN samples.

    The exact zero-order-hold motion p(t) = p_k + v_k s + a_k s^2 / 2 for
    0 <= s <= dt is evaluated at substeps points per step.  The MILP only
    constrains the sampled instants, so these values can be worse than
    the sampled ones (corner cutting).  The result also names the vehicle
    (or pair) and the time at which each worst case occurs.
    """
    P, V, U = sol.positions, sol.velocities, sol.inputs
    m, N = len(inst.vehicles), inst.horizon
    ss = np.linspace(0.0, inst.dt, substeps + 1)
    fine = np.zeros((m, N * substeps + 1, 2))
    for i in range(m):
        for k in range(N):
            seg = P[i, k] + np.outer(ss, V[i, k]) + 0.5 * np.outer(ss ** 2, U[i, k])
            fine[i, k * substeps:(k + 1) * substeps + 1] = seg
    times = np.arange(N * substeps + 1) * inst.dt / substeps
    obs, obs_at = 0.0, None
    for (xmin, xmax, ymin, ymax) in inst.obstacles:
        for i in range(m):
            depth = np.min(np.stack([fine[i, :, 0] - xmin, xmax - fine[i, :, 0],
                                     fine[i, :, 1] - ymin, ymax - fine[i, :, 1]]), axis=0)
            q = int(np.argmax(depth))
            if depth[q] > obs:
                obs, obs_at = float(depth[q]), (i, float(times[q]))
    sep, sep_at = np.inf, None
    for i, j in itertools.combinations(range(m), 2):
        d = np.abs(fine[i] - fine[j]).max(axis=1)
        q = int(np.argmin(d))
        if d[q] < sep:
            sep, sep_at = float(d[q]), (i, j, float(times[q]))
    return {"obstacle_penetration": obs, "min_separation": sep,
            "penetration_at": obs_at, "separation_at": sep_at}


def is_valid(inst, sol, tol=1e-6):
    return sol.positions is not None and all(v <= tol for v in check_solution(inst, sol).values())


# ---------------------------------------------------------------------
# Textbook branch-and-bound on top of LP relaxations
# ---------------------------------------------------------------------
def branch_and_bound(model, max_nodes=500, tol=1e-6):
    """Best-bound-first branch-and-bound; returns (value, x, trace).

    Every trace entry is a dict with the node id, its parent, the branching
    decision that created it, the LP relaxation value and the action taken.
    Before the branching variable is chosen, the harmless binaries are
    rounded up: in an either-or group whose sum is at most 3, a binary that
    is already 0 certifies the disjunction, so the other three may be set
    to 1 without changing feasibility or cost (they have zero cost).
    """
    groups = model.groups()
    bin_idx = np.flatnonzero(model.integrality)
    best_val, best_x, trace = np.inf, None, []
    counter = itertools.count()
    heap = [(-np.inf, next(counter), 0, model.lb.copy(), model.ub.copy(), "root")]
    node_id = 0
    while heap and node_id < max_nodes:
        bound, _, parent, lb, ub, decision = heapq.heappop(heap)
        node_id += 1
        entry = {"node": node_id, "parent": parent, "decision": decision}
        if bound >= best_val - tol:
            entry.update(lp=bound, action="pruned by bound (parent bound)")
            trace.append(entry)
            continue
        sol = model.solve(lb=lb, ub=ub, relax=True)
        if sol.x is None:
            entry.update(lp=np.inf, action="infeasible")
            trace.append(entry)
            continue
        x = sol.x.copy()
        for g in groups:                       # round up the harmless binaries
            if x[g].min() <= tol:
                x[g] = np.where(x[g] > tol, 1.0, 0.0)
        frac = np.abs(x[bin_idx] - np.round(x[bin_idx]))
        entry["lp"] = sol.objective
        if sol.objective >= best_val - tol:
            entry["action"] = "pruned by bound"
        elif frac.max() <= tol:
            best_val, best_x = sol.objective, x
            entry["action"] = "integral: new incumbent"
        else:
            j = bin_idx[int(np.argmax(-np.abs(frac - 0.5)))]   # most fractional
            entry["action"] = "branch on x[%d] = %.3f" % (j, sol.x[j])
            entry["branch_var"] = int(j)
            for side, name in ((0.0, "= 0"), (1.0, "= 1")):
                nlb, nub = lb.copy(), ub.copy()
                nlb[j] = nub[j] = side
                heapq.heappush(heap, (sol.objective, next(counter), node_id,
                                      nlb, nub, "x[%d] %s" % (j, name)))
        trace.append(entry)
    return best_val, best_x, trace


def brute_force(model):
    """Optimum by enumerating, for every either-or group, which side holds."""
    groups = model.groups()
    assert 4 ** len(groups) <= 5000, "instance too large for brute force"
    best = np.inf
    for choice in itertools.product(range(4), repeat=len(groups)):
        lb, ub = model.lb.copy(), model.ub.copy()
        for g, j in zip(groups, choice):
            for q, var in enumerate(g):
                lb[var] = ub[var] = 0.0 if q == j else 1.0
        sol = model.solve(lb=lb, ub=ub, relax=True)
        if sol.x is not None:
            best = min(best, sol.objective)
    return best, 4 ** len(groups)


# ---------------------------------------------------------------------
# Instances used in the chapter
# ---------------------------------------------------------------------
def tiny_instance(objective="fuel"):
    """One vehicle, one obstacle on the straight line, four steps."""
    return Instance(vehicles=[Vehicle((0.0, 0.0), (4.0, 0.0))],
                    obstacles=[(1.5, 2.5, -0.5, 0.5)], horizon=4, dt=1.0,
                    a_max=1.0, v_max=2.0, d_min=0.0, workspace=(-1.0, 5.0, -3.0, 3.0),
                    objective=objective)


def example_instance(objective="fuel", d_min=1.0, horizon=12, dt=0.5, inflate=0.0):
    """The two-vehicle instance of the worked example (meters, seconds).

    inflate grows the block by that margin on every side (inter-sample safety).
    """
    return Instance(vehicles=[Vehicle((1.0, 4.0), (9.0, 4.0)),
                              Vehicle((9.0, 4.5), (1.0, 4.5))],
                    obstacles=[(4.0 - inflate, 6.0 + inflate, 1.5 - inflate, 5.5 + inflate)],
                    horizon=horizon, dt=dt,
                    a_max=2.0, v_max=3.0, d_min=d_min, workspace=(0.0, 10.0, 0.0, 8.0),
                    objective=objective)


def crossing_instance(m, horizon, seed=0, objective="fuel"):
    """m vehicles on a circle around a central block, each to the antipode."""
    rng = np.random.default_rng(seed)
    center, radius = np.array([5.0, 5.0]), 4.0
    vehicles = []
    for i in range(m):
        ang = 2 * np.pi * i / m + rng.uniform(-0.15, 0.15)
        start = center + radius * np.array([np.cos(ang), np.sin(ang)])
        goal = center - radius * np.array([np.cos(ang), np.sin(ang)])
        vehicles.append(Vehicle(tuple(np.round(start, 3)), tuple(np.round(goal, 3))))
    return Instance(vehicles=vehicles, obstacles=[(4.0, 6.0, 4.0, 6.0)],
                    horizon=horizon, dt=0.5, a_max=2.0, v_max=3.0, d_min=1.0,
                    workspace=(0.0, 10.0, 0.0, 10.0), objective=objective)


def solve_instance(inst, time_limit=None, big_m=None):
    model = MilpModel(inst, big_m=big_m)
    return model, model.solve(time_limit=time_limit)


def arrival_times(model, sol):
    """Arrival time of every vehicle from the binaries w (objective time)."""
    inst = model.inst
    out = []
    for i in range(len(inst.vehicles)):
        ks = [k for k in range(1, inst.horizon + 1) if sol.x[model.w(i, k)] > 0.5]
        out.append(ks[0] * inst.dt)
    return out


# ---------------------------------------------------------------------
# Self-test and report
# ---------------------------------------------------------------------
def _print_trace(trace):
    for e in trace:
        lp = "%.3f" % e["lp"] if np.isfinite(e["lp"]) else "inf"
        print("  node %2d  parent %2d  %-10s  LP %-8s  %s"
              % (e["node"], e["parent"], e["decision"], lp, e["action"]))


def _cc_text(cc):
    """One line describing a continuous_check result."""
    text = "penetration %.4f m" % cc["obstacle_penetration"]
    if cc["penetration_at"] is not None:
        text += " (vehicle %d, t=%.2f s)" % cc["penetration_at"]
    if cc["separation_at"] is not None:
        text += ", min separation %.4f m (vehicles %d-%d, t=%.2f s)" % (
            (cc["min_separation"],) + cc["separation_at"])
    return text


def self_test():
    t_all = time.perf_counter()
    # 1. the worked example is solved, feasible and consistent at every step
    inst = example_instance("fuel")
    model, sol = solve_instance(inst)
    assert sol.status == 0, sol.message
    viol = check_solution(inst, sol)
    assert is_valid(inst, sol), viol
    print("example (fuel): vars %d, cons %d, binaries %d, objective %.4f, "
          "%.3f s, %d B&B nodes" % (sol.n_var, sol.n_cons, sol.n_bin,
                                    sol.objective, sol.solve_time, sol.nodes))
    print("  max violations:", {k: round(float(v), 9) for k, v in viol.items()})
    print("  between samples:", _cc_text(continuous_check(inst, sol)))
    print("  positions (k, A, B, |A-B|_inf):")
    for k in range(inst.horizon + 1):
        pa, pb = sol.positions[0, k], sol.positions[1, k]
        print("    k=%2d  A=(%.3f, %.3f)  B=(%.3f, %.3f)  |A-B|_inf=%.3f"
              % (k, pa[0], pa[1], pb[0], pb[1], np.abs(pa - pb).max()))
    for objective in ("peak", "time"):
        inst_o = example_instance(objective)
        model_o, sol_o = solve_instance(inst_o)
        assert sol_o.status == 0 and is_valid(inst_o, sol_o), objective
        print("example (%s): vars %d, cons %d, binaries %d, objective %.4f, "
              "%.3f s, %d B&B nodes" % (objective, sol_o.n_var, sol_o.n_cons,
                                        sol_o.n_bin, sol_o.objective,
                                        sol_o.solve_time, sol_o.nodes))
        print("  between samples:", _cc_text(continuous_check(inst_o, sol_o)))
        if objective == "time":
            print("  arrival times:", arrival_times(model_o, sol_o),
                  " fuel of this solution: %.4f" % (
                      inst_o.dt * np.abs(sol_o.inputs).sum()))
            for k in (4, 5):
                pa, pb = sol_o.positions[0, k], sol_o.positions[1, k]
                print("    k=%d t=%.1f  A=(%.3f, %.3f)  B=(%.3f, %.3f)  |A-B|_inf=%.3f"
                      % (k, k * inst_o.dt, pa[0], pa[1], pb[0], pb[1],
                         np.abs(pa - pb).max()))
        else:
            print("  peak |u|_inf per vehicle:",
                  np.round(np.abs(sol_o.inputs).max(axis=(1, 2)), 4).tolist())
    # 2. a larger separation costs more fuel (the feasible set shrinks)
    values = []
    for d_min in (0.5, 1.0, 1.5, 2.0):
        inst_d = example_instance("fuel", d_min=d_min)
        _, sol_d = solve_instance(inst_d)
        assert sol_d.status == 0 and is_valid(inst_d, sol_d)
        values.append(sol_d.objective)
    print("fuel vs d_min 0.5, 1.0, 1.5, 2.0:", ["%.4f" % v for v in values])
    assert all(values[q] <= values[q + 1] + 1e-7 for q in range(3))
    assert values[-1] > values[0] + 1e-3
    # 3. the tiny instance: milp == brute force == textbook branch-and-bound
    tiny = tiny_instance()
    tmodel, tsol = solve_instance(tiny)
    assert tsol.status == 0 and is_valid(tiny, tsol)
    root = tmodel.solve(relax=True)
    bf_val, n_lp = brute_force(tmodel)
    bb_val, bb_x, trace = branch_and_bound(tmodel)
    print("tiny: milp %.4f, brute force %.4f over %d LPs, B&B %.4f with %d nodes, "
          "root LP relaxation %.4f" % (tsol.objective, bf_val, n_lp, bb_val,
                                       len(trace), root.objective))
    _print_trace(trace)
    assert abs(tsol.objective - bf_val) < 1e-6
    assert abs(bb_val - bf_val) < 1e-6
    print("  tiny positions:", np.round(tsol.positions[0], 3).tolist())
    print("  tiny inputs:", np.round(tsol.inputs[0], 3).tolist())
    # 4. the effect of the big-M value on the two-vehicle instance
    for big_m in (None, 1e2, 1e4, 1e6):
        _, sol_m = solve_instance(inst, big_m=big_m)
        v = check_solution(inst, sol_m) if sol_m.x is not None else None
        print("  big_m %-6s status %d objective %.4f  %.3f s  %4d nodes  "
              "obstacle %.1e  separation %.1e" % (
                  "tight" if big_m is None else "%.0e" % big_m, sol_m.status,
                  sol_m.objective, sol_m.solve_time, sol_m.nodes,
                  v["obstacle"] if v else float("nan"),
                  v["separation"] if v else float("nan")))
    # 5. inter-sample safety: the margins of the proposition (obstacle
    #    inflated by v_max dt / 2, separation raised by v_max dt) make the
    #    continuous motion safe with respect to the ORIGINAL block and d_min
    delta = inst.v_max * inst.dt / 2
    safe = example_instance("fuel", d_min=inst.d_min + inst.v_max * inst.dt,
                            inflate=delta)
    _, sol_s = solve_instance(safe)
    assert sol_s.status == 0 and is_valid(safe, sol_s)
    cc = continuous_check(inst, sol_s)
    print("safe margins (block +%.2f m, d_min %.2f m): objective %.4f, %.2f s, "
          "%d nodes" % (delta, safe.d_min, sol_s.objective, sol_s.solve_time,
                        sol_s.nodes))
    print("  between samples vs the original block:", _cc_text(cc))
    assert cc["obstacle_penetration"] <= 1e-9
    assert cc["min_separation"] >= inst.d_min - 1e-9
    half = example_instance("fuel", inflate=delta)      # obstacle margin only
    _, sol_h = solve_instance(half)
    assert sol_h.status == 0 and is_valid(half, sol_h)
    print("block margin only: objective %.4f;" % sol_h.objective,
          _cc_text(continuous_check(inst, sol_h)))
    # 6. a finer time step reduces corner cutting but costs solve time
    fine = example_instance("fuel", horizon=24, dt=0.25)
    _, sol_f = solve_instance(fine, time_limit=30.0)
    assert sol_f.x is not None and is_valid(fine, sol_f)
    print("dt=0.25, N=24: status %d, objective %.4f, %.1f s, %d nodes, %d binaries"
          % (sol_f.status, sol_f.objective, sol_f.solve_time, sol_f.nodes,
             sol_f.n_bin))
    print("  between samples:", _cc_text(continuous_check(fine, sol_f)))
    # 7. an infeasible instance returns a status and nothing else
    short = example_instance("fuel", horizon=8)
    _, sol_i = solve_instance(short)
    assert sol_i.status == 2 and sol_i.x is None
    print("N=8 (too short): status %d, message '%s', %.3f s"
          % (sol_i.status, sol_i.message, sol_i.solve_time))
    print("self-test passed in %.1f s" % (time.perf_counter() - t_all))


if __name__ == "__main__":
    self_test()
