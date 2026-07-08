#!/usr/bin/env python3
"""TASK K — Active evidence-acquisition ranking (mechanical).

Converts the WP-G anchor-threshold surface into expected equivalence-class
reduction per candidate acquisition, builds the per-sign active-learning queue,
and ranks source classes honestly (absolute-value bits vs relative-only value
kept strictly separate, Art. XV).

All gain numbers are read from data/controls/anchor_threshold/surface.json
(measured cells); anything extrapolated is flagged "EXTRAPOLATED" with the
measured upper bound attached. Seed 20260708 (no stochastic step here; the
ranking is deterministic arithmetic).

Outputs:
  data/source_expansion/acquisition_queue.json
"""
import json, math, os, hashlib

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED = 20260708

surface = json.load(open(f"{BASE}/data/controls/anchor_threshold/surface.json"))
lattice = json.load(open(f"{BASE}/data/anchor_lattice/lattice.json"))
uni = json.load(open(f"{BASE}/data/sign_universe/conservative.json"))
signs = uni["signs"]

# ---------------------------------------------------------------- gain model
# Measured cells (LA-matched degraded bench, coverage 0.20 — the honest grid):
bench = {(r["n_anchors"], r["slots"]): r for r in surface["benches"]["degraded_LB_LA_matched"]["rows"]}
# Measured cells (opaque LB, coverage 0.55 — the generous upper bound):
main = {(r["n_anchors"], r["slots"], r["lineages"]): r for r in surface["surface_opaque_LB"]}

LA_RESIDUAL_LOG10 = surface["linear_A_operating_point"]["collapsed_SEED_A_0"]["residual_ambiguity_log10"]  # 63.3765

def first_anchor_gain(slots):
    """Expected gain of the FIRST dependency-distinct anchor with `slots` slots,
    at the LA-matched operating point. Measured for slots<=2; slots>=4 is a
    ratio extrapolation flagged as such, with the coverage-0.55 measured cell
    as upper bound."""
    if slots in (1, 2):
        r = bench[(1, slots)]
        return {"eqred_log10": round(r["eq_reduction"], 2),
                "abs_recovery": round(r["abs_recovery"], 3),
                "heldout_word": round(r["heldout_word_recovery"], 3),
                "basis": f"MEASURED degraded_LB_LA_matched cell (1,{slots})"}
    # ratio extrapolation from the cov-0.55 surface (lineages=1 row)
    r2la, r2 = bench[(1, 2)], main[(1, 2, 1)]
    rs = main.get((1, slots, 1))
    eq = r2la["eq_reduction"] * (rs["eq_reduction"] / r2["eq_reduction"])
    ab = r2la["abs_recovery"] * (rs["abs_recovery"] / r2["abs_recovery"])
    return {"eqred_log10": round(eq, 2), "abs_recovery": round(ab, 3),
            "heldout_word": round(r2la["heldout_word_recovery"] * (rs["heldout_word_recovery"] / max(r2["heldout_word_recovery"], 1e-9)), 3),
            "basis": f"EXTRAPOLATED (LA-matched slots-2 cell x cov-0.55 slots ratio); measured cov-0.55 upper bound eqred={rs['eq_reduction']:.1f}, abs={rs['abs_recovery']:.3f}"}

G1, G2, G4, G8 = first_anchor_gain(1), first_anchor_gain(2), first_anchor_gain(4), first_anchor_gain(8)
FRONTIER = surface["min_config_abs90_LB"]          # (12,8,12) -> abs 0.972
FOOTHOLD = surface["min_config_abs75_LB"]          # (3,8,3)  -> abs ~0.76
COVERAGE_SAT = "abs saturates ~0.65 by coverage 0.7-1.0 at fixed anchors; at 0 anchors abs=0.0 and eqred=0.0 for ALL coverage values (measured)"

