# EPOCH-093 — LB→LA degradation surface (data-scale threshold)

**Frontier:** F11 TURING_MORPHOGENESIS · **gate:** A · **layer:** L2
**plan_hash:** `7114e97fb49b2ac21d2e459f428232e5cb82a2c48c35dd2e5ba27ebcb7e5bd8e`
**Verdict:** **LINEAR_A_ABOVE_THRESHOLD** (data-sufficiency; QUALIFICATION) · **LA touched:** structural stat only · **licence:** none

## Question
E092 settled Turing is not needed. The campaign question: does ANY graph method recover phonetic-class structure at
**Linear A's data scale**, and is DATA VOLUME the binding constraint? LA vs LB differ mainly in volume (LA ~4,245
tokens vs LB ~43,868; vocab 85 vs 89, near-equal). Degrade LB by token budget; place LA on the surface.

## Design
- **Method:** generic-best from E092 (Laplacian-eigenmap k-means), best-of-{SUBSTITUTION, MULTILAYER}. Not Turing.
- **108-cell factorial:** token_budget {2000,4000,6000,10000,20000,43868} × min_count {2,3,5} × seed {0–5}.
- **Frequency-artifact guard (mandatory):** a meaningful detection must beat the **permutation floor** AND a
  **frequency-only** baseline (+0.03); degree-only checked too. (position→C/V and reduced-seed were refuted as
  frequency artifacts — the guard is required.)

## Surface (min_count=3)
| tokens | vowel F1 | vowel freq-only | vowel detected | role F1 | role detected |
|---|---|---|---|---|---|
| 2000 | 0.460 | 0.331 | 1.00 | 0.499 | 0.00 |
| **4000 (≈LA)** | **0.440** | **0.311** | **1.00** | 0.539 | 0.00 |
| 6000 | 0.436 | 0.285 | 1.00 | 0.545 | 0.00 |
| 10000 | 0.435 | 0.297 | 1.00 | 0.509 | 0.00 |
| 20000 | 0.416 | 0.310 | 1.00 | 0.519 | 0.00 |
| 43868 | 0.490 | 0.361 | 1.00 | 0.636 | 0.00 |

LA operating point: 4,245 tokens, vocab 85 → nearest cell 4,000.

## Reading
- The blinded-LB **vowel-class signal beats frequency-only by a stable +0.13 margin at every budget** including
  LA's ~4,000-token scale (detected in 100% of subsamples), and also beats degree-only — so it is **neither a
  frequency nor a degree artifact**. The surface is **flat**: 10× more data barely moves it.
- ⇒ **LA's data volume is not the binding constraint** for this weak phonetic-class signal. It is detectable at
  LA scale already.
- **Crucial scope:** the signal is WEAK (vowel macro-F1 ~0.44, ceiling ~0.49) and this is **blinded LINEAR B**.
  The verdict licenses **no** LA sound values, vowel readings, or transfer (L2). It **refines** the
  underdetermination story: the binding constraint is the **intrinsic weakness of the co-occurrence signal + the
  absence of a licensed LB→LA phonetic transfer**, NOT corpus size.
- The trivial role/degree channel is itself frequency-confounded (role never beats frequency-only → detected 0%) —
  a sanity asymmetry confirming the guard rejects the confounded channel and passes the genuine one.

## Process note
A single-seed SUBSTITUTION-only probe initially over-claimed (vowel ≈ frequency at full budget on that one
view/seed). Hardening to best-of-view × 6 seeds × the frequency guard produced the stable +0.13 margin. Same
frequency-artifact discipline that refuted position→C/V.

## Successors (5)
1. **E094 — segmentation morphogenesis (queued next).** Distinct graph + task (boundary recovery) vs
   DP/Bayesian/MDL; does the data-sufficiency picture hold for a sequence-structure channel?
2. **E095 — geographic/scribal morphogenesis.** Regional structure at LA scale, provenance/frequency-guarded.
3. **E093b — cross-view stability of the vowel margin.** Is the +0.13 margin carried by one view (MULTILAYER) or
   robust across all four? Bounds how load-bearing the single positive channel is.
4. **§12 map integration.** Fold the F11 arc (E091 mechanism-null, E092 specificity-null, E093 data-sufficiency
   qualification) into the exhaustion map; qualification bucket 4→5, bounded-neg 20→22.
5. **transfer re-statement.** Cross-reference E093 with the prior no-transfer results: data-sufficient +
   transfer-blocked ⇒ the underdetermination is not resolvable by more corpus.

Finalization remains BLOCKED (clock 2026-07-11T03:20Z, not epoch count).
