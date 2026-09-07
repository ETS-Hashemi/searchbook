#!/usr/bin/env python3
"""Nonlinear filtering: EKF, UKF and the bootstrap particle filter.

Reference implementation for Chapter 19 of "Multi-Agent Path Planning and
Drone Collision Avoidance".

Conventions
-----------
* Coordinated-turn state ``x = (px, py, v, psi, omega)``: position in metres,
  speed in m/s, heading ``psi`` in radians (counter-clockwise from the x axis,
  kept in (-pi, pi]) and turn rate ``omega`` in rad/s (positive = left turn).
* Range-bearing measurement ``z = (r, phi)``: range in metres, bearing in
  radians in (-pi, pi], measured from the sensor position.
* Motion and measurement models accept one state (shape ``(5,)``) or an
  array of N states (shape ``(N, 5)``) and return the matching shape.
* Every difference of angles goes through ``wrap_angle``.

Run ``python3 ch19_nonlinear_filters.py`` for the self-test (a few seconds).
"""
from __future__ import annotations

import math
import time

import numpy as np

TWO_PI = 2.0 * math.pi
OMEGA_EPS = 1e-4        # below this |omega| the straight-line expansion is used


def wrap_angle(theta):
    """Map an angle (scalar or array) to the interval (-pi, pi]."""
    return theta - TWO_PI * np.ceil((theta - math.pi) / TWO_PI)


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class CoordinatedTurnModel:
    """Constant speed and constant turn rate in the plane (polar form).

    Process noise: a longitudinal acceleration a ~ N(0, sigma_a^2) and a
    turn acceleration gamma ~ N(0, sigma_gamma^2), constant over the step,
    enter through the matrix G(x) of the chapter, so Q(x) = G diag(...) G^T.
    """
    dim = 5
    angle_index = (3,)          # the heading is an angle

    def __init__(self, dt, sigma_a=1.0, sigma_gamma=0.1):
        self.dt = float(dt)
        self.sigma_a = float(sigma_a)
        self.sigma_gamma = float(sigma_gamma)

    def f(self, x):
        """One step of the motion model for one state or an (N, 5) array."""
        x = np.asarray(x, dtype=float)
        single = x.ndim == 1
        X = np.atleast_2d(x)
        px, py, v, psi, om = X.T
        dt = self.dt
        small = np.abs(om) < OMEGA_EPS
        om_safe = np.where(small, 1.0, om)
        psi1 = psi + om * dt
        # |omega| < OMEGA_EPS: series in omega to second order (avoids 0/0)
        c, s = np.cos(psi), np.sin(psi)
        dx = np.where(small, v * dt * c - 0.5 * v * om * dt ** 2 * s - v * om ** 2 * dt ** 3 * c / 6.0,
                      v / om_safe * (np.sin(psi1) - np.sin(psi)))
        dy = np.where(small, v * dt * s + 0.5 * v * om * dt ** 2 * c - v * om ** 2 * dt ** 3 * s / 6.0,
                      -v / om_safe * (np.cos(psi1) - np.cos(psi)))
        out = np.column_stack([px + dx, py + dy, v, wrap_angle(psi1), om])
        return out[0] if single else out

    def jacobian(self, x):
        """5 x 5 Jacobian of f at the state x (the chapter's proposition)."""
        _, _, v, psi, om = np.asarray(x, dtype=float)
        dt = self.dt
        F = np.eye(5)
        F[3, 4] = dt
        if abs(om) < OMEGA_EPS:                      # series in omega (omega = 0: the limits)
            s, c = math.sin(psi), math.cos(psi)
            F[0, 2] = dt * c - 0.5 * om * dt ** 2 * s - om ** 2 * dt ** 3 * c / 6.0
            F[0, 3] = -v * dt * s - 0.5 * v * om * dt ** 2 * c + v * om ** 2 * dt ** 3 * s / 6.0
            F[0, 4] = -0.5 * v * dt ** 2 * s - v * om * dt ** 3 * c / 3.0
            F[1, 2] = dt * s + 0.5 * om * dt ** 2 * c - om ** 2 * dt ** 3 * s / 6.0
            F[1, 3] = v * dt * c - 0.5 * v * om * dt ** 2 * s - v * om ** 2 * dt ** 3 * c / 6.0
            F[1, 4] = 0.5 * v * dt ** 2 * c - v * om * dt ** 3 * s / 3.0
        else:
            psi1 = psi + om * dt
            s0, c0, s1, c1 = math.sin(psi), math.cos(psi), math.sin(psi1), math.cos(psi1)
            F[0, 2] = (s1 - s0) / om
            F[0, 3] = v / om * (c1 - c0)
            F[0, 4] = v * dt * c1 / om - v * (s1 - s0) / om ** 2
            F[1, 2] = -(c1 - c0) / om
            F[1, 3] = v / om * (s1 - s0)
            F[1, 4] = v * dt * s1 / om + v * (c1 - c0) / om ** 2
        return F

    def noise_matrix(self, x):
        """G(x): maps the noise (a, gamma) into the state; (5, 2) or (N, 5, 2)."""
        x = np.asarray(x, dtype=float)
        single = x.ndim == 1
        X = np.atleast_2d(x)
        dt = self.dt
        G = np.zeros((X.shape[0], 5, 2))
        G[:, 0, 0] = 0.5 * dt * dt * np.cos(X[:, 3])
        G[:, 1, 0] = 0.5 * dt * dt * np.sin(X[:, 3])
        G[:, 2, 0] = dt
        G[:, 3, 1] = 0.5 * dt * dt
        G[:, 4, 1] = dt
        return G[0] if single else G

    def Q(self, x):
        """Process-noise covariance Q(x) = G(x) diag(sa^2, sg^2) G(x)^T."""
        G = self.noise_matrix(x)
        return (G * np.array([self.sigma_a ** 2, self.sigma_gamma ** 2])) @ G.T

    def sample_noise(self, X, rng):
        """One process-noise sample G(x_i) eta_i for every row of X."""
        X = np.atleast_2d(X)
        eta = rng.normal(size=(X.shape[0], 2)) * np.array([self.sigma_a, self.sigma_gamma])
        return np.einsum("nij,nj->ni", self.noise_matrix(X), eta)


