"""Generate the data of the EKF / UKF / particle-filter comparison of Chapter 19.

Writes (whitespace separated, one header row):
  figures/data/ch19-compare-track.dat   one baseline run: t x_true y_true meas_x meas_y
                                        ekf_x ekf_y ukf_x ukf_y pf_x pf_y
  figures/data/ch19-compare-error.dat   the same run: t err_meas err_ekf err_ukf err_pf
and prints the RMSE table of the chapter (mean position RMSE over RUNS Monte Carlo
runs per scenario, number of lost tracks, and the time per filter step).

Scenarios (all use the coordinated-turn model with sigma_a = 1.5 m/s^2 and
sigma_gamma = 0.3 rad/s^2, dt = 0.5 s, sensor at the origin, sigma_r = 3 m):
  baseline        sigma_phi = 2 deg
  wide bearing    sigma_phi = 8 deg
  close pass      sigma_phi = 2 deg, sensor at (35, -20): minimum range about 10 m
  poor start      sigma_phi = 2 deg, initial heading wrong by 90 deg with an
                  initial heading standard deviation of only 0.3 rad
The RMSE is computed after a settling period of 10 steps (5 s).
Fixed seeds.  Run from anywhere:   python3 code/figures/gen_ch19_compare.py
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from ch19_nonlinear_filters import (CoordinatedTurnModel, RangeBearingSensor, TURNING_DT,  # noqa: E402
                                    rmse, run_tracking, turning_target_truth)

DATA = os.path.join(HERE, "..", "..", "figures", "data")
RUNS = 100
N_PARTICLES = 2000
LOST_THRESHOLD = 30.0        # metres of final position error
SCENARIOS = [
    ("baseline ($\\sigma_\\varphi = 2^\\circ$)", dict(sigma_phi=math.radians(2.0))),
    ("wide bearing noise ($\\sigma_\\varphi = 8^\\circ$)", dict(sigma_phi=math.radians(8.0))),
    ("close pass (sensor at $(35, -20)$)", dict(sigma_phi=math.radians(2.0), pos=(35.0, -20.0))),
    ("poor initialisation ($90^\\circ$ heading error)",
     dict(sigma_phi=math.radians(2.0), init_error=(0.0, 0.0, 0.0, math.pi / 2, 0.0), init_heading_std=0.3)),
]


def main():
    truth = turning_target_truth()
    T = truth.shape[0]
    t = np.arange(T) * TURNING_DT
    motion = CoordinatedTurnModel(TURNING_DT, sigma_a=1.5, sigma_gamma=0.3)
    rows = []
    times = {"ekf": [], "ukf": [], "pf": []}
    for s_index, (name, opts) in enumerate(SCENARIOS):
        sensor = RangeBearingSensor(pos=opts.get("pos", (0.0, 0.0)), sigma_r=3.0, sigma_phi=opts["sigma_phi"])
        min_range = float(np.min(np.linalg.norm(truth[:, :2] - sensor.pos, axis=1)))
        sums = {k: [] for k in ("meas", "ekf", "ukf", "pf")}
        lost = {k: 0 for k in ("ekf", "ukf", "pf")}
        for run in range(RUNS):
            rng = np.random.default_rng(1000 * s_index + run)
            res = run_tracking(truth, sensor, motion, rng, n_particles=N_PARTICLES,
                               init_error=opts.get("init_error"), init_heading_std=opts.get("init_heading_std"),
                               seed_pf=5000 + 1000 * s_index + run)
            for k in sums:
                sums[k].append(rmse(res["errors"][k]))
            for k in lost:
                lost[k] += int(res["errors"][k][-1] > LOST_THRESHOLD)
                times[k].append(res["times"][k])
            if s_index == 0 and run == 0:
                write_run(t, truth, res)
        means = {k: float(np.mean(v)) for k, v in sums.items()}
        rows.append((name, means, lost))
        print(f"{name:45s} min range {min_range:5.1f} m  meas {means['meas']:6.2f}  EKF {means['ekf']:6.2f}  "
              f"UKF {means['ukf']:6.2f}  PF {means['pf']:6.2f}   lost EKF {lost['ekf']:3d} UKF {lost['ukf']:3d} "
              f"PF {lost['pf']:3d}   median EKF {np.median(sums['ekf']):5.2f} UKF {np.median(sums['ukf']):5.2f} "
              f"PF {np.median(sums['pf']):5.2f}")
    print("\nLaTeX rows for tab:ch19-rmse:")
    for name, means, lost in rows:
        print(f"  {name} & {means['meas']:.2f} & {means['ekf']:.2f} & {means['ukf']:.2f} & {means['pf']:.2f}"
              f" & {lost['ekf']} & {lost['ukf']} & {lost['pf']}\\\\")
    print("\nmean time per filter step (ms): " +
          ", ".join(f"{k.upper()} {1000 * np.mean(v):.3f}" for k, v in times.items()))


def write_run(t, truth, res):
    est = res["est"]
    path = os.path.join(DATA, "ch19-compare-track.dat")
    with open(path, "w") as f:
        f.write("t x_true y_true meas_x meas_y ekf_x ekf_y ukf_x ukf_y pf_x pf_y\n")
        for k in range(1, len(t)):
            f.write(f"{t[k]:.1f} {truth[k, 0]:.3f} {truth[k, 1]:.3f} "
                    f"{res['meas_xy'][k, 0]:.3f} {res['meas_xy'][k, 1]:.3f} "
                    f"{est['ekf'][k, 0]:.3f} {est['ekf'][k, 1]:.3f} "
                    f"{est['ukf'][k, 0]:.3f} {est['ukf'][k, 1]:.3f} "
                    f"{est['pf'][k, 0]:.3f} {est['pf'][k, 1]:.3f}\n")
    print("wrote", os.path.normpath(path))
    path = os.path.join(DATA, "ch19-compare-error.dat")
    err = res["errors"]
    with open(path, "w") as f:
        f.write("t err_meas err_ekf err_ukf err_pf\n")
        for k in range(1, len(t)):
            f.write(f"{t[k]:.1f} {err['meas'][k]:.3f} {err['ekf'][k]:.3f} {err['ukf'][k]:.3f} {err['pf'][k]:.3f}\n")
    print("wrote", os.path.normpath(path))
    print(f"single run RMSE: meas {rmse(err['meas']):.2f}, EKF {rmse(err['ekf']):.2f}, "
          f"UKF {rmse(err['ukf']):.2f}, PF {rmse(err['pf']):.2f}")


if __name__ == "__main__":
    main()
