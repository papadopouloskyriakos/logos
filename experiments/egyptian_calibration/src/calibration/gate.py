"""§VII matched-scarcity positive control · §VIII end-to-end nulls · §X calibrated power envelope.

The intended Cretan-anchor test has FEW (~3-6 Kom el-Hetan Aegean toponyms) and SHORT (~3-4 consonant)
anchors. The gate here asks whether the validated model retains recovery + false-positive control at
THAT scarcity, using only the frozen non-Cretan corpus (no Cretan data)."""
import json, math, os, random, sys
from collections import Counter
sys.path.insert(0, os.path.dirname(__file__))
import model as M
import validation as V

SEED = 20260706
POOL = None


def _setup():
    global POOL
    recs = M.load(("A", "B"))
    POOL = V._cands(recs)
    return recs


def recovery_by_length(recs):
    """LOO top-1 recovery stratified by anchor length (# consonants) — matched to Cretan-anchor lengths."""
    by = {}
    for i, held in enumerate(recs):
        L = len(held["_sem"])
        mdl = M.Correspondence().fit(recs[:i] + recs[i+1:])
        r = M.recover_rank(mdl, held["_egy"], held["_sem"], POOL, "M2")
        by.setdefault(min(L, 5), []).append(1 if r == 1 else 0)
    return {L: round(sum(v)/len(v), 3) for L, v in sorted(by.items())}, {L: len(v) for L, v in sorted(by.items())}


def null_recovery(recs, kind, seed):
    """§VIII null: recovery under a broken procedure. random_pairing = score against a RANDOM source;
    permuted_model = fit on label-shuffled data; permissive_M9 = all-match. Returns per-anchor top-1."""
    rng = random.Random(seed)
    hits = 0
    for i, held in enumerate(recs):
        train = recs[:i] + recs[i+1:]
        if kind == "random_pairing":
            r = M.recover_rank(M.Correspondence().fit(train), rng.choice(recs)["_egy"], held["_sem"], POOL, "M2")
        elif kind == "permuted_model":
            sh = [dict(t, _sem=rng.choice(train)["_sem"]) for t in train]  # break egy<->sem link
            r = M.recover_rank(M.Correspondence().fit(sh), held["_egy"], held["_sem"], POOL, "M2")
        elif kind == "permissive_M9":
            r = M.recover_rank(None, held["_egy"], held["_sem"], POOL, "M9")
        else:
            raise ValueError(kind)
        hits += (r == 1)
    return round(hits / len(recs), 4)


def positive_control(recs):
    """Matched-scarcity: K short (len<=4) anchors; recovery vs null. Mechanical pass rule."""
    rec_by_len, n_by_len = recovery_by_length(recs)
    p_short = sum(rec_by_len.get(L, 0) * n_by_len.get(L, 0) for L in (2, 3, 4)) / max(sum(n_by_len.get(L, 0) for L in (2, 3, 4)), 1)
    p_null = 1.0 / len(POOL)
    out = {"recovery_by_length": rec_by_len, "n_by_length": n_by_len,
           "short_form_recovery(len<=4)": round(p_short, 3), "per_anchor_null": round(p_null, 5), "by_K": {}}
    for K in (2, 3, 4, 5, 6):
        exp_real = p_short * K
        # null 95th pct of #recovered ~ Binomial(K, p_null): essentially 0
        null_p_ge1 = 1 - (1 - p_null) ** K
        detect = exp_real >= 1.0 and null_p_ge1 < 0.05
        out["by_K"][K] = {"expected_recovered_real": round(exp_real, 2), "null_P(>=1)": round(null_p_ge1, 4),
                          "detectable": detect}
    out["min_detectable_anchors"] = next((K for K in (2, 3, 4, 5, 6) if out["by_K"][K]["detectable"]), None)
    out["control_verdict"] = "PASS" if (p_short > 3 * p_null and out["min_detectable_anchors"] is not None) else "FAIL"
    return out


def nulls(recs):
    fam = {
        "1_random_pairing": null_recovery(recs, "random_pairing", SEED + 1),
        "2_permuted_model": null_recovery(recs, "permuted_model", SEED + 2),
        "3_permissive_M9": null_recovery(recs, "permissive_M9", SEED + 3),
        "real_M2_top1": V.loo(recs, "M2")["top1"],
    }
    fam["specificity_ok"] = fam["real_M2_top1"] > 5 * max(fam["1_random_pairing"], fam["2_permuted_model"])
    fam["permissive_excessive_fp"] = fam["3_permissive_M9"] > 0.2   # architecture rejection trigger
    return fam


def power(recs, pc):
    p = pc["short_form_recovery(len<=4)"]; pool = len(POOL)
    return {"per_anchor_recovery_short": p, "per_anchor_null": round(1/pool, 5),
            "min_detectable_anchors": pc["min_detectable_anchors"],
            "recovery_by_length": pc["recovery_by_length"],
            "prob_no_power_at_K3": round((1 - p) ** 3, 3),   # P(0 of 3 short anchors recovered)
            "note": "Cretan anchors ~3-6, short (3-4 consonants); power estimated at that scarcity"}


def uncertainty_sensitivity(recs):
    """§IX LOW/CENTRAL/HIGH transcription uncertainty on the Egyptian rendering: perturb k consonants of
    each held-out anchor and re-measure recovery. Verdict is fragile if HIGH reverses the control."""
    egy_alpha = list({c for r in recs for c in r["_egy"]})
    out = {}
    for tier, k, seed in (("LOW", 0, 0), ("CENTRAL", 1, 11), ("HIGH", 1, 22)):
        rng = random.Random(SEED + seed); hits = 0; short_hits = short_n = 0
        for i, held in enumerate(recs):
            mdl = M.Correspondence().fit(recs[:i] + recs[i+1:])
            eg = list(held["_egy"])
            if k and eg and (tier == "HIGH" or rng.random() < 0.3):     # CENTRAL perturbs ~30%, HIGH all
                eg[rng.randrange(len(eg))] = rng.choice(egy_alpha)
            r = M.recover_rank(mdl, eg, held["_sem"], POOL, "M2")
            hits += (r == 1)
            if len(held["_sem"]) <= 4:
                short_n += 1; short_hits += (r == 1)
        out[tier] = {"top1": round(hits/len(recs), 3), "short_recovery": round(short_hits/max(short_n, 1), 3)}
    out["verdict_reverses_under_uncertainty"] = out["HIGH"]["short_recovery"] < 3 * (1/len(POOL))
    return out


def run():
    recs = _setup()
    pc = positive_control(recs)
    nl = nulls(recs)
    pw = power(recs, pc)
    unc = uncertainty_sensitivity(recs)
    return {"positive_control": pc, "nulls": nl, "power": pw, "transcription_uncertainty": unc}


if __name__ == "__main__":
    r = run()
    print("positive control:", {k: r["positive_control"][k] for k in ("short_form_recovery(len<=4)", "min_detectable_anchors", "control_verdict")})
    print("  by length:", r["positive_control"]["recovery_by_length"])
    print("nulls:", r["nulls"])
    print("power:", {k: r["power"][k] for k in ("per_anchor_recovery_short", "min_detectable_anchors", "prob_no_power_at_K3")})
    RES = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "results")); os.makedirs(RES, exist_ok=True)
    json.dump(r, open(os.path.join(RES, "gate.json"), "w"), indent=1)
