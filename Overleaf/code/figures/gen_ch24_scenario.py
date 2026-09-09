"""Generate the data files and TikZ figures of Chapter 24 from the worked
scenario of ch24_hybrid.py (deterministic, seed 24 inside that file).

    figures/data/ch24-timeline.dat  per control cycle: t, sepA, sepB, sepC
                                    (distance of each drone to the intruder),
                                    dmate (smallest distance between two
                                    drones), eF (formation error), driftA,
                                    driftC (distance from the plan), avA, avC
                                    (1 while Avoiding), rpA, rpC (1 while
                                    Reconnecting or Replanning), conn (1 if
                                    the communication graph is connected)
    figures/data/ch24-horizon.dat   the trigger profile of drone A one
                                    cycle before the trigger (t = 3.4 s) and
                                    at the trigger (t = 3.5 s): s, sepa, thra,
                                    sepb, thrb (predicted separation and the
                                    threshold R_safe + kappa sigma(s))
    figures/ch24/scenario.tex       six frames of the worked scenario
    figures/ch24/recheck.tex        the conflict re-check after C's
                                    reconnection: before/after the local CBS

The printed numbers are the ones quoted in the chapter.
Run from Overleaf/:   python3 code/figures/gen_ch24_scenario.py
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import ch24_hybrid as H  # noqa: E402

ROOT = os.path.join(os.path.dirname(HERE), "..")
DATA = os.path.join(ROOT, "figures", "data")
FIGS = os.path.join(ROOT, "figures", "ch24")
os.makedirs(DATA, exist_ok=True)
os.makedirs(FIGS, exist_ok=True)

COL = {"A": "sbAgentA", "B": "sbAgentB", "C": "sbAgentC"}
NODE = {"A": "sbagentA", "B": "sbagentB", "C": "sbagentC"}


def write_dat(name, header, rows):
    path = os.path.join(DATA, name)
    with open(path, "w") as f:
        f.write(header + "\n")
        for row in rows:
            f.write(" ".join("%.4f" % v for v in row) + "\n")
    print("wrote", os.path.relpath(path, ROOT), "(%d rows)" % len(rows))


def write_tex(name, lines):
    path = os.path.join(FIGS, name)
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("wrote", os.path.relpath(path, ROOT), "(%d lines)" % len(lines))


def snap_at(sim, t):
    return min(range(len(sim.history)), key=lambda i: abs(sim.history[i]["t"] - t))


def pts(coords):
    return " -- ".join("(%.2f,%.2f)" % (x, y) for x, y in coords)


def cell_path(path):
    return [(x + 0.5, y + 0.5) for x, y in path]


# ------------------------------------------------------------------
# 1. Run the scenario
# ------------------------------------------------------------------
sim = H.worked_example(verbose=False)
p = sim.p
hist = sim.history
names = sim.names
R_infl = lambda cov: p["r_intruder"] + p["kappa"] * H.sigma_max(cov)  # noqa: E731

# ------------------------------------------------------------------
# 2. Timeline data
# ------------------------------------------------------------------
rows = []
for h in hist:
    st = h["state"]
    dm = min(np.linalg.norm(h["pos"][i] - h["pos"][j])
             for i in range(3) for j in range(i + 1, 3))
    rows.append([h["t"], h["sep"][0], h["sep"][1], h["sep"][2], dm, h["e_form"],
                 h["drift"][0], h["drift"][2],
                 1.0 if st[0] == H.AVOIDING else 0.0, 1.0 if st[2] == H.AVOIDING else 0.0,
                 1.0 if st[0] in (H.RECONNECTING, H.REPLANNING) else 0.0,
                 1.0 if st[2] in (H.RECONNECTING, H.REPLANNING) else 0.0,
                 1.0 if h["connected"] else 0.0])
write_dat("ch24-timeline.dat", "t sepA sepB sepC dmate eF driftA driftC avA avC rpA rpC conn", rows)

# ------------------------------------------------------------------
# 3. Trigger profile of A one cycle before and at the trigger
# ------------------------------------------------------------------
t_trig = next(t for (t, n, a, b, r) in sim.log if n == "A" and b == H.AVOIDING)
ia, ib = snap_at(sim, t_trig - H.DT), snap_at(sim, t_trig)
pa, pb = hist[ia]["profiles"]["A"], hist[ib]["profiles"]["A"]
rows = []
for i, s in enumerate(pa[0]):
    rows.append([s, pa[1][i], sim.R_safe + pa[2][i], pb[1][i], sim.R_safe + pb[2][i]])
write_dat("ch24-horizon.dat", "s sepa thra sepb thrb", rows)
print("trigger of A at t=%.1f: at s=%.1f sep=%.2f, kappa*sigma=%.2f, R_safe=%.2f, margin=%.2f"
      % (t_trig, pb[0][-1], pb[1][-1], pb[2][-1], sim.R_safe, pb[1][-1] - pb[2][-1] - sim.R_safe))
print("  one cycle earlier (t=%.1f): sep=%.2f, kappa*sigma=%.2f, margin=%.2f"
      % (t_trig - H.DT, pa[1][-1], pa[2][-1], pa[1][-1] - pa[2][-1] - sim.R_safe))
print("  sigma_max of the prediction at s=0,1,2,3 s: %s"
      % ", ".join("%.2f" % (pb[2][i] / p["kappa"]) for i in (0, 10, 20, 30)))
print("  intruder true position at the trigger: %s, estimate %s, est. velocity %s"
      % (np.round(hist[ib]["intruder"], 2), np.round(hist[ib]["est"], 2),
         np.round(hist[ib]["est_v"], 2)))
print("  filter covariance at the trigger: sigma_p^2=%.4f, sigma_pv=%.4f, sigma_v^2=%.4f"
      % (hist[ib]["est_P"][0, 0], hist[ib]["est_P"][0, 2], hist[ib]["est_P"][2, 2]))
_P, _q = hist[ib]["est_P"], H.PARAMS["q_kf"] * sim.tracker.dt   # effective intensity
print("  extrapolated position variance at s=0,1,2,3: %s (velocity term %s)"
      % (", ".join("%.4f" % (_P[0, 0] + 2 * s * _P[0, 2] + s * s * _P[2, 2] + _q * s ** 3 / 3.0)
                   for s in (0, 1, 2, 3)),
         ", ".join("%.4f" % (s * s * _P[2, 2]) for s in (0, 1, 2, 3))))

# ------------------------------------------------------------------
# 4. The six frames of the scenario
# ------------------------------------------------------------------
W, Hh = sim.grid.cols, sim.grid.rows
GAP = 1.4


def frame(out, i, x0, y0, title, extra=()):
    h = hist[i]
    t = h["t"]
    out.append("\\begin{scope}[shift={(%.2f,%.2f)}]" % (x0, y0))
    out.append("\\drawgrid{%d}{%d}" % (W, Hh))
    for (x, y) in sorted(sim.grid.obstacles):
        out.append("\\gridobstacle{%d}{%d}" % (x, y))
    for k, n in enumerate(names):                       # nominal paths, thin
        out.append("\\draw[%s!45,thin] %s;" % (COL[n], pts(cell_path(sim.nominal[k]))))
    out.extend(extra)
    for k, n in enumerate(names):                       # flown trajectories
        traj = [hist[j]["pos"][k] for j in range(0, i + 1)]
        if len(traj) > 1:
            out.append("\\draw[%s,line width=1.1pt] %s;" % (COL[n], pts(traj)))
    intr = [hist[j]["intruder"] for j in range(0, i + 1)]
    if len(intr) > 1:
        out.append("\\draw[sbIntruder,line width=1.1pt] %s;" % pts(intr))
    for k, n in enumerate(names):
        out.append("\\node[%s] at (%.2f,%.2f) {%s};" % (NODE[n], h["pos"][k][0], h["pos"][k][1], n))
    out.append("\\node[sbintruder] at (%.2f,%.2f) {};" % (h["intruder"][0], h["intruder"][1]))
    for k, n in enumerate(names):
        g = sim.drones[k].goal
        out.append("\\node[sbgoal,minimum size=6pt,inner sep=0pt] at (%.1f,%.1f) {};" % (g[0] + 0.5, g[1] + 0.5))
    out.append("\\node[sbannot,anchor=south west,inner sep=1pt] at (0,%.1f) {%s};" % (Hh + 0.1, title))
    out.append("\\end{scope}")


def prediction_extra(i, horizon_s=3.0):
    pred = hist[i]["pred"]
    if pred is None:
        return []
    means, covs = pred
    n = int(round(horizon_s / H.DT))
    ex = ["\\draw[sbIntruder,dashed] %s;" % pts([means[j] for j in range(0, n + 1)])]
    for j in (10, 20, 30):
        r = R_infl(covs[j])
        ex.append("\\draw[sbIntruder,dashed,fill=sbIntruder,fill opacity=0.08] (%.2f,%.2f) circle (%.2f);"
                  % (means[j][0], means[j][1], r))
    return ex


out = ["% Six frames of the worked scenario of Chapter 24 (generated by",
       "% code/figures/gen_ch24_scenario.py from ch24_hybrid.py).",
       "\\begin{tikzpicture}[x=0.31cm,y=0.31cm,font=\\scriptsize]"]
# frame 1: t = 0
frame(out, 0, 0, Hh + GAP + 1.0, "(a) $t=0$: the \\cbs plan")
# frame 2: the trigger of A
ex = prediction_extra(ib)
frame(out, ib, W + GAP, Hh + GAP + 1.0, "(b) $t=%.1f$: trigger of A" % t_trig, ex)
# frame 3: both avoiding; velocity arrows
t3 = 4.8
i3 = snap_at(sim, t3)
ex = prediction_extra(i3)
for k in (0, 2):
    v = (hist[i3 + 1]["pos"][k] - hist[i3]["pos"][k]) / H.DT
    q = hist[i3]["pos"][k]
    ex.append("\\draw[sbvec,draw=%s] (%.2f,%.2f) -- (%.2f,%.2f);" % (COL[names[k]], q[0], q[1], q[0] + 1.5 * v[0], q[1] + 1.5 * v[1]))
frame(out, i3, 2 * (W + GAP), Hh + GAP + 1.0, "(c) $t=%.1f$: A and C avoiding" % t3, ex)
# frame 4: A's failed reconnection
rc = next(e for e in sim.reconnect_log if e["drone"] == "A")
i4 = snap_at(sim, rc["t"])
ex = prediction_extra(i4)
for (k, delay, reason) in rc["tried"]:
    w = H.centre(sim.nominal[0][k])
    style = "sbGray,dotted" if reason == "too fast" else "sbRed,dashed"
    ex.append("\\draw[%s] (%.2f,%.2f) -- (%.2f,%.2f);" % (style, rc["pos"][0], rc["pos"][1], w[0], w[1]))
frame(out, i4, 0, 0, "(d) $t=%.1f$: A cannot reconnect" % rc["t"], ex)
# frame 5: the replan of A
rp = next(e for e in sim.replan_log if e["drone"] == "A")
i5 = snap_at(sim, rp["t_start"])
ex = []
for (x, y) in rp["layers"].get(rp["t_start"], []):
    ex.append("\\fill[sbRed!18] (%d,%d) rectangle ++(1,1);" % (x, y))
ex.append("\\draw[sbpathalt] %s;" % pts(cell_path(rp["path"])))
frame(out, i5, W + GAP, 0, "(e) $t=%d$: A replanned" % rp["t_start"], ex)
# frame 6: the end
i6 = len(hist) - 1
frame(out, i6, 2 * (W + GAP), 0, "(f) $t=%.0f$: goals reached" % hist[i6]["t"])
out.append("\\end{tikzpicture}")
write_tex("scenario.tex", out)
print("frames at t = 0, %.1f, %.1f, %.1f, %d, %.1f" % (t_trig, t3, rc["t"], rp["t_start"], hist[i6]["t"]))
print("A's candidates at t=%.1f: %s" % (rc["t"], rc["tried"]))
_lay = sorted(rp["layers"])
_pred = sum(len(rp["layers"][l]) for l in _lay) - 2   # minus the 2 teammate cells
print("A's replan: t_start=%d, from %s, %d blocked cells = %d predicted (%s in layers %d-%d)"
      " + 2 teammate cells, path %s"
      % (rp["t_start"], rp["c0"], rp["blocked"], _pred,
         ", ".join(str(len(rp["layers"][l]) - (2 if l == _lay[0] else 0)) for l in _lay),
         _lay[0], _lay[-1], rp["path"]))
for e in sim.replan_log:
    print("replan log: %s at t=%.1f from %s t_start=%d path %s" % (e["drone"], e["t"], e["c0"], e["t_start"], e["path"]))

# ------------------------------------------------------------------
# 5. The conflict re-check after C's reconnection (before / after)
# ------------------------------------------------------------------
rk = next(e for e in sim.recheck_log if e["repaired"])
print("re-check at t=%.1f: conflict %s, subset %s, t_start %d" % (rk["t"], rk["conflict"], rk["subset"], rk["t_start"]))


def panel(out, x0, paths, title, mark=None, t_from=5, t_to=9):
    out.append("\\begin{scope}[shift={(%.2f,0)}]" % x0)
    out.append("\\drawgrid{%d}{%d}" % (W, Hh))
    for (x, y) in sorted(sim.grid.obstacles):
        out.append("\\gridobstacle{%d}{%d}" % (x, y))
    if mark is not None:
        out.append("\\fill[sbRed!30] (%d,%d) rectangle ++(1,1);" % mark)
    for (n, path, t0) in paths:
        if n == "A":
            continue
        cells = [(H.cell_at(path, t0, t), t) for t in range(t_from, t_to + 1)]
        out.append("\\draw[%s,line width=1.1pt] %s;" % (COL[n], pts(cell_path([c for c, _ in cells]))))
        seen = {}
        for c, t in cells:
            seen.setdefault(c, []).append(t)
        for c, ts in seen.items():
            dx = -0.3 if n == "B" else 0.0
            dy = 0.32 if n == "B" else -0.32
            out.append("\\node[%s,fill=white,inner sep=0.5pt,text=%s] at (%.2f,%.2f) {%s};"
                       % ("font=\\tiny", COL[n], c[0] + 0.5 + dx, c[1] + 0.5 + dy, ",".join(str(t) for t in ts)))
    for (n, path, t0) in paths:
        if n != "A":
            c = H.cell_at(path, t0, t_from)
            out.append("\\node[%s] at (%.2f,%.2f) {%s};" % (NODE[n], c[0] + 0.5, c[1] + 0.5, n))
    out.append("\\node[sbannot,anchor=south west,inner sep=1pt] at (0,%.1f) {%s};" % (Hh + 0.1, title))
    out.append("\\end{scope}")


conf = H.first_conflict([pth for (_, pth, _) in rk["before"]], [t0 for (_, _, t0) in rk["before"]],
                        [n for (n, _, _) in rk["before"]], int(rk["t"]))
out = ["%% The conflict re-check after C's reconnection at t = %.1f s (generated by" % rk["t"],
       "% code/figures/gen_ch24_scenario.py from ch24_hybrid.py).",
       "\\begin{tikzpicture}[x=0.42cm,y=0.42cm,font=\\scriptsize]"]
panel(out, 0, rk["before"], "(a) after C's shift: $\\langle B,C,(%d,%d),%d\\rangle$" % (conf.v[0], conf.v[1], conf.t), mark=conf.v)
panel(out, W + GAP + 1.0, rk["after"], "(b) after the local \\cbs from $t=%d$" % rk["t_start"])
out.append("\\end{tikzpicture}")
write_tex("recheck.tex", out)
for (n, path, t0) in rk["before"]:
    print("  before %s t0=%d: %s" % (n, t0, [(H.cell_at(path, t0, t), t) for t in range(5, 10)]))
for (n, path, t0) in rk["after"]:
    print("  after  %s t0=%d: %s" % (n, t0, [(H.cell_at(path, t0, t), t) for t in range(5, 10)]))

# ------------------------------------------------------------------
# 6. Numbers for the text
# ------------------------------------------------------------------
print("cycles %d, end t=%.1f, detected at %.1f, min sep intruder %.2f, mates %.2f"
      % (len(hist), sim.t, sim.detected_at, sim.d_min_intruder, sim.d_min_mates))
print("min separation to the intruder per drone: %s"
      % ", ".join("%s %.2f" % (n, min(h["sep"][k] for h in hist)) for k, n in enumerate(names)))
print("max drift per drone: %s" % ", ".join("%s %.2f" % (n, max(h["drift"][k] for h in hist)) for k, n in enumerate(names)))
print("formation error: max %.2f at t=%.1f, final %.2f; connected always %s; min mate distance %.2f"
      % (max(h["e_form"] for h in hist), max(hist, key=lambda h: h["e_form"])["t"], hist[-1]["e_form"],
         all(h["connected"] for h in hist), sim.d_min_mates))
print("arrival (plan) times: %s; nominal: %s" % (
    ", ".join("%s %d" % (d.name, d.t0 + len(d.path) - 1) for d in sim.drones),
    ", ".join("%s %d" % (n, len(pth) - 1) for n, pth in zip(names, sim.nominal))))
print("time in Avoiding per drone: %s" % ", ".join(
    "%s %.1f s" % (n, H.DT * sum(1 for h in hist if h["state"][k] == H.AVOIDING)) for k, n in enumerate(names)))
print("ORCA infeasible cycles: %d; replans %s; reconnections %s" % (
    sim.orca_infeasible, [d.replans for d in sim.drones], [d.reconnections for d in sim.drones]))
link = max(max(min(np.linalg.norm(h["pos"][i] - h["pos"][j]) for j in range(3) if j != i)
                   for i in range(3)) for h in hist)
print("longest nearest-neighbour link over the run: %.2f m (R_comm %.1f, ell_act %.1f)"
      % (link, p["r_comm"], p["ell_act"]))
