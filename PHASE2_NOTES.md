# Phase 2 notes — taxonomy & demographic grid

Phase 2 of PLAN.md Section 7: build the food-group crosswalk and the age/sex/activity reference
grid that Phases 3 (requirement model) and 4 (consumption model) will both key off. Status: done.

## What Phase 2 delivered

1. **Two data gaps filled** (carried over from Phase 1's open items):
   - Fish self-sufficiency: no Statistikaamet PM-series balance table exists for fish at all. Found
     and used a dedicated Jan 2026 Ministry-commissioned study instead —
     `data/raw/agri_ee/fish_consumption_2026_extract.md`. Confirms the strategy doc's ">200%"
     figure but adds the crucial nuance that ~85% of that supply is exported, so headline
     self-sufficiency massively overstates what actually reaches Estonian plates.
   - Partial nuts/seeds/oils coverage: pulled `PM37_oilseeds_2024.csv` (rapeseed/sunflower/soy —
     Estonia's only real domestic oil crop is rapeseed, ~96,000t/year, mostly crushed
     domestically) and `PM29_honey_2024.csv` (98% self-sufficient, minor category). Tree nuts,
     culinary seeds, and cocoa remain a genuine gap — no Estonian production of any of them at
     meaningful scale, and no source publishes a balance table to confirm a number.

2. **Food-group taxonomy crosswalk** — `data/crosswalk/food_group_crosswalk.csv` (+ README in the
   same folder). Maps all 6 TAI toidupüramiid groups and their sub-items to RTU011 consumption
   categories and Statistikaamet/other production sources. Documents 6 distinct mismatch types
   rather than papering over them: a legume gap (tracked nowhere), fruit/berry inseparability (no
   Estonian source splits them), RTU011 bundling poultry with red meat and offal into one figure,
   no bread-specific balance (only raw wheat/rye), no nut/seed/cocoa data, no sugar/sweets balance.
   Each row is tagged with a `match_quality` (exact / aggregate / needs_split / needs_conversion /
   gap) so Phase 3+ can tell a measured figure from an estimated or assumed one at a glance.

3. **Canonical demographic grid** — the harder half of Phase 2. Three sources
   (RV021 population, RTU011 consumption, Tabelraamat requirements) each use different age-band
   schemes; reconciling them is documented in full in `data/crosswalk/demographic_grid.md`.
   Summary of the decisions made there:
   - RTU011's age bands were chosen as canonical (the only source with real consumption data —
     everything else maps onto it, not the reverse).
   - Population was reconciled from RV021's finer 5-year bins via uniform-within-bin proration
     (documented per-band in the design doc) — this is a real disaggregation, not an estimate from
     a coarser source, though the "uniform within a 5-year bin" assumption is itself a stated
     simplification.
   - Two population gaps needed explicit handling: ages 0-1 (infants, 20,960 people / 1.54% of the
     population) are excluded from v1 scope entirely, since infant feeding doesn't fit the
     toidupüramiid framework this model is built around; ages 75+ (135,615 people / ~10% of the
     population) are kept in scope but their consumption is modelled as a proxy using RTU011's
     70-74 band, since RTU011 itself has no data past 74 and excluding 10% of the population would
     badly distort a national food-security conclusion.
   - Physical activity level (PAL) has no Estonian population-distribution data at all — no source
     cross-tabulates age/sex against self-reported activity level. Rather than inventing a split,
     the model uses PAL=moderate as the single national-aggregate default and keeps
     sedentary/active as an explicit sensitivity range, not a population weighting. This must be
     restated wherever a requirement figure appears in the eventual dashboard.
   - The Tabelraamat → RTU011 lookup method (constant-value for adults, population-weighted
     average across single ages for children) is fixed in the design doc so Phase 3 has no open
     design questions left, even though the actual kcal-requirement numbers aren't computed yet
     — that's Phase 3's job.

   Output tables: `data/processed/population_canonical_grid.csv` (32 rows: 16 age bands x 2 sex,
   each with a `source_note` documenting exactly how it was derived) and
   `data/processed/pal_levels.csv` (the 3 PAL tiers and the moderate-as-default decision).
   Consistency check: 1,339,785 (in-scope population) + 20,960 (excluded infants) = 1,360,745
   (RV021's published national total) — exact, no residual, since every RV021 person was
   accounted for in either the canonical grid or the documented exclusion.

## Confirmed open items carried into Phase 3+

- The children's kcal-requirement mapping (Table 4's single-year/band values → RTU011's 2-5/6-9/
  10-13/14-17 bands) is a real computation still to do, not a data gap — method is fixed, numbers
  aren't computed yet.
- Milk-equivalent aggregation (9 PM47 dairy lines → 1 figure) and oilseed-to-refined-oil yield
  conversion, both flagged in Phase 1/the crosswalk notes, remain Phase 3 tasks.
- Poultry/red-meat/offal split from RTU011's single bundled meat figure — proposed method (split by
  PM42's per-capita consumption shares) is documented in the crosswalk but not yet applied.
- The men >70 row in Tabelraamat Table 5 was not fully captured by the PDF-extraction pass and
  should be re-checked against the source PDF before Phase 3 needs it.
- Legumes, tree nuts, culinary seeds/cocoa, and sugar/sweets remain complete data gaps with no
  Estonian balance table found anywhere — Phase 3/8 should attempt a Eurostat or foreign-trade
  cross-check before the dashboard states any number for these, even a rough one.
