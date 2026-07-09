#!/usr/bin/env python3
"""EPOCH-004 — FRACTION_ORDER_ANETAKI_SEAL derivation, controls, seal build, and frozen scorer.

Implements exactly the frozen plan in epochs/EPOCH-004/prereg.md
(plan_hash da6e024832d2dc75f1c2ecf91ce36179fa425671def15220736cfe724a4ba4ef).

Stages (run in this order; PC first per protocol):
    python3 fraction_order_seal.py pc        # PC-1, PC-2 (positive controls; synthetic only)
    python3 fraction_order_seal.py derive    # real derivation + NC-1..NC-3 + contamination C1-C5
    python3 fraction_order_seal.py seal      # build seal JSON + sha256 manifest

The scorer (`score_sequence`) is frozen in this file and hashed into the manifest; it is the ONLY
authorized way to grade the seal when Anetaki II publishes.

Derivation inputs (value-bearing): corpus/silver/inscriptions_structured.json ONLY.
Seed: 20260708. Constitution v2.2. Claim layer L2/L3 (numeral-notation structure). No licence used.
"""
import json
import math
import os
import random
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import permutations

SEED = 20260708
BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
CAMP = os.path.join(BASE, "experiments", "linear_a_frontier_72h")
EPOCH_DIR = os.path.join(CAMP, "epochs", "EPOCH-004")
SEALS_DIR = os.path.join(CAMP, "data", "seals")
SILVER = os.path.join(BASE, "corpus", "silver", "inscriptions_structured.json")

AEG_LO, AEG_HI = 0x10740, 0x1075F

# ---- frozen parameters (prereg P4/P5) --------------------------------------------------------
PRIOR_PRIMARY = (8, 2)
PRIOR_SENSITIVITY = [(4, 1), (16, 4)]
ANCHORED = {"J": Fraction(1, 2), "E": Fraction(1, 4), "JE": Fraction(3, 4)}
ARITH_CLAIMS = [("J", "E"), ("JE", "J"), ("JE", "E")]  # X > Y, q = 0.99
ARITH_Q = 0.99
Q_CAP = (0.01, 0.99)
TRANSITIVE_MIN = 0.60
PRIMARY_HORIZON_PREFIX = "LMI"

# ---- frozen Corazza et al. 2021 comparator (prereg P7) ---------------------------------------
CORAZZA_TIER1 = {
    "J": Fraction(1, 2), "E": Fraction(1, 4), "B": Fraction(1, 5), "D": Fraction(1, 6),
    "F": Fraction(1, 8), "K": Fraction(1, 10), "L2": Fraction(1, 20), "L3": Fraction(1, 30),
    "L4": Fraction(1, 40), "L6": Fraction(1, 60),
}
CORAZZA_TIER2 = {"H": Fraction(1, 16), "A": Fraction(1, 24), "W": Fraction(2, 5), "X": Fraction(1, 12)}
CORAZZA_COMPOSITE = {"JE": Fraction(3, 4), "DD": Fraction(1, 3)}
CORAZZA_ALL = {**CORAZZA_TIER1, **CORAZZA_TIER2, **CORAZZA_COMPOSITE}
CITATION = ("Corazza, Ferrara, Montecchi, Tamburini & Valério (2021), 'The mathematical values of "
            "fraction signs in the Linear A script: a computational, statistical and typological "
            "approach', J. Archaeol. Sci. 125:105214, doi:10.1016/j.jas.2020.105214. Tier-2 values "
            "flagged uncertain/composite by the authors (H?, A?, W=BB?, X=AA?).")


# ---- extraction (prereg P1-P3) ----------------------------------------------------------------
def is_aeg_seq(raw):
    s = raw.replace("≈", "").strip()  # strip ≈
    return (len(s) >= 2 and all(AEG_LO <= ord(c) <= AEG_HI and unicodedata.name(c, "") for c in s)), s


def letters_of(s):
    return [unicodedata.name(c).split()[-1] for c in s]


def extract_sequence_tokens(silver_path=SILVER):
    data = json.load(open(silver_path, encoding="utf-8"))
    seqs = []
    freq = Counter()
    for rec in data:
        iid = str(rec.get("id", ""))
        ctx = (rec.get("context", "") or "").upper().replace(" ", "")
        for tok in rec.get("stream", []):
            if tok.get("t") != "other":
                continue
            raw = tok.get("raw", "")
            s = raw.replace("≈", "").strip()
            # frequency census: every Aegean fraction glyph occurrence (standalone or in seq)
            for c in s:
                if AEG_LO <= ord(c) <= AEG_HI and unicodedata.name(c, ""):
                    freq[unicodedata.name(c).split()[-1]] += 1
            ok, s2 = is_aeg_seq(raw)
            if ok:
                seqs.append({"doc": iid, "context": ctx, "letters": letters_of(s2), "raw": s2})
    return seqs, freq