class RangeBearingSensor:
    """Range and bearing of the intruder as seen from a fixed sensor."""
    dim = 2
    angle_index = (1,)          # the bearing is an angle

    def __init__(self, pos=(0.0, 0.0), sigma_r=2.0, sigma_phi=0.03):
        self.pos = np.asarray(pos, dtype=float)
        self.sigma_r = float(sigma_r)
        self.sigma_phi = float(sigma_phi)
        self.R = np.diag([self.sigma_r ** 2, self.sigma_phi ** 2])

    def h(self, x):
        """Predicted measurement (r, phi) for one state or an (N, 5) array."""
        x = np.asarray(x, dtype=float)
        single = x.ndim == 1
        X = np.atleast_2d(x)
        dx = X[:, 0] - self.pos[0]
        dy = X[:, 1] - self.pos[1]
        out = np.column_stack([np.hypot(dx, dy), np.arctan2(dy, dx)])
        return out[0] if single else out

    def jacobian(self, x):
        """2 x 5 Jacobian of h at the state x (the chapter's proposition)."""
        dx = x[0] - self.pos[0]
        dy = x[1] - self.pos[1]
        r2 = dx * dx + dy * dy
        r = math.sqrt(r2)
        H = np.zeros((2, 5))
        H[0, 0], H[0, 1] = dx / r, dy / r
        H[1, 0], H[1, 1] = -dy / r2, dx / r2
        return H

    def residual(self, z, z_pred):
        """z - z_pred with the bearing component wrapped; broadcasts over rows."""
        y = np.asarray(z, dtype=float) - np.asarray(z_pred, dtype=float)
        y[..., 1] = wrap_angle(y[..., 1])
        return y

    def log_likelihood(self, z, X):
        """log p(z | x) up to a constant, for every row of X (N, 5)."""
        Y = self.residual(z, self.h(X))
        return -0.5 * (Y[:, 0] ** 2 / self.sigma_r ** 2 + Y[:, 1] ** 2 / self.sigma_phi ** 2)

    def measure(self, x, rng):
        """A noisy measurement of the true state x."""
        z = self.h(x) + rng.normal(size=2) * np.array([self.sigma_r, self.sigma_phi])
        z[1] = wrap_angle(z[1])
        return z

    def to_cartesian(self, z):
        """Position implied by a measurement (r, phi): the converted measurement."""
        z = np.asarray(z, dtype=float)
        r, phi = z[..., 0], z[..., 1]
        return np.stack([self.pos[0] + r * np.cos(phi), self.pos[1] + r * np.sin(phi)], axis=-1)


# ---------------------------------------------------------------------------
# Extended Kalman filter
# ---------------------------------------------------------------------------
class ExtendedKalmanFilter:
    """EKF for a motion model with .f/.jacobian/.Q and a sensor with .h/.jacobian/.R."""

    def __init__(self, motion, sensor, x0, P0):
        self.motion, self.sensor = motion, sensor
        self.x = np.array(x0, dtype=float)
        self.P = np.array(P0, dtype=float)

    def predict(self):
        """Linearise f at the previous estimate, then move mean and covariance."""
        F = self.motion.jacobian(self.x)              # Jacobian at x_{k-1}
        Q = self.motion.Q(self.x)
        self.x = self.motion.f(self.x)                 # true f for the mean
        self.P = F @ self.P @ F.T + Q
        return self.x, self.P

    def update(self, z):
        """Linearise h at the prediction and apply the Kalman update."""
        H = self.sensor.jacobian(self.x)              # Jacobian at x_k^-
        z_pred = self.sensor.h(self.x)                 # true h for the prediction
        y = self.sensor.residual(z, z_pred)            # innovation, bearing wrapped
        S = H @ self.P @ H.T + self.sensor.R
        K = np.linalg.solve(S.T, (self.P @ H.T).T).T   # K = P H^T S^{-1}
        self.x = self.x + K @ y
        for j in self.motion.angle_index:
            self.x[j] = wrap_angle(self.x[j])
        IKH = np.eye(len(self.x)) - K @ H
        self.P = IKH @ self.P @ IKH.T + K @ self.sensor.R @ K.T   # Joseph form
        self.last = dict(H=H, z_pred=z_pred, y=y, S=S, K=K)
        return self.x, self.P

    def step(self, z=None):
        self.predict()
        if z is not None:
            self.update(z)
        return self.x.copy(), self.P.copy()


