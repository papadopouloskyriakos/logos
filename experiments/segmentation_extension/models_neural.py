#!/usr/bin/env python3
"""models_neural.py — Class 2 (PREREG §5.2): tiny supervised BiLSTM boundary model.

Regime disclosure (PREREG): SUPERVISED on the scribes' divisions of the 51 training sites,
predicting the held-out site — a cross-site-predictability probe, labeled supervised in every
table, graded against the identical random floor and bootstrap.

Pre-run corrections (PREREG Addendum A, 2026-07-03 — adversarial review BEFORE any graded run):
  - the LSTM consumes packed sequences, so pad timesteps never enter the recurrent state and
    padded-batch outputs are identical to per-stream unpadded outputs (the graded decode path);
    dev-loss early stopping and threshold selection therefore calibrate the exact predictor
    that is graded;
  - the sign vocabulary is built from the FULL train fold (dev included), per the frozen
    "vocab = train-fold signs + UNK + pad";
  - this class's training set excludes the held-out site's own inscriptions in the one
    "(unknown)" fold where the gate-verified quirk would otherwise place 2 labeled test
    streams in supervised training (unsupervised entries keep the quirk for anchor pairing).

Frozen by PREREG §5.2: embedding 16 / BiLSTM hidden 16 per direction / dropout 0.2 / head on
[h_i ; h_{i+1}] -> linear(64 -> 1); HARD cap <= 10,000 trainable parameters (asserted);
unseen test signs -> UNK; Adam lr=1e-3, weight decay 1e-4, batch 32 streams, max 200 epochs,
early stopping patience 15 on dev loss; dev = train streams with md5(iid) last hex byte
mod 10 == 0; threshold per fold maximizing dev boundary-F1 on grid 0.05..0.95 step 0.05
(default 0.5 if the dev split has no positive positions); graded seed 20260703.
"""
from __future__ import annotations

import hashlib
from typing import Dict, List, Sequence, Tuple

import numpy as np
import torch
import torch.nn as nn

from frozen_metric import Inscription, SignCodec, _prf, true_boundaries

PARAM_CAP = 10_000
EMB_DIM = 16
HIDDEN = 16
DROPOUT = 0.2
LR = 1e-3
WEIGHT_DECAY = 1e-4
BATCH = 32
MAX_EPOCHS = 200
PATIENCE = 15
THRESH_GRID = [round(0.05 * k, 2) for k in range(1, 20)]      # 0.05 .. 0.95


def _is_dev(iid: str) -> bool:
    return int(hashlib.md5(iid.encode("utf-8")).hexdigest()[-2:], 16) % 10 == 0


class TinyBiLSTM(nn.Module):
    def __init__(self, vocab_size: int):
        super().__init__()
        self.emb = nn.Embedding(vocab_size, EMB_DIM, padding_idx=0)
        self.lstm = nn.LSTM(EMB_DIM, HIDDEN, num_layers=1, batch_first=True, bidirectional=True)
        self.drop = nn.Dropout(DROPOUT)
        self.head = nn.Linear(4 * HIDDEN, 1)

    def forward(self, x: torch.Tensor, lengths: torch.Tensor) -> torch.Tensor:
        # packed recurrence: pad timesteps never enter the LSTM state, so a stream's real-position
        # states are identical whether it is batched (training/dev) or decoded solo (grading)
        packed = nn.utils.rnn.pack_padded_sequence(self.emb(x), lengths, batch_first=True,
                                                   enforce_sorted=False)
        out, _ = self.lstm(packed)
        h, _ = nn.utils.rnn.pad_packed_sequence(out, batch_first=True, total_length=x.shape[1])
        pair = torch.cat([h[:, :-1, :], h[:, 1:, :]], dim=-1)  # boundary after sign i: [h_i; h_{i+1}]
        return self.head(self.drop(pair)).squeeze(-1)          # (B, L-1) logits at positions 1..L-1


def _encode(streams: Sequence[str], vocab: Dict[str, int], max_len: int) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """(ids, target, mask): ids (B, max_len) padded with 0; target/mask (B, max_len-1)."""
    B = len(streams)
    ids = torch.zeros((B, max_len), dtype=torch.long)
    tgt = torch.zeros((B, max_len - 1), dtype=torch.float32)
    msk = torch.zeros((B, max_len - 1), dtype=torch.float32)
    return ids, tgt, msk


