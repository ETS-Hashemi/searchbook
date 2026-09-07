#!/usr/bin/env python3
"""Sizes of the joint state space for Chapter 11.

Writes figures/data/ch11-state-space.dat with, for k = 1..20 agents, the
number of joint configurations |V|^k on maps with |V| = 16, 54 and 400 free
cells (a 4x4 map, an 8x8 map with 15 % obstacles, a 20x20 map), the number
of collision-free configurations |V|(|V|-1)...(|V|-k+1) for |V| = 54, and
the number of joint moves 5^k of a 4-connected grid with a wait action.
Also prints the rows of the table in the chapter.  No randomness.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from ch11_mstar import joint_state_counts  # noqa: E402

OUT = os.path.join(HERE, "..", "..", "figures", "data", "ch11-state-space.dat")
SIZES = (16, 54, 400)


def main():
    rows = []
    for k in range(1, 21):
        total16, _, moves = joint_state_counts(SIZES[0], k)
        total54, free54, _ = joint_state_counts(SIZES[1], k)
        total400, _, _ = joint_state_counts(SIZES[2], k)
        rows.append([k, float(total16), float(total54), float(free54),
                     float(total400), float(moves)])
    header = "k states16 states54 free54 states400 moves"
    np.savetxt(OUT, np.array(rows), fmt=["%d", "%.4e", "%.4e", "%.4e", "%.4e", "%.4e"],
               header=header, comments="")
    print("wrote", os.path.normpath(OUT))
    print("table rows (k, 54^k, collision-free, 5^k, 400^k):")
    for k in (1, 2, 3, 4, 5, 8, 10, 20):
        total54, free54, moves = joint_state_counts(SIZES[1], k)
        total400 = joint_state_counts(SIZES[2], k)[0]
        print("k=%2d  54^k=%.2e  free=%.2e  5^k=%.2e  400^k=%.2e" % (
            k, total54, free54, moves, total400))


if __name__ == "__main__":
    main()
