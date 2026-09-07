"""Conflict-Based Search (CBS) for multi-agent path finding on 4-connected
grids -- Chapter 9 of "Multi-Agent Path Planning and Drone Collision
Avoidance".

The file is self-contained:

* ``Grid``            -- a rows x cols grid with obstacles, 4-connected moves,
                         backward BFS distances (an exact, consistent heuristic).
* ``low_level``       -- space-time A* for ONE agent under a set of vertex
                         constraints <v, t> and edge constraints <u, v, t>,
                         with the goal-occupied-later test and a finite horizon.
* ``first_conflict``  -- vertex / edge (swap) conflict detection between
                         time-indexed paths (agents stay at their goals).
* ``cbs``             -- the high level: best-first search on the sum of costs
                         over the binary constraint tree, optional ICBS-style
                         cardinal-conflict prioritisation and bypass.
* ``joint_optimal_cost`` -- Dijkstra on the joint state space (tiny instances
                         only), used by the self-test to certify optimality.

Cells are (x, y) with x the column and y the row, y growing upwards, as in
the figures of the book.  A path is a list of cells, one per time step; its
cost is len(path) - 1, the time of the final arrival at the goal, after
which the agent stays there for ever.

Run ``python3 ch09_cbs.py`` for the self-test (prints the worked example).
"""
from __future__ import annotations

import heapq
import itertools
import random
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Optional, Sequence, Tuple

Cell = Tuple[int, int]
Path = List[Cell]

# ----------------------------------------------------------------------
# Grid
# ----------------------------------------------------------------------


class Grid:
    """A 4-connected grid; '#' cells of the map are obstacles."""

    def __init__(self, cols: int, rows: int, obstacles: Sequence[Cell] = ()):
        self.cols, self.rows = cols, rows
        self.obstacles = frozenset(obstacles)

    @classmethod
    def from_map(cls, lines: Sequence[str]) -> "Grid":
        """Build a grid from text rows; the first row is the top (largest y)."""
        rows, cols = len(lines), len(lines[0])
        obs = [(x, rows - 1 - i) for i, line in enumerate(lines)
               for x, ch in enumerate(line) if ch == "#"]
        return cls(cols, rows, obs)

    def free(self, c: Cell) -> bool:
        x, y = c
        return 0 <= x < self.cols and 0 <= y < self.rows and c not in self.obstacles

    def neighbours(self, c: Cell) -> List[Cell]:
        x, y = c
        cand = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        return [n for n in cand if self.free(n)]

    def free_cells(self) -> List[Cell]:
        return [(x, y) for y in range(self.rows) for x in range(self.cols)
                if self.free((x, y))]

    def distances(self, goal: Cell) -> Dict[Cell, int]:
        """True shortest-path distances to ``goal`` (backward BFS)."""
        dist = {goal: 0}
        queue = deque([goal])
        while queue:
            c = queue.popleft()
            for n in self.neighbours(c):
                if n not in dist:
                    dist[n] = dist[c] + 1
                    queue.append(n)
        return dist


# ----------------------------------------------------------------------
# Constraints and the low level
# ----------------------------------------------------------------------


@dataclass(frozen=True)
class Constraints:
    """The constraints of one agent: vertex <v, t> and edge <u, v, t>."""

    vertex: FrozenSet[Tuple[Cell, int]] = frozenset()
    edge: FrozenSet[Tuple[Cell, Cell, int]] = frozenset()

    def add_vertex(self, v: Cell, t: int) -> "Constraints":
        return Constraints(self.vertex | {(v, t)}, self.edge)

    def add_edge(self, u: Cell, v: Cell, t: int) -> "Constraints":
        return Constraints(self.vertex, self.edge | {(u, v, t)})

    def last_time(self) -> int:
        """Largest time step touched by any constraint (-1 if none)."""
        times = [t for _, t in self.vertex] + [t + 1 for _, _, t in self.edge]
        return max(times, default=-1)


@dataclass
class Stats:
    expanded: int = 0        # high-level (CT) nodes expanded
    generated: int = 0       # CT nodes generated
    low_level_calls: int = 0
    low_level_expanded: int = 0
    bypasses: int = 0
    seconds: float = 0.0


