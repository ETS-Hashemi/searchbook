"""Kalman filter for tracking an unknown drone (Chapter 18).

Linear-Gaussian state-space model
    x_k = F x_{k-1} + B u_k + w_k,   w_k ~ N(0, Q)
    z_k = H x_k + v_k,               v_k ~ N(0, R)

Contents
    KalmanFilter      predict / update (Joseph form), innovation and NIS,
                      chi-square gating, k-step-ahead prediction
    cv_model          constant-velocity model, state [p, v], white-noise-
                      acceleration Q = q [[dt^3/3, dt^2/2], [dt^2/2, dt]]
    ca_model          constant-acceleration model, state [p, v, a]
    init_two_point    track initialisation from two position measurements
    simulate          truth + noisy measurements (misses, outliers)
    run_filter        filter a measurement sequence (None = missing)
    nearest_neighbour_association   gated data association for several tracks
    worked_example    the five-step example of the chapter (Table 18.x)
    nis_bounds, lag1_autocorrelation   innovation diagnostics

Self-test:  python3 code/ch18_kalman.py     (NumPy only, about one second)
"""
from __future__ import annotations

import math
import time
from dataclasses import dataclass

import numpy as np

# Chi-square quantiles gamma with P(chi2_dof <= gamma) = prob, CHI2[dof][prob].
CHI2 = {
    1: {0.90: 2.706, 0.95: 3.841, 0.99: 6.635, 0.999: 10.828},
    2: {0.90: 4.605, 0.95: 5.991, 0.99: 9.210, 0.999: 13.816},
    3: {0.90: 6.251, 0.95: 7.815, 0.99: 11.345, 0.999: 16.266},
    4: {0.90: 7.779, 0.95: 9.488, 0.99: 13.277, 0.999: 18.467},
    5: {0.90: 9.236, 0.95: 11.070, 0.99: 15.086, 0.999: 20.515},
    6: {0.90: 10.645, 0.95: 12.592, 0.99: 16.812, 0.999: 22.458},
}


def chi2_threshold(dof, prob=0.99):
    """Gate threshold gamma with P(chi2_dof <= gamma) = prob (table lookup)."""
    return CHI2[dof][prob]


def symmetrize(P):
    """Remove the round-off asymmetry of a covariance matrix."""
    return 0.5 * (P + P.T)


@dataclass
class UpdateResult:
    innovation: np.ndarray      # y = z - H x^-
    innovation_cov: np.ndarray  # S = H P^- H^T + R
    gain: np.ndarray            # K = P^- H^T S^-1
    nis: float                  # d^2 = y^T S^-1 y
    accepted: bool              # False when the gate rejected z


