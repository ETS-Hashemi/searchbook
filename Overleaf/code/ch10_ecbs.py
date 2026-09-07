"""Chapter 10 -- Bounded-Suboptimal Search: ECBS.

Focal search (the A*-epsilon of Pearl and Kim) at both levels of
conflict-based search:

* a low-level space-time A* whose FOCAL list prefers paths with fewer
  conflicts and that returns, next to the path, a lower bound on the
  optimal constrained cost of the agent (the smallest f-value in OPEN);
* the ECBS high level, whose OPEN is ordered by the sum of the per-agent
  lower bounds and whose FOCAL list holds the constraint-tree nodes whose
  cost is within the factor w of the smallest lower bound, ordered by the
  number of conflicts;
* a CBS baseline (optimal) built from the same parts with w = 1.

The instance format follows chapter 7: grids are lists of strings ('.'
free, '@' or 'T' blocked), cells are (row, col) pairs with row 0 at the
top, paths are lists of cells indexed by time, and an agent that has
reached its goal stays there for ever (stay-at-target).  The file is
self-contained so that it can be dropped into any MAPF code base.

Run this file to execute the self-test:  python3 ch10_ecbs.py
"""
from __future__ import annotations

import bisect
import heapq
import itertools
import random
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Optional, Sequence, Tuple

Cell = Tuple[int, int]      # (row, col); row 0 is the top row of the map
Path = List[Cell]           # path[t] is the cell occupied at time step t

FREE_CHARS = frozenset(".GS")
MOVES = ((-1, 0), (1, 0), (0, -1), (0, 1))   # up, down, left, right
INF = float("inf")


# ---------------------------------------------------------------------
# Instances, paths, costs
# ---------------------------------------------------------------------
@dataclass
class Instance:
    """A grid map plus k agents with distinct starts and distinct goals."""

    grid: List[str]
    starts: List[Cell]
    goals: List[Cell]
    name: str = "instance"
    _dist: Dict[Cell, Dict[Cell, int]] = field(default_factory=dict,
                                              repr=False, compare=False)

    @property
    def rows(self) -> int:
        return len(self.grid)

    @property
    def cols(self) -> int:
        return len(self.grid[0]) if self.grid else 0

    @property
    def k(self) -> int:
        return len(self.starts)

    def is_free(self, cell: Cell) -> bool:
        r, c = cell
        return (0 <= r < self.rows and 0 <= c < self.cols
                and self.grid[r][c] in FREE_CHARS)

    def neighbors(self, cell: Cell) -> List[Cell]:
        r, c = cell
        return [(r + dr, c + dc) for dr, dc in MOVES
                if self.is_free((r + dr, c + dc))]

    def free_cells(self) -> List[Cell]:
        return [(r, c) for r in range(self.rows) for c in range(self.cols)
                if self.is_free((r, c))]

    def check(self) -> None:
        """Raise ValueError unless this is a classical MAPF instance."""
        if len(self.starts) != len(self.goals):
            raise ValueError("starts and goals differ in length")
        if len(set(self.starts)) != self.k or len(set(self.goals)) != self.k:
            raise ValueError("starts and goals must be distinct")
        for cell in self.starts + self.goals:
            if not self.is_free(cell):
                raise ValueError(f"cell {cell} is blocked or outside the map")

    def distances_to(self, goal: Cell) -> Dict[Cell, int]:
        """Exact grid distance of every reachable cell to goal (cached BFS).

        This is the heuristic of the low level: it ignores the other
        agents and the constraints, so it never overestimates, and it is
        consistent because it is a true distance.
        """
        if goal not in self._dist:
            dist = {goal: 0}
            queue = deque([goal])
            while queue:
                cell = queue.popleft()
                for nxt in self.neighbors(cell):
                    if nxt not in dist:
                        dist[nxt] = dist[cell] + 1
                        queue.append(nxt)
            self._dist[goal] = dist
        return self._dist[goal]


def position(path: Path, t: int) -> Cell:
    """Cell of an agent at time t; after its last step it stays at the goal."""
    return path[t] if t < len(path) else path[-1]


def path_cost(path: Path) -> int:
    """Time of the final arrival at the last cell (trailing waits are free)."""
    goal = path[-1]
    t = len(path) - 1
    while t > 0 and path[t - 1] == goal:
        t -= 1
    return t


def sum_of_costs(paths: Sequence[Path]) -> int:
    return sum(path_cost(p) for p in paths)


