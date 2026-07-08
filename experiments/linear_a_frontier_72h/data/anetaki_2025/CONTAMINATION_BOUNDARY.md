# Contamination boundary — Anetaki material vs the frozen prospective seals

**Epoch:** EPOCH-001 · as_of 2026-07-08 · Constitution v2.2 Art. XII (no grading a target
by the rule that created it) + Art. IX.

## The two frozen seals targeting this material

| seal | campaign | plan_hash | status | targets |
|---|---|---|---|---|
| `ANETAKI_FINAL_EDITION_DELTA_SEAL` | research/linear-a-relative-phonology-seals (`experiments/linear_a_relative_phonology/seals/…`) | `979e2fd2c9ecaed68b3796fd54e91b2f3f7da8f41d43c36428d6b884fc0085f6` | SEALED_PROSPECTIVE, unopened | A-prefixation / ledger grammar / libation order (L2/L3) in the **unpublished** Face-B/C/β sign-groups |
| `M_ANETAKI_LATTICE_DELTA_SEAL` | research/linear-a-anchor-lattice (`experiments/linear_a_anchor_lattice/data/seals/…`) | see `M_ANETAKI_LATTICE_DELTA_SEAL.json` | SEALED_PROSPECTIVE, unopened | MP1 A-only token fraction; MP2 anchor-delta darkness; MP3 conditional substitution non-rescue — all on the **unpublished** transliteration |

## What this epoch acquired, classified

1. **J1-public / seal-EXCLUDED (no contamination possible):** everything in
   `sign_candidates.json` rows 1–35 derives from Kanta et al. 2024 — the exact document
   whose contents the J1 exposure audit already flagged and both seals **explicitly
   exclude** from scoring (counts, layout, printed individual signs, directionality,
   genre split, object identity). Re-recording it machine-readably adds ZERO scoring
   exposure.
2. **Preliminary unsourced (row 36, KNZg57a):** already inside `corpus/silver` since
   before both seals were frozen — it is part of the seals' own derivation-time corpus
   state (`in_current_corpus: false` in the M seal refers to the full carrier text, not
   this 5-token fragment, which the seal's base-rate computation already included via the
   silver corpus). No new exposure. HOWEVER: if the *Anetaki II* edition later confirms or
   refutes these 5 tokens, MP1 counting must treat them as PRIOR knowledge (exclude from
   any "prediction credit").
3. **Fringe rows 37–39 (Rjabchikov) and prediction row 40 (Chiapello):** registry
   objects, quarantined, confidence 0.0; both PREDATE the editio princeps and are
   themselves gradable against it. They must never be merged into scoring inputs.
4. **NOT acquired (still held out):** every transliterated sign-group — the 6 Face-B
   groups, ≥9 Face-C groups, the Face-β 4-sign sequence, the Face-A metope inventory, the
   6 fraction-sign identities. **The seals' scoring targets remain 100% unobserved.**

## Verdict on seal integrity

- `SEAL_SCOREABLE_CONTENT_ACQUIRED = false` — no scoring decision arises; nothing is
  handed to the orchestrator for scoring because there is nothing to score.
- Both seals remain SEALED_PROSPECTIVE and unopened. This epoch read only material both
  seals pre-declared as excluded-public.
- **Trigger protocol (unchanged):** the day *Anetaki II* (INSTAP Academic Press) publishes,
  DO NOT read the transliterations in an analysis session. First: freeze a scoring plan
  per each seal's own scoring_rule, then ingest mechanically, then score. Any repo session
  that reads the edition's sign-groups before the scoring plan is frozen contaminates BOTH
  seals — record that session id here if it ever happens.

## Held-out status of existing seals for the silver corpus

The existing silver corpus units used by prior campaigns (held-out inscriptions/sites for
the L2/L3 positives) are untouched: this epoch wrote only under
`experiments/linear_a_frontier_72h/` and never modified `corpus/silver`.
