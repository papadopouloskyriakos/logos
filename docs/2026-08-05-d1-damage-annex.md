# 2026-08-05 — D1 damage annex: word-attached damage restored as a silver sidecar

## Constitutional stage header (Art. XXII)

- **stage:** D1-ANNEX-01 (corpus hygiene; no claim)
- **articles_consulted:** XI, XII, XVII, XXII
- **articles_triggered:** XI (defect recorded against the lineara.xyz/Douros source lineage),
  XVII (append-only: silver byte-identical, annex is a supplement), XXII (this header)
- **required_gates:** none (no verdict issued; L0/L1 data-layer work only)
- **assumptions_checked:** none blocking (A03/A04/A09 not load-bearing here)
- **authorized_outputs:** `corpus/silver/damage_annex.json` (gitignored sidecar),
  script-generated counts, this doc
- **forbidden_outputs:** any silver rebuild; any verdict change; any claim above L1
- **claim_layer:** L0/L1

## What and why

Tsirkas D1 (confirmed on our lineage in `docs/2026-08-05-tsirkas-full-repo-audit.md` §2):
the bronze `transliteratedWords` layer — the only layer `scripts/corpus_io.py` and
`scripts/corpus_io_structured.py` ingest — has **word-attached** break/lacuna notation
stripped. The marker is `U+1076B` (an unassigned codepoint in the Unicode Linear A block,
used by the Douros encoding). It survives in the parallel Unicode `words` layer, which
aligns 1:1 positionally with `transliteratedWords` (1,719/1,720 bronze entries; every one
of the 1,341 silver docs aligns).

Consequence: silver cannot distinguish a complete word from a damaged fragment, and
**phantom types** (types attested *only* damaged) inflate every type-level denominator.

## What was built (Phase 1 of the 5-mechanism plan)

1. **Bronze rescue:** silver's input existed only at volatile `/tmp/lineara/`; copied to
   `corpus/bronze/lineara/inscriptions.json` (gitignored) and sha256-pinned in
   `corpus/bronze/MANIFEST.txt` (`66b94203bd343ed9`). `corpus_io*.py` now resolve
   env override → in-repo bronze → legacy `/tmp`.
2. **`scripts/audit_damage_markers.py`** (mirrors `audit_ab21_ab22.py`): aligns the two
   bronze layers, attributes per-word-token damage (leading/trailing/internal), emits the
   sidecar **`corpus/silver/damage_annex.json`** keyed by doc id, token order = silver
   stream word order, compact codes ⊆ `LTI`. Silver files untouched — byte-identity now
   enforced by pinned sha256s in `tests/test_damage_annex.py`.
3. **Tests** (`tests/test_damage_annex.py`, first real `licensed_data`-marked users):
   flag semantics (unit-safe), silver byte-identity guard, pinned regression numbers,
   determinism, marker-absence mechanism check, silver doc-set cross-check.

## Numbers (script-generated; `python3 scripts/audit_damage_markers.py`)

```
D1 damage annex (damage-annex-v1) — bronze sha256 66b94203bd343ed9
docs: 1341 (misaligned skipped: 0: [])
word tokens: 3147; damage-touching: 911 (28.9%)  flags L/T/I: {'L': 548, 'T': 527, 'I': 28}  combos: {'I': 20, 'L': 360, 'LI': 4, 'LT': 183, 'LTI': 1, 'T': 340, 'TI': 3}
types: 1165; ever-damaged: 492; PHANTOM (only-damaged): 359 (30.8%) -> 806 excluding phantoms
silver cross-check: MATCH
```

Same magnitude as Tsirkas's corpus (his 374/1,247 = 30.0%; different record model), as
independence predicts.

## Disposition

- This is a **supplement, not an erratum**: no published figure consumes type counts
  (frozen-paper exposure assessed in the full-audit doc §2). Silver is NOT rebuilt.
- Any future type-count-sensitive figure must cite the phantom-excluded denominator or
  justify not doing so (the annex makes both available mechanically).
- A future silver v2 with native damage fields remains an explicit owner decision.

## Phase 1b — sensitivity checks (appended when run)

Scope: (1) type-count/effective_n denominators with/without phantoms; (2) metrology null
re-run with damage-filtered numerals; (3) segmentation gap robustness with phantom-only
words flagged. Discipline: results are annexes; if anything *improves*, that is a new
preregistered run deflated for the D1-prompted look — verdicts never flip via annex.

## Close block (Art. XXII)

- **constitutional_compliance:** COMPLIANT — no silver rebuild, no verdict issued, counts
  script-generated, append-only record kept.
- **deviations:** none. **violations:** none. **waivers:** none.
