"""
EPOCH-061 machinery: LINE-ISOLATION test for anonymous token TYPE U+1076B.

L2 only — token-position structure. No sign value / reading / phonetics / meaning.

Null: within each inscription, re-place the same number of target tokens
uniformly at random among the inter-content-token gaps of the non-target
skeleton (preserving nl structure + target count). A placed target is
"isolated" iff its slot is bounded on both sides by a boundary token
(nl/div/START/END) of the skeleton.
"""
import json, random, sys, hashlib
from collections import Counter

TARGET_RAW = "\U0001076b"
BOUNDARY = {"nl", "div"}  # plus START/END sentinels

def is_target(tok):
    return tok.get("t") == "other" and TARGET_RAW in tok.get("raw", "")

def ttype(tok):
    return tok.get("t", "?")

# ---------- OBSERVED ----------
def observed_isolation(inscriptions):
    n_target = 0
    n_isolated = 0
    before = Counter()
    after = Counter()
    for ins in inscriptions:
        stream = ins.get("stream", [])
        for i, tok in enumerate(stream):
            if is_target(tok):
                n_target += 1
                pt = "START" if i == 0 else ttype(stream[i-1])
                nt = "END" if i == len(stream)-1 else ttype(stream[i+1])
                before[pt] += 1
                after[nt] += 1
                if pt in BOUNDARY or pt == "START":
                    if nt in BOUNDARY or nt == "END":
                        n_isolated += 1
    rate = (n_isolated / n_target) if n_target else 0.0
    return rate, n_target, n_isolated, dict(before), dict(after)

# ---------- NULL: skeleton-gap re-placement ----------
def skeleton_and_slots(stream):
    """
    Build the non-target skeleton (list of token types, with START/END
    sentinels) and the list of slots. A slot is a gap between two consecutive
    skeleton tokens (or at the ends). Each slot is characterised by its
    left/right boundary types. Returns:
      boundaries : list of (left_type, right_type) for each slot
      k          : number of target tokens originally in this stream
    Slot i sits between skeleton token (i-1) and skeleton token i.
    """
    skel_types = []  # token types of non-target tokens, in order
    k = 0
    for tok in stream:
        if is_target(tok):
            k += 1
        else:
            skel_types.append(ttype(tok))
    # slots: between consecutive skeleton tokens, plus before-first and after-last
    # slot j (0..len(skel_types)) has left = skel_types[j-1] (or START), right = skel_types[j] (or END)
    n_slots = len(skel_types) + 1
    boundaries = []
    for j in range(n_slots):
        left = "START" if j == 0 else skel_types[j-1]
        right = "END" if j == len(skel_types) else skel_types[j]
        boundaries.append((left, right))
    return boundaries, k

def null_isolation_once(inscriptions, rng):
    """One reshuffle: per inscription, place k targets uniformly among slots."""
    total_target = 0
    total_isolated = 0
    for ins in inscriptions:
        stream = ins.get("stream", [])
        boundaries, k = skeleton_and_slots(stream)
        if k == 0:
            continue
        n_slots = len(boundaries)
        if n_slots == 0:
            # no skeleton at all (stream was all targets) — every target isolated
            total_target += k
            total_isolated += k
            continue
        # sample k slots with replacement (uniform); a target is isolated iff
        # both its slot boundaries are boundary-types
        for _ in range(k):
            slot = rng.randrange(n_slots)
            left, right = boundaries[slot]
            total_target += 1
            if (left in BOUNDARY or left == "START") and (right in BOUNDARY or right == "END"):
                total_isolated += 1
    return (total_isolated / total_target) if total_target else 0.0

def perm_test(inscriptions, observed, n_perm=500, seed=12345):
    rng = random.Random(seed)
    ge = 0
    nulls = []
    for _ in range(n_perm):
        r = null_isolation_once(inscriptions, rng)
        nulls.append(r)
        if r >= observed:
            ge += 1
    p = (ge + 1) / (n_perm + 1)  # add-1 smoothing
    mean = sum(nulls) / len(nulls)
    return p, mean, nulls

# ---------- POSITIVE CONTROL (synthetic) ----------
def make_synth_always_isolated(n_ins=30, seed=0):
    """Each inscription: target on its own line (nl target nl)."""
    rng = random.Random(seed)
    out = []
    for i in range(n_ins):
        stream = []
        # a few content lines, with target always alone on its own line
        nlines = rng.randint(2, 5)
        for _ in range(nlines):
            stream.append({"t": "word", "signs": ["X"]})
            stream.append({"t": "num", "v": 5})
            stream.append({"t": "nl"})
            # target alone on next line
            stream.append({"t": "other", "raw": TARGET_RAW})
            stream.append({"t": "nl"})
        out.append({"id": f"SYN_A_{i}", "site": "SynA", "stream": stream})
    return out

