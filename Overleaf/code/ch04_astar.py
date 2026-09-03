#!/usr/bin/env python3
"""A* search on graphs and grids, weighted A*, and space-time A*.

Reference implementation for Chapter 4 of "Multi-Agent Path Planning and
Drone Collision Avoidance".

Conventions
-----------
* A grid is a 2-D NumPy array ``grid[y, x]`` with 0 = free, 1 = obstacle.
* A cell is a tuple ``(x, y)``: ``x`` is the column, ``y`` the row, and
  ``(0, 0)`` is the bottom-left cell of the figures in the book.
* 4-connected moves cost 1; 8-connected diagonal moves cost sqrt(2) and may
  not cut corners (both orthogonal neighbours must be free).
* Space-time states are ``(cell, t)``; a move or a wait costs one time step.

Run ``python3 ch04_astar.py`` for the self-test (finishes in a few seconds).
"""
from __future__ import annotations

import heapq
import itertools
import math
from collections import deque
from dataclasses import dataclass, field

import numpy as np

INF = float("inf")
EPS = 1e-9          # tolerance for floating-point ties in g and f
SQRT2 = math.sqrt(2.0)


# ---------------------------------------------------------------------------
# Grid heuristics
# ---------------------------------------------------------------------------
def manhattan(a, b):
    """|dx| + |dy|; exact on an empty 4-connected grid."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def octile(a, b):
    """max(dx, dy) + (sqrt(2) - 1) * min(dx, dy); exact on an empty 8-grid."""
    dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
    return max(dx, dy) + (SQRT2 - 1.0) * min(dx, dy)


def euclidean(a, b):
    """Straight-line distance; admissible for every grid connectivity."""
    return math.hypot(a[0] - b[0], a[1] - b[1])


def chebyshev(a, b):
    """max(dx, dy); exact on an 8-grid whose diagonal moves cost 1."""
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def zero(a, b):
    """h = 0 turns A* into Dijkstra's algorithm (uniform-cost search)."""
    return 0.0


HEURISTICS = {"manhattan": manhattan, "octile": octile, "euclidean": euclidean,
              "chebyshev": chebyshev, "zero": zero}


# ---------------------------------------------------------------------------
# Result containers
# ---------------------------------------------------------------------------
@dataclass
class Expansion:
    """One pop from Open: the node and its g, h and f at that moment."""
    node: object
    g: float
    h: float
    f: float
    open_after: tuple = ()      # (node, f) pairs of Open after the expansion


@dataclass
class SearchResult:
    """What a search returns: the path (None on failure) and statistics."""
    path: list | None
    cost: float
    expansions: list = field(default_factory=list)
    closed: set = field(default_factory=set)
    open_nodes: set = field(default_factory=set)
    g: dict = field(default_factory=dict)
    reopenings: int = 0

    @property
    def num_expansions(self):
        return len(self.expansions)


def _reconstruct(parent, node):
    path = [node]
    while parent[path[-1]] is not None:
        path.append(parent[path[-1]])
    path.reverse()
    return path