# ---------------------------------------------------------------------------
# Unscented transform and unscented Kalman filter
# ---------------------------------------------------------------------------
def sigma_points(mean, cov, alpha=1.0, beta=2.0, kappa=0.0, jitter=1e-9):
    """The 2n+1 sigma points (rows) and the weight vectors W_m, W_c."""
    mean = np.asarray(mean, dtype=float)
    n = mean.size
    lam = alpha ** 2 * (n + kappa) - n
    P = 0.5 * (cov + cov.T) + jitter * np.eye(n)     # symmetrise, guard the factorisation
    L = np.linalg.cholesky((n + lam) * P)            # columns l_i: L L^T = (n+lam) P
    X = np.empty((2 * n + 1, n))
    X[0] = mean
    X[1:n + 1] = mean + L.T                          # row i of L.T is column i of L
    X[n + 1:] = mean - L.T
    W_m = np.full(2 * n + 1, 1.0 / (2.0 * (n + lam)))
    W_c = W_m.copy()
    W_m[0] = lam / (n + lam)
    W_c[0] = lam / (n + lam) + 1.0 - alpha ** 2 + beta
    return X, W_m, W_c


def weighted_mean(Y, W_m, angle_index=()):
    """Weighted mean of the rows of Y; angular columns via wrapped residuals."""
    mean = W_m @ Y
    for j in angle_index:
        mean[j] = wrap_angle(Y[0, j] + W_m @ wrap_angle(Y[:, j] - Y[0, j]))
    return mean


def residuals(Y, mean, angle_index=()):
    """Rows of Y minus mean, wrapped in the angular columns."""
    E = Y - mean
    for j in angle_index:
        E[:, j] = wrap_angle(E[:, j])
    return E


def unscented_transform(X, W_m, W_c, g, x_mean=None, angle_in=(), angle_out=()):
    """Push sigma points through g; return mean, covariance and cross-covariance."""
    Y = g(X)                                         # g must accept an (2n+1, n) array
    y_mean = weighted_mean(Y, W_m, angle_out)
    E = residuals(Y, y_mean, angle_out)
    if x_mean is None:
        x_mean = weighted_mean(X, W_m, angle_in)
    D = residuals(X, x_mean, angle_in)
    P_yy = (E.T * W_c) @ E                           # sum_i W_c[i] e_i e_i^T
    P_xy = (D.T * W_c) @ E
    return y_mean, P_yy, P_xy


class UnscentedKalmanFilter:
    """UKF with additive noise; no Jacobians needed."""

    def __init__(self, motion, sensor, x0, P0, alpha=1.0, beta=2.0, kappa=0.0):
        self.motion, self.sensor = motion, sensor
        self.x = np.array(x0, dtype=float)
        self.P = np.array(P0, dtype=float)
        self.params = (alpha, beta, kappa)

    def predict(self):
        X, W_m, W_c = sigma_points(self.x, self.P, *self.params)
        Q = self.motion.Q(self.x)
        ang = self.motion.angle_index
        self.x, P, _ = unscented_transform(X, W_m, W_c, self.motion.f, self.x, ang, ang)
        self.P = P + Q
        self.last = dict(X=X, X_prop=self.motion.f(X), W_m=W_m, W_c=W_c)
        return self.x, self.P

    def update(self, z):
        X, W_m, W_c = sigma_points(self.x, self.P, *self.params)   # redraw around x_k^-
        z_pred, S, C = unscented_transform(X, W_m, W_c, self.sensor.h, self.x,
                                           self.motion.angle_index, self.sensor.angle_index)
        S = S + self.sensor.R
        K = np.linalg.solve(S.T, C.T).T              # K = C S^{-1}
        y = self.sensor.residual(z, z_pred)
        self.x = self.x + K @ y
        for j in self.motion.angle_index:
            self.x[j] = wrap_angle(self.x[j])
        P = self.P - K @ S @ K.T
        self.P = 0.5 * (P + P.T)
        self.last.update(z_pred=z_pred, y=y, S=S, K=K)
        return self.x, self.P

    def step(self, z=None):
        self.predict()
        if z is not None:
            self.update(z)
        return self.x.copy(), self.P.copy()