def low_level(grid: Grid, start: Cell, goal: Cell, cons: Constraints,
              dist: Dict[Cell, int], stats: Optional[Stats] = None) -> Optional[Path]:
    """Space-time A* for one agent: shortest path from ``start`` to ``goal``
    that respects ``cons``; ``dist`` are true distances to the goal.

    The agent may finish at (goal, t) only if no vertex constraint touches
    the goal at a time >= t, because it stays at the goal for ever after.
    """
    if stats is not None:
        stats.low_level_calls += 1
    if start not in dist:
        return None
    goal_block = max((t for v, t in cons.vertex if v == goal), default=-1)
    horizon = cons.last_time() + 1 + max(dist.values())     # T_max = H + 1 + D
    counter = itertools.count()
    g = {(start, 0): 0}
    parent: Dict[Tuple[Cell, int], Tuple[Cell, int]] = {}
    open_heap = [(dist[start], 0, next(counter), (start, 0))]
    closed = set()
    while open_heap:
        f, neg_g, _, state = heapq.heappop(open_heap)
        if state in closed:
            continue
        closed.add(state)
        if stats is not None:
            stats.low_level_expanded += 1
        v, t = state
        if v == goal and t > goal_block:            # goal-occupied-later test
            path = [v]
            while state in parent:
                state = parent[state]
                path.append(state[0])
            return path[::-1]
        if t >= horizon:
            continue
        for w in grid.neighbours(v) + [v]:           # moves and the wait action
            nxt = (w, t + 1)
            if nxt in closed or nxt in cons.vertex or (v, w, t) in cons.edge:
                continue
            if t + 1 < g.get(nxt, float("inf")):
                g[nxt] = t + 1
                parent[nxt] = state
                heapq.heappush(open_heap, (t + 1 + dist[w], -(t + 1), next(counter), nxt))
    return None


# ----------------------------------------------------------------------
# Conflicts
# ----------------------------------------------------------------------


@dataclass(frozen=True)
class Conflict:
    """A vertex conflict <i, j, v, t> (u is None) or an edge conflict
    <i, j, u, v, t>: agent i moves u -> v and agent j moves v -> u at t."""

    i: int
    j: int
    v: Cell
    t: int
    u: Optional[Cell] = None

    def constraints(self) -> List[Tuple[int, Constraints]]:
        """The two children: (agent, constraint to add), without the parent's."""
        if self.u is None:
            return [(self.i, Constraints().add_vertex(self.v, self.t)),
                    (self.j, Constraints().add_vertex(self.v, self.t))]
        return [(self.i, Constraints().add_edge(self.u, self.v, self.t)),
                (self.j, Constraints().add_edge(self.v, self.u, self.t))]

    def __str__(self) -> str:
        if self.u is None:
            return "<a%d, a%d, %s, %d>" % (self.i + 1, self.j + 1, self.v, self.t)
        return "<a%d, a%d, %s->%s, %d>" % (self.i + 1, self.j + 1, self.u, self.v, self.t)


def at(path: Path, t: int) -> Cell:
    """Position at time t; after its last step the agent stays at the goal."""
    return path[t] if t < len(path) else path[-1]


def all_conflicts(paths: Sequence[Path]) -> List[Conflict]:
    """All vertex and edge conflicts, ordered by time, then by agent pair."""
    horizon = max(len(p) for p in paths)
    found = []
    for t in range(horizon):
        for i in range(len(paths)):
            for j in range(i + 1, len(paths)):
                pi, pj = at(paths[i], t), at(paths[j], t)
                if pi == pj:
                    found.append(Conflict(i, j, pi, t))
                if t + 1 < horizon:
                    qi, qj = at(paths[i], t + 1), at(paths[j], t + 1)
                    if pi == qj and qi == pj and pi != qi:
                        found.append(Conflict(i, j, qi, t, u=pi))
    return found


def first_conflict(paths: Sequence[Path]) -> Optional[Conflict]:
    found = all_conflicts(paths)
    return found[0] if found else None


def validate(paths: Sequence[Path], grid: Grid, starts: Sequence[Cell],
             goals: Sequence[Cell]) -> bool:
    """True if every path is legal on the grid and the plan is conflict-free."""
    for p, s, g in zip(paths, starts, goals):
        if p[0] != s or p[-1] != g or not all(grid.free(c) for c in p):
            return False
        if any(b != a and b not in grid.neighbours(a) for a, b in zip(p, p[1:])):
            return False
    return not all_conflicts(paths)


def sum_of_costs(paths: Sequence[Path]) -> int:
    return sum(len(p) - 1 for p in paths)


# ----------------------------------------------------------------------
# The high level
# ----------------------------------------------------------------------


@dataclass
class CTNode:
    constraints: Tuple[Constraints, ...]
    paths: List[Path]
    cost: int
    n_conflicts: int
    id: int = 0
    parent: Optional[int] = None
    added: str = ""          # the constraint added w.r.t. the parent (for traces)