# ---------------------------------------------------------------------------
# Generic A* on an implicit graph
# ---------------------------------------------------------------------------
def astar(start, goal, successors, heuristic, weight=1.0, tie_break="high_g",
          reopen=True, record_open=False):
    """A* graph search with a closed set and a lazy priority queue.

    start        : hashable start node.
    goal         : a node, or a predicate ``is_goal(node)``.
    successors   : ``successors(n)`` yields ``(n2, cost)`` pairs, cost >= 0.
    heuristic    : ``heuristic(n)`` returns h(n) >= 0.
    weight       : w >= 1 gives weighted A* with f = g + w * h.
    tie_break    : "high_g" (prefer larger g), "low_g" or "fifo".
    reopen       : allow a closed node to be re-opened when a cheaper path
                   to it is found (only needed for inconsistent heuristics).
    record_open  : store a snapshot of Open after every expansion (slow;
                   meant for traces and pictures of small instances).
    """
    is_goal = goal if callable(goal) else (lambda n: n == goal)
    counter = itertools.count()          # FIFO among full ties

    def key(f, g_value):
        f = round(f, 9)                  # ignore floating-point noise in ties
        if tie_break == "high_g":
            return (f, -g_value, next(counter))
        if tie_break == "low_g":
            return (f, g_value, next(counter))
        return (f, next(counter))

    def live_open():                     # nodes in Open with their current f
        return tuple(sorted((m, round(ge + weight * heuristic(m), 9))
                            for (_, ge, m) in open_heap
                            if ge == g[m] and m not in closed))

    g = {start: 0.0}
    parent = {start: None}
    closed = set()
    expansions = []
    reopenings = 0
    open_heap = [(key(weight * heuristic(start), 0.0), 0.0, start)]
    while open_heap:
        _, g_entry, n = heapq.heappop(open_heap)
        if g_entry > g[n]:               # stale entry: a cheaper path was found
            continue
        h_n = heuristic(n)
        expansions.append(Expansion(n, g[n], h_n, g[n] + weight * h_n))
        if is_goal(n):
            snapshot = live_open()
            if record_open:
                expansions[-1].open_after = snapshot
            return SearchResult(_reconstruct(parent, n), g[n], expansions,
                                closed, {m for (m, _) in snapshot}, g, reopenings)
        closed.add(n)
        for n2, c in successors(n):
            g2 = g[n] + c
            if g2 < g.get(n2, INF) - EPS:  # relaxation (EPS: fp noise)
                if n2 in closed:
                    if not reopen:
                        continue
                    closed.discard(n2)   # re-open (never for consistent h)
                    reopenings += 1
                g[n2] = g2
                parent[n2] = n
                f2 = g2 + weight * heuristic(n2)
                heapq.heappush(open_heap, (key(f2, g2), g2, n2))
        if record_open:
            expansions[-1].open_after = live_open()
    return SearchResult(None, INF, expansions, closed, set(), g, reopenings)


# ---------------------------------------------------------------------------
# Grids
# ---------------------------------------------------------------------------
MOVES4 = ((1, 0), (0, 1), (-1, 0), (0, -1))          # E, N, W, S
MOVES8 = MOVES4 + ((1, 1), (-1, 1), (-1, -1), (1, -1))  # then NE, NW, SW, SE


def grid_successors(grid, connectivity=4):
    """Return ``successors(cell)`` for a 4- or 8-connected occupancy grid."""
    rows, cols = grid.shape
    moves = MOVES4 if connectivity == 4 else MOVES8

    def free(x, y):
        return 0 <= x < cols and 0 <= y < rows and grid[y, x] == 0

    def successors(cell):
        x, y = cell
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if not free(nx, ny):
                continue
            if dx != 0 and dy != 0:                   # diagonal move
                if not (free(x + dx, y) and free(x, y + dy)):
                    continue                          # no corner cutting
                yield (nx, ny), SQRT2
            else:
                yield (nx, ny), 1.0
    return successors


def astar_grid(grid, start, goal, heuristic="manhattan", connectivity=4,
               weight=1.0, tie_break="high_g"):
    """A* between two cells of an occupancy grid."""
    h = HEURISTICS[heuristic] if isinstance(heuristic, str) else heuristic
    start, goal = tuple(start), tuple(goal)
    return astar(start, goal, grid_successors(grid, connectivity),
                 lambda n: h(n, goal), weight, tie_break)


def dijkstra_grid(grid, source, connectivity=4):
    """Cost from ``source`` to every reachable cell (reference for tests)."""
    succ = grid_successors(grid, connectivity)
    source = tuple(source)
    dist = {source: 0.0}
    heap = [(0.0, source)]
    while heap:
        d, n = heapq.heappop(heap)
        if d > dist[n]:
            continue
        for n2, c in succ(n):
            if d + c < dist.get(n2, INF):
                dist[n2] = d + c
                heapq.heappush(heap, (d + c, n2))
    return dist


def static_distances(grid, goal, connectivity=4):
    """Number of moves from every cell to ``goal`` (breadth-first search)."""
    succ = grid_successors(grid, connectivity)
    goal = tuple(goal)
    dist = {goal: 0}
    queue = deque([goal])
    while queue:
        n = queue.popleft()
        for n2, _ in succ(n):                  # grids are symmetric
            if n2 not in dist:
                dist[n2] = dist[n] + 1
                queue.append(n2)
    return dist


