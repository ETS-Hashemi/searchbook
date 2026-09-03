"""Scenario generator for Chapter 1 (Planning for Drone Swarms).

A *scenario* is a rectangular grid with randomly blocked cells, ``k``
controlled drones with pairwise distinct start and goal cells, and one
non-cooperative *intruder* that moves in a straight line at constant
velocity.  The module needs only the Python standard library.

Conventions used throughout the book (see Chapter 2):

* A cell is a pair ``(x, y)`` with ``0 <= x < width`` and
  ``0 <= y < height``.  Cell ``(x, y)`` covers the unit square
  ``[x, x + 1) x [y, y + 1)``; its centre is ``(x + 0.5, y + 0.5)``.
* The grid is 4-connected.  A drone moves to a neighbouring free cell or
  waits, one action per time step, and stays at its goal after arriving.
* The intruder lives in continuous space and continuous time: its
  position at time ``t`` is ``p0 + v * t`` (cells and cells per step).

Run ``python3 ch01_scenario.py`` to execute the self-test and print the
scenario used for Figure 1.1 of the book.
"""

from __future__ import annotations

import json
import math
import random
import time
from collections import deque
from dataclasses import dataclass

Cell = tuple[int, int]
Point = tuple[float, float]

# Neighbour order fixes the tie-breaking of breadth-first search.
MOVES4 = ((1, 0), (0, 1), (-1, 0), (0, -1))

# Seed of the scenario drawn in Figure 1.1 (chosen so that the independent
# shortest paths of two drones conflict and the intruder crosses the third).
BOOK_SEED = 1462


@dataclass(frozen=True)
class Intruder:
    """A non-cooperative moving object with straight-line motion."""

    position: Point  # (x, y) at time 0, in cell units
    velocity: Point  # cells per time step

    def position_at(self, t: float) -> Point:
        """Return the intruder position at (continuous) time ``t``."""
        return (self.position[0] + self.velocity[0] * t,
                self.position[1] + self.velocity[1] * t)

    def speed(self) -> float:
        """Return the speed in cells per time step."""
        return math.hypot(self.velocity[0], self.velocity[1])


@dataclass
class Scenario:
    """A grid map, the controlled drones and one intruder."""

    width: int
    height: int
    obstacles: set
    starts: list
    goals: list
    intruder: Intruder
    seed: int

    @property
    def num_drones(self) -> int:
        return len(self.starts)

    def in_bounds(self, cell: Cell) -> bool:
        x, y = cell
        return 0 <= x < self.width and 0 <= y < self.height

    def is_free(self, cell: Cell) -> bool:
        return self.in_bounds(cell) and cell not in self.obstacles

    def neighbours(self, cell: Cell) -> list:
        """Free 4-connected neighbours of ``cell`` in a fixed order."""
        x, y = cell
        out = []
        for dx, dy in MOVES4:
            nxt = (x + dx, y + dy)
            if self.is_free(nxt):
                out.append(nxt)
        return out

    def to_json(self) -> str:
        data = {
            "width": self.width,
            "height": self.height,
            "obstacles": sorted(self.obstacles),
            "starts": list(self.starts),
            "goals": list(self.goals),
            "intruder": {"position": list(self.intruder.position),
                         "velocity": list(self.intruder.velocity)},
            "seed": self.seed,
        }
        return json.dumps(data, indent=1)

    @staticmethod
    def from_json(text: str) -> "Scenario":
        d = json.loads(text)
        return Scenario(
            width=d["width"],
            height=d["height"],
            obstacles={tuple(c) for c in d["obstacles"]},
            starts=[tuple(c) for c in d["starts"]],
            goals=[tuple(c) for c in d["goals"]],
            intruder=Intruder(tuple(d["intruder"]["position"]),
                              tuple(d["intruder"]["velocity"])),
            seed=d["seed"],
        )


def bfs_path(scenario: Scenario, start: Cell, goal: Cell):
    """Shortest 4-connected path from ``start`` to ``goal`` or ``None``.

    Breadth-first search; ties are broken by the order of ``MOVES4``.
    """
    if not (scenario.is_free(start) and scenario.is_free(goal)):
        return None
    parent = {start: None}
    queue = deque([start])
    while queue:
        cell = queue.popleft()
        if cell == goal:
            path = []
            while cell is not None:
                path.append(cell)
                cell = parent[cell]
            return path[::-1]
        for nxt in scenario.neighbours(cell):
            if nxt not in parent:
                parent[nxt] = cell
                queue.append(nxt)
    return None


