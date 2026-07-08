#!/usr/bin/env python3
"""
EPOCH-035 machinery — TERMINAL TOTAL-SLOT (inscription-FINAL word-form over-representation).

Pure L2/L3 POSITIONAL / DOCUMENT-STRUCTURAL statistics on ANONYMOUS sign sequences.
No phonetics, no sound, no meaning, no numeral arithmetic. "total-slot" = INSCRIPTION-FINAL
POSITION only.

FROZEN CANDIDATE SELECTION RULE: the word-form with the MOST inscription-FINAL occurrences,
among forms with total count >=8 AND final count >=5. Selection by FINAL COUNT. If none ->
TERMINAL_SLOT_UNDERPOWERED.

FROZEN METRIC: candidate FINAL-POSITION ENRICHMENT = (candidate occurrences that are
inscription-final) / (all candidate occurrences in >=2-word inscriptions). Control axis:
initial_rate (a total-slot form should be FINAL-biased, not initial-biased).

FROZEN NULL — WITHIN-INSCRIPTION POSITION PERMUTATION (calibrated by construction):
  For each inscription, randomly permute its word ORDER (word multiset fixed), recompute the
  candidate's final-position count; >=2000 draws; one-sided p = frac draws with permuted
  final-count >= observed.

POSITIVE CONTROL (gates verdict) on LB (DĀMOS; NO site metadata -> SEEDED pseudo-inscription
partition, stated explicitly):
  - DETECT (planted terminal bias): force a chosen form to be inscription-final in ~X% of
    pseudo-inscriptions; null MUST reject (p<=0.05) in the correct (final-biased) direction.
  - FALSE-POSITIVE: on position-randomized pseudo-inscriptions (exact H0), rejection rate
    (frac p<=0.05) MUST be <=0.10 across >=30 independent sets.
  Failure of either -> MACHINERY_UNINFORMATIVE.

Self-check: `python3 machinery.py` runs the full pipeline + PC and prints a JSON summary.
"""
import json, os, sys, hashlib, random
from collections import Counter, defaultdict

# ---------- paths ----------
HERE = os.path.dirname(os.path.abspath(__file__))
# HERE = .../experiments/linear_a_frontier_72h/epochs/EPOCH-035
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
CORPUS = os.path.join(REPO, "corpus", "silver", "inscriptions_structured.json")
SCRIPTS = os.path.join(REPO, "scripts")

# ---------- seeds / knobs (FROZEN) ----------
SEED_GLOBAL       = 20240750
SEED_PC_DETECT    = 20240751
SEED_PC_FP        = 20240752
SEED_SITE_BASE    = 20240753
SEED_LOO          = 20240754
SEED_LB_PARTITION = 20240755
N_DRAWS           = 2000      # >=2000
PC_DETECT_DRAWS   = 2000
PC_FP_DRAWS       = 1000      # per control set
N_FP_SETS         = 30        # >=30
MIN_SITE_CAND     = 10        # >=10 candidate occurrences per site (candidate metric)
MIN_SITE_INSC     = 15        # >=15 qualifying inscriptions per site (aggregate metric)
PLANT_FRAC        = 0.45      # plant terminal bias: chosen form forced final in ~45% of pseudo-insc
LB_PSEUDO_LEN     = 6         # words per pseudo-inscription (chunk size)
CAND_TOTAL_MIN    = 8         # candidate selection threshold
CAND_FINAL_MIN    = 5         # candidate selection threshold

# ---------- corpus IO ----------
def load_corpus(path=CORPUS):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_b_damos():
    """Linear B positive-control benchmark. DĀMOS has NO site/inscription metadata.
    Returns a flat list of wordforms (each a list of signs)."""
    sys.path.insert(0, SCRIPTS)
    from cross_script import data as D
    seqs, freq, v2g = D.load_b_damos()
    return seqs

# ---------- core: word sequences ----------
def words_of(insc):
    """Ordered list of word sign-tuples for an inscription (non-word tokens ignored)."""
    out = []
    for tok in insc.get("stream", []) or []:
        if tok.get("t") == "word":
            sg = tuple(tok.get("signs", []) or [])
            if sg:
                out.append(sg)
    return out

def qualifying(corpus):
    """Inscriptions with >=2 non-empty word tokens."""
    return [ins for ins in corpus if len(words_of(ins)) >= 2]

# ---------- candidate selection (FROZEN rule) ----------
def select_candidate(qual):
    """Return (form_tuple, final_count, total_count) per the frozen selection rule, or None."""
    total = Counter(); final = Counter()
    for ins in qual:
        ws = words_of(ins)
        for w in ws:
            total[w] += 1
        final[ws[-1]] += 1
    cands = [(w, final[w], total[w]) for w in final
             if total[w] >= CAND_TOTAL_MIN and final[w] >= CAND_FINAL_MIN]
    if not cands:
        return None
    cands.sort(key=lambda x: (-x[1], -x[2]))   # by final count, then total
    return cands[0]

