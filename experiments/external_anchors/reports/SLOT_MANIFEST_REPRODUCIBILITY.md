# Slot-manifest reproducibility — PASS

The gold slot manifest is licensed-derived (gitignored/local) but **deterministically regenerable**
from the checksum-pinned read-only corpus.

- **Regeneration command:** `PYTHONPATH= python3 experiments/external_anchors/src/slot_classifier/build_manifest.py`
- **Inputs (pinned):** `inscriptions_structured.json` (`aaee1aeb…`), `signs_ontology.json` (`246f63f1…`);
  drift ⇒ hard error at load. Classifier `slot-rules-v1-2026-07-06`, split seed `20260706`.
- **Expected gold hash:** `dc9653a91d7ba14dcb76238968c368e6369813583d25bf41c97ffb0a5d024551`
- **Regenerated hash (this pass):** `dc9653a91d7ba14dcb76238968c368e6369813583d25bf41c97ffb0a5d024551` — **MATCH ✓**
- Test: `tests/test_slot_manifest_reproducibility.py` (skips gracefully if the licensed corpus is absent).

Deterministic regeneration confirmed; the frozen internal slot layer is reproducible.