@dataclass
class Result:
    paths: Optional[List[Path]]
    cost: Optional[int]
    stats: Stats
    trace: List[dict] = field(default_factory=list)   # one entry per expansion


def _make_child(node: CTNode, agent: int, extra: Constraints, grid: Grid,
                starts: Sequence[Cell], goals: Sequence[Cell],
                dists: Sequence[Dict[Cell, int]], stats: Stats) -> Optional[CTNode]:
    """Add ``extra`` to ``agent``'s constraints and replan only that agent."""
    old = node.constraints[agent]
    cons = Constraints(old.vertex | extra.vertex, old.edge | extra.edge)
    path = low_level(grid, starts[agent], goals[agent], cons, dists[agent], stats)
    if path is None:
        return None
    constraints = list(node.constraints)
    constraints[agent] = cons
    paths = list(node.paths)
    paths[agent] = path
    if extra.vertex:
        (v, t), = extra.vertex
        added = "<a%d, %s, %d>" % (agent + 1, v, t)
    else:
        (u, v, t), = extra.edge
        added = "<a%d, %s->%s, %d>" % (agent + 1, u, v, t)
    return CTNode(tuple(constraints), paths, sum_of_costs(paths),
                  len(all_conflicts(paths)), parent=node.id, added=added)


def _choose_conflict(node: CTNode, split: str, grid: Grid, starts, goals, dists,
                     stats: Stats) -> Tuple[Optional[Conflict], List[Optional[CTNode]]]:
    """Pick the conflict to split on.  ``split='first'`` takes the earliest
    conflict; ``split='cardinal'`` (ICBS) scans the conflicts in time order,
    generates the two children of each and returns the first cardinal one
    (both children cost more), else the first semi-cardinal, else the
    first conflict.  Children already generated are returned for reuse."""
    conflicts = all_conflicts(node.paths)
    if not conflicts:
        return None, []
    if split == "first":
        return conflicts[0], [None, None]
    best: Tuple[int, Conflict, List[Optional[CTNode]]] = (-1, conflicts[0], [None, None])
    for c in conflicts:
        kids = [_make_child(node, a, extra, grid, starts, goals, dists, stats)
                for a, extra in c.constraints()]
        rank = sum(1 for kid in kids if kid is None or kid.cost > node.cost)
        if rank > best[0]:
            best = (rank, c, kids)
        if rank == 2:
            break
    return best[1], best[2]


def cbs(grid: Grid, starts: Sequence[Cell], goals: Sequence[Cell],
        split: str = "first", bypass: bool = False,
        time_limit: Optional[float] = None, node_limit: Optional[int] = None,
        keep_trace: bool = False) -> Result:
    """Conflict-Based Search.  Returns paths, the sum of costs and statistics;
    ``paths`` is None if the instance has no solution or a limit was hit."""
    t0 = time.perf_counter()
    stats = Stats()
    dists = [grid.distances(g) for g in goals]
    counter = itertools.count()
    root_paths = [low_level(grid, s, g, Constraints(), d, stats)
                  for s, g, d in zip(starts, goals, dists)]
    if any(p is None for p in root_paths):
        return Result(None, None, stats)
    root = CTNode(tuple(Constraints() for _ in starts), root_paths,
                  sum_of_costs(root_paths), len(all_conflicts(root_paths)))
    root.id = next(counter)
    stats.generated = 1
    open_heap = [(root.cost, root.n_conflicts, root.id, root)]
    trace: List[dict] = []
    while open_heap:
        _, _, _, node = heapq.heappop(open_heap)
        stats.expanded += 1
        conflict, kids = _choose_conflict(node, split, grid, starts, goals, dists, stats)
        entry = {"id": node.id, "parent": node.parent, "added": node.added,
                 "costs": [len(p) - 1 for p in node.paths], "cost": node.cost,
                 "n_conflicts": node.n_conflicts,
                 "conflict": str(conflict) if conflict else "none",
                 "paths": [list(p) for p in node.paths], "children": [],
                 "bypass": False}
        if keep_trace:
            trace.append(entry)
        if conflict is None:
            stats.seconds = time.perf_counter() - t0
            return Result(node.paths, node.cost, stats, trace)
        if (time_limit is not None and time.perf_counter() - t0 > time_limit) or \
           (node_limit is not None and stats.expanded >= node_limit):
            break
        children = []
        for kid, (agent, extra) in zip(kids, conflict.constraints()):
            if kid is None and split == "first":
                kid = _make_child(node, agent, extra, grid, starts, goals, dists, stats)
            if kid is not None:
                children.append(kid)
        if bypass:
            better = [c for c in children
                      if c.cost == node.cost and c.n_conflicts < node.n_conflicts]
            if better:                    # adopt the child's paths, do not split
                node.paths, node.n_conflicts = better[0].paths, better[0].n_conflicts
                node.added += " bypass: " + better[0].added
                entry["bypass"] = True
                stats.bypasses += 1
                heapq.heappush(open_heap, (node.cost, node.n_conflicts, node.id, node))
                continue
        for kid in children:
            kid.id = next(counter)
            stats.generated += 1
            entry["children"].append({"id": kid.id, "added": kid.added, "cost": kid.cost,
                                      "costs": [len(p) - 1 for p in kid.paths],
                                      "n_conflicts": kid.n_conflicts})
            heapq.heappush(open_heap, (kid.cost, kid.n_conflicts, kid.id, kid))
    stats.seconds = time.perf_counter() - t0
    return Result(None, None, stats, trace)


