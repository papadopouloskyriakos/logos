# Search-receipt specification

Every run (real or null) emits one machine-readable receipt. **No adaptive choice may exist outside a
receipt** — this is how the end-to-end null stays honest. Written by `src/nulls/nulllib.emit_receipt`.

```json
{
  "experiment_id": "str",
  "dataset_manifest_hash": "sha256 of the frozen slot manifest + anchor set",
  "code_commit": "git short sha",
  "null_family": "real | synthetic_toponyms | shuffled_anchor_ids | ...",
  "seed": 20260706,
  "candidate_set": "tierB | tierB+C | ...",
  "mapping_budget": 300,
  "segmentation_budget": 1,
  "model_family": "frozen_correspondence | mapping_search | ...",
  "hyperparameters": {"tol": 1, "flex": 3},
  "restart_count": 1,
  "selected_result": {"matched": 0, "mapping_id": "..."},
  "heldout_score": 0.0,
  "wall_time_s": 0.0,
  "host": "str",
  "ts": "iso8601"
}
```

Receipts are appended to `results/<experiment_id>/receipts.jsonl`. The confirmatory verdict is
computed **mechanically** from the receipts (observed vs the null-family distribution), never from
prose. A run that fails to write a receipt is treated as invalid.
