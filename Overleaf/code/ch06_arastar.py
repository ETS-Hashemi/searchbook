"""ARA*: Anytime Repairing A* on 2D grids (reference code for Chapter 6).

The implementation follows Likhachev, Gordon and Thrun, "ARA*: Anytime A*
with provable bounds on sub-optimality" (NIPS 2003):

* fvalue(s) = g(s) + eps * h(s) with an inflation factor eps >= 1;
* the lists OPEN, CLOSED and INCONS;
* ImprovePath expands states while fvalue(goal) > min over OPEN of fvalue,
  expands every state at most once per call, and moves a state whose g is
  lowered after it was closed into INCONS instead of re-expanding it;
* Main decreases eps between calls, merges INCONS into OPEN, recomputes the
  keys, empties CLOSED, and publishes after every call the current path with
  its bound eps' = min(eps, g(goal) / min_{s in OPEN u INCONS} (g(s) + h(s))).

Grid conventions
----------------
A cell is a pair (x, y): x is the column, y the row, and (0, 0) is the
bottom-left cell.  4-connected moves cost 1; 8-connected moves cost 1 or
sqrt(2), and a diagonal move is allowed only if the two cells it cuts across
are free (no corner cutting).  Heuristics: Manhattan distance (4-connected)
and octile distance (8-connected).  Both are consistent.

Run the file to execute the self-test:  python3 ch06_arastar.py
"""
from __future__ import annotations

import heapq
import math
import time
from dataclasses import dataclass, field
from typing import Iterator

import numpy as np

INF = math.inf
SQRT2 = math.sqrt(2.0)


class Grid:
    """Rectangular grid with blocked cells and 4- or 8-connected moves."""

    def __init__(self, width, height, obstacles=(), connectivity=4):
        if connectivity not in (4, 8):
            raise ValueError("connectivity must be 4 or 8")
        self.width = int(width)
        self.height = int(height)
        self.obstacles = frozenset(tuple(c) for c in obstacles)
        self.connectivity = connectivity

    def is_free(self, cell):
        """True if the cell lies inside the grid and is not blocked."""
        x, y = cell
        return (0 <= x < self.width and 0 <= y < self.height
                and cell not in self.obstacles)

    def successors(self, cell):
        """Return the (neighbour, cost) pairs of a free cell."""
        x, y = cell
        result = []
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nxt = (x + dx, y + dy)
            if self.is_free(nxt):
                result.append((nxt, 1.0))
        if self.connectivity == 8:
            for dx, dy in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
                nxt = (x + dx, y + dy)
                if (self.is_free(nxt) and self.is_free((x + dx, y))
                        and self.is_free((x, y + dy))):
                    result.append((nxt, SQRT2))
        return result

    def heuristic(self, cell, goal):
        """Manhattan (4-connected) or octile (8-connected) distance."""
        dx = abs(cell[0] - goal[0])
        dy = abs(cell[1] - goal[1])
        if self.connectivity == 4:
            return float(dx + dy)
        return float(max(dx, dy) + (SQRT2 - 1.0) * min(dx, dy))


@dataclass
class Solution:
    """One published ARA* solution (the result of one ImprovePath call)."""

    iteration: int          # 1, 2, ...
    eps: float              # inflation used in this iteration
    eps_bound: float        # eps': published bound, cost <= eps_bound * C*
    lower_bound: float      # L = min over OPEN u INCONS of g + h  (L <= C*)
    path: list              # cells from start to goal (via back-pointers)
    cost: float             # cost of `path` (never larger than g_goal)
    g_goal: float           # g(goal) at the end of the iteration
    expansions: int         # expansions in this iteration
    total_expansions: int   # expansions so far, all iterations together
    closed: frozenset = field(default_factory=frozenset, repr=False)
    open: frozenset = field(default_factory=frozenset, repr=False)
    incons: frozenset = field(default_factory=frozenset, repr=False)


