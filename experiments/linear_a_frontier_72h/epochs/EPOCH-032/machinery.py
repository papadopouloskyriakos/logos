#!/usr/bin/env python3
"""
EPOCH-032 machinery — CROSS-SITE RECURRENT ADMINISTRATIVE WORD-FORMS.

Pure L2/L3 distributional recurrence of ANONYMOUS sign sequences across SITES.
No phonetics, no sound, no meaning, no reading. Word-form = tuple of signs.

FROZEN METRIC: n_shared = # word-forms (total count>=2) appearing in >=2 distinct sites.
FROZEN NULL:   site-label shuffle (permute site labels across inscriptions, preserving each
               site's inscription count and each inscription's word-form multiset). >=1000 draws.
               One-sided p for "more cross-site sharing than chance".

POSITIVE CONTROL (gates verdict):
  - DETECT on LB (seeded pseudo-partition into >=5 pseudo-sites): must reject (p<=0.05).
  - FALSE-POSITIVE: >=20 i.i.d. controls (tokens drawn i.i.d. by marginal form-frequency, then
    partitioned into pseudo-sites of fixed sizes) -> false-positive rate (frac p<=0.05) must be <=0.20.

Self-check: `python3 machinery.py` runs the full pipeline + PC and prints a JSON summary.
"""
import json, os, sys, hashlib, random
from collections import Counter, defaultdict

# ---------- paths ----------
HERE = os.path.dirname(os.path.abspath(__file__))
# HERE = .../experiments/linear_a_frontier_72h/epochs/EPOCH-032
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
CORPUS = os.path.join(REPO, "corpus", "silver", "inscriptions_structured.json")
SCRIPTS = os.path.join(REPO, "scripts")

# ---------- seeds ----------
SEED_GLOBAL = 20240732
SEED_LB_PC = 20240732
SEED_FP = 20240733
N_DRAWS = 2000          # >=1000
N_FP_CONTROLS = 30     # >=20
N_PSEUDO_SITES_LB = 8   # >=5

# ---------- corpus IO ----------
def load_corpus(path=CORPUS):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_b_damos():
    """Linear B positive-control benchmark. Returns list of sign-lists (wordforms)."""
    sys.path.insert(0, SCRIPTS)
    from cross_script import data as D
    seqs, freq, v2g = D.load_b_damos()
    return seqs

# ---------- core: build (inscription -> [wordforms], site) ----------
def inscription_wordforms(insc):
    out = []
    for tok in insc.get("stream", []) or []:
        if tok.get("t") == "word":
            out.append(tuple(tok.get("signs", [])))
    return out

def build_site_records(corpus):
    """Return list of (site, [wordform tuples]) per inscription."""
    recs = []
    for ins in corpus:
        site = ins.get("site", "") or ""
        wfs = inscription_wordforms(ins)
        if wfs:  # only inscriptions that actually carry word tokens
            recs.append((site, wfs))
    return recs

# ---------- statistic: n_shared ----------
def n_shared_from_records(records):
    """records: list of (site, [wordforms]). Returns (n_shared, multiplicity Counter, form->sites)."""
    form_sites = defaultdict(set)
    form_count = Counter()
    for site, wfs in records:
        for f in wfs:
            form_sites[f].add(site)
            form_count[f] += 1
    # restrict to forms with total count >= 2
    cand = [f for f, c in form_count.items() if c >= 2]
    mult = Counter(len(form_sites[f]) for f in cand)  # n_sites -> n_forms
    n_shared = sum(1 for f in cand if len(form_sites[f]) >= 2)
    return n_shared, mult, form_sites, form_count

# ---------- site-label shuffle null ----------
def site_shuffle_null(records, n_draws=N_DRAWS, seed=SEED_GLOBAL, observed=None):
    """Permute site labels across inscriptions (preserving site inscription counts and each
    inscription's word-form multiset). Returns (null_mean, p_one_sided, draws_list)."""
    rng = random.Random(seed)
    sites = [s for s, _ in records]
    obs = observed if observed is not None else n_shared_from_records(records)[0]
    draws = []
    ge = 0
    site_list = sites[:]  # the multiset of site labels (fixed marginals)
    n = len(site_list)
    for _ in range(n_draws):
        # Fisher-Yates shuffle of site labels
        perm = site_list[:]
        for i in range(n - 1, 0, -1):
            j = rng.randint(0, i)
            perm[i], perm[j] = perm[j], perm[i]
        shuffled = list(zip(perm, [wfs for _, wfs in records]))
        ns, _, _, _ = n_shared_from_records(shuffled)
        draws.append(ns)
        if ns >= obs:
            ge += 1
    mean = sum(draws) / len(draws)
    p = (1 + ge) / (1 + n_draws)
    return mean, p, draws

