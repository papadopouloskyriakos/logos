# EPOCH-011 — Unit-slot + arithmetic-totals detectors → **NO_POWER × 2 (both channels), with the E007 "live U channel" unmasked as a class-prior artifact**

**Stage header (Art. XXII).** Frontier F5 · gate A · seed 20260708 · prereg
`epochs/EPOCH-011/prereg.md`, plan_hash `38e5762b187cdda84d49e41c726d1c8df39108577a73fbd1269f96345478d25c`
(frozen 2026-07-08T04:46:45Z, before any run). Articles: V, VII, VIII, IX, XI, XII, XV, XVII, XVIII, XXII.
Claim layer: **L2/L3 only**; no licence touched; no constraints emitted (both gates stayed closed). Verdicts
computed mechanically from the frozen criteria; zero deviations.

## Question

E007 left two channels "live": (1) the unit-slot geometry (post-hoc U recall .862) and (2) the missing
arithmetic sum-consistency feature for totals. This epoch formalizes both as dedicated, preregistered
detectors — A calibrated under a WITHIN-SITE LB split (KN-train/KN-test, killing the convention confound
E007 diagnosed), B calibrated on LB to-so docs — with blind LA transfer gated on LB validation, plus a
non-gating cross-check against the E004 fraction channel.

## Design (frozen)

- **Detector A (unit-slot):** rule space of 6 value-blind geometric rules over `n_signs==1 ∧ followed_by_num
  ∧ X`; selection by F1(gold U) on KN-train (308 docs); grade KN-test (352) + non-KN (433). Fire =
  KN-test F1 ≥ .60 ∧ non-KN F1 ≥ .50 ∧ > numeral-detach null p95.
- **Detector B (totals):** 3 sum tests (global / prefix / suffix-block, exact integer) × 2 attribution rules
  (nearest-group / line-initial-group; forced by the pre-freeze audit fact that **0** gold-T tokens are
  immediately numeral-followed in LB); (doc,type)-deduped (Art. VIII); selection on KN; grade non-KN. Fire =
  precision ≥ .30 ∧ recall ≥ .10 ∧ > value-permutation null p95 ∧ n ≥ 10.
- **PCs run FIRST (both passed):** PC-A F1 .958/1.00 on two planted unit geometries; PC-B precision =
  recall = 1.00 on planted exact-sum totals. The machinery is proven; everything below is about the corpora.

## Results

**Detector A — does NOT fire → NO_POWER.**

| unit | precision | recall | F1 | bar |
|---|---|---|---|---|
| KN-test (within-site) | .148 | .863 | **.253** | ≥ .60 FAIL |
| non-KN (site transfer) | .483 | .892 | **.627** | ≥ .50 pass |
| numeral-detach null p95 (non-KN) | | | .257 | observed > null pass |

Post-hoc oracle table (`e011_posthoc.json` PH-A1): **no rule in the space exceeds F1 .262 within KN** while
the *same* rules reach .53–.67 at non-KN sites (R6 .665; TH .819). The failure is not rule selection — it is
the geometry itself. PH-A2 gives the mechanism: among single-sign numeral-followed occurrences, gold U is
**14% at KN vs 47% at non-KN**. Precision tracks the base rate everywhere; the rules add essentially no
discrimination of U from C beyond the class prior. **Consequence: E007's "unit-slot channel is live"
(post-hoc U recall .862) is unmasked as a class-prior artifact of unit-heavy held-out sites** — the third
frequency-artifact unmasking of this research line (after position→C/V and seed-propagation).

**Detector B — does NOT fire → NO_POWER.**

| metric | observed | bar |
|---|---|---|
| non-KN precision(T) | .053 (1/19) | ≥ .30 FAIL |
| non-KN recall(T) | .013 (1/80) | ≥ .10 FAIL |
| value-perm null p95 | .038 | observed > null pass |
| max-num adversarial baseline | .031 | (beaten, non-gating) |

Selected variant V2+A2 (prefix-sum, line-initial attribution; KN F1 .108, the only variant with any KN true
positive). PH-B1 mechanism: of 67 non-KN gold-T docs, only **2 (V1) / 3 (V2) / 21 (V3)** contain ANY
sum-consistent numeral, and 71.6% of gold-T docs mix unit signs (mean 1.21 denominations). **LB totals are
multi-denomination (GRA n T m V k); exact integer sum-consistency is structurally absent from the LB
surface.** LB is the wrong calibration analogue for integer-sum totals logic — an analogue-mismatch
negative, not an arithmetic-channel refutation.

