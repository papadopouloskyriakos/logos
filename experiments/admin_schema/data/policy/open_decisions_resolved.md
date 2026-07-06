# Open decisions — FROZEN — Stage 5 approved 2026-07-07

Requires explicit approval before Stage 5 freeze. The §XIII decisions plus two findings surfaced during
Stage 4/5.

## §XIII decisions

1. Is the 8-class **coarse ontology** appropriate as the transfer-gate load-bearer?
2. Should **`HUMAN_OR_INSTITUTION` stay merged**, or split PERSON vs INSTITUTION at coarse level? (Drafted
   merged — the split leans on Greek onomastics = LB-only.)
3. Should **`PLACE`** separate entity type (TOPONYM) from the destination/origin **relation**? (Drafted: yes
   — they are different prediction targets, TOKEN_ROLE vs ENTRY_RELATION.)
4. Does **`ANIMAL_OR_HUMAN_CATEGORY`** belong under COMMODITY_OR_CATEGORY or HUMAN_OR_INSTITUTION? (Drafted:
   under COMMODITY_OR_CATEGORY, since it is logogram/counting-bound.)
5. Is **`TITLE_OR_OFFICE`** structurally distinguishable enough for the fine ontology? (Drafted: LB-only
   diagnostic; likely too sparse/lexical for the gate.)
6. Which roles are **transfer-eligible**? (Draft in `label_transferability_draft.csv` — coarse mostly
   eligible; structural-notation = control; onomastic/morphological fine = LB-only.)
7. Which **notation classes are trivial controls only**? (Drafted: NUMERAL, FRACTION, unambiguous LOGOGRAM,
   TOTAL, SECTION_DIVIDER.)
8. **Are the fine labels — and the load-bearing GOLD_A non-trivial-unseen-form partition — too sparse for a
   powered gate?** (Draft estimate: 150–900 GOLD_A test units — this may force an early `NO_POWER`. THE
   central risk.)
9. Minimum annotation **agreement (κ)** required for GOLD_A / per class?
10. **Full** secure set double-annotated, or a **stratified subset**? (Drafted: full if feasible, else
    stratified by role×site×series.)
11. How are **disputed** scholarly interpretations handled? (Drafted: keep both labels, tier GOLD_B/C, never
    force.)
12. Any **LB-only feature** retained as diagnostic but excluded from transfer? (Drafted: scribe, fine
    chronology, fine layout.)

## Findings

- **(A) `site` mis-mapped — RESOLVED in Stage 4.1.** Canonical `site_code` now = heading prefix (19 sites);
  `findspot_code`/`area_code_raw` preserved. `SITE_AND_FINDSPOT_AUDIT.md`.
- **(B) Scribe channel empty — RESOLVED in Stage 4.1.** Recovered from `hand_easy` (293 hands, 3,944 docs);
  `S4_LEAVE_ONE_SCRIBE_OUT = AVAILABLE`. `SCRIBAL_METADATA_AUDIT.md`.
- **(C) NEW — cross-site power is weak (needs a decision).** Post-correction, **KN dominates 71%** and only
  **6 sites have ≥30 docs** (5 small). PC3/S3 cross-site is load-bearing but is effectively "KN-vs-rest".
  Decide: (i) accept KN-vs-rest as the cross-site test with explicit caveat; (ii) require ≥k non-KN sites to
  clear PC3; or (iii) treat cross-site as `SUBGROUP_NO_POWER` beyond KN/PY. Do NOT issue NO_POWER from
  projected counts alone — but this is the sharpest remaining power risk alongside the small GOLD_A
  non-trivial-unseen partition (decision #8).
