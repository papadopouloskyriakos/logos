"""EPOCH-104R — campaign-wide adaptive null, rerun under (a) the CORRECTED categorical joint
maxT (E103R) and (b) a bound-based certification criterion, per prereg_addendum_R.md
(append-only; frozen originals untouched).

Runs the E103 graduation decision rule end-to-end on 400 structure-matched signal-free null
corpora + a naive best-of raw-p ablation arm on the SAME 400 nulls + 40 planted-positive
corpora. Verdict: CAMPAIGN_NULL_GATES_CERTIFIED iff the one-sided exact Clopper-Pearson 95%
upper bound on the false-graduation rate is <= 0.02 AND planted recovery >= 0.8; else
CAMPAIGN_NULL_PILOT_ONLY. Committed blind before any corrected-machinery null was run.

Scope notes (committed): the 12% planted prefix establishes power only for effects of that
general magnitude; "end-to-end" means the graduation DECISION RULE end-to-end (PC and LOMO
are not re-executed per null); the absolute-value-gate zero is structural (a positional-
shuffle null has a single axis and cannot satisfy >=2 independent channels), labeled as such.

This validates the discipline, not a reading. No LA values.
"""
import hashlib
import json
import os
from collections import Counter

import numpy as np

import importlib.util

EPOCH_DIR = os.path.dirname(os.path.abspath(__file__))
E103_DIR = os.path.normpath(os.path.join(EPOCH_DIR, "..", "EPOCH-103"))


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


e103 = _load("e103", os.path.join(E103_DIR, "machinery.py"))
e103r = _load("e103r", os.path.join(E103_DIR, "machinery_R.py"))

SILVER = "corpus/silver/inscriptions_structured.json"
M_MAXT = 5000  # aligned with E103's ORIGINAL prereg commitment (original E104 impl used 2000)


