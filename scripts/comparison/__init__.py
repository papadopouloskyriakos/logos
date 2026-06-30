"""logos comparison / discipline layer (design §A.2/B/C.3 + refinement F.2).

Modules:
  lfake.py     — L_fake fabricated-language canary generator (Nair 2026 calibration technique).
  nulls.py     — the deflation null generators (Packard 1974 banded permutation;
                 random-lexeme; Nair within-inscription fixed-seed permutation).
  lexstat.py   — minimal S_lex: deflated lexeme recall (the Gordon failure-mode metric).
  run_canary.py — the canary self-validation (real cognates clear the bar; L_fake does not).

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
