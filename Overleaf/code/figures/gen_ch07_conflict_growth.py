"""Generate figures/data/ch07-conflict-growth.dat for Chapter 7.

For k = 2, 4, ..., 40 agents on random 16x16 grids with 20% obstacles,
plan every agent independently (shortest path by BFS) and count the
vertex and swapping conflicts of the resulting naive plan.  Fixed seed.
"""
import os
import random
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from ch07_mapf import all_conflicts, naive_plan, random_instance  # noqa: E402

OUT = os.path.join(HERE, "..", "..", "figures", "data", "ch07-conflict-growth.dat")
ROWS, COLS, DENSITY, TRIALS = 16, 16, 0.20, 60


def main() -> None:
    rng = random.Random(7)
    rows = []
    for k in range(2, 41, 2):
        n_conf, n_vertex, n_swap, n_pairs, n_free = [], [], [], [], []
        for _ in range(TRIALS):
            inst = random_instance(ROWS, COLS, k, rng, DENSITY)
            found = all_conflicts(naive_plan(inst))
            n_conf.append(len(found))
            n_vertex.append(sum(c.kind == "vertex" for c in found))
            n_swap.append(sum(c.kind == "swap" for c in found))
            n_pairs.append(len({(c.i, c.j) for c in found}))
            n_free.append(0 if found else 1)
        rows.append([k, np.mean(n_conf), np.mean(n_vertex), np.mean(n_swap),
                     np.mean(n_pairs), np.mean(n_free)])
    header = "k conflicts_mean vertex_mean swap_mean pairs_mean free_frac"
    np.savetxt(OUT, np.array(rows), fmt=["%d", "%.3f", "%.3f", "%.3f", "%.3f", "%.3f"],
               header=header, comments="")
    print("wrote", os.path.normpath(OUT))
    for r in rows:
        print("k=%2d conflicts=%6.2f vertex=%6.2f swap=%5.2f pairs=%6.2f free=%.2f" % tuple(r))


if __name__ == "__main__":
    main()
