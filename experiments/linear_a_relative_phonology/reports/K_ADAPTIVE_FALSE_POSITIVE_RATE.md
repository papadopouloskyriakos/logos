# K1 — Adaptive False-Positive Rate + per-positive SURVIVES/ARTIFACT verdict

**Constitution v2.2** · L2/L3 · no phonetic value · seed `20260708` · data `data/K1_nulls.json`
(`K1_VERDICTS` block). Every number RUN.

This is the campaign's self-audit against its own selection process. The mandate: (a) the
value-layer false-positive rate — verify that under the adaptive value null a value "positive" as
strong as the best observed appears at the **chance** rate (the nulls confirm the nulls, no value
positive suppressed); and (b) subject each L2/L3 positive to the adaptive null that reproduces its
own selection, and rule SURVIVES or ARTIFACT.

---

## (a) VALUE-LAYER false-positive rate

**Verdict: `VALUE_LAYER_FALSE_POSITIVE_RATE_CONSISTENT_WITH_CHANCE`.**

The mechanical basis is relabeling-invariance. The held-out structural read-count (# multi-sign words
that parse to a recurrent-stem morphology) is **1005**, and over 200 consistent value relabelings its
**standard deviation is exactly 0.0** — the count is identical for every value map. Therefore the
value layer carries **0 bits** of selection-exploitable information: any candidate reading has ≥10²⁷
relabeling-equivalent twins (I1), and no search over value maps can prefer one over another without an
external anchor (SEED_A = 0). 

Consequence for the false-positive question: **there is no value positive to suppress or inflate.**
Every value-bearing statistic the campaign produced — position→C/V (freq artifact), substitution axis
on LA (not recoverable), seed-propagation 0.87 (freq artifact), cross-script transfer R@5 (null), SEM
KU-RO='total' (FWER 0.0149 raw but fails Holm, LOO→0), I1 C15 consonant grade (p 0.046, matched by a
permuted-corpus winner) — sits inside its random-lexicon / permuted-corpus band. The adaptive value
null reproduces them at chance. **No value positive was hidden by the nulls; the value layer is
honestly, comprehensively closed.**

---

## (b) L2/L3 positives under their reproducing adaptive null

| positive | selection reproduced | observed | naïve p | **adaptive-null p** | **verdict** |
|---|---|---|---|---:|---|
| **A- prefixation** | best-of {≈195 affix × 8 seg × 2 slot} | prod 47 | 0.050 Holm | **0.008** | **SURVIVES** |
| **A- cross-site generalization** (E3) | best-of affix × both HT split directions | min 16 | 0.0099 | **0.42** | **ARTIFACT** |
| **libation rigid order** (E2) | random 5-anchor systems | 10 pairs all-consistent | 5e-5 | **0.030** | **SURVIVES** |
| **ledger KU-RO terminal** (E2) | random ledger total-anchor | 0.69 / 0.79 | — | **0.002** | **SURVIVES** |
| **carrier-value grammar** (E2) | implied by KU-RO + coverage 96.6 % | — | — | inherits ledger | **SURVIVES** |
| **SEAL_2** (held-out inscriptions, A-) | inherits A- + 1/5 seal choice | rate 0.0525 in band | — | ≤ 0.04 (0.008×5) | **SURVIVES** |
| **SEAL_3** (unseen site Khania, ledger) | inherits ledger + KU-RO absence | wf 0.85, KU-RO=0 | — | ≤ 0.01 (0.002×5) | **SURVIVES** |
| **SEAL_4** (unseen libation LOO) | inherits libation order | 0 inversions | — | ≤ 0.15 (0.030×5) | **SURVIVES / borderline** |

### A- prefixation — SURVIVES (adaptive p 0.008)
The published p_holm 0.050 corrected only for 10 named tests. The full best-of-affix × segmentation
null lifts the chance productivity from a single-affix ≈24 to a best-of ≈37 — yet the observed 47 is
still at the ~99.2nd percentile (adaptive p 0.008). Two **independent** supports confirm it is not a
selection artifact: (i) `shuffled_morphology` collapses the best-of-affix to ≈28 and never reaches 47
→ real within-word position structure exists; (ii) E5's held-out predictive gain beats shuffled-stem /
shuffled-suffix / random-cut corruptions (paired p 0.0005) — a different metric entirely. The residue
is a single robust anonymous word-initial prefix class.