# ----------------------------------------------------------------------
# Brute force on the joint state space (self-test only)
# ----------------------------------------------------------------------


def joint_optimal_cost(grid: Grid, starts: Sequence[Cell],
                       goals: Sequence[Cell]) -> Optional[int]:
    """Optimal sum of costs by Dijkstra over joint states (positions,
    finished flags).  An unfinished agent pays 1 per step; an agent at its
    goal may 'finish' for free and then never moves again.  Tiny instances
    only: the state space has |V|^k 2^k states."""
    k = len(starts)
    start = (tuple(starts), (False,) * k)
    best = {start: 0}
    heap = [(0, 0, start)]
    tie = itertools.count()
    while heap:
        cost, _, state = heapq.heappop(heap)
        if cost > best.get(state, float("inf")):
            continue
        pos, done = state
        if all(done):
            return cost
        options = []
        for i in range(k):
            if done[i]:
                options.append([(pos[i], True, 0)])
            else:
                opts = [(w, False, 1) for w in grid.neighbours(pos[i]) + [pos[i]]]
                if pos[i] == goals[i]:
                    opts.append((pos[i], True, 0))
                options.append(opts)
        for combo in itertools.product(*options):
            new_pos = tuple(c[0] for c in combo)
            if len(set(new_pos)) < k:
                continue
            if any(new_pos[i] == pos[j] and new_pos[j] == pos[i] and pos[i] != pos[j]
                   for i in range(k) for j in range(i + 1, k)):
                continue
            new_state = (new_pos, tuple(c[1] for c in combo))
            new_cost = cost + sum(c[2] for c in combo)
            if new_cost < best.get(new_state, float("inf")):
                best[new_state] = new_cost
                heapq.heappush(heap, (new_cost, next(tie), new_state))
    return None


# ----------------------------------------------------------------------
# Instances
# ----------------------------------------------------------------------


def random_instance(cols: int, rows: int, k: int, density: float,
                    rng: random.Random) -> Tuple[Grid, List[Cell], List[Cell]]:
    """Random grid with random distinct starts and goals, redrawn until
    every agent can reach its goal."""
    while True:
        cells = [(x, y) for y in range(rows) for x in range(cols)]
        obs = [c for c in cells if rng.random() < density]
        grid = Grid(cols, rows, obs)
        free = grid.free_cells()
        if len(free) < 2 * k:
            continue
        starts = rng.sample(free, k)
        goals = rng.sample(free, k)
        if all(s in grid.distances(g) for s, g in zip(starts, goals)):
            return grid, starts, goals


# The worked example of the chapter (Section 9.5).
EXAMPLE_MAP = [
    "..#..",
    ".....",
    "..#..",
]
EXAMPLE_STARTS = [(0, 1), (2, 2), (4, 2)]
EXAMPLE_GOALS = [(4, 1), (2, 0), (0, 2)]


def worked_example(split: str = "first", bypass: bool = False) -> Result:
    grid = Grid.from_map(EXAMPLE_MAP)
    return cbs(grid, EXAMPLE_STARTS, EXAMPLE_GOALS, split=split, bypass=bypass,
               keep_trace=True)


