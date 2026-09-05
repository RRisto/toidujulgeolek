# Phase 21 notes — EAT-Lancet/TAI mass-basis normalization

## Trigger and root cause

The treemap showed TAI above 2,000 g/person/day while both EAT-Lancet diets appeared around
1,100–1,200 g/day. The totals were arithmetically reproducible, but the comparison contract was
wrong. TAI Table 16 uses edible/ready-to-eat portion weights; EAT-Lancet reports important foods,
including whole grains and legumes, as dry/uncooked source weights. Directly summing and comparing
those grams made EAT-Lancet look artificially light.

Two smaller implementation errors amplified the problem:

- EAT-Lancet 2025 added/free sugar is 30 g/day (115 kcal), not 6 g/day. Six grams is the
  palm/coconut-oil line; lard/tallow/butter is 5 g/day.
- Both crosswalks knew the 50 g/day nuts target but left the combined nuts/seeds/cocoa row blank.
  The corrected model retains the known nuts mass and labels seeds/cocoa as unspecified.

Honey was also emitted as its own C/C2 leaf even though it was already included in aggregate
sweets/sugar. C/C2 Honey demand is now blank to prevent double-counting.

## Conversion contract

Every EAT row retains `source_g_per_day`, `source_weight_basis`, and `source_kcal_per_day`.
Comparison mass is calculated as:

`normalized_g_at_reference = source_kcal × TAI_representative_g_per_portion / TAI_kcal_per_portion`

Then:

`scaled_normalized_g_estonia = normalized_g_at_reference × 2234.358 / edition_reference_kcal`

The reference is 2,500 kcal for 2019 and 2,400 kcal for 2025. Whole-grain source mass and energy
are split between bread and porridge using their TAI implied-energy shares. Combined fruit/berries
and nuts/seeds use the TAI component mix. These are edible-equivalent comparison masses, not
primary-commodity equivalents; milling, carcass, cooking-yield, and loss factors remain out of
scope.

## Before and after

| Scenario | Old treemap mass | Corrected comparable mass | Basis |
|---|---:|---:|---|
| A — measured diet | 1,276.7 g/day (included duplicate Honey) | 1,273.6 g/day | measured edible mass |
| B — TAI | 2,143.2 g/day (included duplicate Honey) | 2,141.9 g/day | TAI edible/ready-to-eat |
| C — EAT 2019 | 1,139.2 g/day | 1,568.7 g/day | TAI-basis edible equivalent |
| C2 — EAT 2025 | 1,147.4 g/day | 1,666.9 g/day | TAI-basis edible equivalent |

For traceability, the unnormalized published source totals represented in the corrected crosswalks
are 1,323.8 g/day (2019) and 1,306.0 g/day (2025). They are valid source totals but are not used as
TAI-comparable demand mass.

The tonnage-weighted self-sufficiency headlines changed from C 157.0% / C2 156.8% to **C 140.2% /
C2 129.4%**. A remains 106.4% and B remains 77.0%. The land-reallocation illustration changed to:

| Scenario | Feed no longer needed | Cropland no longer needed | Illustrative vegetables |
|---|---:|---:|---:|
| C | 196.9 kt | 59,367 ha | 1,775,073 t |
| C2 | 173.6 kt | 52,358 ha | 1,565,504 t |

These land values retain all Phase 15 behavioral and yield caveats.

## Implementation and verification

- Shared engine: `src/eatlancet_normalization.py`
- Crosswalks: `data/crosswalk/eatlancet_crosswalk.csv` and
  `data/crosswalk/eatlancet2025_crosswalk.csv`
- Demand propagation: `src/update_scenario_c.py`, `src/update_scenario_c2.py`
- Deterministic treemap data: `build_treemap/build_treemap_data.py`
- Regression tests: `tests/test_eatlancet_normalization.py`

The tests verify primary source values, dry-to-edible mass behavior, whole-grain energy
conservation, C/C2 demand propagation, exact preservation of all Scenario A/B values, canonical
population 1,339,785, exact treemap leaf totals, and Honey exclusion. Dashboard/treemap JSON was
parsed and embedded JavaScript was syntax-checked in all English and Estonian builds.

Branch: `codex/normalize-eat-tai-mass`. Historical Phase 10, 14, 15, and 20 notes retain old values
where useful but mark them as superseded by this phase.
