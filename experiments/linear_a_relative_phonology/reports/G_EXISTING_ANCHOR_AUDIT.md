# G1 — Existing Anchor Audit

**Task.** Audit the Foundry 115-record / 62-sign Linear A (LA) anchor inventory
(`experiments/linear_a_foundry/data/wp5_anchor_inventory_records.csv` +
`…_signs.csv`, enriched from the cross-script gate census), record the twelve audit
fields per record, remove duplicates and dependency clones, and report the
**de-duplicated independent-anchor count**.

**Constitution posture.** L2/L4 evidence census only. Non-circular: conventional LA values
label records, they are never a model input. All held-out numbers are **cited** from the
frozen preregistered cross-script gate (DOIs `10.5281/zenodo.21168887` / `21173639`), not
re-run. Seed 20260708.

Artifacts: `scripts/g1_anchor_audit.py` → `data/anchors_v2/audit.json`.

---

## 1. What the inventory actually contains (raw, measured)

| | count |
|---|---|
| raw provenance records | **115** |
| signs touched | **62** (61 with any anchor, 1 none) |
| exact duplicate records | **0** |

Three evidence channels, five substantive record classes:

| channel | class | records | source |
|---|---|---|---|
| `L_lexical` | toponym | 15 | S&M 2017 (7 primary) + Younger web (8 secondary) |
| `L_lexical` | personal_name | 25 | Hooker 1975 / S&M 2017 onomastic table |
| `L_lexical` | gloss_acrophonic | 3 | Neumann 1960/62; S&M (Hesiod/Hesychius) |
| `L_lexical` | variation_constraint | 4 | S&M 2017 §5 |
| `H_homomorphy` | sign_shape | 57 | Salgarella 2020, Tables 2–4 |
| `C_cypriot` | cross_script_stability | 11 | S&M 2017 Table 6.2 p.98 |

Every record carries the twelve audit fields in `audit.json → audit_rows[]`: `source`,
`page_record`, `chronology`, `geography`, `dependency_class`, `candidate_la_locus`,
`covered_signs` + `matching_slots`, `rule_complexity`, `quality_tier`/`sm_trust`,
`prior_exposure`, `heldout_prediction`, `failure_status`.

---

## 2. Dependency-clone structure — the audit's core finding

**Only ONE of the three channels can derive a phonetic value from evidence outside the
Linear-B value system.** The other two *inherit* the LB value and merely corroborate
sign *identity*:

| lineage | records | value-bearing? | why |
|---|---|---|---|
| `LIN-H` Salgarella-2020 homomorphy | 57 | **NO** | sign-SHAPE identity = the GORILA shape-transcription substrate itself; it *is* the assumption the other channels presuppose. Inherits the LB value, derives none. |
| `LIN-C` S&M Cypriot stability | 11 | **NO** | 3rd-script sign continuity; inherits LB/Greek value |
| `LIN-PN` Hooker/S&M onomastic table | 25 | **NO** | value-blind resemblance: with thousands of LB names, any CVCV string "resembles" one; no external referent constrains the reading |
| `LIN-GLOSS` acrophonic | 3 | weak | single-sign guesses, not held-out testable |
| `LIN-VAR` internal LA variation | 4 | **NO** | independence-class 4 — places signs in a consonant series but *asserts no value* by construction |
| `LIN-TOP` toponym external referent | 15 | **YES** | a known Cretan place-name is an external referent that pins several signs at once |

So of 115 records, **57 + 11 = 68 (59%) are sign-identity records that inherit their value
from LB**, **25 + 3 + 4 = 32 (28%) are value-blind or never-pin**, and only the **15
toponym records (13%) are even in principle value-bearing.**

The 57 homomorphy records are a **single dependency lineage** (one source, one method:
visual LA↔LB glyph matching). The 11 Cypriot records are a **single lineage** (one table).
The 25 personal-name records are a **single lineage** (one onomastic-resemblance tradition).
Counting them as 93 independent anchors would be the exact multiplicity fraud the campaign
exists to refute.

