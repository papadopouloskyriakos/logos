# J2 — Sealed Prediction Register

**Programme:** J2 SEALED PREDICTION PROGRAMME. Five committed, hashed prediction
sets (+ the prospective Anetaki structural seal). Constitution **v2.2** · claim
layer **L2/L3** (structure / functional role) · **NO phonetic value assigned** ·
**NO transfer licence claimed**. Seed `20260708`. `as_of = 2026-07-07`.

- Builder: `scripts/j2_build_seals.py` (run, real measured numbers below).
- Manifests: `seals/*.json` — each carries the prediction, probability, ranked
  alternatives, failure criterion, scoring rule, and a `plan_hash` (sha256 of the
  frozen `structural_predictions` block).
- Index + sha256 of every manifest: `manifests/SEALS_INDEX.json`.
- Held-out **target answers are stored OUTSIDE the sealed manifests** in
  `data/seal_targets/*.json` (never model-visible at prediction time; predictions
  are derived from TRAIN / INDUCTION partitions only, then scored).

## Phonetic scoring — global

**`NO_CANDIDATE_TO_SEAL`.** No value-bearing candidate survived the end-to-end
multi-family null in earlier waves (position→C/V REFUTED as freq artifact;
substitution axis not recoverable on LA; seed-propagation 0.87 = freq artifact;
cross-script transfer NULL; anchors SEED_A=0). Every seal therefore carries only
**structural (L2/L3)** predictions from the two validated grammars (A- prefixation;
ledger CARRIER-VALUE / KU-RO-TOTAL; libation rigid order). The Anetaki phonetic
payload stays sealed as `NO_CANDIDATE_TO_SEAL`.

## Global priors (measured, full 1341-inscription corpus)

- LA word-initial-A base rate: **0.0572** (n_words = 3147).
- Full-corpus A- recurrent-stem enrichment: obs 17 vs freq-null mean 15.98
  (direction enriched; the strong Holm-significant A- signal in E3 is on the
  larger token headline count, obs 47 vs null 23.47, p_holm 0.0099 — the
  recurrent-stem-only restatement here is weaker/underpowered but same direction).

---

## Scoreable-now seals (SEAL_2–5): held-out LA partitions

| seal | split | primary structural prediction | measured result | verdict |
|---|---|---|---|---|
| **SEAL_2** unseen inscriptions | random 15% held out (n=201 / train 1140) | held-out A- rate in train 2·se band **[0.0375, 0.0788]**, A-enriched, ledger well-formed ≥0.70 | rate_A **0.0525** (in band), enriched ✓, ledger wf **0.857**, 7 KU-RO ledgers | **SUPPORTED** |
| **SEAL_3** unseen site | whole non-HT site **Khania** held out (159 ins) | abstract CARRIER-VALUE grammar transfers (wf ≥0.85); KU-RO TOTAL lexeme **predicted ABSENT** (HT-specific in train) | carrier-value wf **0.8525** ✓; **KU-RO carriers = 0** (absence predicted correctly); A- underpowered (obs 2 vs null 3.19, not enriched — expected) | **SUPPORTED** |
| **SEAL_4** unseen formula family | libation carriers held out; per-carrier LOO order | leave-one-carrier-out induced order predicts held-out order with **0 inversions** | 13 multi-anchor carriers, 45 co-occurring pairs, **0 inversions** | **SUPPORTED** |
| **SEAL_5** masked notation | 15% of numerals masked (n≈191) | ledger arithmetic recovery of masked numerals **beats** frequency baseline | only **6** masked numerals land in a TOTAL-constrained segment; arith exact **1** vs baseline exact **2** (arith near 1) | **UNDERPOWERED_NO_SIGNAL** |

### SEAL_2 — unseen inscriptions
A- prefixation and the ledger entry grammar both transfer cleanly to a random
15% held-out slice: the held-out word-initial-A rate lands inside the train-derived
2·se band, is directionally enriched, and 85.7% of held-out ledgers are fully
CARRIER-VALUE well-formed. **SUPPORTED.**

### SEAL_3 — unseen site (Khania)
The interesting, honest result. A well-calibrated predictor trained on non-Khania
data sees that the KU-RO / PO-TO-KU-RO **TOTAL lexeme is HT-concentrated**, so it
predicts the lexeme will **NOT** appear at Khania while the **abstract** carrier-value
entry grammar **will** transfer. Both came true: Khania carries **zero** KU-RO/KI-RO,
yet 85.3% of its ledgers are CARRIER-VALUE well-formed. This cleanly separates a
**transferable abstract grammar** (entry = carrier + value) from a **site-specific
lexeme** (the KU-RO total word) — established without any phonetic reading. Per-site
A- is power-limited (as E3 already showed), so no significance is claimed. **SUPPORTED.**

