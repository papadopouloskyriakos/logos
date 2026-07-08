# EPOCH-017 — DEVIATIONS

None. `scripts/e017_allograph_deconfound.py` executed the frozen prereg
(`epochs/EPOCH-017/prereg.md`, sha256 `3b527541f2ed427028fff73c5264394b874150257833c0f5f6cc32b0b48624c9`)
exactly as specified: STEP 0 source audit (recorded verbatim, pre-run), the feature partition
(`INV`/`SEN`, identical to the pre-existing `COUNT_IDX`/`ORIENT_IDX` in
`scripts/epoch009_stroke_corpus.py`), the synthetic positive control (3 scenarios, run first, PASS),
leg1'/leg2' on both partitions, the {p1_INV, p1_SEN, p2_INV, p2_SEN} Holm family, the rendering-shuffle
null, and the frozen mechanical verdict table. `result.json.deviations == []`.
