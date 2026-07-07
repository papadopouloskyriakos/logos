# Word-segmented pipeline + candidate round 1 + source audit

## Word-segmented full pipeline → `IMPROVED` (channel-dependent trade-off)
GORILA word units (2,479 filtered words, mean 2.0 signs) vs packed inscriptions. **The channels diverge:**
- **Substitution HURT:** LA max context-weight **105 → 47** (word) — GORILA short words (1.84) starve the
  context-hungry channel, moving *away* from the ~120 clean regime; strong edges 328→154; C/V-boundary
  enrichment z 2.59→−0.50 (null). `AT_END_TO_END_NULL` for this channel (opaque-LB gate still fires z=8.46 —
  short-word starvation, not a dead method). **Corrects the WP2 "clean win": segmentation is not uniformly
  better — the substitution channel prefers longer (inscription) context.**
- **C/V bootstrap HELPED:** seeding {A,I} propagates to 6→9 vowel-like signs; word units recover U (2nd). But
  unvalidated on LA (mostly CV signs; true vowel O mis-ranked bottom — coverage, not accuracy). The mechanically
  validated result is the unchanged opaque-LB gate (min 3 correct vowel seeds → AUC≥0.75).

## Candidate-language round 1 → `AT_END_TO_END_NULL`
3 preregistered families (West Semitic, Pre-Greek/Anatolian, agnostic control) on GORILA word units, bounded
correspondences + small cited lexica, scored vs the multi-family null (order-shuffle + wrong-language LB +
random-prior) + 300-draw random-lexicon calibration + leave-one-lexeme-out. **No family is a genuine signal:**
West Semitic clears aggregate FWER 0.030 **but the random control ALSO clears at 0.030** — the "significance"
is a same-structure-lexicon artifact, exactly what the multi-family null exists to catch. Only KU-RO='total'
survives (a single known lexeme). Consistent with WP6.

## Source audit → `INVENTORY_BUILT` (63 sources; quota met)
63 sources audited (25 verified on disk, 6 UNAVAILABLE with what they'd add). **48 independent of the
GORILA/Ventris VALUE lineage** across 6 lineage clusters (palaeography, internal structure/metrology,
archaeology, computational method, sister scripts, Ugaritic-Hebrew). Key: **every phonetic reading of LA is
single-sourced through GORILA homomorphic transfer**; only structural readings are value-agnostic. **The single
most valuable unavailable source is Anetaki II** (forthcoming INSTAP editio princeps of KN Zg 57/58, the
~119-sign longest LA inscription) — the genuine prospective held-out gold.
