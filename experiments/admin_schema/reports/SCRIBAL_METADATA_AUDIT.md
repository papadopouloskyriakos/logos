# Scribal metadata audit (Stage 4.1 Correction 2)

**Problem:** Stage 4 read DĀMOS `vasewriter` — **empty (0/5799)** — and concluded scribe unavailable. That
was a wrong-field error, not a data absence.

**Sources inspected (DĀMOS item fields):** `vasewriter` (0), **`hand_easy` (5712 non-null)**,
`handpreptt3` (5712), `hand_easy_old` (5712), `newhand`/`newhand2` (997), `unhand` (11), `unclass` (20).

**Finding:** `hand_easy` / `handpreptt3` carry the DĀMOS scribal-hand classification (Knossos/Pylos hand
numbers, e.g. 117 [681 docs], 103 [210], 1 [227]). `-` = no hand assigned → scribe null.

**Operative field:** `hand_easy` → opaque `scribe = HAND_<n>`; **3,944/5,799 docs assigned, 293 distinct
hands.** Not inferred from vocabulary, layout, or model clusters (§IV restrictions honored). Provenance:
`scribe_source`, `scribe_assignment_type = DAMOS_hand_classification`, `scribe_crosswalk_version`.

**Verdict:** `S4_LEAVE_ONE_SCRIBE_OUT = AVAILABLE`. Scribe stays `LB_ONLY_DIAGNOSTIC` (no LA equivalent) —
usable to diagnose the LB benchmark, excluded from the transferable model. Crosswalk:
`data/reference/scribe_crosswalk.csv`; test `test_scribe_crosswalk`.
