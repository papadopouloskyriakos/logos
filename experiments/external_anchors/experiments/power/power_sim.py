#!/usr/bin/env python3
"""power_sim.py — ABSTRACT power/false-positive envelope for the toponym-anchor design (Task D).

DESIGN ANALYSIS ONLY. It does NOT match real Egyptian toponyms to real Linear A candidates. It
simulates the *statistical* behaviour of a fuzzy-matching-under-search procedure over synthetic
anchors/candidates, to estimate: (a) how often a search over sign-value mappings can "explain" k of
n anchors BY CHANCE (end-to-end false-positive), and (b) how often it recovers a planted signal at
matched scarcity. All parameters are PROVISIONAL pending REQ-02 (Hoch) calibration of the real
Egyptian->foreign distortion — labelled as such.

Model (transparent, deliberately simple):
  - V distinct signs; a "mapping" gives each sign one of `flex` allowed sound-slots (search freedom).
  - Each external anchor is a length-La skeleton of sound-slots; each internal candidate a length-Lc
    sign string. A candidate MATCHES an anchor under a mapping if the mapped candidate contains the
    anchor skeleton within Hamming tolerance `tol` (a proxy for the Egyptian distortion tolerance).
  - The procedure searches `budget` random mappings and keeps the one maximizing matched anchors
    (best-of-search = the adaptive step the null MUST replay).
  - NULL: anchors random, no planted correspondence. SIGNAL: a fixed true mapping is planted and a
    fraction `signal_frac` of anchors have a genuine candidate image (+ `noise` skeleton flips).
Graduate rule (provisional): >= ceil(0.75*n_anchors) anchors matched by ONE mapping, on held-out.
"""
import argparse, json, math, os, random

def one_trial(rng, n_anchors, n_cand, V, La, Lc, flex, tol, budget, planted):
    slots = list(range(max(4, V // 2)))
    cands = [[rng.randrange(V) for _ in range(Lc)] for _ in range(n_cand)]
    if planted:
        true_map = [rng.choice(slots) for _ in range(V)]
        anchors = []
        for a in range(n_anchors):
            if a < planted:  # genuine image of a random candidate under true_map (+noise)
                c = cands[rng.randrange(n_cand)]
                sk = [true_map[s] for s in c[:La]]
                sk = [(x if rng.random() > 0.15 else rng.choice(slots)) for x in sk]  # noise flips
                anchors.append(sk)
            else:
                anchors.append([rng.choice(slots) for _ in range(La)])
    else:
        anchors = [[rng.choice(slots) for _ in range(La)] for _ in range(n_anchors)]
    best = 0
    for _ in range(budget):
        m = [rng.choice(slots) for _ in range(V)]
        matched = 0
        for sk in anchors:
            hit = False
            for c in cands:
                mc = [m[s] for s in c]
                # sliding Hamming: does anchor skeleton appear within tol anywhere in mapped candidate?
                for i in range(0, max(1, len(mc) - La + 1)):
                    win = mc[i:i+La]
                    if len(win) == La and sum(1 for x, y in zip(win, sk) if x != y) <= tol:
                        hit = True; break
                if hit: break
            matched += hit
        best = max(best, matched)
    return best

def heldout_trial(rng, n_anchors, planted, frozen, **p):
    """Train (select-best mapping on n-1 anchors), then test on the held-out anchor.
    frozen=True disables the mapping search (correspondence model fixed a priori) — the
    discipline condition. Returns 1 if the held-out anchor matches under the selected/fixed map."""
    p2 = dict(p); budget = 1 if frozen else p2.pop("budget"); p2.pop("budget", None)
    V = p["V"]; slots = list(range(max(4, V // 2)))
    cands = [[rng.randrange(V) for _ in range(p["Lc"])] for _ in range(p["n_cand"])]
    tmap = [rng.choice(slots) for _ in range(V)]
    def mk_anchor(genuine):
        if genuine:
            c = cands[rng.randrange(p["n_cand"])]; sk = [tmap[s] for s in c[:p["La"]]]
            return [(x if rng.random() > 0.15 else rng.choice(slots)) for x in sk]
        return [rng.choice(slots) for _ in range(p["La"])]
    anchors = [mk_anchor(i < planted) for i in range(n_anchors)]
    train, test = anchors[:-1], anchors[-1]
    def matches(m, sk):
        for c in cands:
            mc = [m[s] for s in c]
            for i in range(0, max(1, len(mc) - p["La"] + 1)):
                if sum(1 for x, y in zip(mc[i:i+p["La"]], sk) if x != y) <= p["tol"]:
                    return True
        return False
    if frozen:  # fixed a-priori mapping (no search): use a single random fixed map
        m = [rng.choice(slots) for _ in range(V)]
        return int(matches(m, test))
    best_m, best_k = None, -1
    for _ in range(budget):
        m = [rng.choice(slots) for _ in range(V)]
        k = sum(matches(m, sk) for sk in train)
        if k > best_k: best_k, best_m = k, m
    return int(matches(best_m, test))

def run(n_anchors, trials=400, seed=20260706, **p):
    rng = random.Random(seed + n_anchors * 7919)
    thr = math.ceil(0.75 * n_anchors)
    null_grad = sig_grad = ho_null = ho_sig = 0
    for _ in range(trials):
        if one_trial(rng, n_anchors, planted=0, **p) >= thr: null_grad += 1
        if one_trial(rng, n_anchors, planted=max(2, n_anchors), **p) >= thr: sig_grad += 1
        ho_null += heldout_trial(rng, n_anchors, planted=0, frozen=False, **p)
        ho_sig += heldout_trial(rng, n_anchors, planted=n_anchors, frozen=False, **p)
    return {"n_anchors": n_anchors, "graduate_threshold": thr,
            "insample_false_positive_rate": round(null_grad / trials, 4),
            "insample_true_recovery_rate": round(sig_grad / trials, 4),
            "heldout_false_positive_rate": round(ho_null / trials, 4),
            "heldout_true_recovery_rate": round(ho_sig / trials, 4), "trials": trials}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=400)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "..", "results", "power"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    # provisional realistic-scarcity params (label: PROVISIONAL pending REQ-02 calibration)
    base = dict(n_cand=11, V=20, La=3, Lc=3, flex=3, tol=1, budget=300)   # 11 = tier-B TOPONYM_LIKE
    rows = [run(n, trials=a.trials, **base) for n in (2, 3, 4, 5, 6)]
    out = {"note": "ABSTRACT design analysis; params PROVISIONAL pending REQ-02 (Hoch) distortion "
                   "calibration. n_cand=11 = tier-B TOPONYM_LIKE count; graduate=>=75% anchors by one mapping.",
           "params": base, "envelope": rows}
    open(os.path.join(a.out, "toponym_power_envelope.json"), "w").write(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()
