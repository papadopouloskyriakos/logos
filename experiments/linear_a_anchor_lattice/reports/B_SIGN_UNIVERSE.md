# TASK B — Canonical Unresolved-Sign Universe

**Campaign:** `research/linear-a-anchor-lattice` · **Seed:** 20260708 · **Articles:** V (claim layers),
XI (source-dependency), XII (no grading by the creating rule), XVIII (assumptions).
**Builder:** `scripts/build_sign_universe.py` (run from artifacts; every number below is script-generated).
**Outputs:** `data/sign_universe/{split,conservative,merged}.json` + `_meta.json`.

## What this is

The complete **variable universe** for joint anchor-lattice inference: one record per Linear A
sign, carrying every field a downstream joint model needs — identity, corpus statistics, structural
slots, relational neighbours, cross-script link, and existing anchor/stroke coverage. Built at
**three allograph grains** so no result may depend on a single spec.

### Non-circularity (Art. XI / XII)

- LB/GORILA conventional values are attached **only** as `benchmark_label_graded_only` — never a
  variable input, never earning a value or licence. AB-shared signs are therefore counted as
  **still-unresolved** (a graded LB label is not a proven Linear A value).
- The SigLA↔AB cross-reference is a **graded catalog link**: induced by positional voting over 366
  equal-length shared documents (A-only `*NNN` resolve directly by GORILA number). Validated against
  the known decode (KU→AB81, A→AB08, RA2→AB76 all recovered). It supplies "does an image exist",
  not a value.

## The three inventories (differ ONLY on the allograph axis)

| Inventory | Definition | Variables |
|---|---|---|
| `SIGN_UNIVERSE_ALLOGRAPH_SPLIT` | every catalogued sign distinct (letter/subscript allographs `*131B`,`RA2` kept separate) | **166** |
| `SIGN_UNIVERSE_CONSERVATIVE` (PRIMARY) | repo-audited expert merges only (`*131B/*131C→*131`; subscript AB kept distinct) | **163** |
| `SIGN_UNIVERSE_ALLOGRAPH_MERGED` | + fold subscript AB into graphic base (`RA2→RA`, `PA3→PA`, `TA2→TA`, `PU2→PU`) | **158** |

Ligature/canonicalisation is held fixed across all three (the corpus diplomatic→canonical map, 259
raw tokens → 166 canonical keys); only allograph treatment varies. Grain definitions mirror the
audited `scripts/inventory/build_ontology.py` (`_conservative_id`/`_exploratory_id`). All keys are
attested in the corpus (1,341 inscriptions).

## Unresolved-sign counts + coverage (script-measured)

**Class breakdown** (SPLIT / CONSERVATIVE / MERGED):

| class | SPLIT | CONSERVATIVE | MERGED |
|---|---|---|---|
| AB-shared (syllabic, LB-homomorph benchmark) | 59 | 59 | 55 |
| A-only (syllabic, undeciphered `*`-series) | 72 | 69 | 69 |
| uncertain | 3 | 3 | 2 |
| logogram | 20 | 20 | 20 |
| numeral/fraction | 12 | 12 | 12 |
| **total** | **166** | **163** | **158** |
| **syllabic (AB+A-only+uncertain)** | **134** | **131** | **126** |
| **value-unresolved (excl. numerals)** | **154** | **151** | **146** |

**Coverage of the syllabic universe** (the variables joint inference must pin), CONSERVATIVE grain,
n = 131:

| coverage channel | count | note |
|---|---|---|
| stroke/image (SigLA bbox) | 112 | image exists to decompose |
| anchor (wp5 inventory) | 60 | dependency-graded |
| substitution (C_la_graph) | 32 | relational neighbour ≥1 |
| **any of the three** | 117 | |
| **all three** | 31 | |
| **none of the three** | 14 | see list below |
| robust multi-channel anchor | 51 | |
| independent multi-channel set | 26 | the wp5 held-out-survivable set |

### The decisive split — anchor coverage is an AB-shared artefact

CONSERVATIVE grain, by class:

| class | n | stroke | anchor | substitution |
|---|---|---|---|---|
| AB-shared | 59 | 55 | **59** | 31 |
| A-only | 69 | 57 | **1** | 1 |

The genuinely undeciphered core — the 69 A-only signs — has near-total **image** coverage (57/69)
but essentially **zero** anchor (1/69, a single one-toponym-deep pin) and **zero** substitution
constraint (1/69). All anchor/substitution structure lives on the AB-shared signs, i.e. on signs
whose only "value" is a graded LB label. This is the honest state the lattice inherits: **stroke is
abundant, relational/anchor constraint on the unknowns is almost absent.**

### Syllabic signs with NO coverage of any channel (n=14, CONSERVATIVE)

`*164, *188, *348, *401, *404, *405, *413, *414, *82, *86, *OLIV, QA2, PUA:0xfd1eb, __DATA_ERROR__`

(Two are non-signs — `__DATA_ERROR__`, `PUA:...` a PUA placeholder — leaving 12 real dark A-only/
uncertain signs. These are pure free variables: no image-decomposition anchor, no neighbour, no
external pin.)

## Per-sign record schema (all three JSONs)

```
canonical_id, aliases[], class, class_ontology, allograph_family,
conservative_id, merged_id, members_split[] (agg grains only),
occurrence_count, attested_in_corpus, n_documents,
position_counts{initial,interior,final,sole}, formula_slots{in_total_formula,in_KURO,in_KIRO,as_A_prefix_head},
site_distribution{}, chronology_distribution{}, support_distribution{},
substitution_neighbors[], rel_class, morphological_role[],
cross_script{shared_with_linearB, sigla_name, sigla_glyph_bbox_count, sigla_link_method},
stroke_image_available, anchor_coverage{dependency_tier,n_independent_channels,robust_anchor,channel_H,channel_C,...},
in_independent_multichannel_set, literature_index_mentions,
candidate_value_domain, benchmark_label_graded_only, has_{substitution,anchor}_coverage, uncertainty
```

## Sensitivity headline

Across SPLIT→MERGED the syllabic-variable count moves only **134 → 131 → 126** (a 6% band) and the
coverage fractions are stable (none-of-three: 14→13; robust anchor 51→48). **No coverage conclusion
flips with allograph spec.** The one structural fact — anchor/substitution constraint is confined to
AB-shared signs while A-only signs are image-rich but relationally dark — holds at every grain.

## Files

- `data/sign_universe/split.json` — SIGN_UNIVERSE_ALLOGRAPH_SPLIT (166)
- `data/sign_universe/conservative.json` — SIGN_UNIVERSE_CONSERVATIVE (163, PRIMARY)
- `data/sign_universe/merged.json` — SIGN_UNIVERSE_ALLOGRAPH_MERGED (158)
- `data/sign_universe/_meta.json` — counts, alignment stats, all three summaries
- `scripts/build_sign_universe.py` — reproducible builder (seed 20260708)
