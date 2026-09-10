"""Generate the data files of the trajectory-prediction experiment of
Chapter 20 (figures/data/ch20-*.dat) from code/ch20_prediction.py.

Everything is produced by ``run_experiment`` with its fixed seed, so the
numbers quoted in the chapter, the table and the figures agree.  Files:

    ch20-results.dat          ADE_h / FDE_h per horizon step h for every
                              method on the whole test split (ade_<m>,
                              fde_<m>) and the ADE_h of the tuned CV and of
                              LSTM-NLL per subset (ade_cv_<subset>,
                              ade_nll_<subset>)
    ch20-training-nll.dat     epoch, train loss and validation ADE of the
                              free-running LSTM-NLL; ch20-training-tf.dat the
                              same for the teacher-forced LSTM-TF
    ch20-training-cv.dat      the ADE of the tuned CV baseline on the *same
                              validation split*, as two points spanning the
                              epoch axis, so that the reference line of
                              fig:ch20-training uses no test-set number
    ch20-baselines-obs.dat    the observed points of the turning example
    ch20-baselines-pred.dat   its ground truth and the CV / CA / KF
                              predictions (row t=0 is the last observation)
    ch20-baselines-ellipses.dat  95% ellipses of the KF at h = 4, 8, 12
    ch20-example-obs.dat, ch20-example-pred.dat, ch20-example-ellipses.dat,
    ch20-example-samples.dat  the same for the evasive example, with the
                              LSTM-NLL mean, its 95% ellipses (LSTM: e*,
                              KF: k*) and 20 sampled rollouts
    ch20-attention.dat        toy attention weights across four agents
    ch20-attention-agents.dat their positions and velocities

Run from Overleaf/:   python3 code/figures/gen_ch20_results.py
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from ch20_prediction import (DT, SUBSETS, T_OBS, T_PRED, TOY_AGENTS_POS,  # noqa: E402
                             TOY_AGENTS_VEL, ade, agent_frame, covariance_ellipse,
                             displacement_errors, lstm_cell_example, predict_cv,
                             print_results, run_experiment, subset_mask,
                             to_frame, toy_agent_attention)

DATA = os.path.join(os.path.dirname(HERE), "..", "figures", "data")
SHORT = {"CV (k=1)": "cv1", "CV (tuned)": "cv", "CA (tuned)": "ca", "KF (tuned)": "kf",
         "LSTM-NLL": "nll", "LSTM-MSE": "mse", "LSTM-abs": "abs", "LSTM-TF": "tf",
         "Transformer": "tr"}
SUBSET_SHORT = {"all": "all", "straight": "straight", "turn": "turn",
                "evasive_visible": "evis", "evasive_hidden": "ehid"}
ELLIPSE_STEPS = (4, 8, 12)


def write_table(name, columns, rows, fmt="%.4f"):
    """Write a whitespace-separated table with a header row."""
    path = os.path.join(DATA, name)
    with open(path, "w") as f:
        f.write(" ".join(columns) + "\n")
        for row in rows:
            f.write(" ".join(("%d" % v) if isinstance(v, (int, np.integer)) else (fmt % v)
                             for v in row) + "\n")
    print("wrote", os.path.normpath(path))


def with_origin(last_obs, pred):
    """Prepend the last observed position so that plotted lines connect."""
    return np.concatenate([last_obs[None], pred], axis=0)


def ellipse_columns(prefix, means, covs, transform=None):
    """Columns <prefix><h>x, <prefix><h>y of the 95% ellipses at ELLIPSE_STEPS;
    ``transform`` optionally maps the (48, 2) points into another frame."""
    cols, arrays = [], []
    for h in ELLIPSE_STEPS:
        pts = covariance_ellipse(means[h - 1], covs[h - 1], p=0.95, n_points=48)
        if transform is not None:
            pts = transform(pts)
        cols += ["%s%dx" % (prefix, h), "%s%dy" % (prefix, h)]
        arrays += [pts[:, 0], pts[:, 1]]
    return cols, np.stack(arrays, axis=1)


def median_example(test, pred, subset):
    """Index of the trajectory of ``subset`` whose final error of ``pred`` is
    the median of the subset: a typical, not a hand-picked, example."""
    idx = np.where(subset_mask(test, subset))[0]
    final = displacement_errors(pred[idx], test["future"][idx])[:, -1]
    return int(idx[np.argsort(final)[len(idx) // 2]])


def main():
    res = run_experiment(verbose=True)
    print_results(res)
    test, preds, metrics = res["test"], res["preds"], res["metrics"]

    # -- 1. per-horizon metrics -------------------------------------------------
    cols = ["h", "t"]
    arrays = [np.arange(1, T_PRED + 1), np.arange(1, T_PRED + 1) * DT]
    for name, short in SHORT.items():
        ade_h, fde_h = metrics[name]["all"]
        cols += ["ade_" + short, "fde_" + short]
        arrays += [ade_h, fde_h]
    for name, short in (("CV (tuned)", "cv"), ("LSTM-NLL", "nll")):
        for subset in SUBSETS[1:]:
            cols.append("ade_%s_%s" % (short, SUBSET_SHORT[subset]))
            arrays.append(metrics[name][subset][0])
    write_table("ch20-results.dat", cols, np.stack(arrays, axis=1))

    # -- 2. training curves -----------------------------------------------------
    for name, fname in (("LSTM-NLL", "ch20-training-nll.dat"), ("LSTM-TF", "ch20-training-tf.dat")):
        hist = res["histories"][name]
        n = len(hist["train_loss"])
        write_table(fname, ["epoch", "train_loss", "val_ade"],
                    np.stack([np.arange(1, n + 1), hist["train_loss"], hist["val_ade"]], axis=1))
        print("%s: best epoch %d, %d epochs run" % (name, hist["best_epoch"], n))
    n_max = max(len(res["histories"][m]["train_loss"]) for m in ("LSTM-NLL", "LSTM-TF"))
    val, k_cv = res["val"], res["settings"]["k_cv"]
    cv_val_ade = float(ade(predict_cv(val["obs"], k=k_cv), val["future"]))
    write_table("ch20-training-cv.dat", ["epoch", "ade"],
                [(0, cv_val_ade), (n_max + 1, cv_val_ade)])
    print("tuned CV (k=%d) ADE on the validation split: %.4f m" % (k_cv, cv_val_ade))

    # -- 3. the turning example for the baseline figure --------------------------
    #    (the turn with the median final error of LSTM-NLL: a typical case)
    turn = median_example(test, preds["LSTM-NLL"], "turn")
    last = test["obs"][turn, -1]
    steps = np.arange(0, T_PRED + 1)
    #    plotted in the agent frame of the example (origin = last observation,
    #    observed heading along +x) so that the figure is wide, not tall
    origin, rot = agent_frame(test["obs"][turn:turn + 1])

    def turn_frame(points):
        return to_frame(points[None], origin, rot)[0]

    write_table("ch20-baselines-obs.dat", ["t", "x", "y"],
                np.column_stack([np.arange(T_OBS), turn_frame(test["obs"][turn])]))
    cols = ["t", "x_gt", "y_gt", "x_cv1", "y_cv1", "x_cv", "y_cv", "x_ca", "y_ca", "x_kf", "y_kf"]
    arrays = [steps, turn_frame(with_origin(test["clean"][turn, T_OBS - 1], test["future"][turn]))]
    for name in ("CV (k=1)", "CV (tuned)", "CA (tuned)", "KF (tuned)"):
        arrays.append(turn_frame(with_origin(last, preds[name][turn])))
    write_table("ch20-baselines-pred.dat", cols, np.column_stack(arrays))
    ecols, epts = ellipse_columns("k", preds["KF (tuned)"][turn], res["covs"]["KF (tuned)"],
                                  transform=turn_frame)
    write_table("ch20-baselines-ellipses.dat", ecols, epts)
    speed = np.linalg.norm(test["clean"][turn, 1] - test["clean"][turn, 0]) / DT
    print("turning example: test index %d, rate %.3f rad/s, speed %.2f m/s" % (turn, test["rate"][turn], speed))
    print("  observed positions:", np.round(test["obs"][turn], 2).tolist())
    for name in ("CV (k=1)", "CV (tuned)", "CA (tuned)", "KF (tuned)", "LSTM-NLL"):
        err = displacement_errors(preds[name][turn], test["future"][turn])
        print("  %-11s error at h=4/8/12: %.2f %.2f %.2f m" % (name, err[3], err[7], err[11]))

    # -- 4. the evasive example for the LSTM figure ------------------------------
    #    (the visible maneuver with the median final error of LSTM-NLL)
    ev = median_example(test, preds["LSTM-NLL"], "evasive_visible")
    last = test["obs"][ev, -1]
    write_table("ch20-example-obs.dat", ["t", "x", "y"],
                np.column_stack([np.arange(T_OBS), test["obs"][ev]]))
    cols = ["t", "x_gt", "y_gt", "x_cv", "y_cv", "x_kf", "y_kf", "x_nll", "y_nll", "x_mse", "y_mse"]
    arrays = [steps, with_origin(test["clean"][ev, T_OBS - 1], test["future"][ev])]
    for name in ("CV (tuned)", "KF (tuned)", "LSTM-NLL", "LSTM-MSE"):
        arrays.append(with_origin(last, preds[name][ev]))
    write_table("ch20-example-pred.dat", cols, np.column_stack(arrays))
    ecols, epts = ellipse_columns("e", preds["LSTM-NLL"][ev], res["covs"]["LSTM-NLL"][ev])
    kcols, kpts = ellipse_columns("k", preds["KF (tuned)"][ev], res["covs"]["KF (tuned)"])
    write_table("ch20-example-ellipses.dat", ecols + kcols, np.concatenate([epts, kpts], axis=1))
    samples = res["samples"][ev]                                  # (20, T_PRED, 2)
    cols, arrays = ["t"], [steps]
    for j in range(samples.shape[0]):
        cols += ["s%dx" % (j + 1), "s%dy" % (j + 1)]
        arrays.append(with_origin(last, samples[j]))
    write_table("ch20-example-samples.dat", cols, np.column_stack(arrays))
    heading = np.diff(test["clean"][ev], axis=0)
    turning = np.abs(np.diff(np.arctan2(heading[:, 1], heading[:, 0]))) > 0.05
    speed = np.linalg.norm(test["clean"][ev, 1] - test["clean"][ev, 0]) / DT
    print("evasive example: test index %d, onset %d, rate %.3f rad/s, speed %.2f m/s, turning steps %s"
          % (ev, test["onset"][ev], test["rate"][ev], speed, np.where(turning)[0] + 1))
    print("  step   err CV   err KF   err LSTM   sigma_x  sigma_y (LSTM, world frame)")
    e_cv = displacement_errors(preds["CV (tuned)"][ev], test["future"][ev])
    e_kf = displacement_errors(preds["KF (tuned)"][ev], test["future"][ev])
    e_nn = displacement_errors(preds["LSTM-NLL"][ev], test["future"][ev])
    sig = np.sqrt(np.linalg.eigvalsh(res["covs"]["LSTM-NLL"][ev]))       # (T, 2) ascending
    for h in range(T_PRED):
        print("  %4d   %6.2f   %6.2f   %8.2f   %7.3f  %7.3f" % (h + 1, e_cv[h], e_kf[h], e_nn[h], sig[h, 1], sig[h, 0]))

    # -- 5. toy attention across agents -----------------------------------------
    w, _ = toy_agent_attention(TOY_AGENTS_POS, TOY_AGENTS_VEL)
    rows = [(i, j, w[i, j]) for i in range(len(w)) for j in range(len(w))]
    write_table("ch20-attention.dat", ["i", "j", "w"], rows)
    write_table("ch20-attention-agents.dat", ["agent", "x", "y", "vx", "vy"],
                np.column_stack([np.arange(len(w)), TOY_AGENTS_POS, TOY_AGENTS_VEL]))
    print("attention weights (row = query agent):")
    for i in range(len(w)):
        print("  " + " ".join("%.3f" % v for v in w[i]))

    # -- 6. the LSTM cell example -----------------------------------------------
    ex = lstm_cell_example()
    print("LSTM cell example:")
    for key in ("x", "h_prev", "c_prev", "a", "f", "i", "o", "g", "c", "tanh_c", "h"):
        print("  %-7s %s" % (key, " ".join("%8.4f" % v for v in np.atleast_1d(ex[key]))))


if __name__ == "__main__":
    main()
