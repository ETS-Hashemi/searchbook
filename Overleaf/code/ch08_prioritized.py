"""Chapter 8 -- Prioritized Planning and Space-Time A*.

Prioritized planning (Cooperative A*) on 4-connected grids: a reservation
table with vertex, edge (swap) and parked-goal entries, space-time A*
against the table with a correct goal-stay test, the outer priority loop,
an internal plan validator, the well-formedness test, priority-ordering
heuristics with random restarts, a compact windowed variant (WHCA*), a
brute-force optimum for tiny instances, and the examples of the chapter.

Cells are (row, col) with row 0 at the top, as in Chapter 7.  A path is
the list of cells occupied at t = 0, 1, ..., T; the agent stays at
path[-1] afterward (stay-at-target), and its cost is T.

Run this file to execute the self-test:  python3 ch08_prioritized.py
"""
from __future__ import annotations

import heapq
import itertools
import random
import sys
import time
from collections import deque
from dataclasses import dataclass
from typing import Callable, Dict, FrozenSet, List, Optional, Sequence, Set, Tuple

Cell = Tuple[int, int]
Path = List[Cell]
MOVES = ((-1, 0), (1, 0), (0, -1), (0, 1))      # up, down, left, right
INF = float("inf")


# ---------------------------------------------------------------------
# Instances
# ---------------------------------------------------------------------
@dataclass
class Instance:
    """A grid map ('.' free, '@' blocked) plus k agents with starts and goals."""

    grid: List[str]
    starts: List[Cell]
    goals: List[Cell]
    name: str = "instance"

    @property
    def rows(self) -> int:
        return len(self.grid)

    @property
    def cols(self) -> int:
        return len(self.grid[0])

    @property
    def k(self) -> int:
        return len(self.starts)

    def is_free(self, cell: Cell) -> bool:
        r, c = cell
        return 0 <= r < self.rows and 0 <= c < self.cols and self.grid[r][c] == "."

    def neighbors(self, cell: Cell) -> List[Cell]:
        r, c = cell
        return [(r + dr, c + dc) for dr, dc in MOVES if self.is_free((r + dr, c + dc))]

    def free_cells(self) -> List[Cell]:
        return [(r, c) for r in range(self.rows) for c in range(self.cols)
                if self.is_free((r, c))]


def manhattan(a: Cell, b: Cell) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def bfs_distances(inst: Instance, goal: Cell,
                  blocked: FrozenSet[Cell] = frozenset()) -> Dict[Cell, int]:
    """Exact static distances to `goal` (backward Dijkstra with unit costs).

    This is the true-distance heuristic of HCA*; cells in `blocked` are
    treated as obstacles.  Unreachable cells are absent from the result.
    """
    dist = {goal: 0}
    queue = deque([goal])
    while queue:
        v = queue.popleft()
        for u in inst.neighbors(v):
            if u not in dist and u not in blocked:
                dist[u] = dist[v] + 1
                queue.append(u)
    return dist


# ---------------------------------------------------------------------
# Reservation table
# ---------------------------------------------------------------------
class ReservationTable:
    """Space-time entries of the agents planned so far.

    vertices : set of (cell, t)            -- cell occupied at time t
    edges    : set of (u, v, t)            -- move u -> v during step t -> t+1
    parked   : dict cell -> time T         -- cell occupied for all t >= T
    window   : if not None, entries at t >= window are ignored (WHCA*)
    """

    def __init__(self, window: Optional[int] = None) -> None:
        self.vertices: Set[Tuple[Cell, int]] = set()
        self.edges: Set[Tuple[Cell, Cell, int]] = set()
        self.parked: Dict[Cell, int] = {}
        self.window = window
        self.last_timed = -1        # largest t of any timed entry

    def reserve(self, path: Path) -> None:
        """Add a path: its cells, its moves and its parked goal."""
        for t, cell in enumerate(path):
            self.vertices.add((cell, t))
            if t + 1 < len(path) and path[t + 1] != cell:
                self.edges.add((cell, path[t + 1], t))
        self.last_timed = max(self.last_timed, len(path) - 1)
        goal, arrival = path[-1], len(path) - 1
        self.parked[goal] = min(arrival, self.parked.get(goal, INF))

    def in_window(self, t: int) -> bool:
        return self.window is None or t < self.window

    def is_blocked(self, cell: Cell, t: int) -> bool:
        """May an agent NOT be at `cell` at time t?"""
        if not self.in_window(t):
            return False
        return (cell, t) in self.vertices or t >= self.parked.get(cell, INF)

    def is_swap(self, u: Cell, v: Cell, t: int) -> bool:
        """Would moving u -> v during step t swap with a reserved move?"""
        return self.in_window(t) and (v, u, t) in self.edges

    def last_reserved(self, cell: Cell) -> float:
        """Last time at which `cell` is taken: -1 never, inf if parked on."""
        if cell in self.parked and self.in_window(self.parked[cell]):
            return INF
        times = [t for (c, t) in self.vertices if c == cell and self.in_window(t)]
        return max(times) if times else -1

    def static_time(self) -> int:
        """First time from which the table no longer changes."""
        if self.window is not None:
            return self.window
        return self.last_timed + 1