# ---------------------------------------------------------------------------
# Particle filter
# ---------------------------------------------------------------------------
def effective_sample_size(weights):
    """N_eff = 1 / sum(w^2) for normalised weights."""
    w = np.asarray(weights, dtype=float)
    return 1.0 / np.sum(w * w)


def systematic_resample(weights, rng):
    """Indices to keep: one uniform draw, N evenly spaced points."""
    n = len(weights)
    positions = (rng.random() + np.arange(n)) / n
    cumulative = np.cumsum(weights)
    cumulative[-1] = 1.0                             # guard against rounding
    return np.searchsorted(cumulative, positions)


class ParticleFilter:
    """Bootstrap (sequential importance resampling) filter with log-weights.

    ``constraint(X)`` may return a boolean mask of feasible states (for example
    "not inside a building"); infeasible particles receive weight zero.
    """

    def __init__(self, motion, sensor, x0, P0, n_particles, rng,
                 resample_threshold=0.5, constraint=None, roughening=None):
        self.motion, self.sensor, self.rng = motion, sensor, rng
        self.n = int(n_particles)
        self.threshold = resample_threshold * self.n
        self.constraint = constraint
        self.roughening = None if roughening is None else np.asarray(roughening, float)
        self.X = rng.multivariate_normal(np.asarray(x0, float), np.asarray(P0, float), size=self.n)
        self.X[:, 2] = np.abs(self.X[:, 2])          # speeds are non-negative
        self.X[:, 3] = wrap_angle(self.X[:, 3])
        self.logw = np.full(self.n, -math.log(self.n))
        self.n_eff = float(self.n)
        self.resample_count = 0
        self.x, self.P = self.estimate()

    @property
    def weights(self):
        return np.exp(self.logw)

    def predict(self):
        """Propagate every particle through f with its own noise sample."""
        self.X = self.motion.f(self.X) + self.motion.sample_noise(self.X, self.rng)
        self.X[:, 3] = wrap_angle(self.X[:, 3])
        return self.X

    def update(self, z=None):
        """Weight by the likelihood, normalise, estimate, resample."""
        if z is not None:
            self.logw += self.sensor.log_likelihood(z, self.X)
        if self.constraint is not None:
            self.logw[~self.constraint(self.X)] = -np.inf
        top = np.max(self.logw)
        if not np.isfinite(top):            # every particle died: flat
            self.logw[:] = -math.log(self.n)
            top = self.logw[0]
        w = np.exp(self.logw - top)         # log-sum-exp normalisation
        w /= np.sum(w)
        with np.errstate(divide="ignore"):
            self.logw = np.log(w)
        self.n_eff = effective_sample_size(w)
        self.x, self.P = self.estimate(w)
        if self.n_eff < self.threshold:
            idx = systematic_resample(w, self.rng)
            self.X = self.X[idx]
            # optional jitter of the copies
            if self.roughening is not None:
                jitter = self.rng.normal(size=self.X.shape)
                self.X = self.X + jitter * self.roughening
            self.logw = np.full(self.n, -math.log(self.n))
            self.resample_count += 1
        return self.x, self.P

    def estimate(self, w=None):
        """Weighted mean (circular for the heading) and covariance of the cloud."""
        if w is None:
            w = self.weights
        mean = w @ self.X
        for j in self.motion.angle_index:
            mean[j] = math.atan2(w @ np.sin(self.X[:, j]), w @ np.cos(self.X[:, j]))
        D = residuals(self.X, mean, self.motion.angle_index)
        return mean, (D.T * w) @ D

    def step(self, z=None):
        self.predict()
        self.update(z)
        return self.x.copy(), self.P.copy()


# ---------------------------------------------------------------------------
# Simulation of a turning target and tracking experiments
# ---------------------------------------------------------------------------
def simulate_turning_target(x0, segments, dt):
    """True states (T+1, 5) of a target flying the given (duration, omega) legs."""
    model = CoordinatedTurnModel(dt)
    x = np.array(x0, dtype=float)
    states = [x.copy()]
    for duration, omega in segments:
        x[4] = omega
        for _ in range(int(round(duration / dt))):
            x = model.f(x)
            x[4] = omega
            states.append(x.copy())
    return np.array(states)


def initial_estimate(z0, z1, sensor, dt, v_max=30.0, sigma_omega=0.3):
    """Track initialisation from two range-bearing measurements.

    Position from the second measurement, speed and heading from the
    displacement between the two (the speed clipped to [0, v_max]), turn rate
    zero.  The standard deviations follow from the measurement noise at that
    range: sigma_p across and along the line of sight, sqrt(2) sigma_p / dt for
    the speed (capped at v_max / 2) and sqrt(2) sigma_p / |displacement| for
    the heading (capped at 1 rad).
    """
    p0, p1 = sensor.to_cartesian(z0), sensor.to_cartesian(z1)
    d = p1 - p0
    speed = min(np.hypot(*d) / dt, v_max)
    heading = math.atan2(d[1], d[0])
    r = z1[0]
    sigma_p = math.sqrt(sensor.sigma_r ** 2 + (r * sensor.sigma_phi) ** 2)
    sigma_v = min(math.sqrt(2.0) * sigma_p / dt, 0.5 * v_max)
    sigma_psi = min(math.sqrt(2.0) * sigma_p / max(np.hypot(*d), 1e-6), 1.0)
    x0 = np.array([p1[0], p1[1], speed, heading, 0.0])
    P0 = np.diag([sigma_p ** 2, sigma_p ** 2, sigma_v ** 2, sigma_psi ** 2, sigma_omega ** 2])
    return x0, P0


