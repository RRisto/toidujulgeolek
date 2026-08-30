# Phase 4 consumption-model sanity check

Cross-checks for the actual-consumption model (`consumption_model_national.csv`,
`consumption_grams_by_grid_cell.csv`).

## 1. Parse-correctness QA (Task 21, done before any mapping)

Two checks against the raw RTU011 file itself, both passing within normal survey rounding:
- Every top-level RTU011 group's `total/total` value ≈ the sum of its `..`-prefixed sub-groups
  (largest gap: starchy foods, 282 vs 295 = 13g, likely original-survey rounding, not a parse bug).
- Every category's published `total` sex value ≈ the simple average of its `male`/`female` values
  (all matched within 0.5-1.5g), confirming the file was parsed into the right cells.

## 2. Population-weighted actual consumption vs. Phase 1's raw-survey validation

Phase 1 spot-checked two categories directly off RTU011's own (unweighted) national total row.
This phase's population-weighted figures land close, as expected (small shift because the
canonical grid's demographic weighting differs slightly from the survey's raw sex/age split):
- Dairy: 296.4 g/capita/day here vs. 300 g/day in the RTU011 total row (Phase 1).
- Vegetables: 135.7 g/capita/day here vs. 137 g/day (Phase 1).

## 3. Meat: survey-based (RTU011) vs. supply-based (Statistikaamet PM42) — a known, expected gap

Poultry + red meat sum to **39.3 kg/capita/year** here (13.5 kg poultry + 25.8 kg red meat),
against Statistikaamet PM42's supply-side per-capita figure of **80.4 kg/year**. This ~2x gap
matches the same pattern already documented for vegetables in Phase 1/2 (RTU011 survey-recall
consumption vs. Statistikaamet balance-sheet apparent consumption): balance-sheet "human
consumption" figures are a residual (production + trade − feed − waste − industrial use) that
includes food eaten away from home, processing losses attributed to the wrong stage, and generally
runs higher than what a dietary recall survey captures. The PM42 numbers were used here only for
their *relative shares* (poultry vs. red meat vs. offal, as a percentage split) to divide RTU011's
bundled meat figure — that ratio is far more robust to this gap than an absolute level would be,
since both the poultry and red-meat portions of PM42 are inflated by roughly the same structural
factors. This is flagged, not corrected — reconciling survey-based and supply-based consumption
levels is a Phase 5+ question, not something to paper over here.

## 4. Implied national average daily energy intake: survey-based figure is ~74% of the requirement-side figure

Converting the actual-consumption model back to kcal (same method as Phase 3's own cross-check)
gives **~1,655 kcal/capita/day** from RTU011-derived consumption, against Phase 3's
population-weighted *requirement* figure of 2,234 kcal/capita/day — a ratio of about 0.74.

This gap is expected, not a modelling error: dietary recall/frequency surveys are well known in
the nutrition literature to under-report actual intake relative to true consumption (commonly
cited underreporting margins run in the 15-30% range), and RTU011's 16-category taxonomy doesn't
capture everything a person eats — no beverage, alcohol, or "other/mixed dish" category exists in
either this model's requirement or consumption side, so that specific omission is symmetric, but
general recall-survey underreporting is not. It is also a 2014 survey (see PHASE1_NOTES.md), so
some of the gap could reflect a decade of dietary change rather than survey methodology alone —
this model cannot separate those two explanations with the data on hand. The over/under-consumption
*ratios per food group* (the actual Phase 4 deliverable) are far more informative than this
aggregate energy comparison, since a roughly uniform underreporting bias across categories would
shift every ratio in the same direction without changing which categories are furthest off target —
and the ratios found (red meat 3.5x over, sweets 3.1x over, vegetables 0.28x, nuts/seeds 0.09x) are
too large and too food-group-specific to be explained by a uniform survey bias alone.
