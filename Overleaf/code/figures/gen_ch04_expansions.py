"""Generate figures/data/ch04-expansions.dat: expansions of Dijkstra, A* and
weighted A* on random grids of growing size.

For every grid size n in SIZES, INSTANCES random n x n grids with obstacle
density DENSITY are drawn (NumPy RNG, fixed seed).  The start is the
bottom-left cell (0, 0) and the goal the top-right cell (n-1, n-1);
instances where the goal is not reachable on the 4-connected grid are
redrawn.  On each instance the following searches run (code/ch04_astar.py,
tie-breaking: larger g first):

    4-connected, unit costs : Dijkstra (h = 0), A* with the Manhattan
                              heuristic, weighted A* (Manhattan) with
                              w = 1.5 and w = 2
    8-connected, octile costs: Dijkstra (h = 0), A* with the octile
                              heuristic, weighted A* (octile) w = 1.5, 2

Columns (whitespace separated, one header row, means over the instances):
    size, cells, free      n, n*n, number of free cells
    dijkstra4, astar_manh  expansions (nodes popped from Open, goal included)
    wastar_m15, wastar_m20 expansions of weighted A* (Manhattan), w = 1.5, 2
    dijkstra8, astar_oct   expansions on the 8-connected grid
    wastar_o15, wastar_o20 expansions of weighted A* (octile), w = 1.5, 2
    ratio_m15, ratio_m20   mean (cost of weighted A* path) / (optimal cost)
    ratio_o15, ratio_o20   the same on the 8-connected grid

Run from Overleaf/:   python3 code/figures/gen_ch04_expansions.py
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from ch04_astar import astar_grid, dijkstra_grid  # noqa: E402

SIZES = list(range(10, 101, 10))
INSTANCES = 10
DENSITY = 0.25
SEED = 4
OUT = os.path.join(os.path.dirname(HERE), "..", "figures", "data", "ch04-expansions.dat")

COLUMNS = ("size cells free dijkstra4 astar_manh wastar_m15 wastar_m20 "
           "dijkstra8 astar_oct wastar_o15 wastar_o20 "
           "ratio_m15 ratio_m20 ratio_o15 ratio_o20")


def random_grid(rng, n):
    """n x n occupancy grid, grid[y, x], corners kept free."""
    grid = (rng.random((n, n)) < DENSITY).astype(int)
    grid[0, 0] = 0
    grid[n - 1, n - 1] = 0
    return grid


def main():
    rng = np.random.default_rng(SEED)
    rows = []
    for n in SIZES:
        stats = []
        while len(stats) < INSTANCES:
            grid = random_grid(rng, n)
            s, z = (0, 0), (n - 1, n - 1)
            dist4 = dijkstra_grid(grid, s, 4)
            if z not in dist4:
                continue                              # unreachable: draw again
            opt4, opt8 = dist4[z], dijkstra_grid(grid, s, 8)[z]
            d4 = astar_grid(grid, s, z, "zero", 4)
            a4 = astar_grid(grid, s, z, "manhattan", 4)
            w415 = astar_grid(grid, s, z, "manhattan", 4, weight=1.5)
            w420 = astar_grid(grid, s, z, "manhattan", 4, weight=2.0)
            d8 = astar_grid(grid, s, z, "zero", 8)
            a8 = astar_grid(grid, s, z, "octile", 8)
            w815 = astar_grid(grid, s, z, "octile", 8, weight=1.5)
            w820 = astar_grid(grid, s, z, "octile", 8, weight=2.0)
            assert abs(a4.cost - opt4) < 1e-9 and abs(a8.cost - opt8) < 1e-9
            stats.append((int(np.sum(grid == 0)),
                          d4.num_expansions, a4.num_expansions,
                          w415.num_expansions, w420.num_expansions,
                          d8.num_expansions, a8.num_expansions,
                          w815.num_expansions, w820.num_expansions,
                          w415.cost / opt4, w420.cost / opt4,
                          w815.cost / opt8, w820.cost / opt8))
        mean = np.mean(np.array(stats, dtype=float), axis=0)
        rows.append((n, n * n) + tuple(mean))
        print("n=%3d free=%7.1f dij4=%7.1f A*m=%7.1f w1.5=%6.1f w2=%6.1f | "
              "dij8=%7.1f A*o=%7.1f w1.5=%6.1f w2=%6.1f | ratios %.3f %.3f %.3f %.3f"
              % ((n,) + tuple(mean)))
    with open(OUT, "w") as f:
        f.write(COLUMNS + "\n")
        for row in rows:
            f.write("%d %d " % row[:2] + " ".join("%.1f" % v for v in row[2:11])
                    + " " + " ".join("%.4f" % v for v in row[11:]) + "\n")
    print("wrote", os.path.normpath(OUT))


if __name__ == "__main__":
    main()
