"""Generate the data files of Chapter 15 (artificial potential fields).

Every number comes from code/ch15_potential_fields.py with its default gains
(k_att = 1, k_rep = 1, rho0 = 2, v_max = 1, dt = 0.01) and a fixed seed.
Files written into figures/data/ (whitespace separated, one header row):

    ch15-surface.dat        x y U      potential of the one-disc scene of the
                                       worked example, clipped at U = 40, on a
                                       36 x 36 grid (blank line after each row)
    ch15-field.dat          x y u v    unit force directions on a coarse grid
    ch15-example-traj.dat   x y        trajectory of the worked example, start (0, 4.5)
    ch15-localmin-traj.dat  x y        start (0, 4): stops at the local minimum
    ch15-localmin-waypoint.dat x y     the same start steered via waypoint (3, 6.5)
    ch15-localmin-profile.dat x Uatt Urep U   potentials along the axis y = 4
    ch15-gnron-plain.dat    t x y d    goal (5.4, 4) next to the disc, plain repulsion
    ch15-gnron-fixed.dat    t x y d    the same with the d^2 factor (n = 2)
    ch15-osc-smooth.dat     x y e      corridor of width 1.0, dt = 0.01, v_max = 1
    ch15-osc-zigzag.dat     x y e      dt = 0.05, no speed limit
    ch15-osc-crash.dat      x y e      dt = 0.10, no speed limit (hits the wall)
    ch15-nopassage-traj.dat x y        corridor of width 0.6: stops in front of it
    ch15-nopassage-profile.dat x Fx U  force along the axis and potential
    ch15-basin-reached.dat  x y        starts of the basin experiment that reach the goal
    ch15-basin-stuck.dat    x y        starts that end in the local minimum
    ch15-basin-traj.dat     x y        eleven trajectories, separated by nan rows
    ch15-basin-escape.dat   x y        one trapped start rescued by random-walk escapes
    ch15-swarm.dat          x y        six drones on a ring swapping places, with
                                       inter-agent repulsion (nan rows separate them)

Run from Overleaf/:   python3 code/figures/gen_ch15_field.py
"""
import os
import sys

import numpy as np
from dataclasses import replace

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from ch15_potential_fields import (  # noqa: E402
    ApfParams, BASIN_GOAL, BASIN_OBS, CORRIDOR_GOAL, DISC, GOAL, attractive_potential,
    basin_experiment, basin_starts, corridor, corridor_case, gnron_case,
    local_minimum_case, min_clearance, repulsive_potential, simulate, simulate_swarm,
    total_force, total_potential, worked_example)

OUT = os.path.join(os.path.dirname(HERE), "..", "figures", "data")
U_CLIP = 40.0


def write(name, header, rows):
    path = os.path.join(OUT, "ch15-%s.dat" % name)
    with open(path, "w") as fh:
        fh.write(header + "\n")
        for row in rows:
            if row is None:
                fh.write("\n")
            else:
                fh.write(" ".join("%.4f" % v if np.isfinite(v) else "nan" for v in row) + "\n")
    return path


def thin(path, every):
    """Every k-th point of a path plus its last point."""
    idx = list(range(0, len(path), every))
    if idx[-1] != len(path) - 1:
        idx.append(len(path) - 1)
    return np.asarray(path)[idx]


