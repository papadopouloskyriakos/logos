"""
EPOCH-074 POSITIVE CONTROL (SYNTHETIC). Gates the verdict.

Three sub-controls:
 (a) DETECT-BEYOND-SITE: synthetic corpus with the SAME site/genre token structure as observed, but a
     PLANTED genre-specialized lexicon AT BOTH-GENRE SITES (lib vs adm forms disjoint within each
     both-genre site). Measure fraction of >=20 replicates where the site-stratified null flags it
     (power_est = fraction with p_below_sitestrat <= 0.05).
 (b) FALSE-POSITIVE: site-local but genre-NEUTRAL within each site (forms drawn from a shared pool
     within site, no genre specialization). Confirm site-stratified null does NOT flag a genre effect
     (rejection rate <= 0.10).
 (c) GLOBAL-CALIBRATION: confirm GLOBAL null flags a fully genre-partitioned corpus (low p_below) and
     does NOT flag a frequency-only (genre-neutral) corpus (p_below not extreme).

All corpora are SYNTHETIC. Stated as such.
"""
import os, sys, json, random
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import machinery as M

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "epoch_074")
OUT = os.path.abspath(OUT)

# ---- build the observed site/genre token STRUCTURE (counts only) ----
toks = M.load_tokens()
site_g = defaultdict(Counter)
for (site, g, f) in toks:
    site_g[site][g] += 1
# structure: dict site -> {lib: n, adm: n}
structure = {s: {"lib": c["lib"], "adm": c["adm"]} for s, c in site_g.items()}


def make_corpus_genre_specialized(rng, form_alpha=("L", "A")):
    """
    Same site/genre token counts as observed. At BOTH-GENRE sites, plant a genre-specialized lexicon:
    lib forms and adm forms are DISJOINT (drawn from separate pools). At single-genre sites, forms are
    drawn from a generic pool. This is a TRUE genre effect that exists WITHIN sites (beyond site).
    """
    L_pool = [f"L{i}" for i in range(500)]
    A_pool = [f"A{i}" for i in range(500)]
    G_pool = [f"G{i}" for i in range(500)]
    out = []
    for site, c in structure.items():
        nlib, nadm = c["lib"], c["adm"]
        if nlib > 0 and nadm > 0:
            # both-genre site: disjoint lexicons by genre (genre effect WITHIN site)
            lib_forms = [rng.choice(L_pool) for _ in range(nlib)]
            adm_forms = [rng.choice(A_pool) for _ in range(nadm)]
        else:
            # single-genre site: generic pool
            lib_forms = [rng.choice(G_pool) for _ in range(nlib)]
            adm_forms = [rng.choice(G_pool) for _ in range(nadm)]
        for fr in lib_forms:
            out.append((site, "lib", (fr, "x")))
        for fr in adm_forms:
            out.append((site, "adm", (fr, "x")))
    return out


