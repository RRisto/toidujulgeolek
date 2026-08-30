#!/usr/bin/env python3
"""
Phase 15 (post-launch, exploratory): if less meat/eggs were produced under a lower-demand
scenario (B/C/C2), what happens to the feed grain and land behind that production?

User question: "if less meat is produced, some crops could go for food, maybe some land could be
used to grow more stuff?" This script works through that chain in two explicitly separated
confidence tiers, per the user's own request to keep them clearly apart rather than presenting
both at the same confidence level:

TIER 1 (solid): demand drop -> feed grain no longer needed -> cropland no longer needed for feed.
Uses only data already in this project (feed_dependency_model.csv's per-species feed-conversion
figures, Phase 6; scenario_comparison.csv's own demand-change ratios; PM20's own 2024 barley yield,
already in data/raw/statistikaamet/PM20_cereals_2024.csv) plus ONE new, clearly-flagged assumption:
that domestic production scales down in proportion to domestic demand. This is a real assumption,
not a measurement -- every other scenario in this project (A/B/C/C2) explicitly holds production
FIXED and only varies demand; this is the one place production is allowed to move, and that choice
is a hypothesis about producer behaviour, not something derived from data. In reality, Estonia
already exports meat, eggs, and (especially) barley in significant volumes, so actual production
would more plausibly respond to export markets and prices than to domestic consumption alone --
this is exactly why the result is presented as "land no longer NEEDED for feed," not "land that
would ACTUALLY be freed."

Note on why this isn't simply "feed grain redirected to human food": Estonia's barley is already a
large net EXPORT crop (2024: production 315.2kt vs domestic use 177.1kt, exports 179.8kt) with feed
as the dominant domestic use. Redirecting less-needed feed grain doesn't mechanically increase any
self-sufficiency figure -- self-sufficiency is production/domestic-use, and shuffling grain between
feed-use and food-use within the same total domestic use doesn't change that ratio. The only lever
that can actually move a WEAK category (like vegetables) is the land itself growing something else
-- which is Tier 2.

TIER 2 (illustrative sketch, NOT a projection): cropland no longer needed for feed barley ->
illustrative output if switched to vegetables instead, at a GENERIC (non-Estonia-specific) EU-wide
average vegetable yield (Eurostat 2022: 59.8Mt / 2.0M ha = 29.9 t/ha), since no Estonia-specific
field-vegetable yield figure was available in this project's existing data or found in a search.
This tier adds substantial additional uncertainty on top of Tier 1's assumption: it ignores soil
and drainage suitability (a lot of arable feed-grain land may not be well-suited to vegetable row
cropping without new capital investment), the very different labour/capital/storage/market
infrastructure vegetable farming requires versus cereal farming, crop-rotation constraints, and
any transition time or cost. Read Tier 2 as "is the land arithmetic even in the right ballpark,"
not "here is what would actually happen."

Deliberately NOT modelled: dairy cattle and (for beef/sheep-goat) pasture/grazing land. Dairy feed
is predominantly grass/silage, not a grain tonnage this project can convert to hectares with any
confidence (same reason feed_dependency_model.csv excludes dairy from its own feed-tonnage table);
permanent pasture is an even less certain conversion candidate than already-arable feed-cropland
(different soil, drainage, and historical land-use profile), so it's excluded rather than forced
into a number that would overstate confidence.
"""
import csv

# --- Tier 1 inputs -----------------------------------------------------
# Feed-grain tonnage behind current production, from feed_dependency_model.csv (Phase 6).
FEED_KT = {
    "Poultry": 40.0,
    "Eggs": 26.0,
    "Red meat": 117.9 + 94.4 + 2.4,  # pork + beef + sheep_goat, summed since demand ratios below
                                       # are only available for the aggregated "Red meat" row
}

# Estonia's own 2024 barley yield (data/raw/statistikaamet/PM20_cereals_2024.csv) -- feed grain is
# overwhelmingly barley (150.8kt of the 230.7kt known domestic feed supply, per
# feed_dependency_model.csv), so barley's own yield is the right conversion factor, and it's
# Estonia-specific and already in this project rather than a new external figure.
BARLEY_YIELD_T_PER_HA = 3.316

# Scale anchors for context (both cited, neither computed by this project before): Estonia's total
# barley sown area, 2024 (PM20, already in this project) and Estonia's total utilised agricultural
# area, 2023 (Statistikaamet news release, ~980,000 ha -- the most recent published aggregate
# figure found; not broken out by crop type in that source).
BARLEY_SOWN_AREA_HA_2024 = 95056.0
TOTAL_UTILISED_AGRICULTURAL_AREA_HA_2023 = 980000.0

# --- Tier 2 inputs -------------------------------------------------------
# Generic (NOT Estonia-specific) EU-wide average vegetable yield: Eurostat 2022, EU fresh-vegetable
# area 2.0 million ha / production 59.8 million tonnes = 29.9 t/ha. No Estonia-specific field-
# vegetable yield figure was available. Estonia's actual achievable yield is very plausibly lower
# than this EU-wide average (shorter growing season, smaller-scale/less-specialised operations
# relative to leading EU vegetable producers), so if anything this OVERSTATES Tier 2's output.
EU_VEGETABLE_YIELD_T_PER_HA = 29.9

