"""logos.decipher — the combinatorial / EM decipherment engine (the "CORE" lineage).

This package implements the unsupervised character-substitution decipherment loop that
predates the neural seq2seq methods:

  * Berg-Kirkpatrick & Klein (2011), "Unsupervised Transliteration Detection via
    Mixed-Effect EM" / and the broader B-K&K decipherment line (unsupervised alignment +
    EM over a substitution cipher with weighted edit distance).
  * Snyder, Barzilay, Knight (2010) and Ravi & Knight (2011) — the combinatorial
    Bayesian/EM decipherment family this engine is a clean numpy baseline of.
  * Luo, Cao & Barzilay (2019), "Neural Decipherment via Minimum-Cost Flow" (a.k.a.
    "NeuroCipher") — the *future* neural upgrade: it REPLACES the hard E-step alignment
    with a differentiable neural alignment and the M-step with a min-cost-flow (here
    approximated by ``scipy.optimize.linear_sum_assignment``, the bipartite min-cost
    matching = bipartite min-cost flow on a 1-1 policy). This package is the non-neural
    core that Neural Decipherment would warm-start / be compared against.

METHOD (coordinate ascent / EM over a substitution map phi: cipher-token -> plain-token):

  E-step  (align.best_align)      : given current phi, align each cipher word to its
                                    minimum weighted-edit-distance plain candidate, and
                                    collect the aligned (cipher_token, plain_token) cols.
  M-step  (maplearn.fit_map)      : from the aligned pairs build the cipher-x-plain
                                    co-occurrence count matrix, form a cost matrix
                                    (cost = -count), and solve the global 1-1 mapping with
                                    ``scipy.optimize.linear_sum_assignment``.
  Iterate (decipher.run_em)       : to convergence (phi stable) or max_iters.

CONSTRAINTS: pure numpy / scipy / stdlib. Fully deterministic (no RNG; every tie-break is
order-based). Tokens may be single characters (synthetic Latin cipher) OR multi-character
sign strings (Linear A syllabograms like ``KA``, ``RA2``) — the engine is token-sequence
based, so it works at both the letter and the sign level.

Public surface::

    from scripts.decipher import editdist, align, maplearn, eval, decipher, demo_fixture
"""

from . import editdist, align, maplearn, eval, demo_fixture, decipher  # noqa: F401

__all__ = ["editdist", "align", "maplearn", "eval", "demo_fixture", "decipher"]