def makespan(paths: Sequence[Path]) -> int:
    return max(path_cost(p) for p in paths)


def horizon(paths: Sequence[Path]) -> int:
    return max(len(p) for p in paths) - 1


# ---------------------------------------------------------------------
# Conflicts and constraints
# ---------------------------------------------------------------------
@dataclass(frozen=True)
class Conflict:
    """A vertex conflict <i, j, v, t> or a swapping conflict <i, j, u, v, t>.

    For a swap, agent i moves u -> v and agent j moves v -> u between
    time steps t and t + 1.  Always i < j.
    """

    kind: str
    i: int
    j: int
    t: int
    cells: Tuple[Cell, ...]

    def __str__(self) -> str:
        if self.kind == "vertex":
            return f"<{self.i},{self.j},{self.cells[0]},t={self.t}>"
        return f"<{self.i},{self.j},{self.cells[0]}->{self.cells[1]},t={self.t}>"


def _pair_conflicts(p: Path, q: Path, i: int, j: int) -> List[Conflict]:
    """Vertex and swapping conflicts between two paths (stay-at-target)."""
    found = []
    T = max(len(p), len(q)) - 1
    for t in range(T + 1):
        u, v = position(p, t), position(q, t)
        if u == v:
            found.append(Conflict("vertex", i, j, t, (u,)))
        if t < T:
            u2, v2 = position(p, t + 1), position(q, t + 1)
            if u != u2 and u == v2 and u2 == v:
                found.append(Conflict("swap", i, j, t, (u, u2)))
    return found


def all_conflicts(paths: Sequence[Path]) -> List[Conflict]:
    """Every conflict of a plan, sorted by time, vertex before swap, pair."""
    found: List[Conflict] = []
    for i in range(len(paths)):
        for j in range(i + 1, len(paths)):
            found += _pair_conflicts(paths[i], paths[j], i, j)
    found.sort(key=lambda c: (c.t, c.kind != "vertex", c.i, c.j))
    return found


def count_conflicts(paths: Sequence[Path]) -> int:
    """h_c(N): the number of conflicts in the solution of a CT node."""
    return len(all_conflicts(paths))


def conflicts_of_agent(i: int, paths: Sequence[Path]) -> int:
    """Number of conflicts between path i and the paths of the other agents."""
    return sum(len(_pair_conflicts(paths[i], paths[j], min(i, j), max(i, j)))
               for j in range(len(paths)) if j != i)


def first_conflict(paths: Sequence[Path]) -> Optional[Conflict]:
    """The earliest conflict (the one CBS and ECBS split on), or None."""
    found = all_conflicts(paths)
    return found[0] if found else None


@dataclass(frozen=True)
class Constraint:
    """<agent, v, t> (vertex) or <agent, u, v, t> (edge, move u -> v at t)."""

    agent: int
    t: int
    cells: Tuple[Cell, ...]

    @property
    def kind(self) -> str:
        return "vertex" if len(self.cells) == 1 else "edge"

    def __str__(self) -> str:
        if self.kind == "vertex":
            return f"<a{self.agent},{self.cells[0]},t={self.t}>"
        return f"<a{self.agent},{self.cells[0]}->{self.cells[1]},t={self.t}>"


def split_conflict(conflict: Conflict) -> Tuple[Constraint, Constraint]:
    """The two constraints that resolve a conflict, one per agent."""
    if conflict.kind == "vertex":
        (v,) = conflict.cells
        return (Constraint(conflict.i, conflict.t, (v,)),
                Constraint(conflict.j, conflict.t, (v,)))
    u, v = conflict.cells
    return (Constraint(conflict.i, conflict.t, (u, v)),
            Constraint(conflict.j, conflict.t, (v, u)))


