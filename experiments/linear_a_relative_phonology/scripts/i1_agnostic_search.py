#!/usr/bin/env python3
"""I1 — Agnostic value-system search with relative constraints.

Searches for a compact syllabic value system (a C x V factorisation of the Linear A sign
inventory) that predicts HELD-OUT Linear A word sequences better than a chance factorisation
of the same size, pruned by the campaign's relative constraints. Two search methods
(greedy best-swap hill-climbing + annealed swap MCMC), a frozen objective, three nulls/controls,
a mechanical verdict, and full equivalence-class accounting.

DESIGN NOTE (recorded, not silent): a free assignment that may lump signs into arbitrarily few
cells makes the held-out-LL objective degenerate — collapse to ~3 cells maximises LL on a tiny
corpus (low-variance near-unigram) and recovers NO phonology, and the Linear B positive control
confirms that free objective is a DEAD detector (vowel AMI 0.000). See
data/I1_agnostic_free_objective_collapse.json. The PRIMARY search therefore fixes granularity:
assignments are BALANCED partitions (each C-class and V-class holds a fixed count of signs) and
all moves are SWAPS that preserve those counts, so the search varies only WHICH signs group
together — the phonological question — with collapse off the table. The collapse degeneracy is
still reported as a diagnostic.

Frozen spec: reports/I_AGNOSTIC_SEARCH_SPEC.md. Seed 20260708. Constitution v2.2. Claim layer <= L3.
NON-CIRCULAR: known Linear B values grade the winner ONLY; never a model input.
"""
from __future__ import annotations
import json, math, os, random, sys, re
from collections import Counter
import numpy as np

MAIN = "/home/claude-runner/gitlab/n8n/logos"
sys.path.insert(0, MAIN)
from scripts.cross_script import data as X  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
SEED = 20260708
FREQ_TH = 10
NV = 5
NC_PRIMARY = 15
NC_GRID = [12, 15, 18]
ALPHA = 0.5
W = dict(seq=1.0, rel=0.01, form=0.01, morph=0.01, cross=0.01)
N_RAND = 10000
N_RESTART = 20
MCMC_CHAINS = 12
MCMC_STEPS = 9000
EPS = 0.01
CV_RE = re.compile(r"^([BDGJKMNPQRSTWYZ]*)([AEIOU])[0-9]*$")


# ----------------------------------------------------------------------------------------------
# data
# ----------------------------------------------------------------------------------------------
def load_words():
    inv, seqs, freq = X.load_a()
    keep = set(inv)
    recs = json.load(open(os.path.join(MAIN, "corpus/silver/inscriptions_structured.json")))
    words = []
    for r in recs:
        for st in r.get("stream", []):
            if st.get("t") == "word":
                w = [s for s in st.get("signs", []) if s in keep]
                if len(w) >= 1:
                    words.append((r["id"], w))
    core = sorted(s for s in inv if freq.get(s, 0) >= FREQ_TH)
    return core, freq, words


def build_index(core):
    idx = {s: i for i, s in enumerate(core)}
    NCORE = len(core)
    return idx, NCORE, NCORE, NCORE + 1  # RARE, BND


def sign_bigrams(words, idx, RARE, BND):
    n = BND + 1
    M = np.zeros((n, n), dtype=np.float64)
    for _id, w in words:
        toks = [BND] + [idx.get(s, RARE) for s in w] + [BND]
        for a, b in zip(toks[:-1], toks[1:]):
            M[a, b] += 1.0
    return M


def grouped_split(words, frac=0.8, seed=SEED):
    ids = sorted({wid for wid, _ in words})
    rng = random.Random(seed)
    rng.shuffle(ids)
    tr = set(ids[:int(round(len(ids) * frac))])
    return [w for w in words if w[0] in tr], [w for w in words if w[0] not in tr]