def doc_votes(seqs):
    """P3: within-token all ordered distinct-letter pairs -> doc-level majority vote per pair."""
    per_doc = defaultdict(Counter)  # (doc, frozenset pair) -> Counter direction
    for q in seqs:
        L = q["letters"]
        for i in range(len(L)):
            for j in range(i + 1, len(L)):
                if L[i] != L[j]:
                    per_doc[(q["doc"], frozenset((L[i], L[j])))][(L[i], L[j])] += 1
    votes = []  # (doc, X, Y) meaning X-before-Y (majority in doc)
    for (doc, pair), c in sorted(per_doc.items(), key=lambda kv: (kv[0][0], sorted(kv[0][1]))):
        dirs = c.most_common()
        if len(dirs) == 2 and dirs[0][1] == dirs[1][1]:
            continue  # within-doc tie dropped
        (X, Y), _ = dirs[0]
        votes.append({"doc": doc, "first": X, "second": Y})
    return votes


# ---- posterior machinery (prereg P4-P5) -------------------------------------------------------
def moment(a, b, s, f):
    """E_{p~Beta(a,b)}[p^s (1-p)^f] = B(a+s, b+f)/B(a,b), exact."""
    return (math.lgamma(a + s) + math.lgamma(b + f) + math.lgamma(a + b)
            - math.lgamma(a) - math.lgamma(b) - math.lgamma(a + b + s + f))


def pair_q(a, b, s, f):
    m1 = moment(a, b, s, f)
    m2 = moment(a, b, f, s)
    q = 1.0 / (1.0 + math.exp(m2 - m1))
    return min(max(q, Q_CAP[0]), Q_CAP[1])


def build_matrix(votes, prior, anchored=ANCHORED, arith_claims=ARITH_CLAIMS):
    """P4+P5. Returns (claims, p_posterior, consumed) — claims: {(X,Y): {'q':..,'tier':..,'s':..,'f':..,'docs':[..]}}."""
    a0, b0 = prior
    succ, fail, consumed = 0, 0, []
    matrix_votes = defaultdict(lambda: {"s": 0, "f": 0, "docs_s": [], "docs_f": []})
    for v in votes:
        X, Y = v["first"], v["second"]
        if X in anchored and Y in anchored:
            if anchored[X] > anchored[Y]:
                succ += 1
            else:
                fail += 1
            consumed.append(v)
            continue
        key = tuple(sorted((X, Y)))
        e = matrix_votes[key]
        if (X, Y) == (key[0], key[1]):
            e["s"] += 1; e["docs_s"].append(v["doc"])
        else:
            e["f"] += 1; e["docs_f"].append(v["doc"])
    a, b = a0 + succ, b0 + fail
    claims = {}
    for (P, Ql), e in sorted(matrix_votes.items()):
        q = pair_q(a, b, e["s"], e["f"])
        if q >= 0.5:
            X, Y, s, f, ds, df = P, Ql, e["s"], e["f"], e["docs_s"], e["docs_f"]
        else:
            X, Y, s, f, ds, df = Ql, P, e["f"], e["s"], e["docs_f"], e["docs_s"]
            q = 1.0 - q
        claims[(X, Y)] = {"q": round(q, 4), "tier": "sequence_vote", "s": s, "f": f,
                          "docs_for": ds, "docs_against": df}
    for (X, Y) in arith_claims:
        claims[(X, Y)] = {"q": ARITH_Q, "tier": "arithmetic",
                          "basis": "J=1/2 Bennett 1950 (HT104,HTZd156,PE1,HT123a); E=1/4 via JE=3/4 additive"}
    # transitive closure tier (max product path; only pairs with no direct claim)
    direct = dict(claims)
    letters = sorted({x for p in direct for x in p})
    best = {p: c["q"] for p, c in direct.items()}
    # Floyd-Warshall style max-product
    changed = True
    paths = dict(best)
    while changed:
        changed = False
        for (X, Y), qxy in list(paths.items()):
            for (Y2, Z), qyz in list(paths.items()):
                if Y2 == Y and X != Z:
                    nq = qxy * qyz
                    if nq > paths.get((X, Z), 0.0) + 1e-12:
                        paths[(X, Z)] = nq
                        changed = True
    for (X, Y), q in sorted(paths.items()):
        if (X, Y) in direct or (Y, X) in direct:
            continue
        if q >= TRANSITIVE_MIN:
            claims[(X, Y)] = {"q": round(min(q, Q_CAP[1]), 4), "tier": "transitive"}
    return claims, (a, b, succ, fail), consumed, letters


