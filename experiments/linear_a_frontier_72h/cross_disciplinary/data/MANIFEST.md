# DATA MANIFEST — F12 cross_disciplinary

No licensed raw corpus is stored here. All inputs are loaded via repo scripts at run time; only manifests +
regenerable derived artifacts live under `data/`. Licensed vendor data (SigLA, DĀMOS, GORILA-derived) stays
gitignored per Constitution invariant #10.

## Canonical inputs (loaded at run time)
| input | loader | notes |
|---|---|---|
| Linear B sequences (DĀMOS) | `scripts.cross_script.data.load_b_damos()` | 13,562 seqs, 89-vocab, truth values eval-only |
| Linear A sequences | `scripts.cross_script.data.load_a()` | 539 packed inscriptions, 85-vocab, opaque (no values read) |
| anchor set | `scripts.cross_script.data.build_anchor_set()` | multi-slot external anchors (anchor-lattice K) |
| SigLA per-glyph bboxes | `data/sigla_glyphs_bbox.json` (gitignored) | via `scripts/sigla_decode.py`; spatial channel |
| sign classes | `data/sigla_sign_class.json` (gitignored) | role/class metadata |
| morphogenesis graph views | `morphogenesis/scripts/graphs.py` (`build_graphs`) | POSITION/SUBSTITUTION/FORMULA/MULTILAYER — imported as OPTIONAL ablatable channels |
| segmentation variants | (segmentation_extension / silver) | ≥2 variants required for stability tests |
| site/genre/scribe/edition metadata | silver corpus | nuisance sources for E099 |

## Derived artifacts (regenerable, may be committed via git add -f)
- synthetic planted scripts (Stage 1) — generated per epoch with a fixed seed passed in (not Date/Random).
- degradation cells — reuse the E093 token-budget harness.
- factor graphs / coupling matrices / filtrations — written under `results/<epoch>/`.

## Provenance discipline
Every candidate relation records its `corpus_version`, `sign_inventory`, and `segmentation_variant` in
DEPENDENCY_REGISTER.md so E102 can audit independence. Counts are script-generated (invariant #12), never hand-typed.