def _build_batch(items: Sequence[Tuple[str, List[int]]], vocab: Dict[str, int]):
    max_len = max(len(s) for s, _ in items)
    ids, tgt, msk = _encode([s for s, _ in items], vocab, max_len)
    for k, (s, bnds) in enumerate(items):
        for i, ch in enumerate(s):
            ids[k, i] = vocab.get(ch, 1)                       # 1 = UNK
        bset = set(bnds)
        for p in range(1, len(s)):                             # boundary position p -> index p-1
            tgt[k, p - 1] = 1.0 if p in bset else 0.0
            msk[k, p - 1] = 1.0
    lens = torch.tensor([len(s) for s, _ in items], dtype=torch.int64)
    return ids, tgt, msk, lens


class NeuralBoundarySegmenter:
    """Trained per fold; .boundaries(stream) matches the frozen-metric interface."""

    def __init__(self, train: Sequence[Inscription], codec: SignCodec, seed: int):
        torch.manual_seed(seed)
        np.random.seed(seed % (2 ** 32))
        torch.set_num_threads(1)
        self.seed = seed

        items_all = []
        for ins in train:
            stream = codec.enc_word(ins.signs)
            if len(stream) < 2:
                continue
            tb, _ = true_boundaries(ins.words)
            items_all.append((ins.iid, stream, tb))
        dev = [(s, b) for iid, s, b in items_all if _is_dev(iid)]
        tr = [(s, b) for iid, s, b in items_all if not _is_dev(iid)]
        if not tr:                                             # degenerate; train on everything
            tr, dev = dev, []

        chars = sorted({ch for _, s, _ in items_all for ch in s})  # FULL train fold (PREREG §5.2)
        self.vocab = {ch: i + 2 for i, ch in enumerate(chars)}  # 0=pad, 1=UNK
        self.model = TinyBiLSTM(len(self.vocab) + 2)
        n_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        assert n_params <= PARAM_CAP, f"parameter cap violated: {n_params} > {PARAM_CAP}"
        self.n_params = n_params

        opt = torch.optim.Adam(self.model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)
        lossf = nn.BCEWithLogitsLoss(reduction="none")
        order = np.random.default_rng(seed).permutation(len(tr))
        batches = [[tr[i] for i in order[k:k + BATCH]] for k in range(0, len(tr), BATCH)]
        enc_batches = [_build_batch(b, self.vocab) for b in batches]
        enc_dev = _build_batch(dev, self.vocab) if dev else None

        best_dev, best_state, patience = float("inf"), None, 0
        for _epoch in range(MAX_EPOCHS):
            self.model.train()
            for ids, tgt, msk, lens in enc_batches:
                opt.zero_grad()
                logits = self.model(ids, lens)
                loss = (lossf(logits, tgt) * msk).sum() / msk.sum().clamp(min=1.0)
                loss.backward()
                opt.step()
            if enc_dev is None:
                continue
            self.model.eval()
            with torch.no_grad():
                ids, tgt, msk, lens = enc_dev
                dev_loss = float((lossf(self.model(ids, lens), tgt) * msk).sum() / msk.sum().clamp(min=1.0))
            if dev_loss < best_dev - 1e-5:
                best_dev, patience = dev_loss, 0
                best_state = {k: v.clone() for k, v in self.model.state_dict().items()}
            else:
                patience += 1
                if patience >= PATIENCE:
                    break
        if best_state is not None:
            self.model.load_state_dict(best_state)
        self.model.eval()

        self.threshold = 0.5
        if dev:
            with torch.no_grad():
                ids, tgt, msk, lens = enc_dev
                probs = torch.sigmoid(self.model(ids, lens))
            if float((tgt * msk).sum()) > 0:
                best_f1, best_t = -1.0, 0.5
                for t in THRESH_GRID:
                    pred = (probs >= t).float() * msk
                    tp = float((pred * tgt).sum())
                    fp = float((pred * (1 - tgt) * msk).sum())
                    fn = float(((1 - pred) * tgt * msk).sum())
                    prec = tp / (tp + fp) if (tp + fp) else 0.0
                    rec = tp / (tp + fn) if (tp + fn) else 0.0
                    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
                    if f1 > best_f1:
                        best_f1, best_t = f1, t
                self.threshold = best_t
        self.n_train_streams, self.n_dev_streams = len(tr), len(dev)

    def boundaries(self, stream: str) -> List[int]:
        n = len(stream)
        if n < 2:
            return []
        ids = torch.tensor([[self.vocab.get(ch, 1) for ch in stream]], dtype=torch.long)
        with torch.no_grad():
            probs = torch.sigmoid(self.model(ids, torch.tensor([n], dtype=torch.int64)))[0]
        return [p for p in range(1, n) if float(probs[p - 1]) >= self.threshold]
