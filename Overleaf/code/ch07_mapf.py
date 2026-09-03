"""Chapter 7 -- The Multi-Agent Path Finding Problem.

Classical MAPF on 4-connected grids: instances, time-indexed paths with
the stay-at-target convention, path and plan validation, conflict
detection (vertex and swapping conflicts) in O(k^2 T) and O(k T)
expected time, sum of costs and makespan, parsers and writers for the
.map/.scen benchmark formats, and the two examples of the chapter.

Run this file to execute the self-test:  python3 ch07_mapf.py
"""
from __future__ import annotations

import heapq
import itertools
import random
import time
from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

Cell = Tuple[int, int]      # (row, col); row 0 is the top row of the map
Path = List[Cell]           # path[t] is the cell occupied at time step t

FREE_CHARS = frozenset(".GS")   # passable characters of the .map format
MOVES = ((-1, 0), (1, 0), (0, -1), (0, 1))   # up, down, left, right


# ---------------------------------------------------------------------
# Instances
# ---------------------------------------------------------------------
@dataclass
class MAPFInstance:
    """A grid map plus k agents with unique starts and goals."""

    grid: List[str]          # one string per row, '.' free, '@'/'T' blocked
    starts: List[Cell]
    goals: List[Cell]
    name: str = "instance"

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
        """Free 4-neighbours of a cell (the move actions); waiting is separate."""
        r, c = cell
        return [(r + dr, c + dc) for dr, dc in MOVES if self.is_free((r + dr, c + dc))]

    def free_cells(self) -> List[Cell]:
        return [(r, c) for r in range(self.rows) for c in range(self.cols)
                if self.is_free((r, c))]

    def check(self) -> None:
        """Raise ValueError unless the instance is a classical MAPF instance."""
        if len(self.starts) != len(self.goals):
            raise ValueError("starts and goals differ in length")
        if len(set(self.starts)) != self.k or len(set(self.goals)) != self.k:
            raise ValueError("starts and goals must be unique")
        for cell in self.starts + self.goals:
            if not self.is_free(cell):
                raise ValueError(f"cell {cell} is blocked or outside the map")

    def to_map_text(self) -> str:
        head = f"type octile\nheight {self.rows}\nwidth {self.cols}\nmap\n"
        return head + "\n".join(self.grid) + "\n"

    def to_scen_text(self, map_name: str = "map.map") -> str:
        """Write the agents in the .scen format (x = column, y = row)."""
        lines = ["version 1"]
        for (sr, sc), (gr, gc) in zip(self.starts, self.goals):
            dist = len(bfs_path(self, (sr, sc), (gr, gc)) or [None]) - 1
            lines.append("\t".join(map(str, [0, map_name, self.cols, self.rows,
                                             sc, sr, gc, gr, dist])))
        return "\n".join(lines) + "\n"


def parse_map(text: str) -> List[str]:
    """Parse the .map format: 4 header lines, then one text row per map row."""
    lines = [ln.rstrip("\r\n") for ln in text.splitlines()]
    height = width = None
    body_start = None
    for idx, ln in enumerate(lines):
        words = ln.split()
        if not words:
            continue
        if words[0] == "height":
            height = int(words[1])
        elif words[0] == "width":
            width = int(words[1])
        elif words[0] == "map":
            body_start = idx + 1
            break
    if body_start is None or height is None or width is None:
        raise ValueError("not a .map file: missing height/width/map header")
    rows = [ln for ln in lines[body_start:body_start + height]]
    if len(rows) != height or any(len(r) != width for r in rows):
        raise ValueError("map body does not match the declared height/width")
    return rows


def parse_scen(text: str) -> List[Tuple[Cell, Cell]]:
    """Parse a .scen file into (start, goal) pairs as (row, col) cells.

    Each line is: bucket  map  width  height  sx  sy  gx  gy  length,
    where x is the column and y is the row.
    """
    pairs: List[Tuple[Cell, Cell]] = []
    for ln in text.splitlines():
        words = ln.split()
        if not words or words[0].lower().startswith("version"):
            continue
        sx, sy, gx, gy = (int(w) for w in words[4:8])
        pairs.append(((sy, sx), (gy, gx)))
    return pairs


