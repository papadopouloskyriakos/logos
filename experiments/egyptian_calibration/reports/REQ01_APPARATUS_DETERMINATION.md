# REQ-01 — Aegean-list apparatus determination (2026-07-06)

Mechanical determination from the user-delivered **Bělohoubková 2014** BA thesis (sha `91a0035b…`),
extracted + cross-validated by workflow `wf_0d343956-f7c` (9 agents, 0 errors). The thesis apparatus
was vision-read (3 page ranges) and each core Cretan reading cross-checked against the two independent
in-hand sources (**Cline & Stannish 2011**, and **Edel & Görg 2005** as reproduced on German Wikipedia),
with Egyptological transcription conventions normalized to a bare consonantal skeleton before judging.

## Determination

| field | value |
|---|---|
| `document_is_primary_edition` | **false** — secondary BA thesis, not Edel & Görg 2005 and not Kitchen's collation |
| `reproduces_primary_apparatus` | **true** — Obr. 5 (p.54) = line-drawing facsimile of the toponym ovals, cited "(EDEL – GÖRG 2005: Tf. 13)" = **Edel & Görg's own hand-copy**; Obr. 7 = Taf. 14 |
| collatable? | **no** — the reproduced plates are small/low-contrast; intra-oval glyphs are not resolvable to sign level |
| `req01_status` | **ADVANCED_PROXIMATE_ONLY** (not CLOSED) |
| `cretan_targets_confirmatory_eligible` | **false** |

**Why not CLOSED:** facsimile reproduction *inside a secondary source* is not personal collation of the
primary edition (Invariant 3). No sign-level-resolvable primary apparatus is yet in hand.

## Candidate target set (frozen as CANDIDATE, not confirmatory)

Frozen only where **≥2 independent sources** agree on the normalized consonantal skeleton **and** the
list position/identification. Normalization: aleph (`3`/`A`/`ꜣ`) and glides/vowel-carriers (`i`/`j`/`y`/`w`)
dropped; Gardiner **M8** written `s3`/`S3`/`SA`/`š3` → `š`.

| Toponym | Normalized skeleton | En position | Linear B | Sources agreeing | Verdict |
|---|---|---|---|---|---|
| **Knossos** | `k-n-š` | E_N10 (Tab. I row 137) | ko-no-so | thesis `k3-jn.jw-š3` · C&S `kA-n-yw-SA` (knS) · WP `k3-jn-jw-s3` | **FREEZABLE (candidate)** |
| **Amnisos** | `m-n-š` | E_N1 (row 128), **doubled** at E_N11 (row 138) | a-mi-ni-so | thesis `(j)-m-n-j-š3` · C&S `i-m-n-y-SA` (imnS) · WP `ʿ-m-nj-s3` | **FREEZABLE (candidate)** |
| **Lyktos** | `r-k-t` | E_N12 (row 139) | ru-ki-to | thesis `rj-k3-tj` · C&S `ry-kA-ti` (rkt) · WP `rj-k3-tj` | **FREEZABLE (candidate)**¹ |
| **Phaistos** | `b-š-t` (only glyph-bearing form) | conflict: glyph form at E_N2 (row 129) vs conjectural lost oval E_N14 | pa-i-to | Edel & Görg only; form reads **primarily Pisaia/Pisatis**, Phaistos tentative | **NOT freezable** — SUBSTANTIVE_DISCREPANCY |
| **Kydonia** | `k-t-w-n` | early row E_N3 (row 130) vs C&S's final-oval reconstruction | ku-do-ni-ja | all sources reduce to **Edel & Görg alone**; C&S gives no independent glyph reading | **NOT freezable** — single-authority |

¹ Lyktos independence rests on Cline & Stannish 2011 corroborating `r-k-t`; the thesis and Wikipedia both
trace to Edel & Görg 2005:188 and count as one source.

## Residual gap (what still blocks REQ-01)

Obtain and **directly collate** Edel & Görg 2005's own plates (Tf. 13/14) + apparatus at usable
resolution, **or** Kitchen's full hieroglyphic collation. Until then the primary edition is not in hand
at sign-level resolution and the Cretan targets stay a **candidate** set.

## Recommendation

- Keep REQ-01 **OPEN** at `ADVANCED_PROXIMATE_ONLY`.
- Hold **Knossos / Amnisos / Lyktos** (`k-n-š` / `m-n-š` / `r-k-t`) as a **pre-registerable candidate
  target set**, promotable to confirmatory targets **only after** direct collation of Edel & Görg 2005
  (or Kitchen) closes REQ-01.
- Do **NOT** freeze Phaistos or Kydonia.
- Next acquisition action: a high-resolution copy of **Edel & Görg 2005** (ÄAT 50) for personal collation.

*Full per-agent apparatus (all 16+19 entries, incl. Keftiu/Tanaja headings, Mycenae, Nauplia, Kythera,
Messene, the `w3jwrjj`=Ilion/Elis crux) is in the workflow journal `wf_0d343956-f7c/journal.jsonl`.*
