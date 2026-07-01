"""logos comparison / discipline layer (design §A.2/B/C.3 + refinement F.2).

Modules:
  lfake.py     — L_fake fabricated-language canary generator (Nair 2026 calibration technique).
  nulls.py     — the deflation null generators (Packard 1974 banded permutation;
                 random-lexeme; Nair within-inscription fixed-seed permutation).
  lexstat.py   — minimal S_lex: deflated lexeme recall (the Gordon failure-mode metric; §A.2, the
                 pragmatic PRIMARY per F.1).
  phonostat.py — S_phono: held-out phonotactic plausibility under an L-phonotactic n-gram model
                 (§A.2, the WEAK surface statistic; reported beneath S_lex).
  morphostat.py — S_morph: deflated recurring-morphology score, the STRONG/Kober test with the F.1
                 no-power escape (§A.2 — gold-standard WHEN the corpus can power it).
  morphology.py — Direction A: unsupervised Linear A morphology / segmentation induction. Ensemble
                 segmenters (Morfessor + a Goldwater DP unigram) externally validated by leave-one-
                 site-out word-boundary recovery vs the scribe's divisions, plus the FROZEN
                 pre-registered Davis/Thomas/Duhoux affix panel scored against the within-word
                 permutation null + §B.3 multiplicity bar, falsified on sign-shuffle + L_fake floors.
                 STRUCTURAL only — NO phonetic-value claim. (docs/prereg-morphology-2026-06-30.md.)
  metrology.py — Direction D: constraint-optimization over the Linear A ACCOUNTING tablets (HT, LM I).
                 Parses tablets into balance units (line items + KU-RO total, per-commodity sub-totals),
                 treats each fraction SIGN as an unknown rational, and SOLVES the values that balance the
                 most accounts (RANSAC over exact rational solves). HONEST HEADLINE = HELD-OUT balance
                 (leave-a-fold-of-documents-out) vs a fraction-sign->value PERMUTATION NULL — the
                 overfitting guard. Solved values are COMPARED to the cited Corazza et al. 2021 system,
                 not assumed. NUMERICAL/METROLOGICAL only — NO phonetic-value claim.
  searchlog.py — N_eff instrumentation: COUNT the distinct candidates scored, don't estimate them
                 (§B.2; the instrumented trial count fed to the §B.3 deflated bar).
  litindex.py  — literature index + L_known/L_not_indexed partition + not_indexed_support (§C.1/§C.2; the
                 decontamination / generalization machinery feeding the §E gate).
  run_canary.py — the canary self-validation (real cognates clear the bar; L_fake does not).

The verdict pipeline (scripts/verdict.py) integrates these ADDITIVELY: deflated S_lex stays the
pragmatic primary and the L_fake corrected-margin bar stays the headline falsifier (F.1); S_phono /
S_morph are reported diagnostics, searchlog supplies the §B.2 N_eff for the §B.3 order-stat bar, and
litindex.not_indexed_support feeds the §E generalizes-to-L_not_indexed clause. The LLM is NOWHERE on that path.

Everything here is pure numpy/scipy/sklearn/stdlib and deterministic (seeded). L_fake is never
ground truth — it is an empirical false-positive floor (a Gordon/Di Mino-style match must clear
it or it is spurious).

HONESTY BOUND on real content (do NOT re-assert "zero real lexical content" — it is false):
L_fake forms are INVENTED at the whole-form level — under full ETCBC/bhsa rejection, whole-form
collision with a real Hebrew lexeme is ~0 — BUT the F.2 root-template calibration seats attested
Hebrew trilateral ROOTS into the forms, so ~75% of L_fake forms CONTAIN a real Hebrew trilateral
as a substring (by design — that is the root-structure calibration, not a leak). So L_fake is a
whole-form-invented, root-structured floor — conservative (a Hebrew-memorising model may score it
non-trivially, raising the floor in the safe direction) — NOT a "no real lexical content" one.
"""
