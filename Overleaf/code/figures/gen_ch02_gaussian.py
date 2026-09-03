"""Generate the data of the Gaussian figure of Chapter 2.

Writes
  figures/data/ch02-gaussian-samples.dat   columns: x y   (400 samples)
  figures/data/ch02-gaussian-ellipses.dat  columns: x1 y1 x2 y2 (1- and 2-sigma)
for the Gaussian with mean (2, 1) and covariance [[2.0, 1.2], [1.2, 1.0]].
Fixed seed.  Run from anywhere:

    python3 code/figures/gen_ch02_gaussian.py
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from ch02_toolbox import covariance_ellipse, ellipse_points, mahalanobis2  # noqa: E402

DATA = os.path.join(HERE, "..", "..", "figures", "data")
MU = np.array([2.0, 1.0])
SIGMA = np.array([[2.0, 1.2], [1.2, 1.0]])
N = 400


def main():
    rng = np.random.default_rng(2)
    samples = rng.multivariate_normal(MU, SIGMA, size=N)
    with open(os.path.join(DATA, "ch02-gaussian-samples.dat"), "w") as f:
        f.write("x y\n")
        for x, y in samples:
            f.write(f"{x:.4f} {y:.4f}\n")
    e1 = ellipse_points(MU, SIGMA, n_sigma=1.0, n=72)
    e2 = ellipse_points(MU, SIGMA, n_sigma=2.0, n=72)
    with open(os.path.join(DATA, "ch02-gaussian-ellipses.dat"), "w") as f:
        f.write("x1 y1 x2 y2\n")
        for (x1, y1), (x2, y2) in zip(e1, e2):
            f.write(f"{x1:.4f} {y1:.4f} {x2:.4f} {y2:.4f}\n")
    a, b, angle, vecs = covariance_ellipse(SIGMA)
    m2 = np.array([mahalanobis2(s, MU, SIGMA) for s in samples])
    print("wrote ch02-gaussian-samples.dat and ch02-gaussian-ellipses.dat")
    print(f"eigenvalues: {a * a:.3f}, {b * b:.3f}; semi-axes: {a:.3f}, {b:.3f}; "
          f"angle: {math.degrees(angle):.2f} deg")
    print(f"major axis direction: ({vecs[0, 0]:.3f}, {vecs[1, 0]:.3f})")
    print(f"inside 1-sigma: {np.mean(m2 <= 1.0) * 100:.1f}% (theory {100 * (1 - math.exp(-0.5)):.1f}%)")
    print(f"inside 2-sigma: {np.mean(m2 <= 4.0) * 100:.1f}% (theory {100 * (1 - math.exp(-2.0)):.1f}%)")
    print(f"sample mean: ({samples[:, 0].mean():.3f}, {samples[:, 1].mean():.3f})")


if __name__ == "__main__":
    main()
