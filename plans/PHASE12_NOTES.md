# Phase 12 notes — nuts, honey, and the porridge/rice split

Post-launch addition, prompted directly by user feedback after seeing the Phase 11 dashboard:
"we have honey, some nuts are also grown ... rice is one thing we dont have, other things we have
... this is a category which could have a better approach." Status: done, best effort on all three.

## 1. What was actually wrong (and what wasn't)

Before doing any new research, checking this project's own existing files showed all three
questions had already been asked and left open:

- **Nuts** (`data/crosswalk/food_group_crosswalk.csv`, Phase 1): "Estonia's climate does not
  support commercial tree-nut production at any real scale ... **Worth a Phase 3 double-check
  against foreign trade import data rather than leaving as pure assumption.**" That check never
  happened in Phases 2-11.
- **Porridges/pasta/rice** (same file, Phase 1): "**Needs splitting rice out from the rest to
  avoid overstating self-sufficiency**" (`match_quality: needs_split`), blocked on "no consumption-
  mix data to weight barley vs. rice vs. durum pasta."
- **Honey**: not flagged anywhere as a gap, because it wasn't a gap — `data/raw/statistikaamet/
  PM29_honey_2024.csv` was pulled successfully in Phase 1 (Statistikaamet publishes a full honey
  resource-and-use balance) and then simply never used by any downstream script or crosswalk row.
  A plain oversight, confirmed by `find`-ing the file and finding no other reference to it anywhere
  in the repo.

So the task wasn't "the user found new problems" — it was "the project's own self-diagnosis was
right and unresolved; go resolve it as far as the evidence allows."

## 2. Honey

`data/raw/statistikaamet/PM29_honey_2024.csv`: production 1,313 t, human consumption 1,339 t
(2024) → 98.1% self-sufficient. Added as a new resolved subitem under "Sweets, snacks &
discretionary" in `food_group_crosswalk.csv`, `self_sufficiency_model.csv`, and
`scenario_comparison.csv` — its own subitem (independent-source basis) rather than folded into the
unresolved "(total)" pill, the same structural choice already made for Fish & seafood.

TAI's Table 13 doesn't give honey its own recommended-portion count — Table 16.6 uses honey as one
of five equally-weighted items for a representative sweets gram-weight, but there's no honey-
specific recommended intake to compute a real Scenario B/C demand from. Rather than leave B/C
blank, extrapolated using the whole "Sweets (total)" category's own demand-change ratios (0.323x
for B, 0.1743x for C) — an explicit, stated assumption (honey's consumption moves proportionally
with the rest of sweets), not a TAI-specific figure. Result: Scenario A 98.1%, Scenario B 303.7%,
Scenario C 562.8% — moving toward recommended (lower) sweets consumption only strengthens honey
self-sufficiency further, since production is held fixed. Added a matching
`critical_dependency_flags.csv` row (no flags trip; comfortably self-sufficient in every scenario).

## 3. Nuts

Ran the Phase-3 double-check that never happened: FAOSTAT 2022, Estonia, "Nuts and products"
(FAOSTAT's tree-nuts aggregate — the item search also offered Groundnuts and Coconuts as separate
lines, correctly excluded). Result: 0 t production against ~32kt domestic supply = exactly 0%.

This **confirms** the existing "~0% assumed" figure rather than revising it. The user's underlying
observation (some nuts, e.g. hazelnuts, are genuinely grown in Estonia) is true and not in tension
with this: small-scale and garden-level nut growing is real but doesn't register at the national-
statistics resolution these balance sheets operate at. Upgraded the figure from a text pill
("~0% assumed") to a resolved numeric 0.0% — matching the existing treatment of sunflower/soy oil
(also confirmed-zero, also numeric) — which means it now renders as an actual (very short) bar on
the dashboard instead of a "no single figure" badge, and now counts toward the headline weighted
average instead of being silently excluded from it (coverage rose from 77.4% to 77.7% of total
tonnage as a direct result).

## 4. Porridges/pasta/rice/grain products

Pulled FAOSTAT 2022 Estonia data for the three components RTU011 bundles into this one survey
category:

| Item | Production (kt) | Domestic supply (kt) | Self-sufficiency | Food supply (kg/capita/yr) |
|---|---|---|---|---|
| Rice and products | 0 | 7 | 0% | 4.77 |
| Barley and products | 489 | 238 | 205.5% | 7.78 |
| Oats | 100 | 42 | 238.1% | 5.97 |

Barley matches the existing Phase 8 cross-check row exactly (same source). **Oats is new** — the
Phase 1 Statistikaamet PM20 pull had oats production blank for 2024 (not published that year), so
this project had no oats self-sufficiency figure at all until now. Adopted directly as the
project's own figure in the absence of any Estonian-source alternative.

The "Food supply quantity (kg/capita/yr)" element is human-food consumption specifically, not
total domestic supply — an important distinction, since barley and oats' total domestic supply is
mostly animal feed, not human porridge. Using these three figures as consumption-mix weights (the
same per-capita-share splitting technique Phase 3 already used for RTU011's combined poultry/red-
meat figure, via PM42's shares) gives: rice 25.8% of the weighted total (4.77 / 18.52), oats+barley
"porridge grains" 74.2% (13.75 / 18.52).

Weighted blend of just those two parts: 0.258 × 0% + 0.742 × 210.4% (barley+oats combined:
589kt / 280kt) ≈ **156.2%**. This is presented as an **upper bound**, not the resolved
whole-category figure: pasta (durum wheat) is still excluded, because FAOSTAT's aggregate "Wheat
and products" item doesn't separate durum from bread wheat, so no comparable per-capita weight for
pasta specifically was available this round. PM20 already shows 0% durum wheat production, so
pasta's true self-sufficiency is very likely also near 0% — meaning folding it in could only pull
the blended figure down, never above 156.2%. Narrowed the prior 0%-178%+ span (128 percentage
points wide, effectively uninformative) to a single-sided ceiling with real weighting behind it,
without fabricating a false point estimate for the piece that's still genuinely unresolved.

This subitem remains a text pill on the dashboard (not a numeric bar) since it's still not a single
point estimate — but the pill text, tooltip-adjacent note, and underlying CSVs all now carry the
tighter, sourced figure instead of the old opaque range.

## 5. Verification

Re-ran `export_dashboard_data.py` then `build_dashboard.py`. Confirmed in the regenerated
`output/dashboard_data.json`: Honey appears as a new `food_groups` entry (98.1/303.7/562.8%); Nuts
now carries numeric `0.0` for all three scenarios instead of text; headline Scenario A weighted
average shifted from 106.8% to 106.4% (coverage 77.4% → 77.7%) as Nuts (0%) and Honey (98.1%)
both newly count toward it — a small, expected, and correct change, not a bug. Did not re-run the
Playwright visual check from Phase 11 for this round (no new chart code was touched — Honey and
Nuts both render through the same existing `renderSSChart()` path, and the underlying JSON values
were the only thing that changed), but should be spot-checked next time the dashboard is opened.

## 6. Deliverables

- `data/raw/faostat/estonia_2022_nuts_oats_rice_barley.csv`, `README_phase12_pull.md` — raw pull
  and provenance notes for this phase's two FAOSTAT queries.
- `data/processed/faostat_cross_check.csv` — two new rows (Nuts and products; Oats).
- `data/crosswalk/food_group_crosswalk.csv` — Nuts and Porridges rows updated; new Honey row.
- `data/processed/self_sufficiency_model.csv` — Nuts and Porridges rows updated; new Honey row.
- `data/processed/scenario_comparison.csv` — Nuts upgraded to numeric; Porridges narrowed; new
  Honey row (Scenario A/B/C all populated).
- `data/processed/critical_dependency_flags.csv` — Nuts flags refreshed (no longer a data gap);
  new Honey row (no flags trip); Porridges reason text updated.
- `src/export_dashboard_data.py` — `FAOSTAT_ITEM_TO_SUBITEM` gained a "Nuts and products" mapping.
- `docs/methodology.md` Section 8 — new "Three follow-up checks (Phase 12)" paragraph.
- `output/dashboard_data.json`, `output/dashboard.html` — rebuilt.
