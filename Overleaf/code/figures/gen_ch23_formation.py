"""Generate the data files and one TikZ file of Chapter 23.

    figures/data/ch23-consensus.dat   consensus of 6 drones on two radius
                                      graphs (R = 2.1 and R = 3.8 m) with
                                      different lambda_2: columns t, a1..a6,
                                      b1..b6 (states), disa, disb
                                      (disagreement norms), bnda, bndb
                                      (the bounds exp(-lambda_2 t) |delta0|)
    figures/data/ch23-square.dat      the worked example: four drones on the
                                      fixed graph of the example converging
                                      into a square: t, x1 y1 .. x4 y4, err
                                      (edge RMS formation error), errc
                                      (centerd error)
    figures/data/ch23-leader.dat      formation forming while drone 1 is
                                      pinned to a reference moving along a
                                      path: t, rx, ry, x1 y1 .. x4 y4, err,
                                      lam2, lmin, lmax
    figures/ch23/leader.tex           complete TikZ picture for the above
                                      (trajectories plus formation snapshots)
    figures/data/ch23-avoidance.dat   formation error and edge lengths while
                                      an intruder crosses the formation:
                                      t, err, lmin, lmax, dint (distance to
                                      the intruder), lam2, viol (edges longer
                                      than R_comm = 3.2 m), active (0/1)

Everything is deterministic (no randomness is used).  The printed
numbers are the ones quoted in the chapter text and captions.
Run from Overleaf/:   python3 code/figures/gen_ch23_formation.py
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import ch23_consensus as cf  # noqa: E402

ROOT = os.path.join(os.path.dirname(HERE), "..")
DATA = os.path.join(ROOT, "figures", "data")
FIGS = os.path.join(ROOT, "figures", "ch23")
os.makedirs(DATA, exist_ok=True)
os.makedirs(FIGS, exist_ok=True)


def write_dat(name, header, rows):
    path = os.path.join(DATA, name)
    with open(path, "w") as f:
        f.write(header + "\n")
        for row in rows:
            f.write(" ".join("%.5f" % v for v in row) + "\n")
    print("wrote", os.path.relpath(path, ROOT), "(%d rows)" % len(rows))


# ------------------------------------------------------------------
# 1. Consensus of six drones on two radius graphs
# ------------------------------------------------------------------
def consensus_figure():
    P6 = np.array([[0.0, 0.0], [1.8, 0.6], [3.4, -0.4], [5.1, 0.5],
                   [6.9, -0.3], [8.5, 0.4]])
    x0 = np.array([12.0, 3.0, 9.0, 1.0, 6.0, 11.0])
    radii = (2.1, 3.8)
    Ls, lam2s = [], []
    for r in radii:
        W = cf.radius_graph(P6, r)
        L = cf.laplacian(W)
        lam = np.linalg.eigvalsh(L)
        Ls.append(L)
        lam2s.append(lam[1])
        print("consensus: R=%.1f edges=%s lambda_2=%.4f 1/lambda_2=%.3f "
              "lambda_n=%.4f d_max=%d" % (r, cf.edges_of(W), lam[1],
                                          1.0 / lam[1], lam[-1],
                                          int(W.sum(axis=1).max())))
    d0 = cf.disagreement(x0)
    rows = []
    for t in np.arange(0.0, 10.0 + 1e-9, 0.05):
        xa = cf.consensus_exact(Ls[0], x0, t)
        xb = cf.consensus_exact(Ls[1], x0, t)
        rows.append([t] + list(xa) + list(xb)
                    + [cf.disagreement(xa), cf.disagreement(xb),
                       d0 * np.exp(-lam2s[0] * t), d0 * np.exp(-lam2s[1] * t)])
    header = ("t " + " ".join("a%d" % i for i in range(1, 7)) + " "
              + " ".join("b%d" % i for i in range(1, 7))
              + " disa disb bnda bndb")
    write_dat("ch23-consensus.dat", header, rows)
    for r, L, lam2 in zip(radii, Ls, lam2s):
        for target in (0.1, 0.01):
            t = next(tt for tt in np.arange(0.0, 60.0, 0.01)
                     if cf.disagreement(cf.consensus_exact(L, x0, tt))
                     < target * d0)
            print("  R=%.1f: disagreement below %.0f%% of its initial "
                  "value after %.2f s" % (r, 100 * target, t))


# ------------------------------------------------------------------
# 2. The worked example: four drones converging into a square
# ------------------------------------------------------------------
def square_figure():
    ex = cf.worked_example(verbose=False)
    sim = ex["formation"]
    rows = []
    for k in range(0, len(sim["t"]), 5):
        P = sim["P"][k]
        rows.append([sim["t"][k]] + list(P.reshape(-1))
                    + [sim["err"][k], sim["err_c"][k]])
    write_dat("ch23-square.dat",
              "t x1 y1 x2 y2 x3 y3 x4 y4 err errc", rows)
    k1 = int(np.argmax(sim["err"] < 0.01 * sim["err"][0]))
    print("square: e_F below 1%% of e_F(0) after %.2f s; final centroid "
          "shift %s" % (sim["t"][k1], np.round(ex["centroid_shift"], 3)))


# ------------------------------------------------------------------
# 3. Formation forming behind a leader that follows a path
# ------------------------------------------------------------------
WAYPOINTS = np.array([[0.0, 0.0], [8.0, 0.0], [8.0, 6.0], [16.0, 6.0]])
SPEED = 1.0
OFFSETS = np.array([[0.0, 0.0], [-2.0, 0.0], [-2.0, -2.0], [0.0, -2.0]])
R_COMM = 3.5


def reference(t):
    """Position and velocity of the reference point along the waypoints."""
    s = SPEED * t
    for a, b in zip(WAYPOINTS[:-1], WAYPOINTS[1:]):
        seg = np.linalg.norm(b - a)
        if s <= seg:
            direction = (b - a) / seg
            return a + s * direction, SPEED * direction
        s -= seg
    return WAYPOINTS[-1].copy(), np.zeros(2)


def leader_figure():
    P0 = np.array([[-1.0, 2.0], [-4.0, 3.0], [-3.0, 0.5], [0.5, -0.5]])
    W0 = cf.radius_graph(P0, R_COMM)
    print("leader: initial edges %s connected=%s" % (cf.edges_of(W0),
                                                     cf.is_connected(W0)))
    sim = cf.simulate_formation(P0, OFFSETS, 24.0, dt=0.02, gain=1.0,
                                r_comm=R_COMM, ref_fn=reference, pinned=(0,),
                                gain_ref=1.5, v_max=3.0)
    # the same run without velocity feed-forward: the followers lag
    no_ff = cf.simulate_formation(
        P0, OFFSETS, 24.0, dt=0.02, gain=1.0, r_comm=R_COMM,
        ref_fn=lambda t: (reference(t)[0], None), pinned=(0,), gain_ref=1.5,
        v_max=3.0)
    rows = []
    for k in range(0, len(sim["t"]), 10):
        r, _ = reference(sim["t"][k])
        rows.append([sim["t"][k], r[0], r[1]] + list(sim["P"][k].reshape(-1))
                    + [sim["err"][k], sim["lam2"][k], sim["lmin"][k],
                       sim["lmax"][k]])
    write_dat("ch23-leader.dat",
              "t rx ry x1 y1 x2 y2 x3 y3 x4 y4 err lam2 lmin lmax", rows)
    k5 = int(round(5.0 / 0.02))
    k20 = int(round(20.0 / 0.02))
    print("leader: e_F(0)=%.3f e_F(5s)=%.3f e_F(20s)=%.4f max lmax=%.3f "
          "min lam2=%.3f; without feed-forward e_F(5s)=%.3f e_F(20s)=%.3f"
          % (sim["err"][0], sim["err"][k5], sim["err"][k20],
             sim["lmax"].max(), sim["lam2"].min(), no_ff["err"][k5],
             no_ff["err"][k20]))
    # complete TikZ file with trajectories and formation snapshots
    snaps = [0.0, 3.0, 8.0, 12.0, 17.0, 23.0]
    colors = ["sbBlue", "sbOrange", "sbGreen", "sbPurple"]
    lines = []
    lines.append("% Generated by code/figures/gen_ch23_formation.py -- "
                 "do not edit by hand.")
    lines.append("% Four drones forming a square while drone 1 is pinned "
                 "to a reference moving along a path.")
    lines.append("\\begin{tikzpicture}")
    lines.append("\\begin{axis}[width=\\textwidth,height=7.2cm,axis equal "
                 "image,xmin=-5,xmax=17.5,ymin=-4.5,ymax=8,xlabel={$x$ [m]},"
                 "ylabel={$y$ [m]},grid=major,font=\\footnotesize,"
                 "legend style={at={(0.02,0.98)},anchor=north west,"
                 "font=\\scriptsize,fill opacity=0.9,draw opacity=1,"
                 "text opacity=1},legend cell align=left]")
    lines.append("\\addplot[black!50,dashed,thick] table[x=rx,y=ry]"
                 "{figures/data/ch23-leader.dat};")
    lines.append("\\addlegendentry{reference path $\\vect{r}(t)$}")
    for i, c in enumerate(colors):
        lines.append("\\addplot[%s,thin] table[x=x%d,y=y%d]"
                     "{figures/data/ch23-leader.dat};" % (c, i + 1, i + 1))
        lines.append("\\addlegendentry{drone %d%s}"
                     % (i + 1, " (leader)" if i == 0 else ""))
    for ts in snaps:
        k = int(round(ts / 0.02))
        P = sim["P"][k]
        poly = " ".join("(%.3f,%.3f)" % (P[i, 0], P[i, 1])
                        for i in [0, 1, 2, 3, 0])
        lines.append("\\addplot[black!70,thin,fill=sbBlue!12,forget plot] "
                     "coordinates {%s};" % poly)
        for i, c in enumerate(colors):
            lines.append("\\addplot[only marks,mark=*,mark size=1.6pt,%s,"
                         "forget plot] coordinates {(%.3f,%.3f)};"
                         % (c, P[i, 0], P[i, 1]))
        cx, cy = P.mean(axis=0)
        lines.append("\\node[sbannot,font=\\scriptsize] at (axis cs:%.3f,%.3f) "
                     "{$t{=}%g$}; " % (cx, cy - 1.55, ts))
    lines.append("\\end{axis}")
    lines.append("\\end{tikzpicture}")
    path = os.path.join(FIGS, "leader.tex")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("wrote", os.path.relpath(path, ROOT))


# ------------------------------------------------------------------
# 4. Formation error and edge lengths during an avoidance maneuver
# ------------------------------------------------------------------
D_SAFE = 0.8
RHO_INTRUDER = 2.0
R_AVOID = 3.2
L_ACT = 2.95
K_REP = 4.0


def intruder(t):
    return np.array([8.5, 8.0 - 1.0 * t])


def avoidance_figure():
    Kn = np.ones((4, 4)) - np.eye(4)

    def ref_straight(t):
        return np.array([t, 0.0]), np.array([1.0, 0.0])

    def extra(t, P, W):
        v = cf.repulsion_velocity(P, intruder(t), RHO_INTRUDER, K_REP)
        v += cf.mutual_repulsion_velocity(P, 1.5 * D_SAFE, 0.3)
        v += cf.connectivity_velocity(P, Kn, R_AVOID, L_ACT, 0.5)
        return v

    sim = cf.simulate_formation(OFFSETS.copy(), OFFSETS, 20.0, dt=0.02,
                                gain=1.0, r_comm=R_AVOID, W_form=Kn,
                                ref_fn=ref_straight, pinned=(0,), gain_ref=1.5,
                                extra_fn=extra, v_max=2.5)
    rows = []
    dint_all, active_all = [], []
    for k, t in enumerate(sim["t"]):
        d = np.linalg.norm(sim["P"][k] - intruder(t), axis=1)
        dint_all.append(d.min())
        active_all.append(1.0 if d.min() < RHO_INTRUDER else 0.0)
    dint_all = np.array(dint_all)
    active_all = np.array(active_all)
    for k in range(0, len(sim["t"]), 5):
        viol = float(np.sum(cf.edge_lengths(sim["P"][k], Kn) > R_AVOID))
        rows.append([sim["t"][k], sim["err"][k], sim["lmin"][k],
                     sim["lmax"][k], dint_all[k], sim["lam2"][k], viol,
                     active_all[k]])
    write_dat("ch23-avoidance.dat",
              "t err lmin lmax dint lam2 viol active", rows)
    kp = int(np.argmax(sim["err"]))
    on = sim["t"][np.argmax(active_all > 0)]
    off = sim["t"][len(active_all) - 1 - np.argmax(active_all[::-1] > 0)]
    after = np.where((sim["t"] > sim["t"][kp]) & (sim["err"] < 0.05))[0]
    t_rec = sim["t"][after[0]] if len(after) else float("nan")
    print("avoidance: intruder within %.1f m during [%.2f, %.2f] s; peak "
          "e_F=%.3f m at t=%.2f s; e_F<0.05 m again at t=%.2f s; min "
          "distance to intruder %.3f m; min edge %.3f m; max edge %.3f m; "
          "min lambda_2 %.3f; steps with an edge > R_comm: %d"
          % (RHO_INTRUDER, on, off, sim["err"][kp], sim["t"][kp], t_rec,
             dint_all.min(), sim["lmin"].min(), sim["lmax"].max(),
             sim["lam2"].min(), int(np.sum([r[6] for r in rows]))))
    kend = int(round(19.0 / 0.02))
    print("avoidance: e_F at t=19 s %.4f; edges at nominal: side 2, "
          "diagonal %.3f" % (sim["err"][kend], 2.0 * np.sqrt(2.0)))


if __name__ == "__main__":
    consensus_figure()
    square_figure()
    leader_figure()
    avoidance_figure()
