#!/usr/bin/env python3
"""
Phase 14 (post-launch): fixes up two rows that update_scenario_c2.py's generic branch logic
can't handle correctly, mirroring exactly how Phase 12 hand-patched the equivalent Scenario
A/B/C values for these same two rows (they were never produced by a generic script either).

Run this AFTER update_scenario_c2.py and BEFORE update_flags_c2.py -- the pipeline order is:
  scenario_c2_eatlancet2025.py -> update_scenario_c2.py -> patch_scenario_c2_special_cases.py
  -> update_flags_c2.py -> export_dashboard_data.py -> build_dashboard.py

1. Nuts+Seeds,cocoa (combined): self-sufficiency is a confirmed structural 0% (FAOSTAT 2022:
   0 t production) regardless of demand scenario -- update_scenario_c2.py's elif chain only
   matches specific TEXT patterns (e.g. "~0% assumed"), not the numeric "0.0" this row now
   carries since its Phase 12 upgrade from text to number, so it falls through to "" instead
   of "0.0" unless patched here.

2. Honey: EAT-Lancet (2019 or 2025) has no honey-specific gram target, so update_scenario_c2.py's
   crosswalk lookup finds nothing for this row. Phase 12 established the convention of
   extrapolating honey's Scenario B/C demand using the whole "Sweets, snacks & discretionary
   (total)" category's own demand-change ratio -- an explicit, documented assumption that
   honey's consumption share moves proportionally with the rest of sweets. Applied here for C.2
   using that row's own just-computed demand_change_ratio_C2_over_A.
"""
import csv

def main():
    with open("data/processed/scenario_comparison.csv", encoding="utf-8", newline='') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    sweets_row = next(r for r in rows if r["pyramid_group"] == "Sweets, snacks & discretionary"
                       and r["subitem"] == "(total)")
    ratio_c2 = float(sweets_row["demand_change_ratio_C2_over_A"])

    for row in rows:
        if row["pyramid_group"] == "Nuts, seeds, oils & fats" and row["subitem"] == "Nuts+Seeds,cocoa (combined)":
            row["scenario_C2_self_sufficiency_pct"] = "0.0"
        if row["pyramid_group"] == "Sweets, snacks & discretionary" and row["subitem"] == "Honey":
            demand_A = float(row["scenario_A_demand_tonnes_per_year"])
            pct_A = float(row["scenario_A_self_sufficiency_pct"])
            row["scenario_C2_demand_tonnes_per_year"] = round(demand_A * ratio_c2, 1)
            row["demand_change_ratio_C2_over_A"] = ratio_c2
            row["scenario_C2_self_sufficiency_pct"] = round(pct_A / ratio_c2, 1)

    with open("data/processed/scenario_comparison.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    print("patched Nuts (structural 0%) and Honey (sweets-ratio extrapolation) for Scenario C.2")

if __name__ == "__main__":
    main()
