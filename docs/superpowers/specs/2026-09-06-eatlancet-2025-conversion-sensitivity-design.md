# EAT-Lancet 2025 conversion sensitivity analysis design

## Purpose

Quantify how the project's conversion of EAT-Lancet 2025 energy targets into
TAI-representative edible mass affects food-group demand and self-sufficiency.
The analysis must distinguish uncertainty introduced by the conversion from
uncertainty in EAT-Lancet's published energy targets, Estonia's production, or
the population energy reference.

This first version is a standalone calculation. It does not change Scenario
C.2, dashboard data, or the published dashboard.

## Scope

The analysis covers EAT-Lancet 2025 only and reports results by the project's
food-group subitem. It holds constant:

- EAT-Lancet 2025 source grams, energy, and reference intake;
- Estonia's 2,234.358 kcal population reference;
- Scenario A demand and self-sufficiency inputs;
- domestic production;
- the existing taxonomy and direct EAT-to-TAI mappings.

It varies only choices used to express source energy as TAI-basis edible mass:

- the representative TAI portion mass for a mapped food category;
- the mix within a combined TAI category; and
- the bread-versus-porridge allocation of EAT-Lancet whole-grain energy.

## Method

Use a deterministic one-at-a-time sensitivity analysis. For each uncertain
conversion input, keep every other input at its current baseline and recompute
the EAT-Lancet 2025 crosswalk. Candidate values must come from TAI Table 16 or
from an explicit allocation bound; arbitrary percentage shocks are not used.

The baseline is the current `build_crosswalk("2025", root)` result. Each
food-group row receives the minimum and maximum result observed across all
applicable one-at-a-time variants, including the baseline.

For a normalized row:

`normalized grams = EAT source kcal × TAI representative grams per kcal`

`Estonia grams = normalized grams × 2,234.358 / 2,400`

`annual demand tonnes = Estonia grams × population × 365 / 1e6`

`sensitivity self-sufficiency = Scenario A self-sufficiency × Scenario A demand / sensitivity demand`

If the baseline Scenario C.2 self-sufficiency is unresolved, the sensitivity
result remains unresolved rather than inventing a point estimate.

## Conversion variants

The script reads the detailed TAI Table 16 extract and constructs documented
candidate portion masses for each mapped destination. Variants are limited to
foods that are credible members of that destination category.

- Bread: the published bread/baked-goods portion range.
- Porridge/pasta/rice/grain products: the listed cooked staple forms.
- Whole grains: allocation bounds from all bread to all porridge, plus the
  current TAI-energy-share baseline. These are allocation sensitivities, not
  claims about likely menus.
- Potato/sweet potato: listed potato and sweet-potato forms.
- Dairy: the six dairy subtypes represented by the current baseline average.
- Nuts/seeds: listed nut, seed, and cocoa forms, preserving the combined row.
- Oils/fats/spreads: listed high- and lower-fat spread forms that represent an
  equal-energy TAI portion.
- Fish: the listed fish fat tiers and other fish forms.
- Poultry: the listed poultry cut/skin variants.
- Red meat: forms compatible with the fresh red-meat production category;
  processed products are excluded unless they can be mapped to the same
  production basis without changing the question.
- Sweets: solid sweet forms compatible with the aggregate sugar proxy;
  sweetened beverages are excluded because beverage water mass would turn the
  test into a product-form comparison rather than a food-energy conversion.
- Single-value direct mappings, including vegetables and eggs, are marked as
  unchanged.

Every candidate records its TAI source label and value so the extrema remain
auditable. Missing or ambiguous mappings fail explicitly instead of silently
falling back to the baseline.

## Outputs

Create a standalone CSV under `data/processed/` with one row per EAT-Lancet
2025 destination subitem and at least these fields:

- pyramid group and subitem;
- baseline, minimum, and maximum converted grams per day;
- baseline, minimum, and maximum annual demand tonnes;
- baseline, minimum, and maximum self-sufficiency percentages where resolved;
- absolute and relative spread from the baseline;
- variant labels producing the minimum and maximum;
- whether the row changes classification at the 50% or 100% thresholds;
- a concise method note.

Create a short Estonian Markdown report beside the project documentation. It
summarizes the largest demand and self-sufficiency movements, identifies any
threshold crossings, and states which qualitative conclusions survive all
tested variants. It must describe the output as a deterministic sensitivity
range, not a confidence interval or probability distribution.

## Code structure

Add a focused analysis module that consumes the existing normalization module
rather than duplicating its source data or formulas. Extend normalization with
the smallest explicit input seam needed to supply alternative densities and
whole-grain allocations while keeping today's default output unchanged.

The analysis flow is:

1. load baseline EAT-Lancet 2025 crosswalk;
2. derive named conversion candidates from TAI Table 16;
3. recompute one input at a time;
4. translate grams into annual demand and self-sufficiency;
5. aggregate row-level minima and maxima;
6. write the CSV and Estonian report.

No dashboard generator or published HTML is touched in this phase.

## Validation

Tests must demonstrate:

- the default crosswalk is byte-for-byte or value-for-value unchanged;
- every sensitivity candidate is traceable to a TAI row or an explicit grain
  allocation endpoint;
- single-value mappings have zero spread;
- lower demand produces equal or higher self-sufficiency when production is
  fixed, and vice versa;
- row minima and maxima include the baseline and are ordered correctly;
- unresolved baseline self-sufficiency remains unresolved;
- the generated CSV has every 2025 crosswalk row exactly once;
- the report's numerical statements are derived from the generated results.

Run the existing normalization test suite plus new sensitivity tests and
regenerate the standalone outputs from a clean invocation.

## Interpretation limits

The range answers how much the results move under documented alternative TAI
representative compositions. It does not cover uncertainty in dietary energy
needs, production volumes, food losses, trade behavior, or the EAT-Lancet
targets themselves. One-at-a-time extrema also do not describe the probability
of a result and must not be labelled as confidence intervals.
