"""Generate figures/data/ch08-orders.dat for Chapter 8.

For k = 4, 8, ..., 32 agents on random 20x20 grids with 20% obstacles,
run prioritized planning (HCA*, true-distance heuristic) with four ways
of choosing the priority order: one random order, longest path first,
most constrained first, and random restarts (up to RESTARTS random
orders, keeping the cheapest plan).  Records the success rate of each
strategy and the mean sum of costs relative to the sum of the
independent shortest paths, over the instances that all four solve.
Fixed seed; NumPy only for the output.
"""
import os
import random
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from ch08_prioritized import (naive_paths, order_longest_first,  # noqa: E402
                              order_most_constrained_first, order_random, path_cost,
                              plan_with_restarts, prioritized_planning, random_instance,
                              sum_of_costs)

OUT = os.path.join(HERE, "..", "..", "figures", "data", "ch08-orders.dat")
ROWS, COLS, DENSITY, TRIALS, RESTARTS = 20, 20, 0.20, 30, 5
KS = list(range(4, 33, 4))
NAMES = ("random", "lpf", "mcf", "restart")


def main() -> None:
    rng = random.Random(8)
    rows = []
    for k in KS:
        succ = {n: 0 for n in NAMES}
        common = {n: [] for n in NAMES}
        for _ in range(TRIALS):
            inst = random_instance(ROWS, COLS, k, rng, DENSITY)
            lower = sum(path_cost(p) for p in naive_paths(inst))
            plans = {
                "random": prioritized_planning(inst, order_random(inst, rng), "true"),
                "lpf": prioritized_planning(inst, order_longest_first(inst), "true"),
                "mcf": prioritized_planning(inst, order_most_constrained_first(inst), "true"),
                "restart": plan_with_restarts(inst, rng, RESTARTS, "true"),
            }
            for n in NAMES:
                succ[n] += plans[n] is not None
            if all(p is not None for p in plans.values()):
                for n in NAMES:
                    common[n].append(sum_of_costs(plans[n]) / lower)
        n_common = len(common["random"])
        row = [k] + [succ[n] / TRIALS for n in NAMES]
        row += [float(np.mean(common[n])) if n_common else float("nan") for n in NAMES]
        row.append(n_common)
        rows.append(row)
        print("k=%2d success %s ratio %s common %d" % (
            k, " ".join("%.2f" % (succ[n] / TRIALS) for n in NAMES),
            " ".join("%.3f" % r for r in row[5:9]), n_common))
    header = ("k succ_random succ_lpf succ_mcf succ_restart "
              "soc_random soc_lpf soc_mcf soc_restart n_common")
    fmt = ["%d"] + ["%.3f"] * 8 + ["%d"]
    np.savetxt(OUT, np.array(rows), fmt=fmt, header=header, comments="")
    print("wrote", os.path.normpath(OUT))


if __name__ == "__main__":
    main()
