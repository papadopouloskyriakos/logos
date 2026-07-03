<!-- S&M 2017 p.100 trust criteria, VERBATIM (applied as sm_trust in anchor_census.csv): "Personal names are not a particularly good guide as there usually is no independent confirmation available that two identically or very similarly written forms render the same name; in addition it can be hard, even within Linear B, to tell whether a given form is a personal name or an appellative title, indication of a profession or the like. There must be particular doubt concerning the identification of personal names especially when parallels from Pylos are invoked. Further problems with such identifications can be illustrated by the equation a-ka-re-u = a-ka-ru. a-ka-re-u in the Linear B tablet from Knossos is undoubtedly a man's name, but Linear A a-ka-ru, as would appear from its position in the tablet, is a heading and may be a transactional term. Linear A a-ka-ru would thus have nothing to do with Linear B a-ka-re-u. Likewise, i-ja-te in Linear B, attested at Pylos, is probably the entirely Greek word for doctor, ἰατήρ, and has nothing to do with the Linear A term i-ja-te. Where, however, the Linear B personal names are limited to Knossos and/or do not have a ready explanation from within Greek, such as sa-ma-ru or qa-qa-ro, the identification across the two scripts and languages is clearly tempting." -->

# Phase-2 anchor census — provenance record

Companion to `anchor_census.csv`. **Provenance only**: no statistical evaluation of any
anchor — no effect on recovery was computed or estimated for any row. Sources:
Steele & Meissner 2017 ("From Linear B to Linear A", in *Understanding Relations Between
Scripts*, Oxbow, 93–110; local copy `corpus/bronze/steele_meissner_2017/chapter-6.pdf`,
book page N = PDF page N−77) and John Younger's Linear A pages (archived Wayback
captures, see below). Toponym rows carried over verbatim from
`experiments/crossscript_gate/toponym_anchors.csv` (not re-derived).

## Totals (47 rows)

### By class
| class | rows |
|---|---|
| toponym | 15 (6 carried from toponym_anchors.csv + 1 S&M cf.-row i-da-a + 8 Younger-only) |
| personal_name | 25 (all non-bold rows of Table 6.3, p.101) |
| gloss_acrophonic | 3 |
| variation_constraint | 4 |

### By independence_class
| independence_class | rows |
|---|---|
| 1 (toponym) | 15 |
| 2 (personal name / adaptation pair) | 25 |
| 3 (gloss / acrophonic) | 3 |
| 4 (variation constraint — never pins) | 4 |

### By sm_trust
| sm_trust | rows |
|---|---|
| tempting | 9 (6 toponym carryover + i-da-a cf. + sa-ma-ro + qa-qa-ru) |
| debunked | 2 (a-ka-ru, i-ja-te — undermined by S&M themselves, p.100) |
| neutral | 28 (21 personal names + 3 gloss + 4 variation) |
| n/a | 8 (Younger-only rows; S&M take no position) |

### By source_status
| source_status | rows |
|---|---|
| primary (S&M chapter in hand) | 39 |
| secondary (Younger archived Wayback captures) | 8 |

fringe_flag = false on all 47 rows. No row's only source is mainstream-flagged work
(Owens 1993b/1994b appears only *as cited by Younger* inside hedged entries; no Owens
rows were added from memory).

## S&M p.100 trust criteria (verbatim; PDF p.23)

> "Personal names are not a particularly good guide as there usually is no independent
> confirmation available that two identically or very similarly written forms render the
> same name; in addition it can be hard, even within Linear B, to tell whether a given
> form is a personal name or an appellative title, indication of a profession or the
> like. There must be particular doubt concerning the identification of personal names
> especially when parallels from Pylos are invoked."

> "Further problems with such identifications can be illustrated by the equation
> a-ka-re-u = a-ka-ru. a-ka-re-u in the Linear B tablet from Knossos is undoubtedly a
> man's name, but Linear A a-ka-ru, as would appear from its position in the tablet, is
> a heading and may be a transactional term. Linear A a-ka-ru would thus have nothing to
> do with Linear B a-ka-re-u. Likewise, i-ja-te in Linear B, attested at Pylos, is
> probably the entirely Greek word for doctor, ἰατήρ, and has nothing to do with the
> Linear A term i-ja-te. Where, however, the Linear B personal names are limited to
> Knossos and/or do not have a ready explanation from within Greek, such as sa-ma-ru or
> qa-qa-ro, the identification across the two scripts and languages is clearly tempting."

