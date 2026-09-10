"""Numbers and data for Appendix B (Mathematical Refresher).

Recomputes every number quoted in the worked examples of the appendix and
checks it with an assert, then writes

  figures/data/appB-gradient-descent.dat   columns: k xa ya xb yb

for the gradient-descent figure (two step sizes on the same quadratic).
NumPy only, fixed seed.  Run from anywhere:

    python3 code/figures/gen_appB_numbers.py
"""
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "figures", "data")

SIGMA = np.array([[2.0, 1.2], [1.2, 1.0]])
MU = np.array([2.0, 1.0])


def show(label, value):
    """Print one named number (or array) on one line."""
    if isinstance(value, np.ndarray):
        value = np.array2string(value, precision=4, suppress_small=True)
    elif isinstance(value, float):
        value = "%.4f" % value
    print("%-42s %s" % (label, value))


# ---------------------------------------------------------------- B.1
def linear_algebra():
    print("== B.1 vectors and matrices ==")
    w, Q = np.linalg.eigh(SIGMA)          # ascending eigenvalues
    assert np.allclose(w, [0.2, 2.8])
    q1 = Q[:, 1] * np.sign(Q[0, 1])       # eigenvector of 2.8, x > 0
    assert np.allclose(q1, np.array([3.0, 2.0]) / math.sqrt(13))
    angle = math.degrees(math.atan2(q1[1], q1[0]))
    show("eigenvalues of Sigma", w[::-1])
    show("leading eigenvector", q1)
    show("orientation of the ellipse (deg)", angle)
    show("semi-axes of the 1-sigma ellipse", np.sqrt(w[::-1]))
    assert np.isclose(np.linalg.det(SIGMA), 0.56)
    assert np.isclose(np.trace(SIGMA), 3.0)
    assert np.allclose(SIGMA, Q @ np.diag(w) @ Q.T)
    L = np.linalg.cholesky(SIGMA)
    assert np.allclose(L @ L.T, SIGMA)
    show("Cholesky factor L", L)
    # Schur complement and block inverse
    s = SIGMA[0, 0] - SIGMA[0, 1] / SIGMA[1, 1] * SIGMA[1, 0]
    Sinv = np.linalg.inv(SIGMA)
    assert np.isclose(s, 0.56) and np.isclose(Sinv[0, 0], 1.0 / s)
    assert np.isclose(np.linalg.det(SIGMA), SIGMA[1, 1] * s)
    show("Schur complement Sigma_xx - ...", s)
    show("inverse of Sigma", Sinv)
    # least squares: p(t) = p0 + v t through (0,0.0), (1,1.1), (2,1.9)
    A = np.array([[1.0, 0.0], [1.0, 1.0], [1.0, 2.0]])
    b = np.array([0.0, 1.1, 1.9])
    AtA, Atb = A.T @ A, A.T @ b
    x = np.linalg.solve(AtA, Atb)
    assert np.allclose(AtA, [[3, 3], [3, 5]]) and np.allclose(Atb, [3.0, 4.9])
    assert np.allclose(x, [0.05, 0.95])
    r = A @ x - b
    assert np.allclose(r, [0.05, -0.10, 0.05]) and np.isclose(r @ r, 0.015)
    assert np.allclose(A.T @ r, 0.0)      # residual orthogonal to columns
    show("normal equations A^T A, A^T b", (AtA.tolist(), Atb.tolist()))
    show("least-squares solution (p0, v)", x)
    show("residuals, squared norm", (r.round(4).tolist(), float(r @ r)))
    return angle


