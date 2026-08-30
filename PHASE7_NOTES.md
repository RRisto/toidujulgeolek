# Phase 7 — Scenario engine & critical-dependency flagging

Implements PLAN.md sections 5.6 (scenario engine), 5.7 (critical-dependency flagging), and
touches 5.8 (nutritional-adequacy sanity check) qualitatively. Builds two new output tables on
top of Phases 3–6: `data/processed/scenario_comparison.csv` and
`data/processed/critical_dependency_flags.csv`.

## 1. Scenario engine (5.6)

Two scenarios, both run against the *same, unchanged* domestic production:

- **Scenario A — status quo.** Demand = actual current consumption, taken from Phase 4's
  demographic bottom-up model (`consumption_model_national.csv`). Self-sufficiency = the Phase 5
  headline figure (`self_sufficiency_model.csv`), which is itself production ÷ domestic-use on
  the official Statistikaamet/strategy-document basis.
- **Scenario B — TAI-recommended diet.** Demand = recommended consumption, taken from Phase 3's
  model (`requirement_model_national.csv`). Production is held fixed at the same level as
  Scenario A.

**Method — ratio scaling, not a re-derived balance sheet.** Since production is fixed between the
two scenarios and self-sufficiency = production ÷ demand, the Scenario B figure for each item is
computed as:

```
scenario_B_pct = scenario_A_headline_pct × (scenario_A_demand_tonnes / scenario_B_demand_tonnes)
```

This is algebraically exact *if* the Phase 5 headline percentage's implicit demand denominator is
proportionate to the Phase 4 bottom-up consumption tonnage used here as `scenario_A_demand`. In
practice these are two different numbers built from different sources (Phase 5's headline uses
official PM-series domestic-use figures; `scenario_A_demand` here uses the RTU011-based
demographic model) — a known, already-documented gap from earlier phases (RTU011 is a 2014
survey; PM-series figures are 2024). Scaling by the RTU-model ratio therefore isolates the
*diet-composition effect* cleanly, but the resulting Scenario B number should be read as an
illustrative shift from the Scenario A headline, not as a new, independently-measured
self-sufficiency figure. This is flagged in every row's `note` field, not just here.

**Household-waste lever.** Layered on top of Scenario A (composes the same way on Scenario B) per
5.6's optional toggle, using Phase 6's waste model. Since `required_production_inflator` relates
required production to consumption for a group, and cutting household waste lowers that inflator
without needing more production, the lever is applied the same way as the scenario scaling:

```
pct_with_waste_cut = headline_pct × (inflator_current / inflator_after_cut)
```

Available for the 10 food groups Phase 6's waste model covers (not legumes, nuts/seeds, oils, or
sweets — no SEI category-level detail exists for those). Effect sizes are small in percentage-point
terms (e.g. bread 332.5% → 342.0%/352.0% at a 25%/50% household-waste cut) because cutting waste
lowers the amount that needs to flow through the system, not the production side — it's a modest
efficiency gain layered on the existing self-sufficiency picture, exactly as the plan frames it,
not a lever that closes a structural gap on its own.

## 2. Taxonomy reconciliation

The three input tables use three different levels of aggregation (self-sufficiency: 18 rows,
oils split by crop, sweets split into raw-sugar/manufactured; requirement: 16 rows, fruit and
berries reported separately; consumption: 14 rows, the most aggregated). `scenario_comparison.csv`
reconciles these to 16 rows:

- Fruits+Berries: requirement's separate Fruits and Berries rows are summed to match the
  combined figure used elsewhere.
- Nuts+Seeds,cocoa: same summing approach; both sub-items are assumed ~0% self-sufficient, so the
  combined figure stays ~0% regardless of scenario.
