# EPOCH-063 REPORT — Is Linear A's Standalone-Marker Inventory POSITION-DIFFERENTIATED?

**Campaign:** Linear A frontier-72h · **Epoch:** 063 · **Layer:** L2 (pure token-position structure)
**Question:** Do the two line-isolated `other` tokens — M1 = U+1076B (`"\U0001076b"`, peripheral per E062)
and M2 = U+2014 em-dash (`"—"`) — occupy DIFFERENT document-position niches (M1 brackets ENDS, M2 marks
INTERIOR), or are they positionally REDUNDANT (both peripheral)?

**Verdict (mechanical, frozen rule):** `MARKER_SYSTEM_POSITION_DIFFERENTIATED`

---

## 1. Setup (NON-CIRCULAR, L2)

- **Targets:** anonymous token TYPES — `t == 'other'` AND (`"\U0001076b" in raw` → M1, OR `"—" in raw` → M2).
  No sign value, no reading, no phonetics/meaning.
- **Content-line:** maximal run of CONTENT tokens (`t in {word,num,other}`) bounded by `nl`/START/END;
  `div` does NOT flush a line. Lines indexed `0..L-1`.
- **Testable inscriptions:** `L >= 3` content-lines AND `>= 1` target marker.
  → **M1: 440 markers** (E062); **M2: 52 markers**.
- **Metric:** PERIPHERAL = `li in {0, L-1}`; HEADING = `li==0`; INTERIOR = `0 < li < L-1`.
- **H1 (M2 interior-enrichment):** within-inscription line-shuffle null (re-place each M2 marker's `li`
  uniformly in `{0..L-1}`, preserving count + L; 2000 draws). `p_deplete = frac(null_periph <= obs)`.
- **H2 (differentiation contrast):** `d = periph(M1) - periph(M2)`; null = pool all M1+M2 `(li,L)` records,
  relabel which are M1 vs M2 preserving counts, recompute `d` (2000 draws); `perm p = frac(null d >= obs d)`.
- **M1 periphery is E062-established** (0.691, cross-site 6/6); NOT re-litigated here.

## 2. Honest scope caveats (stated up front)

1. **M2 is HT-anchored.** Only Haghia Triada has ≥10 M2 markers (n=21); all 9 other sites have <10
   (Palaikastro 6, Tylissos 6, Khania 5, Phaistos 5, Zakros 3, Milos 2, Petras 2, Knossos 1, Arkhalkhori 1).
   **M2's cross-site robustness CANNOT be certified** — the M2 leg is HT-anchored + global, NOT cross-site-certified.
2. **M2 = U+2014 (em-dash) MAY be a transcription RULING/DIVIDER mark** rather than an inscribed syllabogram.
   We do NOT claim M2 is an inscribed sign — only that it is a line-isolated TOKEN occupying the interior
   niche. The complementary-position finding is robust either way (inscribed interior sign OR ruled interior
   divider); interpret at L2 accordingly.

## 3. Global result

| marker | n | peripheral obs | null mean | p_deplete | heading | interior |
|---|---|---|---|---|---|---|
| **M1** (U+1076B) | 440 | **0.691** | 0.382 (E062) | — (enriched, E062) | 0.286 | 0.309 |
| **M2** (em-dash) | 52 | **0.115** | **0.298** | **0.0005** | **0.000** | **0.885** |

M2 breakdown: first = **0**, interior = **46**, last = **6** (n = 52).
M2 expected peripheral (marker-weighted 2/L) = 0.297, matching the null mean (0.298) — null well-calibrated.
M2 heading obs = 0.000 vs null 0.148, `p_deplete = 0.0` — M2 is **excluded from the heading line**.

**M2 is strongly INTERIOR-enriched** (88.5% interior, peripheral depleted vs null). This is the mirror image
of M1's peripheral enrichment.

## 4. Differentiation contrast (H2)

| metric | value |
|---|---|
| `d = periph(M1) - periph(M2)` | **0.576** |
| null mean of `d` (relabel) | -0.0015 |
| **perm p** (M1 more peripheral than M2) | **0.0** |

The two markers occupy **distinct, complementary** document-position niches. Under the relabel null (which
preserves the pooled position distribution and only shuffles the M1/M2 labels), a contrast this large never
occurs.

## 5. Positive Control (SYNTHETIC — gates verdict)

- **(a) DETECT:** planted corpus with M1 ALWAYS peripheral, M2 ALWAYS interior → differentiation flagged:
  M2 depleted `p = 0.0`, contrast `p = 0.0`. ✓
- **(b) FALSE-POSITIVE:** planted corpus with BOTH M1,M2 at peripheral positions, across 20 draws →
  contrast rejection rate **0.00 ≤ 0.10**. ✓
- **PC verdict: PASSED.** (Synthetic; stated plainly.)

## 6. M2 cross-site (report honestly)

| site | n | peripheral obs | null mean | p_deplete |
|---|---|---|---|---|
| Haghia Triada | 21 | 0.000 | 0.277 | 0.0 |

**n_sites_testable (≥10 M2) = 1.** Only Haghia Triada reaches the threshold, and there M2 is perfectly
interior (0/21 peripheral, p_deplete=0.0). **M2 is HT-anchored; cross-site NOT certified.** The global M2
signal is driven by the HT concentration plus smaller same-direction contributions from other sites, but no
second site clears n≥10. (M1 cross-site is E062-established — 6/6 sites enriched — and is not re-litigated.)

## 7. Frozen mechanical verdict

PC PASSED ∧ M2 peripheral significantly DEPLETED vs null (`p_deplete=0.0005 ≤ 0.05`, M2 interior-enriched)
∧ contrast `d=0.576` significant (perm `p=0.0 ≤ 0.05`, M1 more peripheral than M2) ∧ M1 periphery
E062-established → **`MARKER_SYSTEM_POSITION_DIFFERENTIATED`**.

## 8. Bottom line

**Yes — the standalone-marker inventory is position-differentiated.** Linear A documents deploy a SYSTEM of
(at least) two line-isolated tokens with COMPLEMENTARY structural roles: **M1 (U+1076B) brackets the document
ENDS** (heading and especially colophon, per E062), while **M2 (em-dash U+2014) marks the document INTERIOR**
(88.5% interior, 0% heading, peripheral depleted p=0.0005). The contrast between them (d=0.576, perm p=0.0)
is far beyond any relabel null. This upgrades the structural read from "a standalone marker" to **"a
two-role marker system: peripheral bracket (M1) + interior divider/separator (M2)."**

**Honest caveats, plainly stated:** (1) The M2 leg is **HT-anchored** — only Haghia Triada has ≥10 M2
markers, so M2's cross-site robustness is NOT certified; the differentiation finding is global + HT-anchored,
not cross-site-certified for M2. (2) M2 (em-dash) MAY be a **transcription ruling/divider mark** rather than
an inscribed syllabogram; we claim only that it is a line-isolated TOKEN in the interior niche, and the
complementary-position finding holds whether M2 is an inscribed interior sign or a ruled interior divider.
Anonymous tokens, document content-line position only; **no reading assigned.** Layer L2.

## 9. Outputs

- `prereg.md`, `plan_hash.txt`, `machinery.py`, `result.json` (this epoch dir)
- `data/epoch_063/analysis.json`, `data/epoch_063/marker_positions.json`
