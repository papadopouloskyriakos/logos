#!/usr/bin/env python3
"""One-shot Cretan-anchor confirmatory test (prereg cretan-anchor-oneshot-v2).

TWO entry points, deliberately separated:
  * freeze_checks()  — SCORE-BLIND. Asserts f(target_LB) is present+unique in the frozen pool, re-checks
                       the confusability floor, and reports NO_POWER. Run at FREEZE time; touches no model
                       scoring against the ovals. Safe to run before the plan_hash is minted.
  * run_oneshot()    — the actual verdict: scores M2 vs the identity baseline B_id, the generic-Egyptian
                       ablation B_egy, and the joint permutation null; applies the §7 decision rule. MUST
                       be run ONCE, AFTER the plan_hash is minted (guarded behind --run-oneshot).

Representation: both the Egyptian oval and every candidate/pool/target are reduced by the ONE blind
skeletonizer f() (skeleton.py); the frozen M2 (spec 3c56ed71, refit on the post-holdout corpus) scores
the f()-skeletons via its learned P(egy|sem) table. B_egy replaces that table with identity (each
consonant renders itself = generic Egyptian orthography); B_id is parameter-free edit distance.
"""
import argparse
import hashlib
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import model as M
import skeleton as sk

EXP = os.path.normpath(os.path.join(HERE, "..", ".."))
HELDOUT = os.path.join(EXP, "data", "gold", "egyptian_calibration_heldout.jsonl")
TARGETS = os.path.join(EXP, "frozen", "cretan_confirmatory_targets.json")
POOL = os.path.join(EXP, "frozen", "lb_toponym_pool.json")
RES = os.path.join(EXP, "results")
N_PERM = 10000            # prereg §6: joint permutation replicates
SEED = 20260706
GAP = math.log(0.05)


# ---- data / model -------------------------------------------------------------------------------
def load_heldout(tiers=("A", "B")):
    recs = [json.loads(l) for l in open(HELDOUT, encoding="utf-8")]
    recs = [r for r in recs if r["tier"] in tiers]
    for r in recs:
        r["_egy"] = M.egy_cons(r["egy"]); r["_sem"] = M.sem_cons(r["cons"])
    return recs


def fit_m2(recs):
    return M.Correspondence().fit(recs)


class IdentityCorr:
    """B_egy: generic-Egyptian orthography — each consonant renders itself; no Semitic fitting."""
    def __init__(self, hi=0.9, lo=1e-3):
        self.hi, self.lo = math.log(hi), math.log(lo)

    def score(self, egy_seq, sem_seq):
        tot = 0.0
        for s, e in M._align(sem_seq, egy_seq):
            tot += GAP if (s is None or e is None) else (self.hi if e == s else self.lo)
        return tot


def score_bid(egy_seq, sem_seq):
    """B_id: parameter-free edit-distance similarity (higher = closer)."""
    return -sk.levenshtein(egy_seq, sem_seq)


def rank_of(scorer, egy_seq, true_seq, pool):
    """Rank of true_seq among pool by scorer (desc). Ties at rank 1 => NOT recovered (rank>1)."""
    scored = [(scorer(egy_seq, cand), cand) for cand in pool]
    best = max(s for s, _ in scored)
    top = [c for s, c in scored if s == best]
    if true_seq in top and len(top) == 1:
        return 1
    # strict rank = 1 + number of candidates strictly better than true
    ts = next((s for s, c in scored if c == true_seq), None)
    if ts is None:
        return len(pool) + 1
    strictly_better = sum(1 for s, _ in scored if s > ts)
    return strictly_better + 1 + (1 if true_seq in top and len(top) > 1 else 0)  # tie at top => not rank 1


# Answer-blind, model-blind classification of each En oval by properties knowable WITHOUT the LB match
# (prereg §3), collated from Edel & Görg 2005 — (cretan, palimpsest, surviving_oval, fraglich). The
# primary set is DERIVED mechanically from these primitives, not read off the hand-set freeze_status label.
_SELECTION = {
    "Knossos":  (True,  False, True, False),   # li 10
    "Amnisos":  (True,  False, True, False),   # li 11 — the non-palimpsest occurrence
    "Lyktos":   (True,  False, True, False),   # li 12
    "Phaistos": (True,  True,  True, False),   # li 2 — recut palimpsest
    "Kydonia":  (True,  True,  True, False),   # li 3 — recut palimpsest
    "Kythera":  (False, False, True, False),   # li 8 — bridge island, not Cretan
}


def primary_anchors(tg):
    """Skeleton-blind, model-blind rule (prereg §3): Cretan AND non-palimpsest AND surviving AND not fraglich."""
    by_name = {t["toponym"]: t for t in tg["targets"]}
    picked = [n for n, (cr, pal, surv, fr) in _SELECTION.items()
              if cr and not pal and surv and not fr and n in by_name]
    assert set(picked) == {"Knossos", "Amnisos", "Lyktos"}, f"anchor selection rule drifted: {picked}"
    return [by_name[n] for n in picked]


def load_pool():
    p = json.load(open(POOL, encoding="utf-8"))
    return p, [tuple(s.split("-")) for s in p["skeletons"]]


