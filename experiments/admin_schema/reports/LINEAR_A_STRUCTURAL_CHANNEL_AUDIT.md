# Linear A structural channel audit (Stage 4.1 Correction 3)

**Problem:** Stage-4 LA builder read only `signs` and reported NUMERAL/FRACTION/LOGOGRAM/MEASURE/SERIES as
absent. That was PARSER absence, not corpus absence — `inscriptions_structured.json` carries a typed `stream`.

| channel | source | status | count | transferability |
|---|---|---|---|---|
| NUMERAL | stream `num` (value) | **PRESENT_AND_PARSED** | 1,276 | TRANSFERABLE |
| ROW | stream `nl` | PRESENT_AND_PARSED | 3,435 | TRANSFERABLE |
| ENTRY | stream `div` | PRESENT_AND_PARSED | 3,738 | TRANSFERABLE |
| WORD_FORM / SIGN | stream `word` | PRESENT_AND_PARSED | 3,147 / 5,792 | TRANSFERABLE (A_SIGN, 259) |
| LOGOGRAM | stream `other` | **PRESENT_BUT_NOT_PARSED** | 1,056 | PARTIALLY_TRANSFERABLE |
| FRACTION | stream `other` subset | PRESENT_BUT_NOT_PARSED | (in other) | PARTIALLY_TRANSFERABLE |
| MEASURE_MARKER | — | CHANNEL_UNKNOWN | 0 | UNAVAILABLE |
| DOCUMENT_SERIES | — | **GENUINELY_ABSENT** | 0 | LB_ONLY_DIAGNOSTIC |

**Rulings:** LA logograms/fractions are opaque (`A_LOGO_UNRESOLVED`) — **NOT** equated with LB logograms of
similar shape; no LB commodity meaning imported. A_SIGN vocab **disjoint** from B_SIGN
(`test_linear_a_no_semantic_mapping`). Remaining gap: a SigLA glyph-level pass could sub-type the `other`
bucket (logogram vs fraction vs measure) — deferred, not blocking (structural dry-run). Classes:
`data/reference/linear_a_structural_classes.csv`.
