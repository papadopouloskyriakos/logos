# FEATURE TRANSFERABILITY MATRIX (Stage 4 §II-D)

Every graph feature is classified `TRANSFERABLE` / `LB_ONLY_DIAGNOSTIC` / `AB_SHARED_SENSITIVITY` /
`EXCLUDED`. Machine-readable: `data/schema/feature_transferability.csv` (29 features).
Class counts: **TRANSFERABLE 22 · AB_SHARED_SENSITIVITY 3 · LB_ONLY_DIAGNOSTIC 1 · EXCLUDED 3**.

## Rules (binding)

- **TRANSFERABLE** features exist or are reproducibly approximable in **both** scripts → the ONLY class the
  primary transfer-eligible model may depend on.
- **LB_ONLY_DIAGNOSTIC** may diagnose the LB benchmark but must NOT define the transferable model.
- **AB_SHARED_SENSITIVITY** may use the frozen shared-sign repertoire ONLY in a later sensitivity analysis —
  and **AB-shared signs are never treated as sound-equivalences**.
- **EXCLUDED** never enters model-visible data.

## By class

**TRANSFERABLE (22):** opaque sign identity (within-script), within-script sign frequency, word-form length,
token position (in word / entry), entry position in row, document side/face, document series-or-type (LA:
coarse), site, findspot, chronological phase (LA: coarse), support type, logogram identity (opaque),
numeral value/type, fraction structure, damage flag, uncertain-boundary flag, n_alternatives,
cross-document recurrence (`REPEATS_FORM`), cross-site recurrence, single-site clustering, formula-cluster
membership.

**AB_SHARED_SENSITIVITY (3):** row/column layout coordinates (LA-rich via SigLA, LB-partial via LiBER);
allograph class (SigLA palaeography); the **AB-shared-sign bridge** (a separately versioned sensitivity
layer — *not* a sound map).

**LB_ONLY_DIAGNOSTIC (1):** scribe — no systematic LA equivalent (and empty in this DĀMOS dump; see the repr
spec caveat). Excluded from the transferable model.

**EXCLUDED (3):** phonetic transliteration; Greek/lemma/gloss/translation; known role/entity. All routed to
`data/evaluation_only/`.

## The load-bearing transfer risk (carried from Stage 3)

**Sign-inventory non-homomorphy.** LB (`B_SIGN`, 89) and LA (`A_SIGN`, 58) vocabularies are kept **separate**
and never merged. A model keyed on *specific* sign identities will not transfer; the transferable model must
use sign identity only as (a) within-script-opaque distributional structure and (b) — in sensitivity only —
the frozen AB-shared bridge. This is an explicit ablation/null to build into the gate (later stages), not a
feature to trust.
