"""Consensus and formation control for a drone swarm (Chapter 23).

Communication graph from positions and a radius, Laplacian and algebraic
connectivity lambda_2 (eigen-solver and a power-iteration monitor),
continuous- and discrete-time consensus, leader-follower pinning,
displacement-based formation control (first and second order), the
formation-error metric of Chapter 25, range-keeping and avoidance terms,
and a small flocking controller in the style of Olfati-Saber.

Conventions.  Positions are the rows of an (n, dim) array.  The desired
formation is given by offsets o_i, so that d_ij = o_j - o_i is the desired
position of drone j as seen from drone i, and y_i = p_i - o_i are the
shifted variables on which the formation controller runs consensus.

Run `python3 ch23_consensus.py` for the self-test (a few seconds).
"""
import time

import numpy as np


# ------------------------------------------------------------------
# Communication graph, Laplacian, algebraic connectivity
# ------------------------------------------------------------------
def radius_graph(positions, r_comm):
    """Return the 0/1 adjacency matrix of the communication graph.

    Drones i != j are neighbours if and only if ||p_i - p_j|| <= r_comm.
    """
    P = np.asarray(positions, dtype=float)
    dist = np.linalg.norm(P[:, None, :] - P[None, :, :], axis=2)
    A = (dist <= r_comm).astype(float)
    np.fill_diagonal(A, 0.0)
    return A


def laplacian(A):
    """Graph Laplacian L = D - A; every row of L sums to zero."""
    A = np.asarray(A, dtype=float)
    return np.diag(A.sum(axis=1)) - A


def edges_of(A):
    """Undirected edges (i, j) with i < j and a_ij > 0."""
    A = np.asarray(A)
    n = A.shape[0]
    return [(i, j) for i in range(n) for j in range(i + 1, n) if A[i, j] > 0]


def algebraic_connectivity(L):
    """lambda_2(L): the second-smallest eigenvalue, zero iff disconnected."""
    return float(np.linalg.eigvalsh(np.asarray(L, dtype=float))[1])


def is_connected(A):
    """True if the graph with adjacency matrix A is connected."""
    return algebraic_connectivity(laplacian(A)) > 1e-9


def fiedler_power_iteration(L, iters=3000, seed=0):
    """Estimate lambda_2 by power iteration instead of an eigen-solver.

    With s = 2 d_max the matrix B = s I - L - (s / n) 1 1^T has the
    eigenvalue 0 for the all-ones vector and s - lambda_k for k >= 2.
    All of them are non-negative, so power iteration on B converges to
    s - lambda_2.  Only products B v and the average of v are needed,
    which is what makes a distributed version possible.
    """
    L = np.asarray(L, dtype=float)
    n = L.shape[0]
    s = 2.0 * float(np.max(np.diag(L)))
    if s <= 0.0:
        return 0.0
    B = s * np.eye(n) - L - (s / n) * np.ones((n, n))
    v = np.random.default_rng(seed).standard_normal(n)
    v -= v.mean()
    v /= np.linalg.norm(v)
    for _ in range(iters):
        w = B @ v
        norm = np.linalg.norm(w)
        if norm < 1e-12:
            return s
        v = w / norm
    return s - float(v @ B @ v)


# ------------------------------------------------------------------
# Consensus dynamics
# ------------------------------------------------------------------
def disagreement(x):
    """Euclidean distance of the state from the consensus subspace."""
    x = np.asarray(x, dtype=float)
    return float(np.linalg.norm(x - x.mean(axis=0)))


def consensus_continuous(L, x0, t_end, dt=0.01):
    """Integrate xdot = -L x with RK4; return (times, states)."""
    L = np.asarray(L, dtype=float)
    x = np.array(x0, dtype=float)
    steps = int(round(t_end / dt))
    X = np.empty((steps + 1,) + x.shape)
    X[0] = x
    for k in range(steps):
        k1 = -L @ x
        k2 = -L @ (x + 0.5 * dt * k1)
        k3 = -L @ (x + 0.5 * dt * k2)
        k4 = -L @ (x + dt * k3)
        x = x + dt / 6.0 * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
        X[k + 1] = x
    return dt * np.arange(steps + 1), X