# ---------------------------------------------------------------------
# Space-time A* against the table (Cooperative A*)
# ---------------------------------------------------------------------
def space_time_astar(inst: Instance, start: Cell, goal: Cell, table: ReservationTable,
                     dist: Optional[Dict[Cell, int]] = None,
                     avoid: FrozenSet[Cell] = frozenset(),
                     trace: Optional[list] = None,
                     stats: Optional[dict] = None) -> Optional[Path]:
    """Shortest path from (start, 0) to the goal that respects the table.

    dist  : static distances to the goal (HCA* heuristic); Manhattan if None.
    avoid : cells treated as static obstacles (starts of lower-priority
            agents in revised prioritized planning).
    The closed set collapses the time index beyond table.static_time(),
    where the table is static, so the search is finite without a horizon.
    """
    if dist is not None:
        if start not in dist:
            return None
        h: Callable[[Cell], int] = lambda c: dist.get(c, 10 ** 9)
    else:
        h = lambda c: manhattan(c, goal)
    t_goal = table.last_reserved(goal)      # arrival must be later than this
    if t_goal == INF or table.is_blocked(start, 0):
        return None
    t_static = table.static_time()
    counter = itertools.count()
    open_heap = [(h(start), 0, next(counter), start, 0)]
    parent: Dict[Tuple[Cell, int], Tuple[Cell, int]] = {}
    closed: Set[Tuple[Cell, int]] = set()
    expansions = 0
    while open_heap:
        f, neg_g, _, v, t = heapq.heappop(open_heap)
        key = (v, min(t, t_static))
        if key in closed:
            continue
        closed.add(key)
        expansions += 1
        if v == goal and t > t_goal:
            if stats is not None:
                stats["expansions"] = stats.get("expansions", 0) + expansions
            if trace is not None:
                trace.append((v, t, t, h(v), f, ["goal"], []))
            path = [(v, t)]
            while path[-1] in parent:
                path.append(parent[path[-1]])
            return [cell for cell, _ in reversed(path)]
        generated, blocked = [], []
        for v2 in [v] + inst.neighbors(v):        # wait first, then moves
            if v2 in avoid:
                continue
            if table.is_blocked(v2, t + 1):
                blocked.append((v2, "V"))
                continue
            if v2 != v and table.is_swap(v, v2, t):
                blocked.append((v2, "E"))
                continue
            if (v2, min(t + 1, t_static)) in closed:
                continue
            parent.setdefault((v2, t + 1), (v, t))
            generated.append(v2)
            heapq.heappush(open_heap, (t + 1 + h(v2), -(t + 1), next(counter), v2, t + 1))
        if trace is not None:
            trace.append((v, t, t, h(v), f, generated, blocked))
    if stats is not None:
        stats["expansions"] = stats.get("expansions", 0) + expansions
    return None


# ---------------------------------------------------------------------
# Prioritized planning
# ---------------------------------------------------------------------
def prioritized_planning(inst: Instance, order: Sequence[int], heuristic: str = "manhattan",
                         revised: bool = False, stats: Optional[dict] = None,
                         traces: Optional[dict] = None) -> Optional[List[Path]]:
    """Plan the agents in `order`; each treats the earlier ones as moving obstacles.

    heuristic : "manhattan" (CA*) or "true" (HCA*, backward Dijkstra).
    revised   : also avoid the starts of all lower-priority agents (the rule
                that makes the method complete on well-formed instances).
    Returns the list of paths (indexed by agent) or None on failure.
    """
    table = ReservationTable()
    paths: List[Optional[Path]] = [None] * inst.k
    for j, i in enumerate(order):
        dist = bfs_distances(inst, inst.goals[i]) if heuristic == "true" else None
        avoid = frozenset(inst.starts[m] for m in order[j + 1:]) if revised else frozenset()
        trace = [] if traces is not None else None
        path = space_time_astar(inst, inst.starts[i], inst.goals[i], table, dist,
                                avoid, trace, stats)
        if traces is not None:
            traces[i] = trace
        if path is None:
            return None
        paths[i] = path
        table.reserve(path)
    return paths                                              # type: ignore[return-value]


