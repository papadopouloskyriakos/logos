"""
EPOCH-062 machinery: document-peripheral test for U+1076B marker.

Pure L2 token-position structure: content-line index of an anonymous frequent
token TYPE within multi-line inscriptions. NO sign value, NO reading.

Frozen null: within each testable inscription, re-place each marker's
content-line index uniformly at random in {0,...,L-1}, independent, preserving
marker count per inscription and L. Recompute peripheral rate. >=500 reshuffles.
"""
import json
import random
from collections import Counter, defaultdict

MARKER = "\U0001076b"
CONTENT = {"word", "num", "other"}


def content_lines(stream):
    """Build content-lines: maximal runs of CONTENT tokens bounded by nl/START/END.
    'div' and 'nl' are structural, NOT content. Only 'nl'/START/END bound a line;
    'div' does NOT flush (per spec)."""
    lines = []
    cur = []
    for s in stream:
        t = s.get("t")
        if t in CONTENT:
            cur.append(s)
        elif t == "nl":
            if cur:
                lines.append(cur)
                cur = []
        # div and any other structural token: skip (do not flush, do not add)
    if cur:
        lines.append(cur)
    return lines


def is_marker(tok):
    return tok.get("t") == "other" and MARKER in tok.get("raw", "")


def build_testable(data):
    """Return list of dicts: {id, site, L, marker_lis:[li,...]} for testable inscriptions."""
    out = []
    for ins in data:
        cls = content_lines(ins["stream"])
        L = len(cls)
        if L < 3:
            continue
        marker_lis = []
        for li, line in enumerate(cls):
            for tok in line:
                if is_marker(tok):
                    marker_lis.append(li)
        if marker_lis:
            out.append({"id": ins["id"], "site": ins["site"], "L": L, "marker_lis": marker_lis})
    return out


def rates_from_lis(testable_records, lis_per_ins):
    """lis_per_ins: list aligned with testable_records, each a list of line indices.
    Returns dict of rates + counts."""
    n = 0
    first = 0
    last = 0
    interior = 0
    for rec, lis in zip(testable_records, lis_per_ins):
        L = rec["L"]
        for li in lis:
            n += 1
            if li == 0:
                first += 1
            elif li == L - 1:
                last += 1
            else:
                interior += 1
    if n == 0:
        return {"n": 0, "peripheral": 0.0, "heading": 0.0, "colophon": 0.0, "interior": 0.0,
                "first": 0, "last": 0, "interior_n": 0}
    return {
        "n": n,
        "peripheral": (first + last) / n,
        "heading": first / n,
        "colophon": last / n,
        "interior": interior / n,
        "first": first,
        "last": last,
        "interior_n": interior,
    }


def observed_lis(testable_records):
    return [list(rec["marker_lis"]) for rec in testable_records]


def null_reshuffle(testable_records, rng):
    """Re-place each marker's li uniformly in {0,...,L-1} per inscription."""
    out = []
    for rec in testable_records:
        L = rec["L"]
        k = len(rec["marker_lis"])
        out.append([rng.randrange(L) for _ in range(k)])
    return out


def expected_peripheral_rate(testable_records):
    """Marker-weighted mean of 2/L (for L>=2). For L==1, 2/L would be 2 but a single
    line is both first and last; here L>=3 always so 2/L in (0,1]."""
    total_w = 0.0
    n = 0
    for rec in testable_records:
        L = rec["L"]
        k = len(rec["marker_lis"])
        # peripheral probability for a uniform draw on {0..L-1}: 2/L (first or last)
        p = 2.0 / L
        total_w += p * k
        n += k
    return total_w / n if n else 0.0


def perm_test(testable_records, n_perm=1000, seed=12345, metrics=("peripheral",)):
    """Run permutation test for requested metrics. Returns observed rates, null mean,
    perm p (one-sided enrichment) per metric, plus depletion p."""
    rng = random.Random(seed)
    obs_lis = observed_lis(testable_records)
    obs_rates = rates_from_lis(testable_records, obs_lis)
    out = {}
    null_sums = {m: 0.0 for m in metrics}
    ge_counts = {m: 0 for m in metrics}
    le_counts = {m: 0 for m in metrics}  # for depletion (opposite tail)
    for _ in range(n_perm):
        nl = null_reshuffle(testable_records, rng)
        r = rates_from_lis(testable_records, nl)
        for m in metrics:
            null_sums[m] += r[m]
            if r[m] >= obs_rates[m]:
                ge_counts[m] += 1
            if r[m] <= obs_rates[m]:
                le_counts[m] += 1
    for m in metrics:
        out[m] = {
            "obs": obs_rates[m],
            "null_mean": null_sums[m] / n_perm,
            "perm_p_enrich": ge_counts[m] / n_perm,
            "perm_p_deplete": le_counts[m] / n_perm,
        }
    out["_obs_rates"] = obs_rates
    out["_n_perm"] = n_perm
    return out


def per_site(testable_records, n_perm=1000, seed=999, min_markers=10):
    """Per-site peripheral rate + null + perm p + direction."""
    by_site = defaultdict(list)
    for rec in testable_records:
        by_site[rec["site"]].append(rec)
    results = []
    for site, recs in by_site.items():
        n = sum(len(r["marker_lis"]) for r in recs)
        if n < min_markers:
            continue
        pt = perm_test(recs, n_perm=n_perm, seed=seed)
        obs = pt["peripheral"]["obs"]
        p = pt["peripheral"]["perm_p_enrich"]
        results.append({
            "site": site, "n": n, "peripheral_obs": obs,
            "peripheral_null_mean": pt["peripheral"]["null_mean"],
            "perm_p": p,
            "direction": "enriched" if obs > pt["peripheral"]["null_mean"] else "depleted",
            "sig": p <= 0.05,
        })
    return results


