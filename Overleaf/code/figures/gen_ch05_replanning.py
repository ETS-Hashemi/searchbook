"""Generate figures/data/ch05-replanning.dat: D* Lite vs repeated A*.

On a SIZE x SIZE 4-connected grid with obstacle density DENSITY, the robot
starts in the top-left cell and heads for the bottom-right cell.  Event 0 is
the initial search.  At each of EVENTS further events the robot first takes
one step along its current path; then one new obstacle appears, with
probability ON_PATH on the robot's current path (never on the robot's cell or
the goal, and never disconnecting the goal), otherwise at a uniformly random
free cell.  D* Lite repairs its search; the baseline runs A* from scratch
from the robot's cell on the changed grid, once with the usual grid
tie-breaking (ties on f toward smaller h) and once with the tie-breaking of
the D* Lite key (ties toward smaller g).  Means over SEEDS grids.

Columns (whitespace separated, one header row):
    event       0 = initial search, then 1..EVENTS
    dsl_exp     vertex expansions of D* Lite for the event
    astar_exp   vertex expansions of A* from scratch (ties toward smaller h)
    astarg_exp  vertex expansions of A* from scratch (ties toward smaller g)
    dsl_ms      wall-clock milliseconds of D* Lite (UpdateVertex + repair)
    astar_ms    wall-clock milliseconds of A* (ties toward smaller h)
    astarg_ms   wall-clock milliseconds of A* (ties toward smaller g)
    dsl_cum     cumulative D* Lite expansions
    astar_cum   cumulative A* expansions (ties toward smaller h)
    onpath      fraction of seeds in which the obstacle landed on the path
    cost        mean remaining path cost after the event

Run from Overleaf/:

    python3 code/figures/gen_ch05_replanning.py
"""

import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from ch05_dstar_lite import DStarLite, Grid, astar, reachable  # noqa: E402

SIZE = 50
DENSITY = 0.20
EVENTS = 40
SEEDS = 10
ON_PATH = 0.5
SEED = 5
OUT = os.path.join(os.path.dirname(HERE), "..", "figures", "data", "ch05-replanning.dat")


def random_grid(rng, start, goal):
    while True:
        blocked = {(x, y) for x in range(SIZE) for y in range(SIZE)
                   if rng.random() < DENSITY and (x, y) not in (start, goal)}
        grid = Grid(SIZE, SIZE, blocked)
        if reachable(grid, start, goal):
            return grid


def pick_obstacle(rng, grid, planner, path):
    """A cell to block: on the path with prob. ON_PATH, else random free."""
    for _ in range(200):
        if rng.random() < ON_PATH and path is not None and len(path) > 2:
            c = path[int(rng.integers(1, len(path) - 1))]
            on_path = 1
        else:
            free = [s for s in grid.free_cells() if s not in (planner.start, planner.goal)]
            c = free[int(rng.integers(len(free)))]
            on_path = 1 if (path is not None and c in path) else 0
        grid.set_blocked(c)
        if reachable(grid, planner.start, planner.goal):
            return c, on_path
        grid.set_blocked(c, False)
    raise RuntimeError("could not place an obstacle")


def timed(fn):
    t0 = time.perf_counter()
    result = fn()
    return result, 1000.0 * (time.perf_counter() - t0)


def run(seed):
    rng = np.random.default_rng(seed)
    start, goal = (0, SIZE - 1), (SIZE - 1, 0)
    grid = random_grid(rng, start, goal)
    planner = DStarLite(grid, start, goal)
    rows = []
    n, dsl_ms = timed(planner.compute_shortest_path)
    a, astar_ms = timed(lambda: astar(grid, start, goal))
    ag, astarg_ms = timed(lambda: astar(grid, start, goal, tie="g"))
    assert a.cost == planner.g_of(start)
    rows.append((0, n, a.expansions, ag.expansions, dsl_ms, astar_ms, astarg_ms, 0, a.cost))
    for event in range(1, EVENTS + 1):
        planner.move()
        path = planner.path()
        c, on_path = pick_obstacle(rng, grid, planner, path)
        n, dsl_ms = timed(lambda: planner.notify_changed_cells([c]))
        a, astar_ms = timed(lambda: astar(grid, planner.start, goal))
        ag, astarg_ms = timed(lambda: astar(grid, planner.start, goal, tie="g"))
        assert a.cost == planner.g_of(planner.start), (seed, event)
        rows.append((event, n, a.expansions, ag.expansions, dsl_ms, astar_ms, astarg_ms,
                     on_path, a.cost))
    return np.array(rows, dtype=float)