class OtherPaths:
    """Occupancy of the other agents' paths, for counting conflicts.

    vertex_hits(v, t)   number of other agents at v at time t
    swap_hits(u, v, t)  number of other agents moving v -> u while we move u -> v
    future_hits(v, t)   number of visits of other agents to v after time t
                        (the conflicts of an agent parked at v from time t on)
    """

    def __init__(self, paths: Sequence[Path]):
        self.T = max((len(p) - 1 for p in paths), default=-1)
        self.at: Dict[Tuple[Cell, int], int] = {}
        self.move: Dict[Tuple[Cell, Cell, int], int] = {}
        self.parked: Dict[Cell, int] = {}
        self.visits: Dict[Cell, List[int]] = {}
        for p in paths:
            for t in range(self.T + 1):
                v = position(p, t)
                self.at[(v, t)] = self.at.get((v, t), 0) + 1
                self.visits.setdefault(v, []).append(t)
                if t < self.T:
                    v2 = position(p, t + 1)
                    if v2 != v:
                        self.move[(v, v2, t)] = self.move.get((v, v2, t), 0) + 1
            self.parked[p[-1]] = self.parked.get(p[-1], 0) + 1
        for times in self.visits.values():
            times.sort()

    def vertex_hits(self, v: Cell, t: int) -> int:
        if t <= self.T:
            return self.at.get((v, t), 0)
        return self.parked.get(v, 0)

    def swap_hits(self, u: Cell, v: Cell, t: int) -> int:
        return self.move.get((v, u, t), 0) if t < self.T else 0

    def future_hits(self, v: Cell, t: int) -> int:
        times = self.visits.get(v, ())
        return len(times) - bisect.bisect_right(times, t)


# ---------------------------------------------------------------------
# Low level: focal space-time A* that returns a path and a lower bound
# ---------------------------------------------------------------------
@dataclass
class LowLevelResult:
    path: Path
    lower_bound: int      # smallest f in OPEN when the goal was popped
    conflicts: int        # conflicts of the path with the other agents
    expansions: int


def _reconstruct(parent: Dict, state) -> Path:
    path = []
    while state is not None:
        path.append(state[0])
        state = parent[state]
    return path[::-1]


def _snapshot(trace, state, conflicts, f, f_min, focal, open_heap, closed):
    """Record one low-level expansion with the live FOCAL and OPEN entries."""
    live = [(c, ff, st) for c, ff, _, _, st in focal if st not in closed]
    rest = [(ff, st) for ff, _, _, st in open_heap
            if st not in closed and st != state]
    trace.append({"state": state, "nc": conflicts, "f": f, "f_min": f_min,
                  "focal": sorted(live), "open": sorted(rest)})


def focal_space_time_astar(inst: Instance, agent: int,
                           constraints: FrozenSet[Constraint],
                           others: OtherPaths, w: float = 1.0,
                           max_time: Optional[int] = None,
                           trace: Optional[List[dict]] = None
                           ) -> Optional[LowLevelResult]:
    """Focal search over states (cell, t) for one agent.

    OPEN is ordered by f = t + h (h = exact grid distance, so f never
    overestimates); FOCAL holds the open states with f <= w * f_min and is
    ordered by the number of conflicts of the partial path with the other
    agents' paths (ties: smaller f, then larger t).  The search stops when
    it pops a goal state (cell = goal and t later than every vertex
    constraint on the goal) and returns the path together with f_min,
    a lower bound on the optimal cost under the constraints.  With w = 1
    it is A* that breaks ties towards fewer conflicts.
    """
    start, goal = inst.starts[agent], inst.goals[agent]
    h = inst.distances_to(goal)
    if start not in h:
        return None
    vcons = {(c.cells[0], c.t) for c in constraints if c.kind == "vertex"}
    econs = {(c.cells[0], c.cells[1], c.t) for c in constraints if c.kind == "edge"}
    t_goal = max((t for v, t in vcons if v == goal), default=-1)
    if max_time is None:                       # horizon w * (H + 1 + D)
        last_t = max((c.t for c in constraints), default=-1)
        max_time = int(w * (last_t + 1 + max(h.values())))

    counter = itertools.count()
    s0 = (start, 0)
    nc0 = others.vertex_hits(start, 0)         # conflicts along the path
    if start == goal and t_goal < 0:           # already parked at the goal
        nc0 += others.future_hits(goal, 0)
    nc = {s0: nc0}
    parent: Dict = {s0: None}
    closed = set()
    in_focal = {s0}
    f_min = h[start]
    open_heap = [(f_min, 0, next(counter), s0)]           # (f, -t, tie, state)
    focal = [(nc[s0], f_min, 0, 0, s0)]                    # (nc, f, -t, tie, state)
    expansions = 0
    while True:
        while open_heap and open_heap[0][3] in closed:     # lazy deletion
            heapq.heappop(open_heap)
        if not open_heap:
            return None
        if open_heap[0][0] > f_min:                        # f_min rose:
            f_min = open_heap[0][0]                        # admit new states
            for f, neg_t, tie, st in open_heap:            # to FOCAL
                if f <= w * f_min and st not in in_focal and st not in closed:
                    heapq.heappush(focal, (nc[st], f, neg_t, tie, st))
                    in_focal.add(st)
        conflicts, f, _, _, state = heapq.heappop(focal)
        if trace is not None:                              # for trace tables
            _snapshot(trace, state, conflicts, f, f_min, focal, open_heap, closed)
        closed.add(state)
        cell, t = state
        if cell == goal and t > t_goal:
            return LowLevelResult(_reconstruct(parent, state), f_min,
                                  conflicts, expansions)
        expansions += 1
        t2 = t + 1
        if t2 > max_time:
            continue
        for v in [cell] + inst.neighbors(cell):
            if (v, t2) in vcons or (v != cell and (cell, v, t) in econs):
                continue
            st2 = (v, t2)
            if st2 in parent:                  # same g = t2: first path wins
                continue
            parent[st2] = state
            c = conflicts + others.vertex_hits(v, t2)
            if v != cell:
                c += others.swap_hits(cell, v, t)
            if v == goal and t2 > t_goal:      # parked at the goal from t2 on
                c += others.future_hits(goal, t2)
            nc[st2] = c
            f2 = t2 + h[v]
            tie = next(counter)
            heapq.heappush(open_heap, (f2, -t2, tie, st2))
            if f2 <= w * f_min:
                heapq.heappush(focal, (c, f2, -t2, tie, st2))
                in_focal.add(st2)


