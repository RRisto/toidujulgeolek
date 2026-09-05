# EAT-Lancet to TAI Mass Normalization Design

## Objective

Make Scenario C (EAT-Lancet 2019) and Scenario C2 (EAT-Lancet 2025) comparable with Scenario A
(RTU actual consumption) and Scenario B (TAI recommendations) anywhere the project uses grams or
tonnes. Preserve every published source value and expose the conversion into the project's common
edible, ready-to-eat food basis rather than silently overwriting source units.

## Scope

This correction covers the EAT-Lancet crosswalks, Scenario C/C2 demand, derived self-sufficiency,
critical-dependency flags, land-reallocation analysis, English and Estonian dashboard data and
HTML, the English and Estonian diet treemaps, and methodology/project documentation. Scenario A
and Scenario B source calculations remain unchanged.

Primary-commodity-equivalent conversion is not introduced in this change. The existing
self-sufficiency model estimates Scenario B/C/C2 by scaling the Scenario A percentage with the
ratio of scenario demand masses. This change makes that ratio use one common edible-equivalent
basis. A future primary-commodity layer would require separate milling, cooking, carcass, and
processing yields and should not be implied by this correction.

## Source Corrections

The EAT-Lancet reference tables will be represented faithfully before normalization.

- EAT-Lancet 2019 remains calibrated to 2,500 kcal/day. Its source values include 232 g whole
  grains, 75 g dry legumes, 50 g nuts, and 31 g added sugar.
- EAT-Lancet 2025 remains calibrated to approximately 2,400 kcal/day. Correct source values are
  210 g dry whole grains, 75 g dry legumes, 50 g tree nuts and peanuts, and 30 g added/free sugar.
  The existing 6 g sugar value is erroneous: 6 g is the palm/coconut-oil target. The remaining
  animal-fat target is 5 g, not 6 g.
- The known 50 g nut quantity is included in the combined `Nuts+Seeds,cocoa (combined)` project
  row. The row note will explicitly state that it contains the specified nuts only and does not
  manufacture an unreported seed/cocoa allowance.
- Honey remains a production subitem for self-sufficiency reporting but is not added to any diet's
  total mass. It is already part of the broader sweets/sugar demand and adding it as another leaf
  is double-counting.

## Common-Basis Contract

Every EAT crosswalk row will carry these fields:

- `source_g_per_day`: published EAT-Lancet grams at its native reference energy.
- `source_weight_basis`: concise basis such as `dry`, `milk_equivalent`, or
  `edible_source_weight`.
- `source_kcal_per_day`: published reference energy for the food group.
- `normalized_g_per_day_at_reference_kcal`: source energy expressed using the same representative
  food mass per kcal used by the TAI model.
- `scaled_normalized_g_per_day_estonia`: normalized mass multiplied by the existing Estonia
  demographic energy factor.
- `normalization_method`: human-readable description of the conversion and assumptions.

The existing `scaled_g_per_day_estonia` field will be retired from Scenario C/C2 consumers so a
source-basis value cannot accidentally be used as normalized tonnage.

## Normalization Algorithm

Normalization preserves the published EAT-Lancet calories for each category, not its native mass.
For each destination subitem:

```text
normalized_g_at_reference = source_kcal * TAI_representative_g_per_portion / TAI_kcal_per_portion
scaled_normalized_g_estonia = normalized_g_at_reference * Estonia_average_kcal / EAT_reference_kcal
```

TAI kcal/portion values come from `tabelraamat_table13_portions.csv`; representative gram values
come from `portion_gram_representative.csv`. This makes dry grain, dry legumes, milk equivalents,
and other EAT categories comparable to the exact food representatives already used to turn TAI
portions into Scenario B tonnes.

Whole grains need one additional step because the project has two destination rows. EAT whole-grain
calories will be divided between bread and porridge/pasta/rice using their Scenario B energy shares,
not their mass shares. Each calorie allocation is then converted using that destination's own TAI
grams-per-portion value. This replaces the current invalid split of dry-grain grams using a ratio
derived from prepared-food masses.

For the combined fruit/berries and nuts/seeds rows, the TAI representative grams per kcal will be
calculated from the Scenario B component mix:

```text
combined_g_per_kcal = sum(component recommended grams) / sum(component implied kcal)
```

This preserves the project's documented TAI component mix without inventing a new split.

## Data Flow

One shared Python module will own source constants, basis metadata, TAI-equivalent conversion, and
CSV writing for both EAT editions. The two scenario entry-point scripts will call that module so
the 2019 and 2025 implementations cannot drift again.

Generated flow:

```text
EAT source constants + TAI portion tables
    -> EAT crosswalk CSVs with source and normalized fields
    -> scenario_comparison.csv C/C2 demand and self-sufficiency
    -> critical_dependency_flags.csv
    -> land_reallocation_scenario.csv
    -> dashboard JSON (English, then localized Estonian)
    -> dashboard HTML and diet treemaps
```

Treemap box area will continue to show within-scenario proportions, but those proportions will be
calculated from normalized edible-equivalent grams. Tooltips and notes will label the basis. Honey
will not be emitted as a separate diet-mass leaf. A calorie-proportion view is not added in this
change because the dashboard currently carries no complete per-item calorie dataset for Scenarios A
and B; the normalization metadata prevents the existing mass view from overstating comparability.

## Validation and Failure Handling

Automated tests will verify:

- the 2019 and 2025 source constants, especially 2025 sugar = 30 g, palm/coconut oil = 6 g, and
  lard/tallow/butter = 5 g;
- nuts are retained as a known partial combined-row quantity;
- dry whole-grain and legume normalized masses exceed their dry source masses;
- whole-grain calories are conserved across the bread and porridge split;
- every normalized row conserves its source calories within rounding tolerance;
- CSV headers distinguish source and normalized fields;
- Scenario C/C2 demand tonnes use normalized rather than source grams;
- treemap totals equal the sum of displayed, non-duplicated leaves and exclude honey;
- all generated JSON parses, inline JavaScript passes syntax checking, and both language builds
  complete.

The generator will fail clearly if a required TAI representative gram value, kcal-per-portion
value, source calorie value, or destination mapping is absent. It will not silently fall back to
source grams.

## Documentation

Methodology and phase notes will replace the claim that the earlier total-mass comparison was a
fair direct comparison. They will document the original basis mismatch, the corrected 2025 source
values, the normalization formula, the remaining representative-food uncertainty, and before/after
Scenario C/C2 totals and self-sufficiency results. Existing historical notes may retain old values
only when explicitly marked as superseded.

## Acceptance Criteria

- Source and normalized grams coexist and have explicit bases.
- All Scenario C/C2 gram, tonne, self-sufficiency, dependency, land, dashboard, and treemap outputs
  are regenerated from normalized edible-equivalent grams.
- Scenario A/B numerical inputs remain unchanged.
- Nuts are included, 2025 sugar is 30 g, and honey is not double-counted in diet totals.
- Tests and build checks pass from the branch with no unrelated user files staged or overwritten.
