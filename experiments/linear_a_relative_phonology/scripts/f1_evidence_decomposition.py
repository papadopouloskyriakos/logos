#!/usr/bin/env python3
"""F1 -- CROSS-SCRIPT EVIDENCE DECOMPOSITION (Constitution v2.2, Art. XI/XII/XV).

For the proposed Linear A <-> Linear B sign correspondences (the 59 shared-AB anchor
signs), record SEPARATE (NOT combined) scores across EIGHT evidence channels:

    1. shape .......................... Salgarella 2020 homomorphy grade
    2. stroke_structure ............... palaeographic stroke decomposition
    3. orientation .................... glyph orientation / mirroring
    4. chronology ..................... script-level + LA sign-level date span
    5. geography ...................... LA find-site distribution per sign
    6. admin_function ................. distributional (PPMI/SVD) admin-role channel
    7. scholarly_correspondence ....... Steele & Meissner 2017 Cypriot-stability status
    8. source_dependency .............. provenance / independence of each value claim

We do NOT re-run the value-transfer test (Foundry: NON-CIRCULAR admin channel = NULL,
crossscript_gate = REFUTE_LOTO_FRAGILE) nor re-litigate the SHAPE leg (circular =
LB-identity, capped <=0.75). The purpose here is orthogonal: DECOMPOSE the combined
"cross-script correspondence" evidence into its channels and ask, mechanically, which
channel (if any) is INDEPENDENTLY CALIBRATABLE -- i.e. produces a per-correspondence
score that can be graded against a NON-CIRCULAR known-truth benchmark without smuggling
in the LB phonetic value it is supposed to predict.

NON-CIRCULAR DISCIPLINE: LB phonetic values (conventional_value) are used ONLY as a
grading KEY on the calibration benchmarks, NEVER as an input to any channel score.

Reads (read-only):
  crossscript_gate/anchors.csv        -- the 59 correspondence rows (shape/cypriot/source)
  corpus/silver/inscriptions_structured.json -- LA per-sign site + context (geo + chrono)
  foundry wp4_summary.txt / wp4_calibration.json -- admin-channel LOTO calibration (imported)

Writes:
  data/F1_decompose.json
  reports/F_EVIDENCE_DECOMPOSITION.md
Deterministic seed 20260708.
"""
from __future__ import annotations
import csv, json, math, os, sys
from collections import Counter, defaultdict

SEED = 20260708
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))
REPORTS = os.path.abspath(os.path.join(HERE, "..", "reports"))
MAIN = "/home/claude-runner/gitlab/n8n/logos"
GATE = "/home/claude-runner/gitlab/n8n/logos-la-lb-continuity/experiments/crossscript_gate"
FOUNDRY = "/home/claude-runner/gitlab/n8n/logos-linear-a-relative-phonology-seals/experiments/linear_a_foundry"
SILVER = os.path.join(MAIN, "corpus/silver/inscriptions_structured.json")

# ---------------------------------------------------------------------------
# small stats helpers (self-contained, no model, no LB value as input)
# ---------------------------------------------------------------------------
def shannon_bits(counts):
    tot = sum(counts)
    if tot <= 0:
        return 0.0
    h = 0.0
    for c in counts:
        if c > 0:
            p = c / tot
            h -= p * math.log2(p)
    return h


def norm_entropy_categorical(values):
    """Normalized entropy in [0,1] of a categorical vector across correspondences.
    0 => channel is constant (no power to separate correspondences); 1 => uniform."""
    c = Counter(values)
    k = len(c)
    if k <= 1:
        return 0.0
    return shannon_bits(list(c.values())) / math.log2(k)


def cv(values):
    """Coefficient of variation of a numeric vector (dispersion, scale-free)."""
    vals = [v for v in values if v is not None]
    if not vals:
        return None
    m = sum(vals) / len(vals)
    if m == 0:
        return 0.0
    var = sum((v - m) ** 2 for v in vals) / len(vals)
    return math.sqrt(var) / abs(m)


# ---------------------------------------------------------------------------
# 1. load the 59 correspondence rows
# ---------------------------------------------------------------------------
rows = list(csv.DictReader(open(os.path.join(GATE, "anchors.csv"))))


def shape_ord(g):
    g = (g or "").lower()
    if "homophone" in g:
        return 2  # Salgarella dark-blue (homomorphic AND likely homophone)
    if "homomorphic" in g:
        return 1  # Salgarella light-blue (homomorphic only)
    return 0