**Exploratory LA readout (PH-LA1; gate closed — NOT a result, no constraint emitted):** the identical blind
sum logic applied to LA's integer numeral stream concentrates on KU-RO: V2+A2 → 13 candidates, **7 = KU-RO**
(chance share 3.3%); V3 → 9/35. The arithmetic-totals channel plainly exists in LA — this epoch's LB-gated
transfer design is what could not license it. (KU-RO's totals role is prior knowledge; this is detector
sanity, not discovery. New-candidate types each appear once — no multiplicity-surviving novelty.)

**Cross-check C (non-gating):** 409 LA fraction events in 158 ledger docs; predecessors: line-initial 183,
numeral 108, single-sign word 76, multi-sign word 27. Fractions attach to *quantity positions* (after
numerals or directly after logogram-like single signs), consistent with E004; with no validated unit-slot
class, no unit-slot mediation is demonstrable.

## Mechanical verdicts

> **Detector A: NO_POWER** — within-site LB validation fails at the frozen bar; the E007 unit-slot geometry
> has no discriminative power beyond site-level class priors.
> **Detector B: NO_POWER** — the exact-sum detector, though above both nulls and the adversarial baseline,
> is an order of magnitude below the precision bar on LB because LB's metrological surface (multi-
> denomination quantities) does not carry doc-level integer sum-consistency.

**What this does NOT claim:** nothing about LA for record (both LA legs gated); no statement that totals
arithmetic is absent from LA (the exploratory readout suggests the opposite); KU-RO/PO-TO-KU-RO prior
structure untouched; no licence movement.

## Compliance line (Art. XXII)

Prereg + plan hash frozen before any run; PCs run first and passed; rule/variant spaces enumerated in the
prereg and selected on derivation folds only; nulls + adversarial baseline run as frozen; verdicts by frozen
arithmetic; zero deviations; LA legs not run for record (gated), LA readout labeled exploratory (E007
precedent); append-only artifacts under `epochs/EPOCH-011/` + `data/ledger_roles/detectors/`.

## Successor hypotheses

1. **LA-native totals detector, LA-internal held-out design (highest value):** derive the sum-consistency
   detector on an LA split-half (HT-even docs), grade on HT-odd + non-HT with KU-RO/PO-TO-KU-RO as frozen
   targets — no LB calibration leg at all, since PH-B1 proves LB is an analogue mismatch (its totals are
   multi-denomination) while PH-LA1 shows LA carries the integer channel. New totals-word candidates would
   then be gradeable with real multiplicity control.
2. **Denomination-aware LB totals detector:** treat each maximal (logogram, unit-sign…) run as a mixed-radix
   quantity vector (GRA n T m → n·radix + m with Bennett's ratios as the frozen, cited radix table) and
   re-test sum-consistency on vectors, not scalars. If it fires on LB, the transfer design of this epoch
   becomes runnable as specified.
3. **Unit-slot detection needs identity, not geometry:** PH-A2 shows the slot is shared by U and C; the
   separator at non-KN sites is WHICH sign (S,V,T,Z…) occupies it. A type-level detector (low-entropy
   single-sign types recurring across many docs in the post-numeral position, e.g. "GRA n T m" chaining)
   targeting the *numeral-sandwiched* signature (prev=NUM ∧ next=NUM) may recover units without values —
   test within PY, not KN, where units are dense.
4. **KN as the LA-analogue, not the derivation set:** KN's unit-sparse, logogram-heavy convention is
   structurally closer to LA (fractions instead of unit signs). Detectors should be calibrated on PY/TH
   (unit-rich) and *stress-tested* on KN as the honesty fold before any LA transfer claim.
5. **Fraction-as-unit hypothesis for LA:** cross-check C shows LA fractions occupy the post-quantity
   position where LB puts unit signs. A dedicated epoch could test whether LA fraction sequences after
   numerals obey the E004 descending-order grammar *specifically in totals-candidate docs* (linking the
   arithmetic channel to the fraction channel mechanically, e.g. sum-consistency including fractional parts
   via Corazza values as a frozen comparator).
6. **Totals-line grammar (E007 successor #5, still untested):** the V3 suffix-block hits at LB (21/67 docs)
   suggest section-structured sums; an HMM/regular-grammar over line-category strings with numeral anchors
   remains the untried estimator for the T slot on LB.