class Scorer:
    def __init__(self, tr, te, idx, NCORE, RARE, BND, nc, nv):
        self.idx, self.NCORE, self.RARE, self.BND = idx, NCORE, RARE, BND
        self.nc, self.nv = nc, nv
        self.Mtr = sign_bigrams(tr, idx, RARE, BND)
        self.Mte = sign_bigrams(te, idx, RARE, BND)
        self.n_te_tok = self.Mte.sum()
        self.n = BND + 1
        self.CC, self.VC = nc + 2, nv + 2
        self.iRAREc, self.iBNDc = nc, nc + 1
        self.iRAREv, self.iBNDv = nv, nv + 1
        self.eyeC = np.eye(self.CC)
        self.eyeV = np.eye(self.VC)

    def vecs(self, phiC, phiV):
        cvec = np.empty(self.n, dtype=np.int64); vvec = np.empty(self.n, dtype=np.int64)
        cvec[:self.NCORE] = phiC; vvec[:self.NCORE] = phiV
        cvec[self.RARE], vvec[self.RARE] = self.iRAREc, self.iRAREv
        cvec[self.BND], vvec[self.BND] = self.iBNDc, self.iBNDv
        return cvec, vvec

    def seqLL(self, phiC, phiV):
        cvec, vvec = self.vecs(phiC, phiV)
        Gc, Gv = self.eyeC[cvec], self.eyeV[vvec]
        Ctr, Vtr = Gc.T @ self.Mtr @ Gc, Gv.T @ self.Mtr @ Gv
        logPC = np.log((Ctr + ALPHA) / (Ctr.sum(1, keepdims=True) + ALPHA * self.CC))
        logPV = np.log((Vtr + ALPHA) / (Vtr.sum(1, keepdims=True) + ALPHA * self.VC))
        Cte, Vte = Gc.T @ self.Mte @ Gc, Gv.T @ self.Mte @ Gv
        return float((Cte * logPC).sum() + (Vte * logPV).sum()) / self.n_te_tok


# ----------------------------------------------------------------------------------------------
# constraints
# ----------------------------------------------------------------------------------------------
def build_constraints(core, idx):
    g = json.load(open(os.path.join(DATA, "C_la_graph.json")))
    sub = [(idx[a], idx[b]) for e in g["sign_substitution_graph"]["top_edges"]
           for a, b in [e["signs"]] if a in idx and b in idx]
    d = json.load(open(os.path.join(DATA, "D_la_posterior.json")))
    pre = [idx[s["sign"]] for s in d["affixation_paradigm_L2_L3_anonymous"]["signs"]
           if s["role_anonymous"] == "PREFIX_EDGE" and s["sign"] in idx]
    return sub, pre, idx.get("KU"), idx.get("KI")


def rel_agree(phiC, phiV, sub):
    if not sub:
        return 0.0
    sv = sum(phiV[a] == phiV[b] for a, b in sub) / len(sub)
    sc = sum(phiC[a] == phiC[b] for a, b in sub) / len(sub)
    return max(sv, sc)


def morph_compat(phiC, pre, nc):
    if len(pre) < 2:
        return 0.0
    c = Counter(int(phiC[i]) for i in pre); n = sum(c.values())
    H = -sum((v / n) * math.log(v / n) for v in c.values())
    Hm = math.log(min(len(pre), nc))
    return 1.0 - (H / Hm if Hm > 0 else 0.0)


class Objective:
    def __init__(self, scorer, sub, pre, ku, ki, core, idx, nc):
        self.sc, self.sub, self.pre, self.ku, self.ki, self.nc = scorer, sub, pre, ku, ki, nc
        ab_idx, vlab = [], []
        for s in core:
            m = CV_RE.match(s)
            if m and not s.startswith("*"):
                ab_idx.append(idx[s]); vlab.append(m.group(2))
        self.ab_idx = np.array(ab_idx, dtype=np.int64); self.n_ab = len(ab_idx)
        if self.n_ab >= 3:
            vl = np.array([ord(v) for v in vlab])
            st = (vl[:, None] == vl[None, :])
            self.triu = np.triu(np.ones_like(st, bool), 1)
            self.same_true = st[self.triu]
        else:
            self.same_true = None

    def cross(self, phiV):
        if self.same_true is None:
            return 0.0
        pv = phiV[self.ab_idx]
        return float(((pv[:, None] == pv[None, :])[self.triu] == self.same_true).mean())

    def components(self, phiC, phiV):
        return (self.sc.seqLL(phiC, phiV), rel_agree(phiC, phiV, self.sub),
                (1.0 if self.ku is not None and self.ki is not None and phiC[self.ku] == phiC[self.ki] else 0.0),
                morph_compat(phiC, self.pre, self.nc), self.cross(phiV), self.n_ab)

    def score(self, phiC, phiV):
        seq, rel, frm, mor, crs, _ = self.components(phiC, phiV)
        return W["seq"] * seq + W["rel"] * rel + W["form"] * frm + W["morph"] * mor + W["cross"] * crs