# ---------------------------------------------------------------------
# Constraint-tree nodes and the two high levels
# ---------------------------------------------------------------------
@dataclass
class CTNode:
    constraints: Tuple[FrozenSet[Constraint], ...]   # one set per agent
    paths: List[Path]
    lbs: List[int]                                   # per-agent lower bounds
    cost: int = 0                                    # sum of costs
    lb: int = 0                                      # sum of lbs
    conflicts: int = 0                               # h_c(N)
    id: int = 0
    parent: Optional[int] = None
    new_constraint: Optional[Constraint] = None


@dataclass
class Result:
    paths: Optional[List[Path]]
    cost: Optional[int]
    lower_bound: int
    w: float
    ct_expanded: int
    ct_generated: int
    low_level_expansions: int
    runtime: float
    status: str                   # solved, node_limit, time_limit, unsolvable
    trace: List[dict] = field(default_factory=list)

    @property
    def solved(self) -> bool:
        return self.status == "solved"


class _Stats:
    def __init__(self):
        self.low_level_expansions = 0
        self.generated = 0
        self.ids = itertools.count()


def _plan_root(inst: Instance, w: float, stats: _Stats) -> Optional[CTNode]:
    """Root of the constraint tree: plan the agents one after another.

    Each agent is planned with the focal low level against the agents
    planned before it, so that cheap conflict avoidance already happens
    at the root; agent i still ignores agents i+1, ..., k.
    """
    paths: List[Path] = []
    lbs: List[int] = []
    for i in range(inst.k):
        res = focal_space_time_astar(inst, i, frozenset(), OtherPaths(paths), w)
        if res is None:
            return None
        stats.low_level_expansions += res.expansions
        paths.append(res.path)
        lbs.append(res.lower_bound)
    stats.generated += 1
    return CTNode(tuple(frozenset() for _ in range(inst.k)), paths, lbs,
                  sum_of_costs(paths), sum(lbs), count_conflicts(paths),
                  next(stats.ids))


def _child(inst: Instance, parent: CTNode, con: Constraint, w: float,
           stats: _Stats) -> Optional[CTNode]:
    """Copy the parent, add one constraint and replan the constrained agent.

    The lower bound of the replanned agent is the larger of the parent's
    bound (still valid: more constraints cannot make the optimum cheaper)
    and the f_min returned by the low level.
    """
    a = con.agent
    cons = list(parent.constraints)
    cons[a] = cons[a] | {con}
    others = OtherPaths([p for i, p in enumerate(parent.paths) if i != a])
    res = focal_space_time_astar(inst, a, cons[a], others, w)
    if res is None:
        return None
    stats.low_level_expansions += res.expansions
    stats.generated += 1
    paths = list(parent.paths)
    paths[a] = res.path
    lbs = list(parent.lbs)
    lbs[a] = max(lbs[a], res.lower_bound)
    return CTNode(tuple(cons), paths, lbs, sum_of_costs(paths), sum(lbs),
                  count_conflicts(paths), next(stats.ids), parent.id, con)