class KalmanFilter:
    """Linear Kalman filter: state x (n,), covariance P (n, n)."""

    def __init__(self, F, H, Q, R, x0, P0, B=None):
        self.F = np.asarray(F, float)
        self.H = np.asarray(H, float)
        self.Q = np.asarray(Q, float)
        self.R = np.asarray(R, float)
        self.B = None if B is None else np.asarray(B, float)
        self.x = np.array(x0, float)
        self.P = np.array(P0, float)

    @property
    def n(self):
        return self.x.shape[0]

    @property
    def m(self):
        return self.H.shape[0]

    def predict(self, u=None, F=None, Q=None):
        """Predict: x^- = F x + B u,  P^- = F P F^T + Q.
        Pass F and Q built for the actual time step if dt varies."""
        F = self.F if F is None else np.asarray(F, float)
        Q = self.Q if Q is None else np.asarray(Q, float)
        self.x = F @ self.x
        if u is not None and self.B is not None:
            self.x = self.x + self.B @ np.asarray(u, float)
        self.P = symmetrize(F @ self.P @ F.T + Q)
        return self.x.copy(), self.P.copy()

    def update(self, z, R=None, gate_prob=None, joseph=True):
        """Update with measurement z.  With gate_prob, z is rejected (state
        unchanged) when its NIS exceeds the chi-square threshold."""
        R = self.R if R is None else np.asarray(R, float)
        y, S = self.innovation(z, R)
        d2 = float(y @ np.linalg.solve(S, y))
        K = np.linalg.solve(S, self.H @ self.P).T      # K = P H^T S^-1
        if gate_prob is not None and d2 > chi2_threshold(self.m, gate_prob):
            return UpdateResult(y, S, K, d2, False)
        self.x = self.x + K @ y
        I_KH = np.eye(self.n) - K @ self.H
        if joseph:   # valid for any K, keeps P symmetric positive definite
            self.P = I_KH @ self.P @ I_KH.T + K @ R @ K.T
        else:        # the short form, exact only for the optimal K
            self.P = I_KH @ self.P
        self.P = symmetrize(self.P)
        return UpdateResult(y, S, K, d2, True)

    def innovation(self, z, R=None):
        """Innovation y = z - H x^- and its covariance S = H P^- H^T + R."""
        R = self.R if R is None else np.asarray(R, float)
        y = np.asarray(z, float) - self.H @ self.x
        S = self.H @ self.P @ self.H.T + R
        return y, S

    def nis(self, z, R=None):
        """Normalised innovation squared, the squared Mahalanobis distance
        of z from the predicted measurement."""
        y, S = self.innovation(z, R)
        return float(y @ np.linalg.solve(S, y))

    def step(self, z=None, u=None, gate_prob=None):
        """One cycle: predict, then update if a measurement arrived."""
        self.predict(u)
        if z is None:
            return None
        return self.update(z, gate_prob=gate_prob)

    def predict_ahead(self, steps, F=None, Q=None):
        """Means and covariances 1..steps steps ahead (state unchanged)."""
        F = self.F if F is None else np.asarray(F, float)
        Q = self.Q if Q is None else np.asarray(Q, float)
        x, P, out = self.x.copy(), self.P.copy(), []
        for _ in range(steps):
            x = F @ x
            P = symmetrize(F @ P @ F.T + Q)
            out.append((x.copy(), P.copy()))
        return out

    def copy(self):
        return KalmanFilter(self.F, self.H, self.Q, self.R, self.x, self.P,
                            self.B)


# ---------------------------------------------------------------------------
# Motion models
# ---------------------------------------------------------------------------
def cv_model(dim, dt, q, measure_velocity=False):
    """Constant-velocity model in dim dimensions, state [p, v] (2*dim).
    q is the white-noise-acceleration intensity (m^2/s^3).  H selects the
    positions, or positions and velocities."""
    I, Z = np.eye(dim), np.zeros((dim, dim))
    F = np.block([[I, dt * I], [Z, I]])
    Q = q * np.block([[dt ** 3 / 3 * I, dt ** 2 / 2 * I],
                      [dt ** 2 / 2 * I, dt * I]])
    H = np.eye(2 * dim) if measure_velocity else np.hstack([I, Z])
    return F, H, Q


def ca_model(dim, dt, q):
    """Constant-acceleration model, state [p, v, a] (3*dim), white-noise
    jerk of intensity q (m^2/s^5); positions are measured."""
    I, Z = np.eye(dim), np.zeros((dim, dim))
    F = np.block([[I, dt * I, dt ** 2 / 2 * I], [Z, I, dt * I], [Z, Z, I]])
    Q = q * np.block([[dt ** 5 / 20 * I, dt ** 4 / 8 * I, dt ** 3 / 6 * I],
                      [dt ** 4 / 8 * I, dt ** 3 / 3 * I, dt ** 2 / 2 * I],
                      [dt ** 3 / 6 * I, dt ** 2 / 2 * I, dt * I]])
    H = np.hstack([I, Z, Z])
    return F, H, Q


def expm_nilpotent(A, s, terms=8):
    """exp(A s) by the Taylor series (exact for the nilpotent A of the
    kinematic models)."""
    n = A.shape[0]
    E, term = np.eye(n), np.eye(n)
    for k in range(1, terms):
        term = term @ (A * s) / k
        E = E + term
    return E


def process_noise_numeric(A, G, q, dt, steps=4000):
    """Q = int_0^dt exp(A s) G q G^T exp(A s)^T ds by the trapezoid rule;
    the self-test compares it with the closed forms of cv_model/ca_model."""
    G = np.asarray(G, float).reshape(A.shape[0], -1)
    grid = np.linspace(0.0, dt, steps + 1)
    Q = np.zeros_like(A, dtype=float)
    for i, s in enumerate(grid):
        E = expm_nilpotent(A, s)
        w = 0.5 if i in (0, steps) else 1.0
        Q += w * (E @ G) @ (q * (E @ G).T)
    return Q * (dt / steps)