class ARAStar:
    """Anytime Repairing A* (Likhachev, Gordon and Thrun, 2003).

    ``ARAStar(grid, start, goal, schedule).run()`` is a generator.  It yields
    a Solution after every ImprovePath call, i.e. once per value of the eps
    schedule, and stops early as soon as the published bound eps' is 1
    (``stop_when_optimal=True``).  With ``trace=True`` every expansion is
    recorded in ``self.trace`` (used for the tables of the chapter).
    """

    def __init__(self, grid, start, goal, schedule=(3.0, 2.0, 1.0),
                 stop_when_optimal=True, trace=False):
        self.grid = grid
        self.start = tuple(start)
        self.goal = tuple(goal)
        self.schedule = [float(e) for e in schedule]
        if not self.schedule or min(self.schedule) < 1.0:
            raise ValueError("schedule must be non-empty with all eps >= 1")
        if any(b > a for a, b in zip(self.schedule, self.schedule[1:])):
            raise ValueError("schedule must be non-increasing")
        self.stop_when_optimal = stop_when_optimal
        self.trace = [] if trace else None
        self.eps = self.schedule[0]
        self.g = {}
        self.parent = {}
        self.open_set = set()
        self.closed = set()
        self.incons = set()
        self._heap = []
        self._seq = 0
        self.total_expansions = 0
        self.iteration = 0

    # ---- keys and the OPEN priority queue --------------------------------
    def h(self, s):
        return self.grid.heuristic(s, self.goal)

    def fvalue(self, s):
        """fvalue(s) = g(s) + eps * h(s); infinity for unvisited states."""
        return self.g.get(s, INF) + self.eps * self.h(s)

    def _push(self, s):
        """Insert s into OPEN with its current key (or update the key).

        Ties on fvalue are broken towards the smaller h, then first-in
        first-out.  Old heap entries of s become stale and are skipped.
        """
        self.open_set.add(s)
        self._seq += 1
        heapq.heappush(self._heap,
                       (self.fvalue(s), self.h(s), self._seq, s, self.g[s]))

    def _discard_stale(self):
        while self._heap:
            _, _, _, s, g_at_push = self._heap[0]
            if s in self.open_set and g_at_push == self.g[s]:
                return
            heapq.heappop(self._heap)

    def _min_open_f(self):
        """min over OPEN of fvalue; infinity when OPEN is empty."""
        self._discard_stale()
        return self._heap[0][0] if self._heap else INF

    def _pop_open(self):
        self._discard_stale()
        _, _, _, s, _ = heapq.heappop(self._heap)
        self.open_set.discard(s)
        return s

    # ---- ImprovePath -----------------------------------------------------
    def improve_path(self):
        """One ImprovePath call at the current eps; returns #expansions."""
        expansions = 0
        while self.fvalue(self.goal) > self._min_open_f():
            s = self._pop_open()
            assert s not in self.closed  # expanded at most once per call
            self.closed.add(s)
            expansions += 1
            lowered = []
            for t, c in self.grid.successors(s):
                g_new = self.g[s] + c
                if g_new < self.g.get(t, INF):
                    self.g[t] = g_new
                    self.parent[t] = s
                    if t in self.closed:
                        self.incons.add(t)       # improved but already closed
                        lowered.append((t, g_new, "INCONS"))
                    else:
                        self._push(t)            # insert or update key
                        lowered.append((t, g_new, "OPEN"))
            if self.trace is not None:
                self.trace.append({
                    "event": "expand", "iteration": self.iteration,
                    "step": expansions, "state": s, "g": self.g[s],
                    "h": self.h(s), "f": self.fvalue(s), "lowered": lowered,
                    "min_open_f": self._min_open_f(),
                    "f_goal": self.fvalue(self.goal),
                    "open": self._open_snapshot()})
        return expansions

    # ---- Main ------------------------------------------------------------
    def _start_iteration(self, eps):
        """OPEN := OPEN u INCONS with keys recomputed for eps; CLOSED := {}."""
        self.eps = eps
        self.open_set |= self.incons
        self.incons = set()
        self.closed = set()
        self._heap = []
        for s in sorted(self.open_set):
            self._push(s)

    def _bound(self):
        """Return (L, eps') for the current solution.

        L = min over OPEN u INCONS of g + h is a lower bound on C*.  The
        published bound is eps' = min(eps, g(goal)/L); if g(goal) <= L the
        solution is already optimal and eps' = 1.
        """
        candidates = self.open_set | self.incons
        lower = min((self.g[s] + self.h(s) for s in candidates), default=INF)
        g_goal = self.g.get(self.goal, INF)
        ratio = 1.0 if g_goal <= lower else g_goal / lower
        return lower, max(1.0, min(self.eps, ratio))

    def extract_path(self):
        """Follow the back-pointers from the goal to the start."""
        path = [self.goal]
        while path[-1] != self.start:
            path.append(self.parent[path[-1]])
        path.reverse()
        return path

    def _open_snapshot(self):
        return sorted((s, self.g[s], self.fvalue(s)) for s in self.open_set)

    def run(self) -> Iterator[Solution]:
        """Generator: yields one Solution per ImprovePath call."""
        self.g = {self.start: 0.0}
        self.parent = {}
        self.open_set, self.closed, self.incons = set(), set(), set()
        self._heap = []
        self.total_expansions = 0
        self.eps = self.schedule[0]
        self._push(self.start)
        for i, eps in enumerate(self.schedule):
            self.iteration = i + 1
            if i > 0:
                self._start_iteration(eps)
            if self.trace is not None:
                self.trace.append({"event": "start", "iteration": i + 1,
                                   "eps": eps, "open": self._open_snapshot()})
            n = self.improve_path()
            self.total_expansions += n
            if self.g.get(self.goal, INF) == INF:
                return                           # no path exists
            lower, eps_prime = self._bound()
            path = self.extract_path()
            yield Solution(iteration=i + 1, eps=eps, eps_bound=eps_prime,
                           lower_bound=lower, path=path,
                           cost=path_cost(self.grid, path),
                           g_goal=self.g[self.goal], expansions=n,
                           total_expansions=self.total_expansions,
                           closed=frozenset(self.closed),
                           open=frozenset(self.open_set),
                           incons=frozenset(self.incons))
            if self.stop_when_optimal and eps_prime <= 1.0:
                return                           # published bound is 1


