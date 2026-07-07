# D — Leave-One-Site-Out Libation-Formula Prediction

**Prereg:** DI_MINO_EXACT_CLAIM_V1 (sha 8b098a4c) · **Constitution:** v2.2 · **Seed:** 20260708

**Generator:** `scripts/D_leave_one_site_out.py` → `data/results/loso.json`

Question: does the Di Mino system *predict* held-out peak-sanctuary formula forms, or only explain them retrospectively? Mechanical LOSO; known values grade benchmarks only (non-circular). Primary held-out statistic = recurring morphology (root recurrence).

## Headline verdict: **NO_POWER**

Di Mino's exact-form prediction is identical to the frequency/template/structural baseline at every held-out site (it carries no regional-variation generator), so the exact-form LOSO channel has zero power to separate the system from the baseline; and the effective independent discriminating sites (3) sit at/below the NO_POWER floor (3). Every clean divergent form is a unique single-source singleton, unpredictable by any leave-one-out model.

## A. Sites, forms, partitions

- Peak-sanctuary invocation-slot sites (total): **8** — derivation sites excluded from clean LOSO: ['Iouktas', 'Troullos']

- Clean non-derivation sites: **6**

- Distinct invocation forms (candidate universe, 7): ['A-NA-TI-*301-WA-JA', 'A-TA-I-*301-DE-KA', 'A-TA-I-*301-WA-E', 'A-TA-I-*301-WA-JA', 'JA-TA-I-*301-U-JA', 'TA-NA-I-*301-TI', 'TA-NA-I-*301-U-TI-NU']

- Clean **divergent** (non-modal) forms — the only discriminating targets: ['A-TA-I-*301-DE-KA', 'A-TA-I-*301-WA-E', 'JA-TA-I-*301-U-JA', 'TA-NA-I-*301-TI'] at sites ['Apodoulou', 'Psykhro', 'Zakros']


## B. Exact-form top-1 accuracy (predicted form attested at held-out site)

| model | all sites | clean sites | clean **divergent** sites |
|---|---|---|---|
| M_freq | 0.625 (n=8) | 0.5 (n=6) | 0.0 (n=3) |
| M_tmpl | 0.625 (n=8) | 0.5 (n=6) | 0.0 (n=3) |
| M_markov | 0.625 (n=8) | 0.5 (n=6) | 0.0 (n=3) |
| M_davis | 0.625 (n=8) | 0.5 (n=6) | 0.0 (n=3) |
| M_dimino | 0.625 (n=8) | 0.5 (n=6) | 0.0 (n=3) |

- Di Mino makes a **different** exact-form prediction from the frequency baseline at any held-out site? **False**

- Di Mino **beats** baselines on held-out exact form? **False**

- Any model predicts a clean **divergent** singleton form? **False**


## C. Root recurrence (H2 — the Di Mino system's one falsifiable cross-site prediction)

- Clean held-out sites tested: 6; with `*301-WA-JA` root present: **3**

- Clean **divergent** held-out sites: 3; with the root: **0**

- per-site root presence: Apodoulou=0, Iouktas=1, Kophinas=1, Palaikastro=1, Psykhro=0, Syme=1, Troullos=1, Zakros=0

> The claimed *301-WA-JA root recurs ONLY in copies of the target form itself (and, on the derivation-contaminated Iouktas site, A-NA-TI-*301-WA-JA). In the 3 clean held-out DIVERGENT forms it recurs 0 times -> the root is a property of the single lexeme it was extracted from, not a cross-site morpheme. H2 root-recurrence is REFUTED on held-out divergent sites.


## D. Power / effective independent sites

- Effective independent **discriminating** sites (clean, divergent, single-source singletons): **3** vs NO_POWER floor 3

- Site components after collapsing sites carrying an identical form-set: **5**

- All forms are single-source (GORILA); every divergent form is a one-attestation, one-toponym unique lexeme → not learnable under leave-one-out (no second instance).


## E. Random-Semitic-root null (deflation)

- Representative divergent target `TA-NA-I-*301-TI`, 100000 draws (seed 20260708): null exact-form hit-rate = **0.14183**, null slot-parse hit-rate = **0.25161**; author-stated sims ~1e5.


## F. Boundary / segmentation

Boundary F1 scored vs a DATA-DRIVEN structural edge reference (branching-entropy word edges {b1, b_last} from report 04); it is a structural benchmark, NOT ground truth. Reported per site in loso.json.

| held site | boundary F1 M_dimino | boundary F1 M_davis |
|---|---|---|
| Apodoulou | 0.4 | 0.0 |
| Iouktas | 0.4 | 0.0 |
| Kophinas | 0.4 | 0.0 |
| Palaikastro | 0.4 | 0.0 |
| Psykhro | 0.4 | 0.0 |
| Syme | 0.4 | 0.0 |
| Troullos | 0.4 | 0.0 |
| Zakros | 0.4 | 0.0 |

## G. Interpretation (mechanical)

1. **The Di Mino system is not a predictor of regional form.** Its exact-form output is fixed to the single lexeme it was built on (`A-TA-I-*301-WA-JA` = the modal form), so its held-out prediction is byte-identical to the frequency/template/Davis baseline at every site. It cannot, by construction, exceed those baselines.

2. **The divergent regional forms are unpredictable by any model.** Each clean divergent form is a unique single-source singleton; leave-one-out removes its only instance, so exact-form accuracy on them is 0 for every model including the null.

3. **The one falsifiable cross-site prediction the system does make — recurrence of the `*301-WA-JA` root — FAILS on held-out divergent sites** (root present in 0 of them). The root is a property of one lexeme, not a morpheme that generalises.

4. **Therefore Task D returns NO_POWER for supporting the claim** (the exact-form channel cannot discriminate the system from the baseline, and the discriminating sites sit at/below the floor), with a **secondary REFUTATION** of the H2 root-recurrence sub-claim on the held-out divergent sites. No SUPPORT.
