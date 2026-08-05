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

## Phase 1b — sensitivity checks (script-generated: `python3 scripts/d1_sensitivity.py --write-doc`)

Stage D1-SENS-01 (annex to D1-ANNEX-01; no claim; L0/L1). Machine-readable result: `results/d1_sensitivity.json` (seed 0, annex `damage-annex-v1`, bronze `66b94203bd343ed9`). Verdict flips: NONE.

### (1) Denominators — with vs without phantom types

| quantity | published (with phantoms) | phantom-excluded | delta |
|---|---|---|---|
| distinct word types | 1165 | 806 | -359 |
| word tokens | 3147 | 2752 | -395 |
| docs with ≥1 word token | 1341 | 1256 | -85 |
| sites | 52 | 47 | -5 |
| effective_n (Art. VIII, dims doc+site) | 52 | 47 | -5 |

Under phantom exclusion the type denominator is 1165→806 (-359) and tokens 3147→2752 (-395), while the Art. VIII effective_n (dims doc+site) moves 52→47 — future type-count-sensitive stages must cite the phantom-excluded denominator (no published figure consumed type counts; all tokens are one L_LA_CORPUS lineage under Art. XI).

### (2) Metrology null — as published vs damage-filtered

Mapping: annex token order = silver stream word order; metrology label tokens asserted list-equal to annex `types` per tablet; unit excluded iff its KU-RO total line or any accumulated item line carries a damage-flagged word token; damage-stripped mirror asserted equal to metrology.parse_tablet output for every tablet. Caveat: the annex records WORD-attached damage only — numeral damage and lines without word labels cannot be flagged through it. Excluded: 16/35 balance units (2 fraction-bearing). As-published reproduction matches `runtime/metrology-real.json`: True.

| quantity | published | damage-filtered | delta |
|---|---|---|---|
| balance units | 35 | 19 | -16 |
| held-out fraction balance | 0.0 | 0.0 | 0.0 |
| null mean | 0.112857 | 0.146 | 0.033143 |
| p-value | 1.0 | 1.0 | 0.0 |
| separated | False | False | — |

The published metrology NULL under damage filtering: 16/35 balance units excluded (2 fraction-bearing), held-out fraction balance 0.0 vs null mean 0.146 (p=1.0) — word-token damage does not explain the null and no verdict moves.

### (3) Segmentation boundary-recovery gap — with vs without phantom-only words

Phantom-only word tokens dropped: 395 (annex count 395, agree: True); 85 inscriptions emptied. As-published reproduction matches `runtime/morphology-real.json`: True.

| quantity | published | phantom-filtered | delta |
|---|---|---|---|
| dp_unigram micro-F1 | 0.4361 | 0.4711 | 0.035 |
| random-baseline micro-F1 | 0.3888 | 0.405 | 0.0162 |
| gap (dp − random) | 0.0473 | 0.0661 | 0.0188 |

The boundary-recovery gap without phantom-only words: 0.4361 vs 0.3888 (gap +0.0473) as published → 0.4711 vs 0.405 (gap +0.0661) after dropping 395 phantom tokens — the published positive is not damage-driven and no verdict moves; the larger filtered gap is an IMPROVEMENT and per the discipline rule is NOT a claim — using it would require a new preregistered run deflated for the D1-prompted look (micro-F1 levels are not comparable across corpora: the boundary base rate shifts 0.4058→0.4231; the GAP is the comparand).

Discipline: results are annexes; if anything *improves*, that is a new preregistered run deflated for the D1-prompted look — verdicts never flip via annex.

## Close block (Art. XXII)

- **constitutional_compliance:** COMPLIANT — no silver rebuild, no verdict issued, counts
  script-generated, append-only record kept.
- **deviations:** none. **violations:** none. **waivers:** none.
