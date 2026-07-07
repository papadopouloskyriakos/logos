#!/usr/bin/env python3
"""G3b - COMPOUND ANCHOR SYSTEMS.

A compound system = a set of anchors whose INDEPENDENT constraints jointly pin >=4 distinct
signs, span >=2 contexts (distinct loci/objects/sites), and draw on >=2 evidence channels.

The decisive refinement the campaign demands: count not just channels, but INDEPENDENT
VALUE-BEARING channels. Per G1 the only value-bearing channel is the toponym (external
referent) channel; shape-homomorphy and Cypriot-stability channels INHERIT the LB value
(Art. XII circular for value). So a system can look like a >=2-channel compound while
reaching that bar only by adding value-inheriting channels that supply no independent value.

Builds every sign's channel coverage from the G1 audit, enumerates candidate compound
systems, and for each reports: n_signs, n_contexts, n_channels, n_INDEPENDENT_value_bearing
channels, and whether it clears the strict bar (>=4 signs, >=2 contexts, >=2 INDEPENDENT
value channels).

Non-circular: LA values label only. Writes data/anchors_v2/compound_systems.json +
reports/G_COMPOUND_SYSTEMS.md.
"""
from __future__ import annotations
import json, os
from collections import defaultdict, Counter
from itertools import combinations

HERE = os.path.dirname(os.path.abspath(__file__))
CAMP = os.path.abspath(os.path.join(HERE, ".."))
AUDIT = os.path.join(CAMP, "data", "anchors_v2", "audit.json")
OUT_DATA = os.path.join(CAMP, "data", "anchors_v2", "compound_systems.json")
OUT_REP = os.path.join(CAMP, "reports", "G_COMPOUND_SYSTEMS.md")
SEED = 20260708

rows = json.load(open(AUDIT))["audit_rows"]

def channel_of(r):
    if r["channel"] == "H_homomorphy": return "H_shape"
    if r["channel"] == "C_cypriot": return "C_cypriot"
    return "L_" + r["class"]  # L_toponym, L_personal_name, L_gloss_acrophonic, L_variation_constraint

VALUE_BEARING_CHANNELS = {"L_toponym"}  # only the external-referent channel (G1)

FIRM = {"top_pa_i_to", "top_tu_ru_sa", "top_di_ki_te", "top_su_ki_ri_ta",
        "top_se_to_i_ja", "top_a_tu_ri_si_ti"}
FIRM_REFERENT = {"top_pa_i_to": "Phaistos", "top_tu_ru_sa": "Tylissos",
                 "top_a_tu_ri_si_ti": "Tylissos", "top_di_ki_te": "Mt-Dikte",
                 "top_su_ki_ri_ta": "Sybrita", "top_se_to_i_ja": "se-to-i-ja"}

# ---- per-sign channel coverage
sign_channels = defaultdict(set)
sign_value_channels = defaultdict(set)  # distinct value-bearing referents per sign
for r in rows:
    ch = channel_of(r)
    for s in r["covered_signs"]:
        sign_channels[s].add(ch)
        if ch in VALUE_BEARING_CHANNELS and r["record_id"] in FIRM:
            sign_value_channels[s].add(FIRM_REFERENT[r["record_id"]])

def eval_system(name, record_ids, context_kind):
    recs = [r for r in rows if r["record_id"] in record_ids]
    signs = sorted({s for r in recs for s in r["covered_signs"]})
    channels = sorted({channel_of(r) for r in recs})
    # contexts: distinct external referents (toponyms) or distinct record loci
    if context_kind == "referent":
        contexts = sorted({FIRM_REFERENT.get(r["record_id"], r["record_id"]) for r in recs})
    else:
        contexts = sorted({r["record_id"] for r in recs})
    # value-bearing channel TYPES present (only L_toponym is value-bearing) -> at most 1
    indep_value_channels = sorted(set(channels) & VALUE_BEARING_CHANNELS)
    # DISTINCT firm referents touched = independent value CONTEXTS *within* the toponym channel
    distinct_value_referents = sorted({FIRM_REFERENT[r["record_id"]] for r in recs
                                       if r["record_id"] in FIRM})
    clears_loose = len(signs) >= 4 and len(contexts) >= 2 and len(channels) >= 2
    # STRICT (value-honest): >=2 INDEPENDENT value-bearing channel TYPES. Max possible = 1.
    clears_strict = len(signs) >= 4 and len(contexts) >= 2 and len(indep_value_channels) >= 2
    return {
        "name": name, "n_records": len(recs), "signs": signs, "n_signs": len(signs),
        "channels": channels, "n_channels": len(channels),
        "contexts": contexts, "n_contexts": len(contexts),
        "value_bearing_channel_types_present": indep_value_channels,
        "n_independent_value_channels": len(indep_value_channels),
        "distinct_value_referents_within_channel": distinct_value_referents,
        "n_distinct_value_referents": len(distinct_value_referents),
        "clears_loose_bar(>=4sign,>=2ctx,>=2chan)": clears_loose,
        "clears_STRICT_bar(>=4sign,>=2ctx,>=2 INDEP value chan)": clears_strict,
    }

