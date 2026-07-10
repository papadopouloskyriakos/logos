"""E206 Stage-2 execution — freeze @ 6e6af04. Replay qualification first; then 147
confirmatory candidates vs the LB name inventory under the frozen drift matcher; 3-family
canary battery; Holm; correspondence + held-out gates. Conditional on the UNLICENSED A/B
same-sign convention (labelled). Seeds master|E206S2."""
import hashlib
import json
import os
import unicodedata
from collections import Counter, defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
NAMES = ("/home/claude-runner/gitlab/n8n/logos/corpus/bronze/code/CSA_OptMatcher/data/"
         "linear_b-greek.names.cog")
SLOTS = os.path.join(HERE, "..", "SLOT_FREEZE.json")
MASTER = 1336530913
MATCH_THR = 0.34


def seed_for(*p):
    return int(hashlib.sha256(("|".join(map(str, (MASTER, "E206S2") + p))).encode()
                              ).hexdigest()[:8], 16) % 2**31


def lb_tokens(glyphs):
    toks = []
    for ch in glyphs:
        try:
            nm = unicodedata.name(ch)
        except ValueError:
            return None
        if not nm.startswith("LINEAR B SYLLABLE"):
            return None
        toks.append(nm.split()[-1].lower())
    return toks if toks else None


def la_tokens(signs):
    out = []
    for s in signs:
        t = s.lower()
        for u, a in zip("₀₁₂₃₄₅₆₇₈₉", "0123456789"):
            t = t.replace(u, a)
        out.append(t)
    return out


CONS = lambda t: t[:-1] if len(t) >= 2 and t[-1] in "aeiou" else t