def _record(trace: Optional[List[dict]], node: CTNode, lb_min: int,
            conflict: Optional[Conflict]) -> None:
    if trace is not None:
        trace.append({"id": node.id, "parent": node.parent,
                      "constraint": node.new_constraint, "cost": node.cost,
                      "lb": node.lb, "lbs": list(node.lbs),
                      "conflicts": node.conflicts, "lb_min": lb_min,
                      "split": conflict, "paths": [list(p) for p in node.paths],
                      "children": []})


def _record_child(trace: Optional[List[dict]], con: Constraint,
                  child: Optional[CTNode], admitted: bool) -> None:
    if trace is not None:
        info = {"constraint": con, "id": None, "cost": None, "lb": None,
                "lbs": None, "conflicts": None, "in_focal": admitted}
        if child is not None:
            info.update(id=child.id, cost=child.cost, lb=child.lb,
                        lbs=list(child.lbs), conflicts=child.conflicts)
        trace[-1].setdefault("children", []).append(info)


def ecbs(inst: Instance, w: float = 1.5, node_limit: int = 10 ** 6,
         time_limit: float = INF, keep_trace: bool = False) -> Result:
    """ECBS(w): focal search over the constraint tree.

    OPEN is ordered by LB(N) = sum of the per-agent lower bounds, FOCAL
    holds the open nodes with cost(N) <= w * LB, where LB is the smallest
    LB(N) in OPEN, and is ordered by the number of conflicts (ties: smaller
    cost, then older node).  The returned solution costs at most w * C*.
    """
    t0 = time.perf_counter()
    stats = _Stats()
    trace: Optional[List[dict]] = [] if keep_trace else None
    root = _plan_root(inst, w, stats)
    if root is None:
        return Result(None, None, 0, w, 0, 0, stats.low_level_expansions,
                      time.perf_counter() - t0, "unsolvable")
    open_heap = [(root.lb, root.id, root)]                 # ordered by LB(N)
    focal = [(root.conflicts, root.cost, root.id, root)]   # ordered by h_c(N)
    in_focal = {root.id}
    expanded = set()
    lb_min = root.lb

    def done(status, node=None):
        return Result(node.paths if node else None, node.cost if node else None,
                      lb_min, w, len(expanded), stats.generated,
                      stats.low_level_expansions, time.perf_counter() - t0,
                      status, trace or [])

    while open_heap:
        while open_heap and open_heap[0][1] in expanded:   # lazy deletion
            heapq.heappop(open_heap)
        if not open_heap:
            break
        if open_heap[0][0] > lb_min:                       # LB rose: admit
            lb_min = open_heap[0][0]                       # more nodes to FOCAL
            for lb, nid, n in open_heap:
                if n.cost <= w * lb_min and nid not in in_focal and nid not in expanded:
                    heapq.heappush(focal, (n.conflicts, n.cost, nid, n))
                    in_focal.add(nid)
        _, _, _, node = heapq.heappop(focal)
        expanded.add(node.id)
        conflict = first_conflict(node.paths) if node.conflicts else None
        _record(trace, node, lb_min, conflict)
        if conflict is None:
            return done("solved", node)                    # cost <= w * lb_min
        if len(expanded) >= node_limit:
            return done("node_limit")
        if time.perf_counter() - t0 > time_limit:
            return done("time_limit")
        for con in split_conflict(conflict):
            child = _child(inst, node, con, w, stats)
            if child is None:                              # no path: prune
                _record_child(trace, con, None, False)
                continue
            heapq.heappush(open_heap, (child.lb, child.id, child))
            admitted = child.cost <= w * lb_min
            if admitted:
                heapq.heappush(focal, (child.conflicts, child.cost, child.id, child))
                in_focal.add(child.id)
            _record_child(trace, con, child, admitted)
    return done("unsolvable")


