"""Adversarial tests for scripts.cross_script (Track B: Linear A<->B alignment).

These tests pin the four properties the expert audit demanded, plus the
method-correctness guards for each alignment method:

  1. Procrustes W is genuinely orthogonal (SVD-based, W^T W = I) -- and it
     recovers a KNOWN rotation on aligned data.
  2. The held-out-shared-sign split is GENUINELY held-out: anchors in the test
     fold never reach ``fit`` (no leakage of B-side labels into the alignment).
  3. The pipeline is deterministic for a fixed seed (per_split array identical).
  4. A sanity case: when A and B embeddings are perfectly aligned (B = A @ Q^T),
     held-out bootstrap recovery is ~1.0 -- proving the harness can register a
     real signal (the null on the real corpus is therefore a real null, not a
     broken test).

Plus: CCA degeneracy clamp, Sinkhorn plan is row-stochastic/non-negative, PPMI
is non-negative/finite, and the uniform-random alignment lands at ~1/|B|
through the same harness (negative control).

Run:
    pytest tests/test_cross_script.py -v
"""
import os
import sys

import numpy as np
import pytest

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from scripts.cross_script import align_methods as AM  # noqa: E402
from scripts.cross_script import embeddings as EMB  # noqa: E402
from scripts.cross_script import validate as V  # noqa: E402


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #

def _l2norm(X):
    n = np.linalg.norm(X, axis=1, keepdims=True)
    n[n == 0] = 1.0
    return X / n


def _rand_problem(n=60, d=24, seed=0):
    """Two unrelated L2-normalised embedding spaces + an identity anchor join."""
    rng = np.random.default_rng(seed)
    EA = _l2norm(rng.normal(size=(n, d)))
    EB = _l2norm(rng.normal(size=(n, d)))
    vocabA = {f"a{i}": i for i in range(n)}
    vocabB = {f"b{i}": i for i in range(n)}
    anchors = [(f"a{i}", f"b{i}") for i in range(n)]
    return EA, vocabA, EB, vocabB, anchors


def _aligned_problem(n=60, d=24, seed=0, noise=0.0):
    """B = A @ Q^T (+ optional noise) -> Procrustes MUST recover ~all anchors."""
    rng = np.random.default_rng(seed)
    EA = _l2norm(rng.normal(size=(n, d)))
    G = rng.normal(size=(d, d))
    Q, _ = np.linalg.qr(G)            # orthogonal rotation
    EB = _l2norm(EA @ Q.T + noise * rng.normal(size=(n, d)))
    vocabA = {f"a{i}": i for i in range(n)}
    vocabB = {f"b{i}": i for i in range(n)}
    anchors = [(f"a{i}", f"b{i}") for i in range(n)]
    return EA, vocabA, EB, vocabB, anchors


# --------------------------------------------------------------------------- #
# 1. Procrustes is orthogonal + recovers a known rotation
# --------------------------------------------------------------------------- #

class TestProcrustesOrthogonal:
    def test_W_is_orthogonal_square(self):
        EA, _, EB, _, anchors = _rand_problem()
        m = AM.Procrustes()
        m.fit(EA, EB, [(i, i) for i in range(44)])
        W = m.W
        assert W.shape == (EA.shape[1], EB.shape[1])
        # the load-bearing claim: W^T W = I to numerical precision
        assert np.allclose(W.T @ W, np.eye(W.shape[1]), atol=1e-10)
        assert np.allclose(W @ W.T, np.eye(W.shape[0]), atol=1e-10)

    def test_W_recoveries_known_rotation(self):
        # B = A @ Q^T  =>  learned W must equal Q (up to sign per axis)
        EA, _, _, _, _ = _rand_problem(seed=11)
        rng = np.random.default_rng(99)
        G = rng.normal(size=(EA.shape[1], EA.shape[1]))
        Q, _ = np.linalg.qr(G)
        EB = _l2norm(EA @ Q.T)
        m = AM.Procrustes()
        m.fit(EA, EB, [(i, i) for i in range(EA.shape[0])])
        # W and Q agree as rotations: mapped EA must reconstruct EB direction
        mapped = (EA - EA.mean(0)) @ m.W.T
        cos = (mapped * (EB - EB.mean(0))).sum(1) / (
            np.linalg.norm(mapped, axis=1) * np.linalg.norm(EB - EB.mean(0), axis=1) + 1e-12
        )
        assert cos.mean() > 0.999   # near-perfect directional recovery


