# Phase 0.5 report — S&M 2017 acquired, anchor table settled, power re-run: **GO**

**Date:** 2026-07-03. Follows the operator's option-(b) decision after the Phase-0 MARGINAL
escalation. Nothing under `paper/` read or written; **no recovery model built or run** — Phase 1
remains gated on the final frozen pre-registration.

## 1. Acquisition (deliverable 1)

Steele & Meißner 2017 chapter acquired from the authors' CREWS self-archive (offprint licence
permits posting after July 2020 — stated on the PDF's own licence page):
`corpus/bronze/steele_meissner_2017/chapter-6.pdf` (gitignored; 978,536 bytes; SHA-256
`a80810e419eae8492e63ed7971e9e65d9f78d3506770a750b9e467f126d34553`), PROVENANCE.md alongside,
registered in `docs/related/_acquisition.md` (commit `9d41d82`).

## 2. Anchor table settled FROM THE PDF (deliverable 2, commit `d81ac93`)

All fields verified against the chapter text itself (page-cited constants:
`steele_meissner_2017.py`), not against the instructing summary:

- **Cypriot-stable = true (11):** A, DA, I, NA, PA, PO, RO, SA, SE, TI, TO — Table 6.2 +
  §3, p. 98 ("Eleven signs can be identified with a high degree of certainty"). PO's
  Cypro-Minoan cell recorded **verbatim "Not attested?"**; DA = *ta*, RO = *lo* in the Cypriot
  Syllabary noted per the chapter.
- **SI = candidate:** §3 p. 98, "si, for example, is a good contender" — candidate, not member.
- All other rows `not_listed` (not a sourced claim of instability). The eleven are all robust
  anchors, so a **fixed Cypriot-stable held-out axis of 11** now exists.
- **`sm2017_tier` column (25 rows):** the chapter's cumulative confirmation grids — Table 6.2
  (p. 98), Table 6.5 place-names (p. 102, adds DI KI RI SU TA TE TU + si?), Table 6.6 internal
  variation (p. 104, adds MA ME MI + mu?), Table 6.11 ideographic/acrophonic (p. 108, adds NI
  RU; "confirm some other entries (ma, ki, na)", p. 107).
- **Toponym seed (`toponym_anchors.csv`), Table 6.4 p. 102:** five non-queried LA↔LB
  equations — pa-i-ṭọ (HT 97a.3+), se-to-i-ja (PR Za 1.b), tu-ru-sa (KO Za 1), di-ki-te
  (PK Za 11), su-ki-ri-ta (PH Wa 32) — plus the queried a-tu-ṛị-si-ti variant, recorded and
  flagged (the chapter's own '?', §5 p. 103), excluded from the constraint channel.
  **14 robust anchors covered:** DI I JA KI PA RI RU SA SE SU TA TE TO TU.
- **Internal-variation series (§5 p. 103)** recorded as the confidence channel: m-series
  (ma/me/mi; mu? via the cow-ideogram argument p. 104), t-series (whole series, "crucially"
  p. 102), u/w (both attestation pairs '?'-marked; fn 19 semi-vowel caveat), s-series (both
  '?'-marked).
- **Homomorphy grades: still `pending_primary` (59/59)** — Salgarella 2020 remains unacquired
  and the S&M chapter supplies no homomorphy grading scheme. Nothing substituted.

## 3. Power re-run at the finalized design (Addendum B, commit `33a3fec` BEFORE the run)

Design finalized per operator: **h = 20** (earned by the Phase-0 sensitivity finding) + the
**toponym-constraint channel** (LB-lexicon word completion over the five sourced forms; a
held-out sign is pinned iff all its co-signs in a form are unmasked; **identification
reliability = 1 — a disclosed optimistic bound**). Thresholds **verbatim unchanged** from
`00fb9ea`. Two pre-declared configurations, identical paired seeds (master 20260703); 18.9 s
CPU; artifact `results/power_precheck_phase05.json`.

| s | (a) machinery power / top-1 | (b) design power / top-1 (mean pins of 20) |
|---|---|---|
| 0 | 0.04 / 0.010 | 0.62 / 0.098 (1.8) |
| 0.5 | 0.08 / 0.017 | 0.74 / 0.108 (1.8) |
| 1 | 0.04 / 0.021 | **0.80** / 0.116 (1.9) |
| 2 | 0.18 / 0.030 | 0.68 / 0.119 (1.8) |
| 3 | 0.50 / 0.081 | **0.92** / 0.159 (1.7) |
| 5 | 0.98 / 0.356 | 1.00 / 0.423 (2.0) |
| 8 | 1.00 / 0.827 | 1.00 / 0.847 (2.0) |
| 13 | 1.00 / 0.997 | 1.00 / 0.998 (2.0) |

- **Validity (on config (a), per Addendum B):** s=0 false-fire 0.04 ≤ 0.14 ✓; s=13 power
  1.00 ≥ 0.90 ✓. Config (a) reproduces the Phase-0 h=20 sensitivity curve exactly (same
  seeds) — determinism confirmed.
- **VERDICT: GO** — config (b) meets the frozen GO band (power ≥ 0.80 at some s ≤ 3: 0.80 at
  s=1, 0.92 at s=3). The s=2 dip (0.68) is Monte-Carlo noise at n_rep=50 (binomial SE ≈ 0.07);
  the band is met regardless.
- **Honest attribution:** at s ≤ 1 the detection is carried almost entirely by the toponym
  channel (~1.8 pins/replicate lift top-1 to ~0.10 vs chance 0.014). **The GO is therefore
  conditional on the toponym-identification reliability assumption**; the final prereg MUST
  carry a toponym-reliability robustness clause (e.g. leave-one-toponym-out, or a reliability
  discount) — pre-flagged here so it cannot be quietly dropped.

## 4. What Phase 1 now requires (gate unchanged)

Phase 1 (gate design + **final frozen prereg**) is eligible per the GO. Before any recovery
model runs: freeze the final feature set (contract §1), the held-out axis (random h=20 vs the
fixed Cypriot-stable 11 vs both), the toponym-reliability clause, conflicted-sign exclusions,
grading clauses, SearchLog wiring, and the grep-clean enforcement test. Salgarella 2020
homomorphy grades remain the one open acquisition.

## Confirmations

- Nothing under `paper/` read or written; no recovery model built or run.
- No image/shape feature anywhere (runtime banned-module check: clean).
- Thresholds untouched since `00fb9ea` (Addendum B is design-only, committed pre-run at
  `33a3fec`; both hashes recorded in the results file).
- Cypriot-stable membership, toponym equations, and series evidence taken from the acquired
  primary at page level; homomorphy grades NOT substituted (pending Salgarella 2020).
- All commits pushed.