def cypriot_ord(s):
    s = (s or "").strip()
    if s == "true":
        return 2
    if s == "candidate":
        return 1
    return 0


def source_indep_class(value_source):
    """How independent is the VALUE claim behind this correspondence?
    Returns (class, n_primary_value_sources). All are 'secondary' (derived, not
    primary-attested) -- the point of the source-dependency channel."""
    vs = value_source or ""
    if vs.startswith("litindex"):
        return ("litindex_seed(secondary)", 0)   # LB->LA value transfer seed; not a primary attestation
    if "bridge" in vs:
        return ("datapy_bridge(secondary)", 0)   # romanization==Unicode; needs citation before seed status
    return ("other", 0)


# ---------------------------------------------------------------------------
# 2. LA per-sign geography (site) + chronology (context) from silver
# ---------------------------------------------------------------------------
insc = json.load(open(SILVER))
sign_sites = defaultdict(Counter)
sign_contexts = defaultdict(Counter)
NORM = {"RA₂": "RA2", "RA2": "RA2", "PA₃": "PA3"}  # normalize subscripts to romanization used in anchors


def norm_sign(s):
    s = s.replace("₂", "2").replace("₃", "3").replace("₄", "4")
    return s


for it in insc:
    site = it.get("site") or "?"
    ctx = it.get("context") or "?"
    seen = set()
    for st in it.get("stream", []):
        if st.get("t") == "word":
            for sg in st.get("signs", []):
                sg = norm_sign(sg)
                seen.add(sg)
    for sg in seen:
        sign_sites[sg][site] += 1
        sign_contexts[sg][ctx] += 1

# ---------------------------------------------------------------------------
# 3. admin-function channel calibration -- IMPORTED, not re-run (Foundry wp4)
#    (non-circular shared-AB LOTO on the distributional/PPMI-SVD channel)
# ---------------------------------------------------------------------------
admin_cal = {
    "benchmark": "shared-AB held-out LOTO (leave-one-toponym-out), value graded by LB conventional value",
    "channel": "distributional admin-role (PPMI + SVD co-occurrence, Procrustes-aligned) -- uses NO phonetic value",
    "R@1": 0.000, "R@5": 0.071, "R@10": 0.125, "MRR": 0.0624,
    "chance_R@1": 0.0112, "shuffled_null_R@5": 0.066, "shuffled_null_MRR": 0.0622,
    "perm_p_R@5": 0.60, "perm_p_MRR": 0.50,
    "verdict": "NULL -- does not beat the shuffled null; no non-circular value power at LA scale",
    "source": "linear_a_foundry/data/wp4_summary.txt (wp4_cross_script_evolution.py CAL#2)",
    "crossscript_gate_concordance": "REFUTE_LOTO_FRAGILE; distributional channel = 0.0000 (independent 3rd null confirmation)",
}
shape_cal = {
    "benchmark": "S&M-2017 stable-11 recovery (Fisher one-sided), value graded by Cypriot stability",
    "recall_stable11": 1.00, "fisher_p": 1.59e-05,
    "twobytwo": {"homophone&stable": 11, "homophone&notstable": 14, "other&stable": 0, "other&notstable": 34},
    "verdict": "CIRCULAR -- shape grade = Salgarella LB-homophony judgment; separates the stable-11 perfectly "
               "but confounded (same latent LB-identity fact). Capped <=0.75.",
    "source": "linear_a_foundry/data/wp4_summary.txt (wp4_cross_script_evolution.py CAL#1)",
}

