"""Chapter 21 -- Model Predictive Control (MPC).

Receding-horizon control of a double-integrator drone with a condensed
quadratic program (QP) that is solved by a small dense ADMM solver written
in NumPy (no SciPy).

* ``double_integrator(dt, n)`` returns the zero-order-hold matrices A, B of
  Chapter 2 for an n-dimensional double integrator (state x = [p, v],
  input u = a).
* ``prediction_matrices(A, B, N)`` builds S_x and S_u with X = S_x x0 + S_u U,
  the "condensed" form in which the dynamics are eliminated.
* ``dare(A, B, Q, R)`` computes the terminal weight P of the infinite-horizon
  LQR problem by iterating the discrete algebraic Riccati equation.
* ``solve_qp(H, f, G, l, u, ...)`` solves  min 1/2 z'Hz + f'z  s.t. l <= Gz <= u
  with the ADMM iteration of OSQP (Stellato et al. 2020): one factorization
  per penalty rho, warm starts, a primal-infeasibility certificate and a
  final polishing step that makes the active constraints hold exactly.
* ``MPC`` assembles the condensed QP at every step: cost from the stacked
  reference, input and velocity boxes, one linearized half-plane per
  predicted obstacle position (hard, or soft with slack variables and an
  optional chance-constraint inflation), and polygonal "stay within a disk
  around a moving center" constraints for formation keeping and
  communication range.  ``MPC.step`` returns the first input.
* ``simulate`` runs a drone that follows a reference path while an intruder
  crosses, optionally with followers that must keep a formation offset and
  a communication distance to the leader.  ``worked_example`` prints every
  number quoted in the chapter, ``tuning_runs`` and ``horizon_experiment``
  produce the data of the generated figures.

ASCII only.  Run the self-test with

    python3 ch21_mpc.py
"""
from __future__ import annotations

import math
import time
from typing import NamedTuple

import numpy as np

INF = float("inf")


# ---------------------------------------------------------------- model
def double_integrator(dt: float, n: int = 2):
    """Zero-order-hold matrices A, B of the n-dimensional double integrator."""
    eye = np.eye(n)
    A = np.block([[eye, dt * eye], [np.zeros((n, n)), eye]])
    B = np.vstack([0.5 * dt * dt * eye, dt * eye])
    return A, B


def prediction_matrices(A, B, N):
    """S_x, S_u such that [x_1; ...; x_N] = S_x x_0 + S_u [u_0; ...; u_{N-1}]."""
    nx, nu = B.shape
    powers = [np.eye(nx)]                       # powers[i] = A^i
    for _ in range(N):
        powers.append(powers[-1] @ A)
    Sx = np.zeros((N * nx, nx))
    Su = np.zeros((N * nx, N * nu))
    for k in range(1, N + 1):
        Sx[(k - 1) * nx:k * nx] = powers[k]
        for j in range(k):                      # x_k depends on u_0 .. u_{k-1}
            Su[(k - 1) * nx:k * nx, j * nu:(j + 1) * nu] = powers[k - 1 - j] @ B
    return Sx, Su


def dare(A, B, Q, R, max_iter=2000, tol=1e-11):
    """Fixed point P of the discrete algebraic Riccati equation (LQR cost-to-go)."""
    P = Q.copy()
    for _ in range(max_iter):
        BtP = B.T @ P
        K = np.linalg.solve(R + BtP @ B, BtP @ A)
        P_next = Q + A.T @ P @ (A - B @ K)
        P_next = 0.5 * (P_next + P_next.T)
        if np.max(np.abs(P_next - P)) < tol:
            return P_next
        P = P_next
    return P


def normal_quantile(p: float) -> float:
    """Inverse of the standard normal CDF by bisection on math.erf."""
    lo, hi = -10.0, 10.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if 0.5 * (1.0 + math.erf(mid / math.sqrt(2.0))) < p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


# ------------------------------------------------------------ QP solver
class QPResult(NamedTuple):
    z: np.ndarray
    y: np.ndarray
    status: str            # "solved", "infeasible" or "max_iter"
    iterations: int
    polished: bool


def _norm_inf(v) -> float:
    return float(np.max(np.abs(v))) if np.size(v) else 0.0


def _primal_infeasible(G, l, u, dy, eps=1e-4) -> bool:
    """OSQP certificate: dy with G'dy = 0 and u'dy+ + l'dy- < 0 proves infeasibility."""
    scale = _norm_inf(dy)
    if scale < 1e-12:
        return False
    d = dy / scale
    if _norm_inf(G.T @ d) > eps:
        return False
    dp, dm = np.maximum(d, 0.0), np.minimum(d, 0.0)
    if np.any(dp[np.isinf(u)] > eps) or np.any(dm[np.isinf(l)] < -eps):
        return False
    fu, fl = np.isfinite(u), np.isfinite(l)
    return float(u[fu] @ dp[fu] + l[fl] @ dm[fl]) < -eps


