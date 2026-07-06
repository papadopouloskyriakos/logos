#!/usr/bin/env python3
"""Skeleton-collision hold-out (prereg §11, red-team MAJOR).

"Zero Cretan data" was only a LABEL predicate; leakage here is by SKELETON overlap. This removes from the
frozen calibration corpus every record whose Egyptian OR foreign skeleton is within Levenshtein ≤1 of any
Cretan target skeleton, upgrading the guarantee to "zero target-skeleton information ever entered training".

Exclusion predicate (stated, deterministic):
  drop record r  iff  min_t Levenshtein(f(r.egy), t) ≤ 1  OR  min_t Levenshtein(f(r.cons), t) ≤ 1
  where t ranges over the f()-skeletons of every target's Edel oval AND Linear B form.

Writes the held-out corpus (gitignored, licensed) + a committable manifest with counts and the new sha.
Score-blind: touches no model.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import skeleton as sk

EXP = os.path.normpath(os.path.join(HERE, "..", ".."))
CORPUS = os.path.join(EXP, "data", "gold", "egyptian_calibration_handverified.jsonl")
HELDOUT = os.path.join(EXP, "data", "gold", "egyptian_calibration_heldout.jsonl")
TARGETS = os.path.join(EXP, "frozen", "cretan_confirmatory_targets.json")
MANIFEST = os.path.join(EXP, "frozen", "corpus_holdout_manifest.json")


def target_skeletons():
    d = json.load(open(TARGETS, encoding="utf-8"))
    items = list(d["targets"]) + [d["secondary_robustness_anchor"]]
    sks = set()
    for t in items:
        sks.add(sk.f(t["edel_transliteration"]))
        sks.add(sk.f(t["linear_b"]))
    return sorted(sks)


def collides(rec, tsk):
    for field in ("egy", "cons"):
        s = sk.f(rec.get(field, ""))
        for t in tsk:
            if sk.levenshtein(s, t) <= 1:
                return True, field, sk.f_str(rec.get(field, ""))
    return False, None, None


def run():
    tsk = target_skeletons()
    recs = [json.loads(l) for l in open(CORPUS, encoding="utf-8")]
    kept, dropped = [], []
    for r in recs:
        hit, field, s = collides(r, tsk)
        (dropped if hit else kept).append((r, field, s))
    with open(HELDOUT, "w", encoding="utf-8") as fh:
        for r, _, _ in kept:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    new_sha = hashlib.sha256(open(HELDOUT, "rb").read()).hexdigest()
    manifest = {
        "artifact": "corpus_skeleton_collision_holdout",
        "predicate": "drop record iff min_t Lev(f(egy),t)<=1 OR min_t Lev(f(cons),t)<=1; t over all target Edel-oval and LB f()-skeletons",
        "target_skeletons": ["-".join(t) for t in tsk],
        "n_input": len(recs), "n_dropped": len(dropped), "n_kept": len(kept),
        "dropped_records": [{"id": r.get("id"), "field": field, "skeleton": s} for r, field, s in dropped],
        "input_corpus_sha256_16": hashlib.sha256(open(CORPUS, "rb").read()).hexdigest()[:16],
        "heldout_corpus_file": "data/gold/egyptian_calibration_heldout.jsonl (gitignored)",
        "heldout_corpus_sha256": new_sha,
        "heldout_corpus_sha256_16": new_sha[:16],
    }
    json.dump(manifest, open(MANIFEST, "w"), ensure_ascii=False, indent=1)
    print(f"targets: {[m for m in manifest['target_skeletons']]}")
    print(f"input {len(recs)} -> kept {len(kept)}, dropped {len(dropped)}")
    for r, field, s in dropped:
        print(f"  DROP {r.get('id')}: {field} skeleton {s}")
    print(f"heldout sha256_16: {new_sha[:16]}")
    return manifest


if __name__ == "__main__":
    run()