- Oils/fats/spreads: kept as 3 rows (rapeseed representative, sunflower, soy) rather than forced
  into one blended figure — no consumption-mix-by-oil-type data exists to weight them, so rapeseed
  (Estonia's only real domestic oil crop, 69.3%) is shown as an explicit upper-bound illustration,
  with sunflower and soy both flagged flat at 0% (fully imported, unaffected by scenario).
- Legumes: no consumption or self-sufficiency figure exists at all (a standing gap since Phase
  2/5); only the recommended-demand tonnage is shown, with self-sufficiency left "unknown -
  assumed low" under both scenarios.
- Porridges/pasta/rice/grain products: Phase 5's self-sufficiency is a 0%–178%+ range, not a
  point. Rather than scale a range by a demand ratio (implying false precision), Scenario B is
  described qualitatively only — demand rises ~2.1x, which would compress any point within that
  already-uncertain range.
- Sweets/snacks: raw sugar (~0%, structural — no domestic refining capacity) and manufactured
  goods (not scoreable on a self-sufficiency basis) both stay non-numeric under either scenario;
  only the demand-tonnage change is shown.

## 3. Critical-dependency flagging (5.7)

`critical_dependency_flags.csv` applies a single transparent rule, per PLAN.md 5.7: flag any item
where self-sufficiency falls below **50%**, checked three ways —

1. under Scenario A (status quo) — the primary flag;
2. under Scenario B (TAI-recommended diet) — catches items that are fine today but wouldn't be
   under a fully TAI-compliant diet;
3. under the Phase 6 feed-adjusted lower bound, where computed — catches items whose headline
   figure is comfortable but whose resource-based (feed-import) dependency is not.

A fourth flag marks any item where Scenario B is lower than Scenario A regardless of the 50%
threshold (5.7's "note any group where Scenario B increases the gap"), and a fifth marks
non-numeric/gap items explicitly so they read as flagged-for-data-reasons rather than
flagged-as-measured-dependencies.

**Flagged below 50% under Scenario A:** none of the major categories — the lowest headline
figures (vegetables 46%, fruit+berries 8%) are already below 50% and were already the headline
critical dependencies from Phase 5. Newly flagged here: potato (66.9% headline, but 36.8% under
Scenario B), eggs (53.6% headline, 36.8% under B and 37.5% under the feed-adjusted bound), poultry
(57.7% headline, 40.4% under the feed-adjusted bound though 55.4% under Scenario B alone), and
both non-rapeseed oil types (flat 0%).

**Scenario B worsens self-sufficiency in 9 of 12 numerically-comparable categories** — bread,
potato, vegetables, fruit+berries, dairy, rapeseed oil, fish, eggs, poultry. This is the tension
PLAN.md's 5.6 anticipated: only red meat improves markedly under Scenario B (78.1% → ~274%, since
recommended intake is ~3.5x lower than actual), because it's the one major category that is both
currently over-consumed *and* reasonably self-sufficient. Every other major category either eases
only modestly or worsens, because TAI recommends eating *more* of exactly the categories Estonia
is worst at supplying domestically (vegetables, fruit, dairy, fish) and the demand increase
outpaces the fixed production.

## 4. Headline findings

- **Vegetables** show the sharpest scenario swing: 46% (official-basis headline) → ~13% under a
  fully TAI-compliant diet, because recommended vegetable consumption is ~3.5x current actual
  consumption. This is the single clearest illustration of the plan's core framing tension.
- **Dairy** swings from a comfortable 166% surplus to ~61% — TAI's dairy portion guidance implies
  roughly 2.7x current average consumption. **[Post-launch correction, see docs/methodology.md
  Section 4.2]**: the underlying gram figure this was based on had a methodological error (used
  only one of six dairy product forms in Table 16.3 as if it represented the whole category).
  Corrected figures: dairy swings from 166% to ~100% (not ~61%), on a ~1.65x demand increase (not
  ~2.7x). Left as originally written above for the historical record of what Phase 7 computed at
  the time; the corrected figures are authoritative in `scenario_comparison.csv` and the
  dashboard.
- **Fish** drops from an already-caveated 300% (resource-basis, only ~15% of catch stays
  domestic) to ~89% under Scenario B. Read carefully: this isn't really a production-shortfall
  finding the way vegetables is — Estonia already produces/catches far more fish than it eats, so
  hitting the ~89% figure is a matter of redirecting existing supply toward the domestic market
  rather than producing more.
- **Red meat is the one exception that improves:** 78.1% → ~274% under Scenario B, since current
  consumption is ~3.5x the recommended level.
- **Potato and eggs are new findings this phase** — not previously flagged as critical because
  their Scenario A headline figures (66.9%, 53.6%) look adequate, but both fall meaningfully
  under Scenario B and/or the feed-adjusted bound.
- **Grain (bread) stays comfortably self-sufficient in both scenarios** (332.5% → 185.9%) — the
  one major category with enough surplus to absorb a large recommended-demand increase without
  becoming a concern.

## 5. Cross-phase consistency check

Every numerically-comparable row's `demand_change_ratio_B_over_A` was checked against Phase 4's
independently-computed `over_under_consumption.csv` (`ratio_actual_over_recommended`, the inverse
ratio). All 12 comparable rows match to within rounding — e.g. red meat 3.51 (Phase 4) vs. 3.51
(this phase, inverted), sweets 3.09 vs. 3.09, nuts+seeds 0.09 vs. 0.09 (this pinned down a
transcription slip caught while drafting this file — see below), vegetables 0.28 vs. 0.28,
fish 0.30 vs. 0.30, fruit+berries 0.80 vs. 0.80. This independent agreement is a strong internal
consistency check: two different computations (Phase 4's per-capita gram comparison, this phase's
national-tonnage ratio) built from the same underlying demographic model agree, as they should.

*Self-caught error:* an early draft note for the nuts+seeds row stated the demand increase as
"~9.5x" from a mental approximation; the computed figure is 11.474x (consumption 1,612.9 t/yr vs.
recommended 18,506.7 t/yr), which is what matches Phase 4's 0.09 ratio (1/11.47 ≈ 0.087, rounds to
0.09). Caught by running the cross-phase check and fixed before finalizing the output CSV.

