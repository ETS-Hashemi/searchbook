"""Generate the data files and the worked-example figure of Chapter 21.

Scenario (code/ch21_mpc.py; deterministic, no randomness): a planar
double-integrator drone (dt = 0.1 s, a_max = 2 m/s^2 per axis,
v_max = 2 m/s) starts at the origin with velocity (1, 0) and tracks the
reference p_ref(t) = (t, 0) m at 1 m/s.  An intruder starts at (4.5, -3.0)
and moves with the constant velocity (0, 0.8) m/s; the required separation
is r_safe = 1 m.  The MPC uses N = 15, Q = diag(1, 1, 0.1, 0.1),
R = 0.1 I, the DARE terminal weight, and one linearised half-plane per
predicted intruder position.

Files written (whitespace separated, one header row):
  figures/data/ch21-example.dat        t x y vx vy ax ay ox oy sep err
  figures/data/ch21-example-marks.dat  t x y ox oy   (every full second)
  figures/data/ch21-example-plan.dat   k x y         (the plan at t = 3.0 s)
  figures/ch21/example.tex             the complete worked-example figure
  figures/data/ch21-tuning.dat         t vx5 vx10 vx20 sep1 sep10 sep100
  figures/data/ch21-experiment.dat     N rmsh seph failh rmss seps fails
                                       rmshl sephl failhl rmssl sepsl failsl
                                       (h/s = hard/soft, l = late detection
                                       at 1.2 m; otherwise full knowledge)
The summary numbers quoted in the chapter are printed to stdout.

Run from Overleaf/:   python3 code/figures/gen_ch21_mpc.py
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from ch21_mpc import (MPC, default_scenario, horizon_experiment,  # noqa: E402
                      simulate, summarise, tuning_runs)

ROOT = os.path.normpath(os.path.join(os.path.dirname(HERE), ".."))
DATA = os.path.join(ROOT, "figures", "data")
FIG = os.path.join(ROOT, "figures", "ch21")


def save(name, header, array, fmt="%.4f"):
    path = os.path.join(DATA, name)
    np.savetxt(path, np.asarray(array), fmt=fmt, header=header, comments="")
    print("wrote", os.path.relpath(path, ROOT))


EXAMPLE_TEX = r"""\begin{tikzpicture}
\begin{groupplot}[group style={group size=2 by 1, horizontal sep=1.7cm},
  font=\footnotesize, grid=major, grid style={black!12},
  legend style={font=\scriptsize, fill=white, fill opacity=0.85, text opacity=1, draw=black!30},
  legend cell align=left]
\nextgroupplot[width=7.6cm, height=7.2cm, axis equal image,
  xlabel={$x$ [m]}, ylabel={$y$ [m]}, xmin=-0.3, xmax=8.3, ymin=-3.3, ymax=3.7,
  title={(a) plane view}, legend pos=north west]
\addplot[sbGray, thick] coordinates {(0,0) (8,0)};
\addlegendentry{reference}
\addplot[sbRed, thick, dashed] table[x=ox, y=oy]{figures/data/ch21-example.dat};
\addlegendentry{intruder}
\addplot[sbBlue, line width=1.5pt] table[x=x, y=y]{figures/data/ch21-example.dat};
\addlegendentry{MPC trajectory}
\addplot[sbPurple, thick, dotted] table[x=x, y=y]{figures/data/ch21-example-plan.dat};
\addlegendentry{plan at $t=3$\,s}
\addplot[sbRed, thick, fill=sbRed, fill opacity=0.12, domain=0:360, samples=73, forget plot]
  ({%(ox)s+cos(x)}, {%(oy)s+sin(x)});
\addplot[only marks, mark=*, mark size=1.7pt, sbBlue, forget plot]
  table[x=x, y=y]{figures/data/ch21-example-marks.dat};
\addplot[only marks, mark=square*, mark size=1.7pt, sbRed, forget plot]
  table[x=ox, y=oy]{figures/data/ch21-example-marks.dat};
%(labels)s
\nextgroupplot[width=6.9cm, height=7.2cm, xlabel={time $t$ [s]}, ylabel={[m] or [m/s]},
  xmin=0, xmax=8, ymin=0, ymax=5.6, title={(b) speed, separation, error}, legend pos=north east]
