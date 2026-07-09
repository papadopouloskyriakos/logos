# EPOCH-073 REPORT — GENRE CONTRAST: IS RIGID CANONICAL WORD-ORDER GENERAL LA OR LIBATION-SPECIFIC?

**Layer:** L3 (pure structural ORDER; anonymous word-forms; no reading, no meaning)
**Control for:** EPOCH-072 (libation formula-as-ordered-sequence)
**Verdict:** `ADMIN_ORDER_WEAKER_THAN_LIBATION`

## Question

EPOCH-072 found the LIBATION (stone-vessel) corpus has a PERFECTLY consistent
canonical word-ORDER (all pairs order-consistency 1.000, cross-site, beyond a
within-inscription shuffle null). The skeptic's question: is that just what LA
word-order looks like everywhere (a general feature), or is the RIGID canonical
order a property of the LIBATION genre specifically (a liturgical formula)?

This epoch applies the SAME order-consistency machinery (E072) to the
ADMINISTRATIVE corpus (support in {Tablet, Nodule, Roundel}) and CONTRASTS its
order-rigidity with libation's.

## Data (verified pre-counts reproduced)

- ADMIN: 174 multi-word inscriptions over 11 sites, 77 testable pairs (>=2 occ),
  3 cross-site pairs, C_glob = 0.8394.
- LIBATION (E072 reference): C_glob = 1.0000, 13 testable pairs, 10 cross-site.

## Metric & Null (frozen, identical to E072)

Anonymous word-forms (sign tuples, len>=2). For each inscription every
unordered pair of distinct forms yields one observation (site, sign); sign=+1
if (lex-key fa<fb) fa precedes fb in stream (first-occurrence pos), else -1.
Testable pairs: total occurrences >= 2. consistency(pair) =
max(n_plus,n_minus)/(n_plus+n_minus). C_glob = mean consistency over testable
pairs. NULL: within-inscription word-order shuffle (preserves each
inscription's word multiset -> invariant testable/cross-site pair sets;
destroys only order), 2000 draws, one-sided perm p = frac(null>=obs), add-one
smoothed. Null mean is EMPIRICAL (~0.745, >0.5), validated against closed-form
E[max(H,T)/k] in the machinery self-check.

## Positive Control (SYNTHETIC — stated; gates verdict)

| Gate | Result | Threshold | Pass |
|---|---|---|---|
| (a) DETECT power | 1.000 (20/20 rigid replicates flagged p<=0.05) | >=0.5 | ✓ |
| (b) FALSE-POSITIVE rate | 0.050 (1/20 random-order flagged) | <=0.10 | ✓ |
| (c) DISCRIMINATION | rigid C=1.000 CI(1.000,1.000) vs weak C=0.720 CI(0.697,0.744), separated | separated | ✓ |

**PC VERDICT: PASSED.** Machinery is informative; it detects rigid order,
does not fire on random order, and distinguishes rigid from weak-order corpora.

## Global results

### ADMIN
- n_multiword_inscriptions = 174, n_sites = 11
- n_testable_pairs = 77, n_cross_pairs = 3
- C_glob = **0.8394** vs shuffle-null mean **0.7453**, perm p = **0.0020**
  → admin within-inscription word-order is significantly more consistent than
  the shuffle null. Admin is NOT a pure bag-of-words; it has a weak
  within-document order preference.

### LIBATION (reference)
- C_glob = **1.0000**, n_testable_pairs = 13, n_cross_pairs = 10
  → perfectly rigid (reproduces E072).

## Genre contrast (bootstrap over admin pairs)

- admin C_glob = 0.8394, bootstrap 95% CI = **(0.7879, 0.8874)** (5000 resamples)
- libation C_glob = 1.0000
- delta (lib - admin) = **0.1606**
- admin significantly less rigid than libation: bootstrap upper bound 0.8874
  < libation 1.0000 → **YES**

The admin CI excludes libation's perfect rigidity by a wide margin. The rigid
canonical order is LIBATION-SPECIFIC; admin order is only weakly preferred.

## Cross-site sub-analysis (underpowered, as predicted)

Admin has only **3 cross-site co-occurring pairs** (vs 10 for libation). This
is the predicted consequence of E071's finding that admin vocabulary is
site-local: site-local forms do not co-occur across sites, so the admin
cross-site order test is structurally UNDERPOWERED (n_cross < 5). This is an
honest finding, not a machinery failure — the well-powered signal is the
GLOBAL within-inscription rigidity and the genre contrast, both of which are
decisive.

## Frozen mechanical verdict

- PC PASSED ✓
- admin n_testable_pairs = 77 (>=15) ✓, PC power = 1.000 (>=0.5) ✓ → not UNDERPOWERED
- admin C_glob = 0.8394, perm p = 0.0020 (<=0.05) → significantly > null ✓
- admin bootstrap upper bound 0.8874 < libation 1.0000 → significantly below libation ✓

→ **`ADMIN_ORDER_WEAKER_THAN_LIBATION`**: a rigid canonical word-order is
LIBATION-SPECIFIC; admin order is only weakly preferred. (Admin cross-site
order test is underpowered: n_cross = 3 < 5, as predicted by E071 site-local
admin vocabulary.)

## Bottom line

A rigid canonical within-inscription word-order is **LIBATION-SPECIFIC**, not
a general Linear A feature. Administrative texts do have a weak, statistically
real within-document order preference (C_glob=0.839 vs shuffle-null 0.745,
p=0.002) — they are not a pure bag-of-words — but their order is far less rigid
than libation's perfect 1.000 (bootstrap CI 0.79-0.89 excludes 1.000). This is
consistent with libation being a fixed liturgical formula and admin being
practical record-keeping with only loose ordering conventions. The contrast is
sharp and graded, and the admin cross-site order test is structurally
underpowered (3 cross-site pairs) exactly as E071's site-local vocabulary
finding predicts.

## Non-circular / discipline

Anonymous word-forms (sign tuples, len>=2); genre = physical support field;
within-inscription word-order shuffle null preserves each inscription's word
multiset (which pairs co-occur, at which sites, how often) and destroys ONLY
order; testable pairs restricted to >=2 co-occurrences; null mean of
consistency is EMPIRICAL (~0.745, >0.5), validated against closed-form
E[max(H,T)/k], never naive-0.5; genre contrast via bootstrap over admin pairs.
L3 ONLY: no reading, no phonetic value, no meaning.