def weighted_astar(grid, start, goal, eps):
    """Weighted A* without re-expansions = a single ImprovePath call.

    Returns a Solution (with its bound eps') or None if no path exists.
    """
    return next(iter(ARAStar(grid, start, goal, schedule=(eps,)).run()), None)


def dijkstra(grid, start, goal):
    """Optimal cost from start to goal (infinity if unreachable)."""
    dist = {tuple(start): 0.0}
    heap = [(0.0, tuple(start))]
    while heap:
        d, s = heapq.heappop(heap)
        if s == tuple(goal):
            return d
        if d > dist[s]:
            continue
        for t, c in grid.successors(s):
            if d + c < dist.get(t, INF):
                dist[t] = d + c
                heapq.heappush(heap, (d + c, t))
    return INF


def path_cost(grid, path):
    """Cost of a path given as a list of cells; raises if it is not valid."""
    total = 0.0
    for a, b in zip(path, path[1:]):
        costs = [c for t, c in grid.successors(a) if t == b]
        if not costs:
            raise ValueError(f"invalid move {a} -> {b}")
        total += costs[0]
    return total


def random_grid(rng, width, height, density, connectivity, start, goal):
    """Random grid with blocked cells drawn independently with `density`."""
    blocked = rng.random((height, width)) < density
    obstacles = {(int(x), int(y)) for y, x in zip(*np.nonzero(blocked))}
    obstacles.discard(tuple(start))
    obstacles.discard(tuple(goal))
    return Grid(width, height, obstacles, connectivity)


# Worked example of the chapter (Section "A worked example"): 8 x 6 grid.
EXAMPLE_WIDTH, EXAMPLE_HEIGHT = 8, 6
EXAMPLE_OBSTACLES = set()          # filled in below (see gen_ch06_example.py)
EXAMPLE_START, EXAMPLE_GOAL = (0, 0), (7, 5)


def _self_test():
    t0 = time.time()
    rng = np.random.default_rng(6)
    schedule = (3.0, 2.0, 1.5, 1.0)
    n_paths = n_grids = n_nonmonotone = 0
    for k in range(80):
        conn = 4 if k % 2 == 0 else 8
        w, hgt = 24, 18
        start, goal = (0, 0), (w - 1, hgt - 1)
        grid = random_grid(rng, w, hgt, 0.25, conn, start, goal)
        c_star = dijkstra(grid, start, goal)
        ara = ARAStar(grid, start, goal, schedule)
        sols = list(ara.run())
        if c_star == INF:
            assert sols == [], "ARA* must publish nothing when no path exists"
            continue
        n_grids += 1
        assert sols, "ARA* must find a path when one exists"
        prev_g = INF
        for sol in sols:
            # the published path is a valid start-goal path
            assert sol.path[0] == start and sol.path[-1] == goal
            assert abs(path_cost(grid, sol.path) - sol.cost) < 1e-9
            # the pointer path never costs more than g(goal)
            assert sol.cost <= sol.g_goal + 1e-9
            # L is a lower bound on C* and eps' a valid bound
            assert sol.lower_bound <= c_star + 1e-9
            assert 1.0 <= sol.eps_bound <= sol.eps + 1e-12
            assert sol.cost <= sol.eps_bound * c_star + 1e-9
            assert sol.cost <= sol.eps * c_star + 1e-9
            # g(goal) never increases between iterations
            assert sol.g_goal <= prev_g + 1e-9
            prev_g = sol.g_goal
            n_paths += 1
        if any(b.cost > a.cost + 1e-9 for a, b in zip(sols, sols[1:])):
            n_nonmonotone += 1
        # the last published path (eps = 1 or eps' = 1) is optimal
        assert abs(sols[-1].cost - c_star) < 1e-9
        assert sols[-1].eps_bound == 1.0
        # ARA*'s first iteration is exactly weighted A* at eps_0
        wa = weighted_astar(grid, start, goal, schedule[0])
        assert wa.cost == sols[0].cost and wa.expansions == sols[0].expansions
    assert n_grids >= 40, "too few solvable test grids"
    # the worked example of the chapter (numbers quoted in the text)
    grid = Grid(EXAMPLE_WIDTH, EXAMPLE_HEIGHT, EXAMPLE_OBSTACLES, 4)
    sols = list(ARAStar(grid, EXAMPLE_START, EXAMPLE_GOAL, (3.0, 2.0, 1.0)).run())
    print(f"example: {[(s.eps, s.cost, round(s.eps_bound, 3), s.expansions) for s in sols]}")
    dt = time.time() - t0
    print(f"self-test passed: {n_paths} published paths on {n_grids} grids "
          f"checked against Dijkstra ({n_nonmonotone} grids with a "
          f"non-monotone published cost sequence), {dt:.2f} s")


if __name__ == "__main__":
    _self_test()
