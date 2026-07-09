# EPOCH-086 PREREGISTRATION — Top-Row Glyph-Count / Density (Header Line?)

**Campaign:** Linear A frontier-72h
**Epoch:** EPOCH-086
**Layer:** L2 (spatial; opaque IDs; counts/positions only; NO phonetic/semantic values)
**Axis (DISTINCT):** row GLYPH-COUNT and DENSITY by row position (top vs lower rows).
  - E085 = row SIZE (glyph height); E079-084 = spacing/pitch; E077 = size x word-initial.
  - This epoch is about COUNT/DENSITY of glyphs per row, not size or spacing.

## Question
Does the TOP (first) spatial row carry MORE glyphs than lower rows (a "full/header line")?
Is that a WIDTH/geometry effect (top row spans wider) or a deliberately PACKED header?

## Data
- `experiments/linear_a_frontier_72h/data/sigla_glyphs_bbox.json`
- Exclude `is_divider`. Docs need >=6 non-divider bbox glyphs AND >=2 rows.
- Sites with >=15 usable docs: Haghia Triada, Khania, Zakros.

## Primary metric (COUNT)
`R_count = log( count(first/top row) / mean count(remaining rows) )` per doc.
`R_count > 0` => top row longer. Global `S_obs = median(R_count)` over docs.

## Secondary confound metric (DENSITY)
`R_density = log( density(first) / mean density(rest) )`,
`density = count / (x-span + 1)`, `x-span = max glyph x-center - min glyph x-center` in row.
- If top row longer only because WIDER (spans more): `R_count>0` but `R_density ~ 0` or `<0`
  => WIDTH/GEOMETRY-driven (parallels E083).
- If `R_density>0` too => genuinely PACKED header.

## Null
Random-row-as-heading: pick a UNIFORMLY RANDOM row as pseudo-heading, recompute median-R.
DIRECTIONAL (top LONGER): `perm_p = frac(null median-R >= S_obs)` over 1000 draws.

## Verdict rule (FROZEN, mechanical)
header-row-longer = top row has MORE glyphs, COUNT `S_obs` significantly > 0.
- `HEADER_ROW_LONGER_CROSS_SITE` iff PC passed AND global COUNT `perm_p<=0.05` AND `S_obs>0`
  AND significant in >=2 sites.
- `HEADER_ROW_LONGER_SITE_LOCAL` iff PC passed AND (global OR any site) COUNT significant
  BUT <2 sites significant.
- `NO_HEADER_ROW_LENGTH_STRUCTURE` iff PC passed AND global COUNT NOT significant AND 0 sites significant.
- `HEADER_ROW_UNDERPOWERED` iff <2 sites with >=15 usable docs OR PC power<0.5.
- `MACHINERY_UNINFORMATIVE` iff PC calibration fails.

## Density interpretation (NOT a separate verdict token)
- COUNT significant but DENSITY not (`S_density<=0` OR `perm_p>0.05`) => WIDTH/GEOMETRY-driven
  (full-width header line), NOT deliberately packed (parallels E083 WIDTH-DRIVEN).
- DENSITY also significant => genuinely packed header.

## Coordinator pre-check (for reference only; verdict is mechanical from this run)
COUNT global S +0.065 (p_longer 0.005); HT +0.138 (p=0.004, SIG); Khania 0.0 (p=0.912, null);
Zakros +0.083 (p=0.136, marginal) => expected SITE_LOCAL to HT.
DENSITY global S -0.047 (p=0.102, NS); HT -0.126 (p=0.618, NOT denser) => top row longer because
WIDER, not packed.

## Positive control (synthetic, gates verdict; on COUNT metric)
(a) DETECT: ~40 synthetic docs (2-4 rows), FIRST row ~1.7x MORE glyphs than body rows
    (bodies ~3-4 glyphs, header ~6-7). Confirm COUNT `S_obs` sig > 0 (`perm_p<=0.05`),
    `power_est` over >=15 reps.
(b) FALSE-POSITIVE (uniform): ~40 docs, ALL rows same expected glyph count. Confirm COUNT
    `S_obs` NOT sig > 0 (fire-rate <=0.10 over >=15 reps).
Realistic pixel x-centers (spaced ~100px) so density is well-defined.
If can't DETECT longer headers OR fires on uniform => `MACHINERY_UNINFORMATIVE`.

Seed: fixed (42). Single synchronous run.
