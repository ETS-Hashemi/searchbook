"""Generate figures/data/ch06-anytime.dat: ARA* versus restarted weighted A*.

INSTANCES random SIZE x SIZE grids (8-connected, octile costs, obstacle
density DENSITY, NumPy RNG with a fixed seed; unsolvable instances are
redrawn).  On every grid two anytime planners run through the same
schedule of inflation factors eps_1 > eps_2 > ... > eps_K = 1:

* ARA* (one search that keeps OPEN and INCONS between iterations), and
* "restart": weighted A* run from scratch at every eps of the schedule.

Both publish one path per iteration.  Columns (whitespace separated, one
header row; every value is a mean over the instances):
    iteration       k = 1..K
    eps             inflation factor eps_k of the iteration
    ara_ratio       cost of the ARA* path / optimal cost C*
    ara_bound       published bound eps' of ARA* (cost <= eps' C*)
    ara_exp         expansions of ARA* in this iteration
    ara_cum         cumulative expansions of ARA* after this iteration
    restart_ratio   cost of the restarted weighted A* path / C*
    restart_exp     expansions of weighted A* at eps_k (from scratch)
    restart_cum     cumulative expansions of the restarts after iteration k
    astar_exp       expansions of a single optimal A* run (eps = 1)

Run from Overleaf/:   python3 code/figures/gen_ch06_anytime.py
"""

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from ch06_arastar import ARAStar, astar_reference, random_grid, weighted_astar  # noqa: E402

SIZE = 60
DENSITY = 0.32
INSTANCES = 25
SEED = 6
SCHEDULE = (3.0, 2.5, 2.0, 1.75, 1.5, 1.25, 1.1, 1.0)
OUT = os.path.join(os.path.dirname(HERE), "..", "figures", "data", "ch06-anytime.dat")


def main():
    rng = np.random.default_rng(SEED)
    K = len(SCHEDULE)
    acc = np.zeros((K, 8))
    done = 0
    while done < INSTANCES:
        start, goal = (0, 0), (SIZE - 1, SIZE - 1)
        grid = random_grid(rng, SIZE, SIZE, DENSITY, 8, start, goal)
        c_star, n_astar = astar_reference(grid, start, goal)
        if c_star == np.inf:
            continue                              # unreachable: draw again
        ara = list(ARAStar(grid, start, goal, SCHEDULE, stop_when_optimal=False).run())
        assert len(ara) == K
        cum = 0
        for k, eps in enumerate(SCHEDULE):
            wa = weighted_astar(grid, start, goal, eps)
            cum += wa.expansions
            acc[k] += (ara[k].cost / c_star, ara[k].eps_bound, ara[k].expansions,
                       ara[k].total_expansions, wa.cost / c_star, wa.expansions,
                       cum, n_astar)
        done += 1
    mean = acc / INSTANCES
    with open(OUT, "w") as f:
        f.write("iteration eps ara_ratio ara_bound ara_exp ara_cum "
                "restart_ratio restart_exp restart_cum astar_exp\n")
        for k, eps in enumerate(SCHEDULE):
            f.write("%d %.2f %.4f %.4f %.1f %.1f %.4f %.1f %.1f %.1f\n"
                    % ((k + 1, eps) + tuple(mean[k])))
            print("k=%d eps=%.2f ara: ratio=%.4f bound=%.3f exp=%7.1f cum=%7.1f | "
                  "restart: ratio=%.4f exp=%7.1f cum=%7.1f | A*=%7.1f"
                  % ((k + 1, eps) + tuple(mean[k])))
    print("wrote", os.path.normpath(OUT))


if __name__ == "__main__":
    main()
