# GRAPH SCHEMAS (blinded — nodes are opaque sign IDs)

- **G_POSITION** — nodes: signs; edge weight = PPMI of adjacent (left→right) co-occurrence over sequences (symmetrized).
  Encodes distributional context; the classic substrate for distributional class induction.
- **G_SUBSTITUTION** — edge weight = similarity of (left-context, right-context) neighbor distributions (cosine of
  context vectors). Signs that alternate in the same slots connect. Encodes paradigmatic substitutability.
- **G_FORMULA** — edge weight = shared document/slot co-membership (co-occurrence within the same inscription,
  document-frequency-normalized). Approximates administrative/formula-slot sharing without gold formula labels.
- **G_MULTILAYER** — convex combination (row-normalized sum) of the three, plus optional genre/site layers where
  metadata exists. Kept both separate and combined.

All graphs: symmetric, nonnegative, self-loops removed, largest connected component retained (component count logged
for condition 4). Laplacian: symmetric normalized `L = I − D^{-1/2} W D^{-1/2}`.