def instance_from_text(map_text: str, scen_text: str, k: Optional[int] = None,
                       name: str = "benchmark") -> MAPFInstance:
    """Build an instance from the first k agents of a scenario."""
    grid = parse_map(map_text)
    pairs = parse_scen(scen_text)
    if k is not None:
        pairs = pairs[:k]
    inst = MAPFInstance(grid, [s for s, _ in pairs], [g for _, g in pairs], name)
    inst.check()
    return inst


def instance_from_files(map_path: str, scen_path: str,
                        k: Optional[int] = None) -> MAPFInstance:
    with open(map_path) as f_map, open(scen_path) as f_scen:
        return instance_from_text(f_map.read(), f_scen.read(), k, map_path)


# ---------------------------------------------------------------------
# Single-agent shortest paths (used for naive plans and lower bounds)
# ---------------------------------------------------------------------
def bfs_path(inst: MAPFInstance, start: Cell, goal: Cell) -> Optional[Path]:
    """Shortest path on the grid, ignoring all other agents (deterministic)."""
    parent: Dict[Cell, Optional[Cell]] = {start: None}
    queue = deque([start])
    while queue:
        cell = queue.popleft()
        if cell == goal:
            path: Path = []
            while cell is not None:
                path.append(cell)
                cell = parent[cell]
            return path[::-1]
        for nxt in inst.neighbors(cell):
            if nxt not in parent:
                parent[nxt] = cell
                queue.append(nxt)
    return None


def naive_plan(inst: MAPFInstance) -> List[Path]:
    """Independent shortest paths: the plan you get by ignoring the others."""
    plan = []
    for s, g in zip(inst.starts, inst.goals):
        path = bfs_path(inst, s, g)
        if path is None:
            raise ValueError(f"goal {g} unreachable from {s}")
        plan.append(path)
    return plan


# ---------------------------------------------------------------------
# Time-indexed paths, costs and objectives (stay-at-target)
# ---------------------------------------------------------------------
def position(path: Path, t: int) -> Cell:
    """Cell of an agent at time t; after its last step it stays at the goal."""
    return path[t] if t < len(path) else path[-1]


def horizon(paths: Sequence[Path]) -> int:
    """Largest time index that any path mentions explicitly."""
    return max(len(p) for p in paths) - 1


def path_cost(path: Path) -> int:
    """Time of the final arrival at the last cell (trailing waits cost nothing)."""
    goal = path[-1]
    t = len(path) - 1
    while t > 0 and path[t - 1] == goal:
        t -= 1
    return t


def sum_of_costs(paths: Sequence[Path]) -> int:
    return sum(path_cost(p) for p in paths)


def makespan(paths: Sequence[Path]) -> int:
    return max(path_cost(p) for p in paths)


# ---------------------------------------------------------------------
# Conflicts
# ---------------------------------------------------------------------
@dataclass(frozen=True)
class Conflict:
    """A vertex conflict <i, j, v, t> or a swapping conflict <i, j, u, v, t>.

    For a swap, agent i moves u -> v and agent j moves v -> u between
    time steps t and t + 1.  Always i < j.
    """

    kind: str                 # "vertex" or "swap"
    i: int
    j: int
    t: int
    cells: Tuple[Cell, ...]   # (v,) for a vertex conflict, (u, v) for a swap

    def __str__(self) -> str:
        if self.kind == "vertex":
            return f"vertex conflict: agents {self.i},{self.j} at {self.cells[0]} at t={self.t}"
        u, v = self.cells
        return (f"swapping conflict: agents {self.i},{self.j} on edge {u}-{v}"
                f" between t={self.t} and t={self.t + 1}")


