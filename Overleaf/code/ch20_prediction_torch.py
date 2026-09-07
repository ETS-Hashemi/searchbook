#!/usr/bin/env python3
"""PyTorch version of the sequence-to-sequence trajectory predictor of
Chapter 20 (code/ch20_prediction.py), for experiments on real data.

It uses the same conventions as the NumPy implementation: the inputs are
the observed displacements in the agent-centred frame divided by SCALE, the
decoder predicts the residual over the mean observed displacement, and each
decoder step outputs the mean and log-std of the next displacement.  The
decoder is fed its own mean (free running) so that training and prediction
use the same rollout.  Not executed by the self-test of the chapter.

    pip install torch
    python3 ch20_prediction_torch.py     # trains on the synthetic data set
"""
import numpy as np
import torch
import torch.nn as nn

from ch20_prediction import (SCALE, T_PRED, ade, from_frame, generate_dataset,
                             prepare_sequences)


class Seq2SeqLSTM(nn.Module):
    """Encoder LSTM over the observed displacements, decoder LSTMCell that
    rolls the future out one step at a time (mean and log-std per step)."""

    def __init__(self, n_hidden=32):
        super().__init__()
        self.encoder = nn.LSTM(2, n_hidden, batch_first=True)
        self.decoder = nn.LSTMCell(2, n_hidden)
        self.readout = nn.Linear(n_hidden, 4)        # mu_x, mu_y, log s_x, log s_y

    def forward(self, x, horizon=T_PRED):
        _, (h, c) = self.encoder(x)                  # h, c: (1, B, n_hidden)
        h, c = h[0], c[0]
        base = x.mean(dim=1)                         # constant-velocity residual
        u, outs = x[:, -1], []
        for _ in range(horizon):
            h, c = self.decoder(u, (h, c))
            out = self.readout(h)
            mu = out[:, :2] + base
            outs.append(torch.cat([mu, out[:, 2:]], dim=1))
            u = mu                                   # feed the mean back
        return torch.stack(outs, dim=1)              # (B, horizon, 4)


def gaussian_nll(out, y):
    """Negative log-likelihood of the displacements y under N(mu, diag(s^2))."""
    mu, log_s = out[..., :2], out[..., 2:]
    return (log_s + 0.5 * ((y - mu) * torch.exp(-log_s)) ** 2).sum(-1).mean()


def train(model, x, y, x_val, val, epochs=40, lr=5e-3, batch_size=64, patience=10):
    """Adam with a geometric learning-rate decay and early stopping on the
    validation ADE (in metres, free-running rollout)."""
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    sched = torch.optim.lr_scheduler.ExponentialLR(opt, gamma=(0.1) ** (1.0 / max(1, epochs - 1)))
    origin, R = val_frame = val[1]
    best, best_state, bad = float("inf"), None, 0
    for epoch in range(epochs):
        model.train()
        perm = torch.randperm(x.shape[0])
        for start in range(0, x.shape[0], batch_size):
            idx = perm[start:start + batch_size]
            loss = gaussian_nll(model(x[idx]), y[idx])
            opt.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            opt.step()
        sched.step()
        model.eval()
        with torch.no_grad():
            pos = torch.cumsum(model(x_val)[..., :2], dim=1).numpy() * SCALE
        val_ade = ade(from_frame(pos, origin, R), val[0]["future"])
        print("epoch %3d  loss %.4f  val ADE %.3f m" % (epoch + 1, loss.item(), val_ade))
        if val_ade < best - 1e-4:
            best, bad = val_ade, 0
            best_state = {k: v.clone() for k, v in model.state_dict().items()}
        else:
            bad += 1
            if bad >= patience:
                break
    model.load_state_dict(best_state)
    return best


if __name__ == "__main__":
    torch.manual_seed(0)
    rng = np.random.default_rng(20)
    train_set, val_set = generate_dataset(1600, rng), generate_dataset(400, rng)
    x_tr, y_tr, _ = prepare_sequences(train_set)
    x_va, _, frame = prepare_sequences(val_set)
    model = Seq2SeqLSTM(32)
    best = train(model, torch.tensor(x_tr, dtype=torch.float32), torch.tensor(y_tr, dtype=torch.float32),
                 torch.tensor(x_va, dtype=torch.float32), (val_set, frame))
    print("best validation ADE %.3f m" % best)