### De-duplication applied
- **Exact duplicates:** 0.
- **Dependency-clone collapse (method level):** 115 records → **6 root method-lineages**
  (`LIN-H, LIN-C, LIN-PN, LIN-GLOSS, LIN-VAR, LIN-TOP`).
- **Toponym referent-clone collapse:** the 15 toponym records cover only **14 distinct
  external referents** — `top_tu_ru_sa` and `top_a_tu_ri_si_ti` are both **Tylissos**
  (the second is a morphological derivative "to/at Tylissos" of the same identification),
  so they collapse to one anchor.

---

## 3. De-duplicated independent-anchor count (headline)

The count depends entirely on how strict "independent" is. Reported at every honest tier:

| definition of "independent anchor" | count |
|---|---|
| raw provenance records (no dedup) | 115 |
| root method-lineages | **6** |
| **value-bearing lineages** (can derive a value from outside LB) | **1** (toponym channel) |
| distinct toponym external referents (de-cloned, incl. hedged/cf/secondary) — **TIER-B** | **14** |
| firm, primary, unqueried toponym equations (de-cloned) — **TIER-A** | **5** |
| — Phaistos, Tylissos, Sybrita, Mt-Dikte, se-to-i-ja | |
| **empirically held-out-SURVIVABLE independent anchors** | **0** |

**TIER-A = 5** is the defensible "independent, publishable-quality anchor" count: five
distinct Cretan place-names, each read the same way, each in S&M 2017's unqueried
Table 6.4. Six others are hedged/cf-only (Mt-Ida, Kydonia, ku-ta-to, Ayia-Triada,
Inatos, …) and the personal-name/homomorphy/Cypriot channels add **zero** independent
*value* anchors on top.

### The number that actually decides a reading: **0**

Independence in the *inventory* is far more generous than **held-out survivability**.
The frozen preregistered cross-script gate (cited, not re-run) returned:

- verdict **`REFUTE_LOTO_FRAGILE`**,
- LA-internal distributional channel top-1 = **0.0000** (third null confirmation),
- leave-one-toponym-out recovered only **{I, RI}**, and **each one-toponym-deep** —
  i.e. even signs the inventory grades `multi_channel_independent` are **not** re-derivable
  from held-out LA distribution once their single supporting toponym is removed.

A one-toponym-deep pin is **not** an independent held-out anchor: hold that toponym out and
the value vanishes. So the count of anchors that would survive the Linear-B-new-tablet
standard is **0**, with {I, RI} as one-deep partial recoveries.

---

## 4. Bearing on the campaign (WP-A refuted; substitution channel load-bearing)

This audit is the anchor-side complement to the WP-A refutation. WP-A showed the
position→C/V symmetry-break was a frequency prior, not structure. G1 shows the anchor
inventory that *any* "not value-blind" claim would lean on collapses, once dependency clones
are removed, to **1 value-bearing channel / 5 firm toponym equations / 0 held-out-survivable
anchors**. Two independent facts now point the same way:

1. LA-internal evidence is **relabeling-invariant** (prior campaigns) — internal structure
   cannot fix values.
2. The external anchor inventory has **no held-out-survivable independent value anchor**
   (this audit) — the external channels either inherit LB values (H, C: 68 records) or are
   value-blind (PN, GLOSS, VAR: 32 records), and the 5 firm toponym equations are each
   one-toponym-deep.

Consequence for the load-bearing **substitution channel** (C3, AUC 0.744): it must be
audited as a *relative/structural* signal that is **relabeling-invariant by design** — it
must never be worded to imply recovered *values*, because this audit shows the value-anchor
substrate to support such a claim does not exist. Cracking LA still requires a bilingual or
≥3 genuinely independent held-out anchors; the existing inventory supplies neither.

---

*Generated by `scripts/g1_anchor_audit.py`; numbers echoed from `data/anchors_v2/audit.json`.
All counts are script-generated (invariant 12).*