\addplot[draw=none, fill=sbOrange!20, forget plot] coordinates {(%(tf)s,5.6) (%(tl)s,5.6)} \closedcycle;
\addplot[sbRed, thick] table[x=t, y=sep]{figures/data/ch21-example.dat};
\addlegendentry{separation}
\addplot[sbBlue, thick] table[x=t, y=vx]{figures/data/ch21-example.dat};
\addlegendentry{speed $v_x$}
\addplot[sbPurple, thick] table[x=t, y=err]{figures/data/ch21-example.dat};
\addlegendentry{tracking error}
\addplot[sbGray, dashed, thick] coordinates {(0,1) (8,1)};
\addlegendentry{$r_{\mathrm{safe}}=1$\,m}
\node[sbannot, anchor=south, align=center] at (axis cs:%(tmid)s, 3.4) {avoidance\\ constraint\\ active};
\end{groupplot}
\end{tikzpicture}
"""


def main():
    os.makedirs(DATA, exist_ok=True)
    os.makedirs(FIG, exist_ok=True)
    x0, ref, intr = default_scenario()
    mpc = MPC(N=15, dt=0.1)
    rec = simulate(mpc, x0, ref, intr, T=8.0)
    t, X, U = rec["t"], rec["x"], rec["u"]
    O = np.array([intr.position(ti) for ti in t])
    save("ch21-example.dat", "t x y vx vy ax ay ox oy sep err",
         np.column_stack([t, X[:, 0], X[:, 1], X[:, 2], X[:, 3], U[:, 0], U[:, 1],
                          O[:, 0], O[:, 1], rec["sep"], rec["err"]]))
    marks = [i for i in range(len(t)) if abs(t[i] - round(t[i])) < 1e-9 and 1 <= round(t[i]) <= 7]
    save("ch21-example-marks.dat", "t x y ox oy",
         np.column_stack([t[marks], X[marks, 0], X[marks, 1], O[marks, 0], O[marks, 1]]))
    i3 = int(round(3.0 / mpc.dt))
    plan = rec["pred"][i3][:, :2]
    save("ch21-example-plan.dat", "k x y",
         np.column_stack([np.arange(1, mpc.N + 1), plan[:, 0], plan[:, 1]]))
    s = summarise(rec)
    i_min = int(np.argmin(rec["sep"]))
    active = [i for i, a in enumerate(rec["active"]) if a]
    tf, tl = t[active[0]], t[active[-1]]
    labels = []
    for i in marks:
        ti = int(round(t[i]))
        if 2 <= ti <= 5:
            labels.append(r"\node[sbannot, above] at (axis cs:%.3f,%.3f) {$%d$};" % (X[i, 0], X[i, 1] + 0.05, ti))
        labels.append(r"\node[sbannot, right] at (axis cs:%.3f,%.3f) {$%d$};" % (O[i, 0] + 0.05, O[i, 1], ti))
    tex = EXAMPLE_TEX % dict(ox="%.3f" % O[i_min, 0], oy="%.3f" % O[i_min, 1],
                             labels="\n".join(labels), tf="%.1f" % tf, tl="%.1f" % (tl + mpc.dt),
                             tmid="%.2f" % (0.5 * (tf + tl + mpc.dt)))
    path = os.path.join(FIG, "example.tex")
    with open(path, "w") as fh:
        fh.write(tex)
    print("wrote", os.path.relpath(path, ROOT))
    print("worked example summary:", {k: (round(v, 4) if isinstance(v, float) else v) for k, v in s.items()})
    print("closest approach at t=%.1f: drone (%.3f, %.3f), intruder (%.3f, %.3f), sep %.4f" % (
        t[i_min], X[i_min, 0], X[i_min, 1], O[i_min, 0], O[i_min, 1], rec["sep"][i_min]))
    print("constraint active from t=%.1f to t=%.1f; multiplier max %.2f" % (tf, tl, rec["mult"].max()))

    # tuning figure: horizon (hard) and slack weight (soft)
    tr = tuning_runs()
    save("ch21-tuning.dat", "t vx5 vx10 vx20 sep1 sep10 sep100",
         np.column_stack([tr["N5"]["t"], tr["N5"]["x"][:, 2], tr["N10"]["x"][:, 2], tr["N20"]["x"][:, 2],
                          tr["w1"]["sep"], tr["w10"]["sep"], tr["w100"]["sep"]]))
    for k, r in tr.items():
        sk = summarise(r)
        print("tuning %-5s min sep %.3f rms err %.3f max err %.3f min vx %.3f max slack %.3f failures %d" % (
            k, sk["min_sep"], sk["rms_err"], sk["max_err"], r["x"][:, 2].min(), sk["max_slack"], sk["failures"]))

    # horizon experiment: full knowledge and late detection (1.2 m)
    Ns = (3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30)
    full = horizon_experiment(Ns)
    late = horizon_experiment(Ns, detect_range=1.2)
    rows = np.column_stack([full[:, :7], late[:, 1:7]])
    save("ch21-experiment.dat", "N rmsh seph failh rmss seps fails rmshl sephl failhl rmssl sepsl failsl",
         rows, fmt="%d %.4f %.4f %d %.4f %.4f %d %.4f %.4f %d %.4f %.4f %d")
    print("  N  rms_h  sep_h fail_h  rms_s  sep_s fail_s | rms_hl sep_hl fail_hl rms_sl sep_sl fail_sl")
    for r in rows:
        print("%3d %.3f %.3f %3d   %.3f %.3f %3d   | %.3f %.3f %3d    %.3f %.3f %3d" % tuple(r))


if __name__ == "__main__":
    main()
