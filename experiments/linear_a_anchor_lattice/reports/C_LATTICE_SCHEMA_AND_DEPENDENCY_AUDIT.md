# TASK C — Dependency-Aware All-Anchor Lattice: Schema + Dependency Audit

**Campaign:** research/linear-a-anchor-lattice · **Seed:** 20260708 · **Grain:** conservative
sign universe (163 variables; 69 A-only) · **Constitution:** v2.2 (Art. XI/XII/XV governing)
**Artifact:** `data/anchor_lattice/lattice.json` (562 nodes, 208 hyperedges)
**Verdict:** `ALL_ANCHOR_LATTICE_BUILT — DEPENDENCY_COLLAPSED_INDEPENDENT_ANCHORS = 0`

> This is a *re-run* of the Task-C build (prior attempt died on an API error). Everything
> below is computed by `scripts/c_build_anchor_lattice.py` from the real input files; no
> figure is hand-written (Invariant 12).

---

## 1. What was ingested

| Source | Records | Into the lattice |
|---|---|---|
| WP-5 foundry anchor inventory (`wp5_anchor_inventory.json`) | 115 provenance records over 62 signs | L/H/C equation + descent edges |
| 5 firm toponym equations | Phaistos, Setoija, Sybrita, Tylissos, Dikte | `toponym_equation` (firm) edges |
| WP-B relative substitution (F4) | 5 within-LA rel-classes + 60 pairwise neighbours | `relative_substitution_relation` (value-free) |
| WP-B morphology (universe `morphological_role`) | 22 signs | `morphological_relation` (value-free) |
| WP-B formula slots | 6 signs (A, KI, KU, PO, RO, TO) | `formula_slot_constraint` (value-free) |
| WP-D source expansion (Kom el-Hetan / Edel 1966) | **0 new independent anchors** (SEED_A=0) | one `loanword_equation` edge, flagged NULL |

The 115 L-provenance items resolve to **15 toponym**, **23 personal-name**, **3 commodity/gloss**
referents; homomorphy (Salgarella 2020) grades **57** signs; Cypriot stability (S&M 2017) covers **11**.

---

## 2. Node counts by type (15 declared types, 562 nodes)

| Node type | n | Node type | n |
|---|---|---|---|
| SIGN | 163 | EXTERNAL_FORM (LB/Egyptian) | 14 |
| STROKE_FAMILY | 156 | DEPENDENCY_LINEAGE | 11 |
| CROSS_SCRIPT_SIGN (57 LB-shape + 11 Cypriot) | 68 | SOURCE | 8 |
| EXTERNAL_REFERENT (toponym/PN/commodity) | 51 | LINEAR_A_FORM | 6 |
| CANDIDATE_VALUE (graded-only LB labels) | 39 | SITE | 6 |
| MORPHOLOGICAL_RELATION | 22 | FORMULA_SLOT | 5 |
| RELATIVE_CLASS | 5 | LANGUAGE | 4 |
| INSCRIPTION | 4 | | |

CANDIDATE_VALUE nodes carry `status = benchmark_label_graded_only`: the LB/GORILA conventional
value is attached to grade benchmarks **only**, is never a variable input, and earns no
value/licence (non-circular note; Art. XII).

## 3. Edge counts by type (208 hyperedges)

| Hyperedge type | n | Value-bearing? | Lineage |
|---|---|---|---|
| cross_script_descent (homomorphy 57 + Cypriot 11) | 68 | **NO** (shape / chain, circular) | LIN_H, LIN_C |
| relative_substitution_relation (5 classes + 60 pairs) | 65 | **NO** (value-free, Art. XV) | LIN_REL |
| personal_name_equation | 23 | yes (but see §4) | LIN_L_PN |
| morphological_relation | 22 | **NO** (structural) | LIN_MORPH |
| toponym_equation (5 firm + 15 wp5) | 20 | yes (but see §4) | LIN_L_TOP |
| formula_slot_constraint | 6 | **NO** (structural) | LIN_FORMULA |
| commodity_measure_equation | 3 | yes (but see §4) | LIN_L_GLOSS |
| loanword_equation (WP-D, Egyptian) | 1 | yes (but VACUOUS, 0 anchors) | LIN_EG |

