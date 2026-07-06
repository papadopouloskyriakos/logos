# AB_SIGN_EQUIVALENCE_AUDIT — §V (FROZEN)

_Rule `ab-equiv-v1-2026-07-06`. Built by `src/ab_equivalence/build_equivalence.py`; frozen artifact
`data/gold/ab_sign_equivalence.json` sha256 `77de6684a37cd4efa118bbc3e46bdc27fac86822762fa15964e814dc297f6b20`
(`data/manifests/ab_sign_equivalence.sha256`). Counts generated. **Frozen before any sequence matching.**_

## What was frozen
| tier | meaning | count |
|---|---|---|
| **A** | SigLA AB-class = conventional A/B homomorph (GORILA shared numbering) | **77** |
| **X** | SigLA A-only = Linear-A-specific, no LB homomorph → excluded from primary | **299** |
| — | total repertoire | 376 |
| (robustness) | tier-A with LA attestation ≥ 10 tokens (`high_attestation`) | 63 |

Each row: `gorila_number, la_sign_id (AB##), lb_sign_id (*##), equivalence_level, confidence_tier,
graphic_similarity_basis, source_authority, allograph_scope, site_scope, chronological_scope,
la_attestation, high_attestation, disputed_flag, phonetic_value_used=false,
target_pair_used_in_selection=false`.

## Basis — pair-blind and phonetic-blind by construction
The map is the **SigLA AB-vs-A classification**: SigLA/Salgarella marks a sign `AB` iff it is attested
in **both** Linear A and Linear B (a conventional homomorph, same GORILA number), else `A`. This is a
property of the **sign repertoire**, fixed by Salgarella & Castellan / GORILA / the Ventris–Chadwick
convention **with no reference to any toponym pair or projected sound value**. The builder reads only
the SigLA sign catalogue + LA attestation counts; it never touches a phonetic table, a place-name list,
or the known-pair ledger. Enforced by `test_ab_equivalence_blindness` (source-level + content-level:
zero pair tokens; every row `phonetic_value_used=false`, `target_pair_used_in_selection=false`).

## Comparison levels (kept separate for §IX)
```
LEVEL_1  exact shared GORILA sign-ID — the 77 tier-A AB signs (la AB## ≡ lb *##)   ← primary
LEVEL_2  palaeographic equivalence classes — identical to LEVEL_1 until per-glyph allographs
         are clustered (deferred; SigLA carries the drawings/bboxes to do it)
LEVEL_3  projected LB phonetic values — FIREWALLED; used only as the §IX A4 ablation and the A5
         wrong-value control, never to define the primary result
```

## Tiering choice + declared limitation (no fabrication)
Tier A rests on SigLA's peer-reviewed AB-class designation. A finer per-graph palaeographic
**B/C** sub-tiering (probable / disputed homomorphs, with `disputed_flag`) would require collating the
**Salgarella 2020** monograph (*Aegean Linear Script(s)*, held locally at
`corpus/bronze/salgarella_2020/`, incl. its Index of Signs). That collation is **deferred and
declared** — it is not silently assumed. To avoid fabricating tiers we cannot yet justify, the
robustness handle used downstream is `high_attestation` (LA-side token frequency ≥ 10; 63/77 signs) —
pair-blind and non-phonetic — supporting a prespecified sensitivity variant ("does the result survive
restriction to well-attested homomorphs?"). This adapts the spec's `SENSITIVITY_1` (tier-B+C) with a
defensible, non-fabricated alternative; the palaeographic sub-tiering remains an available refinement.

## Chronological caveat (carried to §VI/§XIV)
The equivalence is cross-horizon by construction: LA (MM II–LM IB) vs LB (LM II–III). Persistence of a
*graph* across ~two centuries is `ORTHOGRAPHIC_CONTINUITY`; it does **not** by itself license
`LEXICAL_` or `PHONETIC_CONTINUITY` (charter rule). The circularity audit (§XIV) must check that this
map's construction never consulted the LB target set or the known pairs — which, per the blindness
tests, it did not.