systems = []

# System 1: all firm toponyms (single value channel, many contexts)
systems.append(eval_system("TOP-FIRM: 6 firm toponym equations", FIRM, "referent"))

# System 2: firm toponyms that SHARE at least one sign (the corroboration core)
# {Phaistos+se-to-i-ja} share I,TO ; {Dikte+Sybrita} share KI ; {Sybrita+Tylissos} share RI
systems.append(eval_system("TOP-CORROB-A: Phaistos + se-to-i-ja (share I,TO)",
                           {"top_pa_i_to", "top_se_to_i_ja"}, "referent"))
systems.append(eval_system("TOP-CORROB-B: Sybrita + Tylissos (share RI)",
                           {"top_su_ki_ri_ta", "top_tu_ru_sa", "top_a_tu_ri_si_ti"}, "referent"))

# System 3: a cross-channel system around a hub sign SA (toponym + shape + Cypriot + PN)
sa_records = {r["record_id"] for r in rows if "SA" in r["covered_signs"]}
systems.append(eval_system("HUB-SA: every anchor touching sign SA (all channels)", sa_records, "record"))

# System 4: the RICHEST cross-channel system that reaches >=2 channels for a shared sign set
# take the firm-toponym signs, then add ALL homomorphy + Cypriot records covering those signs
firm_signs = {s for r in rows if r["record_id"] in FIRM for s in r["covered_signs"]}
cross = set(FIRM)
for r in rows:
    if channel_of(r) in ("H_shape", "C_cypriot") and set(r["covered_signs"]) & firm_signs:
        cross.add(r["record_id"])
systems.append(eval_system("CROSS-3CH: firm toponyms + shape + Cypriot on the same signs",
                           cross, "record"))

# ---- structural summary: max independent value-bearing channel TYPES reachable by ANY subset
max_indep = max(s["n_independent_value_channels"] for s in systems)
max_referents = max(s["n_distinct_value_referents"] for s in systems)
# best loose-bar system, best strict-bar system
loose_pass = [s["name"] for s in systems if s["clears_loose_bar(>=4sign,>=2ctx,>=2chan)"]]
strict_pass = [s["name"] for s in systems if s["clears_STRICT_bar(>=4sign,>=2ctx,>=2 INDEP value chan)"]]

# per-sign channel richness (how many channels touch each sign)
sign_richness = {s: sorted(ch) for s, ch in sorted(sign_channels.items(),
                 key=lambda kv: -len(kv[1]))}
richest = [(s, len(ch)) for s, ch in sorted(sign_channels.items(), key=lambda kv: -len(kv[1]))][:8]

out = {
    "task": "G3b_compound_systems",
    "seed": SEED,
    "strict_bar": ">=4 distinct signs, >=2 contexts, >=2 INDEPENDENT value-bearing channels",
    "loose_bar": ">=4 distinct signs, >=2 contexts, >=2 evidence channels (any)",
    "value_bearing_channels": sorted(VALUE_BEARING_CHANNELS),
    "note_channels": "shape-homomorphy and Cypriot-stability channels INHERIT the LB value "
                     "(Art. XII circular) -> they are NOT independent value-bearing channels; "
                     "the ONLY value-bearing channel is the toponym external-referent channel, "
                     "whose 'sub-channels' are distinct firm referents.",
    "systems": systems,
    "systems_clearing_loose_bar": loose_pass,
    "systems_clearing_STRICT_bar": strict_pass,
    "max_independent_value_channel_TYPES_any_system": max_indep,
    "max_distinct_value_referents_within_channel": max_referents,
    "richest_signs_by_channel_count": richest,
    "headline": (
        "Compound systems that reach >=2 EVIDENCE channels exist (e.g. HUB-SA spans 5 channels; CROSS-3CH "
        "spans 3), but EVERY system reaches the >=2-channel bar only by adding value-INHERITING channels "
        "(shape-homomorphy, Cypriot, personal-name). The number of INDEPENDENT value-bearing channel TYPES "
        "in any system is at most %d (the toponym channel; there is no second value-bearing channel type). "
        "Within that one channel, up to %d distinct firm referents co-occur and can share a sign (apparent "
        "corroboration), but the cited frozen LOTO gate collapses even that to {I,RI}, each one-toponym-deep. "
        "So NO compound system has >=2 genuinely INDEPENDENT value-bearing channels: the entire value "
        "substrate is one channel." % (max_indep, max_referents)),
}
os.makedirs(os.path.dirname(OUT_DATA), exist_ok=True)
json.dump(out, open(OUT_DATA, "w"), indent=1)

