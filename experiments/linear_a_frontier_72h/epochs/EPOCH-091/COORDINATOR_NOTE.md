# EPOCH-091 — Coordinator note: the positive control caught a real detector bug BEFORE banking

## What happened
The FIRST run of the Turing pipeline returned **TURING_NO_POWER**: the planted-Turing positive control recovered
the planted blocks in only **1/5** runs (mean ARI 0.083), even though the Turing instability conditions verified
true. Per the substantive-epoch discipline, a positive control that does not fire means the DETECTOR is broken —
you may not read anything into the real-data arm until the PC fires. So this was a **pre-banking methodology fix**,
not a result revision.

## Root cause (diagnosed mechanically)
`find_Du` originally selected the diffusion scale that **maximized the number of unstable modes**. On a graph, the
Turing unstable band is a contiguous interval [λ₋,λ₊] in the Laplacian spectrum; maximizing the band width places
the instability at **high** frequency (short-wavelength noise). But community / class structure lives in the
**low** (long-wavelength) modes — for the k=3 block PC, the two block-separating eigenvectors are the lowest two
nonzero modes (λ≈0.16, 0.19), sitting below a spectral gap (next mode λ≈0.63). The band-maximizing selection
destabilized modes 3…89 and **skipped** the two modes that carry the blocks, so the emergent pattern encoded no
block structure (pattern–vs–Fiedler-eigenvector corr ≈ 0.01). Direct check: clustering on the low eigenvectors
`U[:,1:3]` gives ARI = 1.0 — the structure is present; the selection rule was pointing the instability at the
wrong wavelength.

## Fix (frozen selection rule, unsupervised — no truth labels)
`find_Du` now **minimizes the smallest nonzero unstable eigenvalue** (destabilize the coarsest / community-scale
structure), tie-broken to the **narrowest band**. The clustering feature is the nonlinear activator field u(∞)
plus the **lowest 4** unstable eigenmodes. This rule uses only the graph spectrum, never the truth labels, so it
introduces no leakage into model selection. After the fix the PC fires **5/5, mean ARI 0.587** (verified on a fresh
seed set). The ring-graph self-test (`rd.py __main__`) independently confirms Schnakenberg + Gierer–Meinhardt form
genuine diffusion-driven patterns.

## Why this does not contaminate the NULL verdict
The fix was made to satisfy the **positive control** (recover planted structure), which is truth-blind on the real
LB graphs, and the real-data selection is the SAME unsupervised rule applied identically to the model and every
negative control. The mechanism comparison that drives the verdict — Turing (unequal diffusion) vs equal-diffusion
vs degree-rewiring — is unchanged by how the low modes are chosen, because all arms use the identical rule. The
NULL rests on a calibration-independent fact: **equal-diffusion (Turing mechanism OFF) recovers role structure as
well as the full Turing model (0.779 ≥ 0.765) on the same view**, and `|corr(pattern, degree)|` is 0.5–0.7 across
views (condition 4 largely fails on real LB) — recovery tracks generic graph structure and node degree, not a
diffusion-driven instability. This is the third time the PC discipline has changed an outcome pre-banking in this
campaign (cf. E080 conditional null, E090 anti-conservative bootstrap) — here it turned a false NO_POWER into a
correctly-powered NULL.

## Verdict
**TURING_LINEAR_B_RECOVERY_NULL** — mechanically valid model, PC fires 5/5, but on blinded LB the Turing mechanism
adds nothing over equal-diffusion / degree-preserving nulls. Consistent with the EPOCH-016 SBI prior. L2, opaque
IDs, no licence earned. Successor E092 (Turing-vs-generic-baseline specificity) is now strongly pre-informed toward
GENERIC_GRAPH_CLUSTERING but is still run as the formal specificity gate.
