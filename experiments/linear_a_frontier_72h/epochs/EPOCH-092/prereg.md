# EPOCH-092 — frozen prereg slice (Turing-specificity vs generic graph clustering)

**Family:** TURING_MORPHOGENESIS (E091–E096) · **priority:** IMMEDIATE · **layer:** L2 · **gate:** A
**Parent prereg:** `morphogenesis/PREREGISTRATION.md` (E092 slice frozen for the plan_hash).

## Question (frozen)
Is graph reaction–diffusion (Turing) morphogenesis EVER specifically needed on blinded Linear B — i.e. does it
beat a panel of generic graph-clustering baselines on held-out class recovery (role / vowel / consonant),
best-of-view (view multiplicity charged equally to every method)?

## Methods (frozen)
**Turing** (E091 frozen pipeline). **Generic baselines** (the panel): spectral clustering (sklearn, precomputed
affinity — the EPOCH-016 null-of-record), Laplacian-eigenmap + k-means, Laplacian-eigenmap + GMM, Louvain
community (networkx), linear-diffusion (heat-kernel exp(−tL) embedding). **Mechanism ablations:** equal-diffusion
RD, reaction-only. Same blinded graphs (opaque IDs, 4 views), same frozen k per truth key (role=2, vowel=5,
consonant=8) for every method.

## Fairness gate (positive control)
Planted-Turing block graph (k=3, p_in=0.45, p_out=0.03), 5 seeds. **Every** method in the panel — Turing AND each
generic baseline — must recover the planted blocks (ARI>0.25, ≥3/5), else that baseline is a strawman and is
excluded; if no generic baseline is fair, the specificity test is NO_POWER.

## Verdicts (mechanical)
- **TURING_SPECIFIC_SUPPORTED** — Turing beats the best fair generic baseline on every tested channel (incl. vowel)
  by >0.02 macro-F1.
- **GENERIC_GRAPH_CLUSTERING (TURING_NOT_NEEDED)** — a generic baseline matches or beats Turing.
- **TURING_SPECIFIC_NULL** — nothing (Turing or generic) exceeds the permutation null.
- **NO_POWER** — Turing PC fails, or no fair generic baseline.

## Prior of record
EPOCH-016 (SBI: raw-cosine spectral clustering ties/beats fancy methods) + EPOCH-091 (equal-diffusion ties full
Turing). `GENERIC_GRAPH_CLUSTERING` is the pre-registered expected outcome; a Turing-specific positive would be the
surprise. L2 only; no licence earned; LA not touched.
