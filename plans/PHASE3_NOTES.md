# Phase 3 notes — demographic nutritional-requirement model

Phase 3 of PLAN.md Section 7 / Section 5.1: build the population-weighted *recommended* demand
per food group — "if everyone ate exactly as TAI recommends, weighted by who Estonia's population
actually is." Status: done.

## What Phase 3 delivered

1. **Filled two remaining Tabelraamat extraction gaps**, both required before any computation
   could start:
   - The missing men >70 kcal row in Table 5 (2,100 / 2,400 / 2,700 kcal for sedentary/moderate/
     active) — confirmed via a targeted WebFetch re-pull.
   - Full gram-weight data (Tables 16.1-16.6) for every pyramid food group and sub-item — this
     required a different retrieval method than Phase 1/2 used, since Chrome's native PDF viewer
     is unreachable by browser automation and WebFetch's PDF-to-text conversion silently truncates
     this particular document somewhere around page 26-29 (below where Table 16 lives, on page
     36). Resolved by rendering the PDF through Google's Docs viewer (`docs.google.com/gview?url=`)
     in a real Chrome tab — a normal web page, readable via screenshots — and reading the tables
     directly off the rendered pages. Full table now at
     `data/raw/tai/tabelraamat_table16_portion_grams.csv` (78 rows).

2. **kcal-requirement-per-capita lookup** — `data/processed/kcal_requirement_by_grid_cell.csv`
   (32 grid cells x 3 PAL = 96 rows). Adults (18-24 through 75+) are a direct constant lookup into
   Table 5's four bands, per the method fixed in `demographic_grid.md`. Children (2-5 through
   14-17) are built by averaging Table 4's single-year and banded values across every single age
   in the canonical band, linearly interpolating within any band Table 4 gives as a range —
   documented as using equal weight per single age, since Statistikaamet doesn't publish
   single-year population to weight it more precisely.

3. **Portion mapping** — `data/processed/tabelraamat_table13_portions.csv` (the full Table 13.1/
   13.2 grid, 20 group/sub-item rows x 14 energy levels) and
   `data/processed/portions_by_grid_cell.csv` (each of the 96 grid-cell x PAL rows joined to its
   recommended portions/day per food group). Method: each grid cell's daily kcal requirement is
   rounded to the *nearest* available 200-kcal level in Table 13.1/13.2 (ties round up, favouring
   not under-stating recommended intake) rather than interpolated — the source table is itself a
   step function of ranges, not a continuous formula, so rounding is more honest than manufacturing
   false precision via interpolation. One real gap: Table 13.1's "grain products & potatoes" total
   at the 2200-kcal column was not captured cleanly by the original extraction pass; it's filled
   here as the sum of that column's own sub-item ranges (8-11 portions), flagged in the data with a
   note rather than silently presented as a sourced figure.

4. **Grams/day and national annual demand** — `data/crosswalk/portion_gram_representative.csv`
   (the necessary bridge table: Table 13's portions don't specify *which* specific food, so a
   representative gram-weight had to be chosen per sub-item from Table 16's several options —
   every choice and its rationale is documented per row, e.g. fish uses an unweighted average
   across the four fat-content tiers since no Estonian data says which tier dominates actual
   consumption) and `data/processed/requirement_model_national.csv` — the core Phase 3 deliverable:
   national recommended demand per food group, in tonnes/year, at PAL=moderate (the documented
   national-aggregate default from `demographic_grid.md`).

   Headline figures (population-weighted, ages 2+, 1,339,785 people): dairy 394,000 t/year (806 g/
   capita/day) is the single largest recommended category by mass; the vegetables+fruit+berries+
   legumes group totals 802 g/capita/day (~393,000 t/year combined) — both driven by TAI's
   guidance being well above what Section 5.2 (Phase 4) will likely find people actually eat,
   which is the whole point of building this model.

5. **Sanity checkpoint (PLAN.md Section 7 item 3)** — `data/processed/SANITY_CHECK_phase3.md`.
   Two independent derivations of national average daily energy — (a) the age/sex/PAL requirement
   grid directly, and (b) summing the final food-group demand table back into kcal via each
   sub-item's own kcal/portion — land within 2% of each other (2,234 vs 2,282 kcal/capita/day),
   which is expected-sized rounding/approximation noise given the nearest-200-kcal rounding and the
   representative-gram-weight choices, not a modelling error. Full macronutrient-level validation
   against Table 6 was not attempted here — it needs per-food-item nutrient-composition data not
   yet sourced, and PLAN.md Section 5.8 already scopes that to Phase 8.

## Confirmed open items carried into Phase 4+

- Every representative-gram-weight and portion-point-estimate choice documented in
  `portion_gram_representative.csv` and `portions_by_grid_cell.csv` is a stated simplification,
  not a measurement — Phase 4's consumption model and Phase 5's supply model should carry these
  same caveats forward rather than treat Phase 3's tonnage figures as more precise than they are.
- The 2200-kcal grain/potato total gap (filled by summing sub-items) should be re-verified against
  the source PDF if a cleaner extraction pass ever becomes worthwhile.
- Macronutrient-level (%E protein/fat/carb) validation against Table 6 remains deferred to Phase 8.
- This model represents *recommended demand assuming PAL=moderate nationally* — the sedentary/
  active bounds are computed and available in `kcal_requirement_by_grid_cell.csv` and
  `portions_by_grid_cell.csv` for a future sensitivity-range view, but were not carried through to
  `requirement_model_national.csv`'s headline figures.