def make_corpus_genre_neutral_within_site(rng):
    """
    Same site/genre token counts. At EVERY site, forms drawn from a SINGLE shared pool regardless of
    genre (genre-NEUTRAL within site). Site-local but no genre effect. Site-stratified null should NOT
    flag this.
    """
    out = []
    for site, c in structure.items():
        nlib, nadm = c["lib"], c["adm"]
        pool = [f"{site}_{i}" for i in range(max(3, (nlib + nadm) // 2 + 2))]
        for _ in range(nlib):
            out.append((site, "lib", (rng.choice(pool), "x")))
        for _ in range(nadm):
            out.append((site, "adm", (rng.choice(pool), "x")))
    return out


def sitestrat_p_below(corpus, obs, rng, reps=500):
    vals = [M.site_stratified_null_s_shared(corpus, rng) for _ in range(reps)]
    return sum(v <= obs for v in vals) / reps, sum(vals)/reps


def global_p_below(corpus, obs, rng, reps=500):
    vals = [M.global_null_s_shared(corpus, rng) for _ in range(reps)]
    return sum(v <= obs for v in vals) / reps, sum(vals)/reps


# ---------------- (a) DETECT-BEYOND-SITE: power_est ----------------
N_REPS = 25
SS_REPS = 500
detect_flags = 0
detect_details = []
for r in range(N_REPS):
    rng = random.Random(10000 + r)
    corp = make_corpus_genre_specialized(rng)
    obs = M.observed_s_shared(corp)
    p, mean = sitestrat_p_below(corp, obs, rng, SS_REPS)
    flag = p <= 0.05
    detect_flags += int(flag)
    detect_details.append({"rep": r, "obs": obs, "ss_mean": round(mean, 2), "p_below_sitestrat": round(p, 4), "flag": flag})
power_est = detect_flags / N_REPS
print(f"(a) DETECT-BEYOND-SITE: power_est = {power_est:.3f} ({detect_flags}/{N_REPS} flagged)")

# ---------------- (b) FALSE-POSITIVE ----------------
fp_flags = 0
fp_details = []
for r in range(N_REPS):
    rng = random.Random(20000 + r)
    corp = make_corpus_genre_neutral_within_site(rng)
    obs = M.observed_s_shared(corp)
    p, mean = sitestrat_p_below(corp, obs, rng, SS_REPS)
    flag = p <= 0.05
    fp_flags += int(flag)
    fp_details.append({"rep": r, "obs": obs, "ss_mean": round(mean, 2), "p_below_sitestrat": round(p, 4), "flag": flag})
false_pos_rate = fp_flags / N_REPS
print(f"(b) FALSE-POSITIVE (genre-neutral within site): rejection rate = {false_pos_rate:.3f} (want <= 0.10)")

# ---------------- (c) GLOBAL-CALIBRATION ----------------
# fully genre-partitioned corpus: lib and adm forms globally disjoint -> GLOBAL null should flag (low p_below)
rng = random.Random(30001)
L_pool = [f"L{i}" for i in range(800)]
A_pool = [f"A{i}" for i in range(800)]
part_corpus = []
for site, c in structure.items():
    for _ in range(c["lib"]):
        part_corpus.append((site, "lib", (rng.choice(L_pool), "x")))
    for _ in range(c["adm"]):
        part_corpus.append((site, "adm", (rng.choice(A_pool), "x")))
obs_part = M.observed_s_shared(part_corpus)
p_part, m_part = global_p_below(part_corpus, obs_part, rng, 500)
global_detect_partition = (p_part <= 0.05) and (obs_part < m_part)
print(f"(c1) GLOBAL on genre-partitioned corpus: obs={obs_part} mean={m_part:.2f} p_below={p_part:.4f} detect={global_detect_partition}")

# frequency-only (genre-neutral globally) corpus: GLOBAL null should NOT flag
rng = random.Random(30002)
G_pool = [f"G{i}" for i in range(800)]
neut_corpus = []
for site, c in structure.items():
    for _ in range(c["lib"] + c["adm"]):
        g = "lib" if len([t for t in neut_corpus if t[0]==site and t[1]=="lib"]) < c["lib"] else "adm"
# simpler: build directly
neut_corpus = []
for site, c in structure.items():
    for _ in range(c["lib"]):
        neut_corpus.append((site, "lib", (rng.choice(G_pool), "x")))
    for _ in range(c["adm"]):
        neut_corpus.append((site, "adm", (rng.choice(G_pool), "x")))
obs_neut = M.observed_s_shared(neut_corpus)
p_neut, m_neut = global_p_below(neut_corpus, obs_neut, rng, 500)
global_detect_neutral_ok = (p_neut > 0.05)
print(f"(c2) GLOBAL on frequency-only (genre-neutral) corpus: obs={obs_neut} mean={m_neut:.2f} p_below={p_neut:.4f} not-flagged={global_detect_neutral_ok}")

global_calib_ok = bool(global_detect_partition and global_detect_neutral_ok)
print(f"(c) GLOBAL-CALIBRATION ok: {global_calib_ok}")

# PC verdict
pc_passed = (power_est >= 0.5) and (false_pos_rate <= 0.10) and global_calib_ok
print(f"\nPC VERDICT: {'PASSED' if pc_passed else 'FAILED'}  (power_est={power_est:.3f}, false_pos={false_pos_rate:.3f}, global_calib={global_calib_ok})")

json.dump({
    "pc_is_synthetic": True,
    "detect_beyond_site": {"power_est": power_est, "n_reps": N_REPS, "ss_reps": SS_REPS, "details": detect_details},
    "false_positive": {"rejection_rate": false_pos_rate, "details": fp_details},
    "global_calibration": {
        "partitioned": {"obs": obs_part, "mean": m_part, "p_below": p_part, "detect": global_detect_partition},
        "frequency_only": {"obs": obs_neut, "mean": m_neut, "p_below": p_neut, "not_flagged": global_detect_neutral_ok},
        "ok": global_calib_ok,
    },
    "pc_passed": pc_passed,
}, open(os.path.join(OUT, "positive_control.json"), "w"), indent=2)
print("PC saved")
