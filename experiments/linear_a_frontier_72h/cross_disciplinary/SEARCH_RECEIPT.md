# SEARCH RECEIPT — F12 (Art. VII, complete-search accounting)

Append one block per epoch at run time. Records EVERY adaptive choice so the adaptive null (§13) can reproduce the
full selection process and charge best-of-search multiplicity. Nothing tried may be omitted (silent search =
undisclosed multiplicity = the "English is Semitic" failure mode).

## Fields per epoch
```
epoch:
methods_tried:            [full list, incl. discarded]
representations_tried:    [graph views / embeddings / distances]
factor_or_coupling_sets:  [which constraints included/excluded]
anchors_tried:            [anchor sets + dependency-cloned variants]
parameter_grids:          [see PARAMETER_SPACES.md ids]
thresholds_swept:
solvers_and_restarts:
initializations:
baselines_run:            [the simpler comparators]
selection_rule:           [how the reported config was chosen — MUST be truth-blind]
best_of_search_charged:   [n_method x n_repr x n_param x ... used to deflate significance]
null_draws:               [cheap>=1000 / moderate>=300 / full>=100]
```

## E097 — (pending; append when ACTIVE)
## E098 — (pending)
## E099 — (pending)
## E100 — (pending)
## E101 — (pending)
## E102 — (pending)

**Rule:** if a config is selected using truth labels, it is leakage — selection rules must be unsupervised or
cross-validated on held-out folds only (cf. the E091 unsupervised diffusion-scale selection). Any deviation is
recorded here and in the epoch's ledger `deviations`.
