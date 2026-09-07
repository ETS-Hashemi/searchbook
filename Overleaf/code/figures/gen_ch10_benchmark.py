"""Generate figures/data/ch10-benchmark.dat: CBS against ECBS(w) for
w = 1.1, 1.5 and 2.0 on random 8 x 8 grids with a growing number of agents.

For every number of agents k in AGENTS, INSTANCES random 8 x 8 grids with
obstacle density DENSITY are drawn (Python's random module, fixed seed;
NumPy is used only for the statistics).  Starts and goals are distinct
random free cells, redrawn until every agent can reach its goal.  Each
solver (code/ch10_ecbs.py) runs once per instance with a wall-clock limit
of TIME_LIMIT seconds and a limit of NODE_LIMIT expanded constraint-tree
nodes.

Columns (whitespace separated, one header row).  For each solver S in
cbs, e11, e15, e20 (CBS, ECBS with w = 1.1, 1.5, 2.0):
    k            number of agents
    S_success    fraction of the instances solved within the limits
    S_time       mean runtime in seconds; an unsolved run counts with the
                 time it used, which is the time limit (a lower bound)
    S_time_solved  mean runtime over the solved instances only
    S_nodes      mean number of expanded CT nodes over the solved instances
    S_lowexp     mean number of low-level state expansions (solved instances)
    S_ratio      mean of cost / optimal cost over the instances solved by
                 both S and CBS (nan if there is none)
    S_ratio_max  the largest such ratio
    S_bound      mean of cost / LB, the bound proven by the solver itself,
                 over the solved instances (1 for CBS)
    S_both       number of instances solved by both S and CBS

Run from Overleaf/:   python3 code/figures/gen_ch10_benchmark.py
"""
import os
import random
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from ch10_ecbs import cbs, ecbs, random_instance, validate  # noqa: E402

AGENTS = (2, 4, 6, 8, 10, 12, 14, 16)
INSTANCES = 10
ROWS = COLS = 8
DENSITY = 0.10
SEED = 10
TIME_LIMIT = 10.0
NODE_LIMIT = 50000
SOLVERS = (("cbs", None), ("e11", 1.1), ("e15", 1.5), ("e20", 2.0))
OUT = os.path.join(os.path.dirname(HERE), "..", "figures", "data",
                   "ch10-benchmark.dat")


def run(name, w, inst):
    if w is None:
        return cbs(inst, node_limit=NODE_LIMIT, time_limit=TIME_LIMIT)
    return ecbs(inst, w=w, node_limit=NODE_LIMIT, time_limit=TIME_LIMIT)


def mean(values):
    return float(np.mean(values)) if values else float("nan")


def main():
    rng = random.Random(SEED)
    header = ["k"]
    for name, _ in SOLVERS:
        header += [f"{name}_success", f"{name}_time", f"{name}_time_solved",
                   f"{name}_nodes", f"{name}_lowexp", f"{name}_ratio",
                   f"{name}_ratio_max", f"{name}_bound", f"{name}_both"]
    lines = [" ".join(header)]
    t_start = time.time()
    for k in AGENTS:
        instances = [random_instance(ROWS, COLS, k, rng, DENSITY)
                     for _ in range(INSTANCES)]
        results = {name: [run(name, w, inst) for inst in instances]
                   for name, w in SOLVERS}
        for name, res_list in results.items():
            for inst, res in zip(instances, res_list):
                if res.solved:
                    assert validate(inst, res.paths) == [], name
                    assert res.cost <= res.w * res.lower_bound + 1e-9
        opt = results["cbs"]
        row = [f"{k}"]
        for name, _ in SOLVERS:
            res_list = results[name]
            solved = [r for r in res_list if r.solved]
            both = [(r, o) for r, o in zip(res_list, opt) if r.solved and o.solved]
            ratios = [r.cost / o.cost for r, o in both]
            row += [f"{len(solved) / INSTANCES:.2f}",
                    f"{mean([r.runtime for r in res_list]):.4f}",
                    f"{mean([r.runtime for r in solved]):.4f}",
                    f"{mean([r.ct_expanded for r in solved]):.1f}",
                    f"{mean([r.low_level_expansions for r in solved]):.0f}",
                    f"{mean(ratios):.4f}",
                    f"{max(ratios) if ratios else float('nan'):.4f}",
                    f"{mean([r.cost / r.lower_bound for r in solved]):.4f}",
                    f"{len(both)}"]
        lines.append(" ".join(row))
        print(lines[-1], f"   [{time.time() - t_start:.0f} s]", flush=True)
    with open(OUT, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("wrote", os.path.normpath(OUT))


if __name__ == "__main__":
    main()