# ---- freeze-time (blind) ------------------------------------------------------------------------
def freeze_checks():
    tg = json.load(open(TARGETS, encoding="utf-8"))
    pmeta, pool = load_pool()
    pool_set = set(pool)
    prim = primary_anchors(tg)
    checks = {"n_pool": pmeta["M"], "primary_anchors": [t["toponym"] for t in prim], "per_target": {}}
    ok = True
    for t in tg["targets"] + [tg["secondary_robustness_anchor"]]:
        lb = sk.f(t["linear_b"])
        present = lb in pool_set
        conf = pmeta["target_confusability"][t["toponym"]]["n_within_editdist_1"]
        floor = conf >= 3
        homoph = pmeta["target_homophony_count"][t["toponym"]]
        checks["per_target"][t["toponym"]] = {"lb_skeleton": sk.f_str(t["linear_b"]),
                                              "present_in_pool": present, "confusable_within_1": conf,
                                              "floor_ok": floor, "homophones": homoph}
        if t in tg["targets"] and t["freeze_status"] == "FROZEN":
            ok = ok and present and floor
    no_power = not (ok and pmeta["M"] >= 30)
    checks["NO_POWER"] = no_power
    checks["freeze_ready"] = (not no_power) and len(prim) == 3
    return checks


# ---- fail-closed integrity (prereg §15) ---------------------------------------------------------
def _sha16(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


def assert_frozen_hashes():
    """FAIL-CLOSED: every pinned artifact must match the minted plan_manifest before any scoring."""
    man = json.load(open(os.path.join(EXP, "frozen", "plan_manifest.json"), encoding="utf-8"))["pinned_sha256_16"]
    pairs = {
        "target_set": (TARGETS, man["target_set"]),
        "candidate_pool_file": (POOL, man["candidate_pool_file"]),
        "corpus_post_holdout": (HELDOUT, man["corpus_post_holdout"]),
        "model_py": (os.path.join(HERE, "model.py"), man["model_py"]),
        "skeletonizer": (os.path.join(HERE, "skeleton.py"), man["skeletonizer"]),
        "verdict_script": (os.path.join(HERE, "cretan_test.py"), man["verdict_script"]),
    }
    for name, (path, want) in pairs.items():
        got = _sha16(path)
        if got != want:
            raise SystemExit(f"FAIL-CLOSED: {name} sha {got} != pinned {want}; freeze violated, refusing to run.")


# ---- one-shot verdict (post-mint only) ----------------------------------------------------------
def run_oneshot():
    assert_frozen_hashes()                               # §15: refuse to run unless the freeze is intact
    fc = freeze_checks()                                 # §7/§10 pool-floor NO_POWER guard
    tg = json.load(open(TARGETS, encoding="utf-8"))
    _, pool = load_pool()
    recs = load_heldout()
    m2 = fit_m2(recs)
    begy = IdentityCorr()
    prim = primary_anchors(tg)
    ovals = [(t["toponym"], sk.f(t["edel_transliteration"]), sk.f(t["linear_b"])) for t in prim]

    def r1(scorer):
        return sum(1 for _, e, tr in ovals if rank_of(scorer, e, tr, pool) == 1)

    r1_m2 = r1(lambda e, s: m2.score(e, s))
    r1_bid = r1(score_bid)
    r1_begy = r1(begy.score)

    # joint PERMUTATION null: bijective shuffle of _sem labels (preserves the multiset), refit, recount r1 (§6)
    rng = random.Random(SEED)
    sem_labels = [r["_sem"] for r in recs]
    null = []
    for _ in range(N_PERM):
        perm = sem_labels[:]; rng.shuffle(perm)
        pm = M.Correspondence().fit([dict(r, _sem=perm[i]) for i, r in enumerate(recs)])
        null.append(sum(1 for _, e, tr in ovals if rank_of(lambda a, b: pm.score(a, b), e, tr, pool) == 1))
    hist = {k: null.count(k) for k in range(len(ovals) + 1)}
    p = (1 + sum(1 for x in null if x >= r1_m2)) / (1 + N_PERM)
    # §10 endpoint-clearability: if the realistic r1=2 endpoint cannot reach p<0.05 under the null, NO_POWER
    p_if_2 = (1 + sum(1 for x in null if x >= 2)) / (1 + N_PERM)
    underpowered = p_if_2 >= 0.05

    if fc["NO_POWER"] or underpowered:
        verdict = "NO_POWER"
    elif r1_m2 <= 1 or p >= 0.05:
        verdict = "REFUTE"
    elif r1_m2 <= max(r1_bid, r1_begy):
        verdict = "RECOVERED_TRIVIAL"
    else:
        verdict = "CONFIRM_GENERALIZES"

    conf = json.load(open(POOL, encoding="utf-8"))["target_confusability"]
    out = {"K": len(ovals), "M_pool": fc["n_pool"], "r1_M2": r1_m2, "r1_B_id": r1_bid, "r1_B_egy": r1_begy,
           "p_value": round(p, 5), "p_if_r1_is_2": round(p_if_2, 5), "underpowered": underpowered,
           "N_perm": N_PERM, "null_r1_histogram": hist, "surprisal_bits": round(-math.log2(p), 2),
           "verdict": verdict,
           "per_anchor": {t: {"oval": sk.f_str(e), "true_lb": sk.f_str(tr),
                              "rank_M2": rank_of(lambda a, b: m2.score(a, b), e, tr, pool),
                              "rank_B_id": rank_of(score_bid, e, tr, pool),
                              "rank_B_egy": rank_of(begy.score, e, tr, pool),
                              "confusable_within_1": conf[t]["n_within_editdist_1"]}
                          for t, e, tr in ovals}}
    os.makedirs(RES, exist_ok=True)
    json.dump(out, open(os.path.join(RES, "cretan_oneshot_verdict.json"), "w"), indent=1)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-oneshot", action="store_true", help="run the ONE-SHOT verdict (post-mint only)")
    a = ap.parse_args()
    if a.run_oneshot:
        print(json.dumps(run_oneshot(), ensure_ascii=False, indent=1))
    else:
        print(json.dumps(freeze_checks(), ensure_ascii=False, indent=1))