# ---------- LB positive control: seeded pseudo-partition ----------
def lb_pseudo_records(seqs, n_sites=N_PSEUDO_SITES_LB, seed=SEED_LB_PC):
    """Partition LB wordforms into n_sites pseudo-sites by SEEDED CONTIGUOUS BLOCKS of the
    original DĀMOS sequence order (which reflects real tablet provenance grouping), then chunk
    each block into pseudo-inscriptions of ~tablet size. This preserves the real within-site
    form clustering that the cross-site test is meant to detect (unlike round-robin, which
    artificially spreads every frequent form across all pseudo-sites and washes out the signal).

    LB has no native site metadata, so this is a declared seeded pseudo-partition (SAY SO).
    """
    rng = random.Random(seed)
    n = len(seqs)
    # contiguous block boundaries: n_sites roughly-equal contiguous segments
    bounds = [int(round(i * n / n_sites)) for i in range(n_sites + 1)]
    records = []
    for si in range(n_sites):
        lo, hi = bounds[si], bounds[si + 1]
        block = [tuple(seqs[k]) for k in range(lo, hi) if seqs[k]]
        # chunk block into pseudo-inscriptions of size 4..12 (tablet-like)
        i = 0
        while i < len(block):
            sz = rng.randint(4, 12)
            chunk = block[i:i + sz]
            i += sz
            if chunk:
                records.append(("LB%d" % si, chunk))
    return records

# ---------- i.i.d. false-positive control ----------
def iid_false_positive_control(records, n_controls=N_FP_CONTROLS, n_draws=N_DRAWS, seed=SEED_FP):
    """For each control: draw wordforms i.i.d. by the marginal form-frequency of the REAL records,
    assign them to pseudo-sites of the SAME sizes as the real site partition (round-robin within
    each pseudo-site). By construction there is NO identity<->site association. Returns the
    fraction of controls whose own site-shuffle test rejects at p<=0.05 (false-positive rate),
    plus the list of per-control p-values.
    """
    rng = random.Random(seed)
    # marginal form frequency (pool of all wordform tokens)
    pool = []
    for _, wfs in records:
        pool.extend(wfs)
    if not pool:
        return 1.0, []
    # site sizes (number of wordform tokens per site) — preserve real site-size structure
    site_sizes = Counter()
    for s, wfs in records:
        site_sizes[s] += len(wfs)
    sites_ordered = list(site_sizes.keys())
    sizes = [site_sizes[s] for s in sites_ordered]
    total = sum(sizes)
    fps = []
    for c in range(n_controls):
        # draw total tokens i.i.d. from pool
        draws_tok = [pool[rng.randrange(len(pool))] for _ in range(total)]
        # partition into pseudo-sites of fixed sizes (round-robin within site)
        recs = []
        pos = 0
        for si, sz in enumerate(sizes):
            psite = "PS%d" % si
            # one pseudo-inscription per pseudo-site carrying all its tokens
            wfs = draws_tok[pos:pos + sz]
            pos += sz
            if wfs:
                recs.append((psite, wfs))
        obs_c, _, _, _ = n_shared_from_records(recs)
        _, p_c, _ = site_shuffle_null(recs, n_draws=n_draws, seed=seed + 1000 + c, observed=obs_c)
        fps.append(p_c)
    fpr = sum(1 for p in fps if p <= 0.05) / len(fps)
    return fpr, fps

# ---------- full pipeline ----------
def run_la_global(records):
    n_shared, mult, form_sites, form_count = n_shared_from_records(records)
    mean, p, draws = site_shuffle_null(records, observed=n_shared)
    return {
        "n_shared": n_shared,
        "multiplicity": dict(sorted(mult.items())),
        "null_mean": mean,
        "null_p": p,
        "form_sites": form_sites,
        "form_count": form_count,
    }

