#!/usr/bin/env python3
"""
EPOCH-063 machinery — Is Linear A's standalone-marker inventory POSITION-DIFFERENTIATED?
M1 = U+1076B (peripheral, E062-established). M2 = U+2014 em-dash (interior hypothesis).
Layer L2: anonymous token TYPES by document content-line index only. No sign value / reading.

Frozen nulls:
  H1 line-shuffle: re-place each M2 marker's li uniformly in {0..L-1} within its inscription,
                   preserving count + L. p_deplete = frac(null_peripheral <= observed).
  H2 relabel-contrast: pool all M1+M2 (li,L) records, relabel which are M1 vs M2 preserving
                       the two counts, recompute d = periph(M1)-periph(M2).
                       perm p = frac(null d >= observed d).
"""
import json, sys, random, hashlib
from collections import Counter

M1_RAW = "\U0001076b"   # U+1076B
M2_RAW = "\u2014"       # em-dash "—"
CONTENT = {"word", "num", "other"}

def parse_content_lines(stream):
    """Return list of content-lines; each is list of content tokens. div does NOT flush."""
    lines = []
    cur = []
    for tok in stream:
        t = tok.get("t")
        if t == "nl":
            lines.append(cur); cur = []
        elif t in CONTENT:
            cur.append(tok)
        # div / others ignored structurally (do not flush)
    lines.append(cur)
    # drop trailing empties? Keep all; but content-lines are non-empty by definition for indexing.
    # We index only non-empty content-lines.
    return [ln for ln in lines if len(ln) > 0]

def is_m1(tok):
    return tok.get("t") == "other" and M1_RAW in tok.get("raw", "")

def is_m2(tok):
    return tok.get("t") == "other" and M2_RAW in tok.get("raw", "")

def collect_markers(inscriptions):
    """For each testable inscription (L>=3 with >=1 target marker), emit marker records.
    Returns list of dicts: {id, site, L, li, kind} for M1 and M2 markers."""
    recs = []
    for ins in inscriptions:
        stream = ins.get("stream", [])
        lines = parse_content_lines(stream)
        L = len(lines)
        if L < 3:
            continue
        # find marker positions
        local = []
        for li, ln in enumerate(lines):
            for tok in ln:
                if is_m1(tok):
                    local.append((li, "M1"))
                elif is_m2(tok):
                    local.append((li, "M2"))
        if not local:
            continue
        for li, kind in local:
            recs.append({"id": ins.get("id"), "site": ins.get("site", "?"),
                         "L": L, "li": li, "kind": kind})
    return recs

def peripheral_rate(recs):
    if not recs: return 0.0
    return sum(1 for r in recs if r["li"] == 0 or r["li"] == r["L"]-1) / len(recs)

def heading_rate(recs):
    if not recs: return 0.0
    return sum(1 for r in recs if r["li"] == 0) / len(recs)

def interior_rate(recs):
    if not recs: return 0.0
    return sum(1 for r in recs if 0 < r["li"] < r["L"]-1) / len(recs)

def expected_periph_weighted(recs):
    """marker-weighted mean of 2/L (for L>=3)."""
    if not recs: return 0.0
    return sum(2.0/r["L"] for r in recs) / len(recs)

# ---------- H1: line-shuffle null for one marker kind ----------
def h1_lineshuffle(recs, n_draws=2000, seed=63001, direction="deplete"):
    """Within each inscription, re-place each marker's li uniformly in {0..L-1}.
    Returns (obs_periph, null_mean, p_deplete, p_enrich, heading_obs, heading_null_mean, heading_p_deplete)."""
    rng = random.Random(seed)
    obs = peripheral_rate(recs)
    # group by inscription id
    by_ins = {}
    for r in recs:
        by_ins.setdefault(r["id"], []).append(r)
    null_periphs = []
    for _ in range(n_draws):
        tot = 0
        for iid, lst in by_ins.items():
            L = lst[0]["L"]
            for _ in lst:
                li = rng.randint(0, L-1)
                if li == 0 or li == L-1:
                    tot += 1
        null_periphs.append(tot / len(recs))
    null_mean = sum(null_periphs)/len(null_periphs)
    p_deplete = sum(1 for x in null_periphs if x <= obs) / len(null_periphs)
    p_enrich  = sum(1 for x in null_periphs if x >= obs) / len(null_periphs)
    # heading
    hobs = heading_rate(recs)
    hnull = []
    for _ in range(n_draws):
        tot = 0
        for iid, lst in by_ins.items():
            L = lst[0]["L"]
            for _ in lst:
                li = rng.randint(0, L-1)
                if li == 0:
                    tot += 1
        hnull.append(tot/len(recs))
    hnull_mean = sum(hnull)/len(hnull)
    h_p_deplete = sum(1 for x in hnull if x <= hobs)/len(hnull)
    return obs, null_mean, p_deplete, p_enrich, hobs, hnull_mean, h_p_deplete