### A- cross-site generalization — ARTIFACT (adaptive p 0.42)
This is the one selection artifact the audit exposes. Requiring "the same affix significant in BOTH
HT-in and HT-out partitions" sounds stringent, but under best-of-affix selection *some* affix reaches
min-both-direction ≥ 16 in 42 % of null corpora. The E3 headline p = 0.0099 therefore does **not**
survive best-of-affix/split correction. This does not refute A- (established above); it means the
cross-site result should be read **descriptively** — A-'s raw word-initial rate is in fact higher
off-HT (Khania 7.1 %, Zakros 9.2 % vs HT 2.5 %, per E3 T1) — not as an independent p = 0.0099 finding.
**Recommended erratum:** downgrade the E3 cross-site claim from "significant generalization (p 0.0099)"
to "descriptive cross-site presence; nominal significance is a best-of-affix selection artifact."

### libation rigid order — SURVIVES (adaptive p 0.030)
Sharpens the E2 claim honestly. Zero inversions **alone** is cheap: 61 % of random 5-anchor systems
also produce a fully consistent order, because most co-occur on only 2–6 pairs. The real strength is
**10 co-occurring pairs all consistent** — reached by just 14/493 = 2.8 % of random systems. Adaptive
p ≈ 0.030: survives, but the honest strength is ~0.03, not 5e-5. The 5e-5 permutation-p correctly
tests *order-shuffling* but not *anchor-set selection*; the latter costs ~2.7 orders of magnitude.

### ledger KU-RO terminal / carrier-value — SURVIVES (adaptive p 0.002)
No random recurring ledger word (0/500) matches KU-RO's terminal-leaning + numeral-adjacency profile;
combined with the arithmetic sum-consistency (7/31 exact, separate channel), the total-slot is a
genuine positional outlier. The carrier-value entry grammar (96.6 % coverage) inherits.

### Seals — inherited, with seal-selection multiplicity
SEAL_2/3/4 are held-out structural transfers of the three surviving positives; their adaptive status
inherits the parent's, times a ≤5× Bonferroni penalty for choosing 3 positives out of 5 seals. SEAL_2
(0.04) and SEAL_3 (0.01) survive comfortably; SEAL_4 (0.15) is borderline once anchor-selection is
credited — consistent with the libation grammar being the weakest of the three.

---

## Campaign-wide false-positive rate

- **Value layer:** 0 positives survive; expected 0 under the adaptive null (relabeling-invariant, 0
  bits). **Match — nulls confirm nulls.**
- **L2/L3 layer:** the strongest single find (A- = 47) has campaign-adjusted **p 0.008**; over ~40
  tasks with selection DOF the expected number of spurious L2/L3 finds *at that strength* is
  40 × 0.008 ≈ **0.32** (< 1). The three surviving positives (A-, libation, ledger) have joint
  adaptive p ≈ 0.008 × 0.030 × 0.002 ≈ 5e-7 — vanishingly unlikely to be jointly spurious.
- **One artifact identified and named:** the E3 cross-site *nominal significance* (adaptive p 0.42),
  now downgraded to a descriptive statement.

## Mechanical K1 verdict

```
VALUE_LAYER_FALSE_POSITIVE_RATE      = CONSISTENT_WITH_CHANCE   (0 bits; 0 positives; none suppressed)
L2L3_POSITIVES_SURVIVING_ADAPTIVE    = {A- prefixation (0.008),
                                        libation rigid order (0.030),
                                        ledger KU-RO terminal / carrier-value (0.002)}
L2L3_POSITIVES_FALLING_TO_ADAPTIVE   = {A- cross-site NOMINAL significance (0.42) -> ERRATUM: descriptive only}
SEALS                                = SEAL_2, SEAL_3 SURVIVE; SEAL_4 borderline (anchor-selection cost)
CAMPAIGN_WIDE                        = NULLS_CONFIRM_NULLS; the surviving positives are NOT search artifacts;
                                       expected spurious L2/L3 at A- strength over 40 tasks ~0.32 (<1).
```

All findings remain **L2/L3 anonymous relative structure**. No phonetic value is assigned; no transfer
licence is earned. The adaptive audit strengthens rather than weakens the honesty of the campaign: it
confirms three durable structural positives, quantifies exactly how much the naïve p-values were
inflated by selection, and surfaces one over-claimed significance (cross-site) for correction.