def consensus_exact(L, x0, t):
    """x(t) = sum_k exp(-lambda_k t) (v_k^T x0) v_k for a symmetric L."""
    lam, V = np.linalg.eigh(np.asarray(L, dtype=float))
    x0 = np.asarray(x0, dtype=float)
    coef = V.T @ x0
    decay = np.exp(-lam * t).reshape((-1,) + (1,) * (x0.ndim - 1))
    return V @ (decay * coef)


def safe_step_size(A):
    """The sufficient bound 1/d_max on eps for x <- (I - eps L) x."""
    return 1.0 / float(np.max(np.asarray(A, dtype=float).sum(axis=1)))


def spectral_step_bound(L):
    """The exact bound 2/lambda_n on eps for the discrete-time protocol."""
    return 2.0 / float(np.linalg.eigvalsh(np.asarray(L, dtype=float))[-1])


def consensus_discrete(L, x0, eps, steps):
    """Iterate x <- (I - eps L) x; return all states (steps + 1 rows)."""
    L = np.asarray(L, dtype=float)
    P = np.eye(L.shape[0]) - eps * L
    x = np.array(x0, dtype=float)
    X = np.empty((steps + 1,) + x.shape)
    X[0] = x
    for k in range(steps):
        x = P @ x
        X[k + 1] = x
    return X


def pinned_matrix(A, pinned, gain=1.0, gain_ref=1.0):
    """M = gain L + gain_ref B of the leader-follower error dynamics."""
    A = np.asarray(A, dtype=float)
    B = np.zeros(A.shape)
    for i in pinned:
        B[i, i] = 1.0
    return gain * laplacian(A) + gain_ref * B


# ------------------------------------------------------------------
# Displacement-based formation control
# ------------------------------------------------------------------
def displacement_targets(offsets):
    """d_ij = o_j - o_i, the desired position of j relative to i."""
    O = np.asarray(offsets, dtype=float)
    return O[None, :, :] - O[:, None, :]


def formation_error(P, offsets, A_form):
    """RMS of ||(p_j - p_i) - d_ij|| over the edges of the formation graph."""
    Y = np.asarray(P, dtype=float) - np.asarray(offsets, dtype=float)
    edges = edges_of(A_form)
    if not edges:
        return float("nan")
    sq = [float(np.sum((Y[j] - Y[i]) ** 2)) for i, j in edges]
    return float(np.sqrt(np.mean(sq)))


def formation_error_centred(P, offsets):
    """RMS deviation from the template after removing the best translation."""
    Y = np.asarray(P, dtype=float) - np.asarray(offsets, dtype=float)
    Y = Y - Y.mean(axis=0)
    return float(np.sqrt(np.mean(np.sum(Y ** 2, axis=1))))


def edge_lengths(P, A):
    """Lengths ||p_i - p_j|| of the edges of A, in edges_of order."""
    P = np.asarray(P, dtype=float)
    return np.array([np.linalg.norm(P[i] - P[j]) for i, j in edges_of(A)])


def formation_velocity(P, offsets, A, gain=1.0, ref=None, ref_vel=None,
                       pinned=(), gain_ref=1.0):
    """First-order displacement-based formation controller (velocities).

    v_i = gain * sum_j a_ij (p_j - p_i - d_ij)
          + b_i gain_ref (r + o_i - p_i)     pinning of the leader(s)
          + rdot                              feed-forward if known
    Because p_j - p_i - d_ij = y_j - y_i with y = p - o, the sum is -L y.
    """
    P = np.asarray(P, dtype=float)
    O = np.asarray(offsets, dtype=float)
    V = -gain * (laplacian(A) @ (P - O))
    if ref is not None:
        r = np.asarray(ref, dtype=float)
        for i in pinned:
            V[i] += gain_ref * (r + O[i] - P[i])
    if ref_vel is not None:
        V += np.asarray(ref_vel, dtype=float)
    return V


