# 00 — Prior-test census: what has and has not already been tested on the Di Mino `*301=/na/` claim

**Branch:** `research/di-mino-301-exact-audit` · **Parent:** `main@6fd4f20` · **Constitution:** v2.2 ·
**Date:** 2026-07-08. Repository-wide search performed for: `Di Mino`, `DiMino`, `*301`, `AB301`,
`A-TA-I-*301-WA-JA`, `nawaya`, `N-W-Y`, `dwell`, `invocation verb`, `West Semitic`, `408`, `40 signs`,
`five Linear B signs` (66 matching tracked files).

## Census by category

| category | status | evidence |
|---|---|---|
| `QUALITATIVE_LITERATURE_AUDIT` | **EXISTS** | `docs/linear-a-claims-2026.md` (three-part takedown + quarantine receipt); the submitted paper's §4 worked-example (`docs/preprint/…-ANON.md` ll.89–99); `scripts/comparison/litindex.py CITATION_DIMINO` (indexed for decontamination). This is a literature-and-primary-source argument, **explicitly flagged in the paper as NOT a mechanical logos verdict**. |
| `MORPHOLOGY_PROBE_CONTAINING_i-*301` | **PARTIAL / ADJACENT** | Direction-A morphology probes + `prereg-morphology-salgarella-addendum-2026-06-30.md` tested LA morphology generally (NO-POWER null + segmentation positive), and the qualitative audit uses Davis's "inflected at both ends" morphology — but **no gate keyed to the exact `*301` claim / its held-out formula prediction**. |
| `BROAD_WEST_SEMITIC_LANGUAGE_TEST` | **PARTIAL / ADJACENT** | `scripts/family_scores.py` + the CSA sufficiency sweep (`results/csa/`) exercised cross-script family scoring at LA scale; `scripts/comparison/lfake.py` + `run_canary.py` validate the L_fake canary on the Ugaritic↔Hebrew surrogate — but **the exact Di Mino lexicon / West-Semitic equations were never scored against the L_fake floor**. |
| `EXACT_CORE_CLAIM_GATE` (H1–H6) | **DOES NOT EXIST — the gap this campaign fills** | No verdict row, search receipt, or preregistration keyed to `A-TA-I-*301-WA-JA` / `*301=/na/` was found. The submitted paper states it verbatim: the graduation gate + L_fake canary "have not been *run on this claim* … the priority of the planned revision." |
| `FULL_40_SIGN_MAP_GATE` (H7/H8) | **DOES NOT EXIST** | No 40-sign table in-repo; the artifact is publicly withheld → expected `SOURCE_BLOCKED`. |
| `FULL_408_LEXICON_GATE` (H9) | **DOES NOT EXIST** | No 408-entry lexicon in-repo; publicly withheld → expected `SOURCE_BLOCKED`. |
| `LINEAR_B_CORRECTION_GATE` (H10) | **DOES NOT EXIST** | No list of the 5 proposed LB corrections in-repo; withheld → expected `SOURCE_BLOCKED`. |
| `LOGOGRAM_CORRECTION_GATE` (H11) | **DOES NOT EXIST** | No logogram-correction table in-repo; withheld → expected `SOURCE_BLOCKED`. |

## Consequence for this campaign
- **Do NOT duplicate** the qualitative audit — reproduce/cite it, then run the missing mechanical gate.
- **The core mechanical gate (H1–H6) is genuinely unrun** and is this campaign's deliverable: score `*301=/na/`
  + the West-Semitic `N-W-Y` equation through the pre-registered, multiplicity-deflated, decontaminated, held-out
  pipeline (`comparison-layer.md` §A–C: `S_morph`/`S_lex`/`S_phono` vs Packard-permutation + L_fake null, deflated
  by `E[max_Neff]`, gate `DSR≥0.95 AND k≤U_floor`).
- **The extended claims (H7–H12) are expected `SOURCE_BLOCKED`** (artifacts withheld) — to be confirmed by the
  public-claim archive (§IV), and NOT collapsed into the core verdict.

## Machinery confirmed present & working (parent 6fd4f20)
`scripts/comparison/{lfake,lexstat,litindex,l_not_indexed,phonostat,morphostat,nulls,run_canary}.py`,
`scripts/family_scores.py`, `scripts/gate_null_calibration.py`, `scripts/verdict.py`,
`docs/design/comparison-layer.md` (the scoring design). Test baseline after corpus symlink: **89 passed**
(the 9 pre-symlink failures were all a missing gitignored bronze file `uga-heb.gold.cog`, now resolved).