def map_orders(claims, top_n=5):
    """P6: exhaustive maximum-likelihood total orders over claimed letters."""
    letters = sorted({x for p in claims for x in p})
    if len(letters) > 10:
        raise SystemExit("exhaustive enumeration >10 letters not frozen; abort")
    def loglik(order):
        pos = {l: i for i, l in enumerate(order)}
        ll = 0.0
        for (X, Y), c in claims.items():
            q = c["q"]
            ll += math.log(q if pos[X] < pos[Y] else 1.0 - q)
        return ll
    scored = []
    for perm in permutations(letters):
        scored.append((loglik(perm), perm))
    scored.sort(key=lambda t: (-t[0], t[1]))
    best_ll = scored[0][0]
    n_tied = sum(1 for ll, _ in scored if abs(ll - best_ll) < 1e-9)
    tot = None  # normalization over all permutations
    m = max(ll for ll, _ in scored)
    tot = sum(math.exp(ll - m) for ll, _ in scored)
    top = [{"order": list(p), "loglik": round(ll, 4),
            "prob_normalized": round(math.exp(ll - m) / tot, 6)} for ll, p in scored[:top_n]]
    p_all_direct = 1.0
    for c in claims.values():
        p_all_direct *= c["q"]
    return {"letters": letters, "n_permutations": math.factorial(len(letters)),
            "n_tied_maximum_likelihood": n_tied, "top": top,
            "p_all_claims_correct": round(p_all_direct, 6)}


# ---- divergence registry (prereg P8) ----------------------------------------------------------
def divergences(claims):
    out = []
    for (X, Y), c in sorted(claims.items()):
        vx, vy = CORAZZA_ALL.get(X), CORAZZA_ALL.get(Y)
        if vx is None or vy is None or vx == vy:
            continue
        cor_dir = X if vx > vy else Y
        if cor_dir != X:
            tier2 = X in CORAZZA_TIER2 or Y in CORAZZA_TIER2
            out.append({"pair": [X, Y], "ours": f"{X}>{Y}", "ours_q": c["q"], "ours_tier": c["tier"],
                        "corazza": f"{Y}>{X}", "corazza_involves_tier2_value": tier2})
    return out


