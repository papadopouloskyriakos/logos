# PARAMETER SPACES — F12 (searched axes per method, for best-of-search null accounting)

The adaptive null (§13) must reproduce selection over EVERY axis below. Sizes are pre-registered so significance is
deflated for the full grid actually searched, not a post-hoc subset.

## PS-097 — Error-correcting-code / belief propagation
- bp_variant ∈ {sum_product, max_product, loopy_damped}  (+ optional {survey, expectation})
- damping ∈ {0.0, 0.3, 0.5, 0.7}
- factor_sets ∈ {sign+form, +formula_slot, +morphology, +ledger_totals, +anchors, +damage}  (nested)
- prior ∈ {uniform, frequency}
- max_iters ∈ {50, 200}, convergence_tol ∈ {1e-4, 1e-6}
- mask_rate (Stage-2 recovery) ∈ {0.05, 0.10, 0.20}
- redundancy_level (Stage-1 synthetic) ∈ {high, medium, low, none}

## PS-098 — Potts / spin-glass
- n_states ∈ {relative_class_k5, phonetic_class_k?, +unknown}
- coupling_sets ∈ {substitution, +morphology, +formula, +admin, +anchors}  (nested)
- solver ∈ {simulated_annealing, parallel_tempering, bp_cavity}  (+ optional replica_exchange_mcmc)
- temperature_ladder (PT) ∈ {geometric_8, geometric_16}
- anneal_schedule ∈ {linear, exponential}
- anchor_field_strength ∈ {0, 0.1, 0.3, 1.0, 3.0}  (phase-transition sweep)
- wrong_anchor_fraction ∈ {0, 0.1, 0.3}  (robustness)
- n_restarts ∈ {20, 50}

## PS-099 — Causal source separation
- method ∈ {ica, nmf, irm}  (+ optional {multiview_lvm, dann, scm})
- n_components ∈ {5, 8, 12, 20}
- nuisance_set ∈ {site, genre, scribe, rendering, edition, frequency, damage, doc_series, chronology}
- intervention ∈ {loso, logo, lo_renderer, lo_edition, freq_balance, damage_balance}
- nmf_beta ∈ {frobenius, kl}, ica_fun ∈ {logcosh, exp}

## PS-100 — Topological data analysis
- distance ∈ {sign_context, substitution, morphology, formula_slot, cross_site, morphogenesis_field, confound_adjusted}
- filtration ∈ {Rips, kNN_graph}, max_homology_dim ∈ {0, 1}
- k (kNN) ∈ {5, 8, 12}, metric ∈ {euclidean, cosine, correlation}
- null ∈ {degree_rewiring, metric_perm, random_embedding, freq_matched, site_shuffle, genre_shuffle}
- barcode summary ∈ {total_persistence, bottleneck_to_null, wasserstein_to_null}

## PS-101 — Global network-flow assignment
- solver ∈ {min_cost_flow, hungarian_bipartite, optimal_transport_sinkhorn}
- cost ∈ {relative_class_dist, formula_dist, morphology_dist, confound_adjusted, persistent}
- constraint ∈ {one_to_one, many_to_one}
- ot_entropy_reg ∈ {0.01, 0.1, 1.0}
- target_mode ∈ {known_target (Stage A only), target_free_equivalence (Stage B / LA)}
- baseline ∈ {local_nn, greedy, random, bayesian_fg, mdl_beam, anchor_lattice}

## PS-102 — Cross-method synthesis
- independence_threshold (min independent channels) = 2  (fixed, not searched)
- stability_inventories ∈ {>=2 sign inventories}, stability_segmentations ∈ {>=2 variants}
- absolute_value_gate = {>=2 channels ∧ loo_anchor ∧ loo_method ∧ held_out_form_prediction ∧ full_adaptive_null}  (fixed)

**Total best-of-search multiplicity per epoch = product of the axes actually run** — recorded in SEARCH_RECEIPT.md
and used to deflate the reported significance (Deflated-Sharpe / effective-n, Art. VIII).
