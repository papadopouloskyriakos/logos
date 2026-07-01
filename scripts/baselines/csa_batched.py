#!/usr/bin/env python3
"""csa_batched.py — batched-parallel CUDA energy for Tamburini's CSA (task #21).

His ``CoupledAnnealer`` evaluates the 16 coupled annealers' energies either sequentially
(``__update_state_no_par``) or across a 16-process CPU ``mp.Pool`` (``__update_state``). The Pool
forks CUDA tensors and dies (``Cannot re-initialize CUDA in forked subprocess``), so the CUDA path
is stuck in slow serial: per step it fires ``16 × N_lost`` tiny ``editdistance1N`` kernels, each
dominated by launch + host↔device transfer overhead, leaving an H100 ~1 % utilised.

But the only GPU work is his per-lost-word edit distance, and the annealers and their lost words are
independent. This module batches ALL of them into ONE edit-distance kernel per step:

  * :func:`batch_energy` computes energies for a LIST of states in a single GPU batch. It reuses his
    EXACT CPU logic — ``State2Assignment``, the ``expandWord`` rewriting, ``lsa_2g``, and the two
    penalties — and replaces only the edit-distance calls: every rewritten query word across every
    state is stacked and scored against the known lexicon with one tiled pairwise ``editdistance``
    call. That primitive is verified bit-identical to his ``editdistance1N`` (tiled-pairwise ==
    1×N, max abs diff 0.0), so ``batch_energy(prob,[s...]) == [prob.energy(s) for s in ...]`` exactly.

  * :func:`install_batched` monkeypatches the annealer's serial ``no_par`` update to build the 16
    probes (consuming RNG in his exact ``worker_probe`` order) and then batch-evaluate their
    energies. The probe sequence and the energies are bit-identical to serial, so the whole
    annealing is unchanged — only the wall clock differs (one big batched kernel that saturates the
    GPU instead of thousands of microscopic sequential launches).

His vendored files are UNTOUCHED (his reproduction is preserved); batching is opt-in.
"""
from __future__ import annotations

import random
import types
from typing import List, Sequence

import numpy as np
import torch

from EditDistanceWild import editdistance  # pairwise batched kernel  # noqa: E402


def _expand_words(prob, state):
    """Replicate his energy() query-building EXACTLY: return (queries, lGroupsW, P).

    ``queries`` is the ordered list of rewritten lost words (each a maxLl-padded token list), in the
    same group→word→expansion order his energy() appends to ``costM``; ``lGroupsW`` is the per-group
    expansion count; ``P`` is the State→Assignment. Mirrors CSA_OptMatcher.Problem.energy lines
    151-188 with the per-word editdistance call removed.
    """
    P = prob.State2Assignment(state)
    idx = getattr(prob, "_lC_idx", None)
    if idx is None:
        idx = {c: i for i, c in enumerate(prob.lC)}         # O(1) sign→index (his .index() is O(n))
        prob._lC_idx = idx

    def expand(w, i, l):
        if i == len(w):
            yield l
        else:
            if w[i] in prob.fix:
                for j in range(len(w[i])):
                    yield from expand(w, i + 1, l + [ord(x) for x in prob.fix[w[i]][j]])
            else:
                ci = idx[w[i]]
                if P[ci] != -1:
                    for j in range(len(P[ci])):
                        yield from expand(w, i + 1, l + [ord(x) for x in prob.kC[P[ci][j]]])
                else:
                    yield from expand(w, i + 1, l)          # DEL char assigned to -1

    queries: List[List[int]] = []
    lGroupsW: List[int] = []
    j = 0
    for lG in range(len(prob.lGroups)):
        nel = 0
        for _ in range(prob.lGroups[lG]):
            for ww in expand(prob.lLex[j], 0, []):
                queries.append((ww + [0] * prob.maxLl)[:prob.maxLl])
                nel += 1
            j += 1
        lGroupsW.append(nel)
    return queries, np.array(lGroupsW), P