def print_trace(result: Result) -> None:
    for e in result.trace:
        print("N%d (parent %s, added %s): costs %s, total %d, conflict %s"
              % (e["id"], "-" if e["parent"] is None else "N%d" % e["parent"],
                 e["added"] or "none", e["costs"], e["cost"], e["conflict"]))
        for i, p in enumerate(e["paths"]):
            print("   a%d: %s" % (i + 1, " ".join("(%d,%d)" % c for c in p)))
        for c in e["children"]:
            print("   -> N%d added %s: costs %s, total %d, %d conflict(s)"
                  % (c["id"], c["added"], c["costs"], c["cost"], c["n_conflicts"]))
        if e["bypass"]:
            print("   bypass: paths replaced, node re-inserted")


# ----------------------------------------------------------------------
# Self-test
# ----------------------------------------------------------------------


def _test_low_level_goal_stay() -> None:
    grid = Grid(4, 1)
    dist = grid.distances((3, 0))
    cons = Constraints().add_vertex((3, 0), 5)       # goal occupied at t = 5
    path = low_level(grid, (0, 0), (3, 0), cons, dist)
    assert path is not None and len(path) - 1 == 6 and path[-1] == (3, 0)
    assert all(not (c == (3, 0) and t == 5) for t, c in enumerate(path))
    cons = Constraints().add_edge((1, 0), (2, 0), 1)  # cannot cross 1->2 at t = 1
    path = low_level(grid, (0, 0), (3, 0), cons, dist)
    assert len(path) - 1 == 4 and path[:3] != [(0, 0), (1, 0), (2, 0)]


def _test_worked_example() -> None:
    res = worked_example()
    assert res.paths is not None and res.cost == 12
    ids = [e["id"] for e in res.trace]
    assert ids == [0, 1, 2, 3, 5], ids
    assert [e["cost"] for e in res.trace] == [10, 11, 11, 12, 12]
    assert res.stats.expanded == 5 and res.stats.generated == 7
    grid = Grid.from_map(EXAMPLE_MAP)
    assert validate(res.paths, grid, EXAMPLE_STARTS, EXAMPLE_GOALS)
    assert joint_optimal_cost(grid, EXAMPLE_STARTS, EXAMPLE_GOALS) == 12
    res2 = worked_example(split="cardinal", bypass=True)
    assert res2.cost == 12 and res2.stats.expanded <= res.stats.expanded


def _test_random_against_brute_force() -> None:
    rng = random.Random(9)
    n_checked = 0
    for k, cols, rows, n in ((2, 4, 4, 30), (3, 4, 3, 12)):
        for _ in range(n):
            grid, starts, goals = random_instance(cols, rows, k, 0.2, rng)
            opt = joint_optimal_cost(grid, starts, goals)
            for split, bypass in (("first", False), ("cardinal", False), ("cardinal", True)):
                res = cbs(grid, starts, goals, split=split, bypass=bypass, node_limit=20000)
                if opt is None:
                    assert res.paths is None
                    continue
                assert res.paths is not None, (starts, goals, split)
                assert validate(res.paths, grid, starts, goals)
                assert res.cost == opt, (res.cost, opt, starts, goals, split)
            n_checked += 1
    print("random instances certified against the joint-space optimum:", n_checked)


def _test_rectangle_symmetry() -> None:
    """Every pair of shortest paths of the two agents of the symmetry figure
    conflicts (rectangle symmetry, Li et al. 2019)."""
    grid = Grid(5, 5)
    s1, g1, s2, g2 = (0, 2), (4, 3), (1, 1), (3, 4)

    def shortest_paths(s, g):
        d = grid.distances(g)
        out = []

        def rec(c, path):
            if c == g:
                out.append(path)
                return
            for n in grid.neighbours(c):
                if d[n] == d[c] - 1:
                    rec(n, path + [n])
        rec(s, [s])
        return out

    p1s, p2s = shortest_paths(s1, g1), shortest_paths(s2, g2)
    assert len(p1s) == 5 and len(p2s) == 10
    assert all(all_conflicts([p, q]) for p in p1s for q in p2s)


if __name__ == "__main__":
    t_start = time.perf_counter()
    _test_low_level_goal_stay()
    _test_worked_example()
    _test_rectangle_symmetry()
    _test_random_against_brute_force()
    print("--- worked example (split on the first conflict) ---")
    res = worked_example()
    print_trace(res)
    print("expanded %d CT nodes, generated %d, low-level calls %d, cost %d"
          % (res.stats.expanded, res.stats.generated, res.stats.low_level_calls, res.cost))
    res = worked_example(split="cardinal", bypass=True)
    print("cardinal-first + bypass: expanded %d, generated %d, bypasses %d, cost %d"
          % (res.stats.expanded, res.stats.generated, res.stats.bypasses, res.cost))
    print("all tests passed in %.1f s" % (time.perf_counter() - t_start))