# ----------------------------------------------------------------------------------------------
# balanced (fixed-granularity) assignments + swap search
# ----------------------------------------------------------------------------------------------
def balanced_labels(N, K, rng):
    base = [i % K for i in range(N)]  # sizes as equal as possible
    rng.shuffle(base)
    return np.array(base, dtype=np.int64)


def rand_phi(NCORE, nc, nv, rng):
    return balanced_labels(NCORE, nc, rng), balanced_labels(NCORE, nv, rng)


def greedy_swap(obj, NCORE, nc, nv, rng, n_cand=240, max_scans=60):
    """Best-first: each scan proposes n_cand random swaps (alternating C/V axis), applies the
    single best improving swap; stops when a scan finds no improvement. Preserves class sizes."""
    phiC, phiV = rand_phi(NCORE, nc, nv, rng)
    cur = obj.score(phiC, phiV)
    for _ in range(max_scans):
        best = None
        for _c in range(n_cand):
            axis = rng.random() < 0.5
            i, j = rng.randrange(NCORE), rng.randrange(NCORE)
            arr = phiC if axis else phiV
            if arr[i] == arr[j]:
                continue
            arr[i], arr[j] = arr[j], arr[i]
            s = obj.score(phiC, phiV)
            arr[i], arr[j] = arr[j], arr[i]
            if s > cur + 1e-12 and (best is None or s > best[0]):
                best = (s, axis, i, j)
        if best is None:
            break
        _, axis, i, j = best
        arr = phiC if axis else phiV
        arr[i], arr[j] = arr[j], arr[i]
        cur = best[0]
    return phiC, phiV, cur


def canonical(phiC, phiV):
    cmap, vmap, key = {}, {}, []
    for a, b in zip(phiC.tolist(), phiV.tolist()):
        cmap.setdefault(a, len(cmap)); vmap.setdefault(b, len(vmap))
        key.append((cmap[a], vmap[b]))
    return tuple(key)


def beam_search(obj, NCORE, nc, nv, seed):
    rng = random.Random(seed); optima = {}; best = None
    for _ in range(N_RESTART):
        phiC, phiV, s = greedy_swap(obj, NCORE, nc, nv, rng)
        k = canonical(phiC, phiV)
        if k not in optima or s > optima[k][0]:
            optima[k] = (s, phiC.copy(), phiV.copy())
        if best is None or s > best[0]:
            best = (s, phiC.copy(), phiV.copy())
    return best, optima


def mcmc(obj, NCORE, nc, nv, seed, best_seq=None, chains=MCMC_CHAINS, steps=MCMC_STEPS):
    rng = random.Random(seed + 1); best = None; near = {}
    for _ in range(chains):
        phiC, phiV = rand_phi(NCORE, nc, nv, rng)
        cur = obj.score(phiC, phiV)
        for t in range(steps):
            T = (0.02) ** (t / steps)
            axis = rng.random() < 0.5
            i, j = rng.randrange(NCORE), rng.randrange(NCORE)
            arr = phiC if axis else phiV
            if arr[i] == arr[j]:
                continue
            arr[i], arr[j] = arr[j], arr[i]
            s = obj.score(phiC, phiV)
            if s >= cur or rng.random() < math.exp((s - cur) / max(T, 1e-6)):
                cur = s
                if best is None or cur > best[0]:
                    best = (cur, phiC.copy(), phiV.copy())
                if best_seq is not None:
                    sq = obj.sc.seqLL(phiC, phiV)
                    if sq >= best_seq - EPS:
                        near[canonical(phiC, phiV)] = sq
            else:
                arr[i], arr[j] = arr[j], arr[i]
    return best, near