def _dist_matrix(prob, queries, max_pairs: int = 0) -> np.ndarray:
    """Edit-distance matrix [M × N] of ``queries`` vs prob.y, via tiled pairwise ``editdistance``.

    Chunked over query rows to bound the kernel's per-call scratch (his kernel ``cudaMalloc``s an
    O(pairs · (srcLen+1)(trgLen+1)) working buffer AND cudaFrees it every call, so FEWER, BIGGER
    chunks are much faster on a large GPU). ``max_pairs`` defaults to a memory-adaptive value that
    targets ~8 GB of scratch from the actual (maxLl, maxLk) so the H100 does the whole matrix in a
    handful of launches instead of dozens. One kernel launch per chunk — vs his one per query word.
    """
    N = int(prob.y.shape[0])
    M = len(queries)
    out = np.empty((M, N), dtype=np.float32)               # match his editdistance1N pred dtype exactly
    if M == 0:
        return out
    X = torch.tensor(queries, dtype=torch.long).to(prob.device)     # [M, maxLl]
    Y = prob.y                                                       # [N, maxLk] on device
    if max_pairs <= 0:
        cell_bytes = (int(X.shape[1]) + 1) * (int(Y.shape[1]) + 1) * 4   # his workingM per pair
        budget = 8 * 1024**3 if prob.device != "cpu" else 64 * 1024**2   # ~8 GB GPU / 64 MB CPU
        max_pairs = max(N, budget // max(cell_bytes, 1))
    rows = max(1, max_pairs // max(N, 1))
    for c in range(0, M, rows):
        Xc = X[c:c + rows]
        mc = int(Xc.shape[0])
        src = Xc.repeat_interleave(N, dim=0)                         # [mc*N, maxLl]
        trg = Y.repeat(mc, 1)                                        # [mc*N, maxLk]
        d = editdistance(src, trg, 0, prob.ED[0], prob.ED[1])[:, 1].reshape(mc, N)
        out[c:c + mc] = d.to("cpu").numpy()
        del src, trg, d
    return out


def batch_energy(prob, states: Sequence, max_pairs: int = 0) -> List[float]:
    """Energies for a list of states, batching all edit-distance work into one kernel per chunk.

    Bit-identical to ``[prob.energy(s) for s in states]`` — reuses his expandWord/lsa_2g/penalties;
    only the GPU edit distance is batched. (His per-eval stdout print is skipped: it changes no value
    and is itself a large serial overhead.)
    """
    from lsa_2g import lsa_2g                                        # his Hungarian-with-groups

    built = [_expand_words(prob, s) for s in states]
    offsets, all_q = [], []
    for queries, _lgw, _P in built:
        offsets.append((len(all_q), len(all_q) + len(queries)))
        all_q.extend(queries)
    D = _dist_matrix(prob, all_q, max_pairs=max_pairs)              # [total_queries × N]

    energies: List[float] = []
    for (s0, s1), (_queries, lGroupsW, P) in zip(offsets, built):
        costM = D[s0:s1, :]
        _row, _col, out = lsa_2g(costM, lGroupsW, prob.kGroups)
        if prob.M > 1:                                               # penalty: multiple assignments
            lPM = sum(1 if ((lP != -1) and (len(lP) > 1)) else 0 for lP in P)
            out = out + prob.penF * lPM
        lPN = sum(1 if (lP == -1) else 0 for lP in P)               # penalty: unassigned lost signs
        out = out + prob.penF * lPN
        energies.append(out)
    return energies


def install_batched(annealer, max_pairs: int = 0) -> None:
    """Monkeypatch the annealer's serial ``no_par`` update to batch the 16 probes' energies.

    anneal() dispatches to ``__update_state_no_par`` when ``processes <= 1``; we replace that bound
    method. The probes are built in his exact ``worker_probe`` order (same RNG draws), then scored in
    one batch — so the annealing trajectory is identical to serial, only faster. Requires
    ``processes <= 1`` (set by the caller) so anneal() actually takes this path.
    """
    prob = annealer.target_function.__self__                        # bound prob.energy → the Problem

    def _batched_update(self):
        # Mirror his worker_probe loop EXACTLY. Critical: his move() mutates the state IN PLACE and
        # returns the same object, and the 16 annealers can share one state object (initial_state is
        # [init]*n). Serial captures each energy immediately after its move; we defer to a batch, so
        # we must SNAPSHOT each probe (list(probe)) before the next move mutates the shared object.
        # probe_states are stored with his exact aliasing (the moved reference), so __step sees the
        # identical objects it would under serial.
        snaps = []
        for i in range(self.m):
            state = self.current_states[i]
            if random.random() < self.qa:
                probe = self.probe_function(state, self.tgen, qa=True)
            else:
                probe = self.probe_function(state, self.tgen, qa=False)
            snaps.append(list(probe))                       # snapshot for the batched energy eval
            self.probe_states[i] = probe                    # exactly as his worker_probe stores it
        energies = batch_energy(prob, snaps, max_pairs=max_pairs)
        for i in range(self.m):
            self.probe_energies[i] = energies[i]

    annealer._CoupledAnnealer__update_state_no_par = types.MethodType(_batched_update, annealer)
