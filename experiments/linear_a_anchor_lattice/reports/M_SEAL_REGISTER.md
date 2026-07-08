# TASK M — Seal Register (anchor-lattice campaign)

**Campaign:** research/linear-a-anchor-lattice · **Seed:** 20260708 · **Constitution:** v2.2 ·
**As of:** 2026-07-08 · **Script:** `scripts/m_seal_audit.py` (all numbers printed by the script,
Invariant 12). **Artifacts:** `data/seals/M_*.json` (4 files).

**Stage header (Art. XXII):** articles_triggered = V, VII, IX, XI, XII, XV, XVII, XVIII.
Gates consumed: H = JOINT_INFERENCE_NULL (3/3 solvers); G = LA_AT_IDENTIFIABILITY_ZERO;
D/E/F = NULL / SOURCE_BLOCKED / NO_POWER. Assumptions: published Anetaki sign count ≈119 (KN Zg 57);
sign-universe base rates from the merged inventory (full corpus — legitimate, target not in corpus).

## Register state

| Seal | Owner campaign | Type | Status | Usable by THIS campaign? |
|---|---|---|---|---|
| SEAL_2 (15% inscriptions) | relative-phonology-seals | held-out partition | SEALED_AND_SCORED (SUPPORTED) | NO — opened + derivation contamination |
| SEAL_3 (Khania site) | relative-phonology-seals | held-out site | SEALED_AND_SCORED (SUPPORTED) | NO — opened + derivation contamination |
| SEAL_4 (libation LOO) | relative-phonology-seals | held-out family | SEALED_AND_SCORED (SUPPORTED) | NO — opened + derivation contamination |
| SEAL_5 (masked numerals) | relative-phonology-seals | held-out masking | SEALED_AND_SCORED (UNDERPOWERED_NO_SIGNAL) | NO — opened; no lattice claim targets numerals |
| ANETAKI_FINAL_EDITION_DELTA_SEAL | relative-phonology-seals | prospective | SEALED_PROSPECTIVE, **still unopened** (re-verified 2026-07-08) | untouched — its P1–P3 belong to the morphology campaign |
| **M_ANETAKI_LATTICE_DELTA_SEAL** | **anchor-lattice (NEW, this task)** | prospective, structural-only | **SEALED_PROSPECTIVE** | scored when the editio princeps publishes |

## Phonetic scoring: NO_CANDIDATE_TO_SEAL

Mechanical rule (in `M_candidate_check.json`): a candidate value system exists iff some sign
gains >0.1 bit **absolute** reduction under the **licensed** scenario (S0, ρ_META=0) or a
PHONETIC+ licence is EARNED. Measured: S0 signs >0.1 bit = **0** (A-only mean reduction
6.6e-06 bits = MC noise); real A-only reduction 0.000 bits, **below all 200 random-anchor
nulls** (p_null≤real = 0.000); MDL art12-discounted ΔDL = **+231.5 bits for UNANCHORED**;
continuity×substitution **UNSAT 15/24**; licence state `all_LA_transfer = NOT_EARNED`.
→ **There is no value hypothesis to put behind any seal.** (Consistent with the H verdict
JOINT_INFERENCE_NULL and the ≥10^270 equivalence classes.)

## NEW seal registered: M_ANETAKI_LATTICE_DELTA_SEAL

`data/seals/M_ANETAKI_LATTICE_DELTA_SEAL.json` ·
**plan_hash `f4b9bae8027c3247f3c6f5bd23acfac165ce71b4b8dd38daa0cd6f2d6b4f52e6`** ·
targets ONLY the unpublished KN Zg 57/58 editio princeps transliteration (evidence never
inspected in this repo; `in_current_corpus=false`). Claim layer **L2**; 3 registered
hypotheses (multiplicity recorded in the seal):

- **MP1 — A-only token fraction.** Corpus base rate 281/5792 = **0.0485** (69 A-only types).
  On ~119 signs: expected 5.77 ± 2.34 → 95% interval **[1, 11]** A-only tokens (rescale
  binomially if published n differs). p = 0.80.
- **MP2 — anchor-delta darkness.** Re-running the lattice builder with the editio princeps
  as a new SOURCE adds **0** dependency-collapsed independent value-bearing anchors and **0**
  value-bearing edges touching A-only signs (dark stays 68/69). p = 0.90. A failure here
  (e.g. a bilingual) would be good news and must be recorded as the seal FAILING.
- **MP3 — conditional substitution non-rescue.** IF ≥5 new both-continuity-pinned variant
  pairs appear, their same-C-or-same-V rate remains at chance (0.251; current 9/28 = 0.321,
  p = 0.252). Prior(condition) = 0.15; p(claim | condition) = 0.85. <5 pairs → NOT_TESTABLE.

**Non-overlap with the existing Anetaki seal** (Art. XVII, no double-dipping): the morphology
seal predicts A-prefixation counts / ledger CARRIER-VALUE grammar / libation order; this seal
predicts sign-CLASS composition, anchor-topology delta, and substitution-channel non-rescue.
No shared scoring target; both use the same publication event as the reveal.

## Anetaki integrity re-verification (2026-07-08)

Web check (see `M_anetaki_integrity_check.json` for URLs): only the 2025 preliminary overview
— Kanta, Nakassis, Palaima & Perna, *Ariadne* 27–43, doi 10.26248/ariadne.vi.1841 — and press
coverage of it (GreekReporter 2026-03-30, La Brújula Verde, Biblical Archaeology Society,
languagehat). **No full edition / transliteration published.** Verdict:
**SEAL_STILL_UNOPENED_AND_UNCONTAMINATED** (both the existing morphology seal and the new one).

**Compliance line (Art. XXII):** no claim worded above L2; no licence changed
(SEMANTIC+ remains NOT_AUTHORIZED); append-only — no prior seal modified; all counts
script-generated; held-out partitions not re-opened.
