"""Generate the data files of the simulation figures of Chapter 13.

Scenarios (code/ch13_orca.py; deterministic: the only randomness is the
fixed-seed perturbation that breaks the symmetry of the circle instance):

  circle   8 agents of radius 0.5 evenly spaced on a circle of radius 10,
           each heading for the antipodal point at nominal speed 1 (speed
           limit 1.5), tau = 5, dt = 0.1, 300 steps; every preferred
           velocity is offset by a fixed vector of length 0.02 (seed 13).
           Run with no avoidance, sampled VO, sampled RVO and ORCA.
  dance    two agents swapping places head-on, B offset laterally by 0.5,
           tau = 5, dt = 0.1, 100 steps, with sampled VO, sampled RVO and
           ORCA; plus sampled RVO with offset 0.1 (the reciprocal dance).

Files written (whitespace separated, one header row):
  figures/data/ch13-circle-<mode>.dat  for mode in none, vo, rvo, orca:
        t x0 y0 ... x7 y7    positions of the eight agents, every 2nd step
  figures/data/ch13-circle-separation.dat
        t none vo rvo orca   smallest centre distance over all pairs
  figures/data/ch13-dance.dat
        t <m>_ax <m>_ay <m>_bx <m>_by <m>_vy  for m in vo, rvo, orca
        (positions of A and B, lateral velocity of A), and rvo01_vy
        (lateral velocity of A with RVO at offset 0.1)
The summary numbers quoted in the chapter are printed to stdout.

Run from Overleaf/:   python3 code/figures/gen_ch13_circle.py
"""
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from ch13_orca import (circle_perturbation, circle_scenario,  # noqa: E402
                       dance_scenario, path_lengths, reversals, simulate,
                       velocity_variation)

DATA = os.path.normpath(os.path.join(os.path.dirname(HERE), "..", "figures",
                                     "data"))
TAU, DT, STEPS = 5.0, 0.1, 300


def write_table(name, header, rows):
    path = os.path.join(DATA, name)
    with open(path, "w") as f:
        f.write(" ".join(header) + "\n")
        for row in rows:
            f.write(" ".join("{:.4f}".format(x) for x in row) + "\n")
    print("wrote", path)


def main():
    os.makedirs(DATA, exist_ok=True)
    pert = circle_perturbation()
    results = {}
    print("circle scenario: 8 agents, tau = %.0f, dt = %.1f, %d steps"
          % (TAU, DT, STEPS))
    print("%-5s %6s %6s %8s %7s %7s %8s %6s %6s %6s"
          % ("mode", "csteps", "cpairs", "min_sep", "at_t", "arr_max",
             "len_mean", "rev0", "var0", "sec"))
    for mode in ("none", "vo", "rvo", "orca"):
        t0 = time.time()
        res = simulate(circle_scenario(), mode, tau=TAU, dt=DT, steps=STEPS,
                       perturbation=pert)
        sec = time.time() - t0
        results[mode] = res
        ms = res["min_separation"]
        print("%-5s %6d %6d %8.3f %7.1f %7.1f %8.2f %6d %6.2f %6.2f"
              % (mode, res["collision_steps"], res["collision_pairs"],
                 ms.min(), ms.argmin() * DT, np.nanmax(res["arrival"]),
                 path_lengths(res).mean(), reversals(res, 0),
                 velocity_variation(res, 0), sec))
        if mode == "orca":
            print("      infeasible steps:", res["infeasible_steps"])
        pos = res["positions"][::2]
        n = pos.shape[1]
        header = ["t"] + ["x%d y%d" % (i, i) for i in range(n)]
        rows = [[k * 2 * DT] + [c for i in range(n)
                                for c in (pos[k, i, 0], pos[k, i, 1])]
                for k in range(len(pos))]
        write_table("ch13-circle-%s.dat" % mode, " ".join(header).split(),
                    rows)
    t = np.arange(STEPS + 1) * DT
    rows = [[t[k]] + [results[m]["min_separation"][k]
                      for m in ("none", "vo", "rvo", "orca")]
            for k in range(STEPS + 1)]
    write_table("ch13-circle-separation.dat",
                ["t", "none", "vo", "rvo", "orca"], rows)

    print("dance scenario: two agents head-on, offset 0.5, tau = %.0f" % TAU)
    dance = {}
    for mode in ("vo", "rvo", "orca"):
        res = simulate(dance_scenario(offset=0.5), mode, tau=TAU, dt=DT,
                       steps=100)
        dance[mode] = res
        print("  %-4s reversals(A) = %3d  velocity variation(A) = %5.2f  "
              "min sep = %.3f  collisions = %d  arrival = %s"
              % (mode, reversals(res, 0), velocity_variation(res, 0),
                 res["min_separation"].min(), res["collision_steps"],
                 np.round(res["arrival"], 1)))
    res01 = simulate(dance_scenario(offset=0.1), "rvo", tau=TAU, dt=DT,
                     steps=100)
    vy = res01["velocities"][:, 0, 1]
    flips = int((np.sign(vy[1:]) * np.sign(vy[:-1]) < 0).sum())
    print("  rvo, offset 0.1: reversals(A) = %d  variation(A) = %.2f  "
          "sign changes of v_y(A) = %d  min sep = %.3f  collisions = %d"
          % (reversals(res01, 0), velocity_variation(res01, 0), flips,
             res01["min_separation"].min(), res01["collision_steps"]))
    header = ["t"]
    for m in ("vo", "rvo", "orca"):
        header += [m + "_ax", m + "_ay", m + "_bx", m + "_by", m + "_vy"]
    header.append("rvo01_vy")
    rows = []
    for k in range(101):
        row = [k * DT]
        for m in ("vo", "rvo", "orca"):
            p, v = dance[m]["positions"][k], dance[m]["velocities"][k]
            row += [p[0, 0], p[0, 1], p[1, 0], p[1, 1], v[0, 1]]
        row.append(vy[k])
        rows.append(row)
    write_table("ch13-dance.dat", header, rows)


if __name__ == "__main__":
    main()
