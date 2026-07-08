# TASK M — Held-Out + Prospective Seal Results

**Campaign:** research/linear-a-anchor-lattice · **Seed:** 20260708 · **Constitution:** v2.2 ·
**As of:** 2026-07-08 · **Script:** `scripts/m_seal_audit.py` · **Artifacts:** `data/seals/M_*.json`.

## Verdict

**`NO_CANDIDATE_TO_SEAL` (phonetic) + `NO_UNCONTAMINATED_HELD_OUT_SCORING_AVAILABLE_NOW`
(structural) + 1 new prospective seal registered on genuinely uninspected evidence.**

No held-out partition was opened or scored in this task. That is the *result*, not an
omission: scoring anything now would violate Art. IX/XII, as shown below.

## 1. Phonetic seal scoring — NO_CANDIDATE_TO_SEAL (mechanical)

From `M_candidate_check.json` (all values read from H artifacts):

| Check | Value | Bar |
|---|---|---|
| S0 (licensed, ρ=0) signs with >0.1 bit absolute reduction | **0 / 163** | >0 needed |
| S0 A-only mean reduction | 6.6e-06 bits (MC noise) | — |
| Real A-only reduction vs 200 random-anchor nulls | 0.000 bits, **below all nulls** (p=0.000) | — |
| MDL, art12-discounted | ΔDL = **+231.5 bits → UNANCHORED wins** | anchored must win |
| Continuity pins × LA substitution (hard-hard) | **UNSAT, 15/24 violated** | SAT |
| Transfer licence | `all_LA_transfer = NOT_EARNED` | PHONETIC earned |

There is no value assignment — not even a privileged equivalence-class representative
(≥10^270 classes) — that could be committed as a falsifiable phonetic prediction. A phonetic
seal would be theater.

## 2. Structural predictions × held-out partitions — the scoreability matrix

The lattice produced three NEW structural findings. From `M_scoreability_audit.json`:

| Lattice finding | SEAL_2 (15%) | SEAL_3 (Khania) | SEAL_4 (libation) | SEAL_5 (numerals) | Anetaki delta |
|---|---|---|---|---|---|
| UNSAT continuity×substitution (15/24) | NOT_SCOREABLE | NOT_SCOREABLE | NOT_SCOREABLE | NOT_SCOREABLE | conditional prospective (MP3) |
| A-only darkness (68/69; below-null topology) | NOT_SCOREABLE | NOT_SCOREABLE | NOT_SCOREABLE | NOT_SCOREABLE | **prospective (MP1+MP2)** |
| Substitution channel at chance (9/28=0.321, p=0.252) | NOT_SCOREABLE | NOT_SCOREABLE | NOT_SCOREABLE | NOT_SCOREABLE | conditional prospective (MP3) |

Why NOT_SCOREABLE on the corpus partitions — two independent blockers, either one fatal:

1. **Derivation contamination (Art. IX/XII).** The F4 substitution neighborhoods and the
   A-only sign classification were computed on the **full 1,341-inscription corpus** —
   including the SEAL_2 15%, Khania, the libation carriers, and every numeral. Scoring
   those partitions would grade a target by the data that created the prediction.
2. **The partitions are already opened.** All four are `SEALED_AND_SCORED` (morphology
   campaign, 2026-07-07). An opened partition cannot be re-consecrated as held-out.

Additionally, category mismatch for two of the three findings: UNSAT and A-only darkness
are properties of the **published-anchor topology × channel semantics**, not per-inscription
text statements — corpus text partitions contain no anchor topology to hold out.

## 3. What IS cleanly scoreable — the prospective route (registered)

KN Zg 57/58 (`in_current_corpus = false`, transliteration unpublished, re-verified
2026-07-08) is the only evidence untouched by the lattice derivation. Registered as
**M_ANETAKI_LATTICE_DELTA_SEAL**, plan_hash
`f4b9bae8027c3247f3c6f5bd23acfac165ce71b4b8dd38daa0cd6f2d6b4f52e6`, 3 hypotheses
(MP1 A-only token fraction, expected [1,11] of ~119; MP2 zero new independent anchors /
A-only dark stays 68/69; MP3 conditional substitution non-rescue). Details in
`M_SEAL_REGISTER.md`. Status: `SEALED_PROSPECTIVE_NOT_YET_SCORED` — scored mechanically
when the editio princeps appears; a MP2 failure (a real new anchor) must be recorded as
FAIL even though it would be the best possible news for the field.

## 4. Interpretation discipline

- Nothing here upgrades any claim: the campaign stays at **L2** with all transfer licences
  NOT_EARNED; SEMANTIC+ NOT_AUTHORIZED.
- The absence of a scoreable held-out test is itself evidence-hygiene output: it certifies
  that the lattice campaign generated **no prediction it could quietly self-confirm** on
  already-seen data.
- No do-not-repeat item was rerun; no existing seal was modified (append-only, Art. XVII).

**Compliance line (Art. XXII):** Art. V (layer-capped wording), VII (search receipt: 3
registered hypotheses, multiplicity in the seal), IX (leakage audit performed and enforced),
XI/XII (contamination blockers applied), XV (no licence change), XVII (append-only),
XVIII (assumptions recorded in the seal). All numbers script-printed (Invariant 12).
