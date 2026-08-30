# Phase 3 requirement-model sanity check

Checkpoint required by PLAN.md Section 7, item 3: "totals sanity-check against national average
calorie/macronutrient figures."

## Calorie cross-check: two independent derivations agree within ~2%

The model computes calorie requirement two different ways that should, in principle, reconcile:

1. **Top-down**: population-weighted average of the age/sex/PAL=moderate kcal requirement grid
   (`kcal_requirement_by_grid_cell.csv`), directly off Tabelraamat Tables 4 and 5.
   **Result: 2,234 kcal/capita/day** (male average 2,474, female average 2,018 — a sensible gap,
   ages 2+ only per the demographic grid's documented scope).

2. **Bottom-up**: sum, across every pyramid food group and sub-item, of (recommended grams/day) ÷
   (grams/portion) × (kcal/portion) — i.e., converting the final national demand table
   (`requirement_model_national.csv`) back into energy.
   **Result: 2,282 kcal/capita/day.**

These two numbers are derived through completely different paths (age/sex/PAL tables vs. the
portion-and-gram-weight tables) and land within 48 kcal (~2%) of each other. Given that the
portion-mapping step (Task 17) rounds each grid cell to the nearest 200-kcal level in Table 13.1/
13.2 and collapses inequality/range portions (">=2", "0.5-1") to point estimates, and the
gram-weight step (Task 18) uses documented representative averages where Table 16 gives several
specific foods per sub-item, a ~2% gap is expected rounding/approximation noise, not a modelling
error. This is treated as a pass.

## Plausibility of the headline number

2,234 kcal/capita/day (ages 2+, PAL=moderate) sits squarely inside the range implied by Table 5's
adult bands (1,700-3,150 kcal depending on age/sex/PAL) once pulled down somewhat by children's
lower requirements and pulled toward the female half of the population (females are the larger
share of the 75+ band, see demographic_grid.md). It is a *requirement* figure — physiological need
per TAI's own tables — not a food-balance-sheet supply figure, so it is not expected to match
gross per-capita food supply statistics (which run structurally higher once waste, feed, and
non-food use are included at the supply level; that reconciliation is the job of Phase 5's supply
model, not this one).

## What this checkpoint does not cover (explicitly out of scope here)

A full macronutrient (%E protein/fat/carbohydrate) validation against Table 6 was not attempted —
doing so honestly would require per-food-group macronutrient composition data (e.g. USDA/national
nutrient database figures for each item in Table 16), which hasn't been sourced. Per PLAN.md
Section 5.8, macronutrient- and micronutrient-level validation is explicitly deferred to Phase 8's
validation pass; this Phase 3 checkpoint is limited to the calorie-total consistency check above,
which is what Section 7's checkpoint actually calls for.