# ----------------------------------------------------------------------------------------------
# free-objective collapse diagnostic (documents the degeneracy the balanced design removes)
# ----------------------------------------------------------------------------------------------
def free_collapse(scorer, NCORE, nc, nv, seed):
    rng = random.Random(seed + 55)
    best = None
    for _ in range(2):
        phiC = np.array([rng.randrange(nc) for _ in range(NCORE)])
        phiV = np.array([rng.randrange(nv) for _ in range(NCORE)])
        cur = scorer.seqLL(phiC, phiV)
        for _s in range(8):
            imp = False
            for i in range(NCORE):
                bc, bv, bs = phiC[i], phiV[i], cur
                oc, ov = phiC[i], phiV[i]
                for c in range(nc):
                    for v in range(nv):
                        phiC[i], phiV[i] = c, v
                        sc = scorer.seqLL(phiC, phiV)
                        if sc > bs + 1e-12:
                            bs, bc, bv = sc, c, v
                phiC[i], phiV[i] = bc, bv
                if bs > cur + 1e-12:
                    cur = bs; imp = True
            if not imp:
                break
        if best is None or cur > best[0]:
            best = (cur, phiC.copy(), phiV.copy())
    cells = len(set(zip(best[1].tolist(), best[2].tolist())))
    return dict(free_best_seqLL=best[0], free_occupied_cells=cells)


# ----------------------------------------------------------------------------------------------
# nulls + grading
# ----------------------------------------------------------------------------------------------
def random_null(scorer, NCORE, nc, nv, n=N_RAND, seed=SEED):
    rng = random.Random(seed + 100); vals = np.empty(n)
    for k in range(n):
        vals[k] = scorer.seqLL(*rand_phi(NCORE, nc, nv, rng))
    return vals


def permute_corpus(words, seed=SEED):
    rng = random.Random(seed + 200)
    pool = [s for _id, w in words for s in w]; rng.shuffle(pool)
    out, k = [], 0
    for _id, w in words:
        out.append((_id, pool[k:k + len(w)])); k += len(w)
    return out


def ami(a, b, rng, n_perm=2000):
    from math import log
    def mi(a, b):
        n = len(a); ca, cb = Counter(a), Counter(b); cab = Counter(zip(a, b))
        return sum((nxy / n) * log((nxy * n) / (ca[x] * cb[y])) for (x, y), nxy in cab.items())
    def ent(a):
        n = len(a); c = Counter(a)
        return -sum((v / n) * log(v / n) for v in c.values())
    obs = mi(a, b); Ha, Hb = ent(a), ent(b)
    nmi = obs / max(1e-9, (Ha + Hb) / 2)
    bb = list(b); hits = 0; nulls = []
    for _ in range(n_perm):
        rng.shuffle(bb); m = mi(a, bb); nulls.append(m); hits += (m >= obs)
    return dict(mi=obs, nmi=nmi, perm_p=(hits + 1) / (n_perm + 1), null_mean=float(np.mean(nulls)))


def grade_axes(core, idx, phiC, phiV, seed=SEED):
    """Grade C-partition vs true consonant and V-partition vs true vowel on AB signs. GRADING ONLY."""
    cons, vow, cl, vl = [], [], [], []
    for s in core:
        m = CV_RE.match(s)
        if m and not s.startswith("*"):
            cl.append(int(phiC[idx[s]])); vl.append(int(phiV[idx[s]]))
            cons.append(m.group(1) or "_"); vow.append(m.group(2))
    r = random.Random(seed + 300)
    return dict(n_ab=len(cl),
                consonant_axis=ami(cl, cons, r),
                vowel_axis=ami(vl, vow, r))


def log10_orbit(phiC, phiV, nc, nv):
    cells = Counter(zip(phiC.tolist(), phiV.tolist()))
    l10 = 1 / math.log(10)
    return (math.lgamma(nc + 1) + math.lgamma(nv + 1)
            + sum(math.lgamma(n + 1) for n in cells.values())) * l10, len(cells)