def path_cost(path: Path) -> int:
    """Time of the final arrival at the goal (trailing waits are free)."""
    T = len(path) - 1
    while T > 0 and path[T - 1] == path[-1]:
        T -= 1
    return T


def sum_of_costs(paths: Sequence[Path]) -> int:
    return sum(path_cost(p) for p in paths)


def makespan(paths: Sequence[Path]) -> int:
    return max(path_cost(p) for p in paths)


def position(path: Path, t: int) -> Cell:
    return path[t] if t < len(path) else path[-1]


def validate(inst: Instance, paths: Sequence[Path]) -> List[str]:
    """Internal validator: legality of every path, then vertex/swap conflicts."""
    errors = []
    for i, p in enumerate(paths):
        if p[0] != inst.starts[i] or p[-1] != inst.goals[i]:
            errors.append(f"agent {i}: wrong start or goal")
        for t in range(len(p) - 1):
            if p[t + 1] != p[t] and p[t + 1] not in inst.neighbors(p[t]):
                errors.append(f"agent {i}: illegal move at t={t}")
        if not all(inst.is_free(c) for c in p):
            errors.append(f"agent {i}: enters an obstacle")
    T = max(len(p) for p in paths)
    for t in range(T):
        occupied: Dict[Cell, int] = {}
        for i, p in enumerate(paths):
            c = position(p, t)
            if c in occupied:
                errors.append(f"vertex conflict agents {occupied[c]},{i} at {c} t={t}")
            occupied[c] = i
        for i in range(len(paths)):
            for j in range(i + 1, len(paths)):
                if (position(paths[i], t) == position(paths[j], t + 1)
                        and position(paths[i], t + 1) == position(paths[j], t)
                        and position(paths[i], t) != position(paths[i], t + 1)):
                    errors.append(f"swapping conflict agents {i},{j} at t={t}")
    return errors


# ---------------------------------------------------------------------
# Well-formed instances
# ---------------------------------------------------------------------
def is_well_formed(inst: Instance) -> bool:
    """Distinct endpoints, and every agent reaches its goal avoiding the others'."""
    endpoints = list(inst.starts) + list(inst.goals)
    if len(set(endpoints)) != 2 * inst.k:
        return False
    for i in range(inst.k):
        others = frozenset(e for e in endpoints if e not in (inst.starts[i], inst.goals[i]))
        if inst.starts[i] not in bfs_distances(inst, inst.goals[i], others):
            return False
    return True


# ---------------------------------------------------------------------
# Priority orderings
# ---------------------------------------------------------------------
def naive_paths(inst: Instance) -> List[Path]:
    """Independent shortest paths (lower bounds), planned against an empty table."""
    return [space_time_astar(inst, s, g, ReservationTable()) or [s]
            for s, g in zip(inst.starts, inst.goals)]


def order_random(inst: Instance, rng: random.Random) -> List[int]:
    order = list(range(inst.k))
    rng.shuffle(order)
    return order


def order_longest_first(inst: Instance) -> List[int]:
    """Longest independent shortest path first."""
    lengths = [path_cost(p) for p in naive_paths(inst)]
    return sorted(range(inst.k), key=lambda i: (-lengths[i], i))


def order_most_constrained_first(inst: Instance) -> List[int]:
    """Agents whose independent path conflicts with most others go first."""
    paths = naive_paths(inst)
    degree = [0] * inst.k
    for i in range(inst.k):
        for j in range(i + 1, inst.k):
            if validate_pair(paths[i], paths[j]):
                degree[i] += 1
                degree[j] += 1
    lengths = [path_cost(p) for p in paths]
    return sorted(range(inst.k), key=lambda i: (-degree[i], -lengths[i], i))


