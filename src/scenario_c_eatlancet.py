#!/usr/bin/env python3
"""
Phase 10 (post-launch): Scenario C -- the EAT-Lancet Planetary Health Diet.

Builds a third demand scenario alongside Scenario A (status quo consumption, Phase 4) and
Scenario B (TAI-recommended diet, Phase 3/7), using the EAT-Lancet reference diet as the demand
basis instead of TAI's Tabelraamat. Production is held fixed (same convention as Scenario B), so
self-sufficiency is re-scaled by the ratio of Scenario A to Scenario C demand tonnage:

    scenario_C_self_sufficiency_pct = scenario_A_self_sufficiency_pct * (demand_A / demand_C)

Same approximation Scenario B uses (Section 10 of docs/methodology.md): this assumes proportional
consistency between demand and the production-side self-sufficiency denominator, not a fully
re-derived balance sheet.

EAT-LANCET REFERENCE VALUES (g/day, at the diet's own 2500 kcal/day calibration) -- source: the
EAT-Lancet Commission's Planetary Health Diet reference table (Willett et al. 2019), as summarised
publicly. NOT independently re-verified against the original Lancet paper this session -- if that
matters for a future phase, re-check against the primary source rather than trusting this
transcription indefinitely.

    Whole grains                 232
    Vegetables                   300
    Fruits                       200
    Dairy foods                  250
    Eggs                          13
    Legumes                       75
    Nuts                          50
    Poultry                       29
    Fish                          28
    Beef/lamb/pork                14
    Added sugars                  31
    Starchy vegetables/tubers     50
    Unsaturated oils              40
    Palm oil                     6.8
    Lard or tallow                 5

SCALING: EAT-Lancet's 2500 kcal/day calibration is scaled to Estonia's own population-weighted
energy requirement (2,234.36 kcal/capita/day, ages 2+, PAL=moderate -- Phase 3's top-down
demographic-grid figure, the same one used in SANITY_CHECK_phase3.md) by simple proportion,
preserving EAT-Lancet's own food-group ratios. This is THIS PROJECT'S OWN methodological choice,
not something EAT-Lancet's own documentation prescribes -- their public materials don't specify a
scaling method for non-2500-kcal populations, so this mirrors how Scenario B already treats TAI's
portion guidance (scaled to Estonia's actual demographic energy needs), applied consistently to
keep A/B/C comparable on the same basis.

    scale_factor = 2234.358 / 2500 = 0.893743
"""
import csv

POPULATION = 1339785.0  # ages 2+, canonical grid total (matches Phase 3)
SCALE = 2234.358 / 2500.0

# EAT-Lancet reference, g/day at 2500kcal
EL = {
    "whole_grains": 232.0,
    "vegetables": 300.0,
    "fruits": 200.0,
    "dairy": 250.0,
    "eggs": 13.0,
    "legumes": 75.0,
    "nuts": 50.0,
    "poultry": 29.0,
    "fish": 28.0,
    "red_meat": 14.0,
    "added_sugars": 31.0,
    "starchy_tubers": 50.0,
    "oils_fats": 40.0 + 6.8 + 5.0,  # unsaturated oils + palm oil + lard/tallow = 51.8
}

# This project's own bread : porridge/rice/pasta split ratio (from requirement_model_national.csv,
# Phase 3), applied to EAT-Lancet's single combined "whole grains" figure since EAT-Lancet doesn't
# split them. Documented assumption, not a measurement -- same pattern Phase 4 used to split
# poultry/red-meat off RTU011's bundled figure using PM42 production shares.
BREAD_SHARE = 131.76 / (131.76 + 261.97)          # 0.33456
PORRIDGE_SHARE = 261.97 / (131.76 + 261.97)        # 0.66544

rows = []  # (pyramid_group, subitem, el_g_per_day_at_2500kcal, scaled_g_per_day, match_note)

def add(group, subitem, el_val, note):
    scaled = None if el_val is None else round(el_val * SCALE, 4)
    rows.append((group, subitem, el_val, scaled, note))

add("Grain products & potatoes", "High-fibre bread/baked goods",
    EL["whole_grains"] * BREAD_SHARE,
    "EAT-Lancet gives one combined 'whole grains' figure (232g); split using this project's own "
    "bread:porridge/rice/pasta ratio (33.5%/66.5%, from requirement_model_national.csv) since "
    "EAT-Lancet doesn't distinguish them. Documented assumption, not a measurement.")