# ---------------------------------------------------------------- B.2
def calculus():
    print("== B.2 calculus ==")

    def h(x):                             # range and bearing of (px, py)
        return np.array([math.hypot(x[0], x[1]), math.atan2(x[1], x[0])])

    def jac(x):
        r2 = x[0] ** 2 + x[1] ** 2
        r = math.sqrt(r2)
        return np.array([[x[0] / r, x[1] / r, 0.0, 0.0],
                         [-x[1] / r2, x[0] / r2, 0.0, 0.0]])

    x0 = np.array([3.0, 4.0, 1.0, 0.5])
    J = jac(x0)
    assert np.allclose(J, [[0.6, 0.8, 0, 0], [-0.16, 0.12, 0, 0]])
    eps, Jfd = 1e-6, np.zeros((2, 4))
    for j in range(4):
        e = np.zeros(4)
        e[j] = eps
        Jfd[:, j] = (h(x0 + e) - h(x0 - e)) / (2 * eps)
    assert np.allclose(J, Jfd, atol=1e-6)
    d = np.array([0.1, -0.2, 0.0, 0.0])
    lin = h(x0) + J @ d
    exact = h(x0 + d)
    show("h(x0) = (range, bearing)", h(x0))
    show("Jacobian H at x0", J)
    show("first-order prediction h(x0)+H d", lin)
    show("exact h(x0+d)", exact)
    show("linearization error", exact - lin)
    assert np.allclose(lin, [4.90, 0.88730], atol=5e-5)
    assert abs(exact[0] - 4.9041) < 5e-5 and abs(exact[1] - 0.8865) < 5e-5
    # double integrator: closed form equals the matrix form
    dt, p, v, a = 0.1, 0.0, 2.0, 1.0
    p1, v1 = p + v * dt + 0.5 * a * dt ** 2, v + a * dt
    Ad = np.array([[1.0, dt], [0.0, 1.0]])
    Bd = np.array([0.5 * dt ** 2, dt])
    assert np.allclose(Ad @ np.array([p, v]) + Bd * a, [p1, v1])
    assert np.isclose(p1, 0.205) and np.isclose(v1, 2.1)
    show("double integrator step (p', v')", (p1, v1))


# ---------------------------------------------------------------- B.3
def chi2_cdf(g, n):
    """Closed-form chi-square CDF for n = 1, 2, 3 degrees of freedom."""
    if n == 1:
        return math.erf(math.sqrt(g / 2.0))
    if n == 2:
        return 1.0 - math.exp(-g / 2.0)
    if n == 3:
        return math.erf(math.sqrt(g / 2.0)) - math.sqrt(2 * g / math.pi) * math.exp(-g / 2.0)
    raise ValueError(n)


def chi2_quantile(p, n):
    lo, hi = 0.0, 50.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if chi2_cdf(mid, n) < p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def probability():
    print("== B.3 probability ==")
    # conditioning of the joint Gaussian on y = 2
    y_obs = 2.0
    m = MU[0] + SIGMA[0, 1] / SIGMA[1, 1] * (y_obs - MU[1])
    s = SIGMA[0, 0] - SIGMA[0, 1] / SIGMA[1, 1] * SIGMA[1, 0]
    assert np.isclose(m, 3.2) and np.isclose(s, 0.56)
    show("x | y=2 : mean, variance, std", (m, s, math.sqrt(s)))
    show("marginal of x : mean, variance, std", (MU[0], SIGMA[0, 0], math.sqrt(SIGMA[0, 0])))
    # Monte Carlo: mass inside the 2-sigma ellipse, exact 1 - exp(-2)
    rng = np.random.default_rng(0)
    L = np.linalg.cholesky(SIGMA)
    N = 10000
    xs = MU + (L @ rng.standard_normal((2, N))).T
    d2 = np.einsum("ij,jk,ik->i", xs - MU, np.linalg.inv(SIGMA), xs - MU)
    p_hat = float(np.mean(d2 <= 4.0))
    p_exact = 1.0 - math.exp(-2.0)
    se = math.sqrt(p_hat * (1 - p_hat) / N)
    show("Monte Carlo P(d^2 <= 4), N=10000", p_hat)
    show("exact 1-exp(-2), standard error", (p_exact, se))
    assert abs(p_hat - p_exact) < 3 * se
    assert np.isclose(p_hat, 0.8695)
    # chi-square gates
    gates = {}
    for n in (1, 2, 3):
        gates[n] = (chi2_quantile(0.95, n), chi2_quantile(0.99, n))
        show("chi2 gate n=%d (95%%, 99%%)" % n, gates[n])
    assert np.allclose(gates[1], [3.8415, 6.6349], atol=2e-4)
    assert np.allclose(gates[2], [-2 * math.log(0.05), -2 * math.log(0.01)])
    assert np.allclose(gates[3], [7.8147, 11.3449], atol=2e-4)
    # Bayes: prior 0.1, detection 0.9, false alarm 0.2
    post = 0.1 * 0.9 / (0.1 * 0.9 + 0.9 * 0.2)
    assert np.isclose(post, 1.0 / 3.0)
    show("Bayes example posterior", post)


