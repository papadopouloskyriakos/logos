# LICENSE & REPRODUCIBILITY (§IV)

| Source | License | Acquisition (deterministic) | Redistribution | Layer |
|---|---|---|---|---|
| **DĀMOS** (LB corpus) | academic / courtesy-gated (Univ. Oslo; see `docs/damos-courtesy-email-DRAFT.md`) | `corpus/bronze/linearb/damos/items.jsonl` (already in repo, main worktree) | **gitignored** — do not redistribute raw; commit only derived structure + hashes | transliteration/lemma = EVAL_ONLY; structure = MODEL_VISIBLE |
| **SigLA** (LA signs/docs) | CC BY-NC-SA | `corpus/bronze/sigla_browse_2026/database.js` → `scripts/sigla_decode.py` (OCaml Marshal decode) | derived JSON **gitignored** (NC-SA); decoder + counts committed | LA structural dry-run only |
| **logos silver LA** | open (this repo) | `corpus/silver/*.json` | committed | LA structural dry-run only |
| **LiBER** | TBD (web) | web — status `TO_AUDIT` | TBD | LB layout sensitivity |
| **PA-I-TO** | TBD (web) | web — status `TO_AUDIT` | TBD | LB imaging sensitivity |
| standard LB lexica (gold labels) | mixed (print/academic) | cite by reference; store only label + citation | **EVAL_ONLY**, never redistributed | role/schema ground truth |

## Reproducibility contract

- **Deterministic builders only.** Every corpus artifact is produced by a committed script from a hashed
  input; no hand-edited data. Manifests under `data/manifests/*.sha256`.
- **Counts are generated, not hand-written** (inherited logos invariant).
- **Two-layer physical separation** (`data/model_visible/` vs `data/evaluation_only/`) with I/O receipts
  (`results/io_receipts/`) proving no eval-only read reached model code (§VII).
- **Licensed raw data gitignored**; only code, derived structure, counts, hashes, and reports are committed.
- Rerun instructions live in each stage's report + `DECISION_LOG.md`.

## Blockers / open items

- LiBER + PA-I-TO licensing/acquisition `TO_AUDIT` — **not blocking**: both are LB-only sensitivity
  enrichments, excluded from the transfer-critical primary set.
- DĀMOS courtesy status: raw corpus stays gitignored; derived *structure* (opaque sign-IDs + metadata) is
  the working layer — confirm this satisfies the courtesy terms before any public artifact.

**Verdict:** no licensing/reproducibility blocker for the primary programme. `status` stays `INCOMPLETE`
(programme in progress), not blocked.
