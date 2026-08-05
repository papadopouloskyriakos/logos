# PREREG — NAME-PARALLEL-01 (Packard-1974 name-parallel probe under logos discipline)

- **task_id:** NAME-PARALLEL-01
- **date frozen:** 2026-08-05 (after calibration went GREEN; BEFORE the LA true-value statistic
  was computed anywhere — `results/name_parallel_calibration.json` records
  `la_pool_true_value_statistic: NOT_COMPUTED` in every calibration round)
- **constitution:** v2.3; **articles_triggered:** V (L3 cap), VII (search receipt = CriterionLog),
  VIII (n_eff), IX (deflated bars + info-budget panel), XI (single L_LB_DECIPHERMENT lineage;
  SRC-NAMESCOG⊕SRC-DAMOS = 1 vote), XII (S1/S2 strata reported), XVII (append-only),
  XXII (this header)
- **claim_layer cap:** L3. A positive is frequency-band-level onomastic-overlap evidence ONLY.
  It validates NO individual sign value, creates NO anchor, and does not modify the published
  REFUTE_LOTO_FRAGILE or the anchor-lattice foothold ≈ 0.
- **seed:** 0; **driver:** `run_probe.py` (this directory), single execution.

## Frozen primary criterion C1 (`packard1974_kn_primary`)

LA word types (≥3 signs, logogram-filtered via `signs_ontology.json`, slots 1–3 decodable under
the conventional AB→LB value identity; pool = 501 decodable types) match a Knossos-attested
Linear B personal name (`names.cog` glossed rows ∩ DĀMOS KN wordform types = 155 names) iff
sign 1 and sign 2 are value-identical and sign 3 shares its consonant (final vowel disregarded).
Statistic **M_obs** = number of matched LA TYPES (Packard's unit).

## P1 — the falsifiable, mechanically graded prediction

**MATCH_EXCESS iff M_obs > augmented bar**, where the augmented bar (bar design v2) =

    max( E[max over n_eff draws] of the B=1,000 banded-map-permutation null,
         Cornish–Fisher + Bonferroni corrected margin of that null at n_eff,
         the OUT-OF-SAMPLE L_fake floor from the green calibration file )

with **n_eff = 12** (the full criterion grid, instrumented by CriterionLog — every variant ever
evaluated, including during development and calibration debugging, is in the grid) and the
L_fake floor = **148.42** (B=200 markov-texture corpora, dedicated seed range 700000+,
best-of-grid counts, corrected-margin operative bar; `calibration_sha256` recorded in
result.json binds the exact file).

Below the bar: **NULL** if k_min ≤ the plausible onomastic band, **DATA-LIMITED** if
k_min > band, where **k_min** = ⌈augmented bar − μ0(banded null)⌉ planted true matches needed
for detection, and the plausible band = 5% of the decodable pool (⌊0.05·501⌋ = 25 types).
**INVALID** only via gate failure (red/absent calibration, prereg hash mismatch).

- **allowed_verdicts:** MATCH_EXCESS | NULL | DATA-LIMITED | INVALID

## Multiplicity pre-commitment

C1 is the ONLY confirmatory criterion. The 12-variant grid
({name_scope: knossos/all_sites/full_lexicon} × {min_signs: 3/2} × {slot3: consonant/exact})
is EXPLORATORY; its counts may be listed in result.json but grade nothing. n_eff = 12 feeds
every bar. (The Tsirkas unrestricted→full-lexicon→Knossos-restricted criterion slide is the
failure mode this clause blocks.)

## Bar-design disclosure (Art. XVII honesty)

Calibration round 1 (bar v1: banded-map bars only) was **RED** — fabricated L_fake corpora
matching LA's sign texture false-fired 41.6% (git history of
`results/name_parallel_calibration.json`, commit 1b2da76). The bar was hardened to v2 by adding
the out-of-sample L_fake floor (the house morphology-gate max(permutation, L_fake) pattern) and
recalibrated: false-fire 1/500 = 0.2% (CP95 0.9%), positive control still fires (39 vs 6.67).
The LA statistic was computed in NO round; the hardening is calibration-driven design, not
outcome-driven tuning. Consequence accepted up front: the v2 bar is dominated by the L_fake
floor (~148 of 501 types), so DATA-LIMITED is the expected verdict unless onomastic overlap is
massive; that is the honest price of a bar that texture alone cannot beat.

## Blocked unless (fail CLOSED)

`results/name_parallel_calibration.json` exists, `fast=false`, `calibration_green=true`;
`plan_hash.txt` = sha256 of this file. The driver refuses (verdict INVALID) otherwise and never
computes M_obs.

## Reported, non-verdict rows

N2 document-permutation null (pseudo-Knossos, B=500); S1 Salgarella-dark-blue stratum; S2
toponym-motivated-signs-excluded stratum (the sharp Art. XII circularity check: excess vanishing
under S2 = the anchors restated); Art. VIII effective_n over matched-type attestations
(dims type+site); Art. IX info-budget panel.