# ---------------------------------------------------------------------------
# Space-time A*
# ---------------------------------------------------------------------------
class ReservationTable:
    """Vertex constraints (v, t), edge constraints (u, v, t) and parked agents.

    A vertex constraint forbids being at cell v at time t.  An edge
    constraint forbids moving from u to v between t and t+1.  An agent that
    reached its goal at time T occupies it for every t >= T.
    """

    def __init__(self, constraints=()):
        self.vertex = set()
        self.edge = set()
        self.parked = {}
        for c in constraints:
            self.add(c)

    def add(self, c):
        if len(c) == 2:
            self.add_vertex(*c)
        elif len(c) == 3:
            self.add_edge(*c)
        else:
            raise ValueError("constraint must be (v, t) or (u, v, t)")

    def add_vertex(self, v, t):
        self.vertex.add((tuple(v), int(t)))

    def add_edge(self, u, v, t):
        self.edge.add((tuple(u), tuple(v), int(t)))

    def add_path(self, path):
        """Reserve a whole path; forbids swaps and parks the agent at the end."""
        for t, v in enumerate(path):
            self.add_vertex(v, t)
        for t in range(len(path) - 1):
            if path[t] != path[t + 1]:
                self.add_edge(path[t + 1], path[t], t)   # no head-on swap
        self.parked[tuple(path[-1])] = len(path) - 1

    def vertex_blocked(self, v, t):
        return (v, t) in self.vertex or t >= self.parked.get(v, INF)

    def edge_blocked(self, u, v, t):
        return (u, v, t) in self.edge

    def last_blocked_time(self, v):
        """Largest t at which v is blocked: -1 if never, INF if parked on."""
        if v in self.parked:
            return INF
        return max((t for (u, t) in self.vertex if u == v), default=-1)

    def horizon(self):
        """Largest time index that appears in any constraint (-1 if none)."""
        times = [t for (_, t) in self.vertex] + [t + 1 for (_, _, t) in self.edge]
        times += list(self.parked.values())
        return max(times, default=-1)


def default_horizon(grid, goal, table, connectivity=4):
    """Latest arrival time worth searching.

    After the last constraint (time H = table.horizon()) the world is
    static, so if a solution exists, one exists that arrives no later than
    H + 1 + (largest static distance to the goal when the parked agents are
    treated as walls).  States beyond this time are not generated.
    """
    post = grid.copy()
    for (x, y) in table.parked:
        post[y, x] = 1
    reach = static_distances(post, tuple(goal), connectivity)
    return table.horizon() + 1 + max(reach.values())


def space_time_astar(grid, start, goal, constraints=(), max_time=None,
                     connectivity=4, tie_break="high_g", record_open=False):
    """Space-time A* with waits, vertex/edge constraints and goal-stay test.

    constraints : a ReservationTable or an iterable of (v, t) and (u, v, t).
    max_time    : time horizon; None uses default_horizon(), which keeps
                  the search complete (no state with t > max_time exists).
    The returned path is indexed by time: path[t] is the cell at step t,
    and the agent stays at path[-1] for ever afterwards.  Every step (move
    or wait) costs 1, so g(v, t) = t and the first discovery of a state
    is already its cheapest: duplicate detection replaces relaxation.
    """
    table = (constraints if isinstance(constraints, ReservationTable)
             else ReservationTable(constraints))
    start, goal = tuple(start), tuple(goal)
    succ = grid_successors(grid, connectivity)
    h = static_distances(grid, goal, connectivity)   # exact static distances
    t_goal = table.last_blocked_time(goal)           # goal must be free after
    if start not in h or t_goal == INF:
        return SearchResult(None, INF)
    if max_time is None:
        max_time = default_horizon(grid, goal, table, connectivity)
    counter = itertools.count()

    def key(v, t):
        f = t + h[v]
        return (f, -t, next(counter)) if tie_break == "high_g" else (f, t, next(counter))

    s0 = (start, 0)
    parent = {s0: None}                 # parents = the set of generated states
    closed = set()
    expansions = []
    heap = [(key(*s0), s0)]
    while heap:
        _, (v, t) = heapq.heappop(heap)  # every state is pushed exactly once
        closed.add((v, t))
        expansions.append(Expansion((v, t), t, h[v], t + h[v]))
        if v == goal and t > t_goal:                 # stay-at-goal is safe
            path = [s[0] for s in _reconstruct(parent, (v, t))]
            if record_open:
                expansions[-1].open_after = tuple(sorted((s, s[1] + h[s[0]]) for (_, s) in heap))
            return SearchResult(path, float(t), expansions, closed,
                                {s for (_, s) in heap}, {s: s[1] for s in closed})
        if t < max_time:
            for v2 in [v] + [n for n, _ in succ(v)]:     # wait first, then moves
                if v2 not in h:                          # cannot reach the goal
                    continue
                if table.vertex_blocked(v2, t + 1) or table.edge_blocked(v, v2, t):
                    continue
                s2 = (v2, t + 1)
                if s2 in parent:                         # g = t + 1: first path is best
                    continue
                parent[s2] = (v, t)
                heapq.heappush(heap, (key(*s2), s2))
        if record_open:
            expansions[-1].open_after = tuple(sorted((s, s[1] + h[s[0]]) for (_, s) in heap))
    return SearchResult(None, INF, expansions, closed, set(), {})


