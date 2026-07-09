#!/usr/bin/env python3
"""EPOCH-077 machinery: within-document position-shuffle null for glyph-size initial-prominence.

L2 only. Signs are opaque catalog IDs. glyph size = within-doc z-scored log bbox-area.
position = glyph index in transcription order (0 = first). No reading, no meaning.
"""
import json, math, os
import numpy as np
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
CAMP = os.path.abspath(os.path.join(HERE, "..", ".."))
DATA = os.path.join(CAMP, "data", "sigla_glyphs_bbox.json")

RNG_SEED = 770077
N_DRAWS = 4000  # >=2000 required


def load_docs(path=DATA, min_glyphs=4):
    raw = json.load(open(path))
    docs = []
    for doc in raw:
        gs = [g for g in doc["glyphs"] if not g["is_divider"] and g.get("bbox") is not None]
        if len(gs) < min_glyphs:
            continue
        areas = np.array([math.log(g["bbox"][2] * g["bbox"][3]) for g in gs], dtype=float)
        mu = areas.mean()
        sd = areas.std()
        if sd == 0:
            sd = 1.0
        z = (areas - mu) / sd
        docs.append({"designation": doc.get("designation", "?"),
                     "site": doc.get("site", "?"),
                     "z": z})
    return docs


def d_init_of(z):
    """(z-size of glyph 0) - (mean z-size of glyphs 1..n-1)."""
    return z[0] - z[1:].mean()


def D_init(docs):
    return float(np.mean([d_init_of(d["z"]) for d in docs]))


def rho_docs(docs):
    rs = []
    for d in docs:
        z = d["z"]
        n = len(z)
        pos = np.arange(n, dtype=float)
        if z.std() > 0 and pos.std() > 0:
            rs.append(np.corrcoef(pos, z)[0, 1])
    return float(np.mean(rs)) if rs else 0.0


def position_shuffle_null(docs, n_draws=N_DRAWS, seed=RNG_SEED, stat="D_init"):
    """Permute each doc's glyph order (preserve size multiset), recompute stat.

    Under this null E[D_init] = 0 because glyph 0 is a uniformly random draw from the doc's z-multiset,
    whose expectation equals the doc mean; z[1:].mean also has that expectation.
    """
    rng = np.random.default_rng(seed)
    zs = [d["z"].copy() for d in docs]
    out = np.empty(n_draws, dtype=float)
    for i in range(n_draws):
        acc = []
        for z in zs:
            p = rng.permutation(len(z))
            zc = z[p]
            if stat == "D_init":
                acc.append(zc[0] - zc[1:].mean())
            else:  # rho
                pos = np.arange(len(zc), dtype=float)
                if zc.std() > 0:
                    acc.append(np.corrcoef(pos, zc)[0, 1])
        out[i] = np.mean(acc)
    return out


def analyze(docs, n_draws=N_DRAWS, seed=RNG_SEED):
    obs_D = D_init(docs)
    null_D = position_shuffle_null(docs, n_draws=n_draws, seed=seed, stat="D_init")
    p_init = float(np.mean(null_D >= obs_D))  # one-sided "initial larger"
    rho = rho_docs(docs)
    return {
        "n_docs": len(docs),
        "D_init": obs_D,
        "D_init_null_mean": float(null_D.mean()),
        "D_init_null_sd": float(null_D.std()),
        "p_init": p_init,
        "rho_pos_size": rho,
        "null_D": null_D,
    }


def per_site(docs, sites=None, n_draws=N_DRAWS, seed=RNG_SEED):
    by = defaultdict(list)
    for d in docs:
        by[d["site"]].append(d)
    if sites is None:
        sites = [s for s, dd in by.items() if len(dd) >= 15]
    out = []
    for s in sites:
        dd = by[s]
        r = analyze(dd, n_draws=n_draws, seed=seed)
        sig = bool(r["p_init"] <= 0.05 and r["D_init"] > 0)
        direction = "larger" if r["D_init"] > 0 else "smaller"
        out.append({"site": s, "n_docs": len(dd), "D_init": r["D_init"],
                    "D_init_null": r["D_init_null_mean"], "p_init": r["p_init"],
                    "sig": sig, "direction": direction})
    return out