def _polish(H, f, G, l, u, z, y):
    """Re-solve the KKT system on the active set guessed from the duals y."""
    n = H.shape[0]
    low, upp = y < -1e-7, y > 1e-7
    act = low | upp
    Ga = G[act]
    ba = np.where(low, l, u)[act]
    na = Ga.shape[0]
    K_true = np.block([[H, Ga.T], [Ga, np.zeros((na, na))]])
    K_reg = K_true - np.diag(np.r_[np.zeros(n), 1e-10 * np.ones(na)])
    rhs = np.concatenate([-f, ba])
    try:
        sol = np.linalg.solve(K_reg, rhs)
        sol += np.linalg.solve(K_reg, rhs - K_true @ sol)   # one refinement step
    except np.linalg.LinAlgError:
        return None
    zp, nu = sol[:n], sol[n:]
    Gz = G @ zp
    viol = max(_norm_inf(np.maximum(Gz - u, 0.0)), _norm_inf(np.maximum(l - Gz, 0.0)))
    if viol > 1e-8:
        return None
    signs_ok = not (np.any(nu[low[act]] > 1e-7) or np.any(nu[upp[act]] < -1e-7))
    obj_admm = 0.5 * z @ H @ z + f @ z
    obj_pol = 0.5 * zp @ H @ zp + f @ zp
    if not signs_ok and obj_pol > obj_admm + 1e-6 * (1.0 + abs(obj_admm)):
        return None
    yp = np.zeros_like(y)
    yp[act] = nu
    return zp, yp


def solve_qp(H, f, G, l, u, z0=None, y0=None, rho=0.1, sigma=1e-6, alpha=1.6,
             eps_abs=1e-4, eps_rel=1e-4, max_iter=5000, polish=True,
             restart_at=2500, eps_inaccurate=1e-3) -> QPResult:
    """Solve  min 1/2 z'Hz + f'z  s.t.  l <= Gz <= u  by ADMM (OSQP iteration).

    H must be positive definite (add a small multiple of I otherwise).  Use
    l = -inf or u = +inf for one-sided rows.  z0, y0 warm-start the primal
    and dual iterates.  The linear system (H + sigma I + rho G'G) zt = rhs
    is solved with a matrix inverse computed once per rho: the problems of
    this chapter have at most a few hundred variables, so that is cheapest.
    A stale dual warm start can stall the iteration; after `restart_at`
    iterations without convergence the duals are reset once.  If the
    iteration cap is reached with residuals below `eps_inaccurate` the
    status is "solved_inaccurate" (as in OSQP); "max_iter" otherwise.
    """
    n, m = H.shape[0], G.shape[0]
    # Equilibrate: scale every row of G (and its bounds) to unit infinity norm,
    # so that one penalty rho suits rows of very different magnitude.
    scale = np.maximum(np.max(np.abs(G), axis=1), 1e-12)
    G_orig, l_orig, u_orig = G, l, u
    G, l, u = G / scale[:, None], l / scale, u / scale
    z = np.zeros(n) if z0 is None else np.array(z0, dtype=float)
    y = np.zeros(m) if y0 is None else np.array(y0, dtype=float) * scale
    w = np.clip(G @ z, l, u)
    GtG = G.T @ G
    eye = np.eye(n)
    Kinv = np.linalg.inv(H + sigma * eye + rho * GtG)
    f_norm = _norm_inf(f)
    rho0 = rho
    status, it = "max_iter", 0
    r_prim = r_dual = s_prim = s_dual = INF
    y_check = y.copy()
    for it in range(1, max_iter + 1):
        zt = Kinv @ (sigma * z - f + G.T @ (rho * w - y))
        w_hat = alpha * (G @ zt) + (1.0 - alpha) * w
        z = alpha * zt + (1.0 - alpha) * z
        w_new = np.clip(w_hat + y / rho, l, u)
        y = y + rho * (w_hat - w_new)
        w = w_new
        if it % 10 == 0:
            Gz, Hz, Gty = G @ z, H @ z, G.T @ y
            r_prim = _norm_inf(Gz - w)
            r_dual = _norm_inf(Hz + f + Gty)
            s_prim = max(_norm_inf(Gz), _norm_inf(w), 1e-12)
            s_dual = max(_norm_inf(Hz), _norm_inf(Gty), f_norm, 1e-12)
            ok_prim = r_prim <= eps_abs + eps_rel * s_prim
            ok_dual = r_dual <= eps_abs + eps_rel * s_dual
            if ok_prim and ok_dual:
                status = "solved"
                break
            if _primal_infeasible(G, l, u, y - y_check):
                status = "infeasible"
                break
            y_check = y.copy()
            if it % 30 == 0:                      # adapt rho to balance the residuals
                ratio = math.sqrt((r_prim / s_prim) / max(r_dual / s_dual, 1e-12))
                if ratio > 5.0 or ratio < 0.2:
                    rho = float(np.clip(rho * np.clip(ratio, 0.01, 100.0), 1e-3, 1e3))
                    Kinv = np.linalg.inv(H + sigma * eye + rho * GtG)
            if it == restart_at:                  # cold restart of the duals
                y, rho = np.zeros(m), rho0
                w = np.clip(G @ z, l, u)
                Kinv = np.linalg.inv(H + sigma * eye + rho * GtG)
    if status == "max_iter" and r_prim <= eps_inaccurate * (1.0 + s_prim) \
            and r_dual <= eps_inaccurate * (1.0 + s_dual):
        status = "solved_inaccurate"
    y = y / scale                                  # duals of the original rows
    polished = False
    if polish and status.startswith("solved"):
        res = _polish(H, f, G_orig, l_orig, u_orig, z, y)
        if res is not None:
            z, y, polished = res[0], res[1], True
    return QPResult(z, y, status, it, polished)


