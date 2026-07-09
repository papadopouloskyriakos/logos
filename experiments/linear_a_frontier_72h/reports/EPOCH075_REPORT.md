# EPOCH-075 REPORT — Hardening the E072 Libation-Order Cross-Site Positive

**Task:** Does the canonical cross-site ORDER of libation (stone-vessel) word-forms
survive LEAVE-ONE-SITE-OUT (LOSO) and LEAVE-THE-HUB-INSCRIPTION-OUT (LHIO), or is
its cross-site BREADTH concentrated in one site / one inscription?

**Layer:** L3 (pure structural ORDER; anonymous sign-tuples; NO reading, NO meaning).

**Verdict:** `LIBATION_ORDER_CROSS_SITE_QUALIFIED` — E072's positive is REAL but
NARROW. This is an append-only QUALIFICATION of E072, not a superseding correction.

---

## 1. Baseline (E072 reproduced)

| stat | value |
|---|---|
| n_testable pairs | 13 |
| n_cross pairs | 10 |
| C_cross | 1.000 |
| A_cross | 10 / 10 |
| perm p (C_cross) | 0.00050 |
| null mean C_cross | 0.737 |

E072's positive is reproduced exactly: all 10 cross-site pairs have perfect
consistency (C_cross=1.0) and unanimous cross-site agreement (A_cross=10/10),
far beyond the within-inscription shuffle null (~0.74), perm p=0.00050.

## 2. Effective-n (Art. VIII) — the concentration concern, confirmed

The 10 raw cross-site pairs are carried by:

- **8 distinct inscriptions** (not 10)
- **6 distinct sites** (Iouktas, Troullos, Kophinas, Syme, Palaikastro, Vrysinas)
- **Hub inscription IOZa2 (Iouktas) is an endpoint of ALL 10 cross-site pairs.**

Top carriers by pair-endpoint count:

| inscription | site | n_cross_pairs (endpoints) |
|---|---|---|
| IOZa2 | Iouktas | **10** (hub) |
| TLZa1 | Troullos | 6 |
| KOZa1 | Kophinas | 6 |
| SYZa3 | Syme | 1 |
| IOZa9 | Iouktas | 1 |
| PKZa27 | Palaikastro | 1 |
| IOZa15 | Iouktas | 1 |
| VRYZa1 | Vrysinas | 1 |

**Pairs sharing the hub inscription are NOT independent evidence.** The effective-n
(8 inscriptions / 6 sites) is far below the raw pair count (10), and the top-3
carriers (IOZa2, TLZa1, KOZa1) carry the overwhelming majority of the weight.

## 3. Leave-One-Site-Out (LOSO)

For each libation site with >=5 inscriptions:

| drop site | n_insc dropped | n_cross | C_cross | A_cross | perm p | null | status |
|---|---|---|---|---|---|---|---|
| Zakros | 42 | 10 | 1.000 | 10 | 0.00050 | 0.739 | **ROBUST** |
| Iouktas | 15 | 3 | 1.000 | 3 | 0.0455 | 0.754 | **ROBUST** |
| Palaikastro | 14 | 9 | 1.000 | 9 | 0.00050 | 0.732 | **ROBUST** |
| Syme | 11 | 10 | 1.000 | 10 | 0.00050 | 0.747 | **ROBUST** |

**ALL four site-drops are ROBUST.** Critically, dropping Iouktas (the hub site)
keeps n_cross=3 (powered, exactly at the floor) with C_cross=1.0 and perm p=0.0455
— still significant. The canonical order is NOT carried by any single site; it is
site-broad. The order signal is real.

## 4. Leave-Hub-Inscription-Out (LHIO) — the harshest concentration test

| drop | dropped ids | n_cross | C_cross | A_cross | perm p | null | status |
|---|---|---|---|---|---|---|---|
| top1 | IOZa2 | 4 | 1.000 | 4 | 0.0080 | 0.735 | **ROBUST** |
| top2 | IOZa2, TLZa1 | 3 | 1.000 | 3 | 0.0598 | 0.750 | **FRAGILE** |
| top3 | IOZa2, TLZa1, KOZa1 | 2 | 1.000 | 2 | 0.246 | 0.748 | **UNDERPOWERED** |