def constraints_for_agent(agent, constraints):
    """Keep the MAPF constraints (a, v, t) and (a, u, v, t) of one agent and
    drop the agent index: the (v, t) / (u, v, t) tuples space_time_astar uses."""
    return [tuple(c[1:]) for c in constraints if c[0] == agent]


def path_respects(path, table):
    """True if a time-indexed path (with stay-at-goal) violates no constraint."""
    for t, v in enumerate(path):
        if table.vertex_blocked(v, t):
            return False
        if t + 1 < len(path) and table.edge_blocked(v, path[t + 1], t):
            return False
    goal, arrival = path[-1], len(path) - 1
    if table.last_blocked_time(goal) >= arrival:
        return False
    return True


# ---------------------------------------------------------------------------
# Instances used in the chapter
# ---------------------------------------------------------------------------
def worked_example_grid():
    """The 6x6 grid of the worked example (Section 4.5)."""
    grid = np.zeros((6, 6), dtype=int)
    for y in (0, 1, 2, 3):
        grid[y, 2] = 1                       # wall at x = 2, y = 0..3
    for y in (1, 2, 3, 4):
        grid[y, 4] = 1                       # wall at x = 4, y = 1..4
    return grid


WORKED_START, WORKED_GOAL = (0, 0), (5, 2)


def inadmissible_example():
    """Tiny graph on which an overestimating heuristic misleads A*."""
    edges = {"s": [("a", 1.0), ("b", 1.0)], "a": [("z", 1.0)],
             "b": [("z", 2.0)], "z": []}
    h_bad = {"s": 2.0, "a": 4.0, "b": 1.0, "z": 0.0}    # h(a) > h*(a) = 1
    return edges, h_bad


def inconsistent_example():
    """Admissible but inconsistent heuristic: node b must be re-opened."""
    edges = {"s": [("a", 1.0), ("b", 3.0)], "a": [("b", 1.0)],
             "b": [("z", 2.0)], "z": []}
    h = {"s": 0.0, "a": 3.0, "b": 0.0, "z": 0.0}       # h(a) > c(a,b) + h(b)
    return edges, h


def spacetime_example():
    """3x3 empty grid, start (0,1), goal (2,1), vertex constraint ((1,1), 1)."""
    grid = np.zeros((3, 3), dtype=int)
    return grid, (0, 1), (2, 1), [((1, 1), 1)]


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
def _random_grid(rng, n, density):
    grid = (rng.random((n, n)) < density).astype(int)
    return grid


def _random_pair(rng, grid, connectivity):
    """A random (start, goal) pair connected in the given grid."""
    free = [(int(x), int(y)) for y, x in zip(*np.nonzero(grid == 0))]
    while True:
        s, z = free[rng.integers(len(free))], free[rng.integers(len(free))]
        if s != z and z in dijkstra_grid(grid, s, connectivity):
            return s, z


