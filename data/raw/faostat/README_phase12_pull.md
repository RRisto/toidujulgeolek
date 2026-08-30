# FAOSTAT pull — Phase 12 (2026-08-30)

Follow-up to the Phase 8 FAOSTAT cross-check (see `docs/methodology.md` Section 8 and
`data/processed/faostat_cross_check.csv`), pulled the same way (FAOSTAT's own "Show Data" tool in
the Food Balances (2010-) domain, live browser session — automated fetch to FAOSTAT's API is
blocked, same as every other FAOSTAT pull in this project).

Triggered by two user-raised questions: whether "Nuts+Seeds,cocoa (combined)"'s "~0% assumed"
self-sufficiency figure was ever actually checked (the crosswalk had flagged this as a to-do since
Phase 1 and never followed up), and whether the "Porridges/pasta/rice/grain products" category's
wide unresolved range could be narrowed using a real consumption-mix weighting.

## Query 1 — Nuts and products

Country: Estonia. Item: "Nuts and products" (FAOSTAT's tree-nuts aggregate — the item search also
offered Groundnuts and Coconuts as separate lines, correctly excluded, matching this project's own
"Nuts" vs. "Seeds & cocoa" split). Elements: Production Quantity, Domestic supply quantity. Year:
2022.

Result: Production 0, Domestic supply 32 (both x1000 t) → 0% self-sufficiency. This CONFIRMS the
project's existing "~0% assumed" figure numerically (production is genuinely zero at national-
statistics resolution) rather than contradicting it — small-scale/garden hazelnut growing in
Estonia is real but doesn't register at the scale these national balance sheets track.

## Query 2 — Rice, Barley, Oats (consumption-mix weighting)

Same country/year. Items: Rice and products, Barley and products, Oats. Elements: Production
Quantity, Domestic supply quantity (for self-sufficiency), plus Food supply quantity (kg/capita/yr)
(for a human-consumption weight — this is the human-food-only portion of domestic supply, distinct
from and much smaller than total domestic supply for barley and oats specifically, most of whose
total domestic use is animal feed, not human food; using total domestic supply as a "how much do
people eat" weight would have been wrong).

Results:
- Rice: Production 0, Domestic supply 7 (x1000 t) → 0% self-sufficiency (unchanged from the
  existing Phase 8 cross-check row — confirms it again from the same pull).
- Barley: Production 489, Domestic supply 238 (x1000 t) → 205.5% self-sufficiency (matches the
  existing Phase 8 cross-check row exactly — same source, re-pulled for this query's context).
- Oats: Production 100, Domestic supply 42 (x1000 t) → 238.1% self-sufficiency. This fills a real
  gap — the Phase 1 Statistikaamet PM20 pull had oats production blank for 2024 (not published),
  so this project never had ANY oats self-sufficiency figure until this FAOSTAT pull.
- Food supply quantity (kg/capita/yr): Rice 4.77, Barley 7.78, Oats 5.97 — used as the weight to
  split the RTU011 "porridges/pasta/rice/grain products" survey category between its rice portion
  and its oats+barley ("porridge") portion. This is the same technique already used elsewhere in
  this project (PM42's per-capita consumption shares splitting RTU011's combined poultry/red-meat
  figure, Phase 3) — not a new method, just applied to a category it hadn't been applied to yet.
  Pasta (durum wheat) could not be included in this weighting: FAOSTAT's aggregate "Wheat and
  products" item doesn't separate durum from bread wheat, so no comparable per-capita figure for
  pasta specifically was available this round. See `docs/methodology.md` Section 8 and
  `PHASE12_NOTES.md` for how this was used.
