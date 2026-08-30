#!/usr/bin/env python3
"""
Phase 14 (post-launch): Scenario C.2 -- the 2025 EAT-Lancet Commission's revised Planetary
Health Diet, alongside the existing Scenario C (the original 2019 diet, Phase 10).

User feedback after being told about the 2019 diet asked whether a newer version existed. It
does: the EAT-Lancet Commission published an updated Summary Report in 2025 (referred to in some
follow-up academic literature as "Planetary Health Diet 2.0"). Its dietary-targets table (Figure
01) revises several food-group gram amounts, not just the framing -- most strikingly a large cut
to added/free sugar (31g -> 6g/day) and a modest across-the-board bump to animal-protein sources
(eggs, fish, poultry, red meat), alongside a lower whole-grains figure, against a slightly lower
reference calorie level (2,500 -> ~2,400 kcal/day). Vegetables, fruit, legumes, nuts, dairy and
starchy tubers are unchanged from 2019.

Same computation pattern as Scenario C (src/scenario_c_eatlancet.py): production held fixed,
self-sufficiency re-scaled by the ratio of Scenario A to Scenario C.2 demand tonnage:

    scenario_C2_self_sufficiency_pct = scenario_A_self_sufficiency_pct * (demand_A / demand_C2)

SOURCING CAVEAT: these 2025 figures were read from the EAT-Lancet Commission's own public Summary
Report PDF (Figure 01), not independently cross-checked against the full peer-reviewed Lancet
paper (paywalled) or a second primary source. If this matters for a future phase -- e.g. before
citing this project's Scenario C.2 numbers externally -- re-verify against the primary journal
article rather than trusting this transcription indefinitely. This is the same caveat Scenario C's
2019 numbers carry, carried forward here for the same reason.

2025 EAT-LANCET REFERENCE VALUES (g/day, at the diet's own ~2,400 kcal/day calibration) -- source:
EAT-Lancet Commission Summary Report 2025, Figure 01 ("Dietary targets for a healthy reference
diet, with possible ranges, for adult population-average energy intake of roughly 2,400 kcal per
day"):

    Whole grains                 210   (2019: 232)
    Starchy roots/tubers          50   (2019: 50, unchanged)
    Vegetables                   300   (2019: 300, unchanged)
    Fruits                       200   (2019: 200, unchanged)
    Legumes                       75   (2019: 75, unchanged)
    Tree nuts & peanuts           50   (2019: 50, unchanged)
    Dairy products                250   (2019: 250, unchanged)
    Eggs                           15   (2019: 13)
    Fish and shellfish             30   (2019: 28)
    Chicken/poultry                30   (2019: 29)
    Beef, pork or lamb             15   (2019: 14)
    Added/free sugars               6   (2019: 31 -- the largest single change)
    Unsaturated plant oils         40   (2019: 40, unchanged)
    Palm/coconut oil                5   (2019: 6.8)
    Lard, tallow, butter            6   (2019: 5)

SCALING: same method Scenario C already uses -- the diet's own reference calorie level scaled to
Estonia's population-weighted energy requirement (2,234.358 kcal/capita/day, Phase 3) by simple
proportion, preserving the 2025 diet's own food-group ratios. This project's own methodological
choice (as with Scenario C), not something EAT-Lancet's documentation prescribes.

    scale_factor_2025 = 2234.358 / 2400 = 0.930983
"""
import csv

POPULATION = 1339785.0  # ages 2+, canonical grid total (matches Phase 3)
SCALE2 = 2234.358 / 2400.0

# 2025 EAT-Lancet reference, g/day at ~2400kcal
EL2 = {
    "whole_grains": 210.0,
    "vegetables": 300.0,
    "fruits": 200.0,
    "dairy": 250.0,
    "eggs": 15.0,
    "legumes": 75.0,
    "nuts": 50.0,
    "poultry": 30.0,
    "fish": 30.0,
    "red_meat": 15.0,
    "added_sugars": 6.0,
    "starchy_tubers": 50.0,
    "oils_fats": 40.0 + 5.0 + 6.0,  # unsaturated oils + palm/coconut + lard/tallow/butter = 51
}

# This project's own bread : porridge/rice/pasta split ratio (from requirement_model_national.csv,
# Phase 3), applied to the 2025 diet's single combined "whole grains" figure since neither
# EAT-Lancet edition splits them. Same documented assumption Scenario C already makes.
BREAD_SHARE = 131.76 / (131.76 + 261.97)          # 0.33456
PORRIDGE_SHARE = 261.97 / (131.76 + 261.97)        # 0.66544

rows = []  # (pyramid_group, subitem, el2_g_per_day_at_2400kcal, scaled_g_per_day, match_note)

def add(group, subitem, el_val, note):
    scaled = None if el_val is None else round(el_val * SCALE2, 4)
    rows.append((group, subitem, el_val, scaled, note))