def formation_acceleration(P, Vel, offsets, A, kp=1.0, kv=1.0, kd=0.0,
                           ref=None, ref_vel=None, pinned=()):
    """Second-order (double-integrator) formation controller.

    u_i = sum_j a_ij [kp (p_j - p_i - d_ij) + kv (v_j - v_i)]
          - kd (v_i - rdot)
          + b_i [kp (r + o_i - p_i) + kv (rdot - v_i)]
    With ref_vel = None the damping term is -kd v_i (swarm comes to rest).
    """
    P = np.asarray(P, dtype=float)
    Vel = np.asarray(Vel, dtype=float)
    O = np.asarray(offsets, dtype=float)
    L = laplacian(A)
    U = -kp * (L @ (P - O)) - kv * (L @ Vel)
    if ref_vel is None:
        vref = np.zeros(P.shape[1])
    else:
        vref = np.asarray(ref_vel, dtype=float)
    U -= kd * (Vel - vref)
    if ref is not None:
        r = np.asarray(ref, dtype=float)
        for i in pinned:
            U[i] += kp * (r + O[i] - P[i]) + kv * (vref - Vel[i])
    return U


# ------------------------------------------------------------------
# Range keeping (connectivity) and avoidance terms
# ------------------------------------------------------------------
def barrier_gradient(length, r_comm, l_act):
    """dV/dl of V(l) = (l - l_act)^2 / (r_comm - l) on l_act < l < r_comm.

    V is zero below l_act, continuously differentiable at l_act and grows
    without bound as l approaches the communication radius.
    """
    if length <= l_act:
        return 0.0
    gap = max(r_comm - length, 1e-6)
    e = length - l_act
    return (2.0 * e * gap + e * e) / (gap * gap)


def connectivity_velocity(P, A_keep, r_comm, l_act, gain=1.0):
    """Velocity that shortens the edges of A_keep before they reach r_comm."""
    P = np.asarray(P, dtype=float)
    V = np.zeros_like(P)
    for i, j in edges_of(A_keep):
        diff = P[i] - P[j]
        length = float(np.linalg.norm(diff))
        g = barrier_gradient(length, r_comm, l_act)
        if g > 0.0 and length > 1e-9:
            V[i] -= gain * g * diff / length
            V[j] += gain * g * diff / length
    return V


def repulsion_velocity(P, points, rho0, gain):
    """APF-style repulsion (Khatib) from each point within distance rho0."""
    P = np.asarray(P, dtype=float)
    V = np.zeros_like(P)
    for q in np.atleast_2d(np.asarray(points, dtype=float)):
        diff = P - q
        rho = np.linalg.norm(diff, axis=1)
        for i in range(P.shape[0]):
            if 1e-9 < rho[i] < rho0:
                mag = gain * (1.0 / rho[i] - 1.0 / rho0) / rho[i] ** 2
                V[i] += mag * diff[i] / rho[i]
    return V


def mutual_repulsion_velocity(P, rho0, gain):
    """Pairwise APF repulsion between drones closer than rho0."""
    P = np.asarray(P, dtype=float)
    V = np.zeros_like(P)
    n = P.shape[0]
    for i in range(n):
        for j in range(i + 1, n):
            diff = P[i] - P[j]
            rho = float(np.linalg.norm(diff))
            if 1e-9 < rho < rho0:
                push = gain * (1.0 / rho - 1.0 / rho0) / rho ** 2 * diff / rho
                V[i] += push
                V[j] -= push
    return V


# ------------------------------------------------------------------
# Simulators
# ------------------------------------------------------------------
def _saturate(V, v_max):
    if v_max is None:
        return V
    speed = np.linalg.norm(V, axis=1, keepdims=True)
    return V * np.minimum(1.0, v_max / np.maximum(speed, 1e-12))


def _record(rec, t, P, O, A, A_form):
    lengths = edge_lengths(P, A_form)
    rec["t"].append(t)
    rec["err"].append(formation_error(P, O, A_form))
    rec["err_c"].append(formation_error_centred(P, O))
    rec["lam2"].append(algebraic_connectivity(laplacian(A)))
    rec["lmin"].append(float(lengths.min()))
    rec["lmax"].append(float(lengths.max()))
    rec["nedges"].append(len(edges_of(A)))