# ------------------------------------------------------- source-class table
# P(realizes >=1 dependency-distinct multi-slot anchor | acquisition happens),
# P(available within ~2 years), slots if realized. Probabilities are stated
# estimates (flagged), NOT measurements; everything downstream of them is arithmetic.
SOURCE_CLASSES = [
 dict(id="new_inscription_occurrence", anchor_producing=False, slots=0, p_anchor=0.0,
      p_avail=0.9, licence="varies (excavation/publication)", automation="low (manual ingest)",
      value_free_role="raises relative-channel coverage + n_documents; G: 0 anchors => 0.0 abs at every coverage",
      note="~0-2 new LA docs/yr base rate"),
 dict(id="longer_continuous_context", anchor_producing=False, slots=0, p_anchor=0.0,
      p_avail=1.0, licence="published (Ariadne Suppl. 2025)", automation="medium (transcription exists)",
      value_free_role="segmentation/formula/morphology channels; held-out test bed; 0 absolute bits",
      note="Anetaki ivory scepter ~119 signs IS this class, available now"),
 dict(id="new_site", anchor_producing=False, slots=0, p_anchor=0.0,
      p_avail=0.3, licence="excavation-gated", automation="low",
      value_free_role="site_coverage axis is mild (abs 0.463@0.2 -> 0.617@1.0) and only matters once anchors exist",
      note=""),
 dict(id="new_join", anchor_producing=True, slots=2, p_anchor=0.02,
      p_avail=0.5, licence="museum access (HM/INSTAP)", automation="medium (bbox/3D match)",
      value_free_role="lengthens words; could push PA-I-TO-type pins past the >=4-slot bar",
      note="anchor only if a join completes an externally-equated word"),
 dict(id="high_resolution_image", anchor_producing=False, slots=0, p_anchor=0.0,
      p_avail=0.7, licence="CC BY-NC-SA (SigLA) / museum", automation="high",
      value_free_role="reading corrections + join detection; shape channel carries 0 value bits (WP-E: AUC 0.57-0.60, H-lineage circular)",
      note=""),
 dict(id="stroke_decomposition", anchor_producing=False, slots=0, p_anchor=0.0,
      p_avail=0.5, licence="CC BY-NC-SA; needs Salgarella/Castellan raw vectors", automation="high once unblocked",
      value_free_role="unblocks WP-E; still not value-bearing (Art. XI: H lineage circular for values)",
      note="SOURCE_BLOCKED today"),
 dict(id="external_name_equation", anchor_producing=True, slots=4, p_anchor=1.0,
      p_avail=0.03, licence="publication", automation="low",
      value_free_role="—",
      note="THE unlock: LIN_EG is the only dependency-distinct value-bearing lineage (SEED_A=0 because {Eg-rendered Cretan toponyms} ∩ {LA >=4-slot words} = {Phaistos,3-slot} only); requires a NEW LA attestation of Amnisos/Kydonia/Knossos-class name"),
 dict(id="commodity_measure_equation", anchor_producing=False, slots=0, p_anchor=0.0,
      p_avail=0.8, licence="published", automation="medium",
      value_free_role="L3-functional only; loan-etymologies (KU-NI-SU etc.) presuppose the reading (Art. XII circular) => 0 absolute bits",
      note=""),
 dict(id="bilingual_biscriptal_fragment", anchor_producing=True, slots=8, p_anchor=1.0,
      p_avail=0.002, licence="excavation-gated", automation="low",
      value_free_role="—",
      note="Rosetta-class; none found in ~120 yrs; if long enough could reach the (12,8,12) frontier in one object, but Art.-XI treatment of a single-provenance document caps effective lineages (bounds reported both ways)"),
 dict(id="anetaki_final_edition_delta", anchor_producing=False, slots=0, p_anchor=0.0,
      p_avail=1.0, licence="published (Kanta et al., Ariadne 2025; suppl. series)", automation="medium",
      value_free_role="new readings/joins for KN cult-center pieces + PROSPECTIVE held-out gold for L2/L3 claims (libation-order, A-prefixation)",
      note="scepter + overview published 2025; full final edition of all cult-center epigraphy still rolling"),
]

for sc in SOURCE_CLASSES:
    if sc["anchor_producing"] and sc["p_anchor"] > 0:
        g = {2: G2, 4: G4, 8: G8}[sc["slots"]]
        sc["gain_if_realized"] = g
        sc["expected_eqred_log10"] = round(sc["p_anchor"] * sc["p_avail"] * g["eqred_log10"], 3)
        sc["expected_abs_recovery"] = round(sc["p_anchor"] * sc["p_avail"] * g["abs_recovery"], 4)
    else:
        sc["gain_if_realized"] = {"eqred_log10": 0.0, "abs_recovery": 0.0,
                                  "basis": "MEASURED: 0-anchor row => 0.0 abs / 0.0 eqred at every coverage (value-free channels are relabeling-invariant)"}
        sc["expected_eqred_log10"] = 0.0
        sc["expected_abs_recovery"] = 0.0