def run_tracking(truth, sensor, motion, rng, n_particles=2000, init_error=None,
                 init_heading_std=None, seed_pf=None, roughening=None):
    """Run EKF, UKF and PF on one measurement sequence; return estimates and errors."""
    T = truth.shape[0]
    Z = np.array([sensor.measure(truth[k], rng) for k in range(T)])
    x0, P0 = initial_estimate(Z[0], Z[1], sensor, motion.dt)
    if init_error is not None:
        x0 = x0 + np.asarray(init_error, float)
        x0[3] = wrap_angle(x0[3])
    if init_heading_std is not None:
        P0[3, 3] = init_heading_std ** 2
    pf_rng = np.random.default_rng(seed_pf) if seed_pf is not None else rng
    filters = {
        "ekf": ExtendedKalmanFilter(motion, sensor, x0, P0),
        "ukf": UnscentedKalmanFilter(motion, sensor, x0, P0),
        "pf": ParticleFilter(motion, sensor, x0, P0, n_particles, pf_rng, roughening=roughening),
    }
    est = {name: np.zeros((T, 5)) for name in filters}
    times = {name: 0.0 for name in filters}
    for name, flt in filters.items():
        est[name][1] = flt.x
    for k in range(2, T):
        for name, flt in filters.items():
            t0 = time.perf_counter()
            x, _ = flt.step(Z[k])
            times[name] += time.perf_counter() - t0
            est[name][k] = x
    meas_xy = sensor.to_cartesian(Z)
    errors = {"meas": np.linalg.norm(meas_xy - truth[:, :2], axis=1)}
    for name in filters:
        errors[name] = np.linalg.norm(est[name][:, :2] - truth[:, :2], axis=1)
    return dict(Z=Z, meas_xy=meas_xy, est=est, errors=errors,
                times={n: times[n] / (T - 2) for n in filters})


SETTLE_STEPS = 10           # RMSE is computed after a 5 s settling period (dt = 0.5 s)


def rmse(err, start=SETTLE_STEPS):
    """Root-mean-square of an error sequence after the settling period."""
    e = np.asarray(err[start:], dtype=float)
    return float(np.sqrt(np.mean(e * e)))


TURNING_SEGMENTS = [(4.0, 0.0), (7.0, 0.3), (6.0, 0.0), (5.0, -0.4), (8.0, 0.0)]
TURNING_X0 = (120.0, -100.0, 12.0, math.pi / 2, 0.0)
TURNING_DT = 0.5


def turning_target_truth():
    return simulate_turning_target(TURNING_X0, TURNING_SEGMENTS, TURNING_DT)