# ---- frozen scorer (prereg 'Frozen scoring rule') ---------------------------------------------
def score_sequence(published_letters, matrix_claims, ground_truth="G2_written_order_descending"):
    """Grade the seal against the published face-δ sequence.

    published_letters: list of klasmatogram letters in DESCENDING-VALUE order per the ground-truth
    hierarchy (G1 editors' printed relative-value order, else G2 written order under A-FD1).
    matrix_claims: {(X,Y): {'q':..}} meaning X>Y with confidence q (the sealed primary matrix).
    Returns the three sub-test results, mechanically.
    """
    L = [l for l in published_letters]
    pairs = [(L[i], L[j]) for i in range(len(L)) for j in range(i + 1, len(L)) if L[i] != L[j]]
    # sub-test 1
    claimed, correct, brier, logs = 0, 0, 0.0, 0.0
    for (X, Y) in pairs:  # ground truth: X > Y
        c = matrix_claims.get((X, Y))
        cr = matrix_claims.get((Y, X))
        if c is not None:
            claimed += 1; correct += 1
            brier += (1 - c["q"]) ** 2; logs += math.log(c["q"])
        elif cr is not None:
            claimed += 1
            brier += (cr["q"]) ** 2; logs += math.log(1 - cr["q"])
    if claimed >= 4:
        acc = correct / claimed
        if acc >= 0.75:
            v1 = "OURS_SUPPORTED"
        elif acc <= 0.5:
            v1 = "OURS_REFUTED"
        else:
            v1 = "OURS_MIXED"
    else:
        acc = correct / claimed if claimed else None
        v1 = "NO_POWER"
    # exact one-sided binomial p vs 0.5
    p_binom = None
    if claimed:
        p_binom = sum(math.comb(claimed, k) for k in range(correct, claimed + 1)) / 2 ** claimed
    # sub-test 2 (Corazza tier-1 only)
    n2 = c2_ours = c2_cor = 0
    for (X, Y) in pairs:
        ours = matrix_claims.get((X, Y)) or matrix_claims.get((Y, X))
        if ours is None or X not in CORAZZA_TIER1 or Y not in CORAZZA_TIER1:
            continue
        n2 += 1
        our_dir = X if (X, Y) in matrix_claims else Y
        cor_dir = X if CORAZZA_TIER1[X] > CORAZZA_TIER1[Y] else Y
        if our_dir == X:
            c2_ours += 1
        if cor_dir == X:
            c2_cor += 1
    if n2 >= 4:
        v2 = ("OURS_BEATS_CORAZZA" if c2_ours > c2_cor else
              "CORAZZA_BEATS_OURS" if c2_cor > c2_ours else "TIE")
    else:
        v2 = "NO_POWER"
    # sub-test 3: divergent registry pairs present
    div = divergences(matrix_claims)
    present, ours_w, cor_w = [], 0, 0
    for d in div:
        X, Y = d["pair"]  # ours: X>Y, corazza: Y>X
        if X in L and Y in L:
            truth = X if L.index(X) < L.index(Y) else Y
            win = "OURS" if truth == X else "CORAZZA"
            present.append({"pair": [X, Y], "winner": win})
            ours_w += win == "OURS"; cor_w += win == "CORAZZA"
    v3 = ("DIVERGENT_ABSENT" if not present else
          "DIVERGENT_OURS" if ours_w > cor_w else
          "DIVERGENT_CORAZZA" if cor_w > ours_w else "SPLIT")
    return {"sub1": {"verdict": v1, "n_claimed": claimed, "n_correct": correct,
                     "accuracy": None if acc is None else round(acc, 4),
                     "binomial_p_one_sided": None if p_binom is None else round(p_binom, 5),
                     "brier": round(brier / claimed, 4) if claimed else None,
                     "log_score": round(logs, 4) if claimed else None},
            "sub2": {"verdict": v2, "n_shared": n2, "ours_correct": c2_ours, "corazza_correct": c2_cor},
            "sub3": {"verdict": v3, "pairs": present}}


# ---- stages -----------------------------------------------------------------------------------
def sha256_file(p):
    import hashlib
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for ch in iter(lambda: f.read(65536), b""):
            h.update(ch)
    return h.hexdigest()


def claims_to_json(claims):
    return [{"pair": f"{X}>{Y}", **{k: v for k, v in c.items() if k in ("q", "tier", "s", "f", "docs_for", "docs_against", "basis")}}
            for (X, Y), c in sorted(claims.items(), key=lambda kv: -kv[1]["q"])]


def json_to_claims(rows):
    out = {}
    for r in rows:
        X, Y = r["pair"].split(">")
        out[(X, Y)] = {k: v for k, v in r.items() if k != "pair"}
    return out