# Bilingual special case: bounds both ways (Art. XI ambiguity for single-provenance docs)
for sc in SOURCE_CLASSES:
    if sc["id"] == "bilingual_biscriptal_fragment":
        # conservative: 1 effective lineage, 8 slots -> G8; liberal: reaches frontier
        sc["bounds_if_realized"] = {
            "conservative_1_lineage": G8,
            "liberal_many_word_equations": {"eqred_log10": round(FRONTIER["eq_reduction"], 1),
                                            "abs_recovery": FRONTIER["abs_recovery"],
                                            "basis": "measured (12,8,12) frontier cell"}}
        sc["expected_eqred_log10"] = round(sc["p_avail"] * FRONTIER["eq_reduction"], 3)  # liberal bound expectation
        sc["expected_abs_recovery"] = round(sc["p_avail"] * FRONTIER["abs_recovery"], 4)

# --------------------------------------------------------- per-sign queue
# Corpus token totals for frequency-based P(sign appears in a new q-slot anchor word)
tot_tokens = sum(v["occurrence_count"] for v in signs.values())
def p_in_anchor(occ, q=4):
    f = occ / max(tot_tokens, 1)
    return 1.0 - (1.0 - f) ** q

def sign_row(k):
    v = signs[k]
    dark = not (v.get("has_anchor_coverage") or v.get("has_substitution_coverage"))
    return dict(
        target_sign=k, sign_class=v["class"], occurrences=v["occurrence_count"],
        n_sites=len(v.get("site_distribution", {})),
        stroke_image=bool(v.get("stroke_image_available")),
        relationally_dark=dark,
        p_appears_in_new_4slot_anchor_word=round(p_in_anchor(v["occurrence_count"]), 4),
    )

# targets: A-only syllabograms (the campaign question) + zero-coverage variables + the 3 pins
aonly = sorted([k for k, v in signs.items() if v["class"] == "A-only"],
               key=lambda k: -signs[k]["occurrence_count"])
zerocov = [k for k, v in signs.items()
           if not v.get("stroke_image_available") and not v.get("has_anchor_coverage")
           and not v.get("has_substitution_coverage") and v["class"] != "numeral"]
pins = ["*49", "*79", "ZU"]

queue = []
for k in aonly[:20] + [z for z in zerocov if z not in aonly[:20]][:10] + [p for p in pins if p in signs]:
    row = sign_row(k)
    # needed evidence, honestly: value bits ONLY via an external equation containing the sign
    row["needed_evidence"] = ("occurrence inside an externally-equated word "
                              "(external_name_equation / bilingual)" if row["relationally_dark"]
                              else "second dependency-distinct lineage for the existing pin")
    row["best_source_class"] = "external_name_equation"
    row["expected_value_bits_from_context_only"] = 0.0  # measured: 0-anchor row
    # expected eqred contribution if the sign lands inside the first indep 4-slot anchor
    row["expected_eqred_log10"] = round(row["p_appears_in_new_4slot_anchor_word"] * 0.03 * G4["eqred_log10"], 5)
    queue.append(row)
queue.sort(key=lambda r: (-r["expected_eqred_log10"], -r["occurrences"]))

