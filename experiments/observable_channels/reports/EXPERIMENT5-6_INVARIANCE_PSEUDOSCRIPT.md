# Experiments 5–6 — cross-site invariance + pseudo-script O2/D8 (STRUCTURAL gate legs)

## Constitutional stage header (Art. XXII)

- **articles_consulted:** V, XIII (remove the convenience), XV (STRUCTURAL licence), XVI.
- **articles_triggered:** XIII (site + sign identity removed), XV (this is the STRUCTURAL-licence gate).
- **claim_layer:** L2 (document structure). **highest_authorized_layer:** L2.
- **compliance:** COMPLIANT — pure L2; no LA model result (LA appears only as a corpus-density statistic).

## Experiment 5 — cross-site invariance (`results/cross_site_invariance.json`)

| direction | template | target-site baseline | beats? |
|---|---|---|---|
| train KN → test non-KN | 0.616 | 0.238 | yes |
| train non-KN → test KN | 0.389 | 0.289 | yes (+0.10) |

- entry-type distribution divergence KN vs non-KN: **TVD = 0.281**
- cross-site accuracy gap 0.227; **site-shuffle null p = 0.000** (the gap is real, not noise)
- **verdict: `SITE_DEPENDENT`.** The within-document template *regularity* transfers in both directions
  (documents are internally templated everywhere), **but** the notation-type inventory/mix is site-specific
  (TVD 0.28) and the predictability gap is significant. Partial transfer, not invariance.

## Experiment 6 — pseudo-script O2 + D8 (`results/pseudo_script_o2d8.json`)

- **O2 (sign-ID permutation):** template accuracy **0.497 → 0.497 (identical)**. The L2 signals never read
  sign identity, so O2 cannot touch them. **Honest flip side: a signal invariant to sign scrambling carries
  no sign-level (L1) or lexical (L3) information — it is pure positional/arithmetic document grammar.**
- **D8 (LA-like entry sparsity sweep):** template stays above baseline as documents are thinned
  (0.497/0.591/0.602/0.589 vs baseline 0.408→0.48) — **robust**. Accounting closure **decays to the null**
  (0.071→0.049→0.047→**0.033 vs 0.054 null** at 35% retention) — **fragile**.
- **LA density (corpus statistic only, not a model result):** LA ≈ LB (mean 2.73 vs 2.29 entries/doc; both
  28% with ≥3 entries), so D8 is mild and the L2 grammar would be *measurable* on LA at similar power — *if*
  a STRUCTURAL licence were ever earned.

## STRUCTURAL_TRANSFER_LICENSE — final disposition: `NOT_EARNED`

The one genuinely robust structural signal is template regularity (held-out, bidirectional, survives O2+D8).
But the charter's STRUCTURAL gate is **not cleared**:
1. **site-dependence** — the "no site dependence" condition fails (TVD 0.28, gap p=0.0 → `SITE_DEPENDENT`);
2. **second channel fragile** — accounting closure is sparse and decays to the null under D8;
3. **content-free** — the surviving signal is *sign-agnostic* positional grammar (O2-identical), i.e. it
   carries no sign/lexical/functional content. It is precisely the already-known L2 document structure
   (the paper's segmentation layer), not a transferable *reading* of anything.

So even the weakest transfer licence is not earned by this route. Combined with the L3 `REFUTED` verdict, the
Observable Administrative Channel Recovery programme is a **complete, well-powered negative** across both the
functional (L3) and structural-transfer (L2) gates.
