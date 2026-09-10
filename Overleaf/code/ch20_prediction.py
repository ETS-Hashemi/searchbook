#!/usr/bin/env python3
"""Trajectory prediction: baselines, metrics, a NumPy LSTM sequence-to-sequence
predictor trained with backpropagation through time, attention, a NumPy
encoder-decoder Transformer predictor, and the helpers that turn a predicted
distribution into planner constraints.

Reference implementation for Chapter 20 of "Multi-Agent Path Planning and
Drone Collision Avoidance".

Conventions
-----------
* A trajectory is an array ``traj[t, :] = (x_t, y_t)`` of planar positions
  sampled every ``DT`` seconds.  The first ``T_OBS`` samples are observed
  (with measurement noise); the next ``T_PRED`` samples are the future that
  has to be predicted (noise-free ground truth).
* Predictions have shape ``(T_PRED, 2)``; batches carry a leading axis.
* Maneuver classes of the synthetic data set: 0 = straight flight,
  1 = gentle turn, 2 = evasive maneuver (a short, sharp turn that starts at
  a random time step ``onset``; it is *visible* if ``onset < T_OBS``).
* The LSTM works in an agent-centered frame: the last observed position is
  the origin, the last observed heading points along +x, and displacements
  are divided by ``SCALE`` so that inputs and targets are of order one.

Run ``python3 ch20_prediction.py`` for the self-test followed by the
experiment of the chapter (about 80 s in total).
"""
from __future__ import annotations

import math
import sys
import time

import numpy as np

DT = 0.2            # sampling interval in seconds
T_OBS = 8           # observed samples (1.6 s)
T_PRED = 12         # predicted samples (2.4 s)
SCALE = 0.5         # typical displacement per step in meters (for normalization)
CLASS_NAMES = ("straight", "turn", "evasive")
TURN_RATE = (0.15, 0.45)          # rad/s, gentle turn
EVASIVE_RATE = (0.8, 1.5)         # rad/s, evasive burst
EVASIVE_ONSET = (2, 10)           # onset step drawn from 2 .. 9 (hidden if >= T_OBS)
EVASIVE_DURATION = (4, 7)         # burst length drawn from 4 .. 6 steps
SUBSETS = ("all", "straight", "turn", "evasive_visible", "evasive_hidden")


# ---------------------------------------------------------------------------
# Synthetic drone trajectories
# ---------------------------------------------------------------------------
def simulate_trajectory(rng, cls, n_steps=T_OBS + T_PRED):
    """Simulate one noise-free trajectory of maneuver class ``cls``.

    The drone flies at constant speed with heading theta; the turn rate
    omega_t is zero (straight), constant (gentle turn) or a short burst
    (evasive maneuver).  Returns ``(positions, onset, rate)``: the onset step
    of the maneuver (-1 unless ``cls == 2``) and the signed turn rate.
    """
    speed = rng.uniform(1.5, 4.0)
    theta = rng.uniform(-math.pi, math.pi)
    pos = rng.uniform(-10.0, 10.0, size=2)
    omega = np.zeros(n_steps)
    onset, rate = -1, 0.0
    if cls == 1:                                   # gentle, constant turn
        rate = rng.choice([-1.0, 1.0]) * rng.uniform(*TURN_RATE)
        omega[:] = rate
    elif cls == 2:                                 # evasive: sharp burst
        onset = int(rng.integers(*EVASIVE_ONSET))
        duration = int(rng.integers(*EVASIVE_DURATION))
        rate = rng.choice([-1.0, 1.0]) * rng.uniform(*EVASIVE_RATE)
        omega[onset:onset + duration] = rate
    traj = np.zeros((n_steps, 2))
    for t in range(n_steps):
        traj[t] = pos
        pos = pos + speed * DT * np.array([math.cos(theta), math.sin(theta)])
        theta += omega[t] * DT
    return traj, onset, rate


def generate_dataset(n, rng, noise=0.05, mix=(0.4, 0.3, 0.3)):
    """Return a dict with ``n`` trajectories drawn from the class mixture.

    Keys: ``clean`` (n, T_OBS+T_PRED, 2) noise-free positions, ``obs``
    (n, T_OBS, 2) observed positions with Gaussian noise of std ``noise``,
    ``future`` (n, T_PRED, 2) ground-truth future, ``cls`` (n,) class id,
    ``onset`` (n,) maneuver onset step (-1 if none), ``rate`` (n,) turn rate.
    """
    cls = rng.choice(3, size=n, p=np.asarray(mix, dtype=float))
    clean = np.zeros((n, T_OBS + T_PRED, 2))
    onset, rate = np.full(n, -1), np.zeros(n)
    for k in range(n):
        clean[k], onset[k], rate[k] = simulate_trajectory(rng, int(cls[k]))
    obs = clean[:, :T_OBS] + noise * rng.standard_normal((n, T_OBS, 2))
    return {"clean": clean, "obs": obs, "future": clean[:, T_OBS:],
            "cls": cls, "onset": onset, "rate": rate}


def subset_mask(data, name):
    """Boolean mask of the trajectories that belong to a named subset."""
    cls, onset = data["cls"], data["onset"]
    if name == "all":
        return np.ones(len(cls), dtype=bool)
    if name == "straight":
        return cls == 0
    if name == "turn":
        return cls == 1
    if name == "evasive_visible":
        return (cls == 2) & (onset < T_OBS)
    if name == "evasive_hidden":
        return (cls == 2) & (onset >= T_OBS)
    raise ValueError(name)


# ---------------------------------------------------------------------------
# Baselines: constant velocity, constant acceleration, Kalman extrapolation
# ---------------------------------------------------------------------------
def estimate_velocity(obs, k=1):
    """Average velocity over the last ``k`` intervals of the observation."""
    return (obs[..., -1, :] - obs[..., -1 - k, :]) / (k * DT)


def predict_cv(obs, horizon=T_PRED, k=1):
    """Constant-velocity extrapolation of the last observed position."""
    v = estimate_velocity(obs, k)
    steps = np.arange(1, horizon + 1) * DT
    return obs[..., -1, None, :] + steps[:, None] * v[..., None, :]


def predict_ca(obs, horizon=T_PRED, k=1):
    """Constant-acceleration extrapolation from finite differences."""
    v1 = (obs[..., -1, :] - obs[..., -1 - k, :]) / (k * DT)
    v0 = (obs[..., -1 - k, :] - obs[..., -1 - 2 * k, :]) / (k * DT)
    a = (v1 - v0) / (k * DT)
    v_last = v1 + 0.5 * a * k * DT       # v1 is the velocity at the midpoint
    steps = np.arange(1, horizon + 1) * DT
    return (obs[..., -1, None, :] + steps[:, None] * v_last[..., None, :]
            + 0.5 * steps[:, None] ** 2 * a[..., None, :])


def kf_cv_matrices(q, r):
    """F, Q, H, R of the constant-velocity Kalman filter with state
    (x, y, vx, vy) and continuous white-noise acceleration of intensity q."""
    F = np.eye(4)
    F[0, 2] = F[1, 3] = DT
    qa = q * np.array([[DT ** 3 / 3.0, DT ** 2 / 2.0], [DT ** 2 / 2.0, DT]])
    Q = np.zeros((4, 4))
    for p, v in ((0, 2), (1, 3)):
        Q[p, p], Q[p, v], Q[v, p], Q[v, v] = qa[0, 0], qa[0, 1], qa[1, 0], qa[1, 1]
    H = np.zeros((2, 4))
    H[0, 0] = H[1, 1] = 1.0
    R = r ** 2 * np.eye(2)
    return F, Q, H, R


def predict_kf(obs, horizon=T_PRED, q=1.0, r=0.05):
    """Run the constant-velocity Kalman filter over the observed window and
    extrapolate ``horizon`` steps.

    Returns ``(means, covs)``: ``means`` has shape (..., horizon, 2); ``covs``
    (horizon, 2, 2) is the position covariance per step, identical for every
    trajectory because the covariance of a linear filter with fixed matrices
    does not depend on the measurements.
    """
    obs = np.asarray(obs, dtype=float)
    single = obs.ndim == 2
    z = obs[None] if single else obs
    F, Q, H, R = kf_cv_matrices(q, r)
    x = np.concatenate([z[:, 1], (z[:, 1] - z[:, 0]) / DT], axis=1)   # (N, 4)
    P = np.diag([r ** 2, r ** 2, 2 * r ** 2 / DT ** 2, 2 * r ** 2 / DT ** 2])
    I4 = np.eye(4)
    for t in range(2, z.shape[1]):
        x = x @ F.T                                   # predict
        P = F @ P @ F.T + Q
        S = H @ P @ H.T + R                           # update
        K = P @ H.T @ np.linalg.inv(S)
        x = x + (z[:, t] - x @ H.T) @ K.T
        P = (I4 - K @ H) @ P @ (I4 - K @ H).T + K @ R @ K.T
    means = np.zeros((z.shape[0], horizon, 2))
    covs = np.zeros((horizon, 2, 2))
    for h in range(horizon):
        x = x @ F.T
        P = F @ P @ F.T + Q
        means[:, h] = x[:, :2]
        covs[h] = H @ P @ H.T
    return (means[0] if single else means), covs


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------
def displacement_errors(pred, gt):
    """Euclidean error at every predicted step, shape (..., horizon)."""
    return np.linalg.norm(np.asarray(pred) - np.asarray(gt), axis=-1)