def cbs(inst: Instance, node_limit: int = 10 ** 6, time_limit: float = INF,
        keep_trace: bool = False) -> Result:
    """Optimal CBS: best-first on the cost of the CT nodes, low level w = 1.

    Ties in cost are broken towards fewer conflicts, then towards the
    older node.  The low level is the focal search with w = 1, that is,
    A* that prefers, among equally short paths, one with fewer conflicts.
    """
    t0 = time.perf_counter()
    stats = _Stats()
    trace: Optional[List[dict]] = [] if keep_trace else None
    root = _plan_root(inst, 1.0, stats)
    if root is None:
        return Result(None, None, 0, 1.0, 0, 0, stats.low_level_expansions,
                      time.perf_counter() - t0, "unsolvable")
    open_heap = [(root.cost, root.conflicts, root.id, root)]
    expanded = 0
    while open_heap:
        cost, _, _, node = heapq.heappop(open_heap)
        expanded += 1
        conflict = first_conflict(node.paths) if node.conflicts else None
        _record(trace, node, cost, conflict)
        if conflict is None:
            return Result(node.paths, node.cost, node.cost, 1.0, expanded,
                          stats.generated, stats.low_level_expansions,
                          time.perf_counter() - t0, "solved", trace or [])
        if expanded >= node_limit or time.perf_counter() - t0 > time_limit:
            status = "node_limit" if expanded >= node_limit else "time_limit"
            return Result(None, None, cost, 1.0, expanded, stats.generated,
                          stats.low_level_expansions, time.perf_counter() - t0,
                          status, trace or [])
        for con in split_conflict(conflict):
            child = _child(inst, node, con, 1.0, stats)
            _record_child(trace, con, child, child is not None)
            if child is not None:
                heapq.heappush(open_heap, (child.cost, child.conflicts,
                                           child.id, child))
    return Result(None, None, 0, 1.0, expanded, stats.generated,
                  stats.low_level_expansions, time.perf_counter() - t0,
                  "unsolvable", trace or [])


# ---------------------------------------------------------------------
# Validation and instances
# ---------------------------------------------------------------------
def validate(inst: Instance, paths: Sequence[Path]) -> List[str]:
    """Problems of a plan; an empty list means it is a valid solution."""
    problems = []
    if len(paths) != inst.k:
        return [f"{len(paths)} paths for {inst.k} agents"]
    for i, path in enumerate(paths):
        if not path or path[0] != inst.starts[i]:
            problems.append(f"agent {i}: does not start at {inst.starts[i]}")
        if not path or path[-1] != inst.goals[i]:
            problems.append(f"agent {i}: does not end at {inst.goals[i]}")
        for t, cell in enumerate(path):
            if not inst.is_free(cell):
                problems.append(f"agent {i}: cell {cell} at t={t} is blocked")
            if t > 0 and cell != path[t - 1] and cell not in inst.neighbors(path[t - 1]):
                problems.append(f"agent {i}: illegal move {path[t - 1]} -> {cell} at t={t}")
    for c in all_conflicts(paths):
        problems.append(f"conflict {c}")
    return problems


def respects(path: Path, constraints: FrozenSet[Constraint]) -> bool:
    """Does the path (with stay-at-target) satisfy every constraint?"""
    T = len(path) - 1
    for c in constraints:
        if c.kind == "vertex":
            if position(path, c.t) == c.cells[0]:
                return False
        elif c.t < T and (path[c.t], path[c.t + 1]) == c.cells:
            return False
    return True


def random_instance(rows: int, cols: int, k: int, rng: random.Random,
                    obstacle_density: float = 0.0) -> Instance:
    """Random obstacles, then k distinct starts and k distinct goals."""
    while True:
        grid = ["".join("@" if rng.random() < obstacle_density else "."
                        for _ in range(cols)) for _ in range(rows)]
        inst = Instance(grid, [], [], f"random-{rows}x{cols}-{k}")
        free = inst.free_cells()
        if len(free) < k:
            continue
        starts = rng.sample(free, k)
        goals = rng.sample(free, k)
        inst = Instance(grid, starts, goals, inst.name)
        if all(s in inst.distances_to(g) for s, g in zip(starts, goals)):
            return inst


def worked_example() -> Instance:
    """The 4 x 4 instance of the worked example of the chapter.

    Agent 0: (2,2) -> (1,1), agent 1: (2,3) -> (1,0), agent 2: (3,0) -> (1,3);
    the cell (3,2) is blocked.  CBS needs 7 expansions for the optimal cost
    12, ECBS(1.2) stops after 2 expansions with cost 13.
    """
    grid = ["....",
            "....",
            "....",
            "..@."]
    starts = [(2, 2), (2, 3), (3, 0)]
    goals = [(1, 1), (1, 0), (1, 3)]
    inst = Instance(grid, starts, goals, "worked-example")
    inst.check()
    return inst