def top_final_forms(qual, k=10):
    total = Counter(); final = Counter()
    for ins in qual:
        ws = words_of(ins)
        for w in ws:
            total[w] += 1
        final[ws[-1]] += 1
    rows = []
    for w, fc in final.most_common(k):
        rows.append([",".join(w), fc, total[w]])
    return rows

# ---------- observed metrics ----------
def candidate_final_count(records, cand):
    return sum(1 for ws in records if ws[-1] == cand)

def candidate_total_count(records, cand):
    return sum(1 for ws in records for w in ws if w == cand)

def candidate_initial_count(records, cand):
    return sum(1 for ws in records if ws[0] == cand)

# ---------- FROZEN NULL: within-inscription position permutation ----------
def null_permutation_final(records, cand, n_draws, seed, observed_final):
    """For each inscription, permute word order; recompute candidate final-count each draw.
    One-sided p = frac draws with permuted final-count >= observed."""
    rng = random.Random(seed)
    ge = 0
    means = []
    for _ in range(n_draws):
        fc = 0
        for ws in records:
            if len(ws) <= 1:
                if ws and ws[0] == cand:
                    fc += 1
            else:
                p = ws[:]
                rng.shuffle(p)
                if p[-1] == cand:
                    fc += 1
        means.append(fc)
        if fc >= observed_final - 1e-15:
            ge += 1
    null_mean = sum(means) / len(means)
    p = ge / n_draws
    return null_mean, p

# ---------- POSITIVE CONTROL ----------
def build_lb_pseudo_inscriptions(seqs, seed):
    """Chunk flat DĀMOS wordform list into ordered pseudo-inscriptions of LB_PSEUDO_LEN words.
    DĀMOS has no site/inscription metadata -> SEEDED partition (stated)."""
    rng = random.Random(seed)
    pool = [tuple(s) for s in seqs if len(s) > 0]
    rng.shuffle(pool)
    recs = []
    i = 0
    while i + LB_PSEUDO_LEN <= len(pool):
        recs.append(pool[i:i + LB_PSEUDO_LEN])
        i += LB_PSEUDO_LEN
    return recs

def plant_terminal_bias(records, form, frac, seed):
    """Force `form` to be the LAST word of a pseudo-inscription in `frac` of records,
    by swapping an existing occurrence of `form` into the final position (or replacing the last
    word with a sampled `form` if none exists). Returns new records with a planted final bias."""
    rng = random.Random(seed)
    pool_form = [w for rec in records for w in rec if w == form]
    out = []
    for rec in records:
        rec = [tuple(w) for w in rec]
        if rng.random() < frac:
            if rec[-1] != form:
                if pool_form:
                    rec[-1] = rng.choice(pool_form)
                else:
                    rec[-1] = form
        out.append(rec)
    return out

def position_randomize(records, seed):
    """Exact H0: permute word order within each pseudo-inscription."""
    rng = random.Random(seed)
    out = []
    for rec in records:
        p = [tuple(w) for w in rec]
        rng.shuffle(p)
        out.append(p)
    return out

def pc_detect(seqs, seed):
    """DETECT arm: plant a terminal bias on a chosen common form and confirm the
    position-permutation null rejects in the correct (final-biased) direction."""
    base = build_lb_pseudo_inscriptions(seqs, SEED_LB_PARTITION)
    # choose a form that actually exists in the pool to plant
    cnt = Counter(w for rec in base for w in rec)
    form = cnt.most_common(1)[0][0]
    planted = plant_terminal_bias(base, form, PLANT_FRAC, seed)
    obs = candidate_final_count(planted, form)
    null_mean, p = null_permutation_final(planted, form, PC_DETECT_DRAWS, seed ^ 0x9e37, obs)
    return {"form": form, "obs": obs, "null_mean": null_mean, "p": p,
            "reject_correct_direction": (p <= 0.05 and obs > null_mean)}

def pc_false_positive(seqs, seed):
    """FALSE-POSITIVE arm: on position-randomized pseudo-inscriptions (exact H0), measure the
    rejection rate across N_FP_SETS independent sets. Must be <=0.10."""
    rng = random.Random(seed)
    rejects = 0
    ps = []
    for k in range(N_FP_SETS):
        s = rng.randrange(1 << 30)
        base = build_lb_pseudo_inscriptions(seqs, SEED_LB_PARTITION + k + 1)
        # exact H0: randomize positions
        rnd = position_randomize(base, s)
        # pick the most frequent form in this set as the "candidate" (worst-case post-hoc pick)
        cnt = Counter(w for rec in rnd for w in rec)
        form = cnt.most_common(1)[0][0]
        obs = candidate_final_count(rnd, form)
        null_mean, p = null_permutation_final(rnd, form, PC_FP_DRAWS, s ^ 0x1234, obs)
        ps.append(p)
        if p <= 0.05 and obs > null_mean:
            rejects += 1
    return {"false_pos_rate": rejects / N_FP_SETS, "n_sets": N_FP_SETS, "ps": ps}

