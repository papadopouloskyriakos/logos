# EPOCH-062 REPORT — Document-Periphery of U+1076B (Linear A)

**Campaign:** Linear A frontier-72h · **Epoch:** 062 · **Layer:** L2 (pure token-position structure)
**Question:** Is the standalone marker U+1076B (`"\U0001076b"`, `t=='other'`) DOCUMENT-PERIPHERAL
(heading/colophon) or an INTERIOR separator within multi-line inscriptions, cross-site?

**Verdict (mechanical, frozen rule):** `MARKER_DOCUMENT_PERIPHERAL_CROSS_SITE`

---

## 1. Setup (NON-CIRCULAR)

- **Target:** anonymous token TYPE — `t == 'other'` AND `"\U0001076b" in raw`. No sign value, no reading.
- **Content-line:** maximal run of CONTENT tokens (`t in {word,num,other}`) bounded by `nl`/START/END.
  `div` and `nl` are structural, not content; `div` does NOT flush a line. Lines indexed `0..L-1`.
- **Testable inscriptions:** `L >= 3` content-lines AND `>= 1` marker-bearing line (so an interior exists).
  → 252 inscriptions, **440 target markers**.
- **Primary metric:** PERIPHERAL rate = fraction of target markers with `li == 0` (heading) OR `li == L-1` (colophon).
- **Null (frozen):** within each testable inscription, re-place each marker's `li` uniformly in `{0..L-1}`,
  independent, preserving marker count and `L`. Expected peripheral rate = marker-weighted mean of `2/L`.
  2000 reshuffles; one-sided perm p (enrichment). Heading and colophon tested separately vs uniform `1/L`.

## 2. Global result

| metric | observed | null mean | perm p (enrich) |
|---|---|---|---|
| **PERIPHERAL** | **0.691** | **0.382** | **0.0** |
| HEADING (li==0) | 0.286 | 0.191 | 0.0 |
| COLOPHON (li==L-1) | 0.405 | 0.191 | 0.0 |
| INTERIOR (0<li<L-1) | 0.309 | (~0.618) | depletion p = 1.0 |

Breakdown: first = 126, interior = 136, last = 178 (n = 440).
Expected peripheral (marker-weighted 2/L) = 0.3815, matching the null mean (0.3821) — null is well-calibrated.

**The marker is strongly enriched at the document periphery** (69.1% vs 38.2% expected). Both heading and
colophon positions are independently enriched; the **colophon/last-line signal is the stronger** (40.5% vs 28.6%).
Interior placement is depleted, ruling out an interior-separator read at the document level.

## 3. Positive Control (SYNTHETIC — gates verdict)

- **(a) DETECT:** planted corpus with every marker on first/last line → peripheral enrichment flagged, **p = 0.0**. ✓
- **(b) FALSE-POSITIVE:** markers placed uniformly among content-lines across 20 draws → rejection rate **0.05 ≤ 0.10**. ✓
- **PC verdict: PASSED.** (Synthetic; stated plainly.)
- Self-check: null mean (0.3579) matches marker-weighted 2/L (0.3577), |diff| < 0.001. ✓

## 4. Cross-site (sites with ≥10 testable markers)

| site | n | peripheral obs | null mean | perm p | direction | sig |
|---|---|---|---|---|---|---|
| Haghia Triada | 182 | 0.670 | 0.352 | 0.0000 | enriched | ✓ |
| Khania | 150 | 0.700 | 0.411 | 0.0000 | enriched | ✓ |
| Zakros | 49 | 0.674 | 0.421 | 0.0000 | enriched | ✓ |
| Phaistos | 18 | 0.889 | 0.410 | 0.0000 | enriched | ✓ |
| Knossos | 15 | 0.733 | 0.390 | 0.0050 | enriched | ✓ |
| Arkhalkhori | 14 | 0.571 | 0.289 | 0.0205 | enriched | ✓ |

**6 / 6 sites significant, same direction (enriched).** Leave-one-site-out on Haghia Triada (largest site):
observed 0.705, null 0.402, **p = 0.0** — survives.

## 5. Frozen mechanical verdict

PC PASSED ∧ global peripheral enriched (p=0.0) ∧ ≥2 sites significant same-direction (6/6 enriched) ∧
survives LOO (p=0.0) → **`MARKER_DOCUMENT_PERIPHERAL_CROSS_SITE`**.

## 6. Bottom line

U+1076B is **not** an interior separator and **not** positionally uniform. Combined with E061 (line-isolated),
the marker is a **document-peripheral element**: it sits on its own line, and that line is preferentially the
FIRST or (more often) the LAST content-line of multi-line Linear A inscriptions, robustly across all six
well-powered sites. This upgrades the structural read from "standalone marker" to **"document-peripheral
element (heading and/or colophon / section boundary) in the LA administrative apparatus."** The colophon
(last-line) role is the stronger signal. Anonymous token, document-line-position only; **no reading assigned.**

## 7. Outputs

- `prereg.md`, `plan_hash.txt`, `machinery.py`, `result.json` (this epoch dir)
- `data/epoch_062/marker_positions.json`, `data/epoch_062/per_site.json`