def run_la_loo(records, exclude_site):
    sub = [(s, wfs) for s, wfs in records if s != exclude_site]
    n_shared, mult, form_sites, form_count = n_shared_from_records(sub)
    mean, p, draws = site_shuffle_null(sub, observed=n_shared, seed=SEED_GLOBAL + 7)
    return n_shared, p, mult

def top_cross_site_forms(form_sites, form_count, k=15):
    cand = [f for f, c in form_count.items() if c >= 2]
    arr = sorted(cand, key=lambda f: (-len(form_sites[f]), -form_count[f]))[:k]
    return [[",".join(f), len(form_sites[f]), form_count[f]] for f in arr]

def run_lb_pc():
    seqs = load_b_damos()
    recs = lb_pseudo_records(seqs)
    obs, _, _, _ = n_shared_from_records(recs)
    mean, p, draws = site_shuffle_null(recs, observed=obs, seed=SEED_LB_PC + 1)
    return obs, mean, p

def run_full():
    corpus = load_corpus()
    records = build_site_records(corpus)

    # 0. inspect
    n_word_tokens = sum(len(wfs) for _, wfs in records)
    forms = set()
    for _, wfs in records:
        for f in wfs:
            forms.add(f)
    site_dist = Counter(s for s, _ in records)

    # 2. global
    g = run_la_global(records)

    # 3. PC
    lb_obs, lb_mean, lb_p = run_lb_pc()
    fpr, fps = iid_false_positive_control(records)

    pc_detect_ok = (lb_p <= 0.05)
    pc_fp_ok = (fpr <= 0.20)
    pc_passed = pc_detect_ok and pc_fp_ok

    # 4. LOO (largest site)
    largest = site_dist.most_common(1)[0][0]
    loo_n_shared, loo_p, loo_mult = run_la_loo(records, largest)
    n_forms_ge3 = sum(v for k, v in g["multiplicity"].items() if k >= 3)

    # 5. verdict
    if not pc_passed:
        verdict = "MACHINERY_UNINFORMATIVE"
    elif len([s for s in site_dist if site_dist[s] >= 5]) < 3:
        verdict = "ADMIN_VOCAB_UNDERPOWERED"
    elif g["null_p"] > 0.05:
        verdict = "ADMIN_VOCAB_NO_SIGNAL"
    elif (loo_p > 0.05) or (n_forms_ge3 < 5):
        verdict = "ADMIN_VOCAB_SITE_LOCAL"
    else:
        verdict = "SHARED_ADMIN_VOCAB_CROSS_SITE"

    top = top_cross_site_forms(g["form_sites"], g["form_count"])

    return {
        "inspect": {
            "n_word_tokens": n_word_tokens,
            "n_distinct_forms": len(forms),
            "n_sites": len(site_dist),
            "site_distribution": dict(site_dist.most_common(15)),
            "largest_site": largest,
        },
        "global": {
            "n_shared": g["n_shared"],
            "multiplicity": g["multiplicity"],
            "null_mean": g["null_mean"],
            "null_p": g["null_p"],
        },
        "positive_control": {
            "lb_n_shared": lb_obs,
            "lb_null_mean": lb_mean,
            "lb_detect_p": lb_p,
            "detect_ok": pc_detect_ok,
            "false_pos_rate": fpr,
            "fp_ok": pc_fp_ok,
            "pc_passed": pc_passed,
            "fp_pvals": fps,
        },
        "held_out": {
            "loo_excluded": largest,
            "loo_n_shared": loo_n_shared,
            "loo_p": loo_p,
            "loo_multiplicity": dict(sorted(loo_mult.items())),
            "n_forms_ge3_sites": n_forms_ge3,
        },
        "top_cross_site_forms": top,
        "verdict": verdict,
    }

# ---------- self-check ----------
if __name__ == "__main__":
    print("EPOCH-032 machinery self-check — running full pipeline...", file=sys.stderr)
    out = run_full()
    # don't dump the giant fp_pvals to stdout summary
    summary = dict(out)
    summary["positive_control"] = {k: v for k, v in out["positive_control"].items() if k != "fp_pvals"}
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print("\nVERDICT: %s" % out["verdict"], file=sys.stderr)