def drift(a, b):
    """Frozen matcher: token Levenshtein; sub .5 same-consonant, else 1; indel 1; /max len."""
    n, m = len(a), len(b)
    D = [[0.0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        D[i][0] = i
    for j in range(m + 1):
        D[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            sub = 0.0 if a[i - 1] == b[j - 1] else (
                0.5 if CONS(a[i - 1]) == CONS(b[j - 1]) else 1.0)
            D[i][j] = min(D[i - 1][j] + 1, D[i][j - 1] + 1, D[i - 1][j - 1] + sub)
    return D[n][m] / max(n, m, 1)


def best(cand, inventory):
    scores = [(drift(cand, nm), i) for i, nm in enumerate(inventory)]
    return min(scores)


def main():
    # slot-set hash verification (freeze requirement)
    h = hashlib.sha256(open(SLOTS, "rb").read()).hexdigest()
    assert h == open(os.path.join(HERE, "..", "SLOT_FREEZE.sha256")).read().split()[0]

    inv = []
    for ln in open(NAMES, encoding="utf-8"):
        col = ln.split("\t")[0].strip()
        t = lb_tokens(col)
        if t and len(t) >= 2:
            inv.append(t)
    print(f"LB name inventory: {len(inv)} usable names", flush=True)

    # ---- replay qualification (detector power; run FIRST) ----
    rng = np.random.default_rng(seed_for("replay"))
    ok = 0
    trials = 200
    vowels = "aeiou"
    for k in range(trials):
        nm = inv[int(rng.integers(0, len(inv)))]
        pert = list(nm)
        j = int(rng.integers(0, len(pert)))
        t = pert[j]
        if t[-1] in vowels:
            pert[j] = t[:-1] + vowels[(vowels.index(t[-1]) + 1 + int(rng.integers(0, 4))) % 5]
        sc, idx = best(pert, inv)
        ok += (inv[idx] == nm and sc <= MATCH_THR)
    replay_rate = ok / trials
    print(f"replay qualification: {replay_rate:.3f} (bar 0.60)", flush=True)
    if replay_rate < 0.60:
        json.dump({"experiment": "E206_S2", "status": "E206_INVALID",
                   "reason": f"detector failed replay qualification ({replay_rate:.3f} < .60)"},
                  open(os.path.join(HERE, "STAGE2_RESULT.json"), "w"), indent=1)
        print("VERDICT: E206_INVALID (detector unqualified)")
        return 1

    slots = json.load(open(SLOTS))
    cands = {k: v for k, v in slots["candidates"].items()
             if not v["contaminated_prior_exposure"]}
    expl = {k: v for k, v in slots["candidates"].items()
            if v["contaminated_prior_exposure"]}
    print(f"confirmatory candidates: {len(cands)} | exploratory: {len(expl)}", flush=True)

    # inventory split for held-out gate
    rng2 = np.random.default_rng(seed_for("invsplit"))
    order = rng2.permutation(len(inv))
    fit_inv = [inv[i] for i in order[:int(0.7 * len(inv))]]
    hold_inv = [inv[i] for i in order[int(0.7 * len(inv)):]]

    # LB sign frequency for fabricated canaries
    freq = Counter(t for nm in inv for t in nm)
    pool = list(freq)
    pw = np.array([freq[t] for t in pool], float)
    pw /= pw.sum()

    results = {}
    for key, c in cands.items():
        cand = la_tokens(c["signs"])
        sc, idx = best(cand, fit_inv)
        L = len(cand)
        rngc = np.random.default_rng(seed_for("canary", key))
        fab = [list(rngc.choice(pool, size=L, p=pw)) for _ in range(200)]
        fab_scores = sorted(best(f, fit_inv)[0] for f in fab)
        p_plus1 = (1 + sum(1 for x in fab_scores if x <= sc)) / 201
        same_len = [nm for nm in fit_inv if len(nm) == L] or fit_inv
        shuf = []
        for _ in range(100):
            nm = same_len[int(rngc.integers(0, len(same_len)))]
            pm = list(nm)
            rngc.shuffle(pm)
            shuf.append(pm)
        shuf_med = float(np.median([best(s2, fit_inv)[0] for s2 in shuf]))
        results[key] = {"score": round(sc, 4), "matched": sc <= MATCH_THR,
                        "best_name": "-".join(fit_inv[idx]),
                        "p_plus1_vs_fabricated": round(p_plus1, 5),
                        "beats_shuffled_median": sc < shuf_med}
    # Holm over the 147-test family
    ps = sorted(((v["p_plus1_vs_fabricated"], k) for k, v in results.items()))
    m = len(ps)
    survivors = []
    for rank, (p, k) in enumerate(ps):
        if p <= 0.05 / (m - rank):
            survivors.append(k)
        else:
            break
    survivors = [k for k in survivors
                 if results[k]["matched"] and results[k]["beats_shuffled_median"]]
    print(f"Holm survivors (matched + beats shuffled): {survivors}", flush=True)

    verdict = "NO_MATCH_BEYOND_CANARIES"
    corr_report = {}
    if len(survivors) >= 3:
        mapping = defaultdict(Counter)
        for k in survivors:
            cand = la_tokens(cands[k]["signs"])
            nm = results[k]["best_name"].split("-")
            for a, b in zip(cand, nm):
                mapping[a][b] += 1
        coherent = all(len(v) == 1 for v in mapping.values())
        corr_report = {"survivors": survivors, "coherent_system": coherent}
        if coherent:
            hits = 0
            for k in survivors:
                sc2, _ = best(la_tokens(cands[k]["signs"]), hold_inv)
                hits += sc2 <= MATCH_THR
            corr_report["held_out_hits"] = hits
            if hits >= 1:
                verdict = "L3_ONOMASTIC_CLASS_SUPPORTED"
            else:
                verdict = "ONOMASTIC_CANDIDATES_EXPLORATORY_ONLY"
        else:
            verdict = "ONOMASTIC_CANDIDATES_EXPLORATORY_ONLY"
    elif survivors:
        verdict = "ONOMASTIC_CANDIDATES_EXPLORATORY_ONLY"

    out = {"experiment": "E206_S2", "freeze": "6e6af04",
           "conditional_on": "UNLICENSED A/B same-sign convention (conditional map)",
           "replay_qualification": replay_rate,
           "n_confirmatory": len(cands), "n_exploratory_flagged": len(expl),
           "holm_family_size": m, "survivors": survivors,
           "correspondence": corr_report,
           "n_matched_raw": sum(1 for v in results.values() if v["matched"]),
           "verdict": verdict,
           "per_candidate": results}
    json.dump(out, open(os.path.join(HERE, "STAGE2_RESULT.json"), "w"), indent=1)
    json.dump({"stage": 2, "status": verdict, "completed": "2026-07-10"},
              open(os.path.join(HERE, "STATUS.json"), "w"), indent=1)
    print("VERDICT:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