def make_synth_random(n_ins=30, seed=0):
    """Target placed at uniformly random content positions (NOT systematically isolated)."""
    rng = random.Random(seed)
    out = []
    for i in range(n_ins):
        stream = []
        nlines = rng.randint(3, 6)
        for _ in range(nlines):
            stream.append({"t": "word", "signs": ["X"]})
            stream.append({"t": "num", "v": 5})
            stream.append({"t": "nl"})
        # insert k targets at uniformly random positions in the stream
        k = rng.randint(1, 4)
        for _ in range(k):
            pos = rng.randint(0, len(stream))
            stream.insert(pos, {"t": "other", "raw": TARGET_RAW})
        out.append({"id": f"SYN_R_{i}", "site": "SynR", "stream": stream})
    return out

def positive_control():
    # (a) DETECT
    syn = make_synth_always_isolated(n_ins=30, seed=1)
    obs, nt, ni, _, _ = observed_isolation(syn)
    p, mean, _ = perm_test(syn, obs, n_perm=500, seed=42)
    detect_p = p
    detect_ok = p <= 0.05
    # (b) FALSE-POSITIVE: across >=20 draws of random-placement corpus
    fp = 0
    draws = 25
    for s in range(draws):
        synr = make_synth_random(n_ins=30, seed=100+s)
        obsr, _, _, _, _ = observed_isolation(synr)
        pr, _, _ = perm_test(synr, obsr, n_perm=200, seed=200+s)
        if pr <= 0.05:
            fp += 1
    fp_rate = fp / draws
    fp_ok = fp_rate <= 0.10
    passed = detect_ok and fp_ok
    return {
        "pc_verdict": "PASSED" if passed else "FAILED",
        "detect_p": detect_p,
        "detect_obs": obs,
        "detect_null_mean": mean,
        "false_pos_rate": fp_rate,
        "fp_draws": draws,
        "pc_is_synthetic": True,
    }

# ---------- CROSS-SITE ----------
def cross_site(inscriptions, n_perm=500, seed=999):
    by_site = {}
    for ins in inscriptions:
        by_site.setdefault(ins.get("site", "?"), []).append(ins)
    out = {}
    for site, ins_list in by_site.items():
        obs, nt, ni, _, _ = observed_isolation(ins_list)
        if nt < 15:
            continue
        p, mean, _ = perm_test(ins_list, obs, n_perm=n_perm, seed=seed)
        out[site] = {"n_target": nt, "isolation_obs": obs,
                     "isolation_null_mean": mean, "perm_p": p,
                     "direction": "enriched" if obs > mean else "depleted"}
    return out

def leave_one_site_out(inscriptions, drop_site="Haghia Triada", n_perm=500, seed=7):
    rest = [ins for ins in inscriptions if ins.get("site") != drop_site]
    obs, nt, ni, _, _ = observed_isolation(rest)
    p, mean, _ = perm_test(rest, obs, n_perm=n_perm, seed=seed)
    return {"loo_obs": obs, "loo_null_mean": mean, "loo_p": p, "loo_n_target": nt}

# ---------- SELF-CHECK ----------
def self_check():
    """Validate the reshuffle null on a tiny synthetic with known structure."""
    # 1 inscription: word nl target nl word nl  -> target isolated (nl|nl)
    # skeleton = [word, nl, word, nl]; slots: 5
    ins = [{"id":"T","site":"T","stream":[
        {"t":"word","signs":["A"]},{"t":"nl"},
        {"t":"other","raw":TARGET_RAW},
        {"t":"nl"},
        {"t":"word","signs":["B"]},{"t":"nl"},
    ]}]
    obs, nt, ni, _, _ = observed_isolation(ins)
    assert nt == 1 and ni == 1, (nt, ni)
    assert abs(obs - 1.0) < 1e-9
    # skeleton types: word, nl, nl, word, nl  (target removed)
    # slots: 6 ; boundaries:
    #  slot0: START|word   -> not isolated
    #  slot1: word|nl      -> not isolated
    #  slot2: nl|nl        -> ISOLATED
    #  slot3: nl|word      -> not isolated
    #  slot4: word|nl      -> not isolated
    #  slot5: nl|END       -> ISOLATED
    # so null isolation prob per target = 2/6 = 0.333
    b, k = skeleton_and_slots(ins[0]["stream"])
    assert k == 1, k
    iso_slots = sum(1 for (l,r) in b if (l in BOUNDARY or l=="START") and (r in BOUNDARY or r=="END"))
    assert iso_slots == 2, (iso_slots, b)
    # run null many times, expect mean ~ 2/6
    rng = random.Random(0)
    vals = [null_isolation_once(ins, rng) for _ in range(20000)]
    m = sum(vals)/len(vals)
    assert abs(m - 2/6) < 0.02, m
    print("SELF-CHECK OK: observed=1.0, null mean=%.4f (expected 0.3333)" % m)
    return True

if __name__ == "__main__":
    ok = self_check()
    print("self_check:", ok)
    # quick PC
    pc = positive_control()
    print("PC:", pc)
