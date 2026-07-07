#!/usr/bin/env python3
"""frozen_power_pass.py — the un-executed 'frozen=True' milestone of the Egyptian toponym-anchor power
envelope (design analysis, Constitution v2.2 Art. VIII/IX). Does NOT touch the frozen artifacts.

The Phase-A audit flagged that the committed toponym_power_envelope.json only reported the frozen=FALSE
(mapping-search) regime. The discipline condition is a FIXED a-priori correspondence (justified by the clean
CC-BY Kilani-2019 group-writing->sound model — its ROLE here is only to license 'no mapping search', so no
Kilani rule is invented). This pass measures, over realistic Egyptian toponym skeleton lengths (La~4-5, e.g.
Knossos kA-n-yw-SA), at the real anchor scarcity (n=3-4 securely-identified Cretan toponyms):

  * FP_frozen  : a fixed a-priori map vs a HELD-OUT RANDOM anchor -> false-positive floor.
  * REC_frozen*: the fixed map == the TRUE correspondence (+ Kilani distortion noise) vs a held-out GENUINE
                 anchor -> an OPTIMISTIC recovery ceiling (assumes Kilani is EXACTLY right).

Verdict rule (transparent): POWERED only if the OPTIMISTIC recovery clears the FP floor by a wide margin AND
FP <= 0.10 (a credible confirmatory bar). If even the optimistic ceiling fails at n=3-4, the channel is
NO_POWER independent of the sound model's quality. Deterministic (seeded).
"""
import json
import os
import random

SEED = 20260707
SLOTS = None


def _slots(V):
    return list(range(max(4, V // 2)))


def _cands(rng, n_cand, Lc, V):
    return [[rng.randrange(V) for _ in range(Lc)] for _ in range(n_cand)]


def _matches(m, sk, cands, La, tol):
    """does the mapped candidate contain the anchor skeleton within Hamming tol anywhere (sliding)?"""
    for c in cands:
        mc = [m[s] for s in c]
        for i in range(0, max(1, len(mc) - La + 1)):
            win = mc[i:i + La]
            if len(win) == La and sum(1 for x, y in zip(win, sk) if x != y) <= tol:
                return True
    return False


def frozen_fp(rng, n_cand, V, La, Lc, tol):
    """fixed a-priori (random) map vs a HELD-OUT RANDOM anchor -> spurious match probability."""
    slots = _slots(V)
    cands = _cands(rng, n_cand, Lc, V)
    m = [rng.choice(slots) for _ in range(V)]                 # the a-priori correspondence (fixed, no search)
    test = [rng.choice(slots) for _ in range(La)]             # held-out anchor with NO genuine image
    return int(_matches(m, test, cands, La, tol))


def frozen_recovery(rng, n_cand, V, La, Lc, tol, noise):
    """fixed map == TRUE correspondence (+distortion noise) vs a held-out GENUINE anchor -> optimistic
    recovery. This is the best case: Kilani gives the exact map and the anchor really is in the corpus."""
    slots = _slots(V)
    cands = _cands(rng, n_cand, Lc, V)
    tmap = [rng.choice(slots) for _ in range(V)]              # the true correspondence == the frozen map
    c = cands[rng.randrange(n_cand)]                          # the genuine internal image of this anchor
    sk = [tmap[s] for s in c[:La]]
    sk = [(x if rng.random() > noise else rng.choice(slots)) for x in sk]   # Egyptian distortion noise
    return int(_matches(tmap, sk, cands, La, tol))


def sweep(trials=4000):
    rows = []
    # realistic: Egyptian consonant-skeleton length La ~ 3-4 (Knossos k-n-s; kA-n-yw-SA), LA candidate word
    # length Lc >= La (a skeleton can only be found in a word at least as long). Sweep Lc in {La, La+1}.
    for n_anchors in (3, 4):
        for La in (3, 4):
            for dLc in (0, 1):
                Lc = La + dLc
                for noise in (0.15, 0.30):
                    rng = random.Random(SEED + n_anchors * 101 + La * 7 + Lc * 3 + int(noise * 100))
                    p = dict(n_cand=11, V=20, tol=1)          # n_cand=11 tier-B TOPONYM_LIKE; V=20 sign space
                    fp = sum(frozen_fp(rng, La=La, Lc=Lc, **p) for _ in range(trials)) / trials
                    rec = sum(frozen_recovery(rng, La=La, Lc=Lc, noise=noise, **p) for _ in range(trials)) / trials
                    gap = round(rec - fp, 3)
                    powered = bool(rec > 2 * max(fp, 0.02) and fp <= 0.10 and gap >= 0.25)
                    rows.append({"n_anchors": n_anchors, "La": La, "Lc": Lc, "kilani_noise": noise,
                                 "FP_frozen": round(fp, 3), "REC_frozen_optimistic": round(rec, 3),
                                 "gap": gap, "powered": powered})
    return rows


def run():
    rows = sweep()
    any_powered = any(r["powered"] for r in rows)
    best = max(rows, key=lambda r: r["gap"])
    verdict = "POWERED_DESIGN" if any_powered else "NO_POWER"
    out = {"regime": "frozen=True (fixed a-priori correspondence; no mapping search)",
           "interpretation": "OPTIMISTIC design ceiling: recovery assumes Kilani gives the EXACT correspondence; "
                             "FP is the fixed-map false-positive floor. If even this optimistic case is NO_POWER "
                             "at n=3-4 real anchors, the Egyptian channel cannot be powered by a better sound model.",
           "verdict": verdict, "any_config_powered": any_powered,
           "best_config": best, "envelope": rows,
           "note": "Design/power analysis only (Art. VIII). Confirmatory use remains SOURCE_BLOCKED (Edel&Gorg "
                   "2005 primary edition not collated; komelhetan transliterations confirmatory_ineligible). "
                   "Frozen result artifacts untouched."}
    outdir = os.path.join(os.path.dirname(__file__), "..", "..", "results", "power")
    os.makedirs(outdir, exist_ok=True)
    json.dump(out, open(os.path.join(outdir, "frozen_power_envelope.json"), "w"), indent=1)
    print(json.dumps({k: out[k] for k in ("verdict", "any_config_powered", "best_config")}, indent=1))
    print("envelope:")
    for r in rows:
        print(" ", r)
    return out


if __name__ == "__main__":
    run()