# --------------------------------------------------------------------------- #
# 2. Held-out split is genuinely held-out (no leakage into fit)
# --------------------------------------------------------------------------- #

class TestHeldOutNoLeakage:
    def test_fit_never_sees_held_out_pairs(self):
        """Instrument .fit; assert no held-out anchor pair is ever passed to it."""
        EA, vocabA, EB, vocabB, anchors = _rand_problem()
        seen = []

        class Spy(AM.Procrustes):
            def fit(self, EA_, EB_, pairs):
                seen.extend(pairs)
                return super().fit(EA_, EB_, pairs)

        V.bootstrap_recovery(
            lambda s: Spy(), EA, vocabA, EB, vocabB, anchors,
            n_splits=1, held_frac=0.2, seed=0,
        )
        invA = {i: t for t, i in vocabA.items()}
        invB = {i: t for t, i in vocabB.items()}
        # reconstruct the exact held-out fold validate.py produced (seed=0, splits=1)
        vrng = np.random.default_rng(0)
        perm = vrng.permutation(len(anchors))
        n_hold = max(1, int(round(len(anchors) * 0.2)))
        held = {(invA[vocabA[anchors[perm[i]][0]]], invB[vocabB[anchors[perm[i]][1]]])
                for i in range(n_hold)}
        fit = {(invA[a], invB[b]) for (a, b) in seen}
        assert held.isdisjoint(fit), "held-out anchor leaked into fit()"

    def test_split_construction_is_disjoint_by_design(self):
        """hold = perm[:n_hold]; train = perm[n_hold:] -- verify disjoint indices."""
        n = 55
        for seed in range(5):
            rng = np.random.default_rng(seed)
            perm = rng.permutation(n)
            n_hold = max(1, int(round(n * 0.2)))
            hold = set(perm[:n_hold].tolist())
            train = set(perm[n_hold:].tolist())
            assert hold.isdisjoint(train)
            assert len(train) + len(hold) == n

    def test_held_out_neighbours_searched_over_all_b(self):
        """A hit must beat ALL B signs, not just held-out anchors (strict MUSE)."""
        EA, vocabA, EB, vocabB, anchors = _rand_problem(n=40, d=16)
        r = V.bootstrap_recovery(
            lambda s: AM.Procrustes(), EA, vocabA, EB, vocabB, anchors,
            n_splits=1, held_frac=0.2, seed=0,
        )
        # argmax is over EB.shape[0] candidates -> chance floor is 1/nB
        assert r["nB"] == EB.shape[0]
        assert abs(r["chance_analytic"] - 1.0 / EB.shape[0]) < 1e-12


# --------------------------------------------------------------------------- #
# 3. Determinism
# --------------------------------------------------------------------------- #

class TestDeterminism:
    def test_same_seed_identical_per_split(self):
        EA, vocabA, EB, vocabB, anchors = _rand_problem()
        fac = lambda s: AM.Procrustes()
        r1 = V.bootstrap_recovery(fac, EA, vocabA, EB, vocabB, anchors, n_splits=30, seed=42)
        r2 = V.bootstrap_recovery(fac, EA, vocabA, EB, vocabB, anchors, n_splits=30, seed=42)
        assert np.array_equal(r1["per_split"], r2["per_split"])
        assert r1["mean"] == r2["mean"]

    def test_embedding_is_deterministic(self):
        seqs = [["a", "b", "c", "d"]] * 6 + [["a", "b", "e"]] * 4
        _, E1 = EMB.embed(seqs, d=12, seed=7)
        _, E2 = EMB.embed(seqs, d=12, seed=7)
        assert np.array_equal(E1, E2)


