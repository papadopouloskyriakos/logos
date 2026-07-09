"""EPOCH-074 full analysis run. Uses machinery.py. Writes data dir artifacts."""
import os, sys, json, random
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import machinery as M

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "epoch_074")
OUT = os.path.abspath(OUT)
os.makedirs(OUT, exist_ok=True)

rng = random.Random(20240704)
toks = M.load_tokens()
N = len(toks)

# ---- 0. inspect ----
forms = defaultdict(set)
for (site, g, f) in toks:
    forms[g].add(f)
lib_forms, adm_forms = len(forms["lib"]), len(forms["adm"])
g_tok = Counter(g for (_, g, _) in toks)
lib_tokens, adm_tokens = g_tok["lib"], g_tok["adm"]
S_shared = M.observed_s_shared(toks)
jaccard = S_shared / len(forms["lib"] | forms["adm"])

site_g = defaultdict(Counter)
for (site, g, f) in toks:
    site_g[site][g] += 1

# ---- confound metric ----
both_ge10 = [(s, c["lib"], c["adm"]) for s, c in site_g.items() if c["lib"] >= 10 and c["adm"] >= 10]
n_both_sites_ge10 = len(both_ge10)
n_swappable = sum(c["lib"] + c["adm"] for s, c in site_g.items() if c["lib"] >= 1 and c["adm"] >= 1)
fixed = sum(c["lib"] + c["adm"] for s, c in site_g.items() if c["lib"] == 0 or c["adm"] == 0)
determinism = fixed / N

inspect = {
    "lib_forms": lib_forms, "lib_tokens": lib_tokens,
    "adm_forms": adm_forms, "adm_tokens": adm_tokens,
    "S_shared": S_shared, "jaccard": jaccard,
    "n_both_sites_ge10": n_both_sites_ge10,
    "n_swappable_tokens": n_swappable,
    "genre_site_determinism": determinism,
    "per_site": {s: {"lib": c["lib"], "adm": c["adm"]} for s, c in sorted(site_g.items(), key=lambda kv: -(kv[1]["lib"]+kv[1]["adm"]))},
}
print("INSPECT:", json.dumps({k:v for k,v in inspect.items() if k!="per_site"}, indent=2))

# ---- 2. GLOBAL null ----
G_REPS = 5000
gvals = [M.global_null_s_shared(toks, rng) for _ in range(G_REPS)]
g_mean = sum(gvals)/G_REPS
g_p_below = sum(v <= S_shared for v in gvals)/G_REPS
g_p_above = sum(v >= S_shared for v in gvals)/G_REPS
closed = M.closed_form_E_S(toks)
print(f"GLOBAL null: mean={g_mean:.3f} p_below={g_p_below:.5f} p_above={g_p_above:.5f} closed_upper={closed:.2f}")

# ---- 4. SITE-STRATIFIED null ----
SS_REPS = 5000
ssvals = [M.site_stratified_null_s_shared(toks, rng) for _ in range(SS_REPS)]
ss_mean = sum(ssvals)/SS_REPS
ss_p_below = sum(v <= S_shared for v in ssvals)/SS_REPS
print(f"SITE-STRATIFIED null: mean={ss_mean:.3f} p_below_sitestrat={ss_p_below:.5f}")

# save raw null distributions
json.dump({"global_null": gvals, "site_stratified_null": ssvals, "obs": S_shared},
          open(os.path.join(OUT, "null_distributions.json"), "w"))
json.dump(inspect, open(os.path.join(OUT, "inspect.json"), "w"), indent=2)

# stash for next steps
json.dump({
    "S_shared": S_shared, "g_mean": g_mean, "g_p_below": g_p_below, "g_p_above": g_p_above,
    "closed_upper": closed, "ss_mean": ss_mean, "ss_p_below": ss_p_below,
    "n_both_sites_ge10": n_both_sites_ge10, "n_swappable_tokens": n_swappable,
    "genre_site_determinism": determinism,
    "lib_forms": lib_forms, "lib_tokens": lib_tokens, "adm_forms": adm_forms, "adm_tokens": adm_tokens,
    "jaccard": jaccard,
}, open(os.path.join(OUT, "_stage.json"), "w"), indent=2)
print("stage saved")