- **top1 (drop the hub alone): ROBUST** (n_cross=4, p=0.008). The hub inscription
  IOZa2 alone does NOT carry the signal — dropping it leaves a significant order
  among the remaining carriers.
- **top2 (drop hub + one partner): FRAGILE** (n_cross=3, powered, but p=0.0598 >
  0.05). Confirmed stable across 10 seeds (p=0.054–0.066). The breadth is carried
  by ~3 inscriptions; removing any 2 of them leaves too few pairs to stay
  significant.
- **top3: UNDERPOWERED** (n_cross=2 < floor of 3).

## 5. Signal-loss vs power-loss (the central discipline)

**In EVERY powered leave-out, C_cross stays at 1.000** — the order signal itself
NEVER collapses toward the null (~0.74). The single non-significant powered
leave-out (LHIO top2, n_cross=3, p~0.056) is a **power-loss at narrow breadth**
(too few pairs to reach p<=0.05), NOT a C_cross collapse. This is why the verdict
is QUALIFIED (narrow breadth) rather than FRAGILE (signal collapse). The canonical
order is intact wherever it is observed; what is narrow is HOW MANY independent
inscriptions carry it.

## 6. Positive Control (SYNTHETIC — gates the verdict)

| arm | result |
|---|---|
| DETECT-FRAGILE | hub-concentrated synthetic corpus: full C_cross=0.938 (n_cross=16); hub-site-drop -> n_cross=4, C_cross=0.750, p=0.5175 (non-sig). Test correctly FLAGS concentration. ✓ |
| DETECT-ROBUST | broadly-spread synthetic corpus: full C_cross=0.892; top-site-drop -> n_cross=13, C_cross=0.958, p=0.0010. Test correctly PASSES as ROBUST. ✓ |
| POWER | 20/20 replicates: fragile hub-drop classified FRAGILE/UNDERPOWERED AND robust top-drop classified ROBUST. power_est=1.00. ✓ |

**PC VERDICT: PASSED.** The machinery CAN distinguish a hub-concentrated order
from a broadly-spread one at the observed scale. It is informative.

## 7. Frozen mechanical verdict

Applying the frozen rule (precedence: MACHINERY_UNINFORMATIVE > UNDERPOWERED >
FRAGILE > QUALIFIED > ROBUST):

- PC PASSED (power_est=1.00) → machinery informative. ✓
- Baseline significant (p=0.00050). ✓
- NOT ROBUST: a powered leave-out (LHIO top2, n_cross=3) is non-significant
  (p=0.0598 > 0.05).
- NOT FRAGILE: no powered leave-out collapses C_cross toward the null (C_cross
  stays 1.0 everywhere; the top2 non-significance is power-loss, not signal-loss).
- NOT UNDERPOWERED-globally: many leave-outs (all LOSO + LHIO top1) stay powered
  and significant.

→ **`LIBATION_ORDER_CROSS_SITE_QUALIFIED`**: the core order consistency SURVIVES
most leave-outs (the order signal is real and site-broad), BUT the cross-site
BREADTH is concentration-dependent — the hub+partner drop (top2) is powered yet
non-significant, and the effective-n (8 inscriptions / 6 sites, with ~3
inscriptions carrying most of the weight) is far below the raw 10 pairs.

## 8. Bottom line

**E072 is a REAL but NARROW cross-site positive.** The canonical order of libation
word-forms is genuine: it survives every site-drop (including the hub site
Iouktas) and even the hub-inscription drop alone, with C_cross=1.0 everywhere.
But its cross-site breadth rests on a small effective-n — 8 inscriptions across 6
sites, with the hub inscription IOZa2 an endpoint of all 10 pairs and the top-3
carriers (IOZa2, TLZa1, KOZa1) bearing most of the weight. Removing the hub plus
one partner collapses the breadth to non-significance (power-loss at n_cross=3).

E072 should be read as **"a canonical order shared across a SMALL set of libation
inscriptions spanning several sites"**, not as a broad corpus-wide formula. This
is an append-only QUALIFICATION of E072 (an erratum/robustness note); it does not
silently strengthen or rewrite E072.

---

*Anonymous word-forms (sign-tuples, len>=2). Pure structural ORDER (stream
position). No reading, no phonetic value, no meaning. L3 only. PC synthetic.*
