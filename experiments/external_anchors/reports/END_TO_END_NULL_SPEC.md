# End-to-end null framework specification

Estimate the false-positive rate of the **entire** discovery procedure, not just the final matching
score. The null pipeline replays **every** adaptive choice in `ADAPTIVE_CHOICE_INVENTORY.md`
(candidate selection, segmentation, transcription draw, mapping search, restart, best-of-search,
held-out split). Significance is **empirical** (fraction of null runs ≥ the observed result), never a
nominal hypothesis count. Scaffold: `src/nulls/`; configs `nulls/configs/`; receipts per
`SEARCH_RECEIPT_SPEC.md`.

## Null families (each a synthetic/permuted anchor or system passed through the SAME pipeline)
1. **synthetic toponyms** — random skeletons matched on length + sound-inventory to the real anchors.
2. **unrelated real toponyms** — attested non-Cretan place-names of similar length.
3. **shuffled anchor identities** — real anchor forms, permuted labels.
4. **shuffled LA candidate assignments** — real candidate forms, permuted class/target labels.
5. **synthetic sign systems** — preserve LA sign frequencies, random strings.
6. **transcription-variant draws** — alternative readings of damaged signs.
7. **wrong projected sign-value maps** — deliberately incorrect fixed mappings.
8. **corrupted Linear-B positive controls** — the E2 control with the relation broken.
9. **false candidate languages / synthetic lexica** — for E8.
10. **target-label permutations** — permute the held-out truth.

## Structure preservation (nulls match the real data on)
word-length distribution · sign frequencies · repeated strings · candidate-slot counts · site
structure · genre structure · recurrence patterns · uncertainty patterns · anchor lengths · repeated
phonological material · train/held-out split size. (So a null result is "as attractive by chance",
not "obviously different data".)

## Operating rule
The confirmatory statistic is compared to the **null distribution over the full pipeline**. Report
`P(procedure ≥ observed | null)`. The pilot already shows the **in-sample** statistic has null
P≈1.0 → only the **held-out statistic under a frozen mapping** is admissible. Every real and null run
emits a search receipt; there is **no adaptive choice outside the receipt**.

## Status
Spec + config schema + generators scaffolded (`src/nulls/nulllib.py`, families 1/3/4/5/10 have working
generators; 2/6/7/8/9 are stubs pending the real anchor+calibration inputs). Tests assert every
family preserves its declared structure and that a run cannot execute without emitting a receipt.