Every hyperedge records the full Art.-XI provenance tuple: `signs_constrained, candidate_values,
slots, source, page, chronology, geography, dependency_lineage, independence_class,
evidence_channels, rule_complexity, transformations, prior_exposure, derivation_vs_heldout,
circularity_risk, search_multiplicity, failure_condition`.

---

## 4. Dependency collapse (Art. XI/XII) — the load-bearing result

**Rule.** An anchor is INDEPENDENT only if ≥2 dependency-lineage-**distinct** value-bearing
edges support it, where the lineages do **not** share a meta-lineage ancestor. No edge is
independent merely for a different citation.

**Value-bearing channels = 1** (from `do_not_repeat_unchanged.json` anchor_state). Only the
lexical/onomastic **L** channel carries value. The homomorphy channel **H** is shape-only and
already ruled CIRCULAR (capped ≤0.75); the Cypriot channel **C** is an LA→LB→Cypriot chain that
*reuses* the very continuity it purports to corroborate. Both are excluded as value-bearing.

**Meta-lineage collapse.** `LIN_L_TOP`, `LIN_L_PN`, `LIN_L_GLOSS` (and H, C) all descend from a
single ancestor: **`META_CONTINUITY_LA_eq_LB`** — the standard "LA sign = LB homophone"
transnumeration. A sign cited by three toponyms and two personal names is graded by the same rule
that created every one of those equations (Art. XII), so those citations are **dependency clones**,
not independent supports. The only genuinely dependency-distinct value-bearing lineage is
`LIN_EG` (Egyptian epigraphic, Kom el-Hetan) — and WP-D returned **SEED_A = 0** (no LA toponym is
both ≥4-slot and externally rendered; Phaistos overlaps at only 3 slots).

**Consequence:** ≥2 distinct meta-lineages is reachable by **no sign**.

| Quantity | Value |
|---|---|
| INVENTORY-side "multi-channel independent" signs (pre-collapse, L+H+C stacked) | 26 |
| INVENTORY-side one-toponym-deep pins | 3 (*49, *79, ZU) |
| **DEPENDENCY-COLLAPSED independent-anchor count (Art. XI)** | **0** |
| Held-out-survivable absolute anchors (frozen gate, SEED_A) | **0** |

The collapse reproduces, from graph structure alone, the empirical frozen-gate verdict
`REFUTE_LOTO_FRAGILE` (distributional channel top-1 = 0.0; only I, RI recovered under LOTO, each
one-toponym-deep). The "26" is an **inventory artifact of citation-stacking within one meta-lineage**,
not evidence of independence.

---

## 5. The 69 A-only signs (WP-B "relationally DARK")

| Measure | Count / signs |
|---|---|
| A-only signs total | 69 |
| …with **any** value-bearing (non-circular) lineage edge | **1** — `*49` only |
| …with an independent (collapse-surviving) value | **0** |
| …with no value-bearing edge at all (dark) | 68 |

`*49` carries a single value-bearing L edge (toponym `da-u-49`, one-toponym-deep pin,
`robust_anchor=false`, not held-out survivable). `*324` has only a **value-free** relative
substitution edge (→ ZU); 57/69 have only the **circular** stroke-family channel. Under the
Art.-XI collapse, the number of A-only signs receiving an *independent-lineage* decided value is
**0** — matching WP-B's 1/69 anchor, 1/69 substitution, 12 free variables framing.

---

## 6. Compliance line

Articles triggered: XI (source-dependency graph + clone collapse), XII (no grading a target by
the rule that created it), XV (relative reduction earns no value), VIII (effective vs raw n),
XVII (append-only; WP-D null recorded, not deleted). Gates: value_bearing_channels=1;
dependency-collapsed independent anchors=0; held-out-survivable=0. Assumptions: `META_CONTINUITY_LA_eq_LB`
is the shared ancestor and is circular-for-values. **No do_not_repeat lineage was re-run** (this
is a lattice-construction + audit task, not a value-search). **COMPLIANT.** No licence changes;
SEMANTIC+ remains NOT_AUTHORIZED.
