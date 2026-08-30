# Food-group taxonomy crosswalk

`food_group_crosswalk.csv` is the single reference table mapping the three different food-group
taxonomies used across this project's sources onto each other:

- **TAI toidupüramiid** (Tabelraamat 2025, Tables 13.1/13.2) — the recommendation side. 6 core
  groups, each with 2-4 sub-items. This is the taxonomy the requirement model (Phase 3) will be
  built around, since it's the one carrying actual portion/kcal targets.
- **RTU011** (TAI 2014 consumption survey) — the actual-consumption side. 6 top-level groups with
  2-3 `..`-prefixed sub-groups each (16 rows total). Only partially aligned with the pyramid's
  grouping.
- **Statistikaamet PM-series** (production/supply balance sheets) — the domestic-production side.
  Organized by commodity, not by nutritional grouping at all.

## Columns

- `pyramid_group` / `pyramid_subitem` — the TAI pyramid taxonomy (canonical for Phase 3+).
- `rtu011_category_et` — the matching RTU011 category, in Estonian as published (`..`-prefix
  preserved so it's greppable against the raw RTU011 CSV).
- `statistikaamet_source` — which PM table(s), or other source, supply the self-sufficiency figure.
- `self_sufficiency_2024_pct` — the figure itself, or a qualitative note where a clean percentage
  isn't computable yet.
- `match_quality` — one of:
  - `exact` — the three taxonomies point at genuinely the same thing.
  - `aggregate` — a pyramid top-level row that blends sub-items with different self-sufficiency
    profiles; don't use the blended number as a headline without checking the sub-items.
  - `needs_split` — one RTU011 or PM-series category bundles together things the pyramid separates
    (e.g. RTU011's single meat figure covers poultry + red meat + offal). A proposed estimation
    method is given in the notes.
  - `needs_conversion` — a real unit/product-form conversion is needed before a self-sufficiency
    number is comparable (e.g. milk-equivalent aggregation across 9 dairy product lines, or
    oilseed-to-refined-oil yield).
  - `gap` — no Estonian data source covers this sub-item at all (legumes, nuts, seeds/cocoa,
    sweets/snacks). These are documented assumptions, not measurements, and should be flagged as
    such wherever they appear in the model or dashboard.
- `notes` — the reasoning, and what a Phase 3 fix would look like where one is identified.

## Known limitations carried forward

Six distinct mismatch types are documented in the table: the legume gap, fruit/berry
inseparability (both RTU011 and Statistikaamet only ever report fruit+berries combined), RTU011's
poultry/red-meat/offal bundling, the missing bread-specific balance (grain self-sufficiency is
computed on raw wheat/rye, not bread), the missing nut/seed/cocoa data, and the missing
sugar/sweets balance. None of these are blockers for Phase 3 — each has either a proposed
estimation method or an explicit "treat as an assumption, not a measurement" flag — but the
dashboard (Phase 9) should surface `match_quality` alongside every number so a reader can tell a
measured self-sufficiency figure from an estimated or assumed one.