def ade(pred, gt):
    """Average displacement error over all steps (and all trajectories)."""
    return float(np.mean(displacement_errors(pred, gt)))


def fde(pred, gt):
    """Final displacement error at the last predicted step."""
    return float(np.mean(displacement_errors(pred, gt)[..., -1]))


def ade_fde_per_horizon(pred, gt):
    """ADE_h (mean error over steps 1..h) and FDE_h (error at step h) for
    every horizon h = 1..T; both arrays have length T."""
    err = displacement_errors(pred, gt).reshape(-1, np.shape(pred)[-2])
    mean_err = err.mean(axis=0)
    ade_h = np.cumsum(mean_err) / np.arange(1, len(mean_err) + 1)
    return ade_h, mean_err


def min_ade_k(samples, gt):
    """minADE_k: for each trajectory the best of k samples, then the mean.
    ``samples`` has shape (N, k, T, 2), ``gt`` (N, T, 2)."""
    err = displacement_errors(samples, gt[:, None]).mean(axis=-1)   # (N, k)
    return float(err.min(axis=1).mean())


def min_fde_k(samples, gt):
    """minFDE_k: best final error among k samples, averaged over N."""
    err = displacement_errors(samples, gt[:, None])[..., -1]        # (N, k)
    return float(err.min(axis=1).mean())


def miss_rate(pred, gt, threshold=1.0):
    """Fraction of trajectories whose final error exceeds ``threshold``."""
    return float(np.mean(displacement_errors(pred, gt)[..., -1] > threshold))


def collision_rate(pred, others, d_min):
    """Fraction of predicted trajectories that come closer than ``d_min`` to
    any other agent at the same time step.  ``pred`` (N, T, 2); ``others``
    (N, M, T, 2) holds the trajectories of M other agents per scene."""
    d = np.linalg.norm(np.asarray(pred)[:, None] - np.asarray(others), axis=-1)
    return float(np.mean(np.any(d < d_min, axis=(1, 2))))


def calibration(means, covs, gt, p=0.95):
    """Fraction of ground-truth positions inside the p-probability ellipse of
    the predicted Gaussian, per horizon step (length T).  ``covs`` may be
    (N, T, 2, 2) or (T, 2, 2) (shared by all trajectories)."""
    covs = np.broadcast_to(covs, np.shape(means) + (2,))
    resid = np.asarray(gt) - np.asarray(means)
    maha2 = np.einsum("nti,ntij,ntj->nt", resid, np.linalg.inv(covs), resid)
    return np.mean(maha2 <= chi2_radius(p) ** 2, axis=0)


# ---------------------------------------------------------------------------
# Agent-centered normalization
# ---------------------------------------------------------------------------
def agent_frame(obs):
    """Origin (N, 2) and rotation (N, 2, 2) of the agent-centered frame: the
    last observed position is the origin and the mean of the last two
    observed displacements points along +x.  ``frame = R @ (p - origin)``."""
    origin = obs[:, -1]
    d = obs[:, -1] - obs[:, -3]
    phi = np.arctan2(d[:, 1], d[:, 0])
    c, s = np.cos(phi), np.sin(phi)
    R = np.stack([np.stack([c, s], -1), np.stack([-s, c], -1)], axis=1)
    return origin, R


def to_frame(points, origin, R):
    """World -> agent frame for points of shape (N, T, 2)."""
    return np.einsum("nij,ntj->nti", R, points - origin[:, None])


def from_frame(points, origin, R):
    """Agent frame -> world for points of shape (N, T, 2)."""
    return origin[:, None] + np.einsum("nji,ntj->nti", R, points)


POS_SCALE = 10.0    # meters; only used by the "absolute" mode below


def prepare_sequences(data, mode="frame"):
    """Inputs and targets of the sequence model.

    ``mode="frame"`` (the method of the chapter): ``x`` (N, T_OBS-1, 2) are the
    observed displacements and ``y`` (N, T_PRED, 2) the future displacements
    (the first one starts at the last observation), both in the agent frame
    and divided by SCALE.  ``mode="world"`` uses world displacements without
    the rotation; ``mode="absolute"`` uses absolute positions divided by
    POS_SCALE as inputs and targets (the pitfall of predicting in absolute
    coordinates, kept for the experiment).  Also returns the frame.
    """
    obs, future = data["obs"], data["future"]
    origin, R = agent_frame(obs)
    if mode == "absolute":
        return obs / POS_SCALE, future / POS_SCALE, (origin, R)
    if mode == "world":
        R = np.tile(np.eye(2), (len(obs), 1, 1))
    full = np.concatenate([obs, future], axis=1)
    disp = np.diff(to_frame(full, origin, R), axis=1) / SCALE
    x, y = disp[:, :T_OBS - 1], disp[:, T_OBS - 1:]
    return x, y, (origin, R)


# ---------------------------------------------------------------------------
# The LSTM cell
# ---------------------------------------------------------------------------
def sigmoid(a):
    """Logistic function 1 / (1 + exp(-a))."""
    return 1.0 / (1.0 + np.exp(-a))


class LSTMCell:
    """One LSTM cell with forget, input and output gates (gate order f, i, o,
    then the candidate g) and its backward pass."""

    def __init__(self, n_in, n_hidden, rng, forget_bias=1.0):
        self.n_in, self.n_hidden = n_in, n_hidden
        bound = math.sqrt(6.0 / (n_in + n_hidden + 4 * n_hidden))
        self.W = rng.uniform(-bound, bound, size=(4 * n_hidden, n_in + n_hidden))
        self.b = np.zeros(4 * n_hidden)
        self.b[:n_hidden] = forget_bias          # start by remembering

    def forward(self, x, h_prev, c_prev):
        """One step.  x (B, n_in), h_prev and c_prev (B, n_hidden)."""
        H = self.n_hidden
        z = np.concatenate([x, h_prev], axis=1)          # [x_t ; h_{t-1}]
        a = z @ self.W.T + self.b                        # pre-activations
        f = sigmoid(a[:, :H])                            # forget gate
        i = sigmoid(a[:, H:2 * H])                       # input gate
        o = sigmoid(a[:, 2 * H:3 * H])                   # output gate
        g = np.tanh(a[:, 3 * H:])                        # candidate values
        c = f * c_prev + i * g                           # new cell state
        tc = np.tanh(c)
        h = o * tc                                       # new hidden state
        cache = (z, f, i, o, g, c_prev, tc)
        return h, c, cache

    def backward(self, dh, dc, cache, grads):
        """Backward step: dh, dc are the loss gradients w.r.t. h_t and c_t
        (the latter arriving from step t+1).  Accumulates dW, db in ``grads``
        and returns (dx, dh_prev, dc_prev)."""
        z, f, i, o, g, c_prev, tc = cache
        do = dh * tc
        dc = dc + dh * o * (1.0 - tc ** 2)
        df, di, dg, dc_prev = dc * c_prev, dc * g, dc * i, dc * f
        da = np.concatenate([df * f * (1 - f), di * i * (1 - i),
                             do * o * (1 - o), dg * (1 - g ** 2)], axis=1)
        grads["W"] += da.T @ z
        grads["b"] += da.sum(axis=0)
        dz = da @ self.W
        return dz[:, :self.n_in], dz[:, self.n_in:], dc_prev