def _manhattan(a: Cell, b: Cell) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def generate(width: int, height: int, k: int, density: float,
             seed: int, min_distance: int | None = None,
             speed_range: tuple = (0.6, 1.2)) -> Scenario:
    """Draw a random scenario with ``k`` drones and one intruder.

    ``density`` is the fraction of blocked cells.  Start and goal cells are
    free, pairwise distinct (all ``2k`` of them), at Manhattan distance at
    least ``min_distance`` (default: a quarter of ``width + height``), and
    every goal is reachable from its start.  The intruder enters from one
    side of the grid and flies straight towards the opposite side without
    touching a blocked cell (it flies at the altitude of the swarm).
    """
    if k < 1 or width < 3 or height < 3:
        raise ValueError("need k >= 1 and a grid of at least 3 x 3 cells")
    rng = random.Random(seed)
    cells = [(x, y) for y in range(height) for x in range(width)]
    n_obstacles = round(density * width * height)
    if 2 * k > width * height - n_obstacles:
        raise ValueError("not enough free cells for the requested drones")
    if min_distance is None:
        min_distance = max(2, (width + height) // 4)

    for _attempt in range(1000):
        obstacles = set(rng.sample(cells, n_obstacles))
        scenario = Scenario(width, height, obstacles, [], [],
                            Intruder((0.0, 0.0), (0.0, 0.0)), seed)
        free = [c for c in cells if c not in obstacles]
        starts, goals = [], []
        for _inner in range(200):
            chosen = rng.sample(free, 2 * k)
            starts, goals = chosen[:k], chosen[k:]
            ok = all(_manhattan(s, g) >= min_distance
                     and bfs_path(scenario, s, g) is not None
                     for s, g in zip(starts, goals))
            if ok:
                break
        else:
            continue  # unlucky obstacle layout: draw a new one
        scenario.starts, scenario.goals = starts, goals
        for _inner in range(200):
            intruder = _random_intruder(rng, width, height, speed_range)
            if intruder_line_is_free(scenario, intruder):
                scenario.intruder = intruder
                return scenario
    raise RuntimeError("could not generate a valid scenario")


def _random_intruder(rng: random.Random, width: int, height: int,
                     speed_range: tuple) -> Intruder:
    """An intruder entering from one border, heading for the opposite one."""
    side = rng.choice(("left", "right", "bottom", "top"))
    if side in ("left", "right"):
        y0, y1 = rng.uniform(0.5, height - 0.5), rng.uniform(0.5, height - 0.5)
        p0 = (0.5, y0) if side == "left" else (width - 0.5, y0)
        p1 = (width - 0.5, y1) if side == "left" else (0.5, y1)
    else:
        x0, x1 = rng.uniform(0.5, width - 0.5), rng.uniform(0.5, width - 0.5)
        p0 = (x0, 0.5) if side == "bottom" else (x0, height - 0.5)
        p1 = (x1, height - 0.5) if side == "bottom" else (x1, 0.5)
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    length = math.hypot(dx, dy)
    speed = rng.uniform(*speed_range)
    velocity = (speed * dx / length, speed * dy / length)
    return Intruder((round(p0[0], 2), round(p0[1], 2)),
                    (round(velocity[0], 2), round(velocity[1], 2)))


def intruder_line_is_free(scenario: Scenario, intruder: Intruder,
                          step: float = 0.05) -> bool:
    """True if the straight line avoids blocked cells while inside the grid."""
    t = 0.0
    while True:
        x, y = intruder.position_at(t)
        if not (0.0 <= x < scenario.width and 0.0 <= y < scenario.height):
            return True
        if (int(x), int(y)) in scenario.obstacles:
            return False
        t += step


def plan_independently(scenario: Scenario) -> list:
    """Shortest path of every drone, ignoring the other drones."""
    return [bfs_path(scenario, s, g)
            for s, g in zip(scenario.starts, scenario.goals)]


def position_on_path(path: list, t: int) -> Cell:
    """Cell occupied at step ``t``; the drone stays at its goal afterwards."""
    return path[min(t, len(path) - 1)]


@dataclass(frozen=True)
class Conflict:
    """A planned conflict between two time-indexed paths."""

    time: int
    kind: str  # "vertex" or "edge"
    agents: tuple
    where: tuple  # a cell, or the pair of cells of a swapped edge


@dataclass(frozen=True)
class Encounter:
    """The intruder comes close to a drone that follows its planned path."""

    time: int
    drone: int
    distance: float


def cell_centre(cell: Cell) -> Point:
    return (cell[0] + 0.5, cell[1] + 0.5)


def find_conflicts(paths: list) -> list:
    """All vertex and edge (swap) conflicts between the given paths."""
    conflicts = []
    horizon = max(len(p) for p in paths)
    for i in range(len(paths)):
        for j in range(i + 1, len(paths)):
            for t in range(horizon):
                a0 = position_on_path(paths[i], t)
                b0 = position_on_path(paths[j], t)
                if a0 == b0:
                    conflicts.append(Conflict(t, "vertex", (i, j), a0))
                a1 = position_on_path(paths[i], t + 1)
                b1 = position_on_path(paths[j], t + 1)
                if a0 == b1 and b0 == a1 and a0 != a1:
                    conflicts.append(Conflict(t, "edge", (i, j), (a0, a1)))
    conflicts.sort(key=lambda c: (c.time, c.agents))
    return conflicts


def intruder_encounters(scenario: Scenario, paths: list, radius: float = 0.75,
                        horizon: int | None = None) -> list:
    """Time steps at which the intruder is within ``radius`` of a drone."""
    if horizon is None:
        horizon = max(len(p) for p in paths) + 1
    out = []
    for t in range(horizon):
        px, py = scenario.intruder.position_at(t)
        for i, path in enumerate(paths):
            cx, cy = cell_centre(position_on_path(path, t))
            d = math.hypot(px - cx, py - cy)
            if d <= radius:
                out.append(Encounter(t, i, round(d, 2)))
    return out


def describe(scenario: Scenario) -> str:
    """Human-readable summary with paths, conflicts and encounters."""
    paths = plan_independently(scenario)
    lines = [f"grid {scenario.width} x {scenario.height}, "
             f"{len(scenario.obstacles)} obstacles, "
             f"{scenario.num_drones} drones, seed {scenario.seed}"]
    for i, (s, g, p) in enumerate(zip(scenario.starts, scenario.goals, paths)):
        lines.append(f"  drone {chr(65 + i)}: {s} -> {g}, "
                     f"{len(p) - 1} steps: {p}")
    for c in find_conflicts(paths):
        a, b = (chr(65 + i) for i in c.agents)
        lines.append(f"  planned {c.kind} conflict {a}/{b} "
                     f"at t={c.time} at {c.where}")
    intr = scenario.intruder
    lines.append(f"  intruder at {intr.position}, velocity {intr.velocity} "
                 f"(speed {intr.speed():.2f} cells/step)")
    for e in intruder_encounters(scenario, paths):
        lines.append(f"  intruder within {e.distance} cells of drone "
                     f"{chr(65 + e.drone)} at t={e.time}")
    return "\n".join(lines)


def _adjacent(a: Cell, b: Cell) -> bool:
    return _manhattan(a, b) == 1


def _self_test() -> None:
    t0 = time.perf_counter()
    # 1. The generator is reproducible and depends on the seed.
    a = generate(12, 8, 3, 0.15, seed=BOOK_SEED)
    b = generate(12, 8, 3, 0.15, seed=BOOK_SEED)
    assert a == b, "same seed must give the same scenario"
    assert a != generate(12, 8, 3, 0.15, seed=BOOK_SEED + 1)

    # 2. Every generated scenario is valid.
    for seed in range(60):
        s = generate(10, 7, 4, 0.2, seed=seed)
        cells = s.starts + s.goals
        assert len(set(cells)) == 8, "starts and goals must be distinct"
        assert all(s.is_free(c) for c in cells)
        assert len(s.obstacles) == round(0.2 * 70)
        assert 0.6 <= s.intruder.speed() <= 1.2 + 1e-9
        assert intruder_line_is_free(s, s.intruder)
        for path, st, gl in zip(plan_independently(s), s.starts, s.goals):
            assert path is not None and path[0] == st and path[-1] == gl
            assert all(_adjacent(p, q) for p, q in zip(path, path[1:]))
            assert all(s.is_free(c) for c in path)
            assert len(path) - 1 >= _manhattan(st, gl) >= 4

    # 3. BFS returns shortest paths and reports unreachable goals.
    walled = Scenario(5, 3, {(2, 0), (2, 1), (2, 2)}, [], [],
                      Intruder((0.0, 0.0), (0.0, 0.0)), 0)
    assert bfs_path(walled, (0, 1), (4, 1)) is None
    walled.obstacles.discard((2, 2))
    assert len(bfs_path(walled, (0, 1), (4, 1))) - 1 == 6

    # 4. Conflict detection follows the MAPF definitions.
    swap = find_conflicts([[(0, 0), (1, 0)], [(1, 0), (0, 0)]])
    assert [c.kind for c in swap] == ["edge"] and swap[0].time == 0
    meet = find_conflicts([[(0, 0), (1, 0), (2, 0)], [(2, 0), (1, 0), (0, 0)]])
    assert [c.kind for c in meet] == ["vertex"]
    assert meet[0].time == 1 and meet[0].where == (1, 0)
    stay = find_conflicts([[(0, 0), (1, 0)], [(3, 0), (2, 0), (1, 0)]])
    assert stay == [Conflict(2, "vertex", (0, 1), (1, 0))], "stay-at-goal"
    assert find_conflicts([[(0, 0), (1, 0)], [(0, 1), (1, 1)]]) == []

    # 5. The intruder moves in a straight line and encounters are found.
    intr = Intruder((3.5, 0.5), (-1.0, 0.0))
    assert intr.position_at(0) == (3.5, 0.5)
    assert intr.position_at(2.5) == (1.0, 0.5)
    fixed = Scenario(4, 1, set(), [(0, 0)], [(0, 0)], intr, 0)
    enc = intruder_encounters(fixed, [[(0, 0)]], radius=0.75, horizon=6)
    assert [e.time for e in enc] == [3] and enc[0].distance == 0.0

    # 6. JSON round trip.
    assert Scenario.from_json(a.to_json()) == a

    # 7. The book scenario has both kinds of trouble.
    paths = plan_independently(a)
    assert find_conflicts(paths), "expected a planned conflict"
    assert intruder_encounters(a, paths), "expected an intruder encounter"
    assert time.perf_counter() - t0 < 10.0
    print("self-test passed")


if __name__ == "__main__":
    _self_test()
    print(describe(generate(12, 8, 3, 0.15, seed=BOOK_SEED)))