# ---- report
L = []
L.append("# G3b - Compound Anchor Systems\n")
L.append("**Task.** Find compound systems where independent anchors JOINTLY constrain **>=4 signs**, "
         "across **>=2 contexts**, drawing on **>=2 evidence channels**.\n")
L.append("**Decisive refinement.** Count not just channels but **INDEPENDENT VALUE-BEARING** channels. "
         "Per G1 the only value-bearing channel is the toponym external-referent channel; "
         "shape-homomorphy and Cypriot-stability **inherit** the LB value (Art. XII circular). "
         "A system can hit the >=2-channel bar while every extra channel supplies zero independent value.\n")
L.append("Non-circular: LA values label only. Artifacts: `scripts/g3_compound_systems.py` -> "
         "`data/anchors_v2/compound_systems.json`. Seed 20260708.\n\n---\n")

L.append("## 1. Enumerated systems (measured)\n")
L.append("| system | records | signs | contexts | channels | INDEP value channels | loose bar | STRICT bar |")
L.append("|---|--:|--:|--:|--:|--:|:--:|:--:|")
for s in systems:
    L.append(f"| {s['name']} | {s['n_records']} | {s['n_signs']} | {s['n_contexts']} | "
             f"{s['n_channels']} | **{s['n_independent_value_channels']}** | "
             f"{'PASS' if s['clears_loose_bar(>=4sign,>=2ctx,>=2chan)'] else 'fail'} | "
             f"{'PASS' if s['clears_STRICT_bar(>=4sign,>=2ctx,>=2 INDEP value chan)'] else '**fail**'} |")
L.append("")
L.append("Channels present per system (H_shape / C_cypriot INHERIT value; only L_toponym is value-bearing):\n")
for s in systems:
    L.append(f"- **{s['name']}**: signs [{','.join(s['signs'])}]; channels [{','.join(s['channels'])}]; "
             f"value-bearing channel TYPES present {s['value_bearing_channel_types_present'] or 'none'}; "
             f"distinct value referents within channel {s['distinct_value_referents_within_channel'] or 'none'}.")
L.append("")

L.append("## 2. Richest signs by channel count\n")
L.append("| sign | #channels | channels |")
L.append("|---|--:|---|")
for s, n in richest:
    L.append(f"| {s} | {n} | {', '.join(sign_richness[s])} |")
L.append("")
L.append("A high channel count here is a MULTIPLICITY illusion, not corroboration: the extra channels "
         "(H_shape, C_cypriot, L_personal_name) inherit or assert no value, so a sign 'touched by 4 channels' "
         "is still pinned by at most one value-bearing referent.\n")

L.append("## 3. Headline\n")
L.append(f"- Systems clearing the **loose** bar (>=4 signs, >=2 contexts, >=2 evidence channels): "
         f"**{len(loose_pass)}** ({'; '.join(loose_pass) if loose_pass else 'none'}).\n")
L.append(f"- Systems clearing the **STRICT** bar (>=4 signs, >=2 contexts, >=2 **INDEPENDENT VALUE-BEARING** "
         f"channels): **{len(strict_pass)}** ({'; '.join(strict_pass) if strict_pass else 'NONE'}).\n")
L.append(f"- Max independent value-bearing channel TYPES reachable by any system: **{max_indep}** "
         f"(the toponym channel; no second value-bearing type exists).\n")
L.append(f"- Max distinct firm value referents co-occurring within that one channel: **{max_referents}** "
         f"-- apparent within-channel corroboration, but the cited LOTO gate collapses it to {{I,RI}}, "
         f"each one-toponym-deep.\n")
L.append(out["headline"] + "\n")
L.append("**Consequence.** The campaign's 'no single decisive anchor / >=2 independent symmetry-breaking "
         "channels' candidate-ready criterion is **NOT met on the value axis**: the entire value substrate is "
         "one channel (toponyms). Compound systems are real and useful for RELATIVE structure "
         "(many signs co-constrained across contexts), but they cannot manufacture a second independent "
         "value channel out of value-inheriting evidence.\n")
L.append("*Generated by `scripts/g3_compound_systems.py`; counts echoed from `data/anchors_v2/compound_systems.json` (invariant 12).*")
open(OUT_REP, "w").write("\n".join(L))

print("max independent value channels:", max_indep)
print("loose pass:", loose_pass)
print("strict pass:", strict_pass)
for s in systems:
    print(f"  {s['name'][:45]:45s} signs={s['n_signs']} ctx={s['n_contexts']} chan={s['n_channels']} indepVal={s['n_independent_value_channels']} strict={s['clears_STRICT_bar(>=4sign,>=2ctx,>=2 INDEP value chan)']}")
print("richest:", richest)