# ---------------------------------------------------------------- B.4
def lp2d(cons, c):
    """Maximize c.z over {z : a.z <= b for (a, b) in cons} by vertex enumeration."""
    best, arg = -math.inf, None
    A = np.array([a for a, _ in cons], float)
    b = np.array([bb for _, bb in cons], float)
    for i in range(len(cons)):
        for j in range(i + 1, len(cons)):
            M = A[[i, j]]
            if abs(np.linalg.det(M)) < 1e-12:
                continue
            z = np.linalg.solve(M, b[[i, j]])
            if np.all(A @ z <= b + 1e-9) and c @ z > best + 1e-12:
                best, arg = float(c @ z), z
    return arg, best


def optimization():
    print("== B.4 optimization ==")
    # LP example: max 2 z1 + 3 z2, z1 + z2 <= 4, z1 + 3 z2 <= 6, z >= 0
    cons = [((1, 1), 4), ((1, 3), 6), ((-1, 0), 0), ((0, -1), 0)]
    c = np.array([2.0, 3.0])
    z, val = lp2d(cons, c)
    assert np.allclose(z, [3, 1]) and np.isclose(val, 9)
    verts = {(0, 0): 0, (4, 0): 8, (3, 1): 9, (0, 2): 6}
    for v, obj in verts.items():
        assert np.isclose(c @ np.array(v, float), obj)
    show("LP vertices and objective", verts)
    show("LP optimum z*, value", (z, val))
    lam = np.linalg.solve(np.array([[1.0, 1.0], [1.0, 3.0]]).T, c)   # c = A_act^T lam
    assert np.allclose(lam, [1.5, 0.5])
    show("KKT multipliers of the active rows", lam)
    # branch and bound: max 5 z1 + 4 z2, 6 z1 + 4 z2 <= 24, z1 + 2 z2 <= 6, z >= 0 integer
    base = [((6, 4), 24), ((1, 2), 6), ((-1, 0), 0), ((0, -1), 0)]
    cb = np.array([5.0, 4.0])
    nodes = {
        "1 root": [],
        "2 z2<=1": [((0, 1), 1)],
        "3 z2>=2": [((0, -1), -2)],
        "4 z2<=1, z1<=3": [((0, 1), 1), ((1, 0), 3)],
        "5 z2<=1, z1>=4": [((0, 1), 1), ((-1, 0), -4)],
    }
    res = {k: lp2d(base + extra, cb) for k, extra in nodes.items()}
    for k, (zz, vv) in res.items():
        show("B&B node " + k, (zz.round(4).tolist(), round(vv, 4)))
    assert np.allclose(res["1 root"][0], [3, 1.5]) and np.isclose(res["1 root"][1], 21)
    assert np.allclose(res["2 z2<=1"][0], [10 / 3, 1]) and np.isclose(res["2 z2<=1"][1], 62 / 3)
    assert np.allclose(res["3 z2>=2"][0], [2, 2]) and np.isclose(res["3 z2>=2"][1], 18)
    assert np.allclose(res["4 z2<=1, z1<=3"][0], [3, 1]) and np.isclose(res["4 z2<=1, z1<=3"][1], 19)
    assert np.allclose(res["5 z2<=1, z1>=4"][0], [4, 0]) and np.isclose(res["5 z2<=1, z1>=4"][1], 20)
    best = max((5 * z1 + 4 * z2, (z1, z2)) for z1 in range(5) for z2 in range(4)
               if 6 * z1 + 4 * z2 <= 24 and z1 + 2 * z2 <= 6)
    assert best == (20, (4, 0))
    show("integer optimum by enumeration", best)
    # gradient descent on f = 0.5 (x1^2 + 10 x2^2) from (9, 2)
    lam_ = np.array([1.0, 10.0])
    x0 = np.array([9.0, 2.0])
    K = 20
    rows = []
    paths = {}
    for alpha in (0.05, 0.18, 0.21):
        x = x0.copy()
        path = [x.copy()]
        for _ in range(K):
            x = x - alpha * lam_ * x
            path.append(x.copy())
        paths[alpha] = np.array(path)
        fac = 1 - alpha * lam_
        show("alpha=%.2f contraction factors" % alpha, fac)
        show("alpha=%.2f x_20, f(x_20)" % alpha, (path[-1], 0.5 * float(lam_ @ path[-1] ** 2)))
    assert np.allclose(1 - 0.21 * lam_, [0.79, -1.1])
    assert np.allclose(paths[0.05][-1], [9 * 0.95 ** K, 2 * 0.5 ** K])
    assert np.allclose(paths[0.18][-1], [9 * 0.82 ** K, 2 * (-0.8) ** K])
    assert abs(paths[0.21][-1][1]) > 2 * 1.1 ** (K - 1)
    with open(os.path.join(DATA, "appB-gradient-descent.dat"), "w") as f:
        f.write("k xa ya xb yb\n")
        for k in range(K + 1):
            f.write("%d %.5f %.6f %.5f %.6f\n" % (k, paths[0.05][k, 0], paths[0.05][k, 1],
                                                  paths[0.18][k, 0], paths[0.18][k, 1]))