# ------------------------------------------------------ concrete acquisitions
ACQ = [
 dict(rank=0, id="ACQ-01", name="Ingest the Anetaki ivory scepter (Knossos cult center, ~119 signs; Kanta, Nakassis, Palaima & Perna, Ariadne Supplements, 2025)",
      source_class=["longer_continuous_context", "new_inscription_occurrence", "anetaki_final_edition_delta"],
      status="AVAILABLE_NOW (published 2025; NOT in silver corpus — only KNZg55/57 Anetaki pieces are)",
      absolute_value_bits=0.0,
      value=("longest continuous LA text (~119 signs vs KNZf13's 19); non-administrative, numeral-free => "
             "unique held-out gold for L2/L3 structural claims (libation order, A-prefixation, formula slots); "
             "~+1.5% corpus tokens; possible new attestations of A-only signs in ritual vocabulary"),
      expected_eqred_log10=0.0, licence="academic publication", automation="medium"),
 dict(rank=0, id="ACQ-02", name="Egyptian-rendered toponym equation on newly published LA text (Amnisos i-m-n-y-s3 / Kydonia k3-tw-n3-y / Knossos k-n-s class, >=4 LA slots)",
      source_class=["external_name_equation"],
      status="EXCAVATION-GATED (WP-D: overlap empty after ~120 yrs; base rate ~0-2 new LA docs/yr)",
      absolute_value_bits="first dependency-distinct anchor",
      value=(f"IF realized: eqred ~{G4['eqred_log10']} log10 of {LA_RESIDUAL_LOG10:.1f} (abs ~{G4['abs_recovery']}); "
             f"{G4['basis']}. Residual still >= 10^{LA_RESIDUAL_LOG10 - G4['eqred_log10']:.0f}"),
      expected_eqred_log10=round(0.03 * G4["eqred_log10"], 3), licence="publication", automation="low"),
 dict(rank=0, id="ACQ-03", name="Bilingual / biscriptal fragment (LA + any read script)",
      source_class=["bilingual_biscriptal_fragment"],
      status="NOT KNOWN TO EXIST (P~0.002 within 2 yrs)",
      absolute_value_bits="up to script recovery",
      value=(f"only acquisition class that can reach the (12,8,12) frontier (abs {FRONTIER['abs_recovery']}); "
             "conservative Art.-XI bound (single provenance = 1 lineage) caps it at "
             f"eqred ~{G8['eqred_log10']} log10 / abs ~{G8['abs_recovery']}"),
      expected_eqred_log10=round(0.002 * FRONTIER["eq_reduction"], 3), licence="excavation-gated", automation="low"),
 dict(rank=0, id="ACQ-04", name="SigLA raw stroke vectors from Salgarella/Castellan (unblock WP-E)",
      source_class=["stroke_decomposition", "high_resolution_image"],
      status="SOURCE_BLOCKED; data exists as drawings; requires author contact",
      absolute_value_bits=0.0,
      value="unblocks the stroke channel for sign-identity/allography ONLY; H-lineage is circular for values (Art. XI)",
      expected_eqred_log10=0.0, licence="CC BY-NC-SA", automation="high once obtained"),
 dict(rank=0, id="ACQ-05", name="Systematic join search in the HT archive (RTI/3D of fragment edges)",
      source_class=["new_join", "high_resolution_image"],
      status="museum-access-gated (Heraklion Museum / INSTAP)",
      absolute_value_bits="only if a join completes an externally-equated word (P~0.02)",
      value="lengthens words; the PA-I-TO pin fails WP-D's >=4-slot bar at 3 slots/1 site — a join or new attestation is the cheapest way to move an EXISTING pin",
      expected_eqred_log10=round(0.5 * 0.02 * G2["eqred_log10"], 3), licence="museum", automation="medium"),
 dict(rank=0, id="ACQ-06", name="Kom el-Hettan recollation / new Aegean-list fragments (Sourouzian excavation, ongoing)",
      source_class=["external_name_equation"],
      status="Egyptian side may grow; binds NOTHING without the LA-side attestation (WP-D)",
      absolute_value_bits=0.0,
      value="raises the menu of Egyptian-rendered toponyms awaiting an LA match; zero bits until ACQ-02 fires",
      expected_eqred_log10=0.0, licence="publication", automation="low"),
 dict(rank=0, id="ACQ-07", name="Full Knossos-cult-center (Anetaki plot) final epigraphic edition beyond the scepter",
      source_class=["anetaki_final_edition_delta", "new_inscription_occurrence"],
      status="ROLLING (Ariadne 2025 overview out; further volumes expected)",
      absolute_value_bits=0.0,
      value="more KN non-administrative texts; new-site-class contexts for A-only ritual signs; held-out gold",
      expected_eqred_log10=0.0, licence="academic publication", automation="medium"),
 dict(rank=0, id="ACQ-08", name="Routine new-excavation LA documents (Sissi, Zominthos, Palaikastro 2022+, Gournia)",
      source_class=["new_inscription_occurrence", "new_site"],
      status="base rate ~0-2/yr, mostly roundels/nodules (1-3 signs)",
      absolute_value_bits=0.0,
      value="coverage axis only; G: 0 anchors => abs 0.0 at every coverage (measured)",
      expected_eqred_log10=0.0, licence="excavation-gated", automation="low"),
]
# rank by expected absolute eqred, tie-break by availability-weighted relative value (manual order for zeros)
order = ["ACQ-02", "ACQ-05", "ACQ-03", "ACQ-01", "ACQ-07", "ACQ-04", "ACQ-06", "ACQ-08"]
# note: ACQ-05 (0.050) vs ACQ-03 (0.048) is inside estimate noise; ACQ-03's
# conditional-on-realization gain dominates every other class by orders of magnitude.
ACQ.sort(key=lambda a: order.index(a["id"]))
for i, a in enumerate(ACQ, 1):
    a["rank"] = i

