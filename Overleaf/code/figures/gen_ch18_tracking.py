"""Generate the data files of Chapter 18 (the Kalman filter).

All scenarios use code/ch18_kalman.py (NumPy only, fixed seeds).  Written
into figures/data/ (whitespace separated, one header row):

  ch18-tracking.dat            experiment A: an intruder flying a constant-
                               velocity model with white-noise acceleration
                               (q = 0.2 m^2/s^3) observed at 10 Hz by a sensor
                               with sigma_x = 1.0 m, sigma_y = 0.5 m; columns
                               t, truth (tx ty tvx tvy), measurement (zx zy),
                               KF estimate (ex ey evx evy), finite-difference
                               velocity of the measurements (fdvx fdvy), the
                               position standard deviations of the estimate
                               (sx sy) and the position errors (errz errkf)
  ch18-tracking-ellipses.dat   2-sigma position ellipses of the estimate at
                               t = 4, 8, 12, 16, 20 s (column pairs x1 y1 ...)
  ch18-rmse-q.dat              experiment B: position/velocity RMSE and mean
                               NIS of the filter versus its q, averaged over
                               20 Monte-Carlo runs of experiment A's model
  ch18-tuning.dat              experiment C: three q values on one data set,
                               a drone that flies straight, turns by 90 deg in
                               4 s and flies straight again (sigma = 1 m)
  ch18-prediction-means.dat    experiment D: prediction 0.5 .. 3 s ahead from
                               the estimate of experiment A at t = 10 s
  ch18-prediction-ellipses.dat 2-sigma ellipses of those predictions
  ch18-prediction-truth.dat    the true trajectory from t = 10 s to 13 s
  ch18-example.dat             the worked example (truth, measurements,
                               predicted and updated positions)
  ch18-example-ellipses.dat    2-sigma circles of P^- (dashed) and P (solid)

Run from Overleaf/:   python3 code/figures/gen_ch18_tracking.py
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import ch18_kalman as kal  # noqa: E402

DATA = os.path.normpath(os.path.join(HERE, "..", "..", "figures", "data"))


def write_dat(name, header, columns):
    """Write columns (equal length) with a header row."""
    path = os.path.join(DATA, name)
    with open(path, "w") as fh:
        fh.write(" ".join(header) + "\n")
        for row in zip(*columns):
            fh.write(" ".join("%.4f" % v for v in row) + "\n")
    print("wrote", os.path.relpath(path, os.path.join(HERE, "..", "..")))


def ellipse(mu, cov, k=2.0, n=72):
    """Points of the k-sigma ellipse of N(mu, cov) (closed polygon)."""
    w, V = np.linalg.eigh(np.asarray(cov, float))
    w = np.sqrt(np.clip(w, 0.0, None))
    ang = np.linspace(0.0, 2.0 * math.pi, n + 1)
    return (mu[None, :] + k * (w[0] * np.cos(ang)[:, None] * V[:, 0][None, :]
                               + w[1] * np.sin(ang)[:, None] * V[:, 1][None, :]))


def ellipse_columns(items, k=2.0):
    header, cols = [], []
    for i, (mu, cov) in enumerate(items, start=1):
        pts = ellipse(mu, cov, k)
        header += ["x%d" % i, "y%d" % i]
        cols += [pts[:, 0], pts[:, 1]]
    return header, cols


# ---------------------------------------------------------------------------
# Experiment A: tracking an intruder (and D: predicting ahead from it)
# ---------------------------------------------------------------------------
DT, Q_TRUE, SIG = 0.1, 0.2, np.array([1.0, 0.5])
N_STEPS = 200


def experiment_a():
    rng = np.random.default_rng(18)
    F, H, Q = kal.cv_model(2, DT, Q_TRUE)
    R = np.diag(SIG ** 2)
    truth, zs = kal.simulate([0.0, 0.0, 2.0, 1.0], F, Q, H, R, N_STEPS, rng)
    x0, P0 = kal.init_two_point(zs[0], zs[1], DT, R)
    kf = kal.KalmanFilter(F, H, Q, R, x0, P0)
    est, cov, nis, _ = kal.run_filter(kf, zs[2:])
    tru = truth[3:]                       # states k = 3 .. N
    z = np.array(zs[2:])
    t = DT * np.arange(3, N_STEPS + 1)
    fd = (z - np.array(zs[1:-1])) / DT    # finite-difference velocity
    errz = np.linalg.norm(z - tru[:, :2], axis=1)
    errk = np.linalg.norm(est[:, :2] - tru[:, :2], axis=1)
    write_dat("ch18-tracking.dat",
              ["t", "tx", "ty", "tvx", "tvy", "zx", "zy", "ex", "ey", "evx",
               "evy", "fdvx", "fdvy", "sx", "sy", "errz", "errkf"],
              [t, tru[:, 0], tru[:, 1], tru[:, 2], tru[:, 3], z[:, 0], z[:, 1],
               est[:, 0], est[:, 1], est[:, 2], est[:, 3], fd[:, 0], fd[:, 1],
               np.sqrt(cov[:, 0, 0]), np.sqrt(cov[:, 1, 1]), errz, errk])
    items = []
    for ts in (4.0, 8.0, 12.0, 16.0, 20.0):
        i = int(round(ts / DT)) - 3
        items.append((est[i, :2], cov[i, :2, :2]))
    write_dat("ch18-tracking-ellipses.dat", *ellipse_columns(items))
    e_p, e_raw = kal.rmse(est[:, :2], tru[:, :2]), kal.rmse(z, tru[:, :2])
    e_v, e_fd = kal.rmse(est[:, 2:], tru[:, 2:]), kal.rmse(fd, tru[:, 2:])
    lo, hi = kal.nis_bounds(len(nis), 2)
    print("A: position RMSE KF %.3f m, raw %.3f m; velocity RMSE KF %.3f m/s,"
          " finite differences %.3f m/s; mean NIS %.3f (95%% band %.2f..%.2f);"
          " final sigma_x %.3f sigma_y %.3f sigma_vx %.3f" %
          (e_p, e_raw, e_v, e_fd, np.mean(nis), lo, hi,
           math.sqrt(cov[-1, 0, 0]), math.sqrt(cov[-1, 1, 1]),
           math.sqrt(cov[-1, 2, 2])))
    # Experiment D: predict ahead from the estimate at t = 10 s
    i10 = int(round(10.0 / DT)) - 3
    kf10 = kal.KalmanFilter(F, H, Q, R, est[i10], cov[i10])
    ahead = kf10.predict_ahead(30)
    hs = [0, 5, 10, 15, 20, 25, 30]
    means = [(kf10.x.copy(), kf10.P.copy())] + [ahead[j - 1] for j in hs[1:]]
    write_dat("ch18-prediction-means.dat", ["h", "x", "y", "sx", "sy"],
              [np.array([h * DT for h in hs]),
               np.array([m[0][0] for m in means]),
               np.array([m[0][1] for m in means]),
               np.array([math.sqrt(m[1][0, 0]) for m in means]),
               np.array([math.sqrt(m[1][1, 1]) for m in means])])
    write_dat("ch18-prediction-ellipses.dat",
              *ellipse_columns([(m[0][:2], m[1][:2, :2]) for m in means]))
    seg = truth[int(round(10.0 / DT)):int(round(13.0 / DT)) + 1]
    write_dat("ch18-prediction-truth.dat", ["t", "x", "y"],
              [np.arange(len(seg)) * DT + 10.0, seg[:, 0], seg[:, 1]])
    for h, (x, P) in zip(hs, means):
        w = np.sqrt(np.linalg.eigvalsh(P[:2, :2]))
        print("D: horizon %.1f s: sigma_x %.3f sigma_y %.3f, 2-sigma semi-axes"
              " %.2f x %.2f m" % (h * DT, math.sqrt(P[0, 0]),
                                  math.sqrt(P[1, 1]), 2 * w[1], 2 * w[0]))


# ---------------------------------------------------------------------------
# Experiment B: RMSE versus q (Monte Carlo)
# ---------------------------------------------------------------------------
def experiment_b(runs=20):
    rng = np.random.default_rng(1818)
    F, H, Q = kal.cv_model(2, DT, Q_TRUE)
    R = np.diag(SIG ** 2)
    data = [kal.simulate([0.0, 0.0, 2.0, 1.0], F, Q, H, R, N_STEPS, rng)
            for _ in range(runs)]
    qs = np.logspace(-2, 2, 17)
    rp, rv, rraw, nism = [], [], [], []
    for q in qs:
        _, _, Qf = kal.cv_model(2, DT, q)
        ep, ev, er, en = [], [], [], []
        for truth, zs in data:
            x0, P0 = kal.init_two_point(zs[0], zs[1], DT, R)
            kf = kal.KalmanFilter(F, H, Qf, R, x0, P0)
            est, _, nis, _ = kal.run_filter(kf, zs[2:])
            tru = truth[3:]
            ep.append(kal.rmse(est[:, :2], tru[:, :2]) ** 2)
            ev.append(kal.rmse(est[:, 2:], tru[:, 2:]) ** 2)
            er.append(kal.rmse(np.array(zs[2:]), tru[:, :2]) ** 2)
            en.append(np.mean(nis))
        rp.append(math.sqrt(np.mean(ep))); rv.append(math.sqrt(np.mean(ev)))
        rraw.append(math.sqrt(np.mean(er))); nism.append(np.mean(en))
    write_dat("ch18-rmse-q.dat", ["q", "rmse_p", "rmse_v", "rmse_raw", "nis"],
              [qs, np.array(rp), np.array(rv), np.array(rraw), np.array(nism)])
    j = int(np.argmin(rp))
    for q, a, b, c, d in zip(qs, rp, rv, rraw, nism):
        print("B: q=%8.3f  RMSE_p %.3f  RMSE_v %.3f  raw %.3f  NIS %.2f" %
              (q, a, b, c, d))
    print("B: best q = %.3f (true q = %.2f), position RMSE %.3f, raw %.3f" %
          (qs[j], Q_TRUE, rp[j], rraw[j]))


# ---------------------------------------------------------------------------
# Experiment C: three q values on a trajectory with a turn
# ---------------------------------------------------------------------------
def turn_trajectory(dt, speed=3.0, t1=8.0, t2=12.0, t3=20.0):
    omega = (math.pi / 2) / (t2 - t1)
    r = speed / omega
    ts = np.arange(0, int(round(t3 / dt)) + 1) * dt
    states = []
    for t in ts:
        if t <= t1:
            states.append([speed * t, 0.0, speed, 0.0])
        elif t <= t2:
            th = omega * (t - t1)
            states.append([speed * t1 + r * math.sin(th), r - r * math.cos(th),
                           speed * math.cos(th), speed * math.sin(th)])
        else:
            states.append([speed * t1 + r, r + speed * (t - t2), 0.0, speed])
    return ts, np.array(states)


def experiment_c():
    rng = np.random.default_rng(181818)
    ts, truth = turn_trajectory(DT)
    sigma = 1.0
    R = sigma ** 2 * np.eye(2)
    z = truth[:, :2] + sigma * rng.standard_normal((len(ts), 2))
    qs = (0.01, 1.0, 100.0)
    cols = [ts[2:], truth[2:, 0], truth[2:, 1], z[2:, 0], z[2:, 1]]
    header = ["t", "tx", "ty", "zx", "zy"]
    for i, q in enumerate(qs, start=1):
        F, H, Q = kal.cv_model(2, DT, q)
        x0, P0 = kal.init_two_point(z[0], z[1], DT, R)
        kf = kal.KalmanFilter(F, H, Q, R, x0, P0)
        innov, est = [], []
        for zk in z[2:]:
            res = kf.step(zk)
            innov.append(res.innovation)
            est.append(kf.x.copy())
        est, innov = np.array(est), np.array(innov)
        kf2 = kal.KalmanFilter(F, H, Q, R, x0, P0)
        nis = np.array([kf2.step(zk).nis for zk in z[2:]])
        err = np.linalg.norm(est[:, :2] - truth[2:, :2], axis=1)
        cols += [est[:, 0], est[:, 1], err]
        header += ["e%dx" % i, "e%dy" % i, "err%d" % i]
        turn = (ts[2:] >= 8.0) & (ts[2:] <= 13.0)
        print("C: q=%6.2f  RMSE %.3f m (turn %.3f m, straight %.3f m)  mean NIS"
              " %.2f  lag-1 autocorrelation %s" %
              (q, kal.rmse(est[:, :2], truth[2:, :2]),
               math.sqrt(np.mean(err[turn] ** 2)),
               math.sqrt(np.mean(err[~turn] ** 2)), np.mean(nis),
               np.round(kal.lag1_autocorrelation(innov), 2)))
    print("C: raw measurement RMSE %.3f m, whiteness bound %.3f" %
          (kal.rmse(z[2:], truth[2:, :2]), 1.96 / math.sqrt(len(ts) - 2)))
    write_dat("ch18-tuning.dat", header, cols)


# ---------------------------------------------------------------------------
# The worked example
# ---------------------------------------------------------------------------
def worked_example_data():
    rows = kal.worked_example()
    k = np.array([r["k"] for r in rows], float)
    write_dat("ch18-example.dat",
              ["k", "tx", "ty", "zx", "zy", "px", "py", "ux", "uy"],
              [k, np.array([r["truth"][0] for r in rows]),
               np.array([r["truth"][1] for r in rows]),
               np.array([r["z"][0] for r in rows]),
               np.array([r["z"][1] for r in rows]),
               np.array([r["x_pred"][0] for r in rows]),
               np.array([r["x_pred"][1] for r in rows]),
               np.array([r["x"][0] for r in rows]),
               np.array([r["x"][1] for r in rows])])
    items = [(r["x_pred"][:2], r["P_pred"][:2, :2]) for r in rows]
    items += [(r["x"][:2], r["P"][:2, :2]) for r in rows]
    write_dat("ch18-example-ellipses.dat", *ellipse_columns(items))


if __name__ == "__main__":
    os.makedirs(DATA, exist_ok=True)
    experiment_a()
    experiment_b()
    experiment_c()
    worked_example_data()