def main():
    os.makedirs(OUT, exist_ok=True)
    prm = ApfParams()

    # potential surface of the one-disc scene
    xs, ys = np.linspace(0.0, 9.0, 36), np.linspace(0.0, 8.0, 36)
    rows = []
    for y in ys:
        for x in xs:
            u = min(float(total_potential(np.array([x, y]), GOAL, DISC, prm)), U_CLIP)
            rows.append((x, y, u))
        rows.append(None)
    write("surface", "x y U", rows)

    # force directions on a coarse grid and the worked-example trajectory
    rows = []
    for y in np.arange(0.5, 7.76, 0.75):
        for x in np.arange(0.0, 9.01, 0.75):
            q = np.array([x, y])
            if min_clearance(q, DISC) < 0.15 or np.linalg.norm(q - GOAL) < 0.3:
                continue
            f = total_force(q, GOAL, DISC, prm)
            f = f / max(np.linalg.norm(f), 1e-12)
            rows.append((x, y, f[0], f[1]))
    write("field", "x y u v", rows)
    table, traj = worked_example(prm)
    write("example-traj", "x y", thin(traj["path"], 10))

    # failure 1: local minimum on the axis, and the waypoint remedy
    lm = local_minimum_case(prm)
    write("localmin-traj", "x y", thin(lm["result"]["path"], 5))
    write("localmin-waypoint", "x y", thin(lm["waypoint"]["path"], 10))
    rows = []
    for x in np.linspace(0.0, 8.0, 321):
        q = np.array([x, 4.0])
        if min_clearance(q, DISC) <= 0.02:
            rows.append((x, np.nan, np.nan, np.nan))
            continue
        ua = float(attractive_potential(q, GOAL, prm))
        ur = min(float(repulsive_potential(q, GOAL, DISC, prm)), U_CLIP)
        rows.append((x, ua, ur, min(ua + ur, U_CLIP)))
    write("localmin-profile", "x Uatt Urep U", rows)

    # failure 2: goal next to the obstacle (GNRON)
    g = gnron_case(prm)
    goal = np.array([5.4, 4.0])
    for name, res in (("plain", g["plain"]), ("fixed", g["fixed"])):
        path = res["path"]
        idx = list(range(0, len(path), 5)) + [len(path) - 1]
        rows = [(i * prm.dt, path[i, 0], path[i, 1], np.linalg.norm(path[i] - goal)) for i in idx]
        write("gnron-" + name, "t x y d", rows)

    # failure 3: oscillation in a passage of width 1.0
    runs = (("smooth", corridor_case(1.0, 0.01, prm), 10),
            ("zigzag", corridor_case(1.0, 0.05, prm, v_max=np.inf), 1),
            ("crash", corridor_case(1.0, 0.10, prm, v_max=np.inf), 1))
    for name, c, every in runs:
        path = thin(c["result"]["path"], every)
        write("osc-" + name, "x y e", [(x, y, y - 4.0) for x, y in path])

    # failure 4: no passage through a gap of width 0.6
    block = corridor_case(0.6, 0.01, prm)
    write("nopassage-traj", "x y", thin(block["result"]["path"], 5))
    obs = corridor(0.6)
    rows = []
    for x in np.linspace(0.0, 8.0, 321):
        q = np.array([x, 4.0])
        fx = float(total_force(q, CORRIDOR_GOAL, obs, prm)[0])
        u = min(float(total_potential(q, CORRIDOR_GOAL, obs, prm)), U_CLIP)
        rows.append((x, max(min(fx, 8.0), -8.0), u))
    write("nopassage-profile", "x Fx U", rows)

    # basin experiment: 441 starts, two overlapping discs (one peanut-shaped obstacle)
    starts = basin_starts()
    plain = basin_experiment(escape=False, prm=prm)
    walk = basin_experiment(escape=True, prm=prm)
    status = plain["status"]
    write("basin-reached", "x y", starts[status == "reached"])
    write("basin-stuck", "x y", starts[status != "reached"])
    rows = []
    for j in range(0, 21, 2):                      # the column x = 0, every other row
        i = j * 21
        path = plain["history"][: plain["steps"][i] + 1, i]
        rows.extend(tuple(q) for q in thin(path, 8))
        rows.append((np.nan, np.nan))
    write("basin-traj", "x y", rows)
    trapped = np.where(status != "reached")[0]
    pick = trapped[np.argmin(np.abs(starts[trapped, 1] - 4.1) + starts[trapped, 0])]
    esc = simulate(starts[pick], BASIN_GOAL, BASIN_OBS, prm, escape=True,
                   rng=np.random.default_rng(15))
    write("basin-escape", "x y", thin(esc["path"], 6))

    # swarm: six drones on a ring of radius 3 swap to the opposite points
    ang = np.linspace(0.0, 2 * np.pi, 6, endpoint=False)
    ring = np.stack([3 * np.cos(ang), 3 * np.sin(ang)], axis=1)
    sw = simulate_swarm(ring, -ring, [], replace(prm, dt=0.02), k_agent=1.0)
    rows = []
    for i in range(6):
        rows.extend(tuple(q) for q in thin(sw["history"][:, i], 10))
        rows.append((np.nan, np.nan))
    write("swarm", "x y", rows)
    print("swarm: min separation %.3f over %d steps" % (sw["min_separation"], len(sw["history"]) - 1))

    print("worked example forces:")
    for name, r in table.items():
        print("  %s p=%s rho=%.4f F_att=%s F_rep=%s F=%s |F|=%.4f U=%.4f" % (
            name, r["p"], r["rho"], np.round(r["f_att"], 4), np.round(r["f_rep"], 4),
            np.round(r["f"], 4), np.linalg.norm(r["f"]), r["u"]))
    print("  example trajectory: %s, %d steps, min clearance %.3f, path length %.3f" % (
        traj["status"], traj["steps"], traj["min_clearance"],
        np.sum(np.linalg.norm(np.diff(traj["path"], axis=0), axis=1))))
    print("local minimum at x=%.4f (root %.4f), stuck after %d steps; waypoint route %s, %d steps" % (
        lm["result"]["final"][0], lm["equilibrium_x"], lm["result"]["steps"],
        lm["waypoint"]["statuses"], len(lm["waypoint"]["path"]) - 1))
    print("GNRON: plain stops at %s, %.4f from goal (%s, %d steps); fixed %s in %d steps" % (
        np.round(g["plain"]["final"], 3), g["d_plain"], g["plain"]["status"], g["plain"]["steps"],
        g["fixed"]["status"], g["fixed"]["steps"]))
    for name, c, _ in runs:
        print("corridor %s: %s, %d steps, %d reversals, amplitude %.3f, clearance %.3f, stiffness %.1f" % (
            name, c["result"]["status"], c["result"]["steps"], c["reversals"], c["amplitude"],
            c["result"]["min_clearance"], c["stiffness"]))
    print("no passage: %s at %s after %d steps; stiffness %.1f" % (
        block["result"]["status"], np.round(block["result"]["final"], 3),
        block["result"]["steps"], block["stiffness"]))
    fx_axis = [float(total_force(np.array([x, 4.0]), CORRIDOR_GOAL, obs, prm)[0])
               for x in np.linspace(2.0, 4.0, 201)]
    print("  most negative F_x on the axis before the gap: %.3f" % min(fx_axis))
    for name, res in (("plain", plain), ("random walk", walk)):
        st = res["status"]
        reached = st == "reached"
        print("basin %s: %d/%d reached (%.1f%%), %d stuck, %d timeout, %d collision; "
              "mean steps of the reached %.0f; mean escapes %.2f" % (
                  name, reached.sum(), len(st), 100 * reached.mean(), (st == "stuck").sum(),
                  (st == "timeout").sum(), (st == "collision").sum(),
                  res["steps"][reached].mean(), res["escapes"].mean()))
    print("  trapped start used for the escape trajectory: %s -> %s after %d steps, %d escapes" % (
        starts[pick], esc["status"], esc["steps"], esc["escapes"]))
    stuck_final = plain["final"][status == "stuck"]
    if len(stuck_final):
        print("  stuck positions: x in [%.3f, %.3f], y in [%.3f, %.3f]" % (
            stuck_final[:, 0].min(), stuck_final[:, 0].max(),
            stuck_final[:, 1].min(), stuck_final[:, 1].max()))


if __name__ == "__main__":
    main()
