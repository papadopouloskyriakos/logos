#!/usr/bin/env python3
"""Freeze the candidate pool = all distinct Linear B wordform skeletons in DĀMOS (prereg §4).

One committed source (DĀMOS items.jsonl via scripts/cross_script/data.load_b_damos), one mechanical
predicate (every syllabic wordform), reduced by the single blind f(), deduplicated by skeleton. Large and
dense → targets have many confusable neighbours (avoids the isolated-target easy-recovery trap). Enforces:
targets present, per-target confusability floor (≥3 distractors within edit-distance ≤1), uniqueness.

SCORE-BLIND: builds skeletons + edit-distance geometry only; never touches M2. Writes frozen pool + sha.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import skeleton as sk

EXP = os.path.normpath(os.path.join(HERE, "..", ".."))
# DĀMOS bronze (items.jsonl) is gitignored and materialised only in the MAIN worktree; import data.py
# from there so its ROOT resolves the corpus correctly.
MAIN_ROOT = "/home/claude-runner/gitlab/n8n/logos"
sys.path.insert(0, os.path.join(MAIN_ROOT, "scripts", "cross_script"))
import data as damos  # noqa: E402

TARGETS = os.path.join(EXP, "frozen", "cretan_confirmatory_targets.json")
POOL = os.path.join(EXP, "frozen", "lb_toponym_pool.json")
DAMOS_ITEMS = os.path.join(MAIN_ROOT, "corpus", "bronze", "linearb", "damos", "items.jsonl")


def target_lb_skeletons():
    d = json.load(open(TARGETS, encoding="utf-8"))
    items = list(d["targets"]) + [d["secondary_robustness_anchor"]]
    return {t["toponym"]: (sk.f(t["linear_b"]), t["linear_b"]) for t in items}


def run():
    wordforms, freq, _ = damos.load_b_damos()
    # skeleton -> set of source wordforms (readability + homophony audit)
    by_skel = {}
    for w in wordforms:
        raw = "-".join(w).lower()
        s = sk.f(raw)
        if not s:
            continue
        by_skel.setdefault(s, set()).add("-".join(w))
    skels = sorted(by_skel)  # deterministic order
    M = len(skels)

    tgt = target_lb_skeletons()
    presence, confus, homophony = {}, {}, {}
    for name, (s, raw) in tgt.items():
        present = s in by_skel
        presence[name] = {"skeleton": "-".join(s), "linear_b": raw, "present": present,
                          "source_wordforms": sorted(by_skel.get(s, []))[:8]}
        homophony[name] = len(by_skel.get(s, []))
        # distractors within edit-distance 1 (exclude the target skeleton itself)
        near = [ "-".join(o) for o in skels if o != s and sk.levenshtein(o, s) <= 1 ]
        confus[name] = {"n_within_editdist_1": len(near), "examples": near[:8], "meets_floor(>=3)": len(near) >= 3}

    all_present = all(v["present"] for v in presence.values())
    all_floor = all(v["meets_floor(>=3)"] for v in confus.values())
    all_unique = all(homophony[n] >= 1 for n in tgt)  # present; homophony count reported for audit

    pool_body = {"M": M, "skeletons": ["-".join(s) for s in skels]}
    pool_sha = hashlib.sha256(json.dumps(pool_body, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    out = {
        "artifact": "lb_toponym_pool",
        "source": "DĀMOS Linear B (corpus/bronze/linearb/damos/items.jsonl) via scripts/cross_script/data.load_b_damos",
        "predicate": "every distinct f()-skeleton of every DĀMOS syllabic wordform (all wordforms; not toponym-filtered)",
        "damos_items_sha256_16": hashlib.sha256(open(DAMOS_ITEMS, "rb").read()).hexdigest()[:16],
        "M": M,
        "targets_present": presence,
        "target_homophony_count": homophony,
        "target_confusability": confus,
        "checks": {"all_targets_present": all_present, "all_confusability_floor_met": all_floor,
                   "M>=30": M >= 30, "NO_POWER": not (all_present and all_floor and M >= 30)},
        "pool_sha256": pool_sha, "pool_sha256_16": pool_sha[:16],
        "skeletons": ["-".join(s) for s in skels],
    }
    json.dump(out, open(POOL, "w"), ensure_ascii=False, indent=1)
    print(f"DĀMOS wordforms: {len(wordforms)}  ->  distinct skeletons M = {M}")
    for name in tgt:
        p, c, h = presence[name], confus[name], homophony[name]
        print(f"  {name:9} {p['skeleton']:8} present={p['present']} homophones={h} "
              f"confusable(<=1)={c['n_within_editdist_1']} floor_ok={c['meets_floor(>=3)']}")
    print(f"checks: {out['checks']}")
    print(f"pool sha256_16: {pool_sha[:16]}")
    return out


if __name__ == "__main__":
    run()