# ------------------------------------------------------------------ MPC
class Obstacle(NamedTuple):
    """Predicted obstacle: centers (N, n), radius (scalar), covs (N, n, n) or None."""
    centers: np.ndarray
    radius: float
    covs: object = None


class KeepIn(NamedTuple):
    """Stay within `radius` of the moving center (N, n): formation or communication."""
    centers: np.ndarray
    radius: float


class MPC:
    """Condensed-QP model predictive controller for an n-dimensional double integrator."""

    def __init__(self, N=15, dt=0.1, n=2, q_pos=1.0, q_vel=0.1, r_in=0.1,
                 a_max=2.0, v_max=2.0, soft=False, w_lin=50.0, w_quad=50.0,
                 terminal="dare", n_poly=8, delta=None):
        self.N, self.dt, self.n = N, dt, n
        self.A, self.B = double_integrator(dt, n)
        self.nx, self.nu = self.B.shape
        self.Q = np.diag([q_pos] * n + [q_vel] * n)
        self.R = r_in * np.eye(n)
        self.P = dare(self.A, self.B, self.Q, self.R) if terminal == "dare" else self.Q.copy()
        self.Sx, self.Su = prediction_matrices(self.A, self.B, N)
        Qbar = np.kron(np.eye(N), self.Q)
        Qbar[-self.nx:, -self.nx:] = self.P
        Rbar = np.kron(np.eye(N), self.R)
        H = 2.0 * (self.Su.T @ Qbar @ self.Su + Rbar)
        self.H_uu = 0.5 * (H + H.T)
        self.F = 2.0 * self.Su.T @ Qbar            # f = F (S_x x0 - X_ref)
        self.a_max, self.v_max = a_max, v_max
        self.soft, self.w_lin, self.w_quad = soft, w_lin, w_quad
        self.kappa = normal_quantile(1.0 - delta) if delta is not None else 0.0
        ang = 2.0 * math.pi * np.arange(n_poly) / n_poly
        self.poly = np.column_stack([np.cos(ang), np.sin(ang)])   # 2-D directions
        self.apothem = math.cos(math.pi / n_poly)
        idx = np.arange(N * self.nx).reshape(N, self.nx)
        self.pos_idx, self.vel_idx = idx[:, :n], idx[:, n:]
        self.reset()

    def reset(self):
        self.U_prev = np.zeros(self.N * self.nu)
        self.y_prev = None
        self.m_prev = -1

    @staticmethod
    def _shift_dual(y, layout):
        """Shift the duals one step forward inside every block (rows_per_step, N)."""
        out, pos = [], 0
        for rows_per_step, N in layout:
            blk = y[pos:pos + rows_per_step * N].reshape(N, rows_per_step)
            out.append(np.vstack([blk[1:], blk[-1:]]).reshape(-1))
            pos += rows_per_step * N
        return np.concatenate(out)

    def _fallback(self, x0):
        """Brake toward zero velocity when the QP cannot be solved."""
        return np.clip(-x0[self.n:] / self.dt, -self.a_max, self.a_max)

    def step(self, x0, Xref, obstacles=(), keep_in=()):
        """One MPC step from state x0 (2n,) with reference Xref (N, 2n) for k = 1..N."""
        N, n, nu = self.N, self.n, self.nu
        x0 = np.asarray(x0, dtype=float)
        xref = np.asarray(Xref, dtype=float).reshape(-1)
        free = self.Sx @ x0                                  # response with U = 0
        U_guess = np.concatenate([self.U_prev[nu:], self.U_prev[-nu:]])   # shift
        X_guess = free + self.Su @ U_guess
        rows, lo, up = [], [], []
        # (1) input box  -a_max <= u <= a_max
        rows.append(np.eye(N * nu))
        lo.append(-self.a_max * np.ones(N * nu))
        up.append(self.a_max * np.ones(N * nu))
        # (2) velocity box on every predicted step
        vidx = self.vel_idx.reshape(-1)
        rows.append(self.Su[vidx])
        lo.append(-self.v_max - free[vidx])
        up.append(self.v_max - free[vidx])
        # (3) one linearized half-plane per obstacle and step
        avoid_rows, avoid_lo, avoid_up = [], [], []
        avoid_k, normals = [], []
        for obs in obstacles:
            for k in range(N):
                pk = self.pos_idx[k]
                d = X_guess[pk] - obs.centers[k]
                dist = float(np.linalg.norm(d))
                if dist < 1e-9:      # on the center: use the reference
                    d = xref[pk] - obs.centers[k]
                    dist = float(np.linalg.norm(d))
                if dist < 1e-9:
                    d = np.eye(n)[-1]
                    dist = 1.0
                nk = d / dist
                radius = obs.radius
                if obs.covs is not None and self.kappa > 0.0:  # chance
                    sig = math.sqrt(float(nk @ obs.covs[k] @ nk))
                    radius += self.kappa * sig
                # nk'(p_k - o_k) >= radius, written as a row in U
                bound = float(nk @ (free[pk] - obs.centers[k])) - radius
                avoid_rows.append(-nk @ self.Su[pk])
                avoid_lo.append(-INF)
                avoid_up.append(bound)
                avoid_k.append(k)
                normals.append(nk)
        # (4) polygonal keep-in constraints  n_m'(p_k - c_k) <= radius cos(pi/M)
        for ki in keep_in:
            for k in range(N):
                pk = self.pos_idx[k]
                for nm in self.poly:
                    rows.append((nm @ self.Su[pk])[None, :])
                    lo.append(np.array([-INF]))
                    up.append(np.array([ki.radius * self.apothem - float(nm @ (free[pk] - ki.centers[k]))]))
        n_avoid = len(avoid_rows)
        n_slack = n_avoid if self.soft else 0
        nz = N * nu + n_slack
        G_list = [np.hstack([r, np.zeros((r.shape[0], n_slack))]) for r in rows]
        if n_avoid:
            Ga = np.zeros((n_avoid, nz))
            Ga[:, :N * nu] = np.array(avoid_rows)
            if self.soft:
                Ga[:, N * nu:] = -np.eye(n_avoid)          # ... - s_k <= bound
            G_list.append(Ga)
            lo.append(np.array(avoid_lo))
            up.append(np.array(avoid_up))
        if n_slack:
            Gs = np.zeros((n_slack, nz))
            Gs[:, N * nu:] = np.eye(n_slack)               # s >= 0
            G_list.append(Gs)
            lo.append(np.zeros(n_slack))
            up.append(np.full(n_slack, INF))
        G = np.vstack(G_list)
        l_vec, u_vec = np.concatenate(lo), np.concatenate(up)
        H = np.zeros((nz, nz))
        H[:N * nu, :N * nu] = self.H_uu
        f = np.zeros(nz)
        f[:N * nu] = self.F @ (free - xref)
        if n_slack:
            H[N * nu:, N * nu:] = 2.0 * self.w_quad * np.eye(n_slack)
            f[N * nu:] = self.w_lin
        layout = ([(nu, N), (n, N)] + [(len(self.poly), N)] * len(keep_in)
                  + [(1, N)] * len(obstacles) + [(1, N)] * (len(obstacles) if n_slack else 0))
        z0 = np.concatenate([U_guess, np.zeros(n_slack)])
        y0 = None
        if self.y_prev is not None and self.m_prev == G.shape[0]:
            y0 = self._shift_dual(self.y_prev, layout)      # warm-start the duals too
        t0 = time.perf_counter()
        res = solve_qp(H, f, G, l_vec, u_vec, z0, y0)
        solve_time = time.perf_counter() - t0
        info = dict(status=res.status, iterations=res.iterations, polished=res.polished,
                    solve_time=solve_time, n_rows=G.shape[0], n_vars=nz,
                    guess=X_guess.reshape(N, self.nx))
        if not res.status.startswith("solved"):
            self.U_prev, self.y_prev = U_guess, None
            info.update(plan=X_guess.reshape(N, self.nx), slack=np.zeros(n_avoid),
                        active=[], multipliers=np.zeros(n_avoid))
            return self._fallback(x0), info
        U = res.z[:N * nu]
        self.U_prev, self.y_prev, self.m_prev = U.copy(), res.y.copy(), G.shape[0]
        first = sum(r.shape[0] for r in rows)
        mult = res.y[first:first + n_avoid]
        info.update(plan=(free + self.Su @ U).reshape(N, self.nx), U=U.reshape(N, nu),
                    slack=res.z[N * nu:], multipliers=mult, normals=normals,
                    active=[avoid_k[i] + 1 for i in range(n_avoid) if mult[i] > 1e-6])
        return np.clip(U[:nu], -self.a_max, self.a_max), info