# ---------------------------------------------------------------------------
# 4. build the per-correspondence decomposition table (channels kept SEPARATE)
# ---------------------------------------------------------------------------
table = []
for r in rows:
    sid = r["sign_id"]
    gs = sign_sites.get(sid, Counter())
    gc = sign_contexts.get(sid, Counter())
    scls, nprim = source_indep_class(r["value_source"])
    la_att = int(r["la_attestations"] or 0)
    row = {
        "sign_id": sid,
        "ab_number": r["ab_number"],
        "value_KEY_gradingonly": r["conventional_value"],  # NEVER an input; grading key only
        # --- 8 SEPARATE channel scores (do NOT combine) ---
        "ch_shape": {
            "grade_ord": shape_ord(r["homomorphy_grade"]),
            "grade": ("homophone" if shape_ord(r["homomorphy_grade"]) == 2
                      else "homomorphic" if shape_ord(r["homomorphy_grade"]) == 1 else "none"),
            "populated": True, "circular": True, "source": "Salgarella 2020",
        },
        "ch_stroke_structure": {
            "score": None, "populated": False,
            "note": "no LA<->LB stroke-decomposition dataset in repo (SigLA signs carry id/class/gorila_number only)",
        },
        "ch_orientation": {
            "score": None, "populated": False,
            "note": "no glyph-orientation / mirroring dataset in repo; not a distinct measurable channel here",
        },
        "ch_chronology": {
            "script_level": "LA(MMII-LMI) -> LB(LMII-IIIB) -> Cypriot(later)",
            "la_context_span_n": len(gc),
            "la_context_entropy_bits": round(shannon_bits(list(gc.values())), 4),
            "la_contexts": dict(gc),
            "sign_discriminative_for_correspondence": False,  # every LA sign predates all LB; no per-sign LB-date
        },
        "ch_geography": {
            "n_sites": len(gs),
            "site_entropy_bits": round(shannon_bits(list(gs.values())), 4),
            "top_site": (gs.most_common(1)[0][0] if gs else None),
            "populated": len(gs) > 0,
            "sign_discriminative_for_correspondence": False,  # LA(Crete) vs LB(Knossos/mainland) share no site system
        },
        "ch_admin_function": {
            "la_attestations": la_att,
            "loto_eligible": la_att >= 5,     # channel operates at sign level only if attested
            "populated": True, "circular": False,
            "channel_verdict": "NULL (calibrated, see admin_calibration)",
        },
        "ch_scholarly_correspondence": {
            "cypriot_stable_ord": cypriot_ord(r["cypriot_stable"]),
            "cypriot_stable": r["cypriot_stable"],
            "sm2017_tier": r["sm2017_tier"],
            "populated": bool(r["sm2017_tier"]) or r["cypriot_stable"] != "not_listed",
            "circular": True,  # scholarly status is itself a value judgment on the same latent fact
            "source": "Steele & Meissner 2017",
        },
        "ch_source_dependency": {
            "value_source": r["value_source"],
            "independence_class": scls,
            "n_primary_value_sources": nprim,
            "source_status": r["source_status"],
            "note": "predictive? NO -- this is an audit instrument (Art. XI), not a value predictor",
        },
    }
    table.append(row)

# ---------------------------------------------------------------------------
# 5. per-channel meta-assessment (mechanical, across all 59 correspondences)
# ---------------------------------------------------------------------------
n = len(table)

def frac(pred):
    return round(sum(1 for t in table if pred(t)) / n, 4)

channel_meta = {}