def validate_pair(p: Path, q: Path) -> bool:
    """True if the two paths have a vertex or swapping conflict."""
    for t in range(max(len(p), len(q))):
        if position(p, t) == position(q, t):
            return True
        if position(p, t) == position(q, t + 1) and position(p, t + 1) == position(q, t) \
                and position(p, t) != position(p, t + 1):
            return True
    return False


def plan_with_restarts(inst: Instance, rng: random.Random, tries: int = 5,
                       heuristic: str = "true") -> Optional[List[Path]]:
    """Random restarts: try random orders, keep the cheapest plan found."""
    best = None
    for _ in range(tries):
        plan = prioritized_planning(inst, order_random(inst, rng), heuristic)
        if plan is not None and (best is None or sum_of_costs(plan) < sum_of_costs(best)):
            best = plan
    return best


def all_orders(inst: Instance, heuristic: str = "manhattan"):
    """(order, costs-per-agent or None, sum of costs or None) for every order."""
    rows = []
    for order in itertools.permutations(range(inst.k)):
        plan = prioritized_planning(inst, order, heuristic)
        if plan is None:
            rows.append((order, None, None))
        else:
            rows.append((order, [path_cost(p) for p in plan], sum_of_costs(plan)))
    return rows


# ---------------------------------------------------------------------
# Windowed variant (WHCA*): plan w steps ahead, execute `step`, repeat
# ---------------------------------------------------------------------
def whca_star(inst: Instance, window: int = 8, step: int = 4,
              max_rounds: int = 200) -> Optional[List[Path]]:
    """Return the executed paths, or None if the agents do not all arrive."""
    dist = [bfs_distances(inst, g) for g in inst.goals]     # true-distance heuristics
    executed: List[Path] = [[s] for s in inst.starts]
    for rnd in range(max_rounds):
        pos = [p[-1] for p in executed]
        if pos == list(inst.goals):
            return executed
        table = ReservationTable(window=window)
        for i in [(m + rnd) % inst.k for m in range(inst.k)]:    # rotate priorities
            path = space_time_astar(inst, pos[i], inst.goals[i], table, dist[i])
            if path is None:
                path = [pos[i]]                                  # stay put (unsafe)
            table.reserve(path)
            moves = path[1:step + 1]
            moves += [path[-1]] * (step - len(moves))
            executed[i].extend(moves)
    return None


# ---------------------------------------------------------------------
# Brute-force optimum for tiny instances (sum of costs)
# ---------------------------------------------------------------------
def _joint_successors(inst: Instance, config: Tuple[Cell, ...], active: Sequence[bool]):
    options = [([c] + inst.neighbors(c)) if a else [c] for c, a in zip(config, active)]
    for nxt in itertools.product(*options):
        if len(set(nxt)) != len(nxt):
            continue
        if any(config[a] != nxt[a] and nxt[a] == config[b] and nxt[b] == config[a]
               for a in range(len(nxt)) for b in range(a + 1, len(nxt))):
            continue
        yield nxt


def optimal_soc(inst: Instance, max_makespan: int = 25) -> Optional[int]:
    """Dijkstra over (configuration, done flags, time); done agents block their goal."""
    k, all_done = inst.k, (1 << inst.k) - 1
    start = (tuple(inst.starts), 0, 0)
    dist = {start: 0}
    heap = [(0, start)]
    while heap:
        d, state = heapq.heappop(heap)
        if d > dist[state]:
            continue
        config, done, t = state
        if done == all_done:
            return d
        for i in range(k):
            if not done >> i & 1 and config[i] == inst.goals[i]:
                s2 = (config, done | 1 << i, t)
                if d < dist.get(s2, INF):
                    dist[s2] = d
                    heapq.heappush(heap, (d, s2))
        if t >= max_makespan:
            continue
        active = [not done >> i & 1 for i in range(k)]
        cost = d + sum(active)
        for nxt in _joint_successors(inst, config, active):
            s2 = (nxt, done, t + 1)
            if cost < dist.get(s2, INF):
                dist[s2] = cost
                heapq.heappush(heap, (cost, s2))
    return None


# ---------------------------------------------------------------------
# The examples of the chapter
# ---------------------------------------------------------------------
def worked_example() -> Instance:
    """Three agents on a 3 x 7 grid: the order decides between 16, 21 and failure."""
    grid = [".......",
            ".@@.@@.",
            "......."]
    return Instance(grid, [(2, 0), (0, 0), (0, 3)], [(2, 6), (0, 6), (2, 3)], "worked")


