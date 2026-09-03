"""Generate figures/data/ch02-double-integrator.dat for Chapter 2.

A 1D double integrator with a_max = 1 m/s^2, v_max = 2 m/s and dt = 0.1 s
travels 10 m: accelerate, cruise, then brake as soon as the remaining
distance equals the stopping distance v^2 / (2 a_max).  Columns: t x v a.
Deterministic (no random numbers).  Run from anywhere:

    python3 code/figures/gen_ch02_double_integrator.py
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from ch02_toolbox import double_integrator_step, stopping_distance  # noqa: E402

OUT = os.path.join(HERE, "..", "..", "figures", "data", "ch02-double-integrator.dat")

A_MAX, V_MAX, DT, GOAL = 1.0, 2.0, 0.1, 10.0


def main():
    x = np.array([0.0, 0.0])            # (position, velocity)
    rows = []
    t = 0.0
    braking_started = None
    for _ in range(200):
        p, v = x
        remaining = GOAL - p
        if remaining <= stopping_distance(v, A_MAX) + 1e-9 and v > 0.0:
            a = -A_MAX                   # brake
            if braking_started is None:
                braking_started = t
        elif v < V_MAX - 1e-9:
            a = A_MAX                    # accelerate
        else:
            a = 0.0                      # cruise
        rows.append((t, p, v, a))
        if v <= 1e-9 and a < 0.0:
            break
        x = double_integrator_step(x, [a], DT, a_max=A_MAX, v_max=V_MAX)
        t = round(t + DT, 10)
        if x[1] <= 1e-9 and braking_started is not None:
            rows.append((t, x[0], x[1], 0.0))
            break
    rows = np.array(rows)
    with open(OUT, "w") as f:
        f.write("t x v a\n")
        for t, p, v, a in rows:
            f.write(f"{t:.2f} {p:.4f} {v:.4f} {a:.2f}\n")
    t_vmax = rows[np.argmax(rows[:, 2] >= V_MAX - 1e-9), 0]
    print(f"wrote {OUT} ({len(rows)} rows)")
    print(f"v_max reached at t = {t_vmax:.1f} s, x = {rows[rows[:, 0] == t_vmax, 1][0]:.3f} m")
    print(f"braking starts at t = {braking_started:.1f} s, "
          f"x = {rows[rows[:, 0] == braking_started, 1][0]:.3f} m, "
          f"stopping distance = {stopping_distance(V_MAX, A_MAX):.3f} m")
    print(f"stopped at t = {rows[-1, 0]:.1f} s, x = {rows[-1, 1]:.4f} m")


if __name__ == "__main__":
    main()
