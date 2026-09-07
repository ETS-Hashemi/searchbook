#!/usr/bin/env python3
"""Effort of joint A*, operator decomposition, independence detection and
M* on random 8x8 maps with 15 % obstacles, for k = 2..6 agents.

Writes figures/data/ch11-expansions.dat with one row per k: how many of the
instances each method solved within the cap on generated successors, and,
over the instances solved by all four methods, the mean and the median of
the number of expansions and of generated successor candidates per method,
the mean running time, the mean size of the largest coupled group of
independence detection and of the largest collision set of M*.  Fixed seed.
"""
import os
import random
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from ch11_mstar import (independence_detection, joint_astar, mstar,   # noqa: E402
                        random_instance)

OUT = os.path.join(HERE, "..", "..", "figures", "data", "ch11-expansions.dat")
SIZE, DENSITY, TRIALS, CAP = 8, 0.15, 30, 1_500_000
KS = (2, 3, 4, 5, 6)
NAMES = ("astar", "od", "id", "mstar")


def main():
    rng = random.Random(2011)
    rows = []
    t_start = time.perf_counter()
    for k in KS:
        results = {name: [] for name in NAMES}
        ok = {name: 0 for name in NAMES}
        groups, csets = [], []
        for _ in range(TRIALS):
            inst, _ = random_instance(rng, SIZE, SIZE, k, DENSITY)
            runs = (joint_astar(inst, max_generated=CAP),
                    joint_astar(inst, operator_decomposition=True, max_generated=CAP),
                    independence_detection(inst, max_generated=CAP),
                    mstar(inst, max_generated=CAP))
            for name, r in zip(NAMES, runs):
                ok[name] += int(r.solved)
            if not all(r.solved for r in runs):
                continue
            assert len({r.cost for r in runs}) == 1
            for name, r in zip(NAMES, runs):
                results[name].append((r.expansions, r.generated, r.seconds))
            groups.append(runs[2].info["largest_group"])
            csets.append(runs[3].info["max_collision_set"])
        row = [k, len(groups)] + [ok[name] for name in NAMES]
        for name in NAMES:
            arr = np.array(results[name], dtype=float)
            row += [arr[:, 0].mean(), np.median(arr[:, 0]), arr[:, 1].mean(),
                    np.median(arr[:, 1]), arr[:, 2].mean()]
        row += [np.mean(groups), np.mean(csets)]
        rows.append(row)
        print("k=%d all=%2d/%d ok=%s" % (k, len(groups), TRIALS,
                                        [ok[name] for name in NAMES]))
        for i, name in enumerate(NAMES):
            e_mean, e_med, g_mean, g_med, sec = row[6 + 5 * i: 11 + 5 * i]
            print("   %-6s exp mean %8.1f med %6.0f | gen mean %10.0f med %8.0f | %.3f s"
                  % (name, e_mean, e_med, g_mean, g_med, sec))
        print("   largest ID group %.2f, largest M* collision set %.2f  (%.0f s elapsed)"
              % (row[-2], row[-1], time.perf_counter() - t_start))
    header = ("k all astar_ok od_ok id_ok mstar_ok "
              + " ".join("%s_exp %s_expmed %s_gen %s_genmed %s_sec" % ((n,) * 5) for n in NAMES)
              + " id_group mstar_cset")
    fmt = ["%d"] * 6 + ["%.3f"] * 22
    np.savetxt(OUT, np.array(rows), fmt=fmt, header=header, comments="")
    print("wrote", os.path.normpath(OUT))


if __name__ == "__main__":
    main()
