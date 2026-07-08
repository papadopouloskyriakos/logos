# EPOCH-032 REPORT — CROSS-SITE RECURRENT ADMINISTRATIVE WORD-FORMS

**Campaign:** Linear A frontier-72h
**Epoch:** EPOCH-032
**Layer:** L2/L3 (pure distributional word-form recurrence; ANONYMOUS sign sequences)
**Verdict (frozen mechanical):** `MACHINERY_UNINFORMATIVE`
**Plan hash:** `75eba8fd3fc24964c7f3658e4b8f9effaf7a3312ab9c8f2a75336a90218f6f19`

---

## 1. Question (frozen)

Does Linear A administration share a common vocabulary of word-forms ACROSS independent SITES —
i.e. do word-forms (full sign sequences) recur at MULTIPLE sites MORE than a site-label-shuffle null
predicts? Pure L2/L3 distributional recurrence. Word-forms are ANONYMOUS sign sequences; no
phonetics, no sound, no meaning.

## 2. Data & metric (frozen)

- Corpus: `corpus/silver/inscriptions_structured.json` — 1341 inscriptions, 52 sites, 3147 word
  tokens, 1165 distinct word-forms.
- Word-form = tuple of `signs` on a `t=="word"` stream token. Site = inscription `site`.
- **Metric:** `n_shared` = # word-forms (total count ≥ 2) appearing in ≥ 2 distinct sites.
- **Null:** site-label shuffle (permute site labels across inscriptions; preserve each site's
  inscription count and each inscription's word-form multiset). 2000 draws. One-sided p for
  "more cross-site sharing than chance".
- Site distribution is highly skewed: **Haghia Triada = 845/1341 (63%)**, next is Khania (159),
  then Knossos (51), Phaistos (48), Zakros (46) …

## 3. Global result

| quantity | value |
|---|---|
| n word tokens | 3147 |
| n distinct forms | 1165 |
| **n_shared (≥2 sites)** | **148** |
| null mean (site-label shuffle) | **202.81** |
| **null p (greater)** | **1.0** |
| supplementary null p (less) | 0.0005 |

Observed cross-site sharing (148) is **far BELOW** the site-shuffle null mean (202.8). The
"more sharing than chance" one-sided p is **1.0** — i.e. there is significantly **LESS**
cross-site sharing than this null predicts (p_less ≈ 0.0005).

Multiplicity (n_sites → n_forms, among count≥2 forms): 1→132, 2→86, 3→23, 4→15, 5→11, 6→3,
7→5, 8→2, 9→2, 10→1. 62 forms span ≥3 sites.

## 4. Why observed < null (null-structure diagnosis)

The site-label-shuffle null **structurally over-predicts** cross-site sharing under site-size
dominance. Haghia Triada holds 63% of all inscriptions and concentrates most word-forms. When
site labels are permuted, HT's concentrated forms get scattered across the many small sites
(Khania, Knossos, Phaistos, …), which **inflates** their apparent site-breadth and pushes null
n_shared (202.8) well above the observed (148). This is a property of the null + the skewed
site-size distribution, not noise.

## 5. Positive control (gates the verdict)

**LB (DĀMOS, 13562 wordforms, 4946 distinct)** seeded into 8 pseudo-sites via **contiguous
blocks** of the original sequence order (declared deviation: contiguous blocks, not round-robin,
to preserve real within-site form clustering — round-robin washes out the signal).

| PC quantity | value |
|---|---|
| LB n_shared | 1136 |
| LB null mean | 1551.18 |
| **LB detect p (greater)** | **1.0** |
| supplementary LB p (less) | 0.0005 |
| **detect_ok** | **false** |
| i.i.d. false-positive rate (30 controls) | **0.0** |
| fp_ok | true |
| **PC verdict** | **FAILED** |

LB shows the **same** pattern as LA: n_shared significantly **below** the site-shuffle null
(p_greater=1.0, p_less≈0.0005). The frozen DETECT criterion required LB to be significantly
**above** chance (p≤0.05); it is not. → **PC FAILED**.

The machinery is, however, **well-calibrated**: across 30 i.i.d. false-positive controls (tokens
drawn i.i.d. by marginal form-frequency, partitioned into pseudo-sites of real site sizes) the
false-positive rate is exactly **0.0** — the test never fires spuriously when there is no
identity↔site association. The failure is a **null-structure / test-direction mismatch**, not a
calibration defect.

## 6. Held-out robustness (leave-one-site-out)

Remove Haghia Triada, recompute on the remaining 51 sites:

| LOO quantity | value |
|---|---|
| loo_n_shared | 93 |
| loo_p (greater) | 1.0 |
| n_forms spanning ≥3 sites (non-HT) | 62 |

Cross-site sharing among the non-HT sites is still **below** the shuffle null (p=1.0). A raw core
of 62 forms spanning ≥3 sites persists, but it does not exceed the null prediction.

## 7. Top cross-site word-forms (ANONYMOUS)

| form (signs) | n_sites | total count |
|---|---|---|
| A | 10 | 25 |
| TE | 9 | 58 |
| JA | 9 | 11 |
| VIN | 8 | 53 |
| KI | 8 | 19 |
| SI | 7 | 118 |
| NI | 7 | 76 |
| I | 7 | 39 |
| TA | 7 | 29 |
| OLE | 7 | 22 |
| KA | 6 | 169 |
| KU | 5 | 170 |
| GRA | 5 | 62 |

These are dominated by **single-sign tokens** and high-frequency commodity/logogram signs. They
are ANONYMOUS sign sequences — **no phonetic or meaning claim is made**. A KU-RO-type total form
is **not** among the top cross-site forms.

## 8. Frozen mechanical verdict

Per the frozen rule: PC DETECT failed (lb_detect_p = 1.0 > 0.05) → **`MACHINERY_UNINFORMATIVE`**.

This verdict is **mechanical**, computed from the frozen rule. The operator does not adjudicate.
The label reflects that the frozen DETECT criterion (which assumed LB would show MORE sharing than
chance) cannot be met because the site-label-shuffle null over-predicts sharing under site-size
dominance — a null-structure/direction mismatch. The machinery itself is calibrated (i.i.d. FPR =
0.0) and detects a strong, consistent, **opposite-direction** signal in both LA and LB
(significantly LESS sharing than chance, p_less ≈ 0.0005).

## 9. Honest bottom line

Under the **frozen** site-label-shuffle null testing for **more** cross-site sharing than chance,
Linear A shows **no signal in the predicted direction** — and neither does the Linear B positive
control. Both corpora have significantly **fewer** cross-site-shared word-forms than this null
predicts, because the null inflates sharing by scattering the dominant site's forms across smaller
sites. The test as specified cannot adjudicate the shared-admin-vocabulary question: the PC gate
fails by construction. A successor epoch should either (a) re-specify the null to test the actual
operative direction (site-localization), (b) use a site-balanced or frequency-stratified null, or
(c) restrict the metric to multi-sign forms and recover real LB provenance for a grounded PC.

## 10. Non-circularity

Word tokens carry NO phonetic / sound / meaning / reading. All statistics are pure L2/L3
distributional recurrence of anonymous sign sequences. LB is a positive-control benchmark ONLY.
The verdict is mechanical from the frozen rule. The supplementary p_less is reported for honesty
about signal direction and is NOT used for the verdict.

## 11. Artifacts

- `experiments/linear_a_frontier_72h/epochs/EPOCH-032/prereg.md`
- `experiments/linear_a_frontier_72h/epochs/EPOCH-032/plan_hash.txt`
- `experiments/linear_a_frontier_72h/epochs/EPOCH-032/machinery.py` (self-check: `python3 machinery.py`)
- `experiments/linear_a_frontier_72h/epochs/EPOCH-032/result.json`
- `experiments/linear_a_frontier_72h/data/epoch_032/la_global_null.json`
- `experiments/linear_a_frontier_72h/data/epoch_032/la_loo_ht.json`
- `experiments/linear_a_frontier_72h/data/epoch_032/lb_pc_null.json`
- `experiments/linear_a_frontier_72h/data/epoch_032/iid_fp_controls.json`
