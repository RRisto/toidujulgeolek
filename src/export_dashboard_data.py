"""
Phase 9: export all Phase 3-8 model outputs into a single consolidated JSON for the dashboard.
Run from the project root. Reads data/processed/*.csv, writes output/dashboard_data.json.
Kept separate from the HTML page per PLAN.md Section 6: re-run this any time the underlying
model/data is updated, without touching the dashboard's presentation code.
"""
import csv
import json
import os
from datetime import date

BASE = os.path.expanduser("~/mnt/toidujulgeolek")
PROC = f"{BASE}/data/processed"
OUT = f"{BASE}/output"

def read_csv(name):
    with open(f"{PROC}/{name}", newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None

# ---------------------------------------------------------------------------
# 1. Food groups (self-sufficiency + scenario + flags + feed-adjustment, merged)
# ---------------------------------------------------------------------------
scenario = read_csv("scenario_comparison.csv")
flags = read_csv("critical_dependency_flags.csv")
flags_by_key = {(r['pyramid_group'], r['subitem']): r for r in flags}

food_groups = []
for r in scenario:
    key = (r['pyramid_group'], r['subitem'])
    fl = flags_by_key.get(key, {})
    a_pct = num(r['scenario_A_self_sufficiency_pct'])
    b_pct = num(r['scenario_B_self_sufficiency_pct'])
    c_pct = num(r['scenario_C_self_sufficiency_pct'])
    food_groups.append({
        "pyramid_group": r['pyramid_group'],
        "subitem": r['subitem'],
        "scenario_A_pct": a_pct,
        "scenario_A_pct_display": r['scenario_A_self_sufficiency_pct'],
        "scenario_B_pct": b_pct,
        "scenario_B_pct_display": r['scenario_B_self_sufficiency_pct'],
        "scenario_C_pct": c_pct,
        "scenario_C_pct_display": r['scenario_C_self_sufficiency_pct'],
        "demand_A_tonnes": num(r['scenario_A_demand_tonnes_per_year']),
        "demand_B_tonnes": num(r['scenario_B_demand_tonnes_per_year']),
        "demand_C_tonnes": num(r['scenario_C_demand_tonnes_per_year']),
        "demand_change_ratio": num(r['demand_change_ratio_B_over_A']),
        "demand_change_ratio_C": num(r['demand_change_ratio_C_over_A']),
        "waste_lever_25_pct": num(r['scenario_A_waste_lever_25pct_household_cut_pct']),
        "waste_lever_50_pct": num(r['scenario_A_waste_lever_50pct_household_cut_pct']),
        "feed_adjusted_low_bound_pct": num(fl.get('feed_adjusted_low_bound_pct', '')),
        "data_status": r['data_status'],
        "note": r['note'],
        "flags": {
            "below_50_scenario_A": fl.get('flag_below_50pct_scenario_A', 'N/A'),
            "below_50_scenario_B": fl.get('flag_below_50pct_scenario_B', 'N/A'),
            "below_50_scenario_C": fl.get('flag_below_50pct_scenario_C', 'N/A'),
            "scenario_C_worsens": fl.get('flag_scenario_C_worsens_dependency', 'N/A'),
            "feed_adjusted_extends_concern": fl.get('flag_feed_adjusted_extends_concern', 'N/A'),
            "scenario_B_worsens": fl.get('flag_scenario_B_worsens_dependency', 'N/A'),
            "unresolved_data_gap": fl.get('flag_unresolved_data_gap', 'N/A'),
        },
        "flag_reason": fl.get('reason', ''),
    })

# ---------------------------------------------------------------------------
# 2. Headline scorecard: tonnage-weighted aggregate self-sufficiency
#    Only over rows with a genuine numeric point estimate (excludes ranges/bimodal/gaps).
# ---------------------------------------------------------------------------
def weighted_headline(pct_field, weight_field="demand_A_tonnes"):
    num_sum = 0.0
    den_sum = 0.0
    included = []
    excluded = []
    total_tonnes_all = 0.0
    for g in food_groups:
        w = g[weight_field]
        if w:
            total_tonnes_all += w
        pct = g[pct_field]
        if pct is not None and w:
            num_sum += pct * w
            den_sum += w
            included.append(f"{g['pyramid_group']} / {g['subitem']}")
        elif w:
            excluded.append(f"{g['pyramid_group']} / {g['subitem']}")
    weighted_pct = round(num_sum / den_sum, 1) if den_sum else None
    coverage = round(den_sum / total_tonnes_all * 100, 1) if total_tonnes_all else None
    return weighted_pct, coverage, included, excluded

hl_A_pct, hl_A_cov, hl_A_incl, hl_A_excl = weighted_headline("scenario_A_pct")
hl_B_pct, hl_B_cov, hl_B_incl, hl_B_excl = weighted_headline("scenario_B_pct")
hl_C_pct, hl_C_cov, hl_C_incl, hl_C_excl = weighted_headline("scenario_C_pct")

hl_no_tonnage = [f"{g['pyramid_group']} / {g['subitem']}" for g in food_groups if g["demand_A_tonnes"] is None]

# waste-lever headline: use lever value where available, else fall back to scenario_A_pct,
# weighted by the SAME scenario_A tonnage base as hl_A, so the delta isolates the lever's effect.
def waste_lever_headline(lever_field):
    num_sum = 0.0
    den_sum = 0.0
    for g in food_groups:
        w = g["demand_A_tonnes"]
        if not w:
            continue
        pct = g[lever_field] if g[lever_field] is not None else g["scenario_A_pct"]
        if pct is not None:
            num_sum += pct * w
            den_sum += w
    return round(num_sum / den_sum, 1) if den_sum else None

hl_waste25_pct = waste_lever_headline("waste_lever_25_pct")
hl_waste50_pct = waste_lever_headline("waste_lever_50_pct")

headline = {
    "scenario_A_weighted_pct": hl_A_pct,
    "scenario_A_coverage_pct_of_tonnage": hl_A_cov,
    "scenario_A_included": hl_A_incl,
    "scenario_A_excluded_from_average": hl_A_excl,
    "scenario_A_no_tonnage_data": hl_no_tonnage,
    "scenario_B_weighted_pct": hl_B_pct,
    "scenario_B_coverage_pct_of_tonnage": hl_B_cov,
    "scenario_C_weighted_pct": hl_C_pct,
    "scenario_C_coverage_pct_of_tonnage": hl_C_cov,
    "scenario_C_excluded_from_average": hl_C_excl,
    "scenario_A_waste25_weighted_pct": hl_waste25_pct,
    "scenario_A_waste50_weighted_pct": hl_waste50_pct,
    "method_note": (
        "Tonnage-weighted average of scenario_A_pct (or scenario_B_pct) across food groups with a "
        "resolved numeric self-sufficiency figure, weighted by each group's Scenario A recommended-"
        "demand tonnage. Excludes groups with no single point estimate (legumes, porridges/pasta/"
        "rice/grain products, sweets & discretionary) -- coverage_pct_of_tonnage states what share "
        "of total national food-group demand this average actually represents, so the headline "
        "number is never presented as more complete than it is. A further 3 items (legumes, and "
        "the two near-zero individual oil types) have no Scenario A demand tonnage available at "
        "all and so cannot even be excluded-with-visibility -- they simply carry no weight in "
        "this calculation; legumes in particular is a genuine, separately-flagged gap. Scenario C "
        "(EAT-Lancet Planetary Health Diet) uses the same weighting basis and the same exclusion "
        "logic -- see scenario_C_excluded_from_average for its own list, which differs slightly "
        "from A/B because EAT-Lancet leaves a different subset of categories unresolved."
    ),
}

# ---------------------------------------------------------------------------
# 3. Consumption comparison (national + by demographic segment)
# ---------------------------------------------------------------------------
over_under = read_csv("over_under_consumption.csv")
consumption_national = []
for r in over_under:
    consumption_national.append({
        "pyramid_group": r['pyramid_group'],
        "subitem": r['subitem'],
        "recommended_g_per_day": num(r['recommended_g_per_cap_day']),
        "actual_g_per_day": num(r['actual_g_per_cap_day']),
        "ratio_actual_over_recommended": num(r['ratio_actual_over_recommended']),
        "assessment": r['assessment'],
    })

by_segment_raw = read_csv("over_under_consumption_by_segment.csv")
consumption_by_segment = []
for r in by_segment_raw:
    consumption_by_segment.append({
        "age_band": r['age_band'],
        "sex": r['sex'],
        "pyramid_group": r['pyramid_group'],
        "subitem": r['subitem'],
        "recommended_g_per_day": num(r['recommended_g_per_day']),
        "actual_g_per_day": num(r['actual_g_per_day']),
        "ratio": num(r['ratio']),
    })
segments_available = sorted({f"{r['age_band']} {r['sex']}" for r in by_segment_raw})

# ---------------------------------------------------------------------------
# 4. Waste module
# ---------------------------------------------------------------------------
waste_raw = read_csv("waste_model.csv")
waste = []
for r in waste_raw:
    waste.append({
        "pyramid_group": r['pyramid_group'],
        "subitem": r['subitem'],
        "waste_tonnes_year": num(r['waste_tonnes_year']),
        "pct_of_total_sei_waste": num(r['pct_of_total_sei_waste']),
        "consumption_tonnes_year": num(r['consumption_tonnes_year']),
        "loss_rate_vs_consumption_pct": num(r['loss_rate_vs_consumption_pct']),
        "required_production_inflator": num(r['required_production_inflator']),
        "household_waste_tonnes_year": num(r['household_waste_tonnes_year']),
        "household_share_of_groups_waste_pct": num(r['household_share_of_this_groups_waste_pct']),
        "inflator_25pct_cut": num(r['inflator_if_household_waste_cut_25pct']),
        "inflator_50pct_cut": num(r['inflator_if_household_waste_cut_50pct']),
    })

# ---------------------------------------------------------------------------
# 5. FAOSTAT cross-check (for the methodology appendix / validation callout)
# ---------------------------------------------------------------------------
faostat_raw = read_csv("faostat_cross_check.csv")
faostat = []
for r in faostat_raw:
    faostat.append({
        "pyramid_group": r['pyramid_group'],
        "faostat_item": r['faostat_item'],
        "faostat_year": r['faostat_year'],
        "faostat_self_sufficiency_pct": num(r['faostat_self_sufficiency_pct']),
        "project_self_sufficiency_pct": num(r['project_self_sufficiency_pct']),
        "note": r['note'],
    })

# ---------------------------------------------------------------------------
# Assemble
# ---------------------------------------------------------------------------
data = {
    "meta": {
        "project": "toidujulgeolek",
        "title": "Could Estonia feed itself?",
        "generated": str(date.today()),
        "phases_complete": 9,
        "reference_years": {
            "population": "2026 (RV021)",
            "production_supply": "2024 (Statistikaamet PM-series)",
            "requirement_model": "TAI Tabelraamat 2025",
            "consumption_survey": "2014 (RTU011, TAI)",
            "waste_study": "2021 (SEI)",
            "faostat_cross_check": "2022",
            "official_strategy_figures": "~2018-2022 (5yr avg, inferred)",
        },
    },
    "headline": headline,
    "food_groups": food_groups,
    "consumption_national": consumption_national,
    "consumption_by_segment": consumption_by_segment,
    "segments_available": segments_available,
    "waste": waste,
    "faostat_cross_check": faostat,
}

out_path = f"{OUT}/dashboard_data.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Wrote {out_path}")
print(f"Headline Scenario A (weighted, {hl_A_cov}% tonnage coverage): {hl_A_pct}%")
print(f"Headline Scenario B (weighted, {hl_B_cov}% tonnage coverage): {hl_B_pct}%")
print(f"Headline Scenario C (weighted, {hl_C_cov}% tonnage coverage): {hl_C_pct}%")
print(f"Waste lever 25%: {hl_waste25_pct}%  |  50%: {hl_waste50_pct}%")
print(f"Excluded from A average: {hl_A_excl}")
print(f"food_groups: {len(food_groups)}, consumption_national: {len(consumption_national)}, "
      f"consumption_by_segment: {len(consumption_by_segment)}, waste: {len(waste)}, "
      f"faostat: {len(faostat)}")