def run_grid(core, idx, NCORE, RARE, BND, words, nc, nv, tag, do_near=True, constraints=True):
    tr, te = grouped_split(words)
    sc = Scorer(tr, te, idx, NCORE, RARE, BND, nc, nv)
    if constraints:
        sub, pre, ku, ki = build_constraints(core, idx)
    else:
        sub, pre, ku, ki = [], [], None, None
    obj = Objective(sc, sub, pre, ku, ki, core, idx, nc)
    bb, optima = beam_search(obj, NCORE, nc, nv, SEED)
    bm, _ = mcmc(obj, NCORE, nc, nv, SEED)
    best = bb if bb[0] >= bm[0] else bm
    bs, bC, bV = best
    best_seq = sc.seqLL(bC, bV)
    seq, rel, frm, mor, crs, nab = obj.components(bC, bV)
    nulls = random_null(sc, NCORE, nc, nv)
    near = {}
    if do_near:
        _, near = mcmc(obj, NCORE, nc, nv, SEED + 7, best_seq=best_seq)
    l10, ncell = log10_orbit(bC, bV, nc, nv)
    res = dict(tag=tag, nc=nc, nv=nv, n_core=NCORE, n_train_words=len(tr), n_test_words=len(te),
               best_score=bs, best_seqLL=best_seq,
               components=dict(seqLL=seq, relAgree=rel, formConsist=frm, morphCompat=mor,
                               crossCompat=crs, n_ab=nab),
               null_mean=float(nulls.mean()), null_sd=float(nulls.std()),
               null_p99=float(np.percentile(nulls, 99)), null_max=float(nulls.max()),
               best_seqLL_percentile=float((nulls < best_seq).mean() * 100),
               gain_over_median=best_seq - float(np.median(nulls)),
               n_beam_optima=len(optima), n_near_optimal_distinct=len(near),
               log10_symmetry_orbit=l10, n_occupied_cells=ncell,
               grade=grade_axes(core, idx, bC, bV),
               free_diag=free_collapse(sc, NCORE, nc, nv, SEED),
               phiC=bC.tolist(), phiV=bV.tolist())
    return res, sc