# ---------------------------------------------------------------------------
# Worked example: one EKF step and one UKF step by hand
# ---------------------------------------------------------------------------
def worked_example(verbose=True):
    """The one-step worked example of the chapter: returns every intermediate quantity."""
    motion = CoordinatedTurnModel(dt=1.0, sigma_a=1.0, sigma_gamma=0.1)
    sensor = RangeBearingSensor(pos=(0.0, 0.0), sigma_r=2.0, sigma_phi=0.03)
    x_prev = np.array([-100.0, -4.0, 10.0, math.pi, 0.3])
    P_prev = np.diag([4.0, 4.0, 1.0, 0.04, 0.01])
    z = np.array([111.5, 3.12])
    out = dict(x_prev=x_prev, P_prev=P_prev, z=z)

    ekf = ExtendedKalmanFilter(motion, sensor, x_prev, P_prev)
    out["F"] = motion.jacobian(x_prev)
    out["Q"] = motion.Q(x_prev)
    out["ekf_x_pred"], out["ekf_P_pred"] = (a.copy() for a in ekf.predict())
    out["z_pred"] = sensor.h(out["ekf_x_pred"])
    out["y_naive"] = z - out["z_pred"]
    out["ekf_x"], out["ekf_P"] = (a.copy() for a in ekf.update(z))
    out.update({"ekf_" + k: v for k, v in ekf.last.items()})

    ukf = UnscentedKalmanFilter(motion, sensor, x_prev, P_prev, alpha=1.0, beta=2.0, kappa=0.0)
    out["ukf_x_pred"], out["ukf_P_pred"] = (a.copy() for a in ukf.predict())
    out["sigma"] = ukf.last["X"]
    out["sigma_prop"] = ukf.last["X_prop"]
    out["W_m"], out["W_c"] = ukf.last["W_m"], ukf.last["W_c"]
    out["ukf_x"], out["ukf_P"] = (a.copy() for a in ukf.update(z))
    out.update({"ukf_" + k: v for k, v in ukf.last.items() if k in ("z_pred", "y", "S", "K")})

    if verbose:
        np.set_printoptions(precision=4, suppress=True, linewidth=120)
        print("=== worked example: one EKF step ===")
        print("F =\n", out["F"])
        print("predicted mean       :", out["ekf_x_pred"])
        print("predicted P (pos blk):\n", out["ekf_P_pred"][:2, :2])
        print("predicted std devs   :", np.sqrt(np.diag(out["ekf_P_pred"])))
        print("h(x_pred) = (r, phi) :", out["z_pred"])
        print("naive innovation     :", out["y_naive"])
        print("wrapped innovation   :", out["ekf_y"])
        print("H =\n", out["ekf_H"])
        print("S =\n", out["ekf_S"])
        print("K =\n", out["ekf_K"])
        print("updated mean         :", out["ekf_x"])
        print("updated std devs     :", np.sqrt(np.diag(out["ekf_P"])))
        print("=== the same step with the UKF (alpha=1, beta=2, kappa=0) ===")
        print("W_m =", out["W_m"])
        print("W_c =", out["W_c"])
        for i, (a, b) in enumerate(zip(out["sigma"], out["sigma_prop"])):
            print(f"X_{i:<2d} {a[0]:9.3f} {a[1]:8.3f} {a[2]:7.3f} {a[3]:7.3f} {a[4]:6.3f}"
                  f"  ->  {b[0]:9.3f} {b[1]:8.3f}")
        print("UKF predicted mean   :", out["ukf_x_pred"])
        print("UKF predicted stds   :", np.sqrt(np.diag(out["ukf_P_pred"])))
        print("UKF z_pred, innov    :", out["ukf_z_pred"], out["ukf_y"])
        print("UKF updated mean     :", out["ukf_x"])
        print("UKF updated stds     :", np.sqrt(np.diag(out["ukf_P"])))
    return out


# ---------------------------------------------------------------------------
# Worked example: an intruder hidden behind a building (multimodal posterior)
# ---------------------------------------------------------------------------
OCC_BUILDING = (-10.0, 10.0, 50.0, 70.0)     # x_min, x_max, y_min, y_max
OCC_BAND = (35.0, 75.0)                      # no measurements while y is in the band
# north for 4 s, a 1 s left turn at 1 rad/s, 2 s straight, a 1 s right turn, then north
OCC_SEGMENTS = [(4.0, 0.0), (1.0, 1.0), (2.0, 0.0), (1.0, -1.0), (7.0, 0.0)]


def outside_building(X, building=OCC_BUILDING):
    """Boolean mask: True for states whose position is not inside the building."""
    x_min, x_max, y_min, y_max = building
    inside = (X[:, 0] > x_min) & (X[:, 0] < x_max) & (X[:, 1] > y_min) & (X[:, 1] < y_max)
    return ~inside


