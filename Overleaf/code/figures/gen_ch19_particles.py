"""Generate the data of the particle-cloud figure of Chapter 19 (the intruder
hidden behind a building, Example 19.14 of the book).

Runs occlusion_example() of code/ch19_nonlinear_filters.py (fixed seed) and
writes (whitespace separated, one header row):
  figures/data/ch19-particles.dat         x1 y1 x2 y2 x3 y3   (SUBSAMPLE particles at
                                          the last measurement before the canyon, while
                                          hidden, and at the first measurement after it)
  figures/data/ch19-particles-truth.dat   k t x y   (the true path)
  figures/data/ch19-particles-marks.dat   x y       (true positions at the three moments)
  figures/data/ch19-particles-ukf.dat     x y       (the UKF mean while hidden)
  figures/data/ch19-particles-neff.dat    k t neff  (effective sample size per step)
and prints the numbers quoted in the chapter.
Run from anywhere:   python3 code/figures/gen_ch19_particles.py
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from ch19_nonlinear_filters import occlusion_example  # noqa: E402

DATA = os.path.join(HERE, "..", "..", "figures", "data")
SUBSAMPLE = 400


def main():
    res = occlusion_example(n_particles=2000, seed=19, verbose=True)
    dt = res["dt"]
    keys = (res["k_last"], res["k_mid"], res["k_first"])
    rng = np.random.default_rng(0)
    idx = rng.choice(2000, size=SUBSAMPLE, replace=False)
    clouds = [res["stages"][k]["particles"][idx] for k in keys]
    with open(os.path.join(DATA, "ch19-particles.dat"), "w") as f:
        f.write("x1 y1 x2 y2 x3 y3\n")
        for i in range(SUBSAMPLE):
            f.write(" ".join(f"{c[i, 0]:.2f} {c[i, 1]:.2f}" for c in clouds) + "\n")
    truth = res["truth"]
    with open(os.path.join(DATA, "ch19-particles-truth.dat"), "w") as f:
        f.write("k t x y\n")
        for k in range(truth.shape[0]):
            f.write(f"{k} {k * dt:.1f} {truth[k, 0]:.2f} {truth[k, 1]:.2f}\n")
    with open(os.path.join(DATA, "ch19-particles-marks.dat"), "w") as f:
        f.write("x y\n")
        for k in keys:
            f.write(f"{truth[k, 0]:.2f} {truth[k, 1]:.2f}\n")
    with open(os.path.join(DATA, "ch19-particles-ukf.dat"), "w") as f:
        u = res["stages"][res["k_mid"]]["ukf_mean"]
        f.write(f"x y\n{u[0]:.2f} {u[1]:.2f}\n")
    with open(os.path.join(DATA, "ch19-particles-neff.dat"), "w") as f:
        f.write("k t neff\n")
        for i, n in enumerate(res["n_eff"]):
            k = i + 2
            f.write(f"{k} {k * dt:.1f} {n:.1f}\n")
    print("wrote ch19-particles*.dat")
    n_eff = res["n_eff"]
    print("N_eff by step:", " ".join(f"{k + 2}:{n:.0f}" for k, n in enumerate(n_eff)))
    gap = res["ukf_est"][res["k_last"]:res["k_first"]]
    print("UKF mean while hidden (k, x, y):",
          " ".join(f"({res['k_last'] + 1 + i}, {g[0]:.1f}, {g[1]:.1f})" for i, g in enumerate(gap)))


if __name__ == "__main__":
    main()