def observability_rank(F, H):
    """Rank of the observability matrix [H; HF; ...; HF^(n-1)]."""
    n = F.shape[0]
    rows, M = [], H.copy()
    for _ in range(n):
        rows.append(M)
        M = M @ F
    return int(np.linalg.matrix_rank(np.vstack(rows)))


# ---------------------------------------------------------------------------
# Track initialisation, simulation, batch filtering, association
# ---------------------------------------------------------------------------
def init_two_point(z0, z1, dt, R):
    """Initialise [p, v] from two position measurements dt apart:
    x0 = [z1, (z1 - z0)/dt],  P0 = [[R, R/dt], [R/dt, 2R/dt^2]]."""
    z0, z1, R = (np.asarray(a, float) for a in (z0, z1, R))
    x0 = np.concatenate([z1, (z1 - z0) / dt])
    P0 = np.block([[R, R / dt], [R / dt, 2.0 * R / dt ** 2]])
    return x0, P0


def sample_gaussian(cov, rng):
    """One sample of N(0, cov) for a symmetric positive semidefinite cov."""
    w, V = np.linalg.eigh(np.asarray(cov, float))
    return V @ (np.sqrt(np.clip(w, 0.0, None)) * rng.standard_normal(len(w)))


def simulate(x0, F, Q, H, R, steps, rng, p_miss=0.0, p_outlier=0.0,
             outlier_sigma=20.0):
    """Simulate the model.  Returns truth (steps+1, n) with x0 in row 0 and
    the measurements z_1..z_steps (None = the sensor returned nothing;
    an outlier is z + N(0, outlier_sigma^2 I))."""
    x = np.asarray(x0, float).copy()
    truth, meas = [x.copy()], []
    for _ in range(steps):
        x = F @ x + sample_gaussian(Q, rng)
        truth.append(x.copy())
        if rng.random() < p_miss:
            meas.append(None)
            continue
        z = H @ x + sample_gaussian(R, rng)
        if rng.random() < p_outlier:
            z = z + outlier_sigma * rng.standard_normal(H.shape[0])
        meas.append(z)
    return np.array(truth), meas


def run_filter(kf, measurements, gate_prob=None):
    """Filter a sequence (None = missing).  Returns est (N, n), cov (N, n, n),
    nis (N,) (nan for missing) and accepted (N,) (False for missing or
    gated-out measurements)."""
    est, cov, nis, acc = [], [], [], []
    for z in measurements:
        res = kf.step(z, gate_prob=gate_prob)
        est.append(kf.x.copy())
        cov.append(kf.P.copy())
        nis.append(math.nan if res is None else res.nis)
        acc.append(res is not None and res.accepted)
    return np.array(est), np.array(cov), np.array(nis), np.array(acc)


def nearest_neighbour_association(filters, zs, gate_prob=0.99):
    """Greedy global nearest neighbour: repeatedly take the (track, z) pair
    with the smallest NIS inside the gate.  Returns {track index: z index};
    unmatched measurements are candidates for new tracks."""
    pairs = []
    for i, kf in enumerate(filters):
        gamma = chi2_threshold(kf.m, gate_prob)
        for j, z in enumerate(zs):
            d2 = kf.nis(z)
            if d2 <= gamma:
                pairs.append((d2, i, j))
    assignment, used_z = {}, set()
    for _, i, j in sorted(pairs):
        if i not in assignment and j not in used_z:
            assignment[i] = j
            used_z.add(j)
    return assignment