def low_level_example() -> Tuple[Instance, List[Path]]:
    """A 3 x 4 grid for the low-level example: agent 0 must cross the
    column that agent 1 walks down.  Returns the instance and the fixed
    path of agent 1."""
    inst = Instance(["....", "....", "...."], [(1, 0), (0, 1)],
                    [(1, 3), (2, 1)], "low-level-example")
    inst.check()
    return inst, [[(0, 1), (1, 1), (2, 1)]]


def print_plan(paths: Sequence[Path]) -> None:
    T = horizon(paths)
    print("t    " + "".join(f"{t:>8}" for t in range(T + 1)))
    for i, path in enumerate(paths):
        cells = "".join(f"{str(position(path, t)):>8}" for t in range(T + 1))
        print(f"a{i}   " + cells + f"   cost {path_cost(path)}")


def print_trace(res: Result) -> None:
    """One line per expanded CT node: id, parent, constraint, cost, LB, ..."""
    print(f"  {'id':>3} {'par':>3} {'new constraint':<28} {'cost':>4} "
          f"{'LB':>3} {'lbs':<12} {'h_c':>3} {'LBmin':>5}  split")
    for row in res.trace:
        con = str(row["constraint"]) if row["constraint"] else "-"
        par = row["parent"] if row["parent"] is not None else "-"
        split = str(row["split"]) if row["split"] else "none (solution)"
        print(f"  {row['id']:>3} {par:>3} {con:<28} {row['cost']:>4} "
              f"{row['lb']:>3} {str(row['lbs']):<12} {row['conflicts']:>3} "
              f"{row['lb_min']:>5}  {split}")
        for ch in row.get("children", []):
            flag = "FOCAL" if ch["in_focal"] else "open only"
            if ch["id"] is None:
                print(f"      child {str(ch['constraint']):<28} pruned (no path)")
            else:
                print(f"      child {ch['id']:>3} {str(ch['constraint']):<28} "
                      f"cost {ch['cost']:>3} LB {ch['lb']:>3} lbs {str(ch['lbs']):<12} "
                      f"h_c {ch['conflicts']:>2}  {flag}")


