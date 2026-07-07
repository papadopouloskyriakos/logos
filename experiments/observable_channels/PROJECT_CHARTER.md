# PROJECT CHARTER — Observable Administrative Channel Recovery

## Decision & pivot

The label-based semantic-role route is CLOSED as a rigorous negative (`NO_POWER_BEFORE_MODELING`: 66
non-trivial units, 2 of 4 classes, 19-unit sealed set). This programme **avoids semantic gold entirely** and
trains/evaluates against **directly-observable administrative channels** present in the tablets:

logogram identity · numeral/quantity presence + range · fraction presence · row/entry structure · total &
subtotal relationships · document-template membership · cross-document recurrence · site-invariant structure.

**Central falsifiable question:** *Can opaque word forms predict independently-observable administrative
channels when lexical identity, site shortcuts, and document-series shortcuts are controlled?* — falsifiable
with **no human annotators**.

## Isolation

- **Branch:** `research/observable-admin-channel-recovery` · **Worktree:** `/home/claude-runner/gitlab/n8n/logos-observable-channels`
- **Parent:** `research/no-human-structural-decipherment @ 946e53e` (inherits the document graph, feature sets,
  pseudo-script/degradation concepts). `main@f6a5682`, paper/, runtime/(CSA), all completed/closed branches
  untouched.

## Permitted / forbidden

- **Permitted Linear A output (after a successful benchmark only):** anonymous, observable associations, e.g.
  "`LA_CLUSTER_07` frequently precedes `A_LOGO_14`, occurs in quantity-bearing entries, medial row position,
  stable across three sites." — functional structure + grounded associations.
- **Forbidden:** "LA_CLUSTER means oil", "LA_FORM is a personal name / is Greek", "LA_SIGN = /ka/". No
  semantic/phonetic/translation claim; `SEMANTIC_DECIPHERMENT = NOT_AUTHORIZED`.

## Primary Linear B experiments

1. **Masked logogram recovery** — hide an entry's logogram, predict it from opaque word forms + order +
   neighbours + numerals + layout; hold out complete lexical + morphological families.
2. **Masked quantity-channel recovery** — predict quantity presence / bucket / fraction / total-contribution;
   explicit numeral tokens must NOT enter the predictor for the masked target.
3. **Accounting-closure** — do inferred row structures improve reconstruction of missing quantities /
   subtotal boundaries / allocation groups / inconsistent entries?
4. **Document-template completion** — mask entries/rows; reconstruct entry count / row order / notation type /
   expected channel / total placement.
5. **Cross-site invariance** — train KN→test non-KN and reverse; remove site identity, scribe, series, lexical
   identity.
6. **Pseudo-script validation** — O2 (independent sign permutations) + D8 (LA-like degradation) with the
   OBSERVABLE target (not sparse semantic gold). **Primary benchmark = O2 + D8.**

## Load-bearing controls

- **A12 (remove lexical identity across train/test) is MANDATORY** — a gain from memorising known LB forms is
  not transferable evidence.
- Ablations A0–A12; end-to-end nulls (logogram-label shuffle, numeral shuffle, row rewiring, template shuffle,
  site shuffle, sign permutation, family-group permutation, model-selection-under-null, best-of-restart,
  best-of-model-family).

## Mechanical gate — `OBSERVABLE_CHANNEL_READY` requires ALL

above the strongest frequency/layout baseline · CI excludes the complete null · success on **≥2 distinct
observable channels** · success under **unseen lexical-family** eval · success in **≥1 KN↔non-KN** direction ·
survives **O2+D8** · no dependence on site/series/lexical identity · stable latent templates across resampling
· adequate simulation-derived effective sample size. Else `NO_POWER` or `REJECT_ARCHITECTURE`.

A negative verdict is a successful scientific result.
