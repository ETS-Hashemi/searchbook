"""Generate the data files of the simulation figures of Chapter 12.

Scenarios (code/ch12_velocity_obstacles.py; deterministic, the only
randomness is the fixed-seed perturbation of the circle instance):

  example   the worked example: A flies from (-5, 0) to (5, 0) at 1.0,
            B from (0, -5) to (0, 5) at 0.9, radii 0.5, tau = 5, dt = 0.1;
            A applies the sampled VO rule, B keeps its velocity.  Also run
            without avoidance.
  headon    two agents swapping places head-on (B offset by 0.2), both
            applying VO at once (the oscillation), and A only.
  stream    one VO agent crossing a picket line of k = 1..8 non-
            cooperative intruders (stream_scenario), with and without VO.
  circle    n = 2..8 agents on a circle of radius 6 heading for the
            antipodal points (every pair on a crossing course), without
            avoidance and with every agent applying VO; seed 12.

Files written (whitespace separated, one header row):
  figures/data/ch12-example-traj.dat
        t ax ay bx by avx avy sep_vo sep_none tc_pref
  figures/data/ch12-oscillation.dat
        t ax ay bx by avy bvy sep  (both avoid)  a1x a1y a1vy (A only)
  figures/data/ch12-crossing.dat   (one row per n = k = 2..8)
        n st_sep_none st_sep_vo st_ratio_vo st_time_vo st_infeasible
          ci_sep_none ci_sep_vo ci_ratio_vo ci_coll_vo ci_infeasible
The summary numbers quoted in the chapter are printed to stdout.

Run from Overleaf/:   python3 code/figures/gen_ch12_sim.py
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from ch12_velocity_obstacles import (circle_scenario,  # noqa: E402
                                     crossing_scenario, head_on_scenario,
                                     norm, simulate, stream_metrics, sub)

DATA = os.path.normpath(os.path.join(os.path.dirname(HERE), "..", "figures",
                                     "data"))
TAU, DT = 5.0, 0.1


def write(name, header, rows):
    path = os.path.join(DATA, name)
    with open(path, "w") as fh:
        fh.write(" ".join(header) + "\n")
        for row in rows:
            fh.write(" ".join("%.4f" % x if isinstance(x, float) else str(x)
                              for x in row) + "\n")
    print("wrote", path, "(%d rows)" % len(rows))


def example():
    tr = simulate(crossing_scenario(), dt=DT, steps=200, tau=TAU,
                  record_info=True)
    tr0 = simulate(crossing_scenario(avoid_a=False), dt=DT, steps=200, tau=TAU)
    sep, sep0 = tr.separations(), tr0.separations()
    rows = []
    for k in range(len(tr.times)):
        kv = min(k, len(tr.velocities) - 1)
        info = tr.infos[kv][0]
        tc = info["tc_pref"] if info is not None else float("inf")
        tc = min(tc, 99.0)
        s0 = sep0[k] if k < len(sep0) else sep0[-1]
        rows.append([tr.times[k], tr.positions[k, 0, 0], tr.positions[k, 0, 1],
                     tr.positions[k, 1, 0], tr.positions[k, 1, 1],
                     tr.velocities[kv, 0, 0], tr.velocities[kv, 0, 1],
                     float(sep[k]), float(s0), float(tc)])
    write("ch12-example-traj.dat",
          "t ax ay bx by avx avy sep_vo sep_none tc_pref".split(), rows)
    print("example: VO min sep %.4f at t=%.1f, none min sep %.4f, path A %.4f,"
          " finished %.1f s" % (sep.min(), tr.times[int(np.argmin(sep))],
                                sep0.min(), tr.path_lengths()[0], tr.times[-1]))


def headon():
    both = simulate(head_on_scenario(), dt=DT, steps=140, tau=TAU)
    ag = head_on_scenario()                 # A avoids, B does not
    ag[1].avoiding = False
    a_only = simulate(ag, dt=DT, steps=140, tau=TAU)
    sep = both.separations()
    rows = []
    n = min(len(both.times), len(a_only.times))
    for k in range(n):
        kv = min(k, len(both.velocities) - 1)
        kv1 = min(k, len(a_only.velocities) - 1)
        rows.append([both.times[k], both.positions[k, 0, 0], both.positions[k, 0, 1],
                     both.positions[k, 1, 0], both.positions[k, 1, 1],
                     both.velocities[kv, 0, 1], both.velocities[kv, 1, 1],
                     float(sep[k]), a_only.positions[k, 0, 0],
                     a_only.positions[k, 0, 1], a_only.velocities[kv1, 0, 1]])
    write("ch12-oscillation.dat",
          "t ax ay bx by avy bvy sep a1x a1y a1vy".split(), rows)
    vy = both.velocities[:, 0, 1]
    flips = int((np.sign(vy[1:]) * np.sign(vy[:-1]) < 0).sum())
    vy1 = a_only.velocities[:, 0, 1]
    flips1 = int((np.sign(vy1[1:]) * np.sign(vy1[:-1]) < 0).sum())
    print("head-on both: %d sign changes of v_Ay, min sep %.4f, path A %.4f,"
          " max |v_Ay| %.3f, finished %.1f s" % (
              flips, sep.min(), both.path_lengths()[0], np.abs(vy).max(),
              both.times[-1]))
    print("head-on A only: %d sign changes, min sep %.4f, path A %.4f,"
          " max |v_Ay| %.3f, finished %.1f s" % (
              flips1, a_only.min_separation(), a_only.path_lengths()[0],
              np.abs(vy1).max(), a_only.times[-1]))


def circle():
    rows = []
    for n in range(2, 9):
        res = {}
        for mode, avoiding in (("none", False), ("vo", True)):
            agents = circle_scenario(n, avoiding=avoiding)
            straight = np.array([norm(sub(a.goal, a.position)) for a in agents])
            tr = simulate(agents, dt=DT, steps=400, tau=TAU, record_info=True)
            seps = tr.separations()
            p = tr.positions
            coll = 0
            for i in range(n):
                for j in range(i + 1, n):
                    d = np.linalg.norm(p[:, i] - p[:, j], axis=1)
                    coll += int(d.min() < 1.0)
            infeasible = sum(1 for step in tr.infos for inf in step
                             if inf is not None and inf["n_feasible"] == 0)
            res[mode] = dict(sep=float(seps.min()), t=float(tr.times[int(np.argmin(seps))]),
                             ratio=float((tr.path_lengths() / straight).mean()),
                             coll=coll, time=float(tr.times[-1]), inf=infeasible,
                             done=all(a.done for a in agents))
        st = stream_metrics(n)
        st0 = stream_metrics(n, avoid_a=False)
        print("stream k=%d: none sep %.4f | VO sep %.4f at t=%.1f ratio %.3f time %.1f"
              " infeasible-steps %d" % (n, st0["min_sep"], st["min_sep"],
                                        st["t_min_sep"], st["path_ratio"],
                                        st["time"], st["infeasible"]))
        rows.append([n, st0["min_sep"], st["min_sep"], st["path_ratio"], st["time"],
                     st["infeasible"], res["none"]["sep"], res["vo"]["sep"],
                     res["vo"]["ratio"], res["vo"]["coll"], res["vo"]["inf"]])
        print("circle n=%d: none sep %.4f coll %d | VO sep %.4f at t=%.1f ratio %.3f"
              " coll %d time %.1f infeasible-steps %d finished %s" % (
                  n, res["none"]["sep"], res["none"]["coll"], res["vo"]["sep"],
                  res["vo"]["t"], res["vo"]["ratio"], res["vo"]["coll"],
                  res["vo"]["time"], res["vo"]["inf"], res["vo"]["done"]))
    write("ch12-crossing.dat",
          ("n st_sep_none st_sep_vo st_ratio_vo st_time_vo st_infeasible "
           "ci_sep_none ci_sep_vo ci_ratio_vo ci_coll_vo ci_infeasible").split(),
          rows)


if __name__ == "__main__":
    os.makedirs(DATA, exist_ok=True)
    example()
    headon()
    circle()