# ---------- CROSS-SITE ----------
def per_site_candidate(qual, cand, n_draws, seed_base):
    """Per site with >=MIN_SITE_CAND candidate occurrences: observed final-enrichment + p."""
    by_site = defaultdict(list)
    for ins in qual:
        by_site[ins.get("site", "?")].append(words_of(ins))
    out = {}
    for site, recs in by_site.items():
        tot = candidate_total_count(recs, cand)
        fin = candidate_final_count(recs, cand)
        if tot < MIN_SITE_CAND:
            continue
        obs = fin
        null_mean, p = null_permutation_final(recs, cand, n_draws, seed_base + hash(site) % 100000, obs)
        out[site] = {"total": tot, "final": fin, "obs_final": obs,
                     "null_mean": null_mean, "p": p,
                     "sig": (p <= 0.05 and obs > null_mean)}
    return out

def per_site_aggregate_concentration(qual, n_draws, seed_base):
    """Fallback metric: per site with >=MIN_SITE_INSC qualifying inscriptions, is the site's set
    of final-position forms more concentrated (top-form share = most-frequent final form's share
    of all final slots) than its position-permutation null?"""
    by_site = defaultdict(list)
    for ins in qual:
        by_site[ins.get("site", "?")].append(words_of(ins))
    out = {}
    for site, recs in by_site.items():
        if len(recs) < MIN_SITE_INSC:
            continue
        finals = [ws[-1] for ws in recs]
        if not finals:
            continue
        cc = Counter(finals)
        top_share = cc.most_common(1)[0][1] / len(finals)
        # null: permute word order within each inscription, recompute top-form share
        rng = random.Random(seed_base + hash(site) % 100000)
        ge = 0; means = []
        for _ in range(n_draws):
            perm_finals = []
            for ws in recs:
                if len(ws) <= 1:
                    perm_finals.append(ws[-1])
                else:
                    p = ws[:]; rng.shuffle(p); perm_finals.append(p[-1])
            pc = Counter(perm_finals)
            ts = pc.most_common(1)[0][1] / len(perm_finals)
            means.append(ts)
            if ts >= top_share - 1e-15:
                ge += 1
        null_mean = sum(means) / len(means)
        p = ge / n_draws
        out[site] = {"n_insc": len(recs), "top_form": ",".join(cc.most_common(1)[0][0]),
                     "top_share": top_share, "null_mean": null_mean, "p": p,
                     "sig": (p <= 0.05 and top_share > null_mean)}
    return out

def leave_one_site_out(qual, cand, exclude_site, n_draws, seed):
    """Exclude the largest site, recompute global candidate final-enrichment p."""
    recs = [words_of(ins) for ins in qual if ins.get("site", "?") != exclude_site]
    obs = candidate_final_count(recs, cand)
    null_mean, p = null_permutation_final(recs, cand, n_draws, seed, obs)
    return {"obs_final": obs, "null_mean": null_mean, "p": p,
            "sig": (p <= 0.05 and obs > null_mean)}

# ---------- main pipeline ----------
def run():
    corpus = load_corpus()
    qual = qualifying(corpus)
    n_qual = len(qual)

    sel = select_candidate(qual)
    top = top_final_forms(qual, 10)

    result = {"n_inscriptions": len(corpus), "n_qualifying": n_qual,
              "top_final_forms": top, "candidate": None}

    if sel is None:
        result["underpowered"] = True
        return result

    cand, final_count, total_count = sel
    records = [words_of(ins) for ins in qual]
    obs_final = candidate_final_count(records, cand)
    tot = candidate_total_count(records, cand)
    ini = candidate_initial_count(records, cand)
    final_enrichment = obs_final / tot if tot else 0.0
    initial_rate = ini / tot if tot else 0.0
    null_mean, p = null_permutation_final(records, cand, N_DRAWS, SEED_GLOBAL, obs_final)

    result["candidate"] = {
        "form_signs": ",".join(cand), "total_count": tot, "final_count": obs_final,
        "final_enrichment": final_enrichment, "null_mean": null_mean, "null_p": p,
        "initial_rate": initial_rate,
    }
    result["global_sig"] = (p <= 0.05 and obs_final > null_mean)
    return result

def main():
    res = run()
    print(json.dumps(res, ensure_ascii=False, indent=2, default=str))

if __name__ == "__main__":
    main()
