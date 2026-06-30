"""logos comparison / discipline layer (design §A.2/B/C.3 + refinement F.2).

Modules:
  lfake.py     — L_fake fabricated-language canary generator (Nair 2026 calibration technique).
  nulls.py     — the deflation null generators (Packard 1974 banded permutation;
                 random-lexeme; Nair within-inscription fixed-seed permutation).
  lexstat.py   — minimal S_lex: deflated lexeme recall (the Gordon failure-mode metric).
  run_canary.py — the canary self-validation (real cognates clear the bar; L_fake does not).

Everything here is pure numpy/scipy/sklearn/stdlib and deterministic (seeded). L_fake contains
zero real lexical content and is never treated as ground truth — it is an empirical
false-positive floor (Gordon/Di Mino-style match must clear it or it is spurious).
"""
