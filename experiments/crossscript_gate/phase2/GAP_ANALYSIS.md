# GAP_ANALYSIS — Phase 2 Steps 1+2: census supply vs the sweep quota

**Verdict: SUPPLY MEETS QUOTA — on both vetting tiers.** A Phase-2 freeze (future prompt, new
pre-registration, new external timestamp) is eligible. Machine artifact:
`results/gap_analysis.json`; census: `anchor_census.csv` (47 rows) + `CENSUS.md`.

## The two sides

- **Quota (Step 1, read off pre-committed SWEEP_SPEC `42618ac`):** 8 anchors, R=1 cap —
  LOTO-survival power 0.93 at s=3; at n=8 ALL swept redundancy regimes pass the band
  (R=1/2/3 → 0.93/0.86/0.93), so the operative existence question is "≥8 anchors within any
  swept regime".
- **Supply (Step 2, provenance-only census):** 47 rows → **38 quota-eligible** (classes 1–3,
  non-fringe, sm_trust ≠ debunked, primary/secondary-sourced, ≥2-sign forms, source-queried
  equations excluded). Excluded: 2 S&M-debunked (a-ka-ru, i-ja-te), 2 source-queried
  (a-tu-ṛị-si-ti; DA-U-*49), 1 single-sign form, 4 class-4 constraint rows (never pins,
  reported separately).

## Coverage accounting

- Union coverage (classes 1–3, non-debunked): 41 sign tokens, of which **36 are eligible
  (pinnable) anchors** — 73% of the 49-sign eligible pool.
- Legs per sign: natural redundancy is plentiful — A(7), SA(7), RU(7), DA(6), I(6), KI(6),
  KU(6), TA(6), NA(5), RE(5)…; 14 signs exceed 3 legs in the RAW pool (harmless: the quota
  needs a fielded subset, not the whole pool at once).
- **Existence certificates (deterministic seed-0 randomized greedy — existence proofs, NOT
  anchor selection; the actual Phase-2 anchor set is chosen by pre-registered provenance rules
  at the freeze):**
  - Lenient tier (38 anchors): sign-disjoint **R=1 subset of 9 ≥ 8** ✓.
  - **Strict tier** (31 anchors after also excluding every hedge-marked row — Younger's
    "perhaps"/"=?" rows, the i-da-a cf. row): **R=1 subset of 9 ≥ 8** ✓ (composition incl.
    pa-i-to, sa-ma-ro, qa-qa-ru, si-ki-ra, du-pu₂-re, da-mi-nu, a-su-ja, ku-ta, di-na-u).
  - R≤3 subset: 20 anchors.

## Supply by class / trust / status (quota-eligible tier)

toponym 13 / personal_name 23 / gloss_acrophonic 2 (= 38; the excluded single-sign form is the
`ni` gloss row); sm_trust: tempting 7, neutral 23, n/a (Younger-only) 8; source_status:
primary 30, secondary (archived Wayback Younger) 8 — exact splits in
`results/gap_analysis.json`. Salgarella 2020 remains the
standing acquisition item (homomorphy grades; independent A/B corroboration for name
equations) — it would UPGRADE rows, not unlock the verdict, which already stands on
S&M-primary material alone for 7 of the 9 strict-certificate anchors.

## Analysis-code disclosure (script fix trail)

`gap_analysis.py` went through three disclosed iterations BEFORE the verdict was accepted:
v1 had a plain bug (PENDING-DOMINATED fired on a negative deficit) and tested the legs cap on
the whole pool; v2 fixed both but demanded the strictest R=1 reading only; v3 grounds the
criterion in the sweep grid (all R regimes band-pass at n=8 → subset-within-any-swept-regime)
and adds the strict-tier robustness count. No iteration involved any statistical evaluation of
any anchor — the criterion changes were dictated by the prompt's verdict definitions and the
already-published grid, and the verdict is identical (MEETS) under v3's lenient AND strict
tiers, and even under the strictest R=1-only reading (9 ≥ 8).

## What this does NOT do

No anchor was evaluated for its effect on recovery; no recovery model ran; no real held-out
label was read. The census and the quota met only arithmetically (counts and sign coverage).
The Phase-2 freeze — anchor-set selection by pre-registered provenance rules, new prereg, new
external timestamp — is a FUTURE prompt.