def _vertex_conflicts_at(paths: Sequence[Path], t: int) -> List[Conflict]:
    found = []
    for i in range(len(paths)):
        for j in range(i + 1, len(paths)):
            v = position(paths[i], t)
            if v == position(paths[j], t):
                found.append(Conflict("vertex", i, j, t, (v,)))
    return found


def _swap_conflicts_at(paths: Sequence[Path], t: int) -> List[Conflict]:
    found = []
    for i in range(len(paths)):
        for j in range(i + 1, len(paths)):
            ui, vi = position(paths[i], t), position(paths[i], t + 1)
            uj, vj = position(paths[j], t), position(paths[j], t + 1)
            if ui != vi and ui == vj and vi == uj:
                found.append(Conflict("swap", i, j, t, (ui, vi)))
    return found


def first_conflict(paths: Sequence[Path]) -> Optional[Conflict]:
    """Earliest conflict by pairwise checking: O(k^2 T) time.

    Scan order: vertex conflicts at t, then swaps between t and t+1, then
    t+1.  Ties within a step go to the lexicographically smallest (i, j).
    """
    T = horizon(paths)
    for t in range(T + 1):
        found = _vertex_conflicts_at(paths, t)
        if found:
            return found[0]
        if t < T:
            found = _swap_conflicts_at(paths, t)
            if found:
                return found[0]
    return None


def all_conflicts(paths: Sequence[Path]) -> List[Conflict]:
    """Every vertex and swapping conflict, in scan order: O(k^2 T) time."""
    T = horizon(paths)
    found: List[Conflict] = []
    for t in range(T + 1):
        found += _vertex_conflicts_at(paths, t)
        if t < T:
            found += _swap_conflicts_at(paths, t)
    return found


def all_conflicts_hashed(paths: Sequence[Path]) -> List[Conflict]:
    """Every vertex and swapping conflict using dictionaries: O(k T) expected.

    At each time step the occupied cells are hashed, so each agent is
    compared with the agents already at its cell instead of with all others.
    """
    T = horizon(paths)
    found: List[Conflict] = []
    for t in range(T + 1):
        occupied: Dict[Cell, List[int]] = {}
        for i, path in enumerate(paths):
            v = position(path, t)
            for j in occupied.get(v, ()):
                found.append(Conflict("vertex", j, i, t, (v,)))
            occupied.setdefault(v, []).append(i)
        if t == T:
            break
        moving: Dict[Tuple[Cell, Cell], List[int]] = {}
        for i, path in enumerate(paths):
            u, v = position(path, t), position(path, t + 1)
            if u == v:
                continue
            for j in moving.get((v, u), ()):        # j traverses v -> u
                found.append(Conflict("swap", j, i, t, (v, u)))
            moving.setdefault((u, v), []).append(i)
    # canonical order: by time, vertex before swap, then by agent pair
    found.sort(key=lambda c: (c.t, c.kind != "vertex", c.i, c.j))
    return found


def first_conflict_hashed(paths: Sequence[Path]) -> Optional[Conflict]:
    """Earliest conflict with dictionaries: O(k T) expected time."""
    T = horizon(paths)
    for t in range(T + 1):
        occupied: Dict[Cell, int] = {}
        best: Optional[Conflict] = None
        for i, path in enumerate(paths):
            v = position(path, t)
            j = occupied.get(v)
            if j is None:
                occupied[v] = i
            elif best is None or (j, i) < (best.i, best.j):
                best = Conflict("vertex", j, i, t, (v,))
        if best is not None:
            return best
        if t == T:
            break
        moving: Dict[Tuple[Cell, Cell], int] = {}
        for i, path in enumerate(paths):
            u, v = position(path, t), position(path, t + 1)
            if u == v:
                continue
            j = moving.get((v, u))
            if j is not None and (best is None or (j, i) < (best.i, best.j)):
                best = Conflict("swap", j, i, t, (v, u))
            moving.setdefault((u, v), i)
        if best is not None:
            return best
    return None


