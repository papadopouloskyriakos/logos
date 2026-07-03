# Phase 2 report — freeze, external timestamp, and the second one-shot

**Date:** 2026-07-03. **Gate verdict (mechanical, from the persisted artifact): `REFUTE`** —
the full statistic missed the corrected two-attempt bar by 0.0002 (p_raw 0.0255 vs 0.02532),
and would have been `REFUTE_LOTO_FRAGILE` even at the unadjusted bar (both pin-carrying LOTO
variants fail at p ≈ 0.21). Nothing under `paper/` read or written; all commits pushed.

## Chronology (promise before result, second time)

| step | evidence |
|---|---|
| Selection rule pre-committed | `fcb0c34` (provenance-only; matcher-fix disclosure in SELECTED_ANCHORS.md) |
| Set drawn content-blind | `64d51b4` — all 5 S&M Table 6.4 toponyms + ku-ta, ku-ni-su, sa-ra₂ (Younger, archived); 17 covered signs, legs ≤ 2 |
| Conjunctive certification | CERTIFIED at k=8, corrected bar: LOTO-survival 0.82 at s=3, machinery valid, k-trail {8} (`P2_CERTIFICATION.md`) |
| **Freeze** | `0aeaee8`, SHA-256 `1fce8401…eb71`; corrected two-attempt bar adopted, veto offered and not exercised |
| **External timestamp** | **DOI 10.5281/zenodo.21173639**, 2026-07-03T16:48:50Z (byte-exact, MD5-verified; recorded at `dc6d919`) |
| One-shot | after the timestamp; artifact `results/p2_oneshot_gate.json`, SHA-256 `4e813682…b492`, 1.3 s |

**Execution disclosure:** the first invocation crashed on a rank-lookup interface bug AFTER
computing but BEFORE any statistic was printed or persisted (same class as Phase 1); a
two-line fix to the reporting path (no analysis logic) and the deterministic re-execution is
the recorded run. The freeze-guard held: the seeded draw reproduced the prereg's materialized
held-out list exactly.

## Results (held-out DI JA KI MA ME NE O PO PU PU2 QE RA RI SU TA2 TE TI TO U WA; 2 pins)

| scoring | top-1 | p_raw | clears bar (0.02532) |
|---|---|---|---|
| **full** | 0.1000 (2/20) | **0.0255** | **NO** (by 0.0002) |
| LOTO −pa-i-to | 0.0500 | 0.2149 | no |
| LOTO −ku-ni-su | 0.0500 | 0.2074 | no |
| LOTO (other six anchors) | 0.1000 | 0.0255 | no |
| secondary-drop (3 Younger pins off) | 0.0500 | 0.2074 | no |
| toponym-off floor | **0.0000** | 1.0000 | no |

- Clause (i) fails → **REFUTE** (honest null; clause (iii) complete: SearchLog n_eff 2001,
  n_trials = 1, nulls non-degenerate, banned modules none, grep-clean only BANNED-constant /
  numpy `.shape` matches).
- Hits: **SU** (via ku-ni-su), **TO** (via pa-i-to) — both one-anchor-deep, both "fresh"
  (non-Phase-1-overlap) signs; overlap row: previously-held-out 0/10, fresh 2/10. Best NN rank
  of a true value: 11 (QE) — the distributional channel again contributed **zero** hits (fourth
  independent confirmation of the co-occurrence null). Cypriot block (descriptive): 0.0909,
  p 0.146, 1 pin (SA via tu-ru-sa).

## Honest read

The frozen draw realized **2 pins against a certified mean of ~3.0**: the mask swallowed
di-ki-te whole and three-quarters of su-ki-ri-ta — the collision risk the harness prices in,
landing unluckily this once. More fundamentally: certification promised LOTO-survival 0.82 at
planted strength s=3; **the real corpus supplies s ≈ 0 distributional signal** (floor exactly
0.0000), where certified survival was 0.45. The world delivered the null branch of a
power-bounded design — which is precisely what the §G.ii abstract pre-wrote: *the LA↔LB value
convention's non-shape support remains bounded by the place-name identifications themselves —
now shown insufficient even at quota-certified anchor supply, at current corpus scale.* Two
externally timestamped attempts now bracket the claim: Phase 1 (five anchors, raw bar) →
REFUTE_LOTO_FRAGILE; Phase 2 (eight vetted anchors, corrected bar, certified design) → REFUTE
by a hair's breadth, with every recovery still one-identification-deep. The identifiability
bound tightens; both attempts are reported in full, per the prereg.

What would actually move this: not more anchors of the same kind (the census is nearly
exhausted at the strict tier), but a larger LA corpus (new excavated tablets bearing the
anchor words in fresh contexts) or an independent non-toponym channel — both outside what any
protocol redesign can conjure. That statement, with two DOIs behind it, is the arc's product.

## Confirmations

Real held-out labels read exactly once, by the frozen configuration, after the DOI existed;
no threshold, set, or clause modified post-freeze; selection was provenance-only; the Phase-1
labels stayed spent; nothing under `paper/` touched; all commits pushed.