add("Grain products & potatoes", "High-fibre bread/baked goods",
    EL2["whole_grains"] * BREAD_SHARE,
    "2025 EAT-Lancet gives one combined 'whole grains' figure (210g, down from 232g in 2019); "
    "split using this project's own bread:porridge/rice/pasta ratio (33.5%/66.5%, from "
    "requirement_model_national.csv) since neither EAT-Lancet edition distinguishes them. "
    "Documented assumption, not a measurement.")
add("Grain products & potatoes", "Porridges/pasta/rice/grain products",
    EL2["whole_grains"] * PORRIDGE_SHARE,
    "See bread row -- same combined-figure split.")
add("Grain products & potatoes", "Potato, sweet potato",
    EL2["starchy_tubers"],
    "2025 'starchy roots/tubers' (50g, unchanged from 2019) used directly -- still a much smaller "
    "allowance than TAI's Table 13, which treats potato as a dietary staple.")
add("Vegetables, fruits & berries", "Vegetables",
    EL2["vegetables"], "Direct match: 2025 'vegetables' line, unchanged from 2019 (300g).")
add("Vegetables, fruits & berries", "Fruits+Berries (combined)",
    EL2["fruits"],
    "2025 gives one 'fruits' figure (200g, unchanged from 2019) with no separate berries line -- "
    "used as-is for the combined fruits+berries row, same treatment as Scenario C.")
add("Vegetables, fruits & berries", "Legumes",
    EL2["legumes"], "Direct match: 2025 'legumes' line, unchanged from 2019 (75g).")
add("Dairy products", "(total)",
    EL2["dairy"], "Direct match: 2025 'dairy products' line, unchanged from 2019 (250g).")
add("Nuts, seeds, oils & fats", "Nuts+Seeds,cocoa (combined)",
    None,
    "2025 report gives tree nuts & peanuts (50g, unchanged) but still no separate seeds/cocoa "
    "figure -- same gap as Scenario C, left blank rather than understating the combined demand. "
    "Self-sufficiency is ~0% (confirmed, Phase 12) regardless of demand scaling, so this gap "
    "doesn't affect the self-sufficiency figure, only the demand-tonnage/ratio columns.")
add("Nuts, seeds, oils & fats", "Oils/fats/spreads (rapeseed, representative)",
    EL2["oils_fats"],
    "2025 unsaturated oils (40g, unchanged) + palm/coconut oil (5g, was 6.8g) + lard/tallow/"
    "butter (6g, was 5g) = 51g (was 51.8g in 2019, essentially unchanged in total). Applied to "
    "the combined oils/fats/spreads demand basis, same convention as Scenario A/B/C.")
add("Fish, eggs & meat", "Fish & seafood",
    EL2["fish"], "Direct match: 2025 'fish and shellfish' line (30g, up from 28g in 2019).")
add("Fish, eggs & meat", "Eggs",
    EL2["eggs"], "Direct match: 2025 'eggs' line (15g, up from 13g in 2019).")
add("Fish, eggs & meat", "Poultry",
    EL2["poultry"], "Direct match: 2025 'chicken/poultry' line (30g, up from 29g in 2019).")
add("Fish, eggs & meat", "Red meat",
    EL2["red_meat"], "Direct match: 2025 'beef, pork or lamb' line (15g, up from 14g in 2019).")
add("Sweets, snacks & discretionary", "(total)",
    EL2["added_sugars"],
    "2025 'added/free sugars' (6g, sharply down from 31g in 2019 -- now explicitly tied to the "
    "WHO's under-10%-of-energy sugar guideline in the report's own text) used as a proxy. Same "
    "category-boundary caveat as Scenario C: EAT-Lancet has no broader 'snacks' category, so this "
    "still likely understates the true comparable figure since this project's category also "
    "includes salty snacks, not just sugar -- but the gap between the proxy and the true figure "
    "is now much larger given how far the sugar target itself dropped.")

with open("data/crosswalk/eatlancet2025_crosswalk.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["pyramid_group", "subitem", "eatlancet2025_g_per_day_at_2400kcal",
                "scaled_g_per_day_estonia", "note"])
    for group, subitem, el_val, scaled, note in rows:
        w.writerow([group, subitem,
                    "" if el_val is None else round(el_val, 2),
                    "" if scaled is None else scaled,
                    note])

print(f"wrote data/crosswalk/eatlancet2025_crosswalk.csv ({len(rows)} rows)")
print(f"scale factor: {SCALE2:.6f}")
for group, subitem, el_val, scaled, note in rows:
    tonnes = None if scaled is None else round(scaled * POPULATION * 365 / 1e6, 1)
    print(f"  {group} / {subitem}: {el_val} -> {scaled} g/day -> {tonnes} t/year")