add("Grain products & potatoes", "Porridges/pasta/rice/grain products",
    EL["whole_grains"] * PORRIDGE_SHARE,
    "See bread row -- same combined-figure split.")
add("Grain products & potatoes", "Potato, sweet potato",
    EL["starchy_tubers"],
    "EAT-Lancet 'starchy vegetables/tubers' (50g) used directly -- a much smaller allowance than "
    "TAI's Table 13, which treats potato as a dietary staple rather than a limited category.")
add("Vegetables, fruits & berries", "Vegetables",
    EL["vegetables"], "Direct match: EAT-Lancet 'vegetables' line.")
add("Vegetables, fruits & berries", "Fruits+Berries (combined)",
    EL["fruits"],
    "EAT-Lancet gives one 'fruits' figure (200g) with no separate berries line -- used as-is for "
    "the combined fruits+berries row (matching how RTU011 and this project's other scenarios also "
    "treat fruit+berries as combined-only). Likely a slight underestimate of the true combined "
    "figure if berries would sit on top of fruit rather than within it, but no EAT-Lancet-specific "
    "berries figure exists to add.")
add("Vegetables, fruits & berries", "Legumes",
    EL["legumes"], "Direct match: EAT-Lancet 'legumes' line.")
add("Dairy products", "(total)",
    EL["dairy"], "Direct match: EAT-Lancet 'dairy foods' line.")
add("Nuts, seeds, oils & fats", "Nuts+Seeds,cocoa (combined)",
    None,
    "EAT-Lancet's published reference gives nuts (50g) but no separate seeds/cocoa figure -- since "
    "this project's row is a combined nuts+seeds+cocoa quantity, reporting nuts alone as the "
    "'combined' demand would understate it and invite a misleading ratio. Left as a gap rather "
    "than a partial number. Self-sufficiency is ~0% assumed regardless of demand scaling (Phase 5), "
    "so this gap doesn't affect the self-sufficiency figure, only the demand-tonnage/ratio columns.")
add("Nuts, seeds, oils & fats", "Oils/fats/spreads (rapeseed, representative)",
    EL["oils_fats"],
    "EAT-Lancet's unsaturated oils (40g) + palm oil (6.8g) + lard/tallow (5g) = 51.8g, applied to "
    "the same combined oils/fats/spreads demand basis Scenario A/B use (no oil-type breakdown "
    "exists in any demand source, so this figure is assigned to the rapeseed representative row "
    "by the same convention as A/B; sunflower/soy rows stay at their fixed 0% self-sufficiency "
    "regardless of scenario).")
add("Fish, eggs & meat", "Fish & seafood",
    EL["fish"], "Direct match: EAT-Lancet 'fish' line.")
add("Fish, eggs & meat", "Eggs",
    EL["eggs"], "Direct match: EAT-Lancet 'eggs' line.")
add("Fish, eggs & meat", "Poultry",
    EL["poultry"], "Direct match: EAT-Lancet 'poultry' line.")
add("Fish, eggs & meat", "Red meat",
    EL["red_meat"], "Direct match: EAT-Lancet 'beef/lamb/pork' line.")
add("Sweets, snacks & discretionary", "(total)",
    EL["added_sugars"],
    "EAT-Lancet's 'added sugars' (31g) used as a proxy -- EAT-Lancet has no broader 'snacks' "
    "category, so this likely understates the true comparable figure (this project's category "
    "also includes salty snacks, not just sugar). Same category-boundary caveat already flagged "
    "for the RTU011 comparison of this row (Section 5.1).")

with open("data/crosswalk/eatlancet_crosswalk.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["pyramid_group", "subitem", "eatlancet_g_per_day_at_2500kcal",
                "scaled_g_per_day_estonia", "note"])
    for group, subitem, el_val, scaled, note in rows:
        w.writerow([group, subitem,
                    "" if el_val is None else round(el_val, 2),
                    "" if scaled is None else scaled,
                    note])

print(f"wrote data/crosswalk/eatlancet_crosswalk.csv ({len(rows)} rows)")
print(f"scale factor: {SCALE:.6f}")
for group, subitem, el_val, scaled, note in rows:
    tonnes = None if scaled is None else round(scaled * POPULATION * 365 / 1e6, 1)
    print(f"  {group} / {subitem}: {el_val} -> {scaled} g/day -> {tonnes} t/year")