def main():
    random.seed(SEED); np.random.seed(SEED)
    core, freq, words = load_words()
    idx, NCORE, RARE, BND = build_index(core)
    out = dict(task="I1", seed=SEED, constitution="v2.2", as_of="2026-07-07", claim_layer_cap="L3",
               non_circular=True, design="balanced_fixed_granularity_swap_search",
               grid_primary=dict(nc=NC_PRIMARY, nv=NV), freq_threshold=FREQ_TH,
               n_core_signs=NCORE, n_gorila_words=len(words), weights=W, core_signs=core)

    grids = {}
    for nc in NC_GRID:
        res, sc = run_grid(core, idx, NCORE, RARE, BND, words, nc, NV, f"real_C{nc}")
        assign_bits = NCORE * math.log2(nc * NV)
        model_bits = ((nc + 2) ** 2 + (NV + 2) ** 2) * 0.5 * math.log2(sc.n_te_tok + 1)
        data_bits = -res["best_seqLL"] * sc.n_te_tok / math.log(2)
        res["mdl_total_bits"] = assign_bits + model_bits + data_bits
        res["mdl_parts"] = dict(assign_bits=assign_bits, model_bits=model_bits, data_bits=data_bits)
        grids[f"C{nc}"] = res
    out["grids_real"] = grids
    out["mdl_selected_grid"] = min(grids, key=lambda g: grids[g]["mdl_total_bits"])
    prim = grids[f"C{NC_PRIMARY}"]

    # N2 permuted-corpus null (primary grid)
    pres, _ = run_grid(core, idx, NCORE, RARE, BND, permute_corpus(words), NC_PRIMARY, NV,
                       "permuted_C15", do_near=False)
    out["permuted_corpus"] = dict(best_seqLL=pres["best_seqLL"],
                                  gain_over_median=pres["gain_over_median"],
                                  best_seqLL_percentile=pres["best_seqLL_percentile"],
                                  grade=pres["grade"])
    real_gain, perm_gain = prim["gain_over_median"], pres["gain_over_median"]
    out["gain_ratio_real_vs_permuted"] = real_gain / perm_gain if perm_gain else float("inf")

    # C1 Linear B positive control (pure seqLL, no LA constraints)
    b_seqs, b_freq, v2g = X.load_b_damos()
    b_core = sorted(s for s in b_freq if b_freq[s] >= FREQ_TH)
    bwords = [(f"b{i}", w) for i, w in enumerate(b_seqs)]
    bidx = {s: i for i, s in enumerate(b_core)}; bNC = len(b_core)
    bres, _ = run_grid(b_core, bidx, bNC, bNC, bNC + 1, bwords, NC_PRIMARY, NV, "lb_control",
                       do_near=False, constraints=False)
    out["lb_positive_control"] = dict(
        n_core=bNC, best_seqLL=bres["best_seqLL"], null_mean=bres["null_mean"],
        null_p99=bres["null_p99"], best_seqLL_percentile=bres["best_seqLL_percentile"],
        gain_over_median=bres["gain_over_median"], grade=bres["grade"],
        n_occupied_cells=bres["n_occupied_cells"])

    # FROZEN verdict
    lb = out["lb_positive_control"]
    detector_fires = (lb["best_seqLL"] > lb["null_p99"] and
                      min(lb["grade"]["consonant_axis"]["perm_p"],
                          lb["grade"]["vowel_axis"]["perm_p"]) < 0.05)
    cond_a = prim["best_seqLL"] > prim["null_p99"]
    cond_b = out["gain_ratio_real_vs_permuted"] > 2.0
    cond_c = min(prim["grade"]["consonant_axis"]["perm_p"],
                 prim["grade"]["vowel_axis"]["perm_p"]) < 0.05
    out["verdict_conditions"] = dict(a_beats_p99=bool(cond_a), b_gain_ratio_gt2=bool(cond_b),
                                     c_axis_ami_sig=bool(cond_c), lb_detector_fires=bool(detector_fires))
    if not detector_fires:
        out["verdict"] = "NO_POWER"
    elif cond_a and cond_b and cond_c:
        out["verdict"] = "VALUE_STRUCTURE_RECOVERED"
    else:
        out["verdict"] = "UNDERDETERMINED_NO_RECOVERY"

    json.dump(out, open(os.path.join(DATA, "I1_agnostic.json"), "w"), indent=2)
    g = prim["grade"]
    print("VERDICT:", out["verdict"])
    print("primary best_seqLL %.4f null_mean %.4f p99 %.4f pct %.2f occ_cells %d"
          % (prim["best_seqLL"], prim["null_mean"], prim["null_p99"],
             prim["best_seqLL_percentile"], prim["n_occupied_cells"]))
    print("real gain %.4f permuted gain %.4f ratio %.3f" % (real_gain, perm_gain,
          out["gain_ratio_real_vs_permuted"]))
    print("LA grade  Caxis nmi %.3f p %.3f | Vaxis nmi %.3f p %.3f"
          % (g["consonant_axis"]["nmi"], g["consonant_axis"]["perm_p"],
             g["vowel_axis"]["nmi"], g["vowel_axis"]["perm_p"]))
    print("LB control best %.4f pct %.2f Caxis nmi %.3f p %.3f | Vaxis nmi %.3f p %.3f occ %d"
          % (lb["best_seqLL"], lb["best_seqLL_percentile"],
             lb["grade"]["consonant_axis"]["nmi"], lb["grade"]["consonant_axis"]["perm_p"],
             lb["grade"]["vowel_axis"]["nmi"], lb["grade"]["vowel_axis"]["perm_p"],
             lb["n_occupied_cells"]))
    print("detector_fires:", detector_fires)
    print("free-collapse diag (LA C15): seqLL %.4f occ_cells %d"
          % (prim["free_diag"]["free_best_seqLL"], prim["free_diag"]["free_occupied_cells"]))
    print("log10 orbit %.1f near-optimal distinct %d beam optima %d MDL grid %s"
          % (prim["log10_symmetry_orbit"], prim["n_near_optimal_distinct"],
             prim["n_beam_optima"], out["mdl_selected_grid"]))


if __name__ == "__main__":
    main()
