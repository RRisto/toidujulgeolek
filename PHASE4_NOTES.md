# Phase 4 notes — actual-consumption model & over/under-consumption

Phase 4 of PLAN.md Section 7 / Section 5.2: population-weighted *actual* demand per food group
from RTU011, and the comparison against Phase 3's recommended-demand model. Status: done.

## What Phase 4 delivered

1. **Parsed and QA'd RTU011** — two independent internal-consistency checks (top-level vs.
   summed sub-groups; published `total` vs. average of `male`/`female`) both passed within normal
   survey rounding, confirming the raw file was read correctly.

2. **Mapped RTU011's 16 categories onto the canonical pyramid taxonomy**
   (`data/processed/consumption_grams_by_grid_cell.csv`, 448 rows). Three mapping types, all
   carried over from the Phase 2 crosswalk's documented mismatches:
   - **Direct 1:1** for 9 categories (bread, porridge/pasta/rice, potato, vegetables, dairy, fish,
     eggs, oils/fats, sweets).
   - **Split**: RTU011 bundles poultry with red meat and offal into one "liha, linnuliha..."
     figure. Split using PM42 2024's own per-capita consumption *shares* (poultry 34.3%,
     beef+pork+sheep-goat+offal 65.7%) — shares, not absolute levels, since (see the sanity check)
     PM42's absolute levels run structurally higher than RTU011's.
   - **Combined-only**: RTU011 can't split fruit from berries, or nuts from seeds/cocoa (matching
     the crosswalk's documented gap) — these are compared against Phase 3's *summed* target for
     the combined pair, not two separate ratios.
   - **Not measured**: legumes have no RTU011 category at all. Left as an explicit gap in every
     output table (never silently treated as zero consumption).
   - The 75+ age band reuses the 70-74 RTU011 value as a proxy, per `demographic_grid.md`'s
     already-documented decision.

3. **National actual-consumption demand** — `data/processed/consumption_model_national.csv`, same
   shape as Phase 3's output for direct comparability.

4. **Over/under-consumption** — `data/processed/over_under_consumption.csv` (national) and
   `data/processed/over_under_consumption_by_segment.csv` (six illustrative age x sex segments:
   6-9, 30-34, and 70-74, each male and female — chosen to contrast childhood, working-age, and
   elderly patterns, per PLAN.md 5.2's expectation that over/under-consumption is not evenly
   distributed across demographic groups).

   **National headline findings**: red meat is consumed at **3.5x** the recommended level, sweets/
   snacks/discretionary at **3.1x**; poultry is roughly on target (0.96x); everything else is
   under-consumed relative to TAI's guidance — most severely nuts/seeds (0.09x), vegetables
   (0.28x), and fish (0.30x). Dairy, despite being Estonia's most self-sufficient category, is only
   at 0.37x its recommended level.

   **Segment-level findings show the national picture hides real unevenness**: children (6-9)
   over-consume sweets at **5.7-9.2x** their (much lower) recommended level — a starker ratio than
   any adult segment shows, because children's recommended sweets allowance is small while their
   actual reported intake is close to the adult level in absolute grams. Red meat over-consumption
   peaks in working-age adults (30-34: 3.7-4.2x) rather than children or the elderly. Vegetable
   under-consumption is remarkably uniform across all six segments (0.24-0.34x) — this isn't a
   life-stage problem, it's constant across the whole population.

5. **Sanity checks** (`data/processed/SANITY_CHECK_phase4.md`): parse QA passed; population-
   weighted dairy/vegetables figures land close to Phase 1's raw-survey spot checks; the poultry+
   red-meat split's *absolute* consumption level (39.3 kg/capita/year) is roughly half PM42's
   supply-side figure (80.4 kg/year) — flagged as the same survey-vs-supply-balance-sheet gap
   already documented for vegetables in Phase 1, not a new error, and not something the split
   itself is sensitive to since only relative *shares* were used; the whole actual-consumption
   model implies a national average of ~1,655 kcal/capita/day, about 74% of Phase 3's
   requirement-side figure (2,234 kcal/day) — consistent with well-documented dietary-recall-survey
   underreporting, discussed at length in the sanity-check file rather than treated as an error to
   fix.

## Confirmed open items carried into Phase 5+

- The RTU011 survey is from 2014 (already flagged repeatedly since Phase 1) — every ratio in this
  phase's output should be read as "vs. a decade-old consumption snapshot," not necessarily today's
  diet.
- Legumes remain completely unmeasured on the consumption side, same as the production side
  (Phase 2's crosswalk gap) — any headline finding about the "vegetables, fruits & berries" pyramid
  group should note legumes are excluded from both halves of the comparison, not just one.
- The poultry/red-meat split rests on a single assumption (PM42's 2024 per-capita shares applied
  uniformly across all demographic segments and back to a 2014 survey) — if meat-type preferences
  have shifted between demographic groups or over the decade, this split would not capture that.
- The survey-vs-supply gap (Section 3 of the sanity check) is worth a dedicated reconciliation pass
  once Phase 5 builds the full supply-side model — right now it's flagged wherever it appears, but
  not explained beyond "known survey artifact."
