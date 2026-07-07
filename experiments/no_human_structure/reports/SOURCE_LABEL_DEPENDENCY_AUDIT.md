# Source-label dependency audit (§IV)

Every machine-readable Linear B label source, its provenance, and the **dependency DAG** that determines
which agreements count as *independent* evidence. Machine-readable graph:
`data/source_labels/source_dependency_graph.json`.

## Sources

| source | kind | derives from | provides | independence class |
|---|---|---|---|---|
| **DĀMOS** | database (in repo) | primary editions + GORILA + 1952 decipherment | transliteration, series/subseries, hand, area, chronogroup, logograms, numerals | SHARED_DECIPHERMENT |
| **LiBER** | database (TO_AUDIT) | primary editions + GORILA + decipherment | layout, series | SHARED_DECIPHERMENT |
| **Ventris–Chadwick, *Documents*²** | lexicon (published) | primary editions + decipherment | toponym index, PN index, role glosses | SHARED_DECIPHERMENT / SHARED_LEXICON |
| **Aura Jorro, *Diccionario Micénico*** | lexicon (published) | **Ventris–Chadwick** + editions + decipherment | lexical role concordance, toponym/PN indexes | SHARED_LEXICON (**derives from V–C**) |
| **STRUCTURAL_RULES** | deterministic derivation | DĀMOS structure only | numeral→quantity, logogram→commodity, total-position→document-structure | **EDITION_INDEPENDENT** |

## The load-bearing dependency ruling

All lexica and databases descend from the **same primary editions + the single 1952 decipherment**.
Therefore:

- **DĀMOS + Ventris–Chadwick + Aura Jorro agreeing is NOT three independent votes** — it collapses to **one**
  `SHARED_DECIPHERMENT` vote. Aura Jorro additionally *derives from* Ventris–Chadwick, so those two are not
  even independent lexica.
- The **only genuinely edition-independent role signal** is `STRUCTURAL_RULES` (a numeral is a quantity, a
  logogram is a commodity, a totalling form is document-structure — true regardless of any reading).
- Consequently `LF_CROSS_SOURCE_CONCORDANCE` (§V) may treat agreement as independent evidence **only across
  independence classes** (e.g. STRUCTURAL_RULES ∧ lexicon), never within `SHARED_DECIPHERMENT`.

## Consequences for SILVER tiers (§IV)

- **SILVER_A from structure:** the trivial classes (NUMERAL→MEASURE_OR_QUANTITY, LOGOGRAM→COMMODITY_OR_
  COUNTED_CATEGORY, total-position→DOCUMENT_STRUCTURE) are edition-independent → SILVER_A (but these are the
  *trivial* partition, excluded from the load-bearing `NONTRIVIAL_UNSEEN_FORM_SCORE`).
- **SILVER_A from lexicon** (PLACE/HUMAN content roles) requires the reading uncontested in the ed. pr. AND
  uncontested index membership; else **SILVER_B**. Because content-role identification rests on the *shared*
  decipherment, most content-role SILVER labels are **SILVER_B**, not SILVER_A — a structural reason the
  no-human `SILVER_A` non-trivial pool will be **thin** (mirrors the Stage 5.1 GOLD_A finding).

## Honest forecast

The dependency structure predicts the central risk up front: **the edition-independent labels are exactly
the trivial classes**, and the non-trivial content-role labels are all downstream of one decipherment, so
they cannot supply *independent* consensus. This bounds how strong a no-human SILVER_A non-trivial signal can
be — to be quantified when the SILVER corpus is built (stage 3), and it is a plausible early route to a
`NO_POWER` verdict that must be tested, not assumed.