### SEAL_4 — unseen formula family (libation)
The rigid libation template **OP < SSR < UNK < IPN < SIR** survives a
leave-one-carrier-out test: for each multi-anchor carrier, the order induced from
the *other* carriers predicts its internal anchor order with **zero inversions**
across all 45 co-occurring pairs. The template is not a single-carrier artefact.
**SUPPORTED.** (Caveat inherited from E2: per-pair support is small; the strength is
in the aggregate zero-inversion LOO.)

### SEAL_5 — masked notation
A committed **negative**. At 15% masking, ledger arithmetic (masked numeral :=
sum/complement under `total == Σ entries`) does **not** beat a trivial mode-value
baseline, because (a) only 6 masked numerals fall in a segment with a visible TOTAL
and a single unknown, and (b) the silver corpus drops fraction glyphs, so the
arithmetic identity rarely closes exactly (the same ceiling seen in E2: 7/31 exact).
Verdict **UNDERPOWERED_NO_SIGNAL** — recorded honestly, not laundered into a pass.
The seal stands as a hashed negative.

---

## Prospective seal: ANETAKI_FINAL_EDITION_DELTA_SEAL

**STRUCTURAL ONLY. Phonetic = `NO_CANDIDATE_TO_SEAL`.** Carriers: KN Zg 57 (ivory
Ring, ~119 signs, no numerals) + KN Zg 58 (ivory handle, accounting). Scored when
Anetaki II's editio princeps publishes the held-out transliteration.
**Every J1-public item is EXCLUDED** (counts, layout skeleton, printed signs,
directionality, object identity, length, genre split — see
`data/J1_exposure.json.excluded_from_prospective_scoring`). Predictions attach only
to the currently-**unpublished transliterated sign-group content**.

- **P1 — Face-B A-prefixation.** Of the 6 held-out Face-B sign-groups, the count
  beginning with sign A(AB08) is consistent with the LA base rate 0.0572 →
  expected ≈ 0.34, binomial 95% interval **[0, 1]**. Most likely 0–1 A-initial.
  Fail if the observed count falls outside [0, 1]. (A ≥3 count would signal a
  cult-specific A- enrichment — explicitly *not* our prediction.)
- **P2 — accounting handle ledger grammar.** Numerals on the numeral/fraction-bearing
  handle obey the CARRIER-VALUE rule (each numeral immediately preceded by a
  value-carrier at ~corpus 0.966). p(carrier-value holds) = 0.80; p(explicit KU-RO
  terminal total) = 0.30 (lower — KU-RO is HT-specific, cf. SEAL_3). Fail if <70%
  of published handle numerals are carrier-preceded.
- **P3 — Ring libation order.** Prior that any libation formula appears on the Ring
  is **LOW (0.25)** (authors report "few parallels"). *Conditional*: IF ≥2 libation
  anchors co-occur on a Ring face, they appear in canonical order
  OP<SSR<UNK<IPN<SIR (0 inversions), p=0.85. An inverted order would REFUTE the
  template on new material.

Verdict: **SEALED_PROSPECTIVE_NOT_YET_SCORED.**

---

## Integrity

| seal | manifest sha256 (16) | plan_hash (16) | status |
|---|---|---|---|
| SEAL_2 | `2fe8581fbd2dcf11` | `f5881ac45fbb9ec9` | SEALED_AND_SCORED |
| SEAL_3 | `840001c806149125` | `0459ab59de8ed84c` | SEALED_AND_SCORED |
| SEAL_4 | `ef1abfd424846597` | `d08e9dcbb45f9c1a` | SEALED_AND_SCORED |
| SEAL_5 | `e57388ae94c2e64a` | `8f1683ee5e55c73f` | SEALED_AND_SCORED |
| ANETAKI | `76c18003a1dda9a0` | `979e2fd2c9ecaed6` | SEALED_PROSPECTIVE |

Full 64-char digests in `manifests/SEALS_INDEX.json`. `plan_hash` = sha256 of the
frozen `structural_predictions` block (prediction integrity); the manifest sha256
additionally covers the appended mechanical `verdict`. Targets held in
`data/seal_targets/` (separate from the sealed manifests).

**Non-circularity.** Predictions use only TRAIN / INDUCTION partitions; anchors are
anonymous GORILA sign-names, never phonetic/semantic values; known values grade
benchmarks only. No value-bearing candidate exists, so no phonetic reading is
sealed or claimed. Two seals are positive structural transfers (SEAL_2, SEAL_4),
one is a nuanced positive that separates transferable grammar from site-specific
lexeme (SEAL_3), one is a committed underpowered negative (SEAL_5), and the Anetaki
seal is a frozen prospective structural bet — all L2/L3, no decipherment.