Context also recorded from the same page: Duhoux (1989, 69) — 3 identical signs ⇒ "low
80% range" likelihood of identity, 4 ⇒ 99%; S&M's caveat that Duhoux's figures "are
blind to the relative frequency of the signs", with qa-ra₂-wo = qa-ra₂-wa (rare sign
ra₂; fn.17: c. 68 LB instances, max 38 LA, 18 of those in sa-ra₂) reaching "a higher
likelihood of indicating the same name".

Mapping to `sm_trust`: **debunked** = the two pairs S&M themselves undermine
(a-ka-re-u = a-ka-ru; i-ja-te = ἰατήρ); **tempting** = those S&M name as the
Knossos-limited / no-Greek-etymology class (sa-ma-ru, qa-qa-ro) plus, per the census
rules, the Table 6.4 toponym carryovers; **neutral** = everything else S&M list without
a specific flag (Pylos-parallel doubts recorded per-row in `disagreement_notes`, not as
a trust downgrade, since S&M state them as a general caution, not a per-row verdict).

## Adaptation pairs (Tables 6.8–6.10, book p.105 / PDF p.28)

All seven pairs are already rows of Table 6.3 and were **annotated, not duplicated**
(dedup invariant): Table 6.8 (LA -u → LB -o): qa-qa-ru/qa-qa-ro, di-de-ru/di-de-ro,
ku-*56-nu/ka-*56-no; Table 6.9 (LA -o → LB -u): sa-ma-ro/sa-ma-ru; Table 6.10
(LA -e → LB -o): pa-ja-re/pa-ja-ro, a-ta-re/a-ta-ro, a-ra-na-re/a-ra-na-ro. Each
carries "morphological adaptation pair" in `disagreement_notes`. S&M §7 (pp.105–106):
-Cu → -Co is "an expected adaptation to the morphological structure of Greek where male
PNs end in /-os/ much more often than in /-us/"; the reverse (6.9) is "curiously, also
attested" and "does raise questions as to the phonological status of the o- and u-series
in Linear A".

## Younger archiving provenance (summary)

The canonical host `people.ku.edu` is DEAD (DNS NXDOMAIN, verified 2026-07-03; KU
decommissioned personal pages early 2024). Younger's successor material is login-gated
on Academia.edu and no longer the cited page structure, so the latest Internet Archive
snapshots of the canonical KU pages were archived instead (raw `id_` captures, original
bytes), in `corpus/bronze/younger_lineara/` (gitignored, not redistributed):

1. `lineara-main.html` — main text page incl. §10c Place Names, page-stated
   "latest update: 3 July 2023", from
   `https://web.archive.org/web/20231222205430id_/https://www.people.ku.edu/~jyounger/LinearA/`
   (CDX digest unchanged since 2023-07-17), 155,975 bytes,
   SHA-256 `4fc646614a37909fe7d50844fa76d4b0c9dc3eec0792c8fabcc069527715ada4`.
2. `lexicon.html` — Linear A Lexicon, page-stated "last update: 7 August 2023", from
   `https://web.archive.org/web/20231203062200id_/https://www.people.ku.edu/~jyounger/LinearA/lexicon.html`,
   159,774 bytes,
   SHA-256 `463778cc7d7262a57adab53c75c33261554af9be69a70a1857bf34079e6c5b94`.