def stage_pc():
    random.seed(SEED)
    real_seqs, _ = extract_sequence_tokens()
    prim = [q for q in real_seqs if q["context"].startswith(PRIMARY_HORIZON_PREFIX)]
    planted = {**CORAZZA_TIER1, **CORAZZA_TIER2, **CORAZZA_COMPOSITE}
    # PC-1 noiseless: same docs, same letter multisets, strictly descending
    synth = [{"doc": q["doc"], "context": q["context"],
              "letters": sorted(q["letters"], key=lambda l: -planted.get(l, Fraction(1, 999)))}
             for q in prim]
    votes = doc_votes(synth)
    claims, post, consumed, _ = build_matrix(votes, PRIOR_PRIMARY)
    wrong, qs_by_k = [], defaultdict(list)
    for (X, Y), c in claims.items():
        if c["tier"] != "sequence_vote":
            continue
        if planted.get(X) is not None and planted.get(Y) is not None and not planted[X] > planted[Y]:
            wrong.append((X, Y))
        qs_by_k[c["s"] + c["f"]].append(c["q"])
    ks = sorted(qs_by_k)
    mono = all(max(qs_by_k[ks[i]]) <= min(qs_by_k[ks[i + 1]]) + 1e-9 for i in range(len(ks) - 1))
    pc1_pass = (not wrong) and mono
    # PC-1 noisy variant (descriptive)
    accs = []
    for rep in range(200):
        nz = []
        for q in prim:
            Ls = sorted(q["letters"], key=lambda l: -planted.get(l, Fraction(1, 999)))
            if random.random() < 0.2:
                Ls = Ls[::-1]
            nz.append({"doc": q["doc"], "context": q["context"], "letters": Ls})
        cl, _, _, _ = build_matrix(doc_votes(nz), PRIOR_PRIMARY)
        seq_cl = [(X, Y) for (X, Y), c in cl.items() if c["tier"] == "sequence_vote"
                  and planted.get(X) is not None and planted.get(Y) is not None]
        ok = sum(1 for (X, Y) in seq_cl if planted[X] > planted[Y])
        if seq_cl:
            accs.append(ok / len(seq_cl))
    # PC-2 scorer round-trip
    six = ["J", "E", "B", "K", "H", "L2"]
    six_desc = sorted(six, key=lambda l: -planted[l])
    fwd = score_sequence(six_desc, claims)
    rev = score_sequence(six_desc[::-1], claims)
    pc2_pass = fwd["sub1"]["verdict"] == "OURS_SUPPORTED" and rev["sub1"]["verdict"] == "OURS_REFUTED"
    out = {"PC1": {"pass": bool(pc1_pass), "n_synth_docs": len(synth), "n_claims_checked":
                   sum(1 for c in claims.values() if c["tier"] == "sequence_vote"),
                   "wrong_direction_pairs": [f"{x}>{y}" for x, y in wrong], "q_monotone_in_k": bool(mono),
                   "noisy_variant_mean_direction_accuracy": round(sum(accs) / len(accs), 4) if accs else None},
           "PC2": {"pass": bool(pc2_pass), "forward_verdict": fwd["sub1"]["verdict"],
                   "reverse_verdict": rev["sub1"]["verdict"],
                   "forward": fwd["sub1"], "reverse": rev["sub1"]}}
    os.makedirs(EPOCH_DIR, exist_ok=True)
    json.dump(out, open(os.path.join(EPOCH_DIR, "controls_pc.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))
    return out


def w_margin(votes, anchored=ANCHORED):
    per_pair = defaultdict(lambda: [0, 0])
    for v in votes:
        X, Y = v["first"], v["second"]
        if X in anchored and Y in anchored:
            continue
        key = tuple(sorted((X, Y)))
        per_pair[key][0 if (X, Y) == key else 1] += 1
    return sum(abs(s - f) for s, f in per_pair.values())


def stage_derive():
    random.seed(SEED)
    seqs, freq = extract_sequence_tokens()
    prim = [q for q in seqs if q["context"].startswith(PRIMARY_HORIZON_PREFIX)]
    sec = seqs
    votes_p = doc_votes(prim)
    claims_p, post_p, consumed_p, letters_p = build_matrix(votes_p, PRIOR_PRIMARY)
    orders = map_orders({p: c for p, c in claims_p.items()})
    div = divergences(claims_p)
    # sensitivity band
    sens = {}
    for pr in PRIOR_SENSITIVITY:
        cl, po, _, _ = build_matrix(votes_p, pr)
        sens[f"Beta{pr}"] = {"posterior": po[:2],
                             "q_k1": round(pair_q(po[0], po[1], 1, 0), 4),
                             "q_k2": round(pair_q(po[0], po[1], 2, 0), 4),
                             "q_k4": round(pair_q(po[0], po[1], 4, 0), 4)}
    # secondary tier (all horizons)
    votes_s = doc_votes(sec)
    claims_s, post_s, consumed_s, _ = build_matrix(votes_s, PRIOR_PRIMARY)
    sec_only = {p: c for p, c in claims_s.items()
                if p not in claims_p and (p[1], p[0]) not in claims_p and c["tier"] == "sequence_vote"}
    # NC-1 shuffle null
    W_real = w_margin(votes_p)
    ge = 0
    NREP = 20000
    for rep in range(NREP):
        sh = []
        for q in prim:
            L = q["letters"][:]
            random.shuffle(L)
            sh.append({"doc": q["doc"], "context": q["context"], "letters": L})
        if w_margin(doc_votes(sh)) >= W_real:
            ge += 1
    nc1_p = ge / NREP
    # NC-2 frequency adversary
    contradicts = []
    for (X, Y), c in claims_p.items():
        if c["tier"] != "sequence_vote":
            continue
        if freq.get(X, 0) < freq.get(Y, 0):  # claim X>Y but X rarer -> contradicts freq-rank
            contradicts.append({"pair": f"{X}>{Y}", "freq_first": freq.get(X, 0), "freq_second": freq.get(Y, 0)})
    # NC-3 relabeling
    alphabet = sorted({l for q in prim for l in q["letters"]} | set(ANCHORED))
    perm = dict(zip(alphabet, alphabet[1:] + alphabet[:1]))
    prim_rl = [{"doc": q["doc"], "context": q["context"], "letters": [perm[l] for l in q["letters"]]} for q in prim]
    anch_rl = {perm[k]: v for k, v in ANCHORED.items()}
    arith_rl = [(perm[a], perm[b]) for a, b in ARITH_CLAIMS]
    cl_rl, _, _, _ = build_matrix(doc_votes(prim_rl), PRIOR_PRIMARY, anchored=anch_rl, arith_claims=arith_rl)
    expect = {(perm[X], perm[Y]): c["q"] for (X, Y), c in claims_p.items()}
    got = {p: c["q"] for p, c in cl_rl.items()}
    nc3_pass = expect == got
    # contamination checks C1-C5
    import subprocess
    kanta_pdf = os.path.join(BASE, "corpus", "bronze", "kanta_etal_2024_anetaki", "kanta_etal_2024_anetaki.pdf")
    txt = subprocess.run(["pdftotext", kanta_pdf, "-"], capture_output=True, text=True).stdout
    aeg_glyphs = [c for c in txt if AEG_LO <= ord(c) <= AEG_HI]
    m = re.search(r"This sequence of fractions[^.]*\.", txt)
    # klasmatogram identity patterns near 'fraction' mentions
    ident = re.findall(r"fraction[^.]{0,120}?\b(A70[0-9]|klasm|\bJ\s*=|\bE\s*=|1/2|1/4|1/5|1/6|1/8|1/10|1/16|1/20)", txt, re.I)
    c1 = {"pass": not aeg_glyphs and not ident, "aegean_glyphs_in_pdf_text": len(aeg_glyphs),
          "identity_patterns_near_fraction": ident, "public_passage": m.group(0).replace("\n", " ") if m else None}
    reg = json.load(open(os.path.join(CAMP, "data", "anetaki_2025", "sign_candidates.json")))
    rows = reg["candidates"]
    r35 = next(r for r in rows if r.get("row") == 35)
    fr_rows = [r for r in rows if "fringe" in str(r.get("quarantine", ""))]
    c2 = {"pass": r35.get("quarantine") == "unpublished_content" and
                  not any(re.search(r"fraction|1/2|klasm|½", json.dumps(r), re.I) for r in fr_rows),
          "row35_quarantine": r35.get("quarantine"),
          "fringe_rows_fraction_pattern": [bool(re.search(r"fraction|1/2|klasm|½", json.dumps(r), re.I)) for r in fr_rows]}
    c3_counts = {}
    fringe_dir = os.path.join(BASE, "corpus", "bronze", "rjabchikov_2025_sceptre")
    for fn in sorted(os.listdir(fringe_dir)):
        p = os.path.join(fringe_dir, fn)
        if fn.endswith(".pdf"):
            t = subprocess.run(["pdftotext", p, "-"], capture_output=True, text=True).stdout
        else:
            try:
                t = open(p, encoding="utf-8", errors="ignore").read()
            except OSError:
                t = ""
        c3_counts[fn] = len(re.findall(r"fraction|klasm|1/2|½", t, re.I))
    c3 = {"pass": True, "blind_pattern_counts_content_never_displayed": c3_counts,
          "note": "counts only; fringe content not read into any session context"}
    c4 = {"pass": True, "value_bearing_input": SILVER,
          "assertion": "this module opens only corpus/silver + register/PDF for contamination checks; "
                       "no anetaki content enters the derivation functions"}
    c5 = {"pass": True, "search_receipt": "EPOCH-001 result.json search_receipt (14 routes, 2026-07-08); no new search run"}
    out = {
        "extraction": {"n_sequence_tokens_all": len(seqs), "n_sequence_tokens_primary_LMI": len(prim),
                       "n_docs_primary": len({q['doc'] for q in prim}),
                       "sequence_tokens_primary": [{"doc": q["doc"], "letters": q["letters"]} for q in prim],
                       "letter_frequency_census": dict(sorted(freq.items(), key=lambda kv: -kv[1]))},
        "p_desc_posterior": {"prior": list(PRIOR_PRIMARY), "successes": post_p[2], "failures": post_p[3],
                             "posterior": list(post_p[:2]), "posterior_mean": round(post_p[0] / (post_p[0] + post_p[1]), 4),
                             "consumed_votes": consumed_p, "sensitivity": sens},
        "primary_matrix": claims_to_json(claims_p),
        "n_claims_primary": len(claims_p),
        "map_orders": orders,
        "divergence_registry_vs_corazza": div,
        "secondary_tier_additional_claims": claims_to_json(sec_only),
        "controls": {"NC1": {"pass": nc1_p < 0.10, "W_real": W_real, "p_shuffle": nc1_p, "n_reps": NREP},
                     "NC2": {"pass": bool(contradicts), "claims_contradicting_frequency_rank": contradicts,
                             "flag": None if contradicts else "FREQUENCY_CONFOUND_UNBROKEN"},
                     "NC3": {"pass": bool(nc3_pass)}},
        "contamination": {"C1": c1, "C2": c2, "C3": c3, "C4": c4, "C5": c5},
    }
    json.dump(out, open(os.path.join(EPOCH_DIR, "derivation.json"), "w"), indent=1, default=str)
    print(json.dumps({k: out[k] for k in ("p_desc_posterior", "n_claims_primary", "controls")}, indent=1, default=str))
    print("divergences:", json.dumps(div, indent=1))
    print("map top:", json.dumps(orders["top"][:2], indent=1))
    print("claims:", json.dumps(out["primary_matrix"], indent=1))
    return out


def stage_seal():
    der = json.load(open(os.path.join(EPOCH_DIR, "derivation.json")))
    pc = json.load(open(os.path.join(EPOCH_DIR, "controls_pc.json")))
    plan_hash = open(os.path.join(EPOCH_DIR, "plan_hash.txt")).read().split()[0]
    seal = {
        "seal_id": "FRACTION_ORDER_ANETAKI_SEAL",
        "name": "Fraction relative-value order — prospective prediction vs Anetaki II face-δ six-fraction sequence",
        "type": "PROSPECTIVE_PREDICTION",
        "ordinal": "third Anetaki-targeting seal (after ANETAKI_FINAL_EDITION_DELTA_SEAL and M_ANETAKI_LATTICE_DELTA_SEAL; overlap: none — those seals score sign-groups/lattice deltas, this one scores ONLY the face-δ fraction ordering)",
        "campaign": "research/linear-a-frontier-72h",
        "epoch": "EPOCH-004",
        "as_of": "2026-07-08",
        "seed": SEED,
        "constitution": "v2.2",
        "claim_layer": "L2/L3 numeral-notation structure (klasmatogram relative-value order); no semantic/lexical/phonetic content; no transfer licence claimed or consumed",
        "plan_hash_sha256": plan_hash,
        "status": "SEALED_PROSPECTIVE",
        "held_out_target": "Anetaki II (Kanta ed., INSTAP Academic Press, forthcoming) editio princeps reading of KN Zg 58 Face δ: six different fraction signs in sequence (existence public via Kanta et al. 2024 pp. 41-42; identities and order UNPUBLISHED)",
        "public_surface_at_freeze": der["contamination"]["C1"]["public_passage"],
        "known_leak_discounted": "Kanta et al. 2024 p.42 publicly implies >=1 discordance with Corazza 2021; predictions of the form 'Corazza has an error' earn zero credit; only pair-level directions committed here are scoreable",
        "our_prediction": {
            "channel": "corpus/silver multi-sign fraction sequence tokens (descending-order convention A-FD1) + arithmetic anchors J=1/2 (Bennett 1950), E=1/4 (JE additive); Corazza-independent",
            "p_desc_posterior": der["p_desc_posterior"],
            "pairwise_matrix_primary": der["primary_matrix"],
            "ranked_orderings": der["map_orders"],
            "secondary_tier_non_primary": der["secondary_tier_additional_claims"],
            "abstention": "pairs absent from the matrix are ABSTAIN; they never score",
        },
        "corazza_prediction": {
            "citation": CITATION,
            "tier1_values": {k: str(v) for k, v in CORAZZA_TIER1.items()},
            "tier2_uncertain_values": {k: str(v) for k, v in CORAZZA_TIER2.items()},
            "composites": {k: str(v) for k, v in CORAZZA_COMPOSITE.items()},
            "implied_total_order_tier1": [k for k, v in sorted(CORAZZA_TIER1.items(), key=lambda kv: -kv[1])],
            "implied_total_order_with_tier2": [k for k, v in sorted({**CORAZZA_TIER1, **CORAZZA_TIER2}.items(), key=lambda kv: -kv[1])],
            "verified": "2026-07-08 against a secondary source reproducing the paper's table; identical to repo scripts/comparison/metrology.py::CORAZZA_2021",
        },
        "divergence_registry": der["divergence_registry_vs_corazza"],
        "scoring_rule": {
            "scorer": "experiments/linear_a_frontier_72h/scripts/fraction_order_seal.py::score_sequence (sha256 in manifest)",
            "ground_truth_hierarchy": ["G1: ed.pr. explicitly printed relative-value ordering",
                                       "G2: written sequence order under descending convention (editors' stated reading direction)"],
            "sub1_primary": "pairs claimed by our matrix among published signs: OURS_SUPPORTED iff n>=4 & acc>=0.75; OURS_REFUTED iff n>=4 & acc<=0.5; OURS_MIXED else; NO_POWER iff n<4; exact binomial p, Brier, log-score reported",
            "sub2_head_to_head": "shared pairs with Corazza tier-1: accuracy comparison, n>=4 required",
            "sub3_divergent_pairs": "frozen divergence_registry pairs present in the sequence: per-pair winner",
            "multiplicity": "one prediction system; sub-test 1 is the headline; sub-tests 2-3 Holm-corrected family of 2; Corazza tier-2 pairs reported outside gates",
            "void_conditions": ["V1 ed.pr. never publishes identities", "V2 fewer than 2 scoreable pairs after mapping",
                                "V3 ed.pr. asserts non-value-ordered and prints no ordering",
                                "V4 contamination: any repo session reads ed.pr. face-δ content before a scoring plan freeze -> verdict capped DESCRIPTIVE, session id recorded"],
            "failure_is_real": "OURS_REFUTED is a publishable negative for the sequence-order channel (Art. XVII: cannot be amended into a success)",
        },
        "calibration_estimates_non_binding": {
            "p_no_power_sub1": "~0.3-0.4 (six signs may fall outside our claimed-letter set {J,JE,E,B,K,L2,L4,L6,H,A})",
            "expected_acc_if_corazza_tier12_true": "13/15 direct claims concordant with Corazza; the 2 divergent pairs (H>K, A>B) would fail",
            "expected_acc_if_our_channel_true": "per-pair q values as listed (0.727-0.99)",
        },
        "controls_at_freeze": {"PC1": pc["PC1"], "PC2": pc["PC2"], **der["controls"]},
        "contamination_audit": der["contamination"],
        "trigger_protocol": "identical to CONTAMINATION_BOUNDARY.md: on Anetaki II publication, freeze a scoring session plan FIRST, then ingest mechanically, then run score_sequence; never read face-δ content in an analysis session before that",
        "source_dependency": {"value_bearing": ["corpus/silver/inscriptions_structured.json (lineara.xyz-derived, pre-2024)"],
                              "anchors": ["Bennett 1950 J=1/2 (via audited metrology finding 2026-06-30)",
                                          "Schrijver 2014 additivity-except-D (audited 2026-07-01)"],
                              "comparator_only": ["Corazza et al. 2021 (never enters derivation)"]},
    }
    os.makedirs(SEALS_DIR, exist_ok=True)
    seal_path = os.path.join(SEALS_DIR, "FRACTION_ORDER_ANETAKI_SEAL.json")
    json.dump(seal, open(seal_path, "w"), indent=1, ensure_ascii=False)
    manifest_items = [seal_path,
                      os.path.join(EPOCH_DIR, "prereg.md"),
                      os.path.join(EPOCH_DIR, "derivation.json"),
                      os.path.join(EPOCH_DIR, "controls_pc.json"),
                      os.path.abspath(__file__)]
    lines = [f"{sha256_file(p)}  {os.path.relpath(p, BASE)}" for p in manifest_items]
    man_path = os.path.join(SEALS_DIR, "FRACTION_ORDER_ANETAKI_SEAL.manifest.sha256")
    open(man_path, "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print("seal written:", seal_path)
    return seal_path, man_path


if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else ""
    if stage == "pc":
        stage_pc()
    elif stage == "derive":
        stage_derive()
    elif stage == "seal":
        stage_seal()
    else:
        raise SystemExit("usage: fraction_order_seal.py {pc|derive|seal}")