def main():
    runs = [run(SEED + s) for s in range(SEEDS)]
    mean = np.mean(np.stack(runs), axis=0)
    dsl_cum = np.cumsum(mean[:, 1])
    astar_cum = np.cumsum(mean[:, 2])
    with open(OUT, "w") as f:
        f.write("event dsl_exp astar_exp astarg_exp dsl_ms astar_ms astarg_ms "
                "dsl_cum astar_cum onpath cost\n")
        for i, row in enumerate(mean):
            f.write("%d %.1f %.1f %.1f %.3f %.3f %.3f %.1f %.1f %.2f %.1f\n"
                    % (row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                       dsl_cum[i], astar_cum[i], row[7], row[8]))
    print("wrote", os.path.normpath(OUT))
    ev = mean[1:]
    print("initial search (event 0): D* Lite %.0f expansions %.1f ms; A* %.0f exp %.1f ms; "
          "A* ties toward smaller g %.0f exp %.1f ms"
          % (mean[0, 1], mean[0, 4], mean[0, 2], mean[0, 5], mean[0, 3], mean[0, 6]))
    print("events 1..%d totals: D* Lite %.0f expansions %.1f ms; A* %.0f expansions %.1f ms; "
          "A* (g ties) %.0f expansions %.1f ms"
          % (EVENTS, ev[:, 1].sum(), ev[:, 4].sum(), ev[:, 2].sum(), ev[:, 5].sum(),
             ev[:, 3].sum(), ev[:, 6].sum()))
    print("ratios A*/D* Lite over events 1..%d: expansions %.1f, time %.1f"
          % (EVENTS, ev[:, 2].sum() / ev[:, 1].sum(), ev[:, 5].sum() / ev[:, 4].sum()))
    print("whole run 0..%d: D* Lite %.0f expansions %.1f ms; A* %.0f expansions %.1f ms"
          % (EVENTS, mean[:, 1].sum(), mean[:, 4].sum(), mean[:, 2].sum(), mean[:, 5].sum()))
    crossing = next((int(mean[i, 0]) for i in range(len(mean)) if dsl_cum[i] < astar_cum[i]), None)
    print("cumulative expansions of D* Lite fall below A*'s at event", crossing)
    on = ev[ev[:, 7] >= 0.5]
    off = ev[ev[:, 7] < 0.5]
    print("events mostly on the path: %d, mean D* Lite %.1f vs A* %.1f expansions"
          % (len(on), on[:, 1].mean(), on[:, 2].mean()))
    print("events mostly off the path: %d, mean D* Lite %.1f vs A* %.1f expansions"
          % (len(off), off[:, 1].mean(), off[:, 2].mean()))
    print("per-event ranges: D* Lite %.1f..%.1f, A* %.1f..%.1f, A* (g ties) %.1f..%.1f"
          % (ev[:, 1].min(), ev[:, 1].max(), ev[:, 2].min(), ev[:, 2].max(),
             ev[:, 3].min(), ev[:, 3].max()))
    rows = np.concatenate([r[1:] for r in runs])
    on, off = rows[rows[:, 7] == 1], rows[rows[:, 7] == 0]
    print("per (grid, event): %d on-path events, D* Lite mean %.1f median %.0f max %.0f vs A* %.1f;"
          % (len(on), on[:, 1].mean(), np.median(on[:, 1]), on[:, 1].max(), on[:, 2].mean()))
    print("                   %d off-path events, D* Lite mean %.1f median %.0f max %.0f "
          "(zero in %.0f%% of them) vs A* %.1f"
          % (len(off), off[:, 1].mean(), np.median(off[:, 1]), off[:, 1].max(),
             100.0 * np.mean(off[:, 1] == 0), off[:, 2].mean()))
    print("per-expansion time [us]: D* Lite %.1f, A* %.1f"
          % (1000 * mean[:, 4].sum() / mean[:, 1].sum(), 1000 * mean[:, 5].sum() / mean[:, 2].sum()))


if __name__ == "__main__":
    main()
