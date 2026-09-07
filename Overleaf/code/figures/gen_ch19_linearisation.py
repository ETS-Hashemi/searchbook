"""Generate the data of the linearisation-error ("banana") figure of Chapter 19.

A Gaussian in range and bearing, r ~ N(100, 5^2), phi ~ N(pi/2, 0.3^2), is
pushed through the polar-to-Cartesian map (r, phi) -> (r cos phi, r sin phi)
in three ways: Monte Carlo (the truth), the EKF linearisation at the mean,
and the unscented transform with alpha = 1, beta = 2, kappa = 3 - n = 1.

Writes (whitespace separated, one header row):
  figures/data/ch19-banana-samples.dat    x y                    (N_SAMPLES samples)
  figures/data/ch19-banana-ellipses.dat   mc_x mc_y ekf_x ekf_y ut_x ut_y   (2-sigma ellipses)
  figures/data/ch19-banana-sigma.dat      x y                    (images of the 5 sigma points)
  figures/data/ch19-banana-mean-{mc,ekf,ut}.dat   x y          (the three means)
and prints the numbers quoted in the chapter.  Fixed seed.
Run from anywhere:   python3 code/figures/gen_ch19_linearisation.py
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from ch19_nonlinear_filters import sigma_points, unscented_transform  # noqa: E402

DATA = os.path.join(HERE, "..", "..", "figures", "data")
N_SAMPLES = 2000
MEAN = np.array([100.0, math.pi / 2])
COV = np.diag([5.0 ** 2, 0.3 ** 2])
SEED = 19


def polar_to_cartesian(P):
    P = np.atleast_2d(P)
    return np.column_stack([P[:, 0] * np.cos(P[:, 1]), P[:, 0] * np.sin(P[:, 1])])


def ellipse(mean, cov, n_sigma=2.0, n=72):
    vals, vecs = np.linalg.eigh(cov)
    order = np.argsort(vals)[::-1]
    vals, vecs = vals[order], vecs[:, order]
    ang = np.linspace(0.0, 2 * math.pi, n + 1)
    pts = np.column_stack([n_sigma * math.sqrt(vals[0]) * np.cos(ang), n_sigma * math.sqrt(vals[1]) * np.sin(ang)])
    return mean + pts @ vecs.T


def inside_fraction(samples, mean, cov, n_sigma=2.0):
    d = samples - mean
    m2 = np.einsum("ij,jk,ik->i", d, np.linalg.inv(cov), d)
    return float(np.mean(m2 <= n_sigma ** 2))


def main():
    rng = np.random.default_rng(SEED)
    polar = rng.multivariate_normal(MEAN, COV, size=N_SAMPLES)
    samples = polar_to_cartesian(polar)
    mc_mean = samples.mean(axis=0)
    mc_cov = np.cov(samples.T)
    # EKF: linearise at the mean
    r, phi = MEAN
    J = np.array([[math.cos(phi), -r * math.sin(phi)], [math.sin(phi), r * math.cos(phi)]])
    ekf_mean = polar_to_cartesian(MEAN)[0]
    ekf_cov = J @ COV @ J.T
    # unscented transform
    X, W_m, W_c = sigma_points(MEAN, COV, alpha=1.0, beta=2.0, kappa=1.0, jitter=0.0)
    ut_mean, ut_cov, _ = unscented_transform(X, W_m, W_c, polar_to_cartesian, MEAN)
    images = polar_to_cartesian(X)

    with open(os.path.join(DATA, "ch19-banana-samples.dat"), "w") as f:
        f.write("x y\n")
        for x, y in samples:
            f.write(f"{x:.3f} {y:.3f}\n")
    e_mc, e_ekf, e_ut = ellipse(mc_mean, mc_cov), ellipse(ekf_mean, ekf_cov), ellipse(ut_mean, ut_cov)
    with open(os.path.join(DATA, "ch19-banana-ellipses.dat"), "w") as f:
        f.write("mc_x mc_y ekf_x ekf_y ut_x ut_y\n")
        for a, b, c in zip(e_mc, e_ekf, e_ut):
            f.write(f"{a[0]:.3f} {a[1]:.3f} {b[0]:.3f} {b[1]:.3f} {c[0]:.3f} {c[1]:.3f}\n")
    with open(os.path.join(DATA, "ch19-banana-sigma.dat"), "w") as f:
        f.write("x y\n")
        for x, y in images:
            f.write(f"{x:.3f} {y:.3f}\n")
    for tag, (x, y) in (("mc", mc_mean), ("ekf", ekf_mean), ("ut", ut_mean)):
        with open(os.path.join(DATA, f"ch19-banana-mean-{tag}.dat"), "w") as f:
            f.write(f"x y\n{x:.3f} {y:.3f}\n")
    print("wrote ch19-banana-*.dat")
    print(f"Monte Carlo mean: ({mc_mean[0]:.2f}, {mc_mean[1]:.2f}); exact mean y = 100 exp(-0.045) = {100 * math.exp(-0.045):.2f}")
    print(f"EKF mean:         ({ekf_mean[0]:.2f}, {ekf_mean[1]:.2f})")
    print(f"UT mean:          ({ut_mean[0]:.2f}, {ut_mean[1]:.2f})")
    print(f"std devs (x, y): MC ({math.sqrt(mc_cov[0, 0]):.2f}, {math.sqrt(mc_cov[1, 1]):.2f}), "
          f"EKF ({math.sqrt(ekf_cov[0, 0]):.2f}, {math.sqrt(ekf_cov[1, 1]):.2f}), "
          f"UT ({math.sqrt(ut_cov[0, 0]):.2f}, {math.sqrt(ut_cov[1, 1]):.2f})")
    print(f"fraction of samples inside the 2-sigma ellipse: MC {100 * inside_fraction(samples, mc_mean, mc_cov):.1f}%, "
          f"EKF {100 * inside_fraction(samples, ekf_mean, ekf_cov):.1f}%, "
          f"UT {100 * inside_fraction(samples, ut_mean, ut_cov):.1f}% (nominal 86.5%)")
    print("sigma point images:", np.round(images, 2).tolist())


if __name__ == "__main__":
    main()