out = dict(
    task="K_acquisition", seed=SEED, constitution="v2.2",
    articles=["VII", "VIII", "IX", "XI", "XII", "XV", "XXII"],
    inputs=dict(surface="data/controls/anchor_threshold/surface.json",
                lattice="data/anchor_lattice/lattice.json",
                sign_universe="data/sign_universe/conservative.json"),
    la_operating_point=dict(residual_ambiguity_log10=LA_RESIDUAL_LOG10,
                            whole_system_eq_classes_log10=">=270 (Task H)",
                            independent_anchors=0),
    gain_model=dict(first_anchor_by_slots={"1": G1, "2": G2, "4": G4, "8": G8},
                    foothold=FOOTHOLD, frontier=FRONTIER, coverage_note=COVERAGE_SAT,
                    caveat="p_anchor/p_avail are stated estimates (flagged), not measurements; all downstream numbers are arithmetic on measured surface cells"),
    source_classes=SOURCE_CLASSES,
    acquisitions_ranked=ACQ,
    per_sign_queue=queue,
    headline=dict(
        best_single_acquisition_for_absolute_ambiguity="NONE AVAILABLE NOW reduces the 10^63.4 residual at all; expectation-weighted best = ACQ-02 (Egyptian-attested toponym on a new LA text): E[eqred] ~ 0.27 log10; conditional-on-realization best = ACQ-03 bilingual",
        best_available_now="ACQ-01 Anetaki scepter ingest — 0 absolute bits, but the largest held-out L2/L3 test bed added to the corpus since GORILA",
        honest_bound=f"even a realized 4-slot independent anchor leaves >= 10^{LA_RESIDUAL_LOG10 - G4['eqred_log10']:.0f} equivalence classes"),
)
os.makedirs(f"{BASE}/data/source_expansion", exist_ok=True)
path = f"{BASE}/data/source_expansion/acquisition_queue.json"
json.dump(out, open(path, "w"), indent=1)
print("wrote", path)
print("md5", hashlib.md5(open(path, 'rb').read()).hexdigest())
print("\n== headline ==")
for k, v in out["headline"].items():
    print(f"- {k}: {v}")
print("\n== source classes by expected absolute eqred (log10) ==")
for sc in sorted(SOURCE_CLASSES, key=lambda s: -s["expected_eqred_log10"]):
    print(f"  {sc['id']:34s} E[eqred]={sc['expected_eqred_log10']:8.3f}  E[abs]={sc['expected_abs_recovery']:7.4f}  p_avail={sc['p_avail']}")
print("\n== acquisitions ranked ==")
for a in ACQ:
    print(f"  {a['rank']}. {a['id']} E[eqred]={a['expected_eqred_log10']}: {a['name'][:90]}")
print("\n== per-sign queue (top 12) ==")
for r in queue[:12]:
    print(f"  {r['target_sign']:8s} occ={r['occurrences']:3d} dark={r['relationally_dark']} p(in new 4-slot anchor)={r['p_appears_in_new_4slot_anchor_word']:.4f} E[eqred]={r['expected_eqred_log10']}")
print(f"\ntotal corpus sign tokens = {tot_tokens}; per-sign queue length = {len(queue)}")