# ------------------------------------------------------------ scenarios
class Intruder(NamedTuple):
    p0: np.ndarray
    v: np.ndarray
    detect_range: float = INF        # the drone only knows it when this close

    def position(self, t):
        return self.p0 + t * self.v

    def predict(self, t, N, dt):
        """Constant-velocity prediction for k = 1..N (positions (N, n))."""
        return np.array([self.position(t + k * dt) for k in range(1, N + 1)])


def straight_reference(v_ref=1.0, offset=(0.0, 0.0)):
    """Reference state at time t: moving along +x at speed v_ref, offset added."""
    off = np.asarray(offset, dtype=float)

    def ref(t):
        return np.array([v_ref * t + off[0], off[1], v_ref, 0.0])
    return ref


def constant_reference(p):
    p = np.asarray(p, dtype=float)

    def ref(t):
        return np.concatenate([p, np.zeros_like(p)])
    return ref


def stack_reference(ref, t, N, dt):
    return np.array([ref(t + k * dt) for k in range(1, N + 1)])


class Follower(NamedTuple):
    mpc: MPC
    x0: np.ndarray
    offset: np.ndarray         # desired p_follower - p_leader
    e_max: float               # formation tolerance
    r_comm: float              # communication range


def simulate(mpc: MPC, x0, ref, intruder=None, T=8.0, r_safe=1.0, followers=(),
             cov_growth=None, wind=None):
    """Run the closed loop; return a dict of per-step records.

    cov_growth = (Sigma0, Sigma_v): the predicted intruder position at step k
    gets covariance Sigma0 + (k dt)^2 Sigma_v (used with mpc.kappa > 0).
    wind: a constant acceleration (n,) added to the plant but not to the model,
    i.e. an unmodeled disturbance the receding horizon has to reject
    (exercise 21.1).
    """
    mpc.reset()
    for fo in followers:
        fo.mpc.reset()
    N, dt, n = mpc.N, mpc.dt, mpc.n
    x = np.asarray(x0, dtype=float).copy()
    xf = [np.asarray(fo.x0, dtype=float).copy() for fo in followers]
    steps = int(round(T / dt))
    rec = {k: [] for k in ("t", "x", "u", "sep", "err", "status", "iters", "time",
                           "slack", "active", "mult", "form_err", "dist")}
    rec["pred"] = []
    rec["guess"] = []
    rec["polished"] = []
    w_wind = np.zeros(mpc.nu) if wind is None else np.asarray(wind, dtype=float)
    for i in range(steps):
        t = i * dt
        Xref = stack_reference(ref, t, N, dt)
        obstacles = []
        sep = INF
        if intruder is not None:
            o_now = intruder.position(t)
            sep = float(np.linalg.norm(x[:n] - o_now))
            if sep <= intruder.detect_range:
                covs = None
                if cov_growth is not None:
                    S0, Sv = cov_growth
                    covs = np.array([S0 + (k * dt) ** 2 * Sv for k in range(1, N + 1)])
                obstacles.append(Obstacle(intruder.predict(t, N, dt), r_safe, covs))
        u, info = mpc.step(x, Xref, obstacles)
        rec["t"].append(t)
        rec["x"].append(x.copy())
        rec["u"].append(u.copy())
        rec["sep"].append(sep)
        rec["err"].append(float(np.linalg.norm(x[:n] - ref(t)[:n])))
        rec["status"].append(info["status"])
        rec["iters"].append(info["iterations"])
        rec["time"].append(info["solve_time"])
        rec["slack"].append(float(np.max(info["slack"])) if len(info["slack"]) else 0.0)
        rec["active"].append(info["active"])
        rec["mult"].append(float(np.max(info["multipliers"])) if len(info["multipliers"]) else 0.0)
        rec["pred"].append(info["plan"].copy())
        rec["guess"].append(info["guess"].copy())
        rec["polished"].append(bool(info["polished"]))
        plan_pos = info["plan"][:, :n]
        ferr, fdist = [], []
        for j, fo in enumerate(followers):
            Xref_f = stack_reference(ref, t, N, dt)
            Xref_f[:, :n] += fo.offset
            keep = [KeepIn(plan_pos + fo.offset, fo.e_max), KeepIn(plan_pos, fo.r_comm)]
            uf, _ = fo.mpc.step(xf[j], Xref_f, obstacles, keep)
            ferr.append(float(np.linalg.norm(xf[j][:n] - x[:n] - fo.offset)))
            fdist.append(float(np.linalg.norm(xf[j][:n] - x[:n])))
            xf[j] = mpc.A @ xf[j] + mpc.B @ uf
        rec["form_err"].append(ferr)
        rec["dist"].append(fdist)
        x = mpc.A @ x + mpc.B @ (u + w_wind)
    for k in ("t", "x", "u", "sep", "err", "iters", "time", "slack", "mult", "form_err", "dist"):
        rec[k] = np.array(rec[k])
    return rec