def simulate_formation(P0, offsets, t_end, dt=0.02, gain=1.0, r_comm=None,
                       A_fixed=None, A_form=None, ref_fn=None, pinned=(),
                       gain_ref=1.0, extra_fn=None, v_max=None):
    """First-order formation control with a switching radius graph.

    Every step: build the communication graph (radius r_comm, or A_fixed),
    compute the formation velocity, add extra_fn(t, P, A) (avoidance,
    range keeping, ...), saturate to v_max and take an Euler step.
    ref_fn(t) returns (r, rdot) of the (virtual) leader.  A_form is the
    formation graph over which the error and the edge lengths are
    measured (default: the complete graph).  Returns a dict of arrays:
    t, P (steps+1, n, dim), err, err_c, lam2, lmin, lmax, nedges.
    """
    P = np.array(P0, dtype=float)
    O = np.asarray(offsets, dtype=float)
    n = P.shape[0]
    if A_form is None:
        A_form = np.ones((n, n)) - np.eye(n)
    steps = int(round(t_end / dt))
    keys = ("t", "err", "err_c", "lam2", "lmin", "lmax", "nedges")
    rec = {k: [] for k in keys}
    traj = np.empty((steps + 1, n, P.shape[1]))
    for k in range(steps + 1):
        t = k * dt
        A = A_fixed if A_fixed is not None else radius_graph(P, r_comm)
        _record(rec, t, P, O, A, A_form)
        traj[k] = P
        if k == steps:
            break
        ref, ref_vel = ref_fn(t) if ref_fn is not None else (None, None)
        V = formation_velocity(P, O, A, gain, ref, ref_vel, pinned, gain_ref)
        if extra_fn is not None:
            V = V + extra_fn(t, P, A)
        P = P + dt * _saturate(V, v_max)
    out = {k: np.array(v) for k, v in rec.items()}
    out["P"] = traj
    return out


def simulate_formation_second_order(P0, V0, offsets, t_end, dt=0.02, kp=1.0,
                                    kv=1.0, kd=0.0, r_comm=None, A_fixed=None,
                                    A_form=None, ref_fn=None, pinned=()):
    """Double-integrator formation control (semi-implicit Euler)."""
    P = np.array(P0, dtype=float)
    Vel = np.array(V0, dtype=float)
    O = np.asarray(offsets, dtype=float)
    n = P.shape[0]
    if A_form is None:
        A_form = np.ones((n, n)) - np.eye(n)
    steps = int(round(t_end / dt))
    keys = ("t", "err", "err_c", "lam2", "lmin", "lmax", "nedges")
    rec = {k: [] for k in keys}
    traj = np.empty((steps + 1, n, P.shape[1]))
    vels = np.empty_like(traj)
    for k in range(steps + 1):
        t = k * dt
        A = A_fixed if A_fixed is not None else radius_graph(P, r_comm)
        _record(rec, t, P, O, A, A_form)
        traj[k] = P
        vels[k] = Vel
        if k == steps:
            break
        ref, ref_vel = ref_fn(t) if ref_fn is not None else (None, None)
        U = formation_acceleration(P, Vel, O, A, kp, kv, kd, ref, ref_vel,
                                   pinned)
        Vel = Vel + dt * U
        P = P + dt * Vel
    out = {k: np.array(v) for k, v in rec.items()}
    out["P"] = traj
    out["V"] = vels
    return out


# ------------------------------------------------------------------
# Flocking (Olfati-Saber's three terms with a linear action function)
# ------------------------------------------------------------------
def bump(z, h=0.2):
    """Olfati-Saber's bump function rho_h: 1 on [0, h), smooth to 0 at 1."""
    z = np.asarray(z, dtype=float)
    out = np.zeros_like(z)
    out[z < h] = 1.0
    m = (z >= h) & (z < 1.0)
    out[m] = 0.5 * (1.0 + np.cos(np.pi * (z[m] - h) / (1.0 - h)))
    return out


def flocking_acceleration(P, V, d, r, c_grad=1.0, c_align=1.0, target=None,
                          target_vel=None, c_nav=(1.0, 1.0)):
    """Acceleration u_i = gradient term + velocity alignment + navigation.

    Gradient term: sum_j rho_h(l_ij / r) (l_ij - d) n_ij, a smooth spring
    with rest length d and zero action beyond the interaction range r
    (repulsion below d, attraction between d and r).  Alignment: consensus
    on velocities with the same smooth weights.  Navigation: a PD term
    towards the target point (the gamma-agent).
    """
    P = np.asarray(P, dtype=float)
    V = np.asarray(V, dtype=float)
    n = P.shape[0]
    U = np.zeros_like(P)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            diff = P[j] - P[i]
            length = float(np.linalg.norm(diff))
            if length >= r or length < 1e-9:
                continue
            w = float(bump(length / r))
            U[i] += c_grad * w * (length - d) * diff / length
            U[i] += c_align * w * (V[j] - V[i])
    if target is not None:
        tv = np.zeros(P.shape[1]) if target_vel is None else target_vel
        U += -c_nav[0] * (P - np.asarray(target, dtype=float))
        U += -c_nav[1] * (V - np.asarray(tv, dtype=float))
    return U