# --------------------------------------------------------------------------- #
# 4. Sanity: perfectly-aligned embeddings recover ~100%
# --------------------------------------------------------------------------- #

class TestPerfectAlignmentSanity:
    def test_perfect_alignment_recovers_all(self):
        EA, vocabA, EB, vocabB, anchors = _aligned_problem(seed=1)
        r = V.bootstrap_recovery(
            lambda s: AM.Procrustes(), EA, vocabA, EB, vocabB, anchors,
            n_splits=50, held_frac=0.2, seed=0,
        )
        assert r["mean"] == pytest.approx(1.0, abs=1e-9)
        assert r["ci_lo"] >= 1.0 - 1e-9     # every split perfect

    def test_perfect_alignment_loo_recovers_all(self):
        EA, vocabA, EB, vocabB, anchors = _aligned_problem(seed=2)
        idx = [(vocabA[a], vocabB[b]) for (a, b) in anchors]
        hits = 0
        for h in range(len(idx)):
            tr = [idx[i] for i in range(len(idx)) if i != h]
            m = AM.Procrustes(); m.fit(EA, EB, tr)
            S = m.similarity(EA, EB)
            hits += int(np.argmax(S[idx[h][0]]) == idx[h][1])
        assert hits == len(idx)


# --------------------------------------------------------------------------- #
# Method-correctness guards (CCA / Sinkhorn / PPMI / chance floor)
# --------------------------------------------------------------------------- #

class TestMethodGuards:
    def test_cca_n_components_clamped_below_n_pairs(self):
        """Few pairs, high d -> n_components must not exceed n_pairs-1 (degeneracy)."""
        rng = np.random.default_rng(0)
        X = rng.normal(size=(5, 24)); Y = rng.normal(size=(5, 24))
        m = AM.CCAAlign()
        m.fit(X, Y, [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)])
        assert m.cca.n_components <= 4
        Xc, Yc = m.cca.transform(X, Y)
        assert Xc.shape == Yc.shape

    def test_sinkhorn_plan_is_row_stochastic_and_nonneg(self):
        rng = np.random.default_rng(0)
        EA = _l2norm(rng.normal(size=(40, 16))); EB = _l2norm(rng.normal(size=(40, 16)))
        fa = rng.uniform(1, 5, size=40); fb = rng.uniform(1, 5, size=40)
        m = AM.SinkhornOT(fa, fb)
        m.fit(EA, EB, [(i, i) for i in range(30)])
        T = m.similarity(EA, EB)
        assert T.shape == (40, 40)
        assert (T >= 0).all()
        assert np.allclose(T.sum(axis=1), 1.0, atol=1e-6)

    def test_isorank_similarity_finite_and_nonneg(self):
        rng = np.random.default_rng(0)
        adj = np.abs(rng.normal(size=(10, 10))); adj = (adj + adj.T) / 2
        m = AM.GraphIsoRank(adj, adj, alpha=0.7, iters=20)
        m.fit(np.zeros((10, 4)), np.zeros((10, 4)), [(0, 0), (1, 1)])
        R = m.similarity(np.zeros((10, 4)), np.zeros((10, 4)))
        assert np.all(np.isfinite(R))
        assert R.min() >= 0.0

    def test_ppmi_nonnegative_and_finite(self):
        rng = np.random.default_rng(0)
        C = rng.uniform(0, 10, size=(12, 12))
        P = EMB.ppmi(C, cds=0.75, k=1)
        assert np.all(np.isfinite(P))
        assert (P >= 0).all()

    def test_random_align_lands_at_chance(self):
        """The uniform-random alignment through the harness reads ~1/|B|."""
        EA, vocabA, EB, vocabB, anchors = _rand_problem(n=50, d=16)
        r = V.bootstrap_recovery(
            lambda s: V.RandomAlign(seed=s), EA, vocabA, EB, vocabB, anchors,
            n_splits=200, held_frac=0.2, seed=3,
        )
        # empirical mean within a loose window of the analytic floor 1/nB
        assert abs(r["mean"] - r["chance_analytic"]) < 0.03


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