# ---------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------
def _self_test() -> None:
    t0 = time.time()
    rng = random.Random(10)

    # -- conflict bookkeeping of the low level matches the plan checker ---
    for _ in range(40):
        inst = random_instance(5, 5, 4, rng, 0.15)
        stats = _Stats()
        root = _plan_root(inst, 1.5, stats)
        assert root is not None
        for i in range(inst.k):
            others = OtherPaths([p for j, p in enumerate(root.paths) if j != i])
            res = focal_space_time_astar(inst, i, frozenset(), others, 1.5)
            plan = list(root.paths)
            plan[i] = res.path
            assert res.conflicts == conflicts_of_agent(i, plan), (res.conflicts, plan)
            assert res.lower_bound <= path_cost(res.path) <= 1.5 * res.lower_bound

    # -- low level: w = 1 is optimal, bounds hold under constraints --------
    for _ in range(60):
        inst = random_instance(6, 6, 3, rng, 0.2)
        i = 0
        others = OtherPaths([])
        cons = set()
        d = inst.distances_to(inst.goals[i])[inst.starts[i]]
        opt = focal_space_time_astar(inst, i, frozenset(), others, 1.0)
        assert path_cost(opt.path) == d == opt.lower_bound
        for t in range(1, d + 2):                    # forbid the optimal cells
            cons.add(Constraint(i, t, (position(opt.path, t),)))
        cons = frozenset(cons)
        best = focal_space_time_astar(inst, i, cons, others, 1.0)
        if best is None:
            continue
        assert respects(best.path, cons)
        for w in (1.2, 1.5, 2.0):
            res = focal_space_time_astar(inst, i, cons, others, w)
            assert res is not None and respects(res.path, cons)
            assert res.lower_bound <= path_cost(best.path)          # a lower bound
            assert path_cost(res.path) <= w * res.lower_bound + 1e-9  # within w

    # -- the worked example ----------------------------------------------
    inst = worked_example()
    opt = cbs(inst, keep_trace=True)
    assert opt.solved and validate(inst, opt.paths) == []
    assert opt.cost == 12 and opt.ct_expanded == 7, (opt.cost, opt.ct_expanded)
    assert opt.ct_generated == 13 and opt.trace[0]["cost"] == 11
    assert opt.trace[0]["lbs"] == [2, 4, 5] and opt.trace[0]["conflicts"] == 1
    sub = ecbs(inst, w=1.2, keep_trace=True)
    assert sub.solved and validate(inst, sub.paths) == []
    assert sub.cost == 13 and sub.ct_expanded == 2, (sub.cost, sub.ct_expanded)
    assert sub.lower_bound == 11 and sub.cost <= 1.2 * sub.lower_bound
    assert sub.trace[-1]["lbs"] == [4, 4, 5] and sub.trace[-1]["conflicts"] == 0
    mid = ecbs(inst, w=1.1, keep_trace=True)
    assert mid.solved and mid.cost == 13 and mid.ct_expanded == 4, (
        mid.cost, mid.ct_expanded)
    assert mid.lower_bound == 12 and mid.ct_generated == 7
    tight = ecbs(inst, w=1.05, keep_trace=True)
    assert tight.solved and tight.cost == 12 and tight.ct_expanded == 7, (
        tight.cost, tight.ct_expanded)
    loose = ecbs(inst, w=1.5)
    assert loose.solved and loose.cost == 13 and loose.ct_expanded == 1
    assert loose.lower_bound == 11 and loose.trace == [] and loose.ct_generated == 1

    # -- the low-level example: w = 1 accepts the conflict, w = 1.5 waits -
    inst, fixed = low_level_example()
    others = OtherPaths(fixed)
    exact = focal_space_time_astar(inst, 0, frozenset(), others, 1.0)
    assert path_cost(exact.path) == 3 and exact.conflicts == 1 and exact.lower_bound == 3
    rows: List[dict] = []
    wide = focal_space_time_astar(inst, 0, frozenset(), others, 1.5, trace=rows)
    assert path_cost(wide.path) == 4 and wide.conflicts == 0 and wide.lower_bound == 3
    assert wide.path == [(1, 0), (1, 0), (1, 1), (1, 2), (1, 3)], wide.path
    assert wide.expansions == 4 and len(rows) == 5, (wide.expansions, len(rows))

    # -- ECBS on random instances: valid, within w of the CBS optimum -----
    checked = 0
    for _ in range(45):
        inst = random_instance(6, 6, 4, rng, 0.2)
        opt = cbs(inst, node_limit=400)
        if not opt.solved:
            continue
        assert validate(inst, opt.paths) == []
        exact = ecbs(inst, w=1.0, node_limit=400)
        assert exact.solved and exact.cost == opt.cost, (exact.cost, opt.cost)
        for w in (1.1, 1.5, 2.0):
            res = ecbs(inst, w=w, node_limit=400)
            assert res.solved, (inst, w)
            assert validate(inst, res.paths) == [], validate(inst, res.paths)
            assert opt.cost <= res.cost <= w * opt.cost + 1e-9, (opt.cost, res.cost, w)
            assert res.lower_bound <= opt.cost
            assert res.cost <= w * res.lower_bound + 1e-9
            assert res.ct_expanded <= opt.ct_expanded * 4 + 40
        checked += 1
    assert checked >= 25, checked

    # -- an instance with a corridor that needs a long detour -------------
    inst = Instance(["......", "@@@@.@", "......"], [(0, 0), (2, 0)],
                    [(2, 5), (0, 5)], "corridor")
    opt = cbs(inst)
    res = ecbs(inst, w=1.5)
    assert opt.solved and res.solved and validate(inst, res.paths) == []
    assert opt.cost <= res.cost <= 1.5 * opt.cost

    elapsed = time.time() - t0
    print(f"ch10_ecbs self-test passed in {elapsed:.1f} s "
          f"({checked} random instances checked against CBS)")


if __name__ == "__main__":
    _self_test()
    inst = worked_example()
    print("\nWorked example, CBS (optimal):")
    res = cbs(inst, keep_trace=True)
    print_trace(res)
    print_plan(res.paths)
    for w in (1.05, 1.2):
        print(f"\nWorked example, ECBS(w={w}):")
        res = ecbs(inst, w=w, keep_trace=True)
        print_trace(res)
        print_plan(res.paths)
        print(f"  cost {res.cost}, LB {res.lower_bound}, "
              f"guaranteed bound w*LB = {w * res.lower_bound:.2f}")
