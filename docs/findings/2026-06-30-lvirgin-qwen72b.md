# Finding 2026-06-30 — L_virgin test on qwen2.5:72b: qwen ABSTAINS on untouched signs (3rd confound caught)

Ran the §C.2 L_virgin generalization test (`scripts/comparison/lvirgin.py`, verifier: SOUND) — the clean
memorization-vs-reasoning probe — on `qwen2.5:72b` (vast.ai H100, 40 seeds; 20 known AB + 11 virgin
`*`-series syllabograms probed in real context every seed; ~$1.02, instance destroyed). Partition was
litindex-quarantine-safe (Di Mino's `*301` excluded from the virgin set).

## The headline excess-gap is COVERAGE-CONFOUNDED — not reported as the result

| class | n_signs | mean proposals/sign (n) | mean modal-share | mean **excess-over-random** |
|---|---|---|---|---|
| L_known (AB) | 20 | **20.15** | 0.909 | **+0.588** |
| L_virgin (`*`-series) | 11 | **1.18** | 0.909 | **−0.013** (≈ random) |

The full-headline known−virgin excess gap = **0.601, permutation p = 0.0005** — but this is **confounded by
coverage**: virgin signs got ~1 proposal each, so their excess-over-random is forced toward 0 (an n=1 sign
has modal-share 1.0 == its random expectation == excess 0), dragging the virgin mean down and inflating the
gap. The pre-registered **matched-n robustness check confirms the confound: `no_power=True` — 0 of the 11
virgin signs reached n≥10**, so the rigorous coverage-controlled consistency comparison **cannot be made.**
The harness flagged this rather than letting the spurious p=0.0005 stand — the **third** confound the
discipline has caught (after the forced-1.0 and the baseline-ceiling artifacts).

## The clean, honest finding: qwen ABSTAINS on the untouched signs

The interpretable signal is the **coverage asymmetry itself**, not the consistency gap. Shown a sign in real
context every seed, qwen assigns a phonetic value to the **known AB signs in ~20/40 seeds** but to the
**virgin `*`-series signs in only ~1/40 seeds** — i.e. it **declines to impute the untouched signs ~97% of
the time**, while confidently valuing the memorizable ones.

**Interpretation (honest, bounded):** this is consistent with **regurgitation-/memorization-dominated**
behaviour — qwen proposes values where it has likely seen them and largely **abstains** where no published
value exists. It does NOT demonstrate *random* imputation on virgin signs (the cleaner "reasoning collapses
to chance" cut the design hoped for) — qwen mostly **opts out** rather than guessing, so the consistency
comparison had no power to run. And per the module's standing rule: **consistency ≠ verified correctness** —
there is no ground truth on virgin signs, so this can never show qwen is *right* about one, only how it
behaves. Together with the per-word contamination table (qwen reproduces web-prevalent published readings),
the picture is coherent: **the model leans on memorized published values and does not confidently generalize
to the untouched signs.**

## Design limitation + decision

The abstention left too few virgin proposals to power the rigorous consistency test. A re-run *forcing* a
value on every virgin sign would measure forced-imputation (likely eliciting noise), a different question —
and would spend more GPU, which the strategic scope freeze rules out (L_virgin was the last GPU run). The
abstention behaviour is itself the honest, interpretable signal; recorded as-is.

## Provenance
`qwen2.5:72b` (Ollama q4) on vast.ai H100 SXM 80 GB (ephemeral). Raw result
`runtime/ablation/lvirgin-qwen72b.json` (gitignored). Harness `39cd122`; partition quarantine `39cd122`.
Total vast.ai spend across the C.4 arc + L_virgin ≈ **$2.80**.