# shape
shape_vals = [t["ch_shape"]["grade_ord"] for t in table]
channel_meta["shape"] = {
    "coverage": frac(lambda t: t["ch_shape"]["populated"]),
    "discriminative_norm_entropy": round(norm_entropy_categorical(shape_vals), 4),
    "non_circular": False,
    "independently_calibratable": False,
    "calibration": shape_cal,
    "reason": "Circular: the grade IS an LB-homophony judgment (=identity). Calibrates perfectly but "
              "confounded with the value it should predict. Capped <=0.75. NOT independently calibratable.",
}
# stroke_structure
channel_meta["stroke_structure"] = {
    "coverage": frac(lambda t: t["ch_stroke_structure"]["populated"]),
    "discriminative_norm_entropy": 0.0,
    "non_circular": True,
    "independently_calibratable": False,
    "calibration": None,
    "reason": "Unpopulated: no LA<->LB stroke-decomposition dataset in the repo. Cannot be scored, so cannot be "
              "calibrated. (Would in principle be non-circular if a palaeographic stroke corpus were acquired.)",
}
# orientation
channel_meta["orientation"] = {
    "coverage": frac(lambda t: t["ch_orientation"]["populated"]),
    "discriminative_norm_entropy": 0.0,
    "non_circular": True,
    "independently_calibratable": False,
    "calibration": None,
    "reason": "Unpopulated: no glyph-orientation dataset. A sub-facet of shape; not independently measurable here.",
}
# chronology
chron_disc = [t["ch_chronology"]["la_context_span_n"] for t in table]
channel_meta["chronology"] = {
    "coverage": 1.0,
    "discriminative_norm_entropy": 0.0,   # by construction: script-level, identical direction for every sign
    "la_context_span_cv": round(cv(chron_disc) or 0.0, 4),
    "non_circular": True,
    "independently_calibratable": False,
    "calibration": None,
    "reason": "Script-level ordering (all LA predates all LB). Not sign-discriminative for a CORRESPONDENCE: it "
              "cannot pin which LB sign an LA sign maps to. LA-internal date span varies but carries no LB-value info.",
}
# geography
geo_nsites = [t["ch_geography"]["n_sites"] for t in table]
geo_ent = [t["ch_geography"]["site_entropy_bits"] for t in table]
channel_meta["geography"] = {
    "coverage": frac(lambda t: t["ch_geography"]["populated"]),
    "discriminative_norm_entropy": None,  # continuous; report CV instead
    "n_sites_cv": round(cv(geo_nsites) or 0.0, 4),
    "site_entropy_cv": round(cv(geo_ent) or 0.0, 4),
    "n_sites_range": [min(geo_nsites), max(geo_nsites)],
    "non_circular": True,
    "independently_calibratable": False,
    "calibration": None,
    "reason": "LA per-sign site profiles ARE measurable and vary across signs, but LA (Crete find-sites) and LB "
              "(Knossos/mainland archives) share no site system, so no non-circular held-out benchmark aligns a "
              "geographic score to an LB correspondence. Measurable but not correspondence-calibratable.",
}
# admin_function -- the load-bearing channel for the F1 question
admin_att = [t["ch_admin_function"]["la_attestations"] for t in table]
channel_meta["admin_function"] = {
    "coverage": frac(lambda t: t["ch_admin_function"]["populated"]),
    "loto_eligible_frac": frac(lambda t: t["ch_admin_function"]["loto_eligible"]),
    "la_attestation_cv": round(cv(admin_att) or 0.0, 4),
    "non_circular": True,
    "independently_calibratable": True,   # <-- the ONE channel that is
    "calibration": admin_cal,
    "reason": "The ONLY channel that is BOTH non-circular (uses no LB value) AND has a non-circular held-out "
              "benchmark (shared-AB LOTO). It IS independently calibratable -- and when calibrated it is NULL "
              "(R@1=0.000, perm-p(R@5)=0.60). Independently calibratable, independently refuted.",
}
# scholarly_correspondence
sch_vals = [t["ch_scholarly_correspondence"]["cypriot_stable_ord"] for t in table]
channel_meta["scholarly_correspondence"] = {
    "coverage": frac(lambda t: t["ch_scholarly_correspondence"]["populated"]),
    "discriminative_norm_entropy": round(norm_entropy_categorical(sch_vals), 4),
    "n_stable": sum(1 for t in table if t["ch_scholarly_correspondence"]["cypriot_stable"] == "true"),
    "n_candidate": sum(1 for t in table if t["ch_scholarly_correspondence"]["cypriot_stable"] == "candidate"),
    "non_circular": False,
    "independently_calibratable": False,
    "calibration": {"note": "same benchmark as shape (S&M stable-11); confounded", **shape_cal},
    "reason": "Scholarly Cypriot-stability status is itself an expert value judgment on the same latent identity. "
              "Grading it by LB/Cypriot value is circular. High-value but not INDEPENDENT of the value channel.",
}
# source_dependency
src_classes = [t["ch_source_dependency"]["independence_class"] for t in table]
channel_meta["source_dependency"] = {
    "coverage": 1.0,
    "discriminative_norm_entropy": round(norm_entropy_categorical(src_classes), 4),
    "class_distribution": dict(Counter(src_classes)),
    "n_correspondences_with_primary_value_source": sum(
        1 for t in table if t["ch_source_dependency"]["n_primary_value_sources"] > 0),
    "all_value_claims_secondary": all(
        t["ch_source_dependency"]["n_primary_value_sources"] == 0 for t in table),
    "non_circular": True,
    "independently_calibratable": False,
    "calibration": None,
    "reason": "A meta / audit channel (Art. XI), not a value predictor: it measures HOW independent each claim is, "
              "not what value a sign has. Finding: 0/59 correspondences rest on a PRIMARY value attestation "
              "(52 litindex-seed + 7 bridge, all secondary); the only primary legs are shape (Salgarella, "
              "pending-primary/absent from repo) and Cypriot (S&M) -- both circular. So even the provenance audit "
              "shows no independent primary support for any LA<->LB VALUE.",
}