def leave_one_site_out(testable_records, exclude_site, n_perm=1000, seed=4242):
    recs = [r for r in testable_records if r["site"] != exclude_site]
    if not recs:
        return None
    pt = perm_test(recs, n_perm=n_perm, seed=seed)
    return {"exclude": exclude_site, "n": sum(len(r["marker_lis"]) for r in recs),
            "peripheral_obs": pt["peripheral"]["obs"],
            "peripheral_null_mean": pt["peripheral"]["null_mean"],
            "perm_p": pt["peripheral"]["perm_p_enrich"]}


# ---------- POSITIVE CONTROL (synthetic) ----------

def synth_detect_corpus(n_ins=60, seed=11):
    """Every marker on FIRST or LAST content-line."""
    rng = random.Random(seed)
    recs = []
    for i in range(n_ins):
        L = rng.randint(3, 8)
        k = rng.randint(1, 3)
        lis = [rng.choice([0, L - 1]) for _ in range(k)]
        recs.append({"id": f"SYN_D_{i}", "site": "SYN", "L": L, "marker_lis": lis})
    return recs


def synth_uniform_corpus(n_ins=60, seed=None, draw=None):
    """Markers placed uniformly at random among content-lines."""
    rng = random.Random(draw if draw is not None else seed)
    recs = []
    for i in range(n_ins):
        L = rng.randint(3, 8)
        k = rng.randint(1, 3)
        lis = [rng.randrange(L) for _ in range(k)]
        recs.append({"id": f"SYN_U_{i}", "site": "SYN", "L": L, "marker_lis": lis})
    return recs


def positive_control(n_perm=500, detect_seed=11, n_fp_draws=20, fp_base_seed=5000):
    """(a) DETECT: peripheral enrichment flagged (perm p<=0.05).
    (b) FALSE-POSITIVE: uniform placement rejected <=0.10 across >=20 draws."""
    # (a) detect
    det_recs = synth_detect_corpus(seed=detect_seed)
    det_pt = perm_test(det_recs, n_perm=n_perm, seed=777)
    det_p = det_pt["peripheral"]["perm_p_enrich"]
    detect_flag = det_p <= 0.05
    # (b) false-positive
    rejections = 0
    for d in range(n_fp_draws):
        urecs = synth_uniform_corpus(draw=fp_base_seed + d)
        upt = perm_test(urecs, n_perm=n_perm, seed=fp_base_seed + d)
        if upt["peripheral"]["perm_p_enrich"] <= 0.05:
            rejections += 1
    fp_rate = rejections / n_fp_draws
    fp_ok = fp_rate <= 0.10
    passed = detect_flag and fp_ok
    return {
        "pc_verdict": "PASSED" if passed else "FAILED",
        "detect_p": det_p,
        "detect_flag": detect_flag,
        "false_pos_rate": fp_rate,
        "fp_ok": fp_ok,
        "n_fp_draws": n_fp_draws,
        "pc_is_synthetic": True,
    }


# ---------- SELF-CHECK ----------

def self_check():
    """Validate line-reshuffle null on a synthetic; confirm null-mean ~= marker-weighted mean of 2/L."""
    rng = random.Random(2024)
    # synthetic testable records
    recs = []
    for i in range(200):
        L = rng.randint(3, 10)
        k = rng.randint(1, 4)
        # place markers with a slight peripheral bias to ensure observed != null trivially
        lis = []
        for _ in range(k):
            if rng.random() < 0.6:
                lis.append(rng.choice([0, L - 1]))
            else:
                lis.append(rng.randrange(L))
        recs.append({"id": f"SC_{i}", "site": "SC", "L": L, "marker_lis": lis})
    exp_rate = expected_peripheral_rate(recs)
    pt = perm_test(recs, n_perm=2000, seed=31)
    null_mean = pt["peripheral"]["null_mean"]
    diff = abs(null_mean - exp_rate)
    ok = diff < 0.02  # null mean should match marker-weighted 2/L closely
    print(f"[self-check] expected (weighted 2/L) = {exp_rate:.4f}")
    print(f"[self-check] null mean (2000 perm)   = {null_mean:.4f}")
    print(f"[self-check] |diff| = {diff:.4f}  -> {'OK' if ok else 'FAIL'}")
    # also confirm null on a uniform-placement corpus gives null_mean ~= obs
    urecs = synth_uniform_corpus(n_ins=200, draw=77)
    uexp = expected_peripheral_rate(urecs)
    upt = perm_test(urecs, n_perm=2000, seed=88)
    uobs = upt["peripheral"]["obs"]
    unull = upt["peripheral"]["null_mean"]
    uok = abs(uobs - unull) < 0.03 and abs(unull - uexp) < 0.02
    print(f"[self-check uniform] obs={uobs:.4f} null={unull:.4f} exp={uexp:.4f} -> {'OK' if uok else 'FAIL'}")
    return ok and uok


if __name__ == "__main__":
    print("=== EPOCH-062 machinery self-check ===")
    sc = self_check()
    print(f"self_check overall: {'PASS' if sc else 'FAIL'}")
    print()
    print("=== positive control (synthetic) ===")
    pc = positive_control(n_perm=500)
    print(json.dumps(pc, indent=2))
