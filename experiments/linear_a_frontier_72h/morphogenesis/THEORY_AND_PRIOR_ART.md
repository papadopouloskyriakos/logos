# THEORY & PRIOR ART — Turing morphogenesis on linguistic graphs

## Mechanism (Turing 1952)
A stable homogeneous chemical equilibrium can be **destabilized by diffusion** when an activator diffuses slower than
its inhibitor: `du/dt=f(u,v)+Du∇²u`, `dv/dt=g(u,v)+Dv∇²v`. On a graph the Laplacian `L` replaces `−∇²`; modes are the
eigenvectors `φ_k` with eigenvalues `λ_k≥0`. Linearizing about `(u*,v*)`, mode `k` grows iff the 2×2 matrix
`M_k = J − diag(Du,Dv)·λ_k` has an eigenvalue with positive real part, where `J` is the reaction Jacobian. **Turing
regime** = `J` stable (mode `λ_0=0` decays) but some band of `λ_k>0` is unstable, and the unstable band requires
`Du≠Dv` (equal diffusion cannot produce it — a built-in negative control).

## The linguistic analogue (and its honest status)
Nodes = signs (or positions/sites); edges = co-occurrence / shared context / substitution / shared slot. The claim
under test: latent classes (vowel/consonant families, roles, formula regions) act like morphogen domains — locally
reinforcing, longer-range differentiating — so a Turing system settles into class-aligned patterns. This is **novel
and speculative**; it is *not* assumed. The load-bearing question (E092) is whether the diffusion-driven instability
buys anything a spectral/SBM baseline does not. Related prior art: Laplacian eigenmaps & spectral clustering (the
baselines), network-diffusion models of dialect/innovation spread (spatial linguistics), and this campaign's own
`EPOCH-016` finding that raw-cosine spectral clustering ties/beats SBI — a strong prior that "morphogenesis" may
reduce to spectral structure. We therefore gate hard on Turing-specificity before any Linear A claim.

## Guardrails
Turing conditions verified per run or `TURING_MODEL_INVALID`. Blinding: opaque sign IDs before graph construction.
Multiplicity charged over every searched axis. L2/L3 ceiling; forbidden outputs hard-gated.
