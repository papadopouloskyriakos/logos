# EPOCH-034 REPORT — A-INITIAL WORDS AS INSCRIPTION-INITIAL (HEADING) MARKERS

**Campaign:** Linear A frontier-72h  |  **Epoch:** EPOCH-034  |  **Layer:** L2/L3 (positional / document-structural)
**Verdict:** `A_HEADING_ROLE_SITE_LOCAL`

> "A-" and "heading" are ANONYMOUS positional labels. "heading" = DOCUMENT-INITIAL POSITION only.
> No phonetics, no sound, no meaning, no reading.

---

## 1. QUESTION

Do **A-initial words** (word tokens whose first sign is `A`) occupy the **inscription-initial
position** (the FIRST word of an inscription) more than chance, and is that robust across sites?
Tests a document-structural (heading) role for the A- class purely positionally.

**Leads:** E025 (A- is a productive word-initial prefix); E033 (A-initial words are depleted on
ledger entries = counted items, suggesting A- words are labels/headings).

## 2. METHOD (frozen)

- **Metric:** among inscriptions with >=2 word tokens, `p_A_first` = fraction whose first word is
  A-initial; `p_A_last` (control axis); `base_A_rate` = per-inscription mean A-initial rate.
- **Null:** within-inscription **word-ORDER permutation** (word multiset fixed), >=2000 draws,
  one-sided p = frac draws with permuted `p_A_first` >= observed. Calibrated by construction
  (permute positions = H0 of no positional preference); verified by the PC false-positive arm.
- **Positive control (gates verdict):** LB (DĀMOS; no site metadata -> SEEDED pseudo-inscription
  partition, stated). DETECT a planted heading bias (force sign `A` initial in ~45% of
  pseudo-inscriptions) — must reject p<=0.05 in the correct direction. FALSE-POSITIVE on
  position-randomized pseudo-inscriptions — rejection rate <=0.10 across >=30 sets.
- **Cross-site:** per site with >=15 qualifying inscriptions; leave-one-site-out on Haghia Triada.

## 3. RESULTS

### 3.1 Global

| metric | value |
|---|---|
| n inscriptions (>=2 words) | **415** |
| `p_A_first` (observed) | **0.1446** |
| null mean `p_A_first` | 0.0790 |
| null max (2000 draws) | 0.1108 |
| **global p (one-sided)** | **0.0** |
| `p_A_last` (control axis) | 0.0458 |
| `base_A_rate` | 0.0795 |

A-initial words are the first word of an inscription **14.46%** of the time vs a null mean of
**7.90%** — the observed value exceeds the **maximum** of 2000 null draws (0.1108), so p=0.0 is
genuine, not a tie artifact. The control axis confirms directionality: `p_A_last` (4.58%) is
**below** the base rate (7.95%) — A-initial words are initial-biased, **not** final-biased.

### 3.2 Positive control — PASSED (gates verdict)

| arm | result |
|---|---|
| DETECT (planted heading bias on LB) | obs=0.497 vs null=0.162, **p=0.0**, correct direction ✓ |
| FALSE-POSITIVE (position-randomized, 30 sets) | **FPR=0.033** (<=0.10) ✓ |

The machinery detects a planted initial-position bias and does not fire on position-randomized
noise. **PC PASSED.**

### 3.3 Cross-site

| site | n_insc | p_A_first | null_mean | p | sig (initial) |
|---|---|---|---|---|---|
| Haghia Triada | 181 | 0.0994 | 0.0408 | **0.0005** | ✓ |
| Khania | 67 | 0.1791 | 0.0959 | **0.0075** | ✓ |
| Knossos | 24 | 0.1250 | 0.0897 | 0.3315 | — (underpowered) |
| Phaistos | 22 | 0.1364 | 0.0907 | 0.3010 | — (underpowered) |
| Zakros | 34 | 0.0294 | 0.0987 | 1.0000 | ✗ (REVERSE) |

- **n_sites_testable = 5** (>=3, so not underpowered).
- **n_sites_sig = 2** (Haghia Triada, Khania).
- **Leave-one-site-out** (exclude Haghia Triada): obs=0.179, **p=0.0**, survives ✓.
- **Zakros reverses** the signal (obs 0.029 << null 0.099, p=1.0) — genuine site heterogeneity.

## 4. VERDICT (frozen mechanical rule)

PC PASSED ✓ · global p=0.0 (<=0.05) ✓ · n_sites_testable=5 (>=3, not underpowered) ✓ ·
**n_sites_sig=2 (<3)** → **`A_HEADING_ROLE_SITE_LOCAL`**.

The global heading-position signal is strong and the control axis confirms directionality, but
cross-site robustness is only partial: the effect is carried by the two largest sites (Haghia
Triada, Khania), two sites are underpowered (Knossos, Phaistos), and Zakros actively reverses it.

## 5. HONEST BOTTOM LINE

There is a **real, positionally-defined document-initial role for the A- class** at the
global level and at the two largest sites — A-initial words open inscriptions more than chance
and avoid the final position, and the machinery is certified by a passing positive control.
But it is **not cross-site robust**: only 2 of 5 testable sites are individually significant
and Zakros reverses the direction. **Verdict = `A_HEADING_ROLE_SITE_LOCAL`** (NOT
`CROSS_SITE_ROBUST`): the cross-site robustness bar (>=3 significant sites) is NOT met.
"Heading" here means DOCUMENT-INITIAL POSITION only — a purely positional label, with no
semantic, phonetic, or reading claim about A- implied.

## 6. SUCCESSORS (see result.json)

E035 Zakros reversal; E036 positional profile of all frequent initial signs; E037 support-type
(tablet) interaction; E038 combine with E033 (non-entry/label words); E039 power small sites;
E040 positional decay profile by word rank.