# ---------------------------------------------------------------------------
# 6. summary verdict
# ---------------------------------------------------------------------------
calibratable = [c for c, m in channel_meta.items() if m["independently_calibratable"]]
summary = {
    "n_correspondences": n,
    "n_channels": 8,
    "channels_populated": [c for c, m in channel_meta.items() if m.get("coverage", 0) > 0],
    "channels_unpopulated": [c for c, m in channel_meta.items() if m.get("coverage", 0) == 0],
    "channels_non_circular": [c for c, m in channel_meta.items() if m["non_circular"]],
    "channels_circular": [c for c, m in channel_meta.items() if not m["non_circular"]],
    "channels_independently_calibratable": calibratable,
    "calibratable_channel_outcome": ("admin_function=NULL" if "admin_function" in calibratable else "NONE"),
    "verdict": (
        "EXACTLY ONE of the eight channels (admin_function, distributional) is BOTH non-circular AND "
        "independently calibratable against a non-circular held-out benchmark -- and it calibrates to NULL. "
        "shape and scholarly_correspondence calibrate but are CIRCULAR (confounded with LB identity, capped "
        "<=0.75). chronology is not sign-discriminative; stroke_structure and orientation are unpopulated; "
        "geography is measurable but has no correspondence-aligned non-circular benchmark; source_dependency is "
        "a provenance audit (0/59 correspondences have a primary VALUE source). Net: DECOMPOSITION CONFIRMS no "
        "channel yields an independently-calibratable NON-NULL, NON-CIRCULAR LA<->LB value correspondence."
    ),
}

out = {
    "experiment": "F1_cross_script_evidence_decomposition",
    "constitution": "v2.2 (Art. XI source-dependency, Art. XII no-grade-by-creating-rule, Art. XV transfer licences)",
    "seed": SEED,
    "non_circular_note": "LB conventional_value used ONLY as a grading key on benchmarks; never a channel input.",
    "channel_definitions": {
        "shape": "Salgarella 2020 LA<->LB homomorphy grade (none/homomorphic/homophone)",
        "stroke_structure": "palaeographic stroke decomposition (UNAVAILABLE in repo)",
        "orientation": "glyph orientation / mirroring (UNAVAILABLE in repo)",
        "chronology": "script-level ordering + LA-internal per-sign date span",
        "geography": "LA per-sign find-site distribution (n_sites, entropy)",
        "admin_function": "distributional PPMI/SVD admin-role channel (non-circular, LOTO-calibrated)",
        "scholarly_correspondence": "Steele & Meissner 2017 Cypriot-stability status",
        "source_dependency": "provenance / independence class of each value claim (audit)",
    },
    "admin_calibration": admin_cal,
    "shape_calibration": shape_cal,
    "channel_meta": channel_meta,
    "per_correspondence_table": table,
    "summary": summary,
}

os.makedirs(DATA, exist_ok=True)
os.makedirs(REPORTS, exist_ok=True)
with open(os.path.join(DATA, "F1_decompose.json"), "w") as f:
    json.dump(out, f, indent=1)

# ---------------------------------------------------------------------------
# report
# ---------------------------------------------------------------------------
def yn(b):
    return "YES" if b else "no"

lines = []
lines.append("# F_EVIDENCE_DECOMPOSITION — cross-script LA↔LB channels, kept separate\n")
lines.append(f"**Task F1** · Constitution v2.2 (Art. XI/XII/XV) · seed {SEED} · "
             f"{n} shared-AB correspondences · 8 channels\n")
lines.append("Articles triggered: XI (source-dependency graph), XII (no grading a target by the rule that "
             "created it), XV (transfer licences — none earned). Non-circular gate: LB `conventional_value` "
             "is a grading key on benchmarks ONLY, never a channel input.\n")
lines.append("## What F1 does and does NOT do\n")
lines.append("- Does NOT re-run the value-transfer test (Foundry admin channel = NULL; crossscript_gate = "
             "`REFUTE_LOTO_FRAGILE`) nor re-litigate the SHAPE leg (circular = LB-identity, capped ≤0.75).\n"
             "- DOES decompose the combined 'cross-script correspondence' evidence into 8 separate channels and "
             "ask, mechanically, which channel (if any) is **independently calibratable** — i.e. scores a "
             "correspondence against a non-circular held-out benchmark without using the LB value it predicts.\n")
