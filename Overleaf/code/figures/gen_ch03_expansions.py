"""Generate figures/data/ch03-expansions.dat: settled cells vs grid size.

For every grid size n in SIZES, INSTANCES random n x n grids with obstacle
density DENSITY are drawn (NumPy RNG, fixed seed); the source is the top-left
and the target the bottom-right cell (instances where the target is not
reachable are redrawn).  Dijkstra runs twice on each grid: once without a
target (every reachable cell is settled) and once with the early exit.

Columns (whitespace separated, one header row, means over the instances):
    size            n (the grid is n x n cells, 8-connected, octile costs)
    cells           n * n
    free            number of free (non-obstacle) cells
    dijkstra_full   cells settled by Dijkstra without a target
    dijkstra_early  cells settled by Dijkstra with the early exit at the target
    cost            cost of the optimal path from source to target
    dijkstra_mid    cells settled with the early exit at the centre cell (n//2, n//2)
    cost_mid        cost of the optimal path from the source to the centre cell

Chapter 4 reuses this format and appends columns such as astar_octile for
the same instances (same seed, same generator settings).  Run from Overleaf/:

    python3 code/figures/gen_ch03_expansions.py
"""

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from ch03_dijkstra import GridGraph, dijkstra  # noqa: E402

SIZES = list(range(10, 101, 10))
INSTANCES = 10
DENSITY = 0.25
SEED = 3
CONNECTIVITY = 8
OUT = os.path.join(os.path.dirname(HERE), "..", "figures", "data", "ch03-expansions.dat")


class CountingGraph:
    """Counts how many nodes had their successors generated (expansions)."""

    def __init__(self, graph):
        self.graph = graph
        self.expanded = 0

    def __getitem__(self, u):
        self.expanded += 1
        return self.graph[u]


def random_grid(rng, n):
    cells = (rng.random((n, n)) < DENSITY).astype(int)
    cells[0, 0] = 0
    cells[n - 1, n - 1] = 0
    cells[n // 2, n // 2] = 0
    return cells.tolist()


def main():
    rng = np.random.default_rng(SEED)
    rows = []
    for n in SIZES:
        stats = []
        while len(stats) < INSTANCES:
            cells = random_grid(rng, n)
            grid = GridGraph(cells, CONNECTIVITY)
            source, target, mid = (0, 0), (n - 1, n - 1), (n // 2, n // 2)
            full = CountingGraph(grid)
            dist, _ = dijkstra(full, source)
            if target not in dist or mid not in dist:
                continue                       # unreachable: draw again
            early = CountingGraph(grid)
            edist, _ = dijkstra(early, source, target)
            centre = CountingGraph(grid)
            mdist, _ = dijkstra(centre, source, mid)
            free = sum(row.count(0) for row in cells)
            # with the early exit the target is settled but not expanded
            stats.append((free, full.expanded, early.expanded + 1, edist[target],
                          centre.expanded + 1, mdist[mid]))
        mean = np.mean(np.array(stats, dtype=float), axis=0)
        rows.append((n, n * n) + tuple(mean))
        print("n=%3d free=%8.1f full=%8.1f early=%8.1f cost=%7.2f mid=%8.1f cost_mid=%7.2f"
              % ((n,) + tuple(mean)))
    with open(OUT, "w") as f:
        f.write("size cells free dijkstra_full dijkstra_early cost dijkstra_mid cost_mid\n")
        for row in rows:
            f.write("%d %d %.1f %.1f %.1f %.3f %.1f %.3f\n" % row)
    print("wrote", os.path.normpath(OUT))


if __name__ == "__main__":
    main()