def incompleteness_example() -> Instance:
    """Two agents swap ends of a corridor with one pocket: every order fails."""
    grid = ["@@.@@",
            "....."]
    return Instance(grid, [(1, 0), (1, 4)], [(1, 4), (1, 0)], "pocket")


def suboptimality_example() -> Instance:
    """Corridor with a pocket and a bypass: the best order is not optimal."""
    grid = [".......",
            ".@@@@@.",
            ".......",
            "@@@.@@@"]
    return Instance(grid, [(2, 0), (2, 6)], [(2, 6), (2, 0)], "bypass")


def incompleteness_solution() -> List[Path]:
    """A valid plan for incompleteness_example(): agent 1 steps into the pocket."""
    return [[(1, 0), (1, 1), (1, 2), (0, 2), (1, 2), (1, 3), (1, 4)],
            [(1, 4), (1, 4), (1, 3), (1, 2), (1, 1), (1, 0)]]


def suboptimality_solution() -> List[Path]:
    """A valid plan for suboptimality_example() cheaper than every order."""
    return [[(2, 0), (2, 1), (2, 2), (2, 3), (3, 3), (2, 3), (2, 4), (2, 5), (2, 6)],
            [(2, 6), (2, 5), (2, 4), (2, 4), (2, 3), (2, 2), (2, 1), (2, 0)]]


def random_instance(rows: int, cols: int, k: int, rng: random.Random,
                    density: float = 0.2) -> Instance:
    """Random obstacles, distinct starts and goals, every pair connected."""
    while True:
        grid = ["".join("@" if rng.random() < density else "." for _ in range(cols))
                for _ in range(rows)]
        inst = Instance(grid, [], [], f"random-{rows}x{cols}")
        free = inst.free_cells()
        if len(free) < 2 * k:
            continue
        starts, goals = rng.sample(free, k), rng.sample(free, k)
        inst = Instance(grid, starts, goals, inst.name)
        if all(s in bfs_distances(inst, g) for s, g in zip(starts, goals)):
            return inst


def print_plan(paths: Sequence[Path]) -> None:
    T = max(len(p) for p in paths)
    print("  t  " + "".join(f"{t:>7}" for t in range(T)))
    for i, p in enumerate(paths):
        print(f"  a{i + 1} " + "".join(f"{str(position(p, t)):>7}" for t in range(T))
              + f"   cost {path_cost(p)}")