def _self_test():
    rng = np.random.default_rng(4)

    # 1. Optimality against Dijkstra, all admissible heuristic/grid pairs.
    for _ in range(25):
        grid = _random_grid(rng, 12, 0.25)
        for conn, names in ((4, ("manhattan", "octile", "euclidean", "chebyshev")),
                            (8, ("octile", "euclidean", "chebyshev"))):
            s, z = _random_pair(rng, grid, conn)
            ref = dijkstra_grid(grid, s, conn)[z]
            for name in names:
                res = astar_grid(grid, s, z, name, conn)
                assert abs(res.cost - ref) < 1e-9, (name, conn, res.cost, ref)
                assert res.reopenings == 0                 # consistent h
                fs = [e.f for e in res.expansions]
                assert all(fs[i] <= fs[i + 1] + 1e-9 for i in range(len(fs) - 1))
                assert len(res.path) >= 1 and res.path[0] == s and res.path[-1] == z
            # weighted A*: cost <= w * optimum
            for w in (1.5, 2.0, 3.0):
                res = astar_grid(grid, s, z, "manhattan" if conn == 4 else "octile",
                                 conn, weight=w)
                assert res.cost <= w * ref + 1e-9
            # dominance: nodes surely expanded by the stronger heuristic are
            # expanded by the weaker one as well
            if conn == 8:
                strong = astar_grid(grid, s, z, "octile", 8)
                weak = astar_grid(grid, s, z, "euclidean", 8)
                surely = {e.node for e in strong.expansions if e.f < strong.cost - 1e-9}
                assert surely <= {e.node for e in weak.expansions}

    # 2. Manhattan distance is NOT admissible on an 8-connected grid: it
    #    overestimates a diagonal step, and A* then misses optimal paths.
    assert manhattan((0, 0), (1, 1)) > SQRT2
    suboptimal = 0
    rng8 = np.random.default_rng(4)
    for _ in range(40):
        grid = _random_grid(rng8, 12, 0.25)
        s, z = _random_pair(rng8, grid, 8)
        res = astar_grid(grid, s, z, "manhattan", 8)
        suboptimal += res.cost > dijkstra_grid(grid, s, 8)[z] + 1e-9
    assert suboptimal > 0, "expected at least one suboptimal path"

    # 3. The inadmissible counterexample of the chapter.
    edges, h_bad = inadmissible_example()
    res = astar("s", "z", lambda n: iter(edges[n]), h_bad.get)
    assert res.path == ["s", "b", "z"] and res.cost == 3.0   # optimum is 2
    assert [e.node for e in res.expansions] == ["s", "b", "z"]

    # 4. Admissible but inconsistent: re-opening restores optimality.
    edges, h = inconsistent_example()
    res = astar("s", "z", lambda n: iter(edges[n]), h.get, reopen=True)
    assert res.cost == 4.0 and res.reopenings == 1
    assert [e.node for e in res.expansions] == ["s", "b", "a", "b", "z"]
    res = astar("s", "z", lambda n: iter(edges[n]), h.get, reopen=False)
    assert res.cost == 5.0                                   # suboptimal

    # 5. The worked example: numbers quoted in the chapter.
    grid = worked_example_grid()
    res = astar_grid(grid, WORKED_START, WORKED_GOAL, "manhattan", 4)
    assert res.cost == 13.0 and res.num_expansions == 21 and res.reopenings == 0
    assert res.path == [(0, 0), (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (2, 4),
                        (3, 4), (3, 5), (4, 5), (5, 5), (5, 4), (5, 3), (5, 2)]
    first = [(e.node, e.g, e.h, e.f) for e in res.expansions[:10]]
    assert first == [((0, 0), 0, 7, 7), ((1, 0), 1, 6, 7), ((1, 1), 2, 5, 7),
                     ((1, 2), 3, 4, 7), ((0, 1), 1, 6, 7), ((0, 2), 2, 5, 7),
                     ((1, 3), 4, 5, 9), ((0, 3), 3, 6, 9), ((1, 4), 5, 6, 11),
                     ((2, 4), 6, 5, 11)], first
    assert [e.node for e in res.expansions[10:]] == [
        (3, 4), (3, 3), (3, 2), (0, 4), (3, 1), (3, 5), (4, 5), (5, 5), (5, 4),
        (5, 3), (5, 2)]
    assert sorted(res.open_nodes) == [(0, 5), (1, 5), (2, 5), (3, 0)]
    traced = astar_grid(grid, WORKED_START, WORKED_GOAL, "manhattan", 4)
    traced = astar(WORKED_START, WORKED_GOAL, grid_successors(grid, 4),
                   lambda n: manhattan(n, WORKED_GOAL), record_open=True)
    assert {m for (m, _) in traced.expansions[-1].open_after} == res.open_nodes
    assert traced.expansions[0].open_after == (((0, 1), 7), ((1, 0), 7))
    dij = astar_grid(grid, WORKED_START, WORKED_GOAL, "zero", 4)
    assert dij.cost == 13.0 and dij.num_expansions == 26
    low = astar_grid(grid, WORKED_START, WORKED_GOAL, "manhattan", 4, tie_break="low_g")
    assert low.cost == 13.0 and low.num_expansions == 24
    oct8 = astar_grid(grid, WORKED_START, WORKED_GOAL, "octile", 8)
    assert abs(oct8.cost - (9 + 2 * SQRT2)) < 1e-9 and oct8.num_expansions == 24

    # 6. Tie-breaking on an empty 20x20 grid: larger g first is much faster.
    grid = np.zeros((20, 20), dtype=int)
    high = astar_grid(grid, (0, 0), (19, 19), "manhattan", 4, tie_break="high_g")
    low = astar_grid(grid, (0, 0), (19, 19), "manhattan", 4, tie_break="low_g")
    assert high.num_expansions == 39 and low.num_expansions == 400
    assert high.cost == low.cost == 38.0

    # 7. Space-time A*: the chapter's mini example forces one wait.
    grid, s, z, cons = spacetime_example()
    free = space_time_astar(grid, s, z)
    assert free.cost == 2.0 and free.path == [(0, 1), (1, 1), (2, 1)]
    assert free.num_expansions == 3
    res = space_time_astar(grid, s, z, cons)
    assert res.cost == 3.0 and res.path == [(0, 1), (0, 1), (1, 1), (2, 1)]
    assert res.num_expansions == 4 and path_respects(res.path, ReservationTable(cons))
    assert all(state != ((1, 1), 1) for state in res.closed)
    # an edge constraint forbids the move (0,1)->(1,1) at t = 1
    res = space_time_astar(grid, s, z, cons + [((0, 1), (1, 1), 1)])
    assert res.cost == 4.0 and path_respects(res.path, ReservationTable(cons + [((0, 1), (1, 1), 1)]))
    # goal-stay handling: the goal is blocked at t = 5, so arrive after 5
    res = space_time_astar(grid, s, z, [((2, 1), 5)])
    assert res.cost == 6.0 and path_respects(res.path, ReservationTable([((2, 1), 5)]))
    assert res.path == [(0, 1), (1, 1), (2, 1), (2, 1), (2, 1), (2, 2), (2, 1)]
    # unsolvable: start walled in by constraints -> finite failure
    res = space_time_astar(grid, s, z, [((0, 1), 1), ((0, 0), 1), ((0, 2), 1), ((1, 1), 1)])
    assert res.path is None and res.num_expansions == 1
    # goal permanently occupied by a parked agent -> failure
    table = ReservationTable()
    table.add_path([(2, 0), (2, 1)])
    assert space_time_astar(grid, s, z, table).path is None
    # horizon supplied by the caller
    assert space_time_astar(grid, s, z, cons, max_time=2).path is None
    assert space_time_astar(grid, s, z, cons, max_time=3).cost == 3.0

    # 8. Reservation table: two agents in a corridor with a passing bay.
    grid = np.ones((2, 5), dtype=int)
    grid[0, :] = 0                   # corridor y = 0, x = 0..4
    grid[1, 2] = 0                   # passing bay above x = 2
    table = ReservationTable()
    p1 = space_time_astar(grid, (0, 0), (4, 0), table).path
    table.add_path(p1)               # agent 1 moves first and parks at (4,0)
    assert p1 == [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)]
    # agent 2 wants to go the other way: it must hide in the bay and wait
    assert space_time_astar(grid, (3, 0), (0, 0)).cost == 3.0    # alone
    p2 = space_time_astar(grid, (3, 0), (0, 0), table).path
    assert p2 is not None and path_respects(p2, table)
    assert p2 == [(3, 0), (2, 0), (2, 1), (2, 1), (2, 0), (1, 0), (0, 0)]
    # from the far end there is no way past agent 1: prioritized planning
    # is incomplete (ch08); the search reports the failure in finite time
    assert space_time_astar(grid, (4, 0), (0, 0), table).path is None
    # MAPF-style constraints carry the agent index in front
    assert constraints_for_agent(1, [(1, (1, 1), 1), (2, (0, 0), 3),
                                     (1, (0, 1), (1, 1), 1)]) == [((1, 1), 1), ((0, 1), (1, 1), 1)]
    for t in range(max(len(p1), len(p2)) + 3):
        a = p1[min(t, len(p1) - 1)]
        b = p2[min(t, len(p2) - 1)]
        assert a != b                                    # no vertex conflict
        if t + 1 < max(len(p1), len(p2)):
            a2 = p1[min(t + 1, len(p1) - 1)]
            b2 = p2[min(t + 1, len(p2) - 1)]
            assert not (a == b2 and b == a2)             # no swap conflict

    # 9. Space-time cost without constraints equals the static distance.
    for _ in range(10):
        grid = _random_grid(rng, 8, 0.2)
        s, z = _random_pair(rng, grid, 4)
        res = space_time_astar(grid, s, z)
        assert res.cost == static_distances(grid, z, 4)[s]
        assert res.reopenings == 0
    print("ch04_astar: all self-tests passed")


if __name__ == "__main__":
    _self_test()
