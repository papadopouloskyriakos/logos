# EPOCH-033 REPORT — Ledger Entry-Word vs Non-Entry-Word Structural Contrast (L2/L3)

**Campaign:** Linear A frontier-72h · **Layer:** L2/L3 (structural statistics only)
**Verdict:** `ENTRY_CLASS_NO_CONTRAST`
**Plan hash:** `57989017c690a043c7b13ce579b52ab0f4017eea34bd935f06006566ebf156ad  prereg.md`

---

## 1. Question & discipline

E031 certified the ledger grammar: **WORD then NUMERAL** (entry then quantity). This defines two
functional word classes by **OBSERVABLE structure only**:

- **ENTRY-word** = a `word` token whose *immediately-following* stream token is `num`.
- **NON-ENTRY word** = a `word` token whose following token is *not* `num` (or it is last).

**Question:** do these two classes differ STRUCTURALLY — in (a) word **LENGTH** (n signs, primary)
and (b) **A-INITIAL rate** (E025's productive prefix, secondary) — and is any contrast ROBUST across
independent sites?

**Discipline (hard):** tokens carry NO phonetic/sound/meaning/reading; L2/L3 structural statistics
only; LB is a positive-control benchmark only. Prereg + plan_hash frozen BEFORE running; PC first;
mechanical verdict from the frozen rule.

## 2. Data & inspection

- Corpus: `corpus/silver/inscriptions_structured.json` — 1341 inscriptions, ordered `stream`.
- Word tokens: **3147** total → **1040 ENTRY-words**, **2107 NON-ENTRY-words**.
- 8 sites are testable (≥15 words in EACH class): Haghia Triada, Khania, Zakros, Phaistos,
  Palaikastro, Arkhalkhori, Tylissos, Malia. (Not underpowered.)

## 3. Positive control (gates the verdict) — **PASSED**

| Check | Result |
|---|---|
| DETECT planted LB length gap | p = **0.0005**, contrast = **+2.34** (correct positive direction) |
| FALSE-POSITIVE (same-distribution, 30 splits) | rate = **0.0** (≤ 0.10) |

The label-permutation machinery is informative: it detects a real planted difference and does not
fire on null splits. The negative LA verdict below is **not** a machinery artifact.

## 4. Global contrast (primary = LENGTH)

| Metric | ENTRY | NON-ENTRY | Contrast (E−N) | two-sided perm p |
|---|---|---|---|---|
| **LENGTH (n signs)** | 1.801 | 1.860 | **−0.059** | **0.211** |
| A-INITIAL rate | 0.0298 | 0.0707 | −0.0409 | 0.001 |

- **Primary metric (LENGTH): NOT significant** (p = 0.211 > 0.05). Entry words are marginally
  *shorter*, but indistinguishable from a label-permutation null.
- Secondary metric (A-rate): significant (entry less A-initial, p = 0.001), but A-rate is
  reported only and does not override the primary length verdict.

## 5. Cross-site (held-out) — LENGTH

8 testable sites; **4 individually significant** for length, but **direction is INCONSISTENT**:

| Site | n_entry | n_nonentry | len_contrast | p | direction |
|---|---|---|---|---|---|
| Haghia Triada | 686 | 1205 | **+0.311** | 0.0005 | entry LONGER |
| Khania | 76 | 292 | −0.441 | 0.0005 | entry shorter |
| Tylissos | 28 | 15 | −0.921 | 0.015 | entry shorter |
| Malia | 25 | 16 | −1.078 | 0.002 | entry shorter |
| Phaistos | 29 | 81 | −0.446 | 0.094 | — |
| Zakros | 114 | 104 | −0.177 | 0.328 | — |
| Arkhalkhori | 27 | 36 | −0.306 | 0.392 | — |
| Palaikastro | 18 | 59 | −0.312 | 0.574 | — |

**Leave-one-site-out (exclude Haghia Triada):** global length contrast = **−0.561**, p = 0.0005.
Haghia Triada (the dominant site) *masks* an opposite effect present elsewhere — outside it, entry
words are clearly shorter. This is **site-local heterogeneity**, not a robust corpus-wide role
contrast.

## 6. Frozen mechanical verdict

Rule precedence: PC > UNDERPOWERED > NO_CONTRAST > SITE_LOCAL > ROBUST.

- PC: **PASSED** ✓
- Testable sites: **8** (≥3) → not UNDERPOWERED
- **Global length-contrast p = 0.211 > 0.05** → **`ENTRY_CLASS_NO_CONTRAST`**

(The inconsistent per-site directions and the LOO flip reinforce — but do not drive — the verdict;
the frozen rule keys off the global primary-metric p, which is non-significant.)

## 7. Bottom line (honest, no overclaim)

There is **no robust corpus-wide structural contrast in word LENGTH** between ledger ENTRY-words
and NON-ENTRY-words. The two functional classes are length-indistinguishable globally (p = 0.21).
What looked like a signal is **site-local heterogeneity**: Haghia Triada alone shows entry words
slightly longer, while most other sites show the opposite — and these cancel to a null. The
secondary A-initial contrast is significant but reported, not verdict-driving. This is a
**structural role-contrast test (L2/L3) with a negative result**: by structure alone, the
entry/non-entry functional split does not mark a consistent word-length role across the Linear A
corpus. No meaning, phonetics, or readings are claimed or implied.

## 8. Outputs (PATH CONTRACT)

- `experiments/linear_a_frontier_72h/epochs/EPOCH-033/prereg.md`
- `experiments/linear_a_frontier_72h/epochs/EPOCH-033/plan_hash.txt`
- `experiments/linear_a_frontier_72h/epochs/EPOCH-033/machinery.py` (self-check via `__main__`)
- `experiments/linear_a_frontier_72h/epochs/EPOCH-033/result.json`
- `experiments/linear_a_frontier_72h/data/epoch_033/` (global_summary, positive_control,
  cross_site, word_records.jsonl, README)
- this report