Fetched 2026-07-03; authorship verified on-page in both files ("Comments, corrections,
questions: John Younger (jyounger@ku.edu)"); PROVENANCE.md written alongside;
acquisition entry added. Hence `source_status=secondary` (archived snapshot, not live
canonical) for all Younger-only rows.

Residual gaps: (1) the archived copies are Wayback snapshots, not the live site — the
KU server is permanently gone; (2) any post-Aug-2023 revision of Younger's place-name
views lives in login-gated Academia.edu PDFs (e.g. academia.edu/117949722) and would
need a human download + diff against §10c; (3) internal inconsistencies to carry when
citing: §10c TU-RI-SA vs lexicon TU-RU-SA for the same KO Za 1b-c word, and §10c
KU-*79-NI = lexicon KU-ZU-NI; (4) Younger has **no** DI-KA-TA form and does **not**
identify WI-NA-DU as a toponym (lexicon: "second name in a three-name list KH 5.3") —
do not cite him for di-ka-ta or wi-na-du = Inatos.

## Salgarella 2020 — pending primary source

Salgarella, E. 2020, *Aegean Linear Script(s): Rethinking the Relationship between
Linear A and Linear B* (CUP) is **not yet in hand**. Its acquisition would settle:

- **Homomorphy grades**: her graded sign-by-sign classification of LA–LB shape
  correspondence would replace our binary "same sign" assumption with explicit grades
  per covered sign, letting each census row record *how* homomorphic its signs are on
  an independent palaeographic basis.
- **Independent A/B sign-relationship corroboration for the name equations**: the
  personal-name rows (independence_class 2) currently rest on sequence identity alone —
  exactly the weakness S&M flag on p.100 ("no independent confirmation available").
  Salgarella's structural/palaeographic derivation of LB signs from LA would provide a
  corroboration channel that does not itself presuppose the name equations.
- Whether any Table 6.3 pairing involves signs she grades as *non*-cognate (which would
  demote the row's sign coverage), and her position on contested signs (*56, *79, ra₂).

Until then, no census field claims Salgarella support; rows rest on S&M (primary) and
Younger (secondary) only.

## Vetting discipline

Vetting was **content-blind to outcomes**: rows were included, classed, and
trust-labelled solely from what the cited sources state (page-cited), before and
independently of any recovery computation. No anchor's statistical effect on recovery
was computed, estimated, or consulted in deciding its inclusion, class, sm_trust, or
notes. The `sm_trust` labels transcribe S&M's own p.100 judgements; the `?` flags
transcribe the chapter's own query marks (§5, p.103); the hedges on Younger rows
transcribe his own wording.

## Input rows skipped / merged (with reasons)

- **Table 6.3 bold rows** pa-i-to, se-to-i-ja, su-ki-ri-ta, tu-ri-so/tu-ru-sa and the
  cf.-row di-ka-ta-jo/di-ki-te: NOT duplicated — already carried from
  `toponym_anchors.csv` (Table 6.4).
- **i-da(-i-jo)/i-da-a cf.-row**: a toponym not in Table 6.4 — included as a new
  toponym row (`top_i_da_a_cf`) with cf.-status noted; Younger's heavily hedged I-DA
  position (incl. the rival "this thing" reading, Davis 2011/2014) appended there
  rather than a new row.
- **Younger TU-RI-SA = Tylissos** and **PA-I-TO / SE-TO-I-JA / SU-KI-RI-TA /
  DI-KI-TE / A-TU-RI-SI-TI** entries: overlap S&M rows — appended to those rows'
  `authority_positions` instead of new rows.
- **WI-NA-DU**: skipped as an anchor row — Younger does *not* identify it as a toponym
  (lexicon: name in a list, KH 5.3); adding it would over-read him (extraction's own
  warning).
- **Tables 6.8–6.10 pairs** (7): merged into their existing Table 6.3 rows as
  annotations (see above), not duplicated.
- **t63 input was null** in the orchestrator's JSON: Table 6.3 and the p.100 criteria
  were extracted directly from the chapter PDF (book pp.100–101 = PDF pp.23–24) for
  this census.

## Addendum (2026-07-03) — Salgarella 2020 ingested; the pending list SETTLED

The monograph (DOI 10.1017/9781108783477; `corpus/bronze/salgarella_2020/`) settles what this
census listed as pending: homomorphy grades now fill `anchors.csv` (57/59 signs, her Table 2–4
labels verbatim with pages; PA3 and ZU stay pending — she carries AB *56/*79 as undeciphered,
Table 4 p.37 / Index pp.412–13). Census enrichment (provenance only, 9 rows): her p.33
endorsement — toponyms pa-i-to, se-to-i-ja, su-ki-ri-ta; anthroponyms da-i-pi-ta, pa-ra-ne,
qa-qa-ru→qa-qa-ro, di-de-ru→di-de-ro ("a strong piece of evidence providing reasonably secure
readings"); MA+RU 'wool'; NI 'fig' (acrophonic) — appended to authority_positions. No NEW
lexical identifications beyond rows already present (reported honestly). Taxonomy notes:
docs/related/salgarella-2020-taxonomy.md. The N=2 ledger is untouched; nothing recomputed.
