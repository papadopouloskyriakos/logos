# EGYPTIAN_CALIBRATION_INCLUSION_RULES — §IV (FROZEN, data-independent)

Non-Cretan only. Excludes Kom el-Hetan Cretan toponyms, EA5647 Keftiu names, alleged Keftiu ritual
strings, all Linear A forms, all future Cretan confirmatory anchors, and any item selected for LA
resemblance (verified by `test_egyptian_schema::cretan_exclusion`).

## Item classes
PERSONAL_NAME · TOPONYM · ETHNONYM · DIVINE_NAME · TITLE · LOANWORD · OTHER

## Eligibility tiers
A = high-confidence Egyptian reading + high-confidence foreign source form · B = one bounded uncertainty ·
C = disputed / sensitivity-only · X = excluded.

## Frozen rules (see `src/calibration/schema.py::INCLUSION_RULES`)
disputed etymology → C · donor-language uncertain → B/C · intermediary transmission → excluded from primary
· duplicate attestations → keep highest, aggregate · multiple spellings of one form → all, one fold ·
multiple source proposals → excluded (ambiguous target) · genre/period mismatch → down-weight / separate
period-matched model / NO_POWER if sparse · names vs loanwords → item-class-stratified · short/damaged/
uncertain-segmentation → confidence-tiered. Cretan/Keftiu/LA → X by rule.
