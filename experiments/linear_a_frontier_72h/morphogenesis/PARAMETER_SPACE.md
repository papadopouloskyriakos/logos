# PARAMETER SPACE (searched axes — every axis is charged in the adaptive null)

- graph_view ∈ {POSITION, SUBSTITUTION, FORMULA, MULTILAYER}
- reaction_family ∈ {Schnakenberg, GiererMeinhardt, GrayScott}
- reaction params: Schnakenberg (a,b); GM (a,b,c); GS (F,k) — each on a small frozen grid in the Turing regime
- (Du, Dv): Dv/Du ratio ∈ {5,10,20,40}; Du fixed small; equal-diffusion Du=Dv is a NEGATIVE control, not a cell
- init: n_seeds ∈ {8} small random perturbations of (u*,v*)
- n_classes k ∈ {5, 8, 12} (frozen; matched across model + controls); primary = vowel(5), consonant(~13)
- threshold for pattern→class: KMeans on steady-state u (frozen); tie-broken by silhouette on the model only
- seed: fixed list; stability = mean pairwise ARI across seeds

Reported multiplicity M = |view|×|family|×|param grid|×|ratio|×|k| tried, deflating every significance.