# ---------------------------------------------------------------------
# Validation of paths and plans
# ---------------------------------------------------------------------
def validate_path(inst: MAPFInstance, i: int, path: Path) -> List[str]:
    """Problems of a single-agent path; an empty list means the path is fine."""
    problems = []
    if not path:
        return [f"agent {i}: empty path"]
    if path[0] != inst.starts[i]:
        problems.append(f"agent {i}: starts at {path[0]}, not at {inst.starts[i]}")
    if path[-1] != inst.goals[i]:
        problems.append(f"agent {i}: ends at {path[-1]}, not at {inst.goals[i]}")
    for t, cell in enumerate(path):
        if not inst.is_free(cell):
            problems.append(f"agent {i}: cell {cell} at t={t} is blocked or outside")
    for t in range(len(path) - 1):
        (r1, c1), (r2, c2) = path[t], path[t + 1]
        if (r1, c1) != (r2, c2) and abs(r1 - r2) + abs(c1 - c2) != 1:
            problems.append(f"agent {i}: illegal step {path[t]} -> {path[t + 1]} at t={t}")
    return problems


def validate_plan(inst: MAPFInstance, paths: Sequence[Path]) -> Tuple[bool, List[str]]:
    """True iff every path is legal and the plan has no vertex/swap conflict."""
    problems: List[str] = []
    if len(paths) != inst.k:
        problems.append(f"plan has {len(paths)} paths for {inst.k} agents")
    for i, path in enumerate(paths[:inst.k]):
        problems += validate_path(inst, i, path)
    if not problems:
        problems += [str(c) for c in all_conflicts(paths)]
    return (not problems), problems


# ---------------------------------------------------------------------
# Brute-force optimal solutions for tiny instances (verification only)
# ---------------------------------------------------------------------
def _joint_successors(inst: MAPFInstance, config: Tuple[Cell, ...],
                      active: Sequence[bool]):
    """Conflict-free joint moves; inactive agents stay where they are."""
    options = [([cell] + inst.neighbors(cell)) if act else [cell]
               for cell, act in zip(config, active)]
    for nxt in itertools.product(*options):
        if len(set(nxt)) != len(nxt):
            continue                       # vertex conflict
        swap = False
        for a in range(len(nxt)):
            for b in range(a + 1, len(nxt)):
                if config[a] != nxt[a] and nxt[a] == config[b] and nxt[b] == config[a]:
                    swap = True
        if not swap:
            yield nxt


def optimal_makespan_bruteforce(inst: MAPFInstance, max_steps: int = 30) -> Optional[int]:
    """Breadth-first search in the joint space of all agents."""
    start = tuple(inst.starts)
    goal = tuple(inst.goals)
    seen = {start}
    frontier = [start]
    for depth in range(max_steps + 1):
        if goal in seen:
            return depth
        nxt_frontier = []
        for config in frontier:
            for nxt in _joint_successors(inst, config, [True] * inst.k):
                if nxt not in seen:
                    seen.add(nxt)
                    nxt_frontier.append(nxt)
        frontier = nxt_frontier
    return None


def optimal_soc_bruteforce(inst: MAPFInstance, max_makespan: int = 30) -> Optional[int]:
    """Dijkstra over (configuration, done-flags, time) with cost = active agents.

    An agent may be declared 'done' when it is at its goal; a done agent
    never moves again and costs nothing, so the path cost of each agent is
    the time of its final arrival, exactly as in the chapter.
    """
    k = inst.k
    all_done = (1 << k) - 1
    start = (tuple(inst.starts), 0, 0)
    dist = {start: 0}
    heap = [(0, start)]
    while heap:
        d, (config, done, t) = heapq.heappop(heap)
        if d > dist.get((config, done, t), float("inf")):
            continue
        if done == all_done:
            return d
        # zero-cost transition: declare agents at their goal done
        for i in range(k):
            if not done >> i & 1 and config[i] == inst.goals[i]:
                state = (config, done | 1 << i, t)
                if d < dist.get(state, float("inf")):
                    dist[state] = d
                    heapq.heappush(heap, (d, state))
        if t >= max_makespan:
            continue
        active = [not done >> i & 1 for i in range(k)]
        n_active = sum(active)
        for nxt in _joint_successors(inst, config, active):
            state = (nxt, done, t + 1)
            if d + n_active < dist.get(state, float("inf")):
                dist[state] = d + n_active
                heapq.heappush(heap, (d + n_active, state))
    return None