# ---------- H2: relabel-contrast null ----------
def h2_relabel_contrast(m1_recs, m2_recs, n_draws=2000, seed=63002):
    """Pool (li,L) records, relabel which are M1 vs M2 preserving counts.
    d = periph(M1) - periph(M2). perm p = frac(null d >= observed d)."""
    rng = random.Random(seed)
    obs_d = peripheral_rate(m1_recs) - peripheral_rate(m2_recs)
    pool = [(r["li"], r["L"]) for r in m1_recs] + [(r["li"], r["L"]) for r in m2_recs]
    n1 = len(m1_recs); n2 = len(m2_recs)
    null_ds = []
    for _ in range(n_draws):
        rng.shuffle(pool)
        a = pool[:n1]; b = pool[n1:n1+n2]
        pa = sum(1 for li,L in a if li==0 or li==L-1)/max(1,len(a))
        pb = sum(1 for li,L in b if li==0 or li==L-1)/max(1,len(b))
        null_ds.append(pa - pb)
    null_mean = sum(null_ds)/len(null_ds)
    p = sum(1 for x in null_ds if x >= obs_d)/len(null_ds)
    return obs_d, null_mean, p

# ---------- synthetic PC ----------
def synth_corpus_differentiated(n_ins=60, seed=100):
    """M1 ALWAYS peripheral, M2 ALWAYS interior. L>=3."""
    rng = random.Random(seed)
    inscs = []
    for i in range(n_ins):
        L = rng.randint(3, 7)
        # build stream: L content-lines separated by nl
        stream = []
        m1_at = rng.choice([0, L-1])
        m2_at = rng.randint(1, L-2)
        for li in range(L):
            if li == m1_at:
                stream.append({"t":"other","raw":M1_RAW})
            elif li == m2_at:
                stream.append({"t":"other","raw":M2_RAW})
            else:
                stream.append({"t":"word","signs":["X"]})
            if li < L-1:
                stream.append({"t":"nl"})
        inscs.append({"id":f"SYN_D{i}","site":"Synth","stream":stream})
    return inscs

def synth_corpus_redundant(seed=200):
    """BOTH M1,M2 at SAME peripheral positions."""
    rng = random.Random(seed)
    inscs = []
    for i in range(60):
        L = rng.randint(3, 7)
        stream = []
        # both at a peripheral line
        periph_choice = rng.choice([0, L-1])
        # place M1 and M2 on (possibly different) peripheral lines
        m1_at = rng.choice([0, L-1])
        m2_at = rng.choice([0, L-1])
        for li in range(L):
            if li == m1_at:
                stream.append({"t":"other","raw":M1_RAW})
            elif li == m2_at:
                stream.append({"t":"other","raw":M2_RAW})
            else:
                stream.append({"t":"word","signs":["X"]})
            if li < L-1:
                stream.append({"t":"nl"})
        inscs.append({"id":f"SYN_R{i}","site":"Synth","stream":stream})
    return inscs