lines.append("## Per-channel decomposition (across all 59 correspondences)\n")
lines.append("| channel | coverage | discriminative | non-circular | indep. calibratable | outcome |")
lines.append("|---|---|---|---|---|---|")
order = ["shape", "stroke_structure", "orientation", "chronology", "geography",
         "admin_function", "scholarly_correspondence", "source_dependency"]
for c in order:
    m = channel_meta[c]
    disc = m.get("discriminative_norm_entropy")
    if disc is None:
        disc = m.get("site_entropy_cv", m.get("la_context_span_cv"))
        disc = f"CV={disc}" if disc is not None else "—"
    else:
        disc = f"H={disc}"
    if c == "admin_function":
        outcome = "**calibrated → NULL**"
    elif c in ("shape", "scholarly_correspondence"):
        outcome = "calibrates but CIRCULAR"
    elif c in ("stroke_structure", "orientation"):
        outcome = "unpopulated"
    elif c == "chronology":
        outcome = "not sign-discriminative"
    elif c == "geography":
        outcome = "measurable, no aligned benchmark"
    else:
        outcome = "audit channel (not predictive)"
    lines.append(f"| {c} | {m.get('coverage')} | {disc} | {yn(m['non_circular'])} | "
                 f"{yn(m['independently_calibratable'])} | {outcome} |")
lines.append("")
lines.append("## The one calibratable channel: admin_function\n")
a = admin_cal
lines.append(f"- Channel: {a['channel']}\n- Benchmark: {a['benchmark']}\n"
             f"- R@1={a['R@1']} R@5={a['R@5']} R@10={a['R@10']} MRR={a['MRR']} "
             f"(chance R@1={a['chance_R@1']}; shuffled-null R@5={a['shuffled_null_R@5']} MRR={a['shuffled_null_MRR']})\n"
             f"- perm-p(R@5)={a['perm_p_R@5']} perm-p(MRR)={a['perm_p_MRR']}\n"
             f"- **{a['verdict']}**\n- Concordance: {a['crossscript_gate_concordance']}\n"
             f"- Source: {a['source']}\n")
lines.append("## Why each other channel is NOT independently calibratable\n")
for c in order:
    if c == "admin_function":
        continue
    lines.append(f"- **{c}** — {channel_meta[c]['reason']}\n")
lines.append("## Source-dependency finding (Art. XI)\n")
sd = channel_meta["source_dependency"]
lines.append(f"- Value-source classes: {sd['class_distribution']}\n"
             f"- Correspondences with a PRIMARY value source: "
             f"{sd['n_correspondences_with_primary_value_source']}/{n}\n"
             f"- All value claims secondary: {yn(sd['all_value_claims_secondary'])} — the only primary legs are "
             f"shape (Salgarella, pending-primary / book absent from repo) and Cypriot (S&M 2017), both CIRCULAR.\n")
lines.append("## Verdict\n")
lines.append(summary["verdict"] + "\n")
lines.append(f"Compliance: no combined score computed; LB value used as grading key only (Art. XII honoured); "
             f"transfer licence unchanged (SEMANTIC+ NOT_AUTHORIZED, Art. XV). Independently-calibratable "
             f"channels: {calibratable or 'admin_function (→NULL)'}\n")

with open(os.path.join(REPORTS, "F_EVIDENCE_DECOMPOSITION.md"), "w") as f:
    f.write("\n".join(lines))

# console summary
print(f"F1 done: {n} correspondences x 8 channels")
print("populated:", summary["channels_populated"])
print("unpopulated:", summary["channels_unpopulated"])
print("non-circular:", summary["channels_non_circular"])
print("circular:", summary["channels_circular"])
print("independently_calibratable:", summary["channels_independently_calibratable"], "->",
      summary["calibratable_channel_outcome"])
print("geo n_sites range:", channel_meta["geography"]["n_sites_range"],
      "site_entropy_cv:", channel_meta["geography"]["site_entropy_cv"])
print("shape discriminative H:", channel_meta["shape"]["discriminative_norm_entropy"])
print("scholarly discriminative H:", channel_meta["scholarly_correspondence"]["discriminative_norm_entropy"],
      "n_stable:", channel_meta["scholarly_correspondence"]["n_stable"])
print("source_dep classes:", channel_meta["source_dependency"]["class_distribution"],
      "all_secondary:", channel_meta["source_dependency"]["all_value_claims_secondary"])