# ---- Positive control (synthetic) ----
def _synth_docs(n_docs, n_per_doc_range=(5, 18), effect=0.0, seed=0):
    """Synthetic docs at observed scale. effect>0 makes glyph 0 reliably larger (in z units)."""
    rng = np.random.default_rng(seed)
    docs = []
    for i in range(n_docs):
        n = rng.integers(n_per_doc_range[0], n_per_doc_range[1] + 1)
        z = rng.normal(0, 1, size=n)
        z[0] += effect  # initial prominence
        docs.append({"site": "SYN", "z": z})
    return docs


def positive_control(n_docs=322, n_replicates=25, n_draws=1000, seed=770077):
    """(a) DETECT: plant prominence, check power. (b) FALSE-POS: no effect, check rejection rate."""
    rng = np.random.default_rng(seed)
    # calibration effect: choose a modest effect so a real prominence is detectable if machinery works
    effect = 0.35  # z-units added to glyph 0
    # DETECT
    detect_flags = 0
    for r in range(n_replicates):
        sd = _synth_docs(n_docs, effect=effect, seed=int(rng.integers(0, 2**31 - 1)))
        res = analyze(sd, n_draws=n_draws, seed=int(rng.integers(0, 2**31 - 1)))
        if res["p_init"] <= 0.05 and res["D_init"] > 0:
            detect_flags += 1
    power_est = detect_flags / n_replicates
    detect_p = power_est  # fraction flagged
    # FALSE-POSITIVE: effect=0 (size independent of position)
    fp_flags = 0
    for r in range(n_replicates):
        sd = _synth_docs(n_docs, effect=0.0, seed=int(rng.integers(0, 2**31 - 1)))
        res = analyze(sd, n_draws=n_draws, seed=int(rng.integers(0, 2**31 - 1)))
        if res["p_init"] <= 0.05 and res["D_init"] > 0:
            fp_flags += 1
    false_pos_rate = fp_flags / n_replicates
    passed = (power_est >= 0.5) and (false_pos_rate <= 0.10)
    return {"pc_verdict": "PASSED" if passed else "FAILED",
            "detect_p": detect_p, "power_est": power_est,
            "false_pos_rate": false_pos_rate, "pc_is_synthetic": True,
            "effect_planted": effect}


def verdict(global_res, per_site_res, pc):
    if pc["pc_verdict"] != "PASSED":
        if pc["power_est"] < 0.5:
            return "SPATIAL_SIZE_POSITION_UNDERPOWERED"
        return "MACHINERY_UNINFORMATIVE"
    g_sig = (global_res["p_init"] <= 0.05) and (global_res["D_init"] > 0)
    n_sites_sig_larger = sum(1 for s in per_site_res if s["sig"])
    n_sites_testable = len(per_site_res)
    if g_sig and n_sites_sig_larger >= 2:
        return "SPATIAL_SIZE_PROMINENCE_CROSS_SITE"
    if g_sig or n_sites_sig_larger >= 1:
        return "SPATIAL_SIZE_POSITION_SITE_LOCAL"
    return "NO_SPATIAL_SIZE_POSITION"


if __name__ == "__main__":
    import sys
    print("=== EPOCH-077 machinery self-check ===")
    docs = load_docs()
    print(f"n docs loaded: {len(docs)}")
    # Self-check: position-shuffle null gives E[D_init] ~ 0
    null_D = position_shuffle_null(docs, n_draws=2000, seed=12345, stat="D_init")
    print(f"null D_init mean={null_D.mean():+.5f} sd={null_D.std():.5f}  (expect ~0)")
    assert abs(null_D.mean()) < 0.05, "null mean not ~0!"
    # observed
    obs = D_init(docs)
    print(f"observed D_init={obs:+.5f}")
    print(f"rho(pos,size)={rho_docs(docs):+.5f}")
    # quick PC
    pc = positive_control(n_docs=322, n_replicates=20, n_draws=800, seed=770077)
    print(f"PC: {pc}")
    print("SELF-CHECK OK")
