# Cretan-anchor preregistration — verification & mint record (2026-07-06)

Before minting, the built machinery + freeze were adversarially verified against the v2 prereg
(workflow `wf_80d0808d-b95`, 5 agents). Skeletonizer-identity and leakage lenses were clean (OK). The
decision-logic and mint-readiness lenses returned **1 BLOCKER + 5 MAJORs** — verdict `FIX_THEN_MINT`.
All fixed below; the plan_hash was then minted.

| # | Sev | Finding | Fix (committed) |
|---|-----|---------|-----------------|
| 1 | **BLOCKER** | `model.py` — the actual M2 scorer (`Correspondence.fit/score`, `_align` used by `B_egy`, refit in the null) — was not in the pinned inputs / plan_hash preimage. | Pinned `src/calibration/model.py` (`e76b2f23`) as the **operative M2** in the inputs table and the plan_hash preimage; added a fail-closed `assert_frozen_hashes()` that refuses to run unless every pinned artifact matches `plan_manifest.json`. |
| 2 | MAJOR | Config `3c56ed71` describes an L2/CV/14-feature model; `model.py` implements a bare add-α=0.5 aligner (spec≠impl). | Demoted the config to a **design reference**; `model.py` is the operative, hash-bound definition of M2 (stated in the prereg). |
| 3 | MAJOR | Null was a **bootstrap** (`rng.choice`, with replacement), not the §6 **permutation**. | Replaced with a true bijective shuffle of the `_sem` labels (multiset preserved); verified `Counter(sem)==Counter(perm)`. |
| 4 | MAJOR | §10 endpoint-clearability NO_POWER branch unimplemented → an underpowered null would be mislabeled REFUTE. | Added: `NO_POWER` if `P_null(r1≥2) ≥ 0.05` (or the pool-floor fails), evaluated before REFUTE. |
| 5 | MAJOR | Frozen targets file still carried the "l→r … the model learned" annotation §3 attested was struck. | Struck the clause; re-froze targets (`b749e2f7`). |
| 6 | MAJOR | §15.7 open: artifacts untracked; no-pilot attestation only template text. | This freeze commit tracks every pinned artifact; the executed no-pilot attestation is recorded in `plan_manifest.json`. |

**Hardening also applied:** primary anchors derived from pinned answer-blind primitives (Cretan ∧
non-palimpsest ∧ surviving ∧ ¬fraglich) with an assertion `== {Knossos, Amnisos, Lyktos}` (not the
hand-set label); pool pinned by whole-file sha (`ff83993c`) alongside the content hash (`26eb7627`);
verdict artifact now serialises the null `r1` histogram, `−log₂(p)` surprisal, per-anchor ranks under all
three scorers, and confusable counts; `model.recover_rank` annotated as the legacy calibration helper, not
the Cretan grader; the f()-space-vs-model-features distinction documented (`representation_note`).

## Minted

- **plan_hash:** `2eab1536cf70c20d0faebafff813b190b9cea573433698b2fdc2d83825cd130a`
- Pinned: `model.py e76b2f23 · skeleton.py feb7e8dc · cretan_test.py 3cc8a8b2 · corpus_holdout.py ed02090b ·
  build_pool.py 3cbb8709 · targets b749e2f7 · pool ff83993c · heldout-corpus 612ff9e9`.
- No-pilot attestation recorded; **the one-shot has not been run** (no verdict artifact exists).
- Reading-independence remains **scoped** (Falttafeln unavailable) — upgradeable later.

**To run (separate, later):** `python3 src/calibration/cretan_test.py --run-oneshot` — once, fail-closed.