def simulate_flock(P0, V0, t_end, dt=0.02, target_fn=None, **params):
    """Integrate the flocking dynamics; returns (times, positions, vels)."""
    P = np.array(P0, dtype=float)
    V = np.array(V0, dtype=float)
    steps = int(round(t_end / dt))
    traj = np.empty((steps + 1,) + P.shape)
    vels = np.empty_like(traj)
    traj[0], vels[0] = P, V
    for k in range(steps):
        t = k * dt
        target, tvel = target_fn(t) if target_fn is not None else (None, None)
        U = flocking_acceleration(P, V, target=target, target_vel=tvel,
                                  **params)
        V = V + dt * U
        P = P + dt * V
        traj[k + 1], vels[k + 1] = P, V
    return dt * np.arange(steps + 1), traj, vels


# ------------------------------------------------------------------
# Worked example of the chapter (all quoted numbers come from here)
# ------------------------------------------------------------------
EXAMPLE_POSITIONS = np.array([[0.0, 0.0], [2.0, 0.0], [1.0, 1.5], [3.5, 3.0]])
EXAMPLE_RADIUS = 3.0
EXAMPLE_ALTITUDES = np.array([10.0, 4.0, 7.0, 1.0])
EXAMPLE_OFFSETS = np.array([[0.0, 0.0], [2.0, 0.0], [2.0, 2.0], [0.0, 2.0]])


def worked_example(verbose=True):
    """Four drones, radius graph, Laplacian, consensus and formation."""
    P0, O = EXAMPLE_POSITIONS, EXAMPLE_OFFSETS
    A = radius_graph(P0, EXAMPLE_RADIUS)
    L = laplacian(A)
    lam = np.linalg.eigvalsh(L)
    z0 = EXAMPLE_ALTITUDES
    out = {"A": A, "L": L, "lam": lam, "lam2": lam[1]}
    times = [0.0, 0.5, 1.0, 2.0, 3.0, 5.0]
    d0 = disagreement(z0)
    rows = []
    for t in times:
        z = consensus_exact(L, z0, t)
        rows.append((t, z, disagreement(z), np.exp(-lam[1] * t) * d0))
    out["consensus_rows"] = rows
    out["eps_safe"] = safe_step_size(A)
    out["eps_exact"] = spectral_step_bound(L)
    out["discrete_ok"] = consensus_discrete(L, z0, 0.25, 4)
    out["discrete_bad"] = consensus_discrete(L, z0, 0.6, 4)
    sim = simulate_formation(P0, O, 10.0, dt=0.02, gain=1.0, A_fixed=A,
                             A_form=A)
    out["formation"] = sim
    out["centroid_shift"] = (P0 - O).mean(axis=0)
    out["final"] = sim["P"][-1]
    if verbose:
        np.set_printoptions(precision=4, suppress=True)
        print("edges:", edges_of(A), " degrees:", A.sum(axis=1))
        print("L =\n", L)
        print("eigenvalues:", lam, " lambda_2 =", lam[1],
              " time constant 1/lambda_2 =", 1.0 / lam[1])
        print("eps bounds: 1/d_max =", out["eps_safe"],
              " 2/lambda_n =", out["eps_exact"])
        print("continuous consensus on altitudes z0 =", z0,
              " mean =", z0.mean())
        for t, z, dis, bnd in rows:
            print("  t=%.1f  z=%s  |delta|=%.4f  bound=%.4f"
                  % (t, np.round(z, 3), dis, bnd))
        print("discrete eps=0.25:\n", np.round(out["discrete_ok"], 3))
        print("discrete eps=0.60:\n", np.round(out["discrete_bad"], 3))
        print("formation: e_F(0)=%.4f  e_c(0)=%.4f  centroid shift=%s"
              % (sim["err"][0], sim["err_c"][0], out["centroid_shift"]))
        for t in [0.0, 1.0, 2.0, 3.0, 5.0]:
            k = int(round(t / 0.02))
            print("  t=%.1f  e_F=%.4f  e_c=%.4f  e_c(0)exp(-t)=%.4f"
                  % (t, sim["err"][k], sim["err_c"][k],
                     sim["err_c"][0] * np.exp(-lam[1] * t)))
        print("final positions:\n", np.round(out["final"], 3))
    return out