def default_scenario():
    """The chapter's instance: reference along +x at 1 m/s, intruder crossing from below."""
    x0 = np.array([0.0, 0.0, 1.0, 0.0])
    ref = straight_reference(1.0)
    intr = Intruder(np.array([4.5, -3.0]), np.array([0.0, 0.8]))
    return x0, ref, intr


def summarize(rec, r_safe=1.0):
    ok = np.array([s.startswith("solved") for s in rec["status"]])
    inacc = int(sum(s == "solved_inaccurate" for s in rec["status"]))
    return dict(min_sep=float(np.min(rec["sep"])), t_min=float(rec["t"][int(np.argmin(rec["sep"]))]),
                inaccurate=inacc,
                rms_err=float(np.sqrt(np.mean(rec["err"] ** 2))), max_err=float(np.max(rec["err"])),
                failures=int(np.sum(~ok)), mean_iters=float(np.mean(rec["iters"])),
                max_iters=int(np.max(rec["iters"])), mean_ms=1e3 * float(np.mean(rec["time"])),
                max_ms=1e3 * float(np.max(rec["time"])), max_slack=float(np.max(rec["slack"])),
                polished=float(np.mean(rec["polished"])),
                violation=float(max(0.0, r_safe - np.min(rec["sep"]))))


def worked_example(verbose=True, N=15):
    """The worked example of the chapter (hard constraints, N = 15, dt = 0.1)."""
    x0, ref, intr = default_scenario()
    mpc = MPC(N=N, dt=0.1)
    rec = simulate(mpc, x0, ref, intr, T=8.0)
    s = summarize(rec)
    if verbose:
        print("Worked example: N=%d dt=%.2f a_max=%.1f v_max=%.1f r_safe=1.0" % (N, mpc.dt, mpc.a_max, mpc.v_max))
        print("terminal weight P (DARE) =")
        print(np.array2string(mpc.P, precision=3, suppress_small=True))
        print("  t     x      y     vx     vy     ax     ay    sep   err   active  mult   iters")
        for i in range(0, len(rec["t"])):
            t = rec["t"][i]
            if abs(t * 2 - round(t * 2)) > 1e-9:
                continue
            x, u = rec["x"][i], rec["u"][i]
            print("%4.1f %6.3f %6.3f %6.3f %6.3f %6.3f %6.3f %6.3f %5.3f %-7s %6.2f %5d" % (
                t, x[0], x[1], x[2], x[3], u[0], u[1], rec["sep"][i], rec["err"][i],
                str(rec["active"][i][:3]), rec["mult"][i], rec["iters"][i]))
        print("summary:", {k: round(v, 4) if isinstance(v, float) else v for k, v in s.items()})
        # first step at which the avoidance constraint is active
        first = next((i for i, a in enumerate(rec["active"]) if a), None)
        if first is not None:
            kact = rec["active"][first][0]
            t_act = rec["t"][first] + kact * mpc.dt
            print("constraint first active at t=%.1f (steps %s), guess point sep=%.3f,"
                  " plan point sep=%.3f" % (
                      rec["t"][first], rec["active"][first],
                      float(np.linalg.norm(rec["guess"][first][kact - 1, :2]
                                           - intr.position(t_act))),
                      float(np.linalg.norm(rec["pred"][first][kact - 1, :2]
                                           - intr.position(t_act)))))
            print("largest multiplier over the run: %.2f" % float(np.max(rec["mult"])))
        print("min speed vx = %.3f at t=%.1f ; max speed vx = %.3f at t=%.1f" % (
            rec["x"][:, 2].min(), rec["t"][rec["x"][:, 2].argmin()],
            rec["x"][:, 2].max(), rec["t"][rec["x"][:, 2].argmax()]))
        print("max |y| = %.3f ; max lag behind reference = %.3f m at t=%.1f" % (
            np.abs(rec["x"][:, 1]).max(), rec["err"].max(), rec["t"][rec["err"].argmax()]))
        # cold start comparison
        mpc_cold = MPC(N=N, dt=0.1)
        it_cold = []
        for i in range(len(rec["t"])):
            mpc_cold.reset()
            t = rec["t"][i]
            obs = [Obstacle(intr.predict(t, N, 0.1), 1.0)]
            _, info = mpc_cold.step(rec["x"][i], stack_reference(ref, t, N, 0.1), obs)
            it_cold.append(info["iterations"])
        print("ADMM iterations warm: mean %.1f max %d ; cold: mean %.1f max %d" % (
            s["mean_iters"], s["max_iters"], np.mean(it_cold), np.max(it_cold)))
        print("solve time per step: mean %.2f ms, max %.2f ms (%d vars, %d rows)" % (
            s["mean_ms"], s["max_ms"], 2 * N, 4 * N + N))
    return rec, s