# Current vegetable production/domestic-use gap, from PM33 2024 (data/raw/statistikaamet/
# PM33_vegetables_2024.csv) -- the same 2024 vintage as the barley yield above, computed directly
# from raw tonnages rather than a headline percentage, since the project's own three vegetable
# self-sufficiency figures disagree (29% derived / 46% official 5yr-avg / 9.2% FAOSTAT 2022 --
# see docs/methodology.md Section on the FAOSTAT cross-check). Using raw 2024 tonnages here keeps
# this analysis on a single, transparent, internally-consistent basis rather than picking a side
# in that unresolved disagreement.
VEG_PRODUCTION_T_2024 = 33229.0
VEG_DOMESTIC_USE_T_2024 = 114297.0
VEG_GAP_T_2024 = VEG_DOMESTIC_USE_T_2024 - VEG_PRODUCTION_T_2024


def load_demand_ratios():
    ratios = {}
    with open("data/processed/scenario_comparison.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["pyramid_group"] == "Fish, eggs & meat" and row["subitem"] in FEED_KT:
                ratios[row["subitem"]] = {
                    "B": float(row["demand_change_ratio_B_over_A"]),
                    "C": float(row["demand_change_ratio_C_over_A"]),
                    "C2": float(row["demand_change_ratio_C2_over_A"]),
                }
    return ratios


def main():
    ratios = load_demand_ratios()
    scenarios = ["B", "C", "C2"]
    scenario_label = {
        "B": "Scenario B (TAI-recommended diet)",
        "C": "Scenario C (EAT-Lancet 2019 diet)",
        "C2": "Scenario C.2 (EAT-Lancet 2025 diet)",
    }

    rows = []
    for scen in scenarios:
        per_species_freed_kt = {}
        net_freed_kt = 0.0
        for species, feed_kt in FEED_KT.items():
            ratio = ratios[species][scen]
            freed = round(feed_kt * (1 - ratio), 2)  # negative = MORE feed needed, not freed
            per_species_freed_kt[species] = freed
            net_freed_kt += freed

        cropland_freed_ha = round(net_freed_kt * 1000 / BARLEY_YIELD_T_PER_HA, 0) if net_freed_kt > 0 else 0.0
        pct_of_barley_sown_area = round(cropland_freed_ha / BARLEY_SOWN_AREA_HA_2024 * 100, 1) if cropland_freed_ha else 0.0
        pct_of_total_agri_area = round(cropland_freed_ha / TOTAL_UTILISED_AGRICULTURAL_AREA_HA_2023 * 100, 1) if cropland_freed_ha else 0.0
        illustrative_veg_t = round(cropland_freed_ha * EU_VEGETABLE_YIELD_T_PER_HA, 0)
        pct_of_veg_gap = round(illustrative_veg_t / VEG_GAP_T_2024 * 100, 1) if VEG_GAP_T_2024 else None
        ha_needed_to_close_gap = round(VEG_GAP_T_2024 / EU_VEGETABLE_YIELD_T_PER_HA, 0)
        pct_of_freed_land_needed = round(ha_needed_to_close_gap / cropland_freed_ha * 100, 1) if cropland_freed_ha else None

        rows.append({
            "scenario": scenario_label[scen],
            "poultry_feed_freed_kt": per_species_freed_kt["Poultry"],
            "eggs_feed_freed_kt": per_species_freed_kt["Eggs"],
            "red_meat_feed_freed_kt": per_species_freed_kt["Red meat"],
            "tier1_net_feed_freed_kt": round(net_freed_kt, 1),
            "tier1_cropland_no_longer_needed_ha": cropland_freed_ha,
            "tier1_pct_of_2024_barley_sown_area": pct_of_barley_sown_area,
            "tier1_pct_of_total_utilised_agricultural_area": pct_of_total_agri_area,
            "tier2_illustrative_vegetable_output_t": illustrative_veg_t,
            "tier2_pct_of_current_vegetable_gap": pct_of_veg_gap,
            "tier2_pct_of_freed_land_needed_to_close_veg_gap": pct_of_freed_land_needed,
        })

    fieldnames = list(rows[0].keys())
    with open("data/processed/land_reallocation_scenario.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    print(f"wrote data/processed/land_reallocation_scenario.csv ({len(rows)} rows)")
    print(f"vegetable production/use gap (2024): {VEG_GAP_T_2024:.0f} t "
          f"({VEG_PRODUCTION_T_2024:.0f}t produced vs {VEG_DOMESTIC_USE_T_2024:.0f}t used)")
    for r in rows:
        print(f"\n{r['scenario']}:")
        print(f"  Tier 1 -- net feed grain no longer needed: {r['tier1_net_feed_freed_kt']} kt "
              f"(poultry {r['poultry_feed_freed_kt']}, eggs {r['eggs_feed_freed_kt']}, "
              f"red meat {r['red_meat_feed_freed_kt']})")
        print(f"  Tier 1 -- cropland no longer needed for that feed: {r['tier1_cropland_no_longer_needed_ha']:.0f} ha "
              f"({r['tier1_pct_of_2024_barley_sown_area']}% of all 2024 barley sown area, "
              f"{r['tier1_pct_of_total_utilised_agricultural_area']}% of Estonia's total agricultural area)")
        print(f"  Tier 2 -- illustrative vegetable output if switched: {r['tier2_illustrative_vegetable_output_t']:.0f} t "
              f"({r['tier2_pct_of_current_vegetable_gap']}% of the current vegetable gap)")
        print(f"  Tier 2 -- only {r['tier2_pct_of_freed_land_needed_to_close_veg_gap']}% of the freed land would be "
              f"needed to close the ENTIRE current vegetable gap, at this generic yield")


if __name__ == "__main__":
    main()