def run_pc():
    """Returns dict with detect_ok, false_pos_rate, pc_verdict."""
    # (a) DETECT
    syn = synth_corpus_differentiated()
    recs = collect_markers(syn)
    m1 = [r for r in recs if r["kind"]=="M1"]
    m2 = [r for r in recs if r["kind"]=="M2"]
    m2_obs, m2_null, m2_p_deplete, _, _, _, _ = h1_lineshuffle(m2, n_draws=1000, seed=71001)
    d_obs, d_null, d_p = h2_relabel_contrast(m1, m2, n_draws=1000, seed=71002)
    detect_ok = (m2_p_deplete <= 0.05) and (d_p <= 0.05)
    # (b) FALSE-POSITIVE: across >=20 draws, fraction where contrast flagged (d_p<=0.05)
    fp = 0; ND = 20
    for k in range(ND):
        syn = synth_corpus_redundant(seed=900+k)
        recs = collect_markers(syn)
        m1 = [r for r in recs if r["kind"]=="M1"]
        m2 = [r for r in recs if r["kind"]=="M2"]
        _, _, fp_d_p = h2_relabel_contrast(m1, m2, n_draws=500, seed=82000+k)
        if fp_d_p <= 0.05:
            fp += 1
    fpr = fp/ND
    pc_passed = detect_ok and (fpr <= 0.10)
    return {"detect_ok": detect_ok, "false_pos_rate": fpr,
            "pc_verdict": "PASSED" if pc_passed else "FAILED",
            "pc_detect_m2_p_deplete": m2_p_deplete, "pc_detect_d_p": d_p,
            "pc_is_synthetic": True, "n_fp_draws": ND}

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "corpus/silver/inscriptions_structured.json"
    inscs = json.load(open(path))
    recs = collect_markers(inscs)
    m1 = [r for r in recs if r["kind"]=="M1"]
    m2 = [r for r in recs if r["kind"]=="M2"]
    print(f"== EPOCH-063 INSPECT ==")
    print(f"n_M1 testable = {len(m1)}; n_M2 testable = {len(m2)}")
    print(f"M1 peripheral = {peripheral_rate(m1):.4f} (E062: 0.691)")
    print(f"M2 peripheral = {peripheral_rate(m2):.4f}; heading={heading_rate(m2):.4f}; interior={interior_rate(m2):.4f}")
    m2_first = sum(1 for r in m2 if r["li"]==0)
    m2_last  = sum(1 for r in m2 if r["li"]==r["L"]-1)
    m2_int   = sum(1 for r in m2 if 0<r["li"]<r["L"]-1)
    print(f"M2 breakdown: first={m2_first} interior={m2_int} last={m2_last}")
    print(f"M2 expected periph (2/L weighted) = {expected_periph_weighted(m2):.4f}")
    # M2 per-site
    site_c = Counter(r["site"] for r in m2)
    print("M2 per-site:", dict(site_c))
    print()
    print("== H1: M2 line-shuffle ==")
    obs,null,pdep,penr,hobs,hnull,hpdep = h1_lineshuffle(m2, n_draws=2000, seed=63001)
    print(f"M2 periph obs={obs:.4f} null_mean={null:.4f} p_deplete={pdep:.4f} p_enrich={penr:.4f}")
    print(f"M2 heading obs={hobs:.4f} null_mean={hnull:.4f} p_deplete={hpdep:.4f}")
    print()
    print("== H2: relabel contrast ==")
    d_obs,d_null,d_p = h2_relabel_contrast(m1, m2, n_draws=2000, seed=63002)
    print(f"d = periph(M1)-periph(M2) = {d_obs:.4f}; null_mean={d_null:.4f}; perm_p={d_p:.4f}")
    print()
    print("== PC (synthetic) ==")
    pc = run_pc()
    print(json.dumps(pc, indent=2))
    print()
    # M2 cross-site
    print("== M2 cross-site (>=10) ==")
    by_site = {}
    for r in m2:
        by_site.setdefault(r["site"], []).append(r)
    n_sites_ge10 = 0
    for s, lst in by_site.items():
        if len(lst) >= 10:
            n_sites_ge10 += 1
            o,n,pd,_,_,_,_ = h1_lineshuffle(lst, n_draws=1000, seed=63010+hash(s)%1000)
            print(f"  {s}: n={len(lst)} periph_obs={o:.4f} null={n:.4f} p_deplete={pd:.4f}")
    print(f"n_sites_ge10 = {n_sites_ge10}")

if __name__ == "__main__":
    main()
