"""Generate figures/data/ch22-example.dat and ch22-example-time.dat: the
two-vehicle worked example of Chapter 22 solved with scipy.optimize.milp,
once with the minimum-fuel objective and once with the minimum-time one.

Columns (whitespace separated, one header row):
    k t xA yA xB yB sep ax_A ay_A ax_B ay_B
sep is the infinity-norm distance between the vehicles at step k; the
inputs of step k act during [t_k, t_k + dt) and are 0 in the last row.

Run from Overleaf/:   python3 code/figures/gen_ch22_example.py
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from ch22_milp import check_solution, example_instance, solve_instance  # noqa: E402

DATA = os.path.join(os.path.dirname(HERE), "..", "figures", "data")


def main() -> None:
    for objective, name in (("fuel", "ch22-example.dat"),
                            ("time", "ch22-example-time.dat")):
        inst = example_instance(objective)
        model, sol = solve_instance(inst)
        assert sol.status == 0, sol.message
        assert all(v <= 1e-6 for v in check_solution(inst, sol).values())
        N = inst.horizon
        lines = ["k t xA yA xB yB sep ax_A ay_A ax_B ay_B"]
        for k in range(N + 1):
            pa, pb = sol.positions[0, k], sol.positions[1, k]
            ua = sol.inputs[0, k] if k < N else np.zeros(2)
            ub = sol.inputs[1, k] if k < N else np.zeros(2)
            lines.append("%d %.2f %.4f %.4f %.4f %.4f %.4f %.4f %.4f %.4f %.4f" % (
                k, k * inst.dt, pa[0], pa[1], pb[0], pb[1],
                np.abs(pa - pb).max(), ua[0], ua[1], ub[0], ub[1]))
        path = os.path.join(DATA, name)
        with open(path, "w") as f:
            f.write("\n".join(lines) + "\n")
        print("%s: objective %.4f, %d variables, %d binaries, %.2f s, wrote %s"
              % (objective, sol.objective, sol.n_var, sol.n_bin, sol.solve_time, path))


if __name__ == "__main__":
    main()
