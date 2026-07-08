# EPOCH-004 — FRACTION_ORDER_ANETAKI_SEAL: the third prospective Anetaki seal (fraction relative-value order)

**Frontier F10 · gate D · 2026-07-08 · seed 20260708 · Constitution v2.2 · claim layer L2/L3
(numeral-notation structure) · plan_hash `da6e0248…4ba4ef` · verdict `SEAL_FROZEN_PROSPECTIVE`**

## What was sealed, and why it is free test power

Kanta, Nakassis, Palaima & Perna 2024 (Ariadne Suppl. 5, pp. 41–42 — public, on disk, EPOCH-001-audited)
state that KN Zg 58 Face δ carries **six different fraction signs in sequence** whose implied relative
values differ from "those suggested until now" (their fn. 12 cites Corazza et al. 2021). The identities
and order are **unpublished** until *Anetaki II* (INSTAP). Before that publication we committed, under an
immutable sha256 manifest:

1. **Our own, Corazza-independent, corpus-derived pairwise ordering** of the LA klasmatograms;
2. the **Corazza et al. 2021 ordering** (verified against a secondary source reproducing the paper's
   table; identical to `scripts/comparison/metrology.py::CORAZZA_2021`) as comparator;
3. an **exact mechanical scoring rule** (`fraction_order_seal.py::score_sequence`), VOID conditions, and
   failure criteria.

## The derivation channel (new: nobody in the repo had used it)

`corpus/silver` holds **26 multi-glyph fraction tokens** (e.g. `𐝆𐝁` = J-then-B) — within-token sign
ORDER, invisible to the balance-solver metrology probe. Under the descending-value writing convention
(A-FD1), each cross-document repetition of a pair order is evidence for a relative value. 20 tokens sit in
the primary LM I horizon (HT/KH/ZA; Phaistos MM II quarantined to a secondary tier, per Corazza's own
system-drift restriction).

**Honesty core:** the single arithmetic-checkable sequence (ZA 8 writes E before J, but J=1/2 > E=1/4 by
Bennett/Schrijver arithmetic) **violates** the convention. The convention-reliability posterior is
therefore Beta(8,2)→Beta(8,3), mean **0.727** — every single-witness confidence in the seal is tempered by
the corpus's own counter-evidence. Nothing is claimed at editorial certainty.

**Frozen primary matrix — 25 claims** (all other pairs ABSTAIN):

| tier | claims | q |
|---|---|---|
| arithmetic | J>E, JE>J, JE>E | 0.99 |
| 4-doc unanimous | **J>B** (HT129, KH5, KH6, KH17) | 0.957 |
| 2-doc unanimous | **K>L2** (KH11, KH75) | 0.857 |
| 1-doc | JE>B, J>K, J>H, J>A, E>B, E>L2, E>L4, E>L6, **H>K**, **A>B** | 0.727 |
| transitive | J>L2/L4/L6, JE>K/H/A/L2/L4/L6, H>L2 | 0.62–0.72 |

972 linear extensions tie at maximum likelihood; the committed content is the pairwise matrix, not one
total order. P(all 25 claims correct) = 0.0011 — recorded, so a later "the whole order was right" spin is
impossible.

**The sharp teeth — the pre-registered divergence registry vs Corazza 2021:**

- **H vs K:** ours **H>K** (HT 34) — Corazza has K=1/10 > H=1/16 (H author-flagged uncertain).
- **A vs B:** ours **A>B** (KH 86) — Corazza has B=1/5 > A=1/24 (A author-flagged uncertain).

Both divergences target exactly Corazza's self-flagged weakest values. If either pair appears among the
six face-δ signs, the seal discriminates the two systems on held-out data. Secondary tier (non-gating):
L>E (PH7b), F>K (PH1b), L>L2 (ZA11a).

## Controls (positive first) and calibration

- **PC-1** planted-value regeneration of the real token structure: **12/12 directions recovered**, q
  monotone in vote count; noisy(0.2) variant recovers 0.799 ≈ the injected rate. The pipeline measures
  what it claims to.
- **PC-2** scorer round-trip: synthetic descending face-δ → `OURS_SUPPORTED` (9/9, binom p .00195);
  reversed → `OURS_REFUTED` (0/9). The scorer can both confirm and kill us.
- **NC-1** within-token order shuffle (20,000 reps): real unanimity W=16, **p = 0.0442** — the
  cross-document order consistency is not direction-random writing.