# ------------------------------------------------------------------
# Self-test
# ------------------------------------------------------------------
def _self_test():
    t0 = time.time()
    rng = np.random.default_rng(23)

    # 1. Laplacian properties and lambda_2 (monitor vs numpy)
    for trial in range(6):
        P = rng.uniform(0.0, 6.0, size=(7, 2))
        A = radius_graph(P, 2.5 + 0.5 * trial)
        L = laplacian(A)
        assert np.allclose(L.sum(axis=1), 0.0)
        assert np.allclose(L, L.T)
        lam = np.linalg.eigvalsh(L)
        assert lam[0] > -1e-9 and abs(lam[0]) < 1e-9
        assert lam[-1] <= 2.0 * A.sum(axis=1).max() + 1e-9
        x = rng.standard_normal(7)
        quad = sum((x[i] - x[j]) ** 2 for i, j in edges_of(A))
        assert abs(x @ L @ x - quad) < 1e-9
        assert abs(fiedler_power_iteration(L) - lam[1]) < 1e-6
        assert (lam[1] > 1e-9) == is_connected(A)

    # 2. Worked example: spectrum {0, 1, 3, 4}, consensus to the mean
    ex = worked_example(verbose=False)
    assert np.allclose(ex["lam"], [0.0, 1.0, 3.0, 4.0])
    z0 = EXAMPLE_ALTITUDES
    _, Z = consensus_continuous(ex["L"], z0, 12.0, dt=0.01)
    assert np.allclose(Z[-1], z0.mean(), atol=1e-4)
    assert np.allclose(Z[100], consensus_exact(ex["L"], z0, 1.0), atol=1e-8)
    for t, z, dis, bnd in ex["consensus_rows"]:
        assert dis <= bnd + 1e-9

    # 3. Disconnected graph: cluster averages, no global agreement
    P = np.array([[0.0, 0.0], [1.0, 0.0], [10.0, 0.0], [11.0, 0.0]])
    A = radius_graph(P, 2.0)
    assert not is_connected(A)
    x0 = np.array([1.0, 3.0, 10.0, 14.0])
    _, X = consensus_continuous(laplacian(A), x0, 20.0)
    assert np.allclose(X[-1], [2.0, 2.0, 12.0, 12.0], atol=1e-6)
    assert disagreement(X[-1]) > 1.0
    assert abs(disagreement(X[-1]) - 10.0) < 1e-6   # quoted in the pitfall
    # Exercise 23.2(b): the 9 m gap has to be bridged before they agree
    L_path = laplacian(radius_graph(P, 9.0))
    assert is_connected(radius_graph(P, 9.0))
    assert not is_connected(radius_graph(P, 8.9))
    assert abs(algebraic_connectivity(L_path) - (2.0 - np.sqrt(2.0))) < 1e-9
    assert np.allclose(np.linalg.eigvalsh(laplacian(radius_graph(P, 10.0))),
                       [0.0, 2.0, 4.0, 4.0])

    # 4. Discrete-time step size: eps < 1/d_max converges, eps > 2/lambda_n
    #    diverges (the 4-cycle has lambda_n = 2 d_max, so both bounds agree)
    A4 = np.array([[0, 1, 0, 1], [1, 0, 1, 0], [0, 1, 0, 1], [1, 0, 1, 0]])
    L4 = laplacian(A4)
    assert abs(safe_step_size(A4) - 0.5) < 1e-12
    assert abs(spectral_step_bound(L4) - 0.5) < 1e-12
    x0 = np.array([4.0, 0.0, 2.0, 5.0])
    good = consensus_discrete(L4, x0, 0.45, 200)
    bad = consensus_discrete(L4, x0, 0.55, 60)
    assert disagreement(good[-1]) < 1e-6
    assert disagreement(bad[-1]) > disagreement(bad[0])
    for trial in range(5):
        A = radius_graph(rng.uniform(0.0, 5.0, size=(6, 2)), 3.0)
        if not is_connected(A):
            continue
        L = laplacian(A)
        eps = 0.95 * safe_step_size(A)
        assert eps < spectral_step_bound(L) + 1e-12
        rho = np.max(np.abs(1.0 - eps * np.linalg.eigvalsh(L)[1:]))
        assert rho < 1.0
        X = consensus_discrete(L, rng.standard_normal(6), eps, 400)
        assert disagreement(X[-1]) < 1e-6

    # 5. Leader-follower: everyone converges to the reference (pinning
    #    drone 1 of the example graph makes L + B positive definite)
    A = ex["A"]
    M = pinned_matrix(A, pinned=(0,))
    mu = np.linalg.eigvalsh(M)[0]
    assert mu > 0.1
    O = np.zeros((4, 1))
    Pp = EXAMPLE_ALTITUDES.reshape(4, 1).copy()
    ref = np.array([7.0])
    for _ in range(5000):
        Pp = Pp + 0.02 * formation_velocity(Pp, O, A, 1.0, ref, None, (0,))
    assert np.allclose(Pp, 7.0, atol=1e-6)
    # not pinned and disconnected from the pinned part: no convergence
    A_cut = A.copy()
    A_cut[2, 3] = A_cut[3, 2] = 0.0
    assert np.linalg.eigvalsh(pinned_matrix(A_cut, (0,)))[0] < 1e-9

    # 6. Formation error: zero exactly on the (translated) formation,
    #    translation invariant, complete-graph identity with the centred
    #    error, and convergence for a consistent d_ij set (first and
    #    second order, fixed graph and switching radius graph)
    O = EXAMPLE_OFFSETS
    Kn = np.ones((4, 4)) - np.eye(4)
    assert formation_error(O + np.array([3.0, -2.0]), O, Kn) < 1e-12
    P = EXAMPLE_POSITIONS
    e1 = formation_error(P, O, Kn)
    e2 = formation_error(P + np.array([5.0, 1.0]), O, Kn)
    assert abs(e1 - e2) < 1e-12
    ec = formation_error_centred(P, O)
    assert abs(e1 - np.sqrt(2.0 * 4 / 3.0) * ec) < 1e-12
    assert abs(ex["formation"]["err"][0] - 2.5) < 1e-12
    assert ex["formation"]["err"][-1] < 1e-2
    assert np.allclose(ex["final"], O + ex["centroid_shift"], atol=1e-3)
    sim = simulate_formation(P, O, 8.0, dt=0.02, gain=1.0, r_comm=3.5)
    assert sim["err"][-1] < 1e-3 and sim["lam2"].min() > 0.0
    sim2 = simulate_formation_second_order(P, np.zeros((4, 2)), O, 25.0,
                                           dt=0.01, kp=1.0, kv=1.0, kd=0.5,
                                           A_fixed=ex["A"], A_form=ex["A"])
    assert sim2["err"][-1] < 1e-3
    assert np.linalg.norm(sim2["V"][-1]) < 1e-3
    # without any damping the double integrator oscillates for ever
    sim3 = simulate_formation_second_order(P, np.zeros((4, 2)), O, 25.0,
                                           dt=0.01, kp=1.0, kv=0.0, kd=0.0,
                                           A_fixed=ex["A"], A_form=ex["A"])
    assert sim3["err"][-1] > 0.1

    # 7. Displacements built from offsets are antisymmetric, and an
    #    inconsistent set (d_ji != -d_ij) makes the centroid drift for ever
    #    at the velocity -(1/n) sum_i sum_{j in N_i} d_ij (Exercise 23.5)
    D = displacement_targets(O)
    assert np.allclose(D, -np.transpose(D, (1, 0, 2)))
    A_path = np.array([[0.0, 1.0, 0.0], [1.0, 0.0, 1.0], [0.0, 1.0, 0.0]])
    D_bad = np.zeros((3, 3, 2))
    for i, j in [(0, 1), (1, 0), (1, 2), (2, 1)]:
        D_bad[i, j] = [1.0, 0.0]            # both ends want the same offset
    Pb = np.array([[0.0, 0.0], [1.0, 0.0], [2.0, 0.0]])
    for _ in range(500):
        Vb = np.array([sum(Pb[j] - Pb[i] - D_bad[i, j]
                           for j in np.flatnonzero(A_path[i]))
                       for i in range(3)])
        Pb = Pb + 0.01 * Vb
    assert np.allclose(Vb.mean(axis=0), [-4.0 / 3.0, 0.0], atol=1e-9)
    assert np.linalg.norm(Pb.mean(axis=0)) > 5.0        # it really drifts away

    # 8. Range keeping: the barrier keeps a stretched edge below r_comm
    Pk = np.array([[0.0, 0.0], [3.3, 0.0]])
    A2 = np.array([[0.0, 1.0], [1.0, 0.0]])
    for _ in range(200):
        pull = np.array([[-0.6, 0.0], [0.6, 0.0]])  # disturbance stretching
        Pk = Pk + 0.02 * (pull + connectivity_velocity(Pk, A2, 3.5, 3.0))
        assert np.linalg.norm(Pk[0] - Pk[1]) < 3.5

    # 9. Flocking: velocities align, no collisions, the flock stays together
    P0 = rng.uniform(0.0, 6.0, size=(8, 2))
    V0 = rng.uniform(-0.5, 0.5, size=(8, 2))
    tgt = (lambda t: (np.array([8.0 + 0.5 * t, 4.0 + 0.2 * t]),
                      np.array([0.5, 0.2])))
    _, traj, vels = simulate_flock(P0, V0, 40.0, dt=0.02, target_fn=tgt,
                                   d=1.5, r=2.5, c_grad=1.0, c_align=1.0,
                                   c_nav=(0.3, 0.6))
    assert disagreement(vels[-1]) < 1e-2
    dmin = min(np.linalg.norm(traj[-1][i] - traj[-1][j])
               for i in range(8) for j in range(i + 1, 8))
    assert dmin > 0.5 * 1.5
    assert np.linalg.norm(traj[-1] - traj[-1].mean(axis=0), axis=1).max() < 6.0

    # 10. Numbers quoted in the exercises and their solutions
    A5 = np.array([[0, 1, 1, 1], [1, 0, 1, 0], [1, 1, 0, 1], [1, 0, 1, 0]])
    assert np.allclose(np.linalg.eigvalsh(laplacian(A5)), [0.0, 2.0, 4.0, 4.0])
    M = pinned_matrix(ex["A"], pinned=(0,))
    z = np.linalg.solve(M, np.ones(4))      # lag without feed-forward
    assert np.allclose(z, [4.0, 16.0 / 3.0, 17.0 / 3.0, 20.0 / 3.0])
    lag = np.sqrt(np.mean([(z[j] - z[i]) ** 2 for i, j in edges_of(ex["A"])]))
    assert abs(lag - 1.19) < 0.01
    assert abs(np.linalg.eigvalsh(M)[0] - 0.178) < 1e-3   # mu_1 of L + B
    # non-closing triangle d_12 = d_23 = (1, 0), d_31 = (-1, 0): e_F = 1/3
    D3 = np.zeros((3, 3, 2))
    for i, j, d in ((0, 1, 1.0), (1, 2, 1.0), (2, 0, -1.0)):
        D3[i, j, 0], D3[j, i, 0] = d, -d
    P3 = np.array([[0.0, 0.0], [1.0, 0.3], [0.5, 1.0]])
    for _ in range(3000):
        V3 = np.array([sum(P3[j] - P3[i] - D3[i, j] for j in range(3) if j != i)
                       for i in range(3)])
        P3 = P3 + 0.01 * V3
    e3 = np.sqrt(np.mean([np.sum((P3[j] - P3[i] - D3[i, j]) ** 2)
                          for i, j in ((0, 1), (1, 2), (2, 0))]))
    assert abs(e3 - 1.0 / 3.0) < 1e-6

    print("ch23_consensus: all self-tests passed in %.1f s"
          % (time.time() - t0))


if __name__ == "__main__":
    worked_example(verbose=True)
    _self_test()