def occlusion_example(n_particles=2000, seed=19, verbose=True):
    """Track an intruder that turns left behind a building while unobserved."""
    dt = 0.5
    truth = simulate_turning_target((0.0, 5.0, 8.0, math.pi / 2, 0.0), OCC_SEGMENTS, dt)
    T = truth.shape[0]
    rng = np.random.default_rng(seed)
    sensor = RangeBearingSensor(pos=(0.0, 0.0), sigma_r=2.0, sigma_phi=0.05)
    motion = CoordinatedTurnModel(dt, sigma_a=0.5, sigma_gamma=0.3)
    visible = ~((truth[:, 1] >= OCC_BAND[0]) & (truth[:, 1] <= OCC_BAND[1]))
    Z = [sensor.measure(truth[k], rng) if visible[k] else None for k in range(T)]
    x0, P0 = initial_estimate(Z[0], Z[1], sensor, dt)
    pf = ParticleFilter(motion, sensor, x0, P0, n_particles, np.random.default_rng(seed + 1),
                        resample_threshold=0.5, constraint=outside_building)
    ukf = UnscentedKalmanFilter(motion, sensor, x0, P0)
    k_last = int(np.max(np.nonzero(visible[:T // 2])[0]))      # last measurement before the canyon
    k_first = int(np.min(np.nonzero(visible & (np.arange(T) > k_last))[0]))  # first one after it
    k_mid = k_last + 8
    stages = {}
    n_eff, pf_est, ukf_est = [], [x0.copy()], [x0.copy()]
    for k in range(2, T):
        pf.predict()
        pf.update(Z[k])
        ukf.step(Z[k])
        n_eff.append(pf.n_eff)
        pf_est.append(pf.x.copy())
        ukf_est.append(ukf.x.copy())
        if k in (k_last, k_mid, k_first):
            stages[k] = dict(particles=pf.X.copy(), weights=pf.weights.copy(), truth=truth[k, :2].copy(),
                             ukf_mean=ukf.x[:2].copy(), n_eff=pf.n_eff)
    west = np.mean(stages[k_mid]["particles"][:, 0] < OCC_BUILDING[0])
    east = np.mean(stages[k_mid]["particles"][:, 0] > OCC_BUILDING[1])
    near = np.mean(np.linalg.norm(stages[k_first]["particles"][:, :2] - truth[k_first, :2], axis=1) < 15.0)
    px = stages[k_mid]["particles"][:, 0]
    py = stages[k_mid]["particles"][:, 1]
    level = np.mean((px >= OCC_BUILDING[0]) & (px <= OCC_BUILDING[1]))
    inside = np.mean((px >= OCC_BUILDING[0]) & (px <= OCC_BUILDING[1])
                     & (py >= OCC_BUILDING[2]) & (py <= OCC_BUILDING[3]))
    result = dict(truth=truth, Z=Z, visible=visible, stages=stages, n_eff=np.array(n_eff),
                  k_last=k_last, k_mid=k_mid, k_first=k_first, west=west, east=east, near=near,
                  resamples=pf.resample_count, pf_est=np.array(pf_est), ukf_est=np.array(ukf_est),
                  dt=dt, sensor=sensor)
    if verbose:
        print("=== occlusion example ===")
        print(f"steps: {T}, last measurement before the canyon k={k_last} (t={k_last * dt:.1f} s), "
              f"first after it k={k_first} (t={k_first * dt:.1f} s)")
        for k in (k_last, k_mid, k_first):
            s = stages[k]
            print(f"k={k:2d}: truth ({s['truth'][0]:6.1f}, {s['truth'][1]:6.1f})  "
                  f"UKF mean ({s['ukf_mean'][0]:6.1f}, {s['ukf_mean'][1]:6.1f})  N_eff={s['n_eff']:7.1f}")
        print(f"at k={k_mid}: {100 * west:.1f}% of the particles west of the building, "
              f"{100 * east:.1f}% east of it")
        print(f"at k={k_mid}: {100 * level:.1f}% level with the building in x, "
              f"of which {100 * inside:.1f}% lie inside its footprint with weight zero")
        print(f"at k={k_first}: {100 * near:.1f}% of the particles within 15 m of the truth")
        print(f"resampling events: {pf.resample_count} of {T - 2} steps")
    return result


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
def _finite_difference_jacobian(g, x, eps=1e-5):
    x = np.asarray(x, dtype=float)
    g0 = np.atleast_1d(g(x))
    J = np.zeros((g0.size, x.size))
    for j in range(x.size):
        d = np.zeros_like(x)
        d[j] = eps
        J[:, j] = (np.atleast_1d(g(x + d)) - np.atleast_1d(g(x - d))) / (2 * eps)
    return J


def _self_test():
    t_start = time.perf_counter()
    rng = np.random.default_rng(1919)

    # 1. angle wrapping
    assert abs(wrap_angle(math.pi + 0.1) - (-math.pi + 0.1)) < 1e-12
    assert abs(wrap_angle(-math.pi - 0.1) - (math.pi - 0.1)) < 1e-12
    assert abs(wrap_angle(math.pi) - math.pi) < 1e-12 and abs(wrap_angle(-math.pi) - math.pi) < 1e-12
    assert abs(wrap_angle(0.5) - 0.5) < 1e-12 and abs(wrap_angle(7 * math.pi) - math.pi) < 1e-12
    assert np.allclose(wrap_angle(np.array([3.0, -3.0, 6.5])), [3.0, -3.0, 6.5 - TWO_PI])
    assert abs(wrap_angle(3.12 - (-3.0917)) - (-0.0715)) < 1e-4

    # 2. Jacobians against finite differences (turning, almost straight, straight)
    motion = CoordinatedTurnModel(dt=0.7, sigma_a=1.0, sigma_gamma=0.2)
    sensor = RangeBearingSensor(pos=(3.0, -2.0), sigma_r=2.0, sigma_phi=0.03)
    for omega in (0.3, -0.8, 5e-4, 0.0):
        for _ in range(5):
            x = np.array([rng.uniform(-100, 100), rng.uniform(-100, 100), rng.uniform(1, 20),
                          rng.uniform(-math.pi, math.pi), omega])
            # compare with the unwrapped heading so that finite differences are smooth
            def f_unwrapped(s):
                y = motion.f(s)
                y[3] = s[3] + s[4] * motion.dt
                return y
            assert np.allclose(motion.jacobian(x), _finite_difference_jacobian(f_unwrapped, x), atol=1e-5)
            assert np.allclose(sensor.jacobian(x), _finite_difference_jacobian(sensor.h, x), atol=1e-6)
    x_lo = np.array([1.0, 2.0, 10.0, 0.4, OMEGA_EPS * (1 - 1e-9)])
    x_hi = x_lo.copy()
    x_hi[4] = OMEGA_EPS * (1 + 1e-9)
    assert np.allclose(motion.f(x_lo), motion.f(x_hi), atol=1e-6)         # continuity at the threshold
    assert np.allclose(motion.jacobian(x_lo), motion.jacobian(x_hi), atol=1e-5)

    # 3. sigma points: weights sum to one, mean and covariance reproduced, affine exactness
    for n, params in ((5, (1.0, 2.0, 0.0)), (5, (1.0, 2.0, -2.0)), (2, (1.0, 2.0, 1.0)),
                      (3, (1e-3, 2.0, 0.0)), (4, (0.5, 2.0, 3.0))):
        A = rng.normal(size=(n, n))
        P = A @ A.T + n * np.eye(n)
        mean = rng.normal(size=n)
        X, W_m, W_c = sigma_points(mean, P, *params, jitter=0.0)
        assert abs(np.sum(W_m) - 1.0) < 1e-12
        assert np.allclose(W_m @ X, mean, atol=1e-9)
        D = X - mean
        assert np.allclose((D.T * W_c) @ D, P, atol=1e-8)
        B = rng.normal(size=(3, n))
        b = rng.normal(size=3)
        y_mean, P_yy, P_xy = unscented_transform(X, W_m, W_c, lambda S: S @ B.T + b, mean)
        assert np.allclose(y_mean, B @ mean + b, atol=1e-9)
        assert np.allclose(P_yy, B @ P @ B.T, atol=1e-8)
        assert np.allclose(P_xy, P @ B.T, atol=1e-8)

    # 4. effective sample size and systematic resampling
    N = 1000
    assert abs(effective_sample_size(np.full(N, 1.0 / N)) - N) < 1e-9
    one_hot = np.zeros(N)
    one_hot[7] = 1.0
    assert abs(effective_sample_size(one_hot) - 1.0) < 1e-12
    assert abs(effective_sample_size([0.7, 0.1, 0.1, 0.1]) - 1.0 / 0.52) < 1e-12
    w = rng.random(N) ** 4
    w /= w.sum()
    idx = systematic_resample(w, rng)
    counts = np.bincount(idx, minlength=N)
    assert np.all((counts >= np.floor(N * w)) & (counts <= np.floor(N * w) + 1))
    assert counts.sum() == N
    assert abs(effective_sample_size(np.full(N, 1.0 / N)) - N) < 1e-9   # weights after resampling

    # 5. the worked example: wrapping of the innovation, EKF and UKF agree
    ex = worked_example(verbose=False)
    assert abs(ex["y_naive"][1] - 6.2117) < 5e-4 and abs(ex["ekf_y"][1] + 0.0715) < 5e-4
    assert np.allclose(ex["ekf_x_pred"][:2], [-109.850, -5.489], atol=2e-3)
    assert np.linalg.norm(ex["ekf_x"][:2] - ex["ukf_x"][:2]) < 0.5
    assert np.allclose(ex["ekf_P"], ex["ekf_P"].T) and np.all(np.linalg.eigvalsh(ex["ekf_P"]) > 0)
    assert np.all(np.linalg.eigvalsh(ex["ukf_P"]) > 0)

    # 6. all three filters beat the raw measurements on the turning target
    truth = turning_target_truth()
    sensor = RangeBearingSensor(pos=(0.0, 0.0), sigma_r=3.0, sigma_phi=math.radians(2.0))
    motion = CoordinatedTurnModel(TURNING_DT, sigma_a=1.5, sigma_gamma=0.3)
    res = run_tracking(truth, sensor, motion, np.random.default_rng(7), n_particles=1000)
    r_meas = rmse(res["errors"]["meas"])
    for name in ("ekf", "ukf", "pf"):
        assert rmse(res["errors"][name]) < r_meas, (name, rmse(res["errors"][name]), r_meas)

    # 7. the occlusion example is bimodal behind the building and unimodal after it
    occ = occlusion_example(verbose=False)
    assert occ["west"] > 0.15 and occ["east"] > 0.15, (occ["west"], occ["east"])
    assert occ["near"] > 0.9, occ["near"]
    bx0, bx1, by0, by1 = OCC_BUILDING
    gap = occ["ukf_est"][occ["k_last"] + 1:occ["k_first"]]
    assert np.any((gap[:, 0] > bx0) & (gap[:, 0] < bx1) & (gap[:, 1] > by0) & (gap[:, 1] < by1))
    # the Gaussian filter's mean passes through the building while the intruder is hidden

    print(f"all self-tests passed in {time.perf_counter() - t_start:.1f} s")
    print(f"turning target, one run: RMSE meas {r_meas:.2f} m, EKF {rmse(res['errors']['ekf']):.2f} m, "
          f"UKF {rmse(res['errors']['ukf']):.2f} m, PF {rmse(res['errors']['pf']):.2f} m")


if __name__ == "__main__":
    worked_example(verbose=True)
    occlusion_example(verbose=True)
    _self_test()