# ---------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------
def _self_test() -> None:
    t0 = time.time()
    # 1. Worked example: all six orders.
    inst = worked_example()
    assert not is_well_formed(inst)
    rows = all_orders(inst)
    table = {order: soc for order, _, soc in rows}
    print("worked example, sum of costs per order (agents numbered 1..3):")
    for order, costs, soc in rows:
        print("  order", tuple(i + 1 for i in order), "costs", costs, "SoC", soc)
    assert table[(0, 1, 2)] == 16 and table[(0, 2, 1)] == 16 and table[(1, 0, 2)] == 16
    assert table[(2, 0, 1)] == 21 and table[(1, 2, 0)] is None and table[(2, 1, 0)] is None
    assert optimal_soc(inst) == 16
    traces: dict = {}
    plan = prioritized_planning(inst, [0, 1, 2], traces=traces)
    assert plan is not None and not validate(inst, plan)
    assert [path_cost(p) for p in plan] == [6, 6, 4]
    print_plan(plan)
    print("trace of agent 3 in order (1,2,3): (cell, t, g, h, f, generated, blocked)")
    for step, row in enumerate(traces[2], 1):
        print(f"  {step:2d}", row)
    for order, costs, soc in rows:
        p = prioritized_planning(inst, order)
        assert p is None or not validate(inst, p)
    print("plan for order (3,1,2):")
    print_plan(prioritized_planning(inst, [2, 0, 1]))
    # 2. Incompleteness and suboptimality counterexamples.
    inc = incompleteness_example()
    assert all(soc is None for _, _, soc in all_orders(inc))
    inc_opt = optimal_soc(inc)
    print("pocket corridor: every order fails; optimal sum of costs =", inc_opt)
    assert inc_opt is not None
    assert not validate(inc, incompleteness_solution())
    assert sum_of_costs(incompleteness_solution()) == inc_opt
    sub = suboptimality_example()
    sub_rows = all_orders(sub)
    sub_best = min(soc for _, _, soc in sub_rows if soc is not None)
    sub_opt = optimal_soc(sub)
    print("bypass corridor: orders give", [soc for _, _, soc in sub_rows],
          "best order", sub_best, "optimal", sub_opt)
    assert sub_opt is not None and sub_opt < sub_best
    assert not validate(sub, suboptimality_solution())
    assert sum_of_costs(suboptimality_solution()) == sub_opt
    print("plan of the best order (1,2) on the bypass corridor:")
    print_plan(prioritized_planning(sub, [0, 1]))
    # 3. Random instances: every returned plan is conflict-free.
    rng = random.Random(8)
    n_ok = n_fail = 0
    for _ in range(40):
        ri = random_instance(10, 10, 5, rng, 0.15)
        for heur in ("manhattan", "true"):
            plan = prioritized_planning(ri, order_random(ri, rng), heur)
            if plan is None:
                n_fail += 1
            else:
                n_ok += 1
                assert not validate(ri, plan), validate(ri, plan)
                assert plan[0][0] == ri.starts[0]
    print(f"random 10x10 instances with 5 agents: {n_ok} plans valid, {n_fail} failures")
    # 4. Well-formed instances: revised PP succeeds for every order.
    n_wf = n_plain_fail = 0
    while n_wf < 25:
        ri = random_instance(6, 6, 3, rng, 0.25)
        if not is_well_formed(ri):
            continue
        n_wf += 1
        for order in itertools.permutations(range(ri.k)):
            plan = prioritized_planning(ri, order, revised=True)
            assert plan is not None and not validate(ri, plan)
            if prioritized_planning(ri, order) is None:
                n_plain_fail += 1
    print(f"{n_wf} random well-formed instances: revised PP never failed;"
          f" plain PP failed in {n_plain_fail} of {n_wf * 6} orders")
    # 5. Heuristics: true distance expands no more than Manhattan.
    exp_m = exp_t = 0
    for _ in range(20):
        ri = random_instance(20, 20, 8, rng, 0.30)
        order = order_longest_first(ri)
        sm, st = {}, {}
        prioritized_planning(ri, order, "manhattan", stats=sm)
        prioritized_planning(ri, order, "true", stats=st)
        exp_m += sm.get("expansions", 0)
        exp_t += st.get("expansions", 0)
    print(f"expansions on 20 cluttered 20x20 grids: Manhattan {exp_m}, true distance {exp_t}")
    assert exp_t <= exp_m
    # 6. Ordering heuristics and restarts return valid plans.
    ri = random_instance(12, 12, 8, rng, 0.2)
    for order in (order_longest_first(ri), order_most_constrained_first(ri)):
        assert sorted(order) == list(range(ri.k))
    plan = plan_with_restarts(ri, rng, tries=5)
    assert plan is None or not validate(ri, plan)
    # 7. Timing: forty agents on a large grid.  One instance by default,
    #    the median of three with the command-line flag "--bench".
    times = []
    for seed in ((1, 2, 3) if "--bench" in sys.argv else (2,)):
        big = random_instance(100, 100, 40, random.Random(seed), 0.2)
        order = order_longest_first(big)
        t1 = time.time()
        plan = prioritized_planning(big, order, heuristic="true")
        times.append(time.time() - t1)
        assert plan is None or not validate(big, plan)
    times.sort()
    if len(times) == 3:
        print(f"forty agents on a 100x100 grid with 20% obstacles: "
              f"{times[0]:.1f}, {times[1]:.1f}, {times[2]:.1f} s "
              f"(median {times[1]:.1f} s)")
    else:
        print(f"forty agents on a 100x100 grid with 20% obstacles: {times[0]:.1f} s"
              f" (run with --bench for three instances and their median)")
    # 8. WHCA*: the executed plan of the worked example is conflict-free.
    ex = whca_star(inst, window=6, step=3)
    assert ex is not None and not validate(inst, ex), ex
    print("WHCA* on the worked example: costs", [path_cost(p) for p in ex],
          "sum", sum_of_costs(ex))
    print(f"self-test passed in {time.time() - t0:.1f} s")


if __name__ == "__main__":
    _self_test()
