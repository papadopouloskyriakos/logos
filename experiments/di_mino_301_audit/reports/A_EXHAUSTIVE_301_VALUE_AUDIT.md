# A — Exhaustive `*301` value audit (Di Mino H1)

**Prereg** DI_MINO_EXACT_CLAIM_V1 (sha 8b098a4c) · **Constitution** v2.2 · **Seed** 20260708

Core H1 question: is `*301=/na/` *specifically* supported over the preregistered admissible value space on held-out data, surviving leave-target-out / leave-site-out / leave-form-out, after deflating for the logged search `N_eff`? The `*301` value is the ONLY parameter varied across candidates; standard transferred values for the other signs render benchmark strings only and never grade the structural channel.

## Candidate value space
- 65 CV syllabary candidates (13 onsets × 5 vowels, includes `/na/`) + 1 NULL/logogram. Subsumes every CV literature proposal.
- `*301` AB anchor = `'-'`: **no external phonetic anchor exists for ANY value, including `/na/`** (external-anchor channel = 0 for all candidates).

## PRIMARY held-out statistic — S_morph (recurring morphology)
- score = **0.2738**, deflated = 0.1148, z = 6.955, has_power = True, is_significant = True.
- **Value-invariance proof:** S_morph(`*301` literal) = 0.273810, S_morph(`*301`→relabelled) = 0.273810 → identical = **True**.
- **Consequence:** S_morph is invariant under relabelling *301 -> any value; the PRIMARY held-out statistic CANNOT discriminate /na/ from any alternative. /na/'s rank on S_morph is a full tie (undetermined).

## /na/ rank on the value-dependent channels (diagnostic; never sufficient alone)
| channel | rank of /na/ | # strictly better | # tied at rank | /na/ score | margin | norm |
|---|---|---|---|---|---|---|
| S_lex (full, Di-Mino segmentation) | 21 / 65 | 20 | 30 | 0.667 | 0.167 | 0.667 |
| S_lex (full, whole-word segmentation) | 21 / 65 | 20 | 15 | 0.429 | 0.143 | 0.500 |
| S_phono (full) | 1 / 65 | 0 | 1 | -2.002 | 0.095 | 1.000 |
| S_lex (LEAVE-TARGET-OUT) | 21 / 65 | 20 | 30 | 0.667 | 0.167 | 0.667 |
| S_phono (LEAVE-TARGET-OUT) | 1 / 65 | 0 | 1 | -1.990 | 0.090 | 1.000 |

- **Candidates scoring ≥ /na/ on S_lex (full):** 50 — `da, de, di, do, du, ka, ke, ki, ko, ku, ma, me, mi, mo, mu, na, ne, ni, no, nu, pa, pe, pi, po, pu, qa, qe, qi, qo, qu, ra, re, ri, ro, ru, ta, te, ti, to, tu, wa, we, wi, wo, wu, za, ze, zi, zo, zu`. /na/ is **not uniquely** best even on the lexical channel.

## A3 — Leave-target-out (remove A-TA-I-*301-WA-JA)
- /na/ S_lex rank = **21 / 65**, 20 strictly better, 30 tied. top-5 = [('ka', 0.8333333333333334), ('ke', 0.8333333333333334), ('ki', 0.8333333333333334), ('ko', 0.8333333333333334), ('ku', 0.8333333333333334)]

## A4 — Leave-site-out (S_lex rank of /na/: rank, #better, #tied)
- (unprovenanced): rank 21, better 20, tied 30
- Apodoulou: rank 6, better 5, tied 40
- Arkhalkhori: rank 21, better 20, tied 30
- Haghia Triada: rank 21, better 20, tied 30
- Iouktas: rank 21, better 20, tied 30
- Khania: rank 21, better 20, tied 30
- Knossos: rank 21, better 20, tied 30
- Palaikastro: rank 11, better 10, tied 40
- Psykhro: rank 26, better 25, tied 30
- Skoteino Cave: rank 21, better 20, tied 30
- Tiryns: rank 21, better 20, tied 30
- Tylissos: rank 21, better 20, tied 30
- Zakros: rank 21, better 20, tied 30

## A5 — Leave-form-out (S_lex rank of /na/)
- *301-NA: rank 21, better 20, tied 30
- *301-SI: rank 21, better 20, tied 30
- *301-U-RA: rank 21, better 20, tied 30
- *301-WA: rank 21, better 20, tied 30
- A-*301: rank 21, better 20, tied 30
- A-*301-KI-TA-A: rank 21, better 20, tied 30
- A-NA-TI-*301-WA-JA: rank 21, better 20, tied 30
- A-RE-NE-SI-DI-*301-PI-KE-PA-JA-TA-RI-SE-TE-RI-MU-A-JA-KU: rank 21, better 20, tied 30
- A-TA-I-*301-DE-KA: rank 21, better 20, tied 30
- A-TA-I-*301-WA-E: rank 11, better 10, tied 40
- A-TA-I-*301-WA-JA: rank 21, better 20, tied 30
- DA+*301: rank 21, better 20, tied 30
- DA-DU-*301: rank 21, better 20, tied 30
- E-*301: rank 21, better 20, tied 30
- JA-TA-I-*301-U-JA: rank 6, better 5, tied 40
- MI+*301: rank 21, better 20, tied 30
- NA-TU-*301-NE: rank 21, better 20, tied 30
- SA-*301-RI: rank 21, better 20, tied 30
- TA-NA-I-*301-TI: rank 26, better 25, tied 30
- TA-NA-I-*301-U-TI-NU: rank 21, better 20, tied 30
- TE-*301: rank 21, better 20, tied 30
- ZU-*301-SE-DE-*21F-*118: rank 21, better 20, tied 30

## Null & deflation
- /na/ S_lex = 0.6667; Packard-permutation null mean = 0.7517; **null percentile = 49.0** ; deflated = 0.0000.
- **N_eff (logged)** = 65 values × 4 segmentations = **260 cells** (× 1936 Ugaritic lexeme compares per root).
- Author's stated simulations ≈ **100,000**.
- E[max] null over logged cells = 0.8333 → /na/ clears = **False**; E[max] over author's ~10⁵ = 0.8333 → /na/ clears = **False**.

## Verdict inputs for H1 (mechanical, per frozen prereg)
- Primary S_morph ranks /na/ = **TIE** (value-invariant) → fails `rank(/na/)=1 with margin>next-best`.
- Even on the diagnostic S_lex, /na/ is tied with 49 other consonant values and its lexical lead collapses under leave-target-out.
- /na/ does not clear E[max] over the author's stated ~10⁵ search: False.
- **H1 status: /na/ is NOT specifically supported over the admissible value space.**
