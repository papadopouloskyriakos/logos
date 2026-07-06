# Stage 5.1 — annotation feasibility pilot (dev-only)

**Mechanical verdict: `NO_POWER`** (α 0.614 < 0.667). A rigorous negative result — the blinded coarse-role
annotation task, at pilot scale on a representative stratified sample, does not reach the frozen agreement
threshold for primary gold. Nothing was retuned; no model or Linear A inference was run.

## Design

160 distinct **content** word-form types, stratified: **KN 80 / non-KN 80 · hapax 80 / recurrent 80**
(deterministic seed). Each item given to two annotators with its evaluation-layer transliteration + entry
context + site/series. **Independent double annotation** by two agents with different framings (lexical-first
vs structure-first), blind to each other; then adjudication. Coarse ontology + gold tiers per the FROZEN
Stage-5 policy (ontology `781902c0`).

## Results

| metric | value |
|---|---|
| Krippendorff α (nominal, coarse role) | **0.614** |
| raw agreement | 0.725 |
| GOLD_A agreed yield | **5.6%** (9/160) |
| non-trivial GOLD_A agreed | **4** (KN 0 / non-KN 4 / hapax 1) |
| class balance (agreed) | HUMAN_OR_INSTITUTION 50 · UNKNOWN 33 · PLACE 12 · QUALIFIER 10 · COMMODITY 6 · OPERATOR 4 · DOC_STRUCTURE 1 |
| sparse classes | DOCUMENT_STRUCTURE, MEASURE_OR_QUANTITY |

## Power simulation (moot — α gates first, but reported)

Corpus pools: 4,759 distinct content forms; **3,123 hapax**; 1,968 KN-only; 2,791 non-KN. Min detectable
K = 16 (p=0.40 vs 1/8 null, 80% power). Scaled estimates: unseen-form GOLD_A non-trivial ≈ **39 units**
(≥16, would be powered); non-KN GOLD_A ≈ **140 units** (SITE_TEST_B viable). So *if* agreement were adequate,
the effective-unit power would clear — but it is not.

## Cross-site design (frozen)

`SITE_TEST_A` = train eligible non-KN → test **KN**. `SITE_TEST_B` = train KN → test eligible non-KN.
Individual site holdouts only for sites meeting a simulation-derived min-effective-unit threshold (KN, PY,
TH clear; MY/TI/KH likely `SUBGROUP_NO_POWER`).

## Honest caveats (load-bearing)

- **α is model-based** — two instances of the same model family, not independent humans → an **optimistic
  upper bound**. True inter-human α is unknown and could be lower; the NO_POWER is therefore, if anything,
  *robust*.
- The failure concentrates in (a) **hapax forms** (annotators split HUMAN vs UNKNOWN) and (b) the **tiny
  secure-GOLD_A yield** (5.6%). Many LB word-forms are not securely role-classifiable even in principle.
- This does NOT prove the task is impossible — a curated GOLD_A candidate set annotated by **real Mycenaean
  epigraphers** (not model agents) might clear the bar on the securely-classifiable subset. But **the pilot
  as run says NO_POWER**, and per the discipline the verdict is not moved.

## Exclusion (holdout hygiene)

The 160 pilot form-families + their **342 documents** (and any joins/scribal-copies/formula/morphological
siblings) are recorded in `data/pilot/pilot_exclusion_manifest.json` and **must be burned from any future
sealed holdout**.

## Mechanical verdict

```
NO_POWER   (α 0.614 < 0.667; GOLD_A non-trivial-unseen partition too thin at agreement)
```
Not `PROCEED_TO_FULL_ANNOTATION`. Not `MERGE_PREDECLARED_SPARSE_CLASSES` (α gates first; and merges may only
be justified by semantic indistinguishability / agreement / preregistered power — never model outcomes).
**Next decision is the reviewer's:** curate a GOLD_A-eligible subset + real human double annotation, or
accept the blinded coarse-role benchmark as underpowered at this scale.
