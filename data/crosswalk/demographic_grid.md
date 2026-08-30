# Canonical demographic grid

This is the "single reference table both the requirement model and the consumption model will key
off" called for in PLAN.md's Phase 2 checkpoint. It resolves three source tables with three
different age-band schemes into one grid.

The computed table lives at `data/processed/population_canonical_grid.csv` (16 age bands x 2 sex =
32 rows). The PAL (physical activity level) reference table lives at
`data/processed/pal_levels.csv`. This file documents how both were built and why.

## The three source age-band schemes

- **RV021** (Statistikaamet population, 1 Jan 2026): finest granularity — single-year band for age
  0, then clean 5-year bands from 1-4 up through 95-99, plus an open-ended 100+.
- **RTU011** (TAI 2014 consumption survey): the only source with actual consumption grams/day, but
  coarser and irregular — 2-5, 6-9, 10-13, 14-17, 18-24, then clean 5-year bands 25-29 through
  70-74. Nothing below age 2, nothing above age 74.
- **Tabelraamat** (TAI 2025 requirement tables): coarsest and least regular of the three. Children
  (Table 4) are given per single year for ages 1-3, then bands 4-6, 7-10, 11-14, 15-17. Adults
  (Table 5) use only four bands: 18-24, 25-50, 51-70, >70.

## Decision: RTU011 bands are canonical

The grid uses RTU011's age bands as the canonical scheme, for one reason: RTU011 is the only source
with actual measured consumption (grams/day), and the consumption model (Phase 4) is what this
whole analysis exists to calibrate against. The other two sources can be *mapped onto* RTU011's
bands without inventing data:

- **Population → RTU011 bands**: RV021's bins are strictly finer than or equal to RTU011's, so
  every RTU011 band's population can be built by summing (or fractionally prorating) RV021 bins.
  This is real disaggregation, not estimation from a coarser source.
- **Tabelraamat → RTU011 bands**: Tabelraamat's bands are coarser than or equal to RTU011's, so
  every RTU011 band falls entirely inside one Tabelraamat band (or, for children, is built from a
  short weighted average of adjacent Tabelraamat values — see "Requirement-side mapping" below).
  This is a lookup, not an interpolation across a boundary.

Going the other direction — using RV021's fine bands as canonical, or Tabelraamat's coarse bands —
would have required inventing sub-band consumption data that RTU011 simply doesn't provide.

## Population reconciliation (RV021 → RTU011 bands)

Method: **uniform-within-bin proration**. Each RV021 5-year bin is assumed to hold its population
evenly across its constituent single ages (e.g. RV021's "5-9" bin, 4 of whose 5 ages fall in
different canonical bands, is split 4/5 : 1/5). This is a standard, explicitly-flagged
simplification — real single-year age distributions are not perfectly flat within a 5-year band —
but Statistikaamet does not publish single-year-of-age population, so it is the best available
method without a second, single-year data source.

| Canonical (RTU011) band | Built from RV021 as |
|---|---|
| 2-5 | 3/4 of "1-4" (ages 2-4) + 1/5 of "5-9" (age 5) |
| 6-9 | 4/5 of "5-9" (ages 6-9) |
| 10-13 | 4/5 of "10-14" (ages 10-13) |
| 14-17 | 1/5 of "10-14" (age 14) + 3/5 of "15-19" (ages 15-17) |
| 18-24 | 2/5 of "15-19" (ages 18-19) + all of "20-24" |
| 25-29 ... 70-74 | exact 1:1 match to the same-named RV021 band |
| 75+ | sum of RV021 "75-79", "80-84", "85-89", "90-94", "95-99", "100+" |

## The two population gaps

RTU011 has no consumption data below age 2 or above age 74. Both ends needed an explicit decision
rather than a silent drop:

- **Ages 0-1 (infants): excluded from v1 scope entirely.** 20,960 people (1.54% of the national
  population, per RV021 2026) — male 10,788 / female 10,172. Rationale: infant feeding
  (breastfeeding/formula, then early complementary foods) is not what the TAI toidupüramiid or
  RTU011 describe in the first place — Tabelraamat treats 6-11 months and 1-2 years as their own
  separate %E-macronutrient regime (Table 6), not portions of the six-food-group pyramid this whole
  model is built around. Folding infants into a "% self-sufficiency" framework built for the
  pyramid would be more misleading than excluding them, so v1 excludes this age band and reports
  the excluded share plainly wherever national totals are shown.
