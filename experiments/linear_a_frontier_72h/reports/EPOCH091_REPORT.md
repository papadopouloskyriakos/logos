# EPOCH-091 — Blinded Linear B Turing-morphogenesis calibration

**Frontier:** F11 TURING_MORPHOGENESIS (family E091–E096, IMMEDIATE priority) · **gate:** A · **layer:** L2
**plan_hash:** `a0a843961c89f3eed3714ed4413a715543ca5fc929a5e8776af98b1685ecc71e`
**Verdict:** **TURING_LINEAR_B_RECOVERY_NULL** · **LA touched:** no · **licence:** none earned

## Question
Does a graph reaction–diffusion (Turing) system on **blinded** Linear B sign co-occurrence graphs recover held-out
phonetic class structure (vowel / consonant / role) through a **mechanically-verified diffusion-driven
instability**, and does the Turing *mechanism* beat its own negative controls?

## Machinery (frozen, `epochs/EPOCH-091/{rd,graphs,evaluate,e091_calibration}.py`)
- Two-field activator–inhibitor on the symmetric-normalized graph Laplacian: `du/dt=f(u,v)−Du·L·u`,
  `dv/dt=g(u,v)−Dv·L·v`, Du<Dv. Families: **Schnakenberg**, **Gierer–Meinhardt** (both pass the strict Turing
  conditions). Gray–Scott is in the registry but has no valid Turing state on these substrates → honest
  `TURING_MODEL_INVALID` (not forced; ≥2 valid families satisfy the prereg).
- **Turing instability verified per run** (else discarded): (1) equilibrium exists; (2) ODE-stable (tr J<0, det J>0);
  (3) ∃ nonzero λ_k with max Re eig(J−λ_k·diag(Du,Dv))>0; (4) condition-4 diagnostic |corr(pattern,degree)| reported.
- **Unsupervised selection (no truth labels):** minimize the smallest nonzero unstable eigenvalue (coarsest
  structure), tie-broken to the narrowest band. Feature = nonlinear u(∞) (seeds 1–3) ∥ lowest-4 unstable eigenmodes.
- Four blinded graph views (opaque sign IDs, min_count=3): POSITION, SUBSTITUTION, FORMULA, MULTILAYER (n=88 each).

## Positive control — PASSED (5/5, mean ARI 0.587)
Planted-Turing block graph (k=3, p_in=0.45, p_out=0.03). The pipeline recovers planted blocks under the same
frozen unsupervised rule. **The PC initially failed (1/5)** and caught a real `find_Du` mode-selection bug
(band-width-maximization placed the instability at high frequency, skipping the community-scale low modes); fixed
pre-banking → 5/5. See `COORDINATOR_NOTE.md`. Third pre-banking PC catch of the campaign (E080, E090, E091).

## Result (blinded LB)
| view / reaction | role F1 | vowel F1 | cons F1 | |corr(pattern,degree)| |
|---|---|---|---|---|
| FORMULA / Gierer–Meinhardt | **0.765** | 0.276 | 0.148 | 0.63 |
| SUBSTITUTION / Schnakenberg | 0.526 | **0.453** | 0.156 | 0.19 |
| MULTILAYER / Schnakenberg | 0.426 | 0.421 | 0.138 | 0.56 |
| POSITION / Schnakenberg | 0.569 | 0.301 | 0.170 | 0.57 |

**Negative controls (MULTILAYER):** equal-diffusion (Turing OFF) role **0.779** · reaction-only 0.494 ·
degree-rewiring role p95 0.739 · label-permutation role p95 0.579 (p=0.930).

## Reading
- The Turing math is sound (conditions verified; PC fires 5/5) — but on blinded LB the **mechanism buys nothing**:
  best role recovery (0.765) is **matched/beaten by equal-diffusion (0.779)** on the same machinery, and by
  degree-preserving rewiring (0.739). Turning the diffusion-driven instability OFF does not hurt recovery.
- Vowel recovery is weak (best 0.453) and consonant ~chance (0.195, 8-class).
- **Condition 4 largely fails on real LB** (|corr(pattern,degree)| 0.5–0.7): the emergent pattern tracks node
  degree, not a morphogenetic class field.
- ⇒ whatever is recoverable is **generic graph structure**, not a Turing mechanism. Directly consistent with the
  EPOCH-016 SBI prior (raw-cosine spectral clustering ties/beats fancy methods on this corpus).

## Successors (5)
1. **E092 — Turing-specificity (queued next).** Formal specificity gate: recovery vs spectral clustering /
   Laplacian eigenmaps / SBM / community detection / GMM / linear-diffusion, best-of-search adjusted. Pre-informed
   toward `GENERIC_GRAPH_CLUSTERING` / `TURING_NOT_NEEDED` by this NULL, but run as the formal test.
2. **E093 — LB→LA degradation surface.** ≥100-cell factorial degrading LB toward LA conditions; locate the LA
   operating point vs the (already-null) Turing detection threshold — quantifies HOW far below, a distinct question.
3. **E094 — Sequence/segmentation morphogenesis.** RD over position/boundary graphs for word/formula boundaries in
   blinded LB vs DP/Bayesian/MDL/finite-state — a DIFFERENT graph + task, not pre-decided by the class-recovery NULL.
4. **E095 — Geographic/scribal morphogenesis.** RD over site/phase/scribe graphs; tests whether regional structure
   (a coarser, possibly-Turing-amenable signal) behaves differently from phonetic-class structure.
5. **E092b — condition-4-hardened variant.** Re-run E091 with degree-partialled features (regress the pattern on
   degree first) to confirm the NULL is not merely a degree artifact masking a weak genuine signal.

**E096 (frozen LA) is NOT reached** unless a downstream epoch produces a Turing-specific positive; E091 makes that
unlikely. Finalization remains BLOCKED (clock 2026-07-11T03:20Z, not epoch count).
