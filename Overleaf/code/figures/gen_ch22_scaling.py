"""Generate figures/data/ch22-scaling.dat and ch22-scaling-horizon.dat:
solve time of the multi-vehicle MILP of Chapter 22 as a function of the
number of vehicles m and of the horizon length N.

For every (m, N) the crossing instance of code/ch22_milp.py (m vehicles
on a circle of radius 4 m around a 2 m x 2 m block, each flying to its
antipode, d_min = 1 m, dt = 0.5 s, minimum-fuel objective) is solved for
len(SEEDS) seeded start jitters with scipy.optimize.milp (HiGHS) under a
wall-clock limit of TIME_LIMIT seconds.

ch22-scaling.dat has one row per m and, for every N in HORIZONS, the columns
    bin{N}    number of binary variables
    var{N}    number of variables
    t{N}      mean solve time in seconds (a run that hits the limit counts
              with the limit, so this is a lower bound on the true mean)
    tmax{N}   largest solve time
    hit{N}    fraction of the runs that hit the time limit
    gap{N}    mean relative MIP gap reported at the end (0 when optimal)
    nodes{N}  mean number of branch-and-bound nodes
ch22-scaling-horizon.dat has one row per N and the columns t{m}, hit{m}.

Run from Overleaf/:   python3 code/figures/gen_ch22_scaling.py
"""
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from ch22_milp import crossing_instance, solve_instance  # noqa: E402

VEHICLES = (1, 2, 3, 4, 5, 6)
HORIZONS = (12, 16, 20, 24)
SEEDS = (0, 1)
TIME_LIMIT = 30.0
DATA = os.path.join(os.path.dirname(HERE), "..", "figures", "data")


def main() -> None:
    t_all = time.perf_counter()
    stats = {}
    for m in VEHICLES:
        for N in HORIZONS:
            times, hits, gaps, nodes, nbin, nvar = [], [], [], [], 0, 0
            for seed in SEEDS:
                inst = crossing_instance(m, N, seed=seed)
                _, sol = solve_instance(inst, time_limit=TIME_LIMIT)
                nbin, nvar = sol.n_bin, sol.n_var
                times.append(min(sol.solve_time, TIME_LIMIT))
                hits.append(1.0 if sol.status == 1 else 0.0)
                gaps.append(sol.gap if np.isfinite(sol.gap) else 1.0)
                nodes.append(sol.nodes)
                print("m=%d N=%2d seed=%d status=%d time=%6.2f s nodes=%6d gap=%.3f"
                      % (m, N, seed, sol.status, sol.solve_time, sol.nodes, sol.gap),
                      flush=True)
            stats[(m, N)] = (nbin, nvar, np.mean(times), np.max(times),
                             np.mean(hits), np.mean(gaps), np.mean(nodes))
    header = ["m"]
    for N in HORIZONS:
        header += ["bin%d" % N, "var%d" % N, "t%d" % N, "tmax%d" % N,
                   "hit%d" % N, "gap%d" % N, "nodes%d" % N]
    lines = [" ".join(header)]
    for m in VEHICLES:
        row = [str(m)]
        for N in HORIZONS:
            nbin, nvar, t, tmax, hit, gap, nd = stats[(m, N)]
            row += ["%d" % nbin, "%d" % nvar, "%.3f" % t, "%.3f" % tmax,
                    "%.2f" % hit, "%.4f" % gap, "%.1f" % nd]
        lines.append(" ".join(row))
    with open(os.path.join(DATA, "ch22-scaling.dat"), "w") as f:
        f.write("\n".join(lines) + "\n")
    header = ["N"] + ["t%d" % m for m in VEHICLES] + ["hit%d" % m for m in VEHICLES]
    lines = [" ".join(header)]
    for N in HORIZONS:
        row = [str(N)] + ["%.3f" % stats[(m, N)][2] for m in VEHICLES]
        row += ["%.2f" % stats[(m, N)][4] for m in VEHICLES]
        lines.append(" ".join(row))
    with open(os.path.join(DATA, "ch22-scaling-horizon.dat"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("done in %.0f s" % (time.perf_counter() - t_all))


if __name__ == "__main__":
    main()