def tuning_runs():
    """Trajectories for N in (5, 10, 20) with hard constraints and for three slack weights."""
    x0, ref, intr = default_scenario()
    out = {}
    for N in (5, 10, 20):
        out["N%d" % N] = simulate(MPC(N=N, dt=0.1), x0, ref, intr, T=8.0)
    for w in (1.0, 10.0, 100.0):
        out["w%g" % w] = simulate(MPC(N=15, dt=0.1, soft=True, w_lin=w, w_quad=w), x0, ref, intr, T=8.0)
    return out


def horizon_experiment(Ns=(3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30), detect_range=INF):
    """RMS tracking error, minimum separation and failures vs N, hard vs soft."""
    x0, ref, intr = default_scenario()
    intr = Intruder(intr.p0, intr.v, detect_range)
    rows = []
    for N in Ns:
        rh = summarize(simulate(MPC(N=N, dt=0.1), x0, ref, intr, T=8.0))
        rs = summarize(simulate(MPC(N=N, dt=0.1, soft=True), x0, ref, intr, T=8.0))
        rows.append((N, rh["rms_err"], rh["min_sep"], rh["failures"],
                     rs["rms_err"], rs["min_sep"], rs["failures"], rs["max_slack"]))
    return np.array(rows)


# ------------------------------------------------------------ self-test
def _self_test():
    t_start = time.perf_counter()
    rng = np.random.default_rng(21)
    # 1. prediction matrices reproduce a rollout
    A, B = double_integrator(0.1, 2)
    Sx, Su = prediction_matrices(A, B, 6)
    x, U = rng.normal(size=4), rng.normal(size=12)
    X = Sx @ x + Su @ U
    xk = x.copy()
    for k in range(6):
        xk = A @ xk + B @ U[2 * k:2 * k + 2]
        assert np.allclose(X[4 * k:4 * k + 4], xk)
    # 2. QP solver: bound active, exact after polish; and an infeasible problem
    res = solve_qp(np.array([[2.0]]), np.array([-6.0]), np.array([[1.0]]),
                   np.array([-INF]), np.array([1.0]))
    assert res.status == "solved" and abs(res.z[0] - 1.0) < 1e-9 and res.polished
    res = solve_qp(np.eye(2), np.zeros(2), np.array([[1.0, 1.0], [1.0, -1.0]]),
                   np.array([1.0, -INF]), np.array([INF, -0.5]))
    assert res.status == "solved" and abs(res.z[0] + res.z[1] - 1.0) < 1e-8
    res = solve_qp(np.array([[1.0]]), np.zeros(1), np.array([[1.0], [1.0]]),
                   np.array([1.0, -INF]), np.array([INF, 0.0]))
    assert res.status == "infeasible", res.status
    # 3. the half-plane excludes the whole disk
    o, r = np.array([1.0, 2.0]), 0.7
    for _ in range(200):
        nk = rng.normal(size=2)
        nk /= np.linalg.norm(nk)
        p = o + r * nk + rng.uniform(0, 3) * nk + rng.normal(size=2) * 0.5
        if nk @ (p - o) >= r:
            assert np.linalg.norm(p - o) >= r - 1e-12
    # 4. no obstacle: track a constant reference; bounds never violated
    mpc = MPC(N=15, dt=0.1)
    rec = simulate(mpc, np.array([2.0, -1.5, 0.0, 0.0]), constant_reference([0.0, 0.0]), None, T=5.0)
    assert all(s.startswith("solved") for s in rec["status"])
    assert rec["err"][-1] < 1e-2, rec["err"][-1]
    assert np.all(np.abs(rec["u"]) <= mpc.a_max + 1e-9)
    assert np.all(np.abs(rec["x"][:, 2:]) <= mpc.v_max + 1e-6)
    # 5. intruder with hard constraints: separation never below r_safe
    x0, ref, intr = default_scenario()
    rec_h = simulate(MPC(N=15, dt=0.1), x0, ref, intr, T=8.0)
    s_h = summarize(rec_h)
    assert s_h["failures"] == 0 and s_h["min_sep"] >= 1.0 - 1e-4, s_h
    assert np.all(np.abs(rec_h["u"]) <= 2.0 + 1e-9) and np.all(np.abs(rec_h["x"][:, 2:]) <= 2.0 + 1e-6)
    assert rec_h["err"][-1] < 0.05                      # back on the reference at the end
    # 6. soft constraints with an exact penalty reproduce the hard solution ...
    rec_s = simulate(MPC(N=15, dt=0.1, soft=True), x0, ref, intr, T=8.0)
    s_s = summarize(rec_s)
    assert s_s["failures"] == 0 and s_s["min_sep"] >= 1.0 - 1e-4, s_s
    assert np.max(np.abs(rec_s["x"] - rec_h["x"])) < 1e-3
    # ... and degrade gracefully when the hard problem is infeasible (late detection)
    late = Intruder(intr.p0, intr.v, detect_range=1.2)
    s_hard_late = summarize(simulate(MPC(N=15, dt=0.1), x0, ref, late, T=8.0))
    s_soft_late = summarize(simulate(MPC(N=15, dt=0.1, soft=True), x0, ref, late, T=8.0))
    assert s_hard_late["failures"] > 0, s_hard_late
    assert s_soft_late["failures"] == 0 and s_soft_late["min_sep"] > s_hard_late["min_sep"], (s_hard_late, s_soft_late)
    seps = [summarize(simulate(MPC(N=15, dt=0.1, soft=True, w_lin=w, w_quad=w), x0, ref, intr, T=8.0))["min_sep"]
            for w in (1.0, 10.0, 100.0)]
    assert seps[0] <= seps[1] + 1e-6 <= seps[2] + 2e-6 and seps[0] > 0.5, seps
    # 7. leader-follower: formation and communication constraints hold at every step
    fo = Follower(MPC(N=15, dt=0.1), np.array([-1.5, 0.0, 1.0, 0.0]), np.array([-1.5, 0.0]), 0.3, 2.0)
    rec_f = simulate(MPC(N=15, dt=0.1), x0, ref, intr, T=8.0, followers=[fo])
    assert np.all(rec_f["form_err"] <= 0.3 + 1e-6), rec_f["form_err"].max()
    assert np.all(rec_f["dist"] <= 2.0 + 1e-6)
    # 8. chance constraint: inflated radius increases the minimum separation
    S0, Sv = 0.05 ** 2 * np.eye(2), 0.2 ** 2 * np.eye(2)
    rec_c = simulate(MPC(N=15, dt=0.1, delta=0.05), x0, ref, intr, T=8.0, cov_growth=(S0, Sv))
    assert summarize(rec_c)["min_sep"] > s_h["min_sep"] + 0.05
    assert abs(normal_quantile(0.95) - 1.6449) < 1e-3
    elapsed = time.perf_counter() - t_start
    assert elapsed < 10.0
    print("self-test passed in %.1f s (hard: min sep %.3f, soft w=1: %.3f, late hard fails %d, "
          "late soft min sep %.3f, chance min sep %.3f)" % (
              elapsed, s_h["min_sep"], seps[0], s_hard_late["failures"], s_soft_late["min_sep"],
              summarize(rec_c)["min_sep"]))


if __name__ == "__main__":
    worked_example(verbose=True)
    _self_test()