def rmse(a, b):
    """Root mean square Euclidean distance between rows of a and b."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    return float(np.sqrt(np.mean(np.sum((a - b) ** 2, axis=1))))


def nis_bounds(N, m, z=1.96):
    """Interval in which the mean NIS of N steps lies with probability
    about 95 % if the filter is consistent (normal approximation of
    chi2_{N m} / N)."""
    half = z * math.sqrt(2.0 * m / N)
    return m - half, m + half


def lag1_autocorrelation(y):
    """Lag-1 autocorrelation of each innovation component (whiteness test:
    |rho| < 1.96/sqrt(N) for a consistent filter)."""
    y = np.asarray(y, float) - np.mean(y, axis=0)
    return np.sum(y[:-1] * y[1:], axis=0) / np.sum(y * y, axis=0)


# ---------------------------------------------------------------------------
# The worked example of the chapter: 2D drone, five steps, dt = 1 s
# ---------------------------------------------------------------------------
WORKED_DT = 1.0
WORKED_Q = 0.1            # m^2/s^3
WORKED_SIGMA = 0.5        # m, position measurement noise per axis
WORKED_X0 = [0.0, 0.0, 0.5, 0.0]          # initial guess (velocity wrong)
WORKED_P0 = np.diag([1.0, 1.0, 1.0, 1.0])
WORKED_TRUE_X0 = [0.0, 0.0, 1.0, 0.5]     # true state, no process noise
# Five noisy position measurements (true position + N(0, 0.5^2) per axis,
# drawn once with numpy.random.default_rng(18) and rounded to 2 decimals).
WORKED_Z = [[1.28, 0.31], [1.71, 0.92], [3.03, 1.81], [4.31, 1.79],
            [5.34, 2.88]]
# Values the self-test must reproduce (from an earlier run of this file).
WORKED_EXPECTED = {
    "K1": [0.8905, 0.4599],                       # k_p, k_v at step 1
    "x5": [5.3197, 2.7335, 1.1349, 0.6300],      # updated mean after step 5
    "P5": [0.1708, 0.0902, 0.1379],               # a, b, c of P_5 per axis
}


def worked_example():
    """Run the five-step example; returns one record per step."""
    F, H, Q = cv_model(2, WORKED_DT, WORKED_Q)
    R = WORKED_SIGMA ** 2 * np.eye(2)
    kf = KalmanFilter(F, H, Q, R, WORKED_X0, WORKED_P0)
    truth = np.array(WORKED_TRUE_X0, float)
    rows = []
    for k, z in enumerate(WORKED_Z, start=1):
        truth = F @ truth
        x_pred, P_pred = kf.predict()
        res = kf.update(z)
        rows.append(dict(k=k, truth=truth.copy(), x_pred=x_pred,
                         P_pred=P_pred, z=np.array(z), y=res.innovation,
                         S=res.innovation_cov, K=res.gain, nis=res.nis,
                         x=kf.x.copy(), P=kf.P.copy()))
    return rows


def print_worked_example(rows):
    """Print the rows of the worked example (the table of the chapter)."""
    print("worked example: dt=%.1f q=%.2f sigma=%.2f x0=%s" %
          (WORKED_DT, WORKED_Q, WORKED_SIGMA, WORKED_X0))
    for r in rows:
        Pp, P, K = r["P_pred"], r["P"], r["K"]
        print("k=%d truth=(%.2f,%.2f,%.2f,%.2f)" % ((r["k"],) + tuple(r["truth"])))
        print("   x_pred=(%.3f,%.3f,%.3f,%.3f) P_pred a,b,c=(%.4f,%.4f,%.4f)"
              % (tuple(r["x_pred"]) + (Pp[0, 0], Pp[0, 2], Pp[2, 2])))
        print("   z=(%.2f,%.2f) y=(%.3f,%.3f) S=%.4f K: k_p=%.4f k_v=%.4f"
              " nis=%.3f" % (tuple(r["z"]) + tuple(r["y"]) +
                             (r["S"][0, 0], K[0, 0], K[2, 0], r["nis"])))
        print("   x=(%.3f,%.3f,%.3f,%.3f) P a,b,c=(%.4f,%.4f,%.4f)"
              " sig_p=%.3f sig_v=%.3f" %
              (tuple(r["x"]) + (P[0, 0], P[0, 2], P[2, 2],
                                math.sqrt(P[0, 0]), math.sqrt(P[2, 2]))))


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
def _chi2_cdf_numeric(x, k, steps=200000):
    """P(chi2_k <= x): erf for one degree of freedom (singular density),
    otherwise the trapezoid rule on the density."""
    if k == 1:
        return math.erf(math.sqrt(x / 2.0))
    t = np.linspace(0.0, x, steps + 1)
    dens = t ** (k / 2 - 1) * np.exp(-t / 2) / (2 ** (k / 2) * math.gamma(k / 2))
    return float(np.sum(0.5 * (dens[1:] + dens[:-1]) * np.diff(t)))


def _self_test():
    t0 = time.time()
    rng = np.random.default_rng(18)

    # 1. chi-square table: dof 2 has the closed form -2 ln(1-p); the others
    #    are checked against a numerical integral of the density.
    for p, g in CHI2[2].items():
        assert abs(g - (-2.0 * math.log(1.0 - p))) < 5e-4
    for dof in (1, 3, 4, 5, 6):
        for p, g in CHI2[dof].items():
            assert abs(_chi2_cdf_numeric(g, dof) - p) < 5e-4, (dof, p)

    # 2. process-noise closed forms equal the continuous-time integral
    A1, G1 = np.array([[0.0, 1.0], [0.0, 0.0]]), np.array([0.0, 1.0])
    _, _, Q = cv_model(1, 0.7, 2.5)
    assert np.allclose(Q, process_noise_numeric(A1, G1, 2.5, 0.7), atol=1e-6)
    A2 = np.array([[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [0.0, 0.0, 0.0]])
    _, _, Qa = ca_model(1, 0.7, 2.5)
    assert np.allclose(Qa, process_noise_numeric(A2, [0, 0, 1], 2.5, 0.7),
                       atol=1e-6)
    # k-step property: summing the CV noise over j steps of dt gives Q(j dt)
    F, _, Q = cv_model(2, 0.1, 0.3)
    Qsum, Fi = np.zeros((4, 4)), np.eye(4)
    for _ in range(7):
        Qsum += Fi @ Q @ Fi.T
        Fi = Fi @ F
    assert np.allclose(Qsum, cv_model(2, 0.7, 0.3)[2])

    # 3. the worked example reproduces the numbers of the chapter
    rows = worked_example()
    K1 = rows[0]["K"]
    assert np.allclose([K1[0, 0], K1[2, 0]], WORKED_EXPECTED["K1"], atol=5e-4)
    assert np.allclose(K1[0, 0], K1[1, 1]) and np.allclose(K1[2, 0], K1[3, 1])
    assert np.allclose(rows[-1]["x"], WORKED_EXPECTED["x5"], atol=5e-4)
    P5 = rows[-1]["P"]
    assert np.allclose([P5[0, 0], P5[0, 2], P5[2, 2]], WORKED_EXPECTED["P5"],
                       atol=5e-4)
    # the gain of step 1 by hand: a^- = 1 + 1 + q/3, S = a^- + r
    a_minus, b_minus = 1.0 + 1.0 + WORKED_Q / 3.0, 1.0 + WORKED_Q / 2.0
    S1 = a_minus + WORKED_SIGMA ** 2
    assert abs(K1[0, 0] - a_minus / S1) < 1e-12
    assert abs(K1[2, 0] - b_minus / S1) < 1e-12

    # 4. linear-Gaussian simulation, position-only sensor, 10 Hz
    dt, q, sigma, N = 0.1, 0.2, 1.0, 2000
    F, H, Q = cv_model(2, dt, q)
    R = sigma ** 2 * np.eye(2)
    truth, zs = simulate([0, 0, 2.0, 1.0], F, Q, H, R, N, rng)
    x0, P0 = init_two_point(zs[0], zs[1], dt, R)
    assert np.allclose(x0[:2], zs[1])
    assert np.allclose(x0[2:], (np.asarray(zs[1]) - zs[0]) / dt)
    assert np.allclose(P0[2:, 2:], 2 * R / dt ** 2)
    kf = KalmanFilter(F, H, Q, R, x0, P0)
    est, cov, nis, acc = run_filter(kf, zs[2:])
    tru = truth[3:]
    e_kf = rmse(est[:, :2], tru[:, :2])
    e_raw = rmse(np.array(zs[2:]), tru[:, :2])
    assert e_kf < 0.6 * e_raw, (e_kf, e_raw)
    v_fd = (np.array(zs[2:]) - np.array(zs[1:-1])) / dt     # differenced
    e_v_kf = rmse(est[:, 2:], tru[:, 2:])
    e_v_fd = rmse(v_fd, tru[:, 2:])
    assert e_v_kf < 0.1 * e_v_fd, (e_v_kf, e_v_fd)
    # covariance symmetric positive definite at every step
    for P in cov:
        assert np.max(np.abs(P - P.T)) < 1e-12
        assert np.min(np.linalg.eigvalsh(P)) > 0.0
    # NIS consistent: mean in the 99.9 % band, 95 % gate accepts about 95 %
    lo, hi = nis_bounds(len(nis), 2, z=3.3)
    assert lo < np.mean(nis) < hi, (lo, np.mean(nis), hi)
    frac = np.mean(nis <= chi2_threshold(2, 0.95))
    assert 0.93 < frac < 0.97, frac
    # NEES consistent: the estimation errors match P.  NEES values of one
    # run are correlated in time, so the test averages over independent
    # Monte-Carlo runs (final step of each), where the chi-square band holds.
    nees = []
    for _ in range(300):
        tr_mc, zs_mc = simulate([0, 0, 2.0, 1.0], F, Q, H, R, 60, rng)
        x0m, P0m = init_two_point(zs_mc[0], zs_mc[1], dt, R)
        kfm = KalmanFilter(F, H, Q, R, x0m, P0m)
        run_filter(kfm, zs_mc[2:])
        e = tr_mc[-1] - kfm.x
        nees.append(float(e @ np.linalg.solve(kfm.P, e)))
    lo4, hi4 = nis_bounds(len(nees), 4, z=3.3)
    assert lo4 < np.mean(nees) < hi4, (lo4, np.mean(nees), hi4)
    kf2 = KalmanFilter(F, H, Q, R, x0, P0)
    innov = []
    for z in zs[2:]:
        innov.append(kf2.step(z).innovation)
    rho = lag1_autocorrelation(np.array(innov))
    assert np.all(np.abs(rho) < 1.96 / math.sqrt(len(innov))), rho

    # 5. Joseph form equals the short form for the optimal gain; the short
    #    form loses symmetry/definiteness with a perturbed gain, Joseph not
    kfa, kfb = kf.copy(), kf.copy()
    z = truth[-1, :2]
    kfa.predict(); kfb.predict()
    kfa.update(z, joseph=True); kfb.update(z, joseph=False)
    assert np.allclose(kfa.P, kfb.P, atol=1e-12) and np.allclose(kfa.x, kfb.x)
    Pm = 4.0 * np.eye(4)                                   # a wide prior
    Kopt = np.linalg.solve(H @ Pm @ H.T + R, H @ Pm).T
    Kbad = 1.5 * Kopt                                       # a wrong gain
    S = H @ Pm @ H.T + R
    P_opt = (np.eye(4) - Kopt @ H) @ Pm
    I_KH = np.eye(4) - Kbad @ H
    P_joseph = I_KH @ Pm @ I_KH.T + Kbad @ R @ Kbad.T
    P_short = symmetrize(I_KH @ Pm)
    assert np.min(np.linalg.eigvalsh(P_joseph)) > 0.0
    assert np.min(np.linalg.eigvalsh(P_short)) < 0.0     # (1 - 1.2) * 4 < 0
    # Joseph(K) = P_opt + (K - Kopt) S (K - Kopt)^T: the optimal gain wins
    assert np.allclose(P_joseph, P_opt + (Kbad - Kopt) @ S @ (Kbad - Kopt).T)
    assert np.trace(P_joseph) > np.trace(P_opt)

    # 6. gating rejects a wild measurement, the ungated filter jumps
    kfg, kfu, kfp = kf.copy(), kf.copy(), kf.copy()
    kfp.predict()                       # the prediction both start from
    wild = kfp.x[:2] + np.array([40.0, -30.0])
    kfg.predict(); resg = kfg.update(wild, gate_prob=0.99)
    kfu.predict(); resu = kfu.update(wild)
    assert not resg.accepted and resu.accepted
    assert resg.nis > chi2_threshold(2, 0.99)
    assert np.allclose(kfg.x, kfp.x) and np.allclose(kfg.P, kfp.P)
    # the ungated filter moves by K y, a jump of metres towards the outlier
    assert np.allclose(kfu.x - kfp.x, resu.gain @ resu.innovation)
    assert np.linalg.norm(kfu.x[:2] - kfp.x[:2]) > 1.0

    # 7. missing measurements: predict-only steps grow the covariance,
    #    the next update shrinks it
    kfm = kf.copy()
    tr0 = np.trace(kfm.P)
    kfm.step(None); tr1 = np.trace(kfm.P)
    kfm.step(None); tr2 = np.trace(kfm.P)
    kfm.step(truth[-1, :2]); tr3 = np.trace(kfm.P)
    assert tr0 < tr1 < tr2 and tr3 < tr2
    truth_m, zs_m = simulate([0, 0, 2.0, 1.0], F, Q, H, R, 500, rng,
                             p_miss=0.3)
    assert sum(z is None for z in zs_m) > 100
    kfm = KalmanFilter(F, H, Q, R, truth_m[0], np.eye(4))
    est_m, _, _, acc_m = run_filter(kfm, zs_m)
    assert rmse(est_m[:, :2], truth_m[1:, :2]) < e_raw

    # 8. k-step prediction equals k successive predicts; the position
    #    variance grows like q h^3/3 for long horizons
    ahead = kf.predict_ahead(30)
    kfk = kf.copy()
    for j in range(30):
        kfk.predict()
        assert np.allclose(kfk.x, ahead[j][0]) and np.allclose(kfk.P, ahead[j][1])
    var_p = [P[0, 0] for _, P in ahead]
    assert all(v2 > v1 for v1, v2 in zip(var_p, var_p[1:]))
    a, b, c = kf.P[0, 0], kf.P[0, 2], kf.P[2, 2]
    h = 30 * dt
    assert abs(var_p[-1] - (a + 2 * h * b + h * h * c + q * h ** 3 / 3)) < 1e-9

    # 9. observability: positions observable, velocity-only sensor is not
    assert observability_rank(F, H) == 4
    Hv = np.hstack([np.zeros((2, 2)), np.eye(2)])
    assert observability_rank(F, Hv) == 2
    kfv = KalmanFilter(F, Hv, Q, R, x0, P0)
    var_pos = []
    for _ in range(300):
        kfv.step(truth[-1, 2:] + rng.standard_normal(2))
        var_pos.append(kfv.P[0, 0])
    # the unobserved position variance never converges: it keeps growing
    assert var_pos[-1] > var_pos[149] > var_pos[49] > P0[0, 0]
    assert kfv.P[2, 2] < P0[2, 2]              # the observed velocity does

    # 10. position + velocity sensor and the 3D constant-acceleration model
    F4, H4, Q4 = cv_model(2, dt, q, measure_velocity=True)
    R4 = np.diag([1.0, 1.0, 0.5, 0.5]) ** 2
    truth4, zs4 = simulate([0, 0, 2.0, 1.0], F4, Q4, H4, R4, 500, rng)
    kf4 = KalmanFilter(F4, H4, Q4, R4, zs4[0], R4.copy())
    est4, _, nis4, _ = run_filter(kf4, zs4[1:])
    assert rmse(est4[:, :2], truth4[2:, :2]) < 0.6 * rmse(np.array(zs4[1:])[:, :2], truth4[2:, :2])
    lo4v, hi4v = nis_bounds(len(nis4), 4, z=3.3)
    assert lo4v < np.mean(nis4) < hi4v
    Fa, Ha, Qa = ca_model(3, dt, 0.5)
    assert Fa.shape == (9, 9) and Ha.shape == (3, 9)
    assert np.min(np.linalg.eigvalsh(Qa)) > 0.0
    assert observability_rank(Fa, Ha) == 9

    # 11. data association with two intruders and a stray measurement
    fa = KalmanFilter(F, H, Q, R, [0, 0, 1, 0], 0.1 * np.eye(4))
    fb = KalmanFilter(F, H, Q, R, [10, 0, -1, 0], 0.1 * np.eye(4))
    fa.predict(); fb.predict()
    zs_assoc = [np.array([50.0, 50.0]), np.array([9.8, 0.3]),
                np.array([0.2, -0.1])]
    assert nearest_neighbour_association([fa, fb], zs_assoc) == {0: 2, 1: 1}

    # 12. time-varying dt: passing F, Q built for the actual step
    kft = kf.copy()
    Ft, _, Qt = cv_model(2, 0.35, q)
    x_before = kft.x.copy()
    kft.predict(F=Ft, Q=Qt)
    assert np.allclose(kft.x[:2], x_before[:2] + 0.35 * x_before[2:])

    print_worked_example(rows)
    print("simulation: RMSE position KF %.3f m vs raw %.3f m; velocity KF "
          "%.3f m/s vs finite differences %.3f m/s" % (e_kf, e_raw, e_v_kf,
                                                        e_v_fd))
    print("mean NIS %.3f (band %.3f..%.3f), 95%% gate accepts %.3f, mean NEES "
          "%.3f, lag-1 autocorrelation %s" % (np.mean(nis), lo, hi, frac,
                                             np.mean(nees), np.round(rho, 3)))
    print("self-test passed in %.2f s" % (time.time() - t0))


if __name__ == "__main__":
    _self_test()
