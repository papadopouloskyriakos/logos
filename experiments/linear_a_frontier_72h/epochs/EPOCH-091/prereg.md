# EPOCH-091 — frozen prereg slice (Turing morphogenesis, blinded LB calibration)

**Family:** TURING_MORPHOGENESIS (E091–E096) · **priority:** IMMEDIATE · **layer ceiling:** L2 · **gate:** A
**Parent prereg:** `morphogenesis/PREREGISTRATION.md` (this is the E091 slice frozen for the plan_hash).

## Question (frozen)
Does a graph reaction–diffusion (Turing) system on **blinded** Linear B sign co-occurrence graphs recover
held-out phonetic class structure (vowel / consonant / role), with the diffusion-driven Turing instability
**mechanically verified**, and does the Turing *mechanism* beat its own negative controls (equal-diffusion,
reaction-only, degree-preserving rewiring, label permutation)?

## Model family (frozen)
Two-field activator–inhibitor on the symmetric-normalized graph Laplacian L (eigenvalues in [0,2]):
`du/dt = f(u,v) − Du·L·u`, `dv/dt = g(u,v) − Dv·L·v`, Du<Dv. Reaction families: **Schnakenberg**,
**Gierer–Meinhardt** (both satisfy the strict activator–inhibitor Turing conditions; Gray–Scott is in the
registry but does NOT meet cond2/cond3 on these substrates and is reported TURING_MODEL_INVALID where it fails).

## Turing verification (frozen, per run, else the run is discarded)
1. homogeneous equilibrium (u*,v*)>0 with f=g=0;  2. ODE-stable: trace(J)<0 AND det(J)>0;
3. diffusion-driven instability: ∃ nonzero Laplacian eigenvalue λ_k with max Re eig(J−λ_k·diag(Du,Dv))>0, Du<Dv;
4. condition-4 diagnostic: |corr(pattern, degree)| reported; single connected component enforced.

## Frozen UNSUPERVISED selection rule (no truth labels)
Over ratios Dv/Du ∈ {10,20,40} and a Du grid, choose the config that **minimizes the smallest nonzero unstable
eigenvalue** (destabilize the coarsest / community-scale structure), tie-broken to the **narrowest band** (fewest
unstable modes). Clustering feature = the nonlinear steady-state activator field u(∞) (seeds 1,2,3, averaged) ∥
the **lowest 4** unstable eigenmodes. k per truth key frozen: role=2, vowel=5, consonant=8 — identical for model
and every control.

## Graph views (blinded, opaque sign IDs; min_count=3)
G_POSITION (adjacent L→R PPMI), G_SUBSTITUTION (cosine of L∥R context), G_FORMULA (shared-document df-normalized
co-membership), G_MULTILAYER (row-normalized sum).

## Positive control
Planted-Turing synthetic block graph (k=3, p_in=0.45, p_out=0.03), 5 seeds: pipeline must recover the planted
blocks (ARI>0.25 ⇒ recovered; require ≥3/5).

## Negative controls
equal-diffusion (Du=Dv), reaction-only (no Laplacian coupling), degree-preserving rewiring (20 rewires, role-F1
distribution), label permutation (200 draws, p-value + p95) — on the MULTILAYER view.

## Verdicts (mechanical)
TURING_MODEL_INVALID (no view×reaction satisfies the conditions) · TURING_NO_POWER (PC recovers <3/5) ·
TURING_LINEAR_B_RECOVERY_SUPPORTED (role beats perm-p95 [p<.05], rewire-p95, equal-diffusion+0.02, AND vowel beats
its perm null) · _PARTIAL (≥2/3 role gates) · _NULL (does not separate from the negative controls).

## Prior of record
EPOCH-016 (SBI): generic clustering ties/beats fancy methods on this corpus. A _NULL / GENERIC outcome is a live,
valid, expected result — not a failure. Turing-vs-baseline specificity is E092, not this epoch.

## Forbidden (Constitution Art. V / XV; brief §11)
No absolute sound values, no translations, no language-family ID, no "pattern = phoneme" from internal
morphogenesis patterns alone. L2 only; no transfer licence is earned by this epoch.
