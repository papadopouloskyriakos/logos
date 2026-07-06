# Linear A notation resolution (Stage 4.2)

The 1,056 previously-`other` LA tokens are resolved **source-groundedly** by their silver `raw` glyph
(`linear_a_structural_recovery.classify_other`) — no Linear B meaning imported; all opaque.

| class | count | representation | rule |
|---|---|---|---|
| **LOGOGRAM** | 654 | opaque `A_LOGO_NNN` (81 glyphs) | `*NNN` numbered ideogram OR Aegean-block glyph (U+10600–U+107FF) |
| **FRACTION** | 311 | opaque `A_FRAC_NNN` (11 glyphs) | unicode fraction chars / super-sub fraction; **value withheld** (LA fraction values contested — Corazza 2021) |
| OTHER_NOTATION | 52 | opaque `A_NOTE_NNN` (1) | dashes/dividers/symbols |
| DAMAGED_OR_UNKNOWN | 9 | TOKEN, damage_flag | brackets/`?`/illegible |
| UNRESOLVED | 30 | TOKEN, uncertain_flag | glyph not source-classifiable |

**965/1,056 (91%) resolved** into typed channels; 39 kept explicit (damaged/unresolved). No LB→LA
equivalence: `A_LOGO`/`A_FRAC`/`A_NOTE` vocabs are LA-only, disjoint from LB.

## Feature sets (`data/policy/feature_sets.csv`)

- **CORE_TRANSFERABLE** (present-and-parsed in BOTH, primary model): opaque sign identity, sequence/position,
  entry/row structure, numeral value, numeral/logogram adjacency, cross-document recurrence, formula-cluster
  membership (grouping), damage/uncertainty, support, site.
- **EXTENDED_STRUCTURAL** (partial/opaque/asymmetric, sensitivity only): logogram identity (opaque), fraction
  identity (opaque), measure marker, layout, allography, document_series (LB-only), scribe (LB-only), fine
  chronology, AB-shared bridge.
- **EXCLUDED_FROM_PRIMARY:** `DAMAGED_OR_UNKNOWN` + `UNRESOLVED` notation (never enter the primary model);
  phonetics/Greek/role (eval-only).

**Ruling:** unresolved channels do NOT enter the primary transfer model.