- **NC-2** frequency adversary: **5 claims contradict glyph-frequency rank** (incl. both divergence-registry
  pairs) — the channel is not the refuted frequency artifact.
- **NC-3** relabeling equivariance: exact PASS.

## Contamination audit (Art. XII) — all PASS

C1: the public PDF prints **zero** fraction identities/glyphs for face δ (existence + novelty statement
only). C2: EPOCH-001 register row 35 = `unpublished_content`; fringe rows carry no fraction patterns.
C3: quarantined fringe (Rjabchikov) scanned **blind** (pattern counts only; never read). C4: derivation
opens only `corpus/silver`. C5: EPOCH-001's 14-route search receipt is the currency check; no new search
(no re-exposure). **Known leak discounted:** the editors' public "differs from Corazza" statement earns
zero scoring credit; only the frozen pair directions score.

## Scoring (when *Anetaki II* publishes)

Ground truth = editors' printed relative-value order (G1), else written order under A-FD1 (G2). Sub-test 1
(headline): our claimed pairs among the six signs — `OURS_SUPPORTED` iff n≥4 ∧ acc≥0.75; `OURS_REFUTED`
iff n≥4 ∧ acc≤0.5; n<4 → `NO_POWER` (est. probability 0.3–0.4, non-binding). Sub-tests 2–3 (Holm family
of 2): head-to-head vs Corazza tier-1 on shared pairs; divergence-registry winners. V4: any session that
reads the ed.pr. face-δ content before a scoring-plan freeze caps the verdict at DESCRIPTIVE.

## Artifacts

`epochs/EPOCH-004/{prereg.md, plan_hash.txt, controls_pc.json, derivation.json, result.json}` ·
`data/seals/FRACTION_ORDER_ANETAKI_SEAL.json` (sha256 `45f34e87…2b3fa6`) + `.manifest.sha256` ·
`scripts/fraction_order_seal.py` (derivation + controls + frozen scorer, sha256 `7fa96ee5…444f22`).
Seal ordinal: **third** Anetaki-targeting seal; zero target overlap with `ANETAKI_FINAL_EDITION_DELTA_SEAL`
(sign-groups) and `M_ANETAKI_LATTICE_DELTA_SEAL` (lattice deltas).

## Ranked successors

1. **S1 (F10):** extend the sequence-order channel to a full Kemeny/Bradley–Terry model over ALL horizons
   with per-site convention-reliability (HT vs KH vs ZA p_desc), sealed as an ERRATUM-safe v2 matrix
   BEFORE Anetaki II — more claims, sharper q's, same held-out target.
2. **S2 (F10):** repetition-count bounds (𐝂𐝂𐝂𐝂 ⇒ 4·D < 1; A-B-B ⇒ A+2B ≤ 1 candidates) as a second
   arithmetic tier — could anchor D and B against the ledger totals the metrology probe already parses.
3. **S3 (F8):** resolve the ZA 8 anomaly philologically (is E-before-J a numeral phrase or two juxtaposed
   quantities?) via GORILA facsimile line context; a single reclassification moves p_desc from 8/11 to
   9/10 and every k=1 confidence from 0.727 to 0.9.
4. **S4 (F3):** test the descending convention on Linear B metrogram/fraction strings (readable analogue):
   earns/refutes A-FD1 as a STRUCTURAL transfer premise with real ground truth.
5. **S5 (F10):** freeze a fourth prospective micro-seal on the face-δ *count* structure (vases+units then
   fractions = ledger-item template from L2 doc-structure work) — independent of sign identities.
6. **S6 (F1):** site-stratified fraction usage (Schrijver: H at HT/PH vs K at KH) as an admin-dialect
   probe — our own divergence pairs (H>K from HT 34, K-heavy KH) may reflect site systems, not one global
   order; quantify before Anetaki II to pre-empt the confound.

**Compliance:** Art. V (L2/L3 stated); VII (inherited receipt, no new search); VIII (doc-level dedup);
IX (budget: ~15 direct bits committed, scoring n ≤ 15 pairs); XI (source graph in seal; comparator never
in derivation); XII (held-out untouched; leak discounted; controls before freeze); XV (no licence);
XVII (append-only); XVIII (A-FD1..A-FD6); XXII (this line). Counts script-generated (Invariant 12).