# ---------------------------------------------------------------- B.5
def graphs():
    print("== B.5 graphs ==")
    edges = [(0, 1), (1, 2), (2, 3), (1, 3)]
    n = 4
    A = np.zeros((n, n))
    for i, j in edges:
        A[i, j] = A[j, i] = 1.0
    D = np.diag(A.sum(axis=1))
    L = D - A
    w, V = np.linalg.eigh(L)
    show("degrees", np.diag(D))
    show("Laplacian", L)
    show("eigenvalues", w)
    assert np.allclose(w, [0, 1, 3, 4])
    assert np.allclose(L @ np.ones(n), 0)
    fied = V[:, 1] / V[3, 1]
    show("Fiedler vector (scaled)", fied)
    assert np.allclose(fied, [-2, 0, 1, 1])
    x = np.array([1.0, -2.0, 0.5, 3.0])
    assert np.isclose(x @ L @ x, sum((x[i] - x[j]) ** 2 for i, j in edges))
    assert w[-1] <= 2 * np.max(np.diag(D))
    L2 = L.copy()
    L2[0, 1] = L2[1, 0] = 0.0
    L2[0, 0] -= 1.0
    L2[1, 1] -= 1.0
    w2 = np.linalg.eigvalsh(L2)
    show("eigenvalues without edge {1,2}", w2)
    assert abs(w2[1]) < 1e-12 and np.allclose(w2, [0, 0, 3, 3])
    # consensus preview: x(t) = expm(-L t) x0 converges to the average
    x0 = np.array([4.0, 0.0, 1.0, -1.0])
    xt = V @ np.diag(np.exp(-w * 10.0)) @ V.T @ x0
    assert np.allclose(xt, np.mean(x0), atol=1e-3)
    show("consensus at t=10 from x0", (x0.tolist(), xt.round(3).tolist()))


if __name__ == "__main__":
    import time
    t0 = time.time()
    linear_algebra()
    calculus()
    probability()
    optimization()
    graphs()
    print("self-test passed in %.2f s" % (time.time() - t0))
