#!/usr/bin/env python3
"""run_ab.py -- Track B orchestrator: cross-script Linear A <-> B phonetic
imputation, validated by held-out-shared-sign recovery.

Pipeline
--------
  1. load A/B sequences + build the A<->B bridge (data.py -- the load-bearing join)
  2. PPMI+SVD embeddings for both scripts at d in {16,24,32} (embeddings.py)
  3. five alignment methods + a uniform-random chance floor (align_methods.py)
  4. bootstrap held-out recovery, 200 splits, train on 80% of the 55 anchors only
     (validate.py -- the falsifiable crux)
  5. ONLY IF the best method beats chance (lower CI > chance): impute the A-only
     signs under it, each with bootstrap stability + nearest-neighbour margin.
     Otherwise: report the bet is not yet supported + recommend the DĀMOS request.

Honest ceiling stated throughout: this is an Etruscan-grade readout (some phonetic
shape of some signs), NOT a decipherment of Minoan.  A and B write different
languages; sign-co-occurrence geometries are not guaranteed to be isomorphic.

References: Mikolov, Le, Sutskever 2013; Conneau et al. 2017 (MUSE);
Bouchard-Cote et al. 2013 (cognate-based, NOT used here).
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)

from scripts.cross_script import data as D
from scripts.cross_script import embeddings as EMB
from scripts.cross_script import align_methods as AM
from scripts.cross_script import validate as V

SEED = 20260630
N_SPLITS = 200
HELD_FRAC = 0.2
DIMS = (16, 24, 32)


def _adjacency(seqs, vocab):
    """Symmetric sign-sign co-occurrence adjacency (window 2) for IsoRank."""
    return EMB.cooccurrence(seqs, vocab, window=2)


def _freq_vec(seqs, vocab):
    fv = np.zeros(len(vocab))
    for s in seqs:
        for t in s:
            if t in vocab:
                fv[vocab[t]] += 1
    return fv


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--splits", type=int, default=N_SPLITS)
    ap.add_argument("--out", default=os.path.join(HERE, "results_ab.json"))
    args = ap.parse_args()

    print("=" * 72)
    print("TRACK B -- cross-script Linear A <-> B phonetic imputation")
    print("Etruscan-grade ceiling. NOT a decipherment of Minoan.")
    print("=" * 72)

    # ---- 1. data + bridge ----
    a_inv, a_seqs, a_freq = D.load_a()
    b_seqs, b_freq, v2g = D.load_b()
    anchor_ab, a_only = D.build_anchor_set(a_freq, b_freq)
    anchors = [(t, t) for t in anchor_ab]  # A-token == B-value (the bridge)
    print(f"\n[data] A: {len(a_seqs)} signstrings, {sum(a_freq.values())} tokens, "
          f"{len(a_freq)} distinct")
    print(f"[data] B: {len(b_seqs)} signstrings, {sum(b_freq.values())} tokens, "
          f"{len(b_freq)} distinct")
    print(f"[data] ANCHORS (shared, both sides embedded): {len(anchors)}")
    print(f"[data] A-side AB signs with NO B-counterpart in cog: {sorted(set(t for t in a_inv if not t.startswith('*')) - set(anchor_ab))}")
    print(f"[data] A-only imputation targets (conservative stream): {len(a_only)} "
          f"(ontology tags 72 syllabogram-Aonly; 33 reach the flat stream, "
          f"{len(a_only)} have per-inscription context here)")

    # ---- 2. embeddings (d-sweep) ----
    print(f"\n[embed] PPMI+SVD at d in {DIMS} ...")
    A_emb = EMB.embed_many(a_seqs, dims=DIMS, seed=SEED)
    B_emb = EMB.embed_many(b_seqs, dims=DIMS, seed=SEED)

    # ---- 3. d-sweep on Procrustes (pick the dim that recovers best) ----
    print("\n[dsweep] Procrustes held-out recovery by embedding dim:")
    sweep = {}
    for d in DIMS:
        vocabA, EA = A_emb[d]
        vocabB, EB = B_emb[d]
        r = V.bootstrap_recovery(
            lambda s: AM.Procrustes(),
            EA, vocabA, EB, vocabB, anchors,
            n_splits=args.splits, held_frac=HELD_FRAC, seed=SEED,
        )
        sweep[d] = r
        print(f"   d={d:2d}: mean={r['mean']:.3f}  CI=[{r['ci_lo']:.3f},{r['ci_hi']:.3f}]"
              f"  chance={r['chance_analytic']:.3f}")
    best_d = max(sweep, key=lambda d: sweep[d]["mean"])
    print(f"[dsweep] best dim = {best_d}")

    vocabA, EA = A_emb[best_d]
    vocabB, EB = B_emb[best_d]
    A_adj = _adjacency(a_seqs, vocabA)
    B_adj = _adjacency(b_seqs, vocabB)
    fa = _freq_vec(a_seqs, vocabA)
    fb = _freq_vec(b_seqs, vocabB)

    # ---- 4. all methods + chance ----
    factories = {
        "freq_position":  lambda s: AM.FreqPosition(a_seqs, b_seqs, vocabA, vocabB),
        "graph_isorank":  lambda s: AM.GraphIsoRank(A_adj, B_adj),
        "cca":            lambda s: AM.CCAAlign(),
        "procrustes":     lambda s: AM.Procrustes(),
        "sinkhorn_ot":    lambda s: AM.SinkhornOT(fa, fb),
        "random_chance":  lambda s: V.RandomAlign(seed=s),
    }

    print(f"\n[validate] held-out recovery, {args.splits} splits, "
          f"train on {int(round(len(anchors)*(1-HELD_FRAC)))}/55 anchors, "
          f"hold out {int(round(len(anchors)*HELD_FRAC))}:")
    print(f"{'method':16s} {'mean':>7s} {'ci_lo':>7s} {'ci_hi':>7s} "
          f"{'chance':>7s} {'>chance?':>9s}")
    results = {}
    for name, fac in factories.items():
        r = V.bootstrap_recovery(
            fac, EA, vocabA, EB, vocabB, anchors,
            n_splits=args.splits, held_frac=HELD_FRAC, seed=SEED,
        )
        r["method"] = name
        results[name] = r
        above = r["ci_lo"] > r["chance_analytic"]
        print(f"{name:16s} {r['mean']:7.3f} {r['ci_lo']:7.3f} {r['ci_hi']:7.3f} "
              f"{r['chance_analytic']:7.3f} {'YES' if above else 'no':>9s}")

    # best non-chance method
    real = {k: v for k, v in results.items() if k != "random_chance"}
    best_name = max(real, key=lambda k: real[k]["mean"])
    best = real[best_name]
    chance = results["random_chance"]
    print(f"\n[best] {best_name}: mean={best['mean']:.3f} CI=[{best['ci_lo']:.3f},{best['ci_hi']:.3f}]"
          f"  vs chance(mean)={chance['mean']:.3f} (analytic 1/{best['nB']}={best['chance_analytic']:.3f})")

    # ---- 4b. harness validity: positive + negative control, and LOO ----
    print("\n[controls] harness validity (is the null real, or a broken test?):")
    controls = {}
    # positive: synthetic isomorphism (rotated+noisy copy of B-embeddings) -> must recover ~1
    rngc = np.random.default_rng(1)
    Gc = rngc.normal(size=(EA.shape[1], EA.shape[1])); Qc, _ = np.linalg.qr(Gc)
    EA_ctrl = np.zeros_like(EA)
    invA = {i: t for t, i in vocabA.items()}
    anchor_set = set(anchor_ab)
    for t in anchor_ab:
        EA_ctrl[vocabA[t]] = EB[vocabB[t]] @ Qc.T + 0.10 * rngc.normal(size=EA.shape[1])
    for i in range(EA.shape[0]):
        if invA[i] not in anchor_set and np.all(EA_ctrl[i] == 0):
            EA_ctrl[i] = rngc.normal(size=EA.shape[1])
    EA_ctrl /= np.linalg.norm(EA_ctrl, axis=1, keepdims=True).clip(min=1e-9)
    rc = V.bootstrap_recovery(lambda s: AM.Procrustes(), EA_ctrl, vocabA, EB, vocabB,
                              anchors, n_splits=min(args.splits, 100), held_frac=HELD_FRAC, seed=11)
    controls["positive_control_procrustes"] = {k: rc[k] for k in ("mean", "ci_lo", "ci_hi")}
    # negative: shuffle the anchor join -> must read ~chance
    shuf = list(anchor_ab); rngc2 = np.random.default_rng(2); rngc2.shuffle(shuf)
    anchors_shuf = list(zip(anchor_ab, shuf))
    rn = V.bootstrap_recovery(lambda s: AM.Procrustes(), EA, vocabA, EB, vocabB,
                              anchors_shuf, n_splits=min(args.splits, 100), held_frac=HELD_FRAC, seed=12)
    controls["negative_control_shuffled_join"] = {k: rn[k] for k in ("mean", "ci_lo", "ci_hi")}
    print(f"   positive (synthetic isomorphism): {rc['mean']:.3f} "
          f"CI=[{rc['ci_lo']:.3f},{rc['ci_hi']:.3f}]  (harness works iff ~1)")
    print(f"   negative (shuffled join):         {rn['mean']:.3f} "
          f"CI=[{rn['ci_lo']:.3f},{rn['ci_hi']:.3f}]  (chance iff ~{rc['chance_analytic']:.3f})")

    # LOO: finest resolution, hold out 1 of 55 each fold
    print("\n[loo] leave-one-out over all 55 anchors (finest resolution):")
    idx_pairs = [(vocabA[a], vocabB[b]) for a, b in anchors]
    loo = {}
    for lname, lfac in (("procrustes", lambda s: AM.Procrustes()),
                        ("freq_position", lambda s: AM.FreqPosition(a_seqs, b_seqs, vocabA, vocabB)),
                        ("sinkhorn_ot", lambda s: AM.SinkhornOT(
                            np.ones(len(vocabA)), np.ones(len(vocabB))))):
        hits = 0
        for h in range(len(idx_pairs)):
            tr = [idx_pairs[i] for i in range(len(idx_pairs)) if i != h]
            ai, bi = idx_pairs[h]
            m = lfac(0); m.fit(EA, EB, tr); S = m.similarity(EA, EB)
            if int(np.argmax(S[ai])) == bi:
                hits += 1
        acc = hits / len(idx_pairs)
        loo[lname] = {"accuracy": acc, "hits": hits, "n": len(idx_pairs)}
        print(f"   {lname:14s} {acc:.3f}  ({hits}/{len(idx_pairs)})  chance={1/EB.shape[0]:.3f}")
    controls["loo"] = loo

    # ---- 5. impute ONLY if clearly above chance ----
    clearly_above = (best["mean"] > chance["ci_hi"]) and (best["ci_lo"] > best["chance_analytic"])
    imputed = []
    print("\n" + "=" * 72)
    if clearly_above:
        print(f"HELD-OUT RECOVERY IS ABOVE CHANCE -- imputing {len(a_only)} A-only signs")
        print(f"under best method ({best_name}); every value carries uncertainty.")
        print("=" * 72)
        fac = factories[best_name]
        imputed = V.impute_aonly(
            fac, EA, vocabA, EB, vocabB, anchors, a_only,
            a_freq=a_freq, n_splits=args.splits, seed=SEED,
        )
        invB = {i: t for t, i in vocabB.items()}
        print(f"\n{'A-only':8s} {'imputed':8s} {'glyph':4s} {'stability':>9s} "
              f"{'margin':>7s} {'a_freq':>6s}  top3")
        for r in sorted(imputed, key=lambda x: -x["stability"]):
            g = v2g.get(r["imputed_value"], "?")
            t3 = ",".join(f"{v}({p})" for v, p in r["top3"])
            print(f"{r['a_only_sign']:8s} {r['imputed_value']:8s} {g:4s} "
                  f"{r['stability']:9.3f} {r['margin_ratio_mean']:7.3f} "
                  f"{str(r['a_freq_in_corpus']):>6s}  {t3}")
    else:
        print("HELD-OUT RECOVERY IS ~ CHANCE -- the bet is NOT yet supported.")
        print("=" * 72)
        ch = best["chance_analytic"]
        nb = best["nB"]
        msg = (f"\nNo method's lower-CI clears the random-alignment chance floor "
               f"({ch:.3f} = 1/{nb}).  We do NOT impute: an imputed value without a "
               f"recoverable signal would be circular noise.")
        print(msg)
        med = sorted(a_freq[t] for t in a_only)[len(a_only) // 2]
        print("\nMost likely cause (data sufficiency):")
        print(f"  - Linear-B side is THIN: {len(b_seqs)} signstrings / {sum(b_freq.values())} tokens")
        print("    (vs DAMOS ~5500 tablets).  919 wordforms cannot anchor a stable")
        print("    distributional geometry for 69 signs.")
        print(f"  - Linear-A side: {sum(a_freq.values())} tokens; A-only signs are rare (median freq {med}).")
        print("  - STRUCTURAL: A writes Minoan, B writes Greek. Sign co-occurrence")
        print("    reflects each LANGUAGE's phonotactics; the embedding geometries are")
        print("    not guaranteed to be isomorphic, so a Procrustes rotation learned on")
        print("    ~44 anchors need not generalise to the 11 held out.")
        print("\nRecommendation: repeat with the full DAMOS Linear-B corpus (~5500")
        print("tablets) + more A-only attestations before this test can register a signal.")

    # ---- persist ----
    out = {
        "seed": SEED,
        "n_splits": args.splits,
        "held_frac": HELD_FRAC,
        "best_d": best_d,
        "data": {
            "a_signstrings": len(a_seqs),
            "a_tokens": int(sum(a_freq.values())),
            "b_signstrings": len(b_seqs),
            "b_tokens": int(sum(b_freq.values())),
            "n_anchors": len(anchors),
            "n_a_only": len(a_only),
            "anchors": anchor_ab,
            "a_not_anchored": sorted(set(t for t in a_inv if not t.startswith("*")) - set(anchor_ab)),
        },
        "dsweep_procrustes": {d: {k: v for k, v in r.items() if k != "per_split"} for d, r in sweep.items()},
        "recovery": {k: {kk: vv for kk, vv in v.items() if kk != "per_split"} for k, v in results.items()},
        "controls": controls,
        "best_method": best_name,
        "clearly_above_chance": bool(clearly_above),
        "imputed_aonly": imputed,
        "ceiling": "Etruscan-grade phonetic readout; NOT a decipherment of Minoan.",
    }
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\n[done] results -> {args.out}")


if __name__ == "__main__":
    main()
