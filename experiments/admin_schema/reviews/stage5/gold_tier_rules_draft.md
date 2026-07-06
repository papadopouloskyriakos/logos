# Gold tier rules — DRAFT (NOT FROZEN / NOT COMMITTED)

Primary evaluation uses **GOLD_A only**; sensitivity uses GOLD_A+GOLD_B; GOLD_C never enters the primary
benchmark.

| tier | criterion |
|---|---|
| **GOLD_A = secure** | role uncontested in the standard LB literature; ≥1 explicit source citation; annotators agree; not damage-dependent; structurally corroborated (e.g. logogram/numeral adjacency for a COMMODITY/QUANTITY, destination structure for a PLACE) |
| **GOLD_B = probable** | role supported but with a bounded, cited uncertainty (one plausible alternative); OR structurally clear but lexically debated |
| **GOLD_C = disputed / sensitivity-only** | scholarship genuinely divided, or role recoverable only via contested reading; used ONLY for sensitivity, never primary |
| **GOLD_X = excluded** | uninterpretable, heavily damaged, vestigial, or purely editorial token; removed from all scoring |

Rules: every row carries `confidence`, `source_citation`, `annotation_rationale`, `dispute_flag`,
`alternative_labels`. A disputed scholarly interpretation is recorded with BOTH labels (never silently
resolved) and tiered GOLD_B or GOLD_C accordingly. Damage-dependent labels cannot be GOLD_A.