# ---------------------------------------------------------------------
# The examples of the chapter
# ---------------------------------------------------------------------
def worked_example() -> MAPFInstance:
    """Three agents on a 4x4 grid with two obstacles (Section 7.6)."""
    grid = ["....",
            "@.@.",
            "....",
            "...."]
    starts = [(0, 0), (0, 3), (1, 1)]
    goals = [(0, 3), (0, 0), (0, 1)]
    inst = MAPFInstance(grid, starts, goals, "worked-example-4x4")
    inst.check()
    return inst


def worked_example_solution() -> List[Path]:
    """A conflict-free plan for worked_example(); optimal for both objectives."""
    return [
        [(0, 0), (0, 1), (1, 1), (0, 1), (0, 2), (0, 3)],
        [(0, 3), (0, 2), (0, 1), (0, 0)],
        [(1, 1), (2, 1), (2, 1), (1, 1), (0, 1)],
    ]


def objectives_example() -> MAPFInstance:
    """Three agents on an empty 4x5 grid where SoC and makespan disagree."""
    grid = ["....."] * 4
    starts = [(1, 0), (0, 1), (3, 2)]
    goals = [(1, 4), (2, 1), (0, 2)]
    inst = MAPFInstance(grid, starts, goals, "objectives-4x5")
    inst.check()
    return inst


def objectives_example_plans() -> Tuple[List[Path], List[Path]]:
    """Plan Y (agent 1 waits once) and plan X (agents 2 and 3 wait once)."""
    plan_y = [
        [(1, 0), (1, 0), (1, 1), (1, 2), (1, 3), (1, 4)],
        [(0, 1), (1, 1), (2, 1)],
        [(3, 2), (2, 2), (1, 2), (0, 2)],
    ]
    plan_x = [
        [(1, 0), (1, 1), (1, 2), (1, 3), (1, 4)],
        [(0, 1), (0, 1), (1, 1), (2, 1)],
        [(3, 2), (3, 2), (2, 2), (1, 2), (0, 2)],
    ]
    return plan_y, plan_x


def random_instance(rows: int, cols: int, k: int, rng: random.Random,
                    obstacle_density: float = 0.0) -> MAPFInstance:
    """Random obstacles, then k distinct starts and k distinct goals."""
    while True:
        grid = ["".join("@" if rng.random() < obstacle_density else "."
                        for _ in range(cols)) for _ in range(rows)]
        inst = MAPFInstance(grid, [], [], f"random-{rows}x{cols}")
        free = inst.free_cells()
        if len(free) < k:
            continue
        starts = rng.sample(free, k)
        goals = rng.sample(free, k)
        inst = MAPFInstance(grid, starts, goals, inst.name)
        if all(bfs_path(inst, s, g) is not None for s, g in zip(starts, goals)):
            return inst


def print_plan(paths: Sequence[Path]) -> None:
    T = horizon(paths)
    print("t    " + "".join(f"{t:>8}" for t in range(T + 1)))
    for i, path in enumerate(paths):
        cells = "".join(f"{str(position(path, t)):>8}" for t in range(T + 1))
        print(f"a{i}   " + cells + f"   cost {path_cost(path)}")


