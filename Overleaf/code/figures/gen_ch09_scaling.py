"""Generate figures/data/ch09-scaling.dat: how CBS scales with the number
of agents on random 8 x 8 grids.

For every number of agents k in AGENTS, INSTANCES random grids with
obstacle density DENSITY are drawn (Python's random module with a fixed
seed; NumPy is used for the statistics only).  Starts and goals are
distinct random free cells, redrawn until every agent can reach its goal.
Two solvers from code/ch09_cbs.py run once per instance, each with a
wall-clock limit of TIME_LIMIT seconds and at most NODE_LIMIT expanded
constraint-tree (CT) nodes:

    cbs   plain CBS: split on the earliest conflict, ties on fewer conflicts
    icbs  CBS with cardinal conflicts first and the bypass (ICBS)

Columns (whitespace separated, one header row), for S in cbs, icbs:
    k            number of agents
    S_success    fraction of the instances solved within the limits
    S_nodes      mean number of expanded CT nodes over the solved instances
    S_nodes_max  largest number of expanded CT nodes over the solved instances
    S_lowexp     mean number of low-level state expansions (solved instances)
    S_time       mean runtime in seconds; an unsolved run counts with the
                 time it used, so this is a lower bound on the true mean
    S_conflicts  mean number of conflicts among the root's paths

Run from Overleaf/:   python3 code/figures/gen_ch09_scaling.py
"""
import os
import random
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from ch09_cbs import all_conflicts, cbs, random_instance, validate  # noqa: E402

AGENTS = (2, 4, 6, 8, 10, 12)
INSTANCES = 12
ROWS = COLS = 8
DENSITY = 0.15
SEED = 9
TIME_LIMIT = 5.0
NODE_LIMIT = 20000
SOLVERS = (("cbs", dict(split="first", bypass=False)),
           ("icbs", dict(split="cardinal", bypass=True)))
OUT = os.path.join(os.path.dirname(HERE), "..", "figures", "data",
                   "ch09-scaling.dat")


def main() -> None:
    rows = []
    t_all = time.perf_counter()
    for k in AGENTS:
        rng = random.Random(SEED + k)
        instances = [random_instance(COLS, ROWS, k, DENSITY, rng)
                     for _ in range(INSTANCES)]
        row = [k]
        for name, kw in SOLVERS:
            solved, nodes, lowexp, times, conflicts = [], [], [], [], []
            for grid, starts, goals in instances:
                res = cbs(grid, starts, goals, time_limit=TIME_LIMIT,
                          node_limit=NODE_LIMIT, **kw)
                ok = res.paths is not None
                if ok:
                    assert validate(res.paths, grid, starts, goals)
                    nodes.append(res.stats.expanded)
                    lowexp.append(res.stats.low_level_expanded)
                solved.append(ok)
                times.append(res.stats.seconds)
                if name == "cbs":
                    root = cbs(grid, starts, goals, node_limit=1)
                    conflicts.append(len(all_conflicts(root.trace[0]["paths"]))
                                     if root.trace else 0)
            row += [np.mean(solved),
                    np.mean(nodes) if nodes else float("nan"),
                    max(nodes) if nodes else float("nan"),
                    np.mean(lowexp) if lowexp else float("nan"),
                    np.mean(times)]
            print("k=%2d %-5s success %.2f  nodes %.1f (max %s)  time %.3f s"
                  % (k, name, row[-5], row[-4], row[-3], row[-1]), flush=True)
        rows.append(row)
    # the root-conflict count is computed once per k (it does not depend on
    # the solver); append it as the last column
    header = ["k"]
    for name, _ in SOLVERS:
        header += ["%s_success" % name, "%s_nodes" % name, "%s_nodes_max" % name,
                   "%s_lowexp" % name, "%s_time" % name]
    with open(OUT, "w") as fh:
        fh.write(" ".join(header) + "\n")
        for row in rows:
            fh.write("%d " % row[0] + " ".join(
                "%.4f" % v if isinstance(v, float) else str(v) for v in row[1:]) + "\n")
    print("wrote", os.path.normpath(OUT), "in %.0f s" % (time.perf_counter() - t_all))


if __name__ == "__main__":
    main()