- **Ages 75+: included, using the 70-74 RTU011 band as a consumption proxy.** 135,615 people (male
  40,481 / female 95,134 — note the strong female skew, consistent with life expectancy). Unlike
  infants, the elderly are unambiguously part of the pyramid framework — Tabelraamat's own
  requirement table has an explicit ">70" band — and excluding over 135,000 people (about 10% of
  the national population) would badly distort any national food-security conclusion. Since
  RTU011 itself has no >74 consumption data, this model assumes elderly consumption patterns
  (75+) resemble the 70-74 band rather than the general adult average — a documented approximation,
  not a measurement. If a newer TAI consumption survey with an 75+ band ever becomes available,
  this is the row to update first.

## Requirement-side mapping (Tabelraamat → RTU011 bands)

Not yet computed as numbers (that's Phase 3's requirement model, PLAN.md Section 5.1) — but the
lookup method is fixed here so Phase 3 has no open design questions left:

- **Adults (18-24, 25-29...70-74, 75+)**: Tabelraamat Table 5's four adult/elderly bands (18-24,
  25-50, 51-70, >70) are each flat (a single kcal figure per sex x PAL, not a range). Every
  canonical adult band therefore does a direct constant-value lookup into whichever Tabelraamat
  band contains it — no averaging needed. 25-29 through 45-49 look up "25-50"; 50-54 through
  65-69 look up "51-70" (note the boundary mismatch: Tabelraamat's band ends at 70, so age 50-54
  spans the 25-50/51-70 boundary — resolved by rounding to the nearer band, 51-70, since it's a
  4/5-year overlap either way and the two adjacent Tabelraamat values are close); 70-74 and 75+
  both look up ">70".
- **Children (2-5, 6-9, 10-13, 14-17)**: messier, since Table 4 mixes single years (1,2,3) with
  bands (4-6, 7-10, 11-14, 15-17) that don't align with RTU011's bands at all. Resolution: build a
  population-weighted average of whichever Table 4 single-year/band values overlap each canonical
  band (e.g. canonical "2-5" = weighted average of age-2, age-3, and the 4-6 band's value, using
  RV021 single-year-equivalent population as weights, consistent with the same uniform-within-bin
  assumption used for the population proration above). This is a real computation to do in Phase 3,
  not a data gap — flagging it here so it isn't rediscovered as a surprise then.

## Physical activity level (PAL): no population distribution exists

Tabelraamat gives three PAL tiers (sedentary 1.4 / moderate 1.6 / active 1.8) per age-sex cell, but
no Estonian source gives the population's actual distribution *across* those tiers — Statistikaamet
does not publish an activity-level census, and none of TAI's tables cross-tabulate age/sex with
self-reported activity level at a level suitable for population weighting.

Decision: rather than inventing a distribution, this model uses **PAL = moderate as the single
national-aggregate default** for every headline requirement figure, and reserves sedentary/active
as an explicit sensitivity range (i.e. "the recommended-intake total could be X% lower if the whole
population were sedentary, or Y% higher if fully active") rather than a population split. This is
documented in `data/processed/pal_levels.csv`'s `usage_note` column and must be restated wherever a
kcal-requirement figure appears in the dashboard, so a reader never mistakes "moderate" for a
measured average.

## Sex

Both RV021 and RTU011 report male/female. RTU011 also publishes a `total` (both sexes combined)
column — kept in the raw data for QA cross-checks (e.g. "does male+female-weighted average match
the published total row") but not part of the canonical grid, since the demographic model needs
sex-specific weights throughout.

## Output files

- `data/processed/population_canonical_grid.csv` — 32 rows (16 age bands x 2 sex), each with the
  reconciled population count and a `source_note` documenting exactly how it was derived (exact
  match / prorated / aggregated-with-proxy). Total across all rows: 1,339,785 — reconciles exactly
  against RV021's national total of 1,360,745 once the 20,960 excluded infants (ages 0-1) are added
  back (1,339,785 + 20,960 = 1,360,745). This identity is a working consistency check: any future
  edit to this grid should preserve it.
- `data/processed/pal_levels.csv` — the 3 PAL tiers, their multipliers, and the usage-note decision
  above.
