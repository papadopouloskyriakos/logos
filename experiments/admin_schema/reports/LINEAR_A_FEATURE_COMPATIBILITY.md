# LINEAR A FEATURE COMPATIBILITY (§IV)

**Rule:** every feature used by the *transferable* model must be representable in Linear A. Otherwise remove
it from the primary model or isolate it as **Linear-B-only sensitivity** evidence. Audited against the logos
silver LA corpus (`corpus/silver/inscriptions.json`: fields `id, signs, site, support, context`; 1,341
inscriptions / 52 sites) and **SigLA** (`corpus/bronze/sigla_browse_2026/database.js` → `scripts/sigla_decode.py`:
802 docs / 376 signs, with bounding boxes).

| Feature (transferable) | Linear B (DĀMOS) | Linear A (silver / SigLA) | verdict |
|---|---|---|---|
| raw sign identity (opaque ID) | B-number (de-phoneticised) | GORILA/SigLA sign ID (natively opaque) | ✅ both — **but inventories only partially homomorphic; treat signs as within-script-opaque + AB-shared bridge** |
| sequence length / n-gram | ✅ | ✅ (`signs`) | ✅ |
| within-word / entry / row position | ✅ (line numbers, word boundaries) | ✅ (SigLA layout; silver structured) | ✅ |
| layout coordinates | ~ (LiBER partial) | ✅ (SigLA bounding boxes) | **sensitivity** — LA-rich, LB-partial; not transfer-critical unless LiBER confirms |
| adjacent-token classes | ✅ | ✅ | ✅ |
| logogram / ideogram identity | ✅ | ✅ (LA logograms/ligatures) | ✅ |
| numeral / fraction structure | ✅ | ✅ (LA fractions — Corazza et al. 2021) | ✅ |
| document / support type | ✅ (`object`) | ✅ (`support`) | ✅ |
| site / findspot | ✅ (`find_area`) | ✅ (`site`) | ✅ |
| chronology / phase | ✅ (`chronology1`) | ~ (`context`; coarser) | **partial** — coarse-map or LB-only sensitivity |
| scribal hand | ✅ (DĀMOS scribe) | ✗ (not systematically available for LA) | **LB-ONLY sensitivity** — exclude from primary transferable model |
| damage / uncertainty | ✅ (editorial marks) | ✅ (SigLA/silver uncertainty) | ✅ |
| allographic class | ~ | ✅ (SigLA palaeography) | ✅ (represent as within-script) |
| frequency / cross-document recurrence | ✅ | ✅ | ✅ |
| cross-site recurrence | ✅ (52+ LB sites) | ✅ (52 LA sites) | ✅ |

## Transfer-critical PRIMARY feature set (representable in both)

opaque sign identity · sequence/position · entry/row/word structure · adjacent-token classes · logograms ·
numerals/fractions · support type · site/findspot · recurrence (within- and cross-document, cross-site) ·
damage/uncertainty · allography.

## Excluded from the transferable model (LB-only → sensitivity)

- **Scribal hand** (no systematic LA equivalent) — LB-only sensitivity (`A5` ablation).
- **Fine chronology** (LA coarser) — coarse-bucket, or LB-only sensitivity.
- **Fine layout coordinates** (LA-rich via SigLA, LB-partial) — sensitivity until LiBER confirms symmetry;
  note the asymmetry runs *opposite* to the others (LA-rich here), so it is a candidate *LA-only* enrichment
  for the eventual transfer, not a transferable-training feature.

## Key transfer risk (flag now)

**Sign-inventory non-homomorphy.** LA and LB share many signs (the AB-series) but not all; a model keyed on
*specific* sign identities will not transfer cleanly. Mitigation to specify in §V/§IX: represent sign identity
(a) as *within-script-opaque* distributional features and (b) via the **AB-shared bridge** only where a sign
is attested in both — never assume a global sign alignment. This is the single largest structural threat to
transfer feasibility and must be an explicit ablation/ null in the gate.