## 6. Nutritional-adequacy note (5.8)

The calorie/macronutrient consistency check for the recommended-diet aggregate was already done
in Phase 3 (`SANITY_CHECK_phase3.md`, two independent derivations within ~2%) — by construction,
since the requirement model is built directly from TAI's own reference values, this is mainly a
modelling-consistency check rather than new analysis, and it passed. The qualitative
micronutrient point from 5.8 is worth stating plainly here since it reinforces the
critical-dependency framing rather than sitting separately from it: vegetables, fruit and fish —
already the three weakest self-sufficiency categories, and the three that worsen most under
Scenario B — are also disproportionately important sources of vitamin C, folate, and omega-3/
iodine. The self-sufficiency gap and the nutritional-adequacy risk point at the same food groups.
This is a qualitative observation, not a quantitative micronutrient model (out of scope for v1
per PLAN.md section 2).

## 7. Files produced

- `data/processed/scenario_comparison.csv` (16 rows) — Scenario A/B demand tonnages, Scenario A/B
  self-sufficiency, and the household-waste-lever adjustment, per pyramid food-group/sub-item.
- `data/processed/critical_dependency_flags.csv` (16 rows) — the five-flag critical-dependency
  table described in section 3.

## 8. Known limitations carried into Phase 8

- The ratio-scaling method (section 1) is an approximation, not a re-derived balance sheet — it
  assumes proportional consistency between the RTU011-based demand model and the PM-series-based
  official self-sufficiency denominator. Directionally reliable; not a substitute for a fully
  independent Scenario B balance-sheet computation (out of scope for v1).
- Oils/fats/spreads' Scenario B figure uses rapeseed as a representative proxy, not a
  consumption-weighted blend across oil types — flagged as an upper-bound illustration.
- Legumes, and the sweets/manufactured-goods split, remain genuine data gaps rather than resolved
  figures — flagged, not fabricated, consistent with every earlier phase's approach.
- Red meat's feed-adjusted bound is not blended into one aggregate figure (its three components —
  pork, beef, sheep-goat — have very different feed-dependency profiles); the flags table leaves
  this cell blank rather than average across a food-mix Estonia's data doesn't quantify.
