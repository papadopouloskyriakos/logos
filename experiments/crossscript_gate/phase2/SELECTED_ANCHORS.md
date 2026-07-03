# SELECTED_ANCHORS — Phase 2 §1 output (rule commit `fcb0c34`, content-blind)

**k = 8 (the Step-1 quota), drawn from the 33-row strict-tier pool by the committed
provenance-only rule:**

| # | anchor | class | sm_trust | source | signs (eligible members) |
|---|---|---|---|---|---|
| 1 | top_su_ki_ri_ta | toponym | tempting | primary | SU KI RI TA |
| 2 | top_tu_ru_sa | toponym | tempting | primary | TU RU SA |
| 3 | top_di_ki_te | toponym | tempting | primary | DI KI TE |
| 4 | top_se_to_i_ja | toponym | tempting | primary | SE TO I JA |
| 5 | top_pa_i_to | toponym | tempting | primary | PA I TO |
| 6 | top_ku_ta_younger | toponym | n/a | secondary | KU TA |
| 7 | top_ku_ni_su_younger | toponym | n/a | secondary | KU NI SU |
| 8 | top_sa_ra2_younger | toponym | n/a | secondary | SA RA2 |

Coverage: **17 distinct eligible signs** (DI I JA KI KU NI PA RA2 RI RU SA SE SU TA TE TO TU);
legs per sign ≤ 2 (I, KI, KU, SA, SU, TA, TO at 2 — natural LOTO redundancy); no
pin-degenerate words. All five S&M Table 6.4 equations are in; the three Younger rows are the
top-ranked archived-secondary toponyms by the seeded tie-break. Artifact:
`results/selected_anchors.json`.

## Implementation-fix disclosure (pre-certification, pre-freeze)

The first run of the pool filter excluded `top_se_to_i_ja` and `top_tu_ru_sa` through
string-matching artifacts that CONTRADICTED the committed rule: (a) se-to-i-ja's note
"the LB equation itself is **unqueried** in S&M" substring-matched 'queried' — while the rule
text explicitly keeps se-to-i-ja selectable; (b) tu-ru-sa's note records S&M's §5 '?' on the
s-series VARIATION evidence, while its Table 6.4 equation is clean — the Phase-1 frozen,
externally-timestamped prereg already adjudicated tu-ru-sa as a non-queried form. The matcher
was fixed to the rule's equation-level semantics (negation-aware; variation-series '?' does not
exclude), disclosed here BEFORE certification ran. `top_i_ti_ni_sa_younger` remains excluded on
substance (Younger's own lexicon does not mark it as a place name — an equation-level internal
inconsistency). Pool: 31 → 33 rows; no statistical quantity of any anchor was computed or
consulted at any point.