def lstm_cell_example():
    """A hand-sized cell step (2 inputs, 2 hidden units) with fixed weights,
    used for the numeric example of the chapter."""
    rng = np.random.default_rng(0)
    cell = LSTMCell(2, 2, rng)
    cell.W = np.array([[0.5, -0.5, 0.3, 0.1],     # forget gate rows
                       [0.2, 0.4, -0.3, 0.6],
                       [1.0, 0.0, 0.2, -0.4],     # input gate rows
                       [-0.5, 0.8, 0.1, 0.3],
                       [0.3, 0.3, -0.6, 0.2],     # output gate rows
                       [0.7, -0.2, 0.4, 0.5],
                       [0.9, -0.6, 0.0, 0.8],     # candidate rows
                       [-0.4, 0.5, 0.7, -0.1]])
    cell.b = np.array([1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    x = np.array([[1.0, -0.5]])
    h_prev = np.array([[0.2, -0.1]])
    c_prev = np.array([[0.5, -0.3]])
    h, c, cache = cell.forward(x, h_prev, c_prev)
    z, f, i, o, g, _, tc = cache
    a = z @ cell.W.T + cell.b
    return {"x": x[0], "h_prev": h_prev[0], "c_prev": c_prev[0], "a": a[0],
            "f": f[0], "i": i[0], "o": o[0], "g": g[0], "c": c[0],
            "tanh_c": tc[0], "h": h[0]}


# ---------------------------------------------------------------------------
# Sequence-to-sequence predictor
# ---------------------------------------------------------------------------
class Seq2SeqPredictor:
    """Encoder LSTM over the observed displacements, decoder LSTM that rolls
    out the future one step at a time.  With ``gaussian=True`` every decoder
    step outputs the mean and log-std of the next displacement and the loss
    is the Gaussian negative log-likelihood; otherwise it outputs the mean
    only and the loss is the mean squared error of the positions.  With
    ``residual=True`` the decoder output is added to the mean observed
    displacement, so that a zero output reproduces constant velocity.  With
    ``cumulative=False`` the outputs are positions instead of displacements
    (only used for the absolute-coordinates variant)."""

    def __init__(self, n_hidden=32, gaussian=True, residual=True, cumulative=True, rng=None):
        rng = np.random.default_rng(0) if rng is None else rng
        self.n_hidden, self.gaussian = n_hidden, gaussian
        self.residual, self.cumulative = residual, cumulative
        self.enc = LSTMCell(2, n_hidden, rng)
        self.dec = LSTMCell(2, n_hidden, rng)
        n_out = 4 if gaussian else 2
        self.W_out = 0.1 * rng.standard_normal((n_out, n_hidden)) / math.sqrt(n_hidden)
        self.b_out = np.zeros(n_out)

    # -- parameters ----------------------------------------------------------
    def params(self):
        return {"enc.W": self.enc.W, "enc.b": self.enc.b, "dec.W": self.dec.W,
                "dec.b": self.dec.b, "W_out": self.W_out, "b_out": self.b_out}

    def set_params(self, values):
        for name, val in values.items():
            self.params()[name][...] = val

    # -- forward -------------------------------------------------------------
    def encode(self, x):
        """Run the encoder over x (B, T_obs-1, 2); returns h, c, caches."""
        B = x.shape[0]
        h = np.zeros((B, self.n_hidden))
        c = np.zeros((B, self.n_hidden))
        caches = []
        for t in range(x.shape[1]):
            h, c, cache = self.enc.forward(x[:, t], h, c)
            caches.append(cache)
        return h, c, caches

    def baseline(self, x):
        """Displacement added to every decoder output: the mean observed
        displacement (constant velocity) if ``residual``, otherwise zero."""
        return x.mean(axis=1) if self.residual else np.zeros((x.shape[0], 2))

    def decode(self, x_last, h, c, horizon, base, y_true=None, rng=None):
        """Roll the decoder out for ``horizon`` steps.  The first input is the
        last observed displacement.  Later inputs are the true displacements
        (teacher forcing, if ``y_true`` is given), sampled displacements (if
        ``rng`` is given) or the predicted means (free running)."""
        u = x_last
        outs, hs, caches = [], [], []
        for k in range(horizon):
            h, c, cache = self.dec.forward(u, h, c)
            out = h @ self.W_out.T + self.b_out
            out[:, :2] += base                         # residual over CV
            outs.append(out)
            hs.append(h)
            caches.append(cache)
            mu = out[:, :2]
            if y_true is not None:
                u = y_true[:, k]
            elif rng is not None and self.gaussian:
                u = mu + np.exp(out[:, 2:]) * rng.standard_normal(mu.shape)
            else:
                u = mu
        return np.stack(outs, axis=1), hs, caches

    def loss_and_grads(self, x, y, teacher_forcing=False):
        """Forward pass, loss, and gradients by backpropagation through time.

        With ``teacher_forcing=True`` the decoder is fed the true displacements
        and no gradient flows through its inputs; otherwise it is fed its own
        predicted means, exactly as at prediction time, and the gradient also
        flows back through the fed-back predictions.
        """
        B, T = y.shape[0], y.shape[1]
        h, c, enc_caches = self.encode(x)
        outs, hs, dec_caches = self.decode(x[:, -1], h, c, T, self.baseline(x),
                                           y_true=y if teacher_forcing else None)
        mu = outs[:, :, :2]
        if self.gaussian:
            log_sigma = outs[:, :, 2:]
            inv_var = np.exp(-2.0 * log_sigma)
            resid = y - mu
            loss = np.mean(np.sum(log_sigma + 0.5 * resid ** 2 * inv_var
                                  + 0.5 * math.log(2 * math.pi), axis=2))
            d_out = np.concatenate([-resid * inv_var,
                                    1.0 - resid ** 2 * inv_var], axis=2) / (B * T)
        elif self.cumulative:
            pos_pred, pos_true = np.cumsum(mu, axis=1), np.cumsum(y, axis=1)
            loss = np.mean(np.sum((pos_pred - pos_true) ** 2, axis=2))
            d_pos = 2.0 * (pos_pred - pos_true) / (B * T)
            d_out = np.cumsum(d_pos[:, ::-1], axis=1)[:, ::-1]   # sum_{j>=k}
        else:
            loss = np.mean(np.sum((mu - y) ** 2, axis=2))
            d_out = 2.0 * (mu - y) / (B * T)
        grads = {name: np.zeros_like(p) for name, p in self.params().items()}
        genc = {"W": grads["enc.W"], "b": grads["enc.b"]}
        gdec = {"W": grads["dec.W"], "b": grads["dec.b"]}
        dh_next = np.zeros((B, self.n_hidden))
        dc_next = np.zeros((B, self.n_hidden))
        du_next = np.zeros((B, 2))                         # d loss / d (fed-back input)
        for k in reversed(range(T)):                       # decoder BPTT
            d_out_k = d_out[:, k].copy()
            if not teacher_forcing:
                d_out_k[:, :2] += du_next                  # through u_{k+1} = mu_k
            grads["W_out"] += d_out_k.T @ hs[k]
            grads["b_out"] += d_out_k.sum(axis=0)
            dh = d_out_k @ self.W_out + dh_next
            du_next, dh_next, dc_next = self.dec.backward(dh, dc_next, dec_caches[k], gdec)
        for t in reversed(range(x.shape[1])):              # encoder BPTT
            _, dh_next, dc_next = self.enc.backward(dh_next, dc_next, enc_caches[t], genc)
        return float(loss), grads

    # -- inference -----------------------------------------------------------
    def _positions(self, outs):
        mu = outs[:, :, :2]
        return np.cumsum(mu, axis=1) if self.cumulative else mu

    def predict_frame(self, x, horizon=T_PRED):
        """Free-running mean rollout.  Returns positions (B, horizon, 2) in the
        normalized frame and the per-step std (B, horizon, 2) (ones for the
        MSE model)."""
        h, c, _ = self.encode(x)
        outs, _, _ = self.decode(x[:, -1], h, c, horizon, self.baseline(x))
        pos = self._positions(outs)
        std = np.exp(outs[:, :, 2:]) if self.gaussian else np.ones_like(pos)
        return pos, std

    def sample_frame(self, x, n_samples, rng, horizon=T_PRED):
        """``n_samples`` autoregressive rollouts with sampled displacements;
        returns positions (B, n_samples, horizon, 2) in the normalized frame."""
        B = x.shape[0]
        xr = np.repeat(x, n_samples, axis=0)
        h, c, _ = self.encode(xr)
        outs, _, _ = self.decode(xr[:, -1], h, c, horizon, self.baseline(xr), rng=rng)
        return self._positions(outs).reshape(B, n_samples, horizon, 2)


def predict_lstm(model, data, mode="frame", n_samples=0, rng=None):
    """World-frame prediction of a trained model on a data set.

    Returns ``(means, covs, samples)``: ``means`` (N, T_PRED, 2); ``covs``
    (N, T_PRED, 2, 2) the position covariance per step obtained by summing
    the per-step displacement variances (None for the MSE model); ``samples``
    (N, n_samples, T_PRED, 2) or None.
    """
    x, _, (origin, R) = prepare_sequences(data, mode)
    pos, std = model.predict_frame(x)
    if mode == "absolute":
        means = pos * POS_SCALE
        scale, unrotate = POS_SCALE, np.tile(np.eye(2), (len(x), 1, 1))
    else:
        means = from_frame(pos * SCALE, origin, R)
        scale, unrotate = SCALE, R
    covs = None
    if model.gaussian:
        var = (np.cumsum(std ** 2, axis=1) if model.cumulative else std ** 2) * scale ** 2
        D = np.zeros(var.shape + (2,))
        D[..., 0, 0], D[..., 1, 1] = var[..., 0], var[..., 1]
        covs = np.einsum("nji,ntjk,nkl->ntil", unrotate, D, unrotate)   # R^T D R
    samples = None
    if n_samples > 0 and model.gaussian:
        s = model.sample_frame(x, n_samples, rng) * scale
        if mode == "absolute":
            samples = s
        else:
            samples = np.stack([from_frame(s[:, j], origin, R) for j in range(n_samples)], axis=1)
    return means, covs, samples


# ---------------------------------------------------------------------------
# Training: Adam, gradient clipping, early stopping
# ---------------------------------------------------------------------------
class Adam:
    """Adam optimizer (Kingma and Ba 2015) over a dict of parameter arrays."""

    def __init__(self, params, lr=3e-3, beta1=0.9, beta2=0.999, eps=1e-8):
        self.params, self.lr, self.b1, self.b2, self.eps = params, lr, beta1, beta2, eps
        self.m = {k: np.zeros_like(v) for k, v in params.items()}
        self.v = {k: np.zeros_like(v) for k, v in params.items()}
        self.t = 0

    def step(self, grads):
        self.t += 1
        for k, p in self.params.items():
            g = grads[k]
            self.m[k] = self.b1 * self.m[k] + (1 - self.b1) * g
            self.v[k] = self.b2 * self.v[k] + (1 - self.b2) * g * g
            m_hat = self.m[k] / (1 - self.b1 ** self.t)
            v_hat = self.v[k] / (1 - self.b2 ** self.t)
            p -= self.lr * m_hat / (np.sqrt(v_hat) + self.eps)


def clip_gradients(grads, max_norm=5.0):
    """Scale all gradients so that their global norm is at most max_norm."""
    norm = math.sqrt(sum(float(np.sum(g * g)) for g in grads.values()))
    if norm > max_norm:
        for g in grads.values():
            g *= max_norm / norm
    return norm


def train_predictor(model, train, val, epochs=60, batch_size=64, lr=5e-3,
                    lr_final=5e-4, patience=10, mode="frame", tf_epochs=0,
                    rng=None, verbose=False):
    """Mini-batch training with Adam, a geometric learning-rate decay from
    ``lr`` to ``lr_final`` over ``epochs``, teacher forcing during the first
    ``tf_epochs`` epochs and free-running training afterward, and early
    stopping on the validation ADE (free-running rollout, in meters).
    Restores the best parameters and returns the training history."""
    rng = np.random.default_rng(1) if rng is None else rng
    x_tr, y_tr, _ = prepare_sequences(train, mode)
    opt = Adam(model.params(), lr=lr)
    decay = (lr_final / lr) ** (1.0 / max(1, epochs - 1))
    history = {"train_loss": [], "val_ade": []}
    best_ade, best_params, best_epoch, bad_epochs = np.inf, None, 0, 0
    n = x_tr.shape[0]
    for epoch in range(epochs):
        opt.lr = lr * decay ** epoch
        order = rng.permutation(n)
        losses = []
        for start in range(0, n, batch_size):
            idx = order[start:start + batch_size]
            loss, grads = model.loss_and_grads(x_tr[idx], y_tr[idx],
                                               teacher_forcing=epoch < tf_epochs)
            clip_gradients(grads)
            opt.step(grads)
            losses.append(loss)
        means, _, _ = predict_lstm(model, val, mode)
        val_ade = ade(means, val["future"])
        history["train_loss"].append(float(np.mean(losses)))
        history["val_ade"].append(val_ade)
        if verbose:
            print("  epoch %3d  train loss %8.4f  val ADE %.4f m"
                  % (epoch + 1, history["train_loss"][-1], val_ade))
        if val_ade < best_ade - 1e-4:
            best_ade, best_epoch, bad_epochs = val_ade, epoch + 1, 0
            best_params = {k: v.copy() for k, v in model.params().items()}
        else:
            bad_epochs += 1
            if bad_epochs >= patience:
                break
    model.set_params(best_params)
    history["best_epoch"] = best_epoch
    return history


# ---------------------------------------------------------------------------
# Attention (Transformer building blocks)
# ---------------------------------------------------------------------------
def softmax(a, axis=-1):
    """Numerically stable softmax along an axis."""
    a = a - np.max(a, axis=axis, keepdims=True)
    e = np.exp(a)
    return e / np.sum(e, axis=axis, keepdims=True)


def scaled_dot_product_attention(Q, K, V, mask=None):
    """softmax(Q K^T / sqrt(d_k)) V.  Q (n_q, d_k), K (n_k, d_k), V (n_k, d_v);
    ``mask`` (n_q, n_k) is True where attention is forbidden."""
    scores = Q @ K.T / math.sqrt(Q.shape[-1])
    if mask is not None:
        scores = np.where(mask, -np.inf, scores)
    weights = softmax(scores, axis=-1)
    return weights @ V, weights


def multi_head_attention(Xq, Xkv, Wq, Wk, Wv, Wo, n_heads, mask=None):
    """Multi-head attention: the model dimension d is split into n_heads
    heads of size d/n_heads, each with its own projections."""
    d = Wq.shape[1]
    dh = d // n_heads
    Q, K, V = Xq @ Wq, Xkv @ Wk, Xkv @ Wv
    heads, weights = [], []
    for j in range(n_heads):
        sl = slice(j * dh, (j + 1) * dh)
        out, w = scaled_dot_product_attention(Q[:, sl], K[:, sl], V[:, sl], mask)
        heads.append(out)
        weights.append(w)
    return np.concatenate(heads, axis=-1) @ Wo, np.stack(weights)


def positional_encoding(n_positions, d):
    """Sinusoidal positional encoding of Vaswani et al. (2017), (n, d)."""
    pos = np.arange(n_positions)[:, None]
    k = np.arange(0, d, 2)[None, :]
    angle = pos / (10000.0 ** (k / d))
    pe = np.zeros((n_positions, d))
    pe[:, 0::2] = np.sin(angle)
    pe[:, 1::2] = np.cos(angle)[:, :pe[:, 1::2].shape[1]]
    return pe


TOY_AGENTS_POS = np.array([[0.0, 0.0], [8.0, -2.0], [3.0, 3.0], [-6.0, -5.0]])
TOY_AGENTS_VEL = np.array([[2.0, 0.0], [-1.75, 1.25], [1.5, 1.5], [0.0, 1.0]])


def toy_agent_attention(pos, vel, tau=2.0, ell=2.0):
    """Attention across agents with hand-set query and key maps.

    Each agent is a token.  With the augmented features
    k_j = (x_j, |x_j|^2, 1) and q_i = (x_i, -1/2, -|x_i|^2/2) * sqrt(d)/ell^2,
    where x = p + tau * v is the position extrapolated tau seconds ahead,
    the scaled dot product equals -|x_i - x_j|^2 / (2 ell^2): agents whose
    extrapolated positions are close get a large weight.  A trained model
    learns such maps from data; this one only illustrates the mechanism.
    """
    x = np.asarray(pos) + tau * np.asarray(vel)
    sq = np.sum(x ** 2, axis=1, keepdims=True)
    K = np.concatenate([x, sq, np.ones_like(sq)], axis=1)              # (N, 4)
    Q = np.concatenate([x, -0.5 * np.ones_like(sq), -0.5 * sq], axis=1) * (2.0 / ell ** 2)
    V = np.asarray(vel)
    out, weights = scaled_dot_product_attention(Q, K, V)
    return weights, out


# ---------------------------------------------------------------------------
# A Transformer trajectory predictor (encoder-decoder, one attention layer)
# ---------------------------------------------------------------------------
def _split_heads(x, n_heads):
    """(B, T, d) -> (B, n_heads, T, d / n_heads)."""
    b, t, d = x.shape
    return x.reshape(b, t, n_heads, d // n_heads).transpose(0, 2, 1, 3)


def _merge_heads(x):
    """(B, n_heads, T, d_h) -> (B, T, n_heads * d_h)."""
    b, h, t, dh = x.shape
    return x.transpose(0, 2, 1, 3).reshape(b, t, h * dh)


def _softmax_backward(weights, d_weights):
    """Gradient of the scores from the gradient of softmax(scores)."""
    return weights * (d_weights - np.sum(d_weights * weights, axis=-1, keepdims=True))


class TransformerPredictor:
    """Encoder-decoder Transformer for one trajectory, in NumPy.

    Encoder: every observed displacement is embedded linearly into R^d, the
    sinusoidal positional encoding of its time step is added, and one
    multi-head self-attention layer with a residual connection, followed by a
    position-wise tanh feed-forward block (also residual), produces one
    context vector per observed step.

    Decoder: the ``horizon`` future steps are represented by their positional
    encodings mapped through a learned matrix, one query per predicted step;
    one multi-head cross-attention layer reads the encoder outputs and a
    linear head maps each query to one displacement.  All ``horizon``
    displacements leave in a single pass, so there is no autoregression and
    hence no exposure bias, but also no way for step k to see what step k-1
    predicted.  As in the LSTM, the output is a residual over the constant
    velocity of the observation window.

    The interface (``params``, ``loss_and_grads``, ``predict_frame`` and the
    attributes ``gaussian`` and ``cumulative``) is that of
    ``Seq2SeqPredictor``, so ``train_predictor`` and ``predict_lstm`` work
    unchanged.  The layer is deliberately simplified: one layer instead of a
    stack, and no layer normalization, which a deep stack needs and a single
    residual layer does not.
    """

    PARAM_NAMES = ("W_emb", "b_emb", "Wq", "Wk", "Wv", "Wo", "Wf1", "bf1",
                   "Wf2", "bf2", "Wq2", "Wk2", "Wv2", "Wo2", "W_out", "b_out")

    def __init__(self, d_model=24, n_heads=2, d_ff=None, horizon=T_PRED,
                 residual=True, rng=None):
        rng = np.random.default_rng(0) if rng is None else rng
        assert d_model % n_heads == 0
        d = d_model
        dff = 2 * d if d_ff is None else d_ff
        self.d_model, self.n_heads, self.d_ff = d, n_heads, dff
        self.horizon, self.residual = horizon, residual
        self.gaussian, self.cumulative = False, True      # squared error on positions
        s = 1.0 / math.sqrt(d)
        self.W_emb = 0.5 * rng.standard_normal((2, d))
        self.b_emb = np.zeros(d)
        for name in ("Wq", "Wk", "Wv", "Wo", "Wq2", "Wk2", "Wv2", "Wo2"):
            setattr(self, name, rng.standard_normal((d, d)) * s)
        self.Wf1 = rng.standard_normal((d, dff)) * s
        self.bf1 = np.zeros(dff)
        self.Wf2 = rng.standard_normal((dff, d)) / math.sqrt(dff)
        self.bf2 = np.zeros(d)
        self.W_out = 0.1 * rng.standard_normal((2, d)) * s
        self.b_out = np.zeros(2)
        self.pe = positional_encoding(T_OBS + horizon, d)     # fixed, not learned

    # -- parameters ----------------------------------------------------------
    def params(self):
        return {n: getattr(self, n) for n in self.PARAM_NAMES}

    def set_params(self, values):
        for name, val in values.items():
            self.params()[name][...] = val

    def n_params(self):
        return int(sum(p.size for p in self.params().values()))

    def baseline(self, x):
        """Displacement added to every decoder output (constant velocity)."""
        return x.mean(axis=1) if self.residual else np.zeros((x.shape[0], 2))

    # -- forward -------------------------------------------------------------
    def forward(self, x, horizon=None):
        """x (B, T_obs-1, 2) -> displacements (B, horizon, 2) and a cache."""
        P = self.horizon if horizon is None else horizon
        nh, dh = self.n_heads, self.d_model // self.n_heads
        T = x.shape[1]
        Z = x @ self.W_emb + self.b_emb + self.pe[:T]     # embed + positional encoding
        Q, K, V = Z @ self.Wq, Z @ self.Wk, Z @ self.Wv   # encoder self-attention
        qh, kh, vh = _split_heads(Q, nh), _split_heads(K, nh), _split_heads(V, nh)
        A = softmax(np.einsum("bhtd,bhsd->bhts", qh, kh) / math.sqrt(dh))
        C = _merge_heads(np.einsum("bhts,bhsd->bhtd", A, vh))
        Z1 = Z + C @ self.Wo                              # residual connection
        Hff = np.tanh(Z1 @ self.Wf1 + self.bf1)
        Z2 = Z1 + Hff @ self.Wf2 + self.bf2               # position-wise feed-forward
        Q2 = self.pe[T_OBS:T_OBS + P] @ self.Wq2          # one query per predicted step
        K2, V2 = Z2 @ self.Wk2, Z2 @ self.Wv2             # decoder cross-attention
        q2h = Q2.reshape(P, nh, dh).transpose(1, 0, 2)
        k2h, v2h = _split_heads(K2, nh), _split_heads(V2, nh)
        A2 = softmax(np.einsum("hpd,bhtd->bhpt", q2h, k2h) / math.sqrt(dh))
        C2 = _merge_heads(np.einsum("bhpt,bhtd->bhpd", A2, v2h))
        Z3 = Q2 + C2 @ self.Wo2
        out = Z3 @ self.W_out.T + self.b_out + self.baseline(x)[:, None]
        cache = (x, Z, qh, kh, vh, A, C, Z1, Hff, Z2, self.pe[T_OBS:T_OBS + P],
                 q2h, k2h, v2h, A2, C2, Z3)
        return out, cache

    # -- loss and backward ---------------------------------------------------
    def loss_and_grads(self, x, y, teacher_forcing=False):
        """Squared error of the predicted positions and its exact gradient.

        ``teacher_forcing`` is accepted for interface compatibility and has no
        meaning here: the decoder is not autoregressive, so it is never fed
        its own output.
        """
        del teacher_forcing
        B, P = y.shape[0], y.shape[1]
        nh, dh = self.n_heads, self.d_model // self.n_heads
        out, cache = self.forward(x, horizon=P)
        (x, Z, qh, kh, vh, A, C, Z1, Hff, Z2, pe_dec, q2h, k2h, v2h, A2, C2, Z3) = cache
        pos_pred, pos_true = np.cumsum(out, axis=1), np.cumsum(y, axis=1)
        loss = np.mean(np.sum((pos_pred - pos_true) ** 2, axis=2))
        d_pos = 2.0 * (pos_pred - pos_true) / (B * P)
        d_out = np.cumsum(d_pos[:, ::-1], axis=1)[:, ::-1]         # sum_{j >= k}

        g = {n: np.zeros_like(p) for n, p in self.params().items()}
        # -- head
        g["W_out"] += np.einsum("bpo,bpd->od", d_out, Z3)
        g["b_out"] += d_out.sum(axis=(0, 1))
        dZ3 = d_out @ self.W_out
        # -- decoder cross-attention
        dQ2 = dZ3.sum(axis=0)                                      # residual branch
        g["Wo2"] += np.einsum("bpi,bpj->ij", C2, dZ3)
        dC2h = _split_heads(dZ3 @ self.Wo2.T, nh)
        dA2 = _softmax_backward(A2, np.einsum("bhpd,bhtd->bhpt", dC2h, v2h))
        dv2h = np.einsum("bhpt,bhpd->bhtd", A2, dC2h)
        dq2h = np.einsum("bhpt,bhtd->hpd", dA2, k2h) / math.sqrt(dh)
        dk2h = np.einsum("bhpt,hpd->bhtd", dA2, q2h) / math.sqrt(dh)
        dQ2 = dQ2 + dq2h.transpose(1, 0, 2).reshape(P, self.d_model)
        g["Wq2"] += pe_dec.T @ dQ2
        dK2, dV2 = _merge_heads(dk2h), _merge_heads(dv2h)
        g["Wk2"] += np.einsum("bti,btj->ij", Z2, dK2)
        g["Wv2"] += np.einsum("bti,btj->ij", Z2, dV2)
        dZ2 = dK2 @ self.Wk2.T + dV2 @ self.Wv2.T
        # -- feed-forward block
        g["Wf2"] += np.einsum("bti,btj->ij", Hff, dZ2)
        g["bf2"] += dZ2.sum(axis=(0, 1))
        dPre = (dZ2 @ self.Wf2.T) * (1.0 - Hff ** 2)
        g["Wf1"] += np.einsum("bti,btj->ij", Z1, dPre)
        g["bf1"] += dPre.sum(axis=(0, 1))
        dZ1 = dZ2 + dPre @ self.Wf1.T
        # -- encoder self-attention
        g["Wo"] += np.einsum("bti,btj->ij", C, dZ1)
        dCh = _split_heads(dZ1 @ self.Wo.T, nh)
        dA = _softmax_backward(A, np.einsum("bhtd,bhsd->bhts", dCh, vh))
        dvh = np.einsum("bhts,bhtd->bhsd", A, dCh)
        dqh = np.einsum("bhts,bhsd->bhtd", dA, kh) / math.sqrt(dh)
        dkh = np.einsum("bhts,bhtd->bhsd", dA, qh) / math.sqrt(dh)
        dQ, dK, dV = _merge_heads(dqh), _merge_heads(dkh), _merge_heads(dvh)
        g["Wq"] += np.einsum("bti,btj->ij", Z, dQ)
        g["Wk"] += np.einsum("bti,btj->ij", Z, dK)
        g["Wv"] += np.einsum("bti,btj->ij", Z, dV)
        dZ = dZ1 + dQ @ self.Wq.T + dK @ self.Wk.T + dV @ self.Wv.T
        # -- embedding
        g["W_emb"] += np.einsum("bti,btj->ij", x, dZ)
        g["b_emb"] += dZ.sum(axis=(0, 1))
        return float(loss), g

    # -- inference -----------------------------------------------------------
    def predict_frame(self, x, horizon=T_PRED):
        """Rollout in one pass: positions (B, horizon, 2) in the normalized
        frame, and a per-step std of ones (this model has no uncertainty)."""
        out, _ = self.forward(x, horizon=horizon)
        pos = np.cumsum(out, axis=1)
        return pos, np.ones_like(pos)

    def attention_maps(self, x, horizon=T_PRED):
        """Encoder self-attention (B, n_heads, T, T) and decoder
        cross-attention (B, n_heads, horizon, T) weights of a forward pass."""
        _, cache = self.forward(x, horizon=horizon)
        return cache[5], cache[14]

# ---------------------------------------------------------------------------
# From a predicted distribution to planner constraints
# ---------------------------------------------------------------------------
def chi2_radius(p):
    """Mahalanobis radius k such that a 2-D Gaussian has probability p inside
    the k-sigma ellipse: p = 1 - exp(-k^2 / 2)."""
    return math.sqrt(-2.0 * math.log(1.0 - p))


def covariance_ellipse(mean, cov, p=0.95, n_points=48):
    """Points of the p-probability ellipse of N(mean, cov), shape (n, 2)."""
    lam, E = np.linalg.eigh(np.asarray(cov, dtype=float))
    k = chi2_radius(p)
    ang = np.linspace(0.0, 2 * math.pi, n_points + 1)
    circle = np.stack([np.cos(ang), np.sin(ang)], axis=1)
    return np.asarray(mean) + k * circle * np.sqrt(np.maximum(lam, 0.0)) @ E.T


def inflated_radius(cov, p=0.95, r_base=0.0):
    """Radius of the disk that contains the p-ellipse of N(., cov), plus the
    physical radius r_base: the obstacle radius handed to ORCA."""
    lam_max = float(np.max(np.linalg.eigvalsh(np.asarray(cov, dtype=float))))
    return r_base + chi2_radius(p) * math.sqrt(lam_max)


def occupancy_cells(mean, cov, p=0.95, cell=0.5, r_base=0.0):
    """Grid cells (ix, iy) whose center lies inside the p-ellipse inflated by
    r_base: the cost region handed to the grid replanner.  Cell (ix, iy)
    covers [ix*cell, (ix+1)*cell) x [iy*cell, (iy+1)*cell)."""
    mean = np.asarray(mean, dtype=float)
    cov = np.asarray(cov, dtype=float)
    k = chi2_radius(p)
    reach = k * math.sqrt(float(np.max(np.linalg.eigvalsh(cov)))) + r_base
    lam, E = np.linalg.eigh(cov)
    cells = set()
    lo = np.floor((mean - reach) / cell).astype(int)
    hi = np.floor((mean + reach) / cell).astype(int)
    for ix in range(lo[0], hi[0] + 1):
        for iy in range(lo[1], hi[1] + 1):
            center = (np.array([ix, iy]) + 0.5) * cell
            y = E.T @ (center - mean)
            # distance to the ellipse in the whitened frame, inflated by r_base
            m = math.sqrt(np.sum(y ** 2 / np.maximum(lam, 1e-12)))
            if m <= k:
                cells.add((ix, iy))
            elif r_base > 0.0:
                # conservative test: shrink the point toward the mean
                direction = center - mean
                dist = np.linalg.norm(direction)
                if dist > 0 and m > k:
                    boundary = mean + direction * (k / m)
                    if np.linalg.norm(center - boundary) <= r_base:
                        cells.add((ix, iy))
    return cells


def chance_constraint_margin(cov, delta, r_base=0.0):
    """Distance the planner must keep from the predicted mean so that the
    probability of being closer than r_base to the obstacle is at most delta,
    using the disk that bounds the (1 - delta)-ellipse."""
    return inflated_radius(cov, 1.0 - delta, r_base)


# ---------------------------------------------------------------------------
# The experiment of the chapter
# ---------------------------------------------------------------------------
def evaluate(pred, data, name="all"):
    """Per-horizon ADE and FDE of ``pred`` on a subset of ``data``."""
    m = subset_mask(data, name)
    return ade_fde_per_horizon(pred[m], data["future"][m])


def run_experiment(seed=20, n_train=1600, n_val=400, n_test=800, noise=0.05,
                   n_hidden=32, epochs=40, d_model=24, n_heads=2, verbose=True):
    """Generate the data, tune the baselines on the validation split, train
    the LSTMs and evaluate everything on the test split.

    Returns a dict with the data sets, the predictions of every method on the
    test split (``preds``), the per-horizon metrics per subset (``metrics``:
    metrics[method][subset] = (ade_h, fde_h)), the tuned baseline settings,
    the training histories, the trained models and the LSTM covariances.
    """
    rng = np.random.default_rng(seed)
    train = generate_dataset(n_train, rng, noise)
    val = generate_dataset(n_val, rng, noise)
    test = generate_dataset(n_test, rng, noise)
    log = print if verbose else (lambda *a, **k: None)

    # -- baselines, tuned on the validation split ------------------------------
    k_cv = min(range(1, T_OBS), key=lambda k: ade(predict_cv(val["obs"], k=k), val["future"]))
    k_ca = min((1, 2, 3), key=lambda k: ade(predict_ca(val["obs"], k=k), val["future"]))
    q_grid = (0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0)
    q_kf = min(q_grid, key=lambda q: ade(predict_kf(val["obs"], q=q, r=noise)[0], val["future"]))
    log("tuned baselines: CV k=%d, CA k=%d, KF q=%.2f (r=%.2f)" % (k_cv, k_ca, q_kf, noise))

    preds = {
        "CV (k=1)": predict_cv(test["obs"], k=1),
        "CV (tuned)": predict_cv(test["obs"], k=k_cv),
        "CA (tuned)": predict_ca(test["obs"], k=k_ca),
    }
    kf_means, kf_covs = predict_kf(test["obs"], q=q_kf, r=noise)
    preds["KF (tuned)"] = kf_means

    # -- learned models --------------------------------------------------------
    models, histories, covs = {}, {}, {"KF (tuned)": kf_covs}
    settings = (("LSTM-NLL", True, "frame", 0), ("LSTM-MSE", False, "frame", 0),
                ("LSTM-abs", True, "absolute", 0), ("LSTM-TF", True, "frame", epochs))
    for name, gaussian, mode, tf_epochs in settings:
        t0 = time.time()
        absolute = mode == "absolute"
        model = Seq2SeqPredictor(n_hidden, gaussian, residual=not absolute,
                                 cumulative=not absolute, rng=np.random.default_rng(seed + 1))
        hist = train_predictor(model, train, val, epochs=epochs, mode=mode, tf_epochs=tf_epochs,
                               rng=np.random.default_rng(seed + 2), verbose=False)
        means, cov, _ = predict_lstm(model, test, mode)
        preds[name], models[name], histories[name] = means, model, hist
        if cov is not None:
            covs[name] = cov
        log("%-9s trained in %5.1f s, best epoch %2d of %2d, val ADE %.3f m"
            % (name, time.time() - t0, hist["best_epoch"], len(hist["val_ade"]),
               min(hist["val_ade"])))

    # -- the Transformer: same data, same optimizer, its own patience -----------
    #    (its validation curve is noisier than the LSTM's, so 10 epochs of
    #    patience stop some initializations while they are still improving)
    t0 = time.time()
    tr = TransformerPredictor(d_model=d_model, n_heads=n_heads,
                              rng=np.random.default_rng(seed + 1))
    hist = train_predictor(tr, train, val, epochs=epochs, mode="frame", patience=15,
                           rng=np.random.default_rng(seed + 2))
    means, _, _ = predict_lstm(tr, test, "frame")
    preds["Transformer"] = means
    models["Transformer"], histories["Transformer"] = tr, hist
    log("%-9s trained in %5.1f s, best epoch %2d of %2d, val ADE %.3f m (%d weights, "
        "d=%d, %d heads)" % ("Transf.", time.time() - t0, hist["best_epoch"],
                             len(hist["val_ade"]), min(hist["val_ade"]), tr.n_params(),
                             d_model, n_heads))

    # -- metrics ---------------------------------------------------------------
    n_params_lstm = sum(p.size for p in models["LSTM-MSE"].params().values())
    metrics = {name: {s: evaluate(p, test, s) for s in SUBSETS} for name, p in preds.items()}
    _, _, samples = predict_lstm(models["LSTM-NLL"], test, "frame", n_samples=20,
                                 rng=np.random.default_rng(seed + 3))
    extra = {"minADE_20": min_ade_k(samples, test["future"]),
             "minFDE_20": min_fde_k(samples, test["future"]),
             "miss_rate": {name: miss_rate(p, test["future"], 1.0) for name, p in preds.items()},
             "calibration": {name: calibration(preds[name], covs[name], test["future"], 0.95)
                             for name in ("KF (tuned)", "LSTM-NLL")}}
    return {"train": train, "val": val, "test": test, "preds": preds, "metrics": metrics,
            "settings": {"k_cv": k_cv, "k_ca": k_ca, "q_kf": q_kf, "noise": noise,
                         "n_params_lstm": n_params_lstm,
                         "n_params_transformer": tr.n_params()},
            "histories": histories, "models": models, "covs": covs, "extra": extra,
            "samples": samples}


def seed_study(n_seeds=3, seed=20, epochs=40, n_hidden=32, d_model=24, n_heads=2,
               noise=0.05, verbose=True):
    """Retrain the three learned predictors with ``n_seeds`` initializations
    and training orders on the *same* data split, and report the mean and the
    standard deviation of their test ADE.

    This is the spread that the coding exercise of the chapter asks for.  It
    is not part of the self-test because it costs about a minute.
    """
    rng = np.random.default_rng(seed)
    train = generate_dataset(1600, rng, noise)
    val = generate_dataset(400, rng, noise)
    test = generate_dataset(800, rng, noise)
    out = {}
    for name in ("LSTM-NLL", "LSTM-MSE", "Transformer"):
        values = []
        for k in range(n_seeds):
            r_init, r_train = np.random.default_rng(seed + 1 + 10 * k), \
                np.random.default_rng(seed + 2 + 10 * k)
            if name == "Transformer":
                model = TransformerPredictor(d_model=d_model, n_heads=n_heads, rng=r_init)
                patience = 15
            else:
                model = Seq2SeqPredictor(n_hidden, gaussian=(name == "LSTM-NLL"), rng=r_init)
                patience = 10
            train_predictor(model, train, val, epochs=epochs, mode="frame",
                            patience=patience, rng=r_train)
            means, _, _ = predict_lstm(model, test, "frame")
            values.append(ade(means, test["future"]))
        v = np.array(values)
        out[name] = (float(v.mean()), float(v.std(ddof=1)), [float(x) for x in v])
        if verbose:
            print("%-12s test ADE %.3f +- %.3f m over %d seeds  %s"
                  % (name, v.mean(), v.std(ddof=1), n_seeds, np.round(v, 3).tolist()))
    return out


def print_results(res):
    """Print the table of the chapter: ADE/FDE at the full horizon per subset."""
    test = res["test"]
    counts = {s: int(subset_mask(test, s).sum()) for s in SUBSETS}
    print("\nADE / FDE in meters at horizon %d steps (%.1f s); test trajectories per subset: %s"
          % (T_PRED, T_PRED * DT, counts))
    print("%-11s" % "method" + "".join("%18s" % s for s in SUBSETS))
    for name, per in res["metrics"].items():
        print("%-11s" % name + "".join("%9.3f/%-8.3f" % (per[s][0][-1], per[s][1][-1]) for s in SUBSETS))
    print("ADE at horizons 4, 8, 12 (all test trajectories):")
    for name, per in res["metrics"].items():
        a = per["all"][0]
        print("  %-11s %.3f  %.3f  %.3f" % (name, a[3], a[7], a[11]))
    ex = res["extra"]
    print("LSTM-NLL minADE_20 = %.3f, minFDE_20 = %.3f" % (ex["minADE_20"], ex["minFDE_20"]))
    print("miss rate (FDE > 1 m): " + ", ".join("%s %.3f" % kv for kv in ex["miss_rate"].items()))
    for name, cal in ex["calibration"].items():
        print("fraction of true positions inside the 95%% ellipse, %s: h=4 %.3f, h=8 %.3f, h=12 %.3f"
              % (name, cal[3], cal[7], cal[11]))
    tr = res["models"].get("Transformer")
    if tr is not None:
        print("weights: Transformer %d, LSTM %d"
              % (res["settings"]["n_params_transformer"], res["settings"]["n_params_lstm"]))
        x, _, _ = prepare_sequences(res["test"], "frame")
        _, dec_w = tr.attention_maps(x)
        w = dec_w.mean(axis=(0, 1, 2))
        print("Transformer decoder attention per observed step: "
              + " ".join("%.3f" % v for v in w)
              + "  (first four %.3f, last three %.3f)" % (w[:4].sum(), w[4:].sum()))


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
def _gradient_check(model, x, y, n_checks=12, rng=None, teacher_forcing=False):
    """Compare BPTT gradients with central finite differences."""
    rng = np.random.default_rng(0) if rng is None else rng
    _, grads = model.loss_and_grads(x, y, teacher_forcing)
    worst = 0.0
    for name, p in model.params().items():
        flat = p.reshape(-1)
        for idx in rng.choice(flat.size, size=min(n_checks, flat.size), replace=False):
            old = flat[idx]
            flat[idx] = old + 1e-5
            lp, _ = model.loss_and_grads(x, y, teacher_forcing)
            flat[idx] = old - 1e-5
            lm, _ = model.loss_and_grads(x, y, teacher_forcing)
            flat[idx] = old
            num = (lp - lm) / 2e-5
            ana = grads[name].reshape(-1)[idx]
            worst = max(worst, abs(num - ana) / max(1e-8, abs(num) + abs(ana)))
    return worst


def _self_test():
    t0 = time.time()
    rng = np.random.default_rng(7)

    # 1. metrics vanish for a perfect predictor and measure a shift exactly
    gt = rng.standard_normal((5, T_PRED, 2))
    assert ade(gt, gt) == 0.0 and fde(gt, gt) == 0.0
    shifted = gt + np.array([3.0, 4.0])
    assert abs(ade(shifted, gt) - 5.0) < 1e-12 and abs(fde(shifted, gt) - 5.0) < 1e-12
    samples = np.stack([shifted, gt, shifted], axis=1)
    assert min_ade_k(samples, gt) == 0.0 and min_fde_k(samples, gt) == 0.0
    ade_h, fde_h = ade_fde_per_horizon(shifted, gt)
    assert np.allclose(ade_h, 5.0) and np.allclose(fde_h, 5.0)
    assert miss_rate(shifted, gt, 1.0) == 1.0 and miss_rate(gt, gt, 1.0) == 0.0
    others = np.stack([gt + np.array([0.3, 0.0]), gt + 10.0], axis=1)  # (N, 2, T, 2)
    assert collision_rate(gt, others, 0.5) == 1.0 and collision_rate(gt, others, 0.1) == 0.0

    # 2. constant velocity is exact on noise-free straight flight, constant
    #    acceleration on a parabola, and the Kalman extrapolation on both
    straight = generate_dataset(20, rng, noise=0.0, mix=(1.0, 0.0, 0.0))
    for k in (1, 3, 7):
        assert ade(predict_cv(straight["obs"], k=k), straight["future"]) < 1e-9
    kf_means, kf_covs = predict_kf(straight["obs"], q=0.5, r=0.05)
    assert ade(kf_means, straight["future"]) < 1e-9
    tr = np.array([np.trace(c) for c in kf_covs])
    assert np.all(np.diff(tr) > 0)                     # uncertainty grows with h
    t = np.arange(T_OBS + T_PRED) * DT
    acc = np.array([0.3, -0.8])
    parab = 2.0 * t[:, None] * np.array([1.0, 0.5]) + 0.5 * t[:, None] ** 2 * acc
    assert ade(predict_ca(parab[:T_OBS]), parab[T_OBS:]) < 1e-9
    assert ade(predict_cv(parab[:T_OBS]), parab[T_OBS:]) > 0.5

    # 3. gate outputs lie in (0, 1), the candidate in (-1, 1)
    cell = LSTMCell(3, 5, rng)
    h, c, cache = cell.forward(rng.standard_normal((4, 3)) * 3, np.zeros((4, 5)), np.zeros((4, 5)))
    _, f, i, o, g, _, _ = cache
    for gate in (f, i, o):
        assert np.all(gate > 0.0) and np.all(gate < 1.0)
    assert np.all(np.abs(g) < 1.0) and np.all(np.abs(h) < 1.0)
    ex = lstm_cell_example()
    assert np.allclose(ex["c"], ex["f"] * ex["c_prev"] + ex["i"] * ex["g"])
    assert np.allclose(ex["h"], ex["o"] * np.tanh(ex["c"]))

    # 4. BPTT gradients agree with finite differences (both losses)
    small = generate_dataset(6, rng, noise=0.05)
    x, y, _ = prepare_sequences(small)
    for gaussian, teacher_forcing in ((True, False), (False, False), (True, True)):
        m = Seq2SeqPredictor(n_hidden=4, gaussian=gaussian, rng=np.random.default_rng(3))
        m.W_out = rng.standard_normal(m.W_out.shape) * 0.3       # non-trivial output layer
        err = _gradient_check(m, x, y, rng=rng, teacher_forcing=teacher_forcing)
        assert err < 1e-6, "gradient check failed: %.2e" % err

    # 5. the agent frame is invertible and puts the last heading on +x
    data = generate_dataset(30, rng, noise=0.05)
    origin, R = agent_frame(data["obs"])
    back = from_frame(to_frame(data["future"], origin, R), origin, R)
    assert np.allclose(back, data["future"])
    d = to_frame(data["obs"][:, -3:], origin, R)
    assert np.allclose(d[:, -1], 0.0) and np.all(d[:, 0, 0] < 0) and np.allclose(d[:, 0, 1], 0.0)

    # 6. training decreases the loss and beats the baseline it starts from
    train = generate_dataset(600, rng, noise=0.05)
    val = generate_dataset(100, rng, noise=0.05)
    model = Seq2SeqPredictor(n_hidden=16, gaussian=True, rng=np.random.default_rng(5))
    hist = train_predictor(model, train, val, epochs=15, lr=1e-2, lr_final=2e-3,
                           patience=15, rng=np.random.default_rng(6))
    assert hist["train_loss"][-1] < hist["train_loss"][0]
    means, covs, samples = predict_lstm(model, val, n_samples=3, rng=rng)
    assert ade(means, val["future"]) < ade(predict_cv(val["obs"], k=T_OBS - 1), val["future"])
    assert means.shape == (100, T_PRED, 2) and covs.shape == (100, T_PRED, 2, 2)
    assert samples.shape == (100, 3, T_PRED, 2)
    assert np.all(np.linalg.eigvalsh(covs) > 0)
    assert np.all(np.diff(np.trace(covs, axis1=2, axis2=3), axis=1) > 0)
    cal = calibration(means, covs, val["future"], 0.95)
    assert cal.shape == (T_PRED,) and np.all(cal >= 0.0) and np.all(cal <= 1.0)
    assert np.allclose(calibration(means, covs, means, 0.95), 1.0)

    # 7. attention rows are probability vectors; identical keys give uniform weights
    Q, K, V = rng.standard_normal((3, 4)), rng.standard_normal((5, 4)), rng.standard_normal((5, 2))
    out, w = scaled_dot_product_attention(Q, K, V)
    assert np.allclose(w.sum(axis=1), 1.0) and np.all(w > 0) and out.shape == (3, 2)
    _, w_same = scaled_dot_product_attention(Q, np.ones((5, 4)), V)
    assert np.allclose(w_same, 0.2)
    mask = np.triu(np.ones((5, 5), dtype=bool), k=1)             # causal mask
    _, w_causal = scaled_dot_product_attention(K, K, V, mask)
    assert np.allclose(np.triu(w_causal, k=1), 0.0) and np.allclose(w_causal.sum(axis=1), 1.0)
    dmodel, heads = 8, 2
    Ws = [rng.standard_normal((dmodel, dmodel)) / math.sqrt(dmodel) for _ in range(4)]
    out_mh, w_mh = multi_head_attention(K @ np.ones((4, dmodel)), K @ np.ones((4, dmodel)), *Ws, heads)
    assert out_mh.shape == (5, dmodel) and w_mh.shape == (heads, 5, 5)
    pe = positional_encoding(T_OBS, dmodel)
    assert np.all(np.abs(pe) <= 1.0) and len({tuple(np.round(r, 6)) for r in pe}) == T_OBS
    pos, vel = TOY_AGENTS_POS, TOY_AGENTS_VEL
    w_ag, _ = toy_agent_attention(pos, vel)
    assert np.allclose(w_ag.sum(axis=1), 1.0)
    x_ext = pos + 2.0 * vel
    expected = softmax(-np.sum((x_ext[:, None] - x_ext[None]) ** 2, axis=-1) / (2 * 2.0 ** 2))
    assert np.allclose(w_ag, expected)

    # 8. the Transformer predictor: exact gradients, shapes, attention rows,
    #    and a short training run that beats the constant-velocity start
    tr = TransformerPredictor(d_model=8, n_heads=2, rng=np.random.default_rng(11))
    err = _gradient_check(tr, x, y, rng=np.random.default_rng(12))
    assert err < 1e-5, "transformer gradient check failed: %.2e" % err
    pos, sd = tr.predict_frame(x)
    assert pos.shape == (x.shape[0], T_PRED, 2) and np.allclose(sd, 1.0)
    enc_w, dec_w = tr.attention_maps(x)
    assert enc_w.shape == (x.shape[0], 2, T_OBS - 1, T_OBS - 1)
    assert dec_w.shape == (x.shape[0], 2, T_PRED, T_OBS - 1)
    assert np.allclose(enc_w.sum(-1), 1.0) and np.allclose(dec_w.sum(-1), 1.0)
    tr = TransformerPredictor(d_model=16, n_heads=2, rng=np.random.default_rng(13))
    train_predictor(tr, train, val, epochs=12, lr=5e-3, lr_final=1e-3, patience=12,
                    rng=np.random.default_rng(14))
    means_tr, _, _ = predict_lstm(tr, val)
    assert ade(means_tr, val["future"]) < ade(predict_cv(val["obs"], k=T_OBS - 1),
                                              val["future"])

    # 9. ellipses, inflated radius and occupancy cells
    cov = np.array([[0.09, 0.0], [0.0, 0.09]])
    assert abs(inflated_radius(cov, 0.95) - 0.3 * math.sqrt(-2 * math.log(0.05))) < 1e-12
    assert abs(chance_constraint_margin(cov, 0.05, 0.5) - (0.5 + inflated_radius(cov, 0.95))) < 1e-12
    cov2 = np.array([[2.0, 1.2], [1.2, 1.0]])
    pts = covariance_ellipse(np.array([2.0, 1.0]), cov2, p=0.95)
    maha = np.einsum("ni,ij,nj->n", pts - [2.0, 1.0], np.linalg.inv(cov2), pts - [2.0, 1.0])
    assert np.allclose(maha, chi2_radius(0.95) ** 2)
    cells = occupancy_cells(np.array([0.0, 0.0]), cov, p=0.95, cell=0.05)
    area = len(cells) * 0.05 ** 2
    assert abs(area - math.pi * inflated_radius(cov, 0.95) ** 2) < 0.03
    assert len(occupancy_cells(np.zeros(2), cov, 0.95, 0.05, r_base=0.3)) > len(cells)

    print("self-test passed in %.1f s" % (time.time() - t0))


if __name__ == "__main__":
    _self_test()
    if "--seed-study" in sys.argv:
        seed_study()
    if "--no-experiment" not in sys.argv:
        t0 = time.time()
        results = run_experiment()
        print_results(results)
        # the claims of the chapter, checked on the test split
        met = results["metrics"]
        assert met["LSTM-NLL"]["evasive_visible"][0][-1] < met["CV (tuned)"]["evasive_visible"][0][-1]
        assert met["LSTM-NLL"]["turn"][0][-1] < met["CV (tuned)"]["turn"][0][-1]
        assert met["LSTM-NLL"]["all"][0][-1] < met["KF (tuned)"]["all"][0][-1]
        assert met["CV (tuned)"]["straight"][0][-1] < met["LSTM-NLL"]["straight"][0][-1]
        assert met["LSTM-NLL"]["all"][0][-1] < met["LSTM-TF"]["all"][0][-1]
        assert met["Transformer"]["all"][0][-1] < met["CV (tuned)"]["all"][0][-1]
        assert met["Transformer"]["turn"][0][-1] < met["CV (tuned)"]["turn"][0][-1]
        # at this data scale the Transformer matches the LSTM but does not beat it
        assert met["Transformer"]["all"][0][-1] > met["LSTM-MSE"]["all"][0][-1]
        print("experiment finished in %.1f s" % (time.time() - t0))