def sha256_file(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


# ---- corpus parsed ONCE; per-null shuffles preserve the frozen null_corpus_words semantics
# and rng-consumption order, so a given seed yields the identical null corpus. ----
_PARSED = None


def parsed_stream(path=SILVER):
    global _PARSED
    if _PARSED is None:
        d = json.load(open(path))
        ins_list = []
        for ins in d:
            st = ins.get("stream", [])
            toks = []
            for i, tok in enumerate(st):
                t = tok.get("t")
                if t == "word":
                    nxt = st[i + 1]["t"] if i + 1 < len(st) else None
                    toks.append(("word", list(tok.get("signs", [])), nxt == "num"))
                else:
                    toks.append((t, None, False))
            ins_list.append(toks)
        _PARSED = ins_list
    return _PARSED


def null_corpus_words(rng):
    """Identical semantics + rng call order to the frozen EPOCH-104 null_corpus_words."""
    A, B, C = [], [], []
    for toks in parsed_stream():
        cur = []
        for t, signs, before_num in toks:
            if t == "word":
                sg = list(signs)
                rng.shuffle(sg)
                A.append(sg)
                cur += sg
                if before_num:
                    C.append(sg)
            else:
                if cur:
                    B.append(cur)
                    cur = []
        if cur:
            B.append(cur)
    ge2 = lambda L: [w for w in L if len(w) >= 2]
    return {"A_editor": ge2(A), "B_divider_strict": ge2(B), "C_numeral_anchored": ge2(C)}


def graduates_both_arms(schemes, seed=0):
    """Apply the E103 graduation rule with the CORRECTED categorical maxT (arm 1) and the
    naive best-of raw-p ablation (arm 2) on the SAME schemes. One maxT computation per
    variant serves both arms (top-sign identification is marginal-only and shared)."""
    passed_maxT, passed_naive, top_signs = [], [], []
    names = list(schemes.keys())
    for name in names:
        words = schemes[name]
        mt = e103r.universe_maxT_categorical(words, n_draws=M_MAXT, seed=seed)
        top = mt["top_sign"]
        top_signs.append(top)
        if mt["maxT_p"][top] <= 0.01:
            passed_maxT.append(name)
        _, _, p_raw = e103.perm_null_fast(words, top, n_draws=M_MAXT, seed=seed)
        if p_raw <= 0.01:
            passed_naive.append(name)

    def decide(passed):
        if len(passed) >= 2:
            top_in_passed = [t for n, t in zip(names, top_signs) if n in passed]
            common = Counter(top_in_passed).most_common(1)[0]
            if common[1] >= 2:
                return True, common[0], len(passed)
        return False, None, len(passed)

    g1 = decide(passed_maxT)
    g2 = decide(passed_naive)
    return g1, g2


def cp95_upper(k, n):
    """One-sided exact Clopper-Pearson 95% upper bound."""
    from scipy.stats import beta
    return 1.0 if k == n else float(beta.ppf(0.95, k + 1, n - k))


def run_R(n_null=400, n_plant=40):
    false_maxT, false_naive = 0, 0
    grad_signs_maxT, grad_signs_naive = Counter(), Counter()
    for i in range(n_null):
        sch = null_corpus_words(np.random.default_rng(1000 + i))
        (g1, s1, _), (g2, s2, _) = graduates_both_arms(sch, seed=i)
        if g1:
            false_maxT += 1
            grad_signs_maxT[s1] += 1
        if g2:
            false_naive += 1
            grad_signs_naive[s2] += 1
        if (i + 1) % 25 == 0:
            print(f"  null {i+1}/{n_null}: maxT {false_maxT}, naive {false_naive}", flush=True)

    recovered = 0
    for i in range(n_plant):
        r = np.random.default_rng(5000 + i)
        sch = null_corpus_words(r)
        for name in sch:
            sch[name] = [(["PX"] + w) if r.random() < 0.12 else w for w in sch[name]]
        (g, s, _), _ = graduates_both_arms(sch, seed=i)
        if g and s == "PX":
            recovered += 1
    print(f"  planted: {recovered}/{n_plant}", flush=True)

    rate_maxT = false_maxT / n_null
    rate_naive = false_naive / n_null
    ub_maxT = cp95_upper(false_maxT, n_null)
    ub_naive = cp95_upper(false_naive, n_null)
    rec_rate = recovered / n_plant
    certified = (ub_maxT <= 0.02) and (rec_rate >= 0.8)
    verdict = "CAMPAIGN_NULL_GATES_CERTIFIED" if certified else "CAMPAIGN_NULL_PILOT_ONLY"
    suppression = (false_naive / false_maxT) if false_maxT > 0 else float("inf")

    out = {
        "epoch": "EPOCH-104R",
        "governing_addendum": "prereg_addendum_R.md",
        "maxT_construction": "corrected categorical joint null (E103R universe_maxT_categorical)",
        "maxT_draws": M_MAXT,
        "maxT_draws_alignment_note": (
            "M=5000 aligns with E103's ORIGINAL prereg commitment; the original E104 "
            "implementation used n_draws=2000 inside graduates() (implementation economy)."),
        "n_null": n_null,
        "false_graduated_count_maxT": false_maxT,
        "false_graduated_rate_maxT": rate_maxT,
        "false_graduated_cp95_upper_maxT": round(ub_maxT, 6),
        "false_graduated_count_naive_ablation": false_naive,
        "false_graduated_rate_naive_ablation": rate_naive,
        "false_graduated_cp95_upper_naive_ablation": round(ub_naive, 6),
        "ablation_suppression_factor": (round(suppression, 2)
                                        if suppression != float("inf") else "inf (0 maxT false grads)"),
        "grad_signs_maxT": dict(grad_signs_maxT),
        "grad_signs_naive": dict(grad_signs_naive),
        "n_plant": n_plant,
        "planted_recovery": f"{recovered}/{n_plant}",
        "planted_recovery_rate": rec_rate,
        "absolute_value_gate_false_fire": 0,
        "absolute_value_gate_note": (
            "STRUCTURAL zero, by construction: the gate requires >=2 independent channels; a "
            "positional-shuffle null has a single axis and cannot satisfy it. Labeled as a "
            "design property, not an empirical finding."),
        "scope_notes": [
            "The 12% planted prefix establishes power only for effects of that general magnitude.",
            "'End-to-end' means the graduation DECISION RULE end-to-end; the positive control "
            "and LOMO are not re-executed per null.",
            "The absolute-value-gate zero is structural (by construction), labeled as such.",
        ],
        "original_run_status": (
            "PILOT: the original E104 (1/200, CP95 upper 2.35%) is a valid empirical "
            "calibration of the rule-as-implemented (its nulls used genuine rng.shuffle), but "
            "does not establish rate <= 2% at 95% confidence; certification language attaches "
            "only to this bound-based verdict."),
        "verdict": verdict,
        "rationale": (
            f"The graduation decision rule (corrected best-of-universe categorical maxT x 3 "
            f"overlapping segmentation/selection variants x >=2/3 agreement) fabricates a "
            f"graduated relative finding on structure-matched signal-free nulls "
            f"{false_maxT}/{n_null} times (one-sided exact CP95 upper bound "
            f"{ub_maxT:.4f}); the naive best-of raw-p ablation on the SAME nulls yields "
            f"{false_naive}/{n_null} (CP95 upper {ub_naive:.4f}) -> suppression factor "
            f"{suppression if suppression != float('inf') else 'inf'}. Planted positive "
            f"(12% prefix) recovered {recovered}/{n_plant}. Verdict under the committed "
            f"bound-based rule: {verdict}."),
    }
    out["plan_hash"] = sha256_file(os.path.join(EPOCH_DIR, "prereg_addendum_R.md"))
    out["code_manifest"] = {
        "machinery_R.py": sha256_file(os.path.join(EPOCH_DIR, "machinery_R.py")),
        "EPOCH-103/machinery_R.py (imported, corrected maxT)":
            sha256_file(os.path.join(E103_DIR, "machinery_R.py")),
        "EPOCH-103/machinery.py (frozen, marginal null)":
            sha256_file(os.path.join(E103_DIR, "machinery.py")),
    }
    out["frozen_original_result_sha256"] = sha256_file(os.path.join(EPOCH_DIR, "result.json"))
    return out


if __name__ == "__main__":
    res = run_R()
    json.dump(res, open(os.path.join(EPOCH_DIR, "result_R.json"), "w"), indent=2)
    print("VERDICT:", res["verdict"])
    print(res["rationale"])