# ---------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------
def _self_test() -> None:
    t0 = time.time()

    # -- positions, padding and costs ----------------------------------
    p = [(0, 0), (0, 1), (0, 1), (0, 2), (0, 2), (0, 2)]
    assert position(p, 0) == (0, 0) and position(p, 5) == (0, 2)
    assert position(p, 99) == (0, 2), "stay-at-target padding"
    assert path_cost(p) == 3, "trailing waits at the goal are free"
    assert path_cost([(2, 2)]) == 0
    assert path_cost([(0, 0), (0, 1), (0, 0), (0, 1)]) == 3, "leaving the goal costs"
    assert sum_of_costs([p, [(5, 5)]]) == 3 and makespan([p, [(5, 5)]]) == 3

    # -- hand-constructed conflicting plans ----------------------------
    corridor = MAPFInstance(["....."], [(0, 0), (0, 4)], [(0, 4), (0, 0)], "corridor")
    head_on = naive_plan(corridor)
    c = first_conflict(head_on)
    assert c is not None and c.kind == "vertex" and c.t == 2 and c.cells == ((0, 2),)
    swap_plan = [[(0, 0), (0, 1), (0, 2)], [(0, 3), (0, 2), (0, 1)]]
    c = first_conflict(swap_plan)
    assert c.kind == "swap" and c.t == 1 and c.cells == ((0, 1), (0, 2)) and (c.i, c.j) == (0, 1)
    assert first_conflict_hashed(swap_plan) == c
    # following (allowed) and a conflict with a parked agent
    convoy = [[(0, 0), (0, 1), (0, 2), (0, 3)], [(0, 1), (0, 2), (0, 3), (0, 4)]]
    assert first_conflict(convoy) is None, "following conflicts are allowed"
    parked = [[(0, 1), (0, 2)], [(0, 0), (0, 1), (0, 2), (0, 3)]]
    c = first_conflict(parked)
    assert c is not None and c.kind == "vertex" and c.t == 2 and (c.i, c.j) == (0, 1)
    assert first_conflict_hashed(parked) == c
    # same edge, same direction: reported as a vertex conflict, never as a swap
    same_edge = [[(0, 0), (0, 1)], [(0, 0), (0, 1)]]
    kinds = [c.kind for c in all_conflicts(same_edge)]
    assert kinds == ["vertex", "vertex"], kinds
    # cycle conflict (rotation on a 2x2 block) is allowed
    rotation = [[(0, 0), (0, 1)], [(0, 1), (1, 1)], [(1, 1), (1, 0)], [(1, 0), (0, 0)]]
    assert all_conflicts(rotation) == [] and all_conflicts_hashed(rotation) == []

    # -- validation ---------------------------------------------------
    ok, problems = validate_plan(corridor, head_on)
    assert not ok and any("vertex" in s for s in problems)
    assert validate_path(corridor, 0, [(0, 0), (0, 2), (0, 4)])  # jumps are illegal
    assert validate_path(corridor, 0, [(0, 0), (1, 0), (0, 4)])  # outside the map
    ok, problems = validate_plan(corridor, [[(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)],
                                            [(0, 4), (0, 3), (0, 2), (0, 1), (0, 0)]])
    assert not ok

    # -- the worked example (numbers quoted in the chapter) -----------
    inst = worked_example()
    naive = naive_plan(inst)
    assert naive == [[(0, 0), (0, 1), (0, 2), (0, 3)],
                     [(0, 3), (0, 2), (0, 1), (0, 0)],
                     [(1, 1), (0, 1)]]
    assert sum_of_costs(naive) == 7 and makespan(naive) == 3
    c = first_conflict(naive)
    assert c == Conflict("vertex", 0, 2, 1, ((0, 1),)), c
    found = all_conflicts(naive)
    assert [(x.kind, x.i, x.j, x.t) for x in found] == [
        ("vertex", 0, 2, 1), ("swap", 0, 1, 1), ("vertex", 1, 2, 2)], found
    assert all_conflicts_hashed(naive) == found
    assert first_conflict_hashed(naive) == c
    sol = worked_example_solution()
    ok, problems = validate_plan(inst, sol)
    assert ok, problems
    assert [path_cost(p) for p in sol] == [5, 3, 4]
    assert sum_of_costs(sol) == 12 and makespan(sol) == 5
    assert optimal_makespan_bruteforce(inst) == 5
    assert optimal_soc_bruteforce(inst) == 12
    # the .map/.scen round trip of the example
    inst2 = instance_from_text(inst.to_map_text(), inst.to_scen_text("example.map"))
    assert inst2.grid == inst.grid and inst2.starts == inst.starts and inst2.goals == inst.goals
    scen_lines = inst.to_scen_text("example.map").splitlines()
    assert scen_lines[1].split() == ["0", "example.map", "4", "4", "0", "0", "3", "0", "3"]

    # -- the objectives example ---------------------------------------
    inst_o = objectives_example()
    naive_o = naive_plan(inst_o)
    assert [(x.kind, x.i, x.j, x.t) for x in all_conflicts(naive_o)] == [
        ("vertex", 0, 1, 1), ("vertex", 0, 2, 2)]
    plan_y, plan_x = objectives_example_plans()
    assert validate_plan(inst_o, plan_y)[0] and validate_plan(inst_o, plan_x)[0]
    assert (sum_of_costs(plan_y), makespan(plan_y)) == (10, 5)
    assert (sum_of_costs(plan_x), makespan(plan_x)) == (11, 4)
    assert optimal_soc_bruteforce(inst_o) == 10
    assert optimal_makespan_bruteforce(inst_o) == 4
    assert optimal_soc_bruteforce(inst_o, max_makespan=4) == 11, "SoC 10 needs makespan 5"

    # -- pairwise and hashed detectors agree on random plans ----------
    rng = random.Random(7)
    for trial in range(60):
        inst_r = random_instance(6, 6, rng.randint(2, 8), rng, 0.15)
        plan_r = naive_plan(inst_r)
        if trial % 2 == 0:            # add random waits so lengths differ
            for path in plan_r:
                t = rng.randrange(len(path))
                path.insert(t, path[t])
        assert all_conflicts(plan_r) == all_conflicts_hashed(plan_r)
        assert first_conflict(plan_r) == first_conflict_hashed(plan_r)
        found = all_conflicts(plan_r)
        assert (first_conflict(plan_r) is None) == (found == [])
        if found:
            assert first_conflict(plan_r) == found[0]

    # -- benchmark format on a small inline example -------------------
    map_text = "type octile\nheight 3\nwidth 4\nmap\n....\n.@T.\n....\n"
    scen_text = ("version 1\n"
                 "0\tsmall.map\t4\t3\t0\t0\t3\t2\t5\n"
                 "1\tsmall.map\t4\t3\t3\t0\t0\t2\t5\n")
    inst_b = instance_from_text(map_text, scen_text)
    assert inst_b.rows == 3 and inst_b.cols == 4
    assert inst_b.starts == [(0, 0), (0, 3)] and inst_b.goals == [(2, 3), (2, 0)]
    assert not inst_b.is_free((1, 1)) and not inst_b.is_free((1, 2)) and inst_b.is_free((1, 0))
    assert len(bfs_path(inst_b, (0, 0), (2, 3))) - 1 == 5

    elapsed = time.time() - t0
    assert elapsed < 10, f"self-test too slow: {elapsed:.1f} s"
    print(f"ch07_mapf self-test passed in {elapsed:.2f} s")


if __name__ == "__main__":
    _self_test()
    inst = worked_example()
    print("\nWorked example, naive plan:")
    print_plan(naive_plan(inst))
    for c in all_conflicts(naive_plan(inst)):
        print("  ", c)
    print("Conflict-free plan:")
    print_plan(worked_example_solution())
    print("SoC =", sum_of_costs(worked_example_solution()),
          " makespan =", makespan(worked_example_solution()))
